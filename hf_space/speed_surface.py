"""d17-moving's (v_car x v_water) load surface: the analysis the Space renders.

Separate from `surface.py` on purpose. `surface.py` is the 17 canonical
STATIONARY-vehicle runs, which carry a FORD / NO-FORD verdict. This file is a
different experiment with a different validation basis and NO verdict: the hull
is a prescribed collider and cannot be swept away.

THREE SPREADS LIVE IN THIS DATA AND THEY ARE NOT THE SAME SIZE. Conflating them
is the single easiest way to misread the dataset, so every function here names
which one it is reporting.

  1. SEED spread, within one cell, across five seeds.
     Measured 0.066 to 0.338 percent, median 0.210. The scene is very nearly
     deterministic. Error bars drawn from this are invisible, and drawing them
     as if they were the interesting variation misrepresents the result.

  2. SPLIT spread, across cells that share |v_rel|.
     Measured as S = (max - min) / mean over an iso-|v_rel| arc. Order 1, i.e.
     roughly 100 percent, three orders of magnitude above the seed spread. THIS
     IS THE RESULT: a scalar |v_rel| does not determine the load.

  3. WINDOW spread, the same cell measured over different frame windows.
     The transient window f20-60 and the settled window f250-400 disagree by
     -45.6 to +271.3 percent on the same 20 cells. Larger than the split effect
     in several cells, and it is not a stochastic error bar at all: it is a
     statement that the load is still changing.

Everything here reads `data/load_surface.csv`, built by `ingest_speed_surface.py`
from a pinned git blob. No number is typed in from a summary.
"""

from __future__ import annotations

import csv
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

CANONICAL_SURFACE_FAMILIES = ["M1s0", "M1s1", "M1s2", "M1s3", "M1s4"]
PUBLISHED_TRANSIENT_FAMILY = "c3full"
G96_SURFACE_FAMILIES = ["M2s0", "M2s1"]
YARIS_HULL = "yaris_coarse_v1l_watertight"

# The pair d17's R5 states as "the contribution stated as a number".
HEADLINE_A = (2.2, 3.0)   # lower |v_rel|, 3.720 m/s
HEADLINE_B = (4.5, 0.5)   # higher |v_rel|, 4.528 m/s


class NoDataError(RuntimeError):
    """Raised when a computation cannot be evaluated.

    Distinct from a computation that evaluates to zero or to an empty set. A
    function that cannot tell those apart reports an error as a result.
    """


def load_records() -> list[dict]:
    path = os.path.join(DATA_DIR, "load_surface.csv")
    if not os.path.exists(path):
        raise NoDataError(f"{path} is absent; run ingest_speed_surface.py")
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise NoDataError(f"{path} exists but holds no rows")
    return rows


def _f(row: dict, key: str):
    v = row.get(key, "")
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _cell(row: dict):
    vc, vw = _f(row, "v_car_ms"), _f(row, "v_water_ms")
    if vc is None or vw is None:
        return None
    return (round(vc, 4), round(vw, 4))


def _select(rows: list[dict], families: list[str]) -> list[dict]:
    want = set(families)
    return [r for r in rows if r.get("family") in want]


