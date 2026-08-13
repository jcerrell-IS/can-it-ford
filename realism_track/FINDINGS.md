# Realism track findings, 2026-08-12

LS6 node c301-003 (A100), job 3360948. Exploratory track, separate from the
canonical warpmpm 17-run pipeline at `renders/yaris_render_s1/`, which was not
touched.

## Verdict up front

**Path (a), the warpmpm SDF collider, is the validated path.** It is the only
one of the two with a measured coupling force, its force agrees with analytic
buoyancy to **-7.67% (g64) and +7.28% (g96)**, and the "a fixed collider cannot
slide" objection is dissolved: `set_sdf_pose` already exists, so the collider can
be re-posed each substep from a free-body integration.

Path (b), Genesis LegacyCoupler, was not pursued. It is strictly more work for a
less-validated force: no coupling-force validation exists anywhere in the Genesis
repo, so it would have to be built from scratch, while path (a) already has one.

**No rendered clips are delivered, and no claim of visual realism is made.** The
reason is stated in "Not delivered" below. The force number above is a real
measurement; the visuals are not started.

## Mandatory reading, status

Two of the four required documents do not exist. Verified by name search across
`/home1`, `/work` (ls6, vista, frontera, stampede3) and `/scratch`:

| Document | Status |
|---|---|
| `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` | **MISSING everywhere** |
| `CLAUDE.md` | read in full |
| `docs/COUPLING_VALIDATION_J1_2026-08-07.md` | **MISSING**; only `..._J1_VISTA_2026-08-07.md` exists, read |
| `docs/MULTIGEOM_VALIDATION_2026-08-11.md` | **MISSING everywhere** |

This has a direct consequence for the brief's instruction "do not use 8% or 1.6%,
both are wrong, check the register". The register could not be checked. Instead
the figure was re-derived from the primary run manifests, which is a stronger
source than the register would have been. **The brief's 7.3-7.7% is confirmed,
and its warning about 1.6% is confirmed as well**: 1.62% is
`err_first3_vs_analytic_pct`, a first-three-frame transient measure, not the
steady-state figure. Details below.

The J1 Vista doc also disagrees with the brief in a way worth flagging: it reports
`err_F_pct` of -90.99, -122.33 and -237.34 for rho_box 700/800/1000. Those are
free-rigid numbers, not fixed-SDF numbers, so they do not contradict the 7.3-7.7%
result, but anyone reading that doc alone would conclude the coupling is broken by
two orders of magnitude. The two documents describe different code paths.

`CLAUDE.md` requires reading `docs/VERIFIED_FACTS_LEDGER_july24.md` before
asserting any parameter as fact, and states Section F records **one** usable
vehicle mesh, not three. The brief's flood-fill density corrections span three
vehicles (Yaris, Rogue, Silverado). Those three density values were **not
verified** here and are not used anywhere in this report.

## Measured force accuracy against analytic buoyancy

Reproduce with `python3 realism_track/verify_coupling_accuracy.py`. Source is the
29 run manifests under `data/coupling_validation*/`; 69 JSON documents parsed
including provenance sidecars.

Gated configuration, variant `C1SDF_fixed_collider`:

| run | collider | steady vs analytic | first3 vs analytic |
|---|---|---|---|
| `c1sdf_sdf_g64` | sdf | **-7.67%** | 1.62% |
| `c1sdf_sdf_g96` | sdf | **+7.28%** | 6.12% |
| `c1sdf_box_g64` | box | -37.91% | -46.63% |
| `c1sdf_box_g96` | box | -21.28% | -23.21% |

Free-rigid material-8 path, the path the 17 canonical runs use:

| run | err_F_pct | headline vs ideal |
|---|---|---|
| `c1_g64` / `c1_rigid_g64` | -48.81 / -48.79 | -122.03 / -121.97 |
| `c1_g96` / `c1_rigid_g96` | -130.35 / -130.48 | -325.87 / -326.21 |
| `c3_fixed2_g64` | -203.29 | n/a |
| `894642_nosubmersion` g64 / g96 | -192.45 / -345.05 | -481.13 / -862.63 |
| `preclamp_894628` g64 / g96 | +168.48 / -290.54 | +421.19 / -726.36 |

The ordering is unambiguous: SDF collider (7.3-7.7%) beats box collider (21-38%)
beats free-rigid (49-345%). This is direct quantitative confirmation of the brief's
core problem statement, that the material-8 free-rigid path exchanges no real
force.

### Why the smoke runs are excluded

Four further SDF/box runs exist under `coupling_validation/smoke/` with errors of
-130.76% (sdf g64), -54.33% (sdf g96), -146.51% and -26.90% (box). They are
excluded from the headline, and the reason is not that they are inconvenient. At
**identical geometry** (a full key-by-key diff shows zero geometry differences
against `c1sdf_sdf_g64`), the smoke run's steady vertical force is
**-9628.7 N, negative**, against the gated run's **+28898.4 N**. A submerged
buoyant body cannot experience net downward hydrostatic force, and
`a_free_body_implied` is -14.84 m/s2, below free fall. The smoke runs also sit at
a different settle state (`submersion_margin_dx` 4.18 vs 2.75,
`surface_after_settle` 2.97 vs 2.76) and carry 8x the lateral asymmetry
(`F_lateral_over_Fz` 0.320 vs 0.040). They are unsettled sanity checks with a
sign-inverted force, not validation runs.

Reporting a single pooled SDF range of 7.28-130.76% would therefore be misleading.
The honest statement is: **the gated SDF configuration is accurate to 7.3-7.7%,
and an unsettled SDF configuration at the same geometry can invert the force sign
entirely.** The settle gate is load-bearing, not decorative.

## The moving-SDF question, answered

The brief asks whether warpmpm's SDF collider can be made to move. It can, and the
API for it already exists in `mpm-engine/src/warpmpm/core/solver.py`:

- `add_sdf_collider` at :324
- `set_sdf_pose` at :339, accepting `center`, `quat`, `velocity`, `omega`
- `reset_sdf_force` at :348
- `sdf_wrench` at :354, returning force and torque
- equivalents for other collider types: `cdf_wrench` :401, `tool_force` :420

So the loop is: `reset_sdf_force` -> `step(dt)` -> `sdf_wrench` -> integrate
Newton-Euler in Python -> `set_sdf_pose`. That yields the validated SDF force
**and** freedom of motion, which is exactly the combination the brief was looking
for, and it means the fixed-collider objection was an artifact of how the collider
was being driven, not a limitation of the engine.

**This is already implemented and must not be duplicated.** The parallel Vista
session built it during this same window: `simulation/coupling_force/` containing
`rigid_body.py`, `rung_b_coupled.py`, `inflow_outflow.py`, `test_rigid_body.py`,
`test_inflow_outflow.py` and a README, with `test_rigid_body.py` reporting 14
analytic checks passing (free fall, neutral-buoyancy zero drift, Archimedes SHM
period to 2%, inertia against the analytic solid-box tensor, torque-free
precession conserving angular momentum and energy). Those validate the
**integrator**, not the fluid coupling. The coupler has never been run against a
live solver.

