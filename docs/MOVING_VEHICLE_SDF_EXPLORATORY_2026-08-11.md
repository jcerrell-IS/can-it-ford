# Driven-hull SDF collider: exploratory, NON-CANONICAL

Date: 2026-08-11. Branch `claude/moving-vehicle-exploratory-2026-08-11`.

**Scope statement, read this before anything else.** Nothing in this document is
canonical, validated, or citable as extending any existing result. It does not
extend `docs/MULTIGEOM_VALIDATION_2026-08-11.md`, it does not touch the 17-run
canonical store, and it must not be folded into the corrections register. It is a
first exploratory scene on a code path that had never been pointed at a real hull.

**There is no FORD or NO-FORD verdict anywhere in this work, and none is
derivable from it.** That verdict belongs to the AR&R-validated stationary-vehicle
criterion (CLAUDE.md L-1), which describes a stationary vehicle subjected to flow.
This scene drives the vehicle and removes exactly the degree of freedom that
verdict is about.

Every number below was produced or read live this session. Where something is
carried from another document it says so.

---

## 1. What this closes, and what it does not

`docs/MULTIGEOM_VALIDATION_2026-08-11.md` section 6 recorded the SDF-collider
cross-check as BLOCKED: `simulation/validate_coupling_force.py` builds its
geometry from `cube_mesh(length)` at line 115 and `run_c1_sdf` at line 705 has no
mesh parameter, while `simulation/box_sdf_collider_setup.py` hardcodes
`BOX_DIMS_M = (4.66, 1.79, 1.44)` through `trimesh.creation.box`. Neither can load
a hull.

`simulation/moving_vehicle_sdf_exploratory.py` closes that specific gap. A real
watertight vehicle hull now loads through the SDF collider path and runs. Both
originals are untouched.

It does **not** deliver a coupling comparison against the canonical 17. Section 5
explains why the resolution this scene can reach makes the measured wrench
quantitatively unusable, which is the main finding here and the reason this
document exists.

---

## 2. Provenance

Hull: `rogue_g96_pd8_coarse_watertight.ply`, sha256
`c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2`, fetched from
`vista:$WORK/hulls/` this session and verified byte-identical to the digest in
`MULTIGEOM_VALIDATION_2026-08-11.md` section 1. **No `.ply` was committed**, per
register E8 on CCSA licence. The file lives outside the repo in a session
scratchpad.

Measured live through the loader: 36,074 verts, 72,520 faces, watertight True,
volume **4.950341 m3**, canonicalized extent (x, y, z) =
2.010112, 4.746607, 1.729385, long axis on y.

Two independent checks that the pipeline is the canonical one:

- The volume reproduces the 4.9503 m3 already on record for this hull.
- Feeding the canonicalized extent through `sim_standing.py:159`'s
  `lim = max(2.2*ext[1], 3.5*ext[0], 6*depth)` gives `grid_lim` 10.442536 m, so dx
  at `n_grid` 64 is **0.163165 m** against the published `class_rogue_g64`
  value of 0.16316.

---

## 3. The loader, and a trap worth recording

The vetted loader is `load_vehicle` as it exists in
`renders/yaris_render_s1/vehicle_live.py:207`, which the 17 gated runs ran. This
work imports the tracked byte-identical copy at
`analysis/render_v1/as_ran_local_copies/vehicle_live.py:207` (both sha256
`5a5bbbab7d2e21df16f59fc3f0d55d40744f61861223cc43160714c6175d5944`), because
`renders/` is gitignored and absent from this worktree. No new loader was written.

**Do not substitute the installed `warpmpm.vehicle.load_vehicle` on this Mac.**
The site-packages copy is older than Vista's: its exports are
`FloodHistory, FloodScene, GridConfig, Path, Solver, VehicleBody, load_vehicle,
solidify_columns`, with **no `is_gaussian_ply` gate and no `solidify_watertight`**,
so it routes every `.ply` to the Gaussian-splat branch. Tested live against this
hull, it fails with `ModuleNotFoundError: No module named 'plyfile'`, that is, it
took the splat branch on a plain mesh. Whether it would return garbage rather than
an error with `plyfile` installed was not tested.

---

## 4. Two mechanical facts established at the source

