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
2. **Friction.** Confirm `friction=0.55` is the live value on the SDF collider calls, don't assume it from a prior session. If the code actually has the 0.4 engine default instead, either change it and cite Azhar et al. 2023, or report 0.4 honestly as "engine default, not yet calibrated," don't silently claim 0.55 when the code says otherwise.
3. **Water compressibility.** `mpm-engine`'s bulk modulus is deliberately softened for timestep stability. Bulk wave speed is therefore not physically real water. State this plainly in Methods/Limitations. It's a defensible, documented tradeoff, not a hidden flaw, don't let it read as an oversight.
4. **Collider type.** Use SDF colliders, not CDF, for anything needing a calibrated force reading. The repo's own docs describe CDF as "soft" and under-reporting contact load.
5. **Failure-mode taxonomy.** Three real hydrodynamic instabilities exist in the literature (Shand et al. 2011): slide, topple, float. "Stuck" is the stable, no-instability baseline, not a fourth mode. Citation anchors, already resolved, don't re-derive: slide → Xia et al. 2011 (drag ≥ friction), topple → Xia et al. 2013, float → Kramer et al. 2016 (Froude < 0.5 = flotation-controlled, > 0.5 = sliding-dominant).
6. **DRIFT_THRESHOLD = 0.05m.** Already resolved, reuse this exact language rather than re-deriving it: "a conservative numerical onset-of-motion detection tolerance, not a peer-reviewed physical instability criterion," grounded conceptually in Xia et al. 2014 and Shah et al. 2018. This has been independently derived three separate times across this project's files, all three agree, treat re-deriving it a fourth time as wasted effort, not added rigor.

## `kks32/mpm-engine`, what it can already do, checked directly against the source

- `src/warpmpm/vehicle.py`: `FloodScene` class, already parameterized close to this project's depth (0.08-0.6m) and velocity (1-3 m/s) targets. `load_vehicle()` accepts a **real 3D Gaussian Splat PLY** (INRIA layout, the same format `gsplat`'s own trainer produces) as a rigid vehicle body. Check this before writing new vehicle-loading code, it may already exist.
- `src/warpmpm/splats/` + `examples/splat_sim.py`: a working, tested PhysGaussian-style splat simulation pipeline, interior filling, covariance advection, SH rotation under deformation. This is not a stub, per direct source inspection it's a real, functioning feature.
- `docs/performance.md` self-reports: bulk modulus is deliberately softened for stability, meaning wave propagation speed is NOT physically accurate, and there's a measured +22% apparent volume inflation in pouring scenarios. Both are known, accepted tradeoffs of the explicit solver, not bugs to chase.
- SDF colliders give calibrated absolute force readings. CDF colliders are "soft" (fluid can sit a few mm inside a thin boundary) and only read a geometry-dependent fraction (about a third for a node-aligned sheet) of the true load. Use SDF when you need a real force number.
- License: MIT for the group's own code. `src/warpmpm/kernels/` (the upstream warp-mpm core) has no license file, cite it, don't treat it as freely re-licensable.

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
- `coup_friction` in Genesis is a numerical stability impulse coefficient, not Coulomb friction. Physical ground friction for this project is mu ≈ 0.3-0.55 (Azhar et al. 2023). Don't conflate the two when someone asks "what's the friction."

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
