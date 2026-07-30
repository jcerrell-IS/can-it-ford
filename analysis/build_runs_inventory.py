import csv
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCOMING = os.path.join(REPO, "renders", "yaris_render_s1", "_incoming")
OUT = os.path.join(REPO, "data", "all_runs_inventory.csv")

FIELDS = [
    "run",
    "sweep",
    "scenario",
    "mass_kg",
    "n_grid",
    "water_layers",
    "h",
    "realized_depth_m",
    "requested_depth_m",
    "velocity_ms",
    "final_disp_mag_m",
    "passthrough_max_frac",
    "determinism_identical",
    "realized_rho",
    "fill_ratio",
    "hull_m3",
    "solid_volume_m3",
    "n_vehicle",
    "n_water",
    "dx",
    "grid_lim",
    "local_depth_bow_peak",
    "local_depth_bow_peak_frame",
    "local_depth_bow_final",
    "local_depth_footprint_peak",
    "local_depth_footprint_final",
    "C2_veh_zmin_final",
    "C2_veh_zmin_start",
    "C2_veh_zmin_rise",
    "C3_oob_particle_frames",
    "leaked_particle_frames",
    "frames",
    "substeps",
    "sound_speed_ms",
    "bulk_modulus",
    "water_eta",
    "floor_friction",
    "label",
    "final_yaw_deg",
    "final_pitch_deg",
    "final_roll_deg",
    "summary_path",
]


def sweep_of(run):
    if run.startswith("sweepV_"):
        return "velocity"
    if run.startswith("sweepD_"):
        return "depth"
    if run.startswith("g48_") or run.startswith("g64_") or run.startswith("g96_"):
        return "mass_grid"
    return "other"


def main():
    runs = []
    for name in sorted(os.listdir(INCOMING)):
        p = os.path.join(INCOMING, name, "summary.json")
        if not os.path.isfile(p):
            continue
        with open(p) as fh:
            s = json.load(fh)
        row = {k: s.get(k, "") for k in FIELDS}
        row["run"] = name
        row["sweep"] = sweep_of(name)
        row["summary_path"] = p
        row["requested_depth_m"] = s.get("depth_m", "")
        wl = s.get("water_layers")
        h = s.get("h")
        if wl is not None and h is not None:
            row["realized_depth_m"] = float(wl) * float(h)
        else:
            row["realized_depth_m"] = ""
        runs.append(row)

    if not runs:
        print("DEGRADE T0.2: no summary.json found under %s" % INCOMING)
        return 1

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in runs:
            w.writerow(r)

    hdr = "%-18s %-32s %8s %5s %3s %10s %7s %12s %10s %6s" % (
        "run", "scenario", "mass_kg", "ngrid", "wl", "depth_real",
        "vel_ms", "final_disp", "passthru", "det",
    )
    print(hdr)
    print("-" * len(hdr))
    for r in runs:
        print("%-18s %-32s %8s %5s %3s %10.6f %7s %12.6f %10.6f %6s" % (
            r["run"], r["scenario"], r["mass_kg"], r["n_grid"], r["water_layers"],
            float(r["realized_depth_m"]), r["velocity_ms"],
            float(r["final_disp_mag_m"]), float(r["passthrough_max_frac"]),
            r["determinism_identical"],
        ))
    print("")
    print("T0.2 OK wrote %s with %d runs" % (OUT, len(runs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
