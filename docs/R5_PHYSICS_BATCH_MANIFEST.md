# D4 batch manifest: ready to fire the moment the TACC socket warms

2026-08-16. Branch `claude/r5-physics`. Nothing here has been run. Every pass criterion is
stated **before** the run, so no result can be graded after the fact.

Companion script: `simulation/r5_physics/prestage_jobs.sh`, which carries the same commands
in runnable form and refuses to do anything without `--go`.

---

## 0. The headline, because it changes the triage question

**SU is not the binding constraint. Wall clock and socket availability are.**

The entire queue below costs about **1.6 node-hours**. Vista has **629 SU remaining**
**[recalled]**. Even if the SU-per-node-hour rate is ten times what I assume, the whole
queue is under 3% of the allocation. So the answer to "which would you drop if the
allocation runs short" is: **on SU grounds, none of them.** A drop order is given in
section 5 anyway, in case the rate assumption is wrong.

Two things I could not verify from this host and am flagging rather than asserting:

1. **The SU-per-node-hour rate.** I have no primary source for it tonight. Costs below are
   quoted in **node-hours**, which is what I can actually derive. Confirm with
   `tacc_alloc_status` on first contact and multiply.
2. **The throughput anchor is from an LS6 job, not Vista.** It comes from
   `data/g128_canonical_2026-08-13/00_provenance.txt` **[measured]**: `start=10:57:44` to
   `ALLDONE end=11:03:57` is **373 s for 6 runs** (3x g96 + 3x g128) on
   `c301-001.ls6.tacc.utexas.edu`, giving **8.88e6 particle-substeps/s** including per-job
   startup. Vista GH200 is different hardware, so treat this as a planning number good to
   maybe a factor of 2 to 3. It does not matter: at a 10x error the queue is still trivial
   against 629. **Every job below prints a timing line first so the estimate self-corrects
   on contact.**

### Batch into few jobs, because startup dominates the small runs

The `warpmpm` import measured **78.9 s on a compute node** and blocks entirely on login
**[recalled]**. Per-job overhead is therefore ~80 to 120 s. The brake sweep is **45 s of
compute**, so submitting it as its own job would spend more than twice its own cost on
startup. **J1 and J2 are deliberately fused into one job for that reason.**

### Two hard constraints on every command below

- **`sim_standing.py` is never edited.** Its sha256 is
  `4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9`, verified live on the
  Mac copy tonight and matching the hash stamped in the g128 provenance **[measured]**.
  Editing it invalidates the provenance of every published run.
- **There is no `--settle-frames` and no `--seed` CLI flag** **[measured]**: `settle_frames=8`
  is a constructor keyword only. Any settle override must go through a **wrapper subclass**,
  which is how D5 did it. Do not "just add a flag": that is an edit to the driver.
  Consequently **every job below runs at the canonical settle of 8**, and that limitation is
  stated in each pass criterion rather than hidden.

### Paths, to be confirmed in the first 5 seconds of contact

```
python : /work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/.venv/bin/python
engine : /work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/src
driver : /work/11603/jcerrell0629/vista/can-it-ford/renders/yaris_render_s1/sim_standing.py
```

The python and engine paths are **[read]** from `tacc_env_probe` output this session
(`is_stub: false`, `VERDICT: usable`). The driver path is **[inferred]** by analogy and is
the one thing to check first:

```
ls -l  /work/11603/jcerrell0629/vista/can-it-ford/renders/yaris_render_s1/sim_standing.py
sha256sum /work/11603/jcerrell0629/vista/can-it-ford/renders/yaris_render_s1/sim_standing.py
```

If that sha256 is not `4696c3b2...`, **stop and report it** rather than running: it would
mean Vista's driver differs from the one that stamped the published runs.

---

## 1. JOB A: brake state and repeats (fused). Fire this first.

