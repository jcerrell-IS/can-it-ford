# CANONICAL CORRECTIONS REGISTER
## Can It Ford, 2026-08-06

This is the single authority every skill file, on every surface, gets audited against. Each entry is a claim, its verification tier, its primary source with file and line, and the exact wording to use.

**Tier definitions.** T1 = read directly from live source or a live artifact in a named session. T2 = read from a research document that itself cites a primary source. T3 = asserted in a summary or skill file with no traceable read. Nothing below T2 belongs in a skill file as fact.

**Standing rule this file enforces.** A skill file may state a T1 or T2 claim as fact with its source. A T3 claim must be written as UNVERIFIED with what would settle it. Deleting a T3 claim is also acceptable. Restating it as fact is not.

---

## SECTION A: solver identity and mechanics, T1

**A1. The 17 gated runs use warpmpm, not Genesis.**
Driver is `renders/yaris_render_s1/sim_standing.py`, which imports warpmpm. Genesis appears only in `simulation/can_it_ford_L2*.py` and `designsafe-staging/scripts/*`, the Track 2 box-proxy path. No Genesis scene has ever loaded the Yaris hull.
Wording: "the 17 gated runs, warpmpm via sim_standing.py". Never "Genesis MPM" for that result.

**A2. Gravity is -9.81 and was never unknown. Citation corrected 2026-08-07.**
`core/solver.py:167-169`, inside `Solver.set_material()`: `self._sim.set_parameters_dict({"material": name, "g": [0.0, 0.0, -9.81], **params}, ...)`. Hardcoded on every call, not a library default. `sim_standing.py:127` calls `set_material(newtonian(...))`; `newtonian()` at `materials/__init__.py:78-83` carries no `g` key to override it. Prior citation to `mpm_solver_warp.py:742-743, :811-812` was never re-checked against the actual vendored file and is superseded by this one; that file lives at `kernels/mpm_solver_warp.py`, not `core/`.
DELETE every claim that gravity is unknown or unset.

**A3. No force accessor exists on the 17-run path.**
`rigid_state()` at `solver.py:194-205` returns exactly `com` (3,), `v` (3,), `omega` (3,), `R` (3,3). `MPM_Simulator_WARP` allocates only `rigid_x_cm`, `rigid_v_cm`, `rigid_omega`, `rigid_orientation`, `rigid_mass`, `rigid_inv_inertia_body` at `mpm_solver_warp.py:497-502, 822-830`. No force, impulse or torque accumulator exists anywhere. Momentum exchange happens on the grid and is never materialized. Verified byte-identical at `fd390d6` and `544c93dd`.
The four wrench readouts attach only to kinematic colliders the 17 runs never create: `tool_force` :420 via `add_box`, `sdf_wrench` :354, `cdf_wrench` :401, `cup_wrench` :302, plus offline `coupling/wrench.py:15`.
Independently corroborated from a separate 2026-07-24 read: `add_sdf_collider` is kinematic and its wrench is write-only.
**`cfrc_coupling_vel` has no counterpart in warpmpm.** That name is Genesis-only. Any skill file naming it in a warpmpm context is engine-conflated and must be corrected.
Consequence to state: two-way coupling cannot be verified by reading a force, because no force is produced. The only measurement on the real path is m·dv/dt from `rigid_state()`.

**A4. Only mass reaches the solver.**
`vehicle_density = vehicle_mass / solid_volume`. Inertia, CG height and SSF from `vehicle_params.py` are never passed in. Any claim that measured inertia tensors informed the simulation is void.

**A5. The vehicle is a free rigid body**, registered via `set_material_range` then `finalize_rigid_bodies()`. Not an SDF collider.

**A6. The post-processing gravity fork, recorded here 2026-08-07 because withdrawing CLAUDE.md item 15 nearly lost it.** Item 15 was withdrawn in `6514bfc` on the correct grounds that gravity is no longer unknown in the solver (A2). Its *other* half was a live, verified fact about a fork in post-processing, and its withdrawal note points readers to "register A2 for ... the two post-processing constants" — **A2 did not contain them.** This item closes that dangling pointer. Standing rule: pull the VERIFIED-tier finding into the register BEFORE withdrawing the item that carried it.

Solver gravity is 9.81 and is not in question (A2). Post-processing is forked, verified live 2026-08-07 by `grep -rn "^G = 9\."`:

| value | sites |
|---|---|
| **9.80665** | `simulation/failure_modes.py:14`, `analysis/viability_dashboard_scaffold.py:11` |
| **9.81** | `renders/yaris_render_s1/gates_all_runs.py:12`, `renders/yaris_render_s1/gates_both_scenarios.py:12`, `analysis/four_rung_ladder.py:7`, `analysis/render_v1/gates_both_scenarios.py:12`, `simulation/validate_coupling_force.py:21` |

Two sites at 9.80665, not one: **the "appears only at failure_modes.py:14" phrasing is wrong** and was corrected in `check_claims.py` C6 the same day. The difference is 0.0342 percent.

