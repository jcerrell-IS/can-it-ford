from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class GaussianCloud:
    positions: np.ndarray
    opacities: np.ndarray
    scales: np.ndarray
    rotations: np.ndarray
    colors: np.ndarray | None = None

    def __len__(self) -> int:
        return int(self.positions.shape[0])


def load_gaussian_checkpoint(path: str) -> GaussianCloud:
    raise NotImplementedError(
        "load_gaussian_checkpoint (TODO-1): parse a trained 3DGS checkpoint "
        "(.ply/.sog/.pt from gsplat/LS6) into positions (N,3), opacities (N,), "
        "scales (N,3), rotations (N,4 quaternion). Confirm log-scale vs linear and "
        "quaternion order (w,x,y,z) vs (x,y,z,w) against the export. See bridge/README.md."
    )


def save_mpm_particles(path: str, pos: np.ndarray, vol: np.ndarray, cov: np.ndarray) -> None:
    import os

    if pos.shape[0] != vol.shape[0] or pos.shape[0] != cov.shape[0]:
        raise ValueError(
            f"particle count mismatch: pos={pos.shape[0]} vol={vol.shape[0]} cov={cov.shape[0]}"
        )
    if pos.shape[1] != 3 or cov.shape[1] != 6:
        raise ValueError(f"expected pos (N,3) and cov (N,6), got {pos.shape} and {cov.shape}")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    np.savez(
        path,
        mpm_init_pos=pos.astype(np.float32),
        mpm_init_vol=vol.astype(np.float32).reshape(-1),
        mpm_init_cov=cov.astype(np.float32),
    )
