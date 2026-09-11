#!/usr/bin/env python3
"""Rung (b) through the FORCE path: partially submerged cube, still water.

Rung (b) already exists as run_c1b in simulation/validate_coupling_force.py, but
it reads the response off the free-rigid material-8 body, which materialises no
force (kernels/mpm_utils.py:1434). This driver runs the SAME rung with the SAME
BoxTank geometry through the collider wrench instead, so the buoyant force is
read directly rather than inferred from a velocity the body merely adopted.

It reuses validate_coupling_force's tank verbatim (import, not copy) so the
geometry, water seeding, carve, planes, walls, dt and substeps are identical to
the published C1/C1b runs. Nothing in validate_coupling_force.py is modified.

ANALYTIC REFERENCE, taken from run_c1b's own derivation:
    F_buoy = rho_w * g * L^2 * h_sub      (wetted height, not full volume)
    a_ideal = g * (rho_w/rho_box * frac - 1)
The reference is built from the MEASURED settled surface, not the requested
fraction, for the reason run_c1b states: the request is a placement target, the
settled surface is what the body actually feels.

Run:
  python simulation/coupling_force/rung_b_coupled.py --n-grid 32 --settle 400 --steps 60
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simulation.validate_coupling_force import (  # noqa: E402
    BoxTank, box_bottom_cells_for_submersion, settle_pinned, DX_CANON, RHO_W, G, LIM,
)
from simulation.coupling_force import (  # noqa: E402
    RigidBodyState, ForceCoupledBody, CouplingConfig,
)


def cube_inertia(mass, length):
    i = mass * (length ** 2 + length ** 2) / 12.0
    return np.diag([i, i, i])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=32)
    ap.add_argument("--rho-box", type=float, default=600.0)
    ap.add_argument("--depth-cells", type=float, default=18.0)
    ap.add_argument("--submersion-frac", type=float, default=0.80)
    ap.add_argument("--settle", type=int, default=900,
                    help="settle FRAMES cap, collider fixed; one frame is "
                         "tank.substeps solver substeps. 900 matches the rung-a "
                         "reference invocation at scripts/c1sdf.sbatch:38, whose "
                         "g96 gate trips at frame 776, so a smaller cap "
                         "under-settles g96")
    ap.add_argument("--steps", type=int, default=60, help="coupled steps")
    ap.add_argument("--relax", type=float, default=1.0)
    ap.add_argument("--freeze-rotation", action="store_true", default=True)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if not 0.0 < a.submersion_frac < 1.0:
        sys.exit("submersion_frac must be strictly inside (0, 1)")

    bbc = box_bottom_cells_for_submersion(a.submersion_frac, a.depth_cells)
    floor = 3.0 * DX_CANON
    z_b0 = floor + bbc * DX_CANON
    if bbc < 0.0:
        sys.exit(f"submersion_frac needs box_bottom_cells={bbc:.4f} < 0")

    print(f"RUNG B (force path)  n_grid={a.n_grid} rho_box={a.rho_box} "
          f"frac_req={a.submersion_frac} box_bottom_cells={bbc:.4f} z_b0={z_b0:.6f}")

    tank = BoxTank(a.n_grid, a.rho_box, a.depth_cells, z_b0,
                   box_mode="collider_sdf", device=a.device)
    L = tank.length
    print(f"TANK dx={tank.dx:.6f} h={tank.h:.6f} floor={tank.floor:.6f} L={L:.6f} "
          f"n_water={tank.n_water} dt={tank.dt:.3e} substeps={tank.substeps} "
          f"collider_handle={tank.collider}")

    settle = settle_pinned(tank, a.settle)
    print(f"SETTLE frames_run={settle['settle_frames_run']}/{settle['settle_frames_cap']} "
          f"gate_met={settle['settle_gate_met']} "
          f"min_frames={settle['settle_min_frames']} "
          f"vmax_final={settle['settle_vmax_final']:.6e} "
          f"substeps_per_frame={tank.substeps} "
          f"physical_s={settle['settle_frames_run'] / 30.0:.4f}", flush=True)
    if not settle["settle_gate_met"]:
        print("SETTLE GATE NOT MET: the water never reached the quiescence ratio. "
              "Every force number below is a transient, not a hydrostatic reading.",
              flush=True)

    zs, n_free_cols, iqr = tank.column_surface()
    h_sub = float(np.clip(zs - z_b0, 0.0, L))
    frac_real = h_sub / L
    print(f"SETTLED surface z={zs:.6f} (free cols={n_free_cols}, iqr={iqr:.3e})  "
          f"h_sub={h_sub:.6f} frac_realized={frac_real:.4f}")
    if frac_real <= 0.0 or frac_real >= 1.0:
        print("WARNING partial submersion NOT realised; the reference below is degenerate")

    f_buoy_analytic = RHO_W * G * L ** 2 * h_sub
    a_ideal = G * (RHO_W / a.rho_box * frac_real - 1.0)
    mass = tank.mass
    print(f"REFERENCE F_buoy_analytic={f_buoy_analytic:.2f} N  mass={mass:.2f} kg  "
          f"a_ideal={a_ideal:+.4f} m/s2  neutral_frac={a.rho_box/RHO_W:.3f}")

    # --- attach the force coupler -------------------------------------------
    state = RigidBodyState(
        mass=mass,
        inertia_body=cube_inertia(mass, L),
        x_cm=np.array(tank.box_center, dtype=float),
    )
    cfg = CouplingConfig(dt=tank.dt, gravity=(0.0, 0.0, -G), relax=a.relax,
                         substeps_per_pose=1, freeze_rotation=a.freeze_rotation)
    body = ForceCoupledBody(tank.solver, tank.collider, state, cfg,
                            displaced_volume_m3=L ** 2 * h_sub)
    print(f"COUPLER added_mass_ratio={body.added_mass_ratio():.3f}  "
          f"expected_static_buoyancy={body.expected_static_buoyancy():.2f} N")

    amr = body.added_mass_ratio()
    stability_unmitigated = bool(
        amr is not None and amr > cfg.warn_added_mass and a.relax >= 1.0
    )
    if stability_unmitigated:
        print("=" * 78, flush=True)
        print(f"VALIDITY FAIL: added_mass_ratio={amr:.4f} exceeds warn_added_mass="
              f"{cfg.warn_added_mass} while relax={a.relax:.3f}, so no mitigation is "
              f"active. Per coupler.py:36-42 a partitioned explicit scheme "
              f"over-predicts and can diverge in exactly this regime. Numbers below "
              f"are NOT a valid coupling-accuracy measurement. Reduce dt or pass "
              f"--relax below 1.", flush=True)
        print("=" * 78, flush=True)

    z0 = float(state.x_cm[2])
    for i in range(a.steps):
        tank.project_water()
        body.step()
        if i % max(1, a.steps // 10) == 0:
            F = body.trace.force[-1]
            print(f"  t={body._t:8.5f}  Fz={F[2]:+12.2f} N  "
                  f"dz={state.x_cm[2]-z0:+.6f} m  vz={state.v_cm[2]:+.6f} m/s", flush=True)

    tr = body.trace.as_arrays()
    Fz = tr["force"][:, 2]
    vz = tr["v_cm"][:, 2]
    t = tr["t"]

    # acceleration from the first substeps, matching run_c1b's window convention
    accs = {}
    for n in (2, 3, 5, 10, 20):
        if n < len(t):
            accs[f"a_first_{n}"] = float(np.polyfit(t[:n + 1], vz[:n + 1], 1)[0])
    a_meas = accs.get("a_first_3", float("nan"))

    Fz_mean = float(np.mean(Fz))
    Fz_med = float(np.median(Fz))
    print()
    print("=" * 78)
    print(f"MEASURED Fz mean={Fz_mean:+.2f} N  median={Fz_med:+.2f} N  "
          f"min={Fz.min():+.2f}  max={Fz.max():+.2f}")
    print(f"ANALYTIC F_buoy      ={f_buoy_analytic:+.2f} N")
    if f_buoy_analytic != 0:
        print(f"RATIO measured/analytic (median) = {Fz_med/f_buoy_analytic:+.4f}")
    print(f"MEASURED a_first_3   ={a_meas:+.4f} m/s2   ANALYTIC a_ideal={a_ideal:+.4f} m/s2")
    print(f"NET dz over {a.steps} steps = {state.x_cm[2]-z0:+.6f} m")
    print(f"NON-ZERO WRENCH: {'YES' if np.abs(Fz).max() > 1e-6 else 'NO'}")
    print("=" * 78)

    out = {
        "rung": "b", "path": "force (sdf_wrench -> Newton-Euler)",
        "n_grid": a.n_grid, "rho_box": a.rho_box, "depth_cells": a.depth_cells,
        "submersion_frac_requested": a.submersion_frac,
        "submersion_frac_realized": frac_real, "h_sub_m": h_sub,
        "L_m": L, "mass_kg": mass, "dt": tank.dt,
        "settle_frames_cap": settle["settle_frames_cap"],
        "settle_frames_run": settle["settle_frames_run"],
        "settle_min_frames": settle["settle_min_frames"],
        "settle_gate_met": settle["settle_gate_met"],
        "settle_vmax_final": settle["settle_vmax_final"],
        "settle_physical_s": settle["settle_frames_run"] / 30.0,
        "substeps_per_frame": tank.substeps,
        "coupled_steps": a.steps,
        "relax": a.relax,
        "warn_added_mass": cfg.warn_added_mass,
        "added_mass_ratio_exceeds_warn": bool(
            amr is not None and amr > cfg.warn_added_mass),
        "stability_unmitigated": stability_unmitigated,
        "valid_accuracy_measurement": bool(
            settle["settle_gate_met"] and not stability_unmitigated),
        "F_buoy_analytic_N": f_buoy_analytic,
        "Fz_measured_mean_N": Fz_mean, "Fz_measured_median_N": Fz_med,
        "ratio_median_over_analytic": (Fz_med / f_buoy_analytic) if f_buoy_analytic else None,
        "a_ideal_ms2": a_ideal, "a_measured_first3_ms2": a_meas,
        "accel_windows": accs,
        "net_dz_m": float(state.x_cm[2] - z0),
        "added_mass_ratio": body.added_mass_ratio(),
        "clamped_steps": len(body.trace.clamped),
        "nonzero_wrench": bool(np.abs(Fz).max() > 1e-6),
    }
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
