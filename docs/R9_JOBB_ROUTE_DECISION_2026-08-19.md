# Job B: is the FAIL a solver defect or an instrument artifact? The route for job C

Slot d21-jobb, branch `claude/r9-jobb-route`, 2026-08-19.
Scope: this document and `analysis/r9_jobb_estimator_test.py`. `sphere_heave.py`,
`grade_job_b.py`, the manifest and `r7_jobb_bcfix_ab.py` are NOT touched.

**This does not re-grade job B and does not re-litigate the verdict.** d11-accessor owns
that and has recorded it: 24 of 24 gradings FAIL, +34.4 to +64.2 percent, recomputed from
raw geometry, nominal denominator reproducing to 69.217987 N. That stands here unaltered.
The question this document answers is a different one: **WHERE the FAIL lives.**

---

## 1. The answer, before the working

**Four findings, three of which are settled and one of which is pending a run.**

1. **The 2R exclusion is a DELIBERATE, DOCUMENTED TRADE, not an oversight.** The docstring
   states its reason. Whether the trade is correct for this denominator is a separate
   question and is the one still open.

2. **No existing run can separate the estimator from the contact band, and I measured the
   degeneracy rather than assuming it.** Over the 8 distinct `band_mult = 1.0` fixed-sphere
   simulations, "the collider is inflated by `k*dx`" and "the surface is under-read by
   `k*dx`" fit the measured force EQUALLY WELL with one global parameter each: RMS relative
   force error **3.36 percent** and **2.76 percent** against a no-correction RMS of 27.75
   percent. The estimator model fits marginally BETTER. **The hypothesis this unit was sent
   to test is not merely alive; on all existing evidence it is the slightly better fit.**

3. **THE PRE-REGISTERED TEST IS SUBMITTED AND ITS THRESHOLDS ARE FIXED.** Vista batch job
   **922584** and **922585**, five runs including a smoke test and a no-body control. The
   result is recorded in section 7 whichever way it falls.

4. **Criterion 3 has the P-2 pathology on the PASS side and NOT on the FAIL side, and this
   is now quantified.** At the state job B actually occupies at g64, a one-particle-layer
   ambiguity in the free-surface location is **13.7 percent of the ratio**, which exceeds
   the entire 10 percent PASS band; a half-layer ambiguity is 6.85 percent, 68 percent of
   it. **A PASS at g64 could not have been informative.** But the observed excess is 5.0x
   to 9.4x the half-layer floor, so **the FAIL is outside the floor by a wide margin and
   remains informative.** That asymmetry is the practically important result and it does
   not depend on which explanation wins.

**Two things the coordinator's framing gets wrong, both checkable in one command each**,
and both are stated here because acting on them would have wasted the run:

- **The restitution path is not in this scene at all.** `add_sdf_collider` takes no
  restitution argument (`mpm_solver_warp.py:2621-2624`, read live on the pinned Vista
  engine); `_apply_rigid_restitution` at `:887` fires only for registered plane colliders
  with `e > 0` (`:1915` gates the registration on `restitution != 0.0`), and
  `sphere_heave.py:577-581` registers all five planes at `restitution=0.0`. The
  restitution=0.05 that is live in the 17 canonical vehicle runs is a different scene and a
  different code path. **There is nothing to test here, and the dispatch's explanation 3(b)
  should be struck rather than investigated.**
- **The band sweep does NOT refute the estimator, and saying it does is a specific,
  already-caught error.** I nearly made it. `docs/R5_PHYSICS_JOB_B_RESULT.md` section 13.1
  states the rule correctly: an experiment that holds `dx` fixed has ZERO POWER over a
  `dx`-scaling rival. The band sweep held `dx` fixed. See section 3.

---

## 2. What `measure_surface` actually says, quoted in full

Read live from `simulation/r5_physics/sphere_heave.py:690-693` at branch head
(sha256 `6ab8cec5fa2acac226954d9a5218fa3de841da1f7ef0a175789a1d4212396a84`, which is
byte-identical to the copy staged on Vista at `d4_scene/sphere_heave.py`):

> Particles within 2R of the sphere axis are excluded: that annulus carries the
> meniscus and any splash off the collider, which is a local deformation and not
> the tank's free surface. The 99th percentile rather than the max, because a
> single ejected particle should not define a surface.

