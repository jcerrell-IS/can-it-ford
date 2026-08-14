# Research briefs for the realistic moving-vehicle environment, 2026-08-14

Eight paste-ready research prompts, one per measured limitation blocking the forked
track, each matched to a specific AI research tool.

**Tool matching authority.** `compass_artifact_wf-62a7f8e6-d07d-5c14-b7f0-3400f917afbe`,
"AI Research Tools & Scientific-Computing Infrastructure to Accelerate Can It Ford",
27,153 bytes, in `/Users/josie/Downloads/`. Note that
`docs/RESEARCH_ARTIFACT_INTEGRATION_2026-08-07.md` section 3.5 lists this artifact id
under "Workflow and tooling reports, no repo science ... Not integrated, deliberately."
Its recommendations have therefore never been applied. This document applies them.

---

## Tool selection, and why each

Taken from the artifact's own characterisations, cross-checked against what is actually
connected in this Claude session.

| Tool | The artifact's verdict | Live now? | Use it for |
|---|---|---|---|
| **Undermind** | "deep semantic search that adapts dynamically; **among the tools least likely to fabricate references**" | **yes** | The methods questions where a wrong citation is expensive. RB-1, RB-2, RB-4, RB-5, RB-7 |
| **DeepWiki** | "**the standout code-adjacent tool**", MCP-native, indexes any public GitHub repo | **yes** | How a specific engine actually implements something. RB-3, RB-6 |
| **Consensus** | not in the artifact; live here | **yes** | Fast yes/no on whether a claim has support, as a cheap pre-filter before an Undermind run |
| **Scite** | "Citation integrity has matured into a dedicated tool class" | **yes** | Verifying every DOI before it is written as settled. RB-8 |
| **Scholar Sidekick** | not in the artifact; live here | **yes** | Catching the real-DOI-wrong-title fabrication pattern. RB-8 |
| **Wolfram** | project standing rule | **yes** | Any unit, scaling or CFL arithmetic before it becomes a claim |
| **Elicit** | "systematic-review-grade synthesis, **data extraction into tables**, ~94% extraction accuracy, Research Reports up to ~80 papers" | **no, needs auth** | RB-5's comparison table. Authorise it in claude.ai connector settings first, or fall back to Undermind |
| **OpenAlex / Connected Papers / Litmaps** | "free programmatic backbone" plus neighbourhood mapping | web, not MCP | One-off breadth checks; not needed for these eight |
| **NHTSA vPIC, USGS Water Data** | "free public REST API" | web/API | RB-8 is a data pull, not a literature search |

**The division of labour that matters.** Undermind for *what is known and what is not*,
DeepWiki for *how this specific code behaves*, Scite plus Scholar Sidekick for *is this
citation real*. The artifact is explicit that DeepWiki's summaries are LLM-generated and
"the source file is the final authority for micro-questions", so every DeepWiki answer is a
hypothesis to verify against source, never a fact.

**Two standing warnings to paste into every brief below.**

1. The Australian small-car limit is a limiting **still-water depth of 0.3 m**, NOT a D x V
   product of 0.3 m2/s. Per ARR Book 6 (Ball et al. 2019) the curves use limiting depths of
   0.3, 0.4 and 0.5 m for small car, large passenger car and large 4WD, and limit velocity
   to 3 m/s. Do not let any tool conflate the depth cap with a depth-velocity hazard product.
2. The AR&R and Shand et al. thresholds describe a **stationary** vehicle subjected to flow.
   A moving vehicle removes the exact degree of freedom those thresholds are about. Any
   answer that applies them unchanged to a driven vehicle is wrong.

---

## The benchmark, specified, and the seam that is genuinely unclaimed

Found in a second research report that is **also not in the corpus**:
`/Users/josie/Downloads/Reconstruction-to-Decision Pipelines- Prior-Art Assessment for
Sensor-Reconstruction → Physics-Simulation → Validated Feasibility:Safety Verdict.md`,
17,638 bytes. It specifies the comparison target precisely, which nothing else on disk does.

**What arXiv 2607.00673 actually built.** Real terrain reconstructed by 3D Gaussian Splatting
from **21 minutes of 4K drone video** with COLMAP poses, seeding a **Material Point Method**
simulation of flooding, landslide and deformation, producing an explicit route-feasibility
decision (feasible / rerouting-cost ratio / unreachable). **It includes an Alaska village
flood case in which a truck transitions from feasible to infeasible crossing under identical
geometry.** That is the Alaskan simulation. Its companion position paper is arXiv 2605.30542,
"Physically Viable World Models: A Case for Query-Conditioned Embodied AI".