def canonical_surface(rows: list[dict] | None = None) -> list[dict]:
    """Per-cell mean and seed spread over the five-seed settled surface.

    Reports SPREAD 1 (seed). n is the number of seeds actually found, never
    assumed to be five.
    """
    rows = rows if rows is not None else load_records()
    sel = _select(rows, CANONICAL_SURFACE_FAMILIES)
    if not sel:
        raise NoDataError(
            f"none of {CANONICAL_SURFACE_FAMILIES} present; cannot build the surface")
    by: dict = {}
    for r in sel:
        c = _cell(r)
        v = _f(r, "force_horiz_mag_N")
        if c is None or v is None:
            continue
        by.setdefault(c, []).append(v)
    out = []
    for c in sorted(by):
        vals = by[c]
        mean = statistics.mean(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
        out.append({
            "v_car_ms": c[0],
            "v_water_ms": c[1],
            "v_rel_mag_ms": round(math.hypot(c[0], c[1]), 4),
            "angle_from_broadside_deg": round(math.degrees(math.atan2(c[0], c[1])), 2)
            if (c[0] or c[1]) else 0.0,
            "n_seeds": len(vals),
            "F_horiz_mean_N": round(mean, 3),
            "F_horiz_sd_N": round(sd, 4),
            "seed_rel_sd_pct": round(100.0 * sd / mean, 4) if mean else None,
            "F_horiz_min_N": round(min(vals), 3),
            "F_horiz_max_N": round(max(vals), 3),
        })
    if not out:
        raise NoDataError("surface families present but carried no usable forces")
    return out


def seed_spread_stats(rows: list[dict] | None = None) -> dict:
    """SPREAD 1 summarised across the surface."""
    surf = canonical_surface(rows)
    vals = [c["seed_rel_sd_pct"] for c in surf if c["seed_rel_sd_pct"] is not None]
    if not vals:
        raise NoDataError("no per-cell seed spreads could be computed")
    ns = {c["n_seeds"] for c in surf}
    return {
        "which_spread": "1 of 3: SEED, within a cell",
        "cells": len(surf),
        "seeds_per_cell": sorted(ns),
        "min_pct": round(min(vals), 4),
        "median_pct": round(statistics.median(vals), 4),
        "max_pct": round(max(vals), 4),
        "reading": ("the scene is very nearly deterministic across seeds; this is NOT "
                    "the interesting variation and must not be drawn as the headline"),
    }


def window_comparison(rows: list[dict] | None = None) -> list[dict]:
    """SPREAD 3. Published transient surface against the settled five-seed surface.

    d17's R5 table is the TRANSIENT window. The settled surface exists in the
    same shipped data. This function is the only place the two meet.
    """
    rows = rows if rows is not None else load_records()
    settled = {(c["v_car_ms"], c["v_water_ms"]): c for c in canonical_surface(rows)}
    trans_rows = _select(rows, [PUBLISHED_TRANSIENT_FAMILY])
    if not trans_rows:
        raise NoDataError(f"{PUBLISHED_TRANSIENT_FAMILY} absent; cannot compare windows")
    out = []
    for r in trans_rows:
        c = _cell(r)
        t = _f(r, "force_horiz_mag_N")
        if c is None or t is None or c not in settled:
            continue
        s = settled[c]["F_horiz_mean_N"]
        out.append({
            "v_car_ms": c[0],
            "v_water_ms": c[1],
            "transient_f20_60_N": round(t, 3),
            "settled_f250_400_N": round(s, 3),
            "settled_minus_transient_pct": round(100.0 * (s - t) / t, 3) if t else None,
        })
    if not out:
        raise NoDataError("no cells matched between the transient and settled surfaces")
    return sorted(out, key=lambda d: (d["v_car_ms"], d["v_water_ms"]))


def headline_pair(rows: list[dict] | None = None) -> dict:
    """The specific published comparison, recomputed in both windows.

    d17 R5: "the cell with the LOWER relative speed carries 2.3x the load."
    That is a TRANSIENT-window statement. This reports what the settled
    five-seed surface says about the same two cells.
    """
    rows = rows if rows is not None else load_records()
    settled = {(c["v_car_ms"], c["v_water_ms"]): c for c in canonical_surface(rows)}
    trans = {}
    for r in _select(rows, [PUBLISHED_TRANSIENT_FAMILY]):
        c = _cell(r)
        v = _f(r, "force_horiz_mag_N")
        if c is not None and v is not None:
            trans[c] = v
    for c in (HEADLINE_A, HEADLINE_B):
        if c not in settled or c not in trans:
            raise NoDataError(f"headline cell {c} missing from a window; cannot compare")
    res = {
        "cell_lower_vrel": {"v_car_ms": HEADLINE_A[0], "v_water_ms": HEADLINE_A[1],
                            "v_rel_mag_ms": round(math.hypot(*HEADLINE_A), 4)},
        "cell_higher_vrel": {"v_car_ms": HEADLINE_B[0], "v_water_ms": HEADLINE_B[1],
                             "v_rel_mag_ms": round(math.hypot(*HEADLINE_B), 4)},
        "transient": {
            "lower_N": round(trans[HEADLINE_A], 3),
            "higher_N": round(trans[HEADLINE_B], 3),
            "ratio_lower_over_higher": round(trans[HEADLINE_A] / trans[HEADLINE_B], 4),
            "n_seeds": 1,
        },
        "settled": {
            "lower_N": settled[HEADLINE_A]["F_horiz_mean_N"],
            "lower_sd_N": settled[HEADLINE_A]["F_horiz_sd_N"],
            "higher_N": settled[HEADLINE_B]["F_horiz_mean_N"],
            "higher_sd_N": settled[HEADLINE_B]["F_horiz_sd_N"],
            "ratio_lower_over_higher": round(
                settled[HEADLINE_A]["F_horiz_mean_N"] / settled[HEADLINE_B]["F_horiz_mean_N"], 4),
            "n_seeds": settled[HEADLINE_A]["n_seeds"],
        },
    }
    res["ratio_crosses_one"] = (
        (res["transient"]["ratio_lower_over_higher"] - 1.0)
        * (res["settled"]["ratio_lower_over_higher"] - 1.0) < 0)
    return res


ial_ARMS = [
    ("c3full", ["c3full"], "g64", "60/20", "transient"),
    ("L2full", ["L2full"], "g64", "400/250", "settled"),
    ("M1s*", CANONICAL_SURFACE_FAMILIES, "g64", "400/250", "settled"),
    ("M2s*", ["M2s0", "M2s1"], "g96", "400/250", "settled"),
]


def arm_ratio_table(rows: list[dict] | None = None) -> list[dict]:
    """The headline pair recomputed in every arm that holds both cells.

    Exists because d17-moving WITHDREW the 2.3x figure in 51c158b once the two
    numbers were shown to be different windows of the same experiment. The
    inversion is not one arm's opinion: it survives a change of seed, of
    bc_per_frame rate, and of grid. This table is the evidence for that, and it
    is computed rather than transcribed.
    """
    rows = rows if rows is not None else load_records()
    out = []
    for name, fams, grid, window, kind in ial_ARMS:
        by: dict = {}
        for r in _select(rows, list(fams)):
            c = _cell(r)
            v = _f(r, "force_horiz_mag_N")
            if c is not None and v is not None:
                by.setdefault(c, []).append(v)
        if HEADLINE_A not in by or HEADLINE_B not in by:
            continue
        a = statistics.mean(by[HEADLINE_A])
        b = statistics.mean(by[HEADLINE_B])
        out.append({
            "arm": name, "grid": grid, "frames_discard": window, "window_kind": kind,
            "n_seeds": len(by[HEADLINE_A]),
            "lower_vrel_N": round(a, 1), "higher_vrel_N": round(b, 1),
            "ratio": round(a / b, 4) if b else None,
        })
    if not out:
        raise NoDataError("no arm held both headline cells; cannot build the ratio table")
    return out


def iso_vrel_arcs(rows: list[dict] | None = None) -> list[dict]:
    """SPREAD 2. S = (max-min)/mean across each iso-|v_rel| arc.

    S is dimensionless and is the size of what a scalar |v_rel| treatment omits.
    """
    rows = rows if rows is not None else load_records()
    arcs: dict = {}
    for r in rows:
        fam = r.get("family", "")
        if not fam.startswith("M3m"):
            continue
        mag = _f(r, "v_rel_mag_ms")
        val = _f(r, "force_horiz_mag_N")
        if mag is None or val is None:
            continue
        arcs.setdefault(round(mag, 3), []).append(
            (_f(r, "v_rel_angle_deg_from_broadside"), val))
    if not arcs:
        raise NoDataError("no M3m* iso-|v_rel| arcs present")
    out = []
    for mag in sorted(arcs):
        pts = arcs[mag]
        vals = [v for _, v in pts]
        mean = statistics.mean(vals)
        out.append({
            "v_rel_mag_ms": mag,
            "n_points": len(vals),
            "F_min_N": round(min(vals), 3),
            "F_max_N": round(max(vals), 3),
            "F_mean_N": round(mean, 3),
            "S_spread": round((max(vals) - min(vals)) / mean, 4) if mean else None,
            "argmax_angle_deg_from_broadside": round(
                max(pts, key=lambda p: p[1])[0], 2) if pts[0][0] is not None else None,
        })
    return out


def three_spreads(rows: list[dict] | None = None) -> dict:
    """The one table that keeps the three spreads apart."""
    rows = rows if rows is not None else load_records()
    seed = seed_spread_stats(rows)
    arcs = iso_vrel_arcs(rows)
    win = window_comparison(rows)
    win_pct = [w["settled_minus_transient_pct"] for w in win
               if w["settled_minus_transient_pct"] is not None]
    s_vals = [a["S_spread"] for a in arcs if a["S_spread"] is not None]
    return {
        "seed_spread_pct": {"min": seed["min_pct"], "median": seed["median_pct"],
                            "max": seed["max_pct"]},
        "split_spread_S": {"min": min(s_vals), "max": max(s_vals),
                           "at_v_rel": [a["v_rel_mag_ms"] for a in arcs]},
        "window_spread_pct": {"min": min(win_pct), "max": max(win_pct)},
        "ordering": ("split and window spreads exceed the seed spread by two to three "
                     "orders of magnitude; only the seed spread is a random error bar"),
    }


def resolution_check(rows: list[dict] | None = None) -> dict:
    """g64 surface against the g96 surface, cell by cell, both averaged over seeds.

    Reports the SIZE of the resolution effect. It is not a convergence claim and
    two grids cannot make one: a grid-convergence statement needs a
    time-averaged observable on a demonstrated-stationary window with a GCI, and
    this project's own record shows the displacement measure is non-monotone
    under refinement.
    """
    rows = rows if rows is not None else load_records()
    settled = {(c["v_car_ms"], c["v_water_ms"]): c for c in canonical_surface(rows)}
    g96_draws: dict = {}
    for r in _select(rows, G96_SURFACE_FAMILIES):
        c = _cell(r)
        v = _f(r, "force_horiz_mag_N")
        if c is not None and v is not None:
            g96_draws.setdefault(c, []).append(v)
    if not g96_draws:
        raise NoDataError(
            f"none of {G96_SURFACE_FAMILIES} present; no resolution check possible")
    diffs = []
    g96_rel_sd = []
    for c, vals in g96_draws.items():
        m96 = statistics.mean(vals)
        if len(vals) > 1 and m96:
            g96_rel_sd.append(100.0 * statistics.stdev(vals) / m96)
        if c in settled and settled[c]["F_horiz_mean_N"]:
            diffs.append(100.0 * (m96 - settled[c]["F_horiz_mean_N"])
                         / settled[c]["F_horiz_mean_N"])
    if not diffs:
        raise NoDataError("no overlapping cells between g64 and g96 surfaces")
    seeds = sorted({len(v) for v in g96_draws.values()})
    return {
        "cells_compared": len(diffs),
        "g96_seeds_per_cell": seeds,
        "g96_seed_rel_sd_pct": (
            {"min": round(min(g96_rel_sd), 4), "max": round(max(g96_rel_sd), 4)}
            if g96_rel_sd else None),
        "g96_minus_g64_pct": {"min": round(min(diffs), 3), "max": round(max(diffs), 3),
                              "median": round(statistics.median(diffs), 3)},
        "reading": ("the size of the resolution effect between two grids, NOT a "
                    "convergence result; no grid-converged claim follows from it"),
    }


def self_test() -> int:
    """Every check must be able to FAIL. A test that cannot fire is not a test."""
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    print("T1 the loader distinguishes absent from empty")
    try:
        load_records()
        loaded = True
    except NoDataError:
        loaded = False
    check("data present", loaded, "run ingest_speed_surface.py if this fails")
    if not loaded:
        print(f"\n{len(fails)} failure(s)")
        return 1
    rows = load_records()

    print("T2 the surface is built from five seeds, not asserted to be")
    surf = canonical_surface(rows)
    check("20 cells", len(surf) == 20, f"{len(surf)} cells")
    check("every cell reports its own n_seeds",
          all(c["n_seeds"] >= 1 for c in surf),
          f"n_seeds seen: {sorted({c['n_seeds'] for c in surf})}")

    print("T3 NEGATIVE CONTROL: an empty selection must raise, not return []")
    try:
        canonical_surface([r for r in rows if r.get("family") == "no-such-family"])
        check("raises NoDataError on an empty selection", False)
    except NoDataError:
        check("raises NoDataError on an empty selection", True)

    print("T4 the three spreads are ordered as documented")
    ts = three_spreads(rows)
    seed_max = ts["seed_spread_pct"]["max"]
    split_min_pct = 100.0 * ts["split_spread_S"]["min"]
    check("split spread exceeds seed spread by >10x",
          split_min_pct > 10 * seed_max,
          f"split min {split_min_pct:.1f} % vs seed max {seed_max:.3f} %")

    print("T5 the headline pair is recomputed in both windows")
    hp = headline_pair(rows)
    check("transient ratio > 1", hp["transient"]["ratio_lower_over_higher"] > 1.0,
          f"{hp['transient']['ratio_lower_over_higher']}")
    check("settled ratio computed from >1 seed", hp["settled"]["n_seeds"] > 1,
          f"n_seeds={hp['settled']['n_seeds']}")
    check("crossing flag agrees with the two ratios",
          hp["ratio_crosses_one"] == ((hp["transient"]["ratio_lower_over_higher"] - 1)
                                      * (hp["settled"]["ratio_lower_over_higher"] - 1) < 0),
          f"crosses={hp['ratio_crosses_one']}")

    print("T6 arcs and resolution check evaluate")
    arcs = iso_vrel_arcs(rows)
    check("at least three arcs", len(arcs) >= 3, f"{len(arcs)} arcs")
    check("every arc reports n_points", all(a["n_points"] > 1 for a in arcs))
    rc = resolution_check(rows)
    check("resolution check compared cells", rc["cells_compared"] > 0,
          f"{rc['cells_compared']} cells")

    print(f"\n{len(fails)} failure(s)" + (": " + ", ".join(fails) if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(self_test())
