# D4 job A: the brake-state flip is MEASURED, and the repeats are not deterministic

2026-08-17. Branch `claude/r5-physics`. **Job 917797**, `SUMMARY runs=23 failed=0`,
`ALLDONE`, stderr **0 bytes**, elapsed 00:10:11 on one `gh-dev` node (`c642-032`).
This is the first GPU physics ever produced on this branch.

Claim tags: **[read]** live from a primary source, **[derived]** computed here,
**[unreviewed]** not yet adversarially checked.

Every number below was measured at **250 frames**, settle **8** (constructor-only, there
is no `--settle-frames` flag), **trimesh 4.12.2**, runtime engine git **627367e**, driver
`sim_standing.py` sha256 `4696c3b2...10d9`.

---

## 1. Attribution, because three jobs shared one output directory

| id | outcome |
|---|---|
| 917786 | dead in 3 s, all 23 runs `ModuleNotFoundError: trimesh`, **wrote no run directories** |
| 917796 | dead, all 23 runs `cannot import name 'solidify_watertight'`, cancelled 16:44:27, **wrote no run directories** |
| **917797** | **COMPLETED, 23/23 succeeded** |

All three targeted a fixed `d4_jobA`, which was a genuine silent-overwrite hazard. It did
not fire, and that is checkable rather than asserted **[read]**: 917796 ended at
**16:44:27** and every byte in the directory was written from **16:45** onward; `jobA.err`
is 0 bytes so none of 917796's ImportError text survives; and both dead jobs produced zero
run directories because every run exited 1 before writing. **Everything here is 917797.**
`OUT` is now keyed by `${SLURM_JOB_ID}` so the hazard cannot recur.

## 2. A1: the control holds and the inferred flip is now measured

Graded with `simulation/failure_modes.py`, **not** by displacement magnitude. SLIDE
requires `(surge_drift >= 0.05 m) AND (surge_speed >= 0.05 m/s)` sustained over
`sustain_frames = 3`. Classified at `mass_kg = 1100.0`, `ssf = 1.42` **[read]**.

| mu | classifier verdict | onset | `final_disp_mag_m` | wall |
|---|---|---|---|---|
| **0.55** | **STUCK (stable)**, no criterion tripped | n/a | 0.028966 | 43 s |
| 0.30 | SLIDE, +128.23% past criterion | frame 8 (t=0.2667 s) | 0.072001 | 16 s |
| **0.0250** | **SLIDE**, +1329.06% past criterion | frame 6 (t=0.2000 s) | 0.137869 | 15 s |

- **The control holds.** mu = 0.55 reproduces **STUCK**, so the job is not void.
- **The flip is MEASURED, not inferred.** mu = 0.0250 gives SLIDE. The branch has carried
  this as INFERRED throughout; it can now be stated as measured, with the caveats below.
- **mu = 0.30 confirms nothing and is reported as such.** It was logged INDETERMINATE
  **in advance** because the bracket (0.369, 0.739] straddles this run's 0.5 m/s. It came
  out SLIDE. That does not promote it, and the whole reason for fixing criteria
  beforehand is that this outcome cannot be narrated into agreement afterwards.

**Displacement is not the verdict.** mu = 0.55's max surge drift is **0.0569 m**, which
*exceeds* the 0.05 m `slide_m` threshold, yet the verdict is STUCK because the
sustained-speed conjunction never fired **[derived]**. Anyone grading on
`final_disp_mag_m` would have called it the other way.

**CORRECTED after review: the earlier wording "mu = 0.55 proves it" was wrong and is
withdrawn.** This re-observes a property already in the published record. The canonical
`sweepV_g64_v0p5` row at `data/failure_modes_by_run_classified.csv:14` already carries
`mode=STUCK, ratio_slide=1.135578, triggered_slide=False, max_surge_drift_m=0.05677891`.
A repeat of a run cannot prove a property of the run it repeats; **the control
re-confirms it**, which is worth having and is not the same claim.

### 2.1 How strong the control actually is, and it is stronger than I said

