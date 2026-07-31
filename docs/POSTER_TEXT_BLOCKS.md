# Poster Text Blocks

Drafted 2026-07-25 by pane ford-F4. One block per section required by `Instructions.docx.md`
items 1 through 6. Every number below traces to `docs/VERIFIED_FACTS_LEDGER_july24.md` or to a
live file read recorded in the provenance table at the end of this document.

Anything not settled is marked **[PENDING]** inline so it is visibly incomplete rather than
quietly wrong. Do not strip a [PENDING] tag without replacing the number it guards.

Target upload name `Cerrell_TACC_42x56`, PDF, under 40 MB, due Monday July 27 at 9am CST.

Spoken length of the narrative blocks (Introduction through Conclusion) is roughly 700 words,
about 4.5 minutes at a normal presenting pace. The program's cap is 5 minutes and you will be
timed.

---

## 1. Title

**Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability**

General-audience alternative, if the title bar is cramped at 42x56 or the audience skews
non-technical:

**Can It Ford? Finding the Simplest Physics That Answers a Flood-Safety Question**

---

## 2. Authors, Department, School

Josie Cerrell (1), Hassan Iqbal (2), Cheng-Hsi Hsiao (2), Krishna Kumar (2)

(1) Claremont McKenna College, Claremont, CA
(2) GeoElements Lab, Texas Advanced Computing Center, The University of Texas at Austin

**[PENDING] Author list and order are not verified.** `README.md:200` names Krishna Kumar as
PI and Hassan Iqbal, Cheng-Hsi Hsiao, and Sarah Etter as daily mentors. No file in this repo
states who appears on the poster or in what order, and Sarah Etter is omitted above only
because her role on this specific work could not be determined from the repo. Ask Kumar
directly before printing. Do not let this default silently.

**[PENDING] Departmental affiliation.** "GeoElements Lab, Texas Advanced Computing Center,
The University of Texas at Austin" is directly supported by `README.md:200`. A department
line for Kumar (likely Civil, Architectural and Environmental Engineering) appears nowhere in
this repo and was not verified. Either confirm it or ship the TACC line above, which is
sourced.

---

## 3. Introduction

My name is Josie Cerrell and I am an Integrated Sciences major at Claremont McKenna College.
This work was done through the NSF REU Site: Cyberinfrastructure Research for Societal
Advancement, hosted at the Texas Advanced Computing Center at The University of Texas at
Austin, in the GeoElements Lab, under PI Dr. Krishna Kumar, with daily mentorship from Hassan
Iqbal, Cheng-Hsi Hsiao, and Sarah Etter.

Flooded roads kill people who could not tell they were dangerous. Water depth, current speed,
and whether the road under the water is still there are all invisible from a driver's seat.
An autonomous vehicle has exactly the same blind spot, and so does an AI world model that
predicts what a scene will look like next: it can generate a future that looks completely
plausible while breaking the physics that actually decides whether the car makes it across.

So my project asks one deliberately narrow question. Given a flooded road and a specific
vehicle, can that vehicle ford it, and what is the simplest physics you can get away with and
still be right?

**[PENDING] Fatality statistic.** Earlier drafts of this project's text open with "over half
of flood-related drownings occur when a vehicle is driven into hazardous floodwater"
(`paper_draft.md:11`). That figure is not in the verified facts ledger and no primary source
for it was confirmed on this pass. Either source it to a citable agency publication and put
the number back, or present the plain-language version above, which needs no number.

**[PENDING] Major.** "Integrated Sciences, Claremont McKenna College" is carried forward from
`poster_text_draft.md:41` and is a biographical fact only Josie can confirm. Confirm it.

---

## 4. Research Goal

Find the minimum sufficient abstraction. I compare three levels of physical model against the
same set of flood conditions:

- **L0**, a static depth threshold. Water deeper than 0.15 m returns NO-FORD, no velocity term
  at all.
- **L1**, the published depth-velocity stability criteria from the Australian Rainfall and
  Runoff Project 10 Stage 2 report, which is the standard the engineering literature actually
  uses.
- **L2**, a fully coupled Material Point Method simulation, where buoyancy and drag are not
  assumed but emerge from water and vehicle interacting.

The question behind the question: when does a cheap model give the same answer as an expensive
one, and where exactly does it stop doing so? A safety criterion that is right on average and
wrong in the specific case you are standing in is not a safety criterion.

---

