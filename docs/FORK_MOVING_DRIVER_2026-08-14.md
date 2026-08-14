# Dispatch 9: the moving-vehicle driver on the warpmpm SDF path

Branch `claude/fork-moving-driver`. Date 2026-08-14. Engine: warpmpm at pinned SHA
`544c93dd02cb9c7ead89e1155a62967243244fce`.

**Every number below is tagged by how it was obtained.** `[live]` means read or run
this session. `[test]` means an assertion executed against the pinned engine.
`[cited]` means carried from a named source and not re-derived here.

**Scope, stated once and binding on everything below.** This is a DRIVEN vehicle:
the hull travels along its own long axis (+y) through still water. That is not the
AR&R / Shand stationary side-on configuration, which is what the project's FORD
verdict is defined against (CLAUDE.md L-1). **No FORD or NO-FORD verdict follows from
anything in this document**, and none is derivable from it.

---

## 1. The concrete first step PASSES

The dispatch's gate: load `rogue_g96_pd8_coarse_watertight.ply` and recover volume
4.950341 m3 and canonicalized extent 2.010112, 4.746607, 1.729385, long axis y. "If
those three numbers do not reproduce, stop and report."

`[live]` `analysis/hull_geometry_gate.py`:

| quantity | measured | published | delta |
|---|---|---|---|
| hull sha256 | `c0b778e2...06c310b2` | `c0b778e2...06c310b2` | MATCH |
| volume_m3 | 4.950341 | 4.950341 | -2.64e-07 |
| extent_x | 2.010112 | 2.010112 | -3.10e-07 |
| extent_y | 4.746607 | 4.746607 | +3.04e-07 |
| extent_z | 1.729385 | 1.729385 | +3.91e-07 |
| long axis | y | y | - |
| verts / faces | 36074 / 72520 | 36074 / 72520 | exact |

Deltas sit inside the 6-decimal precision the published values are quoted to.

**Reproduced on two independent stacks** `[live]`: Mac (numpy 2.4.6, trimesh 5.0.0,
Python 3.11.15) and LS6 (numpy 2.0.2, trimesh 4.12.2, Python 3.9.7). Identical to 6 dp
on both. Different numpy major, different trimesh major, different Python minor.

The gate runs the **gated geometry code**, not a reimplementation: `analysis/vetted_loader.py`
parses `vehicle_live.py` (sha256 `5a5bbbab...`) and the as-ran `sim_standing.py`
(sha256 `5215c38b...`), drops only their `warpmpm` module-scope imports from the AST,
and checks both digests before executing. No function body is edited. This is the same
technique `simulation/validate_coupling_force_ladder.py` already uses on scalar
constants, applied to functions.

### 1a. A seed control, because one of these numbers could have been seed-dependent

`load_vehicle` draws **60,000 random surface samples** (`vehicle_live.py:234`) and
derives its re-centring shift from them (`:251`). Two different quantities are easy to
conflate here, so they were measured separately across 4 seeds `[live]`:

| quantity | source | spread over seeds |
|---|---|---|
| canonicalized extent | mesh vertices, via `canonicalize` | **0.000e+00 m**, bitwise identical |
| volume | mesh | 8.88e-16 m3, 1 ULP |
| `VehicleBody.extent` as returned by `load_vehicle` | the 60k samples | **3.826e-03 m** |

So the gate is correctly defined on the **canonicalized** extent. The raw loader
extent would wobble by ~3.8 mm and could not be quoted to 6 dp at all. I initially
inferred the published extents must be seed-dependent and that was **wrong**;
`canonicalize` recomputes from the mesh, which is exactly why it exists.

---

## 2. The three traps, now proven by execution rather than inspection

`tests/test_sdf_wrench_contract.py`, **3/3 PASS** `[test]` against the pinned engine.
Each test fails loudly if the trap is ever fixed upstream, which is what you want.

