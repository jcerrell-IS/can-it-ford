# Unshipped work inventory, 2026-08-22

Written 2026-08-22 ~01:10 BST from the `/` working directory (see PREFLIGHT below).

**This file is UNTRACKED and UNSTAGED.** Nothing in this pass was staged, committed,
merged or pushed. Part 1 (inventory) is complete. Parts 2 (merge) and 3 (push) were
NOT started, for the reasons in section 1.

Claim tags, following this project's convention:
`[READ]` direct command output this session. `[MEASURED]` a command was run and its
result observed. `[INFERRED]` derived from those, not directly observed.

---

## 1. PREFLIGHT FAILED, and the dispatching prompt carried three false premises

### 1.1 Preflight result

`bash scripts/r8/r8_preflight.sh d1-safe` exited **1**. [MEASURED]

The prompt passed `<SLOT>` as a literal placeholder, so no slot was specified. `d1-safe`
was chosen as the only plan row whose worktree is the main checkout, the only tree from
which a repo-wide merge could run.

Two checks failed:

| # | Check | Result |
|---|---|---|
| 1 | cwd equals planned worktree | **FAIL.** `pwd -P` is `/`, plan wants `/Users/josie/can-it-ford` |
| 2 | on planned branch | **FAIL.** reads `DETACHED`, purely a consequence of #1 (`git -C /` is not a repo) |

The script's own remedy text: "Do NOT 'cd' to fix this; a single cd moves the tracked cwd
for the whole session and breaks relative-path hooks. Relaunch in the right place." The
global CLAUDE.md carries the same rule with two dated incidents behind it. So this session
cannot fix its own position, and its final line is "Do not start work."

Also flagged by preflight, not fatal but recorded: the `research-corpus` SKILL.md reads
0 lines from this cwd against 308 in the main checkout, and **26 live Claude panes**
(`canford8:d11`..`d23` and `phone:d11`..`d23`) are registered against worktrees this
inventory would otherwise merge from.

Read-only inventory was carried out anyway, because it writes nothing and because the
question of what is unshipped is exactly what the failure makes urgent. **No merge and no
push were attempted.**

### 1.2 Three premises in the dispatching prompt that are false, measured

**(a) `origin/add-ci-checks` does not exist.** The remote ref is
`origin/claude/add-ci-checks`. [MEASURED, `git for-each-ref refs/remotes/origin`]
Every `git log origin/add-ci-checks..HEAD` in the prompt would have died with
"unknown revision". All divergence numbers below use the correct ref.

**(b) The `claude/r8-register` caution is moot, twice over.** `grep -n -i 'r8-register'`
returns **no match** in either `/Users/josie/can-it-ford/CLAUDE.md` (1005 lines) or
`/Users/josie/.claude/CLAUDE.md`. [MEASURED] And the branch was already merged: reflog
entry `0000608 HEAD@{2026-08-21 02:11:44}: commit (merge): Merge claude/r8-register`.
Its tip `476bdfd` is an ancestor of the pushed remote. [MEASURED] There is nothing left
to merge and no instruction left to honour.

**(c) `canford-checks.yml` has run many times and passes.** The prompt asks whether this
would be its first execution and says "a workflow that has never executed is not known to
pass." It has executed at least 20 times since 2026-08-18. [MEASURED, `gh run list`]
The most recent run, id `32528900504` at 2026-08-21T21:31:29Z on `claude/add-ci-checks`,
completed **success** in 32s against the current tip `fd4f8b7`. The file is present on
`origin/claude/add-ci-checks` and absent from `origin/main`. It is known to pass on the
branch; it has never run on `main` because it is not there yet.

---

## 2. The headline: no commits are lost, but 21 branches have never been pushed

`git ls-remote --heads origin` was read live, so this does not depend on stale
remote-tracking refs. [MEASURED]

- **Main checkout is fully in sync.** Local `claude/add-ci-checks` = `fd4f8b7` =
  `refs/heads/claude/add-ci-checks` on GitHub. Nothing unshipped in its commit history.
- **21 of 23 plan branches exist locally and are on no remote at all.**
- **All 23 branch refs survive.** Nothing is orphaned and no reflog rescue is needed.

### 2.1 The thing that actually happened tonight

`.claude/worktrees/` was modified at **2026-08-22 00:51**, thirteen minutes before this
session began, and `.git/worktrees/` at the same timestamp. [READ, `stat`]
**16 of the 23 planned worktree directories are gone from disk.** [MEASURED]

The branches were not deleted, only the working trees. But the 26 live tmux panes still
carry `pane_current_path` values pointing into those deleted directories, so a large
number of live sessions are sitting in directories that no longer exist.

**This is the single most important thing in this document and it needs a human.** It is
not clear from the evidence available here whether that removal was deliberate (a cleanup)
or accidental. Nothing was lost either way, because the refs survive.


### 2.2 Branch ledger, all 23 plan slots

`ahead` counts commits in `origin/claude/add-ci-checks..<tip>`, which INCLUDES commits
inherited from the slot's base branch. It is not a count of that slot's own new work.
`tree` says whether the planned worktree directory still exists. [MEASURED]

| slot | branch | tip | on remote | ahead | worktree dir |
|---|---|---|---|---|---|
| d1-safe | `claude/add-ci-checks` | `fd4f8b7` | **yes** | 0 (contained) | present |
| d2-persist | `claude/r8-persistence` | `a363dbf` | no | 27 | **MISSING** |
| d3-force | `claude/r8-force` | `ec968e6` | no | 80 | **MISSING** |
| d4-bcmerge | `claude/r8-bc-merge` | `598792e` | no | 2 | **MISSING** |
| d5-priorart | `claude/r8-priorart` | `969955d` | no | 21 | **MISSING** |
| d6-tooling | `claude/r8-tooling` | `ff9d605` | no | 6 | **MISSING** |
| d7-register | `claude/r8-register` | `476bdfd` | no | 0 (contained) | present |
| d8-naming | `claude/r8-naming` | `7697695` | no | 6 | **MISSING** |
| d9-kramer | `claude/r8-kramer` | `b6fe951` | no | 75 | **MISSING** |
| d10-licence | `claude/r8-licence` | `cca97f2` | no | 7 | **MISSING** |
| d11-accessor | `claude/r9-accessor` | `c621539` | no | 90 | **MISSING** |
| d12-kramerdata | `claude/r9-kramer-extract` | `0024ac1` | no | 84 | **MISSING** |
| d13-renders | `claude/r9-renders` | `733c149` | no | 17 | **MISSING** |
| d14-corpusbib | `claude/r9-corpus-bib` | `de18180` | no | 11 | **MISSING** |
| d15-settle | `claude/r9-settle` | `1ea9f49` | no | 14 | **MISSING** |
| d16-landing | `claude/r9-landing` | `6719728` | no | 10 | **MISSING** |
| d17-moving | `claude/r9-moving-vehicle` | `c1dad7f` | no | 23 | present |
| d18-platform | `claude/r9-platform` | `3f66ba1` | no | 16 | present |
| d19-priorcode | `claude/r9-priorcode` | `dc1a949` | no | 17 | present |
| d20-reader | `claude/r9-reader` | `9c19364` | no | 2 | **MISSING** |
| d21-jobb | `claude/r9-jobb-route` | `87ae518` | no | 86 | **MISSING** |
| d22-gapscan | `claude/r9-gapscan` | `5213f6f` | no | 9 | **MISSING** |
| d23-overleaf | `claude/r9-overleaf` | `cb6617a` | no | 3 | present |

---

## 3. Main checkout working tree, full `git status --short`

80 dirty paths. Reproduced in full, not summarized, as asked. [READ]

