# R9 d17-moving: a load surface in v_car and v_water, pre-registration

Slot `d17-moving`, branch `claude/r9-moving-vehicle`, 2026-08-19.

**THIS SECTION IS THE PRE-REGISTRATION AND IT WAS COMMITTED BEFORE THE FIRST GPU
RUN.** Everything below the pre-registration line is written after the fact and
says so. If a criterion here was changed later, the change is recorded as a
change, not silently applied.

---

## 0. What is being measured, and what cannot be concluded

A Yaris hull is held as a prescribed signed-distance-field collider in a flooded
roadway, and the reaction wrench is measured as a function of two speeds that the
literature usually merges:

- `v_car`, the vehicle's speed over the ground, along its own long axis (+y);
- `v_water`, the flow speed across the roadway, broadside to the vehicle (+x).

Both are reported in the ground frame, alongside the relative-velocity **vector**
`v_rel = (v_water, -v_car, 0)`, its magnitude, and its angle from broadside.

**The body is PRESCRIBED, not free.** It cannot be swept away, because being
swept away is the degree of freedom the scene removes. No FORD or NO-FORD verdict
is reportable from any run in this document. That verdict belongs to the
AR&R-validated stationary-vehicle criterion, which is a different question with a
different validation basis.

The reason the body is prescribed is not convenience. `RigidBody6DOF` raises
`NotImplementedError` on a non-zero COM offset, because the SDF collider rotates
about its centre and `sdf_wrench` reports torque about that same centre, while
the Yaris particle-cloud CG sits 0.6312 m up against a bbox mid-height of
0.7427 m. Prescribing motion and measuring the wrench sidesteps that blocker
instead of pretending it is solved.

Every torque in the output is named `torque_about_collider_centre_Nm` so it can
never be read as a torque about the CG.

## 1. Prior art this is positioned against

The contribution is **not** "a vehicle that moves". At least four published works
already simulate or test a moving or non-stationary vehicle in floodwater:

| DOI | what it is | year |
|---|---|---|
| `10.1051/matecconf/201820307003` | Shah et al, "Instability Criteria for Vehicles in Motion Exposed to Flood Risks", MATEC Web of Conferences | 2018 |
| `10.1111/jfr3.12657` | Shah et al, "Hydrodynamic effect on non-stationary vehicles at varying Froude numbers under subcritical flows on flat roadways", J Flood Risk Mgmt. **1:10 scale**, so a drive force needs x1000 for full scale | 2020 |
| `10.1111/jfr3.12828` | Al-Qadami et al, "A numerical approach to understand the responses of passenger vehicles moving through floodwaters", J Flood Risk Mgmt. **Numerical**, not experimental | 2022 |
| `10.1007/s11069-021-04949-6` | Al-Qadami et al, "Full-scale experimental investigations on the response of a **flooded** passenger vehicle under subcritical conditions", Natural Hazards 110(1) 325-348. **Experimental**, and its title does not announce vehicle speed as a swept variable | **2021** |
| `10.3390/su151713262` | Al-Qadami et al, "Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D CFD Modelling", Sustainability | 2023 |

**Three of these are Al-Qadami et al, in three different years, by three
different methods, and two of them have already been conflated once on this
project.** They are not interchangeable. In particular, "full-scale experimental
moving vehicle" describes no paper on this list: the full-scale experimental one
is 2021 and is about a flooded vehicle, and the moving one is 2022 and is
numerical.

All five DOIs were resolved against Crossref on 2026-08-19. **The titles are
verified against the resolved records; the claims attributed to them are NOT
verified against the paper texts and are marked unverified wherever used.**
Verifying a title against a resolved DOI is not the same as verifying that the
paper says what someone said it says.

~~`analysis/research_index.py --query "Al-Qadami"` returns **zero** matches, so
none of these is in the 332-paper corpus index.~~

> **RETRACTED 2026-08-19, and this was my error, not the tool's.** The query does
> return zero. **The inference from it was invalid.** `research_index.py:518-521`
> matches the query substring against `title` and `abstract` ONLY; it never reads
> the authors field. An author query is therefore structurally incapable of
> matching, and zero was guaranteed before any paper was consulted.
>
> Re-checked by DOI, which is the field the index actually joins on. **Four of
> the five papers above ARE in the corpus:** `10.1007/s11069-021-04949-6`,
> `10.1111/jfr3.12828`, `10.3390/su151713262` and `10.1111/jfr3.12657` each
> return 1 match. Only `10.1051/matecconf/201820307003` is absent (as is
> Pregnolato et al `10.1016/j.trd.2017.06.020`).
>
> So the corpus is **not** silent on this topic, the prior art was available, and
> nothing here may claim otherwise. The novelty statement stands only on the
> SURFACE, which is what the measurements below support.
>
> This is the same failure mode as the two defects in R0 and the analysis bug in
> R9c: **a check that could not have returned any other answer.** I ran the query,
> got zero, and reported it as evidence. The correct move was to ask what the
> query searches before believing what it returned.

**The contribution claimed here is the SURFACE**: `v_car` crossed with `v_water`
as separate variables producing a graded load, where the field publishes
thresholds and single points. That framing survives contact with all five papers
above; "a vehicle that moves" would not.

## 2. The frame, and the assumption it rests on

Solved in the **vehicle rest frame**: the hull sits at the domain centre and the
water arrives at `u_free = (v_water, -v_car, 0)`.

**Why, and it is arithmetic.** The grid is forced cubic (`GridConfig` takes one
scalar) and the domain rule sizes it from the hull,
`lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth) = 9.4217 m` for the Yaris.
Usable ground-frame travel is `lim - 2*pad - ext_long = 4.256 m`, so:

| v_car (m/s) | 2.2 | 4.5 | 6.7 | 8.9 |
|---|---|---|---|---|
| frames of travel at 30 fps | 58.0 | 28.4 | 19.1 | **14.3** |

Against which the exploratory driver's own finding is that traces in this scene
family "never reach a steady value within 150 frames". So the ground frame is
infeasible above walking pace, and the grid being cubic means y cannot be
lengthened without wrecking the depth resolution.

> **CORRECTION.** This slot's scope confirmation stated 7.4 frames at 8.9 m/s.
> That was wrong by a factor of two: it halved the usable run, as though the hull
> started at the domain centre rather than at one end. The correct figure is 14.3.
> The conclusion is unchanged, since 14 frames is still not a steady measurement,
> but the published number was wrong. It was caught by self-test group ST11,
> which is the reason that assertion exists.

