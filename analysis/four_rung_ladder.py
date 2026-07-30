import csv
import json
from pathlib import Path

import numpy as np

G = 9.81
DRIFT_THRESHOLD_M = 0.05
L0_DEPTH_THRESHOLD_M = 0.15
KRAMER_PASSENGER_HE_M = 0.30

REPO = Path(__file__).resolve().parents[1]
RENDERS = REPO / "renders" / "yaris_render_s1"

CLASSES = [
    ("small_passenger", 1100.0, dict(depth_m=0.30, velocity_ms=3.0, haz_m2s=0.30)),
    ("large_passenger", 1609.0, dict(depth_m=0.40, velocity_ms=3.0, haz_m2s=0.45)),
    ("large_4wd", 2337.0, dict(depth_m=0.50, velocity_ms=3.0, haz_m2s=0.60)),
]


def arr_verdict(depth_m, velocity_ms, limits):
    if depth_m > limits["depth_m"]:
        return "NO-FORD", "depth cap"
    if velocity_ms > limits["velocity_ms"]:
        return "NO-FORD", "velocity cap"
    if round(depth_m * velocity_ms, 6) > limits["haz_m2s"]:
        return "NO-FORD", "DxV product"
    return "FORD", ""


def load(run_dir):
    d = np.load(RENDERS / run_dir / "rollout.npz", allow_pickle=True)
    keys = set(d.files)
    h = float(d["h"])
    t = d["t"].astype(np.float64)
    disp = t - t[0]
    mag = np.linalg.norm(disp, axis=1)
    exceed = np.where(mag > DRIFT_THRESHOLD_M)[0]
    R = d["R"].astype(np.float64)
    yaw = np.degrees(np.arctan2(R[:, 1, 0], R[:, 0, 0]))
    yaw = yaw - yaw[0]
    return dict(
        h=h,
        n_particles=int(d["veh_particles_scene0"].shape[0]),
        n_water=int(d["water"].shape[1]),
        n_grid=int(d["n_grid"]),
        lim=float(d["lim"]),
        requested_depth_m=float(d["depth"]),
        velocity_ms=float(d["velocity"]),
        nominal_depth_m=4.0 * h,
        local_depth_peak_m=(
            float(d["local_depth_footprint"].max())
            if "local_depth_footprint" in keys
            else None
        ),
        final_disp_m=float(mag[-1]),
        peak_disp_m=float(mag.max()),
        peak_yaw_deg=float(np.abs(yaw).max()),
        onset_frame=(int(exceed[0]) if len(exceed) else None),
    )


def build(set_tag, prefix):
    rows = []
    for cls, mass, limits in CLASSES:
        r = load(f"{prefix}{int(mass)}")
        v = r["velocity_ms"]
        depth = r["nominal_depth_m"]
        rho = mass / (r["n_particles"] * r["h"] ** 3)
        he = depth + v * v / (2.0 * G)

        l0 = "NO-FORD" if depth >= L0_DEPTH_THRESHOLD_M else "FORD"
        l1a_req, req_bind = arr_verdict(r["requested_depth_m"], v, limits)
        l1a_real, real_bind = arr_verdict(depth, v, limits)
        if r["local_depth_peak_m"] is None:
            l1a_local, local_bind = "", ""
        else:
            l1a_local, local_bind = arr_verdict(r["local_depth_peak_m"], v, limits)
        l1b = "NO-FORD" if he > KRAMER_PASSENGER_HE_M else "FORD"
        l2 = "NO-FORD" if r["onset_frame"] is not None else "FORD"

        rows.append(
            dict(
                set=set_tag,
                run_dir=f"{prefix}{int(mass)}",
                vehicle_class=cls,
                mass_kg=mass,
                n_grid=r["n_grid"],
                h_m=r["h"],
                lim_m=r["lim"],
                n_water=r["n_water"],
                n_vehicle_particles=r["n_particles"],
                realized_rho_kgm3=rho,
                density_plausible=bool(100.0 <= rho <= 300.0),
                requested_depth_m=r["requested_depth_m"],
                nominal_depth_m=depth,
                local_depth_peak_m=r["local_depth_peak_m"],
                velocity_ms=v,
                dxv_requested=r["requested_depth_m"] * v,
                dxv_nominal=depth * v,
                dxv_local_peak=(
                    None
                    if r["local_depth_peak_m"] is None
                    else r["local_depth_peak_m"] * v
                ),
                total_head_he_m=he,
                L0_verdict=l0,
                L1a_verdict_requested=l1a_req,
                L1a_binding_requested=req_bind,
                L1a_verdict_nominal=l1a_real,
                L1a_binding_nominal=real_bind,
                L1a_verdict_local_peak=l1a_local,
                L1a_binding_local_peak=local_bind,
                L1b_verdict=l1b,
                L2_verdict=l2,
                L2_final_disp_m=r["final_disp_m"],
                L2_peak_disp_m=r["peak_disp_m"],
                L2_peak_yaw_deg=r["peak_yaw_deg"],
                L2_onset_frame=r["onset_frame"],
                rungs_agreeing_no_ford=sum(
                    1 for x in (l0, l1a_real, l1b, l2) if x == "NO-FORD"
                ),
            )
        )
    return rows


def main():
    rows = build("A_superseded", "m") + build("B_current", "g64_m")
    out_csv = REPO / "data" / "four_rung_ladder.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out_csv} ({len(rows)} rows)")
    print(json.dumps(rows, indent=2, default=str))


if __name__ == "__main__":
    main()
