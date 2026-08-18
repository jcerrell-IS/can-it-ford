"""Open-channel driver: closed-tank control vs recycling in/outflow, one script.

PURPOSE. The canonical scene is a closed box with an upstream velocity clamp
(renders/yaris_render_s1/sim_standing.py). Its _project_water clamps water into
[wall, lim-wall] on ALL THREE axes (:243-262), so nothing can leave, and its
_sustain_inflow only overwrites vx inside an upstream band (:264-272) without
creating a single particle. There is therefore no mass inflow and no outflow at
all, and the SCENARIO=STANDING_WATER_SUSTAINED_INFLOW label overstates what runs.

That is the bounded-domain artifact: water driven downstream has nowhere to go,
so it must pile against the downstream wall, and any slope signal is swamped by a
redistribution larger than itself.

This script runs BOTH conditions from one code path so the comparison is a
controlled one:
    --bc closed    x-normal walls present, x clamped, upstream velocity band
    --bc recycle   x-normal walls absent, x never clamped, outflow plane recycles
                   to the inflow plane (simulation/openchannel_bc.py)

and records the streamwise free-surface profile every frame, which is the
falsifiable discriminator: closed must ramp upward with x, recycle must not.

WHAT THIS IS NOT. --bc closed is a matched control INSIDE this script. It is not
a bit-reproduction of the 17 gated runs and must never be reported as one; those
remain sim_standing.py's, whose sha256 stamps them.

sim_standing.py is imported, never edited, so the mesh load, canonicalisation and
vehicle registry are literally the same objects the canonical runs used rather
than a fork that can drift.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from warpmpm.core.solver import GridConfig, Solver          # noqa: E402
from warpmpm.materials import newtonian                     # noqa: E402
from warpmpm.vehicle import FloodHistory, load_vehicle      # noqa: E402

from openchannel_bc import (                                # noqa: E402
    RecyclingChannelBC, depth_profile, tilted_gravity,
)
from image_particles import ImageParticleWall               # noqa: E402


def _load_canon(canon_dir=None):
    """Import the canonical driver for its mesh/registry helpers, lazily.

    Lazy and path-configurable on purpose. The Mac repo keeps sim_standing.py at
    renders/yaris_render_s1/ but Vista's copy that produced the g128 set lives at
    $WORK/render_s2/, so a hardcoded relative path is wrong on one machine or the
    other. Verified live 2026-08-18: $WORK/can-it-ford/renders/ does not exist.

    Only needed for --vehicle. A water-only channel never imports it, which keeps
    the BC validation independent of the vehicle path entirely.
    """
    cands = []
    if canon_dir:
        cands.append(Path(canon_dir))
    here = Path(__file__).resolve().parent
    cands += [here, here.parent / "renders" / "yaris_render_s1"]
    for c in cands:
        if (c / "sim_standing.py").is_file():
            if str(c) not in sys.path:
                sys.path.insert(0, str(c))
            import sim_standing
            return sim_standing
    raise SystemExit(
        "sim_standing.py not found in any of: %s. Pass --canon-dir."
        % ", ".join(str(c) for c in cands))


class ChannelScene:
    def __init__(self, depth, velocity, n_grid=64, vehicle=None, vehicle_mass=None,
                 lim=None, bc="recycle", grade_deg=0.0, water_density=1000.0,
                 water_eta=1.0e-3, bulk_modulus=1.5e5, fps=30, floor_friction=0.55,
                 settle_frames=8, device="auto", seed=0, inflow_len=1.5,
                 prescribe="full", n_image=0, floor_plane=True,
                 outflow_cells=4.0):
        if bc not in ("closed", "recycle"):
            raise ValueError("bc must be 'closed' or 'recycle'")
        self.bc_mode = bc
        self.fps = fps
        self.velocity = velocity
        self.grade_deg = float(grade_deg)

        if lim is None:
            if vehicle is None:
                raise ValueError("--lim is required when there is no vehicle")
            ext = vehicle.extent
            lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
        lim = float(lim)
        self.grid = GridConfig(n_grid=n_grid, grid_lim=lim)
        dx = self.grid.dx
        h = dx / 2.0                      # 8 particles per cell, matching Zhao et al's 8 PPE
        floor = 3.0 * dx
        wall = 4.0 * dx
        rng = np.random.default_rng(seed)

        xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        ys = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = (water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)).astype(np.float32)
        self.n_water_before_carve = len(water)
        self.n_carved = 0

        truck = None
        vehicle_density = None
        if vehicle is not None:
            if vehicle.spacing > 1.2 * h:
                vehicle.solidify(h)
            solid_volume = vehicle.n_particles * h ** 3
            vehicle_density = vehicle_mass / solid_volume
            self.vehicle_mass = vehicle_density * solid_volume
            vx, vy = 0.60 * lim, 0.50 * lim
            self._place = np.array([vx, vy, floor + 0.5 * h], dtype=np.float32)
            truck = vehicle.particles + self._place
            # same cell-occupancy carve the canonical scene uses
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
        else:
            self.vehicle_mass = 0.0
            self._place = None

        # Layout is water | images | vehicle. Images are ordinary fluid particles
        # to the solver, so every diagnostic below addresses water as [0, n_water)
        # and the vehicle as [n_veh0, n_total). Getting that wrong would fold the
        # image layer into the free surface and the passthrough fraction.
        self.n_water = len(water)
        self.n_image = int(n_image)
        blocks = [water]
        if self.n_image:
            img = np.repeat(water[:1], self.n_image, axis=0).astype(np.float32)
            img[:, 2] = floor - 0.5 * dx
            blocks.append(img)
        if truck is not None:
            blocks.append(truck)
        pos = np.concatenate(blocks) if len(blocks) > 1 else water
        vol = np.full(len(pos), h ** 3, dtype=np.float32)
        self.n_veh0 = self.n_water + self.n_image
        self.n_total = len(pos)

        s = Solver(grid=self.grid, device=device).load_particles(pos, vol)
        if s.sort_interval != 0:
            raise RuntimeError(
                "sort_interval=%d permutes particle identity; this driver addresses "
                "water as [0, n_water) and would silently mis-slice" % s.sort_interval)

        # Gravity. set_material writes {"material":..., "g":[0,0,-9.81], **params}
        # with **params LAST (solver.py:165-167), so a g here wins, and
        # set_parameters_dict honours it (mpm_solver_warp.py:742-743).
        self.gravity = tilted_gravity(grade_deg)
        s.set_material(newtonian(eta=water_eta, density=water_density,
                                 bulk_modulus=bulk_modulus), g=self.gravity)
        if truck is not None:
            s.set_material_range(self.n_veh0, self.n_total, "rigid", obj_id=0,
                                 density=vehicle_density)
            s.finalize_rigid_bodies()

        # floor_plane=False is the REPLACEMENT arm: Schulz and Sutmann's image
        # particles are meant to stand in for the momentum-zeroing wall, not to sit
        # on top of one. Keeping both tests augmentation; removing the plane tests
        # whether the image layer alone holds the water up. Both are run.
        self.floor_plane = bool(floor_plane)
        if self.floor_plane:
            s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
                        restitution=0.05)
        # Cross-stream walls in both modes. Streamwise walls ONLY in closed mode:
        # leaving them in would stop every particle before it reached the outflow
        # plane and the recycler would never fire.
        cross = (((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0)))
        stream = (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)))
        planes = cross + stream if bc == "closed" else cross
        for pt, nrm in planes:
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
        s.add_domain_walls()

        self.solver = s
        self.floor, self.h, self.dx = floor, h, dx
        self._wall, self._lim = wall, lim
        self.leaked = 0
        self.clamped_x = 0
        self.clamped_y = 0
        self.clamped_z = 0
        self._inflow_x = wall + inflow_len

        # Outflow one wall-thickness inside the domain, inflow at the upstream wall.
        # The outflow plane sits outflow_cells in from the downstream edge. The
        # default 4 reproduces every run in register items 20 and 24. It is a flag
        # because 4 cells leaves only 1.5 dx between x_out and the engine's P2G edge
        # guard, and the image-particle arms pushed WATER (not images) to x=9.064
        # against a guard limit of 9.054 and died before producing a summary. When
        # comparing arms, move it for ALL arms or the comparison is not controlled.
        self.x_in = wall
        self.x_out = lim - float(outflow_cells) * dx
        self.wall = None
        if self.n_image:
            # free_slip mirrors the canonical floor, which is add_plane(..., "slip").
            self.wall = ImageParticleWall(
                self.n_water, self.n_image, floor, dx, band_cells=1.0,
                mode="free_slip",
                safe_lo=np.array([2.0 * dx, 2.0 * dx, 2.0 * dx], np.float32),
                safe_hi=np.array([lim - 3.0 * dx, lim - 3.0 * dx, lim - 3.0 * dx],
                                 np.float32))
            xx, vv = s.x(), s.v()
            self.wall.park(xx, vv)
            s.set_x(xx); s.set_v(vv)

        self.bc = None
        if bc == "recycle":
            self.bc = RecyclingChannelBC(
                n_water=self.n_water, x_in=self.x_in, x_out=self.x_out,
                inlet_velocity=velocity, dx=dx, grid_lim=lim, prescribe=prescribe)

        c = float(np.sqrt(1.1 * bulk_modulus / water_density))
        self.term_acoustic = c / (0.28 * dx)
        self.term_viscous = 6.0 * water_eta / (water_density * dx * dx)
        self.term_advective = max(velocity, 1e-6) / (0.5 * dx)
        rate = max(self.term_acoustic, self.term_viscous, self.term_advective)
        self.sound_speed = c
        self.bulk_modulus = float(bulk_modulus)
        self.substeps = int(np.ceil(rate / fps))
        self.dt = (1.0 / fps) / self.substeps
        # Zhao et al reduce the water bulk modulus and require the numerical sound
        # speed to stay above 10x the maximum flow velocity (the Monaghan rule this
        # project already carries). Recorded, not assumed.
        self.mach_margin = c / max(velocity, 1e-9)

        self.settle_frames = int(settle_frames)
        for _ in range(self.settle_frames):
            self._project()
            s.step(self.dt, self.substeps)

        v = s.v()
        v[: self.n_water, 0] += velocity
        s.set_v(v)

        self.time = 0.0
        self.history = None
        if truck is not None:
            self.com0 = s.rigid_state()["com"].copy()
            self.history = FloodHistory()
            self.history.append(0.0, s.rigid_state(), self.com0)

    def _project(self):
        """Cross-stream containment. In closed mode x is clamped too, which is the
        artifact; in recycle mode x is never touched."""
        s = self.solver
        x = s.x()
        v = s.v()
        w = x[: self.n_water]
        vw = v[: self.n_water]
        eps = 0.25 * self.dx
        if self.bc_mode == "closed":
            lo = np.array([self._wall, self._wall, self.floor], dtype=np.float32) - eps
            hi = np.array([self._lim - self._wall, self._lim - self._wall, np.inf],
                          dtype=np.float32) + eps
        else:
            lo = np.array([-np.inf, self._wall - eps, self.floor - eps], dtype=np.float32)
            hi = np.array([np.inf, self._lim - self._wall + eps, np.inf], dtype=np.float32)
        out_lo = w < lo
        out_hi = w > hi
        if not (out_lo.any() or out_hi.any()):
            s.set_x(x)
            return
        self.leaked += int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
        # Per-axis. A single total cannot distinguish water escaping sideways from
        # water sinking through the floor, and in recycle mode x is never counted
        # because it is never clamped, so the two modes' totals are not comparable
        # until they are split.
        self.clamped_x += int(out_lo[:, 0].sum() + out_hi[:, 0].sum())
        self.clamped_y += int(out_lo[:, 1].sum() + out_hi[:, 1].sum())
        self.clamped_z += int(out_lo[:, 2].sum() + out_hi[:, 2].sum())
        np.clip(w, lo, hi, out=w)
        vw[out_lo] = np.maximum(vw[out_lo], 0.0)
        vw[out_hi] = np.minimum(vw[out_hi], 0.0)
        s.set_x(x)
        s.set_v(v)

    def _drive(self):
        """Streamwise forcing. closed: the canonical upstream velocity band.
        recycle: the outflow/inflow recycler."""
        s = self.solver
        x = s.x()
        v = s.v()
        if self.bc_mode == "closed":
            band = x[: self.n_water, 0] < self._inflow_x
            v[: self.n_water][band, 0] = self.velocity
            s.set_v(v)
            return int(band.sum())
        n = self.bc.apply(x, v)
        if n:
            s.set_x(x)
            s.set_v(v)
        return n

    def step(self):
        self._project()
        self.n_driven = self._drive()
        if self.wall is not None:
            xx, vv = self.solver.x(), self.solver.v()
            self.wall.apply(xx, vv)
            self.solver.set_x(xx); self.solver.set_v(vv)
        self.solver.step(self.dt, self.substeps)
        self.time += 1.0 / self.fps
        if self.history is not None:
            self.history.append(self.time, self.solver.rigid_state(), self.com0)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--bc", choices=("closed", "recycle"), required=True)
    p.add_argument("--depth", type=float, default=0.30)
    p.add_argument("--velocity", type=float, default=1.5)
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--grade-deg", type=float, default=0.0)
    p.add_argument("--eta", type=float, default=1.0e-3)
    p.add_argument("--floor-friction", type=float, default=0.55)
    p.add_argument("--settle-frames", type=int, default=8)
    p.add_argument("--vehicle", default=None,
                   help="yaris|rogue|silverado|path. Omit for a water-only channel.")
    p.add_argument("--mass", type=float, default=None)
    p.add_argument("--lim", type=float, default=None)
    p.add_argument("--bins", type=int, default=12)
    p.add_argument("--images", type=int, default=0,
                   help="image particles mirrored across the floor (0=off)")
    p.add_argument("--outflow-cells", type=float, default=4.0,
                   help="outflow plane distance from the downstream edge, in cells")
    p.add_argument("--no-floor-plane", action="store_true",
                   help="drop the grid-BC floor so the image layer IS the wall")
    p.add_argument("--dump-water", type=int, default=0,
                   help="dump water positions every N frames to rollout.npz (0=off)")
    p.add_argument("--prescribe", choices=("full", "streamwise"), default="full",
                   help="inlet velocity condition: full sets (U,0,0), streamwise sets vx only")
    p.add_argument("--canon-dir", default=None,
                   help="directory holding sim_standing.py (only for --vehicle)")
    a = p.parse_args()

    veh = None
    mass = None
    vkey = None
    if a.vehicle is not None:
        canon = _load_canon(a.canon_dir)
        vkey, vpath, ventry = canon.resolve_vehicle(a.vehicle)
        if not vpath.exists():
            raise SystemExit("PREFLIGHT FAIL hull not found: %s" % vpath)
        mass = a.mass if a.mass is not None else (ventry or {}).get("mass_kg")
        if mass is None:
            raise SystemExit("--mass is required for an unregistered --vehicle path")
        veh = canon.canonicalize(load_vehicle(vpath, up="z"))
        print("PREFLIGHT vehicle=%s hull=%s mass=%.1f" % (vkey, vpath, mass), flush=True)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    sc = ChannelScene(depth=a.depth, velocity=a.velocity, n_grid=a.grid, vehicle=veh,
                      vehicle_mass=mass, lim=a.lim, bc=a.bc, grade_deg=a.grade_deg,
                      water_eta=a.eta, floor_friction=a.floor_friction,
                      settle_frames=a.settle_frames, prescribe=a.prescribe,
                      n_image=a.images, floor_plane=not a.no_floor_plane,
                      outflow_cells=a.outflow_cells)

    print("SCENARIO=OPEN_CHANNEL bc=%s grade_deg=%.3f" % (a.bc, a.grade_deg), flush=True)
    print("INSTRUMENT dx=%.6f h=%.6f floor=%.6f lim=%.6f" % (sc.dx, sc.h, sc.floor, sc._lim),
          flush=True)
    print("INSTRUMENT n_water=%d n_total=%d layers=%d ppc=8"
          % (sc.n_water, sc.n_total,
             len(np.arange(sc.floor + 0.5 * sc.h, sc.floor + a.depth, sc.h))), flush=True)
    print("INSTRUMENT gravity=[%.5f, %.5f, %.5f] |g|=%.5f"
          % (sc.gravity[0], sc.gravity[1], sc.gravity[2],
             float(np.linalg.norm(sc.gravity))), flush=True)
    print("INSTRUMENT x_in=%.4f x_out=%.4f channel_len=%.4f"
          % (sc.x_in, sc.x_out, sc.x_out - sc.x_in), flush=True)
    print("SUBSTEP c=%.4f substeps=%d dt=%.3e mach_margin=%.2f (Zhao/Monaghan want >10)"
          % (sc.sound_speed, sc.substeps, sc.dt, sc.mach_margin), flush=True)

    prof_rows = []
    driven = []
    n0 = sc.n_water
    dump_w, dump_s, dump_f, dump_v = [], [], [], []
    frac_max = 0.0        # max water fraction inside the vehicle bbox = gates.py P-2
    for f in range(a.frames):
        sc.step()
        x = sc.solver.x()
        vel = sc.solver.v()
        w = x[:sc.n_water]
        centres, depths = depth_profile(w, sc.floor, sc.x_in, sc.x_out, n_bins=a.bins)
        prof_rows.append(depths)
        if a.dump_water and (f % a.dump_water == 0 or f == a.frames - 1):
            dump_w.append(w.astype(np.float32))
            dump_s.append(np.linalg.norm(vel[:sc.n_water], axis=1).astype(np.float32))
            dump_f.append(f)
            if sc.n_total > sc.n_veh0:
                dump_v.append(x[sc.n_veh0:].astype(np.float32))
        if sc.n_total > sc.n_veh0:
            veh = x[sc.n_veh0:]
            lo_v, hi_v = veh.min(0), veh.max(0)
            frac_max = max(frac_max, float(((w >= lo_v) & (w <= hi_v)).all(axis=1).mean()))
        driven.append(sc.n_driven)
        if f % 10 == 0 or f == a.frames - 1:
            fin = np.isfinite(depths)
            slope = np.nan
            if fin.sum() >= 3:
                slope = float(np.polyfit(centres[fin], depths[fin], 1)[0])
            print("frame %3d  driven=%5d  depth_lo=%.4f depth_hi=%.4f "
                  "spread=%.4f slope=%+.5f m/m  xmax=%.3f"
                  % (f, sc.n_driven, np.nanmin(depths), np.nanmax(depths),
                     np.nanmax(depths) - np.nanmin(depths), slope, float(w[:, 0].max())),
                  flush=True)

    if sc.history is not None:
        sc.history.to_csv(out / "metrics.csv")

    if a.dump_water:
        np.savez_compressed(
            out / "rollout.npz",
            water=np.asarray(dump_w, dtype=np.float32),
            speed=np.asarray(dump_s, dtype=np.float32),
            frames_dumped=np.asarray(dump_f, dtype=np.int32),
            vehicle=(np.asarray(dump_v, dtype=np.float32) if dump_v else np.zeros((0, 0, 3), np.float32)),
            lim=np.float32(sc._lim), dx=np.float32(sc.dx), h=np.float32(sc.h),
            floor=np.float32(sc.floor), x_in=np.float32(sc.x_in), x_out=np.float32(sc.x_out),
            depth=np.float32(a.depth), velocity=np.float32(a.velocity),
            grade_deg=np.float32(a.grade_deg), n_grid=np.int32(a.grid))

    prof = np.asarray(prof_rows)
    np.savetxt(out / "depth_profile.csv", prof, delimiter=",",
               header=",".join("bin%d" % i for i in range(prof.shape[1])), comments="")

    # Late-window average, so the discriminator is not read off a transient. The
    # window is reported, never assumed adequate: analysis/stationarity.py is the
    # tool that decides that, and it has not been run on this record.
    lo = max(0, int(0.6 * a.frames))
    late = np.nanmean(prof[lo:], axis=0)
    fin = np.isfinite(late)
    slope = float(np.polyfit(centres[fin], late[fin], 1)[0]) if fin.sum() >= 3 else float("nan")
    summary = {
        "scenario": "open_channel", "label": a.label, "bc": a.bc,
        "grade_deg": a.grade_deg, "gravity": sc.gravity,
        "depth_m": a.depth, "velocity_ms": a.velocity, "n_grid": a.grid,
        "frames": a.frames, "settle_frames": a.settle_frames,
        "grid_lim": float(sc._lim), "dx": float(sc.dx), "h": float(sc.h),
        "floor": float(sc.floor), "x_in": float(sc.x_in), "x_out": float(sc.x_out),
        "n_water": int(sc.n_water), "n_total": int(sc.n_total),
        "n_image": int(sc.n_image), "floor_plane": bool(sc.floor_plane),
        "image_sources_last": (int(sc.wall.sources_last) if sc.wall else 0),
        "image_duplicated_last": (int(sc.wall.duplicated_last) if sc.wall else 0),
        "image_clamped_total": (int(sc.wall.clamped_images) if sc.wall else 0),
        "n_carved": int(sc.n_carved), "vehicle_key": vkey,
        "vehicle_mass_kg": float(sc.vehicle_mass),
        "substeps": int(sc.substeps), "sound_speed_ms": float(sc.sound_speed),
        "mach_margin": float(sc.mach_margin),
        "particles_per_cell": 8,
        "late_window_start_frame": lo,
        "late_depth_by_bin": [None if not np.isfinite(d) else float(d) for d in late],
        "late_depth_slope_m_per_m": slope,
        "late_depth_spread_m": float(np.nanmax(late) - np.nanmin(late)),
        "driven_first": int(driven[0]), "driven_last": int(driven[-1]),
        "driven_total": int(np.sum(driven)),
        "recycled_total": int(sc.bc.recycled_total) if sc.bc else 0,
        "max_overshoot_m": float(sc.bc.max_overshoot) if sc.bc else 0.0,
        "leaked_particle_frames": int(sc.leaked),
        "clamped_x": int(sc.clamped_x), "clamped_y": int(sc.clamped_y),
        "clamped_z": int(sc.clamped_z),
        "prescribe": a.prescribe,
        "passthrough_max_frac": float(frac_max),
        "final_disp_mag_m": (float(np.linalg.norm(sc.history.displacement[-1]))
                             if sc.history is not None else None),
        "final_disp_m": ([float(q) for q in sc.history.displacement[-1]]
                         if sc.history is not None else None),
        "final_yaw_deg": (float(sc.history.yaw[-1]) if sc.history is not None else None),
        "final_roll_deg": (float(sc.history.roll[-1]) if sc.history is not None else None),
        "water_count_conserved": bool(sc.n_water == n0),
        # Zhao et al validate against Rouse's free overfall, where the critical depth
        # is about 1.4x the brink depth (their text, retrieved 2026-08-18 via Scite
        # full-text search of doi:10.1016/j.compfluid.2018.10.007). This run is the
        # UNIFORM channel case and does not test that ratio; the overfall case is not
        # implemented here.
        "zhao_overfall_ratio_tested": False,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s" % a.label, flush=True)


if __name__ == "__main__":
    main()
