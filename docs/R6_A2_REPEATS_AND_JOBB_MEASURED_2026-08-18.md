# R6: the N=1 problem measured, and Job B's decay explained

2026-08-18. Branch `claude/can-it-ford-round-5-87a6d6`, whose HEAD `1a868f3` is the J15/J16
register commit. Everything here bears directly on those two items.

**Not folded into the register on purpose.** The register merge (side A on
`claude/add-ci-checks`, side B on `claude/r5-safekeeping`) has not landed. Editing the
register here would create a third side of a two-side merge. Fold these findings in AFTER
that merge, not before.

---

## 0. What is new, in one paragraph

Job 917797 was recorded as "A1, 23 of 23 rc=0". It was not A1. `prestage_jobs.sh`'s `job_a()`
deliberately FUSES A1 and A2 into one script, because A1 is about 45 seconds of compute
against 80 to 120 seconds of warpmpm import startup. The 23 runs are 3 brake arms plus 10 + 10
repeats. **A2 had therefore already run and had never been analysed.** The Round-6 handoff
lists A2 as queued and ready; it was queued, ready, and done. Analysing it costs zero SU and
answers the N=1 problem directly.

---

## 1. The 17 canonical runs are single draws from a genuinely non-deterministic process

**MEASURED.** All 20 repeat trajectories are bit-different. Twenty distinct sha256 over
`metrics.csv`, ten per configuration, at fixed configuration with no seed change (there is no
seed flag; settle is constructor-only at the canonical 8).

Provenance, so these are comparable to the published runs: `jobA.out` stamps the driver at
`4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9`, which is the canonical
published driver sha, and the hull is
`can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`.

Divergence onset is **frame 0**, and the first column to differ is `yaw_deg`. Position holds
to frame 1 and differs from frame 2. So the runs differ in ORIENTATION at the first recorded
frame.

**CORRECTED. Row 0 is NOT the initial condition, and an earlier version of this document said
the divergence happens "before any fluid has done anything". That is false.**
`sim_standing.py:235-237` runs `for _ in range(settle_frames): self._project_water();
s.step(self.dt, self.substeps)` with `settle_frames = 8`, the velocity kick is added at
:238-240, and only then do :244-246 set `time = 0.0` and append the first history row. With
`substeps` 16 at g96 and 11 at v0p5, that is **128 and 88 solver substeps before row 0 is
recorded**. The fluid has done a great deal. The correct statement is that the runs have
already diverged by the time recording starts, which locates the divergence inside the settle
phase and does not by itself say whether the seeding or the solve caused it. This is the same
settle-transient hazard that has invalidated results on this project before.

### 1a. `determinism_identical` measures something adjacent to its own name

**MEASURED, then confirmed at primary source.** `determinism_identical` is `true` in all 20
`summary.json` files while every one of the 20 trajectories differs.

```
renders/yaris_render_s1/sim_standing.py:389
renders/yaris_render_s1/_incoming/sim_standing.py:243
    det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
```

It is a particle count and a grid limit, and nothing else. A different random surface sample of
the same watertight hull preserves both while placing every particle differently, which is
exactly what produces the frame-0 `yaw_deg` difference. The flag therefore returns `true` BY
CONSTRUCTION for runs whose trajectories diverge immediately.

This is the eighth instance of the round's core pattern, and the worst-placed one: unlike the
other seven it is stamped into the summary of every published run.

**Verified, not assumed.** `renders/yaris_render_s1/gates_results_all_runs.json` holds 20
records, the 17 gated plus the 3 dry_start, exactly as CLAUDE.md item 8 says. **17 of 17 gated
runs carry `determinism_identical: true`.** The 3 dry_start records carry the literal
`"ABSENT"`. So the flag reads true on every published run, and none of those runs has ever had
a repeat to compare against.

**Distinguish carefully from what was already known.** The handoff already recorded that this
field is a load-time hull check and not a trajectory check, and named the same line number.
That part is not new. What is new is that nobody had measured whether the trajectories actually
diverge, so nobody knew the flag is not merely weak but FALSE IN PRACTICE for all 17 published
runs.

---

## 2. The verdicts are reproducible. The margins are not.

Run with the project's own published classifier, `simulation/failure_modes.py` at `ssf = 1.42`
(vehicle_params `compact_sedan`) and `G = 9.81`, and with `margin_frames` re-implemented exactly
as `a6a707c` defines it: the longest run of consecutive frames holding the joint SLIDE
condition, minus the 3 the classifier requires.

| | published, N=1 | measured, N=10 |
|---|---|---|
| `g96_m2337` verdict | SLIDE | **SLIDE 10 of 10** |
| `g96_m2337` joint frames | 4 | 3 or 4, **3 in two draws** |
| `g96_m2337` margin | **1** | **1 in eight draws, 0 in two** |
| `v0p5` verdict | STUCK | **STUCK 10 of 10** |
| `v0p5` joint frames | 0 | 0 in all ten |
| `v0p5` margin | -3 | -3 in all ten, no spread |

**Both boundary verdicts are reproducible at 10 of 10.** This is the first repeat-based
evidence the project has for any verdict, and the STUCK control has zero spread.

**J15's "ONE-FRAME margin" is a single-draw value and is not stable.** Across ten draws the
margin spans 0 to 1, and in two of ten the joint condition holds for exactly 3 frames, which is
exactly `sustain_frames`. Those two draws sit precisely on the flip threshold with zero margin.

Restate the claim as: **zero to one frame from STUCK, N=10, two of ten at zero.** That is a
stronger statement of J15's own finding, not a weaker one. The heaviest vehicle at the finest
grid is sometimes exactly at the boundary rather than one frame off it.

