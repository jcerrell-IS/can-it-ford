"""
build_class_specific_inventory.py

Regenerates data/class_specific_runs_2026-08-08.csv (7 rows) from the per-run
summary.json files produced by jobs 896273 and 896302.

THIS IS A RECONSTRUCTION, NOT THE ORIGINAL GENERATOR.
=====================================================
No script in this repo has ever written that CSV by name. This was recorded as an
open provenance gap at docs/MULTIGEOM_VALIDATION_2026-08-11.md section 3, defect 2.
A live search on 2026-08-11 of the repo (including the gitignored renders/ and
data/ trees) found no generator, and two of the CSV's columns hold hand-authored
English prose, which no summary.json field supplies. The original was therefore
almost certainly assembled by hand or by a scratch script that was never committed.

This file reproduces the committed CSV byte for byte from the summaries plus the
derivation rules below. That makes the artifact regenerable going forward. It does
NOT recover the original provenance, and must not be described as the original.

PROVENANCE OF THE INPUTS
  Job 896273, arm canonical_g64, 2 runs:
    $WORK/class_specific_2026-08-08/<label>/summary.json
  Job 896302, arms A_matched_dx and B_fixed_g96, 5 runs:
    $WORK/render_s3_hullsweep/<label>/summary.json
  $WORK is /work/11603/jcerrell0629/vista on Vista. The summaries are not in the
  repo, so --summaries-json accepts a pulled bundle for offline regeneration.

DERIVATION OF THE COLUMNS THAT ARE NOT SUMMARY FIELDS
  Seventeen columns are copied straight from summary.json (dx_m is the summary's
  `dx`, renamed). The rest are derived here:

  arm        class_* -> canonical_g64; hull_*_dxm -> A_matched_dx;
             hull_*_g96 -> B_fixed_g96. From the label, which encodes the arm.
  vehicle    Second underscore-delimited token of the label.
  job_id     896273 for class_*, 896302 for hull_*. The two arms ran as separate
             jobs with separate drivers; see MULTIGEOM section 3 defect 1, where a
             prescribed commit message wrongly attributed all 7 rows to 896302.
  tripwire   Hull-provenance check that --vehicle actually took effect.
             sim_standing.py:417-419 documents the expected yaris_ref_delta_pct per
             vehicle: about 0 for the Yaris, +39.7 for the Rogue, +124.7 for the
             Silverado. PASS when the run's hull_ref_delta_pct matches its vehicle's
             expected value. This catches a run that silently loaded the wrong hull.
  P1_oob     PASS when C3_oob_particle_frames == 0.
  P2_passthrough
             gates.py:148, verbatim: PASS when passthrough_max_frac < 0.10, else
             FAIL. Strict less-than, matching the gate.
  P3_float   gates.py:151, verbatim: PASS when abs(C2_veh_zmin_rise) <= 0.01, else
             "FAIL FLOAT LIVE". NOTE the criterion is on the ABSOLUTE value: a hull
             that SANK fails this gate exactly as one that rose would. Three of the
             seven rows carry a negative rise small enough to pass, so a naive
             "rise < 0 means fail" rule reproduces the wrong verdict on them.
             gates.py prints "PASS no float"; the CSV stores plain "PASS".
  verdict    NO-FORD when final_disp_mag_m > 0.05, the drift tolerance. All 7 rows
             exceed it, so all 7 are NO-FORD. That 0.05 is a conservative internal
             numerical onset-of-motion tolerance with NO peer-reviewed source, and
             is declared 24 times under five names across the repo; see register
             D7. Do not present it as a cited physical threshold.

  The two trailing columns are ANNOTATIONS, not measurements. They restate a
  failure already visible in the numeric columns, in prose, for a reader scanning
  the CSV. They are reproduced from the same data rather than copied:
  rogue_g64_p3_fail
             Set on a Rogue row that fails P-3, as "P-3 FAIL, z-min sank %.5f m".
  silverado_g64_water_layers_degraded
             Set on the canonical_g64 Silverado row, whose water column resolves to
             3 particle layers against the canonical 4. Per L-3 the canonical g64
             baseline is already only 4 layers and exactly 2 grid cells across the
             depth, so 3 is the least resolved run in the set.

CAVEATS THAT TRAVEL WITH THIS DATA, do not drop them
  The 7 runs use ONE water setup but THREE different hulls, and n_grid is not
  resolution: grid_lim derives from the loaded hull's extent, so a fixed n_grid
  gives each vehicle a different dx AND a different realized water depth. Never
  describe a cross-vehicle row pair as "same resolution" or "same depth". That is
  what the A_matched_dx arm exists to control for.

USAGE
  python3 analysis/build_class_specific_inventory.py --check
      Regenerate in memory and diff against the committed CSV. Writes nothing.
  python3 analysis/build_class_specific_inventory.py --write
      Regenerate and overwrite the CSV.
  Add --summaries-json PATH to read a pulled bundle instead of the Vista trees.
"""

