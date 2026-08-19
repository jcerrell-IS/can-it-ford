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
The cell with the LOWER relative speed carries 2.3x the load.

> **WITHDRAWN, see T17.** This table is the `c3full` arm: 60 frames with 20
> discarded, so 40 frames retained. That window is TRANSIENT by this project's
> own settle audit, which found 25 of 25 runs need more than 8 frames discarded
> with a MINIMUM of 29, and this arm discards 20. Over the developed-flow window
> the same pair **inverts** to 0.912x. The "2.3x" figure must not be used. The
> claim that the two variables are not interchangeable survives and is much
> stronger elsewhere; only this particular pair and number are withdrawn.

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
pure vehicle-motion case, the one Al-Qadami et al. 2022 modelled, and it
is the reference against which any statement of the form "the flow adds this
much" has to be made.

> **CORRECTED.** This read "the one Al-Qadami et al. 2022 actually drove".
> `10.1111/jfr3.12828` is **numerical**, so nothing was driven in it; the
> full-scale experimental paper is `10.1007/s11069-021-04949-6` (2021), and its
> title does not announce vehicle speed as a swept variable. All three DOIs were
> re-resolved against Crossref on 2026-08-20 and the titles, years and journals
> in the table above match the records exactly. Its `(0, 0)` cell is also the no-forcing control, which
until now had repeats at a single seed only, a spread this document itself says
carries no information.

## T1. The surface now carries a distribution in every cell

Twenty cells, five seeds. The full table is reproduced by

    python3 analysis/r9_speed_surface.py --from-tsv data/r9_speed_surface.tsv \
        --surface-arm M1 --arc-prefix M3m

**The TOTAL REPEATABILITY FLOOR across the whole surface is S = 0.0086**, that
is 0.86 percent, where S is the pre-registered `(max - min) / mean`. The largest
within-cell standard deviation anywhere is 115 N on a cell whose mean is
30,044 N.

> **CORRECTED NAME, see T11.** This was written as "the seed noise floor" and
> that name is wrong. It bundles the seed effect together with run-to-run
> nondeterminism at fixed seed, which T11 measures at up to 0.59 percent in this
> speed range. It is the CONSERVATIVE comparator and it is the right one to
> grade against, so no number in this document changes; only the name does.
> Anything reported as measuring "the seed" alone would be overstating it.

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

Every S in that table exceeds the total repeatability floor by between 88 and
149 times. Graded instead against T11's worst fixed-seed nondeterminism at the
matching speed, the margin is a factor of about 130 at the very worst cell,
which is the number to quote if a single figure is wanted.

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
| per-cell level change | mean +5.71 percent, min -19.49, max **+40.63** |
| mean absolute change | **10.21 percent** |
| rank inversions | **4 of 190 pairs, 2.1 percent** |

Both arms are seeded: g64 has five seeds and g96 has two, and the g96 noise
floor is **0.00728** against g64's 0.00859, so the two surfaces are compared
floor to floor rather than draw to draw. The comparison is also stable against
its own ensemble: computed from g96 seed 0 alone it gave mean +5.68 percent,
mean absolute 10.24 percent and the same 4 of 190 inversions, so adding the
second seed moved the level figures by less than 0.04 points and moved the
inversion count not at all.

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
to a bundle of changes rather than to resolution alone. Two seeds is also a thin
ensemble: it is enough to establish that a floor exists and roughly where it is,
not enough to characterise a distribution.

## T6. Reproducibility record, which the literature does not supply

A deep search over 105 papers, commissioned for this question and returned this
session, found that the vehicle-wading studies "do not report, in one place,
particle/grid counts, GPU model, wall time per simulated second, multi-GPU
scaling, or a runnable case". So it is put here in one place. **This is a
secondary-source claim about the literature and I have not read those papers.**

All rows are the **Yaris** hull. Read the `dx` caveat below before comparing
grids across vehicles.

| | g64 | g96 | g128 |
|---|---|---|---|
| `n_grid` | 64 | 96 | 128 |
| `grid_lim` (domain, m) | 9.42174 | 9.42174 | 9.42174 |
| **`dx` (m)** | **0.1472147** | **0.0981431** | **0.0736074** |
| water depth (m) | 0.30 | 0.30 | 0.30 |
| depth in cells | 2.04 | 3.06 | 4.08 |
| water particles | 41,636 to 41,649 | 164,351 to 164,382 | 413,878 to 413,880 |
| rigid body | Yaris hull as SDF collider, `--sdf-res 32` | same | same |
| simulated time per run | 14.545 s | 13.333 s | 13.968 s |
| mean wall clock per run | 5.99 s | 28.38 s | 91.3 s |
| **wall per simulated second** | **0.412 s/s** | **2.129 s/s** | **6.54 s/s** |
| runs measured | 170 | 40 | 2 |

**`n_grid` DOES NOT FIX RESOLUTION ACROSS VEHICLES, and this table would mislead
without the warning.** `grid_lim` is derived from the loaded hull's extent, so a
different vehicle at the same `n_grid` gets a different `dx`. Measured in this
very dataset: g64 carries **three** distinct `dx` values, 0.1472147, 0.1998810
and 0.2046201, at three domains 9.42174, 12.79239 and 13.09569 m, because the
Silverado arms load a larger hull. Never describe two vehicles at one `n_grid`
as "the same resolution".

**Memory, measured on the card rather than estimated.** One g64 job: **630 MiB**
of 97,871 MiB. Three concurrent jobs (two g64, one g96): 2,289 MiB. Five
concurrent (adding g128): **4,069 MiB peak observed**. A per-job g128 figure was
never isolated, so none is quoted. The honest headline is that **memory was
never the binding constraint**: this scene cannot fill a 98 GB card at any grid
reached, and utilization rather than capacity is what was worth raising.

GPU: **NVIDIA GH200 120GB**, driver 590.48.01, 97,871 MiB, TACC Vista, one card,
partition `gh`. Engine: **warpmpm** (NOT Genesis) on warp 1.15.0.

Two honest qualifications. The water particle count **varies with the seed**,
by 13 particles at g64 and 31 at g96, which is the seed doing real work rather
than reseeding a random number generator that nothing reads. And every timing above was measured
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
  force by exactly the substep count, plausibly and silently. The mode is
  written into every row of the TSV so no reader has to trust it was set
  correctly.

  **CORRECTED, and the correction reverses the framing.** An earlier version of
  this bullet said, on slot d19-priorcode's authority, that a caller-supplied dt
  is peculiar to this engine's accessor, because Anura3D takes nodal traction
  from particle stress and Chrono zero-fills its accumulator next to the kernel
  launch. **d19 has since refuted its own claim.** `sdfibm`, read locally at
  commit `3627269`, computes `F = rho_f * SUM_cells[alpha * (u_f - u_s) *
  V_cell] / dt` with `dtINV = 1.0/dt` and `dt` supplied through
  `SolidCloud::interact(time, dt)`. That is a momentum difference over a
  timestep, which is this pattern exactly. So a published signed-distance
  immersed-boundary code arrives independently at the same force-extraction
  design, and the requirement is **not** an idiosyncrasy of this engine. It
  remains a trap worth guarding, because the failure is silent, but it is a
  shared design rather than a local defect. This is a secondary-source claim: I
  have not read sdfibm.

## T9. What completed and what did not

Reported separately, because the node window closed on a running job.

**Completed, all four arms:** M1 (full matrix, g64, 5 seeds, 100 runs), M2
(full matrix, g96, 2 seeds, 40 runs), M3 (five arcs at 9 angles, 45 runs), M4b
(still-water edge, 5 cells x 5 seeds, 25 runs). 210 new runs, 368 records in the
committed TSV.

**Did not complete:** nothing that was launched and left running. The one arm
that was killed, the first M4, was killed deliberately and is described below.

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

---

# RESULTS, FOURTH BLOCK (same node 922255, after the first two commits)

Three further arms were run once the card was measured to be idle at 9 to 17
percent. Each answers a question raised by the results above rather than opening
a new one.

## T11. THE FIXED-SEED DETERMINISM CLAIM IS TRUE ONLY IN THE NEAR-STATIC LIMIT

This document, the previous session, and the dispatch that commissioned this
work all state the same thing: the SDF path is effectively deterministic at a
fixed seed, relative spread 4.7e-6, so repeats at fixed configuration carry no
information and an ensemble must come from `--seed`. **That is refuted in the
regime this study is about, and it was refuted by accident.**

M5 re-ran the five arcs at seed 0 under a new label, intended only as a
bookkeeping duplicate of M3. Every recorded field is identical between them:
same grid, same seed, same `bc_per_frame` 4 as applied, same
`substeps_effective` 12, same frames and discard. They should have agreed to the
last few digits. Measured, nine cells per magnitude:

| `\|v_rel\|` m/s | max abs. relative difference | mean |
|---|---|---|
| 1.0 | 0.0037 percent | 0.0015 |
| 2.0 | 0.0182 percent | 0.0077 |
| 3.0 | 0.0764 percent | 0.0301 |
| 4.5 | 0.3876 percent | 0.1919 |
| 6.0 | **0.5881 percent** | 0.2376 |

