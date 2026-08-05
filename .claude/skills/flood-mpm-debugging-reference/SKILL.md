---
name: flood-mpm-debugging-reference
description: Use this skill for ANY task that writes, edits, or debugs code touching Genesis MPM/SPH, kks32/mpm-engine, PhysGaussian, vehicle mass/inertia/friction parameters, water compressibility, collider type, failure-mode classification, DRIFT_THRESHOLD, or gsplat-to-simulation geometry in the Can It Ford project. Also trigger before writing Methods or Limitations text, before rendering any output, and before committing any code adapted from PhysGaussian. Trigger on mentions of grid_density, coup_friction, rho, MPM.Liquid, SPH.Liquid, load_vehicle, FloodScene, splashsurf, SDF/CDF colliders, slide/topple/float, or any error message containing "particles pass through", "GLIBCXX", "arm64", "aarch64", or a CUDA/torch install failure on Vista or LS6. Also trigger before stating any vehicle mass, inertia, or rho value as fact, before writing a new MPM/SPH scene, and before assuming a Genesis or kks32/mpm-engine API behaves a certain way without checking.
---

# Flood-MPM Debugging Reference

This skill exists because this project has repeatedly lost hours rediscovering things already found once. Read the relevant section below before writing code in the matching area. If a section references a file in `reference_data/` or `docs/`, open that file for the full sourced detail, this skill is the index and the hard rules, not the complete research.

## Before touching ANY specific number

Never state a vehicle mass, inertia tensor, rho, or friction value from memory or from a prior session's summary. Check it live against one of these, in this order of authority:
1. `reference_data/vehicle_data_master_reference_2026-07-21.json`, the canonical, live-verified source for the AR&R classification trio (Neon/Explorer/C1500/CR-V) and the NCAC mesh trio (Yaris/Silverado/Rogue).
2. `vehicle_params.py` in the repo, for the box-proxy compact_sedan/midsize_suv/light_pickup classes.
3. If neither has it, say so explicitly and go find a primary source. Do not estimate and present it as sourced.

**Known-wrong value, do not reproduce:** `reference_data/MPM_Flood-Vehicle_Reference_Data__Sedan__SUV__Pickup__NEON_TABLE_SUPERSEDED.md` has a Dodge Neon inertia table (Ixx/Iyy/Izz) that is wrong, contradicted by the master reference. Its Silverado and friction sections are fine.

**Open, unresolved as of this writing:** the real NCAC Yaris mesh's actual weight is 1,078 kg, not the 1,100 kg MASH nominal previously used, meaning rho should be 1078/3.5427 = 304.28 kg/m³, not 310.47. Whichever script actually computes this mesh's rho at simulation time has NOT been confirmed to reflect this correction yet. Check before trusting any Yaris-mesh simulation output.

## The two vehicle pipelines, do not conflate them

- **Box-proxy pipeline**: `vehicle_params.py`, generic bounding box + mass + NHTSA-measured inertia tensor, no real mesh. Currently used by Track 1 and Track 2 vehicle bodies.
- **Real-mesh pipeline**: NCAC/CCSA finite-element models (Yaris resolved, Silverado/Rogue available but not yet converted), or a Gaussian-splat capture loaded via `kks32/mpm-engine`'s `load_vehicle()`. These have their own, separate rho calculation from actual mesh volume, not from `vehicle_params.py`.
A script using one should never silently inherit a number computed for the other.

## PhysGaussian, licensing constraint, do not violate

PhysGaussian's own code is **all-rights-reserved**, not permissively licensed. It is approved for use as a **private, local-only render tool** for generating one hero visual asset, never committed to the public `can-it-ford` repo. Adapting its code (including `gs_simulation.py`) and pushing that adaptation to GitHub is a real license violation, not a citation nicety. If a task calls for the splat-to-particle bridge PhysGaussian demonstrates, check `kks32/mpm-engine`'s own `src/warpmpm/splats` first, it already implements the same concept under MIT, and is safe to commit to. Only a clean-room reimplementation of PhysGaussian's approach, written without copying its code, would be safe to commit publicly.

