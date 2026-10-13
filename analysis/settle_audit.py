#!/usr/bin/env python3
"""Audit each run's per-frame record for how much of it is start-up transient.

The driver the 17 gated runs used (`analysis/render_v1/as_ran_local_copies/sim_standing.py`, line 76,
`settle_frames=8`) lets still water settle for 8 frames, then sets all the water moving in one step
and starts recording. So the record begins at that step, and the leading frames this audit flags are
mostly the start-up surge. In the three 48-cell runs the hull is also still settling 0.04 to 0.05 m
onto the floor during the record, so the frames flagged there may also include that settling. The question per run is: how many leading frames does
the record itself say are transient, and is what remains stationary?

No GPU is needed. By default it reads the 17 per-frame records copied into `tests/data/runs/`; point
`--runs-dir` at a folder of full run outputs to audit those instead.

Method and citations are in `analysis/stationarity.py`. Standard library only.

Usage
    python3 analysis/settle_audit.py                   # the 17 gated runs (test fixtures)
    python3 analysis/settle_audit.py --glob 'g64*'     # subset
    python3 analysis/settle_audit.py --csv out.csv     # machine-readable
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stationarity import analyze  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RUNS = os.path.join(REPO, "tests", "data", "runs")

# The still-water settle the driver ran before the one-step start, for context only. These frames
# are not part of the record, so they are not a discard of it.
DRIVER_SETTLE_FRAMES = 8
DRIVER_REF = "analysis/render_v1/as_ran_local_copies/sim_standing.py:76"

# dmag (displacement magnitude) and vmag (speed) are what the move-or-stay labels read.
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


def find_runs(runs_dir: str, pattern: str | None) -> list[tuple[str, str]]:
    out = []
    for root, _dirs, files in os.walk(runs_dir):
        if "metrics.csv" not in files:
            continue
        if pattern and not fnmatch.fnmatch(os.path.basename(root), pattern):
            continue
        out.append((os.path.relpath(root, runs_dir), os.path.join(root, "metrics.csv")))
    return sorted(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Start-up transient and stationarity audit of run records.")
    ap.add_argument("--runs-dir", default=DEFAULT_RUNS,
                    help="folder searched for <run>/metrics.csv (default: tests/data/runs)")
    ap.add_argument("--glob", default=None, help="run-directory glob")
    ap.add_argument("--csv", default=None, help="write machine-readable output")
    ap.add_argument("--observable", default="dmag",
                    help="observable for the headline table")
    args = ap.parse_args(argv)

    runs = find_runs(args.runs_dir, args.glob)
    if not runs:
        print("no runs with metrics.csv found under", args.runs_dir)
        return 1

    print(f"Start-up transient audit. The driver settled still water for {DRIVER_SETTLE_FRAMES} frames "
          f"({DRIVER_REF})\nbefore the one-step start; the record begins at the start.")
    print(f"runs found: {len(runs)}   headline observable: {args.observable}")
    print()
    hdr = (f"{'run':38} {'n':>4} {'trans':>6} {'tau':>6} "
           f"{'N_eff':>7} {'stat?':>6} {'RUM95':>11}")
    print(hdr)
    print("-" * len(hdr))

    rows, nonstat, at_bound = [], 0, 0
    for name, path in runs:
        cols = load_series(path)
        for obs in OBSERVABLES:
            if obs not in cols or len(cols[obs]) < 20:
                continue
            rep = analyze(cols[obs], f"{name}:{obs}")
            rows.append({
                "run": name, "observable": obs,
                "n_frames": rep["n_total"],
                "transient_frames": rep["recommended_discard"],
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
            if not rep["stationary_at_5pct"]:
                nonstat += 1
            if rep["recommended_discard"] >= rep["n_total"] - 11:
                at_bound += 1
            print(f"{name[:38]:38} {rep['n_total']:4d} "
                  f"{rep['recommended_discard']:6d} "
                  f"{rep['tau_int']:6.2f} "
                  f"{rep['n_eff']:7.1f} "
                  f"{'yes' if rep['stationary_at_5pct'] else 'NO':>6} "
                  f"{rep['rum_95']:11.4g}")

    head = [r for r in rows if r["observable"] == args.observable]
    print()
    print(f"On {args.observable}, across {len(head)} runs:")
    if head:
        needs = sorted(r["transient_frames"] for r in head)
        print(f"  leading frames flagged as transient: min {needs[0]}, "
              f"median {needs[len(needs) // 2]}, max {needs[-1]} (of {head[0]['n_frames']})")
    print(f"  runs where the transient reaches the MSER bound (record too short to settle): "
          f"{at_bound} of {len(head)}")
    print(f"  runs whose remaining window is still NOT stationary at 5%: "
          f"{nonstat} of {len(head)}")
    print()
    print("Reading: 'trans' is max(MSER, Chodera t0, transient-scan start) for that run's own record.\n"
          "'stat?' NO means a trend survives after trimming, so a mean over that window is not a\n"
          "settled value however many frames were dropped. MSER keeps at least 10 frames, so a run\n"
          "reporting trans = n - 11 has hit that bound: variance was still falling at the end of the\n"
          "record, which means the run is too short to establish a settled value at all.")

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