Also relevant, from the Vista side: the briefing premise that "no
force/impulse/torque accumulator exists anywhere in this engine" is false. The
accumulators exist for SDF, box, cup and CDF colliders. What is missing is a force
path for a **free** body, which is precisely what re-posing an SDF collider
supplies.

## Not delivered, and why

The brief asks for 2-3 rendered clips and photoreal water. None are delivered.
This is a hard toolchain limit on this node, not a shortfall of effort. Measured
on LS6 login1 and c301-003, 2026-08-12:

| Needed | Status on LS6 |
|---|---|
| `splashsurf` (free-surface meshing) | absent |
| `blender`, `mitsuba`, `pvpython` | absent |
| `ffmpeg` (clip encode) | absent |
| `pyvista`, `trimesh`, `skimage`, `open3d` | not importable |
| `warpmpm`, `genesis`, `taichi` | not importable |

With no mesher, no renderer, no encoder and no solver on this node, the visual
half of the task cannot begin here, and the coupling-force experiments cannot be
run here either. Per the brief's own instruction not to claim visual realism
without a force-accuracy number backing it, the inverse also holds and is
respected here: a force-accuracy number exists, the visuals do not, and nothing in
this report claims otherwise.

The `drainA` gsplat reconstruction the brief cites does exist and is intact:
`/work/11603/jcerrell0629/ls6/gsplat_results_backup/drainA/ply/point_cloud_29999_merged_3ranks.ply`,
270,857,262 bytes, dated 2026-08-07.

Separately, the multigeom renders the brief's predecessor treated as missing now
exist, produced by Vista during this window:
`renders/multigeom_2026-08-12_render/g64_rogue/multigeom_rogue_2026-08-12.mp4`
(5,468,214 B) and `.../g64_silverado/multigeom_silverado_2026-08-12.mp4`
(4,496,217 B). They are outputs of the kinematic path, so they predate any real
coupling force and should not be presented as physically coupled results.

## Next steps, in dependency order

1. **Run the rung-b coupled test on GH200.** `simulation/coupling_force/rung_b_coupled.py`
   has never been exercised against a live solver, and it is the single blocker
   for everything downstream: physical correctness, visual realism, and any future
   surrogate training corpus. Budgeted at about 1 GPU-hour. Cannot run on LS6.
2. **Re-measure force accuracy with the collider moving.** The 7.3-7.7% figure is
   for a *fixed* collider. Re-posing it each substep changes the coupling, so the
   number must be re-established, not inherited. Target the same 5-10% band.
3. **Sound speed at the physical value.** Run c = 1480.98 m/s directly rather than
   interpolating, per the brief and job 895378. Note the existing runs sit at
   bulk 1.5e5 Pa, i.e. c = 12.845 m/s, two orders of magnitude low, and that
   `sim_enhanced.py` already exposes `--bulk-modulus` as a parameter for exactly
   this sweep.
4. **Meshing and rendering.** Needs a node with splashsurf plus Blender or
   Mitsuba, and ffmpeg. Neither LS6 login nor this A100 node has them. Decide
   whether to install into `$WORK` or move this stage to a machine that has them.
5. **Density correction.** Deferred until the three flood-fill values can be
   traced to a primary source, since the register that would carry them is
   missing and `CLAUDE.md` records one usable mesh rather than three.

## Unresolved conflicts worth a decision

- `CLAUDE.md` states physical mu is 0.3-0.55 "per Azhar et al. 2023", while
  `vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md`
  records that this project's own forensic audit found the specific Azhar
  attribution **unverified** against that paper's full text, and gives
  mu_wet ~= 0.3 as the primary value with 0.25-0.75 as the sensitivity range.
  Two project-canonical files disagree about the provenance of the same number.
- The brief's three-vehicle density corrections versus `CLAUDE.md` Section F's
  "one usable mesh, not three".

## Attempt to run rung (b) on GH200, 2026-08-12, BLOCKED

The coupled run was requested and could not be executed from this session.

**Blocker: Vista is unreachable from LS6 without MFA.** `ssh vista.tacc.utexas.edu`
returns `Permission denied (keyboard-interactive)`. TACC requires an interactive
multi-factor token, which a non-interactive session cannot supply. GH200 is a
Vista resource; LS6 has A100s and cannot import `warpmpm` at all. So there is no
path from here to a GH200 run. The job must be submitted from a Vista session by
the user.

Rather than leave that as a dead end, the run was made submit-ready and the two
follow-up items were costed.

### Readiness audit of rung_b_coupled.py, passed

The driver has never touched a live solver, so it was checked statically before
anyone spends GPU time on it:

- imports resolve: `simulation/coupling_force/__init__.py` exports `RigidBodyState`,
  `ForceCoupledBody`, `CouplingConfig` as the driver expects
- every symbol it pulls from `validate_coupling_force` exists: `BoxTank`,
  `box_bottom_cells_for_submersion`, `DX_CANON`, `RHO_W`, `G`, `LIM`
- both `rung_b_coupled.py` and `rigid_body.py` byte-compile clean
- the only file write is `Path(a.out).write_text(...)`, so it cannot clobber
  anything outside the path passed to `--out`

Nothing static blocks the run. What remains untested is the physics, which is the
whole point of running it.

### Experimental-design correction for item 1

`rung_b_coupled.py` defaults to `--n-grid 32`. The fixed-collider figures this run
must be compared against (-7.67% and +7.28%) were measured at **g64 and g96**. A
g32 coupled run would not be a like-for-like comparison and would confound the
moving-collider effect with a resolution change. `realism_track/run_rung_b_gh200.sbatch`
therefore runs g64 and g96, with `--settle 900` to match the settle depth of the
gated C1SDF runs rather than the driver's default 400.

Submit from a Vista session:

    cd /work/11603/jcerrell0629/vista/can-it-ford
    sbatch realism_track/run_rung_b_gh200.sbatch

Partition is `gh`, matching all 12 of the project's existing sbatch scripts;
`gh-dev` is the interactive idev queue Vista used for job 906873, not the batch
queue.

### Item 2, sound speed: the driver has no knob, and the cost is ~110x

Two findings, both blocking a naive attempt.

**First, `rung_b_coupled.py` exposes no bulk-modulus or sound-speed argument at
all** (zero matches for `bulk`, `BULK`, or `sound_speed`). It inherits
`BULK = 1.5e5` from `validate_coupling_force.py`. So `c = 1480.98` is not
reachable through this driver as written. `sim_enhanced.py` is the file that
exposes `--bulk-modulus`, but it is a *standing-flood* driver, not this rung. One
of the two has to be extended; that is a code change, not a run.

