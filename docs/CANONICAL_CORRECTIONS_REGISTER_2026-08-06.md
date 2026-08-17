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
**Provenance note added 2026-08-12, found by `.claude/checks/register_integrity.py`.** Both of those are UPSTREAM `kks32/mpm-engine` SHAs, not can-it-ford commits, and neither resolves in this clone: `git cat-file -e fd390d6` returns "Not a valid object name". Resolve them this way instead. `544c93dd` is the pin, recorded in full at `third_party/mpm-engine-544c93dd-solver-core/PINNED_SHA.txt` and `third_party/mpm-engine-544c93dd/PINNED_SHA.txt` as `544c93dd02cb9c7ead89e1155a62967243244fce`. `fd390d6` is `fd390d69ecfd1598f56803a215bb8d0eb7231d85`, recorded as the `repo_head` field at `renders/yaris_render_s1/geom_live.py:12` and `analysis/render_v1/geom_live.py:12`. **Never read either as a can-it-ford commit**, and do not conclude from a failed `git cat-file` that the citation is fabricated.
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

**This fork now reaches published output.** `failure_modes.py` uses G at `:170` (`surge_accel_g`) and `:174` (`weight_n`), and the classifier has run on all 17 runs (D6b), so 9.80665 fed the published verdicts. Any statement that it never influenced a gated result is retracted.

**CLOSED 2026-08-12. The unification was performed and the prediction was half right.** `failure_modes.py:14` is now `G = 9.81`; `analysis/classify_failure_modes.py` was re-run and **16 SLIDE / 1 STUCK holds**. All 17 run-to-mode pairs and all `triggered_slide/topple/float` flags are byte-identical before and after. Exactly 3 of 33 columns moved, all direct functions of G: `ratio_topple`, `peak_surge_accel_g`, `weight_n`.

**This entry's own stated REASON is REFUTED, even though its conclusion held.** It claimed "all 13 sub-threshold margins are far larger than 0.034 percent". They are not. `g48_m2337` sat at `ratio_topple` 1.000244, a margin of **0.0244 percent above 1.0, which is SMALLER than the 0.0342 percent change**, and it crossed: 1.000244 -> 0.999903. No verdict moved, because TOPPLE triggers on a sustained joint condition and not on the peak ratio (D6c), so the crossing changed a magnitude and not an outcome. Recorded because the entry told the reader to "verify rather than assume" and the assumption embedded in its own justification was the thing that failed. A conclusion reached for a refuted reason is not verified.
Consequence for D6c, applied there: the "ratio >= 1 in 13" figure is now 12.

**A7. `friction` on warpmpm's collider path IS a Coulomb coefficient, not numerical damping. T1, verified live 2026-08-07** against the pinned vendored core, `third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py:2729`, inside the branch commented `separable + Coulomb friction`:

```python
scale = wp.max(0.0, tlen + param.friction * vn) / tlen
v_tan = v_tan * scale
```

`vn` is the into-surface normal component, `tlen` the tangential magnitude. Reduce tangential velocity in proportion to the normal component, floored at zero: the textbook Coulomb rule. External report `5e706c91` reached the same classification by reading live GitHub through DeepWiki; this entry rests on the vendored pin, which is the stronger source.
**Do not merge this with Genesis `coup_friction`.** They are different parameters in different engines that happen to share a role. Genesis `coup_friction` is separately confirmed as Coulomb at `legacy_coupler.py:322` (CLAUDE.md, 2026-08-05); the Genesis numerical regularisation parameter is `coup_softness`, default 0.002. A skill file asserting either one is "numerical only" is refuted, see Section I.
Incidental but relevant to A3: this same read shows the SDF path accumulating `param.force` and `param.torque` by `atomic_add` of the grid impulse. That is consistent with A3, not a contradiction of it. A force accessor exists, but only on kinematic colliders, and the 17 runs never create one.
Caveat on the source report: **`5e706c91`'s Task B failed outright.** It could not access `jcerrell-IS/can-it-ford` by any method and reports zero findings, positive or negative, about this repo. Never read its conclusions as having been checked against our code. Verified 2026-08-08 by direct read of the report file: its own summary states "I could NOT access this repository by any method and am reporting all of Task B as UNVERIFIED," so this caveat is exact, not a paraphrase.
**Second caveat, added 2026-08-08, and the reason the first one matters.** `5e706c91` itself repeats the refuted Genesis claim. Its analysis section contrasts warpmpm's `friction` with "a Genesis `coup_friction`, which the task correctly describes as a numerical coupling parameter of a different track." That is WRONG, per CLAUDE.md and confirmed 2026-08-05 against `legacy_coupler.py:322`. The report is sound on the half it actually read (warpmpm, via live GitHub) and unsound on the half it did not. Take only the warpmpm half.

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
`data/track1_sweep_v2/manifest.csv` is superseded box-proxy output. Path corrected 2026-08-12: this entry previously cited it bare as `track1_sweep_v2/manifest.csv`, which does not exist at the repo root. The file is real and lives under `data/`, un-ignored by `.gitignore:17-18` because `analysis/gp_surrogate.py` and `analysis/build_poster_phase_space.py` still read it.

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

**D6c. `triggered_*` is the verdict, `ratio_*` is peak magnitude. They disagree.** SLIDE has ratio >= 1 in 17 of 17 runs but triggers in 16; TOPPLE has ratio >= 1 in **12** and triggers in 0; FLOAT has ratio >= 1 in 1 and triggers in 0. Each mode requires a JOINT displacement-and-speed condition sustained 3 consecutive frames (`failure_modes.py:179-185`), not a peak. **Any count taken by filtering on `ratio >= 1` is wrong**, and would report topples that never happened.

**COUNT UPDATED 2026-08-12, from 13 to 12, and the reason is this entry's own point.** The G unification in A6 (9.80665 -> 9.81) moved every `ratio_topple` by -0.0342 percent. `g48_m2337` was sitting at 1.000244 and crossed to 0.999903, leaving 12 runs at ratio >= 1. **No verdict changed**: `triggered_topple` is 0 in all 17 both before and after, which is exactly why the ratio count is not the verdict. Anyone citing "13" is citing a pre-2026-08-12 code state; anyone citing 12 or 13 *as a topple count* is making the error this entry exists to prevent. The stable statement, and the only one worth quoting, is **TOPPLE triggers in 0 of 17**.

**D6d. STUCK is not a fourth mode.** There are three outcomes, SLIDE / TOPPLE / FLOAT; STUCK is the "none sustained" early return (`failure_modes.py:229-230`) and carries no threshold, ratio-of-record or onset frame. Its winning-mode columns are deliberately EMPTY, not zero. Where two modes sustain, `:232` reports the last in `MODE_SEVERITY`, i.e. FLOAT > TOPPLE > SLIDE.

**D6e. `metrics.csv` `pitch_deg` / `roll_deg` are VEHICLE-BODY-SENSE, not raw Euler.** `vehicle_live.py:55-61` computes raw ZYX Euler, then `:295-300` swaps two before writing, so `roll_deg` is the raw Euler pitch (about y, the long axis). The ZYX gimbal singularity is at `|roll_deg| -> 90` and degenerates yaw and pitch, not roll. **It cannot affect any verdict here: the classifier reads neither column.** TOPPLE is an acceleration test, not an angle test. Max `|roll_deg|` over all 17 runs is 4.625 deg.

**D6f. `peak_surge_accel_g` is numerical, not physical.** It is `np.gradient(vel, t)` (`failure_modes.py:127`) over a 30 Hz rigid-body trace; single-frame values reach 3.78 g. The `sustain_frames` guard is the only thing keeping TOPPLE from firing on all 13. Never quote the raw TOPPLE ratio alone.

**D6g. TOPPLE's use of SSF is the correct axis, but only by scene geometry.** SSF is a lateral rollover ratio and TOPPLE tests SURGE acceleration; that is right here ONLY because the vehicle's long axis is y while surge is x (`vehicle_live.py:277-278`), so flow strikes the side. Do not carry this criterion to any scene where the vehicle faces the flow. SSF 1.42 is an estimate flagged "CONFIRM before use" (`vehicle_params.py:108`); every TOPPLE ratio scales as 1/SSF. SLIDE, FLOAT and STUCK do not depend on it.

