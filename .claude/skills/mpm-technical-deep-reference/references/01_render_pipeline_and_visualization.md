# MPM Render/Video Export Path for Headless Vista GH200

## Executive summary

The current `kks32/mpm-engine` source inspected at commit `2ff9caf547b62a9bca36385a05659a4184ee5a16` is a Warp-MPM engine, not a Taichi-MPM engine: its README names the project `warpmpm`, describes a modular Warp MPM engine, and states that the core is a validated `warp-mpm` fork with zero-copy Warp/PyTorch CUDA interoperability ([kks32/mpm-engine README](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/README.md#L1-L13)). The repository does **not** contain an implemented Taichi GGUI or `ti.ui` render path, but it does contain built-in Matplotlib, PyVista, ffmpeg/imageio, PLY, NPZ, and HDF5-oriented export/render utilities in examples and support modules ([kks32 `pyproject.toml`](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/pyproject.toml#L12-L26)).

The most reliable video path for Vista GH200 headless Apptainer jobs is: export particle state arrays from the simulation as `.npz` or per-frame `.npz`, then render PNG frames with Matplotlib's non-interactive Agg backend and encode them with ffmpeg or `imageio-ffmpeg`. This avoids X11, OpenGL, EGL, OSMesa, GPU display devices, and Taichi Linux-aarch64 wheel availability, while matching the repository's own optional render dependency set (`matplotlib`, `imageio`, `imageio-ffmpeg`, `pillow`) ([kks32 `pyproject.toml`](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/pyproject.toml#L20-L26)).

PyVista off-screen rendering is a viable second path only after a smoke test inside the exact Apptainer image on the exact node class, because PyVista depends on VTK OpenGL backends and requires a working EGL or OSMesa runtime for true headless rendering. PyVista's current documentation says VTK 9.5+ can render off screen through EGL when `libegl1` is installed, but PyVista's own issue tracker still contains recent HPC/Singularity/EGL problems and intermittent headless rendering reports ([PyVista installation docs](https://docs.pyvista.org/getting-started/installation.html), [pyvista/pyvista#7212](https://github.com/pyvista/pyvista/issues/7212), [pyvista/pyvista#8225](https://github.com/pyvista/pyvista/issues/8225)).

Taichi GGUI is not recommended for Vista GH200 Linux-aarch64 headless rendering. Taichi documents `ti.ui.Window(..., show_window=False)` and `window.save_image()` for off-screen image output, but PyPI Taichi 1.7.4 does not publish Linux-aarch64 wheels and open Taichi issues explicitly request aarch64 Linux PyPI support and ARM CUDA build support ([Taichi GGUI docs](https://docs.taichi-lang.org/docs/ggui), [Taichi Window API](https://docs.taichi-lang.org/api/taichi/ui/window/), [PyPI Taichi files](https://pypi.org/project/taichi/1.7.4/#files), [taichi-dev/taichi#8369](https://github.com/taichi-dev/taichi/issues/8369), [taichi-dev/taichi#8631](https://github.com/taichi-dev/taichi/issues/8631)).

## What was inspected

The repository was cloned and searched directly, and the relevant source files were inspected for rendering and export code. The inspected commit was `2ff9caf547b62a9bca36385a05659a4184ee5a16`, so line anchors below refer to that version of the source.

The search terms included Taichi and GGUI names (`taichi`, `ti.ui`, `taichi.ui`, `GGUI`, `Window`, `gui.show`), Python visualization and video libraries (`matplotlib`, `pyvista`, `vtk`, `imageio`, `ffmpeg`, `PIL`, `cv2`), and geometry/data formats (`np.savez`, `h5py`, `plyfile`, `.ply`, `.vtk`). The only Taichi mentions found in the current source are comments/import-boundary checks rather than renderer code: one experiment comments that some baseline repositories need Taichi, `ident/io/schema.py` states that the identification I/O layer must stay pure and not import Taichi, and `tests/test_import_boundaries.py` lists Taichi as a forbidden import for `ident/` ([kks32 import boundary test](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/tests/test_import_boundaries.py#L1-L13), [kks32 HDF5/NPZ schema](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/ident/io/schema.py#L1-L8)).

## 1. Built-in visualization, rendering, and video export in `kks32/mpm-engine`

### Direct answer

`kks32/mpm-engine` has built-in visualization/export examples, but they are **Matplotlib/PyVista/Warp/ffmpeg/PLY/HDF5/NPZ**, not Taichi GGUI. The repository's packaging defines optional `render` dependencies as `matplotlib`, `imageio`, `imageio-ffmpeg`, and `pillow`; optional `surface` dependencies include `pyvista`; optional `io` includes `h5py`; and optional `splats` includes `plyfile` ([kks32 `pyproject.toml`](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/pyproject.toml#L20-L26)).

### Exact source findings

| Capability searched | Source finding | Exact files/lines |
|---|---|---|
| Taichi / `ti.ui` / GGUI | No implemented Taichi renderer was found; Taichi appears only in comments/import-boundary tests. | `tests/test_import_boundaries.py` forbids `taichi` imports inside `ident/` ([kks32 import boundary test](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/tests/test_import_boundaries.py#L1-L13)); `ident/io/schema.py` says the I/O layer is pure NumPy plus optional HDF5 and avoids Taichi/sim imports ([kks32 schema header](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/ident/io/schema.py#L1-L8)). |
| Matplotlib PNG and ffmpeg MP4 | Yes; `examples/common.py` has `write_mp4`, and `examples/dough_surface_render.py` renders a surface via Matplotlib Agg and calls `write_mp4`. | `write_mp4` constructs an ffmpeg command using H.264 and `yuv420p` ([kks32 common utilities](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/common.py#L50-L59)); `dough_surface_render.py` imports Matplotlib Agg, renders a 3D surface, saves PNGs, and writes an MP4 ([kks32 dough surface renderer](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/dough_surface_render.py#L43-L108)). |
| Matplotlib animation / FFMpegWriter | Yes; `experiments/shear_rollout_video.py` makes Matplotlib animations and saves MP4 files. | The script imports Matplotlib Agg and animation tooling, then uses `animation.FFMpegWriter` to save videos ([kks32 shear rollout video](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/experiments/shear_rollout_video.py#L28-L100), [kks32 shear 3D video](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/experiments/shear_rollout_video.py#L106-L149)). |
| PyVista off-screen video | Yes; examples use `pv.OFF_SCREEN=True`, `pv.Plotter(off_screen=True)`, movie writers, screenshots, and ffmpeg. | `examples/recovery/elastic_render.py` imports PyVista, creates off-screen plotters, opens MP4 writers, and writes frames ([kks32 elastic PyVista renderer](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/recovery/elastic_render.py#L37-L93)); `experiments/gripper_render_dough.py` reconstructs surfaces with SciPy/skimage, renders with PyVista off screen, saves PNG screenshots, and invokes ffmpeg ([kks32 gripper render setup](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/experiments/gripper_render_dough.py#L24-L36), [kks32 gripper PyVista/ffmpeg render](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/experiments/gripper_render_dough.py#L116-L159)). |
| ImageIO | Yes, but only in the `pour_franka.py` example's PNG-writing path. | `examples/pour_franka.py` imports `imageio.v2`, writes per-frame images, calls `write_mp4`, and also saves compressed particle state data ([kks32 Franka pour export loop](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/pour_franka.py#L360-L445), [kks32 Franka final export](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/pour_franka.py#L496-L504)). |
| Solver particle state export | Yes; the solver exposes NumPy and Torch getters for particle state. | `solver.x()` and `solver.v()` return particle position and velocity as NumPy arrays, and `x_torch()` / `v_torch()` return Torch tensors ([kks32 solver state exports](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/core/solver.py#L404-L485)). |
| PLY / Gaussian splat export | Yes; splat export writes per-frame INRIA-layout Gaussian-splat PLY files and can convert frame PLYs to `.sog`. | `splats/export.py` documents per-frame PLY export to Cheng-Hsi's SplatViewer, implements `export_frame_ply`, records `frame_0000.ply` sequences, and contains `.sog` conversion helpers ([kks32 splat export overview](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/export.py#L1-L10), [kks32 per-frame splat PLY export](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/export.py#L163-L195), [kks32 frame recorder](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/export.py#L198-L225), [kks32 SOG conversion](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/export.py#L238-L250)). |
| PLY file writer | Yes; Gaussian PLY output is implemented via `plyfile`. | `splats/io.py` defines `save_gaussians_ply` and uses `PlyData`/`PlyElement` to write Gaussian-splat PLY records ([kks32 splat PLY writer](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/io.py#L124-L158)). |
| HDF5 / NPZ | Yes; the identification schema supports `.npz` and `.h5` / `.hdf5` reads. | `ident/io/schema.py` states that the dump schema supports `.npz` and optional HDF5, and its loader branches on `.npz`, `.h5`, and `.hdf5` suffixes ([kks32 schema header](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/ident/io/schema.py#L1-L8), [kks32 schema loaders](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/ident/io/schema.py#L132-L143)). |

### Practical interpretation for the water + rigid box case

For Josie's water-particle + box-collider rollout, the engine already exposes the only state needed for an external renderer: particle positions via `s.x()` / `solver.x()` and velocities via `s.v()` / `solver.v()` ([kks32 solver state exports](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/core/solver.py#L404-L485)). The rigid box can be rendered from known collider parameters rather than from the particle dump, so the recommended export contract is a compact state file containing `positions`, optional `velocities`, `times`, and a small `box_center`/`box_size` metadata block.

## 2. Standard export patterns for per-frame MPM particle data

### Recommended minimal contract: `.npz`

The simplest robust data contract is a single compressed `.npz` file with `positions` shaped `(T, N, 3)`, optional `velocities` shaped `(T, N, 3)`, optional `times` shaped `(T,)`, and collider metadata. This contract matches the kks32 solver API, which exposes position and velocity arrays directly as NumPy data ([kks32 solver state exports](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/core/solver.py#L404-L485)).

```python
# inside the simulation script
frames_x, frames_v, times = [], [], []
for step in range(n_steps):
    solver.step()  # or the engine-specific stepping call
    if step % export_every == 0:
        frames_x.append(solver.x().astype('float32').copy())
        frames_v.append(solver.v().astype('float32').copy())
        times.append(step * dt)

np.savez_compressed(
    'water_box_rollout.npz',
    positions=np.asarray(frames_x, dtype=np.float32),
    velocities=np.asarray(frames_v, dtype=np.float32),
    times=np.asarray(times, dtype=np.float32),
    box_center=np.asarray([cx, cy, cz], dtype=np.float32),
    box_size=np.asarray([lx, ly, lz], dtype=np.float32),
)
```

The current kks32 `pour_franka.py` example uses the same overall idiom: it samples `s.x()` and `s.v()`, writes per-frame PNGs with ImageIO, writes per-frame compressed `.npz` files with particle positions/speeds and robot state, and saves a final compressed archive with `x`, `v`, volume, and density arrays ([kks32 Franka pour export loop](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/pour_franka.py#L360-L445), [kks32 Franka final export](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/pour_franka.py#L496-L504)).

### Per-frame `.npz` directory

For long rollouts or memory-constrained jobs, write one `.npz` file per exported frame instead of one large array. This makes failures recoverable and lets the render step process frames incrementally.

```python
out = Path('frames_npz')
out.mkdir(exist_ok=True)
for frame_id, step in enumerate(export_steps):
    # after stepping the solver
    np.savez_compressed(
        out / f'f_{frame_id:04d}.npz',
        x=solver.x().astype('float32'),
        v=solver.v().astype('float32'),
        t=np.float32(step * dt),
    )
```

This mirrors kks32's `pour_franka.py` pattern of writing `f_XXXX.npz` files with `x`, speed, and state values during the rollout ([kks32 Franka pour export loop](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/pour_franka.py#L398-L445)).

### PLY point clouds

PLY is useful for inspection in MeshLab, ParaView, Blender, SplatViewer, or custom viewers. The kks32 repository already has a Gaussian-splat PLY path that writes per-frame INRIA-layout PLY files through `export_frame_ply` and `FrameRecorder` ([kks32 splat export overview](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/export.py#L1-L10), [kks32 frame recorder](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/splats/export.py#L198-L225)).

```python
def write_xyz_ply(path, xyz):
    xyz = np.asarray(xyz, dtype=np.float32)
    header = (
        'ply\nformat binary_little_endian 1.0\n'
        f'element vertex {len(xyz)}\n'
        'property float x\nproperty float y\nproperty float z\n'
        'end_header\n'
    ).encode('ascii')
    with open(path, 'wb') as f:
        f.write(header)
        f.write(xyz.astype('<f4', copy=False).tobytes())
```

PhysGaussian follows the same research-code pattern: it saves frame data through `save_data_at_frame`, supports PLY and HDF5 output, writes HDF5 datasets including `x`, `v`, deformation/state tensors, and implements a binary little-endian PLY writer for particle positions ([PhysGaussian engine utilities](https://github.com/XPandora/PhysGaussian/blob/main/mpm_solver_warp/engine_utils.py#L9-L46), [PhysGaussian PLY writer](https://github.com/XPandora/PhysGaussian/blob/main/mpm_solver_warp/engine_utils.py#L49-L88)). PhysGaussian's main simulation loop writes PLY/HDF5 frame outputs when export flags are enabled, renders PNGs through its Gaussian renderer, and uses ffmpeg to compile an MP4 when `--compile_video` is set ([PhysGaussian simulation export loop](https://github.com/XPandora/PhysGaussian/blob/main/gs_simulation.py#L277-L328), [PhysGaussian render and ffmpeg path](https://github.com/XPandora/PhysGaussian/blob/main/gs_simulation.py#L330-L379)).

### HDF5 for larger datasets

HDF5 is appropriate when a rollout has many frames or particle attributes and random access matters. The current kks32 identification schema supports `.h5` / `.hdf5` loading through optional `h5py`, and the project declares `h5py>=3.10` under its `io` optional extra ([kks32 schema loaders](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/ident/io/schema.py#L132-L143), [kks32 `pyproject.toml`](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/pyproject.toml#L24-L26)).

```python
import h5py
with h5py.File('water_box_rollout.h5', 'w') as h5:
    h5.create_dataset('positions', data=np.asarray(frames_x, np.float32), compression='gzip')
    h5.create_dataset('velocities', data=np.asarray(frames_v, np.float32), compression='gzip')
    h5.create_dataset('times', data=np.asarray(times, np.float32))
    h5.attrs['box_center'] = np.asarray([cx, cy, cz], np.float32)
    h5.attrs['box_size'] = np.asarray([lx, ly, lz], np.float32)
```

### Taichi MPM references for export norms

Classic Taichi MPM examples often export rendered PNGs rather than raw state arrays. The Taichi `mpm128.py` example uses a GUI loop and comments that changing `gui.show()` to `gui.show(f'{frame:06d}.png')` writes images to disk ([Taichi `mpm128.py`](https://github.com/taichi-dev/taichi/blob/master/python/taichi/examples/simulation/mpm128.py#L171-L197)). Taichi's official export documentation also documents `ti.GUI.show(filename)` for image frames, `ti.tools.VideoManager` for MP4/GIF generation through ffmpeg, and `ti.tools.PLYWriter` for exporting mesh/particle coordinates to PLY ([Taichi export docs](https://docs.taichi-lang.org/docs/export_results)).

Yuanming Hu's Taichi MPM README describes the older 88-line MLS-MPM route: enable image I/O, write `tmp/XXXXX.png` frames, and run ffmpeg or `ti video 60` to produce `video.mp4` ([Yuanming Hu Taichi MPM README](https://github.com/yuanming-hu/taichi_mpm/blob/master/README.md#L67-L78), [Yuanming Hu Taichi MPM FAQ](https://github.com/yuanming-hu/taichi_mpm/blob/master/README.md#L219-L228)). Those examples support the general research practice of exporting either raw states (`.npz`, HDF5, PLY) or rendered frames, but for a Vista GH200 no-display job the raw-state-first pattern is safer.

## 3. Headless GH200 Apptainer MP4 paths: reliability comparison

| Approach | Headless aarch64 container status | Strengths | Failure modes | Recommendation |
|---|---|---|---|---|
| Matplotlib Agg + ffmpeg / `imageio-ffmpeg` | Confirmed by architecture: CPU-only rendering, no DISPLAY, no OpenGL; PyPI publishes Linux-aarch64 wheels for Matplotlib and Pillow, and `imageio-ffmpeg` publishes a manylinux2014 aarch64 wheel ([PyPI Matplotlib files](https://pypi.org/project/matplotlib/3.11.0/#files), [PyPI Pillow files](https://pypi.org/project/Pillow/12.3.0/#files), [PyPI imageio-ffmpeg files](https://pypi.org/project/imageio-ffmpeg/0.6.0/#files)). | Most portable; works on MacBook, DesignSafe, Vista login/compute nodes; matches kks32 examples using Agg/ffmpeg. | Slower than GPU rasterization for millions of particles; 3D scatter occlusion is approximate; videos are communication artifacts, not simulation data. | **Primary path.** Use for Josie's water + box MP4 unless a higher-fidelity renderer is specifically required. |
| PyVista `Plotter(off_screen=True)` | Possible on Linux-aarch64 with VTK 9.5+/9.6 wheels plus EGL/OSMesa runtime; PyVista documents off-screen rendering with `libegl1` and `PYVISTA_OFF_SCREEN=true` ([PyVista installation docs](https://docs.pyvista.org/getting-started/installation.html), [PyVista Plotter API](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.html), [PyPI VTK files](https://pypi.org/project/vtk/9.6.2/#files)). | Better 3D camera, lighting, mesh surfaces, point sprites, and movies; kks32 already includes PyVista off-screen examples. | Requires working VTK OpenGL backend; Apptainer/Singularity can break EGL/library access; recent issues report HPC Singularity/EGL problems and intermittent headless EGL behavior. | **Secondary path.** Use only after a one-frame smoke test in the target container on Vista. |
| Taichi `ti.ui.Window(show_window=False)` | Taichi documents off-screen GGUI rendering, but Taichi 1.7.4 lacks Linux-aarch64 PyPI wheels and open issues request Linux aarch64 and ARM CUDA support ([Taichi GGUI docs](https://docs.taichi-lang.org/docs/ggui), [Taichi Window API](https://docs.taichi-lang.org/api/taichi/ui/window/), [PyPI Taichi files](https://pypi.org/project/taichi/1.7.4/#files), [taichi-dev/taichi#8369](https://github.com/taichi-dev/taichi/issues/8369), [taichi-dev/taichi#8631](https://github.com/taichi-dev/taichi/issues/8631)). | Good for native Taichi demos on supported platforms; can save images without showing a window. | Not a path implemented in current kks32 source; Linux-aarch64 install/build is the blocker; NVIDIA driver/GGUI issues exist. | **Do not use for Vista GH200 unless a custom Taichi build is already available and tested.** |

### Primary install and run recipe: Matplotlib Agg

Inside an Apptainer image or a writable venv layered on top of it:

```bash
python3 -m venv /tmp/mpm-render-venv
source /tmp/mpm-render-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install 'numpy>=1.26' 'matplotlib>=3.8' 'pillow>=10' 'imageio-ffmpeg>=0.4.9'
python - <<'PY'
import shutil, imageio_ffmpeg
print('system ffmpeg:', shutil.which('ffmpeg'))
print('imageio-ffmpeg:', imageio_ffmpeg.get_ffmpeg_exe())
PY
python /home/user/workspace/render_frames.py \
  --input water_box_rollout.npz \
  --output water_box.mp4 \
  --fps 24 \
  --box-center 0.25 0.0 0.18 \
  --box-size 0.35 0.28 0.28 \
  --max-points 200000
```

The script uses a system `ffmpeg` if present and falls back to the ffmpeg executable provided by `imageio-ffmpeg` if system ffmpeg is missing. This matches kks32's own `write_mp4` pattern, which shells out to ffmpeg with H.264 and `yuv420p` output for broad MP4 compatibility ([kks32 common utilities](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/examples/common.py#L50-L59)).

### Optional PyVista smoke test

Run this before trusting PyVista in a batch job:

```bash
unset DISPLAY
export PYVISTA_OFF_SCREEN=true
export EGL_PLATFORM=surfaceless
export VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow
python - <<'PY'
import pyvista as pv
pl = pv.Plotter(off_screen=True, window_size=(640, 480))
pl.add_mesh(pv.Cube(), color='orange')
pl.screenshot('pv_smoke.png')
print(type(pl.ren_win).__name__)
pl.close()
PY
```

This smoke test follows PyVista's documented `off_screen=True` Plotter API and environment-variable workflow for off-screen rendering ([PyVista Plotter API](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.html), [PyVista installation docs](https://docs.pyvista.org/getting-started/installation.html)). If the test opens an X connection, reports a bad X server connection, segfaults, or produces a black image, do not spend Vista allocation time on PyVista rendering; fall back to the Matplotlib script.

## 4. Known Taichi and PyVista issues relevant to GH200 / ARM / off-screen rendering

### Taichi issues

| Issue | Status / relevance | Why it matters for Vista GH200 |
|---|---|---|
| [taichi-dev/taichi#8369: Add aarch64 linux support to pypi.org](https://github.com/taichi-dev/taichi/issues/8369) | Open issue requesting Linux-aarch64 PyPI support. | Directly affects `pip install taichi` inside a GH200 Linux-aarch64 Apptainer container. |
| [taichi-dev/taichi#8756: why can not install taichi on aarch64 with pip?](https://github.com/taichi-dev/taichi/issues/8756) | Open user install issue for aarch64 pip. | Confirms that aarch64 installation remains a user-visible problem. |
| [taichi-dev/taichi#8631: Build ARM CUDA](https://github.com/taichi-dev/taichi/issues/8631) | Open build issue for ARM CUDA on linux-aarch64. | GH200 combines Grace ARM CPU and NVIDIA GPU, so ARM CUDA build support is the relevant platform axis. |
| [taichi-dev/taichi#7916: Building on Arm64 (Jetpack 5.1.1)](https://github.com/taichi-dev/taichi/issues/7916) | Open ARM64 build issue. | Not GH200-specific, but it reinforces that ARM64 Taichi builds require special handling. |
| [taichi-dev/taichi#8727: GGUI compatibility issue with Nvidia driver](https://github.com/taichi-dev/taichi/issues/8727) | Open GGUI/NVIDIA driver crash/assertion report using `taichi.ui.Window`. | Even on non-aarch64 systems, GGUI can be driver-sensitive, so it is not the safest no-display path. |
| [taichi-dev/taichi#3853: EGL related issues](https://github.com/taichi-dev/taichi/issues/3853) | Open issue discussing EGL behavior with `DISPLAY` and true headless NVIDIA rendering. | It shows that EGL setup can depend on environment variables and NVIDIA driver server-visualization support. |

No direct Taichi GitHub issue was found that specifically names GH200 or Grace Hopper and provides a confirmed rendering failure. The relevant blockers are broader but still decisive: Linux-aarch64 packaging, ARM CUDA build support, and GGUI/NVIDIA/EGL fragility.

### PyVista issues

| Issue | Status / relevance | Why it matters for Vista GH200 |
|---|---|---|
| [pyvista/pyvista#4305: Installing PyVista on arm64 linux](https://github.com/pyvista/pyvista/issues/4305) | Closed; from the pre-VTK-aarch64-wheel era, maintainers noted that VTK did not then publish ARM64 Linux wheels and suggested building VTK or using conda-forge. | Historical context; current VTK wheels improve the situation, but aarch64 PyVista has been a known packaging concern. |
| [pyvista/pyvista#2142: EGL not detected](https://github.com/pyvista/pyvista/issues/2142) | Closed; discusses Docker/headless GPU rendering and VTK builds with EGL, with later comments mentioning Singularity/Apptainer and `vtk-egl` wheels. | Shows why EGL/OSMesa backend choice matters for containerized HPC rendering. |
| [pyvista/pyvista#7212: Clearing up documentation for headless setups](https://github.com/pyvista/pyvista/issues/7212) | Open; user reports Docker-to-Singularity conversion causing VTK/EGL access problems on an HPC cluster. | Very close operationally to Apptainer on TACC: a renderer working in Docker may fail when converted to Singularity/Apptainer. |
| [pyvista/pyvista#8225: Intermittent rendering when using headless EGL on a GPU](https://github.com/pyvista/pyvista/issues/8225) | Open; reports intermittent headless EGL behavior on H100 with VTK 9.5.2 and PyVista 0.46.4, including a bad X server connection warning. | Modern NVIDIA data-center GPUs can still hit off-screen EGL instability; GH200 should be smoke-tested rather than assumed safe. |
| [pyvista/pyvista#6234: Error while using Pyvista with vtk-osmesa](https://github.com/pyvista/pyvista/issues/6234) | Closed; involved `vtk-osmesa`, Python 3.12, and PyVista version compatibility. | If choosing OSMesa rather than EGL, PyVista/VTK/Python version compatibility still matters. |
| [pyvista/pyvista#7587: Support VTK 9.5.0](https://github.com/pyvista/pyvista/issues/7587) | Closed; discussion includes aarch64/GH200-related VTK wheel context and CI stabilization around VTK 9.5. | This is the closest PyVista issue to GH200/aarch64 wheel availability, but it is not a TACC Vista-specific failure report. |

No PyVista issue was found that documents a reproducible TACC Vista GH200-specific rendering bug. The practical risk is not the GH200 GPU alone; it is the combination of Linux-aarch64 wheels, Apptainer library binding, EGL/OSMesa backend selection, and batch-node environment variables.

## 5. Complete runnable rendering examples

Two runnable scripts were saved in the workspace:

- `/home/user/workspace/render_frames.py`: primary Matplotlib Agg renderer for `.npz` frame arrays or a directory of per-frame `.npz` files.
- `/home/user/workspace/render_frames_pyvista.py`: optional PyVista off-screen renderer to use only after a successful one-frame smoke test.

`render_frames.py` accepts arrays shaped `(T, N, 3)` or `(N, 3)`, renders water particles as blue points, colors them by speed when velocities are present, draws the rigid box collider as a translucent orange cuboid, writes PNG frames in a temporary directory, and encodes an H.264 MP4. It also generates a synthetic water-flow demo if no `--input` is supplied, so it can be tested immediately on MacBook, DesignSafe, or Vista without simulation data.

Example smoke test:

```bash
python /home/user/workspace/render_frames.py \
  --output /home/user/workspace/render_frames_demo.mp4 \
  --fps 24 \
  --width 960 \
  --height 720 \
  --max-points 5000 \
  --axis-off \
  --show-floor
```

Example on a real rollout file:

```bash
python /home/user/workspace/render_frames.py \
  --input /path/to/water_box_rollout.npz \
  --output /path/to/water_box_24fps.mp4 \
  --fps 24 \
  --box-center 0.25 0.0 0.18 \
  --box-size 0.35 0.28 0.28 \
  --max-points 200000 \
  --axis-off \
  --show-floor
```

Example PyVista run after a successful smoke test:

```bash
unset DISPLAY
export PYVISTA_OFF_SCREEN=true
export EGL_PLATFORM=surfaceless
export VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow
python /home/user/workspace/render_frames_pyvista.py \
  --input /path/to/water_box_rollout.npz \
  --output /path/to/water_box_pyvista.mp4 \
  --fps 24 \
  --box-center 0.25 0.0 0.18 \
  --box-size 0.35 0.28 0.28
```

## Where each step should run

| Step | MacBook | DesignSafe JupyterHub | Vista GH200 / LS6 |
|---|---:|---:|---:|
| Develop/export-state code pattern | Yes | Yes | Yes |
| Run small synthetic `render_frames.py` demo | Yes | Yes | Yes, but not necessary |
| Render MP4 from already-exported `.npz` | Yes for modest particle counts | Yes and recommended for analysis/communication | Yes if data is large or already on Lustre/scratch |
| Run the actual MPM simulation/export | Only for tiny tests | Usually no, unless CPU-only toy run | **Yes**, if the production solver and container target Vista GH200 |
| PyVista smoke test | Useful but not authoritative | Useful but not authoritative | **Required** before PyVista render jobs |
| Taichi GGUI render path | Not relevant to current kks32 source | Not recommended | Not recommended; would require custom Taichi Linux-aarch64/ARM CUDA validation |

For the Can It Ford? pipeline, the canonical L2 evidence should remain the numeric simulation state and decision metrics, not the video. The video is a communication artifact for the perceive-predict-control-guarantee story: it helps visualize the prediction/simulation stage of the pipeline, while the ford/no-ford verdict should be computed from exported state such as vehicle drift, lateral force, and particle/rigid-body trajectories. This keeps the visualization aligned with the PVWM abstraction argument and the gsplat-to-MPM bridge context identified by arXiv:2507.09005 and arXiv:2605.30542 ([Hsiao and Kumar arXiv:2507.09005](https://arxiv.org/abs/2507.09005), [Thorpe et al. arXiv:2605.30542](https://arxiv.org/abs/2605.30542)).

## Final recommendation

Use `.npz` or per-frame `.npz` as the first export target, because it is easy to produce from kks32's `solver.x()` / `solver.v()` accessors and easy to consume on any analysis machine ([kks32 solver state exports](https://github.com/kks32/mpm-engine/blob/2ff9caf547b62a9bca36385a05659a4184ee5a16/src/warpmpm/core/solver.py#L404-L485)). Render the first videos with `/home/user/workspace/render_frames.py`, because Matplotlib Agg plus ffmpeg avoids every display-stack dependency that commonly fails in headless Apptainer jobs. Use PyVista only if the Matplotlib output is not visually sufficient and the PyVista smoke test passes inside the target Vista container. Do not spend Vista allocation debugging Taichi GGUI unless the project explicitly returns to a Taichi-native solver build and Taichi Linux-aarch64 installation is already solved.
# Headless HPC Rendering Stack Comparison for Genesis MPM Particle Data

**Prepared for:** Josie Cerrell, NSF SCIPE REU, TACC/UT Austin — "Can It Ford?" project
**Scope:** PyVista (VTK) vs. ParaView (pvbatch/pvpython) vs. Blender (bpy) vs. matplotlib (mplot3d), for headless rendering of Genesis MPM (Taichi) fluid-particle + rigid-mesh data into poster-quality PNGs and MP4 animations, on x86 (Lonestar6, A100) and ARM/aarch64 (Vista, GH200 Grace Hopper) TACC nodes, inside Apptainer containers.

---

## Executive Summary

**Recommendation at a glance:**

- **For the poster static figure:** Use **PyVista off-screen rendering (VTK-based)**. It gives full control over camera, lighting, colormaps, and glyph/point-splatting for MPM particles, produces publication-quality raster or vector output at arbitrary DPI, has first-class conda-forge `linux-aarch64` builds, and as of VTK 9.5 ships EGL-based hardware off-screen rendering in the stock wheel with no `Xvfb` required ([PyVista installation docs](https://docs.pyvista.org/getting-started/installation.html)). If a more filmic/ray-traced look is wanted for the poster hero image only, Blender is an acceptable second choice, but it is heavier to set up on ARM.
- **For the MP4 animation:** Also **PyVista**, driving a `pyvista.Plotter` in an off-screen loop, writing frames with `Plotter.open_movie()` (which uses `imageio-ffmpeg` internally) or dumping PNGs and stitching with `ffmpeg` directly. This reuses the exact same scene-construction code as the static frame, which minimizes duplicate code between the poster figure and the animation ([PyVista Plotter API](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plot.html)).
- **Critical guidance — process isolation:** Render **in a separate, freshly-started Python process from the one running Genesis/Taichi MPM**, and only after the simulation for that run has fully finished (or per-frame with data flushed to disk). Do not `import taichi` (directly or transitively via `genesis`) and `import pyvista`/`vtk`/`bpy` in the same interpreter session. This mirrors the documented Genesis+Taichi+PyGEL3D GLFW class-collision crash on macOS ([Genesis issue #165](https://github.com/Genesis-Embodied-AI/Genesis/issues/165)) and is consistent with community reports of Taichi's own GPU/GLFW/Vulkan context being fragile when a second GPU-context-owning library initializes in-process ([Taichi GGUI docs](https://docs.taichi-lang.org/docs/ggui), [Taichi issue #8536](https://github.com/taichi-dev/taichi/issues/8536)). The clean, low-risk workflow is: **Genesis MPM → NPZ per frame on disk → exit process → new process → load NPZ → render**.

The table below compares the four candidates directly. Detailed reasoning for every cell follows in the four numbered sections.

| | **A. PyVista (VTK)** | **B. ParaView (pvbatch/pvpython)** | **C. Blender (bpy)** | **D. matplotlib (mplot3d)** |
|---|---|---|---|---|
| **ARM/GH200 (aarch64) support** | Strong. `vtk` and `pyvista` both published for `linux-aarch64` on conda-forge ([VTK conda-forge files](https://anaconda.org/channels/conda-forge/packages/vtk/files), [PyVista conda-forge](https://anaconda.org/conda-forge/pyvista)). PyPI `pip install vtk` aarch64 wheels are not officially published by Kitware — must use conda-forge or build from source with documented `manylinux2014_aarch64` recipe ([PyVista "Building VTK" docs](https://docs.pyvista.org/extras/building_vtk.html)). EGL off-screen is the default GPU backend on Linux since VTK 9.4/9.5 ([VTK 9.4 release notes](https://docs.vtk.org/en/latest/release_details/9.4/support-runtime-opengl-window-selection.html)). | Moderate. conda-forge ships prebuilt `linux-aarch64` ParaView 6.0.1 binaries with an `osmesa`-variant build string ([conda-forge ParaView files](https://anaconda.org/conda-forge/paraview/files/modal/info/67a93bdd3b7aeb138c56135c)); Debian/Fedora also package `arm64`/`aarch64` ParaView ([Debian packages.debian.org](https://packages.debian.org/sid/paraview)). No official PyPI wheel for any architecture — ParaView explicitly is not distributed as a pip wheel ([ParaView Discourse on Python packaging](https://discourse.paraview.org/t/adding-paraview-as-a-dependency-to-a-python-project/14649)). EGL headless build is documented and used on GPU clusters ([ParaView Offscreen docs](https://www.paraview.org/paraview-docs/latest/cxx/Offscreen.html)), but per-GPU-index EGL device selection on multi-GPU HPC nodes has open bug reports ([ParaView Discourse EGL device on HPC](https://discourse.paraview.org/t/pvbatch-with-egl-device-on-hpc/9262)). | Weak/unofficial. Blender.org publishes **no official Linux aarch64 build** ([Blender devtalk: ARM64 build](https://devtalk.blender.org/t/is-it-possible-to-compile-blender-for-linux-arm64/30125), [BlenderKit ARM64 guide](https://www.blenderkit.com/articles/blenderkit-on-arm64-linux/)). PyPI `bpy` wheel is published only for `manylinux glibc 2.28+ x86-64`, `macOS 11.0+ ARM64`, and `Windows ARM64` — **no linux-aarch64 wheel** ([bpy on PyPI](https://pypi.org/project/bpy/)). Community members have built Blender from source with CUDA/OptiX/Vulkan for aarch64 (e.g., NVIDIA GB10/DGX Spark) ([blender-arm64 build guide](https://github.com/CoconutMacaroon/blender-arm64/), [NVIDIA forum GB10 Blender build](https://forums.developer.nvidia.com/t/blender-5-0-and-5-1-0-running-on-gb10-with-cuda-optix-vulkan/351254)), but this is a from-source, self-maintained path, not something you can `pip install` on Vista today. | Trivial/universal. Pure-enough Python; conda-forge and PyPI both ship `linux-aarch64` / `manylinux_aarch64` wheels for matplotlib and its C-extension deps (numpy, pillow, freetype, kiwisolver) as a matter of course. No GPU context, no OpenGL/EGL/OSMesa needed at all — matplotlib's `Agg` backend rasterizes on the CPU. |
| **MP4 + static dual output** | Very easy. Same `Plotter` scene object produces both: `screenshot=True`/`plotter.screenshot('poster.png')` at any DPI via `window_size`, and `plotter.open_movie('out.mp4'); plotter.write_frame()` per timestep (uses `imageio-ffmpeg`, native MP4, no manual `ffmpeg` CLI call needed) — or `open_gif`. ~15–25 lines shared between both outputs. | Moderate. `pvbatch`/`pvpython` scripts use `SaveScreenshot()` for the poster PNG and the **Animation View + `SaveAnimation()`** for frame sequences, but `SaveAnimation` in batch mode most reliably writes an image sequence (PNG/JPEG) that must then be stitched with an external `ffmpeg` call for MP4 — ParaView does not robustly encode MP4 directly in headless batch scripting the way `pvpython` GUI export does. More boilerplate (pipeline + view + camera + animation scene setup) than PyVista for the same result. | Moderate-heavy for this use case. Blender natively renders MP4 via the Video Sequencer / FFmpeg output settings (`scene.render.image_settings.file_format = 'FFMPEG'`), so `blender -b file.blend -a` can emit an .mp4 directly ([Blender command-line rendering manual](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html)). But turning raw NPZ particle arrays into a Blender scene requires building mesh/point-cloud objects, materials, and a camera/light rig via the `bpy` API first — meaningfully more code than PyVista for a scatter-style MPM visualization, since Blender is a full DCC tool, not a plotting library. | Easy for animation via `matplotlib.animation.FuncAnimation` + `FFMpegWriter` (needs the `ffmpeg` binary on PATH; matplotlib does not bundle its own encoder) and a single `savefig(dpi=300)` for the poster frame ([Matplotlib animation guide](https://matplotlib.org/stable/users/explain/animations/animations.html)). Code is compact but visual quality/performance for O(10^4–10^6) MPM particles is the limiting factor (see Q2 detail). |
| **Apptainer setup weight (on top of existing PyTorch+Taichi image)** | Light–moderate. `pip install pyvista vtk` (or `vtk-osmesa` on x86) adds ~40–90 MB; needs `libgl1`, `libegl1`, `libopengl0`, `libxrender1` system packages ([PyVista installation docs](https://docs.pyvista.org/getting-started/installation.html)); no X server or `Xvfb` required when EGL is present ([VTK 9.4 runtime OpenGL selection](https://docs.vtk.org/en/latest/release_details/9.4/support-runtime-opengl-window-selection.html)). | Heavy. ParaView is not a pip package; a full binary/conda install is ~300 MB–1 GB depending on variant (conda-forge aarch64 build alone is ~33 MB compressed per package but pulls a large dependency graph: Qt-less "osmesa" builds are smaller, GUI builds much larger) ([conda-forge ParaView files](https://anaconda.org/conda-forge/paraview/files/modal/info/67a93bdd3b7aeb138c56135c)). Managing a separate ParaView Python environment/venv alongside the existing PyTorch+Taichi container is an added maintenance surface, and PyVista's own VTK can conflict with ParaView's bundled VTK if mixed in one venv ([ParaView Discourse: PyVista/VTK conflict warning](https://discourse.paraview.org/t/adding-paraview-as-a-dependency-to-a-python-project/14649)). | Heaviest. The `bpy` wheel itself is ~374 MB on PyPI for x86-64 ([bpy 5.0.1 on PyPI](https://pypi.org/project/bpy/)), and on aarch64 there is no wheel at all — a from-source build inside the container would be required, dragging in OpenColorIO/OpenImageIO/OpenEXR/Embree-class dependencies for a full DCC toolkit ([Blender ARM64 source build thread](https://devtalk.blender.org/t/linux-aarch64-source-build/35311)). Substantial container-image bloat and build-time cost for a tool being used only as a plotting backend. | Negligible. `matplotlib` is already a near-universal dependency of the scientific Python stack (very likely already present transitively via numpy/scipy/PyTorch tooling); no system graphics libraries needed at all. |
| **Taichi/GPU-context conflict risk (same process)** | Low risk **if rendered in a separate process**; nonzero risk in-process. VTK/PyVista's EGL or CUDA-interop paths and Taichi's own CUDA/Vulkan/OpenGL context both compete for GPU driver state; PyTorch+Taichi in the same process already show CUDA-context interplay issues reported by Taichi's own maintainers ([PyTorch forum: sharing CUDA context with Taichi](https://discuss.pytorch.org/t/share-the-cuda-context-created-by-pytorch/113359)), and Genesis (which wraps Taichi) has a documented, closed-but-illustrative GLFW/OpenGL class-collision crash when a second GPU-context library (PyGEL3D) loads in the same interpreter ([Genesis issue #165](https://github.com/Genesis-Embodied-AI/Genesis/issues/165)). Genesis maintainers also state flatly that headless rendering breakage inside Genesis is generally an environment/driver issue independent of Genesis itself ([Genesis discussion #908](https://github.com/Genesis-Embodied-AI/Genesis/discussions/908)). | Same category of risk as PyVista (also VTK-based, same EGL/OSMesa context machinery), plus its own multi-GPU EGL device-selection fragility on clusters ([ParaView Discourse EGL/HPC](https://discourse.paraview.org/t/pvbatch-with-egl-device-on-hpc/9262)). | Highest in-process risk profile: Blender/Cycles claims the GPU via CUDA/OptiX/Vulkan directly and is a large stateful application, not a lightweight library — the least advisable to ever import in the same process as Taichi. | **Zero.** matplotlib's default `Agg` backend is CPU-only software rasterization; it opens no OpenGL/EGL/CUDA/Vulkan context at all, so it is the only one of the four with no theoretical GPU-context collision risk in-process (this comes at the cost of far worse performance/quality for large particle counts, see below). |

**Bottom line on the conflict question (Q4), which the user flagged as most important:** regardless of which rendering library is chosen, the safe and standard mitigation is identical and non-negotiable for the GPU nodes (Vista GH200, LS6 A100): **run the MPM simulation to completion (or per-checkpoint), serialize particle positions/velocities/material IDs to NPZ on disk, exit the Taichi/Genesis process, then launch a brand-new Python process for rendering.** This sidesteps GLFW/EGL/Vulkan/CUDA context collisions entirely because no two GPU-context-owning libraries ever coexist in one address space. Only matplotlib's CPU-only path would be theoretically safe to run in-process with Taichi, but doing so is still not recommended because Taichi's CUDA context and driver state should not be sharing a process with other heavy libraries as a matter of hygiene — and the performance/quality argument favors a separate process regardless.

---

## 1. Confirmed ARM/aarch64 (GH200 Grace Hopper) compatibility as of 2026

### A. PyVista / VTK
VTK publishes official Python wheels for Windows, macOS (Intel and ARM), and Linux from `vtk.org`/PyPI, but **Kitware's PyPI/wheels.vtk.org channel does not currently offer a `linux-aarch64` wheel** — the VTK wheel-building documentation explicitly still targets `manylinux2014_x86_64` for the OSMesa variant on GitLab's registry, and a maintainer confirms on the VTK Discourse: "We don't provide wheels for linux-arm64. You can still build and run x86 docker image on mac" ([VTK Trame/Docker discussion](https://discourse.vtk.org/t/dockerizing-trame-application-with-vtk-osmesa-wheel/14755)). However, **conda-forge does ship native `linux-aarch64` builds of both `vtk` and `pyvista`** — e.g. `vtk-9.6.2-py312h4954c87_4.conda` and later builds are listed directly under the `linux-aarch64` platform on the conda-forge VTK feedstock and Anaconda.org file listing ([conda-forge VTK files](https://anaconda.org/channels/conda-forge/packages/vtk/files), [conda-forge vtk-feedstock CI matrix showing `linux_aarch64_python3.1x` variants](https://github.com/conda-forge/vtk-feedstock)), and `pyvista` itself is a pure-Python `noarch` conda-forge package layered on top ([PyVista conda-forge package](https://anaconda.org/conda-forge/pyvista)). Practically, this means: **on Vista (GH200/aarch64), install PyVista+VTK via `conda install -c conda-forge vtk pyvista` inside the Apptainer container**, not via `pip install vtk`, unless building VTK from source. PyVista's own documentation includes an explicit, tested procedure for building the `aarch64` manylinux wheel via `quay.io/pypa/manylinux2014_aarch64` Docker images with `mesa-libEGL-devel` for EGL support ([PyVista "Building VTK" — aarch64 section](https://docs.pyvista.org/extras/building_vtk.html)), confirming the aarch64 build path is real and documented, just not pre-published to PyPI by Kitware.

For off-screen backend choice on ARM: VTK 9.4+ automatically falls back from GLX → EGL → OSMesa at runtime based on system capability and prints the selected backend to console; this logic is architecture-agnostic and works identically on aarch64 as x86 ([VTK 9.4 runtime OpenGL window selection](https://docs.vtk.org/en/latest/release_details/9.4/support-runtime-opengl-window-selection.html), [VTK runtime settings docs](https://docs.vtk.org/en/latest/advanced/runtime_settings.html)). As of VTK 9.5, **EGL hardware-accelerated off-screen rendering works out of the box from the stock `vtk` wheel** once `libegl1` is installed system-side — no separate `vtk-osmesa` package or `Xvfb` is needed on GPU nodes ([PyVista installation docs — remote server section](https://docs.pyvista.org/getting-started/installation.html)). On GH200 nodes this is directly relevant: NVIDIA's official GH200 driver stack ships EGL/GLVND libraries, so `--nv`-mounted Apptainer containers should expose EGL the same way they do on x86 A100 nodes.

### B. ParaView
No official PyPI wheel exists for ParaView on any platform — Kitware explicitly states ParaView is "really difficult to make into a wheel," and PyPI distribution "isn't really on the schedule at all" ([ParaView Discourse: adding as Python dependency](https://discourse.paraview.org/t/adding-paraview-as-a-dependency-to-a-python-project/14649)). For aarch64 specifically: **conda-forge does publish native `linux-aarch64` ParaView 6.0.1 conda packages**, built with an `osmesa` label in the build string (e.g. `paraview-6.0.1-py312h171a4e2_8_osmesa`), confirming an OSMesa (software) off-screen-capable aarch64 build is maintained ([conda-forge ParaView aarch64 package](https://anaconda.org/conda-forge/paraview/files/modal/info/67a93bdd3b7aeb138c56135c)). Debian/Ubuntu also carry `arm64` ParaView packages in their repositories ([Debian ParaView package listing](https://packages.debian.org/sid/paraview)), and Fedora ships `aarch64` builds as well ([RPMFind ParaView aarch64 listings](https://rpmfind.net/linux/rpm2html/search.php?query=paraview-devel)). ParaView's own build documentation states officially tested/supported CI platforms are "Linux (x86_64), Windows (x86_64) and macOS (x86_64 and arm64)" — **aarch64 Linux is not an officially CI-tested target**, even though community/distro builds exist and work ([ParaView build documentation](https://www.paraview.org/paraview-docs/latest/cxx/md__builds_gitlab-kitware-sciviz-ci_Documentation_dev_build.html)). Users have successfully built the ParaView superbuild for "graphic-less ARM64" configurations from source, confirming the EGL/headless path is achievable on ARM but requires manual superbuild compilation rather than a turnkey binary from paraview.org ([ParaView Discourse: superbuild for ARM](https://discourse.paraview.org/t/advice-on-building-paraview-superbuild-for-openfoam-runtimepostprocessing/8707)). **Net for Vista: use the conda-forge aarch64 build, not the paraview.org binary tarball (which is x86_64/macOS/Windows only).**

### C. Blender (bpy)
This is the weakest link for ARM. The Blender Foundation does **not** provide official Linux aarch64/ARM64 builds — devtalk.blender.org explicitly confirms "It's not a configuration we ship" and that building "will be a bit of a struggle" ([Blender devtalk: ARM64 Linux build](https://devtalk.blender.org/t/is-it-possible-to-compile-blender-for-linux-arm64/30125)); BlenderKit's community guide states plainly: "Blender Foundation does not provide standard builds for aarch64/ARM64. Builds are only available for architecture x64_48 [sic, x86_64] on blender.org" ([BlenderKit ARM64 Linux guide](https://www.blenderkit.com/articles/blenderkit-on-arm64-linux/)). Checking PyPI directly for the `bpy` Python-module wheel confirms only four wheel files exist: **Windows ARM64, manylinux glibc 2.28+ x86-64, and macOS 11.0+ ARM64 — there is no `linux_aarch64` wheel published for `bpy` at all** ([bpy on PyPI, files list](https://pypi.org/project/bpy/)). Distro packages (Debian, ArchLinux ARM) do ship `aarch64`/`arm64` Blender application binaries built from source ([ArchLinux ARM Blender package](https://archlinuxarm.org/packages/aarch64/blender), [Debian package search](https://rpmfind.net/linux/rpm2html/search.php?query=paraview-devel)), and hobbyist/HPC-adjacent efforts have compiled Blender for ARM64 with CUDA/OptiX/Vulkan GPU support targeting NVIDIA's Grace-based GB10/DGX Spark platform — architecturally the same Grace CPU + NVIDIA GPU pairing as GH200 — with a documented from-source build script ([blender-arm64 CUDA/OptiX/Vulkan build guide](https://github.com/CoconutMacaroon/blender-arm64/), [NVIDIA Developer Forum: Blender 5.0/5.1 on GB10](https://forums.developer.nvidia.com/t/blender-5-0-and-5-1-0-running-on-gb10-with-cuda-optix-vulkan/351254)). This is encouraging evidence that Blender *can* run correctly with GPU rendering on Grace-Hopper-class ARM systems, but it means **on Vista, using Blender/bpy requires a self-maintained from-source build inside the Apptainer image** — there is no `pip install bpy` or `conda install blender` shortcut for aarch64 today.

### D. matplotlib (mplot3d)
matplotlib and its core dependencies (NumPy, Pillow, kiwisolver, fonttools, contourpy, freetype) all publish standard `manylinux_aarch64` PyPI wheels and `linux-aarch64` conda-forge builds as a routine part of their release process — this is by far the most mature and boring aarch64 story of the four tools, with no special-casing required. `mplot3d` and `matplotlib.animation` are pure-Python modules layered on the same backend, so there is no aarch64-specific concern at all beyond ensuring the `ffmpeg` system binary (needed only for the `FFMpegWriter`, not for static PNGs) is present in the container, which is architecture-independent and trivially available via `apt`/`conda` on aarch64.

---

## 2. Ease of producing a static poster frame AND an MP4 from the same per-frame particle data

Josie's data model is uniform across all four tools: each frame is a NPZ file with particle positions (and likely velocity/material-ID arrays for MPM fluid vs. rigid-body mesh vertices for the Ford vehicle). The question is how much glue code each tool needs to go from `positions = np.load(f"frame_{i:05d}.npz")["pos"]` to (a) one high-DPI PNG and (b) a full MP4.

**PyVista — easiest dual-output path.** A single `pv.Plotter` object, once configured with a `PolyData` point cloud (`pv.PolyData(positions)`) and a glyph/point-rendering style plus a rigid-body mesh (`pv.read("vehicle.obj")` or constructed from vertex arrays), directly supports both output modes:
- Static: `plotter.screenshot("poster.png")` (or `show(screenshot=...)`), with `window_size=(3840, 2160)` or higher for print-resolution posters, and PyVista also exposes vector/high-quality export paths.
- Animation: `plotter.open_movie("sim.mp4", framerate=30)` opens an MP4 writer directly (via `imageio-ffmpeg` under the hood) — then simply loop over frames, update point coordinates in place (`plotter.mesh.points = new_positions`), and call `plotter.write_frame()` each iteration ([PyVista Plotter API, `off_screen`/`screenshot` parameters](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plot.html)).
This means the exact same scene-setup code (camera position, colormap, lighting, mesh vs. particle glyph styling) is reused for both deliverables — typically under 40-60 lines total for both, since the only difference is the screenshot-vs-loop call at the end.

**ParaView — more boilerplate, no native MP4 encode in batch mode.** In `pvbatch`/`pvpython` scripts, the standard poster path is `SaveScreenshot(view, "poster.png", ImageResolution=[3840,2160])`. For an animation, ParaView's `SaveAnimation()` in scripted/batch mode most robustly writes a PNG (or JPEG) **image sequence** rather than a guaranteed-working direct MP4 encode — HPC visualization docs (e.g., ORNL/NCSA) describe the standard `pvbatch` workflow as headless rendering to frames, with MP4 assembly as a separate downstream step ([OLCF ParaView visualization docs](https://docs.olcf.ornl.gov/software/viz_tools/paraview.html), [NCSA Delta ParaView batch rendering docs](https://github.com/ncsa/Delta_doc/blob/main/docs/source/user_guide/visualization.rst)). Getting particle data into ParaView from NPZ also requires either writing a custom VTK/Python reader, exporting to a ParaView-native format (VTU/VTP) as an intermediate step, or using the `paraview.simple` scripting API's `TrivialProducer`/programmable source — more moving parts than PyVista's direct NumPy → `PolyData` path.

**Blender (bpy) — natively best MP4 encoder, worst point-cloud ergonomics.** Blender's render pipeline writes MP4 directly and natively via its FFmpeg-based video output (`scene.render.image_settings.file_format = 'FFMPEG'`, `scene.render.ffmpeg.format = 'MPEG4'`), and `blender -b file.blend -a` renders a full animation to an .mp4 container in one command with no external stitching step ([Blender manual: rendering from command line](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html), [Blender CLI arguments reference](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)). However, turning raw MPM particle positions into a renderable Blender scene requires substantially more `bpy` boilerplate than PyVista: creating a mesh object (or using Geometry Nodes / a particle system), assigning materials for the fluid vs. the vehicle mesh, setting up camera and studio lighting, and driving per-frame vertex updates via keyframed shape keys or a custom `frame_change` handler. For a fast, science-figure-style particle scatter (not a hero marketing render), this is more engineering effort than PyVista for equivalent visual information content, though Blender wins decisively if genuinely photorealistic water/refraction rendering is desired for the poster hero shot.

**matplotlib — easiest code, worst performance/quality at scale.** The dual-output pattern is textbook: `ax.scatter(x, y, z, ...)` plus `fig.savefig("poster.png", dpi=300)` for the static frame, and `matplotlib.animation.FuncAnimation` combined with `FFMpegWriter` for the MP4 — matplotlib does not implement its own video encoder and shells out to the system `ffmpeg` binary via `animation.ffmpeg_path` ([Matplotlib animation documentation](https://matplotlib.org/stable/users/explain/animations/animations.html)). This is the lowest-code option (~20-30 lines for both outputs) but `mplot3d` uses a simple painter's-algorithm depth-sort rather than a real z-buffer, so with MPM particle counts in the 10^4-10^6 range, both interactivity and per-frame render time degrade badly, and visual artifacts (incorrect occlusion between fluid particles and the vehicle mesh) are a known limitation of `mplot3d`'s 3D scatter rendering. This makes it acceptable for quick-look diagnostic plots but a poor choice for the final poster-quality figure or a smooth publication MP4 at the particle counts Genesis MPM will produce.

---

## 3. Setup complexity & dependency footprint inside an existing Apptainer container (PyTorch + Taichi already installed)

| Tool | Install command | Added size (approx.) | System libraries needed |
|---|---|---|---|
| PyVista | `pip install pyvista vtk` (x86) or `conda install -c conda-forge pyvista vtk` (aarch64/Vista) | ~40-90 MB (VTK wheel/conda package is the bulk) | `libgl1`, `libegl1`, `libopengl0`, `libxrender1` for EGL off-screen; OSMesa packages (`libosmesa6`) only if falling back to software rendering ([PyVista installation docs](https://docs.pyvista.org/getting-started/installation.html)) |
| ParaView | No pip wheel; `conda install -c conda-forge paraview` or unpack an official x86_64 tarball | ~300 MB-1 GB+ depending on Qt-GUI vs. headless "osmesa"/"egl" variant; conda-forge aarch64 package itself is ~33 MB but pulls a large transitive dependency tree | For source/superbuild: `VTK_OPENGL_HAS_EGL`/`VTK_OPENGL_HAS_OSMESA` toggles at build time ([ParaView Offscreen rendering docs](https://www.paraview.org/paraview-docs/latest/cxx/Offscreen.html)); prebuilt headless modules commonly ship as `paraview/X.Y.Z.egl.cuda` or `paraview/X.Y.Z.osmesa.x86_64` module variants on HPC systems ([NCSA Delta ParaView batch docs](https://github.com/ncsa/Delta_doc/blob/main/docs/source/user_guide/visualization.rst)) |
| Blender (bpy) | `pip install bpy` (x86 only; no aarch64 wheel) | **374 MB** for the x86-64 wheel alone ([bpy 5.0.1 file size on PyPI](https://pypi.org/project/bpy/)); on aarch64, a full from-source Blender build additionally requires OpenColorIO, OpenImageIO, OpenEXR, Embree-class libraries ([Blender aarch64 source build thread](https://devtalk.blender.org/t/linux-aarch64-source-build/35311)) | None for the prebuilt x86 wheel beyond standard shared libs; from-source aarch64 build needs a large C++ toolchain plus CUDA/OptiX SDK if GPU rendering is desired ([blender-arm64 build guide](https://github.com/CoconutMacaroon/blender-arm64/)) |
| matplotlib | `pip install matplotlib` (likely already present) | A few MB; negligible marginal cost | None — pure software rasterization via `Agg`; only `ffmpeg` binary needed for MP4 export, no GPU/graphics libraries at all |

**Practical implication for Josie's containers:** PyVista is the only one of the three "real" 3D tools that installs with a single `pip`/`conda` command and stays under ~100 MB on top of the existing PyTorch+Taichi image. ParaView effectively requires either vendoring a separate large binary distribution or a conda environment layer, and mixing PyVista's VTK with ParaView's bundled VTK in the same venv is explicitly warned against by ParaView's own maintainers ("PyVista will install VTK inside the venv which will conflict with the one available on ParaView. So make sure you remove vtk from the venv.") ([ParaView Discourse packaging thread](https://discourse.paraview.org/t/adding-paraview-as-a-dependency-to-a-project/14649)) — meaning ParaView and PyVista should live in **separate** Apptainer images or separate venvs if both are ever used. Blender's `bpy` wheel is nearly 400 MB by itself for x86, and simply does not exist as an installable wheel on aarch64/Vista, forcing a from-source compile that would need to be baked into the container build recipe and rebuilt whenever Blender is updated — a nontrivial maintenance burden for a 7-week REU timeline. matplotlib is essentially free.

---

## 4. Known GPU-context conflicts with Taichi — the critical practical question

This is the crux of the risk Josie is asking about, directly analogous to the documented macOS Genesis+Taichi+PyGEL3D GLFW crash.

### The documented analogous conflict (Genesis + Taichi + PyGEL3D, macOS)
The closed GitHub issue is an almost perfect structural analogue to the question being asked here. On macOS Apple Silicon, running Genesis (which embeds Taichi) alongside PyGEL3D (a separate OpenGL/GLFW-based visualization library) **in the same process** produced duplicate Objective-C class implementations for `GLFWHelper` and `GLFWApplicationDelegate` — because both Taichi's compiled core (`taichi_python.cpython-311-darwin.so`) and PyGEL3D's `libPyGEL.dylib` independently bundle their own copies of GLFW — followed by shader/framebuffer binding failures and a hard crash (`glBindFramebuffer` `GL_INVALID_OPERATION`) ([Genesis issue #165, full report](https://github.com/Genesis-Embodied-AI/Genesis/issues/165)). Community mitigations that emerged were version-pinning PyGEL3D to an older release, or patching PyGEL3D to build without its own GLFW/OpenGL, and ultimately a Genesis-side fix replacing the internal renderer — none of which is a general solution so much as evidence that **two independently-linked GPU-context/windowing libraries loaded into one Python process is fundamentally fragile**, regardless of OS.

### Does the same class of conflict apply to Taichi + PyVista/VTK, ParaView, or Blender on Linux/HPC?
The mechanism differs slightly by platform (Linux headless rendering uses EGL/OSMesa/GLX rather than GLFW+Cocoa, and CUDA driver contexts rather than Objective-C class tables), but the underlying risk category is the same — **contention over GPU driver/context state when multiple libraries each try to own an OpenGL/EGL/Vulkan/CUDA context in one address space**:

- **Taichi's own context management is documented as sensitive to what else is running in-process.** Taichi's GGUI system uses Vulkan (or CUDA/OpenGL as fallback) for its own real-time visualization, and Taichi's global settings docs specifically warn that when using CUDA and GGUI together on multi-GPU machines, `CUDA_VISIBLE_DEVICES` and `TI_VISIBLE_DEVICE` must be kept in sync or GGUI will attempt to bind the wrong device ([Taichi GGUI docs](https://docs.taichi-lang.org/docs/ggui), [Taichi global settings docs](https://docs.taichi-lang.cn/docs/global_settings/)). Taichi's own issue tracker documents Vulkan/GLFW initialization failures under Wayland+dedicated-GPU combinations ([Taichi issue #8536](https://github.com/taichi-dev/taichi/issues/8536)) and a segfault specific to the CUDA backend when GGUI is active that does not reproduce on the Vulkan backend ([Taichi issue #4493](https://github.com/taichi-dev/taichi/issues/4493)) — i.e., even Taichi's *own* rendering path is not fully robust against its own compute backend in some configurations, which is a strong prior that adding a second, independent GPU-context library (VTK/EGL, ParaView/EGL, or Blender/CUDA+Vulkan) into the same process raises risk further, not less.
- **CUDA context sharing between PyTorch and Taichi is explicitly called out as unresolved by Taichi's own core developer.** On the official PyTorch discussion forum, a Taichi core team member (username `K-Ye`) states: "Our program runs both Pytorch and another library (taichi) in the same process. Since both packages use CUDA, this has caused a problem when running the program on a GPU device that's set to `EXCLUSIVE_PROCESS` mode... is there any recommendation for how to workaround the problem?" The suggested workaround (`cuCtxGetCurrent` to retrieve and reuse PyTorch's existing CUDA context) reportedly worked in a simple test case, but the same developer immediately flags that **PyTorch provides no guarantee that its CUDA context persists for the lifetime of the process**, concluding "it's better not to assume the context is sharable" ([PyTorch Discuss: "Share the CUDA context created by pytorch"](https://discuss.pytorch.org/t/share-the-cuda-context-created-by-pytorch/113359)). Since Josie's container already runs PyTorch *and* Taichi together (for Genesis MPM), this tells us the PyTorch+Taichi combination is already operating in a documented gray zone for CUDA context management — adding a *third* GPU-context consumer (VTK/EGL's own OpenGL-CUDA interop path, or Blender's CUDA/OptiX renderer) in the same process compounds an already-acknowledged fragility rather than introducing a fresh, independent risk.
- **Genesis's own maintainers treat headless-rendering breakage as an environment-level, not Genesis-level, problem** — when a user reported `ImportError: Rendering not working on this machine` while trying to run Genesis headlessly on a Slurm cluster with `show_viewer=False`, the response from a Genesis collaborator was: "Basically, headless rendering is probably broken on your machine. Try rendering anything with another tool than Genesis and it should fail similarly. Nothing actionable at Genesis-level" ([Genesis discussion #908](https://github.com/Genesis-Embodied-AI/Genesis/discussions/908)). This is a useful signal: Genesis does not claim to guarantee safe co-existence with other GPU-context libraries in-process, and pushes the responsibility for a clean headless rendering environment onto the user's process/container setup — which is exactly why process separation is the standard mitigation rather than something specific to any one of the four candidate tools.
- **VTK/PyVista, ParaView, and Blender all independently manage their own OpenGL/EGL or CUDA/Vulkan context** the moment they are imported and initialized (VTK creates a `vtkOSOpenGLRenderWindow`/`vtkEGLRenderWindow` per the `VTK_DEFAULT_OPENGL_WINDOW` selection logic ([VTK runtime settings](https://docs.vtk.org/en/latest/advanced/runtime_settings.html)); ParaView's EGL device selection interacts directly with which GPU index is visible via `CUDA_VISIBLE_DEVICES`-style environment binding on multi-GPU nodes, and has open bugs about being unable to select non-zero-index EGL devices on some HPC schedulers ([ParaView Discourse: pvbatch EGL on HPC](https://discourse.paraview.org/t/pvbatch-with-egl-device-on-hpc/9262)); Blender/Cycles directly claims a CUDA or OptiX device via its own device-enumeration API (`bpy.context.preferences.addons['cycles'].preferences.get_devices()`), which on headless nodes sometimes silently fails to find GPUs unless this call is explicitly invoked in a startup script ([Blender devtalk: headless rendering not picking up GPUs](https://devtalk.blender.org/t/headless-rendering-no-longer-automatically-picking-up-gpus/12176))). None of these three make any documented guarantee of safe coexistence with an already-initialized Taichi CUDA/Vulkan runtime in the same process.

### Standard, low-risk mitigation
Given the above, the practically verified, low-risk pattern — and the one implicitly recommended by how the Genesis ecosystem itself handles this (dump-then-visualize, e.g. Taichi's own `ti.tools.PLYWriter`/NPZ-style export-then-import-into-Blender workflow documented in Taichi's own issue tracker for exactly this reason: "you could import the mesh sequence using Blender with Stop-motion-OBJ plugin" rather than rendering in-process ([Taichi issue #5105 discussion of exporting sim data for downstream rendering](https://github.com/taichi-dev/taichi/issues/5105)) — is:

1. **Process 1 (simulation):** Launch Genesis MPM (Taichi backend, `ti.init(arch=ti.cuda, ...)`) inside the Apptainer container on the GPU node. Use Genesis's native particle accessor (e.g. `liquid.get_particles_pos()` / `MPMEntity.get_state()`, which returns `(n_particles, 3)` NumPy-convertible position arrays, per the Genesis MPM API reference) ([Genesis MPMEntity API reference](https://genesis-world.readthedocs.io/en/v0.3.3/api_reference/entity/mpm_entity.html), [Genesis "Beyond Rigid Bodies" tutorial on `get_particles_pos()`](https://genesis-world.readthedocs.io/en/latest/user_guide/getting_started/beyond_rigid_bodies.html)) to pull fluid particle positions each frame, plus the rigid vehicle mesh state, and write each frame to its own `frame_XXXXX.npz` on local/scratch disk. **Do not import PyVista, VTK, ParaView, or bpy anywhere in this process.**
2. **Process boundary:** Let the simulation process exit completely (this tears down the Taichi CUDA/Vulkan runtime and its GPU context cleanly).
3. **Process 2 (rendering):** In a fresh `python` invocation (a separate Slurm step, a separate `apptainer exec` call, or simply a new script run after the first completes), `import pyvista as pv` (or the chosen tool), load the NPZ frames from disk with `numpy.load`, build the scene, and render the static PNG and/or MP4. This process never imports Taichi or Genesis at all, so there is no possibility of a GLFW/EGL/Vulkan/CUDA context collision by construction.

This is a coarse-grained but airtight mitigation, and it is the same pattern implicitly validated by every piece of evidence above: Taichi's own maintainers reach for "reuse an existing CUDA context via the driver API and hope it's not destroyed" rather than "just share the context safely," which is a strong signal that in-process sharing is a fragile, expert-only, per-case-tested path, not something to build a REU-timeline pipeline on. Separate processes also have a secondary benefit for HPC job scheduling: the simulation step can request a full A100/GH200 for compute, while the rendering step (especially with PyVista/EGL) is often light enough to run on a shared or CPU-heavy allocation, improving overall queue turnaround on Lonestar6/Vista.

---

## Recommended workflow for Josie

**Pipeline:**

```
[GH200 or A100 node, Apptainer container, Process 1]
Genesis MPM (Taichi, arch=ti.cuda)
  → per frame: liquid.get_particles_pos(), rigid mesh vertices
  → np.savez(f"frame_{i:05d}.npz", fluid_pos=..., fluid_vel=..., veh_verts=..., veh_faces=...)
  → process exits cleanly (Taichi/CUDA context torn down)

[Same node or different node, Apptainer container, Process 2 — FRESH interpreter]
import pyvista as pv, numpy as np, glob
frames = sorted(glob.glob("frame_*.npz"))
# Build PolyData scene once (mesh for vehicle, point cloud/glyphs for fluid particles)
# (a) Poster: render one representative frame at high resolution
plotter = pv.Plotter(off_screen=True, window_size=(3840, 2160))
... add fluid + vehicle actors, set camera, colormap by velocity/depth ...
plotter.screenshot("poster_hero_frame.png")

# (b) Animation: loop over all frames, update point positions in place
plotter2 = pv.Plotter(off_screen=True, window_size=(1920, 1080))
plotter2.open_movie("flood_traversal.mp4", framerate=30)
for f in frames:
    d = np.load(f)
    fluid_actor.points = d["fluid_pos"]   # update in place
    veh_actor.points = d["veh_verts"]
    plotter2.write_frame()
plotter2.close()
```

If native MP4 writing via `imageio-ffmpeg`/`open_movie` proves unreliable in the container, fall back to writing PNG frames with `plotter.screenshot(f"png/frame_{i:05d}.png")` in the loop and stitching with a plain `ffmpeg -framerate 30 -i png/frame_%05d.png -pix_fmt yuv420p flood_traversal.mp4` call — this is the universal, dependency-light fallback that works identically regardless of which rendering tool produced the PNGs (PyVista, ParaView, Blender, or matplotlib all support "dump PNG sequence, then `ffmpeg` stitches" as the lowest-common-denominator path, and it is explicitly how matplotlib's own `FFMpegWriter` and Blender's older render pipelines have historically worked too).

**Where each step runs:**

| Step | MacBook (Apple Silicon) | DesignSafe JupyterHub | Lonestar6 (x86 A100) | Vista (aarch64 GH200) |
|---|---|---|---|---|
| Genesis MPM simulation (Taichi CUDA) | Not runnable at scale — no NVIDIA GPU; also subject to the known macOS Genesis+Taichi GLFW issue if any visualization import is attempted | Not typical (JupyterHub not GPU-simulation-oriented for this workload) | ✅ Runs (A100, x86 wheels for Taichi/PyTorch native) | ✅ Runs (GH200, this is the intended production target per the project's compute plan) |
| NPZ frame export | N/A (no sim here) | N/A | ✅ Writes to `$SCRATCH`/`$WORK` | ✅ Writes to `$SCRATCH`/`$WORK` |
| PyVista rendering (Process 2) | ✅ Fully runnable — `pip install pyvista` works natively on macOS ARM (no EGL needed; PyVista falls back to its native macOS OpenGL path off-screen), useful for **prototyping the rendering script on small test NPZ files before submitting to TACC** | ✅ Runnable — good place for interactive iteration on colormap/camera before batch runs | ✅ Runs; use `conda install -c conda-forge pyvista vtk` or `pip install pyvista vtk` (x86 wheels are on PyPI) | ✅ Runs; **must use `conda install -c conda-forge pyvista vtk`** (no official PyPI aarch64 VTK wheel) inside the Apptainer image |
| ParaView rendering | ✅ Runnable for prototyping (macOS binary from paraview.org) | Possible if a ParaView module/binary is available | ✅ Runs with x86_64 binary or conda-forge build | ⚠️ Only via conda-forge `linux-aarch64` ParaView build or a from-source EGL/OSMesa compile; not a paraview.org binary download |
| Blender/bpy rendering | ✅ `pip install bpy` works on macOS ARM64 (official wheel exists) — good for local prototyping of a nicer hero-image render style | Uncertain/likely not pre-installed | ✅ `pip install bpy` (x86-64 wheel exists) | ❌ No official wheel or binary; would require a self-maintained from-source Blender build with CUDA/OptiX for GH200 — not recommended given the 7-week project timeline |
| matplotlib quick-look plots | ✅ Trivial, always works | ✅ Trivial, always works | ✅ Trivial | ✅ Trivial |
| ffmpeg stitching | ✅ (`brew install ffmpeg`) | Likely available or installable | ✅ (module or conda `ffmpeg`) | ✅ (module or conda `ffmpeg`) |

**Practical recommendation sequencing:** Prototype the PyVista scene-construction and camera/colormap code on the MacBook using a small synthetic NPZ (or a short local Genesis/Taichi CPU-only run for geometry only, never mixing rendering imports with a Taichi import in the same script) to iterate quickly on visual design before submitting to Vista. Then run the real Genesis MPM production simulations on Vista (GH200) as intended, writing NPZ frames to `$SCRATCH`, and run the rendering step as a second, separate batch job (or a second step within the same Slurm script, invoked as a distinct `python` process after the simulation step's process has exited) using the conda-forge `pyvista`+`vtk` aarch64 build inside the same or a lightweight companion Apptainer image.

---

## Key caveats and unverifiable items

- No official Kitware PyPI aarch64 wheel currently exists for `vtk`/`vtk-osmesa`; this was verified directly against PyPI/wheels.vtk.org discussion threads and is time-sensitive — check `pip index versions vtk` and wheels.vtk.org again before the poster deadline in case this changes ([VTK Discourse: aarch64 wheel status](https://discourse.vtk.org/t/dockerizing-trame-application-with-vtk-osmesa-wheel/14755)).
- ParaView's per-GPU EGL device index selection on multi-GPU HPC nodes has an open, not-fully-resolved community-reported issue (device index 0 works, arbitrary Slurm-assigned GPU indices sometimes do not) ([ParaView Discourse EGL/HPC thread](https://discourse.paraview.org/t/pvbatch-with-egl-device-on-hpc/9262)); this could matter on Vista if GH200 nodes are shared/multi-GPU-visible in a given allocation — this has not been separately verified against TACC's specific Vista GPU-visibility configuration and should be tested empirically if ParaView is used.
- No TACC-specific documentation was found confirming PyVista, ParaView, or Blender are provided as pre-built modules on Vista or Lonestar6; general Vista/Lonestar6 user-guide pages were reviewed ([TACC Vista user guide](https://docs.tacc.utexas.edu/hpc/vista/), [TACC Lonestar6 documentation](https://docs.tacc.utexas.edu/hpc/lonestar6/)) but did not surface a module list for these specific visualization packages — assume they must be installed inside the user-managed Apptainer image rather than relying on a system `module load`.
- The Blender-on-GH200-class-hardware evidence (NVIDIA GB10/DGX Spark) is a strong positive signal but is not a direct TACC/Vista report — GB10 and GH200 are both Grace-based NVIDIA superchips but are not identical hardware, so this should be treated as "very likely feasible" rather than "confirmed on Vista" ([NVIDIA Developer Forum: Blender on GB10](https://forums.developer.nvidia.com/t/blender-5-0-and-5-1-0-running-on-gb10-with-cuda-optix-vulkan/351254)).
# Kumar / GeoElements MPM Visualization Conventions for Josie Cerrell’s “Can It Ford?” Project

## Executive answer

Krishna Kumar’s GeoElements/CB-Geo visual standard for MPM-style particle simulations is particle-first: show material points as points or spheres, compare the learned or reduced model against MPM side-by-side, color particles by displacement or material class, keep axes/scale visible in technical figures, and pair the visual with runout, height/depth, energy, and error plots rather than relying on a single pretty render ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218); [Kumar and Vantassel 2023, DOI:10.21105/joss.05025](https://doi.org/10.21105/joss.05025); [Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/)). For Josie’s Genesis MPM + rigid vehicle flood traversability poster and paper, the closest match is: fixed-camera side and top/aerial particle snapshots; water particles in blue or a fixed viridis scalar field; vehicle displacement/drift highlighted in orange; axes or a scale bar; and companion plots for lateral drift, depth, velocity, depth-velocity product, drag/force if available, and ford/no-ford verdict.

A critical scope note: the attached combined reference file labels “Path Planning in Physically Viable World Models” as an anonymous CoRL 2026 submission and explicitly says it is “NOT CONFIRMED as Kumar-authored,” so this report uses it only as lab-affiliated PVWM context, not as evidence of Krishna Kumar’s own published visualization convention. The confirmed Kumar-authored sources are the GNS granular-flow paper, the GNS repositories, the CB-Geo MPM documentation, and the Galaxy/MPM in-situ visualization papers and repositories ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218); [Kumar and Vantassel 2023, DOI:10.21105/joss.05025](https://doi.org/10.21105/joss.05025); [Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/); [Kumar et al. 2022, arXiv:2206.12683](https://arxiv.org/abs/2206.12683)).

## 1. Rendering and visualization tools used by Kumar / GeoElements / CB-Geo

| Tool or workflow | Evidence and typical use | Visual output style | Reproducibility flag for Josie |
|---|---|---|---|
| **Matplotlib + ImageMagick GIFs** | The `geoelements/gns` renderer imports `matplotlib.animation`, writes GIFs, and exposes `python3 -m gns.render_rollout --output_mode="gif"` for particulate rollouts ([GNS repository](https://github.com/geoelements/gns); [GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)). | Side-by-side “Reality” vs “GNS” scatter plots, grid on, equal aspect, titles, total MSE, 30 fps GIFs; 3D views use 20° elevation and slow azimuth rotation ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)). | **MacBook:** yes for small saved rollouts; **DesignSafe JupyterHub:** yes; **TACC:** needed only for generating large rollouts/training. |
| **VTK/VTU/VTP/PVTP + ParaView** | CB-Geo MPM writes particle VTK attributes including stresses, strains, and velocities, and its docs instruct users to open particle data in ParaView using `Point Gaussian` representation ([CB-Geo MPM VTK docs](https://github.com/cb-geo/mpm-doc/blob/main/user/postprocess/vtk.md); [LearnMPM DesignSafe MPM guide](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)). The GNS renderer also writes `.vtu` files for particulate rollouts for ParaView visualization ([GNS repository](https://github.com/geoelements/gns)). | Technical particle visualization with point-Gaussian particles, scalar coloring, time stepping, and side/top/aerial camera selection. | **MacBook:** yes for small/medium `.vtu/.vtp`; **DesignSafe JupyterHub/DesignSafe ParaView:** yes; **TACC:** needed for large CB-Geo/Genesis data generation. |
| **Python/Pandas HDF5 postprocessing** | CB-Geo MPM writes HDF5 particle outputs readable with Python/Pandas; variables include coordinates, velocities, stresses, strains, volumetric strain, and status ([CB-Geo MPM HDF5 docs](https://github.com/cb-geo/mpm-doc/blob/main/user/postprocess/hdf5.md)). | Not a renderer by itself, but supports derived plots: velocity magnitude, displacement, stress, strain, runout/depth histories. | **MacBook:** yes for small HDF5; **DesignSafe JupyterHub:** best fit for analysis; **TACC:** required only for large simulation production. |
| **TACC Galaxy ray tracing / in-situ visualization** | Kumar co-authored MPM/Galaxy work rendering the 2014 Oso landslide with 4.2 million material points as spheres, reporting only about 2% amortized runtime overhead ([Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/); [2021 Galaxy-MPM paper repo](https://github.com/kks32-docs/2021-galaxy-mpm)). | Photorealistic-ish sphere renderings with global illumination, shadows, ambient occlusion, displacement color gradients, and multiple camera views. | **MacBook:** no; **DesignSafe:** not immediately; **TACC cluster:** yes, but overkill for REU poster unless a mentor provides an existing workflow. |
| **GNS-informed in-situ view planning** | The “Minority Report” workflow uses a GNS surrogate on a smaller platform to choose critical timesteps, data regions, scalar ranges, and side/top/aerial camera views for full MPM/Galaxy visualization ([Kumar et al. 2022, arXiv:2206.12683](https://arxiv.org/abs/2206.12683); [2022 LDAV GNS4VIS repo](https://github.com/kks32-docs/2022-LDAV-GNS4VIS)). | ParaView previews of GNS `.vtp` files first; then full-resolution MPM/Galaxy images using the preselected views and displacement ranges. | **MacBook:** yes for small GNS preview logic; **DesignSafe:** yes for preview/postprocessing; **TACC:** needed for full in-situ Galaxy/MPM runs. |
| **Houdini via Partio / `.bgeo`** | The CB-Geo MPM repository documents Partio support for Houdini SFX visualization and `.bgeo` output ([CB-Geo MPM repository](https://github.com/cb-geo/mpm)). | Potentially high-end SFX rendering of particle data, but this is not the dominant convention in Kumar’s published GNS/MPM papers. | **MacBook:** possible but not immediate because Houdini/Partio setup is heavier; **DesignSafe:** unlikely; **TACC:** not necessary unless producing large assets. |
| **PyVista** | No primary Kumar/GeoElements source reviewed here identifies PyVista as a standard group visualization pathway for MPM particle results; the primary Python plotting route is Matplotlib/GIF and the primary 3D postprocessing route is VTK/ParaView ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py); [CB-Geo MPM VTK docs](https://github.com/cb-geo/mpm-doc/blob/main/user/postprocess/vtk.md)). | Useful for Josie if she wants Python-native VTK rendering, but it should be treated as a convenience layer rather than Kumar’s documented standard. | **MacBook/DesignSafe:** yes for small data; **TACC:** no unless data is huge. |
| **Taichi GGUI** | The GNS inverse examples mention a Taichi coordinate convention, but the actual visualization functions use Matplotlib animations and scatter plots rather than Taichi GGUI ([GNS inverse barrier utility](https://github.com/geoelements/gns-inverse-examples/blob/main/inverse_barrier/utils.py)). | Not a documented Kumar/CB-Geo visualization standard; relevant only if Genesis already outputs Taichi-friendly previews. | **MacBook:** possible for Genesis previews; **DesignSafe:** not primary; **TACC:** required only for heavy Genesis simulations. |

## 2. Common visual conventions in figures and videos

### Particle representation: points and spheres, not reconstructed surfaces

Kumar’s MPM/GNS figures generally preserve the particle nature of the simulation: the GNS granular-flow paper compares GNS and MPM snapshots as particle fields, and its figure captions explicitly state that color represents displacement magnitude and units are meters ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)). The GNS code renders particles as Matplotlib scatter points for 2D and 3D GIFs, while the Galaxy in-situ paper renders MPM material points as spheres with fixed radius matching the particle grid resolution ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py); [Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/)). For Josie, this means a poster render should not hide the MPM particles behind a smooth water surface; a transparent surface can be added for readability, but the scientific visual should still show particles or splats as the data carrier.

### Scalar color: displacement magnitude is the most canonical field

The strongest recurring scalar convention is displacement magnitude: granular column collapse figures color material points by displacement magnitude; GNS/MPM error analysis tracks displacement error; Galaxy Oso landslide images use a color gradient showing particle displacement from original position; and the GNS-informed in-situ paper preselects a displacement range of 0 to 0.38 m for particle coloring ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218); [Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/); [Kumar et al. 2022, arXiv:2206.12683](https://arxiv.org/abs/2206.12683)). The inverse-barrier example uses Matplotlib `viridis` for displacement magnitude in 3D particle animations, with stationary particles in black and a colorbar ([GNS inverse barrier utility](https://github.com/geoelements/gns-inverse-examples/blob/main/inverse_barrier/utils.py)). The GNS renderer also supports categorical material colors: droplet red, boundary black, rigid solids green, goop magenta, sand gold, and water blue ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)).

For “Can It Ford?”, use **viridis for vehicle displacement/drift or water speed magnitude** when presenting a scalar field, and use **categorical blue water + dark/gray terrain + orange vehicle marker** when the goal is communicating the scenario quickly. Keep colorbar limits fixed across frames and scenarios so the L2 flood/no-ford comparison is visually honest.

### Camera angles: side/profile, top-down, and aerial/oblique are all used, but with purpose

For 2D column collapse, Kumar’s paper uses side/profile snapshots over normalized time so runout and height can be read directly from axes in meters ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)). For 3D baffle and in-situ work, the convention expands to multiple views: the GNS-informed visualization paper explicitly chooses side, top, and aerial views from ParaView previews before running full MPM/Galaxy visualization ([Kumar et al. 2022, arXiv:2206.12683](https://arxiv.org/abs/2206.12683)). The default GNS 3D GIF camera uses 20° elevation with a slowly changing azimuth, and the inverse-barrier renderer uses the same 20° elevation idea for rotating particle animations ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py); [GNS inverse barrier utility](https://github.com/geoelements/gns-inverse-examples/blob/main/inverse_barrier/utils.py)).

For Josie, the best match is a **two-view convention**: a top-down plan view for lateral drift and road crossing feasibility, plus a 3/4 oblique view for poster intuition. A side/profile inset should be added when explaining water depth, vehicle clearance, or Froude-like flow context.

### Ground plane, grid, scale, and axes

Kumar’s technical GNS/MPM paper figures are not cinematic-only renders: they include units in meters, normalized time labels, colorbars, and side-by-side GNS/MPM panels ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)). The Matplotlib GNS renderer turns the grid on and fixes equal aspect/bounds for both “Reality” and “GNS” panels, which prevents misleading camera or scaling differences ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)). Galaxy renders reduce visual clutter and use lighting instead of grids, but they still retain physical realism by representing particles as spheres and coloring by displacement ([Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/)).

For Josie’s poster, the readable compromise is: use a clean ground plane or road surface with a scale bar and flow arrow; keep axes/grid in paper figures; use identical camera, bounds, and colorbar for all L2 comparisons.

## 3. Quantities Kumar typically reports alongside visualizations

Kumar’s GNS granular-flow paper pairs particle snapshots with quantitative curves: normalized runout, normalized height, normalized energy components, mean squared displacement error, squared displacement error per material point, upstream depth behind barriers, and final runout error tables ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)). The same paper defines comparisons against MPM, including runout errors generally within about 5% for several column-collapse cases, and reports MPM/GNS compute comparisons on TACC systems ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)). The GNS repository’s renderer writes per-particle displacement to VTK, and its GIF titles include total MSE for side-by-side rollout comparison ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)).

CB-Geo MPM documentation supports reporting a broader set of mechanics quantities because VTK output can include stresses, strains, and velocities, while HDF5 stores coordinates, velocity components, stress components, strain components, volumetric strain, and status ([CB-Geo MPM VTK docs](https://github.com/cb-geo/mpm-doc/blob/main/user/postprocess/vtk.md); [CB-Geo MPM HDF5 docs](https://github.com/cb-geo/mpm-doc/blob/main/user/postprocess/hdf5.md)). For flood traversability, the Kumar-consistent move is not to show every available tensor field; instead, report a small set that explains the decision boundary and mechanism.

Recommended “Can It Ford?” companion quantities:

| Poster/paper quantity | Why it matches Kumar’s reporting style | Suggested plot or annotation | Compute flag |
|---|---|---|---|
| **Vehicle lateral displacement/drift over time** | Analogous to runout as the outcome metric for moving material/objects. | Line plot with no-ford threshold at 0.05 m; final drift annotated on render. | MacBook/DesignSafe after simulation; Vista GH200 for Genesis run. |
| **Water depth, speed, and depth-velocity product** | Provides L0/L1 baseline next to L2, mirroring Kumar’s side-by-side model comparisons. | Small table: depth, velocity, D×V, L1 verdict, L2 verdict. | MacBook/DesignSafe. |
| **Particle displacement or velocity magnitude** | Displacement magnitude is Kumar’s most common particle scalar; velocity is directly supported in CB-Geo outputs. | Viridis colorbar, fixed limits across cases. | MacBook/DesignSafe for render; Vista for large simulation output. |
| **Hydrodynamic/rigid-body force or impulse, if available** | Explains why L2 differs from D×V by showing persistent lateral forcing. | Force vs time or cumulative impulse vs time below the video frames. | DesignSafe after extraction; Vista if force logging requires rerun. |
| **Final path/trajectory of the vehicle center of mass** | Analogous to material point trajectories and final deposit/runout. | Top-down polyline over particles; start/end markers. | MacBook/DesignSafe. |
| **Uncertainty or error band, if running multiple seeds/resolutions** | Kumar’s GNS papers report MSE/error versus MPM; a small band shows robustness. | Shaded band for drift or final verdict across seeds/resolutions. | DesignSafe for aggregation; Vista/LS6 if multiple large runs. |

## 4. Video and GIF outputs linked from papers or repositories

The `geoelements/gns` README embeds a sand rollout GIF and a meshnet fluid-flow GIF, and the command-line renderer supports GIF output for particulate rollouts plus `.vtu` export for ParaView ([GNS repository](https://github.com/geoelements/gns)). These GIFs are simple, scientific animations: fixed or slowly rotating camera, point particles, side-by-side prediction comparison when applicable, and minimal styling rather than cinematic effects ([GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)).

The GNS inverse examples embed trajectory GIFs for final guess and reconstructed trajectories, include optimization-history images, compare predicted and target final deposits, and link a baffle-design video on YouTube ([GNS inverse examples repository](https://github.com/geoelements/gns-inverse-examples); [AD-GNS baffle design video](https://youtu.be/kavtEKsB3hA)). The inverse-barrier utility renders 3D GIFs with viridis displacement coloring, black stationary particles, a colorbar, 20° elevation, a rotating azimuth, and a grid ([GNS inverse barrier utility](https://github.com/geoelements/gns-inverse-examples/blob/main/inverse_barrier/utils.py)).

The GNS-informed in-situ visualization paper links an overview video and uses GNS/ParaView previews to choose side, top, and aerial views for MPM/Galaxy output ([Kumar et al. 2022, arXiv:2206.12683](https://arxiv.org/abs/2206.12683); [GNS-informed visualization overview video](https://youtu.be/j5qFD8lrt74)). The Galaxy/MPM paper emphasizes image sequences and in-situ renderings rather than README GIFs, but its style is clear: material points as shaded spheres, displacement color gradients, and physically legible views that communicate landslide runout to stakeholders ([Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/); [2021 Galaxy-MPM paper repo](https://github.com/kks32-docs/2021-galaxy-mpm)).

## Concrete recommendations for Josie’s poster and final paper

### Poster visual standard

Use one main **L2 Genesis MPM flood/vehicle panel** with particles visible, a fixed 3/4 oblique camera, a flow-direction arrow, and an orange vehicle outline or center-of-mass marker. Color water by **velocity magnitude in viridis** if the central point is lateral drag, or use **blue water particles with orange vehicle trajectory** if the central point is the ford/no-ford decision.

Next to the main panel, include a **top-down drift panel** because the scientific novelty is lateral drift that L1 cannot represent. The top-down panel should show the road, water particles or a translucent flood footprint, the vehicle trajectory polyline, start/end markers, and a dashed 0.05 m lateral drift threshold.

Use a compact **L0/L1/L2 verdict table** under the images: depth, velocity, D×V, L1 verdict, final lateral drift, L2 verdict. This matches Kumar’s habit of pairing visual snapshots with quantitative runout/depth/error metrics rather than asking the visualization to carry the whole argument ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)).

### Paper figure standard

For the final paper, make the main results figure a time sequence with 4 or 5 frames: initial, early impact, mid crossing, maximum drift, final state. Use the same camera, bounds, and colorbar across all frames, label physical time, and keep axes in meters or include a scale bar. This follows the GNS granular-flow convention of showing normalized-time snapshots and final deposit/runout in aligned panels ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)).

Add companion plots directly below the snapshots: lateral displacement vs time, lateral force/impulse vs time if logged, and D×V/L1 threshold as a baseline marker. If multiple Genesis resolutions or seeds are available, add a shaded band around lateral drift to echo Kumar’s GNS-vs-MPM error reporting style ([Choi and Kumar 2023, arXiv:2305.05218](https://arxiv.org/abs/2305.05218)).

### Practical rendering workflow

For immediate REU production, export Genesis particle states to NumPy/HDF5/VTK-like data, then render small poster and paper assets with **Matplotlib or PyVista on MacBook/DesignSafe** and inspect any `.vtu/.vtp` outputs in **ParaView using Point Gaussian**. This is more consistent with Kumar’s documented GNS/CB-Geo workflow than a purely cinematic surface renderer ([GNS repository](https://github.com/geoelements/gns); [CB-Geo MPM VTK docs](https://github.com/cb-geo/mpm-doc/blob/main/user/postprocess/vtk.md); [LearnMPM DesignSafe MPM guide](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)).

Reserve **Vista GH200 or Lonestar6 A100** for simulation generation, neural reconstruction, or any expensive coupled Genesis/gsplat runs; do not spend scarce cluster time trying to reproduce Galaxy-style in-situ rendering unless Krishna’s group specifically wants that asset. Galaxy-style rendering is Kumar-authored and visually strong, but it is a TACC/HPC workflow designed for millions of particles and regional-scale hazards, while Josie’s near-term poster needs clear, reproducible decision evidence ([Abram et al. 2022, DOI:10.1109/MCSE.2022.3155074](https://ieeexplore.ieee.org/document/9722973/)).

### Final “match Kumar” checklist

- Show particles/splats, not only a smooth flood surface.
- Use displacement or velocity magnitude with a fixed colorbar; viridis is safe for scalar fields.
- Use blue for water, black/gray for boundaries/terrain, and orange for the vehicle/trajectory annotation.
- Use side/profile when explaining depth, top-down when explaining lateral drift, and 3/4 oblique when communicating the physical scene.
- Include scale: axes in meters for paper, scale bar for poster.
- Pair every render with a quantitative plot or table: drift, depth, velocity, D×V, force/impulse, and verdict.
- Export a short fixed-camera 30 fps GIF/MP4 with physical time labels and identical color scaling across cases, matching the simple GNS README/video style ([GNS repository](https://github.com/geoelements/gns); [GNS `render_rollout.py`](https://github.com/geoelements/gns/blob/main/gns/render_rollout.py)).