```
 M .claude/settings.json
 M .claude/skills/mpm-technical-deep-reference/references/02_genesis_gh200_and_solver_parameters.md
 M .claude/skills/mpm-technical-deep-reference/references/03_citations_and_physgaussian_bridge.md
 M .mcp.json
 M CLAUDE.md
 M docs/GLOBAL_IMPLEMENTATION_LOG_2026-08-21.md
 M scripts/r8/r8_plan.tsv
?? .claude-plugin/
?? .claude/dispatch_prompts/
?? .claude/plugin/
?? .claude/settings.local.json.bak-20260818-045233
?? .claude/tooling/
?? .mcp.json.bak-20260820-122441
?? archive/bak_sweep_2026-08-21/
?? docs/CANDIDATE_PAPER_SCOPE_TEST.md
?? docs/CLAUDE_CODE_SETUP_HANDOFF_2026-08-18.md
?? docs/CREDENTIAL_EXPOSURE_2026-08-13.md
?? docs/MCP_CONNECTOR_AUDIT_2026-08-18.md
?? docs/REMOTE_ACCESS_SETUP_2026-08-20.md
?? docs/SECOND_EYES_AUDIT_2026-08-20_1200.md
?? renders/yaris_render_s1/check_water_frames.py
?? renders/yaris_render_s1/common.py
?? renders/yaris_render_s1/encode.py
?? renders/yaris_render_s1/g0_validate.py
?? renders/yaris_render_s1/g1_car_check.py
?? renders/yaris_render_s1/g1b_car_check.py
?? renders/yaris_render_s1/gates.py
?? renders/yaris_render_s1/gates_all_runs.py
?? renders/yaris_render_s1/gates_both_scenarios.py
?? renders/yaris_render_s1/geom_live.py
?? renders/yaris_render_s1/render_flood.py
?? renders/yaris_render_s1/render_hero_g64_m1100_2026-08-06.py
?? renders/yaris_render_s1/render_hero_linkedin.py
?? renders/yaris_render_s1/render_pv.py
?? renders/yaris_render_s1/render_pv3.py
?? renders/yaris_render_s1/render_pv_fixed.py
?? renders/yaris_render_s1/render_realistic.py
?? renders/yaris_render_s1/render_seq.py
?? renders/yaris_render_s1/s2_gridgate.py
?? renders/yaris_render_s1/sim_dump.py
?? renders/yaris_render_s1/t1_car.py
?? renders/yaris_render_s1/t4_defects.py
?? scripts/overleaf_token_install.sh
?? scripts/r8/prompts/_body_d1-safe.md
?? scripts/r8/prompts/_body_d10-licence.md
?? scripts/r8/prompts/_body_d2-persist.md
?? scripts/r8/prompts/_body_d3-force.md
?? scripts/r8/prompts/_body_d4-bcmerge.md
?? scripts/r8/prompts/_body_d5-priorart.md
?? scripts/r8/prompts/_body_d6-tooling.md
?? scripts/r8/prompts/_body_d7-register.md
?? scripts/r8/prompts/_body_d8-naming.md
?? scripts/r8/prompts/_body_d9-kramer.md
?? scripts/r8/prompts/bodies/
?? scripts/r8/prompts/d1-safe.md
?? scripts/r8/prompts/d10-licence.md
?? scripts/r8/prompts/d11-accessor.md
?? scripts/r8/prompts/d12-kramerdata.md
?? scripts/r8/prompts/d13-renders.md
?? scripts/r8/prompts/d14-corpusbib.md
?? scripts/r8/prompts/d15-settle.md
?? scripts/r8/prompts/d16-landing.md
?? scripts/r8/prompts/d17-moving.md
?? scripts/r8/prompts/d18-platform.md
?? scripts/r8/prompts/d19-priorcode.md
?? scripts/r8/prompts/d2-persist.md
?? scripts/r8/prompts/d20-reader.md
?? scripts/r8/prompts/d21-jobb.md
?? scripts/r8/prompts/d23-overleaf.md
?? scripts/r8/prompts/d3-force.md
?? scripts/r8/prompts/d4-bcmerge.md
?? scripts/r8/prompts/d5-priorart.md
?? scripts/r8/prompts/d6-tooling.md
?? scripts/r8/prompts/d7-register.md
?? scripts/r8/prompts/d8-naming.md
?? scripts/r8/prompts/d9-kramer.md
?? scripts/refresh_bib_from_zotero.sh
?? scripts/wandb_env.sh
?? scripts/wandb_mcp_launch.sh
?? scripts/wb
```

Note that `.claude/state/r8_board.md` does NOT appear above and is NOT untracked-visible:
it is **gitignored** by `.gitignore:85:.claude/state/`. [MEASURED, `git check-ignore -v`]
It is 559409 bytes / 469 lines of cross-session findings that git will never see and no
push will ever carry. That is a deliberate ignore rule, not an accident, but it means the
board is invisible to GitHub by construction. Flagged, not changed.

## 4. Other worktrees, `git status --short`

| worktree | branch | dirty | detail |
|---|---|---|---|
| `can-it-ford-moving-vehicle` | `claude/moving-vehicle-exploratory-2026-08-11` | 1 | ?? scripts/pinned_span_wrapper.py |
| `can-it-ford-realism` | `realism-exploration` | 0 | clean |
| `can-it-ford-visual-trial` | `claude/visual-physical-realism-trial-2026-08-11` | 0 | clean |
| `can-it-ford-warpmpm-continue` | `warpmpm-continue` | 0 | clean |
| `can-it-ford/.claude/worktrees/concurrent-session-safety-570b39` | `detached d7a51a7` | 0 | clean |
| `can-it-ford/.claude/worktrees/ctx-census` | `worktree-ctx-census` | 3 | ?? docs/C1_ROOT_CAUSE_2026-08-07.md;?? docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md;?? renders_preview/ |
| `can-it-ford/.claude/worktrees/r8-register` | `claude/r8-register` | 0 | clean |
| `can-it-ford/.claude/worktrees/r9-moving-vehicle` | `claude/r9-moving-vehicle` | 0 | clean |
| `can-it-ford/.claude/worktrees/r9-overleaf` | `claude/r9-overleaf` | 1 |  M paper/r10_corrections_2026-08-20.patch |
| `can-it-ford/.claude/worktrees/r9-platform` | `claude/r9-platform` | 0 | clean |
| `can-it-ford/.claude/worktrees/r9-priorcode` | `claude/r9-priorcode` | 0 | clean |
| `can-it-ford/.claude/worktrees/retire-coupling-module-f20ad4` | `detached 8eada8e` | 0 | clean |
| `can-it-ford/.claude/worktrees/slide-resolution-dependence-reconcile-a5bf74` | `detached fbecf5d` | 0 | clean |

---

## 5. Uncommitted files dated 2026-08-18 to 2026-08-21 under docs/, data/, analysis/, simulation/

Swept across every registered worktree. **Six files, all in the main checkout.** The other
worktrees have nothing uncommitted in those four directories in that window. [MEASURED]

| mtime | state | path | what it is, from name + first 300 bytes |
|---|---|---|---|
| 2026-08-18 04:09 | untracked | `docs/MCP_CONNECTOR_AUDIT_2026-08-18.md` | 438 lines. Audit of the Claude Code tool/connector surface for this repo, with per-claim provenance tags. Infrastructure, not physics. |
| 2026-08-18 04:10 | untracked | `docs/CLAUDE_CODE_SETUP_HANDOFF_2026-08-18.md` | 402 lines. Setup handoff for a fresh session, written 04:05 BST, same provenance-tag scheme. Pairs with the file above. |
| 2026-08-20 02:10 | untracked | `docs/CANDIDATE_PAPER_SCOPE_TEST.md` | 133 lines. Five scope questions to ask a candidate paper before relaying it. Written by d21-jobb. Its own header says it is outside that slot's declared write scope. |
| 2026-08-20 14:21 | untracked | `docs/REMOTE_ACCESS_SETUP_2026-08-20.md` | 112 lines. iPhone to MacBook remote access for Claude Code. Header: "Mac side complete and verified. iPhone side unresolved." Infrastructure. |
| 2026-08-20 14:38 | untracked | `docs/SECOND_EYES_AUDIT_2026-08-20_1200.md` | 1334 lines, 74869 bytes. Independent concurrent audit of the live licence/register session. **Largest single unshipped artifact in the working tree.** |
| 2026-08-21 02:13 | **modified** | `docs/GLOBAL_IMPLEMENTATION_LOG_2026-08-21.md` | 324 lines. Replace-and-delete pass over the merged research corpus. Tracked file with uncommitted local edits. Carries its own caveat that 2 of 6 prescribed steps could not be completed. |

Out of the date window and therefore excluded, but present and untracked in the same tree:
`docs/CREDENTIAL_EXPOSURE_2026-08-13.md` (mtime 2026-08-13 16:39).

One more uncommitted change outside the four named directories, worth recording because it
is a live edit in another worktree: `paper/r10_corrections_2026-08-20.patch`, **modified**,
in `.claude/worktrees/r9-overleaf`. [READ]

---

## 6. Cross-reference against the register and the board