**D6h. `failure_modes_result.json` remains condemned, and this is unchanged.** It holds 3 entries keyed only by class label, carries no run identifier, and is written by no script in the repo. Unmodified since 2026-07-26. It was MISCITED as independent confirmation at `docs/four_rung_ladder.md:136` and `docs/four_rung_ladder_GRIDAWARE.md:136`; **both citations were repointed by `841d666` on 2026-08-07**. Do not re-report that specific miscitation as live.

**D6i. The defect that actually survived the repoint was the word "independently."** `four_rung_ladder.md` continued to claim the classifier "independently classifies" the three runs after the filename was corrected. It cannot: `simulation/failure_modes.py` reads the same `_incoming/<run>/metrics.csv` the table above it was built from, so it restates one rollout under an explicit criterion and corroborates nothing from a second source. Fixed 2026-08-07. The `_GRIDAWARE` sibling already carried the retraction. **Repointing a citation does not fix an independence claim; check the verb, not just the path.**

**D7. DRIFT_THRESHOLD 0.05 m has no peer-reviewed source.** Re-declared as a literal in 24 places under five names (count resolved 2026-08-11, see below; the earlier "16 places under three names" was a floor produced by a grep that skipped `renders/`). `gates.py:195-196` records in a print statement that it is a conservative numerical onset-of-motion tolerance.
The attribution to Smith, Modra and Felder 2019 Eq. 6 is a MISATTRIBUTION. That equation contains no such criterion.
**Count disagreement, RESOLVED 2026-08-11 by the `/usr/bin/grep` re-run this entry asked for.** Both prior counts were floors, as predicted. The live total is **24 declaration sites under FIVE names**, not 16 under three or four:

| name | sites |
|---|---|
| `DRIFT_THRESHOLD` | 9 |
| `L2_DRIFT_M` | 7 |
| `DRIFT_THRESHOLD_M` | 5 |
| `THRESHOLD` | 2 |
| `DRIFT_M` | 1 |

Scope of the count: `renders/` and `data/` included explicitly; `.git/`, `third_party/`, `__pycache__/`, `archive/`, `_archive/`, `session_archive/` and every `.bak*` file excluded. Counting only assignments of the literal, not mentions in prose or f-string labels.

**`L2_DRIFT_M` is a FIFTH name that neither this entry nor CLAUDE.md item 13 ever named**, and it is the second most common one, at 7 of the 24 sites: `analysis/make_poster_figures{,_BIG,_GRIDAWARE,_BIG_GRIDAWARE}.py`, `deliverables/figures_src/make_poster_figures_accessible.py`, and the two `deliverables/for_kumar*/03_scripts/` copies. Six of those seven are POSTER FIGURE GENERATORS, so the name absent from both inventories is the one closest to a formal deliverable. It was previously recorded only at `docs/COUPLING_VALIDATION_J1_2026-08-07.md.bak-premerge:318`, which is UNTRACKED, i.e. the finding existed solely in a file git would not have preserved.

These 24 are distances. They are separate from the three `0.05` literals in `failure_modes.py` covered by D7a below, one of which is a speed. Total `0.05` literals in live code is therefore 27, of which 26 are distances and 1 is a speed. **Deduplicate by name and unit, never by value.**

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

**E3a. CORRECTION 2026-08-11. Both hulls entered simulations; the "never entered a simulation" clause above is stale.** Rogue and Silverado ran through the free-rigid path at canonical g64 in job 896273 (class_specific_2026-08-08.sbatch, 2026-08-07T23:16:40) and through a matched-dx / fixed-g96 sweep in job 896302, both verified live 2026-08-11 against Vista summary.json files and tracked non-canonically in data/class_specific_runs_2026-08-08.csv (commit c375adc). See docs/MULTIGEOM_VALIDATION_2026-08-11.md for full results. The rest of E3 is unaffected: the three AR&R mass classes remain one Yaris hull with overrides only, and this correction does not fold Rogue/Silverado into the canonical 17-run store.

**E4. The Yaris class assignment is decided by 1.7 cm.** Length 4.2826 m in the July 24 ledger versus 4.30 m at `paper_draft.md:33`. That margin alone decides Small-passenger versus not. The 1100 versus 1078 kg mass difference does not change the verdict. **UNRESOLVED: which value the live `vehicle_params.py` uses.**

**E5. Three real Yaris masses exist.** 1045 kg (Smith, Modra and Felder), 1078 kg (NCAC), 1100 kg (MASH nominal, used here). Do not silently correct one to another.

**E6. 1609 and 2337 kg are unsourced** against `vehicle_params.py`, which holds 1100 / 1990 / 2300 and contains no density or friction fields at all.

**E6a. AMENDED 2026-08-07. Both masses now have an external source, though still not one in `vehicle_params.py`.** T2, external report `b0d2664f`: all three mass points map onto real CCSA / George Mason FE vehicle models at `ccsa.gmu.edu`, to the kilogram.
1100 kg = 2010 Toyota Yaris (1100C), the same vehicle family as `yaris_coarse_v1l_watertight.ply`. **1609 kg = 2020 Nissan Rogue**, VIN 5N1AT2MT6LC742896, 5-door SUV, v3 August 2024, 3,240,729 elements. **2337 kg = 2018 Dodge Ram 1500**, a 2270P test vehicle, detailed v3a 2,680,106 elements.
This means the mass sweep is no longer "two of three masses unsourced." It is now "three masses traceable to named FE models, applied as overrides to a single Yaris hull." The E3 caveat is unchanged and still governs: geometry never changes, run logs print 8,905 particles for all three, so this is a mass-sensitivity study on one hull, NOT a comparison of three vehicles. Do not upgrade the claim past that.
Before this enters the paper, confirm the masses on the CCSA model pages directly. The report is a single external source and the mass agreement is exact enough to be worth one live check.

**E8. NEW 2026-08-07, RENUMBERED AND SOURCE-CORRECTED 2026-08-08. NCAC / CCSA vehicle-mesh redistribution rights are NOT established. Treat as a blocker, not a footnote.** This item was written as a second **E7** and collided with the Track 2 item immediately below it. It is E8. The register is cited by item number, so a duplicate number is a citation defect, not a cosmetic one.

**CORRECTION 2026-08-08, both source reports were read directly instead of through this entry's own summary: `b0d2664f` and `289743f7` do NOT conflict, and the reasoning gap previously attributed to `b0d2664f` is not in it.** `b0d2664f` states in its own words that "Contractor-authored works are not automatically public domain under 17 U.S.C. 105," that the CCSA GMU site has "NO model license, NO copyright statement, and NO redistribution grant," and it records the CCSA licence status as "UNRESOLVED ... stated as a genuine gap, not a permission." It reaches the same operative conclusion as `289743f7`. Never again describe these two as opposed, and do not attribute that inference error to `b0d2664f`.

What `b0d2664f` genuinely ADDS is a distinction the old wording erased: **NHTSA-hosted** copies carry the "public information and may be distributed or copied" statement, whereas **CCSA-hosted** copies (it names Rogue, Ram, 2014 Silverado) are licence-silent. `289743f7` independently establishes that DOI 10.13021/G8JS5D has an **empty `rightsList`**, was minted by GMU University Libraries on a validation *presentation* PDF rather than a Dataverse deposit, and so carries no CC0 waiver; GMU's Dataverse CC0 default does not reach it, and depositors can opt out of CC0 anyway.

**UNRESOLVED and load-bearing: which side of that line the canonical Yaris falls on.** E1 sources the hull to DOI 10.13021/G8JS5D, which resolves to `ccsa.gmu.edu`, yet `b0d2664f` lists "older Yaris" among the NHTSA-hosted safe set. Both cannot be assumed. Settle this against the actual download page before publishing anything derived from the hull, and do not guess from the DOI alone.

**Operative rule, unchanged and still conservative: do not commit any derived NCAC/CCSA geometry to the public repo, and do not include it in a DesignSafe DOI, without written permission or a confirmed licence.** This gates J10. The rule survives the correction above because it never depended on the reports disagreeing. Separately from the mesh, the GNS code itself (`github.com/geoelements/gns`) is MIT and is safe to reuse, confirmed in `289743f7` against the README badge, the JOSS paper and arXiv:2211.10228.

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

