"""Pure logic for the Can It Ford Space. No gradio, no plotting, so it can be tested.

Separated from app.py deliberately: a Space whose logic only runs inside a web callback
cannot be unit tested, and every number shown to a stranger should be reproducible from a
function call.

WHAT THIS MODULE WILL NOT DO
----------------------------
It will not invent a load surface. When the (v_car x v_water) table is empty it reports
that it is empty and shows the pre-registered matrix as a lattice of planned cells. A
plausible-looking surface drawn from no data is the single worst thing this Space could
render, because it would look exactly like a result.
"""

from __future__ import annotations

import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

# The deciding literals, defaults. Three share the numeral 0.05 across TWO units.
# Never deduplicate these by value; a find-and-replace would turn a speed into a distance.
DEFAULT_SLIDE_M = 0.05          # metres
DEFAULT_SLIDE_SPEED_MS = 0.05   # metres per second
DEFAULT_SUSTAIN_FRAMES = 3      # frames, and unsourced

# d17-moving pre-registration, docs/R9_MOVING_VEHICLE_2026-08-19.md section 3 (d3e52fd).
PREREG_V_CAR = [0.0, 2.2, 4.5, 6.7, 8.9]      # m/s, i.e. 0/5/10/15/20 mph
PREREG_V_WATER = [0.5, 1.0, 2.0, 3.0]         # m/s
PREREG_ARC = [
    ("A0", 0.000, 3.000, 0.0),
    ("A1", 1.148, 2.772, 22.5),
    ("A2", 2.121, 2.121, 45.0),
    ("A3", 2.772, 1.148, 67.5),
    ("A4", 3.000, 0.000, 90.0),
]

# Measured repeat draws. n=2, which is a RANGE and not a distribution.
# Draw 1 is the gated run in data/all_runs_inventory.csv; draw 2 is the independent
# repeat in data/g128_canonical_repeat/. Both read live 2026-08-19.
REPEAT_DRAWS = {
    "g96_m1100": (0.2686379551887512, 0.27009397745132446),
    "g96_m1609": (0.1559590846300125, 0.15585969388484955),
    "g96_m2337": (0.0894387811422348, 0.08549453318119049),
}


def load_table(name: str) -> list[dict]:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _f(row: dict, key: str):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Panel 1: the verdict-flip explorer. This runs on data that exists today.
# ---------------------------------------------------------------------------

def reclassify(runs: list[dict], slide_m: float) -> list[dict]:
    """Recompute the distance half of the SLIDE test at a user-chosen threshold.

    IMPORTANT, and shown in the UI: this varies ONE threshold. The published verdict is a
    JOINT condition over distance, speed and a persistence count, and this project has
    already published and retracted a claim built on a one-at-a-time sweep. So a run that
    does not change here is NOT shown to be robust; it is only not shown to be fragile.
    """
    out = []
    for r in runs:
        drift = _f(r, "max_surge_drift_m")
        if drift is None:
            continue
        published = r.get("failure_mode", "")
        exceeds = drift > slide_m
        # The published label is the joint condition's answer; this is the distance
        # half alone, so we report AGREEMENT with the published label, not a new verdict.
        published_exceeds = published == "SLIDE"
        out.append({
            "run_id": r.get("run_id", ""),
            "n_grid": r.get("n_grid", ""),
            "mass_kg": r.get("mass_kg", ""),
            "velocity_ms": r.get("velocity_ms", ""),
            "max_surge_drift_m": drift,
            "published_mode": published,
            "distance_test_exceeds": exceeds,
            "disagrees_with_published": exceeds != published_exceeds,
            "margin_m": drift - slide_m,
        })
    return out


def flip_summary(rows: list[dict], slide_m: float) -> str:
    n = len(rows)
    dis = [r for r in rows if r["disagrees_with_published"]]
    near = sorted(rows, key=lambda r: abs(r["margin_m"]))[:3]
    lines = [
        f"**{n} runs** evaluated at `slide_m = {slide_m:.4f} m`.",
        "",
        f"- **{len(dis)}** disagree with the published label on the distance test alone.",
        "",
        "Closest to the boundary:",
    ]
    for r in near:
        lines.append(
            f"  - `{r['run_id']}` drift {r['max_surge_drift_m']:.4f} m, "
            f"margin {r['margin_m']:+.4f} m, published **{r['published_mode']}**"
        )
    lines += [
        "",
        "> The published label is a **joint** test of distance, speed and a persistence "
        "count of 3 frames. This slider moves only the distance. A run that does not move "
        "here is not shown to be robust, only not shown to be fragile by this weak test.",
    ]
    return "\n".join(lines)


def repeat_spread_table() -> list[dict]:
    """Measured spread between two independent draws of the same configuration."""
    out = []
    for cfg, (a, b) in sorted(REPEAT_DRAWS.items()):
        mean = (a + b) / 2.0
        out.append({
            "config": cfg,
            "draw_1_final_disp_m": round(a, 6),
            "draw_2_final_disp_m": round(b, 6),
            "abs_range_m": round(abs(a - b), 6),
            "rel_range_pct": round(100.0 * abs(a - b) / mean, 3),
            "n_draws": 2,
        })
    return out


# ---------------------------------------------------------------------------
# Panel 2: the load surface. Honest about being empty.
# ---------------------------------------------------------------------------

