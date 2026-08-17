"""Free-surface depth at a FIXED station, versus the driver's moving-window diagnostic.

WHY. `local_depth_footprint` (sim_standing.py:473-475) takes the 99.5th percentile of water
z inside the vehicle's CURRENT bounding box. That box slides downstream as the vehicle
drifts, into the pile-up against the closed downstream wall. So the diagnostic entangles
two different things: the water getting deeper, and the measurement window moving into
deeper water.

This script separates them by recomputing the identical statistic over the vehicle's
FRAME-0 footprint, held fixed for the whole run. Same percentile, same floor datum, same
selection logic; only the window differs.

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

RUNS = "/Users/josie/can-it-ford/renders/yaris_render_s1/_incoming/*/rollout.npz"
PCTL = 99.5          # identical to sim_standing.py:470,474
MIN_SEL = 20         # identical guard


def measure(path, settle=8):
    z = np.load(path)
    w = z["water"]
    floor = float(z["floor"])
    veh0 = z["veh_particles_scene0"]      # frame-0 vehicle particles: the fixed footprint
    lo, hi = veh0.min(0), veh0.max(0)
    t = z["t"]
    drift = float(np.linalg.norm(t[-1] - t[0]))

    fixed = []
    for f in range(settle, w.shape[0]):
        ww = w[f]
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
        print("  i.e. the driver's diagnostic reads high exactly when the vehicle has moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
