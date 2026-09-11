from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh

from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian
from warpmpm.vehicle import FloodHistory, load_vehicle, solidify_watertight

YARIS = Path("/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply")
HULL = 3.542739


def canonicalize(v):
    mv = np.asarray(v.mesh.vertices, dtype=np.float64)
    lo, hi = mv.min(0), mv.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    mv = mv - shift
    v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces), process=False)
    v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
    v.extent = mv.max(0) - mv.min(0)
    v.spacing = float(v.extent.max()) / 32.0
    return v


def count_odd_columns(mesh, h):
    v = np.asarray(mesh.vertices, dtype=np.float64)
    f = np.asarray(mesh.faces)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    lo, hi = v.min(0), v.max(0)
    nx = int(np.ceil((hi[0] - lo[0]) / h)); ny = int(np.ceil((hi[1] - lo[1]) / h))
    ox, oy = lo[0] + h / 2, lo[1] + h / 2
    tlo = np.minimum(np.minimum(a, b), c); thi = np.maximum(np.maximum(a, b), c)
    i0 = np.clip(np.ceil((tlo[:, 0] - ox) / h).astype(np.int64), 0, nx - 1)
    i1 = np.clip(np.floor((thi[:, 0] - ox) / h).astype(np.int64), 0, nx - 1)
    j0 = np.clip(np.ceil((tlo[:, 1] - oy) / h).astype(np.int64), 0, ny - 1)
    j1 = np.clip(np.floor((thi[:, 1] - oy) / h).astype(np.int64), 0, ny - 1)
    ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0)
    cnt = ni * nj
    idx = np.flatnonzero(cnt > 0)
    CI, CJ, CT = [], [], []
    for s0 in range(0, len(idx), 20000):
        blk = idx[s0:s0 + 20000]
        n = cnt[blk]
        off = np.arange(int(n.sum())) - np.repeat(np.cumsum(n) - n, n)
        njr = np.repeat(nj[blk], n)
        CI.append(np.repeat(i0[blk], n) + off // njr)
        CJ.append(np.repeat(j0[blk], n) + off % njr)
        CT.append(np.repeat(blk, n))
    ci = np.concatenate(CI); cj = np.concatenate(CJ); ct = np.concatenate(CT)
    px = ox + ci * h; py = oy + cj * h
    a2, b2, c2 = a[ct], b[ct], c[ct]
    d = (b2[:, 1] - c2[:, 1]) * (a2[:, 0] - c2[:, 0]) + (c2[:, 0] - b2[:, 0]) * (a2[:, 1] - c2[:, 1])
    ok = np.abs(d) > 1e-14
    dd = np.where(ok, d, 1.0)
    w0 = np.where(ok, ((b2[:, 1] - c2[:, 1]) * (px - c2[:, 0]) + (c2[:, 0] - b2[:, 0]) * (py - c2[:, 1])) / dd, -1.0)
    w1 = np.where(ok, ((c2[:, 1] - a2[:, 1]) * (px - c2[:, 0]) + (a2[:, 0] - c2[:, 0]) * (py - c2[:, 1])) / dd, -1.0)
    w2 = 1.0 - w0 - w1
    hit = ok & (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    ci, cj = ci[hit], cj[hit]
    col = ci * ny + cj
    col = np.sort(col)
    starts = np.flatnonzero(np.r_[True, col[1:] != col[:-1]])
    runs = np.diff(np.r_[starts, len(col)])
    n_odd = int((runs % 2 != 0).sum())
    return n_odd, int(len(runs))


class StandingFloodScene:
    def __init__(self, vehicle, depth, velocity, vehicle_mass, n_grid=64,
                 water_density=1000.0, water_eta=1.0e-3, bulk_modulus=1.5e5,
                 fps=30, floor_friction=0.55, settle_frames=8, device="auto",
                 seed=0, inflow_len=1.5):
        self.vehicle = vehicle
        self.fps = fps
        self.velocity = velocity
        ext = vehicle.extent
        lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
        self.grid = GridConfig(n_grid=n_grid, grid_lim=lim)
        dx = self.grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        rng = np.random.default_rng(seed)

        if vehicle.spacing > 1.2 * h:
            vehicle.solidify(h)

        solid_volume = vehicle.n_particles * h ** 3
        vehicle_density = vehicle_mass / solid_volume
        self.vehicle_mass = vehicle_density * solid_volume

        vx, vy = 0.60 * lim, 0.50 * lim
        self._place = np.array([vx, vy, floor + 0.5 * h], dtype=np.float32)
        truck = vehicle.particles + self._place

        wall = 4.0 * dx
        xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        ys = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = (water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)).astype(np.float32)
        n_before = len(water)

        vk = np.floor(np.asarray(truck, dtype=np.float64) / h).astype(np.int64)
        wk = np.floor(np.asarray(water, dtype=np.float64) / h).astype(np.int64)
        base = vk.min(0)
        span = (vk.max(0) - base + 1).astype(np.int64)
        vlin = np.ravel_multi_index((vk - base).T, span)
        inside = np.all((wk >= base) & (wk <= vk.max(0)), axis=1)
        wlin = np.full(len(water), -1, dtype=np.int64)
        wlin[inside] = np.ravel_multi_index((wk[inside] - base).T, span)
        occupied = np.isin(wlin, np.unique(vlin)) & inside
        water = water[~occupied]
        self.n_carved = int(occupied.sum())
        self.n_water_before_carve = int(n_before)

        pos = np.concatenate([water, truck])
        vol = np.full(len(pos), h ** 3, dtype=np.float32)
        self.n_water = len(water)
        self.n_total = len(pos)

        s = Solver(grid=self.grid, device=device).load_particles(pos, vol)
        s.set_material(newtonian(eta=water_eta, density=water_density,
                                 bulk_modulus=bulk_modulus))
        s.set_material_range(self.n_water, self.n_total, "rigid", obj_id=0,
                             density=vehicle_density)
        s.finalize_rigid_bodies()
        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
                    restitution=0.05)
        for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                        ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
        s.add_domain_walls()
        self.solver = s
        self.floor = floor
        self.h = h
        self.dx = dx
        self._wall = wall
        self._lim = lim
        self.leaked = 0
        self._inflow_x = wall + inflow_len

        c = float(np.sqrt(1.1 * bulk_modulus / water_density))
        self.term_acoustic = c / (0.28 * dx)
        self.term_viscous = 6.0 * water_eta / (water_density * dx * dx)
        self.term_advective = max(velocity, 1e-6) / (0.5 * dx)
        rate = max(self.term_acoustic, self.term_viscous, self.term_advective)
        self.sound_speed = c
        self.substeps = int(np.ceil(rate / fps))
        self.dt = (1.0 / fps) / self.substeps

        for _ in range(settle_frames):
            self._project_water()
            s.step(self.dt, self.substeps)

        v = s.v()
        v[: self.n_water, 0] += velocity
        s.set_v(v)

        self.com0 = s.rigid_state()["com"].copy()
        self.time = 0.0
        self.history = FloodHistory()
        self.history.append(0.0, s.rigid_state(), self.com0)

    def _project_water(self):
        s = self.solver
        x = s.x()
        w = x[: self.n_water]
        eps = 0.25 * self.grid.dx
        lo = np.array([self._wall, self._wall, self.floor], dtype=np.float32) - eps
        hi = np.array([self._lim - self._wall, self._lim - self._wall, np.inf],
                      dtype=np.float32) + eps
        out_lo = w < lo
        out_hi = w > hi
        if not (out_lo.any() or out_hi.any()):
            return
        self.leaked += int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
        v = s.v()
        vw = v[: self.n_water]
        np.clip(w, lo, hi, out=w)
        vw[out_lo] = np.maximum(vw[out_lo], 0.0)
        vw[out_hi] = np.minimum(vw[out_hi], 0.0)
        s.set_x(x)
        s.set_v(v)

    def _sustain_inflow(self):
        s = self.solver
        x = s.x()
        v = s.v()
        band = x[: self.n_water, 0] < self._inflow_x
        vw = v[: self.n_water]
        vw[band, 0] = self.velocity
        s.set_v(v)
        return int(band.sum())

    def step(self):
        self._project_water()
        self.n_inflow = self._sustain_inflow()
        self.solver.step(self.dt, self.substeps)
        self.time += 1.0 / self.fps
        st = self.solver.rigid_state()
        self.history.append(self.time, st, self.com0)
        return st

    def vehicle_pose(self):
        st = self.solver.rigid_state()
        com_veh = self.com0 - self._place
        R = st["R"]
        t = st["com"] - R @ com_veh
        return R, t


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mass", type=float, required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--depth", type=float, default=0.30)
    p.add_argument("--velocity", type=float, default=1.5)
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--eta", type=float, default=1.0e-3)
    p.add_argument("--floor-friction", type=float, default=0.55)
    p.add_argument("--vehicle", default=str(YARIS))
    a = p.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    v1 = canonicalize(load_vehicle(Path(a.vehicle), up="z"))
    v2 = canonicalize(load_vehicle(Path(a.vehicle), up="z"))
    h_probe = float(max(2.2 * v1.extent[1], 3.5 * v1.extent[0], 6.0 * a.depth)) / a.grid / 2.0
    v1.solidify(h_probe)
    v2.solidify(h_probe)
    lim1 = float(max(2.2 * v1.extent[1], 3.5 * v1.extent[0], 6.0 * a.depth))
    lim2 = float(max(2.2 * v2.extent[1], 3.5 * v2.extent[0], 6.0 * a.depth))
    print("DETERMINISM load1 n=%d lim=%.9f" % (v1.n_particles, lim1), flush=True)
    print("DETERMINISM load2 n=%d lim=%.9f" % (v2.n_particles, lim2), flush=True)
    det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
    print("DETERMINISM identical=%s" % det_ok, flush=True)

    n_odd, n_cols = count_odd_columns(v1.mesh, h_probe)
    print("PARITY_ODD_COLUMNS dropped=%d of %d columns (%.4f percent)"
          % (n_odd, n_cols, 100.0 * n_odd / max(n_cols, 1)), flush=True)

    v = v1
    scene = StandingFloodScene(v, depth=a.depth, velocity=a.velocity,
                               vehicle_mass=a.mass, n_grid=a.grid,
                               water_eta=a.eta, floor_friction=a.floor_friction)

    lim = scene.grid.grid_lim
    dx, h, floor = scene.dx, scene.h, scene.floor
    n_water = scene.n_water
    n_veh = scene.n_total - n_water
    solid_volume = n_veh * h ** 3
    layers = int(len(np.arange(floor + 0.5 * h, floor + a.depth, h)))
    gridline = ("grid %d^3 lim=%.2fm  water %d + vehicle %d particles (%.1f kg)  "
                "dt=%.2e (%d substeps/frame)"
                % (a.grid, lim, n_water, n_veh, scene.vehicle_mass, scene.dt, scene.substeps))
    print("SCENARIO=STANDING_WATER_SUSTAINED_INFLOW", flush=True)
    print(gridline, flush=True)
    print("INSTRUMENT dx=%.6f h=%.6f floor=%.6f lim=%.6f" % (dx, h, floor, lim), flush=True)
    print("INSTRUMENT water_layers=%d" % layers, flush=True)
    print("INSTRUMENT solid_volume=%.5f m3 hull=%.5f fill_ratio=%.4f realized_rho=%.2f"
          % (solid_volume, HULL, solid_volume / HULL, scene.vehicle_mass / solid_volume), flush=True)
    print("INSTRUMENT carved %d of %d water particles from vehicle cells (%.2f percent)"
          % (scene.n_carved, scene.n_water_before_carve,
             100.0 * scene.n_carved / max(scene.n_water_before_carve, 1)), flush=True)
    print("SUBSTEP_TERMS eta=%.3e acoustic=%.4f viscous=%.6f advective=%.4f -> rate=%.4f substeps=%d"
          % (a.eta, scene.term_acoustic, scene.term_viscous, scene.term_advective,
             max(scene.term_acoustic, scene.term_viscous, scene.term_advective),
             scene.substeps), flush=True)
    print("ACOUSTIC c=%.4f m/s  vehicle_x=%.4f  downstream_wall=%.4f  round_trip=%.4f s"
          % (scene.sound_speed, 0.60 * lim, lim - 4.0 * dx,
             2.0 * (lim - 4.0 * dx - 0.60 * lim) / scene.sound_speed), flush=True)
    print("FLOOR_FRICTION=%.3f  WATER_ETA=%.3e" % (a.floor_friction, a.eta), flush=True)

    pv0 = np.asarray(v.particles, dtype=np.float64)
    W, S, RR, TT = [], [], [], []
    ld_bow, ld_foot = [], []
    checkpoints = {}
    oob_total = 0
    frac_max = 0.0
    zmin_start = float(scene.solver.x()[n_water:][:, 2].min())

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
        if f in (0, 45, a.frames - 1):
            checkpoints[str(f)] = veh.astype(np.float32)

        oob_total += int(((x < 0.0) | (x > lim)).any(axis=1).sum())
        lo_v, hi_v = veh.min(0), veh.max(0)
        inbox = ((w >= lo_v) & (w <= hi_v)).all(axis=1)
        frac_max = max(frac_max, float(inbox.mean()))

        xf = veh[:, 0].min()
        sel_bow = ((w[:, 0] >= xf - 3.0 * dx) & (w[:, 0] <= xf - 0.5 * dx) &
                   (w[:, 1] >= lo_v[1]) & (w[:, 1] <= hi_v[1]) & (w[:, 2] >= floor))
        ld_bow.append(float(np.percentile(w[sel_bow, 2], 99.5)) - floor
                      if sel_bow.sum() >= 20 else np.nan)
        sel_ft = ((w[:, 0] >= lo_v[0]) & (w[:, 0] <= hi_v[0]) &
                  (w[:, 1] >= lo_v[1]) & (w[:, 1] <= hi_v[1]) & (w[:, 2] >= floor))
        ld_foot.append(float(np.percentile(w[sel_ft, 2], 99.5)) - floor
                       if sel_ft.sum() >= 20 else np.nan)

        if f % 10 == 0 or f == a.frames - 1:
            dd = scene.history.displacement[-1]
            print("frame %3d  |d|=%7.2fcm  yaw=%+6.2f  roll=%+6.2f  ld_bow=%.4f ld_foot=%.4f oob=%d inflow=%d"
                  % (f, float(np.linalg.norm(dd)) * 100, scene.history.yaw[-1],
                     scene.history.roll[-1], ld_bow[-1], ld_foot[-1], oob_total,
                     getattr(scene, "n_inflow", -1)), flush=True)

    scene.history.to_csv(out / "metrics.csv")
    np.savez_compressed(
        out / "rollout.npz",
        water=np.asarray(W, dtype=np.float32), speed=np.asarray(S, dtype=np.float32),
        R=np.asarray(RR, dtype=np.float32), t=np.asarray(TT, dtype=np.float32),
        veh_particles_scene0=checkpoints["0"],
        veh_check_45=checkpoints["45"], veh_check_last=checkpoints[str(a.frames - 1)],
        veh_particles_vehframe=pv0.astype(np.float32),
        local_depth_bow=np.asarray(ld_bow, dtype=np.float32),
        local_depth_footprint=np.asarray(ld_foot, dtype=np.float32),
        extent=np.asarray(v.extent, dtype=np.float32),
        lim=np.float32(lim), dx=np.float32(dx), h=np.float32(h), floor=np.float32(floor),
        depth=np.float32(a.depth), velocity=np.float32(a.velocity),
        mass=np.float32(scene.vehicle_mass), n_grid=np.int32(a.grid),
        frames=np.int32(a.frames), fps=np.int32(scene.fps),
    )

    d = scene.history.displacement[-1]
    veh_last = scene.solver.x()[n_water:]
    ldb = np.asarray(ld_bow); ldf = np.asarray(ld_foot)
    pk = int(np.nanargmax(ldb))
    summary = {
        "scenario": "standing_water_sustained_inflow",
        "label": a.label, "mass_kg": float(scene.vehicle_mass),
        "depth_m": a.depth, "velocity_ms": a.velocity, "n_grid": a.grid,
        "frames": a.frames, "grid_lim": float(lim), "dx": float(dx), "h": float(h),
        "water_layers": layers, "n_water": int(n_water), "n_vehicle": int(n_veh),
        "n_carved": scene.n_carved, "water_eta": a.eta,
        "floor_friction": a.floor_friction, "bulk_modulus": 1.5e5,
        "substeps": int(scene.substeps), "sound_speed_ms": float(scene.sound_speed),
        "term_acoustic": float(scene.term_acoustic),
        "term_viscous": float(scene.term_viscous),
        "term_advective": float(scene.term_advective),
        "solid_volume_m3": float(solid_volume), "hull_m3": HULL,
        "fill_ratio": float(solid_volume / HULL),
        "realized_rho": float(scene.vehicle_mass / solid_volume),
        "parity_odd_columns_dropped": n_odd, "parity_total_columns": n_cols,
        "determinism_identical": bool(det_ok),
        "final_disp_m": [float(q) for q in d],
        "final_disp_mag_m": float(np.linalg.norm(d)),
        "final_yaw_deg": float(scene.history.yaw[-1]),
        "final_roll_deg": float(scene.history.roll[-1]),
        "final_pitch_deg": float(scene.history.pitch[-1]),
        "C3_oob_particle_frames": int(oob_total),
        "local_depth_bow_peak": float(np.nanmax(ldb)),
        "local_depth_bow_peak_frame": pk,
        "local_depth_bow_final": float(ldb[-1]),
        "local_depth_footprint_peak": float(np.nanmax(ldf)),
        "local_depth_footprint_final": float(ldf[-1]),
        "C2_veh_zmin_start": zmin_start,
        "C2_veh_zmin_final": float(veh_last[:, 2].min()),
        "C2_veh_zmin_rise": float(veh_last[:, 2].min()) - zmin_start,
        "passthrough_max_frac": frac_max,
        "leaked_particle_frames": int(scene.leaked),
        "grid_lim_line_verbatim": gridline,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s" % a.label, flush=True)


if __name__ == "__main__":
    main()
