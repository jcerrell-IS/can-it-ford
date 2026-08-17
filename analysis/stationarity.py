#!/usr/bin/env python3
"""Stationarity detection and correlated-sample uncertainty for MPM run series.

WHY THIS EXISTS
---------------
`renders/yaris_render_s1/sim_standing.py:154` hard-codes `settle_frames=8`. A
fixed frame count is not a defensible settling criterion, and this project has
already been burned by it: an 8-frame settle sits inside a ~100-frame ring, it
inflated one spread 6.07x -> 1.94x, and it INVERTED a gate ordering between
8-frame and 250-frame arms. Every number in the three-class study was measured
at that settle.

The Undermind report `Settling_and_Force_Reporting_in_Free_Surface_Flow.md`
searched 68 papers and concluded there is no universal frame count. The
defensible protocol is:

    1. detect and exclude the initial (and final) transient,
    2. demonstrate stationarity for the observable actually being reported,
    3. attach uncertainty computed from CORRELATED samples, not from N.

This module implements that protocol with named, citable algorithms so a
reviewer can check the method rather than trust a number.

IMPLEMENTED METHODS AND THEIR SOURCES
-------------------------------------
MSER, Marginal Standard Error Rule, initial-transient truncation
    Bergmann, Morsbach, Ashcroft, Kuegeler 2021, "Statistical Error Estimation
    Methods for Engineering-Relevant Quantities From Scale-Resolving
    Simulations", doi:10.1115/1.4052402

Automated equilibration detection by maximising effectively uncorrelated samples
    Chodera 2015, "A simple method for automated equilibration detection in
    molecular simulations", doi:10.1101/021659

Integrated autocorrelation time and effective sample size
    Straatsma, Berendsen, Stam 1986, doi:10.1080/00268978600100071
    Grossfield et al 2018, doi:10.33011/livecoms.1.1.5067

Blocking / renormalisation-group error on correlated data
    Flyvbjerg and Petersen 1989, doi:10.1063/1.457480

Reverse arrangement test for stationarity
    Pan and Patton 2017, "On Determining Stationary Periods within Time
    Series", doi:10.1175/JTECH-D-17-0038.1

Transient Scanning Technique and Random Uncertainty of the Mean from a single
stationary record, no repeat runs required
    Brouwer, Tukker, Klinkenberg, van Rijsbergen 2019, "Random uncertainty of
    statistical moments in testing: Mean", doi:10.1016/J.OCEANENG.2019.04.068

Autocorrelation beats binning for time-averaging uncertainty
    Syamlal, Celik, Benyahia 2017, doi:10.1002/AIC.15868

A NOTE THAT MATTERS FOR THE GRID STUDY
--------------------------------------
Syamlal et al 2017 state that successive grid refinement may NOT yield
grid-independent TRANSIENT quantities, while time-averaged quantities do
converge on sufficiently fine grids. This project's g48/g64/g96 study reports
`final_disp_mag_m`, an instantaneous end-of-run value, and finds it non-monotone
(+87.8% then -59.2% at 1100 kg). That is the documented expected behaviour for a
transient quantity, not necessarily a solver defect. Report a time-averaged
observable over a demonstrated-stationary window if grid convergence is the
claim being made.

DEPENDENCIES
------------
Pure standard library, deliberately. The repo's other analysis modules import
numpy, but no system interpreter on this Mac has numpy and CI installs only
pytest and pandas. Keeping this dependency-free means it can run as a gate.
Accepts any sequence of floats, including a numpy array.
"""
from __future__ import annotations

import math
from typing import Sequence

__all__ = [
    "autocorrelation",
    "integrated_autocorrelation_time",
    "effective_sample_size",
    "standard_error_correlated",
    "mser_truncation",
    "chodera_equilibration",
    "blocking_error",
    "reverse_arrangement_z",
    "transient_scan",
    "random_uncertainty_of_mean",
    "analyze",
    "format_report",
]


def _as_floats(series: Sequence[float]) -> list[float]:
    out = [float(x) for x in series]
    if not out:
        raise ValueError("empty series")
    return out


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _variance(xs: Sequence[float], ddof: int = 1) -> float:
    n = len(xs)
    if n - ddof <= 0:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - ddof)


