"""Known-answer tests for analysis/stationarity.py.

Every test here has an answer derivable ANALYTICALLY, not one recorded from a
previous run of this same code. A test that only asserts "the output equals what it
output last time" cannot catch a wrong estimator, and this module's whole purpose is
to be trusted for a number that goes into a paper.

The analytic anchors used:

  AR(1), x_t = phi*x_{t-1} + eps_t, has integrated autocorrelation time
  tau = phi/(1 - phi) and statistical inefficiency g = 1 + 2*tau = (1+phi)/(1-phi).
  For phi = 0.8 that is exactly g = 9, and the correlated standard error of the mean
  is sqrt(g) = 3 times the naive sigma/sqrt(N). Both are checked.

  White noise has g = 1 and no inflation.

  A half-sine pulse sin(pi*t/T) on [0, T] has impulse exactly 2T/pi.

Runs under pytest, and also standalone (`python tests/test_stationarity.py`) because
pytest is not guaranteed present on a TACC compute node.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))

import stationarity as st  # noqa: E402


# ---------------------------------------------------------------------------
# generators with known theoretical properties
# ---------------------------------------------------------------------------

def ar1(n, phi, seed=0, sigma=1.0):
    """AR(1) drawn from its stationary distribution, so there is no burn-in to
    confound an equilibration test."""
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = rng.normal(0.0, sigma / np.sqrt(1.0 - phi * phi))
    for i in range(1, n):
        x[i] = phi * x[i - 1] + rng.normal(0.0, sigma)
    return x


def ar1_theory_g(phi):
    return (1.0 + phi) / (1.0 - phi)


# ---------------------------------------------------------------------------
# statistical inefficiency
# ---------------------------------------------------------------------------

def test_g_white_noise_is_one():
    x = np.random.default_rng(1).normal(size=8000)
    g = st.statistical_inefficiency(x)
    assert 0.85 <= g <= 1.25, g


def test_g_ar1_matches_theory():
    for phi in (0.5, 0.8, 0.9):
        x = ar1(60000, phi, seed=2)
        g = st.statistical_inefficiency(x)
        theory = ar1_theory_g(phi)
        # Finite-record truncated sums are biased low; 25 percent is generous but
        # still fails an estimator that is wrong by a factor.
        assert abs(g - theory) / theory < 0.25, (phi, g, theory)


def test_g_constant_series_is_one_not_nan():
    g = st.statistical_inefficiency(np.full(500, 3.14159))
    assert g == 1.0, g


def test_tau_consistent_with_g():
    x = ar1(20000, 0.8, seed=3)
    g = st.statistical_inefficiency(x)
    tau = st.integrated_autocorrelation_time(x)
    assert abs((1.0 + 2.0 * tau) - g) < 1e-12


# ---------------------------------------------------------------------------
# blocking (Flyvbjerg and Petersen 1989)
# ---------------------------------------------------------------------------

def test_blocking_curve_halves_each_level():
    rows = st.blocking_curve(np.arange(1000, dtype=float))
    for a, b in zip(rows, rows[1:]):
        assert b["n_blocks"] == a["n_blocks"] // 2, (a, b)
        assert b["block_len"] == 2 * a["block_len"]


def test_blocking_white_noise_no_inflation():
    x = np.random.default_rng(4).normal(size=8192)
    r = st.blocking_stderr(x)
    naive = x.std(ddof=1) / np.sqrt(x.size)
    assert abs(r["naive_stderr"] - naive) / naive < 1e-9
    assert 0.7 < r["inflation"] < 1.5, r["inflation"]


def test_blocking_ar1_inflation_matches_sqrt_g():
    phi = 0.8
    x = ar1(65536, phi, seed=5)
    r = st.blocking_stderr(x)
    expected = np.sqrt(ar1_theory_g(phi))          # = 3.0 exactly for phi = 0.8
    assert abs(r["inflation"] - expected) / expected < 0.30, (r["inflation"], expected)
    # The whole point: the naive error bar is too small for correlated data.
    assert r["stderr"] > r["naive_stderr"]
    assert r["plateau_found"], r


def test_blocking_stderr_beats_naive_on_correlated_data():
    x = ar1(16384, 0.9, seed=6)
    r = st.blocking_stderr(x)
    assert r["inflation"] > 2.0, r["inflation"]


# ---------------------------------------------------------------------------
# equilibration detection (Chodera 2015)
# ---------------------------------------------------------------------------

def test_equilibration_discards_a_transient():
    n, tau = 4000, 200.0
    t = np.arange(n)
    transient = 25.0 * np.exp(-t / tau)            # decays to <1% by ~5 tau = 1000
    x = transient + np.random.default_rng(7).normal(size=n) * 0.5
    t0, g, neff, hit_cap = st.detect_equilibration(x, nskip=5)
    assert t0 > 200, t0                            # it must discard something real
    assert t0 < 2500, t0                           # but not throw the record away
    # The retained segment must be flat: its first-to-last-decile drift should be
    # small against its own scatter.
    seg = x[t0:]
    d = abs(seg[: len(seg) // 10].mean() - seg[-len(seg) // 10:].mean())
    assert d < 3.0 * seg.std(), (d, seg.std())


def test_equilibration_keeps_an_already_equilibrated_record():
    x = ar1(4000, 0.5, seed=8)
    t0, g, neff, hit_cap = st.detect_equilibration(x, nskip=5)
    assert t0 < 0.25 * len(x), t0                  # nothing to discard, so discard little


def test_equilibration_short_record_is_safe():
    t0, g, neff, hit_cap = st.detect_equilibration(np.array([1.0, 2.0]))
    assert t0 == 0 and g == 1.0


def test_equilibration_retention_floor_catches_a_never_settling_record():
    """Regression guard on the worst bug this module had. Unconstrained, Chodera's
    N_eff maximiser discarded 1484 of 1500 frames of a pure ramp, and the 16-frame
    tail then PASSED the stationarity test, so analyse() reported a steady mean of
    20.013 +/- 0.060 for a series with no steady value. The retention floor must both
    keep enough samples and raise hit_cap."""
    n = 1500
    x = np.linspace(0.0, 20.0, n) + np.random.default_rng(13).normal(size=n) * 0.2
    t0, g, neff, hit_cap = st.detect_equilibration(x)
    assert hit_cap, "a pure ramp must trip the retention floor"
    assert n - t0 >= 0.10 * n, (t0, n)
    r = st.analyse(x, dt=1.0 / 30.0)
    assert r.equilibration_hit_cap
    assert not r.stationary
    assert np.isnan(r.mean)


def test_equilibration_floor_does_not_fire_on_a_normal_transient():
    """The floor must not turn every record with a transient into a failure."""
    n, tau = 4000, 200.0
    x = 25.0 * np.exp(-np.arange(n) / tau) + np.random.default_rng(19).normal(size=n) * 0.5
    t0, g, neff, hit_cap = st.detect_equilibration(x, nskip=5)
    assert not hit_cap, t0


# ---------------------------------------------------------------------------
# demonstrated stationarity
# ---------------------------------------------------------------------------

def test_stationarity_passes_on_white_noise():
    r = st.demonstrate_stationarity(np.random.default_rng(9).normal(size=4000))
    assert r["stationary"], r


def test_stationarity_fails_on_linear_drift():
    n = 2000
    x = np.linspace(0.0, 10.0, n) + np.random.default_rng(10).normal(size=n) * 0.1
    r = st.demonstrate_stationarity(x)
    assert not r["stationary"], r
    assert not r["trend_pass"], r


def test_stationarity_fails_on_a_step_change():
    x = np.concatenate([np.zeros(1000), np.ones(1000) * 5.0])
    x = x + np.random.default_rng(11).normal(size=2000) * 0.1
    r = st.demonstrate_stationarity(x)
    assert not r["stationary"], r
    assert not r["split_half_pass"], r


def test_stationarity_uses_correlated_errors_not_raw_n():
    """A correlated series with a real step must still be caught, and an ordinary
    correlated series with no step must not be falsely rejected. Using raw-N error
    bars would reject the second one, because raw N understates the error."""
    x = ar1(8000, 0.9, seed=12)
    r = st.demonstrate_stationarity(x)
    assert r["stationary"], r


def test_stationarity_false_rejection_rate_is_low():
    """The property that matters is the FALSE REJECTION RATE on genuinely stationary
    records, and one seed cannot measure a rate. At alpha_z = 2 the target is about
    5 percent per test; this asserts a generous ceiling so the suite is not flaky,
    while still failing hard on a mis-scaled statistic. The pre-fix trend test, which
    compared implied drift against the standard error of the MEAN rather than the
    slope against its own, rejected roughly every stationary record here."""
    ok = sum(st.demonstrate_stationarity(ar1(4000, 0.7, seed=100 + s))["stationary"]
             for s in range(20))
    assert ok >= 16, "only %d of 20 stationary AR(1) records passed" % ok


def test_trend_test_scales_with_slope_error_not_sem():
    """Direct regression guard on the sqrt(12) bug: for a stationary AR(1) the
    trend statistic must sit near 1, not near 3.5."""
    zs = [st.demonstrate_stationarity(ar1(4000, 0.7, seed=200 + s))["trend_z"]
          for s in range(20)]
    assert float(np.median(zs)) < 2.0, float(np.median(zs))


# ---------------------------------------------------------------------------
# no steady state
# ---------------------------------------------------------------------------

def test_impulse_of_half_sine_matches_analytic():
    T = 2.0
    t = np.linspace(0.0, T, 20001)
    x = np.sin(np.pi * t / T)
    r = st.no_steady_state_report(t, x)
    analytic = 2.0 * T / np.pi
    assert abs(r["impulse"] - analytic) / analytic < 1e-4, (r["impulse"], analytic)
    assert abs(r["peak_time"] - T / 2.0) < 1e-3
    assert abs(r["peak_value"] - 1.0) < 1e-6


def test_dominant_frequency_recovered():
    f0, fs, dur = 5.0, 200.0, 20.0
    t = np.arange(0.0, dur, 1.0 / fs)
    x = np.sin(2.0 * np.pi * f0 * t)
    r = st.no_steady_state_report(t, x)
    assert abs(r["dominant_frequency_hz"] - f0) < 0.3, r["dominant_frequency_hz"]


def test_analyse_routes_drift_to_the_fallback():
    n = 1500
    x = np.linspace(0.0, 20.0, n) + np.random.default_rng(13).normal(size=n) * 0.2
    r = st.analyse(x, dt=1.0 / 30.0)
    assert not r.stationary
    assert r.reportable == "impulse_or_peak_distribution"
    assert np.isnan(r.mean), r.mean            # no mean may be quoted
    assert r.fallback and "impulse" in r.fallback
    assert "NO STEADY STATE" in r.summary()


def test_analyse_reports_a_mean_when_stationary():
    x = 7.0 + ar1(6000, 0.7, seed=14)
    r = st.analyse(x, dt=1.0 / 30.0)
    assert r.stationary, r.stationarity
    assert r.reportable == "mean_with_correlated_stderr"
    assert abs(r.mean - 7.0) < 5.0 * r.stderr, (r.mean, r.stderr)
    assert r.stderr > r.naive_stderr           # correlation inflates the bar
    assert "+/-" in r.summary()


# ---------------------------------------------------------------------------
# prespecified window
# ---------------------------------------------------------------------------

def test_prespecified_window_on_stationary_signal():
    t = np.arange(0.0, 10.0, 0.01)
    x = 3.0 + np.random.default_rng(15).normal(size=t.size) * 0.05
    r = st.prespecified_window(t, x, 2.0, 8.0)
    assert r["ok"]
    assert abs(r["mean"] - 3.0) < 0.02
    assert r["interior_stationarity"]["stationary"]
    assert r["window_sensitivity_spread"] < 0.05


def test_prespecified_window_flags_a_trending_interior():
    t = np.arange(0.0, 10.0, 0.01)
    x = 3.0 + 0.5 * t + np.random.default_rng(16).normal(size=t.size) * 0.02
    r = st.prespecified_window(t, x, 2.0, 8.0)
    assert r["ok"]
    assert not r["interior_stationarity"]["stationary"], r["interior_stationarity"]
    assert r["sensitivity_exceeds_stderr"]


def test_symmetric_trimming_alone_is_blind_to_a_linear_trend():
    """Pins the reason one-sided trims exist. For a linear ramp the symmetric-only
    spread is exactly zero, so a sensitivity report built from symmetric trims alone
    would certify a drifting window as insensitive. The one-sided trims must see it."""
    t = np.arange(0.0, 10.0, 0.01)
    x = 3.0 + 0.5 * t
    r = st.prespecified_window(t, x, 2.0, 8.0)
    assert r["window_sensitivity_spread_symmetric_only"] < 1e-9, r
    assert r["window_sensitivity_spread"] > 0.1, r["window_sensitivity_spread"]


def test_prespecified_window_refuses_a_too_short_window():
    t = np.arange(0.0, 10.0, 1.0)
    x = np.ones_like(t)
    r = st.prespecified_window(t, x, 2.0, 4.0)
    assert not r["ok"]


# ---------------------------------------------------------------------------
# probabilistic verdict
# ---------------------------------------------------------------------------

def test_verdict_all_true_triggers_with_probability_one():
    r = st.verdict_probability(np.ones(100, dtype=bool), hold_frames=3, n_boot=300)
    assert r["triggered"] and r["margin_frames"] == 0
    assert r["p_trigger"] == 1.0
    assert r["activity_rate"] == 1.0
    assert r["record_frames"] == 100


def test_verdict_all_false_never_triggers():
    r = st.verdict_probability(np.zeros(100, dtype=bool), hold_frames=3, n_boot=300)
    assert not r["triggered"]
    assert r["margin_frames"] == 3
    assert r["p_trigger"] == 0.0


def test_verdict_margin_frames_counts_distance_from_flipping():
    c = np.zeros(100, dtype=bool)
    c[10:12] = True                       # longest run is 2, one short of 3
    r = st.verdict_probability(c, hold_frames=3, n_boot=300)
    assert r["longest_run"] == 2
    assert r["margin_frames"] == 1
    assert not r["triggered"]


def test_verdict_probability_is_bounded_and_reports_record_length():
    rng = np.random.default_rng(17)
    c = rng.random(200) < 0.4
    r = st.verdict_probability(c, hold_frames=3, n_boot=500)
    assert 0.0 <= r["p_trigger"] <= 1.0
    assert r["record_frames"] == 200
    assert r["bootstrap_block_len"] >= 1


def test_verdict_block_bootstrap_preserves_correlation():
    """A clustered condition must give a HIGHER trigger probability than an
    unclustered one with the same activity rate. This is the property an i.i.d.
    frame bootstrap would destroy, and it is the reason the block bootstrap is
    used, so it gets an explicit test."""
    n = 600
    clustered = np.zeros(n, dtype=bool)
    for s in range(0, n, 60):
        clustered[s:s + 18] = True                  # 30 percent, in runs of 18
    rng = np.random.default_rng(18)
    scattered = np.zeros(n, dtype=bool)
    scattered[rng.choice(n, size=clustered.sum(), replace=False)] = True
    assert clustered.mean() == scattered.mean()
    pc = st.verdict_probability(clustered, hold_frames=8, n_boot=600, seed=1)
    ps = st.verdict_probability(scattered, hold_frames=8, n_boot=600, seed=1)
    assert pc["p_trigger"] > ps["p_trigger"], (pc["p_trigger"], ps["p_trigger"])


def test_verdict_empty_record_is_safe():
    r = st.verdict_probability(np.zeros(0, dtype=bool))
    assert r["record_frames"] == 0


# ---------------------------------------------------------------------------
# standalone runner, so this works without pytest on a compute node
# ---------------------------------------------------------------------------

def _main():
    fns = [(k, v) for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = []
    for name, fn in fns:
        try:
            fn()
            print("PASS %s" % name)
        except AssertionError as e:
            failed.append((name, e))
            print("FAIL %s : %s" % (name, e))
        except Exception as e:                      # noqa: BLE001
            failed.append((name, e))
            print("ERROR %s : %r" % (name, e))
    print("\n%d passed, %d failed, of %d" % (len(fns) - len(failed), len(failed), len(fns)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