**Why first.** It is the cheapest job in the queue by an order of magnitude, and it is the
only one that converts a currently **INFERRED** claim into a measurement. It also serves
two separate queued items with the same runs.

```
tacc_submit(
  host      = "vista",
  nodes     = 1,
  walltime  = "00:45:00",
  cwd       = "/work/11603/jcerrell0629/vista/can-it-ford",
  logfile   = "/work/11603/jcerrell0629/vista/d4_jobA/jobA.out",
  command   = "bash /work/11603/jcerrell0629/vista/d4_jobA/run_jobA.sh"
)
```

Equivalent sbatch header if submitted directly: `-p gh-dev -N 1 -t 00:45:00`.
`tacc_submit` chooses the partition itself and injects `--overlap`; **do not use idev**,
on the recorded evidence that interactive burned 98.5 to 99.1% of Vista node-hours with 95
of 184 runs ending in TIMEOUT **[recalled]**.

### A1. Brake-state sweep, 3 runs, ~45 s compute

Target `sweepV_g64_v0p5`, whose canonical arguments are **[measured from its
`summary.json`]**: depth 0.30, velocity 0.5, grid 64, mass 1100, eta 1.0e-3, frames 90.

```
for MU in 0.55 0.30 0.0250; do
  $PY $DRIVER --label brake_mu${MU} --out $OUT/brake_mu${MU} \
      --depth 0.30 --velocity 0.5 --grid 64 --mass 1100 --eta 1.0e-3 \
      --frames 250 --floor-friction $MU --vehicle yaris
done
```

**250 frames, not 90, and that is a direct consequence of my own blocking result**: 24% of
the canonical 91-frame `vmag` series hit the transient-search cap (corrected from a pooled
41% that wrongly included `dmag`), and 0 of 17 reach a trustworthy blocking plateau at 91 frames **[measured]**.

**Comparison and pass criterion, fixed in advance.**

| mu | prediction, stated now | grading |
|---|---|---|
| 0.55 | **STUCK**, reproducing the canonical verdict | if this does not reproduce, the whole job is void and nothing else in it may be read |
| 0.0250 | **SLIDE** | this is the test of the INFERRED claim |
| 0.30 | **not predicted** | logged as indeterminate in advance; the bracket (0.369, 0.739] straddles the run's 0.5 m/s, so **either outcome confirms nothing and neither may be reported as a success** |

The mu = 0.30 row is the important one to have written down beforehand. Without it, either
result could be narrated as agreement after the fact.

**Secondary check, free:** the mu = 0.55 arm at 250 frames against the canonical 90-frame
verdict is also a settle-length control. If the verdict differs, that is a finding about
run length, not about brake state, and must be reported separately.

### A2. Repeats for the N = 1 problem, and the P2G order-dependence test, from the same runs

All 17 canonical runs are single draws against a determinism floor spanning 0.52 to 1.69 m
**[recalled]**. Repeats at **fixed configuration, identical arguments, no seed change**
(there is no seed flag anyway):

```
for i in 1 2 3 4 5 6 7 8 9 10; do
  $PY $DRIVER --label rep_g96m2337_$i --out $OUT/rep_g96m2337_$i \
      --depth 0.30 --velocity 1.5 --grid 96 --mass 2337 --eta 1.0e-3 \
      --frames 250 --floor-friction 0.55 --vehicle yaris
  $PY $DRIVER --label rep_v0p5_$i --out $OUT/rep_v0p5_$i \
      --depth 0.30 --velocity 0.5 --grid 64 --mass 1100 --eta 1.0e-3 \
      --frames 250 --floor-friction 0.55 --vehicle yaris
done
```

Targets chosen because they are the two boundary cases: `g96_m2337` sits at a **one-frame**
margin and `sweepV_g64_v0p5` is the only STUCK **[recalled]**. Repeating comfortable runs
measures nothing.

**These same runs answer the P2G order-dependence question at no extra cost**, which is why
items 3 and 4 are one job and not two. The discriminator is **when** two identical runs
first differ:

- differ at **frame 1**: an unordered non-associative reduction, which is the cited
  mechanism (`10.3390/app14020639`, `10.1016/j.parco.2019.04.002`) and which can alter
  discrete gates;
- identical at frame 1, diverging **later**: accumulation and amplification, not reduction
  order;
- **bitwise identical throughout**: the P2G reduction is deterministic and the determinism
  floor has some other source, which would itself be a significant negative result.

**Pass criterion:** report, in this order, (a) the divergence-onset frame, (b) the spread of
`max_surge_drift_m` across the 10 repeats **with N and range, never a single draw and never
a ratio**, and (c) **gate-pass frequency out of 10, not pass or fail**. No verdict from this
job may be reported as a binary.

**Cost:** ~16 min compute at n = 10, ~8 min at n = 5. Plus A1's 45 s. Call it **0.3
node-hours** with startup.

---

## 2. JOB B: Kramer sphere hydrostatic pilot. Fire second.

**Why second.** It is the first external validation the project would have, it has a fully
specified pass criterion available **right now**, and it self-measures throughput so
everything else can be re-costed.

```
tacc_submit(
  host      = "vista",
  nodes     = 1,
  walltime  = "00:45:00",
  cwd       = "/work/11603/jcerrell0629/vista/can-it-ford",
  logfile   = "/work/11603/jcerrell0629/vista/d4_jobB/jobB.out",
  command   = "bash /work/11603/jcerrell0629/vista/d4_jobB/run_jobB.sh"
)
```

```
$PY simulation/r5_physics/sphere_heave.py --fixed \
    --n-grid 64 --lim 1.2 --depth 0.5 --h0-over-d 0.0 \
    --frames 200 --sdf-res 96 --verbose \
    --out /work/11603/jcerrell0629/vista/d4_jobB/sphere_fixed_g64.json
```

Scene: dx = 0.01875 m, 16 cells across the sphere, **598,505 water particles** after the
carve, **82 substeps**, 200 frames **[measured by replicating the seeding block]**. The
earlier figure of 606,814 was wrong: it exceeded even the uncarved lattice ceiling of
606,797. Cost impact 1.4%.

**Domain corrected 2026-08-16.** `lim = 1.2` buys only **1.06** clean natural periods on
Kramer's own phase-celerity convention, not the 2.12 first claimed on a group-velocity
convention the benchmark explicitly rejects (section 3.5, p.16). Job B is kept at
`lim = 1.2` deliberately, as a **cheap hydrostatic pilot where reflections do not matter**:
the sphere is pinned and the quantity is a steady reaction, not a decay. **Job C cannot use
this domain** and is re-specified below.

**Comparison number:** analytic buoyancy on the submerged hemisphere at Table 1's
`rho_w = 998.2` and the engine's `g = 9.81`, which is **69.2180 N** **[derived, asserted by
the committed test suite]**. Note this is **not** 69.3428 N: that was the superseded
`rho_w = 1000` derivation.

**Three cautions on 69.2180 N, added 2026-08-19 by slot `d11-accessor`:**

1. **It is a HEMISPHERE, not a fully submerged sphere.** `2/3 pi R^3` is half of
   `4/3 pi R^3`. A fully submerged sphere would be **138.4360 N**. Describing 69.2180 N as
   a fully-submerged buoyancy is wrong by a factor of two and has been done in dispatch
   text before.
2. **It is also the sphere's own weight, by construction of the benchmark.**
   `m*g = 7.056 * 9.81 = 69.2194 N`, against 69.2180 N here, a 0.002% gap that the emitted
   config records as `ref_mass_route_disagreement_kg = 0.00014`. Kramer chose the mass so
   the sphere floats at its equator, so the design-waterline buoyancy and the weight
   coincide. That is why this number is meaningful, and it is not a coincidence to be
   re-derived independently each time.