import argparse
import csv
import glob
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "class_specific_runs_2026-08-08.csv")

WORK = os.environ.get("WORK", "/work/11603/jcerrell0629/vista")
CLASS_ROOT = os.path.join(WORK, "class_specific_2026-08-08")
HULL_ROOT = os.path.join(WORK, "render_s3_hullsweep")

# Row order in the committed CSV: the two job-896273 rows first, then job 896302
# grouped by arm (A_matched_dx before B_fixed_g96), vehicle-alphabetical within arm.
ROW_ORDER = [
    "class_rogue_g64",
    "class_silverado_g64",
    "hull_rogue_dxm",
    "hull_silverado_dxm",
    "hull_yaris_dxm",
    "hull_rogue_g96",
    "hull_silverado_g96",
]

FIELDS = [
    "label", "arm", "vehicle", "job_id", "mass_kg", "n_grid", "dx_m",
    "water_layers", "hull_m3", "hull_ref_delta_pct", "tripwire", "fill_ratio",
    "realized_rho", "solid_volume_m3", "final_disp_mag_m", "final_roll_deg",
    "final_pitch_deg", "final_yaw_deg", "passthrough_max_frac",
    "C2_veh_zmin_rise", "C3_oob_particle_frames", "P1_oob", "P2_passthrough",
    "P3_float", "verdict", "hull_source", "rogue_g64_p3_fail",
    "silverado_g64_water_layers_degraded",
]

# sim_standing.py:417-419. The tripwire that --vehicle took effect.
EXPECTED_DELTA_PCT = {"yaris": 0.0, "rogue": 39.7, "silverado": 124.7}
DELTA_TOL_PCT = 1.0

PASSTHROUGH_LIMIT = 0.10   # gates.py:148
FLOAT_RISE_LIMIT = 0.01    # gates.py:151
DRIFT_TOLERANCE_M = 0.05   # register D7, no peer-reviewed source
CANONICAL_WATER_LAYERS = 4


def arm_of(label):
    if label.startswith("class_"):
        return "canonical_g64"
    if label.endswith("_dxm"):
        return "A_matched_dx"
    if label.endswith("_g96"):
        return "B_fixed_g96"
    raise ValueError("cannot infer arm from label %r" % label)


def job_of(label):
    return 896273 if label.startswith("class_") else 896302


def vehicle_of(label):
    return label.split("_")[1]


def load_summaries(args):
    if args.summaries_json:
        with open(args.summaries_json) as fh:
            return json.load(fh)
    out = {}
    for root in (args.class_root, args.hull_root):
        for path in sorted(glob.glob(os.path.join(root, "*", "summary.json"))):
            with open(path) as fh:
                out[os.path.basename(os.path.dirname(path))] = json.load(fh)
    return out


