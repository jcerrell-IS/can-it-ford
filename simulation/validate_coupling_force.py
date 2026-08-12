from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch
import warp as wp

from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian

LIM = 9.421742313727737
DX_CANON = LIM / 64.0
L_BOX = 10.0 * DX_CANON
RHO_W = 1000.0
BULK = 1.5e5
ETA = 1.0e-3
G = 9.81
GAMMA = 1.1
FPS = 30.0

PROVENANCE = {
    "register_item": "J.1",
    "solver_source": "third_party/mpm-engine-544c93dd-solver-core/",
    "pinned_sha": "544c93dd02cb9c7ead89e1155a62967243244fce",
    "no_force_accessor": "core/solver.py:200-210 rigid_state returns com/v/omega/R only; register A3",
    "gravity": "core/solver.py:167-169 hardcodes g=[0,0,-9.81]; applied on grid at kernels/mpm_utils.py:940",
    "rigid_integrator": "kernels/mpm_utils.py:1416-1459 v_cm = rigid_linear_mom / M, no force term",
    "rigid_no_stress": "kernels/mpm_utils.py:1090-1091 F=I for mat 8, no stress branch assigns mat 8",
    "eos": "kernels/mpm_utils.py:43 pressure = -bulk*(J**-1.1 - 1), gamma=1.1",
    "plane_rigid_gate": "kernels/mpm_solver_warp.py:1915 'if restitution != 0.0' registers rigid contact",
    "deviation_from_canonical": "all planes use restitution=0.0 and friction=0.0 so they act on water only",
    "internal_access": "pin() writes _sim.rigid_x_cm and calls _sim.set_rigid_body_velocity; Solver exposes no pin API",
    "rigid_mass_is_particle_sum": "kernels/mpm_solver_warp.py:856 mass_np[b] = m_b.sum(); with v_cm = mom/M this makes the body adopt a mass-weighted AVERAGE grid velocity, never a force",
    "collider_wrench_sign": "core/solver.py:305-307 a static cup of m kg reads (0,0,-m*g), so buoyancy on a submerged collider is +z",
    "sdf_impulse": "kernels/mpm_solver_warp.py:2731-2734 impulse = m*(v_free - v_new), accumulated before the node velocity is overwritten",
    "box_impulse": "kernels/mpm_solver_warp.py:2082-2085 same accounting for the axis-aligned box collider; solver.py:358 calls sdf_wrench its 6-DOF analogue",
    "coupling_pkg_unused": "warpmpm.coupling (admittance/wrench/backend) is imported by warpmpm/__init__.py but never called here; it drives add_box tool handles, not material-8 rigid bodies",
}


def sound_speed(bulk=BULK, rho=RHO_W):
    return math.sqrt(GAMMA * bulk / rho)


def substeps_and_dt(dx, eta=ETA, rho=RHO_W, bulk=BULK, fps=FPS):
    c = sound_speed(bulk, rho)
    term_acoustic = c / (0.28 * dx)
    term_viscous = 6.0 * eta / (rho * dx * dx)
    term_advective = 1.0e-6 / (0.5 * dx)
    rate = max(term_acoustic, term_viscous, term_advective)
    substeps = int(math.ceil(rate / fps))
    return substeps, (1.0 / fps) / substeps


def draft_incompressible(rho_box, length=L_BOX, rho_w=RHO_W):
    return length * rho_box / rho_w


def eos_b(rho_w=RHO_W, bulk=BULK, g=G):
    return (GAMMA - 1.0) * rho_w * g / (GAMMA * bulk)


def draft_compressible(rho_box, length=L_BOX, rho_w=RHO_W, bulk=BULK, g=G):
    b = eos_b(rho_w, bulk, g)
    n1 = 1.0 / (GAMMA - 1.0) + 1.0
    r = length * rho_box / rho_w
    return ((1.0 + n1 * b * r) ** (1.0 / n1) - 1.0) / b


def hydrostatic_density(zeta, rho_w=RHO_W, bulk=BULK, g=G):
    b = eos_b(rho_w, bulk, g)
    return rho_w * (1.0 + b * zeta) ** (1.0 / (GAMMA - 1.0))


def tank_geometry(n_grid, depth_cells):
    dx = LIM / n_grid
    h = dx / 2.0
    floor = 3.0 * DX_CANON
    wall = 4.0 * DX_CANON
    span = LIM - 2.0 * wall
    nx = int(round(span / h))
    depth = depth_cells * DX_CANON
    nz = int(round(depth / h))
    n_side = int(round(L_BOX / h))
    jitter = 0.2 * h
    lat_max = wall + (nx - 0.5) * h + jitter
    lat_min = wall + 0.5 * h - jitter
    guard_lo = 1.5 * dx
    guard_hi = LIM - 2.5 * dx
    return {
        "dx": dx,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "guard_lo": guard_lo,
        "guard_hi": guard_hi,
        "guard_ok": bool(lat_min > guard_lo and lat_max < guard_hi),
        "h": h,
        "floor": floor,
        "wall": wall,
        "span": span,
        "nx": nx,
        "nz": nz,
        "n_side": n_side,
        "depth": depth,
        "a_tank": (nx * h) ** 2,
        "n_water_lattice": nx * nx * nz,
        "n_box": n_side ** 3,
    }


