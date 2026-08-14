"""Stationarity detection and correlated-sample uncertainty for simulation time series.

WHY THIS MODULE EXISTS
A 68-paper search at 91 percent coverage established that there is NO universal frame
count and NO universal force-settling threshold for free-surface flow. Asking "how many
frames until the force settles" has no literature answer and never will. What the
literature does supply is a PROTOCOL, and this module implements it:

  1. Detect and EXCLUDE the initial transient.
  2. DEMONSTRATE stationarity for the specific observable being reported, do not assume it.
  3. Attach uncertainty computed from CORRELATED samples, not from the raw sample count.
  4. If there is no steady state, SAY SO and report something else that is real.

SOURCES, and what each one is actually doing here.

  Chodera (2015), "A simple method for automated equilibration detection in molecular
  simulations", DOI 10.1101/021659. Supplies step 1. The equilibration point is chosen
  to MAXIMISE the number of effectively uncorrelated samples that survive discarding,
  N_eff(t0) = (T - t0) / g(t0), rather than by eye or by a fixed burn-in. Also supplies
  the statistical inefficiency g = 1 + 2*tau used throughout.

  Flyvbjerg and Petersen (1989), "Error estimates on averages of correlated data",
  DOI 10.1063/1.457480. Supplies step 3. Repeated pairwise block averaging drives the
  correlation out of the series; the standard error estimate rises and then plateaus,
  and the plateau is the correct error. The naive sigma/sqrt(N) is the value at block
  level 0 and is an UNDERESTIMATE whenever the data are correlated, which for an MPM
  force trace they always are.

  Towing-tank practice supplies the finite-passage case, where no infinite stationary
  record exists and a prespecified interior window must be reported instead:
  Brouwer, Sloof and van Walree (2019), DOI 10.1016/J.OCEANENG.2019.04.068, on random
  uncertainty of statistical moments; Jentzsch, Schmidt and Woszidlo (2021),
  DOI 10.1007/s00348-021-03151-5, on steady and unsteady towing-tank velocities; and
  Thomas, Renilson and Bose (2007), DOI 10.1080/14484846.2007.11464528, on water
  stilling, where the FIRST SLOSHING MODE governs how long to wait between runs.

  For the no-steady-state case the accepted practice in slamming, water entry and
  impact loading is peak distributions, impulses, envelopes, or cycle and event
  statistics with repeat-run uncertainty. An impulse is a legitimate result. A
  fabricated steady force is not.

ENGINE SCOPE. Nothing in this module is engine specific. It consumes a time series and
a timestep. It is written for the warpmpm moving-SDF outputs but makes no warpmpm
assumption and would apply unchanged to a Genesis or Chrono trace.

WHAT THIS MODULE DELIBERATELY DOES NOT DO. It does not invent a settling threshold, it
does not calibrate anything out, and when its own tests fail it returns the failure
rather than a number. `analyse()` returning `stationary=False` is a result to be
reported, not an error to be worked around.

Pure numpy, no scipy, so it runs anywhere the solver runs.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Sequence

import numpy as np

__all__ = [
    "statistical_inefficiency",
    "integrated_autocorrelation_time",
    "detect_equilibration",
    "blocking_curve",
    "blocking_stderr",
    "demonstrate_stationarity",
    "no_steady_state_report",
    "prespecified_window",
    "verdict_probability",
    "analyse",
    "StationarityResult",
]


# ---------------------------------------------------------------------------
# Step 3 ingredient: statistical inefficiency, g = 1 + 2*tau
# ---------------------------------------------------------------------------

def statistical_inefficiency(series, mintime: int = 3) -> float:
    """Statistical inefficiency g = 1 + 2*tau of a scalar series.

    g is the number of correlated samples per effectively independent one. The
    normalised fluctuation autocorrelation C(t) is summed with the (1 - t/N)
    finite-record weighting and truncated at the first non-positive C(t) past
    `mintime`, which is the standard guard against the noisy long-lag tail.

    Returns 1.0 for an uncorrelated series and for a constant series (a constant
    has no fluctuation, so its mean carries no sampling error from correlation).
    """
    a = np.asarray(series, dtype=np.float64).ravel()
    n = a.size
    if n < 2:
        return 1.0
    da = a - a.mean()
    sigma2 = float(np.mean(da * da))
    # RELATIVE zero-variance guard, not an absolute one. np.mean of N identical
    # float64 values is not bitwise exact, so a genuinely constant series leaves a
    # ~1e-16 residue whose autocorrelation is perfectly 1.0 at every lag. An
    # absolute `sigma2 <= 0` test misses that and the sum runs to g ~ N: a constant
    # series was reported as g = 500.0 on a 500-sample input before this guard.
    scale = float(np.mean(a * a))
    eps = np.finfo(np.float64).eps
    if sigma2 <= (8.0 * eps) ** 2 * max(scale, 1.0):
        return 1.0                      # constant to round-off: nothing to correlate
    g = 1.0
    t = 1
    while t < n - 1:
        c = float(np.dot(da[: n - t], da[t:]) / ((n - t) * sigma2))
        if c <= 0.0 and t > mintime:
            break
        g += 2.0 * c * (1.0 - t / n)
        t += 1
    return max(g, 1.0)


def integrated_autocorrelation_time(series, mintime: int = 3) -> float:
    """tau, in samples, from g = 1 + 2*tau."""
    return 0.5 * (statistical_inefficiency(series, mintime=mintime) - 1.0)


# ---------------------------------------------------------------------------
# Step 1: automated equilibration detection (Chodera 2015)
# ---------------------------------------------------------------------------

def detect_equilibration(series, nskip: int = 1, mintime: int = 3,
                         min_retain_frac: float = 0.10,
                         min_retain_samples: int = 32) -> tuple[int, float, float, bool]:
    """Chodera 2015 automated equilibration detection, with a retention floor.

    Scans the discard point t0 and returns the t0 that MAXIMISES the number of
    effectively uncorrelated samples remaining, N_eff = (T - t0) / g(t0). This is
    the whole point of the method: discarding more data removes bias but costs
    samples, and N_eff is the quantity that trades those off explicitly instead of
    leaving it to judgement.

    RETENTION FLOOR, and it is load-bearing. Chodera's method assumes the record
    DOES equilibrate. Applied to one that never does, it discards almost everything:
    on a pure linear ramp of 1500 samples the unconstrained optimum discarded 1484,
    and the surviving 16-sample tail then passed a stationarity test and yielded a
    quoted "steady" mean of 20.013 +/- 0.060 for a series with no steady value at all.
    That is precisely the fabrication this module exists to prevent. t0 is therefore
    capped so at least max(min_retain_frac * n, min_retain_samples) samples survive.

    Hitting that cap is INFORMATION, not an inconvenience: it means the optimiser
    wanted to throw the record away, which is evidence of a non-equilibrating series.
    It is returned as the fourth element, `hit_cap`, and callers must surface it.

    Returns (t0, g, n_eff, hit_cap).
    """
    a = np.asarray(series, dtype=np.float64).ravel()
    n = a.size
    if n < 4:
        return 0, 1.0, float(n), False
    floor_keep = int(max(min_retain_frac * n, min_retain_samples))
    floor_keep = max(4, min(floor_keep, n))
    t0_max = max(n - floor_keep, 0)

    best_t0, best_g, best_neff = 0, 1.0, -np.inf
    unconstrained_t0, unconstrained_neff = 0, -np.inf
    # Stop well short of the end: g estimated from a handful of points is noise.
    for t0 in range(0, max(n - 3, 1), max(int(nskip), 1)):
        seg = a[t0:]
        if seg.size < 4:
            break
        if float(np.var(seg)) <= 0.0:
            # A flat tail is perfectly equilibrated; N_eff is its full length.
            g, neff = 1.0, float(seg.size)
        else:
            g = statistical_inefficiency(seg, mintime=mintime)
            neff = seg.size / g
        if neff > unconstrained_neff:
            unconstrained_t0, unconstrained_neff = t0, neff
        if t0 <= t0_max and neff > best_neff:
            best_t0, best_g, best_neff = t0, g, neff
    hit_cap = bool(unconstrained_t0 > t0_max)
    return int(best_t0), float(best_g), float(best_neff), hit_cap


# ---------------------------------------------------------------------------
# Step 3: correlated-sample uncertainty by blocking (Flyvbjerg and Petersen 1989)
# ---------------------------------------------------------------------------

def blocking_curve(series) -> list[dict]:
    """The Flyvbjerg-Petersen blocking transformation, one row per block level.

    At each level the data are replaced by pairwise averages, halving the sample
    count and doubling the block length. The standard-error estimate at level k is
    s_k = sqrt(var_k / n_k), and its own relative uncertainty is 1/sqrt(2(n_k - 1)),
    which is the error bar F&P attach to the plateau judgement. An odd sample count
    drops its last point before pairing, which is F&P's own prescription.
    """
    x = np.asarray(series, dtype=np.float64).ravel()
    rows = []
    level = 0
    while x.size >= 2:
        n = x.size
        var = float(np.var(x, ddof=1)) if n > 1 else 0.0
        s = float(np.sqrt(var / n)) if n > 0 else 0.0
        rel_err = float(1.0 / np.sqrt(2.0 * (n - 1))) if n > 1 else np.inf
        rows.append({
            "level": level,
            "n_blocks": int(n),
            "block_len": int(2 ** level),
            "stderr": s,
            "stderr_rel_err": rel_err,
            "stderr_abs_err": s * rel_err,
        })
        if n % 2:
            x = x[:-1]
        x = 0.5 * (x[0::2] + x[1::2])
        level += 1
    return rows


def blocking_stderr(series, min_blocks: int = 8) -> dict:
    """Standard error of the mean from the blocking plateau.

    PLATEAU RULE, stated explicitly because F&P describe the plateau qualitatively
    and any automation of it is a choice: the selected level is the FIRST (smallest,
    therefore least noisy) level whose stderr is within one of its own error bars of
    every coarser level that still has at least `min_blocks` blocks. Levels below
    `min_blocks` are excluded from the comparison entirely, because their stderr
    estimates carry >25 percent relative error and would let noise end the search.
    If no level satisfies the rule the coarsest usable level is returned and
    `plateau_found` is False, which is a warning that the record is too short to
    resolve its own correlation time, not a number to quote silently.

    Also returns the naive sigma/sqrt(N) and the ratio between them. That ratio is
    the factor by which an uncorrelated-sample error bar would have been too small,
    and it should be reported: for an MPM force trace it is routinely 3 to 10.
    """
    x = np.asarray(series, dtype=np.float64).ravel()
    n = x.size
    rows = blocking_curve(x)
    naive = float(np.sqrt(np.var(x, ddof=1) / n)) if n > 1 else 0.0

    usable = [r for r in rows if r["n_blocks"] >= min_blocks]
    chosen, found = (rows[-1] if rows else None), False
    for i, r in enumerate(usable):
        coarser = usable[i + 1:]
        if not coarser:
            continue
        if all(r["stderr"] >= c["stderr"] - (r["stderr_abs_err"] + c["stderr_abs_err"])
               for c in coarser):
            chosen, found = r, True
            break
    if chosen is None:
        return {"stderr": 0.0, "naive_stderr": naive, "inflation": 1.0,
                "plateau_level": 0, "plateau_found": False, "n_blocks": int(n),
                "curve": rows}
    se = chosen["stderr"]
    return {
        "stderr": se,
        "stderr_of_stderr": chosen["stderr_abs_err"],
        "naive_stderr": naive,
        "inflation": (se / naive) if naive > 0 else float("nan"),
        "plateau_level": int(chosen["level"]),
        "plateau_found": bool(found),
        "n_blocks": int(chosen["n_blocks"]),
        "curve": rows,
    }


# ---------------------------------------------------------------------------
# Step 2: DEMONSTRATE stationarity, do not assume it
# ---------------------------------------------------------------------------

def demonstrate_stationarity(series, alpha_z: float = 2.0) -> dict:
    """Two independent tests that must BOTH pass before a mean may be quoted.

    Test 1, split-halves. The post-equilibration segment is halved and the two means
    compared using BLOCKING standard errors, not raw-N ones. Using raw N here is the
    classic way to "demonstrate" stationarity that a correlated series can never fail.

    Test 2, trend. An ordinary least-squares slope is fitted and compared against ITS
    OWN standard error, with that standard error inflated by the statistical
    inefficiency of the RESIDUALS so that autocorrelation is accounted for.

    CORRECTED after a known-answer test caught it. An earlier version compared the
    implied end-to-end drift against the standard error of the MEAN, which is wrong
    by a factor of sqrt(12): for OLS on n points, Var(slope) = sigma_eff^2 / S_tt with
    S_tt -> n^3/12, so SD(drift) = SD(slope)*(n-1) -> sqrt(12) * SEM. Measured over 40
    stationary AR(1) records, |drift|/SEM had median 3.44 against sqrt(12) = 3.464, so
    the old test rejected almost every genuinely stationary series at alpha_z = 2. The
    slope is now compared against SD(slope) directly, which needs no such factor.

    alpha_z is the threshold in standard errors, default 2.0 (about 95 percent for a
    normal statistic). It is a stated convention, not a literature constant.
    """
    x = np.asarray(series, dtype=np.float64).ravel()
    n = x.size
    if n < 8:
        return {"stationary": False, "reason": "record shorter than 8 samples",
                "n": int(n)}

    half = n // 2
    lo, hi = x[:half], x[half:]
    se_lo = blocking_stderr(lo)["stderr"]
    se_hi = blocking_stderr(hi)["stderr"]
    denom = float(np.hypot(se_lo, se_hi))
    dmean = float(hi.mean() - lo.mean())
    z_split = abs(dmean) / denom if denom > 0 else (0.0 if dmean == 0 else np.inf)

    t = np.arange(n, dtype=np.float64)
    tc = t - t.mean()
    s_tt = float(np.dot(tc, tc))
    slope = float(np.dot(tc, x - x.mean()) / s_tt) if s_tt > 0 else 0.0
    drift = slope * (n - 1)

    # Standard error of the SLOPE, with the residual autocorrelation folded in via
    # the statistical inefficiency g of the residuals. For white residuals g = 1 and
    # this reduces to the textbook OLS slope error.
    resid = x - (x.mean() + slope * tc)
    dof = max(n - 2, 1)
    resid_var = float(np.dot(resid, resid) / dof)
    g_resid = statistical_inefficiency(resid)
    se_slope = float(np.sqrt(g_resid * resid_var / s_tt)) if s_tt > 0 else 0.0
    z_trend = (abs(slope) / se_slope) if se_slope > 0 else (0.0 if slope == 0 else np.inf)

    ok = bool(z_split <= alpha_z and z_trend <= alpha_z)
    return {
        "stationary": ok,
        "alpha_z": alpha_z,
        "split_half_delta_mean": dmean,
        "split_half_z": float(z_split),
        "split_half_pass": bool(z_split <= alpha_z),
        "ols_slope_per_sample": slope,
        "ols_slope_stderr": se_slope,
        "residual_g": float(g_resid),
        "implied_end_to_end_drift": float(drift),
        "implied_drift_stderr": float(se_slope * (n - 1)),
        "trend_z": float(z_trend),
        "trend_pass": bool(z_trend <= alpha_z),
        "n": int(n),
        "reason": "" if ok else "split-half and/or trend test exceeded alpha_z",
    }


# ---------------------------------------------------------------------------
# Step 4: there is no steady state, so report something else that is real
# ---------------------------------------------------------------------------

def no_steady_state_report(times, series) -> dict:
    """Peak, impulse, envelope and cycle statistics for a series with no steady value.

    This is the accepted reporting mode for slamming, water entry and impact loading,
    where a steady force does not exist and quoting a window mean invents one. The
    impulse is a trapezoid integral and is the physically meaningful integrated
    quantity; the peak and the envelope characterise the extremes; the zero-crossing
    rate and dominant frequency characterise the oscillation.

    Repeat-run uncertainty is NOT computed here because it cannot be: it requires
    independent repeats. The key `repeat_runs_required` is returned as a standing
    reminder that a single record cannot supply it.
    """
    t = np.asarray(times, dtype=np.float64).ravel()
    x = np.asarray(series, dtype=np.float64).ravel()
    n = x.size
    imax = int(np.argmax(x)) if n else 0
    imin = int(np.argmin(x)) if n else 0
    impulse = float(np.trapezoid(x, t)) if n > 1 else 0.0
    absimp = float(np.trapezoid(np.abs(x), t)) if n > 1 else 0.0

    dx = x - x.mean()
    crossings = int(np.sum(np.signbit(dx[:-1]) != np.signbit(dx[1:]))) if n > 1 else 0
    duration = float(t[-1] - t[0]) if n > 1 else 0.0
    zcr = (crossings / duration) if duration > 0 else float("nan")

    dom_f = float("nan")
    if n >= 8 and duration > 0:
        dt = duration / (n - 1)
        spec = np.abs(np.fft.rfft(dx * np.hanning(n)))
        freqs = np.fft.rfftfreq(n, d=dt)
        if spec.size > 1:
            dom_f = float(freqs[1 + int(np.argmax(spec[1:]))])

    return {
        "steady_state": False,
        "peak_value": float(x[imax]) if n else float("nan"),
        "peak_time": float(t[imax]) if n else float("nan"),
        "min_value": float(x[imin]) if n else float("nan"),
        "min_time": float(t[imin]) if n else float("nan"),
        "peak_to_peak": float(x.max() - x.min()) if n else float("nan"),
        "peak_to_trough_ratio": (float(abs(x.max() / x.min()))
                                 if n and x.min() != 0 else float("nan")),
        "impulse": impulse,
        "absolute_impulse": absimp,
        "mean_over_record": float(x.mean()) if n else float("nan"),
        "record_duration": duration,
        "zero_crossing_rate_hz": zcr,
        "dominant_frequency_hz": dom_f,
        "repeat_runs_required": True,
        "note": ("No steady value exists for this record. Quote the impulse or the "
                 "peak distribution. Do NOT quote mean_over_record as a steady force; "
                 "it is returned only so an envelope can be drawn around it."),
    }


# ---------------------------------------------------------------------------
# The finite moving passage: a PRESPECIFIED window, with sensitivities
# ---------------------------------------------------------------------------

def prespecified_window(times, series,
                        t_start: float, t_end: float,
                        edge_fracs: Sequence[float] = (0.05, 0.10, 0.20),
                        filter_widths: Sequence[int] = (1, 3, 5, 9)) -> dict:
    """Report a prespecified constant-speed interior window with its sensitivities.

    Towing-tank practice for a finite passage: there is no infinite stationary record,
    so a window is DECLARED IN ADVANCE and reported together with how much the answer
    moves when the window edges and the smoothing filter are varied. A window mean
    quoted without those two sensitivities is not a measurement, it is a choice.

    Acceleration waves and force oscillations can persist inside a nominally
    constant-speed window, so `interior_stationarity` is run and returned. A window
    that fails it should be reported through no_steady_state_report instead.

    The window MUST be prespecified. Passing edges chosen after seeing the trace
    reintroduces exactly the freedom this protocol exists to remove.
    """
    t = np.asarray(times, dtype=np.float64).ravel()
    x = np.asarray(series, dtype=np.float64).ravel()
    sel = (t >= t_start) & (t <= t_end)
    if sel.sum() < 8:
        return {"ok": False, "reason": "fewer than 8 samples inside the window",
                "n_in_window": int(sel.sum())}

    xw = x[sel]
    blk = blocking_stderr(xw)
    stat = demonstrate_stationarity(xw)

    span = t_end - t_start
    win_sens = []
    # BOTH symmetric and one-sided trims. Symmetric trimming alone is provably blind
    # to a linear trend: the mean of a linear function over an interval symmetric
    # about its centre is the centre value, unchanged by any symmetric trim. Measured
    # on x = 3 + 0.5t over [2, 8], symmetric trims of 0, 5, 10 and 20 percent all give
    # exactly 5.500000, while one-sided trims give 5.575, 5.650 and 5.800. Reporting
    # only the symmetric spread would certify a drifting window as insensitive.
    for f in edge_fracs:
        for mode, s2 in (
            ("symmetric", (t >= t_start + f * span) & (t <= t_end - f * span)),
            ("trim_head", (t >= t_start + f * span) & (t <= t_end)),
            ("trim_tail", (t >= t_start) & (t <= t_end - f * span)),
        ):
            if s2.sum() >= 8:
                win_sens.append({"trim_frac": float(f), "mode": mode,
                                 "n": int(s2.sum()), "mean": float(x[s2].mean())})
    means = [w["mean"] for w in win_sens] + [float(xw.mean())]
    win_spread = float(max(means) - min(means)) if len(means) > 1 else 0.0
    sym_means = [w["mean"] for w in win_sens if w["mode"] == "symmetric"] + [float(xw.mean())]
    win_spread_symmetric = float(max(sym_means) - min(sym_means)) if len(sym_means) > 1 else 0.0

    filt_sens = []
    for w in filter_widths:
        w = int(w)
        if w <= 1:
            filt_sens.append({"width": 1, "mean": float(xw.mean())})
            continue
        if xw.size < w:
            continue
        k = np.ones(w) / w
        sm = np.convolve(xw, k, mode="valid")
        filt_sens.append({"width": w, "mean": float(sm.mean())})
    fmeans = [f["mean"] for f in filt_sens]
    filt_spread = float(max(fmeans) - min(fmeans)) if len(fmeans) > 1 else 0.0

    return {
        "ok": True,
        "window": [float(t_start), float(t_end)],
        "n_in_window": int(sel.sum()),
        "mean": float(xw.mean()),
        "stderr_correlated": blk["stderr"],
        "stderr_naive": blk["naive_stderr"],
        "stderr_inflation": blk["inflation"],
        "plateau_found": blk["plateau_found"],
        "interior_stationarity": stat,
        "window_sensitivity": win_sens,
        "window_sensitivity_spread": win_spread,
        "window_sensitivity_spread_symmetric_only": win_spread_symmetric,
        "filter_sensitivity": filt_sens,
        "filter_sensitivity_spread": filt_spread,
        "sensitivity_exceeds_stderr": bool(
            max(win_spread, filt_spread) > 2.0 * blk["stderr"] if blk["stderr"] > 0
            else max(win_spread, filt_spread) > 0),
        "note": ("This is a PROTOCOL, not a transferable run length. The window must be "
                 "prespecified. If sensitivity_exceeds_stderr is True the quoted error "
                 "bar is dominated by the analyst's window and filter choice, not by "
                 "the simulation, and must be reported that way."),
    }


# ---------------------------------------------------------------------------
# The verdict itself: probabilistic and record-length dependent
# ---------------------------------------------------------------------------

def verdict_probability(condition, hold_frames: int = 3,
                        n_boot: int = 2000, seed: int = 0,
                        block_len: int | None = None) -> dict:
    """Reframe a hold-for-k-consecutive-frames verdict as a probability.

    Incipient motion is probabilistic and record-length dependent. The literature
    defines a movement probability or activity rate with detection uncertainty, not a
    single critical stress. A criterion of the form "joint condition held for 3
    consecutive frames" turns a continuous margin into a binary at an arbitrary
    record length, and the project already has a canonical arm sitting at
    margin_frames 0 and another one frame from flipping.

    Reported instead:
      activity_rate     fraction of frames satisfying the condition
      longest_run       longest consecutive satisfied run, in frames
      margin_frames     hold_frames - longest_run, clipped at 0; 0 means it triggered,
                        and a POSITIVE value is how far it is from triggering
      p_trigger         moving-block bootstrap probability that a record of THIS
                        length, with this autocorrelation, contains a qualifying run
      record_frames     stated every time, because the probability is meaningless
                        without it

    The bootstrap resamples CONTIGUOUS BLOCKS, not individual frames, so the
    autocorrelation that makes consecutive-frame criteria easy to satisfy is
    preserved. An i.i.d. frame bootstrap would destroy it and report a p_trigger
    that is far too low.
    """
    c = np.asarray(condition).astype(bool).ravel()
    n = c.size
    if n == 0:
        return {"record_frames": 0, "activity_rate": float("nan"),
                "longest_run": 0, "margin_frames": int(hold_frames),
                "triggered": False, "p_trigger": float("nan")}

    def longest_true_run(b: np.ndarray) -> int:
        best = cur = 0
        for v in b:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        return best

    longest = longest_true_run(c)
    triggered = bool(longest >= hold_frames)

    # Block length from the condition's own correlation time, so the bootstrap is
    # not given a free parameter chosen by hand.
    if block_len is None:
        g = statistical_inefficiency(c.astype(np.float64))
        block_len = int(max(2, min(n // 4, round(g))))
    block_len = int(max(1, min(block_len, max(n // 2, 1))))

    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_len))
    hits = 0
    for _ in range(int(n_boot)):
        starts = rng.integers(0, max(n - block_len + 1, 1), size=n_blocks)
        samp = np.concatenate([c[s:s + block_len] for s in starts])[:n]
        if longest_true_run(samp) >= hold_frames:
            hits += 1
    p = hits / float(n_boot)

    return {
        "record_frames": int(n),
        "hold_frames": int(hold_frames),
        "activity_rate": float(c.mean()),
        "longest_run": int(longest),
        "margin_frames": int(max(hold_frames - longest, 0)),
        "triggered": triggered,
        "p_trigger": float(p),
        "bootstrap_block_len": int(block_len),
        "n_boot": int(n_boot),
        "note": ("p_trigger is conditional on this record length and this "
                 "autocorrelation. It is not a property of the physics alone and must "
                 "never be quoted without record_frames."),
    }


# ---------------------------------------------------------------------------
# The whole protocol in one call
# ---------------------------------------------------------------------------

@dataclass
class StationarityResult:
    """Everything the protocol requires, in one object, including its own failures."""
    n_samples: int
    dt: float
    t0_frames: int
    t0_time: float
    discarded_frac: float
    g: float
    tau_frames: float
    n_eff: float
    stationary: bool
    mean: float = float("nan")
    stderr: float = float("nan")
    naive_stderr: float = float("nan")
    stderr_inflation: float = float("nan")
    plateau_found: bool = False
    plateau_level: int = -1
    equilibration_hit_cap: bool = False
    stationarity: dict = field(default_factory=dict)
    fallback: dict = field(default_factory=dict)
    reportable: str = ""

    def as_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        if self.stationary:
            return ("mean = %.6g +/- %.3g (correlated SEM; naive would have been %.3g, "
                    "a factor %.2f too small). Equilibration discarded %d of %d frames "
                    "(%.1f%%); g = %.2f, tau = %.2f frames, N_eff = %.1f."
                    % (self.mean, self.stderr, self.naive_stderr, self.stderr_inflation,
                       self.t0_frames, self.n_samples, 100.0 * self.discarded_frac,
                       self.g, self.tau_frames, self.n_eff))
        return ("NO STEADY STATE DEMONSTRATED over %d frames. %s Report the impulse "
                "(%.6g) or the peak (%.6g at t = %.4g s) instead of a mean."
                % (self.n_samples, self.stationarity.get("reason", ""),
                   self.fallback.get("impulse", float("nan")),
                   self.fallback.get("peak_value", float("nan")),
                   self.fallback.get("peak_time", float("nan"))))


def analyse(series, dt: float = 1.0, alpha_z: float = 2.0,
            nskip: int = 1) -> StationarityResult:
    """Run the full protocol on one observable and return its result, pass or fail.

    Order matters and follows the protocol exactly: detect and discard the initial
    transient FIRST (Chodera 2015), then demonstrate stationarity on what remains,
    and only then attach a correlated-sample error bar (Flyvbjerg and Petersen 1989).
    Attaching an error bar to a non-stationary segment is the failure this ordering
    exists to prevent, so when the stationarity test fails no mean or stderr is
    returned at all; the no-steady-state report is returned in their place.
    """
    x = np.asarray(series, dtype=np.float64).ravel()
    n = x.size
    t = np.arange(n, dtype=np.float64) * dt

    t0, g, neff, hit_cap = detect_equilibration(x, nskip=nskip)
    seg = x[t0:]
    stat = demonstrate_stationarity(seg, alpha_z=alpha_z)

    # A record whose equilibration search wanted to discard past the retention floor
    # is not a record with a long transient, it is a record that never settles. Treat
    # it as non-stationary regardless of what the surviving tail looks like, because a
    # short tail of a drifting series will pass a stationarity test by having too few
    # samples to resolve its own slope.
    if hit_cap:
        stat = dict(stat)
        stat["stationary"] = False
        stat["reason"] = ((stat.get("reason") or "").strip()
                          + " Equilibration search hit the retention floor, so the "
                            "record does not equilibrate within its own length.").strip()

    res = StationarityResult(
        n_samples=int(n), dt=float(dt), t0_frames=int(t0), t0_time=float(t0 * dt),
        discarded_frac=float(t0 / n) if n else 0.0,
        g=float(g), tau_frames=0.5 * (g - 1.0), n_eff=float(neff),
        stationary=bool(stat.get("stationary", False)),
        equilibration_hit_cap=bool(hit_cap),
        stationarity=stat,
    )

    if res.stationary:
        blk = blocking_stderr(seg)
        res.mean = float(seg.mean())
        res.stderr = blk["stderr"]
        res.naive_stderr = blk["naive_stderr"]
        res.stderr_inflation = blk["inflation"]
        res.plateau_found = blk["plateau_found"]
        res.plateau_level = blk["plateau_level"]
        res.reportable = "mean_with_correlated_stderr"
    else:
        # Fall back on the FULL record, not the post-t0 segment: when there is no
        # steady state the "equilibration point" has no meaning, and the impulse of
        # a truncated record is not the impulse of the event.
        res.fallback = no_steady_state_report(t, x)
        res.reportable = "impulse_or_peak_distribution"
    return res
