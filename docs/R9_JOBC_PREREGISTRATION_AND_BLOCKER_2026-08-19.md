# Job C pre-registration, and why I did not submit it

**Slot** d12-kramerdata. **Branch** `claude/r9-kramer-extract`. **Date** 2026-08-19.
**Engine:** warpmpm (the 1-DOF SDF-collider sphere scene). No Genesis. **No job was
submitted.** No SUs were spent.

**Scope note.** My declared write scope for this round was two files,
`analysis/kramer_extract_numerical.py` and `docs/R9_KRAMER_FULL_EXTRACT_2026-08-18.md`.
This third file exists because the coordinator directed a batch submission, which needs a
pre-registration. I have written **no** simulation driver, **no** job script, and have
touched nothing under `simulation/`.

---

## 0. The short version

I was asked to submit Job C, the Kramer free heave decay. **I did not, and the reason is
not caution: it is that three separate things in the specification are wrong or unmet, and
one of them is a decision the coordinator themselves recorded today.** All four findings
below are read directly from files, not recalled.

**What I did instead, and it is the more valuable half:** the blocker that made Job C
ungradeable against the published data, `BLOCKER-B1`, **is resolved**, and no one had
noticed, because the artifact that resolves it is the archive this slot spent the round
extracting. The comparison Job C was supposed to defer is available today.

---

## 1. Why I did not submit

### 1a. The ladder is STOPPED by an explicit decision recorded today

`claude/r9-accessor`'s copy of `docs/R5_PHYSICS_BATCH_MANIFEST.md` carries this, added
2026-08-19:

> **LADDER STATUS: STOPPED, 2026-08-19**
> **Job B FAILED criterion 3 and the FAIL was accepted. The ladder is stopped under the
> rule stated immediately below. Job C must NOT proceed on an assumption that job B
> passed.** Decision taken by the round-9 coordinator, recorded by slot `d11-accessor`.

The gating rule it refers to is the manifest's own, fixed in advance: **"Any FAIL stops the
ladder"**, and Job C's heading reads **"Fire only after B passes"** with **"If B fails
criterion 1 or 3, C is not worth its wall clock."** Job B failed criterion 3, at +34.4 to
+64.2 percent across 24 of 24 gradings, with no transient-exclusion window out of 184
avoiding a FAIL.

**This dispatch does not mention that decision.** I am not assuming it was reversed, because
reversing a pre-registered gate after seeing the failure is the precise move that produced
the withdrawn placement, and this dispatch warns me about that move in its own final
paragraph. **If the coordinator intends to override, that is a legitimate call, but it needs
to be made explicitly and recorded, not inherited by silence.**

### 1b. The prerequisite d11-accessor named is confirmed unmet, and I checked it live

The same block states two things that must happen before Job C runs. The second is
operational and I tested it:

> Vista's `$WORK/d4_scene/sphere_heave.py` must be re-staged: it is the version from
> **before** this criterion was amended, so job C launched from it would run under the old
> specification and emit no record of which quantity it was graded on.

Measured, three ways:

| copy | md5 |
|---|---|
| Vista `$WORK/d4_scene/sphere_heave.py`, dated Aug 17 22:41 | `1c8994991e0029a89a047d9f3624ca78` |
| my branch `claude/r9-kramer-extract` | `1c8994991e0029a89a047d9f3624ca78` (**identical**) |
| `claude/r9-accessor`, amended | `fbc23b5e9e888bb28dd7453c05a5d8c4` (**differs**) |

`06c7786` changed `sphere_heave.py` by 63 lines. **So Vista is running the pre-amendment
driver, and so is my own branch.** A Job C submitted from either records no statement of
which quantity it was graded on. That is not a theoretical risk; it is the exact failure
`d11-accessor` spent a whole document diagnosing.

The first prerequisite, the near-field surface test of
`docs/R9_ACCESSOR_DEFECT_2026-08-18.md` section 27, I have **no evidence has run**, and I
have not searched exhaustively for it, so treat that as unknown rather than as unmet.