### 2a-bis. The verdict survives repeats. It does not survive `sustain_frames`.

**MEASURED, zero GPU cost.** The classifier requires the joint SLIDE condition to hold for
`sustain_frames` consecutive frames. That value is `3`, declared as a bare literal at
`simulation/failure_modes.py:52`, and it has **no source anywhere**: not in CLAUDE.md, not
in the register, not in `classify_failure_modes.py`, which merely restates it at :26.

Longest joint runs across the 10 `g96_m2337` repeats are `[4,4,4,4,4,4,3,3,4,4]`. Sweeping
the threshold against those same 10 runs, window 0 to 90:

| `sustain_frames` | `g96_m2337` | `v0p5` |
|---|---|---|
| 2 | 10 SLIDE / 0 STUCK | 0 SLIDE / 10 STUCK |
| **3, the published value** | **10 SLIDE / 0 STUCK** | **0 SLIDE / 10 STUCK** |
| 4 | 8 SLIDE / **2 STUCK** | 0 SLIDE / 10 STUCK |
| 5 | **0 SLIDE / 10 STUCK** | 0 SLIDE / 10 STUCK |

**One step up from the published value flips 2 of 10. Two steps up flips all 10.** The
`g96_m2337` SLIDE verdict is not robust to a one-integer change in an unsourced threshold,
and the collapse at 5 is total rather than gradual.

This is the DRIFT_THRESHOLD problem in a new place, and worse, because `sustain_frames`
gates the verdicts in BOTH directions. Register D6f already records that it "is the only
thing keeping TOPPLE from firing on all 13". So the same unsourced integer simultaneously
suppresses 13 TOPPLE verdicts and sustains the SLIDE verdict at the finest published grid.

**`v0p5` is completely insensitive**, 0 SLIDE at every value tested, because its longest
joint run is 0. The STUCK control is robust in this dimension as well as across repeats.

**What this does and does not say.** It does NOT say the published verdict is wrong: 3 is
as defensible as 4, and nothing here identifies a correct value. It says the verdict at
`g96_m2337` rests on a threshold with no provenance, sitting two steps from total collapse,
and that this was never measured. Report `sustain_frames` beside any SLIDE verdict from that
configuration, exactly as the project already requires for DRIFT_THRESHOLD's scope.

### 2a-ter. g128: the margin reaches ZERO, in 6 of 6 draws

**MEASURED 2026-08-18, job 918247, five repeats of `g128_m2337` at 90 frames on the
canonical driver.** All five `metrics.csv` are bit-distinct, so the non-determinism of
section 1 holds at g128 too.

| source | joint frames | margin |
|---|---|---|
| their `g96_m2337`, single draw | 4 | 1 |
| **their `g128_m2337`, single draw** | **3** | **0** |
| **my `g128_m2337`, N=5** | 3, 3, 3, 3, 3 | **0, 0, 0, 0, 0** |

Their g128 value is computed here from THEIR OWN output at
`$WORK/render_s2/g128_m2337/metrics.csv` with the same classifier, not taken from prose,
because the prose is ambiguous. Commit `a677a59` reads "g96_m2337's one-frame margin does not
collapse to STUCK; it stays at 1", which is a statement about the g96 margin and is correct.
Read quickly it suggests the margin held at 1 through refinement, and **their own data does
not show that: at g128 it is 0.**

So six independent draws at g128, one theirs and five mine, all give margin **0**. The m2337
margin series is:

| grid | g48 | g64 | g96 | **g128** |
|---|---|---|---|---|
| margin | 8 | 7 | 1 (0 to 1 across my N=10) | **0, in 6 of 6** |

**The verdict survives refinement and the margin does not.** SLIDE is returned in 5 of 5 of my
repeats and in theirs, so "the verdict survives refinement to g128" stands. But at g128 every
measured draw sits EXACTLY on `sustain_frames = 3`, with zero spare frames. One fewer joint
frame in any of them and the verdict is STUCK.

**Combine that with 2a-bis and the exposure is stark.** `sustain_frames` is an unsourced bare
literal. At g128 the joint condition holds for exactly 3 frames in every draw measured, so
setting it to 4, a one-integer change to a value with no provenance, flips **all six g128
draws to STUCK**. The 16 SLIDE / 1 STUCK headline at the finest grid rests entirely on that
integer being right, and nothing in the project says why it is 3.

This does not overturn J15, it sharpens it: J15 said the margin closes with refinement and
asked for g128. The answer is that it closes **to zero**.

### 2a-quater. The complete series, N=5 at every grid

**Jobs 918247 to 918250**, five repeats of `g96_m2337`'s configuration at each of four grids,
90 frames, canonical driver, job-id-keyed paths. All 20 `metrics.csv` bit-distinct.

| grid | verdict | joint frames | margin | published single draw (a6a707c) |
|---|---|---|---|---|
| g48 | 5 SLIDE | 11, 11, 11, 11, 11 | 8, 8, 8, 8, 8 | 8 |
| g64 | 5 SLIDE | 9, 9, 9, **10**, 9 | 6, 6, 6, **7**, 6 | **7** |
| g96 | 5 SLIDE | 3, **4**, 3, **4**, 3 | 0, **1**, 0, **1**, 0 | **1** |
| g128 | 5 SLIDE | 3, 3, 3, 3, 3 | 0, 0, 0, 0, 0 | 0 (their own data) |

