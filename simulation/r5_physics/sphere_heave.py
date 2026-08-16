"""Kramer et al. 2021 floating-sphere heave decay, as an SDF-collider scene in warpmpm.

WHY THIS EXISTS
---------------
CLAUDE.md item 6 records that no gate in this project is a physics validation: every
gate is a self-consistency or numerical-containment check, and G-3 compares against a
constant derived from the same pipeline. The at-rest buoyancy gate was separately shown
to be tunable (every resolution contains a band width that passes it). This scene is an
attempt at the first EXTERNAL validation the project would have: a published physical
experiment, with published uncertainty, that the solver has never seen.

THE BENCHMARK
-------------
Kramer, Andersen, Thomas, Bendixen, Bingham, Read, Holk, Ransley, Brown, Yu, Tran,
Davidson, Horvath, Janson, Nielsen & Eskilsson (2021), "Highly Accurate Experimental
Heave Decay Tests with a Floating Sphere: A Public Benchmark Dataset for Model
Validation of Fluid-Structure Interaction", Energies 14(2):269,
doi:10.3390/en14020269. Gold OA, CC-BY (verified via Unpaywall 2026-08-16).

NOT the same paper as Kramer, Terheiden & Wieprecht 2016 (watertightness,
doi:10.1016/J.IJDRR.2016.04.003) already in the register. Same first author only.

Test case, read directly from the paper's full text (scite full-text excerpts,
2026-08-16), not recalled:
  * sphere diameter D = 300 mm, ballasted to half submergence, so the waterline sits
    at the equator at rest;
  * three drop heights H0 = {0.1D, 0.3D, 0.5D} (linear, moderately nonlinear, and a
    highly nonlinear case released with the whole sphere above the water);
  * "around eight natural periods in heave should be captured for comparison";
  * wave basin 13.00 x 8.44 m, water depth 900 mm;
  * expanded uncertainty ~0.3% of the respective drop heights at 95% confidence.

Half submergence FIXES the mass: m = rho_w * V/2 = 7.0686 kg at rho_w = 1000, i.e. a
mean sphere density of exactly 500 kg/m3. The paper's Table 1 carries the measured
values; they are NOT reproduced here because the tables did not come through the
full-text extraction and MDPI/DTU are both behind a bot wall from this host. Anything
this script prints as "published" is therefore derived from the half-submergence
constraint, and is labelled DERIVED, never READ.

WHAT IS DELIBERATELY DIFFERENT FROM THE EXPERIMENT, AND WHY
-----------------------------------------------------------
1. Basin size. 13.00 x 8.44 m cannot be resolved at the dx a 300 mm sphere needs. The
   domain here is a square tank of side `lim`. The radiated wave is deep-water
   (L = 0.9425 m at T_n = 0.777 s), so its ENERGY travels at the group velocity
   c_g = g*T/(4*pi) = 0.6065 m/s, not at sqrt(g*h) = 2.2 m/s. `reflection_return_s`
   reports when wall reflections first contaminate the sphere; only cycles before it
   may be compared. This is a truncation of the comparison window, not of the physics.
2. Water depth. 900 mm is reduced to `depth`. At 500 mm, kh = 3.333 and
   tanh(kh) = 0.99746, so the dispersion relation is deep-water to 0.25%. Stated as a
   quantified approximation, not asserted as equivalent.
3. Air is absent. The paper's test case also disregards the air phase.
4. The solver's artificial sound speed is c = sqrt(GAMMA*BULK/RHO_W) = 12.845 m/s, not
   1481 m/s. `mach_peak` is reported per drop height: 0.019 / 0.057 / 0.094 for
   0.1D / 0.3D / 0.5D on the linear peak-velocity estimate. The largest drop sits at
   the edge of the weak-compressibility assumption and must be reported with that
   number attached.

COUPLING
--------
The sphere is an SDF collider, which is the path validated to 7.3-7.7% of analytic
buoyancy (register; NOT the 1.6-7.7% range, which conflates the free-rigid late-window
fit). The collider is kinematic, so this driver integrates the body itself:

    reset_sdf_force -> step -> sdf_wrench(dt=TICK) -> integrate -> set_sdf_pose

Four of the five documented silent traps are handled here and one is avoided by
construction:
  T1 sdf_wrench divides the accumulated impulse by whatever dt it is handed. Passing
     the substep dt instead of the tick duration inflates the force by exactly
     `substeps`, plausibly. This driver passes `self.dt * self.substeps`.
  T2 The engine never zeroes param.force on the SDF path, so a naive read is the
     run-to-date total. `reset_sdf_force` is called immediately before every step.
  T3 Quaternion order is xyzw for add_sdf_collider. Not exercised: no rotation.
  T4 The CoG-offset blocker (RigidBody6DOF raises on a non-zero COM offset because the
     collider rotates about its centre while sdf_wrench reports torque about that same
     centre) CANNOT BITE HERE. Heave is pure translation and this integrator has one
     degree of freedom, so the torque channel is never integrated. The floating sphere
     is precisely the case where that blocker is out of scope.
  T5 periodic_x is never enabled; add_sdf_collider has no guard against it.

Engine constants and API line numbers are those of pinned SHA
544c93dd02cb9c7ead89e1155a62967243244fce.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

# Engine constants, read directly from simulation/validate_coupling_force.py:15-23,
# which reads them from the pinned solver. Do not fork these.
RHO_W = 1000.0
BULK = 1.5e5
ETA = 1.0e-3
G = 9.81
GAMMA = 1.1
FPS = 30.0

# Kramer 2021 test case.
D_SPHERE = 0.300                      # m, READ from the paper
RHO_SPHERE = 500.0                    # kg/m3, DERIVED from half submergence
H0_OVER_D = (0.1, 0.3, 0.5)           # READ from the paper
PUBLISHED_UNCERTAINTY_PCT = 0.3       # READ: ~0.3% of drop height, 95% confidence

# Every (lim, n_grid) this scene is intended to be run at, in one place so a check
# cannot quietly evaluate itself against a friendlier subset. The 2.0 m domain is what
# forced FLOOR/WALL up: at n_grid 96 it needs 3dx = 0.0625 and 4dx = 0.0833, which the
# original 0.060 / 0.080 did not clear, and the first version of the guard test hid that
# by hardcoding the coarsest dx as 1.5/80.
PLANNED_CONFIGS = ((1.2, 64), (1.2, 80), (1.5, 80), (2.0, 96))

PROVENANCE = {
    "benchmark_doi": "10.3390/en14020269",
    "benchmark_oa": "gold, cc-by, verified via Unpaywall 2026-08-16",
    "testcase_source": "scite full-text excerpts of the OA article, 2026-08-16",
    "testcase_read": "D=300mm; half submergence; H0={0.1D,0.3D,0.5D}; basin 13.00x8.44m; depth 900mm; ~0.3% expanded uncertainty at 95%",
    "testcase_derived": "m=rho_w*V/2=7.0686 kg and rho_sphere=500 kg/m3 follow from half submergence; Table 1 itself was NOT readable from this host",
    "pinned_sha": "544c93dd02cb9c7ead89e1155a62967243244fce",
    "sdf_api": "core/solver.py:324 add_sdf_collider, :339 set_sdf_pose, :348 reset_sdf_force, :354 sdf_wrench",
    "wrench_sign": "core/solver.py:305-307 a static cup of m kg reads (0,0,-m*g), so buoyancy on a submerged collider is +z",
    "sdf_impulse": "kernels/mpm_solver_warp.py:2731-2734 impulse = m*(v_free - v_new), accumulated before the node velocity is overwritten",
    "sdf_band_guard": "add_sdf_collider defaults band=dx and REFUSES the collider unless the minimum stored SDF on the grid's six faces exceeds it (mpm_solver_warp.py:2634-2645)",
    "sdf_cell": "build_sdf sets cell = span/(res-1-2*margin) (mesh_sdf.py:346)",
    "gravity": "core/solver.py:167-169 hardcodes g=[0,0,-9.81]",
    "eos": "kernels/mpm_utils.py:43 pressure = -bulk*(J**-1.1 - 1), gamma=1.1",
    "coupling_path": "SDF collider, the path validated to 7.3-7.7% of analytic buoyancy; NOT the free-rigid material-8 path",
}


# --------------------------------------------------------------------------------------
# analytic reference quantities
# --------------------------------------------------------------------------------------
def sound_speed(bulk=BULK, rho=RHO_W):
    return math.sqrt(GAMMA * bulk / rho)


def substeps_and_dt(dx, eta=ETA, rho=RHO_W, bulk=BULK, fps=FPS):
    """Identical form to validate_coupling_force.py:49-56. Not re-tuned."""
    c = sound_speed(bulk, rho)
    rate = max(c / (0.28 * dx), 6.0 * eta / (rho * dx * dx), 1.0e-6 / (0.5 * dx))
    substeps = int(math.ceil(rate / fps))
    return substeps, (1.0 / fps) / substeps


def sphere_reference(d=D_SPHERE, rho_w=RHO_W, g=G, added_mass_ratio=0.5):
    """Closed-form heave quantities for a half-submerged sphere.

    `added_mass_ratio` is a33 / m_displaced. 0.5 is the conventional value for a
    half-immersed sphere near its heave natural frequency; it is an ESTIMATE used only
    to predict T_n and to size the run, and is never compared against as truth. The
    measured T_n is what gets compared to the benchmark.
    """
    r = 0.5 * d
    vol = 4.0 / 3.0 * math.pi * r ** 3
    mass = rho_w * vol / 2.0                     # half submergence
    a_wp = math.pi * r ** 2                      # waterplane area at the equator
    k = rho_w * g * a_wp                         # hydrostatic heave stiffness
    a33 = added_mass_ratio * mass
    t_n = 2.0 * math.pi * math.sqrt((mass + a33) / k)
    wavelength = g * t_n ** 2 / (2.0 * math.pi)  # deep water
    return {
        "diameter_m": d,
        "radius_m": r,
        "volume_m3": vol,
        "mass_kg": mass,
        "density_kg_m3": mass / vol,
        "waterplane_area_m2": a_wp,
        "heave_stiffness_N_per_m": k,
        "buoyancy_at_equilibrium_N": rho_w * g * vol / 2.0,
        "added_mass_ratio_assumed": added_mass_ratio,
        "natural_period_s_predicted": t_n,
        "radiated_wavelength_m": wavelength,
        "group_velocity_m_s": g * t_n / (4.0 * math.pi),
        "sound_speed_m_s": sound_speed(),
    }


def deep_water_error(depth, wavelength):
    """1 - tanh(kh). Zero means the depth is indistinguishable from infinite."""
    return 1.0 - math.tanh(2.0 * math.pi * depth / wavelength)


# --------------------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------------------
def sphere_mesh(diameter, n_lat=48, n_lon=96):
    """Watertight UV sphere centred on the ORIGIN, faces wound outward.

    add_sdf_collider stores the field in the BODY frame and queries it as
    body = quat_rotate_inv(quat, x_world - center) (mpm_solver_warp.py:2697-2703), so the
    mesh must be origin-centred and the world placement passed as `center`. build_sdf
    re-fixes the global sign from an interior probe (mesh_sdf.py:356-358) which for a
    sphere is the centroid, so winding is belt-and-braces rather than load-bearing.

    A UV sphere is used instead of trimesh's icosphere because neither Vista venv has
    trimesh and the shared venv must not be mutated.
    """
    r = 0.5 * float(diameter)
    verts = [(0.0, 0.0, +r)]
    for i in range(1, n_lat):
        theta = math.pi * i / n_lat
        st, ct = math.sin(theta), math.cos(theta)
        for j in range(n_lon):
            phi = 2.0 * math.pi * j / n_lon
            verts.append((r * st * math.cos(phi), r * st * math.sin(phi), r * ct))
    verts.append((0.0, 0.0, -r))
    south = len(verts) - 1

    def ring(i, j):          # index of vertex (lat ring i in 1..n_lat-1, lon j)
        return 1 + (i - 1) * n_lon + (j % n_lon)

    faces = []
    for j in range(n_lon):                                   # north cap
        faces.append((0, ring(1, j), ring(1, j + 1)))
    for i in range(1, n_lat - 1):                            # quad bands
        for j in range(n_lon):
            a, b = ring(i, j), ring(i, j + 1)
            c, d = ring(i + 1, j + 1), ring(i + 1, j)
            faces.append((a, d, c))
            faces.append((a, c, b))
    for j in range(n_lon):                                   # south cap
        faces.append((south, ring(n_lat - 1, j + 1), ring(n_lat - 1, j)))

    return np.asarray(verts, dtype=float), np.asarray(faces, dtype=np.int64)


def sdf_margin_cells(span, dx, res, band_safety=2.0):
    """Smallest margin_cells whose SDF-grid margin clears the collider contact band.

    Same derivation as validate_coupling_force.py:138-158, restated for a sphere whose
    bounding span is the diameter. add_sdf_collider REFUSES the collider if the minimum
    stored SDF value on the grid's six faces does not exceed band = dx, because
    near-surface space outside the stored box would then get no constraint. build_sdf
    sets cell = span/(res-1-2*margin), so the margin distance is
    margin*span/(res-1-2*margin); requiring that to reach band_safety*dx and solving for
    margin gives the expression below. Chosen to satisfy the engine's own guard, not
    tuned against any measured value.
    """
    m = band_safety * dx * (res - 1) / (span + 2.0 * band_safety * dx)
    margin = int(math.ceil(m))
    if res - 1 - 2 * margin < 8:
        raise ValueError(
            f"sdf_res={res} too small: margin_cells={margin} needed to clear a band of "
            f"{band_safety}*dx={band_safety * dx:.5f} m leaves only "
            f"{res - 1 - 2 * margin} cells across the mesh. Raise --sdf-res.")
    return margin


def build_sphere_sdf(diameter, dx, res=96, band_safety=2.0):
    """Build the sphere SDF and return (SDFData, provenance dict).

    The provenance dict carries `sdf_radius_rms_err_m`: the SDF of a sphere has a
    closed form, |x| - r, so the builder can be checked against exact truth here in a
    way a vehicle hull can never be. That check is the reason a sphere is the right
    first external benchmark and it costs nothing.
    """
    from warpmpm.geometry import build_sdf

    verts, faces = sphere_mesh(diameter)
    margin = sdf_margin_cells(diameter, dx, res, band_safety)
    sdf = build_sdf(verts, faces, res=res, margin_cells=float(margin))
    vals = np.asarray(sdf.values)
    boundary_min = float(min(vals[0].min(), vals[-1].min(),
                             vals[:, 0, :].min(), vals[:, -1, :].min(),
                             vals[:, :, 0].min(), vals[:, :, -1].min()))

    # exact-SDF residual over the stored grid
    n = vals.shape[0]
    origin = np.asarray(sdf.origin, dtype=float)
    cell = float(sdf.cell)
    idx = np.arange(n) * cell
    gx, gy, gz = np.meshgrid(idx, idx, idx, indexing="ij")
    pts = np.stack([gx, gy, gz], axis=-1) + origin
    exact = np.linalg.norm(pts, axis=-1) - 0.5 * diameter
    resid = vals - exact
    return sdf, {
        "sdf_res": int(res),
        "sdf_margin_cells": margin,
        "sdf_cell_m": cell,
        "sdf_cell_over_dx": cell / dx,
        "sdf_boundary_min_m": boundary_min,
        "sdf_band_m": dx,
        "sdf_band_clearance": boundary_min / dx,
        "sdf_radius_rms_err_m": float(np.sqrt(np.mean(resid ** 2))),
        "sdf_radius_max_err_m": float(np.max(np.abs(resid))),
        "sdf_mesh_verts": int(len(verts)),
        "sdf_mesh_faces": int(len(faces)),
    }


# --------------------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------------------
class SphereTank:
    """Square tank of side `lim`, still water of depth `depth`, one SDF sphere.

    Absolute (not dx-multiple) floor and wall offsets, so the geometry is identical at
    every resolution and a grid-refinement comparison is not silently also a geometry
    change. This is the lesson of the multi-geometry finding that a fixed n_grid across
    different hulls changes both dx AND the realized depth.
    """

    # Absolute, and sized by the COARSEST entry in PLANNED_CONFIGS (lim 2.0 at n_grid 96,
    # dx = 0.020833), which needs floor >= 0.0625 and wall >= 0.0833. Checked over the
    # whole of PLANNED_CONFIGS by test_floor_wall_guard.
    FLOOR = 0.075      # m
    WALL = 0.100       # m

    def __init__(self, n_grid, lim, depth, h0_over_d=0.1, diameter=D_SPHERE,
                 rho_sphere=RHO_SPHERE, seed=0, device="auto", sdf_res=96,
                 sdf_band_safety=2.0, free=True):
        from warpmpm.core.solver import GridConfig, Solver
        from warpmpm.materials import newtonian

        self.n_grid = int(n_grid)
        self.lim = float(lim)
        self.dx = self.lim / self.n_grid
        self.h = self.dx / 2.0
        self.free = bool(free)
        self.diameter = float(diameter)
        self.radius = 0.5 * self.diameter
        self.depth = float(depth)

        if self.FLOOR < 3.0 * self.dx or self.WALL < 4.0 * self.dx:
            raise ValueError(
                f"dx={self.dx:.5f} m is too coarse for the fixed FLOOR={self.FLOOR} / "
                f"WALL={self.WALL} offsets (need >=3dx and >=4dx). Raise --n-grid or "
                f"lower --lim.")

        self.ref = sphere_reference(self.diameter)
        # Mass is set from the DENSITY, and cross-checked against the independent
        # half-submergence route (m = rho_w*V/2). They agree only because
        # rho_sphere = rho_w/2 exactly; if a future run perturbs either, this raises
        # rather than silently simulating a sphere that no longer matches the benchmark.
        self.mass = float(rho_sphere) * self.ref["volume_m3"]
        if abs(self.mass - self.ref["mass_kg"]) > 1e-9:
            raise ValueError(
                f"rho_sphere={rho_sphere} gives m={self.mass:.6f} kg but half "
                f"submergence requires {self.ref['mass_kg']:.6f} kg. The Kramer test "
                f"case is defined by half submergence; change both or neither.")

        self.surface_z = self.FLOOR + self.depth
        self.h0 = h0_over_d * self.diameter
        self.z0 = self.surface_z + self.h0          # centre height at release
        self.center_xy = (0.5 * self.lim, 0.5 * self.lim)

        # --- water lattice, jittered, with the sphere's release pose carved out
        rng = np.random.default_rng(seed)
        span_lo, span_hi = self.WALL, self.lim - self.WALL
        n_lat = int(round((span_hi - span_lo) / self.h))
        n_z = int(round(self.depth / self.h))
        ax = span_lo + (np.arange(n_lat) + 0.5) * self.h
        az = self.FLOOR + (np.arange(n_z) + 0.5) * self.h
        gx, gy, gz = np.meshgrid(ax, ax, az, indexing="ij")
        w = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
        w += rng.uniform(-0.2 * self.h, 0.2 * self.h, size=w.shape)

        c0 = np.array([self.center_xy[0], self.center_xy[1], self.z0])
        keep = np.linalg.norm(w - c0, axis=1) > self.radius
        self.n_carved = int((~keep).sum())
        w = w[keep]
        self.n_water = len(w)
        if self.n_water == 0:
            raise ValueError("no water particles survived the carve")

        vol = np.full(self.n_water, self.h ** 3, dtype=np.float32)
        self.substeps, self.dt = substeps_and_dt(self.dx)
        self.tick = self.dt * self.substeps

        s = Solver(grid=GridConfig(n_grid=self.n_grid, grid_lim=self.lim),
                   device=device).load_particles(w.astype(np.float32), vol)
        s.set_material(newtonian(eta=ETA, density=RHO_W, bulk_modulus=BULK))
        s.add_plane((0, 0, self.FLOOR), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
        for pt, nrm in (((self.WALL, 0, 0), (1, 0, 0)),
                        ((self.lim - self.WALL, 0, 0), (-1, 0, 0)),
                        ((0, self.WALL, 0), (0, 1, 0)),
                        ((0, self.lim - self.WALL, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
        s.add_domain_walls()

        sdf, self.sdf_info = build_sphere_sdf(self.diameter, self.dx, res=sdf_res,
                                              band_safety=sdf_band_safety)
        # surface and friction are the engine's own add_sdf_collider defaults and are NOT
        # tuned. For surface_type 2 the impulse is m*(v_free - v_surf - v_tan_scaled)
        # (mpm_solver_warp.py:2731), whose NORMAL part is friction-independent; heave is
        # normal-dominated on a sphere, so friction cannot carry this measurement.
        self.collider = s.add_sdf_collider(sdf, (c0[0], c0[1], self.z0),
                                           velocity=(0.0, 0.0, 0.0),
                                           surface="separable", friction=0.4)
        self.solver = s

        # body state, one degree of freedom
        self.z = float(self.z0)
        self.vz = 0.0

    # --- reporting -------------------------------------------------------------------
    def reflection_return_s(self):
        """When wall-reflected radiated energy first returns to the sphere.

        Uses the deep-water GROUP velocity, which is the speed radiated energy actually
        travels at; using sqrt(g*h) here would understate the clean window by ~3.6x and
        is the wrong wave speed for a 0.94 m wave in 0.5 m of water.
        """
        d_wall = 0.5 * self.lim - self.WALL
        return 2.0 * d_wall / self.ref["group_velocity_m_s"]

    def config(self):
        cg = self.ref["group_velocity_m_s"]
        t_n = self.ref["natural_period_s_predicted"]
        v_peak = self.h0 * 2.0 * math.pi / t_n
        return {
            "n_grid": self.n_grid, "lim_m": self.lim, "dx_m": self.dx, "h_m": self.h,
            "depth_m": self.depth, "surface_z_m": self.surface_z,
            "floor_m": self.FLOOR, "wall_m": self.WALL,
            "h0_m": self.h0, "h0_over_d": self.h0 / self.diameter,
            "z0_m": self.z0, "free": self.free,
            "n_water": self.n_water, "n_carved": self.n_carved,
            "substeps": self.substeps, "dt_substep_s": self.dt, "dt_tick_s": self.tick,
            "sphere_cells_across": self.diameter / self.dx,
            "depth_over_dx": self.depth / self.dx,
            "reflection_return_s": self.reflection_return_s(),
            "reflection_return_periods": self.reflection_return_s() / t_n,
            "deep_water_error": deep_water_error(self.depth, self.ref["radiated_wavelength_m"]),
            "peak_velocity_estimate_m_s": v_peak,
            "mach_peak": v_peak / self.ref["sound_speed_m_s"],
            "group_velocity_m_s": cg,
            **{f"ref_{k}": v for k, v in self.ref.items()},
            **self.sdf_info,
        }

    # --- integration ------------------------------------------------------------------
    def advance(self):
        """One frame. Returns the record for this tick.

        Order matters and is the documented contract: reset the accumulator, step, read
        the wrench over the TICK duration, integrate, then post the new pose for the
        next tick's start.
        """
        self.solver.reset_sdf_force(self.collider)          # T2
        self.solver.step(self.dt, self.substeps)
        w = self.solver.sdf_wrench(self.collider, self.tick)  # T1: tick, not substep
        fz = float(np.asarray(w["force"], dtype=float)[2])

        az = fz / self.mass - G
        if self.free:
            # semi-implicit (symplectic) Euler: velocity first, then position
            self.vz += az * self.tick
            self.z += self.vz * self.tick
            self.solver.set_sdf_pose(self.collider,
                                     center=(self.center_xy[0], self.center_xy[1], self.z),
                                     velocity=(0.0, 0.0, self.vz))
        return {
            "z_m": self.z,
            "vz_m_s": self.vz,
            "fz_N": fz,
            "az_m_s2": az,
            "heave_m": self.z - self.surface_z,
            "net_N": fz - self.mass * G,
        }


# --------------------------------------------------------------------------------------
def run(args):
    tank = SphereTank(n_grid=args.n_grid, lim=args.lim, depth=args.depth,
                      h0_over_d=args.h0_over_d, seed=args.seed, device=args.device,
                      sdf_res=args.sdf_res, free=not args.fixed)
    cfg = tank.config()
    cfg["mode"] = "fixed" if args.fixed else "free"
    cfg["seed"] = args.seed
    print(json.dumps(cfg, indent=2, sort_keys=True), flush=True)

    if args.fixed:
        # Hydrostatic control: the sphere is pinned at the requested pose and the
        # steady vertical reaction is compared to the analytic buoyancy of the
        # submerged cap. At h0=0 that is exactly rho*g*V/2 = 69.343 N. This is the
        # sphere-scale analogue of the C1-SDF check that gave 7.3-7.7% on the box.
        sub = tank.surface_z - (tank.z - tank.radius)
        sub = min(max(sub, 0.0), tank.diameter)
        cap_v = math.pi * sub ** 2 * (3.0 * tank.radius - sub) / 3.0
        cfg["analytic_submerged_volume_m3"] = cap_v
        cfg["analytic_buoyancy_N"] = RHO_W * G * cap_v

    rows = []
    for i in range(args.frames):
        rec = tank.advance()
        rec["frame"] = i
        rec["t_s"] = (i + 1) * tank.tick
        rows.append(rec)
        if args.verbose and i % max(1, args.frames // 40) == 0:
            print(f"  f{i:4d} t={rec['t_s']:7.4f}  z={rec['z_m']:9.6f}  "
                  f"heave={rec['heave_m']:+9.6f}  Fz={rec['fz_N']:10.4f}  "
                  f"net={rec['net_N']:+10.4f}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"config": cfg, "provenance": PROVENANCE, "rows": rows}
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"wrote {out} ({len(rows)} frames)", flush=True)


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--n-grid", type=int, default=64)
    p.add_argument("--lim", type=float, default=1.2, help="tank side, m")
    p.add_argument("--depth", type=float, default=0.5, help="still-water depth, m")
    p.add_argument("--h0-over-d", type=float, default=0.1, choices=None,
                   help="drop height as a multiple of D; the benchmark uses 0.1/0.3/0.5")
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--fixed", action="store_true",
                   help="pin the sphere and measure the steady reaction (hydrostatic control)")
    p.add_argument("--sdf-res", type=int, default=96)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="auto")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--out", default="sphere_heave.json")
    run(p.parse_args())


if __name__ == "__main__":
    main()
