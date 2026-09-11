"""Vehicles in floods: a splat-captured body as a two-way rigid body in MPM fluid.

A vehicle arrives as a 3D Gaussian Splatting PLY (or a watertight mesh). Its splats give
the surface; interior filling makes it a solid; the particle set is registered with the
fork's rigid-body system (material "rigid" plus obj_id), so per substep the fluid's grid
momentum accumulates into a body force and torque and the body translates and rotates as
one piece. Displacement and rotation from the spawn pose read directly off the body
state; FloodScene records them per frame.

Conventions: the scene is metric, z up. The vehicle is oriented so its long axis lies
along y and the flood surge travels along +x, hitting the side. Water is the
weakly compressible newtonian fluid with a softened bulk modulus; depth and surge
velocity are the study parameters.

    from warpmpm.vehicle import load_vehicle, FloodScene
    v = load_vehicle("truck_trimmed.ply")          # up="-y" etc. if not z-up
    scene = FloodScene(v, depth=0.15, velocity=2.0)
    history = scene.run(frames=90)
    history.to_csv("truck_metrics.csv")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian

_AXES = {"x": 0, "y": 1, "z": 2, "-x": 0, "-y": 1, "-z": 2}

# vertex properties that mark a ply as an INRIA-layout 3DGS export rather than a
# plain mesh; these are the first fields load_gaussians_ply reads
_GAUSSIAN_PLY_FIELDS = frozenset({"opacity", "f_dc_0"})
_PLY_HEADER_MAX_LINES = 1000


def _up_rotation(up: str) -> np.ndarray:
    """Rotation taking the named source axis to +z (right handed)."""
    if up not in _AXES:
        raise ValueError(f"up must be one of {sorted(_AXES)}, got {up!r}")
    sign = -1.0 if up.startswith("-") else 1.0
    src = np.zeros(3)
    src[_AXES[up]] = sign
    dst = np.array([0.0, 0.0, 1.0])
    v = np.cross(src, dst)
    c = float(src @ dst)
    if np.allclose(v, 0.0):
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1.0 + c)


def euler_zyx(R: np.ndarray) -> tuple[float, float, float]:
    """(yaw, pitch, roll) in radians from a rotation matrix, ZYX convention: yaw about
    z (heading), pitch about y, roll about x."""
    yaw = float(np.arctan2(R[1, 0], R[0, 0]))
    pitch = float(np.arcsin(np.clip(-R[2, 0], -1.0, 1.0)))
    roll = float(np.arctan2(R[2, 1], R[2, 2]))
    return yaw, pitch, roll


def solidify_columns(pos: np.ndarray, h: float) -> np.ndarray:
    """Solid particle set from a surface point cloud by vertical column fill.

    Voxelize at pitch h; every (x, y) column that contains surface points is filled
    from its lowest to its highest occupied cell. Robust on holey splat shells (open
    windows, thin walls) where ray-cast interiority finds little, at the cost of
    merging wheel wells and window openings into the solid; for blocking flow that is
    the right approximation."""
    key = np.floor(pos / h).astype(np.int64)
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
    k = key[order]
    col = k[:, :2]
    starts = np.flatnonzero(np.r_[True, np.any(col[1:] != col[:-1], axis=1)])
    out = []
    for s, e in zip(starts, np.r_[starts[1:], len(k)], strict=True):
        zlo, zhi = k[s, 2], k[e - 1, 2]
        zs = np.arange(zlo, zhi + 1)
        cells = np.column_stack([np.full_like(zs, k[s, 0]),
                                 np.full_like(zs, k[s, 1]), zs])
        out.append(cells)
    cells = np.concatenate(out)
    return ((cells + 0.5) * h).astype(np.float32)


def solidify_watertight(mesh, h: float) -> np.ndarray:
    """Solid particle set from a watertight mesh by exact vertical ray parity.

    For each grid column, collect every z where the column axis crosses the surface,
    sort them, and fill only between successive entry/exit pairs. Unlike
    solidify_columns this leaves genuine voids (ground clearance, wheel wells) empty,
    so the realized particle volume matches the hull volume and buoyancy is unbiased.
    Requires a closed surface; use solidify_columns for holey splat shells."""
    v = np.asarray(mesh.vertices, dtype=np.float64)
    f = np.asarray(mesh.faces)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    lo, hi = v.min(0), v.max(0)
    nx = int(np.ceil((hi[0] - lo[0]) / h)); ny = int(np.ceil((hi[1] - lo[1]) / h))
    ox, oy = lo[0] + h / 2, lo[1] + h / 2
    tlo = np.minimum(np.minimum(a, b), c); thi = np.maximum(np.maximum(a, b), c)
    i0 = np.clip(np.ceil((tlo[:, 0] - ox) / h).astype(np.int64), 0, nx - 1)
    i1 = np.clip(np.floor((thi[:, 0] - ox) / h).astype(np.int64), 0, nx - 1)
    j0 = np.clip(np.ceil((tlo[:, 1] - oy) / h).astype(np.int64), 0, ny - 1)
    j1 = np.clip(np.floor((thi[:, 1] - oy) / h).astype(np.int64), 0, ny - 1)
    ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0)
    cnt = ni * nj
    idx = np.flatnonzero(cnt > 0)
    CI, CJ, CT = [], [], []
    for s0 in range(0, len(idx), 20000):
        blk = idx[s0:s0 + 20000]
        n = cnt[blk]
        off = np.arange(int(n.sum())) - np.repeat(np.cumsum(n) - n, n)
        njr = np.repeat(nj[blk], n)
        CI.append(np.repeat(i0[blk], n) + off // njr)
        CJ.append(np.repeat(j0[blk], n) + off % njr)
        CT.append(np.repeat(blk, n))
    ci = np.concatenate(CI); cj = np.concatenate(CJ); ct = np.concatenate(CT)
    px = ox + ci * h; py = oy + cj * h
    a2, b2, c2 = a[ct], b[ct], c[ct]
    d = (b2[:, 1] - c2[:, 1]) * (a2[:, 0] - c2[:, 0]) + (c2[:, 0] - b2[:, 0]) * (a2[:, 1] - c2[:, 1])
    ok = np.abs(d) > 1e-14
    dd = np.where(ok, d, 1.0)
    w0 = np.where(ok, ((b2[:, 1] - c2[:, 1]) * (px - c2[:, 0]) + (c2[:, 0] - b2[:, 0]) * (py - c2[:, 1])) / dd, -1.0)
    w1 = np.where(ok, ((c2[:, 1] - a2[:, 1]) * (px - c2[:, 0]) + (a2[:, 0] - c2[:, 0]) * (py - c2[:, 1])) / dd, -1.0)
    w2 = 1.0 - w0 - w1
    hit = ok & (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    ci, cj = ci[hit], cj[hit]
    z = w0[hit] * a2[hit][:, 2] + w1[hit] * b2[hit][:, 2] + w2[hit] * c2[hit][:, 2]
    col = ci * ny + cj
    order = np.lexsort((z, col))
    col, z = col[order], z[order]
    starts = np.flatnonzero(np.r_[True, col[1:] != col[:-1]])
    out = []
    z0 = lo[2] + h / 2
    for st, en in zip(starts, np.r_[starts[1:], len(col)]):
        if (en - st) % 2:
            continue
        zs = z[st:en]
        i, j = col[st] // ny, col[st] % ny
        for k in range(0, en - st, 2):
            ka = np.ceil((zs[k] - z0) / h); kb = np.floor((zs[k + 1] - z0) / h)
            if kb < ka:
                continue
            kk = np.arange(ka, kb + 1)
            out.append(np.column_stack([np.full(len(kk), ox + i * h),
                                        np.full(len(kk), oy + j * h), z0 + kk * h]))
    if not out:
        return np.zeros((0, 3), dtype=np.float32)
    return np.concatenate(out).astype(np.float32)


@dataclass
class VehicleBody:
    """A vehicle ready to drop into a scene: solid particle set in the vehicle frame
    (z up, long axis along y, centered at the origin in x and y, floor at z = 0) plus
    the visible splats for rendering. spacing is the particle lattice pitch; call
    solidify to rebuild the particle set at a scene's own pitch."""
    particles: np.ndarray          # (M, 3) solid particle set, vehicle frame
    spacing: float
    extent: np.ndarray             # (3,) bounding size after orientation
    surface: np.ndarray | None = None       # oriented surface points, vehicle frame
    splat_pos: np.ndarray | None = None    # (N, 3) splat centers, vehicle frame
    splat_colors: np.ndarray | None = None  # (N, 3) DC colors in [0, 1]
    source: str = ""
    mesh: object | None = None              # oriented watertight mesh, when available

    @property
    def n_particles(self) -> int:
        return len(self.particles)

    def solidify(self, h: float) -> VehicleBody:
        """Rebuild the solid particle set at pitch h (in place); returns self."""
        if self.mesh is not None and bool(self.mesh.is_watertight):
            self.particles = solidify_watertight(self.mesh, h)
        else:
            src = self.surface if self.surface is not None else self.particles
            self.particles = solidify_columns(np.asarray(src, dtype=np.float64), h)
        self.spacing = h
        return self