**THE ASSUMPTION, labelled and reversible:** a horizontal frame change leaves the
load unchanged. This is **exact for a slip bed**, because a plane exerting no
tangential stress is the same plane in any frame sliding parallel to it. It is
**false for a frictional bed**, where the roadway would have to move at `-v_car`
in this frame and does not. This scene uses a slip floor, so the assumption is
self-consistent here. It does **not** transfer to the canonical scene, whose
floor carries friction 0.55.

The assumption is not taken on trust: criterion **C4** below tests it.

**The frame choice does not collapse the matrix.** `v_car` and `v_water` are on
perpendicular axes, so each pair is a distinct free-stream vector whose magnitude
and direction both move.

## 3. Pre-registered matrix

Run in this priority order, because the node is time-boxed and the arc is the
falsifiable claim while the matrix is the surface.

**A. No-forcing control.** `(v_car, v_water) = (0, 0)`, n = 3 repeats.

**B. Iso-|v_rel| arc.** `|v_rel| = 3.0 m/s` held exactly, angle swept in 5 steps
from pure broadside to pure axial:

| cell | v_car | v_water | angle from broadside |
|---|---|---|---|
| A0 | 0.000 | 3.000 | 0 deg |
| A1 | 1.148 | 2.772 | 22.5 deg |
| A2 | 2.121 | 2.121 | 45 deg |
| A3 | 2.772 | 1.148 | 67.5 deg |
| A4 | 3.000 | 0.000 | 90 deg |

**C. Full matrix.** `v_car` in {0, 2.2, 4.5, 6.7, 8.9} m/s (0, 5, 10, 15, 20 mph)
crossed with `v_water` in {0.5, 1.0, 2.0, 3.0} m/s. 20 cells.

**D. Resolution rung.** The arc repeated at a second `n_grid`.

**E. Frame control.** `--ground-frame` at `v_car = 2.2`, the one speed where the
ground frame is feasible (58 frames), against the rest-frame cell at the same
`v_rel`.

Fixed across everything: depth 0.30 m, 30 settle frames, 60 measured frames of
which the first 20 are discarded, `n_grid` 64 unless stated, seed 0.

## 4. Pre-registered pass criteria

**C1, no-forcing control (a gate).** At `(0, 0)` the mean horizontal force must
satisfy `|F_horiz| / (rho*g*V_sub) < 0.05`. A driver that produces a horizontal
load with no flow and no motion is not measuring flow. **If C1 fails, nothing
else in this document is reportable.**

**C2, the iso-|v_rel| test (the result, either way).** Across arc cells A0 to A4,
let `S = (max|F_horiz| - min|F_horiz|) / mean|F_horiz|`.

- `S < 0.10`: the load is a function of `|v_rel|` alone to within 10 percent, and
  the field's practice of collapsing the two speeds is **defensible**. That is a
  publishable negative and it is reported as such.
- `S >= 0.10`: the split matters, and `S` is the size of what a scalar treatment
  omits. That is the positive result.

Registered in advance precisely so neither outcome can be presented as the one
that was expected.

**C3, resolution stability (a qualifier, not a gate).** `S` recomputed at the
second grid. If `S` changes sign of conclusion between grids, C2 is reported as
unresolved rather than as either outcome.

**C4, the frame assumption (a qualifier).** Ground-frame vs rest-frame at
`v_car = 2.2`. Agreement in `|F_horiz|` within 15 percent supports the frame
change; a larger gap bounds the error the rest frame introduces and is reported
with the surface rather than buried.

**NOT a criterion: absolute force accuracy.** Deliberately excluded.
`docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md` section 5 established for
this same scene family that the validated C1-SDF buoyancy regime runs at
`depth_cells = 18` while a 0.30 m column in a hull-sized domain gets 1.4 to 3.7,
and concluded "no force number from this scene is quotable". Re-derived for the
Yaris: **g64 gives 2.04 depth cells, g96 gives 3.06, against a validated 18.**

That finding is accepted, not re-litigated. So `fz_settle_over_analytic` is
recorded every run as a **diagnostic** and is expected to be poor. Every reported
result is a **difference at fixed resolution**, never an absolute. The dispatch
for this slot proposed "the wrench at v_car = 0 must reproduce the canonical
stationary case's order of magnitude" as a gate; on the evidence above that test
is predicted to fail for reasons that are not about this driver, so it is
demoted to a diagnostic. That demotion is recorded here, before the run, rather
than after seeing the number.

## 5. The five traps, and where each is handled

Verified live against `core/solver.py` on Vista, 2026-08-19, warp 1.15.0.

| # | trap | source | handled |
|---|---|---|---|
| 1 | `sdf_wrench` divides by whatever dt it is handed | `:354-361`, body is `force: f / dt` | `step_frame` passes the tick duration; self-test ST1 excises its own body and asserts the driver's call site |
| 2 | the engine never zeroes `param.force` on the SDF path | `reset_sdf_force` is a separate method at `:348` | reset at the top of every tick, exactly one reset per wrench read; ST2 |
| 3 | quaternion order differs within one file | `add_sdf_collider :324` xyzw vs `add_cup :256` wxyz | identity written explicitly as xyzw at the call site, hull never rotated |
| 4 | COM offset is a hard blocker | `RigidBody6DOF` raises on non-zero offset | avoided by construction: the body is prescribed and never integrated; torque explicitly labelled about the collider centre |
| 5 | `periodic_x` has no guard on the SDF path | `add_cdf_collider` raises at `:379`, `add_sdf_collider` at `:324` does not | never set; streamwise wrap done host-side; ST3 |

## 6. What is reused rather than rebuilt

- `simulation/moving_vehicle_sdf_exploratory.py` (commit `187d868`): the vetted
  loader, `canonicalize()`, `build_hull_sdf()` with its winding-number chunk, and
  `sdf_nearest()`. That driver already handled traps 1, 2 and 3 correctly and
  there was no reason to re-derive them.
- `simulation/openchannel_bc.py`: `RecyclingChannelBC`, implementing Zhao,
  Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179, 27-33,
  `10.1016/j.compfluid.2018.10.007`. That is the correct citation for MPM
  in/outflow, **not** Kumar.
- `AxisRecycler` in this slot's own file generalises it to either horizontal axis
  and a signed free stream, as a subclass, because `openchannel_bc.py` is outside
  this slot's write scope. The inherited part is the safety-critical part: the
  P2G edge guard, the sub-cell overshoot carry, and the modulo that stops a
  particle recycling forever inside one tick.
- `ReservePool` is **not** used. It has a known row-collision defect that
  silently corrupts CG and inertia and presents as physics, and that defect is
  one of the items awaiting Josie's decision.

## 7. Self-test, run before any GPU time

`python3 simulation/moving_vehicle_channel.py --selftest`, 11 groups, pure numpy,
no GPU. It covers the three source-scannable traps, the domain rule, the arc
construction, both recycler flow directions including the negative one the parent
class cannot express, the zero-stream no-op that makes C1 a clean control, the
inherited P2G guard, the floor clamp, and the ground-frame feasibility arithmetic.