**The verdict is robust and the margin is not.** SLIDE in 20 of 20. But the published series
8, 7, 1 is three single draws, and **two of the three are the MINORITY value**: g64 gives 7
in 1 of 5 (mode 6), and g96 gives 1 in 2 of 5 (mode 0). Only g48 has zero spread.

**`sustain_frames` sensitivity, and it is entirely a fine-grid problem:**

| grid | sf=3, published | sf=4 | sf=5 |
|---|---|---|---|
| g48 | 5S / 0K | 5S / 0K | 5S / 0K |
| g64 | 5S / 0K | 5S / 0K | 5S / 0K |
| g96 | 5S / 0K | 2S / **3K** | 0S / **5K** |
| **g128** | 5S / 0K | **0S / 5K** | 0S / 5K |

At g48 and g64 the verdict is completely insensitive to the threshold. At g128 a
**one-integer change to a value with no provenance flips all five runs**. So the exposure
is not uniform across the study: it is concentrated exactly where the refinement argument
lives. Any claim that the verdict survives refinement must state `sustain_frames` alongside
it, because at the finest grid that integer IS the verdict.

### 2a-quinquies. The ladder is inadequate against the literature's own criterion, at EVERY grid

**MEASURED from the hull mesh, `analysis/r6_hull_clearance.py`.** The corpus review
"Particle Resolution and Force Convergence for Rigid Bodies in Flood-Type Flows: A Critical
Review" (`/Users/josie/Claude/reu/compass_artifact_wf-211aad60-...md`) makes two findings
that bear directly on section 2a-quater, and this project has absorbed neither.

**First: there is NO validated force-convergence criterion** for particle methods on immersed
bodies. Only conventions. The two most cited are `dp <= D/10` on the smallest force-bearing
feature, and ~10 particles per flow depth (40 for broken waves). The depth rule is attributed
to a 2021 *Engineering Structures* tsunami study and was calibrated on free-surface elevation,
NOT on force. So L-3's "roughly 10 particles per flow depth" does have a lineage, but it
cannot legitimately be cited as a FORCE criterion. Provenance is being traced separately.

**Second, and this is the one that reframes everything: set spacing from the SMALLEST
FORCE-BEARING FEATURE, and for a vehicle the review names the GROUND CLEARANCE explicitly**,
not the body length and not the domain. This project sets `dx` from the domain.

The clearance is recorded nowhere in `vehicle_params.py`, so measure it. Binning the
327,212 hull vertices in plan and taking per-column minima between the axles (a global z-min
returns the tyre contact patch, not the clearance):

| region | min | 5th pct | median |
|---|---|---|---|
| central 40% length x 50% width | 160.5 mm | **177.4 mm** | 201.9 mm |
| between axles, full width | 160.5 mm | 177.0 mm | 204.5 mm |

**Underbody clearance = 177 mm.** Against it:

| grid | dx | cells across the clearance | meets `dp <= D/10`? |
|---|---|---|---|
| g48 | 196.3 mm | **0.90** | no |
| g64 | 147.2 mm | 1.21 | no |
| g96 | 98.1 mm | 1.81 | no |
| g128 | 73.6 mm | 2.41 | no |
| g160 | 58.9 mm | 3.01 | no |
| g192 | 49.1 mm | 3.61 | no |

**At g48, the published baseline, `dx` is LARGER than the ground clearance.** The gap that
carries the entire underbody flow is sub-cell. `D/10` would require `dx <= 17.7 mm`, about
4.2x finer than g192, roughly g810 on this domain, and unreachable.

**This is a mechanism for the margin collapse, not just a caveat.** The review documents that
coarse resolution most often OVER-predicts peak hydrodynamic force, via boundary kernel
truncation and particle deficiency. An underbody gap spanned by 0.9 cells cannot pass flow
correctly and blocks it instead, inflating drag, inflating sliding, inflating the margin. As
`dx` falls from 196 to 74 mm the gap resolves from 0.9 to 2.4 cells and the spurious force
drains away. Margin 8 to 0. **The collapse is the artifact leaving, not the physics arriving,
and nothing indicates it has bottomed out.**

**The free win nobody has proposed.** `grid_lim` is 9.42 m for a 4.28 m hull, so 2.2 vehicle
lengths of largely empty water, and it is DERIVED from the hull extent rather than chosen. At
fixed `n_grid`, shrinking the domain multiplies resolution at zero compute cost. A 6 m domain
at g128 would give `dx` 46.9 mm, i.e. 3.8 cells across the clearance, beating g192 on the
current domain for less than half the particles. Being costed separately, with the
wall-reflection window as the constraint.

**Caveat on the bias direction.** CLAUDE.md L-4 states coarse over-prediction as settled and
concludes NO-FORD verdicts are "therefore conservative". The review calls it "a documented
tendency with clear exceptions, not a consistently validated law", with a documented inversion
where over-fine resolution triggered premature wave breaking and UNDER-predicted. The
conservatism argument survives for SAFETY, since predicting unsafe when it is safe errs the
right way. It does not survive for the SCIENTIFIC claim: the verdict distribution is biased
toward SLIDE by an amount nobody has bounded.

### 2a. What this does NOT overturn

J15's refinement trend survives. The `m2337` series collapses 11 to 10 to 4 across g48/g64/g96,
a drop of 7 frames, against a measured run-to-run spread of 1 frame at the one point where
repeats exist. A 7-frame collapse is far outside a 1-frame noise band, so the trend is not a
noise artifact.

**Tag this honestly: transferring the g96 spread to the g48 and g64 points is an ASSUMPTION.**
There are no repeats at those two grids. It is a falsifiable test that came out confirming, and
it is written up the same way it would have been if it had overturned.

