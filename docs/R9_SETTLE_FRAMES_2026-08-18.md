# settle_frames: what it should be, what moves, and what no settle length can fix

Slot d15-settle, branch `claude/r9-settle`, 2026-08-18.

> ## THE PUBLISHED VERDICT SURVIVES. READ THIS FIRST.
>
> This document prices a methodological error at 16 of 24 verdicts. The first
> question that raises is whether **16 SLIDE / 1 STUCK** is affected.
>
> **It is not, and not by luck. It was computed under the correct rule from the
> start.** `simulation/failure_modes.py:168-182` builds `surge_drift` from the
> whole array and `_first_sustained_index` scans from index 0. There is no
> truncation, no window and no discard anywhere in that file, confirmed by
> reading the computation rather than by a keyword search returning nothing.
>
> Full record, surge channel, `>=`. That is the correct rule for a verdict, and it
> is what produced the canonical result. **Nothing in this document proposes
> changing a published verdict.** Section 1.1 traces every other published number
> to the rule it was computed under.
Every number here was measured live this session against the MAIN checkout
`/Users/josie/can-it-ford`. Nothing is quoted from a dispatch, a summary, or
another session's claim without independent re-derivation. Reproduction commands
are in section 11.

---

## 1. The rule, its price, and why the price is asymmetric

**Use the FULL RECORD for a verdict. Use a demonstrated-stationary window for any
convergence or uncertainty claim.**

**The price, measured on the same 24 runs** (`analysis/settle_audit.py
--asymmetry`):

| you get this wrong | runs that move | direction |
|---|---|---|
| stationary window used for a VERDICT | **16 of 24** on the magnitude channel, **14 of 24** on the surge channel | all 30 moves DELETE a SLIDE; creation is impossible, see below |
| full record used for an UNCERTAINTY | **24 of 24** error bars too small, median **4.32x**, worst **5.64x** | always overstates precision |

**Why the price is asymmetric, in one line: the error arrives looking like a
cleaner analysis.**

That is the whole reason nobody catches it. Applying the stationary-window rule to
a verdict does not produce an obviously wrong answer, it produces a tidier one.
All 30 moves DELETE a SLIDE and none creates one, so the mistake is directional
and it runs toward the quieter result every time.

**CORRECTED 2026-08-19, AND THE CORRECTION STRENGTHENS THE CLAIM.** An earlier
version of this document reported the "0 create one" as a measured property of
these 24 runs. **It is not a measurement. It is a theorem, and I was presenting a
tautology as data.** The stationary window is a SUFFIX `d[start:]`, so any
sustained episode inside it is a sub-run of an episode in the full record, and the
full record's longest episode is therefore always at least the suffix's. Window
SLIDE implies full-record SLIDE. No input can produce a creation. Verified by
exhaustion over every mask to length 14 and every start, 425,986 cases, 0
creations against 119,413 deletions, reproducible with
`analysis/settle_audit.py --selftest-asymmetry`.

Only the **30** is data. The **0** was never at risk.

The corrected claim is stronger than the one it replaces. The directional bias is
not a fact about this dataset that might not hold elsewhere: **it is a property of
suffix truncation itself, so it holds for any dataset and any sustained-episode
gate.** Any transient-removal rule that keeps a suffix can only ever erase a
sustained-episode verdict, never manufacture one.

I found this by applying the register's new rule, that a commit adding a check
must name the input making that check fail, to my own new code. There is no such
input for the creation counter. That is the eighth-plus instance of the pattern
this document describes in section 17, it is mine, and it was produced inside the
function written to demonstrate the pattern, one commit after I had already caught
myself doing the same thing there once.

**And the direction matters for this project's headline specifically.** The
canonical outcome is 16 SLIDE / 1 STUCK. The wrong rule deletes slides, so
misapplying it would have moved the published count toward STUCK: toward "the
vehicle mostly stayed put", which reads as the more conservative and therefore the
more defensible finding. A reviewer would have had no reason to push back on it.
The error would have been adopted, not caught.

The rule is asymmetric because the two questions are different. Incipient motion
is an EVENT: trimming the startup transient before a SLIDE test deletes exactly
the frames the test exists to find. A time-averaged force or a grid-convergence
claim is the opposite: a mean over a non-stationary window is not a settled value
no matter how many frames went into it.

The uncertainty row's factor is `sqrt(N / N_eff)` with `N` the full 91-frame
record and `N_eff` measured on the retained window, and **that pairing mixes two
windows, so it was tested rather than assumed.** Recomputing with `N_eff` from the
full record instead, which is the self-consistent pairing for a mean taken over
the whole record, gives median **4.56x** on `dmag` and **4.63x** on `dx` against
the 4.32x quoted. The quoted figure is therefore the more conservative of the two
and the conclusion is insensitive to the choice, but the pairing has to be stated:
a bare "4.32x" is a factor without its predicate, which is the failure section 16
is about. Worst case moves the other way, 5.63x/5.64x on the retained window
against 5.55x/5.54x on the full record.

The uncertainty row is unfixable by any settle length and is the subject of
section 7: 91 frames carry a median `N_eff` of about 5, so `sqrt(N / N_eff)` is
4.32x even before anything else goes wrong.

The rule is not only a sampling convention. Section 18 gives it a hydrodynamic
mechanism, verified to primary source: an accelerating body near a free surface
has a time-varying apparent mass, so the transient is a distinct physical regime
rather than noise decaying toward the answer.

`analysis/probabilistic_verdict.py:107` already defaults
`use_stationary_window=False` for this reason, and this measurement reproduces its
docstring exactly as a held-fixed control before recomputing anything: 21 of 24
SLIDE on the full record, 5 of 24 with the transient removed.

---

### 1.1 WHICH PUBLISHED NUMBER WAS COMPUTED UNDER WHICH RULE

The first question a reader has is whether **16 SLIDE / 1 STUCK** is affected.
**It is not, and not by luck: it was computed under the correct rule from the
start.** Every row below was traced to the code that produces it, live, this
session. Read directly, not recalled.

| published number | computed on | is that the right rule? |
|---|---|---|
| **16 SLIDE / 1 STUCK**, the canonical verdict | **FULL RECORD**, surge channel, `>=`. `failure_modes.py:168-182` builds `surge_drift` from the whole array and `_first_sustained_index` scans from index 0. There is no truncation, no window, no discard anywhere in that file | **YES.** Correct rule, correct channel. Unaffected |
| 21 of 24 full-record SLIDE | FULL RECORD, magnitude channel. `probabilistic_verdict.py:107` defaults `use_stationary_window=False` | YES |
| 19 of 24, the same on the surge channel | FULL RECORD, surge channel | YES |
| 5 of 24 transient-removed | STATIONARY WINDOW, deliberately | YES **as a robustness diagnostic**, which is the only thing it is ever allowed to be. Reporting it as the verdict is the error this document prices |
| 17 of 24 threshold flip | FULL RECORD | YES |
| `N_eff` 2.84 to 90, the settle audit, section 7 | STATIONARY WINDOW | YES |
| **`final_disp_mag_m` grid convergence**, CLAUDE.md item 5, the +87.8 percent and -59.2 percent across g48/g64/g96 | **NEITHER.** `sim_standing.py:501` is `d = scene.history.displacement[-1]`, a SINGLE TERMINAL FRAME. Not a verdict and not a mean over any window | **NO, and no settle length or window choice fixes it.** See below |

**The last row is the one that matters, because the rule as stated is binary and
that number is in neither class.** A single terminal-frame value has no window to
choose. It cannot be made to converge by discarding more leading frames, because
the quantity is not an average of anything: it is one sample of a still-evolving
transient. This is not a new complaint, it is the same conclusion CLAUDE.md
already records under "GRID REFINEMENT DOES NOT CONVERGE A TRANSIENT QUANTITY",
and it is why item 5 instructs readers to cite the verdict and never the
displacement magnitude.

So the honest statement of scope is three-way, not two-way:

1. **Verdicts** take the full record. Published and correct.
2. **Convergence and uncertainty claims** take a demonstrated-stationary window.
   Published and correct where they exist.
3. **Instantaneous and extremal quantities** obey neither rule and are not
   rescued by either. A grid-convergence claim built on one needs replacing with
   a time-averaged observable over a demonstrated-stationary window plus a GCI,
   which is work this document does not do and does not claim to have done.

Nothing in this document proposes changing a published verdict, and nothing in it
licenses quoting `final_disp_mag_m` as converged.

---

## 2. Results in brief

| # | Finding | Evidence |
|---|---|---|
| 1 | `settle_frames` and the audit's `recommended_discard` are DIFFERENT QUANTITIES and must never be substituted | `sim_standing.py:235-246`, section 4 |
| 2 | `settle_frames=8` is too short, but only by about 6 frames, not by 40 | section 5 |
| 3 | **No canonical verdict moves.** Zero of 41 SLIDE onset frames shift under a perfectly-settled counterfactual | section 6 |
| 4 | The SLIDE verdict is set by an impulsive kick at frame 1, which the settle length cannot reach | section 6.2 |
| 5 | A 91-frame record holds 2.84 to 11.0 independent samples. No settle length fixes that | section 7 |
| 6 | CLAUDE.md's "25 of 25 runs" is 22 distinct records presented as 25, and the true population is 48 | section 8 |
| 7 | The vertical velocity column does not integrate to the vertical displacement column | section 9 |
| 8 | The stationarity test reported STATIONARY for records it never evaluated. Fixed, and it moved no number | section 13 |
| 9 | A count without its PREDICATE fails exactly as a count without its channel does, now four instances | section 14 |
| 10 | `classify_failure_modes.py` carried six defective citations, not the one assigned | section 15 |
| 11 | **The asymmetric rule costs 16 of 24 verdicts one way and 24 of 24 error bars the other**, measured on the same runs | section 1, `--asymmetry` |
| 11a | **16 SLIDE / 1 STUCK was computed under the correct rule and is unaffected**, traced to `failure_modes.py:168-182` | section 1.1 |
| 11b | A THIRD class exists that neither rule covers: single-frame terminal values such as `final_disp_mag_m` | section 1.1 |
| 12 | The "15 of 24" collision is resolved and the error was mine: it is a threshold-flip count, not a SLIDE count | section 16 |
| 12a | The whole `n of 24` family in one table: one denominator, seven numerators, all correct, all different | section 16.1 |
| 12b | **`5 of 24` is channel-invariant member-for-member**, the only entry in the family safe to quote without a channel | section 16.1 |
| 13 | The rule has a physical mechanism, verified to primary source: added mass is not one coefficient during acceleration | section 18 |
| 14 | Three sessions independently built instruments that could not fail, in one round | section 17 |
| 15 | **400 frames costs 21 seconds.** The record-length finding was never blocked on GPU time | section 20.1 |
| 16 | **Velocity equilibrates, displacement cannot.** `N_eff` scales 3.06x on `vx` and saturates at 0.12x on `dx` | section 20.5 |
| 17 | The SLIDE verdict is unchanged at 400 frames, so the full-record rule is right for the right reason | section 20.6 |
| 18 | The same config reports 0.657 m or 0.291 m of displacement depending only on when you stop | section 20.4 |
| 19 | The canonical free-rigid path is NON-DETERMINISTIC: 7.8e-08 at frame 0 grows to 1.9e-02 by frame 26 | section 20.3 |
| 20 | **Register B4: the population was 21, not 25. No conclusion moves**, and the median shift was duplicates, not the truck | section 21 |
| 21 | **CLAUDE.md item 5's non-monotone displacement now has a MECHANISM**: the trajectory itself is non-monotonic | section 22 |