**Second, the physical sound speed costs about 110x more compute.** Derived from
the solver's own CFL rule, `substeps_and_dt` at `validate_coupling_force.py:49-56`,
where `rate = max(c/(0.28*dx), 6*eta/(rho*dx^2), 1e-6/(0.5*dx))` and
`substeps = ceil(rate/fps)`:

| n_grid | dx (m) | substeps at bulk 1.5e5 | substeps at c=1480.98 | cost |
|---|---|---|---|---|
| 32 | 0.29443 | 6 | 599 | 100x |
| 48 | 0.19629 | 8 | 899 | 112x |
| 64 | 0.14721 | 11 | 1198 | 109x |
| 96 | 0.09814 | 16 | 1797 | 112x |
| 128 | 0.07361 | 21 | 2396 | 114x |

Required bulk for c = 1480.98 m/s is **1.9939e9 Pa** (from
`c = sqrt(GAMMA*bulk/rho)` with GAMMA=1.1, rho=1000), a **13,293x** increase over
the current 1.5e5. Sanity check: real water's bulk modulus is about 2.2e9 Pa, same
order, so the target value is physically right.

The consequence is the part worth deciding on before submitting anything: **a run
that costs 1 GPU-hour at the current bulk costs roughly 100-115 GPU-hours at the
physical sound speed.** Against a remaining Vista budget of about 670 SU expiring
2026-09-30, that is a large fraction of what is left, and it should not be spent at
g96 on a first attempt. The SU-per-node-hour conversion on Vista GH200 was not
verified from this session and should be checked with `taccinfo` before committing.

Recommended sequence, cheapest informative step first:

1. Submit the g64/g96 coupled run at the current bulk. This answers item 1, whether
   the moving collider preserves the 5-10% force accuracy, for about 1 GPU-hour.
2. Only then, add a `--bulk-modulus` argument to `rung_b_coupled.py` and run the
   sound-speed point at **g32 or g48**, where the 100-112x multiplier lands on the
   cheapest grid. Note job 895378's finding that the response is not monotone in
   grid resolution, so a g32 result cannot be extrapolated to g96; it establishes
   feasibility and rough magnitude only.
3. Treat a full g96 run at c=1480.98 as a separate budget decision, not a
   follow-on.

## Item 1 ANSWERED: the moving collider does NOT preserve 7.3-7.7%

Executed on LS6, not Vista. Vista stayed unreachable (MFA), so the run was moved
to the A100, which is where the brief's own resource guidance puts warpmpm
SDF-collider work anyway. Zero Vista SU spent. `warpmpm` was installed into
`/scratch/11603/jcerrell0629/warpmpm_ls6_env` (warp-lang + torch + numpy, 6.7 GB,
24 minutes on BeeGFS); LS6 is x86_64, which sidesteps the aarch64 failure class
entirely.

Jobs: **3361315** (baseline, g64 + g96) and **3361371** (relax sweep), node
c301-004, 3x A100-PCIE-40GB, driver 570.195.03. Results in
`realism_track/rung_b_ls6_3361315/` and `realism_track/rung_b_relax_3361371/`.

The 14 analytic integrator tests passed first, on GPU, exactly as the Vista session
reported on CPU (SHM period 1.73731 s against theory 1.7373 s, |L| drift 7.6e-5,
E drift 1.0e-4, R orthonormal to 1.1e-16).

**The coupling force is real.** `nonzero_wrench=true`, `clamped_steps=0` in every
run, 445,184 water particles at g64 and 1,502,496 at g96. The material-8 objection
does not apply to this path: force genuinely transfers.

**But the accuracy does not carry over, and gets worse with refinement:**

| grid | relax | moving-collider err | fixed-collider err | added_mass_ratio | net_dz | a_first3 | a_ideal |
|---|---|---|---|---|---|---|---|
| g64 | 1.00 | **-18.86%** | -7.67% | 0.864 | -0.124 m | -2.19 | -1.330 |
| g64 | 0.50 | -19.94% | -7.67% | 0.864 | -0.127 m | -3.04 | -1.330 |
| g64 | 0.25 | -23.12% | -7.67% | 0.864 | -0.131 m | -5.20 | -1.330 |
| g96 | 1.00 | **+115.03%** | +7.28% | 0.930 | +0.401 m | +39.85 | -0.689 |
| g96 | 0.50 | +119.91% | +7.28% | 0.930 | +0.396 m | +34.66 | -0.685 |
| g96 | 0.25 | +132.28% | +7.28% | 0.930 | +0.389 m | +20.48 | -0.687 |

Error is `(Fz_measured_median - F_buoy_analytic) / F_buoy_analytic`, against the
analytic reference the driver builds from its own measured settled surface.

Three conclusions, in order of importance.

**1. The brief's instruction not to inherit 7.3-7.7% was correct.** Freeing the
collider degrades g64 from -7.67% to -18.86%, a factor of 2.5, and destroys g96,
from +7.28% to +115.03%. Any realism claim resting on the fixed-collider number
would have been wrong by an order of magnitude at g96.

**2. Under-relaxation does not fix it, so this is not simple partitioned-explicit
instability.** Both runs tripped the coupler's own guard
(`added_mass_ratio` 0.864 and 0.930, against its stated 0.5 limit), which made
scheme instability the obvious suspect. It is refuted: relax 1.0 -> 0.5 -> 0.25
made the force error monotonically **worse** (-18.86 -> -19.94 -> -23.12 at g64;
+115 -> +120 -> +132 at g96). `added_mass_ratio` is unchanged by relax because it
is a property of the geometry and density ratio, not of the scheme parameter.
Relaxation damps the body's motion response (g96 `a_first3` falls 39.85 -> 20.48)
without improving the measured wrench. The error is systematic, not oscillatory
divergence.

**3. The g96 behaviour is unphysical, and divergence under refinement points at a
bug rather than discretisation error.** A box at rho_box=600 in water of 1000 must
sink gently: `a_ideal` = -0.689 m/s2. Instead it accelerates **upward** at
+39.85 m/s2, four times gravity, and rises 0.40 m. Refining g64 -> g96 makes the
error worse (-19% -> +115%) and flips its sign. Convergent schemes do not behave
this way. Something in the re-pose loop, most plausibly double-counting between
`set_sdf_pose` and the grid velocity update, or a sign or frame error in how the
wrench is applied, is wrong.

**So the moving-SDF path is not validated, and must not be presented as such.**
The fixed collider remains the only configuration meeting the 5-10% target. The
realism track does not yet have a coupling force it can build visuals on.

Recommended next step, cheap and diagnostic rather than more sweeping: run rung (b)
with the body held fixed through the *same* new code path (force read via
`sdf_wrench`, pose never updated). If that reproduces -7.67% at g64, the wrench
read is sound and the defect is isolated to the pose-update loop. If it does not,
the defect is in the wrench read itself. That single run separates the two
hypotheses and needs no new physics.

## Item 2, sound speed: not run, and deliberately so

Two reasons, one practical and one now evidential.