**What it does not do, in the authors' own words.** The environments "exist only in
simulation", which "limits the applicability of hardware validation". There is no check
against published fording thresholds or physical test data.

**The seam.** That report searched defense (DTIC, TARDEC/GVSC, ERDC, NATO NG-NRMM/AMSP-06),
off-road, disaster-response and amphibious domains and found **no published pipeline chaining
reconstruction to physics simulation to a specific vehicle's fording go/no-go to validation
against independent fording criteria**. All four capabilities exist separately:

| Capability | State of the art | Why the chain breaks |
|---|---|---|
| Reconstruction of crossing geometry | ERDC LiDAR river-crossing site assessment; 3DGS terrain | no physics in the loop |
| Vehicle-fluid physics | **Project Chrono SPH fording with two-way vehicle-fluid coupling**; automotive VOF wading (Simerics, DualSPHysics, SPH-flow) | CAD vehicle in an idealised flat pool, not reconstructed terrain; validates water ingress, not traversability |
| Empirical fording thresholds | **US Army FM 90-13 Appendix C**, TM 9-238; Czech wet-gap work (days per year a gap exceeds 120/140 cm) | never coupled to a simulation |
| Validated flood reconstructions | urban flood digital twins, FlowsDT-Galveston | output is inundation, not a vehicle verdict |

**Two consequences that change the briefs below.**

1. **There is an empirical validation target for a MOVING vehicle after all.** FM 90-13
   (River-Crossing Operations, Appendix C) states verbatim: *"Fording is possible for current
   velocities that are less than 1.5 MPS. Riverbeds at fording sites must be firm and free of
   large rocks and other obstructions. Vehicle-operator manuals contain specific depth
   capabilities and required adaptations."* This is a fording criterion, not a
   stationary-stability criterion, so unlike AR&R it survives the vehicle moving. It is the
   missing target for L5 and L7.
2. **There is an existing engine with two-way vehicle-fluid fording coupling**: Project
   Chrono. Caveat, stated by the source and to be carried: water fording is a **known gap** in
   NG-NRMM, the validated parts are soft-soil mobility, and the SPH fording capability is
   **demo-level, not a validated reconstruction-to-fording-verdict pipeline**. The source also
   warns that specific quantitative NG-NRMM fording error-reduction figures **could not be
   verified in open sources and should not be cited**. Carry that warning.

**So the forked track's claim is now precise.** Not "a more realistic simulation", but:
*closing criterion 4, empirical validation against independent fording criteria, on a
reconstruction-to-simulation-to-verdict pipeline for a road vehicle.* That is the one thing
arXiv 2607.00673 explicitly omits, and the prior-art sweep found nobody else has done it.

---

## The limitations these briefs target

All measured, all from `docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md` on branch
`claude/moving-vehicle-exploratory-2026-08-11`, except L1 which I computed.

| # | Limitation | Evidence |
|---|---|---|
| **L1** | Road-scale extent and validated resolution are mutually exclusive. A 30 x 12 x 3 m scene at 18 depth cells needs **246.8 M grid cells** against the canonical tank's **884,736**, a 279x increase | computed from realized depth 0.2944294473 m |
| **L2** | Floor BC smears **27 to 72 percent** of a shallow water column; penetration saturates at 0.93 to 1.01 dx, so corrupted fraction is about 1/depth_cells, and it is 6 percent at the validated 18 cells | doc section 5(a) |
| **L3** | At-rest vertical reaction wrong by a large factor **and not consistently in one direction**: hull reads high, box control reads low. Rules out a calibration offset, points at a fixed 1 dx contact skirt merging the Rogue's wheels and underbody into a larger effective displaced volume | doc section 5(b) |
| **L4** | Nothing reaches steady state in 150 frames (5.0 s); Fz oscillates by a factor of 2 or more. The validated harness settles for 600 frames | doc section 5 |
| **L5** | **No force number from that scene is quotable.** Not drag, not buoyancy, not torque | doc section 5, stated verbatim |
| **L6** | The SDF cache never hits: `load_vehicle` draws 60,000 **random** surface samples, back-to-back loads differ by 2.22e-16 m, one ULP, enough to change `build_sdf_cached`'s content hash | doc section 7 |
| **L7** | A driven vehicle removes the degree of freedom the AR&R verdict is about, so no FORD verdict is derivable from a moving scene | doc scope statement |
| **L8** | Engine: Genesis LegacyCoupler FAILED buoyancy on the real hull (-105.8 percent fixed-body, body sank when it should have risen); warpmpm material-8 assigns velocity rather than integrating force | Vista `track2_realism/FINDINGS_TRACK2_2026-08-13.md`; register A-1 |

