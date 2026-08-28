import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from vehicle_params import AR_R_STABILITY_LIMITS, L1_verdict

G = 9.81
DRIFT_THRESHOLD_M = 0.05
L0_DEPTH_THRESHOLD_M = 0.15
KRAMER_PASSENGER_HE_M = 0.30

INCOMING = HERE / "_incoming"
DRY_RUNS = [
    ("m1100", "small_passenger", "sim_dump.py"),
    ("m1609", "large_passenger", "sim_dump.py"),
    ("m2337", "large_4wd", "sim_dump.py"),
]


def sweep_of(run):
    if run.startswith("sweepV_"):
        return "velocity"
    if run.startswith("sweepD_"):
        return "depth"
    if run[:4] in ("g48_", "g64_", "g96_"):
        return "mass_grid"
    return "dry_start"


def collect():
    jobs = []
    for d in sorted(INCOMING.iterdir()):
        if not (d / "summary.json").is_file():
            continue
        jobs.append((d, d.name, None, "sim_standing.py", "_incoming"))
    for name, label, driver in DRY_RUNS:
        d = HERE / name
        if (d / "summary.json").is_file():
            jobs.append((d, name, label, driver, "top_level"))
    return jobs


def evaluate(d, name, label_override, driver, origin):
    s = json.load(open(d / "summary.json"))
    z = np.load(d / "rollout.npz", allow_pickle=True)

    h = float(z["h"])
    v = float(z["velocity"])
    layers = int(s["water_layers"])
    nominal_depth = layers * h
    requested_depth = float(s.get("depth_m", float("nan")))
    label = label_override or s.get("label")
    he = nominal_depth + v * v / (2.0 * G)

    t = z["t"].astype(np.float64)
    mag = np.linalg.norm(t - t[0], axis=1)
    onset = np.where(mag > DRIFT_THRESHOLD_M)[0]

    if "local_depth_bow_peak" in s:
        peak = float(s["local_depth_bow_peak"])
        peak_src = "summary.json local_depth_bow_peak"
    elif "C2_local_depth_max" in s:
        peak = float(s["C2_local_depth_max"])
        peak_src = "summary.json C2_local_depth_max"
    else:
        peak = None
        peak_src = "ABSENT"

    scenario = s.get("scenario") or "dry_start"

    r = dict(
        run=name,
        origin=origin,
        sweep=sweep_of(name),
        scenario=scenario,
        driver=driver,
        arr_limit_set=label,
        mass_kg=float(s["mass_kg"]),
        n_grid=int(s["n_grid"]),
        h_m=h,
        water_layers=layers,
        requested_depth_m=requested_depth,
        nominal_depth_m=nominal_depth,
        velocity_ms=v,
        dxv_nominal=nominal_depth * v,
        dxv_requested=requested_depth * v,
        total_head_he_m=he,
        arr_depth_cap_m=AR_R_STABILITY_LIMITS[label]["depth_m"],
        arr_haz_cap_m2s=AR_R_STABILITY_LIMITS[label]["haz_m2s"],
        L0_verdict="NO-FORD" if nominal_depth >= L0_DEPTH_THRESHOLD_M else "FORD",
        L1a_verdict=L1_verdict(nominal_depth, v, vehicle_class=label),
        L1b_verdict="NO-FORD" if he > KRAMER_PASSENGER_HE_M else "FORD",
        L2_verdict="NO-FORD" if len(onset) else "FORD",
        L2_final_disp_mag_m=float(s["final_disp_mag_m"]),
        L2_onset_frame=(int(onset[0]) if len(onset) else None),
        local_depth_peak_m=peak,
        local_depth_peak_source=peak_src,
        passthrough_max_frac=float(s["passthrough_max_frac"]),
        oob_particle_frames=int(s.get("C3_oob_particle_frames", -1)),
        determinism_identical=s.get("determinism_identical", "ABSENT"),
        realized_rho=float(s["realized_rho"]),
        fill_ratio=float(s["fill_ratio"]),
        n_vehicle=int(s["n_vehicle"]),
        n_water=int(s["n_water"]),
    )
    r["rungs_no_ford"] = sum(
        1 for x in (r["L0_verdict"], r["L1a_verdict"], r["L1b_verdict"], r["L2_verdict"])
        if x == "NO-FORD"
    )
    return r


def main():
    out = []
    fails = []
    for d, name, label, driver, origin in collect():
        try:
            out.append(evaluate(d, name, label, driver, origin))
        except Exception as exc:
            fails.append((name, repr(exc)))
            print("DEGRADE gates: %s failed, %r" % (name, exc))

    dest = HERE / "gates_results_all_runs.json"
    json.dump(out, open(dest, "w"), indent=2)

    hdr = "%-18s %-10s %-32s %5s %3s %10s %6s %8s %8s %8s %8s %5s" % (
        "run", "sweep", "scenario", "ngrid", "wl", "nom_depth", "v",
        "L0", "L1a", "L1b", "L2", "nf/4")
    print(hdr)
    print("-" * len(hdr))
    for r in out:
        print("%-18s %-10s %-32s %5d %3d %10.6f %6.2f %8s %8s %8s %8s %5s" % (
            r["run"], r["sweep"], r["scenario"], r["n_grid"], r["water_layers"],
            r["nominal_depth_m"], r["velocity_ms"],
            r["L0_verdict"], r["L1a_verdict"], r["L1b_verdict"], r["L2_verdict"],
            "%d/4" % r["rungs_no_ford"]))

    print("")
    for g in ("g48", "g64", "g96"):
        rows = [r for r in out if r["run"].startswith(g + "_")]
        if rows:
            print("%s nominal_depth set: %s  (layer counts %s)" % (
                g,
                sorted({round(r["nominal_depth_m"], 6) for r in rows}),
                sorted({r["water_layers"] for r in rows})))
    print("")
    print("T1.4 OK wrote %s with %d runs, %d degraded" % (dest, len(out), len(fails)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