### 1c. The Job C command block still specifies a domain the same file retracts

This one is independent of the gate, and it would have silently produced a wrong run.

- The submit block (`:512` on `claude/r9-accessor`) reads **`--lim 1.2`**.
- The cost line (`:552`) reads **"3.7 node-hours at the corrected `lim = 2.2` domain, up
  from 1.0 at the retracted `lim = 1.2`"**.
- Job C's own reflection criterion (`:525`) reads **"reflections return at 1.649 s = 2.12
  natural periods at `lim = 1.2`"**, while `:202` of the same file states `lim = 1.2` buys
  only **1.06** clean natural periods, **"not the 2.12 first claimed on a group-velocity
  convention the benchmark explicitly rejects"**.

**The cost line was updated to the corrected domain and the command block was not.** Running
the block as written executes the retracted domain and grades it against a reflection window
computed on a convention the benchmark rejects. **Whoever owns the manifest should reconcile
`:512` and `:525` against `:202` and `:552` before any Job C runs.** I have not edited it:
it is outside my scope and on another slot's branch.

---

## 2. BLOCKER-B1 IS RESOLVED, and the manifest does not know it

This is the finding that changes what Job C is worth.

The manifest says, twice:

> **BLOCKER-B1 still applies and it changes how this is graded.** The raw benchmark time
> series is MDPI Supplementary Materials at `/s1`, 403 from two independent hosts.
> **Without it, the published-comparison criterion cannot be evaluated at all.**

**That artifact is on this machine and this slot has spent the round reducing it.**
`energies-14-00269-s001`, sha256 `04c4d78d...9c7623f`, at
`/Users/josie/can-it-ford-refs/2026-08-16/`, CC BY 4.0 (verified from the article PDF, not
from a project file: see `R9_KRAMER_FULL_EXTRACT_2026-08-18.md` header). It holds **58
series**: 31 numerical, 27 experimental, including the three `*_CI95_Normalized.txt` bands
and all twelve `*_Raw` repetitions.

**So Job C's deferred criterion set is evaluable today, for the first time.** The manifest's
split into "available now, self-consistency only" and "requires `/s1`, deferred" is stale.

### 2a. I tested the deferred criterion's own input, and it holds

The manifest corrected Job C's displacement criterion on 2026-08-16, before the data existed
to check it, on the strength of Kramer **Table 4 p.17** giving measured drop heights of
**{29.16, 89.18, 150.06} mm** against nominal {30, 90, 150}. **That correction can now be
verified against the shipped series rather than against the table alone:**

| drop | Table 4, mm | archive mean, mm | vs Table 4 | vs nominal |
|---|---|---|---|---|
| 01D | 29.16 | 29.1236 | **-0.125 pct** | -2.921 pct |
| 03D | 89.18 | 89.0858 | **-0.106 pct** | -1.016 pct |
| 05D | 150.06 | 150.1288 | **+0.046 pct** | +0.086 pct |

**Table 4 reproduces from the supplementary to within 0.13 percent at every drop.** The
2026-08-16 correction was right, and it is now supported by the data and not only by the
table.

**It is also understated, and this is new.** The manifest justified the correction by the
nominal-versus-measured gap at 01D, "0.84 mm, which is 9.6x the 0.090 mm tolerance". But the
**repetition-to-repetition spread** at 01D is larger still: the four measured releases are
**29.177, 28.361, 27.720, 31.236 mm**, a spread of **3.5166 mm = 12.075 percent of the mean,
which is 39.07x the 0.090 mm tolerance.** Grading absolute displacement at 01D is swamped by
repetition scatter before the nominal offset is even considered. This is precisely why the
paper normalises each repetition by its own measured drop height.

---

## 3. PRE-REGISTRATION, fixed before any run exists

Committed before submission, per the dispatch. Nothing below may be changed after seeing a
result; if it is changed, the change and its reason must be recorded here and the original
left visible.

### 3.1 Statistic