---

## RB-1. Multi-resolution MPM: how to get road-scale extent without losing the near-body regime

**Targets L1.** **Tool: Undermind.** This is a methods-survey question where a fabricated
citation would send a week of implementation the wrong way, which is exactly the case the
artifact says Undermind is least likely to fail at.

```
I am building a Material Point Method free-surface water simulation of a road vehicle
crossing floodwater. I have a hard resolution-versus-extent conflict and I need to know how
the published literature resolves it.

THE CONFLICT, measured on my own stack:
- My validated regime resolves the water depth with about 18 grid cells.
- Realized water depth is 0.2944294473 m, so 18 cells means dx = 0.01636 m.
- A road-scale domain of 30 x 12 x 3 m at that dx is 246.8 million grid cells.
- My current canonical tank is 884,736 cells. That is a 279x increase.
- The coarsest thing I have run at road-ish scale reached only 3.68 depth cells (dx 0.0816 m),
  where boundary smearing corrupts 27 to 72 percent of the water column.

WHAT I NEED:
1. Every published technique for spatially varying resolution in MPM specifically: adaptive
   mesh refinement on the background grid, nested or multi-level grids, particle splitting
   and merging, adaptive particle radius, moving or body-fitted refinement windows, and
   hybrid MPM/shallow-water or MPM/depth-averaged coupling where the far field is cheap.
2. For each: does it preserve MPM's conservation properties, what does it do to the
   time step and CFL, and has it been demonstrated on free-surface flow with a rigid body?
3. The specific failure modes reported at refinement interfaces: spurious reflection,
   mass or momentum error, ringing, particle clustering.
4. Whether anyone has published a moving refinement window that follows a rigid body
   through a large domain, which is exactly my case.
5. The honest alternative: papers that argue you should NOT refine and should instead
   shrink the domain, use periodic or open boundaries, or simulate a moving reference frame
   that travels with the vehicle.

CONSTRAINTS ON THE ANSWER:
- Give DOIs or arXiv ids for everything. I will verify each one.
- Distinguish clearly between what is demonstrated for free-surface water plus a rigid body
  and what is only shown for solids or single-phase flow.
- If a technique exists only as a preprint or has never been reproduced, say so.
- Report negative results: if no one has done moving-window refinement in MPM, that is a
  valuable answer, say it plainly rather than offering the nearest adjacent thing as if it fits.
- Note explicitly that Steffen, Kirby and Berzins 2008 is my current anchor for MPM losing
  convergence under refinement at fixed particles-per-cell, and tell me whether the
  multi-resolution literature interacts with that result.
```

---

## RB-2. Boundary conditions for shallow water columns over a no-slip floor

**Targets L2.** **Tool: Undermind.** Narrow, technical, and a wrong answer is silently
destructive because the corruption is invisible in a rendered frame.

```
In an MPM free-surface water simulation the floor is an enforced plane boundary condition on
the background grid nodes. I measure that water particles settle up to about one grid cell
below the plane: penetration saturates at 0.93 to 1.01 dx across every resolution I tested,
and no mass leaves the domain, so the column is smeared rather than drained.

The consequence is that the corrupted fraction of the water column is roughly 1/depth_cells.
At my validated 18 cells that is 6 percent and tolerable. In a shallow road-flood scene at
3 to 6 depth cells it is 27 to 72 percent, which destroys the quantity I am trying to measure.

WHAT I NEED:
1. The published treatments of solid boundaries in MPM that reduce or eliminate this
   penetration: separate boundary layers, ghost or mirror particles, level-set or SDF
   boundaries instead of grid-aligned planes, cut-cell methods, augmented or Nitsche-type
   weak enforcement, and any explicitly conservative contact formulation.
2. Quantitative comparisons: does any paper actually MEASURE penetration depth in units of
   dx and report it, so I can compare against my 0.93 to 1.01 dx?
3. Whether the choice of basis function changes it, specifically linear versus quadratic or
   cubic B-spline, and whether GIMP, CPDI or B-spline MPM reduce boundary penetration.
4. How shallow-water and thin-film MPM or SPH work handles this, since a flooded road is by
   definition a thin layer over a solid surface. Include any minimum resolution guidance:
   how many cells across the depth do practitioners consider the floor for a quantitative
   free-surface result?
5. Whether anyone reports a correction or calibration for the smeared layer rather than a
   scheme change, and whether such corrections are considered acceptable in the literature.

CONSTRAINTS:
- DOIs or arXiv ids for everything.
- I care about water with a free surface, not dry granular MPM. Flag anything that is
  granular-only.
- If the honest answer is that thin-layer free-surface MPM over a no-slip floor is simply
  not well resolved in the literature, say that clearly. That is a citable limitation for me.
```

