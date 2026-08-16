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

Test case READ from Table 1 of the article PDF (p.4), held outside the repo at
/Users/josie/can-it-ford-refs/2026-08-16/, sha256 0d885109...4e9354. See the constants
block below. The earlier version of this file derived the test case from the abstract
plus a half-submergence argument, and THREE of those values were wrong:

    quantity   assumed here   Table 1    consequence
    rho_w      1000 kg/m3     998.2      buoyancy and stiffness both 0.18% high
    m          7.0686 kg      7.056      the mass followed the wrong rho_w
    g          9.81 (engine)  9.82       IRREDUCIBLE, see GRAVITY_BIAS_FRACTION

The derivation method was sound: 998.2 * V/2 = 7.0559 kg reproduces Table 1's 7.056 to
the quoted precision, so half submergence really does fix the mass. The input was wrong,
not the reasoning. This is why a derived value is not a read one even when the algebra
is right.

Table 1 also gives CoG = (0, 0, -34.8) mm, i.e. the sphere is BALLASTED and its centre
of gravity sits 34.8 mm below the geometric centre. In a 1-DOF heave integration that is
immaterial, which is a second and independent reason the sphere is the right first
benchmark for this engine: see trap T4 below.

The PDF is the paper, NOT the benchmark time series. The raw decay series ships as MDPI
Supplementary Materials at /s1, which is 403 from this host and independently reproduced
as blocked by the Round-5 coordinator.

WHAT IS DELIBERATELY DIFFERENT FROM THE EXPERIMENT, AND WHY
-----------------------------------------------------------
1. Basin size. 13.00 x 8.44 m cannot be resolved at the dx a 300 mm sphere needs. The
   domain here is a square tank of side `lim`, so wall reflections truncate the
   comparison window.

   CORRECTED 2026-08-16 after an adversarial review, and this changed a scene-sizing
   decision, not just a sentence. An earlier version of this file used the deep-water
   GROUP velocity on the argument that radiated ENERGY travels at c_g. Kramer 2021
   section 3.5, p.16, uses the PHASE celerity for exactly this purpose and says why,
   verbatim: "This can be considered a conservative estimate, as the main wave front of
   radiated waves would have propagated with the group velocity rather than the phase
   velocity." So the benchmark deliberately picks the FASTER, more conservative speed,
   and the group-velocity choice was the less conservative one dressed as the more
   physical one. `reflection_return_s` now defaults to Kramer's convention and
   `reflection_windows()` reports all three so the choice is visible rather than
   embedded:

       c_group   = g*T/(4*pi) = 0.6065 m/s   least conservative
       c_phase   = g*T/(2*pi) = 1.2131 m/s   KRAMER'S OWN CHOICE, the default here
       sqrt(g*h)              = 2.2147 m/s   fastest possible component, hardest bound

   The practical cost of the correction: at lim = 1.2 the clean window is 1.06 natural
   periods on Kramer's convention, not the 2.12 previously claimed on the group
   convention, and only 0.58 on the sqrt(g*h) bound. Two clean periods on Kramer's
   convention needs lim >= 2.085 m, which is why PLANNED_CONFIGS now carries 2.2.
2. Water depth. 900 mm is reduced to `depth`. At 500 mm, kh = 3.333 and
   tanh(kh) = 0.99746, so the dispersion relation is deep-water to 0.25%. Stated as a
   quantified approximation, not asserted as equivalent.
3. Air is absent. The paper's test case also disregards the air phase.
4. The solver's artificial sound speed is c = sqrt(GAMMA*BULK/RHO_W_BENCHMARK) = 12.8568 m/s, not
   1481 m/s. `mach_peak` is reported per drop height: 0.019 / 0.057 / 0.094 for
   0.1D / 0.3D / 0.5D on the linear peak-velocity estimate. The largest drop sits at
   the edge of the weak-compressibility assumption and must be reported with that
   number attached.

COUPLING
--------
The sphere is an SDF collider, which is the path validated to 7.3-7.7% of analytic
buoyancy (register; NOT the 1.6-7.7% range, which conflates the free-rigid late-window
fit).

REGISTER J.1 CAVEAT, added 2026-08-16 after an adversarial review found it missing from
every R5 document while two of them leaned on the 7.3-7.7% figure as a warrant. That
validation DOES NOT CLEAR THE 17 CANONICAL RUNS, for three recorded reasons: the 17 runs
use restitution 0.05 on floor and walls where C1 used 0.0 everywhere; they resolve depth
at 2 grid cells; and self-consistency is not validation. Citing the SDF path as
"validated" is a statement about the C1-SDF box scene only. It is precisely because that
warrant is so narrow that an external benchmark is worth building, so quoting it without
the caveat would undercut this file's own reason for existing.

