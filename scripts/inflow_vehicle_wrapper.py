#!/usr/bin/env python3
"""
inflow_vehicle_wrapper.py  --  run the CANONICAL vehicle scene with Zhao et al 2019
recycling in/outflow instead of reflecting streamwise walls, WITHOUT editing the driver.

WHAT THIS PORTS, AND FROM WHERE
simulation/openchannel_bc.py (commit be1b138, branch claude/add-ci-checks) translates
Zhao, Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179, 27-33,
doi:10.1016/j.compfluid.2018.10.007 (Anura3D) add/remove inflow-outflow into an engine
that cannot add or remove a particle: one-in-one-out recycling inside a fixed pool. That
module was measured on the WATER-ONLY channel (simulation/sim_channel.py). It had never
been run with a vehicle. This wrapper is that port and nothing else: the BC class is
imported, not reimplemented, so the physics translation has exactly one definition.

WHY A WRAPPER AND NOT AN EDIT
renders/yaris_render_s1/sim_standing.py sha256
4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9 stamps every published
run. Editing it would break that stamp for all 17. The precedent for injecting behaviour
from outside is register D5 (settle and seed) and scripts/pinned_span_wrapper.py, which
monkeypatches `canonicalize` on the imported module. This wrapper patches two module
globals of the SAME imported module and calls its `main()` unchanged:

  mod.Solver              -> a subclass whose add_plane DROPS the two x-normal slip walls
  mod.StandingFloodScene  -> a subclass that recycles instead of clamping x, and that
                             records the per-frame instrumentation the comparison needs

Both patches are applied ONLY when --bc recycle. At --bc closed the driver runs through
its own untouched classes and the wrapper adds read-only instrumentation, so the closed
arm is a matched control produced by the same code path rather than a different script.

WHY NOT periodic_x
core/solver.py:93 documents periodic_x as "Incompatible with CDF colliders and rigid
bodies". The gated vehicle IS a rigid body (sim_standing.py calls set_material_range(...,
"rigid", obj_id=0) then finalize_rigid_bodies()). Recycling is the route; periodic is not.

WHAT THE STREAMWISE WALLS COST, AND WHY IT IS WORTH REMOVING THEM
The tank is closed on four slip walls plus a floor. A shallow-water gravity wave
c_g = sqrt(g*d) launched at the vehicle reflects off the downstream wall and returns.
RECONSTRUCTED, NOT READ: with d = 0.2944294473039918 m, g = 9.81, lim = 9.421742313727738,
dx = lim/64, vehicle at 0.60*lim and the wall at lim - 4*dx, the round trip is
2*(lim - 4*dx - 0.60*lim)/sqrt(g*d) = 3.7420 s = 112.26 frames at 30 fps. That reproduces
the "predicted frame 112.3" carried by analysis/r6_repeat_stats.py:20-21 to within 0.04 of
a frame, so the mechanism is a shallow-water reflection. The derivation itself is nowhere
in the repo; treat this paragraph as the reconstruction, not as a citation.

The CROSS-STREAM walls remain in both arms. The same arithmetic puts their first return at
2*(0.5*lim - 4*dx)/sqrt(g*d) = 145.5 frames, later than the streamwise 112.3, which is why
the streamwise pair is the binding one and why removing it is expected to push the first
reflection from ~112 to ~145 rather than to infinity. That is a pre-registered prediction.

THE SETTLE PHASE IS DELIBERATELY MATCHED, AND IT IS NOT BIT-IDENTICAL
sim_standing.py runs 8 settle frames of `_project_water(); step()` BEFORE the velocity
kick and before history row 0. In the recycle arm the streamwise planes are absent for the
whole run, so an unmodified settle would let the block slump out of the channel at the
dam-break speed 2*sqrt(g*d) = 3.4 m/s, about 0.9 m in 8 frames. Instead this wrapper
clamps x during the settle phase ONLY, exactly as the canonical `_project_water` does, and
switches to recycling the instant the settle loop ends. So the t=0 geometry is the same
rectangular block in both arms and the boundary condition is the only thing that differs
from t=0 onward. It is NOT a bit-reproduction of the canonical settle: the canonical arm
also has grid-node slip planes acting during those 8 frames and the recycle arm does not.
Stated, not hidden.

THE INFLOW BAND IS KEPT BY DEFAULT, AND THAT IS A CHOICE
sim_standing.py's `_sustain_inflow` overwrites vx for every water particle upstream of
wall + 1.5 m, every frame. That IS a velocity-controlled inflow in Zhao's sense, just over
a slab rather than a plane, and it is the scene's only momentum source. Keeping it holds
the forcing identical between the two arms so that a difference is attributable to the
boundary and not to the drive. --no-band removes it, which is the faithful sim_channel.py
recycle mode, and is run as a sensitivity arm rather than as the default.

WHY THE P2G EDGE GUARD CANNOT FIRE ON THE OUTFLOW SIDE
core/solver.py:430-431 runs _update_grid_box at the START of Solver.step, before the
frame's substeps, and :506-512 raise if any particle sits beyond grid_lim - 2.5*dx.
sim_standing.py's step() calls _project_water() BEFORE solver.step(), and the recycler
lives inside _project_water, so at the instant the guard reads the particle array nothing
is downstream of x_out = grid_lim - 4*dx. 4*dx > 2.5*dx, so the guard is satisfied by
construction rather than by luck. Within-frame excursions are the bounding box's job
(add_domain_walls, "prevents splashes from leaving [0, grid_lim]^3"), and _update_grid_box
already pads the launch box by 1.5*|v|max*dt*substeps for exactly that. x_out is therefore
placed at the closed arm's wall position and not backed off from it, which is what makes
the two arms share a streamwise extent.

KNOWN LIMITATION, MEASURED RATHER THAN ASSUMED AWAY
Recycling is a recirculation: wake water leaving at x_out re-enters at x_in carrying its
(y, z). With a blocking vehicle that feeds wake structure back to the inlet, which the
water-only channel could not exhibit. Advecting at the inlet velocity the round trip from
the vehicle's downstream face to x_out and from x_in back to its upstream face is about
6.5 m, or roughly 130 frames at 1.5 m/s, so it should not reach the vehicle inside the
canonical 90-frame horizon. This wrapper does not assume that: it tags every particle that
has ever been recycled and records, per frame, how many tagged particles are inside the
vehicle's streamwise influence window, so the contamination onset is measured.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "simulation"))

from openchannel_bc import RecyclingChannelBC, depth_profile  # noqa: E402

CANONICAL_DRIVER_SHA256 = (
    "4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9"
)
G_POST = 9.81  # solver value, core/solver.py:167-169. Used only for the wave prediction.


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_driver(path):
    """Import sim_standing.py by path without importing it as 'sim_standing'.

    Same shape as scripts/pinned_span_wrapper.py:load_driver. A distinct module name keeps
    this from colliding with any other copy of the driver on sys.path.
    """
    spec = importlib.util.spec_from_file_location("sim_standing_inflow", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sim_standing_inflow"] = mod
    spec.loader.exec_module(mod)
    for need in ("main", "StandingFloodScene", "Solver"):
        if not hasattr(mod, need):
            raise SystemExit("driver %s lacks %s" % (path, need))
    return mod


# --------------------------------------------------------------------------------------
# Pure helpers. Free functions on purpose: --selftest exercises every one of them on the
# Mac with numpy alone, so the logic is checked before a GPU node is ever allocated.
# --------------------------------------------------------------------------------------

def is_streamwise_plane(normal) -> bool:
    """True for the two x-normal walls sim_standing.py adds, false for the floor.

    sim_standing.py:212-215 adds exactly four walls with normals (1,0,0), (-1,0,0),
    (0,1,0), (0,-1,0) and one floor with (0,0,1). Only the first two are dropped.
    """
    n = np.asarray(normal, dtype=float)
    return bool(abs(n[0]) > 0.5)


def water_budget(w, wall, lim, floor, eps):
    """Per-face count of water outside the canonical box, BEFORE any clamp.

    The canonical `leaked_particle_frames` counter is a single number over all six faces
    (sim_standing.py:250), so it cannot say whether a change came from the floor or from a
    wall. This returns the split, on the canonical box in BOTH arms, so the closed and
    recycle numbers are computed against the same reference volume even though the recycle
    arm no longer treats the x faces as walls.
    """
    lo_x, hi_x = wall - eps, lim - wall + eps
    lo_y, hi_y = wall - eps, lim - wall + eps
    lo_z = floor - eps
    below = w[:, 2] < lo_z
    out_xlo = w[:, 0] < lo_x
    out_xhi = w[:, 0] > hi_x
    out_ylo = w[:, 1] < lo_y
    out_yhi = w[:, 1] > hi_y
    any_out = below | out_xlo | out_xhi | out_ylo | out_yhi
    return {
        "n_below_floor": int(below.sum()),
        "n_out_xlo": int(out_xlo.sum()),
        "n_out_xhi": int(out_xhi.sum()),
        "n_out_ylo": int(out_ylo.sum()),
        "n_out_yhi": int(out_yhi.sum()),
        "n_out_any": int(any_out.sum()),
        "min_z": float(w[:, 2].min()),
        "x_min": float(w[:, 0].min()),
        "x_max": float(w[:, 0].max()),
    }


def clamp_box(w, vw, lo, hi):
    """The canonical clamp, factored out so both arms share one implementation.

    Mirrors sim_standing.py:246-259 exactly: clip positions, then kill the OUTWARD velocity
    component only (max with 0 on the low faces, min with 0 on the high faces). Returns the
    number of distinct particles clamped, which is what the canonical `leaked` counter adds.
    """
    out_lo = w < lo
    out_hi = w > hi
    if not (out_lo.any() or out_hi.any()):
        return 0
    n = int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
    np.clip(w, lo, hi, out=w)
    vw[out_lo] = np.maximum(vw[out_lo], 0.0)
    vw[out_hi] = np.minimum(vw[out_hi], 0.0)
    return n


class TrackedRecyclingBC(RecyclingChannelBC):
    """RecyclingChannelBC plus a permanent per-particle 'has been recycled' tag.

    The base class returns only a count. The recirculation question needs identity: which
    particles have been round the loop, and when do they reach the vehicle. The crossing
    mask is recomputed here from the SAME array and the SAME predicate the base class uses
    (x[:n_water, 0] >= x_out), immediately before delegating, so the tag cannot drift from
    what was actually moved.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.ever = np.zeros(self.n_water, dtype=bool)

    def apply(self, x, v):
        crossed = x[: self.n_water, 0] >= self.x_out
        n = super().apply(x, v)
        if n:
            self.ever |= crossed
        return n