Two defects were caught by it before any GPU run:

1. **The first version of ST1 failed on its own assertion string.** It scanned
   the whole file for a bad call pattern, and the needle is itself source text of
   the file being scanned. Had the polarity been reversed, the check would have
   **passed on its own text while the driver was wrong**. That is the
   laundered-check failure mode slot `d9-kramer` recorded tonight: a correct test
   pointed at the wrong quantity looks like rigour. ST1 now excises the
   self-test's own body before asserting anything about the driver.
2. **ST11 caught the factor-of-two travel error** described in section 2.

---

# RESULTS

Written after the runs. Everything above this line was committed as `d3e52fd`
before the first GPU run and is unedited. Every number below is regenerated by
`python3 analysis/r9_speed_surface.py --dir out/r9_moving`.

Platform: Vista `c642-071`, GH200, warp 1.15.0, idev job 920452, 2026-08-19.
SDF resolution 32, cell 0.225401 m.

**WHERE THE RECORDS ARE.** `out/` is gitignored (`.gitignore:92`), so the per-run
JSON is NOT in this repo. It lives on Vista at
`/work/11603/jcerrell0629/vista/r9_moving/out/r9_moving/`, with the two superseded
generations preserved beside it as `out/r9_moving_STALLED_v1` (before the inflow
slab) and `out/r9_moving_BUGGED_v2` (before the recycle planes were moved clear of
the wall band), so the two defects in R0 can be re-derived rather than taken on
trust. A local copy sits in this worktree's untracked `out/r9_moving/`. Whether
any of it should be promoted into tracked `data/` is a decision for the
coordinator; this slot's declared write scope does not include `data/`.

> **THE SDF RESOLUTION WAS CHOSEN BY WALL-CLOCK AND CACHE AVAILABILITY, NOT BY A
> CONVERGENCE ARGUMENT.** This is a labelled, reversible assumption. The hull has
> 655,308 faces, 9x the hull the exploratory driver timed, and the SDF builder is
> a numpy generalized-winding-number pass costing `n_points x n_faces`. res 64
> would be a multi-hour build. A res-32 SDF of exactly this hull already existed
> in the cache at `margin_cells = 6.0`, confirmed by computing `_hashkey` for
> this mesh across res 16 to 96 and matching `sdf_1e4c605e77fd6fa2`. So res 32
> was free and res 64 was unaffordable. A coarse SDF that completes the matrix
> beats a fine one that yields three cells and no surface, but the choice is not
> a convergence claim and must not be reported as one.

## R0. Two defects were found and fixed before any result was believed

Both were found by controls, not by inspection, and the first one had already
produced a clean-looking arc that was entirely an artifact.

### R0a. The forcing stalled, and the first arc measured the stall

The first driver forced the flow with a one-shot additive kick and left the
recyclers to maintain it. A recycler only re-imposes the free stream on particles
that actually cross the outflow plane, so it is not forcing at all: it does
nothing once the flow stops.

Measured, g64 arc, 60 frames: pure broadside at 3.0 m/s recycled **34** of 48,746
water particles where the travel distance implies roughly 33,000, while pure
axial at the same speed recycled **34,414**. The upstream inflow slab drained to
0.01 percent of the pool against 10 percent elsewhere, and the mean water
velocity in x was **-0.325 m/s against a commanded +3.0**.

Fixed by adding `InflowSlab`, a per-tick Dirichlet clamp on an upstream slab,
which is `sim_standing.py`'s own mechanism (:190-198, called every frame at :202)
rather than something invented here.

### R0b. The recycle planes sat inside the domain-wall kill band

The stall survived the fix in one direction. My first explanation was physical:
the hull blocks about 54 percent of the broadside path against 24 percent of the
axial one, so I proposed that broadside flow was choking.

**That explanation was wrong, and the control that refuted it is the most useful
thing in this document.** A `--no-hull` run, identical domain and water and
forcing with the vehicle removed, gave `stream_established_frac` **-0.187** for
broadside against **+0.997** for axial. Removing the vehicle made broadside
*worse*. A blockage explanation cannot survive that.

A 2x2 of axis against sign, no hull, |u| = 3.0 m/s, isolated it in four runs:

| commanded | +x | -x | +y | -y |
|---|---|---|---|---|
| `stream_established_frac` | **-0.187** | +0.997 | **-0.188** | +0.997 |

Negative flow worked perfectly on both axes; positive flow failed identically on
both. One sign bug, not an axis bug and not the vehicle.

**Cause, read from source:** `Solver.add_domain_walls` "zero[es] outward velocity
in a three-cell band at each domain face" (`solver.py:315-322`). The recycle
planes were at exactly `3 dx` and `lim - 3 dx`, the band edge, so a particle
driven outward had its outward velocity zeroed exactly where the plane sat and
never crossed it. It failed asymmetrically because the recycler tests
`s >= p_hi` one way and `s <= p_lo` the other, and against a wall that arrests
particles at the plane those two predicates do not behave alike.

**This is why it survived the unit tests.** ST6 and ST7 test both recycler
directions and both pass: the arithmetic was never wrong. The bug was in the
*geometry between two components*, which no single-component test could see.

Fixed by moving the planes to `5 dx`, leaving `2 dx` of clear interior. After the
fix the same 2x2 gives **0.967, 0.966, 0.966, 0.967**, spread 3e-4. ST13 now
asserts the plane-versus-band geometry, and `report_stream_health` refuses to
grade any cell whose stream did not establish.

## R1. C1, the no-forcing gate: PASS

| | |
|---|---|
| `\|F_horiz\|` | 50.50 N |
| `rho g V_sub` | 4468.6 N |
| ratio | **0.01130** against a pre-registered 0.05 |

## R2. C0, the trap-1 detector, shown to fire

Re-running the control with `--wrench-dt-mode substep`, deliberately committing
the trap, moves `fz_settle/analytic` from 2.0474 to 22.5218, a ratio of
**11.000003** against `substeps_effective = 11`.

The detector is not merely asserted to work: it was made to fire on demand. A
detector never observed to fire has not been tested.

## R3. C2, the iso-|v_rel| arc: THE SPLIT MATTERS

Five cells at `|v_rel| = 3.000 m/s` held exactly, angle swept broadside to axial.

