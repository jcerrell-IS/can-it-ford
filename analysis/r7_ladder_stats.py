#!/usr/bin/env python3
"""Regenerate every number in the refinement-ladder margin table, g48 through g192.

Built on the pattern of analysis/r6_repeat_stats.py, which did the same job for the
job-917797 A2 repeats. Two differences that matter:

  1. r6_repeat_stats.py has NO `GRIDS` dict. A round-7 task description said its
     GRIDS dict "needs 192 adding"; that is a conflation with
     analysis/r6_hull_clearance.py:61, whose GRIDS dict is a dx lookup for the
     clearance rule and ALREADY carries 192. Neither script computed the ladder
     margin table, so this script exists. Verified live 2026-08-18 by
     `/usr/bin/grep -n GRIDS analysis/*.py`.

  2. The ladder runs are 5 repeats named rep_1..rep_5 under one directory per grid,
     not 10 repeats named <cfg>_1..<cfg>_10, so the directory walk differs.

WHAT THIS PRINTS, per grid, and why each one is here:

  bit identity      sha256 of every metrics.csv. `determinism_identical` in
                    summary.json is TRUE on these runs and is NOT a claim that the
                    repeats agree; it is a within-run flag. The digests are the
                    actual test of repeat-to-repeat identity.
  verdict           simulation/failure_modes.py classify_timeseries, the published
                    classifier, at ssf 1.42 (vehicle_params compact_sedan).
  joint frames      longest run of consecutive frames holding the JOINT slide
                    condition (drift >= slide_m AND speed >= slide_speed_ms), the
                    definition a6a707c fixed.
  margin            joint frames minus th.sustain_frames. sustain_frames = 3 is
                    UNSOURCED (failure_modes.py:52); the margin is reported so a
                    reader can see how close each grid sits to that arbitrary line.
  water_layers      from summary.json. The only depth-based resolution convention
                    in the literature asks for ~10 particle layers across the flow
                    depth (Reis et al. 2021, 10.1016/j.engstruct.2021.113280).
  span              lim * (1 - 8/n). THE CONFOUND. wall = 4*dx on each side and dx
                    shrinks with n, so grid_lim being identical across the ladder
                    does NOT mean the tank is identical. It is not. Printed beside
                    every row so no reader can take the ladder for a pure
                    resolution sweep.

THE HORIZON IS ROW INDEX 90, NOT 91. Each metrics.csv here holds 92 lines: one
header plus 91 data rows at indices 0..90. summary.json carries "frames": 90.
A window of 91 runs one row past the canonical horizon.

Needs numpy. No system python on this Mac has it:
    /opt/homebrew/bin/uv run --with numpy python3 analysis/r7_ladder_stats.py --base <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# grid -> (directory name under --base, slurm job id). Every one of these is a
# 5-repeat run of m2337 at depth 0.30 m and velocity 1.5 m/s with the canonical
# driver, so grid is the ONLY intended difference. See the span column for the
# unintended one.
GRIDS = {
    48: ("r6_rep_g48_918250", 918250),
    64: ("r6_rep_g64_918249", 918249),
    96: ("r6_rep_g96_918248", 918248),
    128: ("r6_rep_g128_918247", 918247),
    160: ("r6_rep_g160_918350", 918350),
    192: ("r6_rep_g192_918351", 918351),
}
N_REP = 5
SSF = 1.42          # vehicle_params compact_sedan, the value the published runs used
MASS = 2337.0       # the heaviest vehicle, J15's most fragile case
HORIZON = 90        # canonical row index, see docstring
WALL_CELLS = 8      # 4*dx each side, so span = lim*(1 - 8/n)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summary_of(d: Path) -> dict:
    return json.loads((d / "summary.json").read_text())


def bit_identity(base: Path) -> dict[int, bool]:
    print("=" * 78)
    print("1. BIT IDENTITY. Are the five repeats distinct files?")
    print("=" * 78)
    out = {}
    for g, (dirname, job) in GRIDS.items():
        digests = {}
        for i in range(1, N_REP + 1):
            p = base / dirname / f"rep_{i}" / "metrics.csv"
            if not p.is_file():
                print(f"\n  g{g}: MISSING {p}")
                break
            digests[i] = sha256(p)
        else:
            uniq = set(digests.values())
            all_distinct = len(uniq) == len(digests)
            out[g] = all_distinct
            print(f"\n  g{g:<4d} job {job}")
            for i, d in digests.items():
                print(f"    rep {i}  {d[:24]}")
            print(f"    {len(digests)} files, {len(uniq)} distinct digests -> "
                  f"{'ALL DISTINCT' if all_distinct else 'NOT all distinct'}")
    return out


def geometry(base: Path) -> dict[int, dict]:
    print()
    print("=" * 78)
    print("2. GEOMETRY AND THE CONFOUND. grid_lim is constant; the TANK IS NOT.")
    print("=" * 78)
    print(f"\n  {'grid':>5} {'dx (m)':>10} {'layers':>7} {'n_water':>10} "
          f"{'grid_lim':>10} {'span (m)':>10} {'span vs g48':>12}")
    rows = {}
    base_span = None
    for g, (dirname, _job) in GRIDS.items():
        d = base / dirname / "rep_1"
        if not (d / "summary.json").is_file():
            continue
        s = summary_of(d)
        span = s["grid_lim"] * (1.0 - WALL_CELLS / s["n_grid"])
        if base_span is None:
            base_span = span
        rows[g] = dict(dx=s["dx"], layers=s["water_layers"], n_water=s["n_water"],
                       lim=s["grid_lim"], span=span)
        print(f"  {g:5d} {s['dx']:10.6f} {s['water_layers']:7d} {s['n_water']:10d} "
              f"{s['grid_lim']:10.5f} {span:10.5f} {span / base_span:11.4f}x")
    print("\n  span = grid_lim * (1 - 8/n_grid), because the driver sets wall = 4*dx")
    print("  on each side. Refining the grid ENLARGES the water tank. Resolution and")
    print("  tank size are co-directional across this whole ladder and this set of")
    print("  runs cannot separate them.")
    return rows


def classify(base: Path, window: int) -> dict[int, dict]:
    sys.path.insert(0, str(REPO / "simulation"))
    import numpy as np
    import failure_modes as FM

    print()
    print("=" * 78)
    print(f"3. VERDICT AND margin. classifier ssf={SSF}, G={FM.G}, mass={MASS} kg, "
          f"window=0..{window}")
    print("=" * 78)
    th = FM.FailureThresholds()
    print(f"  thresholds: slide_m={th.slide_m} slide_speed_ms={th.slide_speed_ms} "
          f"sustain_frames={th.sustain_frames}  (sustain_frames is UNSOURCED)")
    out = {}
    for g, (dirname, job) in GRIDS.items():
        verdicts, joints, margins = [], [], []
        for i in range(1, N_REP + 1):
            p = base / dirname / f"rep_{i}" / "metrics.csv"
            if not p.is_file():
                break
            res = FM.classify_timeseries(str(p), MASS, SSF)
            verdicts.append(res.mode.value)

            cols = FM.load_timeseries(str(p))
            kin = FM.kinematics_from_columns(cols, MASS)
            drift = np.abs(kin.disp[:window + 1, FM.SURGE_AXIS])
            spd = np.abs(kin.vel[:window + 1, FM.SURGE_AXIS])
            joint = (drift >= th.slide_m) & (spd >= th.slide_speed_ms)
            best = run = 0
            for v in joint:
                run = run + 1 if v else 0
                best = max(best, run)
            joints.append(best)
            margins.append(best - th.sustain_frames)
        else:
            tally = dict(Counter(verdicts))
            out[g] = dict(verdicts=tally, joints=joints, margins=margins)
            print(f"\n  g{g:<4d} job {job}")
            print(f"    verdicts     {tally}")
            print(f"    joint frames {joints}   min={min(joints)} max={max(joints)}")
            print(f"    margin       {margins}   min={min(margins)} max={max(margins)}")
    return out


def ladder_table(geo: dict, cls: dict, distinct: dict) -> None:
    print()
    print("=" * 78)
    print("4. THE LADDER TABLE")
    print("=" * 78)
    print(f"\n  {'grid':>5} {'dx (m)':>9} {'layers':>7} {'verdict':>12} {'margin':>10} "
          f"{'span (m)':>9} {'5 distinct':>11}")
    for g in sorted(set(geo) & set(cls)):
        v = cls[g]["verdicts"]
        vs = " ".join(f"{k} {n}/{N_REP}" for k, n in v.items())
        m = cls[g]["margins"]
        ms = str(m[0]) if len(set(m)) == 1 else f"{min(m)} to {max(m)}"
        print(f"  {g:5d} {geo[g]['dx']:9.5f} {geo[g]['layers']:7d} {vs:>12} {ms:>10} "
              f"{geo[g]['span']:9.4f} {str(distinct.get(g)):>11}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True,
                    help="directory holding the r6_rep_g*_<job>/ trees")
    ap.add_argument("--window", type=int, default=HORIZON,
                    help=f"last row index inclusive (default {HORIZON}, the canonical horizon)")
    a = ap.parse_args()
    distinct = bit_identity(a.base)
    geo = geometry(a.base)
    cls = classify(a.base, a.window)
    ladder_table(geo, cls, distinct)


if __name__ == "__main__":
    main()