def surface_status() -> dict:
    rows = load_table("load_surface.csv")
    cells = {}
    for r in rows:
        key = (r.get("v_car_ms", ""), r.get("v_water_ms", ""))
        cells.setdefault(key, []).append(r)
    return {
        "n_rows": len(rows),
        "n_cells": len(cells),
        "populated": len(rows) > 0,
        "cells": cells,
    }


def surface_lattice() -> list[dict]:
    """The pre-registered matrix as planned cells, with any measured values attached."""
    st = surface_status()
    out = []
    for vc in PREREG_V_CAR:
        for vw in PREREG_V_WATER:
            got = []
            for (k_vc, k_vw), rows in st["cells"].items():
                try:
                    if math.isclose(float(k_vc), vc) and math.isclose(float(k_vw), vw):
                        got = rows
                except (TypeError, ValueError):
                    continue
            forces = [_f(r, "F_horiz_N") for r in got]
            forces = [f for f in forces if f is not None]
            rec = {
                "v_car_ms": vc,
                "v_water_ms": vw,
                "v_rel_mag_ms": round(math.hypot(vc, vw), 4),
                "angle_from_broadside_deg": round(math.degrees(math.atan2(vc, vw)), 2)
                if (vc or vw) else 0.0,
                "n_repeats": len(forces),
            }
            if forces:
                mean = sum(forces) / len(forces)
                rec["F_horiz_mean_N"] = round(mean, 4)
                rec["F_horiz_range_N"] = round(max(forces) - min(forces), 4)
                rec["spread_pct"] = round(100.0 * (max(forces) - min(forces)) / mean, 3) \
                    if mean else None
            else:
                rec["F_horiz_mean_N"] = None
                rec["F_horiz_range_N"] = None
                rec["spread_pct"] = None
            out.append(rec)
    return out


def iso_vrel_spread() -> tuple[float | None, str]:
    """Pre-registered criterion C2: spread of |F_horiz| across the iso-|v_rel| arc.

    S < 0.10 means collapsing v_car and v_water into one scalar is defensible, and that
    is a publishable NEGATIVE. S >= 0.10 means the split matters and S measures what a
    scalar treatment omits. Registered in advance so neither outcome can be presented as
    the expected one.
    """
    rows = load_table("load_surface.csv")
    by_cell: dict[str, list[float]] = {}
    for r in rows:
        cid = r.get("cell_id", "")
        val = _f(r, "F_horiz_N")
        if cid.startswith("A") and val is not None:
            by_cell.setdefault(cid, []).append(abs(val))
    have = [c for c, _, _, _ in PREREG_ARC if c in by_cell]
    if len(have) < len(PREREG_ARC):
        return None, (
            f"Not computable: {len(have)} of {len(PREREG_ARC)} arc cells present. "
            "C2 needs all five."
        )
    means = [sum(by_cell[c]) / len(by_cell[c]) for c, _, _, _ in PREREG_ARC]
    m = sum(means) / len(means)
    if m == 0:
        return None, "Not computable: mean |F_horiz| is zero."
    s = (max(means) - min(means)) / m
    verdict = ("the split MATTERS, and S is the size of what a scalar treatment omits"
               if s >= 0.10 else
               "collapsing v_car and v_water into one scalar is DEFENSIBLE (a negative "
               "result, reported as such)")
    return s, f"S = {s:.4f}. Pre-registered reading: {verdict}."


def self_test() -> int:
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    print("T1 an empty surface must report empty, never fabricate")
    st = surface_status()
    check("no rows reported as not populated",
          st["populated"] == (st["n_rows"] > 0), f"n_rows={st['n_rows']}")
    lat = surface_lattice()
    check("lattice covers the pre-registered matrix",
          len(lat) == len(PREREG_V_CAR) * len(PREREG_V_WATER), f"{len(lat)} cells")
    check("unpopulated cells carry None, not 0.0",
          all(c["F_horiz_mean_N"] is None for c in lat) if st["n_rows"] == 0 else True)

    print("T2 C2 refuses to compute from a partial arc")
    s, msg = iso_vrel_spread()
    check("returns None when the arc is incomplete", s is None if st["n_rows"] == 0 else True, msg)

    print("T3 reclassify tracks the threshold")
    runs = load_table("canonical_runs.csv")
    if runs:
        lo = reclassify(runs, 0.001)
        hi = reclassify(runs, 10.0)
        check("tiny threshold: all exceed", all(r["distance_test_exceeds"] for r in lo))
        check("huge threshold: none exceed", not any(r["distance_test_exceeds"] for r in hi))
        check("POSITIVE CONTROL: the two differ",
              [r["distance_test_exceeds"] for r in lo] != [r["distance_test_exceeds"] for r in hi])
    else:
        check("canonical_runs.csv present", False, "no data dir; run hf_dataset_publish.py")

    print("T4 repeat spread is a range, labelled n=2")
    rs = repeat_spread_table()
    check("three configs", len(rs) == 3, str([r["config"] for r in rs]))
    check("every row says n=2", all(r["n_draws"] == 2 for r in rs))
    check("largest spread is g96_m2337",
          max(rs, key=lambda r: r["rel_range_pct"])["config"] == "g96_m2337")

    print(f"\n{len(fails)} failure(s)" + (": " + ", ".join(fails) if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(self_test())
