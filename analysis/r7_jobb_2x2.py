#!/usr/bin/env python3
"""Grade the Job B boundary 2x2: engine fix x sacrificial sub-floor.

    engine \ ghost      0                    3
    pinned              918461 sphere_ghost0 918461 sphere_ghost3
    bcfix               918526 bcfix_ghost0  918526 bcfix_ghost3

Job 918450 is deliberately NOT a cell of this design: it ran 200 frames with no SDF
cache, so using it as the bcfix/ghost0 cell would confound the interaction with a
settings change. Pass it as --consistency to check it against 918526's ghost0 arm
instead.

TWO METRICS, AND ONE OF THEM INVERTS IF READ NAIVELY.
  fz_over_analytic_measured is the accessor sphere_heave.py:669-670 designates as the
  number Job B is graded on. Manifest bands: <=10 PASS, 10-25 REPORTABLE PARTIAL,
  >25 FAIL.
  n_below_floor CANNOT be compared raw across a ghost A/B. --ghost-layers N seeds
  particles BELOW the nominal floor, so the column counts a seeding choice, not a leak,
  and the raw comparison reports the fix making leakage WORSE. The comparable quantity
  is crossings during the run, n_below_floor(t) - n_below_floor(0), reported here as a
  fraction of each run's own real (non-ghost) water.

Needs no numpy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BANDS = ((10.0, "PASS"), (25.0, "REPORTABLE PARTIAL"))


def band(pct_err: float) -> str:
    a = abs(pct_err)
    for lim, name in BANDS:
        if a <= lim:
            return name
    return "FAIL"


def load(p):
    return json.loads(Path(p).read_text())


def mean_last(rows, key, w):
    v = [r[key] for r in rows[-w:]]
    return sum(v) / len(v)


def crossed_frac(doc, real_water):
    rows = doc["rows"]
    return (rows[-1]["n_below_floor"] - rows[0]["n_below_floor"]) / real_water


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pinned-ghost0", required=True)
    ap.add_argument("--pinned-ghost3", required=True)
    ap.add_argument("--bcfix-ghost0", required=True)
    ap.add_argument("--bcfix-ghost3", required=True)
    ap.add_argument("--consistency", default=None, help="918450, different settings")
    ap.add_argument("--window", type=int, default=20)
    a = ap.parse_args()

    cells = {
        ("pinned", 0): load(a.pinned_ghost0), ("pinned", 3): load(a.pinned_ghost3),
        ("bcfix", 0): load(a.bcfix_ghost0),   ("bcfix", 3): load(a.bcfix_ghost3),
    }
    W = a.window

    print("=" * 76)
    print("JOB B BOUNDARY 2x2   metric: fz_over_analytic_measured, mean of last %d" % W)
    print("=" * 76)

    print("\n0. COMPARABILITY. All four cells must match except engine and ghost layers.")
    print("   A key ABSENT from every config is reported NOT CHECKED, never OK: an")
    print("   all-None comparison is a check that cannot fail. The `lim` key was exactly")
    print("   that mistake, the real key is `lim_m`.")
    ref = cells[("pinned", 0)]["config"]
    MUST_MATCH = ("n_grid", "lim_m", "dx_m", "h_m", "depth_m", "floor_m", "surface_z_m",
                  "wall_m", "substeps", "sdf_res", "seed", "h0_over_d",
                  "ref_radius_m", "ref_mass_kg", "analytic_buoyancy_N")
    MUST_DIFFER = ("n_ghost_layers", "ghost_depth_m", "n_water")
    bad = 0
    for k in MUST_MATCH:
        vals = {n: c["config"].get(k) for n, c in cells.items()}
        if all(v is None for v in vals.values()):
            print(f"   {k:24s} NOT CHECKED, absent from all four configs")
            bad += 1
            continue
        ok = len(set(map(repr, vals.values()))) == 1
        if not ok:
            bad += 1
        print(f"   {k:24s} {'OK        ' if ok else 'DIFFER    '} {ref.get(k)}"
              + ("" if ok else f"   {vals}"))
    for k in MUST_DIFFER:
        vals = {n: c["config"].get(k) for n, c in cells.items()}
        by_ghost = {n[1]: v for n, v in vals.items()}
        consistent = all(vals[(e, g)] == by_ghost[g] for e, g in vals)
        print(f"   {k:24s} {'VARIES BY GHOST ONLY' if consistent else 'INCONSISTENT'}  {by_ghost}")
    print(f"   -> {bad} comparability problem(s)")
    for n, c in cells.items():
        print(f"   {str(n):16s} frames={len(c['rows']):4d}  n_water={c['config'].get('n_water')}"
              f"  n_ghost={c['config'].get('n_ghost_layers')}")
    real = cells[("pinned", 0)]["config"]["n_water"]

    print("\n1. THE 2x2, as percent error against analytic")
    r = {}
    for n, c in cells.items():
        v = mean_last(c["rows"], "fz_over_analytic_measured", W)
        r[n] = v
        print(f"   engine={n[0]:7s} ghost={n[1]}   ratio {v:.5f}   {100*(v-1):+7.2f} %   {band(100*(v-1))}")

    print("\n2. MAIN EFFECTS AND INTERACTION, in ratio units")
    e_at_g0 = r[("bcfix", 0)] - r[("pinned", 0)]
    e_at_g3 = r[("bcfix", 3)] - r[("pinned", 3)]
    g_at_p = r[("pinned", 3)] - r[("pinned", 0)]
    g_at_b = r[("bcfix", 3)] - r[("bcfix", 0)]
    inter = r[("bcfix", 3)] - r[("pinned", 0)] - e_at_g0 - g_at_p
    print(f"   engine effect at ghost=0   {e_at_g0:+.5f}")
    print(f"   engine effect at ghost=3   {e_at_g3:+.5f}")
    print(f"   ghost  effect at pinned    {g_at_p:+.5f}")
    print(f"   ghost  effect at bcfix     {g_at_b:+.5f}")
    print(f"   INTERACTION                {inter:+.5f}   "
          f"({'additive' if abs(inter) < 0.02 else 'NOT additive'}, |.|<0.02 called additive)")
    add = r[("pinned", 0)] + e_at_g0 + g_at_p
    print(f"   additive prediction for bcfix+ghost3  {add:.5f} ({100*(add-1):+.2f} %)")
    print(f"   observed                              {r[('bcfix',3)]:.5f} ({100*(r[('bcfix',3)]-1):+.2f} %)")

    print("\n3. WHICH PRE-REGISTERED BRANCH FIRED")
    obs = 100 * (r[("bcfix", 3)] - 1)
    best_single = min(100 * (r[("bcfix", 0)] - 1), 100 * (r[("pinned", 3)] - 1), key=abs)
    if obs <= 10:
        br = "B: PASS. Both defects were the whole story. Job B is rescued."
    elif 20 <= obs <= 26:
        br = "A: independent and additive. REPORTABLE PARTIAL, NOT a pass. Ladder stays stopped."
    elif obs >= 34:
        br = "C: no better than the better single fix. The two accounts are ONE defect counted twice."
    elif obs > 51:
        br = "D: antagonistic. Treat as a bug in the composition, not a physical result."
    else:
        br = (f"NONE EXACTLY. observed {obs:+.2f} % falls between the pre-registered bands. "
              f"Report it as such rather than rounding it into the nearest branch.")
    print(f"   observed {obs:+.2f} %   best single fix {best_single:+.2f} %")
    print(f"   -> {br}")
    print(f"   Job B criterion 3 verdict on the combined run: {band(obs)}")

    print("\n4. FLOOR CROSSINGS, baseline-corrected, as fraction of real water %d" % real)
    for n, c in cells.items():
        print(f"   engine={n[0]:7s} ghost={n[1]}   crossed {100*crossed_frac(c, real):6.3f} %"
              f"   (raw final n_below_floor {c['rows'][-1]['n_below_floor']})")

    if a.consistency:
        d = load(a.consistency)
        v = mean_last(d["rows"], "fz_over_analytic_measured", W)
        print("\n5. CONSISTENCY, job 918450 (200 frames, no SDF cache) vs this job's bcfix/ghost0")
        print(f"   918450        {v:.5f} ({100*(v-1):+.2f} %)  frames={len(d['rows'])}")
        print(f"   918526 ghost0 {r[('bcfix',0)]:.5f} ({100*(r[('bcfix',0)]-1):+.2f} %)  "
              f"frames={len(cells[('bcfix',0)]['rows'])}")
        print("   These differ in frame count and SDF caching, so a gap here is not an error;")
        print("   it bounds how much those settings move the metric.")


if __name__ == "__main__":
    main()
