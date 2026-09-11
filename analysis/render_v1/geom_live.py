from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import trimesh

LIVE_SRC = Path(__file__).resolve().parent / "vehicle_live.py"
LIVE_SRC_PROVENANCE = {
    "origin": "/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py",
    "repo_head": "fd390d69ecfd1598f56803a215bb8d0eb7231d85",
    "working_tree_state": "M (uncommitted solidify_watertight patch, NOT in repo_head)",
    "md5": "4c3e8b2e3870194f9ec30f5398ca8407",
    "size_bytes": 22970,
    "mtime": "2026-07-25 18:25:42 -0500",
    "pulled": "2026-07-25",
}
YARIS = Path("/Users/josie/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply")
WANT = ("_up_rotation", "euler_zyx", "solidify_columns", "solidify_watertight")


def load_live_funcs(path: Path = LIVE_SRC) -> dict:
    tree = ast.parse(path.read_text())
    ns = {"np": np, "frozenset": frozenset}
    picked = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            try:
                mod = ast.Module(body=[node], type_ignores=[])
                exec(compile(ast.fix_missing_locations(mod), str(path), "exec"), ns)
            except Exception:
                pass
        if isinstance(node, ast.FunctionDef) and node.name in WANT:
            mod = ast.Module(body=[node], type_ignores=[])
            code = compile(ast.fix_missing_locations(mod), str(path), "exec")
            exec(code, ns)
            picked[node.name] = ns[node.name]
    missing = [w for w in WANT if w not in picked]
    if missing:
        raise RuntimeError(f"live functions not found in {path}: {missing}")
    return picked


LIVE = load_live_funcs()
up_rotation = LIVE["_up_rotation"]
euler_zyx = LIVE["euler_zyx"]
solidify_columns = LIVE["solidify_columns"]
solidify_watertight = LIVE["solidify_watertight"]


def orient(pos: np.ndarray, up: str = "z", target_length: float | None = None):
    R = up_rotation(up)
    pos = pos @ R.T
    ext = pos.max(0) - pos.min(0)
    if ext[0] > ext[1]:
        Rz = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        pos = pos @ Rz.T
        R = Rz @ R
    scale_applied = None
    if target_length is not None:
        scale_applied = target_length / float((pos.max(0) - pos.min(0))[1])
        pos *= scale_applied
    lo, hi = pos.min(0), pos.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    pos -= shift
    return pos, R, shift, scale_applied


class Body:
    def __init__(self, surface, extent, mesh, source):
        self.surface = surface
        self.extent = extent
        self.mesh = mesh
        self.source = source
        self.particles = None
        self.spacing = None

    def solidify(self, h: float, force_columns: bool = False):
        if self.mesh is not None and bool(self.mesh.is_watertight) and not force_columns:
            self.particles = solidify_watertight(self.mesh, h)
        else:
            self.particles = solidify_columns(np.asarray(self.surface, dtype=np.float64), h)
        self.spacing = h
        return self


def load_vehicle_local(path=YARIS, up: str = "z", n_sample: int = 60_000,
                       seed: int | None = 0, target_length: float | None = None) -> Body:
    src_mesh = trimesh.load(path, force="mesh")
    if seed is not None:
        np.random.seed(seed)
    pos = np.asarray(src_mesh.sample(n_sample), dtype=np.float64)
    pos, R, shift, scale_applied = orient(pos, up=up, target_length=target_length)
    mv = np.asarray(src_mesh.vertices, dtype=np.float64) @ R.T
    if scale_applied is not None:
        mv *= scale_applied
    mv -= shift
    oriented = trimesh.Trimesh(vertices=mv, faces=np.asarray(src_mesh.faces), process=False)
    extent = pos.max(0) - pos.min(0)
    return Body(surface=pos.astype(np.float32), extent=extent, mesh=oriented, source=str(path))


def scene_grid(extent: np.ndarray, depth: float, n_grid: int) -> dict:
    lim = float(max(2.2 * extent[1], 3.5 * extent[0], 6.0 * depth))
    dx = lim / n_grid
    h = dx / 2.0
    floor = 3.0 * dx
    n_layers = len(np.arange(floor + 0.5 * h, floor + depth, h))
    return {"lim": lim, "dx": dx, "h": h, "floor": floor, "water_layers": int(n_layers)}
