# RENDER-v1 through AMENDMENT A: process record

Session `f59c1292-11dc-4c13-971c-40d183ffc9e2`, 2026-07-25.
Machine: MacBook (local). No Vista job was submitted in this session.

This file is the durable record of a render/verification pass whose working
directory, `renders/yaris_render_s1/`, is **gitignored** (`.gitignore:14`,
rule `renders/`). Everything noteworthy from that directory is mirrored into
tracked locations listed under "Archive layout" below.

## Provenance convention used in this file

Every number carries a tag. Nothing here is copied from a summary without a tag.

- **[LIVE]** re-measured at the time this file was written, command shown or
  reproducible from the archived script.
- **[RUN]** measured during the session, recorded in the session transcript,
  **not** re-measured at write time.
- **[INCOMPLETE]** the job that would produce it did not finish. No value is
  stated. Do not fill these in from memory.

---

## A0. The code that actually ran is patched, and diverges from upstream

Upstream is `kks32/mpm-engine` at pinned SHA
`544c93dd02cb9c7ead89e1155a62967243244fce`, archived under
`third_party/mpm-engine-544c93dd/`.

| | upstream `vehicle_main.py` | local `vehicle_live.py` (as ran) |
|---|---|---|
| PLY dispatch | `:121` `if path.suffix.lower() == ".ply":` | `:221` `... and is_gaussian_ply(path)` |
| solid fill | `:104`, `:156` `solidify_columns` always | `:176`, `:266` `solidify_watertight` when watertight |

**[LIVE]** both greps re-run against the archived upstream copy and against
`analysis/render_v1/as_ran_local_copies/vehicle_live.py`.

Consequence: upstream would route a watertight mesh PLY into
`load_gaussians_ply`, which reads `opacity` / `f_dc_0` / `scale_0` / `rot_0`,
none of which a mesh PLY has. It would crash. The runs did not crash, which is
independent evidence the local copy is the one that executed.

Second consequence, and the one that matters for the gate: `solidify_watertight`
is exact vertical ray parity, so every solid particle is inside the mesh by
construction. That is why absolute containment is a meaningful test here, and it
is why AMENDMENT A's retraction of the absolute threshold (which assumed
`solidify_columns` fills wheel wells outside the surface) does not apply to
these runs.

## A1. The mesh frame

`load_vehicle` order: `_up_rotation(up)`, then long-axis-to-Y `Rz` if
`ext[0] > ext[1]`, then optional `target_length` scale, then centre x/y and put
the floor at z=0.