## Part 3: physics properties to lock before rendering anything

Each of these is a one-line, cited decision that belongs in CLAUDE.md and in any Methods/Limitations section, not something a script should silently assume. Check the live value before stating any of these as fact, don't assume the number below still matches what a given script currently does.

1. **Vehicle mass/density.** Pick one and use it everywhere: 1078 kg / rho=304.28 (NCAC actual modeled weight, most defensible), or 1100 kg / rho=310.47 (MASH class nominal, also defensible if explicitly labeled as such). Either is fine. Using both, silently, in different files is the actual problem.
2. **Friction.** Confirm `friction=0.55` is the live value on the SDF collider calls, don't assume it from a prior session. This project's own forensic audit found the specific "0.55, Azhar et al. 2023" attribution unverified against Azhar's full text. μ_wet ≈ 0.3 is the primary, best-sourced value in this project's literature (Bonham & Hattersley 1967, Kramer et al. 2016, Xia et al. 2011), with 0.25-0.75 as the documented sensitivity range. If the code says 0.4, that's the engine default, report it honestly as "not yet calibrated," don't claim 0.55 when the code says otherwise either way.
3. **Water compressibility.** `mpm-engine`'s bulk modulus is deliberately softened for timestep stability. Bulk wave speed is therefore not physically real water. State this plainly in Methods/Limitations. It's a defensible, documented tradeoff, not a hidden flaw, don't let it read as an oversight. **For Genesis's own `MPM.Liquid` specifically** (relevant if Track 2 is still active): there is no exposed sound-speed/EOS-stiffness parameter at all: it uses a `lam·J·(J-1)` compressible pressure term, `lam` derived from `E`/`nu` (defaults `E=1e6`, `nu=0.2`). Tune compressibility via `E`, not a named sound-speed argument. `SPH.Liquid` DOES expose `stiffness`/`exponent` directly if an explicit, physically-named speed of sound is ever needed. Source: `docs/research_2026-08/MPM_Rigid_Coupling_in_Genesis-_A_Source-Level_Audit.md`.
4. **Collider type.** Use SDF colliders, not CDF, for anything needing a calibrated force reading. The repo's own docs describe CDF as "soft" and under-reporting contact load.
5. **Failure-mode taxonomy.** Three real hydrodynamic instabilities exist in the literature (Shand et al. 2011): slide, topple, float. "Stuck" is the stable, no-instability baseline, not a fourth mode. Citation anchors, already resolved, don't re-derive: slide → Xia et al. 2011 (drag ≥ friction), topple → Xia et al. 2013, float → Kramer et al. 2016 (Froude < 0.5 = flotation-controlled, > 0.5 = sliding-dominant).
6. **DRIFT_THRESHOLD = 0.05m.** Already resolved, reuse this exact language rather than re-deriving it: "a conservative numerical onset-of-motion detection tolerance, not a peer-reviewed physical instability criterion," grounded conceptually in Xia et al. 2014 and Shah et al. 2018. This has been independently derived three separate times across this project's files, all three agree, treat re-deriving it a fourth time as wasted effort, not added rigor.
7. **Coupling force validation, currently zero, and this is now mandatory, not optional.** No test, example, or benchmark anywhere in the Genesis repo validates MPM-rigid coupling force against an analytical or experimental reference (Archimedes buoyancy, Stokes drag, published data). Before trusting ANY force number this pipeline produces: submerge a rigid box of known volume in MPM water, sum the per-substep coupling force (`cfrc_coupling_vel`), compare steady-state vertical force to `ρgV`. Repeat for a towed body vs. a drag estimate. Decision threshold: >5-10% deviation means reduce `dt`/raise `substeps`/raise `grid_density` before trusting anything else from the run.
8. **Particle/grid resolution, no formal force-convergence criterion exists in the SPH/MPM/PIC-FLIP literature, full stop.** What exists is rules of thumb: `dp ≤ D/10` on the SMALLEST force-bearing feature, not the whole vehicle (a girder spanned by 2 particles over-predicted force by a wide margin in the one study that measured this directly), and ≥10 particles across flow depth (≥40 if flow is breaking/aerated). When under-resolved, the field's dominant (not universal) bias is OVER-prediction of peak force. Required practice for this project: run ≥3 resolutions, report the % change in the actual decision metric (drift, FORD/NO-FORD verdict) between them, declare convergence only below a stated tolerance (5-10% is defensible). This project already ran this practice once: g48/g64/g96 at fixed depth (0.2944294 m) and velocity (1.5 m/s), across all three mass classes. Non-monotone in dx for two of three masses (1100 kg and 1609 kg swing by as much as 2.4x between refinement steps), but the FORD/NO-FORD verdict is grid-invariant, all nine runs land NO-FORD by a 1.8x-13x margin over DRIFT_THRESHOLD. What's actually missing: a formal convergence declaration against a stated tolerance. Cite the verdict, never the magnitude.
Source for both: `docs/research_2026-08/MPM_Rigid_Coupling_in_Genesis-_A_Source-Level_Audit.md` and `docs/research_2026-08/Particle_Resolution_and_Force_Convergence_for_Rigid_Bodies_in_Flood-Type_Flows-_A_Critical_Review.md`.

