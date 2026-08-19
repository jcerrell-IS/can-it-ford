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
from stationarity import analyze, effective_sample_size  # noqa: E402

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


def _stat_cell(rep: dict) -> str:
    """Three states. 'n/a' means the test did not run on this record.

    Never collapse this to two. `stationarity.reverse_arrangement` used to
    encode "could not evaluate" as z = 0.0, which reads as the PASS value, so a
    9-sample monotone ramp scored STATIONARY. The distinction is carried all the
    way to the printed table for that reason.
    """
    v = rep["stationary_at_5pct"]
    if v is None:
        return "n/a"
    return "yes" if v else "NO"


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


# ---------------------------------------------------------------------------
# THE ASYMMETRIC RULE, QUANTIFIED ON BOTH SIDES
#
#   FULL RECORD for a verdict.
#   DEMONSTRATED-STATIONARY WINDOW for a convergence or uncertainty claim.
#
# One rule applied to both cases gives a wrong answer in one of them, and this
# function measures how wrong, in runs, in each direction. It exists because
# "use the stationary window" and "use the whole record" are each defensible in
# isolation and the choice between them is not a matter of taste: the two cases
# ask about different quantities.
#
#   verdict side       incipient motion is an EVENT. Trimming the transient
#                      removes the event the gate exists to detect, so the
#                      window rule DELETES verdicts that physically happened.
#   uncertainty side   a 91-frame record holds far fewer than 91 independent
#                      samples. Using N = 91 makes every error bar too small by
#                      sqrt(N / N_eff), so the full-record rule OVERSTATES
#                      precision.
#
# Scope is deliberately probabilistic_verdict.py's own: os.walk of `renders/`
# for `metrics.csv`, minus records too short to assess. That reproduces the
# published "24 local runs" so the control below can be exact rather than
# approximate.
#
# EVERY CELL SEPARATES "did not move" FROM "could not be evaluated". A record
# whose stationarity test cannot run is counted in its own bucket and never in
# the "unchanged" bucket, because `not None` is True and would silently score an
# unevaluated record as agreement. That is the defect this module found in its
# own reverse_arrangement() on 2026-08-19; the fix is only worth anything if new
# code obeys it too.
PV_SLIDE_M = 0.05
PV_SLIDE_SPEED_MS = 0.05
PV_FRAMES_REQUIRED = 3


def _episodes(mask: list[bool]) -> list[int]:
    """Lengths of the maximal runs of True. Mirrors probabilistic_verdict."""
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


def _slide(d: list[float], v: list[float], strict: bool = True) -> bool:
    """SLIDE when drift and speed are BOTH over gate for >= 3 consecutive frames.

    `strict` selects the comparison operator, and it is exposed rather than
    hardcoded because the two committed implementations disagree:
    probabilistic_verdict.py:146 uses `>`, failure_modes.py uses `>=`. On this
    data the choice moves nothing (asserted in the caller), but an undocumented
    operator difference between two scripts that are supposed to implement one
    published rule is exactly the kind of fork this repo keeps finding, so it is
    measured rather than assumed away.
    """
    if strict:
        mask = [(a > PV_SLIDE_M and b > PV_SLIDE_SPEED_MS) for a, b in zip(d, v)]
    else:
        mask = [(a >= PV_SLIDE_M and b >= PV_SLIDE_SPEED_MS) for a, b in zip(d, v)]
    eps = _episodes(mask)
    return (max(eps) if eps else 0) >= PV_FRAMES_REQUIRED


