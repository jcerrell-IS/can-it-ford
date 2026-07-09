"""
Minimal box-shaped vehicle proxy as a mesh-SDF collider for kks32/mpm-engine.
Dimensions are metres: length/width/height = (4.66, 1.79, 1.44), a sedan bounding box.
Length runs along +x, the flow direction (nose-on to the current).
Run from the mpm-engine repo root after installing geometry extras:
    python /home/user/workspace/box_sdf_collider_setup.py
"""
from __future__ import annotations

import numpy as np
import trimesh

from warpmpm import GridConfig, Solver
from warpmpm.geometry import build_sdf_cached
from warpmpm.materials import newtonian

BOX_DIMS_M = (4.66, 1.79, 1.44)  # x=length (along +x flow), y=width, z=height (m)
DOMAIN_SIZE_M = 10.0  # cubic domain [0, DOMAIN_SIZE_M]^3 (m); >= 2x sedan length for upstream/downstream room
SDF_RES = 96
SDF_MARGIN_CELLS = 6.0
SDF_CACHE_DIR = "out/sdf_cache"


def make_vehicle_box_sdf():
    # trimesh.creation.box returns a closed triangular box mesh centered at the origin.
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
        # A box is convex and centered at the origin, so the default centroid probe is inside.
    )
    print(f"vehicle box SDF: res={sdf.res}, cell={sdf.cell:.5f} m")
    return sdf


def make_water_block(grid: GridConfig, depth=0.30, velocity_x=1.5):
    """Small smoke-test water block. Replace with project particles/volumes for production."""
    dx = grid.dx
    h = 0.5 * dx
    # Seed from near the upstream (low-x) edge to x=3.80, ~0.37 m short of the vehicle's
    # upstream face at x=4.17 (center 6.5 - length 4.66/2), leaving a gap for flow to develop.
    # y spans 3..7 (4 m) around y=5.0, enveloping the vehicle's y=[4.11, 5.90] (width 1.79).
    x = np.arange(0.30, 3.80, h)
    y = np.arange(3.00, 7.00, h)
    z = np.arange(0.05, depth, h)
    pts = np.stack(np.meshgrid(x, y, z, indexing="ij"), -1).reshape(-1, 3)
    # Keep the smoke test small on CPU; production should use a denser water particle set.
    pts = pts[::4].astype(np.float32)
    vol = np.full(len(pts), h**3 * 4.0, dtype=np.float32)
    vel = np.zeros_like(pts, dtype=np.float32)
    vel[:, 0] = velocity_x
    return pts, vol, vel


def main(device="auto"):
    grid = GridConfig(n_grid=192, grid_lim=DOMAIN_SIZE_M)
    floor_z = 0.0
    sdf = make_vehicle_box_sdf()

    water_pos, water_vol, water_vel = make_water_block(grid)
    solver = Solver(grid=grid, device=device).load_particles(water_pos, water_vol)
    solver.set_material(newtonian(eta=0.001, density=1000.0, bulk_modulus=2.0e5))

    solver.set_v(water_vel)

    solver.add_plane(point=(0.0, 0.0, floor_z), normal=(0.0, 0.0, 1.0), surface="slip", friction=0.2)

    # --- Lateral confinement walls -------------------------------------------------
    # P2G/G2P use a quadratic B-spline stencil reaching ~2 cells; a particle that drifts
    # within 2*dx of a true domain edge pushes the stencil off-grid and crashes the run.
    # Reflect settling/splashing particles with slip walls placed 2*dx *inside* each
    # lateral edge. Inward-pointing normals match the floor plane convention above; the
    # floor (low-z) is already handled and the top (high-z) is left open for the free
    # surface to rise. dx = grid_lim / n_grid, so this tracks DOMAIN_SIZE_M automatically.
    dx = grid.dx
    margin = 2.0 * dx
    lo, hi = margin, DOMAIN_SIZE_M - margin
    solver.add_plane(point=(lo, 0.0, 0.0), normal=(1.0, 0.0, 0.0), surface="slip", friction=0.2)   # low-x
    solver.add_plane(point=(hi, 0.0, 0.0), normal=(-1.0, 0.0, 0.0), surface="slip", friction=0.2)  # high-x
    solver.add_plane(point=(0.0, lo, 0.0), normal=(0.0, 1.0, 0.0), surface="slip", friction=0.2)   # low-y
    solver.add_plane(point=(0.0, hi, 0.0), normal=(0.0, -1.0, 0.0), surface="slip", friction=0.2)  # high-y
    print(f"lateral slip walls at {lo:.4f} & {hi:.4f} m (2*dx={margin:.4f} m inside domain [0, {DOMAIN_SIZE_M}])")

    vehicle_center = (6.5, 5.0, floor_z + BOX_DIMS_M[2] / 2.0)
    vehicle = solver.add_sdf_collider(
        sdf,
        center=vehicle_center,
        quat=(0.0, 0.0, 0.0, 1.0),   # identity, order x,y,z,w for this SDF path
        velocity=(0.0, 0.0, 0.0),
        omega=(0.0, 0.0, 0.0),
        surface="separable",
        friction=0.55,
        # band=None uses the solver grid dx; ensure SDF margin_cells leaves boundary_min > dx.
    )

    # --- Longer run to develop contact forces ------------------------------------
    # The water slug's leading edge starts at x=3.80, ~0.37 m upstream of the vehicle
    # face at x=4.17, moving +x at velocity_x=1.5 m/s -> first contact at ~0.37/1.5
    # = 0.25 s. Run well past that so the impact force ramps and peaks.
    # dt=1e-4 s keeps a large CFL margin: sound speed = sqrt(bulk/rho)
    # = sqrt(2e5/1e3) = 14.1 m/s, dx=0.052 m -> dx/c = 3.7e-3 s (~37x headroom).
    dt = 1.0e-4
    substeps = 20            # sub-timesteps advanced per step() call -> 2 ms of sim per step
    sim_time = 1.0           # total physical time to simulate (s); the main runtime knob
    report_every = 0.02      # seconds of sim time between force reports

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
