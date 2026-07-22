---
name: mpm-render-pipeline
description: Use this skill for the hands-on workflow of producing an MPM simulation render/video with kks32/mpm-engine for the Can It Ford project — environment setup on Vista, vehicle collider setup (box or SDF), water material config, the export-then-render process-isolation pattern, and matching Kumar's visualization conventions. Trigger on "render the MPM video", "set up the water/vehicle scene", "add_sdf_collider", "add_box collider", "export particle frames", "render_frames.py", "PyVista smoke test", "why did my render fail", "make this look like Kumar's figures", or any request to actually run/build/troubleshoot the kks32/mpm-engine pipeline end to end. Companion to geoelements-tech-reference (conceptual/API knowledge) and reu-research-log (progress tracking) — this skill is the hands-on production workflow, mirroring how splat-dataset-prep is the hands-on companion to geoelements-tech-reference for the gsplat half of the pipeline.
---

# MPM Render Pipeline: kks32/mpm-engine Production Workflow

Compiled July 8, 2026, from six cross-validated Perplexity research reports (commit-SHA and file/line cited where noted) plus direct chat-history verification. This skill is deliberately narrow: it covers **producing a render**, not general MPM theory (that's `geoelements-tech-reference`) and not logging progress (that's `reu-research-log`).

## 0. Standing rules (read first, every time)

1. **The current target is `kks32/mpm-engine`, per Kumar's direct Slack instruction.** Do not default to discussing Genesis's `MPM.Liquid` or `SPH.Liquid` unless explicitly asked. The SPH pilot study is closed.
2. **Never restate a prior claim about API/solver status as fact without checking the live source first.** This exact failure (confident claim → false on direct grep) has happened at least twice in this project.
3. **Never import Taichi/Genesis in the same process as PyVista/VTK/bpy.** Documented GPU-context collision risk (GLFW/EGL/CUDA). Always: simulate → save `.npz` → exit process → new process → render.
4. **When two sources disagree, say so — don't silently pick one.** See Section 1 for the two live disputes in this pipeline right now.

## 1. Open disputes — verify before trusting either side

### Dispute A: does `add_sdf_collider()` / `build_sdf()` actually work today?
- **Claims yes**, with a quoted docstring and a "cloned, installed, ran it successfully" statement, no commit SHA given.
- **Claims no**, citing the live README directly: shipped colliders today are a single kinematic box (`Solver.add_box`/`set_box`); mesh-to-SDF colliders are "Planned (empty stubs today)," roadmap item 1 of 6.
- A third, most rigorously sourced report (exact commit `2ff9caf547b62a9bca36385a05659a4184ee5a16`, file/line citations for every claim) confirms `solver.x()`/`solver.v()` are real but never checked collider APIs either way.
- **Default recommendation until resolved: use `Solver.add_box()` for the vehicle proxy.** It's confirmed by the more specific source, and the vehicle is a box anyway — this sidesteps the entire dispute and removes `trimesh`/SDF-voxelization as a dependency for tonight's render. Only reach for `add_sdf_collider`/`build_sdf` once you've personally confirmed on Vista (`python3 -c "from warpmpm... import add_sdf_collider"` or equivalent) that it's real, not planned.

### Dispute B: which render stack is "primary"?
- Resolved, not actually contradictory: **Matplotlib Agg + ffmpeg for tonight's first working video** (zero GPU-context risk, no aarch64 wheel gap, one report's fully worked example). **PyVista via `conda install -c conda-forge vtk pyvista` (not `pip install`) for later poster-quality renders**, once environment is proven with a one-frame smoke test. Blender: no official Linux-aarch64 build, skip. ParaView: heavy setup for the ROI here, skip unless a mentor specifically wants `.vtu`/ParaView-native output.

## 2. Environment setup (Vista GH200)

```bash
ssh jcerrell0629@vista.tacc.utexas.edu
python3 --version   # confirm 3.12.x; kks32/mpm-engine requires >=3.12,<3.13
cd /work/11603/jcerrell0629/vista/
git clone https://github.com/kks32/mpm-engine.git   # skip if already cloned
cd mpm-engine
python3 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu126   # adjust cu tag to match `nvidia-smi`; NEVER bare `pip install torch`, silently resolves CPU-only on aarch64
pip install "warp-lang>=1.10.1,<2" numpy scipy trimesh
pip install -e ".[dev,render]"
python3 -c "import warp as wp; wp.init(); print(wp.get_cuda_device_count())"   # must print >0 on a GPU node (idev first, not login node)
```

## 3. Vehicle collider setup

**Default path (recommended, per Dispute A above): `Solver.add_box()`.** No mesh, no SDF, no `trimesh` dependency:
```python
vehicle_center = (1.40, 1.50, floor_z + BOX_DIMS_M[2] / 2.0)
vehicle = solver.add_box(
    center=vehicle_center,
    size=(1.0, 1.6, 1.5),      # already-validated vehicle box dims, ~1450kg at rho=604
    friction=0.55,              # Azhar et al. 2023 + Smith et al. 2019, already cited
)
```

