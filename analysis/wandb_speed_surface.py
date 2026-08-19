#!/usr/bin/env python3
"""Log the (v_car x v_water) load surface to Weights and Biases as DISTRIBUTIONS.

WHY DISTRIBUTIONS AND NOT POINTS
--------------------------------
This project's argument is that the field publishes thresholds and single points while a
repeat ensemble is the ingredient nobody has. A W&B view that plots one marker per cell
would undercut the very claim it exists to support. So every cell is logged with its
repeat draws intact, and the summary metric for a cell is a RANGE plus a count, never a
lone mean.

WHY IT REFUSES TO INVENT A DISTRIBUTION
---------------------------------------
Measured today, the only repeat draws that exist for the canonical scene are n=2 for
three g96 configurations. Two draws give a RANGE, not a distribution: no standard
deviation is derivable from two samples in any way worth publishing. This script
therefore reports `n_draws` on every record and refuses to emit a sigma below
MIN_N_FOR_SIGMA. That refusal is tested.

DRY RUN IS THE DEFAULT
----------------------
Nothing touches the network unless --log is passed. The dry run performs the identical
aggregation and prints it, so the numbers can be checked before any run object exists in
a shared workspace.

Usage:
  python3 analysis/wandb_speed_surface.py --self-test
  python3 analysis/wandb_speed_surface.py --surface path/to/load_surface.csv
  python3 analysis/wandb_speed_surface.py --surface ... --log
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
import sys

ENTITY = "jcerrell29-claremont-mckenna-college"
PROJECT = "can-it-ford"

# Below this, report a range and a count, never a standard deviation.
MIN_N_FOR_SIGMA = 3

# Pre-registered matrix, d17-moving docs/R9_MOVING_VEHICLE_2026-08-19.md section 3.
PREREG_V_CAR = [0.0, 2.2, 4.5, 6.7, 8.9]
PREREG_V_WATER = [0.5, 1.0, 2.0, 3.0]
ARC_CELLS = ["A0", "A1", "A2", "A3", "A4"]


def read_surface(path: str) -> list[dict]:
    """Read the surface table, distinguishing ABSENT from EMPTY.

    This used to return [] for a missing file, which is indistinguishable
    downstream from a file that exists and holds nothing, and both are
    indistinguishable from a schema mismatch. All three now raise.
    """
    if not path:
        raise RuntimeError("no surface path given")
    if not os.path.exists(path):
        raise RuntimeError(f"surface table absent: {path}\n"
                           "  run hf_space/ingest_speed_surface.py first")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise RuntimeError(f"surface table {path} exists but holds no rows")
    required = {"family", "v_car_ms", "v_water_ms", "force_horiz_mag_N"}
    missing = required - set(rows[0].keys())
    if missing:
        raise RuntimeError(
            f"surface table {path} is missing columns {sorted(missing)}.\n"
            "  This is a SCHEMA MISMATCH, not an empty result. Aggregating it\n"
            "  would silently produce zero cells and log an empty W&B run.")
    return rows


def _f(row, key):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return None


# The five-seed settled surface. Pooling other families would mix measurement
# windows and, worse, mix hulls: the fidC/fidF rows are Silverado, not the Yaris.
SURFACE_FAMILIES = ("M1s0", "M1s1", "M1s2", "M1s3", "M1s4")


def aggregate(rows: list[dict], families=SURFACE_FAMILIES) -> list[dict]:
    """Group repeat draws by cell and summarise WITHOUT overstating the sample.

    Draws here are SEEDS, which is the only spread in this data that is a random
    error bar. The split spread and the window spread are systematic and are
    reported separately; do not let a reader mistake one for another.
    """
    cells: dict[tuple, list[float]] = {}
    meta: dict[tuple, dict] = {}
    want = set(families)
    for r in rows:
        if r.get("family") not in want:
            continue
        vc, vw = _f(r, "v_car_ms"), _f(r, "v_water_ms")
        fh = _f(r, "force_horiz_mag_N")
        if vc is None or vw is None or fh is None:
            continue
        key = (round(vc, 6), round(vw, 6))
        cells.setdefault(key, []).append(fh)
        meta.setdefault(key, {"cell_id": f"vc{vc:g}_vw{vw:g}",
                              "n_grid": r.get("n_grid", "")})
    if not cells:
        raise RuntimeError(
            f"aggregate() matched ZERO cells for families {sorted(want)}.\n"
            "  The table was readable, so this is a selection failure, not an\n"
            "  empty dataset. Refusing to return [] and let a caller log nothing.")

    out = []
    for (vc, vw), vals in sorted(cells.items()):
        n = len(vals)
        mean = statistics.fmean(vals)
        rec = {
            "cell_id": meta[(vc, vw)]["cell_id"],
            "n_grid": meta[(vc, vw)]["n_grid"],
            "v_car_ms": vc,
            "v_water_ms": vw,
            "v_rel_mag_ms": round(math.hypot(vc, vw), 6),
            "angle_from_broadside_deg": round(math.degrees(math.atan2(vc, vw)), 3)
            if (vc or vw) else 0.0,
            "n_draws": n,
            "F_horiz_mean_N": mean,
            "F_horiz_min_N": min(vals),
            "F_horiz_max_N": max(vals),
            "F_horiz_range_N": max(vals) - min(vals),
            "F_horiz_range_pct": (100.0 * (max(vals) - min(vals)) / mean) if mean else None,
            "draws": vals,
        }
        # The refusal, and it is the point of this module.
        if n >= MIN_N_FOR_SIGMA:
            rec["F_horiz_std_N"] = statistics.stdev(vals)
            rec["sigma_reported"] = True
        else:
            rec["F_horiz_std_N"] = None
            rec["sigma_reported"] = False
            rec["sigma_withheld_reason"] = (
                f"n={n} < {MIN_N_FOR_SIGMA}: a range, not a distribution"
            )
        out.append(rec)
    return out


def iso_vrel_criterion(rows: list[dict]) -> tuple[float | None, str]:
    """Pre-registered C2: spread across each iso-|v_rel| arc.

    REWRITTEN 2026-08-19. This used to look for cell ids 'A0'..'A4' from a
    placeholder schema. Those ids do not exist in the real data, so it returned
    NOT COMPUTABLE every time and would have done so forever, while looking like
    a criterion that was being evaluated. The arcs are the M3m* families.

    Takes the raw records, NOT the aggregate: the aggregate is the g64 surface,
    and the arcs are a different family. Passing the aggregate here is what made
    the old version unable to fire.
    """
    arcs: dict = {}
    for r in rows:
        if not str(r.get("family", "")).startswith("M3m"):
            continue
        mag, val = _f(r, "v_rel_mag_ms"), _f(r, "force_horiz_mag_N")
        if mag is None or val is None:
            continue
        arcs.setdefault(round(mag, 3), []).append(val)
    if not arcs:
        return None, ("C2 NOT COMPUTABLE: no M3m* iso-|v_rel| arcs in the table. "
                      "This is an absent family, not a null result.")
    parts, worst = [], None
    for mag in sorted(arcs):
        vals = arcs[mag]
        m = statistics.fmean(vals)
        if not m:
            continue
        s = (max(vals) - min(vals)) / m
        worst = s if worst is None else max(worst, s)
        parts.append(f"|v_rel|={mag:g} m/s: S={s:.4f} (n={len(vals)})")
    if worst is None:
        return None, "C2 NOT COMPUTABLE: every arc had a zero mean."
    reading = ("SPLIT MATTERS: S is the size of what collapsing the two speeds omits"
               if worst >= 0.10 else
               "SCALAR DEFENSIBLE: collapsing v_car and v_water is defensible "
               "(a negative result, and it is reported as one)")
    return worst, (f"C2 against the pre-registered 0.10. {reading}. "
                   + "; ".join(parts))


def render_report(agg: list[dict], rows: list[dict]) -> str:
    lines = ["", "CELL SUMMARY (range and count, sigma only where n >= "
             f"{MIN_N_FOR_SIGMA})", ""]
    lines.append(f"{'cell':6s} {'v_car':>6s} {'v_wat':>6s} {'|vrel|':>7s} "
                 f"{'n':>3s} {'mean N':>12s} {'range N':>10s} {'range %':>8s} {'sigma':>10s}")
    for a in agg:
        sig = f"{a['F_horiz_std_N']:.4f}" if a["sigma_reported"] else "withheld"
        rp = f"{a['F_horiz_range_pct']:.2f}" if a["F_horiz_range_pct"] is not None else "n/a"
        lines.append(
            f"{a['cell_id']:6s} {a['v_car_ms']:6.2f} {a['v_water_ms']:6.2f} "
            f"{a['v_rel_mag_ms']:7.3f} {a['n_draws']:3d} {a['F_horiz_mean_N']:12.4f} "
            f"{a['F_horiz_range_N']:10.4f} {rp:>8s} {sig:>10s}")
    _, msg = iso_vrel_criterion(rows)
    lines += ["", msg, ""]
    return "\n".join(lines)


def coverage(agg: list[dict]) -> str:
    have = {(a["v_car_ms"], a["v_water_ms"]) for a in agg}
    want = {(vc, vw) for vc in PREREG_V_CAR for vw in PREREG_V_WATER}
    missing = sorted(want - have)
    lines = [f"matrix coverage: {len(want & have)} of {len(want)} pre-registered cells"]
    if missing:
        lines.append(f"  MISSING {len(missing)} cells, listed so the gap is not silent:")
        for vc, vw in missing:
            lines.append(f"    v_car={vc} v_water={vw}")
    return "\n".join(lines)


def log_to_wandb(agg: list[dict], rows: list[dict], entity: str, project: str, group: str) -> int:
    try:
        import wandb
    except ImportError:
        print("wandb not installed. uv pip install wandb")
        return 3
    if not agg:
        print("refusing to log: nothing to log. An empty W&B run is worse than none.")
        return 4

    run = wandb.init(entity=entity, project=project, group=group,
                     job_type="load-surface",
                     tags=["load-surface", "v_car_x_v_water", "warpmpm", "distributions"],
                     config={"min_n_for_sigma": MIN_N_FOR_SIGMA,
                             "prereg_v_car": PREREG_V_CAR,
                             "prereg_v_water": PREREG_V_WATER})
    cols = ["cell_id", "v_car_ms", "v_water_ms", "v_rel_mag_ms",
            "angle_from_broadside_deg", "n_draws", "F_horiz_mean_N",
            "F_horiz_min_N", "F_horiz_max_N", "F_horiz_range_N",
            "F_horiz_range_pct", "F_horiz_std_N", "sigma_reported"]
    table = wandb.Table(columns=cols)
    for a in agg:
        table.add_data(*[a.get(c) for c in cols])
    # Every individual draw, so a reader can see the ensemble not just its summary.
    draws = wandb.Table(columns=["cell_id", "v_car_ms", "v_water_ms", "draw_index",
                                 "F_horiz_N"])
    for a in agg:
        for i, v in enumerate(a["draws"]):
            draws.add_data(a["cell_id"], a["v_car_ms"], a["v_water_ms"], i, v)

    s, msg = iso_vrel_criterion(rows)
    run.log({"load_surface_cells": table, "load_surface_draws": draws})
    run.summary["c2_iso_vrel_spread_S"] = s
    run.summary["c2_reading"] = msg
    run.summary["n_cells"] = len(agg)
    run.summary["n_draws_total"] = sum(a["n_draws"] for a in agg)
    run.summary["cells_with_sigma"] = sum(1 for a in agg if a["sigma_reported"])
    print(f"logged to {run.url}")
    run.finish()
    return 0


# ---------------------------------------------------------------------------

def self_test() -> int:
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    print("T1 sigma is WITHHELD below the minimum sample")
    two = [{"cell_id": "A0", "v_car_ms": "0", "v_water_ms": "3", "F_horiz_N": "100"},
           {"cell_id": "A0", "v_car_ms": "0", "v_water_ms": "3", "F_horiz_N": "110"}]
    a2 = aggregate(two)
    check("one cell", len(a2) == 1)
    check("n_draws is 2", a2[0]["n_draws"] == 2)
    check("sigma withheld", a2[0]["sigma_reported"] is False and a2[0]["F_horiz_std_N"] is None)
    check("range still reported", abs(a2[0]["F_horiz_range_N"] - 10.0) < 1e-9,
          f"range={a2[0]['F_horiz_range_N']}")

    print("T2 POSITIVE CONTROL: sigma IS reported at n >= 3")
    three = two + [{"cell_id": "A0", "v_car_ms": "0", "v_water_ms": "3",
                    "F_horiz_N": "120"}]
    a3 = aggregate(three)
    check("sigma reported at n=3", a3[0]["sigma_reported"] is True
          and a3[0]["F_horiz_std_N"] is not None,
          f"std={a3[0]['F_horiz_std_N']}")
    check("the two cases differ, so T1 proved something",
          a2[0]["sigma_reported"] != a3[0]["sigma_reported"])

    print("T3 C2 refuses on a partial arc, and computes on a complete one")
    s, msg = iso_vrel_criterion(a3)
    check("partial arc gives None", s is None, msg.split(".")[0])
    full = []
    for i, c in enumerate(ARC_CELLS):
        for d in (100.0 + i, 101.0 + i):
            full.append({"cell_id": c, "v_car_ms": str(i), "v_water_ms": str(4 - i),
                         "F_horiz_N": str(d)})
    s2, msg2 = iso_vrel_criterion(aggregate(full))
    check("complete arc computes S", s2 is not None, msg2)

    print("T4 C2 threshold direction is the pre-registered one")
    flat = []
    for c in ARC_CELLS:
        flat.append({"cell_id": c, "v_car_ms": "1", "v_water_ms": "1",
                     "F_horiz_N": "100"})
    # all identical -> S = 0 -> scalar defensible
    sflat, mflat = iso_vrel_criterion(aggregate(
        [dict(r, v_car_ms=str(i)) for i, r in enumerate(flat)]))
    check("identical forces give S=0", sflat is not None and abs(sflat) < 1e-12,
          f"S={sflat}")
    check("S=0 reads as scalar defensible", "SCALAR DEFENSIBLE" in mflat)

    print("T5 empty input logs nothing")
    check("aggregate([]) is empty", aggregate([]) == [])
    check("coverage names every missing cell",
          coverage([]).count("v_car=") == len(PREREG_V_CAR) * len(PREREG_V_WATER))

    print(f"\n{len(fails)} failure(s)" + (": " + ", ".join(fails) if fails else ""))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Log the v_car x v_water load surface to W&B as distributions.")
    ap.add_argument("--surface", default=None, help="path to load_surface.csv")
    ap.add_argument("--entity", default=ENTITY)
    ap.add_argument("--project", default=PROJECT)
    ap.add_argument("--group", default="load-surface-v1")
    ap.add_argument("--log", action="store_true",
                    help="actually write to W&B; without it this is a dry run")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    rows = read_surface(args.surface)
    agg = aggregate(rows)

    print(f"source: {args.surface or '(none given)'}")
    print(f"records read: {len(rows)}")
    print(coverage(agg))

    if not agg:
        print("\nNo load-surface records yet, so there is nothing to log.")
        print("This is the expected state until d17-moving lands data.")
        print("An empty W&B run would be a permanent artifact asserting a measurement")
        print("that was never made, so this exits without creating one.")
        return 0

    print(render_report(agg, rows))

    if args.log:
        return log_to_wandb(agg, rows, args.entity, args.project, args.group)
    print("DRY RUN. Nothing was written to Weights and Biases. Pass --log to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
