"""T1: shaded Yaris mesh in scene coordinates, per frame, from rollout.npz.

Source-verified against kks32/mpm-engine @ main (fetched 2026-07-25):
  vehicle.py load_vehicle : up-rotation, long-axis-to-y Rz, centre x/y, floor z=0
  dough_surface_render.py : LIGHT / Lambertian / Poly3DCollection recipe
  test_vehicle.py         : R @ p_veh + t = p_scene pose convention

The .ply on disk has its long axis on X. load_vehicle rotates it to Y. That
rotation is NOT in the v1 directive's T1c and must be applied before the
per-run rigid offset, or the car renders sideways.
"""
from __future__ import annotations

import numpy as np
import trimesh

PLY = "/Users/josie/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply"

# dough_surface_render.py:25
LIGHT = np.array([0.35, 0.55, 0.78])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# vehicle.py:243
RZ = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])

BODY = np.array([0.70, 0.13, 0.13])   # deep red
GLASS = np.array([0.42, 0.56, 0.64])  # blue-grey
TIRE = np.array([0.13, 0.13, 0.15])   # near-black rubber


def mesh_in_vehframe(face_count: int | None = 50_000):
    """Load the .ply and reproduce load_vehicle's orientation and placement.

    Returns (vertices_vehframe, faces, extent). Decimated if face_count is set.
    """
    m = trimesh.load(PLY, force="mesh")
    V = np.asarray(m.vertices, dtype=np.float64) @ RZ.T
    lo, hi = V.min(0), V.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2]])
    V = V - shift
    full = trimesh.Trimesh(vertices=V, faces=np.asarray(m.faces), process=False)
    extent = V.max(0) - V.min(0)
    if face_count is None or face_count >= len(full.faces):
        return np.asarray(full.vertices), np.asarray(full.faces), extent
    dm = full.simplify_quadric_decimation(face_count=face_count)
    return np.asarray(dm.vertices, dtype=np.float64), np.asarray(dm.faces), extent


def run_offset(d) -> np.ndarray:
    """T1b: per-run rigid translation from the raw vehframe array into the pose frame."""
    R = d["R"].astype(np.float64)
    t = d["t"].astype(np.float64)
    pv_raw = d["veh_particles_vehframe"].astype(np.float64)
    pv = (d["veh_particles_scene0"].astype(np.float64) - t[0]) @ R[0]
    dif = pv - pv_raw
    sd = dif.std(0)
    assert sd.max() < 1e-4, f"NON-RIGID OFFSET, std={sd}"
    return dif.mean(0)


def segment(Vv, F, extent):
    """T1e: geometric part segmentation in the VEHICLE frame, so it is pose-invariant.

    tires : z < 0.30*height AND |y - y_center| > 0.30*length
    glass : z > 0.55*height AND |normal_z| < 0.55
    body  : everything else
    """
    tri = Vv[F]
    fc = tri.mean(1)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    height, length = extent[2], extent[1]
    y_center = 0.0  # load_vehicle centres y
    tires = (fc[:, 2] < 0.30 * height) & (np.abs(fc[:, 1] - y_center) > 0.30 * length)
    glass = (fc[:, 2] > 0.55 * height) & (np.abs(n[:, 2]) < 0.55) & ~tires
    body = ~(tires | glass)
    base = np.repeat(BODY[None, :], len(F), axis=0)
    base[glass] = GLASS
    base[tires] = TIRE
    return base, {"tires": int(tires.sum()), "glass": int(glass.sum()),
                  "body": int(body.sum()), "total": len(F)}


def car_frame(Vv, F, base, off, R, t, f):
    """T1c + T1e: vertices and per-face colours for frame f, in scene coordinates."""
    V = (Vv + off) @ R[f].T + t[f]
    tri = V[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    sh = np.clip(n @ LIGHT, 0, 1) * 0.6 + 0.4        # dough_surface_render.py:79
    fc = np.clip(sh[:, None] * base, 0, 1)
    return V, tri, fc
