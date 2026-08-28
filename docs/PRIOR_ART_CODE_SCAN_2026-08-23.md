# Comparable prior art on public GitHub, 2026-08-23

Scope: public GitHub only, searched via `search_repositories` and `search_code`,
summarised via DeepWiki with every load-bearing symbol re-verified by direct
code search. Judged against the three open problems named in the request:
coupling force validation, in/outflow BCs, grid convergence.

**Note on the framing:** the request cited "CLAUDE.md Part 5". Checked live
today, `CLAUDE.md` has no numbered Part headings at all, so there is no Part 5.
The three problems are real and traceable in that file, just not under that
heading. I worked from the three named problems.

## Method caveat, stated because it changes how to read the negatives

GitHub repo search ANDs terms across name/description/readme. Long queries
return zero for query-form reasons, not absence. Three of my first four queries
returned zero and were false negatives, caught by re-running `PhysGaussian`
alone (11 hits). Every zero below was re-tested in a shorter form. Even so,
absence here means "not found by keyword search of public repos", never
"does not exist".

DeepWiki fabricated one function name during this scan
(`MPM_to_rigid_body_force_transfer`, zero hits anywhere on GitHub) while
answering a question about a repo it was not reading. Every symbol quoted
below was confirmed by an independent `search_code` call.

---

## 1. `ishaldogar/flood-traversability-mpm` — the one that actually matters

**This is a sibling NSF REU project at TACC/UT Austin, summer 2026.** Its
README says so in the first line. Same institution, same summer, same research
question, same threshold source.

What it is: five Python files, ~15 KB total, no solver in the repo. Synthetic
10,000-point road terrain, dam-break flood in Taichi MPM on Lonestar6 A100s,
~18k particles, 500 steps, ~2 min/run. 24 scenarios varying water height
(0.03-0.5 m) and release velocity (0.1-4.0 m/s): 6 SAFE, 10 RISKY, 8 UNSAFE.

**What it does NOT do, in its own words: "the vehicle is not simulated."** It
compares water depth and velocity at the crossing against published thresholds.
Its "Future work" section lists, verbatim, three items:
- Train a GNN surrogate on the dataset
- Replace synthetic terrain with 3D Gaussian Splatting reconstructions
- **Add vehicle-fluid interaction to the simulation**

That is a description of Can It Ford. This is the single most important find in
the scan and it is not a technical one: it is a positioning fact.

**Useful to you:**
- It grades against **Shand et al. 2011, AR&R Project 10, Table 3** with
  small-car limits depth <= 0.3 m, D x V <= 0.3 m^2/s, velocity <= 3.0 m/s.
  That is an independent second user of the same table, and their D x V is
  **0.3**, against Al-Qadami's 0.39 (2022) and 0.36 (2023). Three numbers now
  in play for the same quantity. Worth naming the source every time.
- Their key finding is directly relevant and slightly awkward for a velocity
  sweep: **"Crossing hazard is governed by released water volume, not initial
  flow velocity"** — gravity-driven collapse brings even 0.1-0.3 m/s releases
  to 1-3 m/s at the crossing. This echoes the Al-Qadami 2023 result that drag
  decreases with Froude number, already in CLAUDE.md.
- Solves none of the three open problems. No vehicle, so no coupling force; no
  in/outflow BC (dam-break initial condition instead); no convergence study.

**Action:** this is a talk-to-your-PI item, not a code item.

---

## 2. `kks32/mpm-engine` — the upstream, and it already has the accumulator

Not external prior art, but the scan turned up something worth stating plainly.
The blob SHAs served by GitHub for this repo resolve to
`544c93dd02cb9c7ead89e1155a62967243244fce`, which is exactly the commit vendored
locally at `third_party/mpm-engine-544c93dd-solver-core/`.

**Finding: the exact reaction wrench the coupling-force problem asks for is
already implemented in the pinned solver, on the SDF collider path.** Read live
from the vendored tree:

- `kernels/mpm_solver_warp.py:2733-2735` — `impulse = m * (v_free - v_new)`,
  then `wp.atomic_add(param.force, 0, impulse)` and
  `wp.atomic_add(param.torque, 0, wp.cross(rel, impulse))`
- `kernels/mpm_solver_warp.py:2115-2116` — "each substep the kernel accumulates
  the exact reaction impulse m*(v_free - v_imposed) AND its torque about
  `point` BEFORE overwriting the node, so wrench = impulse/dt"
- `core/solver.py:355-357` — "Reaction wrench the material exerts on an SDF
  collider, from the grid impulse ... sum (x - center) x impulse / dt"

This is consistent with CLAUDE.md A-1, which already says the SDF collider path
is the validated one and the material-8 free-rigid path used by the 17 canonical
runs has no force accumulator. So this is corroboration from the pinned source,
not news.

**The structural catch, and it is the useful part.** That accumulator measures
`m * (v_free - v_imposed)`: the impulse required to *impose* a kinematic
velocity. It reports force on a body whose motion is prescribed. Using it for a
*free-floating* vehicle means staggering: measure wrench, integrate the rigid
body, prescribe the new pose, repeat. That is partitioned FSI, and partitioned
schemes are known to go unstable from added mass when the body is light relative
to the displaced fluid. The canonical hull is 310.494 kg/m^3 against water at
1000, so this is squarely the light-body regime.

I am flagging that as **inference, not sourced**. I queried the project's own
research index: 6 papers carry the `added-mass` method tag, and a query for
"added mass instability partitioned" returns **0 matches**. So the corpus does
not currently cover the partitioned-FSI stability mechanism, and this concern
is unreviewed.

**Also in the upstream but NOT in the local vendored tree:** `src/warpmpm/`
contains `coupling/` (`wrench.py`, `admittance.py`, `backend.py`), `colliders/`,
`splats/`, `geometry/`, `vehicle.py`. The local vendor kept only `kernels/`,
`materials/`, `core/` — `find third_party -name 'wrench.py'` returns nothing.

`coupling/wrench.py` is worth reading but does **not** solve your problem: it is
a stress-integral traction estimator for a **box** end-effector pressing down,
integrating `sigma . e_z` over a horizontal band beneath the box. Wrong geometry
for a hull, and it measures a vertical force, not drag. Its own docstring is the
valuable line: *"This estimator is used for quasi-static controller feedback;
moving-contact measurements use the collider grid impulse instead."* The
upstream authors are saying, in their own code, that for moving contact you use
the grid impulse path, not the stress integral.

---

## 3. `yuanming-hu/taichi_mpm` — the CPIC reference implementation

CLAUDE.md A-1 names Hu et al. 2018 CPIC (doi:10.1145/3197517.3201293) as the
literature-backed alternative to velocity averaging. This is that paper's code,
and it is the most directly useful external repo in the scan.

Verified: `apply_tmp_impulse` exists in `src/transfer.cpp` (1 hit),
`advect_rigid_bodies` exists in `src/mpm.h`, `src/mpm.cpp`,
`src/mpm_rigid_body.cpp` (3 hits). Both confirmed by direct code search after
DeepWiki named them.

How it couples, per DeepWiki over those files: the force is computed as an
**impulse during P2G**. When a particle and a grid node have different "colors"
(the CPIC compatibility flag), the code compares particle velocity against the
rigid body's velocity at the grid position, computes a velocity change with
friction projection, forms an impulse from particle mass and kernel weight, and
calls `r->apply_tmp_impulse(impulse, grid_pos)`. Rigid bodies can be **either**
free-floating (integrated from accumulated impulses via `advect_rigid_bodies`)
**or** kinematically prescribed via `pos_func`/`rot_func` with infinite mass.

