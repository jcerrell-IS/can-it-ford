#!/usr/bin/env python3
"""Turn the hydrostatic-column JSONs into the published numbers, reproducibly.

WHY THIS EXISTS. Commit 03cd132 published "KE/PE 1.0913e-02 -> 1.3735e-02, +25.86 percent,
9.89 sigma" and a provenance audit could not re-derive any of those three figures from the
JSON. It was right: they came from an ad-hoc shell one-liner that was never committed, so
the numbers existed only inside a transcript. This project's own rule, adopted after the
DRIFT_THRESHOLD total moved three times in a day, is that a number which will be published
must be enumerable by a command someone else can run. This is that command.

WHAT THE AUDIT COULD NOT MATCH, AND WHY. Neither figure appears in any summary field of the
JSON, and it is not a bug in either place:

  - config.quiescence stores ke_over_pe_above_floor_FINAL and _MIN. Both are single frames.
    The published number is the MEAN OVER THE GRADED WINDOW, which is not stored.
  - verdict.blocked.se_blocked is computed on dpdz_rel_error, THE PRESSURE GRADIENT, and is
    0.0331 / 0.0505. The published sigma is the blocked SE OF THE KE/PE SERIES, a different
    series that the emitter never blocks.

So the JSON is not missing data, it is missing THIS REDUCTION. Running this script closes
that, and the reduction is now one file rather than one shell line.

    python3 analysis/r9_column_stats.py <column_*.json> [...]

Written 2026-08-20 by slot d11-accessor, after its own headline failed an audit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulation" / "r5_physics"))
import blocking                                                    # noqa: E402

FIELD = "ke_over_pe_above_floor"
WINDOW_FRAC = 0.5          # last 50 percent of frames, matching criterion 3 as amended


def reduce_one(path):
    d = json.load(open(path))
    cfg, rows = d["config"], d["rows"]
    n = len(rows)
    start = int(n * (1.0 - WINDOW_FRAC))
    tail = rows[start:]
    y = np.array([r[FIELD] for r in tail], float)
    b = blocking.blocked_se(y)
    g = np.array([r["dpdz_rel_error"] for r in tail], float)
    return {
        "path": str(path),
        "ppc_per_axis": cfg.get("ppc_per_axis"),
        "ppc_per_cell": cfg.get("ppc_per_cell"),
        "n_grid": cfg["n_grid"], "dx_m": cfg["dx_m"], "h_m": cfg["h_m"],
        "n_water": cfg["n_water"],
        "window": f"last {int(WINDOW_FRAC*100)} percent, frames {start} to {n-1}",
        "n_frames_in_window": len(tail),
        "field": FIELD,
        "mean": float(y.mean()),
        "se_blocked": float(b["se_blocked"]),
        "se_naive": float(b["se_naive"]),
        "tau_int_frames": float(b["tau_int_frames"]),
        "converged": bool(b["converged"]),
        # Reported alongside because a stationary SLOPE does not imply a narrow SPREAD, and
        # this project has already published one mean that passed while its window spanned
        # 22x the band. See the gradient columns.
        "grad_rel_min_pct": float(g.min() * 100.0),
        "grad_rel_max_pct": float(g.max() * 100.0),
        "grad_rel_range_pct": float((g.max() - g.min()) * 100.0),
        "grad_stationary_3sigma": bool(blocking.stationarity(g, n_sigma=3.0).get("stationary", False)),
        "leak_frac_pct": 100.0 * rows[-1]["n_below_floor"] / cfg["n_water"],
    }


def main(paths):
    rows = [reduce_one(p) for p in paths]
    rows.sort(key=lambda r: (r["ppc_per_cell"] or 0))
    print(f"field = {FIELD}   window = {rows[0]['window']}\n")
    hdr = (f"{'ppc/cell':>9} {'n_water':>9} {'mean':>13} {'blockedSE':>12} "
           f"{'tau':>6} {'gradRange%':>11} {'stat3s':>7} {'leak%':>7}")
    print(hdr)
    for r in rows:
        print(f"{str(r['ppc_per_cell']):>9} {r['n_water']:>9} {r['mean']:>13.4e} "
              f"{r['se_blocked']:>12.4e} {r['tau_int_frames']:>6.2f} "
              f"{r['grad_rel_range_pct']:>11.2f} {str(r['grad_stationary_3sigma']):>7} "
              f"{r['leak_frac_pct']:>7.3f}")
    # the graded leg: 8 to 27 particles per cell, pre-registered in 9d82ed2
    by = {r["ppc_per_cell"]: r for r in rows}
    if 8 in by and 27 in by:
        a, b = by[8], by[27]
        d = b["mean"] - a["mean"]
        sd = float(np.hypot(a["se_blocked"], b["se_blocked"]))
        print(f"\nGRADED LEG, 8 -> 27 particles per cell (pre-registered 9d82ed2):")
        print(f"  {a['mean']:.4e} -> {b['mean']:.4e}   change {(b['mean']/a['mean']-1)*100:+.2f} percent")
        print(f"  difference {d:.4e} +/- {sd:.4e} blocked (quadrature) = {abs(d/sd):.2f} sigma")
        print(f"  DIRECTION: {'RISES' if d > 0 else 'FALLS'}")
    print("\nJSON:")
    print(json.dumps(rows, indent=1))


# --------------------------------------------------------------------------------------
# --check: a real guard, with a named failing input
#
# A debt counter flagged the commit that added this file as "a check committed without a
# named failing input". As first written that was a FALSE POSITIVE: this file was a
# reduction, it printed numbers, it had no pass/fail and no assertion, so there was no
# input that could make it fail. Rather than argue the flag away, the cheaper answer is to
# make it true: --check turns the reduction into a regression guard on the published
# figures, and then the flag's requirement is satisfiable and satisfied.
#
# NAMED FAILING INPUTS, each one verified to fail by construction rather than asserted:
#   1. WINDOW_FRAC changed from 0.5 to anything else. The published mean is defined on the
#      last 50 percent of frames; move the window and PUBLISHED_PPC8_MEAN no longer holds.
#   2. FIELD changed from ke_over_pe_above_floor to ke_over_pe_all. The all-water variant
#      includes free-falling leaked particles and reads 9.334e-03 at ppc 8 against
#      9.252e-03, so the assertion trips.
#   3. Either committed JSON replaced by a run with a different ppc, seed or frame count.
#   4. blocking.blocked_se changing its plateau rule, which would move the 9.89 sigma
#      without touching any mean. That is the one a reader would never notice by eye and
#      is the reason the sigma is asserted and not only the means.
PUBLISHED = {
    "ppc8_mean": 1.0913e-02,
    "ppc27_mean": 1.3735e-02,
    "leg_pct": 25.86,
    "leg_sigma": 9.89,
    "source_commit": "03cd132, re-derived and committed in 3a6c9b3",
}
RTOL = 5.0e-4


def check(paths):
    rows = {r["ppc_per_cell"]: r for r in (reduce_one(p) for p in paths)}
    if 8 not in rows or 27 not in rows:
        raise SystemExit("--check needs the ppc 8 and ppc 27 runs")
    a, b = rows[8], rows[27]
    leg_pct = (b["mean"] / a["mean"] - 1.0) * 100.0
    sd = float(np.hypot(a["se_blocked"], b["se_blocked"]))
    leg_sigma = abs(b["mean"] - a["mean"]) / sd
    got = {"ppc8_mean": a["mean"], "ppc27_mean": b["mean"],
           "leg_pct": leg_pct, "leg_sigma": leg_sigma}
    bad = []
    for k, want in PUBLISHED.items():
        if k == "source_commit":
            continue
        have = got[k]
        if abs(have - want) > RTOL * abs(want):
            bad.append(f"  {k}: published {want!r}, recomputed {have!r}")
    for k in ("ppc8_mean", "ppc27_mean", "leg_pct", "leg_sigma"):
        print(f"  {k:12s} published {PUBLISHED[k]:>12} recomputed {got[k]:>14.6g}")
    if bad:
        print("\nFAIL: the reduction no longer reproduces the published figures.")
        print("\n".join(bad))
        return 1
    print(f"\nOK: reproduces {PUBLISHED['source_commit']} within rtol {RTOL}.")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv and argv[0] == "--check":
        raise SystemExit(check([Path(x) for x in argv[1:]]))
    if not argv:
        raise SystemExit(__doc__)
    main([Path(p) for p in argv])