A further qualification measured this session, see docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md:
the 7.3-7.7% range is NOT one uniform band. At g96 the residual drift is 0.07x the error
being claimed; at g64 it is 0.57x, and on the actually-published back-half window it is
1.18x, i.e. the drift exceeds the error. Quote the grids separately.

The collider is kinematic, so this driver integrates the body itself:

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
RHO_W = 1000.0        # the project's canonical water density, NOT the benchmark's
BULK = 1.5e5
ETA = 1.0e-3
G_ENGINE = 9.81       # hardcoded at core/solver.py:167-169 and NOT overridable
GAMMA = 1.1
FPS = 30.0

# --------------------------------------------------------------------------------------
# Kramer 2021 Table 1, READ from the article PDF (p.4, "Values of the test case physical
# parameters"), sha256 0d885109119d390ae30d42c620ddf0bd8bcad130396dcfe8053b67510d4e9354.
# Every one of these was previously DERIVED or assumed here and three of them were wrong.
# --------------------------------------------------------------------------------------
D_SPHERE = 0.300                      # m       Table 1 D = 300 mm
M_SPHERE = 7.056                      # kg      Table 1 m = 7.056 kg   (was derived 7.0686)
COG_M = (0.0, 0.0, -0.0348)           # m       Table 1 CoG = (0, 0, -34.8) mm
G_BENCHMARK = 9.82                    # m/s2    Table 1 g = 9.82       (engine has 9.81)
H0_M = (0.030, 0.090, 0.150)          # m       Table 1 H0 = {30 90 150} mm
RHO_W_BENCHMARK = 998.2               # kg/m3   Table 1 rho_w = 998.2  (was assumed 1000)
SEABED_DEPTH_M = 0.900                # m       Table 1 d = 900 mm, and section 1.1 d = 3D
N_REPEATS_PUBLISHED = 4               # "Four repetitions were carried out for each drop height"

H0_OVER_D = tuple(h / D_SPHERE for h in H0_M)   # exactly (0.1, 0.3, 0.5)

# THE UNCERTAINTY IS NOT A BLANKET RELATIVE TOLERANCE. Verbatim from the abstract:
# "At a 95% confidence level, uncertainties were found to be very low - on average only
# about 0.3% of the respective drop heights." So it is (a) an AVERAGE over the decay
# series, not a per-sample bound, (b) at 95% confidence, and (c) a fraction of the DROP
# HEIGHT, which makes it an ABSOLUTE DISPLACEMENT tolerance of 0.09 / 0.27 / 0.45 mm for
# the three drops. It cannot be applied to a period, a damping ratio or a force. Both the
# Round-5 bootstrap and RECONCILE_ROUND4 paraphrase it as a flat 0.3%; do not inherit that.
UNCERTAINTY_FRACTION_OF_DROP = 0.003
UNCERTAINTY_IS_AVERAGE_AT_95PCT = True


def published_displacement_tolerance_m(h0):
    """The benchmark's stated tolerance, in metres, for a given drop height."""
    return UNCERTAINTY_FRACTION_OF_DROP * float(h0)


# THE GRAVITY MISMATCH IS IRREDUCIBLE. The benchmark's local g is 9.82 m/s2; the solver
# hardcodes 9.81 inside Solver.set_material() and newtonian() carries no g key to
# override it, so this scene CANNOT be run at the benchmark's gravity. The bias is
# +0.102% in g. Both the weight and the hydrostatic stiffness scale with g, so the
# equilibrium draft is unaffected and only the period moves, as T ~ 1/sqrt(g): -0.051%,
# about -0.0004 s on a 0.777 s period. That is roughly an order of magnitude below the
# benchmark's own displacement tolerance, so it is a stated systematic, not the limiting
# error. It must still travel with every period reported from this scene.
GRAVITY_BIAS_FRACTION = (G_ENGINE - G_BENCHMARK) / G_BENCHMARK

PLANNED_CONFIGS_DOC = "see PLANNED_CONFIGS below"

# Every (lim, n_grid) this scene is intended to be run at, in one place so a check
# cannot quietly evaluate itself against a friendlier subset. The 2.0 m domain is what
# forced FLOOR/WALL up: at n_grid 96 it needs 3dx = 0.0625 and 4dx = 0.0833, which the
# original 0.060 / 0.080 did not clear, and the first version of the guard test hid that
# by hardcoding the coarsest dx as 1.5/80.
PLANNED_CONFIGS = ((1.2, 64), (1.5, 80), (2.0, 107), (2.2, 117))