def is_gaussian_ply(path: Path) -> bool:
    """True when a .ply carries 3DGS splat attributes, false for plain geometry.

    .ply is a container, not a single format: an INRIA-layout splat export and a
    watertight mesh both wear the suffix, so the extension cannot decide which
    reader applies. Dispatch on the vertex properties load_gaussians_ply actually
    requires (opacity and the DC colour f_dc_0); a mesh ply carries neither. The
    header is ASCII in every ply variant, ascii or binary body alike, so this
    stays a short read of the first lines."""
    props = set()
    with path.open("rb") as f:
        for _ in range(_PLY_HEADER_MAX_LINES):
            raw = f.readline()
            if not raw:
                break
            line = raw.decode("ascii", errors="replace").strip()
            if line == "end_header":
                break
            if line.startswith("property "):
                props.add(line.split()[-1])
    return _GAUSSIAN_PLY_FIELDS.issubset(props)


def load_vehicle(path, up: str = "z", spacing: float | None = None,
                 target_length: float | None = None,
                 fill_kwargs: dict | None = None) -> VehicleBody:
    """Load a vehicle from a 3DGS splat PLY (or a watertight mesh readable by trimesh)
    and build its solid particle set.

    up names the source file's up axis; the body is rotated to z up, then about z so
    the longest horizontal extent lies along y (the flood hits the side). target_length
    rescales the long axis to that many metres. spacing defaults to extent/32 and sets
    the interior fill pitch; FloodScene re-solidifies at its own grid pitch anyway."""
    path = Path(path)
    splat_colors = None
    src_mesh = None
    scale_applied = None
    if path.suffix.lower() == ".ply" and is_gaussian_ply(path):
        from warpmpm.splats.appearance import eval_sh
        from warpmpm.splats.io import load_gaussians_ply
        cloud = load_gaussians_ply(path)
        pos = cloud.pos.astype(np.float64)
        opacity = cloud.opacity.reshape(-1)
        cov6 = cloud.cov
        # DC color for rendering, viewed head on
        dirs = np.tile(np.array([0.0, 1.0, 0.0]), (len(pos), 1))
        splat_colors = np.clip(eval_sh(0, cloud.sh[:, :1, :], dirs), 0.0, 1.0)
    else:
        import trimesh
        src_mesh = trimesh.load(path, force="mesh")
        pos = np.asarray(src_mesh.sample(60_000), dtype=np.float64)
        opacity = np.ones(len(pos))
        cov6 = None

    R = _up_rotation(up)
    pos = pos @ R.T
    # long horizontal axis along y
    ext = pos.max(0) - pos.min(0)
    if ext[0] > ext[1]:
        Rz = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        pos = pos @ Rz.T
        R = Rz @ R
    if target_length is not None:
        scale_applied = target_length / float((pos.max(0) - pos.min(0))[1])
        pos *= scale_applied
    # center in x, y; floor at z = 0
    lo, hi = pos.min(0), pos.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    pos -= shift
    extent = pos.max(0) - pos.min(0)
    h = spacing if spacing is not None else float(extent.max()) / 32.0
    del opacity, cov6, fill_kwargs  # column fill replaces ray-cast interiority here

    oriented = None
    if src_mesh is not None:
        import trimesh
        mv = np.asarray(src_mesh.vertices, dtype=np.float64) @ R.T
        if scale_applied is not None:
            mv *= scale_applied
        mv -= shift
        oriented = trimesh.Trimesh(vertices=mv, faces=np.asarray(src_mesh.faces), process=False)
    if oriented is not None and bool(oriented.is_watertight):
        particles = solidify_watertight(oriented, h)
    else:
        particles = solidify_columns(pos, h)
    return VehicleBody(particles=particles, spacing=h, extent=extent, mesh=oriented,
                       surface=pos.astype(np.float32),
                       splat_pos=pos.astype(np.float32) if splat_colors is not None else None,
                       splat_colors=splat_colors, source=str(path))


