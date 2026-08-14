"""DISPATCH 9: a driven vehicle on the warpmpm moving-SDF-collider path.

ARMS, ranked by defensibility, not ambition (the dispatch's ranking, kept):
  (a) PRESCRIBED KINEMATICS. Constant velocity through still water. The only arm the
      validation literature covers, so the only arm with a comparison.
  (b) PRESCRIBED VELOCITY WITH A TRACTION BUDGET CHECK. Arm (a) plus a per-step
      diagnostic: is the drag the vehicle must overcome larger than the traction its
      tyres can supply? This is the graded result.
  (c) FREE 6-DOF WITH PROPULSION is NOT implemented here. It is unvalidatable (no
      published source applies engine torque in a coupled flood simulation) and it is
      blocked by the COM-offset trap below. Arm (c) must not be run on a real hull
      until COM-offset migration exists.

ARM (b) IS A STRICT SUPERSET OF ARM (a)'s PHYSICS. Identical scene, identical solver
calls, identical RNG draws; (b) only adds post-hoc arithmetic over the same trace. So
running both at one seed is a NON-DETERMINISM CONTROL: any difference in the shared
columns is solver non-determinism, not an arm effect. --arm both exploits that.

WHY THE TRACTION BUDGET SURVIVES THE ENGINE'S LIMITATION. The net force on the hull
cannot be DECOMPOSED into hydrodynamic, contact and gravitational parts. The traction
budget does not need it to be:

    F_N     = W - Fz_up            net normal load, ONE number, no decomposition
    F_avail = mu * F_N             available traction
    F_dem   = F_drive + mu_RO*F_N  drag along travel, plus rolling resistance

Only the NET vertical reaction enters. That is why arm (b) is reportable while the
individual force components are not.

CAVEATS CARRIED INTO EVERY OUTPUT RECORD, not just the docs:
  * no_rigid_pressure: mpm_utils.py:1100 initialises rigid-particle stress to a zero
    mat33 and :1104 excludes material 8 from the SVD, and no mat==8 branch in
    :1105-1147 ever assigns one. On the free-rigid path a rigid hull therefore exerts
    NO PRESSURE on the water. THIS SCENE USES THE SDF-COLLIDER PATH, which is a grid
    boundary condition and does push water, and which DOES have a force accumulator
    (param.force / param.torque, read by sdf_wrench). The defect is recorded because
    the project's standing note is easy to misapply across the two paths.
  * cannot_decompose: the wrench is a net reaction. Drag, buoyancy, lift and contact
    are not separable from it.
  * at_rest_gate: the at-rest vertical reaction is checked against rho*g*V_submerged
    before any moving number is read. The exploratory scene FAILED this gate. If it
    fails here the moving numbers are qualitative only, and the record says so.

TRAPS HONOURED HERE, each verified by tests/test_sdf_wrench_contract.py (3/3 PASS on
the pinned engine, LS6 CPU, 2026-08-14):
  1 wrench dt is the TICK duration (substeps*dt), never dt_sub. Measured inflation
    factor when got wrong: exactly n_substeps.
  2 reset_sdf_force every tick; nothing in the engine zeroes it automatically.
  3 quaternion is XYZW here, matching wp.quat. The cup path's WXYZ tuple would rotate
    the hull 90 degrees differently and SILENTLY.
  4 COM offset: not engaged, because arms (a) and (b) prescribe the pose and never
    integrate free rotation. Guarded by --arm refusing 'c'.
  5 periodic_x is never enabled: add_cdf_collider guards on it, add_sdf_collider does
    NOT, so the combination would be silently wrong.
  band: add_sdf_collider's band defaults to ONE dx, flat and not feature-scaled, so
    thin features inflate to at least one cell. Reported as band_over_depth.

ENGINE: warpmpm at pinned SHA 544c93dd02cb9c7ead89e1155a62967243244fce.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------------
# Scene constants. Every one traces to the canonical driver or to a cited source.
# ---------------------------------------------------------------------------------
WATER_DENSITY = 1000.0     # CLAUDE.md physical anchor
WATER_ETA = 1.0e-3
BULK_MODULUS = 1.5e5       # sim_standing.py
EOS_GAMMA = 1.1            # the 1.1 inside sim_standing.py's sound speed
G = 9.81                   # CLAUDE.md item 3: solver hardcodes 9.81, NOT 9.80665
FPS = 30
COLLIDER_SURFACE = "separable"   # add_sdf_collider default, NOT tuned
COLLIDER_FRICTION = 0.4          # add_sdf_collider default, NOT tuned
SDF_MARGIN_CELLS = 6.0           # box_sdf_collider_setup.py:13
WN_CHUNK = 128                   # winding-number point chunk; a numerical identity
                                 # vs the 4096 default, and 4096 needs 64 GiB on the
                                 # 655k-face Yaris hull (OOM, commit 9480b0a exit 137)

# Traction parameters, with provenance. Do not invent these.
MU_PARKED = 0.30      # Bonham and Hattersley 1967, conservative for hazard curves
MU_PARALLEL = 0.52    # measured parallel to flow
MU_TYRE_WET = 0.75    # Smith, Modra, Felder 2019, wet concrete
MU_RO = 0.092         # rolling resistance, Shah et al. 2018
CD_LOW, CD_HIGH = 1.22, 6.82   # Hu et al. 2023, JOINT envelope over 3 vehicles and
                               # ALL flow directions. The midpoint is not an estimate.


def build_hull_sdf(mesh, res, cache_dir):
    """Stock warpmpm build_sdf_cached with only the winding-number point chunk reduced.

    The chunk splits the POINT axis only; each point's solid-angle sum still runs over
    all faces in the same order, so it is a numerical identity (verified bitwise in the
    2026-08-11 exploratory work), and it drops peak memory from 64 GiB to 0.83 GiB.
    """
    from warpmpm.geometry import mesh_sdf as _ms
    _orig = _ms._winding_number
    _ms._winding_number = lambda p, vt, f, chunk=WN_CHUNK: _orig(p, vt, f, chunk=chunk)
    try:
        from warpmpm.geometry import build_sdf_cached
        return build_sdf_cached(
            np.asarray(mesh.vertices, dtype=np.float64),
            np.asarray(mesh.faces, dtype=np.int64),
            res=int(res), margin_cells=SDF_MARGIN_CELLS, cache_dir=str(cache_dir))
    finally:
        _ms._winding_number = _orig


def sdf_nearest(sdf, pts_body):
    """Nearest-cell SDF lookup, accurate to half an SDF cell. Used to carve water out
    of the hull and its contact band before the run starts."""
    idx = np.rint((pts_body - np.asarray(sdf.origin)) / sdf.cell).astype(np.int64)
    res = sdf.values.shape[0]
    ok = np.all((idx >= 0) & (idx < res), axis=1)
    out = np.full(len(pts_body), np.inf)
    j = idx[ok]
    out[ok] = sdf.values[j[:, 0], j[:, 1], j[:, 2]]
    return out


def submerged_volume(particles, h, waterline_z_body):
    """V_submerged from the vetted solidify fill, in the BODY frame (floor at z=0)."""
    return float((particles[:, 2] < waterline_z_body).sum()) * h ** 3


class DrivenHullScene:
    """Hull driven at prescribed velocity along +y (its own long axis) through still
    water. NOT the AR&R stationary side-on configuration."""

    def __init__(self, ply, n_grid, depth, velocity, sdf_res, cache_dir, mass,
                 device="cuda:0", mesh_seed=0, water_seed=0, fill_pitch=0.025):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
        from vetted_loader import load_as_ran_canonicalize, load_vehicle_live

        canonicalize = load_as_ran_canonicalize()
        mod = load_vehicle_live()

        # SEEDED: load_vehicle draws 60,000 RANDOM surface samples and derives the mesh
        # shift from them. canonicalize cancels that shift mathematically but not
        # bitwise, leaving ~1 ULP, which changes build_sdf_cached's content hash and
        # forces a full SDF rebuild every run. Seeding makes the cache usable.
        np.random.seed(int(mesh_seed))
        v = canonicalize(mod.load_vehicle(ply, up="z"))
        self.mesh_volume = float(abs(v.mesh.volume))

        # Fine fill for the analytic submerged volume. The loader default pitch
        # (extent/32 = 0.148 m here) quantises the waterline into ~0.15 m steps.
        v.solidify(float(fill_pitch))
        self.fill_pitch = float(fill_pitch)
        self.fill_particles = np.asarray(v.particles, dtype=float)
        self.fill_volume = len(self.fill_particles) * fill_pitch ** 3

        ext = np.asarray(v.mesh.extents, dtype=float)
        self.ext = ext
        self.velocity = float(velocity)
        self.depth = float(depth)
        self.mass = float(mass)
        self.weight_N = self.mass * G

        t0 = time.time()
        sdf = build_hull_sdf(v.mesh, sdf_res, cache_dir)
        self.sdf_build_s = time.time() - t0
        self.sdf_res = int(sdf_res)

        from warpmpm.core.solver import GridConfig, Solver
        from warpmpm.materials import newtonian

        # Domain rule, as-ran: lim = max(2.2*ext_long, 3.5*ext_short, 6*depth).
        # THE AXIS TRAP: ext[1] is the LONG axis after load_vehicle's permutation, so
        # taking PLY axes at face value gives 14.989 m instead of 9.4217 m for the
        # Yaris, a 59 percent error. Here ext is the canonicalized mesh extent.
        lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
        grid = GridConfig(n_grid=int(n_grid), grid_lim=lim)
        dx = grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        wall = 4.0 * dx
        self.lim, self.dx, self.h, self.floor, self.wall = lim, dx, h, floor, wall
        self.n_grid = int(n_grid)

        # Placement: centred across the channel, set back so the hull has travel room.
        half_len = float(ext[1]) / 2.0
        clearance = 2.0 * dx
        self.half_len = half_len
        self.y_start = wall + half_len + clearance
        self.center0 = np.array([0.50 * lim, self.y_start, floor], dtype=float)
        self.travel_available = (lim - wall - clearance) - (self.y_start + half_len)

        # Water block, sim_standing.py's construction.
        rng = np.random.default_rng(int(water_seed))
        xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        ys = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        self.water_layers = len(zs)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)
        n_before = len(water)

        # Carve water out of the hull AND its contact band, so no particle starts
        # inside the band where the collider BC acts.
        inside = sdf_nearest(sdf, water - self.center0) < dx
        water = water[~inside].astype(np.float32)
        self.n_carved = int(inside.sum())
        self.n_water = len(water)
        self.n_water_before_carve = int(n_before)

        vol = np.full(len(water), h ** 3, dtype=np.float32)
        s = Solver(grid=grid, device=device).load_particles(water, vol)
        s.set_material(newtonian(eta=WATER_ETA, density=WATER_DENSITY,
                                 bulk_modulus=BULK_MODULUS))
        # Planes act on WATER ONLY: this scene has no rigid PARTICLES, so the canonical
        # 0.55 vehicle-on-bed Coulomb coefficient has nothing to act on and applying it
        # to water would be an unsourced bed-friction model. validate_coupling_force.py
        # makes the same deviation for the same reason. NOTE mpm_solver_warp.py:1915
        # registers rigid contact only when restitution is non-zero, and there is no
        # rigid body here to register.
        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
        for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                        ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
        s.add_domain_walls()

        # TRAP 3: XYZW. (0,0,0,1) is identity in XYZW; in the cup path's WXYZ it would
        # be a 180 degree rotation about z.
        # TRAP 5: periodic_x is never set on this solver.
        self.handle = s.add_sdf_collider(
            sdf, center=tuple(self.center0), quat=(0.0, 0.0, 0.0, 1.0),
            velocity=(0.0, 0.0, 0.0), omega=(0.0, 0.0, 0.0),
            surface=COLLIDER_SURFACE, friction=COLLIDER_FRICTION)
        self.solver, self.sdf = s, sdf

        # CFL and substeps, sim_standing.py's construction.
        c = float(np.sqrt(EOS_GAMMA * BULK_MODULUS / WATER_DENSITY))
        self.sound_speed = c
        rate = max(c / (0.28 * dx),
                   6.0 * WATER_ETA / (WATER_DENSITY * dx * dx),
                   max(self.velocity, 1e-6) / (0.5 * dx))
        self.substeps = int(np.ceil(rate / FPS))
        self.dt = (1.0 / FPS) / self.substeps
        self.tick_dt = 1.0 / FPS          # TRAP 1: this is what sdf_wrench gets
        self.sweep_per_substep = self.velocity * self.dt
        self.band_over_depth = dx / float(depth)
        self.depth_cells = float(depth) / dx
        self.time = 0.0

        # Analytic buoyancy target for the at-rest gate. The hull floor sits at
        # z = floor, so the waterline in BODY coordinates is at depth.
        self.V_sub_analytic = submerged_volume(self.fill_particles, fill_pitch, depth)
        self.B_analytic_N = WATER_DENSITY * G * self.V_sub_analytic

    # -- engine reads, never assumptions -------------------------------------------
    def collider_center(self):
        c = self.solver._sim.collider_params[self.handle].center
        return np.array([float(c[0]), float(c[1]), float(c[2])], dtype=float)

    def set_drive_speed(self, v):
        """Velocity only, never center: modify_bc integrates center += dt*velocity
        every substep, so writing center as well would double-advance the hull."""
        self.solver.set_sdf_pose(self.handle, velocity=(0.0, float(v), 0.0))

    def tick(self):
        """One frame. TRAP 2: reset first. TRAP 1: wrench gets the TICK duration."""
        s = self.solver
        s.reset_sdf_force(self.handle)
        s.step(self.dt, self.substeps)
        self.time += self.tick_dt
        return s.sdf_wrench(self.handle, dt=self.tick_dt)

    def floor_penetration_dx(self):
        x = self.solver.x()
        return float((self.floor - float(x[:, 2].min())) / self.dx)


def traction_record(fz_up_N, f_drive_N, weight_N):
    """Arm (b). Needs only the NET vertical reaction, so it survives the engine's
    inability to decompose the wrench."""
    F_N = max(weight_N - fz_up_N, 0.0)
    out = {"F_N_net_normal_N": F_N, "Fz_up_measured_N": fz_up_N,
           "drag_along_travel_N": f_drive_N}
    for name, mu in (("mu0p30", MU_PARKED), ("mu0p52", MU_PARALLEL),
                     ("mu0p75", MU_TYRE_WET)):
        avail = mu * F_N
        demand = abs(f_drive_N) + MU_RO * F_N
        out[f"F_avail_{name}_N"] = avail
        out[f"margin_{name}_N"] = avail - demand
        out[f"demand_over_avail_{name}"] = (demand / avail) if avail > 0 else float("inf")
    out["demand_N"] = abs(f_drive_N) + MU_RO * F_N
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ply", required=True, type=Path)
    ap.add_argument("--arm", default="both", choices=["a", "b", "both"],
                    help="'c' is deliberately absent: free 6-DOF with propulsion is "
                         "unvalidatable and blocked by the COM-offset trap")
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--depth", type=float, default=0.30)
    ap.add_argument("--velocity", type=float, default=1.5)
    ap.add_argument("--mass", type=float, default=1609.0,
                    help="kg. 1609 = AR&R reference for the Rogue; NHTSA AWD is 1610")
    ap.add_argument("--sdf-res", type=int, default=32)
    ap.add_argument("--settle-frames", type=int, default=60)
    ap.add_argument("--ramp-frames", type=int, default=15)
    ap.add_argument("--drive-frames", type=int, default=90)
    ap.add_argument("--mesh-seed", type=int, default=0)
    ap.add_argument("--water-seed", type=int, default=0)
    ap.add_argument("--fill-pitch", type=float, default=0.025)
    ap.add_argument("--device", default=None)
    ap.add_argument("--cache-dir", type=Path, default=Path("./sdf_cache"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tag", default="run")
    args = ap.parse_args()

    import warp as wp
    wp.init()
    device = args.device or ("cuda:0" if wp.get_cuda_device_count() > 0 else "cpu")

    args.out.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 84)
    print("DISPATCH 9: driven hull on the warpmpm moving-SDF path")
    print("=" * 84)
    t_start = time.time()
    sc = DrivenHullScene(args.ply, args.n_grid, args.depth, args.velocity,
                         args.sdf_res, args.cache_dir, args.mass, device=device,
                         mesh_seed=args.mesh_seed, water_seed=args.water_seed,
                         fill_pitch=args.fill_pitch)

    print(f"\ndevice            {device}")
    print(f"grid              n_grid={sc.n_grid}  grid_lim={sc.lim:.9f}  dx={sc.dx:.6f}")
    print(f"water             depth={sc.depth} m  layers={sc.water_layers}  "
          f"n={sc.n_water} (carved {sc.n_carved} of {sc.n_water_before_carve})")
    print(f"RESOLUTION        depth_cells={sc.depth_cells:.3f}   "
          f"band/depth={sc.band_over_depth:.3f}")
    print(f"substeps/frame    {sc.substeps}   dt={sc.dt:.3e} s   tick={sc.tick_dt:.6f} s")
    print(f"sdf               res={sc.sdf_res}  build={sc.sdf_build_s:.1f} s")
    print(f"hull              mesh V={sc.mesh_volume:.6f} m3  fill V={sc.fill_volume:.6f} m3"
          f"  ({100*(sc.fill_volume/sc.mesh_volume-1):+.2f}%)")
    print(f"mass              {sc.mass:.1f} kg   W={sc.weight_N:.1f} N")
    print(f"travel available  {sc.travel_available:.3f} m at {sc.velocity} m/s "
          f"= {sc.travel_available/max(sc.velocity,1e-9):.2f} s")
    print(f"sweep/substep     {sc.sweep_per_substep*1e3:.3f} mm vs band {sc.dx*1e3:.1f} mm")

    # ---- AT-REST GATE -----------------------------------------------------------
    print(f"\n--- settle, {args.settle_frames} frames at rest ---")
    settle = []
    for i in range(args.settle_frames):
        w = sc.tick()
        f = np.asarray(w["force"], dtype=float)
        settle.append({"frame": i + 1, "fz_N": float(f[2]),
                       "force_N": f.tolist()})
        if (i + 1) % 20 == 0:
            print(f"  frame {i+1:4d}  Fz={f[2]:12.1f} N   "
                  f"analytic rho*g*V_sub={sc.B_analytic_N:.1f} N")

    fz_rest = float(np.mean([r["fz_N"] for r in settle[-10:]]))
    gate_err = 100.0 * (fz_rest - sc.B_analytic_N) / sc.B_analytic_N
    gate_pass = abs(gate_err) <= 10.0
    print(f"\nAT-REST GATE: Fz(last 10 frames mean) = {fz_rest:.1f} N")
    print(f"              analytic rho*g*V_sub     = {sc.B_analytic_N:.1f} N "
          f"(V_sub={sc.V_sub_analytic:.6f} m3)")
    print(f"              error {gate_err:+.2f}%   -> {'PASS' if gate_pass else 'FAIL'}")
    if not gate_pass:
        print("              Moving force numbers are QUALITATIVE ONLY. This is the")
        print("              known state of this scene: the water column is resolved to")
        print(f"              {sc.depth_cells:.2f} cells against the validated harness's 18.")

    # ---- RAMP + DRIVE -----------------------------------------------------------
    print(f"\n--- ramp {args.ramp_frames} frames, then drive {args.drive_frames} ---")
    rows = []
    for i in range(args.ramp_frames):
        v_cmd = sc.velocity * (i + 1) / args.ramp_frames
        sc.set_drive_speed(v_cmd)
        w = sc.tick()
        f = np.asarray(w["force"], dtype=float)
        t = np.asarray(w["torque"], dtype=float)
        c = sc.collider_center()
        rows.append({"phase": "ramp", "frame": i + 1, "t_s": sc.time, "v_cmd_ms": v_cmd,
                     "in_ramp": True, "center_m": c.tolist(),
                     "force_N": f.tolist(), "torque_Nm": t.tolist(),
                     **traction_record(float(f[2]), float(f[1]), sc.weight_N)})

    for i in range(args.drive_frames):
        sc.set_drive_speed(sc.velocity)
        w = sc.tick()
        f = np.asarray(w["force"], dtype=float)
        t = np.asarray(w["torque"], dtype=float)
        c = sc.collider_center()
        rec = {"phase": "drive", "frame": i + 1, "t_s": sc.time,
               "v_cmd_ms": sc.velocity, "in_ramp": False, "center_m": c.tolist(),
               "force_N": f.tolist(), "torque_Nm": t.tolist(),
               **traction_record(float(f[2]), float(f[1]), sc.weight_N)}
        rows.append(rec)
        if (i + 1) % 15 == 0:
            print(f"  drive {i+1:4d}  y={c[1]:7.3f} m  Fy(drag)={f[1]:11.1f} N  "
                  f"Fz={f[2]:11.1f} N  demand/avail(mu=0.30)="
                  f"{rec['demand_over_avail_mu0p30']:.3f}")
        if c[1] + sc.half_len > sc.lim - sc.wall:
            print(f"  STOP at frame {i+1}: hull reached the downstream wall.")
            break

    drive = [r for r in rows if r["phase"] == "drive"]
    finite = [r for r in drive if np.isfinite(r["force_N"]).all()]
    print(f"\n--- summary ---")
    print(f"drive frames      {len(drive)}   non-finite {len(drive)-len(finite)}")
    if finite:
        fy = np.array([r["force_N"][1] for r in finite])
        fz = np.array([r["force_N"][2] for r in finite])
        ratio = np.array([r["demand_over_avail_mu0p30"] for r in finite])
        print(f"drag Fy           mean {fy.mean():11.1f}  min {fy.min():11.1f}  "
              f"max {fy.max():11.1f} N")
        print(f"vertical Fz       mean {fz.mean():11.1f}  min {fz.min():11.1f}  "
              f"max {fz.max():11.1f} N")
        print(f"peak/mean |Fy|    {np.abs(fy).max()/max(np.abs(fy).mean(),1e-12):.2f}  "
              f"(a steady value would be near 1)")
        print(f"demand/avail      mean {ratio.mean():.3f}  max {ratio.max():.3f} "
              f"(mu=0.30, >1 means drag exceeds available traction)")
        print(f"floor penetration {sc.floor_penetration_dx():.3f} dx")

    meta = {
        "dispatch": 9, "tag": args.tag, "arm": args.arm,
        "engine_pinned_sha": "544c93dd02cb9c7ead89e1155a62967243244fce",
        "device": device, "warp": wp.config.version,
        "hull": str(args.ply), "mass_kg": sc.mass, "weight_N": sc.weight_N,
        "n_grid": sc.n_grid, "grid_lim_m": sc.lim, "dx_m": sc.dx,
        "depth_m": sc.depth, "depth_cells": sc.depth_cells,
        "band_over_depth": sc.band_over_depth, "water_layers": sc.water_layers,
        "n_water": sc.n_water, "n_carved": sc.n_carved,
        "velocity_ms": sc.velocity, "substeps": sc.substeps, "dt_s": sc.dt,
        "tick_dt_s": sc.tick_dt, "sdf_res": sc.sdf_res,
        "sdf_build_s": sc.sdf_build_s, "mesh_volume_m3": sc.mesh_volume,
        "fill_volume_m3": sc.fill_volume, "fill_pitch_m": sc.fill_pitch,
        "V_sub_analytic_m3": sc.V_sub_analytic, "B_analytic_N": sc.B_analytic_N,
        "at_rest_gate": {"fz_rest_N": fz_rest, "error_pct": gate_err,
                         "pass": bool(gate_pass),
                         "meaning": "vertical reaction vs rho*g*V_submerged"},
        "mesh_seed": args.mesh_seed, "water_seed": args.water_seed,
        "wall_clock_s": time.time() - t_start,
        "traction_params": {"mu_parked": MU_PARKED, "mu_parallel": MU_PARALLEL,
                            "mu_tyre_wet": MU_TYRE_WET, "mu_RO": MU_RO,
                            "C_D_band": [CD_LOW, CD_HIGH]},
        "caveats": {
            "cannot_decompose": "The wrench is a NET reaction. Drag, buoyancy, lift "
                                "and contact are not separable from it.",
            "no_rigid_pressure": "mpm_utils.py:1100/:1104 leave material-8 rigid "
                                 "particles with zero stress, so on the FREE-RIGID "
                                 "path a hull exerts no pressure on water. This scene "
                                 "uses the SDF-COLLIDER path (a grid BC with a real "
                                 "force accumulator), so the defect does not apply "
                                 "directly here, but the two paths must not be "
                                 "conflated.",
            "at_rest_gate": "If the at-rest gate FAILS, no force number here is "
                            "quotable; report them as resolution evidence only.",
            "configuration": "Driven along +y, the hull's own long axis. NOT the AR&R "
                             "stationary side-on case. No FORD verdict follows.",
            "arm_c_absent": "Free 6-DOF with propulsion is not implemented: no "
                            "published source applies engine torque in a coupled "
                            "flood simulation, and the COM-offset trap blocks free "
                            "rotation on a non-centre-symmetric hull.",
        },
    }
    (args.out / f"{args.tag}_summary.json").write_text(json.dumps(meta, indent=2))
    (args.out / f"{args.tag}_settle.json").write_text(json.dumps(settle, indent=2))
    (args.out / f"{args.tag}_trace.json").write_text(json.dumps(rows, indent=2))

    # CSV for the trace, so it can be read without a json parser
    import csv
    keys = ["phase", "frame", "t_s", "v_cmd_ms", "in_ramp", "y_m", "fx_N", "fy_N",
            "fz_N", "F_N_net_normal_N", "F_avail_mu0p30_N", "demand_N",
            "demand_over_avail_mu0p30", "margin_mu0p30_N"]
    with (args.out / f"{args.tag}_trace.csv").open("w", newline="") as f:
        wcsv = csv.DictWriter(f, fieldnames=keys)
        wcsv.writeheader()
        for r in rows:
            wcsv.writerow({
                "phase": r["phase"], "frame": r["frame"], "t_s": r["t_s"],
                "v_cmd_ms": r["v_cmd_ms"], "in_ramp": r["in_ramp"],
                "y_m": r["center_m"][1], "fx_N": r["force_N"][0],
                "fy_N": r["force_N"][1], "fz_N": r["force_N"][2],
                "F_N_net_normal_N": r["F_N_net_normal_N"],
                "F_avail_mu0p30_N": r["F_avail_mu0p30_N"], "demand_N": r["demand_N"],
                "demand_over_avail_mu0p30": r["demand_over_avail_mu0p30"],
                "margin_mu0p30_N": r["margin_mu0p30_N"]})

    print(f"\nwrote {args.out}/{args.tag}_*.json and _trace.csv")
    print(f"wall clock {meta['wall_clock_s']:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