def autocorrelation(series: Sequence[float], max_lag: int | None = None
                    ) -> list[float]:
    """Normalised autocorrelation r_k for k = 0..max_lag.

    r_0 is 1 by construction. A constant series has no defined correlation
    structure and returns [1.0] so callers can detect that case.
    """
    xs = _as_floats(series)
    n = len(xs)
    m = _mean(xs)
    denom = sum((x - m) ** 2 for x in xs)
    if denom <= 0.0:
        return [1.0]
    if max_lag is None:
        max_lag = max(1, n // 2)
    max_lag = min(max_lag, n - 1)
    out = []
    for k in range(max_lag + 1):
        num = sum((xs[t] - m) * (xs[t + k] - m) for t in range(n - k))
        out.append(num / denom)
    return out


def integrated_autocorrelation_time(series: Sequence[float]) -> float:
    """tau_int = 1 + 2 * sum_k r_k, truncated at the first non-positive r_k.

    The initial-positive-sequence truncation is the standard automatic window
    (Straatsma 1986; Grossfield 2018). Returns 1.0 for an uncorrelated or
    constant series, so effective sample size degrades to N.
    """
    r = autocorrelation(series)
    if len(r) < 2:
        return 1.0
    total = 0.0
    for k in range(1, len(r)):
        if r[k] <= 0.0:
            break
        total += r[k]
    tau = 1.0 + 2.0 * total
    return max(1.0, tau)


def effective_sample_size(series: Sequence[float]) -> float:
    """N_eff = N / tau_int. The number of genuinely independent samples."""
    xs = _as_floats(series)
    tau = integrated_autocorrelation_time(xs)
    return len(xs) / tau


def standard_error_correlated(series: Sequence[float]) -> float:
    """Standard error of the mean, corrected for serial correlation.

    Using N instead of N_eff here is the single most common way to understate
    uncertainty in a simulation time series.
    """
    xs = _as_floats(series)
    neff = effective_sample_size(xs)
    if neff <= 1.0:
        return float("inf")
    return math.sqrt(_variance(xs) / neff)


def mser_truncation(series: Sequence[float], min_keep: int = 10
                    ) -> tuple[int, float]:
    """Marginal Standard Error Rule truncation point (Bergmann et al 2021).

    Chooses the number of leading samples d to discard that minimises
        MSER(d) = var(x[d:]) / (N - d)
    which is the squared standard error of the retained mean. Returns
    (d, mser_value).
    """
    xs = _as_floats(series)
    n = len(xs)
    best_d, best_v = 0, float("inf")
    upper = max(1, n - min_keep)
    for d in range(0, upper):
        tail = xs[d:]
        k = len(tail)
        if k < 2:
            break
        v = _variance(tail) / k
        if v < best_v:
            best_d, best_v = d, v
    return best_d, best_v


def chodera_equilibration(series: Sequence[float], stride: int = 1
                          ) -> tuple[int, float]:
    """Equilibration point maximising effectively uncorrelated samples.

    Chodera 2015. For each candidate truncation t0, compute
        N_eff(t0) = (N - t0) / tau_int(x[t0:])
    and take the t0 that maximises it. Returns (t0, N_eff at t0).

    `stride` subsamples the candidate set; tau_int is O(n^2) here so a long
    series benefits from stride > 1.
    """
    xs = _as_floats(series)
    n = len(xs)
    best_t0, best_neff = 0, -1.0
    upper = max(1, n - 10)
    for t0 in range(0, upper, max(1, stride)):
        tail = xs[t0:]
        if len(tail) < 10:
            break
        neff = effective_sample_size(tail)
        if neff > best_neff:
            best_t0, best_neff = t0, neff
    return best_t0, best_neff


def blocking_error(series: Sequence[float]) -> list[tuple[int, float, float]]:
    """Flyvbjerg-Petersen blocking transformation (1989).

    Repeatedly average adjacent pairs. At each level report
    (block_size, mean, naive standard error). A plateau in the standard error
    across levels is the signature that correlation has been averaged out, and
    the plateau value is the honest error. Returns levels while at least 4
    blocks remain.
    """
    xs = _as_floats(series)
    out: list[tuple[int, float, float]] = []
    block, size = xs[:], 1
    while len(block) >= 4:
        se = math.sqrt(_variance(block) / len(block)) if len(block) > 1 else 0.0
        out.append((size, _mean(block), se))
        nxt = [(block[i] + block[i + 1]) / 2.0
               for i in range(0, len(block) - 1, 2)]
        block, size = nxt, size * 2
    return out


def reverse_arrangement_z(series: Sequence[float]) -> float:
    """Reverse arrangement test z-score for stationarity (Pan & Patton 2017).

    Counts A, the number of pairs i < j with x_i > x_j. Under a stationary,
    independent record A is asymptotically normal with
        mean = n(n-1)/4
        var  = n(2n^2 + 3n - 5)/72
    A |z| above about 1.96 indicates a monotone trend, so the record is not
    stationary at the 5% level. This test is invariant to a constant offset,
    which is why it survives an arbitrary datum choice.
    """
    xs = _as_floats(series)
    n = len(xs)
    if n < 10:
        return 0.0
    a = 0
    for i in range(n - 1):
        xi = xs[i]
        for j in range(i + 1, n):
            if xi > xs[j]:
                a += 1
    mu = n * (n - 1) / 4.0
    var = n * (2.0 * n * n + 3.0 * n - 5.0) / 72.0
    if var <= 0:
        return 0.0
    return (a - mu) / math.sqrt(var)


def transient_scan(series: Sequence[float], min_keep: int = 10
                   ) -> tuple[int, int]:
    """Transient Scanning Technique, start and end effects (Brouwer et al 2019).

    Trims leading samples by MSER, then trims trailing samples while doing so
    still reduces the squared standard error of the retained mean. Returns
    (start_index, end_index_exclusive) of the retained window.

    Brouwer et al note the TST detects instationarities that visual inspection
    of the time series would miss, which is the relevant failure mode when a
    settle length was chosen by eye.
    """
    xs = _as_floats(series)
    n = len(xs)
    start, _ = mser_truncation(xs, min_keep=min_keep)
    end = n
    while end - start > min_keep:
        cur = xs[start:end]
        cand = xs[start:end - 1]
        if len(cand) < 2:
            break
        if _variance(cand) / len(cand) < _variance(cur) / len(cur):
            end -= 1
        else:
            break
    return start, end


def random_uncertainty_of_mean(series: Sequence[float]) -> float:
    """Random Uncertainty of the Mean from one record (Brouwer et al 2019).

    RUM is the 95% half-width on the mean of a single stationary series,
    obtained from its autocovariance rather than from repeat tests. Computed
    here as 1.96 * sqrt(var / N_eff), the correlated-sample standard error
    scaled to a two-sided 95% interval.

    The point of the method is that repeat runs are expensive; this project has
    exactly that constraint, since a repeat costs GPU allocation.
    """
    se = standard_error_correlated(series)
    return 1.96 * se if math.isfinite(se) else float("inf")


def analyze(series: Sequence[float], label: str = "series") -> dict:
    """Full stationarity and uncertainty report for one observable."""
    xs = _as_floats(series)
    n = len(xs)
    mser_d, _ = mser_truncation(xs)
    chod_t0, chod_neff = chodera_equilibration(xs)
    start, end = transient_scan(xs)
    window = xs[start:end] if end - start >= 2 else xs
    tau = integrated_autocorrelation_time(window)
    neff = effective_sample_size(window)
    z = reverse_arrangement_z(window)
    blocks = blocking_error(window)
    plateau = max((se for _, _, se in blocks), default=0.0)
    return {
        "label": label,
        "n_total": n,
        "mser_discard": mser_d,
        "chodera_t0": chod_t0,
        "chodera_neff": chod_neff,
        "window_start": start,
        "window_end": end,
        "window_len": end - start,
        "mean": _mean(window),
        "std": math.sqrt(_variance(window)),
        "tau_int": tau,
        "n_eff": neff,
        "std_err_correlated": standard_error_correlated(window),
        "rum_95": random_uncertainty_of_mean(window),
        "reverse_arrangement_z": z,
        "stationary_at_5pct": abs(z) < 1.96,
        "blocking_plateau_se": plateau,
        "recommended_discard": max(mser_d, chod_t0, start),
    }


def format_report(rep: dict) -> str:
    """Human-readable one-observable report."""
    stat = "STATIONARY" if rep["stationary_at_5pct"] else "NOT STATIONARY"
    lines = [
        f"observable            {rep['label']}",
        f"samples               {rep['n_total']}",
        f"MSER discard          {rep['mser_discard']}",
        f"Chodera t0            {rep['chodera_t0']}  "
        f"(N_eff {rep['chodera_neff']:.1f})",
        f"retained window       [{rep['window_start']}, {rep['window_end']}) "
        f"= {rep['window_len']} samples",
        f"RECOMMENDED DISCARD   {rep['recommended_discard']} leading samples",
        f"mean                  {rep['mean']:.6g}",
        f"std                   {rep['std']:.6g}",
        f"tau_int               {rep['tau_int']:.3f}",
        f"N_eff                 {rep['n_eff']:.2f}  "
        f"(of {rep['window_len']} raw samples)",
        f"std err (correlated)  {rep['std_err_correlated']:.6g}",
        f"RUM 95% half-width    {rep['rum_95']:.6g}",
        f"reverse-arrangement z {rep['reverse_arrangement_z']:.3f}  -> {stat}",
        f"blocking plateau SE   {rep['blocking_plateau_se']:.6g}",
    ]
    return "\n".join(lines)


def _self_test() -> int:
    """Sanity checks with known answers. Run: python3 analysis/stationarity.py"""
    import random
    random.seed(20260815)
    fails = 0

    def check(name, cond, detail=""):
        nonlocal fails
        if cond:
            print(f"  PASS  {name}")
        else:
            fails += 1
            print(f"  FAIL  {name}  {detail}")

    # 1. white noise: tau_int near 1, N_eff near N, stationary
    wn = [random.gauss(0, 1) for _ in range(500)]
    tau = integrated_autocorrelation_time(wn)
    check("white noise tau_int < 2", tau < 2.0, f"tau={tau:.3f}")
    check("white noise reads stationary", abs(reverse_arrangement_z(wn)) < 1.96)

    # 2. strongly correlated AR(1): tau_int clearly above 1, N_eff well below N
    ar, prev = [], 0.0
    for _ in range(500):
        prev = 0.9 * prev + random.gauss(0, 1)
        ar.append(prev)
    tau_ar = integrated_autocorrelation_time(ar)
    check("AR(1) tau_int > white-noise tau_int", tau_ar > tau,
          f"ar={tau_ar:.2f} wn={tau:.2f}")
    check("AR(1) N_eff < N/2", effective_sample_size(ar) < 250,
          f"neff={effective_sample_size(ar):.1f}")

    # 3. a decaying transient then noise: MSER must discard part of the ramp,
    #    and the trend must be detected as non-stationary on the full record
    trans = [10.0 * math.exp(-t / 5.0) + random.gauss(0, 0.05)
             for t in range(300)]
    d, _ = mser_truncation(trans)
    check("MSER discards a transient", d > 5, f"discard={d}")
    check("full transient record reads NOT stationary",
          abs(reverse_arrangement_z(trans)) >= 1.96,
          f"z={reverse_arrangement_z(trans):.2f}")
    rep = analyze(trans, "decaying transient")
    check("retained window reads stationary after trim",
          rep["stationary_at_5pct"],
          f"z={rep['reverse_arrangement_z']:.2f}")

    # 4. MSER minimises standard error, which is NOT the same as achieving
    #    stationarity. A slowly decaying exponential still carries a residual
    #    trend inside the MSER window, and the reverse-arrangement test must
    #    catch it. This is why analyze() reports BOTH and why a settle length
    #    chosen to stabilise a mean is not evidence the record is stationary.
    slow = [10.0 * math.exp(-t / 12.0) + random.gauss(0, 0.05)
            for t in range(120)]
    s0, s1 = transient_scan(slow)
    check("MSER window can still be non-stationary (both tests needed)",
          abs(reverse_arrangement_z(slow[s0:s1])) >= 1.96,
          "residual trend went undetected, which would defeat the point")

    # 4. correlated error must exceed the naive iid error
    naive = math.sqrt(_variance(ar) / len(ar))
    check("correlated SE > naive SE for AR(1)",
          standard_error_correlated(ar) > naive,
          f"corr={standard_error_correlated(ar):.4f} naive={naive:.4f}")

    # 5. constant series must not crash and must not claim correlation
    check("constant series tau_int == 1",
          integrated_autocorrelation_time([3.0] * 50) == 1.0)

    print()
    print(format_report(analyze(trans, "decaying transient (demo)")))
    return fails


if __name__ == "__main__":
    import sys
    print("stationarity.py self-test")
    n = _self_test()
    print()
    print("FAILURES:", n)
    sys.exit(1 if n else 0)