### 2b. J16, partially addressed

J16 records that six margins are not independently checkable, because job 866887 overwrote the
g48/g96 directories on 2026-07-26, and that the most fragile verdict in the set is one of the
six. These repeats do not recover the original run and cannot. They do give, for the first time,
an independent N=10 measurement of the margin AT that configuration. The original single draw
stays unrecoverable; the quantity it was measuring is now known with an error bar.

---

## 3. The noise floor does not transfer between statistics, demonstrated on one dataset

Same 20 runs, same frames, four statistics:

| statistic | spread across 10 repeats |
|---|---|
| `margin_frames` | 0 to 1 frame, and IDENTICAL at the 90, 111 and 250 frame windows |
| `dmag` at frame 90 (canonical) | 3.70 % of mean (`v0p5`), 2.35 % (`g96_m2337`) |
| `dmag` at frame 250 | 9.56 % (`v0p5`), 4.48 % (`g96_m2337`) |
| `leaked_particle_frames` | 489,722 to 490,044, a range of 0.066 % |

**CORRECTED: the canonical horizon is row index 90, not 91.** Verified live at
`renders/yaris_render_s1/_incoming/g96_m2337/summary.json`, which carries `"frames": 90`, and
whose `metrics.csv` holds 92 lines, that is one header plus 91 data rows at indices 0 to 90,
with last `t` = 2.999999999999999 s, exactly 3.0 s at 30 fps. An earlier version of this
document reported the canonical column at frame 91, which is one row past the horizon. The
corrected figures are 3.70 and 2.35 percent, against the 3.84 and 2.38 previously stated. The
verdicts and margins are unchanged at either window.

The 250-frame window inflates the `dmag` spread by about 2.6x on `v0p5` through wall-reflection
contamination (first reflection predicted at frame 112.3, observed at 112, 125, 126), while
leaving `margin_frames` completely unchanged, because the joint SLIDE condition fires early.

**Operationally: `margin_frames` may be quoted off the 250-frame runs. `dmag` may not.** Always
name the statistic beside any spread, and name the frame window beside any magnitude, and state
which row index the window ends on rather than a frame count, since 90 frames is 91 rows.

---

## 4. Job B, job 918043: the decay is the tank draining, and the pre-registration proved it

Submitted by `sbatch` on partition `gh`, NOT idev. COMPLETED, 00:06:45, ExitCode 0:0, rc=0,
`ALLDONE`, 200 frames. Roughly half of 917909's 13:55, from the SDF cache fix in `d9ff5f7`.

The run used the measured-surface build staged at `$WORK/d4_scene/sphere_heave.py`,
sha256 `f74223122ae868c1a1e95c4e061eac55e649ccbdf47da49782460b9833e10118`, byte-identical to the
local file at branch HEAD. The criterion was committed at `ae08cce` BEFORE any run had ever
produced the field, so it cannot have been tuned to this result.

`grade_job_b.py` reports **NOT GRADEABLE** on the nominal series, rejecting it for
non-stationarity. Late-window mean 53.5913 N against the 69.2180 N target. **Do NOT stop
reading there, and do not repeat that as the verdict: it is not what the manifest asks for.
See 4a-bis, which supersedes it.** `68731f7` fixed the tuple-parsing bug that previously
reported PASS at -9.806 percent, so the tool no longer passes a bad run; it now refuses a
gradeable one instead.

### 4a. The mechanism fired

Under the project's own `blocking.stationarity`, late window frames 100 to 199:

| series | halves_stationary | trend_stationary | slope, blocked sigma |
|---|---|---|---|
| `fz_N` | False | False | 8.52 |
| `fz_over_analytic_nominal` | False | False | 8.52 |
| **`fz_over_analytic_measured`** | **True** | **True** | **0.15** |

The 8.52 reproduces `grade_job_b.py`'s own reported figure exactly, which is the cross-check
that the harness here is the same one the grader uses.

Normalising the reaction by the closed form at the surface that actually exists converts a
decisively non-stationary series into a stationary one, 8.52 sigma to 0.15. **That settles the
question 917909 could not answer: the decay is the tank draining, not the coupling failing.**

All sigmas here are blocked, not OLS. It matters in both directions: blocking DEFLATES the
`fz_N` figure (a naive OLS gives 23.28) and it also deflates the measured ratio's (naive 0.24
to blocked 0.15). The stationarity conclusion is robust either way, since both readings sit far
below any threshold, but quote the blocked ones.

### 4a-bis. CORRECTED VERDICT: Job B FAILS, and the ladder is stopped

**An earlier version of this document reported Job B as NOT GRADEABLE and stopped there.
That was wrong, and the error was mine, not the tool's.** I took `grade_job_b.py`'s refusal
as the answer instead of grading against the criterion the tool exists to implement. Three
things, all read live at source, settle it:

1. `docs/R5_PHYSICS_BATCH_MANIFEST.md:214`: "Pass criteria, fixed in advance and graded in
   this order. **Any FAIL stops the ladder.**"
2. `simulation/r5_physics/sphere_heave.py:669-670`, in the code that writes the field:
   "**`fz_over_analytic_measured` is the number job B should actually be graded on**".
3. Manifest criterion 5: "Stationarity, via `blocking.py`. Given what blocking found on the
   C1-SDF series, a **NOT-STATIONARY verdict here is expected, not disqualifying**."

So the grader refuses on precisely the ground the manifest says is not disqualifying. The
first version of that grader wrongly reported PASS at -9.806 percent; the fixed version now
wrongly refuses. Both failures are the same shape: the check and the criterion were never
connected.