**G1a. AMENDED 2026-08-07, the configuration detail behind G1.** T2, external report `baa355db`, which tabulates what was physically done in every foundational study. Load-bearing additions:
Restraint was by fine threads read as force (Bonham & Hattersley 1967 at 1:25; Gordon & Stone 1973 at 1:16), and Keller & Mitsch 1993 was a **desk study with no physical test at all**, assuming mu = 0.3 and Cd = 1.1. Direct buoyancy measurement on a real full-scale vehicle did not happen until the UNSW WRL program (Smith, Modra, Felder 2017 and 2019); everything earlier inferred buoyancy from displaced volume or model float depth.
**Channel blockage ratio and afflux corrections are essentially UNREPORTED across every incipient-motion study in this literature.** That is a limitation of the thresholds this project validates against, and our own tank has a computable blockage ratio, so it is also an opportunity. Do not claim the AR&R curves are blockage-corrected.
Model-scale watertight vehicles **float too shallow**, a sealing scale effect, and full-scale vehicles are somewhat more stable than the conservative AR&R curves (Kramer 2016 prototype; Smith, Modra, Felder). Yaw matters and was varied by several studies, with Kramer finding the critical angle at 45 degrees, and per-study mu varies strongly with yaw: Toda et al. 2013 report 0.26 at 0 degrees against 0.57 at 90 degrees for a sedan.

**G2. The 3.0 m/s velocity cap is administrative.** Imposed to keep vehicle curves consistent with human-stability curves, not derived from vehicle data. The constant D×V form is also administrative, inherited from pedestrian stability work.

**G3. AR&R limits.** Still-water depths 0.3 / 0.4 / 0.5 m and D×V limits 0.30 / 0.45 / 0.60 m2/s for small passenger, large passenger, large 4WD.
**0.45 m2/s is BOTH the AR&R large-passenger threshold AND, separately, a value Azhar et al. 2026 propose for small passenger vehicles** under combined critical conditions, with the caveat that it "needs to be verified by further scenario testing." Never conflate the two uses.

**G4. Friction. `mu_wet ≈ 0.30` is REFUTED as a wet-road value.** 0.30 is the sand and gravel worst case in Smith, Modra and Felder 2019. Wet AND dry concrete both read about 0.78. Model-scale measurements run 0.52 to 0.68.
Any skill file asserting "mu_wet 0.3 is the primary, best-sourced defensible value" is WRONG and must be corrected.
`floor_friction` 0.55 remains defensible as a value between the sand-gravel floor and the concrete figure, but NOT as a conservative wet-road number.

**G4a. AMENDED 2026-08-07. The "0.55 per Azhar et al. 2023" attribution is no longer unverified.** Citation-provenance audit, T2, external report `65474f37`: Azhar, Pauwels and Bui 2023 (DOI 10.1111/jfr3.12885, open access, correct title "Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements") **measured 0.55 themselves** with a spring balance on the rubber mat used as their road-surface proxy, and cite Wong, *Theory of Ground Vehicles*, only to show the value falls inside a handbook range of 0.50 to 0.70 for tyres on wet asphalt. Two-hop chain, terminating in a general-automotive handbook, not in a flood-specific measurement. So: it is a genuine measurement, but **of lab rubber mat, not of submerged asphalt**, and it sits at the high end of this literature's assumptions. The canonical paper at `paper/canonical_2026-08-02/conference_101719_1.tex:205` already states exactly this, independently; that text is now corroborated, not merely unrefuted.

**G4b. 0.30 is REFUTED as a measurement and REAL as a convention. Do not collapse the two.** G4 refutes 0.30 as a wet-road measured value, and that stands. Separately, 0.30 genuinely is the flood-vehicle literature's inherited convention: Shand et al. 2011 record that "correspondence with various road experts and test laboratories" settled on mu = 0.3, and Bonham & Hattersley 1967 and Gordon & Stone 1973 both adopt it. Anyone reading only the convention half will try to resurrect 0.30 as best-sourced and will be wrong. Anyone reading only G4 will call the AR&R derivation unsourced and will also be wrong. Measured comparanda, Shu et al. 2011 spring balance on wet carpet: Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68.

**G5. Al-Qadami tested a PERODUA VIVA, not a Toyota Yaris.** Any claim that Al-Qadami found a Yaris floating at 0.40 m under about 11 kN buoyancy is a MISATTRIBUTION and must never be used. The verified full-scale Yaris source is Smith, Modra and Felder 2019, DOI 10.1111/jfr3.12527.

**G6. Unsteady flow raises drag 40 to 50 percent** relative to steady at matched conditions, varying approximately linearly with flow acceleration. Azhar et al. 2026, DOI 10.1111/jfr3.70181. Best-sourced of that batch, safe to cite directly. Steady baseline: Azhar et al. 2023, DOI 10.1111/jfr3.12885.

**G7. Artificial sound speed can qualitatively flip a rigid-body outcome.** Isik and He 2022, DOI 10.1007/s40571-022-00511-8. Neutrally buoyant cylinder in Poiseuille flow, not a vehicle, so magnitudes do not transfer. No vehicle-flood or MPM study isolates this parameter; state that explicitly if cited.

**G8. NEGATIVE FINDING, handle as one.** No flood-vehicle study demonstrates that mesh or particle resolution changes the predicted slide, float or topple threshold. **Do not cite any flood-vehicle paper as proof that resolution moves the stability threshold.** Al-Qadami et al. 2023, DOI 10.3390/su151713262, is the one flood-vehicle paper with a formal mesh-independence study, but its convergence metric was flow velocity and Froude number, not the stability threshold. If the claim is needed, support it only with general automotive CFD and state the domain mismatch.
This gap is why Josie's grid study is a potential contribution rather than only a weakness.

**G9. Ground slope matters and is unmodeled.** Xia et al. 2014: incipient velocity for a small passenger vehicle on a 1:50 slope is about 25 percent lower than on flat ground at 0.25 m depth.

**G10. Xia 2011 and Shu 2011 full text are NOT RETRIEVABLE.** Both `isOa: false`, `oaStatus: closed`, `contentDenied: true` on Scite, and absent from the Scholar Gateway corpus. Neither PDF is local. Correct behaviour is to stop, not to reconstruct from citing papers. Route: UT Austin library proxy or ILL.
Xia, Teo, Lin, Falconer 2011, Natural Hazards 58(1):1-14, DOI 10.1007/s11069-010-9639-x. Shu, Xia, Falconer, Lin 2011, J. Hydraulic Research 49(6):709-717, DOI 10.1080/00221686.2011.616318. Scite records Xia's date as 2010-10-20, the online-first date; 2011 is the correct citation year.

**G10a. AMENDED 2026-08-07. A transcription now exists, T2, and J6 stays open anyway.** External report `266e9a8a` reports retrieving both full texts as author-accepted manuscripts on academia.edu, with Shu matched against the typeset *Journal of Hydraulic Research* version of record. Both final formulas, all force terms, both fitted coefficient tables, flume geometry and model scales are recorded in `docs/RESEARCH_ARTIFACT_INTEGRATION_2026-08-07.md` section 4.1. Load-bearing facts from it: **both papers formulate SLIDING ONLY**, neither derives a toppling equation, and neither publishes numeric CD, CL or mu inside the working formula, all of which are folded into two lumped flume-calibrated parameters. Both are flat-bed.
**J6 is NOT closed by this and must not be marked closed.** The route stated in G10 (library proxy or ILL) is still required, because the paper must cite the published article, not a transcription of a preprint, and only Shu was cross-checked against the version of record. What changed is that the equations are no longer unknown, so downstream work can proceed in parallel with retrieval. Do not cite the transcribed coefficients in the paper before the publisher PDFs confirm them.

**AMENDED AGAIN 2026-08-08, after reading `266e9a8a` directly instead of through this entry.** The report does substantiate G10a: it claims verbatim transcription from author-accepted manuscripts on academia.edu and Cardiff ORCA, with Shu matched against the typeset *JHR* version of record and equation numbers and coefficient tables confirmed to match. **G10 and G10a are therefore NOT in conflict and must not be "reconciled" by deleting either.** G10 records the *publisher* paywall (Scite `isOa: false`), and a green-OA author manuscript is fully compatible with a closed publisher record.

One narrow contradiction survives and is UNSETTLED: `266e9a8a` says it retrieved full text from **Cardiff ORCA**, while an independent 2026-08-08 check reports that same ORCA record is metadata-only, "Full text not available from this repository," with no download and no request-a-copy control. Both cannot be right about the same repository. Resolve by opening the ORCA record directly, not by preferring the later date. Note separately that the 2026-08-08 run recorded in `docs/semi_empirical_baseline_findings.md` also failed retrieval, but via Scite and Unpaywall, which tests the publisher route and NOT the green-OA route, so it is not evidence against `266e9a8a`.

