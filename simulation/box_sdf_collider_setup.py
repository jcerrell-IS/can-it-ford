from __future__ import annotations

import numpy as np
import trimesh

from warpmpm import GridConfig, Solver
from warpmpm.geometry import build_sdf_cached
from warpmpm.materials import newtonian

BOX_DIMS_M = (4.66, 1.79, 1.44)
DOMAIN_SIZE_M = 10.0
SDF_RES = 96
SDF_MARGIN_CELLS = 6.0
SDF_CACHE_DIR = "out/sdf_cache"


def make_vehicle_box_sdf():
    mesh = trimesh.creation.box(extents=BOX_DIMS_M)
    if not mesh.is_watertight:
        raise RuntimeError("Generated vehicle box mesh is not watertight")
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    sdf = build_sdf_cached(
        verts,
        faces,
        res=SDF_RES,
        margin_cells=SDF_MARGIN_CELLS,
        cache_dir=SDF_CACHE_DIR,
    )
    print(f"vehicle box SDF: res={sdf.res}, cell={sdf.cell:.5f} m")
    return sdf


def make_water_block(grid: GridConfig, floor_z=0.0, depth=0.30, velocity_x=1.5):
    dx = grid.dx
    h = 0.5 * dx
    x = np.arange(0.30, 3.80, h)
    y = np.arange(3.00, 7.00, h)
    z = np.arange(floor_z, floor_z + depth, h)
    pts = np.stack(np.meshgrid(x, y, z, indexing="ij"), -1).reshape(-1, 3)
    pts = pts[::4].astype(np.float32)
    vol = np.full(len(pts), h**3 * 4.0, dtype=np.float32)
    vel = np.zeros_like(pts, dtype=np.float32)
    vel[:, 0] = velocity_x
    return pts, vol, vel


def main(device="auto"):
    grid = GridConfig(n_grid=288, grid_lim=DOMAIN_SIZE_M)
    floor_z = 3.0 * grid.dx
    sdf = make_vehicle_box_sdf()

    water_pos, water_vol, water_vel = make_water_block(grid, floor_z=floor_z)
    solver = Solver(grid=grid, device=device).load_particles(water_pos, water_vol)
    solver.set_material(newtonian(eta=0.001, density=1000.0, bulk_modulus=2.0e5))

    solver.set_v(water_vel)

    solver.add_plane(point=(0.0, 0.0, floor_z), normal=(0.0, 0.0, 1.0), surface="slip", friction=0.2)

    dx = grid.dx
    margin = 4.0 * dx
    lo, hi = margin, DOMAIN_SIZE_M - margin
    solver.add_plane(point=(lo, 0.0, 0.0), normal=(1.0, 0.0, 0.0), surface="slip", friction=0.2)
    solver.add_plane(point=(hi, 0.0, 0.0), normal=(-1.0, 0.0, 0.0), surface="slip", friction=0.2)
    solver.add_plane(point=(0.0, lo, 0.0), normal=(0.0, 1.0, 0.0), surface="slip", friction=0.2)
    solver.add_plane(point=(0.0, hi, 0.0), normal=(0.0, -1.0, 0.0), surface="slip", friction=0.2)
    print(f"lateral slip walls at {lo:.4f} & {hi:.4f} m (2*dx={margin:.4f} m inside domain [0, {DOMAIN_SIZE_M}])")

    vehicle_center = (6.5, 5.0, floor_z + BOX_DIMS_M[2] / 2.0)
    vehicle = solver.add_sdf_collider(
        sdf,
        center=vehicle_center,
        quat=(0.0, 0.0, 0.0, 1.0),
        velocity=(0.0, 0.0, 0.0),
        omega=(0.0, 0.0, 0.0),
        surface="separable",
        friction=0.55,
    )

    dt = 1.0e-4
    substeps = 20
    sim_time = 1.0
    report_every = 0.02

    step_dt = dt * substeps
    n_steps = max(1, round(sim_time / step_dt))
    report_stride = max(1, round(report_every / step_dt))
    print(f"running {sim_time:.2f} s ({n_steps} steps x {substeps} substeps, dt={dt:g}); "
          f"expect first water contact near t~0.25 s")

    t = 0.0
    peak_force = 0.0
    peak_time = 0.0
    for i in range(n_steps):
        solver.reset_sdf_force(vehicle)
        solver.step(dt, substeps=substeps)
        wrench = solver.sdf_wrench(vehicle, step_dt)
        t += step_dt
        force = np.asarray(wrench["force"], dtype=float)
        torque = np.asarray(wrench["torque"], dtype=float)
        fmag = float(np.linalg.norm(force))
        if fmag > peak_force:
            peak_force, peak_time = fmag, t
        if i % report_stride == 0 or i == n_steps - 1:
            print(f"t={t:6.3f}s  |F|={fmag:9.2f} N  force={force}  torque={torque}")

    print(f"peak |force| = {peak_force:.2f} N at t={peak_time:.3f} s")
    return solver, vehicle


if __name__ == "__main__":
    main()
