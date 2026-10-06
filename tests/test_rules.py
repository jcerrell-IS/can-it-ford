"""Tests for the L0 depth rule and the L1 AR&R rule, and for the published sweep they produce.

The sweep tests pin the numbers quoted in README.md to the code: if a rule changes, the CSV
and the README must be regenerated together.
"""
import csv
from pathlib import Path

import pytest

from can_it_ford_L0 import DEPTH_THRESHOLD_M, ford_L0
from vehicle_params import AR_R_CLASS_ORDER, AR_R_STABILITY_LIMITS, L1_verdict

SWEEP = Path(__file__).resolve().parents[1] / "data" / "scenario_sweep.csv"


def test_l0_boundary_is_inclusive():
    assert ford_L0(DEPTH_THRESHOLD_M) == "FORD"
    assert ford_L0(DEPTH_THRESHOLD_M + 1e-9) == "NO-FORD"
    assert ford_L0(0.0) == "FORD"


@pytest.mark.parametrize("vehicle_class", AR_R_CLASS_ORDER)
def test_l1_each_limit_trips_on_its_own(vehicle_class):
    lim = AR_R_STABILITY_LIMITS[vehicle_class]
    assert L1_verdict(0.0, 0.0, vehicle_class) == "FORD"
    # Depth cap, at zero velocity so the product cannot trip.
    assert L1_verdict(lim["depth_m"], 0.0, vehicle_class) == "FORD"
    assert L1_verdict(lim["depth_m"] + 0.01, 0.0, vehicle_class) == "NO-FORD"
    # Velocity cap, at a depth small enough that the product stays under its cap.
    d = 0.01
    assert L1_verdict(d, lim["velocity_ms"], vehicle_class) == "FORD"
    assert L1_verdict(d, lim["velocity_ms"] + 0.01, vehicle_class) == "NO-FORD"
    # D x V cap, at a depth under the depth cap.
    d = lim["depth_m"] / 2
    v_edge = lim["haz_m2s"] / d
    assert L1_verdict(d, v_edge, vehicle_class) == "FORD"
    assert L1_verdict(d, v_edge * 1.01, vehicle_class) == "NO-FORD"


def test_l1_rejects_unknown_class():
    with pytest.raises(ValueError):
        L1_verdict(0.1, 0.1, "bicycle")


def _sweep_rows():
    with open(SWEEP, newline="") as fh:
        return list(csv.DictReader(fh))


def test_sweep_matches_the_rules():
    rows = _sweep_rows()
    assert len(rows) == 70
    for r in rows:
        d, v = float(r["depth_m"]), float(r["velocity_ms"])
        assert r["L0_verdict"] == ford_L0(d)
        for c in AR_R_CLASS_ORDER:
            assert r[f"L1_verdict_{c}"] == L1_verdict(d, v, c), (d, v, c)


def test_sweep_headline_counts():
    rows = _sweep_rows()
    ford = {c: sum(r[f"L1_verdict_{c}"] == "FORD" for r in rows) for c in AR_R_CLASS_ORDER}
    assert ford == {"small_passenger": 14, "large_passenger": 19, "large_4wd": 26}
    moved = sum(r["L1_haz_product_only"] == "FORD" and r["L1_verdict_small_passenger"] == "NO-FORD"
                for r in rows)
    reverse = sum(r["L1_haz_product_only"] == "NO-FORD" and r["L1_verdict_small_passenger"] == "FORD"
                  for r in rows)
    assert (moved, reverse) == (23, 0)