**Bibliographic note, now settled: Xia 2011 and Xia 2014 are DIFFERENT PAPERS, not a year error.** 2011 (*Natural Hazards*) is the flat-bed sliding formulation; the 2014 companion adds slope and orientation. A document referring to "Xia 2014" is not necessarily misciting G10. `266e9a8a` also records a fourth-author discrepancy on the 2014 accepted manuscript, Caiwen Shu on the post-print against Yejiang Wang on the version of record under the same DOI, which is an author-list revision and not a content difference. Cite the version of record.

**G11. The "simplest sufficient abstraction" principle is PRIOR ART.** VVUQ adequacy-for-purpose (Oberkampf and Roy 2010; National Academies 2012; ASME V&V 40-2018), goal-oriented error estimation, control-relevant model reduction (Gevers and Ljung 1986), MDP state abstraction (Li, Walsh and Littman 2006). Deepest formalism: Blackwell sufficiency and Le Cam deficiency. Mature within silos, fragmented across them. Do not claim to have invented it. Distinguish from MDL/AIC/BIC, which are data-fit conditioned rather than decision conditioned.

**G12. The pipeline shape is also prior art**, as the digital twin decision pipeline (NASEM 2024, doi:10.17226/26894). Full four-criteria exemplars: Cadia tailings dam (doi:10.1680/jgeot.21.00399), rockfall runout back-analysis. It has not been transferred to vehicle flood traversability with external empirical validation. **That fourth criterion is the differentiator.**

**G13. `arXiv 2607.00673`** (Low, Hsiao, Li, Thorpe, Topcu, Kumar) satisfies reconstruction, simulation and decision but explicitly NOT external empirical validation; the authors state the environments "exist only in simulation."

**G14. NEGATIVE FINDING, handle as one. No `v_max(depth, flow_velocity)` exists in the literature.** T2, external report `045982be`. No peer-reviewed paper, standard or design guide expresses a recommended safe crossing speed as a function of BOTH depth and flow velocity. The field is threshold-based, not speed-based. The closest single-variable result is Pregnolato et al. 2017, `v = 0.0009w^2 - 0.5529w + 86.9448` (w in mm, v in km/h, R^2 = 0.95), which is **depth-only**, is a driver-control and serviceability advisory rather than a stability criterion, and treats the road as impassable at 0.30 m. Do not present Pregnolato as a stability result and do not present it as velocity-aware.
Two bodies of work must never be conflated: driver-visibility, braking and aquaplaning speed advisories (about tyre-road traction) versus vehicle-stability criteria (float, slide, topple). Aquaplaning models (Gallaway, Horne, Ong and Fwa) are genuinely speed-dependent and validated, but they are functions of water-film thickness and tyre pressure, not of floodwater sweep. Citing one for the other is a category error.

**G15. NEGATIVE FINDING, handle as one. No coupled flood simulation applies propulsive force or engine torque.** T2, external report `c963203d`. Across SPH, MPM, CFD and SWE-DEM, the vehicle is universally a passive rigid or rigid-linked body under drag, buoyancy and friction, Azhar et al. 2023 included. No propulsion force or torque value, from any manufacturer spec, dynamometer or assumption, is stated anywhere in that literature.
The underlying physics IS established: `F_F = mu(W - B - L)`, buoyancy reduces the normal force and therefore the available friction. Smith, Modra and Felder 2019 measured it directly with a winch and dynamometer on full-scale vehicles. Arrighi et al. 2015 states buoyancy and lift "reduce the normal component of the weight thus promoting sliding conditions even for very low water depths." Shah, Mustaffa, Kim and Yusof 2018 (DOI 10.1051/matecconf/201820307003) is the closest prior work, adding an engine driving force `F_DV` to the sliding balance.
**Consequence for this project: the passive-body treatment is standard practice, not a shortcut, and a self-propelled traction budget is a genuine unfilled gap.** State it that way. Do not describe the passive treatment as a limitation without also stating that every published study shares it.

**G16. There is NO accepted particle or force convergence criterion for SPH or MPM.** T2, external report `211aad60`, and consistent with L-3. No formally validated criterion specifies how many particles or cells must span the flow depth or the body before drag, lift and overturning moment become resolution-independent. Published resolutions are wildly inconsistent, roughly 2 to 60 across a load-bearing feature. Where convergence is claimed it is typically demonstrated on free-surface elevation or pressure and merely asserted for force, not quantified to a stated tolerance.
Refines G8 and L-4: coarse resolution most often OVER-predicts peak hydrodynamic force, via kernel truncation, particle deficiency and neglected air cushioning, **but this is a documented tendency with clear exceptions, not a law.** Do not write "coarse over-predicts, therefore our NO-FORD verdicts are conservative" as though it were guaranteed. State it as the likely direction and cite the exception.

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
| "`coup_friction` is a numerical stability coefficient, not Coulomb" | Refuted, CLAUDE.md and A7 |
| "warpmpm `friction` is numerical damping" | Coulomb, verified at `mpm_solver_warp.py:2729`, A7 |
| "the 0.55 / Azhar 2023 attribution is unverified" | Now confirmed, G4a |
| "1609 and 2337 kg are unsourced" | Nissan Rogue and Dodge Ram, E6a |
| "NCAC/CCSA meshes are public domain, safe to redistribute" | Contractor works, rights NOT established, E8 |
| "`b0d2664f` says the CCSA meshes are redistributable" | It says the opposite; the two reports agree, E8 |
| "DRIFT_THRESHOLD is grounded in Xia 2014 / Shah 2018" | No source at all, D7 |
| "coarse resolution over-predicts force, so we are conservative" | A tendency with exceptions, not a law, G16 |
| Pregnolato 2017 cited as velocity-aware or as a stability criterion | Depth-only, control-focused, G14 |

**Correction, 2026-08-07, to this table's own use.** Three of the rows above were found live in `vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md` and corrected in place that day: the `coup_friction`-is-numerical claim at `:97`, the "mu_wet ≈ 0.3 is primary" claim at `:58`, and the DRIFT_THRESHOLD sourcing claim at `:62`. The file's name already contained the words "friction_corrected," which is precisely why nobody re-checked it. **A filename asserting a correction is not evidence of one.**

---

## SECTION J: open, do not state as resolved

