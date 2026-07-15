# `bridge/` — PhysGaussian → Genesis MPM particle bridge (SCAFFOLD)

Piece 2 of the rebuild, and the project's actual novel contribution: take a trained 3D
Gaussian Splatting (3DGS) scene and turn its kernels into initial MPM particles that feed
**Genesis `MPM.Liquid`**, instead of PhysGaussian's own Warp/Taichi solver. No public
PhysGaussian→Genesis flood-scene bridge exists (verified: GitHub, local, arXiv all zero) —
this is the gap.

> **Status: scaffold only.** Signatures, data structures, and the pipeline skeleton are in
> place; the hard stages raise `NotImplementedError` with a pointer to the TODO below. It is
> not runnable end-to-end yet. That is intentional — stub structure first, then fill.

## ⚠️ License / attribution (read before writing any real logic)

`XPandora/PhysGaussian` has **no confirmed LICENSE file**, and `can-it-ford` is a **public**
GitHub repo. Per `REBUILD_REFERENCE.md`: *do not commit derived code publicly without
resolving this.* Therefore every stage here must be an **independent reimplementation from
the published algorithm** (Xie et al. 2024, arXiv:2311.12198), **not** a copy of
PhysGaussian's `gs_simulation.py` / `particle_filling/filling.py`. The algorithm is public;
their unlicensed source is not. Cite the paper, credit the repo as prior art, keep the code
original.

## Pipeline (maps to PhysGaussian `gs_simulation.py`, adapted)

| Stage | PhysGaussian ref | This scaffold | Status |
|---|---|---|---|
| 1. Load 3DGS checkpoint | — | `gaussian_io.load_gaussian_checkpoint` | stub (TODO-1) |
| 2. Opacity filter | `gs_simulation.py` L122-128 (`opacity > threshold`) | `extract.opacity_filter` | done |
| 3. Coordinate/rotation align | `gs_simulation.py` L138-142 | `extract.euler_rotation_matrix` + `apply_rotation` | done |
| 4. `sim_area` cuboid crop | `gs_simulation.py` L154-170 | `extract.crop_sim_area` | done |
| 5. Normalize to cube | centers to `[1,1,1]`, `grid_lim=2.0` | `extract.normalize_to_cube` | done |
| 6. Covariance + volume | `mpm_init_cov`, `mpm_init_vol` | `extract.gaussian_covariance`, `extract.particle_volume` | done (verify conventions) |
| 7. Internal filling (optional) | `particle_filling/filling.py` | `filling.fill_internal_particles` | stub (TODO-5) |
| 8. **Intercept + save** | `gs_simulation.py` L241-245, before `MPM_Simulator_WARP(...)` | `gaussian_io.save_mpm_particles` → `.npz` | done |
| 9. Feed Genesis MPM.Liquid | — (novel) | `genesis_particles.to_genesis_scene` | stub (TODO-6) |

The **intercept** is the whole point: PhysGaussian hands `mpm_init_pos`, `mpm_init_vol`,
`mpm_init_cov` to `MPM_Simulator_WARP`. We stop there and write those three arrays to disk
(`save_mpm_particles`), then load them into Genesis on the other side.

## Module map

- `config.py` — `BridgeConfig` (all knobs; defaults below).
- `gaussian_io.py` — `GaussianCloud` container; checkpoint load stub; `save_mpm_particles` (real).
- `extract.py` — stages 2-6, the PhysGaussian-adapted preprocessing (mostly real).
- `filling.py` — optional internal filling (stub; original reimpl required).
- `genesis_particles.py` — load `.npz`; build Genesis `MPM.Liquid` scene (stub).
- `run_bridge.py` — CLI orchestration: load → extract → save `.npz`.

## Defaults (sourced, see `REBUILD_REFERENCE.md`)

| Param | Default here | Note |
|---|---|---|
| `opacity_threshold` | `0.05` | PhysGaussian demo default is `0.02`; use `0.05-0.1` for outdoor/flood, lower only if under-filled |
| `grid_lim` | `2.0` | PhysGaussian cube edge length |
| `n_grid` | `128` | real car geometry min; `64` tunnels thin panels (Genesis #600) |
| `fill_density_threshold` | `5.0` | PhysGaussian `decode_param.py` |
| `mu` (MPM.Liquid) | do **not** set | `viscous=False`, `mu=0.0` internally; setting `1e-3` is the same trap as the SPH `mu` bug |

## TODO

- **TODO-1** `load_gaussian_checkpoint`: parse the gsplat/LS6 export (`.ply`/`.sog`/`.pt`) →
  positions (N,3), opacities (N,), scales (N,3), rotations (N,4). Confirm whether scales are
  log-scale and whether quaternions are `(w,x,y,z)` or `(x,y,z,w)` — `gaussian_covariance`
  assumes linear scales + `(w,x,y,z)`.
- **TODO-2** Validate `opacity_filter` threshold on a real flood splat (`chhsiao93/hicss-splat`).
- **TODO-3** Confirm rotation convention vs the real scene axes (PhysGaussian aligns bottom
  surface to the xy-plane; do the same for road surface).
- **TODO-4** Decide world-meters vs normalized-cube target (see Open questions).
- **TODO-5** `fill_internal_particles`: original reimpl of opacity-field densify + 6-axis ray
  interior test. License-gated — do not copy PhysGaussian.
- **TODO-6** `to_genesis_scene`: pre-positioned seeding is **confirmed supported** (see Open
  questions #1). `MPMEntity.set_particles_pos(pos)` takes shape `(M, N, 3)`, called after
  entity creation and `scene.build()`, before the first step. Remaining work: particle count
  `N` is fixed by the initial morph's sampling and is **not** directly settable, so
  `genesis_particles.py` must size the seeding morph to match the bridge's actual particle
  count, then overwrite positions with `set_particles_pos`.
- **TODO-7** Round-trip test: `run_bridge` on a tiny synthetic cloud → `.npz` → assert
  shapes/dtypes (`pos` f32 (N,3), `vol` f32 (N,), `cov` f32 (N,6)).

## Open questions (unresolved, do not assume)

1. **Does Genesis MPM accept pre-positioned initial particles, or only the per-step emitter
   pattern?** **Resolved: yes, pre-positioned seeding is supported.** `MPMEntity.set_particles_pos(pos)`
   accepts an array of shape `(M, N, 3)` and is called after entity creation and `scene.build()`,
   before the first step. One caveat: the particle count `N` is fixed by the initial morph's
   sampling and cannot be set directly, so the seeding morph must be sized to match the bridge's
   actual particle count and its positions then overwritten (see TODO-6). No emitter workaround
   or Genesis patch needed.
2. **Normalized vs world coordinates.** PhysGaussian's output is normalized to the `[0,2]`
   cube, not world meters. Either un-normalize back to metric before building the Genesis
   domain, or build the Genesis domain in the normalized space. Pick one and be consistent;
   the saved `transform` (center/scale) makes either reversible.
3. **Vehicle geometry is not in this bridge.** A trained splat is not a mesh; the rigid car
   comes from photogrammetry/CAD/download and is coupled separately (Piece 3/`box_sdf_collider_setup.py`).
