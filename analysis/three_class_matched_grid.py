"""Design the three-class matched-resolution matrix, and prove the grid arithmetic first.

WHY THIS EXISTS. Fixed n_grid is NOT fixed resolution across vehicles. sim_standing.py
derives the domain edge from the loaded hull:

    lim = max(2.2*extent[1], 3.5*extent[0], 6.0*depth)      sim_standing.py:160
    dx  = lim / n_grid                                       core/solver.py:53-54
    h   = dx / 2                                             sim_standing.py:163

so a shared n_grid gives each vehicle a different cell size AND a different realized
water depth. This module picks a PER-VEHICLE n_grid so that dx is matched instead, and
prints what was actually achieved rather than what was intended.

REALIZED DEPTH IS NOT THE NOMINAL --depth. The water block is built as
    zs = arange(floor + 0.5*h, floor + depth, h)             sim_standing.py:181
so the layer count is ceil(depth/h - 0.5) and the realized depth is n_layers*h. It is
quantized in steps of h, which is why matching dx is the ONLY way to match realized
depth: the layer count is an integer, and one layer is ~25 percent of the depth here.

VERIFICATION. The extents are read from the .ply vertex blocks (stdlib struct, no
numpy on this Mac). The transform is confirmed, not assumed: load_vehicle(up="z")
puts the mesh's long axis (raw PLY x) on scene y, so extent[1] is the raw x extent.
That reproduces three independently-known dx values to 4 significant figures. See
verify_against_known() below; it runs on import of __main__ and refuses to plan if it
fails.

Engine: warpmpm (NOT Genesis). This is a COMPANION experiment, non-canonical.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Measured live 2026-08-14 from the vertex blocks of the three qualified hulls, and
# anchored by sha256 rather than by path because the mesh pipeline is NOT
# bit-reproducible (same effective arguments give a different digest, and at g96 even
# a different face count). Volumes are from vehicle_meshes/candidates/SUMMARY.md,
# re-measured 2026-08-08 with the same trimesh loader the 17 gated runs used.
#
# extent_ply is the raw PLY bounding box (x, y, z). The scene's vehicle.extent is a
# permutation of it: scene extent[0] = raw y, extent[1] = raw x.
HULLS = {
    "yaris": {
        "vehicle_class": "small_passenger",
        "arr_class": "compact_sedan",
        "file": "yaris_coarse_v1l_watertight.ply",
        "sha256": "b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95",
        "extent_ply": (4.282610143, 1.746378005, 1.518008132),
        "n_vertices": 327212,
        "hull_m3": 3.542739,
        # AR&R class figure AND the deck header mass; for the Yaris the two coincide.
        "mass_kg": 1100.0,
        "mass_source": "vehicle_params.py mass_kg 1100.0; also Yaris deck header line 28",
        "mass_alt_kg": None,
        "mass_alt_source": None,
    },
    "rogue": {
        "vehicle_class": "large_passenger",
        "arr_class": "midsize_suv",
        "file": "rogue_g96_pd8_coarse_watertight.ply",
        "sha256": "c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2",
        "extent_ply": (4.746607304, 2.010111690, 1.729385391),
        "n_vertices": 36074,
        "hull_m3": 4.950341,
        "mass_kg": 1609.0,
        "mass_source": "AR&R large_passenger class figure (gates_both_scenarios.py:22)",
        # 1571.3 traced live 2026-08-14 to sim_standing.py:54 (mass_alt_kg). It is a
        # cars.com 2020 Rogue FWD S curb weight of 3464 lb; the Rogue deck states no
        # mass at all, unlike the Yaris and Silverado decks.
        "mass_alt_kg": 1571.3,
        "mass_alt_source": "Rogue web-sourced curb mass; the Rogue deck states no mass at all",
    },
    "silverado": {
        "vehicle_class": "large_4wd",
        "arr_class": "large_4wd",
        "file": "silverado_g96_pd8_coarse_watertight.ply",
        "sha256": "46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9",
        "extent_ply": (5.939969540, 2.337685943, 2.010161832),
        "n_vertices": 26072,
        "hull_m3": 7.962083,
        "mass_kg": 2337.0,
        "mass_source": "AR&R large_4wd class figure (gates_both_scenarios.py:23)",
        "mass_alt_kg": 2270.0,
        "mass_alt_source": "Silverado deck header line 28 mass",
    },
}

ORDER = ("yaris", "rogue", "silverado")

# Scene constants, all read from sim_standing.py rather than recalled.
WALL_CELLS = 4.0      # wall = 4.0*dx            :178
FLOOR_CELLS = 3.0     # floor = 3.0*dx           :164
INFLOW_LEN = 1.5      # metres, ABSOLUTE, not scaled by domain    :155, :223
PLACE_FRAC = (0.60, 0.50)  # vx, vy = 0.60*lim, 0.50*lim          :174


def scene_extent(extent_ply):
    """Map the raw PLY bbox to the scene's vehicle.extent.

    load_vehicle(path, up="z") rotates the mesh so its long axis lies on scene y,
    while the .ply stores it on x. Confirmed against three known dx values.
    """
    x, y, z = extent_ply
    return (y, x, z)


def domain_edge(extent_ply, depth):
    """sim_standing.py:160."""
    ext = scene_extent(extent_ply)
    return max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth)


def water_layers(depth, h):
    """Length of arange(floor+0.5h, floor+depth, h). sim_standing.py:181."""
    n = math.ceil(depth / h - 0.5)
    return max(int(n), 0)


def axis_count(lim, wall, h):
    """Length of arange(wall+0.5h, lim-wall-0.5h, h). sim_standing.py:179-180."""
    span = (lim - wall - 0.5 * h) - (wall + 0.5 * h)
    return max(int(math.ceil(span / h)), 0)


def realize(key, n_grid, depth):
    """Everything the scene derives, for one vehicle at one n_grid."""
    hull = HULLS[key]
    lim = domain_edge(hull["extent_ply"], depth)
    dx = lim / n_grid
    h = dx / 2.0
    wall = WALL_CELLS * dx
    nz = water_layers(depth, h)
    nx = axis_count(lim, wall, h)
    n_water = nx * nx * nz
    realized_depth = nz * h
    free_span = lim - 2.0 * wall
    return {
        "vehicle": key,
        "vehicle_class": hull["vehicle_class"],
        "n_grid": n_grid,
        "grid_lim_m": lim,
        "dx_m": dx,
        "h_m": h,
        "nominal_depth_m": depth,
        "water_layers": nz,
        "realized_depth_m": realized_depth,
        "depth_over_dx": realized_depth / dx,
        "wall_m": wall,
        "floor_m": FLOOR_CELLS * dx,
        "free_span_m": free_span,
        "n_water_before_carve": n_water,
        "water_volume_m3": free_span * free_span * realized_depth,
        # Residual confounds that matching dx does NOT remove, reported not hidden.
        "vehicle_x_m": PLACE_FRAC[0] * lim,
        "inflow_x_m": wall + INFLOW_LEN,
        "inflow_to_vehicle_m": PLACE_FRAC[0] * lim - (wall + INFLOW_LEN),
        "hull_m3": hull["hull_m3"],
        "blockage_hull_over_water": hull["hull_m3"] / (free_span * free_span * realized_depth),
    }


def verify_against_known():
    """Refuse to plan unless the extent->dx chain reproduces known values.

    Three independent anchors, none of them derived from this file:
      Yaris g64 dx  0.1472147236519959  (CLAUDE.md L-3, quoted from
                                         data/all_runs_inventory.csv)
      Yaris g96 dx  0.0981   Rogue g96 dx  0.1088   Silverado g96 dx  0.1361
                                        (reconciliation dispatch trap 3)
    """
    checks = []
    lim_y = domain_edge(HULLS["yaris"]["extent_ply"], 0.30)
    checks.append(("yaris g64 dx", lim_y / 64, 0.1472147236519959, 1e-7))
    checks.append(("yaris g96 dx", lim_y / 96, 0.0981, 5e-5))
    checks.append(("rogue g96 dx",
                   domain_edge(HULLS["rogue"]["extent_ply"], 0.30) / 96, 0.1088, 5e-5))
    checks.append(("silverado g96 dx",
                   domain_edge(HULLS["silverado"]["extent_ply"], 0.30) / 96, 0.1361, 5e-5))
    # The canonical realized depth, which must fall out of the layer arithmetic.
    h64 = lim_y / 64 / 2.0
    checks.append(("yaris g64 realized depth",
                   water_layers(0.30, h64) * h64, 0.2944294473039918, 1e-7))

    ok = True
    print("VERIFY extent -> lim -> dx chain, against values this file did not produce")
    for name, got, want, tol in checks:
        d = abs(got - want)
        flag = "OK  " if d <= tol else "FAIL"
        if d > tol:
            ok = False
        print("  %s %-26s got %.10f  want %.10f  |d| %.2e  tol %.0e"
              % (flag, name, got, want, d, tol))
    if not ok:
        raise SystemExit(
            "VERIFY FAILED. The extent->dx chain does not reproduce known values, so "
            "every number this script would print is unsafe. Do not plan a run.")
    print("  all anchors reproduce; the scene_extent permutation is confirmed, "
          "not assumed\n")
    return True


def search_matched(depth, n_ref_lo, n_ref_hi, max_n, top=8):
    """Find per-vehicle n_grid triples that minimise the spread in dx.

    The domain edges are irrational-ish measured floats, so an EXACT common dx does
    not exist for any integer triple. This reports the achieved spread rather than
    claiming a match.
    """
    lims = {k: domain_edge(HULLS[k]["extent_ply"], depth) for k in ORDER}
    out = []
    for n_ref in range(n_ref_lo, n_ref_hi + 1):
        dx_target = lims["yaris"] / n_ref
        trial = {"yaris": n_ref}
        for k in ORDER[1:]:
            n = int(round(lims[k] / dx_target))
            if n < 8 or n > max_n:
                trial = None
                break
            trial[k] = n
        if trial is None:
            continue
        dxs = {k: lims[k] / trial[k] for k in ORDER}
        lo, hi = min(dxs.values()), max(dxs.values())
        spread = (hi - lo) / lo
        # A layer-count mismatch would break the realized-depth match outright.
        layers = {k: water_layers(depth, dxs[k] / 2.0) for k in ORDER}
        depths = {k: layers[k] * dxs[k] / 2.0 for k in ORDER}
        dlo, dhi = min(depths.values()), max(depths.values())
        out.append({
            "n": dict(trial), "dx": dxs, "spread_pct": 100.0 * spread,
            "layers": layers, "depths": depths,
            "depth_spread_pct": 100.0 * (dhi - dlo) / dlo,
            "layers_equal": len(set(layers.values())) == 1,
            "cost": sum(realize(k, trial[k], depth)["n_water_before_carve"] for k in ORDER),
        })
    out.sort(key=lambda r: (not r["layers_equal"], r["spread_pct"]))
    return out[:top]


def fmt_plan(rows):
    hdr = ("vehicle", "n_grid", "dx_m", "realized_depth_m", "depth/dx",
           "water_layers", "n_water", "grid_lim_m")
    print("%-11s %6s %12s %17s %9s %13s %10s %11s" % hdr)
    for r in rows:
        print("%-11s %6d %12.7f %17.9f %9.3f %13d %10d %11.5f"
              % (r["vehicle"], r["n_grid"], r["dx_m"], r["realized_depth_m"],
                 r["depth_over_dx"], r["water_layers"], r["n_water_before_carve"],
                 r["grid_lim_m"]))


def equal_density_masses(rho_ref):
    """Masses that give all three hulls the SAME bulk density.

    This rules DENSITY out. It does NOT separate mass from geometry, and an earlier
    version of this docstring wrongly claimed it did: holding density fixed forces
    mass to scale with volume, so mass and displaced volume stay rank-correlated.
    Separating them needs a MASS SWAP that breaks the correlation, which is arm X
    in scripts/run_three_class_massswap.sh.

    rho_ref = 310.494 is the canonical Yaris working density (1100/3.542739), so
    the Yaris arm is unchanged at 1100 kg by construction and acts as its own
    no-forcing control: if it does not reproduce Arm M, the difference is run-to-run
    draw, not geometry. Register item 17 records this stack as non-deterministic at
    fixed configuration, so that check is not optional.
    """
    return {k: rho_ref * HULLS[k]["hull_m3"] for k in ORDER}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--depth", type=float, default=0.30,
                   help="nominal --depth handed to sim_standing.py")
    p.add_argument("--n-ref-lo", type=int, default=88)
    p.add_argument("--n-ref-hi", type=int, default=136)
    p.add_argument("--max-n", type=int, default=200)
    p.add_argument("--triple", default=None,
                   help="explicit n_grid triple 'yaris,rogue,silverado' to report "
                        "instead of the search winner")
    a = p.parse_args()

    verify_against_known()

    print("SHARED-n_grid arm, the confound this experiment exists to remove")
    fmt_plan([realize(k, 96, a.depth) for k in ORDER])
    dxs = [realize(k, 96, a.depth)["dx_m"] for k in ORDER]
    ds = [realize(k, 96, a.depth)["realized_depth_m"] for k in ORDER]
    print("  dx spread %.2f%%, realized-depth spread %.2f%% at a shared n_grid=96\n"
          % (100.0 * (max(dxs) - min(dxs)) / min(dxs),
             100.0 * (max(ds) - min(ds)) / min(ds)))

    print("MATCHED-dx candidates, ranked by achieved dx spread")
    print("%-28s %10s %10s %10s %12s" % ("n_grid (yaris/rogue/silv)", "dx spread",
                                         "depth spr", "layers eq", "sum n_water"))
    cands = search_matched(a.depth, a.n_ref_lo, a.n_ref_hi, a.max_n, top=10)
    for c in cands:
        print("%-28s %9.4f%% %9.4f%% %10s %12d"
              % ("%d / %d / %d" % (c["n"]["yaris"], c["n"]["rogue"], c["n"]["silverado"]),
                 c["spread_pct"], c["depth_spread_pct"],
                 str(c["layers_equal"]), c["cost"]))
    print()

    if a.triple:
        parts = [int(t) for t in a.triple.split(",")]
        if len(parts) != 3:
            raise SystemExit("--triple needs three integers")
        sel = dict(zip(ORDER, parts))
        dxs_sel = {k: domain_edge(HULLS[k]["extent_ply"], a.depth) / sel[k] for k in ORDER}
        lo, hi = min(dxs_sel.values()), max(dxs_sel.values())
        ds_sel = {k: realize(k, sel[k], a.depth)["realized_depth_m"] for k in ORDER}
        dlo, dhi = min(ds_sel.values()), max(ds_sel.values())
        best = {"n": sel, "spread_pct": 100.0 * (hi - lo) / lo,
                "depth_spread_pct": 100.0 * (dhi - dlo) / dlo}
    else:
        best = cands[0]
    print("SELECTED matched-dx arm: n_grid %d / %d / %d"
          % (best["n"]["yaris"], best["n"]["rogue"], best["n"]["silverado"]))
    rows = [realize(k, best["n"][k], a.depth) for k in ORDER]
    fmt_plan(rows)
    print("  achieved dx spread %.4f%%, realized-depth spread %.4f%%"
          % (best["spread_pct"], best["depth_spread_pct"]))
    print()

    print("RESIDUAL CONFOUNDS that matching dx does NOT remove, stated not hidden")
    print("%-11s %12s %14s %18s %20s" % ("vehicle", "free_span_m", "water_vol_m3",
                                         "inflow->vehicle_m", "hull/water_vol"))
    for r in rows:
        print("%-11s %12.5f %14.3f %18.4f %20.5f"
              % (r["vehicle"], r["free_span_m"], r["water_volume_m3"],
                 r["inflow_to_vehicle_m"], r["blockage_hull_over_water"]))
    print("  The domain edge scales with the hull, so tank width, water volume and the")
    print("  upstream fetch from the fixed 1.5 m inflow band to the vehicle all differ")
    print("  across the three. Matching dx fixes RESOLUTION, not the tank.")
    print()

    print("DENSITY, both mass choices, never merged")
    print("%-11s %10s %12s %12s %12s %12s"
          % ("vehicle", "hull_m3", "mass_kg", "rho", "mass_alt", "rho_alt"))
    for k in ORDER:
        hu = HULLS[k]
        rho = hu["mass_kg"] / hu["hull_m3"]
        if hu["mass_alt_kg"] is None:
            print("%-11s %10.6f %12.1f %12.3f %12s %12s"
                  % (k, hu["hull_m3"], hu["mass_kg"], rho, "-", "-"))
        else:
            print("%-11s %10.6f %12.1f %12.3f %12.1f %12.3f"
                  % (k, hu["hull_m3"], hu["mass_kg"], rho, hu["mass_alt_kg"],
                     hu["mass_alt_kg"] / hu["hull_m3"]))
    print("  rho here is mass/HULL volume. The solver's realized rho divides by the")
    print("  SOLIDIFIED particle volume (n_particles*h^3), which is resolution")
    print("  dependent, so the run's own PREFLIGHT realized_rho is the one to quote.")
    print()

    rho_ref = HULLS["yaris"]["mass_kg"] / HULLS["yaris"]["hull_m3"]
    eq = equal_density_masses(rho_ref)
    print("EQUAL-DENSITY CONTROL ARM, rho held at the canonical Yaris %.6f kg/m3" % rho_ref)
    print("%-11s %12s %12s %14s" % ("vehicle", "mass_kg", "rho_check", "vs own mass"))
    for k in ORDER:
        own = HULLS[k]["mass_kg"] if HULLS[k]["mass_alt_kg"] is None else HULLS[k]["mass_alt_kg"]
        print("%-11s %12.3f %12.6f %13.2f%%"
              % (k, eq[k], eq[k] / HULLS[k]["hull_m3"], 100.0 * (eq[k] - own) / own))
    print("  Same three hulls, same matched dx, identical bulk density. This rules")
    print("  DENSITY out. It does NOT separate mass from geometry: holding density")
    print("  fixed forces mass to scale with volume, so the two stay rank-correlated.")


if __name__ == "__main__":
    main()