Two identical invocations agree to 3.7e-5 at 1.0 m/s and to only 5.9e-3 at
6.0 m/s. The disagreement grows **monotonically and by a factor of 160** across
the range, which is why it is reported as a finding rather than as scatter: pure
scheduling jitter would not order itself by velocity.

**Why the original number was not wrong, only narrow.** The 4.7e-6 was measured
on the C1 no-forcing control, where the water is still and the vehicle is
stationary. Almost nothing is being accumulated, so almost nothing can be
accumulated in a different order. The claim was then carried to a moving,
forced scene where it does not hold.

**Mechanism, offered as a hypothesis and NOT established here.** Faster flow
means more particles crossing more cells per step, so more atomic collisions in
the particle-to-grid scatter, and floating point addition is not associative
under reordering. That predicts exactly the observed monotone growth with
speed. It has not been tested and no attempt was made to test it.

**Three consequences, and the first two matter more than the third.**

1. **The "seed noise floor" in T1 is not a seed floor.** It is a total
   repeatability floor that bundles seed effect together with run-to-run
   nondeterminism at fixed seed. That is the conservative comparator and it is
   the right one to grade against, so no number above changes. But it must not
   be described as measuring the seed.
2. **Fixed-config repeats DO carry information at speed**, and roughly as much
   variance as changing the seed does. The instruction to spend runs only on
   seeds is correct at low speed and wasteful of a control at high speed.
3. **The headline is untouched.** S runs from 0.76 to 1.29 against a
   repeatability floor of at most 0.59 percent, so the margin is a factor of
   130 at the very worst cell rather than the 149 quoted from the seed floor.

## T12. Error bars on S, the headline statistic

S is a ratio of extremes across cells, and the uncertainty of an extremal
statistic does not follow from the uncertainty of its members, so S needed its
own ensemble. **Five seeds per magnitude, nine angles each, 225 runs.**

| `\|v_rel\|` m/s | S per seed | mean S | sd |
|---|---|---|---|
| 1.0 | 0.7590, 0.7578, 0.7621, 0.7564, 0.7574 | **0.7585** | 0.0022 |
| 2.0 | 0.9733, 0.9701, 0.9727, 0.9702, 0.9708 | **0.9714** | 0.0015 |
| 3.0 | 1.0683, 1.0697, 1.0712, 1.0666, 1.0647 | **1.0681** | 0.0026 |
| 4.5 | 1.1150, 1.1140, 1.1148, 1.1173, 1.1171 | **1.1156** | 0.0015 |
| 6.0 | 1.2864, 1.2847, 1.2847, 1.2868, 1.2848 | **1.2855** | 0.0010 |

**The monotone rise is not seed scatter, and the margin is not marginal.** Each
step between consecutive magnitudes, expressed in units of the larger of the two
standard deviations:

| step | gap in S | in sd |
|---|---|---|
| 1.0 to 2.0 | 0.2129 | **97 sd** |
| 2.0 to 3.0 | 0.0967 | **38 sd** |
| 3.0 to 4.5 | 0.0475 | **19 sd** |
| 4.5 to 6.0 | 0.1698 | **114 sd** |

The tightest step in the whole sweep is 19 standard deviations. There is no
reading of this data in which the trend is noise.

Note that the mean S at 4.5 is 1.1156 here against the 1.1202 reported in T2
from a single arc, and that T2's value sits OUTSIDE the five-seed range
[1.1140, 1.1173]. That is T11 in action: T2's column came from one invocation
each, and a single invocation is not reproducible to better than half a percent
at these speeds. **T2's S column should be read as the single draws they are;
this table supersedes it.** The qualitative content of T2 is unaffected, since
the peak-angle shift and the monotone rise both survive at 19 sd or better.

## T13. The bc guard was silently violated, and it cost at most 1.5 percent

**The defect.** The scene refuses a `bc_per_frame` coarser than its CFL-style
auto rule, because a particle could overshoot a recycle plane. It checks BEFORE
it snaps the value to divide the substeps evenly, and the snap can push the
applied value back under the rule with no error at all. At g64 with 11 substeps:

```
pass 4  ->  4 < auto 5   ->  ValueError, run aborts     (this is what killed uni.log)
pass 5  ->  5 >= auto 5  ->  snap to 4  ->  APPLIED 4 < auto 5, silently
```

The identical condition that aborts one run is reached quietly by another. It
caught the four `v_car` = 8.9 m/s cells of the main g64 surface, twenty runs
across five seeds. The g96 arm is unaffected: it applied 8 against an auto of 7.

**The control.** With 11 substeps, passing 6 gives `sub_per_tick` 2 and an
applied `bc_per_frame` of 6, which satisfies the rule, while
`substeps_effective` stays 12 exactly as in the suspect runs. dt and the frame
duration are therefore identical and the ONLY thing that changes is how often
the boundary condition is applied. Five seeds per cell:

| v_car | v_water | suspect (applied 4) | control (applied 6) | difference |
|---|---|---|---|---|
| 8.9 | 0.5 | 13737.9 N | 13535.8 N | -1.471 percent |
| 8.9 | 1.0 | 20097.0 N | 19873.5 N | -1.112 percent |
| 8.9 | 2.0 | 25622.6 N | 25666.7 N | +0.172 percent |
| 8.9 | 3.0 | 30035.4 N | 30299.6 N | +0.880 percent |

**Worst case 1.471 percent, and the signs are mixed.** So the violation is a
real systematic, not nothing: it is about twice the repeatability floor at these
speeds. It is also two orders of magnitude below the S values it could have
threatened, so no conclusion in this document turns on it. Reported as bounded,
not as harmless.

**The fix belongs in the driver and was NOT applied tonight**, because changing
the driver mid-flight would have split the provenance of the runs being
collected. The guard should re-check after the snap, or the snap should round
up to a legal value instead of down.

## T14. A FINER GRID CUTS THE FORCES BY 43 PERCENT AND CUTS S BY 43 PERCENT, AND THIS QUALIFIES THE HEADLINE

The `|v_rel|` = 3.0 arc was re-run at g128, which is roughly eight times the
cells of g64 and is what the idle 98 GB card was for. It does not confirm the
g64 arc. It is written up exactly as it would have been had it confirmed it.

| angle from broadside | g64 N | g128 N | change |
|---|---|---|---|
| -0.00 (all water) | 1882.3 | 1331.1 | -29.28 percent |
| -11.25 | 3580.3 | 1820.7 | -49.15 |
| -22.50 | 4219.5 | 2073.0 | -50.87 |
| -33.75 | 3518.6 | 1675.8 | -52.37 |
| -45.00 | 2170.2 | 1396.0 | -35.68 |
| -56.25 | 4036.2 | 1602.9 | -60.29 |
| -67.50 | 4262.0 | 1996.3 | -53.16 |
| -78.75 | 3516.1 | 1975.2 | -43.82 |
| -90.00 (all vehicle) | 923.7 | 1066.3 | **+15.43** |

**Mean absolute level change 43.34 percent, worst 60.29 percent.** Note the sign
flip at the pure-vehicle end: every mixed cell falls, the all-vehicle cell rises.

Three consequences, in descending order of how much they hurt.

1. **S falls from 1.0689 at g64 to 0.6065 at g128**, a 43 percent reduction in
   the headline statistic itself.
2. **The peak angle moves from -67.50 deg to -22.50 deg** under refinement alone,
   at fixed speed. At g64 that same shift was reported in T2 as a consequence of
   RAISING THE SPEED past 3.0 m/s. Refinement reproduces it without touching the
   speed. **So T2's claim 3, that the worst-case split moves with speed, is
   confounded with resolution and must not be stated as a physical result on
   this evidence.** It is withdrawn to the status of an observation at g64.
3. Rank inversions along the arc rise to **6 of 36 pairs (16.7 percent)**,
   against 2.1 percent for the g64-to-g96 surface comparison. The ordering is
   not as robust as the g96 comparison alone suggested.

**WHAT SURVIVES, AND IT IS THE MAIN CLAIM.** S = 0.6065 at g128 is still a 61
percent variation in load at a FIXED relative speed, against a fixed-seed
repeatability floor of 0.076 percent at this magnitude (T11). That is a margin
of about 800. **The existence and the scale of the split-dependence are robust
to a doubling of resolution in every direction. Its precise value, and the
location of its worst case, are not.** The paper-level claim, that v_car and
v_water cannot be collapsed into one speed, stands. Any specific S value must
carry its grid.

**Ruled out as the explanation: simulated duration.** The three grids simulate
14.545, 13.333 and 13.968 s in 400 frames, within 8 percent of each other, and
all retain 150 frames. The g128 arc is not a shorter run.

