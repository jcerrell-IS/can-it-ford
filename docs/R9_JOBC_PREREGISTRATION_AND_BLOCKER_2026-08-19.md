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

## 4. Review status

**UNREVIEWED by a second party.** The `physics-skeptic` subagent is dead fleet-wide,
measured at 20 Agent calls across 18 transcripts with zero successes (`c621931`), and an
explicit model override does not reach it. I did not retry it. Every number above is either
read directly from a named file or regenerated from
`analysis/kramer_extract_numerical.py` and `simulation/r5_physics/kramer_benchmark.py`.