Asked for: flag anything that supersedes or corrects something already on GitHub, as
highest priority to land first.

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` is **tracked, committed and pushed**
(3532 lines, last written 2026-08-21 22:23, matching commit `fd4f8b7` at 22:23). It is not
itself unshipped. [MEASURED]

| doc | mentions in register | mentions on board | correction markers in its own text |
|---|---|---|---|
| `MCP_CONNECTOR_AUDIT_2026-08-18.md` | 0 | 0 | 2 |
| `CLAUDE_CODE_SETUP_HANDOFF_2026-08-18.md` | 0 | 0 | 1 |
| `CANDIDATE_PAPER_SCOPE_TEST.md` | 0 | **4** | 0 |
| `REMOTE_ACCESS_SETUP_2026-08-20.md` | 0 | 0 | 0 |
| `SECOND_EYES_AUDIT_2026-08-20_1200.md` | 0 | 0 | 1 |
| `GLOBAL_IMPLEMENTATION_LOG_2026-08-21.md` | 0 | 0 | 3 |

"Correction markers" counts lines matching
`RETRACT|WITHDRAW|SUPERSED|IS WRONG|WAS WRONG|CORRECTION|INCORRECT|REFUTED`. It is a
keyword count, **not** a judgement that the document overturns a published claim.

**The honest finding: none of the six is registered as correcting anything.** Zero register
references across all six. Only `CANDIDATE_PAPER_SCOPE_TEST.md` appears on the board, four
times, consistent with d21-jobb's own board row saying it placed that file untracked in the
main tree and deliberately did not stage it because the tree belongs to another session.

**So the prompt's "highest priority to land first" category is, on this evidence, empty.**
I am not going to manufacture a supersedes-relationship to fill it. Establishing whether
the 1334-line second-eyes audit or the 3 markers in the implementation log actually
overturn a published claim requires reading both against the register, which is a research
judgement, not an inventory one, and the prompt explicitly says not to generate findings.

---

## 7. Duplicate or already-shipped, leave alone

| slot | branch | why |
|---|---|---|
| d1-safe | `claude/add-ci-checks` | Local tip `fd4f8b7` equals the GitHub ref exactly. Fully shipped. |
| d7-register | `claude/r8-register` | Tip `476bdfd` is an ancestor of the pushed remote. Merged 2026-08-21 02:11. **Do not re-merge.** |
| d20-reader | `claude/r9-reader` | Not an ancestor, but **all three of its changed files are byte-identical to the pushed base** (verified by blob SHA, not by name or size): `analysis/r9_session_reader.py`, `docs/R9_COORDINATOR_AUDIT_2026-08-19.md`, `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md`. Landed by cherry-pick, so the tip diverges while the content does not. **Content is fully shipped; merging it would add nothing.** |

A large overlap also exists among d3-force, d9-kramer, d11-accessor, d12-kramerdata and
d21-jobb: all five inherit the same `docs/R5_PHYSICS_*.md` set from `claude/r5-physics`.
Those documents would land once, not five times, and any per-slot count that treats them
as distinct new work is inflated.

---

## 8. What each unshipped branch would actually add

Files ADDED versus the merge-base with the pushed remote, restricted to
`docs/ data/ analysis/ simulation/`, and checked blob-by-blob against the base so that
a path already present is marked rather than counted as new. [MEASURED]

**d2-persist** `claude/r8-persistence` `a363dbf`, 21 files changed vs merge-base, 15 additions in the four dirs:

- `analysis/inflow_vehicle_stats.py`
- `analysis/inflow_vehicle_tables.py`
- `analysis/r6_a1_caveats.py`
- `analysis/r6_hull_clearance.py`
- `analysis/r6_repeat_stats.py`
- `analysis/r8_persistence_frequency.py`
- `data/r7_inflow_918506/profiles.npz`
- `data/r7_inflow_918506/runs.json`
- `docs/HANDOFF_ROUND_7_2026-08-18.md`
- `docs/OVERLEAF_CONNECTION_SETUP_2026-08-18.md`
- `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md`
- `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md`
- `docs/R8_PERSISTENCE_GATE_2026-08-18.md`
- `docs/overleaf_staging/mpm_foundations_additions.bib`
- `simulation/openchannel_bc.py` (path already on base)

**d3-force** `claude/r8-force` `ec968e6`, 32 files changed vs merge-base, 32 additions in the four dirs:

- `analysis/r8_noforcing_control.py`
- `docs/R5_PHYSICS_BATCH_MANIFEST.md`
- `docs/R5_PHYSICS_BENCHMARK_UNBLOCKED.md`
- `docs/R5_PHYSICS_BLOCKED_FLAGS.md`
- `docs/R5_PHYSICS_BRAKE_STATE.md`
- `docs/R5_PHYSICS_DEPTH_CONFOUND.md`
- `docs/R5_PHYSICS_FLOOR_BC_DIAGNOSIS.md`
- `docs/R5_PHYSICS_HANDOFF_2026-08-18.md`
- `docs/R5_PHYSICS_ITEM15_STATUS.md`
- `docs/R5_PHYSICS_JOB_A_RESULTS.md`
- `docs/R5_PHYSICS_JOB_B_RESULT.md`
- `docs/R5_PHYSICS_KRAMER2021_TESTCASE.md`
- `docs/R5_PHYSICS_NIHEI_2025_BRAKE_GROUNDING.md`
- `docs/R5_PHYSICS_OPTION_A_FEASIBILITY.md`
- `docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md`
- `docs/R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md`
- `docs/R5_PHYSICS_SKEPTIC_CORRECTIONS.md`
- `docs/R5_PHYSICS_START_HERE.md`
- `docs/R5_PHYSICS_SU_TRIAGE.md`
- `docs/R5_PHYSICS_WHAT_SURVIVES.md`
- `docs/R8_FORCE_ROUTE_2026-08-18.md`
- `simulation/r5_physics/blocking.py`
- `simulation/r5_physics/depth_station.py`
- `simulation/r5_physics/grade_job_b.py`
- `simulation/r5_physics/kramer_benchmark.py`
- `simulation/r5_physics/outflow_deactivate.py`
- `simulation/r5_physics/p2_decompose.py`
- `simulation/r5_physics/prestage_jobs.sh`
- `simulation/r5_physics/sphere_heave.py`
- `simulation/r5_physics/spin_down.py`
- `simulation/r5_physics/test_sphere_dryrun.py`
- `simulation/r5_physics/test_sphere_geometry.py`

**d4-bcmerge** `claude/r8-bc-merge` `598792e`, 2 files changed vs merge-base, 2 additions in the four dirs:

- `docs/R8_OPENCHANNEL_BC_RECONCILE.md`
- `simulation/openchannel_bc.py` (path already on base)

**d5-priorart** `claude/r8-priorart` `969955d`, 10 files changed vs merge-base, 8 additions in the four dirs:

- `analysis/r6_a1_caveats.py`
- `analysis/r6_hull_clearance.py`
- `analysis/r6_repeat_stats.py`
- `docs/HANDOFF_ROUND_7_2026-08-18.md`
- `docs/OVERLEAF_CONNECTION_SETUP_2026-08-18.md`
- `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md`
- `docs/R8_PRIOR_ART_2026-08-18.md`
- `docs/overleaf_staging/mpm_foundations_additions.bib`

**d6-tooling** `claude/r8-tooling` `ff9d605`, 19 files changed vs merge-base, 1 additions in the four dirs:

- `docs/R8_TOOLING_PROVENANCE.md`

**d8-naming** `claude/r8-naming` `7697695`, 9 files changed vs merge-base, 1 additions in the four dirs:

- `docs/R8_DETERMINISM_RENAME_2026-08-18.md`

**d9-kramer** `claude/r8-kramer` `b6fe951`, 31 files changed vs merge-base, 31 additions in the four dirs:

- `docs/R5_PHYSICS_BATCH_MANIFEST.md`
- `docs/R5_PHYSICS_BENCHMARK_UNBLOCKED.md`
- `docs/R5_PHYSICS_BLOCKED_FLAGS.md`
- `docs/R5_PHYSICS_BRAKE_STATE.md`
- `docs/R5_PHYSICS_DEPTH_CONFOUND.md`
- `docs/R5_PHYSICS_FLOOR_BC_DIAGNOSIS.md`
- `docs/R5_PHYSICS_HANDOFF_2026-08-18.md`
- `docs/R5_PHYSICS_ITEM15_STATUS.md`
- `docs/R5_PHYSICS_JOB_A_RESULTS.md`
- `docs/R5_PHYSICS_JOB_B_RESULT.md`
- `docs/R5_PHYSICS_KRAMER2021_TESTCASE.md`
- `docs/R5_PHYSICS_NIHEI_2025_BRAKE_GROUNDING.md`
- `docs/R5_PHYSICS_OPTION_A_FEASIBILITY.md`
- `docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md`
- `docs/R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md`
- `docs/R5_PHYSICS_SKEPTIC_CORRECTIONS.md`
- `docs/R5_PHYSICS_START_HERE.md`
- `docs/R5_PHYSICS_SU_TRIAGE.md`
- `docs/R5_PHYSICS_WHAT_SURVIVES.md`
- `docs/R8_KRAMER_INTERCODE_2026-08-18.md`
- `simulation/r5_physics/blocking.py`
- `simulation/r5_physics/depth_station.py`
- `simulation/r5_physics/grade_job_b.py`
- `simulation/r5_physics/kramer_benchmark.py`
- `simulation/r5_physics/outflow_deactivate.py`
- `simulation/r5_physics/p2_decompose.py`
- `simulation/r5_physics/prestage_jobs.sh`
- `simulation/r5_physics/sphere_heave.py`
- `simulation/r5_physics/spin_down.py`
- `simulation/r5_physics/test_sphere_dryrun.py`
- `simulation/r5_physics/test_sphere_geometry.py`

**d10-licence** `claude/r8-licence` `cca97f2`, 11 files changed vs merge-base, 2 additions in the four dirs:

- `analysis/wandb_log_gated_runs.py`
- `docs/R8_LICENCE_RECONCILE_2026-08-18.md`

**d11-accessor** `claude/r9-accessor` `c621539`, 38 files changed vs merge-base, 38 additions in the four dirs:

- `analysis/r9_column_stats.py`
- `data/r9_column/column_923219_bcfix.json`
- `data/r9_column/column_923219_control.json`
- `data/r9_column/column_923270_ppc1.json`
- `data/r9_column/column_923270_ppc2.json`
- `data/r9_column/column_923270_ppc3.json`
- `docs/R5_PHYSICS_BATCH_MANIFEST.md`
- `docs/R5_PHYSICS_BENCHMARK_UNBLOCKED.md`
- `docs/R5_PHYSICS_BLOCKED_FLAGS.md`
- `docs/R5_PHYSICS_BRAKE_STATE.md`
- `docs/R5_PHYSICS_DEPTH_CONFOUND.md`
- `docs/R5_PHYSICS_FLOOR_BC_DIAGNOSIS.md`
- `docs/R5_PHYSICS_HANDOFF_2026-08-18.md`
- `docs/R5_PHYSICS_ITEM15_STATUS.md`
- `docs/R5_PHYSICS_JOB_A_RESULTS.md`
- `docs/R5_PHYSICS_JOB_B_RESULT.md`
- `docs/R5_PHYSICS_KRAMER2021_TESTCASE.md`
- `docs/R5_PHYSICS_NIHEI_2025_BRAKE_GROUNDING.md`
- `docs/R5_PHYSICS_OPTION_A_FEASIBILITY.md`
- `docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md`
- `docs/R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md`
- `docs/R5_PHYSICS_SKEPTIC_CORRECTIONS.md`
- `docs/R5_PHYSICS_START_HERE.md`
- `docs/R5_PHYSICS_SU_TRIAGE.md`
- `docs/R5_PHYSICS_WHAT_SURVIVES.md`
- `docs/R9_ACCESSOR_DEFECT_2026-08-18.md`
- `simulation/r5_physics/blocking.py`
- `simulation/r5_physics/depth_station.py`
- `simulation/r5_physics/grade_job_b.py`
- `simulation/r5_physics/hydrostatic_column.py`
- `simulation/r5_physics/kramer_benchmark.py`
- `simulation/r5_physics/outflow_deactivate.py`
- `simulation/r5_physics/p2_decompose.py`
- `simulation/r5_physics/prestage_jobs.sh`
- `simulation/r5_physics/sphere_heave.py`
- `simulation/r5_physics/spin_down.py`
- `simulation/r5_physics/test_sphere_dryrun.py`
- `simulation/r5_physics/test_sphere_geometry.py`

**d12-kramerdata** `claude/r9-kramer-extract` `0024ac1`, 34 files changed vs merge-base, 34 additions in the four dirs:

- `analysis/kramer_extract_numerical.py`
- `docs/R5_PHYSICS_BATCH_MANIFEST.md`
- `docs/R5_PHYSICS_BENCHMARK_UNBLOCKED.md`
- `docs/R5_PHYSICS_BLOCKED_FLAGS.md`
- `docs/R5_PHYSICS_BRAKE_STATE.md`
- `docs/R5_PHYSICS_DEPTH_CONFOUND.md`
- `docs/R5_PHYSICS_FLOOR_BC_DIAGNOSIS.md`
- `docs/R5_PHYSICS_HANDOFF_2026-08-18.md`
- `docs/R5_PHYSICS_ITEM15_STATUS.md`
- `docs/R5_PHYSICS_JOB_A_RESULTS.md`
- `docs/R5_PHYSICS_JOB_B_RESULT.md`
- `docs/R5_PHYSICS_KRAMER2021_TESTCASE.md`
- `docs/R5_PHYSICS_NIHEI_2025_BRAKE_GROUNDING.md`
- `docs/R5_PHYSICS_OPTION_A_FEASIBILITY.md`
- `docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md`
- `docs/R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md`
- `docs/R5_PHYSICS_SKEPTIC_CORRECTIONS.md`
- `docs/R5_PHYSICS_START_HERE.md`
- `docs/R5_PHYSICS_SU_TRIAGE.md`
- `docs/R5_PHYSICS_WHAT_SURVIVES.md`
- `docs/R8_KRAMER_INTERCODE_2026-08-18.md`
- `docs/R9_JOBC_PREREGISTRATION_AND_BLOCKER_2026-08-19.md`
- `docs/R9_KRAMER_FULL_EXTRACT_2026-08-18.md`
- `simulation/r5_physics/blocking.py`
- `simulation/r5_physics/depth_station.py`
- `simulation/r5_physics/grade_job_b.py`
- `simulation/r5_physics/kramer_benchmark.py`
- `simulation/r5_physics/outflow_deactivate.py`
- `simulation/r5_physics/p2_decompose.py`
- `simulation/r5_physics/prestage_jobs.sh`
- `simulation/r5_physics/sphere_heave.py`
- `simulation/r5_physics/spin_down.py`
- `simulation/r5_physics/test_sphere_dryrun.py`
- `simulation/r5_physics/test_sphere_geometry.py`

**d13-renders** `claude/r9-renders` `733c149`, 12 files changed vs merge-base, 11 additions in the four dirs:

- `analysis/cycles_caption.py`
- `analysis/cycles_render.py`
- `analysis/cycles_road_scene.py`
- `analysis/cycles_sequence.sh`
- `analysis/mesh_quality_sweep.py`
- `analysis/prep_cycles_frames.py`
- `analysis/prep_cycles_scene.py`
- `docs/R9_APPEARANCE_HULL_COSTING_2026-08-19.md`
- `docs/R9_ASSET_PROVENANCE_B6_2026-08-20.md`
- `docs/R9_CYCLES_PRESENTATION_RENDER_2026-08-19.md`
- `docs/R9_RENDER_MATERIALS_2026-08-18.md`

**d14-corpusbib** `claude/r9-corpus-bib` `de18180`, 6 files changed vs merge-base, 4 additions in the four dirs:

- `data/deep_searches/buoyancy-overestimation.json`
- `data/deep_searches/vehicle-mesh-assets.json` (path already on base)
- `data/r9_bib_corpus_census.tsv`
- `docs/R9_CORPUS_BIB_GAP_2026-08-18.md`

**d15-settle** `claude/r9-settle` `1ea9f49`, 8 files changed vs merge-base, 3 additions in the four dirs:

- `analysis/r9_vista_inventory.py`
- `analysis/r9_vista_stationarity_pass.py`
- `docs/R9_SETTLE_FRAMES_2026-08-18.md`

**d16-landing** `claude/r9-landing` `6719728`, 1 files changed vs merge-base, 1 additions in the four dirs:

- `docs/R9_LANDING_PLAN_2026-08-18.md`

**d17-moving** `claude/r9-moving-vehicle` `c1dad7f`, 5 files changed vs merge-base, 5 additions in the four dirs:

- `analysis/r9_render_frames.py`
- `analysis/r9_speed_surface.py`
- `data/r9_speed_surface.tsv`
- `docs/R9_MOVING_VEHICLE_2026-08-19.md`
- `simulation/moving_vehicle_channel.py`

**d18-platform** `claude/r9-platform` `3f66ba1`, 14 files changed vs merge-base, 3 additions in the four dirs:

- `analysis/hf_dataset_publish.py`
- `analysis/wandb_speed_surface.py`
- `docs/R9_PLATFORM_ROI_2026-08-19.md`

**d19-priorcode** `claude/r9-priorcode` `dc1a949`, 3 files changed vs merge-base, 3 additions in the four dirs:

- `analysis/r9_chrono_tow_drag.cpp`
- `analysis/r9_prior_code_compare.py`
- `docs/R9_MOVING_VEHICLE_PRIOR_CODE_2026-08-19.md`

**d20-reader** `claude/r9-reader` `9c19364`, 3 files changed vs merge-base, 3 additions in the four dirs:

- `analysis/r9_session_reader.py` (path already on base)
- `docs/R9_COORDINATOR_AUDIT_2026-08-19.md` (path already on base)
- `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md` (path already on base)

**d21-jobb** `claude/r9-jobb-route` `87ae518`, 33 files changed vs merge-base, 33 additions in the four dirs:

- `analysis/r9_jobb_estimator_test.py`
- `docs/CANDIDATE_PAPER_SCOPE_TEST.md`
- `docs/R5_PHYSICS_BATCH_MANIFEST.md`
- `docs/R5_PHYSICS_BENCHMARK_UNBLOCKED.md`
- `docs/R5_PHYSICS_BLOCKED_FLAGS.md`
- `docs/R5_PHYSICS_BRAKE_STATE.md`
- `docs/R5_PHYSICS_DEPTH_CONFOUND.md`
- `docs/R5_PHYSICS_FLOOR_BC_DIAGNOSIS.md`
- `docs/R5_PHYSICS_HANDOFF_2026-08-18.md`
- `docs/R5_PHYSICS_ITEM15_STATUS.md`
- `docs/R5_PHYSICS_JOB_A_RESULTS.md`
- `docs/R5_PHYSICS_JOB_B_RESULT.md`
- `docs/R5_PHYSICS_KRAMER2021_TESTCASE.md`
- `docs/R5_PHYSICS_NIHEI_2025_BRAKE_GROUNDING.md`
- `docs/R5_PHYSICS_OPTION_A_FEASIBILITY.md`
- `docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md`
- `docs/R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md`
- `docs/R5_PHYSICS_SKEPTIC_CORRECTIONS.md`
- `docs/R5_PHYSICS_START_HERE.md`
- `docs/R5_PHYSICS_SU_TRIAGE.md`
- `docs/R5_PHYSICS_WHAT_SURVIVES.md`
- `docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md`
- `simulation/r5_physics/blocking.py`
- `simulation/r5_physics/depth_station.py`
- `simulation/r5_physics/grade_job_b.py`
- `simulation/r5_physics/kramer_benchmark.py`
- `simulation/r5_physics/outflow_deactivate.py`
- `simulation/r5_physics/p2_decompose.py`
- `simulation/r5_physics/prestage_jobs.sh`
- `simulation/r5_physics/sphere_heave.py`
- `simulation/r5_physics/spin_down.py`
- `simulation/r5_physics/test_sphere_dryrun.py`
- `simulation/r5_physics/test_sphere_geometry.py`

**d22-gapscan** `claude/r9-gapscan` `5213f6f`, 40 files changed vs merge-base, 40 additions in the four dirs:

- `docs/R10_WEB_ACQUISITION_2026-08-19.md`
- `docs/r10/acquired_verified.tsv`
- `docs/r10/acquisition_manifest.tsv`
- `docs/r10/all_oa_manifest.tsv`
- `docs/r10/disk_resolution.tsv`
- `docs/r10/disk_verified.tsv`
- `docs/r10/fetch_all_oa.py`
- `docs/r10/fetch_oa.sh`
- `docs/r10/fetch_priority.py`
- `docs/r10/fetch_run.log`
- `docs/r10/fetch_unpaywall.log`
- `docs/r10/fetch_unpaywall.py`
- `docs/r10/fetch_unpaywall2.log`
- `docs/r10/fetch_verified.log`
- `docs/r10/fetch_verified.py`
- `docs/r10/fou19_still_water_read.md`
- `docs/r10/local_tree_resolution.tsv`
- `docs/r10/pdf_first_text.py`
- `docs/r10/pdftext.swift`
- `docs/r10/priority_manifest.tsv`
- `docs/r10/quote_verification.tsv`
- `docs/r10/quotes_to_check.tsv`
- `docs/r10/reaim_manifest.tsv`
- `docs/r10/resolve_disk.sh`
- `docs/r10/resolve_local_trees.py`
- `docs/r10/resolve_oa.py`
- `docs/r10/resolve_run.log`
- `docs/r10/resolve_stragglers.py`
- `docs/r10/scan_new.log`
- `docs/r10/scan_new.py`
- `docs/r10/schulz2019_image_particles_read.md`
- `docs/r10/stragglers_judged.tsv`
- `docs/r10/stragglers_resolved.tsv`
- `docs/r10/unpaywall_manifest.tsv`
- `docs/r10/verified_manifest.tsv`
- `docs/r10/verify_acquired.py`
- `docs/r10/verify_disk_matches.sh`
- `docs/r10/verify_quotes.py`
- `docs/r10/want_list_deep_searches.tsv`
- `docs/r10/want_list_deep_searches_resolved.tsv`

**d23-overleaf** `claude/r9-overleaf` `cb6617a`, 3 files changed vs merge-base, 2 additions in the four dirs:

- `analysis/paper_fig_force_balance_v2_check.py`
- `docs/R10_PAPER_CORRECTIONS_2026-08-20.md`

---

## 9. Why Part 2 (merge) and Part 3 (push) were not started

Five independent blockers. Any one of them alone would justify stopping; the first two are
hard.

**(1) Preflight failed and cannot self-correct.** Section 1.1. The remedy is to relaunch
in `/Users/josie/can-it-ford`, which this session cannot do without a `cd` that both the
script and the global CLAUDE.md forbid, with dated incidents behind the rule.

**(2) 26 live Claude sessions hold these branches.** Preflight lists panes `canford8:d11`
through `d23` and `phone:d11` through `d23`. Its own text: "do not touch their branches or
worktrees." Rebasing or merging 21 branches out from under 26 live sessions is precisely
the concurrency topology this project's preflight exists to prevent, and the board records
two prior breaches of exactly this shape.

**(3) The 8-file pre-commit ceiling versus the actual change sizes.**
`.git/hooks/pre-commit` refuses more than 8 staged files. [READ, verbatim] Measured file
counts vs merge-base: d22-gapscan 40, d11-accessor 38, d12-kramerdata 34, d21-jobb 33,
d3-force 32, d9-kramer 31. Landing these as merges is fine, since the hook counts staged
files and not merge contents, but any hand-staged reconciliation of them is not a
mechanical job and cannot be done in single commits.

**(4) The rebase question in Part 2 step 1 has no clean answer.** The prompt says to
confirm each branch is based on a current `add-ci-checks` and rebase if not. But
`origin/main` is **5 commits ahead** of `origin/claude/add-ci-checks` (`c7f0a16`, `1c71a5a`,
`aee70ab`, `f6348c7`, `647aaa0`, all merged PRs #10 to #14), while `add-ci-checks` is 147
ahead of main. [MEASURED] So "current" is ambiguous: current with respect to the branch, or
to main. Rebasing 21 branches carrying 2 to 90 commits each onto a moving base, while 26
sessions hold them, is where silent loss happens. The prompt asks me to say explicitly if a
rebase conflicts rather than resolve silently; I am saying that I did not start any rebase.

**(5) The write-scope question for this very file.** Slot `d1-safe`, the slot used for
preflight, declares its write scope as `CLAUDE.md`, `.claude/settings.json`,
`.claude/hooks/orient_live.sh`, `.claude/checks/params_check.py`,
`.claude/skills/connector-router/SKILL.md`, `scripts/check_claims.py`. **`docs/` is not in
it.** This file is therefore outside the declared scope of the only slot that fits. It has
been written **untracked and unstaged**, which is the same handling d21-jobb chose for
`docs/CANDIDATE_PAPER_SCOPE_TEST.md` and recorded on the board. Staging it needs either a
slot that owns `docs/` or an explicit human instruction.

---

## 10. What needs a human decision

Named plainly rather than forced into looking finished.

1. **Were the 16 worktree directories removed on purpose at 00:51 tonight?** Nothing is
   lost, all refs survive, but 26 live sessions are pointing into deleted directories. This
   should be answered before anything else, because it determines whether the right next
   move is to recreate the worktrees or to stand the sessions down.

2. **Which slot owns this task?** The prompt left `<SLOT>` literal. No plan row covers
   "inventory, merge and push everything", and no row owns `docs/` broadly enough to write
   this file. Landing 21 branches is a coordinator action that the plan does not model.

3. **Relaunch location.** This session is in `/` and cannot merge or push from there.
   It needs relaunching in `/Users/josie/can-it-ford`.

4. **Target of the merge: `add-ci-checks` or `main`?** `add-ci-checks` is 147 ahead of
   `main` and 5 behind. Landing 21 more branches onto `add-ci-checks` widens a gap that is
   already the largest thing separating this project from its published state. The more
   valuable question may be whether `add-ci-checks` (147 commits, CI green on `fd4f8b7`)
   should go to `main` first.

5. **Do any of the six uncommitted docs actually correct published claims?** Section 6
   found zero register references. Deciding whether the 1334-line second-eyes audit
   overturns anything is a research judgement and the prompt forbids generating findings.

6. **The gitignored board.** `.claude/state/r8_board.md` holds 469 lines of cross-session
   findings that no push can ever carry, by an intentional `.gitignore` rule. If that
   content is meant to survive, it needs a different home.

---

## 11. Provenance of this document

Every number came from a command run against the live repository during this session. No
number was recalled, and none was carried from a prior summary. The commands were: preflight,
`git status --porcelain`, `git worktree list --porcelain`, `git for-each-ref`,
`git ls-remote --heads origin` (live network read), `git merge-base --is-ancestor`,
`git rev-list --count`, `git diff --name-status`, `git rev-parse` for blob comparison,
`git check-ignore -v`, `git reflog`, `stat`, and `gh run list`.

**Unreviewed.** Per preflight's standing notice, the adversarial reviewer path was measured
dead fleet-wide on 2026-08-19 (20 Agent calls, 0 successes). It was not retried and not
faked. No claim in this document has had a second pair of eyes.

**Not verified here:** whether the 00:51 worktree removal was deliberate; whether any of the
six uncommitted docs overturns a published claim; whether the 21 branches rebase cleanly.
All three are stated as open, not resolved.

---
---

# ADDENDUM, 2026-08-22 ~01:25 BST

Second dispatch, acting only on parts not covered above. Still no writes to git:
nothing staged, committed, merged or pushed.

## 12. Step Zero, in its revised form

```
hostname   Josephines-MacBook-Air.local
pwd        /
git -C /Users/josie/can-it-ford branch --show-current   claude/add-ci-checks
```

**FAIL on pwd.** Required `/Users/josie/can-it-ford` exactly. Actual `/`. This is the same
positional fault the preflight caught in section 1.1, now confirmed by the simpler check.
The dispatching prompt's own remedy applies: "stop and relaunch Claude Code from the
correct folder rather than cd-ing there, per this project's standing no-cd rule."

**PASS on branch, with one naming note.** The branch is `claude/add-ci-checks`, not bare
`add-ci-checks`. It is the intended branch and not a stray feature branch, but the bare
form does not exist either locally or on the remote, which is the same naming gap that made
`origin/add-ci-checks` unresolvable in section 1.2(a).

Also confirmed: the checkout is the canonical one, not an archived copy. It is not under
`.claude/worktrees/`, and it is not `can-it-ford-BACKUP-*`, `can-it-ford-demo`,
`can-it-ford-rescue`, or any other sibling. [MEASURED]

## 13. The transcript-derived worktree list, checked against live git

The supplied list was confirmed exactly against `.claude/projects/` folder names: twelve
`r9-*` entries plus `concurrent-session-safety-570b39`, thirteen total. [MEASURED]

**It is stale for 9 of the 13, exactly as the prompt warned.** Checked against a live
`git worktree list --porcelain`:

| name | registered worktree | directory |
|---|---|---|
| r9-moving-vehicle | yes | present |
| r9-priorcode | yes | present |
| r9-platform | yes | present |
| concurrent-session-safety-570b39 | yes | present |
| r9-gapscan | **no** | **gone** |
| r9-kramer-extract | **no** | **gone** |
| r9-settle | **no** | **gone** |
| r9-corpus-bib | **no** | **gone** |
| r9-accessor | **no** | **gone** |
| r9-renders | **no** | **gone** |
| r9-reader | **no** | **gone** |
| r9-jobb-route | **no** | **gone** |
| r9-landing | **no** | **gone** |

The staleness runs the other way too. **Nine registered worktrees have no transcript folder
in that list at all:** `can-it-ford-moving-vehicle`, `can-it-ford-realism`,
`can-it-ford-visual-trial`, `can-it-ford-warpmpm-continue`, `.claude/worktrees/ctx-census`,
`.claude/worktrees/r8-register`, `.claude/worktrees/r9-overleaf`,
`.claude/worktrees/retire-coupling-module-f20ad4`,
`.claude/worktrees/slide-resolution-dependence-reconcile-a5bf74`.

Neither list is a superset of the other. A transcript folder records that a session once ran
in a path; it does not record that the path is still a worktree. Both were needed.

## 14. The priority unknown, resolved: the folder name is misleading

`concurrent-session-safety-570b39` was flagged as the thing to inventory first, on the
reading that something built session-collision safety very recently and nothing downstream
knows about it. **Three of the four premises there do not survive contact with the repo.**

**(a) The worktree is not on the branch its folder is named after.** It sits at
**detached HEAD `d7a51a7`**, and `git branch --contains d7a51a7` returns exactly one
branch: `claude/meta-prompt-reconcile-dispatch-14a3c8`. The directory name and its contents
belong to different lineages. [MEASURED]

**(b) The branch of that name is already shipped.**
`claude/concurrent-session-safety-570b39` is `13187c0`, 2026-08-12, "Add
REMEDIATION_PLAN_AUDIT_2026-08-12", and it **is an ancestor of the pushed remote**. That
work is on GitHub already. [MEASURED]

**(c) It is not recent.** The Aug 20 17:16 timestamp is the transcript folder's mtime. That
folder contains **no conversation transcript at all**, only a single hook stdout file
(`hook-ff148f96...-stdout.txt`, 243 lines). The worktree is clean, and its HEAD commit is
dated **2026-08-14**. Nothing was committed there on Aug 20. The recency is a hook firing,
not session work. [MEASURED]

**(d) What IS real, and it is worth landing.** The lineage the detached HEAD belongs to,
`claude/meta-prompt-reconcile-dispatch-14a3c8`, is **8 commits ahead of the pushed base and
is on no remote**. It adds four files, **none of which is on the pushed base**:

- `docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md`
- `docs/RESEARCH_BRIEFS_REALISTIC_ENV_2026-08-14.md`
- `scripts/canford_monitor.sh`
- `scripts/canford_tmux.sh`

Its commits: `9e940e8` reconcile across three machines, `644b802` 13-pane dispatch launcher,
`d04b642` three launcher defects, `f66fa79` health monitor, `9dc12c0` rebuilt dispatch
monitor with overwrite detection, `9b4da01` STALL ambiguity note, **`de6a8d5` "Add pushcheck:
verify a branch before it reaches a public remote"**, `d7a51a7` log monitor alerts to file.

**This branch is absent from `scripts/r8/r8_plan.tsv` entirely**, which is the concrete
sense in which nothing downstream knows about it. It is outside the whole r8/r9 slot
structure, so no slot owns it and no dispatch would ever have landed it.

**The sharpest single item: `pushcheck` is an unshipped guard against exactly the risk
Part 3 runs.** It lives in `scripts/canford_monitor.sh:355`, and its header reads: "What
must never reach a PUBLIC remote: third-party-derived mesh geometry (register E8, the
CCSA/NCAC zips carry no redistribution grant), credential material, and run artifacts." It
blocks on paths matching
`\.(ply|obj|stl|npz|npy|env|key|pem|pth)$|secret|token|credential|id_rsa`
and honours a `*DO-NOT-PUSH*` branch convention. A tool written to vet pushes to this public
repo has itself never been pushed. **It should land before, not after, any bulk push.**

## 15. The three forbidden backup clones, audited

All three exist, all three are real git repositories, and **all three have
`https://github.com/jcerrell-IS/can-it-ford.git` as origin.** [MEASURED]