Graded against criterion 3's bands (10 PASS, 10 to 25 REPORTABLE PARTIAL, beyond 25 FAIL):

| accessor | last 20 | last 40 | last 80 | last 100 | last 150 | last 200 | stationary |
|---|---|---|---|---|---|---|---|
| `fz_over_analytic_nominal` | -29.11 **FAIL** | -27.92 **FAIL** | -24.68 PARTIAL | -22.58 PARTIAL | -17.12 PARTIAL | -9.67 **PASS** | No, 8.52 sigma |
| `fz_over_analytic_measured` | +64.19 | +63.52 | +62.97 | +63.08 | +61.68 | +61.08 | **Yes, 0.15 sigma** |

**The nominal accessor cannot yield a verdict.** Criterion 3 names no window, and on a series
this non-stationary the window chooses the band: FAIL, REPORTABLE PARTIAL and PASS are all
reachable from the same 200 frames. A criterion with an unnamed free parameter that selects
its own outcome was not operationally fixed in advance, whatever its text says.

**The measured accessor is stationary, therefore window-robust, and it FAILS at every window
from last-20 to last-200, +61.08 to +64.19 percent.** It is also the accessor the code itself
designates. So:

> **JOB B: FAIL on criterion 3. Per manifest line 214, the ladder is stopped.**

**UPDATED with the h/2 surface fix, and the verdict is unchanged.** The figures in the table
above are from 918043, which predates commit `7c9e0af`'s correction to `measure_surface` and
is therefore biased HIGH on this ratio. The corrected run is **918240 at +50.06 percent**,
still FAIL at every window from last-20 to last-200. See section 4d-bis for how the two runs
were told apart, which was by sha and not by timestamp. **Quote +50.06, not +63.**

This is a decision for Josie, not for a session to quietly route around. The two honest
options are to accept the FAIL and stop the ladder as the manifest instructs, or to amend the
criterion in writing, naming the accessor AND the window, and state explicitly that a band
declared unmovable was moved. Do not let Job C proceed on an assumption that B passed.

### 4b. The level, and why neither target is right

Stationary ratio **1.6308 ± 0.0082**, blocked SE, converged, plateau at block size 8 with 12
blocks, inflation over naive 1.548, tau_int 2.396 frames. That is **+63.1 percent**, outside the
pre-registered 25 percent FAIL band. The nominal ratio was 0.774, i.e. -22.6 percent, outside it
in the other direction. The true reaction sits BETWEEN the two targets and neither is right.

The estimator is not arithmetically at fault. Recomputing the spherical cap independently from
`surface_z_measured_m`, with `ref_radius_m` 0.15 and sphere centre fixed at z = 0.575, reproduces
the reported `submerged_cap_m3` to six decimals at every frame checked.

### 4c. The surface fall, measured rather than inferred

Design waterline is z = 0.575 m (`floor_m` 0.075 plus `depth_m` 0.5), and the sphere centre is
fixed at exactly that height, half submerged, `ref_density_kg_m3` 499.11 against water 998.2.

| frame | surface z, m | drop from design | `fz_N` | measured ratio |
|---|---|---|---|---|
| 0 | 0.561534 | 1.347 cm | -0.0666 | -0.0011 |
| 50 | 0.539878 | 3.512 cm | 51.5764 | 1.1373 |
| 100 | 0.526719 | 4.828 cm | 64.6597 | 1.7498 |
| 150 | 0.519832 | 5.517 cm | 51.9991 | 1.5876 |
| 199 | 0.514445 | **6.055 cm** | 47.8245 | 1.6168 |

Monotone, and still falling at frame 199: `blocking.stationarity` on `surface_z_measured_m`
over the late window gives `trend_stationary=False` at **19.98 sigma**. (A naive OLS slope test
gives 58 sigma on the same series; use the blocked figure, because OLS assumes independent
residuals that an autocorrelated series does not have.) The handoff's 3.09 cm was back-derived
from a force deficit on a shorter run; the direct measurement is roughly double it and has not
converged. **This confirms the handoff's call that more frames alone will not fix it.**

### 4d. The volume budget: compression is bounded, the fall is not

The tank's plan area is not in the config, so derive it. `n_water` 598,505 particles at spacing
`h_m` 0.009375 gives a particle volume of h^3 = 8.2397e-7 m3 and a water volume of
**0.493153 m3**. Adding the 8,292 carved particles (0.006832 m3, against the sphere's analytic
half-volume of 0.007069, a 3.4 percent discretisation shortfall as expected) and dividing by
`depth_m` 0.5 gives a plan area of **0.999971 m2**, which closes on exactly 1.0 m2 to 0.003
percent. So the tank is 1.0 x 1.0 m of water inside a 1.2 m grid. DERIVED, not read.

Compression, computed independently from the sound speed rather than taken from the docstring:
bulk modulus K = rho c^2 = 998.2 x 12.8568^2 = 165,000 Pa; mean hydrostatic pressure over the
column rho g d / 2 = 2448.1 Pa; strain **1.4837 percent**, so the column shortens **0.7418 cm**.
`sphere_heave.py`'s own docstring says 1.497 percent and 0.74 cm. Independent agreement, from a
different starting point.

| surface drop | source | volume lost | compression explains | UNEXPLAINED |
|---|---|---|---|---|
| 3.090 cm | 917909, back-derived from a force deficit | 6.27 % of the water | 24.0 % | 76.0 % |
| **6.055 cm** | **918043, measured directly** | **12.28 % of the water** | **12.3 %** | **87.7 %** |

