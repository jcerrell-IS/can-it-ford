from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation.validate_coupling_force import (
    BoxTank, box_bottom_cells_for_submersion, DX_CANON, RHO_W, G,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--rho-box", type=float, default=600.0)
    ap.add_argument("--depth-cells", type=float, default=18.0)
    ap.add_argument("--submersion-frac", type=float, default=0.80)
    ap.add_argument("--settle", type=int, default=900)
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--mode", default="fixed",
                    choices=["fixed", "pose_zero_vel", "pose_full"])
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    bbc = box_bottom_cells_for_submersion(a.submersion_frac, a.depth_cells)
    floor = 3.0 * DX_CANON
    z_b0 = floor + bbc * DX_CANON

    tank = BoxTank(a.n_grid, a.rho_box, a.depth_cells, z_b0,
                   box_mode="collider_sdf", device=a.device)
    L = tank.length
    print(f"MODE={a.mode} n_grid={a.n_grid} dx={tank.dx:.6f} dt={tank.dt:.3e} "
          f"substeps={tank.substeps} n_water={tank.n_water} handle={tank.collider}",
          flush=True)

    for i in range(a.settle):
        tank.project_water()
        tank.solver.step(tank.dt, 1)

    zs, n_free, iqr = tank.column_surface()
    h_sub = float(np.clip(zs - z_b0, 0.0, L))
    frac_real = h_sub / L
    f_analytic = RHO_W * G * L ** 2 * h_sub
    mass = tank.mass
    print(f"SETTLED z={zs:.6f} h_sub={h_sub:.6f} frac={frac_real:.4f} "
          f"F_analytic={f_analytic:.2f} N mass={mass:.2f} kg", flush=True)

    center = np.array(tank.box_center, dtype=float)
    v_cm = np.zeros(3)
    quat = (0.0, 0.0, 0.0, 1.0)
    Fz_hist, z_hist = [], []

    for i in range(a.steps):
        tank.project_water()
        tank.solver.reset_sdf_force(tank.collider)
        tank.solver.step(tank.dt, 1)
        w = tank.solver.sdf_wrench(tank.collider, tank.dt)
        F = np.asarray(w["force"], dtype=float)
        Fz_hist.append(F[2])

        if a.mode != "fixed":
            acc = F / mass + np.array([0.0, 0.0, -G])
            v_cm = v_cm + acc * tank.dt
            center = center + v_cm * tank.dt
            vel = (0.0, 0.0, 0.0) if a.mode == "pose_zero_vel" else tuple(v_cm)
            tank.solver.set_sdf_pose(tank.collider, center=tuple(center),
                                     quat=quat, velocity=vel,
                                     omega=(0.0, 0.0, 0.0))
        z_hist.append(center[2])

        if i % max(1, a.steps // 8) == 0:
            print(f"  i={i:4d} Fz={F[2]:+12.2f} N  z={center[2]:.6f} "
                  f"vz={v_cm[2]:+.6f}", flush=True)

    Fz = np.asarray(Fz_hist)
    med = float(np.median(Fz))
    err = (med - f_analytic) / f_analytic * 100.0 if f_analytic else float("nan")
    print("=" * 74)
    print(f"MODE {a.mode}  Fz median={med:+.2f} N  mean={Fz.mean():+.2f} "
          f"min={Fz.min():+.2f} max={Fz.max():+.2f}")
    print(f"ANALYTIC {f_analytic:+.2f} N   ERROR {err:+.2f}%")
    print(f"net dz = {z_hist[-1] - float(tank.box_center[2]):+.6f} m")
    print("=" * 74)

    out = {
        "mode": a.mode, "n_grid": a.n_grid, "rho_box": a.rho_box,
        "dt": tank.dt, "substeps_cfl": tank.substeps,
        "settle": a.settle, "steps": a.steps,
        "submersion_frac_realized": frac_real, "h_sub_m": h_sub,
        "mass_kg": mass, "F_buoy_analytic_N": f_analytic,
        "Fz_median_N": med, "Fz_mean_N": float(Fz.mean()),
        "Fz_min_N": float(Fz.min()), "Fz_max_N": float(Fz.max()),
        "err_pct": err,
        "net_dz_m": float(z_hist[-1] - float(tank.box_center[2])),
    }
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