**Not ruled out, and the most likely candidate: stream development.** Mean
`stream_established_frac` on this arc is +0.744 at g64, +0.787 at g96 and
**+0.902** at g128. The same relationship holds cell-by-cell within every arc:
the cells with the best-established stream carry the lowest load. A coarser grid
represents the hull on fewer cells and obstructs the channel more, so the free
stream is less developed and the measured reaction is larger. That is a
hypothesis consistent with every number here and it has **not** been tested.

**Convergence is NOT claimed and the ladder is not monotone-by-assumption.**
CLAIMING a trend from two rungs would assume away this solver's documented
behaviour: CLAUDE.md's August 4 audit item 5 records `final_disp_mag_m` moving
+87.8 percent from g48 to g64 and then -59.2 percent from g64 to g96 at fixed
everything else. Syamlal, Celik and Benyahia 2017 is the citable reason a
transient quantity need not converge under refinement at all. The middle rung
was therefore run rather than interpolated.

**The g128 arm is one seed.** Given T11, a single g128 draw at this speed is
reproducible to roughly 0.08 percent, so the 43 percent effect is far outside
run-to-run noise; but one draw cannot bound a distribution and none is claimed.
Cost, for the record: 413,880 water particles, dx 0.073607 m, 91.3 s of wall
clock per run against 5.99 s at g64.

## T15. The resolution ladder with an ensemble, and a confound I proposed and then refuted

The `|v_rel|` = 3.0 arc now exists at three grids. g64 and g96 carry ensembles;
g128 is one draw.

| grid | arcs | mean S | sd S | mean `\|F_h\|` | peak angle | mean stream |
|---|---|---|---|---|---|---|
| g64 | 5 | 1.0681 | 0.0026 | 3118.5 N | -67.5 deg | +0.744 |
| g96 | 4 | 1.0076 | 0.0032 | 3109.9 N | -56.2 deg | +0.739 |
| g128 | 1 | 0.6065 | n/a | 1659.7 N | -22.5 deg | +0.902 |

**g64 and g96 agree closely and g128 does not.** From g64 to g96 the mean load
moves by 0.3 percent and S by 5.7 percent. From g96 to g128 the load falls 47
percent and S falls 40 percent. That is not the shape of a converging sequence,
and it should not be reported as one. It is consistent with this solver's
documented non-monotonicity under refinement.

### The confound I proposed

The three rungs did not apply the boundary condition equally often relative to
what the CFL-style rule required: applied 4 against auto 2 at g64, 8 at g96, and
**11 against auto 3** at g128. The inflow slab is a per-tick Dirichlet clamp, so
applying it more often forces the stream harder. g128 had both the
best-established stream (+0.902) and the lowest load, which is exactly what
over-forcing would produce. The hypothesis was that the g128 result was a
BC-rate artifact rather than a resolution effect.

### The control, and it refutes the hypothesis

The grid was held at g64 and only the application rate moved, to g128's value.
`substeps_effective` stays at 11 or 12 throughout, so frame duration is
effectively unchanged:

| run | applied / auto | mean `\|F_h\|` | S | mean stream |
|---|---|---|---|---|
| g64, bc applied 4 | 4 / 2 | 3123.1 N | 1.0683 | +0.744 |
| g64, bc applied 6 | 6 / 2 | 3161.4 N | 1.1156 | +0.729 |
| g64, bc applied 11 | 11 / 2 | 3213.0 N | 1.1872 | +0.710 |
| **g128, bc applied 11** | 11 / 3 | **1659.7 N** | **0.6065** | **+0.902** |

**Over-applying the BC moves both quantities the WRONG WAY.** At fixed grid it
raises the mean load by 2.9 percent and *lowers* stream establishment from
+0.744 to +0.710. g128 at the same applied rate has a 47 percent *lower* load
and a *higher* stream. A BC-rate explanation predicts the opposite sign on both,
so it is refuted.

**Conclusion: the g128 result is a genuine resolution effect.** It is still one
draw, and the batch job queued tonight runs g96, g128 and g160 arcs at five
seeds to bound it properly.

**A further reason not to trust the peak angle.** It reads -67.50, -22.50 and
-67.50 at bc 4, 6 and 11 on the SAME grid. It is not even monotone in a
numerical parameter that changes the load by under 3 percent. Combined with T14,
the location of the worst-case split is not a reportable quantity at any
resolution reached here. The EXISTENCE and SCALE of the split-dependence, which
is the actual claim, are unaffected: S is between 0.61 and 1.19 across every
grid and every BC rate tried, against a repeatability floor of 0.076 percent.

### T15a. The g128 collapse reproduces on a second seed

A second g128 arc landed in the last minutes of the window. The two draws:

| draw | S | mean `\|F_h\|` |
|---|---|---|
| seed 0 | 0.6065 | 1659.7 N |
| seed 1 | 0.6076 | 1657.6 N |

They agree to **0.18 percent on S and 0.13 percent on load**. So the collapse
from S ~1.07 at g64 to S ~0.61 at g128 is not a single-draw fluke, and neither
is the 47 percent drop in load. The finest rung is still only two draws, and the
queued batch job takes it to five.

## T16. Which window the headline PAIR belongs to, answered, and the confound cleared first

Raised by slot d18-platform, who measured that the headline pair inverts and
correctly said it was not theirs to close. Answered here with the window named,
as d15-settle's rule requires.

### The confound first: `hull_y_m` empty in `c3full`

`hull_y_m` is empty in exactly twelve arms and they are all from the FIRST
session: `c0wrongdt`, `c1ctrl`, `c2arc`, `c3full`, `c3res`, `c4ground`,
`c4rest` and `seed0` to `seed4`. **Every arm run since records it, and records
the same value**, 4.710871156863869, across `M1`, `M2`, `M3`, `M4`, `M5`, `M6`,
`M8`, `M9` and both BC controls. So the empty field is a RECORDING gap in the
older runs, not a placement difference between them. It does mean hull placement
in `c3full` cannot be verified from the record, only assumed.

> **CORRECTED, this sentence used to end "so `c3full` is not used below" and that
> is inconsistent with T17, which does use it.** T17 uses `c3full` deliberately,
> because it is the arm that produced the published 2.262x and a number cannot be
> withdrawn without showing where it came from. The confound that sentence was
> worried about is now CLOSED by measurement rather than by avoidance: see T33.

### The measurement

The pair is pure broadside (all water, the stationary-vehicle case) against the
-22.5 deg split at the same `|v_rel|` = 3.0.

| arm | frames / discard | retained | seeds | broadside N | split N | ratio |
|---|---|---|---|---|---|---|
| `seed*` | 60 / 20 | 40 | 5 | 4418.2 | 6144.7 | **1.391x** |
| `L1s*` | 400 / 250 | 150 | 5 | 1864.4 | 3842.4 | 2.061x |
| `U1s*` | 400 / 250 | 150 | 5 | 1864.2 | 3842.7 | 2.061x |
| `M3` | 400 / 250 | 150 | 1 | 1882.3 | 4219.5 | 2.242x |
| `M5m3.0s*` | 400 / 250 | 150 | 5 | 1876.1 | 4208.7 | **2.243x** |

### The answer

**The ratio belongs to the LATE window: frames 250 to 400 of 400, 150 frames
retained, which is the developed-flow window.** Stated with that window it is
**2.06x** at the `bc_per_frame` 2 setting the original figure came from, and
**2.24x** at the applied-4 setting used by every arm run tonight.

**I could not reproduce an inversion.** The broadside cell carries the lower
load in every window I hold, 1.391x, 2.061x and 2.243x, all above 1. If
d18-platform's inversion came from a different window, depth or pair, the
specific window should be named and I will re-run against it rather than argue
from mine.

**What IS true, and it is why the pair should never be quoted bare.** The ratio
moves from 1.391x to 2.243x, a 61 percent change, purely with the window, and
the absolute forces move further: the broadside cell reads 4418.2 N over the
early window against 1864.4 N over the late one, a factor of 2.4. The early
window retains frames 20 to 60, which is transient; the late window retains 250
to 400, which is developed. Both cells fall as the flow develops and the
broadside cell falls further, which is what raises the ratio.

**Restated rather than withdrawn: the pair is 2.24x over the developed-flow
window, frames 250 to 400 of 400, at g64 with applied `bc_per_frame` 4, five
seeds.** Any use of it must carry that window.

**The general S result is NOT affected by any of this**, and this is the
important part. S is computed within a single arm at a single window, so a
window change rescales the cells it compares together. Measured, S at
`|v_rel|` 3.0 is 1.0681 (g64, five seeds, sd 0.0026), 1.0076 (g96, four seeds),
0.6065 and 0.6076 (g128, two seeds), and 1.0683 to 1.1872 across three BC rates
at fixed grid. It is between 0.61 and 1.19 everywhere, against a fixed-seed
repeatability floor of 0.076 percent. The claim that v_car and v_water cannot be
collapsed into one speed does not rest on the pair.

