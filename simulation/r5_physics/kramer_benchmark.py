"""Read the Kramer 2021 benchmark series and reduce it to gradeable numbers.

WHY THIS EXISTS
---------------
`docs/R5_PHYSICS_BLOCKED_FLAGS.md` FLAG-2a recorded the benchmark time series as
unfetchable, which made half of Option B's definition of done ungradeable and forced
job C's pass criteria down to self-consistency only. **The series is now on disk.** It
was fetched 2026-08-17 by driving a real browser to the article page, which the
publisher serves normally; every prior attempt had used curl, WebFetch or a resolver,
all of which MDPI answers with 403. That is FLAG-2's own lesson (a licence status is not
a fetch status) with one more entry: **a host-level bot filter is not an access barrier,
and the difference is whether a real browser was ever tried.**

Nothing here is transcribed. Every number this module reports is recomputed from the
files each time it runs, because a figure that cannot be re-derived is not a figure.

THE DATA
--------
`Datafile/Experimental results/` in `energies-14-00269-s001.zip`, sha256
04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f, held OUTSIDE the repo
at /Users/josie/can-it-ford-refs/2026-08-16/ because the repo is public and E8 is
unresolved. 27 files: for each drop height {01D, 03D, 05D}, four repetitions in Raw and
Normalized form, plus a CI95 series. That matches Table 1's H0 = {30, 90, 150} mm and
the paper's "four repetitions were carried out for each drop height".

Raw columns:        t [s], x3 [m], WG1 [m], WG2 [m], WG3 [m]
Normalized columns: t/Te0, x3/H0m, WG1/H0m, WG2/H0m, WG3/H0m
CI95 columns:       t/Te0, mean x3/H0m, lower 95% bound, upper 95% bound

x3 is the heave displacement; WG1-3 are wave gauges. Release is t = 0; each series
begins at t/Te0 = -0.5, i.e. the hold phase is included.

`Datafile/Numerical results/` EXTRACTED 2026-08-18, from the same archive, and never
opened before that date (`git grep -I -l FNPF` across every local branch head returned
zero). It holds the ELEVEN independent codes that were run blind on this same case:
FNPF1, LPF0 to LPF4, RANS1 to RANS5.

    THE DESIGN IS UNBALANCED AND THE IMBALANCE IS ONE CODE.
    31 series, not 33. RANS3 ships 05D only, with no 01D and no 03D. Measured live
    by `numerical_inventory()`, which discovers what is on disk rather than asserting
    a shape. Every 01D and 03D cross-code statistic below is therefore over TEN codes
    and says so in its own `n_codes` field. Silently dropping RANS3 would have made the
    01D and 03D rows look like the 05D row.

    WG1-3 ARE ON FOUR CODES OF ELEVEN, not on all of them.
    Only RANS2, RANS3, RANS4 and RANS5 carry the five-column form. FNPF1, LPF0-4 and
    **RANS1** are two columns, t and x3. This is not a corruption and not an oversight
    on our side: the paper's own Appendix A says the WG columns "are included for the
    experimental results and for certain numerical results". On the experimental side
    they are on all 24 Measured files and on none of the 3 CI95 files, which are four
    columns. See `wg_inventory()` and `wg_verdict()`.

THE TRAP IN Te0, WHICH COST ME A WRONG CLAIM
--------------------------------------------
`Te0` recovers from t / (t/Te0) as **0.756100 s, identical across all three drop heights
and all four repetitions**. It is therefore a single fixed NORMALISING CONSTANT, not a
per-drop measurement. Reading it as "the measured natural period" would contradict the
paper's own Figure 13 finding that the damped period rises with drop height, and would
be exactly the kind of number that looks measured because it came out of a data file.
The damped periods are measured here from the displacement series instead.

WHY THE DECAY STATISTIC IS BRACKETED BY ZERO CROSSINGS
------------------------------------------------------
The eleven codes were written to a case, not to a sampling convention. Their records run
from 951 to 19,468 rows over 6.0 to 10.0 s, a **20x range in sample density**, and the
RANS records are not even uniformly spaced in time (RANS3's first three stamps are
0.000000, 0.005677, 0.006884). A peak picked with any fixed-width window would therefore
resolve a densely sampled code's extremum more sharply than a sparse one's, and because
the sparse codes here are the potential-flow ones and the dense ones are the RANS ones,
that artefact would have landed as a clean FNPF/LPF-versus-RANS damping trend. It would
have looked like physics. It would have been the row count.

So every extremum below is bracketed between two linearly interpolated zero crossings,
which are defined by the signal and not by the grid, and refined by an exact quadratic
through the three samples nearest the bracket's argmax. The first release peak at t = 0
is deliberately NOT among them: it is not bracketed by two crossings, and it is the
imposed drop height rather than a response, so including it would import the
nominal-versus-measured release-height difference straight into the decay fit.

THE ELEVEN CODES ALL RELEASE FROM THE NOMINAL H0. THE EXPERIMENT DID NOT.
Every numerical series starts at exactly {0.030, 0.090, 0.150} m. The measured releases
are {29.22, 90.32, 149.37} mm for repetition 1 (Table 4 gives the four-repetition means
as {29.16, 89.18, 150.06} mm). The largest gap is 01D at +2.68% of H0. On PERIOD this is
negligible and quantified: the measured dT/dH0 between 01D and 03D is 0.367 s/m, so
0.78 mm of release-height difference moves the first damped period by 0.29 ms, 0.036% of
it. On AMPLITUDE it is not negligible and every absolute-mm comparison below carries it.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

REFS = Path("/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001/Datafile")
DEFAULT_ROOT = REFS / "Experimental results"
NUM_ROOT = REFS / "Numerical results"

ZIP_SHA256 = "04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f"

# Drop label -> H0 in metres, from Table 1. The labels are the paper's own.
DROPS = {"01D": 0.030, "03D": 0.090, "05D": 0.150}
REPS = (1, 2, 3, 4)

# The eleven blind-test codes, and the fidelity family the paper groups them into
# (Section 1.2 / Appendix C). Order is the paper's own directory order.
CODES = ("FNPF1", "LPF0", "LPF1", "LPF2", "LPF3", "LPF4",
         "RANS1", "RANS2", "RANS3", "RANS4", "RANS5")
FAMILY = {c: ("FNPF" if c.startswith("FNPF") else
              "LPF" if c.startswith("LPF") else "RANS") for c in CODES}

# Table 1 constants, for the closed-form stiffness. Benchmark gravity, not the engine's:
# this module describes the EXPERIMENT, so it uses the experiment's g.
RHO_W = 998.2
G_BENCHMARK = 9.82
D_SPHERE = 0.300
M_SPHERE = 7.056

# How much of each record the shared statistic uses. Both are bounded by the SHORTEST
# record in the whole set: the smallest crossing count measured over all 43 series
# (31 numerical + 12 experimental) is 15, which supports 14 bracketed extrema, so 6 is
# inside every one of them with room to spare. Held identical for experiment and codes,
# because a statistic applied to the codes but not to the experiment is not a comparison.
N_CYCLES = 5        # successive damped-period estimates, the pre-existing convention
N_EXTREMA = 6       # bracketed extrema entering the decay-envelope fit, i.e. 3 periods


# --------------------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------------------
def _load(root: Path, drop: str, rep: int, kind: str) -> np.ndarray:
    p = root / f"{drop}_Measured{rep}_{kind}.txt"
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found. Extract the supplementary archive first:\n"
            f"  unzip -d <dir> energies-14-00269-s001.zip 'Datafile/Experimental results/*'\n"
            f"and pass --root <dir>/'Datafile/Experimental results'.")
    return np.loadtxt(p, skiprows=1)


def _num_path(num_root: Path, code: str, drop: str) -> Path:
    return num_root / code / f"{drop}_{code}.txt"


def _load_numerical(num_root: Path, code: str, drop: str) -> np.ndarray:
    """One blind-test series. Two OR five columns; the caller must not assume which."""
    p = _num_path(num_root, code, drop)
    if not p.exists():
        raise FileNotFoundError(f"{p} not found. Extract 'Datafile/Numerical results/*'.")
    return np.loadtxt(p, skiprows=1)


def numerical_inventory(num_root: Path = NUM_ROOT) -> dict:
    """What is ACTUALLY on disk, per code and drop. Measured, never assumed.

    This function exists because the dispatch that commissioned this work described the
    set as eleven codes at three drop heights each, i.e. 33 series, and it is 31.
    """
    present, missing, ncols = {}, [], {}
    for code in CODES:
        got = []
        for drop in DROPS:
            p = _num_path(num_root, code, drop)
            if p.exists():
                got.append(drop)
                with open(p) as fh:
                    fh.readline()
                    ncols[(code, drop)] = len(fh.readline().split())
            else:
                missing.append(f"{code}/{drop}")
        present[code] = tuple(got)
    return {
        "n_codes": len(CODES),
        "n_series": sum(len(v) for v in present.values()),
        "n_series_if_balanced": len(CODES) * len(DROPS),
        "present": {k: list(v) for k, v in present.items()},
        "missing": missing,
        "codes_with_all_three_drops": [c for c, v in present.items() if len(v) == len(DROPS)],
        "columns": {f"{c}/{d}": n for (c, d), n in sorted(ncols.items())},
    }


def wg_inventory(root: Path = DEFAULT_ROOT, num_root: Path = NUM_ROOT) -> dict:
    """Which series carry WG1-3, on both sides. Column counts read from the files."""
    num = numerical_inventory(num_root)
    with_wg = sorted(k for k, n in num["columns"].items() if n >= 5)
    without = sorted(k for k, n in num["columns"].items() if n < 5)
    exp = {}
    for drop in DROPS:
        for rep in REPS:
            for kind in ("Raw", "Normalized"):
                d = _load(root, drop, rep, kind)
                exp[f"{drop}_Measured{rep}_{kind}"] = int(d.shape[1])
        d = np.loadtxt(root / f"{drop}_CI95_Normalized.txt", skiprows=1)
        exp[f"{drop}_CI95_Normalized"] = int(d.shape[1])
    codes_with = sorted({k.split("/")[0] for k in with_wg})
    return {
        "numerical_series_with_wg": with_wg,
        "numerical_series_without_wg": without,
        "n_numerical_with_wg": len(with_wg),
        "n_numerical_total": num["n_series"],
        "codes_with_wg": codes_with,
        "codes_without_wg": [c for c in CODES if c not in codes_with],
        "n_codes_with_wg": len(codes_with),
        "experimental_columns": exp,
        "experimental_measured_all_have_wg": all(
            v == 5 for k, v in exp.items() if "Measured" in k),
        "experimental_ci95_have_wg": any(v >= 5 for k, v in exp.items() if "CI95" in k),
    }


# --------------------------------------------------------------------------------------
# the shared reduction: identical code path for the experiment and for all eleven codes
# --------------------------------------------------------------------------------------
def _crossings(t: np.ndarray, y: np.ndarray) -> tuple:
    """Linearly interpolated zero crossings of y, and the sample index before each."""
    idx = np.where(np.diff(np.sign(y)) != 0)[0]
    tc = np.array([t[i] + (t[i + 1] - t[i]) * (-y[i]) / (y[i + 1] - y[i]) for i in idx])
    return idx, tc


def _periods_from(t: np.ndarray, y: np.ndarray, n_cycles: int = N_CYCLES) -> np.ndarray:
    """Successive damped periods from zero crossings. A crossing-to-crossing interval is
    a HALF period, hence the factor 2. Unchanged from the pre-2026-08-18 version of this
    module, so the experimental numbers it already published are reproduced exactly."""
    _, tc = _crossings(t, y)
    return (np.diff(tc) * 2.0)[:n_cycles]


def _extrema(t: np.ndarray, y: np.ndarray, n: int) -> tuple:
    """First `n` extrema of y, each bracketed between two interpolated zero crossings.

    Sampling-rate agnostic by construction: the bracket is set by the signal's own
    crossings, not by a window in samples. Inside the bracket the argmax is refined with
    an exact quadratic through its three neighbouring samples, which removes the residual
    O(dt^2) dependence on where the grid happened to fall relative to the peak. See the
    module docstring for why a fixed-width picker would have manufactured a
    potential-flow-versus-RANS damping trend out of a 20x row-count range.

    Returns (times, |amplitudes|, signs). The t = 0 release peak is not included.
    """
    idx, _ = _crossings(t, y)
    tt, aa, ss = [], [], []
    for k in range(min(n, len(idx) - 1)):
        lo, hi = idx[k] + 1, idx[k + 1] + 1          # samples strictly inside the bracket
        if hi <= lo:
            continue
        seg = y[lo:hi + 1]
        j = lo + int(np.argmax(np.abs(seg)))
        if 0 < j < len(y) - 1:
            t3 = t[j - 1:j + 2] - t[j]
            y3 = y[j - 1:j + 2]
            a, b, c = np.polyfit(t3, y3, 2)
            if a != 0.0:
                dt = -b / (2.0 * a)
                # refuse a vertex that leaves the three-sample support: fall back to the
                # sample itself rather than extrapolate a peak that was never bracketed
                if t3[0] <= dt <= t3[2]:
                    tt.append(float(t[j] + dt))
                    aa.append(abs(float(c - b * b / (4.0 * a))))
                    ss.append(int(np.sign(y[j])))
                    continue
        tt.append(float(t[j]))
        aa.append(abs(float(y[j])))
        ss.append(int(np.sign(y[j])))
    return np.array(tt), np.array(aa), np.array(ss)


def decay_envelope(t_ext: np.ndarray, a_ext: np.ndarray) -> dict:
    """Exponential decay envelope through the bracketed extrema.

    A least-squares fit of ln|A| against peak time over ALL the extrema in the window,
    rather than a decrement between one chosen pair, so no single noisy peak sets the
    answer. `r2` is reported because the decay here is amplitude-dependent (that is the
    paper's own Fig 13 finding) and a single exponential is therefore a CHARACTERISATION
    of the window, not a linear system identification. A low r2 is information, not a
    failure: it says the record is strongly nonlinear over these three periods.

    T_fit comes from the extrema themselves, (n-1) half periods between the first and
    last, so the decrement and the damping ratio are internally consistent with the same
    window the slope was fitted over.
    """
    if len(t_ext) < 3:
        return {"n": int(len(t_ext)), "ok": False}
    ln = np.log(a_ext)
    slope, intercept = np.polyfit(t_ext, ln, 1)
    pred = slope * t_ext + intercept
    ss_res = float(((ln - pred) ** 2).sum())
    ss_tot = float(((ln - ln.mean()) ** 2).sum())
    sigma = float(-slope)
    t_fit = float(2.0 * (t_ext[-1] - t_ext[0]) / (len(t_ext) - 1))
    omega_d = 2.0 * math.pi / t_fit
    return {
        "n": int(len(t_ext)),
        "ok": True,
        "decay_rate_per_s": sigma,
        "period_over_fit_window_s": t_fit,
        "log_decrement_per_cycle": float(sigma * t_fit),
        "damping_ratio_zeta": float(sigma / math.sqrt(omega_d ** 2 + sigma ** 2)),
        "envelope_r2": float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan"),
        "first_extremum_amp_m": float(a_ext[0]),
    }


def reduce_series(t: np.ndarray, x: np.ndarray, n_cycles: int = N_CYCLES,
                  n_extrema: int = N_EXTREMA) -> dict:
    """THE shared statistic. Every row of every table below comes through this function.

    Equilibrium is the mean of the last 15% of the record rather than 0.0, because the
    sphere settles a few tens of micrometres off the nominal waterline (Table 1's mass is
    rounded, which alone implies a ~2 um offset) and a hard zero would bias early
    crossings. The window is a fraction of each record, so it lands at a different
    absolute time for a 6 s record than for a 10 s one; every series here is settled well
    before 85% of its own length, and `settled_level_m` is returned so that assumption is
    checkable rather than buried.
    """
    eq = float(x[int(0.85 * len(x)):].mean())
    y = x - eq
    post = t >= 0.0
    tp, yp = t[post], y[post]
    per = _periods_from(tp, yp, n_cycles)
    te, ae, se = _extrema(tp, yp, n_extrema)
    env = decay_envelope(te, ae)
    k = RHO_W * G_BENCHMARK * math.pi * (0.5 * D_SPHERE) ** 2
    t1 = float(per[0]) if len(per) else float("nan")
    a33 = k * (t1 / (2.0 * math.pi)) ** 2 - M_SPHERE
    trough = float(ae[0]) if len(ae) else float("nan")
    crest = float(ae[1]) if len(ae) > 1 else float("nan")
    return {
        "release_amp_m": float(yp[0]),
        "settled_level_m": eq,
        "n_samples": int(len(t)),
        "n_crossings": int(len(_crossings(tp, yp)[0])),
        "first_damped_period_s": t1,
        "cycle_periods_s": [float(v) for v in per],
        "implied_added_mass_kg": float(a33),
        "implied_a33_over_m": float(a33 / M_SPHERE),
        "first_trough_amp_m": trough,
        "first_crest_amp_m": crest,
        "first_trough_over_release": trough / abs(float(yp[0])),
        "extrema_times_s": [float(v) for v in te],
        "extrema_amps_m": [float(v) for v in ae],
        "decay": env,
    }


def damped_periods(root: Path, drop: str, rep: int, n_cycles: int = N_CYCLES) -> np.ndarray:
    """Back-compatible wrapper. Kept because the pre-2026-08-18 API is referenced in
    docs/R5_PHYSICS_BENCHMARK_UNBLOCKED.md."""
    d = _load(root, drop, rep, "Raw")
    x = d[:, 1]
    eq = float(x[int(0.85 * len(x)):].mean())
    y = x - eq
    post = d[:, 0] >= 0.0
    return _periods_from(d[post, 0], y[post], n_cycles)


# --------------------------------------------------------------------------------------
# experiment
# --------------------------------------------------------------------------------------
def recover_te0(root: Path) -> dict:
    """Recover the normalising constant, and PROVE it is constant rather than assume it.

    The check matters: if Te0 ever differed by drop height it would be a measurement,
    and every period below would have to be interpreted differently.
    """
    vals = {}
    for drop in DROPS:
        for rep in REPS:
            raw = _load(root, drop, rep, "Raw")
            nor = _load(root, drop, rep, "Normalized")
            m = np.abs(nor[:, 0]) > 1e-9
            vals[(drop, rep)] = float(np.median(raw[m, 0] / nor[m, 0]))
    arr = np.array(list(vals.values()))
    return {
        "te0_s": float(np.median(arr)),
        "te0_spread_s": float(arr.max() - arr.min()),
        "is_constant_across_drops_and_reps": bool(arr.max() - arr.min() < 1e-6),
        "n_series": len(arr),
    }


def ci95_halfwidth(root: Path, drop: str) -> dict:
    """The published uncertainty, read off the CI95 series in its own units.

    This is the direct test of how the abstract's "on average only about 0.3% of the
    respective drop heights" should be read. The file is NORMALIZED by H0, so a
    half-width expressed in those units is by construction a fraction of drop height.
    """
    p = root / f"{drop}_CI95_Normalized.txt"
    d = np.loadtxt(p, skiprows=1)
    half = (d[:, 3] - d[:, 2]) / 2.0          # (upper - lower)/2, in units of H0
    h0 = DROPS[drop]
    return {
        "mean_halfwidth_frac_of_H0": float(half.mean()),
        "mean_halfwidth_pct_of_H0": float(half.mean() * 100.0),
        "mean_halfwidth_mm": float(half.mean() * h0 * 1000.0),
        "max_halfwidth_pct_of_H0": float(half.max() * 100.0),
        "n_samples": int(len(half)),
    }


def experiment(root: Path = DEFAULT_ROOT) -> dict:
    """The four repetitions per drop, each through `reduce_series`."""
    out = {}
    for drop in DROPS:
        reps = {}
        for rep in REPS:
            d = _load(root, drop, rep, "Raw")
            reps[rep] = reduce_series(d[:, 0], d[:, 1])
        t1 = np.array([reps[r]["first_damped_period_s"] for r in REPS])
        sg = np.array([reps[r]["decay"]["decay_rate_per_s"] for r in REPS])
        ld = np.array([reps[r]["decay"]["log_decrement_per_cycle"] for r in REPS])
        tr = np.array([reps[r]["first_trough_amp_m"] for r in REPS])
        rel = np.array([reps[r]["release_amp_m"] for r in REPS])
        out[drop] = {
            "reps": reps,
            "first_damped_period_s": _stat(t1),
            "decay_rate_per_s": _stat(sg),
            "log_decrement_per_cycle": _stat(ld),
            "first_trough_amp_m": _stat(tr),
            "release_amp_m": _stat(rel),
            "implied_a33_over_m": float(np.mean(
                [reps[r]["implied_a33_over_m"] for r in REPS])),
            "ci95": ci95_halfwidth(root, drop),
        }
    return out


def _stat(a: np.ndarray) -> dict:
    a = np.asarray(a, dtype=float)
    return {"n": int(a.size), "mean": float(a.mean()), "min": float(a.min()),
            "max": float(a.max()), "spread": float(a.max() - a.min()),
            "std": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "spread_pct_of_mean": float(100.0 * (a.max() - a.min()) / a.mean())
            if a.mean() != 0 else float("nan")}


# --------------------------------------------------------------------------------------
# the eleven codes
# --------------------------------------------------------------------------------------
def _family_spreads(rows: dict) -> dict:
    """Spread within each fidelity family separately.

    The paper draws this line itself (Section 4: the LPF and partly the FNPF models
    "should be used with care in applications with motions of very large amplitudes,
    whereas the RANS models, if proper convergence is reached, are capable of producing
    accurate results for all drop heights"). Pooling all eleven into one spread lets the
    two amplitude-blind linear models set the width, so both readings are reported and
    neither is presented as THE spread.
    """
    out = {}
    for fam in ("FNPF", "LPF", "RANS"):
        mem = [c for c in rows if rows[c]["family"] == fam]
        if not mem:
            continue
        t1 = np.array([rows[c]["first_damped_period_s"] for c in mem])
        sg = np.array([rows[c]["decay"]["decay_rate_per_s"] for c in mem])
        dv = np.array([abs(rows[c]["dev_period_pct"]) for c in mem])
        tr = np.array([abs(rows[c]["dev_first_trough_mm"]) for c in mem])
        out[fam] = {"members": mem, "n": len(mem),
                    "first_damped_period_s": _stat(t1),
                    "decay_rate_per_s": _stat(sg),
                    "max_abs_dev_period_pct": float(dv.max()),
                    "max_abs_dev_first_trough_mm": float(tr.max())}
    return out


def intercode(root: Path = DEFAULT_ROOT, num_root: Path = NUM_ROOT) -> dict:
    """Every code reduced with the SAME statistic as the four experimental repeats.

    RANS3 is absent at 01D and 03D. It is reported as absent in `codes_absent` and
    excluded from those two rows' spreads, and every spread carries its own `n_codes`.
    """
    exp = experiment(root)
    inv = numerical_inventory(num_root)
    out = {"inventory": inv, "drops": {}}
    for drop in DROPS:
        rows, absent = {}, []
        for code in CODES:
            if drop not in inv["present"][code]:
                absent.append(code)
                continue
            d = _load_numerical(num_root, code, drop)
            r = reduce_series(d[:, 0], d[:, 1])
            r["family"] = FAMILY[code]
            r["has_wg"] = bool(d.shape[1] >= 5)
            e = exp[drop]
            r["dev_period_pct"] = 100.0 * (
                r["first_damped_period_s"] / e["first_damped_period_s"]["mean"] - 1.0)
            r["dev_decay_rate_pct"] = 100.0 * (
                r["decay"]["decay_rate_per_s"] / e["decay_rate_per_s"]["mean"] - 1.0)
            r["dev_first_trough_mm"] = 1000.0 * (
                r["first_trough_amp_m"] - e["first_trough_amp_m"]["mean"])
            r["dev_first_trough_pct_of_H0"] = 100.0 * (
                r["first_trough_amp_m"] - e["first_trough_amp_m"]["mean"]) / DROPS[drop]
            # The paper normalises by each repetition's OWN measured drop height, which
            # "practically eliminates deviations between repetitions" (Section 4). The
            # eleven codes all released from the nominal H0 and the experiment did not,
            # so the absolute-mm column above carries that offset and this one does not.
            exp_norm = float(np.mean([e["reps"][rp]["first_trough_over_release"]
                                      for rp in REPS]))
            r["exp_first_trough_over_release"] = exp_norm
            r["dev_first_trough_norm_pct_of_H0"] = 100.0 * (
                r["first_trough_over_release"] - exp_norm)
            rows[code] = r
        t1 = np.array([rows[c]["first_damped_period_s"] for c in rows])
        sg = np.array([rows[c]["decay"]["decay_rate_per_s"] for c in rows])
        a33 = np.array([rows[c]["implied_a33_over_m"] for c in rows])
        dev = np.array([abs(rows[c]["dev_period_pct"]) for c in rows])
        out["drops"][drop] = {
            "codes": rows,
            "codes_absent": absent,
            "n_codes": len(rows),
            "spread_first_damped_period_s": _stat(t1),
            "spread_decay_rate_per_s": _stat(sg),
            "spread_implied_a33_over_m": _stat(a33),
            "max_abs_dev_period_pct": float(dev.max()),
            "median_abs_dev_period_pct": float(np.median(dev)),
            "by_family": _family_spreads(rows),
            "experiment": {
                "first_damped_period_s": exp[drop]["first_damped_period_s"],
                "decay_rate_per_s": exp[drop]["decay_rate_per_s"],
                "log_decrement_per_cycle": exp[drop]["log_decrement_per_cycle"],
                "first_trough_amp_m": exp[drop]["first_trough_amp_m"],
                "implied_a33_over_m": exp[drop]["implied_a33_over_m"],
                "ci95": exp[drop]["ci95"],
            },
        }
    return out


# --------------------------------------------------------------------------------------
# placing an external force-ratio error against the published inter-code spread
# --------------------------------------------------------------------------------------
def force_error_as_period_error(force_ratio_excess: float,
                                a33_over_m: float = 0.5) -> dict:
    """Convert a HYDROSTATIC vertical-force ratio error into an implied period error.

    THIS IS AN ATTRIBUTION, NOT A MEASUREMENT, and both defensible attributions are
    returned rather than one being chosen silently. Job B is a pinned-sphere hydrostatic
    check: `R5_PHYSICS_BATCH_MANIFEST.md` criterion 3 grades the steady vertical reaction
    against 69.2180 N of analytic buoyancy. The eleven codes are compared here on damped
    PERIOD, because that is what a free-decay record measures. Nothing in the benchmark
    converts one into the other for free.

        T = 2*pi*sqrt((m + a33)/k),   k = rho*g*pi*R^2

    so the bridge is whatever the force error does to k, and that depends on WHERE the
    error is:

      * SCALE. The error is in the rho*g product, or in the coupling's force
        normalisation, i.e. anything that multiplies the buoyant force without changing
        the geometry. Then k carries the same factor one for one, and
        e_T = 1/sqrt(1+f) - 1.
      * GEOMETRY. The error is an isotropic error in the sphere's effective radius in the
        solver. Then F ~ R^3 while k ~ R^2, so a force excess f implies a radius excess
        (1+f)^(1/3) - 1 and a stiffness excess (1+f)^(2/3) - 1, which is SMALLER. This is
        the most forgiving of the two and is the one to quote when the claim is that a
        number is an outlier.

    Both are returned. The added-mass route is deliberately NOT offered: at a33/m = 0.5 a
    1% period error becomes a ~6% error in a33, so routing a force error through a33
    inflates the equivalent by about six and is the wrong bridge for a hydrostatic check,
    which contains no added mass at all.
    """
    f = force_ratio_excess
    e_scale = 1.0 / math.sqrt(1.0 + f) - 1.0
    k_geom = (1.0 + f) ** (2.0 / 3.0)
    e_geom = 1.0 / math.sqrt(k_geom) - 1.0
    m_eff = 1.0 + a33_over_m
    e_am_for_1pct = ((1.01 ** 2) * m_eff - 1.0) / a33_over_m - 1.0
    return {
        "force_ratio_excess": f,
        "scale_attribution": {
            "what": "error multiplies the buoyant force, k carries it one for one",
            "stiffness_excess_frac": f,
            "equivalent_period_error_pct": 100.0 * e_scale,
        },
        "geometry_attribution": {
            "what": "isotropic effective-radius error, F ~ R^3 but k ~ R^2",
            "implied_radius_excess_pct": 100.0 * ((1.0 + f) ** (1.0 / 3.0) - 1.0),
            "stiffness_excess_frac": k_geom - 1.0,
            "equivalent_period_error_pct": 100.0 * e_geom,
        },
        "added_mass_route_amplification_per_1pct_period": 100.0 * e_am_for_1pct,
        "note": ("an attribution, not a measurement; the geometry route is the smaller "
                 "equivalent and is therefore the conservative one for an outlier claim"),
    }


# --------------------------------------------------------------------------------------
# can WG1-3 separate radiation damping from viscous damping?
# --------------------------------------------------------------------------------------
def hydrostatic_pe(z: float, r: float = 0.5 * D_SPHERE, rho_w: float = RHO_W,
                   g: float = G_BENCHMARK) -> float:
    """EXACT hydrostatic potential energy of a half-submerged sphere raised z above
    equilibrium. NOT 0.5*k*z^2.

    THIS CORRECTION IS NOT COSMETIC AND IT IS LARGEST EXACTLY WHERE THE BENCHMARK IS
    HARDEST. The linear form assumes a waterplane area that does not change, and over a
    150 mm displacement of a 300 mm sphere the waterplane goes to ZERO: at H0 = 0.5D the
    sphere's bottom pole sits exactly on the free surface at release and the submerged
    volume is 0.0000 of its equilibrium value. Measured overstatement of 0.5*k*z^2:
    +0.67% at 01D, +6.38% at 03D, +20.00% at 05D. Using the linear form would have put a
    20% error straight into the 05D radiated fraction, in the direction that makes the
    non-radiated share look larger.

        V(z) = pi*(R-z)^2*(2R+z)/3            spherical cap still submerged
        U(z) = rho*g*[ (2/3)pi R^3 z - (pi/3)( (3/4)R^4 - R(R-z)^3 + (R-z)^4/4 ) ]

    Valid for 0 <= z <= R. Above R the sphere is clear of the water and the restoring
    force is the constant weight, so U grows linearly; the benchmark never goes there.
    """
    z = min(abs(z), r)
    return rho_w * g * ((2.0 / 3.0) * math.pi * r ** 3 * z
                        - (math.pi / 3.0) * ((3.0 / 4.0) * r ** 4
                                             - r * (r - z) ** 3
                                             + (r - z) ** 4 / 4.0))


def radiated_energy_budget(t: np.ndarray, x: np.ndarray, wg: np.ndarray,
                           radii, te0_s: float = 0.7561) -> dict:
    """Energy the body lost, against energy that crossed each gauge circle.

    TWO THINGS HERE ARE EASY TO GET WRONG AND BOTH WERE, IN THE FIRST VERSION.

    1. THE ENERGY IS NOT 0.5*k*A^2. See hydrostatic_pe. At the largest drop the linear
       form is 20% high.
    2. THE TWO WINDOWS ARE NOT THE SAME WINDOW. Energy that has crossed radius r by the
       end of the record was shed by the body roughly r/c_g EARLIER, because that is how
       long the group front takes to get there. Comparing a full-record wave integral
       against a full-record body loss counts wave energy the body had not yet shed at
       the far gauge, and the offset is 3.02 s at WG1 against a 6.05 s record. Each gauge
       therefore gets its OWN body window, ending at T_end - r/c_g. This is not a
       refinement: it is the difference between three gauges that agree and three that do
       not, and it works in the direction that reduces their disagreement.

    The body's envelope amplitude at an arbitrary time comes from log-linear interpolation
    through the bracketed extrema, which is exact for an exponential envelope and the
    envelope fits at r2 >= 0.998.

    1 - fraction is everything not radiated: viscous dissipation, separation, and any
    measurement or modelling error that lands in neither term.
    """
    m = t >= 0.0
    tt = t[m]
    eq = float(x[int(0.85 * len(x)):].mean())
    y = (x - eq)[m]
    c_g = G_BENCHMARK * te0_s / (4.0 * math.pi)
    # every extremum in the record, not only the fit window
    te, ae, _ = _extrema(tt, y, 10 ** 6)
    a0 = abs(float(y[0]))
    e0 = hydrostatic_pe(a0)

    def amp_at(tq):
        """Envelope amplitude at time tq, log-linear through the measured extrema."""
        if tq <= te[0]:
            return float(ae[0])
        if tq >= te[-1]:
            return float(ae[-1])
        return float(np.exp(np.interp(tq, te, np.log(ae))))

    out = {"E0_J": float(e0), "release_amp_m": a0, "c_group_m_s": c_g,
           "n_extrema_in_record": int(len(te)),
           "wavelength_m": G_BENCHMARK * te0_s ** 2 / (2.0 * math.pi),
           "record_end_s": float(tt[-1]),
           "E0_linear_J": float(0.5 * RHO_W * G_BENCHMARK * math.pi
                                * (0.5 * D_SPHERE) ** 2 * a0 ** 2),
           "gauges": {}}
    out["linear_pe_overstatement_pct"] = 100.0 * (out["E0_linear_J"] / e0 - 1.0)
    fracs = []
    for i, r in enumerate(radii):
        eta = wg[m, i]
        integral = float(np.trapezoid(eta ** 2, tt))
        e_rad = 2.0 * math.pi * r * RHO_W * G_BENCHMARK * c_g * integral
        t_body = float(tt[-1]) - r / c_g
        e_body_end = hydrostatic_pe(amp_at(t_body))
        d_e = e0 - e_body_end
        out["gauges"][f"WG{i+1}"] = {
            "radius_m": r, "radius_in_wavelengths": r / out["wavelength_m"],
            "group_transit_s": r / c_g,
            "body_window_end_s": t_body,
            "eta2_integral_m2s": integral,
            "E_radiated_J": float(e_rad),
            "E_body_lost_J": float(d_e),
            "radiated_fraction": float(e_rad / d_e),
        }
        fracs.append(e_rad / d_e)
    a = np.array(fracs)
    out["radiated_fraction_mean"] = float(a.mean())
    out["radiated_fraction_gauge_spread"] = float(a.max() - a.min())
    out["non_radiated_fraction_mean"] = float(1.0 - a.mean())
    # The ordering test needs no gauge positions at all: 1/r spreading forces the eta^2
    # integral to RISE toward the sphere. A code whose integrals fall toward the sphere
    # has its columns in the opposite radial order, and no choice of radii can fix that.
    ints = np.array([out["gauges"][f"WG{i+1}"]["eta2_integral_m2s"] for i in range(len(radii))])
    out["eta2_integral_ratio_near_over_far"] = float(ints[-1] / ints[0])
    out["radial_order_matches_experiment"] = bool(ints[-1] > ints[0])
    return out


def wg_verdict(root: Path = DEFAULT_ROOT, num_root: Path = NUM_ROOT) -> dict:
    """The whole item-4 answer, computed rather than argued."""
    w = wg_inventory(root, num_root)
    g = wave_gauge_distances()
    radii = [g["distances_m"][f"WG{i}"] for i in (1, 2, 3)]
    exp = {}
    for drop in DROPS:
        per = []
        for rep in REPS:
            d = _load(root, drop, rep, "Raw")
            per.append(radiated_energy_budget(d[:, 0], d[:, 1], d[:, 2:5], radii))
        exp[drop] = {
            "reps": per,
            "radiated_fraction_mean": float(np.mean([p["radiated_fraction_mean"] for p in per])),
            "radiated_fraction_rep_spread": float(
                np.ptp([p["radiated_fraction_mean"] for p in per])),
            "gauge_spread_mean": float(np.mean([p["radiated_fraction_gauge_spread"] for p in per])),
        }
    codes = {}
    for drop in DROPS:
        for code in CODES:
            p = _num_path(num_root, code, drop)
            if not p.exists():
                continue
            a = np.loadtxt(p, skiprows=1)
            if a.shape[1] < 5:
                continue
            codes[f"{code}/{drop}"] = radiated_energy_budget(a[:, 0], a[:, 1], a[:, 2:5], radii)
    return {
        "inventory": w, "gauge_distances": g,
        "gauge_radii_in_wavelengths": {f"WG{i+1}": radii[i] / (G_BENCHMARK * 0.7561 ** 2
                                                              / (2.0 * math.pi))
                                       for i in range(3)},
        "experiment": exp, "codes": codes,
        "codes_with_inverted_radial_order": sorted(
            {k.split("/")[0] for k, v in codes.items()
             if not v["radial_order_matches_experiment"]}),
    }


# --------------------------------------------------------------------------------------
# placing Job B against the published inter-code envelope
# --------------------------------------------------------------------------------------
# The lineage of the Job B grades, supplied by the R8 coordinator from primary documents
# and NOT re-derived here. This module does not grade Job B and must never be used to:
# the criterion was fixed in advance at R5_PHYSICS_BATCH_MANIFEST.md:214-226 and
# re-scoring after seeing a failure is forbidden. What is computed here is only WHERE a
# given grade sits relative to eleven published codes on the same benchmark.
JOB_B_GRADES = (
    # (job id, fz_over_analytic_measured excess, status)
    ("918043", 0.6419, "SUPERSEDED, EXPLICITLY. Predates commit 7c9e0af's measure_surface "
                       "h/2 correction and is biased high. "
                       "R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md:661 reads "
                       "'Quote 918240. 918043 is superseded.' Do not quote it."),
    ("918240", 0.5006, "THE CANONICAL GRADE. Job B against its pre-registered criterion, "
                       "pinned engine, --n-grid 64. Range across windows +49.36 to +50.29."),
    ("918450", 0.3435, "A DIFFERENT CONFIGURATION, the boundary-fix treatment. Still FAIL. "
                       "Not a re-grade of 918240 and must not be substituted for it. "
                       "Range +34.35 to +36.40."),
    ("918722", 0.2368, "n_grid 128 rung of the refinement series (n=64 +35.23, n=96 +27.00, "
                       "n=128 +23.68). A two-term fit gives an irreducible floor of "
                       "+18.05 points, so refinement alone never reaches the 10% band."),
    ("918722-floor", 0.1805, "The fitted irreducible floor of that refinement series, i.e. "
                             "the best the current formulation can reach at infinite "
                             "resolution."),
)


def published_envelope(ic: dict) -> dict:
    """The signed min and max period deviation from experiment over every code and drop.

    This is the yardstick: how far a code can be from the physical measurement and still
    have been published in a peer-reviewed inter-model comparison of this exact case.
    """
    all_dev, rans_dev, rows = [], [], []
    for drop in DROPS:
        for c, r in ic["drops"][drop]["codes"].items():
            all_dev.append(r["dev_period_pct"])
            rows.append((drop, c, r["family"], r["dev_period_pct"]))
            if r["family"] == "RANS":
                rans_dev.append(r["dev_period_pct"])
    a, rr = np.array(all_dev), np.array(rans_dev)
    lo = min(rows, key=lambda x: x[3])
    hi = max(rows, key=lambda x: x[3])
    return {
        "n_series": int(a.size),
        "all_codes_min_pct": float(a.min()), "all_codes_max_pct": float(a.max()),
        "all_codes_worst_abs_pct": float(np.abs(a).max()),
        "worst_low": {"drop": lo[0], "code": lo[1], "family": lo[2], "dev_pct": lo[3]},
        "worst_high": {"drop": hi[0], "code": hi[1], "family": hi[2], "dev_pct": hi[3]},
        "rans_only_min_pct": float(rr.min()), "rans_only_max_pct": float(rr.max()),
        "rans_only_worst_abs_pct": float(np.abs(rr).max()),
        "n_rans_series": int(rr.size),
    }


def place_job_b(root: Path = DEFAULT_ROOT, num_root: Path = NUM_ROOT) -> dict:
    """Where each Job B grade sits against the eleven-code envelope. NOT a re-grade."""
    ic = intercode(root, num_root)
    env = published_envelope(ic)
    out = {"envelope": env, "grades": []}
    for job, excess, status in JOB_B_GRADES:
        b = force_error_as_period_error(excess)
        rec = {"job": job, "force_excess_pct": 100.0 * excess, "status": status,
               "equivalents": b}
        for key, tag in (("scale_attribution", "scale"),
                         ("geometry_attribution", "geometry")):
            e = b[key]["equivalent_period_error_pct"]
            inside_all = env["all_codes_min_pct"] <= e <= env["all_codes_max_pct"]
            rec[f"{tag}_period_pct"] = e
            rec[f"{tag}_inside_all_code_envelope"] = bool(inside_all)
            rec[f"{tag}_times_worst_published_code"] = abs(e) / env["all_codes_worst_abs_pct"]
            rec[f"{tag}_times_worst_rans_code"] = abs(e) / env["rans_only_worst_abs_pct"]
            # every Job B equivalent is NEGATIVE (a force excess shortens the period), so
            # the bound it has to clear is the envelope's LOW edge, not its widest side.
            # Comparing a negative equivalent against a positive worst case would flatter
            # it: at 05D the worst code high is LPF4 at +12.83 and the worst low is LPF0
            # at -12.26, and the difference decides whether "inside the scatter" is true.
            same = env["all_codes_min_pct"] if e < 0 else env["all_codes_max_pct"]
            rec[f"{tag}_same_sign_worst_code_pct"] = same
            rec[f"{tag}_times_worst_same_sign_code"] = abs(e) / abs(same)
            rec[f"{tag}_beyond_same_sign_bound_pct_points"] = abs(e) - abs(same)
        out["grades"].append(rec)
    return out


# --------------------------------------------------------------------------------------
# what a measured a33/m does to sphere_heave.py's reflection windows
# --------------------------------------------------------------------------------------
def reflection_windows(a33_over_m: float, lim: float = 1.2, wall: float = 0.100,
                       depth: float = 0.5, g: float = 9.81, rho_w: float = RHO_W,
                       mass: float = M_SPHERE, d: float = D_SPHERE) -> dict:
    """Reproduce `sphere_heave.SphereTank.reflection_windows()` for any a33/m.

    Reimplemented rather than imported because `sphere_heave.py` is out of scope for this
    slot and must not be touched, and because importing it would drag in the engine
    module. The constants are read from it: FLOOR/WALL at :478-479, PLANNED_CONFIGS at
    :199, --lim/--depth defaults at :868-869, G_ENGINE at :146.

    THE SCALING IS NOT LINEAR IN T FOR TWO OF THE THREE SPEEDS, and that is the finding.
    c_group and c_phase are both PROPORTIONAL to T_n, so the window expressed in periods
    goes as (2*d_wall/c)/T_n ~ 1/T_n^2. Only the sqrt(g*h) bound, whose speed does not
    depend on the body at all, goes as 1/T_n.
    """
    k = rho_w * g * math.pi * (0.5 * d) ** 2
    t_n = 2.0 * math.pi * math.sqrt((mass * (1.0 + a33_over_m)) / k)
    d_wall = 0.5 * lim - wall
    speeds = {"group": g * t_n / (4.0 * math.pi),
              "kramer_phase": g * t_n / (2.0 * math.pi),
              "shallow_bound": math.sqrt(g * depth)}
    out = {"a33_over_m": a33_over_m, "natural_period_s": t_n, "wall_distance_m": d_wall,
           "lim_m": lim, "depth_m": depth, "stiffness_N_per_m": k}
    for name, c in speeds.items():
        t = 2.0 * d_wall / c
        out[f"c_{name}_m_s"] = c
        out[f"reflect_{name}_s"] = t
        out[f"reflect_{name}_periods"] = t / t_n
    return out


def reflection_delta(a33_measured: float, baseline: float = 0.5, **kw) -> dict:
    """What every reflection window becomes if the estimate is replaced by the measurement."""
    b = reflection_windows(baseline, **kw)
    m = reflection_windows(a33_measured, **kw)
    f = m["natural_period_s"] / b["natural_period_s"]
    out = {"baseline_a33_over_m": baseline, "measured_a33_over_m": a33_measured,
           "period_factor": f, "period_change_pct": 100.0 * (f - 1.0),
           "baseline": b, "measured": m, "windows": {}}
    for name in ("group", "kramer_phase", "shallow_bound"):
        p0 = b[f"reflect_{name}_periods"]
        p1 = m[f"reflect_{name}_periods"]
        out["windows"][name] = {
            "periods_at_baseline": p0,
            "periods_at_measured": p1,
            "change_pct": 100.0 * (p1 / p0 - 1.0),
            "scaling_exponent_measured": float(
                math.log(p1 / p0) / math.log(f)) if f != 1.0 else float("nan"),
        }
    return out


def lim_for_clean_periods(n_periods: float, a33_over_m: float, wall: float = 0.100,
                          g: float = 9.81, rho_w: float = RHO_W, mass: float = M_SPHERE,
                          d: float = D_SPHERE) -> dict:
    """Tank side needed for `n_periods` clean periods on Kramer's phase-celerity convention.

    Inverts reflection_windows(). Because the window in periods goes as 1/T_n^2 while the
    tank enters linearly, the REQUIRED SIDE grows as T_n^2, i.e. as (1 + a33/m). That is
    why re-sizing a tank against a revised added mass is not a small correction.
    """
    k = rho_w * g * math.pi * (0.5 * d) ** 2
    t_n = 2.0 * math.pi * math.sqrt((mass * (1.0 + a33_over_m)) / k)
    d_wall = n_periods * g * t_n ** 2 / (4.0 * math.pi)
    return {"n_periods": n_periods, "a33_over_m": a33_over_m, "natural_period_s": t_n,
            "required_wall_distance_m": d_wall, "required_lim_m": 2.0 * (d_wall + wall)}


def wave_gauge_distances(te0_s: float = 0.7561, g: float = G_BENCHMARK,
                         wall_distance_m: float = 4.22) -> dict:
    """Radial distances of WG1-3, DERIVED from the paper's own reflection statement.

    NOT read from Figure 8, which is a drawing and is not machine-readable here. Kramer
    2021 Section 3.5 p.16 states, of the reflected wave front: "Reflected waves propagated
    past the locations of wave gauges 1, 2, and 3 for around 2.0, 1.3, and 0.7 periods
    before t_r0", with t_r0 = 8.44/c and c the celerity of a linear wave of period Te0.

    A reflected wave reaches gauge i after travelling (2*L - r_i) and the body after 2*L,
    so the lead time is r_i/c and r_i = n_i * Te0 * c = n_i * g * Te0^2 / (2*pi).

    The paper gives n_i to one decimal and says "around", so these carry roughly +/-0.045 m
    (half a least count). They are an ORDER-OF-MAGNITUDE handle, adequate for asking
    whether a radiated-energy budget is possible and not adequate for computing one.
    """
    c = g * te0_s / (2.0 * math.pi)
    leads = {"WG1": 2.0, "WG2": 1.3, "WG3": 0.7}
    per_period = g * te0_s ** 2 / (2.0 * math.pi)
    return {
        "celerity_m_s": c, "te0_s": te0_s, "metres_per_lead_period": per_period,
        "reflective_wall_distance_m": wall_distance_m,
        "distances_m": {k: v * per_period for k, v in leads.items()},
        "lead_periods": leads,
        "least_count_uncertainty_m": 0.05 * per_period,
        "source": ("derived from Kramer 2021 Section 3.5 p.16, not read from Figure 8"),
    }


# --------------------------------------------------------------------------------------
def summarise(root: Path = DEFAULT_ROOT) -> dict:
    te0 = recover_te0(root)
    exp = experiment(root)
    r = 0.5 * D_SPHERE
    k = RHO_W * G_BENCHMARK * math.pi * r ** 2
    out = {"te0": te0, "drops": {}, "source": {"root": str(root), "zip_sha256": ZIP_SHA256}}
    for drop, h0 in DROPS.items():
        e = exp[drop]
        out["drops"][drop] = {
            "H0_m": h0,
            "first_damped_period_s": e["first_damped_period_s"],
            "cycle_means_s": [float(np.mean([e["reps"][rp]["cycle_periods_s"][i]
                                             for rp in REPS]))
                              for i in range(N_CYCLES)],
            "implied_added_mass_kg": float(e["implied_a33_over_m"] * M_SPHERE),
            "implied_a33_over_m": e["implied_a33_over_m"],
            "decay_rate_per_s": e["decay_rate_per_s"],
            "log_decrement_per_cycle": e["log_decrement_per_cycle"],
            "damping_ratio_zeta": _stat(np.array(
                [e["reps"][rp]["decay"]["damping_ratio_zeta"] for rp in REPS])),
            "envelope_r2": _stat(np.array(
                [e["reps"][rp]["decay"]["envelope_r2"] for rp in REPS])),
            "ci95": e["ci95"],
        }
    o = [out["drops"][d]["first_damped_period_s"]["mean"] for d in ("01D", "03D", "05D")]
    out["period_rises_with_drop_height"] = bool(o[0] < o[1] < o[2])
    out["heave_stiffness_N_per_m"] = float(k)
    # the small-amplitude limit the decay tends toward, from the LAST cycle estimate
    late = float(np.mean([out["drops"][d]["cycle_means_s"][-1] for d in DROPS]))
    out["late_cycle_period_s"] = late
    out["late_cycle_implied_a33_over_m"] = float(
        (k * (late / (2.0 * math.pi)) ** 2 - M_SPHERE) / M_SPHERE)
    return out


def _p_exp(s):
    t = s["te0"]
    print(f"Te0 normalising constant: {t['te0_s']:.6f} s over {t['n_series']} series, "
          f"spread {t['te0_spread_s']:.2e} s")
    print(f"  constant across all drops and reps: {t['is_constant_across_drops_and_reps']} "
          f"-> it is a NORMALISER, not a per-drop measurement\n")
    print(f"heave stiffness rho*g*pi*R^2 = {s['heave_stiffness_N_per_m']:.3f} N/m "
          f"(rho_w={RHO_W}, g={G_BENCHMARK} benchmark)\n")
    print("drop  H0[mm]  first damped period [s]         N  spread    a33/m   CI95 half-width")
    for drop in ("01D", "03D", "05D"):
        d = s["drops"][drop]
        f = d["first_damped_period_s"]
        c = d["ci95"]
        print(f"{drop}   {d['H0_m']*1000:5.0f}   {f['mean']:.4f} "
              f"[{f['min']:.4f}, {f['max']:.4f}]  {f['n']}  {f['spread']:.4f}  "
              f"{d['implied_a33_over_m']:.3f}   {c['mean_halfwidth_pct_of_H0']:.3f}% of H0 "
              f"= {c['mean_halfwidth_mm']:.3f} mm")
    print(f"\npaper's Fig 13 claim, period rises with drop height: "
          f"{'CONFIRMED' if s['period_rises_with_drop_height'] else 'NOT CONFIRMED'}")
    print("cycle-by-cycle means (4 reps), showing decay toward the Te0 normaliser:")
    for drop in ("01D", "03D", "05D"):
        print(f"  {drop}: " + ", ".join(f"{v:.4f}" for v in s["drops"][drop]["cycle_means_s"]))
    print(f"\nlate-cycle period {s['late_cycle_period_s']:.4f} s "
          f"-> small-amplitude a33/m = {s['late_cycle_implied_a33_over_m']:.3f}")
    print("decay envelope over the first %d bracketed extrema (experiment):" % N_EXTREMA)
    print("  drop   decay rate [1/s]        log decrement/cycle    zeta     env r2")
    for drop in ("01D", "03D", "05D"):
        d = s["drops"][drop]
        sg, ld = d["decay_rate_per_s"], d["log_decrement_per_cycle"]
        print(f"  {drop}   {sg['mean']:.4f} +/- {sg['std']:.4f}      "
              f"{ld['mean']:.4f} +/- {ld['std']:.4f}       "
              f"{d['damping_ratio_zeta']['mean']:.4f}   "
              f"{d['envelope_r2']['mean']:.4f}")


def _p_intercode(ic):
    inv = ic["inventory"]
    print(f"ELEVEN CODES, {inv['n_series']} SERIES "
          f"(a balanced design would be {inv['n_series_if_balanced']}). "
          f"absent: {', '.join(inv['missing']) or 'none'}\n")
    for drop in ("01D", "03D", "05D"):
        d = ic["drops"][drop]
        e = d["experiment"]
        print(f"=== {drop}, H0 = {DROPS[drop]*1000:.0f} mm, "
              f"{d['n_codes']} codes"
              + (f", ABSENT: {', '.join(d['codes_absent'])}" if d["codes_absent"] else "")
              + " ===")
        print("  code    fam   T1[s]   dT1%    decay[1/s]  dsig%   a33/m  trough[mm] "
              " dtrough[mm] dnorm%H0  WG")
        for c, r in d["codes"].items():
            print(f"  {c:7s} {r['family']:4s}  {r['first_damped_period_s']:.4f} "
                  f"{r['dev_period_pct']:+6.2f}  {r['decay']['decay_rate_per_s']:8.4f} "
                  f"{r['dev_decay_rate_pct']:+7.2f}  {r['implied_a33_over_m']:.3f} "
                  f"{r['first_trough_amp_m']*1000:8.3f} {r['dev_first_trough_mm']:+10.3f}"
                  f" {r['dev_first_trough_norm_pct_of_H0']:+8.2f}"
                  f"    {'y' if r['has_wg'] else '-'}")
        sp = d["spread_first_damped_period_s"]
        sd = d["spread_decay_rate_per_s"]
        print(f"  EXPERIMENT (4 reps)   {e['first_damped_period_s']['mean']:.4f} "
              f"        {e['decay_rate_per_s']['mean']:8.4f}          "
              f"{e['implied_a33_over_m']:.3f} "
              f"{e['first_trough_amp_m']['mean']*1000:8.3f}")
        print(f"  inter-code period spread {sp['min']:.4f} to {sp['max']:.4f} s, "
              f"{sp['spread_pct_of_mean']:.2f}% of the mean; "
              f"max |dev| from experiment {d['max_abs_dev_period_pct']:.2f}%, "
              f"median {d['median_abs_dev_period_pct']:.2f}%")
        print(f"  inter-code decay-rate spread {sd['min']:.4f} to {sd['max']:.4f} 1/s, "
              f"{sd['spread_pct_of_mean']:.1f}% of the mean\n")


def _p_wg(w):
    print(f"WG1-3 on {w['n_codes_with_wg']} of {len(CODES)} codes: "
          f"{', '.join(w['codes_with_wg'])}")
    print(f"  absent from: {', '.join(w['codes_without_wg'])}")
    print(f"  {w['n_numerical_with_wg']} of {w['n_numerical_total']} numerical series carry them")
    print(f"  every experimental Measured file carries them: "
          f"{w['experimental_measured_all_have_wg']}")
    print(f"  any experimental CI95 file carries them: {w['experimental_ci95_have_wg']}")


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p.add_argument("--num-root", type=Path, default=NUM_ROOT)
    p.add_argument("--json", action="store_true", help="emit the summary as JSON")
    p.add_argument("--intercode", action="store_true",
                   help="reduce all eleven blind-test codes with the same statistic")
    p.add_argument("--wg", action="store_true", help="wave-gauge availability inventory")
    p.add_argument("--reflection", type=float, metavar="A33_OVER_M", default=None,
                   help="recompute sphere_heave.py's reflection windows at this a33/m")
    p.add_argument("--wg-verdict", action="store_true",
                   help="radiated-energy budget on every series that carries WG1-3")
    p.add_argument("--place", action="store_true",
                   help="place every Job B grade against the eleven-code envelope")
    p.add_argument("--force-excess", type=float, metavar="FRAC", default=None,
                   help="convert a vertical-force ratio excess (e.g. 0.5006) to the "
                        "period error it would imply under a stiffness attribution")
    a = p.parse_args()

    if a.wg:
        w = wg_inventory(a.root, a.num_root)
        print(json.dumps(w, indent=2, sort_keys=True)) if a.json else _p_wg(w)
        return
    if a.intercode:
        ic = intercode(a.root, a.num_root)
        print(json.dumps(ic, indent=2, sort_keys=True)) if a.json else _p_intercode(ic)
        return
    if a.wg_verdict:
        print(json.dumps(wg_verdict(a.root, a.num_root), indent=2, sort_keys=True))
        return
    if a.place:
        print(json.dumps(place_job_b(a.root, a.num_root), indent=2, sort_keys=True))
        return
    if a.reflection is not None:
        d = reflection_delta(a.reflection)
        print(json.dumps(d, indent=2, sort_keys=True))
        return
    if a.force_excess is not None:
        print(json.dumps(force_error_as_period_error(a.force_excess), indent=2,
                         sort_keys=True))
        return

    s = summarise(a.root)
    if a.json:
        print(json.dumps(s, indent=2, sort_keys=True))
        return
    _p_exp(s)


if __name__ == "__main__":
    main()
