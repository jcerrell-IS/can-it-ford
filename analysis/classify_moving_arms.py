"""Classify arms (a) and (b) across the resolution ladder.

WHAT "CLASSIFIED" MEANS FOR A DRIVEN VEHICLE, and why it is not the canonical scheme.
The canonical 17 are classified SLIDE / STUCK / TOPPLE / FLOAT, which are outcomes of a
FREE body subjected to flow. This scene PRESCRIBES the pose, so the hull cannot slide
or topple by construction and those labels are meaningless here. The question a driven
vehicle poses instead is whether the traction it needs exceeds the traction it has:

  TRACTION_OK          demand < available across the whole measured window
  TRACTION_MARGINAL    demand < available on the mean, but the window's max crosses 1
  TRACTION_EXCEEDED    demand > available on the mean of the window
  FLOATING             net normal load is zero, so no traction exists at any mu
  INDETERMINATE        the at-rest gate failed, so no force number is quotable

INDETERMINATE IS A REAL VERDICT HERE, NOT AN ERROR PATH. The at-rest vertical reaction
is the one quantity in this scene with an independent analytic target
(rho*g*V_submerged). If it does not agree, the drag demand is not measured either, and
the honest output is the resolution evidence rather than a number.

THE MEASUREMENT WINDOW IS PRESPECIFIED, not chosen after seeing the trace: ramp frames
are excluded by construction, and a further --skip-frames of drive settling is dropped.
Peak/mean is reported as a NON-STATIONARITY INDICATOR: a steady force would sit near 1,
and the exploratory scene measured Fz oscillating by a factor of 2 or more with no
steady value at 150 frames.

The full stationarity-and-uncertainty protocol (equilibration detection, blocking for
correlated samples) is DISPATCH 12's deliverable in analysis/stationarity.py. This
module deliberately does not duplicate it and does not claim its rigour: what is
reported here is a prespecified window with a spread, not a correlated-sample
uncertainty.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def classify(summary: dict, rows: list, skip_frames: int) -> dict:
    gate = summary.get("at_rest_gate", {})
    drive = [r for r in rows if r.get("phase") == "drive"]
    window = drive[skip_frames:] if len(drive) > skip_frames else []

    out = {
        "tag": summary.get("tag"), "n_grid": summary.get("n_grid"),
        "dx_m": summary.get("dx_m"), "depth_cells": summary.get("depth_cells"),
        "band_over_depth": summary.get("band_over_depth"),
        "water_layers": summary.get("water_layers"),
        "at_rest_gate_pass": gate.get("pass"),
        "at_rest_error_pct": gate.get("error_pct"),
        "n_drive": len(drive), "n_window": len(window), "skip_frames": skip_frames,
    }
    if not window:
        out["verdict"] = "NO_DATA"
        return out

    fy = np.array([r["force_N"][1] for r in window], dtype=float)
    fz = np.array([r["force_N"][2] for r in window], dtype=float)
    fn = np.array([r["F_N_net_normal_N"] for r in window], dtype=float)
    ratio = np.array([r["demand_over_avail_mu0p30"] for r in window], dtype=float)
    finite = np.isfinite(ratio)

    out.update({
        "drag_fy_mean_N": float(fy.mean()), "drag_fy_std_N": float(fy.std()),
        "drag_fy_min_N": float(fy.min()), "drag_fy_max_N": float(fy.max()),
        "fz_mean_N": float(fz.mean()), "fz_std_N": float(fz.std()),
        "F_N_mean_N": float(fn.mean()),
        "peak_over_mean_absfy": float(np.abs(fy).max() / max(np.abs(fy).mean(), 1e-12)),
        "peak_over_mean_absfz": float(np.abs(fz).max() / max(np.abs(fz).mean(), 1e-12)),
        "demand_over_avail_mean": float(ratio[finite].mean()) if finite.any() else None,
        "demand_over_avail_max": float(ratio[finite].max()) if finite.any() else None,
        "n_nonfinite_ratio": int((~finite).sum()),
    })

    # Verdict. Gate first: an unquotable scene cannot produce a traction verdict.
    if gate.get("pass") is False:
        out["verdict"] = "INDETERMINATE"
        out["verdict_reason"] = (
            f"at-rest gate FAILED at {gate.get('error_pct'):+.2f}% against "
            f"rho*g*V_submerged, so no force number from this run is quotable. "
            f"Water depth is {summary.get('depth_cells'):.2f} cells against the "
            f"validated harness's 18.")
    elif fn.mean() <= 0.0:
        out["verdict"] = "FLOATING"
        out["verdict_reason"] = "net normal load is zero: buoyancy exceeds weight"
    elif out["demand_over_avail_mean"] is None:
        out["verdict"] = "NO_DATA"
    elif out["demand_over_avail_mean"] > 1.0:
        out["verdict"] = "TRACTION_EXCEEDED"
        out["verdict_reason"] = (
            f"mean demand/available = {out['demand_over_avail_mean']:.3f} > 1 at mu=0.30")
    elif out["demand_over_avail_max"] > 1.0:
        out["verdict"] = "TRACTION_MARGINAL"
        out["verdict_reason"] = (
            f"mean {out['demand_over_avail_mean']:.3f} but window max "
            f"{out['demand_over_avail_max']:.3f} crosses 1")
    else:
        out["verdict"] = "TRACTION_OK"
        out["verdict_reason"] = (
            f"max demand/available = {out['demand_over_avail_max']:.3f} < 1 at mu=0.30")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", required=True, type=Path,
                    help="directory holding <tag>_summary.json and <tag>_trace.json")
    ap.add_argument("--tags", nargs="+", default=["driven_g64", "driven_g96", "driven_g128"])
    ap.add_argument("--skip-frames", type=int, default=15,
                    help="drive frames dropped after the ramp; PRESPECIFIED")
    ap.add_argument("--csv-out", type=Path, default=None)
    args = ap.parse_args()

    results = []
    for tag in args.tags:
        s_path = args.out_dir / f"{tag}_summary.json"
        t_path = args.out_dir / f"{tag}_trace.json"
        if not s_path.exists():
            print(f"  (missing {s_path.name}, skipping)")
            continue
        summary = json.loads(s_path.read_text())
        rows = json.loads(t_path.read_text()) if t_path.exists() else []
        results.append(classify(summary, rows, args.skip_frames))

    if not results:
        print("No runs found. Nothing to classify.")
        return 1

    print("=" * 104)
    print("DISPATCH 9: arms (a) and (b) across the resolution ladder")
    print("=" * 104)
    print(f"\n{'tag':<14}{'n_grid':>7}{'dx':>9}{'d_cells':>9}{'gate':>7}"
          f"{'gate_err%':>11}{'drag_Fy':>11}{'pk/mean':>9}{'dem/avail':>11}  verdict")
    print("-" * 104)
    for r in results:
        gate = "PASS" if r["at_rest_gate_pass"] else "FAIL"
        err = r["at_rest_error_pct"]
        print(f"{str(r['tag']):<14}{r['n_grid']:>7}{r['dx_m']:>9.4f}"
              f"{r['depth_cells']:>9.2f}{gate:>7}"
              f"{(f'{err:+.1f}' if err is not None else 'n/a'):>11}"
              f"{r.get('drag_fy_mean_N', float('nan')):>11.1f}"
              f"{r.get('peak_over_mean_absfy', float('nan')):>9.2f}"
              f"{(r.get('demand_over_avail_mean') if r.get('demand_over_avail_mean') is not None else float('nan')):>11.3f}"
              f"  {r['verdict']}")

    print("\nVERDICT REASONS:")
    for r in results:
        print(f"  {r['tag']}: {r.get('verdict_reason', '-')}")

    # The resolution question this ladder exists to answer.
    verdicts = {r["verdict"] for r in results}
    ratios = [r.get("demand_over_avail_mean") for r in results
              if r.get("demand_over_avail_mean") is not None]
    print("\nRESOLUTION DEPENDENCE:")
    if len(verdicts) > 1:
        print(f"  THE VERDICT CHANGES WITH RESOLUTION: {sorted(verdicts)}")
        print("  That is a result, and it matches the project's own register J15 finding")
        print("  that a verdict can be resolution-dependent. It is not a bug to be tuned")
        print("  away, and no single-resolution number should be quoted without it.")
    else:
        print(f"  All {len(results)} rungs classify {sorted(verdicts)[0]}.")
    if len(ratios) > 1:
        span = max(ratios) - min(ratios)
        base = abs(ratios[0]) if ratios[0] else 1.0
        print(f"  demand/available spans {min(ratios):.3f} to {max(ratios):.3f} "
              f"(range {span:.3f}, {100*span/base:.1f}% of the coarsest rung)")
        print("  Monotone movement here means the drag demand is not resolved; a flat")
        print("  line means it is, at least on this measure.")

    print("\nCAVEATS: every drag number above is a NET reaction that cannot be")
    print("decomposed into hydrodynamic, contact and gravitational parts. Any run whose")
    print("at-rest gate FAILED is resolution evidence, not a measurement. The window is")
    print("prespecified, not stationarity-tested; the correlated-sample protocol is")
    print("Dispatch 12's deliverable.")

    if args.csv_out:
        import csv
        keys = sorted({k for r in results for k in r})
        with args.csv_out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in results:
                w.writerow(r)
        print(f"\nwrote {args.csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