**Why this is the useful one:** it is the only repo in the scan that accumulates
material-on-body force *and* integrates a free body from it, in one scheme,
without staggering. That is exactly the architecture the SDF-wrench path cannot
give you, and it sidesteps the added-mass staggering concern above because the
impulse is applied inside the transfer rather than between solves.

**Caveats before anyone gets excited:** C++ and Taichi, not Warp; CLAUDE.md's
engine decision is do-not-switch and that still stands; and this would be a
translation of a scheme, not a port of code, the same way the Zhao 2019 BC is.

---

## 4. `Anura3D/Anura3D_OpenSource` — the in/outflow BC is NOT in the open release

174 stars, Fortran, MPM soil-water-structure. CLAUDE.md names Zhao, Bolognin,
Liang, Rohe and Vardon 2019 (Computers and Fluids 179, 27-33) as the in/outflow
BC this project needs, and says it is "implemented in Anura3D".

**That is true of the paper and appears not to be true of this public release.**

DeepWiki over the source reports that in/outflow is handled by prescribing
velocities on existing **nodes**, via `CorrectWaterForPrescribedVelocity`
(`src/MPMDYN2PhaseSP.FOR`, `src/MPMDYNConsolidation.FOR`) and
`ApplyNodalInfiltrationRate` (`src/MPMDYN2PhaseSP.FOR`), with material points
neither created nor deleted at the boundary. It found no evidence of the Zhao
2019 scheme.

I tested that negative rather than trusting it, because code search returning
zero on a repo can mean the repo is not indexed:
- `repo:Anura3D/Anura3D_OpenSource ApplyNodalInfiltrationRate` → **1 hit**
  (`src/MPMDYNConvPhase.FOR`). So the repo IS indexed and searchable.
- `repo:Anura3D/Anura3D_OpenSource inflow` → **0 hits**
- `repo:Anura3D/Anura3D_OpenSource outflow OR Zhao OR MovingMesh` → **0 hits**

So: the literal tokens are absent from an indexed repo. That is a real negative,
though a Fortran codebase could implement the scheme under different names.

**Why this matters:** it means there is no reference implementation sitting
there to translate from. The plan of record already says implementing Zhao 2019
in warpmpm is "a translation, not a port" — this scan says it is a translation
**from the paper alone**, with the open-source Anura3D providing the
prescribed-nodal-velocity approach instead, which is architecturally close to
what `sim_standing.py` already does with its Dirichlet slab clamp.

That is a meaningful downgrade of the expected shortcut, and it is worth
recording before anyone budgets time against "port the Anura3D BC".

---

## 5. `XPandora/PhysGaussian` — the splat-to-particle bridge, and one usable number

1,412 stars, CVPR 2024 Highlight. The reference splat-to-MPM pipeline.

Its internal filling step is the direct analogue of `solidify_watertight`:
a ray-collision method with `density_threshold`, `search_threshold`,
`ray_cast_direction`, `search_exclude_direction`, `max_particles_per_cell`, and
a filling grid that defaults to **4x** the simulation `n_grid`. Volume is then
assigned by `get_particle_volume` from `grid_lim / n_grid`.

**The one directly transferable item for the grid-convergence problem:** its
docs give a stability rule of thumb of **at least 3-4 grid cells across the
thinnest feature of the model**, plus the CFL form `substep_dt < dx / max_velocity`.
No formal convergence study, explicitly empirical.

Set that against what this project already measured: hull ground clearance
177 mm, and at g48 `dx` exceeds the clearance outright. The 3-4-cells-across-the-
thinnest-feature criterion is a published, citable statement of a rule the
canonical ladder violates at its coarse end. That is more useful as a
*limitation citation* than as a fix.

---

## 6. Scanned and judged not useful

- `zeshunzong/warp-mpm` (223 stars). DeepWiki confirms colliders impose velocity
  constraints on `grid_v_out`, one-way, **no force/torque reporting**. Useful
  only as corroboration that the missing accumulator is an upstream
  architectural property, not a local defect.