The review reproduced the classifier and then went further, cross-checking against the
**published canonical timeseries**, which is on local disk at
`renders/yaris_render_s1/_incoming/sweepV_g64_v0p5/metrics.csv` **[read]**:

```
peak_surge_accel_g    job 0.68204033  pub 0.68203942   +0.0001%
peak_surge_force_n    job 7359.89715  pub 7359.88730   +0.0001%
max_surge_drift_m(0..90) job 0.05590725 pub 0.05677891  -1.5352%
```

It reaches **zero of the three required sustain frames, not two**. The two SLIDE
conditions are **temporally disjoint**: `|vx| >= 0.05` holds only on frames 1 to 8, while
`|dx| >= 0.05` holds only from frame 36. On the 130 drift-qualifying frames the maximum
surge speed is 0.014961 m/s, **0.299x the threshold**. To flip the verdict, `slide_m`
would have to fall 37.2% or `slide_speed_ms` 81.1%. It is invariant to `sustain_frames`
over {1..20}, to dropping the first {0..100} frames, and to frame count
(n=91 STUCK, n=251 STUCK).

### 2.2 Three things that weaken how the flip was stated, though not the verdict

1. **The onset frames are not physical onsets.** Settle runs in the constructor
   (`sim_standing.py:235-241`), so CSV frame 0 is already post-settle and post-kick. The
   mu = 0.0250 onset moves to frame 0 as soon as 6+ frames are dropped. "SLIDE at frame 6"
   is where a growing drift crosses a fixed number during the impulsive start.
2. **53% of the SLIDE evidence is the vehicle moving UPSTREAM.** `failure_modes.py:170`
   takes `np.abs` of the surge velocity, so reverse motion scores as SLIDE. For
   mu = 0.0250, 102 of the 191 conjunction frames have `vx < 0`, mean -0.1617 m/s.
3. **mu = 0.0250 has no vehicle-physical basis.** It is 22x below the canonical 0.55 and
   about 31x below Smith 2019's wet-or-dry 0.78. **"The flip is measured" must never be
   read as "the flip occurs at a realistic friction."**

### 2.3 BLOCKING: every 250-frame magnitude sits inside the reflection window

Predicted closed-tank gravity-wave round trip, from the scene's own geometry
**[derived]**: vehicle to downstream wall 3.1798 m, `c = sqrt(g*0.29443) = 1.6995 m/s`,
round trip 3.7421 s = **112.3 frames**. Observed drift peaks: **frames 112, 125, 126**.

**So every `max_surge_drift_m` reported from these 250-frame runs is measured at or after
the first wall reflection arrives.** Either truncate to <= 91 frames, matching the
canonical, or state the contamination beside every 250-frame magnitude. The 250-frame
endpoint is separately not comparable to the published one: `dmag` at frame 250 is
0.02896647 against the published `final_disp_mag_m` 0.05781253, **-49.90%**. Only the
matched-frame comparison (-1.5%) is legitimate.

## 3. A2: ten repeats, and they are not deterministic

Fixed configuration, no seed flag exists, N = 10 per case **[derived]**:

| case | max drift mean | range | spread | final drift spread | divergence onset |
|---|---|---|---|---|---|
| `g96_m2337` | 0.086249 m | [0.085223, 0.087426] | **2.203e-03 m** | 3.079e-03 m | **frame 1** |
| `sweepV_g64_v0p5` | 0.058910 m | [0.057807, 0.059860] | **2.052e-03 m** | 2.793e-03 m | **frame 1** |

Reported as the manifest requires: N and range, never a single draw, and **frequency, not
pass/fail**. Against `slide_m = 0.05 m`, max drift falls below it in **0/10** repeats for
both cases.

**CORRECTED after review, and this is a real understatement in my own numbers.** A1's
`brake_mu0.55` is the *same configuration* as the `v0p5` repeats, so it is an eleventh
sample of that ensemble. Its 250-frame max drift is **0.056934**, which lands **0.87 mm
below the observed minimum of 0.057807** **[derived]**. The true spread across N=11 is
therefore at least **2.926e-03 m, about 43% wider than the 2.052e-03 m I reported**. Do
not quote 2.052e-03 without noting that a further sample of the same configuration fell
outside it. This is precisely the failure the "report N and spread, never a single draw"
rule exists to prevent, and reporting a range from 10 draws still understated it.

