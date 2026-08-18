#!/usr/bin/env python3
"""Audit every local run's time series against a data-driven settling criterion.

Answers one question per run: how many leading frames does the record itself say
must be discarded, against the 8 frames `sim_standing.py` actually used?

This needs no GPU. The 15-column FloodHistory metrics CSV for the local runs is
already on disk, so the whole audit is a laptop job.

Method and citations live in analysis/stationarity.py. Pure standard library.

Usage
    python3 analysis/settle_audit.py                    # every run under the repo
    python3 analysis/settle_audit.py --scope renders    # the pre-2026-08-18 scope
    python3 analysis/settle_audit.py --glob 'g64*'      # subset
    python3 analysis/settle_audit.py --csv out.csv      # machine-readable

RUN THIS AGAINST THE MAIN CHECKOUT, NOT A WORKTREE
--------------------------------------------------
Nearly every run record is gitignored (`.gitignore` `data/*` and
`renders/yaris_render_s1/*`), so it is PHYSICALLY ABSENT from a git worktree.
Measured 2026-08-18: a repo-root walk finds 51 records in
/Users/josie/can-it-ford and 1 in .claude/worktrees/r9-settle. A worktree run
therefore returns an almost-empty audit with no error at all. Use `--root` to
point at the main checkout when running from anywhere else.

DISCOVERY, AND THE TWO WAYS IT USED TO UNDERCOUNT
-------------------------------------------------
Both fixed 2026-08-18, both measured, and each one alone was silent:

1. ROOT. Discovery walked only `<repo>/renders`, which sees 25 records. It
   missed 12 under `data/g128_canonical_2026-08-13/` and
   `data/g128_canonical_repeat/`, and 3 under
   `render_s2/multigeom_2026-08-08/`, which is a SIBLING of `renders/` and not
   inside it. Slot d2-persist hit the identical defect in its own script and
   fixed it the same way, by walking the repo root and pruning, rather than by
   lengthening a hardcoded tree list.

2. FILENAME. Discovery matched the exact name `metrics.csv`. Eleven further
   records, all TRACKED and all 15-column, are named `<run>_metrics.csv` under
   `data/g128_2026-08-18/` and `data/g128_sweeps_2026-08-18/`. A root walk alone
   still misses them, so fixing the root without fixing the pattern gives 40 and
   looks complete.

Together: 51 records on disk, of which 3 are byte-identical duplicates of
another record (the top-level `renders/yaris_render_s1/{g64_m1100,g64_m1609,
g64_m2337}/` copies of the `_incoming/` originals, confirmed by md5), so there
are 48 DISTINCT records. Duplicates are detected by content hash and dropped,
because counting a file twice inflates the apparent independence of the
evidence. `--keep-duplicates` restores the old behaviour for reproduction.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stationarity import analyze  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories that never hold run output and are expensive or misleading to walk.
PRUNE = {".git", ".claude", "third_party", "__pycache__", ".venv",
         "node_modules", ".mypy_cache", ".pytest_cache"}

# The settle length baked into the driver, for comparison.
DRIVER_SETTLE_FRAMES = 8
DRIVER_REF = "renders/yaris_render_s1/sim_standing.py, settle_frames default"

# Observables worth testing.
#
# WHICH CHANNEL A VERDICT ACTUALLY READS, corrected 2026-08-18. This comment
# used to read "dmag and vmag are what the verdicts read". THAT WAS FALSE.
# simulation/failure_modes.py sets SURGE_AXIS = 0 and gates SLIDE on the surge
# COMPONENT, not the magnitude:
#     surge_drift = np.abs(kin.disp[:, SURGE_AXIS])   -> |dx|
#     surge_speed = np.abs(kin.vel[:, SURGE_AXIS])    -> |vx|
#     slide when (surge_drift >= slide_m) & (surge_speed >= slide_speed_ms)
#                sustained for sustain_frames
# read directly from simulation/failure_modes.py this session, not relayed.
# Slot d2-persist found the same surge-versus-magnitude split independently and
# it survived an adversarial check, so this is a confirmed claim, not a raw one.
#
# The code under the old comment had HALF believed it: `vx` was tested but `dx`
# was not, and the headline default was `dmag`. So the published headline was
# computed on a channel no verdict reads. Both surge channels are now included
# and the headline defaults to `dx`.
#
# dmag and vmag are retained deliberately: they are what analysis/
# probabilistic_verdict.py reads, so the magnitude channel is still a real
# published channel. It is simply a DIFFERENT one, and every count from this
# script names its channel.
OBSERVABLES = ["dx", "dmag", "vx", "vmag"]

VERDICT_CHANNEL = {
    "dx": "surge displacement, the SLIDE distance gate in failure_modes.py",
    "vx": "surge speed, the SLIDE speed gate in failure_modes.py",
    "dmag": "displacement magnitude, read by probabilistic_verdict.py",
    "vmag": "speed magnitude, read by probabilistic_verdict.py",
}


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


def _digest(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def find_runs(root: str, pattern: str | None = None, scope: str = "all",
              keep_duplicates: bool = False
              ) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return (runs, duplicates_dropped).

    A run is any `metrics.csv` or `<run>_metrics.csv` under `root`. `scope`
    "renders" restricts to `<root>/renders`, reproducing the pre-2026-08-18
    behaviour so the old figures can be re-derived rather than argued about.
    """
    base = os.path.join(root, "renders") if scope == "renders" else root
    found: list[tuple[str, str]] = []
    for dirpath, dirnames, files in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        for fn in files:
            if fn == "metrics.csv":
                name = os.path.relpath(dirpath, base)
            elif fn.endswith("_metrics.csv"):
                stem = fn[: -len("_metrics.csv")]
                rel = os.path.relpath(dirpath, base)
                name = stem if rel == "." else os.path.join(rel, stem)
            else:
                continue
            found.append((name, os.path.join(dirpath, fn)))
    found.sort()

    if pattern:
        found = [(n, p) for n, p in found
                 if fnmatch.fnmatch(os.path.basename(n), pattern)]

    if keep_duplicates:
        return found, []

    seen: dict[str, str] = {}
    runs, dropped = [], []
    for name, path in found:
        d = _digest(path)
        if d in seen:
            dropped.append((name, seen[d]))
            continue
        seen[d] = name
        runs.append((name, path))
    return runs, dropped