@dataclass
class FloodHistory:
    """Per-frame rigid-body record. displacement is com minus the spawn com in scene
    coordinates (x = surge direction, y = along the vehicle, z = up). Angles are ZYX
    Euler angles of the body rotation from spawn, in degrees, reported in the vehicle's
    frame: yaw is heading (about z), roll is rotation about the vehicle's long axis
    (y, so a side-hit rollover reads as roll), pitch is about the surge axis (x).
    Near |roll| = 90 (vehicle on its side) yaw and pitch are degenerate (the ZYX
    gimbal singularity); read roll alone there."""
    t: list = field(default_factory=list)
    displacement: list = field(default_factory=list)
    yaw: list = field(default_factory=list)
    pitch: list = field(default_factory=list)
    roll: list = field(default_factory=list)
    v: list = field(default_factory=list)
    omega: list = field(default_factory=list)

    def append(self, t: float, state: dict, com0: np.ndarray) -> None:
        self.t.append(t)
        self.displacement.append(state["com"] - com0)
        y, p, r = euler_zyx(state["R"])
        self.yaw.append(np.degrees(y))
        # the long axis lies along y, so the Euler pitch (about y) is the vehicle's
        # roll and the Euler roll (about x) its pitch
        self.pitch.append(np.degrees(r))
        self.roll.append(np.degrees(p))
        self.v.append(state["v"])
        self.omega.append(state["omega"])

    def arrays(self) -> dict:
        return {
            "t": np.asarray(self.t),
            "displacement": np.asarray(self.displacement),
            "yaw_deg": np.asarray(self.yaw),
            "pitch_deg": np.asarray(self.pitch),
            "roll_deg": np.asarray(self.roll),
            "v": np.asarray(self.v),
            "omega": np.asarray(self.omega),
        }

    def to_csv(self, path) -> None:
        a = self.arrays()
        d = a["displacement"]
        v = a["v"]
        w = a["omega"]
        rows = np.column_stack([a["t"], d, np.linalg.norm(d, axis=1),
                                a["yaw_deg"], a["pitch_deg"], a["roll_deg"],
                                v, np.linalg.norm(v, axis=1), w])
        header = ("t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg,"
                  "vx,vy,vz,vmag,wx,wy,wz")
        np.savetxt(path, rows, delimiter=",", header=header, comments="")


