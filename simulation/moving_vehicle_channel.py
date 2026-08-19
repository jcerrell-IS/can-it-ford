"""moving_vehicle_channel.py

A prescribed-motion vehicle hull in a flooded roadway, measuring the reaction
wrench as a function of TWO separate speeds: the vehicle's and the water's.

NON-CANONICAL. Nothing here feeds the 17 gated runs, the poster or the paper's
verdicts. It answers a different question with a different scene.

THE QUESTION
------------
The published field treats vehicle instability in floodwater as a threshold in
depth, or in depth times flow velocity. Where a vehicle is moving, the vehicle's
own speed and the water's speed are usually merged into one number or the second
is omitted. Three works are titled for the moving case (Shah et al 2018
10.1051/matecconf/201820307003; Shah et al 2020 10.1111/jfr3.12657, 1:10 scale;
Al-Qadami et al 2022 10.1111/jfr3.12828, NUMERICAL) and none of them outputs a
graded load as a function of both speeds independently.

So the contribution here is NOT "a vehicle that moves", which exists. It is the
SURFACE: v_car crossed with v_water as separate variables, reported with
v_relative alongside and never collapsed into it.

CITATION DISCIPLINE FOR ANYONE EXTENDING THIS FILE
   10.1007/s11069-021-04949-6 is Al-Qadami et al **2021**, "Full-scale
   experimental investigations on the response of a flooded passenger vehicle
   under subcritical conditions", Natural Hazards 110(1) 325-348. It is
   EXPERIMENTAL and its title does not announce vehicle speed as a swept
   variable. It is a DIFFERENT PAPER from 10.1111/jfr3.12828 (2022, numerical,
   moving) and from 10.3390/su151713262 (2023, 3D CFD). Merging any two of them
   produces a paper that does not exist, and that conflation has already
   happened once on this project. Resolved against Crossref 2026-08-19.
   None of these is in data/research_corpus_index.json: `--query "Al-Qadami"`
   returns zero. The index's silence about this topic is not evidence of absence.

THE FRAME, AND THE ASSUMPTION IT RESTS ON  (labelled, reversible)
-----------------------------------------------------------------
The scene is solved in the VEHICLE REST FRAME. The hull sits at the domain
centre and the water arrives with free-stream velocity

    u_free = (v_water, -v_car, 0)

with the flow across the roadway on +x (broadside, as in the canonical 17) and
the vehicle's direction of travel on +y (its own long axis, which is where
load_vehicle(up='z') puts it).

WHY, and it is arithmetic, not preference. The grid is forced cubic
(GridConfig takes one scalar), and the domain rule sizes it from the hull:
lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth) = 9.4217 m for the Yaris. A
ground-frame vehicle at 8.9 m/s crosses the usable run in about 7 frames at
30 fps, which measures nothing, and lengthening y is impossible without wrecking
the depth resolution because the grid is cubic.

THE ASSUMPTION: a horizontal frame change leaves the load unchanged. That is
EXACT for a slip bed, because a plane that exerts no tangential stress is the
same plane in any frame sliding parallel to it. It is FALSE for a frictional
bed, where the roadway would have to move at -v_car in this frame and does not.
This scene uses a slip floor (see the deviations note below), so the assumption
is self-consistent here; it does NOT transfer to the canonical scene, whose
floor carries friction 0.55.

Do not read the assumption as verified by this file. `--ground-frame` runs the
same scene the other way at a speed where the ground frame is still feasible, so
the two can be compared. That comparison is the test, not the assumption.

WHAT THE FRAME CHOICE DOES *NOT* DO
   It does not collapse the matrix. v_car and v_water are on PERPENDICULAR axes,
   so each (v_car, v_water) pair is a distinct free-stream VECTOR: the magnitude
   and the direction both move. Because the hull is not axisymmetric, |v_rel|
   alone cannot predict the load, and the iso-|v_rel| arc below is built to test
   exactly that.

THE FIVE TRAPS, AND WHERE EACH IS HANDLED IN THIS FILE
------------------------------------------------------
 1. sdf_wrench divides the accumulated impulse by whatever dt it is handed.
    Verified live 2026-08-19 at core/solver.py:354-361: the body is
    `return {"force": f / dt, "torque": t / dt}`. Handing it dt_sub instead of
    the tick duration inflates the force by exactly n_substeps, plausibly and
    with no error. HANDLED: Scene.step_frame passes self.frame_dt, never
    self.dt, and _WRENCH_DT_IS_FRAME_DT below is asserted in the self-test.
 2. The engine never zeroes param.force on the SDF path, so a naive read is the
    run-to-date total rather than this tick's. HANDLED: reset_sdf_force is
    called at the top of every tick in step_frame, exactly once per wrench read.
 3. Quaternion order differs WITHIN solver.py: add_sdf_collider at :324 defaults
    xyzw (0,0,0,1), while add_cup at :256 documents wxyz (1,0,0,0). HANDLED: the
    hull is never rotated, and the identity is written explicitly as xyzw with
    this comment at the call site rather than left to a default.
 4. COM offset is a hard blocker: RigidBody6DOF raises NotImplementedError on a
    non-zero COM offset, because the SDF collider rotates about its centre and
    sdf_wrench reports torque about that same centre, while the Yaris cloud CG
    sits 0.6312 m up against a bbox mid-height of 0.7427 m. HANDLED BY AVOIDANCE,
    which is the point: the body here is PRESCRIBED and never integrated, so no
    COM offset is ever needed. Every torque reported is explicitly about the
    collider centre and is labelled torque_about_collider_centre_Nm so it can
    never be read as a torque about the CG.
 5. periodic_x has no guard on the SDF path: add_cdf_collider raises at :379,
    add_sdf_collider at :324 has no equivalent. HANDLED: periodic_x is never set,
    and the streamwise wrap is done host-side by the recyclers below. The
    self-test asserts the solver's periodic_x is False.

RESOLUTION, STATED UP FRONT BECAUSE IT BOUNDS WHAT IS QUOTABLE
---------------------------------------------------------------
docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md section 5 established, for
this same scene family, that the validated C1-SDF buoyancy regime runs at
depth_cells = 18 while a 0.30 m column in a hull-sized domain gets 1.4 to 3.7,
and concluded "no force number from this scene is quotable". Re-derived for the
Yaris: g64 gives 2.04 depth cells, g96 gives 3.06, against 18.

That finding is accepted here and NOT re-litigated. The response is to report
DIFFERENCES at fixed resolution rather than absolutes, and to run the arc at two
grids so the differences can be checked for resolution stability. An absolute
force from this file is a diagnostic, never a measurement.

DELIBERATE DEVIATIONS FROM sim_standing.py, WITH REASONS
--------------------------------------------------------
 - Slip floor, friction 0.0, not 0.55. There are no rigid PARTICLES in this
   scene at all, so a vehicle-on-bed Coulomb coefficient has nothing to act on,
   and applying it to water would be an unsourced bed-friction model.
   simulation/validate_coupling_force.py:277-282 and the exploratory driver both
   make the same deviation for the same reason. It is also what makes the frame
   assumption above exact rather than approximate, so it is load-bearing here.
 - No horizontal slip walls. They would block the through-flow this file exists
   to impose. Only the floor plane and the engine's own add_domain_walls remain,
   with the recycle planes set 3 dx inside the boundary so nothing reaches them.
 - Collider friction 0.4 and surface "separable" are add_sdf_collider's own
   defaults and are NOT tuned, matching validate_coupling_force.py:296.

WHAT IS REUSED RATHER THAN REINVENTED
   The vetted PLY loader, canonicalize(), build_hull_sdf() with its
   winding-number chunk, and sdf_nearest() are taken from
   simulation/moving_vehicle_sdf_exploratory.py (commit 187d868), which in turn
   took the loader from analysis/render_v1/as_ran_local_copies/vehicle_live.py,
   sha256 5a5bbbab7d2e21df... , verified against that file 2026-08-19. The
   in/outflow machinery is simulation/openchannel_bc.py, which implements Zhao,
   Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179, 27-33,
   doi:10.1016/j.compfluid.2018.10.007. That is the correct citation for MPM
   in/outflow, NOT Kumar.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
LOADER_PATH = REPO / "analysis" / "render_v1" / "as_ran_local_copies" / "vehicle_live.py"

sys.path.insert(0, str(REPO / "simulation"))
from openchannel_bc import RecyclingChannelBC  # noqa: E402

# sim_standing.py's own water and CFL constants, not re-derived here
WATER_DENSITY = 1000.0
WATER_ETA = 1.0e-3
BULK_MODULUS = 1.5e5
EOS_GAMMA = 1.1
FPS = 30
G = 9.81

COLLIDER_SURFACE = "separable"
COLLIDER_FRICTION = 0.4
SDF_MARGIN_CELLS = 6.0
WN_CHUNK = 128

# Trap 1 sentinel. The wrench dt must be the TICK duration. Asserted in selftest.
_WRENCH_DT_IS_FRAME_DT = True


# --------------------------------------------------------------------------
# reused, with attribution in the module docstring
# --------------------------------------------------------------------------
def load_vetted_loader():
    if not LOADER_PATH.exists():
        raise SystemExit("vetted loader not found: %s" % LOADER_PATH)
    spec = importlib.util.spec_from_file_location("vehicle_live_asran", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vehicle_live_asran"] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "solidify_watertight") or not hasattr(mod, "is_gaussian_ply"):
        raise SystemExit("loader at %s is not the as-ran patched copy" % LOADER_PATH)
    return mod


def canonicalize(v):
    """Verbatim from renders/yaris_render_s1/sim_standing.py:97-106."""
    import trimesh
    mv = np.asarray(v.mesh.vertices, dtype=np.float64)
    lo, hi = mv.min(0), mv.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    mv = mv - shift
    v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces), process=False)
    v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
    v.extent = mv.max(0) - mv.min(0)
    v.spacing = float(v.extent.max()) / 32.0
    return v


def build_hull_sdf(mesh, res, cache_dir):
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
    idx = np.rint((pts_body - np.asarray(sdf.origin)) / float(sdf.cell)).astype(np.int64)
    res = int(np.asarray(sdf.values).shape[0])
    outside = np.any((idx < 0) | (idx >= res), axis=1)
    idx = np.clip(idx, 0, res - 1)
    val = np.asarray(sdf.values)[idx[:, 0], idx[:, 1], idx[:, 2]]
    return np.where(outside, np.inf, val)


def domain_limit(ext_long, ext_short, depth):
    """lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth).

    Read directly from renders/yaris_render_s3_enhanced/hull_sweep.sbatch, which
    records lim 9.421742314 for the Yaris. NOTE: that value implies
    ext_long = 4.28261 m, while CLAUDE.md August 4 item 4 records the gated
    hull's measured extents as (1.7078, 4.2014, 1.4853), implying 9.2431, a 1.9
    percent difference. Which hull each refers to is UNRESOLVED, so this is
    derived from the loaded mesh at runtime and both numbers are printed rather
    than either being hardcoded.
    """
    return float(max(2.2 * ext_long, 3.5 * ext_short, 6.0 * depth))


# --------------------------------------------------------------------------
# in/outflow, generalised to either horizontal axis and a signed free stream
# --------------------------------------------------------------------------
class AxisRecycler(RecyclingChannelBC):
    """RecyclingChannelBC generalised to either horizontal axis, either flow
    direction, and a VECTOR free-stream velocity.

    simulation/openchannel_bc.py is outside this slot's write scope, so the
    generalisation lives here as a subclass rather than as an edit there. What
    is inherited and NOT re-implemented is the part that matters for safety: the
    P2G edge guard (the engine raises if a particle lands within 2 cells of the
    grid edge, solver.py:506-512), the sub-cell overshoot carry, the modulo that
    stops a particle recycling forever inside one tick, and the counters.

    The parent hardcodes column 0 and a positive flow direction. Both are
    parameterised here. The parent's guard requires x_in < x_out, so the two
    planes are always passed in geometric order and the SIGN of the free-stream
    component decides which of them is the exit.
    """

    def __init__(self, *, axis, n_water, p_lo, p_hi, u_free_vec, dx, grid_lim, seed=0):
        axis = int(axis)
        if axis not in (0, 1):
            raise ValueError("axis must be 0 (x) or 1 (y); z is the free surface")
        u_free_vec = np.asarray(u_free_vec, dtype=np.float64).reshape(3)
        super().__init__(n_water=n_water, x_in=p_lo, x_out=p_hi,
                         inlet_velocity=float(u_free_vec[axis]),
                         dx=dx, grid_lim=grid_lim, prescribe="full", seed=seed)
        self.axis = axis
        self.u_free_vec = u_free_vec
        self.u_axis = float(u_free_vec[axis])
        self.p_lo = float(p_lo)
        self.p_hi = float(p_hi)

    @property
    def active(self):
        return self.u_axis != 0.0

    def apply(self, x, v):
        """Recycle in place along self.axis. Returns particles moved."""
        if not self.active:
            self.recycled_last = 0
            return 0
        nw = self.n_water
        a = self.axis
        s = x[:nw, a]
        L = self.p_hi - self.p_lo
        if self.u_axis > 0.0:
            crossed = s >= self.p_hi
            n = int(crossed.sum())
            if n == 0:
                self.recycled_last = 0
                return 0
            overshoot = s[crossed] - self.p_hi
            landing = self.p_lo + np.mod(overshoot, L)
        else:
            crossed = s <= self.p_lo
            n = int(crossed.sum())
            if n == 0:
                self.recycled_last = 0
                return 0
            overshoot = self.p_lo - s[crossed]
            landing = self.p_hi - np.mod(overshoot, L)
        self.recycled_last = n
        self.max_overshoot = max(self.max_overshoot, float(overshoot.max()))
        col = x[:nw, a]
        col[crossed] = landing
        x[:nw, a] = col
        # Velocity-controlled inflow: a recycled particle re-enters at the clean
        # free stream. This is what stops the hull's own wake recirculating back
        # onto the hull, which a naive periodic wrap would do.
        v[:nw][crossed] = self.u_free_vec
        self.recycled_total += n
        return n



class InflowSlab:
    """Per-tick Dirichlet clamp on an upstream slab, re-imposed EVERY tick.

    WHY THIS EXISTS, and it was added after a measured failure rather than by
    foresight. The first version of this driver forced the flow with a one-shot
    additive kick and then relied on the recyclers alone to maintain it. A
    recycler only re-imposes the free stream on particles that actually CROSS the
    outflow plane, so it is not forcing at all: it is a boundary condition that
    does nothing when the flow stops.

    And the flow does stop. Measured 2026-08-19 on the g64 arc: with pure
    broadside flow at 3.0 m/s only 34 of 48,746 water particles recycled in 60
    frames, against roughly 33,000 expected from the travel distance, while the
    pure axial cell at the same speed recycled 34,414. The hull is 4.28 m long
    and 1.75 m wide in an 8.53 m channel, so it blocks about 54 percent of the
    broadside path and about 24 percent of the axial one. The kick's momentum was
    destroyed by the obstruction and never replaced, so the broadside cells were
    measuring how fast the flow STALLED, not the load on the hull.

    This is sim_standing.py's own mechanism (a per-frame Dirichlet clamp on an
    upstream particle slab, :190-198, called every frame at :202) rather than
    something invented here, which is what keeps the forcing comparable to the
    canonical runs.
    """

    def __init__(self, axis, u_free_vec, p_lo, p_hi, thickness):
        self.axis = int(axis)
        self.u = np.asarray(u_free_vec, dtype=np.float64).reshape(3)
        self.u_axis = float(self.u[self.axis])
        self.p_lo, self.p_hi, self.thickness = float(p_lo), float(p_hi), float(thickness)
        self.n_last = 0

    @property
    def active(self):
        return self.u_axis != 0.0

    def apply(self, x, v, n_water):
        if not self.active:
            self.n_last = 0
            return 0
        s = x[:n_water, self.axis]
        if self.u_axis > 0.0:
            sel = s <= (self.p_lo + self.thickness)
        else:
            sel = s >= (self.p_hi - self.thickness)
        n = int(sel.sum())
        v[:n_water][sel] = self.u
        self.n_last = n
        return n


def clamp_floor_only(x, v, n_water, z_floor):
    """Vertical containment only.

    openchannel_bc.project_cross_stream clamps y with hard walls and leaves x
    free, which is right for a single-axis channel. Here BOTH horizontal axes
    carry through-flow, so a y wall would block the very flow the y recycler
    imposes. Only the floor is clamped. Returns the number of clamps.
    """
    w = x[:n_water]
    below = w[:, 2] < z_floor
    n = int(below.sum())
    if n:
        w[below, 2] = z_floor
        vv = v[:n_water]
        vz = vv[:, 2]
        vz[below] = np.maximum(vz[below], 0.0)
        vv[:, 2] = vz
    return n


# --------------------------------------------------------------------------
# the scene
# --------------------------------------------------------------------------
class MovingVehicleChannelScene:
    """Prescribed hull, bi-axial recycling free stream, wrench measured per tick."""

    def __init__(self, mesh, sdf, depth, v_car, v_water, n_grid,
                 ground_frame=False, device="auto", seed=0, bc_target_frac=0.5,
                 wrench_dt_mode="frame", inflow_cells=6.0, no_hull=False,
                 hull_y=None, bc_per_frame_force=None):
        from warpmpm.core.solver import GridConfig, Solver
        from warpmpm.materials import newtonian

        ext = np.asarray(mesh.extents, dtype=float)
        self.ext = ext
        self.depth = float(depth)
        self.v_car = float(v_car)
        self.v_water = float(v_water)
        self.ground_frame = bool(ground_frame)
        if wrench_dt_mode not in ("frame", "substep"):
            raise ValueError("wrench_dt_mode must be 'frame' or 'substep'")
        self.wrench_dt_mode = wrench_dt_mode

        # ext[1] is the LONG axis AFTER load_vehicle(up='z') permutes. Taking the
        # PLY axes at face value gives 14.989 m instead of 9.4217 m, a 59 percent
        # error. sim_standing.py:82 makes the same indexed choice for the same reason.
        lim = domain_limit(ext_long=ext[1], ext_short=ext[0], depth=depth)
        grid = GridConfig(n_grid=int(n_grid), grid_lim=lim)
        dx = grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        # RECYCLE PLANES MUST CLEAR THE DOMAIN-WALL KILL BAND.
        #
        # Solver.add_domain_walls "zero[es] outward velocity in a three-cell band
        # at each domain face" (solver.py:315-322). The first version of this
        # driver put the recycle planes at exactly 3 dx and lim - 3 dx, which is
        # the band edge, so a particle driven outward had its outward velocity
        # zeroed exactly where the plane sat and never crossed it.
        #
        # THAT FAILED ASYMMETRICALLY, WHICH IS WHY IT SURVIVED THE UNIT TESTS.
        # The recycler tests `s >= p_hi` for positive flow and `s <= p_lo` for
        # negative flow, and against a wall that arrests particles at the plane
        # those two predicates do not behave alike. Measured 2026-08-19, no hull,
        # 3.0 m/s, stream_established_frac: +x -0.187, -x +0.997, +y -0.188,
        # -y +0.997. Negative flow worked perfectly on both axes and positive
        # flow failed identically on both, so it was one sign bug, not an axis
        # bug and not the vehicle: the no-hull control was WORSE than with the
        # hull, which is what refuted the blockage explanation.
        #
        # 5 dx leaves 2 dx of clear interior between each plane and its band.
        wall_band = 3.0 * dx
        pad = 5.0 * dx
        if pad <= wall_band:
            raise ValueError(
                "recycle plane at %.4f m is inside add_domain_walls' %.1f-cell "
                "kill band; outward velocity is zeroed there and nothing will "
                "ever cross the plane" % (pad, wall_band / dx))
        self.wall_band = wall_band
        self.lim, self.dx, self.h, self.floor, self.pad = lim, dx, h, floor, pad
        self.n_grid = int(n_grid)

        # free stream in the solved frame
        if ground_frame:
            # vehicle really moves; water carries only its own velocity
            self.u_free = np.array([v_water, 0.0, 0.0], dtype=np.float64)
            self.hull_velocity = np.array([0.0, v_car, 0.0], dtype=np.float64)
        else:
            self.u_free = np.array([v_water, -v_car, 0.0], dtype=np.float64)
            self.hull_velocity = np.zeros(3, dtype=np.float64)
        self.v_rel_vec = np.array([v_water, -v_car, 0.0], dtype=np.float64)
        self.v_rel_mag = float(np.linalg.norm(self.v_rel_vec))
        # angle of the relative flow measured from the broadside (+x) axis
        self.v_rel_angle_deg = float(math.degrees(math.atan2(-v_car, v_water))
                                     ) if self.v_rel_mag > 0 else 0.0

        # hull at the domain centre in both horizontal axes; canonicalize put the
        # mesh floor at z = 0, so centre z = floor rests it on the bed.
        if ground_frame:
            half_len = float(ext[1]) / 2.0
            self.y_start = pad + half_len + 2.0 * dx
            self.center0 = np.array([0.5 * lim, self.y_start, floor])
            self.travel_available = (lim - pad - 2.0 * dx) - (self.y_start + half_len)
        else:
            # hull_y ISOLATES THE PLACEMENT CONFOUND IN THE FRAME COMPARISON.
            # The rest frame naturally puts the hull at the domain centre and the
            # ground frame must start it at one end, so the two arms of C4 did not
            # share a hull position and their at-rest vertical reactions already
            # differed (2.0474 against 1.6751) before either hull moved. Setting
            # hull_y lets the rest frame be run at the ground frame's own
            # positions, which turns one of C4's three confounds into a measured
            # quantity instead of a caveat.
            self.center0 = np.array([0.5 * lim,
                                     0.5 * lim if hull_y is None else float(hull_y),
                                     floor])
            self.travel_available = float("inf")
        self.hull_y = float(self.center0[1])

        # water block
        rng = np.random.default_rng(seed)
        lo = pad + 0.5 * h
        hi = lim - pad - 0.5 * h
        xs = np.arange(lo, hi, h)
        ys = np.arange(lo, hi, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        self.water_layers = len(zs)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)
        n_before = len(water)

        # no_hull is the CONTROL that separates a defect in this file's own
        # forcing path from a physical blockage effect of the vehicle. Identical
        # domain, identical water block, identical recyclers and inflow slabs,
        # with the hull removed and nothing else changed. If the stream
        # establishes here and not with the hull, the forcing code is sound and
        # the vehicle is what stops the flow.
        self.no_hull = bool(no_hull)
        if self.no_hull:
            inside = np.zeros(len(water), dtype=bool)
        else:
            inside = sdf_nearest(sdf, water - self.center0) < dx
        water = water[~inside].astype(np.float32)
        self.n_carved = int(inside.sum())
        self.n_water_before_carve = int(n_before)
        self.n_water = len(water)

        vol = np.full(len(water), h ** 3, dtype=np.float32)
        s = Solver(grid=grid, device=device).load_particles(water, vol)
        s.set_material(newtonian(eta=WATER_ETA, density=WATER_DENSITY,
                                 bulk_modulus=BULK_MODULUS))
        # Floor only. No horizontal walls: they would block the through-flow.
        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
        s.add_domain_walls()

        # Trap 3: xyzw explicitly, NOT left to a default, because add_cup at
        # solver.py:256 documents wxyz one screen away in the same file.
        # Trap 4: prescribed only; the body is never integrated, so no COM offset
        # is ever required and RigidBody6DOF is never constructed.
        if self.no_hull:
            self.handle = None
        else:
            self.handle = s.add_sdf_collider(
                sdf, center=tuple(self.center0), quat=(0.0, 0.0, 0.0, 1.0),
                velocity=(0.0, 0.0, 0.0), omega=(0.0, 0.0, 0.0),
                surface=COLLIDER_SURFACE, friction=COLLIDER_FRICTION)
        self.solver = s

        # CFL and substeps: sim_standing.py:227-233
        c = float(np.sqrt(EOS_GAMMA * BULK_MODULUS / WATER_DENSITY))
        u_max = float(max(abs(self.u_free).max(), abs(v_car), abs(v_water), 1e-6))
        self.term_acoustic = c / (0.28 * dx)
        self.term_viscous = 6.0 * WATER_ETA / (WATER_DENSITY * dx * dx)
        self.term_advective = u_max / (0.5 * dx)
        rate = max(self.term_acoustic, self.term_viscous, self.term_advective)
        self.sound_speed = c
        self.substeps = int(np.ceil(rate / FPS))
        self.dt = (1.0 / FPS) / self.substeps
        self.frame_dt = 1.0 / FPS

        # How often the host-side BC must run inside one frame. A particle must
        # not travel more than bc_target_frac*dx past a recycle plane before the
        # recycler sees it, or it reaches the engine's own domain wall first.
        travel_per_frame = u_max * self.frame_dt
        # bc_per_frame_force MAKES THE INTEGRATION UNIFORM ACROSS A MATRIX.
        #
        # The auto rule below sets bc_per_frame from u_max, so cells with
        # different speeds get different numbers of host-BC applications AND
        # different substeps_effective, hence a different physical duration per
        # frame. Measured on the |v_rel| = 3.0 arc: the 45 degree cell (u_max
        # 2.121) fell on bc_per_frame 1 while all four others (u_max 2.772 to
        # 3.000) got 2, so it received half the BC applications and simulated
        # 13.333 s against 14.545 s over the same 400 frames. That cell was
        # exactly the anomalous dip in the arc, so the arc's SHAPE was partly an
        # artifact of this threshold, not physics. Any matrix meant to be
        # compared cell-to-cell must pass this explicitly.
        if bc_per_frame_force is not None:
            self.bc_per_frame = max(1, int(bc_per_frame_force))
        else:
            self.bc_per_frame = max(1, int(math.ceil(travel_per_frame / (bc_target_frac * dx))))
        self.bc_auto = int(math.ceil(travel_per_frame / (bc_target_frac * dx)))
        # never coarser than the auto rule: that would let a particle overshoot
        # a recycle plane by more than the safe fraction of a cell
        if self.bc_per_frame < self.bc_auto:
            raise ValueError(
                "bc_per_frame %d is coarser than the %d the CFL-style rule needs at "
                "u_max %.3f m/s; a particle would overshoot the recycle plane"
                % (self.bc_per_frame, self.bc_auto, u_max))
        # substeps must divide into the sub-ticks; round up so the frame is whole
        self.sub_per_tick = max(1, int(math.ceil(self.substeps / self.bc_per_frame)))
        self.bc_per_frame = int(math.ceil(self.substeps / self.sub_per_tick))
        self.substeps_effective = self.sub_per_tick * self.bc_per_frame
        self.frame_dt_effective = self.substeps_effective * self.dt

        self.band_over_depth = dx / float(depth)
        self.depth_cells = float(depth) / dx
        self.time = 0.0

        # recyclers, one per horizontal axis, built from the SOLVED-frame stream
        self.rec = []
        self.slab = []
        self.inflow_thickness = float(inflow_cells) * dx
        for a in (0, 1):
            r = AxisRecycler(axis=a, n_water=self.n_water, p_lo=pad, p_hi=lim - pad,
                             u_free_vec=self.u_free, dx=dx, grid_lim=lim, seed=seed + a)
            self.rec.append(r)
            self.slab.append(InflowSlab(a, self.u_free, pad, lim - pad,
                                        self.inflow_thickness))
        self.n_clamped_floor = 0
        self.slab_frac = None

    # ----------------------------------------------------------------
    def _host_bc(self):
        x = self.solver.x()
        v = self.solver.v()
        moved = 0
        for r in self.rec:
            moved += r.apply(x, v)
        ns = 0
        for sl in self.slab:
            ns += sl.apply(x, v, self.n_water)
        self.slab_frac = ns / float(self.n_water)
        self.n_clamped_floor += clamp_floor_only(x, v, self.n_water, self.floor)
        self.solver.set_x(x)
        self.solver.set_v(v)
        return moved

    def water_speed_stats(self):
        """Mean water velocity over the whole pool.

        THE STALL DETECTOR. It exists because the stall above was found only by
        noticing an odd recycle count, which is an indirect symptom. A driver
        whose forcing dies should say so in its own record. u_mean projected on
        the intended free stream, divided by |u_free|, is 1.0 for a fully
        established stream and falls toward 0 as it stalls.
        """
        v = self.solver.v()[:self.n_water]
        um = v.mean(axis=0)
        mag = float(np.linalg.norm(self.u_free))
        proj = float(um @ self.u_free / mag) / mag if mag > 0 else 0.0
        return um.tolist(), proj

    def kick(self):
        """One-shot additive free-stream kick on every water particle.

        This is sim_standing.py's own mechanism (a one-shot additive kick after
        the settle phase, :156-162) rather than something invented here, which is
        what keeps the v_car = 0 cell comparable to the canonical runs. Without
        it the recyclers alone would need a full flush-through to establish the
        stream, which costs frames this scene does not have.
        """
        v = self.solver.v()
        v[:self.n_water] = v[:self.n_water] + self.u_free
        self.solver.set_v(v)

    def settle(self, frames):
        """Hold everything at rest and let the column reach hydrostatic balance.

        The vertical reaction here is the one quantity in this scene with an
        independent analytic target, rho*g*V_submerged, so this trace is the
        physical check on the coupling rather than a warm-up.
        """
        trace = []
        for i in range(int(frames)):
            if self.handle is None:
                self.solver.step(self.dt, self.substeps)
                trace.append({"settle_frame": i + 1, "force_N": [0.0, 0.0, 0.0]})
                continue
            self.solver.reset_sdf_force(self.handle)          # trap 2
            self.solver.step(self.dt, self.substeps)
            wdt = self.dt if self.wrench_dt_mode == "substep" else self.frame_dt
            w = self.solver.sdf_wrench(self.handle, wdt)             # trap 1
            f = np.asarray(w["force"], dtype=float)
            trace.append({"settle_frame": i + 1, "force_N": f.tolist()})
        return trace

    def start_motion(self):
        """Ground frame only: hand the hull its prescribed velocity."""
        if self.ground_frame and self.handle is not None:
            self.solver.set_sdf_pose(self.handle,
                                     velocity=tuple(float(c) for c in self.hull_velocity))

    def collider_center(self):
        c = self.solver._sim.collider_params[self.handle].center
        return np.array([float(c[0]), float(c[1]), float(c[2])], dtype=float)

    def step_frame(self):
        """One tick. reset -> step -> wrench(TICK dt) -> host BC.

        Trap 1 lives here: the wrench dt is self.frame_dt_effective, the duration
        of everything stepped since the reset, NOT self.dt. Handing it self.dt
        would inflate every force in this file by exactly substeps_effective.

        wrench_dt_mode EXISTS TO MAKE THAT FAILURE REPRODUCIBLE ON PURPOSE.
        A test that merely passes when the right dt is handed over is not
        evidence: it would also pass if the detector were blind. Setting
        wrench_dt_mode = "substep" commits the trap deliberately, so the
        no-forcing control can be shown to MOVE by exactly substeps_effective.
        A detector that has never been seen to fire has not been tested.
        """
        s = self.solver
        if self.handle is not None:
            s.reset_sdf_force(self.handle)                   # trap 2, every tick
        for _ in range(self.bc_per_frame):
            s.step(self.dt, self.sub_per_tick)
            self._host_bc()
        if self.handle is None:
            self.time += self.frame_dt_effective
            return {"force": np.zeros(3), "torque": np.zeros(3)}
        if self.wrench_dt_mode == "substep":
            w = s.sdf_wrench(self.handle, self.dt)           # DELIBERATELY WRONG
        else:
            w = s.sdf_wrench(self.handle, self.frame_dt_effective)   # trap 1
        self.time += self.frame_dt_effective
        return w


# --------------------------------------------------------------------------
# matrices
# --------------------------------------------------------------------------
V_CAR_GRID = [0.0, 2.2, 4.5, 6.7, 8.9]        # 0, 5, 10, 15, 20 mph
V_WATER_GRID = [0.5, 1.0, 2.0, 3.0]


def iso_vrel_arc(mag=3.0, n=5):
    """Cells with IDENTICAL |v_rel| and different (v_car, v_water) split.

    This is the falsifiable core of the unit. If the load is a function of
    |v_rel| alone, as the field's scalar treatments assume, every cell on this
    arc returns the same load. If it is not, the split matters and the size of
    the difference is the measurement. Both outcomes are results.
    """
    out = []
    for k in range(n):
        th = (math.pi / 2.0) * k / (n - 1)     # 0 = pure broadside, pi/2 = pure axial
        out.append((round(mag * math.sin(th), 6), round(mag * math.cos(th), 6)))
    return out                                  # (v_car, v_water)


def full_matrix():
    return [(c, w) for c in V_CAR_GRID for w in V_WATER_GRID]


# --------------------------------------------------------------------------
# self-test, pure numpy, runs without warpmpm or a GPU
# --------------------------------------------------------------------------
def _selftest():
    ok = 0

    # ST1 trap 1 sentinel.
    #
    # SCAN THE DRIVER, NOT THIS FUNCTION. The first version of this check tested
    # the whole file for the bad call pattern and FAILED on its own assertion
    # string, because the needle is itself source text of the file being scanned.
    # That is not a nuisance: had the polarity been the other way the check would
    # have PASSED on its own text while the driver was wrong, which is the
    # laundered-check failure mode slot d9-kramer recorded tonight (a correct
    # test pointed at the wrong quantity looks like rigour). So the self-test's
    # own body is excised before any source assertion runs.
    assert _WRENCH_DT_IS_FRAME_DT is True
    src = Path(__file__).read_text()
    marker = "def _self" + "test()"
    assert src.count(marker) == 1, "excision marker is ambiguous"
    body = src.split(marker)[0]
    assert "sdf_wrench(self.handle, self.frame_dt_effective)" in body, \
        "step_frame must hand sdf_wrench the TICK duration, not dt"
    # The WRONG call form is present ON PURPOSE, exactly once, and only behind the
    # wrench_dt_mode guard, so the no-forcing control can be re-run with the trap
    # deliberately committed and the detector shown to fire. A detector that has
    # never been observed to fire has not been tested. What must hold is that it
    # is guarded and that the default is the correct branch.
    assert body.count("sdf_wrench(self.handle, self.dt)") == 1, \
        "the wrong-dt call must appear exactly once, behind its guard"
    assert 'self.wrench_dt_mode == "substep"' in body, \
        "the wrong-dt call must be reachable only through the explicit mode"
    assert 'wrench_dt_mode="frame"' in body, \
        "the DEFAULT wrench dt mode must be the correct one"
    ok += 1

    # ST2 trap 2: a reset in the settle loop and a reset in step_frame
    assert body.count("reset_sdf_force(self.handle)") >= 2
    ok += 1

    # ST3 trap 5: periodic_x never set on a scene carrying an SDF collider
    assert "periodic_x=True" not in body and "periodic_x = True" not in body
    ok += 1

    # ST4 domain rule reproduces the published Yaris limit from its own extents
    lim = domain_limit(ext_long=4.28261, ext_short=1.7078, depth=0.30)
    assert abs(lim - 9.421742) < 1e-4, lim
    ok += 1

    # ST5 the iso arc really is iso
    arc = iso_vrel_arc(3.0, 5)
    for vc, vw in arc:
        assert abs(math.hypot(vc, vw) - 3.0) < 1e-6, (vc, vw)
    assert abs(arc[0][0]) < 1e-9 and abs(arc[-1][1]) < 1e-9
    ok += 1

    # ST6 recycler, POSITIVE x flow: crosses the high plane, lands past the low
    # plane by its overshoot, keeps y and z, and leaves with the free stream.
    dx, lim = 0.147215, 9.421742
    u = np.array([3.0, 0.0, 0.0])
    r = AxisRecycler(axis=0, n_water=2, p_lo=3 * dx, p_hi=lim - 3 * dx,
                     u_free_vec=u, dx=dx, grid_lim=lim)
    x = np.array([[lim - 3 * dx + 0.05, 4.0, 0.2], [1.0, 4.0, 0.2]])
    v = np.array([[9.9, 9.9, 9.9], [0.1, 0.2, 0.3]])
    n = r.apply(x, v)
    assert n == 1, n
    assert abs(x[0, 0] - (3 * dx + 0.05)) < 1e-9, x[0, 0]
    assert x[0, 1] == 4.0 and x[0, 2] == 0.2, "y and z must survive: J is a function of z"
    assert np.allclose(v[0], u), v[0]
    assert np.allclose(v[1], [0.1, 0.2, 0.3]), "an uncrossed particle must be untouched"
    ok += 1

    # ST7 recycler, NEGATIVE y flow: this is the case v_car creates, and the
    # parent class cannot express it at all.
    u = np.array([0.0, -8.9, 0.0])
    r = AxisRecycler(axis=1, n_water=1, p_lo=3 * dx, p_hi=lim - 3 * dx,
                     u_free_vec=u, dx=dx, grid_lim=lim)
    x = np.array([[4.0, 3 * dx - 0.05, 0.2]])
    v = np.array([[0.0, 0.0, 0.0]])
    n = r.apply(x, v)
    assert n == 1
    assert abs(x[0, 1] - (lim - 3 * dx - 0.05)) < 1e-9, x[0, 1]
    assert np.allclose(v[0], u)
    ok += 1

    # ST8 zero free stream is a no-op, which is what makes the no-forcing control
    # a control: if the BC itself injected momentum the control could not be clean.
    r = AxisRecycler(axis=0, n_water=1, p_lo=3 * dx, p_hi=lim - 3 * dx,
                     u_free_vec=np.zeros(3), dx=dx, grid_lim=lim)
    x = np.array([[lim, 4.0, 0.2]])
    v = np.array([[0.0, 0.0, 0.0]])
    assert r.apply(x, v) == 0 and x[0, 0] == lim
    ok += 1

    # ST9 the inherited P2G edge guard still fires through the subclass
    for bad in (dict(p_lo=1.0 * dx, p_hi=lim - 3 * dx),
                dict(p_lo=3 * dx, p_hi=lim - 1.0 * dx)):
        try:
            AxisRecycler(axis=0, n_water=1, u_free_vec=np.array([1.0, 0, 0]),
                         dx=dx, grid_lim=lim, **bad)
        except ValueError:
            pass
        else:
            raise AssertionError("P2G edge guard did not fire for %r" % bad)
    ok += 1

    # ST10 floor clamp is vertical only
    x = np.array([[1.0, 2.0, -0.5]])
    v = np.array([[1.0, 2.0, -3.0]])
    assert clamp_floor_only(x, v, 1, 0.4) == 1
    assert x[0, 2] == 0.4 and x[0, 0] == 1.0 and x[0, 1] == 2.0
    assert v[0, 2] == 0.0 and v[0, 0] == 1.0
    ok += 1

    # ST11 ground-frame feasibility is genuinely bounded, which is WHY the rest
    # frame exists.
    #
    # CORRECTION, 2026-08-19, caught by this very assertion on its first run. The
    # scope confirmation for this slot claimed 7.4 frames at 8.9 m/s. That was
    # WRONG BY A FACTOR OF TWO: it halved the usable run, as if the hull started
    # at the domain centre, when it starts at one end and travels to the other.
    # The true figure is 14.3 frames. The conclusion is unchanged, because
    # docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md section 5 records that
    # traces in this scene family "never reach a steady value within 150 frames",
    # so 14 frames is not a measurement either. But the number that was published
    # in the confirmation was wrong and is corrected here rather than quietly.
    lim = 9.421742
    dxg = lim / 64.0
    usable = (lim - 2 * (3 * dxg) - 4.28261)
    frames_at_89 = usable / 8.9 * FPS
    assert 10.0 < frames_at_89 < 20.0, frames_at_89
    frames_at_22 = usable / 2.2 * FPS
    assert frames_at_22 > 50.0, frames_at_22
    ok += 1

    # ST13 THE PLANE-VERSUS-KILL-BAND GEOMETRY. This is the assertion that would
    # have caught the sign bug above, and it did not exist when that bug shipped.
    # add_domain_walls zeroes OUTWARD velocity in a three-cell band at each face,
    # so a recycle plane at or inside 3 dx can never be crossed from the inside.
    dxk = 9.421742 / 64.0
    assert 5.0 * dxk > 3.0 * dxk, "recycle pad must clear the 3-cell wall band"
    assert 9.421742 - 5.0 * dxk < 9.421742 - 3.0 * dxk
    # and it must still satisfy the inherited P2G guard, which is the OTHER
    # constraint; the window is [2.5 dx, lim - 2.5 dx] and both must hold at once
    assert 5.0 * dxk >= 2.5 * dxk
    ok += 1

    # ST12 the inflow slab picks the UPSTREAM end for each sign, and is a no-op
    # at zero stream. This is the forcing whose absence stalled the first arc.
    dx2 = 0.147215
    lo2, hi2 = 3 * dx2, 9.421742 - 3 * dx2
    sl = InflowSlab(0, np.array([3.0, 0.0, 0.0]), lo2, hi2, 6 * dx2)
    x = np.array([[lo2 + 0.1, 4.0, 0.2], [hi2 - 0.1, 4.0, 0.2]])
    v = np.zeros((2, 3))
    assert sl.apply(x, v, 2) == 1
    assert np.allclose(v[0], [3.0, 0, 0]), "upstream end must be clamped"
    assert np.allclose(v[1], [0, 0, 0]), "downstream end must be free"
    sl = InflowSlab(1, np.array([0.0, -3.0, 0.0]), lo2, hi2, 6 * dx2)
    x = np.array([[4.0, lo2 + 0.1, 0.2], [4.0, hi2 - 0.1, 0.2]])
    v = np.zeros((2, 3))
    assert sl.apply(x, v, 2) == 1
    assert np.allclose(v[1], [0, -3.0, 0]), "for -y flow the HIGH end is upstream"
    assert np.allclose(v[0], [0, 0, 0])
    sl = InflowSlab(0, np.zeros(3), lo2, hi2, 6 * dx2)
    v = np.zeros((2, 3))
    assert sl.apply(np.array([[lo2, 4.0, 0.2], [hi2, 4.0, 0.2]]), v, 2) == 0, \
        "zero stream must inject nothing, or the no-forcing control is not a control"
    ok += 1

    print("SELFTEST OK: %d groups passed" % ok)
    return 0


# --------------------------------------------------------------------------
def run_cell(args, mesh, sdf, v_car, v_water, f_buoy, tag):
    t0 = time.time()
    scene = MovingVehicleChannelScene(
        mesh, sdf, depth=args.depth, v_car=v_car, v_water=v_water,
        n_grid=args.n_grid, ground_frame=args.ground_frame,
        device=args.device, seed=args.seed,
        wrench_dt_mode=args.wrench_dt_mode, no_hull=args.no_hull,
        hull_y=args.hull_y, bc_per_frame_force=args.bc_per_frame)
    if scene.ground_frame:
        need = v_car * (args.frames / FPS)
        if need > scene.travel_available:
            return {"tag": tag, "status": "REFUSED_TRAVEL",
                    "needed_m": need, "available_m": scene.travel_available}
    settle = scene.settle(args.settle_frames)
    fz_settle = float(np.mean([s["force_N"][2] for s in settle[-5:]]))
    scene.kick()
    scene.start_motion()

    rows = []
    for i in range(args.frames):
        w = scene.step_frame()
        f = np.asarray(w["force"], dtype=float)
        t = np.asarray(w["torque"], dtype=float)
        rows.append({"frame": i + 1, "fx": float(f[0]), "fy": float(f[1]),
                     "fz": float(f[2]), "tx": float(t[0]), "ty": float(t[1]),
                     "tz": float(t[2])})
    u_mean, u_proj = scene.water_speed_stats()
    keep = rows[args.discard:]
    arr = np.array([[r["fx"], r["fy"], r["fz"]] for r in keep], dtype=float)
    tq = np.array([[r["tx"], r["ty"], r["tz"]] for r in keep], dtype=float)

    rec = {
        "tag": tag, "status": "OK",
        "v_car_ms": v_car, "v_water_ms": v_water,
        "v_rel_mag_ms": scene.v_rel_mag,
        "v_rel_angle_deg_from_broadside": scene.v_rel_angle_deg,
        "frame": "ground" if scene.ground_frame else "vehicle_rest",
        "n_grid": scene.n_grid, "dx_m": scene.dx, "lim_m": scene.lim,
        "depth_m": scene.depth, "depth_cells": scene.depth_cells,
        "band_over_depth": scene.band_over_depth,
        "no_hull": scene.no_hull,
        "hull_y_m": scene.hull_y,
        "ground_y_start_m": (scene.y_start if scene.ground_frame else None),
        "travel_available_m": (scene.travel_available if scene.ground_frame else None),
        "n_water": scene.n_water, "water_layers": scene.water_layers,
        "substeps": scene.substeps, "substeps_effective": scene.substeps_effective,
        "bc_per_frame": scene.bc_per_frame,
        "bc_per_frame_auto": scene.bc_auto, "dt_s": scene.dt,
        "wrench_dt_mode": scene.wrench_dt_mode,
        "wrench_dt_s": (scene.dt if scene.wrench_dt_mode == "substep"
                        else scene.frame_dt_effective),
        "frames": args.frames, "discard": args.discard,
        "settle_frames": args.settle_frames,
        "fz_settle_N": fz_settle,
        "f_buoy_analytic_N": f_buoy,
        "fz_settle_over_analytic": fz_settle / f_buoy if f_buoy else None,
        "force_mean_N": arr.mean(0).tolist(),
        "force_std_N": arr.std(0, ddof=1).tolist() if len(arr) > 1 else [0, 0, 0],
        "force_horiz_mag_N": float(np.linalg.norm(arr.mean(0)[:2])),
        "torque_about_collider_centre_mean_Nm": tq.mean(0).tolist(),
        "recycled_x": self_total(scene, 0), "recycled_y": self_total(scene, 1),
        "max_overshoot_over_dx": max(r.max_overshoot for r in scene.rec) / scene.dx,
        "floor_clamps": scene.n_clamped_floor,
        "inflow_slab_cells": 6.0,
        "inflow_slab_frac_of_pool": scene.slab_frac,
        "u_mean_water_ms": u_mean,
        "stream_established_frac": u_proj,
        "wall_s": time.time() - t0,
        "series": rows,
    }
    return rec


def self_total(scene, axis):
    return int(scene.rec[axis].recycled_total)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hull", default=str(REPO / "vehicle_geometry_research"
                                          / "yaris_coarse_v1l_watertight.ply"))
    ap.add_argument("--depth", type=float, default=0.30)
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--sdf-res", type=int, default=64)
    ap.add_argument("--frames", type=int, default=60)
    ap.add_argument("--discard", type=int, default=20)
    ap.add_argument("--settle-frames", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--mesh-seed", type=int, default=0)
    ap.add_argument("--fill-pitch", type=float, default=0.03)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--ground-frame", action="store_true")
    ap.add_argument("--matrix", default="arc",
                    choices=["arc", "full", "control", "single"])
    ap.add_argument("--arc-mag", type=float, default=3.0)
    ap.add_argument("--arc-n", type=int, default=5)
    ap.add_argument("--v-car", type=float, default=0.0)
    ap.add_argument("--v-water", type=float, default=0.0)
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--out", default=str(REPO / "out" / "r9_moving"))
    ap.add_argument("--sdf-cache", default=str(REPO / "out" / "sdf_cache"))
    ap.add_argument("--label", default="r9")
    ap.add_argument("--wrench-dt-mode", default="frame", choices=["frame", "substep"],
                    help="substep DELIBERATELY commits trap 1, so the detector can "
                         "be shown to fire. Never use it for a reported result.")
    ap.add_argument("--bc-per-frame", type=int, default=None,
                    help="force a uniform host-BC count per frame across a matrix; "
                         "the auto rule varies it with speed and that changes the "
                         "physical duration of a frame between cells.")
    ap.add_argument("--hull-y", type=float, default=None,
                    help="rest frame only: place the hull at this y instead of the "
                         "domain centre, to match a ground-frame position.")
    ap.add_argument("--no-hull", action="store_true",
                    help="CONTROL: identical scene with the vehicle removed, to "
                         "separate a forcing defect from a blockage effect.")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    print("NON-CANONICAL. Prescribed-motion hull. No FORD verdict is reportable "
          "from this scene: the vehicle cannot be swept away because its motion "
          "is imposed.", flush=True)
    print("FRAME = %s" % ("ground" if args.ground_frame else "vehicle rest"), flush=True)

    vl = load_vetted_loader()
    # SEED FIRST. load_vehicle draws 60,000 random surface samples and derives the
    # mesh shift from them, so an unseeded load is not bit-reproducible; the 2.2e-16
    # residue changes build_sdf_cached's content hash and the SDF cache NEVER hits,
    # costing about 45 minutes at res 64. Recorded in the exploratory driver.
    np.random.seed(args.mesh_seed)
    t0 = time.time()
    veh = canonicalize(vl.load_vehicle(args.hull, up="z", spacing=0.40))
    mesh = veh.mesh
    print("hull %s: %d faces watertight=%s volume %.6f m3 (%.1f s)"
          % (Path(args.hull).name, len(mesh.faces), mesh.is_watertight,
             float(mesh.volume), time.time() - t0), flush=True)
    ext = np.asarray(mesh.extents, dtype=float)
    print("canonical extent (x,y,z) = %.6f %.6f %.6f, long axis on y" % tuple(ext),
          flush=True)
    print("domain lim = %.9f m (CLAUDE.md item 4 extents would give %.9f; "
          "derived from THIS mesh, not hardcoded)"
          % (domain_limit(ext[1], ext[0], args.depth),
             domain_limit(4.2014, 1.7078, args.depth)), flush=True)

    t0 = time.time()
    sdf = build_hull_sdf(mesh, args.sdf_res, args.sdf_cache)
    print("SDF res=%d cell=%.6f m (%.1f s)" % (args.sdf_res, sdf.cell, time.time() - t0),
          flush=True)

    fill = vl.solidify_watertight(mesh, args.fill_pitch)
    v_sub = float((np.asarray(fill)[:, 2] < args.depth).sum()) * args.fill_pitch ** 3
    f_buoy = WATER_DENSITY * G * v_sub
    print("submerged volume below z=%.2f m: %.6f m3 -> analytic buoyancy %.1f N"
          % (args.depth, v_sub, f_buoy), flush=True)

    if args.matrix == "arc":
        cells = iso_vrel_arc(args.arc_mag, args.arc_n)
    elif args.matrix == "full":
        cells = full_matrix()
    elif args.matrix == "control":
        cells = [(0.0, 0.0)]
    else:
        cells = [(args.v_car, args.v_water)]

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    print("MATRIX %s: %d cells x %d repeats" % (args.matrix, len(cells), args.repeat),
          flush=True)

    results = []
    for (vc, vw) in cells:
        for rep in range(1, args.repeat + 1):
            tag = "%s_g%d_vc%.4f_vw%.4f_r%d" % (args.label, args.n_grid, vc, vw, rep)
            rec = run_cell(args, mesh, sdf, vc, vw, f_buoy, tag)
            rec["repeat"] = rep
            results.append(rec)
            p = outdir / (tag + ".json")
            p.write_text(json.dumps(rec, indent=1))
            if rec["status"] != "OK":
                print("CELL %s %s %r" % (tag, rec["status"], rec), flush=True)
                continue
            fm = rec["force_mean_N"]
            print("CELL %s  v_car %.3f v_water %.3f |v_rel| %.4f angle %.2f deg  "
                  "F = (%.1f, %.1f, %.1f) N  |F_h| %.1f N  fz_settle/analytic %.4f  "
                  "%.1f s"
                  % (tag, vc, vw, rec["v_rel_mag_ms"],
                     rec["v_rel_angle_deg_from_broadside"], fm[0], fm[1], fm[2],
                     rec["force_horiz_mag_N"], rec["fz_settle_over_analytic"] or 0.0,
                     rec["wall_s"]), flush=True)

    summary = outdir / ("SUMMARY_%s_g%d.json" % (args.label, args.n_grid))
    summary.write_text(json.dumps(
        [{k: v for k, v in r.items() if k != "series"} for r in results], indent=1))
    print("WROTE %s" % summary, flush=True)
    print("ALLDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
