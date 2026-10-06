# `bridge/`: Gaussian splat to MPM particle bridge (unfinished scaffold)

This package is the planned link between a trained 3D Gaussian Splatting (3DGS) scene and the
particle simulation: it turns splat kernels into initial MPM particles, following the extraction
steps published in PhysGaussian (Xie et al. 2024, [arXiv:2311.12198](https://arxiv.org/abs/2311.12198)).

> **Status.** The splat-to-particles half is implemented: a 3DGS `.ply` loader, opacity filter,
> alignment, crop, normalisation, covariance and volume, optional interior filling, and `.npz`
> output (`python -m bridge.run_bridge scene.ply --output out/mpm_init.npz`). The solver hand-off
> is not: `to_genesis_scene` returns a seeding specification for Genesis `MPM.Liquid`, a solver the
> project later stopped using, and builds no scene. Every reported L2 result uses the `warpmpm`
> solver and starts from a vehicle mesh, not a splat, so no result depends on this package.
> `tests/test_bridge_roundtrip.py` checks the implemented half on a synthetic splat and a closed shell.

**Licensing.** `XPandora/PhysGaussian` publishes no licence, so this code is an independent
NumPy implementation of the published algorithm, not a copy of the upstream source. See
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Pipeline (maps to PhysGaussian `gs_simulation.py`, adapted)

| Stage | PhysGaussian ref | This scaffold | Status |
|---|---|---|---|
| 1. Load 3DGS checkpoint | none | `gaussian_io.load_gaussian_checkpoint` | done (`.ply` only) |
| 2. Opacity filter | `gs_simulation.py` L122-128 (`opacity > threshold`) | `extract.opacity_filter` | done |
| 3. Coordinate/rotation align | `gs_simulation.py` L138-142 | `extract.euler_rotation_matrix` + `apply_rotation` | done |
| 4. `sim_area` cuboid crop | `gs_simulation.py` L154-170 | `extract.crop_sim_area` | done |
| 5. Normalize to cube | centers to `[1,1,1]`, `grid_lim=2.0` | `extract.normalize_to_cube` | done |
| 6. Covariance + volume | `mpm_init_cov`, `mpm_init_vol` | `extract.gaussian_covariance`, `extract.particle_volume` | done |
| 7. Internal filling (optional) | `particle_filling/filling.py` | `filling.fill_internal_particles` | done |
| 8. **Intercept + save** | `gs_simulation.py` L241-245, before `MPM_Simulator_WARP(...)` | `gaussian_io.save_mpm_particles` → `.npz` | done |
| 9. Feed Genesis MPM.Liquid | none | `genesis_particles.to_genesis_scene` | specification only, no scene built |

The **intercept** is the whole point: PhysGaussian hands `mpm_init_pos`, `mpm_init_vol`,
`mpm_init_cov` to `MPM_Simulator_WARP`. We stop there and write those three arrays to disk
(`save_mpm_particles`), then load them into Genesis on the other side.

## Module map

- `config.py`: `BridgeConfig` (all knobs; defaults below).
- `gaussian_io.py`: `GaussianCloud` container, `.ply` checkpoint loader, `save_mpm_particles`.
- `extract.py`: stages 2 to 6.
- `filling.py`: optional interior filling (independent implementation).
- `genesis_particles.py`: load `.npz`; domain sizing and a Genesis `MPM.Liquid` seeding specification.
- `run_bridge.py`: command line, load then extract then save `.npz`.

## Defaults (sourced, see `docs/REBUILD_REFERENCE.md`)

| Param | Default here | Note |
|---|---|---|
| `opacity_threshold` | `0.05` | PhysGaussian demo default is `0.02`; use `0.05-0.1` for outdoor/flood, lower only if under-filled |
| `grid_lim` | `2.0` | PhysGaussian cube edge length |
| `n_grid` | `128` | real car geometry min; `64` tunnels thin panels (Genesis #600) |
| `fill_density_threshold` | `5.0` | PhysGaussian `decode_param.py` |
| `mu` (MPM.Liquid) | do **not** set | `viscous=False`, `mu=0.0` internally; setting `1e-3` is the same trap as the SPH `mu` bug |

## Remaining work

- Run the loader and extraction on the project's trained drainage-crossing splat and check the
  particle count, opacity threshold and axis alignment against the scene.
- Give the splat a metric scale (it has none yet) and decide between world metres and the
  normalised cube.
- Replace the Genesis seeding specification with a hand-off to `warpmpm`.

## Open questions (unresolved, do not assume)

1. **Does Genesis MPM accept pre-positioned initial particles, or only the per-step emitter
   pattern?** **Believed yes, not confirmed against Genesis source.** `MPMEntity.set_particles_pos(pos)`
   accepts an array of shape `(M, N, 3)` and is called after entity creation and `scene.build()`,
   before the first step. One caveat: the particle count `N` is fixed by the initial morph's
   sampling and cannot be set directly, so the seeding morph must be sized to match the bridge's
   actual particle count and its positions then overwritten. No emitter workaround
   or Genesis patch needed.
2. **Normalized vs world coordinates.** PhysGaussian's output is normalized to the `[0,2]`
   cube, not world meters. Either un-normalize back to metric before building the Genesis
   domain, or build the Genesis domain in the normalized space. Pick one and be consistent;
   the saved `transform` (center/scale) makes either reversible.
3. **Vehicle geometry is not in this bridge.** A trained splat is not a mesh; the rigid car
   comes from photogrammetry/CAD/download and is coupled separately (Piece 3/`box_sdf_collider_setup.py`).
