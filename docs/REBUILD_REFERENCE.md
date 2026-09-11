# Rebuild Reference (Piece 1-4 living document)

Source-cited research for the real-scene, real-MPM rebuild, cross-validated across three independent research passes. Treat as living, re-verify flagged items as the rebuild progresses, not a one-time answer.

---

## New, real, and worth acting on: Cheng-Hsi already has flood splat data

His `SplatViewer` page links to a real Hugging Face dataset, `chhsiao93/hicss-splat`, with downloadable `.sog` files: `flood_high_scene.sog`, `flood_high_truck.sog`, `flood_high_water.sog`. He has already reconstructed a flood scene with a vehicle in it. This doesn't replace shooting real footage, but it's a real candidate for prototyping the Piece 2/3 bridge before your own capture exists. Whether the vehicle in that data is a real mesh or a placeholder sphere is genuinely unconfirmed either way across all three research passes, don't repeat either claim as settled, ask him directly.

---

## First real MPM test run, new finding not in any of the three research passes

`can_it_ford_L2_mpm.py` crashed on its very first `add_entity` call for the water box: `Entity has particles outside solver boundary`. Genesis's `MPMSolver` silently pads whatever `lower_bound`/`upper_bound` you specify inward by a safety margin, confirmed exactly `0.046875m` at `grid_density=64` (that's 3 grid cells, `dx=1/64=0.015625`, `3*dx=0.046875`). SPH does not do this, the same water box geometry that worked fine in the SPH script sits exactly on `z=0`, which is fine for SPH but outside MPM's actual usable interior once padding is applied.

**Fix applied:** domain expanded from `(0,-1,0)-(2,1,2.4)` to `(-0.1,-1,-0.1)-(2.1,1,2.5)`, giving more than double the required margin on the tight faces. General rule going forward: any MPM domain must extend at least `3*dx` past the outermost geometry on every face, not just past the vehicle/water as originally sized for SPH.

---

## Headline corrections vs what was previously assumed

- **`coup_friction` Genesis default is `0.1`, not `0.0`, confirmed across two independent research passes with pinned source lines.** The old pipeline's `coup_friction=0.0` was a hardcoded override in the code itself, not something Genesis does to you by default. `needs_coup` defaults to `True`.
- **Rigid material `rho` default is context-dependent, not a flat `600`.** Confirmed from source: `1000 kg/m3` for MuJoCo compatibility, `600 kg/m3` for basic objects, `1500 kg/m3` for poly-articulated robots. Regardless of which fallback applies, the point stands, any rigid body without explicit `rho` is not guaranteed to sink, set it explicitly every time.
- **`MPM.Liquid` `mu` is not water viscosity, same trap as the SPH `mu` bug, different solver.** `viscous=False` by default, `mu=0.0` internally. Do not set `mu=1e-3` on MPM.Liquid thinking it matches real water.
- **`opacity_threshold=0.02` is a PhysGaussian demo default, not a universal flood-scene value.** Start at `0.05-0.1` for outdoor splats, only lower toward `0.02` if the object comes out under-filled.
- **PhysGaussian's output coordinates are normalized, not world meters.** Must un-normalize before building a Genesis scene, or build the Genesis domain to match that normalized space instead.
- **A trained splat is not a mesh.** Vehicle rigid-body geometry has to come from somewhere else entirely, real photogrammetry, a CAD file, or a downloaded model.
- **No inlet/outlet API exists in Genesis v1.2.0**, confirmed across all three passes, with an exact source citation for the emitter pattern (`genesis/engine/scene.py`, `add_emitter`). Every liquid scene is closed/reflecting.
- **MPM pads the specified domain inward by `3*dx`.** Confirmed empirically on the first real run, see above. Domain construction must account for this, SPH does not have this behavior.

---

## Real vehicle mass, sourced, not guessed

EPA 2025 Automotive Trends Report: average new US vehicle weight MY2024 ~1,975 kg (4,354 lb), MY2025 preliminary ~2,014 kg (4,441 lb). If the specific vehicle class in your mesh isn't known, run sensitivity at 1,500 / 2,000 / 2,500 kg rather than picking one number and hoping. This is a stronger source than the earlier AR&R-table-based ~1200-1400 estimate, use this one going forward for a generic passenger vehicle.

---

## Validated Genesis source values (confirmed from source code, cited file, cross-checked)