**The SDF collider self-advects.** `set_sdf_pose`'s docstring claims it and the
source confirms it: `kernels/mpm_solver_warp.py:2756` inside the `modify` closure
reads

```python
param.center = wp.vec3(c[0] + dt*v[0], c[1] + dt*v[1], c[2] + dt*v[2])
```

registered as `modify_bc` at `:2776` and called every substep at `:1332-1333`. So
passing `velocity=` to `add_sdf_collider` genuinely translates the hull; the pose
does not have to be driven frame by frame. Confirmed in the run output: the
collider centre advances by exactly `v/fps` per frame, read back out of
`collider_params[handle].center` rather than assumed.

**`sdf_wrench` is a real force accumulator**, `force = sum m*(v_free - v_new)/dt`
(`core/solver.py:354`), unlike the material-8 free-rigid path the canonical 17 use,
where no force is ever formed (register A-1). Every frame of every run reported
here returned finite force and torque: **0 non-finite frames**.

---

## 5. The finding: this scene cannot resolve its own water column

This is the result that matters and it is negative.

The validated C1-SDF buoyancy harness runs at **`depth_cells=18.0`**
(`validate_coupling_force.py:705`), and that is the regime in which its 7.3 to 7.7
percent agreement with analytic was established. This scene, at the canonical
0.30 m depth on a domain sized from the hull's own extent, gets:

| n_grid | dx (m) | water depth in cells | water particle layers | contact band / depth |
|---|---|---|---|---|
| 48 | 0.217553 | 1.38 | 3 | 73% |
| 64 | 0.163165 | 1.84 | 4 | 54% |
| 96 | 0.108776 | 2.76 | 6 | 36% |
| 128 | 0.081582 | 3.68 | 7 | 27% |

Even the finest locally-feasible grid is **five times coarser in depth than the
validated regime**. Two independent consequences, both measured:

**(a) The floor boundary corrupts a fixed absolute depth, so it corrupts a large
fraction of a shallow column.** An MPM plane BC is enforced on grid nodes, so
particles settle up to about one cell below it. Measured penetration saturates at
**0.93 to 1.01 dx across every resolution tested**, which makes the corrupted
fraction of the water column approximately `1 / depth_cells`. At the validated 18
cells that is 6 percent. Here it is 27 to 72 percent. No mass is lost: particle
count is fixed and 0 particles ever left the domain. The column is smeared, not
drained.

**(b) The at-rest vertical reaction is wrong by a large factor, and not even
consistently in one direction.** The one quantity in this scene with an
independent analytic target is the at-rest reaction against `rho*g*V_submerged`.
`V_submerged` comes from the repo's own vetted `solidify_watertight` fill, which
reproduces the mesh volume to -0.21 percent, giving 0.504603 m3 below z = 0.30 m
and an analytic **4950.2 N** for the hull.

<!--LADDER-->

The hull reads high and the box control reads low at the same resolution. That
rules out a single calibration offset and points at geometry-dependent band
effects: the contact band is a fixed 1 dx skirt around the hull, which at 0.22 m
merges the Rogue's slender submerged features (wheels, underbody) into a much
larger effective displaced volume, while the box, which already spans its full
footprint, instead loses level to the over-carve and the floor smear.

The traces also never reach a steady value within 150 frames (5.0 s); Fz
oscillates by a factor of 2 or more between reports. The validated harness settles
for 600 frames.

**Consequence: no force number from this scene is quotable.** Not the drag, not
the buoyancy, not the torque. They are reported here only as evidence about the
resolution, never as measurements of the vehicle.

---

## 6. What the scene does show

<!--BOWWAVE-->

---

## 7. Two reusable findings that are not about this scene

**The SDF cache never hits, because the vetted loader is not bit-reproducible.**
`load_vehicle` draws 60,000 **random** surface samples and derives the mesh shift
from them, so `v.mesh` differs between calls. `canonicalize()` re-derives the shift
from the mesh and cancels it mathematically but not bitwise. Measured 2026-08-11:
back-to-back unseeded loads differ by **2.22e-16 m**, one ULP, physically nothing,
but enough to change `build_sdf_cached`'s content hash. Every run therefore
rebuilt its SDF from scratch, about 6 to 8 minutes at res 32 and 45 at res 64.
Seeding numpy's global RNG first makes the loads bitwise identical and the cache
usable. This is a concrete downstream cost of the already-known
mesh-pipeline non-reproducibility.

