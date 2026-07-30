# Vista source reads, Stage 2 half one, 2026-07-25 23:40 CDT

Read-only. No GPU, no allocation, no venv activation, nothing installed, nothing written on
Vista. All reads over the existing ControlMaster socket at `~/.ssh/cm-vista`.

Repo root read: `/work/11603/jcerrell0629/vista/mpm-engine`

## Provenance guarantee, established first

```
/work/11603/jcerrell0629/vista/.venv/bin/python -c "import warpmpm; print(warpmpm.__file__)"
-> /work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/__init__.py
```

MEASURED. The installed package resolves to the same working tree that was read. Every
SOURCE line below is therefore the code that actually produced the `g64_m*` and `m*`
rollouts, not a possibly-divergent copy. Without this the whole pass would be
circumstantial.

---

## 2a. What exists

SOURCE, `ls` output.

`tests/` contains 27 files. **`tests/test_analytic_benchmarks.py` EXISTS.** Also present and
relevant: `test_vehicle.py`, `test_sdf_collider.py`, `test_cdf_collider.py`,
`test_coupling.py`, `test_splat_bake.py`, `test_splat_export.py`, `test_splats.py`,
`test_mesh_sdf.py`, `test_pour.py`.

`src/warpmpm/`: `adapters`, `colliders`, `core`, `coupling`, `geometry`, `__init__.py`,
`kernels`, `materials`, `render`, `scenes.py`, `splats`, `vehicle.py`, and
`vehicle.py.bak_preparity`.

`src/warpmpm/core/`: `__init__.py`, `solver.py`. That is all.

Two notes. First, DeepWiki's paths were correct this time for `tests/` and
`core/solver.py`; that is a single observation and does not retire the 2026-07-24 finding
that it was wrong about this repo. Second, `vehicle.py.bak_preparity` is an untracked-looking
backup sitting next to the live `vehicle.py`. Not read, not touched. Flagged only so it is
not mistaken later for the module that runs.

## 2b. Friction, the literal defaults

SOURCE.

`src/warpmpm/core/solver.py:318-321`

```
def add_sdf_collider(self, sdf, center, quat=(0.0, 0.0, 0.0, 1.0),
                     velocity=(0.0, 0.0, 0.0), omega=(0.0, 0.0, 0.0), band=None,
                     surface: str = "separable", friction: float = 0.4,
                     start_time: float = 0.0, end_time: float = 1.0e9) -> int:
```

**`add_sdf_collider` default friction is 0.4.** Confirmed at the kernel level too,
`src/warpmpm/kernels/mpm_solver_warp.py:2623`, same literal `friction=0.4`.

The number is right. It is also **not the friction that acts in the flood runs**, because
`add_sdf_collider` is never called by them. See 2e.

The friction that does act comes in through `add_plane`. Surface-type mapping,
`mpm_solver_warp.py:1905-1912`:

```
if surface == "sticky":   collider_param.surface_type = 0
elif surface == "slip":   collider_param.surface_type = 1
elif surface == "cut":    collider_param.surface_type = 11
else:                     collider_param.surface_type = 2
# frictional
collider_param.friction = friction
```

The plane collide kernel, `mpm_solver_warp.py:1974-1989`:

```
v = state.grid_v_out[grid_x, grid_y, grid_z]
normal_component = wp.dot(v, n)
if param.surface_type == 1:
    v = (v - normal_component * n)              # Project out all normal component
else:
    v = (v - wp.min(normal_component, 0.0) * n) # Project out only inward normal component
if normal_component < 0.0 and wp.length(v) > 1e-20:
    v = wp.max(0.0, wp.length(v) + normal_component * param.friction) * wp.normalize(v)
```

Read this carefully, because the obvious guess is wrong. `"slip"` here does **not** mean
frictionless. The friction branch sits **outside** the if/else and is gated only on the
material approaching the plane. So `surface="slip"` projects out the entire normal
component and then applies Coulomb friction on top. **`floor_friction` is live, not inert.**