3. **As of the 2026-08-19 amendment, 69.2180 N is the COMPANION number, not the graded
   one.** Criterion 3 below grades `fz_over_analytic_measured`. 69.2180 N is still reported
   with every run and is still required; it is no longer what the band is computed from.
   See `docs/R9_ACCESSOR_DEFECT_2026-08-18.md` for why.

**Pass criteria, fixed in advance and graded in this order.** Any FAIL stops the ladder:

1. **The collider is accepted.** `add_sdf_collider` refuses a collider whose stored SDF does
   not clear `band = dx`. The margin logic is asserted on the Mac at every planned
   resolution, so a refusal here means the Vista engine differs from the vendored copy.
2. **The SDF matches the closed form.** `sdf_radius_rms_err_m` must be small against
   `sdf_cell_m`. A sphere's SDF is exactly `|x| - r`, so this is a check no vehicle hull
   permits. **This grades the builder, not the physics.**
3. **The steady vertical reaction, graded on `fz_over_analytic_measured`**, with a
   **blocked** standard error from `blocking.py`, not a raw standard deviation. Prior
   expectation from the box-SDF path is 7.3 to 7.7% **[recalled]**, so: **within 10% is a
   PASS, 10 to 25% is a REPORTABLE PARTIAL, beyond 25% is a FAIL.** These bands are set now
   and will not be moved.

   **AMENDED 2026-08-19 by slot `d11-accessor`. The bands are untouched; what changed is
   that the criterion now names WHICH quantity and OVER WHAT WINDOW.** As originally
   written this criterion said only "the steady vertical reaction against 69.2180 N", which
   named a denominator but no window, and `sphere_heave.py` designated a *different*
   denominator in a source comment. Two quantities were live under one criterion and the
   comment, not this manifest, is what downstream tools followed. Full working, the
   downstream inventory, and the evidence for every figure below:
   `docs/R9_ACCESSOR_DEFECT_2026-08-18.md`.

   - **Graded quantity:** `fz_over_analytic_measured` = `fz_N` divided by
     `analytic_buoyancy_at_measured_surface_N`, that is Archimedes on the spherical cap
     actually submerged at the free surface the run actually has. **Not** 69.2180 N. The
     sphere is pinned (`mode = fixed`) and the tank drains, so 69.2180 N is the reaction at
     a waterline that did not exist during the measurement. This criterion's own prior, the
     7.3 to 7.7% box-SDF figure, is a *coupling* accuracy prior, and only this quantity
     isolates coupling accuracy; the nominal ratio is coupling error and drainage combined,
     and they partly cancel.
   - **Primary window:** the last 50% of frames. Fixed in advance rather than chosen from
     the data, the coarsest defensible transient exclusion, and already what
     `grade_job_b.py` applies as `DEFAULT_DROP_FRAC`.
   - **Window-robustness gate.** The band must be identical at last-20, last-50, last-100
     and full-series. If it is not, the run is **NOT GRADEABLE on window sensitivity** and
     that is reported, never resolved by picking a window. Measured: the nominal ratio
     swings FAIL / PARTIAL / PASS across those four windows on jobs 917909, 918043 and
     918240, a 19.4-point spread, and job 918240's nominal reading crosses a band edge at
     frame 163 of its own 200-frame run. The graded ratio spans 1.1 to 3.1 points.
   - **Stationarity gate, on the GRADED RATIO only, at 3.0 sigma.** Non-stationarity of the
     raw `fz_N` series is expected and is not disqualifying, per criterion 5 below. This
     distinction is what makes criteria 3 and 5 satisfiable at once: measured on jobs
     918043 / 918240 / 918450, `fz_N` is non-stationary at 8.52 / 8.52 / 3.95 sigma while
     the graded ratio is stationary at 0.15 / 0.64 / 1.08 sigma.
   - **Mandatory companion, never suppressed:** the nominal ratio against **69.2180 N**,
     with its own window table, plus `surface_drop_m`. Where the two disagree that
     disagreement IS the finding, because it separates a coupling error from a draining
     tank. Both quantities remain meaningful and neither is deleted.
   - **Standing caveat that travels with any PASS on this criterion.** The denominator
     depends on a free-surface estimate that excludes every particle within 2R of the
     sphere axis, which is exactly where the pressure generating `fz` acts. Measured
     sensitivity is 0.0278 ratio-points per mm of surface, so roughly 1 dx of surface offset
     at g64 spans the entire discrepancy observed to date. **A PASS here is not a coupling
     validation until that estimator is validated in the near field.**
   - **Note on stationarity of a ratio.** A stationary ratio built from two co-trending
     non-stationary series shows that numerator and denominator fall together, not that the
     measurement has settled; `surface_z_measured_m` is non-stationary at 16.9 to 20.0
     sigma. The claim licensed here is only the weaker one that suffices for grading: the
     verdict does not depend on window choice. Convergence remains open.