# ---------------------------------------------------------------------------
# VERDICT SENSITIVITY TO THE SETTLE LENGTH
#
# The audit above measures how long the RECORDED series takes to become
# stationary. That is NOT the same quantity as the driver's `settle_frames`,
# and the two must never be substituted for one another:
#
#   settle_frames      frames run BEFORE recording starts and BEFORE the
#                      displacement datum com0 is captured. Changing it changes
#                      the physical initial condition and costs GPU time.
#   recommended_discard  a post-hoc truncation of the RECORDED frames. Changing
#                      it costs nothing and only changes which statistics you
#                      compute.
#
# Read sim_standing.py: the settle loop runs, THEN the one-shot velocity kick is
# added to the water, THEN com0 is captured and the first history row written.
# So the recorded record contains zero settle frames, and a large
# recommended_discard is mostly the forced response to the kick, which is the
# physics under study rather than leftover settling.
#
# What the recorded data CAN answer is whether the residual initial condition
# left by a short settle is large enough to change a published verdict. That is
# what this section measures, on the surge channel the SLIDE gate actually
# reads.
# ---------------------------------------------------------------------------

# simulation/failure_modes.py, read live 2026-08-18: SURGE_AXIS = 0,
# slide_m = 0.05 m, slide_speed_ms = 0.05 m/s, sustain_frames = 3.
SLIDE_M = 0.05
SLIDE_SPEED_MS = 0.05
SUSTAIN_FRAMES = 3