| trap | source `[live]` | executed result `[test]` |
|---|---|---|
| **T1 wrench dt** | `core/solver.py:361` returns `{"force": f/dt, "torque": t/dt}` | `force(dt_sub)/force(tick)` = **8.000000000000** for an 8-substep tick, max err **0.000e+00**. Passing `dt_sub` inflates force by exactly n. |
| **T2 accumulator** | zeroing exists only as explicit caller APIs: `reset_cup_wrench:295`, `reset_sdf_force:348`, `reset_cdf_wrench` via `:398`, `reset_tool_force:415` | impulse **8.39e-03** after 1 tick, **1.90e-02** after 2 with no reset, **1.14e-02** after an explicit reset. A naive read is the run-to-date total. |
| **T3 quaternion** | `add_sdf_collider` stores `wp.quat(q[0..3])` (xyzw); `add_cup:256` documents wxyz, defaults `(1,0,0,0)` | the **same** 4-tuple rotates a probe to `[0,1,0]` on the SDF path and `[-1,0,0]` via `quat_to_mat`. Divergence **1.0000**, and **neither errors**. |

Traps 4 and 5 are handled structurally rather than tested, because both are about
configurations this driver refuses to enter:

- **T4 COM offset** is not engaged: arms (a) and (b) prescribe the pose and never
  integrate free rotation. `--arm` refuses `c`. `[live]` The `RigidBody6DOF`
  `NotImplementedError` cited by the dispatch lives in `simulation/rigid6dof.py`,
  which is **unpushed on Vista** (Dispatch 8.3 owns recovering it), so that specific
  line was NOT verified here and is marked `[cited]`, unverified.
- **T5 periodic_x** is never enabled. `[live]` `core/solver.py:90-92` states it is
  "Incompatible with CDF colliders and rigid bodies"; `add_cdf_collider` raises at
  `:379-380`; `add_sdf_collider` (`:324-337`) has **no equivalent guard**, confirmed by
  reading the full function body.

### 2a. Trap 2 is broader than the dispatch states

The dispatch says the engine never zeroes `param.force` **on the SDF path**. `[live]`
That is true, and the stronger statement is also true: a repo-wide read of `core/` and
`kernels/` finds **no automatic per-step zeroing of any wrench accumulator**. All four
accessor families (cup, sdf, cdf, tool) require an explicit caller-side reset. A reader
who believes the hazard is SDF-specific will get the same silent run-to-date total from
the cup or tool accessors.

### 2b. Two engine guards the dispatch does not mention, both helpful

`[live]` `add_sdf_collider` carries a **containment guard** that raises `ValueError`
when the contact band reaches the SDF grid's boundary margin (near-surface space
outside the stored grid would get no constraint), and a **tunneling guard** that warns
once when the collider surface sweeps more than the contact band per substep. Neither
is silent. In the runs configured here the sweep is 0.12 mm against a 163 mm band, so
the guard is far from tripping.

`[live]` The RB-3 band amendment reproduces exactly: `kernels/mpm_solver_warp.py:2626-2627`
sets `band = float(self.mpm_model.dx)` when `band is None`, flat and not feature-scaled,
while the CDF path at `:2833-2834` uses `min(built_band, 2.0*dx)`.

---

## 3. Arm (b), and why it is the result that survives

The dispatch records the engine limitation that bounds this whole track: the net force
cannot be **decomposed** into hydrodynamic, contact and gravitational parts. (The
correct nuance is kept: "no force is ever formed" is false, `_apply_rigid_restitution`
is defined at `mpm_solver_warp.py:887` and called at `:1362` `[live]`.)

**The traction budget does not need the decomposition.** It needs only the net normal
load:

```
F_N     = W - Fz_up                 one number, no decomposition
F_avail = mu * F_N                  available traction
F_dem   = F_drive + mu_RO * F_N     drag along travel plus rolling resistance
```

That splits the deliverable cleanly, and the split is the point:

| side | how obtained | trustworthy at this resolution? |
|---|---|---|
| available traction `F_avail(d)` | **analytic**, no solver | yes |
| flotation depth | **analytic** | yes |
| drag demand | **solver-measured** | no, see section 4 |

### 3a. The analytic result, computable today without a GPU

