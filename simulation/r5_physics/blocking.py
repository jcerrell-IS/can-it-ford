"""Transient exclusion, stationarity, and blocked standard errors for correlated series.

WHY THIS EXISTS
---------------
This project's current defence of any settle length is that a longer one changed the
answer, so the shorter one was wrong. `settle_frames=8` was refuted by 60, and 60 by 250.
**That argument has no stopping rule**: 250 can fail the same way, and nothing in it says
when to stop lengthening. It is an infinite regress dressed as a convergence study.

Blocking supplies the stopping rule. Under the blocking transformation the estimated
standard error of the mean grows with block size only while blocks are still correlated,
and then stops growing. The plateau IS the answer: it converts "we ran 250 frames" into
"this observable is stationary over this window and its standard error is X", which is
what a reviewer actually asks for.

The settling-literature position, from the catalog D1 mined (e9b3717): no universal frame
count and no universal force-settling threshold emerges. The defensible protocol is to
(1) detect and exclude the transient, (2) demonstrate stationarity for the reported
observable, and (3) attach an uncertainty computed from CORRELATED samples. This module
does those three things. A frame count is not an answer to any of them.

METHOD AND CITATIONS
--------------------
* Flyvbjerg & Petersen (1989), "Error estimates on averages of correlated data",
  J. Chem. Phys. 91(1):461-466, doi:10.1063/1.457480. The classical blocking
  transformation and its error bars. This is the anchor and it is implemented here in
  full.
* Jonsson (2018), Phys. Rev. E 98:043304, doi:10.1103/PhysRevE.98.043304. Supplies a
  formal automatic block-size criterion, removing the hand-chosen plateau.
  **NOT IMPLEMENTED HERE AS ITS OWN STATISTIC.** The paper is paywalled and I have not
  read it, so writing down "Jonsson's test" from memory would be the same error as
  deriving Table 1 instead of reading it. `plateau()` uses an explicitly stated rule of
  my own (below) which achieves the same PROPERTY (no hand-chosen block size) without
  claiming to be his criterion. Replace it once the primary source is in hand.
* Grossfield et al. (2019), LiveCoMS 1(1):5067, doi:10.33011/livecoms.1.1.5067. Quotable
  best-practice document. Note 2019, not 2018: the catalog's year was corrected by audit.
* Bergmann et al. (2021), doi:10.1115/1.4052402. Closest venue match, engineering CFD
  rather than molecular simulation.

None of these four is cited anywhere in this repository.

THE PLATEAU RULE USED HERE, stated so it can be criticised
----------------------------------------------------------
Walk the blocking ladder upward. Stop at the first level k whose standard-error estimate
is not significantly below the largest estimate seen at or above it, where "significantly"
means "by more than `n_sigma` times its own error bar". Report that level's estimate.
Levels with fewer than `min_blocks` blocks are never selected, because their error bars
are meaningless. If no level qualifies before the ladder runs out, `converged` is False
and the standard error is reported as a LOWER BOUND, never as a converged value.

A non-converged blocking result is a real and reportable outcome: it means the series is
too short for its own correlation time, which is exactly the diagnosis a settle-length
argument needs and cannot otherwise state.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

CITATIONS = {
    "flyvbjerg_petersen_1989": "10.1063/1.457480",
    "jonsson_2018": "10.1103/PhysRevE.98.043304",
    "grossfield_2019": "10.33011/livecoms.1.1.5067",
    "bergmann_2021": "10.1115/1.4052402",
}


# --------------------------------------------------------------------------------------
# Flyvbjerg-Petersen blocking
# --------------------------------------------------------------------------------------
def blocking_ladder(x):
    """The full blocking transformation, one row per level.

    At each level the series is halved by pairwise averaging. `se` is the naive
    standard error of the mean AT THAT LEVEL, sqrt(c0/(n-1)); under FP it is an
    increasing, eventually-plateauing estimate of the true standard error. `se_err` is
    its own uncertainty, se/sqrt(2(n-1)), which is what makes the plateau decidable
    rather than eyeballed.
    """
    x = np.asarray(x, dtype=float).ravel()
    if x.size < 2:
        raise ValueError(f"need at least 2 samples, got {x.size}")
    levels = []
    k = 0
    while x.size >= 2:
        n = x.size
        c0 = float(np.var(x))                 # biased, i.e. /n, as in FP
        se = math.sqrt(c0 / (n - 1)) if n > 1 else float("nan")
        levels.append({
            "level": k,
            "n_blocks": int(n),
            "block_size": int(2 ** k),
            "mean": float(x.mean()),
            "var": c0,
            "se": se,
            "se_err": se / math.sqrt(2.0 * (n - 1)) if n > 1 else float("nan"),
        })
        if x.size % 2:                        # drop the odd sample, standard practice
            x = x[:-1]
        x = 0.5 * (x[0::2] + x[1::2])
        k += 1
    return levels


def plateau(levels, n_sigma=1.0, min_blocks=8):
    """Pick the level where the standard error stops growing. Rule stated in the docstring.

    Returns (index, converged). `converged=False` means the ladder ran out before the
    estimate stopped growing: the series is too short for its own correlation time.
    """
    usable = [i for i, L in enumerate(levels) if L["n_blocks"] >= min_blocks]
    if not usable:
        return 0, False
    for i in usable:
        later = [levels[j]["se"] for j in usable if j >= i]
        if not later:
            continue
        if levels[i]["se"] + n_sigma * levels[i]["se_err"] >= max(later):
            return i, True
    return usable[-1], False


def blocked_se(x, n_sigma=1.0, min_blocks=8):
    """Standard error of the mean of a correlated series. Returns a dict."""
    levels = blocking_ladder(x)
    i, converged = plateau(levels, n_sigma=n_sigma, min_blocks=min_blocks)
    naive = levels[0]["se"]
    se = levels[i]["se"]
    return {
        "n": levels[0]["n_blocks"],
        "mean": levels[0]["mean"],
        "se_naive": naive,
        "se_blocked": se,
        "se_is_lower_bound": not converged,
        "plateau_level": i,
        "plateau_block_size": levels[i]["block_size"],
        "plateau_n_blocks": levels[i]["n_blocks"],
        "converged": converged,
        # How badly the naive error bar understates the truth. This is the number that
        # says whether correlation matters for this observable at all.
        "inflation_vs_naive": (se / naive) if naive > 0 else float("nan"),
        # Integrated autocorrelation time implied by the inflation, tau = (se/se_naive)^2.
        "tau_int_frames": (se / naive) ** 2 if naive > 0 else float("nan"),
        "levels": levels,
    }


# --------------------------------------------------------------------------------------
# transient exclusion and stationarity
# --------------------------------------------------------------------------------------
def find_transient(x, max_drop_frac=0.5, n_candidates=40, min_blocks=8):
    """Choose a truncation point by minimising the blocked standard error of the mean.

    A transient inflates the variance of the retained window, so the blocked SE is a
    natural objective. Restricting the search to `max_drop_frac` of the series stops it
    from "converging" by throwing everything away, which is the standard failure mode of
    an unconstrained truncation rule.

    Returns (index, table). index 0 means no transient was detected.
    """
    x = np.asarray(x, dtype=float).ravel()
    n = x.size
    hi = int(n * max_drop_frac)
    cands = sorted(set(int(round(v)) for v in np.linspace(0, hi, n_candidates)))
    table = []
    for d in cands:
        rest = x[d:]
        if rest.size < 4 * min_blocks:
            continue
        try:
            r = blocked_se(rest, min_blocks=min_blocks)
        except ValueError:
            continue
        table.append({"drop": d, "kept": int(rest.size), "mean": r["mean"],
                      "se_blocked": r["se_blocked"], "converged": r["converged"]})
    if not table:
        return 0, []
    best = min(table, key=lambda r: r["se_blocked"])
    return int(best["drop"]), table


def stationarity(x, min_blocks=8, n_sigma=2.0):
    """Two independent stationarity checks on the SAME window, each using blocked errors.

    1. Halves test: the two halves' means must agree within their combined blocked SE.
    2. Trend test: a least-squares slope must be consistent with zero, where the slope's
       uncertainty is inflated by the same factor blocking found for the mean. Using the
       ordinary-least-squares slope error here would understate it by exactly the factor
       that makes this whole module necessary.

    A series can pass one and fail the other, so both verdicts are returned and the
    overall verdict is the AND. Reporting only the one that passes would be the tunable
    gate problem again.
    """
    x = np.asarray(x, dtype=float).ravel()
    n = x.size
    half = n // 2
    a, b = x[:half], x[half:]
    ra, rb = blocked_se(a, min_blocks=min_blocks), blocked_se(b, min_blocks=min_blocks)
    diff = ra["mean"] - rb["mean"]
    sd = math.hypot(ra["se_blocked"], rb["se_blocked"])
    halves_ok = bool(abs(diff) <= n_sigma * sd) if sd > 0 else False

    t = np.arange(n, dtype=float)
    full = blocked_se(x, min_blocks=min_blocks)
    slope, intercept = np.polyfit(t, x, 1)
    resid = x - (slope * t + intercept)
    stt = float(((t - t.mean()) ** 2).sum())
    se_slope_ols = math.sqrt(float((resid ** 2).sum()) / (n - 2) / stt) if n > 2 else float("nan")
    se_slope = se_slope_ols * full["inflation_vs_naive"]
    trend_ok = bool(abs(slope) <= n_sigma * se_slope) if se_slope > 0 else False

    return {
        "halves_mean_a": ra["mean"], "halves_mean_b": rb["mean"],
        "halves_diff": diff, "halves_combined_se": sd,
        "halves_n_sigma": abs(diff) / sd if sd > 0 else float("inf"),
        "halves_stationary": halves_ok,
        "slope_per_frame": float(slope),
        "se_slope_ols": se_slope_ols,
        "se_slope_inflated": se_slope,
        "slope_n_sigma": abs(slope) / se_slope if se_slope > 0 else float("inf"),
        "trend_stationary": trend_ok,
        "stationary": bool(halves_ok and trend_ok),
        "n_sigma_threshold": n_sigma,
    }


def analyse(x, dt=None, label="", min_blocks=8):
    """Full protocol: exclude the transient, test stationarity, attach a blocked error."""
    x = np.asarray(x, dtype=float).ravel()
    drop, table = find_transient(x, min_blocks=min_blocks)
    kept = x[drop:]
    res = blocked_se(kept, min_blocks=min_blocks)
    st = stationarity(kept, min_blocks=min_blocks)
    out = {
        "label": label,
        "n_total": int(x.size),
        "transient_excluded_frames": int(drop),
        "n_retained": int(kept.size),
        "mean": res["mean"],
        "se_blocked": res["se_blocked"],
        "se_naive": res["se_naive"],
        "se_is_lower_bound": res["se_is_lower_bound"],
        "inflation_vs_naive": res["inflation_vs_naive"],
        "tau_int_frames": res["tau_int_frames"],
        "plateau_block_size": res["plateau_block_size"],
        "plateau_n_blocks": res["plateau_n_blocks"],
        "blocking_converged": res["converged"],
        "stationary": st["stationary"],
        "stationarity": st,
        "transient_scan": table,
    }
    if dt:
        out["transient_excluded_s"] = drop * float(dt)
        out["tau_int_s"] = res["tau_int_frames"] * float(dt)
    return out


# --------------------------------------------------------------------------------------
def _fmt(r):
    conv = "converged" if r["blocking_converged"] else "NOT CONVERGED (lower bound)"
    stat = "stationary" if r["stationary"] else "NOT STATIONARY"
    return (f"  {r['label']:<34s} n={r['n_total']:>4d} drop={r['transient_excluded_frames']:>3d} "
            f"kept={r['n_retained']:>4d}  mean={r['mean']:+.6g}  "
            f"se={r['se_blocked']:.4g} ({conv})  "
            f"inflation={r['inflation_vs_naive']:.2f}x  tau={r['tau_int_frames']:.1f}f  {stat}")


def run_metrics(paths, columns, min_blocks=8):
    out = []
    for p in paths:
        p = Path(p)
        with p.open() as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            continue
        t = [float(r["t"]) for r in rows]
        dt = (t[1] - t[0]) if len(t) > 1 else None
        for col in columns:
            if col not in rows[0]:
                continue
            series = np.array([float(r[col]) for r in rows])
            if not np.isfinite(series).all() or np.allclose(series, series[0]):
                continue
            try:
                out.append(analyse(series, dt=dt, label=f"{p.parent.name}:{col}",
                                   min_blocks=min_blocks))
            except ValueError:
                continue
    return out


def run_force_series(paths, min_blocks=8):
    """The C1-SDF / C1-box collider force series, which carry the project's
    err_steady_vs_analytic_pct headline. Those use fz[len(fz)//2:].mean(), a HAND-CHOSEN
    back-half window with a reported std that is not a standard error of the mean."""
    out = []
    for p in paths:
        p = Path(p)
        d = json.loads(p.read_text())
        fs = d.get("f_series")
        if not fs:
            continue
        fz = np.asarray(fs, dtype=float)[:, 2]
        r = analyse(fz, label=f"{p.stem}:Fz", min_blocks=min_blocks)
        r["published"] = {
            "F_buoy_analytic": d.get("F_buoy_analytic"),
            "F_steady_tail_mean": d.get("F_steady_tail_mean"),
            "F_steady_tail_std": d.get("F_steady_tail_std"),
            "err_steady_vs_analytic_pct": d.get("err_steady_vs_analytic_pct"),
            "window": "fz[len(fz)//2:], hand-chosen back half",
        }
        fa = d.get("F_buoy_analytic")
        if fa:
            r["err_vs_analytic_pct"] = 100.0 * (r["mean"] - fa) / fa
            r["err_se_pct"] = 100.0 * r["se_blocked"] / abs(fa)
        out.append(r)
    return out


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--metrics", nargs="*", default=[], help="metrics.csv paths")
    p.add_argument("--forces", nargs="*", default=[], help="coupling_validation json paths")
    p.add_argument("--columns", nargs="*",
                   default=["dmag", "vmag", "vx", "dz", "pitch_deg", "roll_deg"])
    p.add_argument("--min-blocks", type=int, default=8)
    p.add_argument("--out", default="")
    a = p.parse_args()

    results = []
    if a.metrics:
        print("METRICS SERIES")
        rs = run_metrics(a.metrics, a.columns, a.min_blocks)
        for r in rs:
            print(_fmt(r))
        results += rs
    if a.forces:
        print("\nCOLLIDER FORCE SERIES (Fz)")
        rs = run_force_series(a.forces, a.min_blocks)
        for r in rs:
            print(_fmt(r))
            pub = r["published"]
            print(f"      published tail mean {pub['F_steady_tail_mean']:.4f} N "
                  f"(std {pub['F_steady_tail_std']:.4f}, {pub['window']})")
            print(f"      err vs analytic: {r.get('err_vs_analytic_pct', float('nan')):+.4f}% "
                  f"+/- {r.get('err_se_pct', float('nan')):.4f}% (blocked SE), "
                  f"published {pub['err_steady_vs_analytic_pct']:+.4f}% with no SE")
        results += rs

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(
            {"citations": CITATIONS, "results": results}, indent=2, sort_keys=True))
        print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