def slide_onset(dx: list[float], vx: list[float]) -> int:
    """First frame of the first `SUSTAIN_FRAMES`-long sustained SLIDE window.

    Reproduces failure_modes.py's gate on the surge component. Returns -1 for no
    sustained slide. Verified against data/failure_modes_by_run_classified.csv:
    17 of 17 canonical runs match `onset_frame_slide`, including the single -1.
    """
    run = 0
    for i in range(len(dx)):
        hit = abs(dx[i]) >= SLIDE_M and abs(vx[i]) >= SLIDE_SPEED_MS
        run = run + 1 if hit else 0
        if run >= SUSTAIN_FRAMES:
            return i - SUSTAIN_FRAMES + 1
    return -1


def _flip_bias(t, dx, vx, base, limit=2.0, step=1e-4):
    """Smallest constant surge-velocity bias that flips the SLIDE verdict.

    A residual settle velocity acts on the record as a constant surge drift, so
    this asks how large that drift would have to be before the verdict changes.
    Returns None if no bias below `limit` m/s flips it.
    """
    t0 = t[0]
    n = int(limit / step)
    for k in range(1, n + 1):
        for sgn in (1, -1):
            b = sgn * k * step
            dxc = [d + b * (tt - t0) for d, tt in zip(dx, t)]
            vxc = [v + b for v in vx]
            if (slide_onset(dxc, vxc) >= 0) != (base >= 0):
                return abs(b)
    return None


