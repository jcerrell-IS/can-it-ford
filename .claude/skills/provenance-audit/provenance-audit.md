---
name: provenance-audit
description: >
  Use this skill whenever Josie needs to establish whether a claim, number, figure,
  dataset, parameter, citation, or "done" milestone in the Can It Ford project is
  actually TRUE, traceable to a primary source, and safe to build a simulation or a
  deliverable on. Trigger on "audit this", "does this trace back", "where did this
  number come from", "verify this figure/claim/citation", "is this CLAUDE.md current",
  "reconcile the Claude Code sessions / panes", "run a background check on my figures",
  "what did that source actually say", "build me a Scite / DeepWiki / Consensus prompt
  to verify X", or any moment a specific number from a project file is about to be
  acted on, published, put on the poster, or told to Kumar. Also trigger PROACTIVELY,
  without being asked, the instant a "DONE", a milestone, a parameter value, or a
  cited threshold is about to be restated as fact from a summary rather than from the
  live artifact. This skill is the layer that decides what counts as TRUE before
  anything downstream uses it.
---

# PROVENANCE AUDIT

The purpose of this skill is narrow and load bearing: **decide what is true, on evidence, before Josie builds a simulation or a deliverable on top of it.** It exists because the single most damaging failure in this project has never been a bad file. It has been a written summary (a prior chat, a Perplexity report, a CLAUDE.md, an audit doc) being restated as current fact without a live check against the actual code, CSV, commit, or paper. That exact failure has recurred at least three times with the same shape ("X already works, here is the exact number", false on direct grep). This skill makes that failure structurally hard to repeat.

---

## 0. THE PRIME DIRECTIVE

**An audit never terminates in self-review. It always terminates in a live read of a primary source.**

If the last thing done before stating a verdict was "the summary looks internally consistent", the audit is not finished. The last thing must be a `grep`, a `git show`, a file read, a `web_fetch` of the actual paper, a Scite tally, a DeepWiki answer, or a terminal command output. No exceptions. A claim never outranks a checkable source that sits above it in the hierarchy below.

Do not let this skill itself become the new over-trusted document. This file records what was true when it was written. Any specific number in the Known-Error Register (Section 8) is re-checkable and must be re-checked if it is about to be acted on again.

---

## 1. THE SOURCE HIERARCHY (higher tier always wins)

| Tier | What | Examples in this project | Trust |
|---|---|---|---|
| **T1 Primary artifact** | The thing itself, machine-checkable | live `.py` on Vista, `scenario_sweep.csv`, `git show <hash>`, terminal stdout, the actual PDF of a paper, a Scite/DeepWiki tool result | Ground truth |
| **T2 Active ground-truth doc** | A file whose job is to track current state, and that is actively maintained | `SESSION_STATE.md`, `kumar_july9_update/STATUS.md`, the current canonical `CLAUDE.md` (once verified) | Provisional, verify against T1 |
| **T3 Synthesized claim** | Anything written by summarizing something else | prior chat summaries, Perplexity/research `.md` files, the "Master Instructions v6" doc, an old README, a memory entry | Suspect until reconciled |

Rules:
- A T3 claim cannot promote a milestone, a parameter, or a result to "true". Only T1 can.
- When T2 and T3 conflict, T2 wins only if T2 was verified against T1 more recently. Otherwise both get re-checked.
- **The "Master Instructions v6, July 7" brief is T3.** It predates the July 8 to July 17 corrections and it still lists the render milestones as "DONE" (Part 3, asks 1 and 2). Those exact "DONE" claims were later complicated or retracted. Do not quote v6 as current status. Use it for stable context (who people are, deadlines, learning protocols) only.

---

## 2. THE FORENSIC ROOT-CAUSE METHOD (per claim)

For any single claim under audit, answer these five, in order, and write the answer down.