**The SDF build, not the solve, is the binding cost, and it is CPU-bound
regardless of venue.** `build_sdf` signs via a generalized winding number that is
O(points x faces) in pure numpy, chunked over points at 4096 and vectorised over
all faces (`mesh_sdf.py:205-231`). At the Yaris hull's 655,308 faces one
`(4096, F, 3)` float64 array alone is 64 GiB, which is what OOM-killed Dispatch A's
`yaris_sdf_smoke.py` (commit `9480b0a`, exit 137). This work reduced the point
chunk to 128, which drops peak memory to 0.83 GiB and is **numerically an
identity**: the loop splits the point axis only and each point's solid-angle sum
still runs over all faces in the same order. Verified live, chunk 4096 against
chunk 128 is bitwise identical. Measured throughput on the 72,520-face Rogue hull
is 99.5 points/s, so res 32 is about 6 minutes, res 64 about 45, res 96 about 148.

The hull was deliberately **not** decimated. Decimation is cheap on volume
(8,000 faces costs -0.379 percent, 4,000 costs -0.663 percent) but **breaks
watertightness at every level tested**, which is the wrong trade given
`vehicle_geometry_research/failed_reconstructions_2026-07-25/README.md`.

Because `build_sdf` is numpy on the CPU, a GPU allocation would not accelerate it.
Only the MPM solve is GPU work, and the MPM solve turned out to be cheap.

---

## 8. Cost, and why no Vista job was submitted

<!--COST-->

---

## 9. Deliberate deviations from `sim_standing.py`, with reasons

- **Planes use friction 0.0 and restitution 0.0**, not 0.55 and 0.05. This scene
  has no rigid PARTICLES at all, so 0.55, a vehicle-on-bed Coulomb coefficient,
  has nothing to act on, and applying it to water would be an unsourced bed
  friction model. `validate_coupling_force.py:277-282` makes the same deviation
  for the same reason. Note `mpm_solver_warp.py:1915` registers rigid contact only
  when restitution is non-zero, and there is no rigid body here to register.
- **Collider `surface="separable"`, `friction=0.4`** are `add_sdf_collider`'s own
  engine defaults and are NOT tuned, matching `validate_coupling_force.py:296`.
- **Settle is 60 to 150 frames, not 8.** `sim_standing.py` uses 8, which is 0.27 s
  against a 10.44 m / 12.85 m/s = 0.81 s acoustic transit, so the pressure field
  has not equilibrated. Even 150 frames is not enough here, see section 5.
- **A 15-frame velocity ramp** replaces a step change, which would otherwise
  accelerate about 505 kg of displaced water inside a single substep. Ramp frames
  are flagged `in_ramp` and are not a steady reading.
- **Water is carved within one contact band of the hull**, not just inside it, so
  no particle starts inside the band where the collider BC acts. The carve uses a
  nearest-cell SDF lookup, accurate to half an SDF cell.

---

## 10. What would have to change for this to become quantitative

1. Water depth resolved to something approaching the validated 18 cells. At the
   canonical 0.30 m on this domain that means `n_grid` of order 600, which is a
   GPU-scale problem, or a deeper scenario, or a smaller domain, which conflicts
   with the travel room a moving vehicle needs.
2. A settle long enough to reach a steady at-rest reaction, of order the validated
   harness's 600 frames.
3. An at-rest reaction that agrees with `rho*g*V_submerged` before any moving
   result is read. That check is built into the script and currently fails.
4. A contact band small relative to the water depth. Band defaults to dx, and
   shrinking it below dx risks leakage rather than fixing anything, so this is the
   same requirement as item 1.

Until item 3 passes, this scene answers a qualitative question only.

---

## 11. Files

- `simulation/moving_vehicle_sdf_exploratory.py`, the scene. `--settle-only` runs
  the at-rest resolution probe.
- `analysis/render_moving_vehicle_placeholder.py`, a labelled placeholder plot,
  not artwork. Dispatch A had established no render path for this scene; the
  existing `analysis/render_multigeom_rollout.py` targets the free-rigid schema
  (`veh_particles_scene0` plus a rigid R/t reconstruction) which a kinematic
  collider has no analogue for.
- Outputs under `out/`, which is gitignored. No large binary is committed.