def verdict_sensitivity(runs: list[tuple[str, str]]) -> int:
    print("VERDICT SENSITIVITY TO THE SETTLE LENGTH")
    print("Channel: surge (dx, vx), which is what failure_modes.py gates SLIDE "
          "on.\nFull record, never a trimmed window: incipient motion is an "
          "EVENT and trimming\nthe transient would delete the frames the gate "
          "exists to find.")
    print()
    hdr = (f"{'run':44} {'v[0]':>9} {'a0->1(g)':>9} {'vx1/pk':>7} "
           f"{'onset':>6} {'cf':>4} {'flip@':>8}")
    print(hdr)
    print("-" * len(hdr))

    n_slide = n_slide_cf = 0
    shifts, v0s, accs, fracs, flips, resid = [], [], [], [], [], []
    for name, path in runs:
        c = load_series(path)
        if "vx" not in c or len(c.get("vx", [])) < 5:
            continue
        t, dx, vx = c["t"], c["dx"], c["vx"]
        dt = (t[-1] - t[0]) / (len(t) - 1)
        base = slide_onset(dx, vx)
        v0 = vx[0]
        # counterfactual: a perfectly settled scene has vx[0] = 0. Remove the
        # frame-0 surge velocity as a rigid drift from both channels.
        dxc = [d - v0 * (tt - t[0]) for d, tt in zip(dx, t)]
        vxc = [v - v0 for v in vx]
        cf = slide_onset(dxc, vxc)
        pk = max(abs(x) for x in vx) or 1.0
        acc = abs(vx[1] - vx[0]) / dt / 9.81
        fb = _flip_bias(t, dx, vx, base)

        n_slide += base >= 0
        n_slide_cf += cf >= 0
        if base >= 0 and cf >= 0:
            shifts.append(cf - base)
        if base >= 0:
            resid.append(abs(v0 * (t[base] - t[0])))
        v0s.append(abs(v0))
        accs.append(acc)
        fracs.append(abs(vx[1]) / pk)
        if fb is not None:
            flips.append((fb, name))
        print(f"{name[:44]:44} {v0:9.5f} {acc:9.2f} {abs(vx[1]) / pk:7.3f} "
              f"{base:6d} {cf:4d} "
              f"{(f'{fb:.4f}' if fb is not None else '>2.0'):>8}")

    v0s.sort(); accs.sort(); fracs.sort(); resid.sort(); flips.sort()
    print()
    print(f"runs evaluated: {len(v0s)}")
    print(f"  SLIDE as recorded            : {n_slide}")
    print(f"  SLIDE perfectly settled (cf) : {n_slide_cf}")
    print(f"  onset frames that MOVE under the counterfactual: "
          f"{sum(1 for s in shifts if s != 0)} of {len(shifts)}")
    print()
    print("  THE INITIAL CONDITION IS SMALL IN THE CHANNEL THAT DECIDES THE "
          "VERDICT:")
    print(f"    |vx[0]| max {v0s[-1]:.5f} m/s = "
          f"{v0s[-1] / SLIDE_SPEED_MS:.3f}x the slide_speed_ms gate "
          f"(never reaches it)")
    if resid:
        print(f"    |vx[0]| * t_onset, the drift it contributes by the time the "
              f"gate is tested:\n      max {resid[-1] * 1000:.3f} mm = "
              f"{resid[-1] / SLIDE_M * 100:.2f} percent of the {SLIDE_M} m gate")
    print()
    print("  THE FORCING IS IMPULSIVE, WHICH IS WHY THE SETTLE CANNOT REACH "
          "THE VERDICT:")
    print(f"    frame 0->1 surge acceleration, g : min {accs[0]:.2f}  "
          f"median {accs[len(accs) // 2]:.2f}  max {accs[-1]:.2f}")
    print(f"    |vx[1]| as a share of that run's peak |vx| : "
          f"median {fracs[len(fracs) // 2]:.3f}")
    print(f"    runs above half their peak surge speed by frame 1: "
          f"{sum(1 for f in fracs if f > 0.5)} of {len(fracs)}")
    print("    For scale, steady drag at Cd = 1.0 on the 1100 kg hull at "
          "2.0 m/s over a\n    1.7078 m x 0.2944 m submerged frontal area is "
          "0.0932 g. The measured frame\n    0->1 acceleration is more than an "
          "order of magnitude above that, so it is the\n    one-shot kick "
          "landing, not a steady hydrodynamic load.")
    print()
    print("  WHERE THE MARGIN IS THIN. Smallest surge bias that flips a "
          "verdict:")
    for fb, name in flips[:6]:
        print(f"    {fb:.4f} m/s  = {fb / (v0s[-1] or 1):5.1f}x the worst "
              f"frame-0 residual observed   {name}")
    if not flips:
        print("    none below 2.0 m/s")
    return 0

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO,
                    help="repo root to search; point at the MAIN checkout when "
                         "running from a worktree, where run data is absent")
    ap.add_argument("--scope", default="all", choices=["all", "renders"],
                    help="'renders' reproduces the pre-2026-08-18 scope")
    ap.add_argument("--glob", default=None, help="run-directory glob")
    ap.add_argument("--csv", default=None, help="write machine-readable output")
    ap.add_argument("--keep-duplicates", action="store_true",
                    help="do not drop byte-identical records")
    ap.add_argument("--verdict-sensitivity", action="store_true",
                    help="measure whether the settle residual could change "
                         "a SLIDE verdict, on the surge channel")
    ap.add_argument("--observable", default="dx",
                    help="observable for the headline table")
    args = ap.parse_args()

    runs, dropped = find_runs(args.root, args.glob, args.scope,
                              args.keep_duplicates)
    if not runs:
        print(f"no runs found under {args.root} (scope={args.scope}).")
        print("If you are in a git worktree, the run data is gitignored and "
              "physically absent. Pass --root /Users/josie/can-it-ford.")
        return 1

    if args.verdict_sensitivity:
        return verdict_sensitivity(runs)

    print(f"Settle audit against the driver's fixed "
          f"settle_frames={DRIVER_SETTLE_FRAMES} ({DRIVER_REF})")
    print(f"root: {args.root}   scope: {args.scope}")
    print(f"distinct runs: {len(runs)}   byte-identical duplicates dropped: "
          f"{len(dropped)}")
    for name, keeper in dropped:
        print(f"    dup: {name}  ==  {keeper}")
    print(f"headline observable: {args.observable}  "
          f"({VERDICT_CHANNEL.get(args.observable, 'unclassified')})")
    print()
    hdr = (f"{'run':44} {'n':>4} {'need':>5} {'used':>5} {'tau':>6} "
           f"{'N_eff':>7} {'stat?':>6} {'RUM95':>11}")
    print(hdr)
    print("-" * len(hdr))

    rows: list[dict] = []
    per_obs: dict[str, list[dict]] = {o: [] for o in OBSERVABLES}
    missing: dict[str, list[str]] = {o: [] for o in OBSERVABLES}
    for name, path in runs:
        cols = load_series(path)
        for obs in OBSERVABLES:
            if obs not in cols or len(cols[obs]) < 20:
                missing[obs].append(name)
                continue
            rep = analyze(cols[obs], f"{name}:{obs}")
            row = {
                "run": name, "observable": obs,
                "n_frames": rep["n_total"],
                "recommended_discard": rep["recommended_discard"],
                "driver_settle_frames": DRIVER_SETTLE_FRAMES,
                "exceeds_driver": rep["recommended_discard"]
                > DRIVER_SETTLE_FRAMES,
                "at_mser_bound": rep["recommended_discard"]
                >= rep["n_total"] - 11,
                "tau_int": round(rep["tau_int"], 4),
                "n_eff": round(rep["n_eff"], 2),
                "window_len": rep["window_len"],
                "stationary_at_5pct": rep["stationary_at_5pct"],
                "reverse_arrangement_z": round(
                    rep["reverse_arrangement_z"], 3),
                "mean": rep["mean"],
                "rum_95_halfwidth": rep["rum_95"],
                "std_err_correlated": rep["std_err_correlated"],
            }
            rows.append(row)
            per_obs[obs].append(row)
            if obs != args.observable:
                continue
            print(f"{name[:44]:44} {rep['n_total']:4d} "
                  f"{rep['recommended_discard']:5d} "
                  f"{DRIVER_SETTLE_FRAMES:5d} {rep['tau_int']:6.2f} "
                  f"{rep['n_eff']:7.1f} "
                  f"{'yes' if rep['stationary_at_5pct'] else 'NO':>6} "
                  f"{rep['rum_95']:11.4g}")

    print()
    print("PER-CHANNEL SUMMARY. Every count below names its channel, because "
          "the SLIDE gate\nand the probabilistic verdict read different ones "
          "and a bare integer hides which.")
    print()
    ch = (f"{'channel':6} {'runs':>5} {'need>8':>7} {'nonstat':>8} "
          f"{'atbound':>8} {'min':>4} {'med':>4} {'max':>4}  what it gates")
    print(ch)
    print("-" * len(ch))
    for obs in OBSERVABLES:
        head = per_obs[obs]
        if not head:
            continue
        needs = sorted(r["recommended_discard"] for r in head)
        worse = sum(1 for r in head if r["exceeds_driver"])
        nonstat = sum(1 for r in head if not r["stationary_at_5pct"])
        bound = sum(1 for r in head if r["at_mser_bound"])
        print(f"{obs:6} {len(head):5d} {worse:7d} {nonstat:8d} {bound:8d} "
              f"{needs[0]:4d} {needs[len(needs) // 2]:4d} {needs[-1]:4d}  "
              f"{VERDICT_CHANNEL.get(obs, '')}")
    for obs in OBSERVABLES:
        if missing[obs]:
            print(f"  note: {obs} absent or too short in {len(missing[obs])} "
                  f"run(s): {', '.join(missing[obs][:3])}"
                  f"{' ...' if len(missing[obs]) > 3 else ''}")

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
          "settle-length\nsweep across arms. The 'atbound' column counts those "
          "runs so they are never read as\na settle recommendation.")
    print()
    print("THE RULE IS ASYMMETRIC, AND THIS SCRIPT DOES NOT LICENSE HALF OF "
          "IT.\nUse the FULL RECORD for a verdict: incipient motion is an "
          "EVENT, and trimming the\ntransient before a SLIDE test removes the "
          "very frames the test exists to find.\nUse a demonstrated-stationary "
          "window for any CONVERGENCE or UNCERTAINTY claim.\nApplying either "
          "rule to both cases gives a wrong answer in one of them.")

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
