from __future__ import annotations

import numpy as np

from .config import BridgeConfig
from .filling import fill_internal_particles
from .gaussian_io import GaussianCloud


def opacity_filter(cloud: GaussianCloud, threshold: float) -> np.ndarray:
    return cloud.opacities.reshape(-1) > threshold


def euler_rotation_matrix(degrees: tuple[float, float, float]) -> np.ndarray:
    rx, ry, rz = (float(np.deg2rad(d)) for d in degrees)
    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    cz, sz = np.cos(rz), np.sin(rz)
    mx = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
    my = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
    mz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
    return (mz @ my @ mx).astype(np.float64)


def apply_rotation(positions: np.ndarray, rot: np.ndarray) -> np.ndarray:
    return positions @ rot.T


def crop_sim_area(positions: np.ndarray, sim_area) -> np.ndarray:
    if sim_area is None:
        return np.ones(positions.shape[0], dtype=bool)
    xmin, xmax, ymin, ymax, zmin, zmax = sim_area
    return (
        (positions[:, 0] >= xmin)
        & (positions[:, 0] <= xmax)
        & (positions[:, 1] >= ymin)
        & (positions[:, 1] <= ymax)
        & (positions[:, 2] >= zmin)
        & (positions[:, 2] <= zmax)
    )


def normalize_to_cube(positions: np.ndarray, grid_lim: float):
    lo = positions.min(axis=0)
    hi = positions.max(axis=0)
    extent = float(np.max(hi - lo))
    if extent <= 0.0:
        raise ValueError("normalize_to_cube: degenerate bounding box, extent <= 0")
    scale = grid_lim / extent
    center = 0.5 * (lo + hi)
    normalized = (positions - center) * scale + 0.5 * grid_lim
    transform = {"center": center, "scale": float(scale), "grid_lim": float(grid_lim)}
    return normalized, transform


def quaternion_to_matrix(quats: np.ndarray) -> np.ndarray:
    q = quats / np.linalg.norm(quats, axis=1, keepdims=True)
    w, x, y, z = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    n = q.shape[0]
    r = np.empty((n, 3, 3), dtype=np.float64)
    r[:, 0, 0] = 1.0 - 2.0 * (y * y + z * z)
    r[:, 0, 1] = 2.0 * (x * y - w * z)
    r[:, 0, 2] = 2.0 * (x * z + w * y)
    r[:, 1, 0] = 2.0 * (x * y + w * z)
    r[:, 1, 1] = 1.0 - 2.0 * (x * x + z * z)
    r[:, 1, 2] = 2.0 * (y * z - w * x)
    r[:, 2, 0] = 2.0 * (x * z - w * y)
    r[:, 2, 1] = 2.0 * (y * z + w * x)
    r[:, 2, 2] = 1.0 - 2.0 * (x * x + y * y)
    return r


def gaussian_covariance(scales: np.ndarray, rotations: np.ndarray) -> np.ndarray:
    rot = quaternion_to_matrix(rotations)
    m = rot * scales[:, None, :]
    sigma = m @ np.transpose(m, (0, 2, 1))
    pairs = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
    return np.stack([sigma[:, i, j] for i, j in pairs], axis=1)


def particle_volume(scales: np.ndarray) -> np.ndarray:
    return (4.0 / 3.0) * np.pi * np.prod(scales, axis=1)


def extract_mpm_particles(cloud: GaussianCloud, config: BridgeConfig):
    keep = opacity_filter(cloud, config.opacity_threshold)
    rot = euler_rotation_matrix(config.rotation_degrees)
    pos = apply_rotation(cloud.positions[keep], rot)
    scales = cloud.scales[keep]
    quats = cloud.rotations[keep]

    in_area = crop_sim_area(pos, config.sim_area)
    pos = pos[in_area]
    scales = scales[in_area]
    quats = quats[in_area]

    if pos.shape[0] == 0:
        raise ValueError("extract_mpm_particles: no particles survived opacity + sim_area filters")

    transform = None
    if config.normalize_to_cube:
        pos, transform = normalize_to_cube(pos, config.grid_lim)

    cov = gaussian_covariance(scales, quats)
    vol = particle_volume(scales)

    if transform is not None:
        s = transform["scale"]
        cov = cov * (s * s)
        vol = vol * (s ** 3)

    if config.fill_internal:
        pos, vol, cov = fill_internal_particles(pos, vol, cov, config)

    return pos.astype(np.float32), vol.astype(np.float32).reshape(-1), cov.astype(np.float32), transform
