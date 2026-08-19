# The job B force accessor: a designation that lives only in a source comment

Slot `d11-accessor`, branch `claude/r9-accessor`. Work done 2026-08-18 into 2026-08-19.
The filename carries `2026-08-18` because that is the path fixed in this slot's write
scope; the work crossed midnight. Not a transcription error.

Every number below was recomputed by this slot from the raw per-frame series pulled
read-only off Vista, with stdlib code written before the sibling documents' result tables
were read. Nothing here is transcribed from another slot unless it is explicitly labelled
as theirs.

---

## READ THIS FIRST: THERE IS NO CODE FORK, AND THERE NEVER WAS

**One implementation, three disagreeing prose statements. The defect was only ever the
specification.**

`sphere_heave.py` has exactly **one distinct content** across all five copies in this
repository, by `git hash-object`. Both accessors were verified correct by rebuilding them from
raw geometry, independently of the emitted fields, and they reproduce to machine precision
(section 14). **A reader who takes away "the code was wrong" will go looking for a fix that
does not exist.** What disagreed was three pieces of English about the same working code:

| where | what it said | which accessor |
|---|---|---|
| `docs/R5_PHYSICS_BATCH_MANIFEST.md` criterion 3, before amendment | "the steady vertical reaction against 69.2180 N" | **nominal** |
| `sphere_heave.py` source comment, before amendment | "the number job B should actually be graded on" | **measured** |
| `analysis/r7_jobb_bcfix_ab.py:208` on branch `r7-collect` | `"THE DESIGNATED ACCESSOR"` | **measured** |

The fix was therefore never a code change. It was to make one document authoritative, name the
denominator **and** the window in it, and make the designation travel with the data so it
cannot drift away from it again.

---

## 0. The finding, stated first

**Criterion 3 of the batch manifest grades a quantity that the manifest and the source code
name differently, and the code's name has no authoritative basis. It exists only as a
comment. That comment has since propagated into at least four downstream sites in three
worktrees, two of which now assert the opposite of the manifest in their own printed
output.**

This is a stronger problem than "two numbers disagree". Two numbers disagreeing is a
measurement question. A *designation* that exists only as a comment is a governance
question: nothing in the repository can adjudicate it, so each new tool re-decides it, and
they have decided differently. The manifest is the pre-registration. It is supposed to be
the thing that cannot be re-decided after seeing data. On this criterion it has been
silently overridden by a docstring.

The practical urgency: **the denominator choice, and nothing else, decides whether job B's
floor-BC treatment run passes criterion 3 and unblocks the ladder.** That is demonstrated
in section 5. Job C is scheduled to reuse this template and has not run.

---

## 1. What the two denominators actually are

Read directly from `simulation/r5_physics/sphere_heave.py` at HEAD `6ed163e`:

| accessor | line | denominator |
|---|---|---|
| `fz_over_analytic_measured` | `:818` | `analytic_buoyancy_at_measured_surface_N` (`:813`, formed at `:787` from `buoyancy_at(surf)`) |
| `fz_over_analytic_nominal` | `:819` | `RHO_W_BENCHMARK * G_ENGINE * (2/3 pi R^3)` |

### The nominal denominator is a HEMISPHERE, not a fully submerged sphere

`2/3 pi R^3` is half of `4/3 pi R^3`. Computed live from the constants at `:146` and `:160`
and `ref_radius_m` in the emitted config:

```
998.2 * 9.81 * (2/3)pi(0.15)^3  =  69.2179867994 N     <- the nominal denominator
998.2 * 9.81 * (4/3)pi(0.15)^3  = 138.4359735989 N     <- a fully submerged sphere
```

`R5_PHYSICS_BATCH_MANIFEST.md:210` already says this correctly: "analytic buoyancy on the
submerged **hemisphere**". Any description of 69.2180 N as a fully-submerged buoyancy is
wrong by a factor of two, and the whole physical argument turns on it.

### 69.2180 N is also the sphere's own weight, and that is not a coincidence

```
m * g  =  7.056 kg * 9.81 m/s2  =  69.2193600 N        (Kramer 2021 Table 1 mass)
```

against the emitted `analytic_buoyancy_N = 69.2179868 N`, a gap of 0.0014 N or 0.002
percent. The config explains the gap itself: `ref_mass_from_half_submergence_kg` is
7.055860 against `ref_mass_kg` 7.056, recorded as
`ref_mass_route_disagreement_kg = 0.00014`. **Kramer chose the sphere's mass so that it
floats exactly at its equator.** So the nominal denominator is simultaneously the
design-waterline buoyancy and the body's weight, and those coincide by construction of the
benchmark. [read directly, emitted config of all four runs]

### So the two denominators answer different questions

The scene is a **pinned** sphere: `mode = fixed`, `free = False` in the config of all four
runs. It does not move, so there is no equilibrium condition it must satisfy.

- **Nominal, 69.2180 N.** The reaction the sphere would feel if the water stood at its
  design waterline. External to the run: it comes from Kramer's Table 1 constants and
  closed-form geometry, and no simulated quantity enters it.
- **Measured, `analytic_buoyancy_at_measured_surface_N`.** Archimedes evaluated on the
  spherical cap actually submerged, given the free surface the run actually has
  (`:768-769`, cap volume `pi h^2 (3R - h)/3`).

For a fixed body in still water, the physically correct reaction is the buoyancy on the
volume actually displaced. The tank drained during every run, so the sphere ended up proud
of the waterline and those two quantities came apart.

### They do not "disagree on the sign" in any pathological sense

There is one force. It sits between the two denominators, so the sign of the relative error
is forced to flip. On job 918240, late window:

```
fz = 53.5915 N,   measured denominator 35.7139 N,   nominal denominator 69.2180 N
53.5915 / 35.7139 = 1.5006   ->  +50.06 %
53.5915 / 69.2180 = 0.7744   ->  -22.58 %
```

Both are true simultaneously and neither is an error. **The defect is that the
specification never said which one it grades, and never named a window.**

---

## 2. Which quantity does each artefact ACTUALLY use

Established by reading the execution path and by running the tool, not by reading prose.

| artefact | what it actually grades | evidence |
|---|---|---|
| `docs/R5_PHYSICS_BATCH_MANIFEST.md:222` | **nominal**, "The steady vertical reaction against 69.2180 N" | read directly |
| `grade_job_b.py`, top-level `band` | **nominal**: `mean(fz)` against `TARGET_N = 69.2180` (`:47`, `:179-180`) | read directly and executed |
| `grade_job_b.py`, `measured_surface_criterion` | **measured**: `ratio_key = "fz_over_analytic_measured"` (`:154`) | read directly and executed |
| `sphere_heave.py:804-807` comment | **measured**, "is the number job B should actually be graded on" | read directly |

So on the primary path the grader and the manifest **already agree**: both are nominal. The
grader never reads the `fz_over_analytic_nominal` field at all; it recomputes the equivalent
from `mean(fz)`. The measured accessor is a documented companion that the file's own comment
at `:150-151` says is "reported ALONGSIDE the nominal grade, never instead of it".

**The lone dissenting voice is the comment at `sphere_heave.py:804-807`.** And it is the one
that won everywhere downstream.

Minor fork risk noted while reading: 69.2180 N is derived twice independently, symbolically
at `sphere_heave.py:819` and as a rounded literal `TARGET_N = 69.2180` at
`grade_job_b.py:47`. They differ by 1.3e-5 N, which is immaterial now but is two sources of
truth for one constant.

---

## 3. The designation-site inventory

This is the deliverable for the cross-worktree collision. **This slot may not edit any file
in this table except the two in its own worktree.** Someone with authority over those
branches has to act on it.

Search method: `/usr/bin/grep -rn "fz_over_analytic"` across `/Users/josie/can-it-ford`
including `renders/` and `data/`, excluding `.git`, `third_party`, `__pycache__`, and this
slot's own worktree. Board rows, session digests and the send log are excluded below as
transcripts rather than designation sites.

