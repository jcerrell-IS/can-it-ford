#!/usr/bin/env python3
"""Probabilistic SLIDE verdicts with detection uncertainty.

WHY THIS EXISTS
---------------
The published verdicts are deterministic: SLIDE when drift exceeds `slide_m` AND
speed exceeds `slide_speed_ms` for 3 consecutive frames. Register J15 records that
`g96_m2337` satisfies that condition for exactly 4 frames against the 3 required,
a ONE-FRAME margin, 0.033 s at 30 fps, and that the margin closes with
refinement (11 -> 10 -> 4 across g48/g64/g96). A binary label carries none of
that.

The Undermind report `Settling_and_Force_Reporting_in_Free_Surface_Flow.md`
concluded, from the incipient-motion literature, that:

    "Incipient motion is probabilistic and record-length dependent; define a
     movement probability or activity rate with detection uncertainty, not a
     single critical stress."

That is not a stylistic preference. Dancey et al 2002 introduced exactly this
criterion for sediment threshold-of-motion, specifying the threshold by a fixed
value of a PROBABILITY rather than a critical stress, precisely because movement
in turbulent flow is statistical and depends on the observation time scale.

WHAT THIS COMPUTES
------------------
p_move          fraction of frames in the stationary window satisfying the joint
                drift-and-speed condition
wilson_ci       confidence interval on p_move using EFFECTIVE sample size, not
                frame count, so serial correlation cannot inflate confidence
activity_rate   qualifying episodes per second, the record-length-independent
                companion to p_move
margin_frames   longest consecutive run satisfying the condition, minus the 3
                required (the existing assumption-free metric, retained)
robustness      the verdict recomputed across a sweep of probability thresholds,
                so "is this verdict close to flipping" is answerable

SOURCES
-------
Dancey, Diplas, Papanicolaou, Bala 2002, "Probability of Individual Grain
    Movement and Threshold Condition", Journal of Hydraulic Engineering. The
    probability-as-threshold criterion.
Wilson 1927 score interval, used because the normal approximation is unreliable
    at p near 0 or 1, which is exactly where these verdicts sit.
Brouwer et al 2019, doi:10.1016/J.OCEANENG.2019.04.068, and Grossfield et al
    2018, doi:10.33011/livecoms.1.1.5067, for correlated-sample uncertainty.
Bocanegra, Valles-Moran, Frances 2019, doi:10.1111/jfr3.12551, which reviews
    vehicle stability models and finds published thresholds "vary over a
    relatively wide range" with several models not fitting measured data well.
    That spread is the external reason a single deterministic threshold
    overstates precision.

Pure standard library. Thresholds default to the values the classifier uses.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stationarity import analyze, effective_sample_size  # noqa: E402

# Values as declared in simulation/failure_modes.py. NOTE the unit trap recorded
# in CLAUDE.md item 13: slide_m is METRES and slide_speed_ms is METRES PER
# SECOND, and they happen to share the numeral 0.05. Never deduplicate these by
# value; only by name and unit.
SLIDE_M = 0.05           # metres
SLIDE_SPEED_MS = 0.05    # metres per second
FRAMES_REQUIRED = 3      # consecutive frames for the deterministic rule
FPS = 30.0


def wilson_ci(k: float, n: float, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion, robust near p = 0 and p = 1.

    `n` should be the EFFECTIVE sample size. Passing the raw frame count is the
    mistake this function exists to avoid.
    """
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def episodes(mask: list[bool]) -> list[int]:
    """Lengths of consecutive True runs."""
    out, run = [], 0
    for m in mask:
        if m:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def assess(dmag: list[float], vmag: list[float], fps: float = FPS,
           slide_m: float = SLIDE_M, slide_speed: float = SLIDE_SPEED_MS,
           use_stationary_window: bool = False) -> dict:
    """Probabilistic assessment of one run's SLIDE condition.

    `use_stationary_window` DEFAULTS TO FALSE, and that default is a correction
    to an earlier version of this file. The reasoning matters enough to record.

    Removing the startup transient is the right move for a steady observable
    such as a mean resistance force. It is the WRONG move for an incipient-motion
    verdict, because incipient motion is an EVENT, not a steady state. The same
    Undermind report that supplies the stationarity protocol says so directly:
    slamming, water entry and impact loading "generally have no steady force:
    report peak distributions, impulses, envelopes or cycle/event statistics
    with repeat-run uncertainty, rather than a steady mean."

    Measured consequence on the 24 local runs, which is why this is not
    hypothetical. On the full record 21 of 24 read SLIDE, reproducing the
    canonical pattern including the register J15 one-frame margin for
    `g96_m2337`. With the transient removed, only 5 of 24 still satisfy the
    condition, because the vehicle's motion happens during the surge and the
    speed channel falls below `slide_speed` afterwards.

    So: pass use_stationary_window=True only as a ROBUSTNESS DIAGNOSTIC, asking
    "does the condition persist beyond startup?". That is a real and interesting
    question, and its answer is mostly no. It is not the verdict, and reporting
    it as the verdict would silently contradict the published 16 SLIDE / 1 STUCK
    on a category error.
    """
    n = min(len(dmag), len(vmag))
    dmag, vmag = dmag[:n], vmag[:n]
    if n < 12:
        raise ValueError("record too short to assess")

    start = 0
    if use_stationary_window:
        # Trim on the drift channel, the quantity the verdict reads.
        rep = analyze(dmag, "dmag")
        start = min(rep["recommended_discard"], n - 12)
    d_w, v_w = dmag[start:], vmag[start:]

    mask = [(d > slide_m and v > slide_speed) for d, v in zip(d_w, v_w)]
    k = sum(mask)
    nw = len(mask)
    eps = episodes(mask)
    longest = max(eps) if eps else 0

    # Effective sample size from the drift channel governs how much independent
    # evidence the window actually contains.
    neff = effective_sample_size(d_w) if nw > 1 else 1.0
    neff = max(1.0, min(neff, float(nw)))
    k_eff = (k / nw) * neff if nw else 0.0
    p = k / nw if nw else 0.0
    lo, hi = wilson_ci(k_eff, neff)

    duration_s = nw / fps
    qualifying = [e for e in eps if e >= FRAMES_REQUIRED]

    return {
        "n_frames_total": n,
        "window_start": start,
        "n_frames_window": nw,
        "window_duration_s": duration_s,
        "p_move": p,
        "p_move_ci_lo": lo,
        "p_move_ci_hi": hi,
        "n_eff": neff,
        "frames_satisfying": k,
        "episodes": len(eps),
        "qualifying_episodes": len(qualifying),
        "activity_rate_per_s": (len(qualifying) / duration_s
                                if duration_s > 0 else 0.0),
        "longest_run_frames": longest,
        "margin_frames": longest - FRAMES_REQUIRED,
        "deterministic_verdict": ("SLIDE" if longest >= FRAMES_REQUIRED
                                 else "STUCK"),
    }