**The first damped period, `first_damped_period_s`.** Chosen because it is the quantity
`kramer_benchmark.intercode()` already grades all eleven codes on, against the experimental
**mean of the same quantity over four repetitions**. Any other choice would not be
commensurable with the envelope. Cycle 1 only: a multi-cycle average is unavailable anyway
inside the reflection window, and would flatter the experiment.

**Grouping key: AUTHOR.** Fixed now because the envelope is grouping-key dependent by this
slot's own measurement, 5 of 6 groups within 0.82 percent by author against 4 of 6 by
institution. The author key is the defensible one for an independence claim, because the
paper's own affiliation list gives "Morten Bech Kramer 1,2" across both Aalborg University
and Floating Power Plant, so the institution column separates one person from himself.

### 3.2 Primary drop height: 01D. Stated with its reason, which is that it is the hardest.

| drop | codes | envelope, pct | envelope width, points |
|---|---|---|---|
| **01D (primary)** | 10 | **-3.31 to +0.58** | **3.89** |
| 03D | 10 | -5.98 to +3.62 | 9.60 |
| 05D | 11 | -12.26 to +12.83 | 25.08 |

**01D is designated primary because its envelope is the narrowest, so it is the test hardest
to pass by accident.** 05D would have been the easy choice: it has all eleven codes and an
envelope 6.4x wider. Choosing the widest target after the fact is how the withdrawn
placement happened, and choosing it in advance would be the same error with better timing.

Costs of the choice, stated now rather than discovered later: 01D has the largest
repetition scatter in release amplitude (12.07 percent, section 2a), the smallest absolute
signal, and the lowest Mach (0.019, so it is the least compressibility-stressed and
therefore the least informative about that particular failure mode).

**All three drops will be run and all three reported regardless of outcome.** 01D is the
headline; the other two are not optional and may not be dropped if they are unflattering.

### 3.3 THE FALSIFIER, in absolute seconds

The dispatch asked for the input that makes the check fail, stated before the run. Here it
is as a single number per drop. `T_exp` is the experimental four-repetition mean.

| drop | T_exp, s | PASS band (inside the eleven-code envelope), s | band width, s |
|---|---|---|---|
| **01D** | 0.786901 | **[0.760850, 0.791480]** | 0.030629 |
| 03D | 0.809270 | [0.760850, 0.838539] | 0.077688 |
| 05D | 0.867135 | [0.760850, 0.978361] | 0.217511 |

> **CORRECTION MADE BEFORE ANY RUN, recorded rather than silently applied.** The first
> draft of this table hand-computed the 03D and 05D lower bounds as 0.760876 and
> 0.760825. **Both were wrong.** All three lower bounds are 0.760850 s, because LPF0
> sets the minimum at every drop and returns a bit-identical period (section 3.4). My
> hand arithmetic contradicted my own finding two subsections later, and the
> regenerates-check caught it. Third time this pattern has bitten me today, and the
> reason the check exists.

**FAIL is defined now: a measured first damped period at 01D outside [0.760850, 0.791480] s
places this solver outside the envelope of all ten codes that ship 01D.** That is the
falsifier. It is one number and one interval.

**The gravity bias must travel with every period quoted.** The engine hardcodes g = 9.81 and
the benchmark used 9.82, an irreducible **+0.051 percent** on period, which is +0.000401 s
at 01D, **1.3 percent of the 01D band width**. Not dominant, not negligible, and it is a
one-sided bias rather than a scatter.

### 3.4 A second, stronger falsifier that costs nothing extra

Both ends of the envelope are set by the same author's two potential-flow configurations at
**every** drop height, and the lower end has a signature worth testing against:

| drop | envelope MIN | code | envelope MAX | code |
|---|---|---|---|---|
| 01D | 0.760850 s | LPF0 | 0.791480 s | LPF4 |
| 03D | **0.760850 s** | LPF0 | 0.838539 s | LPF4 |
| 05D | **0.760850 s** | LPF0 | 0.978361 s | LPF4 |