---

## 3. TWO DIFFERENT SETTLES. DO NOT MERGE THEM.

This section exists because the two will look mergeable to a later reader: both
are called settling, both were measured on 2026-08-18, and both produced a frame
count. They are unrelated.

| | THIS document | slot d3-force |
|---|---|---|
| scene | Yaris standing-flood tank | sphere heave, coupling-force rung |
| mechanism | `settle_frames` pre-roll before recording | pinned-settle quiescence gate |
| criterion | none, a fixed count | `sound_speed / vmax >= 20` |
| number | 8 frames, recommended 14 | trips at 2596 frames against a 900 cap |
| what it governs | the initial condition of the 17 gated runs | whether a buoyancy-force measurement is valid |

A frame in this document is `1/fps` of a Yaris tank run. A frame in d3-force's
result is a step of a sphere-heave scene. **8 and 2596 are not on the same
scale, not in the same scene, and not measuring the same thing.** Do not write a
sentence containing both without this table.

One finding of d3-force's DOES carry over, as a caution and not as a merge: they
showed that a quiescence gate of exactly the shape recommended in section 5.2
tripped at 2596 frames in one run and 3280 in another on the same grid and
config, a 26 percent spread, while the quantity being measured was still moving
monotonically. So `settle_gate_met=True` is not a certificate of convergence.
Section 5.2 carries that caveat into the recommendation.

---

## 4. THE CENTRAL CORRECTION: the audit does not measure the settle length

Read `renders/yaris_render_s1/sim_standing.py:235-246` directly:

```python
for _ in range(settle_frames):
    self._project_water()
    s.step(self.dt, self.substeps)

v = s.v()
v[: self.n_water, 0] += velocity     # the one-shot kick, water only
s.set_v(v)

self.com0 = s.rigid_state()["com"].copy()    # the datum is set HERE
self.time = 0.0
self.history = FloodHistory()
self.history.append(0.0, s.rigid_state(), self.com0)
```

The settle loop finishes, THEN the kick is added to the water, THEN `com0` is
captured and the first row is written. So:

> **The 91 recorded frames contain zero settle frames.**

That makes `settle_frames` and `recommended_discard` different quantities in
different places:

| | `settle_frames` | `recommended_discard` |
|---|---|---|
| when | before recording, before the datum | after the fact, on the recorded series |
| what changes | the physical initial condition | which statistics you compute |
| cost | GPU time per run | nothing |
| what a large value means | the scene needed longer to reach equilibrium | the forced response takes a while to become stationary |

**Consequence.** The inference "25 of 25 runs need more than 8 frames discarded,
therefore `settle_frames` should be about 48" is INVALID. The frames being
discarded are post-kick frames that contain the response to the kick, which is
the physics under study. That reading also collides head-on with section 1: it
would trim the transient before a verdict.

CLAUDE.md's section "THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA"
does not make that inference explicitly, but it places the `settle_frames=8`
citation and the discard statistic in adjacent sentences with no note that they
are different quantities, which invites it. Section 8 proposes the correction.

---

## 5. What `settle_frames` should be

### 5.1 The evidence that 8 is too short, from the channel that represents motion

Since the settle happens before recording, the only direct evidence in the data
is what leaks into the record. Measured on `dz`, the vertical displacement, with
the plateau defined as the median of the last 20 frames and the plateau frame as
the last frame where `|dz - plateau|` exceeds 1 mm:

- 32 of 48 runs are settling-dominated (plateau reached within 20 frames).
  Frames to plateau: min 0, **median 2, p90 5, max 6**.
  Vertical settling that leaked into the record: median 3.02 mm, max 30.38 mm.
- The remaining 16 runs never plateau within 20 frames. Their vertical motion is
  the flow response, not settling, and no settle length addresses it.

So the scene is close to settled at 8 frames and finishes within a further 6.

### 5.2 The recommendation

**Set `settle_frames = 14`** (8 already run, plus the 6-frame worst case over the
settling-dominated subset). Better, settle to a CRITERION with 14 as the minimum;
the patch in section 10 does both.

**Failure mode of the fixed number.** 14 is calibrated on the 48 records that
exist. The 6-frame worst case is `render_s2/multigeom_2026-08-08/g64_rogue`, a
different vehicle, so the bound is already being set by geometry outside the
Yaris set. A new hull, a deeper tank, or a softer floor could need more, and a
fixed count gives no signal when it is insufficient. That is the same defect
`settle_frames=8` has; 14 fixes today's numbers, not the class of error.

**Failure mode of the criterion.** A quiescence gate reports `gate_met` and a
reader takes that as converged. d3-force measured, on a different scene, that
such a gate trips with a 26 percent run-to-run spread while the measured
quantity is still drifting monotonically. So the patch RECORDS `settle_frames_run`
and `settle_gate_met` into `summary.json` rather than only acting on them, and
neither field should ever be read as a convergence certificate.

**Cost.** Six extra pre-roll frames on a 91-frame run, under 7 percent more
compute for the settle phase. This is not a reason to defer it.

### 5.3 The honest size of the effect

Going from 8 to 14 frames removes a median of 3.02 mm of vertical settling from
the record. Against the 0.05 m `slide_m` and `float_m` gates that is 6 percent.
It is a real defect and it is worth fixing, and it is not a large one.

---

## 6. What moves, and what does not

### 6.1 No canonical verdict moves

The counterfactual: a perfectly settled scene has `vx[0] = 0`, so remove the
frame-0 surge velocity as a constant drift from both channels
(`dx'(t) = dx(t) - vx[0]*t`, `vx'(t) = vx(t) - vx[0]`) and recompute the SLIDE
gate exactly as `simulation/failure_modes.py` does, on the surge component, over
the full record.

| | as recorded | perfectly settled |
|---|---|---|
| SLIDE, all 47 runs with velocity columns | 41 | 42 |
| **onset frames that move** | **0 of 41** | |
| verdict flips | 1, `renders/yaris_L2_d0p30_v1p5` | NOT one of the canonical 17 |

**Not one of the 41 SLIDE onset frames shifts by a single frame.** The single
flip is an L2 box-proxy run outside the canonical set.

This is not luck, and the margin is quantified. Define the safety factor as the
surge-velocity bias needed to flip a run's verdict, divided by that run's own
measured `|vx[0]|`:

| run | safety factor |
|---|---|
| 15 of the canonical 17 | unflippable below 2.0 m/s of bias, over 83x the worst residual seen anywhere |
| `sweepV_g64_v0p5` (the published STUCK) | **7.1x** |
| `g96_m2337` (register J15's margin-1 run) | 274x |
| `renders/yaris_L2_d0p30_v1p5` (not canonical) | **0.46x** |
| `renders/yaris_render_s1/m1100` (not canonical) | **0.57x** |

The canonical minimum is 7.1x. Two non-canonical runs are already below 1.0x,
meaning their verdicts are sensitive to a settle residual no larger than the one
they actually carry. Neither is in the 17 and neither is published.

That the two thinnest canonical margins land on `sweepV_g64_v0p5` and
`g96_m2337` is worth noting: `g96_m2337` is the run register J15 independently
flags with `margin_frames 1`, reached there by a threshold sweep rather than by
an initial-condition perturbation. Separate origins, so it counts as
corroboration.

### 6.2 Why the settle cannot reach the verdict: the forcing is impulsive

The SLIDE verdict is decided early. Recomputing `failure_modes.py`'s gate
independently gives onset frames of 2 to 5, median 3, of 91, and this matches
`data/failure_modes_by_run_classified.csv` column `onset_frame_slide` for
**17 of 17 canonical runs including the single -1**. The recomputation is
therefore validated against the published artifact, not merely self-consistent.

The reason the verdict is decided that fast is the one-shot kick:

- Frame 0 to 1 surge acceleration: median **1.54 g**, max 3.78 g.
- **43 of 47 runs reach more than half their peak surge speed within frame 1**,
  median 81.8 percent of peak.
- For scale, steady drag at Cd = 1.0 on the 1100 kg hull at 2.0 m/s over a
  1.7078 m x 0.2944 m submerged frontal area is **0.0932 g** (checked with
  Wolfram Alpha). Even at Cd = 2.0 it is 0.186 g.

The measured startup acceleration is more than an order of magnitude above
anything steady drag can deliver, which is what an impulsive start looks like:
`v[:n_water, 0] += velocity` takes the water from rest to full speed in zero
time. Added mass does not rescue the alternative reading, because added mass
makes an impulsively started body HARDER to accelerate, so it makes 1.54 g more
anomalous, not less.

Self-check on this inference, since it is the weakest link: the acceleration
figure comes from `vx`, and section 9 shows the vertical velocity column is
untrustworthy. Is the surge velocity column trustworthy? Yes. Net surge
displacement is 99.4 percent of the path implied by integrating `|vx|`, against
4.6 percent in the vertical. And the displacement channel independently confirms
the impulse: `dx[1]/dt` is 1.46 to 1.65 times the mean of `vx[0]` and `vx[1]`
across eight runs, so the displacement channel says the frame-1 motion was
FASTER than the two velocity samples imply. **The 1.54 g is a lower bound.**

Since the kick is applied identically regardless of how long the scene settled
beforehand, a longer settle cannot change it.

### 6.3 What DOES move

- Nothing in the published 16 SLIDE / 1 STUCK.
- The frame-0 initial condition itself: a median 3.02 mm of vertical settling
  leaves the record.
- Any quantity read off the MAGNITUDE channel near the start of a run. At frame
  0, before the flow has done anything, `vmag[0]` exceeds the 0.05 m/s
  `slide_speed_ms` threshold in **18 of 47 runs, by up to 6.00x**, while
  `|vx[0]|` exceeds it in **0 of 47** (max 0.478x). The magnitude channel is
  contaminated by the settle residual at frame 0; the surge channel is not.

### 6.4 A claim I tried to make and could not support

I initially read the margins as halving with grid refinement, from
`sweepV_v0p5` going 7.1x at g64 to 2.9x at g128. Testing it properly across all
**11 matched g64/g128 pairs** on disk: only 1 pair has a finite safety factor on
both sides, 9 pairs are unflippable on both, and 1 more (`m2337`) goes from
unflippable at g64 to 9.2x at g128. So 2 of 11 pairs degrade, 9 are unmeasurable,
and 0 improve.

**The direction is consistent but n is far too small to claim a rate.**
"The margin halves with refinement" is withdrawn before publication. What stands:
in every pair where the comparison is measurable, the finer grid had the smaller
margin, and that is worth re-testing when the g128 set is complete.

---

## 7. What NO settle length can fix

> **PARTLY WITHDRAWN 2026-08-19 by measurement, see section 20.5.** The
> unqualified claim "the record is too short" is now known to be **correct for
> velocity and wrong for displacement.** At 400 frames `N_eff` on `vx` reaches
> 58.92 against a linear prediction of 19.23, so velocity gains independent
> samples faster than linearly; but `dx` reaches 3.50 against 28.44, which is
> LOWER than its own value at 90 frames. Displacement is the integral of
> velocity, so if velocity settles to any non-zero mean, displacement drifts
> forever and no window of it is stationary at any length. Running longer fixes
> the velocity statistic and cannot fix the displacement one. The section below
> is retained because its measurements stand; only the unqualified framing is
> withdrawn.

**The record is too short.** Effective sample size over the retained window, 48
distinct runs, four channels, 190 run-observable pairs:

| channel | N_eff min | median | max |
|---|---|---|---|
| `dx` | 2.86 | 4.87 | 10.49 |
| `dmag` | 2.86 | 4.87 | 11.00 |
| `vx` | 2.84 | 9.27 | 47.80 |
| `vmag` | 2.84 | 13.00 | 90.00 |

132 of 190 pairs carry fewer than 10 independent samples; 76 carry fewer than 5.

An uncertainty computed from N = 91 rather than N_eff is too small by
`sqrt(91/N_eff)`: **2.88x at N_eff = 11, 4.27x at 5, 5.60x at 2.9.** Use
`effective_sample_size`, never the frame count.

Also unfixable by settling: 13 of 48 runs hit the MSER `min_keep` bound, meaning
variance was still falling at the end of the record. That is not "discard 80
frames", it is "this run is too short to establish a settled value at all".

This reaches register D9's 250-frame conclusion by a different route. D9 ran a
settle-length sweep across arms; this is a stationarity statistic on single
records. **Separate origins, so it counts as corroboration**, and only for that
reason.

---

## 8. CORRECTION TO CLAUDE.md, for slot d1-safe

Not applied here. CLAUDE.md is owned by d1-safe and is outside my write scope.

**File:** `/Users/josie/can-it-ford/CLAUDE.md`
**Section:** `## AUGUST 15 2026, THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA`
(quoted by heading, never by line number, per this repo's own standing rule)

**What survives, and it is the larger part.** The finding reproduces exactly. On
the `dmag` channel in the original scope: 25 runs, 25 need more than 8 frames
discarded, min 29, median 48, max 80, and 12 of 25 retained windows still
non-stationary at 5 percent. Every one of those figures re-derives on the first
attempt. On the corrected scope and the channel the SLIDE gate actually reads it
gets STRONGER: **48 of 48 runs need more than 8 frames discarded on `dx`, min 29,
median 54, max 80.** The direction of the finding is not in question.

**What needs correcting: the denominator, stated with its scope.**

The sentence "25 of 25 runs need MORE than 8 frames discarded" reads as 25
independent runs. It is not. The audit's discovery had two independent defects,
each silent on its own:

1. **Root.** It walked `<repo>/renders` only. That misses 12 records under
   `data/g128_canonical_2026-08-13/` and `data/g128_canonical_repeat/`, and 3
   under `render_s2/multigeom_2026-08-08/`, which is a SIBLING of `renders/`.
2. **Filename.** It matched the exact name `metrics.csv`. Eleven further records,
   all TRACKED and all 15-column, are named `<run>_metrics.csv` under
   `data/g128_2026-08-18/` and `data/g128_sweeps_2026-08-18/`. Fixing the root
   alone still gives 40 and looks complete.

Full enumeration, so the number can be audited rather than trusted:

```
  25   under renders/, what the committed script saw
+ 12   data/g128_canonical_2026-08-13/ and data/g128_canonical_repeat/
+  3   render_s2/multigeom_2026-08-08/
+ 11   data/g128_2026-08-18/ and data/g128_sweeps_2026-08-18/  (*_metrics.csv)
----
  51   records on disk
-  3   byte-identical duplicates, confirmed by md5
----
  48   DISTINCT records
```

The 3 duplicates are `renders/yaris_render_s1/{g64_m1100,g64_m1609,g64_m2337}/metrics.csv`,
each byte-identical to its `_incoming/` original. All three fall inside the
audited 25, so **the audited population was 22 distinct records presented as 25.**

**Suggested replacement sentence**, carrying its scope as this repo's rule for
scope-sensitive counts requires:

> **48 of 48 distinct runs need MORE than 8 frames discarded** on `dx`, the
> surge-displacement channel the SLIDE gate reads. Min 29, median 54, max 80 of
> 91 frames. Scope: a repo-root walk matching both `metrics.csv` and
> `*_metrics.csv`, pruning `.git/`, `.claude/`, `third_party/`, `__pycache__/`
> and `.venv/`, with 3 byte-identical duplicates dropped. The original figure,
> 25 of 25 with min 29 median 48 max 80, is correct for the `dmag` channel over
> `renders/` only with duplicates counted, and reproduces exactly in that scope.

**Two further notes for the same section.**

- The audited set includes `renders/mpm-engine-out/flood_vehicle/`, which is the
  bundled model-scale truck, not the Yaris and not full scale, and is the one
  record of the 48 with no velocity columns (8-column schema). It contributes to
  every `dmag` count in the original figure.
- The section places the `settle_frames=8` citation and the discard statistic in
  adjacent sentences. They are different quantities (section 4). A sentence
  saying so would prevent the invalid inference.

---

## 9. A defect found on the way, not mine to fix

**The vertical velocity column does not integrate to the vertical displacement
column.**

Both are written from the same `rigid_state()` dict at the same instant, in
`renders/yaris_render_s1/vehicle_live.py`, `FloodHistory.append`:
`displacement` is `state["com"] - com0` and `v` is `state["v"]`.

Measured across 47 runs, net displacement as a fraction of the path length
implied by summing `|v| * dt`:

| axis | min | median | max |
|---|---|---|---|
| surge (x) | 0.585 | **0.994** | 1.261 |
| vertical (z) | 0.0002 | **0.046** | 0.479 |

This is not oscillation cancelling out: `vz` changes sign a median of **0** times
across the 91-frame record, against a median of 10 for `vx`.

Worked single case, `sweepV_g64_v0p5`: 90 of 91 frames report a negative `vz`,
mean -0.0331 m/s, integrating to a descent of **-0.1005 m** over the 3.0 s
record. The actual net `dz` is **-0.0122 m**, reached by frame 4 and flat
thereafter. A factor of **8.2**.

A persistently negative velocity with no sign changes must integrate to a large
net displacement. It does not. INFERRED, not verified: the body's reported
velocity is the mass-weighted grid average of the material-8 free-rigid path
while its position is separately constrained by the floor collider, so the grid
reports sinking that the collider prevents. That is consistent with the coupling
architecture described in CLAUDE.md item A-1, but I have not read the solver to
confirm it and it should not be repeated as established.

**Why it matters here.** It means a large `vmag[0]` is NOT evidence that the
scene is under-settled, and the settling evidence in section 5 is drawn from
`dz` for that reason. It also gives an independent mechanism for why the
magnitude channel over-reports motion.

**Relation to d2-persist's finding.** They measured, by leave-one-out on the gap
frames, that vertical descent is scored as sliding in the magnitude channel. This
is the same conclusion from a different starting point, the initial condition and
the whole-record integral. Separate origins, so corroboration. It is NOT a
refutation of their "one-directional descent" reading: they examined a specific
subset of frames, concentrated on g48 where there is genuine floor penetration,
and my median-0-sign-changes figure is consistent with descent being
one-directional.

Recorded, not assigned. Whoever owns the solver or the metrics writer owns this.

---

## 10. The driver patch, as a diff, NOT applied

`sim_standing.py` is canonical, drives all 17 gated runs, and is held by slot
d8-naming. It is byte-unchanged by me. Confirmed clean in the main checkout at
the time of writing.

```diff
--- a/renders/yaris_render_s1/sim_standing.py
+++ b/renders/yaris_render_s1/sim_standing.py
@@ class StandingFloodScene:
     def __init__(self, vehicle, depth, velocity, vehicle_mass, n_grid=64,
                  water_density=1000.0, water_eta=1.0e-3, bulk_modulus=1.5e5,
-                 fps=30, floor_friction=0.55, settle_frames=8, device="auto",
-                 seed=0, inflow_len=1.5):
+                 fps=30, floor_friction=0.55, settle_frames=14,
+                 settle_tol_m=1.0e-3, settle_max_frames=None, device="auto",
+                 seed=0, inflow_len=1.5):
@@ (the settle loop)
-        for _ in range(settle_frames):
-            self._project_water()
-            s.step(self.dt, self.substeps)
+        # Settle to a criterion with settle_frames as the MINIMUM. Passing
+        # settle_max_frames=settle_frames reproduces the old fixed-count
+        # behaviour exactly, which keeps the 17 gated runs reproducible.
+        #
+        # settle_frames=14 is 8 (as run) + 6, the worst frames-to-plateau over
+        # the 32 settling-dominated records of 48 measured 2026-08-18. The
+        # tolerance is on the rigid body's com height between frames.
+        #
+        # settle_gate_met IS NOT A CONVERGENCE CERTIFICATE. Slot d3-force
+        # measured, on the sphere-heave scene, a gate of this shape tripping at
+        # 2596 and 3280 frames on the same config while the measured quantity
+        # was still drifting. Both fields are recorded so a reader can audit the
+        # settle rather than trust it.
+        cap = settle_max_frames if settle_max_frames is not None \
+            else 4 * settle_frames
+        z_prev = float(s.rigid_state()["com"][2])
+        self.settle_frames_run = 0
+        self.settle_gate_met = False
+        for i in range(cap):
+            self._project_water()
+            s.step(self.dt, self.substeps)
+            self.settle_frames_run = i + 1
+            z_now = float(s.rigid_state()["com"][2])
+            if i + 1 >= settle_frames and abs(z_now - z_prev) < settle_tol_m:
+                self.settle_gate_met = True
+                break
+            z_prev = z_now
@@ (the summary dict, around line 505)
     summary = {
+        "settle_frames_requested": settle_frames,
+        "settle_frames_run": scene.settle_frames_run,
+        "settle_gate_met": scene.settle_gate_met,
+        "settle_tol_m": settle_tol_m,
```

**Before applying, note the re-run cost.** Changing the initial condition
invalidates bit-for-bit reproduction of the 17 gated runs. Section 6 says no
verdict should move, but that is a prediction from the recorded data, not a
result from a re-run. Applying this is a decision with GPU attached and it is not
mine to make. The backward-compatible path is to land the code with
`settle_frames=8, settle_max_frames=8` (an exact no-op) and change the default
only when a re-run is budgeted.

---

## 11. Reproduction

Run against the MAIN checkout. Run data is gitignored and physically absent from
worktrees: a repo-root walk finds 51 records in `/Users/josie/can-it-ford` and 1
in this worktree, so a worktree run returns an almost-empty audit with no error.

```bash
# corrected scope, headline on the channel the SLIDE gate reads
/usr/bin/python3 analysis/settle_audit.py --root /Users/josie/can-it-ford --observable dx

# reproduce CLAUDE.md's original figures exactly
/usr/bin/python3 analysis/settle_audit.py --root /Users/josie/can-it-ford \
    --scope renders --keep-duplicates --observable dmag

# verdict sensitivity: counterfactual, impulse, flip thresholds
/usr/bin/python3 analysis/settle_audit.py --root /Users/josie/can-it-ford \
    --verdict-sensitivity

# the module's own self-test, including the MSER-is-not-stationarity trap
/usr/bin/python3 analysis/stationarity.py
```

---

## 13. SELF-AUDIT: can the test tell "not stationary" from "could not be evaluated"?

Asked before publishing, because a 91-frame record with N_eff near 2.9 is close
to the edge where that distinction stops being academic.

**It could not, and now it can.** `analysis/stationarity.py` had two inputs on
which it returned a confident verdict without running the test:

| input | old result | why it is wrong |
|---|---|---|
| 9-sample monotone ramp | `z = 0.000` -> **STATIONARY** | `n < 10` returned 0.0, and 0.0 is the PASS value. The most non-stationary series that exists scored a pass. |
| constant series, 50 samples | `z = -10.247` -> **NOT STATIONARY** | every pair is a tie, so A = 0 against an expected n(n-1)/4. The statistic measured the ties, not a trend. |

The first is a false PASS and is the dangerous one: the check is displayed, it
genuinely returned, and a reader cannot see it never ran. The second is a false
FAIL, so it errs conservatively, but it is still the test reporting on something
it did not measure. I predicted the constant series would fail the same way as
the ramp and it does not, which is why the probe printed the data rather than
the prediction.

**Did it fire on this data? No, and the margin is one sample.**

Over 48 runs and 4 channels, 190 run-observable pairs, the shortest retained
window is **exactly 10**, and 0 of 190 fall below it. But that is a coincidence,
not a safety property: `mser_truncation` and `transient_scan` floor the retained
window at `min_keep`, which defaults to 10, and the reverse-arrangement test
refuses below `n = 10`. **Two independent constants that happen to be equal.**
Five run-observable pairs sit exactly on the floor, all in the `g128_m1609`
family. Lower `min_keep` and the audit silently starts reporting untested
windows as stationary.

**The fix.** `reverse_arrangement()` now returns
`{"z", "evaluable", "reason", "tie_fraction", "n"}` with `z = None` when the test
cannot run, `analyze()` reports `stationary_at_5pct` as **None** rather than True
in that case, and the audit prints a third state `n/a` with its own WARNING line
instead of folding it into either column. The summary counts use
`is False` deliberately, not a truthiness check, because `not None` is True and
would bucket an unevaluated record as non-stationary. Seven self-tests cover it.
The legacy `reverse_arrangement_z` is kept, still returns the ambiguous 0.0, and
now says so in its own docstring.

**The guard moved no number.** Every figure in this document reproduces
unchanged after the fix, and no WARNING fires on the current data. It closes a
latent failure, not an active one. That is the outcome to want, and it is also
why the defect survived: nothing was visibly wrong.

**N_eff is a separate axis and is not fixed by this.** A 23-sample window with
N_eff 2.84 has enough raw samples for the test to RUN but only about three
independent ones. 26 of 190 pairs carry N_eff below 3. Evaluability and power are
different questions; section 7 is the one about power.

---

## 14. A COUNT WITHOUT ITS PREDICATE FAILS THE SAME WAY AS A COUNT WITHOUT ITS CHANNEL

This document already argues that a verdict count is meaningless without its
channel. The same structure, with a different missing word, has now produced
four instances in this project, and one of them I inflicted on myself while
writing this section.

| quantity | the numbers | the predicate that separates them |
|---|---|---|
| `9.80665` in tracked Python | **4** / **8** / **1** | files containing / occurrences / **assignments** |
| `DRIFT_THRESHOLD` = 0.05 | 22 / 23 / 24 | bare literals or also the CLI default; archive/ in or out (CLAUDE.md item 13) |
| run records for the settle audit | 51 / 48 / 25 / 22 | on disk / distinct / audited / audited-and-distinct (section 8) |
| SLIDE out of 24 | 21 / 19 | magnitude channel / surge channel (section 12) |

Every one of those numbers is correct. None of them is meaningful alone.

**The 9.80665 case is the sharpest, because the file-level answer looks like a
refutation.** A file-level grep for `9.80665` in tracked Python, excluding
`third_party/`, `.claude/worktrees/`, `archive/` and `__pycache__/`, returns FOUR
files, which appears to refute CLAUDE.md item 15's "exactly ONE site survives".
It does not. Exactly one is an ASSIGNMENT,
`analysis/viability_dashboard_scaffold.py:11`, where G is assigned and never
read. The others are prose: a stale comment, a correct historical note, and the
text of the checker rule that exists to stop this very mistake. **The claim is
true for assignments and false for occurrences.** CLAUDE.md item 15 is correct
and must not be "corrected".

**The self-inflicted instance, which is the most convincing one.** While fixing
`analysis/classify_failure_modes.py` I wrote into its docstring that four files
contain the string "across six occurrences". That was true when I measured it and
**false by the time I finished writing it**, because the replacement block I was
writing contains the string three more times. Six became eight inside a single
edit. The count was invalidated by the act of recording it.

So the fixed comment quotes **no occurrence count at all**. It states the stable
invariant, exactly one assignment, and ships the command to re-derive it:

```bash
git ls-files '*.py' | grep -v ^third_party/ | grep -v ^archive/ \
  | xargs grep -n '^[[:space:]]*[A-Za-z_][A-Za-z_0-9]*[[:space:]]*=[[:space:]]*9\.80665'
```

Returns exactly one line. **Prefer an invariant plus a re-derivation command over
a number, wherever the number can be invalidated by editing the text around it.**

---

## 15. `analysis/classify_failure_modes.py`: one assigned fix, six found

Assigned: `:30` stated `G 9.80665, failure_modes.py:14`. Verified live first, and
the defect is real but not quite as described. `failure_modes.py:14` **is** still
the `G` assignment, so the LINE was right; the VALUE was stale. That is the
harder case to spot, because following the citation lands on real, relevant code.

The fork is closed: commit `e495b56` (2026-08-12) set `G = 9.81` and regenerated
both artifacts in the same commit. And the file's own output already disagreed
with its own docstring: `classify_failure_modes.py:276` emits `FM.G`, and
`data/failure_modes_by_run.json` carries `"G_postprocessing": 9.81`. **The code
was correct and self-updating; only the prose was stale.**

Auditing the other five `failure_modes.py:NN` citations in the same file, all
verified live, all fixed:

| site | cited | live | kind |
|---|---|---|---|
| `:30` | `:14`, value 9.80665 | `:14` is `G = 9.81` | **value stale**, line right |
| `:36` | `:229-230` | `:230-232` (`reached` / `if not reached` / STUCK return) | off by one, stopped before the return |
| `:38` | `:232` "reports the last mode" | `:234` `mode = reached[-1]`; **`:232` is the STUCK return** | **points at code contradicting the claim** |
| `:45` | `:179-185` | `:181-187`, the three `_first_sustained_index` calls | drifted +2 |
| `:49`, `:275` | `:46,48` for `slide_m`, `float_m` | `:48`, `:50` | drifted +2, both copies |
| `:61` | `:127` for `np.gradient` | `:129`; `:127` is a bare `else:` | drifted +2 |

The `:38` case is the worst: `:232` is the STUCK return, the none-sustained case,
which is the opposite of "more than one mode sustains".

The `:127` case is **not confined to this file**. Slot d3-force reported that
register D6f cites `failure_modes.py:127` for `np.gradient` and that live it is
`:129`. Same stale citation, two files, which is the propagation CLAUDE.md item
13 warns about in exactly these words: the stale line numbers "had already
propagated into a downstream analysis script that cited them verbatim". **This is
that downstream script.** The register copy is d7-register's, not mine, and is
untouched.

Every citation is now anchored to a SYMBOL as well as a line
(`failure_modes.py:48` plus the symbol `slide_m`), so the next drift is detectable rather than
silently wrong. `scripts/check_claims.py` still passes 0 ERROR 0 WARN, and
`py_compile` is clean. The script was NOT executed: it rewrites
`data/failure_modes_by_run*.csv/json`, which are canonical artifacts outside my
scope.

**A reproduction, and deliberately not called corroboration.** The committed
`peak_surge_accel_g` column in `data/failure_modes_by_run_classified.csv` matches
my independently computed frame 0 to 1 surge acceleration for **all 17 canonical
runs to every digit** (1.9821565 against 1.98, 3.78212353 against 3.78). Two
consequences. First, the published "peak" surge acceleration occurs in the very
first frame transition of every canonical run, which is section 6.2's finding
sitting in a committed artifact. Second, `classify_failure_modes.py:61` already
concludes those single-frame values "are numerical, not physical", the same
reading I reached independently.

But this is **reproduction, not corroboration**, and the project's own rule is
why: both compute the same arithmetic from the same `metrics.csv`, one via
`np.gradient`, one via a forward difference. Same origin, different tool. It
confirms my arithmetic; it adds no independent evidence.

**Not touched: `scripts/check_claims.py`.** A handoff in circulation says its
Rule C6 is stale for asserting 9.80665 appears at two sites. Read live, `:151`
says "9.80665 survives at exactly ONE site, and it is DEAD CODE" and `:164` says
"Do NOT write that 9.80665 appears at two sites." **The checker is correct and
the handoff describing it is what went stale.** The file was opened read-only and
left byte-unchanged.

---

## 12. Limitations, and one review that did not happen

**THE ADVERSARIAL REVIEW IS MISSING AND THE CLAIMS HERE ARE UNREVIEWED.** The
`physics-skeptic` subagent was invoked twice and a `general-purpose` adversarial
verifier once. All three terminated on the same infrastructure error, an
unavailable model (`deepseek-ai/DeepSeek-V4-Flash:deepinfra`), before reading
anything. No review was performed and none is claimed. Section 6.4 records the
one claim I withdrew by self-attack, which is not a substitute.

Specific claims that most need an outside check:

1. The impulsive-kick inference in section 6.2. Section 6.2 already carries the
   self-check that survived, but the drag comparison rests on an assumed Cd and
   an assumed frontal area.
2. The mechanism inferred in section 9. The measurement is solid; the explanation
   is not verified against the solver.
3. The 20-frame cutoff separating settling-dominated from flow-driven runs in
   section 5.1 is a judgement call, not a derived threshold.
4. Section 13's evaluability guard was written and self-tested by me and has had
   no outside review either. It moved no number, which is reassuring and is also
   exactly what a guard that does nothing would look like; the seven self-tests
   are the evidence that it is not that.

**Other limitations.**

- Everything is post-hoc analysis of recorded data. No re-run was performed, so
  "no verdict moves" is a prediction, not a demonstration. The falsifiable test
  is one re-run at `settle_frames=14`, and the run to site it on is
  `sweepV_g64_v0p5`, the thinnest canonical margin at 7.1x and the published
  STUCK.
- The safety factors in section 6.1 model a settle residual as a constant surge
  drift. A real longer settle also changes the initial position and the water
  field, which this cannot capture.
- Slot d2-persist's surge-versus-magnitude finding is used here as context. I
  verified the underlying gate independently by reading
  `simulation/failure_modes.py` (SURGE_AXIS = 0, `slide_m` 0.05 m,
  `slide_speed_ms` 0.05 m/s, `sustain_frames` 3), but I did not re-derive their
  29.67 pp gap figure and do not restate it.
- Channel discipline, per this repo's rule on scope-sensitive counts, CORRECTED
  2026-08-19, see section 16. The earlier form of this bullet paired my
  "21 of 24 and 5 of 24" against d2-persist's "19 of 24 and 15 of 24" as though
  the two pairs measured the same things. They do not, and the 15 is not mine to
  map. Re-derived here: on the surge channel the pair is **19 of 24 and 5 of
  24**, because the transient-removed count is 5 on BOTH channels.

---

## 16. THE "15 OF 24" COLLISION, RECONCILED. THE ERROR WAS MINE.

Slot d14-corpusbib flagged, on 2026-08-19, that two committed mappings of the
same round disagreed about which published figure becomes "15 of 24", declined to
resolve it without re-deriving either, and addressed it to d15-settle and
d2-persist. That was the correct call. Resolved here, and the defect is in my
document, not in theirs.

**Three different quantities were in play, and two of them land on integers close
enough to swap unnoticed:**

| quantity | what it asks | committed channel | surge channel |
|---|---|---|---|
| full-record SLIDE | does the run slide at all | 21 of 24 | **19 of 24** |
| transient-removed SLIDE | does sliding PERSIST past startup | 5 of 24 | **5 of 24** |
| threshold flip | does the verdict change anywhere in `p >= 0.01` to `0.50` | 17 of 24 | **15 of 24** |

### 16.1 THE WHOLE "n of 24" FAMILY, IN ONE PLACE

One denominator, seven numerators, every one of them correct, every one of them
measuring something different. This is the table to reach for when two figures
appear to contradict each other:

| n of 24 | quantity | channel | rule | origin |
|---|---|---|---|---|
| **21** | SLIDE | magnitude | full record | this document, reproduces `probabilistic_verdict.py` |
| **19** | SLIDE | surge | full record | d2-persist, re-derived here |
| **5** | SLIDE, transient removed | **either** | stationary window | this document, both channels |
| **17** | threshold flip | magnitude | full record | CLAUDE.md, **not re-derived by me** |
| **15** | threshold flip | surge | full record | d2-persist, **not re-derived by me** |
| **16** | verdicts moved by the wrong rule | magnitude | both, compared | this document, `e50191b` |
| **14** | verdicts moved by the wrong rule | surge | both, compared | this document, `e50191b` |

Two of those seven I have **not** recomputed: the 17 and the 15. I established
which quantity they measure and who owns them, which is what the collision needed,
but the values remain CLAUDE.md's and d2-persist's respectively and are marked as
theirs. The other five were measured here.

**ONE ENTRY IS SAFE TO QUOTE BARE, AND ONLY ONE.** The transient-removed count is
**5 on both channels**: it is channel-invariant. Every other row in that table
changes value when the channel changes, so every other row needs its channel
stated or it is not a fact.

**And it is invariant member-for-member, not merely in total**, which is the
stronger result and was tested rather than assumed. Two sets of five with
different members summing to the same count would be a coincidence dressed up as a
property, so the sets were compared directly:

```
dmag : sweepD_g64_d0p35  sweepD_g64_d0p45  sweepV_g64_v2p0  sweepV_g64_v2p5  sweepV_g64_v3p0
dx   : sweepD_g64_d0p35  sweepD_g64_d0p45  sweepV_g64_v2p0  sweepV_g64_v2p5  sweepV_g64_v3p0
identical set? True    in both: 5    dmag only: []    dx only: []
```

The mechanism is visible in section 6.3: the transient is exactly where the two
channels disagree, because `vmag[0]` exceeds the speed gate in 18 of 47 runs while
`|vx[0]|` does so in 0 of 47. The magnitude channel is contaminated at frame 0 by
the settle residual and the surge channel is not. Remove those frames and what
remains is essentially all surge, so the two channels stop being different
questions. **The number that survives channel choice is the one computed after the
contaminating frames are gone**, which is why this is the only bare-quotable entry
in the family.

The five are the deepest and fastest cells in the sweep, `d0p35`, `d0p45`, `v2p0`,
`v2p5` and `v3p0`, which is the physically expected membership: sliding persists
past startup where the forcing is largest.

OBSERVED AND EXPLICITLY NOT CLAIMED AS CAUSAL: those five are exactly CLAUDE.md
item 7's seven P-2 failures minus the two `m1100` runs, a clean subset. Both sets
plausibly just track forcing severity, and d19-priorcode measured that P-2 is
dominated by a structural frame-0 bounding-box term rather than by dynamics, so
the correspondence is recorded as an observation for whoever owns the gates and
not as a mechanism.

That is a useful thing to know and it is also a trap, because 5 of 24 is the one
number in the family that reads as quotable and is the one that must never be
quoted as the verdict. Safe to quote bare, safe to quote without a channel, and
still only ever a robustness diagnostic.

d2-persist's 15 is the **threshold-flip** count, descending from CLAUDE.md's
"17 of 24 runs flip verdict somewhere in p >= 0.01 to 0.50". My limitations
bullet took their "19 of 24 and 15 of 24" as the surge-channel image of MY pair,
which would have made the 15 a transient-removed SLIDE count. It is not.

**The transient-removed count does not move between channels at all.** Their
document says so in terms, at `docs/R8_PERSISTENCE_GATE_2026-08-18.md` on
`claude/r8-persistence`: "The stationary-window diagnostic CLAUDE.md quotes as
'5 of 24' is 5 of 24 on both channels. Unchanged." I did not take that on their
word. `settle_audit.py --asymmetry` recomputes it from the CSVs and returns
5 of 24 on `dmag` and 5 of 24 on `dx`, alongside 21 and 19 for the full record,
so their figure reproduces from a separate implementation and my correction is
not a matter of deferring to the other slot.

**How the error was made, because that is the reusable part.** Both mappings were
written as "X of 24 becomes Y of 24" with the quantity named only in surrounding
prose. Once the sentence is compressed to its integers, `21 -> 19` and `17 -> 15`
are indistinguishable in shape, and a reader with two mappings and one pair of
slots to attribute them to will pair them wrongly about half the time. This is
the predicate-confusion class the register already records three times over:
*reach* against *cited*, *assignment* against *occurrence*, and *content
ancestry* against *merge behaviour*. The common form is that **two different
predicates were reported in a shared unit, and the unit survived into the summary
while the predicate did not.**

The remedy that generalises is not "be careful with integers". It is that a count
must be quoted with its predicate attached in the same breath, exactly as this
repo already requires a count to be quoted with its scope. "15 of 24" is not a
fact. "15 of 24 runs flip verdict somewhere in `p >= 0.01` to `0.50`, surge
channel" is one.

---

## 17. THE GENERAL RULE: A CHECK THAT CANNOT FAIL IS NOT A CHECK

Section 13 reports this as a bug in one function. It is not one bug. It is the
most common failure shape in this round, it has appeared in at least six
independent tools written by at least four different slots, and it deserves to be
stated as a rule rather than as an anecdote.

### 17.1 The rule

**A measurement must be able to distinguish three states, not two: the thing is
true, the thing is false, and the measurement did not run. Any tool that encodes
the third state using the value of the first or second is not a check, because no
input can make it fail.**

The corollary is what makes this urgent rather than pedantic:

**These failures are biased toward looking like success.** An unevaluated cell
does not usually return garbage, which would be caught. It returns the pass
value, the empty set, or zero, each of which reads as a clean result. So the
defect survives review, gets quoted, and propagates, precisely because nothing
about it looks wrong.

### 17.2 Why the bias is toward success and not toward noise

The reason is structural, not bad luck. Every one of these is a case where the
"nothing happened" path and the "everything is fine" path are represented by the
same token:

| domain | the token | reads as |
|---|---|---|
| a test statistic | `z = 0.0` | perfectly stationary, the best possible pass |
| a search | 0 hits | the string is absent |
| a set comparison | empty equals empty | the two sides agree |
| a shell pipeline | a command that does not exist | no output, so no findings |
| an API call | 200 with a null body | reachable and healthy |
| narration in code | a printed sentence with no test behind it | a verified claim |

In each row the failure mode and the success mode are the same bytes. No amount
of care at the call site recovers the distinction once it has been collapsed,
which is why the remedy has to be structural.

### 17.3 The instances, with their provenance marked

First-hand, measured by me this session:

1. `stationarity.reverse_arrangement` returned `z = 0.0` for `n < 10`, and 0.0 is
   the pass value, so a 9-sample monotone ramp, the most non-stationary series
   that exists, scored STATIONARY. The same function returned `z = -10.247`
   NOT STATIONARY for a 50-sample constant series, because every pair is a tie
   and the statistic measured ties rather than trend. A false pass and a false
   fail from one function. Section 13 has the full working.
2. **In the function written to demonstrate this very rule, today.**
   `settle_audit.asymmetry()` printed "a verdict is only ever DELETED by the
   wrong rule, never created" as narration, while the code counted only whether a
   verdict moved and never which way. No dataset could have contradicted that
   sentence. Measuring it gave 30 deletions and 0 creations, so the claim was
   true. It was still unearned, and being right is not the same as having
   checked. Fixed in the same commit; both directions are now counted and
   printed.

**Three sessions built an instrument that could not fail, in one round, and
found it independently.** That co-occurrence is the transferable result, more than
any single fix: this slot's stationarity test reporting verdicts on records it
never ran, d18-platform's CI/health check answering from an error path, and
d12-kramerdata's fail-loud guards whose first catch was its own author's
non-regenerating number. Three different domains, three different authors, one
shape. A defect that independent sessions reproduce without contact is a property
of how the tools are written, not a lapse by any of them.

Reported by other slots on the shared board, read there and **not independently
re-derived by me**, listed because the pattern is the point:

3. d18-platform: W&B's GraphQL endpoint returns HTTP 200 to an unauthenticated
   call, so any health check written against the status code passes with an
   absent credential. Caught by running an unauthenticated control.
4. d12-kramerdata: built fail-loud guards, and the first thing they caught was a
   number of its own author's that was not regenerating. The instrument worked
   because it was built to fail loudly; the lesson is that the author is inside
   the blast radius, not outside it.
5. d18-platform: `grep -c` already prints 0 and exits 1 on no match, so an
   `|| echo 0` fallback produced the two-line string `"0\n0"`, and every "NO" in
   a table came from a comparison that errored rather than from a test.
6. d16-landing: an add/add merge control returned exit 1 on both arms because the
   branch did not exist, so a broken harness printed as a clean result.
7. d14-corpusbib: an author-search route skipped surnames of three characters or
   fewer and reported the skip as "0 matches" rather than as "did not run".

### 17.4 The remedy, which is a schema and not more care

Every instance above was produced by someone who knew about this failure mode.
Two of them were produced by people actively writing about it at the time,
including me. So the remedy cannot be attention.

- **Give the third state its own value.** Return `None`, not `0.0`. Return
  `NOT-EVALUABLE(reason)`, not an empty list. `stationarity.analyze` now returns
  `stationary_at_5pct = None` with a separate `stationarity_evaluable` flag and a
  reason string.
- **Test with `is False`, never with truthiness.** `not None` is `True`, so a
  bare negation buckets every unevaluated record as a failure. This one line is
  where the fix is usually lost.
- **Carry the denominator.** "0 outside the domain" is unfalsifiable; "0 of
  4,353,030 particle-frames outside the domain" cannot be produced by a check
  that never ran.
- **Run the control that should fail.** The unauthenticated call, the arm with no
  branch, the deliberately committed trap. A detector never observed to fire has
  not been tested.
- **Treat uniformity across arms that should differ as a harness fault** until
  proven otherwise. Every instance above first showed up as suspiciously clean
  agreement.

### 17.5 What it cost, and what it did not

Worth stating plainly in both directions. The guard in `stationarity.py` **moved
no number**: every figure in this document reproduces unchanged, and it did not
fire on this data, 0 of 190 run-observable pairs. That is the outcome to want, and
it is also exactly why the defect survived so long, because nothing looked wrong.

But the margin is one sample. The shortest retained window across 48 runs and four
channels is exactly 10, with five pairs sitting on it, and the only thing holding
that floor is `mser_truncation`/`transient_scan` defaulting `min_keep` to the same
10 that the test refuses to run below. Two independent constants that happen to be
equal today, not a guarantee. A single change to either default puts real records
into the branch that used to return a confident STATIONARY.

---

## 18. THE ASYMMETRIC RULE HAS A PHYSICAL MECHANISM, NOT ONLY A STATISTICAL ONE

Sections 1 and 7 argue the rule from sampling: an event is not a mean, and a
91-frame record does not hold 91 independent samples. That argument is sound but
it is about estimators, and it would be just as true of a series with no physics
in it at all. There is a stronger reason, and it is hydrodynamic.

**Added mass is not constant during acceleration near a free surface.** A body
accelerating through water entrains a growing volume of fluid, so the apparent
inertial force changes with time rather than sitting at one coefficient. This is
why a window chosen to stabilise a mean can be exactly the wrong window for an
incipient-motion event: the transient is not measurement noise decaying toward the
answer, it is a distinct physical regime with its own force balance, and the
verdict is decided inside it.

**Primary source, resolved and verified this session** (Crossref, verdict
`matched`, high confidence, checked title AND authors rather than only that the
DOI resolves):

> Grift, E. J., Vijayaragavan, N. B., Tummers, M. J. and Westerweel, J. (2019).
> "Drag force on an accelerating submerged plate." *Journal of Fluid Mechanics*
> **866**, 369-398. `10.1017/jfm.2019.102`. Open access, CC BY 4.0.

Two things in that paper's own abstract carry the argument, quoted from the
resolved record and not from a summary of it:

1. It separates the record into **three phases**: "(i) the acceleration phase
   during which the plate drag is enhanced, (ii) the transition phase during which
   the plate drag decreases to a constant steady value upon which (iii) the steady
   phase is reached." That is the same three-part structure this document imposes
   on a run record, arrived at experimentally and independently.
2. "the drag force during acceleration of the plate increases over time and **is
   not captured by a single added mass coefficient for prolonged accelerations**."

The second sentence is the mechanism. If one coefficient cannot represent the
accelerating phase, then no scalar summary of that phase, including a mean taken
over a window chosen to stabilise it, represents the force that acts during it.
Discarding the transient does not remove a nuisance; it removes a regime.

That paper also measured a free-surface proximity effect in the steady phase:
submerging the plate top by one fifth of the plate height raised steady drag by
45 percent against the plate top at the surface. Recorded because this project's
hull sits in shallow water at 2 grid cells of depth, not because anything here
depends on it.

### 18.1 What this does and does not license

**Does:** it upgrades section 1 from a statistical convention to a claim with a
physical reason, and the reason is falsifiable. It also predicts the sign already
measured in section 6.2, that the frame 0 to 1 acceleration is more than an order
of magnitude above the steady-drag scale, since the acceleration phase is the
enhanced-drag phase.

**Does not:** Grift et al. is a rigid plate towed on a straight path in a tank at
`Re` of 4e4 to 8e4. It is not a vehicle, not MPM, and not this geometry. It
supplies a mechanism, not a validation target, and it must not be cited as
agreement with any number in this repo.

### 18.2 Citations relayed to me that I have NOT resolved

Marked rather than used. Received as shorthand keys from a deep-search report via
the coordinator, and a report saying a paper reports something is not that paper
reporting it:

- **[Kra21b]**, described as a public benchmark at about 0.3 percent experimental
  uncertainty. Not resolved to a DOI or a title by me. If it is the Kramer
  reference family already in this project, note that CLAUDE.md and register line
  228 carry Kramer 2016 `10.1016/J.IJDRR.2016.04.003`, which is a different year
  and would need checking rather than assuming.
- **[Wau69]**, accelerating-plate drag with free-surface effects. Unresolved.
- **[Chu77]**, near-surface added mass and damping. Unresolved. This is the key
  that would most directly support section 18, so it is the one worth resolving
  first, and I did not.

`analysis/research_index.py --method added-mass` returns 6 corpus records, all
marked UNCITED, which is how [Gri19] above was located and then verified
externally. None of the three unresolved keys was matched there.

### 18.3 Two bounds on what a settle change could ever show

Both relayed from the same deep-search pass, both consistent with what this
document measured independently, and both stated as bounds rather than as support:

- **A large force change does not imply a verdict change.** Simulated drag rising
  40 to 50 percent under accelerating flow is attributed to Azhar 2026, which this
  project already carries at `10.1111/jfr3.70181` for the same finding, and the
  search itself notes the result is "not a discrete verdict comparison". That is
  the same gap between a measured quantity and the setting it is cited against
  that section 4 documents for `settle_frames`, and it is why section 6 reports a
  verdict count rather than a force delta.
- **Two things this analysis must not lean on.** No retrieved study shows reduced
  sound speed or outlet-boundary choice flipping a vehicle motion verdict, and the
  ten-times-flow-speed rule for artificial sound speed has no primary derivation.
  Nothing in this document rests on either, checked: the settle recommendation in
  section 5 is derived from vertical-plateau frames, and the verdict result in
  section 6 from the surge channel and the impulse. Neither reads a sound speed or
  an outlet condition. Recorded so that a future session does not add a dependency
  on them believing they were settled here.

---

## 19. PRE-REGISTRATION: THE LONG-RECORD TEST

**Written and committed BEFORE the job was submitted.** This section exists
because I have argued all round that a threshold chosen after seeing the data is
not a threshold, and this is the first time that rule binds on me.

### 19.1 Why this run has to exist

Every claim in this document about record length is an inference from records that
do not exist. The canonical runs are 91 rows. **Nobody has ever run a longer one.**
Section 7 says the record is too short; register D9 reaches a 250-frame conclusion
by a different route; both are inferences from the same absent evidence. Two
inferences agreeing is not a measurement, and I have spent this whole document
saying so about other people's numbers.

### 19.2 Design

Three arms, one variable. Only `--frames` changes. Canonical Yaris g64, mass
1100 kg, depth 0.30 m, velocity 1.5 m/s, eta 1.0e-3, floor friction 0.55.
`scripts/r9_settle_longrecord.sbatch`.

| arm | frames | purpose |
|---|---|---|
| `probe_f10` | 10 | measure per-frame cost instead of guessing it |
| `control_f90` | 90 | the canonical length, held fixed |
| `long_f400` | 400 | past D9's 250, so saturation is visible if it exists |

**The control arm is not a formality and it is the reason the job has three arms
rather than one.** Its only job is to distinguish "the environment still
reproduces the canonical result" from "could not evaluate". This round has logged
eight instrument failures where exactly that distinction was collapsed, one of
them mine, so a long run without a same-job control would be a ninth.

Driver is Vista `$WORK/render_s2/sim_standing.py`, sha256 `5215c38b`, **the driver
that produced the 17 gated runs**, chosen over the Mac canonical `4696c3b2` and
the Aug 8 staged `7236e474` because the control arm's entire value is
comparability with those records. Stated as a decision with a cost: this does not
test the current repo driver.

### 19.3 WHAT WOULD CHANGE MY RECOMMENDATION, fixed in advance

**Gate 0, the control. If `control_f90` does not reproduce, I report that and
nothing else.** Reproduction means the SLIDE verdict matches canonical
`g64_m1100`, which is SLIDE, and `final_disp_mag_m` lands within 20 percent of
0.658537 m. The 20 percent is deliberately loose and is not a precision claim: it
is sized to catch gross environment drift only, because item 5 already records a
3.4 percent disagreement between two measures of this very quantity on this very
run, and this configuration's true run-to-run spread is unknown to me. **If the
control fails I will not report the 400-frame numbers as a result**, because a
difference would then be unattributable between length and environment.

**Q1. Does the retained window become stationary at an affordable length?**
Currently 12 of 25 retained windows are non-stationary at 5 percent, and a short
record cannot be told from a genuinely non-stationary one.
- Prediction: at 400 frames the majority of channels become stationary.
- **If >= 75 percent of channels are stationary at 400**: length was the binding
  constraint, D9 is supported, and I recommend 250 to 400 frames for any
  convergence claim.
- **If the record is still non-stationary at 400**: the non-stationarity is not a
  short-record artifact. My recommendation changes materially, from "run longer"
  to **"displacement is not a stationary observable at any affordable length, and
  convergence claims must move to a different observable entirely."** That is a
  stronger and more negative result than D9's and it would need saying plainly.

**Q2. Does `N_eff` scale with frame count, or saturate?** This is the sharpest of
the three because the two outcomes are quantitatively separated in advance. The
independent-sample argument predicts `N_eff` proportional to `N`, so 400 frames
should give roughly `5 x (400 / 91) = 22.0`.
- **Ratio to prediction >= 0.7, i.e. `N_eff` >= 15.4**: scaling holds, length is
  the binding constraint, D9 stands, section 7's "the record is too short" is
  correct as written and running longer buys real independent samples.
- **Ratio <= 0.3, i.e. `N_eff` <= 6.6**: saturation. The correlation time is
  growing with the record, which means drift rather than mere correlation.
  **Running longer would NOT buy independent samples**, D9's 250-frame conclusion
  needs revisiting, and section 7 must be restated from "too short" to "does not
  equilibrate".
- **Between 0.3 and 0.7**: ambiguous. I will report it as ambiguous and will not
  force a verdict out of it.

**Q3. Does the SLIDE verdict survive a 4.4x longer record?**
- Prediction: **yes, SLIDE, with onset at the same frame as the control.** Section
  6.2 measured that 43 of 47 runs reach half their peak surge speed by frame 1, so
  onset is an early-record event and should be untouched by what happens after
  frame 90.
- **If onset is unchanged**: the full-record rule is right for the right reason,
  not right by luck, and the asymmetric-rule pricing in section 1 stands.
- **If the verdict flips at 400 frames**: a 91-frame record was truncating the
  physics, and the published verdicts would rest on an arbitrary record length.
  That is the outcome that would most damage this document, and it is why the
  prediction is written down before the run rather than after.

### 19.4 What this run cannot answer

It is ONE configuration and one seed. It cannot establish a run-to-run
distribution, it cannot separate grid effects from length effects, and a single
non-stationary result at 400 frames would not prove non-stationarity at 2000. It
also does not change `settle_frames`, which runs before recording starts and is
not what this measures, per section 4.

---

## 20. THE LONG-RECORD TEST, RESULT. Vista job 922622.

Graded against section 19's thresholds, which were committed in `ee6a0bc`
**before** the job was submitted. Nothing below was chosen after seeing the data.

### 20.1 THE COST FINDING, WHICH INVALIDATES THE PREMISE OF THE WHOLE SECTION 7

| arm | frames | wall | s/frame | RC |
|---|---|---|---|---|
| `probe_f10` | 10 | 11 s | 1.100 | **1** |
| `control_f90` | 90 | 9 s | 0.100 | 0 |
| `long_f400` | 400 | **21 s** | 0.052 | 0 |

**Four hundred frames cost twenty-one seconds.** The "record is too short"
finding, 25 of 25 runs needing more than 8 frames discarded, `N_eff` between 2.84
and 11.0, 12 of 25 retained windows non-stationary, has been carried all round as
if it were blocked on GPU time. **It was never blocked on anything.** Marginal
cost from the 90 and 400 arms is `(21 - 9) / (400 - 90) = 0.0387 s/frame` with
about 5.5 s of startup.

The per-frame rate falls 21x from the probe to the long run. That is startup
amortisation, so **short probe runs are the expensive ones per frame** and a long
record is nearly free once the process is up. Do not size an arm from a probe's
rate, which is what the 1.100 figure would have led me to do.

### 20.2 GATE 0: PASSES, so the 400-frame numbers may be reported

| criterion, fixed in advance | required | measured | verdict |
|---|---|---|---|
| SLIDE verdict matches canonical `g64_m1100` | SLIDE | **SLIDE** | pass |
| `final_disp_mag_m` within 20 percent of 0.658537 m | 0.527 to 0.790 | **0.656813 m**, off by 0.26 percent | pass |

Onset frame is 3 against the committed classification's 2. One frame, not part of
Gate 0 as written, and explained by 20.3.

### 20.3 THE RUNS ARE NOT ONE TRAJECTORY, AND THAT IS ITSELF A FINDING

Only `--frames` changed, so I expected frames 0 to 90 to be identical between the
two arms. **They are not.** Max absolute difference over the first 91 rows and six
channels is `1.94e-02` at `vz[26]`.

Traced rather than assumed. The divergence is present at frame 0 at `7.8e-08` in
`vz`, which is float32 epsilon, and grows:

```
frame    0    1    2     5      20      26
|dvz| 7.8e-08 3.8e-07 3.0e-08 1.2e-03 7.7e-03 1.9e-02
```

Five orders of magnitude in 26 frames. **This is chaotic amplification of
floating-point non-determinism, not a `--frames` dependency**, and it means the
canonical free-rigid path is non-deterministic at fixed configuration. d17-moving
measured the SDF-collider path as effectively deterministic at 4.7e-6 relative
spread; that result does not transfer to this path.

Consequence, stated because it limits everything after it: **the two arms are two
draws, not one trajectory truncated twice.** Any cross-arm comparison conflates
record length with run-to-run variation. The findings in 20.5 survive this only
because they are measured WITHIN the 400-frame run.

### 20.4 THE TERMINAL-FRAME QUANTITY, DEMONSTRATED RATHER THAN ARGUED

Section 1.1 argued that `final_disp_mag_m` obeys neither rule because it is a
single terminal frame. The long record demonstrates it:

- `long_f400` `dmag` **peaks at 0.667127 m at row 64**, then ends at
  **0.290845 m**, which is **43.6 percent of its own peak**.
- `control_f90` ends at 0.656813 m, near that peak, because 90 frames happens to
  stop close to row 64.

**The same configuration reports 0.657 m or 0.291 m depending only on when you
stop looking.** The vehicle moves downstream and then comes back; net displacement
is not monotonic. CLAUDE.md item 5's non-monotone `final_disp_mag_m` across
g48/g64/g96, +87.8 percent then -59.2 percent, now has a mechanism: those runs are
sampling a non-monotonic trajectory at an arbitrary time. Item 5's standing
instruction to cite the verdict and never the displacement magnitude is correct
and this is the direct evidence for it.

### 20.5 Q1 AND Q2: BOTH SPLIT, AND THEY SPLIT THE SAME WAY

This is the result. It is a within-run comparison, so 20.3 does not touch it.

| arm | channel | n | discard | window | `N_eff` | stationary at 5 pct |
|---|---|---|---|---|---|---|
| control_f90 | `dx` | 91 | 47 | 33 | 6.40 | yes |
| control_f90 | `dmag` | 91 | 47 | 33 | 6.42 | yes |
| control_f90 | `vx` | 91 | 52 | 32 | 4.33 | NO |
| control_f90 | `vmag` | 91 | 49 | 42 | 4.12 | NO |
| **long_f400** | `dx` | 401 | **389** | **11** | **3.50** | **NO** |
| **long_f400** | `dmag` | 401 | **388** | **11** | **5.59** | **NO** |
| **long_f400** | `vx` | 401 | 195 | 216 | **58.92** | **yes** |
| **long_f400** | `vmag` | 401 | 165 | 236 | **201.80** | **yes** |

**Q1, pre-registered threshold 75 percent of channels stationary at 400: FAILS,
at 2 of 4, 50 percent.** By the letter of section 19 my recommendation changes
from "run longer" to "displacement is not a stationary observable at any
affordable length". The data says something more useful than the binary allowed
for, and the extra structure is what makes it worth having.

**Q2, pre-registered `N_eff` prediction 22.0 from linear scaling:**

| channel | `N_eff` at 90 | at 400 | linear prediction | ratio | pre-registered band |
|---|---|---|---|---|---|
| `dx` | 6.40 | 3.50 | 28.44 | **0.12** | **SATURATION** |
| `dmag` | 6.42 | 5.59 | 28.51 | **0.20** | **SATURATION** |
| `vx` | 4.33 | 58.92 | 19.23 | **3.06** | **SCALING** |
| `vmag` | 4.12 | 201.80 | 18.33 | **11.01** | **SCALING** |

**The split is by channel family and it is enormous, a factor of 25 between `dx`
and `vx`.** Run-to-run variation cannot plausibly produce that, and it is a
within-run measurement in any case.

**VELOCITY EQUILIBRATES. DISPLACEMENT DOES NOT, AND CANNOT.** That is not a
solver defect, it is arithmetic: displacement is the time integral of velocity, so
if velocity settles to any non-zero mean, displacement drifts forever and no window
of it is ever stationary. `dx`'s retained window at 400 frames is 11 rows out of
401, and its `N_eff` at 400 is **lower** than at 90. Running longer makes the
displacement statistic worse, not better.

So the honest answers are channel-dependent, and both halves matter:

- **For any velocity-based convergence or uncertainty claim**, longer records buy
  independent samples faster than linearly: `N_eff` goes 4.33 to 58.92 on `vx`
  for a 4.4x longer record. Register D9's 250-frame conclusion is supported and
  exceeded, and this reaches it by a third route.
- **For any displacement-based claim**, longer records buy nothing at all.
  Section 7's "the record is too short" is **correct for velocity and wrong for
  displacement**, and I am withdrawing the unqualified form.

Section 19 pre-committed that a non-stationary result at 400 would mean
"convergence claims must move to a different observable entirely". The data has
now named that observable: **velocity, not displacement.**

### 20.6 Q3: THE VERDICT SURVIVES

`long_f400` reads **SLIDE with onset at frame 3**, identical to `control_f90`, on
a record 4.4x longer. The prediction in section 19 was SLIDE with unchanged onset,
on the section 6.2 grounds that 43 of 47 runs reach half their peak surge speed by
frame 1, and that is what happened.

**The full-record rule is right for the right reason, not right by luck.** The
verdict is set in the first handful of frames and 310 further frames do not touch
it, including 310 frames during which net displacement falls to 43.6 percent of
its peak. A quantity that moves that much while the verdict does not is the
cleanest available statement of why section 1.1 separates them.

### 20.7 `probe_f10` EXITED 1 AND STILL WROTE PLAUSIBLE OUTPUT

`metrics.csv` holds 12 lines, 11 rows for 10 frames, exactly what a healthy run
would produce. A reader checking that the file exists, or counting its rows, grades
a crashed arm as a good one. This round's own instrument-failure pattern, in my
directory, in a job I wrote to test something else.

Cause, read from the traceback and not guessed:

```
File ".../render_s2/sim_standing.py", line 333, in main
  veh_check_45=checkpoints["45"], ...
KeyError: '45'
```

The driver records a checkpoint only at `f in (0, 45, a.frames - 1)`, then indexes
`checkpoints["45"]` unguarded. **Any run with `frames < 46` crashes after writing
`metrics.csv`.** The simulation itself completed; only `rollout.npz` and
`summary.json` are missing, which is why the wreckage looks healthy.

**I wrote the hazard into my own job.** `scripts/r9_settle_longrecord.sbatch`
states "f=45 exists at every length used here and the npz write cannot KeyError".
I checked the 400 arm and the 90 arm and did not check the 10-frame arm I had
myself added. The Mac canonical driver already carries the fix,
`f_check = min(45, a.frames - 1)`, with a comment describing this exact bug; the
Vista `5215c38b` driver that produced the 17 gated runs does not.

Gated in `scripts/r9_canonical_400.sbatch`: every arm's RC is recorded next to its
row count, **both** are printed because neither alone is sufficient, and the job
exits non-zero if any arm failed.

### 20.8 PRICING THE FULL CANONICAL SET AT 400 FRAMES

Measured anchor: one g64 400-frame run is 21 s, of which about 5.5 s is startup
and 15.5 s is compute. Grid mix of the 17, read from
`data/all_runs_inventory.csv`: **11 at g64, 3 at g48, 3 at g96.**

Cost is taken as `grid^4`, since particle count goes as `grid^3` and the substep
count goes as `grid` through the acoustic CFL. That gives g48 at 0.32 and g96 at
5.06 g64-equivalents.

| quantity | value |
|---|---|
| g64-equivalents per full pass | `11 + 3(0.32) + 3(5.06)` = **27.1** |
| compute per pass | 27.1 x 15.5 s = **420 s** |
| startup, 17 runs | 17 x 5.5 s = **94 s** |
| **one pass of all 17 at 400 frames** | **about 8.6 minutes** |
| three draws per cell, 51 runs | **about 26 minutes** |

A `grid^3` model instead of `grid^4` gives 7.4 minutes per pass, so the estimate
is not sensitive to that choice.

**What it takes: one gh node, one job, `-t 00:40:00`, and no code changes.**
`--frames` is an existing CLI argument. Submitted as job **923186**,
`scripts/r9_canonical_400.sbatch`, writing to a new tree
`$WORK/r9_canonical_400`. **No canonical artifact is read, written or moved, and
these runs are not part of the 17 gated set.**

Three draws rather than one because 20.3 measured that this path is
non-deterministic. A single draw per cell would not be a result.

**On the walltime**: job 922622 requested 2:00:00 and ran 00:01:06, a 109x
over-request that queued behind 139 jobs, because Slurm backfills short requests
into gaps a long one cannot fit. 923186 asks 00:40:00 against a 26-minute
estimate, sized from the measured 0.0387 s/frame rather than from a
comfortable-looking round number.

---

## 21. REGISTER ROW B4: THE POPULATION WAS WRONG. NO CONCLUSION MOVES.

The cross-session reader filed B4: the settle audit is reported as "25 of 25 runs"
and is actually 22 distinct records, one of which is a model-scale truck rather
than a full-scale vehicle. Both halves are correct. Re-derived here over the
corrected population, and **the headline claims all survive unchanged**, which is
worth stating as plainly as the defect.

### 21.1 The exclusion criterion is SCHEMA, not scale

`renders/mpm-engine-out/flood_vehicle` is excluded, but not primarily because it
is model-scale. **Its `metrics.csv` carries 8 columns**, `t, dx, dy, dz, dmag,
yaw_deg, pitch_deg, roll_deg`, **against the 15-column FloodHistory schema this
audit is documented to read.** It has no `vx`, no `vmag`, no velocity channel at
all, so it cannot be evaluated on the surge channel the SLIDE gate reads. That is
checkable from the file; the model-scale claim comes from a session memory
recording a 1.447 m, 28.7 kg bundled truck splat and I did **not** re-verify those
dimensions here.

Membership is now decided by schema in `settle_audit.py`, because a schema test is
falsifiable and a directory-name test is not. `--keep-offschema` reproduces the old
population exactly.

### 21.2 All four populations, so no count is quoted without its scope

| deduplicated | schema gate | n | discard min / median / max | `N_eff` | non-stationary | need > 8 |
|---|---|---|---|---|---|---|
| no | no | **25** | 29 / **48** / 80 | 2.87 to 11.00 | 12 of 25 | **25 of 25** |
| no | yes | 24 | 29 / 48 / 80 | 2.87 to 11.00 | 11 of 24 | 24 of 24 |
| yes | no | 22 | 29 / 62 / 80 | 2.87 to 11.00 | 12 of 22 | 22 of 22 |
| yes | **yes** | **21** | 29 / **61** / 80 | 2.87 to 11.00 | 11 of 21 | **21 of 21** |

**Row 1 is CLAUDE.md's published figure and it reproduces exactly**: 25 of 25,
min 29, median 48, max 80, `N_eff` 2.9 to 11.0. The published numbers were right
for the population they were computed on. **Row 4 is the corrected population: 21
distinct, full-scale, on-schema records.**

### 21.3 What moves, and what does not

**Nothing that was concluded from it moves.**

- **"Every record needs more than 8 frames discarded" survives at 100 percent**,
  21 of 21. This is the claim the whole section rests on and it is untouched.
- **The `N_eff` range is identical to two decimal places**, 2.87 to 11.00, in all
  four populations.
- **Min and max discard are identical**, 29 and 80, in all four.
- Non-stationary goes 12 of 25 to 11 of 21, which is 48 percent to 52 percent.
  Same conclusion, that roughly half the retained windows are still not
  stationary.

**One number moves: the median discard, 48 to 61.** And the cause is not the
truck. It is **deduplication**: the median is 48 with duplicates and 61 or 62
without, in both gated and ungated populations. The three byte-identical
duplicates are low-discard `g64` records counted as independent, and they pulled
the median down 13 frames. **The off-schema record changes the non-stationary
count by one and nothing else at all.**

I had expected the truck to be load-bearing, on the grounds that its displayed
discard 80 and `N_eff` 2.9 looked like the published extremes. **Tested, and that
was wrong.** Max discard 80 is a tie across eight records, seven of them
full-scale, and the true minimum `N_eff` of 2.87 belongs to
`yaris_L2_d0p30_v1p5`, not to the truck. The hypothesis was refuted by computing
it rather than asserting it, which is the only reason it is not in this document
as a finding.

**New denominator, with its scope: 21 distinct on-schema records under
`renders/`, byte-identical duplicates dropped, off-schema records excluded.** The
wider corrected scope of section 8 is a different population again, 48 distinct
across the whole repo, and must not be mixed with this one.

### 21.4 A note on how the wrong count survived

The published figure was not sloppy arithmetic. It was `--keep-duplicates` plus no
schema gate, both defensible defaults at the time, and the number reproduces
perfectly under them. What was missing was the scope travelling with the count,
which is the same defect as the `n of 24` family in section 16 and the
`DRIFT_THRESHOLD` totals in CLAUDE.md item 13. **Three instances now, in three
different quantities, in one document.** The remedy is not more care at the call
site; it is that a count and its population must be one object.

---

## 22. CLAUDE.md ITEM 5 NOW HAS A MECHANISM

Recorded here explicitly and in the commit message, because item 5 has been
carried as unexplained since August and it is now explained.

**Item 5 records that `final_disp_mag_m` is non-monotone across the grid study:
1100 kg moves +87.8 percent from g48 to g64 then -59.2 percent from g64 to g96;
1609 kg moves +22.3 then -50.3.** It instructs readers to cite the binary verdict
and never the displacement magnitude. That instruction is correct. Until now the
reason was a statistical one, that an instantaneous value is not expected to
converge under refinement, which is Syamlal, Celik and Benyahia 2017 and is
already in CLAUDE.md.

**The long record supplies the physical mechanism.** In `long_f400`, section 20.4,
`dmag` **peaks at 0.667127 m at row 64 and ends at 0.290845 m, 43.6 percent of its
own peak.** The vehicle moves downstream and then comes back: net displacement is
**not monotonic in time**, so `final_disp_mag_m` is one sample of an oscillating
trajectory taken at whatever time the record happens to stop.

That is the mechanism. **The g48, g64 and g96 runs are not disagreeing about a
converged displacement. They are sampling a non-monotonic trajectory at an
arbitrary phase**, and the sign of the difference between any two of them is set
by where in that oscillation frame 90 falls for each. A ±88 percent swing between
grids needs no numerical explanation once the same configuration is known to swing
by a factor of 2.3 within a single run at fixed grid.

The three consequences worth carrying:

1. **Item 5's instruction is strengthened, not weakened.** Cite the verdict. The
   verdict is unchanged at 400 frames, section 20.6, while the displacement fell
   to 43.6 percent of peak over the same frames.
2. **The non-monotonicity is not evidence of a solver defect** and should stop
   being cited as if it might be. It is the expected reading of a terminal-frame
   sample of an oscillating quantity.
3. **A grid-convergence claim is still possible, but not on this observable.**
   It needs a time-averaged quantity over a demonstrated-stationary window with a
   GCI, and section 20.5 establishes that the window exists for velocity and does
   not exist for displacement at any length.