### Sites that ASSERT a designation

| file | line | exact text | asserts |
|---|---|---|---|
| `simulation/r5_physics/sphere_heave.py` (this worktree, in scope) | `804-807` | "`fz_over_analytic_measured` is the number job B should actually be graded on" | **measured** |
| `.claude/worktrees/r7-collect/analysis/r7_jobb_bcfix_ab.py` | `23` | "THE ACCESSOR. `fz_over_analytic_measured`. The designation is a source comment reading" | **measured** |
| `.claude/worktrees/r7-collect/analysis/r7_jobb_bcfix_ab.py` | `208-209` | `"THE DESIGNATED ACCESSOR"` / `"nominal, reported for contrast only"` | **measured** |
| `.claude/worktrees/r7-collect/analysis/r6_repeat_stats.py` | `241` | "`sphere_heave.py:669-670` designates `fz_over_analytic_measured` as" | **measured** |
| `.claude/worktrees/r7-collect/analysis/r6_repeat_stats.py` | `252` | `"MEASURED, the designated accessor"` | **measured** |
| `.claude/worktrees/r7-collect/docs/R7_G192_AND_JOBB_BCFIX_2026-08-18.md` | `570` | "the accessor the source designates" | **measured** |
| `.claude/worktrees/r7-collect/docs/HANDOFF_ROUND_7_2026-08-18.md` | `194` | "graded on `fz_over_analytic_measured`, the accessor `sphere_heave.py:669-670`" | **measured** |
| `docs/R5_PHYSICS_BATCH_MANIFEST.md` | `222` | "The steady vertical reaction against 69.2180 N" | **nominal** |
| `simulation/r5_physics/grade_job_b.py` | `47`, `179-180`, `243` | `TARGET_N = 69.2180`; top-level `band` from the nominal path | **nominal** |

Two further copies of `R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md` and
`HANDOFF_ROUND_7_2026-08-18.md` exist in `r8-persistence`, `r7-inflow`, `r8-priorart`,
`r7-pinned-span` and `slide-resolution-dependence-reconcile-a5bf74`. They are branch copies
of the same content, not independent assertions.

### Two stale line citations, both pointing at the wrong place now

`r6_repeat_stats.py:241` and `HANDOFF_ROUND_7_2026-08-18.md:194` both cite
`sphere_heave.py:669-670` for the designating comment. **At HEAD `6ed163e` that comment is at
`:804-807`.** `:669-670` currently falls inside the `measure_surface` docstring. The dispatch
that commissioned this slot carried the same stale `:669-670`. Anyone re-deriving the
designation from those citations today reads a different function.

### Consequence

Four of the nine asserting sites are executable code. Two of them print the words "THE
DESIGNATED ACCESSOR" to a human reader. **A reader of any r7-collect output is told, in
capitals, that the measured accessor is designated; a reader of the manifest is told the
target is 69.2180 N. Neither reader is given any reason to suspect the other document
exists.**

### THERE IS NO CODE FORK. This is a specification defect only

**Do not go looking for a divergent implementation; there is not one.** A future reader
finding three conflicting statements will reasonably assume they arose from three different
copies of the code. They did not.

Reported by the coordinating session's provenance audit
(`docs/R9_DISCREPANCY_REGISTER_2026-08-19.md` rows B2 and C) and **independently re-verified
here by content hash rather than accepted**:

```
3a9d6d7bb33ffb2fcf586f351ed78c1d52f7a666  worktrees/r5-physics/.../sphere_heave.py
3a9d6d7bb33ffb2fcf586f351ed78c1d52f7a666  worktrees/r8-force/.../sphere_heave.py
3a9d6d7bb33ffb2fcf586f351ed78c1d52f7a666  worktrees/r8-kramer/.../sphere_heave.py
3a9d6d7bb33ffb2fcf586f351ed78c1d52f7a666  worktrees/r9-kramer-extract/.../sphere_heave.py
ba046f2d366c64ff5a3647c26e75337884c9aadd  worktrees/r9-accessor/.../sphere_heave.py
```

Five copies, and **four share one hash. The fifth is mine and differs only because this
slot edited it during this unit.** Before that edit all five were byte-identical. So one
implementation defines both accessors identically everywhere, and only the prose around it
disagrees. The respecification therefore cannot desynchronise code from code; the risk it
carries is leaving prose behind, which is what the table above is for.

**Two refinements this slot adds to that finding:**

1. **The file does not exist on `main` at all.** `git ls-tree main -- simulation/r5_physics/`
   returns empty, and so does the same query for `docs/R5_PHYSICS_BATCH_MANIFEST.md`. Both
   the code and its governing manifest live only on feature branches.
2. **5 branches of 105 carry it**: `claude/r5-physics`, `claude/r8-force`,
   `claude/r8-kramer`, `claude/r9-accessor`, `claude/r9-kramer-extract`. That matches the
   five worktree copies exactly, so the enumeration is complete rather than merely
   consistent.

**Method warning, because my first attempt at (2) returned a false zero.** Enumerating
branches with `git cat-file -e "$b:simulation/r5_physics/sphere_heave.py"` printed **nothing
at all**, which reads identically to "no branch carries this file". It is wrong. zsh applies
its `:s` history modifier to `$b:simulation/...`, silently eating the path and resolving the
bare revision, and **double quotes do not protect against it**. `simulation/` is one of the
paths where this failure is silent rather than an error. Use
`git ls-tree -r --name-only "$b" -- <path>` instead, which is what produced the count above.

---

## 4. What each run reads, recomputed from the raw series

Four runs pulled read-only from Vista, byte sizes verified against the remote listing:

| job | path on Vista | bytes | what it is |
|---|---|---|---|
| 917909 | `$WORK/d4_jobB_917909/sphere_fixed_g64.json` | 51193 | first pilot, pre-instrumentation |
| 918043 | `$WORK/d4_jobB_918043/sphere_fixed_g64.json` | 124894 | instrumented, pre h/2 surface fix |
| 918240 | `$WORK/d4_jobB_918240/sphere_fixed_g64.json` | 170493 | **control**, post h/2 fix |
| 918450 | `$WORK/d4_jobBbc_918450/sphere_fixed_bcfix.json` | 170020 | **treatment**, floor-BC fix |

All four: `n_grid = 64`, `lim = 1.2`, `dx = 0.01875`, `mode = fixed`, `free = False`, 200
frames, `analytic_buoyancy_N = 69.21798679943727`.

Bands are the manifest's own: within 10 percent PASS, 10 to 25 REPORTABLE PARTIAL, beyond 25
FAIL.

### 918240, the control

| window | n | mean fz | vs 69.2180 | band | measured ratio | vs 1.0 | band |
|---|---|---|---|---|---|---|---|
| last 20 | 20 | 49.0696 N | -29.109 % | FAIL | 1.5029 | +50.286 % | FAIL |
| last 50 | 50 | 50.2651 N | -27.381 % | FAIL | 1.4918 | +49.177 % | FAIL |
| last 100 | 100 | 53.5915 N | -22.576 % | **PARTIAL** | 1.5006 | +50.056 % | FAIL |
| full 200 | 200 | 62.5218 N | -9.674 % | **PASS** | 1.4943 | +49.429 % | FAIL |

**Nominal spread 19.43 points, three different verdicts from one run. Measured spread 1.11
points, one verdict.**

### 918450, the floor-BC treatment

| window | n | mean fz | vs 69.2180 | band | measured ratio | vs 1.0 | band |
|---|---|---|---|---|---|---|---|
| last 20 | 20 | 64.0741 N | -7.431 % | PASS | 1.3580 | +35.803 % | FAIL |
| last 50 | 50 | 64.7223 N | -6.495 % | PASS | 1.3502 | +35.024 % | FAIL |
| last 100 | 100 | 66.4934 N | -3.936 % | PASS | 1.3435 | +34.355 % | FAIL |
| full 200 | 200 | 72.5631 N | +4.833 % | PASS | 1.3640 | +36.401 % | FAIL |