def build_row(label, s):
    vehicle = vehicle_of(label)
    arm = arm_of(label)

    rise = s["C2_veh_zmin_rise"]
    layers = s["water_layers"]
    delta = s["hull_ref_delta_pct"]

    p1 = "PASS" if s["C3_oob_particle_frames"] == 0 else "FAIL"
    p2 = "PASS" if s["passthrough_max_frac"] < PASSTHROUGH_LIMIT else "FAIL"
    p3 = "PASS" if abs(rise) <= FLOAT_RISE_LIMIT else "FAIL FLOAT LIVE"

    expected = EXPECTED_DELTA_PCT[vehicle]
    tripwire = "PASS" if abs(delta - expected) <= DELTA_TOL_PCT else "FAIL"

    verdict = "NO-FORD" if s["final_disp_mag_m"] > DRIFT_TOLERANCE_M else "FORD"

    note_p3 = ""
    if vehicle == "rogue" and p3 != "PASS":
        note_p3 = "P-3 FAIL, z-min sank %.5f m" % rise
    note_layers = ""
    if (vehicle == "silverado" and arm == "canonical_g64"
            and layers < CANONICAL_WATER_LAYERS):
        note_layers = "%d layers, canonical is %d" % (layers, CANONICAL_WATER_LAYERS)

    return {
        "label": s["label"],
        "arm": arm,
        "vehicle": vehicle,
        "job_id": job_of(label),
        "mass_kg": s["mass_kg"],
        "n_grid": s["n_grid"],
        "dx_m": s["dx"],
        "water_layers": layers,
        "hull_m3": s["hull_m3"],
        "hull_ref_delta_pct": delta,
        "tripwire": tripwire,
        "fill_ratio": s["fill_ratio"],
        "realized_rho": s["realized_rho"],
        "solid_volume_m3": s["solid_volume_m3"],
        "final_disp_mag_m": s["final_disp_mag_m"],
        "final_roll_deg": s["final_roll_deg"],
        "final_pitch_deg": s["final_pitch_deg"],
        "final_yaw_deg": s["final_yaw_deg"],
        "passthrough_max_frac": s["passthrough_max_frac"],
        "C2_veh_zmin_rise": rise,
        "C3_oob_particle_frames": s["C3_oob_particle_frames"],
        "P1_oob": p1,
        "P2_passthrough": p2,
        "P3_float": p3,
        "verdict": verdict,
        "hull_source": s["hull_source"],
        "rogue_g64_p3_fail": note_p3,
        "silverado_g64_water_layers_degraded": note_layers,
    }


def render_csv(summaries):
    missing = [r for r in ROW_ORDER if r not in summaries]
    if missing:
        raise SystemExit("missing summaries for: %s" % ", ".join(missing))
    extra = [k for k in summaries if k not in ROW_ORDER]
    if extra:
        raise SystemExit("unexpected runs present: %s" % ", ".join(sorted(extra)))

    buf = io.StringIO()
    # CRLF, the csv module's default. The committed file carries \r\n on all 8
    # lines; forcing \n here makes the output differ by exactly 8 bytes and the
    # difference is invisible to a line-by-line diff. Do not "tidy" this to \n.
    w = csv.DictWriter(buf, fieldnames=FIELDS)
    w.writeheader()
    for label in ROW_ORDER:
        w.writerow(build_row(label, summaries[label]))
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summaries-json",
                    help="pulled bundle {label: summary_dict}, for offline use")
    ap.add_argument("--class-root", default=CLASS_ROOT)
    ap.add_argument("--hull-root", default=HULL_ROOT)
    ap.add_argument("--check", action="store_true",
                    help="diff against the committed CSV, write nothing")
    ap.add_argument("--write", action="store_true", help="overwrite the CSV")
    args = ap.parse_args()

    if not (args.check or args.write):
        ap.error("pass --check or --write")

    text = render_csv(load_summaries(args))

    if args.check:
        with open(OUT, newline="") as fh:
            committed = fh.read()
        if committed == text:
            print("IDENTICAL: regenerated output matches %s byte for byte"
                  % os.path.relpath(OUT, REPO))
            return 0
        print("DIFFERS from %s" % os.path.relpath(OUT, REPO))
        new = text.splitlines()
        old = committed.splitlines()
        for i in range(max(len(new), len(old))):
            a = old[i] if i < len(old) else "<missing>"
            b = new[i] if i < len(new) else "<missing>"
            if a != b:
                print("  line %d\n    committed: %s\n    rebuilt  : %s" % (i + 1, a, b))
        return 1

    with open(OUT, "w", newline="") as fh:
        fh.write(text)
    print("wrote %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