**Stretch path (only after confirming `add_sdf_collider` is real): `box_sdf_collider_setup.py`.** Already written, uses `trimesh.creation.box()` → `build_sdf_cached()` → `add_sdf_collider()`. Keep this on hand for when a real car mesh is sourced (Cheng-Hsi, Kumar, or Luke's tutorial — none confirmed to have one as of July 7, ask directly rather than searching blind).

## 4. Water material

```python
water = newtonian(eta=0.001, density=1000.0, bulk_modulus=2.0e5)
```
`eta=0.001` Pa·s is real water viscosity at ~20°C, not a project-specific tuning number — defensible as-is, cite as a basic physical constant if asked.

## 5. Run loop and export (canonical pattern)

```python
frames_x, frames_v, times = [], [], []
for step in range(n_steps):
    solver.step(dt, substeps=substeps)
    if step % export_every == 0:
        frames_x.append(solver.x().astype('float32').copy())   # method call, not property
        frames_v.append(solver.v().astype('float32').copy())
        times.append(step * dt)

np.savez_compressed(
    'water_box_rollout.npz',
    positions=np.asarray(frames_x, dtype=np.float32),
    velocities=np.asarray(frames_v, dtype=np.float32),
    times=np.asarray(times, dtype=np.float32),
    box_center=np.asarray(vehicle_center, dtype=np.float32),
    box_size=np.asarray((1.0, 1.6, 1.5), dtype=np.float32),
)
```
Exit the process here. Start a new one for rendering (Section 0, rule 3).

## 6. Render — primary path (matplotlib, use tonight)

```bash
python render_frames.py \
  --input water_box_rollout.npz \
  --output water_box_24fps.mp4 \
  --fps 24 \
  --box-center 1.40 1.50 0.75 \
  --box-size 1.0 1.6 1.5 \
  --max-points 200000 \
  --axis-off --show-floor
```
No `--input`: generates a synthetic demo, useful to test the renderer itself works before real sim data exists.

**Known gap to fix before poster/paper use:** current script colors water by speed using `cm.Blues`; Kumar's own GNS/CB-Geo work consistently uses **viridis** for displacement/velocity scalar fields (Section 8). Swap the colormap before final figures; fine to leave as-is for tonight's smoke test.

## 7. Render — secondary path (PyVista, poster-quality, later)

```bash
conda install -c conda-forge vtk pyvista   # NOT pip install — no official aarch64 PyPI wheel
unset DISPLAY
export PYVISTA_OFF_SCREEN=true EGL_PLATFORM=surfaceless VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow
python -c "
import pyvista as pv
pl = pv.Plotter(off_screen=True, window_size=(640,480))
pl.add_mesh(pv.Cube(), color='orange')
pl.screenshot('pv_smoke.png')
pl.close()
"
# If that smoke test opens an X connection, segfaults, or produces a black image: stop, use matplotlib instead.
python render_frames_pyvista.py --input water_box_rollout.npz --output water_box_pyvista.mp4 --fps 24 \
  --box-center 1.40 1.50 0.75 --box-size 1.0 1.6 1.5
```

## 8. Matching Kumar's visualization conventions

Confirmed-Kumar-authored sources only (Choi & Kumar 2023 arXiv:2305.05218, Kumar & Vantassel 2023 DOI:10.21105/joss.05025, Abram et al. 2022 DOI:10.1109/MCSE.2022.3155074). The CoRL 2026 PVWM paper is explicitly excluded here — anonymous submission, not confirmed as his own.

- Particles/points visible, not a smooth reconstructed surface only.
- Viridis for displacement/velocity magnitude scalar fields; categorical blue/black-gray/orange (water/boundary/vehicle) when the point is the scenario, not a specific field.
- Two-camera convention: top-down for lateral drift (this project's actual novelty over L1), 3/4 oblique for intuition. Side/profile inset when explaining depth.
- Fixed camera and fixed colorbar limits across every frame in a comparison set — never let scale drift between scenarios.
- Always pair the visual with a quantitative companion: lateral drift vs. time, D×V/L1 threshold marker, depth/velocity/verdict table. Never let the render carry the argument alone.
- Scale bar (poster) or labeled meter axes (paper).

## 9. Troubleshooting (only things actually hit or found in source, not guessed)

- `solver.x` / `solver.v` return bound methods, not arrays — always call with `()`.
- Bare `pip install torch` on Vista silently resolves to a CPU-only wheel on aarch64 — always use the explicit `--index-url`.
- `GridConfig`'s `n_grid`/`grid_lim` use a different domain-padding convention than Genesis's `grid_density`/bounds — don't port Genesis domain math over.
- Mesh not watertight → bad SDF. Check in a viewer before debugging physics, if using the SDF path at all.
- "particles outside solver boundary" → check `GridConfig` bounds against your water block's actual extent, not Genesis's padding rules.
- PyVista black frame / X-connection error / segfault → environment isn't actually headless-EGL-capable yet, fall back to matplotlib, don't debug further mid-deadline.

## 10. Data schema for a full parameter sweep (once past tonight's single render)

Full runnable pattern (deterministic run IDs, per-run `.npz` + summary manifest, lazy loader, Plotly phase-space export, retrospective W&B logging) lives in `mpm_sweep_data_schema.md` in project files — don't duplicate that here, it's 800+ lines of working code. Pull it in directly when you get to the sweep stage, not before.
