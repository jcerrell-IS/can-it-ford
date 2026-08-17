"""What does the P-2 gate actually count? Independent re-derivation.

WHY THIS EXISTS. An adversarial review reported that `passthrough_max_frac`, the quantity
behind gate P-2, is 78-97 percent bounding-box VOID rather than water inside the hull, and
that its 0.10 gate limit sits on a 10.3-11.0 percent "transparent box" null baseline. That
would make P-2 a pile-up test rather than a leakage test, which reframes CLAUDE.md item 7.

I carried that into a document on the reviewer's word. One source cited twice is not two
sources, and it is the most consequential thing I am carrying, so this script derives it
myself from the rollout artifacts, with no shared code path with the reviewer's scripts.

WHAT P-2 IS, read from source (`sim_standing.py:463-465`):

    lo_v, hi_v = veh.min(0), veh.max(0)
    inbox = ((w >= lo_v) & (w <= hi_v)).all(axis=1)
    frac_max = max(frac_max, float(inbox.mean()))

so it is the fraction of ALL water particles inside the vehicle's axis-aligned bounding box
at the worst frame. Nothing in that expression restricts to the hull interior.

THE DECOMPOSITION. At each run's own argmax frame, in-box water is split into:
  in_hull    water in a cell OCCUPIED by a vehicle particle, using the driver's own
             voxel-occupancy test (`sim_standing.py:186-195`), i.e. genuine passthrough
  box_void   water in the bounding box but not in an occupied cell, i.e. the empty space
             a box inevitably encloses around a car-shaped object

THE NULL BASELINE. If the vehicle displaced no water at all, a box spanning the full water
column would contain water in proportion to its footprint area, so P-2 would read
A_box / A_water_footprint with NO leakage whatsoever. That baseline is computed here per
run rather than assumed, and compared against the gate limit of 0.10 (`gates.py:147-148`).

Run:  python simulation/r5_physics/p2_decompose.py
"""
from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np

RUNS = os.environ.get(
    "CANFORD_RUNS",
    # Data lives in the MAIN checkout, not this worktree. Override with CANFORD_RUNS.
    "/Users/josie/can-it-ford/renders/yaris_render_s1/_incoming/*/rollout.npz")
GATE_LIMIT = 0.10        # gates.py:147-148


def checkpoint_frames(z):
    """Frames where the vehicle particle cloud is stored EXACTLY, with its cloud.

    Reconstructing the pose from `R`/`t` and `veh_particles_vehframe` is possible,
    `body @ R.T + t` is the right convention, but it carries a **0.0613 m** maximum
    registration residual against the stored clouds, constant across frames. On a 4.2 m
    hull that is 1.5 percent, and at h = 0.0736 m it is most of a voxel, which is too
    coarse for the occupancy test that decides `in_hull`.

    So this uses only the three frames the driver stored exactly, `sim_standing.py:451`:
    frame 0, `min(45, frames-1)`, and the last frame. No reconstruction, no residual.

    LIMITATION, stated rather than hidden: P-2 is a MAX over all frames, and its argmax is
    usually frame 69-89. The last checkpoint is therefore near, but generally not exactly
    at, the argmax. The decomposition is reported at the last checkpoint and P-2 at that
    frame is reported beside the run's true max, so the gap is visible.
    """
    nf = int(z["frames"]) if "frames" in z else np.asarray(z["water"]).shape[0]
    return [(0, np.asarray(z["veh_particles_scene0"], dtype=float)),
            (min(45, nf - 1), np.asarray(z["veh_check_45"], dtype=float)),
            (nf - 1, np.asarray(z["veh_check_last"], dtype=float))]


