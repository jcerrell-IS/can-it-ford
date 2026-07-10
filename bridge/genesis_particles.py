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


def to_genesis_scene(pos: np.ndarray, vol: np.ndarray, cov: np.ndarray, config: BridgeConfig):
    raise NotImplementedError(
        "to_genesis_scene (TODO-6): build a Genesis MPM.Liquid scene seeded from these "
        "pre-positioned particles. OPEN QUESTION (REBUILD_REFERENCE.md): Genesis v1.2.0 may "
        "only support the per-step emitter pattern, not arbitrary pre-positioned initial "
        "particles. Verify against gs.options.MPMOptions / scene.add_entity BEFORE building "
        "this. Do not set mu on MPM.Liquid (viscous=False, mu=0.0). Pad the MPM domain 3*dx "
        "past the particle extent on every face."
    )