1. Run the coupling-force validation. Variant C on the free particle rigid body: CV2 equilibrium float draft against Archimedes, C1 initial submerged acceleration `a = g(rho_w/rho_box - 1)` giving `F_buoy = m(a+g)`. Run at the canonical resolution AND one refinement. A coarse-case miss is a finding, not a failure. Never tune a threshold to force a pass.

   NAMING, 2026-08-12: the coupling-validation variant formerly written `C2` is now
   `CV2` (`CV2_equilibrium_draft`, emitted at `simulation/validate_coupling_force.py:586`).
   It collided with the unrelated gate metric `C2_veh_zmin_rise`, a summary-JSON key
   written by `renders/yaris_render_s3_enhanced/sim_enhanced.py:709` and gated at
   `gates.py:150-151`. `CV2` was the one renamed because it is the only one of the four
   colliding `C`-series identifiers that appears in **zero** stamped artifacts under
   `data/coupling_validation/`; coupling `C1_initial_submerged_acceleration` and
   `C3_neutral_buoyancy_null`, and the gate `C2_veh_*` keys, are all stamped and were
   therefore left alone. **The `C3` collision is unresolved and deliberately so**: gate
   `C3_oob_particle_frames` and coupling `C3_neutral_buoyancy_null` still share a token,
   and neither can be renamed without desynchronising a stamped artifact from its source.
   The CLI token `--variant c2` is unchanged, so existing sbatch invocations still work.

   J1a. RUNG (b) RAN AND FAILED; CAUSE CORRECTED ONCE, 2026-08-13. Rung (b),
   partially submerged, RAN on LS6 A100 as job 3361315 (`COMPLETED`, `0:0`,
   `00:34:21`) and FAILED: buoyancy read -18.9 percent at g64 and +115.0 percent at
   g96, and the body sank at one grid while accelerating upward at about 4 g at the
   other. Artifacts and full working are committed at
   `realism_track/rung_b_ls6_3361315/` and `realism_track/FINDINGS.md`.

   **CAUSE CORRECTED SAME DAY, 2026-08-13. Read this before the paragraphs below.**
   The first version of J1a named the added-mass ratio as the cause. That is
   WITHDRAWN. It was an inference, and an experiment refuted it: job 3361371 swept
   `--relax` 1.0, 0.5, 0.25 and under-relaxation, the documented remedy for
   added-mass instability, made the error **monotonically worse** at both grids
   (g64 0.8114 -> 0.8006 -> 0.7688; g96 2.1503 -> 2.1991 -> 2.3228) while
   `added_mass_ratio` held fixed. Job 3361423 closes it off: with the body held
   completely still the error is -48.49 percent at g64 and +349.55 percent at g96,
   so it does not require body motion, and fixed-body `Fz` sweeps 27,207 N peak to
   peak against a 16,233 N analytic, which is a ringing tank.

   THE ACTUAL CAUSES, both established:
   (i) The water was never settled. `rung_b_coupled.py:83` advanced one substep per
   iteration where `settle_pinned` (`simulation/validate_coupling_force.py:617-643`)
   advances one frame under a `sound_speed/vmax >= 20` gate. That gate is met at
   3,894 substeps at g64 and 12,416 at g96, so the 900 that ran were 23 percent and
   7.2 percent of the settling the reference needed. Fixed in `79fec32`.
   (ii) The comparison was never like-for-like. `run_c1_sdf`, which produced the
   -7.67/+7.28 percent rung-(a) figures, is FULLY submerged at frac 1.0 with 2.75 dx
   and 5.36 dx of water above the cube top; rung (b) realizes frac 0.5187 against a
   partial reference. Two different experiments were being compared.

   The identity below is RETAINED because it is true and constrains future scheme
   choice, but it is NOT the diagnosis for this failure.
   `simulation/coupling_force/coupler.py:121-130` defines
   `added_mass_ratio = rho_w * V_displaced / m_body`; `coupler.py:72` warns above
   0.5 and `coupler.py:36-42` calls a ratio near 1 the divergence point for a
   partitioned explicit scheme. A body floating at equilibrium satisfies
   `m*g = rho_w*g*V_disp`, so `rho_w*V_disp = m`, so **`added_mass_ratio` is exactly
   1.000000 for ANY body floating at equilibrium**, independent of size, shape, mass
   and density. The canonical Yaris hull confirms it numerically: 310.494 kg/m3
   floats at fraction 0.3105 and `(1000/310.494)*0.3105 = 1.0000`.

   Consequence for SCHEME CHOICE in later work, not for this failure: **every
   floating-vehicle case this project exists to simulate sits at twice that module's
   own warning threshold, by construction, with no parameter escape.** Reaching 0.5
   at the rung-b design submersion of 0.80 would require a body density of
   1600 kg/m3, which sinks rather than floats. Job 3361315 did print the module's
   warning on both grids and continue at `relax = 1.0`. Note that the error ordering
   with the ratio (0.8644 -> -18.9 percent, 0.9298 -> +115.0 percent) is a
   CORRELATION that the relax sweep has since shown is not causal; an earlier version
   of this entry read it as confirmation, which is exactly the trap.

   STATE OF THE MITIGATIONS, so none is re-proposed as untried:
   under-relaxation is DONE and refuted (job 3361371). The gated-settle rerun at the
   reference geometry is SUBMITTED as job 3361443 (`rung_b_settled.py`) and was
   PENDING when this was written; it is the decisive test. Reduced `dt` at fixed grid
   is untried. Implicit or monolithic coupling is disclaimed by `coupler.py:35-36`
   and would be new development.

   NOT VERIFIED, stated so it is not later mistaken for a primary read: the claim
   that a partitioned explicit scheme *diverges* near ratio 1 is `coupler.py`'s own,
   attributed there to Zhang et al. 2026, and that citation has not been checked
   against its source. The relax sweep is now evidence AGAINST that mechanism
   operating here, which is a further reason to verify it before relying on it. What
   is independently established is the identity (algebra), the 0.5 threshold (source
   read), and the two settle/configuration causes above (measured).

   J1b. RUNG (b) NOW HAS FOUR VALID MEASUREMENTS, AND THEY POINT AWAY FROM THE
   COUPLING, 2026-08-13. Job 3362208 on LS6 A100 re-ran rung (b) at g96 with the
   settle cap raised from 900 to 3000 frames and changed nothing else. Artifacts at
   `realism_track/rung_b_g96_gated_3362208/`, working in `realism_track/FINDINGS.md`.

   **The g96 discard was a cap artifact.** J1a's "the gated-settle rerun is the
   decisive test" ran as job 3361443 and BOTH its g96 runs were self-declared
   discards, `settle_gate_met false` at the 900-frame cap. With the cap at 3000 the
   gate is met at 1030 frames (coupled) and 1031 (fixed), `ratio_c_over_vmax` 20.54
   and 20.91. 900 was about 13 percent short. The g96 settle is reachable at partial
   submersion; it costs about 2.9x the frames g64 needs.

   **The four gate-met rows**, scored against `F_buoy_analytic_partial_N`, which is
   the correct reference for a partially submerged body and not the full-submersion
   number the stdout banner prints:

   | grid | mode | frac_sub | err vs partial |
   |------|---------|----------|----------------|
   | 64 | coupled | 0.7540 | -25.21 % |
   | 64 | fixed | 0.7548 | -49.92 % |
   | 96 | coupled | 0.8437 | -29.64 % |
   | 96 | fixed | 0.8445 | -32.51 % |

   **The divergence signature is retired.** J1a records the unsettled pair as -18.9
   percent at g64 and +115.0 percent at g96 and reads it as divergence. Settled, the
   same comparison is -25.21 and -29.64 percent: same sign, 4.4 points apart. The
   sign flip was an artifact of settling two grids for different physical durations.

   **THE LOAD-BEARING RESULT.** Fixed and coupled are 24.71 points apart at g64 and
   **2.87 points apart at g96**. A deficit that an SDF-fixed collider and a
   free-rigid force-coupled body both reproduce to within 2.9 points at the finer
   grid **is not primarily an artifact of the free-rigid coupling**. Any framing that
   calls the force-coupled path the broken one and the fixed collider the trustworthy
   baseline is unsupported at partial submersion, and at g64 it is backwards: the
   fixed collider is worse by 24.7 points. Note this is a FORCE-error comparison at
   partial submersion and does not by itself overturn the rung-(a) fully-submerged
   figures, which are a different metric at a different configuration.

   **NOT ESTABLISHED, recorded so this entry is not over-read.** The pair is
   confounded: realized `frac_submerged` is 0.754 at g64 against 0.844 at g96, so a
   second variable moves with the grid. A clean refinement test at matched realized
   submersion has NOT been run. **SUPERSEDED SAME DAY by J1d, which ran it.** And the
   constant-offset model is not confirmed by
   these numbers: the deficits as pressure over the 2.1662 m2 cross-section are 2747,
   5444, 3613 and 3967 Pa, not a resolution-independent constant, and none is the
   roughly 6.2 kPa job 3361504's direct profile reports. That discrepancy is open.

   **Rungs (c) and (d) still unattempted**, and the reason has changed. It is no
   longer that rung (b) lacks a valid measurement. It is that the deficit rung (b)
   exposes is unexplained and is not specific to the coupling path the ladder exists
   to test. A fixed-collider ladder cannot close this gap on its own in any case: a
   fixed collider cannot slide, so it can never reproduce a SLIDE outcome, and it can
   only bound how wrong the load is by a known factor.

   J1d. THE MATCHED-SUBMERSION TEST RAN, AND IT REVERSES J1b'S MECHANISM,
   2026-08-13. J1b's stated confound, that realized submersion moves with the grid,
   was removed by varying submersion with `--depth-cells` at fixed grid. Ten gate-met
   points, artifacts at `realism_track/rung_b_matched_submersion_3362208/`.

   Fitting the g64 rows against `frac_submerged` and evaluating at each g96 row's
   realized submersion leaves grid as the only difference:

   | mode | at frac | g64 interpolates | g96 measures | grid gap |
   |------|---------|------------------|--------------|----------|
   | coupled | 0.7800 | -26.47 % | -24.96 % | **1.51 pts** |
   | coupled | 0.8437 | -29.54 % | -29.64 % | **0.10 pts** |
   | fixed | 0.7757 | -48.95 % | -29.88 % | **19.07 pts** |
   | fixed | 0.8445 | -45.76 % | -32.51 % | **13.25 pts** |

   **The free-rigid force-coupled path is grid-converged between g64 and g96, to 0.10
   and 1.51 points. The fixed SDF collider is not, by 13.25 and 19.07 points.**

   **CORRECTS J1b's mechanism.** J1b says the coupled path "degrades slightly" under
   refinement, -25.21 to -29.64. It does not. That was the confound J1b flagged: at
   fixed grid, moving submersion 0.754 to 0.857 moves the coupled error -25.21 to
   -30.16, and the g96 point at 0.844 lies on that same g64 curve. J1b's convergence
   observation survives, but not its reading: the two paths do not meet at a shared
   physical answer, **the fixed collider converges toward the coupled path's already
   grid-stable value.**

   What this does NOT say: that the coupled path is correct. It carries a residual
   deficit at every point measured, about -25 percent at frac 0.78 rising to about
   -30 percent at frac 0.86. What it says is that the deficit is grid-converged and
   is therefore not a resolution artifact, so a finer grid will not remove it. It
   also means the working framing of the whole ladder, force-coupled path broken and
   fixed SDF collider trustworthy, is not supported at partial submersion; on grid
   convergence the ordering is reversed by more than an order of magnitude.

   DRIVER PROPERTY, so nobody repeats the dead end: **submersion is quantized.**
   `--depth-cells` 18.78 and 18.89 both realize frac 0.856 to 0.857 at g64 because
   water seeds in whole layers, so an arbitrary target submersion cannot be dialled
   in and the comparison above interpolates instead. The two near-duplicate g64 rows
   are an effective repeat measurement and agree to 0.04 (coupled) and 0.06 (fixed)
   points, bounding run-to-run scatter far below every gap above.

   J1e. THE LADDER RAN TO RUNG (d) AT THE GATED GEOMETRY, 2026-08-13. Rungs (b), (c)
   and (d) of `simulation/validate_coupling_force_ladder.py` all ran on LS6 and all
   met the settle gate. Artifacts at
   `realism_track/ladder_gated_geometry_3362208/`. **Note this is a DIFFERENT
   experiment from J1b and J1d**: those float a cube mid-water at frac 0.75 to 0.86,
   this puts the body's bottom face ON the floor at frac 0.20 with `water_depth_m`
   0.2944294473039918 and 4 layers, the `g64_m1100` gated values exactly.

   Settle cap again: at the default 1200 both rungs were `settle_is_discard true`
   (ratio 13.78 and 12.40 against 20). Raised to 5000, rung (b) meets it at 3490 and
   rung (c) at 1843. **Third distinct place a settle cap rather than the physics
   produced a discard.** The numbers barely moved between discard and gate-met
   versions.

   | rung | contact | a_late / a_ideal | v_mean_late | vertical travel |
   |------|---------|------------------|-------------|-----------------|
   | (b) | none | -4.2041 | -1.5854 m/s | -0.21208 m |
   | (c) | floor rest. 0.05 | -0.0006 | -0.0441 m/s | -0.03660 m |
   | (d) | (c) + flow 1.5 m/s | -0.0040 | -0.0408 m/s | 0.00000 m |

   **PREDICTION (b) REFUTED.** The pre-registered value was `a_late ~ 0` with drift
   -0.13 m/s bounded to -0.09/-0.17. Measured drift -1.5854 m/s, about 12x and far
   outside the band, with `a_late` +28.4 m/s2. Treat rung (b) here as DEGENERATE
   rather than merely wrong: at frac 0.20 and `rho_box` 600 the body must sink and
   with all planes at restitution 0.0 nothing holds it, so it ends at `box_bottom`
   0.2319 against `floor_z` 0.4416, below the floor plane. There is no equilibrium to
   measure.

   **PREDICTION (c) CONFIRMED.** Registering the floor at restitution 0.05 arrests the
   descent: travel -0.21208 -> -0.03660 m (82.7 percent), drift -1.5854 -> -0.0441 m/s
   (97.2 percent), `a_late` +28.4 -> +0.0042 m/s2, which is 0.06 percent of analytic.

   **CONSEQUENCE.** In the regime the 17 runs occupy, with the gated floor contact and
   then the gated flow, vertical acceleration is 0.06 and 0.40 percent of analytic and
   vertical travel is 0.037 m then exactly 0.000 m. **The floor contact, not the
   buoyancy coupling, sets the vertical dynamics there**, so the roughly 30 percent
   buoyancy deficit of J1b/J1d has very little leverage on a floor-supported body.

   **THIS DOES NOT CLEAR THE VERDICTS, and the limitation is structural.** The ladder
   records vertical quantities ONLY: `box_bottom_travel_m`, `v_series` and `zb_series`
   are all z, and there is no horizontal displacement, surge drift or x velocity
   anywhere in its output. It therefore cannot produce, refute or bound a SLIDE
   outcome, and SLIDE is 16 of the 17 verdicts. Rung (d) confirms the flow reaches the
   body (water `vx` near the box, mean 0.0018 -> 0.8304 m/s over 2735 particles) but
   not what that flow does horizontally. Closing the loop needs a horizontal-drift
   instrument that does not currently exist.

   J1c. THE RUNG-B EVIDENCE EXISTED ON ONE CLONE ONLY UNTIL 2026-08-13. The result
   JSONs and drivers for jobs 3361371, 3361423, 3361443 and 3361504 were committed on
   `/work/11603/jcerrell0629/vista/can-it-ford`, a clone 166 commits behind
   `origin/main` with a dirty working tree, and never pushed. `origin/main` carried
   the prose ABOUT those jobs (`6434258`, `ca9bdeb`, `d98837f`, `be20075`) while the
   evidence those commits cite was absent from the repo entirely. Recovered by
   `8695539`. `realism_track/FINDINGS.md` had also diverged on both clones from a
   shared base (`02f08eb` = `cdcdf9d`, sha256 `185968e0`); it was reconciled by
   three-way merge, purely additive at 496 insertions and 0 deletions, with a
   RECONCILIATION SEAM section marking which narrative supersedes which. **The
   standing lesson: a commit is not a backup. Prose about an experiment on one clone
   and the experiment's evidence on another is the state this project was in for a
   day, and neither clone alone was sufficient to check the other's claims.**