**This fork now reaches published output.** `failure_modes.py` uses G at `:170` (`surge_accel_g`) and `:174` (`weight_n`), and the classifier has run on all 17 runs (D6b), so 9.80665 fed the published verdicts. Any statement that it never influenced a gated result is retracted. Unify on 9.81, then re-run `analysis/classify_failure_modes.py` and confirm 16 SLIDE / 1 STUCK still holds before treating the change as cosmetic. TOPPLE is the only criterion that could move: it compares `surge_accel_g` against SSF, and all 13 sub-threshold margins are far larger than 0.034 percent, so no verdict flip is expected. Verify rather than assume.

---

## SECTION B: resolution and numerics, T1

**B1. Two depth-resolution numbers exist and both are correct, for different engines.**
warpmpm: `dx = lim/n_grid`, lim about 9.42 m, dx = 0.1472 m, so 0.30 m depth spans about **2 cells**. This limitation is real for the 17 gated runs.
Genesis: `grid_density` is cells per metre, `dx = 1.0/grid_density` independent of domain bounds, so at gd 64 dx = 0.015625 m and 0.30 m spans **19.2 cells**.
The "0.234 m" figure was channel length divided by grid_density and is not how Genesis defines dx.
**Never let these two numbers appear in one sentence without engine tags.**

**B2. The grid convergence study exists and is not converged.**
g48/g64/g96 at fixed depth 0.2944294 m and v = 1.5 m/s, three masses. Non-monotone in dx for 1100 kg and 1609 kg. Largest single refinement step changes displacement by 2.4x. All nine runs land NO-FORD by a 1.8x to 13x margin.
Wording: the binary verdict is grid-invariant, the displacement magnitude is not. **Cite the verdict, never the magnitude.**
Mechanism to cite, not "unexplained anomaly": Steffen, Kirby and Berzins 2008, classic MPM can lose convergence as the grid refines at fixed particles-per-cell.

**B3. No accepted force-convergence criterion exists** in the SPH/MPM/PIC-FLIP literature. Rules of thumb only: `dp <= D/10` on the smallest force-bearing feature, and about 10 particles across flow depth. Say "no accepted criterion exists" rather than inventing one.

**B4. Under-resolution most likely inflates force**, so an over-threshold NO-FORD verdict is conservative rather than wrong. Wei and Dalrymple 2016; St-Germain, Nistor and Townsend 2012; Jian et al. 2016; Kleefsman et al. 2005. Exception: over-fine resolution triggering premature wave breaking.

**B5. Vehicle effective density: 310.494 kg/m3** for the canonical Yaris hull. The 100-300 kg/m3 plausibility band is STALE. Delete it from any gate or check.
Realized density is grid-coupled by construction, since `solid_volume = n_particles * h^3`. It is not an independent physics validation metric.

**B6. P-2 passthrough: 7 of 17 runs fail**, rising monotonically with velocity from 7.99 percent at 0.5 m/s to 15.88 percent at 3.0 m/s. The highest-velocity phase-space cells are the least trustworthy.

**B7. No pressure field exists anywhere in warpmpm.** `grep -ci pressure kernels/mpm_solver_warp.py` returns 0 across 3,181 lines, at pinned SHA 544c93dd. Pressure exists only implicitly, derived per particle from `J = det(F)` and `bulk_modulus` inside the weakly-compressible EOS. Consequence for any future in/outflow BC work: Zhao et al. 2019's pressure-controlled outflow cannot be ported literally. The correct re-expression is a depth-controlled outflow, deactivating particles above a target free-surface height rather than Dirichlet-constraining a pressure that does not exist. **Never describe a warpmpm outflow BC as "pressure-controlled."** Source: docs/OPTION_A_SESSION1_FINDINGS.md F-5.

**B8. The 10x sound-speed criterion is violated on 15 of the 17 canonical runs.** `c = sqrt(1.1 * bulk_modulus / water_density)` with the actual per-run `bulk_modulus` and `water_density` from `data/all_runs_inventory.csv`, cross-checked live 2026-08-07: all 9 mass-class runs at v=1.5 m/s and the 3 fastest velocity-sweep runs (2.0, 2.5, 3.0 m/s) fall below 10x, ratios from 8.56 down to 4.28. Only v=0.5 (25.69x) and v=1.0 (12.85x) pass. Criterion source: Zhao et al. 2019, citing Liang, valid for their setup; not independently validated as a hard requirement for this project's EOS and geometry, so this is a disclosed limitation, not evidence the results are wrong. Does not change grid-invariance of the binary verdict (B2); it is a separate numerical axis, not yet stress-tested the way grid resolution was. Add to any future limitations section alongside B2 through B4.

---

## SECTION C: Genesis-specific, T1. These do NOT apply to warpmpm.

**C1. Installed version is 1.1.1** on Vista. Prior crash forensics were pinned to 1.2.0 source and are unconfirmed as the same code.

**C2. grid_density crash boundary re-bisected 2026-08-05.** gd 80 and 88 pass 3/3 at 60 steps. gd 90+ fails. Non-monotone above the boundary and non-deterministic at fixed config. "gd >= 96 is the crash threshold" and "64 is confirmed safe" are BOTH wrong.

**C3. The crash is `CUDA_ERROR_ILLEGAL_ADDRESS`** from an unguarded p2g grid write, with dmesg-level `NVRM: Xid 31` hardware confirmation.

