#!/usr/bin/env python3
"""Compare two run summaries WITHOUT silently skipping fields.

WHY THIS EXISTS. On 2026-08-18 a cross-machine comparison printed "6 of 6
identical" and was nearly reported as a result. It had skipped every float,
because the consolidated artifact `data/openchannel_2026-08-18/results_round2.json`
renames one driver field and drops twenty-five others, and the comparison used
`dict.get(...)`, which returns None for a missing key instead of complaining.
A second attempt then compared genuinely unrelated fields against each other
(`sound_speed_ms` vs `mach_margin`, `substeps` vs `n_grid`).

The lesson is not "be careful". A comparison that skips the quantities most
likely to differ is worse than no comparison, because it returns a PASS. So this
module makes skipping impossible to do quietly: every key in either input lands
in exactly one bucket, the buckets are printed, and an undeclared skip is a
non-zero exit.

MEASURED, 2026-08-18: the raw driver summary carries 46 keys; the consolidated
artifact carries 25, of which 20 are shared. So consolidation retains 43 percent
of the record. Always compare RAW driver output to RAW driver output. If you must
use a consolidated file, ALIASES below is the only mapping that has been checked,
and everything else is a genuine loss, not a rename.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Consolidated-artifact name -> raw driver name. Verified by direct key diff of
# results_round2.json against a raw sim_channel.py summary.json, 2026-08-18.
# This is the ONLY rename found. Do not add to it without re-running that diff.
ALIASES = {"free_surface_slope_m_per_m": "late_depth_slope_m_per_m"}

# Keys that legitimately differ between any two runs and are not physics.
NON_PHYSICS = {"label", "out", "batch"}


def canon(d: dict) -> dict:
    """Rename consolidated keys to their raw driver equivalents."""
    return {ALIASES.get(k, k): v for k, v in d.items()}


def compare(a: dict, b: dict, name_a: str = "A", name_b: str = "B") -> dict:
    a, b = canon(a), canon(b)
    keys = (set(a) | set(b)) - NON_PHYSICS
    shared = sorted(k for k in keys if k in a and k in b)
    only_a = sorted(k for k in keys if k not in b)
    only_b = sorted(k for k in keys if k not in a)

    exact, diff, nonnum = [], [], []
    for k in shared:
        x, y = a[k], b[k]
        if isinstance(x, (int, float)) and not isinstance(x, bool) \
           and isinstance(y, (int, float)) and not isinstance(y, bool):
            rel = 0.0 if x == y else abs(y - x) / max(abs(x), 1e-30)
            (exact if x == y else diff).append((k, x, y, rel))
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y) \
                and all(isinstance(v, (int, float)) for v in x + y):
            rels = [0.0 if p == q else abs(q - p) / max(abs(p), 1e-30)
                    for p, q in zip(x, y)]
            m = max(rels) if rels else 0.0
            (exact if m == 0.0 else diff).append((k + "[]", x[0], y[0], m))
        else:
            nonnum.append((k, x, y, x == y))

    worst = max((r for *_, r in diff), default=0.0)
    return {"shared": shared, "only_a": only_a, "only_b": only_b,
            "exact": exact, "diff": diff, "nonnum": nonnum, "worst": worst,
            "name_a": name_a, "name_b": name_b}


def report(res: dict, allow_missing: bool = False) -> int:
    na, nb = res["name_a"], res["name_b"]
    ncmp = len(res["exact"]) + len(res["diff"])
    print("compared %d numeric fields: %d bit-exact, %d differing"
          % (ncmp, len(res["exact"]), len(res["diff"])))
    print("non-numeric fields compared: %d, all equal = %s"
          % (len(res["nonnum"]), all(s for *_, s in res["nonnum"])))
    if res["diff"]:
        print("\ndiffering (worst first):")
        for k, x, y, r in sorted(res["diff"], key=lambda t: -t[3]):
            print("  %-30s %-22.12g %-22.12g rel %.3e" % (k, x, y, r))
    for k, x, y, same in res["nonnum"]:
        if not same:
            print("  NON-NUMERIC DIFFERS %-18s %s=%r  %s=%r" % (k, na, x, nb, y))
    print("\nworst relative difference: %.3e" % res["worst"])

    missing = res["only_a"] or res["only_b"]
    if missing:
        print("\nUNCOMPARED KEYS. These were NOT checked:")
        for k in res["only_a"]:
            print("   only in %-10s %s" % (na, k))
        for k in res["only_b"]:
            print("   only in %-10s %s" % (nb, k))
        if not allow_missing:
            print("\nFAIL: %d key(s) went uncompared. Re-run with --allow-missing "
                  "ONLY after confirming each is genuinely inapplicable, and say so "
                  "in whatever you write up." % (len(res["only_a"]) + len(res["only_b"])))
            return 2
        print("\n(--allow-missing set: the above were declared inapplicable.)")
    return 0


def _selftest() -> int:
    """The exact trap this module exists to stop, as an assertion."""
    raw  = {"late_depth_slope_m_per_m": -0.00166762, "late_depth_spread_m": 0.06085}
    cons = {"free_surface_slope_m_per_m": -0.00166765}
    r = compare(raw, cons, "raw", "consolidated")
    assert "late_depth_slope_m_per_m" in r["shared"], "alias failed to bind"
    assert r["only_a"] == ["late_depth_spread_m"], \
        "a dropped key must surface as uncompared, not vanish"
    assert report(r, allow_missing=False) == 2, "an undeclared skip must FAIL"
    print("\nselftest OK: the rename binds, and the dropped key fails loudly.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow = "--allow-missing" in sys.argv
    if "--selftest" in sys.argv or not args:
        sys.exit(_selftest())
    if len(args) != 2:
        print(__doc__); sys.exit(1)
    pa, pb = Path(args[0]), Path(args[1])
    res = compare(json.loads(pa.read_text()), json.loads(pb.read_text()),
                  pa.parent.name or pa.stem, pb.parent.name or pb.stem)
    sys.exit(report(res, allow_missing=allow))
