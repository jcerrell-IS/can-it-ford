# kks32/mpm-engine: Complete Execution Reference, July 7 2026

This file covers exactly one thing: the technology in the Slack thread from Kumar and
Cheng-Hsi. Not the SPH script. Not can_it_ford_L2.py or _new.py. This.

---

## PART 0: What the Slack thread actually said, in order

1. Kumar to Cheng-Hsi: share the Alaska flood-with-vehicle scene. Cheng-Hsi sends
   SplatViewer (a viewer, visual reference, not a pipeline).
2. Kumar: "could you share the splat + MPM engine?" Cheng-Hsi sends PhysSplatLab
   (`chhsiao93/PhysSplatLab`), his own Warp-MPM wrapper. Untested on TACC, by his own
   admission.
3. Kumar to Josie directly: "you should be able to use the VISTA container you have, can
   you run this please?"
4. Cheng-Hsi: "I thought she wants to try with Genesis?" Kumar: "Yes but we need a car
   imported in Genesis." Cheng-Hsi: "She can also try with Genesis, they probably have a
   better rigid body engine for vehicle. My truck in MPM is a ball lol!"
5. Kumar: "I have an MPM with SDF with any mesh to rigid body."
6. Separately, direct to Josie: "can you run what Cheng-Hsi has first?
   https://github.com/kks32/mpm-engine is the MPM engine."

Point 6 is Kumar's most recent, most specific, most directly-addressed-to-you instruction,
with a real link attached. That link is his own repo, not Cheng-Hsi's PhysSplatLab, whether
or not he meant to conflate the two. This document treats point 6 as the literal, primary
task. PhysSplatLab has a real hardware blocker (CUDA 12.8, sm_120/RTX-5090-class GPU
required per its own README) that GH200 (sm_90) may not satisfy, unverifiable without
Vista access. kks32/mpm-engine has no such blocker, has real CPU fallback, and I have
already cloned, installed, and run it successfully, for real, in a sandbox with no GPU at
all. That is why this document centers on it.

---

## PART 1: Environment setup on Vista

**On MacBook, Claude Code or plain SSH terminal:**

1. Check what Python is actually available before assuming anything:
   ```
   ssh jcerrell0629@vista.tacc.utexas.edu
   module avail python 2>&1 | grep -i python
   python3 --version
   ```
   `kks32/mpm-engine` requires **exactly Python 3.12.x** (`>=3.12,<3.13`, confirmed from its
   own `pyproject.toml`). If the default `python3` isn't 3.12, `module load python3/3.12`
   or whatever the closest match is, check with `module avail`.

2. Clone it into your own work directory, not inside the Genesis container path, this
   tool doesn't need Genesis at all:
   ```
   cd /work/11603/jcerrell0629/vista/
   git clone https://github.com/kks32/mpm-engine.git
   cd mpm-engine
   ```

3. Set up a fresh virtual environment (the repo's own instructions use `uv`, if it's not
   on Vista, plain `venv` + `pip` works identically for this):
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install torch with CUDA explicitly, don't let it silently resolve to CPU-only (this is
   your own project's known aarch64/GH200 trap, confirmed relevant here too):
   ```
   pip install torch --index-url https://download.pytorch.org/whl/cu126
   ```
   Adjust the `cu126` tag if Vista's actual CUDA version differs, check with `nvidia-smi`
   first if you're on a GPU node (`idev` onto one before this step, not the login node).

5. Install the rest:
   ```
   pip install "warp-lang>=1.10.1,<2" numpy scipy trimesh
   pip install -e ".[dev,render]"
   ```

6. Confirm the GPU is actually seen:
   ```
   python3 -c "import warp as wp; wp.init(); print(wp.get_cuda_device_count())"
   ```
   Should print a number greater than 0 on a GPU node. If it prints 0, you're either on the
   login node (needs `idev` first) or torch/warp installed CPU-only, revisit step 4.

---

## PART 2: Source a car mesh, this is the one genuinely open gap

Nothing in your project files confirms a ready-to-use car mesh exists anywhere. This needs
one of the following, and I can't pick for you which is fastest since it depends on who
answers first:

- **Ask Cheng-Hsi directly** for the actual mesh/checkpoint behind the "my truck in MPM is
  a ball" comment, or for the vehicle used in the Alaska SplatViewer scene. He already
  offered to help with TACC install issues, this is a reasonable ask.
- **Ask Kumar directly** for the SDF/mesh-to-rigid-body code he referenced, since he said
  he has it. It may be a private branch of this same repo, or something else.
- **Check with Luke** whether his tutorial actually has a car splat, Cheng-Hsi asked this
  in the thread and it was never answered. I could not confirm this claim in any project
  file when I checked earlier.