The 24.0 percent reproduces the handoff's 23.9 percent, which is real corroboration because it
was reached from the sound speed rather than copied.

**The decisive point is the trend, not the level.** Compression is a ONE-TIME 0.7418 cm: once
the column reaches hydrostatic equilibrium it contributes nothing further. The surface has
fallen 6.055 cm and is still falling at 19.98 sigma at the last frame. So every additional
centimetre beyond the first 0.74 is 100 percent unexplained, and the unexplained fraction has
grown from 76.0 to 87.7 percent purely because the run got longer. **The mechanism is ongoing
and it is not compression.** Roughly 0.0531 m3 is unaccounted for, about 64,500 particles' worth
of volume.

### 4d-bis. ANSWERED: the water leaks through the floor plane

**Job 918240**, the same scene with `water_budget()` instrumentation added, COMPLETED rc=0,
200 frames. The instrumentation was built with an explicit discriminator: counts GROW under
leakage, occupied volume FALLS under compaction, and the two are independent so one run
separates them.

| frame | `n_below_floor` | `n_outside_walls` | `occupied_volume_m3` | `water_z_min_m` | surface drop |
|---|---|---|---|---|---|
| 0 | 2,248 | 965 | 0.518056 | 0.07411 | 0.878 cm |
| 25 | 11,849 | 10,301 | 0.506520 | 0.06044 | 2.325 cm |
| 50 | 16,610 | 10,901 | 0.497694 | 0.05890 | 3.043 cm |
| 100 | 22,122 | 12,613 | 0.496296 | 0.05290 | 4.359 cm |
| 150 | 25,301 | 13,640 | 0.490753 | 0.05235 | 5.048 cm |
| **199** | **26,964** | **14,423** | **0.492308** | **0.05236** | **5.587 cm** |

**It is LEAKAGE.** The counts grow monotonically and are still growing at the last frame:
`n_below_floor` rises 12x to **4.505 percent of all water**, and `water_z_min_m` ends at
0.05236 against a floor plane at `FLOOR = 0.075`, i.e. **2.4 cm underneath it**.
`n_outside_walls` rises 15x to 2.410 percent. Occupied volume falls only 4.97 percent and is
essentially flat after frame 50, which is the compaction signature and it is the SMALLER term.

Budget, at the 5.587 cm this run measured:

| term | contribution | of the fall |
|---|---|---|
| leakage, roughly 6.9 percent of particles leaving the column | ~3.45 cm | 62 % |
| compression, the bounded one-time term | 0.74 cm | 13 % |
| **residual, still unexplained** | **~1.4 cm** | **25 %** |

**That moves the unexplained fraction from 87.7 percent to about 25 percent, and names the
dominant mechanism.** The residual is real and should not be rounded away; leakage and
compression are not additive in a strict sense because a particle below the floor still
displaces nothing in the column, so treat the split as indicative and the identification as
the result.

**This is a known engine defect, not a new one.** CLAUDE.md item 7 records that all three g48
runs fail gate P-3 with a negative z rise near -0.05 m, "the hull sank into the floor plane".
The same floor plane leaks water here. The two are almost certainly the same defect seen from
two sides.

**It also corroborates the other session's B3 measurement independently** (commit `be1b138`):
in a channel at ZERO grade a closed box manufactures +0.0927 m/m of free-surface slope and
drains 2 of 12 bins, while a recycling BC leaves 33x less and drains none. Different scene,
different diagnostic, same engine, same conclusion: **the closed-domain configuration loses
water at zero forcing.** Two independent origins, so this is corroboration rather than one
source cited twice.

**CORRECTED. The two runs are the SAME trajectory, not two draws.** An earlier version of
this section said the 6.055 cm and 5.587 cm drops were "different draws of a
non-deterministic process". That is false. Both runs report a bias-free drop CHANGE over
the run of **4.709 cm, identical to three decimals**, because the sphere scene seeds at
`seed: 0` with no trimesh surface sampling and is therefore deterministic, unlike the
vehicle scene of section 1. The entire 0.469 cm difference is the h/2 surface fix, see
below.

