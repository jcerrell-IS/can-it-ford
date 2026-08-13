#!/usr/bin/env python3
"""Aggregate the Rogue/Silverado grid sweep into a NON-CANONICAL csv.

Part 2.7 of the corrections register: this file is not canonical and must never be
merged into data/all_runs_inventory.csv or data/gates_results_all_runs.json.

Reads the g96/g128 runs produced on LS6 this session AND the pre-existing g64 anchor
runs from job 896273 on Vista, so the ladder is complete. The g64 rows are marked with
their own job id and host so the cross-machine provenance is never lost.
"""
import csv
import json
import sys
from pathlib import Path

LS6_BASE = Path(sys.argv[1] if len(sys.argv) > 1 else "/scratch/11603/jcerrell0629/rs_sweep_v2")
VISTA_G64 = Path("/work/11603/jcerrell0629/vista/class_specific_2026-08-08")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "data/rogue_silverado_grid_sweep_2026-08-13.csv")

# Tripwire: --vehicle not taking effect silently runs the Yaris hull. These are the
# yaris_ref_delta_pct values the g64 anchor runs recorded for each hull.
EXPECT_HULL_M3 = {"rogue": 4.950341, "silverado": 7.962083}

rows = []

# Pre-existing g64 anchors, Vista GH200, job 896273, 2026-08-07.
for veh in ("rogue", "silverado"):
    p = VISTA_G64 / f"class_{veh}_g64" / "summary.json"
    if p.exists():
        d = json.load(open(p))
        d["vehicle"] = veh
        d["source_job"] = "896273"
        d["source_host"] = "c642-002.vista (GH200)"
        d["source_date"] = "2026-08-07"
        rows.append(d)

# This session, LS6 A100, run inside allocation 3362208.
for veh in ("rogue", "silverado"):
    for g in (64, 96, 128):
        p = LS6_BASE / f"rs_{veh}_g{g}" / "summary.json"
        if p.exists():
            d = json.load(open(p))
            d["vehicle"] = veh
            d["source_job"] = "3362208"
            d["source_host"] = "c301-003.ls6 (A100)"
            d["source_date"] = "2026-08-13"
            rows.append(d)

if not rows:
    sys.exit("no summary.json found under %s or %s" % (LS6_BASE, VISTA_G64))

# Hull tripwire, refuse to write a mislabelled sweep.
for d in rows:
    exp = EXPECT_HULL_M3[d["vehicle"]]
    got = float(d.get("hull_m3", -1))
    if abs(got - exp) / exp > 0.001:
        sys.exit("TRIPWIRE: %s g%s hull_m3=%s expected ~%s. --vehicle did not take "
                 "effect; this is the Yaris hull mislabelled. Refusing to write."
                 % (d["vehicle"], d.get("n_grid"), got, exp))

lead = ["vehicle", "n_grid", "mass_kg", "requested_depth_m", "velocity_ms",
        "passthrough_max_frac", "final_disp_mag_m", "hull_m3", "realized_rho",
        "source_job", "source_host", "source_date"]
rest = sorted({k for d in rows for k in d} - set(lead))
cols = lead + rest

rows.sort(key=lambda d: (d["vehicle"], int(d["n_grid"])))
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for d in rows:
        w.writerow(d)

print("wrote %s, %d rows" % (OUT, len(rows)))
print()
print("%-11s %5s %9s %10s %12s" % ("vehicle", "grid", "mass_kg", "pass%", "disp_m"))
for d in rows:
    print("%-11s %5s %9s %10.3f %12.4f"
          % (d["vehicle"], d["n_grid"], d["mass_kg"],
             100 * float(d["passthrough_max_frac"]), float(d["final_disp_mag_m"])))