def cube_mesh(length):
    """Watertight axis-aligned cube of side `length`, centred on the ORIGIN.

    add_sdf_collider stores the field in the BODY frame and queries it as
    body = quat_rotate_inv(quat, x_world - center) (mpm_solver_warp.py:2697-2703),
    so the mesh must be origin-centred and the world placement passed as `center`.
    Faces are wound outward; build_sdf re-fixes the global sign from an interior
    probe anyway (mesh_sdf.py:356-358), the centroid, which is inside a cube.
    """
    a = 0.5 * float(length)
    verts = np.array([[-a, -a, -a], [+a, -a, -a], [+a, +a, -a], [-a, +a, -a],
                      [-a, -a, +a], [+a, -a, +a], [+a, +a, +a], [-a, +a, +a]],
                     dtype=float)
    faces = np.array([[0, 2, 1], [0, 3, 2],      # z = -a
                      [4, 5, 6], [4, 6, 7],      # z = +a
                      [0, 1, 5], [0, 5, 4],      # y = -a
                      [1, 2, 6], [1, 6, 5],      # x = +a
                      [2, 3, 7], [2, 7, 6],      # y = +a
                      [3, 0, 4], [3, 4, 7]],     # x = -a
                     dtype=np.int64)
    return verts, faces


def sdf_margin_cells(length, dx, res, band_safety=2.0):
    """Smallest margin_cells whose SDF-grid margin clears the collider contact band.

    add_sdf_collider defaults band = dx and REFUSES the collider if the minimum stored
    SDF value on the grid's six faces does not exceed it (mpm_solver_warp.py:2634-2645),
    because near-surface space outside the stored box would then get no constraint.
    build_sdf sets cell = span/(res-1-2*margin) (mesh_sdf.py:346), so the margin distance
    is margin*span/(res-1-2*margin); requiring that to reach band_safety*dx and solving
    for margin gives the expression below. At build_sdf's own defaults (res=64,
    margin_cells=4) the margin is 0.0727*L = 0.107 m against band = dx = 0.147 m at
    g64, so the DEFAULTS RAISE. This is chosen to satisfy the engine's own guard, not
    tuned against any measured value.
    """
    m = band_safety * dx * (res - 1) / (length + 2.0 * band_safety * dx)
    margin = int(math.ceil(m))
    if res - 1 - 2 * margin < 8:
        raise ValueError(
            f"sdf_res={res} too small: margin_cells={margin} needed to clear a "
            f"band of {band_safety}*dx={band_safety * dx:.4f} m leaves only "
            f"{res - 1 - 2 * margin} cells across the mesh. Raise --sdf-res.")
    return margin


def build_box_sdf(length, dx, res=64, band_safety=2.0):
    """Build the cube SDF and return (SDFData, provenance dict)."""
    from warpmpm.geometry import build_sdf

    verts, faces = cube_mesh(length)
    margin = sdf_margin_cells(length, dx, res, band_safety)
    sdf = build_sdf(verts, faces, res=res, margin_cells=float(margin))
    vals = np.asarray(sdf.values)
    boundary_min = float(min(vals[0].min(), vals[-1].min(),
                             vals[:, 0, :].min(), vals[:, -1, :].min(),
                             vals[:, :, 0].min(), vals[:, :, -1].min()))
    return sdf, {
        "sdf_res": int(res),
        "sdf_margin_cells": margin,
        "sdf_cell_m": float(sdf.cell),
        "sdf_cell_over_dx": float(sdf.cell) / dx,
        "sdf_boundary_min_m": boundary_min,
        "sdf_band_m": dx,
        "sdf_band_clearance": boundary_min / dx,
        "sdf_max": float(sdf.sdf_max),
    }


