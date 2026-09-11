from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation.validate_coupling_force import (
    BoxTank, settle_pinned, hydrostatic_density, eos_b,
    DX_CANON, RHO_W, G, GAMMA, BULK,
)


def hydrostatic_J(z, z_surface):
    zeta = np.clip(z_surface - z, 0.0, None)
    rho = hydrostatic_density(zeta)
    return RHO_W / rho


def apply_precompression(tank, z_surface):
    import torch

    sim = tank.solver._sim
    F = tank.solver.F()
    n_w = tank.n_water
    if n_w == 0:
        raise RuntimeError("no water particles to pre-compress")

    x = tank.solver.x()
    J = hydrostatic_J(x[:n_w, 2], z_surface)
    s = J ** (1.0 / 3.0)

    F_new = F.copy()
    F_new[:n_w] = 0.0
    F_new[:n_w, 0, 0] = s
    F_new[:n_w, 1, 1] = s
    F_new[:n_w, 2, 2] = s

    sim.import_particle_F_from_torch(
        torch.from_numpy(np.ascontiguousarray(F_new, dtype=np.float32)),
        device=tank.solver.device,
    )

    det = np.linalg.det(tank.solver.F()[:n_w])
    return {
        "J_min": float(J.min()), "J_max": float(J.max()),
        "J_mean": float(J.mean()),
        "compression_max_pct": float(100.0 * (1.0 - J.min())),
        "rho_max_kg_m3": float(RHO_W / J.min()),
        "detF_after_import_min": float(det.min()),
        "detF_after_import_max": float(det.max()),
        "detF_matches_J": bool(np.allclose(np.sort(det), np.sort(J), rtol=1e-4, atol=1e-6)),
        "eos_b_per_m": float(eos_b()),
        "gamma": GAMMA, "bulk": BULK,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--rho-box", type=float, default=600.0)
    ap.add_argument("--depth-cells", type=float, default=18.0)
    ap.add_argument("--box-bottom-cells", type=float, default=8.0)
    ap.add_argument("--precompress", default="off", choices=["off", "on"])
    ap.add_argument("--settle-frames", type=int, default=900)
    ap.add_argument("--sdf-res", type=int, default=64)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    floor = 3.0 * DX_CANON
    z_b0 = floor + a.box_bottom_cells * DX_CANON

    tank = BoxTank(a.n_grid, a.rho_box, a.depth_cells, z_b0, water=True,
                   device=a.device, box_mode="collider_sdf", sdf_res=a.sdf_res)
    z_surface = tank.floor + tank.water_depth
    print(f"PRECOMPRESS={a.precompress} n_grid={a.n_grid} dx={tank.dx:.6f} "
          f"dt={tank.dt:.6e} substeps/frame={tank.substeps} n_water={tank.n_water} "
          f"c={tank.sound_speed:.4f}", flush=True)
    print(f"WATER floor={tank.floor:.6f} depth={tank.water_depth:.6f} "
          f"z_surface_t0={z_surface:.6f}", flush=True)

    pc = None
    if a.precompress == "on":
        pc = apply_precompression(tank, z_surface)
        print(f"APPLIED J in [{pc['J_min']:.6f}, {pc['J_max']:.6f}] "
              f"max compression {pc['compression_max_pct']:.3f}% "
              f"rho_max {pc['rho_max_kg_m3']:.2f} kg/m3", flush=True)
        print(f"VERIFY detF in [{pc['detF_after_import_min']:.6f}, "
              f"{pc['detF_after_import_max']:.6f}] matches_J={pc['detF_matches_J']}",
              flush=True)
        if not pc["detF_matches_J"]:
            print("IMPORT DID NOT TAKE: det F read back does not match the requested J. "
                  "Treat this run as a discard.", flush=True)

    settle = settle_pinned(tank, a.settle_frames)
    frames = settle["settle_frames_run"]
    substeps = frames * tank.substeps
    print("=" * 76)
    print(f"SETTLE frames={frames}/{a.settle_frames} substeps={substeps} "
          f"gate_met={settle['settle_gate_met']}")
    print(f"  vmax_peak={settle['settle_vmax_peak']:.4f} m/s  "
          f"vmax_final={settle['settle_vmax_final']:.4f} m/s  "
          f"c/vmax_final={tank.sound_speed / settle['settle_vmax_final']:.2f}")
    print(f"  vmax_peak / c = {settle['settle_vmax_peak'] / tank.sound_speed:.4f}")

    zs, n_free_cols, iqr = tank.column_surface()
    box_top = z_b0 + tank.length
    h_sub = float(np.clip(zs - z_b0, 0.0, tank.length))
    print(f"  surface_after_settle={zs:.6f} (t=0 nominal {z_surface:.6f}, "
          f"drop {z_surface - zs:+.6f} m)")
    print(f"  frac_submerged={h_sub / tank.length:.4f} "
          f"margin_dx={(zs - box_top) / tank.dx:+.4f}")
    print("=" * 76)

    out = {
        "precompress": a.precompress, "n_grid": a.n_grid,
        "depth_cells": a.depth_cells, "box_bottom_cells": a.box_bottom_cells,
        "dx": tank.dx, "dt": tank.dt, "substeps_per_frame": tank.substeps,
        "sound_speed_m_s": tank.sound_speed, "n_water": tank.n_water,
        "z_surface_t0": z_surface,
        "settle_frames_run": frames, "settle_substeps_run": substeps,
        "settle_frames_cap": a.settle_frames,
        "settle_gate_met": bool(settle["settle_gate_met"]),
        "settle_vmax_peak": settle["settle_vmax_peak"],
        "settle_vmax_final": settle["settle_vmax_final"],
        "vmax_peak_over_c": settle["settle_vmax_peak"] / tank.sound_speed,
        "surface_after_settle": zs, "surface_iqr_m": iqr,
        "surface_drop_from_t0_m": z_surface - zs,
        "submerged_height_frac": h_sub / tank.length,
        "submersion_margin_dx": (zs - box_top) / tank.dx,
        "precompression": pc,
        "settle_vmax_trace": settle["settle_vmax_trace"],
    }
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
