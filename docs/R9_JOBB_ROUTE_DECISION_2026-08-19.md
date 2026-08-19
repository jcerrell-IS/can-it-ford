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

**THE FAIL IS A SOLVER-SIDE DEFECT, NOT AN INSTRUMENT ARTIFACT. The estimator hypothesis is
refuted by direct measurement, and it is refuted by four independent lines in one run.**

1. **The near-field surface the estimator discards sits 0.98 mm above the far field. The
   hypothesis needed 26.02 mm.** That is 3.8 percent of the requirement, and 2.8 percent
   once the no-body control is subtracted. The ratio against the near-field surface is
   **1.493**, against a pre-registered E1 threshold of 1.10 and an E3 threshold of 1.25.
   **Including every particle the estimator throws away moves the ratio the WRONG WAY,
   1.522 to 1.528.** Vista job 922584, 2 min 58 s, `RC = 0` on all three runs.
   **It holds at three arms and at g96 the sign reverses**: the offset is +0.98, +0.07 and
   **-1.14 mm** at g64/band1, g64/band2 and g96/band1, against requirements of 26.02, 26.02
   and 17.34 mm. E1's specific prediction was that the offset scales as `1.3875*dx`; it
   does not scale with dx at all, because it is noise about zero (section 7.2a).

2. **The `2R` exclusion is not merely a defensible trade, it is the correct call, and that
   is now measured rather than argued.** The docstring says the annulus carries "the
   meniscus and any splash off the collider". `water_z_max` is indeed 30.13 mm above the
   far-field surface, so those particles exist, but the annulus 99th percentile is only
   0.98 mm up. **A few ejected particles, not an elevated shelf.** Nobody had checked.

3. **The no-body control removes the last escape route.** With the sphere pinned clear of
   the water and `max |fz| = 0.000e+00 N` over 300 frames, **the free surface still falls
   59.75 mm**, against 61.84 mm with the body. **97 percent of the surface fall happens
   with no body present.** It is the floor and wall leak, not the sphere.

4. **Criterion 3 has the P-2 pathology on the PASS side and NOT on the FAIL side, and the
   analytic prediction was confirmed by measurement.** Section 5 derived a half-layer floor
   of **9.22 percent** at this state from `A_w/V_cap` alone. The measured spread between
   two independent estimators is **9.8 ratio-points**. Separate derivations, agreeing to 6
   percent. **A PASS at g64 could not have been informative** because the band equals the
   instrument's resolution. But the excess is 5.0x to 9.4x that floor, so **d11-accessor's
   FAIL clears its own floor by a factor of several and stands.**

**The estimator is not worth nothing, and section 7.2 says what it is worth**: the whole
family of defensible estimator choices spans 10.4 ratio-points against a 52.2-point excess,
at most 20 percent, and none of it in the direction the hypothesis needed.

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

**This section is preserved as it stood BEFORE the run, because it is why the run was worth
buying.** Section 7 refuted the estimator model by direct measurement. That does not make
this analysis wrong; it makes it the correct reading of the evidence that existed, and the
gap between "fits marginally better on 8 points" and "refuted at 3.8 percent of its
requirement" is the whole argument for spending three minutes of a GH200 rather than
reasoning further from force fits.

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
construction. **The control on my own tool is run 1**: it must reproduce an existing run to
within this scene's run-to-run reproducibility, or the instrumentation changed the physics
and nothing below is usable.

**THE CONTROL PASSED AND MY PREDICTION OF WHICH RUN IT WOULD MATCH WAS WRONG.** I predicted
`d4_ngrid_918722/sphere_bcfix_n64` at `fz = 60.476 N`. Run 1 gives `fz = 44.7281 N` and
reproduces `d4_band/sphere_g64_band1.0` instead, to a per-frame `max |dFz|` of **2.375e-3 N
= 3.43e-5 of the 69.218 N target**, which is the reproducibility floor of this scene. So
the instrumentation is validated, against a different reference than I named.

**The reason matters and is a provenance finding for whoever owns the floor BC.** Run 1
used `d4_scene/sphere_heave.py` (sha256 `6ab8cec5...`, byte-identical to my branch head)
with `--ghost-layers 0`, and ended with **`n_below_floor = 29350`**, the leaky-floor
behaviour. The "bcfix" runs 918450, 918526 and 918722 also carry `n_ghost_layers = 0` and
end with **1079**. Same file and same flags cannot give both. **Therefore the bcfix code
state is NOT in `d4_scene/sphere_heave.py` and NOT on this branch.** It exists somewhere
else, plausibly the branch carrying `r7_jobb_bcfix_ab.py`, which is out of my scope. Anyone
citing a "bcfix" number should say which file produced it, because the copy staged on Vista
for jobs B and C does not.

Consequence for this section: **every run below is at the LEAKY floor configuration.** That
is stated in the result rather than discovered later, and section 7.1 says what it does and
does not compromise.

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

### 7.1 RESULT: E1 IS REFUTED. The FAIL is a solver-side defect, not an instrument artifact

Job 922584 ran on `c608-091` and finished in **2 minutes 58 seconds**, all three runs
`RC = 0`, `ALLDONE`. Applied mechanically by `r9_jobb_estimator_test.py verdict`, last 50
frames:

    ratio against the far-field surface  (as published)   1.522
    ratio against the near-field surface (the test)       1.493
    E1 required near-field rise at this dx: 26.02 mm; measured +0.98 mm
    VERDICT E3: the estimator does NOT explain the FAIL (ratio > 1.25)

**The near-field surface sits 0.98 mm above the far field. E1 needed 26.02 mm. That is 3.8
percent of the requirement**, and the resulting ratio, 1.493, is not close to the 1.10
threshold; it is above the 1.25 threshold that supports the opposite conclusion.

**Four independent lines in the same run all say so, and each is a different measurement.**

**(a) The exclusion radius barely moves the surface, and removing the exclusion makes the
ratio WORSE.** Same statistic, same `+h/2`, only the population changes:

| exclusion | surface | vs far-field | ratio | n |
|---|---|---|---|---|
| 0 (keep everything) | 0.51390 m | -0.22 mm | **1.528** | 598505 |
| 0.5R | 0.51399 | -0.14 | 1.526 | 590419 |
| 1R | 0.51428 | +0.16 | 1.517 | 562983 |
| 1.5R | 0.51414 | +0.02 | 1.521 | 511065 |
| **2R, as written** | **0.51412** | **0.00** | **1.522** | 438606 |
| 3R | 0.51459 | +0.47 | 1.508 | 231196 |
| 4R | 0.51534 | +1.21 | 1.486 | 34566 |

The whole sweep spans **1.43 mm** of surface and 4.2 points of ratio. **Including every
particle the estimator throws away moves the ratio from 1.522 to 1.528, in the wrong
direction.** The dispatch's hypothesis predicted a collapse toward 1.0.