1. **What exactly is claimed?** State it as one falsifiable sentence with the number in it. Vague claims cannot be audited. "The MPM works" is not auditable. "`can_it_ford_L2_mpm.py` ran to completion and produced verdict=FORD at peak_x_disp=0.0038m" is.
2. **What tier supports it right now?** If the only support is T3, stop and mark UNVERIFIED before going further. Do not restate it.
3. **Does the cited source still exist, and does it say this?** Go find it. File on Vista or GitHub or Drive. Equation in the actual paper. Row in the actual CSV. If the source cannot be located, the claim is ORPHAN. If the source exists but does not say the thing, the claim is CONTRADICTED.
4. **When and how did the claim enter?** Trace it back through commits and chats to the first appearance. This is what "at the root" means. A claim fixed in chat but left uncorrected in a file (README, STATUS, CLAUDE.md) will re-enter later. Find the file it is frozen in.
5. **What upstream misread caused it?** Almost every false claim in this project came from conflating two adjacent things. Name the conflation. Examples that actually happened:
   - "script imports `gs.materials.MPM`" (an edit or an aspiration) got read as "an MPM run produced a verdict" (never happened).
   - "Azhar 2023 uses friction 0.55" (a physical Coulomb coefficient) got fed into Genesis `coup_friction` (a numerical coupling impulse coefficient) as if they were the same quantity.
   - "the drift is friction-invariant" (real number) got read as a physics finding, when a near-massless floating body produces friction-invariance as an artifact (normal force approx 0, so mu times N approx 0 for any mu).

**Verdict for each claim:** VERIFIED (T1 confirms) / UNVERIFIED (only T3 supports) / CONTRADICTED (a higher tier disproves) / ORPHAN (cited source does not exist).

---

## 3. THE KILL LIST (removing invalid sources at the root)

A false claim keeps coming back as long as the document that carries it still exists and still reads as current. So the audit does not just correct a claim in chat, it hunts the carrier file.

When a source is CONTRADICTED, ORPHAN, or is actively inducing a bug (a stale script, a mis-headered CSV, a superseded CLAUDE.md), mark it a **KILL candidate** and record: full path, what it falsely asserts, what supersedes it, and why deleting it is safe.

**Deletion protocol (respect the confirmation-pause rule):**
- Never delete without showing Josie the KILL list and getting an explicit "yes, delete".
- Prefer archive over delete when the file has any forensic value (it shows how an error propagated). Move to a clearly dated `_ARCHIVE_stale_<date>/` folder rather than `rm`.
- Hard-delete only true duplicates and known-false single-claim files with no other content.
- After removal, grep the repo and Drive for the same false string to confirm it is not frozen in a second file. A correction that leaves a copy behind is not a correction.

Precedents from this project of carrier files that had to be caught: `PROVISIONAL_STATUS.md` re-asserting the retracted FORD/0.0038m milestone after it was retracted in chat; a `designsafe-staging/` folder frozen July 2 with overclaiming MPM prose; un-suffixed `08_GeoElements_Project_Brain.md` superseded by its `_UPDATED` twin; a Vista copy of `box_sdf_collider_setup.py` at 5,207 bytes that was older than the git version at 6,450 bytes and would silently skip the walls fix.

---

## 4. CLAUDE.md CURRENCY AUDIT

Because Kumar and every Claude Code pane read whatever CLAUDE.md is on disk, a stale one is an active risk the entire time it sits there.

1. **Find every CLAUDE.md-class file that exists** across chat project files, `~/.claude/CLAUDE.md` (user-global) and the repo-root `.claude/CLAUDE.md` on Mac, Vista, and LS6. There have been several: a v3 comprehensive (July 13), the "Master Instructions v6" (July 7), a "consolidated canonical v3" (July 15). Version numbers alone do not tell you which is newest. Read dates and content.
2. **Establish exactly one canonical file.** Everything else is archived per Section 3.
3. **Diff the canonical file against T1.** Any status claim, parameter value, or "DONE" in it gets checked against the live code/CSV/commit. The canonical CLAUDE.md is only allowed to contain T1-verified status, plus stable non-status context (paths, rules, people, deadlines).
4. **Confirm the Safe Resume Protocol is present** in `~/.claude/CLAUDE.md` on each machine (restate mid-task, check git status and running processes before continuing after `--continue`/`--resume`, stop and report if anything is mid-write). A pane that resumes without it will assume a clean boundary that may not exist.
5. **Never let the canonical file assert a solver, a scene provenance, or a milestone that the diff in step 3 did not confirm.** The abstract-vs-code gap (MPM claimed, SPH run) lived in files for weeks precisely because no one diffed the doc against the code.