- `kywind/real2sim-eval` (226 stars). Splat-to-sim, but the physics is
  **spring-mass via PhysTwin**, not MPM. Its rigid coupling uses
  `wp.mesh_query_point_sign_winding_number` plus impulse response, and
  `create_rigid_phystwin.py` samples interior points with trimesh. Technique
  parallels only.
- `cb-geo/mpm` (294 stars), `geoelements/gns` (236), `geoelements/diffmpm` (48),
  `geoelements/LearnMPM` (25). Same-lab infrastructure, already known.
  DeepWiki could not answer a coupling/convergence question about `cb-geo/mpm`
  without drifting to another repo, so I make no claim about its contents.
- `Anura3D` forks, `PhysSplat`, `MetaSCUT`, `EndoGSim`, `RoboSplatter`,
  `gausstwin`, `splatground`, `genesis-sand-water-walker`. Adjacent, none
  bearing on the three problems.

## What the scan did not find

No public repo that simulates a vehicle in floodwater with two-way coupling.
The nearest is a sibling REU project that explicitly does not simulate the
vehicle. On the code side, the novelty claim holds.

---

# Round 2, 2026-08-23: narrower queries, and two corrections to the above

## Query-form evidence, recorded so the zeros are interpretable

`search_repositories` ANDs every token across repo **metadata only** (name,
description, indexed readme). Measured this round:

| query | hits |
|---|---|
| `PhysGaussian` | 11 |
| `PhysGaussian simulation` | 1 |
| `PhysGaussian vehicle` | 0 |
| `PhysGaussian flood` | 0 |
| `gsplat physics simulation vehicle` | 0 |
| `NVIDIA warp mpm vehicle` | 0 |
| `warp mpm rigid body coupling` | 0 |
| `mpm vehicle` | 4 |

Two-token queries work when both tokens are common (`mpm vehicle` → 4). They
collapse to zero when a niche token is paired with anything (`PhysGaussian
vehicle` → 0). So those five zeros mean "no repo carries both words in its
metadata", which is a real but narrow negative, and NOT "no such code exists".

`search_code` searches file **content** and is the correct instrument here:
`MPM vehicle flood language:python` → **163 hits**, versus 0 for the
equivalent repo-metadata query.

## Correction 1: the coupling-force problem is not open, it has an implementation

`simulation/coupling_force/` exists locally and is **tracked** (8 files, created
2026-08-12): `force_coupling.py`, `inflow_outflow.py`, `rigid_body.py`,
`coupler.py`, `rung_b_coupled.py`, `test_rigid_body.py`.

Its README states the scheme is exactly reset → step → `sdf_wrench` → integrate
→ `set_sdf_pose`, described in its own words as "a standard **partitioned
(weakly coupled) explicit FSI** scheme", carrying the vehicle as an SDF collider
to close the loop for a free body.

**Withdrawing what I wrote in round 1.** I flagged partitioned-FSI added-mass
divergence as my own "inference, not sourced, unreviewed". That was already
documented in this README on 2026-08-12, in near-identical terms: "As displaced
fluid mass approaches body mass, the explicit update over-predicts and can
diverge. That regime is exactly a near-neutrally-buoyant vehicle."
`ForceCoupledBody.added_mass_ratio()` reports it and warns past a threshold.
The concern was right; presenting it as new was wrong.

Status per that README: rung (b) gate **passed** 2026-08-12, force path produces
a non-zero upward buoyant wrench where the kinematic path produces none.
`test_rigid_body.py` is 14 analytic checks passing, and the README is explicit
that **these validate the integrator, not the fluid coupling**.

## Correction 2: this sharpens exactly what taichi_mpm is worth