**The two accessors give opposite verdicts at every one of the four windows. Neither verdict
is a window artefact.** This reproduces the finding already reported by slot `r7-collect` at
`R7_G192_AND_JOBB_BCFIX_2026-08-18.md:626-627`; my figures agree with theirs to three
decimals at every window they and I share.

### 918043 and 917909

918043: nominal -29.109 / -27.382 / -22.576 / -9.674 percent (FAIL, FAIL, PARTIAL, PASS);
measured +64.187 / +62.666 / +63.076 / +61.080 percent (FAIL at all four).
917909: nominal -29.069 / -27.389 / -22.635 / -9.806 percent (FAIL, FAIL, PARTIAL, PASS); no
measured accessor, the run predates the instrumentation.

**The nominal accessor swings across all three bands on window choice in all three
pre-treatment runs.** That is not a property of one run.

### The h/2 pair is a clean instrument calibration

918043 and 918240 are the same scene, differing only by commit `7c9e0af`'s h/2 correction to
`measure_surface`. Verified rather than assumed:

- `fz` last-100 differs by **+0.000272 N**, or +0.00051 percent. Same physics.
- Surface drop differs by **4.68746 mm** against `h/2 = dx/4 = 4.6875 mm`, a match to
  **0.039 micron**.

So the pair isolates a pure denominator change and measures the estimator sensitivity
directly rather than by linearisation:

```
secant   d(ratio)/d(surface) = 0.027775 ratio-points per mm, over 4.687 mm
tangent  at the 918240 operating point (draft 0.099674 m, waterplane 0.062729 m2) = 0.025809 per mm
```

The secant reproduces slot `d9-kramer`'s 0.0277 independently. Consequence, carried forward
to section 6:

- **918240**: 18.022 mm of surface offset, **0.9612 dx**, accounts for the entire +50.056 percent.
- **918450**: 12.369 mm, **0.6597 dx**, accounts for the entire +34.355 percent.

---

## 5. Why the nominal accessor cannot carry criterion 3 as written

Three independent reasons, all measured.

### 5.1 It has no steady value, and the manifest's own tool says so

`blocking.stationarity` at `grade_job_b.py:65`'s threshold `STATIONARITY_N_SIGMA = 3.0`, on
the window the tool itself selects (frame 100 onward, `DEFAULT_DROP_FRAC = 0.5`):

| run | `fz_N` | `fz_over_analytic_measured` |
|---|---|---|
| 918043 | not stationary, slope 8.52 sigma | stationary, slope **0.15 sigma** |
| 918240 | not stationary, slope 8.52 sigma | stationary, slope **0.64 sigma** |
| 918450 | not stationary, slope 3.95 sigma | stationary, slope **1.08 sigma** |

This reproduces `r7-collect`'s table at `R7_G192_AND_JOBB_BCFIX_2026-08-18.md:689` exactly.

### 5.2 The drift dwarfs the error being claimed

Criterion 5 already requires the drift be reported "against the error being claimed". Doing
that for criterion 3's own quantity:

| run | drift across the graded window | as a fraction of the error being claimed |
|---|---|---|
| 918240 nominal | 12.833 N | **82.1 %** |
| 918450 nominal | 7.118 N | **261.3 %** |
| 918240 measured | 0.0164 ratio | 3.3 % |
| 918450 measured | 0.0260 ratio | 7.6 % |

On the treatment, the series moves 2.6 times further during the window than the error the
window is being used to measure.

### 5.3 The band changes DURING the run, and the treatment's PASS expires 8 frames after the run ends

Projecting each run's own late-window trend. **This is a labelled extrapolation of a trend
that `blocking.stationarity` rejects, not a measurement.** Its only purpose is to size the
PASS margin against the drift of the series producing it.

- **918240** crosses the PARTIAL/FAIL edge at **frame 163, inside the 200-frame run.** The
  control's nominal reading changes band mid-run.
- **918450** reaches the PASS/PARTIAL edge at **frame 208**, eight frames after the run
  stopped, and the PARTIAL/FAIL edge at frame 353.

So the treatment's window-robust PASS is a decaying series caught inside the band. Its margin
to the edge (3.936 points at last-100) is smaller than its own drift across that same window
(10.28 percent of target). A criterion that names the nominal denominator and no window would
have recorded a PASS here and unblocked the ladder on that basis.

---

## 6. Why the measured accessor can carry it, and precisely what it cannot claim

### What it does well

1. **It matches the physics of the scene.** The sphere is pinned and the tank drained.
   Archimedes on the volume actually displaced is the correct closed form for the reaction on
   a fixed body; 69.2180 N is the reaction at a waterline that did not exist during the
   measurement.
2. **It matches criterion 3's own pre-registered prior.** The manifest sets the expectation
   at "7.3 to 7.7 percent" from the box-SDF path. That is a *coupling* accuracy prior. Only
   the measured accessor isolates coupling accuracy; the nominal one is coupling error and
   tank drainage combined, and the two partly cancel.
3. **Its verdict is window-robust**, 1.11 to 3.11 points of spread against the nominal
   accessor's 19.43.

### What it emphatically cannot claim

**(a) Stationarity here is not convergence.** Slot `r7-collect` makes this point at
`R7_G192_AND_JOBB_BCFIX_2026-08-18.md` and it is correct, so it is repeated here rather than
quietly dropped: a stationary ratio formed from two co-trending non-stationary series is
evidence that numerator and denominator are falling together, not that the measurement has
settled. `surface_z_measured_m` is non-stationary at 19.98 sigma (control) and 16.90 sigma
(treatment) in the same window. The correct claim is therefore the weaker one, which is
still sufficient for a grading criterion: **the VERDICT does not depend on window choice.**
Convergence is a separate, open question.

**(b) The denominator is produced by the pipeline under test.** CLAUDE.md's August 4 audit
item 6 is explicit that a gate comparing against a value derived from the same pipeline
"cannot fail for a reason external to the code". That objection has force here and must be
stated. It is mitigated but not removed: the measured denominator is a hybrid, taking one
simulated input (the free surface) and closed-form geometry plus Kramer's constants for
everything else, and it demonstrably *can* fail, since it currently reads +50 percent.

**(c) The estimator is blind exactly where the force is generated.** `measure_surface` at
`:698` keeps only particles with `r > 2.0 * self.radius`, excluding everything within 2R of
the sphere axis, which is precisely where the pressure generating `fz` acts. The exclusion is
deliberate and its stated reason (meniscus and splash are local deformation, not the tank's
free surface) is sound. But it means the near-field surface is unmeasured **by construction**,
so a surface-estimator explanation for the discrepancy cannot be excluded by this instrument.
And from section 4: 0.96 dx of surface offset on the control, 0.66 dx on the treatment, would
account for the whole thing with zero physics error.

**Therefore: a PASS on criterion 3 as respecified below would NOT by itself constitute a
coupling validation, and must not be reported as one, until the surface estimator is
validated in the near field.** That validation is out of scope for this slot and is flagged in
section 10.

### The escape hatch worth naming

The ambiguity is proportional to the drainage. If `surface_drop_m` were zero the two
denominators would be identical by construction and this entire question would evaporate. The
floor-BC fix already cut the drop from 5.033 cm to 2.884 cm (last-100 means). **Fixing the
drainage dissolves the defect; choosing a denominator only manages it.**

---

## 7. The respecified criterion 3

Written into `docs/R5_PHYSICS_BATCH_MANIFEST.md` by this slot. It names a denominator, a
window, and a reason the window is defensible, and it adds a robustness gate so the choice of
window cannot be quietly load-bearing again.