| angle | v_car | v_water | `\|F_horiz\|` g64 | `\|F_horiz\|` g96 |
|---|---|---|---|---|
| 0 deg (broadside) | 0.000 | 3.000 | 4409.8 N | 5822.9 N |
| 22.5 deg | 1.148 | 2.772 | **6119.3 N** | **7529.1 N** |
| 45 deg | 2.121 | 2.121 | 5755.0 N | 6358.9 N |
| 67.5 deg | 2.772 | 1.148 | 3969.3 N | 4543.9 N |
| 90 deg (axial) | 3.000 | 0.000 | 2158.2 N | 2988.0 N |

**S = 0.8837 (g64) and 0.8334 (g96), against a pre-registered threshold of 0.10.**

Over five seeds at g64, **S = 0.8886, sd 0.0033, range 0.8837 to 0.8923**, with
per-cell relative standard deviations of 0.13 to 0.26 percent. The conclusion
sits roughly 240 standard deviations above the threshold.

So: **at identical relative-speed magnitude, the load varies by about 89 percent
depending on how that speed is split between the vehicle and the water.** A
scalar treatment of "relative speed" cannot represent this scene. Since the
threshold was fixed before the runs, this is the pre-registered positive outcome
and not a threshold chosen to fit.

**Two features worth separating from the headline.**

The **broadside-to-axial ratio is 2.043 (g64) and 1.949 (g96)**, against a
projected frontal-area ratio of 4.2826 / 1.7464 = 2.452. An effective drag
coefficient formed from the *realised* stream gives 1.243 broadside against 1.249
axial at g64, and 1.849 against 1.757 at g96. **At each grid the two orientations
return nearly the same Cd**, which is what a bluff body in a stream should do and
is a sanity check the pre-fix scene failed badly. So most of the directional
difference is projected frontal area, which is geometry rather than anything
subtle. That is the honest reading and it is less exciting than "the split
matters" alone.

The arc is **not monotone**: it peaks at 22.5 deg, above pure broadside, at both
grids. A yaw-angle peak in side load is a known bluff-body behaviour, but this
scene has 2 to 3 depth cells and I am not claiming it as a physical finding. It
is recorded because it reproduces across both grids and all five seeds.

## R4. C3, resolution: the CONCLUSION is stable, the ABSOLUTES are not

- S: 0.8837 (g64) against 0.8334 (g96). Same side of the threshold by a wide
  margin, so C3 passes and C2 is reported as a result rather than as unresolved.
- broadside/axial ratio: 2.043 against 1.949, a 4.6 percent change.
- **Cd_eff: 1.24 against 1.80, a 45 percent change.**

That contrast is the whole justification for the pre-registered decision to
report differences rather than absolutes, and it is now measured rather than
assumed. `fz_settle/analytic` is 2.0474 at g64, so the at-rest vertical reaction
is more than double the analytic buoyancy, exactly as
`MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md` section 5 predicted for 2 depth
cells. **No absolute force in this document is quotable.**

## R4b. C4, the frame assumption: FAILS its threshold, and the test is confounded

| arm | `\|F_horiz\|` | `fz_settle/analytic` |
|---|---|---|
| rest frame, hull static, water at (0, -2.2, 0) | 2692.8 N | 2.0474 |
| ground frame, hull really moving at +2.2 m/s | 1910.4 N | 1.6751 |

Gap **34.0 percent** of the mean, against a pre-registered 15 percent. **C4 does
not pass.** The Galilean frame change is therefore NOT supported at the level
required, and every number in R3 and R5 inherits that.

**But this test does not isolate the assumption, and saying so matters more than
the number.** Three things differ between the arms, not one:

1. **Hull placement.** The rest frame puts the hull at the domain centre; the
   ground frame must start it at one end so it has room to travel. The at-rest
   vertical reactions already differ, 2.0474 against 1.6751, and that is measured
   BEFORE either hull moves. So the two arms do not share a starting state.
2. **Developed stream against starting transient.** The rest frame measures a
   maintained free stream. The ground frame has no forcing at all, `u_free` is
   zero, and the hull ploughs into still water from rest. Those are different
   problems.
3. **Window length.** The ground frame gets 40 frames because 4.256 m of travel
   at 2.2 m/s is all there is, of which 25 are measured, against a scene the
   exploratory driver found is not steady within 150.

So 34 percent is an **upper bound on the frame error that also contains the
placement and transient confounds**, not a measurement of the frame error. A
clean test needs the hull at the same place and a developed stream in both arms,
and the cubic grid cannot give the ground frame a developed stream in 4.256 m.
That is a real limitation of the scene, not a scheduling problem, and it is the
single thing I would fix next.

## R5. The surface

`|F_horiz|` in N, g64, one seed. Rows are v_car, columns v_water, both m/s.

| v_car \ v_water | 0.50 | 1.00 | 2.00 | 3.00 |
|---|---|---|---|---|
| 0.00 | 349.0 | 1168.0 | 2934.7 | 4409.8 |
| 2.20 | 2031.1 | 2789.3 | 5562.6 | 8621.4 |
| 4.50 | 3811.1 | 5845.6 | 12191.8 | 15999.0 |
| 6.70 | 5320.7 | 8653.7 | 20731.0 | 29998.2 |
| 8.90 | 7469.3 | 11934.6 | 27114.0 | 42221.0 |

All 20 cells established their free stream (minimum 0.666). The load rises
monotonically in both variables, and the two variables are **not
interchangeable**: compare (v_car 2.20, v_water 3.00) at 8621 N with
(v_car 4.50, v_water 0.50) at 3811 N, whose `|v_rel|` are 3.720 and 4.528 m/s.
**The cell with the LOWER relative speed carries 2.3x the load.** That single
comparison is the contribution stated as a number.

## R6. What was NOT done, and is not claimed

- **C4 ran and FAILED**, see R4b. The frame assumption is not supported at the
  15 percent level; the measured gap is 34 percent and is confounded by hull
  placement and by the ground frame having no developed stream. The surface in R5
  is reported WITH that caveat, not as if the frame change were free.
- The 22.5 deg peak is recorded, not explained.
- Repeats at a **fixed** seed carry no information: three gave a relative spread
  of 4.7e-6, so the scene is effectively deterministic and the dispatch's
  expectation that fixed-config repeats would spread does not hold here. The
  five-seed sweep is the real distribution.
- No FORD or NO-FORD verdict. The body is prescribed and cannot be swept away.
- The claims attributed to the five cited papers are **not** verified against
  their texts, only their titles against Crossref records.
- `analysis/research_index.py --query "Al-Qadami"` returns zero and
  `--method moving-vehicle` returns no match, so the corpus is silent on this
  topic. No novelty claim here rests on that silence.

---

# RESULTS, SECOND SESSION (node 922255, c642-091, 2026-08-19)

The first session's results above are unchanged. This session tested the
headline against three things that could have destroyed it, and it survived all
three. It also found one more defect in my own analysis.

