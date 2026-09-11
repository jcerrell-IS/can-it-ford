from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation.validate_coupling_force import (
    BoxTank, settle_pinned, DX_CANON, RHO_W, G, GAMMA, BULK,
)


def profile(tank, zs, nbins):
    n_w = tank.n_water
    x = tank.solver.x()[:n_w]
    sig = tank.solver.stress()[:n_w]
    F = tank.solver.F()[:n_w]

    J = np.linalg.det(F)
    p_stress = -(sig[:, 0, 0] + sig[:, 1, 1] + sig[:, 2, 2]) / 3.0
    p_eos = BULK * (np.power(np.clip(J, 1e-6, None), -GAMMA) - 1.0)

    z = x[:, 2]
    edges = np.linspace(tank.floor, zs, nbins + 1)
    idx = np.clip(np.digitize(z, edges) - 1, 0, nbins - 1)

    rows = []
    for b in range(nbins):
        m = idx == b
        if not m.any():
            continue
        zc = 0.5 * (edges[b] + edges[b + 1])
        depth = zs - zc
        p_analytic = RHO_W * G * depth
        rows.append({
            "bin": b,
            "z_center": float(zc),
            "depth_below_surface_m": float(depth),
            "depth_in_cells": float(depth / tank.dx),
            "n_particles": int(m.sum()),
            "p_stress_mean_Pa": float(p_stress[m].mean()),
            "p_stress_std_Pa": float(p_stress[m].std()),
            "p_eos_mean_Pa": float(p_eos[m].mean()),
            "p_analytic_Pa": float(p_analytic),
            "deficit_Pa": float(p_analytic - p_stress[m].mean()),
            "deficit_in_cells_of_head": float((p_analytic - p_stress[m].mean())
                                              / (RHO_W * G * tank.dx)),
            "err_pct": (float(100.0 * (p_stress[m].mean() - p_analytic) / p_analytic)
                        if p_analytic > 1e-9 else float("nan")),
            "J_mean": float(J[m].mean()),
            "J_min": float(J[m].min()),
            "rho_implied_mean": float(RHO_W / J[m].mean()),
        })
    return rows, float(J.min()), float(J.max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--rho-box", type=float, default=600.0)
    ap.add_argument("--depth-cells", type=float, default=18.0)
    ap.add_argument("--box-bottom-cells", type=float, default=3.0)
    ap.add_argument("--settle-frames", type=int, default=900)
    ap.add_argument("--nbins", type=int, default=18)
    ap.add_argument("--sdf-res", type=int, default=64)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    floor = 3.0 * DX_CANON
    z_b0 = floor + a.box_bottom_cells * DX_CANON

    tank = BoxTank(a.n_grid, a.rho_box, a.depth_cells, z_b0, water=True,
                   device=a.device, box_mode="collider_sdf", sdf_res=a.sdf_res)
    print(f"n_grid={a.n_grid} dx={tank.dx:.6f} dt={tank.dt:.6e} "
          f"substeps/frame={tank.substeps} n_water={tank.n_water} "
          f"c={tank.sound_speed:.4f} bulk={BULK:.4e} gamma={GAMMA}", flush=True)

    settle = settle_pinned(tank, a.settle_frames)
    frames = settle["settle_frames_run"]
    print(f"SETTLE frames={frames}/{a.settle_frames} "
          f"substeps={frames * tank.substeps} gate_met={settle['settle_gate_met']} "
          f"vmax_peak={settle['settle_vmax_peak']:.4f} "
          f"vmax_final={settle['settle_vmax_final']:.4f}", flush=True)
    if not settle["settle_gate_met"]:
        print("SETTLE GATE NOT MET: discard, the profile below is not hydrostatic.",
              flush=True)

    zs, n_free_cols, iqr = tank.column_surface()
    box_top = z_b0 + tank.length
    print(f"surface={zs:.6f} iqr={iqr:.6f} box_top={box_top:.6f} "
          f"margin_dx={(zs - box_top) / tank.dx:+.4f}", flush=True)

    rows, j_min, j_max = profile(tank, zs, a.nbins)
    print(f"J over all water particles: [{j_min:.6f}, {j_max:.6f}]")
    print("")
    print(f"{'z':>9} {'depth_m':>9} {'cells':>7} {'n':>9} {'p_stress':>11} "
          f"{'p_eos':>11} {'p_analytic':>11} {'deficit':>10} {'def_cells':>9} {'err%':>8}")
    for r in rows:
        print(f"{r['z_center']:>9.4f} {r['depth_below_surface_m']:>9.4f} "
              f"{r['depth_in_cells']:>7.2f} {r['n_particles']:>9} "
              f"{r['p_stress_mean_Pa']:>11.1f} {r['p_eos_mean_Pa']:>11.1f} "
              f"{r['p_analytic_Pa']:>11.1f} {r['deficit_Pa']:>10.1f} "
              f"{r['deficit_in_cells_of_head']:>9.2f} {r['err_pct']:>8.2f}")

    deep = [r for r in rows if r["depth_in_cells"] >= 4.0]
    if deep:
        dc = np.array([r["deficit_in_cells_of_head"] for r in deep])
        print("")
        print(f"deficit over bins deeper than 4 cells: mean {dc.mean():.3f} cells, "
              f"std {dc.std():.3f}, min {dc.min():.3f}, max {dc.max():.3f}")
        print("A deficit that is CONSTANT in cells of head across depth is a "
              "surface-layer offset and scales with dx. One that grows with depth "
              "is a gradient error instead.")

    out = {
        "n_grid": a.n_grid, "dx": tank.dx, "dt": tank.dt,
        "substeps_per_frame": tank.substeps, "n_water": tank.n_water,
        "bulk": BULK, "gamma": GAMMA, "sound_speed_m_s": tank.sound_speed,
        "box_bottom_cells": a.box_bottom_cells, "depth_cells": a.depth_cells,
        "settle_frames_run": frames,
        "settle_substeps_run": frames * tank.substeps,
        "settle_gate_met": bool(settle["settle_gate_met"]),
        "settle_is_discard": not bool(settle["settle_gate_met"]),
        "settle_vmax_final": settle["settle_vmax_final"],
        "surface_after_settle": zs, "surface_iqr_m": iqr,
        "box_top_z": box_top,
        "submersion_margin_dx": (zs - box_top) / tank.dx,
        "J_min_all": j_min, "J_max_all": j_max,
        "profile": rows,
    }
    if deep:
        dc = np.array([r["deficit_in_cells_of_head"] for r in deep])
        out["deficit_cells_deep_mean"] = float(dc.mean())
        out["deficit_cells_deep_std"] = float(dc.std())
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
