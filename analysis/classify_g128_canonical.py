#!/usr/bin/env python3
"""Classify the canonical Yaris set at g96 and g128, the direct test register J15 calls
"the single highest-value open item in the project".

NON-CANONICAL, per Part 2.7. Writes ONLY to
data/g128_canonical_slide_classification_2026-08-13.csv. It never touches
data/all_runs_inventory.csv, data/failure_modes_by_run_classified.csv,
data/failure_modes_by_run.json or gates_results_all_runs.json.

WHAT THIS ANSWERS
  Register J15: a SLIDE verdict has been shown to be resolution-dependent for the
  Silverado (SLIDE at g64/g96, STUCK at g128), and the canonical set is exposed the
  same way, with g96_m2337 holding the joint condition for 4 frames against the 3
  required. J15 states plainly: "The direct test has never been run: the canonical set
  does not exist at g128." It does now, LS6 job 3362573.

WHY g96 IS RE-RUN RATHER THAN READ FROM THE FROZEN STORE
  1. Register J16: six of the seventeen frozen margins, the g48_* and g96_* runs, are
     NOT reproducible. Job 866887 overwrote those directories on 2026-07-26, so the
     frozen g96 numbers came from outputs that no longer exist.
  2. Register J17: this stack is non-deterministic at fixed configuration.
  A cross-job control could therefore not separate a refinement effect from a
  run-to-run draw. g96 and g128 were produced in the SAME job, same node, same driver
  sha256 4696c3b2, so the refinement comparison here is within-job.

METHOD is identical to analysis/classify_rogue_silverado_sweep.py: call the library
function simulation/failure_modes.classify_timeseries directly, the same one behind the
17 gated verdicts. margin_frames and longest_joint_run reproduce
analysis/slide_verdict_fragility.py exactly, because J15 names margin_frames as the
assumption-free number to quote.

ssf 1.42 (compact_sedan) is applied to all six for parity with
analysis/classify_failure_modes.py:99. It cannot affect `ratio_slide` or
`triggered_slide`, which are ssf-independent because ssf feeds TOPPLE only
(failure_modes.py:184, :211). It is NOT true that ssf cannot affect the `mode` column:
`mode` is `reached[-1]` over MODE_SEVERITY (:33, :234), so a sustained TOPPLE would
displace SLIDE. Three of the six arms exceed ssf 1.42 in `peak_surge_accel_g`
instantaneously (1.8487, 1.5377, 1.6441) and none for 3 consecutive frames, so the
question does not arise here; swept ssf 1.42/1.19/1.04/0.90/0.80 and all six stay SLIDE.
mass_kg is genuinely inert for the verdict, it only scales reported forces
(failure_modes.py:130, :176): mass 1 / 1100 / 2337 / 1e6 all return ratio_slide
1.473360.

SCOPE, STATED BECAUSE IT IS EASY TO OVERSTATE
  The canonical set is SEVENTEEN runs: 9 mass_grid, 3 sweepD, 5 sweepV. This tests THREE
  of those configurations, the mass sweep, replicated at g96 and extended to g128.
  Fourteen canonical configurations still have no g128 counterpart, including
  `sweepV_g64_v0p5`, the only STUCK run. And these are NEW RUNS: a canonical verdict
  cannot itself flip, only a replication of it can.

MANDATORY CAVEATS ON ANYTHING BUILT FROM THIS
  - ENGINE IS warpmpm (sim_standing.py:10-12), on the MATERIAL-8 FREE-RIGID path, which
    is the coupling register A3/J1 criticises for forming no force. This refines an
    independently flawed coupling. Do NOT import the SDF-collider validation
    (7.3 to 7.7 percent) as support for these numbers: different path.
  - Artificial sound speed is 12.845 m/s, sqrt(1.1*150000/1000) from sim_standing.py:225,
    about 117x below real water, so the flow sits near Mach 0.117. Any surge-MAGNITUDE
    claim inherits that. The sound-speed sweep is already done, jobs 895330 and 895378.
  - Displacement magnitudes are non-monotone in grid (register item 5). Cite the VERDICT
    and `margin_frames`, not the magnitude. Steffen, Kirby and Berzins 2008 is the
    citable mechanism for MPM losing convergence under refinement at fixed
    particles-per-cell, and PPC here is constant at 8 (h = dx/2, sim_standing.py:163),
    which is exactly the case that paper addresses.
  - `canon_g128_m1100` FAILS gate P-2, passthrough 0.11159 against the 0.10 limit at
    gates.py:146-148, reproduced at 0.11155 in the repeat job. Treat that arm as
    containment-failed, not as a result.
"""
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))

import failure_modes as FM              # noqa: E402
from vehicle_params import get_vehicle  # noqa: E402

TH = FM.FailureThresholds()
SSF = get_vehicle("compact_sedan")["ssf"]
BASE = REPO / "data" / "g128_canonical_2026-08-13"
OUT = REPO / "data" / "g128_canonical_slide_classification_2026-08-13.csv"

MASSES = (1100.0, 1609.0, 2337.0)
GRIDS = (96, 128)

# Register J16, the live re-classification of the surviving Vista metrics.csv. Recorded
# so the in-job g96 arms can be compared against BOTH the frozen store and that live
# re-read, since J16 shows those two already disagree for the g96 runs.
FROZEN_G96 = {1100.0: None, 1609.0: None, 2337.0: 1.80047}
J16_LIVE_G96 = {1100.0: None, 1609.0: None, 2337.0: 1.74225}