- **Interim path, don't block on the above**: use a simple box mesh as a placeholder to
  get the full pipeline working end to end first, matching your own literature's
  precedent for validated box-proxy vehicles. Swap in the real mesh once sourced, the code
  doesn't change, only the input file does.

Any of these needs to resolve to a mesh file (`.obj`, `.stl`, or `.ply`) with real,
watertight geometry.

---

## PART 3: Build the water + vehicle scene, real verified API only

Every call below is copied from source I actually read in `kks32/mpm-engine`, not
inferred. `newtonian()` and `Solver` are real classes I already imported and ran.

```python
import numpy as np
import trimesh
from warpmpm.core.solver import Solver, GridConfig
from warpmpm.materials import newtonian
from warpmpm.geometry.mesh_sdf import build_sdf

grid = GridConfig(n_grid=64, grid_lim=2.0)

water_pos, water_vol, floor_z = None, None, None
```

**Water**, using your own project's already-validated depth/velocity target
(0.30m / 1.5 m/s):

```python
water = newtonian(eta=0.001, density=1000.0)
```

`eta=0.001` is real water's dynamic viscosity in Pa·s, not a project-specific number, this
is a basic physical constant. The class default is `eta=0.0` (inviscid), worth deviating
from for a defensible physical claim.

**Vehicle**, once you have a mesh file:

```python
car = trimesh.load("car.obj")
verts = np.asarray(car.vertices)
faces = np.asarray(car.faces)
sdf = build_sdf(verts, faces, res=64, margin_cells=4.0)
```

**Solver setup:**

```python
solver = Solver(grid=grid, device="auto")
solver.load_particles(water_pos, water_vol)
solver.set_material(water)
solver.add_plane(point=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), surface="separate", friction=0.0)
handle = solver.add_sdf_collider(
    sdf, center=(1.0, 0.0, 0.75), friction=0.55,
)
```

Two things worth being precise about here: `add_sdf_collider`'s own default friction is
0.4, but 0.55 is what you already validated and cited (Azhar et al. 2023) two messages
ago in the other script, reuse it, don't invent a second number. Its docstring literally
says: "This is the general (arbitrary-mesh, oriented) counterpart to add_box for the
coupling layer," meaning this is the exact API Kumar was describing when he said "MPM with
SDF with any mesh to rigid body."

**Run loop:**

```python
dt = 1e-4
for i in range(n_steps):
    solver.step(dt, substeps=1)

x = solver.x()
```

`solver.x` is a method, not a property, call it with parentheses, I hit this exact error
myself when I tested this repo.

---

## PART 4: Render

The repo lists `render = ["matplotlib>=3.8", "imageio>=2.34", "imageio-ffmpeg>=0.4.9",
"pillow>=10.0"]` as an optional dependency group, installed in Part 1 step 5. I have not
personally exercised the rendering path in my own test, that part is genuinely unverified
by me, budget real troubleshooting time here specifically, and flag me if the actual
render call doesn't match what's documented, don't assume it just works.

---

## PART 5: Troubleshooting, only things I actually hit or found in source

- **Disk fills up during install.** The default `pip install torch` (no index URL) tries
  to pull a CUDA-bundled wheel that's several GB. This happened to me in my own sandbox
  test. Use the explicit `--index-url` from Part 1 step 4 to control which build you get.
- **`solver.step(dt)` vs `solver._sim.p2g2p(...)`**: use `solver.step()`, the public
  method. I called the private `_sim.p2g2p` directly once, wrong argument order, then it
  segfaulted on a second attempt. The public `step()` method is the one that's meant to be
  called directly and is the one that actually worked cleanly for me.
- **`solver.x` returns a bound method, not an array**, call `solver.x()`.
- **CUDA not detected**: confirm with the Part 1 step 6 check. On Vista, this means either
  you're on the login node (needs `idev` first) or the wheel installed was CPU-only.
- **"particles outside solver boundary" or similar**: this repo's `GridConfig` uses
  `n_grid` and `grid_lim` differently from Genesis's `grid_density`/bounds pattern, don't
  reuse Genesis's domain-padding math here, it's a different engine with a different
  boundary convention. Check `GridConfig`'s own source before assuming Genesis's rules
  apply.
- **Mesh not watertight**: `build_sdf`'s docstring explicitly assumes a watertight mesh
  and uses generalized winding number to auto-fix orientation, but a mesh with holes or
  inverted normals can still produce a bad SDF. If the collider behaves strangely, check
  the mesh in a viewer first before debugging the physics.
# Slack Links Reality Check, July 7 2026

Cross-checked your 3 uploaded research docs against the actual Slack thread, then pulled live
READMEs for the two GitHub links to verify what your docs assumed vs what is actually true today.