**On convergence, since the sequence above is not converging.** Grid refinement
is not expected to converge a transient quantity (Syamlal, Celik and Benyahia
2017, `10.1002/AIC.15868`), so the g96-to-g128 fall should not be read as a
solver defect. A convergence claim would need a time-averaged observable over a
demonstrated-stationary window with a GCI, and none of the windows above has
been shown stationary. That is stated so a reader does not infer divergence is a
bug, and it is not claimed either way here.

## T17. C-1 RESOLVED: the pair really does invert, and it is a WINDOW effect

Raised as an open contradiction by slot d18-platform, who computed 0.912x where
this document had committed 2.3x, and correctly said it was not theirs to close.
**Both numbers are right. They are different windows of the same experiment.**

My T16 above answered a DIFFERENT pair (broadside against the -22.5 deg split)
and did not touch this one. That was my error in reading the report, and T16's
content stands on its own but does not close C-1. This does.

The cells are (v_car 2.20, v_water 3.00), `|v_rel|` 3.720, against
(v_car 4.50, v_water 0.50), `|v_rel|` 4.528. Measured across every arm that
holds both:

| arm | grid | frames / discard | retained | bc | seeds | (2.2, 3.0) | (4.5, 0.5) | ratio |
|---|---|---|---|---|---|---|---|---|
| `c3full` | g64 | 60 / 20 | **40** | 2 | 1 | 8621.4 N | 3811.1 N | **2.262x** |
| `L2full` | g64 | 400 / 250 | 150 | 2 | 1 | 5028.4 N | 5534.7 N | 0.909x |
| `M1s*` | g64 | 400 / 250 | 150 | 4 | **5** | 5176.5 N | 5675.3 N | **0.912x** |
| `M2s*` | g96 | 400 / 250 | 150 | 8 | 2 | 5315.9 N | 6246.4 N | 0.851x |

**The inversion is real and it is clean.** Over a 40-frame retained window the
lower-relative-speed cell carries 2.26x the load. Over a 150-frame retained
window it carries 0.85x to 0.91x. The sign of the comparison flips.

**Which window is defensible, under d15-settle's rule.** A load ratio is not a
verdict, so the "full record" half of that rule does not apply; what applies is
that the window must not be transient. The project's settle audit applied
`stationarity.py` to all 25 local runs and found **every one needs more than 8
frames discarded, minimum 29, median 48**. The `c3full` arm discards **20**,
which is below that minimum. Its retained window is therefore contaminated by
the starting transient by this project's own criterion, and the 2.262x is a
transient measurement.

**Resolution: the 2.3x figure is WITHDRAWN. The pair is 0.912x**, over frames
250 to 400 of 400, at g64, applied `bc_per_frame` 4, five seeds. It has been
marked withdrawn in place at the R5 table above rather than deleted, so the
error stays visible.

**The late-window answer is not a single arm's opinion.** Three arms agree on
the inverted side, 0.909x at bc 2, 0.912x at applied bc 4 with five seeds, and
0.851x at g96, so it survives a change of seed, of BC rate and of grid.

**What this does NOT touch.** The claim that v_car and v_water are not
interchangeable never rested on this pair, and the pair was always the weakest
possible way to state it: a single two-cell comparison on a product grid, where
the two cells differ in BOTH variables and in `|v_rel|`. The iso-`|v_rel|` arc
is the right instrument, because it holds relative speed EXACTLY fixed and
varies only the split. S there is 1.0681 at g64 over five seeds with sd 0.0026,
and between 0.61 and 1.19 across every grid and BC rate tried, against a
fixed-seed repeatability floor of 0.076 percent. **That is the result. The pair
was a convenience and it should not have been quoted as "the contribution stated
as a number".**

**A general lesson this cost, worth more than the pair.** Every load figure in
this project is a mean over a retained window, and the window is a free
parameter that can flip the SIGN of a comparison between two cells. A ratio
quoted without its window is not a weak claim, it is an unfalsifiable one.

## T18. The novelty claim, narrowed and strengthened

**All of this section is SECONDARY SOURCE.** The numbers come from a reader
who read the primary text tonight and from a 105-paper deep search. I have not
opened Shah 2018 myself and nothing below is a primary-source claim.

**The strongest form of the gap.** The nearest published moving-vehicle
experiment, Shah 2018 `[Sha18c]`, **did not treat vehicle speed as an
independent variable** in its methodology. So the gap is not only that nobody
has produced a continuous safe-speed surface; the closest experiment did not
sweep the axis at all. The `(v_car x v_water)` matrix here does, and that is the
narrowest true statement of what is new.

Reported with the handling both numbers require, because this project has a
documented history of conflating scales:

| quantity | value | scale |
|---|---|---|
| vehicle | Perodua Viva | **1:10 model** |
| critical depth | 0.0457 m | **MODEL scale**, not comparable to a full-scale 0.38 m without conversion |
| drive force | 0.00169 to 0.02115 N | **1:10**, needs x1000 for full scale |

**Correction to a prior-art count I would otherwise have inherited.** "Four
prior vehicle fording or wading simulations" is an **undercount**. At least
`[Lyu23]` (`10.1016/j.compfluid.2023.106144`, particle-based 3D SPH vehicle
wading), `[Ols18b]`, `[Xin21b]` and `[Var21]` are additional. Corrected in
CLAUDE.md at `c621931`. **The novelty here is the surface and the separated
axes, not being first to move a vehicle**, and no text in this document should
imply otherwise.

**The refinement-window negative, narrowed as asked.** Two compatible but
non-identical claims exist and they should not be merged. The project's own
record says no moving-vehicle refinement window was found across 206 papers; the
later search says a **body-following** window "appears unreported". **The claim
I am making is the second and narrower one**: no body-following refinement
window appears in the searched corpus. I am not claiming the broader negative,
and neither claim has been checked against a primary record.

## T19. Final state of the interactive window

**GPU utilization achieved, measured not asserted.** The node was found at
`0 %, 1 MiB` of 97,871 MiB. Over the session it ran at 17, 58, 62, 76, 84 and
95 percent at various points, with a peak observed memory of 4,069 MiB. It was
also observed at 9 to 10 percent twice, between arms, and refilled both times.
**Memory was never the binding constraint and it is honest to say so**: g64 uses
about 630 MiB and g128 about 3 GB, so a 98 GB card cannot be filled by this
scene at any grid reached. Utilization, not capacity, was the thing worth
raising, and concurrency rather than a bigger grid is what raised it.

**Completed:** M1 (matrix g64, 5 seeds, 100 runs), M2 (matrix g96, 2 seeds, 40),
M3 (5 arcs x 9 angles, 45), M4b (still-water edge, 5 cells x 5 seeds, 25), M5
(5 arcs x 9 angles x 5 seeds, 225), M6 (g128 arc, 9), M7 (bc guard control, 20),
M8 and M9 (g96 arcs x 4 seeds, g128 arc seed 1, 45), and two BC-frequency
controls (18). **694 records in the committed TSV, 532 runs added this session.**

**Did not complete:** nothing that was left running. The one arm killed was
killed deliberately, the first M4, whose shared labels made each invocation
overwrite the last.

**Continues after this window:** batch job **922514** on `c634-111`, four hours
on the `gh` production partition, verified before submission to checkpoint at
invocation granularity and to put **five seeds on g128**, which was the only
n=1 rung. It also runs ten further matrix seeds, a g160 arc, and the Silverado
mesh-fidelity control.

## T20. A moving car, as a renderable sequence, and why it is NOT a measurement

Josie asked for a video of a moving car. d13-renders has a working Cycles scene
but every frame so far is a stationary hull, which is not the research question.
The data for motion has to come from here, because every arm above is a
**rest-frame** run: the hull is fixed and the water carries the relative
velocity. That is correct for a load measurement and it renders as a stationary
car sitting in a current.

**Ground frame is the right frame for a video and the wrong frame for a number.**
`start_motion()` hands the hull its prescribed velocity and the collider
translates, so the car actually drives. But the ground frame **failed this
study's own C4 frame check at 34 percent**, with an undeveloped stream among its
confounds. **No force from the render runs may be quoted as a measurement.** The
load surface is built from the rest-frame arms and nothing here changes it.

### Two driver additions, both additive and both default-off

- **`--lim`**, a domain override. The computed rule sizes the box to the hull,
  which is right when nothing translates. In the ground frame it leaves the hull
  **3.16 m** of travel, which at 2.2 m/s is 43 frames, or 1.4 seconds. The
  driver already refuses such a run with `REFUSED_TRAVEL` rather than silently
  driving into a wall, so the limitation was known and guarded; it just could
  not be lifted. `--lim 22.0` at `n_grid` 160 gives dx **0.1375 m**, which is
  FINER than the g64 baseline's 0.1472, and **15.87 m** of travel.
- **`--dump-frames`**, the per-frame field. The tidy record is one row per RUN
  and cannot be rendered. This writes `FRAMES_<label>_g<n>.npz`: water positions
  and hull centre every frame, in float32, plus the domain, dx, depth, floor,
  frame dt and both speeds so a renderer can place the scene without
  re-deriving any of it. Off by default because it is hundreds of megabytes and
  no measurement needs it.

