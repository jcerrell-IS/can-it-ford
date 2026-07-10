from __future__ import annotations

import argparse

from .config import BridgeConfig
from .extract import extract_mpm_particles
from .gaussian_io import load_gaussian_checkpoint, save_mpm_particles


def run(config: BridgeConfig):
    cloud = load_gaussian_checkpoint(config.checkpoint_path)
    pos, vol, cov, transform = extract_mpm_particles(cloud, config)
    save_mpm_particles(config.output_npz, pos, vol, cov)
    return pos, vol, cov, transform


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="bridge.run_bridge",
        description="PhysGaussian-style 3DGS -> Genesis MPM particle bridge (scaffold)",
    )
    parser.add_argument("checkpoint")
    parser.add_argument("--output", default="out/mpm_init.npz")
    parser.add_argument("--opacity-threshold", type=float, default=0.05)
    parser.add_argument("--grid-lim", type=float, default=2.0)
    parser.add_argument("--n-grid", type=int, default=128)
    parser.add_argument("--fill-internal", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    config = BridgeConfig(
        checkpoint_path=args.checkpoint,
        output_npz=args.output,
        opacity_threshold=args.opacity_threshold,
        grid_lim=args.grid_lim,
        n_grid=args.n_grid,
        fill_internal=args.fill_internal,
    )
    run(config)


if __name__ == "__main__":
    main()