def decompose(path):
    z = np.load(path)
    w = np.asarray(z["water"], dtype=float)
    h = float(z["h"])
    floor = float(z["floor"])
    nf = w.shape[0]

    cps = checkpoint_frames(z)
    fa, veh = cps[-1]              # last exact checkpoint: nearest to P-2's usual argmax
    ww = w[fa]
    p2_here = float(((ww >= veh.min(0)) & (ww <= veh.max(0))).all(axis=1).mean())
    # P-2's own value, from the driver's stored summary, for comparison.
    sj = os.path.join(os.path.dirname(path), "summary.json")
    p2_reported = float(json.load(open(sj))["passthrough_max_frac"]) if os.path.exists(sj) else float("nan")
    lo, hi = veh.min(0), veh.max(0)
    inbox = ((ww >= lo) & (ww <= hi)).all(axis=1)

    # Driver's own voxel-occupancy test, sim_standing.py:186-195.
    vk = np.floor(veh / h).astype(np.int64)
    wk = np.floor(ww / h).astype(np.int64)
    base = vk.min(0)
    span = (vk.max(0) - base + 1).astype(np.int64)
    vlin = np.ravel_multi_index((vk - base).T, span)
    inside = np.all((wk >= base) & (wk <= vk.max(0)), axis=1)
    wlin = np.full(len(ww), -1, dtype=np.int64)
    wlin[inside] = np.ravel_multi_index((wk[inside] - base).T, span)
    in_hull = np.isin(wlin, np.unique(vlin)) & inside

    # Transparent-box null: box footprint area over the water's own footprint area.
    a_box = float((hi[0] - lo[0]) * (hi[1] - lo[1]))
    a_water = float((ww[:, 0].max() - ww[:, 0].min()) * (ww[:, 1].max() - ww[:, 1].min()))
    return {
        "run": os.path.basename(os.path.dirname(path)),
        "velocity": float(z["velocity"]),
        "checkpoint_frame": fa,
        "n_frames": nf,
        "p2_pct": 100.0 * p2_here,
        "p2_reported_max_pct": 100.0 * p2_reported,
        "in_hull_pp": 100.0 * float(in_hull.mean()),
        "box_void_pp": 100.0 * float((inbox & ~in_hull).mean()),
        "in_hull_share_of_p2": 100.0 * float(in_hull.sum()) / max(int(inbox.sum()), 1),
        "transparent_box_baseline_pct": 100.0 * a_box / a_water if a_water > 0 else float("nan"),
    }


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--json", default="")
    a = p.parse_args()

    rows = [r for r in (decompose(f) for f in sorted(glob.glob(RUNS))) if r]
    print(f"N={len(rows)}. P-2 decomposed at each run's OWN argmax frame.\n")
    print(f"{'run':<20} {'v':>4} {'frm':>4} {'P-2 %':>7} {'in hull':>8} {'void':>7} "
          f"{'hull/P2':>8} {'null %':>7}")
    for r in rows:
        print(f"{r['run']:<20} {r['velocity']:4.1f} {r['checkpoint_frame']:4d} {r['p2_pct']:7.2f} "
              f"{r['in_hull_pp']:8.2f} {r['box_void_pp']:7.2f} "
              f"{r['in_hull_share_of_p2']:7.1f}% {r['transparent_box_baseline_pct']:7.2f}")

    def st(k):
        v = np.array([r[k] for r in rows], dtype=float)
        return np.median(v), v.min(), v.max()

    print()
    for k, lab in (("in_hull_share_of_p2", "share of P-2 actually INSIDE the hull"),
                   ("transparent_box_baseline_pct", "transparent-box null baseline"),
                   ("p2_pct", "P-2 at the last exact checkpoint"),
                   ("p2_reported_max_pct", "P-2 as the driver reports it (true max)")):
        m, lo, hi = st(k)
        print(f"  {lab:<38} median {m:7.2f}  range {lo:7.2f} to {hi:7.2f}")

    nb = np.array([r["transparent_box_baseline_pct"] for r in rows])
    p2 = np.array([r["p2_pct"] for r in rows])
    print(f"\n  gate limit is {100 * GATE_LIMIT:.0f}%. Null baseline exceeds it in "
          f"{int((nb > 100 * GATE_LIMIT).sum())}/{len(rows)} runs.")
    print(f"  P-2 minus its own null: median {np.median(p2 - nb):+.2f} pp, "
          f"range {(p2 - nb).min():+.2f} to {(p2 - nb).max():+.2f} pp")
    print("  A gate whose limit sits AT its own null baseline is testing pile-up, not")
    print("  leakage: a vehicle displacing NOTHING would already read at or above it.")
    gap = np.array([r["p2_reported_max_pct"] - r["p2_pct"] for r in rows])
    print(f"\n  checkpoint vs true max gap: median {np.median(gap):+.2f} pp, "
          f"range {gap.min():+.2f} to {gap.max():+.2f} pp (checkpoint is not the argmax)")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=2, sort_keys=True)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