Because the local scheme is partitioned explicit, and its documented failure
mode is displaced-fluid-mass approaching body mass, the vehicle regime is the
bad one: at 310.494 kg/m^3 against water at 1000, displaced mass is roughly 3x
body mass, well past neutral.

**`yuanming-hu/taichi_mpm` CPIC is the direct answer to that specific limit.**
It applies the material-on-body impulse *inside* the P2G transfer
(`apply_tmp_impulse`, `src/transfer.cpp`, verified) rather than between solves,
and integrates the free body from the accumulated impulses
(`advect_rigid_bodies`, verified in 3 files). There is no staggered exchange, so
the partitioned divergence mode does not arise in the same way.

That is a narrower and more defensible reason to look at CPIC than "it is the
paper A-1 cites". It targets the known limit of code that already exists here.

The local README independently names its own preferred swap for a different
reason: "For a thin-walled hull the CDF collider path (`add_cdf_collider` /
`cdf_wrench` / `set_cdf_pose`) has the identical interface and is the correct
swap." CDF is the compatible-distance-field machinery CPIC is built on, so the
two routes point the same way.

## Correction 3: the in/outflow finding is stronger than round 1 said

`simulation/coupling_force/inflow_outflow.py` header, read live: "Zhao et al.
2019 in/outflow BCs for warpmpm: inlet IMPLEMENTED, outflow SUBSTITUTED.
Written 2026-08-12. Status: CPU reference implementation, analytically
self-tested. NOT run against the GPU solver. No gated run uses it. Do not cite
as validated."

It establishes the blocking engine constraint: Zhao's outflow is
**pressure-controlled**, and `grep -ci pressure kernels/mpm_solver_warp.py`
returns 0 across 3,181 lines at pinned SHA 544c93dd. There is no pressure field
to Dirichlet-constrain. The substitute is a recycling conveyor that retires and
reissues particles so the fixed allocation never changes.

So round 1's Anura3D negative compounds rather than duplicates: the open-source
Anura3D does not ship the scheme to copy, **and** the half that matters most
could not be copied literally even if it did.

Caveat, unresolved: that "NOT run against the GPU solver" line is dated
2026-08-12, and there is a later record of an R7 in/outflow experiment
completing on GPU (jobs 918501 and 918506) on a separate branch. I did not
reconcile the two. Check the branch before repeating either status.

## New find: `kks32/mpm-engine/experiments/flood_sweep.py`

Surfaced only by content search. The upstream's own flood-vehicle sweep, using
`warpmpm.vehicle.FloodScene` as an importable harness over 5 (depth, velocity)
cases: (0.08, 1.0), (0.15, 1.0), (0.08, 2.0), (0.15, 2.0), (0.15, 3.0).

Three things in it worth having:

1. **A Froude scaling recipe, stated explicitly.** The bundled truck is model
   scale at 1.45 m; read at full size with depths and displacements x lam,
   velocities x sqrt(lam), masses x lam^3, lam = L_real / 1.45. This is the
   missing half of the local note that the bundled truck reproduces to 0.43%
   but stays unverified.
2. **A domain-exhaustion artifact, named by the upstream author:** "Final
   displacement saturating near 0.83 m means the truck was washed into the
   downstream wall (the domain ran out, not the surge)." A saturating
   displacement is a boundary artifact, not a physical plateau. Worth checking
   against any saturating displacement in the local sweeps.
3. **A `scene.leaked` diagnostic** printed per case, alongside peak yaw. Related
   in spirit to the local P-2 water-fraction-inside-bbox gate and the measured
   21-31% particle pass-through at gd=64.

## Coverage statement

No external public repo found that simulates a vehicle in floodwater with
two-way coupling, and none bridging Gaussian splats to a vehicle-scale MPM
flood scene. Probed by repo-metadata search and by file-content search, in
multiple query forms, this round and last. The nearest remains a sibling REU
project that explicitly does not simulate the vehicle. Everything that actually
bears on the three problems is either the upstream engine or already in this
repository.
