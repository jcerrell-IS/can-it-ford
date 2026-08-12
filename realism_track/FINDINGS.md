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

**SUPERSEDED IN PART, 2026-08-12 evening, by job 3361315.** The -7.67%/+7.28%
figures are rung (a), fully submerged and still. Rung (b), partially submerged,
has since been RUN, and it does not carry: buoyancy reads **-18.9% at g64 and
+115.0% at g96**, and the body sinks at one grid while rising at 4 g at the
other. Read "the validated path" as validated at full submersion only. It is
refuted, for now, at the partial submersion where buoyancy is actually generated.
Do not quote -7.67%/+7.28% as a coupling-accuracy figure for a floating vehicle.

**Root cause, after one wrong turn and a retraction, 2026-08-13.** Two causes,
both established, neither of them exotic:

1. **The water was never settled.** `rung_b_coupled.py:83` advanced one substep per
   iteration where the reference `settle_pinned` advances one frame under a
   quiescence gate. The gate needs 3,894 substeps at g64 and 12,416 at g96, so the
   900 that ran were 23 percent and 7.2 percent of the settling the reference
   required. A fixed body in that tank shows `Fz` sweeping 27,207 N peak to peak
   against a 16,233 N analytic: a ringing tank, not a hydrostatic reading. Fixed in
   `79fec32`.
2. **The comparison was never like-for-like.** `run_c1_sdf`, source of the
   -7.67/+7.28 percent figures, is FULLY submerged at frac 1.0; rung (b) realizes
   frac 0.5187 against a partial reference. The two were never the same experiment.

**A retracted third explanation, kept visible on purpose.** An intermediate revision
of this document argued the added-mass ratio was the primary cause. It is not.
Under-relaxation, the documented remedy, makes the error monotonically WORSE at both
grids, and the error persists at -48.49/+349.55 percent with the body held
completely still. The underlying identity (any floating body sits at ratio exactly
1.0) is still true and still constrains scheme choice, but it did not cause this.
Full retraction below.

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

## Rung (b) RAN on LS6 A100, job 3361315, and FAILED

The GH200 blocker above was routed around: rung (b) does not need Hopper, and LS6
does import `warpmpm` once the venv is built in `$SCRATCH` (the "LS6 cannot import
warpmpm at all" claim in the BLOCKED section is refuted by this job's own
`=== warpmpm import check ===` line). Job 3361315, partition `gpu-a100-dev`, node
c301-004, `State=COMPLETED ExitCode=0:0`, `Elapsed=00:34:21`. Both grids produced
output; nothing crashed or timed out.

| | g64 | g96 |
|---|---|---|
| `F_buoy_analytic_N` | 16233.24 | 17460.36 |
| `Fz_measured_median_N` | 13172.21 | 37544.72 |
| `ratio_median_over_analytic` | **0.8114** | **2.1503** |
| `a_ideal_ms2` | -1.3299 | -0.6889 |
| `a_measured_first3_ms2` | **-2.1898** | **+39.8544** |
| `net_dz_m` | -0.1236 | +0.4007 |
| `submersion_frac_realized` | 0.5187 | 0.5579 |
| `nonzero_wrench` / `clamped_steps` | true / 0 | true / 0 |

The force accumulator is alive: the wrench is non-zero and nothing was clamped on
either grid. That is the one thing rung (b) does confirm. Everything else fails.
Buoyancy is 18.9% low at g64 and 115.0% high at g96, and the sign of the motion
flips between grids: the body sinks at g64 and accelerates upward at 39.85 m/s2,
about 4 g, at g96, when both should sink gently at about -1 m/s2. Refining the
grid makes the answer worse and reverses it, which is a divergence signature, not
convergence scatter.

### What is NOT the cause

Two plausible explanations were checked and both are ruled out.

**Not the submersion shortfall.** `submersion_frac_realized` is 0.52 and 0.56
against 0.80 requested, but `rung_b_coupled.py:87-96` builds the analytic
reference from the MEASURED settled surface, not the request, exactly as its
docstring says. Each grid is therefore compared against its own realized `h_sub`,
and both `F_buoy_analytic_N` values reproduce `RHO_W * G * L^2 * h_sub` to
rounding. The reference is sound.