**Reused-code provenance, now pinned properly.** The exploratory driver was read
from the `orphan-rescue-token-rotate-d72f90` worktree, which **no longer exists**
as of this session. That is why a worktree path is a bad citation. The content is
durable in history and is cited by blob:

| file | blob | at commit |
|---|---|---|
| `simulation/moving_vehicle_sdf_exploratory.py` | `86ef1905...` (29,788 B) | `187d868` |
| `docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md` | `bb9c7c58...` | `187d868` |

**The `srun` form that works on Vista**, for any slot that needs it. All five are
required and the wrapper reveals the missing ones one at a time:

```
srun -p gh-dev -N 1 -n 1 -t 00:20:00 --overlap --jobid=<id> <cmd>
```

## R7. The frame problem, measured

**R7a. How far the ground frame would need to travel.** A 300-frame rest-frame
run at `|v_rel| = 2.2 m/s` reaches within 10 percent of its own final-40-frame
mean at frame 190, which is 6.333 s, i.e. **13.933 m of equivalent travel**.

The ground frame has **3.078 m**. It is short by a factor of **4.5**.

That is the negative with a number: the ground frame cannot develop in this
domain, and the cubic grid means lengthening the travel axis costs `n_grid^3`
while wrecking the depth resolution. This is a property of the scene, not a
scheduling problem.

**R7b. The frame gap across three speeds**, at each of which the ground frame is
at least nominally feasible:

| v_car | frames available | ground `\|F_h\|` | rest `\|F_h\|` | gap |
|---|---|---|---|---|
| 0.5 | 180 | 225.8 N | 581.1 N | 88.1 % |
| 1.0 | 90 | 745.7 N | 986.7 N | 27.8 % |
| 2.2 | 41 | 1911.5 N | 2678.3 N | 33.4 % |

**R7c. AND HERE IS WHY I WILL NOT CALL ANY OF THAT A FRAME DISCREPANCY.** I ran
the placement control: the rest frame, hull moved along y across the span the
ground-frame hull traverses, everything else identical.

| hull y (m) | 3.1718 | 3.9414 | 4.7109 | 5.4804 | 6.2499 |
|---|---|---|---|---|---|
| `\|F_h\|` (N) | 2190.6 | 2493.0 | 2678.2 | 3525.9 | 6611.9 |

**Spread 126.3 percent from placement alone**, which is four times the 33 percent
"frame gap" at the same speed. Restricted to the three positions clear of the
upstream inflow slab the spread is still ~20 percent; the blow-up at y = 6.2499
is the hull's leading end reaching into the Dirichlet slab, which is a second,
separate scene constraint worth recording: **the hull must be kept clear of the
inflow slab, and the auto-placement does not enforce it.**

So the honest statement is: **at this resolution the frame change cannot be
separated from hull placement, because placement alone moves the answer further
than the frame does.** 34 percent is an upper bound containing the placement
term, not a measurement of a frame effect, and I am not going to present it as
the first number on the moving-reference-frame problem. It is not clean enough to
be that. What IS defensible is R7a: the travel distance needed, against the
travel distance available, both measured.

## R8. The headline survives three attacks

**R8a. It is not a transient artifact.** The surface was measured over frames
20-60; the 300-frame run shows the load still falling there (the 41-frame rest
arm read 2678 N where the settled value is 673 N, a factor of 4). So I re-ran the
arc at 400 frames, 5 seeds, and computed S over five windows:

| window | f20-60 | f60-150 | f150-250 | f250-325 | f325-400 |
|---|---|---|---|---|---|
| S | 0.8886 | 1.0233 | 1.2053 | 1.1633 | 1.1879 |

**S exceeds the pre-registered 0.10 by more than an order of magnitude in every
window**, including the settled one, where residual drift per cell between the
last two windows is 0.4 to 3.8 percent. Per-seed at f250-400: S = 1.1776,
sd 0.0016 over 5 seeds.

**8b. It is not an artifact of non-uniform integration.** I found that
`bc_per_frame` was set per-cell from `u_max`, so the 45 deg cell got 1 host-BC
application per frame where the other four got 2, and simulated 13.333 s against
14.545 s. I predicted that was causing the arc's jagged shape. **I was wrong.**
Forcing `bc_per_frame = 2` uniformly moved that cell by 1.07 percent and every
other cell by under 0.01 percent, and S went 1.1755 to 1.1776. The
non-uniformity was real and is now fixed (`--bc-per-frame`), but it was not the
cause. The jagged shape is reproducible, seed-independent, and **unexplained**.

**8c. It survives a 23x change in mesh fidelity.** See R9 below.

**What does NOT survive: the shape of the arc.** In the transient window the peak
is at 22.5 deg; in the settled window it is at 67.5 deg. My first-session note
that "the 22.5 deg peak reproduces across both grids and all five seeds" was true
**within the transient window only** and is withdrawn as a general statement.
Report the spread; do not interpret the ordering.

## R9. Mesh fidelity, same vehicle, two meshes

Silverado hulls from `~/Downloads/vehicle_meshes/` (untracked, not previously on
Vista), same vehicle, 23x apart in vertex count:

| | coarse | fine |
|---|---|---|
| vertices / faces | 2,108 / 4,380 | 48,706 / 97,596 |
| `lim` (m) | 12.792386 | 13.095687 |
| `dx` (m) | 0.199881 | 0.204620 |
| depth cells | 1.501 | 1.466 |
| analytic buoyancy | 2529.5 N | 2476.0 N |

**R9a. The control is itself caught by the resolution trap.** `lim` derives from
the loaded hull's extent, and decimation shrinks the extent, so the same vehicle
at two fidelities gets a domain differing by **2.37 percent** and therefore a
different `dx`, a different realized depth in cells, and a different displaced
volume. A mesh-fidelity comparison at fixed `n_grid` is not at fixed resolution.
This is the documented cross-vehicle trap appearing **within a single vehicle
class**, which is sharper than the form it is usually stated in.

**R9b. The conclusion is fidelity-robust; individual cells are not.**

| v_car | coarse | fine | diff |
|---|---|---|---|
| 0.000 | 2527.0 N | 2575.1 N | +1.9 % |
| 1.148 | 4789.4 N | 4773.7 N | -0.3 % |
| 2.121 | 3304.1 N | 3183.2 N | -3.7 % |
| 2.772 | 4489.7 N | 6085.6 N | **+35.5 %** |
| 3.000 | 1492.4 N | 1587.2 N | +6.4 % |

**S(coarse) = 0.9929, S(fine) = 1.2355**, both an order of magnitude above the
threshold. Four of five cells agree within 6.4 percent; one moves 35.5 percent,
and it is the 67.5 deg cell, the same one that is the maximum in the settled
Yaris arc. So the spread survives fidelity and the shape does not, which is the
same split as R8.

