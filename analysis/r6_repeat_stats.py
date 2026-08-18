#!/usr/bin/env python3
"""Regenerate every number in docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md.

Three independent analyses, each of which prints its own enumeration rather than a
bare total, because on this project every hand-derived figure has been wrong at least
once and every figure recomputed inside a checked script that printed its enumeration
has been right.

  --jobA <dir>   the extracted d4_jobA tree from job 917797. Expects
                 rep_g96m2337_1..10/ and rep_v0p5_1..10/, each with metrics.csv and
                 summary.json. Runs: bit-identity, divergence onset, dmag spread,
                 the published classifier, and margin_frames per a6a707c.
  --jobB <json>  sphere_fixed_g64.json from job 918043 or later. Runs the project's
                 own blocking.stationarity on the nominal and measured ratios.

Needs numpy. No system python on the Mac has it:
    /opt/homebrew/bin/uv run --with numpy python3 analysis/r6_repeat_stats.py ...

WHY THE FRAME WINDOW IS AN ARGUMENT AND NOT A CONSTANT. These repeats are 250-frame
runs against a canonical horizon of ROW INDEX 90. The first wall reflection is predicted
at frame 112.3 and observed at 112, 125 and 126, so any magnitude at or after that is
contaminated. margin_frames is unaffected because the joint SLIDE condition fires early;
dmag is inflated about 2.5x. The spread of one statistic does not transfer to another, so
the window is stated beside every number this prints.

THE CANONICAL HORIZON IS 90, NOT 91. Verified live at
renders/yaris_render_s1/_incoming/g96_m2337/summary.json, which carries "frames": 90, and
whose metrics.csv holds 92 lines, i.e. one header plus 91 data rows at indices 0 to 90,
with last t = 2.999999999999999 s, exactly 3.0 s at 30 fps. A window of "0 to 91
inclusive" therefore runs ONE ROW PAST the canonical horizon. An earlier version of this
script defaulted to 91 and was wrong by that one row.

ROW 0 IS NOT THE INITIAL CONDITION, so do not describe row-0 spread as a difference in
starting conditions. sim_standing.py:235-237 runs `for _ in range(settle_frames):
self._project_water(); s.step(self.dt, self.substeps)` with settle_frames = 8, the
velocity kick is added at :238-240, and only then do :244-246 set time = 0.0 and append
the first history row. With substeps 16 (g96) and 11 (v0p5) that is 128 and 88 solver
substeps BEFORE row 0 is recorded.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The two boundary configurations job 917797 repeated. Repeating comfortable runs
# measures nothing, so only these two were run: g96_m2337 sits at the tightest
# published margin (J15) and v0p5 is the only STUCK among the 17.
CONFIGS = (
    ("rep_g96m2337", 2337.0, "g96 m2337 v1.5, J15's one-frame margin"),
    ("rep_v0p5", 1100.0, "g64 m1100 v0.5, the only STUCK of the 17"),
)
SSF = 1.42  # vehicle_params compact_sedan, the value the published classification used
N_REP = 10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows_of(path: Path) -> list[dict]:
    with path.open() as fh:
        return list(csv.DictReader(fh))


def bit_identity(base: Path) -> None:
    print("=" * 72)
    print("1. BIT IDENTITY. Are the repeats identical to each other?")
    print("=" * 72)
    for cfg, _mass, note in CONFIGS:
        digests = {}
        for i in range(1, N_REP + 1):
            p = base / f"{cfg}_{i}" / "metrics.csv"
            digests[i] = sha256(p)
        uniq = set(digests.values())
        print(f"\n  {cfg}  ({note})")
        for i, d in digests.items():
            print(f"    rep {i:2d}  {d[:16]}")
        print(f"    {len(digests)} files, {len(uniq)} distinct digests -> "
              f"{'ALL IDENTICAL' if len(uniq) == 1 else 'ALL DIFFERENT' if len(uniq) == len(digests) else 'MIXED'}")


def divergence_onset(base: Path) -> None:
    print()
    print("=" * 72)
    print("2. DIVERGENCE ONSET. First frame at which any two repeats disagree.")
    print("=" * 72)
    for cfg, _mass, _note in CONFIGS:
        series = [rows_of(base / f"{cfg}_{i}" / "metrics.csv") for i in range(1, N_REP + 1)]
        n = min(len(s) for s in series)
        cols = list(series[0][0].keys())
        hit = None
        for idx in range(n):
            for col in cols:
                if len({s[idx][col] for s in series}) > 1:
                    hit = (idx, col)
                    break
            if hit:
                break
        if hit:
            idx, col = hit
            t = float(series[0][idx]["t"])
            print(f"\n  {cfg}: frame {idx} (t={t:.4f} s), first column to differ: {col}")
        else:
            print(f"\n  {cfg}: no divergence in {n} frames")


def dmag_spread(base: Path, windows: tuple[int, ...]) -> None:
    import statistics as st

    print()
    print("=" * 72)
    print("3. dmag SPREAD. Name the statistic and the window beside every number.")
    print("=" * 72)
    for cfg, _mass, _note in CONFIGS:
        series = [rows_of(base / f"{cfg}_{i}" / "metrics.csv") for i in range(1, N_REP + 1)]
        print(f"\n  {cfg}")
        for w in windows:
            vals = [float(s[w]["dmag"]) for s in series]
            mean = st.mean(vals)
            rng = max(vals) - min(vals)
            flag = "  <- CONTAMINATED, at or past first wall reflection (112)" if w >= 112 else ""
            print(f"    frame {w:3d}: N={len(vals)} min={min(vals):.6e} max={max(vals):.6e} "
                  f"range={rng:.6e} m")
            print(f"               mean={mean:.6e} sd={st.pstdev(vals):.6e} m  "
                  f"range/mean={rng / mean * 100:.2f} %{flag}")


def _truncate(src: Path, nframes: int, dst: Path) -> Path:
    with src.open() as fh:
        rows = list(csv.reader(fh))
    with dst.open("w", newline="") as fh:
        csv.writer(fh).writerows(rows[: nframes + 1])  # +1 keeps the header
    return dst


def classify_and_margin(base: Path, windows: tuple[int, ...], tmp: Path) -> None:
    """The published verdict, plus margin_frames exactly as a6a707c defines it:
    the longest run of consecutive frames holding the JOINT slide condition, minus
    the 3 the classifier requires. Unlike k_crit it assumes nothing: no scaling, no
    linearity, just a count."""
    sys.path.insert(0, str(REPO / "simulation"))
    import numpy as np
    import failure_modes as FM

    print()
    print("=" * 72)
    print(f"4. VERDICT AND margin_frames. classifier ssf={SSF}, G={FM.G}")
    print("=" * 72)
    tmp.mkdir(parents=True, exist_ok=True)
    th = FM.FailureThresholds()
    for cfg, mass, note in CONFIGS:
        print(f"\n  {cfg}  ({note})   mass {mass} kg")
        for w in windows:
            verdicts, joints, margins = [], [], []
            for i in range(1, N_REP + 1):
                src = base / f"{cfg}_{i}" / "metrics.csv"
                p = _truncate(src, w, tmp / f"{cfg}_{i}_{w}.csv")
                res = FM.classify_timeseries(str(p), mass, SSF)
                verdicts.append(res.mode.value)

                cols = FM.load_timeseries(str(p))
                kin = FM.kinematics_from_columns(cols, mass)
                drift = np.abs(kin.disp[:, FM.SURGE_AXIS])
                spd = np.abs(kin.vel[:, FM.SURGE_AXIS])
                joint = (drift >= th.slide_m) & (spd >= th.slide_speed_ms)
                best = run = 0
                for v in joint:
                    run = run + 1 if v else 0
                    best = max(best, run)
                joints.append(best)
                margins.append(best - th.sustain_frames)
            print(f"    window {w:3d} frames")
            print(f"      verdicts     {dict(Counter(verdicts))}")
            print(f"      joint frames {joints}   min={min(joints)} max={max(joints)}")
            print(f"      margin       {margins}   min={min(margins)} max={max(margins)}")


def find_blocking(explicit: Path | None) -> Path:
    """blocking.py lives on claude/r5-physics, NOT on every branch. This script is
    useful from a worktree that does not carry it, so locate it rather than assume
    it. Fails with a message naming the branch instead of an ImportError."""
    cands = []
    if explicit:
        cands.append(explicit)
    cands.append(REPO / "simulation" / "r5_physics")
    # sibling worktrees under .claude/worktrees, and the main checkout
    for root in (REPO.parent, REPO / ".claude" / "worktrees"):
        if root.is_dir():
            for d in sorted(root.iterdir()):
                cands.append(d / "simulation" / "r5_physics")
    for c in cands:
        if (c / "blocking.py").is_file():
            return c
    raise SystemExit(
        "blocking.py not found. It lives in simulation/r5_physics/ on branch\n"
        "claude/r5-physics and is not present on every branch. Either run this from\n"
        "a checkout that has it, or pass --blocking-dir <path to simulation/r5_physics>.\n"
        f"Searched: {', '.join(str(c) for c in cands[:6])} ..."
    )


def job_b(json_path: Path, window_start: int, blocking_dir: Path | None) -> None:
    """Job B's pre-registered companion criterion. ae08cce fixed this BEFORE any run
    had produced the field, so it cannot have been tuned to a result."""
    bdir = find_blocking(blocking_dir)
    print(f"  [blocking.py from {bdir}]")
    sys.path.insert(0, str(bdir))
    import numpy as np
    import blocking as B

    doc = json.loads(json_path.read_text())
    rows, cfg = doc["rows"], doc["config"]

    def col(name):
        return np.array([r[name] for r in rows], dtype=float)

    print()
    print("=" * 72)
    print(f"5. JOB B, {json_path.name}, {len(rows)} frames, late window from {window_start}")
    print("=" * 72)
    target = cfg["analytic_buoyancy_N"]
    print(f"\n  nominal target {target:.4f} N, sphere r={cfg['ref_radius_m']} m fixed at the")
    print(f"  design waterline z = floor {cfg['floor_m']} + depth {cfg['depth_m']} = "
          f"{cfg['floor_m'] + cfg['depth_m']}")

    print("\n  blocking.stationarity, the project's own test:")
    for name in ("fz_N", "fz_over_analytic_nominal", "fz_over_analytic_measured"):
        r = B.stationarity(col(name)[window_start:])
        print(f"    {name:28s} halves={str(r['halves_stationary']):5s} "
              f"trend={str(r['trend_stationary']):5s} slope_n_sigma={r['slope_n_sigma']:.2f}")

    y = col("fz_over_analytic_measured")[window_start:]
    se = B.blocked_se(y)
    print(f"\n  measured ratio late-window mean {y.mean():.6f} +/- {se['se_blocked']:.6f} "
          f"(blocked SE, converged={se['converged']})")
    print(f"    that is {(y.mean() - 1) * 100:+.3f} % from the closed form at the surface that exists")
    print(f"    tau_int {se['tau_int_frames']:.3f} frames, inflation over naive "
          f"{se['inflation_vs_naive']:.3f}x")
    print("    CAVEAT: the ratio is flat because numerator and denominator fall together.")
    print("    That confirms the MECHANISM. It is NOT an equilibrium measurement.")

    # Independent recomputation of the spherical cap, to show the estimator is not
    # arithmetically at fault. Any disagreement here would mean the +63 % is a slip.
    R = cfg["ref_radius_m"]
    zc = cfg["floor_m"] + cfg["depth_m"]
    design = zc
    print(f"\n  surface fall, and an independent spherical-cap recomputation:")
    print(f"    {'frame':>5} {'surface z':>11} {'drop':>9} {'cap reported':>13} "
          f"{'cap recomputed':>15} {'fz_N':>9} {'ratio':>8}")
    for i in (0, len(rows) // 4, len(rows) // 2, 3 * len(rows) // 4, len(rows) - 1):
        r = rows[i]
        sz = r["surface_z_measured_m"]
        h = sz - (zc - R)
        cap = math.pi * h * h * (3 * R - h) / 3
        print(f"    {r['frame']:5d} {sz:11.6f} {(design - sz) * 100:7.3f} cm "
              f"{r['submerged_cap_m3']:13.6f} {cap:15.6f} {r['fz_N']:9.4f} "
              f"{r['fz_over_analytic_measured']:8.4f}")

    ssz = col("surface_z_measured_m")[window_start:]
    rs = B.stationarity(ssz)
    print(f"\n    surface_z_measured_m late window: trend_stationary={rs['trend_stationary']}, "
          f"slope_n_sigma={rs['slope_n_sigma']:.2f}")
    print("    Still falling at the last frame means more frames alone will not fix it.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobA", type=Path, help="extracted d4_jobA directory from job 917797")
    ap.add_argument("--jobB", type=Path, help="sphere_fixed_g64.json from job 918043 or later")
    ap.add_argument("--windows", type=int, nargs="+", default=[90, 111, 250],
                    help="frame windows to report. 90 is the CANONICAL horizon (see below), "
                         "112 is the first observed wall reflection. Default: 90 111 250")
    ap.add_argument("--jobB-window-start", type=int, default=100,
                    help="late-window start for job B (default 100, the grader's)")
    ap.add_argument("--tmp", type=Path, default=Path("/tmp/r6_repeat_stats"),
                    help="scratch for truncated CSVs. Never inside the repo.")
    ap.add_argument("--blocking-dir", type=Path, default=None,
                    help="path to simulation/r5_physics, which carries blocking.py. "
                         "Only on branch claude/r5-physics; auto-located if omitted.")
    args = ap.parse_args()

    if not args.jobA and not args.jobB:
        ap.error("give at least one of --jobA or --jobB")

    if args.jobA:
        base = args.jobA
        if not (base / "rep_v0p5_1" / "metrics.csv").exists():
            ap.error(f"{base} does not look like a d4_jobA tree "
                     f"(no rep_v0p5_1/metrics.csv)")
        bit_identity(base)
        divergence_onset(base)
        dmag_spread(base, tuple(args.windows))
        classify_and_margin(base, tuple(args.windows), args.tmp)

    if args.jobB:
        job_b(args.jobB, args.jobB_window_start, args.blocking_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