**THE h/2 SURFACE BIAS, and which of my runs carries it.** A concurrent session found that
`measure_surface` took a percentile of particle CENTRES, which sit h/2 below their layer's
fill line, so it under-read the free surface by h/2 = dx/4 = 4.688 mm at this resolution
(commit `7c9e0af`, "runs before this commit are biased LOW on the surface and HIGH on
`fz_over_analytic_measured`"). Established by sha, not by timestamp: `7c9e0af`'s version of
`sphere_heave.py` is sha256 `583b4c7af94dca...`, which is EXACTLY the file staged to Vista
and run as 918240.

| run | h/2 fix | late-window `fz_over_analytic_measured` | surface drop at last frame |
|---|---|---|---|
| 918043 | **no** | +63.08 % | 6.055 cm |
| **918240** | **yes** | **+50.06 %** | **5.587 cm** |

**Quote 918240. 918043 is superseded.** Applying the h/2 correction to 918240 a second time
would double-count and yields a spurious +38 percent; I did that once before checking the
sha, and the sha is what settled it.

**The FAIL verdict survives the correction**: +50.06 percent is still far outside criterion
3's 25 percent FAIL band, at every window from last-20 to last-200. What changes is the
magnitude, not the band.

**The leakage result in the table above is UNAFFECTED**, because `n_below_floor`,
`n_outside_walls` and `water_z_min_m` are direct particle counts against the floor plane and
wall bands, not surface-derived quantities.

**Open, and now sharply posed:** does the leak fraction fall when the walls move away at held
dx? Job `918251` runs the same scene at `lim` 2.2 / `n_grid` 117 (dx 0.018803 against
0.018750, so dx is held and only the domain grows) to answer exactly that.

### 4d-ter. Domain-size control: two mechanisms separated, and the FAIL survives

**Job 918251**, the same scene at `lim` 2.2 / `n_grid` 117 (dx 0.018803 against 0.018750, so
dx is held to 0.28 percent and only the domain grows), 4x the water plan area, 2,396,211
particles against 598,505. COMPLETED 00:08:22, rc=0.

| quantity at the last frame | lim 1.2, 1.0 m2 | lim 2.2, 4.0 m2 | ratio | predicted |
|---|---|---|---|---|
| `n_below_floor` | 4.505 % | 3.796 % | 1.19 | **1.00** if area-distributed |
| `n_outside_walls` | 2.410 % | **1.231 %** | **1.96** | **2.00** if perimeter-driven |
| combined leak | 6.915 % | 5.026 % | 1.38 | |
| surface drop | 5.587 cm | 4.125 cm | 1.35 | |
| `fz_over_analytic_measured` | 1.4790 | 1.4654 | **1.01** | |

**The wall leak is a boundary artifact, quantitatively.** For a square of side L the
perimeter-to-area ratio is 4L / L^2 = 4/L, so doubling L must HALVE a perimeter-driven leak
fraction. Measured 1.96 against a predicted 2.00, agreement to 2 percent. That is a
prediction made from geometry before the run and matched by it, not a curve fitted after.

**The floor leak is NOT.** The floor area scales WITH the domain, so an area-distributed
floor loss should give a fraction independent of L, ratio 1.00. Measured 1.19. It barely
moves, which is the signature of a loss spread over the whole floor rather than concentrated
at an edge. So the two leaks in section 4d-bis are two DIFFERENT mechanisms and should never
be quoted as one number again.

**THE HEADLINE: Job B's FAIL is not a bounded-domain artifact.** Quadrupling the plan area
moves the graded ratio by 1 percent, 1.4790 to 1.4654. The most obvious alternative
explanation for a +48 percent overshoot, that the tank is too small, is **refuted by direct
measurement**. Whatever is wrong is not the domain.

This also sharpens what the other session's B3 result does and does not transfer. `be1b138`
measured a closed box manufacturing false free-surface slope in a CHANNEL, and that IS a
boundary effect. The wall component here behaves the same way. But the dominant term in this
scene is the floor, and it does not scale like a boundary at all.

### 4e. One hypothesis tested and largely refuted, by reading the code

The obvious unifying explanation for both anomalies, the +63 percent ratio and the missing
volume, is that the surface estimator samples where the sphere depresses the surface, which
would under-report the waterline and inflate the ratio while inventing a volume loss.

**`sphere_heave.py:605-629` already guards against exactly that.** It excludes every particle
within `2.0 * self.radius` of the sphere axis, on the stated grounds that the annulus carries
the meniscus and any splash and is a local deformation rather than the tank's free surface, and
it takes the 99th percentile rather than the max so a single ejected particle cannot define a
surface. The simple version of the hypothesis is therefore refuted at source, and the mystery
deepens rather than resolving. Name the mechanism, then check it fires; this one does not.

What survives as candidates are the two named in `f5e2f30`: particles leaving through the floor
or wall bands, and the jittered seed lattice settling denser than it was created. Both are
volume questions, not mass questions, since the particle count is fixed at load.

**The instrumentation that would settle it in one run:** record per frame the count of particles
below the floor plane and outside the wall bands, and the mean local packing density. If the
count is flat and the density rises, it is settling; if the count grows, it is leakage. Neither
is currently recorded, and both are cheap.

### 4f. The caveat that must travel with this

The measured ratio is flat because numerator and denominator are falling together in proportion.
That confirms the decay MECHANISM. It does NOT mean the system reached equilibrium, and the run
is a transient throughout, so **+63 percent is not a validation number and must never be quoted
as one.**

What Job B bought is the conversion of "we cannot distinguish a broken coupling from a draining
tank" into "it is the draining tank, measured", plus a sharper question: where does 6 cm of water
column go, when the particle count is fixed at load and no particle is created or destroyed
during a run, and compression accounts for well under a quarter of it.

---

## 4g. A1's caveats, independently re-derived from the same job's data

The handoff states these as caveats that must travel with A1. None had been re-derived. All are
now checked against `d4_jobA/brake_mu*/metrics.csv` using the published classifier.

| claim | status |
|---|---|
| mu = 0.55 reproduces STUCK, the control holds | **CONFIRMED**, 0 joint frames of 251 |
| mu = 0.30 SLIDE at frame 8 | **CONFIRMED**, first sustained index 8 |
| mu = 0.0250 SLIDE at frame 6 | **CONFIRMED**, first sustained index 6 |
| `peak_surge_accel_g` 0.682 g is a frame-0 artifact | **CONFIRMED**, the max is at frame 0 exactly |
| excluding frame 0 gives 0.3954 g | **CONFIRMED to 4 dp** |
| from frame 20, 0.0285 g | **CONFIRMED to 4 dp** |
| real margin to SSF is 49.8x, not 2.08x | **CONFIRMED**, 49.82x from frame 20 against 2.08x including frame 0 |
| 102 of 191 conjunction frames have vx below zero | **CONFIRMED exactly** |
| mean -0.1617 m/s | **CORRECT, but the statistic must be named.** See below |

**The one number that needs its statistic named.** -0.1617 m/s is the mean over the 102 NEGATIVE
frames, not over all 191 conjunction frames. Both readings are grammatically available in the
handoff's sentence. Over the same 191 frames:

```
mean vx over ALL conjunction frames  +0.0156 m/s
mean vx over the NEGATIVE subset     -0.1617 m/s   <- 102 frames, this is the handoff's number
mean vx over the POSITIVE subset     +0.2187 m/s   <-  89 frames
mean |vx| over all conjunction       +0.1882 m/s
min  vx over all conjunction         -0.2361 m/s
```

**This sharpens the caveat rather than weakening it.** The natural misreading, that the vehicle
drifts upstream on average, is false: the mean over all conjunction frames is +0.0156 m/s, which
is nearly zero. What is actually happening is an OSCILLATION about a near-stationary mean, 53.4
percent of frames upstream at mean -0.1617 and 46.6 percent downstream at mean +0.2187. The
`abs()` at `failure_modes.py:170` converts that oscillation into 191 consecutive frames scoring
as sustained sliding. "Upstream slosh scores as SLIDE" understates it: a vehicle going nowhere
on average scores as SLIDE.

This is the project's own deduplicate-by-name-and-unit rule appearing in a new place. A mean is
not a statistic until its support set is named.

## 5. Closed, with evidence

**CLAUDE.md item 15 and Round-6 handoff section 4 item 5 are CLOSED, not started.**

Commit `e495b56`, 2026-08-12, set `simulation/failure_modes.py:14` to 9.81, regenerated
`data/failure_modes_by_run_classified.csv` and `data/failure_modes_by_run.json` via
`analysis/classify_failure_modes.py`, and recorded the outcome: verdicts unchanged at 16 SLIDE
and 1 STUCK, all 17 run-to-mode pairs and all triggered flags byte-identical, exactly 3 of 33
columns moved, all direct functions of G. That is precisely the closure procedure item 15
demanded, including the instruction not to close it by assertion.

`git merge-base --is-ancestor e495b56 origin/main` returns true, so it is published.

On Vista, `can-it-ford-track1-6dof` (the tree holding the published driver) and `d5_seedpolicy`
both carry `G = 9.81`. The only remaining 9.80665 copies are under `can-it-ford-OLD-pre-purge`
and `home_archive`, which safekeeping already decided not to re-import as history. The handoff
conflated a stale pre-purge copy with an open task.

---

## 6. What to do next

1. **Restate J15's margin** as zero to one frame, N=10, two of ten at zero. J15's headline ask,
   run the canonical set at g128, is unchanged and is still the highest-value open item.
2. **Fix or retire `determinism_identical`.** It cannot be left reading `true` on every published
   run while every trajectory differs. Either rename it to what it measures, hull load
   reproducibility, or make it compare trajectories.
3. **Job B's open question is where the water goes, and section 4d sharpens it.** Compression is
   a bounded one-time 0.7418 cm against a 6.055 cm fall that is still going at 19.98 sigma, so
   the mechanism is ongoing and cannot be compression. Add the two per-frame counters named in
   4e (particles below the floor and outside the wall bands, plus mean packing density) and one
   short run settles leakage against settling. Candidates named in `f5e2f30`: particles
   leaving through the floor or wall bands, or the jittered seed lattice settling denser than it
   was created. The particle count is fixed at load, so this is a volume question, not a mass one.
4. **The grader short-circuits before the companion.** `grade_job_b.py` refuses on the nominal
   stationarity test and never reports `fz_over_analytic_measured`, although `ae08cce` specifies
   it be reported ALONGSIDE the nominal and that the tool say so out loud when they differ. The
   measured series is present in the output JSON for all 200 frames. Report both, then refuse.

## 7. Reproducing everything above

Every number in this document is regenerated by one script, which prints its enumeration
rather than a bare total:

```
/opt/homebrew/bin/uv run --with numpy python3 analysis/r6_repeat_stats.py \
    --jobA <extracted d4_jobA dir> --jobB <sphere_fixed_g64.json>
```

`blocking.py` lives in `simulation/r5_physics/` on `claude/r5-physics` and is NOT on every
branch, including this one. The script locates it across sibling worktrees and fails with a
message naming the branch rather than an ImportError. Override with `--blocking-dir`.

`--windows` defaults to 90, 111 and 250 and the output flags any window at or past the first
observed wall reflection at frame 112. 90 is the canonical row index, see section 3.

### The data


Metrics for all 23 runs of job 917797 were pulled as a 914 KB tarball, `metrics.csv` plus
`summary.json` only, leaving the 8.2 GB of `rollout.npz` on Vista:

```
ssh vista "cd /work/11603/jcerrell0629/vista && tar czf d4_jobA_light.tgz \
  d4_jobA/*/metrics.csv d4_jobA/*/summary.json d4_jobA/jobA.out d4_jobA/jobA.err d4_jobA/run_jobA.sh"
scp vista:/work/11603/jcerrell0629/vista/d4_jobA_light.tgz .
```

Job B's result is `/work/11603/jcerrell0629/vista/d4_jobB_918043/sphere_fixed_g64.json`, 122 KB,
200 rows carrying `fz_over_analytic_measured`, `surface_z_measured_m`, `surface_drop_m`,
`submerged_cap_m3` and `analytic_buoyancy_at_measured_surface_N`.

There is no numpy on any system python on this Mac. Use `/opt/homebrew/bin/uv`, for example
`uv run --with numpy python3 <script>`.

One incidental shell trap, because it cost real time: in zsh, `while read -r a b path` clobbers
`$PATH`, since `path` is tied to it. Every external command then fails with "command not found"
while builtins keep working, which reads as a broken tool rather than a broken variable name.