4. **Lateral force vanishes by symmetry.** `|F_lateral| / |Fz|` should be small; a large
   value means the readout is unsound regardless of whether `Fz` matches.
5. **Stationarity, via `blocking.py`.** Given what blocking found on the C1-SDF series, a
   NOT-STATIONARY verdict here is **expected, not disqualifying**, and must be reported with
   its **drift ratio against the error being claimed**, exactly as in
   `R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md` section 3.

   **Scope clarified 2026-08-19 by slot `d11-accessor`.** This tolerance applies to the raw
   `fz_N` series. It is **not** a licence to grade criterion 3 on a drifting quantity:
   criterion 3 carries its own stationarity gate on the *graded ratio*. Before this was
   distinguished, `grade_job_b.py` refused all four job B runs as `NOT GRADEABLE` on exactly
   the ground this criterion calls "expected, not disqualifying", which is a direct
   contradiction between criteria 3 and 5 and is why no job B run had a top-level band.
   Reporting the drift ratio is where this criterion does its real work: on job 918450 the
   raw series drifts **261%** of the error being claimed against it, which is what exposes
   that run's nominal PASS as a decaying series caught inside the band.

**Explicitly not graded here:** the 0.090 / 0.270 / 0.450 mm per-drop-height tolerances.
Those are **displacement** tolerances and apply only to the free-decay drops in Job C. A
hydrostatic force check cannot be graded against a displacement tolerance, which is the
category error section 3.2 of the test-case doc warns about.

**Cost:** ~19 min, **0.35 node-hours**.

---

## 3. JOB C: Kramer free heave decay, three drops. Fire only after B passes.

**Gated on Job B.** The free-decay path exercises the 1-DOF integrator and `set_sdf_pose`,
neither of which has ever run. If B fails criterion 1 or 3, C is not worth its wall clock.

```
tacc_submit(
  host      = "vista",
  nodes     = 1,
  walltime  = "04:30:00",
  cwd       = "/work/11603/jcerrell0629/vista/can-it-ford",
  logfile   = "/work/11603/jcerrell0629/vista/d4_jobC/jobC.out",
  command   = "bash /work/11603/jcerrell0629/vista/d4_jobC/run_jobC.sh"
)
```

```
for H0D in 0.1 0.3 0.5; do
  $PY simulation/r5_physics/sphere_heave.py \
      --n-grid 64 --lim 1.2 --depth 0.5 --h0-over-d $H0D \
      --frames 200 --sdf-res 96 --verbose \
      --out /work/11603/jcerrell0629/vista/d4_jobC/sphere_h0_${H0D}.json
done
```

**BLOCKER-B1 still applies and it changes how this is graded.** The raw benchmark time
series is MDPI Supplementary Materials at `/s1`, 403 from two independent hosts. **Without
it, the published-comparison criterion cannot be evaluated at all.** So Job C has two
criterion sets and only the first is available today:

**Available now, self-consistency only:**

- **Reflection window respected.** Wall reflections return at 1.649 s = 2.12 natural periods
  at `lim = 1.2` **[derived]**. Only cycles before that may be used. Any period or decay
  quoted from beyond frame ~50 is contaminated by construction.
- **Natural period consistent across the three drops**, and increasing with drop height,
  which is the paper's own Figure 13 finding **[read]**. This is a **direction** check, not
  a magnitude one.
- **Mach reported per drop**: 0.019 / 0.057 / **0.094** **[derived]**. The 0.5D case sits at
  the weak-compressibility edge and its Mach must travel with any number from it.
- **Equilibrium recovered**: the sphere should settle toward half submergence.

**Requires `/s1`, and is deferred until it arrives:**

- **CRITERION CORRECTED 2026-08-16 before the job ran; the original was unworkable.**
  Kramer **Table 4, p.17** gives the **measured** drop heights as
  **{29.16, 89.18, 150.06} mm**, not the nominal {30, 90, 150}, and p.21 states results are
  normalised "with respect to the measured drop height in each repetition". At 0.1D the
  nominal-versus-measured gap is **0.84 mm, which is 9.6x the 0.090 mm tolerance** the
  original criterion proposed to grade against. Grading absolute displacement at nominal
  `H0` was therefore incoherent.
  **Corrected criterion:** compare on **normalised** `x3/H0`, or on absolute displacement
  with each run's `H0` set to its **measured** value. The tolerances remain
  **0.090 / 0.270 / 0.450 mm**, still an **average at 95% confidence** rather than a
  per-sample envelope **[read]**. This is exactly what fixing criteria in advance is for:
  the error was caught before the run, not after it.
- The irreducible **+0.051%** period bias from `g = 9.81` against the benchmark's 9.82 must
  be stated beside any period comparison **[derived]**.

**Cost:** ~221 min, **3.7 node-hours** at the corrected `lim = 2.2` domain, up from 1.0 at the retracted `lim = 1.2`. Needs the `gh` partition, not `gh-dev`. This is by far the most expensive item and the only one that
cannot be fully graded on arrival.

---

## 4. Nothing goes to LS6

LS6 is x86 with no usable `warpmpm` **[recalled]**, so no item in my scope can run there. I
have no pysplashsurf or Chrono work queued; if those paths want exercising, they belong to
whoever owns render, not to D4.

---

## 5. Order, and what I would drop

| # | job | node-hours | converts | drop rank |
|---|---|---|---|---|
| 1 | **A1** brake sweep | ~0.02 | an **INFERRED** claim into a measurement | **never drop** |
| 2 | **A2** repeats + P2G | ~0.28 | N = 1 into spread and gate-pass frequency | drop n = 10 to n = 5 first |
| 3 | **B** sphere hydrostatic | ~0.35 | no external validation into one | drop frames 200 to 120 |
| 4 | **C** sphere free decay | ~3.7 | nothing gradeable until `/s1` arrives | **drop this first** |

**Total ~4.3 node-hours**, up from 1.6 after Job C moved to the corrected domain. Still under 1% of the allocation at 1 SU per node-hour, so the conclusion that SU is not the binding constraint is unchanged.

**Drop order: C, then A2's repeat count, then B's frame count. A1 is never dropped**: it
costs 45 seconds and it is the only item that resolves a claim currently standing on
inference. If only one thing runs, run A1.

**C is the first drop for a reason that is not cost**: it is the only job whose primary pass
criterion cannot be evaluated on arrival, because `/s1` is still blocked. Running it before
the data exists produces a result nobody can grade, which is the failure mode this whole
manifest is written to prevent.

---

## 6. Status

Nothing here has run. The STUCK-to-SLIDE flip stays **INFERRED** until A1 measures it.
Everything in this manifest and in every document it references is **UNREVIEWED**: no
physics-skeptic pass has run.