**(b) The radial profile is flat. There is no shelf.** Deviation from the far-field
estimate, 99th percentile plus `h/2` in each annulus: `1-1.5R +2.28 mm`, `1.5-2R +0.19`,
`2-2.5R -0.47`, `2.5-3R -0.56`, `3-4R +0.34`, `4R+ +1.21`. **A 2.84 mm span across the
entire tank.** The `0-1R` bin reads -32.67 mm, which is the body's own carved footprint and
is not a free surface, exactly as section 2 said it would not be.

**(c) The ceiling from section 3.2a is reconciled, and the docstring is vindicated.**
`water_z_max - far` is **+30.13 mm**, so the single highest particle really is 30 mm up.
But the annulus 99th percentile is only **+0.98 mm** up. **The annulus holds a few ejected
particles, not an elevated shelf.** That is precisely what `measure_surface`'s docstring
claims is in there, and it had never been checked. **The 2R exclusion is not just a
defensible trade; it is the correct call, and it is now measured rather than argued.**

**(d) The no-body control removes the last escape route.** With the sphere pinned 0.3 m
clear of the water, `n_carved = 0` and `max |fz| = 0.000e+00 N` over all 300 frames, so the
collider provably never touches fluid:

| | far-field vs design | near minus far |
|---|---|---|
| frame 0 | -8.78 mm | +0.05 mm |
| first 50 | -22.93 mm | -5.44 mm |
| last 50 | **-59.75 mm** | **+0.26 mm** |

**The free surface falls 59.75 mm with no body present at all**, against 61.84 mm in the
main run. **97 percent of the surface fall is reproduced with the body removed**, and
`n_below_floor` is 29122 without the body against 29350 with it. The fall is the floor and
wall leak, full stop; the sphere contributes essentially nothing to it. And subtracting the
control, **the body's true near-field elevation is +0.98 - 0.26 = +0.72 mm**, which is
**2.8 percent** of what E1 requires.

### 7.2 What the estimator IS worth, because it is not zero and section 5 predicted it

The honest counterpart. Two defensible estimators on the same cloud disagree by more than
the synthetic flat-surface test suggested, because the real surface is wavy:

| estimator | surface | ratio |
|---|---|---|
| percentile 99 plus `h/2`, as written | 0.51412 m | 1.522 |
| column-max median, independent route | 0.51755 m | 1.424 |
| domain-clean (drop leaked particles) | 0.51458 m | 1.508 |

The two independent routes differ by **3.43 mm = 0.183 dx**, worth **9.8 ratio-points**.
Across every variant measured, the whole estimator family spans **1.424 to 1.528, 10.4
points, against an excess of 52.2 points**: at most **20 percent** of the discrepancy, and
none of it in the direction E1 needed.

**Section 5's floor calculation is independently corroborated by this.** It predicted an
`h/2` floor of **9.22 percent** at this exact state from `A_w/V_cap` alone, with no run
involved. The measured spread between two defensible estimators is **9.8 points**. Those
are separate derivations, one analytic and one measured, and they agree to within 6
percent. **Criterion 3's 10 percent PASS band really is the same size as the instrument's
own resolution at g64**, and that now rests on a measurement, not only on arithmetic.

The percentile choice is a much bigger lever than the exclusion radius: p95 gives 2.395,
p99 gives 1.522, p99.9 gives 1.194 and the raw maximum gives 0.871. **This is not a free
parameter to tune.** p99.9 and max let a handful of ejected particles define the surface,
which is the failure the docstring rejects by name, and (c) above shows those particles
exist and sit 30 mm up. The defensible band is p99 to the column-max median: 1.424 to 1.522.

### 7.2a The two supporting arms landed, and one refutes E1 with the sign reversed

Job **922600**, 7 minutes, `RC = 0` on both. (922585 asked 75 minutes and never scheduled;
after job A finished in 2 min 58 s that request was obviously the wrong shape, so it was
cancelled and resubmitted at 15 minutes, which started almost at once.) Same code state,
same floor BC, so these three are a self-consistent set:

| run | dx | band/dx | fz | sub | ratio | near minus far | E1 needs | fitted k |
|---|---|---|---|---|---|---|---|---|
| g64 band 1.0 | 18.75 mm | 1.0 | 44.728 N | 89.12 mm | 1.522 | **+0.98 mm** | 26.02 mm | 0.864 |
| g64 band 2.0 | 18.75 | 2.0 | 69.107 | 91.25 | 2.256 | **+0.07 mm** | 26.02 mm | 0.915 |
| g96 band 1.0 | 12.50 | 1.0 | 34.511 | 83.90 | 1.306 | **-1.14 mm** | 17.34 mm | 0.765 |

**Three things, and the second is what the g96 arm was bought for.**

1. **At g96 the near-field surface is BELOW the far field.** E1 needed +17.34 mm and got
   -1.14 mm. The sign is against the hypothesis, and using the near-field surface makes the
   ratio WORSE, 1.310 to 1.342. Across the three arms the offset is +0.98, +0.07, -1.14 mm:
   **a 2.1 mm span straddling zero**, against requirements of 26.02, 26.02 and 17.34 mm.
2. **The near-field offset does not scale with dx.** That was E1's specific, falsifiable
   prediction: it required `1.3875 * dx`, so 26.0 mm at g64 falling to 17.3 mm at g96. The
   measured offset does not fall with dx because it is not a function of dx; it is noise
   about zero. **This is the arm that could have rescued E1 and it did the opposite.**
3. **The near-field surface is passive to the band, and the FAR field is not.** Quadrupling
   the band from 0.5 to 2.0 dx nearly doubles the force, and the near-field offset moves
   only +0.98 to +0.07 mm. But the **far-field surface rises +2.12 mm** over the same
   change. That is job B result section 13.5's displacement-rise mechanism, reached from a
   completely independent direction: the inflated body displaces more water and lifts the
   whole tank slightly, while doing nothing special to the annulus.

**A SECOND INSTRUMENTATION CONTROL, AND THIS ONE I PREDICTED CORRECTLY.** The g96 arm
reproduces the existing `d4_jobB_idev/sphere_fixed_g96_300` at `fz = 34.5107` against
`34.5115 N`, a per-frame `max |dFz|` of **5.014e-3 N = 7.24e-5 of target**. Two independent
reproductions of two different pre-existing runs, at two resolutions, both inside this
scene's reproducibility floor. The instrumentation does not touch the physics.

Fitted inflation `k = 0.864 / 0.915 / 0.765` across the three arms, consistent with the
global `k = 0.84` to `0.86` of section 3.2 fitted to a different and larger set.

### 7.3 What this result does NOT establish

- **It is measured at the LEAKY floor**, because that is what the staged code produces (see
  the control note above). The surface has fallen 61.8 mm and `sub` is 89.1 mm rather than
  113.8 mm. **This does not weaken the refutation**: the quantity refuted is a near-field
  RISE, and the radial profile is flat to 2.84 mm regardless of where the mean level sits.
  It does mean the numbers here should not be pooled with bcfix-arm numbers.
- **It is two resolutions and two bands, not one, but all at the same floor BC.** Section
  7.2a adds g96 and band 2.0. What is still untested is whether the near-field offset
  behaves the same way once the floor stops leaking, and that cannot be tested from this
  branch because the bcfix is not on it.