---

## 5. CLAUDE CODE SESSION / PANE RECONCILIATION

Multiple Claude Code panes run in parallel across Vista, LS6, and Mac. A correction in one pane is invisible to the next unless it landed in git or in `SESSION_STATE.md`. Reconciliation asks, per pane: **what did this pane do solely, what state did it leave, and does a T1 artifact confirm it.**

For each pane / session under review:
1. **What it touched.** Read `SESSION_STATE.md` (the cross-terminal handoff file, one header per pane with last command, status, next action). This is T2; verify against T1.
2. **What actually landed.** `git log --oneline`, `git status`, `git show <hash>` for anything the pane claims to have committed. A commit message is T3; the diff is T1. Confirm the diff matches the message (a message claiming MPM over an SPH diff is a red flag).
3. **What is uncommitted or process-local.** A fix that was edited into a file but never committed does not exist for any other pane. A fix that ran on a compute node but was scp'd rather than committed can be silently older than git (the 5,207 vs 6,450 byte case). Always check byte size and mtime against the committed version, not just presence.
4. **What is still running.** `squeue -u jcerrell0629`, `kill -0 $(cat *.pid)`, background job PIDs. A pane that "finished a sweep" may have a job that died on a closed terminal.
5. **Impact on now.** State plainly how this pane's work changes current ground truth, and flag any place two panes edited the same file (collision risk). Never edit a file another pane may own without checking `git status` first.

Cross-pane pattern already documented: an 8-commit gap was once split 4 from a chat session and 4 from a parallel Claude Code session (README rewrite, `render_frames.py`, LICENSE, confinement walls in `box_sdf_collider_setup.py`). Both Track 1 and Track 2 crashes traced to the same underlying cause (P2G operations near domain boundaries), which only became visible by reconciling the two panes against each other, not reading either alone.

---

## 6. THE ARTIFACT BACKGROUND CHECK (every figure and dataset needs a trail)

Nothing goes on the poster, in the paper, to Kumar, or to DesignSafe without a trail back to a primary artifact. Build and maintain a **provenance manifest** (a table, one row per artifact) with these columns. If any column cannot be filled, the artifact is ORPHAN and does not ship until it can.

| Column | What it must contain |
|---|---|
| Artifact | figure or dataset filename (`phase_space.png`, `scenario_sweep.csv`, a specific number) |
| Source data | the exact CSV/NPZ/log it came from, plus a content hash or byte size + mtime |
| Generating script | the exact `.py` and its commit hash, so the figure is reproducible |
| Params | the parameter values live at generation (depth, velocity, n_grid, rho, coup_friction, DRIFT_THRESHOLD) |
| Solver + scene | SPH vs MPM, synthetic-box vs real-reconstruction, which track |
| What it shows | the one claim the artifact actually supports |
| What it does NOT show | the claim a viewer might wrongly infer (the guardrail line) |
| Caveat label | one of: SPH-PILOT (synthetic), MPM-REAL, INVALID (do not ship), UNVERIFIED |