**LPF0 returns 0.760850 s at all three drop heights, bit-identical.** That is the signature
of a linear solution whose period is amplitude-independent by construction, while the
physical period rises 0.786901 to 0.867135 s across the same drops. It also explains
mechanically why the envelope widens 6.4x from 01D to 05D: the potential-flow family
brackets the experiment ever more loosely as nonlinearity grows, rather than the RANS codes
disagreeing more.

**So, pre-registered: does this solver's first damped period RISE with drop height?** The
experiment does, and the paper's Figure 13 says so. A flat period across the three drops
would place this solver in LPF0's failure mode, an effectively linear response, and that is
a specific diagnosable verdict rather than a bare number mismatch. **This direction test is
graded independently of the band test, and either may fail without the other.**

### 3.5 What this run cannot establish, fixed now so it is not claimed later

- **It is not a validation of the benchmark.** Section 12 of
  `R9_KRAMER_FULL_EXTRACT_2026-08-18.md` establishes that the 0.3 percent figure is the
  paper's own abstract, reproducing at 0.2915 percent from its own supplementary. The
  benchmark is precise **by its own account** and no independent assessment of that is in
  hand.
- **Kramer supplies no tolerance for a static force.** Per `d11-accessor`'s amendment, and
  consistent with this slot's section 12.2, the 0.3 percent is **of drop height** and is
  normalisation dependent, 5.1x to 5.2x larger against the local signal. It must not be
  imported as an acceptance band for anything, and specifically not for criterion 3.
- **Landing inside the envelope is not a pass mark for the physics.** The 01D envelope is
  3.89 points wide and its ends are set by two configurations of one author's potential-flow
  code. Sitting inside a spread that wide is a weak claim, and the honest statement of a
  success is "inside the published inter-code envelope", not "validated".
- **This is not a re-litigation of the withdrawn Job B placement**, which stays withdrawn
  and is not reopened here.

---

---

## 5. Do the ladder's pre-registered criteria still mean what they meant when written?

Added 2026-08-20 at the coordinator's request, after reading `3f4c1ec` and `d826c8a` on
`claude/r9-jobb-route`. **Short answer: NO, for three reasons, and one thing that DOES
survive unchanged is the ladder-stop itself.**

### 5.1 What survives: the stop is still correct at the resolution Job B was specified at

Job B is specified `--n-grid 64 --lim 1.2`. d21's dx arms are 18.75, 12.50 and 9.375 mm,
and `1.2 / 64 = 18.75 mm`, so **Job B is the coarsest arm of that sweep**. At matched
submergence with the trend regressed out, d21 measures the excess there as **+46.17 percent
+/- 8.04**. Criterion 3's FAIL band is "beyond 25 percent". **FAIL stands, the ladder-stop
stands, and nothing in section 1 of this document is weakened.**

### 5.2 What broke: criterion 3 grades a quantity now known to be dominated by dx

d21's grid prong, same engine, PPC 8, matched submergence:

| dx | excess at 130 mm | +/- |
|---|---|---|
| 18.75 mm (**g64, = Job B**) | +46.17 pct | 8.04 |
| 12.50 mm | +28.11 pct | 6.14 |
| 9.375 mm | +21.50 pct | 10.55 |

Linear in dx, `excess = 2.669*dx_mm - 4.217`, extrapolating to **-4.2 percent at dx -> 0**.

Criterion 3's bands are anchored, in the manifest's own words, to "this project's box-SDF
buoyancy agreement of 7.3 to 7.7 percent, rounded outward", and are explicitly "a PROJECT
CHOICE, not a literature tolerance". **That anchor carries no resolution.** Grading a
quantity whose value is mostly a function of dx against a band imported from a different
path at an unstated resolution is a category error, and it is the same one this slot
documented for the 0.3 percent figure in section 12 of
`R9_KRAMER_FULL_EXTRACT_2026-08-18.md`: **a ratio is meaningless against a band derived
under a different normalisation or operating point.** Two slots found the same defect shape
in two different criteria on the same night.