## 2c. The 100 to 300 kg/m3 band, C11 CLOSED

SOURCE. `src/warpmpm/vehicle.py:328-337`, the `FloodScene` class docstring:

> A flood surge hitting a rigid vehicle from the side.
>
> A water slab of the given depth spawns upstream with an initial velocity along +x
> and breaks against the vehicle. The vehicle is one rigid body: the fluid's grid
> momentum accumulates into its force and torque each substep, so sliding, floating,
> and overturning come out of the coupling. vehicle_density is the body's effective
> density (vehicles are mostly air; a car is roughly 100 to 300 kg/m^3 spread over
> its volume, which is why they float); vehicle_mass, if given, overrides it with a
> total mass in kg. The realized mass is self.vehicle_mass either way.

The band is at **`vehicle.py:335`**. C11 moves **UNRESOLVED to SOURCE**. It is not a
DeepWiki artifact and not an unattributed project anchor: it is Kumar's own docstring.

What it actually is, though, matters more than where it is. The band is the stated
rationale for the default `vehicle_density: float = 250.0` (`vehicle.py:342`), and the same
sentence says `vehicle_mass`, if given, **overrides** it. Our runs all specify
`vehicle_mass`. So the density path is overridden and the band is not a constraint our runs
violate. It is a rule of thumb for the path we did not take. This corrects `limitations.md`
L-4, which currently reads as though realized density being outside 100 to 300 were a defect
in the runs.

## 2d. splat_pos

SOURCE. `tests/test_vehicle.py:74`, inside `test_load_vehicle_from_mesh`:

```
assert v.splat_pos is None  # meshes render nothing; particles still simulate
```

`vehicle.py:164` declares `splat_pos: np.ndarray | None = None`. `vehicle.py:271` sets it
only `if splat_colors is not None`. `vehicle.py:491-496`, `splat_positions()` returns None
when `splat_pos` is None.

Consequence for Stage 4: if the Yaris takes the mesh path, the vehicle **cannot be drawn
from splats** and the render must use `vehicle.particles` or the `surface` array
(`vehicle.py:270`, `surface=pos.astype(np.float32)`).

**This is not yet established for our vehicle.** The test proves it for a trimesh-generated
STL. Our input is `yaris_coarse_v1l_watertight.ply`, and a `.ply` can carry vertex colors,
which is exactly the condition at `vehicle.py:271`. Whether `load_vehicle` populates
`splat_colors` from a coloured `.ply` was **not read**. Class: UNRESOLVED, logged as R1
below. Do not design the render around either answer until it is checked.

## 2e. Which collider path the flood runs use

This is the item that came back differently from how it was asked.

SOURCE, the full grep for collider calls in `vehicle.py`:

```
270:                       surface=pos.astype(np.float32),
397:        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
401:            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
```

**`vehicle.py` contains no `add_sdf_collider` call and no `add_cdf_collider` call.** Line
270's `surface=` is a keyword argument for the vehicle's surface point array, not a collider
surface mode. The SDF-versus-CDF question does not apply to this scene, because **the
vehicle is not a collider at all.**

The vehicle is a **rigid particle body**, coupled two-way through the grid:

```
392:        s.set_material_range(self.n_water, self.n_total, "rigid", obj_id=0,
393:                             density=vehicle_density)
394:        s.finalize_rigid_bodies()
```

The only colliders in the scene are planes:

- `vehicle.py:397-398` floor, `"slip"`, `friction=floor_friction`, `restitution=0.05`
- `vehicle.py:400-401` four inset side walls, `"slip"`, `friction=0.0`, `restitution=0.05`
- `vehicle.py:402` `s.add_domain_walls()`, which per `core/solver.py:309-314` will "Zero
  outward velocity in a three-cell band at each domain face."

The comment at `vehicle.py:395-396` says why restitution is nonzero:

> restitution > 0 makes each plane a rigid-body contact surface as well; the
> grid BC alone holds only the water, and the body would sink through the floor

So the body is held by a second, separate mechanism: `_apply_rigid_restitution`,
`mpm_solver_warp.py:886`. It reads the same friction value (`mu = float(surf["friction"])`)
and applies a genuine Coulomb-capped tangential impulse, `mpm_solver_warp.py:965-976`:

```
J_n = -(1.0 + e) * v_n / denom
...
if mu > 0.0:
    ...
    J_t = min(v_t_mag / denom_t, mu * J_n)
```

So a true static hold **is** representable in principle: when under the Coulomb cap, `J_t`
is the impulse that fully stops sliding at the contact point.

### The caveat that the source states itself

`mpm_solver_warp.py:938-940`, verbatim:

> Positional stabilization: project the body out of the surface by
> the deepest penetration. The grid gather resets v_cm every substep,
> so the impulse alone cannot hold a resting body against sustained
> load; without this it creeps through the plane.

And `mpm_solver_warp.py:951-952`: `if v_n >= 0.0: continue  # already separating`.

### The consequence, and its evidence class

`J_n` is proportional to the instantaneous normal **approach speed** `v_n`, not to the
normal force or the body's weight. For a body resting on the floor under sustained lateral
drag, which is precisely the ford scenario, `v_n` tends to zero. Then `J_n` tends to zero,
and the Coulomb cap `mu * J_n` tends to zero with it. In that regime the tangential hold
from this path collapses, and it collapses regardless of what `floor_friction` is set to.

**Class: HYPOTHESIS derived from SOURCE. Not measured.** The code lines are quoted above
and are SOURCE; the behavioural consequence is an inference from them, and `v_n` has not
been instrumented in any run. Per the standing rule this does not go into a caption, a
poster, a limitation stated as fact, or a sentence written for Kumar until it is measured.
Logged as R2.

### What this does and does not do to the frozen finding

It does **not** invalidate it. The frozen finding claims displacement magnitudes and
NO-FORD verdicts. Every standing-water run exceeds `DRIFT_THRESHOLD = 0.05 m`, so the
finding never claims that any vehicle held. A weaker-than-intended floor hold biases toward
**more** sliding, which is the direction already reported, so the finding is conservative
with respect to this mechanism rather than threatened by it.

It bears on exactly one recorded verdict: the dry-start `large_4wd` `L2 = FORD` at
0.038901 m in `renders/yaris_render_s1/gates_results.json`. That is the project's only
"held below threshold" claim, and it is the one number that should not be presented as a
physical hold until R2 is measured.

It also retires the framing of the question as originally posed. There was no SDF-versus-CDF
choice to discover.

## 2f. common.py

Not copied, because it did not need to be.

MEASURED: fetched the Vista original to the scratchpad and compared before touching
anything. Both files are 4965 bytes; `cmp -s` returned a match; `surface_from_cloud` is
present. The existing `renders/yaris_render_s1/common.py` is already byte-identical to
`vista:/work/11603/jcerrell0629/vista/mpm-engine/examples/common.py`.

No overwrite was performed. Stage 4 remains unblocked. The file is still third-party
`kks32/mpm-engine` code and still must not be committed.

---

## New, and it changes limitation L-5

MEASURED, by grep across both drivers.

`sim_dump.py` never passes `floor_friction` anywhere in the file. `FloodScene`'s default is
`floor_friction: float = 0.5` (`vehicle.py:343`). So the **dry-start runs ran at 0.50**.

`sim_standing.py:76` defaults `floor_friction=0.55`, passes it at `:253`, and records it at
`:355`, which is why it appears in `summary.json`.

L-5 currently says `floor_friction` was recorded for standing water and **absent** for dry
start. That was right about the record and wrong about the run. It was absent from the
record, not from the physics: the two scenarios differ by **0.50 versus 0.55**, and that is
now a quantified confound axis rather than an unknown one.

