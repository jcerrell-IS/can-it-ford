# WHY THERE IS NO REALISTIC ENVIRONMENT YET, AND THE PLAN TO BUILD ONE
2026-08-14 23:47 CEST. Every claim below is sourced to a file read live tonight
or to a run that executed tonight. Nothing here is recalled.

Josie asked directly: why have we not made a realistic environment. The answer is
not neglect. It is five specific blockers, four of which are now measured.

## THE ANSWER, FIVE BLOCKERS

### B1. The scene is a flat plane inside a box. That is the entire environment.

CLAUDE.md item 3, from primary source read of `sim_standing.py`: the only
constraints are a **floor plane at friction 0.55** and **four slip walls at
friction 0.0**. There is no terrain, no road camber, no crown, no curb, no
gutter, no gradient, no drain, no embankment. The "road" is an infinite
frictional plane.

### B2. The grid is forced cubic, so a road cannot be expressed.

warpmpm forces a cubic domain. A road is long, thin and shallow. A cube spends
almost all of its cells on empty air above the vehicle in order to buy resolution
across the floor layer. This is why `grid_lim` comes from the loaded hull's
extent, and why a cross-vehicle run at fixed `n_grid` silently changes both dx
and realized depth.

### B3. A bounded domain physically cannot measure a slope. Tilting the floor does not work.

D10 established this tonight and it is the deepest of the five: **conserving
volume in a bounded domain forces redistribution larger than the effect being
measured.** Water that runs downslope has nowhere to go, so it piles at the wall
and the pile is bigger than the signal. You cannot get a road-realistic slope by
tilting the floor of a sealed box, no matter how fine the grid.

D10's own arms quantify the consequence: excursion grows with slope in the
downslope direction, **0.664, 0.937, 1.562 m** at increasing slope. A margin
sized at S=0 is wrong by **2.35x** at S=0.06.

### B4. The correct instrument is wired but never validated.

The fix for B3 is an open channel with a **real mass sink**: inflow at one end,
outflow at the other, so water leaves the domain instead of piling. That is
Zhao, Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179, 27-33,
DOI 10.1016/j.compfluid.2018.10.007, implemented in Anura3D. Per CLAUDE.md this
is a **translation** into warpmpm, not a port.

D10 wired it. **Nobody has ever validated it.** So the one component that unlocks
a realistic domain has no known error bar. That is the single highest-leverage
unblocked task in the project and it is running now.

### B5. The literature has not solved it either, so this is a contribution, not a catch-up.

Undermind multi-resolution report, quoted verbatim from
`01_Solver_Physics_and_Coupling/2026-08-14_undermind-report_multi-resolution-mpm-large-domain-flooding_CURRENT.md`:

> "no demonstrated MPM study was found that follows a rigid vehicle with a
> refinement window through a large flood domain"

The closest fluid result is dynamic AMR for free-surface waves and breaking
**without a vehicle**. Adaptive MPM-FSI work is "preliminary and not road-scale
flooding". Nested-grid GIMP, structured GIMP refinement, mesh grading,
hierarchical B-spline MPM and local BSMPM bridging are **solid-only**.

The report also names the trap directly: sparse active grids and dynamic meshing
cut memory when the domain is empty but **do not reduce the smallest-cell
explicit timestep and do not resolve the floor layer**. So "just make the domain
bigger and sparser" does not buy the thing we need.

And its reference [4] is decisive, which is the same finding D9 tested tonight:
fixed particles-per-cell can lose convergence under refinement, so AMR silently
changes quadrature unless PPC is co-refined.

### B5b. The alternative architecture has terrain natively, and its terrain is measurably broken here.

Chrono ingests OBJ and heightfield terrain through `RigidTerrain::AddPatch`, which
is exactly the realistic-environment capability warpmpm lacks. D13 built it on
GH200 in 94 s and returned a GO on architecture.

But D13 measured `RigidTerrain::GetNormal` on Vista aarch64 over 10,800 samples:

    ON-VERTEX   3600 samples   3600 bad   100.0%   worst 88.85 deg
    ON-EDGE     3600 samples      0 bad     0.0%   worst  1.02 deg
    INTERIOR    3600 samples      0 bad     0.0%   worst  1.09 deg