---

## RB-3. How warpmpm and Genesis actually build their SDF contact bands

**Targets L3 and L6.** **Tool: DeepWiki**, which the artifact calls "the standout
code-adjacent tool" and recommends pointing at `kks32/mpm-engine` and
`Genesis-Embodied-AI/genesis-world` specifically. Treat every answer as a hypothesis and
confirm against the pinned source at `third_party/mpm-engine-544c93dd-solver-core/`.

Ask DeepWiki these, one at a time, against `kks32/mpm-engine` and then `Genesis-Embodied-AI/genesis-world`:

```
1. Where is the signed-distance-field collider built for a rigid body, and what is the
   width of the contact or influence band in grid cells? Is it a fixed number of cells, or
   does it scale with the mesh feature size?

2. When a rigid body's mesh has slender features much thinner than one grid cell, such as
   wheels or an underbody gap, what does the SDF band do to the effective displaced volume?
   Is there any sub-cell or fractional-volume treatment, or does the band inflate thin
   features to at least one cell?

3. Show me the exact call chain from the rigid body's surface mesh to the grid nodes that
   feel it, with file and line references.

4. Is the surface sampling used to build the collider deterministic? Specifically, does the
   loader draw a fixed number of random surface points, and is that draw seeded? If it is
   unseeded, what is the downstream consequence for any content-addressed cache of the SDF?

5. Is there an existing API for a MOVING or time-varying SDF collider, one whose transform
   updates each step, and does anything write a reaction force back to the body from it?
```

**Why this matters concretely.** My measured symptom is that the at-rest vertical reaction
reads HIGH for the hull and LOW for a box control at the same resolution. A single
calibration offset cannot produce opposite signs, so the suspect is a fixed 1 dx skirt that
merges the Rogue's wheels and underbody into a larger effective displaced volume while the
box, which already spans its footprint, instead loses level to over-carve and floor smear.
Question 4 targets a separate measured defect: the loader draws 60,000 random surface
samples, back-to-back loads differ by 2.22e-16 m (one ULP), and that is enough to change the
cache's content hash so the SDF is rebuilt every run.

---

## RB-4. Settling, transients and quasi-steady measurement for a body in free-surface flow

**Targets L4.** **Tool: Undermind**, with **Wolfram** for any timescale arithmetic.

```
I need to know how long a rigid body in a free-surface MPM or SPH water simulation must run
before a force measurement is meaningful, and how the literature decides that.

MY MEASUREMENTS:
- My validated stationary harness settles for 600 frames before measuring.
- My moving-vehicle scene shows Fz still oscillating by a factor of 2 or more at 150 frames
  (5.0 s at 30 fps), with no steady value reached.
- A related ladder experiment showed the settle gate at one resolution is NON-DETERMINISTIC
  at fixed configuration and identical seed: three identical runs gave settle_vmax_final of
  0.865234, 0.861557 and 0.594807, with an identical peak to four decimals.

WHAT I NEED:
1. The established criteria for declaring a free-surface simulation settled or
   quasi-steady. Not rules of thumb, actual published criteria: kinetic-energy decay
   thresholds, velocity-magnitude gates, force-signal stationarity tests, running-mean
   convergence, spectral criteria.
2. The relevant physical timescales I should be comparing against, with formulas: sloshing
   and seiche period for a tank of given length and depth, gravity-wave transit time,
   viscous and numerical damping timescales, and the settling time for an initially
   disturbed free surface.
3. For a body that is MOVING through the water rather than held fixed, what is the
   equivalent of steady state? How does the literature handle a genuinely transient
   quantity, and what is the accepted practice for reporting a force during a transit?
4. Whether anyone reports non-determinism in a settle criterion at fixed configuration and
   attributes it to a mechanism, for example non-deterministic atomic accumulation in the
   particle-to-grid transfer on GPU. Is that a known and documented effect?
5. Ensemble practice: when a single run is not reproducible, how many seeds or repeats does
   the literature consider sufficient, and how are results reported?

CONSTRAINTS:
- DOIs or arXiv ids for everything.
- Separate what is established for a FIXED body from what is established for a MOVING one.
  I expect the moving case to be much thinner, and if so I want that stated as a gap.
```