| Parameter | Confirmed value | Source |
|---|---|---|
| `flush_cubes.py` dt | `4e-3` | genesis/examples/coupling |
| `flush_cubes.py` substeps | `20` | genesis/examples/coupling |
| `flush_cubes.py` grid_density | `64` | genesis/examples/coupling |
| `flush_cubes.py` emitter speed | `1.5 m/s` | genesis/examples/coupling |
| `MPM.Liquid` default rho | `1000.0` | genesis/engine/materials/MPM/liquid.py |
| `Rigid` default needs_coup | `True` | genesis/engine/materials/rigid.py, L81-95 |
| `Rigid` default coup_friction | `0.1` | genesis/engine/materials/rigid.py, L81-95 |
| `Rigid` default rho (unset) | context-dependent: 1000 / 600 / 1500 | genesis/engine/materials/rigid.py, L25-37 |
| `Rigid` default sdf_cell_size | `0.005` (5mm) | genesis/engine/materials/rigid.py |
| `MPMOptions` default domain | `(-1,-1,0)` to `(1,1,1)` | genesis/options/solvers.py, L569-621 |
| `MPMSolver` boundary safety padding | `3*dx` inward on every face | confirmed empirically, first real run, 0.046875m at grid_density=64 |
| PhysGaussian opacity_threshold default | `0.02` | gs_simulation.py, L123 + config/ |
| PhysGaussian fill density_threshold | `5.0` | utils/decode_param.py |