**Divergence begins at frame 1 in both cases**, growing from 2.6e-05 m to 3.1e-03 m
(`g96_m2337`) and from 4.9e-07 m to 2.8e-03 m (`v0p5`). So the runs are reproducible to
about **2 to 3 millimetres over 250 frames**, not bitwise.

**Do NOT compare this to the 0.52 to 1.69 m determinism floor** in the R7 record. That
floor was measured at g128 in a different scene with a rigid particle body; these are g96
and g64 with the canonical driver. Different scene, different resolution, and the
comparison would be the exact "one source cited twice" error the project's rules forbid.

**`sweepV_g64_v0p5`'s mean max drift is 0.0589 m, above the 0.05 m threshold in all ten
repeats**, which is consistent with A1's mu = 0.55 STUCK at 0.0569 m and reinforces
section 2: this STUCK verdict lives entirely on the sustained-speed conjunction, not on
displacement staying small.

## 4. `determinism_identical` is a load-time check, and its name oversells it

Every `summary.json` in all 23 runs carries `"determinism_identical": true`, while
section 3 shows the trajectories diverging from frame 1. **That is not a contradiction**,
and it was checked before being reported as one **[read]**, `sim_standing.py:389`:

```python
det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
```

It loads the hull twice and compares particle count and `grid_lim`. It is a **mesh-load
reproducibility check** and says nothing whatever about the simulation trajectory.

It is still a trap, and the same one this branch keeps finding: **a field whose name
promises more than it measures.** A reader of `summary.json` would reasonably conclude the
runs are deterministic. They are reproducible to millimetres, and the field cannot see the
difference. This is the sixth instance of the pattern collected in `START_HERE` 5b.

**trimesh 4.12.2 is load-bearing for exactly this field**: `np.random.seed` still controls
sampling on 4.x and is a **silent no-op** on 5.x. On an upgrade `det_ok` would start
failing, or worse, keep passing while the sampling drifted. State the trimesh version
beside any A2 spread, as with settle length.

## 5. Job C, re-costed as instructed

**The drop rule is retired because its premise was removed, not because I changed my
mind.** C was dropped because "its primary criterion cannot be evaluated until the Kramer
`/s1` supplementary exists". That supplementary is now on disk, and C's criteria are
quantitative: measured first damped periods **0.7869 / 0.8093 / 0.8671 s** (N = 4 each,
spreads 0.0010 / 0.0012 / 0.0029 s) with per-drop tolerances **0.096 / 0.239 / 0.435 mm**.

**The triage order does not change.** A, then B, then C last. What changes is C's drop
*reason*: from "ungradeable" to "cost only".

**The cost cannot yet be settled from the meter, and this is a measurement failure worth
recording.** `taccinfo` reported **627 SU before and after** job 917797's completed
10:11 run, and after both dead jobs. The balance is **not a live meter**; it lags. Three
jobs including a ten-minute one did not move it, which is evidence of lag, not of free
compute. **Nobody should quote a measured SU rate from this session.**

What can be said, and it is **[derived, unreviewed]**: `sacct` reports
`AllocTRES billing=72, node=1` for 917797 at 00:10:11. If SU is charged as
`billing x hours`, that is about **12.2 SU** for job A, which would put the full 4.27
node-h queue near 307 SU and C alone near 265 SU, comfortably inside 627. That is an
inference from the TRES billing field, **not** a confirmed rate, and it should be checked
against the meter once accounting catches up.

## 6. Physics-skeptic review: REVIEWED-WITH-CORRECTIONS, verdict NOT CLEAN

The review ran and returned **five blocking issues**. Its corrections are folded into the
sections above rather than appended, and the two that changed my own published numbers are
marked CORRECTED in place. Verdict summary: claim 1 **CONFIRMED, stronger than stated**;
claim 2 **CONFIRMED as a verdict, WEAKENED as stated**; claim 3 **CONFIRMED for a stronger
reason than I gave**; claim 4 **CONFIRMED but not novel**.