**[LIVE]** native extent after `Rz`, from
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`:

```
ext (x, y, z) = [1.746378  4.282610  1.518008]
watertight = True   faces = 655308   volume = 3.542739 m3
```

`ext[0] = 1.746 < ext[1] = 4.283` only **after** `Rz`; on disk the long axis is
X, so `Rz` fires and maps `(x,y,z) -> (-y,x,z)`.

This rotation is absent from RENDER-v1's T1c. Without it the car renders
sideways. T1b cannot detect the omission, because T1b compares particles to
particles and never touches the mesh.

**[RUN]** A1b residual between the run's `sample(60_000)`-derived shift and the
vertex-derived shift: `2.03e-07 m`, which is 0.4 float32 ulp at this scale. The
unseeded sample did not move the bounding box by a representable amount, so no
correction was applied. The unseeded sampling is still a genuine reproducibility
defect for mesh inputs and belongs in Limitations.

## A2. The containment gate

**[LIVE]** `trimesh.ray.has_embree = False` on this machine, so the gate was run
subsampled rather than over all particles.

**[RUN]** `docs/render_v1_task_outputs/A2_containment_gate.output`:

```
rotated mesh extents      [1.746378 4.28261  1.518008]
particle  extents         [1.692969 4.19562  1.472147]   h = 0.07360736280679703
particle bbox lo          [-0.836385 -2.104501  0.036804]  hi [0.856584 2.091118 1.508951]
mesh-in-vehframe bbox lo  [-0.873189 -2.141305  0.      ]  hi [0.873189 2.141305 1.518008]
watertight True   volume 3.542739
CONTAINMENT bbox-match: 100.00% of 2000 sampled solid particles inside mesh
```

**[RUN]** the full pose chain reproduces the stored `veh_check_45` and
`veh_check_last` to `1.06e-6 m`.

### A2b four-rotation relative gate: **[INCOMPLETE]**

Task `bpu7vpmd2` was still running when the session was interrupted and has
since been marked stopped by the harness. Its output file contains only the
header line and no data rows. Preserved verbatim at
`docs/render_v1_task_outputs/A2b_four_rotation_gate.output`.

The four fractions (source `Rz`, `Rz` inverse, identity, 180 degrees) have
**not** been measured. AMENDMENT A requires that source `Rz` be the clear
maximum. That check is outstanding. Do not treat the 100.00% absolute figure as
a substitute: it is a different test.

### A2d does the particle offset apply to the mesh

**[LIVE]** the particle-to-particle offset, recomputed from the npz:

```
mean = [ 0.001333  0.002008 -0.061347]     std_max = 2.019e-06
```

`std_max` at 2.0e-6 confirms the term is a rigid translation, not a deformation.

Measured argument that it applies to the mesh as well: solid particles are
generated by exact ray parity against this mesh, and 100.00% of the sampled
particles fall inside the mesh in the vehicle frame. Mesh and particles
therefore share a frame with zero relative offset, so whatever maps particles
into the pose frame maps the mesh identically. This is a measurement, not an
assumption, but note it rests on the subsampled gate above.

## A3. Decimation

**[LIVE]** `fast_simplification 0.1.13` is installed, so
`simplify_quadric_decimation` did not raise and returned exactly 50,000 faces.
The gate ran on the full 655,308-face mesh; decimation is for drawing only.

## A4. Water surfacing

### The retraction was correct

**[RUN]** Kumar's `examples/common.py::surface_from_cloud` returns an **open**
mesh on this domain: `watertight False`, `euler_number 551`, enclosed volume
`2.6310 m3` against a true `19.2891 m3`.

Cause, diagnosed by reading the source: the pad is a hardcoded `0.012 m`. On the
0.4 m dough domain that is about 3.6 cells. Here `cell = h/2 = 0.036804`, so
0.012 m is **0.326 cells**, well under `sigma = 1.3`. The density field never
decays to zero before the array edge, marching cubes clips at the boundary, and
the surface never closes.

### The prescribed sweep range does not contain the answer

Replacement is `examples/recovery/nclaw_geom_render.py::_surface` at the pinned
SHA: 4-cell pad, adaptive isolevel `iso_frac * fld[fld>0].mean()`, spacing
passed into `marching_cubes`.

**[LIVE]** calibration target from the npz:

```
h = 0.073607362807   cell = h/2 = 0.036804   n_water = 48367
V_true = n_water * h^3 = 19.2891 m3
```

**[RUN]** sweep on frame 45, `g64_m1100`, `sigma = 1.3`:

| iso_frac | volume error | note |
|---|---|---|
| 0.20 | +36.66% | prescribed range |
| 0.25 | +32.66% | prescribed range |
| 0.30 | +29.13% | prescribed range, and the source default |
| 0.35 | +25.95% | prescribed range |
| 0.40 | +23.05% | prescribed range |
| 0.50 | +17.97% | extension |
| 0.70 | +9.62% | extension |
| **0.90** | **+2.42%** | **chosen, euler_number 2, single closed body** |
| 1.10 | -4.33% | euler_number 54, fragments |

AMENDMENT A's prescribed range `[0.20, 0.40]` spans +23% to +37% and never
reaches the target. The source's own default of 0.30 is off by +29%. `0.90` was
chosen by measurement, and it is the only value tested that is both within 3%
on volume and a single closed body.

Note this beats the padded `common.py` variant on topology even though the
padded variant was closer on volume (-2.45%, but `euler_number 40`).

## A5. P-2 discriminator

**[LIVE]** the npz carries no leak counter. Keys present:

```
R, depth, dx, extent, floor, fps, frames, h, lim, local_depth_bow,
local_depth_footprint, mass, n_grid, speed, t, veh_check_45, veh_check_last,
veh_particles_scene0, veh_particles_vehframe, velocity, water
```

No key matches `leak`. The independent `scene.leaked` signal AMENDMENT A hoped
for is not available from these rollouts.

### mesh.contains series: **[INCOMPLETE]**

Task `bmqm36363` was still running at interruption and has since been marked
stopped. Its output file contains the header and column titles only, no data
rows. Preserved verbatim at
`docs/render_v1_task_outputs/A5_p2_mesh_contains.output`.

### What was resolved, by the voxel route instead

**[RUN]** `t4_defects.py::t4b` computes two independent membership tests per
frame over all 90 frames: the AABB of the posed vehicle, and the vehicle's own
pitch-`h` solid voxel occupancy set, which is the body the simulation actually
integrated.

- AABB reads **8.3301% at frame 0**, where penetration is zero by construction.
  Most of the headline 10.67% is bounding-box void, not water inside the car.
- Voxel occupancy peaks at **1.4411%** (m1100), **0.9014%** (m1609),
  **0.5376%** (m2337).
- Rises above each run's own frame-0 baseline: **+1.05, +0.52, +0.17 pp**, which
  order with displacement, as physical penetration should.
- For m2337 the AABB maximum occurs at frame 0 itself.

**Verdict, in writing:** the 10.67% P-2 failure is dominated by an AABB
artifact. A real but small penetration signal exists on top of it, it is
sub-1.5% of water particles, and it scales with vehicle displacement. The
`mesh.contains` run would tighten this but the voxel test already uses the
simulation's own solid body, which is arguably the stricter comparison.

## A6. Class discretization, measured rather than predicted

AMENDMENT A retracted the predicted densities (310 / 303 / 369) and required
measurement. `target_length` changes `ext`, which changes
`lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)`, which changes `dx = lim/n_grid`,
`h = dx/2`, `floor = 3*dx`, the particle count, and the water layer count.

**[LIVE]** re-measured at write time, `depth = 0.30`, `n_grid = 64`:

| class | target_L | lam | lim | dx | h | floor | **layers** |
|---|---|---|---|---|---|---|---|
| small_passenger | 4.283 | 1.000 | 9.42174 | 0.147215 | 0.073607 | 0.441644 | **4** |
| large_passenger | 4.900 | 1.144 | 10.78000 | 0.168438 | 0.084219 | 0.505313 | **4** |
| large_4wd | 5.200 | 1.214 | 11.44000 | 0.178750 | 0.089375 | 0.536250 | **3** |

**A6b confound, stated in writing as required:** the three-class table would
**not** be like-for-like. `large_4wd` discretizes the water column 25% coarser
and receives three layers where the other two receive four. Its displacement
would conflate mass, length, and water discretization. Combined with the finding
that ground clearance is already in the live spec (`vehicle_params.py:169, 174,
179`) and with Kumar's own "you can import a PLY directly", `target_length`
rescaling cannot carry class labels.

**This is the finding that blocks T3.** To make the rows comparable you must
hold the layer count fixed, which means varying `n_grid` per class so `h`
matches, or you must accept the confound and state it. That is a design decision,
not a code fix.

## A7. Greps, all re-verified live

**A7a floor_friction. [LIVE], and it falsifies the amendment in the writeup's
favour.** `sim_standing.py:76` defaults `floor_friction=0.55`; `:253` passes
`floor_friction=a.floor_friction`; `:280` and `:355` record it. The runs used
**0.55, not 0.5**. The claim that the driver never passes it is wrong for this
driver. Note also the driver is `StandingFloodScene` (`:73`), not Kumar's
`FloodScene`, so `flood_vehicle.py::run` does not govern these runs at all.

**A7b water_eta. [LIVE]** `sim_standing.py:75` defaults `water_eta=1.0e-3`,
`:226` sets `--eta` default `1.0e-3`, `:253` passes it. The corrected value was
used.

**A7c the arange fragility. [LIVE], confirmed upstream and the mechanism
corrected.** The fragile pattern is in Kumar's code, not this project's:
`third_party/mpm-engine-544c93dd/vehicle_main.py:262-264`.

Re-measured from the npz:

```
span   = 8.170417271554470
span/h = 111.000000000000
span - 111*h = 0.000e+00        <- exact to the last float64 bit
arange count = 111
111 * 111 * 4 = 49284;  49284 - 48367 (stored n_water) = 917 carved
```

The ulp reasoning in the amendment is right that float32 storage alone cannot
explain a 22 micrometre delta, and the truth is stronger than that: `span` is an
**exact integer multiple of h**, so this is an arange boundary landing, not a
round-trip error. Both candidate `lim` values yield 111 columns, so the 22
micrometre delta changes nothing. The count only flips between the float32-stored
path (111, what ran) and a float64 recompute (112). Recomputing the scene from
the mesh does not reproduce the run's own discretization.

Fix, implemented in `t4_defects.py::t4a`: replace `np.arange(start, stop, h)`
with an explicit count, `n = floor((stop-start)/h + eps) + 1`, then
`np.linspace(start, start + (n-1)*h, n)`.

## A8. Vendoring and licence

`third_party/mpm-engine-544c93dd/VENDORED.md` records the raw URL pattern,
pinned SHA, fetch date, licence, and the upstream-vs-local divergence table.
Licence is **MIT**, confirmed by fetching `LICENSE` at the pinned SHA.

**Open provenance caveat, carried forward:** five of the eight files
(`examples/common.py`, `examples/dough_surface_render.py`,
`examples/flood_vehicle.py`, `splats/appearance.py`, `tests/test_vehicle.py`)
were fetched from `main` before a SHA was pinned. They are reproducible only if
`main` has not moved. **Re-fetch them at the pinned SHA before any is cited in
the paper or relied on.** The three that drive the render
(`vehicle_main.py`, `nclaw_geom_render.py`, `LICENSE`) are pinned.

---

## Final render

`figures/render_v1/realistic_A4_g64_m1100_f0045.png`, opened and judged in
writing during the session. **[RUN]**

- Car shaded with three distinguishable colours from geometric segmentation
  performed in the vehicle frame, so it is pose-invariant: body, glass, tyres.
- Water is a **single closed body**, `euler_number 2`, `watertight True`.
- Enclosed volume `19.7550 m3` against the true `19.2891 m3`, **+2.42%**.
- `water_faces_total = 244652`.
- Car and water are rendered in **one** `Poly3DCollection` with per-face RGBA.
  Separate collections are depth-sorted as wholes by matplotlib's painter's
  algorithm, which paints the water sheet over the entire car and fabricates a
  false waterline. The ground plane is subdivided 24x24 for the same reason:
  two large triangles sort wrongly against thousands of small water triangles.

This satisfies the RENDER-v1 stop condition: a frame personally opened and
judged, showing a shaded car with more than one colour and a water isosurface
whose enclosed volume was measured against the target.

## Still open at the end of this session

1. **A2b** four-rotation relative gate, never completed. Slow because
   `has_embree` is False.
2. **A5** `mesh.contains` P-2 series, never completed, same reason.
3. **T3** blocked on the A6b design decision above, not on code.
4. **v16 O5** velocity sweep `{0.10, 0.15, 0.50, 1.00, 1.50}` at depth 0.30,
   mass 1100, standing water, `n_grid 64`, plus displacement-vs-inflow-velocity
   plot. Requested twice by Kumar, two meetings overdue. Not started.
5. **Vista patch** commit: three modified tracked files at Vista HEAD `fd390d6`.
   Requires explicit confirmation before any push.
6. **Re-fetch** the five unpinned vendored files at the pinned SHA (A8 above).

## Security items carried forward, not resolved in this session

- A password was pasted into this session's chat and is stored in plaintext in
  `~/.claude/projects/-Users-josie/f59c1292-11dc-4c13-971c-40d183ffc9e2.jsonl`.
  It was never used. Treat that credential as compromised and rotate it.
- Vista `~/.bashrc:112` exports a live plaintext `CLAUDE_CODE_OAUTH_TOKEN` on a
  shared login node. The value was redacted, never read. Rotate it.
  (Line measured as 112; an earlier directive said 117.)

---

## Archive layout

`renders/yaris_render_s1/` is gitignored, so this is where the work now lives:

| path | contents |
|---|---|
| `analysis/render_v1/` | scripts written this session, plus their JSON/log outputs |
| `analysis/render_v1/as_ran_local_copies/` | `vehicle_live.py`, `common.py`, `sim_standing.py`, job scripts. The patched code that actually ran, pulled from Vista. Not upstream. |
| `figures/render_v1/` | the four rendered PNGs |
| `docs/render_v1_task_outputs/` | raw background-job output, including the two truncated ones |
| `third_party/mpm-engine-544c93dd/` | vendored upstream with `VENDORED.md` and `LICENSE` |
| `vehicle_geometry_research/failed_reconstructions_2026-07-25/` | the two failed reconstruction meshes, see the README there |

**Not archived:** `renders/yaris_render_s1/*/rollout.npz`, 397 MB across six
runs. Raw simulation data, still on disk in the gitignored working directory.
Back it up separately if the machine is at risk. Everything in this document was
derived from `g64_m1100/rollout.npz`.

The environment that runs these scripts is not a checked-in venv. Reproduce with:

```bash
uv run --python 3.12 --with numpy --with trimesh --with scikit-image --with scipy --with fast-simplification python t1_car.py
```