> **Graded quantity:** `fz_over_analytic_measured`, that is `fz_N` divided by
> `analytic_buoyancy_at_measured_surface_N`, Archimedes on the spherical cap actually
> submerged at the free surface the run actually has.
>
> **Primary window:** the last 50 percent of frames. Defensible because it is fixed in
> advance rather than chosen from the data, it is the coarsest defensible transient
> exclusion, and it is already what `grade_job_b.py:53` applies as `DEFAULT_DROP_FRAC`.
>
> **Bands, unchanged:** within 10 percent PASS, 10 to 25 REPORTABLE PARTIAL, beyond 25 FAIL.
>
> **Window-robustness gate.** The band must be identical at last-20, last-50, last-100 and
> full-series. If it is not, the run is NOT GRADEABLE on window sensitivity and that is
> reported, never resolved by choosing a window.
>
> **Stationarity gate, on the graded quantity only.** The graded ratio must pass
> `blocking.stationarity` at 3.0 sigma on the primary window. Non-stationarity of the raw
> `fz_N` series is expected and is not disqualifying, per criterion 5.
>
> **Mandatory companion, never suppressed:** the nominal ratio against 69.2180 N, with its
> own window table, plus `surface_drop_m`. Where the two disagree, that disagreement is the
> finding: it separates a coupling error from a draining tank.
>
> **Standing caveat that travels with any PASS.** The denominator depends on a free-surface
> estimate that excludes every particle within 2R of the sphere axis, which is where the
> pressure generating `fz` acts. Measured sensitivity is 0.0278 ratio-points per mm, so
> about 1 dx of surface offset at g64 spans the entire discrepancy currently observed. A
> PASS on this criterion is not a coupling validation until that estimator is validated in
> the near field.

### What changed in the code

`grade_job_b.py`, restructured so the tool matches the criterion:

- The top-level `band` now comes from the graded quantity and from nowhere else. It
  previously came from the nominal path while the graded number sat one level down inside
  `measured_surface_criterion`, so a machine reading `band` got a verdict on a quantity the
  manifest does not grade. New keys `graded_quantity`, `criterion3` and `nominal_companion`
  make the structure explicit. All previous top-level keys are retained so existing readers
  do not break, with a comment marking them as companion values that must not be banded from.
- The window-robustness gate and the stationarity-on-the-ratio gate are implemented and both
  are reported, including the full four-window sweep for **both** quantities.
- The nominal companion is always emitted and carries `drift_as_pct_of_claimed_error`, which
  is what criterion 5 has always asked for and is what exposes job 918450's PASS.
- `_band_of` replaces two separate inline band expressions that happened to agree. One
  definition, no fork.
- One behaviour change worth flagging: **no run now returns a top-level `NOT GRADEABLE`
  purely because `fz_N` is non-stationary.** Job 917909 still returns `NOT GRADEABLE`, but
  for the correct reason, which is that it predates the instrumentation and does not contain
  criterion 3's graded field at all.

`sphere_heave.py`: the designating comment no longer designates and now points at the
manifest; and the emitted config carries a new `criterion3_spec` block so the JSON says which
field is graded without a reader having to consult a comment in a file that is absent from
`main`. **No accessor was deleted and no emitted key was renamed**, because those keys are a
data contract read by scripts on branches this slot may not edit.

### This also resolves the criterion 3 / criterion 5 contradiction

Criterion 5 says a NOT-STATIONARY verdict is "expected, not disqualifying", yet
`grade_job_b.py` returns `NOT GRADEABLE` on exactly that ground, which is why **all four runs
currently return NOT GRADEABLE**, verified by execution this session. Applying the
stationarity gate to the *graded ratio* rather than to the raw force resolves it: `fz_N` may
be non-stationary (criterion 5 says so), while the graded ratio is stationary at 0.15 to 1.08
sigma, so the run is gradeable. Both criteria are satisfiable at once.

---

## 8. What this does to job B's recorded verdict

**Direct answer to the question the dispatch asked explicitly: yes, job B still FAILS
criterion 3 under the respecified criterion, and it fails at every window on both the control
and the treatment.**

| run | respecified criterion 3 | old nominal reading |
|---|---|---|
| 917909 | not gradeable, no measured accessor exists | swings FAIL / PARTIAL / PASS |
| 918043 | **FAIL**, +61.1 to +64.2 percent | swings FAIL / PARTIAL / PASS |
| 918240 control | **FAIL**, +49.2 to +50.3 percent | swings FAIL / PARTIAL / PASS |
| 918450 treatment | **FAIL**, +34.4 to +36.4 percent | PASS at all four windows |

So the respecification does **not** rescue job B and does not change the headline. What
changes is that the FAIL now rests on a criterion stated in the pre-registration rather than
on a docstring, and the PASS that the nominal denominator produces on the treatment is
correctly identified as a transient inside a decaying series.

### The A/B's answer, as required

The floor-BC treatment is a genuine and large improvement and this respecification does not
diminish it: the measured error falls from +50.06 to +34.36 percent (15.7 points), surface
drop falls from 5.033 cm to 2.884 cm, and the reaction rises from 53.59 N to 66.49 N. **The
A/B's direction is unchanged under either denominator. Only its verdict changes**: FAIL under
measured at every window, PASS under nominal at every window. Under the respecified criterion
the A/B reads "large confirmed improvement, still failing", which is what both accessors agree
on once the nominal PASS is read with its drift attached.

### Not corrected by this slot

`docs/R5_PHYSICS_JOB_B_RESULT.md` is outside this slot's write scope. Read live: it documents
job **917909** only, its headline is already "NOT GRADEABLE", and it contains no measured-
accessor figure, so it carries no claim that this work falsifies. It does not currently need a
correction on this point. `R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md:517`, also out of
scope, states "JOB B: FAIL on criterion 3" while grading on the measured accessor. **Its
verdict survives this respecification; its justification changes**, because criterion 3 now
actually names the accessor it used.

---

## 9. What this means for job C, which has not run

Job C is the free-decay comparison and it is `free = True`, not pinned. Three consequences:

1. **A freely floating sphere finds its own draft.** The pinned-versus-drained mismatch that
   makes the two denominators diverge is a property of pinning the body while the water
   leaves. A free body follows the surface down. The gap between the accessors should be much
   smaller in job C, which is a testable prediction and a good check that this diagnosis is
   right.
2. **Criterion 3 is a hydrostatic criterion and job C is graded on displacement**, against
   Kramer's 0.090 / 0.270 / 0.450 mm per-drop-height tolerances. The manifest already says at
   `:233-235` that those are displacement tolerances and cannot grade a force check. So the
   denominator question does not propagate into job C's own headline metric.
3. **It propagates into job C's setup instead.** If job C inherits the draining tank, its
   equilibrium draft is wrong before the drop even starts, and a decay period measured about
   a wrong equilibrium is not comparable to Kramer. **That is the thing to fix before job C
   runs, and it is the same fix that dissolves this defect: stop the drainage.**

---

## 10. The two options, and this is Josie's call not mine

The manifest says at `:214` "Any FAIL stops the ladder." Job B FAILS under either denominator
once the nominal PASS is read with its drift attached. The decision is what to do about that.

### Option A: hold the ladder stopped, fix the drainage, re-run job B

**For.** The FAIL is real and window-robust on the graded accessor. The drainage is a scene
defect that is already partly diagnosed and partly fixed, with 15.7 points of graded error
removed by one character of engine change. Fixing it collapses the accessor ambiguity
entirely, because both denominators converge as the drop goes to zero. It also removes the
prerequisite risk for job C in section 9.3. The pre-registration is honoured, which is the
whole reason it exists.

**Against.** Cost. The residual leak is now mostly through the walls and it grew, per
`r7-collect`, so the next fix is not obviously another one-character change. Job C stays
gated meanwhile, and there is no evidence yet that the +34 percent residual is drainage
rather than coupling or surface estimation.

### Option B: proceed to job C with the FAIL recorded and carried

