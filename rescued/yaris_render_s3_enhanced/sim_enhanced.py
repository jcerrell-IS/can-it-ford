#!/usr/bin/env python3
"""Enhanced standing-flood driver. NEW FILE, derived from sim_standing.py, edits nothing.

PROVENANCE
----------
Derived from `renders/yaris_render_s1/sim_standing.py`, sha256 5215c38bed607ef6...,
verified 2026-08-07 to be BYTE-IDENTICAL to `$WORK/render_s2/sim_standing.py` on Vista,
i.e. the exact code that produced the 17 gated runs. `diff` the two files: that diff is
the audit trail and it is the only claim this file makes about its own correctness.

These runs are NOT canonical. They must never be merged into
`data/all_runs_inventory.csv`, `renders/yaris_render_s1/gates_results_all_runs.json`,
or any figure describing the 17 gated runs.

WHAT IS ENHANCED, AND WHY EACH ONE
----------------------------------
E1. `--bulk-modulus` is a parameter instead of a hardcoded 1.5e5.
    sim_standing.py takes bulk_modulus=1.5e5, giving c = 12.845 m/s against water's
    real 1481 m/s, two orders of magnitude low. CLAUDE.md records Isik and He 2022:
    artificial sound speed can qualitatively FLIP a rigid-body outcome. It has never
    been swept. This is the single largest un-probed physics knob in the project.
    BUG FIXED IN PASSING: sim_standing.py:355 writes `"bulk_modulus": 1.5e5` as a
    literal into summary.json rather than reading the value the scene used, so a
    parameterised run there would silently record the wrong number. Here it is
    threaded through from the actual scene attribute.

E2. Herschel-Bulkley / Bingham rheology via `--tau-y`, `--hb-k`, `--hb-n`.
    `kirchoff_stress_newtonian` (kernels/mpm_utils.py:32-54) already implements
    eta_app = eta + tau_y/gd + K*gd^(n-1) with gd floored at eps = 0.02. Proven to
    run: the 11-point ladder in analysis/bingham_sweep/ completed on this path.
    tau_y = 0 and hb_K = 0 recover the Newtonian baseline EXACTLY, because the
    `.with_*` calls are skipped entirely rather than applied with zero arguments.

E3. THE PAIRED CFL EDIT, which is not optional.
    sim_standing.py:149 computes term_viscous from the NEWTONIAN eta. The kernel's
    apparent viscosity is capped at eta + tau_y/0.02 + K*0.02^(n-1), which for a
    modest yield stress is orders of magnitude larger. The settle loop runs the water
    at rest, where the shear rate sits exactly on the eps floor by construction, so
    this is the FIRST thing that breaks, not a corner case. core/solver.py has no CFL
    check and no NaN guard, so the failure mode is silent degradation, not a crash.
    The 0.02 is deliberately inline and must NOT be lifted into a shared constant with
    mpm_utils.py:41: that kernel lives in a vendored engine at a pinned SHA, and a
    shared name would falsely imply that changing one changes the other. It is also
    NOT one of the 0.05 DRIFT_THRESHOLD literals in CLAUDE.md item 13.

E4. `--estimate` costs a configuration WITHOUT running the solver.
    Vista had 670 SUs left on 2026-08-07 expiring 2026-09-30, and substeps scale
    LINEARLY in sound speed, so a physical bulk modulus is a ~115x cost multiplier
    per frame on top of any grid refinement. Guessing here is how an allocation dies.
    Estimate first, then spend.

E5. Latent crash fixed. sim_standing.py:302 checkpoints frames (0, 45, frames-1) and
    :333 reads checkpoints["45"] unconditionally, so ANY run with frames <= 45 dies
    with KeyError at the very end, after all the compute is already spent. Here the
    mid checkpoint is frames//2 and the keys are written from the same variable.

E6. Resolution diagnostics promoted to first-class output.
    CLAUDE.md L-3: the g64 baseline has 4 water particle layers and exactly 2.000 grid
    cells per flow depth, against a rule of thumb of ~10 particles per depth. That is
    a stated limitation, not a converged resolution, and it should be visible in every
    run rather than recomputed by hand afterwards.

E7. Ground-clearance resolution reported per run.
    Ground clearance, not vehicle length, is the smallest force-bearing feature.
    Measured over 120 sampled columns of the canonical hull: median 0.180554 m,
    p10 0.161677 m, min 0.146952 m (analysis/verify_cpic_ground_clearance.py). At the
    g64 baseline that is 1.226 cells, i.e. sub-stencil for a 3-cell quadratic B-spline.
    See docs/limitations.md L-11 for why CPIC does NOT fix this.

E8. grid_lim is asserted against the recorded value, not trusted.
    sim_standing.py:82 reads `2.2*ext[1]` where `ext` is the extent AFTER
    load_vehicle(up="z") permutes axes, so the driver's ext[1] is the PLY's x. Taking
    the PLY axes at face value gives 14.989 m instead of the as-run 9.421742314 m, a
    59 percent error that silently rescales every dx. At the canonical geometry this
    file refuses to run if it does not reproduce the recorded number.

WHAT IS DELIBERATELY NOT CHANGED
--------------------------------
The rigid-particle zero-stress issue is NOT addressed here and cannot be from a
driver. mpm_utils.py:1100 initialises stress to a zero mat33, :1104 excludes mat 8
from the SVD, and no `mat == 8` branch in :1105-1147 ever assigns one, so the hull
exerts no pressure on the water. That is very likely the same defect as the P-2
pass-through failures, but that identification has NOT been tested and must not be
asserted. Fixing it means patching a vendored engine at a pinned SHA. Out of scope
for a driver; recorded so it is not mistaken for something this file solved.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

# --- ENGINE IMPORTS ARE DELIBERATELY LAZY. Do not hoist them back to module scope. ---
#
# Two independent reasons, both from recorded live findings:
#
# 1. `from warpmpm.vehicle import load_vehicle` BLOCKS on the Vista LOGIN node. Measured:
#    600 s wall for only 0.75 s of CPU, exit 124, against 78.9 s to completion on a
#    compute node. Near-zero CPU over ten minutes proves a blocking call, not contention.
#    `--estimate` is pure arithmetic and is meant to be run on a login node to cost a job
#    BEFORE spending SUs on it; a module-scope import would hang exactly there, which is
#    the one place it has to work.
#
# 2. The pip-installed warpmpm on the Mac lacks `solidify_watertight` entirely, so a
#    module-scope import of the vehicle module makes `--estimate` fail locally too.
#
# `solidify_watertight` is never imported: this driver does not call it directly
# (VehicleBody.solidify dispatches internally). The presence check that sim_standing.py:12
# was really performing via its import now lives in run_enhanced.py's
# bind_canonical_vehicle(), where it can act on the result instead of just crashing.
trimesh = None
GridConfig = Solver = newtonian = FloodHistory = load_vehicle = None


def _load_engine():
    """Import trimesh + warpmpm into module globals. Call ONLY on a compute node."""
    global trimesh, GridConfig, Solver, newtonian, FloodHistory, load_vehicle
    if Solver is not None:
        return
    import trimesh as _trimesh
    from warpmpm.core.solver import GridConfig as _GC, Solver as _S
    from warpmpm.materials import newtonian as _newt
    from warpmpm.vehicle import FloodHistory as _FH, load_vehicle as _LV
    trimesh = _trimesh
    GridConfig, Solver, newtonian, FloodHistory, load_vehicle = _GC, _S, _newt, _FH, _LV

# Published volume of the canonical Yaris hull (vehicle_geometry_research/
# WATERTIGHT_HULL_TOOL_FINDINGS.md), kept as a REFERENCE ANCHOR only.
# It must never be the fill_ratio denominator. Using it as one made every
# non-Yaris --vehicle run silently report the Yaris hull volume and a
# fill_ratio computed against the wrong denominator, while still looking
# plausible. Corrected 2026-08-08; see docs/MESH_RECONCILIATION_2026-08-08.md
# section 7. The live denominator is hull_m3, derived from the loaded mesh.
HULL_YARIS_REF = 3.542739

# Canonical anchors, from data/all_runs_inventory.csv row g64_m1100, read live 2026-08-07.
CANON_GRID_LIM = 9.421742313727737
CANON_DX = 0.1472147236519959

# Ground clearance of the canonical hull, from analysis/verify_cpic_ground_clearance.py
# over 120 sampled columns. Used for reporting only; nothing branches on it.
CLEARANCE_MEDIAN_M = 0.180554
CLEARANCE_MIN_M = 0.146952

# Kernel shear-rate regularisation floor, kernels/mpm_utils.py:41 and :51, at the pinned
# SHA 544c93dd. Inline on purpose: see E3 in the module docstring. NOT a DRIFT_THRESHOLD.
KERNEL_EPS = 0.02

REAL_WATER_C = 1481.0  # m/s, for reporting how far the artificial sound speed is off.


def canonicalize(v):
    """Verbatim from sim_standing.py:18-27. A repair, not a deviation.

    Upstream load_vehicle derives extent, shift and spacing from a 60k random surface
    sampling of a 327,212-vertex mesh rather than from the vertices. This rewrites them
    from the vertices. It leaves v.particles stale and unshifted, so the caller MUST
    re-solidify immediately; that is a live trap for any new driver.
    """
    mv = np.asarray(v.mesh.vertices, dtype=np.float64)
    lo, hi = mv.min(0), mv.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    mv = mv - shift
    v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces), process=False)
    v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
    v.extent = mv.max(0) - mv.min(0)
    v.spacing = float(v.extent.max()) / 32.0
    return v


def eta_cap_for(water_eta: float, tau_y: float, hb_K: float, hb_n: float) -> float:
    """Apparent viscosity ceiling the KERNEL can reach, at the regularisation floor.

    kernels/mpm_utils.py:32-54 computes
        gd      = sqrt(2*dev(D):dev(D) + eps^2),  eps = 0.02
        eta_app = eta + tau_y/gd + K*gd^(n-1)
    gd is floored at eps, so eta_app is capped at eta + tau_y/eps + K*eps^(n-1).
    The driver's own substep formula must use THIS, not the Newtonian eta. See E3.
    """
    return water_eta + tau_y / KERNEL_EPS + hb_K * KERNEL_EPS ** (hb_n - 1.0)


def cfl_terms(*, bulk_modulus, water_density, water_eta, tau_y, hb_K, hb_n,
              dx, velocity, fps):
    """Substep count from the driver's own CFL formula, with the eta_cap correction.

    Mirrors sim_standing.py:147-154 exactly EXCEPT that term_viscous uses eta_cap.
    Pure arithmetic, no solver, so --estimate can call it with no GPU and no mesh.
    """
    c = float(np.sqrt(1.1 * bulk_modulus / water_density))
    eta_cap = eta_cap_for(water_eta, tau_y, hb_K, hb_n)
    term_acoustic = c / (0.28 * dx)
    term_viscous = 6.0 * eta_cap / (water_density * dx * dx)
    term_advective = max(velocity, 1e-6) / (0.5 * dx)
    rate = max(term_acoustic, term_viscous, term_advective)
    substeps = int(np.ceil(rate / fps))
    return {
        "sound_speed_ms": c,
        "eta_cap_pas": eta_cap,
        "term_acoustic": term_acoustic,
        "term_viscous": term_viscous,
        "term_advective": term_advective,
        "rate": rate,
        "substeps": substeps,
        "dt": (1.0 / fps) / substeps,
        "limiter": max(
            (("acoustic", term_acoustic), ("viscous", term_viscous),
             ("advective", term_advective)), key=lambda kv: kv[1])[0],
    }


class EnhancedFloodScene:
    """sim_standing.StandingFloodScene with E1/E2/E3 applied. Everything else verbatim."""

    def __init__(self, vehicle, depth, velocity, vehicle_mass, n_grid=64,
                 water_density=1000.0, water_eta=1.0e-3, bulk_modulus=1.5e5,
                 tau_y=0.0, hb_K=0.0, hb_n=1.0,
                 fps=30, floor_friction=0.55, settle_frames=8, device="auto",
                 seed=0, inflow_len=1.5):
        self.vehicle = vehicle
        self.fps = fps
        self.velocity = velocity
        self.bulk_modulus = bulk_modulus          # E1: kept, so summary cannot lie
        self.water_density = water_density
        self.water_eta = water_eta
        self.tau_y, self.hb_K, self.hb_n = tau_y, hb_K, hb_n

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

        # E2. tau_y = 0 and hb_K = 0 must reproduce the Newtonian baseline EXACTLY, so
        # the .with_* calls are SKIPPED rather than applied with neutral arguments.
        mat = newtonian(eta=water_eta, density=water_density, bulk_modulus=bulk_modulus)
        if tau_y > 0.0:
            mat = mat.with_yield(tau_y)
        if hb_K > 0.0:
            mat = mat.with_powerlaw(K=hb_K, n=hb_n)
        s.set_material(mat)

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

        # E3. The paired CFL edit. term_viscous from eta_cap, never from water_eta.
        t = cfl_terms(bulk_modulus=bulk_modulus, water_density=water_density,
                      water_eta=water_eta, tau_y=tau_y, hb_K=hb_K, hb_n=hb_n,
                      dx=dx, velocity=velocity, fps=fps)
        self.cfl = t
        self.sound_speed = t["sound_speed_ms"]
        self.eta_cap = t["eta_cap_pas"]
        self.term_acoustic = t["term_acoustic"]
        self.term_viscous = t["term_viscous"]
        self.term_advective = t["term_advective"]
        self.substeps = t["substeps"]
        self.dt = t["dt"]

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

    # --- below here verbatim from sim_standing.py:169-214 -------------------------
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


def build_parser():
    p = argparse.ArgumentParser(
        description="Enhanced standing-flood driver. NOT canonical.")
    p.add_argument("--mass", type=float, default=1100.0)
    p.add_argument("--label", default="enhanced")
    p.add_argument("--out", default=None, help="required unless --estimate")
    p.add_argument("--depth", type=float, default=0.30)
    p.add_argument("--velocity", type=float, default=1.5)
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--eta", type=float, default=1.0e-3)
    p.add_argument("--floor-friction", type=float, default=0.55)
    p.add_argument("--vehicle", default=None, help="path to the watertight hull PLY")
    # E1
    p.add_argument("--bulk-modulus", type=float, default=1.5e5,
                   help="Pa. 1.5e5 -> c=12.845 m/s (as-run). 1.99e9 -> c=1481 m/s (real water).")
    # E2
    p.add_argument("--tau-y", type=float, default=0.0, help="Bingham yield stress, Pa")
    p.add_argument("--hb-k", type=float, default=0.0, help="Herschel-Bulkley consistency K")
    p.add_argument("--hb-n", type=float, default=1.0, help="Herschel-Bulkley exponent n")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--settle-frames", type=int, default=8)
    # E4
    p.add_argument("--estimate", action="store_true",
                   help="print CFL/cost for this config and exit WITHOUT running")
    p.add_argument("--allow-lim-drift", action="store_true",
                   help="bypass the E8 grid_lim anchor assertion (do not use casually)")
    return p


def estimate(a, dx=None):
    """E4. Cost a configuration with no solver, no GPU and no mesh load."""
    if dx is None:
        # Anchor on the RECORDED grid_lim, never on a re-derived one. See E8.
        dx = CANON_GRID_LIM / a.grid
    t = cfl_terms(bulk_modulus=a.bulk_modulus, water_density=1000.0,
                  water_eta=a.eta, tau_y=a.tau_y, hb_K=a.hb_k, hb_n=a.hb_n,
                  dx=dx, velocity=a.velocity, fps=a.fps)
    base = cfl_terms(bulk_modulus=1.5e5, water_density=1000.0, water_eta=1.0e-3,
                     tau_y=0.0, hb_K=0.0, hb_n=1.0,
                     dx=CANON_GRID_LIM / 64, velocity=1.5, fps=30)
    cells = (a.grid / 64.0) ** 3
    work = cells * (t["substeps"] / base["substeps"]) * (a.frames / 90.0)
    print("=" * 74)
    print("ESTIMATE  grid=%d  depth=%.3f  vel=%.2f  frames=%d" %
          (a.grid, a.depth, a.velocity, a.frames))
    print("  dx                 = %.9f m   (grid_lim %.9f / %d)" % (dx, dx * a.grid, a.grid))
    print("  bulk_modulus       = %.4g Pa" % a.bulk_modulus)
    print("  sound speed c      = %.4f m/s   (real water %.1f, ratio %.4g)" %
          (t["sound_speed_ms"], REAL_WATER_C, REAL_WATER_C / t["sound_speed_ms"]))
    print("  tau_y=%.4g  K=%.4g  n=%.4g  ->  eta_cap = %.6g Pa.s" %
          (a.tau_y, a.hb_k, a.hb_n, t["eta_cap_pas"]))
    print("  CFL terms          : acoustic=%.4f  viscous=%.6f  advective=%.4f" %
          (t["term_acoustic"], t["term_viscous"], t["term_advective"]))
    print("  limiting term      = %s" % t["limiter"])
    print("  substeps/frame     = %d      (as-run g64 baseline = %d)" %
          (t["substeps"], base["substeps"]))
    print("  dt                 = %.4e s" % t["dt"])
    print("  cells vs g64       = %.3fx" % cells)
    print("  substeps vs g64    = %.3fx" % (t["substeps"] / base["substeps"]))
    print("  TOTAL WORK vs the g64/90-frame baseline = %.2fx" % work)
    depth_cells = a.depth / dx
    print("  resolution         : %.3f grid cells per flow depth   (rule of thumb ~10 particles)" %
          depth_cells)
    print("                       %.3f cells across median ground clearance %.6f m" %
          (CLEARANCE_MEDIAN_M / dx, CLEARANCE_MEDIAN_M))
    print("                       %.3f cells across MINIMUM clearance %.6f m" %
          (CLEARANCE_MIN_M / dx, CLEARANCE_MIN_M))
    # Measured wall-clock model, calibrated on Vista GH200 job 895330, 2026-08-07.
    # An earlier version of this function warned that >500 substeps/frame was "not
    # affordable on 670 SUs". That was REFUTED by measurement: the whole 3-stage ladder,
    # including a 156-substep g96 run, completed in 2 min 09 s of job elapsed time.
    # Two calibration points at g96 / 90 frames / 209,871 particles:
    #     16 substeps -> 5.5 s      156 substeps -> 30.0 s
    # giving wall ~= 2.7 + 0.175 * substeps seconds at g96, scaled by the cell ratio.
    # The linear-in-substeps part dominates; the intercept is launch and JIT warmup,
    # which is why the FIRST run of a job looks anomalously slow (g64 took 13.4 s for
    # only 11 substeps) and why raw work-ratios over-predict for short runs.
    cell_scale = (a.grid / 96.0) ** 3
    wall_s = (2.7 + 0.175 * t["substeps"]) * cell_scale * (a.frames / 90.0)
    print("  est. wall (GH200)  = %.0f s  (~%.1f min)  [calibrated on job 895330]"
          % (wall_s, wall_s / 60.0))
    if wall_s > 3600:
        print("  NOTE: over 1 h on one node. Still affordable against 670 SUs, but raise")
        print("        the sbatch -t limit and check the queue before submitting.")
    print("=" * 74)
    return t, work


def main():
    a = build_parser().parse_args()

    if a.estimate:
        estimate(a)
        return

    if not a.out:
        raise SystemExit("--out is required unless --estimate is given")
    if not a.vehicle:
        raise SystemExit("--vehicle is required (path to the watertight hull PLY)")

    # Past this point we are committed to a real run, so the engine may be imported.
    # This is the line that hangs for 600 s on a Vista login node. Compute nodes only.
    _load_engine()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    v1 = canonicalize(load_vehicle(Path(a.vehicle), up="z"))
    v2 = canonicalize(load_vehicle(Path(a.vehicle), up="z"))

    # Hull volume of the mesh ACTUALLY loaded via --vehicle, not a Yaris literal.
    # canonicalize() applies a pure translation, so mesh volume is invariant under it.
    # abs() guards an inverted winding, which trimesh reports as a negative volume.
    hull_m3 = float(abs(v1.mesh.volume))
    hull_watertight = bool(v1.mesh.is_watertight)
    hull_ref_delta_pct = 100.0 * (hull_m3 - HULL_YARIS_REF) / HULL_YARIS_REF

    h_probe = float(max(2.2 * v1.extent[1], 3.5 * v1.extent[0], 6.0 * a.depth)) / a.grid / 2.0
    v1.solidify(h_probe)
    v2.solidify(h_probe)
    lim1 = float(max(2.2 * v1.extent[1], 3.5 * v1.extent[0], 6.0 * a.depth))
    lim2 = float(max(2.2 * v2.extent[1], 3.5 * v2.extent[0], 6.0 * a.depth))
    print("DETERMINISM load1 n=%d lim=%.9f" % (v1.n_particles, lim1), flush=True)
    print("DETERMINISM load2 n=%d lim=%.9f" % (v2.n_particles, lim2), flush=True)
    det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
    print("DETERMINISM identical=%s" % det_ok, flush=True)

    # E8. Refuse to run if the loaded geometry does not reproduce the lim implied by its
    # OWN extents. GENERALISED 2026-08-08. The previous form compared against the Yaris
    # literal CANON_GRID_LIM unconditionally, so ANY non-Yaris --vehicle hit ANCHOR FAIL
    # and the only escape was --allow-lim-drift, which switches the axis-trap guard OFF
    # entirely. That was a false choice: a Rogue legitimately gives lim 10.442536068 and
    # a Silverado 13.067932987, both correct. Deriving the expectation from the mesh's
    # own sorted extents still catches the axis trap, because a permuted axis changes
    # which extent feeds which term and so moves the derived lim too, and it now catches
    # it for EVERY hull rather than only the canonical one. The guard gets STRONGER here.
    # Height is the smallest extent on all three qualified hulls, so sorting ascending
    # puts the long horizontal at [-1] and the short horizontal at [-2].
    ext_sorted = np.sort(np.abs(np.asarray(v1.mesh.extents, dtype=np.float64)))
    exp_lim = max(2.2 * float(ext_sorted[-1]), 3.5 * float(ext_sorted[-2]), 6.0 * a.depth)
    drift_own = abs(lim1 - exp_lim)
    print("ANCHOR grid_lim=%.9f expected_from_mesh=%.9f drift=%.3e"
          % (lim1, exp_lim, drift_own), flush=True)
    if drift_own > 1e-6 and not a.allow_lim_drift:
        raise SystemExit(
            "ANCHOR FAIL: grid_lim %.9f != %.9f implied by this hull's own extents. "
            "This is the axis trap: load_vehicle(up='z') permutes axes, so ext[1] is "
            "the PLY's x. Taking the PLY axes at face value gives 14.989 m for the "
            "Yaris instead of 9.421742314 m, a 59 percent error that silently rescales "
            "every dx. Fix the geometry path; do not pass --allow-lim-drift."
            % (lim1, exp_lim))

    # The canonical Yaris must ALSO still hit the recorded literal, so the original
    # 17-run anchor is preserved exactly, unchanged, for the canonical case.
    if abs(a.depth - 0.30) < 1e-12 and abs(hull_m3 - HULL_YARIS_REF) < 1e-4:
        drift = abs(lim1 - CANON_GRID_LIM)
        print("ANCHOR canonical_yaris grid_lim=%.9f recorded=%.9f drift=%.3e"
              % (lim1, CANON_GRID_LIM, drift), flush=True)
        if drift > 1e-6 and not a.allow_lim_drift:
            raise SystemExit(
                "ANCHOR FAIL: canonical Yaris grid_lim %.9f != recorded %.9f."
                % (lim1, CANON_GRID_LIM))

    estimate(a, dx=lim1 / a.grid)

    v = v1
    t0 = time.time()
    scene = EnhancedFloodScene(v, depth=a.depth, velocity=a.velocity,
                               vehicle_mass=a.mass, n_grid=a.grid,
                               water_eta=a.eta, floor_friction=a.floor_friction,
                               bulk_modulus=a.bulk_modulus,
                               tau_y=a.tau_y, hb_K=a.hb_k, hb_n=a.hb_n,
                               fps=a.fps, settle_frames=a.settle_frames)
    print("SETUP %.1f s" % (time.time() - t0), flush=True)

    lim = scene.grid.grid_lim
    dx, h, floor = scene.dx, scene.h, scene.floor
    n_water = scene.n_water
    n_veh = scene.n_total - n_water
    solid_volume = n_veh * h ** 3
    layers = int(len(np.arange(floor + 0.5 * h, floor + a.depth, h)))
    gridline = ("grid %d^3 lim=%.2fm  water %d + vehicle %d particles (%.1f kg)  "
                "dt=%.2e (%d substeps/frame)"
                % (a.grid, lim, n_water, n_veh, scene.vehicle_mass, scene.dt, scene.substeps))
    print("SCENARIO=ENHANCED_STANDING_WATER_SUSTAINED_INFLOW", flush=True)
    print(gridline, flush=True)
    print("INSTRUMENT dx=%.6f h=%.6f floor=%.6f lim=%.6f" % (dx, h, floor, lim), flush=True)
    print("INSTRUMENT water_layers=%d cells_per_depth=%.4f" % (layers, a.depth / dx), flush=True)
    print("INSTRUMENT clearance_cells_median=%.4f clearance_cells_min=%.4f"
          % (CLEARANCE_MEDIAN_M / dx, CLEARANCE_MIN_M / dx), flush=True)
    print("INSTRUMENT solid_volume=%.5f m3 hull=%.5f fill_ratio=%.4f realized_rho=%.2f"
          % (solid_volume, hull_m3, solid_volume / hull_m3,
             scene.vehicle_mass / solid_volume), flush=True)
    # Hull provenance. yaris_ref_delta_pct is the tripwire that --vehicle took effect:
    # ~0 percent is the Yaris, ~+39.7 the Rogue, ~+124.7 the Silverado.
    print("INSTRUMENT hull_source=%s hull_m3=%.6f watertight=%s yaris_ref_delta_pct=%+.3f"
          % (a.vehicle, hull_m3, hull_watertight, hull_ref_delta_pct), flush=True)
    print("INSTRUMENT carved %d of %d water particles from vehicle cells (%.2f percent)"
          % (scene.n_carved, scene.n_water_before_carve,
             100.0 * scene.n_carved / max(scene.n_water_before_carve, 1)), flush=True)
    print("SUBSTEP_TERMS eta=%.3e eta_cap=%.6g acoustic=%.4f viscous=%.6f advective=%.4f "
          "limiter=%s substeps=%d"
          % (a.eta, scene.eta_cap, scene.term_acoustic, scene.term_viscous,
             scene.term_advective, scene.cfl["limiter"], scene.substeps), flush=True)
    print("ACOUSTIC c=%.4f m/s (real water %.1f, off by %.4gx)"
          % (scene.sound_speed, REAL_WATER_C, REAL_WATER_C / scene.sound_speed), flush=True)
    print("RHEOLOGY tau_y=%.6g K=%.6g n=%.6g bulk_modulus=%.6g"
          % (a.tau_y, a.hb_k, a.hb_n, a.bulk_modulus), flush=True)

    pv0 = np.asarray(v.particles, dtype=np.float64)
    W, S, RR, TT = [], [], [], []
    ld_bow, ld_foot = [], []
    oob_total = 0
    frac_max = 0.0
    zmin_start = float(scene.solver.x()[n_water:][:, 2].min())

    # E5. Mid checkpoint from a variable, so frames <= 45 cannot KeyError at the end.
    f_mid = max(0, min(a.frames // 2, a.frames - 1))
    ck_frames = sorted({0, f_mid, a.frames - 1})
    checkpoints = {}

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
        if f in ck_frames:
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
            print("frame %3d  |d|=%7.2fcm  yaw=%+6.2f  roll=%+6.2f  ld_bow=%.4f "
                  "ld_foot=%.4f oob=%d inflow=%d  [%.1fs]"
                  % (f, float(np.linalg.norm(dd)) * 100, scene.history.yaw[-1],
                     scene.history.roll[-1], ld_bow[-1], ld_foot[-1], oob_total,
                     getattr(scene, "n_inflow", -1), time.time() - t0), flush=True)

    wall_s = time.time() - t0
    scene.history.to_csv(out / "metrics.csv")
    np.savez_compressed(
        out / "rollout.npz",
        water=np.asarray(W, dtype=np.float32), speed=np.asarray(S, dtype=np.float32),
        R=np.asarray(RR, dtype=np.float32), t=np.asarray(TT, dtype=np.float32),
        veh_particles_scene0=checkpoints[str(ck_frames[0])],
        veh_check_mid=checkpoints[str(f_mid)],
        veh_check_last=checkpoints[str(a.frames - 1)],
        veh_particles_vehframe=pv0.astype(np.float32),
        local_depth_bow=np.asarray(ld_bow, dtype=np.float32),
        local_depth_footprint=np.asarray(ld_foot, dtype=np.float32),
        extent=np.asarray(v.extent, dtype=np.float32),
        lim=np.float32(lim), dx=np.float32(dx), h=np.float32(h), floor=np.float32(floor),
        depth=np.float32(a.depth), velocity=np.float32(a.velocity),
        mass=np.float32(scene.vehicle_mass), n_grid=np.int32(a.grid),
        frames=np.int32(a.frames), fps=np.int32(scene.fps),
        checkpoint_frames=np.asarray(ck_frames, dtype=np.int32),
    )

    d = scene.history.displacement[-1]
    veh_last = scene.solver.x()[n_water:]
    ldb = np.asarray(ld_bow); ldf = np.asarray(ld_foot)
    pk = int(np.nanargmax(ldb))
    summary = {
        "scenario": "enhanced_standing_water_sustained_inflow",
        "NOT_CANONICAL": "Enhanced-physics run, not one of the 17 gated runs",
        "derived_from": "renders/yaris_render_s1/sim_standing.py sha256 5215c38bed607ef6",
        "label": a.label, "mass_kg": float(scene.vehicle_mass),
        "depth_m": a.depth, "velocity_ms": a.velocity, "n_grid": a.grid,
        "frames": a.frames, "grid_lim": float(lim), "dx": float(dx), "h": float(h),
        "water_layers": layers, "cells_per_depth": float(a.depth / dx),
        "clearance_cells_median": float(CLEARANCE_MEDIAN_M / dx),
        "clearance_cells_min": float(CLEARANCE_MIN_M / dx),
        "n_water": int(n_water), "n_vehicle": int(n_veh),
        "n_carved": scene.n_carved, "water_eta": a.eta,
        "floor_friction": a.floor_friction,
        # E1: read from the scene, never a literal. sim_standing.py:355 hardcoded this.
        "bulk_modulus": float(scene.bulk_modulus),
        "tau_y_pa": float(a.tau_y), "hb_K": float(a.hb_k), "hb_n": float(a.hb_n),
        "eta_cap_pas": float(scene.eta_cap),
        "cfl_limiter": scene.cfl["limiter"],
        "substeps": int(scene.substeps), "dt": float(scene.dt),
        "sound_speed_ms": float(scene.sound_speed),
        "sound_speed_error_factor": float(REAL_WATER_C / scene.sound_speed),
        "term_acoustic": float(scene.term_acoustic),
        "term_viscous": float(scene.term_viscous),
        "term_advective": float(scene.term_advective),
        "solid_volume_m3": float(solid_volume), "hull_m3": hull_m3,
        "fill_ratio": float(solid_volume / hull_m3),
        "hull_source": str(a.vehicle),
        "hull_watertight": hull_watertight,
        "hull_yaris_ref_m3": HULL_YARIS_REF,
        "hull_ref_delta_pct": float(hull_ref_delta_pct),
        "realized_rho": float(scene.vehicle_mass / solid_volume),
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
        "wall_seconds": wall_s,
        "grid_lim_line_verbatim": gridline,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s in %.1f s" % (a.label, wall_s), flush=True)


if __name__ == "__main__":
    main()