**Not the integrator.** `simulation/coupling_force/test_rigid_body.py` passes all
13 assertions, on the A100 in this job and independently on the Mac: SHM period
1.73731 s against a theoretical 1.7373, torque-free |L| and E drift of 7.6e-05
and 1.0e-04 relative, inertia within 0.4% of the analytic solid box. Newton-Euler
is correct. The error is upstream of it.

### RETRACTED as a cause: the added-mass identity is true but does not explain rung (b)

**Retracted 2026-08-13, same day it was written, by experiment.** An earlier
revision of this section claimed the added-mass ratio was the PRIMARY cause of
rung (b)'s failure and demoted the settle defect to secondary. That causal claim is
withdrawn. The settle defect is primary after all. The identity below is still
mathematically true and still worth knowing, but it is not the failure mechanism.

What refuted it, verified here by reading the artifacts directly rather than
accepting the claim: job 3361371 swept `--relax` and under-relaxation, which is the
documented remedy for added-mass instability, makes the error **monotonically
worse** at both grids while `added_mass_ratio` stays fixed.

| grid | relax 1.0 | relax 0.5 | relax 0.25 | added_mass_ratio |
|---|---|---|---|---|
| g64 | 0.8114 | 0.8006 | 0.7688 | 0.8644 |
| g96 | 2.1503 | 2.1991 | 2.3228 | 0.9300 |

If this were partitioned-explicit added-mass divergence, relaxation would have
improved it. It did the opposite, monotonically, at both grids. Two further
results from job 3361423's fixed-pose diagnostic close it off: with the body held
**completely still** the error is -48.49 percent at g64 and +349.55 percent at g96,
so the error does not require body motion at all, and fixed-body `Fz` sweeps
27,207 N peak to peak against a 16,233 N analytic, which is a ringing tank rather
than a hydrostatic measurement.

A caution for anyone re-deriving this from the relax-sweep JSONs: every one of them
records `relax` as absent, so a reader has only the FILENAME to tell 0.25 from 1.0.
That provenance gap is closed going forward by `79fec32`, which records `relax` in
the artifact.

**The identity itself still stands and is still a design constraint**, just not the
diagnosis:

`coupler.py:121-130` defines

    added_mass_ratio = rho_w * V_displaced / m_body

and `coupler.py:36-42` states that a partitioned explicit scheme over-predicts and
can diverge as this ratio approaches 1, with `warn_added_mass = 0.5` at
`coupler.py:72` as the warning threshold.

Now impose flotation. A body floating at equilibrium satisfies
`m_body * g = rho_w * g * V_displaced`, so `rho_w * V_displaced = m_body`, so

    added_mass_ratio = 1.000000, EXACTLY, for ANY body floating at equilibrium.

That is an identity, not a measurement. It is independent of size, shape, mass and
density. Checked against this project's own vehicle: the canonical Yaris hull at
310.494 kg/m3 floats at submersion fraction 0.3105, giving
`(1000/310.494) * 0.3105 = 1.0000`.

The consequence is structural, not a tuning problem. **Every floating-vehicle case
this project exists to simulate sits at exactly twice the coupling module's own
warning threshold, and at the value its documentation calls the divergence point.**
There is no parameter choice that escapes it while still floating: reaching a ratio
of 0.5 at the rung-(b) design submersion of 0.80 would require a body density of
1600 kg/m3, which is denser than water and therefore sinks rather than floats.

Job 3361315 ran at `relax = 1.0`, meaning no under-relaxation, and printed the
module's own warning on both grids and then continued:

    COUPLING WARNING added_mass_ratio=0.86 exceeds 0.5; a partitioned explicit
    scheme is at its stability limit here. Reduce dt or set relax<1 and treat the
    transient as unconverged until a dt study says otherwise.

The measured errors order with the ratio exactly as that warning predicts:

| | added_mass_ratio | error vs analytic |
|---|---|---|
| g64 | 0.8644 | -18.9% |
| g96 | 0.9298 | +115.0% |
| rung-b design point (frac 0.80) | 1.3333 | not reached |
| any vehicle at true flotation | 1.0000 | not reached |

### ALSO RETRACTED: the prediction that fixing the settle makes rung (b) worse