**C4. Hydrostatic pre-fill is refuted as a fix** as stated. It holds only 6 to 8 steps before the same p2g fault class recurs. Compatible with, and probably the mechanism behind, the `channel_recirc_v2` guard aborts at steps 25, 5 and 13.

**C5. The "97 percent channel blockage" explanation is refuted.** A zero-vehicle fluid-only control reproduces the same stagnation and backwater.

**C6. `gs clean` is not a valid subcommand** on the installed 1.1.1 CLI. Any toolchain-cache-clear recommendation citing it was never checked against what is installed.

**C7. `MPMEntity.set_particles_pos()` exists** on 1.1.1, at `genesis/engine/entities/mpm_entity.py`. The seeding-bridge approach for the splat bridge is viable.

**C8. No inlet, outlet, open or periodic boundary exists** for MPM or SPH. `boundaries.py` defines only `CubeBoundary` and `FloorBoundary`. A per-step re-imposed velocity clamp is therefore NECESSARY, not a hack: a closed domain with restitution 0 necessarily decays a uniform initial velocity.

**C9. `MPM.Liquid` has no viscosity parameter in Pa·s.** Only a `viscous` bool, which yields an elastic shear modulus `mu = E/(2(1+nu))` = 416,667 Pa. Wrong units. Sound speed is not a parameter but is derivable: `lam` = 277,778 Pa, `c = sqrt(lam/rho)` = 16.67 m/s, which is 11.1x the 1.5 m/s design velocity and already satisfies Monaghan's 10x rule at defaults. Tune compressibility through `E`.

**C10. `coup_friction` is genuine Coulomb friction**, `|v_t_new| = max(0, |v_t| - mu|v_n|)`, at `legacy_coupler.py:322`. It acts at grid-node velocity level under an SDF influence blend, is entangled with `coup_softness` (default 0.002), and is distinct from `Rigid.friction`. Default 0.1.
**It is NOT the same parameter as warpmpm's `floor_friction`, which is 0.55 in the 17 runs.** Both have appeared as 0.55 in this project's documents. Never conflate.

**C11. The downstream sill is provably unbuildable** at h = 0.30, v = 1.5. q = 0.45, h_c = 0.274317, E_min = 0.411475, E = 0.414679, so the maximum non-choking sill is 0.003204 m = 0.205 cells at dx 0.015625 and 0.41 cells even at gd 128. `channel_recirc_v2.py` runs `sill_cells: 0` deliberately. A derived impossibility, not an oversight.

**C12. Genesis rejects `.ply` for rigid morphs.** `convexify=True` inflates the Yaris hull to 8.041 m3, 2.27x true. `convexify=False` preserves 3.542739 m3.

**C13. No coupling-force validation exists anywhere in the Genesis repository** against any analytical or experimental reference.

---

## SECTION D: data and verdicts, T1

**D1. The L1 AR&R fix, canonical.** 37 FORD under the bare hazard-only rule to 14 FORD under the joint rule (depth <= 0.30 AND velocity <= 3.0 AND `round(D*V, 6)` <= 0.30). 23 of 70 rows reclassify FORD to NO-FORD, zero the other way.

**D2. The live `data/scenario_sweep.csv` has 10 columns.** `L1_verdict` = 14 FORD. `L1_haz_product_only` = 37 FORD, the old rule preserved separately. Class columns: `L1_verdict_small_passenger` 14, `L1_verdict_large_passenger` 19, `L1_verdict_large_4wd` 26. `L1_class_sensitive` True in 12 of 70 rows.
**The 5-column `scenario_sweep.csv` in Claude.ai project knowledge is a STALE SNAPSHOT.** Any chat-side read of it reports 37 and is wrong. This has produced two false "critical bug" escalations.

**D3. The July 24 ledger L1 numbers are a pre-fix code state.** Commit `85e2252`: 25 of 70 changed, 37 to 12, class counts 12 / 19 / 24. Superseded by D1 and D2. Large passenger 19 and class-sensitive 12 of 70 agree across both states; Small and 4WD do not.

**D4. Canonical results stores.** `data/all_runs_inventory.csv` (17 rows) and `renders/yaris_render_s1/gates_results_all_runs.json` (20 records = 17 standing plus 3 dry_start), plus per-run `summary.json`.
`renders/yaris_render_s1/gates_results.json` is NOT a 17-run store; it holds 3 dry_start records.
`analysis/render_v1/` is a duplicate tree with a 6-record file.
`track1_sweep_v2/manifest.csv` is superseded box-proxy output.

**D4a. `_incoming/` is the canonical per-run tree, and the sibling trees are NOT all safe.** `data/all_runs_inventory.csv`'s `summary_path` column resolves to `renders/yaris_render_s1/_incoming/<run>/`. Verified live 2026-08-07 by byte-comparing `metrics.csv`:
`renders/yaris_render_s1/g64_m{1100,1609,2337}/` ARE byte-identical to their `_incoming/` counterparts, so `analysis/fig4_velocity_regime.py:60`, which reads the `g64_m1100` sibling for its v=1.5 point, is reading correct data.
`renders/yaris_render_s1/m1100/`, `m1609/` and `m2337/` **match NO canonical run**. They are orphan rollouts. Any number read from them appears nowhere in the 17 and cannot be reconciled with any published verdict. Do not source a figure, table or gate from them.

