"""Tests for check_buoyancy_consistency, the automated Archimedes recomputation.

The point of this check is to end manual buoyancy re-verification, so the tests are
mostly about it being arithmetically right and about it REFUSING to render a verdict.
Nothing here asserts a particular measured deficit: those figures are still moving while
the force-coupled body runs on a canonical arm, and a test pinned to today's numbers
would go stale and then fail for the wrong reason.
"""

import math
import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from analysis.viability_dashboard_scaffold import (  # noqa: E402
    G, RHO_WATER, BuoyancyCase, Coverage, Status, check_buoyancy_consistency,
    format_certificate, run_dashboard, submerged_volume_box,
)


def _case(f_measured, volume, **kw):
    return BuoyancyCase(run_tag="t", f_measured_n=f_measured,
                        submerged_volume_m3=volume, **kw)


# --- the defining property of this check -------------------------------------------------

def test_never_returns_a_verdict():
    """It reports, it does not judge. PASS or FAIL here would be the bug."""
    for f in (0.0, 1.0, 1e6, -1e6, 12345.678):
        r = check_buoyancy_consistency(_case(f, 1.0))
        assert r.status is Status.INDETERMINATE, f"{f} produced {r.status}"


def test_asserts_no_tolerance_ever():
    for f in (0.0, 500.0, -500.0):
        assert check_buoyancy_consistency(_case(f, 2.0)).tolerance is None
    assert check_buoyancy_consistency(None).tolerance is None
    assert check_buoyancy_consistency(_case(1.0, 0.0)).tolerance is None


# --- arithmetic --------------------------------------------------------------------------

def test_exact_agreement_is_zero_error():
    vol, rho, g = 3.5427, RHO_WATER, G
    r = check_buoyancy_consistency(_case(rho * vol * g, vol))
    assert math.isclose(r.value, 0.0, abs_tol=1e-12)
    assert math.isclose(r.detail["f_analytic_n"], rho * vol * g, rel_tol=1e-12)


@pytest.mark.parametrize("frac,expect_pct", [
    (0.70, -30.0), (1.00, 0.0), (1.25, 25.0), (0.5, -50.0), (2.0, 100.0),
])
def test_relative_error_sign_and_magnitude(frac, expect_pct):
    """A shortfall must read NEGATIVE. Sign errors here would invert every reading."""
    vol = 1.7
    analytic = RHO_WATER * vol * G
    r = check_buoyancy_consistency(_case(frac * analytic, vol))
    assert math.isclose(r.value, expect_pct, rel_tol=1e-9, abs_tol=1e-9)


def test_archimedes_identity_at_flotation_equilibrium():
    """At equilibrium the displaced weight equals the body weight, so error is zero.

    This is the timeless form of the identity, stated without any vehicle's mass: pick any
    mass, displace exactly mass/rho of fluid, and the analytic buoyancy is that weight.
    """
    for mass_kg in (256.0, 1100.0, 2337.0):
        vol_displaced = mass_kg / RHO_WATER
        weight = mass_kg * G
        r = check_buoyancy_consistency(_case(weight, vol_displaced))
        assert math.isclose(r.value, 0.0, abs_tol=1e-9)


def test_partial_submersion_uses_displaced_not_total_volume():
    """Scoring a partial run against the fully submerged analytic manufactures a deficit.

    A half-submerged box read against its full volume looks like a 50 percent shortfall
    when it is in fact exact. The check can only be right if it is handed displaced volume.
    """
    L, W, H = 2.0, 1.5, 1.0
    v_total = submerged_volume_box(L, W, H)
    v_half = submerged_volume_box(L, W, H / 2.0)
    assert math.isclose(v_half, v_total / 2.0, rel_tol=1e-12)
    f_true = RHO_WATER * v_half * G
    assert math.isclose(check_buoyancy_consistency(_case(f_true, v_half)).value,
                        0.0, abs_tol=1e-9)
    assert math.isclose(check_buoyancy_consistency(_case(f_true, v_total)).value,
                        -50.0, rel_tol=1e-9)


def test_submerged_volume_box_rejects_negative():
    with pytest.raises(ValueError):
        submerged_volume_box(-1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        submerged_volume_box(1.0, 1.0, float("nan"))


# --- edges and guards --------------------------------------------------------------------

def test_zero_displaced_volume_is_indeterminate_not_a_division():
    r = check_buoyancy_consistency(_case(100.0, 0.0))
    assert r.status is Status.INDETERMINATE
    assert r.value is None
    assert "zero" in r.note.lower()
    assert np.isfinite(r.detail["f_analytic_n"])


def test_no_case_is_not_implemented():
    r = check_buoyancy_consistency(None)
    assert r.status is Status.NOT_IMPLEMENTED
    assert r.coverage is Coverage.RIGID_HELD


@pytest.mark.parametrize("kwargs", [
    {"f_measured": 1.0, "volume": -1.0},
    {"f_measured": float("nan"), "volume": 1.0},
    {"f_measured": 1.0, "volume": float("inf")},
])
def test_rejects_nonsense_inputs(kwargs):
    with pytest.raises(ValueError):
        check_buoyancy_consistency(_case(**kwargs))


def test_rejects_bad_rho_and_g():
    with pytest.raises(ValueError):
        check_buoyancy_consistency(_case(1.0, 1.0, rho_fluid=0.0))
    with pytest.raises(ValueError):
        check_buoyancy_consistency(_case(1.0, 1.0, g=-9.81))


# --- integration with the existing dashboard ---------------------------------------------

def test_g_is_unified_at_9_81():
    """Guards the 0.0342 percent fork from creeping back into rho*V*g."""
    assert G == 9.81


def test_dashboard_includes_the_new_check():
    results = run_dashboard()
    names = [r.name for r in results]
    assert "buoyancy_consistency" in names
    assert len(results) == 7


def test_certificate_renders_with_and_without_a_case():
    """format_certificate must survive value=None, which the zero-volume path returns."""
    for case in (None, _case(1.0, 0.0), _case(9810.0, 1.0)):
        text = format_certificate(run_dashboard(buoyancy=case))
        assert "buoyancy_consistency" in text
        assert "archimedes" in text