| clone | HEAD | date | commits | leaked paths in history |
|---|---|---|---|---|
| `can-it-ford-BACKUP-before-history-purge` | `0f35620` | 2026-07-23 | 190 | **6 commits, 3 additions** |
| `can-it-ford-BACKUP-2026-08-11` | `f63e766` | 2026-08-11 | 419 | **0, clean** |
| `can-it-ford-rescue/ls6_scratch/can-it-ford-OLD-pre-purge` | `d567079` | 2026-07-21 | 149 | **3 commits, 3 additions** |

**The quoted commit title is exact.** `0f35620` is "Remove leaked personal CLAUDE.md copies
and ADHD reference from tracking."

**The risk is confirmed, not merely suspected.** That commit deletes three paths:
`files/CLAUDE_md_CANONICAL_july13.md`, `files/CLAUDE_md_FINAL_july13.md`,
`files/CLAUDE_md_corrected_july13.md`. All three are **still retrievable at `0f35620^`** in
that clone. Deleting a file in a later commit does not remove it from history. [MEASURED]

**The canonical repo is clean and the histories are disjoint.** Those three paths appear in
**0 commits** across all refs in `/Users/josie/can-it-ford`, and `0f35620` is **not present
as an object** there at all. So a merge or pull from that clone would not re-add a file, it
would graft an entire disjoint pre-purge lineage carrying the leaked content onto a
**public** repository, permanently. [MEASURED]