The collider topology itself is **not** confounded: `sim_standing.py:132-136` builds the
same floor plane and the same four `friction=0.0` walls as `vehicle.py:397-401`.

---

## Residual UNRESOLVED, carried forward

**R1.** Does the Yaris `.ply` populate `splat_colors`, and therefore `splat_pos`? Decides
whether Stage 4 can render the vehicle from splats at all. One command:

```bash
ssh -S ~/.ssh/cm-vista vista 'cd /work/11603/jcerrell0629/vista/mpm-engine && grep -n "splat_colors\|def load_vehicle" -A 6 src/warpmpm/vehicle.py | head -60'
```

**R2.** Does the Coulomb cap `mu * J_n` actually collapse in these runs? Needs `v_n` at the
floor contact instrumented over one rollout. Until then the dry-start `large_4wd` FORD
verdict carries a caveat and the "holds position" phrasing is not available.

**R3.** `tests/test_analytic_benchmarks.py` exists but was **not run**. This pass was
source reads only, per the dispatch. Running it needs an allocation and is Stage 2 half two.

---

## Not done, and why

No GPU work, no allocation, no `pytest`, no venv activation, no writes on Vista. Job 866601
was left alone. Nothing was installed. Nothing was committed or pushed. The only local
write is this file and the appended corrections.

---

# Stage 3 archaeology, 2026-07-25 23:55 CDT

Three premises in the Stage 3 dispatch were wrong about which script is which. All three
are corrected below at source. The net effect is good: the refinement run needs **no file
copy, no edit, and no diff**, because the correct driver is already parameterized.

## The script named in the dispatch is the DRY-START driver

MEASURED. `examples/flood_vehicle_laneR_yaris.py` (7397 bytes, local copy byte-identical to
Vista) is the **Set A dry-start** driver, not the one that produced `g64_m*`.

Proof, from the job's own stdout, `yarisford_866214.out:7-12` and `:32`:

```
+ /work/11603/jcerrell0629/vista/.venv/bin/python -u examples/flood_vehicle_laneR_yaris.py
grid 64^3 lim=9.42m  water 23532 + vehicle 8904 particles (1100.0 kg)  dt=3.03e-03 (11 substeps/frame)
PASSTHROUGH max_water_frac_in_veh_bbox=3.71 percent
final: {... 'disp_mag_m': 0.09043 ...}
```

against `g64_m1100/summary.json`: `n_water` 48367, `passthrough_max_frac` 0.10670,
`final_disp_mag_m` 0.6585370302200317, `"scenario": "standing_water_sustained_inflow"`.

The mechanism is visible at `flood_vehicle_laneR_yaris.py:59-60`:

```
scene = FloodScene(v, depth=DEPTH, velocity=VELOCITY, n_grid=N_GRID,
                   vehicle_mass=MASS_KG, device="auto")
```

It passes neither `water_eta` nor `floor_friction`, so it takes `FloodScene`'s defaults,
`water_eta = 1.0` and `floor_friction = 0.5`. `summary.json` records 0.001 and 0.55. A
script cannot have produced a run whose recorded parameters it never sets.

**Consequence.** Copying this file and changing `N_GRID` 64 to 96 would have produced a
dry-start run at grid 96, and comparing it against the standing-water `g64_m*` set would
have varied scenario and grid together. That is not a refinement study, it is limitation
L-5 again with a finer mesh.

## The hardcoded constants, for the record

SOURCE, `examples/flood_vehicle_laneR_yaris.py`:

| line | constant | value |
|---|---|---|
| 12 | `YARIS` | `/work/.../vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` |
| 13 | `OUT` | `/work/.../mpm-engine/out/flood_vehicle_laneR_yaris` |
| 15 | `DEPTH` | `0.30` |
| 16 | `VELOCITY` | `1.5` |
| **17** | **`N_GRID`** | **`64`** |
| 18 | `FRAMES` | `90` |
| 19 | `MASS_KG` | `1100.0` |
| 20 | `UP` | `"z"` |
| 21 | `RENDER_EVERY` | `2` |
| 22 | `DUMP_EVERY` | `10` |
| 74 | `hull` | `3.542739` |