## `kks32/mpm-engine`, what it can already do, checked directly against the source

- `src/warpmpm/vehicle.py`: `FloodScene` class, already parameterized close to this project's depth (0.08-0.6m) and velocity (1-3 m/s) targets. `load_vehicle()` accepts a **real 3D Gaussian Splat PLY** (INRIA layout, the same format `gsplat`'s own trainer produces) as a rigid vehicle body. Check this before writing new vehicle-loading code, it may already exist.
- `src/warpmpm/splats/` + `examples/splat_sim.py`: a working, tested PhysGaussian-style splat simulation pipeline, interior filling, covariance advection, SH rotation under deformation. This is not a stub, per direct source inspection it's a real, functioning feature.
- `docs/performance.md` self-reports: bulk modulus is deliberately softened for stability, meaning wave propagation speed is NOT physically accurate, and there's a measured +22% apparent volume inflation in pouring scenarios. Both are known, accepted tradeoffs of the explicit solver, not bugs to chase.
- SDF colliders give calibrated absolute force readings. CDF colliders are "soft" (fluid can sit a few mm inside a thin boundary) and only read a geometry-dependent fraction (about a third for a node-aligned sheet) of the true load. Use SDF when you need a real force number.
- License: MIT for the group's own code. `src/warpmpm/kernels/` (the upstream warp-mpm core) has no license file, cite it, don't treat it as freely re-licensable.

## Sustained open-channel flow, does not exist natively in either engine

Confirmed by reading `genesis/engine/boundaries.py`, `sph_solver.py`, and
`mpm_solver.py` directly: exactly two boundary classes exist (`CubeBoundary`,
`FloorBoundary`), no inlet/outlet/periodic class anywhere. A uniform initial
velocity in a closed box WILL decay and recirculate. Viscosity, pressure/
incompressibility, and `restitution=0.0` wall absorption all remove directed
momentum every substep. True for both MPM.Liquid and SPH.Liquid; MPM adds grid-
transfer dissipation on top. GitHub issue/PR search (exhaustive but not
paginated to completion) found zero inlet/outlet/periodic-boundary work in the
repo's history.

If the current or any future scene needs sustained current past a stationary
vehicle rather than a one-shot dam-break/inrush, pick one, ranked by effort:
1. **Re-impose velocity each step (cheapest, no source changes).** Every
   `scene.step()`, reset the upstream slab of particles to target velocity `U`.
   Benchmark: probe mean speed just upstream of the vehicle, target within
   10-15% of `U` over the full run.
2. **`Constant`/`Wind` force field + hand-rolled drain.** Drive fluid with
   constant acceleration, periodically deactivate/recycle particles piling at
   the downstream wall. Benchmark: monitor downstream particle count, increase
   drain rate if it grows unbounded.