`rung_b_coupled.py` exposes no bulk-modulus argument (zero matches for `bulk`,
`BULK`, `sound_speed`); it inherits `BULK = 1.5e5` from `validate_coupling_force.py`.
Reaching c = 1480.98 m/s therefore requires a code change, not a flag. Required
bulk is **1.9939e9 Pa**, a 13,293x increase, and by the solver's own CFL rule
(`substeps_and_dt`, `validate_coupling_force.py:49-56`) substeps rise from 11 to
1198 at g64 and 16 to 1797 at g96, about **109-112x more compute**.

The evidential reason is the stronger one: **item 1 has just shown the moving-collider
model is wrong at both resolutions.** Sweeping the single most expensive parameter
in the project on a model that accelerates a sinking body upward at 4g would spend
roughly 100x a run's cost measuring an artifact. Sound speed should follow, not
precede, a coupling path that reproduces analytic buoyancy.

## Item 1 CORRECTED: the defect is the settle state, not the pose-update loop

Job **3361423** ran the three-mode wrench diagnostic
(`realism_track/diag_wrench_fixed_pose.py`, results in
`realism_track/diag_wrench_3361423/`), six runs, all completed. The mode named
`fixed` reads the force through the identical new code path but never updates the
collider pose, so it isolates the wrench read from the pose loop.

| n_grid | `fixed` | `pose_zero_vel` | `pose_full` | rung (b), for reference |
|---|---|---|---|---|
| 64 | **-48.49%** | -45.53% | -18.86% | -18.86% |
| 96 | **+349.55%** | +62.33% | +114.94% | +115.03% |

`pose_full` reproduces rung (b) to within 0.09 percentage points at both
resolutions, so the diagnostic is a faithful stand-in for rung (b).

**The `fixed` mode did not reproduce -7.67%. It came in at -48.49%.** Both
hypotheses in the previous section were therefore wrong: the wrench read is not
sound in this configuration, and the pose-update loop is not the primary defect.
With the body held completely still, the force is already off by a factor of two
at g64 and a factor of 4.5 at g96.

### Root cause, verified in the source and in the reference data

`rung_b_coupled.py` and `run_c1_sdf` never shared a configuration. Two differences,
both material, both checked live:

**1. Submersion.** `run_c1_sdf` (`validate_coupling_force.py:899-1000`) places the
cube with `box_bottom_cells=8.0`, which puts `box_top` exactly at the nominal free
surface, and after the displacement rise the cube ends up **fully** submerged. The
reference JSONs confirm it: `submerged_height_frac` = 1.0 with margin +2.75 dx
(g64) and +5.36 dx (g96) of water above the cube top, measured against
`F_buoy_analytic = rho_w * V * g` = 31,298.44 N. `rung_b_coupled.py` instead calls
`box_bottom_cells_for_submersion(0.80, 18)` and realizes frac **0.5187**, against a
partial-submersion reference of 16,233 N. Different geometry, different reference,
different physics.

**2. Settling.** `settle_pinned` (`validate_coupling_force.py:620-646`) advances
`tank.substeps` substeps per iteration (11 at g64, 16 at g96) and exits on a
convergence gate, `sound_speed / vmax >= 20`. The reference runs met that gate at
354 frames = **3,894 substeps** (g64) and 776 frames = **12,416 substeps** (g96),
finishing at vmax 0.510 and 0.634 m/s. `rung_b_coupled.py`'s settle loop advances
**one** substep per iteration with no gate: at 900 substeps it delivers **23%** of
the settling the reference needed at g64 and **7.2%** at g96.

The force scatter confirms the water is still ringing. The reference tail standard
deviation is 828 N at g64 (2.9% of the mean) and 102 N at g96 (0.3%). In rung (b)'s
configuration, Fz sweeps -3,360 to +23,847 N at g64 with the body fixed, a
peak-to-peak of 27,207 N against an analytic 16,233 N, and 35,077 to 118,831 N at
g96. A hydrostatic measurement cannot swing by 1.7 times the quantity it is
measuring. `settle_vmax_peak` in the reference runs is 9.82 and 12.43 m/s against
c = 12.845 m/s, so the initial collapse is very nearly sonic and needs the full
gated settle to decay.

### What this retracts

The previous section's headline, "the moving collider does not preserve 7.3-7.7%",
is correct as a bare observation but wrong in attribution. It charged the
difference to collider motion. Most of it is geometry and settle state: an
unsettled, half-submerged tank measured against a partial reference. The 7.3-7.7%
figure was never inheritable by rung (b), and not because the collider moves.
**Treat that section as superseded on cause, retained only for the raw numbers.**

### One genuine positive result about the API

Comparing `pose_zero_vel` with `pose_full` isolates the velocity argument to
`set_sdf_pose`. At g64 the steady force moves from -45.53% to -18.86% and the net
descent halves, from -0.2449 m to -0.1236 m; at g96 it moves from +62.33% to
+114.94%. Both shifts are in the same direction, more upward reaction when the
body's velocity is communicated. So `set_sdf_pose`'s `velocity` argument does reach
the grid coupling and is not silently dropped, which is a prerequisite for the
moving-collider path and is now confirmed rather than assumed.

### The test that actually settles it

Job **3361443** puts the reference geometry through both code paths:
`realism_track/rung_b_settled.py`, modes `fixed` and `coupled`, at g64 and g96,
with `box_bottom_cells=8.0` and `settle_pinned` including the convergence gate,
scored on the same steady-tail-mean statistic against `rho_w * V * g`. The `fixed`
arm must reproduce -7.67% and +7.28%, which validates the harness; the `coupled`
arm is then the first honest measurement of the moving collider. Any run that
fails the settle gate is flagged `settle_is_discard` in its JSON and must not be
quoted.

Until that returns, the standing statement is unchanged and now better founded:
**no validated coupling force exists for the realism track, so no visual-realism
claim is backed.**

## Item 2 re-costed against the gated settle, and a route that could make it possible

The earlier item-2 estimate priced the measurement window but not the settle. Now
that the settle is known to be the binding constraint, the real cost is much worse,
and the number is worth stating exactly.

Reproducing the solver's own CFL rule (`substeps_and_dt`,
`validate_coupling_force.py:49-56`) with the true `LIM = 9.421742313727737` gives
11 substeps at dt 3.030e-3 (g64) and 16 at dt 2.083e-3 (g96), matching every run
in this track, so the cost model is validated before being extrapolated.

| n_grid | dx | substeps at bulk 1.5e5 | at bulk 1.9939e9 | factor | gated settle now | gated settle at c = 1480.98 |
|---|---|---|---|---|---|---|
| 64 | 0.147215 | 11 | 1,198 | 108.9x | 3,894 substeps | **424,092 substeps** |
| 96 | 0.098143 | 16 | 1,797 | 112.3x | 12,416 substeps | **1,394,472 substeps** |