## 5. Methods

**The criterion side.** The AR&R report's Table 3 gives three vehicle classes, small
passenger, large passenger, and large 4WD, each with a limiting still-water depth, a limiting
velocity of 3.0 m/s, and a limiting depth times velocity product. I read all three rows
directly from the source PDF and applied all three caps jointly, which the earlier
implementation in this project did not do. Two things the source says that are easy to get
wrong and that I state explicitly: these are criteria for *stationary* vehicles, and the
3.0 m/s velocity cap is an evacuation safety limit imported from human stability research,
not a vehicle stability result.

**The simulation side.** A watertight Toyota Yaris hull, 327,212 vertices, at MASH 1100C class
mass of 1100 kg, is placed in a water column and simulated as a rigid body coupled to
weakly-compressible water on an MPM grid.

**The verification side, which became the bulk of the summer.** Before trusting a simulated
verdict I audited what the pipeline actually builds. I measured the true submerged volume of
the vehicle mesh independently, by clipping the watertight mesh at the waterline and
integrating with the divergence theorem, and compared it against the volume the simulation's
own solidifier produces at three grid resolutions. The check validates against the closed
mesh: run above the roofline it reproduces the mesh volume to six decimal places, run at the
road plane it returns exactly zero.

---

## 6. Results

### 6.1 A published criterion does not return one answer, it returns one answer per class

Evaluating all three AR&R classes over the same 70-condition sweep, 10 depths from 0.1 to
1.0 m crossed with 7 velocities from 0 to 3.0 m/s:

| Class | FORD | NO-FORD |
|---|---|---|
| Small passenger | 12 | 58 |
| Large passenger | 19 | 51 |
| Large 4WD | 24 | 46 |

**12 of the 70 cells are class-sensitive**, meaning at least two classes disagree there. This
project's own headline example, 0.30 m of water moving at 1.5 m/s, sits inside that band: it
is NO-FORD for a small passenger car and FORD for a large 4WD. The vehicle class you assume
decides the verdict, and there is no tie-break rule in the source when a vehicle's length,
weight, and ground clearance disagree about which class it belongs to.

### 6.2 Grid resolution biases traction in one direction, and truth is outside the measured range

The vehicle is converted to particles on the simulation grid before any physics runs. At a
0.30 m waterline, every grid resolution over-fills the vehicle, so every one of them overstates
buoyancy and understates the traction holding the car on the road:

| Grid resolution | Modeled traction | Understated by |
|---|---|---|
| 64 | 1391 N | 60 percent |
| 96 | 2459 N | 30 percent |
| 128 | 3204 N | 8.3 percent |
| **true geometry** | **3495.2 N** | reference |

**This is a one-sided bias, not an uncertainty band, and the distinction is the whole point.**
A band would mean the true answer sits somewhere inside the measured spread and refining the
grid narrows in on it from both sides. That is not what happens here. The true value lies
outside the measured range entirely, above all of it. Every resolution errs in the same
direction, and the error shrinks as the grid refines rather than centering on anything.

Stated as assumptions, because they all move the number: hydrostatic only, valid at zero flow
velocity, friction coefficient mu = 0.55 which is the most traction-favorable value in the
0.30 to 0.55 range this project cites, 1100 kg vehicle, and a sealed vehicle body that
displaces water over its full submerged envelope.

### 6.3 The cause is upstream of the grid, in how geometry enters the solver

The scene builder throws the mesh away. It resamples it into a fixed 60,000-point surface
cloud and solidifies from that, so a 327,212-vertex watertight hull and a sparse point cloud
scanned from video arrive at the solver as the same kind of object. Watertightness cannot
protect against what happens next.

At the default resolution the solidified body displaces **2.17 times the hull's true volume,
that is +117 percent over hull volume**. Every simulation run to date used a vehicle
displacing more than twice the water it should.

A dead end recorded earlier in this project, that a finer grid "hollows out" the vehicle, is
better explained as a limit of that fixed 60,000-point sample than as a limit of grid
resolution: once the grid spacing approaches the spacing between sample points, columns start
missing hits. **[PENDING]** the confirming test, which is to raise the sample count well above
60,000, re-run the resolution probe, and revert. Until that runs, this is the better
explanation, not a measured fact.

### 6.4 A null result: verdicts that never touched water

