"""Water spin-down in the canonical scene, measured reproducibly.

WHY THIS FILE EXISTS AT ALL: an adversarial review failed my spin-down numbers on run
provenance. They were tagged [measured] in a document while no committed script produced
them, so nobody could re-derive or audit them. That is the project's own standing rule and
I broke it. This file is the fix.

It also corrects three defects the same review found in the numbers themselves:

  1. SETTLE LABEL. The figures were reported as "settle 8" and were computed frame 0 to 89.
     The recorded series starts AT the kick (sim_standing.py:240 applies it right after the
     8 settle frames), so frame 0 is the kick frame and a settle-8 window is frames 8..89.
     Both are reported here, labelled.

  2. ORIGIN. `mean z` was absolute simulation z, whose origin is arbitrary; the floor sits
     at 3*dx. A level must be referenced to the floor. On the absolute origin the level
     proxy looked ~17x stiffer than the flow; on the floor datum it is ~3.8x.

  3. SPRAY. The centroid rise is dominated by particles thrown above the initial free
     surface. Excluding them, the bulk centroid FALLS in a substantial fraction of runs, so
     the rise is not "sustained redistribution" of the bulk.

Run:
  python simulation/r5_physics/spin_down.py [--settle 8] [--json out.json]
"""
from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np

RUNS = os.environ.get(
    "CANFORD_RUNS",
    # Data lives in the MAIN checkout, not in this worktree; a checkout of this branch
    # alone cannot reproduce these numbers. Override with CANFORD_RUNS. Flagged by review.
    "/Users/josie/can-it-ford/renders/yaris_render_s1/_incoming/*/rollout.npz")


def measure(path, settle=8):
    z = np.load(path)
    w = z["water"]                       # (frames, n_water, 3)
    sp = z["speed"].mean(axis=1).astype(float)
    floor = float(z["floor"])
    n = w.shape[0]
    a, b = settle, n - 1

    zc = w[:, :, 2].astype(float)
    mean_abs = zc.mean(axis=1)
    mean_rel = mean_abs - floor          # the only datum a level has

    # Free surface at the first retained frame, taken as a high percentile of z.
    surf0 = float(np.percentile(zc[a], 99.0))
    spray = (zc > surf0)
    frac_spray = spray.mean(axis=1)
    # bulk centroid with spray excluded, relative to the floor
    bulk = np.array([zc[i][~spray[i]].mean() if (~spray[i]).any() else np.nan
                     for i in (a, b)]) - floor

    def pct(x0, x1):
        return 100.0 * (x1 - x0) / x0 if x0 else float("nan")

    return {
        "run": os.path.basename(os.path.dirname(path)),
        "n_frames": int(n),
        "n_water": int(w.shape[1]),
        "floor_m": floor,
        "speed_pct": pct(sp[a], sp[b]),
        "meanz_abs_pct": pct(mean_abs[a], mean_abs[b]),
        "meanz_floor_pct": pct(mean_rel[a], mean_rel[b]),
        "bulk_nospray_floor_pct": pct(bulk[0], bulk[1]),
        "spray_frac_start": float(frac_spray[a]),
        "spray_frac_end": float(frac_spray[b]),
        # A two-point difference hides an oscillation; report the peak too.
        "meanz_floor_peak_pct": pct(mean_rel[a], float(mean_rel[a:].max())),
        "meanz_peak_frame": int(a + np.argmax(mean_rel[a:])),
    }


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--settle", type=int, default=8,
                   help="first RETAINED frame; 0 reproduces the superseded figures")
    p.add_argument("--json", default="")
    a = p.parse_args()

    rows = [measure(f, a.settle) for f in sorted(glob.glob(RUNS))]
    print(f"settle={a.settle} (first retained frame), N={len(rows)} runs\n")
    hdr = (f"{'run':<20} {'speed%':>8} {'z_abs%':>8} {'z_floor%':>9} "
           f"{'bulk%':>8} {'spray0':>7} {'sprayN':>7} {'peak%':>7}")
    print(hdr)
    for r in rows:
        print(f"{r['run']:<20} {r['speed_pct']:8.1f} {r['meanz_abs_pct']:8.2f} "
              f"{r['meanz_floor_pct']:9.2f} {r['bulk_nospray_floor_pct']:8.2f} "
              f"{r['spray_frac_start']:7.3f} {r['spray_frac_end']:7.3f} "
              f"{r['meanz_floor_peak_pct']:7.2f}")

    def stat(k):
        v = np.array([r[k] for r in rows], dtype=float)
        v = v[np.isfinite(v)]
        return np.median(v), v.min(), v.max()

    print()
    for k, label in (("speed_pct", "bulk mean speed"),
                     ("meanz_abs_pct", "mean z, ABSOLUTE origin (misleading)"),
                     ("meanz_floor_pct", "mean z, FLOOR datum"),
                     ("bulk_nospray_floor_pct", "bulk centroid, spray excluded")):
        m, lo, hi = stat(k)
        print(f"  {label:<38} median {m:+7.2f}%  range {lo:+7.2f} to {hi:+7.2f}%")
    neg = sum(1 for r in rows if r["bulk_nospray_floor_pct"] < 0)
    print(f"\n  bulk centroid FALLS once spray is excluded: {neg}/{len(rows)} runs")
    sm, slo, shi = stat("speed_pct")
    fm, _, _ = stat("meanz_floor_pct")
    print(f"  level stiffness vs flow, floor datum: {abs(fm / sm):.3f} "
          f"(i.e. {abs(sm / fm):.1f}x stiffer, NOT the 17x an absolute origin implies)")

    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"settle": a.settle, "rows": rows}, fh, indent=2, sort_keys=True)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