The settle columns use the frame counts at which the reference runs actually met
the convergence gate (354 and 776 frames). At the throughput measured in job
3361423, roughly 11 substeps/s at g64 and 8.5/s at g96 once startup is excluded,
the settle alone is about **11 hours** at g64 and about **46 hours** at g96, per
run, before a single measurement substep. The g96 figure exceeds a normal LS6
single-job wall clock. So at physical sound speed, with this explicit solver and
this settle criterion, the sweep is not merely expensive, it is out of reach.

### A caution: monkeypatching BULK would be worse than having no knob

`BULK` reaches three places, and they do not respond alike. `sound_speed()` and
`substeps_and_dt()` take it as a **default argument**, bound at function definition
time, and `BoxTank` calls both with no argument (`:267-268`). `set_material` reads
the module global at call time (`:272`). Reassigning `BULK` before constructing a
tank therefore changes the fluid's stiffness while leaving the timestep and the
reported sound speed at their 12.845 m/s values. The run would be under-resolved by
a factor of about 110, and worse, the settle gate itself (`sound_speed / vmax >= 20`)
would be evaluated against the wrong speed and would pass far too early. A correct
knob has to thread bulk through `BoxTank.__init__` into all three call sites. That
edit is deliberately not made here while job 3361443 is reading the file.

### The lead that could remove most of the settle cost

The settle exists only because the water is seeded uncompressed. `set_material`
gives every particle density `RHO_W` with the deformation gradient at identity, so
J = 1 everywhere and the column has no pressure gradient at t = 0. It then collapses
into its own hydrostatic profile, and the reference runs record that collapse
peaking at `settle_vmax_peak` 9.82 m/s (g64) and 12.43 m/s (g96) against
c = 12.845 m/s. The tank is very nearly shocked at startup, and the thousands of
settle substeps are spent bleeding that off.

Two pieces needed to skip it are already present:

1. `hydrostatic_density(zeta)` at `validate_coupling_force.py:74` already computes
   the compressible hydrostatic density profile for this EOS. It is currently used
   only for reporting a local density in `run_c3` (`:1008`), never at seeding.
2. The engine exposes `import_particle_F_from_torch`
   (`mpm-engine/src/warpmpm/kernels/mpm_solver_warp.py`). `Solver` has no `set_F`
   wrapper, but `_sim` is reachable directly, which is the same route `BoxTank.pin`
   already uses to write `sim.rigid_x_cm` (`:365-372`). So no engine change is
   required.

Seeding F = J^(1/3) * I per particle, with J = rho_w / hydrostatic_density(depth),
would start the column at its equilibrium compression instead of driving it there.
**This is a lead, not a result: nothing here has been run, and the size of the
settle reduction is unmeasured.** It is recorded because it attacks the root cause
found today, and because it is the only identified route by which a physical sound
speed becomes affordable at all.

## Job 3361443: the settle defect and the force defect are separate

### First, a correction to the section above

The reference runs do **not** use `box_bottom_cells = 8.0`. Both
`data/coupling_validation/c1sdf_sdf_g64.json` and `..._g96.json` record
`z_b_nominal_at_spawn = 0.8832883` against `floor = 0.4416442`, exactly 3.0
DX_CANON above the floor, and `box_top_z = 2.3554356`, exactly 16 DX_CANON. So the
reference used `box_bottom_cells = 3.0`, which is why the cube ends fully submerged.
`run_c1_sdf`'s signature default is 8.0 and its docstring quotes the C1 defaults; I
took the signature default for the reference and was wrong. Job 3361443 therefore
ran at 75-84% submersion, not full, so its `fixed` arm is not the harness-validating
control it was meant to be. The claim in the previous section that the reference
geometry is `box_bottom_cells=8.0` is retracted.

### What the job nevertheless established

| mode | n_grid | frac | gate | settle substeps | steady N | std | ptp | vs full | vs partial | net dz | lat/Fz |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coupled | 64 | 0.7540 | met | 3,883 | 17,650.9 | 298.1 | 1,278.8 | -43.60% | **-25.21%** | -0.0623 | 0.0028 |
| fixed | 64 | 0.7548 | met | 3,883 | 11,829.8 | 322.3 | 1,013.8 | -62.20% | **-49.92%** | 0.0 | 0.0355 |
| coupled | 96 | 0.8389 | NOT met | 14,400 | 18,957.6 | 46.7 | 134.7 | -39.43% | -27.80% | +0.0002 | 0.0616 |
| fixed | 96 | 0.8406 | NOT met | 14,400 | 19,040.4 | 168.7 | 582.0 | -39.17% | -27.63% | 0.0 | 0.1199 |

**The gated settle works, and it is not the cause of the force offset.** At g64 the
settle reproduced the reference almost exactly (353 frames vs 354, 3,883 substeps vs
3,894, `vmax_peak` 9.8143 vs 9.8172, gate met) and it removed the ringing entirely:
Fz peak-to-peak fell from 27,207 N ungated to 1,014 N, which is reference-quality
quiet. The mean offset survived that unchanged. So the unsettled tank was a real
defect that made the signal unusable noise, and a separate defect sets the mean.

**The two g96 rows are discards and must not be quoted.** They failed the
convergence gate at 900 frames (14,400 substeps), ending at vmax 1.02 and 1.30 m/s
against the required c/20. They fail a second, independent criterion too: this
file's own rule is that a lateral force comparable to Fz means the readout is
unsound, and `lat/Fz` is 0.1199 at g96 fixed against 0.0121 in the reference.

**A caveat on scatter, against my own earlier reasoning.** The g96 rows have very
low scatter (ptp 135 and 582 N) while failing the gate at vmax ~1 m/s, because the
residual motion there is slow large-scale sloshing rather than high-frequency
ringing. Scatter is therefore a necessary but not a sufficient indicator of a
settled state. The earlier use of a 27,207 N spread as evidence of ringing is sound
for the ungated runs it described, but it should not be generalized.

### Partial submersion, not resolution, is what breaks the g96 settle

g96 with the waterline cutting through the collider ran the full 900 frames without
converging. The fully submerged reference at the same resolution met the gate at 776
frames with `vmax_final` 0.6341. So g96 does not simply need more settling: with the
free surface intersecting the collider the waterline sustains motion. g64 at the
same placement did meet the gate, so the effect is resolution dependent. This
matters because **the flood-vehicle case is intrinsically the partial-submersion
case.** It is the regime of interest, and it is the regime where both the settle
criterion and the force reading are worst.

## A pressure-deficit model, with its prediction tested

Collecting the fixed-collider results against the analytic appropriate to each
geometry:

| configuration | frac | gate | error |
|---|---|---|---|
| reference g64, bbc 3.0 | 1.0 | met | -7.67% vs full |
| reference g96, bbc 3.0 | 1.0 | met | +7.28% vs full |
| ungated g64, frac request 0.80 | 0.519 | n/a | -48.49% vs partial |
| gated g64, bbc 8.0 | 0.755 | met | -49.92% vs partial |
| gated-attempt g96, bbc 8.0 | 0.841 | NOT met | -27.63% vs partial |

