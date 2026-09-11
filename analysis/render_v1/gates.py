from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from geom_live import YARIS, load_vehicle_local, scene_grid

HULL = 3.542739
EXT_REF = np.array([1.746, 4.283, 1.518])
RHO_REF = 310.49
DRIFT_THRESHOLD = 0.05

AR_R = {
    "small_passenger": {"depth_m": 0.30, "velocity_ms": 3.0, "haz_m2s": 0.30},
    "large_passenger": {"depth_m": 0.40, "velocity_ms": 3.0, "haz_m2s": 0.45},
    "large_4wd": {"depth_m": 0.50, "velocity_ms": 3.0, "haz_m2s": 0.60},
}


def L1_verdict(depth_m, velocity_ms, vehicle_class):
    lim = AR_R[vehicle_class]
    if depth_m > lim["depth_m"]:
        return "NO-FORD"
    if velocity_ms > lim["velocity_ms"]:
        return "NO-FORD"
    if round(depth_m * velocity_ms, 6) > lim["haz_m2s"]:
        return "NO-FORD"
    return "FORD"


def gate(name, value, lo, hi, unit=""):
    ok = (value >= lo) and (value <= hi)
    print("  %-5s %-42s measured=%-14s band=[%s, %s]%s  %s"
          % (name, "", "%.6g" % value, "%.6g" % lo, "%.6g" % hi, unit,
             "PASS" if ok else "FAIL"))
    return ok


