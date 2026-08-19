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
# Panel 2 MOVED. The (v_car x v_water) load surface now lives in
# speed_surface.py, because it is a DIFFERENT experiment from the 17 canonical
# runs above: a prescribed collider with no verdict, against free bodies with a
# FORD / NO-FORD verdict. The functions that used to sit here were written
# against a placeholder schema (cell_id, F_horiz_N) that the real data does not
# use, so they would have returned "not computable" forever without ever saying
# they could not read the file. Removed rather than left to answer from an
# error path.
# ---------------------------------------------------------------------------

def self_test() -> int:
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    print("T1/T2 moved to speed_surface.self_test, along with the surface itself")

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
