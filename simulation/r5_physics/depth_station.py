"""Free-surface depth at a FIXED station, versus the driver's moving-window diagnostic.

WHY. `local_depth_footprint` (sim_standing.py:315-317) takes the 99.5th percentile of water
z inside the vehicle's CURRENT bounding box. That box slides downstream as the vehicle
drifts, into the pile-up against the closed downstream wall. So the diagnostic entangles
two different things: the water getting deeper, and the measurement window moving into
deeper water.

This script separates them by recomputing the identical statistic over the vehicle's
FRAME-0 footprint, held fixed for the whole run. Same percentile, same floor datum, same
selection logic; only the window differs.

WITHDRAWN IN PART, review 2026-08-17: this fixed station is NOT vehicle-free. Occupancy of
the frame-0 footprint collapses 96.9 -&gt; 6.6 percent across the sweep and correlates with the
reading at -0.951, so it swaps one perfect confound for another. Vehicle-free controls give
1.132x (non-monotone) and 1.374x (mass-based). Treat 1.81x as an upper bound.

Result on the canonical velocity sweep: the moving window spans 2.58x across v = 0.5 to
3.0, the fixed station spans 1.81x. Both are monotone in velocity. So the depth confound is
real but roughly 40 percent smaller than the driver's own diagnostic implies, and the
remainder is a measurement artifact that inflates with drift.

Run:  python simulation/r5_physics/depth_station.py [--settle 8]
"""
from __future__ import annotations

import argparse
import glob
import os

import numpy as np

RUNS = os.environ.get(
    "CANFORD_RUNS",
    # Data lives in the MAIN checkout, not in this worktree; a checkout of this branch
    # alone cannot reproduce these numbers. Override with CANFORD_RUNS. Flagged by review.
    "/Users/josie/can-it-ford/renders/yaris_render_s1/_incoming/*/rollout.npz")
PCTL = 99.5          # identical to sim_standing.py:313,317
MIN_SEL = 20         # identical guard


# --------------------------------------------------------------------------------------
# GHOST GUARD, added 2026-08-17 after review found the failure mode.
# --------------------------------------------------------------------------------------
def active_water(z, frame_water):
    """Return (water, n_ghosts) with RETIRED particles removed.

    Why this exists. `outflow_deactivate.py` retires water by setting
    `particle_selection` non-zero. A retired particle does NOT leave: advection is inside
    `g2p_particle` (`mpm_utils.py:1026`) behind the gate at `:1049`, so it **freezes in
    place and stays in the array**. `sim_standing.py:294` dumps `w = x[:n_water]` with no
    selection filter, so frozen ghosts land in `rollout.npz` looking exactly like water.

    Every depth statistic here is a high percentile of water z, and the ghosts are by
    construction the particles that were ABOVE the retirement target, frozen there
    forever. Unfiltered, a retirement run reports a level that is flat to three decimals
    and made of dead water. Review measured 0.7339-0.7347 over 60 ticks against a live
    surface at 0.6609.

    Contract: a run that used retirement MUST dump a boolean `retired` array. If the
    archive carries one, it is applied. If it does not, this returns the water unchanged,
    which is correct for all 17 canonical runs because none of them ever wrote
    `particle_selection`; the repo-wide grep for it returns only prose.
    """
    if "retired" not in getattr(z, "files", []):
        return frame_water, 0
    mask = np.asarray(z["retired"], dtype=bool).ravel()
    if mask.size != frame_water.shape[0]:
        raise ValueError(
            f"`retired` mask has {mask.size} entries against {frame_water.shape[0]} water "
            f"particles. Refusing to guess the alignment: a mis-aligned ghost filter is "
            f"worse than none, because it silently deletes live water instead.")
    return frame_water[~mask], int(mask.sum())