**This is a reasoned trade, correctly documented, and it is defensible on its own terms.**
For the Archimedes closed form `rho*g*V_cap(surface)` the relevant level IS the undisturbed
far-field surface, because the closed form assumes a flat free surface. Excluding a local
meniscus is the right thing to do for that formula.

The trade becomes questionable only if the excluded annulus contains not a meniscus but a
genuine, sustained elevation of the water that the body is actually resting on, in which
case the far field is not the level setting the pressure at the body. **Nobody has
measured which it is**, because no run has ever reported the surface inside the annulus.

Two further facts about the estimator, both read directly, both relevant:

- The `+0.5*self.h` fill-line offset was added 2026-08-18. It is worth exactly `h/2`,
  which is 4.6875 mm at g64. I can confirm it independently: `d4_jobB_918043` and
  `d4_jobB_918240` are the same simulation (per-frame `|dFz|` never exceeds 1.5e-3 N) and
  their frame-0 surface readings differ by **4.687 mm**, to three decimal places `h/2`.
- The literature does not treat near-body exclusion as benign. The deep search
  commissioned for this exact question
  (`free surface elevation estimator error in particle method buoyancy validation`,
  workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`, completed) concludes: "Near-body
  exclusion is not established as a benign operation", and independently recommends the
  three diagnostics this unit had already designed: nested exclusion radii including zero,
  local vertical columns, and a body-off hydrostatic run. That is convergence on a test
  DESIGN, not corroboration of a result, and it is reported as such.

---

## 3. The measurement that decides what run to spend money on

`analysis/r9_jobb_estimator_test.py offline <dir>` reproduces everything in this section.

### 3.1 There are 10 distinct simulations on Vista, not 18 files

18 `sphere_heave` payloads exist under `$WORK`. Twelve carry the `surface_z_measured_m`
column and are gradeable. Of those twelve, **seven pairs are the same simulation
re-executed**: per-frame `|dFz|` never exceeds 1.4e-4 of the 69.218 N target, against a
minimum of 6.7e-2 for any genuinely distinct pair. The distribution is bimodal by a factor
of 480, so the duplicate threshold is not a tuned number. Grouping is by transitive closure
because without it the partition depends on file order.

**10 distinct fixed-sphere simulations survive, 8 of them at `band_mult = 1.0`.** The
evidence base is materially smaller than the file count suggests. This is consistent with,
and extends, sections 10.1 and 13.3 of the job B result, which caught two of these pairs.

### 3.2 The two live models are near-degenerate, and the estimator fits slightly better

One global parameter each, fitted to the measured `fz` of every distinct run, last-50-frame
window. `V_cap` is the same closed form `sphere_heave.buoyancy_at` uses, clamp included.

| model | ALL 10 runs | `band_mult = 1.0` only, 8 runs |
|---|---|---|
| NULL, no correction | RMS 30.88% | RMS **27.75%** |
| BAND, collider radius and submergence both `+ k*band` | k=0.8605, RMS 3.56% | k=0.8400, RMS **3.36%** |
| SURFACE, `surf += Delta` (resolution-independent) | 20.6 mm, RMS 14.53% | 21.3 mm, RMS 6.50% |
| SURFACE, `surf += k*dx` | k=1.2915, RMS 13.89% | k=**1.3875**, RMS **2.76%** |

**Read the right column.** On ALL runs the BAND model wins by a factor of four, but that
comparison is decided by the two band-sweep arms, and per section 13.1 those arms have no
power over a `dx`-scaling rival. On the `band_mult = 1.0` subset, where both mechanisms
have power, **the surface model fits better than the band model** (2.76 against 3.36
percent). The difference is not significant on 8 points and I do not claim it is. The
correct statement is that **the two are indistinguishable on all data that exists**, and
that the estimator hypothesis is not a long shot.

`k = 1.3875` means the surface model needs the true surface to sit **26.0 mm above the
far-field estimate at g64** (1.39 dx), 17.3 mm at g96, 13.0 mm at g128. Those are the
numbers the run has to confirm or refute.

### 3.2a How demanding is E1? A ceiling that was already in the payloads

`water_z_max_m` is the height of the single highest water particle **anywhere, including
the annulus the estimator discards**. A 99th percentile over a subpopulation cannot exceed
the population maximum, so this is a hard ceiling on any near-field surface, and it has
been sitting in every instrumented payload since `water_budget` was added.

It is an EXTREMAL quantity. Per CLAUDE.md it is used here **only as a bound**, never for a
trend and never for a convergence claim, which is why the table below is not ordered by dx
and no slope is fitted to it.

| run | n_grid | E1 needs | ceiling | needs/ceiling |
|---|---|---|---|---|
| bcfix n128 | 128 | 13.01 mm | 25.71 mm | 0.51 |
| bcfix n96 | 96 | 17.34 mm | 27.78 mm | 0.62 |
| jobBbig | 117 | 26.09 mm | 42.20 mm | 0.62 |
| bcfix n64 / combo ghost0 | 64 | 26.02 mm | 31.23 mm | 0.83 |
| band1.0 / ghost0 (leaky floor) | 64 | 26.02 mm | 30.11 mm | 0.86 |

**E1 is not ruled out.** But it requires the annulus 99th percentile to reach **51 to 86
percent of the way to the tank's single highest particle**. A 99th percentile that close to
a global maximum describes a **flat elevated shelf, not a meniscus and not a splash**,
which is the opposite of what the docstring assumes is in there. That is a sharper form of
the hypothesis than "the estimator might be biased", and it is what makes the radial
profile, rather than a single near-field number, the informative output. This bound is
superseded the moment run 1 lands, because run 1 measures the percentile directly.

### 3.3 Why the band sweep cannot settle this, restated so it is not re-derived wrongly

At fixed `dx = 18.75 mm`, changing only `band_mult`, the measured force is
34.644 / 44.729 / 69.106 N at 0.5 / 1.0 / 2.0 dx, and the far-field surface moves by only
3.0 mm across the whole sweep. So the band moves the FORCE, not the surface. That
identifies the band as the source of **band-dependence**, which is what section 13.7 says
survives, and it is all it says.

It does not bound the estimator, because a `dx`-scaling estimator error contributes the
same additive constant to all three arms. Section 13.1 inverted the cap law across the arms
and found a roughly band-independent residual of **-2.75 mm = -0.147 dx**, with the
OPPOSITE sign to a surface under-read. That is a real bound and it is against the estimator
hypothesis at g64 with the leaky floor. It is not decisive, for two reasons: the band-sweep
arms are the leaky-floor configuration (4.93 percent of particles below the floor by frame
299), and the inversion assumes the `R + band` cap law is the correct functional form,
which section 12.1 shows it is not exactly.

---

## 4. E2, the weakly-compressible explanation, is bounded out by two orders of magnitude

Arithmetic, not literature. The bulk modulus is `K = rho*c^2` with the artificially reduced
sound speed `c = 12.8568 m/s` read from the run config, giving **K = 165,000 Pa**. Peak
Mach is 0.0 in the fixed-sphere runs, also from the config, so there is no dynamic term.

| pressure scale | p | strain p/K |
|---|---|---|
| sphere's maximum submergence at the measured surface, 0.114 m | 1116 Pa | **0.68%** |
| the full still-water depth, 0.500 m | 4896 Pa | **2.97%** |

A density error of that size produces a buoyancy error of that size. The observed excess is
34 to 64 percent, which is **11x to 94x** the largest defensible compressibility bias. E2
cannot be the dominant term. It survives only as a contributor to the few-percent residual.

This does not say weak compressibility is harmless in this solver generally: [Che18c],
*v-p material point method for weakly compressible problems*, Computers & Fluids 176:170-181,
2018, doi:10.1016/j.compfluid.2018.09.005 (verified matched against the Crossref record,
high confidence) documents volumetric locking and interface pressure oscillation in WCMPM.
It says compressibility cannot produce THIS magnitude in THIS static configuration.

---

## 5. Can criterion 3 produce an informative PASS at all? Mostly no, and the FAIL survives it

This answers the pathology the coordinator flagged, and it is the most consequential thing
in this document. `analysis/r9_jobb_estimator_test.py floor <dir>` regenerates the table.

The sensitivity is exact, not fitted. `V_cap(sub) = pi*sub^2*(3R-sub)/3`, so
`dV/d(sub) = pi*sub*(2R-sub) = A_w`, the waterplane area, and

    d(ratio)/d(surface) = -ratio * A_w / V_cap

At the g64 bcfix state (`sub = 113.77 mm`, `R = 150 mm`), `A_w/V_cap = 14.605 per metre`,
verified independently by Wolfram Alpha. That is **1.46 percent of the ratio per millimetre
of surface**, at ratio 1.

The free surface in a particle method is only located to within the particle spacing
`h = dx/2`. This is not hypothetical: `measure_surface` itself moved by exactly `h/2` on
2026-08-18 when the layer-centre convention was replaced by the fill-line convention. Both
`h/2` (the spread between conventions this code has actually used) and `h` (the full layer)
are defensible, so both are reported.

| state | dx | h | sub | %/mm | floor at h/2 | floor at h | 10% band / floor(h/2) |
|---|---|---|---|---|---|---|---|
| design, half submerged, g64 | 18.75 mm | 9.38 mm | 150.0 mm | 1.00 | 4.69% | 9.38% | 2.13 |
| design, half submerged, g96 | 12.50 | 6.25 | 150.0 | 1.00 | 3.13% | 6.25% | 3.20 |
| design, half submerged, g128 | 9.38 | 4.69 | 150.0 | 1.00 | 2.34% | 4.69% | 4.27 |
| **g64 bcfix, as run** | 18.75 | 9.38 | 113.8 | 1.46 | **6.85%** | **13.69%** | **1.46** |
| g64 leaky floor, as run | 18.75 | 9.38 | 89.1 | 1.97 | 9.22% | 18.44% | 1.08 |
| g96 bcfix, as run | 12.50 | 6.25 | 111.3 | 1.50 | 4.70% | 9.39% | 2.13 |
| g128 bcfix, as run | 9.38 | 4.69 | 102.6 | 1.66 | 3.89% | 7.79% | 2.57 |

**The finding, in three parts.**

1. **The floor is much worse at the state job B occupies than at its design point.** The
   surface falls, the sphere becomes less submerged, `A_w/V_cap` rises, and the sensitivity
   nearly doubles. At the leaky-floor configuration the band/floor ratio is **1.08**, which
   is the P-2 pathology exactly: the gate sits on its own floor. Even after the floor BC
   fix it is 1.46.
2. **So a PASS at g64 would not have been informative**, and this should be recorded
   against criterion 3 independently of anything else in this document.
3. **But the FAIL is informative, and this is the asymmetry that matters.** The observed
   excess is +34.4 to +64.2 percent, which is **5.0x to 9.4x** the g64 half-layer floor and
   **2.5x to 4.7x** the full-layer floor. Unlike P-2, where d19-priorcode measured 7.9 to
   10.0 percent against a 10 percent gate and neither outcome could be read, job B's excess
   clears its own floor by a factor of several. **The ladder-stopping decision does not rest
   on a number inside the noise.**

A consequence worth acting on separately: **criterion 3's 10 percent PASS band is only
meaningful at g128 or finer.** At g64 it is 1.5 to 2.1 times the estimator's own resolution.
If a future job is to be graded on this criterion, either the grid has to be finer or the
band has to be widened to something the instrument can actually resolve, and the second
option is a criterion change and must be pre-registered as one.

---

## 6. A control that costs nothing: the estimator at frame 0

At frame 0 the tank has been stepped once and the surface is still flat, so the deficit
against the design waterline `FLOOR + depth = 0.575 m` is close to a body-free reading.
Measured across the clean `band_mult = 1.0`, `ghost = 0` runs:

| run | dx | h | frame-0 deficit | deficit / h |
|---|---|---|---|---|
| bcfix n64 | 18.75 mm | 9.38 mm | 8.78 mm | 0.94 |
| bcfix n96 | 12.50 | 6.25 | 6.24 mm | 1.00 |
| bcfix n128 | 9.38 | 4.69 | 7.81 mm | 1.67 |

**The deficit does not scale with `h`.** It sits at 6 to 9 mm at every resolution while `h`
halves. One tick of free fall from rest is `0.5*9.81*0.03333^2 = 5.45 mm`, which accounts
for most of it. So the estimator is not grossly biased on a flat surface, and the surface
model's required 13 to 26 mm cannot be a static estimator offset that is present from the
first frame. **It would have to be generated by the body.** That is a genuine narrowing and
it is why the near-field measurement, not a flat-tank calibration, is the test.

This control is weak on its own, because frame 0 is after a step and mixes estimator bias
with real settling. Run 2 of job 922584 is the clean version: the sphere pinned 0.3 m clear
of the water for 300 frames, where no body effect is available to explain anything.

### 6.1 The instrument is validated against a planted answer, and that narrows E1 further

`analysis/r9_jobb_estimator_test.py selftest` builds a synthetic particle cloud with a
KNOWN free surface, flat everywhere except the annulus `R < r <= 2R`, where three extra
layers are stacked on purpose. A smoke run proves the code does not crash; this proves the
numbers mean something, which matters because this unit's whole conclusion rests on them.

**IT ALREADY BIT, AND THE BUG WAS IN MY TEST.** The first version planted `FLOOR + DEPTH`
as the far-field answer and reported a 3.26 mm instrument error. The lattice holds an
integer number of layers of spacing `h`, and `0.5 / 0.009375 = 53.33`, so the real fill
line is `FLOOR + 53h = 0.57187 m`, not 0.575. **The 3.26 mm was the test's own rounding,
not the instrument's bias.** Recorded because a wrong instrument-error figure would have
gone straight into the E1 assessment with the right sign to help it.

With the geometry planted consistently:

| quantity | planted | measured | error |
|---|---|---|---|
| far-field fill line, FLAT surface | 0.57187 m | 0.57174 m | **-0.14 mm** |
| annulus fill line | 0.60000 m | 0.60172 m | +1.72 mm |
| near minus far | 28.125 mm | 29.99 mm | **+1.87 mm, 6.7% high** |
| column-max-median route, same flat surface | 0.57187 m | 0.57307 m | +1.20 mm |

**Three things follow, and the second is the most useful.**

1. The exclusion sweep behaves exactly as designed: 0.60159 / 0.60159 / 0.60160 / 0.60150
   at exclusion 0 / 0.5R / 1R / 1.5R, then 0.57174 / 0.57171 / 0.57174 at 2R / 3R / 4R. A
   30 mm step landing exactly on the 2R boundary. That is the signature the real run has to
   show if E1 holds, and the radial profile resolves it into bins.
2. **The two independent estimators differ by only 1.34 mm on a flat surface, which is
   0.071 dx.** The percentile-plus-h/2 route reads 0.14 mm low, the column-max-median route
   reads 1.20 mm high, and their bracket is 1.34 mm wide. At 1.46 percent of ratio per mm
   that is **about 2 percentage points of ratio, not 40**. So **E1 cannot be an estimator
   CONVENTION error.** Combined with section 6, where no 13-to-26 mm static offset is
   present from the first frame, E1 survives only in one specific form: **the body
   genuinely holds up about 26 mm of water in the annulus that the estimator discards.**
   That is now the entire hypothesis, and it is exactly what run 1 measures.
3. **The instrument is biased TOWARD E1** by 6.7 percent of whatever near-field rise it
   measures, because a top-tail statistic on a partially filled top region reads high. An
   E1 verdict has to clear that bias and must be reported with it attached. Against a
   required 26 mm the bias is 1.9 mm, so it does not change the verdict at the
   pre-registered thresholds, but it is stated rather than discovered later.

---

## 7. The pre-registered test: submitted, thresholds fixed before the run

Vista jobs **922584** (40 min, the decisive pair) and **922585** (75 min, the supporting
arms), partition `gh`, account BCS20003. Scripts `run_r9a.sh` and `run_r9b.sh`, with the
scene and test sha256 stamped into each log.

**These replace job 922535, which I cancelled, and the reason is worth recording as a
scheduling fact rather than a footnote.** 922535 asked for 2 hours in one block. `sinfo`
showed the `gh` partition with **560 of 576 nodes allocated**, and `squeue --start` put
922535's estimated start at **16:12 CDT, about 2.7 hours out**, behind nine other users'
pending jobs. A long request can only start when a long window opens; a short one
backfills into gaps that already exist. Splitting the same work into 40 and 75 minutes
costs nothing and makes the decisive half schedulable first. The smoke run was also moved
from g48 to g64 so it shares the MAIN run's cached SDF: at g48 the SDF is not in
`d4_sdf_cache` and the serial numpy build dominated job 917909 at over five minutes.

`analysis/r9_jobb_estimator_test.py` SUBCLASSES `SphereTank`. Its `measure_surface`
override computes the diagnostics and then returns `super().measure_surface()` verbatim, so
every column the published grader reads is bit-identical. In `--fixed` mode the surface
never feeds the dynamics (`self.free` is False), so the physics risk is zero by
construction. **The control on my own tool is run 1**: its configuration is identical to
`d4_ngrid_918722/sphere_bcfix_n64` and `d4_combo_918526/sphere_bcfix_ghost0`, which agree
with each other to 2.25e-3 N and give `fz = 60.476 N`. **If run 1 does not reproduce that,
the instrumentation changed the physics and nothing below is usable.**

The five runs:

| job | # | configuration | what it decides |
|---|---|---|---|
| 922584 | 0 | g64, 3 frames | smoke; a typo dies in a minute, on the cached SDF |
| 922584 | 1 | g64 band 1.0 ghost 0, 300 frames | MAIN. Near-field surface, exclusion sweep, radial profile |
| 922584 | 2 | g64, sphere pinned 0.3 m clear of the water, 300 frames | NO-BODY control: estimator bias with no body available |
| 922585 | 1 | g64 band 2.0, 300 frames | does the near-field surface respond to the band, or is it passive? |
| 922585 | 2 | g96 band 1.0, 300 frames | does the near-field offset scale with dx, as E1 requires? |

**Thresholds fixed in advance, in the script as constants, and not to be moved:**

    E1 supported   ratio against the near-field surface falls BELOW 1.10
    E3 supported   ratio against the near-field surface stays ABOVE 1.25
    in between     separates nothing, and must be reported as separating nothing

E1's quantitative requirement at g64 is a near-field surface **26.0 mm** above the far
field. E3 requires only the inflated body's displacement rise, which section 13.5 already
measured at 0.79 to 1.02 of its own prediction and is a few mm.

### 7.1 RESULT

**PENDING at the time of writing. 922584 and 922585 were queued, not yet running.** This section is
to be completed from `r9_jobb_estimator_test.py verdict`, which applies the thresholds
above mechanically, and the outcome is to be written up the same way whichever it is. **If
the near-field surface turns out to sit ~26 mm high and the ratio collapses to ~1, then the
FAIL is an instrument artifact, two sessions have committed a verdict whose MEANING is
wrong, and this document says so.**

---

## 8. The recommendation for job C, and why it depends on section 7

**This is Josie's decision to take or leave. What follows is the case, with the branch
point made explicit, because the two live explanations imply OPPOSITE recommendations.**

Job C is the free heave decay, three drop heights, `--n-grid 117 --lim 2.2`, 4.5 h
requested. It is graded against Kramer's published displacement time series, whose stated
experimental uncertainty is about 0.3 percent of drop height.

**The branch point is this: job C's dynamics never use the measured surface.** `advance()`
integrates `az = fz/mass - g`; `measure_surface` feeds only the reported ratio columns. So:

- **If E1 (estimator) holds**, the FORCE is right, the MOTION is right, and only the
  diagnostic column is wrong. Job C is graded on motion, not on the buoyancy ratio.
  **Recommendation: run job C. The instrument is broken, not the solver, and job C does not
  read that instrument.** Fix the denominator column separately and re-grade job B on it.
- **If E3 (contact band) holds**, the fluid sees a sphere inflated by `k*dx`, and job C
  measures exactly the quantity that inflation corrupts. At `n_grid 117`, `lim 2.2`,
  `dx = 18.803 mm` and `b = 0.8605*dx = 16.18 mm`, so `(R+b)/R = 1.108`. The heave
  stiffness `rho*g*A_w` scales as `(R+b)^2/R^2 = 1.227`, **+22.7 percent**. The predicted
  natural-period bias is:

  | added-mass assumption | period bias |
  |---|---|
  | `a33` NOT inflated (`a33/m = 0.5` held at the config's assumed value) | **-9.7%** |
  | `a33` inflated as `(R+b)^3` | **-4.5%** |

  Both bracket a bias 15x to 32x Kramer's experimental uncertainty. **Recommendation: do
  NOT run job C at `n_grid 117`. It would spend 4.5 hours measuring the contact band.**
  The band is `band_mult * dx` and `band_mult` is a run-time flag, so the cheap fix exists:
  either refine until `b` is small against `R`, or run job C at two band values and
  extrapolate to `band -> 0`, which is a defensible correction and costs one extra arm.

**What is common to both branches, and is the recommendation I would make regardless:**

1. **Do not re-use criterion 3's 10 percent band at g64 or coarser for anything.** Section
   5 shows it is 1.5 to 2.1 times the instrument's own resolution there. This is
   independent of which explanation wins.
2. **Whatever job C runs at, report the near-field surface column.** It costs one extra
   array operation per frame and it is the column whose absence made this whole question
   unanswerable for four audit rounds.
3. **The ladder-stopping decision stands either way.** Under E3 it stands because the
   solver's coupling is biased. Under E1 it stands because the project's only external
   validation instrument was measuring itself, which is a worse problem, not a lesser one.

---

## 9. What I could not verify, and what I am not claiming

- **Section 7.1 is empty.** No run of mine had landed. Every claim above rests on payloads
  other sessions produced plus arithmetic I did on them.
- **The "49 particles out of 598505" leak figure is unlocated.** It appears in the goal text
  of the 2026-08-18 deep search
  (`MPM SPH buoyancy force overestimation and hydrostatic validation benchmarks`), which is
  prose a session wrote, not a measurement. **The lowest end-of-run `n_below_floor` in any
  of the 18 payloads on Vista is 1079 of 598505, which is 0.180 percent, not 0.008
  percent.** The better run may exist on a branch I cannot see (`r7_jobb_bcfix_ab.py` is out
  of my scope), so this is a labelled gap, not a refutation. It matters because the
  30-percent-of-the-error figure quoted alongside it is calibrated to that state.
- **[Sch19e]** *A Consistent Boundary Method for the Material Point Method - Using Image
  Particles to Reduce Boundary Artefacts*, Schulz and Sutmann 2019, is the top-ranked hit
  for the E3 mechanism ("traditional MPM wall momentum zeroing can distort stress several
  grid lengths into an object"). **It has NO DOI**, resolves only to a Semantic Scholar
  record, and carries 5 citations. It is recorded as a LEAD, not as support, and must not
  enter the paper without a primary-record check.
- **The deep-search summaries are secondary.** Only [Che18c] has been verified against its
  publisher record. Everything else quoted from those searches is relayed.
- **No physics-skeptic pass on this document.** The subagent was not invoked. **Every claim
  here is UNREVIEWED** in that sense; the arithmetic in sections 4 and 5 is independently
  checked (Wolfram for `A_w/V_cap`, a second Python route for the rest) and the model fits
  in section 3 regenerate from `analysis/r9_jobb_estimator_test.py`.
- **8 points, one parameter.** The section 3.2 comparison is not a significance test and I
  do not claim the estimator model "wins". The claim is degeneracy.

---

## 10. Reproduction

    # pull the payloads (they live on Vista, not in the repo)
    ssh vista 'cd /work/11603/jcerrell0629/vista && tar czf /tmp/jobb.tgz d4_band d4_ngrid_918722 \
        d4_jobB_918043 d4_jobB_918240 d4_jobBbc_918450 d4_jobBbig_918251 d4_jobB_917909 \
        d4_ghost_918461 d4_combo_918526 d4_jobB_idev d4_jobB'
    scp vista:/tmp/jobb.tgz . && mkdir -p jobb && tar xzf jobb.tgz -C jobb

    python3 analysis/r9_jobb_estimator_test.py offline  jobb   # sections 3.1, 3.2
    python3 analysis/r9_jobb_estimator_test.py floor    jobb   # section 5
    python3 analysis/r9_jobb_estimator_test.py selftest        # section 6.1, needs numpy
    python3 analysis/r9_jobb_estimator_test.py verdict <instrumented payloads>   # section 7.1

Sections 3, 5 and 6 are stdlib-only and run on the Mac in under a minute. Section 6.1 needs
numpy but no GPU and no warpmpm: `uv venv v && uv pip install --python v/bin/python numpy`
provisions it in about fifteen seconds, which is the standing route on this Mac because no
system interpreter here has numpy. Section 7 needs a GH200.

A note on the four claims that carry a number and could be wrong cheaply, so they can be
killed in one command each rather than surviving to the paper:

  A_w/V_cap = 14.605 per metre         Wolfram Alpha, independently of the Python
  K = rho*c^2 = 165,000 Pa             c read from the run config, not assumed
  10 distinct simulations, not 18      the pairwise distance matrix is printed
  instrument accurate to 0.14 mm flat  `selftest` exits non-zero if it is not