def robustness(res: dict, thresholds=(0.01, 0.05, 0.10, 0.25, 0.50)) -> dict:
    """Verdict as a function of the probability threshold chosen.

    A verdict that flips inside this sweep is a verdict whose label is a choice,
    not a measurement. Reporting the sweep makes that visible instead of hiding
    it behind a single cut.
    """
    return {f"p>={t:g}": ("SLIDE" if res["p_move"] >= t else "STUCK")
            for t in thresholds}


def load_metrics(path: str) -> dict[str, list[float]]:
    cols: dict[str, list[float]] = {}
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rdr = csv.DictReader(fh)
        if not rdr.fieldnames:
            return cols
        for nm in rdr.fieldnames:
            cols[nm.strip()] = []
        for row in rdr:
            for nm in rdr.fieldnames:
                try:
                    cols[nm.strip()].append(float(row[nm]))
                except (TypeError, ValueError, KeyError):
                    pass
    return cols


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders"))
    ap.add_argument("--csv", default=None)
    ap.add_argument("--stationary-window", action="store_true",
                    help="DIAGNOSTIC: re-assess after removing the startup transient")
    args = ap.parse_args()

    runs = []
    for root, _d, files in os.walk(args.renders):
        if "metrics.csv" in files:
            runs.append((os.path.relpath(root, args.renders),
                         os.path.join(root, "metrics.csv")))
    runs.sort()
    if not runs:
        print("no metrics.csv found under", args.renders)
        return 1

    print("Probabilistic SLIDE assessment "
          f"(slide_m={SLIDE_M} m, slide_speed={SLIDE_SPEED_MS} m/s, "
          f"{FRAMES_REQUIRED} frames required)")
    print("p_move CI uses EFFECTIVE sample size, not frame count.")
    print()
    hdr = (f"{'run':36} {'det':>6} {'margin':>7} {'p_move':>7} "
           f"{'95% CI':>15} {'N_eff':>6} {'act/s':>6} {'flips?':>7}")
    print(hdr)
    print("-" * len(hdr))

    rows, flippers = [], 0
    for name, path in runs:
        cols = load_metrics(path)
        if "dmag" not in cols or "vmag" not in cols:
            continue
        try:
            res = assess(cols["dmag"], cols["vmag"],
                         use_stationary_window=args.stationary_window)
        except ValueError:
            continue
        rob = robustness(res)
        verdicts = set(rob.values())
        flips = len(verdicts) > 1
        if flips:
            flippers += 1
        row = {"run": name}
        row.update(res)
        row.update(rob)
        row["verdict_flips_across_thresholds"] = flips
        rows.append(row)
        print(f"{name[:36]:36} {res['deterministic_verdict']:>6} "
              f"{res['margin_frames']:7d} {res['p_move']:7.3f} "
              f"[{res['p_move_ci_lo']:.2f},{res['p_move_ci_hi']:.2f}]".ljust(0)
              + f" {res['n_eff']:6.1f} {res['activity_rate_per_s']:6.2f} "
              f"{'YES' if flips else 'no':>7}")

    print()
    print(f"runs assessed: {len(rows)}")
    print(f"verdicts that flip somewhere in p >= 0.01 .. 0.50: "
          f"{flippers} of {len(rows)}")
    print()
    print("A flipping verdict is not necessarily wrong. It means the label "
          "depends on a\nprobability cut nobody has stated, so the cut has to "
          "be declared in the paper\nalongside the verdict, exactly as Dancey "
          "et al 2002 declare theirs.")

    if args.csv and rows:
        keys = list(rows[0].keys())
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"\nwrote {len(rows)} rows to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