**D5. No gate is a physics validation.** G-1 to G-4, P-1 to P-3 and P-6 are self-consistency and numerical-containment checks. G-3 compares against a reference derived from the same pipeline. P-4 and P-5 are physics but printed only, never gated.

**D6. CORRECTED 2026-08-07. The failure-mode classifier HAS been run on all 17 runs.** The original D6 text, "the failure-mode classifier was never run ... it was never wired in," was true when written but went stale on 2026-08-05. Do not restate it.

**D6a. Canonical failure-mode stores.** `data/failure_modes_by_run_classified.csv` (17 rows, keyed by `run`) and `data/failure_modes_by_run.json` (same 17, richer nesting). Both are regenerated by `analysis/classify_failure_modes.py`, so neither is un-regenerable.
**The JSON's `_provenance.generator` named `scratchpad/classify_17_runs.py` until 2026-08-07, a path that does not exist in the repo.** That is the same defect class that condemned `failure_modes_result.json`, and reproducing the file byte-for-byte would have preserved it, so the field now names the real generator. The 17 run records are byte-identical across that correction; only `_provenance` changed. The script's own check compares the `runs` payload, NOT whole-file bytes, so a genuine verdict regression cannot hide behind an expected provenance diff.
`renders/yaris_render_s1/failure_modes_by_run.json` carries the same verdicts but is GITIGNORED (`.gitignore:14`) and is not written by the generator; the generator only warns if it drifts. Cite the `data/` paths.
`.gitignore:10` is `data/*`, so every store in `data/` is invisible unless explicitly un-ignored. `all_runs_inventory.csv` and `failure_modes_by_run.json` were tracked only by force-add in `841d666`; the un-ignore list added 2026-08-07 makes that survivable. **A new file in `data/` will not appear in `git status` by default.**

**D6b. Verdicts: 16 SLIDE, 1 STUCK.** The exception is `sweepV_g64_v0p5`. Verified live 2026-08-07 by re-running the classifier: reproduces the 2026-08-05 artifact on all 17. All 17 `_incoming/<run>/metrics.csv` carry the full `REQUIRED_COLUMNS` and `OMEGA_COLUMNS` sets, 91 rows, strictly increasing `t`, zero NaN. No run is disqualified.

**D6c. `triggered_*` is the verdict, `ratio_*` is peak magnitude. They disagree.** SLIDE has ratio >= 1 in 17 of 17 runs but triggers in 16; TOPPLE has ratio >= 1 in 13 and triggers in 0; FLOAT has ratio >= 1 in 1 and triggers in 0. Each mode requires a JOINT displacement-and-speed condition sustained 3 consecutive frames (`failure_modes.py:179-185`), not a peak. **Any count taken by filtering on `ratio >= 1` is wrong**, and would report 13 topples that never happened.

**D6d. STUCK is not a fourth mode.** There are three outcomes, SLIDE / TOPPLE / FLOAT; STUCK is the "none sustained" early return (`failure_modes.py:229-230`) and carries no threshold, ratio-of-record or onset frame. Its winning-mode columns are deliberately EMPTY, not zero. Where two modes sustain, `:232` reports the last in `MODE_SEVERITY`, i.e. FLOAT > TOPPLE > SLIDE.

**D6e. `metrics.csv` `pitch_deg` / `roll_deg` are VEHICLE-BODY-SENSE, not raw Euler.** `vehicle_live.py:55-61` computes raw ZYX Euler, then `:295-300` swaps two before writing, so `roll_deg` is the raw Euler pitch (about y, the long axis). The ZYX gimbal singularity is at `|roll_deg| -> 90` and degenerates yaw and pitch, not roll. **It cannot affect any verdict here: the classifier reads neither column.** TOPPLE is an acceleration test, not an angle test. Max `|roll_deg|` over all 17 runs is 4.625 deg.

**D6f. `peak_surge_accel_g` is numerical, not physical.** It is `np.gradient(vel, t)` (`failure_modes.py:127`) over a 30 Hz rigid-body trace; single-frame values reach 3.78 g. The `sustain_frames` guard is the only thing keeping TOPPLE from firing on all 13. Never quote the raw TOPPLE ratio alone.

**D6g. TOPPLE's use of SSF is the correct axis, but only by scene geometry.** SSF is a lateral rollover ratio and TOPPLE tests SURGE acceleration; that is right here ONLY because the vehicle's long axis is y while surge is x (`vehicle_live.py:277-278`), so flow strikes the side. Do not carry this criterion to any scene where the vehicle faces the flow. SSF 1.42 is an estimate flagged "CONFIRM before use" (`vehicle_params.py:108`); every TOPPLE ratio scales as 1/SSF. SLIDE, FLOAT and STUCK do not depend on it.

