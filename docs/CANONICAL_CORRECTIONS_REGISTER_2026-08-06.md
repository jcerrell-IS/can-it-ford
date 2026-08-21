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
`core/solver.py:167-169`, inside `Solver.set_material()`: `self._sim.set_parameters_dict({"material": name, "g": [0.0, 0.0, -9.81], **params}, ...)`. ~~Hardcoded on every call, not a library default.~~ **That clause is WRONG about the mechanism and is corrected in A2a; the -9.81 result is UNCHANGED.** `sim_standing.py:205` calls `set_material(newtonian(...))`; nothing on the gated path supplies a `g` key to override it. **The `:127` this line carried until 2026-08-21 was stale by 78 lines**, re-measured live that day; `newtonian()` is at `materials/__init__.py:125-130` and carries no `g` key. Prior citation to `mpm_solver_warp.py:742-743, :811-812` was never re-checked against the actual vendored file and is superseded by this one; that file lives at `kernels/mpm_solver_warp.py`, not `core/`.
DELETE every claim that gravity is unknown or unset.

**A2a. `g` IS A DEFAULT WITH AN OVERRIDE PATH, NOT AN UNCONDITIONAL ASSIGNMENT. THE 9.81 RESULT DOES NOT MOVE. Relayed by the scene/domain thread 2026-08-14 and re-derived here from primary source before acceptance, not taken on report.** A2 above said "Hardcoded on every call, not a library default", and CLAUDE.md item 3 says "unconditionally, not a library default". Both are wrong about the mechanism, and each **contradicts the very next sentence of its own item**, which explains that `newtonian()` "carries no `g` key **to override it**" — a sentence that only makes sense if an override path exists.

**The mechanism, read live 2026-08-14 from `third_party/mpm-engine-544c93dd-solver-core/core/solver.py`:**

```python
:166        params = {**params, **overrides}
:167-169    self._sim.set_parameters_dict(
                {"material": name, "g": [0.0, 0.0, -9.81], **params}, device=self.device)
```

`**params` expands **after** the `g` key, and in a Python dict literal the later key wins. So **any material whose `resolve()` returns a `g` key, or any caller passing `g=` as a `**overrides` kwarg, silently replaces the -9.81 vector.** It is this wrapper's own hardcoded **default**, with a live override path.

**WHY THE CONCLUSION IS UNAFFECTED, verified live on four independent points rather than asserted.** (1) `newtonian()` at `materials/__init__.py:125-130` takes `(eta, density, bulk_modulus, E, nu)` and has no `g` parameter. (2) The materials module contains **no `g` key at all**, at any line. (3) The gated driver `renders/yaris_render_s1/_incoming/sim_standing.py` (sha256 `5215c38b`, the driver that ran the 17, per D8c) calls `set_material(newtonian(...))` at `:127-128` with **no `g=` override**, and a grep of the whole file for `g=`, `"g"` or `gravity` returns **nothing**. (4) The only other material call, `set_material_range(...)` at `:129-130`, routes through `solver.py:189-190` to `set_parameters_for_particles`, a per-particle-range path that never touches the global parameter dict, so it cannot set `g` either. **All 17 gated runs ran at exactly 9.81 m/s^2. Do not weaken that.**

**CITATION CORRECTED IN THE SAME PASS, and the original pointed at better evidence than it claimed.** A2 cited "`newtonian()` at `materials/__init__.py:78-83`". `newtonian()` is at **`:125-130`**; `:78-83` is a different thing, the `base == "newtonian"` branch of `Material.resolve()`. **`:78-83` is in fact the STRONGER citation for this claim**, because it is the actual `params` dict that reaches `set_parameters_dict`, and it returns exactly eight keys, `E`, `nu`, `density`, `bulk_modulus`, `plastic_viscosity`, `yield_stress`, `hardening`, `softening`, **none of them `g`**. Cite both, and do not call `:78-83` the factory: `:125-130` is the factory, `:78-83` is the resolver.

**SCOPE FENCE, stated because this correction is easy to over-apply.** This touches the **solver** gravity constant only. It does **not** reopen **A6**, which is the separate `9.80665` vs `9.81` **post-processing** fork in `failure_modes.py`; that question is closed by regeneration and is untouched here. A relay describing "A2 and A6" as jointly about the post-processing fork is mistaken about A2: A2 has always been the solver-gravity item, which is exactly why the defect lives here. **Engine tag: warpmpm.** Genesis has its own gravity path and nothing above applies to it.

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

**THE TABLE ABOVE IS THE 2026-08-07 STATE AND IS NOW HISTORICAL.** **CORRECTED 2026-08-18 AT THE R8 REGISTER MERGE.** The clause that stood here read "as of 2026-08-12, no code site holds 9.80665; both were set to 9.81". **Its second half is FALSE, and it contradicted the very next sentence of this same entry**, which describes the surviving site as dead code. Measured live 2026-08-18 by `/usr/bin/grep -rn "9\.80665"` over `*.py` in the working tree, excluding `third_party/`, `.claude/worktrees/`, `archive/` and `__pycache__/`: **exactly ONE assignment of 9.80665 survives, `analysis/viability_dashboard_scaffold.py:11`, and it is tracked.** `simulation/failure_modes.py:14` does read `G = 9.81`, unified by `e495b56`, so the first half was right. The remaining occurrences of the string are prose: a docstring at `analysis/classify_failure_modes.py:30`, a comment at `simulation/failure_modes.py:15`, and three message strings in `scripts/check_claims.py`. **Count assignments, not string occurrences.** A further correction to that table's framing, found while closing it: **only `failure_modes.py:14` was ever a post-processing consumer.** In `analysis/viability_dashboard_scaffold.py` the constant is DEAD CODE, declared once at `:11` and never used anywhere in that file, and nothing in the repo imports that scaffold (verified live 2026-08-12 by a Python walk for both `import` sites and in-file uses of the bare name). So the fork's operative reach was always ONE site, even though the string genuinely appeared twice. `check_claims.py` C6 asserted "Both are post-processing consumers of the rigid timeseries" and that half was wrong; it has been corrected. Counting occurrences of a constant is not the same as counting its consumers.

**This fork now reaches published output.** `failure_modes.py` uses G at `:170` (`surge_accel_g`) and `:174` (`weight_n`), and the classifier has run on all 17 runs (D6b), so 9.80665 fed the published verdicts. Any statement that it never influenced a gated result is retracted. **CLOSED 2026-08-12 by regeneration, not by assertion.** `failure_modes.py:14` now reads `G = 9.81` and both `data/` stores were regenerated. 16 SLIDE / 1 STUCK holds: the `mode` column and all three `triggered_*` columns are byte-identical across all 17 runs. Exactly 3 of 33 columns move, all direct functions of G: `ratio_topple` and `peak_surge_accel_g` by -0.034 percent, `weight_n` by +0.034 percent.

**CLOSED TWICE, INDEPENDENTLY, AND THE TWO AGREE BYTE FOR BYTE. Recorded 2026-08-13 during the merge that brought the two branches together.** Two sessions performed this unification without knowledge of each other: `e495b56` on `main` (2026-08-12 22:31) and `6ea4329` on `warpmpm-continue` (same day). Verified live by `git rev-parse` on all three refs: the regenerated `data/failure_modes_by_run.json` and `data/failure_modes_by_run_classified.csv` are the **same blob** on both branches, so the merge had nothing to reconcile in either store. That is an unplanned independent replication of the regeneration, and it is the strongest evidence in this entry: two runs of `analysis/classify_failure_modes.py`, from two working trees, produced identical output. It is **not** independent confirmation of the *verdicts*, which come from the same 17 `metrics.csv` in both cases.

**The two closures did NOT agree about the source edit, and that difference was load-bearing. See A6b.**

**THIS ENTRY'S OWN STATED REASON IS REFUTED, EVEN THOUGH ITS CONCLUSION HELD. Present only on `claude/add-ci-checks` before the 2026-08-18 merge; carried in here because it exists on no other lineage.** It claimed "all 13 sub-threshold margins are far larger than 0.034 percent". They are not. `g48_m2337` sat at `ratio_topple` 1.000244, a margin of **0.0244 percent above 1.0, which is SMALLER than the 0.0342 percent change**, and it crossed: 1.000244 -> 0.999903. No verdict moved, because TOPPLE triggers on a sustained joint condition and not on the peak ratio (D6c), so the crossing changed a magnitude and not an outcome. Recorded because the entry told the reader to "verify rather than assume" and the assumption embedded in its own justification was the thing that failed. **A conclusion reached for a refuted reason is not verified.** Consequence for D6c, applied there: the "ratio >= 1 in 13" figure is now 12.

**A6a. The margin argument A6 used to predict the no-flip was WRONG, and the prediction was right for a different reason.** This entry previously read "all 13 sub-threshold margins are far larger than 0.034 percent, so no verdict flip is expected." Verified live 2026-08-12: `g48_m2337`'s peak TOPPLE magnitude sat **0.0244 percent** above SSF, which is SMALLER than the 0.034 percent shift, and it did cross below, 1.000244 -> 0.999903. Nothing flipped anyway, because TOPPLE requires its condition sustained 3 CONSECUTIVE frames (`failure_modes.py:179-185`), not a peak, and `triggered_topple` was already False in all 17. Recorded because the entry told the reader to "verify rather than assume" and the assumption embedded in its own justification was the thing that failed. **A conclusion reached for a refuted reason is not verified.** **The correct argument is structural, and it is a proof rather than a margin estimate.** G reaches exactly two lines. `weight_n = mass*G` (`:174`) feeds NO criterion and is an output field only. `surge_accel_g = |accel_x|/G` (`:170`) feeds ONLY the TOPPLE test. SLIDE (`:179-181`) and FLOAT (`:183-185`) are displacement and speed alone, and `force = mass*accel` (`:127`) carries no G. Raising G LOWERS `surge_accel_g`, so TOPPLE becomes strictly harder, and it already triggered in 0 of 17. A flip in this direction is impossible. Cite that argument, never a margin comparison. Consequence for D6c, applied there: the "ratio >= 1 in 13" figure is now 12.

**A6b. THE COMMENT ABOVE THE CONSTANT IS A LINE-GEOMETRY HAZARD, AND IT WAS NOT HYPOTHETICAL: IT LANDED ON `main` AND SILENTLY REPOINTED 33 CITATIONS. Found and fixed 2026-08-13 while merging `warpmpm-continue` into `main`.** `6ea4329` deliberately kept the edit to ONE physical line and wrote the rule down. `e495b56` did the opposite: it wrote a three-line comment, growing `simulation/failure_modes.py` from 327 lines to 329 and shifting **every line at or above the old `:15` by +2**. That shipped on `main` for a day.

The damage is silent because the shifted citations still land on real, plausible, WRONG lines rather than erroring. Verified live 2026-08-13 against both checkouts:

| citation | means | lands on, `main` before this merge |
|---|---|---|
| `:46`, `:47`, `:48` | the three `0.05` literals; `:47` is the SPEED (D7a) | `@dataclass`, `class FailureThresholds:`, `slide_m` |
| `:127-128` | `accel = np.gradient(...)`, `force = mass*accel` | `else:`, `omega = np.zeros_like(vel)` |
| `:170` | `surge_accel_g` | `surge_speed`, a different physical quantity |
| `:174` | `weight_n` | `vertical_force` |
| `:176` | `driven_downstream`, the AND in D8's criterion | `weight_n` |
| `:179-185` | the three sustained joint conditions | `driven_upward` and the SLIDE block |

`e495b56`'s own comment text says the fork fed the verdicts "via `:170` and `:174`", and after its own edit `:170` and `:174` are `surge_speed` and `vertical_force`. **A comment that invalidates its own citation by being written is the compact form of this defect.**

ENUMERATED, NOT ESTIMATED. `6ea4329` said "16 citation sites"; that figure is **withdrawn as an estimate** and replaced by a live count, independently re-derived twice. Scope, stated because the number is scope-sensitive: tracked content of ref `main`, `third_party/` excluded, strict token match that rejects `classify_failure_modes.py:N` and `failure_modes_by_run*` substrings, **and counting only citations that carry the filename token**. On that scope: **51 citation instances across 22 files; 18 cite `:14` and are geometry-independent; 33 across 18 files cite a line above `:14` and therefore changed meaning.**

**"ALL 33 WERE BROKEN" WOULD BE FALSE. The correct split is 28 stale in 14 files and 5 CORRECT in 4 files.** The 5 were authored *after* `e495b56`, against the shifted numbering, and are the ones the fix in this merge breaks; they are tabled below. A universal quantifier was in an earlier draft of this entry and is withdrawn. **A count of citations that moved is not a count of citations that are wrong.**

SCOPE CAVEAT ON THE 51, because it undercounts. **Bare continuation references are not matched.** `analysis/classify_rogue_silverado_sweep.py:25-26` carries `", :211"` and `", :176"`, genuine citations of this file with no filename token, both correct post-shift. Counting continuations gives **53**, which coincidentally equals a naive unfiltered match while being composed differently. **State whether continuations are counted, or the total is a bare number with no scope**, which is the failure D7a exists to prevent. Reproduce with the walk in `docs/FRICTION_RESOLUTION_RECONCILE_2026-08-13.md` section 2; do not trust either figure without re-running it.

FOR THE RECORD, the project's own claim-checker went stale in the same session that broke it: `scripts/check_claims.py:234` was authored **2026-08-12 22:35**, four minutes after `e495b56` landed at 22:31, and still cited the pre-shift `:179-185`. It is correct again after this merge, but it was never re-checked against the edit made minutes earlier.

RESOLUTION TAKEN IN THE MERGE: the constant is back to ONE physical line carrying `e495b56`'s full text, so the file is 327 lines again and all 33 resolve as they did before 2026-08-12. **28 of the 33 are restored by this.** The other **5 were authored AFTER `e495b56`, against the shifted numbering**, and are the ones this merge breaks. All 5 are outside this dispatch's write scope and are listed for their owners in section 5 of the write-up; each needs a -2 correction:

| site | cites | should cite |
|---|---|---|
| `analysis/slide_verdict_fragility.py:14` | `:181-183` | `:179-181` |
| `analysis/classify_rogue_silverado_sweep.py:25` | `:184`, `:211` | `:182`, `:209` |
| `analysis/classify_rogue_silverado_sweep.py:26` | `:130`, `:176` | `:128`, `:174` |
| `docs/SESSION_TRACK1B_2026-08-13.md:197` | `:48` | `:46` |
| `simulation/validate_coupling_force_ladder.py:348` | `:135-151` | `:133-149` |

**STANDING RULE, and it is now enforced in the source itself.** `simulation/failure_modes.py:14` carries an inline note saying why it is one line. Never add a line above `:46` in that file without re-running the enumeration and correcting every site it moves. The general form: **a line-number citation is a pointer into a mutable file, and a comment is an edit.** The same failure is already recorded for `.gitignore` (CLAUDE.md, provenance section, where positional citations went stale three times in one day) and for `sim_standing.py:132` (D8b).

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

**B9. THE AT-REST GATE DOES NOT DISCRIMINATE RESOLUTION, IT DISCRIMINATES BAND TUNING. AND CLAUDE.md ITEM 5 NOW HAS A CANDIDATE MECHANISM, NOT A SETTLED CAUSE. 24 runs on Vista GH200 2026-08-14, commit `d2c13e8` on `claude/fork-moving-driver`, read from its body here. Yaris, PPC 8, band swept 0.25 to 2.0 `dx` at three resolutions, all else held fixed. Engine warpmpm.** Gate error percent, `*` passes the 10 percent gate:

| `dx` | 0.25 | 0.50 | 0.75 | 1.00 | 1.25 | 1.50 | 1.75 | 2.00 |
|---|---|---|---|---|---|---|---|---|
| 0.14721 | -90.7 | **-6.7\*** | 45.9 | 63.3 | 76.4 | 81.7 | 82.8 | 82.5 |
| 0.09814 | -32.1 | 16.9 | 29.3 | 37.1 | 23.3 | **2.8\*** | **-4.3\*** | -14.2 |
| 0.07361 | -70.8 | -19.9 | **3.9\*** | 52.3 | 96.2 | 108.9 | 116.1 | 132.6 |

**(a) THE INSTRUMENT FINDING, AND IT IS THE STRONGER FORM OF AN EXISTING ITEM. EVERY RESOLUTION CONTAINS A BAND THAT PASSES**: `dx` 0.147 at band 0.5, `dx` 0.098 at 1.5 and 1.75, `dx` 0.074 at 0.75. **A gate that ANY grid can satisfy by moving one free parameter is not certifying the coupling.** CLAUDE.md item 6 already records that no gate is a physics validation and that several cannot fail for a reason external to the code; **this is a sharper case than any of those, because here the gate CAN fail, and whether it does is set by a tunable knob rather than by the physics.** A single reported PASS is one point on a tunable curve, not a validation.

**(b) OPERATIVE RULE: do not report the at-rest gate as pass/fail on a run until the band is either DERIVED FROM GEOMETRY or SWEPT AND REPORTED AS A CURVE.** A single-band gate result is a point on a surface. Any prior PASS obtained at one band should be re-read as such.

**(c) THE CANDIDATE MECHANISM FOR CLAUDE.md ITEM 5, AND IT MUST BE LABELLED CANDIDATE.** At the engine default **band = 1.0 `dx`** the three errors are **63.28, 37.06, 52.27**, which is exactly the non-monotone Yaris sequence that started this enquiry. **The default TIES BAND TO `dx`, so refining does not move along one curve; it cuts a DIAGONAL ACROSS THREE DIFFERENTLY-SHAPED CURVES.** The coarsest and finest rows are monotone increasing in band, the middle row rises then falls, and sampling three shapes at one point each has no reason to be monotone.

**(d) THE SIMPLE FORM OF THAT HYPOTHESIS IS ALSO REFUTED, BY THE SAME RUN, WHICH IS WHY (c) IS A CANDIDATE.** The surface does **not** collapse onto one curve. Zero crossings are **0.532** band/`dx` at `dx` 0.147, then **0.414 AND 1.598** at 0.098, then **0.709** at 0.074; in metres 0.0783, 0.0406/0.1568, 0.0522. **Constant in neither variable, and the middle row crosses twice.** So **"error is a function of band alone" is refuted alongside "error is a function of PPC alone"** (G4f). **What survives is weaker and true: band is a first-order control, it is tied to `dx` by default, and the surface is not of one shape.** **Steffen, Kirby and Berzins 2008 remains the citation for the PHENOMENON** (L-5, G22); this is a candidate mechanism in this scene, not a general one.

**(e) THE SIGN STRUCTURE IS PHYSICALLY LEGIBLE, AND IT POISONS THE NEAR-CROSSING PASSES.** Small bands read LOW, to **-90.7** percent; large bands read HIGH, to **+132.6**, monotonically at the coarsest and finest `dx`. A wider skirt engages more grid nodes and returns more reaction. **The zero crossing is where two errors cancel, so a run that passes near it is right for a reason unrelated to resolution.** Of the four passes above, `dx` 0.147 at -6.7 and `dx` 0.074 at 3.9 both sit adjacent to a crossing. **Treat a near-crossing PASS as cancellation, not agreement.**

**(f-PROVENANCE) THIS TABLE HAS NO BACKING ARTIFACT. Found on adversarial review 2026-08-14 and recorded here because item 16 exists for exactly this.** `[live]` `git show --stat d2c13e8` touches **one file, a markdown document**. There is **no CSV, no JSON, and no job ID anywhere in the diff**, and a repo-wide search plus a `git log --all -S` pickaxe on the distinctive particle counts finds **no stored artifact for these 24 runs**. **The 24 numbers exist nowhere except as hand-typed prose.** The transcription into this register was verified byte-for-byte against that prose, and the four zero crossings were independently re-derived by linear interpolation on the table and reproduce to rounding, **so the table is internally consistent and not fabricated arithmetic. But it is unreproducible in the sense item 16 defines**: cite it as a reported result, not as a checkable one, and **do not treat B9 as load-bearing for a publication until the run outputs are stored.** G4f is one tier better and still short: it names job `912094` but has no CSV either.

**(f) WHAT THIS DOES AND DOES NOT CHANGE.** It does **not** rehabilitate anything: verdicts previously marked INDETERMINATE because the gate failed **stand and are better founded**, since the gate is now known to be tunable rather than an independent check. **Nothing becomes quotable.** It **does** bear on F6e: a realistic-domain AMR scheme must control band width, and co-refining PPC alone will not save it. **And it is the THIRD member of a pattern this register should now name: an engine default, never varied, materially controlling a reported result** — alongside `COLLIDER_FRICTION` 0.4 (G4e, "NOT tuned" in its own comment) and the artificial sound speed 12.845 m/s (D9, never swept). **Inherited defaults are this project's largest class of unexamined parameter.**

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

**COUNT UPDATED 2026-08-12, from 13 to 12, and the reason is this entry's own point.** The G unification in A6 (9.80665 -> 9.81) moved every `ratio_topple` by -0.0342 percent. `g48_m2337` was sitting at 1.000244 and crossed to 0.999903, leaving 12 runs at ratio >= 1. **No verdict changed**: `triggered_topple` is 0 in all 17 both before and after, which is exactly why the ratio count is not the verdict. **SLIDE's 17 and FLOAT's 1 did not move at all, both criteria being G-free** (A6a: G reaches only `:170` and `:174`), so the tally that shifted is the one nobody should have been quoting. Anyone citing "13" is citing a pre-2026-08-12 code state; anyone citing 12 or 13 *as a topple count* is making the error this entry exists to prevent. The stable statement, and the only one worth quoting, is **TOPPLE triggers in 0 of 17**. `check_claims.py` C10c deliberately does not hardcode the tally, for this reason; do not re-add it.

**D6d. STUCK is not a fourth mode.** There are three outcomes, SLIDE / TOPPLE / FLOAT; STUCK is the "none sustained" early return (`failure_modes.py:229-230`) and carries no threshold, ratio-of-record or onset frame. Its winning-mode columns are deliberately EMPTY, not zero. Where two modes sustain, `:232` reports the last in `MODE_SEVERITY`, i.e. FLOAT > TOPPLE > SLIDE.

**D6e. `metrics.csv` `pitch_deg` / `roll_deg` are VEHICLE-BODY-SENSE, not raw Euler.** `vehicle_live.py:55-61` computes raw ZYX Euler, then `:295-300` swaps two before writing, so `roll_deg` is the raw Euler pitch (about y, the long axis). The ZYX gimbal singularity is at `|roll_deg| -> 90` and degenerates yaw and pitch, not roll. **It cannot affect any verdict here: the classifier reads neither column.** TOPPLE is an acceleration test, not an angle test. Max `|roll_deg|` over all 17 runs is 4.625 deg.

**D6f. `peak_surge_accel_g` is numerical, not physical.** It is `np.gradient(vel, t)` (`failure_modes.py:129`) over a 30 Hz rigid-body trace; single-frame values reach 3.78 g. The `sustain_frames` guard is the only thing keeping TOPPLE from firing on all 13. Never quote the raw TOPPLE ratio alone.

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

**D7b. THOSE LINE NUMBERS ARE STALE ON `main` BY TWO, AND THE REASON IS THAT A6b's CODE FIX NEVER LANDED THERE. Raised by the visuals thread 2026-08-14 from a direct read; verified here across three refs before recording, because the answer differs by ref.**

| ref | `simulation/failure_modes.py` | `:46` `:47` `:48` are | `:170` | `:174` |
|---|---|---|---|---|
| **`main`** | **329 lines** | `@dataclass`, `class FailureThresholds:`, `slide_m` | `surge_speed` | `vertical_force` |
| `claude/friction-resolution-reconcile-84465d` | **327 lines** | the three `0.05` literals | `surge_accel_g` | `weight_n` |

**On `main` the three `0.05` literals are at `:48` `slide_m`, `:49` `slide_speed_ms`, `:50` `float_m`.** D7a above and CLAUDE.md item 13 both cite `:46/:47/:48`, correct for the friction branch and **stale by two on `main`**. **The rule those entries state is unaffected**: three literals, one of them a SPEED, deduplicate by name and unit.

**THE STRUCTURAL FINDING IS BIGGER THAN THE OFFSET.** A6b records that `e495b56` grew this file 327 to 329 with a three-line comment, shifting 33 citations, and that the repair "is back to ONE physical line ... so the file is 327 lines again and all 33 resolve as they did before 2026-08-12." **That repair exists ONLY on the friction branch.** `[live]` `e495b56` is still the **last commit to touch this file on `main`**, `main`'s copy is 329 lines, the working tree is unmodified against HEAD, and every line lands exactly where A6b's "lands on, main before this merge" column predicts. **So `main` is still in the broken state A6b describes as fixed, and the 33 shifted citations are still shifted there.**

**CONSEQUENCE FOR THIS REGISTER, stated because I caused it.** This branch merged A6b's register TEXT without A6b's code FIX, so the register now asserts a completed repair that `main` does not have. **A6b is true of `claude/friction-resolution-reconcile-84465d` and false of `main`, and it does not say so.** Read A6b with this entry. **Any line citation into `failure_modes.py` must name its ref**, the same rule D8c reached for `sim_standing.py` by a different route. **The fix is a two-line edit on `main`, outside this dispatch's write scope.**

**D7c. `max_speed_ms` IS NOT THE SLIDE CRITERION'S QUANTITY, AND THIS REGISTER MISLABELS IT AS `|vx|`. Raised by the visuals thread, verified here against source and store 2026-08-14.** In `failure_modes.py` the SLIDE test uses `surge_speed = np.abs(kin.vel[:, SURGE_AXIS])`, a single axis, while the reported column comes from `speed = np.linalg.norm(kin.vel, axis=1)`, the **3D magnitude**, stored as `max_speed_ms`. (On `main` those are `:170` and `:175`, stored at `:222`; on the friction branch subtract two, per D7b.)

**The register quotes that column and calls it `|vx|`.** Item 15 says "peak `|vx|` 0.771 -> 0.360 -> 0.204 m/s". `[live]` from `data/rogue_silverado_slide_classification_2026-08-13.csv`, `max_speed_ms` for `rs_silverado_g64/g96/g128` is **0.771335 / 0.360132 / 0.204362**. **Character for character the same numbers. It is the 3D magnitude, not the surge component.**

**AND THE CRITERION'S OWN QUANTITY IS NOT IN THE STORE AT ALL.** The speed-like columns are `max_surge_drift_m`, `max_speed_ms`, `peak_surge_accel_g`, `peak_surge_force_n`, `slide_speed_ms_threshold`. **There is no `surge_speed` column**, so the speed clause cannot be checked from this file by anyone.

**BOUNDED CONSEQUENCE, and the verdicts are safe.** Since `|v| >= |vx|` always, every speed ratio quoted from this column is an **UPPER BOUND** on the criterion's value. That includes D9's row "speed max vs `slide_speed_ms` 15.43x -> 7.20x -> 4.09x", which is `max_speed_ms/0.05`. **So "the speed clause is still over threshold" is not established by these numbers**; it is consistent with them and unproven. **The VERDICTS are unaffected**, because `triggered_slide` and `onset_frame_slide` are computed inside the classifier from the correct `surge_speed` and are what the store records. **Relabel the quantity wherever it is quoted; do not restate D9's conclusion as resting on it.** D9's conclusion that refinement de-synchronises two clauses rather than dropping one comes from `onset_frame_slide`, which is sound.

**D7d. "THE SILVERADO'S FLIP INTO STUCK" NOW DENOTES TWO DIFFERENT RESULTS. Do not merge them.** (a) The `rs_*` refinement sweep, real Silverado hull 2270 kg, job 3362208, non-canonical: SLIDE at g64 and g96, **STUCK at g128**, with peak drift still **1.5557x** threshold, so no threshold falls below 1 and `onset_frame_slide` goes to -1 purely by loss of 3-frame co-occurrence. (b) The matched-`dx` square at Section J item 15a, arm at `n_grid` 154, mass 2270 kg, **STUCK at margin -3**. **Different runs, different grids, different framing.** Where one sentence is needed, **(a) is the sharper illustration** of the optimistic direction, because **both ratios still exceed threshold and the verdict flips anyway.**

**READ D9 WITH THIS ENTRY.** A SECOND, DIFFERENT mechanism also flips a SLIDE verdict "at g96" (J15, grid refinement). D8 was written without knowledge of it. D9 reconciles the two: they break different clauses of the same criterion, the two g96 labels are three different resolutions, and both sit on the same unswept artificial sound speed. Do not cite D8 alone as *the* explanation of a SLIDE flip.

**D8. Floor friction FLIPS the SLIDE verdict at g96. Measured 2026-08-13, warpmpm, 3 seeds per arm, plus a forcing-independence re-run.** The regime ladder walked restitution only and left its floor at friction 0.0; the 17 gated runs carry `floor_friction = 0.55` (`sim_standing.py:210-211`). `docs/FLOOR_FRICTION_RUNG_2026-08-12.md` ran that variable but recorded **vertical motion only**, so it could not speak to SLIDE, which is horizontal. `docs/FRICTION_RUNG_HORIZONTAL_INSTRUMENTATION_2026-08-13.md` adds the missing channel. Evaluating the FULL criterion, `failure_modes.py:179-181` ANDed with `driven_downstream` at `:176`, on the per-frame flow block:

| arm | drift max vs `slide_m` 0.05 | speed max vs `slide_speed_ms` 0.05 | SLIDE |
|---|---|---|---|
| mu = 0.00, 3 seeds | 22.63 to 22.64x **over** | 16.65x **over** | **True, 3 of 3** |
| mu = 0.55, 3 seeds | 0.525 to 0.578x, **under** | 3.99 to 4.18x, **over** | **False, 0 of 3** |

**ONE clause flips, not two.** The gated arm remains about **4x OVER the speed threshold** and fails the joint condition on the **drift clause alone**. An earlier draft of this entry claimed it crossed BOTH thresholds; that was produced by pairing a max drift against a late-window MEAN speed, a statistic `failure_modes` neither computes nor uses. **Never pair a max against a mean when quoting against these thresholds.**

**It is a verdict, not a "kinematic pair."** An earlier draft hedged that `driven_downstream` was unevaluable because the material-8 path accumulates no contact force (A3, CLAUDE.md A-1). **Withdrawn.** `failure_modes.py:129-130` is `accel = np.gradient(vel, t, axis=0)` then `force = mass_kg * accel`, i.e. mass times finite-difference acceleration of the body's own velocity, fully derivable from `(t, vx)`. A3 is a fact about the **solver** and does not transfer to this **classifier**. `driven_downstream` is True in every arm and gates nothing (`:176` takes `max|.|`, so it is direction-blind).

**Not a seed draw, and not an artefact of the forcing.** Gap 1.104 m against a worst within-arm spread of 0.002656 m. The flip also reproduces with `kick_water` DISABLED and `sustain_inflow` as the only forcing over 200 frames: drift 1.161353 m SLIDE True at mu=0.00 against 0.017969 m SLIDE False at mu=0.55, a 64.6x ratio.

**"Sustained inflow" is the wrong label for the DEFAULT rung-d forcing.** `kick_water` (`validate_coupling_force_ladder.py:402`) adds +1.5 m/s to **all 163,944** water particles **once**; `sustain_inflow` then clamps **220 per frame, 0.134 percent**. The default flow block is a decaying slosh transient (mean `|vx|` per 10 frames: 0.271, 0.531, 0.709, 0.808, 0.781, 0.301; final sample 0.1135 m/s). **Do not cite its 0.6303 m/s late-window mean as a characteristic speed.** Cite the verdict.

**Three limits that bound this entry.** (a) The harness's own arrival gate `flow_reached_body` is **False for all three mu=0.55 arms and for both `--no-kick` arms**; it tracks the box, which moved 1.1 m in the control, so it is not a clean between-arm test, but no arm here is measured under a verified-arrived flow. (b) **Single grid.** Only g96 was run; **no grid-refinement check of the horizontal channel exists.** (c) Every number sits on an artificial sound speed of **12.845 m/s**, about 118x below real water, never swept, which Isik and He 2023 (year corrected, see G7a) record can qualitatively flip a rigid-body outcome.

**Two things this does NOT license.** It measures **friction**, not the coupling defect; it shows the route from a buoyancy error into the normal force and thence into `mu*N` is dominant in the horizontal channel, which is what section 5.3 posited and section 8 of `REGIME_LADDER_RESULTS_2026-08-07.md` could not test, but how much the rung-b buoyancy error moves a verdict stays open. And the body is a **600 kg/m^3 cube**, not the 310.494 hull, so nothing transfers numerically to the 17 runs. Do not read it as contradicting the 16 SLIDE verdicts (D6b).

**Consequence for every earlier rung.** All prior ladder rungs ran at mu = 0.0, the arm that slides. The ladder's configuration **overstates horizontal motion by 40 to 65x relative to the gated one**.

**D8a. Register A7 extended: warpmpm applies Coulomb friction at THREE distinct sites, and A7's line number is the SDF path, not the plane.** Verified live 2026-08-13 against the pinned vendored core, `third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py`:

| site | path | acts on |
|---|---|---|
| `:1986` | plane grid BC, inside `add_surface_collider` (def `:1880`) | water and deformable particles |
| `:2729` | **SDF collider** grid BC, inside `add_sdf_collider` (def `:2621`) | water and deformable particles |
| `:967-977` | `_apply_rigid_restitution`, contact impulse | **the rigid body** |

A7 cites `:2729` as warpmpm's Coulomb site. That is correct as a Coulomb site but it is the **SDF collider's**, not the plane's; the plane's water-side friction is `:1986`. An earlier draft of this entry called it "the plane grid BC" and counted only TWO paths. Both corrected.

The rigid site is `J_t = min(v_t_mag / denom_t, mu * J_n)` applied to `v_cm` and `omega`, opposing tangential contact velocity, capped at the Coulomb limit. `add_surface_collider` sets `collider_param.friction` at `:1913` unconditionally for the water, and the `restitution != 0.0` gate at `:1915` additionally appends the plane to `rigid_surface_colliders` for the body. Since the gated floor is `add_plane(..., "slip", friction=0.55, restitution=0.05)` (`sim_standing.py:210-211`), **the 17 gated runs carry Coulomb floor friction on the vehicle itself, not only on the water.**

Caveat: `J_n` is the restitution impulse from the approach velocity, not a weight-supported steady normal force, so the resistance is not exactly `mu*N` in the static sense. **Fidelity gap in D8's arms:** `enable_floor_restitution` (`validate_coupling_force_ladder.py:190-199`) bypasses `add_surface_collider` and appends the entry directly, so there `friction` reaches the rigid path ONLY and never the water. The gated floor drives both channels; the rung reproduces the rigid half.

**D8b. `sim_standing.py:132` is a STALE citation for the gated floor and is baked into shipped artifacts.** The gated floor is `:210-211`; `:132` is triangle-rasterisation arithmetic. Verified live 2026-08-13. Enumerated live rather than taken on report: `simulation/coupling_validation/rung_e_floor_friction.py` carried it at four sites (**fixed 2026-08-13**), and `simulation/validate_coupling_force_ladder.py` carries it at **three, in two variants**: `:188` and `:893` say `:132`, and `:97` says `:133`. All are stale for the same reason. That file is **not fixed**, being held under the read-only rule. Its `:208`, `:220` and `:897` cite `:160-162` and `:190-198` for the kick and clamp; those were NOT checked here and are not covered by this entry. Every friction-rung arm JSON on Vista carries the stale string inside `arm_provenance.friction_source`; those are not retro-edited. **The VALUE 0.55 was always correct**; only the line number was wrong.

**D8c. D8b'S HEADLINE IS REFUTED FOR THE DRIVER THAT ACTUALLY RAN THE 17. Found 2026-08-13 while merging `warpmpm-continue` into `main`; D8b is retained above verbatim, unedited, so the correction can be audited against what it corrects. Adversarially reviewed before writing: six issues returned, all six upheld, three of which changed this entry, including its central framing.**

**THE DISCRIMINATOR IS CONTENT AND DATE, NOT PATH. Do not read this entry as "the wrong file".** The gated driver lived at `renders/yaris_render_s1/sim_standing.py`, the top-level path, at run time. `docs/vista_source_reads_2026-07-25.md:355-356` records it MEASURED on 2026-07-25 as "17435 bytes, byte-identical to the local `renders/yaris_render_s1/sim_standing.py`", and `renders/yaris_render_s1/_incoming/sim_standing.py` is exactly **17435 bytes**. **That path was then overwritten in place on 2026-08-08 by a later revision**, and `renders/yaris_render_s1/_incoming/sim_standing.py` is the surviving copy of the original bytes. Neither local file ran anything; the 17 executed on Vista.

| content | lines | sha256 | at that content, floor plane |
|---|---|---|---|
| the gated driver, preserved at `renders/yaris_render_s1/_incoming/sim_standing.py` | 389 | `5215c38b...` | **`:132-133`**, walls `:134-136` |
| the 2026-08-08 revision, now at the top-level path | 564 | `4696c3b2...` | `:210-211`, walls `:213-214` |

**THE EVIDENCE IS CRYPTOGRAPHIC, NOT CIRCUMSTANTIAL.** `renders/yaris_render_s1/_incoming/conv_2026-07-26_idev/00_provenance.txt:6` is an on-node record written by the run itself:

```
driver sha256: 5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45  /work/11603/jcerrell0629/vista/render_s2/sim_standing.py
```

`shasum -a 256` on `renders/yaris_render_s1/_incoming/sim_standing.py` returns exactly that. The top-level copy returns `4696c3b2...`. Corroborating and independent: D4a already records `_incoming/` as the canonical per-run tree with `all_runs_inventory.csv`'s `summary_path` resolving there, and the 17435-byte measurement above. **An earlier draft of this entry led with the file's mtime. That leg is WITHDRAWN**: an rsync-preserved mtime is not provenance, and it was the weakest of the three while being stated first.

**SCOPE LIMIT, so this is not over-read.** That sha is recorded **once**, for one idev session on 2026-07-26 01:54-01:55, and the record does not map its three tasks onto named runs. The `conv_2026-07-25/` and `sweep_2026-07-26/` directories are **empty**, so no comparable record survives for the runs they were to hold. What IS established for all 17: every one of the 17 `summary.json` stamps the same `canitford_git_commit`, `d43081a6`. **The driver's own identity is not a per-run stamped field.** `summary.json` carries `mesh_sha256`, `solver_git_sha` and `canitford_git_commit` and no driver hash, which is the same gap `lit:manifest_provenance` names.

