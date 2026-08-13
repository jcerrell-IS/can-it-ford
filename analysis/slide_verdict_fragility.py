#!/usr/bin/env python3
"""How much would the surge response have to weaken for a gated SLIDE verdict to flip?

NON-CANONICAL, per Part 2.7. Writes only
data/slide_verdict_fragility_2026-08-13.csv. Touches no canonical store.

MOTIVATION. The Rogue/Silverado grid sweep showed a SLIDE verdict flipping to STUCK
between g96 and g128 (data/rogue_silverado_slide_classification_2026-08-13.csv), driven
by the initial surge impulse weakening under refinement. The canonical 17 exist only at
g48/g64/g96 and have never been run at g128, so the direct test is unavailable. This
asks the cheaper question instead: how much weakening would each gated run tolerate?

THE METRIC. SLIDE needs |dx| >= 0.05 m AND |vx| >= 0.05 m/s held for 3 consecutive
frames (failure_modes.py:181-183). Scale the whole surge response by k and the condition
becomes k*|dx| >= 0.05 and k*|vx| >= 0.05, i.e. k >= 0.05 / min(|dx|, |vx|) per frame.
k_crit is the smallest k that still clears some 3-frame window:

    k_crit = min over windows w of ( max over frames i in w of 0.05 / min(|dx_i|,|vx_i|) )

k_crit < 1 means the run currently SLIDEs with headroom 1/k_crit. k_crit > 1 means it
does not slide at all, which is the built-in sanity check: sweepV_g64_v0p5, the one
canonical STUCK run, must come back above 1.

ASSUMPTION, stated because it bounds what this can claim. It scales dx and vx by the
SAME k, a first-order stand-in for a weaker impulse under a linear drag response. Real
refinement also changes the trajectory's shape, not just its amplitude: in the
Rogue/Silverado sweep the SLIDE onset frame moved 3 -> 5 and the decay shortened. So
k_crit ranks fragility and gives an order of magnitude. It is NOT a prediction that a
specific run flips at a specific grid.

PROVENANCE RESTRICTION, and this is the reason the list is 11 and not 17.
/work/11603/jcerrell0629/vista/render_s2/<run>/metrics.csv exists for all 17 with the
full FloodHistory 15-column header. Re-classifying them live reproduces all 17 VERDICTS
(16 SLIDE / 1 STUCK) but only 11 of the 17 ratio_slide values. The six g48_* and g96_*
directories were overwritten on 2026-07-26 03:08-03:10 by job 866887 (its provenance
file is render_s2/conv_2026-07-25/00_provenance.txt, start 2026-07-26T03:07:17), while
g64_* still dates from 2026-07-25 20:12 and the sweeps from the 01:54 idev run. Their
frozen margins came from run outputs that no longer exist on this machine. Largest gap:
g96_m2337, frozen 1.80047 against 1.74225 live, 3.2 percent, on the smallest-margin run
in the set. Only the 11 that reproduce bit-exactly are used here.
"""
import csv
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))

import failure_modes as FM              # noqa: E402
from vehicle_params import get_vehicle  # noqa: E402

BASE = Path("/work/11603/jcerrell0629/vista/render_s2")
OUT = REPO / "data" / "slide_verdict_fragility_2026-08-13.csv"
TH = FM.FailureThresholds()
SSF = get_vehicle("compact_sedan")["ssf"]

# Measured peak-|vx| weakening g64 -> g128 in the Rogue/Silverado sweep, for reference.
MEASURED_WEAKENING = {"rogue": 0.546, "silverado": 0.265}


def k_crit(dx, vx, slide_m, slide_v, sustain):
    need = slide_m / np.maximum(np.minimum(np.abs(dx), np.abs(vx)), 1e-12)
    if slide_v != slide_m:  # thresholds are equal by default; guard if they diverge
        need = np.maximum(slide_m / np.maximum(np.abs(dx), 1e-12),
                          slide_v / np.maximum(np.abs(vx), 1e-12))
    best = np.inf
    for i in range(len(need) - sustain + 1):
        best = min(best, float(need[i:i + sustain].max()))
    return best


def main():
    inv = {r["run"]: r for r in csv.DictReader(open(REPO / "data" / "all_runs_inventory.csv"))}
    frozen = {r["run"]: r for r in
              csv.DictReader(open(REPO / "data" / "failure_modes_by_run_classified.csv"))}
    S = FM.FailureMode.SLIDE

    rows = []
    for run, meta in inv.items():
        path = BASE / run / "metrics.csv"
        if not path.exists():
            continue
        res = FM.classify_timeseries(str(path), float(meta["mass_kg"]), SSF)
        fz = frozen[run]
        reproduces = (res.mode.value == fz["mode"]
                      and abs(res.ratios[S] - float(fz["ratio_slide"])) < 1e-6)
        d = np.genfromtxt(path, delimiter=",", names=True)
        k = k_crit(d["dx"], d["vx"], TH.slide_m, TH.slide_speed_ms, TH.sustain_frames)
        rows.append({
            "run": run, "n_grid": meta["n_grid"], "mass_kg": meta["mass_kg"],
            "velocity_ms": meta["velocity_ms"], "requested_depth_m": meta["requested_depth_m"],
            "mode_live": res.mode.value, "mode_frozen": fz["mode"],
            "ratio_slide_live": res.ratios[S], "ratio_slide_frozen": float(fz["ratio_slide"]),
            "reproduces_frozen": reproduces,
            "k_crit": k, "headroom_x": (1.0 / k) if k > 0 else float("inf"),
            "flips_under_rogue_weakening": k > MEASURED_WEAKENING["rogue"],
            "flips_under_silverado_weakening": k > MEASURED_WEAKENING["silverado"],
        })

    rows.sort(key=lambda r: -r["k_crit"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT}, {len(rows)} rows "
          f"({sum(r['reproduces_frozen'] for r in rows)} reproduce the frozen store)")
    print()
    print("%-20s%6s%8s%9s%11s%11s%8s" %
          ("run", "grid", "mode", "k_crit", "headroom", "repro", "flips"))
    for r in rows:
        flips = ("silverado" if r["flips_under_silverado_weakening"] and
                 r["flips_under_rogue_weakening"] else
                 "sil-only" if r["flips_under_silverado_weakening"] else "-")
        print("%-20s%6s%8s%9.4f%10.2fx%11s%8s" %
              (r["run"], r["n_grid"], r["mode_live"], r["k_crit"], r["headroom_x"],
               "yes" if r["reproduces_frozen"] else "NO", flips))
    print()
    print("k_crit > 1 means the run does not slide at all. sweepV_g64_v0p5 is the one")
    print("canonical STUCK run and is the built-in check that the metric is oriented right.")
    print("'flips' compares k_crit against the measured g64->g128 peak-|vx| weakening")
    print("in the Rogue/Silverado sweep: rogue 0.546x, silverado 0.265x.")
    print("Rows marked repro=NO have unverifiable margins; see this file's docstring.")


if __name__ == "__main__":
    main()
