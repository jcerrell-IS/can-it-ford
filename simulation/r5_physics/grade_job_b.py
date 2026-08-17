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
    try:
        win = blocking.find_stationary_window(fz)
        start = int(win.get("start", 0)) if isinstance(win, dict) else 0
        win_info = win if isinstance(win, dict) else {"raw": str(win)}
    except Exception as e:                      # noqa: BLE001
        start = int(round((drop_frac if drop_frac is not None else 0.5) * n_total))
        win_info = {"error": f"{type(e).__name__}: {e}", "fallback_start": start}

    if drop_frac is not None:
        start = int(round(drop_frac * n_total))

    steady = fz[start:]
    if len(steady) < 16:
        raise SystemExit(f"stationary window too short: {len(steady)} frames from {n_total}")

    se = blocking.blocked_se(steady)
    mean = float(np.mean(steady))
    err = mean - TARGET_N
    rel = abs(err) / TARGET_N

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


if __name__ == "__main__":
    main()