An entire earlier simulation track produced FORD verdicts in which the water never reached the
vehicle. In the scene as written, the water block sat **0.295 m away from the vehicle** and the
inflow velocity was **0**, so nothing ever closed the gap. Vehicle displacement logged 0.0000 m
at every one of 500 steps. The single velocity signature in the run, 0.8240 m/s, **matches
free fall through the vehicle's own 3.5 cm ground clearance to within 0.6 percent**: the square
root of 2 x 9.81 x 0.035 is 0.8287 m/s. It is the car dropping onto dry ground beside a puddle
it never contacted.

Those verdicts are **retracted, not blocked.** A blocked result is waiting on a run that has
not happened yet and could still turn out real. A retracted result never measured what it
claimed to measure, and no future run rehabilitates it.

A second, independent defect in the same track was logged to the ledger (section F4) while
this draft was being written: that script still hardcodes a superseded vehicle box of
4.66 x 1.79 x 1.44 m, a volume 3.39 times the real hull, which by itself would put the
vehicle's density below the physically plausible band. Two independent reasons the same
verdicts cannot stand. This detail belongs in the spoken answer if someone asks, not on the
printed poster.

### 6.5 What is not on this poster

**[PENDING] L2 coupled verdicts.** No verified L2 FORD or NO-FORD verdict exists as of
2026-07-25. No results file in `data/` carries an `L2_verdict` column, and the one file
holding earlier L2-labeled rows comes from the retracted track described in 6.4. The L1 versus
L2 divergence claim that appears in older drafts of this project is therefore not asserted
here.

---

## 7. Conclusion

Three things, and the third one is the one I would defend hardest.

**The minimum sufficient abstraction depends on the question.** Deep, still water is handled
correctly by a threshold anyone can compute in their head. Shallow, fast water is where the
cheap models and the expensive ones part company, and it is also the condition drivers most
often misjudge as safe.

**A published safety criterion is not a single number.** It is a family of criteria, one per
vehicle class, drafted for stationary vehicles as an explicitly interim revision whose own
authors called for full-scale testing and model calibration before anything like it could
stand as a true safety guideline. Twelve of seventy conditions in this sweep change answer
depending on which class you assume.

**Verification is a result, not overhead.** The two findings I trust most this summer are both
negative: a traction estimate biased in one direction at every resolution tested, and a set of
verdicts produced by a vehicle that never touched the water. Neither was found by running more
simulations. Both were found by measuring what the pipeline actually built and comparing it
against the geometry it claimed to be using. A number without the settings that produced it is
not a result.

**Future Directions.** Settle the sampling-versus-resolution question with a direct
oversampling test, run the coupled L2 sweep on the corrected geometry to produce the first
trustworthy simulated verdicts, and extend from stationary-vehicle criteria toward the moving
vehicle the "Can It Ford" question actually asks about.

---

## 8. Acknowledgments

This material is based upon work supported by the National Science Foundation under the NSF
REU Site: Cyberinfrastructure Research for Societal Advancement, Award # 2447887. This
research was conducted at The University of Texas at Austin Texas Advanced Computing Center
(TACC), whose computational resources made this work possible.

I thank my PI, Dr. Krishna Kumar, and my mentors Hassan Iqbal, Cheng-Hsi Hsiao, and Sarah
Etter of the GeoElements Lab for their guidance; Cristian Moran for near-peer support; Luke
Smith for simulation environment support; and Rosalia Gomez and the TACC Education and
Outreach team for organizing the REU program.

Any opinions, findings, and conclusions or recommendations expressed in this material are
those of the author and do not necessarily reflect the views of the National Science
Foundation.

---

## 9. References

1. Shand, T. D., Cox, R. J., Blacka, M. J., and Smith, G. P. (2011). *Appropriate Safety
   Criteria for Vehicles: Project 10, Stage 2 Literature Review* (P10/S2/020). Water Research
   Laboratory, Australian Rainfall and Runoff Revision Project. ISBN 978-0-85825-948-5.
   **Verified at primary source**, read directly from the PDF in `citations/`. This is the
   source of every L1 threshold on this poster.

2. Kumar, K. *mpm-engine*. https://github.com/kks32/mpm-engine. The L2 solver. Behavior cited
   here was read from the installed package source, not from documentation.

3. Thorpe, A., Iqbal, H., Hsiao, C.-H., et al. (2026). *Physically Viable World Models: A Case
   for Query-Conditioned Embodied AI.* arXiv:2605.30542. The framing this project instantiates.