**D6h. `failure_modes_result.json` remains condemned, and this is unchanged.** It holds 3 entries keyed only by class label, carries no run identifier, and is written by no script in the repo. Unmodified since 2026-07-26. It was MISCITED as independent confirmation at `docs/four_rung_ladder.md:136` and `docs/four_rung_ladder_GRIDAWARE.md:136`; **both citations were repointed by `841d666` on 2026-08-07**. Do not re-report that specific miscitation as live.

**D6i. The defect that actually survived the repoint was the word "independently."** `four_rung_ladder.md` continued to claim the classifier "independently classifies" the three runs after the filename was corrected. It cannot: `simulation/failure_modes.py` reads the same `_incoming/<run>/metrics.csv` the table above it was built from, so it restates one rollout under an explicit criterion and corroborates nothing from a second source. Fixed 2026-08-07. The `_GRIDAWARE` sibling already carried the retraction. **Repointing a citation does not fix an independence claim; check the verb, not just the path.**

**D7. DRIFT_THRESHOLD 0.05 m has no peer-reviewed source.** Re-declared as a literal in 16 places under three names. `gates.py:195-196` records in a print statement that it is a conservative numerical onset-of-motion tolerance.
The attribution to Smith, Modra and Felder 2019 Eq. 6 is a MISATTRIBUTION. That equation contains no such criterion.
**Count disagreement, unresolved:** this entry says three names, CLAUDE.md item 13 says four (`DRIFT_THRESHOLD`, `DRIFT_THRESHOLD_M`, `DRIFT_M`, `THRESHOLD`). Both counts were produced by a bare recursive grep, which H0 shows skips `renders/`, so both are FLOORS, not totals. Re-run with `/usr/bin/grep` before citing either.

**D7a. `simulation/failure_modes.py` carries THREE `0.05` literals, not two, and one of them is not a distance. Verified live 2026-08-07 with `/usr/bin/grep`.**

| line | name | value | UNIT |
|---|---|---|---|
| `:46` | `slide_m` | 0.05 | metres |
| `:47` | `slide_speed_ms` | 0.05 | **metres per second** |
| `:48` | `float_m` | 0.05 | metres |

CLAUDE.md item 13 previously named only `:46` and `:48`. **`:47` is a speed that shares the numeral.** Any deduplication done by find-and-replace on the value `0.05` would silently convert a speed threshold into a distance threshold. `slide_speed_ms` participates in the JOINT sustained condition at `failure_modes.py:179-185` that produces the 16 SLIDE / 1 STUCK verdicts (D6b, D6c), so corrupting it changes published output without raising an error. **Deduplicate by name and unit, never by value.**

---

## SECTION E: vehicle and mesh, T1

**E1. Canonical mesh.** `yaris_coarse_v1l_watertight.ply`, 327,212 verts, 655,308 faces, volume 3.542739 m3. NCAC/CCSA 2010 Toyota Yaris coarse FE deck, DOI 10.13021/G8JS5D.

**E2. FloodScene `vehicle.py:162` samples the mesh down to 60,000 surface points before solidifying.** The source mesh's watertightness does not survive that step. The measured fill_ratio 1.0024 result stands, but do not claim watertightness propagates through the pipeline.

**E3. The three AR&R mass classes are one hull with mass overrides only.** 1100 / 1609 / 2337 kg. Run logs print 8,905 particles for all three, so geometry never changes. Class names denote which AR&R limit set was applied by kerb weight, nothing more. Rogue and Silverado meshes exist but never entered a simulation.

**E4. The Yaris class assignment is decided by 1.7 cm.** Length 4.2826 m in the July 24 ledger versus 4.30 m at `paper_draft.md:33`. That margin alone decides Small-passenger versus not. The 1100 versus 1078 kg mass difference does not change the verdict. **UNRESOLVED: which value the live `vehicle_params.py` uses.**

**E5. Three real Yaris masses exist.** 1045 kg (Smith, Modra and Felder), 1078 kg (NCAC), 1100 kg (MASH nominal, used here). Do not silently correct one to another.

**E6. 1609 and 2337 kg are unsourced** against `vehicle_params.py`, which holds 1100 / 1990 / 2300 and contains no density or friction fields at all.

**E7. Track 2's `can_it_ford_L2_mpm.py:26` hardcodes `VEHICLE_SIZE = (4.66, 1.79, 1.44)`**, a pre-Yaris placeholder 3.391x the canonical hull volume. Still unfixed. Do not cite Track 2 output.

---

## SECTION F: scene and reconstruction, T1

**F1. The L2 water is a parametric tank**, filled to a depth with a car in it, spanning the domain wall to wall with the vehicle footprint carved out. No road, camber, channel or terrain. Say "tank," not "flooded road."
**The tank is the CORRECT analogue for L1, not a limitation**, because the AR&R criteria were derived from stationary vehicles subjected to flow.

**F2. No video-reconstructed flood scene has ever entered a simulation.** gsplat is proven only on a non-flood bench scene.

**F3. The gsplat reconstruction is in arbitrary units, not metrically scaled.** `normalize_world_space` rescales median camera-to-subject distance to 1.0. Any splat-to-MPM bridge needs a metric scale-recovery step that does not currently exist. This is a specific technical blocker, not just an unwritten bridge.

