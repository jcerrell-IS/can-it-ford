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

<!--RESULTS-->

*Nothing below this line yet. Results are appended after the runs, and any
criterion changed after this point is recorded as a change.*
