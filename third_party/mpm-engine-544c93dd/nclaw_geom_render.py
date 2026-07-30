"""Shared PyVista surfacing and scene helpers for the recovery renders.

Not a standalone example: elastic_render.py imports _poly, _setup, and _view from here.
The helpers surface an MPM particle cloud (density field -> marching cubes -> Taubin
smoothing) and set up a shaded ground-plane scene with a soft cast shadow, coloured by
accumulated equivalent shear strain. The scene script that once drove this module
directly (an NCLaw bunny/dragon geometry-generalization render) lives in the research
tree, and its dumps are not part of this repo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "nclaw_compare"
GEOM = {"bunny": ("geom_bunny_truth", "geom_bunny_rec"),
        "dragon": ("geom_dragon_truth", "geom_dragon_rec")}
# per-shape surfacing voxel size (m) and a flattering camera azimuth (deg)
CFG = {"bunny": dict(h=0.0030, sigma=1.25, col="#d8b277", az=90),
       "dragon": dict(h=0.0021, sigma=1.20, col="#7fb069", az=130)}
TRUTH = dict(mu_s=0.38, delta_mu=0.26, I0=0.3)
MUHAT = dict(mu_s=0.377, delta_mu=0.247, I0=0.10)


def _accum_strain(L, times):
    """Accumulated equivalent shear strain eps(t,p) = int_0^t sqrt(2 D:D) dt', D = sym(L)."""
    dt = np.diff(times, prepend=times[0])
    D = 0.5 * (L + L.transpose(0, 1, 3, 2))
    gd = np.sqrt(2.0 * np.einsum("fpij,fpij->fp", D, D))
    return np.cumsum(gd * dt[:, None], axis=0)


def _surface(pts, h, sigma, iso_frac=0.30):
    """Density-field marching-cubes surface of a particle cloud (the standard MPM surfacing)."""
    from scipy.ndimage import gaussian_filter
    from skimage import measure
    lo = pts.min(0) - 4 * h
    hi = pts.max(0) + 4 * h
    dims = np.ceil((hi - lo) / h).astype(int) + 1
    idx = np.clip(np.floor((pts - lo) / h).astype(int), 0, dims - 1)
    fld = np.zeros(dims)
    np.add.at(fld, (idx[:, 0], idx[:, 1], idx[:, 2]), 1.0)
    fld = gaussian_filter(fld, sigma)
    verts, faces, *_ = measure.marching_cubes(fld, level=iso_frac * fld[fld > 0].mean(),
                                              spacing=(h, h, h))
    return verts + lo, faces


def _poly(pts, scalar, h, sigma):
    import pyvista as pv
    from scipy.spatial import cKDTree
    v, f = _surface(pts, h, sigma)
    pd = pv.PolyData(v, np.hstack([np.full((len(f), 1), 3), f]).astype(np.int64).ravel())
    if scalar is not None:
        _, nn = cKDTree(pts).query(v)
        pd["strain"] = scalar[nn]
    return pd.smooth_taubin(n_iter=18, pass_band=0.05)


def _view(x_all):
    """Fixed orthographic framing that fits every frame: focal point at the global bbox centre
    (biased toward the floor) and a view radius covering the global bounding diagonal."""
    lo = x_all.min(axis=(0, 1))
    hi = x_all.max(axis=(0, 1))
    ctr = 0.5 * (lo + hi)
    diag = float(np.linalg.norm(hi - lo))
    focal = np.array([ctr[0], ctr[1], lo[2] + 0.42 * (hi[2] - lo[2])])
    return focal, 0.52 * diag, float(lo[2]) - 0.002


def _setup(p, focal, view_radius, az, zfloor, elev=22.0):
    import pyvista as pv
    gp = pv.Plane(center=(focal[0], focal[1], zfloor), direction=(0, 0, 1),
                  i_size=8 * view_radius, j_size=8 * view_radius)
    p.add_mesh(gp, color="#eef0f3", ambient=0.55, diffuse=0.55, specular=0.0)
    p.enable_ssao(radius=0.012, bias=0.001)
    p.enable_anti_aliasing("ssaa")
    try:
        p.enable_shadows()
    except Exception:
        pass
    p.set_background("white")
    p.enable_parallel_projection()
    a = np.deg2rad(az)
    e = np.deg2rad(elev)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    p.camera.focal_point = tuple(focal)
    p.camera.position = tuple(focal + 4.0 * view_radius * d)
    p.camera.up = (0, 0, 1)
    p.camera.parallel_scale = view_radius