**R9c. A THIRD DEFECT, THIS ONE IN MY OWN ANALYSIS, AND IT IS THE MOST INSTRUCTIVE
OF THE THREE.** While computing the per-seed distribution I called a spread
helper with a **dict** where it expected a sequence. Python reduced over the
KEYS. It returned 1.6591 for all five seeds with a standard deviation of exactly
0.0000, and 1.6591 is `(3.0 - 0.0) / mean(0, 1.148, 2.121, 2.772, 3.0)`: **the
spread of the sweep axis itself, computed without reading a single force.** It
sat next to a correct aggregate of 1.1776 and looked like a plausible result.

The sd of exactly zero is what exposed it. `spread()` now raises on a dict and
the self-test asserts that it does. Corrected per-seed values: 1.1766, 1.1762,
1.1782, 1.1771, 1.1801.

This is the third time in this slot that a check returned a number it could not
have derived from the data it claimed to measure: the self-test that passed on
its own source text, the corpus query that could not search authors, and now a
statistic that reduced over its own sweep axis. All three looked like results.

## R10. Vehicle class provenance, recorded and NOT acted on

Reported to me this session, from an Undermind deep search of 21 July:
the CCSA/NCAC LS-DYNA set with teardown provenance and NHTSA NCAP validation is
**Yaris, Camry, Silverado**, and there is **no Nissan Rogue** in it. The code's
`MASS` entries for Yaris (1100) and Silverado (2270) match the MASH designations;
`rogue` at 1571.3 has no such anchor. The same search reports as a negative that
no publicly redistributable OBJ/PLY/glTF/USD conversion of these models is
verified to exist, which makes this project's own `vehicle_mesh_pipeline.py` the
sole provenance for every `.ply` hull, and it is untracked.

**This is a SECONDARY-SOURCE claim and I have not verified any of it against a
primary record.** It is recorded because it bears on a class comparison, not
because it is established. I have **not** swapped any hull: the 89 percent result
is measured on the Yaris hull named in section 0, and changing geometry would
invalidate comparison with it. Whether to move to Yaris/Camry/Silverado is
Josie's call.

## R11. Records promoted out of `out/`

`analysis/r9_speed_surface.py --export` writes `data/r9_speed_surface.tsv`, one
tidy row per run, **162 runs**, no per-frame series. The series stay on the node:
they are ~400 rows per run and are a working artifact, not a result.

---

# RESULTS, THIRD SESSION (post-crash, node 922255 c642-091, 2026-08-19)

## How this session started, and what the recovery commit did not say

The tmux server died at approximately 17:40 taking all nine R9 sessions and the
Vista ControlMaster with it. The coordinator committed this branch's staged tree
as `98d4d9d`, whose own message says it "is NOT a checkpoint the session chose
and it has not been reviewed by its author". Everything below treats that commit
as unverified input, which is how it asked to be treated.

Three things were checked before anything was run, and one of them changed the
plan:

1. The worktree was clean and the Vista copy of the driver had md5
   `3ea7c487a25ec52a9279c53cd18747e6`, **identical to the committed one**, so no
   sync was needed and no run below is from a different driver than the one in
   git.
2. The dispatch named node 920452 on c642-071. That node was **dead**: its
   two-hour window had ended roughly sixteen hours earlier. The live node was
   922255 on c642-091. A dispatch is not evidence about a running allocation.
3. **THE FULL MATRIX HAD NEVER COMPLETED, AND NOTHING IN THE COMMITTED RECORD
   SAID SO.** `uni.log` ends in a traceback:

   ```
   ValueError: bc_per_frame 4 is coarser than the 5 the CFL-style rule needs at
   u_max 8.900 m/s; a particle would overshoot the recycle plane
   RC=1
   ```

   The run died on the **first cell of the v_car = 8.9 m/s row**, so the fastest
   vehicle speed in the entire study had no 400-frame data at all. The committed
   TSV is not wrong about this, it is simply silent: a missing row looks exactly
   like a row nobody asked for. This is the failure mode where an incomplete
   sweep is indistinguishable from a complete one unless the runner's exit code
   is stored next to the records, and it is not.

## The four arms run this session

All four use the hull, depth 0.30 m, 400 frames with 250 discarded, and
`wrench_dt_mode=frame`. `bc_per_frame` was passed **explicitly and uniformly**
in every arm, never left to the auto rule, for the reason the driver already
records: the auto rule gives different cells different numbers of BC
applications and therefore different physical frame durations, which previously
faked a feature in the arc.

| arm | what it is | cells | seeds |
|---|---|---|---|
| M1 | the full (v_car x v_water) matrix, g64 | 20 | 5 |
| M2 | the same matrix at g96 | 20 | 2 |
| M3 | five iso-`\|v_rel\|` arcs at 9 angles, g64 | 45 | 1 |
| M4 | the still-water edge, v_water = 0 | 5 | 5 |

M4 exists because `V_WATER_GRID` is `[0.5, 1.0, 2.0, 3.0]` and **has no zero**,
so the surface had no still-water column. That column is not a nicety: it is the
pure vehicle-motion case, the one Al-Qadami et al. 2022 actually drove, and it
is the reference against which any statement of the form "the flow adds this
much" has to be made. Its `(0, 0)` cell is also the no-forcing control, which
until now had repeats at a single seed only, a spread this document itself says
carries no information.

## T1. The surface now carries a distribution in every cell

Twenty cells, five seeds. The full table is reproduced by

    python3 analysis/r9_speed_surface.py --from-tsv data/r9_speed_surface.tsv \
        --surface-arm M1 --arc-prefix M3m

**The seed noise floor across the whole surface is S = 0.0086**, that is 0.86
percent, where S is the pre-registered `(max - min) / mean`. The largest
within-cell standard deviation anywhere is 115 N on a cell whose mean is
30,044 N.

This number is what makes everything below a measurement rather than scatter,
and it could only be obtained by varying `--seed`. Repeats at a fixed seed give
a relative spread of 4.7e-6, because the SDF path is effectively deterministic
and GPU atomic ordering is all that separates two identical runs. A "repeat"
that does not vary the seed samples nothing.

## T2. The split-dependence is NOT a property of 3.0 m/s, and it GROWS with speed

This is the main new result. Each arc holds `|v_rel|` fixed and sweeps the angle
from pure broadside (all water) to pure axial (all vehicle), so the spread along
one arc **is** the split-dependence at that relative speed.