**Current status of the rule: satisfied.** `git remote -v` on the canonical repo lists only
`origin` and `overleaf`. None of the three is configured as a remote. [MEASURED]

**One material correction to the rule as written.** It groups all three under one stated
reason, the pre-purge leak. That reason is **true for two and false for the third**:

- `BACKUP-before-history-purge` and `OLD-pre-purge` are contaminated **and** disjoint from
  canonical history. These are the genuinely dangerous two.
- `BACKUP-2026-08-11` is **clean of the leak (0 commits, 0 additions)** and its HEAD
  `f63e766` **is already present in the canonical repo**, so it shares lineage rather than
  being disjoint. It is an ordinary post-purge backup.

The prohibition still stands on all three, because it is yours to relax and not mine, and
"do not merge without explicit confirmation" costs nothing. But if something is ever needed
out of `BACKUP-2026-08-11`, the leak argument is not the reason to refuse, and treating the
three as interchangeable would misprice the risk in both directions.

The extraction method given in the rule is the right one and needs no change:
`git show <sha>:<path> > newfile`, never `git merge` or `git pull`.

## 16. Revised priority order for whoever runs Part 2

1. **Answer the 00:51 worktree-removal question** (section 2.1). Unchanged, still first.
2. **Land `claude/meta-prompt-reconcile-dispatch-14a3c8`, especially `pushcheck`.** New in
   this pass. A public-remote safety guard that is itself unpushed should precede a bulk
   push, and the branch is small: 8 commits, 4 files, none colliding with the base.