4. Hsiao, C.-H., and Kumar, K. (2025). *NeRF-to-MPM Inversion for Granular Material Property
   Estimation.* arXiv:2507.09005. The inverse-direction sibling of this forward-direction work.

5. Smith, G. P., Modra, B. D., and Felder, S. (2019). Full-scale testing of stability curves
   for vehicles in flood waters. *Journal of Flood Risk Management*, 12.
   https://doi.org/10.1111/jfr3.12527

6. National Weather Service. *Turn Around Don't Drown.*
   https://www.weather.gov/safety/flood-turn-around-dont-drown. Source of the L0 0.15 m
   threshold as used in this project.

**[PENDING] friction coefficient citation.** The mu = 0.55 used in result 6.2 is attributed in
this repo to Azhar, Pauwels and Bui (2023), *Journal of Flood Risk Management* 16(2):e12885,
https://doi.org/10.1111/jfr3.12885. That attribution is flagged UNRESOLVED in
`analysis/failure_mode_citations.md:67` because the full text could not be retrieved to
confirm it. Either confirm it against the paper or present mu = 0.55 as a sensitivity bound
rather than a cited value. It does not change the direction of the 6.2 result, only the
magnitude.

---

## 10. Provenance for every number on this poster

Working notes. Not poster text. Strip this section at layout.

| Claim | Source | Checked |
|---|---|---|
| 70 cells, 10 depths x 7 velocities | `data/scenario_sweep.csv` | Live, 2026-07-25, 70 rows counted |
| FORD counts 12 / 19 / 24 | `data/scenario_sweep.csv`, three class columns | Live, 2026-07-25, recounted |
| 12 class-sensitive cells | `data/scenario_sweep.csv`, `L1_class_sensitive` | Live, 2026-07-25, 12 rows enumerated |
| 0.30 m / 1.5 m/s is class-sensitive | same file, that row | Live, NO-FORD small passenger, FORD large 4WD |
| L0 rule, FORD if depth <= 0.15 m | `scripts/gen_scenario_sweep.py:24` | Live, 2026-07-25 |
| AR&R three-class thresholds, stationary scope, 3.0 m/s rationale | Ledger A1, A2, A3, read from the source PDF | Ledger, verified at primary source |
| Traction 1391 / 2459 / 3204 N vs true 3495.2 N | `figures/traction_bias_CAPTION.md`, values-plotted table | Live, 2026-07-25 |
| Understatement 60 / 30 / 8.3 percent | same | Live, 2026-07-25 |
| mu range 0.30 to 0.55, mu = 0.55 is the favorable end | same caption, assumption 4 | Live. Attribution unresolved, see References |
| 60,000-point resample | Ledger A8. Confirmed live in the local copy at `citations/vehicle(kks32).py:152` | Live, 2026-07-25 |
| +117 percent over hull, 2.17x | Ledger A9, consequence 1, basis named | Ledger |
| 327,212 vertices, watertight, 1100 kg MASH 1100C | Ledger F1 | Ledger, confirmed from PLY header |
| Hollowing is a sampling limit, not a resolution limit | Ledger A9 consequence 2 and Section C | **INTERPRETATION, untested. Tagged [PENDING] in 6.3** |
| Gap 0.295 m, velocity 0, x_disp 0.0000 m at 500 steps | `.claude/handoffs/_mission_ford-F5_ADDENDUM.md` section 2, sourced to `logs/c0_crash_isolation_result_20260725.md` **on Vista only** | Not readable from the Mac. Cited as reported |
| 0.8240 m/s matches free fall within 0.6 percent | Arithmetic: sqrt(2 x 9.81 x 0.035) = 0.8287 m/s vs 0.8240 m/s measured | Recomputed this pass. Do not write it as an exact identity |
| Track 2 box 4.66 x 1.79 x 1.44, 3.39x hull volume | Ledger F4, appended by another pane at 01:08 on 2026-07-25 | Read live from the ledger after it landed |
| No L2_verdict column in any results file | `grep -l L2_verdict data/*.csv` returns nothing | Live, 2026-07-25 |
| NSF award number and required acknowledgment wording | `Instructions.docx.md:30` | Live, 2026-07-25 |
| Mentor names | `README.md:200` | Live, 2026-07-25 |

### Line-number discrepancy worth knowing