`[live]` `analysis/traction_budget.py`, Rogue hull, mass 1609 kg (AR&R reference mass;
NHTSA curb weight for the 2020 Rogue AWD is 1610 kg, a 0.06 percent difference).
W = 15784.3 N, hull volume 4.950341 m3, rho_vehicle 325.0 kg/m3.

| depth (m) | V_sub (m3) | B (N) | F_N (N) | A_front (m2) | F_F at mu=0.30 (N) | drag band, C_D 1.22-6.82 (N) |
|---|---|---|---|---|---|---|
| 0.10 | 0.0067 | 65.9 | 15718.4 | 0.0356 | 4715.5 | 48.9 - 273.3 |
| 0.20 | 0.1131 | 1109.4 | 14674.8 | 0.1713 | 4402.5 | 235.0 - 1313.9 |
| 0.30 | 0.5034 | 4938.3 | 10846.0 | 0.3213 | 3253.8 | 440.9 - 2464.8 |
| 0.40 | 0.9179 | 9004.8 | 6779.5 | 0.4700 | 2033.8 | 645.1 - 3606.1 |
| 0.50 | 1.4442 | 14167.5 | 1616.8 | 0.6656 | 485.0 | 913.6 - 5107.0 |
| 0.55 | 1.7296 | 16967.0 | **0.0** | 0.7144 | **0.0** | 980.5 - 5481.0 |

**Flotation depth 0.55 m**, where available traction reaches zero.

**Crossing depths**, where demand first exceeds available traction at 1.5 m/s `[live]`:

| mu | C_D 1.22 | C_D 6.82 |
|---|---|---|
| 0.30 parked baseline | 0.50 m | 0.30 m |
| 0.52 measured parallel | 0.50 m | 0.40 m |
| 0.75 tyre wet | 0.55 m | 0.45 m |

So the band is **0.30 to 0.50 m**, and it **brackets Al-Qadami 2022's measured 0.38 m**
critical depth for a vehicle moving perpendicular to flow `[cited]`. That is a contact
point with the one moving-vehicle measurement in the literature, not agreement: the
band is wide precisely because C_D 1.22-6.82 is a joint envelope over three vehicles
and all flow directions (Hu et al. 2023), so its midpoint is not an estimate for this
vehicle at this orientation and is never quoted as one.

### 3b. Cross-check, and what it is not

`[live]` V_sub(0.30 m) = 0.5034 m3 and B = 4938.3 N here, against the exploratory
document's 0.504603 m3 and 4950.2 N: **0.24 percent apart**. This is **not independent
corroboration**: both use the same `solidify_watertight` fill. What is independent is
the waterline integration, which was written separately. Recorded as one source with
two integrations, per the project's claim-discipline rule.

`[live]` Fill convergence against mesh volume, which is why the pitch was changed from
the loader default: **-0.22 percent at 0.05 m**, **+0.02 percent at 0.025 m**. The
loader default for this hull is extent/32 = **0.1483 m**, which quantises the waterline
into ~0.15 m steps and made V_sub(d) a staircase, constant across three consecutive
0.05 m rows. That was a defect in the first version of this diagnostic and it was
found by reading the output rather than by assuming it was fine.

### 3c. Comparison with Smith 2019, stated carefully

`[cited]` Smith, Modra and Felder 2019 measure Yaris (1045 kg) rear-axle traction
4.5-4.7 kN at 0 m depth falling to 0 kN at ~0.6 m, and Nissan Patrol (2478 kg)
9.3-9.6 kN falling to 0 at ~0.95 m.

The comparable feature is the **shape**: traction falls monotonically to zero at
flotation. The magnitudes are **not** directly comparable, for three reasons that must
travel with any use of this: Smith measures a **rear axle**, this is whole-vehicle; it
is a **stationary sideways winch pull-test**, which bounds available traction and does
not validate propulsion; and our hull is a **fully watertight solid**, which inflates
displaced volume relative to a real vehicle, so 0.55 m is not the flotation depth of a
real Rogue. CLAUDE.md A-4 already records that watertightness assumptions materially
shift flotation depth, and register E2 records that watertightness does not even
propagate into the sim (the mesh is resampled to 60,000 surface points before
solidifying).

