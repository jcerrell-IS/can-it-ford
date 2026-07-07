# Rebuild Reference (Piece 1-4 living document)

Source-cited research for the real-scene, real-MPM rebuild. Full unabridged version lives in Josie's local research files, this is the condensed, code-ready version. Treat as living, re-verify flagged items as the rebuild progresses, not a one-time answer.

---

## Headline corrections vs what was previously assumed

- **`coup_friction` Genesis default is `0.1`, not `0.0`.** The old pipeline's `coup_friction=0.0` was a hardcoded override, not what you get by doing nothing. `needs_coup` defaults to `True`.
- **Rigid material `rho` default is `600 kg/m3`** for basic objects (confirmed from source, not docs prose), below water's `1000`. Any rigid body without explicit `rho` floats. This is the same category as the box-proxy mass bug, will recur with a real mesh if not set again explicitly.
- **`MPM.Liquid` `mu` is not water viscosity, same trap as the SPH `mu` bug, different solver.** `viscous=False` by default, `mu=0.0` internally. Do not set `mu=1e-3` on MPM.Liquid thinking it matches real water, that's the SPH mistake repeating itself in a new place. Leave `viscous=False`.
- **`opacity_threshold=0.02` (PhysGaussian default) is confirmed exactly right for indoor demo objects, likely wrong for an outdoor flood scene.** Start at `0.05-0.1` for outdoor splats, only lower toward `0.02` if the object comes out under-filled.
- **PhysGaussian's output coordinates are normalized, not world meters.** Positions live in a unit cube centered at `[1,1,1]`. Must un-normalize before building a Genesis scene, or build the Genesis domain to match that normalized space instead.
- **A trained splat is not a mesh.** Vehicle rigid-body geometry has to come from somewhere else entirely, real photogrammetry, a CAD file, or a downloaded model, this is a separate sourcing step, not a byproduct of the splat.

---

## Validated Genesis source values (confirmed from source code, cited file)

| Parameter | Confirmed value | Source |
|---|---|---|
| `flush_cubes.py` dt | `4e-3` | Genesis examples/coupling |
| `flush_cubes.py` substeps | `20` | Genesis examples/coupling |
| `flush_cubes.py` grid_density | `64` | Genesis examples/coupling |
| `flush_cubes.py` emitter speed | `1.5 m/s` | Genesis examples/coupling |
| `MPM.Liquid` default rho | `1000.0` | genesis/engine/materials/MPM/liquid.py |
| `Rigid` default needs_coup | `True` | genesis/engine/materials/rigid.py |
| `Rigid` default coup_friction | `0.1` | genesis/engine/materials/rigid.py |
| `Rigid` default rho (unset) | `600` (basic objects) | genesis/engine/materials/rigid.py docstring |
| `Rigid` default sdf_cell_size | `0.005` (5mm) | genesis/engine/materials/rigid.py |
| PhysGaussian opacity_threshold default | `0.02` | utils/decode_param.py |
| PhysGaussian fill density_threshold | `5.0` | utils/decode_param.py |