`water_eta`, `floor_friction`, `bulk_modulus` and `fps` do **not** appear in this file at
all. They are engine defaults. It is a single-mass script: no mass sweep, `MASS_KG = 1100.0`
only.

## The real driver takes command-line arguments

MEASURED. The standing-water driver is `/work/11603/jcerrell0629/vista/render_s2/sim_standing.py`,
17435 bytes, byte-identical to the local `renders/yaris_render_s1/sim_standing.py`. It is
**not** in `examples/`. Its argparse block, `sim_standing.py:218-228`, includes:

```
p.add_argument("--grid", type=int, default=64)
p.add_argument("--eta", type=float, default=1.0e-3)
p.add_argument("--floor-friction", type=float, default=0.55)
```

The dispatch premise "the driver takes NO command-line arguments" is true of the dry-start
script and false of this one.

Better still, the runner `render_s2/run_s2.sh` is already parameterized by grid **and** by
output directory:

```
GRID=${1:-64}
...
$VENV -u $DRIVER --mass $MASS --label $LAB --out $BASE/g${GRID}_m${MASS} \
  --depth 0.30 --velocity 1.5 --frames 90 --grid $GRID \
  --eta 1.0e-3 --floor-friction 0.55
```

So `bash run_s2.sh 96` writes to `g96_m1100`, `g96_m1609`, `g96_m2337` and cannot collide
with the existing `g64_*`. Verified absent before staging: no `g96_m1100`, no `g48_m1100`.

This is a stronger provenance guarantee than a copied and edited file could give. The
refinement uses the identical script, identical driver and identical flags, with one
integer changed at the call site.

## 3d. Cost prediction

MEASURED baseline: `sacct -j 866266` step `.2`, `run_s2.sh`, Elapsed **00:04:57** = 297 s
for all three masses at grid 64. That is 99 s per mass.

Scaling, computed rather than assumed. Water particles scale as `n_grid^3` (fixed physical
slab, `h = dx/2`). Substeps are `ceil(rate/fps)` with `rate` dominated by
`term_acoustic = 311.625` which scales as `n_grid`: 11 at grid 64, 16 at grid 96, 8 at
grid 48.

| grid | particle factor | substep factor | cost factor | three masses |
|---|---|---|---|---|
| 96 | 3.01 to 3.38 | 16/11 = 1.455 | **4.4x to 4.9x** | **22 to 25 min** |
| 48 | 0.42 | 8/11 = 0.727 | 0.31x | 1.5 min |

The dispatch's 5.1x estimate is slightly high because vehicle particles may not scale with
the grid; the honest figure is about 4.6x.

**Prediction: about 23 minutes for the three grid-96 masses, plus 1.5 minutes for grid 48,
plus pytest.** Comfortably under the 100 minute threshold, and under a 2 hour walltime with
roughly 4x headroom. Recommendation is to submit.

## 3f. MEASURED findings, all read from `g64_m1100/summary.json`, no compute

Confirmed live against the file this session.

| quantity | value | note |
|---|---|---|
| `water_eta` | 0.001 | already corrected in Set B, the viscosity run is unnecessary |
| `term_acoustic` | 311.6252878790618 | dominates |
| `term_viscous` | 0.0002768526942394007 | 1.13 million times smaller |
| `term_advective` | 20.37839643738194 | |
| `substeps` | 11 | set by the acoustic term alone |
| `bulk_modulus` | 150000.0 Pa | |
| `sound_speed_ms` | 12.84523257866513 | |
| Mach | 1.5 / 12.845 = **0.1168** | |
| density fluctuation | ~ Ma^2 = **1.36 percent** | arithmetic only. The judgment that this is "acceptable" is NOT sourced, see the correction below |
| `determinism_identical` | true | |
| `parity_odd_columns_dropped` | 0 of 1335 | |
| `C3_oob_particle_frames` | 0 | |
| `fill_ratio` | 1.0024403113437104 | solid 3.5513844 m3 vs hull 3.542739 m3 |
| `realized_rho` | 309.7383668982256 | 3.25 percent above the 300 top of the band |
| `passthrough_max_frac` | 0.10670 standing water | vs 0.0371 dry start, the latter confirmed independently at `yarisford_866214.out:32` |