---

## RB-5. What validates a MOVING rigid body in free-surface flow

**Targets L5, L7 and L8. This is the most important brief of the eight.** **Tool: Undermind
for the survey, then Elicit for the comparison table** (the artifact credits Elicit with
"data extraction into tables" and Research Reports across up to ~80 papers). Elicit needs
authorising in your claude.ai connector settings first; if that is not done, run the table
step in Undermind too and accept a weaker table.

```
I need the validation targets for a rigid body MOVING through free-surface water in a
particle method (MPM or SPH). A stationary-body buoyancy check does not validate a moving
body, and I currently have no falsifiable target.

MY SITUATION:
- Validated: a FIXED SDF collider in still water agrees with analytic Archimedes buoyancy to
  within 7.3 to 7.7 percent.
- Failed: a different engine's built-in coupler on the same real vehicle hull gave -105.8
  percent against analytic buoyancy on a fixed body, and in a free-body test a body of half
  water density SANK 0.20 m in 0.64 s when ideal buoyancy would have raised it about 2.0 m.
- My existing verdict criterion comes from stationary-vehicle flood-stability thresholds,
  which by construction describe a vehicle held still in flow. Driving the vehicle removes
  the exact degree of freedom those thresholds are about, so the criterion does not transfer.

WHAT I NEED:
1. Canonical VALIDATION CASES for a moving rigid body in free-surface water that have
   published experimental or analytical reference data. Candidates I expect: dam-break
   impacting a movable obstacle; a floating body in regular waves with measured RAOs; water
   entry and slamming of a wedge or cylinder with measured pressure; planing hull resistance;
   a body towed at constant speed with measured drag; sloshing with a moving baffle.
   For each: what is measured, what is the reference data, how accessible is it.
2. The ACCEPTED ERROR BANDS. When a particle method is validated on those cases, what
   agreement is considered publishable? I want numbers, not adjectives.
3. ADDED MASS and unsteady drag for a bluff body accelerating in water near a free surface,
   including how added-mass coefficients are measured or computed, and how much they change
   the apparent force during acceleration.
4. Whether a road vehicle specifically has ever been simulated MOVING through floodwater in
   any particle method. I believe the answer is no and that the closest MPM-adjacent
   fluid-structure work is aircraft-tire hydroplaning and dam-breach simulation. Confirm or
   refute that, and give me the closest existing work either way.
5. What a defensible verdict even IS for a moving vehicle. The stationary thresholds give
   incipient motion. For a driven vehicle the analogous quantities might be loss of traction,
   loss of steering authority, or a stopping-distance criterion. What does the literature use?

6. THE FORDING LITERATURE SPECIFICALLY, which I have only just discovered and which appears
   to be the right frame. US Army FM 90-13 (River-Crossing Operations, Appendix C) states
   "Fording is possible for current velocities that are less than 1.5 MPS. Riverbeds at
   fording sites must be firm and free of large rocks and other obstructions. Vehicle-operator
   manuals contain specific depth capabilities and required adaptations." TM 9-238 covers
   deep-water fording. Czech military wet-gap work (Rybansky, Sedlacek, Dohnal et al.)
   computes per-vehicle fording feasibility against published fording-depth limits, in
   days-per-year a gap exceeds 120 or 140 cm.
   Get me: the primary documents; whether the 1.5 m/s figure has an experimental basis or is
   a doctrinal rule of thumb; what vehicle-specific fording depth limits are published and
   for which vehicles; and whether any civilian equivalent exists. This is a FORDING
   criterion, so unlike the stationary-stability curves it should survive the vehicle moving.
   That makes it my candidate validation target and I need to know how solid it is.

CONSTRAINTS AND WARNINGS:
- DOIs or arXiv ids for everything, and flag anything you cannot resolve.
- The Australian small-car limit is a limiting STILL-WATER DEPTH of 0.3 m, NOT a
  depth-times-velocity product of 0.3 m2/s. Per ARR Book 6 (Ball et al. 2019) the limiting
  depths are 0.3, 0.4 and 0.5 m for small car, large passenger car and large 4WD, with
  velocity limited to 3 m/s. Do not conflate the depth cap with a hazard product.
- Negative findings are as valuable as positive ones here. If there is no validation case
  for a moving road vehicle, that is my result and I need it stated cleanly.
```