**For.** Job C's headline metric is displacement, not force, so criterion 3's failure does not
directly invalidate it. Job C would generate independent evidence on whether the coupling is
wrong, from a free body, which is the regime the project actually cares about. The 15.7-point
improvement shows the trend is in the right direction.

**Against.** It overrides a pre-registered stop rule, which is exactly the class of decision
this project has repeatedly had to retract. Section 9.3 is the substantive objection: an
uncorrected drainage puts job C's equilibrium draft wrong before the drop begins, so job C may
be uninterpretable for the same underlying reason, and that would be discovered after
spending the allocation rather than before.

**What I would want before choosing:** the cheapest discriminator is not a decision, it is a
measurement, and it does not need a GPU beyond one short run. If the drainage is the whole
story, then the measured ratio must fall toward 1.0 as `surface_drop_m` falls. Two points
exist already (drop 5.033 cm at +50.06 percent, drop 2.884 cm at +34.36 percent). A third
point at a materially smaller drop would tell you whether the residual extrapolates to zero
or to a floor. **If it extrapolates to a floor, that floor is the coupling error and no amount
of drainage fixing will clear criterion 3.** That is a falsifiable test of the whole diagnosis
and it should probably precede either option.

---

## 11. What I could not verify

- **Whether the +34 percent residual is coupling error, surface-estimator bias, or remaining
  drainage.** These are not separable with the current instrument, per section 6(c). The
  surface estimator is blind within 2R of the axis by construction and about 1 dx of offset
  spans the entire effect. Rewriting the estimator was explicitly out of scope for this slot.
- **Any claim about job C's behaviour.** Section 9.1 is a prediction, labelled as such. Job C
  has not run.
- **The extrapolations in section 5.3** project a trend that the project's own stationarity
  test rejects. They size a margin; they are not measurements and are labelled at the point of
  use.
- **Whether the downstream sites in section 3 have been acted on.** This slot cannot edit
  them and did not.
- **`STATIONARITY_N_SIGMA` history.** The value read live at `grade_job_b.py:65` is 3.0. My
  first pass used 4.0 from a misread and was re-run at 3.0; every stationarity figure quoted
  here is at 3.0. No conclusion changed between the two.

---

## 12. How this verification was made falsifiable, and two traps I hit doing it

A criterion is only as good as the check that it was applied to the right quantity. The
neighbouring failure recorded last night is the reason: **a correct calculation attached to
the wrong quantity does not merely fail to support a claim, it launders it**, because the
check is displayed, it genuinely passed, and a reader cannot see that it was pointed
elsewhere. That is exactly how this defect produced a published claim in the first place.

### The verification does not assume which quantity is graded

It reads `graded_quantity` out of `grade_job_b.py`'s own output and asserts that the field it
independently averaged is that same field, **by name**. If criterion 3 is ever respecified to
grade something else, the check breaks rather than quietly continuing to verify the old
quantity. Result, on the criterion's own named window (last 50 percent of frames):

```
run      grader names                  grader mean  independent    abs diff
918043   fz_over_analytic_measured        1.630757     1.630757    2.22e-16
918240   fz_over_analytic_measured        1.500564     1.500564    0.00e+00
918450   fz_over_analytic_measured        1.343549     1.343549    2.22e-16
VERIFIED: 3 runs, each on the field the grader itself names as graded.
```

### And it was shown to be capable of failing

A passing check proves nothing until its failure path has fired. Five deliberately broken
inputs, each of which could otherwise have produced an empty comparison that reads as
agreement:

| input | outcome | exit |
|---|---|---|
| graded field stripped from every row | refused, "no criterion3 block" | 1 |
| `rows: []` | refused, "has no rows" | 1 |
| truncated mid-JSON | raised `JSONDecodeError` | 1 |
| file does not exist | raised `FileNotFoundError` | 1 |
| job 917909, genuinely lacks the field | refused | 1 |

The positive control exits 0. The count of runs compared is itself asserted, so a total load
failure cannot pass as agreement by comparing two empty sets.

**One honest imprecision:** the stripped-field case refuses with "grader produced no
criterion3 block" rather than the more specific "the graded field is ABSENT" message written
for it, because `grade_job_b.grade` returns `measured = None` first and my check catches that
stage earlier. Still loud, still exit 1, less informative than intended.

### Two traps I walked into during this unit

Recorded because both produced an answer I could have believed.

1. **A false zero from zsh.** Detailed at the end of section 3. A branch enumeration printed
   nothing and the correct reading was "5 of 105 branches carry this file". Nothing in the
   output distinguished the two.
2. **A pipeline exit code read as the program's.** I first measured the broken-input runs as
   `$PY ... 2>&1 | tail -3; echo "exit=$?"`, which reports **`tail`'s** status. Every one
   printed `exit=0` while the underlying Python was exiting 1. Had the refusals been silent
   rather than printing a visible message, that harness would have reported five clean
   passes. Re-measured without the pipe, which is where the table above comes from.

Both are the same failure as the defect this document is about: **a check that returns a
status it did not actually evaluate.** The verification table is quoted from the re-measured
run, not the first one.

---

## 13. Provenance

Raw series: `scp` read-only from Vista, byte sizes matched against the remote `find` listing
before use. Nothing was written to Vista. No GPU node was used; Vista job 920452 on c642-071
belongs to slot `d17-moving` and was not touched.

Independent recomputation: stdlib-only Python, no project imports, written before the sibling
result tables in `r7-collect` were read. The project's own `blocking.py` and `grade_job_b.py`
were then run against the same files as a cross-check and agree.

Corroboration and credit: slot `r7-collect` reached the window-robustness and stationarity
results independently and first, at `R7_G192_AND_JOBB_BCFIX_2026-08-18.md:615-700`. My
figures agree with theirs to three decimals. Their caveat on co-trending series is adopted
here and materially weakened my own argument, which is recorded in section 6(a) rather than
dropped. Slot `d9-kramer` first reported the two-accessor defect and the 0.0277 per-mm
sensitivity; the sensitivity is re-derived here from the 918043/918240 pair rather than
transcribed, and agrees.

---

# ROUND 9 CONTINUATION, 2026-08-19, same slot, with a GPU node

The first pass of this document was written with no node and no new runs. A node became
available afterwards (Vista job 922255, partition `gh-dev`, node c642-091, shared with slot
`d17-moving`). Everything below is new work. **Four of the six findings correct or qualify
this document's own earlier claims**, which is the point of writing the section rather than
quietly editing the tables above.

**Correction to the dispatch's own srun form, verified live:** job 922255 is on partition
**`gh-dev`**, not `gh`. The prescribed `srun -p gh ... --jobid=922255` names the wrong
partition for this allocation. The form that works is

```
srun -p gh-dev -N 1 -n 1 -t 00:30:00 --overlap --jobid=922255 <command>
```

All five flags are still required; only the partition differs.

## 14. Both accessors re-derived from raw geometry, and they are correct

The instruction was to recompute rather than transcribe. Done, from the raw fields only:
`fz_N`, `z_m`, `surface_z_measured_m` and `ref_radius_m`, rebuilding the spherical cap
`V = pi*sub^2*(3R - sub)/3` and both denominators from `RHO_W_BENCHMARK = 998.2` and
`G_ENGINE = 9.81`. The emitted ratio fields were **not** read. Script:
`scratchpad/recompute.py`, stdlib plus numpy only.

| run | max abs deviation, recomputed against stored |
|---|---|
| 918043 | `sub` 0, `cap` 0, `fb` 0, `ratio_meas` 0, `ratio_nom` 0 |
| 918240 | `sub` 0, `cap` 1.7e-18 m3, `fb` 2.1e-14 N, `ratio_meas` 8.9e-16, `ratio_nom` 0 |
| 918450 | `sub` 0, `cap` 0, `fb` 0, `ratio_meas` 0, `ratio_nom` 0 |