def silhouette_fill(pts, ax_a, ax_b, cell):
    a = pts[:, ax_a]
    b = pts[:, ax_b]
    ia = np.floor((a - a.min()) / cell).astype(np.int64)
    ib = np.floor((b - b.min()) / cell).astype(np.int64)
    na, nb = ia.max() + 1, ib.max() + 1
    occ = np.zeros(na * nb, dtype=bool)
    occ[ia * nb + ib] = True
    return float(occ.sum()) / float(na * nb), int(na), int(nb)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", nargs="+", required=True)
    p.add_argument("--cell", type=float, default=0.02)
    a = p.parse_args()

    print("=" * 100)
    print("GEOMETRY GATE   (mesh path, independent of any sim run)")
    print("=" * 100)

    v = load_vehicle_local(YARIS)
    g = scene_grid(v.extent, 0.30, 64)
    ext = np.asarray(v.extent, dtype=np.float64)
    rel = np.abs(ext - EXT_REF) / EXT_REF
    print("  G-1  loaded mesh extents = %s m   expected %s   max rel dev %.4f%%  %s"
          % (np.round(ext, 4), EXT_REF, rel.max() * 100,
             "PASS" if rel.max() <= 0.02 else "FAIL"))

    v.solidify(g["h"])
    solid_particles = np.asarray(v.particles, dtype=np.float64)
    solid_vol = len(solid_particles) * g["h"] ** 3
    fr = solid_vol / HULL
    print("  G-2  fill_ratio = %.5f / %.6f = %.5f   band [0.95, 1.10]   %s"
          % (solid_vol, HULL, fr, "PASS" if 0.95 <= fr <= 1.10 else "FAIL"))
    if fr > 2.0:
        print("       *** fill_ratio near 2.17 means the OLD solidifier is active. STOP. ***")

    rho = 1100.0 / solid_vol
    dev = abs(rho - RHO_REF) / RHO_REF
    print("  G-3  effective density = 1100.0 / %.5f = %.2f kg/m3   expected %.2f   dev %.3f%%   %s"
          % (solid_vol, rho, RHO_REF, dev * 100, "PASS" if dev <= 0.05 else "FAIL"))

    surf = np.asarray(v.surface, dtype=np.float64)
    print()
    print("  G-4  POINT SET ACTUALLY DRAWN AS THE VEHICLE")
    for tag, pts in (("surface points", surf), ("MPM solid particles", solid_particles)):
        e = pts.max(0) - pts.min(0)
        r = np.abs(e - EXT_REF) / EXT_REF
        print("       %-20s n=%-7d extents=%s  max rel dev %.4f%%  %s"
              % (tag, len(pts), np.round(e, 4), r.max() * 100,
                 "PASS" if r.max() <= 0.02 else "FAIL"))

    print()
    print("  G-5  SIDE-VIEW SILHOUETTE FILL FRACTION (project out x, the lateral axis; cell %.3f m)"
          % a.cell)
    for tag, pts, cell in (("surface points", surf, a.cell),
                           ("MPM solid particles", solid_particles, g["h"])):
        f, na, nb = silhouette_fill(pts, 1, 2, cell)
        if tag.startswith("surface"):
            verdict = "PASS (car profile)" if 0.5 <= f <= 0.7 else (
                "FAIL loaf" if f > 0.85 else "OUT OF BAND")
        else:
            verdict = "loaf" if f > 0.85 else "not loaf (voids preserved)"
        print("       %-20s fill=%.4f  grid %dx%d  cell %.4f m   %s"
              % (tag, f, na, nb, cell, verdict))

    print()
    print("  G-6  DISTINCT z-LEVELS IN THE DRAWN CLOUD")
    for tag, pts in (("surface points", surf), ("MPM solid particles", solid_particles)):
        nz = len(np.unique(np.round(pts[:, 2], 6)))
        print("       %-20s distinct z = %d" % (tag, nz))

    print()
    print("=" * 100)
    print("PHYSICS GATE")
    print("=" * 100)

    rows = []
    for rp in a.runs:
        run = Path(rp)
        z = np.load(run / "rollout.npz")
        s = json.loads((run / "summary.json").read_text())
        water = z["water"]
        speed = z["speed"]
        R = z["R"]
        T = z["t"]
        floor = float(z["floor"])
        dx = float(z["dx"])
        nominal_depth = float(z["depth"])
        nominal_vel = float(z["velocity"])
        label = s["label"]

        ref0 = np.asarray(z["veh_particles_scene0"], dtype=np.float64)
        pv = (ref0 - T[0]) @ R[0]

        print()
        print("-" * 100)
        print("RUN %s   mass %.0f kg   nominal depth %.2f m   nominal surge %.1f m/s   n_grid %d"
              % (label, s["mass_kg"], nominal_depth, nominal_vel, s["n_grid"]))
        print("-" * 100)

        print("  P-1  oob particle-frames = %d   required 0   %s"
              % (s["C3_oob_particle_frames"], "PASS" if s["C3_oob_particle_frames"] == 0 else "FAIL"))
        print("  P-2  max water fraction in vehicle bbox = %.4f %%   limit 10 %%   %s"
              % (s["passthrough_max_frac"] * 100,
                 "PASS" if s["passthrough_max_frac"] < 0.10 else "FAIL"))
        rise = s["C2_veh_zmin_rise"]
        print("  P-3  veh_z_min rise = %.6f m   FLOAT live above 0.01 m   %s"
              % (rise, "PASS no float" if abs(rise) <= 0.01 else "FAIL FLOAT LIVE"))

        nf = water.shape[0]
        loc_depth = np.full(nf, np.nan)
        loc_speed = np.full(nf, np.nan)
        for f in range(nf):
            vp = pv @ R[f].T + T[f]
            xf = vp[:, 0].min()
            ylo, yhi = vp[:, 1].min(), vp[:, 1].max()
            w = water[f]
            sel = ((w[:, 0] >= xf - 3.0 * dx) & (w[:, 0] <= xf - 0.5 * dx) &
                   (w[:, 1] >= ylo) & (w[:, 1] <= yhi) & (w[:, 2] >= floor))
            if sel.sum() >= 20:
                loc_depth[f] = float(np.percentile(w[sel, 2], 99.5)) - floor
                loc_speed[f] = float(np.mean(speed[f][sel]))

        pk = int(np.nanargmax(loc_depth))
        d_pk = float(loc_depth[pk])
        v_pk = float(loc_speed[pk])
        d_fin = float(loc_depth[-1])
        v_fin = float(loc_speed[-1])
        print("  P-4  nominal upstream slab depth = %.4f m" % nominal_depth)
        print("       measured local depth at vehicle: peak = %.4f m (frame %d), final = %.4f m"
              % (d_pk, pk, d_fin))
        print("  P-6  water_layers = %d   required >= 4 for depth dependence   %s"
              % (s["water_layers"], "PASS" if s["water_layers"] >= 4 else "FAIL"))

        dv_nom = nominal_depth * nominal_vel
        dv_hon = d_pk * v_pk
        print("  P-5  D x V nominal  = %.4f x %.4f = %.4f m2/s" % (nominal_depth, nominal_vel, dv_nom))
        print("       D x V honest   = %.4f x %.4f = %.4f m2/s  (local depth and local water speed at peak frame %d)"
              % (d_pk, v_pk, dv_hon, pk))
        print("       relative difference = %+.1f %%" % ((dv_hon - dv_nom) / dv_nom * 100))

        disp = s["final_disp_mag_m"]
        l2 = "NO-FORD" if disp > DRIFT_THRESHOLD else "FORD"
        l1_nom = L1_verdict(nominal_depth, nominal_vel, label)
        l1_hon = L1_verdict(d_pk, v_pk, label)
        print("  VERDICTS")
        print("       L1 (AR&R, nominal D,V)      = %s   [limits d<=%.2f v<=%.1f DxV<=%.2f]"
              % (l1_nom, AR_R[label]["depth_m"], AR_R[label]["velocity_ms"], AR_R[label]["haz_m2s"]))
        print("       L1 (AR&R, honest local D,V) = %s" % l1_hon)
        print("       L2 (MPM) final |d| = %.5f m vs DRIFT_THRESHOLD %.2f m -> %s"
              % (disp, DRIFT_THRESHOLD, l2))
        print("       DRIFT_THRESHOLD 0.05 m has NO peer-reviewed source; it is a conservative")
        print("       numerical onset-of-motion tolerance, not a literature stability criterion.")
        agree = "AGREE" if l1_nom == l2 else "DIVERGE"
        print("       L1(nominal) vs L2: %s" % agree)

        rows.append({
            "label": label, "mass_kg": s["mass_kg"],
            "nominal_depth": nominal_depth, "nominal_vel": nominal_vel,
            "local_depth_peak": d_pk, "local_depth_final": d_fin,
            "local_speed_peak": v_pk, "local_speed_final": v_fin,
            "peak_frame": pk, "dv_nominal": dv_nom, "dv_honest": dv_hon,
            "final_disp_mag_m": disp, "final_yaw_deg": s["final_yaw_deg"],
            "final_roll_deg": s["final_roll_deg"],
            "L1_nominal": l1_nom, "L1_honest": l1_hon, "L2": l2, "agreement": agree,
            "oob": s["C3_oob_particle_frames"], "passthrough_pct": s["passthrough_max_frac"] * 100,
            "zmin_rise": rise, "fill_ratio": s["fill_ratio"],
            "realized_rho": s["realized_rho"], "water_layers": s["water_layers"],
            "n_vehicle": s["n_vehicle"],
        })

    Path("gates_results.json").write_text(json.dumps(rows, indent=2))
    print()
    print("wrote gates_results.json")


if __name__ == "__main__":
    main()