A heightfield puts its vertices on a **regular grid**. So a 100 percent failure
rate on vertex hits means terrain contact is unreliable at exactly the points a
realistic road surface is sampled, with a worst-case normal 88.85 degrees off,
essentially perpendicular to correct. D13 traced the origin to Bullet's trimesh
raycast callback, not to Chrono, which populates it correctly from
`ChCollisionSystemBullet.cpp:402-403`.

D11 is running the x86 reproduction now. Either answer closes it.

## THE PLAN, IN DEPENDENCY ORDER

Nothing below is optional-looking busywork. Each step unblocks the next.

**Step 1, running now, D10.** Validate the Zhao 2019 open BC. Still-water column
with outflow open against its analytic mass-loss rate, then steady inflow equal
to outflow where the free surface must hold a constant level. Report the achieved
tolerance, because every later slope result carries it. **Until this has an error
bar, no realistic-domain result is quotable.**

**Step 2, running now, D11 for D13.** Settle whether the Chrono terrain-normal
defect is general or aarch64-specific. This decides whether the realistic
environment is built in warpmpm with a translated BC, or in Chrono with native
terrain plus a documented caveat and rigid or FEA tyres, which per D13 go through
the contact engine and never consult `GetNormal`.

**Step 3, after step 1.** Open-channel road segment: inflow, outflow, a real
cross-slope. D10's `required_patch_margin_m` already extrapolates rather than
clamps, 31/31 tests pass, so the margin logic is ready for a real patch.

**Step 4, after step 3.** Terrain that is not a plane. In order of cost: constant
cross-slope, then crown plus gutter, then a reconstructed surface. Note register
E8: derived hull and reconstructed geometry never reach the public repo or a
DesignSafe DOI.

**Step 5, the honest limitations either way.** From the moving-rigid-body report,
quoted: "no validated vehicle-fording MPM chain is identified", and the records
"do not establish an experimental basis for the 1.5 m/s rule". Whatever we build,
those two sentences stay in the paper.

## WHAT THE RESEARCH SAYS TO USE WHEN BUILDING IT

- **Validation targets that exist, with numbers.** Total-head criteria of 0.3 m
  for passenger cars and 0.6 m for emergency vehicles, and separately a simulated
  critical depth 0.38 m with minimum depth x velocity 0.39 m2/s. **Still-water
  depth limits must never be conflated with depth-velocity products.** One public
  benchmark carries approximately **0.3 percent experimental uncertainty** and is
  the right locked regression case.
- **Unsteady flow raises drag 40 to 50 percent** (Azhar 2026) and is not
  modelled. A realistic environment makes the flow less steady, not more, so this
  grows rather than shrinks.
- **Class-specific geometry, not mass alone.** Buoyancy, drag and lift lever
  arms, wheel normal loads and sliding thresholds depend on displaced volume,
  underbody shape, wheelbase, track and CoM. D5 has already executed the fix
  with real Rogue and Silverado hulls at matched dx.
- **Settling has no threshold, only a protocol**: exclude transients, demonstrate
  stationarity for the reported observable, attach uncertainty from correlated
  samples via autocorrelation, blocking or bootstrap. A longer, more complex
  domain makes the transient longer, so this becomes mandatory rather than nice.
- **Order-dependent reductions can alter discrete gates.** A SLIDE / STUCK /
  FLOAT verdict is exactly such a gate. Use reproducible reductions.

## TONIGHT'S RESULTS THAT CONSTRAIN THE BUILD

- **PPC is refuted** as the non-monotone mechanism (D9, run tonight). Band width
  is dominant, `COLLIDER_FRICTION 0.4` influential. So AMR in a realistic domain
  must control band width, and co-refining PPC alone will not save it.
- **J15 needs two qualifiers**, its mu and a **realized-depth confound** nobody
  had recorded (D1, `92088f1`). Any multi-vehicle realistic scene must hold
  realized depth fixed by construction, as D5's matched-dx design does.
- **The noise floor does not transfer between statistics**: 0.11 to 1.21 percent
  on `ratio_slide`, 19 to 26 percent on `k_crit`. Name the statistic.
- **mu = 0.55** is Azhar, Pauwels and Bui 2023's own spring-balance measurement
  of their experimental rubber mat, against the 0.3 convention which is Bonham
  and Hattersley 1967 carried forward, an 83 percent difference in T_avail. A
  realistic road surface is the one place this stops being a constant and becomes
  a field.