**Orphan and mislabel detection is the point.** Concrete cases this catches in the current project:
- The 30.4 percent L1/L2 agreement result was produced on a synthetic flat-plane / box-water / box-vehicle SPH scene, not a real reconstruction. Caveat label = SPH-PILOT. It is the motivating pilot, not the final result. A figure of it labeled as the final MPM result is a mislabel and must be relabeled or pulled.
- The friction-invariant drift near 0.395 to 0.400m is the signature of a floating near-massless body, produced while vehicle mass was wrong. Caveat label = UNVERIFIED until rerun with correct mass. Do not present it as physics.
- The v3 sweep at n_grid=128 (60 runs) is INVALID: `truck_trimmed.ply` is a surface-only splat with no interior, so `solidify_columns` produces a hollow body at fine grid resolution, giving `density_plausible=False` on all rows and systematically under-buoyant physics. Caveat label = INVALID (do not ship). Any figure drawn from it is pulled.
- The genuine finding (deep, slow water rates FORD under L1's D×V product but shows real drift under L2, because near-buoyancy reduces normal force in a way D×V cannot represent) was independently confirmed by two separate Claude Code sessions. That is a strong provenance trail. Still label it by the track and grid that produced it, and confirm the mechanism against literature (Section 7, Consensus/Scholar prompt) before it is a headline claim.

---

## 7. CROSS-TOOL VERIFICATION PROMPT CONSTRUCTION

Each open gap gets sent to the tool built to close it, with a prompt explicit about (a) the exact claim, (b) the exact quantity/units the answer must be expressed in, and (c) an instruction to flag a negative rather than infer a plausible positive. Vague prompts to research AIs are how ungrounded claims entered in the first place. **Perplexity output is T3 and is never verification; it is a lead that must then be checked in Scite/DeepWiki/the actual paper.**

### Tool routing

| Gap type | Tool | Why |
|---|---|---|
| Does a paper actually support a claim / a number / an equation | **Scite** | citation-context tally (supporting/contrasting/mentioning), full-text snippets by DOI |
| What would a reviewer cite against a simplification | **Consensus** or **Scholar Gateway** | surfaces contrasting/limiting evidence, not just confirming |
| What does a repo's code actually do / a crash cause / an API | **DeepWiki** | grounded Q&A over the actual repo (kks32/mpm-engine, Genesis, PhysGaussian) |
| Broad orientation, "what exists in the field" | Perplexity (T3 only) | fast synthesis, then re-verify every specific number in Scite |

### Ready templates (fill the bracket, paste into the named tool)

**Scite, citation-support check (the general form):**
> Using citation context and full text, does [PAPER, DOI] actually support the claim that [EXACT CLAIM WITH NUMBER AND UNITS]? I need (a) whether the paper states this at all, (b) the exact quantity and units the paper expresses it in (depth, velocity, D x V in m2/s, Froude number, displacement in m, or friction coefficient), and (c) the supporting vs contrasting vs mentioning tally. If the specific value or equation number I named does not appear in the paper, say so explicitly and do not infer a substitute.

**Scite, the DRIFT_THRESHOLD re-verify (keep on file, this was the canonical error):**
> Does peer-reviewed flood-vehicle stability literature define instability by an absolute lateral displacement or drift distance in meters (near 0.05 m), as opposed to depth, velocity, depth x velocity (D x V), incipient/critical velocity, or Froude number? Specifically: does Smith, Modra and Felder 2019 (DOI 10.1111/jfr3.12527) contain an Equation 6, and is it a lateral-drift criterion or a limiting-Froude/flow-velocity relationship? Confirm or deny the attribution of a 0.05 m drift threshold to that paper. Also report what Xia et al. 2014 and Shah et al. 2018 actually use as their criterion. Flag any negative explicitly.

**Scite, coup_friction sourcing (open conceptual gap):**
> Azhar et al. 2023 (DOI 10.1111/jfr3.12885) reportedly uses a vehicle friction coefficient of 0.55 in a DualSPHysics + Chrono flood simulation. Confirm (a) the exact value and (b) that it is a physical Coulomb friction coefficient between vehicle and bed, not a numerical solver-coupling parameter. Report the tally and the full-text context in which 0.55 appears.

**Scite, Shand / AR&R thresholds:**
> Confirm whether Shand et al. 2011 (Australian Rainfall and Runoff Revision Project 10, Stage 2, Report P10/S2/020) establishes vehicle stability thresholds as a depth x velocity product (m2/s) and confirm the class values (small passenger, large passenger, 4WD) and their limiting depths. Report whether the 0.30 / 0.45 / 0.60 m2/s values are attributable to this source.

**DeepWiki, kks32/mpm-engine FloodScene + the live blocker:**
> In the kks32/mpm-engine repo: (1) What does warpmpm.vehicle.FloodScene output per frame (displacement, yaw, pitch, roll) and how is the rigid vehicle coupled to the MPM water? (2) The function that converts a Gaussian-splat point cloud into MPM particle bodies (solidify_columns or equivalent) produces a hollow body when the input .ply is surface-only and the grid is fine (n_grid=128), because many grid columns capture a single surface point. What is the intended handling for surface-only meshes, and does the engine expect a watertight or volumetric input? (3) During gravity settling, what boundary or initialization behavior would cause water particles to drift toward one domain edge (low-x) rather than settling symmetrically? (4) What are the intended units and scale conventions for domain bounds, particle spacing, and vehicle box dimensions?

**DeepWiki, Genesis MPM crash (Track 2, deprioritized but the traceback is a deliverable):**
> In Genesis (Genesis-Embodied-AI), MPM solver: (1) What conditions during substep_pre_coupling p2g (particle-to-grid) produce CUDA_ERROR_ILLEGAL_ADDRESS? (2) Is particle tunneling through car-scale rigid bodies at grid_density=64 a known issue, and what grid_density resolves it? (3) What is the correct MPM.Liquid plus rigid-body coupling API, including needs_coup and coup_friction, and does the solver pad domain bounds inward relative to the bounds I specify?

**DeepWiki, PhysGaussian bridge + license:**
> In XPandora/PhysGaussian gs_simulation.py: what does the extraction pipeline output (mpm_init_pos, mpm_init_cov, mpm_init_vol), what are the opacity_threshold and fill_particles defaults, and what license (if any) governs reuse of this code in a separate public repository?

**Consensus / Scholar Gateway, adversarial (defend the simplifications):**
> What are the documented limitations and validity conditions of (a) representing a vehicle as a rigid box or rigid-linked-block proxy rather than true geometry in SPH/MPM flood-interaction simulations, and (b) using a closed reflecting domain with no inlet/outlet to approximate open-channel flood flow? What is the strongest objection a reviewer would raise to each?

**Consensus / Scholar Gateway, validate the genuine finding:**
> Is it an established mechanism that increasing water depth reduces a vehicle's effective normal force (via buoyancy / partial flotation) and therefore its resistance to lateral sliding, in a way that a depth x velocity hazard product does not capture? Return supporting and contrasting evidence with the physical quantity each source uses.

---

## 8. KNOWN-ERROR REGISTER (do not rediscover these; re-verify before acting)

Each row is a claim that has already been forensically resolved once. Status is as of the last verification. Re-run the check in the "verify by" column before the claim is acted on again, because any of these can drift.

| Claim / item | Resolved finding | Root cause (the conflation) | Verify by |
|---|---|---|---|
| "MPM already works, verdict=FORD, peak_x_disp=0.0038m" | FALSE. No such file/run. Live grep showed SPH.Liquid only. Neither MPM track has produced a verdict. | "script edited toward MPM" read as "MPM run completed" | live grep of the live script on Vista; git log |
| DRIFT_THRESHOLD = 0.05m attributed to Smith 2019 Eq. 6 | FALSE attribution. Eq. 6 is a Froude/flow-velocity relationship. No 0.05m drift criterion exists in any peer-reviewed flood-vehicle paper. Reframe as an internal numerical onset-of-motion detector (cite Xia 2014, Shah 2018 for underlying physics). | "there must be a paper for this" led to grabbing a plausible equation | Scite DRIFT_THRESHOLD template |
| coup_friction = 0.55 | Value 0.55 is real in Azhar 2023 (physical Coulomb friction). But Genesis coup_friction is a numerical coupling coefficient, not Coulomb friction. Feeding one into the other is an open modeling question, not a settled fact. | physical friction coefficient conflated with solver coupling parameter | Scite coup_friction template + DeepWiki Genesis coupling API |
| coup_friction "fixed to 0.4/0.55 in session 5" | Was still 0.0 as of July 8, fixed live that day. Do not trust any "fixed in session N" claim by its confidence. | uncommitted/unverified chat claim treated as landed | git blame / grep live file |
| rho = 604 vs 115.7 on the vehicle box | rho left over from a prior box size after a sedan-scale resize; correct value for a 1390kg sedan target is 115.7. | box dimensions edited without updating density and mass (coupled variables) | grep live script; recompute mass = rho * box volume |
| Friction-invariant drift ~0.395 to 0.400m | Signature of a floating near-massless body (N approx 0), produced with wrong mass. UNVERIFIED as physics until rerun with correct mass. | numerical artifact read as a physics finding | rerun with corrected rho, check if invariance survives |
| The 30.4% L1/L2 agreement "finding" | Legitimate but produced on synthetic box/plane SPH geometry. It is the motivating pilot, NOT the final reconstruct-to-decide result the abstract describes. | pilot result presented as final result | check scene provenance of the generating run |
| v3 sweep, n_grid=128, 60 runs | INVALID. Surface-only .ply solidifies hollow at fine grid, density_plausible=False on all rows, under-buoyant. Do not ship any figure from it. | surface mesh treated as volumetric body | grep density_plausible column in the sweep CSV |
| Deep-slow-water L1/L2 divergence (near-buoyancy reduces normal force) | GENUINE, independently confirmed by two Claude Code sessions. Still confirm the mechanism against literature before headlining. | none; this one is real, just needs external grounding | Consensus/Scholar buoyancy template |
| W&B API key in commit 50eff29 | Rotation was CLAIMED but never confirmed by comparing the live .netrc key against the exposed key. Treat as UNCONFIRMED. | "rotated" restated without the comparison actually run | diff the .netrc key vs the key in commit 50eff29; rotate on wandb.ai if they match |
| "Master Instructions v6, July 7" milestones marked DONE | T3 doc, predates July 8 to July 17 corrections, lists retracted render milestones as DONE. | old brief treated as current status | this whole skill; use v6 for stable context only |

---

## 9. VERIFIED CLAIMS BECOME THE SIM SPEC (the generative payoff)

The audit is not only defensive. A claim that reaches VERIFIED becomes a **locked input** to the simulation Josie actually wants to run. This is how "make it accurate" turns into "get the sim I want":
- Verified vehicle mass and density (recomputed, coupled) lock the buoyancy and the normal force.
- Verified friction, with the coup_friction-vs-Coulomb question resolved, locks the coupling.
- Verified domain scale and boundary behavior lock the flow regime.
- Verified DRIFT_THRESHOLD framing (numerical detector, not a cited physical threshold) locks how a verdict is declared and defended.
- A valid sweep (not the hollow v3) locks the phase-space figure.

Keep a short **LOCKED SPEC** list at the top of the provenance manifest. Only VERIFIED items go on it. The simulation is built from the LOCKED SPEC, and the poster/paper cite from the manifest. Nothing that is UNVERIFIED, CONTRADICTED, ORPHAN, or INVALID is allowed to silently become a sim input or a claim.

---

## 10. AUDIT OUTPUT FORMAT

Every audit returns one table, plus a KILL list if any carrier files were found, plus a set of prompts to dispatch for anything still open.

| Claim | Tier supporting | Source exists? | Says it? | Verdict | Root-cause conflation | Action |
|---|---|---|---|---|---|---|

Verdicts: VERIFIED / UNVERIFIED / CONTRADICTED / ORPHAN / INVALID. Every UNVERIFIED and ORPHAN row must have a dispatched prompt (Section 7) or a live command attached. Every CONTRADICTED and INVALID row must have a KILL or relabel action. The audit is not done while any row's action is "trust the summary".