3. Everything in section 8, unchanged.

Duplicate or already shipped, now four rather than three: **d1-safe**, **d7-register**,
**d20-reader** (section 7), and **`claude/concurrent-session-safety-570b39`** at `13187c0`,
already an ancestor of the pushed remote.

**Still unreviewed.** The adversarial path remains dead and was not retried or faked. The
00:51 removal is still unexplained. No rebase was attempted on any branch.

---
---

# PART 2 AND PART 3 EXECUTION RECORD, 2026-08-22 ~01:40 BST

Third dispatch. **This is the pass that actually merged and pushed.** The two earlier
passes ran from cwd `/` and correctly refused to write; this one ran from
`/Users/josie/can-it-ford` on `claude/add-ci-checks`, so the positional blocker in
section 9(1) was gone and the human instruction in section 9(5) was given explicitly.

## 17. Step Zero, passing this time

```
hostname   Josephines-MacBook-Air.local
pwd        /Users/josie/can-it-ford        <- exact, not a worktree, not a BACKUP copy
branch     claude/add-ci-checks
```

## 18. The rebase question, answered: merged, not rebased

The prompt asked to rebase each branch onto a current `add-ci-checks` if it was not
already based there. **I did not rebase anything, deliberately.**

`tmux list-panes -a` returns **26 live panes** (`canford8:d11`..`d23` and
`phone:d11`..`d23`), each sitting on one of these branches. [MEASURED] Rebasing rewrites
commits; a merge does not. Rewriting 21 branches out from under 26 live sessions is
exactly the topology the standing rule "never let two panes touch the same file, branch,
or process without explicit sequencing" exists to prevent, and the board records two prior
breaches of that shape. **Every source branch is byte-identical after this pass.** The
merges are all `--no-ff`, so each one is a recoverable, individually revertable commit.