| `\|v_rel\|` m/s | min `\|F_h\|` N | max `\|F_h\|` N | split S | S / seed noise | peak angle |
|---|---|---|---|---|---|
| 1.0 | 414.8 | 970.2 | 0.7589 | 88x | -67.50 deg |
| 2.0 | 652.2 | 2208.2 | 0.9734 | 113x | -67.50 deg |
| 3.0 | 923.7 | 4262.0 | 1.0689 | 124x | -67.50 deg |
| 4.5 | 1457.2 | 8749.6 | 1.1202 | 130x | **-22.50 deg** |
| 6.0 | 1928.4 | 16179.4 | 1.2809 | 149x | **-22.50 deg** |

Angle is measured from broadside, so 0 deg is all water and -90 deg is all
vehicle.

Three separate statements, and they should not be merged:

1. **The effect exists at every relative speed tested**, from 1.0 to 6.0 m/s. It
   is not an artifact of the single magnitude the earlier arc used.
2. **It grows monotonically with relative speed**, 0.76 to 1.28. So collapsing
   v_car and v_water into one speed gets *worse* as conditions get *more*
   dangerous, which is the opposite of the direction that would make the
   simplification safe to keep.
3. **The worst-case split MOVES.** At and below 3.0 m/s the peak load is at
   -67.5 deg, which is mostly vehicle motion. At and above 4.5 m/s it jumps to
   -22.5 deg, which is mostly water flow. The surface changes shape, it does not
   merely scale. A single worst-case split quoted from one magnitude would be
   wrong at another.

Every S in that table exceeds the seed noise floor by between 88 and 149 times.

## T3. A dip at exactly -45 deg survives the explanation that was supposed to kill it

At every one of the five magnitudes, the equal-split cell at -45 deg sits well
below both of its neighbours. At `|v_rel|` = 6.0 it reads 6,606 N between 13,770
and 14,093 N.

The driver already carries an explanation for a dip at this cell: the auto
`bc_per_frame` rule put the 45 degree cell on a different number of BC
applications than its neighbours, so it simulated a different physical duration.
**That explanation does not apply here and the arms above were designed so that
it could not.** Measured from the records rather than assumed:

| quantity | across all 45 arc cells |
|---|---|
| `bc_per_frame` as applied | **4 everywhere** |
| `substeps_effective` | **12 everywhere** |
| `wrench_dt_s` | **0.0363636... everywhere** |
| `bc_per_frame_auto` | varies, 1 to 3 |

So the auto rule still *wants* different values, but nothing downstream of it
differs: every cell got the same treatment and the same frame duration. The dip
is therefore **not** the previously named artifact. It is recorded here as
unexplained.

**It does not drive the headline.** At every magnitude the arc's minimum is the
pure-axial cell at -90 deg and the maximum is at -22.5 or -67.5 deg, so the dip
lies strictly between the two extremes that set S. Removing it entirely would
not change any S in T2.


## T4. The still-water edge, and a defect it exposed in my own reporting

`v_water = 0` with the vehicle moving is the pure vehicle-motion case, and it is
consistently the **lowest** load on its arc. From M3, at matched relative speed:

| `\|v_rel\|` m/s | still water, `\|F_h\|` N | worst split at the same `\|v_rel\|` | ratio |
|---|---|---|---|
| 1.0 | 414.8 | 970.2 | 2.3x |
| 3.0 | 923.7 | 4262.0 | 4.6x |
| 6.0 | 1928.4 | 16179.4 | **8.4x** |

Driving at 6 m/s through still water and standing still in 6 m/s water are not
the same loading. The still-water case is roughly **eight times lighter** at
that speed, and the gap widens with speed. That asymmetry is the whole reason
v_car and v_water cannot be collapsed into one number, and it is visible only
because they are separate axes here.

The M4 arm adds five seeds to that edge. Its per-cell seed spread is 0.46 to
1.21 percent, the same order as the 0.86 percent floor of the main surface in
T1 and slightly above it. **These figures are from the completed five-seed arm.**
A two-seed reading taken while the arm was still running gave 0.25 to 0.41
percent, which was not wrong so much as premature: a spread from two samples
understates one from five, systematically and in a known direction. It is
recorded because the earlier number was drafted into this document before the
arm finished.

**IT ALSO EXPOSED A DEFECT IN MY OWN REPORTING, WHICH IS RECORDED RATHER THAN
QUIETLY FIXED.** M4 includes the `(0, 0)` no-forcing cell. Five seeds gave
`|F_h|` of 0.573, 1.594, 1.699, 2.189 and 1.677 N, that is 0.013 to 0.049
percent of analytic buoyancy, every one of them a pass by a factor of more than
a hundred against the pre-registered 5 percent. But `S = (max - min) / mean` on
those five numbers is **1.045**, a hundred times the floor of every forced
cell, and my first version of the surface report published that as the noise
floor of the whole arm. It divides by a quantity the experiment exists to drive
to zero. This is precisely the failure the `spread()` docstring in this same
file already warns about, committed by the same person who wrote the warning.
No-forcing cells are now excluded from the floor and still printed.

**A second, smaller inconsistency, reported not resolved.** The C1 control
records 50.50 N of residual horizontal force where these five record 0.573 to
2.189 N, a factor of 23 to 88. Both pass C1 by a wide margin (ratio 0.0113
against these 0.000128 to 0.000490), and the arms differ in `bc_per_frame` and in
frame budget, so the two are not run at the same settings. It is noted because
"the control passes" is a weaker statement than it looks when the control's own
value moves by two orders of magnitude between arms.

## T5. Resolution: the LEVEL moves, the ORDER does not

The same 20-cell matrix was run at g96 (M2, seed 0). Reproduced by
`report_grid_compare` in the analysis script.

| quantity | g64 to g96 |
|---|---|
| per-cell level change | mean +5.68 percent, min -19.54, max **+40.59** |
| mean absolute change | **10.24 percent** |
| rank inversions | **4 of 190 pairs, 2.1 percent** |

So the absolute force at a cell is resolution-sensitive at the ten percent level
and up to forty percent in one cell, while the ORDERING of the surface is 97.9
percent preserved. Any claim of the form "these conditions load the vehicle more
than those" survives the grid change; any claim of the form "the load is N
newtons" does not.

This is the same lesson CLAUDE.md's August 4 audit item 5 already records for
`final_disp_mag_m` ("cite the verdict, never the displacement magnitude"),
reached here by a different route and on a different quantity. Syamlal, Celik
and Benyahia 2017 is the citable reason a transient quantity need not converge
under refinement at all.

**This is NOT a GCI and must not be quoted as one.** `n_grid`, `dt` and
`bc_per_frame` all move together between the two arms, so it bounds sensitivity
to a bundle of changes rather than to resolution alone. M2's second seed had not
finished when the node window closed, so g96 carries no distribution and nothing
above is graded against a g96 noise floor.

## T6. Reproducibility record, which the literature does not supply