---

## 4. What the GPU run can and cannot settle

Job **3364526** submitted to LS6 `gpu-a100` as **BATCH**, 3 resolutions
(n_grid 64, 96, 128) at depth 0.30 m and 1.5 m/s, with the trap tests re-run on the
GPU device and the geometry gate re-run in-job.

**The binding constraint is already known and is not fixable by this dispatch.**
`[cited]` from the 2026-08-11 exploratory work, `[live]`-consistent with the grid
arithmetic here: at the canonical 0.30 m depth on a domain sized from this hull's own
extent, the water column is 1.84 cells deep at n_grid 64 and 3.68 at n_grid 128,
against the **18 cells** at which the C1-SDF buoyancy harness established its 7.3-7.7
percent agreement. The scene's own at-rest gate (vertical reaction against
`rho*g*V_submerged`) **failed** in that work, and the driver re-runs that gate every
time and marks the run's outputs qualitative if it fails again.

Therefore the run is designed to answer a **resolution question**, not to produce a
force number: does the demand/available ratio move systematically with refinement? Both
answers are reportable. A converged ratio would be a genuine result; a drifting one
confirms that the drag demand needs the resolution the scene cannot currently reach.

`[live]` The smoke test on CPU (n_grid 24, deliberately absurd) exercised every code
path end to end and the at-rest gate correctly returned **FAIL at -100.00 percent**,
which is the behaviour required: with 0.69 cells of water depth there is nothing to
measure and the code says so rather than reporting a number.

---

## 5. Corrections found while executing this dispatch

These are recorded here because they bear on other dispatches' scopes. **I have not
edited any file I do not own.**

### 5a. Register D8c: both sides of the floor-plane dispute were right, about different files

`[live]` There are two `sim_standing.py` in this worktree:

| path | sha256 | lines | floor plane |
|---|---|---|---|
| `analysis/render_v1/as_ran_local_copies/sim_standing.py` | `5215c38b...` | **389** | **`:132-133`** |
| `renders/yaris_render_s1/sim_standing.py` | `4696c3b2...` | **564** | **`:210-211`** |

The dispatch and register D8c describe the gated driver as "sha256 5215c38b, 389
lines, and :132-133 IS its floor plane", and a 2026-08-13 change that repointed the
citation to `:210-211` was refused on that evidence. Both line numbers are **correct**,
for different files. The 175-line difference is the live copy having evolved.

The live copy is the one that is **tracked** (committed in `00b735c`) and is the path
CLAUDE.md item 3 names. So a reader who follows CLAUDE.md item 3 to
`renders/yaris_render_s1/sim_standing.py` and checks `:132-137` will find a
point-in-triangle routine, not the floor plane, and will reasonably conclude the
citation is broken.

**Recommendation for Dispatch 4 (register owner), not applied here:** the citation
needs the **file digest**, not just a line number. Suggested form: "floor plane at
`:132-133` of the as-ran driver, sha256 `5215c38b`; the same statement in the evolved
tracked copy `4696c3b2` is at `:210-211`."

### 5b. The "do not use anything in `vehicle_meshes/candidates/`" rule is now too broad

`[live]` That directory holds four `.ply`. The two condemned by the original
measurement are `rogue_candidate_euler-32.ply` and `silverado_candidate_euler-82.ply`
(selected on `euler_number`, 47.5 and 31.1 percent below converged volume). But
`candidates/rogue_g96_pd8_coarse_watertight.ply` and its Silverado sibling were added
later (2026-08-08) and are **byte-identical** to the canonical pool hulls: sha256
`c0b778e2...06c310b2`, matching the digest this dispatch gates on.

A reader following "do not use anything in `candidates/`" literally would refuse the
correct hull. The rule should name the two condemned files, not the directory.

### 5c. LS6 cannot run this dispatch from its own warpmpm, and there are two engine SHAs on `/work`

`[live]`, and this is operational knowledge worth keeping:

