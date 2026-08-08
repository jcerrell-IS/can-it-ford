#!/usr/bin/env python3
"""Collect the Bingham / Herschel-Bulkley sensitivity ladder into one table.

NOT a canonical result set. See analysis/bingham_sweep/README.md.

The verdict column applies DRIFT_THRESHOLD = 0.05 m to final_disp_mag_m, the same
literal the 17 gated runs use. CLAUDE.md item 13: that threshold has NO peer-reviewed
source and is declared in 16 places under four names. It is used here because it is what
the published verdicts use, not because it is defensible.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SWEEP = HERE / "bingham_sweep"
DRIFT_THRESHOLD_M = 0.05  # unit: METRES. Not the speed literal at failure_modes.py:47.

# canonical g64_m1100, data/all_runs_inventory.csv, produced on Vista GH200
CANON_DISP = 0.6585370302200317
CANON_PASSTHROUGH = 0.10670498480368847

ORDER = [
    "tau0p0_control", "tau0p1", "tau1p0", "tau3p0", "tau10p0", "tau30p0", "tau100p0",
    "etacoup_tau3p1", "etacoup_tau40p0", "hb_tau10_K5_n0p8", "hb_tau0_K5_n0p8",
]


def main() -> int:
    rows = []
    for tag in ORDER:
        f = SWEEP / tag / "summary.json"
        if not f.exists():
            print(f"  (missing: {tag})")
            continue
        r = json.loads(f.read_text())
        # key on the DIRECTORY tag, not summary["label"]: the control was launched by
        # hand as --label control_g64_m1100 before the ladder script existed, so the
        # label and the tag disagree for exactly that one point.
        r["tag"] = tag
        rows.append(r)

    if not rows:
        print("no results yet")
        return 1

    base = next((r for r in rows if r["tag"] == "tau0p0_control"), None)
    if base is None:
        print("no control point; cannot normalize")
        return 1
    base_disp = base["final_disp_mag_m"]

    out = SWEEP / "bingham_sweep_results.csv"
    cols = ["label", "tau_y_pa", "hb_K", "hb_n", "water_eta", "eta_cap_pas", "substeps",
            "final_disp_mag_m", "pct_vs_control", "verdict",
            "passthrough_max_frac", "C2_veh_zmin_rise", "final_yaw_deg"]
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            d = r["final_disp_mag_m"]
            w.writerow([r["tag"], r["tau_y_pa"], r["hb_K"], r["hb_n"], r["water_eta"],
                        r["eta_cap_pas"], r["substeps"], d,
                        100.0 * (d / base_disp - 1.0),
                        "NO-FORD" if d > DRIFT_THRESHOLD_M else "FORD",
                        r["passthrough_max_frac"], r["C2_veh_zmin_rise"],
                        r["final_yaw_deg"]])

    print(f"# Bingham / Herschel-Bulkley sensitivity ladder, g64 / 1100 kg / "
          f"depth 0.30 m / velocity 1.5 m/s / 90 frames")
    print(f"# venue: Mac CPU-ARM (warp 1.16.0, no CUDA). Canonical runs were Vista GH200.")
    print(f"# control vs canonical: {base_disp!r} vs {CANON_DISP!r} "
          f"({100.0 * (base_disp / CANON_DISP - 1.0):+.4f} percent)\n")
    hdr = (f"{'label':<18}{'tau_y':>8}{'K':>6}{'n':>6}{'eta':>8}{'eta_cap':>10}"
           f"{'sub':>5}{'disp (m)':>12}{'vs ctrl':>10}{'verdict':>9}{'passthru':>10}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        d = r["final_disp_mag_m"]
        print(f"{r['tag']:<18}{r['tau_y_pa']:>8.1f}{r['hb_K']:>6.1f}{r['hb_n']:>6.2f}"
              f"{r['water_eta']:>8.3f}{r['eta_cap_pas']:>10.2f}{r['substeps']:>5}"
              f"{d:>12.6f}{100.0 * (d / base_disp - 1.0):>9.2f}%"
              f"{('NO-FORD' if d > DRIFT_THRESHOLD_M else 'FORD'):>9}"
              f"{r['passthrough_max_frac']:>10.5f}")

    disps = [r["final_disp_mag_m"] for r in rows]
    verdicts = {("NO-FORD" if d > DRIFT_THRESHOLD_M else "FORD") for d in disps}
    print(f"\n  displacement range: {min(disps):.6f} to {max(disps):.6f} m "
          f"(spread {100.0 * (max(disps) / min(disps) - 1.0):.2f} percent)")
    print(f"  distinct verdicts across the whole ladder: {sorted(verdicts)}")
    print(f"  margin to DRIFT_THRESHOLD {DRIFT_THRESHOLD_M} m: "
          f"min displacement is {min(disps) / DRIFT_THRESHOLD_M:.1f}x the threshold")
    print(f"\n  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