### This also fixes d13-renders' structural artifact

d13's renders show road patches floating on an infinite mirror because each
vehicle's **simulation domain is smaller than the camera frame**. The render
runs use a 22.0 m domain against the 9.42 m the rule produces, so the water
extends well past any reasonable frame. The two jobs supply the motion and the
larger domain together.

### Submitted

Job **922582**, `r9_render_motion`, 90 minutes on `gh`, two cells at depth
0.30 m, `v_water` 1.0 m/s, seed 0, `n_grid` 160, `lim` 22.0:

| cell | v_car | frames | video at 30 fps | travel needed |
|---|---|---|---|---|
| A | 2.2 m/s (5 mph, a realistic fording speed) | 150 | 5.0 s | 11.0 m |
| B | 4.5 m/s (10 mph) | 100 | 3.3 s | 15.0 m |

Both fit inside the 15.87 m available. **It runs a SEPARATE driver file**,
`simulation/moving_vehicle_render.py` on the node, md5
`d052005287ec9ae421d2a3f2fd6a33e2`, because batch 922514 was already running
against `moving_vehicle_channel.py` at md5 `3ea7c487a25ec52a9279c53cd18747e6`
and overwriting a driver mid-flight would split the provenance of the runs it is
collecting. The batch copy was verified unchanged after the render copy landed.

## T21. C-16 fixed: absence was being printed as a measured zero

`moving_vehicle_channel.py` printed `rec["fz_settle_over_analytic"] or 0.0`, so
a `None` on an OK cell rendered as `fz_settle/analytic 0.0000`. **A printed
0.0000 there is not a missing value, it reads as a measured zero vertical
reaction**, which would be a startling physical claim. It is a console line and
never a verdict, and the `status != "OK"` branch already skipped, so the blast
radius was small. It is fixed anyway because it is the manufacture-a-value shape
that produced most of this round's instrument failures, and it was sitting in my
own file while I was writing up two other instances of it.

**The input that makes the old line fail:** an OK cell whose
`f_buoy_analytic_N` is 0.0, which sets `fz_settle_over_analytic` to `None` where
the record is built. The old line printed `0.0000`; the new one prints `n/a`.

## T22. C-19: the corroboration of 4.7e-6 is narrower than it reads

Slot d18-platform lists among its independent verifications that "the fixed-seed
repeat spread reproduces d17's stated 4.7e-6 at 4.687e-6". **That verification
is correct and it is not evidence for the general claim.** It reproduces the
figure in the regime where the figure holds, the no-forcing control, which is
exactly the regime T11 shows is unrepresentative. Neither session is wrong; the
corroboration is narrower than its wording, and a reader would take it as
confirming a general determinism claim that T11 refutes.

**It also touches C-1 quantitatively, and the error bars there should widen.**
d18 argued the settled-window inversion is not noise, using a per-cell seed
spread of 0.066 to 0.338 percent. The nondeterminism measured in T11 is 0.0764
percent at `|v_rel|` 3.0 and 0.3876 percent at 4.5, **comparable to or larger
than the spread quoted**. The conclusion is untouched, because 2.262 against
0.912 is not a fraction-of-a-percent effect, but the uncertainty attached to it
was understated.

**"Seed noise floor" is now "total repeatability floor" in this document and in
`report_seeded_surface` itself**, not only in a commit message, because the name
was doing the misleading and the name is what people copy.

## T23. A crowned road against a flat plane, submitted with its gate first

The 105-paper realism search reports that **no retrieved study quantifies a
crowned or cambered road against a flat plane**, while ranking bed friction and
watertightness as the things that do move an incipient-motion verdict, and
finding **no** study where air entrainment, spray, surface tension, turbulence
closure, reduced sound speed or outlet-boundary choice flips one. So the crown
is unclaimed ground with a named gap behind it, and the numerical sound speed,
which was the tempting thing to fix, is not.

### What varies, and what deliberately does not

**Only the cross slope.** `road_geometry.road_profile` (tracked, committed at
`1e6732b`, owned by another slot and read-only from here) also carries gutters
and kerbs, and a 0.15 m kerb is a wall that ponds water. Including it would
confound three features and could not answer the question, so the carriageway is
widened to the whole domain and gutter and kerb are switched off. The profile
then reduces to a pure crown.

**The axes are the real ones.** The crown runs along the centreline in x, which
is the axis the WATER crosses, so the water must climb it; the car drives along
y, that is ALONG the road. Dropping the road module in unrotated would have put
the crown 90 degrees out, so that the car drove across the road's width and the
water ran along its length.

**The water surface is level and the DEPTH varies.** That is the entire point of
a crown and the only mechanism by which it could matter: the centreline is
shallower than the edges. Depth is 0.30 m at the edges and the crown removes
`cross_slope * lim / 2`, which is 0.094 m at 2 percent and 0.188 m at 4 percent.
Seeding a constant-depth film over the profile instead would drape water on the
road and destroy the effect being measured.

### The equivalence gate, and why it is not a formality

`--road-cross-slope 0.0` is **not** the same as omitting the flag. Omitting it
takes the scalar clamp, which is byte-identical to every run made before the
road existed. Passing `0.0` takes the **array** clamp with a flat profile. If
the array plumbing is wrong, the gate disagrees with the committed flat arm
`M5m3.0s*` at identical settings and everything after it is void. It is phase 0
of the job and it costs 27 runs against an existing baseline, so it needs no new
control of its own.

### Two selftests, each naming the input that makes it fail

- **ST14, the crown must be a crown.** The failing input is a sign error in
  `crown_profile`, returning `z - 0.5*slope*lim` instead of `z + ...`. That
  turns the road into a **trough** that is deepest on the centreline, ponding
  water exactly where the vehicle sits. It would look like a physical result
  rather than a bug, because a dished road really does hold more water.
  **Verified to fire**: the mutant raises `AssertionError: crown height wrong`
  while the real file passes.
- **ST15, the array clamp.** The failing input is `w[below, 2] = z_floor` in the
  array branch, which broadcasts the whole floor array into the selected rows.
  The test also asserts a constant array reproduces the scalar path exactly, so
  the backward-compatibility claim is checked rather than asserted.

### Submitted, not yet analysed

Job **922593**, `r9_crowned_road`, one hour on `gh`: the `|v_rel|` = 3.0 arc,
9 angles, three seeds each at cross slopes 0.0 (gate), 0.02 and 0.04, 81 runs at
g64. **No result is claimed here.** If the gate fails, the arm is void and that
is what will be reported.

**One thing the node did not have.** `road_geometry.py` was absent from the
node. The guarded import means a crowned run would have **raised** rather than
silently running on a flat floor, which is what the guard is for; the module was
shipped read-only and its own selftest passes there, 8 checks.

## T24. Review status of every number in this document: UNREVIEWED

**No adversarial subagent reviewed any claim here, and none could have.** The
fleet audit measured 20 `Agent` calls across 18 transcripts with **zero**
successes: every attempt hit the same pinned model id, and the three transcripts
showing no errors are exactly the three that never attempted one. This project
BUILT the control the corpus recommends, `.claude/agents/physics-skeptic.md`,
and ran a whole round with it silently dead.

So, stated plainly rather than left to inference: **every percentage, force,
verdict count, distance and ratio in this document is UNREVIEWED by an
independent checker.** What they do have instead, and it is not nothing:

- every headline number is regenerated from the committed TSV by
  `analysis/r9_speed_surface.py --from-tsv`, on stdlib alone, with no GPU;
- the two claims that could be attacked cheapest were attacked deliberately and
  one of them died: I proposed a BC-rate confound for the g128 collapse and a
  held-fixed control refuted it (T15), and the 2.3x pair was withdrawn (T17);
- three separate results were withdrawn or narrowed by my own controls rather
  than by a reviewer.

That is self-checking, and self-checking is weaker than review. It should not be
described as review.

## T25. The bc guard is STILL UNFIXED, and here is the spec for fixing it

To be unambiguous, because a readout has already described it as fixed: **I did
not fix the bc guard.** T13 reports it and says explicitly that the fix belongs
in the driver and was deliberately not applied, because batch 922514 was
mid-flight against that file and changing a driver under a running job splits
the provenance of the runs it is collecting. It is still self-bypassing today.

The register's new rule is that any commit adding a check must name the input
that makes the check FAIL. Applied to the guard as it should be rebuilt:

**The fix.** Re-check the constraint AFTER the snap that divides the substeps,
or make the snap round UP to a legal value instead of down.

**The input that makes the FIXED guard fail, i.e. the case it must reject and
the current one accepts:** g64 with `substeps` 11, `bc_per_frame_auto` 5, and a
caller passing `--bc-per-frame 5`. Today: the pre-snap check sees 5 >= 5 and
passes, then `sub_per_tick = ceil(11/5) = 3` and `bc_per_frame = ceil(11/3) = 4`,
so the run proceeds at applied 4 against an auto of 5, silently. A correct guard
must reject that, or lift it to 6, which is the next value giving
`sub_per_tick = 2` and applied 6.