2. CLOSED 2026-08-07, superseded: H5.
3. CLOSED 2026-08-07, D6h and D6i. The two `failure_modes_result.json` citations were repointed by `841d666`; the surviving independence overclaim in `four_rung_ladder.md` was fixed separately the same day. Note `841d666`'s message claimed to close this item but never edited this register, which is why it sat open for a day after the work was done. **A commit message is not a register edit.**
4. CLOSED 2026-08-07, D6a and D6b. The classifier ran on all 17 on 2026-08-05 and was re-verified live 2026-08-07. Same caveat as item 3: `841d666` claimed the closure without making it.
5. Which length `vehicle_params.py` actually uses, E4.
6. Retrieve Xia 2011 and Shu 2011 via library proxy, G10. **STILL OPEN, but no longer blocking.** A full transcription now exists at T2, G10a, so the equations are known and downstream work can proceed. The publisher PDFs are still required before the paper cites the coefficients.
7. The velocity tail in `channel_recirc_v2`: 329 of 3.66M particles over the Torricelli cap at bulk mean 1.008 m/s.
8. CLOSED 2026-08-07, was a false premise: the in/outflow BC paper (Zhao, Bolognin, Liang, Rohe, Vardon 2019, DOI 10.1016/j.compfluid.2018.10.007) is not Kumar's, it was implemented in Anura3D by a Cambridge/TU Delft/Deltares team unrelated to cb-geo/mpm. No reason to expect it merged there.
9. Whether the p2g source read matches genesis 1.1.1 rather than 1.2.0, C1.
10. DesignSafe DOI pending Kumar sign-off. **NOW ALSO GATED ON E8:** if the DOI would include any derived NCAC/CCSA geometry, redistribution rights must be established in writing first. Sign-off does not resolve a licence question.
11. NEW 2026-08-07. Establish CCSA/NCAC mesh redistribution rights, E8. Blocks item 10 and blocks committing any derived mesh publicly. Narrowed 2026-08-08: the first concrete sub-question is whether the canonical Yaris hull is NHTSA-hosted (safe) or CCSA-hosted (licence-silent), which E8 records as unresolved.
12. NEW 2026-08-07. The three-mass FE swap-in is now *possible* and not done, E6a. The Rogue and Ram decks are LS-DYNA keyword files of shell elements in millimetres, multi-million elements, not watertight, exterior needs extracting. Gated on item 11 for anything public. Note `63a4b5d4`: `lsdyna-mesh-reader` reports element *sections*, not elements, so a "1 shell + 1 solid" count is a parsing artifact, not a mesh count. Verify with `len(deck.element_shell_sections[0].eid)` and grep the deck for `*INCLUDE`.
13. NEW 2026-08-07. Compute the tank's blockage ratio. G1a records that blockage and afflux corrections are unreported across the entire incipient-motion literature, which makes this both a limitation of the thresholds we validate against and a cheap self-contained contribution. Nobody has computed ours.
14. NEW 2026-08-07. Write the G14 and G15 negative findings into the paper's related-work and novelty framing. Both are defensible differentiators and neither is currently in the text.
15. **NEW 2026-08-13, and it is now the single highest-value open item: RUN THE CANONICAL SET AT g128.** A SLIDE verdict has been shown to be resolution-dependent. `analysis/classify_rogue_silverado_sweep.py`, calling the same `classify_timeseries` behind the 17, puts Silverado at **SLIDE at g64 and g96 and STUCK at g128** (`data/rogue_silverado_slide_classification_2026-08-13.csv`). It is not a drift-threshold failure: max drift at g128 is 0.0778 m, still 1.56x `slide_m`. It fails the JOINT drift-and-speed condition for 3 consecutive frames, the same signature as `sweepV_g64_v0p5`. Mechanism is the initial surge impulse weakening with refinement, peak `|vx|` 0.771 -> 0.360 -> 0.204 m/s. Passthrough does not explain it: Rogue's passthrough is flat, 9.95 -> 9.88 percent, while its drift still falls 67 percent.

    **The canonical set is exposed the same way.** `analysis/slide_verdict_fragility.py` measures each gated run's distance from the boundary. The assumption-free metric is `margin_frames`, the longest run of consecutive frames holding the joint condition minus the 3 required. **`g96_m2337` holds it for 4 frames: a ONE-FRAME margin, 0.033 s at 30 fps.** The m2337 series collapses **11 -> 10 -> 4** frames across g48/g64/g96, so the margin is closing with refinement and closing fastest for the heaviest vehicle, which is the same mass-ordering as the Silverado flip. Every other run has a margin of 7 frames or more. Metric is oriented correctly by construction: `sweepV_g64_v0p5`, the one STUCK run, returns margin -3 and `k_crit` 1.4957.

    NOT CLAIMED: that any gated verdict does flip. Different vehicle and mass, and `k_crit` assumes uniform scaling of `dx` and `vx` while refinement also changes trajectory shape (`onset_frame_slide` moved 3 -> 5). `margin_frames` assumes nothing and is the number to quote. **The direct test has never been run: the canonical set does not exist at g128.** Until it does, "16 SLIDE / 1 STUCK" is not established as grid-converged, and that should be said explicitly wherever the figure is published.