class BoxTank:
    def __init__(self, n_grid, rho_box, depth_cells, box_bottom, water=True,
                 seed=0, device="auto", box_mode="rigid", sdf_res=64,
                 sdf_band_safety=2.0):
        # box_mode: "rigid"        free rigid MPM body (material 8), the C0-C3 path
        #           "collider_sdf" the same cube as a FIXED mesh-SDF collider
        #           "collider_box" the same cube as a FIXED axis-aligned box collider
        # The collider modes create NO box particles: the cube is a boundary condition,
        # so the reaction wrench is materialised on the grid instead of being inferred
        # from the body's motion. Water seeding, carve, planes, walls, dt and substeps
        # are byte-identical across all three.
        if box_mode not in ("rigid", "collider_sdf", "collider_box"):
            raise ValueError(f"unknown box_mode {box_mode!r}")
        self.box_mode = box_mode
        self.collider = None
        self.n_grid = int(n_grid)
        geo = tank_geometry(self.n_grid, depth_cells)
        self.dx = geo["dx"]
        self.h = geo["h"]
        self.floor = geo["floor"]
        self.wall = geo["wall"]
        self.rho_box = float(rho_box)
        self.box_bottom0 = float(box_bottom)
        h = self.h

        if water and not geo["guard_ok"]:
            raise ValueError(
                f"n_grid={self.n_grid}: water lattice spans "
                f"[{geo['lat_min']:.4f}, {geo['lat_max']:.4f}] m but the P2G edge guard "
                f"requires ({geo['guard_lo']:.4f}, {geo['guard_hi']:.4f}) m for dx={geo['dx']:.4f}. "
                f"wall is fixed at 4*DX_CANON to keep geometry invariant across the "
                f"refinement step, so only n_grid >= 64 satisfies this.")

        n_side = geo["n_side"]
        if not math.isclose(n_side * h, L_BOX, rel_tol=1e-12):
            raise ValueError(f"box side {L_BOX} is not an integer multiple of h={h}")
        self.n_side = n_side
        self.length = n_side * h

        off = (np.arange(n_side) + 0.5) * h
        bx = LIM / 2.0 - self.length / 2.0
        self.box_x0 = bx
        if self.box_mode == "rigid":
            gx, gy, gz = np.meshgrid(off + bx, off + bx, off + box_bottom, indexing="ij")
            box = np.stack([gx, gy, gz], -1).reshape(-1, 3)
        else:
            box = np.zeros((0, 3))
        # centre of the cube the water is carved against; the collider surface is placed
        # on that same cube so the excluded volume is identical in all three modes.
        self.box_center = (LIM / 2.0, LIM / 2.0, float(box_bottom) + self.length / 2.0)

        nx = geo["nx"]
        self.a_tank = geo["a_tank"]

        if water:
            depth = geo["depth"]
            nz = geo["nz"]
            xs = self.wall + (np.arange(nx) + 0.5) * h
            zs = self.floor + (np.arange(nz) + 0.5) * h
            wx, wy, wz = np.meshgrid(xs, xs, zs, indexing="ij")
            w = np.stack([wx, wy, wz], -1).reshape(-1, 3)
            rng = np.random.default_rng(seed)
            w = w + rng.uniform(-0.2 * h, 0.2 * h, w.shape)
            lo = np.array([bx, bx, box_bottom])
            hi = lo + self.length
            inside = np.all((w >= lo) & (w <= hi), axis=1)
            self.n_carved = int(inside.sum())
            w = w[~inside]
            self.water_depth = depth
            self.n_water_layers = nz
        else:
            w = np.zeros((0, 3))
            self.n_carved = 0
            self.water_depth = 0.0
            self.n_water_layers = 0

        self.n_water = len(w)
        pos = np.concatenate([w, box]).astype(np.float32)
        vol = np.full(len(pos), h ** 3, dtype=np.float32)
        self.n_total = len(pos)
        self.mass = self.rho_box * self.length ** 3
        self.volume = self.length ** 3

        self.substeps, self.dt = substeps_and_dt(self.dx)
        self.sound_speed = sound_speed()

        s = Solver(grid=GridConfig(n_grid=self.n_grid, grid_lim=LIM),
                   device=device).load_particles(pos, vol)
        s.set_material(newtonian(eta=ETA, density=RHO_W, bulk_modulus=BULK))
        if self.box_mode == "rigid":
            s.set_material_range(self.n_water, self.n_total, "rigid", obj_id=0,
                                 density=self.rho_box)
            s.finalize_rigid_bodies()
        s.add_plane((0, 0, self.floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
        for pt, nrm in (((self.wall, 0, 0), (1, 0, 0)),
                        ((LIM - self.wall, 0, 0), (-1, 0, 0)),
                        ((0, self.wall, 0), (0, 1, 0)),
                        ((0, LIM - self.wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
        s.add_domain_walls()

        self.sdf_info = {}
        if self.box_mode == "collider_sdf":
            sdf, self.sdf_info = build_box_sdf(self.length, self.dx, res=sdf_res,
                                               band_safety=sdf_band_safety)
            # surface and friction are the engine's own add_sdf_collider defaults and are
            # NOT tuned. friction cannot reach this measurement anyway: for surface_type 2
            # the impulse is m*(v_free - v_surf - v_tan_scaled) (mpm_solver_warp.py:2731),
            # whose NORMAL part is friction-independent, and the tangential part is zero
            # on a stationary collider in still water.
            self.collider = s.add_sdf_collider(sdf, self.box_center,
                                               velocity=(0.0, 0.0, 0.0),
                                               surface="separable", friction=0.4)
        elif self.box_mode == "collider_box":
            hs = self.length / 2.0
            self.collider = s.add_box(self.box_center, (hs, hs, hs),
                                      velocity=(0.0, 0.0, 0.0))

        self.solver = s
        self.leaked = 0
        self.spawn_com = (s.rigid_state()["com"].copy() if self.box_mode == "rigid"
                          else np.asarray(self.box_center, dtype=float))
        self.realized_rho = self.mass / (self.n_side ** 3 * h ** 3)

    # --- collider wrench readout -----------------------------------------------------
    def reset_wrench(self):
        """Zero the collider's reaction accumulator. Call immediately before step()."""
        if self.box_mode == "collider_sdf":
            self.solver.reset_sdf_force(self.collider)
        elif self.box_mode == "collider_box":
            self.solver.reset_tool_force(self.collider)

    def wrench(self, dt):
        """Force the MATERIAL exerts on the collider, sum m*(v_free - v_new)/dt.

        Sign convention is the engine's, stated at core/solver.py:305-307: a static cup
        holding m kg of settled liquid reads force = (0, 0, -m*g). So a submerged body
        reads buoyancy as POSITIVE z. Returns (force[3], torque[3] or None).
        """
        if self.box_mode == "collider_sdf":
            w = self.solver.sdf_wrench(self.collider, dt)
            return np.asarray(w["force"], dtype=float), np.asarray(w["torque"], dtype=float)
        if self.box_mode == "collider_box":
            return np.asarray(self.solver.tool_force(self.collider, dt), dtype=float), None
        raise RuntimeError("wrench() is only defined for the collider modes")

    def project_water(self):
        if self.n_water == 0:
            return 0
        x = self.solver.x()
        w = x[: self.n_water]
        eps = 0.25 * self.dx
        lo = np.array([self.wall, self.wall, self.floor], dtype=np.float32) - eps
        hi = np.array([LIM - self.wall, LIM - self.wall, np.inf], dtype=np.float32) + eps
        out_lo = w < lo
        out_hi = w > hi
        if not (out_lo.any() or out_hi.any()):
            return 0
        n = int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
        v = self.solver.v()
        vw = v[: self.n_water]
        np.clip(w, lo, hi, out=w)
        vw[out_lo] = np.maximum(vw[out_lo], 0.0)
        vw[out_hi] = np.minimum(vw[out_hi], 0.0)
        self.solver.set_x(x)
        self.solver.set_v(v)
        self.leaked += n
        return n

    def reseat(self, z_bottom):
        sim = self.solver._sim
        com = self.solver.rigid_state()["com"].copy()
        com[2] = float(z_bottom) + self.length / 2.0
        sim.set_rigid_body_velocity(0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                                    device=self.solver.device)
        wp.to_torch(sim.rigid_x_cm)[0] = torch.tensor(
            np.asarray(com, dtype=np.float32))
        self.solver.step(self.dt, 1)
        return com

    def pin(self, com):
        if self.box_mode != "rigid":
            return   # a collider is kinematic: already held, nothing to pin
        sim = self.solver._sim
        sim.set_rigid_body_velocity(0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                                    device=self.solver.device)
        wp.to_torch(sim.rigid_x_cm)[0] = torch.tensor(
            np.asarray(com, dtype=np.float32))

    def step(self, n_frames=1):
        for _ in range(n_frames):
            self.solver.step(self.dt, self.substeps)

    def z_bottom(self):
        if self.box_mode != "rigid":
            return float(self.box_center[2]) - self.length / 2.0
        return float(self.solver.rigid_state()["com"][2]) - self.length / 2.0

    def column_surface(self, bin_cells=2.0):
        if self.n_water == 0:
            return float("nan"), 0, float("nan")
        x = self.solver.x()[: self.n_water]
        vol = self.solver.vol()[: self.n_water]
        b = bin_cells * self.h
        i = np.floor(x[:, 0] / b).astype(np.int64)
        j = np.floor(x[:, 1] / b).astype(np.int64)
        key = i * 1000003 + j
        order = np.argsort(key, kind="stable")
        key_s = key[order]
        vol_s = vol[order]
        starts = np.flatnonzero(np.r_[True, key_s[1:] != key_s[:-1]])
        col_vol = np.add.reduceat(vol_s, starts)
        cx = (i[order][starts] + 0.5) * b
        cy = (j[order][starts] + 0.5) * b
        under_box = ((cx >= self.box_x0 - b) & (cx <= self.box_x0 + self.length + b)
                     & (cy >= self.box_x0 - b) & (cy <= self.box_x0 + self.length + b))
        heights = col_vol / (b * b)
        free = heights[~under_box]
        if free.size == 0:
            return float("nan"), 0, float("nan")
        return (self.floor + float(np.median(free)), int(free.size),
                float(np.percentile(free, 75) - np.percentile(free, 25)))

    def draft(self):
        zb = self.z_bottom()
        if self.n_water == 0:
            return float("nan"), float("nan"), zb
        zs, _, _ = self.column_surface()
        return zs - zb, zs, zb

    def draft_by_tank_area(self):
        zb = self.z_bottom()
        if self.n_water == 0:
            return float("nan"), float("nan")
        vw = float(self.solver.vol()[: self.n_water].sum())
        ab = self.length ** 2
        zs = (vw + self.a_tank * self.floor - ab * zb) / (self.a_tank - ab)
        return zs - zb, zs

    def surface_direct(self):
        if self.n_water == 0:
            return float("nan")
        x = self.solver.x()[: self.n_water]
        h = self.h
        near = np.all((x[:, :2] >= self.box_x0 - 2.0 * h)
                      & (x[:, :2] <= self.box_x0 + self.length + 2.0 * h), axis=1)
        x = x[~near]
        if len(x) == 0:
            return float("nan")
        b = 4.0 * h
        i = np.floor(x[:, 0] / b).astype(np.int64)
        j = np.floor(x[:, 1] / b).astype(np.int64)
        key = i * 1000000 + j
        order = np.argsort(key, kind="stable")
        key = key[order]
        z = x[order, 2]
        starts = np.flatnonzero(np.r_[True, key[1:] != key[:-1]])
        tops = np.maximum.reduceat(z, starts)
        return float(np.median(tops) + 0.5 * h)

    def diagnostics(self):
        v = self.solver.v()
        x = self.solver.x()
        vmax = float(np.abs(v).max()) if len(v) else 0.0
        out = {
            "max_abs_v": vmax,
            "sound_speed_over_vmax": (self.sound_speed / vmax) if vmax > 1e-12 else float("inf"),
            "advective_cfl": vmax * self.dt / self.dx,
            "inverted_count": int(self.solver.inverted_count()),
            "leaked_cumulative": int(self.leaked),
        }
        if self.n_water:
            w = x[: self.n_water]
            tol = 0.5 * self.dx
            escaped = np.any((w[:, :2] < self.wall - tol)
                             | (w[:, :2] > LIM - self.wall + tol), axis=1)
            escaped |= w[:, 2] < self.floor - tol
            out["escaped_water"] = int(escaped.sum())
            out["escaped_water_frac"] = float(escaped.sum()) / float(self.n_water)
            out["max_floor_penetration_dx"] = float(
                max(0.0, self.floor - w[:, 2].min())) / self.dx
            out["max_wall_penetration_dx"] = float(max(
                0.0, self.wall - w[:, :2].min(),
                w[:, :2].max() - (LIM - self.wall))) / self.dx
            zb = self.z_bottom()
            lo = np.array([self.box_x0, self.box_x0, zb])
            hi = lo + self.length
            inb = np.all((w >= lo) & (w <= hi), axis=1)
            out["water_inside_box"] = int(inb.sum())
            out["water_inside_box_frac"] = float(inb.sum()) / float(self.n_water)
        return out

    def geometry(self):
        return {
            "box_mode": self.box_mode,
            "box_center": list(self.box_center),
            **self.sdf_info,
            "n_grid": self.n_grid,
            "grid_lim": LIM,
            "dx": self.dx,
            "h": self.h,
            "floor": self.floor,
            "wall": self.wall,
            "box_side_m": self.length,
            "box_side_cells": self.length / self.dx,
            "box_particles_per_side": self.n_side,
            "box_volume_m3": self.volume,
            "box_mass_kg": self.mass,
            "rho_box_requested": self.rho_box,
            "rho_box_realized": self.realized_rho,
            "n_water": self.n_water,
            "n_box": self.n_side ** 3,
            "n_total": self.n_total,
            "n_carved": self.n_carved,
            "water_depth_m": self.water_depth,
            "water_depth_cells": self.water_depth / self.dx if self.dx else 0.0,
            "water_layers": self.n_water_layers,
            "a_tank_m2": self.a_tank,
            "box_footprint_frac": self.length ** 2 / self.a_tank,
            "substeps": self.substeps,
            "dt": self.dt,
            "sound_speed": self.sound_speed,
        }


def heave_period(mass, length, rho_w=RHO_W, g=G, ca=0.5):
    k = rho_w * g * length ** 2
    v_disp = length ** 2 * (mass / (rho_w * length ** 2))
    m_eff = mass + ca * rho_w * v_disp
    return 2.0 * math.pi * math.sqrt(m_eff / k)


def run_c0(n_grid, rho_box=600.0, n_substeps=20, device="auto"):
    tank = BoxTank(n_grid, rho_box, 0, LIM / 2.0, water=False, device=device)
    ts, vs = [0.0], [float(tank.solver.rigid_state()["v"][2])]
    for i in range(n_substeps):
        tank.solver.step(tank.dt, 1)
        ts.append((i + 1) * tank.dt)
        vs.append(float(tank.solver.rigid_state()["v"][2]))
    a = float(np.polyfit(np.asarray(ts), np.asarray(vs), 1)[0])
    return {
        "variant": "C0_dry_drop",
        "geometry": tank.geometry(),
        "a_measured": a,
        "a_expected": -G,
        "rel_error_pct": 100.0 * (a - (-G)) / G,
        "v_series": vs,
        "t_series": ts,
    }


def run_c2(n_grid, rho_box=600.0, depth_cells=10, offset_cells=0.0,
           settle_frames=60, max_frames=3000, device="auto", seed=0):
    d_inc = draft_incompressible(rho_box)
    d_com = draft_compressible(rho_box)
    dx = LIM / n_grid
    floor = 3.0 * DX_CANON
    wall = 4.0 * DX_CANON
    a_tank = (LIM - 2.0 * wall) ** 2
    rise = (L_BOX ** 2) * d_inc / (a_tank - L_BOX ** 2)
    z_surf_nom = floor + depth_cells * DX_CANON + rise
    z_b0 = z_surf_nom - d_inc + offset_cells * dx

    tank = BoxTank(n_grid, rho_box, depth_cells, z_b0, water=True,
                   device=device, seed=seed)
    settle_state = settle_pinned(tank, settle_frames)
    settle_state["draft_after_settle"] = tank.draft()[0]
    settle_state["surface_direct_after_settle"] = tank.surface_direct()

    zs_settled, _, _ = tank.column_surface()
    z_b_reseat = zs_settled - d_inc + offset_cells * dx
    tank.reseat(z_b_reseat)
    settle_state["surface_after_settle"] = zs_settled
    settle_state["z_b_nominal_at_spawn"] = z_b0
    settle_state["z_b_reseated"] = z_b_reseat
    settle_state["reseat_shift_m"] = z_b_reseat - z_b0

    t_heave = heave_period(tank.mass, tank.length)
    window = max(int(round(t_heave * FPS)), 10)
    tol = 0.01 * tank.h

    drafts, surfs, com_trace = [], [], []
    means, converged, frames_run = [], False, 0
    for f in range(max_frames):
        tank.project_water()
        tank.solver.step(tank.dt, tank.substeps)
        drafts.append(tank.draft()[0])
        com_trace.append(tank.solver.rigid_state()["com"].copy().tolist())
        cxyz = com_trace[-1]
        print("com_frame", f, cxyz[0], cxyz[1], cxyz[2], flush=True)
        frames_run = f + 1
        if frames_run % window == 0:
            m = float(np.mean(drafts[-window:]))
            means.append(m)
            surfs.append(tank.surface_direct())
            if len(means) >= 2 and abs(means[-1] - means[-2]) < tol:
                converged = True
                break

    tail = np.asarray(drafts[-window:])
    d_meas = float(tail.mean())
    return {
        "variant": "CV2_equilibrium_draft",
        "geometry": tank.geometry(),
        "settle": settle_state,
        "offset_cells": offset_cells,
        "z_b_initial": z_b0,
        "heave_period_s": t_heave,
        "window_frames": window,
        "tol_m": tol,
        "converged": converged,
        "frames_run": frames_run,
        "window_means": means,
        "draft_measured": d_meas,
        "draft_ptp_final_window": float(tail.max() - tail.min()),
        "draft_incompressible": d_inc,
        "draft_compressible": d_com,
        "err_vs_incompressible_pct": 100.0 * (d_meas - d_inc) / d_inc,
        "err_vs_compressible_pct": 100.0 * (d_meas - d_com) / d_com,
        "one_particle_layer_pct_of_draft": 100.0 * tank.h / d_inc,
        "surface_direct_series": surfs,
        "surface_column_final": tank.draft()[1],
        "surface_column_bins": tank.column_surface()[1],
        "surface_column_iqr_m": tank.column_surface()[2],
        "surface_direct_final": tank.surface_direct(),
        "draft_by_tank_area": tank.draft_by_tank_area()[0],
        "surface_by_tank_area": tank.draft_by_tank_area()[1],
        "diagnostics": tank.diagnostics(),
        "draft_series": drafts,
        "com_trace": com_trace,
    }


def settle_pinned(tank, settle_frames, ratio_target=20.0):
    com_pin = tank.spawn_com.copy()
    trace = []
    transit = tank.water_depth / tank.sound_speed
    min_settle = max(20, int(math.ceil(10.0 * transit * FPS)))
    settled = False
    for i in range(settle_frames):
        tank.project_water()
        tank.solver.step(tank.dt, tank.substeps)
        tank.pin(com_pin)
        vm = float(np.abs(tank.solver.v()[: tank.n_water]).max())
        trace.append(vm)
        if i + 1 >= min_settle and vm > 0.0 and tank.sound_speed / vm >= ratio_target:
            settled = True
            break
    return {
        "settle_frames_run": len(trace),
        "settle_frames_cap": settle_frames,
        "settle_gate_met": settled,
        "settle_ratio_target": ratio_target,
        "settle_min_frames": min_settle,
        "settle_acoustic_transit_s": transit,
        "settle_vmax_peak": max(trace) if trace else None,
        "settle_vmax_final": trace[-1] if trace else None,
        "settle_vmax_trace": trace,
        "diagnostics_after_settle": tank.diagnostics(),
    }


def run_c1(n_grid, rho_box=600.0, depth_cells=18.0, box_bottom_cells=8.0,
           settle_frames=600, measure_substeps=120, device="auto", seed=0):
    dx = LIM / n_grid
    floor = 3.0 * DX_CANON
    z_b0 = floor + box_bottom_cells * DX_CANON
    tank = BoxTank(n_grid, rho_box, depth_cells, z_b0, water=True,
                   device=device, seed=seed)
    settle = settle_pinned(tank, settle_frames)

    zs_settle, _, _ = tank.column_surface()
    z_b_reseat = z_b0
    submerged = bool(zs_settle > z_b0 + tank.length + 0.5 * dx)

    ts, vs = [0.0], [float(tank.solver.rigid_state()["v"][2])]
    for i in range(measure_substeps):
        tank.project_water()
        tank.solver.step(tank.dt, 1)
        ts.append((i + 1) * tank.dt)
        vs.append(float(tank.solver.rigid_state()["v"][2]))

    t = np.asarray(ts)
    v = np.asarray(vs)
    a_ideal = G * (RHO_W / rho_box - 1.0)
    windows = {}
    for n in (2, 3, 5, 10, 20, 40):
        if n < len(t):
            windows[f"a_first_{n}_substeps"] = float(np.polyfit(t[: n + 1], v[: n + 1], 1)[0])
    a0 = windows.get("a_first_3_substeps", float("nan"))
    tail = min(len(t) - 1, measure_substeps)
    a_late = float(np.polyfit(t[tail // 2:], v[tail // 2:], 1)[0]) if tail > 8 else float("nan")

    m = tank.mass
    return {
        "variant": "C1_initial_submerged_acceleration",
        "geometry": tank.geometry(),
        "settle": settle,
        "fully_submerged_at_release": submerged,
        "surface_after_settle": zs_settle,
        "box_top_z": z_b_reseat + tank.length,
        "z_b_reseated": z_b_reseat,
        "z_b_nominal_at_spawn": z_b0,
        "submersion_margin_dx": (zs_settle - (z_b_reseat + tank.length)) / dx,
        "a_ideal": a_ideal,
        "a_added_mass_asymptote_ca067": a_ideal / (1.0 + 0.67 * RHO_W / rho_box),
        "a_windows": windows,
        "a_headline_first3": a0,
        "a_late_window": a_late,
        "err_headline_vs_ideal_pct": (100.0 * (a0 - a_ideal) / a_ideal if abs(a_ideal) > 1e-12 else float("nan")),
        "F_buoy_from_a": m * (a0 + G),
        "F_buoy_analytic": RHO_W * tank.volume * G,
        "err_F_pct": 100.0 * (m * (a0 + G) - RHO_W * tank.volume * G)
                     / (RHO_W * tank.volume * G),
        "acoustic_transit_substeps": (tank.length / tank.sound_speed) / tank.dt,
        "t_series": ts,
        "v_series": vs,
        "diagnostics": tank.diagnostics(),
    }


def run_c1_sdf(n_grid, rho_box=600.0, depth_cells=18.0, box_bottom_cells=8.0,
               settle_frames=600, measure_substeps=120, collider="sdf",
               sdf_res=64, device="auto", seed=0):
    """C1-SDF: the C1 cube and water, but the cube is a FIXED collider.

    C1 infers the buoyant force from a free rigid body's acceleration. That path
    materialises no force at all: rigid_body_integrate sets v_cm = rigid_linear_mom / M
    (kernels/mpm_utils.py:1434) where rigid_linear_mom is the mass-weighted sum of the
    GRID velocity gathered at each rigid particle (:1411) and M is the sum of those same
    particle masses (mpm_solver_warp.py:856). The body therefore adopts a mass-weighted
    AVERAGE of grid velocity; no force or impulse is ever formed, so C1's F_buoy_from_a is
    a back-computation, not a measurement.

    A collider does form one: it accumulates sum m*(v_free - v_new) on the grid before
    overwriting node velocity, and sdf_wrench / tool_force divide it by dt. Same box, same
    water, same resolution, same excluded volume. Discriminator, as scoped:
      collider right, free-rigid wrong -> defect is in the free rigid coupling
      both wrong                       -> defect is in the scene or the harness
      collider also negative           -> the water is not hydrostatic
    rho_box is accepted but only enters as reporting context; a fixed collider has no
    mass and its reading cannot depend on one.
    """
    dx = LIM / n_grid
    floor = 3.0 * DX_CANON
    z_b0 = floor + box_bottom_cells * DX_CANON
    tank = BoxTank(n_grid, rho_box, depth_cells, z_b0, water=True, device=device,
                   seed=seed, box_mode=f"collider_{collider}", sdf_res=sdf_res)
    settle = settle_pinned(tank, settle_frames)

    zs_settle, _, _ = tank.column_surface()
    box_top = z_b0 + tank.length

    f_series, t_series = [], []
    for i in range(measure_substeps):
        tank.project_water()
        tank.reset_wrench()
        tank.solver.step(tank.dt, 1)
        f, _tau = tank.wrench(tank.dt)
        f_series.append([float(f[0]), float(f[1]), float(f[2])])
        t_series.append((i + 1) * tank.dt)

    f = np.asarray(f_series)
    fz = f[:, 2]
    f_analytic = RHO_W * tank.volume * G
    # Second analytic, for the case the cube is NOT fully submerged. At the C1 defaults
    # (depth_cells=18, box_bottom_cells=8) box_top = floor + 18*DX_CANON is EXACTLY the
    # nominal free surface, so full buoyancy is only reached via the displacement rise.
    # Reported alongside, never instead of, rho_w*V*g.
    h_sub = float(np.clip(zs_settle - z_b0, 0.0, tank.length))
    f_partial = RHO_W * G * (tank.length ** 2) * h_sub

    # Report the same window ladder C1 reports so the two are read on one axis. For a
    # FIXED collider the added-mass transient that makes C1's earliest window the honest
    # one does not arise (the body never accelerates), so the steady tail is the physically
    # meaningful figure here. Both are reported; neither is silently preferred.
    windows = {f"F_first_{n}_mean": float(fz[:n].mean())
               for n in (1, 2, 3, 5, 10, 20, 40) if n <= len(fz)}
    tail = fz[len(fz) // 2:]
    f_steady = float(tail.mean())
    f_first3 = float(fz[:3].mean()) if len(fz) >= 3 else float("nan")

    return {
        "variant": f"C1SDF_fixed_collider_buoyancy_{collider}",
        "collider_kind": collider,
        "geometry": tank.geometry(),
        "settle": settle,
        "surface_after_settle": zs_settle,
        "box_top_z": box_top,
        "z_b_nominal_at_spawn": z_b0,
        "submersion_margin_dx": (zs_settle - box_top) / dx,
        "fully_submerged_at_measure": bool(zs_settle > box_top + 0.5 * dx),
        "F_buoy_analytic": f_analytic,
        "F_buoy_analytic_partial_submersion": f_partial,
        "submerged_height_m": h_sub,
        "submerged_height_frac": h_sub / tank.length,
        "err_steady_vs_partial_pct": (100.0 * (f_steady - f_partial) / f_partial
                                      if f_partial > 0 else float("nan")),
        "F_windows": windows,
        "F_first3_mean": f_first3,
        "F_steady_tail_mean": f_steady,
        "F_steady_tail_std": float(tail.std()),
        "F_steady_tail_ptp": float(tail.max() - tail.min()),
        "err_steady_vs_analytic_pct": 100.0 * (f_steady - f_analytic) / f_analytic,
        "err_first3_vs_analytic_pct": 100.0 * (f_first3 - f_analytic) / f_analytic,
        # lateral force must vanish by symmetry: a nonzero Fx/Fy relative to Fz means the
        # readout itself is unsound, independent of whether Fz matches buoyancy.
        "F_lateral_steady": [float(f[len(f) // 2:, 0].mean()),
                             float(f[len(f) // 2:, 1].mean())],
        "F_lateral_over_Fz": float(np.hypot(f[len(f) // 2:, 0].mean(),
                                            f[len(f) // 2:, 1].mean())
                                   / abs(f_steady)) if f_steady != 0 else float("nan"),
        "box_weight_at_rho_box": rho_box * tank.volume * G,
        "a_free_body_implied": (f_steady - rho_box * tank.volume * G) / tank.mass,
        "a_ideal_for_comparison": G * (RHO_W / rho_box - 1.0),
        "acoustic_transit_substeps": (tank.length / tank.sound_speed) / tank.dt,
        "t_series": t_series,
        "f_series": f_series,
        "diagnostics": tank.diagnostics(),
    }


def run_c3(n_grid, depth_cells=18.0, box_bottom_cells=8.0, settle_frames=600,
           measure_substeps=120, device="auto", seed=0):
    res = run_c1(n_grid, RHO_W, depth_cells, box_bottom_cells, settle_frames,
                 measure_substeps, device, seed)
    res["variant"] = "C3_neutral_buoyancy_null"
    zc = res["surface_after_settle"] - (res["geometry"]["box_side_m"] / 2.0
                                        + 3.0 * DX_CANON + box_bottom_cells * DX_CANON)
    depth_to_centroid = max(zc, 0.0)
    rho_local = hydrostatic_density(depth_to_centroid)
    res["a_ideal_incompressible"] = 0.0
    res["rho_local_at_centroid"] = rho_local
    res["a_expected_compressible"] = G * (rho_local / RHO_W - 1.0)
    res["a_as_fraction_of_g"] = res["a_headline_first3"] / G
    a_exp = res["a_expected_compressible"]
    res["err_headline_vs_ideal_pct"] = (
        100.0 * (res["a_late_window"] - a_exp) / a_exp
        if abs(a_exp) > 1e-12 else float("nan")
    )
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--variant", default="c2",
                   choices=["c0", "c1", "c2", "c3", "c1sdf"])
    p.add_argument("--collider", default="sdf", choices=["sdf", "box"],
                   help="c1sdf only: mesh-SDF collider (primary) or axis-aligned box "
                        "collider (cross-check, exact geometry, no SDF interpolation)")
    p.add_argument("--sdf-res", type=int, default=64,
                   help="c1sdf --collider sdf only: voxels per axis of the cube SDF")
    p.add_argument("--n-grid", type=int, default=64)
    p.add_argument("--rho-box", type=float, default=600.0)
    p.add_argument("--depth-cells", type=float, default=10.0)
    p.add_argument("--offset-cells", type=float, default=0.0)
    p.add_argument("--settle-frames", type=int, default=60)
    p.add_argument("--max-frames", type=int, default=3000)
    p.add_argument("--substeps-c0", type=int, default=20)
    p.add_argument("--box-bottom-cells", type=float, default=8.0)
    p.add_argument("--measure-substeps", type=int, default=120)
    p.add_argument("--device", default="auto")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    if a.variant == "c0":
        res = run_c0(a.n_grid, a.rho_box, a.substeps_c0, a.device)
    elif a.variant == "c1":
        res = run_c1(a.n_grid, a.rho_box, a.depth_cells, a.box_bottom_cells,
                     a.settle_frames, a.measure_substeps, a.device, a.seed)
    elif a.variant == "c1sdf":
        res = run_c1_sdf(a.n_grid, a.rho_box, a.depth_cells, a.box_bottom_cells,
                         a.settle_frames, a.measure_substeps, a.collider,
                         a.sdf_res, a.device, a.seed)
    elif a.variant == "c3":
        res = run_c3(a.n_grid, a.depth_cells, a.box_bottom_cells,
                     a.settle_frames, a.measure_substeps, a.device, a.seed)
    else:
        res = run_c2(a.n_grid, a.rho_box, a.depth_cells, a.offset_cells,
                     a.settle_frames, a.max_frames, a.device, a.seed)
    res["provenance"] = PROVENANCE

    print(json.dumps({k: v for k, v in res.items()
                      if k not in ("draft_series", "v_series", "t_series", "f_series")},
                     indent=2, default=float))
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, indent=2, default=float))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