**The regression that proves the fix is not vacuous:** the same call must still
be ACCEPTED at `bc_per_frame_auto` 4 or lower, where applied 4 is legal. A guard
that rejects both is not stricter, it is broken, and it would have refused the
whole `v_car` 6.7 m/s row, which ran legally at applied 4 against auto 4.

**Blast radius, measured not assumed:** exactly the four `v_car` = 8.9 m/s cells
of the g64 matrix, 20 runs across five seeds. The g96 arm is unaffected, applied
8 against auto 7. The measured cost is bounded at 1.471 percent (T13).

## T26. The video: frames verified, and a render defect that was NOT a physics defect

Job 922582 COMPLETED, ExitCode 0:0, 36:43 elapsed. **The frame counts were
verified from the arrays, not from the exit code**, because an exit code cannot
tell you a dump is short:

| cell | v_car | frames requested | frames in `frame_index` | contiguous | `water_xyz` |
|---|---|---|---|---|---|
| A | 2.2 m/s | 150 | **150** | yes, 1 to 150 | (150, 352844, 3) |
| B | 4.5 m/s | 100 | **100** | yes, 1 to 100 | (100, 352844, 3) |

**No frame is missing, so nothing was renumbered.** Four further checks, all
passing, none of which the exit code covers:

- **The car actually moves.** Hull y goes 3.1771 to 14.1039, travel **10.9267 m**
  against a predicted `v_car * n * dt` of 11.0000 m. The 0.073 m difference is
  exactly one frame step: travel spans 149 intervals, not 150.
- **It drives straight.** Hull x and z spans are **exactly 0.00e+00**, which is
  the signature of a prescribed body and would not hold for a free one.
- **The step is uniform**, 0.073333 to 0.073334 m per frame.
- **No particle leaves the domain**, 0 of 52,926,600 positions outside in x or y.

### The defect the picture exposed, and it was in the picture

The first render drew the vehicle in elevation from `hull_center_z - ext_z/2`,
which put **0.76 m of the car underneath the roadway**. It looked like a physics
bug and it was not one.

`canonicalize()` shifts the mesh by `[(lo+hi)/2, (lo+hi)/2, lo[2]]`: x and y are
centred on the bounding box, but **z is shifted so the mesh minimum sits at 0**,
so the hull's origin is its UNDERSIDE. A collider centre at `z = floor`
therefore puts the wheels on the road, which is correct, and is verbatim the
convention `sim_standing.py` uses. The renderer assumed a centred origin.

This is the more dangerous way round. **The physics was right and the picture
was wrong, and the picture is what people believe.** Fixed, and the comment in
`r9_render_frames.py` records why.

### The caption is on the frame, not in a README

A rendered fluid image is the most persuasive artefact this project makes and
the least self-describing: nothing in a picture of water says which parts came
out of the solver. Every frame names three categories separately, following
d13-renders' pattern:

- **SOLVER**: water particle positions and hull pose, warpmpm MPM and not
  Genesis, 352,844 particles, n_grid 160, dx 0.1375 m.
- **MEASURED**: v_car and v_water on perpendicular axes, depth, domain, frame
  dt and the hull travel, all read from the npz rather than retyped.
- **DRAWN**: colour, camera, scale, and the vehicle as its **bounding box**,
  because the dump carries the centre and extents but not the mesh.

And the run's own warning travels with it, in red, on every frame: **this is a
ground-frame sequence, it failed C4 at 34 percent, it is a VISUALISATION and no
force from it may be quoted.** A caption in a README travels separately from the
file and does not get read.

### Two rendering choices that are not cosmetic

- **Particles are sorted by height before drawing.** Unsorted scatter paints in
  array order, so whether spray is visible depends on particle indexing rather
  than on height, and splash vanishes behind bulk water at random.
- **Colour limits are fixed across the whole sequence** and anchored to the still
  surface. Autoscaling per frame is the classic way to make still water look
  like it is surging: the colour of a given height would change frame to frame
  and the eye reads that as motion that is not in the data.

### Encoding refuses to hide a gap

The encode uses ffmpeg's `concat` demuxer over an explicit file list, not
`-start_number` with a glob. The image2 demuxer **stops at the first missing
index**, so a gap would silently produce a shorter video that still looks
continuous, which is exactly the failure that reads as a jump in the physics
rather than as a missing file. The job also prints `PNG_COUNT` per cell so the
count is checkable after the fact.

### Walltime, sized from measurement

One frame renders in about 1.5 s measured on the node, so 250 frames across both
cells is about 7 minutes. The encode job asks **25 minutes**, that plus a margin,
rather than the hour a guess would have taken.

### T26a. Encoding on Vista: three failures, and one of them writes a file

The videos exist. Getting them out took three distinct failures worth recording,
because the first two both LOOK like success.

**1. `/usr/bin/ffmpeg` is on the PATH and does not run**, on the login node and
on a `gh` compute node alike: `error while loading shared libraries:
libunwind.so.8`. My tooling check was `which ffmpeg`, which passed. That is
presence mistaken for function, and it is the same shape as the round's other
instrument failures. The working binary is the static build bundled with
`imageio_ffmpeg`.

**2. My own script reported success it never had.** The sbatch ran
`ffmpeg ... 2>&1 | tail -3` and then `echo "RC=$?"`, which captures the exit
status of **`tail`**, not of ffmpeg. So the log printed `RC=0` and
`ENCODE COMPLETE` while Slurm recorded the job **FAILED, ExitCode 2:0**, and no
mp4 existed. A pipeline's `$?` is the last command's.

**3. libx264 fails on this ARM build unless threading is forced off.** It reports
`using cpu capabilities: ARMv8 NEON SVE SVE2`, then `Error while opening
encoder`, and **writes a zero-byte mp4**. `-threads 1 -x264-params threads=1`
fixes it. Note the failure mode: a check that tested only whether the output file
existed would have passed on an empty video.

Also: use the image2 **glob** reader, not `-f concat`, which expects timestamped
streams and gives images invalid PTS; and never `-start_number` with a numeric
pattern, which stops at the first missing index and silently yields a shorter
video that still looks continuous.

### The delivered files, counted twice on two machines

**CORRECTED: this table named two filenames that exist nowhere on the node.**
The names below are the artifacts as WRITTEN by the job; the third column is the
name each was given when delivered to Josie, which is where the earlier, wrong
names came from. Same bytes, two names, and a reader following the old table
found nothing.

| on Vista, `out/` | frames | duration | size (bytes) | delivered as |
|---|---|---|---|---|
| `r9_RENDvc2p2.mp4` | **150** | 5.000 s | 7,664,603 | `can_it_ford_moving_2p2ms.mp4` |
| `r9_RENDvc4p5.mp4` | **100** | 3.333 s | 5,810,911 | `can_it_ford_moving_4p5ms.mp4` |

Both 1280x960 at 30 fps. The PNG count and the encoder's own reported frame
count were compared on the node (`match=YES` for both), and the frame counts were
then re-derived on the Mac with a **different ffmpeg build** via
`ffprobe -count_frames`. 150 requested, 150 dumped, 150 rendered, 150 encoded.

---

# RESULTS, FIFTH BLOCK: the batch and the crowned road

Three jobs completed: **922514** `r9_speed_surface` (02:59:11), **922582**
`r9_render_motion` (00:36:43) and **922593** `r9_crowned_road` (00:07:31), all
ExitCode 0:0. The committed TSV now holds **1,137 records**.

## T27. YES, the crowned road IS the paired comparison the literature is missing

A deep search of 18 August states plainly that **no retrieved study quantifies a
crowned or cambered road against a flat plane**. The question asked of me was
whether job 922593 actually answers that, because an unpaired run would not.

**It is paired, and the flat side is measured, not assumed.** Every arm is the
same `|v_rel|` = 3.0 arc, 9 angles, 3 seeds, g64, 400 frames with 250 discarded,
`bc_per_frame` 5, depth 0.30 m, same hull, same domain, same seeds. **The only
thing that differs is the cross slope.**

| arm | cross slope | crown height | n_water | mean `\|F_h\|` | S | peak angle |
|---|---|---|---|---|---|---|
| `RDgate0` | **0.00, flat** | 0.0000 m | 41,648 | **3119.7 N** | 1.0703 | -67.5 deg |
| `RDs2p0` | 0.02 | 0.0942 m | 34,946 | **1979.8 N** | 1.1196 | |
| `RDs4p0` | 0.04 | 0.1884 m | 28,340 | **1563.6 N** | 1.5347 | |

**A 2 percent crown, which is the standard road camber, cuts the horizontal load
by 36.5 percent. A 4 percent crown cuts it by 49.9 percent.**

### The gate passed, and it did NOT pass exactly