Nominal denominator recomputed independently: **69.217987 N**, matching `analytic_buoyancy_N`
in all three configs and the manifest's 69.2180 N.

**So both accessors are implemented correctly and the emitted ratio fields are what they
claim to be.** This closes the possibility that the disagreement was an arithmetic bug. It
also confirms, from a second direction, the coordinator's point that `sphere_heave.py` has
exactly one distinct content in this repo: **there is no code fork, there never was, and a
future reader should not go looking for one.** One implementation, three disagreeing prose
statements. The defect was always and only in the specification.

## 15. My own "about 1 dx" figure was a linearisation and it is 34.4 percent too small

Section 4 above reported "918240: 18.022 mm of surface offset, 0.9612 dx, accounts for the
entire +50.056 percent", and the same figure propagated into the manifest's standing caveat
and into `sphere_heave.py`'s `criterion3_spec` block as "about 1 dx at g64 spans the whole
discrepancy". **That was the error divided by the local secant, which is a tangent-line
estimate of a strongly convex function.** Replaced with an exact root-find: apply a uniform
surface offset to every frame in the window, recompute the cap denominator, bisect to the
target ratio. Script: `scratchpad/floor.py`.

| run | graded ratio | offset to reach 1.00 | in dx | in particle layers `h` |
|---|---|---|---|---|
| 918043 | 1.6308 | 32.177 mm | 1.716 | 3.432 |
| 918240 control | 1.5006 | 27.490 mm | 1.466 | 2.932 |
| 918450 treatment | 1.3435 | 24.904 mm | 1.328 | 2.656 |
| 918251 job C tank | 1.5060 | 33.424 mm | 1.778 | 3.555 |

Direct check of the linearisation: at the 18.022 mm the old figure named, the window-mean
ratio is **1.1342**, not 1.0000. The exact answer is 27.490 mm.

**The correction cuts against the easy explanation, which is why it matters.** At "about
1 dx" the surface-estimator escape hatch is cheap. At **1.33 to 1.78 dx, or 2.66 to 3.56
particle layers**, it is a much larger claim, and nothing has shown the estimator is wrong by
that much. The corrected figure strengthens the case that something real is being measured,
and it strengthens the FAIL. All three copies of the old figure are fixed.

## 16. RETRACTED AND REPLACED: criterion 3 does NOT sit at its own achievable floor

**I wrote the wrong answer here first and am recording the retraction rather than editing it
away, because the error is easy for the next person to repeat.**

The question was whether criterion 3 has the property P-2 has, where a gate sits at its own
achievable floor and therefore cannot distinguish a defect from the floor: P-2's
zero-penetration floor is 7.9 to 10.0 percent against a 10 percent gate. **My first answer was
"yes, and worse, the lever is 1.302x the whole band, so a PASS is not a physics result". That
is FALSE.**

**What was wrong.** I measured the instrument's resolution at the operating point these runs
are at now (ratio about 1.5, draft 0.0997 m) and then applied that number to a hypothetical
PASS. The sensitivity is state dependent:

```
d(ratio)/ds = -ratio * A_w / V_cap
```

**Both factors shrink toward a PASS at once.** Measured on 918240:

| operating point | ratio | draft | `V_cap` | `A_w` | tangent |
|---|---|---|---|---|---|
| observed (FAIL) | 1.5006 | 0.099674 m | 3.6447e-03 m3 | 0.062729 m2 | **0.025827 /mm** |
| a ratio-1.0 point | 1.0000 | 0.127164 m | 5.4669e-03 m3 | 0.069048 m2 | **0.012630 /mm** |

`V_cap` grows 1.500x and the ratio factor falls to 1.0, so the tangent falls **2.045x**.

**The corrected answer.** Half a particle layer of surface convention, `h/2` = 4.6875 mm at
g64, is worth:

| evaluated at | lever, ratio points | vs the 10.0 point PASS half-width |
|---|---|---|
| the observed FAIL points, four runs | **8.0 to 15.1** | comparable or larger |
| a ratio-1.0 (PASS) point, four runs | **4.6 to 6.3** | about half the band |

**So a PASS on criterion 3 would carry roughly half a band of surface-convention uncertainty.
Real caveat, not disqualifying. The P-2 pathology does not apply and the criterion is
two-sided.** The large lever at today's operating points is a symptom of how far these runs
sit from equilibrium, shallow draft and high ratio, not a property of the criterion.

**A second defect in the retracted version: the lever is direction dependent.** The response is
convex, so up and down differ, and I had quoted the larger direction as a single number. At
918240, `-h/2` gives **+13.020** points and `+h/2` gives **-11.338**. Across the four runs at
their own operating points the down-lever is 9.0 to 15.1 and the up-lever 8.0 to 13.0. **Quote
the range, and say which direction and which operating point.**

**Also worth stating plainly, since I leaned on it:** the `h/2` offset was a **bias
correction**, not a free choice of convention. Particle centres genuinely do sit `h/2` below
the fill line of their layer, so `+h/2` is the correct estimator and 918043 was simply wrong.
Using the size of that correction as a proxy for ongoing "convention ambiguity" is a
**demonstration of the sensitivity, not evidence that the current estimator is uncertain by
that much**. The honest reading is narrower than the one I first wrote: it shows what a
half-layer error in the surface would cost, and there was such an error, and it has been
fixed. It does not show that another one is present.

**Unchanged by every part of this: the FAIL is robust.** Reaching the PASS boundary of 1.10
needs 16.1 to 24.9 mm across the four graded runs, which is 1.72 to 2.66 particle layers, well
beyond any half-layer argument in either direction.

Three scales, for orientation: the Kramer benchmark's own experimental uncertainty about **0.3
percent** *(relayed from the project's deep-search summary, NOT verified against the primary by
this slot, treat as unverified)*, this band **10 percent**, the half-layer lever at a PASS point
**4.6 to 6.3 percent**.

**Band provenance, now stated in the manifest.** The 10 / 25 percent bands are a **project
choice**, this project's own box-SDF agreement of 7.3 to 7.7 percent rounded outward. No
external method's tolerance was imported to set them and none should be: benchmark cases
transfer across methods, reported tolerances do not. The 7.3 to 7.7 percent prior is itself an
internal self-consistency figure, so the band is anchored to a number of the same kind as the
thing it grades.

**Band provenance, now stated in the manifest.** The 10 / 25 percent bands are a **project
choice**, this project's own box-SDF agreement of 7.3 to 7.7 percent rounded outward. No
external method's tolerance was imported to set them and none should be: benchmark cases
transfer across methods, reported tolerances do not. The 7.3 to 7.7 percent prior is itself an
internal self-consistency figure, so the band is anchored to a number of the same kind as the
thing it grades.

## 17. Evidence-count correction: two independent runs, not three

Section 4 above says the nominal accessor swings across all three bands "in all three
pre-treatment runs. That is not a property of one run", listing 917909, 918043 and 918240.
**For this accessor 918043 and 918240 are one measurement, not two.** The nominal denominator
never touches the free surface, and the two runs differ only by the h/2 fix:

| pair | max abs `fz_N` difference | relative |
|---|---|---|
| 918043 vs 918240 | 1.49e-03 N | **4.3e-06** |
| 917909 vs 918043 | 1.82 N | **5.3e-03** |

Their nominal window readings are identical to four decimals, -29.109 / -27.381 / -22.576 /
-9.674 percent each. 917909 differs by three orders of magnitude more and is genuinely
separate. **The conclusion survives unchanged**, because two independent runs still both swing
across all three bands, but the enumeration was wrong and the same document identifies the
918043/918240 pair as an instrument-calibration pair fifteen lines later. It was counting a
controlled pair as independent replication in one sentence and as one instrument in the next.
Corrected in the manifest too.

## 18. The fix had never executed, because the machine that produces the data is on older code

Verified by `md5sum`, not assumed:

| copy | md5 | what it is |
|---|---|---|
| Vista `$WORK/d4_scene/sphere_heave.py` | `1c8994991e0029a89a047d9f3624ca78` | identical to commit `6ed163e`, the commit BEFORE the amendment |
| this worktree at `06c7786` | `8b9538dae28be68a7705616de065697d` | the amendment |

**The `criterion3_spec` block, whose entire purpose is to make the designation travel with the
data, was not on the machine that produces the data.** Job C is staged to launch from
`d4_scene`, so job C run today would have emitted output carrying no designation at all: the
exact failure the block was written to prevent, reappearing one layer down, in the gap between
the repository and the compute node.

Resolved without overwriting anything shared: the current file was staged to a **new**
directory `$WORK/d11_accessor/` (md5 verified `8b9538da...` after transfer) and run. The block
emits correctly, confirmed by reading `config.criterion3_spec` back out of
`repeat_seed0.json`. **This is the first time the amendment has ever executed.**

`$WORK/d4_scene/sphere_heave.py` was deliberately **not** overwritten. Overwriting a shared
staged file is a destructive action on a machine other sessions use, and it needs Josie's
say-so, not mine. **Whoever launches job C must re-stage first, or job C inherits the old
file.** That is a live pre-launch blocker, not a tidy-up.

## 19. True repeats, which nobody had: the graded accessor is reproducible

Every "repeat" quoted in this project so far has been the 918043/918240 pair, which differs by
a code change. Two genuine repeats were run today on one code version.

**Same seed (`seed 0`), against 918240, two days apart on a shared GPU:**

| quantity | max abs difference |
|---|---|
| `fz_N` | 1.32e-03 N |
| `surface_z_measured_m` | 3.99e-06 m |
| `fz_over_analytic_measured` | 1.12e-04 |

Window means of the graded ratio agree to **0.0006 ratio points** at all four windows
(last 20, last 50, last 100, full). **Run-to-run nondeterminism is not a source of the
discrepancy and can be set aside.** It also confirms retrospectively that the entire 13.019
point move between 918043 and 918240 was the code fix, with nothing left over for noise.
**Different seed (`seed 7` against `seed 0`), identical code, same node:** the graded ratio
moves **+0.405 ratio points** at the primary window (1.500561 to 1.504609), and 0.076 to 0.457
points across the four windows. `seed 7` grades **FAIL at all four windows** (+49.560 to
+50.461 percent), the same verdict, robust, stationary at 0.70 sigma. **N = 2 is
reproducibility, not an error bar**, and is not quoted as one.

**The complete sensitivity budget for the graded accessor at g64**, which is what the earlier
sections were missing and what makes the caveat quantitative instead of rhetorical:

| source | effect on the graded ratio |
|---|---|
| run-to-run, same seed | **0.0006 points** |
| particle sampling seed | **0.405 points** |
| surface convention, half a particle layer | **13.019 points** |
| *PASS band half-width, for scale* | *10.000 points* |
| the discrepancy actually observed | **34.4 to 63.1 points** |

**The surface-convention term dominates everything except the discrepancy itself, and it alone
exceeds the whole PASS band.** Numerics and sampling are three to four orders of magnitude
below the effect being argued about, so neither can explain it. That is a negative result and
it is worth as much as a positive one here: it removes two candidate explanations and leaves
the estimator and the physics.

## 20. THE VERDICT, stated plainly, on my criterion and my recomputation

**Job B FAILS criterion 3. The FAIL is robust and I do not consider it close.**

Criterion as I have landed it: **graded quantity** `fz_over_analytic_measured`; **primary
window** the last 50 percent of frames; **bands** within 10 percent PASS, 10 to 25 REPORTABLE
PARTIAL, beyond 25 FAIL, and those bands are a project choice, not a literature tolerance;
**window-robustness gate** across last 20, last 50, last 100 frames and the full series;
**stationarity gate at 3.0 sigma on the graded ratio**, not on `fz_N`.

Every figure below is recomputed by me from the raw series, not transcribed:

| run | what it is | primary window | all four windows | verdict |
|---|---|---|---|---|
| 918043 | pre h/2 fix | +63.076 % | +61.080 to +64.187 % | **FAIL** |
| 918240 | control | +50.056 % | +49.177 to +50.286 % | **FAIL** |
| 918450 | floor-BC treatment | +34.355 % | +34.355 to +36.401 % | **FAIL** |
| 918251 | job C tank, pinned | +50.601 % | +47.166 to +54.615 % | **FAIL** |
| `repeat_seed0` | true repeat, today | +50.056 % | +49.428 to +50.285 % | **FAIL** |
| `repeat_seed7` | second seed, today | +50.461 % | +49.560 to +50.461 % | **FAIL** |

**Six runs, four windows each, twenty-four gradings, every one a FAIL.** The best run in the
set, the floor-BC treatment, sits at +34.4 percent against a 25 percent FAIL threshold, so it
misses even the PARTIAL band by 9.4 points. Window choice cannot rescue it (spread 2.0
points), seed cannot (0.4 points), numerics cannot (0.0006 points), and the surface-convention
lever cannot (13.0 points, and 1.72 to 2.66 particle layers would be needed).

**Does the respecification change the answer? No.** It changes what the answer rests on. Under
the old unstated criterion, job B's verdict depended on which of two accessors a reader
happened to follow and, on the nominal one, on an unstated window: the nominal reading swings
FAIL / PARTIAL / PASS across the same 200 frames. Under the criterion as landed, the verdict
is FAIL at every window on every run, and it is stated in the pre-registration rather than in
a source comment.

**What the FAIL does and does not license.** Section 16 originally claimed a PASS here would
sit inside the instrument's own resolution, and **that claim is retracted**: measured at a
ratio-1.0 operating point the half-layer surface lever is 4.6 to 6.3 ratio points against a
10.0 point band, so a PASS would carry about half a band of convention uncertainty. **The
criterion is two-sided and can clear the ladder as well as stop it**, with that caveat
attached. What remains true is narrower: a PASS on criterion 3 alone is a hydrostatic
self-consistency result, not a coupling validation, and the surface estimator is still blind
within 2R of the axis. Validating it there is what would remove the caveat.

## 21. What this means for job C, updated by evidence rather than prediction

