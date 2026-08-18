#!/usr/bin/env python3
"""
inflow_vehicle_tables.py  --  emit the markdown tables the write-up quotes, computed
rather than typed.

WHY THIS EXISTS. analysis/r6_repeat_stats.py:8-11 records the project's own experience:
"every hand-derived figure has been wrong at least once and every figure recomputed inside
a checked script that printed its enumeration has been right". So no number in
docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md is transcribed by hand. This script reads the
JSON written by analysis/inflow_vehicle_stats.py --json and prints the tables verbatim.

Usage
  /opt/homebrew/bin/uv run --with numpy python3 analysis/inflow_vehicle_tables.py \
      --json <runs.json> [--npz <bundle.npz>]
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

# Water-only channel reference, commit be1b138, data/openchannel_2026-08-18/results.json,
# read from that blob rather than retyped from the commit message. Same grid, same
# grid_lim, same nominal depth and velocity as the vehicle scene, no vehicle.
CHANNEL = {
    "closed_g64": {"slope": 0.09268156864666216, "rum95": 0.0016066260963303566,
                   "drained": 2, "leaked": 111779},
    "recycle_g64": {"slope": -0.00283669, "rum95": 0.00029392,
                    "drained": 0, "leaked": 346680},
}
TAN3 = 0.05240777928304121   # tan(3 deg), a 3 degree road
TAN1 = 0.017455064928217585  # tan(1 deg)

ARM_ORDER = ("bare", "closed", "recycle", "recycnb")
ARM_LABEL = {"bare": "bare (unwrapped driver)", "closed": "closed (wrapped control)",
             "recycle": "recycle", "recycnb": "recycle, no inflow band"}


def ms(vals, fmt="%.5f", sd_fmt="%.5f"):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    if not v:
        return "-"
    if len(v) == 1:
        return fmt % v[0]
    return ("%s +/- %s" % (fmt, sd_fmt)) % (statistics.mean(v), statistics.stdev(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--npz", default=None)
    a = ap.parse_args()
    doc = json.loads(Path(a.json).read_text())
    rows = doc["rows"]
    by = defaultdict(list)
    for r in rows:
        by[(r["config"], r["arm"])].append(r)
    configs = sorted({r["config"] for r in rows})

    def group(cfg, arm):
        return by.get((cfg, arm), [])

    print("### T1. Wrapper inertness: the unwrapped driver against the wrapped control\n")
    print("| config | quantity | bare, N=1 | closed wrapped, N | bare inside closed range |")
    print("|---|---|---|---|---|")
    for cfg in configs:
        b, c = group(cfg, "bare"), group(cfg, "closed")
        if not b or not c:
            continue
        for f, fmt in (("final_disp_mag_m", "%.6f"), ("local_depth_bow_peak", "%.6f"),
                       ("passthrough_max_frac", "%.6f"),
                       ("leaked_particle_frames", "%.0f"), ("n_water", "%.0f")):
            cv = [x[f] for x in c]
            bv = float(b[0][f])
            inside = "yes" if min(cv) <= bv <= max(cv) else "NO"
            print("| %s | `%s` | %s | %s (N=%d, range %s to %s) | %s |"
                  % (cfg, f, fmt % bv, ms(cv, fmt, fmt), len(cv),
                     fmt % min(cv), fmt % max(cv), inside))
    print()

    print("### T2. Verdicts. Tallied, never meaned.\n")
    print("| config | arm | N | verdict at metrics row 90 (canonical horizon) | "
          "verdict at metrics row 250 |")
    print("|---|---|---|---|---|")
    for cfg in configs:
        for arm in ARM_ORDER:
            rs = group(cfg, arm)
            if not rs:
                continue
            t90, tend = defaultdict(int), defaultdict(int)
            for r in rs:
                t90[r["verdict_h90"]] += 1
                tend[r["verdict_hend"]] += 1
            f = lambda t: ", ".join("%d %s" % (v, k) for k, v in sorted(t.items()))
            print("| %s | %s | %d | %s | %s |" % (cfg, ARM_LABEL[arm], len(rs),
                                                  f(t90), f(tend)))
    print()

    print("### T3. Free-surface slope, m/m. Positive means water piled downstream.\n")
    print("| config | arm | rows 60-89 (pre) | rows 120-149 | rows 220-249 | "
          "drained bins of 12, rows 60-89 |")
    print("|---|---|---|---|---|---|")
    for cfg in configs:
        for arm in ARM_ORDER:
            rs = [r for r in group(cfg, arm) if "slope_pre_reflection_f60_89" in r]
            if not rs:
                continue
            print("| %s | %s | %s | %s | %s | %s |"
                  % (cfg, ARM_LABEL[arm],
                     ms([r["slope_pre_reflection_f60_89"] for r in rs], "%+.5f"),
                     ms([r.get("slope_post_reflection_f120_149") for r in rs], "%+.5f"),
                     ms([r.get("slope_late_f220_249") for r in rs], "%+.5f"),
                     sorted({r["drained_pre_reflection_f60_89"] for r in rs})))
    print()
    print("Water-only channel at the same grid, grid_lim, depth and velocity, no vehicle "
          "(commit `be1b138`): closed %+.5f +/- %.5f, %d of 12 bins drained; "
          "recycle %+.5f +/- %.5f, %d of 12 drained. A 3 degree road is tan(3 deg) = "
          "%.5f m/m; a 1 degree road is %.5f."
          % (CHANNEL["closed_g64"]["slope"], CHANNEL["closed_g64"]["rum95"],
             CHANNEL["closed_g64"]["drained"], CHANNEL["recycle_g64"]["slope"],
             CHANNEL["recycle_g64"]["rum95"], CHANNEL["recycle_g64"]["drained"],
             TAN3, TAN1))
    print()

    print("### T4. Vehicle motion, with the row window named beside every magnitude.\n")
    print("| config | arm | dmag at row 90, m | dmag at row 250, m | row250 / row90 | "
          "bow depth peak, m | bow peak row |")
    print("|---|---|---|---|---|---|---|")
    for cfg in configs:
        for arm in ARM_ORDER:
            rs = group(cfg, arm)
            if not rs:
                continue
            r90 = [r["dmag_h90"] for r in rs]
            rend = [r["dmag_hend"] for r in rs]
            ratio = [b / a2 for a2, b in zip(r90, rend) if a2]
            print("| %s | %s | %s | %s | %s | %s | %s |"
                  % (cfg, ARM_LABEL[arm], ms(r90, "%.4f", "%.4f"),
                     ms(rend, "%.4f", "%.4f"), ms(ratio, "%.3f", "%.3f"),
                     ms([r["local_depth_bow_peak"] for r in rs], "%.4f", "%.4f"),
                     ms([float(r["local_depth_bow_peak_frame"]) for r in rs],
                        "%.0f", "%.0f")))
    print()

    print("### T5. Water budget, percent of water outside the canonical box at the last "
          "frame.\n")
    print("Measured pre-clamp against the SAME reference box in both arms, so the columns "
          "are commensurable even though the recycle arm no longer walls the x faces.\n")
    print("| config | arm | below floor, % | outside y walls, % | outside x band, % | "
          "deepest floor penetration, m |")
    print("|---|---|---|---|---|---|")
    for cfg in configs:
        for arm in ARM_ORDER:
            rs = [r for r in group(cfg, arm) if "pct_n_below_floor" in r]
            if not rs:
                continue
            print("| %s | %s | %s | %s | %s | %s |"
                  % (cfg, ARM_LABEL[arm],
                     ms([r["pct_n_below_floor"] for r in rs], "%.3f", "%.3f"),
                     ms([r["pct_n_out_ylo"] + r["pct_n_out_yhi"] for r in rs], "%.3f", "%.3f"),
                     ms([r["pct_n_out_xlo"] + r["pct_n_out_xhi"] for r in rs], "%.4f", "%.4f"),
                     ms([r["floor_penetration_final_m"] for r in rs], "%.4f", "%.4f")))
    print()

    print("### T6. Recycling and how far the recirculation reaches.\n")
    print("| config | arm | particles recycled, total | fraction ever recycled by row 250 "
          "| first row a recycled particle is inside the vehicle window | largest "
          "single-tick overshoot, m |")
    print("|---|---|---|---|---|---|")
    for cfg in configs:
        for arm in ("recycle", "recycnb"):
            rs = [r for r in group(cfg, arm) if r.get("recycled_total")]
            if not rs:
                continue
            print("| %s | %s | %s | %s | %s | %s |"
                  % (cfg, ARM_LABEL[arm],
                     ms([float(r["recycled_total"]) for r in rs], "%.0f", "%.0f"),
                     ms([r["tagged_frac_final"] for r in rs], "%.3f", "%.3f"),
                     sorted(r["first_tagged_near_vehicle_frame"] for r in rs),
                     ms([r["max_overshoot_m"] for r in rs], "%.4f", "%.4f")))
    print()

    if a.npz:
        z = np.load(a.npz)
        print("### T7. Free-surface slope as a time series, fitted at every profile row.\n")
        print("| config | arm | slope at row 89 | at row 149 | at row 249 | max over the "
              "record | first sustained sign reversal |")
        print("|---|---|---|---|---|---|---|")
        for cfg in configs:
            for arm in ARM_ORDER:
                rs = group(cfg, arm)
                series = []
                for r in rs:
                    kd, kc = "%s|depth_profile" % r["run"], "%s|bin_centres" % r["run"]
                    if kd not in z:
                        continue
                    prof = np.asarray(z[kd], dtype=float)
                    cen = np.asarray(z[kc], dtype=float)
                    sl = np.full(prof.shape[0], np.nan)
                    for i in range(prof.shape[0]):
                        fin = np.isfinite(prof[i])
                        if fin.sum() >= 3:
                            sl[i] = float(np.polyfit(cen[fin], prof[i][fin], 1)[0])
                    series.append(sl)
                if not series:
                    continue
                def rev(sl):
                    ref = None
                    for i in range(40, len(sl)):
                        if not np.isfinite(sl[i]):
                            continue
                        if ref is None:
                            ref = np.sign(sl[i]); continue
                        if np.sign(sl[i]) != ref and ref != 0:
                            seg = sl[i:i + 5]; seg = seg[np.isfinite(seg)]
                            if len(seg) >= 3 and np.all(np.sign(seg) != ref):
                                return i
                    return None
                print("| %s | %s | %s | %s | %s | %s | %s |"
                      % (cfg, ARM_LABEL[arm],
                         ms([s[89] for s in series if len(s) > 89], "%+.5f", "%.5f"),
                         ms([s[149] for s in series if len(s) > 149], "%+.5f", "%.5f"),
                         ms([s[249] for s in series if len(s) > 249], "%+.5f", "%.5f"),
                         ms([float(np.nanmax(s)) for s in series], "%+.5f", "%.5f"),
                         sorted(x for x in (rev(s) for s in series) if x is not None)
                         or "none"))
        print()


if __name__ == "__main__":
    main()