**The viscosity correction was free, and the run proved it itself.** `term_viscous` is
2.77e-4 against `term_acoustic` 311.6, so the substep count is set entirely by the acoustic
CFL. Changing `water_eta` by three orders of magnitude does not change `substeps`. No new
compute is needed to establish this.

**One correction to the 3f list as dispatched.** It reads `floor_friction = 0.55 (live
value, not the 0.4 engine default)`. 0.4 is the default of `add_sdf_collider`
(`core/solver.py:320`), which this scene never calls. The engine default that 0.55 actually
overrides is `FloodScene`'s `floor_friction: float = 0.5` at `vehicle.py:343`. See C20: dry
start ran at that 0.5.

## 3g. What `leaked` counts, now defined

SOURCE. `sim_standing.py:169-187` reimplements the engine's `_project_water`, with the
accumulator identical to `vehicle.py:452`:

```
self.leaked += int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
```

The engine docstring, `vehicle.py:432-440`, states the intent:

> Push leaked water particles back inside the floor and wall planes and kill
> their inward velocity component. A slip plane corrects grid nodes, not
> particles, so sustained pressure lets a few particles creep through it (about
> a millimetre per frame under the surge front) ... Particles hovering within a
> quarter cell of a plane are the normal boundary layer of the grid BC and are
> left alone; only deeper ones are projected back to that shell, once per frame.
> The vehicle is excluded ... self.leaked counts projected particle-frame events.

**Definition.** `leaked` is the cumulative count of **water-particle-frame projection
events**: each frame, the number of distinct water particles found more than a quarter cell
outside the floor or the side walls, which were then clipped back to that shell. Vehicle
particles are excluded. It is not a count of particles that left the domain, and it is not
a count of distinct particles: one particle corrected on forty frames contributes forty.

**Why it coexists with `C3_oob_particle_frames = 0`.** The two are consistent by
construction, not in tension. `_project_water()` runs at the top of every `step()`
(`sim_standing.py:201`) and clips offenders back inside, so by the time the instrumentation
callback samples positions, nothing is outside `[0, lim]`. `leaked` counts the corrections
that keep `oob` at zero. A large `leaked` with zero `oob` means the boundary is leaky and
the correction is working, which is exactly the designed behaviour.

**Magnitude, now that it can be stated.** `_project_water()` is called 98 times per run
(90 frames plus 8 settle frames). 108249 / 98 = about 1105 events per frame, against
`n_water = 48367`, so roughly **2.3 percent of water particles require boundary correction
per frame**. That is a defensible number to quote and it belongs in limitations, because it
is a non-conservative correction: clipping positions and zeroing inward velocity components
does not conserve momentum.

---

# Second-pass audit response, 2026-07-26

Four items from the audit, two closed exactly, one refuted, one conceded against my own text.

## CLOSED. Why sound_speed is 12.845 and not sqrt(K/rho) = 12.247

SOURCE plus MEASURED. `sim_standing.py:147`:

```
c = float(np.sqrt(1.1 * bulk_modulus / water_density))
```

`sqrt(1.1 * 150000 / 1000) = 12.84523257866513`, bit-identical to `summary.json`'s
`sound_speed_ms`. It is a 1.1 safety factor applied to the bulk modulus inside the CFL
estimate, nothing more.

