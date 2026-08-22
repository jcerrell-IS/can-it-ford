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
    ratio_key = "fz_over_analytic_measured"
    have_measured = ratio_key in rows[0]
    measured = None
    if have_measured:
        rr = np.array([r[ratio_key] for r in rows], dtype=float)[start:]
        rr = rr[np.isfinite(rr)]
        if len(rr) >= 16:
            r_mean = float(np.mean(rr))
            r_se = blocking.blocked_se(rr)
            r_rel = abs(r_mean - 1.0)
            measured = {
                "mean_ratio": r_mean,
                "rel_error": r_rel,
                "rel_error_pct_signed": (r_mean - 1.0) * 100.0,
                "se_blocked": r_se["se_blocked"],
                "se_is_lower_bound": r_se["se_is_lower_bound"],
                "band": ("PASS" if r_rel <= BAND_PASS else
                         "REPORTABLE PARTIAL" if r_rel <= BAND_PARTIAL else "FAIL"),
                "mean_surface_drop_m": float(np.mean(
                    [r.get("surface_drop_m", float("nan")) for r in rows][start:])),
            }

    st = blocking.stationarity(steady, n_sigma=STATIONARITY_N_SIGMA)
    se = blocking.blocked_se(steady)
    mean = float(np.mean(steady))
    err = mean - TARGET_N
    rel = abs(err) / TARGET_N

    # Second refusal gate. Even with a window in hand, a series the stationarity test
    # rejects has no steady value, and a band computed from it would be an average of a
    # trend rather than a measurement.
    if not st.get("stationary", False):
        return {
            "file": str(path),
            "n_frames_total": n_total,
            "stationary_start_frame": start,
            "n_frames_used": int(len(steady)),
            "band": "NOT GRADEABLE",
            "refusal_reason": (
                "blocking.stationarity rejects this series "
                f"(halves_stationary={st.get('halves_stationary')}, "
                f"trend_stationary={st.get('trend_stationary')}, "
                f"slope={st.get('slope_per_frame'):+.5f} N/frame at "
                f"{st.get('slope_n_sigma'):.2f} sigma). A mean over a trend is not a "
                "steady value."),
            # THE PROMISE AT THE TOP OF THIS FUNCTION WAS BROKEN HERE. The measured-surface
            # criterion is documented as "reported ALONGSIDE the nominal grade, never
            # instead of it", and this refusal path omitted the key entirely. Both real
            # runs refuse, so the tool had NEVER emitted that criterion for real data, and
            # the +60.8% in the job B document was computed by hand OUTSIDE the tool built
            # to stop hand-computed grading. Same defect class as the one this file's own
            # header documents. It is emitted on the refusal path too now.
            "measured_surface_criterion": measured,
            "measured_surface_available": have_measured,
            "stationarity_window": {k: v for k, v in st.items()
                                   if not isinstance(v, (list, tuple))},
            "stationarity_full_series": {k: v for k, v in st_full.items()
                             if not isinstance(v, (list, tuple))},
            "window_detection": win_info,
            "mean_over_window_N": mean,
            "late_window_mean_N": float(np.mean(fz[int(0.9 * n_total):])),
            "provenance": PROVENANCE,
            "config": {k: cfg.get(k) for k in ("n_grid", "lim_m", "frames", "mode")},
        }

    if rel <= BAND_PASS:
        band = "PASS"
    elif rel <= BAND_PARTIAL:
        band = "REPORTABLE PARTIAL"
    else:
        band = "FAIL"

    return {
        "file": str(path),
        "n_frames_total": n_total,
        "stationary_start_frame": start,
        "n_frames_used": int(len(steady)),
        "window_detection": win_info,
        "mean_fz_N": mean,
        "target_N": TARGET_N,
        "abs_error_N": err,
        # rel_error is UNSIGNED because the bands are symmetric; rel_error_pct_signed
        # carries the direction. Reporting a negative newton error beside a positive
        # percentage, as an earlier version did, reads as a sign inconsistency and is
        # exactly the kind of thing a reader is right to distrust.
        "rel_error": rel,
        "rel_error_pct": rel * 100.0,
        "rel_error_pct_signed": (err / TARGET_N) * 100.0,
        "direction": "over" if err > 0 else "under",
        "band": band,
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

    # A refusal carries no mean, no SE and no band. Printing the full report would crash
    # on the missing keys, which is how the first version of main() behaved.
    if g["band"] == "NOT GRADEABLE":
        print(f"  window start          {g.get('stationary_start_frame', 'n/a')}")
        print(f"  late-window mean      {g.get('late_window_mean_N', float('nan')):.4f} N")
        print(f"  target                {TARGET_N:.4f} N")
        print(f"\n  BAND: NOT GRADEABLE")
        print(f"  reason: {g['refusal_reason']}")
        m = g.get("measured_surface_criterion")
        if m:
            print(f"    measured-surface ratio {m['mean_ratio']:.4f} "
                  f"({m['rel_error_pct_signed']:+.2f}% from 1.0)  BAND: {m['band']}")
        return

    print(f"  stationary window     from frame {g['stationary_start_frame']} "
          f"({g['n_frames_used']} frames used)")
    print(f"  mean steady reaction  {g['mean_fz_N']:.4f} N")
    print(f"  target                {g['target_N']:.4f} N  (rho_w=998.2, g=9.81)")
    print(f"  error                 {g['abs_error_N']:+.4f} N  = "
          f"{g['rel_error_pct_signed']:+.3f}%  ({g['direction']}-predicts the closed form)")
    print(f"  blocked SE            {g['se_blocked_N']:.4f} N"
          f"{'  (LOWER BOUND, ladder did not converge)' if g['se_is_lower_bound'] else ''}")
    print(f"  naive SE              {g['se_naive_N']:.4f} N, "
          f"inflation {g['inflation_vs_naive']:.2f}x, tau_int {g['tau_int_frames']:.1f} frames")
    print(f"  plateau               block size {g['plateau_block_size']}, "
          f"{g['plateau_n_blocks']} blocks")
    print(f"  distance from target  {g['n_sigma_from_target']:.1f} blocked SE")
    print(f"\n  BAND: {g['band']}")
    if g["se_is_lower_bound"]:
        print("  WARNING: the blocked SE is a lower bound, so this band is optimistic.")

    m = g.get("measured_surface_criterion")
    if m:
        print(f"\n  MEASURED-SURFACE CRITERION (fz / closed form at the surface that exists)")
        print(f"    mean ratio          {m['mean_ratio']:.4f}  "
              f"({m['rel_error_pct_signed']:+.3f}% from 1.0)")
        print(f"    blocked SE          {m['se_blocked']:.4f}"
              f"{'  (LOWER BOUND)' if m['se_is_lower_bound'] else ''}")
        print(f"    mean surface drop   {m['mean_surface_drop_m']*100:.3f} cm")
        print(f"    BAND: {m['band']}")
        if m["band"] != g["band"]:
            print(f"    NOTE: this DISAGREES with the nominal band ({g['band']}). The "
                  f"disagreement is the finding:\n          it separates a coupling error "
                  f"from a falling free surface, which job 917909 could not.")
    elif not g.get("measured_surface_available"):
        print("\n  measured-surface criterion: NOT AVAILABLE in this run "
              "(predates the instrumentation)")


if __name__ == "__main__":
    main()