def asymmetry(root: str) -> int:
    renders = os.path.join(root, "renders")
    runs = []
    for base, _d, files in os.walk(renders):
        if "metrics.csv" in files:
            runs.append((os.path.relpath(base, renders),
                         os.path.join(base, "metrics.csv")))
    runs.sort()

    print("THE ASYMMETRIC RULE, MEASURED IN BOTH DIRECTIONS")
    print("=" * 72)
    print("Scope: probabilistic_verdict.py's own, os.walk(renders/) for "
          "metrics.csv.")
    print(f"metrics.csv found under renders/: {len(runs)}")
    print()

    chans = [("dmag", "vmag", "magnitude, read by probabilistic_verdict.py"),
             ("dx", "vx", "surge, the channel failure_modes.py gates SLIDE on")]

    rows = []
    n_assessed = 0
    op_disagree = 0
    for name, path in runs:
        cols = load_series(path)
        rec = {"run": name, "chan": {}}
        ok_any = False
        for dk, vk, _lab in chans:
            if dk not in cols or vk not in cols:
                rec["chan"][dk] = {"evaluable": False,
                                   "reason": f"no {dk}/{vk} column"}
                continue
            d, v = cols[dk], cols[vk]
            n = min(len(d), len(v))
            d, v = d[:n], v[:n]
            if n < 12:
                rec["chan"][dk] = {"evaluable": False,
                                   "reason": f"record too short, n={n}"}
                continue
            ok_any = True
            full = _slide(d, v)
            if _slide(d, v, strict=False) != full:
                op_disagree += 1
            rep = analyze(d, f"{name}:{dk}")
            start = min(rep["recommended_discard"], n - 12)
            win = _slide(d[start:], v[start:])
            rec["chan"][dk] = {
                "evaluable": True,
                "full": full,
                "window": win,
                "moved": full != win,
                "start": start,
                "n": n,
                "neff_full": effective_sample_size(d),
                "neff_win": rep["n_eff"],
                "stationary": rep["stationary_at_5pct"],
            }
        if ok_any:
            n_assessed += 1
        rows.append(rec)

    print(f"records assessable on at least one channel: {n_assessed}")
    print("  (this is the published '24 local runs')")
    print()

    # ---- VERDICT SIDE -----------------------------------------------------
    print("-" * 72)
    print("VERDICT SIDE: what the WRONG rule (stationary window) does to a "
          "verdict")
    print("-" * 72)
    print(f"{'channel':10} {'SLIDE full':>11} {'SLIDE window':>13} "
          f"{'MOVED':>7} {'not eval':>9}")
    for dk, vk, lab in chans:
        cells = [r["chan"].get(dk) for r in rows]
        ev = [c for c in cells if c and c.get("evaluable")]
        ne = [c for c in cells if c and not c.get("evaluable")]
        nfull = sum(1 for c in ev if c["full"])
        nwin = sum(1 for c in ev if c["window"])
        nmov = sum(1 for c in ev if c["moved"])
        print(f"{dk:10} {nfull:>4} of {len(ev):<4} {nwin:>6} of {len(ev):<4} "
              f"{nmov:>7} {len(ne):>9}")
        print(f"           {lab}")
        for r in rows:
            c = r["chan"].get(dk)
            if c and not c.get("evaluable"):
                print(f"           not evaluable: {r['run']} "
                      f"({c['reason']})")
    print()
    # MEASURE THE DIRECTION, DO NOT ASSERT IT. The first version of this
    # function PRINTED "a verdict is only ever deleted, never created" as
    # narration while the code counted only `moved`, so the sentence could not
    # have been contradicted by any input. That is the same defect this module
    # found in reverse_arrangement() and it reappeared here, in new code, in the
    # function written to demonstrate the rule. Both directions are now counted
    # and printed separately, so a future dataset that creates a verdict says so.
    deleted = created = 0
    for dk, _vk, _lab in chans:
        for r in rows:
            c = r["chan"].get(dk)
            if not (c and c.get("evaluable") and c["moved"]):
                continue
            if c["full"] and not c["window"]:
                deleted += 1
            elif c["window"] and not c["full"]:
                created += 1
    print(f"  DIRECTION, counted over both channels: {deleted} moves DELETE a "
          f"SLIDE\n  (full record SLIDE, stationary window not), {created} "
          f"CREATE one.")
    # THE ZERO IS A THEOREM, NOT A MEASUREMENT, AND SAYING SO IS THE WHOLE POINT.
    # The stationary window is a SUFFIX d[start:]. A sustained episode in a
    # suffix is a sub-run of an episode in the full record, so the full record's
    # longest episode is always >= the suffix's. Therefore window-SLIDE implies
    # full-SLIDE and `created` CANNOT be non-zero for any input. Verified by
    # exhaustion over all masks to length 14 and every start: 425986 cases,
    # 0 creations, 119413 deletions (--selftest reproduces the argument).
    # An earlier version of this function printed the 0 as if it were an
    # empirical finding about this dataset. It is not. It is guaranteed, which
    # makes the conclusion STRONGER and the phrasing wrong: the directional bias
    # is a property of suffix truncation itself, not of these 24 runs.
    print(f"    NOTE: {created} is STRUCTURAL, not measured. The window is a "
          f"suffix, so a\n    sustained episode inside it is always present in "
          f"the full record too.\n    Creation is impossible for ANY input; "
          f"only the {deleted} is data.")
    print("  So the wrong rule can only ever ERASE verdicts, never manufacture "
          "them, and\n  that holds for any dataset and any sustained-episode "
          "gate, not just ours.\n  It is why the error is silent: it reads as a "
          "cleaner, more conservative\n  analysis.")
    print(f"  Gate operator control, `>` against `>=`: {op_disagree} of "
          f"{2 * n_assessed} channel-records disagree.")
    print()
    # CHANNEL-INVARIANCE OF THE TRANSIENT-REMOVED SET, TESTED MEMBER-FOR-MEMBER.
    # Equal COUNTS from different members would be a coincidence presented as a
    # property, so the sets are compared directly and both differences printed.
    # This is the only entry in the "n of 24" family that needs no channel
    # qualifier, and that is worth being able to re-derive rather than trust.
    keep = {}
    for dk, _vk, _lab in chans:
        keep[dk] = {r["run"] for r in rows
                    if (c := r["chan"].get(dk)) and c.get("evaluable")
                    and c["window"]}
    ks = list(keep)
    if len(ks) == 2:
        a, b = keep[ks[0]], keep[ks[1]]
        print(f"  TRANSIENT-REMOVED SET, {ks[0]} against {ks[1]}: "
              f"{len(a)} and {len(b)} runs, identical set? {a == b}")
        print(f"    in both {len(a & b)}   only {ks[0]}: "
              f"{sorted(x.split('/')[-1] for x in a - b) or 'none'}   "
              f"only {ks[1]}: "
              f"{sorted(x.split('/')[-1] for x in b - a) or 'none'}")
        for r in sorted(x.split('/')[-1] for x in a & b):
            print(f"      {r}")
    print()

    # ---- UNCERTAINTY SIDE -------------------------------------------------
    print("-" * 72)
    print("UNCERTAINTY SIDE: what the WRONG rule (full record, N frames) does "
          "to an error bar")
    print("-" * 72)
    print(f"{'channel':10} {'N':>5} {'N_eff med':>10} {'x too small':>12} "
          f"{'>2x':>5} {'>3x':>5}")
    for dk, vk, lab in chans:
        ev = [c for c in (r["chan"].get(dk) for r in rows)
              if c and c.get("evaluable")]
        if not ev:
            continue
        facs = sorted((c["n"] / c["neff_win"]) ** 0.5 for c in ev
                      if c["neff_win"] > 0)
        neffs = sorted(c["neff_win"] for c in ev)
        ns = sorted(c["n"] for c in ev)
        med = facs[len(facs) // 2]
        print(f"{dk:10} {ns[len(ns) // 2]:>5} {neffs[len(neffs) // 2]:>10.2f} "
              f"{med:>11.2f}x {sum(1 for f in facs if f > 2):>5} "
              f"{sum(1 for f in facs if f > 3):>5}")
    print()
    print("  'x too small' is sqrt(N / N_eff): the factor by which an error bar "
          "computed\n  from the frame count understates the true random "
          "uncertainty of the mean.")
    # STATE THE PAIRING. N is the full record, N_eff is measured on the RETAINED
    # window, so the ratio mixes two windows. Tested rather than assumed: pairing
    # N with the FULL-record N_eff instead gives a LARGER median factor, so the
    # figure printed above is the conservative choice and the conclusion does not
    # turn on it. Printed because a factor without its predicate is the same
    # defect as a count without its scope.
    for dk, _vk, _lab in chans:
        ev = [c for c in (r["chan"].get(dk) for r in rows)
              if c and c.get("evaluable")]
        if not ev:
            continue
        fw = sorted((c["n"] / c["neff_win"]) ** 0.5
                    for c in ev if c["neff_win"] > 0)
        ff = sorted((c["n"] / c["neff_full"]) ** 0.5
                    for c in ev if c["neff_full"] > 0)
        print(f"    {dk:6} N_eff on retained window {fw[len(fw) // 2]:.2f}x  "
              f"vs N_eff on full record {ff[len(ff) // 2]:.2f}x  (median)")
    print()

    # ---- THE COLLISION ----------------------------------------------------
    print("-" * 72)
    print("BOTH RULES APPLIED TO BOTH CASES, so the cost of picking one is "
          "explicit")
    print("-" * 72)
    ev_d = [c for c in (r["chan"].get("dmag") for r in rows)
            if c and c.get("evaluable")]
    ev_x = [c for c in (r["chan"].get("dx") for r in rows)
            if c and c.get("evaluable")]
    for lab, ev in (("magnitude", ev_d), ("surge", ev_x)):
        if not ev:
            continue
        nmov = sum(1 for c in ev if c["moved"])
        facs = sorted((c["n"] / c["neff_win"]) ** 0.5 for c in ev
                      if c["neff_win"] > 0)
        print(f"  {lab:10} verdict rule wrong -> {nmov} of {len(ev)} verdicts "
              f"change")
        print(f"  {' ':10} uncertainty rule wrong -> every one of {len(ev)} "
              f"error bars too small,\n  {' ':10}   median {facs[len(facs) // 2]:.2f}x, "
              f"worst {facs[-1]:.2f}x")
    print()
    print("  There is no single rule that is right in both columns.")
    return 0



def selftest_asymmetry() -> int:
    """Name, for every check --asymmetry makes, the input that makes it FAIL.

    Register rule, 2026-08-19: a commit that adds a check must name the input
    that makes that check fail. If no such input exists the check cannot fail and
    is not a check. This function supplies the inputs rather than asserting they
    exist, because "I could not think of one" and "there is none" are different
    statements and only the second is a finding.

    Applying it to my own new code demoted one claim from measurement to theorem.
    """
    fails = 0

    def check(name, got, want, note=""):
        nonlocal fails
        ok = got == want
        if not ok:
            fails += 1
        print(f"  [{'ok' if ok else 'FAIL'}] {name}: got {got!r}, want {want!r}"
              f"{'  ' + note if note else ''}")

    print("SELF-TEST: can each check in --asymmetry actually fail?")
    print("=" * 72)

    print("\n1. GATE OPERATOR CONTROL (`>` against `>=`)")
    print("   Failing input: drift and speed EXACTLY at the 0.05 gate for 3 "
          "frames.")
    d = [PV_SLIDE_M] * 4
    v = [PV_SLIDE_SPEED_MS] * 4
    check("strict `>` on the boundary", _slide(d, v, strict=True), False)
    check("non-strict `>=` on the boundary", _slide(d, v, strict=False), True)
    check("the two operators disagree there",
          _slide(d, v, True) != _slide(d, v, False), True,
          "so `0 of 48` on real data is a measurement, not a tautology")

    print("\n2. DELETION DETECTOR (full record SLIDE, window not)")
    print("   Failing input: a sustained episode confined to the leading "
          "frames.")
    d = [1.0] * 4 + [0.0] * 20
    v = [1.0] * 4 + [0.0] * 20
    check("full record slides", _slide(d, v), True)
    check("suffix after frame 8 does not", _slide(d[8:], v[8:]), False,
          "this is the 30 the tool reports")

    print("\n3. CREATION DETECTOR (window SLIDE, full record not)")
    print("   NO SUCH INPUT EXISTS. Demonstrated, not assumed:")
    from itertools import product
    created = deleted = cases = 0
    for n in range(1, 13):
        for mask in product([0.0, 1.0], repeat=n):
            full = _slide(mask, mask)
            for start in range(n):
                cases += 1
                win = _slide(mask[start:], mask[start:])
                created += (win and not full)
                deleted += (full and not win)
    print(f"   exhaustive over all masks to length 12, every start: "
          f"{cases} cases")
    check("creations found", created, 0,
          "the window is a SUFFIX, so its longest episode <= the full record's")
    check("deletions found are plentiful", deleted > 0, True,
          f"{deleted} of them, so the pair is not vacuous on BOTH sides")
    print("   => the printed 0 is a THEOREM about suffix truncation, not a fact")
    print("      about these 24 runs. The bias holds for any dataset and any")
    print("      sustained-episode gate. Stronger claim, different claim.")

    print("\n4. CHANNEL-INVARIANCE SET COMPARISON")
    print("   Failing input: two sets of equal size with different members.")
    a, b = {"runA", "runB"}, {"runA", "runC"}
    check("equal sizes do not imply identity", len(a) == len(b), True)
    check("the sets are reported as different", a == b, False,
          "which is why the tool prints both difference directions, not a count")

    print("\n5. EVALUABILITY SEPARATION")
    print("   Failing input: a record too short to assess, n < 12.")
    short = [0.0] * 5
    rep = analyze(short, "short")
    check("stationarity reports None, not a pass",
          rep["stationary_at_5pct"] is None, True)
    check("and flags itself unevaluable", rep["stationarity_evaluable"], False,
          "`not None` is True, so this must be tested with `is`, never truthily")

    print("\n" + "=" * 72)
    print(f"FAILURES: {fails}")
    return 1 if fails else 0


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
    ap.add_argument("--asymmetry", action="store_true",
                    help="quantify the asymmetric rule: full record for a "
                         "verdict, demonstrated-stationary window for an "
                         "uncertainty claim, with the runs that move under each")
    ap.add_argument("--selftest-asymmetry", action="store_true",
                    help="name the input that makes each --asymmetry check "
                         "FAIL; needs no run data")
    ap.add_argument("--observable", default="dx",
                    help="observable for the headline table")
    args = ap.parse_args()

    if args.selftest_asymmetry:
        return selftest_asymmetry()

    if args.asymmetry:
        return asymmetry(args.root)

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
                "stationarity_evaluable": rep["stationarity_evaluable"],
                "stationarity_note": rep["stationarity_note"],
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
                  f"{_stat_cell(rep):>6} "
                  f"{rep['rum_95']:11.4g}")

    print()
    print("PER-CHANNEL SUMMARY. Every count below names its channel, because "
          "the SLIDE gate\nand the probabilistic verdict read different ones "
          "and a bare integer hides which.")
    print()
    ch = (f"{'channel':6} {'runs':>5} {'need>8':>7} {'nonstat':>8} "
          f"{'atbound':>8} {'min':>4} {'med':>4} {'max':>4}  what it gates")
    print("'nonstat' counts records the test EVALUATED and rejected. A record "
          "the test could\nnot evaluate is reported on its own WARNING line, "
          "never folded into either column.")
    print(ch)
    print("-" * len(ch))
    for obs in OBSERVABLES:
        head = per_obs[obs]
        if not head:
            continue
        needs = sorted(r["recommended_discard"] for r in head)
        worse = sum(1 for r in head if r["exceeds_driver"])
        # `is False` deliberately, NOT `not r[...]`. None means the test could
        # not be evaluated on that record, and a truthiness check would bucket
        # it as non-stationary, which is a verdict the data does not support.
        nonstat = sum(1 for r in head if r["stationary_at_5pct"] is False)
        unevl = sum(1 for r in head if r["stationary_at_5pct"] is None)
        bound = sum(1 for r in head if r["at_mser_bound"])
        if unevl:
            print(f"  WARNING: {unevl} of {len(head)} {obs} records could NOT be "
                  f"evaluated for stationarity; they are counted separately and "
                  f"are NOT included in the nonstat column.")
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
          "rule to both cases gives a wrong answer in one of them.\n"
          "\nMeasured on the 24 local runs, `--asymmetry` prints the working:\n"
          "  wrong rule on a verdict     16 of 24 verdicts change on the "
          "magnitude channel,\n"
          "                              14 of 24 on the surge channel. All 30 "
          "moves DELETE\n"
          "                              a SLIDE and none creates one, so the "
          "error reads as a\n"
          "                              cleaner analysis rather than as a "
          "mistake.\n"
          "  wrong rule on an error bar  24 of 24 too small, median 4.32x, "
          "worst 5.64x,\n"
          "                              because 91 frames carry a median "
          "N_eff of 5.")

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