**F4. The PhysGaussian kernel-to-MPM bridge exists as a concept and a citation, never as code.**

**F5. How velocity enters.** A particle-level Dirichlet velocity clamp on an upstream slab, re-applied every frame, plus a one-shot additive kick after 8 settle frames. Not a grid boundary condition, not mass inflow. Particle count is fixed at load.

---

## SECTION G: literature and citations, T2 unless noted

**G1. The AR&R / Shand et al. 2011 thresholds describe a STATIONARY vehicle subjected to flow**, not a vehicle driving under power. Stated, not inferred: every criterion table is titled "stationary vehicle stability," and "vehicle movement through flood waters" is listed among the gaps the data cannot assess. Smith, Modra and Felder state directly "Laboratory testing was completed with stationary vehicles."

**G2. The 3.0 m/s velocity cap is administrative.** Imposed to keep vehicle curves consistent with human-stability curves, not derived from vehicle data. The constant D×V form is also administrative, inherited from pedestrian stability work.

**G3. AR&R limits.** Still-water depths 0.3 / 0.4 / 0.5 m and D×V limits 0.30 / 0.45 / 0.60 m2/s for small passenger, large passenger, large 4WD.
**0.45 m2/s is BOTH the AR&R large-passenger threshold AND, separately, a value Azhar et al. 2026 propose for small passenger vehicles** under combined critical conditions, with the caveat that it "needs to be verified by further scenario testing." Never conflate the two uses.

**G4. Friction. `mu_wet ≈ 0.30` is REFUTED as a wet-road value.** 0.30 is the sand and gravel worst case in Smith, Modra and Felder 2019. Wet AND dry concrete both read about 0.78. Model-scale measurements run 0.52 to 0.68.
Any skill file asserting "mu_wet 0.3 is the primary, best-sourced defensible value" is WRONG and must be corrected.
`floor_friction` 0.55 remains defensible as a value between the sand-gravel floor and the concrete figure, but NOT as a conservative wet-road number. The specific attribution "0.55 per Azhar et al. 2023" has never been confirmed against that paper's full text.

**G5. Al-Qadami tested a PERODUA VIVA, not a Toyota Yaris.** Any claim that Al-Qadami found a Yaris floating at 0.40 m under about 11 kN buoyancy is a MISATTRIBUTION and must never be used. The verified full-scale Yaris source is Smith, Modra and Felder 2019, DOI 10.1111/jfr3.12527.

**G6. Unsteady flow raises drag 40 to 50 percent** relative to steady at matched conditions, varying approximately linearly with flow acceleration. Azhar et al. 2026, DOI 10.1111/jfr3.70181. Best-sourced of that batch, safe to cite directly. Steady baseline: Azhar et al. 2023, DOI 10.1111/jfr3.12885.

**G7. Artificial sound speed can qualitatively flip a rigid-body outcome.** Isik and He 2022, DOI 10.1007/s40571-022-00511-8. Neutrally buoyant cylinder in Poiseuille flow, not a vehicle, so magnitudes do not transfer. No vehicle-flood or MPM study isolates this parameter; state that explicitly if cited.

**G8. NEGATIVE FINDING, handle as one.** No flood-vehicle study demonstrates that mesh or particle resolution changes the predicted slide, float or topple threshold. **Do not cite any flood-vehicle paper as proof that resolution moves the stability threshold.** Al-Qadami et al. 2023, DOI 10.3390/su151713262, is the one flood-vehicle paper with a formal mesh-independence study, but its convergence metric was flow velocity and Froude number, not the stability threshold. If the claim is needed, support it only with general automotive CFD and state the domain mismatch.
This gap is why Josie's grid study is a potential contribution rather than only a weakness.

**G9. Ground slope matters and is unmodeled.** Xia et al. 2014: incipient velocity for a small passenger vehicle on a 1:50 slope is about 25 percent lower than on flat ground at 0.25 m depth.

**G10. Xia 2011 and Shu 2011 full text are NOT RETRIEVABLE.** Both `isOa: false`, `oaStatus: closed`, `contentDenied: true` on Scite, and absent from the Scholar Gateway corpus. Neither PDF is local. Correct behaviour is to stop, not to reconstruct from citing papers. Route: UT Austin library proxy or ILL.
Xia, Teo, Lin, Falconer 2011, Natural Hazards 58(1):1-14, DOI 10.1007/s11069-010-9639-x. Shu, Xia, Falconer, Lin 2011, J. Hydraulic Research 49(6):709-717, DOI 10.1080/00221686.2011.616318. Scite records Xia's date as 2010-10-20, the online-first date; 2011 is the correct citation year.

**G11. The "simplest sufficient abstraction" principle is PRIOR ART.** VVUQ adequacy-for-purpose (Oberkampf and Roy 2010; National Academies 2012; ASME V&V 40-2018), goal-oriented error estimation, control-relevant model reduction (Gevers and Ljung 1986), MDP state abstraction (Li, Walsh and Littman 2006). Deepest formalism: Blackwell sufficiency and Le Cam deficiency. Mature within silos, fragmented across them. Do not claim to have invented it. Distinguish from MDL/AIC/BIC, which are data-fit conditioned rather than decision conditioned.