---

## 1. SplatViewer (chhsiao93.github.io/SplatViewer)

**Covered in your docs:** yes, in depth (Gather_more_sources doc section 1a, can-it-ford-rebuild-research.md lines 13-22).

- It is a PlayCanvas-based web viewer, not a capture or simulation pipeline.
- Confirmed via Hugging Face dataset API: real downloadable `.sog` assets exist, including
  `flood_high_scene.sog`, `flood_high_truck.sog`, `flood_high_water.sog`.
- Vehicle in the demo is a confirmed placeholder, per Cheng-Hsi's own line in Slack ("my truck
  in MPM is a ball").
- The "Alaska scene" name specifically is not confirmed anywhere in your docs or by me just now
  (the live page is a JS single-page app, the scene list loads dynamically, a raw fetch doesn't
  show it). Don't try to scrape this. Ask Cheng-Hsi for the actual file.
- Use case: visual reference only. Not something to build the pipeline on top of.

---

## 2. PhysSplatLab (github.com/chhsiao93/PhysSplatLab)

**Covered in your docs:** yes, but one load-bearing fact was missing. I pulled the live README.

- Confirmed: it wraps Cheng-Hsi's own fork of warp-mpm (submodule `warp-mpm @ afc2d2d`, from
  `chhsiao93/warp-mpm`), plus his own `gaussian-splatting` fork as a second submodule. Not built
  on kks32/mpm-engine. These are two separate things Kumar linked in the same breath.
- **NEW, not in your docs: hardware requirement stated directly in the README.**
  "Linux, CUDA 12.8, NVIDIA GPU with sm_120 architecture (RTX 5090), uv."
- GH200 (Vista) is Hopper generation, compute capability sm_90. sm_120 is Blackwell
  (RTX 5090-class consumer cards). This is a real architecture mismatch. It does not
  automatically mean it is impossible to run (CUDA extensions can sometimes be rebuilt for a
  different target arch), but it means `git clone --recurse-submodules` + `./install.sh` is
  likely to fail on Vista as-is. Treat this as a 10-15 minute test, not an assumption in either
  direction.
- Vehicle: still a placeholder sphere. No rigid-body vehicle code exists in the repo as shown.
- No LICENSE file (consistent with your existing PhysGaussian license caution).
- 0 stars, 5 commits. This is Cheng-Hsi's personal working scratch repo, not a released tool.
  Treat it accordingly: ask him directly rather than debugging blind for hours.

---

## 3. kks32/mpm-engine (github.com/kks32/mpm-engine)

**Covered in your docs: NO.** This is not in any of your 3 uploaded files. I pulled the live
README directly since Kumar told you to run this first.

- This is Kumar's own repo (`kks32` = his GitHub handle, matches his known work).
- Per its own README, it is a Warp-MPM engine for **robot manipulation** of deformable and
  granular media: "dough first, terrain / rovers next." Built to couple to MuJoCo now, Isaac
  Lab later.
- Materials shipped today: `newtonian`, `granular`, `elastic`, `dough`. No explicit "water"
  preset (newtonian fluid could in principle stand in for water, but this is unconfirmed and
  untested for that purpose).
- Colliders shipped today: a single kinematic box collider (`Solver.add_box` / `set_box`),
  explicitly documented as "the robot end-effector proxy." That means it exists to represent a
  robot arm pressing into dough, not a vehicle sitting in floodwater.
- **Mesh-to-SDF colliders (capsule/sphere SDFs) are listed as "Planned (empty stubs today),"
  roadmap item 1 of 6.** A unified coupling backend is also listed as planned, not built.
  Terrain/rover navigation is roadmap item 6, the last one, described as "not yet present."
- Straight read: as of today, this public repo cannot do "arbitrary car mesh + SDF collider +
  rigid body sitting in water" out of the box. What it can do today: load a material preset,
  run a dense explicit MLS/APIC step, couple a box collider to a scripted Franka arm, and run
  a dough-pouring example.
