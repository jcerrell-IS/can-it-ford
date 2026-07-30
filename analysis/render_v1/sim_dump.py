from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from warpmpm.vehicle import FloodScene, load_vehicle

YARIS = Path("/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply")
HULL = 3.542739


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mass", type=float, required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--depth", type=float, default=0.30)
    p.add_argument("--velocity", type=float, default=1.5)
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--vehicle", default=str(YARIS))
    a = p.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    v = load_vehicle(Path(a.vehicle), up="z")
    print("STAGE=G3 RUNG=R1 label=%s mass=%.1f" % (a.label, a.mass), flush=True)
    print("vehicle: %d solid particles, extent %s, spacing %.1f mm"
          % (v.n_particles, np.round(v.extent, 4), v.spacing * 1000), flush=True)

    scene = FloodScene(v, depth=a.depth, velocity=a.velocity, n_grid=a.grid,
                       vehicle_mass=a.mass, device="auto")

    lim = scene.grid.grid_lim
    dx = lim / a.grid
    h = dx / 2.0
    floor = 3.0 * dx
    n_water = scene.n_water
    n_veh = scene.n_total - n_water
    solid_volume = n_veh * h ** 3
    layers = int(len(np.arange(floor + 0.5 * h, floor + a.depth, h)))

    gridline = ("grid %d^3 lim=%.2fm  water %d + vehicle %d particles (%.1f kg)  "
                "dt=%.2e (%d substeps/frame)"
                % (a.grid, lim, n_water, n_veh, scene.vehicle_mass, scene.dt, scene.substeps))
    print(gridline, flush=True)
    print("INSTRUMENT dx=%.6f h=%.6f floor=%.6f lim=%.6f" % (dx, h, floor, lim), flush=True)
    print("INSTRUMENT water_layers=%d" % layers, flush=True)
    print("INSTRUMENT solid_volume=%.5f m3  hull=%.5f m3  fill_ratio=%.4f"
          % (solid_volume, HULL, solid_volume / HULL), flush=True)
    print("INSTRUMENT realized_rho=%.2f kg_m3" % (scene.vehicle_mass / solid_volume), flush=True)

    veh0 = scene.solver.x()[n_water:].copy()
    W, S, RR, TT = [], [], [], []
    oob_total = 0
    gmin = np.full(3, np.inf)
    gmax = np.full(3, -np.inf)
    depth_min, depth_max = np.inf, -np.inf
    zmin_start = float(veh0[:, 2].min())
    frac_max = 0.0

    for f in range(a.frames):
        scene.step()
        x = scene.solver.x()
        vel = scene.solver.v()
        w = x[:n_water]
        veh = x[n_water:]
        R, t = scene.vehicle_pose()

        W.append(w.astype(np.float32))
        S.append(np.linalg.norm(vel[:n_water], axis=1).astype(np.float32))
        RR.append(np.asarray(R, dtype=np.float32))
        TT.append(np.asarray(t, dtype=np.float32))

        oob_total += int(((x < 0.0) | (x > lim)).any(axis=1).sum())
        gmin = np.minimum(gmin, x.min(0))
        gmax = np.maximum(gmax, x.max(0))

        lo = veh.min(0)
        hi = veh.max(0)
        inbox = ((w >= lo) & (w <= hi)).all(axis=1)
        frac_max = max(frac_max, float(inbox.mean()))

        near = (np.abs(w[:, 1] - t[1]) < 1.0) & (np.abs(w[:, 0] - t[0]) < 2.5)
        if near.any():
            d = float(w[near, 2].max() - floor)
            depth_min = min(depth_min, d)
            depth_max = max(depth_max, d)

        if f % 10 == 0 or f == a.frames - 1:
            dd = scene.history.displacement[-1]
            print("frame %3d  |d|=%7.2fcm  yaw=%+6.2f  roll=%+6.2f  oob=%d"
                  % (f, float(np.linalg.norm(dd)) * 100, scene.history.yaw[-1],
                     scene.history.roll[-1], oob_total), flush=True)

    scene.history.to_csv(out / "metrics.csv")

    np.savez_compressed(
        out / "rollout.npz",
        water=np.asarray(W, dtype=np.float32),
        speed=np.asarray(S, dtype=np.float32),
        R=np.asarray(RR, dtype=np.float32),
        t=np.asarray(TT, dtype=np.float32),
        veh_particles_scene0=veh0.astype(np.float32),
        extent=np.asarray(v.extent, dtype=np.float32),
        lim=np.float32(lim), dx=np.float32(dx), h=np.float32(h),
        floor=np.float32(floor), depth=np.float32(a.depth),
        velocity=np.float32(a.velocity), mass=np.float32(scene.vehicle_mass),
        n_grid=np.int32(a.grid), frames=np.int32(a.frames), fps=np.int32(scene.fps),
    )

    d = scene.history.displacement[-1]
    veh_last = scene.solver.x()[n_water:]
    summary = {
        "label": a.label, "mass_kg": float(scene.vehicle_mass),
        "depth_m": a.depth, "velocity_ms": a.velocity, "n_grid": a.grid,
        "frames": a.frames, "grid_lim": float(lim), "dx": float(dx), "h": float(h),
        "water_layers": layers, "n_water": int(n_water), "n_vehicle": int(n_veh),
        "solid_volume_m3": float(solid_volume), "hull_m3": HULL,
        "fill_ratio": float(solid_volume / HULL),
        "realized_rho": float(scene.vehicle_mass / solid_volume),
        "final_disp_m": [float(q) for q in d],
        "final_disp_mag_m": float(np.linalg.norm(d)),
        "final_yaw_deg": float(scene.history.yaw[-1]),
        "final_roll_deg": float(scene.history.roll[-1]),
        "final_pitch_deg": float(scene.history.pitch[-1]),
        "C3_oob_particle_frames": int(oob_total),
        "C3_global_min": [float(q) for q in gmin],
        "C3_global_max": [float(q) for q in gmax],
        "C2_local_depth_min": float(depth_min), "C2_local_depth_max": float(depth_max),
        "C2_veh_zmin_start": zmin_start, "C2_veh_zmin_final": float(veh_last[:, 2].min()),
        "C2_veh_zmin_rise": float(veh_last[:, 2].min()) - zmin_start,
        "passthrough_max_frac": frac_max,
        "grid_lim_line_verbatim": gridline,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s" % a.label, flush=True)


if __name__ == "__main__":
    main()
