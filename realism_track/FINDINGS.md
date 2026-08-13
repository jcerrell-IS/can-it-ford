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

**COST, settled by measurement after two wrong estimates.** The first estimate said
9x, using the frame cap as the denominator. The second "corrected" it to roughly
the cost of what already ran, using `min_settle` (62 frames) as the expected trip
point. **The second was wrong and the first was right.** `min_settle` is only a
floor below which the gate is not even tested; the gate does not actually trip
anywhere near it.

The measured trip points are in this repo already, in the committed rung-(a)
artifacts under `data/coupling_validation/`:

| | substeps/frame | gate tripped at | substeps to settle | job 3361315 ran |
|---|---|---|---|---|
| g64 (`c1sdf_sdf_g64.json`) | 11 | frame **354** | 3,894 | 900 |
| g96 (`c1sdf_sdf_g96.json`) | 16 | frame **776** | 12,416 | 900 |

Total 16,310 substeps against 1,800, so **9.1x**, and that is a measurement rather
than either bound. Job 3361315 took 34:21, so a correctly settled rung (b) will not
fit `-t 02:00:00` on `gpu-a100-dev` and needs the normal `gpu-a100` queue or one job
per grid.

**The cap must be 900, not 600.** An earlier revision of this document, and of both
sbatch files, used 600. That is wrong: `c1sdf_sdf_g96` trips its gate at frame 776,
so a 600 cap would stop g96 short, return `settle_gate_met=false`, and silently
reintroduce under-settling at precisely the grid that failed worst. 900 is also what
the rung-(a) reference actually used, at `scripts/c1sdf.sbatch:38`
(`--settle-frames 900`); 600 is only the Python default of `run_c1_sdf`, which that
invocation overrode. Corrected in the driver default and in both sbatch files.

One row is worth noting for expectations: `c1sdf_box_g96` ran the full 900 frames
and still returned `settle_gate_met=false`, so 900 is not a guarantee at g96 either.
Read `settle_frames_run` and `settle_gate_met` in the output before trusting any
number from a run.

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

---

## RECONCILIATION SEAM, added 2026-08-13. Read this before the sections below.

Everything above this line and everything below it were written in parallel, by two
sessions, on two clones that shared a base and never saw each other. The base is
`realism_track/FINDINGS.md` at `02f08eb` on `origin/main`, byte-identical to the same
file at `cdcdf9d` on the unpushed `/work/11603/jcerrell0629/vista/can-it-ford` clone
(sha256 `185968e0`). Both sides then appended, and neither side's additions are in the
other. This file is the three-way merge of the two, with the common base kept once.

**Above the seam** is the `origin/main` narrative: `6434258`, `ca9bdeb`, `d98837f`,
`be20075`. It analyses job 3361315 and lands on two causes, the one-substep settle and
the not-like-for-like comparison, after retracting the added-mass identity as the cause.

**Below the seam** is the unpushed vista narrative: `001a62c`, `20e2063`, `a3ab0d0`,
`0d81f2f`, `45be8c3`. It is CHRONOLOGICALLY LATER and covers three jobs the sections
above never saw: 3361423 (fixed-pose wrench diagnostic), 3361443 (the gated-settle
rerun), and 3361504 (the pressure probe).

### What the later sections supersede in the earlier ones

1. **The settle is not the whole cause.** The section above titled "Primary cause,
   confirmed independently: the settle is 1 substep per iteration, not 1 frame" is
   correct that the settle was defective and correct that `79fec32` fixes it. It is
   wrong to read it as sufficient. Job 3361443 ran WITH the gated settle and the error
   did not close. Job 3361504 then isolated the residual as a resolution-independent
   constant pressure offset of about 6.2 kPa.

2. **"Do not proceed to rung (c) or (d)" still stands**, and for a stronger reason than
   the section above gives. It is not only that the settle was wrong; it is that at
   g96 the settle gate is still not met even at a 900-frame cap, so the controlled
   refinement pair rung (b) exists to produce does not exist yet.

3. **The added-mass retraction is consistent across both sides.** The identity itself,
   `added_mass_ratio = 1.000000` for any body floating at equilibrium, is retained by
   both as true and as a constraint on future scheme choice, and rejected by both as
   the diagnosis for this failure.

### What is NOT reconciled, and is therefore still open

The two narratives were not rewritten into a single argument, only concatenated in
chronological order with this seam between them. Specific claims above may be stated
more confidently than the sections below leave warranted, and the prose still contains
two independent voices. Anyone quoting this file should quote the LATER section when
the two touch the same question, and should treat a claim that appears only above the
seam and concerns jobs 3361423, 3361443 or 3361504 as untested by the section that
makes it.