### 6.1 Blocking

1. **Reflection contamination**, section 2.3. Every 250-frame drift magnitude is measured
   at or after the first wall reflection. Truncate to <= 91 frames or caveat every figure.
2. **Upstream slosh scores as SLIDE**, section 2.2. Fix or caveat `failure_modes.py:170`
   before publishing any SLIDE onset or duration.
3. **`peak_surge_accel_g = 0.682 g` is a frame-0 artifact, in this job AND in the
   published record.** It is `np.gradient`'s one-sided forward difference across the
   velocity kick: `(0.228787 - 0.005759)/0.033333 = 6.6908 m/s2 = 0.68204 g`. Excluding
   frame 0 gives 0.3954 g; from frame 20 on, 0.0285 g, a **23.9x** overstatement. The real
   hydrodynamic margin to SSF is **49.8x**, not the 2.08x that quoting 0.682 g implies.
   **Never quote 0.682 g as a hydrodynamic load.**
4. **A1's control lands outside this job's own A2 range**, section 3. Spread understated
   by at least 43%.
5. **Engine `627367e` is unvalidated against the register.** Every gravity and material-8
   fact in the register was verified against the vendored **`544c93dd`**
   (`third_party/mpm-engine-544c93dd-solver-core/core/solver.py:167-169`). No local
   artifact records `627367e`'s gravity line, and no manifest field records a
   `solver_git_sha`. This is an open provenance gap of the same class as the missing
   manifest field, and it applies to every number in this document.

### 6.2 Non-blocking, but they change how things must be worded

- **mu = 0.30 is transient-dependent by measurement**, which is a stronger statement than
  "indeterminate by prior agreement". Its SLIDE rests on a **single 9-frame conjunction at
  frames 8 to 16** and nothing else in 251 frames; it becomes STUCK under `drop17` or
  `sustain_frames = 10`. mu = 0.0250 by contrast survives `drop100` and `sustain = 20`.
  Cite the measurement; the pre-registration is now the weaker argument.
- **No verdict depends on `ssf`.** The critical ssf to trip TOPPLE is 0.1588 / 0.0604 /
  0.1107 against the actual 1.42, margins of **8.9x to 23.5x**. SLIDE, FLOAT and STUCK
  never reference it. So `vehicle_params.py:150`'s "CONFIRM before use" flag endangers
  nothing here, though it does scale `ratio_topple` as 1/SSF.
- **The axis is right, the name is wrong, and do not "fix" it.** `SURGE_AXIS = 0` is
  correct because flow is +x while the hull's long axis is y, so the flow strikes
  broadside and SSF (a lateral ratio) is the right comparison. The label "surge" is
  wrong; this is sway. **Setting `SURGE_AXIS = 1` to match the name would break both the
  drift measure and the SSF comparison.**
- **Lateral drift crosses the threshold unseen.** mu = 0.0250 has `max|dy| = 0.054930 m`,
  above `slide_m`, on an axis the classifier does not test.
- **FLOAT is structurally untestable in all four runs**, including the canonical:
  `max dz = 0.0` exactly, because dz is measured from `com0` and the hull only sinks. The
  verdict string's "max lift=0.0000m" is an identity, not a measurement, and it is the P-3
  sink-into-floor signature.
- **The three runs do not start from the same state.** Friction is set before settling, so
  mu perturbs the initial condition: frame-0 `vz` is +0.0324 / +0.0322 / +0.0139 m/s. The
  effect is small and divergence tracks mu monotonically from frame 3, so friction is
  still the driver, but the single-variable framing is imperfect.
- **The D7a unit collision is live in this worktree at shifted line numbers**:
  `failure_modes.py:48,49,50` carry `slide_m` (m), `slide_speed_ms` (**m/s**) and
  `float_m` (m). The register records `:46-48`. Deduplicate by NAME and UNIT, never by
  value.

### 6.3 Still unreviewed

Sections 4 and 5 (the `determinism_identical` reading, the job C re-cost, and the SU
inference from `AllocTRES billing=72`) were **not** part of the review and remain
**UNREVIEWED**.