3. **Modify solver source (only route to true steady-state).** Add a real
   inlet/outlet or a periodic boundary variant of `impose_pos_vel`. No upstream
   PR exists to build on. Use this tier only if reported velocities/forces need
   to be physically calibrated rather than illustrative.

Check `can_it_ford_L2.py` and any active MPM scene against this: if the setup
assumes sustained flow past a parked vehicle without one of the above three
mitigations, the flow is decelerating over the run whether or not that's been
noticed yet.

Source: `docs/research_2026-08/Can_Genesis__genesis-world__v1_2_0_Natively_Simulate_Sustained_Open-Channel_Flow_Past_a_Vehicle__A_Source-Level_Verdict.md`.

## Genesis, known failure modes with exact fixes or workarounds

| Symptom | Cause / fix | Source |
|---|---|---|
| MPM particles pass through a thin rigid body | `grid_density` too coarse below 128 for the object's scale. Fix: bump to 128 or 256. | Issue #600 |
| SPH particles scatter at extreme velocity on any collision | Known, unresolved upstream. Partial mitigant: reduce collision velocity or particle size, both have real tradeoffs. | Issue #685 |
| MPM demo bounces/jerks differently than the reference video | Reported on stock RTX 4090, not hardware-specific. Don't assume it's your setup. | Issue #476 |
| `pip install torch` on Vista/GH200 silently resolves CPU-only | aarch64 wheel gap. Fix: use PyTorch nightly aarch64+CUDA build, or NVIDIA's prebuilt container. Always run `torch.cuda.is_available()` after any dependency change to confirm, don't assume. | Known ARM/GH200 issue |
| `GLIBCXX_3.4.26' not found` at runtime | Shared library version mismatch, seen on differentiable MPM examples. Watch for this on any new container/environment, not project-specific. | Issue #1180 |
| LuisaRender fails to build, `Undefined symbols for architecture arm64` | Confirmed real build failure on ARM64 (seen on Apple Silicon, same failure class expected on Vista). Don't attempt the LuisaRender path on Vista without a specific reason to retry it. | Issue #42 |
| MPM Elastic `pbs` sampler stopped working after an update | Real regression, seen after a Genesis version bump. If something that worked before suddenly breaks after a `pip install --upgrade`, check for this pattern before assuming your own code changed. | Issue #1598 |
| No macro-scale wave/hydrodynamics model | Doesn't exist in Genesis, particle-level fluid only. Don't search for a wave-height API that isn't there. | Issue #682 |

No published wave-propagation or bow-wake/wake-formation benchmark exists for either Genesis or kks32/mpm-engine at this project's scale, confirmed by direct search, not just absence of evidence found in this repo. Treat both engines' fluid behavior at shallow-flood scale as unvalidated against a ground truth, not as either "known good" or "known bad."

## `splashsurf`, particle-to-mesh surface reconstruction

Real, established tool (`InteractiveComputerGraphics/splashsurf`), marching-cubes based, takes VTK/PLY/BGEO/XYZ particle input. Published `pysplashsurf` wheels on PyPI cover `x86_64`, `i686`, `armv7l`, **not** `aarch64`, which is what Vista and LS6 actually are. Do not assume `pip install pysplashsurf` will find a prebuilt wheel there, check first, likely needs `cargo build` from source.

## Environment rules, do not violate

