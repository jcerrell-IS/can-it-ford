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

RUNS = [
    ("dry_start", "sim_dump.py", "m1100", "small_passenger", 1100.0),
    ("dry_start", "sim_dump.py", "m1609", "large_passenger", 1609.0),
    ("dry_start", "sim_dump.py", "m2337", "large_4wd", 2337.0),
    ("standing_water_sustained_inflow", "sim_standing.py", "g64_m1100", "small_passenger", 1100.0),
    ("standing_water_sustained_inflow", "sim_standing.py", "g64_m1609", "large_passenger", 1609.0),
    ("standing_water_sustained_inflow", "sim_standing.py", "g64_m2337", "large_4wd", 2337.0),
]

PHYSICS_KEYS = ["water_eta", "floor_friction", "bulk_modulus", "substeps", "sound_speed_ms", "n_carved"]


def main():
    out = []
    for scenario, driver, run_dir, label, mass in RUNS:
        s = json.load(open(HERE / run_dir / "summary.json"))
        z = np.load(HERE / run_dir / "rollout.npz", allow_pickle=True)

        h = float(z["h"])
        v = float(z["velocity"])
        nominal_depth = 4.0 * h
        he = nominal_depth + v * v / (2.0 * G)
        limits = AR_R_STABILITY_LIMITS[label]

        disp = float(s["final_disp_mag_m"])
        t = z["t"].astype(np.float64)
        mag_npz = np.linalg.norm(t - t[0], axis=1)
        onset = np.where(mag_npz > DRIFT_THRESHOLD_M)[0]

        out.append(
            dict(
                scenario=scenario,
                driver=driver,
                run_dir=run_dir,
                arr_limit_set=label,
                mass_kg=mass,
                n_grid=int(z["n_grid"]),
                h_m=h,
                grid_lim=float(s["grid_lim"]),
                n_water=int(s["n_water"]),
                n_vehicle=int(s["n_vehicle"]),
                realized_rho=float(s["realized_rho"]),
                density_plausible=bool(100.0 <= float(s["realized_rho"]) <= 300.0),
                nominal_depth_m=nominal_depth,
                velocity_ms=v,
                dxv_nominal=nominal_depth * v,
                total_head_he_m=he,
                L0_verdict="NO-FORD" if nominal_depth >= L0_DEPTH_THRESHOLD_M else "FORD",
                L1a_verdict=L1_verdict(nominal_depth, v, vehicle_class=label),
                L1a_rule="vehicle_params.L1_verdict, full AR&R depth cap + velocity cap + product",
                L1b_verdict="NO-FORD" if he > KRAMER_PASSENGER_HE_M else "FORD",
                L2_verdict="NO-FORD" if len(onset) else "FORD",
                L2_final_disp_mag_m=disp,
                L2_measure="summary.json final_disp_mag_m, metrics.csv t=0..3.0s, 91 rows",
                L2_final_disp_npz_m=float(mag_npz[-1]),
                L2_measure_delta_m=disp - float(mag_npz[-1]),
                L2_onset_frame=(int(onset[0]) if len(onset) else None),
                passthrough_max_frac=float(s["passthrough_max_frac"]),
                oob_particle_frames=int(s.get("C3_oob_particle_frames", -1)),
                rungs_no_ford=None,
                physics_recorded={k: s.get(k, "ABSENT") for k in PHYSICS_KEYS},
            )
        )
        r = out[-1]
        r["rungs_no_ford"] = sum(
            1 for x in (r["L0_verdict"], r["L1a_verdict"], r["L1b_verdict"], r["L2_verdict"])
            if x == "NO-FORD"
        )

    dest = HERE / "gates_results_both_scenarios.json"
    json.dump(out, open(dest, "w"), indent=2)
    print(f"wrote {dest}")

    for sc in ("dry_start", "standing_water_sustained_inflow"):
        rows = [r for r in out if r["scenario"] == sc]
        d = [r["L2_final_disp_mag_m"] for r in rows]
        print(f"\n=== {sc}")
        print(f"    D x V identical across all masses: {set(round(r['dxv_nominal'], 6) for r in rows)}")
        print(f"    displacement {d[0]:.6f} -> {d[-1]:.6f} m, spread {d[0]/d[-1]:.3f}x")
        for r in rows:
            print(f"    {r['mass_kg']:7.0f} kg  L0={r['L0_verdict']:8s} L1a={r['L1a_verdict']:8s} "
                  f"L1b={r['L1b_verdict']:8s} L2={r['L2_verdict']:8s}  |d|={r['L2_final_disp_mag_m']:.6f}  "
                  f"rungs_NO-FORD={r['rungs_no_ford']}/4")


if __name__ == "__main__":
    main()
