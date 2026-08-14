"""ARM (b), the available-traction side: F_F = mu*(W - B - L), depth-resolved.

WHY THIS RUNS WITHOUT A SOLVER, AND WHY THAT MATTERS. Dispatch 9 records an engine
limitation that bounds everything in this track: the net force on the hull cannot be
DECOMPOSED into hydrodynamic, contact and gravitational parts (the correct nuance;
"no force is ever formed" is false, `_apply_rigid_restitution` is live at
mpm_solver_warp.py:887, called at :1362).

The traction budget is the one verdict quantity that DOES NOT NEED that decomposition:

    F_N = W - (net upward reaction)          <- one number, no decomposition needed
    F_F = mu * F_N                           <- available traction
    demand = F_drag + mu_RO * F_N            <- what the vehicle must overcome

Only the NET normal load enters. So the available-traction side is computable
analytically here, and the solver is needed only for the DEMAND side (drag). That
split is the reason this arm is the graded deliverable rather than the force numbers.

WHAT IS ANALYTIC HERE AND WHAT IS NOT.
  ANALYTIC, no solver:   W, B(d), F_N(d), F_F(d), flotation depth, frontal area A(d)
  LITERATURE BAND:       drag demand from C_D 1.22 to 6.82 (Hu et al. 2023)
  SOLVER-MEASURED:       the actual drag, supplied by simulation/moving_vehicle_driver.py

L (hydrodynamic lift) IS SET TO ZERO HERE and that is stated, not hidden: a static
hull has no lift, so F_F(d) computed here is an UPPER BOUND on available traction.
Any real L > 0 reduces it. Smith, Modra and Felder 2019 measure the full
depth-resolved curve on real vehicles and are the comparison target.

PROVENANCE OF EVERY PARAMETER IS IN `PARAMS` BELOW. Nothing here is invented.

SCOPE. This is a DRIVEN-vehicle configuration: the hull travels along its own long
axis (+y), so the frontal area is the x-z cross-section. That is NOT the AR&R /
Shand stationary side-on configuration, and no FORD verdict follows from it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vetted_loader import load_as_ran_canonicalize, load_vehicle_live  # noqa: E402

G = 9.81            # CLAUDE.md item 3: the solver hardcodes 9.81; do not use 9.80665
RHO_W = 1000.0      # CLAUDE.md physical anchor

PARAMS = {
    "mu_parked_baseline": (0.30, "Bonham and Hattersley 1967, adopted conservatively "
                                 "for the published hazard curves (Dispatch 9)"),
    "mu_parallel_measured": (0.52, "measured parallel to flow (Dispatch 9)"),
    "mu_tyre_wet": (0.75, "measured tyre friction on wet concrete, Smith, Modra, "
                          "Felder 2019"),
    "mu_tyre_dry": (0.78, "measured tyre friction on dry concrete, Smith, Modra, "
                          "Felder 2019"),
    "mu_RO": (0.092, "rolling resistance, Shah et al. 2018"),
    "C_D_low": (1.22, "Hu et al. 2023, J. Hydrology 620:129525, JOINT ENVELOPE over "
                      "three vehicles and ALL flow directions"),
    "C_D_high": (6.82, "Hu et al. 2023, same joint envelope"),
}

# Rogue mass. The deck states NO mass (reconciliation 2026-08-14), so every value is
# external and each is carried with its source rather than silently averaged.
ROGUE_MASSES = {
    "arr_reference_1609": (1609.0, "AR&R reference mass per the mesh README"),
    "nhtsa_awd_1610": (1610.0, "NHTSA curb weight, 2020 Rogue AWD"),
    "nhtsa_fwd_1550": (1550.0, "NHTSA curb weight, 2020 Rogue FWD"),
    "job_896273_1571p3": (1571.3, "job 896273; PROVENANCE OPEN, the string 1571.3 is "
                                  "untraced in project knowledge (Dispatch 5 owns it)"),
}


def submerged_profile(particles: np.ndarray, h: float, depths: np.ndarray) -> dict:
    """Submerged volume and frontal area vs waterline depth, from the vetted fill.

    `particles` is the solidify_watertight lattice in the vehicle frame, floor at
    z = 0, pitch h. Volume is n_below * h^3. Frontal area for travel along +y is the
    projected x-z footprint of the submerged set, counted as unique (x, z) cells.
    """
    z = particles[:, 2]
    ix = np.round(particles[:, 0] / h).astype(np.int64)
    iz = np.round(particles[:, 2] / h).astype(np.int64)
    vols, areas = [], []
    for d in depths:
        m = z < d
        vols.append(float(m.sum()) * h ** 3)
        if m.any():
            cells = np.unique(np.stack([ix[m], iz[m]], 1), axis=0)
            areas.append(len(cells) * h * h)
        else:
            areas.append(0.0)
    return {"volume_m3": np.array(vols), "frontal_area_m2": np.array(areas)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ply", required=True, type=Path)
    ap.add_argument("--mass-key", default="arr_reference_1609", choices=list(ROGUE_MASSES),
                    help="Rogue-specific presets; ignored when --mass is given")
    ap.add_argument("--mass", type=float, default=None,
                    help="override mass in kg for a different vehicle, e.g. the "
                         "canonical Yaris at 1100.0 (vehicle_params.py mass_kg)")
    ap.add_argument("--mass-source", default=None,
                    help="provenance string for --mass; REQUIRED with --mass so no "
                         "unsourced mass can enter a result")
    ap.add_argument("--velocity", type=float, default=1.5,
                    help="driven speed for the drag-demand band, m/s")
    ap.add_argument("--spacing", type=float, default=0.025,
                    help="fill pitch. NOT the loader default: extent/32 = 0.1483 m for "
                         "this hull, which quantises the waterline into ~0.15 m steps and "
                         "makes V_sub(d) a staircase. Measured convergence of the fill "
                         "against mesh volume: -0.22%% at 0.05 m, +0.02%% at 0.025 m.")
    ap.add_argument("--depth-max", type=float, default=1.2)
    ap.add_argument("--depth-step", type=float, default=0.05)
    ap.add_argument("--mesh-seed", type=int, default=0)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    canonicalize = load_as_ran_canonicalize()
    mod = load_vehicle_live()

    # Seeded load: load_vehicle draws 60,000 RANDOM surface samples, and an unseeded
    # load changes the mesh by ~1 ULP, which is enough to miss the SDF cache.
    np.random.seed(args.mesh_seed)
    v = canonicalize(mod.load_vehicle(args.ply, up="z"))
    if args.spacing is not None:
        v.solidify(float(args.spacing))
    h = float(v.spacing)
    parts = np.asarray(v.particles, dtype=float)
    mesh_vol = float(abs(v.mesh.volume))
    fill_vol = len(parts) * h ** 3

    if args.mass is not None:
        if not args.mass_source:
            ap.error("--mass requires --mass-source: an unsourced mass must not enter "
                     "a result. CLAUDE.md item 10 exists because two of three masses in "
                     "the canonical sweep had no traceable source.")
        mass, mass_src = float(args.mass), args.mass_source
    else:
        mass, mass_src = ROGUE_MASSES[args.mass_key]
    W = mass * G
    rho_veh = mass / mesh_vol

    depths = np.arange(args.depth_step, args.depth_max + 1e-9, args.depth_step)
    prof = submerged_profile(parts, h, depths)
    B = RHO_W * G * prof["volume_m3"]
    F_N = np.maximum(W - B, 0.0)

    mu_RO = PARAMS["mu_RO"][0]
    cd_lo, cd_hi = PARAMS["C_D_low"][0], PARAMS["C_D_high"][0]
    q = 0.5 * RHO_W * args.velocity ** 2
    drag_lo = q * cd_lo * prof["frontal_area_m2"]
    drag_hi = q * cd_hi * prof["frontal_area_m2"]

    print("=" * 86)
    print("ARM (b) AVAILABLE-TRACTION BUDGET, analytic side. Rogue hull, driven along +y.")
    print("=" * 86)
    print(f"\nhull            {args.ply.name}")
    print(f"mesh volume     {mesh_vol:.6f} m3")
    print(f"fill volume     {fill_vol:.6f} m3   ({100*(fill_vol/mesh_vol - 1):+.2f}% vs mesh, "
          f"pitch {h:.6f} m, {len(parts)} particles)")
    print(f"mass            {mass:.1f} kg   [{mass_src}]")
    print(f"rho_vehicle     {rho_veh:.3f} kg/m3")
    print(f"W = m*g         {W:.1f} N")
    print(f"drive speed     {args.velocity:.2f} m/s")
    print("\nL (hydrodynamic lift) is SET TO ZERO: F_F below is an UPPER BOUND.")

    # flotation depth: first depth where B >= W
    fl = np.where(B >= W)[0]
    d_float = float(depths[fl[0]]) if len(fl) else float("nan")

    print(f"\n{'depth':>7}{'V_sub':>10}{'B':>11}{'F_N':>11}{'A_front':>10}"
          f"{'F_F@0.30':>11}{'F_F@0.52':>11}{'drag band (N)':>22}")
    print(f"{'(m)':>7}{'(m3)':>10}{'(N)':>11}{'(N)':>11}{'(m2)':>10}{'(N)':>11}{'(N)':>11}"
          f"{'C_D 1.22 - 6.82':>22}")
    print("-" * 93)
    rows = []
    for i, d in enumerate(depths):
        ff30 = 0.30 * F_N[i]
        ff52 = 0.52 * F_N[i]
        print(f"{d:>7.2f}{prof['volume_m3'][i]:>10.4f}{B[i]:>11.1f}{F_N[i]:>11.1f}"
              f"{prof['frontal_area_m2'][i]:>10.4f}{ff30:>11.1f}{ff52:>11.1f}"
              f"{drag_lo[i]:>10.1f} -{drag_hi[i]:>10.1f}")
        rows.append({"depth_m": float(d), "V_sub_m3": float(prof["volume_m3"][i]),
                     "B_N": float(B[i]), "F_N_N": float(F_N[i]),
                     "A_frontal_m2": float(prof["frontal_area_m2"][i]),
                     "F_F_mu0p30_N": float(ff30), "F_F_mu0p52_N": float(ff52),
                     "drag_CD1p22_N": float(drag_lo[i]), "drag_CD6p82_N": float(drag_hi[i])})

    print(f"\nflotation depth (B >= W): {d_float:.2f} m"
          + ("" if np.isfinite(d_float) else "  (not reached within depth-max)"))

    # Where does demand exceed available? Report per mu, using the literature band.
    print("\nCROSSING DEPTHS, where demand exceeds available traction:")
    print("  demand = drag + mu_RO*F_N,  mu_RO = 0.092 (Shah et al. 2018)")
    cross = {}
    for name, mu in (("mu=0.30 parked baseline", 0.30), ("mu=0.52 parallel measured", 0.52),
                     ("mu=0.75 tyre wet", 0.75)):
        for cd_name, drag in (("C_D 1.22", drag_lo), ("C_D 6.82", drag_hi)):
            avail = mu * F_N
            demand = drag + mu_RO * F_N
            bad = np.where(demand > avail)[0]
            d_cross = float(depths[bad[0]]) if len(bad) else float("nan")
            cross[f"{name} | {cd_name}"] = d_cross
            print(f"  {name:<28} {cd_name:<9} -> "
                  + (f"{d_cross:.2f} m" if np.isfinite(d_cross)
                     else "no crossing within depth-max"))

    print("\nCAVEATS THAT TRAVEL WITH EVERY NUMBER ABOVE:")
    print("  * L = 0, so F_F is an upper bound on available traction.")
    print("  * The C_D band 1.22-6.82 is a JOINT ENVELOPE over three vehicles and ALL")
    print("    flow directions (Hu et al. 2023). Its midpoint is not an estimate for")
    print("    this vehicle at this orientation, so the band is reported, never a point.")
    print("  * Driven along +y (own long axis). NOT the AR&R stationary side-on case.")
    print("    No FORD / NO-FORD verdict follows from this table.")
    print("  * Smith, Modra and Felder 2019 is a STATIONARY SIDEWAYS WINCH PULL-TEST.")
    print("    It bounds available traction; it does not validate propulsion.")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps({
            "hull": str(args.ply), "mesh_volume_m3": mesh_vol, "fill_volume_m3": fill_vol,
            "fill_pitch_m": h, "n_fill_particles": len(parts),
            "mass_kg": mass, "mass_source": mass_src, "rho_vehicle": rho_veh,
            "W_N": W, "velocity_ms": args.velocity, "g": G, "rho_water": RHO_W,
            "flotation_depth_m": d_float, "params": {k: {"value": v[0], "source": v[1]}
                                                     for k, v in PARAMS.items()},
            "lift_assumption": "L = 0, so F_F is an UPPER BOUND on available traction",
            "crossing_depths_m": cross, "rows": rows,
        }, indent=2))
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