16. **NEW 2026-08-13. SIX OF THE SEVENTEEN CANONICAL MARGINS ARE NOT REPRODUCIBLE.** The 17 runs' `metrics.csv` do survive, at `/work/11603/jcerrell0629/vista/render_s2/<run>/`, with the full 15-column `FloodHistory` header including `vx,vy,vz`; they are missing from the checkout only because `.gitignore` re-includes `*.py` alone under `renders/`. Re-classifying them live reproduces **all 17 verdicts, 16 SLIDE / 1 STUCK**, so that headline is safe. It reproduces only **11 of 17 `ratio_slide` values**. The six `g48_*` and `g96_*` runs differ. Cause, from mtimes and provenance files: those directories were overwritten 2026-07-26 03:08-03:10 by job 866887 (`render_s2/conv_2026-07-25/00_provenance.txt`, start 2026-07-26T03:07:17), while `g64_*` still dates 2026-07-25 20:12 and the sweeps 01:59. **The frozen g48/g96 margins came from run outputs that no longer exist on this machine and no other copy is on disk.** Largest gap `g96_m2337`, frozen 1.80047 against 1.74225 live, 3.2 percent. Cite the frozen store for those six, but do not present them as independently checkable. **Note the coincidence with item 15: the most fragile verdict in the set is one of the six.**


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

K0. **Research artifact integration.** Twenty-nine external research reports were worked through on 2026-08-07. Their per-report disposition, provenance tier and the two inter-report conflicts are recorded in `docs/RESEARCH_ARTIFACT_INTEGRATION_2026-08-07.md`. That file is NOT canonical: everything from it strong enough to be canonical was written into this register as G1a, G4a, G4b, G10a, G14, G15, G16, E6a, E8 and A7. Anything in it not mirrored here is a lead, not a fact. Note that several reports turned out to be already integrated (G11, G12, G13, G1, G2, G6, G7, G8), so check this register before treating any report finding as new.
**Located on disk 2026-08-08, and this is how to re-verify any of them: the 8-hex ids in this register are real files**, `~/Downloads/compass_artifact_wf-<id>-*_text_markdown.md`. All ten ids cited in this register resolve. **33 such artifacts exist on disk against the 29 said to have been worked through, so roughly four are un-triaged**; do not assume the sweep was exhaustive. Reading a report directly rather than through a register summary has already caught two errors in this file, the E8 mischaracterisation and the G10a over-reading, so prefer the file over the summary whenever a claim is load-bearing.

K1. drainA COLMAP directory structure is correct, not broken. Confirmed live via find /scratch/11603/jcerrell0629/drainA -maxdepth 3 on LS6: sparse/0/ holds cameras.bin, images.bin, points3D.bin, rigs.bin, frames.bin; images/ holds all captured jpgs. This was already fixed by an earlier session before this one ran. Any earlier note calling the gsplat AssertionError about a missing sparse directory still blocked is stale as of this date.

K2. gsplat_env has a slow first-import chain that reads as a hang. On LS6 node c301-004, simple_trainer.py appeared to hang after launch. Confirmed via Ctrl+C traceback: mid-import of torchmetrics to matplotlib to ft2font, a compiled extension, not a real error. nvidia-smi showed 0 percent GPU across all three A100s and no running process; ss -tnp showed no open network connection, ruling out an outbound-download stall. Root cause is cold-cache reads of shared gsplat_env on Lustre scratch. Standing rule: wait 3-5 minutes on first run in this env before assuming failure.

K3. Diagnostic playbook for a job that seems hung on TACC. squeue -u jcerrell0629 from a second terminal confirms the job is alive. nvidia-smi and ps aux on the reported node show GPU and process state. ss -tnp checks for a stalled outbound connection. time python3 -c import X twice in a row isolates a slow import from a real hang.

K4. Open as of this date. Whether the matplotlib import timing test was run, and whether simple_trainer.py completed a training run on drainA, were not confirmed in this session.

## ADDENDUM 2026-08-15