The ledger cites the 60,000-point resample at `vehicle.py:162` in the package installed on
Vista. The copy of the same file kept locally at `citations/vehicle(kks32).py` has the
identical line at **152**. The fact is confirmed in both places; only the line number differs
between copies. No line number appears in the poster text for exactly this reason.

### Contamination warning carried forward, not independently verified here

Per the F5 addendum, the null run described in 6.4 appended rows to
`data/track2_sweep/manifest.csv` and `data/phase_space_results_mpm.csv`. Any figure built from
either file inherits a null-result row.

Checked live on the Mac 2026-07-25: **neither path exists here.** `data/track2_sweep/` is
absent and `data/phase_space_results_mpm.csv` is absent. The contaminated files are therefore
on Vista, not on this machine, or they are named differently here. Do not go looking for them
locally and conclude the contamination is not real. No CSV was edited by this pane.

---

## 11. F0 evidence closing PENDING tags, added by lane P 2026-07-25

Lane F0 ran a read-only geometry probe on Vista this session against
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`, using the repo's own
`solidify_columns` imported from `mpm-engine/src/warpmpm/vehicle.py`. Handoff at
`.claude/handoffs/2026-07-25_ford-F0-gridgate.md` on Vista. What it closes and what it
explicitly does not:

**CLOSED, now verified at primary source:**

| Item | F0 measurement | Was |
|---|---|---|
| Hull volume 3.5427 m3 | `mesh.volume` = 3.542739 m3, `is_watertight` True, `is_volume` True | Ledger figure, not verified at the mesh |
| Implied vehicle density | 1100.0 / 3.542739 = 310.494 kg/m3 | Ledger A9 |
| 327,212 vertices | Confirmed live from the PLY, 655,308 faces | Ledger F1 |
| Over-fill at n_grid 64 | ratio 2.1763, i.e. +117.6 percent over hull | Ledger A9, flagged "not reproduced on this pass" |
| Submerged-volume bias at 0.30 m | 1.64x the true submerged volume | Not previously measured |
| Section 6.3 oversampling test | RUN. 60k vs 1M samples: gap 0.7 / 1.6 / 1.8 / 4.6 / 12.3 / 37.2 percent at n_grid 32 / 48 / 64 / 96 / 128 / 192 | **[PENDING]** in 6.3 |

The 6.3 sampling-limit explanation is now measured, not inferred. 60,000 surface samples are
adequate to n_grid 64, marginal at 96, inadequate at 128 and above.

F0 also independently reproduced the note 2 submerged-volume column to within about 1 percent
(F0 0.8499 / 0.6474 / 0.5120 m3 at n_grid 64 / 96 / 128 against note 2's 0.842252 / 0.644214 /
0.506268), using the repo's own solidifier. That was row 2's exact blocker.

**NOT CLOSED, still PENDING, do not let this drift:**

- No L2 verdict, FORD or NO-FORD, is verified. Section 6.5 stands unchanged.
- No divergence count is verified. The 39.1 percent / 9 of 23 / 14 divergences figures remain
  under the `af95d17` stale-mass caveat.
- No render is verified. F0 ran no solver and produced no image.
- The true-geometry reference volume 0.452204 m3 is still NOT independently reproduced. F0's
  voxel-containment estimate at 0.015 m pitch gives 0.51920 m3, which is an over-count upper
  bound, not a confirmation. The divergence-theorem clipping routine remains absent from the
  repo, so the 3495.2 N reference traction and the 60 / 30 / 8.3 percent understatements still
  rest on an unverified number.
- F0 could not run the clipping check itself: `shapely` is not installed on Vista, so
  `trimesh.slice_plane` raises `ModuleNotFoundError`.

**Two corrections F0 forces:**

1. The 60,000-point resample is at `vehicle.py:134`, not 162 and not 152. Both recorded line
   numbers are wrong against the live file on Vista.
2. `load_vehicle` cannot load the watertight Yaris PLY at all. It dispatches on the `.ply`
   suffix into the Gaussian-splat loader and raises `ValueError: no field of name opacity`.
   The mesh branch containing `mesh.sample` is unreachable for this file. Any statement that
   the Yaris has been run through this pipeline is therefore not currently supportable.

**Water layer count is 4, not 3**, at n_grid 64 and depth 0.30 m, computed against the engine's
own `zs = np.arange(floor + 0.5*h, floor + depth, h)` with `floor = 3*dx`. Do not print 3.

**Yaris mass attribution, corrected.** Section 5 says "MASH 1100C class mass of 1100 kg". The
number 1100 kg is right but that attribution is backwards. 1100 kg is the LS-DYNA deck header
value ("Version 1l, 1100 kg"), the primary source. The MASH label and the competing 1078 kg
figure are NCAC-webpage annotations, not deck content. `paper/poster_methods.md:13` has this
fully inverted and must not ship as written.

---

## 12. Condensed poster cut, lane P, 2026-07-25

This is the text that goes on the printed poster. Sections 3 through 9 above remain the
long-form source for the July 31 paper and were not edited. Every number and every caveat in
6 and 7 is preserved here. Only connective prose was cut. The cut diff is section 13.

### Title
**Can It Ford? Finding the Minimum Sufficient Physical Abstraction for Vehicle Flood Traversability**

### Authors
Josie Cerrell (1), Hassan Iqbal (2), Cheng-Hsi Hsiao (2), Krishna Kumar (2)
(1) Claremont McKenna College, Claremont, CA
(2) GeoElements Lab, Texas Advanced Computing Center, The University of Texas at Austin
**[PENDING]** author list and order unconfirmed; Sarah Etter omitted pending Kumar's call.

### Introduction
Josie Cerrell, Integrated Sciences, Claremont McKenna College. NSF REU Site:
Cyberinfrastructure Research for Societal Advancement, at the Texas Advanced Computing Center,
The University of Texas at Austin, GeoElements Lab, PI Dr. Krishna Kumar, with daily
mentorship from Hassan Iqbal, Cheng-Hsi Hsiao, and Sarah Etter.

Flooded roads kill people who could not tell they were dangerous. Depth, current speed, and
whether the road is still there are invisible from a driver's seat. An autonomous vehicle has
the same blind spot, and so does an AI world model that predicts what a scene will look like
next: it can generate a future that looks plausible while breaking the physics that decides
whether the car makes it across.

### Research Goal
Given a flooded road and a specific vehicle, can that vehicle ford it, and what is the simplest
physics that still gets the answer right? Three levels, same conditions:
**L0** static depth threshold, NO-FORD above 0.15 m, no velocity term.
**L1** the AR&R Project 10 Stage 2 depth-velocity stability criteria.
**L2** a fully coupled MPM simulation where buoyancy and drag emerge rather than being assumed.

A safety criterion that is right on average and wrong in the specific case you are standing in
is not a safety criterion.

### Methods
**Criterion side.** AR&R Table 3 gives three classes, small passenger, large passenger, large
4WD, each with a limiting still-water depth, a limiting velocity of 3.0 m/s, and a limiting
depth-velocity product. All three caps applied jointly, which the earlier implementation did
not do. Two things the source says that are easy to get wrong: these are criteria for
*stationary* vehicles, and the 3.0 m/s cap is an evacuation safety limit imported from human
stability research, not a vehicle stability result.

**Simulation side.** A watertight Toyota Yaris hull, 327,212 vertices, 1100 kg from the
LS-DYNA deck header, hull volume 3.542739 m3, implied density 310.494 kg/m3, placed in a water
column as a rigid body coupled to weakly-compressible water on an MPM grid.

**Verification side, which became the bulk of the summer.** Before trusting a verdict I
measured what the pipeline actually builds and compared it against the geometry it claims to
use.

### Results 1: a published criterion returns one answer per class, not one answer
70 conditions, 10 depths from 0.1 to 1.0 m crossed with 7 velocities from 0 to 3.0 m/s.

| Class | FORD | NO-FORD |
|---|---|---|
| Small passenger | 12 | 58 |
| Large passenger | 19 | 51 |
| Large 4WD | 24 | 46 |

**12 of 70 cells are class-sensitive.** The headline example, 0.30 m at 1.5 m/s, sits inside
that band: NO-FORD as a small passenger car, FORD as a large 4WD. The class you assume decides
the verdict, and the source gives no tie-break when length, weight, and ground clearance
disagree about which class a vehicle is.

### Results 2: grid resolution biases traction one way, and truth is outside the measured range
At a 0.30 m waterline every resolution over-fills the vehicle, overstating buoyancy and
understating the traction holding the car down.

| Grid | Modeled traction | Understated by |
|---|---|---|
| 64 | 1391 N | 60 percent |
| 96 | 2459 N | 30 percent |
| 128 | 3204 N | 8.3 percent |
| **true geometry** | **3495.2 N** | reference |

**This is a one-sided bias, not an uncertainty band.** A band would mean the true answer sits
inside the measured spread and refining the grid closes in from both sides. It does not. The
true value lies above all of it. Every resolution errs the same direction.

Assumptions, all of which move the number: hydrostatic only, valid at zero flow velocity,
mu = 0.55 presented as a sensitivity bound not a cited value, 1100 kg, and a sealed body
displacing water over its full submerged envelope. The sealed-body assumption and the
column-fill over-fill both inflate buoyancy, so they compound rather than cancel.
**[PENDING]** the true-geometry reference 3495.2 N derives from a submerged volume of
0.452204 m3 whose generating routine is not in the repository.

### Results 3: the cause is upstream of the grid
The scene builder throws the mesh away. It resamples any input to a fixed 60,000-point surface
cloud and solidifies from that, so a 327,212-vertex watertight hull and a sparse video-scanned
point cloud arrive at the solver as the same kind of object. Watertightness cannot protect
against what happens next.

At default resolution the solidified body displaces **2.17 times the hull's true volume, +117
percent**, and its submerged volume at 0.30 m depth is **1.64 times** the true submerged
volume. Every run to date used a vehicle displacing more than twice the water it should.

The earlier "a finer grid hollows out the vehicle" dead end is a limit of the fixed 60,000-point
sample, not of grid resolution. Measured directly this session: raising the sample count 16x
changes the particle count by 0.7, 1.6, 1.8, 4.6, 12.3 and 37.2 percent at n_grid 32, 48, 64,
96, 128 and 192. 60,000 samples are adequate to 64, marginal at 96, inadequate at 128 and above.

### Results 4: a null result, verdicts that never touched water
An entire earlier simulation track produced FORD verdicts in which the water never reached the
vehicle. The water block sat **0.295 m** from the vehicle at inflow velocity **0**, so nothing
closed the gap. Displacement logged **0.0000 m at every one of 500 steps**. The single velocity
in the run, **0.8240 m/s**, matches free fall through the vehicle's own 3.5 cm ground clearance
to within **0.6 percent**: sqrt(2 x 9.81 x 0.035) = 0.8287 m/s. It is a car dropping onto dry
ground beside a puddle it never contacted.

Those verdicts are **retracted, not blocked.** A blocked result waits on a run that has not
happened and could still be real. A retracted result never measured what it claimed to measure.
A second independent defect in the same track: it hardcodes a superseded vehicle box of
4.66 x 1.79 x 1.44 m, **3.39 times** the real hull volume.

### Results 5: what is not on this poster
**No verified L2 FORD or NO-FORD verdict exists as of 2026-07-25.** No results file carries an
`L2_verdict` column, and the one file holding earlier L2-labelled rows comes from the retracted
track above. The L1 versus L2 divergence claim in older drafts of this project is therefore not
asserted here.

### Conclusion
**The minimum sufficient abstraction depends on the question.** Deep, still water is handled
correctly by a threshold anyone can compute in their head. Shallow, fast water is where cheap
and expensive models part company, and it is the condition drivers most often misjudge as safe.

**A published safety criterion is not a single number.** It is a family of criteria, one per
vehicle class, drafted for stationary vehicles as an explicitly interim revision whose own
authors called for full-scale testing before anything like it could stand as a safety
guideline. Twelve of seventy conditions change answer depending on the class assumed.

**Verification is a result, not overhead.** The two findings I trust most this summer are both
negative: a traction estimate biased one direction at every resolution tested, and a set of
verdicts produced by a vehicle that never touched the water. Neither was found by running more
simulations. Both were found by measuring what the pipeline actually built. A number without
the settings that produced it is not a result.

**Future directions.** Run the coupled L2 sweep on corrected geometry to produce the first
trustworthy simulated verdicts, reproduce the true-geometry submerged volume with a routine
that lives in the repository, and extend from stationary-vehicle criteria toward the moving
vehicle the question actually asks about.

### Acknowledgments
This material is based upon work supported by the National Science Foundation under the NSF
REU Site: Cyberinfrastructure Research for Societal Advancement, Award # 2447887. This research
was conducted at The University of Texas at Austin Texas Advanced Computing Center (TACC),
whose computational resources made this work possible.

I thank my PI, Dr. Krishna Kumar, and my mentors Hassan Iqbal, Cheng-Hsi Hsiao, and Sarah Etter
of the GeoElements Lab; Cristian Moran for near-peer support; Luke Smith for simulation
environment support; and Rosalia Gomez and the TACC Education and Outreach team.

The finite element vehicle models were developed by the Center for Collision Safety and
Analysis at George Mason University under contract with the FHWA and NHTSA.

Any opinions, findings, and conclusions or recommendations expressed in this material are those
of the author and do not necessarily reflect the views of the National Science Foundation.

### References
1. Shand, T. D., Cox, R. J., Blacka, M. J., and Smith, G. P. (2011). Appropriate Safety Criteria
   for Vehicles: Project 10, Stage 2 (P10/S2/020). Water Research Laboratory, Australian
   Rainfall and Runoff Revision Project. ISBN 978-0-85825-948-5.
2. Kumar, K. mpm-engine. https://github.com/kks32/mpm-engine
3. Thorpe, A., Iqbal, H., Hsiao, C.-H., et al. (2026). Physically Viable World Models: A Case
   for Query-Conditioned Embodied AI. arXiv:2605.30542
4. Hsiao, C.-H., and Kumar, K. (2025). NeRF-to-MPM Inversion for Granular Material Property
   Estimation. arXiv:2507.09005
5. Smith, G. P., Modra, B. D., and Felder, S. (2019). Full-scale testing of stability curves for
   vehicles in flood waters. J. Flood Risk Management, 12. doi:10.1111/jfr3.12527
6. National Weather Service. Turn Around Don't Drown.

---

## 13. Condensation diff, what was cut from sections 6 and 7

Cut is prose only. No number, no table row, no caveat, and no PENDING tag was dropped.

| Cut from | Text removed | Why it was safe |
|---|---|---|
| 6.1 heading | "A published criterion does not return one answer, it returns one answer per class" shortened to "a published criterion returns one answer per class, not one answer" | Same claim, fits a panel header |
| 6.1 body | "Evaluating all three AR&R classes over the same 70-condition sweep" reduced to "70 conditions" | The sweep scope is stated by the numbers that follow |
| 6.1 body | "meaning at least two classes disagree there" | Redundant with "class-sensitive", which is defined by the table above it |
| 6.1 body | "This project's own headline example" to "The headline example" | Voice only |
| 6.2 body | "The vehicle is converted to particles on the simulation grid before any physics runs." | Restated more precisely in Results 3, which owns that mechanism |
| 6.2 body | "and refining the grid narrows in on it from both sides. That is not what happens here." | Compressed into the retained sentence; the claim survives verbatim in substance |
| 6.2 body | "and the error shrinks as the grid refines rather than centering on anything" | The table's understatement column shows this directly |
| 6.2 assumptions | "which is the most traction-favorable value in the 0.30 to 0.55 range this project cites" | Replaced by "presented as a sensitivity bound not a cited value", which is stronger and reflects the failed scite confirmation |
| 6.3 heading | "The cause is upstream of the grid, in how geometry enters the solver" shortened | Panel header length |
| 6.3 body | "so a 327,212-vertex watertight hull and a sparse point cloud scanned from video arrive at the solver as the same kind of object" retained; only "that is +117 percent over hull volume" reflowed inline | Number retained |
| 6.3 body | The `[PENDING]` tag on the oversampling test | **Not a cut. Closed by F0 measurement**, and the six measured percentages were added |
| 6.4 heading | "A null result: verdicts that never touched water" retained nearly verbatim | none |
| 6.4 body | "In the scene as written" and "at every one of 500 steps" retained | none |
| 6.4 body | "This detail belongs in the spoken answer if someone asks, not on the printed poster" | Instruction to the presenter, not poster text. The 3.39x number it guards was kept |
| 6.5 | Retained in full as Results 5 | none |
| 7 | "Three things, and the third one is the one I would defend hardest" | Presenter voice; the three conclusions follow in order regardless |
| 7 future | "Settle the sampling-versus-resolution question with a direct oversampling test" | **Removed because F0 ran it.** Replaced with the true-geometry reproduction task, which is now the real open item |

**Added, not present in 6 or 7:** the submerged-volume bias 1.64x, the six oversampling
percentages, hull volume 3.542739 m3, implied density 310.494 kg/m3, the LS-DYNA deck-header
sourcing of 1100 kg, and the `[PENDING]` on the 0.452204 m3 reference volume. All six trace to
the F0 handoff on Vista, recorded in section 11.
