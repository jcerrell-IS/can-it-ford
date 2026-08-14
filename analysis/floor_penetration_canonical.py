"""Measure water-particle penetration of the floor plane in the 17 canonical runs.

WHY THIS EXISTS
A 16-paper literature search at 99 percent coverage found no paper reporting the
0.93 to 1.01 dx floor-penetration plateau measured in this project's MOVING scene,
and no defensible minimum cell count across a shallow water layer. The inference
that was NOT to be asserted, and that this script tests instead:

    if that penetration is a property of the enforced plane boundary condition
    rather than of one scene, then a corrupted layer of order one cell over a
    water column that is only 2.000 cells deep puts roughly 50 percent of the
    canonical column inside it.

The canonical set turns that into a real experiment rather than a single number.
Realized water depth is INVARIANT at 0.2944294 m across g48, g64 and g96, while
dx changes, so the same physical column is resolved at 1.500, 2.000 and 3.000
cells. Two hypotheses then separate cleanly:

    H_bc      penetration is a property of the boundary condition and the kernel
              support, so it is CONSTANT IN UNITS OF dx across the three grids.
    H_phys    penetration is a fixed physical distance, so it is CONSTANT IN
              METRES and shrinks in dx units as the grid refines.

H_bc is the one that would transfer to the moving scene and would put half the
canonical column in a corrupted layer. H_phys would not.

MECHANISM UNDER TEST (Steffen, Kirby and Berzins 2008, DOI 10.3970/CMES.2008.031.107):
with a quadratic or cubic B-spline a particle influences nodes 1.5 to 2 cells away,
so a particle can sit about a cell below a node-enforced plane and still be seen by
it. If that is the mechanism, penetration scales with basis support width, which is
measured in cells, which is H_bc.

WHAT THIS SCRIPT CAN AND CANNOT SHOW, stated before any number is produced.
CAN:  how far below the plane particles actually sit, in dx and in metres; how that
      scales across the three grids; and whether the near-floor layer's kinematics
      and packing differ from the bulk.
CANNOT: prove a stress error. Schulz and Sutmann 2019 report grid-based boundary
      treatment distorting stress MULTIPLE grid lengths into the body; penetration
      depth is a lower bound on the disturbed region, not a measurement of it.
      No paper reports an accepted correction for a smeared near-wall layer, so
      nothing here is calibrated out.

THE DENOMINATOR TRAP for any under-hull comparison. Water is CARVED out of
vehicle-occupied cells at scene construction (:186-196), so the region under the hull
does not start with its share of the water. Comparing the under-hull share of
PENETRATING particles against the under-hull share of FLOOR AREA is therefore biased,
and the correct denominator is the share of water actually present under the hull
footprint at that frame. Measured on g64_m1100 the bias turns out mild here (under-hull
water runs 8.8 to 11.2 percent against an 11.09 percent area share), but that is a
property of this scene, not a general licence to use the area share.

A STRUCTURAL CONFOUND FOUND BY DIRECT SOURCE READ, and it is load-bearing.
renders/yaris_render_s1/sim_standing.py:248-267 (_project_water) hard-clamps every
water particle to z >= floor - 0.25*dx at the START of each frame, and zeroes its
downward velocity. So accumulated penetration in this scene is capped at 0.25 dx by
the driver, not by the physics. The clamp runs before solver.step() and the recorded
position is read after it, so WITHIN-frame penetration is still recorded in full and
is the quantity to report. Any comparison against the moving scene, whose driver has
no such clamp, must carry this difference.

Reads only. Every input is under renders/yaris_render_s1/_incoming/, which register
D4a records as the canonical per-run tree. Nothing here writes to a canonical store.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

# The 17 gated runs, per data/all_runs_inventory.csv. Named explicitly rather than
# globbed so a stray directory cannot silently enter or leave the population.
CANONICAL = [
    "g48_m1100", "g48_m1609", "g48_m2337",
    "g64_m1100", "g64_m1609", "g64_m2337",
    "g96_m1100", "g96_m1609", "g96_m2337",
    "sweepD_g64_d0p25", "sweepD_g64_d0p35", "sweepD_g64_d0p45",
    "sweepV_g64_v0p5", "sweepV_g64_v1p0", "sweepV_g64_v2p0",
    "sweepV_g64_v2p5", "sweepV_g64_v3p0",
]

# Height bins above the floor, in units of dx, for the near-floor structure profile.
# Resolved finely enough that a one-cell layer is many bins wide at every grid.
PROFILE_EDGES = np.arange(0.0, 3.5 + 1e-9, 0.125)


def analyse_run(npz_path: Path, settle_frac: float = 0.5) -> dict:
    """Penetration and near-floor structure for one rollout.

    settle_frac names the trailing fraction of frames used for the time-averaged
    profile, so the initial transient does not dominate it. Penetration extremes
    are reported over ALL frames as well, because a transient penetration is still
    a real excursion of the boundary condition.
    """
    z = np.load(npz_path, mmap_mode="r")
    floor = float(z["floor"])
    dx = float(z["dx"])
    h = float(z["h"])
    water = z["water"]                      # (frames, n_water, 3) float32
    speed = z["speed"]                      # (frames, n_water)    float32
    n_frames, n_water, _ = water.shape
    f0 = int(n_frames * (1.0 - settle_frac))

    clamp_dx = 0.25                         # sim_standing.py:252, eps = 0.25*dx

    pen_all = []                            # penetration depths, dx units, all frames
    n_below = 0
    n_below_clamp = 0                       # deeper than the driver clamp
    per_frame_max = np.zeros(n_frames)
    per_frame_frac = np.zeros(n_frames)

    prof_counts = np.zeros(len(PROFILE_EDGES) - 1)
    prof_speed = np.zeros(len(PROFILE_EDGES) - 1)
    prof_frames = 0

    for f in range(n_frames):
        zc = np.asarray(water[f, :, 2], dtype=np.float64)
        hgt = (zc - floor) / dx             # height above the plane, in cells
        below = hgt < 0.0
        nb = int(below.sum())
        n_below += nb
        per_frame_frac[f] = nb / n_water
        if nb:
            pen = -hgt[below]               # positive depth below the plane, in dx
            pen_all.append(pen.astype(np.float32))
            per_frame_max[f] = float(pen.max())
            n_below_clamp += int((pen > clamp_dx + 1e-6).sum())

        if f >= f0:
            sp = np.asarray(speed[f], dtype=np.float64)
            idx = np.digitize(hgt, PROFILE_EDGES) - 1
            ok = (idx >= 0) & (idx < len(prof_counts))
            np.add.at(prof_counts, idx[ok], 1.0)
            np.add.at(prof_speed, idx[ok], sp[ok])
            prof_frames += 1

    pen_cat = np.concatenate(pen_all) if pen_all else np.zeros(0, dtype=np.float32)
    total_pf = n_frames * n_water

    def pct(q):
        return float(np.percentile(pen_cat, q)) if pen_cat.size else float("nan")

    with np.errstate(invalid="ignore", divide="ignore"):
        prof_mean_speed = np.where(prof_counts > 0, prof_speed / np.maximum(prof_counts, 1), np.nan)

    # Realized depth is the particle-seeding depth, not the --depth argument:
    # sim_standing.py:181 seeds layers at floor + 0.5h + k*h, so realized = layers*h.
    layers = int(round(float(z["depth"]) / h - 0.5 + 1e-9))
    layers = max(layers, 1)
    realized_depth = layers * h

    return {
        "run": npz_path.parent.name,
        "n_grid": int(z["n_grid"]),
        "frames": n_frames,
        "n_water": n_water,
        "dx_m": dx,
        "h_m": h,
        "floor_m": floor,
        "nominal_depth_m": float(z["depth"]),
        "velocity_ms": float(z["velocity"]),
        "water_layers": layers,
        "realized_depth_m": realized_depth,
        "depth_cells": realized_depth / dx,
        # --- penetration, the primary result ---
        "frac_particle_frames_below_floor": n_below / total_pf,
        "frac_particle_frames_below_clamp": n_below_clamp / total_pf,
        "pen_max_dx": float(pen_cat.max()) if pen_cat.size else 0.0,
        "pen_p99p9_dx": pct(99.9),
        "pen_p99_dx": pct(99.0),
        "pen_p50_dx": pct(50.0),
        "pen_mean_dx": float(pen_cat.mean()) if pen_cat.size else 0.0,
        "pen_max_m": (float(pen_cat.max()) * dx) if pen_cat.size else 0.0,
        "pen_p99_m": pct(99.0) * dx,
        "pen_mean_m": (float(pen_cat.mean()) * dx) if pen_cat.size else 0.0,
        "per_frame_max_dx_median": float(np.median(per_frame_max)),
        "per_frame_max_dx_late": float(np.median(per_frame_max[f0:])),
        "driver_clamp_dx": clamp_dx,
        # --- near-floor structure, time-averaged over the trailing frames ---
        "profile_frames": prof_frames,
        "profile_edges_dx": PROFILE_EDGES.tolist(),
        "profile_counts": (prof_counts / max(prof_frames, 1)).tolist(),
        "profile_mean_speed_ms": [None if np.isnan(v) else float(v) for v in prof_mean_speed],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--incoming", default="/Users/josie/can-it-ford/renders/yaris_render_s1/_incoming",
                   help="canonical per-run tree (register D4a); read-only")
    p.add_argument("--out", required=True, help="output directory on THIS branch")
    p.add_argument("--settle-frac", type=float, default=0.5)
    a = p.parse_args()

    inc = Path(a.incoming)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for name in CANONICAL:
        npz = inc / name / "rollout.npz"
        if not npz.exists():
            print("MISSING %s" % npz, flush=True)
            continue
        r = analyse_run(npz, settle_frac=a.settle_frac)
        results.append(r)
        print("%-20s g%-3d depth_cells=%.3f  below=%.4f%%  pen_max=%.3f dx  "
              "pen_p99=%.3f dx  pen_mean=%.4f dx (%.5f m)"
              % (r["run"], r["n_grid"], r["depth_cells"],
                 100.0 * r["frac_particle_frames_below_floor"],
                 r["pen_max_dx"], r["pen_p99_dx"], r["pen_mean_dx"], r["pen_mean_m"]),
              flush=True)

    (out / "floor_penetration_by_run.json").write_text(json.dumps(results, indent=2))

    cols = ["run", "n_grid", "dx_m", "realized_depth_m", "depth_cells", "velocity_ms",
            "frac_particle_frames_below_floor", "frac_particle_frames_below_clamp",
            "pen_max_dx", "pen_p99p9_dx", "pen_p99_dx", "pen_mean_dx",
            "pen_max_m", "pen_p99_m", "pen_mean_m", "driver_clamp_dx"]
    lines = [",".join(cols)]
    for r in results:
        lines.append(",".join(repr(r[c]) if not isinstance(r[c], str) else r[c] for c in cols))
    (out / "floor_penetration_by_run.csv").write_text("\n".join(lines) + "\n")

    # --- THE CROSSED CONTROL, and it is already inside the canonical set ---
    # The mass sweep varies dx at fixed realized depth. The DEPTH sweep varies realized
    # depth at fixed dx. Together they CROSS dx against depth-in-cells, so the two can be
    # separated instead of confounded:
    #   depth 1.500 cells is reached by g48 (dx 0.1963) AND by sweepD_g64_d0p25 (dx 0.1472)
    #   depth 3.000 cells is reached by g96 (dx 0.0981) AND by sweepD_g64_d0p45 (dx 0.1472)
    # If depth-in-cells controlled penetration, the two members of each pair would agree.
    grid_vals = sorted({round(r["dx_m"], 6) for r in results})
    cross = {}
    for r in results:
        cross.setdefault(round(r["depth_cells"], 3), {})[round(r["dx_m"], 6)] = r
    print("\n=== CROSSED CONTROL: dx against depth-in-cells ===", flush=True)
    print("cells below-floor %% of particle-frames, by dx", flush=True)
    print("%-11s | %s" % ("depth_cells", " | ".join("dx=%-9.6f" % d for d in grid_vals)),
          flush=True)
    for dc in sorted(cross):
        cells = []
        for dv in grid_vals:
            r = cross[dc].get(dv)
            cells.append("%6.2f%% %-12s" % (100.0 * r["frac_particle_frames_below_floor"],
                                            "(" + r["run"][:10] + ")") if r else "%-20s" % "-")
        print("%-11.3f | %s" % (dc, " | ".join(cells)), flush=True)

    crossed = {}
    for dc in sorted(cross):
        if len(cross[dc]) >= 2:
            crossed[str(dc)] = {str(k): {"run": v["run"],
                                         "frac_below": v["frac_particle_frames_below_floor"],
                                         "pen_max_dx": v["pen_max_dx"]}
                                for k, v in sorted(cross[dc].items())}

    # --- the discriminating test: dx-invariant or metre-invariant? ---
    # Held fixed across the three grids by construction: realized depth, mass sweep
    # membership, nominal depth 0.30, velocity 1.5. Only dx moves.
    ladder = [r for r in results if r["run"].startswith(("g48_", "g64_", "g96_"))]
    print("\n=== H_bc vs H_phys, the g48/g64/g96 ladder at fixed realized depth ===",
          flush=True)
    print("%-12s %-8s %-9s %-11s %-11s %-11s" %
          ("grid", "dx_m", "cells", "pen_p99_dx", "pen_p99_m", "pen_mean_dx"), flush=True)
    by_grid = {}
    for g in (48, 64, 96):
        sel = [r for r in ladder if r["n_grid"] == g]
        if not sel:
            continue
        by_grid[g] = {
            "dx_m": sel[0]["dx_m"],
            "depth_cells": sel[0]["depth_cells"],
            "pen_p99_dx": float(np.mean([r["pen_p99_dx"] for r in sel])),
            "pen_p99_m": float(np.mean([r["pen_p99_m"] for r in sel])),
            "pen_mean_dx": float(np.mean([r["pen_mean_dx"] for r in sel])),
            "pen_mean_m": float(np.mean([r["pen_mean_m"] for r in sel])),
            "n_runs": len(sel),
        }
        b = by_grid[g]
        print("g%-11d %-8.5f %-9.3f %-11.4f %-11.6f %-11.5f"
              % (g, b["dx_m"], b["depth_cells"], b["pen_p99_dx"], b["pen_p99_m"],
                 b["pen_mean_dx"]), flush=True)

    verdict = {}
    if len(by_grid) == 3:
        # Use the MEAN, not a percentile: a run that never crossed the plane has no
        # percentile (NaN) but a perfectly well defined mean penetration of zero.
        # Reporting NaN here once produced the false line "supports H_phys" from two
        # grids that in fact showed no penetration at all, which is neither hypothesis.
        dxs = np.array([by_grid[g]["pen_mean_dx"] for g in (48, 64, 96)])
        ms = np.array([by_grid[g]["pen_mean_m"] for g in (48, 64, 96)])
        # Non-monotonicity is checked FIRST and is disqualifying. Both H_bc and H_phys
        # predict a monotone (indeed constant, in their own units) trend. A pattern that
        # rises then falls is consistent with neither, and no coefficient of variation
        # should be allowed to name a winner in that case.
        monotone = bool((dxs[0] <= dxs[1] <= dxs[2]) or (dxs[0] >= dxs[1] >= dxs[2]))
        cv_dx = float(dxs.std(ddof=0) / dxs.mean()) if dxs.mean() > 0 else float("nan")
        cv_m = float(ms.std(ddof=0) / ms.mean()) if ms.mean() > 0 else float("nan")
        if not monotone:
            call = ("NEITHER. Penetration is NON-MONOTONE in dx (absent, present, absent "
                    "across g48/g64/g96), which no constant-in-dx or constant-in-metres "
                    "mechanism predicts.")
        elif np.isnan(cv_dx) or np.isnan(cv_m):
            call = "UNDETERMINED (a unit system has zero mean)."
        else:
            call = "dx (supports H_bc)" if cv_dx < cv_m else "metres (supports H_phys)"
        verdict = {
            "pen_mean_dx_by_grid": {str(g): by_grid[g]["pen_mean_dx"] for g in (48, 64, 96)},
            "pen_mean_m_by_grid": {str(g): by_grid[g]["pen_mean_m"] for g in (48, 64, 96)},
            "monotone_in_dx": monotone,
            "cv_in_dx_units": cv_dx,
            "cv_in_metres": cv_m,
            "call": call,
        }
        print("\npen_mean by grid, dx units : %s" % np.array2string(dxs, precision=5), flush=True)
        print("pen_mean by grid, metres   : %s" % np.array2string(ms, precision=6), flush=True)
        print("monotone in dx             : %s" % monotone, flush=True)
        print("CALL: %s" % call, flush=True)

    # A run with ZERO penetrating particles has no percentile to report, so its
    # pen_p99_dx is NaN by construction, not by failure. Treat a run that never
    # crossed the plane as penetration 0 for the invariance test, and say so.
    (out / "penetration_ladder_verdict.json").write_text(json.dumps({
        "by_grid": by_grid,
        "verdict": verdict,
        "crossed_control": crossed,
        "note": ("pen_p99 is NaN for a run with zero particles below the plane; such a "
                 "run is penetration-free, which is a result, not a missing value."),
    }, indent=2))
    print("\nWROTE %s" % out, flush=True)


if __name__ == "__main__":
    main()