### Verification status of this seam

Independently re-derived from the committed JSONs during the merge: the 3361443 result
table, specifically that only g64 carries `settle_gate_met true` and
`settle_is_discard false`, that both g96 runs are self-declared discards, and the
`err_steady_vs_partial_pct` figures of -25.21 (coupled) and -49.92 (fixed) at g64.
NOT independently re-derived, and reproduced here from the vista commit messages and
the sections below: the 6.2 kPa offset figure, the J-compression numbers behind
"the velocity gate does not certify hydrostatic equilibrium", and the
`mpm_utils.py:1086-1089` mechanism behind the pre-compression retraction.

---
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

---

## Job 3362208: the g96 settle gate IS reachable, and the two coupling paths converge

Run 2026-08-13 on LS6 A100 c301-003, inside idev allocation 3362208, driver
`realism_track/run_g96_gated.sh`, results in `realism_track/rung_b_g96_gated_3362208/`.
Identical to `run_rung_b_settled.sbatch` in every argument except `--n-grid` fixed at 96
and `--settle-frames` raised from 900 to 3000.

### The 900-frame cap was short by about 13 percent, nothing more

Both g96 runs in job 3361443 were self-declared discards, `settle_gate_met false`, and
the sections above treat that as a property of g96. It is not. It is a property of the
cap. With the cap at 3000 the gate is met at **1030 frames (coupled)** and **1031 frames
(fixed)**, `ratio_c_over_vmax` 20.54 and 20.91 against the 20 required. Nothing about
the configuration needed to change. 900 was roughly 13 percent short of a gate that both
modes clear at essentially the same frame.

This also retires "Partial submersion, not resolution, is what breaks the g96 settle" as
a statement about reachability. The g96 settle is reachable at partial submersion; it
simply costs about 2.9x the frames g64 needs (1030 against 353).

### The first valid controlled refinement pair rung (b) has produced

All four rows below are `settle_gate_met true`. Errors are against
`F_buoy_analytic_partial_N`, the correct reference for a partially submerged body, and
NOT against the full-submersion figure the stdout banner prints.

| grid | mode | frames | frac_sub | Fz steady N | F_partial N | err vs partial |
|------|---------|--------|----------|-------------|-------------|----------------|
| 64   | coupled | 353    | 0.7540   | 17650.9     | 23600.6     | -25.21 %       |
| 64   | fixed   | 353    | 0.7548   | 11829.8     | 23623.2     | -49.92 %       |
| 96   | coupled | 1030   | 0.8437   | 18580.0     | 26407.9     | -29.64 %       |
| 96   | fixed   | 1031   | 0.8445   | 17837.3     | 26430.9     | -32.51 %       |

**No divergence, and no sign flip.** The unsettled pair from job 3361315 read -18.9
percent at g64 and +115.0 percent at g96, and the sections above call that divergence.
Settled, the same comparison is -25.21 and -29.64 percent: same sign, same order of
magnitude, a 4.4 point spread. The divergence signature was an artifact of comparing two
grids settled for different physical durations. That is now measured, not argued.

### The result that matters most: fixed and coupled converge under refinement

At g64 the two paths are **24.71 points apart** (-25.21 against -49.92). At g96 they are
**2.87 points apart** (-29.64 against -32.51). The fixed collider improves sharply with
refinement, the coupled path degrades slightly, and they meet near -30 percent.

The consequence is the important part. **A deficit that both an SDF-fixed collider and a
free-rigid force-coupled body reproduce, to within 2.9 points at the finer grid, is not
primarily an artifact of the free-rigid coupling.** Whatever produces the roughly 30
percent shortfall at partial submersion is common to both paths. Any framing that treats
the force-coupled path as the broken one and the fixed collider as the trustworthy
baseline is not supported at partial submersion, and at g64 it is backwards: the fixed
collider is the worse of the two by 24.7 points.

### What this does NOT establish, stated so it is not read as more than it is

**The pair is confounded by submersion.** The two grids settle to different surfaces, so
realized `frac_submerged` is 0.754 at g64 and 0.844 at g96. Each grid is scored against
its own reference so neither number is wrong, but this is a refinement comparison with a
second variable moving. A clean refinement test needs the same realized submersion at
both grids and that has not been run.

**The constant-offset model is not confirmed by these numbers.** Taking the deficits as a
pressure over the 2.1662 m2 horizontal cross-section gives 2747 Pa (g64 coupled), 5444 Pa
(g64 fixed), 3613 Pa (g96 coupled) and 3967 Pa (g96 fixed). Those are not a
resolution-independent constant, and none is the roughly 6.2 kPa the section above
reports from job 3361504's direct pressure profile. The two measurements may be probing
different things, the probe being a direct profile read and this being a force residual,
but the discrepancy is unresolved and is recorded here rather than smoothed over.