**So a FAIL at g64 is a statement about g64's discretisation error, not about the solver's
physics.** It was written to be the latter.

### 5.3 What is still missing: criterion 3 names no OPERATING POINT

`d11-accessor` amended criterion 3 to name **which quantity** and **over what window**,
because a comment was silently doing that job. **It still does not name a submergence.**

That is now the load-bearing omission, and d21 measured why: the arms sat at 67.9 to 125.4
mm submergence because a coarser lattice drains more, and reading them as though they were
the same state **inverted a trend**. Their own words: the `k` rise to 0.829 at PPC 64 "is an
ARTIFACT of the unmatched operating point and does not survive". They withdrew their own
published non-convergence claim over it.

**The same run can therefore be graded to different values depending on a parameter the
criterion does not fix.** That is exactly the defect d11 repaired one level up, still open
one level down. **Criterion 3 needs a third specifier: quantity, window, and submergence.**

### 5.4 The verdict is resolution-dependent, and at the finest arm it is not a FAIL

At dx 9.375 mm the excess is **+21.50 percent**, which sits inside criterion 3's **10 to 25
percent REPORTABLE PARTIAL** band, not the FAIL band. The error bar spans 10.95 to 32.05,
so it straddles PARTIAL and FAIL.

**"Job B FAILED" is a property of g64, not of the solver.** Anyone restating the ladder-stop
should say at which resolution.

**Stated limits, because this is the weakest link in the argument above.** The grid prong is
**1.86 sigma end-to-end, below this project's 3 sigma bar**, the finest point rests on 35
frames, and d21 calls it "suggestive and not established". Vista job 923291 (g192, dx 6.25
mm) is pre-registered to settle it: the O(dx) line predicts +12.5 percent, and a value near
21.5 percent or above restores a non-zero asymptote. **Until that lands, 5.2 and 5.4 are
provisional and 5.3 is not**, because 5.3 is a defect in the criterion's wording rather than
a claim about the data.

There is also an unresolved tension d21 flagged and did not close: Wal07's own analytic
reference (Vshivkov) predicts **h^2** while the measured fit is linear in **h**. Not mine.

### 5.5 WHAT THIS DOES TO MY OWN PRE-REGISTRATION, which is the part I owe

**Section 3 grades the first damped PERIOD, and the period is not immune to this.** The
natural period is set by the restoring stiffness, which is set by the waterplane at the
equilibrium submergence. If a coarser lattice drains more, the equilibrium submergence
differs, and the period differs **for a discretisation reason rather than a physical one**.
**A period compared at unmatched equilibrium submergence is the same error d21 just
withdrew, and my falsifier as written does not exclude it.**

**AMENDMENT, made before any run exists and therefore inside the rules:**

1. **Every period reported must travel with the achieved equilibrium submergence**, in mm,
   and with the analytic half-draft it should have reached. The benchmark sphere is
   ballasted to float at its equator, so the target is unambiguous.
2. **A period is not gradeable against the band in section 3.3 unless its equilibrium
   submergence is within a stated tolerance of half draft.** I fix that tolerance now, before
   any data: **+/- 5 percent of the sphere radius**. Outside it, the run is reported as
   UNGRADEABLE ON OPERATING POINT, which is a real outcome and not a failure to measure.
3. **The direction test of section 3.4 survives this and becomes the more robust of the
   two**, because it asks whether the period RISES across three drops run at one resolution,
   where the equilibrium submergence is common to all three and largely cancels.

**This makes my own pre-registration harder to pass, and I am recording it before the run
rather than after seeing one.** That is the whole point of the instrument.

---

---

## 6. Do the criteria survive the shared-numerator finding?

Added 2026-08-20 after `ea1d385`. **Criterion 3 does not survive and needs rewriting before
anything is graded against it. Criteria 1, 2 and 5 survive. Criterion 4 survives but must
stop being cited as reassurance. The ladder-stop is NOT reopened, and Job C's value goes UP.**

