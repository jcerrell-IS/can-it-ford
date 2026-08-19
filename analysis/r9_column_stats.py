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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main([Path(p) for p in sys.argv[1:]])