**AND GIT HOLDS NO BLOB FOR THE GATED DRIVER, EVER.** At `d43081a6`, the commit all 17 runs stamp, `renders/yaris_render_s1/sim_standing.py` was **untracked**: `git ls-tree d43081a6 -- renders/yaris_render_s1/sim_standing.py` returns nothing. The path was first tracked at `00b735c`, **2026-08-12**, by which time it held the 2026-08-08 revision. So the only surviving copy of the code that produced the published verdicts is a **gitignored, untracked file with no commit history**. Treat that as a live provenance risk, not a footnote.

**They are NOT "the same program", and an earlier draft of this entry said so wrongly.** `diff` gives 188 added and **13 modified** lines, and at least one modification is behavioural rather than cosmetic: the `fill_ratio` denominator moved off the hardcoded `HULL` constant onto `hull_m3` measured from the loaded mesh, which the revision's own header (`sim_standing.py:19-21`) documents as a bug fix, and `--mass` went from required to defaulted. The correct statement is narrower: **the floor `add_plane` call is byte-identical between the two, merely relocated**, verified by hashing the two-line spans, so **no physics claim about the floor moves. Only the pointer does.**

So against the driver that produced the published verdicts, `:132-133` **is** the floor plane and `:134-136` **is** the four slip walls. **CLAUDE.md item 3's `(:132-137)` was correct, and D8b's instruction to repoint it to `:210-211` would have introduced the error it was trying to remove.** That repoint was requested and is **not** being made; see CLAUDE.md item 3, which now names the copy instead.

**THE HEADLINE WORD SHOULD BE AMBIGUOUS, NOT STALE.** `:132-133` is the gated floor in the driver that produced the 17; `:210-211` is the floor in the 2026-08-08 revision at the same path. Both are true of their own content. **Fix such a citation by qualifying which content it means, never by renumbering it.**

**The tell was already inside the file D8b was correcting, in the same sentence.** `validate_coupling_force_ladder.py`'s provenance string reads "`sim_standing.py:132-133` floor restitution=0.05 friction=0.55; **`:136`** walls restitution=0.05 friction=0.0". D8b called `:132-133` stale and left `:136` standing, **three tokens away in the same sentence**. Against the gated driver `:136` is the wall `add_plane`; against the 2026-08-08 revision it is `ok = np.abs(d) > 1e-14`. The same file also cites `:160-162` and `:190-198` for the kick and clamp, both correct against the gated driver, which D8b explicitly declined to check. **One citation frame, one file, one read session, and the resolution was applied to one member of four.** A file whose citations are internally consistent is evidence about which content its author was reading; when a line citation disagrees with the source, suspect the content before suspecting the citation.

**TEN FOR TEN, which is what makes this decisive rather than arguable.** Every line CLAUDE.md items 2 and 3 cite resolves exactly against the gated driver and to unrelated code against the 2026-08-08 revision: `:126` `load_particles`, `:127` `set_material(newtonian(`, `:129-131` rigid registration and `finalize_rigid_bodies()`, `:132-137` floor and walls and domain walls, `:150` `term_advective`, `:156-162` settle loop and one-shot kick, `:161` `v[:n_water,0] += velocity`, `:183-186` water-range clip, `:190-198` `_sustain_inflow`, `:202` its per-frame call. **Ten citations written by different sessions on different dates do not all land correctly on the wrong file by chance.** Two further corroborations, both against the gated driver: `docs/CITATION_AUDIT_2026-07-30.md:245` cites `:76` for `floor_friction=0.55`, and `docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md:232` cites `:75` for `water_eta=1.0e-3`.

**THE 2026-08-13 "FIX" PROPAGATED THE ERROR INTO NEW CODE, AND THAT IS NOW CORRECTED.** `simulation/coupling_validation/rung_e_floor_friction.py` had been edited that day so that `:18`, `:97-99` and the stamped `friction_source` at `:451` all attribute the **17 gated runs'** floor to `:210-211`. That points a claim about the 17 at content that did not exist until thirteen days after they ran. Corrected 2026-08-13 in this merge to name the driver instead. **Arm JSONs already stamped on Vista keep the old string and are not retro-edited**, so expect a seam between arms stamped before and after this change; the seam is a labelling difference only, since the value 0.55 was correct throughout.

**A SITE NEITHER D8b NOR ITS ENUMERATION CAUGHT, and it is wrong against BOTH contents:** `docs/semi_empirical_baseline_findings.md:82` cites `sim_standing.py:84` and `:235` for `mu = 0.55`. Against the gated driver those are `dx = self.grid.dx` and a `canonicalize(load_vehicle(...))` call. The real sites are **`:76`** (the `floor_friction=0.55` keyword default) and **`:227`** (the `--floor-friction` argparse default). Out of scope for this round, listed so it is not lost.

WHAT SURVIVES OF D8b, unchanged: the value 0.55 was always correct; the Vista arm JSONs really do carry `:210-211`, which is right for the 2026-08-08 revision and **wrong for the 17**; and the general hazard is real. What is withdrawn: the words "STALE" and "triangle-rasterisation arithmetic" as applied to the gated runs' driver, and the claim that its enumeration was complete.

TWO OF D8b'S OWN LINE NUMBERS WENT STALE INSIDE THIS MERGE, which is the same defect one level up. D8b was written against `warpmpm-continue`'s copy of `validate_coupling_force_ladder.py`; `main` grew that file (blob `3feba12` -> `62dd76a`) and the branch never touched it, so `main`'s copy survives the merge and **D8b's `:893` is now `:1002` and its `:897` is now `:1006`**. `:97`, `:188`, `:208` and `:220` are unmoved. Verified live in the merged tree.

