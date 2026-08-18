#!/usr/bin/env python3
"""Gate-pass FREQUENCY for the SLIDE condition, and the channel defect it exposed.

WHY THIS EXISTS
---------------
Ledger item 9 (docs/HANDOFF_ROUND_7_2026-08-18.md:616) asks for gate-pass frequency
in place of a persistence-gated pass/fail, because `sustain_frames = 3`
(simulation/failure_modes.py:52) is unsourced and gates the verdicts in both
directions. Building that table surfaced a defect in the committed script that
already reports a frequency, and the defect now leads, because it changes what
every previously quoted frequency means.

THE DEFECT: THE COMMITTED p_move READS A DIFFERENT CHANNEL FROM THE CLASSIFIER
------------------------------------------------------------------------------
The classifier gates on the SURGE COMPONENT:

  simulation/failure_modes.py:18      SURGE_AXIS = 0
  simulation/failure_modes.py:168     surge_drift = np.abs(kin.disp[:, SURGE_AXIS])   -> |dx|
  simulation/failure_modes.py:170     surge_speed = np.abs(kin.vel[:, SURGE_AXIS])    -> |vx|
  simulation/failure_modes.py:181-183 joint mask, comparator >=
  simulation/failure_modes.py:178     driven_downstream = max(|surge_force|) > 0
  simulation/failure_modes.py:195     SLIDE = (sustained joint mask) AND driven_downstream

The committed probabilistic script gates on the 3D MAGNITUDES:

  analysis/probabilistic_verdict.py:244  guards on cols["dmag"], cols["vmag"]
  analysis/probabilistic_verdict.py:247  assess(cols["dmag"], cols["vmag"])
  analysis/probabilistic_verdict.py:146  mask comparator is strict >, not >=

`dmag` and `vmag` are the Euclidean norms of (dx,dy,dz) and (vx,vy,vz); `dx` and
`vx` are the surge components. Since dmag >= |dx| and vmag >= |vx| elementwise, and
the joint mask is monotone increasing in each channel, mask_surge implies
mask_magnitude frame by frame. Therefore

    p_move(magnitude channel) >= p_move(surge channel)      for every run, always.

That is an identity, not an empirical result, so this script CHECKS it on every run
as a self-test. A violation means a bug in this script, not a finding.

The consequence: every p_move number this project has quoted is an UPPER BOUND on
the classifier's own gate, by a margin nobody had measured. This script measures it.

WHAT IT COMPUTES, three variants, one change at a time
-----------------------------------------------------
  A  committed    |  channel dmag, vmag   |  comparator >   |  what the repo quotes today
  B  channel-fix  |  channel |dx|, |vx|   |  comparator >   |  isolates the CHANNEL change
  C  exact        |  channel |dx|, |vx|   |  comparator >=  |  plus driven_downstream:
                                                               reproduces failure_modes.py

A against B is the headline gap and holds the comparator fixed. B against C isolates
the comparator alone and is expected to be nil, since a float landing exactly on
0.05 is measure zero. Reporting both means the gap cannot be attributed to the wrong
cause.

THRESHOLDS, quoted together every time a count is printed
---------------------------------------------------------
  slide_m         = 0.05 m     failure_modes.py:46
  slide_speed_ms  = 0.05 m/s   failure_modes.py:47
  sustain_frames  = 3          failure_modes.py:52   UNSOURCED, and the subject here

CLAUDE.md item 13's unit trap applies: three literals share the numeral 0.05 across
two units at failure_modes.py:46-48. `float_m = 0.05 m` (:48) belongs to the FLOAT
mode and is NOT part of the SLIDE gate. Deduplicate by NAME and UNIT, never by value.

REUSE, NOT REIMPLEMENTATION
---------------------------
`assess`, `episodes` and `wilson_ci` are imported from analysis/probabilistic_verdict.py
and `effective_sample_size` from analysis/stationarity.py, both resolved from --repo so
that the module measured is the committed one and not a worktree copy. The resolved
module path is printed on every run. This script does not edit either file; the
proposed fix ships as a diff in docs/R8_PERSISTENCE_GATE_2026-08-18.md for a human to
apply.

FULL RECORD, NOT A STATIONARY WINDOW
------------------------------------
Per CLAUDE.md "THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA": incipient
motion is an EVENT, not a steady state. Removing the transient drops SLIDE from 21 of
24 runs to 5 of 24. Every number here is on the full record. `assess` already defaults
that way and this script never passes use_stationary_window=True.

DATA LOCATION, a labelled assumption
------------------------------------
--repo defaults to /Users/josie/can-it-ford, the MAIN checkout, because metrics.csv
files are gitignored build artifacts: only 1 of the 37 is physically present inside a
worktree. All access is read only. The root actually used is printed on every run.

Pure standard library. No numpy, no uv.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

DEFAULT_REPO = "/Users/josie/can-it-ford"

# Values as declared in simulation/failure_modes.py:46,47,52.
SLIDE_M = 0.05           # metres,           failure_modes.py:46
SLIDE_SPEED_MS = 0.05    # metres per second, failure_modes.py:47
SUSTAIN_FRAMES = 3       # frames,           failure_modes.py:52, UNSOURCED
FPS = 30.0

TRIPLE = ("slide_m = 0.05 m, slide_speed_ms = 0.05 m/s, "
          "sustain_frames = 3")


# --------------------------------------------------------------------------
# numeric helpers, pure python
# --------------------------------------------------------------------------

def gradient(f, x):
    """numpy.gradient(f, x) with edge_order=1, non-uniform spacing.

    Reproduced rather than imported so this script needs no numpy. Used only to
    rebuild `driven_downstream`, which failure_modes.py:178 forms from
    force = mass * gradient(vel, t).
    """
    n = len(f)
    if n < 2:
        return [0.0] * n
    out = [0.0] * n
    out[0] = (f[1] - f[0]) / (x[1] - x[0])
    out[-1] = (f[-1] - f[-2]) / (x[-1] - x[-2])
    for i in range(1, n - 1):
        hs = x[i] - x[i - 1]
        hd = x[i + 1] - x[i]
        out[i] = (hs * hs * f[i + 1] + (hd * hd - hs * hs) * f[i] - hd * hd * f[i - 1]) \
            / (hs * hd * (hs + hd))
    return out


def joint_mask(d, v, slide_m=SLIDE_M, slide_speed=SLIDE_SPEED_MS, strict=False):
    """The joint drift-and-speed condition. strict=False reproduces the >= at
    failure_modes.py:182; strict=True reproduces the > at probabilistic_verdict.py:146."""
    if strict:
        return [(a > slide_m and b > slide_speed) for a, b in zip(d, v)]
    return [(a >= slide_m and b >= slide_speed) for a, b in zip(d, v)]


def longest_run(mask):
    best = run = 0
    for m in mask:
        run = run + 1 if m else 0
        if run > best:
            best = run
    return best


def frac(mask):
    return (sum(1 for m in mask if m) / len(mask)) if mask else 0.0


# --------------------------------------------------------------------------
# run discovery
# --------------------------------------------------------------------------

def discover(repo):
    """Every metrics.csv under repo/renders and repo/data. Enumerated, not asserted."""
    found = []
    for top in ("renders", "data"):
        base = os.path.join(repo, top)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d != ".claude"]
            if "metrics.csv" in files:
                found.append(os.path.relpath(os.path.join(root, "metrics.csv"), repo))
    found.sort()
    return found


def grid_of(repo, rel):
    """n_grid read from the run's own summary.json where present, else None.

    Data derived, not parsed from the directory name, because two local runs
    (renders/yaris_render_s1/m*) carry no grid marker in their name at all.
    """
    sj = os.path.join(repo, os.path.dirname(rel), "summary.json")
    if os.path.isfile(sj):
        try:
            with open(sj, encoding="utf-8", errors="replace") as fh:
                d = json.load(fh)
            g = d.get("n_grid")
            if g is not None:
                return int(g), "summary.json"
        except (ValueError, OSError):
            pass
    return None, "unavailable"


def family_of(rel):
    if rel.startswith("renders/yaris_render_s1/_incoming/"):
        return "canonical-17"
    if rel.startswith("data/g128_canonical_2026-08-13/"):
        return "g128-batch-A"
    if rel.startswith("data/g128_canonical_repeat/"):
        return "g128-batch-B"
    return "other-local"


def label_of(rel):
    return os.path.dirname(rel).replace("renders/yaris_render_s1/_incoming/", "") \
        .replace("renders/yaris_render_s1/", "s1/") \
        .replace("data/g128_canonical_2026-08-13/", "A:") \
        .replace("data/g128_canonical_repeat/", "B:") \
        .replace("renders/", "")


# --------------------------------------------------------------------------
# per run assessment
# --------------------------------------------------------------------------

def assess_run(repo, rel, mod):
    """Returns a row dict, or a dict with 'excluded' set and the reason."""
    path = os.path.join(repo, rel)
    cols = mod.load_metrics(path)
    have = set(cols)
    need_mag = {"dmag", "vmag"}
    need_surge = {"dx", "vx", "t"}
    missing = sorted((need_mag | need_surge) - have)
    if missing:
        return {"rel": rel, "excluded": True,
                "reason": "missing columns " + ",".join(missing)}

    n = min(len(cols["dmag"]), len(cols["vmag"]), len(cols["dx"]),
            len(cols["vx"]), len(cols["t"]))
    if n < 12:
        return {"rel": rel, "excluded": True,
                "reason": "record too short, %d frames, assess() needs 12" % n}

    dmag = cols["dmag"][:n]
    vmag = cols["vmag"][:n]
    dx = [abs(a) for a in cols["dx"][:n]]
    vx = [abs(a) for a in cols["vx"][:n]]
    t = cols["t"][:n]

    # A and B go through the committed assess(), which supplies p_move, the Wilson
    # CI on EFFECTIVE sample size, N_eff and the activity rate. Only the channel
    # differs between them, so the comparison holds everything else fixed.
    a = mod.assess(dmag, vmag)
    b = mod.assess(dx, vx)

    # C is the classifier reproduced exactly: surge channel, >= comparator, and the
    # driven_downstream guard.
    mask_c = joint_mask(dx, vx, strict=False)
    accel_x = gradient(cols["vx"][:n], t)
    driven = max(abs(z) for z in accel_x) > 0.0
    lr_c = longest_run(mask_c)
    p_c = frac(mask_c)

    row = {
        "rel": rel, "excluded": False,
        "label": label_of(rel), "family": family_of(rel), "frames": n,
        "p_A": a["p_move"], "p_B": b["p_move"], "p_C": p_c,
        "lr_A": a["longest_run_frames"], "lr_B": b["longest_run_frames"], "lr_C": lr_c,
        "neff_B": b["n_eff"], "ci_lo_B": b["p_move_ci_lo"], "ci_hi_B": b["p_move_ci_hi"],
        "act_B": b["activity_rate_per_s"],
        "driven_downstream": driven,
        "dx_abs": dx, "vx_abs": vx,
        "verdict_C_sf3": "SLIDE" if (lr_c >= 3 and driven) else "STUCK",
        "verdict_C_sf4": "SLIDE" if (lr_c >= 4 and driven) else "STUCK",
        "verdict_C_sf5": "SLIDE" if (lr_c >= 5 and driven) else "STUCK",
        "verdict_A_sf3": a["deterministic_verdict"],
    }
    # WHICH CHANNEL CREATES THE GAP. On every frame counted by A but not by B,
    # ask which of the two conditions the surge channel failed. This names the
    # mechanism instead of only sizing the discrepancy. Both conditions are keyed
    # by NAME (slide_m in metres, slide_speed_ms in metres per second), never by
    # their shared numeral, per CLAUDE.md item 13.
    mask_a = joint_mask(dmag, vmag, strict=True)
    mask_b = joint_mask(dx, vx, strict=True)
    only_a = [i for i in range(n) if mask_a[i] and not mask_b[i]]
    row["only_a"] = len(only_a)
    row["only_a_speed"] = sum(1 for i in only_a if dx[i] > SLIDE_M
                              and vx[i] <= SLIDE_SPEED_MS)
    row["only_a_drift"] = sum(1 for i in only_a if vx[i] > SLIDE_SPEED_MS
                              and dx[i] <= SLIDE_M)
    row["only_a_both"] = sum(1 for i in only_a if dx[i] <= SLIDE_M
                             and vx[i] <= SLIDE_SPEED_MS)
    row["max_vx"] = max(vx)
    row["max_vz"] = max(abs(z) for z in cols["vz"][:n]) if "vz" in cols else float("nan")
    row["gap"] = row["p_A"] - row["p_B"]
    if row["p_B"] > 0:
        row["ratio"] = row["p_A"] / row["p_B"]
    elif row["p_A"] > 0:
        row["ratio"] = float("inf")   # surge channel never passes, magnitude channel does
    else:
        row["ratio"] = None           # neither channel ever passes, 0/0 is not inf
    row["identity_ok"] = row["p_A"] >= row["p_B"] - 1e-12
    row["comparator_delta"] = row["p_C"] - row["p_B"]
    g, gsrc = grid_of(repo, rel)
    row["grid"], row["grid_src"] = g, gsrc
    return row


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def pct(x):
    return "%6.2f" % (100.0 * x)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=DEFAULT_REPO,
                    help="repo root holding renders/ and data/ (default: the main checkout)")
    ap.add_argument("--markdown", action="store_true",
                    help="emit the write-up tables as markdown")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    sys.path.insert(0, os.path.join(repo, "analysis"))
    import probabilistic_verdict as mod  # noqa: E402

    print("R8 SLIDE gate-pass frequency, and the channel gap in the committed p_move")
    print("=" * 78)
    print("repo root      %s" % repo)
    print("module wrapped %s" % os.path.abspath(mod.__file__))
    print("thresholds     %s" % TRIPLE)
    print("               full record, no stationary window (incipient motion is an EVENT)")
    print()

    rels = discover(repo)
    print("RUN ENUMERATION, walked from the tree, not asserted")
    print("-" * 78)
    print("metrics.csv found: %d" % len(rels))
    by_family = {}
    for r in rels:
        by_family.setdefault(family_of(r), []).append(r)
    for fam in sorted(by_family):
        print("  %-14s %2d" % (fam, len(by_family[fam])))
    print()

    rows, excluded = [], []
    for rel in rels:
        r = assess_run(repo, rel, mod)
        (excluded if r.get("excluded") else rows).append(r)

    if excluded:
        print("EXCLUDED, with path and reason:")
        for e in excluded:
            print("  %-52s %s" % (e["rel"], e["reason"]))
        print()
    print("classified: %d of %d found" % (len(rows), len(rels)))
    print()

    bad = [r for r in rows if not r["identity_ok"]]
    print("SELF TEST  p_move(magnitude) >= p_move(surge) on every run: %s (%d/%d)"
          % ("HOLDS" if not bad else "VIOLATED, THIS IS A BUG",
             len(rows) - len(bad), len(rows)))
    print()

    # ---- table 1, the gap -------------------------------------------------
    print("TABLE 1  THE CHANNEL GAP, committed p_move against the classifier's own channel")
    print("A = dmag,vmag with >   (analysis/probabilistic_verdict.py:247, what the repo quotes)")
    print("B = |dx|,|vx| with >   (simulation/failure_modes.py:168,170, channel changed only)")
    print("-" * 78)
    h = "%-26s %5s %8s %8s %8s %8s" % ("run", "frm", "p_A %", "p_B %", "gap pp", "A/B")
    print(h)
    print("-" * len(h))
    for r in sorted(rows, key=lambda z: -z["gap"]):
        rat = ("  n/a" if r["ratio"] is None
               else "  inf" if r["ratio"] == float("inf") else "%5.2f" % r["ratio"])
        print("%-26s %5d %8s %8s %8s %8s"
              % (r["label"][:26], r["frames"], pct(r["p_A"]), pct(r["p_B"]),
                 pct(r["gap"]), rat))
    gaps = sorted(r["gap"] for r in rows)
    finite = [r["ratio"] for r in rows if r["ratio"] not in (None, float("inf"))]
    print("-" * len(h))
    print("gap in percentage points: min %.2f  median %.2f  max %.2f  mean %.2f"
          % (100 * gaps[0], 100 * gaps[len(gaps) // 2], 100 * gaps[-1],
             100 * sum(gaps) / len(gaps)))
    if finite:
        fs = sorted(finite)
        print("ratio A/B (finite only, n=%d): min %.3f  median %.3f  max %.3f"
              % (len(fs), fs[0], fs[len(fs) // 2], fs[-1]))
    n_inf = sum(1 for r in rows if r["ratio"] == float("inf"))
    n_na = sum(1 for r in rows if r["ratio"] is None)
    print("runs where the surge channel NEVER passes but the magnitude channel DOES: %d"
          % n_inf)
    print("runs where NEITHER channel ever passes (ratio is 0/0, not inf): %d" % n_na)
    print()

    # ---- mechanism ---------------------------------------------------------
    tot = sum(r["only_a"] for r in rows)
    sp = sum(r["only_a_speed"] for r in rows)
    dr = sum(r["only_a_drift"] for r in rows)
    bo = sum(r["only_a_both"] for r in rows)
    print("MECHANISM  which condition the surge channel fails on the gap frames")
    print("  frames counted by A but not by B, summed over %d runs: %d" % (len(rows), tot))
    if tot:
        print("    surge speed under slide_speed_ms while drift clears slide_m: %4d (%.1f%%)"
              % (sp, 100.0 * sp / tot))
        print("    surge drift under slide_m while speed clears slide_speed_ms: %4d (%.1f%%)"
              % (dr, 100.0 * dr / tot))
        print("    both surge channels under their own named threshold:         %4d (%.1f%%)"
              % (bo, 100.0 * bo / tot))
    nvz = sum(1 for r in rows if r["max_vz"] > r["max_vx"])
    print("  runs where the vertical bob exceeds the surge speed, max|vz| > max|vx|: %d of %d"
          % (nvz, len(rows)))
    print("  those are the runs where vmag is carried over slide_speed_ms by vertical")
    print("  motion, so the committed p_move counts BOBBING as SLIDING.")
    print()

    # ---- comparator control ------------------------------------------------
    cd = [abs(r["comparator_delta"]) for r in rows]
    print("COMPARATOR CONTROL  B (>) against C (>=), channel held fixed at |dx|,|vx|")
    print("  max |p_C - p_B| over %d runs: %.3e percentage points"
          % (len(rows), 100 * max(cd)))
    print("  so the gap in Table 1 is the CHANNEL, not the comparator.")
    print()

    # ---- table 2, the frequency table on the corrected gate ---------------
    print("TABLE 2  GATE-PASS FREQUENCY on the classifier's own gate (variant C)")
    print("         %s" % TRIPLE)
    print("-" * 78)
    h2 = ("%-26s %5s %8s %14s %6s %6s %5s %5s %5s"
          % ("run", "grid", "p_C %", "95% CI (Neff)", "N_eff", "long", "sf3", "sf4", "sf5"))
    print(h2)
    print("-" * len(h2))
    for r in sorted(rows, key=lambda z: (z["grid"] or 0, z["label"])):
        print("%-26s %5s %8s   [%5s,%5s] %6.1f %6d %5s %5s %5s"
              % (r["label"][:26], r["grid"] if r["grid"] else "?", pct(r["p_C"]),
                 pct(r["ci_lo_B"]).strip(), pct(r["ci_hi_B"]).strip(), r["neff_B"],
                 r["lr_C"],
                 "S" if r["verdict_C_sf3"] == "SLIDE" else "K",
                 "S" if r["verdict_C_sf4"] == "SLIDE" else "K",
                 "S" if r["verdict_C_sf5"] == "SLIDE" else "K"))
    print()

    # ---- table 3, per grid -------------------------------------------------
    print("TABLE 3  PER GRID, %s" % TRIPLE)
    print("-" * 78)
    h3 = "%-8s %4s %9s %9s %9s %9s %11s" % ("grid", "n", "p_C min", "p_C med",
                                            "p_C max", "p_A med", "SLIDE sf3/4/5")
    print(h3)
    print("-" * len(h3))
    grids = {}
    for r in rows:
        grids.setdefault(r["grid"], []).append(r)
    for g in sorted(grids, key=lambda z: (z is None, z)):
        gr = grids[g]
        ps = sorted(x["p_C"] for x in gr)
        pa = sorted(x["p_A"] for x in gr)
        s3 = sum(1 for x in gr if x["verdict_C_sf3"] == "SLIDE")
        s4 = sum(1 for x in gr if x["verdict_C_sf4"] == "SLIDE")
        s5 = sum(1 for x in gr if x["verdict_C_sf5"] == "SLIDE")
        print("%-8s %4d %9s %9s %9s %9s   %2d/%2d/%2d of %d"
              % ("g%s" % g if g else "unknown", len(gr), pct(ps[0]),
                 pct(ps[len(ps) // 2]), pct(ps[-1]), pct(pa[len(pa) // 2]),
                 s3, s4, s5, len(gr)))
    print()

    # ---- the published 17 --------------------------------------------------
    canon = [r for r in rows if r["family"] == "canonical-17"]
    print("AGAINST THE PUBLISHED 16 SLIDE / 1 STUCK, %s" % TRIPLE)
    print("-" * 78)
    print("canonical runs reproduced locally: %d" % len(canon))
    for sf, key in ((3, "verdict_C_sf3"), (4, "verdict_C_sf4"), (5, "verdict_C_sf5")):
        s = sum(1 for r in canon if r[key] == "SLIDE")
        print("  sustain_frames = %d  ->  %2d SLIDE / %2d STUCK   (slide_m = 0.05 m, "
              "slide_speed_ms = 0.05 m/s)" % (sf, s, len(canon) - s))
    stuck3 = [r["label"] for r in canon if r["verdict_C_sf3"] == "STUCK"]
    print("  STUCK at sustain_frames = 3: %s" % (", ".join(stuck3) if stuck3 else "none"))
    print("  driven_downstream False anywhere: %d"
          % sum(1 for r in rows if not r["driven_downstream"]))
    print()

    # ---- refuting mechanism -------------------------------------------------
    print("REFUTING MECHANISMS FOR THE FREQUENCY MEASURE")
    print("-" * 78)
    # R1 degeneracy
    deg = sum(1 for r in rows if r["p_C"] <= 0.0 or r["p_C"] >= 1.0)
    print("R1 DEGENERACY. If p_C only ever took the values 0 or 1 it would carry no")
    print("   more information than the binary it replaces.")
    print("   runs at exactly 0 or 1: %d of %d" % (deg, len(rows)))
    # R2 discrimination within a single binary class
    sl = sorted(r["p_C"] for r in canon if r["verdict_C_sf3"] == "SLIDE")
    if sl:
        print("R2 NO DISCRIMINATION. If every run the binary calls SLIDE had the same p_C,")
        print("   frequency would add nothing to the label.")
        print("   canonical SLIDE runs: n=%d  p_C spans %s to %s percent, span %s pp"
              % (len(sl), pct(sl[0]).strip(), pct(sl[-1]).strip(),
                 pct(sl[-1] - sl[0]).strip()))
    # R3 reproducibility across the repeat pairs
    pair = {}
    for r in rows:
        if r["family"] in ("g128-batch-A", "g128-batch-B"):
            pair.setdefault(r["label"].split(":", 1)[1], {})[r["family"]] = r
    print("R3 REPRODUCIBILITY, the one that would actually settle it. The complaint")
    print("   against the binary is that it flips under refinement. If the frequency")
    print("   were LESS reproducible across identical-setting repeats than the binary,")
    print("   the frequency would be the worse measure.")
    if pair:
        print("   %-16s %9s %9s %9s   %s" % ("run", "p_C A %", "p_C B %", "|diff| pp",
                                             "binary agrees?"))
        agree = 0
        diffs = []
        for k in sorted(pair):
            p = pair[k]
            if "g128-batch-A" in p and "g128-batch-B" in p:
                a, b = p["g128-batch-A"], p["g128-batch-B"]
                d = abs(a["p_C"] - b["p_C"])
                diffs.append(d)
                same = a["verdict_C_sf3"] == b["verdict_C_sf3"]
                agree += 1 if same else 0
                print("   %-16s %9s %9s %9s   %s"
                      % (k, pct(a["p_C"]), pct(b["p_C"]), pct(d),
                         "yes (%s)" % a["verdict_C_sf3"] if same
                         else "NO (%s vs %s)" % (a["verdict_C_sf3"], b["verdict_C_sf3"])))
        if diffs:
            ds = sorted(diffs)
            print("   pairs: %d   binary agrees on %d   |diff| in p_C: median %.2f pp, "
                  "max %.2f pp" % (len(ds), agree, 100 * ds[len(ds) // 2], 100 * ds[-1]))
        print()
        print("   R3 POWER. Zero difference is only meaningful if the two batches are")
        print("   distinct data with something for the test to detect. Per pair: the")
        print("   largest frame-wise disagreement in each gated channel, and how many")
        print("   frames sit within that disagreement of the 0.05 threshold, that is")
        print("   how many frames COULD have flipped the count.")
        print("   %-16s %11s %11s %10s" % ("run", "max d|dx| m", "max d|vx| m/s",
                                           "at-risk fr"))
        for k in sorted(pair):
            q = pair[k]
            if "g128-batch-A" not in q or "g128-batch-B" not in q:
                continue
            a, b = q["g128-batch-A"], q["g128-batch-B"]
            m = min(len(a["dx_abs"]), len(b["dx_abs"]))
            dd = max(abs(a["dx_abs"][i] - b["dx_abs"][i]) for i in range(m))
            dv = max(abs(a["vx_abs"][i] - b["vx_abs"][i]) for i in range(m))
            atrisk = sum(1 for i in range(m)
                         if abs(a["dx_abs"][i] - SLIDE_M) <= dd
                         or abs(a["vx_abs"][i] - SLIDE_SPEED_MS) <= dv)
            print("   %-16s %11.3e %11.3e %10d of %d" % (k, dd, dv, atrisk, m))
    else:
        print("   NO REPEAT PAIRS FOUND. R3 cannot be evaluated on this tree.")
    print()

    if args.markdown:
        emit_markdown(rows, canon, excluded, rels, grids, pair)
    return 0


def emit_markdown(rows, canon, excluded, rels, grids, pair):
    print()
    print("<!-- MARKDOWN TABLES, generated by analysis/r8_persistence_frequency.py -->")
    print()
    print("### Table 1. The channel gap")
    print()
    print("| run | frames | p_A (dmag,vmag) % | p_B (\\|dx\\|,\\|vx\\|) % | gap pp | A/B |")
    print("|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda z: -z["gap"]):
        rat = ("n/a" if r["ratio"] is None
               else "inf" if r["ratio"] == float("inf") else "%.2f" % r["ratio"])
        print("| `%s` | %d | %s | %s | %s | %s |"
              % (r["label"], r["frames"], pct(r["p_A"]).strip(), pct(r["p_B"]).strip(),
                 pct(r["gap"]).strip(), rat))
    print()
    print("### Table 2. Gate-pass frequency on the classifier's own gate")
    print()
    print("| run | grid | p_C % | 95% CI on N_eff | N_eff | longest run | sf=3 | sf=4 | sf=5 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda z: (z["grid"] or 0, z["label"])):
        print("| `%s` | %s | %s | [%s, %s] | %.1f | %d | %s | %s | %s |"
              % (r["label"], r["grid"] or "?", pct(r["p_C"]).strip(),
                 pct(r["ci_lo_B"]).strip(), pct(r["ci_hi_B"]).strip(), r["neff_B"],
                 r["lr_C"], r["verdict_C_sf3"], r["verdict_C_sf4"], r["verdict_C_sf5"]))
    print()
    print("### Table 3. Per grid")
    print()
    print("| grid | n | p_C min % | p_C median % | p_C max % | p_A median % | SLIDE at sf=3/4/5 |")
    print("|---|---|---|---|---|---|---|")
    for g in sorted(grids, key=lambda z: (z is None, z)):
        gr = grids[g]
        ps = sorted(x["p_C"] for x in gr)
        pa = sorted(x["p_A"] for x in gr)
        s3 = sum(1 for x in gr if x["verdict_C_sf3"] == "SLIDE")
        s4 = sum(1 for x in gr if x["verdict_C_sf4"] == "SLIDE")
        s5 = sum(1 for x in gr if x["verdict_C_sf5"] == "SLIDE")
        print("| %s | %d | %s | %s | %s | %s | %d/%d/%d of %d |"
              % ("g%s" % g if g else "unknown", len(gr), pct(ps[0]).strip(),
                 pct(ps[len(ps) // 2]).strip(), pct(ps[-1]).strip(),
                 pct(pa[len(pa) // 2]).strip(), s3, s4, s5, len(gr)))
    print()


if __name__ == "__main__":
    raise SystemExit(main())