def predict_reflection_frames(lim, dx, depth, fps=30.0, veh_frac=0.60, wall_cells=4.0):
    """Shallow-water round-trip frames for the streamwise and cross-stream wall pairs.

    RECONSTRUCTION. See the module docstring: this reproduces the repo's carried 112.3 to
    0.04 frames but the repo records no derivation, so it is labelled as inferred.
    """
    c_g = float(np.sqrt(G_POST * depth))
    d_stream = (lim - wall_cells * dx) - veh_frac * lim
    d_cross = 0.5 * lim - wall_cells * dx
    return {
        "c_gravity_ms": c_g,
        "stream_half_path_m": float(d_stream),
        "cross_half_path_m": float(d_cross),
        "stream_reflection_frame": float(2.0 * d_stream / c_g * fps),
        "cross_reflection_frame": float(2.0 * d_cross / c_g * fps),
    }


def build_patched(mod, cfg):
    """Return (SceneClass, SolverClass or None). Nothing is installed here."""
    Base = mod.StandingFloodScene
    BaseSolver = mod.Solver
    dropped = []

    class NoStreamwiseWallSolver(BaseSolver):
        def add_plane(self, point, normal, surface="sticky", friction=0.0,
                      restitution=0.0):
            if is_streamwise_plane(normal):
                dropped.append({
                    "point": [float(q) for q in point],
                    "normal": [float(q) for q in normal],
                    "surface": surface, "friction": float(friction),
                    "restitution": float(restitution),
                })
                return self
            return super().add_plane(point, normal, surface, friction=friction,
                                     restitution=restitution)

    class InflowScene(Base):
        # main() keeps its scene object local, so the one instance records itself here.
        # Simpler and less fragile than threading a return value out of the driver.
        _last = None

        # Set before super().__init__ so the settle-phase _project_water sees them.
        def __init__(self, *a, **kw):
            self._settled = False
            self._instr_on = False
            self.bc = None
            self.budget = []
            self.prof = []
            self.recycled_per_frame = []
            self.tagged_near_vehicle = []
            self.tagged_total = []
            self.veh_bbox = []
            self.water_x_span = []
            self.leaked_split = {"floor": 0, "x": 0, "y": 0}
            super().__init__(*a, **kw)
            self.x_in = float(self._wall)
            self.x_out = float(self._lim - self._wall)
            if cfg["bc"] == "recycle":
                self.bc = TrackedRecyclingBC(
                    n_water=self.n_water, x_in=self.x_in, x_out=self.x_out,
                    inlet_velocity=self.velocity, dx=self.dx, grid_lim=self._lim,
                    prescribe="full")
            self._settled = True
            self._instr_on = True
            InflowScene._last = self

        # ---- boundary condition -----------------------------------------------------
        def _project_water(self):
            s = self.solver
            x = s.x()
            v = s.v()
            w = x[: self.n_water]
            vw = v[: self.n_water]
            eps = 0.25 * self.grid.dx

            if self._instr_on:
                self.budget.append(water_budget(w, self._wall, self._lim, self.floor, eps))

            recycled = 0
            if cfg["bc"] == "recycle" and self._settled:
                # Streamwise: outflow plane recycles to the inflow plane. x is NEVER
                # clamped after the settle phase; that clamp IS the closed-box artifact.
                recycled = self.bc.apply(x, v)
                lo = np.array([-np.inf, self._wall - eps, self.floor - eps],
                              dtype=np.float32)
                hi = np.array([np.inf, self._lim - self._wall + eps, np.inf],
                              dtype=np.float32)
            else:
                # Canonical three-axis clamp. Also used for the recycle arm's settle
                # phase, so both arms reach t=0 with the same rectangular block.
                lo = np.array([self._wall, self._wall, self.floor],
                              dtype=np.float32) - eps
                hi = np.array([self._lim - self._wall, self._lim - self._wall, np.inf],
                              dtype=np.float32) + eps

            n_clamped = clamp_box(w, vw, lo, hi)
            self.leaked += n_clamped
            self._recycled_this_frame = recycled
            if n_clamped or recycled:
                s.set_x(x)
                s.set_v(v)

        def _sustain_inflow(self):
            if cfg["no_band"]:
                return 0
            return super()._sustain_inflow()

        # ---- instrumentation --------------------------------------------------------
        def step(self):
            st = super().step()
            if not self._instr_on:
                return st
            x = self.solver.x()
            w = x[: self.n_water]
            veh = x[self.n_water:]
            _, depths = depth_profile(w, self.floor, self.x_in, self.x_out,
                                      n_bins=cfg["bins"])
            self.prof.append(depths)
            lo_v, hi_v = veh.min(0), veh.max(0)
            self.veh_bbox.append([float(lo_v[0]), float(hi_v[0]),
                                  float(lo_v[1]), float(hi_v[1]),
                                  float(lo_v[2]), float(hi_v[2])])
            self.water_x_span.append([float(w[:, 0].min()), float(w[:, 0].max())])
            self.recycled_per_frame.append(int(getattr(self, "_recycled_this_frame", 0)))
            if self.bc is not None:
                near = ((w[:, 0] >= lo_v[0] - 3.0 * self.dx) &
                        (w[:, 0] <= hi_v[0] + 3.0 * self.dx))
                self.tagged_near_vehicle.append(int((near & self.bc.ever).sum()))
                self.tagged_total.append(int(self.bc.ever.sum()))
            else:
                self.tagged_near_vehicle.append(0)
                self.tagged_total.append(0)
            return st

    return InflowScene, (NoStreamwiseWallSolver if cfg["bc"] == "recycle" else None), dropped


