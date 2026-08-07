"""
classify_failure_modes.py

Runs simulation/failure_modes.py over all 17 gated runs and writes the run-keyed
classification to data/failure_modes_by_run_classified.csv. Also re-emits
data/failure_modes_by_run.json, whose original generator (scratchpad/classify_17_runs.py,
2026-08-05) no longer exists in the repo; regenerating it here makes that artifact
reproducible from tracked code instead of un-regenerable.

PROVENANCE
  Run list      data/all_runs_inventory.csv, 17 rows. THE canonical 17-run results file.
  Source data   renders/yaris_render_s1/_incoming/<run>/metrics.csv (time series) and
                <run>/summary.json (scalars). The duplicate trees at
                renders/yaris_render_s1/{g64_m1100,m1100,...}/ are NOT canonical;
                all_runs_inventory.csv's summary_path column resolves to _incoming/.
  Solver        kks32/mpm-engine, vendored at third_party/mpm-engine-544c93dd,
                pinned SHA 544c93dd02cb9c7ead89e1155a62967243244fce, MIT.
                Driver renders/yaris_render_s1/sim_standing.py, which imports
                warpmpm.core.solver, warpmpm.materials.newtonian, warpmpm.vehicle.
                NOT Genesis. Do not relabel.
  Vehicle       yaris_coarse_v1l_watertight.ply, one hull, mass overrides only
                (1100 / 1609 / 2337 kg). 8,905 particles in all three; geometry never
                changes, so the AR&R class label denotes only which limit set applies.
  Classifier    simulation/failure_modes.py, classify_timeseries(), STOCK THRESHOLDS.
                slide_m 0.05, slide_speed_ms 0.05, float_m 0.05, float_speed_ms 0.02,
                sustain_frames 3. This script modifies no threshold.
  SSF           vehicle_params.get_vehicle('compact_sedan')['ssf'] = 1.42. get_vehicle
                accepts only compact_sedan|midsize_suv|light_pickup, NOT the AR&R labels
                in the inventory's `label` column.
  G             9.80665, failure_modes.py:14 (post-processing only; the solver itself
                hardcodes 9.81, core/solver.py:167-169, a 0.034 percent fork).

OUTCOME STRUCTURE
  Three possible outcomes per run: SLIDE, TOPPLE, FLOAT. STUCK is not a fourth mode
  scored on its own scale; it is the "none of the three sustained" case
  (failure_modes.py:229-230) and carries no threshold, ratio-of-record or onset frame.
  The winning-mode columns are therefore EMPTY on a STUCK row, not zero.
  When more than one mode sustains, failure_modes.py:232 reports the last in
  MODE_SEVERITY = (SLIDE, TOPPLE, FLOAT), i.e. FLOAT > TOPPLE > SLIDE.

CAVEAT LABELS, carried into the CSV consumer's hands deliberately
  triggered_* is the authoritative per-mode outcome. ratio_* is MAGNITUDE ONLY. They
  disagree: sweepV_g64_v0p5 has ratio_slide 1.14 and is STUCK, and sweepV_g64_v3p0 has
  ratio_float 1.07 and is SLIDE, because each mode needs a JOINT displacement-and-speed
  condition held for 3 consecutive frames (failure_modes.py:179-185), not a peak.
  Filtering this CSV on ratio >= 1 gives the wrong count.

  slide_m = float_m = 0.05 m is an INTERNAL NUMERICAL ONSET DETECTOR
  (failure_modes.py:46,48). It has no peer-reviewed source, and the attribution to
  Smith, Modra & Felder 2019 Eq. 6 is a misattribution: that equation contains no such
  criterion.

  ssf = 1.42 is an ESTIMATE flagged "CONFIRM before use" at vehicle_params.py:108.
  Every TOPPLE ratio scales as 1/ssf. SLIDE, FLOAT and STUCK do not depend on it.

  TOPPLE tests SURGE acceleration against SSF. SSF is a lateral rollover ratio, and that
  is the correct axis here ONLY because the vehicle's long axis is y while surge is x
  (vehicle_live.py:277-278), so flow strikes the vehicle's side. Do not carry this
  criterion to a scene where the vehicle faces the flow.

  peak_surge_accel_g is np.gradient(vel, t) (failure_modes.py:127) over a 30 Hz rigid-body
  trace: single-frame values reach 3.78 g and are numerical, not physical. The
  sustain_frames guard is what keeps TOPPLE from firing. Never quote the raw ratio alone.

  metrics.csv pitch_deg/roll_deg are VEHICLE-BODY-SENSE, not raw Euler: vehicle_live.py
  computes raw ZYX Euler at :55-61 then swaps two of them at :295-300, so roll_deg is the
  raw Euler pitch (about y, the long axis). The classifier reads NEITHER column, so the
  ZYX gimbal singularity at |roll_deg| -> 90 cannot affect any verdict here. Max
  |roll_deg| over all 17 runs is 4.625 deg.

Usage
  /opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python \
      analysis/classify_failure_modes.py
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))

import failure_modes as FM  # noqa: E402
from vehicle_params import get_vehicle  # noqa: E402

INVENTORY = REPO / "data" / "all_runs_inventory.csv"
INCOMING = REPO / "renders" / "yaris_render_s1" / "_incoming"
OUT_CSV = REPO / "data" / "failure_modes_by_run_classified.csv"
OUT_JSON = REPO / "data" / "failure_modes_by_run.json"
# Gitignored byte-twin (.gitignore:14). NOT authoritative and NOT written here; only
# checked for drift, because a copy git cannot see is a copy review cannot catch.
SHADOW_JSON = REPO / "renders" / "yaris_render_s1" / "failure_modes_by_run.json"

EXPECTED_RUNS = 17
PARAMS_CLASS = "compact_sedan"

MODES = ("SLIDE", "TOPPLE", "FLOAT")

CSV_COLUMNS = [
    "run", "mode",
    "triggered_slide", "triggered_topple", "triggered_float",
    "ratio_slide", "ratio_topple", "ratio_float",
    "onset_frame_slide", "onset_frame_topple", "onset_frame_float",
    "first_reached_frame", "first_reached_time_s",
    "threshold_value", "threshold_units",
    "percent_over_threshold", "absolute_over_threshold", "magnitude_ratio",
    "max_surge_drift_m", "max_vertical_lift_m", "max_speed_ms", "peak_surge_accel_g",
    "peak_surge_force_n", "peak_vertical_force_n", "weight_n",
    "arr_class_label", "mass_kg", "n_grid", "realized_depth_m", "velocity_ms",
    "ssf_used", "n_frames", "timeseries",
]


def _r(value, ndigits):
    """Round, preserving None. STUCK rows carry None in the winning-mode block and must
    not be coerced to 0."""
    return None if value is None else round(float(value), ndigits)


def _blank(value):
    return "" if value is None else value


def classify_all(ssf: float) -> list[dict]:
    rows = list(csv.DictReader(open(INVENTORY, newline="")))
    if len(rows) != EXPECTED_RUNS:
        raise SystemExit(f"{INVENTORY.name}: expected {EXPECTED_RUNS} runs, found {len(rows)}")

    out = []
    for row in rows:
        run = row["run"]
        run_dir = INCOMING / run
        ts = run_dir / "metrics.csv"
        if not ts.exists():
            raise SystemExit(f"{run}: {ts} missing. Refusing to emit a partial store.")

        mass = float(row["mass_kg"])
        summ_path = run_dir / "summary.json"
        if summ_path.exists():
            summ_mass = float(json.loads(summ_path.read_text())["mass_kg"])
            if abs(summ_mass - mass) > 1e-9:
                raise SystemExit(
                    f"{run}: inventory mass_kg {mass} != summary.json mass_kg {summ_mass}"
                )
        else:
            raise SystemExit(f"{run}: {summ_path} missing, cannot cross-check mass.")

        res = FM.classify_timeseries(str(ts), mass, ssf)
        ratios = {m.value: v for m, v in res.ratios.items()}
        sustained = {m.value: v for m, v in res.sustained.items()}
        first_index = {m.value: v for m, v in res.first_index.items()}
        n_frames = len(FM.load_timeseries(ts)["t"])

        out.append({
            "run": run,
            "mode": res.mode.value,
            "arr_class_label": row["label"],
            "mass_kg": mass,
            "n_grid": int(row["n_grid"]),
            "realized_depth_m": float(row["realized_depth_m"]),
            "velocity_ms": float(row["velocity_ms"]),
            "ssf_used": ssf,
            "first_reached_frame": res.first_reached_frame,
            # 6 dp, not the 4 dp that failure_modes.classify_manifest():291 uses. This
            # matches the 2026-08-05 artifact and is what makes it byte-reproducible.
            "first_reached_time_s": _r(res.first_reached_time, 6),
            "threshold_value": _r(res.threshold_value, 4),
            "threshold_units": res.threshold_units,
            "percent_over_threshold": _r(res.percent_over_threshold, 4),
            "absolute_over_threshold": _r(res.absolute_over_threshold, 8),
            "magnitude_ratio": _r(res.magnitude_ratio, 6),
            "ratios": {m: round(ratios[m], 6) for m in MODES},
            "sustained": {m: bool(sustained[m]) for m in MODES},
            "first_index": {m: int(first_index[m]) for m in MODES},
            "max_surge_drift_m": _r(res.max_surge_drift_m, 8),
            "max_vertical_lift_m": _r(res.max_vertical_lift_m, 8),
            "max_speed_ms": _r(res.max_speed_ms, 8),
            "peak_surge_force_n": _r(res.peak_surge_force_n, 4),
            "peak_vertical_force_n": _r(res.peak_vertical_force_n, 4),
            "peak_surge_accel_g": _r(res.peak_surge_accel_g, 8),
            "weight_n": _r(res.weight_n, 4),
            "timeseries": str(ts.relative_to(REPO)),
            "n_frames": n_frames,
        })
    return out


def write_csv(records: list[dict]) -> None:
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in records:
            flat = {
                "run": r["run"],
                "mode": r["mode"],
                "threshold_units": r["threshold_units"],
                "arr_class_label": r["arr_class_label"],
                "mass_kg": r["mass_kg"],
                "n_grid": r["n_grid"],
                "realized_depth_m": r["realized_depth_m"],
                "velocity_ms": r["velocity_ms"],
                "ssf_used": r["ssf_used"],
                "n_frames": r["n_frames"],
                "timeseries": r["timeseries"],
            }
            for m in MODES:
                flat[f"triggered_{m.lower()}"] = r["sustained"][m]
                flat[f"ratio_{m.lower()}"] = r["ratios"][m]
                flat[f"onset_frame_{m.lower()}"] = r["first_index"][m]
            # Winning-mode block: blank on STUCK, never zero (see OUTCOME STRUCTURE).
            for k in ("first_reached_frame", "first_reached_time_s", "threshold_value",
                      "percent_over_threshold", "absolute_over_threshold",
                      "magnitude_ratio"):
                flat[k] = _blank(r[k])
            for k in ("max_surge_drift_m", "max_vertical_lift_m", "max_speed_ms",
                      "peak_surge_accel_g", "peak_surge_force_n",
                      "peak_vertical_force_n", "weight_n"):
                flat[k] = r[k]
            w.writerow(flat)


def _committed_bytes(path: Path) -> bytes | None:
    """The blob at git HEAD, NOT the working-tree file. Comparing against the working
    tree is worthless here: a previous run of this script has already overwritten it."""
    rel = path.relative_to(REPO).as_posix()
    proc = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
                          capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def write_json(records: list[dict], ssf: float) -> bool:
    """Re-emit data/failure_modes_by_run.json. Returns True if the RUNS PAYLOAD matches
    the committed copy.

    Payload, not whole-file bytes. The committed `_provenance.generator` names
    `scratchpad/classify_17_runs.py`, a path that does not exist in the repo, so
    reproducing the file byte-for-byte would perpetuate a pointer to a missing
    generator: the exact defect that condemned failure_modes_result.json. The
    verdicts are what must reproduce, and they do; the provenance block is corrected
    to name this script. Register D6a."""
    before_raw = _committed_bytes(OUT_JSON)
    before = json.loads(before_raw)["runs"] if before_raw else None
    th = FM.FailureThresholds()
    doc = {
        "_provenance": {
            "generated": "2026-08-05",
            "regenerated": "2026-08-07, provenance block corrected",
            "generator": "analysis/classify_failure_modes.py",
            "generator_note": "The 2026-08-05 original named scratchpad/classify_17_runs.py, "
                              "which no longer exists in the repo. This script reproduces "
                              "that run's verdicts on all 17 runs exactly; only this "
                              "provenance block differs. Register D6a.",
            "classifier": "simulation/failure_modes.py, classify_timeseries()",
            "run_list_source": "data/all_runs_inventory.csv (17 rows)",
            "timeseries_source": "renders/yaris_render_s1/_incoming/<run>/metrics.csv",
            "mass_source": "all_runs_inventory.csv mass_kg, cross-checked against "
                           "<run>/summary.json mass_kg",
            "ssf": ssf,
            "ssf_source": "vehicle_params.py:108 (compact_sedan). ESTIMATE, flagged "
                          "'CONFIRM before use'. Only the TOPPLE criterion depends on "
                          "it; SLIDE, FLOAT and STUCK do not.",
            "thresholds": {
                "slide_m": th.slide_m,
                "slide_speed_ms": th.slide_speed_ms,
                "float_m": th.float_m,
                "float_speed_ms": th.float_speed_ms,
                "sustain_frames": th.sustain_frames,
            },
            "threshold_caveat": "slide_m = float_m = 0.05 m is an internal numerical "
                                "onset detector, not a peer-reviewed distance criterion "
                                "(failure_modes.py:46,48; CLAUDE.md item 13).",
            "G_postprocessing": FM.G,
            "notes": "Supersedes renders/yaris_render_s1/failure_modes_result.json, "
                     "which is keyed by AR&R class rather than run id, carries no run "
                     "identifier, and is written by no script in the repo.",
        },
        "runs": {r["run"]: {k: v for k, v in r.items() if k != "run"} for r in records},
    }
    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n")
    # Compare the runs payload against the committed copy, NOT whole-file bytes: the
    # provenance block is deliberately corrected (see docstring), so a byte comparison
    # would always report False and hide a real payload regression behind it.
    return before is not None and doc["runs"] == before


def main() -> None:
    ssf = get_vehicle(PARAMS_CLASS)["ssf"]
    records = classify_all(ssf)

    write_csv(records)
    reproduces = write_json(records, ssf)
    doc_runs = json.loads(OUT_JSON.read_text())["runs"]

    counts = {}
    for r in records:
        counts[r["mode"]] = counts.get(r["mode"], 0) + 1

    print(f"classifier simulation/failure_modes.py, stock thresholds "
          f"{FM.FailureThresholds()}, ssf {ssf} ({PARAMS_CLASS})")
    print()
    print("%-18s %-6s %8s %8s %8s  %-5s %-5s %-5s" %
          ("run", "mode", "r_SLIDE", "r_TOPPLE", "r_FLOAT", "tSLI", "tTOP", "tFLO"))
    for r in records:
        print("%-18s %-6s %8.4f %8.4f %8.4f  %-5s %-5s %-5s" % (
            r["run"], r["mode"], r["ratios"]["SLIDE"], r["ratios"]["TOPPLE"],
            r["ratios"]["FLOAT"], r["sustained"]["SLIDE"], r["sustained"]["TOPPLE"],
            r["sustained"]["FLOAT"]))

    print()
    print(f"{len(records)} runs: " + ", ".join(f"{n} {m}" for m, n in sorted(counts.items())))
    ratio_ge1 = {m: sum(1 for r in records if r["ratios"][m] >= 1.0) for m in MODES}
    trig = {m: sum(1 for r in records if r["sustained"][m]) for m in MODES}
    for m in MODES:
        print(f"  {m:<7} ratio >= 1 in {ratio_ge1[m]:2d} runs, triggered in {trig[m]:2d}")
    print()
    print(f"wrote {OUT_CSV.relative_to(REPO)}")
    print(f"wrote {OUT_JSON.relative_to(REPO)}")
    print(f"JSON runs payload matches committed copy: {reproduces}"
          f"{'' if reproduces else '  <-- VERDICTS CHANGED, STOP AND INVESTIGATE'}")

    # The renders/ copy is gitignored (.gitignore:14) and cannot be kept honest by
    # review, so warn on drift rather than silently letting two stores disagree.
    if SHADOW_JSON.exists():
        same = json.loads(SHADOW_JSON.read_text()).get("runs") == doc_runs
        if not same:
            print(f"\nNOTE {SHADOW_JSON.relative_to(REPO)} has DRIFTED from the tracked "
                  f"copy.\n     It is gitignored and not authoritative. Cite the data/ "
                  f"paths (register D6a).")


if __name__ == "__main__":
    main()