**STANDING RULE, and it is the same one A6b arrives at from the other direction.** Before citing `sim_standing.py` by line, state which copy. For any claim about the 17 gated runs the answer is `_incoming/`, which `git check-ignore -v` will confirm is ignored by the `renders/yaris_render_s1/*` rule (re-derive that rule's line number, never cite it). For new work on the current driver the answer is the tracked top-level copy. **A line number without a copy is not a citation.**

**D9. TWO SLIDE FLIPS, TWO MECHANISMS, AND THEY BREAK DIFFERENT CLAUSES OF THE SAME CRITERION. Written 2026-08-13 as the reconciliation of D8 with J15/J16, which were produced on two branches with neither aware of the other.** D8 (`warpmpm-continue`) reports that floor friction flips SLIDE at g96. J15 (`main`) reports that grid refinement flips SLIDE at g96. Both are correct and they are not the same finding.

**Start from the criterion, exactly.** SLIDE is not a force balance. It is `_first_sustained_index((surge_drift >= slide_m) & (surge_speed >= slide_speed_ms), 3) >= 0`, ANDed with `driven_downstream` (`failure_modes.py:179-181` with `:176`). Both thresholds are 0.05, one a metre and one a metre per second (D7a). The mask is elementwise per frame and needs **three CONSECUTIVE frames on which BOTH clauses hold**. There are therefore three distinct ways to fail it: drop the drift clause, drop the speed clause, or keep both maxima above threshold and de-synchronise them.

**The two mechanisms take two different ones.** Verified live 2026-08-13 from the committed stores, not from either entry's prose:

| | friction arm (D8) | refinement arm (J15) |
|---|---|---|
| body | 600 kg/m^3 cube, side 1.472 m, rung-e in BoxTank | Silverado hull, 2270 kg |
| walked | `mu` 0.00 -> 0.55, **grid fixed at g96** | `n_grid` 64 -> 96 -> 128, **`mu` fixed at 0.55** |
| drift max vs `slide_m` | 22.64x over -> **0.52 to 0.58x, UNDER** | 6.97x -> 1.81x -> **1.56x, still OVER** |
| speed max vs `slide_speed_ms` | 16.65x over -> 3.99 to 4.18x, still over | 15.43x -> 7.20x -> **4.09x, still OVER** |
| `slide_idx` / `onset_frame_slide` | 7 -> **-1** | 3 -> 5 -> **-1** |
| clause that fails | **the drift clause, outright** | **neither: their 3-frame co-occurrence** |

Friction removes a clause. **Refinement removes nothing and de-synchronises two clauses that each still pass**, which is the `sweepV_g64_v0p5` signature J15 names. Sources: `data/rogue_silverado_slide_classification_2026-08-13.csv` (all six `rs_*` rows carry `floor_friction` 0.55) and `docs/FRICTION_RUNG_HORIZONTAL_INSTRUMENTATION_2026-08-13.md` section 3.

So the working shorthand, **friction changes the resisting term and refinement changes the driving term**, is right about the momentum balance and understates the difference at the criterion. Section 5.3 of `REGIME_LADDER_RESULTS_2026-08-07.md` established that in the floor-supported regime any buoyancy error lands in the **normal force**, and section 8 concluded from that, before anything was measured, that sliding resistance is `mu*N` and floor friction was "the obvious next rung and it was not run here." **D8 is that rung, and it confirms the prediction.** The driving side is the surge impulse: Silverado's `peak_surge_force_n` falls 32,441 -> 21,855 -> 14,275 N under refinement, which is the direction L-4 expects, since coarse resolution over-predicts peak hydrodynamic force. Cite L-5 (Steffen, Kirby and Berzins 2008) for the refinement mechanism; it is already this project's citation for the g48/g64/g96 non-monotonicity and no new one is needed.

**SEPARATELY SUFFICIENT. NOT SHOWN INDEPENDENT.** Each arm flips its verdict while holding the other's variable fixed, so neither result needs the other. That is weaker than independence and the difference matters, because **a mechanism by which they could interact is already on the record**: the rigid-side Coulomb impulse is `J_t = min(v_t_mag/denom_t, mu*J_n)` (D8a, `mpm_solver_warp.py:967-977`), and `J_n` is a restitution impulse computed from the approach velocity, which refinement changes. ~~**The 2 x 2 has never been run.**~~ D8 walked `mu` at one grid; J15 walked grid at one `mu`. Until `mu` x `n_grid` is crossed on one body, "independent" is an assumption.

**RESOLVED 2026-08-14, AND THE ASSUMPTION WOULD HAVE BEEN WRONG. The 2 x 2 has now been run** on the Silverado, commit `a5a7b62`, tabulated at Section J item **15a**. This entry's caution was correct and the answer is now known: **the two effects are NOT independent, they interact.** STUCK occupies exactly one corner of the square, requiring fine grid **and** high `mu` together, and the whole resolution sensitivity sits at `mu` 0.55 while at `mu` 0.30 a 37 percent refinement moves the margin only 10 -> 11 frames. **So "separately sufficient" was right and "independent" is now refuted rather than merely unestablished.** Ranked-open item (1) below is therefore **discharged for the Silverado** and stays open for the canonical Yaris hull, on which no `mu` x `n_grid` square exists. Two cautions carried from Section J item 15a: the STUCK corner **fails gate P-2** while the coarse `mu` 0.30 corner passes at 0.09170 (corrected, see 15a(c-CORRECTED)), so the only cleanly-contained corner is a SLIDE corner; and the square is NON-CANONICAL, at a `dx` 38.7 percent coarser than the Yaris at the same `n_grid`.

**"BOTH AT g96" IS A LABEL, NOT A SHARED CONFIGURATION, AND THIS IS THE EASIEST ERROR TO MAKE HERE.** `n_grid` is a cell COUNT; `grid_lim` is set from the loaded hull's extent (`_incoming/sim_standing.py:160`, `lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)`), so `dx = grid_lim/n_grid` differs per vehicle. Measured live:

| body at n_grid 96 | `grid_lim` | `dx` |
|---|---|---|
| Yaris, the canonical 17 | 9.4217 | **0.098143** |
| Rogue | 10.4425 | 0.108776 |
| Silverado, J15's flip | 13.0679 | **0.136124** |

**Silverado's g96 is 38.7 percent coarser than the Yaris g96 of the canonical set**, and D8's g96 is a fourth geometry again, a cube in the rung-e tank. Three bodies, three resolutions, one label. Never write that the two flips happened "at the same resolution."

**THE ONE THING BOTH ARMS GENUINELY SHARE IS UNCONTROLLED.** `sound_speed_ms` is **12.845233** in all six Silverado/Rogue rows and `BULK = 1.5e5` with gamma 1.1 gives **12.845** m/s in the friction rung: the same artificial sound speed, about 118x below real water, **never swept in either arm**. Isik and He 2023 (year corrected, see G7a) record that artificial sound speed can qualitatively flip a rigid-body outcome. So a third mechanism sitting under both flips has not been excluded, and **neither flip is evidence about the other's robustness.** This is the single cheapest test that would bear on both.

**CORRECTION TO J15, found while checking it.** J15 states Rogue's "drift still falls 67 percent". Re-derived live from the `rs_*` rows of job 3362208: g64 -> g128 the fall is **64.22 percent** on `max_surge_drift_m` (identically on `ratio_slide`, 14.4857 -> 5.1829) and **65.20 percent** on `final_disp_mag_m` (0.711779 -> 0.247664). No column in either store yields 67. Quote 64.2 percent and name the column. J15's passthrough figures do reproduce, 9.95 -> 9.88 percent, but they are endpoints: g96 sits at **10.72 percent**, above both, so the series is non-monotone rather than flat. The passthrough argument is nonetheless **stronger** than J15 claims, because Silverado's passthrough *rises* 8.36 -> 8.95 -> 9.68 percent while its drift falls 77.67 percent. Passthrough does not merely fail to explain the flip; it moves the wrong way.

**WHAT THIS PAIR DOES TO THE 16 SLIDE VERDICTS. Chain of established results, then one inference clearly marked as such.** Established: 5.3 puts any buoyancy error into `N`; J1b/J1d measure that error at about -25 to -30 percent and **grid-converged**, so refinement will not remove it; D8 shows `mu*N` is decisive in the horizontal channel. Inference, not measured: for a floor-supported body `N = W - F_b`, so a fractional error in `F_b` enters `N` amplified by `F_b/N`, and with `rho_veh` 310.494 against water 1000 that factor is a strong function of the submerged fraction `f` of the solid volume: **0.48x at f = 0.10, 1.81x at f = 0.20, 4.13x at f = 0.25, and 14.2x at f = 0.29**, diverging as `f` approaches the equilibrium float fraction 0.3105 where `N` goes to zero. **Quote no single amplification factor without its `f`, and `f` has not been measured for the hull** (the ladder's frac 0.20 is a cube). The SIGN is the usable part and it is robust across that whole range: under-predicting buoyancy over-predicts `N`, over-predicts `mu*N`, and therefore **under-predicts sliding**. Sixteen runs slide anyway, so the SLIDE verdicts are conservative in the safety-relevant direction, consistent with L-4. **The exposed verdict is the other one**: `sweepV_g64_v0p5`, the single STUCK, is the run this error could be holding still, and it already sits at `margin_frames` -3. Nobody has propagated this. Doing so is the concrete next test and it needs `f` for the hull first.

**OPEN, AND RANKED.** (1) Cross `mu` x `n_grid` on one body; it is the only thing that converts "separately sufficient" into "independent". (2) Sweep the artificial sound speed, the shared uncontrolled variable. (3) J15's item, the canonical set at g128, remains the highest-value single run. (4) Measure the hull's submerged fraction so the amplification above can be evaluated rather than bounded.

**RANKED ITEM (3) IS PARTLY DISCHARGED, NOTED 2026-08-14 AT THE THREE-WAY REGISTER MERGE.** D9 was written on one branch while **item 44** was written on another on the same day, neither aware of the other; the merge is the first place both are readable together. Item 44 runs the g128 canonical mass sweep: three masses, no verdict flips, **3 of the 17 configurations**. So (3) narrows, and it does **not** narrow (1), (2) or (4), which item 44 does not touch.

**"3 TESTED, 8 UNTESTED" DOES NOT SUM TO 17, AND THE GAP IS 6 RUNS. Flagged by adversarial review 2026-08-14 and verified live against `data/all_runs_inventory.csv`.** The 17 decompose as **9 mass/grid + 3 `sweepD` + 5 `sweepV`**, and the 9 are g48/g64/g96 crossed with m1100/m1609/m2337. Item 44 ran the three masses at g96 and g128, so on the natural reading only the **three g96 arms** gained a g128 companion. That leaves the **6 g48 and g64 arms** unaccounted for by both "3" and "8": 3 + 8 + 6 = 17. **The ambiguity is in the word "counterpart"**, which has been used to mean "this mass now has some g128 data" (true of 9 configurations) and "this exact grid-and-mass configuration was replicated at g128" (true of 3). **State which you mean.** This is not a defect unique to this note: the same loose "8 of the 17" appears in item 44's own text and in `54aa806`, so all three should be read with this arithmetic in hand. The **safe, unambiguous statement** is the one item 44 already makes: the 3 `sweepD` and 5 `sweepV`, including the only STUCK run, have **no g128 data at any mass**, which is the strongest form and is what the open item turns on. **Item 44 also strengthens (1) rather than weakening it**: it holds `mu` at 0.55 and walks grid, the same half of the 2 x 2 J15 walked, so the crossed design D9 asks for is still unrun. And note the direction item 44 adds: the g128 result is a **margin** collapse to `margin_frames` 0 at `k_crit` 0.9759 while the verdict holds, which is the de-synchronisation failure mode this entry's table attributes to refinement, now measured on the Yaris hull rather than the Silverado.

**D9a. THE FRICTION VALUE AND THE BUOYANCY ERROR BIAS THE SAME WAY, SO THE SINGLE STUCK VERDICT IS EXPOSED TWICE OVER, NOT ONCE. Noted 2026-08-14 at the three-way register reconciliation; this is a cross-section link, not a new measurement.** D9 arrived on the friction branch and Section G's friction items were already on `main`, so nothing connected them. D9's chain is: under-predicted buoyancy over-predicts `N`, over-predicts `mu*N`, and therefore **under-predicts sliding**, which makes the 16 SLIDE verdicts conservative and leaves `sweepV_g64_v0p5`, the single STUCK at `margin_frames` **-3**, as the exposed one. **G4, G4a and G4b add a second, independent push in the same direction.** The gated `mu` is **0.55**, which G4a establishes is a genuine measurement **of a lab rubber mat, not of submerged asphalt**, and which sits at the high end of this literature; the flood-vehicle convention, real per G4b and adopted deliberately as conservative by Shand et al. 2011, Bonham and Hattersley 1967 and Gordon and Stone 1973, is **0.30**. Al-Qadami 2023 uses 0.30 for exactly that reason (item 44's import). **A `mu` chosen high over-predicts resistance and under-predicts sliding by the same route the buoyancy error does.**

**What this does and does not license.** It does **not** say 0.55 is wrong: G4 refutes 0.30 as a wet-road measurement and 0.55 is defensible between the sand-gravel and concrete figures. It does **not** quantify anything; sliding resistance scales directly with `mu`, but no run has been done at another `mu` on the canonical hull, and D8's `mu` walk is a 600 kg/m^3 cube in the rung-e tank, not the 310.494 hull, so nothing transfers numerically. **What it does say is that the two known biases are not independent checks on each other, and the conservatism argument for the 16 SLIDE verdicts is correspondingly stronger while the STUCK verdict is correspondingly weaker.** **Concrete and cheap: the `mu` sensitivity bracket external report `65474f37` recommends, mu = 0.30 / 0.55 / 0.78, has never been run on the canonical hull, and `sweepV_g64_v0p5` is the single arm where it could change a published verdict.** That is a sharper and cheaper test than the four already ranked below, and it does not need a new mesh or a new grid.

**Cross-references, so neither entry is read alone: D8, D8a, D8b, D8c, D9a, G4, G4a, G4b, J15, J16, J1b, J1d, J1e, A6b, L-4, L-5.**

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

**E6b. THE LIVE CODE TELLS A DIFFERENT PROVENANCE STORY AND E6a's "resolved" ROW IS NOT SAFE TO LEAN ON. Read directly 2026-08-21.** `renders/yaris_render_s1/sim_standing.py:53` sources 1609 to *"AR&R large_passenger class figure (gates_both_scenarios.py:22)"* and `:62` sources 2337 to the AR&R `large_4wd` figure, and `gates_both_scenarios.py:19-20` confirms both numbers are paired with AR&R **class names**, not with vehicles. Separately `scripts/class_specific_2026-08-08.sbatch:52-56` states that **the Rogue LS-DYNA deck header carries NO mass at all**, unlike the Yaris and Silverado decks, and that the Rogue's own mass figure, 1571.3 kg, is **web-sourced from cars.com** and must be labelled so. So 1609 is an AR&R class limit that the Rogue was run under, not a measured Rogue mass, and the two are not interchangeable. The deck-derived masses that DO exist are **1571.3** (web-sourced, 18 live sites) and **2270.0** (deck header line 28, 17 live sites), and neither is the number the sweep uses. Beware the coincidence that the Ram's test-vehicle designation is **2270P** while 2270.0 kg is the **Silverado** deck mass.

**E6c. THE `floor_friction` SITE LIST IN ITEM 29 IS INCOMPLETE. Python `re` walk, main tree, 2026-08-21.** Item 29 names `sim_standing.py`, `sim_dam_break.py`, `box_sdf_collider_setup.py` and the Genesis Track 2 files. Live there are **9 sites and `box_sdf_collider_setup.py` is not among them**: `renders/yaris_render_s1/sim_standing.py:154`, `renders/yaris_render_s1/_incoming/sim_standing.py:76`, `analysis/render_v1/as_ran_local_copies/sim_standing.py:76`, `render_s2/multigeom_2026-08-08/sim_standing.py:154`, `renders/yaris_render_s3_enhanced/sim_enhanced.py:221`, `simulation/sim_dam_break.py:16`, `simulation/sim_channel.py:83`, `scripts/semi_empirical_baseline.py:51`, and **`.claude/hooks/session_start_protocol.py:6`**, which asserts a physics parameter into every session start. Separately `coup_friction` is **also literally 0.55** at six code sites (`simulation/can_it_ford_L2.py:44,:136`, `simulation/can_it_ford_L2_mpm_ytest.py:45,:137`, `designsafe-staging/scripts/can_it_ford_L2.py:40,:132`), so the never-conflate warning at the top of this register is load-bearing and now measured.
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

**READ BEFORE F6: FRAMING CORRECTED 2026-08-14, SAME DAY, BEFORE ANYONE ACTED ON IT: THESE ARE IMPLEMENTATION BLOCKERS, NOT METHOD BLOCKERS. See G19b.** Two catalogued papers put **MPM on a real road surface already**: Zhou et al. 2025 (tyre, pavement, water film, DOI `10.1063/5.0276643`) and Chen et al. 2022 (MPM deformable terrain under a vehicle, DETC2022-89632). **So nothing below is a limit of MPM as a method; F6a to F6d are facts about OUR scene and OUR domain.** F6e's negative survives because it is narrower than "MPM on a road": it is specifically about **following a vehicle with a refinement window through a large flood domain.** **And there is a sixth blocker, which is that none of this was read until 2026-08-14: the project's own commissioned catalogs contain the papers that address the problem. See G19a.**

**F6. THERE IS NO REALISTIC ENVIRONMENT, AND THE REASON IS FIVE MEASURED BLOCKERS RATHER THAN NEGLECT. Recorded 2026-08-14 because this was asked directly and the register, as sole authority, had no answer to point at.** Four of the five are now measured rather than argued.

**F6a. The scene IS a flat plane in a box, and that is the whole environment.** Per CLAUDE.md item 3 from primary source, the only constraints are a floor plane at friction 0.55 and four slip walls at 0.0. **No terrain, camber, crown, curb, gutter, gradient, drain or embankment exists.** The "road" is an infinite frictional plane.

**F6b. The grid is forced cubic, so a road cannot be expressed.** A road is long, thin and shallow; a cube spends almost all its cells on empty air above the vehicle to buy resolution in the floor layer. **This is the same mechanism behind D9's cross-vehicle trap**: `grid_lim` follows the loaded hull's extent, so a fixed `n_grid` across vehicles silently changes both `dx` and realized depth, which is also 15b's realized-depth confound seen from the domain side rather than the ladder side.

**F6c. A BOUNDED DOMAIN PHYSICALLY CANNOT MEASURE A SLOPE, so tilting the floor is not a workaround.** Conserving volume in a sealed box forces a redistribution **larger than the effect being measured**: water running downslope has nowhere to go, piles at the wall, and the pile exceeds the signal. Measured consequence, from the scene thread's own arms: downslope excursion grows **0.664, 0.937, 1.562 m** with increasing slope, and **a margin sized at S = 0 is wrong by 2.35x at S = 0.06.** **No grid refinement fixes this; it is a conservation argument, not a resolution one.**

**F6d. THE INSTRUMENT THAT WOULD FIX IT IS WIRED AND HAS NEVER BEEN VALIDATED.** The fix for F6c is an open channel with a **real mass sink**, inflow one end and outflow the other, so water leaves the domain instead of piling: **Zhao, Bolognin, Liang, Rohe and Vardon 2019**, *Computers and Fluids* 179, 27-33, DOI `10.1016/j.compfluid.2018.10.007`, implemented in Anura3D and, per CLAUDE.md, a **translation** into warpmpm rather than a port. It is wired. **It has no error bar.** **STANDING CONSEQUENCE: until that BC is validated against its analytic mass-loss rate and a steady inflow-equals-outflow level, NO realistic-domain result is quotable**, because every slope result inherits its tolerance.

**F6e. THE LITERATURE HAS NOT SOLVED THIS EITHER, WHICH MAKES IT A CONTRIBUTION RATHER THAN CATCH-UP. T2.** The multi-resolution review states verbatim: **"no demonstrated MPM study was found that follows a rigid vehicle with a refinement window through a large flood domain"**. The closest fluid work is dynamic AMR for free-surface waves and breaking **without a vehicle**; adaptive MPM-FSI is "preliminary and not road-scale flooding"; nested-grid GIMP, structured GIMP refinement, mesh grading, hierarchical B-spline MPM and local BSMPM bridging are **solid-only**. **Handle as a negative finding under G8's rule: the absence is in the searched corpus, not in the world.**

**AND IT NAMES THE TRAP THAT WOULD OTHERWISE BE TRIED FIRST:** sparse active grids and dynamic meshing cut memory when the domain is empty but **do not reduce the smallest-cell explicit timestep and do not resolve the floor layer.** So "make the domain bigger and sparser" does not buy what a road-scale scene needs. **Read this with G4f**: PPC co-refinement is refuted as the non-monotone mechanism here, band width dominates, so **AMR in a realistic domain must control band width, and co-refining PPC alone will not save it.**

**F6f. THE ALTERNATIVE ARCHITECTURE HAS TERRAIN NATIVELY AND ITS TERRAIN IS MEASURABLY BROKEN ON THIS HARDWARE. T1 for the measurement, aarch64 only.** Chrono ingests OBJ and heightfield terrain via `RigidTerrain::AddPatch`, exactly the capability warpmpm lacks, and it builds on GH200 in 94 s. But `RigidTerrain::GetNormal` measured over 10,800 samples on Vista aarch64:

| sample class | n | bad | rate | worst error |
|---|---|---|---|---|
| **ON-VERTEX** | 3600 | **3600** | **100.0%** | **88.85 deg** |
| ON-EDGE | 3600 | 0 | 0.0% | 1.02 deg |
| INTERIOR | 3600 | 0 | 0.0% | 1.09 deg |

**A heightfield places its vertices on a REGULAR GRID, so a 100 percent vertex-hit failure means terrain contact is unreliable at exactly the points a road surface is sampled**, with a worst-case normal essentially perpendicular to correct. Traced to **Bullet's trimesh raycast callback, not to Chrono**, which populates it correctly. **An x86 reproduction is in flight and either answer closes it**; until then this is an **aarch64 measurement and must not be stated as a general Chrono defect.** Note the escape hatch already identified: rigid and FEA tyres go through the contact engine and never consult `GetNormal`.

**F6g. THE LIMITATIONS THAT SURVIVE WHICHEVER WAY THIS IS BUILT.** Both are at G19 and both stay in the paper regardless of architecture: **"no validated vehicle-fording MPM chain is identified"**, and the records **"do not establish an experimental basis for the 1.5 m/s rule"**. Three further constraints the build must carry, all already in this register: **unsteady flow raises drag 40 to 50 percent (G6) and is not modelled, and a realistic environment makes flow LESS steady, so that gap grows rather than shrinks**; **settling has no threshold, only a protocol** (exclude transients, demonstrate stationarity, attach uncertainty from correlated samples), and a longer domain lengthens the transient, so the protocol becomes mandatory; and **order-dependent reductions can alter discrete gates**, which item 15a(e) has now observed rather than cited, at 7/8 SLIDE and 1/8 STUCK on one cell.

**F6h. THE ONE PLACE `mu` STOPS BEING A CONSTANT.** G4e records `floor_friction` 0.55 as a single scalar for the whole floor. **A realistic road surface is exactly where that becomes a field rather than a constant**, varying with sealed asphalt, gutter silt, gravel shoulder and debris, and G4/G4b bracket that range at roughly 0.16 to 1.15 across measured regimes. **Any realistic-environment build must decide whether `mu` is spatially varying before it reports a sliding threshold**, and the +83.3 percent gap between 0.55 and the 0.30 convention is the scale of what is at stake.

## SECTION G: literature and citations, T2 unless noted

**G1. The AR&R / Shand et al. 2011 thresholds describe a STATIONARY vehicle subjected to flow**, not a vehicle driving under power. Stated, not inferred: every criterion table is titled "stationary vehicle stability," and "vehicle movement through flood waters" is listed among the gaps the data cannot assess. Smith, Modra and Felder state directly "Laboratory testing was completed with stationary vehicles."

**G1a. AMENDED 2026-08-07, the configuration detail behind G1.** T2, external report `baa355db`, which tabulates what was physically done in every foundational study. Load-bearing additions:
Restraint was by fine threads read as force (Bonham & Hattersley 1967 at 1:25; Gordon & Stone 1973 at 1:16), and Keller & Mitsch 1993 was a **desk study with no physical test at all**, assuming mu = 0.3 and Cd = 1.1. Direct buoyancy measurement on a real full-scale vehicle did not happen until the UNSW WRL program (Smith, Modra, Felder 2017 and 2019); everything earlier inferred buoyancy from displaced volume or model float depth.
**Channel blockage ratio and afflux corrections are essentially UNREPORTED across every incipient-motion study in this literature.** That is a limitation of the thresholds this project validates against, and our own tank has a computable blockage ratio, so it is also an opportunity. Do not claim the AR&R curves are blockage-corrected.
Model-scale watertight vehicles **float too shallow**, a sealing scale effect, and full-scale vehicles are somewhat more stable than the conservative AR&R curves (Kramer 2016 prototype; Smith, Modra, Felder). Yaw matters and was varied by several studies, with Kramer finding the critical angle at 45 degrees, and per-study mu varies strongly with yaw: Toda et al. 2013 report 0.26 at 0 degrees against 0.57 at 90 degrees for a sedan.

**G2. The 3.0 m/s velocity cap is administrative.** Imposed to keep vehicle curves consistent with human-stability curves, not derived from vehicle data. The constant D×V form is also administrative, inherited from pedestrian stability work.

**G3. AR&R limits.** Still-water depths 0.3 / 0.4 / 0.5 m and D×V limits 0.30 / 0.45 / 0.60 m2/s for small passenger, large passenger, large 4WD.
**0.45 m2/s is BOTH the AR&R large-passenger threshold AND, separately, a value Azhar et al. 2026 propose for small passenger vehicles** under combined critical conditions, with the caveat that it "needs to be verified by further scenario testing." Never conflate the two uses.

**G3a. THE SMALL-PASSENGER CLASS READS 0.3 IN BOTH SERIES, IN DIFFERENT UNITS, AND THAT COINCIDENCE IS WHY THE TWO KEEP GETTING CONFLATED. Added 2026-08-14.** AR&R carries **two** limits per class, not one: a depth x velocity product (**0.30 / 0.45 / 0.60 m2/s**) and a still-water buoyancy **depth** (**0.30 / 0.40 / 0.50 m**). For small passenger both are the numeral **0.3**, in **m2/s** and in **m** respectively. **A bare "AR&R 0.3" is ambiguous and must never be written.** Quote the unit every time, and say which series. **This is structurally the same defect as D7a**, where `slide_m` 0.05 (metres) and `slide_speed_ms` 0.05 (metres per second) share a numeral inside `failure_modes.py` and a find-and-replace on the value would silently convert a speed into a distance. Same trap, different section: **deduplicate and cite by name and unit, never by numeral.** Note the two series also diverge above the small class, 0.45 against 0.40 and 0.60 against 0.50, so the coincidence is confined to the one class most likely to be quoted.

**CONFIRMED AGAINST THE PRIMARY PDF 2026-08-14, commit `1c9ef7e`**, upgrading this entry from a secondary-artifact reading: all six figures reproduce exactly from **Table 3** of `ARR_Project_10_Stage2_Report_Final.pdf`, and the divergence one row down is confirmed, so **the 0.3 pairing is an ACCIDENT, not an identity.** **Terminology, three names for one quantity, and the register should use the report's own:** the table header reads **"Limiting still water depth"**, the body text reads **"floating limits"**, and **"limiting buoyancy depth" appears only in secondary sources.** Prefer **floating limit**, and never let the third name imply a separately-derived quantity.

**G4. Friction. `mu_wet ≈ 0.30` is REFUTED as a wet-road value.** 0.30 is the sand and gravel worst case in Smith, Modra and Felder 2019. Wet AND dry concrete both read about 0.78. Model-scale measurements run 0.52 to 0.68.
Any skill file asserting "mu_wet 0.3 is the primary, best-sourced defensible value" is WRONG and must be corrected.
`floor_friction` 0.55 remains defensible as a value between the sand-gravel floor and the concrete figure, but NOT as a conservative wet-road number.

**G4c. THREE DISTINCT NUMBERS SIT NEAR 0.78 WITH THREE DIFFERENT PROVENANCES. Flagged 2026-08-14, NOT yet settled against the primary source.** G4 above records "wet AND dry concrete both read about **0.78**" from Smith, Modra and Felder 2019. External report `65474f37` separately records that the same paper's full-scale traction tests measured an **average `mu` ~ 0.76**, and that the associated **WRL Technical Report 2017/07 (Smith et al. 2017) *used* 0.78** as an input. Those are three different things — a surface-specific reading, a test-wide average, and a value adopted in a technical report — and they are **not** in conflict, but collapsing them into one "Smith 0.78" would be a citation error of exactly the kind Section G exists to prevent. **Do not quote 0.78 without saying which of the three it is.** The same report also notes that Smith's published stability curves are **commonly rescaled to the conservative flood convention of 0.3 for guideline use**, so a curve attributed to Smith may embed 0.3 rather than 0.76 or 0.78. **Unresolved and cheap to close**: read Smith, Modra and Felder 2019 (DOI `10.1111/jfr3.12527`, already the verified full-scale Yaris source per G5) and record which number belongs to which surface. Until then treat G4's 0.78 as **provenance-ambiguous**, not wrong.

**PARTLY RESOLVED 2026-08-14 by an independent route, contributed by the moving-validation thread.** Wong tabulates wet **concrete** separately from wet asphalt, at `mu_p` **0.80** / `mu_s` **0.70** (G4a). Smith's ~0.76 to 0.78 sits inside that concrete band and **outside** the wet-asphalt band 0.50-0.70. **That independently corroborates the SURFACE attribution: the 0.78 family is a concrete-surface value, which is what G4 says.** It does **not** resolve the remaining ambiguity, which is between a surface-specific reading, a test-wide average and a value adopted in WRL TR 2017/07; that still needs the primary read. **And it sharpens the contrast with 0.55: 0.55 is an ASPHALT-range number, measured on a rubber mat, so 0.55 and 0.78 are not two points on one surface's scale.**

**G4a. AMENDED 2026-08-07. The "0.55 per Azhar et al. 2023" attribution is no longer unverified.** Citation-provenance audit, T2, external report `65474f37`: Azhar, Pauwels and Bui 2023 (DOI 10.1111/jfr3.12885, open access, correct title "Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements") **measured 0.55 themselves** with a spring balance on the rubber mat used as their road-surface proxy, and cite Wong, *Theory of Ground Vehicles*, only to show the value falls inside a handbook range of 0.50 to 0.70 for tyres on wet asphalt. Two-hop chain, terminating in a general-automotive handbook, not in a flood-specific measurement. **Three details added 2026-08-14 from the same report, none of which were recorded here before.** (i) **Wong tabulates TWO numbers for wet asphalt, a PEAK `mu_p` 0.50-0.70 and a SLIDING `mu_s` 0.45-0.60**, and this entry previously quoted only the peak. 0.55 sits inside the peak band but near the TOP of the sliding band, and it is the *sliding* coefficient that governs the SLIDE criterion, so quoting the peak alone flatters the value. Wong lists wet **concrete** separately and higher (`mu_p` 0.80 / `mu_s` 0.70), so "0.50-0.70 for wet asphalt or concrete" is wrong for concrete. (ii) **The terminus is named: SAE Paper 690214, Harned, Johnston and Scharpf 1969**, a General Motors tyre brake-force study, supplemented by Bosch *Automotive Handbook* compilations. **Carry the report's own caveat with it**: it flags the specific table-cell-to-690214 link as **"highly likely rather than 100% visually confirmed"**, so cite the terminus as probable, not established. (iii) Azhar's own conclusions state the value "could drop to as low as 0.30 in case of poor road conditions."

**A WORDING GUARD, added 2026-08-14 from the moving-validation thread's direct read of the artifact.** Azhar's phrase **"in accordance with"** refers to internal consistency between their **1:14 physical flume model and their 1:1 SPH model**, NOT to accordance with a prior paper. **Any statement that Azhar adopted 0.55 without measuring it is wrong.** It is a hybrid: a measured lab value cross-checked against a handbook range. Their model carried a **COG height 0.45 m and weight 1097 kg**; note 1097 kg is within 0.3 percent of this project's canonical 1100 kg, which is a coincidence of vehicle class and **not** a shared source, so do not cite one for the other. So: it is a genuine measurement, but **of lab rubber mat, not of submerged asphalt**, and it sits at the high end of this literature's assumptions. The canonical paper at `paper/canonical_2026-08-02/conference_101719_1.tex:205` already states exactly this, independently; that text is now corroborated, not merely unrefuted.

**G4b. 0.30 is REFUTED as a measurement and REAL as a convention. Do not collapse the two.** G4 refutes 0.30 as a wet-road measured value, and that stands. Separately, 0.30 genuinely is the flood-vehicle literature's inherited convention: Shand et al. 2011 record that "correspondence with various road experts and test laboratories" settled on mu = 0.3, and Bonham & Hattersley 1967 and Gordon & Stone 1973 both adopt it. **A FOURTH convention source, added 2026-08-14: Keller and Mitsch 1993, UWRAA Report No. 69, also adopts 0.3, purely theoretically.** Full report identifiers, so the convention can be traced rather than asserted: Bonham and Hattersley 1967 *Low-level causeways*, WRL Report No. 100, UNSW, with a **measured** range of 0.3 to 0.5 for a Ford Falcon; Gordon and Stone 1973 *Car stability on road floodways*, Report 73/12, UNSW; Shand, Cox, Blacka and Smith 2011, Report P10/S2/020, whose verbatim justification is that **"While the assumed coefficient of friction of mu = 0.3 is likely conservative, the present lack of suitable data and wide range of road surfaces and tyre tread conditions prohibits the refinement of the coefficient."** **That sentence is the convention's actual warrant: 0.3 is adopted BECAUSE the data are insufficient, and is explicitly labelled conservative by the people who adopted it.** Four sources adopting one number from a shared data gap is one convention, not four independent measurements, which is item 43's rule applied to the literature. **Two sentences and one measured set below were present only on `claude/add-ci-checks` before the 2026-08-18 merge and are carried in here.** Anyone reading only the convention half will try to resurrect 0.30 as best-sourced and will be wrong. Anyone reading only G4 will call the AR&R derivation unsourced and will also be wrong. Measured comparanda, Shu et al. 2011 spring balance on wet carpet: Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68.

**G4d. READ FROM THE AR&R PDF ITSELF, NOT FROM A SECONDARY ARTIFACT, AND IT RELOCATES THE 0.3. Commit `1c9ef7e` on `claude/fork-vista-triage`, 2026-08-14, read from `ARR_Project_10_Stage2_Report_Final.pdf`.** Three corrections and one addition, all superseding any secondary rendering including the one this register used.

    **(i) THE 0.3 IS NOT AR&R'S MEASUREMENT. It is Bonham and Hattersley's 1967 ASSUMPTION, carried forward** while the report itself notes that measured stationary values are roughly three times higher. G4b above says four sources "adopt" it, which is right; this names the origin.

    **(ii) THE FRICTION SENTENCE APPEARS TWICE IN THE PDF, and the conclusions version is the better citation because it states what the value was used FOR:** *"While a coefficient of friction of 0.3 assumed WHEN COMPARING EXPERIMENTAL AND ANALYTICAL RESULTS is likely conservative, the present lack of suitable data and wide range of road surfaces and tyre tread conditions prohibits the refinement of the coefficient."* **The PDF writes the bare number, not the `mu` symbol.** Quote this version, and note the scope clause: 0.3 was assumed *for comparing experiment against analysis*, not asserted as a road property.

    **(iii) A THIRD PASSAGE, not previously quoted anywhere in this project, gives the measurements that make 0.3 conservative.** Stationary flooded-road tyre coefficients **0.85 to 1.15** (Yandell 1973, measured in Canberra by UNSW); skidding at 30 km/h **0.16 to 0.48** (Woods et al. 1960). **These are two DIFFERENT physical quantities and 0.3 sits between them**, so 0.3 is not a midpoint of one distribution.

    **(iv) `floor_friction` 0.55 IS NOW BRACKETED BY PRIMARY NUMBERS FOR THE FIRST TIME:**

    | quantity | value |
    |---|---|
    | skidding at 30 km/h, Woods et al. 1960 | 0.16 to 0.48 |
    | AR&R **assumed** (Bonham and Hattersley 1967) | 0.30 |
    | **THIS PROJECT'S FLOOR** | **0.55** |
    | Smith 2019 swept pair | 0.3 and 0.78 |
    | stationary flooded road, Yandell 1973 | 0.85 to 1.15 |

    **0.55 sits in the gap between the two measured regimes, above every skidding value and below every stationary one.** Consequence, and it agrees with D9a by a different route: 0.55 is **less conservative than AR&R's own 0.3**, more friction means more traction resisting slide, so relative to the guideline assumption this project's floor biases **away from a SLIDE verdict** — and 16 of 17 gated verdicts are SLIDE.

    **CAVEAT, LOAD-BEARING, DO NOT DROP IT WHEN QUOTING THE BRACKET.** The AR&R coefficient is **tyre-on-road in an analytical force balance over four contact patches**; this project's `floor_friction` is a **Coulomb coefficient in the MPM floor contact applied across the hull's whole lower particle surface** (A7, D8a). Analogous in direction and rough magnitude, **not the same quantity**. **No claim may say 0.55 "is" a measured tyre friction.** That also bounds G4a: Azhar measured 0.55 on a rubber mat with a spring balance, which is a real measurement of a surrogate surface, not of the quantity the solver applies.

**G4e. THE CONSOLIDATED FRICTION ENTRY. SIX SESSIONS REACHED THIS FROM SIX DIRECTIONS ON 2026-08-14 AND NONE OWNED IT; this is the single place it is stated. Components live at G4, G4a, G4b, G4c, G4d and Section J item 15a and are NOT restated here, because restating them would manufacture the multi-source appearance item 43 exists to prevent.**

**THE HEADLINE, and it is the only sentence that needs to travel: `floor_friction` 0.55 biases AWAY from a slide verdict. It is therefore CONSERVATIVE for the 16 SLIDE verdicts and OPTIMISTIC for the Silverado's flip into STUCK.** More friction means more traction resisting slide. Against the AR&R convention of 0.30 it raises available traction by **+83.3 percent** (`0.55/0.30 = 1.8333`, arithmetic checked).

**THE LIVE VALUE INVENTORY, enumerated 2026-08-14 by a `/usr/bin/grep` over `*.py` excluding `third_party/` and `.claude/worktrees/`, because a bare count was about to be published as "a fourth value" and that undercounts.** The values split into CHOSEN and INHERITED-DEFAULT, and conflating those two is the defect:

| value | where | what surface | chosen or default |
|---|---|---|---|
| **0.55** | `sim_standing.py` `floor_friction`, the gated 17 | MPM **floor plane**, hull underside | chosen |
| **0.55** | `box_sdf_collider_setup.py:78` | the **vehicle SDF collider** | chosen |
| **0.55** | `coup_friction`, 6 sites | Genesis `LegacyCoupler` | chosen, **Genesis not warpmpm** |
| **0.4** | `validate_coupling_force.py:296` | SDF collider, `separable` | **solver DEFAULT, written out** |
| **0.4** | `moving_vehicle_driver.py:80`, `claude/fork-moving-driver` only | SDF collider | **solver DEFAULT**, its own comment says "NOT tuned" |
| **0.2** | `box_sdf_collider_setup.py:59` | **floor plane**, slip | chosen |
| **0.2** | `box_sdf_collider_setup.py:64-67` | 4 lateral slip walls | chosen |
| **0.0** | gated walls, `validate_coupling_force.py` | slip walls | `add_plane` DEFAULT |

**TWO CORRECTIONS THIS TABLE FORCES.** (i) **0.4 is NOT a fourth chosen value. It is the solver's own default**, verified live at `kernels/mpm_solver_warp.py:2621-2624`, `def add_sdf_collider(..., friction=0.4, ...)`; `add_plane` defaults to `friction=0.0` at `core/solver.py:212`. Both 0.4 sites are that default, one written out explicitly. **An untouched library default is not a parameter choice and must not be tabulated beside 0.55 as though someone picked it.** **UPDATED 2026-08-14 and it sharpens rather than softens: the moving-driver thread reports `COLLIDER_FRICTION` 0.4 is INFLUENTIAL on its results.** Combined with the above, the correct statement is the uncomfortable one: **an untuned library default is materially influencing output.** That is worse than a badly-chosen parameter, because nobody chose it and its own source comment says "NOT tuned". **It needs a sweep before any result depending on it is quoted**, and it is the same defect class as the artificial sound speed at D9, a value inherited rather than selected and never varied. (ii) **A 0.2 family exists that no session named**, five sites in `box_sdf_collider_setup.py`, and in that same file **the floor is 0.2 while the vehicle collider is 0.55, which is the OPPOSITE assignment from the gated scene** where 0.55 is the floor. **So "0.55" does not denote the same surface across files.** Always name the surface with the value.

**PROVENANCE, one line each, full working at the cited items.** 0.55 is Azhar, Pauwels and Bui 2023's own spring-balance measurement of a lab rubber mat, chaining through Wong's *Theory of Ground Vehicles* wet-asphalt band to a 1969 GM tyre brake-force study, general automotive and not submerged (G4a, terminus caveat there). 0.30 is **Bonham and Hattersley's 1967 assumption carried forward**, not an AR&R measurement, adopted because the data are insufficient and labelled conservative by those who adopted it (G4b, G4d). The regime table placing 0.55 in the gap between two measured regimes is at G4d. Resolution-dependence is itself friction-dependent, so **J15's flip must carry its `mu`** (Section J item 15a).

**THE ENTRY'S OWN GUARD, carried verbatim as required.** *The AR&R coefficient is tyre-on-road across four contact patches in an analytical force balance; ours is a Coulomb coefficient in the MPM floor contact across the whole hull underside. Comparable in direction and magnitude, **not the same quantity**. No claim may say 0.55 "is" a measured tyre friction.*

**CONFIRMATION STATE, 2026-08-14. Recorded because five lines are attributed to sessions that have not yet confirmed them.** Verified by me from primary source or live code: the 0.30 origin (AR&R PDF), the value inventory and both defaults (live grep plus vendored solver), the +83.3 percent arithmetic, and the D5 square at item 15a (read from commit `a5a7b62`). **UNCONFIRMED BY THEIR OWNING SESSION at time of writing: D2's regime-table line, D5's line, D6's rendered-frame caveat line, D9's `COLLIDER_FRICTION` line.** D9's line is additionally **corrected** here rather than merely relayed, per (i) above.

**D11's provenance-chain line: CONFIRMED 2026-08-14 by its owning session, from a direct read of artifact `65474f37` outside the blocked directory, with one self-correction.** It withdrew its own earlier wording that the chain terminates in SAE 690214 as though established; the correct form is **SAE 690214 plus Bosch *Automotive Handbook* compilations, and hop 2 is "highly likely", not confirmed.** **That correction was already carried in G4a before the confirmation arrived**, because the artifact's own caveat was read directly rather than taken from the relay that had dropped it. Hops 0 and 1 are documented inside the Azhar paper itself and are solid; only hop 2 is soft. Its **+83.3 percent** figure is confirmed and is linear in `mu`, and it asked that D2's caveat be carried verbatim rather than its own, which is what this entry does. Anyone reading only the convention half will try to resurrect 0.30 as best-sourced and will be wrong. Anyone reading only G4 will call the AR&R derivation unsourced and will also be wrong. Measured comparanda, Shu et al. 2011 spring balance on wet carpet: Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68.

**G4f. FIXED PARTICLES-PER-CELL IS REFUTED AS THE MECHANISM FOR THIS SCENE'S NON-MONOTONE CONVERGENCE. Tested 2026-08-14 on Vista GH200 c642-012, commit `5abdbec`, read from the commit body here.** The multi-resolution review names fixed PPC as the mechanism by which MPM loses convergence under refinement, and this project holds **PPC = 8**, so it was the candidate cause of the Yaris gate error going 63.3, 37.1, 52.3. A no-forcing control was run with `--ppc` co-refining instead of held:

| cells | PPC 8 fixed, gate error | co-refined, PPC / gate error |
|---|---|---|
| 2.04 | 63.28 | 8 / **63.28** |
| 3.06 | 37.06 | 27 / 47.03 |
| 4.08 | 52.27 | 64 / 70.97 |

~~**The control is exact**: the first row is the same configuration in both arms and returns an identical gate error and identical particle count (45138), so PPC is the only variable.~~ **THAT SENTENCE IS OVERSTATED AND IS WITHDRAWN, 2026-08-14, on adversarial review.** At the coarsest grid **co-refined PPC EQUALS fixed PPC = 8 BY CONSTRUCTION**, because 8 is the project default, so the identical row 1 may be **one data point reported twice rather than two independent executions that agreed.** An identity by construction is not a control. **This matters because item 42 measured this exact stack returning DIFFERENT results from identical seed and config**, so two genuine executions agreeing to six figures would have been notable evidence and a single reused row is none. **UNVERIFIABLE either way: no raw log or CSV for the six runs exists** (see the provenance note below). **The refutation of PPC does not depend on it** — it rests on both ladders staying non-monotone and on co-refinement making agreement worse at every refined rung — **but do not cite row 1 as a validated control.** **VERDICT: REFUTED for this scene.** Both ladders are non-monotone with the same down-then-up shape; co-refinement did not flatten it. **And it made agreement WORSE at every refined rung**, +27 percent at 3.06 cells and +36 percent at 4.08, while raising the finest grid from 429,052 to **3,471,745** water particles. **Eight times the particles per cell bought a worse answer.**

**RECORD THIS AS A REFUTED HYPOTHESIS WITH ITS TEST, NOT AS AN OPEN QUESTION.** **UPDATED 2026-08-14: item 5 now has a CANDIDATE mechanism at B9, band width tied to `dx` by the engine default, which reproduces 63.28 / 37.06 / 52.27 exactly. B9's own sweep also refutes the simple form of that hypothesis, so it is a candidate and not a cause. Read B9 with this entry.** CLAUDE.md item 5's non-monotone grid study therefore **still has no CONFIRMED mechanism**, and **Steffen, Kirby and Berzins 2008 remains the correct citation for the PHENOMENON while NOT being the operative mechanism here** (L-5, G22, item 44). Anywhere item 44 or L-5 is cited as though PPC-at-8 were the tested cause, that is now wrong. `[live]` the adversarial review on the same branch (`a846cc9`) confirmed three blocking defects in that thread's other results and **contains zero mentions of PPC**, so this result is not among the damaged ones. **One unchecked interaction**: that review also corrects a depth bug giving `depth_cells` 1.84 -> 2.00 at `n_grid` 64 and 3.68 -> 3.50 at 128; **whether the cells column above is affected has not been verified here.**

**G4g. SMITH 2019 IS A SIDEWAYS WINCH TEST **FROM THE REAR AXLE**, AND A RELAYED CLAIM THAT IT IS "NOT REAR-AXLE" IS REFUTED. Verified 2026-08-14 against the paper's own full text via Scite, DOI `10.1111/jfr3.12527`, open access.** Verbatim: *"prototype vehicles were partially submerged in different water depths (0 <= d <= 1 m) and **towed sideways by the axles**"*; *"**The testing was focussed on the stability of the rear axle**, as the point of instability was defined as the loss of traction at any axle, and for all vehicles tested the engine was forward mounted meaning the rear axle was lighter"*; *"All wheels were locked ... for winching **both axles**, but only the rear axles were locked for winching the rear axle"*. **So it is BOTH: sideways winching AND rear-axle focussed, with a both-axles variant also run. "Sideways winch, therefore not rear-axle" is a false dichotomy.**

**THE FRICTION MEASUREMENT SPECIFICALLY USED THE REAR AXLE, which bears on G4 and G4c:** *"The coefficient of friction mu between the vehicle tyres and the ground surface was directly measured for the **Nissan Patrol and the Ford Festiva**. The horizontal traction force was determined by **winching the vehicle sideways from the rear axle**. The vertical weight force was measured directly by hoisting the vehicles from the rear wheel."* **So the friction coefficients this register quotes from Smith 2019 come from the Patrol and the Festiva, NOT from the Yaris.** That is a further reason G4c's 0.78 needs its surface and vehicle named.

**AND IT CONFIRMS G5 FROM THE PRIMARY SOURCE: the Toyota Yaris IS one of the tested vehicles** — *"Time series of traction forces for winch tests with **Toyota Yaris**. (a) Traction forces for Toyota Yaris winched from rear axle with one passenger"* — so G5's "the verified full-scale Yaris source is Smith, Modra and Felder 2019" is now confirmed against the paper rather than inherited.

**A PROVENANCE DETAIL FOR G4b AND G4d, not previously recorded:** Smith 2019 states that **Bonham and Hattersley suggested the single conservative 0.3 "after a detailed review of studies by Bird and Scott and adjustments for worst-case conditions of SIDEWAY forces and SLIPPING forces rather than BRAKING force, and taking debris into account."** So the 0.3 convention is a worst-case adjustment of braking-derived data toward sideways slipping, which is a better account of its origin than "an assumption carried forward" alone and reinforces that it is deliberately conservative.

**G4h. THE 0.55 FRAMING MUST BE SOFTENED: IT SITS INSIDE A PEER-MEASURED RANGE, ARRIVED AT BY THE SAME METHOD. T2, artifact `baa355db`, read 2026-08-15. This CORRECTS wording carried all night, including in this register.** **Martinez-Gomariz et al. 2017 measured mu = 0.52 to 0.62** on a **wet metallic surface**, by **spring balance and tilt angle**, on 12 model cars. **That brackets 0.55, by the same method Azhar used.** So the framing that 0.55 is anomalously high, or is an artefact of one lab's rubber mat, is wrong and must be replaced by: **0.55 sits inside one peer-measured range of 0.52-0.62, while the guidelines ADOPT 0.30. The gap is between measured and adopted values, not between this project's value and the field's.**

**What does NOT change.** The arithmetic, 0.55/0.30 = **1.8333**, so +83.3 percent on `T_avail`. The direction at G4d's headline, conservative for the 16 SLIDE verdicts and optimistic for the flip into STUCK. And G4b's separation of 0.30-as-measurement from 0.30-as-convention. **Only the word "anomalous" goes**, and with it the implied limitation that the value rests on a single unrepresentative surface.

**G4i. THE 0.30 CONVENTION'S ACTUAL DERIVATION, AND IT RECONSTRUCTS TO 0.288 RATHER THAN 0.300. T2 for the derivation, T1 for the arithmetic check.** G4b and G4d(i) record that 0.30 is Bonham and Hattersley's 1967 **assumption** but not how they arrived at it. They took a **braking coefficient of 0.5** and reduced it **10 percent for sideways, 20 percent for slip and 20 percent for debris.** Checked here, and the two readings do not agree:

- **multiplicative**, `0.5 x 0.9 x 0.8 x 0.8` = **0.288**, which rounds to 0.3
- **additive**, `0.5 x (1 - 0.1 - 0.2 - 0.2)` = **0.25**, which does not

**So the multiplicative reading is the one that reproduces the convention, and the canonical 0.30 is a rounded 0.288.** State it that way: the number under every downstream guideline is **a rounded product of three judgement factors applied to a braking coefficient**, not a measurement of anything.

**G4j. THE MEASURED-mu INVENTORY WITH SOURCES. T2, same artifact, NONE checked against a primary record, so all are UNREVIEWED at that tier.**

| source | mu | condition |
|---|---|---|
| Bonham and Hattersley 1967 | **0.30** | **ADOPTED, never measured**, see G4i |
| Gordon and Stone 1973 (citing Yandell 1973) | 0.85 - 1.15 / 0.16 - 0.48 | stationary flooded road / skidding |
| Shu 2011 | 0.39 / 0.50 / 0.68 | Transit / Focus / Volvo |
| Toda 2013 | 0.26 at 0 deg, 0.57 at 90 deg; 0.42 and 0.65 | sedan; minivan |
| Xia 2014 | 0.25 at 0 deg, 0.75 at 90 deg | |
| Martinez-Gomariz et al. 2017 | **0.52 - 0.62** | wet metallic, spring balance and tilt, 12 model cars |
| Shah 2018 | 0.09 / 0.52 | rolling / sliding |
| Smith 2019 | **measured 0.75 wet and 0.78 dry**, then **ADOPTED 0.30** for the published curves | |
| Azhar, Pauwels and Bui 2023 | 0.55 | spring balance, lab rubber mat |

**Three things this settles or sharpens.** **(a) Toda 2013 is the source of the 0.26 to 0.57 yaw spread** that has been cited in this project without one. **(b) Smith 2019 splits wet 0.75 from dry 0.78**, so any statement that its value is "0.78 wet-or-dry" is contradicted; this bears directly on **G4c's three numbers near 0.78 and must be settled against the primary source, not against this artifact.** **(c) THE ADOPTED-VERSUS-MEASURED PATTERN IS SYSTEMATIC AND IS THE REAL FINDING**: Bonham adopts 0.30 without measuring, and **Smith measures 0.75-0.78 and then adopts 0.30 anyway for its published curves.** Two foundational sources adopt a value their own or cited measurements contradict. That is a stronger and more citable statement than any single number in the table.

**AND mu IS NOT A SCALAR PROPERTY OF THE ROAD.** Toda's 0.26 to 0.57 and Xia's 0.25 to 0.75 are **2.2x and 3.0x swings with yaw alone, on one surface.** F6h already records that a realistic road makes `floor_friction` a field rather than a constant; this adds that **even a perfectly uniform road makes it a function of orientation**, which the single scalar at G4e cannot express either.

**G4k. THREE SHORTER ITEMS FROM THE SAME ARTIFACT. T2, 2026-08-15.** **(a) L-2 IS CONFIRMED FROM THE PRIMARY CONFIGURATION**: the 3.0 m/s cap was set by Shand to keep the vehicle curves **below the human-stability curves**, not from vehicle data. Cite it as administrative with that reason. **(b) Kramer 2016 finds the critical orientation is 45 degrees, not 0 or 90**, and that model-scale watertight vehicles **float too shallow through a sealing scale effect.** Both bear on CLAUDE.md addendum A-4 and on any future orientation choice, and the second is a reason model-scale flotation depths transfer badly to full scale. **(c) Blockage ratio is unreported in essentially every study**, which is a nameable gap. **Say "essentially every", not "every":** this register already carries one measured value, blockage ratio **0.22**, read from a paper's full text at Section J, so a blanket claim is refutable from inside this document.

**G5. Al-Qadami tested a PERODUA VIVA, not a Toyota Yaris.** Any claim that Al-Qadami found a Yaris floating at 0.40 m under about 11 kN buoyancy is a MISATTRIBUTION and must never be used. The verified full-scale Yaris source is Smith, Modra and Felder 2019, DOI 10.1111/jfr3.12527.

**G5a. THE YARIS MISATTRIBUTION CAME BACK ON 2026-08-15, WITH A YEAR AND A JOURNAL ATTACHED, AND IT IS STILL WRONG. G5 IS UPHELD AND NOW COVERS THE EXACT PAPER THE RELAY NAMED. Verified via Scite the same day; two independent citing papers' full text.** A relay reported, as "a full-scale validation datum for our own vehicle", that **Al-Qadami et al. 2021 in *Natural Hazards* found a full-scale Toyota Yaris floating at 0.40 m under approximately 11 kN buoyancy**. That is the claim G5 already bars. **The new detail is what makes this worth recording: G5's supporting quote came from the 2023 *Sustainability* paper, so a differently-dated Al-Qadami paper was a live loophole. It is now closed.**

The paper is **`10.1007/s11069-021-04949-6`**, *"Full-scale experimental investigations on the response of a flooded passenger vehicle under subcritical conditions"*, Al-Qadami, Mustaffa and Shah, *Natural Hazards* **110(1):325-348**, online **2021-07-26**. It is **closed access, `contentDenied`**, so it cannot be read directly, but two citing papers state its vehicle from their own full text:

- `10.3390/su151713262`: *"The experimental study was performed for the **same vehicle model (Peruodu Viva)** but only under subcritical flow conditions."*
- `10.1111/jfr3.12828`: *"Al-Qadami, Mustaffa, Shah, et al. (2022) conducted an experimental study on the **same vehicle model** at full-scale size."*

**THE NUMBERS ARE ALSO MIS-PAIRED, which is a second and separate error.** The literature splits them: **0.40 m is the full-scale experimental floating depth**, while **0.38 m and 9.2 kN are the CFD pair**, stated verbatim in both citing papers as *"the vehicle floated at 0.38 m water depth and 9.2 KN buoyancy force"*. **The relayed "approximately 11 kN" could not be sourced to any of these papers**, and the buoyancy that does have a source, 9.2 kN, belongs with 0.38 m rather than with 0.40 m. **So the relay pairs an experimental depth with an unsourced buoyancy.** Do not quote "0.40 m and 11 kN" as a pair from anywhere.

**A CITATION-YEAR TRAP, recorded so it does not cause a third round.** This paper is online 2021 but sits in a 2022 issue, and the citing literature calls it **"Al-Qadami et al. (2022)"** throughout. **The same paper is therefore reachable as 2021 or 2022**, which is how it re-entered wearing a year G5 had not explicitly barred. G5's rule is about the vehicle, not the year: **the verified full-scale Yaris source remains Smith, Modra and Felder 2019, DOI `10.1111/jfr3.12527`.** One further caution for anyone re-checking: `10.1111/jfr3.12828` prints the figure as *"0.40 cm"*, a unit typo for metres.

**G6. Unsteady flow raises drag 40 to 50 percent** relative to steady at matched conditions, varying approximately linearly with flow acceleration. Azhar et al. 2026, DOI 10.1111/jfr3.70181. Best-sourced of that batch, safe to cite directly. Steady baseline: Azhar et al. 2023, DOI 10.1111/jfr3.12885.

**G7. Artificial sound speed can qualitatively flip a rigid-body outcome.** Isik and He ~~2022~~ **2023**, DOI 10.1007/s40571-022-00511-8.

**G7a. THE YEAR IS 2023, NOT 2022, AND THE DOI IS WHY THE ERROR HAPPENED. Raised by another session 2026-08-14, then verified INDEPENDENTLY here against Scite rather than accepted on relay.** Full record: **Isik, Doruk and He, Zhaoming**, *"Effect of numerical speed of sound and density diffusion on SPH modeling of rigid body migration in plane Poiseuille flow"*, **Computational Particle Mechanics 10(3):503-517**, published **2023-06-01**, DOI `10.1007/s40571-022-00511-8`, closed access, **no editorial notices**. The relayed volume, issue and pages reproduce exactly.

**THE TRAP, and it is reusable: the DOI contains `-022-` while the issue is 2023.** Springer mints the DOI at acceptance and the article appears in a later volume, so **the year embedded in a DOI is not the publication year.** G7 above carried the correct DOI and the wrong year, which is exactly what that mismatch produces. **Never read a year out of a DOI string.**

**TWO SCOPE CORRECTIONS THAT MATTER MORE THAN THE YEAR.** (i) **It is SPH, not MPM.** The title says so. This project is warpmpm, and G7 is cited in D9 and at item 44's neighbourhood as a caution on our own artificial sound speed of 12.845 m/s. The caution is still worth carrying, but it is a **cross-method transfer** and must be tagged as one, the same way L-5 (Steffen 2008) is tagged as the MPM-specific mechanism. (ii) The paper's subject is rigid-body **migration in plane Poiseuille flow**, not a flood-stability verdict. **"Can qualitatively flip a rigid-body outcome" is a fair paraphrase of a migration result and must not be upgraded into a claim about verdicts.** `citingPublications` 3, tally 0/0/0, so it carries no Smart Citation support or contrast either way.

**CLAUDE.md CARRIES THE SAME WRONG YEAR and is NOT edited from here.** Its research-integration section reads "Artificial sound speed can qualitatively flip a rigid-body outcome, Isik and He 2022". CLAUDE.md is the shared standing-rules file, is on no session's ownership list, and a session editing it unilaterally is the 2026-08-07 breach pattern. **Recorded here as the correction of record; it needs a single named owner to apply.** Neutrally buoyant cylinder in Poiseuille flow, not a vehicle, so magnitudes do not transfer. No vehicle-flood or MPM study isolates this parameter; state that explicitly if cited.

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

**G16a. THE NUMBERS INSIDE ARTIFACT `211aad60`, AND ONE PUBLISHED MINIMUM THIS PROJECT IS BELOW AT EVERY RESOLUTION IT HAS EVER RUN. T2 for the conventions, read live here from the artifact rather than from the relay; T1 for this project's own ratios, recomputed below.** A relay reported this artifact as unopened. **It is already cited at G16** for its headline negative, so the finding is not that it was unread but that **its specific numbers were never extracted.** Three conventions exist, and G16's point stands that none is a force-convergence criterion:

1. **`dp <= D/10`** on the characteristic body dimension. Pringgana, Cunningham and Rogers 2020, *Coastal Engineering Proceedings*, DualSPHysics. Worth noting the paper **itself used `D/25`**, and the "previous convergence studies" it rests on validated impact pressure and force against experiments, never a drag, lift or moment tolerance.
2. **Roughly 10 particles per wave or flow height** for a non-breaking case, and **about 40, four times more, for a broken wave.**
3. **`H/dp >= 5`**, the DualSPHysics convention for **capturing the largest wave at all**, citing Roselli et al. 2018 and Altomare et al. 2017.

**THE THIRD IS THE ONE THAT BITES, AND IT IS SHARPER THAN L-3's CURRENT WORDING.** Recomputed here, live:

| configuration | depth / dx |
|---|---|
| canonical 17 runs at g64 (`realized_depth_m / dx`) | **2.000** exactly |
| three-class, shared-`n_grid` arm (Yaris / Rogue / Silverado) | 3.0 / 3.0 / **2.0** |
| three-class, matched-`dx` arms, both mass bases | 3.5 / 3.5 / 3.5 |

**The highest depth-per-cell this project has ever run is 3.5, and the lowest is 2.0.** Every configuration is **below the minimum-to-capture-a-wave heuristic of 5**, not merely below the 10-per-depth rule of thumb, and the relay's two configurations are actually three: the shared-`n_grid` Silverado sits at 2.0, tied with the canonical worst. **State it that way, it is more citable and more honest than the softer wording.**

**A CAVEAT FROM THE SAME SOURCE THAT CUTS THE OTHER WAY, and it must travel with the threshold.** The same DualSPHysics study that states `H/dp >= 5` also reports that **halving `dp`, to `H/dp` about 7.2, produced "no significant impact" on results** while runtime rose from 96 to 768 hours. So the threshold's own source found refinement past it changed nothing measurable. `H/dp >= 5` is a **wave-capture heuristic, explicitly not a force-convergence rule**; cite it as a convention this project sits under, never as a validated accuracy floor it has failed.

**G16b. THE BIAS DIRECTION HAS A MECHANISM AND A REAL EXCEPTION, AND L-4 MUST NOT BE WRITTEN AS A LAW. T2, same artifact.** Under-resolution **usually over-predicts** peak hydrodynamic force and pressure, by kernel truncation, boundary-particle deficiency and neglected air cushioning in single-phase models. That supports L-4, and therefore supports over-threshold NO-FORD verdicts being conservative. **The exception is documented and is not recorded anywhere in this project:** over-*fine* resolution can trigger **premature wave breaking and under-predict**. Wei and Dalrymple 2016 is the instance, where the **finest** spacing under-predicted horizontal peak force because the front broke before reaching the deck. **So the direction is problem-dependent, not a settled law.** Write L-4 as "usually, with a documented exception", never as a guarantee, because the whole conservatism argument for the published verdicts rests on it.

**G16c. TWO CONTEXT NUMBERS THAT REDUCE, RATHER THAN RAISE, THE ALARM. T2, same artifact.** Published resolutions span **roughly 2 to 60** across a load-bearing feature, so this project is **not unusually coarse by publication standards**, only against the conventions at G16a. And **MPM particles-per-cell is typically 3.5 to 16**, against this project's fixed 8, so **PPC is mid-range and is not an outlier.** The artifact independently reaches for Steffen, Kirby and Berzins 2008 on classic MPM losing convergence under refinement at fixed PPC, which corroborates the choice of anchor as G22 records, **but it is the same paper and is therefore not a second source for it.** Note also that PPC was tested as the mechanism for this scene's non-monotonicity and **refuted**, with band width dominant instead, so the general trap is real while not being what bites here.

**G17. P-2 IS NOT COMMENSURABLE ACROSS VEHICLES, AND THAT DOES NOT TOUCH THE PUBLISHED 17-RUN FAILURE LIST. Both halves measured live 2026-08-14 before anything was changed, because the instruction was not to soften a published item without a live measurement.**

**THE FINDING, from another session and correctly scoped by it:** P-2's geometric baseline, bbox plan area over free-span plan area, is **0.0905 to 0.1041** across the three vehicle classes, so the fixed **0.10** limit sits **inside its own baseline spread**. That is real, and its own word for the scope is "here", meaning across Yaris, Rogue and Silverado. **Consequence: a P-2 comparison BETWEEN vehicle classes is partly measuring hull geometry rather than water ingress, and P-2 must not be used as a cross-vehicle metric.**

**IT DOES NOT PROPAGATE TO CLAUDE.md ITEM 7, AND THE TEMPTATION TO SOFTEN THAT ITEM SHOULD BE RESISTED. Two live checks against `data/all_runs_inventory.csv`:**

1. **All 17 canonical runs share ONE hull.** `hull_m3` is **single-valued at 3.542739** across all 17 rows. Mass varies (1100/1609/2337) and particle count varies with grid (`n_vehicle` 3846 / 8905 / 29804), but the mesh does not, so **the bbox plan area is identical across the 17 and the geometric baseline is constant within the canonical set.** The cross-vehicle spread cannot arise there.
2. **The published failure list reproduces exactly, all seven.** Recomputed from `passthrough_max_frac` against the 0.10 limit: `sweepV_g64_v3p0` 0.15881, `sweepV_g64_v2p5` 0.12781, `sweepV_g64_v2p0` 0.11491, `sweepD_g64_d0p45` 0.10800, `g64_m1100` 0.10670, `sweepD_g64_d0p35` 0.10440, `g48_m1100` 0.10053. **Seven runs, and they are the same seven CLAUDE.md item 7 names.**

**CAVEAT ON THE FILE ITSELF, found on adversarial review and independently reproduced here 2026-08-14.** `data/all_runs_inventory.csv` **on disk in the main checkout is NOT byte-identical to the blob `main` holds**: on-disk sha256 begins `9c3cf047`, the git blob begins `c20ad29d`, and the difference is **line endings, CRLF on disk**. **`git status` reports the file CLEAN**, so the divergence is invisible to the normal check. **Values are identical once line endings are stripped, so nothing above moves** — I parsed with `csv.DictReader`, which is insensitive to it. **But do not treat the on-disk copy as byte-canonical, and note that a naive line-oriented tool may read it differently from a git-based one.** The file is **frozen by standing rule and was not touched.** Worth a `git diff --stat` and an `.gitattributes` check by whoever owns it.

**So item 7 STANDS, unsoftened.** Within one hull, P-2 differences are differences in water ingress, which is what the gate is for. **The correct statement of the limitation is narrow: P-2 is a within-vehicle containment check, not a between-vehicle one.**

**What is NOT settled and should not be asserted either way:** whether the P-2 bbox is taken from the mesh or from the discretised particle cloud. `solid_volume_m3` varies **3.2 percent** across the three grids (3.5218 / 3.5514 / 3.6357), so if the bbox is particle-derived it moves slightly with resolution. That is roughly a fifth of the cross-vehicle spread and does not threaten the seven-run list, but it is unmeasured. **Do not claim the within-hull baseline is exactly invariant until someone reads the bbox construction in `gates.py`.**

**G17a. AT MATCHED `dx` ALL THREE CLASSES FAIL P-2, AND REFINING TO MATCHED `dx` IS WHAT BROKE CONTAINMENT. Relayed by the visuals thread 2026-08-14 and verified here by reading `data/three_class_matched_2026-08-14.csv` on `claude/fork-three-class` directly, not from the relay.** All nine arms, `passthrough_max_frac` against the 0.10 limit:

| arm | `n_grid` | passthrough | P-2 | verdict |
|---|---|---|---|---|
| `S_yaris_n96_m1100` | 96 | 0.09695 | **PASS** | SLIDE |
| `S_rogue_n96_m1571p3` | 96 | 0.10720 | fail | SLIDE |
| `S_silverado_n96_m2270` | 96 | 0.09041 | **PASS** | SLIDE |
| `M_yaris_n111_m1100` | 111 | **0.10892** | fail | SLIDE |
| `M_rogue_n123_m1571p3` | 123 | **0.10043** | fail | SLIDE |
| `M_silverado_n154_m2270` | 154 | **0.10318** | fail | **STUCK** |
| `D_yaris_n111_m1100` | 111 | 0.10890 | fail | SLIDE |
| `D_rogue_n123_m1537p1` | 123 | 0.10073 | fail | SLIDE |
| `D_silverado_n154_m2472p2` | 154 | 0.10145 | fail | **STUCK** |

The three relayed `M_` figures reproduce exactly. **Two findings the relay did not carry.**

**(a) THE SHARED-`n_grid` ARMS ARE THE ONLY ONES THAT PASS, AND REFINEMENT DESTROYED THAT.** At shared `n_grid` 96, Yaris 0.09695 and Silverado 0.09041 both **pass**; at matched `dx` the same two vehicles fail, 0.10892 and 0.10318. **Every arm that passes P-2 anywhere in this set is a shared-`n_grid` arm, and every matched-`dx` arm fails.** So removing the resolution confound, which is the step that makes the three-class comparison physically meaningful (G20), is also the step that put every arm outside containment. **The project's strongest result is entirely containment-failed**, and that should be stated wherever it is presented, exactly as the visuals thread has now put it on the frame.

**(b) MOST OF THESE FAILURES ARE INSIDE THE GEOMETRIC BASELINE AND CANNOT BE READ AS INGRESS.** Against the 0.0905 to 0.1041 baseline band this entry records, **`M_rogue` 0.10043 and `M_silverado` 0.10318 both sit INSIDE the band**, as do `S_yaris` 0.09695, `D_rogue` 0.10073 and `D_silverado` 0.10145. Only `M_yaris` 0.10892, `D_yaris` 0.10890 and `S_rogue` 0.10720 exceed it. **A reading inside the band is not distinguishable from what the hull's own bbox geometry contributes, so for those arms P-2 is not measuring water ingress at all.** **Do not report those five as ingress failures.**

**SPLIT PROVENANCE, stated so the two halves are not quoted as equally solid.** The nine measured values above are **verified**, read from the store. The **0.0905 to 0.1041 baseline band is still only relayed**, from another session's commit body, and its construction (bbox plan area over free-span plan area) has **not** been re-derived here. **Confirm the baseline before publishing (b).** The direction of (a) does not depend on the baseline at all.

**None of this touches CLAUDE.md item 7 or the 17 canonical runs**, which are one hull at shared `n_grid` and whose seven-run failure list this entry reproduces exactly above. **Nor does it void the three-class verdicts**: those come from the classifier, not from this gate.

**G18. A THIRD QUANTITY NOW SHARES THE NUMERAL 0.3, AND G3a's TRAP IS WIDER THAN RECORDED. T2, from the moving-rigid-body review, 2026-08-14.** That review states, and it is worth quoting because it is the same warning arrived at independently: *"Still-water depth limits must not be conflated with depth-velocity products."* It reports **total-head criteria of 0.3 m for passenger cars and 0.6 m for emergency vehicles**, and separately a **simulated critical depth 0.38 m with minimum depth x velocity 0.39 m2/s**.

**So the register now tracks THREE distinct quantities that collide on two numerals:**

| numeral | as a still-water / floating limit | as a depth x velocity product | as a total-head criterion |
|---|---|---|---|
| **0.3** | AR&R small passenger, **0.30 m** | AR&R small passenger, **0.30 m2/s** | passenger cars, **0.3 m** |
| **0.6** | AR&R large 4WD, 0.60 m2/s (product) | | emergency vehicles, **0.6 m** |

**G3a already forbids a bare "AR&R 0.3". This extends it: a bare "0.3 m" is ALSO ambiguous, between a floating limit and a total-head criterion, which are different physical quantities.** Total head includes a velocity-head term and is not a still-water depth. **Name the quantity, the unit and the source, every time.** Note 0.38 m and 0.39 m2/s sit close to 0.4 and are a further collision risk against AR&R's large-passenger 0.40 m floating limit.

**G19. TWO NEGATIVE FINDINGS THAT BELONG IN LIMITATIONS AS CITABLE, NOT ASSERTED. T2, same review, 2026-08-14.** Quoted: **"no validated vehicle-fording MPM chain is identified"**, and **"The supplied records do not establish an experimental basis for the 1.5 m/s rule."**

**G19a. VEHICLE FORDING HAS BEEN SIMULATED BEFORE, FOUR TIMES, AND NONE OF IT IS CITED HERE. THIS IS THE MOST CONSEQUENTIAL CITATION FINDING OF 2026-08-14 AND IT NARROWS THE NOVELTY CLAIM. T2, from the paper CATALOGS of the two Undermind reviews, which had previously been read only to their Summary sections.**

| # | paper | method |
|---|---|---|
| A1 | **Wasfy, Wasfy and Peters 2015**, DETC2015-47142, *Coupled Multibody Dynamics and Smoothed Particle Hydrodynamics for Modeling Vehicle Water Fording*. In **BOTH** catalogs. | multibody + SPH |
| A2 | **Pazouki, Jayakumar and Negrut 2016**, *Investigation of the Vehicle Mobility in Fording* | multibody, **the Chrono authors** |
| A3 | **Khapane and Ganeshwade 2014**, SAE 2014-01-0936, *Wading Simulation - Challenges and Solutions* | **CFD**, not SPH |
| A4 | **He et al. 2026**, *Predicting Vehicle-Water Interaction in Shallow Water: Simulations and Experimental Validation*, J. Computational and Nonlinear Dynamics, DOI `10.1115/1.4071177` | with **experimental validation** |

**DOIs RESOLVED AND ABSTRACTS READ VIA SCITE 2026-08-14, so these are citable rather than merely named. Three of the four verified; one not.**

| # | verified DOI | what the abstract actually says |
|---|---|---|
| A1 Wasfy 2015 | **`10.1115/DETC2015-47142`** | SPH **integrated with multibody in one solver**, modelling **suspension, wheels, steering, axles, differential and engine**; penalty contact between tyres/body and fluid particles; **Humvee-type vehicle through a shallow water pool**. `citingPublications` 4. |
| A2 Pazouki 2016 | **NOT RESOLVED** | **UNVERIFIED.** Named in the catalog only; no DOI retrieved. Do not cite as settled until located. |
| A3 Khapane 2014 | **`10.4271/2014-01-0936`** | Title is *Wading Simulation - Challenges and Solutions*. **It is CFD, not SPH** ("a non-classical CFD approach was deemed necessary"). **Validated against a simplified rectangular block at two speeds and three immersion depths FIRST, then a full vehicle test.** |
| A4 He 2026 | **`10.1115/1.4071177`** | *J. Computational and Nonlinear Dynamics* **21(6)**, 2026-03-11, He, Matthew, Yamashita. Model-scale vehicle, **free-running experiments in a shallow water pool plus flume experiments** for hydrodynamic loads; validates physics-based **and** data-driven models. |

**TWO CORRECTIONS THE ABSTRACTS FORCE.** (i) **The four are NOT all "SPH and multibody".** A3 is **CFD**, and A4 couples multibody with CFD and a data-driven surrogate. **The correct statement of why G19's negative survives is that NONE OF THE FOUR IS MPM**, which is broader and more defensible than a claim about SPH. (ii) **A3 is a methodological precedent this project should not have missed: it validated on a simplified rectangular BLOCK before the full vehicle**, which is the same box-proxy-then-real-hull ladder this project uses. **That is prior art for the validation STRUCTURE, not just the subject.**

**AND A4 STATES THIS PROJECT'S OWN GAP IN PUBLISHED FORM**, which is worth more than an internal assertion: *"only limited studies have been conducted regarding the validation of the models in real physical settings. There are few or no experimental data available to characterize hydrodynamic loads for the evaluation of transient vehicle responses in shallow water."* **Cite A4 for the gap rather than asserting it.**

**"NOBODY HAS SIMULATED VEHICLE FORDING" IS FALSE AND MUST NEVER BE WRITTEN.** G19's quoted negative survives **only as written**, because **none of A1 to A4 is MPM** (see the correction above; they are SPH-multibody, multibody, CFD, and multibody-CFD respectively). **The defensible novelty claim is therefore narrower than anything this project has stated: not the first vehicle-fording simulation, but the first pairing MPM with validation.** A1 to A4 must appear as related work or a reviewer will find them.

**AND A2 BEARS ON THE ARCHITECTURE DECISION, NOT JUST THE BIBLIOGRAPHY.** Pazouki and Negrut are already in this project's standing notes (CLAUDE.md addendum A-1) as the citation for real two-way rigid coupling requiring accumulated contact force. **The same authors published on fording, and the Chrono go/no-go recorded at F6f was conducted without reading it.** Whatever F6f's x86 reproduction returns, **A2 should be read before Chrono is accepted or rejected as the host for a realistic environment.**

**G19b. MPM ON A REAL ROAD SURFACE ALREADY EXISTS, SO THIS PROJECT'S BLOCKERS ARE IMPLEMENTATION BLOCKERS, NOT METHOD BLOCKERS. T2, same catalogs.** **Zhou et al. 2025**, *Analysis of tire-pavement viscous hydroplaning based on the material point method*, *Physics of Fluids*, DOI `10.1063/5.0276643` — **MPM, a tyre, a pavement and a water film**, which is a realistic road environment in MPM with a contact patch. And **Chen et al. 2022**, DETC2022-89632, *Modeling Large Deformable Terrain With Material Point Method for Off-Road Mobility Simulation* — **MPM terrain under a vehicle.**

**Together these refute the framing that MPM cannot host a realistic road.** **F6 is corrected accordingly: F6a to F6d describe OUR implementation, not a limit of the method.** F6e's literature negative still stands as written, because it is specifically about **following a vehicle with a refinement window through a large flood domain**, which is narrower than "MPM on a road".

**G19c. THE 0.3 PERCENT BENCHMARK NOW HAS A NAME AND IS DOWNLOADABLE.** G19 said it could not be cited until identified. It is **Kramer et al. 2021**, *Highly Accurate Experimental Heave Decay Tests with a Floating Sphere: A Public Benchmark Dataset for Model Validation of Fluid-Structure Interaction*, *Energies* **14(2):269**, DOI `10.3390/en14020269`. A **public, downloadable dataset**: floating sphere, heave decay. **This is the locked regression case the deployment order's Phase 1 asks for, and it does not have to be built.**

**DO NOT MERGE IT WITH THE OTHER KRAMER.** This register already cites **Kramer, Terheiden and Wieprecht 2016** (DOI `10.1016/J.IJDRR.2016.04.003`) for the watertightness prototype finding. **Same lead author, different paper, different subject, different decade of relevance.** Citing "Kramer" without a year in this project is now ambiguous.

**Both are negative findings and must be handled as G8 requires**: the absence is in the searched corpus, not in the world. **State the scope of the search whenever either is written down.** They are nonetheless the strongest available framing for this project's novelty claim and for the velocity cap, and they agree with the standing project note that the 3.0 m/s cap is administrative rather than vehicle-derived. **Neither has been checked against a primary record here; both are UNREVIEWED at T2.** The same review reports a public benchmark at approximately **0.3 percent experimental uncertainty** as a locked free-surface regression case; **it is not yet identified by name in this register and cannot be cited until it is.**

**G19d. THREE CITATIONS CONFIRMED FROM A THIRD INDEPENDENT SOURCE, AND ONE RE-DATING REFUTED AGAIN. T2, from the same catalogs.**

**(i) `mu` = 0.55 is Azhar, Pauwels and Bui 2023**, *Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements*, DOI `10.1111/jfr3.12885`. This is a **third** independent confirmation of the provenance chain at G4a, after the artifact and the moving-validation thread's direct read. **Note it is an SPH paper**, which is worth carrying in G4e's inventory: the canonical `floor_friction` traces to a measurement reported in an **SPH** study, applied in an **MPM** solver, on top of the lab-rubber-mat caveat already recorded.

**(ii) Bonham and Hattersley 1967 is titled *Low Level Causeways*.** Already at G4d in that form; the catalog independently confirms both the title and that the 0.3 is their assumption carried forward.

**(iii) SHAH IS 2020, AND THE RE-DATING TO 2021 IS REFUTED FOR THE THIRD TIME.** The catalog gives **Shah, Mustaffa, Martinez-Gomariz and Yusof 2020**, DOI `10.1111/jfr3.12657`, matching a Crossref date of **2020-07-28**. An instruction circulated earlier today to "correct Shah, Mustaffa and Martinez-Gomariz from 2019 to **2021**". **That instruction was wrong; 2021 must not be applied.** `[live]` this register does not currently cite Shah with a year outside Section I's list of claims to delete, so nothing here needs changing — **but if the 2021 re-dating was applied anywhere else in the project, it needs reverting to 2020.** Note also there are at least two distinct Shah papers in play (a 2018 moving-vehicle force balance is referenced in project notes), so **a bare "Shah" is ambiguous and must carry its year and DOI.**

**G19e. THE RANKED ROUTE TO A LARGE DOMAIN, WITH CITATIONS, NONE OF WHICH THIS PROJECT HAS EVER CITED. T2, from the multi-resolution catalog. Recorded so the next attempt starts from the literature rather than from scratch.**

1. **Hybrid 3D near-vehicle plus 2D far-field**, the only approach that makes a road-scale domain affordable without refining everywhere: Pan et al. 2023 (`10.1002/fld.5233`), Zheng et al. 2023 (`10.1016/j.compgeo.2023.105673`), Suchde 2024 (`10.1016/j.cma.2024.117199`), Fois, de Falco and Formaggia 2024 (`10.1016/j.cnsns.2024.108202`).
2. **Sparse and octree grids, for EXTENT ONLY**: Qiu et al. 2022 (`10.1145/3570160`), Zhao et al. 2026 (arXiv 2605.28525), Bird, Coombs, Augarde and O'Hare 2026. **The review is explicit that these do NOT reduce the smallest-cell timestep and do NOT resolve the floor layer** (F6e), so they buy domain size and nothing else.
3. **Moving refinement window**, the thing the review says nobody has done: Luo, Li and Jiang 2026 (arXiv 2605.09097, space-time refinement, the closest published machinery), Huang et al. 2021 (`10.1145/3478513.3480495`, a moving body in an effectively unbounded free-surface domain, graphics and unvalidated but the right shape), Gao, Tampubolon, Jiang and Sifakis 2017 (`10.1145/3130800.3130879`, adaptive GIMP).
4. **The open boundary already chosen**, confirmed present in the catalog: Zhao et al. 2019 (`10.1016/J.COMPFLUID.2018.10.007`), F6d.
5. **The PPC trap**, catalogued and called decisive for AMR: Steffen, Wallstedt, Guilkey, Kirby and Berzins 2008 (`10.3970/CMES.2008.031.107`). **We tested it and refuted it for this scene (G4f), finding band width dominant instead (B9). That is a result the catalog does not contain**, and it is the one place tonight's work is ahead of the commissioned literature rather than behind it.

**G20. THE VEHICLE-CLASS GEOMETRY GAP IS CLOSED, AND NOBODY HAS CONNECTED THE RESULT TO THE GAP. T2 for the framing, T1 for the closure. 2026-08-14.** The 2026-08-08 deployment order records that all 17 gated runs represent three AR&R mass classes (1100 / 1609 / 2337 kg) **using one hull, the Yaris, with mass relabelled only**, while buoyancy, drag and lift lever arms, wheel normal loads and sliding/float/roll thresholds *"depend jointly on displaced volume, underbody shape, wheelbase and track, and center of mass, not on mass alone"*. This is the same gap CLAUDE.md addendum A-3 records. It offered Path A, run real Rogue and Silverado hulls, or Path B, an explicit limitations sentence.

**Path A has been executed.** The three-class matched-`dx` set uses the real Rogue and Silverado hulls at a common `dx`, and Section J item 15a records its `(dx, mu)` square. **The register's own confirmation that this is not a mass relabel: `hull_m3` is single-valued at 3.542739 across all 17 canonical runs (G17), which is precisely the one-hull limitation, and the three-class set is the thing that lifts it.** **Whoever writes the limitations section should state the gap and its closure in the same paragraph**, rather than shipping the A-3 limitation sentence as though Path A had not been done.

**G21. SAE 2003-01-0966 AND SAE 1999-01-1336 ARE DISTINCT PAPERS AND ARE NOT INDEPENDENT SOURCES. Verified via Scite 2026-08-14, both records retrieved, no editorial notices on either.**

| | SAE 1999-01-1336 | SAE 2003-01-0966 |
|---|---|---|
| title | *Measured Vehicle Inertial Parameters, NHTSA's Data Through November 1998* | *Estimation of Passenger Vehicle Inertial Properties and Their Effect on Stability and Handling* |
| authors | Heydinger, Bixel, Garrott | Allen, Klyde, Rosenthal | 
| date | 1999-03-01 | 2003-03-03 |
| kind | **measured database**, 496 entries | **regression equations** |

**Distinct, as required before either is cited. But the more useful answer is that they are NOT independent.** `[live]` Scite's citation records show **2003-01-0966 cites 1999-01-1336**, and its own abstract states it *"will present an analysis of the NHTSA Inertia Database and give regression equations that approximate moments of inertia and center of gravity height given basic vehicle properties"*. **The 2003 regressions are fitted TO the 1999 measured database.** So citing both as mutual support is item 43's error in the literature: **a derived model plus the data it was fitted to is one source, not two.**

**AND ITS USE HERE IS BARRED ON OTHER GROUNDS, which the deployment order does not know.** CLAUDE.md item 4 establishes that inertia and CG must NOT be wired into this solver: the tabulated tensor is a box fallback, its axes are transposed against the gated scene, and the solver already computes a better tensor from the real hull particle cloud. **So 2003-01-0966 is a legitimate provisional estimator for a quantity this project has decided on measured grounds not to use.** Cite it, if at all, as prior art for class-based estimation, never as a source for a value to wire in.

**G22. CITATIONS FOR LIMITATIONS ALREADY KNOWN TO BE TRUE. T2, 2026-08-14, NONE YET CHECKED AGAINST A PRIMARY RECORD, so all are UNREVIEWED at this tier.** Roache 1994 (Grid Convergence Index) and Celik, Ghia, Roache and Freitas 2007 are the anchors for **how a resolution study should be reported**; this project reports verdict-invariance rather than a formal GCI number, and `params_check`'s `lit:resolution_convergence_gci` gate already records that an apparent order cannot be computed because the study is non-monotone (B2). **State that gap with those citations rather than leaving it implicit.** Bai and Schroeder 2022 and Sun, Shinar and Schroeder 2020 derive the sound-speed-to-CFL relationship formally and are the anchor for the sound-speed result and for the `lit:sound_speed_cfl` warning at B8. **Steffen, Kirby and Berzins remains the correct anchor for grid-crossing error** and is already this project's citation at L-5 and in item 44; it is reported as the most-cited MPM numerics paper across the four reviews, which corroborates the choice but is not itself a verification.

**G23. R7, THE MIRROR-SYMMETRY CONTROL. THE HEADLINE WAS RETRACTED BY ITS OWN AUTHOR WITHIN THE HOUR, AND SEPARATELY, THE SCENE IT RUNS ON IS NOT SYMMETRIC. Three sessions produced three different sets of numbers from one script, 2026-08-14/15.** The design is a metamorphic control: build a scene exactly symmetric about `y`, run it, mirror it, and any `y`-asymmetry beyond the run-to-run floor is a solver defect. Two byte-identical runs give the floor, the mirrored run gives the asymmetry. Script `r7_mirror.py`, logs `r7_vista.log`, `r7_g64.log`, `r7_g96.log`, on Vista `$SCRATCH`, env `R7_NGRID` and `R7_FRAMES`.

**G23a. THE RETRACTION, AND WHAT SPECIFICALLY DIED. T2, relayed by the coordinator who both ran the original and withdrew it, after the moving-driver session tested it rather than adopting it (commit `278ea81`, `claude/fork-moving-driver`).** The original relay reported, as `n_grid` then floor then mirror asymmetry then ratio, all max abs particle displacement in metres: **48 -> 0.0020821 / 0.1318053 / 63.3x; 64 -> 0.0067501 / 0.0066214 / 0.98x; 96 -> 0.0011301 / 0.0112944 / 10.0x**, and drew from it a **third independent instance of non-monotonicity** and a **second tunable-pass** (a control passing at g64 while both neighbours fail). **Both conclusions are withdrawn.** The mirror asymmetry itself reproduces across sessions at two of three points, 0.1318053 against 0.1317959 at g48 (0.007 percent) and 1.02x at g96, **but the determinism floor does not reproduce at all**: 0.0020821 against 0.0043464 at g48, a factor of 2.1, and 2.0x at g64 and 1.4x at g96. The floor is a measure of run-to-run variation and is therefore itself a random variable, so **the 63.3x ratio is not reproducible: 30.3x for the identical configuration.** The two sessions disagree **1.93x at g64**, which is the single cell the entire non-monotonicity claim rested on: 0.1318 / 0.0128 / 0.0111 is **monotone decreasing**. **Report a range over repeats, never a single ratio divided by a floor.**

**G23b. THE CAUSE OF THE RETRACTION IS SHORT INTEGRATION, AND THAT IS NOW THE NIGHT'S DOMINANT FAILURE MODE.** `R7_FRAMES` defaults to **20**, and this stack rings with a roughly **100-frame period**, so the measurement sat inside the initial transient. At longer integration the control passes and the solver looks healthy: **0.2616 / 0.0675 / 0.0319 at 100 frames** and **0.1704 / 0.0615 / 0.0234 at 200**, monotone decreasing both times, with g64 at 1.02 and g96 at 1.53 against the floor. **The determinism floor itself grows strongly with integration length**, at g96 by 19x between 20 and 100 frames, so **ratios taken at different frame counts are not comparable quantities.** Consistent with B2, and the same defect the settling protocol at G22 and R3 warn about.

**G23c. THE SCENE IS NOT SYMMETRIC BY CONSTRUCTION. T1, MEASURED HERE 2026-08-15 AT t=0 WITH NO PHYSICS RUNNING, AND PREDICTED FROM LATTICE ARITHMETIC ALONE TO 6-7 SIGNIFICANT FIGURES. This is independent of the retraction above and survives it.** `r7_mirror.py`'s docstring asserts the scene is *"built EXACTLY symmetric about the plane y = lim/2, by construction"* and that therefore *"Any y-asymmetry in the OUTPUT is a solver defect, with no interpretation needed."* **The premise is false.** The body lattice is `gy = np.arange(cy - by/2, cy + by/2 + 1e-9, h)` with `by = 4.2014` and `h = dx/2`, and **`by/h` is not an integer at any of the three resolutions**: 42.809, 57.079, 85.618. `arange` therefore truncates the `+y` end and the body sits low by exactly `h*frac(by/h)/2`:

| `n_grid` | `by/h` | predicted offset, m | measured at t=0, m | rel. err |
|---|---|---|---|---|
| 48 | 42.80890 | -0.03969387 | **-0.03969386** | 2.7e-07 |
| 64 | 57.07853 | -0.00289019 | **-0.00289020** | 3.9e-06 |
| 96 | 85.61779 | -0.01515808 | **-0.01515808** | 8.0e-08 |

The relayed body `y`-centroid offsets, **-0.0399 / -0.0030 / -0.0145**, are this artifact, not a solver result. Two consequences. **(a)** Mirroring moves the body by twice the offset relative to a fixed grid, a sub-cell phase shift of **0.4044 / 0.0393 / 0.3089 cells**, which does not vanish under refinement because it is `frac(by/h)/2`. **(b)** `frac()` has no reason to be monotone in `n_grid`, so **the retracted non-monotonicity had a purely arithmetic candidate cause available the whole time.** The line `B[:, 1] = cy + (B[:, 1] - cy)`, commented *"force exact y-symmetry of the body about cy"*, is an identity map and symmetrises nothing.

**G23d. THAT DEFECT IS REAL BUT IS NOT WHAT DRIVES THE SIGNAL. MY OWN HYPOTHESIS, REFUTED BY MY OWN CONTROL, RUN ON THE GH200 2026-08-15.** `r7_mirror_sym.py` changes one thing, building the `y` lattices exactly symmetric about `cy` (`n = round(extent/h)`, points at `cy + (k - n/2)*h`, so `k` and `n-k` are exact reflections), and leaves every parameter, the step protocol and the three arms byte-identical. It drives the t=0 offset from -0.0397 m to **3e-09 m**, the summation-error floor of the measurement. **It does not remove the mirror discrepancy.** At g48, where the signal is largest and cleanest, **five measurements from three sessions across BOTH scenes agree to 0.12 percent**: 0.13180530 and 0.13179590 on the original asymmetric lattice, against 0.13165104, 0.13164341 and 0.13165140 on the symmetrised one. Symmetrising shifts g48 by about **-0.11 percent** and changes nothing else about it. At g64 and g96 the repeat-to-repeat spread (G23g) is **1.4x to 2.0x**, which swamps any scene difference, so **no effect of symmetrising is resolvable there at all.** **The lattice truncation is a genuine defect in the control and is not the mechanism behind the measured asymmetry.** Record both facts; do not let the first be cited as an explanation of the second. Caveat on the comparison: at g48 and g96 the symmetric lattice carries one extra `y`-plane of body particles (12384 -> 12672 and 93310 -> 94395), so only **g64 is particle-count-identical** and strictly controlled.

**G23e. AT CONVERGED INTEGRATION THE MONOTONE-DECREASING RESULT REPRODUCES ON A GENUINELY SYMMETRIC SCENE. T1, run here at 200 frames.** This is the test that matters, because a symmetry control on an asymmetric scene cannot, in principle, confirm convergence toward a symmetric exact solution, so the positive conclusion at G23b was open to exactly that objection. It survives:

| scene, 200 frames | g48 | g64 | g96 | shape |
|---|---|---|---|---|
| original, asymmetric lattice, single run | 0.1704 | 0.0615 | 0.0234 | monotone decreasing |
| **symmetrised lattice, T1 here, 2 repeats** | **0.16735 - 0.16906** | **0.04189 - 0.04756** | **0.01163 - 0.01558** | **monotone decreasing** |

**The three repeat ranges do not overlap**, so on the symmetrised scene the monotone-decreasing ordering is robust to the repeat spread rather than resting on one draw. **The geometry defect at G23c therefore does not overturn the converged conclusion**, and that conclusion now stands on a scene whose exact solution really is `y`-symmetric. **Quote the asymmetry, never the ratio**: the same two repeats give ratios of 5.66-17.88, 0.84-3.79 and 0.58-0.80, because the floors underneath them span 3.19x and 3.99x at g48 and g64 (G23g).

**G23f. NUMERAL AND NAME COLLISIONS INSIDE THIS ONE ITEM. Two traps, both live.** First, **63.3 denotes two unrelated quantities**: the retracted R7 ratio at g48 (dimensionless, asymmetry over floor) and the Yaris at-rest gate error (a percentage). The relay cited the two as sharing a shape; **they share a numeral, in different units, and one of the two is now withdrawn.** This is G3a and G18's hazard in a new place: name the quantity and its unit every time. *A draft of this item claimed a third instance, "the percentage by which symmetrising changed the g64 asymmetry". That was 63.3 in one run and 123 in the next, so it was noise dressed as a coincidence; it is withdrawn, and its withdrawal is the same repeat-count lesson as G23g.* Second, **the session names `D5`, `D9`, `D11`, `D12` and `D13` collide with register item IDs in section D**, and two of them are live items about entirely different subjects: D5 is "no gate is a physics validation" and D9 is the two-slide-flips reconciliation. `register_integrity.py` only counts a token as a cross-reference when a cue word precedes it, which is what keeps this from producing false references today, so **never write a cue word (`per`, `see`, `item`, `recorded at`, `refuted,`) immediately before a session name.**

**G23g. THE RATIO IS NOT A STATISTIC, AND THE TWO SESSIONS' DISAGREEMENT AT g64 IS FULLY EXPLAINED BY THE REPEAT SPREAD. T1, measured here 2026-08-15, every cell repeated. Artifact `docs/R7_MIRROR_SYM_RESULTS_2026-08-15.json`, machine-written by shell redirect from the solver's own stdout, script `simulation/r7_mirror_sym.py` committed alongside at md5 `0447514add6c2750960680125c5815a5`, byte-identical to the copy that ran on the GH200.** Repeating each configuration, which nobody had done, separates a reproducible quantity from an irreproducible one:

| frames | `n_grid` | reps | mirror asymmetry, m | spread | determinism floor, m | spread | ratio range |
|---|---|---|---|---|---|---|---|
| 20 | 48 | 3 | 0.1316434 - 0.1316514 | **1.00x** | 0.0010254 - 0.0023537 | 2.30x | 55.93 - 128.38 |
| 20 | 64 | 3 | 0.0147419 - 0.0211079 | 1.43x | 0.0068326 - 0.0094974 | 1.39x | 1.56 - 2.36 |
| 20 | 96 | 3 | 0.0085697 - 0.0171056 | 2.00x | 0.0029974 - 0.0088058 | 2.94x | 1.19 - 2.86 |
| 200 | 48 | 2 | 0.1673453 - 0.1690551 | **1.01x** | 0.0093603 - 0.0298767 | 3.19x | 5.66 - 17.88 |
| 200 | 64 | 2 | 0.0418878 - 0.0475626 | 1.14x | 0.0125546 - 0.0501080 | 3.99x | **0.84 - 3.79** |
| 200 | 96 | 2 | 0.0116271 - 0.0155811 | 1.34x | 0.0195794 - 0.0200553 | 1.02x | 0.58 - 0.80 |

Four conclusions. **(a) The mirror asymmetry is a well-behaved quantity** and at g48 is reproducible to 1.00x within a session and 0.12 percent across three sessions and two scenes. **(b) The determinism floor is not reproducible anywhere**, spanning 1.4x to 4.0x, which matches the 2.1x/2.0x/1.4x disagreement between the other two sessions at G23a. **(c) Therefore the ratio is not a statistic and must not be reported as one.** At g64 and 200 frames it runs **0.84 to 3.79, straddling the pass threshold of 1.0**, so the *verdict itself* flips between two runs of one script on one node with one configuration. An earlier 20-frame run here, not archived, gave a g48 floor of 0.0030851 m, widening that cell to 3.0x. **(d) The g64 disagreement that broke the original claim is explained**, not merely withdrawn: at 20 frames the g64 and g96 asymmetry ranges **overlap** (0.01474-0.02111 against 0.00857-0.01711), so the ordering of those two cells is not resolvable from one draw, and the two sessions reported opposite orderings at exactly that pair. **Neither session mismeasured. Both over-interpreted a single sample.**

**The operating rule: report the asymmetry with a repeat range, never a single run, and never a ratio against a floor that is itself a random variable.** Note how this was caught: the repeats were run only to avoid hand-transcribing numbers into this register after B9's provenance failure, and the second run immediately contradicted the first. **The provenance discipline found the statistical error.**

**G23h. SCRIPT PROVENANCE BY sha256, AND THERE ARE TWO SCRIPTS IN PLAY, NOT THREE. T1, hashed live 2026-08-15 on both machines.** Raised as a three-way fork risk, since `r7_mirror.py` is on nobody's ownership list. **Hashing refutes the fork:**

| sha256 | bytes | locations | produced |
|---|---|---|---|
| `5a48aa9a88565d15bdeba3114cb7a8cc568b3c2b2d3753acf865eec3440a59fd` | 5777 | LS6 `$SCRATCH/d11_r7_2026-08-14/r7_mirror.py` (15:55) **and** Vista `$SCRATCH/r7_mirror.py` | the withdrawn 20-frame ladder, the frame sweep at G23b, the four-rung ladder below |
| `a2277f74b9149a7545a7508fd7eb13cbf1828bb25b1837995ca73f41823dbb27` | 6471 | `simulation/r7_mirror_sym.py`, committed here, **and** Vista `$SCRATCH/r7_mirror_sym.py` | every row of `docs/R7_MIRROR_SYM_RESULTS_2026-08-15.json` |

**The LS6 original and the Vista copy are byte-identical**, so the duplication is of location, not of content, and every number attributed to `r7_mirror.py` is attributable to one body of code regardless of which machine ran it. Only the symmetrised variant differs, deliberately and in one function. **Two scripts, one fork of intent, no accidental fork.** The results file carries none of the withdrawn numbers, checked by value.

**G23i. THE FOUR-RUNG 200-FRAME LADDER, AND TWO CORRECTIONS TO IT. T2 for the ladder, relayed 2026-08-15; T1 for the corrections, measured here.** The ladder reports, on the original lattice at 200 frames, mirror asymmetry **0.1701 / 0.0490 / 0.0244 m** at g48/g64/g96 with g128 still integrating, **monotone decreasing**; determinism floor **0.0139 / 0.0737 / 0.0293 m**, **non-monotone and largest at g64**; ratios **0.67 at g64 and 0.83 at g96**, read as the control passing. **The monotone decrease agrees with this session's symmetrised repeats and with the frame sweep, so that conclusion now rests on three parties and two scenes.** The accompanying judgement, that **no convergence order can be extracted from data sitting inside the noise**, is correct and should be kept. Two corrections:

**(a) The body `y`-centroid offset is NOT a convergence result and must not be reported as one.** The ladder reports it "falls from about 0.040 m at g48 to 0.001 to 0.005 m at g64". Those are the two values G23c predicts from `np.arange` truncation alone, -0.03969 and -0.00289, with no physics involved, and **the sequence does not continue downward: at g96 it rises again to -0.01516**, so quoting only g48 and g64 stops at exactly the point where the artifact is smallest. On a symmetrised lattice the offset is **3e-09 m at all three resolutions**. It measures the lattice, not the solver.

**(b) "The control passes at g64" does not reproduce here.** Two 200-frame repeats of the symmetrised scene give g64 ratios of **0.84 and 3.79**, straddling the threshold, against the ladder's single 0.67. The g96 reading is the one that holds up, 0.58-0.80 here against 0.83 there. **This is G23g's point arriving from a second direction: a pass/fail verdict divided by a floor that swings 4.0x between repeats is not a verdict.** Report g96 as passing, and report g64 as unresolved pending repeats.

**One resolvable scene difference, stated cautiously.** At g96 and 200 frames the symmetrised scene gives **0.01163-0.01558 m** against **0.0244 and 0.0234 m** on the original, roughly half, with both repeats below both original-scene values. That is the only cell where symmetrising produced a difference larger than the repeat spread, and it rests on two repeats against one apiece, so treat it as a lead rather than a result.

**G23j. THE CONTROL BREAKS BETWEEN g96 AND g112 AND THE BREAK REPRODUCES, AT A 200-FRAME SETTLE THROUGHOUT SO IT IS NOT THE TRANSIENT ARTIFACT. T2 for the ladder, relayed 2026-08-15; T1 for the geometry column and the held-fixed comparison, computed here.**

| `n_grid` | mirror asymmetry, m | determinism floor, m | ratio | body offset, m | grid-phase shift, cells |
|---|---|---|---|---|---|
| 48 | 0.1701 | 0.0139 | 12.24 | -0.039694 | 0.4044 |
| 64 | 0.0490 | 0.0737 | 0.66 | **-0.002890** | 0.0393 |
| 96 | 0.0244 | 0.0293 | 0.83 | -0.015158 | 0.3089 |
| 112 | **1.6744** | 0.2880 | 5.81 | -0.018663 | **0.4437** |
| 128 | **2.0252** | 1.6936 | 1.20 | **-0.002890** | 0.0785 |

**The asymmetry falls cleanly through g96 then jumps 68.6x.** The blow-up is **a reproducible property of the configuration, not a bad draw**: g128 was run three independent times and the mirror asymmetry agrees to **0.14 percent**, 2.0252 / 2.0280 / 2.0272. **The determinism floor again does not reproduce**, 1.6936 / 0.5220 / 1.4515, a 3.2x spread, so **run-to-run variation at g128 in this scene is metre-scale, larger than the vehicle itself.** This is G23g's separation holding at a fifth and sixth rung: the asymmetry is a real quantity, the floor is not, and only the asymmetry may be quoted.

**THE GEOMETRY DEFECT AT G23c IS NOT THE MECHANISM HERE EITHER, AND THE LADDER NOW PROVES IT WITHOUT NEEDING A RUN.** The last two columns are computed here from lattice arithmetic. **g64 and g128 have IDENTICAL body offsets, -0.002890 m**, which is exact rather than coincidental: `by/h` doubles precisely when `h` halves, so `h*frac(by/h)/2` returns the same value. Their grid-phase shifts, 0.0393 and 0.0785 cells, are the **two smallest on the ladder**. **Yet their asymmetries differ by 41x, 0.0490 against 2.0252.** And g112, which carries the **largest** phase shift of any rung at 0.4437 cells, sits between them rather than at an extreme. **The blow-up does not track the geometry in level, in ordering, or at the break point.** G23d reached this by direct control at g48-g96; the ladder extends it to g112 and g128 by arithmetic alone.

**AND THE CONTROL WAS THEN RUN RATHER THAN LEFT AS AN INFERENCE. T1, GH200, 200 frames, symmetrised lattice.** The blow-up **reproduces on a genuinely symmetric scene**: **g112 gives 1.635163 m against the original's 1.6744, and g128 gives 2.032827 m against 2.0252**, that is **0.98x and 1.00x**, while the t=0 body offset is driven to 1.4e-09 and -3.6e-09 m. **Removing the geometry defect entirely leaves the metre-scale symmetry violation exactly where it was.** The lattice truncation at G23c is therefore excluded as the mechanism by measurement at every rung of the ladder, not only by argument. Note also that at g128 the symmetrised floor is **2.054779 m against a 2.032827 m asymmetry, a ratio of 0.99**, so the control "passes" there only because its own noise has grown past the signal, which is the precise sense in which the ladder carries no information above the break.

**SCOPE, AND IT IS NARROW.** This establishes that **in the R7 symmetric test domain**, the solver develops a reproducible metre-scale symmetry violation somewhere between g96 and g112, and that above that point **the control carries no information because its own floor is metre-scale**. The canonical scene has a different domain and a different `grid_lim`, so **this does NOT establish that the canonical g128 runs are broken**, and it must not be read as such.

**WHAT IT DOES LICENSE IS A REQUIREMENT.** Any result quoted at **g128 or finer, in any scene**, must now be reported **with a repeat-run determinism floor beside it**, because at this resolution in this scene two byte-identical runs differ by more than a car length. That covers Section J item 15's Silverado flip at g128, the `rs_*` STUCK at g128 recorded at D7d, item 44's canonical g128 mass sweep, and any matched-`dx` arm finer than g128. **The check is two identical runs and a reported spread, about 130 seconds each.** Note that the machinery half-exists and is already distrusted: `data/three_class_matched_2026-08-14.csv` carries a column literally named **`determinism_identical_FLAG_DO_NOT_TRUST`**, reading `True` on every row. **A boolean that someone has already labelled untrustworthy is not a substitute for a reported spread.**

**G23k. THE g112 BREAK IS A GROWING INSTABILITY, NOT A SETUP ERROR AND NOT A TRANSIENT, AND THE ARGUMENT THAT DISTINGUISHES THEM IS THE VALUABLE PART. T2 for the ladder, relayed 2026-08-15; T1 for the checks, computed here from its numbers.** Frame ladder at `n_grid` 112:

| frames | mirror asymmetry, m | determinism floor, m | ratio | floor growth per frame-doubling |
|---|---|---|---|---|
| 20 | 0.3608 | 0.00568 | **63.52** | |
| 50 | 1.0911 | 0.02012 | 54.23 | 2.60x |
| 100 | 1.9262 | 0.09369 | 20.56 | 4.66x |
| 200 | 1.6744 | 0.28795 | 5.81 | 3.07x |

**The asymmetry GROWS with integration time and saturates near 2 m, which is domain scale.** The reasoning that makes this diagnostic rather than descriptive is worth keeping verbatim: **a setup error would be constant, and a transient would decay.** Growth followed by saturation at domain scale is neither, so this is a genuine instability. **That also retires, for this rung, the settle-length explanation that correctly killed three other results tonight** at G23b and G24a: here a longer settle makes it worse, not better.

**Two checks run here on the relayed numbers rather than passing them through.** **(a) The apparent fall from 1.9262 at f100 to 1.6744 at f200 is NOT a turnover and must not be read as one.** The change is **-0.2518 m against an f200 determinism floor of 0.28795 m**, so it sits inside the noise and is unresolvable from single runs. **Saturation is the right reading; the dip is not a feature.** **(b) "Roughly 4x per doubling" is the middle step only.** Computed per frame-doubling, and correcting for the f20 to f50 step being 2.5x rather than 2x, the growth is **2.60x, 4.66x and 3.07x**. **All three exceed 2x, so "faster than linear" is confirmed**, but quote the range rather than the single figure.

**THE TRAP THIS EXPLAINS.** At f20 the g112 asymmetry is only 0.36 m, which looks unremarkable in absolute terms, **yet its ratio is already 63.52.** So **the break exists from the start and has merely not grown yet**, and a short run at fine resolution reads as acceptable while already being broken. **A small absolute asymmetry at a fine grid is not evidence of health.** Caution on the numeral: **"63x" is now ambiguous** between this g112 f20 ratio of 63.52 and the withdrawn g48 f20 ratio of 63.3 at G23a, which are the same kind of quantity at different rungs. Always name the rung and the frame count.

**THE TRANSITION IS SHARP.** At f200, mirror asymmetry across the ladder is **0.1701 / 0.0490 / 0.0244 / 1.6744 / 2.0252** at g48 / g64 / g96 / g112 / g128. Below the break the control converges cleanly and passes below its own floor at g64 and g96; above it the solver develops a **metre-scale, reproducible, time-growing violation of a symmetry the scene possesses by construction.** g128 reproduces to 0.14 percent across three runs, so it is a property of the configuration, while the **floor** at g128 spans **0.52 to 1.69 m** across those same three runs, so run-to-run variation there exceeds a car length.

**THE OPERATIONAL RULE, STRENGTHENED FROM G23j IN TWO WAYS.** It now begins at **g112, not g128**, and it now requires **a frame count as well as a repeat-run determinism floor**, because both matter and **both were invisible in every published number so far.** Any result quoted at g112 or finer, in any scene, must carry both. **Scope is unchanged and narrow:** this is the R7 symmetric test domain, the canonical scene has a different `grid_lim`, and this does **not** by itself establish that canonical g128 is broken. What it does establish is that **this solver has a resolution ceiling in at least one scene, that the ceiling sits between g96 and g112, and that above it a control which should converge instead diverges with time.**

**G23l. THE CEILING IS BISECTED, AND THE SCOPE CAVEAT IS WRONG IN THE DANGEROUS DIRECTION: THE R7 SCENE SHARES THE CANONICAL YARIS GRID EXACTLY. T2 for the ladder, relayed 2026-08-15 at a 200-frame settle throughout; T1 for the `dx` column, the grid identity and the three corrections, all computed or read live here.**

| `n_grid` | `dx`, m | depth/`dx` | mirror asymmetry, m | floor, m | ratio |
|---|---|---|---|---|---|
| 96 | 0.0981431 | **3.000** | 0.0244 | 0.0293 | 0.83, passes |
| 100 | 0.0942174 | 3.125 | 0.1895 | 0.2686 | 0.71, **one run only** |
| 104 | 0.0905937 | **3.250** | 1.5810 / 1.6027 | 0.3774 / 0.1697 | **4.19 and 9.44** |
| 112 | 0.0841227 | 3.500 | 1.6744 | 0.2880 | 5.81 |
| 128 | 0.0736074 | 4.000 | 2.0252 | 1.6936 | 1.20 |

**Correction 1, "roughly 8x the floor" at g104 picks the high run.** The two runs give **4.19 and 9.44**, a 2.25x spread driven **entirely by the floor**, which differs 2.22x between them, while the **asymmetry agrees to 1.37 percent.** The repeats were run, correctly, and then a single ratio was quoted from them anyway. G23g's rule applies unchanged: **quote the asymmetry, 1.5810 and 1.6027, and give the ratio as a range.**

**Correction 2, the degradation begins one rung EARLIER than the ratio test fires, and the g100 pass is not established.** From g96 to g100 the mirror asymmetry jumps **7.77x** and the floor jumps **9.17x**, nearly in lockstep, so the ratio barely moves, 0.83 to 0.71, and reports a pass **while run-to-run variation goes from 3 cm to 27 cm.** **A ratio cannot detect an instability that inflates its numerator and denominator together, because the reference is contaminated by the very thing being tested for.** And g100's floor is **a single unrepeated draw**: applying the 2.22x floor spread measured one rung up gives a g100 ratio of **1.57, a fail.** **So the honest bracket is g96 to g104, and g100 is UNRESOLVED pending a repeat**, not a passing rung.

**Correction 3, and it is the one that matters. The caveat "grid_lim differs between them, so do not translate by grid number" is FALSE for the Yaris.** `r7_mirror.py` sets `lim = 9.421742313727737` commented *"canonical Yaris grid_lim"* and `DEPTH = 0.2944294473039918` commented *"canonical realized depth"*. Both are **bit-identical** to the canonical Yaris row of `data/three_class_matched_2026-08-14.csv`, checked live. **So `n_grid`, `dx` and depth/`dx` all translate EXACTLY between R7 and the canonical Yaris scene.** The caveat holds only for Rogue and Silverado, whose `grid_lim` are 10.4425 and 13.0679.

**Consequence, and it should be read as a flag rather than a verdict:**

| project result | depth/`dx` | against the ceiling |
|---|---|---|
| canonical 17 runs, g48 / g64 / g96 | 1.500 / 2.000 / **3.000** | at or below the last passing rung |
| matched-`dx` three-class, all arms | **3.500** | **above** |
| `M_yaris_n111`, same box as R7 | **3.500** | **above, and between the two failing rungs** |
| item 44's canonical g128 mass sweep | **4.000** | **above** |

**`M_yaris_n111` is the sharpest case**: identical `grid_lim`, identical depth, and an `n_grid` sitting between g104 and g112, both of which fail in R7 at about 1.6 m.

**WHAT GENUINELY DOES NOT TRANSFER, stated so this is not over-read.** R7's body is a **rigid box at the hull's bounding-box dimensions**, 1.7078 x 4.2014 x 1.4853, **not the hull**, and its forcing is a **one-shot velocity kick** rather than the per-frame Dirichlet clamp of the gated driver. **The grid axis now transfers exactly; the body and forcing axes are untested.** That is the experiment to run, and it is no longer a question of whether the scenes are comparable in resolution, because on that axis they are identical.

**THE METHOD POINT IS CORRECT AND SHOULD BE KEPT VERBATIM.** A symmetry control is cheap, it is unambiguous because the exact solution is known by construction rather than by comparison, and **it found a ceiling that no gate in this project detects.** D5 records that no gate here is a physics validation; this is the first check in the project that could have failed for a reason external to the code, and it did.

**THE OPERATIONAL RULE, RESTATED IN THE CURRENCY THAT TRANSFERS.** G23j set it at g128, G23k at g112; both are `n_grid`, which does not transfer across vehicles. **State it as depth/`dx`: any result above depth/`dx` 3.0 needs a repeat-run determinism floor and a frame count beside it.** That covers every matched-`dx` arm and every g128 result while correctly leaving the canonical 17 below the line. The full night record is `.claude/dispatch_prompts/NIGHT_FINDINGS_2026-08-15.md` in the **main checkout**; it is absent from this worktree, which is the known worktree-visibility gap and not a missing file.

**G24. THE SAME SETTLE DEFECT INVALIDATES PUBLISHED THREE-CLASS NUMBERS, AND ONE ORDERING IS NOT WRONG IN LEVEL BUT INVERTED. T2, relayed 2026-08-15 from commit `5e421dd` on `claude/fork-moving-driver`, three classes at matched `dx`, 250-frame settle so the ring has decayed, 50 drive frames so no vehicle reaches the wall, band 1.0 `dx`, PPC 8, both `F_N` bases. Supersedes that session's own 4f and 4p.** Five changes, all downward in drama:

1. **The traction-margin spread collapses from 6.07x to 1.94x measured, 1.82x analytic**, so the published figure was inflated roughly threefold by the settle transient plus the wall. **Any 6.1x on a figure, caption or doc is superseded.**
2. **The gate-error ordering REVERSES.** At 60 frames it read **63.28, 94.44, 157.06**, monotone *increasing* with vehicle size, and a paragraph was built on the Silverado being worst. Converged it reads **72.88, 49.75, 34.01**, monotone *decreasing*. **Every relative statement about coupling error across vehicles was inverted in order, not merely wrong in level.**
3. **The adversarial review's blocking finding largely dissolves.** Measured against analytic normal load now agree at 5951.6 vs 6367.9 (6.5 percent), 10009.4 vs 10846.0 (7.7 percent) and 19901.5 vs 19787.5 (0.6 percent), against a **factor of two** for the Yaris at 60 frames. **The defect was the settle, not the algebra.**
4. **The corner is one marginal cell.** Only the Yaris exceeds, at **1.149 measured and 1.078 analytic**, 8 to 15 percent over threshold rather than 276 percent, and substituting the measured mu = 0.55 for the 0.30 convention divides by 1.83 and **removes it outright**. Consistent with the mu provenance chain and its +83.3 percent on `T_avail`.
5. **Drag is nearly vehicle-independent**, at -1473, -1813 and -1696 N, so the spread is driven by weight minus buoyancy, not by drag. **All three still fail the at-rest gate, so all three remain INDETERMINATE and none is a measurement of a vehicle.**

**G24a. THE STANDING RULE THIS PRODUCES, AND IT IS THE NIGHT'S SINGLE MOST TRANSFERABLE RESULT.** Three times out of three on 2026-08-14/15, **non-monotone and dramatic-looking results in this stack turned out to be short integrations**: a 60-frame settle produced a 6.1x spread, an inverted ordering, a factor-of-two `F_N` gap and a corner that vanished under substitution, and every one of them looked like a physical result. The same defect refuted the R7 mirror ladder at G23a and that session's own at-rest gate. **Before publishing any number from this stack, state the settle length it was measured at.** A number without its settle length is not a result. This generalises B2's non-monotone grid study: **an apparent non-monotonicity is a claim about the converged state, and it cannot be made from inside the transient.**

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

**H7. WITHDRAWN AS A PRESENT-TENSE CLAIM 2026-08-21: THE `_GRIDAWARE` LEDGER SIBLING NO LONGER EXISTS.** This entry read "`VERIFIED_FACTS_LEDGER_july24.md` and its `_GRIDAWARE` sibling are byte-identical except one sentence at line 307 of each", V24 saying "the 17 gated runs" and GA "the 17 runs in render_s2". A `find` over the whole tree on 2026-08-21 returns **eleven `_GRIDAWARE` files and no `VERIFIED_FACTS_LEDGER_july24_GRIDAWARE.md`**. The one-sentence fork is retained as history; do not send a reader to the sibling. `CLAUDE.md` carried the same dangling reference and was corrected the same day.

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
15. **THIS ITEM NEEDS TWO QUALIFIERS, NOT ONE: ITS `mu` (15a) AND A REALIZED-DEPTH CONFOUND (15b). Every pushed copy of item 15 as of 2026-08-14 reads as unqualified resolution-dependence, and that reading is not supportable.**

    **15b. THE PUBLISHED g96 -> g128 FLIP IS A `dx` CUT AND A DEPTH INCREASE AT THE SAME TIME. Found by the rtfd thread, commit `92088f1`, 2026-08-14. This item presents it as refinement alone.** Silverado realized depth across the flipping ladder is **0.30627968 / 0.27224860 / 0.30627968** at g64 / g96 / g128. **g64 and g128 are BIT-IDENTICAL and g96 is 11.11 percent shallower**, so the g96 -> g128 step is a **25.0 percent `dx` cut AND a 12.50 percent depth increase together.** A deeper flow at the finer grid is not a refinement control.

    **AND IT IS STRUCTURAL, NOT A SETUP SLIP.** Realized depth is `water_layers * h` with **integer** layers, so depth is quantised by the grid. **"Hold depth fixed while refining" is impossible on this ladder without matching layers**, which is the same quantisation that makes item 44's depth exactly invariant only because its layer counts happen to land (3.000 and 4.000 cells). **The Rogue's depth moves DIFFERENTLY**, 0.32632925 / 0.32632925 / 0.28553810, so this is not a uniform bias that could be argued away. **"Opposite" was my word and it oversimplifies, corrected 2026-08-14 on review: the two shapes are not mirror images.** The Silverado's bit-identical pair is its two **endpoints**, g64 = g128, with the dip at the **middle** grid; the Rogue's bit-identical pair is its **first two**, g64 = g96, with the drop only at the **finest**. **Both are non-monotone and differently shaped, which is the substantive point; neither is the other's mirror.** All figures independently recomputed from the raw `h` and `water_layers` columns of `data/rogue_silverado_grid_sweep_2026-08-13.csv` rather than from any pre-computed depth column, and the 11.111111 / 12.500000 / 25.000000 percent figures reproduce exactly, not merely to rounding.

    **THIS ITEM'S PASSTHROUGH ARGUMENT ALSO USES THE WRONG VEHICLE.** It argues the Rogue's passthrough is flat, 9.95 to 9.88 percent, while **omitting Rogue g96 at 0.10716, which BREACHES P-2**; and the body that actually flips is the **Silverado**, whose passthrough is **not flat but rises monotonically 0.08362 / 0.08950 / 0.09679** across exactly the flipping rungs. **The rising-Silverado form is the stronger argument and is already recorded at D9; use that one.**

    **NET EFFECT ON THIS ITEM, stated plainly: the flip is real and reproduced, and it is contingent on `mu` (15a) and confounded with a 12.50 percent depth change (15b). It may not be cited as evidence of resolution-dependence alone.**

    **READ D9 AND ITEM 44 WITH THIS ITEM.** A SECOND, DIFFERENT mechanism also flips a SLIDE verdict "at g96": floor friction (D8), measured on the other branch and merged in on 2026-08-13. D9 reconciles them and corrects this item's "67 percent" to **64.2 percent** with the column named. Item 15 walks grid at fixed `mu` 0.55; D8 walks `mu` at fixed grid; ~~the 2 x 2 has never been run~~ **the 2 x 2 HAS NOW BEEN RUN, see item 15a below, and the two effects INTERACT.**

    **15a. THIS ITEM MUST CARRY ITS `mu`. THE FLIP IS JOINTLY CONTINGENT ON `dx` AND `mu`, NOT RESOLUTION-DEPENDENT SIMPLICITER. Measured by the three-class thread, commit `a5a7b62` on `claude/fork-three-class`, relayed and re-read here from the commit body 2026-08-14. Engine warpmpm, NON-CANONICAL, Silverado 2270 kg, everything else held fixed.**

    | | `mu` 0.30 | `mu` 0.55 |
    |---|---|---|
    | `n96`, `dx` 0.1361 | SLIDE, margin **10** | SLIDE, margin **0** |
    | `n154`, `dx` 0.0849 | SLIDE, margin **11** | **STUCK**, margin **-3** |

    **(a) STUCK OCCUPIES EXACTLY ONE CORNER.** A fine grid **and** a high friction coefficient are **both** necessary; neither alone produces it. **This item is not refuted, it is reproduced and made conditional.** Write "the flip is jointly contingent on `dx` and `mu`", never "the verdict is resolution-dependent" unqualified.

    **(b) THE RESOLUTION-DEPENDENCE IS ITSELF FRICTION-DEPENDENT, and this is the part most likely to be lost.** At the AR&R/Shand convention `mu` **0.30**, a **37 percent** `dx` refinement moves the margin only **10 -> 11 frames**, so the verdict is robustly SLIDE at **both** resolutions. **The entire resolution sensitivity of this verdict lives at the high-`mu` end.** That is an **interaction, not two independent main effects**, and the operative consequence is that **a grid-convergence statement made at `mu` 0.55 does not transfer to `mu` 0.30.**

    **(c) THE STUCK CORNER IS CONTAINMENT-FAILED, and this qualifier was absent from the relay that carried the result here. Recovered by reading `a5a7b62`'s own body.** In its words: the coarse `mu` 0.30 run **passes** gate P-2 at ~~0.09046~~ **0.09170**, see (c-CORRECTED) below, "while every matched-dx run fails it, so the one corner with clean containment is a SLIDE corner." **So the single STUCK cell is a gate-failed cell.** Treat it exactly as item 44 treats `canon_g128_m1100`: containment-failed, not a result. **The strongest defensible statement from this square is therefore the negative one** — at the safety convention `mu` 0.30, refinement does not flip the verdict and containment is clean — **and the STUCK corner is the weakest cell in the square, not the headline.**

    **(d) SCOPE.** Silverado hull, not the canonical Yaris; two grids, not four; one mass. `n96` here is `dx` 0.1361, which D9 records is **38.7 percent coarser** than the Yaris `n96`, so this square is not at the canonical set's resolution either.

    **(c-CORRECTED 2026-08-14) THE NUMBER IN (c) IS WRONG AND THE SCOPE OF (c) IS TOO WIDE. Both caught by the rtfd thread, commit `92088f1`, and both re-verified here against the square's OWN STORE rather than against either commit body.**

    **The number.** (c) says the coarse `mu` 0.30 corner passes P-2 at **0.09046**. `[live]` `data/three_class_dxmu_2026-08-14.csv` on `claude/fork-three-class`, the file `a5a7b62` itself added, records `MU_silverado_n96_m2270_mu0p30` at **0.09169538815033645**, i.e. **0.09170**. The commit body and its own committed CSV disagree, and **the CSV wins**. Note its `job_id` field is **empty**. (The nearby 0.09041 is `S_silverado_n96_m2270`, job 3364497, a **different** arm from the matched set; 0.09046 looks like a conflation of the two.) **The conclusion is unchanged: 0.09170 is still under 0.10 and still passes.** Only the figure moves.

    **And the reason I propagated it is item 43's rule applied to my own entry.** (c) states it was "relayed and re-read from the commit body". **The relay and the re-read were the SAME commit body, so that was one source cited twice, and it carried one defect into three places.** Re-reading a claim's own source is not corroboration of it; only a different artifact is, which is what the CSV provided.

    **The scope.** (c) is true of **the square** and must not be read onto J15's own ladder. `[live]` **J15's g128 STUCK is CONTAINED, passthrough 0.09679**, while the square's `n154` STUCK fails P-2 at 0.10318. **Two different STUCK results with opposite containment status.** Cite (c) only against the square.

    **(e) THE `n96` MARGIN-0 CELL IS ONE DRAW FROM A DISTRIBUTION THAT CONTAINS STUCK. Measured 2026-08-14, LS6 job 3365305, 8 independent starts per cell, commit `12a20c0`; read from the commit body here, not relayed.** The square above reports one run per cell. With the initial condition actually varied:

    | cell | 8 independent starts | `k_crit` |
    |---|---|---|
    | `n96`, `dx` 0.1361, the margin-0 cell | **SLIDE 7/8, STUCK 1/8** | 0.9292 +/- 0.0656, range 0.8429 to 1.0029 |
    | `n154`, `dx` 0.0849, the flip cell | **STUCK 8/8**, `margin_frames` exactly -3 every start | 2.6860 +/- 0.2477 |

    **So the "SLIDE, margin 0" entry in the square is not a stable verdict**; the ensemble straddles the `k_crit` = 1.0 boundary and one start in eight returns STUCK. **The flip cell is the opposite and is strengthened**: 8/8, `margin_frames` -3 every time, `k_crit` never within 1.37 of the boundary. **Quote the square with its ensemble, and never present the margin-0 cell as a determinate SLIDE.**

    **(f) THE REASON EVERY EARLIER REPEAT UNDERSTATED THIS: NOTHING WAS VARYING THE INITIAL CONDITION.** **THE LINE NUMBERS BELOW ARE THE TOP-LEVEL COPY ONLY, corrected 2026-08-14 on adversarial review after I committed them without a ref, which is precisely the hazard D7b and D8c exist to prevent and which I wrote D7b about before making this mistake.** In `renders/yaris_render_s1/sim_standing.py` (**tracked, 564 lines, sha256 `4696c3b2`**) `:155` accepts `seed=0`, uses it at `:165` and `:183` for the initial water-particle jitter, and `main()` at `:397` **never passes one**. **In the `_incoming/` copy (untracked, 389 lines, sha256 `5215c38b`, the driver that produced the 17 canonical runs per D8c) the same facts sit at `:77`, `:87`, about `:105` and `:251`, and `:397` DOES NOT EXIST — the file is 389 lines.** **The substance holds for BOTH copies: no seed is ever injected and every run shares one initial condition.** But **if this is ever used to caveat the 17 canonical runs specifically, cite the `_incoming/` numbers, not these.** The ensemble experiment itself imported the top-level copy, so these numbers are correct for what was actually run. **So every prior repeat in this project measured solver noise at ONE fixed initial state, not sensitivity to the state.** This is the distinction the settling review draws between repeat counts and independent-start ensembles, and it is why item 42's non-determinism and item 44's repeat job are weaker evidence than they appear: they are same-seed repeats. **`determinism_identical` (item 44) is even less informative than recorded, since it was never exposed to a different start.** The seed was injected by a wrapper subclassing the scene, so the driver's stamped sha256 is untouched and D8c's identity argument is unaffected.

    **(g) THE `k_crit` NOISE FLOOR DOES NOT TRANSFER BETWEEN STATISTICS, AND THIS INVALIDATES A PRECISION CLAIM IN ITEM 44.** The earlier floor was measured on `ratio_slide` at **0.11 to 1.21 percent**; on `k_crit` the same cells spread **19 to 26 percent**, because `k_crit` is a min-over-windows-of-a-max and is far noisier. The two-run **6.3 percent** estimate for the flip cell is **superseded by 25.9 percent over eight runs**. **Consequence for item 44: it states `g128_m2337` is `k_crit` 0.9759, "needing 2.4 percent weakening to flip".** A 2.4 percent margin sits an order of magnitude inside a 19-26 percent spread. **That measurement is on Silverado cells and no ensemble exists for the Yaris `g128_m2337` cell, so this is a caution and not a measured refutation** — but **2.4 percent must not be quoted as a precision statement until that cell has its own ensemble.** **`margin_frames` is the stable statistic**, -3 in all eight starts, which is what item 15's "margin_frames assumes nothing and is the number to quote" already says and is now measured rather than asserted. **Any fragility number must name the statistic it was measured on.** **AND THE TEST THIS ITEM ASKS FOR HAS NOW BEEN PARTLY RUN: item 44, added 2026-08-13 on a third branch and merged in here on 2026-08-14, reports the g128 canonical mass sweep. Do not read the "single highest-value open item" wording below as untouched.** All three masses stay SLIDE, so no verdict flips, but that covers **3 of the 17 canonical configurations**; the 3 `sweepD` and 5 `sweepV` runs, including the only STUCK run, still have no g128 counterpart. **The item stays open with its scope narrowed, and the finding moved from the verdict to the margin**: `g128_m2337` sits at `margin_frames` 0, `k_crit` 0.9759, i.e. 2.4 percent from flipping.

    **NEW 2026-08-13, and it is now the single highest-value open item: RUN THE CANONICAL SET AT g128.** A SLIDE verdict has been shown to be resolution-dependent. `analysis/classify_rogue_silverado_sweep.py`, calling the same `classify_timeseries` behind the 17, puts Silverado at **SLIDE at g64 and g96 and STUCK at g128** (`data/rogue_silverado_slide_classification_2026-08-13.csv`). It is not a drift-threshold failure: max drift at g128 is 0.0778 m, still 1.56x `slide_m`. It fails the JOINT drift-and-speed condition for 3 consecutive frames, the same signature as `sweepV_g64_v0p5`. Mechanism is the initial surge impulse weakening with refinement, peak `|vx|` 0.771 -> 0.360 -> 0.204 m/s. Passthrough does not explain it: Rogue's passthrough is flat, 9.95 -> 9.88 percent, while its drift still falls 67 percent.

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

17. **THE g128 CANONICAL SET NOW EXISTS, AND THE VERDICT SURVIVES REFINEMENT.**
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

18. **THE g128 VELOCITY SWEEP: EVERY VERDICT HOLDS, AND PASSTHROUGH GETS WORSE.**
     Run 2026-08-18 on Vista c642-032 (GH200) in idev job 917886 via the unmodified
     `run_sweep.sh 128`, writing to new `sweepV_g128_*` directories.

     | v (m/s) | g64 margin | g128 margin | g64 verdict | g128 verdict |
     |---------|-----------:|------------:|-------------|--------------|
     | 0.5     |         -2 |          -3 | STUCK       | STUCK        |
     | 1.0     |         22 |           7 | SLIDE       | SLIDE        |
     | 2.0     |         50 |          37 | SLIDE       | SLIDE        |
     | 2.5     |         56 |          46 | SLIDE       | SLIDE        |
     | 3.0     |         50 |          53 | SLIDE       | SLIDE        |

     **All five verdicts are identical at g64 and g128**, including `v0p5` staying
     STUCK. Combined with J17's three masses, the binary verdict is now shown
     grid-invariant at twice the canonical resolution across eight cases. Margins
     move substantially (22 to 7 at v=1.0), so again: the verdict converges, the
     margin does not.

     **P-2 PASSTHROUGH IS WORSE AT g128, NOT BETTER, AND THE PENALTY GROWS WITH
     VELOCITY.** Measured live, both grids, `passthrough_max_frac`:

     | v (m/s) | g64 | g128 | delta |
     |---------|------:|------:|-------:|
     | 0.5 | 0.0799 | 0.0837 | +0.0038 |
     | 1.0 | 0.0922 | 0.0928 | +0.0006 |
     | 2.0 | 0.1149 | 0.1257 | +0.0107 |
     | 2.5 | 0.1278 | 0.1437 | +0.0159 |
     | 3.0 | 0.1588 | 0.1771 | +0.0183 |

     This is counter-intuitive and it matters. Refining the grid does NOT reduce
     water penetration into the hull; it increases it at every velocity, and the
     increase itself rises monotonically with velocity. Three of the five g128
     cases fail the 0.10 P-2 limit where the same cases failed at g64, so
     refinement does not rescue them.
     **Do not offer resolution as the remedy for passthrough.** The Undermind
     report `Quantitative_MPM_Wall_Penetration.md` searched 16 papers and found no
     record of a calibration or subtraction protocol for a smeared wall layer and
     no defensible minimum cell count across shallow water, so there is no
     published correction to appeal to either. The candidate fix is a boundary
     treatment, not a finer grid: image particles (Schulz and Sutmann 2019) address
     exactly the stress artefact that smears multiple grid lengths into the body.

     Artifacts at `data/g128_sweeps_2026-08-18/`. The three `sweepD_g128_*` depth
     cases from the same runner are NOT yet classified here.

19. **THE g128 DEPTH SWEEP COMPLETES AN 11-CASE GRID-INVARIANCE RESULT, AND
     REFINEMENT INTRODUCES A NEW P-2 FAILURE.** Same run as J18, `run_sweep.sh 128`,
     Vista c642-032, job 917886.

     | depth (m) | g64 margin | g128 margin | g64 verdict | g128 verdict | g128 layers |
     |-----------|-----------:|------------:|-------------|--------------|------------:|
     | 0.25      |         22 |          17 | SLIDE       | SLIDE        |           7 |
     | 0.35      |         56 |          40 | SLIDE       | SLIDE        |          10 |
     | 0.45      |         49 |          44 | SLIDE       | SLIDE        |          12 |

     **THE COMPLETE g128 PICTURE IS NOW 11 CASES**, three masses (J17), five
     velocities (J18) and three depths here. **Every one of the 11 verdicts is
     identical to its g64 counterpart**, including the single STUCK at v=0.5. The
     binary verdict is therefore grid-invariant from g64 to g128 across the entire
     canonical design, which is a materially stronger statement than the
     three-grid, verdict-only claim of August 4 item 5. `margin_frames` remains
     non-convergent in all three families.

     **REFINEMENT CREATES A P-2 FAILURE THAT DID NOT EXIST AT g64.**

     | depth | g64 P-2 | g128 P-2 | delta | newly failing |
     |-------|--------:|---------:|------:|---------------|
     | 0.25  |  0.0968 |   0.1051 | +0.0083 | **YES** |
     | 0.35  |  0.1044 |   0.1141 | +0.0097 | no, already failing |
     | 0.45  |  0.1080 |   0.1203 | +0.0123 | no, already failing |

     `sweepD_d0p25` PASSED the 0.10 limit at g64 and FAILS it at g128. Across all
     11 g128 cases passthrough rose without exception. Refinement is not merely
     failing to fix wall penetration, it is actively worsening it and can convert
     a passing case into a failing one. Anyone reporting "we refined the grid" as
     a robustness improvement must report this alongside it.

     Water layers scale as expected with depth, 7 / 10 / 12, so the free surface
     is better resolved at g128 even where P-2 degrades. Those two facts are not
     in conflict: layer count measures how well the water column is sampled,
     passthrough measures the boundary treatment at the hull, and only the second
     is what image particles (Schulz and Sutmann 2019) would address.

20. **THE BOUNDED-DOMAIN ARTIFACT IS LARGER THAN THE SLOPE IT WOULD MASK, AND
     OPENING THE STREAMWISE FACES REMOVES IT. B3 IS NOW MEASURED, NOT ASSERTED.**

     `docs/HANDOFF_2026-08-18_REALISTIC_ENVIRONMENT.md` blocker B3 stated that a
     bounded domain physically cannot measure a slope, because conserving volume
     in a closed box forces a redistribution larger than the effect. That was an
     assertion carried across sessions. It is now a number.

     Measured 2026-08-18 on Vista c642-032 (GH200, idev job 917886), g64, water
     only, 90 frames, depth 0.30 m, velocity 1.5 m/s, domain lim 9.421742314 m
     (the Yaris-derived value, so the geometry matches the canonical scene).
     Driver `simulation/sim_channel.py`, BC module `simulation/openchannel_bc.py`,
     both landed in be1b138. Artifacts `data/openchannel_2026-08-18/`.

     The discriminator is the streamwise slope of the free surface. In
     road-aligned axes, uniform flow has a surface parallel to the bed, so the
     correct answer is ~0 whatever the grade; a non-zero slope is accumulation.
     Discard length and n_eff come from `analysis/stationarity.py`, NOT from a
     fixed settle length.

     | bc      | grade | slope m/m | RUM95   | n_eff | discard | stationary | drained bins |
     |---------|------:|----------:|--------:|------:|--------:|------------|-------------:|
     | closed  | 0 deg | +0.09268  | 0.00161 |   4.4 |      59 | yes        | 2 of 12      |
     | closed  | 3 deg | +0.16946  | 0.00224 |   3.9 |      70 | **no**     | 4 of 12      |
     | recycle | 0 deg | -0.00284  | 0.00029 |   9.1 |      65 | yes        | 0 of 12      |
     | recycle | 1 deg | -0.00072  | 0.00096 |   5.3 |      52 | yes        | 0 of 12      |
     | recycle | 3 deg | +0.00596  | 0.00086 |   4.3 |      79 | **no**     | 0 of 12      |

     **AT ZERO GRADE THE CLOSED BOX MANUFACTURES +0.0927 m/m OF FREE-SURFACE
     SLOPE.** The bed slope of a 3 degree road is tan(3 deg) = 0.05241 m/m. The
     artifact is **1.77x the entire signal**, and 5.31x the signal at 1 degree.
     Any slope study run in the closed configuration would have been reading its
     own boundary condition. Recycling leaves 33x less.

     The drained-bin column is the same finding in binary form. The closed box
     empties 2 of 12 streamwise bins at zero grade and 4 of 12 at 3 degrees: the
     upstream end of the channel runs dry while water piles 0.74 m deep against
     the downstream wall, against a 0.30 m nominal depth. Recycling never drains
     a bin at any grade.

     SECOND, INDEPENDENT SIGNATURE, separate origin from the depth profile:
     outflow discharge rises monotonically with grade, 240.7 then 278.4 then 355.4
     particles per frame at 0, 1 and 3 degrees, +47.6 percent. The closed box
     cannot produce this quantity at all, because its upstream velocity band
     drains from 9044 particles at frame 0 to 4 by frame 89.

     THAT DECAY ALSO SETTLES A STANDING QUESTION. The canonical
     `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW` label is wrong in both halves.
     `_sustain_inflow` (sim_standing.py) only overwrites vx inside an upstream
     band and creates no particle, so it is a momentum source, not a mass inflow;
     and `_project_water` clamps x, so there is no outflow either. The handoff's
     reading that "inflow partly exists, outflow is the missing half" is wrong:
     **neither exists**. The decay of the band count was previously inferred from
     code; it is now measured, 9044 to 4.

     NOT TESTED, AND NOT CLAIMED. Zhao et al's free-overfall case, and its
     end-depth ratio, is not exercised; this is their uniform-channel case only.
     Their stated target is Rouse's finding that the critical depth is about 1.4x
     the brink depth, retrieved 2026-08-18 from their own full text via Scite
     (`10.1016/j.compfluid.2018.10.007`), because NEITHER that PDF NOR the
     hydroplaning PDF was retrievable this session: Undermind returned "could not
     get PDF" for both, and the CityU green-OA copy of the hydroplaning paper sits
     behind a Cloudflare bot challenge that was not worked around. Both grade=3
     runs are non-stationary at 5 percent over 90 frames, so those two rows are
     provisional. No vehicle is in the loop yet.

     **PRECISION RETRACTED THE SAME DAY, SEE J24.** The table above quotes the
     recycle residual as -0.00284 +/- 0.00029 m/m. Re-running the identical
     configuration at 300 frames gives +0.00673 at the same grade, and two of the
     three grades flip sign. The RUM95 measured scatter inside one short record and
     was read here as a precision; it is not one. THE COMPARISON SURVIVES, the
     precision does not. Cite the bound (|recycle slope| <= 0.0088) and the
     separation (10.6x worst case), never a recycle slope to five decimals.

21. **THE ENGINE PERMITS NO PARTICLE ADD OR REMOVE, AND periodic_x IS RULED OUT
     BY THE VEHICLE. RECYCLING IS THE ONLY AVAILABLE TRANSLATION OF ZHAO 2019.**

     Read live 2026-08-18 from `third_party/mpm-engine-544c93dd-solver-core/`:

     - `core/solver.py:103` `load_particles` constructs
       `MPM_Simulator_WARP(len(pos))` exactly once. There is no `add_particles`,
       no `remove_particles` and no resize anywhere in the Solver class. Zhao et
       al's add/remove formulation therefore cannot be implemented literally.
     - `core/solver.py:93` `periodic_x` is the engine's own streamwise wrap, and
       its docstring says "Incompatible with CDF colliders and **rigid bodies**".
       The gated vehicle IS a rigid body. `add_cdf_collider` guards this at :379;
       `add_sdf_collider` does not, so the incompatibility is silent on the SDF
       path. Do not reach for periodic_x as the road-slope fix.
     - `core/solver.py:80` `sort_interval` defaults to 0 and its own docstring
       warns that sorting "changes particle index identity". Every driver here
       addresses water as `[0, n_water)`, so this MUST stay 0. `sim_channel.py`
       raises if it is not.
     - `F` has no setter. `F()` (:543) and `F_torch()` (:625) are exports only.
       This is why a recycled particle must keep its (y, z): for a fluid,
       `kernels/mpm_utils.py:1086-1089` overwrites F every substep with
       J^(1/3) I for mat 6, 10 and 12, discarding the deviatoric part, so the only
       carried state is J; pressure is p = -bulk (J^-1.1 - 1)
       (`mpm_utils.py:28-54`); and in a uniform channel the head is a function of
       z alone. Re-inserting at the same depth re-inserts at the correct J. There
       is no host-side way to correct a wrong one.

     ALSO REACHABLE WITH NO ENGINE CHANGE, and previously believed not to be:
     gravity is overridable. `set_material` builds
     `{"material": name, "g": [0,0,-9.81], **params}` with `**params` LAST
     (solver.py:165-167), so a `g` passed through `**overrides` wins, and
     `set_parameters_dict` honours it (`kernels/mpm_solver_warp.py:742-743`).
     August 4 item 3 says the 9.81 is hardcoded "unconditionally"; that is true
     of the 17 gated runs, which pass no override, but it is NOT a property of
     the API. A road grade goes in as tilted gravity with the floor left flat,
     which is the chute formulation the periodic_x docstring itself names.

22. **THE SOUND-SPEED SHORTFALL IS NOT A NEW FINDING. THE REPO'S OWN GATE
     ALREADY REPORTS IT, AND THIS ITEM ONLY EXTENDS ITS SCOPE AND ITS SOURCING.**

     WRITTEN AS A NEW DISCOVERY IN THE FIRST DRAFT OF THIS ITEM, AND CORRECTED THE
     SAME DAY BEFORE COMMIT. Running `.claude/checks/params_check.py` emits:
     `[lit:sound_speed_cfl] 15/17 runs below the 10x convention (gamma=1.1 from the
     pinned solver), worst is sweepV_g64_v3p0: sound speed 12.8452 m/s is only
     4.28x v_max`. That gate landed in aa754dc and already carries the same
     numbers, including the same 4.28x. A number recomputed by a second script is
     the same source measured twice, not corroboration. The table below is a
     restatement of an existing gate, not an independent result.

     TWO THINGS HERE ARE ACTUALLY NEW, and only these should be cited as such:
     (a) the shortfall extends to the g128 set (J17 to J19), which postdates the
     gate's 17-run scope, since `bulk_modulus` and `sound_speed_ms` are unchanged
     at 1.5e5 and 12.8452 in every g128 summary; and (b) Zhao et al 2019 is a
     SECOND, independent citation for the same 10x convention, alongside the
     Monaghan line the gate already cites, which matters because the gate's own
     wording rests on a single convention.

     `sim_standing.py` fixes `bulk_modulus=1.5e5`, giving
     c = sqrt(1.1 K / rho) = 12.8452 m/s, a figure the g128 summaries carry
     directly as `sound_speed_ms`. Zhao et al reduce the water bulk modulus and
     require the numerical sound speed to stay above 10x the maximum flow
     velocity (`docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md`, citing Liang; the same
     Monaghan 10x convention already in this project's literature base).

     | velocity m/s | c/v   | meets >10x |
     |-------------:|------:|------------|
     | 0.5          | 25.69 | yes        |
     | 1.0          | 12.85 | yes        |
     | 1.5          |  8.56 | **no**     |
     | 2.0          |  6.42 | **no**     |
     | 2.5          |  5.14 | **no**     |
     | 3.0          |  4.28 | **no**     |

     So the canonical g64 and g128 baselines at v=1.5, and the whole upper half
     of the velocity sweep, sit below it, the worst case by a factor of 2.3. The
     gate counts 15 of 17 rather than the 4 of 6 velocities implied by the table
     because the 17 runs are not evenly spread over velocity.
     STATE THIS CAREFULLY. It is a criterion from one paper's practice, and the
     ratio uses the NOMINAL inlet velocity, so the true margin against the maximum
     realised flow velocity is worse than the table. The consequence of a low
     margin is excess compressibility, not instability, and NO published verdict
     is known to turn on it. That has not been tested. To close it, re-run one
     canonical case at a bulk modulus giving c/v >= 10 and confirm the verdict is
     unchanged. Do not close it by assertion.

23. **THE g128 RUNS WERE PRODUCED BY A DIFFERENT DRIVER FROM THE ONE THE REPO
     CALLS CANONICAL. THE PHYSICS IS IDENTICAL; THE PROVENANCE RECORD WAS NOT.**

     `docs/HANDOFF_2026-08-18_REALISTIC_ENVIRONMENT.md` says of `sim_standing.py`
     "its sha256 stamps 40 D5 runs". True for D5. NOT true for J17, J18 and J19.

     Measured live 2026-08-18. `run_s2.sh` and `run_sweep.sh`, the two scripts
     that produced the entire g128 set, both set
     `DRIVER=$BASE/sim_standing.py` with `BASE=$WORK/render_s2`. That file is
     **389 lines, sha256 5215c38b...**. The Mac canonical copy at
     `renders/yaris_render_s1/sim_standing.py` is **564 lines, sha256
     4696c3b2...**. Two other Vista copies
     (`can-it-ford-track1-6dof/`, `render_s2/multigeom_2026-08-08/`) are
     4696c3b2 and are NOT the ones the g128 runs used.

     CONFIRMED BY OUTPUT, not just by the launcher text: the 389-line driver has
     no vehicle registry, and every g128 `summary.json` is missing `vehicle_key`,
     `vehicle_class`, `mass_source`, `hull_source`, `preflight_fill_ratio`,
     `hull_watertight` and `mass_alt_kg`, all of which the 564-line driver writes.

     THE VERDICTS STAND. Extracting `class StandingFloodScene` from both files and
     diffing gives exactly ONE differing line: the 564-line version has
     `self.bulk_modulus = float(bulk_modulus)` and the 389-line one does not. That
     is a recorded attribute, not a computation. The 175-line gap is the vehicle
     registry, `resolve_vehicle`, the preflight block and hull provenance
     instrumentation, none of which enters the scene for a `--mass`-driven Yaris
     run. Scope of this check: the scene class was diffed in full; the two
     `main()` bodies were not.

     ONE LATENT FORK SURVIVES. The 389-line driver writes
     `"bulk_modulus": 1.5e5` into its summary as a HARDCODED LITERAL, while the
     564-line one writes the value actually used. They agree today because
     nothing overrides it. The moment anyone adds a `--bulk-modulus` flag, which
     J22 is a direct reason to do, the g128-lineage driver will report 1.5e5
     whatever it ran. Fix the literal before running that sweep.

24. **ROUND 2: OPENING THE DOMAIN MOVES VEHICLE PASSTHROUGH ACROSS THE P-2 GATE,
     THE LEAK HYPOTHESIS IS REFUTED, AND J20'S PRECISION IS WITHDRAWN.**

     Twenty runs, Vista jobs 918238 and 918241, 2026-08-18. Artifacts
     `data/openchannel_2026-08-18/results_round2.json`, figures under
     `renders/openchannel_2026-08-18/`.

     **(a) PASSTHROUGH IS PARTLY A BOUNDARY-CONDITION ARTIFACT.** Same script, same
     hull, same mass, only the BC differs:

     | grid | bc      | passthrough_max_frac | P-2 (limit 0.10) |
     |------|---------|---------------------:|------------------|
     | g64  | closed  | 0.1069               | FAIL             |
     | g64  | recycle | 0.0833               | **PASS**         |
     | g96  | closed  | 0.0972               | pass             |
     | g96  | recycle | 0.0848               | pass             |

     -22.1 percent at g64, crossing the gate limit, and -12.8 percent at g96. J18
     and J19 established that REFINEMENT makes passthrough worse and even converted
     a passing case to failing. This adds the other half: a substantial part of the
     passthrough is water having nowhere to go, not the hull boundary treatment.
     Image particles (Schulz and Sutmann 2019) remain worth doing and are still the
     right instrument for the hull-boundary component, but they were never going to
     address this component, and any future passthrough claim must say which of the
     two it is talking about.

     Rogue 0.0823 and Silverado 0.0797 also pass in the open channel. THESE ARE NOT
     SAME-RESOLUTION COMPARISONS: at fixed n_grid a different hull changes both dx
     and the realised depth, giving 4.1, 3.7 and 2.9 water layers for yaris, rogue
     and silverado. Displacement over 90 frames is 0.7076, 0.7437 and 0.3428 m.

     **(b) THE LEAK HYPOTHESIS IS REFUTED BY ITS OWN CONTROL.** J20 recorded that
     `leaked_particle_frames` runs 2 to 3x higher in recycle mode and was
     undiagnosed. I predicted the cause was the inlet velocity condition. A
     controlled A/B refutes it: prescribe=full 346679 against prescribe=streamwise
     350551, 1.1 percent apart. The per-axis split, added for this purpose, says
     what it actually is: **87.2 percent z, 12.8 percent y, 0.0 percent x**. Water
     is sinking through the floor plane, not escaping sideways.

     The closed-vs-open contrast is the informative part: for the SAME Yaris scene,
     clamped_z is 8009 closed against 258334 recycle, a factor of 32. A closed box
     ends as a deep slow pile; an open channel keeps fast water in contact with the
     floor for the whole run. So this is not a defect the recycler introduces, it is
     a floor-BC defect that only becomes visible once the flow is sustained, and it
     is the same class of penetration as the hull passthrough in (a).

     **(c) THE RECYCLE RESIDUAL SLOPE IS BOUNDED, NOT RESOLVED. J20's PRECISION IS
     WITHDRAWN.** Identical configurations at two record lengths:

     | grade | 90 frames | 300 frames | |
     |-------|----------:|-----------:|--|
     | 0 deg | -0.00284  | +0.00673   | **sign flip** |
     | 1 deg | -0.00072  | -0.00350   | |
     | 3 deg | +0.00596  | -0.00876   | **sign flip** |

     The trend with grade is monotone increasing at 90 frames and monotone
     decreasing at 300. Two of three flip sign. n_eff is 4.3 to 13.5. The 300-frame
     grade=1 run is NON-stationary at 5 percent with a recommended discard of 268 of
     300, so a longer record did not simply fix it, and D9's 250-frame figure is not
     sufficient here either.

     WHAT SURVIVES, and this is what J20 was actually claiming: every recycle
     residual, at both record lengths and all three grades, has magnitude <= 0.0088,
     against 0.0927 and 0.1695 for the closed box. Worst-case separation 10.6x, and
     every recycle residual sits at least 6.0x below tan(3 deg) = 0.05241. The
     closed-box artifact still exceeds the bed slope of a 3 degree road and the
     recycle residual still sits well under it. **Cite the bound and the separation.
     Never cite a recycle slope to five decimals.**

     GENERAL LESSON, worth more than the number: a RUM95 computed from one record
     measures scatter WITHIN that record. It is not run-to-run reproducibility and
     it is not evidence the mean has converged. The only thing that caught this was
     re-running at a different length, which is the cheapest control available here
     and was not part of the protocol. It should be.

25. **THE FIRST FREE-OVERFALL ATTEMPT DRAINED ITSELF, AND `clamped_z == 0` WAS THE
     TELL THAT LOOKED LIKE CLEANLINESS.**

     `add_box` (solver.py:224) is documented as a "volumetric grid-node velocity
     overwrite", not surface contact. It zeroes the velocity of grid nodes it
     covers and applies NO restoring force. A particle that drifts into the bed is
     therefore trapped there for the rest of the run.

     The first three overfall runs (v=0.7, 1.0, 1.3, 2026-08-18) bled water into
     their own bed for 240 frames: discharge decayed from q=0.16 to q=0.016 m2/s,
     the caught count fell 611 to 63, the approach flow went supercritical with Fr
     rising past 13, the brink depth collapsed to NaN, and the Rouse ratio read 2.2
     to 7.5 against a target of 1.4.

     `water_count_conserved` was TRUE throughout, because the particles still
     existed; they were just inside the bed. And `clamped_z` was **exactly 0** in
     all three runs, which reads as a clean containment record and actually meant
     the projection had been handed `z_floor=0.0` and never fired at all. A zero in
     a diagnostic counter is not evidence of health until you have confirmed the
     diagnostic can produce a non-zero.

     Fixed in `simulation/sim_overfall.py`: the bed the box could not provide is now
     imposed host-side for x <= x_brink, and bed re-entries are counted rather than
     silently absorbed. THE ROUSE 1.4x TEST IS NOT YET PASSED OR FAILED; the
     corrected runs were still queued when this was written. Do not record a verdict
     on it from this item.

26. **THE FREE-OVERFALL BED HAD TO BE AN SDF COLLIDER. add_box IS A VELOCITY SINK,
    NOT A WALL, AND THE SOLVER'S OWN DOCSTRING SAYS SO.**

    Item 25 recorded that the first overfall attempt drained itself and blamed the
    absence of a host-side bed clamp. Adding that clamp did NOT fix it. The real
    cause is the collider choice, and the engine documents it at
    `core/solver.py:224`: add_box is a "volumetric grid-node velocity overwrite
    ... for oriented surface contact with friction modes use add_sdf_collider".

    Measured 2026-08-18, three inlet velocities each, grid 96, 94656 water
    particles, `data/openchannel_2026-08-18/overfall_rounds.json`:

    | bed | bed re-entries per frame | y_b late | Fr late | regime |
    |-----|-------------------------:|---------:|--------:|--------|
    | add_box            | 31903 | 0.0217 | 6.95 | supercritical, drained |
    | add_sdf_collider   |  1094 | 0.0523 | 0.11 | subcritical, holds depth |

    A 29x reduction in bed penetration, the depth holds instead of collapsing to a
    0.01 m film, and the flow lands in the subcritical regime Rouse's end-depth
    ratio actually applies to. THE BOX ARM IS KEPT as an explicit control rather
    than deleted, because the failure mode is the reusable part.

    SECOND DEFECT, found by fixing the first. With the SDF bed the channel holds
    depth but the discharge decays from 0.28 to 0.009 m2/s: a horizontal bed with
    no sustained head has nothing driving it once the injected momentum is spent.
    Rouse fed his channel from a constant-head tank. `sim_overfall.py --head-len`
    adds a sustained upstream velocity band, applied ONLY upstream of the brink so
    the brink section stays unforced.

27. **THE ROUSE 1.4x TEST IS NOT PASSED. THE BEST STATIONARY SUBCRITICAL
    MEASUREMENT IS 1.286 +/- 0.025, AN 8.2 PERCENT SHORTFALL.**

    This is the project's FIRST comparison against a number that did not come out
    of its own pipeline, so the result matters more than its sign.

    Head-velocity sweep at the SDF bed, grid 96, 300 frames, discard and n_eff from
    `analysis/stationarity.py` applied to the ratio series:

    | U m/s | Fr late | ratio | RUM95 | n_eff | stationary |
    |------:|--------:|------:|------:|------:|------------|
    | 0.30  | 0.638   | 1.286 | 0.0246 | 23.2 | **yes** |
    | 0.45  | 0.858   | 1.973 | 0.1149 |  6.2 | no |
    | 0.60  | 0.980   | 1.912 | 0.0420 | 19.2 | no |

    Only the U=0.30 run is both subcritical and stationary. It gives
    **1.286 +/- 0.025 against Rouse's 1.4**: 8.2 percent low, and 1.4 sits OUTSIDE
    the RUM95 band, so this is a measured disagreement, not agreement within error.

    FOUR REASONS NOT TO CALL THIS EITHER A PASS OR A REFUTATION YET.
    (a) The retained window is 31 frames of 295 (discard 264) and n_eff is 23.2.
    (b) The ratio series passes the stationarity test while the DISCHARGE is still
        decaying, 0.171 to 0.042 m2/s. That is possible because the ratio is
        scale-free, y_b and y_c shrinking together, so a stationary ratio does NOT
        certify a steady flow. Do not read it as one.
    (c) The two faster runs, closer to Fr = 1, give 1.9 to 2.0, so the ratio is
        strongly regime-dependent across the sweep and one point is not a curve.
    (d) The recycling BC, the SDF bed friction (0.4, unsourced here) and the finite
        head are all candidate sources of an 8 percent bias and none has been
        separated. Resolution has not been varied either.

    WHAT WOULD SETTLE IT: hold a subcritical approach AND a steady discharge at the
    same time, then vary bed friction and grid resolution and see whether 1.286
    moves.

    **THAT SWEEP HAS NOW BEEN RUN AND THE 8.2 PERCENT FIGURE IS WITHDRAWN. SEE
    ITEM 30.** The ratio moves by more than 100 percent across plausible friction
    and grid choices, so 1.286 was one point on an unconverged surface and the
    8.2 percent agreement with Rouse was a coincidence of one configuration. Do not
    quote it.

28. **IMAGE PARTICLES ARE IMPLEMENTED AND NOT USABLE AS WRITTEN. THE J
    APPROXIMATION FORCED BY F HAVING NO SETTER APPEARS TO DOMINATE.**

    `simulation/image_particles.py` translates Schulz and Sutmann's boundary into a
    fixed pool: images carved out at load time, repositioned each tick as mirrors of
    band particles, because the engine cannot create a particle (item 21). Nine
    self-tests pass on synthetic data.

    In the scene it fails. THREE attempts, 12000 images, Yaris in the open channel:
    every arm with images tripped the engine's P2G edge guard before producing a
    summary, and the particle at the offending coordinate was WATER, not an image,
    both upstream (x=0.2158 against a 0.2208 limit) and downstream (x=9.064 against
    9.054). Moving the outflow plane from 4 cells to 8 fixed the downstream end and
    the upstream failure survived it. So the image layer is displacing the water,
    not merely sitting near the edge itself.

    THE LIKELY MECHANISM IS THE ONE THE MODULE DOCSTRING ALREADY FLAGS. An image
    ought to carry its source's compression state. F has no setter, so it carries
    whatever J its own history produced, and pressure is p = -bulk (J^-1.1 - 1). At
    12000 images that is a large spurious pressure source sitting under the floor.
    THE COUNT SCAN SETTLES IT, AND IT IS A REFUTATION, NOT A TUNING PROBLEM.
    Same scene, outflow at 8 cells, only the image count varies:

    | images | clamped_z | vs baseline | P-2    | vs baseline |
    |-------:|----------:|------------:|-------:|------------:|
    |      0 |   664372  |      -      | 0.0833 |      -      |
    |    500 |   650615  |   -2.1%     | 0.0833 |    0.0%     |
    |   2000 |   713498  |   +7.4%     | 0.0833 |    0.0%     |
    |   6000 |   877972  |  **+32.2%** | 0.0869 |   +4.3%     |
    |  12000 |   CRASHED |      -      |   -    |      -      |

    Floor penetration gets MONOTONICALLY WORSE as images are added, and the one
    case that is indistinguishable from baseline (500) is the one with almost no
    images in it. That is the opposite of what a working boundary treatment does,
    and monotonicity rules out "the count was mistuned": there is no count at which
    this helps. It is the signature of the images acting as a spurious pressure
    source rather than as boundary support, which is exactly the J mechanism the
    module docstring flags, so the refutation and the predicted failure mode agree.

    WHAT THIS DOES AND DOES NOT ESTABLISH. It refutes THIS implementation, a
    host-side mirror in a pool whose F cannot be written. It does NOT refute Schulz
    and Sutmann, whose method assumes the image carries the source's stress state.
    Implementing it properly needs a kernel-side F assignment, which is engine work,
    not driver work. Record it as "attempted, refuted, mechanism identified",
    never as "image particles do not work".

    DO NOT record image particles as the passthrough fix. Item 24 already showed
    that a substantial part of the passthrough is a boundary-condition artifact
    that opening the domain removes, and this item shows the remaining part is not
    addressed by this implementation.

29. **`floor_friction = 0.55` IS UNSOURCED AND IS 23x THE ONLY MEASURED VALUE.
    NIHEI ET AL 2025 IS THE FULL-SCALE SLIDING EXPERIMENT THIS PROJECT HAS BEEN
    SAYING DOES NOT EXIST.**

    Nihei, Onomura, Bando, Inoue, Kashiwada, Yoshikawa and Tanaka (2025),
    *Results in Engineering* 28, 107189, `10.1016/j.rineng.2025.107189`, CC-BY.
    Verified matched, high confidence, 2026-08-18. **NOT in the 332-paper corpus
    index** (`--query` returns 0), so it is genuinely new to the project, and the
    PDF is on local disk at `~/Downloads/1-s2.0-S259012302503244X-main.pdf`.

    **IT CARRIES AN ERRATUM**, `10.1016/j.rineng.2025.107527`, listed twice by
    Crossref. Check it before quoting any number below into the paper.

    WHAT IT MEASURES. Full-scale prototype passenger vehicles in a large outdoor
    open channel, targeting SLIDING rather than floating, which is the mode 16 of
    the project's 17 runs return. At washaway with the handbrake DISENGAGED the
    rolling-resistance coefficient is **mu_R = 0.0250 and 0.0242**, about an order
    of magnitude below the locked-wheel static value **mu_s ~ 0.30**. They also
    report **C_D = 1.38 +/- 0.18**, and that mu_R decays to a steady state near 40
    percent of its initial maximum, so a criterion built on peak mu_R is
    unconservative.

    WHAT IT SAYS ABOUT THIS REPO. `sim_standing.py` defaults `floor_friction=0.55`
    and nothing sources it; the same literal recurs in `sim_dam_break.py`,
    `box_sdf_collider_setup.py` and the abandoned Genesis Track 2 files. Against
    Nihei's measurements, 0.55 is **1.8x the locked-wheel value and 23x the
    free-rolling value**. Their Eq. 8 discussion gives critical velocity scaling as
    sqrt(mu), so:

    | condition | mu | mu / 0.55 | V_crit factor vs the project |
    |---|---:|---:|---:|
    | project default        | 0.55   | 1.000 | 1.000 |
    | locked wheels (mu_s)   | 0.30   | 0.545 | 0.739 |
    | free-rolling (mu_R)    | 0.0242 | 0.044 | **0.210** |

    THE DIRECTION OF THE ERROR MATTERS AND IT IS MOSTLY GOOD NEWS. Lower friction
    slides more easily, so the 16 SLIDE verdicts obtained at mu=0.55 are
    CONSERVATIVE with respect to friction and would only strengthen at a realistic
    rolling resistance. **The single STUCK, `sweepV_g64_v0p5`, is the one verdict
    NOT protected by that argument**, and it is the one to re-run at mu_R before
    anyone reports "16 SLIDE and 1 STUCK" again.

    DO NOT SIMPLY SET friction TO 0.0242. Nihei's mu_R is a TIRE-ON-ROAD rolling
    resistance for a wheeled vehicle free to roll. The project's floor_friction is
    a Coulomb coefficient in an MPM grid boundary condition acting on a solidified
    particle hull with no wheels. They are not the same quantity, and substituting
    one for the other would be the same category error as the AR&R-versus-hull
    mismatches already in this register. What IS established is that 0.55 is
    unsourced, that it sits far above every measured value in the nearest
    experiment, and that the sensitivity is a square root rather than linear.

    IT ALSO RETIRES A STANDING GAP. Item L-2 and the paper's limitations draft both
    say there is no experimental basis for a sliding threshold in the corpus. There
    is now, at full scale, and it disagrees with AR&R specifically because AR&R's
    experiments were static with fixed wheels while real washaways involve vehicles
    free to roll. Their Fig. 17 plots all three, unbraked, braked and AR&R (2011),
    for a small passenger vehicle.

    **AMENDED 2026-08-18: THE CORRIGENDUM IS STILL UNREAD, BUT ITS BLAST RADIUS IS
    NOW MEASURED, AND IT IS DOCUMENTARY ONLY.** Every number in this item comes from
    Nihei et al 2025, `10.1016/j.rineng.2025.107189`, which carries a corrigendum,
    `10.1016/j.rineng.2025.107527`. scite confirms the link in the original's
    `editorialNotices`. The corrigendum text has resisted **ten** retrieval routes
    (doi.org, ScienceDirect, linkinghub, DOAJ, Unpaywall, OpenAlex, Semantic Scholar,
    Europe PMC, the scite connector, and scite's own signed access link), all recorded
    at `.claude/worktrees/r5-research/docs/R5_RESEARCH_NIHEI_ROUTES_AND_AUTHOR_TRAP_2026-08-16.md`.
    Two further attempts on 2026-08-18, scite full-text and a WebFetch through the
    Elsevier redirect, also returned nothing: scite holds the metadata and scores the
    full-text query `relevancyScore: 0.0` on both records.

    **NO ELEVENTH AUTOMATED ATTEMPT SHOULD BE MADE.** The landing page carries
    `tdm-reservation: 1`, a machine-readable opt-out from automated retrieval. Driving
    a browser at it to extract the text is the thing that header reserves against, and
    the article being CC-BY does not settle that. The remaining routes are a person
    opening the DOI, UT Austin institutional access, or asking the authors.

    **WHAT TURNS ON IT, measured live 2026-08-18 rather than assumed.** A scoped
    search for `0.0242` and `0.0250` returns **zero hits in any Python file** outside
    `third_party/` and `.claude/worktrees/`. No script, no gate, no verdict, and no
    published figure consumes these numbers. They appear in five markdown documents
    and in the `nihei2025fullscale` bib note. The four apparent hits under
    `deliverables/for_kumar/` are `passthrough_max_frac: 0.024264...`, a numeric
    coincidence and not this coefficient; that was checked, not assumed from a count.

    **SO: this is not blocking, and it was being carried as though it were.** Nothing
    computed depends on it. It becomes blocking the moment the friction argument, the
    order-of-magnitude braked-versus-unbraked claim, or the `(mu_R/mu_s)^(1/2)`
    scaling enters the paper or the poster. Resolve it before writing that section,
    not before the next run. Until then the values stay PROVISIONAL and every use
    must say so.


30. **THE OVERFALL RATIO IS NOT CONVERGED IN EITHER BED FRICTION OR GRID, AND NO
    CONFIGURATION HOLDS A STEADY DISCHARGE. ITEM 27'S 8.2 PERCENT IS WITHDRAWN.**

    Seven runs, one factor at a time about a centre point of grade 0.15 deg, bed
    friction 0.4, grid 96, head 0.6 m at U=0.30, 300 frames each. Vista job 918391.

    | run | grade | fric | grid | Fr late | q_last/q_first | ratio | RUM95 | n_eff | stationary |
    |---|---:|---:|---:|---:|---:|---:|---:|---:|---|
    | sep_g0p00   | 0.00 | 0.4 |  96 | 0.638 | 0.25 | 1.431 | 0.2495 |  4.9 | no |
    | sep_g0p15   | 0.15 | 0.4 |  96 | 0.662 | 0.25 | 1.249 | 0.0256 | 20.0 | **yes** |
    | sep_g0p30   | 0.30 | 0.4 |  96 | 0.690 | 0.27 | 1.379 | 0.0830 |  5.3 | no |
    | sep_f0p20   | 0.15 | 0.2 |  96 | 0.854 | 0.26 | 2.711 | 0.0679 | 29.2 | **yes** |
    | sep_f0p60   | 0.15 | 0.6 |  96 | 0.617 | 0.28 | 1.072 | 0.0288 | 21.6 | **yes** |
    | sep_grid64  | 0.15 | 0.4 |  64 | 0.293 | 0.26 | 0.740 | 0.0317 | 29.9 | no |
    | sep_grid128 | 0.15 | 0.4 | 128 | 1.063 | 0.29 | 2.479 | 0.0346 | 39.6 | **yes** |

    **(a) NOT CONVERGED, AND BY A LOT.** Holding everything else fixed, the ratio
    spans 1.07 to 2.71 across bed friction 0.2 to 0.6, and 0.74 to 2.48 across grid
    64 to 128. Those are swings of 117 and 124 percent about a target of 1.4. Grade
    barely matters by comparison, 0.182 of spread. So item 27's 1.286 was one point
    on an unconverged surface and its 8.2 percent agreement was a coincidence of
    one configuration, not a measurement of anything.

    **(b) THE GRID SWEEP IS CONFOUNDED AND MUST NOT BE READ AS A CONVERGENCE
    STUDY.** Froude covaries with resolution, 0.293 / 0.662 / 1.063 at grid
    64 / 96 / 128, so refining the grid changes the FLOW REGIME as well as the
    discretisation. The grid-128 case is supercritical, where Rouse's ratio does
    not apply at all. Two things moved at once; nothing was isolated.

    **(c) THE RUNS THAT AGREE ARE NOT STATIONARY AND THE STATIONARY RUNS DO NOT
    AGREE.** Only sep_g0p00 (+2.2 percent) and sep_g0p30 (-1.5 percent) put 1.4
    inside their RUM95, and both fail the reverse-arrangement test. Every run that
    passes it lands at -23.4, -10.8, +77.1 or +93.6 percent. That pattern is the
    signature of reading a number off a transient: the short, noisy records happen
    to straddle the target while the well-resolved ones do not.

    **(d) NO CONFIGURATION HOLDS A STEADY DISCHARGE, AND THE FAILURE IS
    STRUCTURAL.** q_last/q_first is 0.25 to 0.29 in ALL SEVEN runs, essentially
    independent of grade, friction and resolution. A mild bed slope did not fix it.
    That constancy is the diagnosis: the decay is a property of the recycling
    closure, not of any physics knob. With one-in-one-out recycling the total water
    is fixed and the only reservoir is the channel itself, so the channel fills,
    the throughflow settles to whatever the geometry allows, and no sustained
    supply exists to hold a discharge.

    **THIS CLOSES A LOOP THAT WAS OPEN FROM THE FIRST COMMIT.**
    `simulation/openchannel_bc.py` has said since be1b138 that one-in-one-out
    recycling expresses Zhao et al's UNIFORM channel case and "cannot express their
    NON-UNIFORM case, which needs a net flux imbalance and therefore a spare
    particle reservoir". The free overfall IS a non-uniform case. The limitation
    documented at the start is exactly the one now blocking the validation, which
    is at least evidence the documentation was honest.

    **WHAT TO DO NEXT, in order.** (1) Implement the reserve pool: allocate spare
    particles, park them outside the wetted domain, and draw from them at the inlet
    so inflow can exceed outflow. That is the piece that makes a sustained head
    possible and it is the only route to a steady discharge in this engine.
    (2) Only then re-run the friction and grid sweeps, holding Froude fixed rather
    than letting it drift with resolution. (3) Do not report a Rouse comparison
    before (1) and (2). The test is currently incapable of passing or failing.

31. **THE HYDROPLANING PAPER IS READ. IT DOES NOT SOLVE BLOCKER B2 FOR US, AND THE
    REASON IS SCALE, NOT METHOD.**

    Zhou, Zhong, He, Wang, Tang and Li (2025), *Phys. Fluids* 37(8), 083121,
    `10.1063/5.0276643`. Read in full 2026-08-18 from the CityU green-OA copy that
    Josie retrieved; four earlier routes had failed and the paper was never on this
    machine. Author list corrected: **Zhou Changhong, Zhong Qing, He Zhihe, Wang
    Yixuan, Tang Xianyuan, Li Peilin**, Guilin University of Electronic Technology
    and City University of Hong Kong. Earlier project notes said "Zhou, Qing and
    Wang", which turned Zhong Qing's given name into a surname.

    **HOW THEY EXPRESS A PAVEMENT, which is what the handoff wanted.** Not a plane
    boundary condition and not an SDF collider. The pavement is **rigid MATERIAL
    POINTS**, one of three single-phase materials (tire, water film, pavement) meeting
    at contact interfaces, handled by a **multi-material / multi-velocity-field
    contact algorithm**: contact detected by (P_I^TM - P_I^WM) . n_I^c < 0, nodal
    normals from the mass gradient, momentum corrected by normal and tangential
    contact forces with a Coulomb limit, Newton's third law imposed pairwise
    (their Eqs. 18 to 25, Fig. 3). Their Sec. III.A states the pavement "is assumed
    to be a rigid structure" and the tire-pavement friction coefficient is
    **mu = 0.7**.

    **ROUGHNESS IS EXPLICIT GEOMETRY, NOT A PARAMETER.** Their Sec. III.D models
    "micro-protrusions" as actual pavement relief, and the water film "entirely
    fills up to a 1 mm line above the peak of the highest roughness". The physical
    result is that on a rough pavement the tread load is shared between fluid and
    protrusions so dynamic water pressure falls, whereas on a smooth pavement the
    film carries all of it.

    **WHY IT DOES NOT TRANSFER, and this is the load-bearing part.** Their domain is
    a water film **0.3 m long by 0.22 m wide and 0.2 to 1.0 mm thick**, around a
    205/55R16 tire of 0.64 m diameter at 25.7 to 30.4 m/s. To resolve a 1 mm film
    and sub-millimetre texture their cell size must be a fraction of a millimetre.
    This project's domain is **9.42 m with dx = 0.147 m at g64**, three orders of
    magnitude coarser, and a road texture depth of a few millimetres is under
    1/50th of one cell. **Pavement-as-material-points with resolved roughness is
    therefore not available at this project's scale**, and the handoff's expectation
    that this paper would answer B2 is not met. It establishes that MPM CAN host a
    real road; it does not show how to do so when the road is 60 times longer than
    the cell.

    **WHAT DOES TRANSFER, three things.** (a) The multi-material contact framework
    is an architecture alternative to our grid-BC plane, and it is the same family
    register A-1 already pointed at via Hu et al 2018. (b) Pavement as a rigid body
    rather than a boundary condition is validated practice. (c) A contrast worth
    stating in the paper: they use the **REAL sound speed c_0 = 1480 m/s** with a
    Grueneisen equation of state (rho_0 = 1000, s = 1.92, gamma_0 = 1.2, their
    Table I) and did NOT reduce the bulk modulus, where this project runs a reduced
    modulus giving c = 12.85 m/s. Both are legitimate; item 22 already records that
    ours sits below the 10x criterion, and this is a live example of the other
    choice being affordable at small scale.

    **A THIRD NUMBER FOR TIRE-ROAD FRICTION, AND THE LITERATURE DOES NOT AGREE.**
    Their mu = 0.7 (rolling tire on pavement, hydroplaning context) against Nihei et
    al's measured 0.30 locked and 0.0242 free-rolling (item 29) against this repo's
    unsourced 0.55. Three papers, three values, spanning a factor of 29. Any paper
    text quoting a tire-road friction coefficient must say which condition it means.

32. **THE RESERVE POOL IS IMPLEMENTED, AND ITS KEY CLAIM IS TESTED RATHER THAN
    ASSERTED.**

    `simulation/openchannel_bc.py` gains `ReservePool`, the piece item 30 identified
    as the blocker: spare particles held out of the flow so inflow can differ from
    outflow, which is what Zhao et al's NON-UNIFORM case needs and what one-in-one-out
    recycling cannot express. Eight self-tests.

    THE HONEST DIFFICULTY. Particle volume is fixed at load, so a parked particle
    still carries h^3 of fluid and still deposits mass on the grid wherever it sits,
    and there is nowhere in a warpmpm domain that is truly outside the simulation:
    the edge guard forbids parking near the boundary, and parking below the floor or
    outside the walls still writes to nodes. The park is therefore a pinned block
    placed far from the wetted region, and the claim that it is inert is a
    **falsifiable control, not an assumption**:

        a reserve that is never drawn from must reproduce the no-reserve run.

    `--reserve-hold` runs exactly that. **JOB 918500 HAS RUN AND BOTH ANSWERS ARE
    BELOW.**

    **THE CONTROL: INERT LATE, NOT INERT EARLY, AND THE "PASS" IS WEAK.**

    | quantity | A reserve=0 | B held | delta |
    |---|---:|---:|---:|
    | q_first  | 0.1726 | 0.1394 | **-19.3%** |
    | q_last   | 0.0430 | 0.0425 | -1.0% |
    | Fr_late  | 0.665  | 0.661  | -0.6% |
    | ratio    | 1.290  | 1.469  | +13.9% |

    The late-time quantities agree to within 1 percent, so a settled parked block is
    effectively inert. The EARLY discharge does not: q_first differs by 19.3 percent,
    which is the parked block settling onto the grid before the pin takes hold. And
    the ratio comparison nominally passes only because B's RUM95 is 0.2275 at n_eff
    5.0, a band wide enough to hide most disagreements. **Record this as "inert after
    the transient, not established during it", not as a clean pass.** The fix, if the
    pool is kept, is to pin from before the settle phase rather than from frame 0 of
    the run.

    **THE TREATMENT: THE POOL DRAINED AND THE DEPTH STILL COLLAPSED.**
    Drawn 67467, retired 27467, **starved 164626**, active at the end 40000 of 40000.
    The pool was completely empty and 164626 further draw requests went unmet. Inlet
    depth against a 0.350 m target: 0.2582 over the first 30 frames, **0.0833** over
    the last 30, which is exactly the 2*dx fallback floor, i.e. no standing water at
    the inlet at all. q_last/q_first is 0.29 against the baseline's 0.25, so the
    discharge decay is essentially unchanged.

    **WHY, and it is a design fault not a physics result.** Retirement is triggered
    by the same fall test as the outflow, so a drawn particle only returns to the
    pool after traversing the channel and going over the brink, which takes on the
    order of 100 frames. Draws ran at 536 per frame initially. The pool therefore
    emptied in roughly 75 frames and could never refill fast enough. Adding 40000
    particles to a 94656-particle scene, 42 percent more water, still did not hold
    the target depth.

    **WHAT THIS MEANS. The reserve pool is not the fix on its own.** It is
    mechanically correct, its instrumentation is what made the failure diagnosable
    (a hidden starvation counter would have left this looking like an unexplained
    null), and it remains necessary for a non-uniform boundary condition. But the
    discharge decay is not a shortage of particles. Item 30 attributed it to the
    recycling closure; that is now too narrow. **Even with an independent supply the
    channel does not hold depth**, which points at the outflow side: water leaves
    over the brink faster than any inlet condition tried so far can replace it, and
    the free-overfall geometry may simply be the wrong first validation case for a
    domain this size. A uniform channel with a pressure-controlled outlet, Zhao's
    other case and Remmerswaal's prescribed-traction machinery (item 31), is the
    cheaper target and should be tried first.

    One more measured detail worth keeping: run C is the only one of the three that
    passes the stationarity test, at Fr 0.375 and ratio 0.803. It is the most
    subcritical and the furthest from Rouse's 1.4, 43 percent below. Holding depth
    with an inlet supply moved the flow AWAY from the target, not toward it.

33. **LS6 NOW RUNS warpmpm, PINNED TO VISTA, AND IT HOLDS 15.5x VISTA'S REMAINING
    BUDGET. THE x86 ARCHITECTURE ALSO RETIRES NOTE L-8 ON THAT MACHINE.**

    Measured live 2026-08-18: **Vista 616 SUs on aarch64, LS6 9,539 SUs on x86_64**
    with no venv, no engine and no warpmpm. Vista is close to exhausted. Standing
    the stack up on LS6 is therefore worth more than any single physics change, and
    `scripts/ls6_setup.sh` now does it reproducibly.

    **THE PINS ARE THE POINT.** Left alone, pip installs warp-lang **1.16.0** on LS6
    while Vista runs **1.15.0**. A cross-machine comparison across two solver
    versions is not a cross-machine comparison, and the mismatch is silent. All
    three versions are pinned to values measured on Vista the same day: warp 1.15.0,
    torch 2.11.0+cu128, mpm-engine **627367e**.

    That engine SHA is VISTA'S working-copy HEAD and is **not** the SHA this repo
    vendors (`third_party/mpm-engine-544c93dd`). The setup script matches Vista on
    purpose, because the immediate goal is reproducing Vista's numbers. The
    vendoring discrepancy is still unresolved and is not closed by this item.

    **L-8 DOES NOT APPLY ON LS6.** That note fixed the engine decision on the
    grounds that DualSPHysics ships x86-only static libraries, a hard aarch64
    blocker on GH200. LS6 is x86_64, so the blocker is absent there and the decision
    was never re-examined for it. **And the literature does not independently confirm
    the blocker even for aarch64**: a deep search found no source establishing that
    the package is intrinsically x86-only today, nor any documented ARM-host CUDA
    build failure (item 34). L-8 may rest on one local build attempt. Re-test rather
    than inherit it.

    Two traps, both hit: `module load python/3.12.11` does NOT change what `python3`
    resolves to on LS6, so use `/opt/apps/python/3.12.11/bin/python3`; and
    `scripts/tacc.sh` refuses commands containing destructive verbs, which is
    correct and which left an orphaned 3.9.7 venv at `$WORK/.venv312` on LS6.
    LS6 also exposes **gpu-h100** alongside gpu-a100 and gpu-a100-dev.

    **CORRECTED 2026-08-18, SAME DAY, BY DIRECT READ OF BOTH MACHINES. THE ENGINE
    PIN IN THIS ITEM IS FALSE AND WAS NEVER ACHIEVABLE.** This item says all three
    versions are pinned to Vista's, "warp 1.15.0, torch 2.11.0+cu128, mpm-engine
    627367e". The first two are true and were re-verified. The third is not.
    `git rev-parse HEAD` on each machine returns LS6
    `544c93dd02cb9c7ead89e1155a62967243244fce`, on `main`, clean, never moved; Vista
    `627367ecc0d022b366f825b1c3f60c37f286f1e2`. **`627367e` is one of five commits
    Vista holds above its own upstream**, so it does not exist in a public clone and
    `git cat-file -t 627367e` on LS6 returns "NOT PRESENT". The checkout in
    `scripts/ls6_setup.sh` could not have succeeded and the script has been corrected
    to pin 544c93dd, which is what is actually reachable.
    The delta is **one file**, `src/warpmpm/vehicle.py`, +126/-10, carried by fd390d6
    and b43c3a2. 544c93dd is an ancestor of 627367e, so this is a gap, not a fork.
    **`solidify_watertight` is ABSENT from 544c93dd**, confirmed by grep against
    `third_party/mpm-engine-544c93dd/src/warpmpm/vehicle.py`. See item 37 for what
    that costs. The line "the vendoring discrepancy is still unresolved" is now
    resolved in the opposite direction from the one this item assumed: the VENDORED
    SHA is what LS6 runs, and Vista is the outlier.

34. **THREE DEEP SEARCHES: WHAT THEY SETTLED, AND THREE GAPS THAT ARE
    CONTRIBUTIONS RATHER THAN OVERSIGHTS.**

    **TIER: T2 THROUGHOUT. Added 2026-08-18, one session late.** Every bullet in this
    item is an Undermind deep-search synthesis, which is the same evidence class this
    register already tiers T2 at E6a, G1a and G4a ("T2, external report `<id>`"). It is
    NOT T1: nothing here was read off a primary source by this project. The item was
    originally written in the same voice as the measured items 26 to 33, which is the
    exact failure the register's line-8 standing rule exists to prevent.

    **AND THE NEGATIVE CLAIMS ARE WEAKER THAN T2.** "The ten-times sound-speed rule has
    no primary derivation", "no published speed-depth map exists", "no crowned-road
    comparison exists" and "no surrogate preserves a discrete threshold" are claims of
    ABSENCE from a retrieval, not from an exhaustive search. Per this project's own
    claim-discipline rule, absence of evidence from a partial view is not evidence of
    absence. Write them as "not found by four deep searches covering 243 papers",
    never as "nobody has done this", and never in a paper's novelty sentence without a
    named primary-source check. Item 36 records the framework that says the same thing
    in the V&V literature's own vocabulary.

    Launched 2026-08-18 into the `Can it ford` Undermind workspace after an audit
    found the previous prompt asked about a stationary vehicle only, inferred gaps
    from tag counts rather than content, and ignored compute. 48, 47 and 56 papers.

    **SETTLED, so stop re-deriving these.**
    - *Wheel contact for a moving vehicle*: Wasfy et al 2015 resolve suspension,
      wheels, steering, axles, drivetrain and both tire/ground and tire/fluid
      contact with penalty and asperity friction. Mazhar et al 2018 give the
      integrator, half-implicit symplectic with a cone-constrained solve. Pazouki
      et al 2016 apply distributed point-cloud FSI forces.
    - *An open-source moving-vehicle precedent exists*: Canelas et al 2018 extend
      **DualSPHysics with Project Chrono's differential variational inequality
      solver** and it is explicitly open source. Combined with item 33 this is
      buildable on the machine that has the budget.
    - *Scaling*: multi-GPU MPM reaches 100 million particles on 4 GPUs and 134
      million on 8. A 10 to 50 million particle flooded roadway is comfortably a
      SINGLE-NODE job. Stop treating it as a multi-node problem.
    - *The ten-times sound-speed rule has NO primary derivation in the retrieved
      literature.* Item 22 measures this project against a convention, not a
      derived criterion. Say so wherever it is cited.
    - *Open-boundary machinery for particle methods exists*: characteristic,
      buffer, pressure and traction outlet formulations are published, with
      Tafuni et al 2018 (GPU SPH open boundaries) and Negi et al 2019
      (non-reflecting outlet for weakly compressible SPH) the two most directly
      usable for the unsolved outlet in item 32.

    **THREE GAPS. Each is a result, not a hole to be filled by reading harder.**
    1. **No published speed-depth map for a self-propelled vehicle ENTERING water.**
       Existing work parks a vehicle in a flow or prescribes a trajectory. This is
       the project's stated target and it appears to be unoccupied.
    2. **No study reports the same vehicle-in-floodwater case in two independent
       solvers with the force-coefficient disagreement.** Existing vehicle studies
       compare one solver against experiment or against other CFD. A warpmpm
       versus DualSPHysics-Chrono comparison would be new.
    3. **No crowned or cambered road has been compared against a flat plane** for a
       vehicle stability threshold. A 5 percent grade study exists, and terrain
       slope appears in conceptual models, but the flat-versus-shaped comparison
       does not. That makes the road-geometry work already in this repo novel
       territory rather than catch-up.

    **AND ONE NEGATIVE THAT SAVES EFFORT.** Graph-network surrogates trained on MPM
    rollouts report 5 percent trajectory error and 5000x speedup, but on granular
    and obstacle problems, and **no retrieved work demonstrates a surrogate
    preserving a discrete threshold or classification outcome**. This project's
    output IS a discrete verdict. Do not build the surrogate expecting it to carry
    the verdict; if it is built, the burden is to show threshold preservation, not
    trajectory accuracy.

    Also measured, and directly relevant to item 29's friction question: full-scale
    tests on concrete, gravel and sand find materially different friction
    coefficients and recommend a worst-case value, but **no retrieved study
    quantifies the error from substituting an effective roughness for resolved
    roughness**, which is exactly the substitution this project's cell size forces.

35. **THE LS6 CROSS-MACHINE REPRODUCTION, WITH THE TWO CAVEATS THE RUN ITSELF
    REVEALED AND THE ONE THE LITERATURE IMPOSES.** T1, artifacts committed at
    `data/ls6_reproduction_2026-08-18/`, regenerated from the raw driver summaries
    on 2026-08-18 rather than transcribed.

    LS6 job 3372943 (gpu-a100-dev, x86_64 A100) against the Vista `leak_full` run
    (aarch64 GH200), warp 1.15.0, torch 2.11.0+cu128, identical arguments.
    **THE ENGINES WERE NOT THE SAME AND THE FIRST VERSION OF THIS ITEM SAID THEY
    WERE.** LS6 ran 544c93dd, Vista ran 627367e; see item 33's correction. What
    rescues the comparison is not the pinning, it is that the entire engine delta is
    `vehicle.py` and **this run has no vehicle**: both summaries carry
    `vehicle_key: None`, `vehicle_mass_kg: 0.0`, `n_carved: 0`, and
    `n_total == n_water == 50176`. `sim_channel.py:45` does import that module, so
    the delta is inert by CALL GRAPH, not by import graph. State it that way. **45 fields compared: 17 integer counts all identical; 16 scalar
    floats, 14 bit-exact; 12 depth bins, 0 bit-exact.** Worst relative difference
    **1.852e-05**, on `late_depth_slope_m_per_m`; the bins are tighter at 2.991e-06.
    Divergence is confined to quantities accumulated over 90 frames, the expected
    signature of non-associative summation under a different parallel decomposition.

    **CAVEAT 1, THE DRIVERS WERE NOT THE SAME.** The pins covered engine, warp and
    torch. They did not cover `sim_channel.py`. The LS6 summary carries five fields
    Vista's does not (`n_image`, `image_clamped_total`, `image_duplicated_last`,
    `image_sources_last`, `floor_plane`), so the LS6 copy post-dates the Vista run.
    The claim "any difference is the MACHINE, not the software" was true in effect
    but false as written. It survives on a CHECK, not on the pinning: `n_image` is 0
    and all three image counters are 0, so the added path produced no particles.
    Pin the driver too, or record its hash, before the next cross-machine claim.
    Note the pattern: THREE separate things were assumed matched and only two were,
    and in both misses the saving grace was that the differing code was never
    executed. That is luck twice, not method. The next comparison should assert
    inertness up front rather than discover it afterwards.

    **CAVEAT 2, THE FIRST COMPARISON WAS WRONG AND NEARLY SHIPPED.** It printed
    "6 of 6 identical" while silently skipping every float, because the consolidated
    artifact had been re-keyed (`free_surface_slope_m_per_m`) away from the driver's
    own name (`late_depth_slope_m_per_m`). The second attempt then compared genuinely
    unrelated fields, `sound_speed_ms` against `mach_margin` and `substeps` against
    `n_grid`. **A comparison that skips the quantities most likely to differ is worse
    than no comparison**, because it returns a pass. Compare raw driver output to raw
    driver output; if a consolidation step renames keys, it must carry the mapping.

    **CAVEAT 3, AND IT BOUNDS WHAT THIS BUYS. Cross-architecture agreement is
    evidence of ROBUSTNESS, NOT of physical validity.** That is the V&V literature's
    position, not an internal hedge: rounding growth and parallel-reduction ordering
    alter trajectories without any physics changing (Senoner et al 2008,
    `10.2514/1.34862`; Gopalakrishnan et al 2021,
    `10.1109/Correctness54621.2021.00007`). See item 36. This reproduction licenses
    "LS6 may carry work comparable to Vista's". It licenses nothing about whether
    either machine's answer is right.

    **SCOPE.** 90 frames only. **ANSWERED BY ITEM 39, and the answer is that it does
    grow: superlinearly, roughly as frames^2.8, and at 300 frames FIVE of the 17
    integer counts stop matching.** Never quote "17 of 17 identical" without "at 90
    frames" attached. It remains 265x inside the RUM95 band at these record lengths,
    so no verdict is threatened, but the exactness claim is record-length-specific and
    this item as first written did not say so.

36. **HOW COMPUTATIONAL SCIENTISTS ACTUALLY AUDIT WORK LIKE THIS, AND WHAT IT SAYS
    ABOUT RESULTS THIS PROJECT ALREADY HOLDS.** T2, Undermind deep search
    "how computational researchers audit and defend simulation credibility",
    2026-08-18, 92 papers. Tier and negative-claim caveats of item 34 apply here too.

    This is the search that should have been run first, because it is the only one of
    the four that changes how the EXISTING results get written up rather than what to
    compute next.

    - **Credibility is a context-of-use claim, assembled from separate evidence about
      code correctness, solution accuracy, model adequacy and uncertainty. It is not
      conferred by agreement with one benchmark.** Oberkampf and Trucano 2002
      `10.1016/S0376-0421(02)00005-2`; Roy and Oberkampf 2011
      `10.1016/J.CMA.2011.03.016`; Riedmaier et al 2020 `10.1007/s11831-020-09473-7`.
      This directly supports CLAUDE.md item 6, "no gate is a physics validation",
      from outside the project rather than from self-inspection.
    - **Richardson extrapolation and GCI are defensible only in an asymptotic
      refinement regime. A non-monotone quantity should be reported as numerical
      UNCERTAINTY, not reduced to significant figures.** Roy 2010 `10.2514/6.2010-126`;
      Celik et al 2007 `10.1115/1.2960953`. The g48/g64/g96 `final_disp_mag_m`
      non-monotonicity (CLAUDE.md item 5) therefore already has the right treatment,
      "cite the verdict, never the displacement magnitude", and now has a citation
      for why that is correct practice rather than evasion.
    - **For a binary verdict, the defensible object is a robustness or
      failure-probability statement over record length, friction and resolution, and
      threshold-based validation relates comparison error to DISTANCE FROM THE
      ENGINEERING THRESHOLD.** Hariharan et al 2017 `10.1371/journal.pone.0178749`.
      `analysis/probabilistic_verdict.py` already computes the right shape of object;
      this is the framework that licenses reporting it as the primary result instead
      of as a robustness appendix to a deterministic 16 SLIDE / 1 STUCK.
    - **A correlated finite record must carry sampling uncertainty.** Oliver et al
      2012 `10.1063/1.4866813`. This is the missing citation for the measured
      N_eff of 2.9 to 11.0 across all 25 runs (CLAUDE.md, 2026-08-15), which is
      currently an internal measurement with no external support.
    - **A benchmark at a different physical scale supports only PARTIAL validation
      unless a hierarchy of simpler shared-physics tests links it to the target, and
      extrapolation uncertainty is an open problem.** Oliver and Moser 2014
      `10.1016/j.cma.2014.08.023`. This is the governing frame for validating a
      full-scale hull against 1:10 scale experiments.
    - **No universal minimum evidence standard for particle methods has been
      adopted.** Brannon et al 2011, no DOI,
      `https://www.semanticscholar.org/paper/a1110387f396ff2323bd21373a1de6e3d7ae97c5`.
      A credible weakly-compressible case normally combines manufactured solutions and
      order tests, boundary-condition verification, conservation and stability checks,
      refinement, and validation of the coupled physics: Negi and Ramachandran 2021
      `10.1063/5.0072383`; Vacondio et al 2020 `10.1007/S40571-020-00354-1`.
      **This project currently has none of the manufactured-solution tier.**
    - **Provenance expected with a result**: versioned code, inputs, parameters,
      environment, hardware and parallel settings, workflow, output provenance.
      Leipzig et al `10.1016/j.patter.2021.100322`. Item 35's caveat 1 is exactly the
      "hardware and parallel settings plus versioned code" clause failing in practice.
    - **Two documented traps this project is exposed to.** Agreement for the wrong
      reasons, Berg et al 2018 `10.1002/cnm.3150`, which is the named failure mode for
      gate G-3 comparing against `RHO_REF` derived from the same pipeline. And
      underestimated iterative error, Eca et al 2020 `10.1115/1.4047922`.
    - **Null and self-refuting results are strongest reported as sensitivity,
      uncertainty and decision-boundary findings, not buried.** Easterling 2001
      `10.2172/780290`. This project has accumulated an unusual number of
      self-refutations (items 27, 30, the withdrawn 8.2 percent, the settle-transient
      reversals). That is a reportable pattern under this frame, not an embarrassment
      to be compressed.

37. **LS6 CANNOT REPRODUCE ANY OF THE 17 GATED VEHICLE RUNS, AND THE REASON IS THREE
    COMMITS THAT EXIST ONLY ON VISTA'S LOCAL DISK.** T1, read live 2026-08-18 from
    both machines plus a grep of the vendored tree.

    LS6's engine is 544c93dd. The seeding function `solidify_watertight` is not in
    it: `grep -rn "def solidify_watertight"
    third_party/mpm-engine-544c93dd/src/warpmpm/vehicle.py` returns nothing. It is
    introduced by b43c3a2, which sits with fd390d6 and the merge 627367e among the
    **five commits Vista holds above its upstream**. `git ls-remote` cannot see them;
    they are not on GitHub in any form.

    **WHY THIS IS LOAD-BEARING AND NOT A VERSION-SKEW FOOTNOTE.**
    `solidify_watertight` is what produces the canonical hull fill and density: it
    superseded the old column-fill path, giving fill_ratio 1.0023 and rho 309.78
    against the retired 2.17 / 143 figures, and 310.494 kg/m^3 is the number CLAUDE.md
    carries as the canonical Yaris effective density. An LS6 vehicle run on 544c93dd
    would seed the hull by the OLD path and silently produce a different density,
    which is exactly the class of difference no gate in `gates.py` can catch, because
    G-3 compares against a `RHO_REF` derived from the same pipeline (CLAUDE.md item 6,
    and the "agreement for the wrong reasons" trap in item 36).

    **SO THE LS6 CAPABILITY CLAIM MUST BE SPLIT.** Item 33 says LS6 "runs warpmpm".
    Precisely: LS6 can run **water-only** cases faithfully, which is what job 3372943
    demonstrated and all the open-channel work needs. It **cannot** run the vehicle
    scenes, and the 15.5x budget argument does not transfer to vehicle work until the
    commits move. Do not queue a vehicle sweep on LS6 on the strength of item 33.

    **TWO WAYS TO CLOSE IT, NEITHER DONE, BOTH NEEDING A DECISION.**
    (a) Push the three commits from Vista to the `jcerrell-IS/mpm-engine` fork, then
        fetch on LS6. Durable, and it also removes a single-copy risk: those commits
        currently exist in exactly one place.
    (b) `git bundle create` on Vista, scp to LS6, fetch from the bundle. No public
        write, fully reversible, but leaves the single-copy risk standing.
    **RESOLVED 2026-08-18, SAME DAY, AND THIS ITEM'S DIAGNOSIS WAS WRONG.** Neither
    (a) nor (b) was needed, because **there was no single-copy exposure.**
    `git ls-remote` against `jcerrell-IS/mpm-engine` returns
    `627367ecc0d022b366f825b1c3f60c37f286f1e2  refs/heads/main`. The commit was on
    GitHub the whole time. This item said "they are not on GitHub in any form". False.

    **HOW THE ERROR WAS MADE, because it is the interesting part.** The "five unpushed
    commits" figure came from `git log @{u}..HEAD` on Vista. `@{u}` is VISTA'S OWN
    CACHED TRACKING REF and it points at `00bbfb1`, which is stale. CLAUDE.md's
    repo-clone-inventory rule states this exact trap: do not test provenance by asking
    a clone about its own cached remote ref, resolve the canonical SHA from the LIVE
    remote first. The rule was in front of me and I used the cached ref anyway. Two of
    the five "unpushed" commits, `544c93d` and `49a098a`, are Krishna's and were public
    upstream already.

    **THE REAL ROOT CAUSE WAS THE REMOTE, NOT THE SHA.** `scripts/ls6_setup.sh` cloned
    UPSTREAM `kks32/mpm-engine`, whose main is `544c93d` and which does not carry this
    project's engine work. Pointing LS6 at the fork and fetching fixed it in one step.

    **LS6 IS NOW AT 627367e, VERIFIED BY EXECUTION, NOT BY CHECKOUT EXIT CODE.**
    `rev-parse HEAD` returns the full SHA; `grep -c "def solidify_watertight"` returns
    1; and `from warpmpm.vehicle import solidify_watertight` imports and is callable
    under the pinned warp 1.15.0 / torch 2.11.0+cu128 venv. So the split-capability
    claim above is **withdrawn**: LS6 can now run the vehicle scenes, and the 15.5x
    budget argument does transfer. `ls6_setup.sh` now clones the fork and pins the full
    40-character SHA rather than a short one.

    A bundle of Vista's engine history was created anyway and verified complete
    (913,301 bytes, `git bundle verify` reports a complete history). It is redundant
    for recovery and is kept only as a cheap second copy.

38. **SINGLE-COPY EXPOSURE: 45 LOCAL BRANCHES HAVE NEVER BEEN PUSHED, AND THE
    LARGEST CARRIES 83 COMMITS.** T1, measured live 2026-08-18 with
    `git for-each-ref` and `rev-list --count origin/main..<branch>`.

    87 local branches. **45 have no upstream at all**, so they exist on one laptop
    and nowhere else. Twelve or more carry commits unreachable from `origin/main`,
    led by `claude/r5-research` at 83, `claude/r5-physics` at 73,
    `claude/r5-safekeeping` and `claude/r5-exposure` at 47 each, and the current
    `claude/add-ci-checks` at 41.

    Read this together with item 37, where five mpm-engine commits including the
    canonical `solidify_watertight` seeding exist only on Vista's `$WORK`, and with
    the standing note that `~/can-it-ford-demo` `4d228d9` is single-copy. The project
    is not one backup away from being safe; it is many.

    **A CAVEAT THAT MATTERS BEFORE ANYONE "HARVESTS" A BRANCH.** The plan to harvest
    `claude/fork-three-class` cites "85 files and 3,565 insertions". Re-measured, that
    matches neither available reading. Three-dot against merge-base, which is the one
    that answers "what does this branch ADD", gives **23 files and 3564 insertions**.
    Two-dot gives 92 files, 3582 insertions and **26,459 DELETIONS**. Those deletions
    are the point: the branch is an OLD fork, not a superset, so a naive merge or
    cherry-pick would revert work that is on the current branch. Harvest the 23 files
    deliberately, never by merging the branch wholesale, and re-measure before quoting
    any figure, stating which of the two readings you used.

    **CORRECTED AND CLOSED 2026-08-18, SAME DAY. THE COUNT WAS WRONG AND THE FIX IS
    DONE.** "45 never pushed" was measured with `%(upstream)`, which reports whether an
    upstream is CONFIGURED, not whether the commits exist remotely. A branch can be
    fully published and still have no upstream set. Re-measured the right way, by
    resolving the 46 live `origin` refs with `ls-remote` and then asking whether each
    local tip is an ancestor of any of them: **38 branches carry commits not reachable
    from any live remote ref**, not 45. Same class of error as item 37's, made twice in
    one session, both times by trusting a local cache instead of the live remote.
    Also corrected: `claude/can-it-ford-round-5-87a6d6`, the Job B branch, **is** on
    origin at `fbecf5d` and was never at risk.

    **CLOSED WITHOUT ANY REMOTE WRITE.** `git bundle create --all` captured **167
    refs** and verifies as a complete history. It was copied to LS6 `$WORK` and the
    sha256 matches byte-for-byte on both ends
    (`787eea16686bc0a1987e67a0f3234db7599ded564d529bcd84dcbeccb4ff373c`), so all 167
    refs now exist on two machines. Permissions set to 600 so the shared TACC
    filesystem does not expose it to the group.
    A bundle sitting next to the repo on the same laptop would NOT have closed this;
    the off-machine copy is the part that does.

    **WHY BUNDLE RATHER THAN PUSH, on evidence.** `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`
    was scanned on both the working tree and the branch for live secret values, by
    pattern rather than by eye: `ghp_`, `github_pat_`, `olp_`, `sk-`, `AKIA` and
    40-hex forms all return **zero**. It documents exposures by path and type, never by
    value, so nothing live would have leaked. It is still a map of where credentials
    were, and publishing a map on a PUBLIC repo is a bad trade when a bundle closes the
    same risk at zero disclosure. The bundle also covers all 38, including that one,
    which a selective push deliberately could not.

39. **THE CROSS-MACHINE DIVERGENCE GROWS WITH RECORD LENGTH, AND THE INTEGER COUNTS
    STOP MATCHING. ITEM 35's "17 OF 17 IDENTICAL" IS RECORD-LENGTH-SPECIFIC AND DOES
    NOT GENERALISE.**

    Item 35 reports the LS6/Vista water-only reproduction at 90 frames: all 17
    integer quantities identical, worst relative float difference 1.852e-05. I
    measured that at ONE record length and reported it without testing whether it
    held. It does not. LS6 job 3373051 repeats the identical configuration at 300
    frames against Vista's `long_grade0p0`:

    | quantity | Vista GH200 | LS6 A100 | delta |
    |---|---:|---:|---:|
    | driven_total          |   48129 |   48127 | **2** |
    | recycled_total        |   48129 |   48127 | **2** |
    | clamped_y             |  183393 |  183417 | **24** |
    | clamped_z             | 2253695 | 2253410 | **285** |
    | leaked_particle_frames| 2412228 | 2411952 | **276** |

    **Five of 17 integer counts now differ**, where at 90 frames none did. The worst
    relative float difference goes **1.852e-05 to 5.242e-04, a factor of 28.3**,
    while the record only grew 3.33x. So the divergence accumulates FASTER than
    linearly in frame count. Two points is not a law, but the direction is not in
    doubt and the growth is clearly superlinear.

    **IT IS STILL FAR BELOW WHAT THE MEASUREMENT CAN RESOLVE.** The absolute slope
    delta is 3.390e-06 against item 30's RUM95 of 0.00090 on that quantity, so the
    two machines disagree **265x inside the uncertainty band**. No verdict is
    threatened at these record lengths. A crude extrapolation of the observed
    exponent (about frames^2.8) puts the divergence at the RUM95 near 2000 frames,
    which is worth knowing before anyone runs one, and is an extrapolation from two
    points and should be treated as such.

    **WHAT TO SAY, AND WHAT NOT TO SAY.** Say: at the record lengths used here the
    two machines agree far inside the measurement uncertainty. Do NOT say the
    reproduction is exact, and do not quote "17 of 17 identical" without "at 90
    frames" attached. Item 36 already establishes the frame that matters: cross
    architecture agreement is evidence of ROBUSTNESS, not of physical validity,
    precisely because rounding and parallel reduction order alter trajectories. This
    item is that mechanism showing up in the project's own numbers.

    **ONE CONFOUND, AND IT IS MINE.** The two runs did NOT use the same driver
    version. The LS6 summary carries `n_image`, `floor_plane`,
    `image_sources_last`, `image_duplicated_last` and `image_clamped_total`; the
    Vista run predates the image-particle work and carries none of them. The LS6 run
    used `n_image = 0` and `floor_plane = True`, which is the same physics path, so
    the comparison is defensible but is NOT a clean matched pair. A rerun of the
    Vista side on the current driver would remove the doubt and has not been done.
    Recording it because an unstated version difference is exactly the kind of thing
    that makes a reproduction claim collapse later.

40. **THE PARKED RESERVE IS NOT INERT, AND PINNING CANNOT MAKE IT INERT. MY OWN FIX
    IS REFUTED BY THE CONTROL I WROTE FOR IT.**

    Item 32 recorded the reserve-hold control as a weak pass and blamed the 19.3
    percent early-discharge disagreement on `pin_parked` running once BEFORE the
    8-step settle loop, so the parked block free-fell through settling. Commit
    ad6f169 pinned it inside the loop and stated the falsifiable form: if the
    early-time disagreement does not shrink, the park is not inert for a different
    reason and the design needs rethinking rather than retuning.

    **IT DID NOT SHRINK. IT DID NOT MOVE AT ALL.** Job 918731, same configuration:

    | quantity | before fix | after fix |
    |---|---:|---:|
    | q_first  | **-19.25%** | **-19.25%** |
    | q_last   | -1.01%  | +0.25%  |
    | Fr_late  | -0.60%  | +0.53%  |
    | ratio    | +13.91% | +17.16% |

    q_first is identical to four significant figures across the two jobs while other
    quantities moved by a few percent, so the runs are not trivially identical and
    the fix genuinely had no effect on the discriminator. The deployed file was
    checked and did carry the change.

    **WHY, and it is obvious in hindsight.** The per-frame pin already runs on frame
    0 of the main loop, so wherever the block fell to during settling, it was put
    back before the first measured frame. The settle-phase fall was transient and
    self-correcting. **The perturbation is from the block's PRESENCE, not its
    motion**: 40,000 particles carrying h^3 of fluid each, suspended in the domain,
    deposit mass and exert pressure on the grid for the whole run. Pinning holds them
    still; it does not make them weightless.

    **THE CONSEQUENCE FOR THE DESIGN.** To be inert the reserve would have to be
    genuinely outside the computational domain, and item 21 establishes there is no
    such place in warpmpm: the edge guard forbids the boundary, and any interior
    location deposits mass. So a spare-particle reservoir cannot be made
    non-perturbing in this engine by any host-side means. Item 30's route to a
    sustained discharge is therefore closed as stated, and the remaining candidates
    are the open-boundary formulations item 34 names (Tafuni et al 2018, Negi et al
    2019) or a genuine pressure/traction outlet, none of which need a reservoir.

    **THE CONTROL STILL CANNOT DISCRIMINATE, and that is worth keeping.** B's RUM95
    on the ratio is 0.2277 at n_eff 5.0, unchanged. The comparison "passes" on the
    ratio for the same bad reason as before. What carries this item is q_first and
    the 33-of-37 bit-exact agreement on everything else, not the ratio.

    **ONE STALE DIAGNOSTIC, fix before it misleads someone.**
    `water_count_conserved` reports **False** for every reserve run. It tests
    `len(s.x()) == n_water`, which is false by construction once n_reserve > 0. It is
    a pre-reserve check that was never updated, not a conservation failure. Nothing
    was lost: `analysis/summary_compare.py` surfaced it only because that tool
    refuses to skip non-numeric fields.

41. **THE MANUFACTURED-SOLUTIONS TIER IS BLOCKED BY EXACTLY ONE MISSING API, AND THE
    FIX IS ONE KERNEL.** T1, read live 2026-08-18 against
    `third_party/mpm-engine-544c93dd-solver-core/`, plus T2 from Negi and
    Ramachandran 2021 `10.1063/5.0072383` read from the arXiv v2 full text.

    Item 36 recorded that this project has no manufactured-solution or
    order-of-accuracy tier, which the V&V literature treats as baseline evidence for a
    particle method. This item says what it would actually take.

    **MMS IS NOT SPH-SPECIFIC.** The paper's own statement of the requirement is that
    it be possible to add an arbitrary source term to a particular equation. Nothing
    else about the method is tied to SPH, so "we run MPM, not SPH" is not a reason to
    skip it. Manufacture a solution, take the residual as a source, add it, sweep the
    spacing, fit the order from an L1 error.

    **CORRECTED WITHIN THE HOUR, BY A 22-AGENT ADVERSARIAL PASS THAT REFUTED ME.
    EVERYTHING BELOW HEADED "THE BLOCKER" IS WRONG, AND WRONG IN THE EXPENSIVE
    DIRECTION: IT SAYS THE THING IS BLOCKED WHEN IT IS NOT.**

    **MMS NEEDS NO ENGINE CHANGE.** `kernels/mpm_solver_warp.py:1182-1188` is a launch
    loop over `self.pre_p2g_operations`, firing each registered Warp kernel at
    `dim=self.n_particles` with `inputs=[self.time, dt, self.mpm_state,
    self.impulse_params[k]]`. A user-supplied kernel appended there computes
    `q(x, t)` analytically from `state.particle_x[p]` and the `time` argument, which
    is precisely the spatially and temporally varying momentum source MMS requires.
    A subagent applied `b(x,t) = A sin(kx) cos(wt)` through this path and measured the
    response live on CPU, so this is executed, not read.

    **WHY I GOT IT WRONG, because the mechanism generalises.** I grepped `def set_` on
    the typed facade `core/solver.py`, plus a handful of force-shaped names, found
    nothing, and reported absence. The capability is not on the facade, it is on the
    simulator class underneath. That is the project's own standing rule broken in one
    step: absence of evidence from a partial view is not evidence of absence, and I did
    not say which view I had searched.

    **WHAT IS ACTUALLY TRUE, and it is narrower.** The *documented* injector,
    `add_impulse_on_particles` (`:2385`), cannot express `q(x)`: its kernel applies one
    uniform `param.force` divided by particle mass over an axis-aligned box mask
    (`:2419-2423`). So "the documented API cannot do MMS" holds. "The engine cannot do
    MMS" does not, and that is the claim that was load-bearing.

    **TRAP IN THAT EXTENSION POINT.** `pre_p2g_operations[k]` and `impulse_params[k]`
    are INDEX-PAIRED at the launch site. Appending a kernel without a matching param
    entry raises `IndexError`. `particle_velocity_modifiers` is a separate list pair,
    so mixing the two stays aligned only by care.

    **AND THE F CLAIM BELOW IS ALSO WRONG.** `import_particle_F_from_torch` exists at
    `:1658` and does write `particle_F`, so "export-only, no setter" (inherited from a
    DeepWiki answer, never checked live) is false. The real constraint is subtler:
    `compute_stress_from_F_trial` runs first in each substep and reads
    `particle_F_trial`, not `particle_F`, so an imported F is overwritten before it can
    reach the stress update on some material paths. Manufacture in velocity, not in F.

    **PySPH'S ANSWER TO ITEM 32 IS ALSO OVERSTATED BELOW.** Its inlet/outlet case is a
    SUBMERGED bluff body at Re 200. It is not a free-surface outlet, so its
    applicability to item 32's actual problem is NOT ESTABLISHED. The underlying
    formulation is Negi, Ramachandran and Haftu 2020, CMAME 367:113119, which is absent
    from the 332-paper corpus (a grep for `113119` returns zero), so nobody here has
    read it. Adopting the design is a REIMPLEMENTATION, not a port: the IOM hands SPH
    kernel interpolation equations to a scheme object warpmpm does not have, and the
    typed API exposes no grid accessor at all, only particle-level and collider-level
    ones, so the ghost-particle extrapolation would have to be done host-side in numpy
    and written back through `set_x` and `set_v`. Say that fidelity gap out loud.

    **CHEAPEST NEXT ACTION FOR ITEM 32, AND IT COSTS NO SU.** The register already
    names the mechanism as loop latency. Test it: at `simulation/sim_overfall.py:254`
    retirement uses the SAME fall predicate as the outflow (`catch_z`, passed at
    `:198`, implemented as `fallen = w[:, 2] < self.catch_z` at
    `openchannel_bc.py:381`), so a drawn particle only returns to the pool after
    crossing the whole channel. Decouple retirement from the outflow test and rerun.
    Both outcomes are results. And do NOT blame `draw_cap`: it is computed once outside
    the frame loop at `:197`, giving 800 per frame against an observed 536, so it never
    engaged.

    **SUPERSEDED TEXT FOLLOWS, RETAINED ONLY SO THE ERROR IS AUDITABLE.**

    **THE BLOCKER, NAMED.** warpmpm has no per-particle or per-node source term. The
    complete host-side setter list on `core/solver.py` is `set_material`,
    `set_material_range`, `set_box`, `set_cup`, `set_sdf_pose`, `set_cdf_pose`,
    `set_x` and `set_v`. The only body force is `set_gravity`
    (`kernels/mpm_solver_warp.py:811`), which assigns a **single global `wp.vec3`**
    and is consumed at grid level in `grid_normalization_and_gravity`
    (`kernels/mpm_utils.py:928`). A valid manufactured solution must vary in space and
    time, so gravity cannot carry it. The deformation gradient is export-only, with no
    setter, so a solution cannot be manufactured in F either.

    **THE OBVIOUS WORKAROUND IS A TRAP.** One could read velocity, add `dt * s_u`, and
    write it back through `set_v` each step. That is operator splitting, it is
    first-order in the splitting, and it would contaminate the very second-order
    result the exercise exists to measure. Do not do this and then report an order.

    **THE CLEAN FIX IS SMALL.** Gravity is already applied per grid node in
    `grid_normalization_and_gravity`. A source term belongs in the same place: one
    additional array of per-node source values and one kernel that adds it alongside
    gravity. That is a scoped engine change, not a redesign, and it is the single
    thing standing between this project and a real verification tier.

    **ONE CONSTRAINT THAT DOES NOT BITE.** warpmpm fixes particle count at load and
    cannot add or remove particles. Negi and Ramachandran hit the same issue and
    resolve it with iterative particle shifting rather than insertion or deletion, so
    the fixed count is compatible with the method as published.

    **THREE EMPIRICAL RESULTS FROM THAT PAPER, EACH WORTH A SWEEP.** A
    divergence-free manufactured field FAILS to show second order, because the initial
    divergence error is not captured, so use a non-solenoidal field. At least 100
    timesteps are needed before the measured order is trustworthy, after which it stops
    depending on the initial particle configuration. And a packed, not perturbed,
    configuration is what tests discretisation robustness. Boundary conditions get
    their own manufactured solution by multiplying by `(C - F)^m`, m = 1 for Dirichlet
    and m = 2 for Neumann. Source terms are generated symbolically with sympy rather
    than hand-coded.

    **AND A SOUND-SPEED WARNING THAT LANDS ON THIS PROJECT.** The authors needed
    `c_o = 80 m/s` on Taylor-Green to demonstrate second order, against `20 m/s` for
    their MMS cases. Achievable order is sound-speed dependent. This project runs
    `12.85 m/s`. Whatever order a future suite measures must be reported WITH the
    sound speed it was measured at, or it will not be comparable to anything.

    **SEPARATELY, PySPH ANSWERS ITEM 32.** Ramachandran et al 2021
    `10.1145/3460773`, section 3.4.2, implements a full `InletOutletManager`: ghost
    particles, interpolation equations, a stepper, and a callback converting
    inlet/outlet particles to fluid and back. Section 4.3 exercises it on flow past a
    cylinder at Re 200 and reports lift 1.524 and drag 0.722 within 5 percent of
    reference, Strouhal 0.2 within 2 percent. That is a working, quantitatively
    checked outlet, which is what item 32 has been unable to build. It is BSD-3 and
    pure Python with runtime code generation, so it also carries none of the
    architecture-specific static libraries that note L-8 used to rule out DualSPHysics
    on aarch64. The paper tests no ARM, so that is absence of the known blocker and
    not a port report; say it that way.


## ADDENDUM 2026-08-18, MERGED FROM `claude/fork-register-reconcile`

The three items below were **items 17, 18 and 19 on `claude/fork-register-reconcile`**, written
2026-08-13. `claude/add-ci-checks` independently continued Section J's numbering to 17, 18 and 19
for unrelated g128 content on 2026-08-18, so the two lineages collided on three identifiers. The
`add-ci-checks` numbering is preserved above and these three are renumbered 42, 43 and 44. They are
placed here, rather than back in Section J, so that numeric order and file order agree for a reader
scanning for an item by number. Full working, including the entry counts of both inputs and of this
file, is in `docs/R8_REGISTER_MERGE_2026-08-18.md`.

**These three are dated 2026-08-13 and are therefore OLDER than items 17 to 41 above, despite
carrying higher numbers.** The number records identity, not chronology. In particular item 44 says
"the canonical set does not exist at g128" is now answered; item 17 above reports that it does.

42. **NEW 2026-08-13. THE g64 SETTLE GATE IS NON-DETERMINISTIC AT FIXED CONFIGURATION, AND THERE ARE THREE SEPARATE NON-DETERMINISMS IN THIS PROJECT THAT MUST NOT BE MERGED.** Written up since 2026-08-07 but never registered, so it kept being re-discovered. Engine is **warpmpm** throughout this item.

    **NUMBERING: this was item 42 on `claude/fork-register-reconcile`, and is item 17 here.** It was renumbered at the 2026-08-18 merge because `claude/add-ci-checks` had independently used 17 for unrelated g128 content, and that numbering is the one already cited in the wild (`CLAUDE.md` cites J15 and J16; `origin/claude/add-ci-checks` is public). Renumbering the public side would have silently repointed existing citations; renumbering this side breaks nothing, because `claude/fork-register-reconcile` has never been pushed and nothing outside it cites its 17. **Every cross-reference to "item 17" in this file was repointed to 42 in the same pass; the sub-labels moved with it.**

    **(a) THE ONE THIS ITEM ADDS: the ladder's g64 settle gate is a coin flip.** `docs/REGIME_LADDER_RESULTS_2026-08-07.md` section 5.5, job `895653`: three settle phases with identical code, identical geometry and identical `seed=0` gave three different outcomes. `ladder_b_g64` and `ladder_c_g64` both hit the 1200-frame cap with the gate **not met**; `ladder_d_g64` met it at **974** frames. `settle_vmax_final` 0.865234 / 0.861557 / **0.594807**, against a `settle_vmax_peak` identical to four decimals (2.0488) in all three. Same peak, divergent tails. Independently reproduced 2026-08-12 at three seeds in `docs/FLOOR_FRICTION_RUNG_2026-08-12.md` section 3: of six g64 arms **only one settled** (`fric_c_g64_mu000_s2`), failing for all three `mu=0.55` seeds and two of three `mu=0.0` seeds. **Operative rule: no single g64 arm of this ladder is quotable, including the arms in the 2026-08-07 table.** A changed verdict on a g64 arm is not evidence of changed physics. g96 is not affected: it met the gate in every arm, at the `min_frames` floor of 20, with `settle_vmax_final` 0.352205 / 0.352217 / 0.352215, differing only in the fifth decimal. Mechanism is consistent with non-deterministic atomic accumulation in P2G. **This bears on item 15**: the g128 canonical test prescribed there should be run at g96 and above, or repeated at several seeds if any g64 arm enters the comparison, or the settle draw will be confounded with the refinement effect.

    **(b) NOT THE SAME THING: unseeded mesh sampling.** `docs/limitations_B9a_scaling_and_solver.md` section 5. `load_vehicle` computes the vehicle-frame shift from `mesh.sample(60_000)`, which is unseeded, so the vehframe transform, the solid particle count and therefore the effective vehicle density are not bit-reproducible for mesh inputs. **Measured magnitude for the canonical hull is negligible**: the residual against the stored `npz["extent"]` is 2.030e-07 m, **0.43 float32 ulp** at 4.28 m, below the storage precision of the value it perturbs, and it did not move the discretization. Real defect, report it, add a seed upstream, but do not cite it as the cause of (a): different mechanism, different stage, and four orders of magnitude smaller.

    **(c) NOT THE SAME THING AND NOT EVEN THE SAME ENGINE: the `grid_density` crash boundary.** Section C2 of this register, `gd` 80 and 88 passing 3/3 while `gd` 90+ fails, non-monotone and non-deterministic at fixed config. **Section C is Genesis-specific and says so in its own heading; it does not apply to warpmpm.** Do not cite C2 as support for (a).

    Cost of merging them: (b) would make (a) look like a negligible float-precision artifact, and (c) would attribute a warpmpm result to Genesis. Both errors have already been made once in session notes.
43. **NEW 2026-08-13. THE "TWO INDEPENDENT RESOLUTION-DEPENDENCE FINDINGS" ARE ONE FINDING, AND THERE IS NO CONFLICT TO RESOLVE.** Registered because a dispatch was written to reconcile them and the reconciliation would have manufactured agreement between a claim and itself. A 2026-08-13 RTFD session report listed, as needing deliberate reconciliation, (i) "a Silverado sweep showing margin collapse 6.9x to 1.5x from g64 to g128" and (ii) "commit `ed8bf8e`'s separate surge-instrument-based finding, reached a different way." Verified live by `git log -1 --format=%B ed8bf8e`: **the commit body IS that sweep.** Its part 1, "THE ROGUE/SILVERADO SWEEP, PUT THROUGH THE REAL CLASSIFIER", tabulates `rs_silverado_g64` `ratio_slide` **6.9669**, `rs_silverado_g96` **1.8105**, `rs_silverado_g128` **1.5557**, which is the 6.9-to-1.5 collapse attributed to the other finding. Cross-checked against the primary store `data/rogue_silverado_slide_classification_2026-08-13.csv`: identical values, and the g96/g128 rows carry one `source_job`, 3362208 on LS6 A100. Part 2 of `ed8bf8e` is the **surge instrument** (`simulation/validate_coupling_force_ladder.py` gaining COM and velocity 3-vectors), which is a measurement tool, not a second finding about the SLIDE verdict. **Reading a commit's two parts as two independent corroborating results is the specific failure here**, and the report's own preamble names the likely cause: its source RTFD capture contained a duplicated block, "content from roughly the back half reappears nearly verbatim." **Standing consequence: one commit is one source, however many sections it has, and a claim plus the tool that measured it is not two-source corroboration.** Item 15 is unaffected and remains the open item: the direct g128 canonical test still has not been run.

    **NUMBERING: this was item 43 on `claude/fork-register-reconcile`, and is item 18 here.** It was renumbered at the 2026-08-18 merge because `claude/add-ci-checks` had independently used 18 for unrelated g128 content, and that numbering is the one already cited in the wild (`CLAUDE.md` cites J15 and J16; `origin/claude/add-ci-checks` is public). Renumbering the public side would have silently repointed existing citations; renumbering this side breaks nothing, because `claude/fork-register-reconcile` has never been pushed and nothing outside it cites its 18. **Every cross-reference to "item 18" in this file was repointed to 43 in the same pass; the sub-labels moved with it.**

    **43a. PHRASING CORRECTED 2026-08-14 DURING THE THREE-WAY REGISTER RECONCILIATION, AND THE CORRECTION THIS ENTRY WAS GIVEN WAS ITSELF WRONG. Read this before quoting item 43.** Two separate defects, one in item 43 and one in the instruction to fix it.

    **(i) "ONE FINDING IN ONE COMMIT" IS THE WRONG UNIT. The right unit is ONE MEASUREMENT.** Item 43 above locates the sweep in `ed8bf8e`'s body and stops there, which invites the reading that any *other* appearance of those numbers is a second source. It is not. Enumerated live 2026-08-14, the same measurement has **four write-ups**: (1) the `ed8bf8e` commit body; (2) `docs/SESSION_TRACK1B_2026-08-13.md:230-235`, the same table; (3) register item 15 itself, which reports the same runs through different columns, 0.0778 m and 1.56x rather than `ratio_slide`; and (4) the primary store `data/rogue_silverado_slide_classification_2026-08-13.csv`. **Write-ups 2 and 3 are the SAME COMMIT**, `1a868f3`, which touched exactly two files. **So the register is itself one of the write-ups, and an entry in this file quoting a measurement does not make the register a second source for it.** That is the sharper form of item 43's rule and the one to quote.

    **43a(iv). THREE AND FOUR ARE BOTH DEFENSIBLE, AND A BARE NUMBER IS THE DEFECT. Reconciled 2026-08-14 after an adversarial review found a competing count already committed.** While this reconciliation was running, commit **`54aa806`** (2026-08-14 17:15:40 +0200) landed independently on `claude/rtfd-test-phase-1-4-569130` making the *same* correction to item 43 and reaching **three** write-ups: `ed8bf8e`'s body, `SESSION_TRACK1B_2026-08-13.md:233-235`, and the CSV store. This entry reaches **four**, adding register item 15. **Neither session knew of the other**; `fe95f13` (17:31:54) declared the overlap from that side. Both independently refuted the same false dispatch premise (`b62d554`, "44 minutes before"), by the same method, and agreed on `1a868f3` and on 19 minutes after.

    **The two counts differ on exactly ONE binary scope choice: does a register entry that reports a measurement count as a write-up of it?**

    | scope choice | count |
    |---|---|
    | exclude the register's own entry | **3** (`54aa806`) |
    | include it | **4** (this entry) |

    **The inclusion is an identity, not a judgement call, verified live 2026-08-14.** Item 15 reports "max drift at g128 is 0.0778 m, still 1.56x `slide_m`". From the primary store, `rs_silverado_g128` carries `max_surge_drift_m` **0.07778644561767578** and `ratio_slide` **1.5557289123535156**, and `0.07778644561767578 / 0.05` **is** `1.5557289123535156` exactly. Item 15 is the same measurement in a different column. **On the merits four is the more complete count, and three under-counts by omitting the register's own entry** — a bad one to omit, given that this item exists precisely to stop the register being read as independent corroboration of a number it merely quotes.

    **But the operative rule is the one CLAUDE.md's DRIFT_THRESHOLD item already establishes: never quote the total without its scope.** That item records 22/23/23/24 as all defensible on two independent binary choices. Write "four write-ups, counting the register's own entry" or "three, excluding it". **Do not write a bare number, and do not treat 3 and 4 as a contradiction needing adjudication: they are one measurement counted under two stated scopes.**

    **AND NOTE WHAT JUST HAPPENED, because it is the third recurrence.** Item 43 is about miscounting sources. Its own fix miscited its evidence (43a(ii)). Its fix has now been **counted two different ways by two sessions working in parallel**, each unaware of the other, both writing into the file CLAUDE.md calls the sole authority. `54aa806` recorded the second recurrence in its own words, "Item 18's own failure mode recurred inside the fix for item 18". **The quotation is left verbatim as it stood, so the two "item 18" inside it are `claude/fork-register-reconcile` numbering and mean THIS item, 43. Two notes from the 2026-08-18 merge, which read `54aa806` live: its closing words are actually "because it is item 18's own failure mode recurring inside the fix for item 18", so the tense here is altered and this is a paraphrase rather than a quotation; and the commit body itself is numbered against that branch, not against this file.** **This is the third. A correction is not exempt from the defect it corrects.**

    **(ii) THE CORRECTION HANDED TO THIS RECONCILIATION IS REFUTED ON ALL THREE OF ITS COMPONENTS.** The dispatch instructed: correct item 43 because the same table "also appears in `docs/SESSION_TRACK1B_2026-08-13.md:233`, added by **`b62d554`**, **44 minutes EARLIER**" than `ed8bf8e`. Tested directly rather than accepted, 2026-08-14, by walking every commit that has ever touched that file and grepping each one's own blob for `6.9669`:

    | | claimed | live |
    |---|---|---|
    | commit that added the table | `b62d554` | **`1a868f3`** |
    | direction | 44 min **before** `ed8bf8e` | **19 min 15 s AFTER** |
    | `b62d554`'s own copy | contains the table | **163 lines, ZERO occurrences of `6.9669`** |

    `b62d554` (2026-08-13 05:23:47) created the file but cited a **different** store, `data/rogue_silverado_grid_sweep_2026-08-13.csv`, 8 rows. The table first appears at `1a868f3` (06:54:07), against `ed8bf8e` at 06:34:52. Intermediate commits `8590313` and `5e0f764` also carry zero. **The conclusion "three write-ups, one measurement" was right; every fact offered in support of it was wrong, and the true count is four.** Recorded at length because this is item 43's own failure mode recurring one level up: a correction to a sourcing error, itself asserted rather than derived, and it would have entered the register as verified had it not been re-run. `git blame` alone is not sufficient here either, since it attributes only the last commit to touch a line; the decisive test is per-commit content.

    **(iii) ITEM 43'S CLOSING SENTENCE WAS ALREADY STALE ON ITS OWN BRANCH, 50 MINUTES AFTER IT WAS WRITTEN.** It ends "the direct g128 canonical test still has not been run." Item 43 landed in `e431877` at 17:40:26; **item 44, recording that the test HAS been run for the mass sweep, landed in `a6e42c1` at 18:30:42 on the same branch.** The sentence is retained above unedited so the sequence stays auditable. **Superseded by item 44, scope-limited: the test is run for 3 of the 17 canonical configurations; the 3 `sweepD` and 5 `sweepV` runs, including the only STUCK run, still have no g128 counterpart, so item 15 stays open with its scope narrowed.**
44. **NEW 2026-08-13. ITEM 15's DIRECT TEST HAS NOW BEEN RUN FOR THE MASS SWEEP. NO VERDICT FLIPS, AND THE HEAVIEST ARM IS NOW 2.4 PERCENT FROM STUCK.** Engine **warpmpm**, material-8 free-rigid path. LS6 jobs **3362573** and **3362619** (independent repeat), both `COMPLETED 0:0` on `c301-001`, driver sha256 `4696c3b2`. Masses 1100/1609/2337 at g96 **and** g128 in the same job, because item 16 says the frozen g96 margins are unreproducible and item 42 says the stack is non-deterministic, so a cross-job control could not separate refinement from a run draw. Full working: `docs/G128_CANONICAL_FINDINGS_2026-08-13.md`; store `data/g128_canonical_slide_classification_2026-08-13.csv`.

    **NUMBERING: this was item 44 on `claude/fork-register-reconcile`, and is item 19 here.** It was renumbered at the 2026-08-18 merge because `claude/add-ci-checks` had independently used 19 for unrelated g128 content, and that numbering is the one already cited in the wild (`CLAUDE.md` cites J15 and J16; `origin/claude/add-ci-checks` is public). Renumbering the public side would have silently repointed existing citations; renumbering this side breaks nothing, because `claude/fork-register-reconcile` has never been pushed and nothing outside it cites its 19. **Every cross-reference to "item 19" in this file was repointed to 44 in the same pass; the sub-labels moved with it.**

    **44a. THAT DRIVER IS NOT THE ONE THAT RAN THE 17, AND ONLY THIS MERGE MAKES IT VISIBLE. Noted 2026-08-14 at the three-way register reconciliation.** Item 44 stamps its runs `4696c3b2` and stops; **D8c's table identifies `4696c3b2` as the 2026-08-08 revision, 564 lines, and the driver that produced the 17 gated runs as `5215c38b`, 389 lines**, preserved at `renders/yaris_render_s1/_incoming/sim_standing.py` and evidenced by an on-node `00_provenance.txt` sha. Verified live 2026-08-14 that the two facts were on **different branches and neither cited the other**: the branch carrying item 44 names `4696c3b2` once and `5215c38b` never; the branch carrying D8c names both and never mentions item 44. **WHAT IS NEW HERE IS THE IDENTIFICATION, NOT THE EXISTENCE OF A DRIVER CHANGE. Stated precisely so this is not over-read.** Item 44 already lists "a driver and engine-checkout change" alongside Vista GH200 to LS6 A100 when it explains the **-4.79 percent** g96 gap, so it is not unaware that the driver moved. What it does not say, and could not, is **which** driver: it names `4696c3b2` and never names `5215c38b`, so nothing in item 44 or on its branch reveals that the driver it ran is a **different program from the one that produced the 17**. That identification only exists once D8c is readable beside it. **Consequence: do not describe the g128 canonical runs as having used the canonical driver.** Two further consequences: D8c's line-number warning applies to item 44's driver in the `:210-211` sense, not the `:132-133` sense; and per D8c the two contents are **not** the same program (188 added and 13 modified lines, including a `fill_ratio` denominator change), so "same driver, finer grid" is not available as a description of this comparison either. **Untested and worth stating as open: whether any part of the g96-arm discrepancy is attributable to the driver change rather than to venue.**

    **44b. ITEM 44's EVIDENCE IS NOT REACHABLE FROM THIS BRANCH. Stated inline 2026-08-14 because a reader consults the register, not a session's side notes.** `docs/G128_CANONICAL_FINDINGS_2026-08-13.md` ("full working"), `data/g128_canonical_slide_classification_2026-08-13.csv` ("store") and `analysis/classify_g128_canonical.py` **do not exist on `main` or on this branch**; verified live, `git ls-tree main -- <path>` is empty for all three. They exist only on `claude/rtfd-test-phase-1-4-569130`, force-added past `.gitignore` precisely because item 16 records six canonical margins becoming permanently unverifiable when a job overwrote its run directories. **So item 44's numbers are currently checkable only by someone with that branch.** This is a consequence of reconciling the register file alone, not a defect in item 44. **Until those branches merge, cite item 44 with that caveat attached.** The same applies to `docs/FLOOR_FRICTION_RUNG_2026-08-12.md`, `docs/FRICTION_RESOLUTION_RECONCILE_2026-08-13.md`, `docs/FRICTION_RUNG_HORIZONTAL_INSTRUMENTATION_2026-08-13.md` and `simulation/coupling_validation/rung_e_floor_friction.py`, which D8/D8b/D8c cite and which live only on `claude/friction-resolution-reconcile-84465d`.

    **RESULT: all three stay SLIDE at g128.** So the Silverado flip does NOT reproduce on the Yaris mass sweep. **SCOPE, and it must be stated every time: this is 3 of the 17 canonical configurations.** The 3 `sweepD` and 5 `sweepV` runs, including `sweepV_g64_v0p5`, the only STUCK run, still have **no g128 counterpart**. These are also new runs; a canonical verdict cannot flip, only a replication of it can.

    **THE FINDING IS THE MARGIN, NOT THE VERDICT.** `g128_m2337` has `margin_frames` **0**: it meets the joint condition on frames 6, 7 and 8 and nowhere else, a single run of exactly the 3 required. **Quote `k_crit` beside it or the closeness is mis-scaled**: g96_m2337 is `k_crit` 0.8721, needing **12.8 percent** weakening to flip, while g128_m2337 is **0.9759**, needing **2.4 percent**. **DO NOT QUOTE THAT 2.4 PERCENT AS A PRECISION STATEMENT: `k_crit` has a measured run-to-run spread of 19 to 26 percent on comparable cells, so 2.4 sits an order of magnitude inside the noise. See item 15a(g); `margin_frames` is the stable statistic.** The binding frame has `|dx|` 0.05124 against `slide_m` 0.05.

    **CORRECTION TO A FIRST READING OF THIS RUN, recorded because it is the exact trap item 5 warns about.** An initial pass called it "the lighter masses strengthen with refinement, only the heaviest weakens." That is WITHDRAWN: it read two points where four exist. The full ladder is m1100 6.9142 / 13.3068 / 5.3854 / 9.4704 (+92.5, **-59.5**, +76.3 percent) and m1609 5.0211 / 6.4287 / 3.1323 / 3.5580 (+28.0, **-51.3**, +14.5). Both **oscillate**, and m1100's +76.3 has the same sign and near magnitude as its g48-to-g64 step that the next refinement reversed. **Only m2337 is monotone across all four grids**, -21.6 / -36.6 / -14.1, which is the defensible claim and the stronger one. Cite **Steffen, Kirby and Berzins 2008** (G/L-5): particles-per-cell is constant at 8 here (`h = dx/2`, `sim_standing.py:163`), exactly that paper's case.

    **AL-QADAMI 2023 VERIFIED AGAINST PRIMARY SOURCE, AND IT IS A WRITE-UP PRECEDENT, NOT CORROBORATION. Imported 2026-08-14 from `54aa806` on `claude/rtfd-test-phase-1-4-569130`, which landed after the `658ecfa` snapshot this reconciliation merged from; carried across so the reconciled register is not missing verified content that exists on a source branch.** Project notes name it as the mesh-independence precedent for a flood-vehicle result, but it is absent from the 115-row research corpus manifest, so it was being carried as UNVERIFIED. Retrieved via Scite full text: **Al-Qadami et al. 2023**, *Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D CFD Modelling*, `10.3390/su151713262`, *Sustainability* 15(17):13262, gold OA CC-BY, **no editorial notice**, tally 2 total / 0 supporting / 0 contrasting. The mesh-independence study is **confirmed verbatim**: "The mesh-independent study was performed by testing a total of four mesh blocks with cell sizes of 0.1, 0.075, 0.05, and 0.025 m", with 0.05 m selected on three stated criteria.

    **RE-VERIFIED INDEPENDENTLY VIA SCITE FULL TEXT 2026-08-14, AND THE IMPORTED SUMMARY WAS INCOMPLETE ON THE POINT THAT MATTERS MOST.** The DOI, title, journal (*Sustainability* 15(17):13262, MDPI), 2023, gold OA CC-BY, **no editorial notices**, and tally 2 total / 0 supporting / 0 contrasting all reproduce. **"0.05 m was selected" is not the whole setup, and quoting it alone inverts the lesson.** Full text: *"It was found that the mesh block with a cell size of 0.05 m could not c[apture] model details accurately. Therefore, a **nested mesh block** was defined with 0.025 m to only capture the vehicle domain."* So the converged choice was **0.05 m for the fluid domain plus a nested 0.025 m block on the vehicle** — they needed **2x finer resolution on the body than on the flow**. **This is the most transferable thing in the paper for this project** and it was missing from the imported summary: the canonical scene resolves the water depth at 2.000 cells (L-3) and resolves the hull at the same `dx` as the flow, with no nested refinement available, since the warpmpm grid is forced cubic and uniform.

    **The convergence is quantified, which strengthens the contrast this item draws.** Full text: cell sizes 0.100 and 0.075 m gave "a noticeable difference", while **0.05 and 0.025 m agree to "an average percentage difference of 1%"**. So their study converged to a stated 1 percent band and selected on it. Item 5's g48/g64/g96 ladder is non-monotone and item 44's four-grid ladder oscillates, with no band of any width. **Quote the 1 percent beside our non-convergence; it is the sharpest available statement of the gap.**

    **G5 IS UPHELD AND NOW HAS A DIRECT QUOTE.** Full text: *"One vehicle model called Peruodu Viva was chosen to represent a medium-sized Malaysian passenger vehicle."* (the paper's own spelling of Perodua). So **this paper is a Perodua Viva, not a Yaris**, exactly as G5 says, and G5's misattribution warning stands against this DOI specifically. Two cautions that follow. (a) The paper reports floating at **0.38 m**, which is close enough to the "**0.40 m** Yaris" figure G5 forbids that **0.38 m is the likely origin of that misattribution**; treat any "≈0.4 m float depth" attributed to a Yaris as this Perodua Viva result until proven otherwise. (b) **The paper is internally inconsistent about vehicle class**, calling the Viva "medium-sized" in its own methods while its introduction describes the earlier Al-Qadami 2021 study of the same vehicle as "a small-size passenger vehicle". **Do not map this paper onto an AR&R class on the strength of the word "medium".**

    **THREE FURTHER VERIFIED NUMBERS THAT BEAR ON OPEN ITEMS IN THIS REGISTER, all from full text.** (1) **Blockage ratio 0.22**, defined as projected side area of the vehicle over frontal area of the domain, in a 10 m wide x 12 m long x 1.8 m high domain. **Section E item 13 records that nobody has computed ours and that blockage/afflux corrections are unreported across the whole incipient-motion literature (G1a); this is a published comparator to compute ours against.** (2) Their road **static friction coefficient is 0.30**, cited to **Bonham and Hattersley 1967 and Gordon and Stone 1973** — which is **exactly the pair G4b names as the source of the field's inherited 0.30 convention**, so this is not a stray choice by one paper but the convention being applied, and my first draft of this note called it merely "a different surface assumption", which undersold it. Against the gated `floor_friction` **0.55** (A7, G4, G4a, D8a). **Read G4, G4a and G4b before using either number**: 0.30 is refuted as a wet-road *measurement* and real as a *convention*, while 0.55 is a genuine measurement of a **lab rubber mat**, not of submerged asphalt. D8 shows this channel is decisive, so **never compare a sliding threshold across the two without naming both `mu` values and which of the two senses each one is.** (3) Engine and physics: FLOW-3D v11.2, FVM, k-epsilon turbulence, general moving object (GMO) model, coupled 6-DOF. **Engine tag: not MPM, not warpmpm.** **Two limits on how it may be used.** (a) The superlative in the project notes, that it is the field's ONLY such study, is **NOT verified** and must not be written down. (b) It is **FLOW-3D, finite-volume VOF**, not MPM, so Steffen 2008's fixed-particles-per-cell mechanism does not apply to it, and its converged cell-size selection neither corroborates nor contradicts this item's non-monotone MPM ladder. It is the model for how to REPORT a refinement study, and the contrast is the contribution: their study converged and selected a cell size, this one does not converge.

    **Two checks run on the import rather than accepting it, 2026-08-14.** The BibTeX is in-repo and matches the citation field for field, read directly at `docs/LIT_QUEUE_2026-07-30.md:276` (`@article{alqadami2023}`, *Sustainability* 15(17):13262, DOI `10.3390/su151713262`). And **it does not disturb G5**: G5 records that Al-Qadami tested a **Perodua Viva, not a Toyota Yaris**, which is a fact about the *vehicle*, while this import is about the *mesh-independence method*. Both hold. **Do not read this import as licence to cite Al-Qadami for any Yaris result** — per G5 the verified full-scale Yaris source remains Smith, Modra and Felder 2019, DOI `10.1111/jfr3.12527`.

    **REPRODUCIBILITY, MEASURED.** The repeat job shows all six `metrics.csv` differ between jobs at identical config, node and driver, **while every run's own `determinism_identical` flag reports True**; that flag does not detect this. But `margin_frames` is **identical in all six** and `ratio_slide` moves by **under 1 percent**. So `margin 1 -> 0` is reproduced, not a draw. **This settles a causal question**: the in-job g96 arms differ from the frozen store by -0.24, -0.79 and **-4.79** percent, and since same-node spread is under 1 percent, that 4.79 is **not** non-determinism. It spans Vista GH200 to LS6 A100 plus a driver and engine-checkout change. Never call it a non-determinism measurement. Separately worth noting: the least reproducible g96 arm is the most fragile one.

    **A GATE FAILS, ON THE ARM WITH THE LARGEST NUMBER.** `canon_g128_m1100` fails **P-2**, `passthrough_max_frac` **0.11159** against the 0.10 limit (`gates.py:146-148`), reproduced at 0.11155. That is the +76.3 percent arm. Treat it as containment-failed, not a result. The other eleven pass P-2 (0.0797-0.0944) and all twelve pass P-3.

    **CONFOUND CHECKED AND CLEARED, ONE WAY ONLY.** Realized depth is **exactly** invariant, 0.2944294473 m at both grids (3.000 and 4.000 cells), the same value item 5's g48/g64/g96 carry, and `grid_lim` is identical. **But the domain is not scale-invariant**: `wall = 4.0*dx` grows the tank side +2.27 percent, water volume +5.64 percent and fetch +2.61 percent from g96 to g128. Small against the 14-76 percent ratio changes, unbounded, so this is not a pure refinement. Bears on J13. The settle is also fixed-duration (`settle_frames = 8`), not gated, with residual velocity 2.4-2.9x larger at g96; do not call the initial conditions matched.

    **J15 STAYS OPEN, scope narrowed.** g192 costs about the same as this did (six runs, 6:15).

---

<!-- PORTED 2026-08-20 from claude/add-ci-checks, verbatim except the R9D- id
     prefixes, which were added on the source side first so both lineages carry
     the identical text. The two copies had diverged to 2232 and 3148 lines with a
     shared merge-base at 0efe4f3; this makes the r8 copy a superset, so the merge
     is a take-mine rather than a conflict. -->

## COORDINATOR CORRECTIONS, 2026-08-19, from the R9 cross-session readout section 5.4

Three rows in this register asserted things this register or a sibling had already
refuted. Recorded here rather than edited in place, so the retraction is visible.

**IDS RELABELLED 2026-08-20, AND THE COLLISION WAS DANGEROUS.** This section originally
wrote its three rows as `A2`, `B1` and `B7`. Those are ids from
`docs/R9_DISCREPANCY_REGISTER_2026-08-19.md`, and **all three collide with unrelated
canonical items in THIS file**, roughly 2,100 lines above:

| id | canonical item, this file | R9 discrepancy row, this section |
|---|---|---|
| A2 | **Gravity is -9.81 and was never unknown** | the corpus-index claim, retracted |
| B1 | two depth-resolution numbers, both correct for different engines | the corpus-skill item, closed |
| B7 | no pressure field exists anywhere in warpmpm | the 9.80665 item, re-scoped |

The A2 collision is the one that could do real damage: **"A2 is RETRACTED" sitting in the
same document as "A2. Gravity is -9.81 and was never unknown"** means a reader who quotes
"register A2 is retracted" reopens the gravity claim, which is precisely the claim item 15
spent two separate corrections killing. Every row below is therefore prefixed `R9D-` for
the register it actually comes from. Do not restore the bare ids.

**R9D-A2 is RETRACTED.** It read "None of these six papers is in the 332-paper corpus index.
`--query "Al-Qadami"` returns zero." Both halves are false. `--query` matched title and
abstract only and NEVER authors, so an author query could not succeed; d14-corpusbib fixed
it in `8bad9b4` and the same query now returns 5. Four of the six ARE in the corpus,
including `10.1111/jfr3.12828`. The coordinator withdrew this VERBALLY on a board row at
17:44 and never updated this file, which is exactly the failure this register exists to
prevent: the corrections authority served a claim its own author had withdrawn.

**R9D-B1 is CLOSED.** It was listed "OPEN, UNOWNED". It is closed on `r9-corpus-bib`
(`8bad9b4`) and on `add-ci-checks` itself (`faf53d1`), where the skill now reads
"DO NOT SAY 256 ARE CITED NOWHERE". The register listed as open an item its own branch
had fixed.

**R9D-B7 is RE-SCOPED, not open-unowned.** Fixed on `r9-settle` (`0861b52`, which reads 9.81
with a dated correction block). Still stale on the landing target, where
`classify_failure_modes.py:30` reads 9.80665. The row was right about the target and wrong
that nobody owns it.

## THE FALSIFIER RULE, 2026-08-19, from readout section 5.9

Eight instrument failures were found in one round, every one with the same signature:
**a code path that returns a value indistinguishable from a measurement when it could not
measure.** `stationarity.py` returning 0.0 where 0.0 is also the pass value; a
`grep -c ... || echo 0` producing "0\n0" so the integer comparison errored and fell to
else; `all([])` returning True over zero data; a two-arm control where both arms failed
because the branch did not exist; `--query` unable to match an author so zero was
unreachable rather than absent; a preflight that checks CLAUDE.md and silently ignores the
authority skill; `gh run view --json jobs` reporting `conclusion: success` on a step that
exited 1; and mesh acceptance checks passing watertight, edge-manifold and correct-bbox on
a mesh with one blob per particle. Six of the eight were caught by their own authors, all
after publication.

**RULE: any commit that adds a check must name, in the commit message, the input that
makes that check FAIL.** If no such input can be named, the check cannot fail and is not a
check. `analysis/r9_session_reader.py --self-test` demonstrates the cheap form: assert that
each guard fires, and assert a known limitation explicitly so a later "fix" cannot silently
remove the caveat.

---

## ADDENDUM 2026-08-20, FROM THE 13A LITERATURE AUDIT

Written by the session that executed section 13A of `docs/R9_SESSION_HANDOFF_2026-08-20.md`:
all 21 deep searches opened live, both workflow journals mined, the five unread audit
documents read. Full working in `docs/R10_JOURNAL_AUDIT_2026-08-20.md` and
`docs/R10_LITERATURE_IMPLEMENTATION_2026-08-20.md` on `claude/add-ci-checks`. Filed here
rather than on the integration branch because register rows belong here.

### R1. THIS REGISTER CONTRADICTS ITSELF ON `floor_friction`. T1, OPEN.

**Item 29 (2026-08-18) asserts `floor_friction = 0.55` IS UNSOURCED and that "nothing
sources it". Items G4a (2026-08-07) and the submitted paper both source it to a
spring-balance measurement by Azhar et al 2023.** Two rows of the same authority, opposite
verdicts, eleven days apart. Whichever is right, a reader hitting item 29 first will write
something the paper contradicts.

This sits on top of a bracket the R10 journal establishes: **AR&R's `mu = 0.30` is a
safety-factored DESIGN value carrying a documented 40 percent reduction from a physical
measurement, directly measured stationary flooded road-tyre friction is 0.85 to 1.15, and
Nihei et al 2025 measured the ROLLING RESISTANCE of an unbraked full-scale vehicle at the
moment of washaway at 0.0250 and 0.0242**, an order of magnitude below the `mu_s` near 0.30
every existing criterion assumes. So the physically relevant value spans **0.024 to 1.15**
depending on whether the vehicle is braked, rolling, or being washed away, and the gated
runs use 0.55, which is a lab rubber mat. G4b's distinction between 0.30 as convention and
0.30 as measurement is the right frame; extend it to name the regime as well as the sense.

**Owner: whoever reconciles item 29 against G4a. Do not change any run parameter on this.**

### R2. ITEM 4 LEG (a) HAS THREE COUNTER-ORIGINS, AND LEGS (b) AND (c) ARE UNTOUCHED. T1.

CLAUDE.md item 4 extension (a) states "It is not measured ... **No measured Yaris tensor
exists anywhere**: SAE 1999-01-1336 ends Nov 1998." Three independent origins now say a
measured 2010 Toyota Yaris inertia tensor and CG exist:

1. R10 agent `a2bcb1f09`, read-directly.
2. R10 agent `a25a0c14c`, read-directly, naming the address: **register E1's own document,
   DOI `10.13021/G8JS5D`**, which this project already cites as its hull provenance.
3. The `Simulation Ready Vehicle Mesh Assets` deep search, which records the CCSA/NCAC
   Yaris as carrying measured or calibrated mass and inertial properties and functioning
   suspension and steering, and the Camry as dismantled part-by-part with model mass and
   inertia checked against the production vehicle.

**THIS DOES NOT LICENSE WIRING INERTIA.** Item 4's legs (b) and (c) are untouched and are
independently sufficient: the solver already computes a better tensor from the real hull
particle cloud, and the documented axes are transposed against the gated scene, where a
naive write gives Ixx -69.2 percent and Iyy +379.2 percent. Only leg (a) is in question.

Corroborating from a different direction, the `Optical Vehicle Collision Geometry` search:
inertia errors materially affect 3-D trajectories, and pendulum-based mass-property work
cautions that **simple estimators are inadequate for accurate dynamics**, which is what
`box_inertia` is. That strengthens item 4's refusal by a route item 4 does not currently use.

### R3. THE AL-QADAMI DEPTH-VELOCITY THRESHOLD IS AMBIGUOUS BETWEEN TWO OF THEIR OWN PAPERS. T1.

`10.1111/jfr3.12828` (2022) gives critical depth 0.38 m and minimum D x V **0.39 m2/s**.
`10.3390/su151713262` (2023), same group, gives the **same 0.38 m** and a sliding threshold
of **0.36 m2/s**. The depth agrees exactly and the depth-velocity figure does not. **Never
quote an Al-Qadami D x V without naming the paper.** The 2023 paper additionally reports
drag DECREASING with Froude number and flow velocity, which runs against the intuition
behind this project's velocity sweep and should be read before that sweep is written up.

Also on Al-Qadami: the `moving vehicle floodwater GPU particle simulation` search records
that **their available record does not expose their motion algorithm or wheel model**, so
the 0.38 m cannot be reproduced from the paper.

### R4. `xiong2024` IS THE CLOSEST VALIDATED PRIOR ART AND BIBTEX DROPS IT. T1.

CLAUDE.md records that the shipped bibliography carries exactly one entry that is never
cited, `xiong2024`, so BibTeX does not print it. Acquired and read by the gapscan slot:
Xiong, Liang, Zheng, Wang and Tong 2024, *Water Resources Research* 60,
`10.1029/2023WR036739`, CC BY. It is "a new coupled model for simulation of entrainment,
transport and deposition of vehicles driven by and interacting with flood hydrodynamics",
and it is **used to reproduce a real flash flood event that moved over 100 vehicles, with
results consistent with post-event report and survey**.

So the one entry the paper carries and never cites is a vehicle-flood model validated
against a real multi-vehicle event. **That is a sourcing decision currently being made by a
BibTeX default.** Decide it deliberately.

### R5. THE WELL-POSEDNESS CLASSIFICATION OF THIS PROJECT'S OWN DOMAIN. T1.

Zhao, Bolognin, Liang, Rohe and Vardon's in/outflow rule, read from the PDF: "One of the
BCs must control the kinematics... If neither BCs controls the kinematics, the problem is
not well-posed." This project applies a per-frame Dirichlet velocity clamp on an upstream
particle slab inside a domain closed by slip walls. **That is kinematic control at inflow,
no outflow, and momentum injected every frame into a box mass cannot leave.** It belongs in
the paper's limitations as a classification, not as a hedge.

Two further facts from the same read. Their method **requires adding and removing material
points**, and this driver holds particle count fixed at load, so it is not a drop-in. And
their reference implementation carries **two mitigations this solver lacks**: a mixed Gauss
algorithm integrating at Gauss points for full elements and material points for partially
filled ones, and explicit strain and pressure smoothing to mitigate grid-crossing stress
oscillation.

### R6. A GATE THAT CAN FAIL FOR AN EXTERNAL REASON NOW EXISTS. T1, NEW.

Item 6 of CLAUDE.md's AUGUST 4 AUDIT records that no gate in this project is a physics
validation. `analysis/cm_floor_check.py` is the first that is not purely self-referential.
Method from Baumgarten, Couchman and Kamrin `10.1002/nme.7217` equation 73: for a fluid of
fixed volume above a floor, `z_cm >= z_bottom + (A_tank - A_hull)*depth/(2*A_tank)`. Runs on
`rollout.npz`, no GPU.

**Result on all 17 canonical runs: 11 violate over the full record, 4 survive the settle
transient.** The structure matters more than the count:

- **g48 x3 violate at FRAME 0 with ZERO particles below the clamp**, so it is the initial
  condition and not dynamics. Those are the same three runs item 7 flags for gate P-3.
  **Two gates now flag the same three, one internal and one external.**
- g64 baseline sits ON the bound, -0.0002 to +0.0003 m.
- The sweepV margin is **monotone in velocity**, -0.0035 m at 0.5 m/s to +0.0060 m at
  3.0 m/s, and the below-clamp fraction rises monotonically with it too, 0.5 to 4.6 percent,
  matching item 7's independently recorded P-2 rise across the same sweep.
- The three largest violations, at -0.20 of depth, belong to `m1100`, `m1609` and `m2337`,
  which are **NOT among the canonical 17**. The check reads membership from
  `data/all_runs_inventory.csv` so that split cannot be lost.

**A pass is not a validation**, it is a failure to falsify against a bound made conservative
four ways. And one unexplained observation, recorded not resolved: at g64 about 2300 to 2800
water particles sit below the `floor` scalar at frame 0, while at g48 and g96 the count is
zero. Nobody has read the initialisation path to explain a resolution-dependent difference
of that shape, and it should not be called a defect until somebody does.

### R7. TWO CLAUDE.md RULES AMENDED, RECORDED HERE SO THE REGISTER AGREES WITH THE CONSTITUTION.

- **L-4 is no longer a flat rule.** It said coarse resolution over-predicts peak force so
  over-threshold NO-FORD verdicts are conservative. Smith and Mack 2014, in WRL 2014/07
  section 6.3.2, found numerical models at 1 m, 5 m and 10 m grids **UNDER-predicting** peak
  local velocity around a building, against both a physical model and observed damage. This
  register's Section I already listed that exact sentence for deletion on sight, so the two
  documents disagreed. An under-predicted force makes a NO-FORD verdict LESS conservative.
- **L-8 keeps its decision and loses its reason.** "DualSPHysics ships x86-only static
  libraries, a hard aarch64 blocker on GH200" is not established: the deep search
  commissioned to test it returns that the literature neither confirms x86-only status today
  nor documents an ARM-host CUDA build failure, and Chrono::FSI-SPH builds on Vista aarch64
  in 94 seconds. Do not switch, and do not restate the premise as fact.