A partially submerged box takes its entire upward force from the bottom face's
**absolute** pressure, `rho*g*L^2*h_sub`. A fully submerged box takes it from the
**difference** between bottom and top face pressures, where any uniform additive
pressure deficit cancels. That is exactly the observed split: about -7 to +7% when
the quantity is a difference, about -50% when it is an absolute. The candidate
mechanism is that MPM free-surface particles have incomplete kernel support, so J
stays near 1 and pressure near 0 over a surface layer some cells thick, removing
`rho*g*(layer)` of head from every pressure beneath it.

That model makes a falsifiable prediction: if the layer is a fixed number of
**cells**, the error must shrink in proportion to dx. Recorded before reading the
g96 result, the prediction was about -30% vs partial (-29.88% once the submersion
actually realized at g96 is used, frac 0.8406 giving h_sub 1.2375 m). **Measured
-27.63%.** Stated as the invariant the model is about:

| | dx | deficit Pa | deficit in cells of head |
|---|---|---|---|
| g64, gate met | 0.147215 | 5,441.6 | **3.768** |
| g96, gate NOT met | 0.098143 | 3,354.4 | **3.484** |

The deficit falls by a third in Pascals while staying nearly constant in cells,
which is a fixed-thickness surface layer and not a gradient error.

**This is two points, one of them a discard, and inferred from force rather than
measured.** Job 3361504 tests it directly: it exports per-particle stress after a
gated settle and compares the binned pressure against `rho*g*(zs - z)`. A deficit
constant in cells of head across depth confirms a surface offset; one that grows
with depth means a gradient error and refutes the model. That job also runs the
hydrostatic pre-compression test, which matters more now that the settle is
confirmed to cost 3,883 substeps even at the cheap resolution.

## Job 3361504: the deficit is a constant PRESSURE offset, and two of my own claims fall

The probe reproduced the reference configuration exactly at both resolutions, which
validates it before anything is concluded from it: g64 settled in 354 frames / 3,894
substeps with `vmax_peak` 9.8172 and surface 2.760394, against the reference's 354 /
3,894 / 9.8172 / 2.760142; g96 in 777 frames / 12,432 substeps with surface 2.877205
against 776 / 12,416 / 2.881011.

### The surface-layer model is refuted

| | dx | deficit in cells of head | deficit in Pa |
|---|---|---|---|
| g64 | 0.147215 | 4.238 | **6,121** |
| g96 | 0.098143 | 6.508 | **6,266** |

The fixed-cell model required the cell figure to be constant across dx. It changes by
54%. The Pascal figure changes by 2.4%. So the deficit is a **resolution-independent
pressure offset of about 6.1 to 6.3 kPa**, not a fixed-thickness surface layer. The
prediction was recorded before the g96 force result and its apparent success there
was coincidental: a single force-inferred aggregate can match a mean while the
profile it is supposed to describe is wrong.

### The offset model does explain the full-versus-partial split

A constant additive offset cancels in a pressure **difference** and survives in an
**absolute** pressure. That is the whole pattern:

| case | force depends on | predicted | measured |
|---|---|---|---|
| full submersion, g64 | p_bottom - p_top | 0% (offset cancels) | -7.67% |
| full submersion, g96 | p_bottom - p_top | 0% (offset cancels) | +7.28% |
| partial, g64, gate met | p_bottom absolute | -56.2% | **-49.92%** |
| partial, g96, gate NOT met | p_bottom absolute | -51.6% | -27.63% (discard) |

The residual -7.67% and +7.28% at full submersion are not explained by this model,
but they are small and they bracket zero. The g64 partial prediction lands within
6.3 percentage points of measurement. The g96 partial row is a discard and is listed
only for completeness.

**An earlier apparent contradiction dissolves.** Differencing two measured bins gave
a force implying -54.9% at full submersion against the wrench's -7.67%, a factor of
2.05, which looked like the wrench and the pressure field disagreeing. Both bins were
unfit for the purpose: the deep one (depth 1.8679) is an outlier carrying a
11,355 Pa deficit against a 6,121 Pa mean, and the shallow one (depth 0.4509) has
`p_analytic` 4,423 Pa below the offset itself, so its pressure is floored near zero
and its deficit is clipped. No cup test is needed to resolve it.

### The velocity gate does not certify hydrostatic equilibrium

At g64, comparing the measured J per depth bin against the EOS's own hydrostatic
requirement `J(zeta) = (1 + b*zeta)^(-1/(gamma-1))` with `b = 0.00594545` per m, the
column reached on average **0.459 of the required compression** (std 0.258) at the
moment the gate passed. At the bottom, J measured 0.948 where hydrostatic needs
0.875. So the gate certifies quiet velocities, not a hydrostatic pressure field, and
a run can pass it while its pressure is a third to a half short. Both resolutions
stop at the same `c/vmax >= 20` criterion, which is consistent with both ending the
same amount short in Pascals.

Per-particle J spans [0.227, 1.978] at g64 and [0.367, 2.030] at g96, where
equilibrium needs [0.875, 1.0]. At bulk 1.5e5 the equilibrium signal is a 4.6%
compression, so it sits well inside the particle-level noise.

### Hydrostatic pre-compression: refuted, and my "no engine change" claim retracted

Pre-compression changed **nothing**: 354 frames with and without, `vmax_peak` 9.8172
both, and vmax traces identical value by value (first six 0.336, 0.710, 1.104, 1.458,
1.773, 2.076 in both). The write itself succeeded, J applied in
[0.856393, 0.998687] and `detF_matches_J` True on read-back.

The source says why. For mat 6, 10 and 12, `mpm_utils.py:1086-1089` does

    J = wp.determinant(state.particle_F_trial[p])
    Jcbr = J ** (1.0 / 3.0)
    state.particle_F[p] = wp.mat33(Jcbr, 0, 0, 0, Jcbr, 0, 0, 0, Jcbr)

so for a fluid `particle_F` is **overwritten from `particle_F_trial`** at every stress
evaluation. The engine imports `particle_x`, `particle_v`, `particle_F`, `particle_C`,
`particle_selection` and `particle_material`, but there is **no importer for
`particle_F_trial`**. So the earlier statement in this file that hydrostatic seeding
"requires no engine change" is **wrong and is retracted**. Writing `particle_F` is
discarded for fluids; the array that governs fluid pressure cannot currently be set
from outside. My verification was also insufficient: it confirmed the write landed,
not that the write mattered.

### Two defects in the probe itself, to fix before it is used again

`np.clip(np.digitize(z, edges) - 1, 0, nbins - 1)` dumps every particle at or below
the floor into bin 0, which is why bin 0 holds 126,017 particles against about 25,000
elsewhere. Bin 0 is uninterpretable and was excluded from every number above. And the
settled free surface is rough, `column_surface` IQR 0.347 m at g64 which is 2.36
cells, so a single median surface is a poor per-particle depth reference and the
near-surface bins inherit that error.