`--road-cross-slope 0.0` runs the array clamp over a flat profile and must
reproduce the scalar-clamp flat arm `M5m3.0s*`. Measured, three seeds:

| seed | max abs. relative difference | mean |
|---|---|---|
| 0 | 0.159 percent | 0.045 |
| 1 | **0.254 percent** | 0.060 |
| 2 | 0.219 percent | 0.045 |

**I claimed this would be byte-identical and it is not.** Every recorded field
is identical between the two arms, `n_water` 41,648 on both, same dx, lim,
substeps, `substeps_effective`, applied `bc_per_frame`, `wrench_dt_s`, hull
placement and analytic buoyancy. So it is the same scene. But the worst
disagreement, 0.254 percent, is about **three times** the fixed-seed
nondeterminism floor of 0.0764 percent that T11 measured at this speed. The
extra array operations plausibly perturb accumulation order, **and I have not
isolated it, so it is reported as an unexplained residual rather than explained
away.** It is 140 times smaller than the crown effect it gates, so the arm
stands; a gate that had to resolve a 0.25 percent effect would not.

### The mechanism is mostly the obvious one, and saying so is the honest move

A crown makes the centreline shallower at a level flood surface, which is the
whole point of a crown. The water it displaces is measured, not inferred:
`n_water` falls **16.1 percent** at 2 percent slope and **32.0 percent** at 4
percent. So this is not a subtle hydrodynamic result, it is mostly "the vehicle
is standing in less water", and it should be reported that way rather than
dressed up. What makes it worth publishing is that **nobody has put a number on
it**, and the number is large.

**Two framings exist and this is one of them.** Holding the flood LEVEL fixed
and crowning the road, which is what a real road does, is the operational
question. Holding the depth AT THE VEHICLE fixed and crowning the road would
isolate the geometry from the depth. **This arm answers the first.** The second
is a different experiment and is not claimed here.

### A trap this created, flagged before anyone reads past it

`f_buoy_analytic_N` is **4468.62 N in all three arms**, because it is computed
from the nominal 0.30 m depth and the hull geometry, not from the water actually
present. On a crowned road the vehicle sits in 0.206 m (2 percent) or 0.112 m
(4 percent). **So `fz_settle_over_analytic` is not a valid buoyancy ratio for
the crowned arms** and must not be read as one. The flat arm is unaffected.

### What this is NOT

**No verdict, on either side.** The body is prescribed and cannot be swept away,
so the comparison is a paired LOAD comparison, not a paired verdict comparison.
Filling the literature's gap completely would need a free body, which
`RigidBody6DOF` refuses at a non-zero COM offset. A 36.5 percent load reduction
is large enough to matter to any threshold, but converting it into a FORD or
NO-FORD claim is exactly the step this document has refused throughout.

## T28. The resolution ladder does not converge, and now there are four rungs

The batch put five seeds on g96 and g128 and added g160.

| grid | seeds | S | mean `\|F_h\|` | peak angle | mean stream |
|---|---|---|---|---|---|
| g64 | 5 | 1.0681 +- 0.0026 | 3118.5 N | -67.5 deg | +0.744 |
| g96 | 5 | 1.0067 +- 0.0029 | 3109.1 N | -56.25 deg | +0.739 |
| g128 | 5 | 0.6075 +- 0.0010 | 1659.0 N | -22.5 deg | +0.902 |
| g160 | 2 | **0.4964 +- 0.0008** | **1127.8 N** | -22.5 deg | +0.930 |

**The load keeps falling and shows no sign of settling**: 3118, 3109, 1659,
1128. g64 to g96 moves it 0.3 percent, then g96 to g128 drops 47 percent and
g128 to g160 a further 32 percent. **This is not a converging sequence and no
convergence is claimed from it.** `stream_established_frac` rises monotonically
across the same ladder, 0.744, 0.739, 0.902, 0.930, which is the pattern T15's
control is consistent with and which the BC-rate explanation was refuted for.

**S falls with it**, 1.068, 1.007, 0.608, 0.496, so the SIZE of the
split-dependence is strongly resolution dependent. **Its existence is not**: even
at g160 the load varies by 50 percent at a fixed relative speed, against a
per-arm sd of 0.0008 and a fixed-seed repeatability floor of 0.0764 percent.
That separation is why the qualitative claim survives while every absolute
number in this document carries its grid.

## T29. Mesh density moves the answer too, by 5 percent on load and 21 percent on S

Same vehicle, same everything, two mesh densities, three seeds each:

| Silverado mesh | vertices | mean `\|F_h\|` | S | peak angle |
|---|---|---|---|---|
| coarse | 2,108 | 4273.1 N | 0.9274 +- 0.0006 | -56.25 deg |
| fine | 48,706 | 4490.8 N | 1.1248 +- 0.0026 | -67.5 deg |

A 23-fold increase in vertex count moves the load **5.1 percent** and S **21.3
percent**, and moves the peak angle. So the hull's mesh resolution is a third
axis of sensitivity alongside grid and BC rate, and the peak angle is unstable
under all three, which is the last nail in T14's withdrawal of it.

## T30. Where the remaining allocation should NOT go

The same search ranks realism effects by whether any retrieved study shows them
flipping a vehicle motion verdict. **No retrieved study shows air entrainment,
spray, surface tension, turbulence closure, reduced sound speed, or outlet
boundary choice flipping one.** The ten-times-flow-speed sound-speed rule **has
no primary derivation** in that literature; it is convention. What does have
threshold evidence is bed condition and friction, road slope and flow
orientation, and watertightness.

**This bears directly on where this project has been spending.** Considerable
effort has gone into the in/outflow boundary condition and the recirculating
outlet. That work is not wasted, and this document depends on the forcing being
sound, but the literature does not support treating outlet formulation as
verdict-critical, and it should stop being prioritised as though it were.

**All of T30 is secondary source. I have read none of those papers.**

## T31. The crowned road as a NOVELTY CLAIM, with the absence cited

This section restates T27 as a contribution rather than a diagnostic, because
the basis for the novelty claim changed after T27 was written.

### The absence, cited by source

An Undermind deep search commissioned **2026-08-18**, titled **"which realism
effects change a flood vehicle stability verdict"**, states that **no retrieved
study quantifies a crowned or cambered road against a flat plane.** Its goal text
describes this project's own configuration, down to the 0.15 m cell against
millimetre road texture and the c = 13 m/s sound speed.

**Two things make this a usable basis where this project's previous novelty
claim was not.** It is a documented absence from a search whose goal text anyone
can read and re-run, rather than an inference from silence; and it is not the
subagent-derived absence result this project already had to retract. It remains a
**secondary source**: I have not read the retrieved papers, and a search's
failure to retrieve is not proof of non-existence.

### The design, stated so a reader can see it is paired

Not a single arm. Three arms, and the flat side is **measured, not assumed**:

| held identical across all three | value |
|---|---|
| relative speed and sweep | `\|v_rel\|` = 3.0 m/s, 9 angles, broadside to axial |
| seeds | 0, 1, 2 (three per arm) |
| grid, domain | g64, `lim` 9.421742 m, dx 0.1472147 m |
| frames, discard, settle | 400, 250, 30 |
| applied `bc_per_frame` | 4 (auto 2) on every arm |
| hull, placement, flood level | Yaris, `hull_y` 4.710871 m, level surface at floor + 0.30 m |
| **the one thing that varies** | **cross slope: 0.00, 0.02, 0.04** |

### The result

| cross slope | crown height | mean `\|F_h\|` | change vs flat | S |
|---|---|---|---|---|
| 0.00 (flat) | 0.0000 m | 3119.7 N | reference | 1.0703 |
| **0.02**, the standard camber | 0.0942 m | **1979.8 N** | **-36.5 percent** | 1.1196 |
| **0.04** | 0.1884 m | **1563.6 N** | **-49.9 percent** | 1.5347 |

Every arm is three seeds. The per-arm seed spread on S is at the third decimal,
against differences in the first, so the ordering is not seed scatter.

### What the claim is, and what it is not

**Claimed:** at a fixed flood level, crowning the roadway at a standard 2 percent
camber reduces the horizontal hydrodynamic load on a stationary-to-moving vehicle
by 36.5 percent in this model, and doubling the camber roughly halves the load.
The comparison is paired and only the cross slope varies.

**Not claimed:** any verdict. The body is prescribed and cannot be swept away, so
this is a paired LOAD comparison and not a paired stability comparison. **Not
claimed:** that the effect is subtle. `n_water` falls 16.1 and 32.0 percent, so
most of it is the vehicle standing in shallower water, which is what a crown is
for. **Not claimed:** that the magnitude is grid-converged; T28 shows the ladder
does not converge and every absolute force here carries its grid.

**The decomposition is running now**, job 923302: the same crowns at depths
0.3942 m and 0.4884 m, chosen so the crown carries exactly 0.30 m and the depth
AT THE VEHICLE matches the flat arm. If those reproduce the flat arm's 3119.7 N,
the effect is entirely depth-at-vehicle; whatever they differ by is the bed
geometry. The prediction was written into the job script before it ran.