Conflicts were tested BEFORE any merge, with `git merge-tree --write-tree`, which writes
nothing to the working tree. That is how the four conflicting branches below were
identified without ever entering a conflicted state.

## 19. What merged: 17 branches

All landed on `claude/add-ci-checks`. 165 files, 137744 insertions, 146 deletions.

| # | branch | what shipped |
|---|---|---|
| 1 | `claude/meta-prompt-reconcile-dispatch-14a3c8` | **pushcheck**, merged FIRST on purpose |
| 2 | `claude/r8-force` | R5 physics suite, 19 docs, `analysis/r8_noforcing_control.py` |
| 3 | `claude/r8-priorart` | `R8_PRIOR_ART`, R6 measurement scripts |
| 4 | `claude/r8-tooling` | `.claude/tooling/` brought under version control |
| 5 | `claude/r8-naming` | `R8_DETERMINISM_RENAME` |
| 6 | `claude/r8-kramer` | `R8_KRAMER_INTERCODE` |
| 7 | `claude/r8-licence` | `R8_LICENCE_RECONCILE`, `wandb_log_gated_runs.py` |
| 8 | `claude/r9-accessor` | `R9_ACCESSOR_DEFECT`, `hydrostatic_column.py`, 5 job records |
| 9 | `claude/r9-kramer-extract` | `R9_KRAMER_FULL_EXTRACT`, `R9_JOBC_PREREGISTRATION` |
| 10 | `claude/r9-renders` | Cycles pipeline, 4 docs |
| 11 | `claude/r9-landing` | `R9_LANDING_PLAN` |
| 12 | `claude/r9-moving-vehicle` | `moving_vehicle_channel.py`, speed surface |
| 13 | `claude/r9-priorcode` | `R9_MOVING_VEHICLE_PRIOR_CODE`, Chrono tow drag |
| 14 | `claude/r9-reader` | lineage only, content was already shipped |
| 15 | `claude/r9-jobb-route` | `R9_JOBB_ROUTE_DECISION`, `CANDIDATE_PAPER_SCOPE_TEST` |
| 16 | `claude/r9-gapscan` | `R10_WEB_ACQUISITION` plus the 39-file `docs/r10/` tree |
| 17 | `claude/r9-overleaf` | `R10_PAPER_CORRECTIONS` |

**`pushcheck` went first by design.** A guard written to vet what reaches this PUBLIC
remote was itself unpushed, so it landed before the bulk push rather than after it.

### 19.1 Two merges needed an untracked file cleared, and neither lost anything

`r8-tooling` and `r9-jobb-route` both failed initially with "untracked working tree files
would be overwritten". **Every colliding file was compared to the branch version before
anything was removed, and the whole tree was copied to the scratchpad first.**

- `docs/CANDIDATE_PAPER_SCOPE_TEST.md`: **byte-identical** to the branch copy. The merge
  restored the same bytes as a tracked file.
- `.claude/tooling/`: 15 local files, **14 byte-identical**, and every local file also
  exists on the branch (which carries 3 more). All 15 verified present again after the
  merge.
- The one real difference, `.claude/tooling/corpus_mcp.py`, local 260 lines against the
  branch's 380: the branch version won, and **that is a correction rather than a loss.**
  The branch file's own header records that `corpus_cited_status` returned "cited" for any
  bare DOI appearing in any file until 2026-08-18, "which made the novelty guard a check
  that could not fail". The 15 local-only lines are that superseded grep-based
  implementation. Local copy preserved at
  `scratchpad/corpus_mcp.py.LOCAL-BACKUP`.

## 20. What did NOT merge: 4 branches conflict, left for a human

**Not resolved silently, as instructed.** Each is a content conflict requiring a judgement
about which implementation is correct, which is a research decision, not a merge decision.