## The -50% was a measurement artifact. Corrected, the wrench is accurate to about 8%

This section overturns the central negative result of this track. It is built on
numbers already in hand, re-read rather than re-run, and the confirming run is
job 3362500.

### The tank leaks continuously and the rescue piles water at the floor

The reference runs record their own leak counters, and they are extraordinary:

| | n_water | `leaked_cumulative` after settle | per substep | per particle |
|---|---|---|---|---|
| g64 | 443,584 | **9,496,472** | 2,439 | **21.4** |
| g96 | 1,502,496 | **24,873,999** | 2,003 | **16.6** |

`escaped_water` reads 0 and `max_floor_penetration_dx` reads 0.2599, which is
exactly the `eps = 0.25*dx` clamp target in `project_water`
(`validate_coupling_force.py:331-352`). That routine clamps an escaped particle's
position to a single plane and then zeroes the offending velocity component,
`vw[out_lo] = np.maximum(vw[out_lo], 0.0)`. So water sinks through the floor about
0.55% of all particles per substep, gets teleported back to one z plane with its
downward momentum deleted, and does so 21 times per particle over a settle.

The result is a particle sheet at the floor. Measured from the probe histograms,
with bin 0 handled explicitly:

| | excess particles packed at the floor | fraction of all water |
|---|---|---|
| g64 | 100,246 | **22.6%** |
| g96 | 231,948 | **15.5%** |

Their `J_mean` is 0.948, so they are not physically compressed. They are spatially
overpacked while their bookkeeping volume is untouched, which is precisely what a
position clamp does.

### That inflates the free-surface estimate, and the estimate is the reference

`column_surface` (`:395-405`) is a good estimator of the wrong thing here. It sums
particle **volume** per column and divides by column area, so it reports the height
the water would have if it were distributed normally. It cannot see that a fifth of
the water has been spatially collapsed into a sheet. Two independent estimates of
the true surface agree:

| | reported (volume-based) | half-density surface | gap | gap as head |
|---|---|---|---|---|
| g64 | 2.7604 | 2.1653 | 0.5951 m | 5,838 Pa |
| g96 | 2.8772 | 2.2918 | 0.5854 m | 5,743 Pa |

A sheet-corrected estimate gives 5,911 Pa (g64) and 6,376 Pa (g96). **The measured
pressure offsets were 6,121 Pa and 6,266 Pa.** The agreement is 2 to 8%.

So the "constant pressure deficit" is real as a measurement and is **not a defect in
the MPM pressure field**. It is `rho*g*` the amount by which the free-surface
reference is too high. Its dx-independence, which refuted the surface-layer model,
now follows immediately: the gap is about 0.59 m at both resolutions because it is
set by the piled mass fraction, which is a physical quantity, not a cell count.

### The force errors follow, and they collapse

`f_partial = rho*g*L^2*h_sub` takes `h_sub` from that same inflated surface, so the
partial-submersion reference was too large by the same 0.6 m of head:

| g64, gate met | h_sub used | analytic | measured | error |
|---|---|---|---|---|
| fixed, reported surface | 1.1111 m | 23,623 N | 11,830 N | **-49.92%** |
| fixed, half-density surface | 0.5160 m | 10,971 N | 11,830 N | **+7.83%** |

Full submersion uses `F = rho*V*g`, which contains no surface term at all. That is
why -7.67% and +7.28% were never affected, and why the two cases looked so
different. Corrected, every static configuration agrees with analytic buoyancy to
within about 8%:

| configuration | error |
|---|---|
| full submersion, g64 | -7.67% |
| full submersion, g96 | +7.28% |
| partial submersion, g64, corrected | +7.83% |

**The SDF collider wrench was sound the whole time.** The apparent -50% catastrophe
was an inflated reference.

### What this retracts

- "Partial submersion is where the force reading is worst" is **withdrawn**. Partial
  submersion is where the *reference* is worst.
- The constant-offset explanation of the full-versus-partial split stands as
  arithmetic, but its stated cause, an under-compressed column, is **wrong**. The
  column is not meaningfully under-compressed; the surface estimate is too high.
- The earlier reading that the velocity gate leaves the column at 0.459 of
  hydrostatic compression is **an artifact of the same inflated surface**, since the
  required compression was computed from an over-deep column.

### Confidence, stated plainly

The gap is interpolated from binned histograms with a bin width of 0.875 dx, so it
carries roughly half a bin of uncertainty, about 0.06 m, which is about 600 Pa and
about 6 percentage points on the corrected force error. So the honest statement is
**+8% with an uncertainty near 6 points**, not a precise 7.83%. That is still
decisively different from -50%. Job 3362500 measures the surface directly from a
raw z-histogram rather than inferring it, on both the partial and full geometries.

### The leak is still a real defect, and it now has a testable cause

None of the above makes the pile-up acceptable. A fifth of the water sitting in a
clamped sheet with deleted momentum is a genuine pathology, and it is the reason the
free surface cannot be estimated by volume. The likely cause is that at bulk 1.5e5,
c = 12.845 m/s, the water is too soft to resist floor penetration, so particles sink
through and the clamp stacks them. That predicts the leak rate should fall sharply
as bulk rises. Job 3362500 tests exactly that at bulk 1.5e5, 1.5e6 and 1.5e7, with a
guard that aborts if the patched bulk does not reach `tank.sound_speed`, so a
desynchronized timestep cannot be measured by mistake.

If that prediction holds, the sound-speed work is re-motivated by a concrete
mechanism rather than a noise argument, and the realism track has, for the first
time, a coupling force that agrees with analytic buoyancy to about 8% in every
static configuration tested.

## Job 3362500: the artifact confirmed by direct measurement, and by intervention

### Direct measurement replaces the inference

Run A repeats the partial-submersion case and measures the free surface from a raw
z-histogram instead of inferring it from binned counts:

| quantity | inferred earlier | measured in run A |
|---|---|---|
| water below the floor plane | not obtainable | **80,186 = 18.08%** |
| excess piled near the floor | 100,246 = 22.6% | 96,869 = **21.84%** |
| surface gap | 0.5951 m | **0.5698 m** |
| leak rescues per particle | 21.4 | **22.24** |
| partial-submersion error, corrected | +7.83% | **+2.98%** |

Run B repeats the reference geometry and reproduces the canonical run essentially
exactly: `leaked_cumulative` 9,496,478 against the reference's 9,496,472, and
surface 2.760561 against 2.760142.

### The reference case is not fully submerged, which corrects the canonical figure

Run B's measured surface is 2.1813, and the box top is at 2.3554. **The free
surface is below the box top.** The reference configuration, the one the project's
canonical 7.3 to 7.7% figure rests on, is about 88% submerged, not fully submerged.

That withdraws my own claim from the previous section that full submersion "has no
surface term so was never affected". `rho*V*g` is surface-independent only if the
body is genuinely submerged, and it is not.