**Realistic values, cited:**
- Vehicle mass: 1,975-2,014 kg average (EPA 2025), sensitivity-test 1500/2000/2500 if class unknown
- Tire-water coupling friction: 0.3-0.5 (ASTM E1337, wet rubber on submerged asphalt), matches the already-fixed `0.4`
- Grid density for a real car mesh: minimum 128, not 64, thin body panels tunnel through at 64 (issue #600)
- Domain sizing rule of thumb: >=2x vehicle length upstream/downstream, >=3x vehicle width laterally, plus `3*dx` padding on every face for MPM specifically
- CFL sanity check at dt=4e-3, substeps=20, 1.5m/s, grid_density=128: per-substep travel ~0.0003m vs grid spacing ~0.0078m, ratio ~0.038, comfortably stable, not just "probably fine"

---

## Genesis coupling examples, what each actually shows

- `water_wheel.py --solver mpm`: confirmed switches to `MPM.Liquid`. Fixed wheel, `dt=4e-3, substeps=10`, no `grid_density` override, emitter speed `5.0 m/s` (not 1.5, don't copy this one for velocity).
- `sand_wheel.py`: `coup_friction=0.2` set on the **plane**, not the wheel. Wheel itself uses `coup_softness`, not friction. `dt=3e-3, substeps=10, grid_density=64`.
- `rigid_mpm_attachment.py`: attachment constraints, not fluid drag, low relevance.
- **No canonical example anywhere of a free, non-fixed rigid vehicle-shaped body against MPM liquid.** Confirmed across all three passes. This part of the build is genuinely novel.

---

## Vehicle mesh import, mandatory checks (new detail, not in earlier version of this doc)

`gs.morphs.Mesh` exposes `scale`, `pos`, `euler`, `quat`, `decimate`, `convexify`, `recompute_inertia`, `file_meshes_are_zup`, among others. `convexify` defaults to true for rigid collision, meaning a thin bumper or undercarriage can get simplified away silently unless audited.

**Before import, always check units:**
```bash
python3 -c "import trimesh; m=trimesh.load('car.obj'); print(m.bounds)"
```
A sedan in meters should show roughly `[[0,0,0],[4.5,1.8,1.5]]`. If it shows `[[0,0,0],[450,180,150]]`, the mesh is in centimeters, set `scale=0.01`.

**Validate mass after import, don't assume it applied:** Genesis's rigid pipeline can recompute inertia from geometry, confirm the resulting mass matches what you intended rather than trusting the `rho` argument was applied as expected.

---

## Genesis SDF, answers Kumar's "MPM with SDF with any mesh to rigid body" comment directly

Every `Rigid` material carries `sdf_cell_size`, `sdf_min_res`, `sdf_max_res`, auto-generated from mesh geometry at scene build time. This is native, no custom code needed. For thin real-car features, set `sdf_cell_size` smaller than the 0.005m default.

---

## Bridge intercept point (Piece 2, the actual novel contribution)

```python
mpm_solver = MPM_Simulator_WARP(10)
mpm_solver.load_initial_data_from_torch(
    mpm_init_pos, mpm_init_vol, mpm_init_cov,
    n_grid=material_params["n_grid"], grid_lim=material_params["grid_lim"],
)
```
Confirmed exact line range across two passes: `gs_simulation.py`, L241-245. Intercept right before this instantiation. `mpm_init_pos` (N,3), `mpm_init_vol` (N,), `mpm_init_cov` (N,6), all float32. Save these three to disk instead of handing them to Warp.

**Open, unconfirmed across all three passes:** whether Genesis MPM supports loading arbitrary pre-positioned initial particles directly, versus only the per-step emitter pattern. Flag for direct testing.

---

## Failure-mode taxonomy for verdict computation (new, maps directly to Kumar's stuck/slide/topple/float ask)

- **Lateral drift:** persistent sideways displacement under flow, the central reason L1 can miss danger.
- **Flotation/buoyancy:** vehicle loses effective ground contact or rises, tied to mass/density/underbody volume/water depth.
- **Tunneling/contact failure:** water particles pass through the collision geometry, indicates numerical invalidity, especially at coarse grid density.
- **Boundary clipping:** wake or vehicle hits the simulation box, indicates domain sizing error.
- **Inactive coupling:** L2 trajectory insensitive to coupling parameters, indicates a recurrence of the friction-invariant bug.

---

## The 8-step pipeline, in execution order

1. **Splat capture.** Real video, >=20-30 overlapping images, 60%+ overlap, include a known scale reference. Cheng-Hsi's existing flood splat dataset is a viable prototyping substitute while this step is pending.
2. **Splat training (gsplat, LS6 A100s).** `--resolution 2` if VRAM exceeded.
3. **PhysGaussian-style extraction.** Stop before Warp instantiation. Clip with `sim_area` first. Pre-filter with `opacity_threshold>=0.05` for outdoor scenes.
4. **Genesis MPM scene construction (water).** `grid_density=128` minimum for real geometry, domain sized to real-scene rule of thumb, plus `3*dx` padding.
5. **Vehicle mesh sourcing.** Photogrammetry preferred, then CAD, then downloaded model. Check units and validate resulting mass, don't assume.
6. **Rigid-MPM coupling.** `coup_friction=0.4` carries over. Omit `fixed=True` for a free body. Untested path anywhere publicly.
7. **Run headless.** `show_viewer=False`. Check `torch.cuda.is_available()`, `wp.init()` device count, `ti.init(arch=ti.cuda)`, every time.
8. **Verdict computation + failure-mode classification.** Use the taxonomy above, not just binary FORD/NO-FORD.

---

## Legacy code migration map

| Block | Action |
|---|---|
| Sweep loop, output filename convention, CSV schema, verdict threshold | KEEP AS-IS |
| `SPH.Liquid(...)` | DELETE, replace with `MPM.Liquid(rho=1000)` |
| Box water volume | DELETE, replace with real particle positions from Piece 2 |
| Box vehicle | DELETE, replace with `gs.morphs.Mesh(file=car.obj)` |
| `rho=604` on vehicle | synthetic-box proxy value, use EPA-sourced 1975-2014 kg (or 1500/2000/2500 sensitivity) for a real mesh instead |
| `dt=4e-3` | keep as starting point, re-derive via CFL for the real domain |
| `coup_friction=0.4` | keep exactly, confirm attached to the new Rigid material |
| `mu=0.005` (SPH) | delete, no MPM analog |
| MPM domain bounds | must add `3*dx` padding beyond geometry extent on every face, new rule, not in the original SPH-derived bounds |

---

## Known unresolved risks

- PhysGaussian issue #47 (`fill_particles` hang on noisy covariance eigenvalues): re-check status before each new reconstruction run.
- PhysGaussian and PhysSplatLab license: neither has a confirmed LICENSE file. Do not commit derived code publicly without resolving this.
- PhysSplatLab requires sm_120 (RTX 5090/Blackwell), incompatible with Vista's GH200 (sm_90/Hopper) as written.
- Whether Genesis MPM accepts arbitrary pre-positioned initial particles vs only the emitter pattern: untested.
- Whether Cheng-Hsi's flood splat truck is a real mesh or a placeholder: unconfirmed, ask him directly rather than assume either way.

---

## Re-verification checklist

- PhysGaussian repo activity + issue #47 status
- Genesis release notes if the container's Genesis version changes
- `opacity_threshold` optimal value, tuned per scene
- `torch.cuda.is_available()`, `wp.init()` device count, `ti.init(arch=ti.cuda)`, every dependency change