- Track 1 (`kks32/mpm-engine`) runs in the `mpmenv` venv. **Never** through Apptainer.
- Track 2 (direct Genesis MPM) runs through the Apptainer container at `$GENESIS_PATH`. **Never** in `mpmenv`.
- `$GENESIS_PATH` is unset at the start of every new shell session, re-export it every time, don't assume it persists.
- Genesis pads MPM domain bounds inward by `3*dx` on each side. SPH does not. Size domains accordingly, don't reuse an SPH domain size for an MPM scene without adjusting.
- `coup_friction` in Genesis IS genuine Coulomb-type friction, confirmed by reading `_func_collide_in_rigid_geom` at commit 6d2d19ec directly. It multiplies the signed normal relative velocity and subtracts μ·|v_normal| from tangential speed, clamped to zero for sticking. This is the textbook impulse form of Coulomb friction. **Cross-checked live on Vista 2026-08-05** against the code actually deployed, `$WORK/genesis-world` at commit `639131dc`: the function is defined at `genesis/engine/couplers/legacy_coupler.py:284`, and the friction clamp is line 322, `qd.max(0, rvel_tan_norm + rvel_normal_magnitude * geoms_info.coup_friction[geom_idx])`, with `rvel_normal_magnitude` negative when colliding, so it evaluates to `max(0, |v_t| - μ·|v_n|)`. The deployed code matches the description above. **This also reconciles the two provenance anchors this project has been citing separately:** `_func_collide_in_rigid_geom` here and CLAUDE.md's `legacy_coupler.py:322` are the same line of the same function, one source cited two ways, not two independent confirmations. **This corrects the earlier "numerical stability impulse coefficient, not Coulomb friction" claim in this file, which was wrong.** Caveats that still matter: it operates at grid-node velocity level under an SDF `influence` blend (confirmed live at line 333, `vel = vel_rigid + rvel_new * influence + rvel * (1 - influence)`; the `influence = exp(-signed_dist/coup_softness)` form and the `influence > 0.1` gate were NOT re-read in this pass and remain on 6d2d19ec's authority only), not as a clean force-level μN bound, and it is strictly distinct from `Rigid.friction`, which governs rigid-rigid contact only; do not conflate the two names. Physical ground friction in this project's literature: **μ_wet ≈ 0.3 is the primary, best-sourced defensible value** (Bonham & Hattersley 1967, reused by Kramer et al. 2016 and Xia et al. 2011), with **0.25-0.75 as the documented sensitivity range** across studies (Xiong et al. 2024). If live code uses `friction=0.55`, that falls inside the documented range but is **not** the project's primary-cited value, and the specific attribution "0.55 per Azhar et al. 2023" has **not** been independently confirmed against that paper's full text, per this project's own forensic audit. Don't state "0.55, Azhar 2023" as a settled citation, either cite it as μ_wet≈0.3 (primary) with 0.55 noted as within the sensitivity sweep, or flag the Azhar attribution explicitly as unverified if it must be used. **Since coup_friction is now confirmed as a genuine Coulomb coefficient, feeding a real Coulomb value (0.3 or 0.55) into it is no longer a category error. See item 7 under Part 3 above: the coupling force itself has never been validated, so the resulting physics is still not confirmed correct.**
Source: `MPM_Rigid_Coupling_in_Genesis-_A_Source-Level_Audit.md` in `docs/research_2026-08/`.

## `can_it_ford_L2.py` specifically, confirmed live, three real bugs as of last audit

This is the original SPH pilot script (`SPH.Liquid`, not `MPM.Liquid`), not connected to `vehicle_params.py` at all:
1. Hardcodes `rho=604` on the vehicle material, unresolved, disconnected from any vehicle_params source.
2. Hardcodes vehicle box `(1.0, 1.6, 1.5)`, not the sedan-scale `(4.66, 1.79, 1.44)` box `vehicle_params.py` defines.
3. `run_tag` string hardcodes `"cf0p4"` but the code actually sets `coup_friction=0.55`. Every output filename and CSV row from this script has mislabeled the friction value used. Do not trust the run_tag string for this parameter on any existing output from this script, check the actual code that produced it.

## Where everything currently lives

- Vista: `/work/11603/jcerrell0629/vista/can-it-ford/reference_data/` and `/docs/`
- LS6: `/scratch/11603/jcerrell0629/can-it-ford-reference/` (flat, reference-only copy, LS6 does not run any of this project's simulation code, this exists for lookup convenience while working on gsplat there)
- Mac: `~/can-it-ford/_inbox/` for working notes and session logs, not citable research

## When you hit something not covered above

Say so explicitly. Do not extrapolate a fix from a superficially similar entry in this table and present it with the same confidence as a sourced one. Search fresh, and if the finding is worth keeping, it belongs back in `reference_data/` or `docs/` and a short pointer added here, not left to be rediscovered next session.