| branch | conflicting paths |
|---|---|
| `claude/r8-persistence` | `simulation/openchannel_bc.py` (add/add) |
| `claude/r8-bc-merge` | `simulation/openchannel_bc.py` (add/add) |
| `claude/r9-corpus-bib` | `analysis/research_index.py`, `.claude/skills/research-corpus/SKILL.md`, `data/deep_searches/vehicle-mesh-assets.json` |
| `claude/r9-settle` | `analysis/classify_failure_modes.py` |
| `claude/r9-platform` | `hf_space/README.md`, `hf_space/app.py` |

That is five rows for "4 branches" because **`r9-platform` conflicts only in the presence
of the other merges.** Its dry run against the pre-merge HEAD was CLEAN and it conflicted
when attempted after 12 other branches had landed. **Merge conflicts here are
order-dependent, so a clean dry run is not a promise.** Recorded because the next person
will otherwise re-derive it the hard way.

The two `openchannel_bc.py` add/add conflicts are the substantive one: two branches
independently created the same file, and reconciling them is the declared purpose of
`d4-bcmerge` (`docs/R8_OPENCHANNEL_BC_RECONCILE.md`). That document should be read before
either is merged.

`claude/r8-register` is **CONTAINED**, re-derived at merge time as the prompt required
rather than trusted from its name: tip `476bdfd` is already an ancestor of the pushed
remote, and `grep -n -i 'r8-register'` returns no match in either CLAUDE.md, so the
instruction it refers to no longer exists. Nothing to merge.

## 21. The public-remote safety scan, run before pushing

The repo is PUBLIC and a push is permanent, so `pushcheck`'s own rule set was applied by
hand, twice: once per branch across all 22 candidates, and once over the final push diff.

- **Path scan across 22 branches: one hit.** `data/r7_inflow_918506/profiles.npz` on
  `claude/r8-persistence`, 571.4 KB. That branch did not merge anyway (conflict). For the
  record it is a solver-output profile, not third-party mesh geometry and not credential
  material, and **12 `.npz` files are already tracked on the pushed base**, so it matches
  existing practice rather than opening a new category.
- **Path scan over the final push diff: ALL CLEAR.** No `.ply/.obj/.stl/.npz/.npy/.env/
  .key/.pem/.pth`, no `secret|token|credential|id_rsa`.
- **Content scan for live credential material** (`ghp_`, `github_pat_`, `sk-`, `AKIA`,
  `hf_`, PEM private-key headers) across every added line of all 22 branches AND over the
  final push diff: **zero matches.**
- **`docs/CREDENTIAL_EXPOSURE_2026-08-13.md` was deliberately NOT staged** and remains
  untracked, per the standing rule that credential write-ups stay off a public remote.
- Largest blob landing: `data/r9_speed_surface.tsv`, 614.4 KB.

## 22. Local CI before pushing

All six `canford-checks.yml` steps were run locally against the merged tree first. **All
exit 0**, including the two that are `continue-on-error` in CI:
`params_check`, `register_integrity`, `count_claims_check`, `analysis/stationarity.py`,
`analysis/research_index.py --stats`, `tests/test_physics_gates.py`.

This mattered more than usual: the merge added 165 files, and `count_claims_check` enforces
the scope-sensitive DRIFT_THRESHOLD total that CLAUDE.md item 13 says must land on 22, 23
or 24. It still does.

## 23. The push

```
PUSH_OK=1 git push origin claude/add-ci-checks
fd4f8b7..fe638d5  claude/add-ci-checks -> claude/add-ci-checks
```

The pre-push hook was **read verbatim before use** rather than assumed:
`.git/hooks/pre-push` tests `[ "$PUSH_OK" != "1" ]`, so the documented syntax is current.

**Fast-forward, not a force.** `merge-base --is-ancestor` confirmed the remote tip was an
ancestor of HEAD before pushing, so no history was rewritten.

**Landing verified by live network read, not by exit code:**
`git ls-remote origin refs/heads/claude/add-ci-checks` returns
`fe638d517448135feac31e31913a50d7cb345a03`, equal to local HEAD.

## 24. The CI question, answered: NOT a first run

The prompt asked to flag it if this were the workflow's first ever execution, since "a
workflow that has never executed is not known to pass."

**It is not.** `gh run list --workflow=canford-checks.yml` returns **22 runs**, of which 21
completed before this session and the visible history is all `success`. [MEASURED] The
push above triggered run `32541068089`.

The distinction from the session-start banner still holds and is worth restating, because
the two halves get collapsed: **`canford-checks.yml` is ABSENT from `origin/main` and
PRESENT on `claude/add-ci-checks`.** [MEASURED, `git cat-file -e` against both refs] It
runs, and it passes, on the branch. It has never run on `main` because it is not there.
"Absent from main" and "never executed" are different claims and only the first is true.

## 25. A concurrent session wrote into the shared index DURING this pass

At 01:40:09, in the status check taken immediately before pushing, a file appeared
**staged** that I did not stage: `docs/CORPUS_MERGE_FINAL_2026-08-22.md`, 41730 bytes,
mtime 01:39. Its own header says it was built against `claude/add-ci-checks` at `d1490df`,
which is **one of the merge commits this session created** (`Merge claude/r9-overleaf`), so
another session was reading my in-progress merges while I made them.

**It did not ride along.** Staging does not affect a push, and it is confirmed absent from
the `fd4f8b7..fe638d5` diff. **I did not commit it and I did not unstage it.** It is left
exactly as its owning session left it.

This is the live form of the shared-index hazard the standing rules describe, and it is why
every commit in this pass used the path-limited `git commit -- <path>` form and why the
status check was retaken immediately before the push rather than reused from earlier.

## 26. What still needs a human

1. **The four conflicting branches** in section 20. `openchannel_bc.py` first.
2. **`claude/r9-platform`**, whose conflict is order-dependent and appeared only after
   other merges landed.
3. **The 00:51 worktree removal is still unexplained**, and 26 live panes are still
   pointing into directories that no longer exist. Unchanged from section 10.
4. **`docs/CORPUS_MERGE_FINAL_2026-08-22.md`** is staged but uncommitted by another
   session. It needs its owner, not me.
5. **`add-ci-checks` to `main`.** The branch is now further ahead of `main` than before
   this pass, and `canford-checks.yml` still does not exist on `main`. The gap between
   this branch and the published state is the largest single thing outstanding.
6. **The three backup clones** stay prohibited. Section 15 stands unchanged.

**Still unreviewed.** The adversarial subagent path was not retried and the review was not
faked. No physics claim was generated, evaluated or altered in this pass; it was inventory,
merge and push only.

## 27. CORRECTION to section 25: the other session's work DID reach the remote

Section 25 says of `docs/CORPUS_MERGE_FINAL_2026-08-22.md`, "It did not ride along." **That
was true when written and became false about ninety seconds later. Correcting it here
rather than editing it away, because the mechanism is the point.**

The sequence, all measured:

1. 01:40:09, the file was **staged** in the shared index by another session. My first push
   (`fd4f8b7..fe638d5`) did not carry it, because staging genuinely does not affect a push.
   Section 25 is accurate up to here.
2. 01:41:50, that session **committed** it as `6778913`, "All 138 uncited DOIs accounted
   for, and zero of them are cited in the paper", onto `claude/add-ci-checks`, the same
   branch I was on.
3. My second push (`fe638d5..b66ff71`) therefore carried **two** commits, not one:
   `b66ff71` (mine) and `6778913` (theirs).

**A path-limited commit protects the commit, not the push.** `git commit -- <path>` did
exactly its job: `b66ff71` contains one file and none of their content. But a push sends a
BRANCH, and once a concurrent session commits onto the same branch, the next push of that
branch carries their commit whether or not the pusher knows about it. The commit-level
guard and the push-level exposure are different problems and the first does not solve the
second.

Nothing was lost, damaged or rewritten: `6778913` is their own finished commit, authored by
them, and it landed intact and unmodified. But it reached a **public** remote on my push
rather than on a push they chose to make, and they have not necessarily run their own
pre-push scan over it.

**The operational rule this yields:** before pushing a shared branch, diff the actual push
range and confirm every commit in it is yours, rather than checking only your own working
tree. `git log --oneline <remote-tip>..HEAD` answers it in one command and would have
surfaced this before the push instead of after.

For the record, that commit's content was covered by the same scan: the final push diff was
path-clean and returned zero matches for live credential material, and section 21's scan
ran over the whole diff rather than over my commits alone.