**Rungs (c) and (d) remain unattempted**, and the guidance above not to advance the
ladder still stands. What changed is the reason: it is no longer that rung (b) has no
valid measurement, because it now has four. It is that the deficit rung (b) exposes is
unexplained and is not specific to the coupling path the ladder was built to test.

---

## The matched-submersion design: the COUPLED path is grid-converged, the FIXED one is not

Same allocation 3362208, later the same session. Artifacts in
`realism_track/rung_b_matched_submersion_3362208/`, drivers `run_matched_sub.sh` and
`run_matched_2x2.sh`.

The section above closes on an explicit caveat: the four-row refinement pair moves
realized submersion with the grid (0.754 at g64 against 0.844 at g96), so it is a
refinement comparison with a second variable in it. That caveat is now resolved, and
resolving it changes the reading.

### Ten gate-met points, submersion varied independently of grid

Submersion is moved with `--depth-cells` at fixed grid. Every row below is
`settle_gate_met true`.

| grid | mode | frac_sub | err vs partial |
|------|---------|----------|----------------|
| 64 | coupled | 0.7540 | -25.21 % |
| 64 | coupled | 0.8567 | -30.16 % |
| 64 | coupled | 0.8572 | -30.20 % |
| 96 | coupled | 0.7800 | -24.96 % |
| 96 | coupled | 0.8437 | -29.64 % |
| 64 | fixed | 0.7548 | -49.92 % |
| 64 | fixed | 0.8564 | -45.16 % |
| 64 | fixed | 0.8573 | -45.22 % |
| 96 | fixed | 0.7757 | -29.88 % |
| 96 | fixed | 0.8445 | -32.51 % |

### The comparison, with grid isolated

Fitting the g64 rows against `frac_submerged` and evaluating that fit at each g96 row's
realized submersion, so grid is the only thing left differing:

| mode | at frac | g64 interpolates | g96 measures | grid gap |
|------|---------|------------------|--------------|----------|
| coupled | 0.7800 | -26.47 % | -24.96 % | **1.51 pts** |
| coupled | 0.8437 | -29.54 % | -29.64 % | **0.10 pts** |
| fixed | 0.7757 | -48.95 % | -29.88 % | **19.07 pts** |
| fixed | 0.8445 | -45.76 % | -32.51 % | **13.25 pts** |

**The free-rigid force-coupled path is grid-converged between g64 and g96, to 0.10 and
1.51 points. The fixed SDF collider is not, by 13.25 and 19.07 points.**

### What this corrects in the section above

The section above reports that under refinement "the fixed collider improves sharply,
the coupled path degrades slightly", from -25.21 to -29.64 percent. **The coupled
path does not degrade under refinement.** That apparent degradation was entirely the
submersion confound the same section flagged: at fixed grid, moving submersion 0.754 to
0.857 moves the coupled error -25.21 to -30.16, and g96 at 0.844 sits exactly on that
g64 curve. The coupled error is a function of submersion, and essentially not of grid.

The convergence between the two paths at g96 is real but its mechanism is the reverse of
the natural reading. The two do not meet at a shared physical answer. **The fixed
collider is converging toward the coupled path's already grid-stable value.**

### What this does and does not say about the coupling

It does NOT say the coupled path is correct. It carries a large residual deficit at every
point measured, about -25 percent at frac 0.78 rising to about -30 percent at frac 0.86,
and that deficit is the unexplained physics. What it says is narrower and still
important: **that deficit is grid-converged, and it is not a resolution artifact of the
coupling.** The 30 percent is a real property of this scheme at partial submersion, not
something a finer grid will remove.

It also inverts the working framing this ladder was built on. Treating the force-coupled
path as the broken one and the fixed SDF collider as the trustworthy baseline is not
supported at partial submersion. On grid convergence the ordering is the other way round,
by more than an order of magnitude in the gap.

### A driver property worth knowing before anyone repeats this

**Submersion is quantized.** `--depth-cells` 18.78 and 18.89 both realize frac 0.856 to
0.857 at g64, a 0.0009 spread across a 0.11-cell request, because water is seeded in
whole layers. Requested depth-cells cannot be used to land on an arbitrary submersion,
which is why the comparison above interpolates the g64 curve rather than trying to hit
g96's submersion exactly. The two near-duplicate g64 rows at 0.8567 and 0.8572 are a
useful side effect: they are an effective repeat measurement, and they agree to 0.04
points (coupled) and 0.06 points (fixed), which bounds run-to-run scatter well below
every gap discussed here.

---

