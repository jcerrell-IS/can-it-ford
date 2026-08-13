from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import simulation.validate_coupling_force as vcf
from simulation.validate_coupling_force import (
    BoxTank, settle_pinned, DX_CANON, RHO_W, G, GAMMA, ETA, FPS,
)


def patch_bulk(new_bulk):
    vcf.BULK = new_bulk
    vcf.sound_speed.__defaults__ = (new_bulk, vcf.RHO_W)
    vcf.substeps_and_dt.__defaults__ = (vcf.ETA, vcf.RHO_W, new_bulk, vcf.FPS)


def surfaces(tank, zs_reported):
    n_w = tank.n_water
    z = tank.solver.x()[:n_w, 2].astype(float)
    floor = tank.floor
    h = tank.dx / 2.0
    w = 0.25 * h
    lo = floor - 3.0 * tank.dx
    hi = z.max() + w
    edges = np.arange(lo, hi + w, w)
    cnt, _ = np.histogram(z, bins=edges)
    zc = 0.5 * (edges[:-1] + edges[1:])
    dens = cnt / w

    filled = np.flatnonzero(cnt > 0)
    i0, i1 = filled[0], filled[-1]
    mid = dens[i0 + (i1 - i0) // 3: i0 + 2 * (i1 - i0) // 3]
    bulk_dens = float(np.median(mid)) if mid.size else float("nan")

    z_half = float("nan")
    for i in range(i1, i0, -1):
        if dens[i] < 0.5 * bulk_dens <= dens[i - 1]:
            f = (0.5 * bulk_dens - dens[i]) / (dens[i - 1] - dens[i])
            z_half = float(zc[i] + f * (zc[i - 1] - zc[i]))
            break

    below = z < floor
    near_floor = z < floor + 1.0 * tank.dx
    expected_near = bulk_dens * (1.0 * tank.dx + max(0.0, floor - z.min()))
    pile = float(near_floor.sum() - expected_near)

    return {
        "z_min": float(z.min()), "z_max": float(z.max()),
        "n_below_floor": int(below.sum()),
        "frac_below_floor": float(below.sum()) / n_w,
        "floor_penetration_dx": float(max(0.0, floor - z.min()) / tank.dx),
        "bulk_density_particles_per_m": bulk_dens,
        "z_half_density": z_half,
        "zs_reported_volume_based": float(zs_reported),
        "surface_gap_m": float(zs_reported - z_half),
        "surface_gap_Pa": float(RHO_W * G * (zs_reported - z_half)),
        "pile_excess_particles": pile,
        "pile_excess_frac": pile / n_w,
        "hist_z": zc.tolist(),
        "hist_count": cnt.tolist(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--rho-box", type=float, default=600.0)
    ap.add_argument("--depth-cells", type=float, default=18.0)
    ap.add_argument("--box-bottom-cells", type=float, default=8.0)
    ap.add_argument("--settle-frames", type=int, default=900)
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--bulk", type=float, default=None)
    ap.add_argument("--sdf-res", type=int, default=64)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.bulk is not None:
        patch_bulk(a.bulk)
    bulk = vcf.BULK
    c_expect = float(np.sqrt(GAMMA * bulk / RHO_W))

    floor = 3.0 * DX_CANON
    z_b0 = floor + a.box_bottom_cells * DX_CANON
    tank = BoxTank(a.n_grid, a.rho_box, a.depth_cells, z_b0, water=True,
                   device=a.device, box_mode="collider_sdf", sdf_res=a.sdf_res)

    if abs(tank.sound_speed - c_expect) > 1e-6 * max(1.0, c_expect):
        sys.exit(f"BULK PATCH FAILED: tank.sound_speed={tank.sound_speed} "
                 f"expected {c_expect}. Refusing to run a desynchronized timestep.")
    print(f"n_grid={a.n_grid} dx={tank.dx:.6f} dt={tank.dt:.6e} "
          f"substeps/frame={tank.substeps} n_water={tank.n_water} "
          f"bulk={bulk:.4e} c={tank.sound_speed:.4f} VERIFIED", flush=True)

    settle = settle_pinned(tank, a.settle_frames)
    frames = settle["settle_frames_run"]
    subs = frames * tank.substeps
    dg = settle["diagnostics_after_settle"]
    leaked = int(dg["leaked_cumulative"])
    print(f"SETTLE frames={frames} substeps={subs} gate_met={settle['settle_gate_met']} "
          f"vmax_final={settle['settle_vmax_final']:.4f}", flush=True)
    print(f"LEAK leaked_cumulative={leaked} "
          f"per_substep={leaked / max(1, subs):.1f} "
          f"per_particle={leaked / tank.n_water:.2f} "
          f"escaped_now={dg['escaped_water']} "
          f"max_floor_pen_dx={dg['max_floor_penetration_dx']:.4f}", flush=True)

    zs, n_free_cols, iqr = tank.column_surface()
    s = surfaces(tank, zs)
    L = tank.length
    A = L * L
    print(f"SURFACE volume_based={zs:.6f} half_density={s['z_half_density']:.6f} "
          f"gap={s['surface_gap_m']:.4f} m = {s['surface_gap_Pa']:.0f} Pa", flush=True)
    print(f"PILE below_floor={s['n_below_floor']} ({100 * s['frac_below_floor']:.2f}%) "
          f"excess_near_floor={s['pile_excess_particles']:.0f} "
          f"({100 * s['pile_excess_frac']:.2f}%)", flush=True)

    f_series = []
    for i in range(a.steps):
        tank.project_water()
        tank.reset_wrench()
        tank.solver.step(tank.dt, 1)
        f, _t = tank.wrench(tank.dt)
        f_series.append(float(f[2]))
    fz = np.asarray(f_series)
    steady = float(fz[len(fz) // 2:].mean())

    h_rep = float(np.clip(zs - z_b0, 0.0, L))
    h_true = float(np.clip(s["z_half_density"] - z_b0, 0.0, L))
    f_rep = RHO_W * G * A * h_rep
    f_true = RHO_W * G * A * h_true
    f_full = RHO_W * tank.volume * G
    fully = bool(zs > z_b0 + L + 0.5 * tank.dx)

    print("=" * 78)
    print(f"WRENCH steady={steady:+.1f} N   fully_submerged_by_reported_surface={fully}")
    print(f"  vs partial analytic on REPORTED surface  h={h_rep:.4f} F={f_rep:9.1f} "
          f"-> {100 * (steady - f_rep) / f_rep:+7.2f}%")
    if h_true > 0:
        print(f"  vs partial analytic on HALF-DENSITY surf h={h_true:.4f} F={f_true:9.1f} "
              f"-> {100 * (steady - f_true) / f_true:+7.2f}%")
    print(f"  vs full-submersion analytic              F={f_full:9.1f} "
          f"-> {100 * (steady - f_full) / f_full:+7.2f}%")
    print("=" * 78)

    out = {
        "n_grid": a.n_grid, "dx": tank.dx, "dt": tank.dt,
        "substeps_per_frame": tank.substeps, "n_water": tank.n_water,
        "bulk": bulk, "sound_speed": tank.sound_speed,
        "box_bottom_cells": a.box_bottom_cells, "depth_cells": a.depth_cells,
        "settle_frames_run": frames, "settle_substeps_run": subs,
        "settle_gate_met": bool(settle["settle_gate_met"]),
        "settle_vmax_final": settle["settle_vmax_final"],
        "leaked_cumulative": leaked,
        "leaked_per_substep": leaked / max(1, subs),
        "leaked_per_particle": leaked / tank.n_water,
        "diagnostics_after_settle": dg,
        "surface_iqr_m": iqr,
        "fully_submerged_by_reported_surface": fully,
        "h_sub_reported_m": h_rep, "h_sub_half_density_m": h_true,
        "F_partial_reported_N": f_rep, "F_partial_half_density_N": f_true,
        "F_full_N": f_full,
        "Fz_steady_N": steady,
        "err_vs_reported_pct": 100.0 * (steady - f_rep) / f_rep,
        "err_vs_half_density_pct": (100.0 * (steady - f_true) / f_true
                                    if h_true > 0 else None),
        "err_vs_full_pct": 100.0 * (steady - f_full) / f_full,
    }
    out.update(s)
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