PROVENANCE = {
    "benchmark_doi": "10.3390/en14020269",
    "benchmark_oa": "gold, cc-by, verified via Unpaywall 2026-08-16",
    "testcase_source": "Table 1, p.4 of the article PDF at /Users/josie/can-it-ford-refs/2026-08-16/, sha256 0d885109119d390ae30d42c620ddf0bd8bcad130396dcfe8053b67510d4e9354",
    "testcase_read": "D=300mm; m=7.056kg; CoG=(0,0,-34.8)mm; g=9.82; H0={30,90,150}mm; rho_w=998.2; d=900mm; 4 repetitions per drop height",
    "testcase_superseded": "an earlier version of this file DERIVED m=7.0686 kg and rho=500 kg/m3 assuming rho_w=1000; Table 1 gives rho_w=998.2 and m=7.056, so all three were wrong. The half-submergence reasoning was correct; its input was not.",
    "uncertainty_semantics": "0.3% is an AVERAGE at 95% confidence expressed as a fraction of DROP HEIGHT, i.e. 0.09/0.27/0.45 mm absolute. NOT a blanket relative tolerance and NOT applicable to a period, damping ratio or force.",
    "gravity_irreducible": "benchmark g=9.82, engine hardcodes 9.81 at core/solver.py:167-169 with no override; +0.102% in g, -0.051% in period, equilibrium draft unaffected",
    "pdf_route": "only https://backend.orbit.dtu.dk/ws/portalfiles/portal/238040494/ serves it. MDPI article/pdf/s1 403, orbit.dtu.dk front end 403, vbn.aau.dk files 403 to curl, hdl.handle.net 404, research-hub.nrel.gov DNS failure. 'DTU is blocked' is wrong: the FRONT END is blocked and the Pure BACKEND is not.",
    "timeseries_blocked": "the raw decay series is MDPI Supplementary Materials at /s1, 403 from this host, independently reproduced by the Round-5 coordinator",
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
def sound_speed(bulk=BULK, rho=RHO_W_BENCHMARK):
    return math.sqrt(GAMMA * bulk / rho)


def substeps_and_dt(dx, eta=ETA, rho=RHO_W_BENCHMARK, bulk=BULK, fps=FPS):
    """Identical form to validate_coupling_force.py:49-56. Not re-tuned."""
    c = sound_speed(bulk, rho)
    rate = max(c / (0.28 * dx), 6.0 * eta / (rho * dx * dx), 1.0e-6 / (0.5 * dx))
    substeps = int(math.ceil(rate / fps))
    return substeps, (1.0 / fps) / substeps


def sphere_reference(d=D_SPHERE, rho_w=RHO_W_BENCHMARK, g=G_ENGINE, mass=M_SPHERE,
                     added_mass_ratio=0.5):
    """Closed-form heave quantities for the Kramer sphere.

    `mass` defaults to Table 1's READ value, not to a half-submergence derivation.
    `mass_from_half_submergence_kg` is returned alongside it so the two routes stay
    visible and any future drift between them is legible rather than silent.

    `g` defaults to the ENGINE's 9.81, because that is what the simulation will actually
    run at and this dict is used to size and interpret the run. The benchmark's own 9.82
    is carried in the same dict as `natural_period_s_at_benchmark_g` so the two are never
    confused. Both weight and stiffness scale with g, so the equilibrium draft is
    identical and only the period moves.

    `added_mass_ratio` is a33 / m. 0.5 is the conventional value for a half-immersed
    sphere near its heave natural frequency; it is an ESTIMATE used only to predict T_n
    and to size the run, and is never compared against as truth. The measured T_n is what
    gets compared to the benchmark.
    """
    r = 0.5 * d
    vol = 4.0 / 3.0 * math.pi * r ** 3
    m_half = rho_w * vol / 2.0                   # the independent half-submergence route
    a_wp = math.pi * r ** 2                      # waterplane area at the equator
    k = rho_w * g * a_wp                         # hydrostatic heave stiffness
    a33 = added_mass_ratio * mass
    t_n = 2.0 * math.pi * math.sqrt((mass + a33) / k)
    k_bench = rho_w * G_BENCHMARK * a_wp
    t_n_bench = 2.0 * math.pi * math.sqrt((mass + a33) / k_bench)
    wavelength = g * t_n ** 2 / (2.0 * math.pi)  # deep water
    return {
        "diameter_m": d,
        "radius_m": r,
        "volume_m3": vol,
        "mass_kg": mass,
        "mass_from_half_submergence_kg": m_half,
        "mass_route_disagreement_kg": mass - m_half,
        "density_kg_m3": mass / vol,
        "water_density_kg_m3": rho_w,
        "gravity_used_m_s2": g,
        "gravity_benchmark_m_s2": G_BENCHMARK,
        "waterplane_area_m2": a_wp,
        "heave_stiffness_N_per_m": k,
        "buoyancy_at_equilibrium_N": rho_w * g * vol / 2.0,
        "weight_N": mass * g,
        "added_mass_ratio_assumed": added_mass_ratio,
        "natural_period_s_predicted": t_n,
        "natural_period_s_at_benchmark_g": t_n_bench,
        "natural_period_gravity_bias_frac": (t_n - t_n_bench) / t_n_bench,
        "radiated_wavelength_m": wavelength,
        "group_velocity_m_s": g * t_n / (4.0 * math.pi),
        "phase_velocity_m_s": g * t_n / (2.0 * math.pi),
        "sound_speed_m_s": sound_speed(),
        # T ~ sqrt(1 + a33/m), so the added-mass ASSUMPTION propagates into the period,
        # the wavelength, both wave speeds and therefore every reflection window. It is
        # not a cosmetic input. Sensitivity is reported so it travels with those numbers
        # instead of sitting silently under them.
        "natural_period_s_at_a33_ratio_0p83": (
            2.0 * math.pi * math.sqrt((mass + 0.83 * mass) / k)),
        "period_sensitivity_note": (
            "a33/m=0.5 is an ESTIMATE, not a source. Raising it to 0.83 lengthens T_n by "
            "about 10 percent and shortens every reflection window in periods by the "
            "same factor. Any reflection figure inherits this."),
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
                 mass=M_SPHERE, seed=0, device="auto", sdf_res=96,
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

        self.ref = sphere_reference(self.diameter, mass=float(mass))
        # Mass is Table 1's READ value. It is cross-checked against the INDEPENDENT
        # half-submergence route rho_w*V/2, which is how it was (wrongly) derived before
        # the PDF was in hand. The two agree to 1.5e-4 kg, which is Table 1's own
        # rounding to three decimals; a wider gap means someone has changed rho_w, D or m
        # without changing the others, and the sphere is no longer the benchmark's.
        self.mass = float(mass)
        gap = abs(self.mass - self.ref["mass_from_half_submergence_kg"])
        if gap > 1.0e-3:
            raise ValueError(
                f"m={self.mass:.6f} kg disagrees with half submergence at rho_w="
                f"{RHO_W_BENCHMARK} ({self.ref['mass_from_half_submergence_kg']:.6f} kg) "
                f"by {gap:.6f} kg, beyond Table 1's 1e-3 kg rounding. The Kramer sphere "
                f"is DEFINED as floating with the waterline at the equator; changing one "
                f"of m, D or rho_w without the others makes this a different experiment.")

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
        s.set_material(newtonian(eta=ETA, density=RHO_W_BENCHMARK, bulk_modulus=BULK))
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
    def reflection_windows(self):
        """Round-trip time to the nearest wall under all three defensible wave speeds.

        CORRECTED 2026-08-16. The earlier version used the deep-water GROUP velocity and
        argued that radiated ENERGY travels at c_g, dismissing sqrt(g*h) as the wrong
        speed. Kramer 2021 section 3.5, p.16, does the same calculation with the PHASE
        celerity and states the reason: "This can be considered a conservative estimate,
        as the main wave front of radiated waves would have propagated with the group
        velocity rather than the phase velocity." The benchmark deliberately takes the
        FASTER speed because it bounds contamination earlier. Choosing c_g gave a window
        exactly 2x longer than the benchmark's own convention would allow, which is the
        least conservative of the three options presented as the most physical.

        All three are returned. `kramer_phase` is the one to quote.
        """
        d_wall = 0.5 * self.lim - self.WALL
        c_g = self.ref["group_velocity_m_s"]
        c_p = self.ref["phase_velocity_m_s"]
        c_sh = math.sqrt(G_ENGINE * self.depth)
        t_n = self.ref["natural_period_s_predicted"]
        out = {}
        for name, c in (("group", c_g), ("kramer_phase", c_p), ("shallow_bound", c_sh)):
            t = 2.0 * d_wall / c
            out[f"reflect_{name}_s"] = t
            out[f"reflect_{name}_periods"] = t / t_n
            out[f"c_{name}_m_s"] = c
        out["wall_distance_m"] = d_wall
        return out

    def reflection_return_s(self):
        """Kramer's own convention: deep-water PHASE celerity. See reflection_windows."""
        return self.reflection_windows()["reflect_kramer_phase_s"]

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
            **self.reflection_windows(),
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

        az = fz / self.mass - G_ENGINE
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
            "net_N": fz - self.mass * G_ENGINE,
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
        cfg["analytic_buoyancy_N"] = RHO_W_BENCHMARK * G_ENGINE * cap_v

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
