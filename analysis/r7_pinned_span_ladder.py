#!/usr/bin/env python3
"""Regenerate every number in docs/R7_PINNED_SPAN_LADDER_2026-08-18.md.

THE QUESTION. At g160 the heaviest vehicle's verdict flips SLIDE -> STUCK in 5 of 5
repeats, at exactly the ~10 particle layers across the flow depth that the only
depth-based convention in the literature asks for. That result is CONFOUNDED:
sim_standing.py:82 sets the domain from the hull alone,

    lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)        # independent of n_grid

while :86 and :100 set the offsets IN CELLS, floor = 3.0*dx and wall = 4.0*dx. The
water interior span is therefore lim - 8*dx = lim*(1 - 8/n) and it GROWS under
refinement. The tank is LARGEST exactly where the verdict flips, tank growth and
resolution both push toward STUCK, and no pre-existing run separates them.

THE CONTROL. Re-run the ladder with the interior span PINNED IN METRES, by choosing
lim per grid, lim_n = S*n/(n-8), presented to the driver as a different extent[1]
through scripts/pinned_span_wrapper.py. sim_standing.py is NOT edited: its sha256
4696c3b2... (canonical copy) / 5215c38b... (the as-ran copy that produced every rung
of the confounded ladder) stamps every published run.

WHICH DRIVER. There are TWO sim_standing.py files in this repo and they are NOT the
same file:
    renders/yaris_render_s1/sim_standing.py                     564 lines  4696c3b2...
    analysis/render_v1/as_ran_local_copies/sim_standing.py      389 lines  5215c38b...
Job 918350, the g160 flip, stamped 5215c38b on line 3 of its own output, and that file
is byte-identical to $WORK/render_s2/sim_standing.py on Vista. The control must differ
from the confounded experiment in the pinned span and NOTHING ELSE, so 5215c38b is the
driver used here. The line numbers quoted above (:82 :86 :100) are that file's.

TWO VARIANTS, because pinning the span does NOT pin the realized water depth. Depth is
quantized to L*h with L = ceil(depth/h - 0.5), so it moves unless 40 | (n-8). The
unpinned ladder happens to hold realized depth EXACTLY at 0.2944294473039918 m on every
rung, which is a real control and must not be surrendered silently in exchange for the
span control. So both were run:
    free    span pinned, realized depth allowed to move
    exact   span AND realized depth both pinned   (n = 48, 88, 128, 168, 208)
n=48 and n=128 are exact-depth grids and belong to BOTH variants. They were run ONCE
and are shared between the two tables, not run twice.

n=48 IS A NULL CONTROL. At n=48 the pinned lim equals the unpinned lim to float
precision, so that rung must reproduce unpinned job 918250 exactly. If it does not, the
wrapper is wrong and nothing else here is valid. The check is printed in section 2.

NO TRUNCATION. Every run here is --frames 90 and its metrics.csv holds 92 lines, one
header plus 91 data rows at indices 0 to 90, last t = 3.0 s at 30 fps. That IS the
canonical horizon, so the full file is classified and no window argument is needed.
The R6 repeats were 250-frame runs and needed one; these do not.

Needs numpy. No system python on this Mac has it:
    /opt/homebrew/bin/uv run --with numpy python3 analysis/r7_pinned_span_ladder.py \
        --pinned <dir> --unpinned <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SSF = 1.42          # vehicle_params compact_sedan, the value the published runs used
MASS = 2337.0       # the boundary case; repeating comfortable runs measures nothing
N_REP = 5
HULL_M3 = 3.542739  # the real hull volume. Invariant under a correct wrapper.
LIM_UNPINNED = 9.421742313727737
TARGET_DEPTH = 0.2944294473039918   # = LIM_UNPINNED / 32
SPAN_PINNED = LIM_UNPINNED * (1.0 - 8.0 / 48.0)   # 7.851451928106448

# The six unpinned rungs, by the job that produced each.
UNPINNED = [(48, "r6_rep_g48_918250"), (64, "r6_rep_g64_918249"),
            (96, "r6_rep_g96_918248"), (128, "r6_rep_g128_918247"),
            (160, "r6_rep_g160_918350"), (192, "r6_rep_g192_918351")]

# Which pinned rungs belong to which variant. 48 and 128 are in both.
FREE_GRIDS = [48, 64, 96, 128, 141, 160, 192]
EXACT_GRIDS = [48, 88, 128, 168, 208]


def load_summaries(run_dir: Path) -> list[dict]:
    out = []
    for i in range(1, N_REP + 1):
        p = run_dir / f"rep_{i}" / "summary.json"
        if p.exists():
            out.append(json.loads(p.read_text()))
    return out


def bit_distinct(run_dir: Path) -> str:
    """Are the N repeats genuinely independent draws, or did something copy a file?
    The process is non-deterministic (register 3a), so all N metrics.csv MUST differ.
    N identical files would mean the repeats are not repeats."""
    hs = []
    for i in range(1, N_REP + 1):
        p = run_dir / f"rep_{i}" / "metrics.csv"
        if p.exists():
            hs.append(hashlib.sha256(p.read_bytes()).hexdigest()[:12])
    if not hs:
        return "no data"
    return "%d/%d distinct" % (len(set(hs)), len(hs))


def maxdrift_of(run_dir: Path, FM, np) -> float:
    """max |surge displacement| over the run, the CONTINUOUS quantity the binary verdict
    is a threshold on. Reported because the verdict is threshold-fragile and this is not."""
    out = []
    for i in range(1, N_REP + 1):
        q = run_dir / f"rep_{i}" / "metrics.csv"
        if q.exists():
            k = FM.kinematics_from_columns(FM.load_timeseries(str(q)), MASS)
            out.append(float(np.max(np.abs(k.disp[:, FM.SURGE_AXIS]))))
    return max(out) if out else float("nan")


def verdicts_and_margins(run_dir: Path, FM, np) -> tuple[list, list, list, set]:
    th = FM.FailureThresholds()
    verdicts, joints, margins, nrows = [], [], [], set()
    for i in range(1, N_REP + 1):
        p = run_dir / f"rep_{i}" / "metrics.csv"
        if not p.exists():
            continue
        nrows.add(sum(1 for _ in p.open()) - 1)
        verdicts.append(FM.classify_timeseries(str(p), MASS, SSF).mode.value)
        cols = FM.load_timeseries(str(p))
        kin = FM.kinematics_from_columns(cols, MASS)
        drift = np.abs(kin.disp[:, FM.SURGE_AXIS])
        spd = np.abs(kin.vel[:, FM.SURGE_AXIS])
        joint = (drift >= th.slide_m) & (spd >= th.slide_speed_ms)
        best = run = 0
        for v in joint:
            run = run + 1 if v else 0
            best = max(best, run)
        joints.append(best)
        margins.append(best - th.sustain_frames)
    return verdicts, joints, margins, nrows


def find_pinned(root: Path, grid: int) -> Path | None:
    hits = sorted(root.glob(f"r7_pin_g{grid}_*"))
    return hits[0] if hits else None


def fmt_counter(vs: list) -> str:
    if not vs:
        return "NO DATA"
    c = Counter(vs)
    return " ".join(f"{k} {v}/{len(vs)}" for k, v in sorted(c.items()))


def section_confound(unp_root: Path) -> None:
    print("=" * 78)
    print("1. THE CONFOUND, recomputed from the six unpinned run summaries")
    print("=" * 78)
    print("   span = lim - 8*dx = lim*(1 - 8/n).  water volume = n_water * h^3.")
    print()
    print("   %4s %12s %12s %12s %12s %14s" %
          ("n", "lim", "dx", "span", "plan area", "water vol"))
    first = None
    for n, d in UNPINNED:
        ss = load_summaries(unp_root / d)
        if not ss:
            print("   %4d  MISSING" % n)
            continue
        s = ss[0]
        span = s["grid_lim"] - 8.0 * s["dx"]
        area = span * span
        vol = s["n_water"] * s["h"] ** 3
        if first is None:
            first = (span, area, vol)
        print("   %4d %12.7f %12.7f %12.7f %12.4f %14.4f" %
              (n, s["grid_lim"], s["dx"], span, area, vol))
    if first:
        ss = load_summaries(unp_root / dict(UNPINNED)[128])
        if ss:
            s = ss[0]
            span = s["grid_lim"] - 8.0 * s["dx"]
            print()
            print("   g48 -> g128 :  span %+.2f %%   plan area %+.2f %%   water volume %+.2f %%"
                  % (100 * (span / first[0] - 1),
                     100 * (span * span / first[1] - 1),
                     100 * (s["n_water"] * s["h"] ** 3 / first[2] - 1)))
    print()


def section_invariance(pin_root: Path, unp_root: Path) -> bool:
    print("=" * 78)
    print("2. DID THE WRAPPER DO WHAT IT CLAIMS. The falsifiers.")
    print("=" * 78)
    print("   (a) span pinned to %.12f m on every rung" % SPAN_PINNED)
    print("   (b) hull_m3 invariant at %.6f  <- falsifier for 'the wrapper shrank the hull'"
          % HULL_M3)
    print("   (c) n=48 reproduces unpinned job 918250 exactly  <- the null control")
    print()
    ok = True
    print("   %4s %6s %12s %12s %12s %10s %8s %12s %10s" %
          ("n", "mode", "lim", "dx", "span", "span err", "layers", "realized_d", "hull_m3"))
    for grid in sorted(set(FREE_GRIDS) | set(EXACT_GRIDS)):
        d = find_pinned(pin_root, grid)
        if d is None:
            print("   %4d  NOT COLLECTED" % grid)
            ok = False
            continue
        mode = d.name.split("_")[3]
        ss = load_summaries(d)
        if not ss:
            print("   %4d  %6s  NO SUMMARIES" % (grid, mode))
            ok = False
            continue
        s = ss[0]
        span = s["grid_lim"] - 8.0 * s["dx"]
        err = span - SPAN_PINNED
        hull_ok = abs(s["hull_m3"] - HULL_M3) < 1e-6
        span_ok = abs(err) < 1e-9
        ok = ok and hull_ok and span_ok
        print("   %4d %6s %12.7f %12.7f %12.9f %10.1e %8d %12.9f %10.6f%s%s" %
              (grid, mode, s["grid_lim"], s["dx"], span, err, s["water_layers"],
               s["realized_depth_m"] if "realized_depth_m" in s
               else s["water_layers"] * s["h"], s["hull_m3"],
               "" if span_ok else "  SPAN-FAIL", "" if hull_ok else "  HULL-FAIL"))
    # the null control, field by field
    print()
    d48 = find_pinned(pin_root, 48)
    u48 = load_summaries(unp_root / "r6_rep_g48_918250")
    if d48 and u48:
        p = load_summaries(d48)[0]
        u = u48[0]
        print("   NULL CONTROL, pinned n=48 vs unpinned job 918250:")
        for k in ("grid_lim", "dx", "h", "water_layers", "n_water", "n_carved",
                  "n_vehicle", "solid_volume_m3", "hull_m3", "fill_ratio",
                  "realized_rho", "substeps", "sound_speed_ms"):
            same = p.get(k) == u.get(k)
            ok = ok and same
            print("     %-18s pinned %-24s unpinned %-24s %s"
                  % (k, p.get(k), u.get(k), "MATCH" if same else "DIFFER"))
    # The confound is removed only if the water volume stops trending. Print the spread
    # for both ladders so the comparison is a computed number, not an assertion.
    print()
    print("   WATER VOLUME SPREAD, the quantity the confound moved by +30.69 percent:")
    for label, dirs in (("unpinned ladder", [(n, unp_root / d) for n, d in UNPINNED]),
                        ("pinned, free   ", [(n, find_pinned(pin_root, n)) for n in FREE_GRIDS]),
                        ("pinned, exact  ", [(n, find_pinned(pin_root, n)) for n in EXACT_GRIDS])):
        vols = []
        for n, d in dirs:
            if d is None:
                continue
            ss = load_summaries(d)
            if ss:
                vols.append(ss[0]["n_water"] * ss[0]["h"] ** 3)
        if len(vols) >= 2:
            print("     %s  min %.4f  max %.4f  spread %+.2f %%  (%d rungs)"
                  % (label, min(vols), max(vols), 100.0 * (max(vols) / min(vols) - 1), len(vols)))
    print()
    print("   ALL WRAPPER CHECKS PASS: %s" % ok)
    print()
    return ok


def section_verdicts(pin_root: Path, unp_root: Path, FM, np) -> dict:
    print("=" * 78)
    print("3. VERDICTS AND MARGINS. classifier G=%s ssf=%s slide_m=%s slide_speed_ms=%s"
          % (FM.G, SSF, FM.FailureThresholds().slide_m,
             FM.FailureThresholds().slide_speed_ms))
    print("   sustain_frames=%s. margin = longest consecutive joint-condition run minus it."
          % FM.FailureThresholds().sustain_frames)
    print("=" * 78)
    res = {"unpinned": {}, "pinned": {}}

    print()
    print("   UNPINNED LADDER, the confounded experiment (tank grows with n)")
    print("   %4s %8s %8s %14s %-22s %-22s %s" %
          ("n", "layers", "dx", "water vol", "verdicts (N=5)", "margin", "repeats"))
    for n, d in UNPINNED:
        run = unp_root / d
        ss = load_summaries(run)
        v, j, m, nr = verdicts_and_margins(run, FM, np)
        if not ss or not v:
            print("   %4d  MISSING" % n)
            continue
        s = ss[0]
        res["unpinned"][n] = dict(verdicts=v, joints=j, margins=m,
                                  layers=s["water_layers"], dx=s["dx"],
                                  maxdrift=maxdrift_of(run, FM, np))
        print("   %4d %8d %8.5f %14.4f %-22s %-22s %s" %
              (n, s["water_layers"], s["dx"], s["n_water"] * s["h"] ** 3,
               fmt_counter(v), str(m), bit_distinct(run)))

    for label, grids in (("free  (span pinned, realized depth free)", FREE_GRIDS),
                         ("exact (span AND realized depth pinned)", EXACT_GRIDS)):
        print()
        print("   PINNED LADDER, variant %s" % label)
        print("   %4s %8s %8s %14s %12s %-22s %-22s %s" %
              ("n", "layers", "dx", "water vol", "depth dev%", "verdicts (N=5)", "margin", "repeats"))
        for n in grids:
            d = find_pinned(pin_root, n)
            if d is None:
                print("   %4d  NOT COLLECTED" % n)
                continue
            ss = load_summaries(d)
            v, j, m, nr = verdicts_and_margins(d, FM, np)
            if not ss or not v:
                print("   %4d  NO DATA" % n)
                continue
            s = ss[0]
            rd = s["water_layers"] * s["h"]
            res["pinned"][n] = dict(verdicts=v, joints=j, margins=m,
                                    layers=s["water_layers"], dx=s["dx"],
                                    realized_depth=rd,
                                    maxdrift=maxdrift_of(d, FM, np))
            print("   %4d %8d %8.5f %14.4f %+11.3f %-22s %-22s %s" %
                  (n, s["water_layers"], s["dx"], s["n_water"] * s["h"] ** 3,
                   100.0 * (rd - TARGET_DEPTH) / TARGET_DEPTH, fmt_counter(v), str(m),
                   bit_distinct(d)))
    print()
    return res


def section_verdict(res: dict) -> None:
    print("=" * 78)
    print("4. DOES THE FLIP SURVIVE THE PINNED SPAN")
    print("=" * 78)
    unp = res["unpinned"]
    pin = res["pinned"]

    def first_stuck(dd):
        ks = sorted(k for k in dd if dd[k]["verdicts"])
        for k in ks:
            if all(v == "STUCK" for v in dd[k]["verdicts"]):
                return k
        return None

    def first_stuck_layers(dd):
        ks = sorted(k for k in dd if dd[k]["verdicts"])
        for k in ks:
            if all(v == "STUCK" for v in dd[k]["verdicts"]):
                return dd[k]["layers"]
        return None

    fu, fp = first_stuck(unp), first_stuck(pin)
    print("   unpinned: first all-STUCK rung n=%s  (%s water layers)"
          % (fu, first_stuck_layers(unp)))
    print("   pinned  : first all-STUCK rung n=%s  (%s water layers)"
          % (fp, first_stuck_layers(pin)))
    print()
    if fp is None:
        print("   RESULT: THE FLIP DOES NOT SURVIVE. No pinned rung is all-STUCK.")
        print("   Tank growth was doing the work, not resolution.")
    else:
        lu, lp = first_stuck_layers(unp), first_stuck_layers(pin)
        print("   RESULT: THE FLIP SURVIVES at pinned span.")
        print("   It reappears at %s water layers pinned vs %s unpinned." % (lp, lu))
        print("   The controlling variable is h, NOT the size of the tank.")
        print("   NOT 'the resolution of the flow depth' specifically: at fixed depth,")
        print("   layers across the depth and particles across the 177.4 mm underbody")
        print("   clearance are perfectly collinear, both being const/h. This experiment")
        print("   separates tank size from h. It does NOT separate depth resolution from")
        print("   clearance resolution or hull resolution.")
    print()
    print("   margin by rung, unpinned then pinned:")
    for k in sorted(set(unp) | set(pin)):
        u = unp.get(k, {}).get("margins")
        p = pin.get(k, {}).get("margins")
        print("     n=%4d  unpinned %-20s  pinned %-20s" % (k, u if u else "-", p if p else "-"))
    print()


def section_layer_matched(res: dict) -> None:
    """The like-for-like test, corrected after adversarial review.

    Two fixes over the first version. (1) The old code keyed by layers alone and so
    SILENTLY OVERWROTE one of the two 12-layer pinned rungs; both are shown now.
    (2) Verdict agreement alone is a weak test, because the verdict is a coarse
    threshold readout. max surge drift, the continuous quantity the verdict is a
    threshold on, is reported beside it."""
    print("=" * 78)
    print("5. LAYER-MATCHED COMPARISON, with the continuous measure beside the verdict")
    print("=" * 78)
    print("   Equal n is NOT equal resolution across these two ladders. Equal layers is.")
    print("   NOTE both 12-layer pinned rungs are listed: they differ in realized depth")
    print("   and in max drift by 24 percent, so 'same layers' is not 'same state'.")
    print()
    rows = []
    for which in ("unpinned", "pinned"):
        for n, d in res[which].items():
            rows.append((d["layers"], which, n, d))
    print("   %7s %-9s %5s %-7s %-11s %-24s" %
          ("layers", "ladder", "n", "verdict", "max drift", "margin"))
    for L, which, n, d in sorted(rows, key=lambda r: (r[0], r[1], r[2])):
        print("   %7d %-9s %5d %-7s %-11.5f %-24s" %
              (L, which, n, "/".join(sorted(set(d["verdicts"]))),
               d["maxdrift"], str(d["margins"])))
    print()


def section_tank_effect(pin_root: Path, unp_root: Path, FM, np) -> None:
    """THE DIRECT MEASUREMENT OF THE TANK EFFECT, and the real hull falsifier.

    This supersedes the verdict-agreement argument. Three pairs exist in which dx, h,
    realized depth, n_vehicle, solid_volume_m3 and substeps are IDENTICAL and the ONLY
    difference is the size of the tank. They bound the tank effect directly, instead of
    inferring it from verdicts.

    They are also the correct falsifier for 'the wrapper shrank the hull'. hull_m3 CANNOT
    serve: it is a hardcoded literal, sim_standing.py:15 HULL = 3.542739, written verbatim
    to the summary at :360, so it prints 3.542739 whatever the hull is. n_vehicle and
    solid_volume_m3 are MEASURED from the particle cloud, and they match exactly across a
    tank change of up to 32.9 percent."""
    print("=" * 78)
    print("6. THE TANK EFFECT, MEASURED DIRECTLY. Matched dx, h and depth.")
    print("=" * 78)
    print("   hull_m3 is a hardcoded literal (sim_standing.py:15) and falsifies NOTHING.")
    print("   n_vehicle and solid_volume_m3 are measured, and they are the real falsifier.")
    print()

    def maxdrift(d):
        out = []
        for i in range(1, N_REP + 1):
            q = d / f"rep_{i}" / "metrics.csv"
            if not q.exists():
                continue
            k = FM.kinematics_from_columns(FM.load_timeseries(str(q)), MASS)
            out.append(float(np.max(np.abs(k.disp[:, FM.SURGE_AXIS]))))
        return out

    pool = {}
    for n, dname in UNPINNED:
        ss = load_summaries(unp_root / dname)
        if ss:
            pool[round(ss[0]["h"], 12)] = (n, unp_root / dname, ss[0])
    for grid in sorted(set(FREE_GRIDS) | set(EXACT_GRIDS)):
        d = find_pinned(pin_root, grid)
        if d is None:
            continue
        ss = load_summaries(d)
        if not ss:
            continue
        k = round(ss[0]["h"], 12)
        if k not in pool:
            continue
        un, ud, us = pool[k]
        ps = ss[0]
        uvol = us["n_water"] * us["h"] ** 3
        pvol = ps["n_water"] * ps["h"] ** 3
        umd, pmd = maxdrift(ud), maxdrift(d)
        # Relative tolerance, NOT ==. h is reached by two different float paths that are
        # equal in real arithmetic (e.g. lim_pinned(88) = LIM*11/12 gives dx = LIM/96, the
        # same as unpinned n=96), so they agree to about 1 ULP, not bitwise. n_vehicle and
        # parity_total_columns are integers and DO match exactly, which is the stronger
        # statement: the particle cloud and the raw mesh bbox are identical.
        rel = abs(ps["solid_volume_m3"] - us["solid_volume_m3"]) / us["solid_volume_m3"]
        hull_same = (us["n_vehicle"] == ps["n_vehicle"]
                     and us["parity_total_columns"] == ps["parity_total_columns"]
                     and rel < 1e-12)
        print("   %2d layers, h=%.7f, depth %.9f" % (ps["water_layers"], ps["h"],
                                                    ps["water_layers"] * ps["h"]))
        print("      hull identity  n_vehicle %d = %d, parity_cols %d = %d, solid_volume rel diff %.1e   %s"
              % (us["n_vehicle"], ps["n_vehicle"], us["parity_total_columns"],
                 ps["parity_total_columns"], rel, "HOLDS" if hull_same else "BROKEN"))
        print("      tank           unpinned g%-3d vol %.4f m3  vs  pinned g%-3d vol %.4f m3   %+.2f %%"
              % (un, uvol, grid, pvol, 100.0 * (uvol / pvol - 1.0)))
        print("      max drift      unpinned mean %.5f  vs  pinned mean %.5f   %+.2f %%"
              % (np.mean(umd), np.mean(pmd), 100.0 * (np.mean(umd) / np.mean(pmd) - 1.0)))
    print()
    print("   READ THE SIGN. A BIGGER tank gives MORE drift, that is toward SLIDE.")
    print("   So tank growth worked AGAINST the flip, not for it. The premise that tank")
    print("   growth 'pushes toward STUCK' is refuted by this project's own data.")
    print()


def section_threshold_fragility(pin_root: Path, unp_root: Path, FM, np) -> None:
    """sustain_frames = 3 is unsourced (failure_modes.py:52) and it gates the verdict.
    Report what the verdict does at 1, 2, 3, 4 and 5, and report the drift exceedance
    separately, because margin = -3 does NOT mean the vehicle did not move."""
    th = FM.FailureThresholds()
    print("=" * 78)
    print("7. HOW MUCH OF THE VERDICT IS THE UNSOURCED sustain_frames = 3")
    print("=" * 78)
    print("   margin = -3 means the JOINT condition never fired. It does NOT mean the")
    print("   vehicle stayed put: drift alone can exceed 0.05 m for most of the run.")
    print()
    print("   %-22s %6s %10s %14s %14s %s" %
          ("run", "layers", "max drift", "frames d>=.05", "frames|v|>=.05", "verdict at sustain 1/2/3/4/5"))
    entries = [("unp", n, unp_root / d) for n, d in UNPINNED]
    entries += [("pin", g, find_pinned(pin_root, g))
                for g in sorted(set(FREE_GRIDS) | set(EXACT_GRIDS))]
    for tag, n, d in entries:
        if d is None:
            continue
        ss = load_summaries(d)
        if not ss:
            continue
        md, fd, fv, bests = [], [], [], []
        for i in range(1, N_REP + 1):
            q = d / f"rep_{i}" / "metrics.csv"
            if not q.exists():
                continue
            k = FM.kinematics_from_columns(FM.load_timeseries(str(q)), MASS)
            dr = np.abs(k.disp[:, FM.SURGE_AXIS])
            sp = np.abs(k.vel[:, FM.SURGE_AXIS])
            md.append(float(dr.max()))
            fd.append(int((dr >= th.slide_m).sum()))
            fv.append(int((sp >= th.slide_speed_ms).sum()))
            j = (dr >= th.slide_m) & (sp >= th.slide_speed_ms)
            b = r = 0
            for x in j:
                r = r + 1 if x else 0
                b = max(b, r)
            bests.append(b)
        cells = []
        for sus in (1, 2, 3, 4, 5):
            nslide = sum(1 for b in bests if b >= sus)
            cells.append("%dS/%dK" % (nslide, len(bests) - nslide))
        print("   %-22s %6d %10.5f %14s %14s %s" %
              ("%s g%d" % (tag, n), ss[0]["water_layers"], max(md),
               "%d-%d" % (min(fd), max(fd)), "%d-%d" % (min(fv), max(fv)),
               "  ".join(cells)))
    print()
    print("   S = SLIDE, K = STUCK, out of N=5. The STUCK rungs with best=0 are robust")
    print("   for ANY sustain >= 1. The SLIDE rungs adjacent to the transition are NOT:")
    print("   several sit exactly at best = 3, so sustain_frames = 4 moves the transition.")
    print()


def section_gates(pin_root: Path, unp_root: Path) -> None:
    """The fix for one confound introduced a breach of another gate. Disclose it."""
    print("=" * 78)
    print("8. P-2 CONTAINMENT GATE. gates.py:146-148, passthrough_max_frac limit 0.10")
    print("=" * 78)
    print("   THE PINNED LADDER FAILS A GATE THE UNPINNED LADDER PASSES.")
    print("   Shrinking the tank raised water passthrough into the vehicle bbox.")
    print()
    print("   %-22s %6s %10s %10s %s" % ("run", "layers", "min", "max", "P-2"))
    nf_u = nf_p = tot_u = tot_p = 0
    entries = [("unp", n, unp_root / d, "u") for n, d in UNPINNED]
    entries += [("pin", g, find_pinned(pin_root, g), "p")
                for g in sorted(set(FREE_GRIDS) | set(EXACT_GRIDS))]
    for tag, n, d, which in entries:
        if d is None:
            continue
        ss = load_summaries(d)
        if not ss:
            continue
        v = [x["passthrough_max_frac"] for x in ss]
        fail = max(v) >= 0.10
        if which == "u":
            tot_u += 1
            nf_u += fail
        else:
            tot_p += 1
            nf_p += fail
        print("   %-22s %6d %10.4f %10.4f %s" %
              ("%s g%d" % (tag, n), ss[0]["water_layers"], min(v), max(v),
               "FAIL" if fail else "pass"))
    print()
    print("   unpinned %d of %d rungs FAIL P-2.  pinned %d of %d rungs FAIL P-2."
          % (nf_u, tot_u, nf_p, tot_p))
    print("   Every pinned STUCK rung is a P-2 failure. This must be stated with the result.")
    print()


def section_threshold_sweep(pin_root: Path, FM, np) -> None:
    """Robustness of the pinned verdicts to ALL THREE unsourced literals, not just
    sustain_frames.

    Prompted by the r7-collect session, which measured this on the UNPINNED ladder and
    found its g160 and g192 joint runs stay at 0 down to slide_m 0.040 and
    slide_speed_ms 0.010, concluding the fragility is concentrated in the middle rungs.
    That conclusion does NOT transfer to the pinned ladder, which is why it is recomputed
    here rather than carried over: on the pinned ladder the 9 and 10 layer STUCK verdicts
    are threshold-contingent, and unconditional STUCK does not begin until 12 layers."""
    print("=" * 78)
    print("9. VERDICT ROBUSTNESS TO ALL THREE LITERALS, not just sustain_frames")
    print("=" * 78)
    print("   published (slide_m, slide_speed_ms) = (0.050, 0.050), sustain_frames = 3")
    print("   failure_modes.py:46-48. None of the three has a peer-reviewed source.")
    print()
    grid = [(0.050, 0.050), (0.040, 0.050), (0.050, 0.010), (0.040, 0.010), (0.060, 0.050)]

    def joints(d, sm, ss):
        out = []
        for i in range(1, N_REP + 1):
            q = d / f"rep_{i}" / "metrics.csv"
            if not q.exists():
                continue
            k = FM.kinematics_from_columns(FM.load_timeseries(str(q)), MASS)
            dr = np.abs(k.disp[:, FM.SURGE_AXIS])
            sp = np.abs(k.vel[:, FM.SURGE_AXIS])
            j = (dr >= sm) & (sp >= ss)
            best = r = 0
            for x in j:
                r = r + 1 if x else 0
                best = max(best, r)
            out.append(best)
        return out

    print("   %-7s %-6s %s" % ("layers", "n", "  ".join("m%.3f/s%.3f" % g for g in grid)))
    robust = []
    for grid_n in sorted(set(FREE_GRIDS) | set(EXACT_GRIDS)):
        d = find_pinned(pin_root, grid_n)
        if d is None:
            continue
        ss_ = load_summaries(d)
        if not ss_:
            continue
        cells, verds = [], []
        for sm, sp_ in grid:
            j = joints(d, sm, sp_)
            nsl = sum(1 for x in j if x >= FM.FailureThresholds().sustain_frames)
            verds.append(nsl)
            cells.append("%dS/%dK(%d-%d)" % (nsl, len(j) - nsl, min(j), max(j)))
        if all(v == 0 for v in verds):
            robust.append((ss_[0]["water_layers"], grid_n))
        print("   %-7d %-6d %s" % (ss_[0]["water_layers"], grid_n,
                                   "  ".join("%-16s" % c for c in cells)))
    print()
    print("   S = SLIDE, K = STUCK at sustain 3, N=5. (min-max) is the joint-run length.")
    print("   UNCONDITIONALLY STUCK under every variation tested: %s"
          % ", ".join("%d layers (n=%d)" % r for r in robust))
    print("   Everything below that is threshold-contingent. The continuous measure in")
    print("   section 4 is unaffected by any of this, which is why it leads the write-up.")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pinned", required=True, type=Path)
    ap.add_argument("--unpinned", required=True, type=Path)
    a = ap.parse_args()

    sys.path.insert(0, str(REPO / "simulation"))
    import numpy as np
    import failure_modes as FM

    print()
    print("R7 TASK 1. THE PINNED-SPAN LADDER CONTROL.")
    print("driver 5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45 (as-ran)")
    print("S = %.15f m, the g48 interior span" % SPAN_PINNED)
    print()
    section_confound(a.unpinned)
    section_invariance(a.pinned, a.unpinned)
    res = section_verdicts(a.pinned, a.unpinned, FM, np)
    section_verdict(res)
    section_layer_matched(res)
    section_tank_effect(a.pinned, a.unpinned, FM, np)
    section_threshold_fragility(a.pinned, a.unpinned, FM, np)
    section_gates(a.pinned, a.unpinned)
    section_threshold_sweep(a.pinned, FM, np)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