**G12. The pipeline shape is also prior art**, as the digital twin decision pipeline (NASEM 2024, doi:10.17226/26894). Full four-criteria exemplars: Cadia tailings dam (doi:10.1680/jgeot.21.00399), rockfall runout back-analysis. It has not been transferred to vehicle flood traversability with external empirical validation. **That fourth criterion is the differentiator.**

**G13. `arXiv 2607.00673`** (Low, Hsiao, Li, Thorpe, Topcu, Kumar) satisfies reconstruction, simulation and decision but explicitly NOT external empirical validation; the authors state the environments "exist only in simulation."

---

## SECTION H: repo state, T1

**H0. `grep` in this environment silently skips gitignored paths, and that invalidates bare repo-wide audits. Confirmed live 2026-08-07.** `declare -f grep` shows a shell function wrapping ugrep with `--ignore-files`. `.gitignore:14` is `renders/` and `:10` is `data/*`, so `grep -rn "pattern" .` from the repo root omits `renders/yaris_render_s1/` entirely: `sim_standing.py`, `vehicle_live.py`, `gates.py`, `gates_all_runs.py`, `gates_both_scenarios.py` and all 17 runs' `metrics.csv`. Measured on the gravity inventory for A6: **5 hits from `.`, 7 when `renders/` was named explicitly.** The two missing hits were `gates_all_runs.py:12` and `gates_both_scenarios.py:12`, both load-bearing.
Consequence: **an absent grep hit is not evidence of absence in this repo**, and any prior audit or "declared in N places" count produced by a bare recursive grep from the root is a floor, not a total. Re-run before citing one. Use `/usr/bin/grep -rn`, or name `renders/` and `data/` explicitly. Exclude `./can-it-ford/` (nested duplicate), `./third_party/` (vendored) and `./.claude/worktrees/` (27 stale copies, which otherwise multiply every hit roughly 20-fold: the same gravity pattern returns 80 raw hits, of which 73 are worktree copies).
This also means `check_claims.py --all`, which enumerates via `git ls-files`, cannot see `renders/` or `data/` either. Its counts are scoped to tracked files by construction.

**H1. `paper/canonical_2026-08-02/` is untracked BY DESIGN.** A PreToolUse hook denies edits: "Snapshot of overleaf/main. Editing it creates a silent second canonical source. Edit in Overleaf." Overleaf is canonical, `refs/heads/main` at `6466dfa1c9d1adb9753bc5d48d885ab1eee16971`. Root `paper/conference_101719.tex` is marked SUPERSEDED by commit `a991216`. **The two-paper-copy question is CLOSED.**

**H2. No history divergence.** `git rev-list --left-right --count origin/main...main` returns `0 9`. origin/main `6ae618c` is an ancestor. Reflog clean back to 2026-07-31. "23 commits ahead" was a stale summary; "no common ancestor with Overleaf" was a malformed command using `overleaf/master` when the branch is `main`.

**H3. warpmpm upstream and license.** MIT, `kks32/mpm-engine`, pinned SHA `544c93dd02cb9c7ead89e1155a62967243244fce`. Footnote, not a license risk: 5 of 8 vendored files came from unpinned main.

**H4. 32 worktrees exist**, one prunable under `/private/tmp`, 29 directories under `.claude/worktrees/`. None contain a `.claude/skills` directory.

**H5. CLOSED 2026-08-07, superseded by a different merge path.** The Warp MPM figure-label fix is live on main via `b844118` ("Emit the Warp MPM label in the pipeline figure generator"), confirmed `git merge-base --is-ancestor b844118 main` and confirmed live in `analysis/paper_fig_pipeline_diagram_v2.py:92` ("Warp MPM", not "Genesis MPM"). The originally identified commits, `claude/verify-execute-code-changes-d89fd8` (7390168) and `claude/bibliography-formatting-fix-4c3864` (f302ce0), are NOT ancestors of main and are now redundant, not pending. Do not cherry-pick either; the change they contain already exists on main through a different history.

**H6. The same script on two machines can differ on a physics input.** Mac `can_it_ford_L2_mpm.py:147` passes no `rho` to `gs.materials.MPM.Liquid()`; Vista `:148` passes `rho=1000.0`. Before citing any parameter read on one machine, confirm which machine ran the result.

**H7. `VERIFIED_FACTS_LEDGER_july24.md` and its `_GRIDAWARE` sibling are byte-identical except one sentence at line 307 of each.** V24 says "the 17 gated runs"; GA says "the 17 runs in render_s2." The whole fork is that sentence.

**H8. A nested duplicate `can-it-ford/can-it-ford/` tree exists** on Vista and inside the Mac repo root, with differing `scenario_sweep.csv`, `vehicle_params.py` and `ford_sweep_driver.py`. Verify pwd and git root before trusting any read.

---

## SECTION I: claims to DELETE on sight

Any skill file containing any of the following must be corrected in place.

