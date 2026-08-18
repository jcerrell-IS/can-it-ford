#!/usr/bin/env python3
"""Grade one rung of the refinement ladder: verdict, joint frames, margin, and the
domain geometry that rung actually ran in.

WHY THIS EXISTS SEPARATELY FROM r6_repeat_stats.py
r6_repeat_stats.py hardcodes CONFIGS (rep_g96m2337, rep_v0p5) and N_REP = 10, because
it regenerates one specific document. The ladder rungs are a different shape: N=5, one
mass, and a new rung arrives each time a job lands. This takes a directory and grades
whatever is in it, so g192 and the pinned-span control use the same code path as g160.

NO TRUNCATION. The 90-frame ladder runs already end at the canonical horizon: metrics.csv
is 92 lines, one header plus 91 data rows at indices 0..90, last t = 3.0 s at 30 fps.
r6_repeat_stats.py needed _truncate only because job 917797's repeats were 250-frame runs
that had to be cut back. Cutting a file that is already the right length would drop a row,
so this asserts the length instead of trimming it, and says so if it differs.

IT ALSO PRINTS THE DOMAIN. span = grid_lim - 8*dx is the confounded quantity: grid_lim is
set from the hull alone and does not depend on n_grid, but wall = 4.0*dx does, so the water
span GROWS under refinement. Printing it beside the verdict keeps the confound attached to
the result instead of living only in prose.

Needs numpy. No system python on the Mac has it:
    /opt/homebrew/bin/uv run --with numpy python3 analysis/r7_ladder_grade.py \
        --reps <dir> --mass 2337
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SSF_DEFAULT = 1.42  # vehicle_params compact_sedan, the value the published runs used
CANONICAL_LINES = 92  # header + 91 data rows, indices 0..90, last t = 3.0 s


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover(base: Path) -> list[Path]:
    """Any immediate subdirectory holding a metrics.csv, sorted by trailing integer
    when there is one so rep_10 does not sort before rep_2."""
    dirs = [d for d in base.iterdir() if d.is_dir() and (d / "metrics.csv").is_file()]

    def key(d: Path):
        tail = d.name.rsplit("_", 1)[-1]
        return (0, int(tail)) if tail.isdigit() else (1, d.name)

    return sorted(dirs, key=key)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", required=True, help="directory containing rep_*/metrics.csv")
    ap.add_argument("--mass", type=float, required=True)
    ap.add_argument("--ssf", type=float, default=SSF_DEFAULT)
    ap.add_argument("--sustain", type=int, nargs="+", default=[3, 4, 5],
                    help="sustain_frames values to sweep; the published value is 3")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "simulation"))
    import numpy as np
    import failure_modes as FM

    base = Path(args.reps)
    reps = discover(base)
    if not reps:
        raise SystemExit(f"no rep_*/metrics.csv under {base}")
    label = args.label or base.name

    print("=" * 74)
    print(f"LADDER RUNG  {label}   mass {args.mass} kg   ssf {args.ssf}   G {FM.G}")
    print(f"classifier {REPO / 'simulation' / 'failure_modes.py'}")
    print("=" * 74)

    # ---- 1. bit identity, enumerated -------------------------------------------------
    print("\n1. BIT IDENTITY")
    digests = {}
    for d in reps:
        p = d / "metrics.csv"
        digests[d.name] = sha256(p)
        n = len(p.read_text().splitlines())
        note = "" if n == CANONICAL_LINES else f"   <- {n} lines, NOT the canonical {CANONICAL_LINES}"
        print(f"   {d.name:24s} {digests[d.name][:16]}  {n} lines{note}")
    uniq = set(digests.values())
    verdict = ("ALL IDENTICAL" if len(uniq) == 1
               else "ALL DISTINCT" if len(uniq) == len(digests) else "MIXED")
    print(f"   {len(digests)} files, {len(uniq)} distinct digests -> {verdict}")

    # ---- 2. the domain this rung actually ran in -------------------------------------
    print("\n2. DOMAIN GEOMETRY  (span = grid_lim - 8*dx; grid_lim does not depend on n_grid)")
    for d in reps:
        sp = d / "summary.json"
        if not sp.is_file():
            print(f"   {d.name:24s} no summary.json")
            continue
        s = json.loads(sp.read_text())
        lim, dx, n = s["grid_lim"], s["dx"], s["n_grid"]
        span = lim - 8.0 * dx
        print(f"   {d.name:24s} n_grid {n:4d}  dx {dx:.7f}  lim {lim:.9f}  "
              f"span {span:.6f} m  area {span * span:.4f} m2  layers {s['water_layers']:3d}  "
              f"n_water {s['n_water']}")

    # ---- 3. verdict, joint frames, margin --------------------------------------------
    print(f"\n3. VERDICT AND MARGIN, swept over sustain_frames {args.sustain}")
    print("   margin = longest run of consecutive JOINT-SLIDE frames  minus  sustain_frames")
    joint_len: dict[str, int] = {}
    for d in reps:
        p = d / "metrics.csv"
        cols = FM.load_timeseries(str(p))
        kin = FM.kinematics_from_columns(cols, args.mass)
        th0 = FM.FailureThresholds()
        drift = np.abs(kin.disp[:, FM.SURGE_AXIS])
        spd = np.abs(kin.vel[:, FM.SURGE_AXIS])
        joint = (drift >= th0.slide_m) & (spd >= th0.slide_speed_ms)
        best = run = 0
        for v in joint:
            run = run + 1 if v else 0
            best = max(best, run)
        joint_len[d.name] = int(best)

    for sf in args.sustain:
        th = FM.FailureThresholds(sustain_frames=sf)
        verdicts, margins = [], []
        for d in reps:
            res = FM.classify_timeseries(str(d / "metrics.csv"), args.mass, args.ssf, th)
            verdicts.append(res.mode.value)
            margins.append(joint_len[d.name] - sf)
        tag = "  <- published value" if sf == 3 else ""
        print(f"\n   sustain_frames = {sf}{tag}")
        print(f"     verdicts     {dict(Counter(verdicts))}")
        print(f"     joint frames {[joint_len[d.name] for d in reps]}")
        print(f"     margin       {margins}   min={min(margins)} max={max(margins)}")


if __name__ == "__main__":
    main()