**The audit's inference of "an effective density of 909 rather than 1000" is wrong.** Density
is 1000 throughout. There is no hidden density. Nothing in the parameter manifest changes.

## CLOSED, and 1D was right. The 0.4951 s round trip is printed by the driver itself

The audit states "Nothing in either file is 3.18 m long" and marks the reflection sentence as
blocking. It is in the file, and it is labelled. `sim_standing.py:277-279`:

```
print("ACOUSTIC c=%.4f m/s  vehicle_x=%.4f  downstream_wall=%.4f  round_trip=%.4f s"
      % (scene.sound_speed, 0.60 * lim, lim - 4.0 * dx,
         2.0 * (lim - 4.0 * dx - 0.60 * lim) / scene.sound_speed), flush=True)
```

`sim_standing.py:96` sets `vx, vy = 0.60 * lim, 0.50 * lim`, so `0.60 * lim` is the **vehicle's
x position**, not the inflow band. The path is vehicle to downstream wall.

MEASURED arithmetic:

| quantity | value |
|---|---|
| `lim` | 9.421742313727737 m |
| vehicle x = 0.60 lim | 5.6530453882366425 m |
| downstream wall = lim - 4dx | 8.832883419119753 m |
| **path** | **3.1798380308831105 m** |
| round trip = 2 path / c | **0.49510010992943154 s** |
| reflections in 3.0 s | **6.06** |

That reproduces 0.4951 s to ten significant figures. The 3.18 m is
`downstream_wall - vehicle_x`.

**Six reflections is the correct figure and it is the better-motivated one.** The audit's
alternative, 2.0 reflections from the full 9.42 m domain, answers a different question. The
quantity that matters is how many times the vehicle is struck by its own reflected acoustic
signal, which is a round trip from the vehicle to the downstream wall and back, not a
traverse of the whole box. The driver computes and prints exactly that. Six is also the more
conservative number for a limitation, so there is no reason to prefer two.

## REFUTED. `leaked_particle_frames` is not a recycling particle pool

The audit hypothesises, from research report 20's emitter description, that 108 249 leak
events "is exactly what a recycling inflow looks like." It is not. The grep was run and the
definition is above under 3g: `_project_water()` counts water-particle-frame events where a
particle was found more than a quarter cell outside the floor or wall planes and was clipped
back. Source at `sim_standing.py:169-187`, accumulator at `:181`, engine twin at
`vehicle.py:452`. No pool, no recycling, no emitter.

## CONCEDED, against my own text. The Mach interpretation was unsourced

The audit is right and this is a correction to my own table above, not to the dispatch. I
recorded `density fluctuation ~ Ma^2 = 1.36 percent` and annotated it "weakly compressible,
acceptable." The arithmetic is fine. The word **acceptable** is an unsourced judgment, and
the "Mach below 0.1 gives under 1 percent" convention behind it was never read at a source.
The table cell has been corrected in place.

Use the audit's replacement Limitations wording, which cites the engine's own
`docs/performance.md` for the softened bulk modulus rather than presenting it as our
discovery. Two caveats on the new citations before they reach the paper: **Isik et al. 2022
and Meringolo et al. 2017 have not been verified at source in this repo.** They came from a
Consensus search, not from a read. Per the project's standing rule they need a
title-and-DOI check before they appear in a caption, the same treatment Lazzarin got.

## Precedence note on the 2b finding

My Stage 2 conclusion that `add_plane` friction is applied to `"slip"` surfaces is not new.
`docs/VERIFIED_FACTS_LEDGER_july24.md` section A6 already established it on 2026-07-24, from
the same kernel lines. My read reproduced it independently, which is a confirmation and worth
having, but the finding belongs to that audit. One drift worth noting: A6 cites
`vehicle.py:313` for the `friction=floor_friction` call site; it is now at `vehicle.py:397`.
The physics is unchanged, the line numbers have moved, so ledger line cites should be
re-resolved before being quoted.