**Already established, do not spend the run rediscovering it.** A prior-art sweep across
DTIC, TARDEC/GVSC, ERDC, NATO NG-NRMM/AMSP-06, off-road, disaster-response and amphibious
domains found no published pipeline chaining reconstruction to physics simulation to a
vehicle fording go/no-go to validation against independent fording criteria. Use the run to
test that negative, not to re-derive it.

Then, in Elicit, extract this table across every validation case found: *case name, body
motion type (free, towed, prescribed), fluid method used, reference data type (experiment,
analytic, other simulation), reported error band, Reynolds and Froude regime, whether the
free surface is resolved, DOI*.

---

## RB-6. Engine selection for a moving body, and what the moving path costs in code

**Targets L8.** **Tool: DeepWiki** for the code reality, plus one **Undermind** pass for the
comparative literature.

DeepWiki, ask against `kks32/mpm-engine`, `Genesis-Embodied-AI/genesis-world`,
`InteractiveComputerGraphics/SPlisHSPlasH`, and `DualSPHysics/DualSPHysics`:

```
1. What is the exact mechanism by which a rigid body receives force from the fluid? Show me
   whether a force or impulse is accumulated and integrated, or whether the body's velocity
   is instead assigned or averaged from the fluid. Give file and line references.

2. Is there a two-way coupled path where the body writes momentum BACK to the fluid grid or
   particles, and is momentum conserved across the interface? Show the write-back site, or
   confirm there is none.

3. What is required to drive a body with prescribed kinematics while still reading the
   fluid reaction force on it?

4. Does the engine support a moving or rotating collider whose transform updates every step,
   and is the SDF rebuilt or transformed?

5. What are the documented aarch64 and CUDA constraints for building and running this on an
   NVIDIA GH200?
```

**Add Project Chrono to the DeepWiki targets**, repo `projectchrono/chrono`. This is the
single most important addition to this brief: prior-art work identifies **Chrono SPH fording
with two-way vehicle-fluid coupling** as existing capability, and Chrono also ships a full
multibody vehicle model with tyres and drivetrain, which is exactly the moving-vehicle half
this project lacks. Ask it specifically:

```
6. Where is the SPH fluid solver coupled to the multibody vehicle model, and is the coupling
   two-way? Show the force transfer in both directions with file and line references.
7. Is there a worked fording or water-crossing demo, and what does it actually validate?
8. What terrain representation does the vehicle drive on, and can it ingest an external
   heightfield or mesh from a reconstruction?
9. What are the GPU and aarch64 build constraints?
```

**Four hard constraints already established, do not spend time rediscovering them.**
DualSPHysics ships x86-only static libraries, a hard aarch64 blocker on GH200. Genesis's
LegacyCoupler was tested to destruction on the real Yaris hull and failed buoyancy. Chrono's
water fording is a **known gap** in NG-NRMM, where the validated parts are soft-soil
mobility and the SPH fording capability is **demo-level, not a validated
reconstruction-to-fording-verdict pipeline**. And specific quantitative NG-NRMM fording
error-reduction figures **could not be verified in open sources and must not be cited**.

---

## RB-7. Building a metrically correct outdoor scene, and the splat-to-simulation bridge

**Targets the scene half of the fork.** **Tool: Undermind** for the literature, **DeepWiki**
for `nerfstudio-project/gsplat` and `nerfstudio-project/nerfstudio` code questions.

