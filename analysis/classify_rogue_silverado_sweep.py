#!/usr/bin/env python3
"""Classify the Rogue/Silverado grid sweep with the SAME classifier that produced the
17 gated verdicts, to test whether a verdict is resolution-dependent.

NON-CANONICAL, per Part 2.7 of the corrections register. This writes ONLY to
data/rogue_silverado_slide_classification_2026-08-13.csv. It never touches
data/all_runs_inventory.csv, data/failure_modes_by_run_classified.csv or
data/failure_modes_by_run.json.

WHY THIS IS NOT analysis/classify_failure_modes.py
  That script is hardcoded to the 17 Yaris runs: it reads data/all_runs_inventory.csv,
  refuses to proceed unless it finds exactly EXPECTED_RUNS = 17, and looks for
  timeseries under renders/yaris_render_s1/_incoming/, which is gitignored and absent
  from this checkout. It cannot be pointed at other runs without editing it, and editing
  it would put non-canonical runs through the canonical driver. This calls the same
  library function, simulation/failure_modes.classify_timeseries, directly instead.

INPUT is metrics.csv, which sim_standing.py already writes via FloodHistory.to_csv with
the full 15-column header including vx,vy,vz. That is the classifier's hard requirement
(failure_modes.REQUIRED_COLUMNS); the older 8-column timeseries in data/track1_sweep_v*/
lack the velocity columns and raise MissingKinematicsError.

ssf: 1.42, compact_sedan, the same value analysis/classify_failure_modes.py applies to
all 17. It is used for parity and it CANNOT affect this result: ssf feeds TOPPLE only
(failure_modes.py:184, :211). mass_kg likewise cannot change a verdict, it only scales
reported forces (failure_modes.py:130, :176).
"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))

import failure_modes as FM              # noqa: E402
from vehicle_params import get_vehicle  # noqa: E402

SSF = get_vehicle("compact_sedan")["ssf"]
OUT = REPO / "data" / "rogue_silverado_slide_classification_2026-08-13.csv"

LS6 = Path("/scratch/11603/jcerrell0629/rs_sweep_v2")
VISTA = Path("/work/11603/jcerrell0629/vista/class_specific_2026-08-08")

# mass: the values the runs actually used. Silverado 2270.0 is deck-header primary;
# Rogue 1571.3 is WEB-SOURCED only, the Rogue deck states no mass.
MASS = {"rogue": 1571.3, "silverado": 2270.0}

RUNS = []
for veh in ("rogue", "silverado"):
    RUNS.append((f"anchor_{veh}_g64", veh, 64,
                 VISTA / f"class_{veh}_g64" / "metrics.csv", "896273", "Vista GH200"))
    for g in (64, 96, 128):
        RUNS.append((f"rs_{veh}_g{g}", veh, g,
                     LS6 / f"rs_{veh}_g{g}" / "metrics.csv", "3362208", "LS6 A100"))


def main():
    SLIDE = FM.FailureMode.SLIDE
    rows = []
    for run, veh, grid, path, job, host in RUNS:
        if not path.exists():
            raise SystemExit(f"{run}: {path} missing. Refusing to emit a partial store.")
        r = FM.classify_timeseries(str(path), MASS[veh], SSF)
        rows.append({
            "run": run, "vehicle": veh, "n_grid": grid,
            "mass_kg": MASS[veh], "mode": r.mode.value,
            "triggered_slide": r.sustained[SLIDE],
            "ratio_slide": r.ratios[SLIDE],
            "max_surge_drift_m": r.max_surge_drift_m,
            "onset_frame_slide": r.first_index[SLIDE],
            "max_speed_ms": r.max_speed_ms,
            "peak_surge_accel_g": r.peak_surge_accel_g,
            "peak_surge_force_n": r.peak_surge_force_n,
            "max_vertical_lift_m": r.max_vertical_lift_m,
            "weight_n": r.weight_n, "ssf": r.ssf,
            "slide_m_threshold": FM.FailureThresholds().slide_m,
            "slide_speed_ms_threshold": FM.FailureThresholds().slide_speed_ms,
            "sustain_frames": FM.FailureThresholds().sustain_frames,
            "source_job": job, "source_host": host,
            "timeseries": str(path),
        })

    rows.sort(key=lambda d: (d["vehicle"], d["n_grid"], d["run"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT}, {len(rows)} rows")
    print()
    hdr = ("run", "grid", "mode", "sustained", "ratio_slide", "drift_m", "onset")
    print("%-22s%6s%8s%11s%13s%10s%7s" % hdr)
    for d in rows:
        print("%-22s%6d%8s%11s%13.4f%10.4f%7d"
              % (d["run"], d["n_grid"], d["mode"], d["triggered_slide"],
                 d["ratio_slide"], d["max_surge_drift_m"], d["onset_frame_slide"]))

    flips = {}
    for d in rows:
        flips.setdefault(d["vehicle"], []).append((d["n_grid"], d["mode"]))
    print()
    for veh, seq in flips.items():
        modes = {m for _, m in seq}
        print(f"{veh}: {' -> '.join(f'g{g}:{m}' for g, m in seq)}"
              f"   {'VERDICT IS RESOLUTION-DEPENDENT' if len(modes) > 1 else 'stable'}")


if __name__ == "__main__":
    main()
