"""Shared helpers for the example scripts.

Each demo stays runnable on its own; this module holds the pieces they would
otherwise copy from each other: the kernel-matched shear-rate measure, the
Chamfer metric, the ffmpeg frame-folder encoder, the Franka descent calibration
used by the press demos, and the particle-cloud surfacing used by the render
demos. Scripts under experiments/ import from here as well (they put this
directory on sys.path first).
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np

OUT_ROOT = Path(__file__).resolve().parents[1] / "out"


def device_cli(description: str | None = None, no_render: bool = False) -> argparse.ArgumentParser:
    """The argument parser every demo shares: --device, and optionally --no-render."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--device", default="auto",
                        help="Warp device: auto (cuda if available), cuda:N, or cpu")
    if no_render:
        parser.add_argument("--no-render", action="store_true", help="skip video rendering")
    return parser


def equivalent_shear_rate(L: np.ndarray, eps: float = 0.05) -> np.ndarray:
    """|gd|_eps = sqrt(2 dev(D):dev(D) + eps^2), D = sym(L), matching the warp kernel's
    regularized shear rate including the default eps."""
    D = 0.5 * (L + np.transpose(L, (0, 2, 1)))
    tr = (D[..., 0, 0] + D[..., 1, 1] + D[..., 2, 2]) / 3.0
    Dd = D - tr[..., None, None] * np.eye(3)
    dd = np.einsum("...ij,...ij->...", Dd, Dd)
    return np.sqrt(2.0 * dd + eps * eps)


def chamfer(a: np.ndarray, b: np.ndarray) -> float:
    """Symmetric Chamfer distance between two point clouds (mean nearest neighbour, both
    directions). Dense pairwise distances, meant for the few-hundred-point match sets the
    planners use."""
    d = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1) + 1e-18)
    return float(d.min(1).mean() + d.min(0).mean())


def write_mp4(frame_dir: Path, mp4: Path, fps: int = 16, pattern: str = "f_%04d.png") -> Path:
    """Encode a folder of numbered PNG frames to H.264. The scale filter rounds odd frame
    sizes down to even, which libx264 requires."""
    mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", str(Path(frame_dir) / pattern),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", str(mp4)],
                   check=True, capture_output=True)
    print("wrote", mp4)
    return mp4


def franka_descent_map(arm, frame_dt: float, cx: float, cy: float, z_ref: float,
                       a_ref: float = 0.30, n: int = 80) -> SimpleNamespace:
    """Calibrate the MuJoCo Franka's scripted descent against an MPM tool height.

    Samples the end-effector path once over the descent parameter a in [0, 1], then fixes
    the constant world-frame z offset that places the gripper tip at the MPM height z_ref
    when a = a_ref. Returns a_of (tool-top height in MPM coordinates to descent parameter),
    to_world (MPM points to the arm's world frame), the reference EE (x, y), and z_off.
    """
    a_grid = np.linspace(0.0, 1.0, n)
    ee = np.array([arm.set_descent(float(a), frame_dt)["pos"] for a in a_grid])
    arm._prev_ee = None
    ee_z = ee[:, 2]
    ex0, ey0 = float(ee[len(ee) // 2, 0]), float(ee[len(ee) // 2, 1])
    z_off = float(np.interp(a_ref, a_grid, ee_z)) - z_ref

    def a_of(tool_top_mpm: float) -> float:
        return float(np.interp(tool_top_mpm + z_off, ee_z[::-1], a_grid[::-1]))

    def to_world(p: np.ndarray) -> np.ndarray:
        out = np.empty_like(p)
        out[:, 0] = ex0 - cx + p[:, 0]
        out[:, 1] = ey0 - cy + p[:, 1]
        out[:, 2] = p[:, 2] + z_off
        return out

    return SimpleNamespace(a_of=a_of, to_world=to_world, ex0=ex0, ey0=ey0, z_off=z_off)


def surface_from_cloud(x: np.ndarray, cell: float = 0.0033, sigma: float = 1.3,
                       level: float = 0.18):
    """Particle cloud to isosurface mesh: splat onto a density grid, gaussian-smooth,
    marching cubes. Returns (world vertices, faces, unit face normals). Needs the
    'surface' extra (scipy, scikit-image)."""
    from scipy.ndimage import gaussian_filter
    from skimage.measure import marching_cubes

    mn = x.min(0) - 0.012
    mx = x.max(0) + 0.012
    dims = np.ceil((mx - mn) / cell).astype(int)
    rng = [(mn[i], mn[i] + dims[i] * cell) for i in range(3)]
    H, _ = np.histogramdd(x, bins=dims, range=rng)
    H = gaussian_filter(H.astype(float), sigma=sigma)
    H /= max(H.max(), 1e-9)
    verts, faces, _, _ = marching_cubes(H, level=level)
    vw = mn + verts * cell
    fn = np.cross(vw[faces[:, 1]] - vw[faces[:, 0]], vw[faces[:, 2]] - vw[faces[:, 0]])
    fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9
    return vw, faces, fn
