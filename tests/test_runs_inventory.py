"""Tests for data/all_runs_inventory.csv, the store of the 17 gated runs.

These pin the run counts that README.md and FINDINGS.md quote to the data, so a changed inventory
fails here before a stale number reaches a reader.
"""
import csv
from pathlib import Path

INVENTORY = Path(__file__).resolve().parents[1] / "data" / "all_runs_inventory.csv"
ROWS = list(csv.DictReader(INVENTORY.open(encoding="utf-8")))


def test_exactly_17_distinct_runs():
    assert len(ROWS) == 17
    assert len({r["run"] for r in ROWS}) == 17


def test_one_hull_volume():
    # One mesh, the watertight Yaris, in every run.
    assert {r["hull_m3"] for r in ROWS} == {"3.542739"}


def test_three_grids_and_three_masses():
    assert {r["n_grid"] for r in ROWS} == {"48", "64", "96"}
    assert {float(r["mass_kg"]) for r in ROWS} == {1100.0, 1609.0, 2337.0}


def test_passthrough_gate_fails_in_7_runs():
    # FINDINGS.md: particle passthrough (P-2) fails in 7 of the 17 runs at a 10 percent limit.
    over = [r["run"] for r in ROWS if float(r["passthrough_max_frac"]) > 0.10]
    assert len(over) == 7


def test_every_run_is_lighter_than_water():
    # FINDINGS.md: every configuration's realized density is below water's 1000 kg/m3.
    assert all(float(r["realized_rho"]) < 1000.0 for r in ROWS)


def test_no_machine_specific_paths():
    for r in ROWS:
        p = r["summary_path"]
        assert not p.startswith("/"), p
        assert p.startswith("renders/yaris_render_s1/"), p