### 6.1 The claim, verified rather than relayed

Read directly, not taken from the relay:

- `sphere_heave.py:782` computes `w = self.solver.sdf_wrench(self.collider, self.tick)` and
  `fz = w["force"][2]`. **One reading.**
- `:818` returns `fz / fb_meas`; `:819` returns `fz / (RHO_W_BENCHMARK * G_ENGINE *
  2/3 pi R^3)`. **Same `fz`. The two accessors differ only in the divisor.**
- Solver side, vendored copy: the gate is `if sd <= param.band`, and the accumulation is
  `impulse = m * (v_free - v_new)` followed by `wp.atomic_add(param.force, 0, impulse)`.

**One citation correction:** that impulse is at `kernels/mpm_solver_warp.py:2733`, not
:2732. Line 2732 is `m = state.grid_m[gx, gy, gz]`, the mass fetch. This project has closed
an identical off-by-one before (the rigid-mass citation `:851-853` corrected to `:856`), so
it is worth getting right rather than passing on.

**The claim is confirmed. The two accessors are one measurement under two normalisations.**

### 6.2 Why criterion 3 does not survive

**Criterion 3 has never graded a force. It grades a normalisation choice applied to a single
force reading.** That is now provable from source rather than arguable.

`d11-accessor`'s amendment was necessary and correct: two quantities were live under one
criterion and a source comment, not the manifest, was deciding which. But **naming one of
two denominators over a shared numerator resolves an ambiguity without adding any
information about the force.** The amended criterion is well defined and still cannot do the
job it was written for.

Concretely, a FAIL at +46.17 percent is consistent with all three of:

1. the coupling force really is 46 percent high;
2. the denominator is wrong (the analytic buoyancy at the measured surface is not the right
   comparison for what `sdf_wrench` accumulates);
3. `sdf_wrench` itself is biased, so neither ratio means what it appears to.

**With one numerator, no window and no choice of denominator separates these three.** Job B
ran 24 gradings and 184 transient-exclusion windows and could not, because every one of them
divided the same number.

**This is the same defect shape this slot documented for the 0.3 percent figure** in section
12 of `R9_KRAMER_FULL_EXTRACT_2026-08-18.md`: one measured quantity expressed under two
normalisations that differ by a large factor, where the number is meaningless unless the
normalisation is named, and a band derived under one cannot grade a value computed under the
other. Three instances now, in three different criteria, found by three slots in two days.

**The rewrite is specifiable, which it was not before `ea1d385`.** Criterion 3 should grade
**agreement between two independent routes**, not one route against a closed form. d21's
`control_volume_force()` reads only fluid state, `cauchy()` and `vol()`, and never touches
the body, the SDF or the band. Its own framing is the right criterion: if it returns
`rho*g*V_cap` while `sdf_wrench` returns 1.35x, the defect is in the accessor; if it returns
1.35x too, the fluid really is pushing that hard. **Job 923343 was RUNNING at 00:57 on
2026-08-20, 5:08 elapsed, so that number does not exist yet.**

### 6.3 The other criteria

| criterion | survives? | why |
|---|---|---|
| 1, collider accepted | **yes** | structural, on `add_sdf_collider`; does not read `fz` |
| 2, SDF matches closed form | **yes** | grades the builder via `sdf_radius_rms_err_m`; does not read `fz` |
| 3, steady vertical reaction | **NO** | section 6.2 |
| 4, lateral force vanishes | **yes, but** | see below |
| 5, stationarity | **yes** | a statement about the series, and already "expected, not disqualifying" |

**Criterion 4 needs a warning label.** It grades `|F_lateral| / |Fz|`, and **both components
come from the same wrench vector**. A uniform multiplicative bias on the accessor cancels
exactly in that ratio. So criterion 4 is **structurally incapable of detecting the error
criterion 3 is disputing**, and a PASS on 4 is not evidence that the force readout is sound.
It tests isotropy, which is worth testing, and nothing more. Do not cite it as reassurance.

