import argparse
import json
from pathlib import Path

import numpy as np
import trimesh

from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian
from warpmpm.vehicle import FloodHistory, load_vehicle, solidify_watertight


class DamBreakFloodScene:
    def __init__(self, vehicle, reservoir_depth, runout_length, vehicle_mass,
                 n_grid=64, water_density=1000.0, water_eta=1.0e-3,
                 bulk_modulus=1.5e5, fps=30, floor_friction=0.55,
                 device="auto", seed=0):
        self.vehicle = vehicle
        self.fps = fps
        ext = vehicle.extent
        gate_x = 2.0 * reservoir_depth
        lim = float(gate_x + runout_length + 2.0 * ext[0])
        width = float(max(2.5 * ext[1], 4.0 * reservoir_depth))
        self.grid = GridConfig(n_grid=n_grid, grid_lim=max(lim, width))
        dx = self.grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        rng = np.random.default_rng(seed)

        if vehicle.spacing > 1.2 * h:
            vehicle.solidify(h)

        solid_volume = vehicle.n_particles * h ** 3
        vehicle_density = vehicle_mass / solid_volume
        self.vehicle_mass = vehicle_density * solid_volume

        vx = gate_x + runout_length
        vy = 0.5 * width
        self._place = np.array([vx, vy, floor + 0.5 * h], dtype=np.float32)
        truck = vehicle.particles + self._place

        wall = 4.0 * dx
        xs = np.arange(wall + 0.5 * h, gate_x - 0.5 * h, h)
        ys = np.arange(wall + 0.5 * h, width - wall - 0.5 * h, h)
        zs = np.arange(floor + 0.5 * h, floor + reservoir_depth, h)
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
                        ((0, wall, 0), (0, 1, 0)), ((0, width - wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
        s.add_domain_walls()
        self.solver = s
        self.floor = floor
        self.h = h
        self.dx = dx
        self._wall = wall
        self._lim = lim
        self.gate_x = gate_x
        self.vehicle_x = vx
        self.leaked = 0

        ritter_v = 2.0 * float(np.sqrt(9.81 * reservoir_depth))
        c = float(np.sqrt(1.1 * bulk_modulus / water_density))
        self.term_acoustic = c / (0.28 * dx)
        self.term_viscous = 6.0 * water_eta / (water_density * dx * dx)
        self.term_advective = max(ritter_v, 1e-6) / (0.5 * dx)
        rate = max(self.term_acoustic, self.term_viscous, self.term_advective)
        self.sound_speed = c
        self.ritter_front_velocity = ritter_v
        self.substeps = int(np.ceil(rate / fps))
        self.dt = (1.0 / fps) / self.substeps

        self.com0 = s.rigid_state()["com"].copy()
        self.time = 0.0
        self.history = FloodHistory()
        self.history.append(0.0, s.rigid_state(), self.com0)

    def local_depth_velocity_at_vehicle(self, band=0.3):
        s = self.solver
        x = s.x()[: self.n_water]
        v = s.v()[: self.n_water]
        near = np.abs(x[:, 0] - self.vehicle_x) < band
        if not near.any():
            return 0.0, 0.0
        local_depth = float(x[near, 2].max() - self.floor)
        local_velocity = float(np.mean(v[near, 0]))
        return local_depth, local_velocity

    def step(self):
        self.solver.step(self.dt, self.substeps)
        self.time += self.dt
        self.history.append(self.time, self.solver.rigid_state(), self.com0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle-path", required=True)
    parser.add_argument("--vehicle-mass", type=float, required=True)
    parser.add_argument("--reservoir-depth", type=float, default=0.60)
    parser.add_argument("--runout-length", type=float, default=5.0)
    parser.add_argument("--n-grid", type=int, default=64)
    parser.add_argument("--n-steps", type=int, default=180)
    parser.add_argument("--out", default="dam_break_result.json")
    args = parser.parse_args()

    vehicle = load_vehicle(args.vehicle_path)
    scene = DamBreakFloodScene(
        vehicle=vehicle,
        reservoir_depth=args.reservoir_depth,
        runout_length=args.runout_length,
        vehicle_mass=args.vehicle_mass,
        n_grid=args.n_grid,
    )

    print("gate_x", scene.gate_x, "vehicle_x", scene.vehicle_x)
    print("ritter_front_velocity_estimate", scene.ritter_front_velocity)
    print("n_water", scene.n_water, "n_total", scene.n_total)
    print("substeps", scene.substeps, "dt", scene.dt)

    log = []
    for i in range(args.n_steps):
        scene.step()
        depth, vel = scene.local_depth_velocity_at_vehicle()
        log.append({"step": i, "t": scene.time, "local_depth_m": depth,
                    "local_velocity_ms": vel})
        if i % 10 == 0:
            print(i, scene.time, depth, vel)

    with open(args.out, "w") as f:
        json.dump({"gate_x": scene.gate_x, "vehicle_x": scene.vehicle_x,
                   "ritter_front_velocity_estimate": scene.ritter_front_velocity,
                   "log": log}, f, indent=2)


if __name__ == "__main__":
    main()