A deep search over 105 papers, commissioned for this question and returned this
session, found that the vehicle-wading studies "do not report, in one place,
particle/grid counts, GPU model, wall time per simulated second, multi-GPU
scaling, or a runnable case". So it is put here in one place. **This is a
secondary-source claim about the literature and I have not read those papers.**

| | g64 | g96 |
|---|---|---|
| water particles | 41,636 to 41,649 | 164,382 |
| rigid particles | Yaris hull, SDF collider, `--sdf-res 32` | same |
| simulated time per run | 14.545 s | 13.333 s |
| mean wall clock per run | 6.07 s | 29.50 s |
| **wall per simulated second** | **0.417 s/s** | **2.213 s/s** |
| runs measured | 156 | 20 |

GPU: **NVIDIA GH200 120GB**, driver 590.48.01, 97,871 MiB, TACC Vista, one card,
partition `gh`. Engine: **warpmpm** (NOT Genesis) on warp 1.15.0.

Two honest qualifications. The water particle count **varies with the seed**,
41,636 to 41,649, which is the seed doing real work rather than reseeding a
random number generator that nothing reads. And every timing above was measured
with **up to four concurrent jobs sharing the one card**, so each is an upper
bound on the cost of a single job, not a dedicated-card benchmark. The g64 and
g96 rows also simulate slightly different durations because `bc_per_frame`
differs between the arms, so the per-simulated-second figures are the
comparable ones, not the per-run ones.

## T7. Where this sits in the literature, in the literature's own words

The same deep search states that the moving-vehicle studies "still reduce
stability to failure thresholds (e.g., depth or depth x velocity), **not a
continuous safe-speed surface resolving vehicle speed independently from current
velocity**". That is the object built here, so the gap is confirmed in the
field's own terms rather than asserted from this project's silence.

It also reports that body-fixed formulations, while established for Eulerian
immersed-boundary and level-set solvers, "are not evident as a developed
moving-reference formulation for MPM", and that a body-following refinement
window "appears unreported". The 34 percent rest-frame against ground-frame
discrepancy recorded in R4b of the previous session is therefore a number on
open ground, and it should be presented as an **upper bound with its confounds
attached** (hull placement, undeveloped ground-frame stream, window length),
because an upper bound with a number is worth more than an open question.

**None of these citation claims has been checked against a primary record.**
They are reported as what a search returned.

## T8. Limitations this session did not remove

- **The body is prescribed.** `RigidBody6DOF` raises `NotImplementedError` on a
  non-zero COM offset, and the Yaris cloud CG sits 0.6312 m above the floor
  against bbox mid-height 0.7427 m. Every number here is a load on a commanded
  body. **No FORD or NO-FORD verdict follows**, because a prescribed body cannot
  be swept away.
- **There are no wheels.** The hull is a single rigid body with no wheels, no
  suspension and no rolling degree of freedom. This matters quantitatively:
  reported wheel friction spans an order of magnitude, near 0.3 locked against
  near 0.024 free rolling, so a single hull-floor coefficient cannot represent
  both and the choice is not neutral.
- **The in/outflow treatment has no reference implementation.**
  `openchannel_bc.py` implements Zhao, Bolognin, Liang, Rohe and Vardon 2019,
  and slot d19-priorcode established this session that this BC is **not present
  in public Anura3D**. Its correctness rests on the publication alone.
- **What was deliberately NOT spent node time on.** The same search found that
  no retrieved study shows air entrainment, spray, surface tension, turbulence
  closure, reduced sound speed or outlet-boundary choice flipping a vehicle
  motion verdict, and that the ten-times-flow-speed sound-speed rule has no
  primary derivation in that corpus. The numerical sound speed was therefore
  left alone. What the same source says DOES move a verdict, bed friction and
  watertightness, is untouched here and is the better target for a next window.
- **The -45 degree dip is unexplained**, see T3.
- **`wrench_dt_mode=frame` is a design decision, not a detail.** The accumulator
  is divided by the caller-supplied dt, so handing it the substep inflates every
  force by exactly the substep count, plausibly and silently. d19-priorcode
  established this session that this caller-supplied dt is peculiar to this
  engine's accessor: Anura3D takes nodal traction from particle stress and
  Chrono zero-fills its accumulator next to the kernel launch, so neither
  exposes the trap. The mode is written into every row of the TSV so no reader
  has to trust it was set correctly.

## T9. What completed and what did not

Reported separately, because the node window closed on a running job.

**Completed:** M1 (full matrix, g64, 5 seeds, 100 runs), M3 (five arcs, 9
angles, 45 runs), M2 seed 0 (full matrix, g96, 20 runs).

**Did not complete:** M2 seed 1, so g96 has no ensemble and no noise floor. M4b
was still running when the window closed; its completed cells are in the TSV and
its `n` per cell is printed by the analysis rather than assumed.

**Discarded deliberately:** the first M4 attempt. It gave all five cells of a
seed the same `--label`, and the driver names its record
`SUMMARY_<label>_g<n_grid>.json`, so each invocation overwrote the last and only
the final cell of each seed survived. The file existed and parsed and held one
cell where five had run, which is the quiet kind of wrong. Its records were
deleted and the arm re-run as M4b with unique labels rather than being patched
up in analysis.

## T10. Tooling changes, and the defect adding them found

`analysis/r9_speed_surface.py` gained `--from-tsv` this session. Until now the
analysis could only read `SUMMARY_*.json` under `out/`, which lives on an idev
node; when that allocation ends, the inputs to every published number end with
it. The committed TSV now regenerates every table above with no GPU and no
allocation, on stdlib alone, which matters because this Mac has numpy in no
system interpreter.

Adding it immediately found a real defect. `export_tidy` flattens
`force_mean_N` into three scalar columns, so records loaded from the TSV were
**not interchangeable** with records loaded from JSON, and the pre-existing C2
section raised `KeyError: 'force_mean_N'` on its fourth print. It failed loudly
only because that section indexes rather than `.get()`s. A section written with
`.get()` would have printed `None` as a measurement and nothing would have
complained. The loader now rebuilds the composite fields.

**The seed is still not a first-class field.** It is written nowhere in the
record and survives only inside the run label, recovered by parsing
`<arm>s<seed>`. An arm named any other way is dropped from an ensemble silently
rather than loudly, so every ensemble printed reports its own `n` and a silent
drop shows up as a wrong count, which is visible, instead of a wrong mean, which
is not. The pre-existing `seed0` to `seed4` labels do **not** match that pattern
(the character before the digit is `d`, not `s`) and are correctly excluded
rather than half-counted. Writing the seed into the record is the right fix and
was not done tonight, because changing the driver mid-flight would have split
the provenance of the very runs being collected.