# --------------------------------------------------------------------------------------

def _selftest():
    """numpy only, no warp, no driver. Runs on the Mac."""
    # 1. plane predicate picks exactly the two streamwise walls
    assert is_streamwise_plane((1, 0, 0)) and is_streamwise_plane((-1, 0, 0))
    assert not is_streamwise_plane((0, 1, 0))
    assert not is_streamwise_plane((0, -1, 0))
    assert not is_streamwise_plane((0, 0, 1))

    wall, lim, floor, eps = 0.5888588946, 9.4217423137, 0.4416441710, 0.0368036809
    w = np.array([
        [5.0, 5.0, 0.60],            # interior
        [0.10, 5.0, 0.60],           # past the low x wall
        [9.30, 5.0, 0.60],           # past the high x wall
        [5.0, 0.10, 0.60],           # past the low y wall
        [5.0, 9.30, 0.60],           # past the high y wall
        [5.0, 5.0, 0.30],            # below the floor
    ], dtype=np.float32)
    b = water_budget(w, wall, lim, floor, eps)
    assert b["n_below_floor"] == 1 and b["n_out_xlo"] == 1 and b["n_out_xhi"] == 1
    assert b["n_out_ylo"] == 1 and b["n_out_yhi"] == 1 and b["n_out_any"] == 5
    assert abs(b["min_z"] - 0.30) < 1e-6

    # 2. clamp_box reproduces the canonical clamp: positions clipped, outward v killed,
    #    inward v untouched, and the count is DISTINCT particles not axis violations.
    w2 = w.copy()
    v2 = np.array([[0, 0, 0], [-1, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, -1]],
                  dtype=np.float32)
    lo = np.array([wall, wall, floor], dtype=np.float32) - eps
    hi = np.array([lim - wall, lim - wall, np.inf], dtype=np.float32) + eps
    n = clamp_box(w2, v2, lo, hi)
    assert n == 5, n
    assert (w2[:, 0] >= lo[0] - 1e-6).all() and (w2[:, 0] <= hi[0] + 1e-6).all()
    assert v2[1, 0] == 0.0 and v2[2, 0] == 0.0 and v2[5, 2] == 0.0
    assert np.array_equal(w2[0], w[0]), "interior particle moved"
    # a particle violating two axes at once counts once
    w3 = np.array([[0.1, 0.1, 0.6]], dtype=np.float32)
    v3 = np.zeros((1, 3), dtype=np.float32)
    assert clamp_box(w3, v3, lo, hi) == 1

    # 3. recycle-mode bounds never touch x
    w4 = w.copy(); v4 = np.zeros_like(v2)
    lo_r = np.array([-np.inf, wall - eps, floor - eps], dtype=np.float32)
    hi_r = np.array([np.inf, lim - wall + eps, np.inf], dtype=np.float32)
    clamp_box(w4, v4, lo_r, hi_r)
    assert np.array_equal(w4[:, 0], w[:, 0]), "recycle-mode clamp moved x"
    assert w4[3, 1] > 0.10 and w4[5, 2] > 0.30, "y/z still clamped in recycle mode"

    # 4. TrackedRecyclingBC tags exactly the particles the base class moved
    rng = np.random.default_rng(0)
    nw, nveh = 400, 31
    dx, gl = 0.1472147237, 9.4217423137
    x = np.zeros((nw + nveh, 3), dtype=np.float32)
    x[:, 0] = rng.uniform(0.6, 9.0, nw + nveh)
    x[:, 1] = rng.uniform(0.6, 8.8, nw + nveh)
    x[:, 2] = rng.uniform(0.45, 0.75, nw + nveh)
    v = rng.normal(0, 0.3, (nw + nveh, 3)).astype(np.float32)
    x0 = x.copy()
    bc = TrackedRecyclingBC(n_water=nw, x_in=0.5888588946, x_out=8.8328834191,
                            inlet_velocity=1.5, dx=dx, grid_lim=gl)
    n = bc.apply(x, v)
    expected = x0[:nw, 0] >= 8.8328834191
    assert n == int(expected.sum()) == int(bc.ever.sum()), (n, expected.sum(), bc.ever.sum())
    assert np.array_equal(bc.ever, expected)
    assert np.array_equal(x[nw:], x0[nw:]), "vehicle rows moved"
    # tags are permanent across calls
    bc.apply(x, v)
    assert bc.ever.sum() >= expected.sum()

    # 5. the reflection reconstruction reproduces the repo's carried 112.3
    p = predict_reflection_frames(lim=9.421742313727738, dx=9.421742313727738 / 64,
                                  depth=0.2944294473039918)
    assert abs(p["stream_reflection_frame"] - 112.3) < 0.1, p["stream_reflection_frame"]
    assert p["cross_reflection_frame"] > p["stream_reflection_frame"]

    print("inflow_vehicle_wrapper selftest: 5 groups PASS "
          "(stream reflection %.2f frames, cross %.2f frames)"
          % (p["stream_reflection_frame"], p["cross_reflection_frame"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--driver")
    ap.add_argument("--bc", choices=("closed", "recycle"))
    ap.add_argument("--out")
    ap.add_argument("--label")
    ap.add_argument("--depth", type=float, default=0.30)
    ap.add_argument("--grid", type=int, default=64)
    ap.add_argument("--velocity", type=float, default=1.5)
    ap.add_argument("--frames", type=int, default=250)
    ap.add_argument("--bins", type=int, default=12)
    ap.add_argument("--no-band", action="store_true",
                    help="drop sim_standing's upstream velocity band; the faithful "
                         "sim_channel.py recycle mode, run as a sensitivity arm")
    ap.add_argument("--allow-noncanonical-driver", action="store_true")
    args, passthrough = ap.parse_known_args()

    if args.selftest:
        _selftest()
        return
    for req in ("driver", "bc", "out", "label"):
        if getattr(args, req) is None:
            raise SystemExit("--%s is required" % req.replace("_", "-"))

    drv_sha = sha256(args.driver)
    if drv_sha != CANONICAL_DRIVER_SHA256 and not args.allow_noncanonical_driver:
        raise SystemExit(
            "REFUSED: driver sha256 %s is not the canonical %s that stamps the 17 "
            "published runs. A boundary-condition comparison against those runs is only "
            "meaningful on that driver. Pass --allow-noncanonical-driver to override, and "
            "say so in the write-up." % (drv_sha, CANONICAL_DRIVER_SHA256))

    cfg = {"bc": args.bc, "no_band": bool(args.no_band), "bins": int(args.bins)}
    mod = load_driver(args.driver)
    Scene, SolverCls, dropped = build_patched(mod, cfg)
    mod.StandingFloodScene = Scene
    if SolverCls is not None:
        mod.Solver = SolverCls

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("INFLOW bc=%s band=%s bins=%d" % (args.bc, "off" if args.no_band else "on",
                                            args.bins), flush=True)
    print("INFLOW driver=%s sha256=%s" % (args.driver, drv_sha), flush=True)
    print("INFLOW wrapper=%s sha256=%s" % (Path(__file__).resolve(), sha256(__file__)),
          flush=True)
    print("INFLOW bc_module_sha256=%s" % sha256(REPO / "simulation" / "openchannel_bc.py"),
          flush=True)
    print("INFLOW slurm_job_id=%s" % os.environ.get("SLURM_JOB_ID"), flush=True)

    sys.argv = [args.driver, "--label", args.label, "--out", str(out),
                "--depth", str(args.depth), "--grid", str(args.grid),
                "--velocity", str(args.velocity),
                "--frames", str(args.frames)] + passthrough
    print("INFLOW argv %s" % " ".join(sys.argv[1:]), flush=True)

    mod.main()

    # The scene object is local to mod.main(), so grab the one instance the patched class
    # recorded. Simpler and less fragile than threading a return value out of main().
    scene = Scene._last
    lim, dx = float(scene._lim), float(scene.dx)
    realized_depth = float(scene.h * len(np.arange(scene.floor + 0.5 * scene.h,
                                                   scene.floor + args.depth, scene.h)))
    pred = predict_reflection_frames(lim, dx, realized_depth)

    prof = np.asarray(scene.prof, dtype=float)
    centres = 0.5 * (np.linspace(scene.x_in, scene.x_out, args.bins + 1)[:-1] +
                     np.linspace(scene.x_in, scene.x_out, args.bins + 1)[1:])
    budget = scene.budget
    keys = ("n_below_floor", "n_out_xlo", "n_out_xhi", "n_out_ylo", "n_out_yhi",
            "n_out_any", "min_z", "x_min", "x_max")
    bud = {k: np.asarray([b[k] for b in budget], dtype=float) for k in keys}

    np.savez_compressed(
        out / "inflow_instrument.npz",
        depth_profile=prof.astype(np.float32),
        bin_centres=centres.astype(np.float32),
        recycled_per_frame=np.asarray(scene.recycled_per_frame, dtype=np.int64),
        tagged_near_vehicle=np.asarray(scene.tagged_near_vehicle, dtype=np.int64),
        tagged_total=np.asarray(scene.tagged_total, dtype=np.int64),
        veh_bbox=np.asarray(scene.veh_bbox, dtype=np.float32),
        water_x_span=np.asarray(scene.water_x_span, dtype=np.float32),
        **{"budget_" + k: v for k, v in bud.items()},
    )

    def slope_at(rows):
        late = np.nanmean(prof[rows], axis=0)
        fin = np.isfinite(late)
        if fin.sum() < 3:
            return float("nan"), float("nan"), int((~fin).sum())
        s = float(np.polyfit(centres[fin], late[fin], 1)[0])
        return s, float(np.nanmax(late) - np.nanmin(late)), int((~fin).sum())

    n = prof.shape[0]
    # PROFILE ROW f IS THE STATE AFTER FRAME f, so profile row f is metrics.csv row f+1.
    # The canonical horizon is metrics row 90, i.e. profile row 89, which is why the
    # pre-reflection window stops at 89 and not at 90.
    windows = {
        "pre_reflection_f60_89": range(60, min(90, n)),
        "post_reflection_f120_149": range(120, min(150, n)),
        "late_f220_249": range(220, min(250, n)),
    }
    slopes = {}
    for name, rows in windows.items():
        rr = [r for r in rows if r < n]
        if len(rr) < 2:
            continue
        sl, spread, drained = slope_at(rr)
        slopes[name] = {"slope_m_per_m": sl, "spread_m": spread,
                        "drained_bins": drained,
                        "profile_rows": [rr[0], rr[-1]]}

    nw = int(scene.n_water)
    summary = {
        "bc": args.bc, "band": (not args.no_band), "label": args.label,
        "frames": int(n), "n_water": nw, "n_grid": args.grid,
        "grid_lim_m": lim, "dx_m": dx, "wall_m": float(scene._wall),
        "floor_m": float(scene.floor), "x_in_m": scene.x_in, "x_out_m": scene.x_out,
        "realized_depth_m": realized_depth,
        "driver": str(args.driver), "driver_sha256": drv_sha,
        "wrapper_sha256": sha256(__file__),
        "bc_module_sha256": sha256(REPO / "simulation" / "openchannel_bc.py"),
        "bc_module_provenance": "simulation/openchannel_bc.py, blob from commit be1b138",
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "dropped_planes": dropped,
        "n_dropped_planes": len(dropped),
        "reflection_prediction": pred,
        "free_surface_slope": slopes,
        "recycled_total": int(scene.bc.recycled_total) if scene.bc else 0,
        "recycled_last_frame": int(scene.recycled_per_frame[-1]) if scene.recycled_per_frame else 0,
        "max_overshoot_m": float(scene.bc.max_overshoot) if scene.bc else 0.0,
        "tagged_frac_final": (float(scene.tagged_total[-1]) / nw) if scene.tagged_total else 0.0,
        "first_tagged_near_vehicle_frame": (
            int(np.argmax(np.asarray(scene.tagged_near_vehicle) > 0))
            if scene.tagged_near_vehicle and max(scene.tagged_near_vehicle) > 0 else None),
        "leaked_particle_frames_canonical_counter": int(scene.leaked),
        "budget_final": {k: float(bud[k][-1]) for k in keys},
        "budget_final_pct_of_water": {
            k: 100.0 * float(bud[k][-1]) / nw
            for k in ("n_below_floor", "n_out_xlo", "n_out_xhi", "n_out_ylo",
                      "n_out_yhi", "n_out_any")},
        "budget_at_frame_90": ({k: float(bud[k][90]) for k in keys} if n > 90 else None),
        "min_z_ever": float(np.nanmin(bud["min_z"])),
    }
    (out / "inflow_summary.json").write_text(json.dumps(summary, indent=2))
    print("INFLOW_SUMMARY " + json.dumps(summary), flush=True)
    print("INFLOW_DONE %s" % args.label, flush=True)


if __name__ == "__main__":
    main()