## The regime ladder at the GATED geometry: rungs (b), (c) and (d) all ran and all met the gate

Allocation 3362208, LS6 A100. Driver `simulation/validate_coupling_force_ladder.py`,
byte-identical to the `origin/main` copy. Artifacts in
`realism_track/ladder_gated_geometry_3362208/`, wrappers `run_ladder_bc.sh`,
`run_ladder_bc2.sh`, `run_ladder_d.sh`.

**This is a DIFFERENT experiment from everything above.** `rung_b_settled.py` floats a cube
mid-water at frac 0.75 to 0.86. This ladder puts the body's bottom face ON the floor at
frac 0.20, with `water_depth_m` 0.2944294473039918 and 4 water layers, which are the
`g64_m1100` gated values to the last digit. It is the regime the 17 gated runs actually
occupy. Predictions were pre-registered in the module docstring before any of this ran.

### The settle cap was too low here too, and raising it changed nothing material

At the default 1200-frame cap both rungs were `settle_is_discard true`, ratio 13.78 and
12.40 against 20. Raised to 5000, rung (b) meets the gate at 3490 frames (ratio 22.02)
and rung (c) at 1843 (20.69). **This is the third distinct place in this project where a
settle cap, not the physics, produced a discard.** The measured numbers moved barely at
all between the discard and gate-met versions, which is itself worth knowing: the cap
defect was real but was not driving these particular results.

### Results, all gate-met

| rung | contact | a_ideal | a_late | a_late / ideal | v_mean_late | vertical travel |
|------|---------|---------|--------|----------------|-------------|-----------------|
| (b) | none | -6.7550 | **+28.3986** | -4.2041 | -1.5854 m/s | -0.21208 m (1.44 dx) |
| (c) | floor rest. 0.05 | -6.7641 | +0.0042 | -0.0006 | -0.0441 m/s | -0.03660 m (0.25 dx) |
| (d) | (c) + flow 1.5 m/s | -6.3459 | +0.0253 | -0.0040 | -0.0408 m/s | **0.00000 m** |

Rung (d)'s flow reached the body: water `vx` near the box goes from mean 0.0018 to
0.8304 m/s (p95 1.0756) over 2735 particles, `flow_reached_body true`, at the gated
`velocity_ms` 1.5.

### PREDICTION (b): REFUTED

The docstring pre-registered `a_late ~ 0` with a sustained drift of order -0.13 m/s,
explicitly bounded to -0.09 to -0.17 as an order-of-magnitude claim. Measured drift is
**-1.5854 m/s, about 12x the prediction and far outside the stated band**, and `a_late`
is **+28.4 m/s2**, neither zero nor negative. The dry-fraction fixed-point model behind
that prediction does not describe this configuration.

There is a reason to treat rung (b) here as degenerate rather than merely wrong. At frac
0.20 with `rho_box` 600 the body is far denser than the displaced water can support, so
it must sink, and with every plane at restitution 0.0 nothing can hold it: it ends at
`box_bottom` 0.2319 against `floor_z` 0.4416, **below the floor plane**. The +28 m/s2 is
read from a body that has left the physical domain. Rung (b) at this geometry has no
equilibrium to measure.

### PREDICTION (c): CONFIRMED

The docstring predicted that registering the floor at restitution 0.05 would arrest the
descent and collapse the drift toward zero. It does, decisively: travel falls 0.21208 to
0.03660 m (**82.7 percent**), drift falls 1.5854 to 0.0441 m/s (**97.2 percent**), and
`a_late` falls from +28.4 to +0.0042 m/s2, which is **0.06 percent of the analytic
buoyant value**.

### What rungs (c) and (d) mean for the 17 gated verdicts

In the gated configuration, with the gated floor contact and then the gated flow, the
body's vertical acceleration is 0.06 and 0.40 percent of analytic and its vertical travel
is 0.037 m and then exactly 0.000 m. **The floor contact, not the buoyancy coupling,
determines the vertical dynamics in the regime the 17 runs occupy.** A body resting on a
floor is held by the floor, and the roughly 30 percent buoyancy deficit measured in the
floating-cube experiments above has very little leverage on it.

**This does NOT clear the verdicts, and the reason is a hard limitation of this
instrument.** The ladder records vertical quantities only: `box_bottom_travel_m`,
`v_series` and `zb_series` are all z. There is **no horizontal displacement, no surge
drift and no x velocity anywhere in its output**, so it cannot produce, refute or bound a
SLIDE outcome, and SLIDE is what 16 of the 17 verdicts are. Rung (d) adds flow and
confirms the flow reaches the body, but what that flow does horizontally is not measured.
Closing the loop to the gated verdicts needs a horizontal-drift instrument this ladder
does not have.