- LS6's local warpmpm copy (`$SCRATCH/instantsplat_probe_2026-08-13/warpmpm`) has **no
  `add_sdf_collider` and no `geometry/`**, so it cannot run the SDF path at all. It is
  also not a git repo, so it carries no SHA provenance.
- The pinned engine lives on Vista's `$WORK`, and **LS6 can read it directly** because
  Stockyard `/work` is shared across machines. That is what makes "LS6 batch on the
  pinned SHA" possible without copying anything.
- **There are two engine checkouts under Vista's `$WORK` at different SHAs:**
  `/work/11603/jcerrell0629/vista/can-it-ford/mpm-engine` is at the pinned
  `544c93dd...`, and `/work/11603/jcerrell0629/vista/mpm-engine` is at `627367ec...`
  with an untracked `test_meshes/`. Pointing `PYTHONPATH` at the wrong one silently
  changes the engine under a run that will otherwise look normal. Always confirm with
  `git -C <path> rev-parse HEAD` before a run.
- The LS6 environment lacks `scipy`, which the engine's SDF builder uses for its
  `cKDTree` nearest-face path; without it the fallback needs 3.3 GiB for the exact
  point-triangle distance and dies. Installed to `--target` inside this dispatch's own
  `$SCRATCH` directory rather than into any shared environment.

---

## 6. Caveats that travel with every number in this document

1. **cannot_decompose.** The wrench is a net reaction. Drag, buoyancy, lift and contact
   are not separable from it. Arm (b) is built to avoid needing them separated.
2. **no_rigid_pressure.** `[live]` `mpm_utils.py:1100` initialises rigid-particle
   stress to a zero `mat33`, `:1104` excludes material 8 from the SVD, and no `mat == 8`
   branch anywhere in `:1105-1147` ever assigns one (the branches are 0/5, 1, 2, 6, 10,
   12, 9/13, 11). On the **free-rigid** path a rigid hull therefore exerts no pressure
   on the water. **This scene uses the SDF-collider path**, which is a grid boundary
   condition and does push water, and which **does** have a force accumulator. The two
   paths must not be conflated in either direction, which is the RB-3 scope correction.
3. **at_rest_gate.** If the at-rest reaction does not agree with `rho*g*V_submerged`,
   no force number from the scene is quotable. Enforced in code, recorded per run.
4. **configuration.** Driven along its own long axis. Not the AR&R stationary side-on
   case. No FORD verdict follows.
5. **L = 0** in the analytic budget, so `F_F` is an upper bound on available traction.
6. **Not physics-skeptic reviewed, and the reason is not that the claim is weak.** The
   operating protocol asks for the `physics-skeptic` subagent before finalising any
   percentage, force, verdict count or distance. It was **not run**, because this
   session's operating instructions restrict spawning subagents to cases the user has
   asked for. Per the protocol's own rule, the affected claims are therefore marked
   **UNREVIEWED** rather than presented as reviewed: specifically the section 3a
   traction table, the 0.30-0.50 m crossing band, the 0.55 m flotation depth, and the
   0.24 percent cross-check in 3b. The review is a real outstanding step, not a
   formality, and the numbers are reproducible from the committed scripts.

---

## 7. Status against the dispatch's definition of done

| requirement | status |
|---|---|
| concrete first step reproduces | **DONE**, PASS on two stacks |
| wrench normalisation verified by explicit test | **DONE**, T1, exact ratio 8 |
| accumulator zeroing verified by explicit test | **DONE**, T2 |
| quaternion order verified by explicit test | **DONE**, T3 |
| arm (a) implemented | **DONE**, runs end to end |
| arm (b) implemented, per-step traction margin vs `F_F = mu*(W-B-L)` | **DONE** in code; analytic side **measured**; solver-measured demand pending the queue |
| every force number carries both caveats | **DONE**, in the JSON records themselves, not only in prose |
| arms running and classified | **PENDING** job 3364526, queued behind D5 on a fully allocated partition |
| branch pushed with PUSH_OK=1, confirmed by ls-remote | **NOT DONE**, awaiting explicit approval; the dispatch prompt forbids pushing without asking |