An earlier revision predicted that correcting the settle would raise realized
submersion toward 0.80, drive `added_mass_ratio` toward 1.3333, and therefore make
rung (b) fail harder. That prediction rested entirely on the added-mass mechanism
retracted above, so it carries no weight and is withdrawn. **Do not use it to
argue against re-running.**

The observation underneath it is still factual and still worth recording: after the
settle fix landed, a 4-frame Mac run reaches realized submersion 0.7758 with
`added_mass_ratio = 1.2930`, so the ratio does rise as the water settles further.
What is withdrawn is the claim that this causes the force error.

Job 3361443 (`rung_b_settled.py`) runs the reference geometry through both the
fixed and coupled paths with the gated settle and is the direct test of what a
properly settled rung (b) reads. As of this writing it is **PENDING**, so its
outcome is unknown and is deliberately not predicted here.

### The comparison was never like-for-like, which matters more than either cause

Job 3361423's diagnostic established something that undercuts the whole rung
(a) versus rung (b) framing: **`run_c1_sdf` and `rung_b_coupled` never shared a
configuration.** `run_c1_sdf`, which produced the -7.67 and +7.28 percent figures,
is FULLY submerged, frac 1.0, with 2.75 dx and 5.36 dx of water standing above the
cube top, and is scored against `rho_w*V*g` for the whole cube. Rung (b) realizes
frac 0.5187 and is scored against a partial-submersion reference.

So the headline "buoyancy accuracy does not carry from rung (a) to rung (b)" was
comparing two different experiments. That is a design defect in the ladder step,
not only an execution defect in the run, and it has to be fixed before any number
from rung (b) can be set beside the rung (a) figures at all.

### What this means for the moving-SDF path

Less than the retracted section claimed. The pose-update loop is NOT the primary
defect: with the body held completely still the error is still -48.49 percent and
+349.55 percent. Confirmed in passing by the same diagnostic, `set_sdf_pose`'s
velocity argument does reach the grid coupling, and enabling it moves g64 from
-45.53 to -18.86 percent, so the moving-collider machinery works as intended.

The live explanation is the plain one: an unsettled, ringing tank measured against
a mismatched reference. Both are fixable, and neither refutes path (a).

The added-mass identity remains a real constraint on SCHEME CHOICE for later work,
since any floating body sits at ratio 1.0 against a module that warns above 0.5.
It is simply not what went wrong here.

CAVEAT retained, and now doubly relevant: the claim that a partitioned explicit
scheme *diverges* near ratio 1 is `coupler.py`'s own, attributed there to Zhang et
al. 2026, and that citation has NOT been checked against its source. The relax
sweep is evidence against that mechanism operating here, which is one more reason
to verify the citation before relying on it.

### Primary cause, confirmed independently: the settle is 1 substep per iteration, not 1 frame

Reinstated as primary after the added-mass retraction above. Job 3361423 reached the
same conclusion from a different direction and measured the deficit better than the
cap-based figures below: `settle_pinned`'s gate is met at **3,894 substeps at g64 and
12,416 at g96**, so the 900 substeps rung (b) ran were **23 percent and 7.2 percent**
of the settling the reference actually needed. Prefer those numbers to the
cap-relative ones in the table below, which use the 600-frame ceiling as denominator
and therefore understate how close the run came to the floor.

`rung_b_coupled.py:81-85` settles with

    tank.solver.step(tank.dt, 1)

one SUBSTEP per iteration. Every canonical path settles through
`settle_pinned` at `simulation/validate_coupling_force.py:617-643`, which steps

    tank.solver.step(tank.dt, tank.substeps)

one FRAME per iteration, via `BoxTank.step` at `:373-375`. Because `tank.substeps`
is grid-dependent (`substeps_and_dt`, `:49-56`), a fixed iteration count settles
each grid for a different physical duration:

| | substeps | dt | 900 iterations | canonical 600-frame cap |
|---|---|---|---|---|
| g64 | 11 | 0.00303030 s | **2.7273 s** | 6600 substeps, 20.0 s |
| g96 | 16 | 0.00208333 s | **1.8750 s** | 9600 substeps, 20.0 s |

Both `dt` values reproduce the JSON bit-for-bit from `substeps_and_dt`, so the
table is derived, not assumed. Three consequences, and they match every anomaly
observed:

1. The settle is 13.6% (g64) and 9.4% (g96) of the canonical substep budget, so
   the water is nowhere near equilibrium when the coupler is attached. That is why
   `submersion_frac_realized` never reaches the requested 0.80 on either grid.
2. The two grids settle for DIFFERENT physical times, 2.7273 s against 1.8750 s,
   a 31.2% shorter settle at g96. That is why the realized fractions differ from
   each other, and it means the g64/g96 pair was never a controlled refinement
   comparison.
3. g96, settled least, is furthest from equilibrium and carries the most residual
   water motion, which is the natural reading of its 2.15x wrench and 4 g upward
   launch. The measured force is transient water dynamics, not hydrostatic
   buoyancy.

This also corrects the "Experimental-design correction for item 1" section above,
which states that `--settle 900` was chosen "to match the settle depth of the
gated C1SDF runs". It does not match it. The gated runs cap at 600 FRAMES with a
convergence gate; 900 iterations of 1 substep is 81.8 frames at g64 and 56.3 at
g96, with no gate at all.

`settle_pinned` also carries a convergence criterion, `settled = True` once
`sound_speed / vmax >= 20.0` past a `min_settle` floor derived from acoustic
transit time, and reports it as `settle_gate_met`. `rung_b_coupled.py` has no
equivalent, so it cannot detect that it stopped early. It stopped early.

### Do not proceed to rung (c) or (d)

Per the standing instruction, rung (b) gates the ladder and rung (b) has not
passed. No threshold was adjusted and none should be.

### The settle fix, DONE, and what it actually costs

Landed in commit `79fec32`. The hand-rolled loop is gone; `rung_b_coupled.py` now
calls the same `settle_pinned` that `run_c1_sdf` uses, which is safe with an SDF
collider because `BoxTank.pin` is a no-op for non-rigid modes
(`validate_coupling_force.py:365-366`). `--settle N` now means N FRAMES on both
grids, and the default moved 400 to 600 to match `run_c1_sdf`'s `settle_frames`.

**COST CORRECTION.** An earlier draft of this section put the fix at roughly 9x the
solver work. That took the 600-frame cap as the expected cost, which is wrong,
because `settle_pinned` BREAKS EARLY once its quiescence gate trips. The floor is
`min_settle`, and because `DX_CANON` is a fixed constant rather than `dx`, the
water depth is grid-independent at 2.6499 m, so the acoustic transit is 0.206292 s
and `min_settle` is **62 frames on both grids**, confirmed by the Mac run
reporting `settle_min_frames=62`.

| | substeps/frame | if gate trips at the 62-frame floor | if it runs to the 600 cap | job 3361315 ran |
|---|---|---|---|---|
| g64 | 11 | 682 substeps | 6600 substeps | 900 |
| g96 | 16 | 992 substeps | 9600 substeps | 900 |

So the realistic cost is comparable to what already ran, and only the pathological
no-convergence case is 9x. Budget for the cap, expect the floor, and read
`settle_frames_run` in the output to see which happened.

### What is actually outstanding

Both mitigations an earlier revision proposed have already been tried or are in
flight, so the open question is narrower than it looked.

- **Under-relaxation: DONE and refuted.** Job 3361371 swept relax 1.0, 0.5, 0.25.
  Monotonically worse at both grids. Do not re-propose it as the fix.
- **Gated settle at the reference geometry: SUBMITTED, job 3361443**
  (`rung_b_settled.py`), running the reference geometry through both the fixed and
  coupled paths. PENDING as of this writing. This is the decisive test and its
  result should be read before anything else is decided.
- **Configuration match: still unresolved and probably the real blocker.** Rung (b)
  at frac 0.5187 cannot be set against a rung (a) reference at frac 1.0. Either
  rung (b) must be rerun fully submerged to isolate the partial-submersion variable,
  or a partial-submersion fixed-collider reference has to be produced so there is
  something legitimate to compare against.
- **Reduced `dt` at fixed grid:** untried, and it is the one lever the module's
  warning names that has not been exercised.

Rung (c) and (d) remain unattempted, the ladder is still gated, and no threshold has
been tuned at any point.