**Realistic values, cited:**
- Sedan effective density: ~1200 kg/m3 (curb weight over volume, Shand et al. 2011 AR&R Book 7 Table 5.1)
- Tire-water coupling friction: 0.3-0.5 (ASTM E1337, wet rubber on submerged asphalt), matches the already-fixed `0.4`
- Grid density for a real car mesh: minimum 128, not 64, thin body panels tunnel through at 64 (issue #600)
- Domain sizing rule of thumb: >=2x vehicle length upstream/downstream, >=3x vehicle width laterally

---

## Genesis coupling examples, what each actually shows

- `water_wheel.py --solver mpm`: confirmed switches to `MPM.Liquid`. Fixed wheel, `dt=4e-3, substeps=10`, no `grid_density` override, emitter speed `5.0 m/s` (not 1.5, don't copy this one for velocity).
- `sand_wheel.py`: `coup_friction=0.2` set on the **plane**, not the wheel. Wheel itself uses `coup_softness`, not friction. `dt=3e-3, substeps=10, grid_density=64`.
- `rigid_mpm_attachment.py`: attachment constraints, not fluid drag, low relevance.
- **No canonical example anywhere of a free, non-fixed rigid vehicle-shaped body against MPM liquid.** Every public example uses `fixed=True`. This part of the build is genuinely novel, not a case of finding the right example to copy.

---

## Genesis SDF, answers Kumar's "MPM with SDF with any mesh to rigid body" comment directly

Every `Rigid` material carries `sdf_cell_size`, `sdf_min_res`, `sdf_max_res`, auto-generated from mesh geometry at scene build time. This is native, no custom code needed. For thin real-car features (door sills, bumper edges), set `sdf_cell_size` smaller than the 0.005m default.

---

## Bridge intercept point (Piece 2, the actual novel contribution)

PhysGaussian hands off to its Warp solver here:
```python
mpm_solver = MPM_Simulator_WARP(10)
mpm_solver.load_initial_data_from_torch(
    mpm_init_pos, mpm_init_vol, mpm_init_cov,
    n_grid=material_params["n_grid"], grid_lim=material_params["grid_lim"],
)
```
The intercept point is right before that instantiation. `mpm_init_pos` (N,3), `mpm_init_vol` (N,), `mpm_init_cov` (N,6), all float32. These three arrays are the entire bridge payload, save them to disk instead of handing them to Warp, then build a Genesis scene from them instead. Genesis's own MPM data structures do not accept Warp's array shapes directly, extract to numpy/torch first.

**Open, unconfirmed:** whether Genesis MPM supports loading arbitrary pre-positioned initial particles directly, versus only the per-step emitter pattern seen in `flush_cubes.py`. Flag for direct testing, not assumed either way.

---

## The 8-step pipeline, in execution order

1. **Splat capture.** Real video, >=20-30 overlapping images, 60%+ overlap, include the vehicle in frame, measure one real-world reference length for scale.
2. **Splat training (gsplat, LS6 A100s).** `--resolution 2` if VRAM exceeded on dense outdoor scenes.
3. **PhysGaussian-style extraction.** Run through `mpm_init_pos/vol/cov`, stop before Warp. Clip to vehicle + immediate water region with `sim_area` first, an unclipped outdoor scene fills ground and sky too. Pre-filter with `opacity_threshold>=0.05` to reduce the issue #47 hang risk from noisy floater Gaussians.
4. **Genesis MPM scene construction (water).** `grid_density=128` minimum for real geometry, domain sized to the real-scene rule of thumb, not the current tiny 2m box. `dt`/`substeps` must be re-derived via CFL for the new domain size, not ported blindly.
5. **Vehicle mesh sourcing.** Photogrammetry of the actual vehicle preferred, then CAD, then a downloaded model as last resort. Mandatory check before import: `python3 -c "import trimesh; m=trimesh.load('car.obj'); print(m.bounds)"`, confirm meters not centimeters.
6. **Rigid-MPM coupling.** `coup_friction=0.4` carries over as-is. Omit `fixed=True` for a free body. This exact path is untested anywhere publicly, treat it as the highest-uncertainty step in the whole rebuild.
7. **Run headless.** `show_viewer=False`. Pre-run check every time: `torch.cuda.is_available()`, `wp.init()` device count, `ti.init(arch=ti.cuda)` confirms cuda not cpu.
8. **Verdict computation.** Threshold logic (`lateral_drift>0.05m => NO-FORD`) carries over unchanged. New: classify divergence type when L1/L2 disagree, `L1_FORD_L2_NOFORD` (L1 misses persistent lateral drag, the core PVWM finding), `L1_NOFORD_L2_FORD` (L1 over-conservative), `BOTH_FORD`, `BOTH_NOFORD`.

---

## Legacy code migration map

| Block | Action |
|---|---|
| Sweep loop, output filename convention, CSV schema, verdict threshold | KEEP AS-IS |
| `SPH.Liquid(...)` | DELETE, replace with `MPM.Liquid(rho=1000)` |
| Box water volume | DELETE, replace with real particle positions from Piece 2 |
| Box vehicle | DELETE, replace with `gs.morphs.Mesh(file=car.obj)` |
| `rho=604` on vehicle | value was a synthetic-box proxy, use ~1200 for a real sedan mesh instead, not a direct port |
| `dt=4e-3` | keep as starting point, re-derive via CFL for the real domain, don't assume it still holds |
| `coup_friction=0.4` | keep exactly, just confirm it's attached to the new Rigid material |
| `mu=0.005` (SPH) | delete, no MPM analog, MPM.Liquid ignores viscosity by default |

---

## Known unresolved risks, not yet fixed by anyone

- PhysGaussian issue #47 (`fill_particles` hang on noisy covariance eigenvalues): status must be re-checked at `github.com/XPandora/PhysGaussian/issues/47` before each new real-scene reconstruction run, not assumed fixed.
- PhysGaussian license: no LICENSE file detected. Do not commit derived code to the public repo without resolving this first, either contact the maintainer or rewrite the extraction logic from the algorithm description rather than copying code.
- PhysSplatLab (Cheng-Hsi's own repo) requires sm_120 (RTX 5090/Blackwell), incompatible with Vista's GH200 (sm_90/Hopper) as written.
- Whether Warp's CUDA kernels JIT-compile correctly on GH200's sm_90a: verify with `wp.init(); wp.context.runtime.core.device_count()` before assuming it works.
- Whether Genesis MPM accepts arbitrary pre-positioned initial particles vs only the emitter pattern: untested, flag for direct testing at Step 4.

---

## Re-verification checklist (living document, check before each new run)

- PhysGaussian repo activity + issue #47 status
- Genesis release notes, especially MPM coupling API, if the container's Genesis version changes
- `opacity_threshold` optimal value, must be tuned per scene, not fixed globally
- `torch.cuda.is_available()`, `wp.init()` device count, `ti.init(arch=ti.cuda)`, all three, every time the container's dependencies change
