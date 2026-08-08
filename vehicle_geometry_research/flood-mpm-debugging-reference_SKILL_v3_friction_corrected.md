# SUPERSEDED, DO NOT READ OR CITE. Historical snapshot only.

Marked superseded 2026-08-07. This is a stale 92-line copy of what is now the
130-line live skill at `.claude/skills/flood-mpm-debugging-reference/SKILL.md`,
which is the ONLY canonical copy. 42 lines differ.

Its skill frontmatter (`name: flood-mpm-debugging-reference`) was REMOVED as
part of marking it superseded. It duplicated the live skill's name while
sitting outside `.claude/skills/`, so anything scanning the tree for skill
definitions could have loaded this stale copy instead of the real one.

Known-wrong content still present below, which is why it must not be cited:

- It predates the `coup_friction` correction. The live skill records, verified
  by direct source read on Vista at commit `639131dc`
  (`legacy_coupler.py:284`, clamp at `:322`), that `coup_friction` IS a genuine
  Coulomb friction coefficient. Text below still reflects the earlier, refuted
  "numerical stability impulse coefficient, not Coulomb friction" framing.
- Its DRIFT_THRESHOLD wording is flagged by `scripts/check_claims.py` rule C8,
  and its Xia year by rule C9.

Kept rather than deleted because it is the only record of the intermediate
"v3 friction corrected" state. Read `.claude/skills/flood-mpm-debugging-reference/SKILL.md`
for anything current.

---

# Flood-MPM Debugging Reference (SUPERSEDED SNAPSHOT)

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
2. **Friction.** Confirm `friction=0.55` is the live value on the SDF collider calls, don't assume it from a prior session. **CORRECTED 2026-08-07.** Two claims that used to sit here are refuted by register G4 and by the citation-provenance audit, do not restate either. (a) "μ_wet ≈ 0.3 is the primary, best-sourced value" is REFUTED: 0.30 is the sand-and-gravel worst case in Smith, Modra and Felder 2019, while wet AND dry concrete both read about 0.78. 0.30 does survive as the *adopted convention* of the flood-vehicle stability literature, but it reached that status through expert correspondence, not measurement: Shand et al. 2011 record that "correspondence with various road experts and test laboratories" settled on 0.3. Cite it as an inherited convention, never as the best-sourced measured value. (b) The "0.55, Azhar et al. 2023" attribution is NO LONGER unverified. Azhar, Pauwels and Bui 2023 (DOI 10.1111/jfr3.12885, open access) measured 0.55 themselves with a spring balance on the rubber mat standing in for their road surface, and cited Wong, *Theory of Ground Vehicles*, only to show it falls inside a handbook range of 0.50 to 0.70 for tyres on wet asphalt. So it is a real measurement, but of lab rubber mat, NOT of submerged asphalt, and it sits at the high end of what this literature assumes. Measured comparanda from Shu et al. 2011 (spring balance, wet carpet): Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68. If the code says 0.4, that's the engine default, report it honestly as "not yet calibrated," don't claim 0.55 when the code says otherwise either way.
3. **Water compressibility.** `mpm-engine`'s bulk modulus is deliberately softened for timestep stability. Bulk wave speed is therefore not physically real water. State this plainly in Methods/Limitations. It's a defensible, documented tradeoff, not a hidden flaw, don't let it read as an oversight.
4. **Collider type.** Use SDF colliders, not CDF, for anything needing a calibrated force reading. The repo's own docs describe CDF as "soft" and under-reporting contact load.
5. **Failure-mode taxonomy.** Three real hydrodynamic instabilities exist in the literature (Shand et al. 2011): slide, topple, float. "Stuck" is the stable, no-instability baseline, not a fourth mode. Citation anchors, already resolved, don't re-derive: slide → Xia et al. 2011 (drag ≥ friction), topple → Xia et al. 2013, float → Kramer et al. 2016 (Froude < 0.5 = flotation-controlled, > 0.5 = sliding-dominant).
6. **DRIFT_THRESHOLD = 0.05m.** **CORRECTED 2026-08-07**, this entry previously overclaimed its own provenance. The safe half of the old language stands: it is "a conservative numerical onset-of-motion detection tolerance, not a peer-reviewed physical instability criterion." The rest is withdrawn. It is NOT "grounded conceptually in Xia et al. 2014 and Shah et al. 2018": per CLAUDE.md item 13 and register D7 it has **no peer-reviewed source at all**, and citing those two papers next to it manufactures one. Nor was it "independently derived three separate times, all three agree": repeated agreement across this project's own files is the same source cited repeatedly, not independent confirmation, and the old closing advice to treat a fourth check as "wasted effort" inverts this project's verification rule. It is declared as a bare literal in 16 places under four names (`DRIFT_THRESHOLD`, `DRIFT_THRESHOLD_M`, `DRIFT_M`, `THRESHOLD`); register D7 counts three names, and that disagreement is unresolved, so treat both counts as floors. If you deduplicate, deduplicate by NAME and UNIT: `failure_modes.py:47` is a SPEED in m/s that merely shares the numeral 0.05, and a value-based find-and-replace would silently convert it into a distance and move the 16 published SLIDE verdicts.

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
- **CORRECTED 2026-08-07, this bullet previously carried three refuted claims. Do not restore any of them.**
  (a) "`coup_friction` in Genesis is a numerical stability impulse coefficient, not Coulomb friction" is REFUTED. Per CLAUDE.md, confirmed 2026-08-05 by direct source read, `coup_friction` IS the Coulomb friction coefficient in the LegacyCoupler MPM-rigid momentum exchange (`genesis/engine/couplers/legacy_coupler.py:322`), applied as `|v_t_new| = max(0, |v_t| - mu*|v_n|)`. The separate numerical regularisation parameter is `coup_softness`, default 0.002. This supersedes every earlier statement that `coup_friction` was numerical-only.
  (b) The same "numerical, not physical" error must not be made about **warpmpm** either, and the two are different parameters in different engines, never merge them. The `friction` argument on warpmpm's SDF-collider path is a Coulomb coefficient. Verified live 2026-08-07 against the pinned vendored core at `third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py:2729`, inside the branch commented `separable + Coulomb friction`: `scale = wp.max(0.0, tlen + param.friction * vn) / tlen`, then `v_tan = v_tan * scale`. That is the textbook Coulomb rule, reduce tangential velocity in proportion to the normal component, floored at zero.
  (c) "μ_wet ≈ 0.3 is the primary, best-sourced defensible value" is REFUTED, see Part 3 item 2 above and register G4. 0.30 is the sand-and-gravel worst case in Smith, Modra and Felder 2019, and it is the flood-vehicle literature's inherited convention (Shand et al. 2011, adopted via expert correspondence), not its best-sourced measurement. The "0.55 per Azhar et al. 2023" attribution is no longer unverified: Azhar et al. measured it themselves on a rubber mat and bounded it with Wong's 0.50 to 0.70 wet-asphalt handbook range. State it as a lab rubber-mat value, not a submerged-asphalt value.

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
