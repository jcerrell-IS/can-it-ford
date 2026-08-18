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

`analysis/research_index.py --query "Al-Qadami"` returns **zero** matches, so
none of these is in the 332-paper corpus index. The index cannot report on this
topic's closest prior art and its silence is not evidence of absence.

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
