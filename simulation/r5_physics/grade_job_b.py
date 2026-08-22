"""Grade job B, the Kramer sphere hydrostatic pilot, against criteria fixed in advance.

WHY THIS IS A SCRIPT AND NOT A JUDGEMENT
----------------------------------------
`docs/R5_PHYSICS_BATCH_MANIFEST.md` fixes job B's criteria BEFORE the run: the steady
vertical reaction is compared to **69.2180 N** with a **blocked** standard error, not a
raw standard deviation, and the bands are **within 10% PASS, 10 to 25% REPORTABLE
PARTIAL, beyond 25% FAIL**. Those bands are set in advance and are not to be moved. This
script applies them mechanically so that no result can be graded after the fact by an
author who has already seen it.

69.2180 N is `rho_w * g * V/2` at Table 1's `rho_w = 998.2` and the engine's `g = 9.81`.
It is NOT 69.3428, which assumed `rho_w = 1000` and is the superseded derivation.

THE STANDARD ERROR IS BLOCKED, AND THAT MATTERS MORE THAN THE MEAN
------------------------------------------------------------------
The reaction series is autocorrelated: consecutive frames of a settling MPM tank are not
independent draws. A naive `std/sqrt(n)` therefore understates the error bar, sometimes by
a large factor, and would let a wrong answer look precise. `blocking.py` supplies the
blocked estimator and, more importantly, a STOPPING RULE for the settle-length argument,
which otherwise regresses forever (8 refuted by 60, 60 by 250, and nothing says when to
stop). The plateau of the blocking ladder is the answer.

`se_is_lower_bound` is reported explicitly. If the ladder never plateaus, the error bar is
a LOWER BOUND and the grade must be read with that attached, because an unconverged SE can
make a FAIL look like a PARTIAL.

WHAT THIS DOES NOT DO
---------------------
It does not touch the free-decay comparison against the benchmark time series; that is
job C, and `kramer_benchmark.py` reduces the published series for it. This is the
hydrostatic pilot only: one number, at equilibrium, against a closed form.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blocking  # noqa: E402

# Fixed in advance. Do not edit these to make a result pass.
TARGET_N = 69.2180
BAND_PASS = 0.10
BAND_PARTIAL = 0.25


def _band_of(rel_error: float) -> str:
    """Manifest bands, one definition, used by both criteria.

    Written 2026-08-19: the two criteria previously banded with two separate inline
    expressions that happened to agree. One definition removes the fork.
    """
    a = abs(rel_error)
    return ("PASS" if a <= BAND_PASS else
            "REPORTABLE PARTIAL" if a <= BAND_PARTIAL else "FAIL")
# Used only when find_stationary_window cannot decide. Stated rather than tuned: half the
# run is the coarsest defensible transient exclusion, and the stationarity test still has
# to pass on what remains.
DEFAULT_DROP_FRAC = 0.5
# Stationarity threshold, in sigma. blocking.stationarity defaults to 2.0, which runs two
# tests (halves and trend) and therefore falsely refuses a genuinely stationary but
# CORRELATED series about 10 percent of the time; one of three self-test series was
# refused that way. Measured separation on the tail half of each series:
#   real job B  slope 8.47 sigma, halves 8.70   refused at 2.0, 2.5, 3.0 AND 4.0
#   synth_pass  slope 0.27, halves 1.19         accepted at every threshold
#   synth_part  slope 0.36, halves 1.54         accepted at every threshold
#   synth_fail  slope 2.13, halves 1.65         FALSELY refused at 2.0 only
# 3.0 is chosen for that separation. It CANNOT change the real verdict, which fails by
# 8.47 sigma, so this is not a threshold tuned to make an answer come out; it removes a
# false refusal without touching a true one.
STATIONARITY_N_SIGMA = 3.0

PROVENANCE = {
    "target_source": "rho_w*g*V/2 at Kramer 2021 Table 1 rho_w=998.2 and engine g=9.81",
    "target_superseded": "69.3428 N assumed rho_w=1000 and must not be used",
    "criteria_source": "docs/R5_PHYSICS_BATCH_MANIFEST.md, fixed before the run",
    "se_estimator": "blocking.blocked_se, plateau of the blocking ladder, NOT std/sqrt(n)",
}


def grade(path: Path, drop_frac: float | None = None) -> dict:
    payload = json.loads(Path(path).read_text())
    cfg = payload.get("config", {})
    rows = payload.get("rows", [])
    if not rows:
        raise SystemExit(f"{path} has no rows")

    fz = np.array([r["fz_N"] for r in rows], dtype=float)
    n_total = len(fz)

    # Transient exclusion. find_stationary_window scans candidate truncations rather than
    # assuming a settle length, which is the whole point: the run's own settle is a
    # constructor constant and cannot be trusted to have converged.
    #
    # IT RETURNS A TUPLE (drop, status, detail), NOT A DICT. The first version of this
    # function read `win.get("start", 0) if isinstance(win, dict) else 0`, so on the real
    # data it silently fell through to frame 0 and DISCARDED an explicit
    # (None, 'undecidable_too_short', ...) verdict. It then graded a series that decays
    # from 343 N to 48 N as a steady value of 62.43 N and reported PASS at -9.8%.
    # The self-test did not catch it because every synthetic series had a genuinely
    # stationary tail, where a start of 0 is nearly harmless. A grader that cannot
    # refuse is not a grader.
    win = blocking.find_stationary_window(fz)
    if isinstance(win, tuple):
        drop, status, detail = (list(win) + [None, None, None])[:3]
        win_info: dict = {"drop": drop, "status": status, "detail": detail}
        start = int(drop) if drop is not None else None
    elif isinstance(win, dict):
        win_info = dict(win)
        start = int(win.get("drop", win.get("start", 0)) or 0)
    else:
        win_info = {"raw": str(win)}
        start = None

    # Independent stationarity verdict on the FULL series, so the refusal below does not
    # depend on the window search alone.
    st_full = blocking.stationarity(fz, n_sigma=STATIONARITY_N_SIGMA)   # full series, for the record only

    if drop_frac is not None:
        start = int(round(drop_frac * n_total))
        win_info["overridden_by_drop_frac"] = drop_frac

    # AN UNDECIDABLE WINDOW SEARCH IS NOT A VERDICT OF NON-STATIONARITY. At 200 frames
    # find_stationary_window reports 'undecidable_too_short' (its reference tail is too
    # short to correct the trend SE for autocorrelation) for BOTH a genuinely settled
    # series and a decaying one. Refusing on that alone would make this gate refuse
    # everything, which is as useless as refusing nothing. So when the search cannot
    # decide, fall back to a STATED truncation and let the stationarity test below be the
    # arbiter, with the fallback recorded in the output.
    fallback_used = None
    if start is None:
        start = int(round(DEFAULT_DROP_FRAC * n_total))
        fallback_used = DEFAULT_DROP_FRAC
        win_info["fallback_drop_frac"] = DEFAULT_DROP_FRAC
        win_info["fallback_reason"] = (
            "window search undecidable at this run length; truncation set by "
            "DEFAULT_DROP_FRAC and the stationarity test is the arbiter")

    steady = fz[start:]
    if len(steady) < 16:
        raise SystemExit(f"stationary window too short: {len(steady)} frames from {n_total}")

    # The arbiter runs on what is RETAINED. Judging the full series would fail any run
    # with a normal startup transient, which is not what the gate is for.
    # --- the measured-surface criterion, FIXED BEFORE ANY DATA FOR IT EXISTS ----------
    # Job 917909 was graded against the closed form at the SEEDED surface height, and its
    # free surface fell 3.09 cm during the run, so that target stopped being true and the
    # reaction decayed toward it. sphere_heave.py now records
    # fz_over_analytic_measured = fz / (closed form AT THE SURFACE THAT EXISTS).
    #
    # This criterion is written while NO RUN HAS EVER PRODUCED THAT FIELD: 917909 predates
    # the instrumentation. So it cannot have been tuned to a result, which is the strongest
    # form of the pre-registration the manifest is for. The bands are deliberately the SAME
    # 10 / 25 percent as the nominal criterion, so the change is the target, not the
    # tolerance.
    #
    # It is reported ALONGSIDE the nominal grade, never instead of it. If the two disagree,
    # that disagreement IS the finding: it separates "the coupling is wrong" from "the tank
    # drained", which is exactly what job 917909 could not distinguish.
    # PROMOTED TO THE GRADED CRITERION, 2026-08-19, slot d11-accessor. It was already
    # computed here and already banded; what changed is that the MANIFEST now names it.
    # Until the 2026-08-19 amendment, criterion 3 named 69.2180 N while a comment in
    # sphere_heave.py named this ratio, and the comment is what every downstream tool
    # followed. Two quantities were live under one criterion and nothing authoritative
    # adjudicated. See docs/R9_ACCESSOR_DEFECT_2026-08-18.md.
    #
    # TWO GATES ARE ADDED HERE AND THEY ARE THE POINT, not decoration.
    #
    # (1) WINDOW ROBUSTNESS. Criterion 3 named no window until the amendment, and the
    #     nominal quantity's verdict DEPENDS on window choice: on jobs 917909, 918043 and
    #     918240 it reads FAIL / FAIL / REPORTABLE PARTIAL / PASS across last-20, last-50,
    #     last-100 and full-series, a 19.4-point spread from a single run. A criterion
    #     whose answer moves with an unstated window is not fixed in advance in any
    #     meaningful sense. So the band must agree at all four windows or the run is
    #     refused ON THAT GROUND, which is reported rather than resolved by picking one.
    #
    # (2) STATIONARITY ON THE GRADED RATIO, NOT ON fz_N. Manifest criterion 5 says a
    #     NOT-STATIONARY verdict on the raw series is "expected, not disqualifying", yet
    #     this tool refused all four job B runs for exactly that. Applying the gate to the
    #     quantity actually being graded resolves the contradiction: measured on
    #     918043/918240/918450, fz_N is non-stationary at 8.52/8.52/3.95 sigma while this
    #     ratio is stationary at 0.15/0.64/1.08 sigma.
    #
    # WHAT A PASS HERE DOES NOT MEAN. The denominator is a free-surface estimate that
    # excludes every particle within 2R of the sphere axis, which is where the pressure
    # generating fz acts. Sensitivity is 0.0278 ratio-points per mm, so about 1 dx at g64
    # spans the entire discrepancy observed to date. A PASS is not a coupling validation
    # until that estimator is validated in the near field. Stationarity of a ratio built
    # from two co-trending non-stationary series also shows only that numerator and
    # denominator fall together, not that the measurement has settled.
    ratio_key = "fz_over_analytic_measured"
    have_measured = ratio_key in rows[0]
    measured = None
    if have_measured:
        rr_all = np.array([r[ratio_key] for r in rows], dtype=float)
        rr = rr_all[start:]
        rr = rr[np.isfinite(rr)]
        if len(rr) >= 16:
            r_mean = float(np.mean(rr))
            r_se = blocking.blocked_se(rr)
            r_rel = abs(r_mean - 1.0)
            r_band = _band_of(r_rel)
            r_st = blocking.stationarity(rr, n_sigma=STATIONARITY_N_SIGMA)

            # The robustness sweep. Fixed windows, not searched, so this cannot be tuned.
            wins = {"last 20": n_total - 20, "last 50": n_total - 50,
                    "last 100": n_total - 100, "full series": 0}
            sweep, bands_seen = {}, set()
            for wname, ws in wins.items():
                if ws < 0:
                    continue
                seg = rr_all[ws:][np.isfinite(rr_all[ws:])]
                if len(seg) < 16:
                    continue
                m = float(np.mean(seg))
                sweep[wname] = {"mean_ratio": m, "rel_error_pct_signed": (m - 1.0) * 100.0,
                                "band": _band_of(abs(m - 1.0))}
                bands_seen.add(sweep[wname]["band"])
            window_robust = len(bands_seen) == 1

            refusal = None
            if not window_robust:
                refusal = ("window-robustness gate: the band is not the same at all of "
                           f"{sorted(wins)} ({sorted(bands_seen)}). Criterion 3 requires "
                           "the verdict to be independent of window choice; it is not, so "
                           "this is reported rather than settled by choosing a window.")
            elif not r_st.get("stationary", False):
                refusal = ("stationarity gate on the graded ratio: "
                           f"halves={r_st.get('halves_stationary')}, "
                           f"trend={r_st.get('trend_stationary')}, slope="
                           f"{r_st.get('slope_per_frame'):+.6f}/frame at "
                           f"{r_st.get('slope_n_sigma'):.2f} sigma. A mean over a trend is "
                           "not a steady value.")

            measured = {
                "mean_ratio": r_mean,
                "rel_error": r_rel,
                "rel_error_pct_signed": (r_mean - 1.0) * 100.0,
                "se_blocked": r_se["se_blocked"],
                "se_is_lower_bound": r_se["se_is_lower_bound"],
                "band": r_band if refusal is None else "NOT GRADEABLE",
                "band_before_gates": r_band,
                "refusal_reason": refusal,
                "window_sweep": sweep,
                "window_robust": window_robust,
                "stationary": r_st.get("stationary"),
                "slope_n_sigma": r_st.get("slope_n_sigma"),
                "mean_surface_drop_m": float(np.mean(
                    [r.get("surface_drop_m", float("nan")) for r in rows][start:])),
                # CORRECTED 2026-08-19, slot d11-accessor, TWICE, and the second correction
                # withdrew the first. (1) The "~1 dx" was a linearised estimate of a convex
                # response and understated the offset by 34.4 percent; the exact root-find is
                # 1.33 to 1.78 dx across the four runs graded to date. (2) I then asserted
                # that half a particle layer of surface convention exceeds the PASS band, so
                # a PASS could not be a physics result. THAT WAS WRONG. I had evaluated the
                # lever where the runs sit now (ratio ~1.5, shallow draft) rather than where
                # a PASS would sit. d(ratio)/ds = -ratio*A_w/V_cap falls 2.045x between the
                # two, so the lever is 8.0 to 15.1 points at today's operating points but
                # only 4.6 to 6.3 at a ratio-1.0 point, against a 10.0 point band. A PASS
                # carries about half a band of convention uncertainty: a real caveat, not a
                # disqualifying one. The FAIL is unaffected either way.
                "caveat": ("denominator uses a free-surface estimate blind within 2R of the "
                           "sphere axis; closing the discrepancy needs 1.33 to 1.78 dx of "
                           "surface offset (exact, not linearised). Half a particle layer of "
                           "surface convention is worth 8.0 to 15.1 ratio points at the "
                           "operating points observed so far and 4.6 to 6.3 at a ratio-1.0 "
                           "point, against a 10.0 point PASS band, so a PASS carries roughly "
                           "half a band of convention uncertainty and is not by itself a "
                           "coupling validation. A FAIL needs 1.72 to 2.66 particle layers to "
                           "overturn and is robust to it."),
            }

    st = blocking.stationarity(steady, n_sigma=STATIONARITY_N_SIGMA)
    se = blocking.blocked_se(steady)
    mean = float(np.mean(steady))
    err = mean - TARGET_N
    rel = abs(err) / TARGET_N

    # --- THE NOMINAL COMPANION -------------------------------------------------------
    # RESTRUCTURED 2026-08-19, slot d11-accessor. This block used to BE criterion 3 and to
    # own the top-level `band`; the manifest amendment makes it the mandatory companion.
    # It is never suppressed, because where it disagrees with the graded criterion THAT
    # DISAGREEMENT IS THE FINDING: it separates a coupling error from a draining tank.
    #
    # Its own non-stationarity is recorded here rather than used to refuse the whole run.
    # Manifest criterion 5 says a NOT-STATIONARY verdict on this series is "expected, not
    # disqualifying"; refusing the run on it contradicted criterion 5 directly and is why
    # all four job B runs previously returned a top-level NOT GRADEABLE with the graded
    # number buried one level down.
    #
    # The drift ratio is what criterion 5 actually asks for and it is the reason this
    # quantity cannot carry a verdict: on job 918450 the series moves 261 percent of the
    # error being claimed against it, so its window-robust "PASS" is a decaying series
    # caught inside the band, crossing the band edge about 8 frames after the run ended.
    nom_sweep, nom_bands = {}, set()
    for wname, ws in (("last 20", n_total - 20), ("last 50", n_total - 50),
                      ("last 100", n_total - 100), ("full series", 0)):
        if ws < 0:
            continue
        seg = fz[ws:]
        if len(seg) < 16:
            continue
        m = float(np.mean(seg))
        nom_sweep[wname] = {"mean_fz_N": m,
                            "rel_error_pct_signed": (m / TARGET_N - 1.0) * 100.0,
                            "band": _band_of(m / TARGET_N - 1.0)}
        nom_bands.add(nom_sweep[wname]["band"])

    drift_N = abs(st.get("slope_per_frame", 0.0)) * max(len(steady) - 1, 0)
    nominal_companion = {
        "graded": False,
        "target_N": TARGET_N,
        "target_is": "buoyancy on the submerged HEMISPHERE at the design waterline, "
                     "which equals the sphere's own weight m*g by construction of the "
                     "benchmark. NOT a fully submerged sphere, which would be 138.4360 N.",
        "mean_fz_N": mean,
        "abs_error_N": err,
        "rel_error": rel,
        "rel_error_pct_signed": (err / TARGET_N) * 100.0,
        "direction": "over" if err > 0 else "under",
        "band": _band_of(err / TARGET_N),
        "window_sweep": nom_sweep,
        "window_robust": len(nom_bands) == 1,
        "stationary": st.get("stationary", False),
        "slope_n_sigma": st.get("slope_n_sigma"),
        "drift_over_window_N": drift_N,
        "drift_as_pct_of_claimed_error": (100.0 * drift_N / abs(err)) if err else float("inf"),
        "note": ("reported under manifest criterion 5, which calls non-stationarity here "
                 "expected rather than disqualifying. A band from this quantity is an "
                 "average over a trend; read it with drift_as_pct_of_claimed_error."),
    }

    # --- THE TOP-LEVEL BAND IS CRITERION 3 -------------------------------------------
    # It comes from the graded quantity and from nowhere else. Previously it came from the
    # nominal path while the graded number sat inside measured_surface_criterion, so a
    # machine reading `band` got a verdict on a quantity the manifest does not grade.
    if measured is not None:
        band = measured["band"]
        refusal = measured.get("refusal_reason")
    else:
        band = "NOT GRADEABLE"
        refusal = ("fz_over_analytic_measured is absent from this run, so criterion 3's "
                   "graded quantity does not exist in it. Runs predating the measured-"
                   "surface instrumentation (e.g. job 917909) cannot be graded on "
                   "criterion 3 as amended 2026-08-19; only the companion is available.")

    return {
        "file": str(path),
        "n_frames_total": n_total,
        "stationary_start_frame": start,
        "n_frames_used": int(len(steady)),
        "window_detection": win_info,
        "band": band,
        "refusal_reason": refusal,
        "graded_quantity": "fz_over_analytic_measured",
        "criterion3": measured,
        "nominal_companion": nominal_companion,
        "mean_fz_N": mean,
        "target_N": TARGET_N,
        "abs_error_N": err,
        # rel_error is UNSIGNED because the bands are symmetric; rel_error_pct_signed
        # carries the direction. Reporting a negative newton error beside a positive
        # percentage, as an earlier version did, reads as a sign inconsistency and is
        # exactly the kind of thing a reader is right to distrust.
        # THESE TOP-LEVEL NOMINAL KEYS ARE RETAINED FOR EXISTING READERS and duplicate
        # nominal_companion. They are NOT the graded criterion. Do not band from them.
        "rel_error": rel,
        "rel_error_pct": rel * 100.0,
        "rel_error_pct_signed": (err / TARGET_N) * 100.0,
        "direction": "over" if err > 0 else "under",
        "stationarity_window": {k: v for k, v in st.items()
                                if not isinstance(v, (list, tuple))},
        "stationarity_full_series": {k: v for k, v in st_full.items()
                                     if not isinstance(v, (list, tuple))},
        "late_window_mean_N": float(np.mean(fz[int(0.9 * n_total):])),
        "measured_surface_criterion": measured,
        "measured_surface_available": have_measured,
        "se_blocked_N": se["se_blocked"],
        "se_naive_N": se["se_naive"],
        "se_is_lower_bound": se["se_is_lower_bound"],
        "se_converged": se["converged"],
        "inflation_vs_naive": se["inflation_vs_naive"],
        "tau_int_frames": se["tau_int_frames"],
        "plateau_block_size": se["plateau_block_size"],
        "plateau_n_blocks": se["plateau_n_blocks"],
        "n_sigma_from_target": (abs(err) / se["se_blocked"]) if se["se_blocked"] > 0 else float("inf"),
        "config": {k: cfg.get(k) for k in
                   ("n_grid", "lim_m", "dx_m", "depth_m", "h0_m", "frames",
                    "substeps", "sphere_cells_across", "sdf_res", "mode",
                    "analytic_buoyancy_N", "ref_mass_kg", "ref_natural_period_s_predicted")},
        "provenance": PROVENANCE,
    }


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("json_path", type=Path)
    p.add_argument("--drop-frac", type=float, default=None,
                   help="override transient exclusion with a fixed leading fraction")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    g = grade(a.json_path, a.drop_frac)
    if a.json:
        print(json.dumps(g, indent=2, sort_keys=True, default=str))
        return

    print(f"JOB B GRADE, criteria fixed in advance (manifest): "
          f"<={BAND_PASS*100:.0f}% PASS, {BAND_PASS*100:.0f}-{BAND_PARTIAL*100:.0f}% "
          f"REPORTABLE PARTIAL, >{BAND_PARTIAL*100:.0f}% FAIL\n")
    print(f"  frames total          {g['n_frames_total']}")

    print(f"  window start          frame {g['stationary_start_frame']} "
          f"({g['n_frames_used']} frames used)")

    # --- CRITERION 3, the graded quantity --------------------------------------------
    m = g.get("criterion3")
    print(f"\n  CRITERION 3, GRADED: {g['graded_quantity']}")
    print( "    fz / (closed form at the surface that EXISTS, not the design waterline)")
    if m:
        print(f"    mean ratio          {m['mean_ratio']:.4f}  "
              f"({m['rel_error_pct_signed']:+.3f}% from 1.0)")
        print(f"    blocked SE          {m['se_blocked']:.4f}"
              f"{'  (LOWER BOUND)' if m['se_is_lower_bound'] else ''}")
        print(f"    mean surface drop   {m['mean_surface_drop_m']*100:.3f} cm")
        print(f"    stationary          {m['stationary']} "
              f"(slope {m['slope_n_sigma']:.2f} sigma)")
        print(f"    window robustness   {'ROBUST' if m['window_robust'] else 'NOT ROBUST'}")
        for wname, w in m["window_sweep"].items():
            print(f"      {wname:<12} {w['mean_ratio']:.4f}  "
                  f"{w['rel_error_pct_signed']:+8.3f}%   {w['band']}")
    else:
        print("    NOT AVAILABLE in this run (predates the measured-surface instrumentation)")
    print(f"\n  BAND: {g['band']}")
    if g.get("refusal_reason"):
        print(f"  reason: {g['refusal_reason']}")
    if m:
        print(f"  CAVEAT: {m['caveat']}")

    # --- the mandatory companion, never suppressed -----------------------------------
    c = g["nominal_companion"]
    print(f"\n  COMPANION, NOT GRADED: nominal ratio against {c['target_N']:.4f} N")
    print(f"    {c['target_is']}")
    print(f"    mean steady reaction  {c['mean_fz_N']:.4f} N")
    print(f"    error                 {c['abs_error_N']:+.4f} N = "
          f"{c['rel_error_pct_signed']:+.3f}%  ({c['direction']}-predicts)  BAND: {c['band']}")
    print(f"    stationary            {c['stationary']} "
          f"(slope {c['slope_n_sigma']:.2f} sigma)")
    print(f"    drift over window     {c['drift_over_window_N']:.4f} N = "
          f"{c['drift_as_pct_of_claimed_error']:.1f}% OF THE ERROR BEING CLAIMED")
    print(f"    window robustness     "
          f"{'ROBUST' if c['window_robust'] else 'NOT ROBUST, verdict depends on window'}")
    for wname, w in c["window_sweep"].items():
        print(f"      {wname:<12} {w['mean_fz_N']:9.4f} N  "
              f"{w['rel_error_pct_signed']:+8.3f}%   {w['band']}")
    print(f"    blocked SE            {g['se_blocked_N']:.4f} N"
          f"{'  (LOWER BOUND, ladder did not converge)' if g['se_is_lower_bound'] else ''}, "
          f"naive {g['se_naive_N']:.4f} N, inflation {g['inflation_vs_naive']:.2f}x, "
          f"tau_int {g['tau_int_frames']:.1f}")

    if m and m["band"] != c["band"]:
        print(f"\n  THE TWO DISAGREE: criterion 3 says {m['band']}, the companion says "
              f"{c['band']}.\n  THAT DISAGREEMENT IS THE FINDING. One force lies between two "
              f"denominators, so the\n  signs are opposite by arithmetic, not by "
              f"contradiction. It separates a coupling\n  error from a draining tank. Read "
              f"the companion with its drift ratio attached.")


if __name__ == "__main__":
    main()