| Delete | Replace with |
|---|---|
| "Genesis MPM" as the solver of the 17 runs | warpmpm, A1 |
| "gravity is unknown / never set" | -9.81, A2 |
| `cfrc_coupling_vel` in a warpmpm context | No force accessor exists, A3 |
| "verify the coupling force direction" | Malformed; measure m·dv/dt, A3 |
| "μ_wet ≈ 0.3 is the primary defensible value" | Refuted, G4 |
| "grid_density 64 is safe / 96 is the crash threshold" | 80 and 88 pass, 90+ fails, C2 |
| "vehicle effective density 100-300 kg/m3" | 310.494, B5 |
| "Al-Qadami found a Yaris floating at 0.40 m" | Perodua Viva, G5 |
| DRIFT_THRESHOLD from Smith et al. 2019 Eq. 6 | No peer-reviewed source, D7 |
| "23 pairs / 16 divergences / 30.4 percent" | Unusable under any characterization, do not cite |
| "which paper copy ships is open" | Closed, H1 |
| "the tank is a limitation" | The tank is the correct analogue, F1 |
| "measured inertia tensors informed the sim" | Only mass reaches the solver, A4 |
| "box proxy vehicle" for the 17 runs | Real Yaris hull, E1 |
| "a flood-vehicle study shows resolution moves the threshold" | Negative finding, G8 |
| "the splat bridge just needs writing" | Also needs metric scale recovery, F3 |

---

## SECTION J: open, do not state as resolved

1. Run the coupling-force validation. Variant C on the free particle rigid body: C2 equilibrium float draft against Archimedes, C1 initial submerged acceleration `a = g(rho_w/rho_box - 1)` giving `F_buoy = m(a+g)`. Run at the canonical resolution AND one refinement. A coarse-case miss is a finding, not a failure. Never tune a threshold to force a pass.
2. CLOSED 2026-08-07, superseded: H5.
3. CLOSED 2026-08-07, D6h and D6i. The two `failure_modes_result.json` citations were repointed by `841d666`; the surviving independence overclaim in `four_rung_ladder.md` was fixed separately the same day. Note `841d666`'s message claimed to close this item but never edited this register, which is why it sat open for a day after the work was done. **A commit message is not a register edit.**
4. CLOSED 2026-08-07, D6a and D6b. The classifier ran on all 17 on 2026-08-05 and was re-verified live 2026-08-07. Same caveat as item 3: `841d666` claimed the closure without making it.
5. Which length `vehicle_params.py` actually uses, E4.
6. Retrieve Xia 2011 and Shu 2011 via library proxy, G10.
7. The velocity tail in `channel_recirc_v2`: 329 of 3.66M particles over the Torricelli cap at bulk mean 1.008 m/s.
8. CLOSED 2026-08-07, was a false premise: the in/outflow BC paper (Zhao, Bolognin, Liang, Rohe, Vardon 2019, DOI 10.1016/j.compfluid.2018.10.007) is not Kumar's, it was implemented in Anura3D by a Cambridge/TU Delft/Deltares team unrelated to cb-geo/mpm. No reason to expect it merged there.
9. Whether the p2g source read matches genesis 1.1.1 rather than 1.2.0, C1.
10. DesignSafe DOI pending Kumar sign-off.


## Addendum, 2026-08-06

F3 and F4 are partially superseded. `bridge/config.py`, `extract.py`,
`filling.py`, `gaussian_io.py`, `genesis_particles.py`, `run_bridge.py`,
and `scale_calibration.py` are committed (`837c554`, `b0579f2`) and
contain a real splat-to-Genesis-particle bridge plus a real metric
scale-recovery step, calibrated against a photographed reference object.
Both target Genesis, not warpmpm. Neither has produced a validated
result. Committed is not validated: do not cite either as validated until
someone actually checks the bridge's output particles or the calibration
script's derived scale against ground truth.

## ADDENDUM 2026-08-07

K1. drainA COLMAP directory structure is correct, not broken. Confirmed live via find /scratch/11603/jcerrell0629/drainA -maxdepth 3 on LS6: sparse/0/ holds cameras.bin, images.bin, points3D.bin, rigs.bin, frames.bin; images/ holds all captured jpgs. This was already fixed by an earlier session before this one ran. Any earlier note calling the gsplat AssertionError about a missing sparse directory still blocked is stale as of this date.

K2. gsplat_env has a slow first-import chain that reads as a hang. On LS6 node c301-004, simple_trainer.py appeared to hang after launch. Confirmed via Ctrl+C traceback: mid-import of torchmetrics to matplotlib to ft2font, a compiled extension, not a real error. nvidia-smi showed 0 percent GPU across all three A100s and no running process; ss -tnp showed no open network connection, ruling out an outbound-download stall. Root cause is cold-cache reads of shared gsplat_env on Lustre scratch. Standing rule: wait 3-5 minutes on first run in this env before assuming failure.

K3. Diagnostic playbook for a job that seems hung on TACC. squeue -u jcerrell0629 from a second terminal confirms the job is alive. nvidia-smi and ps aux on the reported node show GPU and process state. ss -tnp checks for a stalled outbound connection. time python3 -c import X twice in a row isolates a slow import from a real hang.

K4. Open as of this date. Whether the matplotlib import timing test was run, and whether simple_trainer.py completed a training run on drainA, were not confirmed in this session.