class FloodScene:
    """A flood surge hitting a rigid vehicle from the side.

    A water slab of the given depth spawns upstream with an initial velocity along +x
    and breaks against the vehicle. The vehicle is one rigid body: the fluid's grid
    momentum accumulates into its force and torque each substep, so sliding, floating,
    and overturning come out of the coupling. vehicle_density is the body's effective
    density (vehicles are mostly air; a car is roughly 100 to 300 kg/m^3 spread over
    its volume, which is why they float); vehicle_mass, if given, overrides it with a
    total mass in kg. The realized mass is self.vehicle_mass either way."""

    def __init__(self, vehicle: VehicleBody, depth: float = 0.12, velocity: float = 1.5,
                 water_density: float = 1000.0, water_eta: float = 1.0,
                 bulk_modulus: float = 1.5e5, vehicle_density: float = 250.0,
                 vehicle_mass: float | None = None,
                 n_grid: int = 64, fps: int = 30, floor_friction: float = 0.5,
                 settle_frames: int = 8, device: str = "auto", seed: int = 0):
        self.vehicle = vehicle
        self.fps = fps
        ext = vehicle.extent
        # domain: room for the slab upstream, the vehicle, and runout downstream
        lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
        self.grid = GridConfig(n_grid=n_grid, grid_lim=lim)
        dx = self.grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        rng = np.random.default_rng(seed)

        # match the vehicle's particle pitch to the scene so the body blocks flow
        if vehicle.spacing > 1.2 * h:
            vehicle.solidify(h)

        solid_volume = vehicle.n_particles * h ** 3
        if vehicle_mass is not None:
            vehicle_density = vehicle_mass / solid_volume
        self.vehicle_mass = vehicle_density * solid_volume

        # vehicle placement: centered in y, at 60 percent of x, resting on the floor
        vx, vy = 0.60 * lim, 0.50 * lim
        self._place = np.array([vx, vy, floor + 0.5 * h], dtype=np.float32)
        truck = vehicle.particles + self._place

        # water slab upstream of the vehicle, resting against the inset walls. The
        # engine's domain band alone lets pressed water creep to the guard radius, and
        # a surge can still penetrate a slip plane by most of a cell, so the walls sit
        # 4 cells in: guard fires at 2.5 dx, leaving 1.5 dx of overshoot room.
        wall = 4.0 * dx
        gap = 2.0 * dx
        x0, x1 = wall + 0.5 * h, vx + vehicle.particles[:, 0].min() - gap
        y0, y1 = wall + 0.5 * h, lim - wall - 0.5 * h
        xs = np.arange(x0, x1, h)
        ys = np.arange(y0, y1, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = (water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)).astype(np.float32)

        pos = np.concatenate([water, truck])
        vol = np.full(len(pos), h ** 3, dtype=np.float32)
        self.n_water = len(water)
        self.n_total = len(pos)

        s = Solver(grid=self.grid, device=device).load_particles(pos, vol)
        s.set_material(newtonian(eta=water_eta, density=water_density,
                                 bulk_modulus=bulk_modulus))
        s.set_material_range(self.n_water, self.n_total, "rigid", obj_id=0,
                             density=vehicle_density)
        s.finalize_rigid_bodies()
        # restitution > 0 makes each plane a rigid-body contact surface as well; the
        # grid BC alone holds only the water, and the body would sink through the floor
        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
                    restitution=0.05)
        for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                        ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
        s.add_domain_walls()
        self.solver = s
        self.floor = floor
        self._wall = wall
        self._lim = lim
        self.leaked = 0

        # substeps from the acoustic CFL plus the advective bound of the surge itself
        c = float(np.sqrt(1.1 * bulk_modulus / water_density))
        rate = max(c / (0.28 * dx), 6.0 * water_eta / (water_density * dx * dx),
                   max(velocity, 1e-6) / (0.5 * dx))
        self.substeps = int(np.ceil(rate / fps))
        self.dt = (1.0 / fps) / self.substeps

        # settle: the vehicle seats on the floor and the slab finds hydrostatic rest,
        # so displacement and rotation measure the surge, never the drop onto the floor
        for _ in range(settle_frames):
            self._project_water()
            s.step(self.dt, self.substeps)
        # surge: the settled slab starts moving toward the vehicle
        v = s.v()
        v[: self.n_water, 0] += velocity
        s.set_v(v)

        self.com0 = s.rigid_state()["com"].copy()
        self.time = 0.0
        self.history = FloodHistory()
        self.history.append(0.0, s.rigid_state(), self.com0)

    def _project_water(self) -> None:
        """Push leaked water particles back inside the floor and wall planes and kill
        their inward velocity component. A slip plane corrects grid nodes, not
        particles, so sustained pressure lets a few particles creep through it (about
        a millimetre per frame under the surge front); left alone they reach the
        grid-edge guard. Particles hovering within a quarter cell of a plane are the
        normal boundary layer of the grid BC and are left alone; only deeper ones are
        projected back to that shell, once per frame. The vehicle is excluded: its
        particles are slaved to the body, whose contact is the plane's restitution
        impulse. self.leaked counts projected particle-frame events."""
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

    def step(self) -> dict:
        """Advance one frame; returns the rigid state after it."""
        self._project_water()
        self.solver.step(self.dt, self.substeps)
        self.time += 1.0 / self.fps
        state = self.solver.rigid_state()
        self.history.append(self.time, state, self.com0)
        return state

    def run(self, frames: int, callback=None) -> FloodHistory:
        for f in range(frames):
            state = self.step()
            if callback is not None:
                callback(f, self, state)
        return self.history

    # rendering helpers -----------------------------------------------------------
    def water_positions(self) -> np.ndarray:
        return self.solver.x()[: self.n_water]

    def vehicle_pose(self) -> tuple[np.ndarray, np.ndarray]:
        """(R, t) mapping vehicle-frame points into the scene: x_scene = R x_veh + t.
        Derived from x_scene = R (x_veh - com_veh) + com(t), where com_veh is the spawn
        com expressed in the vehicle frame."""
        st = self.solver.rigid_state()
        com_veh = self.com0 - self._place
        R = st["R"]
        t = st["com"] - R @ com_veh
        return R, t

    def splat_positions(self) -> np.ndarray | None:
        """The vehicle's visible splats moved rigidly with the body."""
        if self.vehicle.splat_pos is None:
            return None
        R, t = self.vehicle_pose()
        return self.vehicle.splat_pos @ R.T + t
