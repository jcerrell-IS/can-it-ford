from __future__ import annotations

import numpy as np

from .config import BridgeConfig


class FillAbort(Exception):
    pass


def _rasterize(pos, radius, lo, dx, n, halfwidth_cap):
    hw = np.floor(radius / dx).astype(np.int64)
    worst = int(hw.max()) if hw.size else 0
    if worst > halfwidth_cap:
        bad = int(np.argmax(hw))
        raise FillAbort(
            f"FILL_ABORT_RADIUS_EXCEEDS_CAP: Gaussian index {bad} has fill radius "
            f"{float(radius[bad]):.6f} scene units = {worst} voxels at dx={dx:.6f}, over the "
            f"cap of {halfwidth_cap}. Marking it alone would touch {(2*worst+1)**3} voxels. "
            f"Apply a scale filter (BridgeConfig.max_scale) before filling."
        )
    occ = np.zeros(n * n * n, dtype=bool)
    base = np.floor((pos - lo) / dx).astype(np.int64)
    np.clip(base, 0, n - 1, out=base)
    marks = 0
    for h in range(worst + 1):
        sel = hw == h
        if not np.any(sel):
            continue
        b = base[sel]
        if h == 0:
            offs = np.zeros((1, 3), dtype=np.int64)
        else:
            r = np.arange(-h, h + 1, dtype=np.int64)
            gx, gy, gz = np.meshgrid(r, r, r, indexing="ij")
            offs = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
        for o in offs:
            idx = b + o
            np.clip(idx, 0, n - 1, out=idx)
            lin = (idx[:, 0] * n + idx[:, 1]) * n + idx[:, 2]
            occ[lin] = True
            marks += lin.size
    return occ.reshape(n, n, n), marks


def _enclosed(occ):
    px = np.maximum.accumulate(occ, axis=0)
    nx = np.maximum.accumulate(occ[::-1], axis=0)[::-1]
    py = np.maximum.accumulate(occ, axis=1)
    ny = np.maximum.accumulate(occ[:, ::-1], axis=1)[:, ::-1]
    pz = np.maximum.accumulate(occ, axis=2)
    nz = np.maximum.accumulate(occ[:, :, ::-1], axis=2)[:, :, ::-1]
    return (px & nx & py & ny & pz & nz) & ~occ


def fill_internal_particles(pos: np.ndarray, vol: np.ndarray, cov: np.ndarray,
                            config: BridgeConfig):
    pos = np.asarray(pos, dtype=np.float64)
    cov_a = np.asarray(cov, dtype=np.float64)
    radius = np.sqrt(np.maximum(cov_a[:, 0] + cov_a[:, 3] + cov_a[:, 5], 0.0))

    plo = np.percentile(pos, 0.1, axis=0)
    phi = np.percentile(pos, 99.9, axis=0)
    ext = phi - plo
    dx = float(np.max(ext) / config.n_grid)
    lo = plo - 3.0 * dx
    n = int(np.ceil(float(np.max(ext) + 6.0 * dx) / dx))

    grid_bytes = n ** 3
    if grid_bytes > config.fill_max_grid_bytes:
        raise FillAbort(
            f"FILL_ABORT_GRID_MEMORY: n_grid resolves to {n}, so {grid_bytes} bytes of "
            f"occupancy grid, over fill_max_grid_bytes={config.fill_max_grid_bytes}. "
            f"Lower config.n_grid."
        )

    halfwidth_cap = max(1, int(np.ceil(0.05 * n)))
    occ, marks = _rasterize(pos, radius, lo, dx, n, halfwidth_cap)
    if marks > config.fill_max_marks:
        raise FillAbort(
            f"FILL_ABORT_WORK_EXCEEDED: rasterization performed {marks} voxel marks, over "
            f"fill_max_marks={config.fill_max_marks}."
        )
    inter = _enclosed(occ)

    ii = np.argwhere(inter)
    if ii.shape[0] == 0:
        return pos, np.asarray(vol).reshape(-1), np.asarray(cov)

    fpos = lo + (ii.astype(np.float64) + 0.5) * dx
    fvol = np.full(ii.shape[0], dx ** 3, dtype=np.float64)
    r = (3.0 * fvol / (4.0 * np.pi)) ** (1.0 / 3.0)
    fcov = np.zeros((ii.shape[0], 6), dtype=np.float64)
    fcov[:, 0] = r ** 2
    fcov[:, 3] = r ** 2
    fcov[:, 5] = r ** 2

    return (np.vstack([pos, fpos]),
            np.concatenate([np.asarray(vol).reshape(-1), fvol]),
            np.vstack([np.asarray(cov), fcov]))