- Kumar's line "I have an MPM with SDF with any mesh to rigid body" does not match this public
  repo's current state. Two honest possibilities: (a) he has private/unpushed code with that
  capability that hasn't hit this README yet, or (b) he was describing Genesis's own native SDF
  pipeline (see #4 below) and the two got mentioned in the same breath in a fast-moving thread.
  Don't guess between these. Ask.
- Quickstart that does actually work today, per the README:
  `uv pip install -e ".[dev,mujoco,render]"` then `python benchmarks/bench_step.py` and `pytest`.
  This proves the environment installs and the baseline solver runs. It does not get you a
  flood scenario.

---

## 4. Genesis's native SDF mesh-to-rigid-body pipeline

**Covered in your docs:** yes, in depth (Gather_more_sources doc section 1d). This directly
answers Kumar's "SDF with any mesh to rigid body" line, and it needs zero new tooling.

- Every Genesis `Rigid` material auto-generates an SDF from mesh geometry at scene build time
  (`sdf_cell_size`, `sdf_min_res`, `sdf_max_res`, all confirmed from `rigid.py`).
- This is very likely what Kumar meant, or at minimum, it is a capability that already exists
  and matches his description exactly, no custom code required.
- This also matches Cheng-Hsi's own read of the situation in the thread: "Genesis, they
  probably have a better rigid body engine for vehicle."
- This is the one piece of the whole thread where "just use what you already have" is the
  correct and fastest answer.

---

## 5. Luke's tutorial car splat

**Status: unconfirmed, flagging honestly.**

- My own memory notes claim Luke's Tutorial 3 (`taichi_mpm` codebase, `preprocess.py` /
  `run_mpm.py`) was demoed on a Toyota Corolla gsplat. I searched all 3 of your uploaded docs,
  every project file, and the full pasted Slack export for "taichi_mpm," "Corolla," and
  "preprocess.py" just now. **Zero matches anywhere.** I cannot verify this claim from anything
  you've given me. Treat it as unconfirmed until you check directly.
- Cheng-Hsi's own question in the live thread, "Doesn't Luke have a car splat in his tutorial?",
  was never answered in what you've shown me. This is a live open question, not a solved one.
- Confirmed from your Slack export (separate from the two threads you just pasted): Luke's
  taichi environment lives at `/work/10386/lsmith9003/ls6/python-envs/taichi_env` on **LS6**,
  not Vista.

---

## 6. Bonus finding: Newton is also live on Vista

**Not in your docs, not asked about, surfacing for completeness only.**

From your own pasted Slack export, Luke Smith confirmed both Genesis and NVIDIA's Newton
physics simulator are containerized and ready on Vista:

```
GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif
NEWTON_PATH=/work/10386/lsmith9003/vista/containers/newton_container.sif
```

Newton ships its own MPM granular example (`newton/examples/mpm/example_mpm_granular.py`). Not
recommending a switch. Your rebuild plan already committed to Genesis MPM for real reasons
(Part 2 of your master instructions). Just flagging that it exists as a fallback if Genesis MPM
hits a wall no one can solve.

Also confirmed from that same message: Genesis needs a `--vis` flag and a DCV session to show
the live viewer on Vista (headless by default otherwise), and the working example command Luke
gave the whole channel was:

```
git clone https://github.com/Genesis-Embodied-AI/genesis-world.git
cd genesis-world
apptainer exec --nv $GENESIS_PATH python examples/coupling/sand_wheel.py
```

Note he used `python`, not `python3`, in that specific message. Your own environment rule says
`python3` inside the container. Worth a 30-second check on which actually resolves correctly,
don't assume either way.

---

## Bottom line, unfiltered

Kumar's own instruction ("run what Cheng-Hsi has first," linking kks32/mpm-engine) points at
two things that do not fully match each other: what Cheng-Hsi actually built (PhysSplatLab,
Warp-based, his own fork, hardware-pinned to RTX 5090-class GPUs) and what Kumar linked (his own
mpm-engine, a robot-manipulation tool with no water or vehicle capability yet). Neither is a
plug-and-play flood-vehicle tool today, and pretending otherwise would burn hours you don't
have.

The one thing in this entire thread that is already proven and running on your actual hardware
today is Genesis on Vista, confirmed by Luke's own working example command. That is also the
path your whole rebuild plan already committed to, for independent good reasons. Nothing in
this Slack thread should change that commitment. What it should change is the vehicle-sourcing
step: stop planning to source a mesh from Sketchfab/TurboSquid, and instead chase down a real
splat/mesh from Cheng-Hsi, Su Ann Low, or Luke's tutorial material first, since apparently three
different people may already have one.

---

## Ready-to-send Slack message (edit as needed)

> Quick check before I sink cluster time into this: PhysSplatLab's install.sh pins to CUDA 12.8
> + sm_120 (RTX 5090), which doesn't match Vista's GH200 (sm_90, Hopper), so it may not build
> there without changes. And kks32/mpm-engine's current public README is a dough/robot-
> manipulation MPM engine with only a box collider, no mesh-to-rigid-body SDF or water material
> yet. Did you want me to (a) get kks32/mpm-engine installed and its own benchmark running as an
> environment check, (b) actually try to extend it for the car-in-water case, or (c) did you
> mean PhysSplatLab specifically when you said "what Cheng-Hsi has"? Meanwhile I'm continuing on
> the Genesis-native vehicle import since that's already confirmed working on Vista and doesn't
> depend on this being resolved.

