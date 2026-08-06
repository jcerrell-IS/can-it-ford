from __future__ import annotations

import numpy as np

from .config import BridgeConfig


def load_mpm_particles(npz_path: str):
    data = np.load(npz_path)
    return data["mpm_init_pos"], data["mpm_init_vol"], data["mpm_init_cov"]


def denormalize(pos: np.ndarray, transform: dict) -> np.ndarray:
    center = np.asarray(transform["center"], dtype=np.float64)
    scale = float(transform["scale"])
    grid_lim = float(transform["grid_lim"])
    return (pos.astype(np.float64) - 0.5 * grid_lim) / scale + center


def mpm_domain(pos: np.ndarray, n_grid: int, pad_cells: float = 3.0):
    lo = pos.min(axis=0).astype(np.float64)
    hi = pos.max(axis=0).astype(np.float64)
    dx = float(np.max(hi - lo) / n_grid)
    return (lo - pad_cells * dx).tolist(), (hi + pad_cells * dx).tolist(), dx


def to_genesis_scene(pos: np.ndarray, vol: np.ndarray, cov: np.ndarray,
                     config: BridgeConfig):
    pos = np.asarray(pos, dtype=np.float64)
    vol = np.asarray(vol, dtype=np.float64).reshape(-1)
    cov = np.asarray(cov, dtype=np.float64)
    if pos.shape[0] != vol.shape[0] or pos.shape[0] != cov.shape[0]:
        raise ValueError(
            f"to_genesis_scene: count mismatch pos={pos.shape[0]} vol={vol.shape[0]} cov={cov.shape[0]}"
        )
    if pos.shape[1] != 3 or cov.shape[1] != 6:
        raise ValueError(f"to_genesis_scene: expected pos (N,3) cov (N,6), got {pos.shape} {cov.shape}")

    lower, upper, dx = mpm_domain(pos, config.n_grid)
    return {
        "n_particles": int(pos.shape[0]),
        "lower_bound": lower,
        "upper_bound": upper,
        "dx": dx,
        "n_grid": int(config.n_grid),
        "pad_cells": 3.0,
        "seed_positions": pos.astype(np.float32),
        "particle_volume_mean": float(vol.mean()),
        "material": {"kind": "MPM.Liquid", "viscous": False, "mu": 0.0},
        "seeding_contract": (
            "size the seeding morph so its sampled particle count equals n_particles, "
            "call scene.build(), then MPMEntity.set_particles_pos(pos[None, ...]) "
            "with shape (1, n_particles, 3) before the first step"
        ),
        "UNVERIFIED": (
            "set_particles_pos shape and call ordering are taken from bridge/README.md "
            "Open questions #1 and have NOT been confirmed against live Genesis source "
            "in this session: Genesis is absent from LS6 and Vista is out of scope for "
            "this pane"
        ),
    }
