from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BridgeConfig:
    checkpoint_path: str
    output_npz: str = "out/mpm_init.npz"
    opacity_threshold: float = 0.05
    rotation_degrees: tuple[float, float, float] = (0.0, 0.0, 0.0)
    sim_area: tuple[float, float, float, float, float, float] | None = None
    grid_lim: float = 2.0
    n_grid: int = 128
    normalize_to_cube: bool = True
    fill_internal: bool = False
    fill_density_threshold: float = 5.0
