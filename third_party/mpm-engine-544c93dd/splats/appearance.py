"""Spherical-harmonic evaluation and filler-particle appearance.

The real-SH basis constants are the standard textbook normalization values (the same
ones used across 3D Gaussian Splatting code and the PlenOctree paper); they are written
out here and the evaluator is reimplemented in numpy. Filler particles are the interior
solid-fill points that make a thin splat shell behave as a body; this module decides how
they look, defaulting to inheritance from the nearest original splats.
"""
from __future__ import annotations

import numpy as np

# real spherical-harmonic normalization constants, degrees 0 through 3
C0 = 0.28209479177387814
C1 = 0.4886025119029199
C2 = (
    1.0925484305920792,
    -1.0925484305920792,
    0.31539156525252005,
    -1.0925484305920792,
    0.5462742152960396,
)
C3 = (
    -0.5900435899266435,
    2.890611442640554,
    -0.4570457994644658,
    0.3731763325901154,
    -0.4570457994644658,
    1.445305721320277,
    -0.5900435899266435,
)


def rgb_to_sh_dc(rgb: np.ndarray) -> np.ndarray:
    """Inverse of the DC render: the SH DC coefficient that renders to color rgb."""
    return (np.asarray(rgb, dtype=np.float32) - 0.5) / C0


def eval_sh(deg: int, sh: np.ndarray, dirs: np.ndarray) -> np.ndarray:
    """Evaluate real spherical harmonics up to degree 3 and return RGB colors.

    sh: (N, K, 3) coefficients with K >= (deg+1)^2 (DC at index 0). dirs: (N, 3) unit
    directions. Returns (N, 3) colors, clamped to [0, 1] after the +0.5 offset that
    matches the 3D Gaussian Splatting convention.
    """
    if not 0 <= deg <= 3:
        raise ValueError(f"eval_sh supports degree 0..3, got {deg}")
    sh = np.asarray(sh, dtype=np.float32)
    dirs = np.asarray(dirs, dtype=np.float32)
    result = C0 * sh[:, 0, :]
    if deg > 0:
        x = dirs[:, 0:1]
        y = dirs[:, 1:2]
        z = dirs[:, 2:3]
        result = result - C1 * y * sh[:, 1, :] + C1 * z * sh[:, 2, :] - C1 * x * sh[:, 3, :]
        if deg > 1:
            xx, yy, zz = x * x, y * y, z * z
            xy, yz, xz = x * y, y * z, x * z
            result = (
                result
                + C2[0] * xy * sh[:, 4, :]
                + C2[1] * yz * sh[:, 5, :]
                + C2[2] * (2.0 * zz - xx - yy) * sh[:, 6, :]
                + C2[3] * xz * sh[:, 7, :]
                + C2[4] * (xx - yy) * sh[:, 8, :]
            )
            if deg > 2:
                result = (
                    result
                    + C3[0] * y * (3.0 * xx - yy) * sh[:, 9, :]
                    + C3[1] * xy * z * sh[:, 10, :]
                    + C3[2] * y * (4.0 * zz - xx - yy) * sh[:, 11, :]
                    + C3[3] * z * (2.0 * zz - 3.0 * xx - 3.0 * yy) * sh[:, 12, :]
                    + C3[4] * x * (4.0 * zz - xx - yy) * sh[:, 13, :]
                    + C3[5] * z * (xx - yy) * sh[:, 14, :]
                    + C3[6] * x * (xx - 3.0 * yy) * sh[:, 15, :]
                )
    return np.clip(result + 0.5, 0.0, 1.0)


def _isotropic_cov6(n: int, sigma: float) -> np.ndarray:
    """(n, 6) upper-triangular covariance for an isotropic sigma^2 I Gaussian."""
    s2 = float(sigma) * float(sigma)
    cov = np.zeros((n, 6), dtype=np.float32)
    cov[:, 0] = cov[:, 3] = cov[:, 5] = s2
    return cov


def _median_nn_spacing(pos: np.ndarray) -> float:
    """Median nearest-neighbor distance of a point set (scipy cKDTree)."""
    from scipy.spatial import cKDTree

    if pos.shape[0] < 2:
        return 1.0
    tree = cKDTree(pos)
    d, _ = tree.query(pos, k=2)
    return float(np.median(d[:, 1]))


def assign_filler_appearance(cloud, filler_pos: np.ndarray, mode: str = "inherit",
                             k: int = 8, color=(0.72, 0.62, 0.5), opacity: float = 0.9,
                             sigma: float | None = None):
    """Appearance for M filler particles, aligned with cloud.sh_degree.

    Returns (cov6, opacity, sh): cov6 (M, 6), opacity (M, 1), sh (M, K, 3) with
    K = (cloud.sh_degree + 1)^2. cloud.pos and filler_pos must live in the same space.

    Modes:
      "inherit": average the sh and opacity of the k nearest original splats per filler;
                 covariance isotropic with sigma (default half the median filler spacing).
      "invisible": zero opacity and zero sh; isotropic covariance. n_visible drops these.
      "flat": DC-only sh from color, fixed opacity, isotropic covariance.
    """
    from scipy.spatial import cKDTree

    filler_pos = np.ascontiguousarray(filler_pos, dtype=np.float32)
    m = filler_pos.shape[0]
    kdim = (cloud.sh_degree + 1) ** 2
    if sigma is None:
        sigma = 0.5 * _median_nn_spacing(filler_pos)
    cov6 = _isotropic_cov6(m, sigma)

    if m == 0:
        return (cov6, np.zeros((0, 1), np.float32), np.zeros((0, kdim, 3), np.float32))

    if mode == "inherit":
        kq = int(min(max(k, 1), cloud.n))
        tree = cKDTree(cloud.pos)
        _, idx = tree.query(filler_pos, k=kq)
        idx = np.atleast_2d(idx.reshape(m, kq))
        sh = cloud.sh[idx].mean(axis=1).astype(np.float32)              # (M, K, 3)
        op = cloud.opacity.reshape(-1)[idx].mean(axis=1).astype(np.float32)[:, None]
        return (cov6, op, sh)

    if mode == "invisible":
        return (cov6, np.zeros((m, 1), np.float32), np.zeros((m, kdim, 3), np.float32))

    if mode == "flat":
        sh = np.zeros((m, kdim, 3), np.float32)
        sh[:, 0, :] = rgb_to_sh_dc(color)
        op = np.full((m, 1), float(opacity), np.float32)
        return (cov6, op, sh)

    raise ValueError(f"filler mode must be 'inherit', 'invisible', or 'flat', got {mode!r}")