Section 9 above made a prediction about job C. Part of it can now be tested, because **the job
C tank has already run**, in fixed mode, as job 918251 (`n_grid 117`, `lim 2.2`, `depth 0.5`,
`dx` within 0.28 percent of job B's). Nobody had graded it. Graded now:

- **The bigger tank does not fix the discrepancy.** +50.601 percent at the primary window,
  against +50.056 percent in job B's tank. Essentially unchanged.
- **It does drain less in absolute terms.** Mean surface drop 3.596 cm against 5.033 cm.
- **The nominal companion is more misleading there, not less.** Its drift over the window is
  **672.8 percent of the error it claims** (against 82.1 percent in job B's tank), and it is
  **not window-robust**, reading PARTIAL at last-20 and PASS at the other three.

So domain size is not the explanation, and grading job C's hydrostatics on the nominal
accessor would produce a PASS built on a drift six times larger than the error claimed.
**Section 9's remaining prediction is untested**: 918251 is pinned, and the claim that a free
body follows the surface down still needs a `free = True` run.

## 22. Downstream sites that hard-code a designation, for their owners

Enumerated with file, line and quoted text, all **verified live at `claude/r7-collect` branch
head today**, not copied forward. None is in this slot's write scope and none was edited.

| file | line | exact text at head |
|---|---|---|
| `analysis/r7_jobb_bcfix_ab.py` | 23 | "THE ACCESSOR. `fz_over_analytic_measured`. The designation is a source comment reading" |
| `analysis/r7_jobb_bcfix_ab.py` | 208 | `("fz_over_analytic_measured", "THE DESIGNATED ACCESSOR")` |
| `analysis/r6_repeat_stats.py` | 241 | "`# the ladder", and sphere_heave.py:669-670 designates fz_over_analytic_measured as`" |
| `analysis/r6_repeat_stats.py` | 252 | `("fz_over_analytic_measured", "MEASURED, the designated accessor")` |
| `docs/R7_G192_AND_JOBB_BCFIX_2026-08-18.md` | 570 | "Graded on `fz_over_analytic_measured`, the accessor the source designates, against the manifest" |
| `docs/HANDOFF_ROUND_7_2026-08-18.md` | 194 | "Job 918240, graded on `fz_over_analytic_measured`, the accessor `sphere_heave.py:669-670`" |

**All six now name the right quantity**, because the manifest was amended to the measured
accessor, so no verdict downstream changes. What they still get wrong is the **authority**:
they cite a source comment, and two of them cite it by a line number.

**The line numbers have now drifted three times in three days.** `:669-670` was correct before
`6ed163e`, became `:804-807`, and after today's edits `:669-670` lands in the config dict and
`:804-807` lands in a docstring about `occupied_volume_m3`. **Do not repoint them. Cite
`docs/R5_PHYSICS_BATCH_MANIFEST.md` criterion 3 instead**, which is the authority, or read
`config.criterion3_spec` out of the run's own JSON, which now travels with the data.

## 23. What I still could not verify, added to section 11 rather than replacing it

- **Whether the +34 percent residual is coupling error, estimator bias, or drainage.** Still
  not separable, and section 16 now bounds how much of it the estimator could carry: to take
  the whole thing it would have to be wrong by 2.66 to 3.56 particle layers.
- **The Kramer 0.3 percent experimental uncertainty** is relayed from a deep-search summary and
  was **not** checked against the primary paper by this slot. Marked unverified.
- **The 2.28 percent per mm sensitivity** in `measure_surface`'s comment is unreconciled with
  the measured 2.7775 and the spec block's 2.78. I flagged it in place rather than overwriting
  it, because I could not reproduce 2.28 at any operating point I tried and do not know which
  quantity it belongs to.
- **Job C free-body behaviour.** Still a prediction. 918251 is pinned.
- **Whether any downstream site has been acted on.** Still cannot edit them; now enumerated
  for their owners in section 22.

---

## 24. THE FLOOR QUESTION IS STILL OPEN, and my retraction did NOT close it

**Said plainly, because leaving this implied would be the same error twice.** Section 16
retracted a claim about the *surface-convention lever*. That is a **sensitivity**, how much the
answer moves when a convention changes. **It is not the floor.** The floor is a different
quantity: the smallest `|ratio - 1|` this instrument could report **if the coupling were
perfect**. My retraction did not measure it, and nothing in this document does.

**So the question d19-priorcode raised about P-2 remains open for criterion 3, and here is
exactly how open.**

### What can be said

**Nobody has measured the floor for this configuration.** It would take a case with known-zero
coupling error in the Kramer sphere scene, and no such case has been run. The best available
proxy is this project's own SDF-collider agreement, `err_steady_vs_analytic_pct` of
**-7.6682** (`c1sdf_sdf_g64`) and **+7.2804** (`c1sdf_sdf_g96`) from job 894731, traced to
`docs/CONTEXT_CENSUS_2026-08-07.md:1049-1050`. **That is a different scene**, so importing it
here is an assumption, and it is labelled as one. It is also the same number the manifest
already used to set the band, so the band and the floor estimate are not independent.

### Against that proxy, criterion 3 does NOT have P-2's exact pathology

| gate | floor estimate | headroom |
|---|---|---|
| P-2, 10.0 percent | 7.9 to 10.0 percent | **0.000 to 2.100 points, the floor reaches the gate** |
| criterion 3, 10.0 percent | 7.28 to 7.67 percent | **2.332 to 2.720 points, the floor clears the gate** |

P-2's floor touches its gate, so a P-2 FAIL can be produced by a perfect simulation.
Criterion 3's floor clears its gate, but **by only 2.3 to 2.7 points out of 10**. That is thin,
and it means any criterion 3 reading between about 7.3 and 10 percent could not distinguish
good coupling from the floor. **The PASS band is mostly floor.**

### But it does not touch this decision, and here is the falsifiable reason

Job B's readings as a multiple of the proxy floor:

| run | reading | multiple of floor |
|---|---|---|
| 918450, the best run in the set | 34.355 % | **4.48x to 4.72x** |
| 918240 control | 50.056 % | 6.53x to 6.88x |
| 918251 job C tank | 50.601 % | 6.60x to 6.95x |
| 918043 worst | 63.076 % | 8.23x to 8.66x |

**The FAIL survives unless the true floor is at least 4.48x the project's own estimate**, that
is 34.4 percent rather than 7.3 to 7.7. Merely reaching the 25 percent FAIL threshold would
take a floor **3.26x** the estimate. **That is the falsifiable form of the claim**: produce a
zero-coupling-error case in this scene that reads above 25 percent and the FAIL becomes
uninformative. Nothing observed so far is anywhere near that, and the box-collider path, which
is the worst comparator on record, reads -37.91 and -21.28 percent in the same job 894731.

### Status, in one line

**OPEN in principle: the floor for this configuration has never been measured, and the PASS
band is mostly floor. CLOSED for this decision: job B fails by 4.5x to 8.7x the best floor
estimate available.** Measuring the floor properly is the work that would make a future PASS
on criterion 3 mean something. It is not needed to act on this FAIL.

---

## 25. THE DECISION PAGE, for a reader who has not read anything above

**What happened.** Job B is the Kramer floating-sphere pilot, the rung the ladder is currently
on. It was graded against a criterion that named a target number but not which of two force
measurements to apply it to, and not over what stretch of the run. Two measurements were live,
they differ by roughly a factor of two once the tank drains, and they disagree about the sign
of the error. Different tools followed different ones. **No code was wrong. The specification
was incomplete.**

**What has been fixed.** Criterion 3 now names the measurement (`fz_over_analytic_measured`),
the window (the last 50 percent of frames), the robustness check (the verdict must be the same
at last 20, last 50, last 100 frames and the full series), and where its pass/fail bands came
from (a project choice, not a number borrowed from any published paper). The designation is now
written into the run's own output file, so it travels with the data.

**What the answer is.** **Job B fails.** Six runs, four windows each, twenty-four gradings, all
of them a fail. The best run of the set is at +34.4 percent where the fail threshold is 25
percent, so it misses even the middle band by 9.4 points. Changing the window does not rescue
it, a different random seed does not, and numerical noise is thousands of times too small.

**Why this needs a decision.** `docs/R5_PHYSICS_BATCH_MANIFEST.md:214` says **"Any FAIL stops
the ladder."** Job C has not run and was scheduled to reuse this template.

### The two honest options. This is Josie's call and this document does not make it.

**Option A: accept the FAIL and stop the ladder.**
The criterion is now fully specified, the FAIL is robust to every check applied to it, and it
is 4.5x to 8.7x the project's own best estimate of the measurement floor. The likely cause is
already diagnosed: the tank drains during the run (the free surface falls 2.9 to 6.1 cm) and
the sphere is pinned, so it ends up proud of the waterline. Fixing the drainage is the work
this points to. **Cost:** job C does not run until that is done.

**Option B: amend the criterion in writing and proceed.**
Legitimate if argued in the open. **But say out loud what it costs:** the manifest states of
these bands that "These bands are set now and will not be moved." **Moving them means a band
declared unmovable was moved after seeing the result it produced.** That is exactly the pattern
this project has retracted findings over before. If this option is taken, the amendment must be
recorded in the manifest with the date, the reason, and the fact that the result was already
known, so a future reader can see it was not set in advance.

**A third thing that is not an option, it is a prerequisite either way.** Vista's staged copy
of the scene file is the version from **before** the amendment. Whoever launches job C must
re-stage it first, or job C will run under the old, unfixed specification and emit no record of
which measurement it was graded on.
