#!/usr/bin/env python3
"""Audit every local run's time series against a data-driven settling criterion.

Answers one question per run: how many leading frames does the record itself say
must be discarded, against the 8 frames `sim_standing.py:154` actually used?

This needs no GPU. The 15-column FloodHistory `metrics.csv` for the local runs is
already on disk, so the whole audit is a laptop job.

Method and citations live in analysis/stationarity.py. Pure standard library.

Usage
    python3 analysis/settle_audit.py                 # all runs under renders/
    python3 analysis/settle_audit.py --glob 'g64*'   # subset
    python3 analysis/settle_audit.py --csv out.csv   # machine-readable
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stationarity import analyze  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERS = os.path.join(REPO, "renders")

# The settle length baked into the driver, for comparison.
DRIVER_SETTLE_FRAMES = 8
DRIVER_REF = "renders/yaris_render_s1/sim_standing.py:154"

# Observables worth testing. dmag and vmag are what the verdicts read.
OBSERVABLES = ["dmag", "vmag", "vx"]


def load_series(path: str) -> dict[str, list[float]]:
    cols: dict[str, list[float]] = {}
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rdr = csv.DictReader(fh)
        if not rdr.fieldnames:
            return cols
        for name in rdr.fieldnames:
            cols[name.strip()] = []
        for row in rdr:
            for name in rdr.fieldnames:
                v = row.get(name, "")
                try:
                    cols[name.strip()].append(float(v))
                except (TypeError, ValueError):
                    pass
    return cols


def find_runs(pattern: str | None) -> list[tuple[str, str]]:
    out = []
    for root, _dirs, files in os.walk(RENDERS):
        if "metrics.csv" not in files:
            continue
        name = os.path.relpath(root, RENDERS)
        if pattern:
            import fnmatch
            if not fnmatch.fnmatch(os.path.basename(root), pattern):
                continue
        out.append((name, os.path.join(root, "metrics.csv")))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default=None, help="run-directory glob")
    ap.add_argument("--csv", default=None, help="write machine-readable output")
    ap.add_argument("--observable", default="dmag",
                    help="observable for the headline table")
    args = ap.parse_args()

    runs = find_runs(args.glob)
    if not runs:
        print("no runs with metrics.csv found under", RENDERS)
        return 1

    print(f"Settle audit against the driver's fixed "
          f"settle_frames={DRIVER_SETTLE_FRAMES} ({DRIVER_REF})")
    print(f"runs found: {len(runs)}   headline observable: {args.observable}")
    print()
    hdr = (f"{'run':38} {'n':>4} {'need':>5} {'used':>5} {'tau':>6} "
           f"{'N_eff':>7} {'stat?':>6} {'RUM95':>11}")
    print(hdr)
    print("-" * len(hdr))

    rows, worse, nonstat = [], 0, 0
    for name, path in runs:
        cols = load_series(path)
        for obs in OBSERVABLES:
            if obs not in cols or len(cols[obs]) < 20:
                continue
            rep = analyze(cols[obs], f"{name}:{obs}")
            rows.append({
                "run": name, "observable": obs,
                "n_frames": rep["n_total"],
                "recommended_discard": rep["recommended_discard"],
                "driver_settle_frames": DRIVER_SETTLE_FRAMES,
                "exceeds_driver": rep["recommended_discard"]
                > DRIVER_SETTLE_FRAMES,
                "tau_int": round(rep["tau_int"], 4),
                "n_eff": round(rep["n_eff"], 2),
                "window_len": rep["window_len"],
                "stationary_at_5pct": rep["stationary_at_5pct"],
                "reverse_arrangement_z": round(
                    rep["reverse_arrangement_z"], 3),
                "mean": rep["mean"],
                "rum_95_halfwidth": rep["rum_95"],
                "std_err_correlated": rep["std_err_correlated"],
            })
            if obs != args.observable:
                continue
            if rep["recommended_discard"] > DRIVER_SETTLE_FRAMES:
                worse += 1
            if not rep["stationary_at_5pct"]:
                nonstat += 1
            print(f"{name[:38]:38} {rep['n_total']:4d} "
                  f"{rep['recommended_discard']:5d} "
                  f"{DRIVER_SETTLE_FRAMES:5d} {rep['tau_int']:6.2f} "
                  f"{rep['n_eff']:7.1f} "
                  f"{'yes' if rep['stationary_at_5pct'] else 'NO':>6} "
                  f"{rep['rum_95']:11.4g}")

    head = [r for r in rows if r["observable"] == args.observable]
    print()
    print(f"On {args.observable}, across {len(head)} runs:")
    print(f"  runs needing MORE than {DRIVER_SETTLE_FRAMES} discarded frames: "
          f"{worse} of {len(head)}")
    print(f"  runs whose retained window is still NOT stationary at 5%: "
          f"{nonstat} of {len(head)}")
    if head:
        needs = sorted(r["recommended_discard"] for r in head)
        print(f"  recommended discard: min {needs[0]}, "
              f"median {needs[len(needs) // 2]}, max {needs[-1]}")
    print()
    print("Reading: 'need' is max(MSER, Chodera t0, transient-scan start) for "
          "that run's own record.\n'stat?' NO means a residual trend survives "
          "even after trimming, so a mean over\nthat window is not a settled "
          "value regardless of how many frames were dropped.")
    print()
    print("CAVEAT, do not over-read a large 'need'. MSER is bounded below by "
          "min_keep=10, so a\nrun reporting need = n_frames - 11 has hit that "
          "bound: variance was still falling at\nthe end of the record. That "
          "does not mean 'discard exactly that many'. It means the\nRUN IS TOO "
          "SHORT to establish a settled value at all, which is the same "
          "conclusion\nD9 reached by direct comparison when 60 frames proved "
          "inadequate and 250 were needed.\nTwo independent methods, so treat "
          "the agreement as corroboration only because the\norigins differ: "
          "this is a stationarity statistic on one record, D9 was a "
          "settle-length\nsweep across arms.")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            if rows:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        print(f"\nwrote {len(rows)} rows to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
