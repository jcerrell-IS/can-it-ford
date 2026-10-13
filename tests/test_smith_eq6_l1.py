"""Pin the result: Smith et al. 2019 Eq. 6 vs L0 / L1 on the 70-cell grid."""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "analysis"))

import smith_eq6_l1 as m  # noqa: E402


def _summary(d_pan=None):
    rows = m.load_grid()
    scored = m.score(rows) if d_pan is None else m.score(rows, d_pan)
    return m.summarise(scored)


def test_grid_is_70_cells_and_63_in_domain():
    s = _summary()
    assert s["n_total"] == 70
    assert s["n_out_of_domain"] == 7
    assert s["n_in_domain"] == 63
    # the excluded cells are exactly the depth-0.1 m row, below the 0.155 m floor pan
    assert {d for d, _ in s["out_of_domain_cells"]} == {0.1}


def test_pinned_counts():
    s = _summary()
    assert s["n_eq6_ford"] == 14
    assert s["n_l1_ford"] == 7
    assert s["n_l0_ford"] == 0
    assert s["l1_ford_subset_of_eq6_ford"] is True


def test_eq6_ford_cells_exact():
    s = _summary()
    expected = {
        (0.2, 0.0), (0.2, 0.5), (0.2, 1.0), (0.2, 1.5), (0.2, 2.0),
        (0.3, 0.0), (0.3, 0.5), (0.3, 1.0), (0.3, 1.5),
        (0.4, 0.0), (0.4, 0.5), (0.4, 1.0),
        (0.5, 0.0), (0.5, 0.5),
    }
    assert set(s["eq6_ford_cells"]) == expected


def test_named_disagreement_cell():
    # at (0.30 m, 1.5 m/s) Eq. 6 says FORD (0.145 < 0.201), L1 says NO-FORD
    assert m.eq6_verdict(0.30, 1.5) == "FORD"
    assert m.eq6_verdict(0.60, 0.0) == "NO-FORD"


def test_float_trap_boundary_is_inclusive_in_l1():
    # 0.2 * 1.5 <= 0.30 is False in raw floats; L1 must still say FORD there
    rows = {(r["depth_m"], r["velocity_ms"]): r for r in m.score(m.load_grid())}
    assert rows[(0.2, 1.5)]["L1"] == "FORD"


def test_sensitivity_to_2010_hull_clearance_is_reported_not_pinned():
    s = _summary(m.COEFFS["D_PAN_HULL_2010_M"][0])
    assert s["n_in_domain"] == 63
    assert s["l1_ford_subset_of_eq6_ford"] is True