def longest_joint_run(dx, vx, slide_m, slide_v):
    """Longest run of consecutive frames satisfying the joint SLIDE condition.

    Reproduced from analysis/slide_verdict_fragility.py rather than imported, keeping
    that file's read-only status. The classifier needs sustain_frames (3) consecutive,
    so longest_run - 3 is the margin IN FRAMES, and a margin of 0 means one frame from
    STUCK. It makes no scaling assumption at all.
    """
    j = (np.abs(dx) >= slide_m) & (np.abs(vx) >= slide_v)
    best = cur = 0
    for x in j:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return int(best)


def main():
    S = FM.FailureMode.SLIDE
    rows = []
    for g in GRIDS:
        for m in MASSES:
            run = f"canon_g{g}_m{int(m)}"
            path = BASE / run / "metrics.csv"
            if not path.exists():
                raise SystemExit(f"{run}: {path} missing. Refusing to emit a partial store.")
            res = FM.classify_timeseries(str(path), m, SSF)
            d = np.genfromtxt(path, delimiter=",", names=True)
            L = longest_joint_run(d["dx"], d["vx"], TH.slide_m, TH.slide_speed_ms)
            rows.append({
                "run": run, "vehicle": "yaris", "n_grid": g, "mass_kg": m,
                "mode": res.mode.value,
                "triggered_slide": res.sustained[S],
                "ratio_slide": res.ratios[S],
                "max_surge_drift_m": res.max_surge_drift_m,
                "onset_frame_slide": res.first_index[S],
                "max_speed_ms": res.max_speed_ms,
                "peak_surge_accel_g": res.peak_surge_accel_g,
                "peak_surge_force_n": res.peak_surge_force_n,
                "max_vertical_lift_m": res.max_vertical_lift_m,
                "weight_n": res.weight_n, "ssf": res.ssf,
                "longest_joint_frames": L,
                "sustain_frames_required": TH.sustain_frames,
                "margin_frames": L - TH.sustain_frames,
                "slide_m_threshold": TH.slide_m,
                "slide_speed_ms_threshold": TH.slide_speed_ms,
                "source_job": "3362573", "source_host": "LS6 A100 c301-001",
                "timeseries": str(path),
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # lineterminator="\n" on purpose. csv.DictWriter's default excel dialect emits CRLF,
    # while .gitattributes:4 pins *.csv to eol=lf. Commit 789cf7b fixed exactly this
    # defect in classify_failure_modes.write_csv, where it would have defeated a
    # byte-compare; classify_rogue_silverado_sweep.py's convention was copied here
    # before that was noticed. Do not drop this argument.
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT}, {len(rows)} rows\n")

    hdr = ("run", "grid", "mass", "mode", "sustained", "ratio_slide",
           "drift_m", "onset", "margin")
    print("%-20s%6s%7s%8s%11s%13s%10s%7s%8s" % hdr)
    for d in rows:
        print("%-20s%6d%7d%8s%11s%13.4f%10.4f%7d%8d"
              % (d["run"], d["n_grid"], d["mass_kg"], d["mode"], d["triggered_slide"],
                 d["ratio_slide"], d["max_surge_drift_m"], d["onset_frame_slide"],
                 d["margin_frames"]))

    by = {(d["n_grid"], d["mass_kg"]): d for d in rows}
    print("\n=== THE DIRECT TEST: g96 -> g128 at fixed mass, same job ===")
    any_flip = False
    for m in MASSES:
        a, b = by[(96, m)], by[(128, m)]
        flip = a["mode"] != b["mode"]
        any_flip |= flip
        print(f"  m{int(m):<5} g96:{a['mode']:<6} -> g128:{b['mode']:<6}"
              f"  ratio {a['ratio_slide']:8.4f} -> {b['ratio_slide']:8.4f}"
              f"  ({100*(b['ratio_slide']/a['ratio_slide'] - 1):+6.1f}%)"
              f"  margin {a['margin_frames']:>3} -> {b['margin_frames']:>3}"
              f"   {'*** VERDICT FLIPS ***' if flip else 'verdict stable'}")
    print(f"\n  RESULT: {'A REPLICATED MASS-SWEEP VERDICT FLIPS UNDER REFINEMENT' if any_flip else 'none of the 3 replicated mass-sweep verdicts flips between g96 and g128'}")
    print("  SCOPE: 3 of the 17 canonical configurations. The 3 sweepD and 5 sweepV runs,")
    print("         including the only STUCK run sweepV_g64_v0p5, have no g128 counterpart.")

    print("\n=== g96 in-job control against the two recorded g96 values (register J16) ===")
    for m in MASSES:
        d = by[(96, m)]
        fz, lv = FROZEN_G96[m], J16_LIVE_G96[m]
        if fz is None:
            print(f"  m{int(m):<5} in-job {d['ratio_slide']:8.4f}   "
                  f"(no frozen value recorded in J15/J16 for this mass)")
            continue
        print(f"  m{int(m):<5} in-job {d['ratio_slide']:8.4f}   frozen {fz:8.5f} "
              f"({100*(d['ratio_slide']/fz - 1):+6.1f}%)   J16-live {lv:8.5f} "
              f"({100*(d['ratio_slide']/lv - 1):+6.1f}%)")


if __name__ == "__main__":
    main()