### 6.4 The ladder-stop is NOT reopened

Three reasons, and none of them is procedural conservatism:

1. **The discrepancy is real as a discrepancy.** Something disagrees with the closed form by
   +46 percent at g64. Whether the fault is the accessor or the physics, it is unexplained,
   and running the harder path on top of an unexplained 46 percent is exactly what the gate
   exists to prevent.
2. **This finding makes it LESS understood, not more.** Two readings that had been treated as
   two views of the force turn out to be one. Evidence that seemed to bracket the problem
   does not. That argues for holding.
3. **It does not touch the two independent prerequisites** in section 1: Vista's stale
   driver, and the `lim` contradiction between the command block and the cost line.

**Additional and new: Job C must not be GRADED until 923343 reports**, separately from the
gate. Job C's criteria are written against accessors that may be about to be shown biased.
Grading a decay run against `sdf_wrench` and then learning the accessor carries a
multiplicative bias would mean regrading everything.

### 6.5 BUT JOB C'S VALUE GOES UP, and this is the actionable part

The shared numerator propagates into the free-decay trajectory, because the 1-DOF
integration is `az = fz/mass - G` with the same `fz`. **That makes the period an independent
probe of the same numerator, and it separates two hypotheses that no static measurement can.**

In the small-amplitude limit `T = 2*pi*sqrt(m/k)`:

- a **multiplicative** bias `k` on the coupling force scales the restoring stiffness, so
  `T -> T/sqrt(k)`;
- an **additive** offset shifts the equilibrium submergence and leaves `T` unchanged.

**So the free-decay period discriminates a multiplicative accessor bias from an additive
one, and the equilibrium submergence of section 5.5 catches the additive case.** Together
they cover both.

Quantified against my own 01D band `[0.760850, 0.791480]` s, using d21's matched-submergence
excesses:

| arm | static excess | predicted 01D period | inside my band? |
|---|---|---|---|
| g64 (Job B's own arm) | +46.17 pct | **0.650865 s** | **NO** |
| g96 | +28.11 pct | 0.695230 s | **NO** |
| g128 | +21.50 pct | 0.713891 s | **NO** |

**The 01D band tolerates only `+6.965` percent multiplicative force bias before leaving it**
(`k = (0.786901/0.760850)^2`), against a static disagreement of +46.17 percent.

**PRE-REGISTERED PREDICTION, before any Job C run exists:**

- **If the static excess is a multiplicative force error that acts on the dynamics, Job C at
  01D FAILS at every resolution measured, landing near 0.651 to 0.714 s against a floor of
  0.760850 s.**
- **If Job C at 01D lands inside the band, the static excess CANNOT be a multiplicative
  force error acting on the dynamics**, which localises the defect to the accessor's static
  path or to the held configuration, and does so without any new machinery.

**Both outcomes are informative, and that was not true of Job C before `ea1d385`.** It is
the strongest argument yet for eventually running it, and it is not an argument for running
it now.

**Assumptions, stated because the mapping is where this could be wrong.** `T = 2*pi*sqrt(m/k)`
is the small-amplitude linear limit. 01D is the drop the paper itself calls "a small drop
height, which can be considered a linear case", which is a second reason 01D was the right
primary choice; the mapping should NOT be applied at 05D, where the waterplane area varies
materially over the cycle. The excesses are d21's matched-submergence estimates and the dx
prong is **1.86 sigma, below this project's 3 sigma bar**, so the three predicted periods are
provisional in magnitude although not in sign.

---

## 4. Review status

**UNREVIEWED by a second party.** The `physics-skeptic` subagent is dead fleet-wide,
measured at 20 Agent calls across 18 transcripts with zero successes (`c621931`), and an
explicit model override does not reach it. I did not retry it. Every number above is either
read directly from a named file or regenerated from
`analysis/kramer_extract_numerical.py` and `simulation/r5_physics/kramer_benchmark.py`.
