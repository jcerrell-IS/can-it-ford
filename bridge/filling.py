from __future__ import annotations

import numpy as np

from .config import BridgeConfig


def fill_internal_particles(pos: np.ndarray, vol: np.ndarray, cov: np.ndarray, config: BridgeConfig):
    raise NotImplementedError(
        "fill_internal_particles (TODO-5): ORIGINAL reimplementation of PhysGaussian internal "
        "filling required. Algorithm (public, arXiv:2311.12198 Sec 3.7): densify an opacity "
        "field onto a grid, mark cells above fill_density_threshold, then flag interior empty "
        "cells via 6-axis ray casting + odd-intersection test, and add particles in accepted "
        "cells with cov = diag(r^2), r = (3V/4pi)^(1/3). DO NOT copy XPandora/PhysGaussian "
        "particle_filling/filling.py: its license is unresolved and this repo is public."
    )