## T32. The crown decomposition, and it flips sign

Job **923302** COMPLETED, 00:06:28, ExitCode 0:0, 54 cells. 1,191 records.

T27 said most of the crown's benefit was probably "the vehicle stands in less
water", and offered the depth-matched comparison as the way to find out. It has
now run, and **the answer is more interesting than the prediction.**

Depth is measured from the floor, that is at the road edges, and the crown
removes `crown_height` from it at the centreline. Setting depth to
`0.30 + crown_height` therefore puts **exactly 0.30 m over the crown**, matching
the flat arm at the vehicle.

| arm | depth (edges) | crown | depth AT VEHICLE | n_water | mean `\|F_h\|` | vs flat |
|---|---|---|---|---|---|---|
| flat | 0.3000 | 0.0000 | **0.300** | 41,648 | 3119.7 N | reference |
| 2 pct, level fixed | 0.3000 | 0.0942 | 0.206 | 34,946 | 1979.8 N | **-36.5 pct** |
| 4 pct, level fixed | 0.3000 | 0.1884 | 0.112 | 28,340 | 1563.6 N | **-49.9 pct** |
| 2 pct, vehicle depth fixed | 0.3942 | 0.0942 | **0.300** | 45,129 | 2539.6 N | **-18.6 pct** |
| 4 pct, vehicle depth fixed | 0.4884 | 0.1884 | **0.300** | 58,733 | 3307.4 N | **+6.0 pct** |

### Three things, and the second one is the result

1. **The crown is not only depth.** At 2 percent, with the vehicle standing in
   exactly the same 0.30 m of water as on the flat road, the load is still
   **18.6 percent lower**. Roughly half of the level-fixed 36.5 percent survives
   the depth being matched.
2. **The depth-matched difference REVERSES SIGN between 2 and 4 percent**, from
   -18.6 to **+6.0 percent**. A single monotone mechanism cannot produce that.
   Whatever the crown does, it is not one effect scaling with camber.
3. **The level-fixed benefit is real and large at both cambers**, -36.5 and
   -49.9 percent, and that is the operational question: a flood has a level, and
   the road either has a camber or does not.

### The honest name for the second column, which is NOT "the geometry term"

I set this up calling the depth-matched difference the geometry term. **That name
is wrong and I am not keeping it.** Holding the depth at the vehicle fixed
necessarily makes the flood DEEPER AT THE EDGES: 0.3942 m and 0.4884 m against
0.30 m, and `n_water` rises to 45,129 and 58,733 against 41,648. So the
depth-matched arm changes the bed shape **and** puts more water in the domain,
and the 4 percent case has 41 percent more water than the flat reference. That
extra water at the sides is the obvious candidate for the sign flip.

**Neither framing isolates bed geometry alone.** They bracket it. A clean
geometry term would need a third design that holds both the vehicle depth and
the total water fixed, which is not possible on a fixed domain without changing
something else, so it is not claimed and was not attempted.

### What is safe to say

- At a fixed flood level, a standard 2 percent camber reduces the horizontal load
  by **36.5 percent**, and 4 percent by **49.9 percent**. Paired, three seeds,
  only the cross slope varying.
- **Most but not all of that is the shallower water at the vehicle.** At 2
  percent, 18.6 of the 36.5 points survive matching the vehicle depth.
- The residual is **not monotone in camber** and is confounded with the extra
  water the depth-matched design introduces.
- All of it carries the grid caveat of T28 and none of it is a verdict.

## T33. C-1 finished: the placement confound is CLOSED, and the pair still inverts

d18-platform named one confound it could not close, and it was the right one to
name: the settled side of the C-1 comparison records `hull_y_m`, and the
transient side is `c3full`, whose `hull_y_m` is empty because it predates the
field. **If `c3full` had placed the hull differently, the inversion would be
placement and not window**, and every conclusion drawn from it would be wrong.
Noting that is not closing it. So it was measured.

Job **923314** re-ran the TRANSIENT window on an arm that records its placement,
at the same grid, seeds and `bc_per_frame` as the settled arm, so the two differ
in the window **and nothing else**:

| window | arm | `hull_y_m` | applied bc | seeds | (2.20, 3.00) | (4.50, 0.50) | ratio |
|---|---|---|---|---|---|---|---|
| transient | `c3full` | **EMPTY** | 2 | 1 | 8621.4 N | 3811.1 N | 2.262 |
| transient | **`WTrans`** | **4.710871156863869** | 4 | 3 | 9253.3 N | 3848.8 N | **2.404** |
| settled | `L2full` | 4.710871156863869 | 2 | 1 | 5028.4 N | 5534.7 N | 0.909 |
| settled | `M1` | 4.710871156863869 | 4 | 5 | 5176.5 N | 5675.3 N | **0.912** |

**The confound is closed and the conclusion is unchanged.** With placement
recorded and IDENTICAL on both sides and the same applied bc, the transient
window gives 2.404 and the settled gives 0.912. **The ratio still crosses one.**
`WTrans` also reproduces `c3full` to within 6 percent, and the two differ in bc
(4 against 2), so `c3full` was not anomalous, merely under-recorded.

Note in passing that the settled side is insensitive to bc, 0.909 against 0.912,
while the transient side is not, 2.262 against 2.404. A transient window is more
sensitive to a numerical parameter as well as to its own length, which is a
further reason not to publish from one.

The prediction was written into the job script before it ran: "I expect a ratio
above 1, near c3full's 2.262". It came out at 2.404.

## T34. The classification question: a load ratio is d15's THIRD class, and here is the rule

The question put to me was which of d15-settle's two classes a load ratio is:
**full record for a verdict, demonstrated-stationary window for a convergence or
uncertainty claim.** It is neither, and forcing it into either would be wrong.

- It is **not a verdict**. Nothing moves or fails to move; the body is prescribed.
- It is **not an uncertainty or convergence claim**. It is not an error bar and
  not a refinement statement.

It is a **COMPARISON**: an ordering between two conditions, of the form "A carries
more load than B". That is a third class and d15's rule does not cover it.

### The rule I propose for the third class

> **A comparison must be reported over a window in which the ORDERING is stable,
> and the stability must be shown at more than one window, not assumed. If the
> ordering flips between windows, the comparison is not a result: report it as
> window-dependent with both values named, and do not resolve it to one.**

The load ratio fails that test, so under this rule it does not get restated as a
single number at all. **The correct handling of the C-1 pair is therefore neither
"2.3x" nor "0.912x" but "2.404 transient, 0.912 settled, and the ordering is not
a property of the scene".** That is what T17 withdrew it to and this is the rule
that justifies the withdrawal rather than just performing it.

### Why the general result is in a different position, tested rather than asserted

The obvious worry is that if the pair fails a window change, the headline should
too. It was tested on the same scene at the same two windows:

| window | frames kept | S at `\|v_rel\|` 3.0 | seeds |
|---|---|---|---|
| transient, 60/20 | 40 | **0.8886 +- 0.0033** | 5 |
| settled, 400/250, bc 2 | 150 | **1.1776 +- 0.0016** | 5 |
| settled, 400/250, bc 4 | 150 | **1.0681 +- 0.0026** | 5 |

**S moves with the window, by 20 to 32 percent, and its conclusion does not.**
In every window the load varies by 89 to 118 percent at a fixed relative speed,
against a repeatability floor of about 0.08 percent. The claim "the split
matters" is true in both windows; the claim "this cell carries more than that
one" is true in one and false in the other.

**That asymmetry is the whole reason S is the result and the pair never should
have been.** S is a spread over a whole arc at exactly fixed relative speed, so a
window change rescales every cell it compares together. The pair is two cells
that differ in BOTH speeds and in `|v_rel|`, compared across a product grid,
which is the fragile construction. The magnitude of S still carries its window
and its grid, exactly as T28 requires.

## T35. The R5 surface table is the TRANSIENT surface, and its settled twin exists

Broader than the pair, and worth stating separately because a reader looking at
R5 sees a 20-cell surface with no window warning on the cells themselves.

**The R5 table is `c3full`: 60 frames with 20 discarded.** Its settled-window
twin is the `L2full` arm at 400/250, which is in the shipped TSV and was not
tabulated anywhere. Four cells, to show the size of it:

| cell | R5 as published (transient) | `L2full` (settled) |
|---|---|---|
| (2.20, 3.00) | 8621.4 N | **5028.4 N** |
| (4.50, 0.50) | 3811.1 N | **5534.7 N** |
| (6.70, 0.50) | not comparable, see below | 9577.9 N |
| (8.90, 3.00) | 42221.0 N | **30211.8 N** |

**The settled surface with five seeds is already published in this document, in
T1**, and T1 supersedes R5's table for every purpose. R5 is retained as the
record of what was originally claimed, with its withdrawal note, and should not
be read as a current result. Anyone quoting a force from R5 is quoting a
transient-window number from a single seed.
