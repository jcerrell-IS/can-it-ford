# settle_frames: what it should be, what moves, and what no settle length can fix

Slot d15-settle, branch `claude/r9-settle`, 2026-08-18.
Every number here was measured live this session against the MAIN checkout
`/Users/josie/can-it-ford`. Nothing is quoted from a dispatch, a summary, or
another session's claim without independent re-derivation. Reproduction commands
are in section 11.

---

## 1. The rule, which is the point of this document

**Use the FULL RECORD for a verdict. Use a demonstrated-stationary window for any
convergence or uncertainty claim.**

The rule is asymmetric because the two questions are different. Incipient motion
is an EVENT: trimming the startup transient before a SLIDE test deletes exactly
the frames the test exists to find. A time-averaged force or a grid-convergence
claim is the opposite: a mean taken over a non-stationary window is not a settled
value no matter how many frames went into it.

Anyone who applies one rule to both cases gets a wrong answer in one of them, and
the wrong answer in the verdict direction silently contradicts the published
16 SLIDE / 1 STUCK. `analysis/probabilistic_verdict.py:107` defaults
`use_stationary_window=False` for this reason and its docstring records the
measured consequence: on the full record 21 of 24 read SLIDE, with the transient
removed only 5 of 24 do.

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
- Channel discipline, per this repo's rule on scope-sensitive counts: the
  21 of 24 and 5 of 24 figures in section 1 are on the COMMITTED magnitude
  channel that `probabilistic_verdict.py` reads today. On the corrected surge
  channel d2-persist measured 19 of 24 and 15 of 24. Both are right and answer
  different questions; d2-persist's diff is deliberately unapplied, which is why
  the committed code still yields 21. Never quote either as a bare integer.