def measure(path, settle=8):
    z = np.load(path)
    w = z["water"]
    floor = float(z["floor"])
    veh0 = z["veh_particles_scene0"]      # frame-0 vehicle particles: the fixed footprint
    lo, hi = veh0.min(0), veh0.max(0)
    t = z["t"]
    drift = float(np.linalg.norm(t[-1] - t[0]))

    fixed = []
    n_ghost = 0
    for f in range(settle, w.shape[0]):
        ww, n_ghost = active_water(z, w[f])          # ghost guard
        sel = ((ww[:, 0] >= lo[0]) & (ww[:, 0] <= hi[0]) &
               (ww[:, 1] >= lo[1]) & (ww[:, 1] <= hi[1]) & (ww[:, 2] >= floor))
        fixed.append(np.percentile(ww[sel, 2], PCTL) - floor
                     if sel.sum() >= MIN_SEL else np.nan)
    moving = np.asarray(z["local_depth_footprint"], dtype=float)[settle:]
    return {
        "run": os.path.basename(os.path.dirname(path)),
        "velocity": float(z["velocity"]),
        "nominal_depth": float(z["depth"]),
        "moving_median": float(np.nanmedian(moving)),
        "fixed_median": float(np.nanmedian(fixed)),
        "drift_m": drift,
        "ghosts_filtered": n_ghost,
    }


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--settle", type=int, default=8)
    a = p.parse_args()

    rows = [measure(f, a.settle) for f in sorted(glob.glob(RUNS))]
    print(f"settle={a.settle}, N={len(rows)}. 99.5th pct of water z over the footprint, "
          f"minus floor.\n")
    print(f"{'run':<20} {'v':>5} {'nom':>6} {'moving':>8} {'FIXED':>8} {'drift':>7} {'bias':>8}")
    for r in rows:
        print(f"{r['run']:<20} {r['velocity']:5.1f} {r['nominal_depth']:6.2f} "
              f"{r['moving_median']:8.4f} {r['fixed_median']:8.4f} {r['drift_m']:7.4f} "
              f"{r['moving_median'] - r['fixed_median']:+8.4f}")

    sweep = sorted([r for r in rows if r["nominal_depth"] == 0.30], key=lambda r: r["velocity"])
    if len(sweep) >= 2:
        mv = np.array([r["moving_median"] for r in sweep])
        fx = np.array([r["fixed_median"] for r in sweep])
        print(f"\nVELOCITY SWEEP (all labelled 0.30 m), N={len(sweep)}:")
        print(f"  moving window span {mv.max() / mv.min():.2f}x, monotone={bool(np.all(np.diff(mv) > 0))}")
        print(f"  FIXED station span {fx.max() / fx.min():.2f}x, monotone={bool(np.all(np.diff(fx) > 0))}")
        print(f"  fixed-station depth vs the 0.30 m label: "
              f"{100 * (fx.min() - 0.30) / 0.30:+.0f}% to {100 * (fx.max() - 0.30) / 0.30:+.0f}%")

    d = np.array([r["drift_m"] for r in rows])
    b = np.array([r["moving_median"] - r["fixed_median"] for r in rows])
    if len(d) > 2:
        print(f"\n  correlation(drift, moving-minus-fixed bias) = {np.corrcoef(d, b)[0, 1]:+.3f}")
        print(f"  bias is NEGATIVE in {int((b < 0).sum())}/{len(b)} runs, "
              f"range {b.min():+.4f} to {b.max():+.4f} m")
        keep = d < 0.6
        if keep.sum() > 2:
            print(f"  with drift >= 0.6 m removed (N={int(keep.sum())}): "
                  f"r = {np.corrcoef(d[keep], b[keep])[0, 1]:+.3f}")
        print("  CORRECTED after review 2026-08-17: the Pearson r is carried by ~5 high-drift")
        print("  runs and the bias CHANGES SIGN near 0.6-0.9 m of drift. The diagnostic does")
        print("  NOT simply 'read high', and nothing here is proportional. These 17 runs are")
        print("  also five overlapping designed sweeps sharing a run, not independent draws,")
        print("  so this r is descriptive co-variation and not an effect size.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