```
I need to build a realistic outdoor flooded-road environment for a physics simulation:
terrain, road surface, banks and obstacles, at correct metric scale, into which I can place
a vehicle and water.

MY CONSTRAINTS AND WHAT I ALREADY KNOW:
- A prior reconstruction attempt produced a geometrically correct but metrically WRONG mesh:
  a car reconstructed at 0.333 x 0.174 x 0.715 m, volume 0.0173 m3, watertight. The
  reconstruction succeeded; only the scale was lost, because the splat trainer normalises
  median camera-to-subject distance to 1.0 and no scale-recovery step exists.
- My vehicle geometry does NOT come from reconstruction. It comes from finite-element
  crash-test decks and is metrically exact. So I need the SCENE from reconstruction, not the
  vehicle.
- The target to be comparable with is arXiv 2607.00673, "Path Planning in Physically Viable
  World Models", whose authors state their environments exist only in simulation with no
  external empirical validation.

WHAT I NEED:
1. Metric scale recovery for 3D Gaussian Splatting and photogrammetry: known-length
   reference object in frame, GPS or IMU, stereo baseline, LiDAR fusion, or a known camera
   rig. Which are reliable, and what residual scale error does each report?
2. Splat-to-simulation bridges. PhysGaussian and its successors, including implicit-MPM
   variants, Gaussian Splashing, and any work that turns a splat scene into a simulatable
   collision surface or continuum. For each: does it produce a mesh, an SDF, or particles,
   and is the terrain treated as rigid, deformable, or as a boundary condition?
3. Reconstructing scenes captured "in the wild" with unconstrained lighting and moving
   water, since a real flooded road has both. I am aware of Splatfacto-W for unconstrained
   collections; tell me what else exists and what breaks on reflective or moving water
   specifically.
4. The alternative to reconstruction: procedural or DEM-based terrain. Public elevation
   data sources with real road geometry, and how to get a road surface and cross-slope
   correct enough to matter hydraulically.
5. How much terrain fidelity actually CHANGES a flood-vehicle result. Is there any
   sensitivity study on terrain resolution or roughness for vehicle stability in floodwater,
   or would a flat plane with correct cross-slope be defensible?

CONSTRAINTS:
- DOIs or arXiv ids for everything.
- Distinguish what has been demonstrated on real outdoor captures from what is shown only on
  synthetic or object-centric benchmarks.
- Item 5 is the one I most want an honest answer on, including "nobody has studied this."
```

---

## RB-8. Grounding the scenario in real data, and a citation-integrity pass

**Not a literature search.** The artifact identifies these as REST APIs to pull, and
separately as a citation-verification job.

**Data pulls, scriptable, no research tool needed:**
- **NHTSA vPIC** (`vpic.nhtsa.dot.gov/api`) for real curb weights and footprints for the
  three classes, so masses map to real vehicles rather than assumed values. This bears
  directly on the fact that the Rogue's 1571.3 kg is web-sourced only, its FE deck stating
  no mass at all.
- **USGS Instantaneous Values Service and the Real-Time Flood Impact API** for real gauged
  depth and velocity, and surveyed road and bridge flood-impact heights, to justify the
  sweep ranges rather than asserting them.
- Zenodo flooded-vehicle imagery, if a visual comparison is ever wanted: STURM-FloodDepth
  DOI 10.5281/zenodo.14833532, and the flooded-bus dataset DOI 10.5281/zenodo.17151262.
  Note these give *classified depth bins*, not continuous depth-plus-velocity ground truth.

**Citation integrity, run in this order:**
1. **Scholar Sidekick** `auditBibliography` over the whole `.bib`. It targets the dominant
   fabrication pattern, a real resolvable DOI paired with an invented title, which a
   does-the-DOI-resolve check cannot catch.
2. **Scite** on every threshold, coefficient and DOI before it is written as settled.
3. **Crossref plus Retraction Watch** (`api.crossref.org/works/{DOI}`, check `update-to` and
   `relation`) as a free batch retraction check.
4. Re-verify the Australian thresholds against **ARR Book 6 (Ball et al. 2019)** and **WRL
   Technical Report 2014/07** directly, because the depth-versus-D x V conflation is the
   specific error the artifact warns is easy to make and easy to miss.

---

## Running order

RB-3 and RB-6 are DeepWiki and cost minutes, so run them first: they may change the engine
decision, which changes what the rest is for. RB-5 is the one that determines whether the
forked track can produce a defensible number at all, so run it next and give it the most
attention. RB-1 and RB-2 decide whether the domain can be built at all. RB-4 and RB-7 are
refinements. RB-8 runs continuously.

**Verification rule for every one of these.** These tools produce hypotheses. Nothing from
any of them enters the register, the paper or a commit message until the primary source has
been read. The artifact says this about DeepWiki specifically, and the project's own record
shows why: a research report in this same corpus asserted that 2337 kg was a 2018 Dodge Ram
mass, and a direct read of the run's own `summary.json` later showed `mass_source` recorded
it as an AR&R class figure. That retraction is the standing example.