| g64, gate met | analytic used | error |
|---|---|---|
| A, bbc 8.0, reported surface | 23,601 N | -49.88% |
| A, bbc 8.0, measured surface | 11,487 N | **+2.98%** |
| B, bbc 3.0, full-submersion assumption | 31,298 N | -9.32% |
| B, bbc 3.0, measured surface, h = 1.2980 m | 27,596 N | **+2.85%** |

Two very different geometries, corrected independently, agree to 0.13 percentage
points. **The SDF collider wrench reproduces analytic buoyancy to about +2.9% at
g64.** The spread that this track has been chasing since the beginning, -7.67% to
+115%, was almost entirely a free-surface reference error.

### The causal chain, confirmed by intervention

Runs C and D raise the bulk modulus with the timestep and sound speed correctly
re-derived, guarded by an abort if `tank.sound_speed` does not match:

| bulk | c (m/s) | leaks per substep | per particle | below floor | piled | surface gap |
|---|---|---|---|---|---|---|
| 1.5e5 | 12.85 | 2,541.2 | 22.24 | 18.08% | 21.84% | 0.5698 m (5,590 Pa) |
| 1.5e6 | 40.62 | 397.0 | 1.83 | 3.04% | 1.72% | 0.0939 m (921 Pa) |
| 1.5e7 | 128.45 | **13.1** | **0.06** | **1.18%** | **0.41%** | **0.0544 m (533 Pa)** |

Monotone across three points, and the reduction is large: 194x fewer rescues, 53x
less piling, 10.5x smaller surface gap. This closes the loop:

    water too soft to resist floor penetration
      -> particles sink through the floor plane
      -> project_water clamps them to one z plane and deletes their downward momentum
      -> a spatially overpacked sheet accumulates at the floor
      -> column_surface, which sums bookkept volume, cannot see the collapse
      -> the reported free surface is ~0.57 m too high
      -> every analytic reference built on it is inflated
      -> the wrench appears to be ~50% low when it is actually within ~3%

Raising the stiffness removes the first link and the last one disappears with it.

### A second defect in the settle criterion

The gate is `sound_speed / vmax >= 20`, so its velocity threshold **scales with c**
and becomes easier as the fluid stiffens:

| bulk | gate threshold vmax | stopped at vmax | frames used |
|---|---|---|---|
| 1.5e5 | 0.642 m/s | 0.510 | 354 |
| 1.5e6 | 2.031 m/s | 1.950 | 62 |
| 1.5e7 | 6.423 m/s | 4.028 | **20** |

Run D stopped at exactly `settle_min_frames`, the floor of the allowed range. So C
and D are far **less** settled in absolute terms than the baseline, and **their force
numbers are not usable**: D reads -48.67% even after correction simply because its
tank has barely settled. They are reported here only for the leak trend.

That makes the leak result stronger rather than weaker. Run D leaks 194 times less
than the baseline while ending at eight times the absolute velocity, which is the
opposite of what more violent motion would produce.

It also means a bulk sweep cannot use this gate. An absolute criterion is needed,
for instance `vmax < 0.05 m/s` or a fixed physical settle time, or every stiffer run
will silently stop earlier and look worse.

### The moving collider is now the only open defect

With the reference corrected, the coupled g64 run still reads high. Its recorded
force and displacement are internally consistent, reintegrating `f_series`
reproduces `net_dz` to the digit. Against corrected static buoyancy of 11,486 N it
measures 17,651 N, an excess of 6,164 N. Explaining that as added mass requires
7,731 kg, which is 2.42 times the displaced mass of the **entire** cube while the
body is only about 37% submerged, against a physical bluff-body coefficient of 0.5
to 1.0. So it is not added mass.

The leading candidate is the velocity handed to `set_sdf_pose`. The three-mode
diagnostic showed `pose_zero_vel` to `pose_full` adding roughly 4,300 N at g64, the
same order as this excess, and for a separable collider the impulse is
`m*(v_free - v_surf - v_tan)`, so every node in the contact band contributes once
`v_surf` is nonzero, which a fixed collider never exercises. The test is a
kinematic sweep: drive the collider at several prescribed constant velocities and
check whether the wrench scales like physical drag or like a node count.

## The correct estimator: mass above the face, not a half-density crossing

The half-density surface used above is a proxy. The physically correct quantity is
the mass of water per unit area above the face in question, because that is what
sets the pressure there, and it assumes nothing about the shape of a diffuse
interface. From the raw histograms,

    h_eff = (particles above the box bottom) / (bulk linear particle density)

| run | gate | h_eff | analytic | measured | error |
|---|---|---|---|---|---|
| A, g64, bbc 8.0 partial | met | 0.5509 m | 11,712 N | 11,829 N | **+1.00%** |
| B, g64, bbc 3.0 "full" | met | 1.3181 m | 28,023 N | 28,382 N | **+1.28%** |
| E, g96, bbc 3.0 | **NOT met** | 1.3978 m | 29,719 N | 32,948 N | +10.87% |

At g64 the two gate-met runs, at box positions five cells apart, agree with analytic
buoyancy to **+1.0% and +1.3%**. The more principled estimator gives the better
agreement, which is itself evidence the correction is real rather than a fitted
fudge: a spurious correction does not improve when it is made more rigorous.

The half-density numbers above (+2.98%, +2.85%) are superseded by these.

**So the SDF collider wrench reproduces analytic buoyancy to about 1% at g64.** The
entire -50% to +115% history of this track was a free-surface reference error caused
by leaked water piling at the floor.

## The g96 settle is not reproducible, and that is its own problem

Run E used a configuration byte-identical to the earlier pressure probe: dx
0.0981431491013306, dt 2.083333e-03, 16 substeps per frame, `n_water` 1,497,096,
bulk 1.5e5, c 12.8452. The outcomes differ:

| run | frames to gate | vmax_final | gate |
|---|---|---|---|
| canonical reference | 776 | 0.6341 | met |
| pressure probe | 777 | 0.6232 | met |
| run E | 900 (cap) | **1.5132** | **not met** |

That is not a marginal miss. E ends at more than twice the threshold. At g64 the
same comparison is tight, three independent runs meeting the gate at 353, 354 and
354 frames, so reproducibility degrades with particle count and settle length.
warp's P2G uses atomic adds, which are order-nondeterministic in floating point, and
`vmax` is an extreme-value statistic over 1.5 million particles, so a long near-sonic
settle can diverge.

Consequences worth stating:

- **Run E is a discard** and its +10.87% cannot be quoted. The +1% result stands only
  at g64 until a gate-met g96 run with a direct histogram exists.
- **The canonical "gate met at 776 frames" is not a reproducible property.** Any
  validation number taken from a single g96 settle needs repeat runs and an error
  bar, not a single value. That applies to the project's existing 7.3 to 7.7%
  figure, which came from one run per resolution.
