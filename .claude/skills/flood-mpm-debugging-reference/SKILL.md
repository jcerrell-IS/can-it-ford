---
name: flood-mpm-debugging-reference
description: Use this skill for ANY task that writes, edits, or debugs code touching Genesis MPM/SPH, kks32/mpm-engine, vehicle mass/inertia/friction parameters, or gsplat-to-simulation geometry in the Can It Ford project. Trigger on mentions of grid_density, coup_friction, rho, DRIFT_THRESHOLD, MPM.Liquid, SPH.Liquid, load_vehicle, FloodScene, splashsurf, or any error message containing "particles pass through", "GLIBCXX", "arm64", "aarch64", or a CUDA/torch install failure on Vista or LS6. Also trigger before stating any vehicle mass, inertia, or rho value as fact, before writing a new MPM/SPH scene, and before assuming a Genesis or kks32/mpm-engine API behaves a certain way without checking.
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

## Session-start pointer (folded in from the CLAUDE.md addendum)

This section preserves the text originally drafted as a CLAUDE.md addendum. CLAUDE.md is gitignored in this repo to keep personal profile information off GitHub, so the pointer lives here in the committed skill instead.

Before writing or debugging any code touching Genesis MPM/SPH, kks32/mpm-engine, vehicle mass/inertia/friction parameters, or gsplat-to-simulation geometry, load the `flood-mpm-debugging-reference` skill. It indexes known Genesis/kks32 bugs with fixes, the current correct vehicle parameter values, and which files in `reference_data/` and `docs/` to open for full sourced detail.

Never state a vehicle mass, inertia, rho, or friction value as fact without checking it against `reference_data/vehicle_data_master_reference_2026-07-21.json` or `vehicle_params.py` live. Prior session summaries and superseded research files in this repo are not sources of truth, the skill above tells you which specific files are currently known-wrong.