- **Refuting E1 does not by itself prove E3.** E3's positive evidence is separate and
  pre-existing: the force moves 34.6 to 69.1 N across the band sweep at fixed dx, and the
  inflated-collider geometric model fits every distinct run with one constant `k = 0.84`
  to `0.86` at 3.4 percent RMS. E2 is bounded out arithmetically in section 4. So E3 is
  reached by elimination PLUS positive evidence, which is stronger than elimination alone
  and weaker than a direct measurement of the contact impulse. **That direct measurement,
  decomposing the wrench into pressure and contact parts, is the next test and this unit
  did not do it.**

---

## 8. The recommendation for job C. Section 7 resolved the branch, and it moved

**This is Josie's decision to take or leave.** Section 7 refuted E1, so the branch that
said "the instrument is broken, the solver is fine, run job C" is closed. What follows is
the case on the surviving branch, **plus a blocker the no-body control turned up that is
worse than the one this unit was sent to look for.**

### 8.1 THE LEAK IS THE HARDER BLOCKER, AND IT IS MEASURED WITH A NO-FORCING CONTROL

The no-body run is the cleanest thing in this document: no body, `max |fz| = 0.000e+00 N`
over 300 frames, nothing to argue about. In it, **the tank loses 29122 of 606797 particles
through the floor, 4.80 percent, and the free surface falls 59.75 mm in 10 seconds.**

Job C is a free heave decay. Its predicted natural period is **0.777 s**. Over the 200
frames the staged script requests, that is 6.7 s, roughly **9 periods**, during which the
waterline in this configuration falls by about **40 mm, which is 27 percent of the sphere
radius**. The sphere would be settling relative to a draining waterline for the entire
decay. **A decay measured against a moving waterline cannot be compared to an experiment
with a fixed one**, and Kramer's stated experimental uncertainty is 0.3 percent of drop
height, so there is no tolerance to absorb it.

**The fix exists and is not in the staged file.** The bcfix arms end with `n_below_floor =
1079` against 29350 here, a **27-fold** reduction, and their surface falls 36.2 mm rather
than 61.8 mm. But section 7's control note shows that code state is **not** in
`d4_scene/sphere_heave.py` and not on this branch. **The highest-value action before job C
is to locate and stage the bcfix, not to run anything.** It costs no GPU time to find.

### 8.2 THE BAND, WHICH IS THE ORIGINAL BLOCKER AND IS STILL THERE

At `n_grid 117`, `lim 2.2`, `dx = 18.803 mm`, and the inflated-collider fit `k = 0.8605`
gives `b = 16.18 mm`, so `(R+b)/R = 1.108`. Heave stiffness `rho*g*A_w` scales as
`(R+b)^2/R^2 = 1.227`, **+22.7 percent**. The predicted natural-period bias is:

| added-mass assumption | period bias |
|---|---|
| `a33` NOT inflated (`a33/m = 0.5`, the config's own assumed value) | **-9.7%** |
| `a33` inflated as `(R+b)^3` | **-4.5%** |

Both bracket a bias **15x to 32x** Kramer's experimental uncertainty. Labelled assumption:
`a33/m = 0.5` is an estimate carried in the run config, not a measurement, and the two rows
above are the honest bracket rather than a single number.

**`band_mult` is a run-time flag**, so the cheap route exists: run job C at two band values
and extrapolate to `band -> 0`. That is one extra arm, it is a defensible correction, and
it converts a systematic error into a measured one.

### 8.3 THE RECOMMENDATION

1. **Do not run job C at `n_grid 117` on the staged code.** It would spend 4.5 hours
   measuring a 4.8 percent floor leak and a 22.7 percent stiffness inflation, both of which
   are already characterised and neither of which job C is designed to measure.
2. **Locate and stage the bcfix first.** Zero GPU cost, 27-fold leak reduction, and it is
   the difference between a draining tank and a tank.
3. **Then run job C with a band arm**, two `band_mult` values, and extrapolate to zero. The
   period is the graded quantity and the band biases it in a computable direction.
4. **Report the near-field surface column in whatever runs next.** It costs one extra array
   operation per frame. Its absence is why this question stayed open through four audit
   rounds, and its presence closed it in a 3-minute job.

### 8.4 WHAT STANDS REGARDLESS OF ALL OF THE ABOVE

- **The ladder-stopping decision stands, and it is now better founded than when it was
  taken.** The FAIL is a real solver-side defect, it clears the instrument's own floor by a
  factor of 5 to 9, and the leading mechanism is named.
- **Criterion 3's 10 percent PASS band is unusable at g64 or coarser.** Predicted at 9.22
  percent analytically, measured at 9.8 points between two defensible estimators. If a
  future job is graded on this criterion, either the grid gets finer or the band gets
  widened to something the instrument can resolve, and widening a pre-registered band is a
  criterion change that must be pre-registered as one.

---

## 9. What I could not verify, and what I am not claiming

- **The leaky-floor caveat is CLOSED, not carried.** Section 12 ran the bcfix engine, whose
  floor loses 0.180 percent, and the near-field offset there is +0.65 mm. The expectation I
  recorded here became a measurement rather than staying an expectation.
- **What is still untested is the baseline leak's own cause.** Section 12.2 shows a 2.2
  percent floor loss that neither the alignment nor the engine fix touches. I did not
  diagnose it. Section 13.3 shows the SURFACE DROP converges in PPC (82 to 24.6 mm), so
  particle resolution is part of it, but I did not run the `--ghost-layers` arm that would
  test B-spline stencil truncation directly.
- **The `dx` prong is now measured (section 14.2) but at only 1.86 sigma end-to-end**,
  below this project's 3 sigma bar, with the finest point resting on 35 frames. Job 923291
  (g192) is the arm that settles it, pre-registered.
- **My own convergence claim in sections 3.2 and 7.2a is WITHDRAWN** (section 14.3). It was
  computed at unmatched submergence.
- **Wal07 claim (a) is withdrawn, not adopted.** Section 13.2. Nothing here rests on it.
- **Section 12.3's `n_grid` recommendation is arithmetic, not a measured result.** That an
  exactly-aligned constrained plane is best is measured at g64; that it will hold at other
  grids and at `lim = 2.2` is inference from one 2x2.
- **Everything in section 7 is at the LEAKY floor**, because the staged code produces it.
  See the control note in section 7. Do not pool these numbers with bcfix-arm numbers.
- **I predicted the wrong control reference and said so rather than quietly repointing it.**
  I wrote that run 1 would reproduce `fz = 60.476 N`. It reproduced 44.728 N. The
  instrumentation control passed on its own terms, to 3.43e-5 of target, but my statement of
  which run it would match was wrong, and the reason turned out to be a provenance fact
  worth more than the prediction was.
- **The adversarial reviewer is dead and this was measured by d20-reader**, 20 Agent calls
  across 18 transcripts with zero successes. I did not attempt one and did not fake one.
  **Every percentage, force, verdict count and distance in this document is UNREVIEWED.**
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

---

## 11. What job 918450 actually set, and whether the leak explains criterion 3

Asked by the coordinator, 2026-08-19 23:05. Neither d11-accessor nor I had read 918450.

### 11.1 It is a ONE-CHARACTER FORK OF THE ENGINE, not a change to the scene

`run_jobBbc.sh` on Vista points `PYTHONPATH` at `mpm-engine-bcfix-src`, not at the
canonical `mpm-engine/src`. Its `sphere_heave.py` is sha256 `6ab8cec5...`, **byte-identical
to the one I ran**. The entire difference is in the solver:

    mpm_solver_warp.py:1955   -  if dotproduct < 0.0:
                              +  if dotproduct <= 0.0:

`diff -u` over the two trees gives **one hunk, one line**, and `diff -rq` finds no other
differing source file. That is the whole of the "floor BC treatment".

**This corrects my own section 7 note.** I wrote that the bcfix "is not in `d4_scene` and
not on this branch", which is true but reads as a missing scene edit. It is not a scene
edit at all. Neither branch nor scene file could ever have held it.

### 11.2 Why one character mattered: the floor lands exactly on a grid plane

The kernel computes `offset = float(grid_z)*model.dx - param.point[2]` and constrains the
node only when the dot product with the plane normal is negative. A node lying **exactly**
on the plane gives `0.0`, which `< 0.0` rejects, so it is left unconstrained.

`FLOOR = 0.075` and `dx = lim/n_grid`, and at `lim = 1.2` that quotient is an exact
integer at every grid this project has run:

| grid | dx | FLOOR/dx | node on the floor plane? |
|---|---|---|---|
| g48 | 0.025000 | 3.000 | **yes**, exact in f64 and f32 |
| g64 | 0.018750 | 4.000 | **yes** |
| g96 | 0.012500 | 6.000 | **yes** |
| g128 | 0.009375 | 8.000 | **yes** |
| g192 | 0.006250 | 12.000 | **yes** |
| **117 / lim 2.2 (job C's geometry)** | 0.018803 | 3.9886 | **no**, dot = 2.14e-4 |

So a whole grid plane at the floor went unconstrained in **every** job B run, and the
same test says **job C's own geometry would not have hit it**. The wall planes at
`0.100` are exact only at g48, g96 and g192, and the measured wall loss follows that:
my canonical g96 run loses **5.135 percent** of particles past the walls where g64 and
g128 lose 2.5 to 2.6 percent, and the bcfix engine takes that g96 figure down to 2.730.

### 11.3 SIGN and MAGNITUDE, from an A/B differing by exactly one character

My `r9_g64_band1` (canonical `<`) against `d4_combo_918526/sphere_bcfix_ghost0` (bcfix
`<=`). Same scene sha `6ab8cec5`, same flags, same 300 frames, one character apart:

| | canonical `<` | bcfix `<=` | change |
|---|---|---|---|
| particles below the floor | 29350 (4.904%) | 1079 (0.180%) | **-96.3% of the leak** |
| surface drop | 60.88 mm | 36.23 mm | -24.65 mm |
| `fz` | 44.728 N | 60.476 N | +15.75 N |
| **criterion-3 ratio** | **1.5217** | **1.3551** | **-0.1666** |
| `fz` / 69.218 N (nominal) | 0.6462 | 0.8737 | +0.2275 |

**SIGN: CONSISTENT.** Stopping the leak lowers the criterion-3 ratio. More water lost
through the floor, larger criterion-3 excess, in the direction the question supposed.

**MAGNITUDE: ABOUT ONE THIRD, AND THAT IS THE USEFUL HALF OF THE ANSWER.** Removing
**96.3 percent** of the floor leak removed **31.9 percent** of the excess: 52.2 points
down to 35.5. **Two thirds of the criterion-3 failure survives a floor that has
essentially stopped leaking**, so the leak is a real contributor and cannot be the
explanation. The FAIL is not rescued by fixing the floor: 35.5 points is still far
outside the 25 percent FAIL band and still 3.9x the 9.22 percent instrument floor of
section 5.

**This reproduces a figure that section 9 recorded as unlocated.** The 2026-08-18 deep
search's goal text asserts that eliminating the leak "removed only 30 percent of the force
error". **The 30 percent reproduces from the payloads at 31.9.** The other figure in the
same sentence still does not: it claims 49 particles, 0.008 percent, where the best run on
Vista loses **1079 particles, 0.180 percent**, twenty-two times more.

Volume budget at the last frame, per-particle volume `h^3 = 8.2397e-7 m3` over the 1.0 m2
column, with the 7.42 mm one-time compression from `water_budget`'s own derivation:

| | floor loss | wall loss | compression | total | observed drop |
|---|---|---|---|---|---|
| canonical `<` | 24.18 mm | 12.41 mm | 7.42 mm | 44.01 mm | 60.88 mm (72%) |
| bcfix `<=` | 0.89 mm | 13.89 mm | 7.42 mm | 22.20 mm | 36.23 mm (61%) |

**Fixing the floor does not fix the surface.** The bcfix run still drops 36 mm, of which
the floor now contributes 0.89. The wall loss is untouched and is now the largest measured
term. That is consistent with 11.2: at g64 the wall planes are NOT on grid nodes, so the
one-character fix does nothing for them, and whatever moves water past the walls is a
different mechanism.

### 11.4 The alignment story does not survive its own test, so it is being tested

`d4_jobBbig_918251` runs `n_grid 117, lim 2.2` on the **canonical** engine with the floor
**off** the grid plane, and still loses **3.796 percent** through the floor, close to the
4.5 to 4.9 percent of the aligned canonical runs rather than the 0.18 percent of the fixed
one. **If exact-node alignment were the whole mechanism, that run should not leak.**

It is confounded: its scene is sha `4b329d90`, not the `6ab8cec5` used by every run
compared in 11.3, so it cannot decide the question. **Vista job 923195 completes the 2x2**,
engine {canonical, bcfix} x floor {on-node, off-node by half a cell}, all at `lim = 1.2`
with `dx`, the SDF cache key and the scene file held fixed. The off-node arms shift `FLOOR`
by `0.5*dx` through a subclass attribute; `sphere_heave.py` is still not edited.

**Pre-registered, written before the runs:** if exact-node alignment is the mechanism, the
canonical off-node arm leaks like the fixed case, about 0.2 percent, because off the plane
`<` and `<=` are the same test. **If it still leaks about 4.9 percent, the alignment story
is refuted and the one-character fix works by some other route.**

### 11.5 The dependence on d11-accessor's column, stated precisely

d11-accessor's job 922619 is a no-body hydrostatic column whose `below_floor` climbs
monotonically to 46,926 over 180 frames. It points the same way as my no-body control,
where 97 percent of the surface fall happened with no body present.

**It is not independent corroboration, and the shared parent is sharper than "copied
defaults".** Their column runs `floor_m = 0.075`, `lim_m = 1.2`, `dx_m = 0.01875`, read
live from their job log. That is **exactly** the geometry of 11.2: `0.075/0.01875 = 4.000`,
a grid node sits precisely on their floor plane, and on the canonical engine it is
unconstrained. **Their column and my control are two observations of one bug at one grid
plane in one engine**, not two independent origins, and this project's rule says to say so.

**What that buys them, which generic corroboration would not**: a falsifiable prediction.
**Their column should stop leaking on `mpm-engine-bcfix-src`, or with `FLOOR` shifted half
a cell, and its `dp/dz` deficit should shrink with it.** If it does not, section 11.4's
result applies to their scene too and the mechanism is elsewhere. Either way it is one
20-minute job, and their column is a cleaner probe of it than my sphere scene because it
has no collider at all.

---

## 12. The 2x2 landed. Half my pre-registration failed, and that half is the finding

Vista job **923195**, 3 arms, `RC = 0` on all, at `lim = 1.2` and g64 with `dx`, the SDF
cache key and the scene file (`6ab8cec5`) held fixed. The fourth cell is my earlier
`r9_g64_band1`. Engine {canonical `<`, bcfix `<=`} x floor {on a grid plane, shifted off it
by half a cell through a subclass attribute}.

| engine | floor | below floor | outside walls | surface drop | `fz` | ratio | near minus far |
|---|---|---|---|---|---|---|---|
| canonical `<` | ON-node | **4.904%** | 2.516% | 60.88 mm | 44.728 N | 1.522 | +0.98 mm |
| bcfix `<=` | ON-node | **0.180%** | 2.816% | 36.23 mm | 60.476 N | 1.355 | +0.65 mm |
| canonical `<` | OFF-node | **2.213%** | 2.552% | 50.51 mm | 51.741 N | 1.454 | +0.99 mm |
| bcfix `<=` | OFF-node | **2.214%** | 2.552% | 50.51 mm | 51.741 N | 1.454 | +0.99 mm |

### 12.1 The half that passed, and it is exact

**At an off-node floor the engine fix does literally nothing.** 2.213 against 2.214 percent,
`fz` 51.741 against 51.741 N, drop 50.51 against 50.51 mm, ratio 1.454 against 1.454. Off
the grid plane `<` and `<=` are the same test and there is nothing to fix. That is the
mechanism of the one-character change confirmed exactly, and it is why the fix bought 96.3
percent of the leak at an on-node floor and 0.0 percent at an off-node one.

**The negative control passed too.** Neither factor touches the wall planes, and the wall
loss is 2.516 / 2.816 / 2.552 / 2.552 percent across all four arms, flat. A design where
the wall column had moved with the floor treatment would have been measuring something
else.

### 12.2 The half that failed: alignment is NOT the whole leak

**I pre-registered that the canonical off-node arm would leak like the fixed case, about
0.2 percent. It leaks 2.213 percent, twelve times that.** The prediction is refuted and the
correct statement is narrower than the one section 11.2 implied:

**There are two floor-leak mechanisms, not one.** The exactly-aligned unconstrained plane is
the larger at `lim = 1.2` and is what the one character fixes. Underneath it sits a
**baseline leak of about 2.2 percent that neither the alignment nor the engine fix
touches**, and which is the only mechanism present whenever the floor falls between grid
planes. Section 11.2 was right about what the fix does and wrong to leave the impression
that alignment was the whole story.

**This resolves section 11.4's anomaly rather than leaving it open.** `d4_jobBbig_918251`
runs off-node on the canonical engine and loses 3.796 percent, which looked inconsistent
with an alignment-only account. It is not an anomaly: it is an off-node run showing the
baseline leak, the same regime as this 2.213 percent. The remaining gap is its different
scene sha and its different `lim`, and neither needs a new mechanism.

### 12.3 A result neither branch predicted, and it points at the fix to make

**Shifting the floor off the grid makes the FIXED engine WORSE: 0.180 to 2.214 percent.**
The best of the four configurations is the one where a node lies exactly on the floor AND
is constrained. An exactly-aligned, correctly-constrained plane suppresses the baseline
leak as well as its own, presumably because the constrained node sits precisely where the
B-spline stencil of the bottom particle layer is truncated.

**Operationally that is worth more than the diagnosis.** It says do not chase the floor BC
with a general fix first: **run at a grid where `FLOOR/dx` is an exact integer AND use the
`<=` engine**, and the floor loss falls from 4.9 percent to 0.18 percent for one character
and no cost. Job C's `n_grid 117, lim 2.2` satisfies neither condition: `FLOOR/dx = 3.9886`.
**Choosing `n_grid` so that `0.075/(lim/n_grid)` is an integer is free**, and at `lim = 2.2`
the nearest such grids are `n_grid = 88` (`dx = 0.025`, `FLOOR/dx = 3`) and `n_grid = 117.33`
which is not an integer, so `88` or `176` are the candidates.

### 12.4 The magnitude answer, now on three levels of leak instead of two

Three arms give three floor-leak levels on one code path, and the criterion-3 ratio is
linear in the leak to 11 percent of its own span:

    ratio = 0.03474 * (percent below floor) + 1.35922

| percent below floor | ratio | fit | residual |
|---|---|---|---|
| 4.904 | 1.5217 | 1.5296 | -0.0079 |
| 2.213 | 1.4544 | 1.4361 | +0.0183 |
| 0.180 | 1.3551 | 1.3655 | -0.0104 |

**EXTRAPOLATED TO ZERO FLOOR LEAK THE RATIO IS 1.359, still +35.9 percent.** That is
**1.44x the 25 percent FAIL band** and **3.9x the 9.22 percent instrument floor** of section
5. Removing all of the floor leak removes 31.2 percent of the excess, which reproduces the
two-point A/B's 31.9 percent from an independent third point.

**So the answer to the question as asked is: consistent in sign, about one third in
magnitude, and the FAIL survives the floor entirely.** A tank that lost no water through
its floor at all would still fail criterion 3 by a factor of 1.4 on the band.

### 12.5 E1 stays refuted, now at six arms including a non-leaking floor

`near minus far` across every instrumented arm: **+0.98, +0.07, -1.14, +0.65, +0.99, +0.99
mm**, against requirements of 26.02, 26.02, 17.34, 26.02, 26.02, 26.02 mm. **Section 9's
one real limitation is closed**: the `bcfix` on-node arm has a floor that has essentially
stopped leaking (0.180 percent) and its near-field offset is +0.65 mm, 2.5 percent of the
requirement, verdict E3. The estimator hypothesis does not survive at any floor BC, any
band, or any resolution tested.

---

## 13. Is the accessor the velocity-projection route? Yes, and its plateau signature holds

### 13.1 What the accessor computes, read from source rather than inferred

`core/solver.py:354-360`:

> "Reaction wrench the material exerts on an SDF collider, from the grid impulse
> accumulated since the last reset: **force = sum m\*(v_free - v_new) / dt**"

and the kernel that accumulates it, `mpm_solver_warp.py:2732-2734`:

    v_free  = state.grid_v_out[gx, gy, gz]
    m       = state.grid_m[gx, gy, gz]
    impulse = m * (v_free - v_new)
    wp.atomic_add(param.force, 0, impulse)

**So the answer is yes, with a precision worth keeping.** The accessor is not itself a
velocity projection; it is a grid-level momentum difference over the nodes the collider
touches. But **both of its inputs are outputs of the mass-weighted P2G projection**:
`state.grid_m` is `sum_p w_ip m_p`, and `state.grid_v_out` descends from
`sum_p w_ip m_p v_p / sum_p w_ip m_p` plus the stress and gravity update. **It is not a
pressure integral over the wetted surface**, which is the alternative the 2026-08-18 deep
search's goal text contrasted it with. Any systematic error in the projection propagates
into `m` and `v_free` and therefore into the reported force.

### 13.2 Wal07 read directly, and two of the relayed claims do not survive

The citation record resolves: **Wallstedt and Guilkey 2007, "Improved Velocity Projection
for the Material Point Method", CMES 19, 223-232, doi:10.3970/CMES.2007.019.223**, matching
the relayed description including the page range. The PDF is retrievable, so I read it
rather than relying on the relay, and the project's rule that "report X says paper Y
reports N" is not "paper Y reports N" earned its keep twice:

**(a) "For a body held fixed the projection error is a CONSTANT SYSTEMATIC BIAS, not
noise" is NOT IN THE PAPER.** What the paper says is that accuracy "is strongly dependent
on particle density and location" (abstract), and section 2 adds the opposite emphasis:
"even if the initial particle distribution is ideal, as simulations evolve, the particles
will generally move into a less favorable configuration." The paper never characterises the
error as constant, and it never treats a fixed body. **The claim should be withdrawn**, and
nothing below leans on it. It also would not have applied cleanly here: the body is fixed
but the water particles move, so the particle-grid registration in this scene is not static.

**(b) The plateau IS in the paper and is quoted correctly, but its O(h) scaling is NOT a
stated result.** Section 3, page 226, on a prescribed quadratic velocity field: the error
descends "to a plateau ... further increase in PPC produces no decrease in error ... The
right term, and the associated plateau, could be reduced independently by fixing PPC and
reducing grid cell size." The `PPC^-2` (bilinear) and `PPC^-3` (GIMP) scalings are also the
paper's own words, for the LINEAR field. **But the paper's analytic reference for the
plateau is Vshivkov's 1996 bound, whose grid term is `h^2`, not `h`.** The `O(h)` reading
comes from measuring Figure 10 off the page. So the direction is the paper's; the exponent
is not, and it should be quoted as "grid-set" rather than as `O(h)`.

**Ste08 checks out as the negative result, and adds something nobody asked for.** Steffen
et al. 2008, doi:10.3970/CMES.2008.031.107, calls quadrature errors **"force kicks"** that
constrain the time step, not a one-signed bias, so quadrature is not the explanation here.
The unasked-for part is directly on point: **"The geometric errors are exacerbated when
smoother, and necessarily wider, basis functions are used, such as uGIMP, or B-splines."**
This engine uses quadratic B-splines. That is a second, literature-backed mechanism for a
boundary-region force error, and it points at the same place as the contact band.

### 13.3 THE TEST: particles per cell at fixed grid

Vista job **923239**, 30 minutes requested, all arms `RC = 0`. `sphere_heave` hardcodes
`self.h = self.dx/2`, pinning PPC at 8, so this needed a property override on `h` in my
subclass; `h` is assigned exactly once at `sphere_heave.py:491` and read in nine places, so
the interception is complete and consistent. `PPC_DIVISOR = 2` reproduces the unmodified
path bit-for-bit. Every arm is the bcfix engine at the on-node floor, the lowest-leak
configuration measured, with `dx`, `dt`, substeps, the SDF, the band and the scene held
fixed. **Only the particle spacing moves.**

| PPC | particles | h | below floor | surface drop | sub | `fz` | excess | fitted k | near minus far |
|---|---|---|---|---|---|---|---|---|---|
| 3.375 | 252,379 | 12.50 mm | 0.330% | 82.08 mm | 67.92 mm | 27.298 N | +51.03% | 0.687 | +1.36 mm |
| **8.000** | 598,505 | 9.375 | 0.180% | 36.23 | 113.77 | 60.476 | **+35.51%** | **0.726** | +0.65 |
| 27.000 | 2,019,044 | 6.250 | 0.245% | 26.49 | 123.51 | 68.220 | +33.58% | 0.727 | -0.55 |
| 64.000 | 4,784,798 | 4.688 | 0.218% | 24.62 | 125.38 | 72.432 | **+38.41%** | **0.829** | -0.47 |

**Compare on `k`, not on the raw excess.** The arms sit at different submergences because a
coarser particle lattice drains and compacts more, so `sub` runs 67.9 to 125.4 mm. `k` is
the collider inflation in units of `dx` that reproduces the measured force AT THAT
submergence, so it removes the operating-point difference; the raw excess does not.

**SECTION 14 SUPERSEDES THE NUMBERS BELOW AND CONFIRMS THEIR CONCLUSION.** Three of these
four arms are NOT stationary on the last-50 window and they sit at different submergences,
so the `k_fit` column below carries two confounds. Section 14.2 redoes it at matched
submergence with the trend regressed out and blocked residual errors: the flatness in PPC
holds and tightens, every step under 0.62 sigma. The `k` rise to 0.829 at PPC 64 shown
below is an ARTIFACT of the unmatched operating point and does not survive. Read 14.2.

**RESULT, against the pre-registration.** Over the resolved subset, PPC 8 to 64, an **8.0x
span** with particle count from 0.6 to 4.8 million:

    k_fit  0.7259 -> 0.8287           measured log-log slope in PPC:  +0.0596
    PPC^-2 predicts a 98.4 percent fall.  PPC^-3 predicts 99.8 percent.

**The error is FLAT in PPC. The measured slope is +0.06 where the convergent hypotheses
require -2 or -3, and the sign is if anything the wrong way.** Eight times the particles,
4.8 million of them, does not reduce the error at all. **That is the pre-registered
signature of a grid-set plateau, and Wal07's mechanism survives its own test.**

Honest scatter: `k` over the three resolved arms is 0.726, 0.727, 0.829, a 13.5 percent
spread about the mean, and the PPC 64 point is the highest. So the correct statement is
**flat to within its own scatter and certainly not converging**, not "constant". A 13.5
percent spread is one seventh of the smallest fall either convergent hypothesis predicts.

### 13.4 What the sweep separates, which is more than it was asked to

**The surface drop converges in PPC and the force error does not.** Drop falls 82.08 to
36.23 to 26.49 to 24.62 mm, flattening toward roughly 24 mm, while `k` stays flat. Those
are two different failures with two different remedies, and before this sweep they were
entangled in every run in this document. **Adding particles fixes the water column. It does
not touch the force.**

**E1 is refuted at four more arms**, `near minus far` = +1.36, +0.65, -0.55, -0.47 mm
against a requirement of 26.02 mm, across a 19x PPC span. That is nine instrumented arms
now, spanning two grids, three bands, two engines, two floor alignments and four particle
densities, and the estimator hypothesis has not come within 5 percent of its requirement in
any of them.

### 13.5 A correction to my own section 11, prompted by d11-accessor's 1f98170

Their hydrostatic column, re-graded with the blocked standard error criterion 3 already
mandates, gives g64 -0.6679 percent with blocked SE 3.3090 and g96 -0.7295 with 1.9954,
both stationary and inside the band. Their NOT GRADEABLE is withdrawn and **the ambient
pressure field is exonerated**, at 10 to 17 blocked SE from job B's excess.

**That does not retract section 11 or 12, and the distinction is worth stating because it
is easy to blur.** My leak analysis never claimed the leak corrupts the ambient pressure
field. It claimed the leak lowers the WATER LEVEL, which changes the submerged cap volume
in criterion 3's denominator, which is a geometric effect on the analytic term and not a
pressure effect on the measured one. Section 12.4 measured that directly: three leak levels,
`ratio = 0.03474*(percent below floor) + 1.35922`, extrapolating to **+35.9 percent at zero
leak**. Their result and mine agree: **the leak is not the explanation**, they by showing
the pressure field is clean and I by showing the excess survives the leak's removal.

---

## 14. Locking against projection, and a correction to my own section 13.3

The coordinator supplied a clean discriminator with Zhao, Jiang and Choo 2023 (Zha22d,
volumetric locking, arXiv 2209.02466): **locking predicts an error that GROWS with
particles per cell** (more integration points per element, more incompressibility
constraints) **and is insensitive or ADVERSE to grid refinement**, while **Wal07's
projection bias predicts a plateau set by the grid and INSENSITIVE to PPC**. Opposite
predictions on one sweep.

**The sweep had already run.** Job 923239 landed and was committed as `d826c8a` before the
dispatch arrived. What follows re-analyses it properly rather than re-running it, and the
re-analysis corrects my own numbers.

### 14.1 THREE OF MY FOUR PPC ARMS WERE NOT STATIONARY, AND I COMPARED THEM ANYWAY

By the project's own `blocking.stationarity` at 3 sigma, on the graded last-50 window:

| arm | stationary? | halves | slope |
|---|---|---|---|
| PPC 3.375 | **False** | 4.56 | 8.24 |
| PPC 8 | **False** | 3.71 | 4.77 |
| PPC 27 | **False** | 3.12 | 3.62 |
| PPC 64 | True | 2.25 | 2.70 |

**Stationarity improves monotonically with PPC, and only the finest arm had settled.**
Section 13.3 compared four last-50 means of which three were still drifting, and it did so
eleven days after this project's own settle-transient finding recorded that a transient
"inflated a spread 6.07 to 1.94x and INVERTED a gate ordering". The arms also sat at
different submergences, 67.9 to 125.4 mm, because a coarser lattice drains more. **Two
confounds, both mine.**

### 14.2 The corrected estimator, and it is the one the question deserved

Compare the force **at a matched submergence of 130 mm**, with the trend inside the band
regressed out and the residual standard error **blocked**. The matched band is a transient
slice, so a raw mean carries the trend into its own error bar; regressing `sub` out first
answers the question actually asked, which is force at a stated submergence.

**PPC PRONG**, bcfix engine, g64, floor on-node, 19x span in PPC:

| PPC | frames | excess at 130 mm | +/- |
|---|---|---|---|
| 3.375 | 17 | +32.23% | 22.97 |
| 8 | 88 | +46.17% | 8.04 |
| 27 | 168 | +40.49% | 4.45 |
| 64 | 223 | +41.69% | 3.32 |

Pairwise: 3.375→8 **0.57 sigma**, 8→27 **0.62**, 27→64 **0.22**, end-to-end **0.41**.

**FLAT IN PPC. Every step is under two-thirds of one blocked standard error, across a 19x
span topping out at 4.8 million particles.** Locking's first prong requires the force to
RISE with PPC. It does not. **Locking is refuted as the dominant term, and the projection
plateau is what the data looks like.**

**GRID PRONG**, same engine, PPC 8, 2x span in dx:

| dx | frames | excess at 130 mm | +/- |
|---|---|---|---|
| 18.75 mm | 88 | +46.17% | 8.04 |
| 12.50 mm | 85 | +28.11% | 6.14 |
| 9.375 mm | 35 | +21.50% | 10.55 |

Pairwise: **1.79 sigma**, **0.54**, end-to-end **1.86**. The excess is **linear in dx**,
`excess = 2.669*dx_mm - 4.217`, extrapolating to **-4.2 percent at dx -> 0**.

**Locking's second prong requires refinement to make it worse or leave it alone. The sign
is against locking: refinement makes it monotonically BETTER by 24.68 points. But at 1.86
sigma end-to-end that is BELOW this project's 3 sigma bar, so it is suggestive and not
established**, and the g128 point rests on 35 frames.

### 14.3 THIS OVERTURNS MY OWN PUBLISHED CLAIM, AND THE CORRECTION MATTERS FOR JOB C

Sections 3.2 and 7.2a of this document say the discrepancy "is NOT converging to zero under
refinement" and estimate a non-zero asymptote near +24 percent. **That estimate was computed
from last-window ratios at UNMATCHED submergence and it is withdrawn.** At matched
submergence with the trend removed the same three runs give a straight line in `dx` through
approximately the origin.

The two are not in conflict about the data; they are two readings of the same three runs,
and the earlier one compared arms sitting at 102 to 114 mm submergence as though they were
the same state. **A resolution ladder whose operating point moves with resolution cannot be
read as a convergence study without matching the operating point first.** That is the
general form of the error and it is worth more than the particular number.

**Consequence for job C, which moves again**: if the excess really is O(dx) and convergent,
then refinement is a remedy rather than a dead end, and section 8's "do not run job C at
`n_grid 117`" should become "run it finer". At 1.86 sigma that is not yet a recommendation.

**Vista job 923291 is the arm that settles it**: g192, `dx = 6.25 mm`, doubling the lever to
3x end-to-end. `0.075/6.25e-3 = 12` exactly, so the floor stays on a grid node where the
`<=` engine suppresses the leak. **Pre-registered before submission: the O(dx) line predicts
+12.5 percent at 130 mm submergence; a value near the g128 21.5 percent or above refutes
convergence and restores a non-zero asymptote.**

### 14.4 What is NOT settled, and the third channel

- **Zha22d's magnitude overlap is not a diagnosis and I have not read it.** The coordinator
  read it; I did not, and its strip footing is an elastoplastic solid rather than weakly
  compressible water. What I tested is its stated PPC signature, and that fails. **Locking
  could still contribute a sub-dominant term**; refuting "dominant" is not refuting "present".
- **The decisive locking test is a compressibility sweep, and I did not run it.** Locking is
  a nearly-incompressible phenomenon, so raising the bulk modulus should worsen it while
  leaving a projection bias alone. `BULK` is a module constant in the scene, reachable by
  monkeypatch from my own file without editing it. That is the one-parameter test that would
  settle locking directly rather than by its PPC signature.
- **Sch19e remains a LEAD and no more.** It has no DOI, resolves only to a Semantic Scholar
  record, and its PDF is not retrievable, so the "wall momentum zeroing distorts stress
  several grid lengths into an object" claim reaches me only through a search summary.
  **Ste08, which I did read, supplies a verified relative of it**: "The geometric errors are
  exacerbated when smoother, and necessarily wider, basis functions are used, such as uGIMP,
  or B-splines." This engine uses quadratic B-splines, and that is a boundary-region
  geometric error with a primary source behind it.
- **The searches prescribed my controls hours before I ran them.** The 17:44 search called
  for nested exclusion radii including zero, local vertical columns, a level-set
  reconstruction, and "a body-off hydrostatic run provides the estimator bias independently
  of body loading". I ran three of those four and d11-accessor ran the fourth. **The
  index reads 8 of 21 searches, so neither of us could see it.** The cost was not the GPU
  time, which was three minutes; it was that we could not know the design was already
  vetted, and a design nobody has vetted gets pre-registered thresholds and a self-test,
  which is what those three minutes actually bought.

---

## 15. Specification robustness, and my second correction to the same claim

d15-settle (`claude/r9-settle`) warned that the g128 point rested on 35 frames and that an
`N_eff` computed from a window that barely exists is unreliable rather than merely small,
and said to check that first because it is upstream of everything. **Checking it found a
larger problem than the one flagged, and it is systematic rather than statistical.**

### 15.1 The blocking is fine. The BAND is not

`blocking.blocked_se` reports `converged = True` and `se_is_lower_bound = False` at every
grid point, including g128, with `tau_int` at 1.00 to 1.36 after `sub` is regressed out.
So the residuals are near-uncorrelated and the standard errors are honest **as standard
errors**. d15-settle's specific worry does not bite here, and their arithmetic about `N_eff`
does not apply: this is an instantaneous force, the velocity-like family, and the blocking
ladder converged.

**But the ESTIMATE moves with the matching band by more than the effect being measured.**
Excess at 130 mm submergence, linear in `sub`:

| band | dx 18.75 | dx 12.50 | dx 9.375 | end-to-end | monotone? |
|---|---|---|---|---|---|
| [126, 140] mm | 46.17 | 28.11 | 21.50 | -24.68, 1.86 sigma | yes |
| [115, 150] mm | 31.55 | 16.80 | 23.91 | -7.63, 0.94 sigma | **no** |
| [105, 155] mm | 31.45 | 24.40 | 16.74 | -14.71, 2.41 sigma | yes |

**The g96 point moves 28.11 to 16.80 to 24.40 across bands, and in the middle band the
monotonicity breaks.** A linear model for `fz(sub)` is evidently not adequate over the
wider windows, so the intercept at the reference submergence shifts with the window. That
is a specification sensitivity, not noise, and no amount of extra frames fixes it.

### 15.2 Six specifications, and what survives all of them

Three bands times two models, linear and quadratic in `sub`:

**PPC PRONG, excess at 130 mm across PPC 8 / 27 / 64:**

| specification | 8 | 27 | 64 | change |
|---|---|---|---|---|
| linear [126,140] | 46.17 | 40.49 | 41.69 | -4.5 |
| linear [115,150] | 31.55 | 37.21 | 40.16 | +8.6 |
| linear [105,155] | 31.45 | 34.16 | 39.38 | +7.9 |
| quadratic [126,140] | 49.15 | 53.67 | 51.74 | +2.6 |
| quadratic [115,150] | 44.42 | 38.94 | 40.08 | -4.3 |
| **quadratic [105,155]** | **42.28** | **43.26** | **42.52** | **+0.2** |

**The change straddles zero in sign and never exceeds the standard errors of 3.3 to 9.3
points. In the best-conditioned specification, the widest band with the more flexible
model, it is +0.2 points over an 8x PPC span.** The PPC prong is robust: **flat under
every specification tried, and flattest where the estimator is best conditioned. Locking's
first prong stays refuted.**

**GRID PRONG, end-to-end dx 18.75 to 9.375:**

| specification | change | sigma | monotone? |
|---|---|---|---|
| linear [126,140] | -24.68 | 1.86 | yes |
| linear [115,150] | -7.63 | 0.94 | no |
| linear [105,155] | -14.71 | 2.41 | yes |
| quadratic [126,140] | -35.29 | 1.91 | yes |
| quadratic [115,150] | -23.80 | 2.29 | yes |
| quadratic [105,155] | -19.99 | 2.59 | yes |

**Every one of the six is NEGATIVE and five of six are monotone. None reaches 3 sigma.**

### 15.3 THE CORRECTION, and it is my second on this same claim tonight

Section 14.3 withdrew my earlier "not converging, asymptote about +24 percent" and replaced
it with "linear in `dx`, extrapolating to -4.2 percent at `dx -> 0`". **That replacement was
also over-stated and is now itself corrected.** The defensible position is between the two:

- **DIRECTION: established, and by consistency rather than by significance.** Refinement
  improves the excess in **all six** specifications. A sign that survives three bands and
  two functional forms is not a band artifact. **This contradicts locking's second prong in
  every specification tried**, which strengthens section 14.2's refutation rather than
  weakening it.
- **MAGNITUDE: NOT established.** The end-to-end change spans -7.6 to -35.3 points
  depending on band and model, a factor of 4.6, and the largest significance reached is
  2.59 sigma against this project's 3 sigma bar.
- **THE EXTRAPOLATION IS WITHDRAWN.** `excess = 2.669*dx_mm - 4.217` and its "-4.2 percent
  at `dx -> 0`" were one specification's answer quoted as if specification-independent. **No
  asymptote is determined by this data, neither zero nor +24 percent.** The honest statement
  is that the excess falls with refinement by an amount this data cannot pin down.

**Twice in one night I converted a real signal into a number the data did not support, and
both times the mechanism was the same**: I picked one analysis window, got a clean-looking
fit, and reported the fit rather than the fit's sensitivity to the choice. The first time
the window was "last 50 frames at whatever submergence the run happened to reach"; the
second time it was "sub in [126,140] mm, linear". **The cheap defence is not a better window,
it is to report the spread across several defensible windows before quoting any coefficient
from one of them**, which costs one loop and would have caught both.

### 15.4 What this does and does not change

**Unchanged**: E1 refuted (sections 7, 12.5, 13.3), the leak accounting for about a third
(11.3, 12.4), criterion 3's PASS band being the size of the instrument's own resolution at
g64 (5, 7.2), the accessor being the projection route (13.1), locking refuted on its PPC
signature (14.2, 15.2), and the two Wal07 claims that did not survive reading the paper
(13.2). None of those rests on the grid-prong magnitude.

**Changed**: any statement about where the excess converges to. Section 14.3 said job C's
recommendation "moves again" to "run it finer" if the error is convergent. **That
recommendation is not supported at 2.59 sigma with a factor-of-4.6 spread in magnitude**,
and section 8's original position stands until a further grid point settles it. Vista job
923291 (g192, `dx = 6.25 mm`) is that point, and its value should be read against **all six
specifications**, not the one it was pre-registered against.
