from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation.validate_coupling_force import (
    BoxTank, settle_pinned, DX_CANON, RHO_W, G,
)
from simulation.coupling_force.rigid_body import RigidBodyState
from simulation.coupling_force.coupler import CouplingConfig, ForceCoupledBody
from simulation.coupling_force.rung_b_coupled import cube_inertia


def summarize(fz, f_analytic, f_partial):
    tail = fz[len(fz) // 2:]
    steady = float(tail.mean())
    first3 = float(fz[:3].mean()) if len(fz) >= 3 else float("nan")
    return {
        "Fz_steady_tail_mean_N": steady,
        "Fz_steady_tail_std_N": float(tail.std()),
        "Fz_steady_tail_ptp_N": float(tail.max() - tail.min()),
        "Fz_first3_mean_N": first3,
        "Fz_median_all_N": float(np.median(fz)),
        "Fz_min_N": float(fz.min()),
        "Fz_max_N": float(fz.max()),
        "err_steady_vs_analytic_pct": 100.0 * (steady - f_analytic) / f_analytic,
        "err_first3_vs_analytic_pct": 100.0 * (first3 - f_analytic) / f_analytic,
        "err_steady_vs_partial_pct": (100.0 * (steady - f_partial) / f_partial
                                      if f_partial > 0 else float("nan")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--rho-box", type=float, default=600.0)
    ap.add_argument("--depth-cells", type=float, default=18.0)
    ap.add_argument("--box-bottom-cells", type=float, default=8.0)
    ap.add_argument("--settle-frames", type=int, default=900)
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--mode", default="fixed", choices=["fixed", "coupled"])
    ap.add_argument("--relax", type=float, default=1.0)
    ap.add_argument("--freeze-rotation", action="store_true")
    ap.add_argument("--sdf-res", type=int, default=64)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    floor = 3.0 * DX_CANON
    z_b0 = floor + a.box_bottom_cells * DX_CANON

    tank = BoxTank(a.n_grid, a.rho_box, a.depth_cells, z_b0, water=True,
                   device=a.device, box_mode="collider_sdf", sdf_res=a.sdf_res)
    L = tank.length
    print(f"MODE={a.mode} n_grid={a.n_grid} dx={tank.dx:.6f} dt={tank.dt:.6e} "
          f"substeps/frame={tank.substeps} n_water={tank.n_water} "
          f"c={tank.sound_speed:.4f} handle={tank.collider}", flush=True)

    settle = settle_pinned(tank, a.settle_frames)
    frames = settle["settle_frames_run"]
    print(f"SETTLE frames={frames}/{a.settle_frames} "
          f"substeps={frames * tank.substeps} gate_met={settle['settle_gate_met']} "
          f"vmax_peak={settle['settle_vmax_peak']:.4f} "
          f"vmax_final={settle['settle_vmax_final']:.4f} "
          f"ratio_c_over_vmax={tank.sound_speed / settle['settle_vmax_final']:.2f}",
          flush=True)
    if not settle["settle_gate_met"]:
        print("SETTLE GATE NOT MET: this run is a discard, the water is still ringing "
              "and any wrench read from it is not a hydrostatic measurement.", flush=True)

    zs, n_free_cols, iqr = tank.column_surface()
    box_top = z_b0 + L
    h_sub = float(np.clip(zs - z_b0, 0.0, L))
    frac = h_sub / L
    f_analytic = RHO_W * tank.volume * G
    f_partial = RHO_W * G * L ** 2 * h_sub
    mass = tank.mass
    print(f"GEOM surface={zs:.6f} box_top={box_top:.6f} "
          f"margin_dx={(zs - box_top) / tank.dx:+.4f} frac_submerged={frac:.4f} "
          f"fully_submerged={bool(zs > box_top + 0.5 * tank.dx)}", flush=True)
    print(f"REFERENCE F_full={f_analytic:.2f} N  F_partial={f_partial:.2f} N  "
          f"mass={mass:.2f} kg", flush=True)

    center0 = np.array(tank.box_center, dtype=float)
    f_series = []
    z_hist, v_hist = [], []
    body = None

    if a.mode == "fixed":
        for i in range(a.steps):
            tank.project_water()
            tank.reset_wrench()
            tank.solver.step(tank.dt, 1)
            f, _tau = tank.wrench(tank.dt)
            f_series.append([float(f[0]), float(f[1]), float(f[2])])
            z_hist.append(float(center0[2]))
            v_hist.append(0.0)
            if i % max(1, a.steps // 8) == 0:
                print(f"  i={i:4d} Fz={f[2]:+12.2f} N", flush=True)
    else:
        state = RigidBodyState(mass=mass, inertia_body=cube_inertia(mass, L),
                               x_cm=center0.copy())
        cfg = CouplingConfig(dt=tank.dt, gravity=(0.0, 0.0, -G), relax=a.relax,
                             substeps_per_pose=1, freeze_rotation=a.freeze_rotation)
        body = ForceCoupledBody(tank.solver, tank.collider, state, cfg,
                                displaced_volume_m3=L ** 2 * h_sub)
        print(f"COUPLER added_mass_ratio={body.added_mass_ratio():.4f}", flush=True)
        for i in range(a.steps):
            tank.project_water()
            body.step()
            F = body.trace.force[-1]
            f_series.append([float(F[0]), float(F[1]), float(F[2])])
            z_hist.append(float(state.x_cm[2]))
            v_hist.append(float(state.v_cm[2]))
            if i % max(1, a.steps // 8) == 0:
                print(f"  i={i:4d} Fz={F[2]:+12.2f} N  dz={state.x_cm[2] - center0[2]:+.6f} "
                      f"vz={state.v_cm[2]:+.6f}", flush=True)

    f = np.asarray(f_series)
    fz = f[:, 2]
    stats = summarize(fz, f_analytic, f_partial)
    lat = [float(f[len(f) // 2:, 0].mean()), float(f[len(f) // 2:, 1].mean())]
    lat_ratio = (float(np.hypot(*lat) / abs(stats["Fz_steady_tail_mean_N"]))
                 if stats["Fz_steady_tail_mean_N"] != 0 else float("nan"))
    net_dz = z_hist[-1] - float(center0[2])

    print("=" * 76)
    print(f"MODE {a.mode}  n_grid {a.n_grid}  relax {a.relax}")
    print(f"  Fz steady tail mean = {stats['Fz_steady_tail_mean_N']:+12.2f} N  "
          f"std {stats['Fz_steady_tail_std_N']:.2f}  ptp {stats['Fz_steady_tail_ptp_N']:.2f}")
    print(f"  Fz median (all)     = {stats['Fz_median_all_N']:+12.2f} N  "
          f"min {stats['Fz_min_N']:+.2f} max {stats['Fz_max_N']:+.2f}")
    print(f"  F_analytic (full)   = {f_analytic:+12.2f} N")
    print(f"  ERROR steady vs full submersion = "
          f"{stats['err_steady_vs_analytic_pct']:+.2f} %")
    print(f"  ERROR first3 vs full submersion = "
          f"{stats['err_first3_vs_analytic_pct']:+.2f} %")
    print(f"  lateral/Fz = {lat_ratio:.4f}   net dz = {net_dz:+.6f} m")
    print("=" * 76)

    out = {
        "mode": a.mode, "n_grid": a.n_grid, "rho_box": a.rho_box,
        "depth_cells": a.depth_cells, "box_bottom_cells": a.box_bottom_cells,
        "relax": a.relax, "steps": a.steps,
        "dx": tank.dx, "dt": tank.dt, "substeps_per_frame": tank.substeps,
        "sound_speed_m_s": tank.sound_speed, "n_water": tank.n_water,
        "settle_frames_run": frames,
        "settle_substeps_run": frames * tank.substeps,
        "settle_frames_cap": a.settle_frames,
        "settle_gate_met": bool(settle["settle_gate_met"]),
        "settle_is_discard": not bool(settle["settle_gate_met"]),
        "settle_vmax_peak": settle["settle_vmax_peak"],
        "settle_vmax_final": settle["settle_vmax_final"],
        "surface_after_settle": zs,
        "surface_iqr_m": iqr,
        "box_top_z": box_top,
        "submersion_margin_dx": (zs - box_top) / tank.dx,
        "fully_submerged_at_measure": bool(zs > box_top + 0.5 * tank.dx),
        "submerged_height_m": h_sub,
        "submerged_height_frac": frac,
        "mass_kg": mass, "volume_m3": tank.volume,
        "F_buoy_analytic_full_N": f_analytic,
        "F_buoy_analytic_partial_N": f_partial,
        "F_lateral_steady_N": lat,
        "F_lateral_over_Fz": lat_ratio,
        "net_dz_m": net_dz,
        "z_final_m": z_hist[-1],
        "vz_final_m_s": v_hist[-1],
        "f_series": f_series,
    }
    out.update(stats)
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