Every item below was measured live on 2026-08-15 by a local Claude Code session with a
real shell. Nothing here is transcribed from a prior summary. Full working:
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/05_Repo_Clone_Inventory_2026-08-15.tsv`
and `06_Phase_C_Near_Duplicates_2026-08-15.tsv`.

L1. **THE REPO-CLONE SPRAWL IS 28 LOCATIONS AND 31.6 GB, OF WHICH 15.9 GB IS NON-CANONICAL.**
    Verdict split: 17 `NON_GIT_COPY`, 4 `ORPHANED_CLONE`, 3 `STALE_BACKUP`, 3 `CANONICAL`,
    1 `VENV_EXCLUDE`. `~/can-it-ford` is the canonical one and it is exactly at
    `origin/main` `1a868f3`, confirmed against the GitHub default branch, not against a
    cached ref. A pointer symlink now exists at
    `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_CANONICAL_REPO`.
    **METHOD WARNING, this is the trap.** Asking each clone whether its HEAD is an
    ancestor of `origin/main` answers using THAT CLONE's own cached remote-tracking ref,
    which is stale by construction in a backup. Four clones report "0 ahead, 0 behind"
    while sitting at four different commits. The only sound test is to resolve the
    canonical SHA once from the live remote and then ask the canonical repo's object
    database about every other clone's HEAD.
    The 3 `CANONICAL` rows are not three copies of one repo: `~/can-it-ford-demo` is
    canonical for `jcerrell-IS/can-it-ford-demo` and `~/can-it-ford-paper` is canonical for
    the Overleaf remote. Both are separate remotes.

L2. **CLOSED: `CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07`, carried as blocked since Sprint 1,
    was never blocked. The recorded path was wrong.** It is not at
    `~/Archive/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07`; it is one level deeper, at
    `~/Archive/_ZZZ_DELETE_THESE_2026-07-17/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07`,
    inside the prior pass's own delete-staging folder. It holds 6 files and 44 KB, of which
    2 are `.DS_Store`. Of the 4 real files, 3 are exact-checksum duplicates of content
    Sprint 2 already catalogued and exactly 1 is new, `build_phase_space_v2.py`. A gap
    carried for weeks was worth one file. Its `scenario_sweep.csv` is a 5-column, 70-row
    copy, another instance of the snapshot the standing rules warn against.

L3. **THE CLAUDE.AI PROJECT'S GITHUB SYNC IS NOT WIRED TO THIS REPO.** The two synced
    sources are under `jcerrell-IS/mpm-engine`, which `gh repo view` confirms is a FORK of
    `kks32/mpm-engine` carrying `docs/ src/ tests/ examples/ experiments/`. This repo is
    `jcerrell-IS/can-it-ford`, a different remote with a different tree. Consequence, and it
    is load-bearing for anyone planning to "just commit it so Claude chat picks it up":
    **committing to `can-it-ford/docs/` does NOT reach the Project knowledge base.** The
    solver this project actually runs is vendored in-tree at
    `third_party/mpm-engine-544c93dd` with no `.git` of its own, so it is a vendored copy,
    not a submodule of the fork.

L4. **`~/can-it-ford-paper` EXISTS. The CLAUDE.md line saying it was deleted 2026-08-08 is
    stale.** Directory birth time is 2026-08-08 05:13, it holds 40 files, and its HEAD is
    `6466dfa` "Update on Overleaf." (2026-07-31), which is four commits past the `92ce4de`
    that CLAUDE.md records as the state at deletion. It is clean, 0 ahead and 0 behind its
    own `origin/main`, and matches this repo's `overleaf/main` ref. **The credential half of
    that CLAUDE.md entry still holds and was re-verified:** all five `can-it-ford*/.git/config`
    files are free of any `olp_` string. Presence was tested, no value was read or recorded.

L5. **TWO UNPUSHED COMMITS EXIST OUTSIDE THE CANONICAL REPO, and they are not equally safe.**
    (a) `~/can-it-ford-demo` HEAD `4d228d9` (2026-08-07) is **single-copy on disk and not on
    GitHub**. The live tip of `jcerrell-IS/can-it-ford-demo` is still `a10b037` (2026-07-23).
    That commit's own message says it fixes the L1 verdict to the joint AR&R rule and that
    the previous behaviour "used bare hazard product only, which overstated FORD cases in
    the 3.0-5.0 m/s range". So the **public demo repo currently serves the superseded rule**
    and the fix exists in exactly one place.
    (b) `~/can-it-ford-warpmpm-continue` HEAD `4924940` (2026-08-13,
    `analysis/run_provenance.py`) is one commit ahead of `origin/warpmpm-continue`
    `66912e3`. This one is NOT single-copy: the same commit is on local branch
    `warpmpm-continue` inside the canonical repo.
    **NOTE FOR `register_integrity.py`, which will flag `4d228d9` and `a10b037` as
    unresolved hex: that is CORRECT and expected, not a fabrication.** Both are commits in
    `jcerrell-IS/can-it-ford-demo`, a DIFFERENT remote, so neither object can exist in this
    clone. Resolve them with `git -C ~/can-it-ford-demo show <sha>` or
    `gh api repos/jcerrell-IS/can-it-ford-demo/commits/a10b037`. The checker searches this
    clone, `third_party/*/PINNED_SHA.txt` and the research artifacts only, so a
    cross-repository SHA is outside every one of its three resolution routes by
    construction.

L6. **PHASE C, CONTENT SIMILARITY: `make_phase_space.py` FORKS ON THE 0.60 BOUNDARY
    OPERATOR, AND FOUR OF THE SEVENTY SCENARIOS SIT EXACTLY ON IT.** A MinHash pass over
    6,090 in-scope text files found 6,540 pairs that are similar but NOT byte-identical.
    The sharpest is a one-character divergence in
    `designsafe-staging/scripts/make_phase_space.py`:
    `'FORD' if h <= 0.60` in 7 copies including the canonical repo, against
    `'FORD' if h < 0.60` in 2 copies, both of them pre-history-purge trees. The two files
    are 4267 and 4266 bytes, so a size-delta pass cannot see this and a checksum pass sees
    only "different" without saying why.
    `data/scenario_sweep.csv` has exactly 4 rows at `L1_haz` == 0.60: (0.2, 3.0), (0.3, 2.0),
    (0.4, 1.5) and (0.6, 1.0). So the operator is not academic.
    **NOT CLAIMED, and this matters:** no currently published verdict count turns on it.
    The live 10-column `scenario_sweep.csv` reads NO-FORD for all four boundary rows and
    totals 14 FORD / 56 NO-FORD, which is the JOINT AR&R rule, not this script's bare
    hazard-product rule. The exposure is forward-looking: `designsafe-staging/` is the
    publication-bound tree, and regenerating a figure from that script would produce a
    different answer than the canonical CSV for those four points.
    Scale note for anyone re-running this: of the 722 pairs at Jaccard >= 0.999, a sample of
    200 split 164 whitespace-or-CRLF-only against 36 with real content differences. Do not
    report the raw pair count as "near-duplicates found" without that split.

L7. **SKILL DRIFT, RE-VERIFIED, and the previously recorded drift is FIXED.** Five skills
    exist in both `.claude/skills/` and `~/.claude/skills/`. Three are byte-identical
    (`bug-triage-protocol`, `claude-code-prompt-install`, `mpm-render-pipeline`). The
    `panel-audit-dispatch` copies still differ but only in wording: both now carry
    310.494 kg/m^3 and both state `coup_friction` is genuine Coulomb friction, so the stale
    density band and refuted friction claim recorded earlier are gone from both.
    **The remaining divergence runs the other way from the historical case: the USER-LEVEL
    copy is AHEAD.** `~/.claude/skills/connector-router/SKILL.md` carries a Scholar Sidekick
    routing row that the repo copy lacks. Not applied here, deliberately: the repo had 27
    uncommitted files at the time and this session did not add a 28th to a tree with a
    documented concurrent-session hazard. One additive table row closes it.

## ADDENDUM 2026-08-18

J17. **THE g128 CANONICAL SET NOW EXISTS, AND THE VERDICT SURVIVES REFINEMENT.**
     J15 called running it "the single highest-value open item". Run 2026-08-18 on
     Vista node c642-032 (GH200 120GB) inside idev job 917886, via the unmodified
     `run_s2.sh 128`, which writes to new `g128_m*` directories and therefore did
     NOT repeat the 2026-07-26 overwrite that destroyed six margins. Three masses,
     all rc=0, 90 frames, depth 0.30 m, velocity 1.5 m/s, floor_friction 0.55.

     `margin_frames` across all four grids, joint drift-and-speed condition:

     | grid | m1100 | m1609 | m2337 | verdicts |
     |------|------:|------:|------:|----------|
     | g48  |    22 |    25 |    19 | SLIDE x3 |
     | g64  |    41 |    28 |     8 | SLIDE x3 |
     | g96  |    15 |     7 |     1 | SLIDE x3 |
     | g128 |    39 |    11 |     1 | SLIDE x3 |

     **All three remain SLIDE at g128. The verdict does not flip.** `g96_m2337`'s
     one-frame margin does NOT collapse to STUCK at g128; it stays at 1. The
     16 SLIDE / 1 STUCK headline is therefore not overturned by refinement to g128
     for the three canonical masses.

     **BUT `margin_frames` ITSELF IS NOT CONVERGING.** m1100 runs 22, 41, 15, 39
     and m1609 runs 25, 28, 7, 11. Only the BINARY verdict is stable. That is the
     behaviour Syamlal, Celik and Benyahia 2017 (`10.1002/AIC.15868`) predict for a
     transient quantity. Quote the margin as a fragility indicator at a stated
     grid, never as a converged number.

     Three independent resolution gains at g128, read from the summaries:
     `water_layers` rises 4 to **8**, retiring the L-3 limitation of only 4
     particle layers per flow depth; `C2_veh_zmin_rise` is **0.0** on all three, so
     the g48 floor-penetration defect is absent; `determinism_identical` is **true**
     on all three.

     **P-2 IS IMPROVED BUT NOT CLEARED.** Max water fraction inside the vehicle
     bbox against the 0.10 limit: m2337 **0.0794** passes, m1609 **0.0945** passes,
     m1100 **0.1116** STILL FAILS. Do not write that g128 fixes passthrough; it
     clears it for the two heavier masses only.

     Artifacts at `data/g128_2026-08-18/`, three `summary.json` and three
     `metrics.csv`, so this is re-derivable without the cluster.
