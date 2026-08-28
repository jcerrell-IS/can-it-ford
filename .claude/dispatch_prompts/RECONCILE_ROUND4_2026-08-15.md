# RECONCILIATION AND DISPATCH, ROUND 4
2026-08-15 18:05 CEST. Built per META_PROMPT_reconcile_and_dispatch.md.

Source: live git across all 13 worktrees and the tmux transcripts, read
directly. No number below is restated from a session summary; each is read from
a commit body, a file, or a command output. Where two sessions disagree, the
disagreement is reported as a finding, not silently resolved.

**Safe Resume checks, run first:** main tree at exactly 26 dirty entries,
unchanged from baseline; coordinator worktree clean; zero local background
processes; 14 tmux windows alive; both TACC ControlMaster sockets expired after
~17h idle, so remote reads need `ssh vista` / `ssh ls6` once. Nothing mid-write.

---

# PHASE 1 — RECONCILIATION

## LIST A. UNPUSHED WORK, by session and branch

All thirteen worktrees are **dirty = 0**, so every piece of work is committed.
Exposure is therefore "committed but on one local branch with no remote copy",
not "uncommitted in a working tree". No `.bundle` files were produced.

| D | branch | unpushed | pushcheck |
|---|---|---|---|
| 1 | `claude/rtfd-test-phase-1-4-569130` | **13** | **BLOCK** |
| 2 | `claude/fork-vista-triage` | 11 | OK |
| 3 | `claude/credential-exposure-...-DO-NOT-PUSH` | 8 | SKIP by design |
| 4 | `claude/fork-register-reconcile` | **23** | OK |
| 5 | `claude/fork-three-class` | 19 | OK |
| 6 | `claude/fork-render-3class` | 19 | OK |
| 8 | `claude/moving-vehicle-exploratory-2026-08-11` | **0** | pushed |
| 9 | `claude/fork-moving-driver` | **29** | OK |
| 10 | `claude/fork-scene` | 16 | OK |
| 11 | `claude/fork-validation` | 15 | OK |
| 12 | `claude/fork-protocol` | 23 | OK |
| 13 | `claude/fork-chrono-eval` | 12 | OK |

**Total 188 commits with no remote copy**, of which 8 (D3) are deliberately
local. D1 is blocked on `docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`: the repo
is public and D3 reports credentials still unrotated, so a file naming which
machines hold them is a targeting document even though it contains no values.

D8 is the only session with nothing outstanding.

## LIST B. RESOLVED ERRORS (a later session fixed an earlier claim)

1. **mu = 0.55 as an anomalous lab value.** Before: relayed by the coordinator
   to six sessions as a spring-balance rubber-mat outlier. After: D2 `64a2e67`
   "0.55 is not an outlier, 0.3 was never measured"; corroborated D4 `75eb2e9`,
   D11 `d55a55f`, D6 `7d43b97`. Martinez-Gomariz 2017 measured 0.52-0.62 by the
   same method. The real gap is measured-vs-adopted, not us-vs-field.
2. **R7 "63.3x, non-monotone, third instance."** Before: coordinator, single
   20-frame run. After: refuted by D9 `278ea81`, retracted by D11 `8e5900d`,
   withdrawn by D12 `0133082`. Cause: `R7_FRAMES` defaults to 20 and the stack
   rings with a ~100-frame period.
3. **D9's 6.07x traction-margin spread.** After `5e421dd`: **1.94x**, and the
   gate-error ordering **inverted** (63.28/94.44/157.06 increasing became
   72.88/49.75/34.01 decreasing).
4. **PPC as the convergence mechanism.** D9 `5abdbec`: "fixed PPC = 8 is
   REFUTED, and more particles made it worse."
5. **The band as a particle support width** (a coordinator relay of Baumgarten
   & Kamrin). D9 `a740338`: "the band is a spatial integration error, but it is
   NOT a particle support width."
6. **"Three-way fork of r7_mirror.py"** (coordinator). D4 `fc5c784`: "two
   scripts, not three, and no fork occurred."
7. **D10's vehicle-independence headline.** `691276b` WITHDRAWN, 8 blocking
   issues confirmed.
8. **D13's structural argument against Chrono.** `8b86795` withdrawn:
   "GetNormal works on Chrono's own mesh."
9. **D12's "the clamp barely mattered."** `565b43e` superseded by its own re-run
   as a short-settle artifact.
10. **Chrono defect architecture-specificity.** D11 `009a3a5` and D13 `d6146c9`:
    x86 reproduces 100%/0%/0%, so it is general, not aarch64.

## LIST C. STILL-OPEN ERRORS (self-flagged, unfixed anywhere)

**C1. THE CANONICAL YARIS HULL IS ALREADY PUBLIC. Highest severity.**
D3 `20c06a6`, verified independently by the coordinator against `origin/main`:
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`, blob `46a9f730`,
**12,445,769 bytes, present on the public remote**, plus three further derived
`.ply` files and 15 rendered `.mp4`/`.gif`. E8's operative rule forbids
committing derived NCAC/CCSA geometry publicly without written permission or a
confirmed licence, and E8 itself records the Yaris's licence side as
**UNRESOLVED**. So D6 spent the entire evening correctly enforcing an E8 hold on
new frames whose source hull is already public. **Nobody owns this.**

**C2. Twelve to fifteen credentials, ZERO rotated.**
D3 `5ba182d`: sweep complete, 89/89 Mac roots, 12 credentials; `fc99e30`: "the
count is 15 not 8". D3 is diagnosis-only by design, so rotation has no owner and
has not happened. D3 also self-reported leaking an HF token into its own
transcript while investigating (`c4ef6a5`, bounded to exactly one).

**C3. The Zhao 2019 BC does not hold a level.**
D10 `1905233`: "the Zhao BC outflow works, the level does NOT hold. Second
negative." This is the gate on every realistic-domain result and it is failing.
D10 `a536aab` found the likely cause: "the Anura3D team impose BCs at GRID
NODES; mine is particle-level." The fix is identified, not implemented.

**C4. Chrono segfaults on ingested terrain.**
D13 `893357b`: "Attempted to drive a vehicle on ingested terrain. Assembles,
then segfaults." Unresolved. This is the realistic-environment path.

**C5. The R7 scene is not actually symmetric.**
D4 `1cfa5e0`, T1 measurement: `r7_mirror.py`'s premise is false. `by/h` is not an
integer at any resolution (42.809, 57.079, 85.618), so `np.arange` truncates the
+y end and the body sits low by `h*frac(by/h)/2`, predicted from lattice
arithmetic and measured at t=0 with no physics, agreeing to 6-7 significant
figures. **D4 then refuted its own hypothesis**: symmetrising drives the t=0
offset to 3e-09 m and does NOT remove the mirror discrepancy (g48 unchanged to
0.11%). So the defect is real, is not the mechanism, and the control's stated
guarantee ("any asymmetry is a solver defect with nothing to interpret") is void
even though its measurements still measure something.

**C6. `settle_frames=8` is still the shipped default.**
D11 `af9d293`: "settle is 8 frames and NO artifact records it." D12 `f5cb012`:
"the vehicle is still falling when recording starts." Diagnosed everywhere,
changed nowhere, because `sim_standing.py` is shared and its sha256 stamps runs.

## LIST D. DANGEROUS CROSSOVERS

**D-1. Three sessions, three answers on R7 monotonicity.** D9 `278ea81` monotone
decreasing at 3 rungs / 200 frames. D11 `fae3ab6` **"third pass, N=5 per grid:
the asymmetry is NON-MONOTONE, and both my earlier conclusions were wrong."**
Coordinator: monotone through g96, then a sharp break at g104. These are the same
physical quantity measured three ways with three answers, and **none of the three
has been reconciled against the other two**. D4 `1cfa5e0` adds that "the ratio is
not a statistic" and D11 `3b1973f` that "the ratio metric INVERTS with run
length". This is the single most tangled item in the bundle.

**D-2. D1 and D9 disagree about what PPC-refutation reaches.** D9 `5abdbec`
refutes fixed PPC = 8 as the mechanism. D1 `197e044`: "The Steffen citation is
NOT wrong, and **D9's PPC refutation does not reach J15**." Both are careful and
both may be right about different scopes, but no document states the boundary.

**D-3. Does the determinism floor grow with frames?** Coordinator g112 ladder:
floor 0.0057 → 0.0201 → 0.0937 → 0.288 across 20/50/100/200 frames, i.e. it
grows. D9 `4ef1f50`: "Every g112+ result now carries a floor, and **the floor
does NOT grow with frames here**." Different scenes, same claim shape, opposite
sign. Unreconciled.

**D-4. "Initial-condition driven" is being used for two different things.**
D5 `b512853`: "the verdict flip IS initial-condition driven, and reproduces
across architectures." D9 `c6eb8d2`: "CLAUDE.md item 5 SURVIVES the settle
control." One is a verdict flip, the other a displacement magnitude, and they are
one careless sentence away from being read as contradictory.

**D-5. E8 hold versus already-public source.** D6 enforces an E8 hold on new
frames (`0f4e62e`, verified with `git check-ignore -v`). D3 shows the source hull
and 15 rendered videos are already public. Two sessions acting correctly under
incompatible pictures of the same rule.

**D-6. `analysis/` is a shared write surface.** D5 wrote
`analysis/preflight_hull_guard.py` and `analysis/ensemble_seed_runner.py`; D6
owns `analysis/render_*.py`; D4 added `simulation/r7_mirror_sym.py`; D9 modified
`analysis/traction_budget.py`; D12 owns `analysis/stationarity.py`. No collision
occurred because worktrees are isolated, but **all 188 commits merge into one
tree eventually**, and `analysis/` is where they will collide.

---

# PHASE 2 — OPEN ITEMS MAPPED TO RESEARCH

| Open item | Document | The specific finding |
|---|---|---|
| **C1** public hull | Register E8; D3 `20c06a6` | E8 forbids public derived NCAC/CCSA geometry absent written permission; E8 records the Yaris side as UNRESOLVED. NHTSA-hosted copies carry a distribution statement; CCSA and GMU grant nothing; DOI 10.13021/G8JS5D has an EMPTY rights field. |
| **C3** BC level drift | Zhao, Bolognin, Liang, Rohe & Vardon 2019, Comput. Fluids 179:27-33, doi 10.1016/J.COMPFLUID.2018.10.007 | The BC is imposed at **grid nodes** in Anura3D. Companion: Remmerswaal, Bolognin, Vardon, Hicks & Rohe 2019, "Implementation of non-trivial boundary conditions in MPM" (wall-penetration catalog #15), same team. Validation target: Zhao, Liang & Martinelli 2017, dam-break with MPM, doi 10.1016/J.PROENG.2017.01.041. |
| **C4** Chrono terrain segfault | Pazouki, Jayakumar & Negrut 2016, "Investigation of the Vehicle Mobility in Fording" (moving-rigid catalog #39) | **The Chrono authors published on fording.** D13 `2ad8121` records it evaluated Chrono without reading it. Also Mazhar/Pazouki/Rakhsha/Jayakumar/Negrut 2018, doi 10.1016/j.jcp.2018.05.013, the Chrono FSI formulation. |
| **C5/D-1** R7 validity | Undermind wall-penetration report | "**No formally validated force-convergence criterion** exists"; conventions only. So a bespoke symmetry control is the right instrument, but its own construction must be verified, which D4 did and it failed. |
| **C6** settle | Undermind settling report, 68 papers | "No universal frame count or force-settling threshold emerges." Named algorithms: **Chodera 2015** automated equilibration detection, doi 10.1101/021659; **Flyvbjerg & Petersen 1989** blocking, doi 10.1063/1.457480; Grossfield 2018 best practices, doi 10.33011/livecoms.1.1.5067. |
| Resolution adequacy | Undermind wall-penetration; artifact `211aad60` | `H/dp >= 5` is the DualSPHysics minimum to capture the largest wave **at all** (Roselli 2018, Altomare 2017). Canonical g64 = **2.000**; matched-dx = **3.500**. Both below. |
| Render quality | Artifact `genesis_vs_mpmengine_fluid_research.md` Q5 | **splashsurf**, marching cubes for SPH/MPM output, weighted Laplacian smoothing to remove the blobby look. `pysplashsurf` verified installing on LS6 x86 (00:17). Wheels exclude aarch64. Chain: arXiv 2403.11156, SPH → SplashSurf → Blender. |
| Novelty claim | Moving-rigid catalog | Fording simulated **four times**: Wasfy 2015 DETC2015-47142; Pazouki 2016; Khapane & Ganeshwade 2014 SAE 2014-01-0936; He 2026 doi 10.1115/1.4071177. MPM already on a road: Zhou 2025 doi 10.1063/5.0276643; Chen 2022 DETC2022-89632. |

## Research findings NOT yet operationalized (highest leverage)

1. **Kramer et al. 2021**, Energies 14(2):269, doi 10.3390/en14020269 — a
   **public downloadable** floating-sphere heave-decay dataset at ~0.3%
   experimental uncertainty. D12 `518bb3d` named it and stopped: "it needs a
   record shape the module lacked." **Nothing has been run against it.** This is
   the only external validation target the project has.
2. **Ransley et al. 2020**, CCP-WSI Blind Test Series 3, doi
   10.17736/ijope.2020.jc774 — a **blind** comparative study. D11 `b340f35`
   flagged the protocol; nobody has applied it. It is the direct answer to
   "every gate is self-consistency" (CLAUDE.md item 6).
3. **Kramer 2016's critical orientation is 45 degrees**, not 0 or 90. D5
   `5dd7332` named orientation as the axis it never swept. The **worst case is
   the one nobody runs**.
4. **Al-Qadami et al. 2021** full-scale **Toyota Yaris** floated at 0.40 m under
   ~11 kN. Caution: D4 `75eb2e9` says "the Yaris datum is the old misattribution
   again" — verify before use.
5. **splashsurf** — verified installable, never run.

---

# PHASE 3 — ANGLE CHECK, ALL SIX LENSES

**Physics/validation.** The genuinely unchecked quantity is **buoyancy against
an external measurement**. Every gate is internal. Kramer 2021 is a public
dataset with a sphere, i.e. an analytic displaced volume, and the SDF-collider
path already validates buoyancy to 7.3-7.7%. Running the project's own solver
against a 0.3%-uncertainty external dataset has never been attempted and is the
highest-value physics item available.

**Software engineering/reproducibility.** `settle_frames=8` is shipped, is a
guess, is diagnosed by three sessions, and no artifact records it (D11
`af9d293`). Separately, `analysis/` is a shared write surface across five
branches (D-6) and no merge order exists.

**Literature positioning/novelty.** Materially changed. "Nobody has simulated
vehicle fording" is **false** and was close to shipping on a video caption (D2
`7e6dc51` caught it). The defensible claim narrows to MPM-plus-validation. This
is not yet written into the paper anywhere.

**Visualization/communication.** Two blockers cleared and unused: the asphalt PBR
maps already sit in `assets/` unreferenced by any render module, and splashsurf
installs on LS6. Both were verified last night; neither has been applied.

**Licensing/provenance.** This is the lens with the live problem, and it is C1.
The mesh question was asked and answered as "unresolved", then the file shipped
to the public remote anyway. Also unchecked: the ambientCG assets are CC0 (fine),
but no LICENCE/attribution file records that in-repo.

**Infrastructure/deployment.** Three real risks. LS6 **cannot run warpmpm** (its
only copy is a 6-line stub raising `RuntimeError`), which wasted hours before it
was found. `srun --jobid=` into an idev **requires `--overlap`** or the step
hangs and dies. Both ControlMaster sockets expire and take every session's remote
access down at once, which killed running work last night.

---

# PHASE 4 — DISPATCHES

Eight dispatches. Each writes to a distinct branch and a distinct file set. None
depends on another's output.

**Recommendation: run all eight as FRESH sessions**, not compactions. Context
fill ranges 0% to 94%; the dispatch carries the continuation context; and last
night demonstrated that lossy relays are this project's characteristic failure
mode. Exception: **D9 is currently running at 14% and must be allowed to finish
before its window is reused.**

The operating protocol from the meta-prompt is included verbatim in each
dispatch below.

---

## THE OPERATING PROTOCOL (verbatim in every dispatch below)

```
OPERATING PROTOCOL:

Before starting: check git log, .remember/ files, and the research
citations you were given, in that order. Do not duplicate work already
done elsewhere in this bundle.

When you hit an obstacle: try a fix. If it doesn't work, try a second,
genuinely different approach, not a variation of the same one. Before
concluding you're stuck, check whether an available connector or subagent
resolves it:
  - DeepWiki, for any question about how a library/repo actually behaves.
    Treat its answer as a hypothesis to verify against source, not fact.
  - The physics-skeptic subagent, before finalizing any claim involving a
    percentage, force, verdict count, or distance. If it's unavailable this
    session, say so explicitly and mark the claim unreviewed, do not fake
    the review.
  - Wolfram, for any physical parameter, unit conversion, or equation
    before it becomes a stated claim.
  - Scite, for any citation, DOI, or threshold before it's written as
    settled.
  - register_integrity.py (or the project's equivalent), before any commit.

Prefer proceeding on a clearly-labeled, reversible assumption over
stopping. State the assumption explicitly, in the commit message or the
write-up, so it can be revisited later without re-deriving it from
scratch.

Tag every factual claim by its source: read directly, recalled from
context, or inferred. Tag every solver/engine claim by which engine it
applies to. Never state a number from memory when you could check it live.

Keep working on everything else in your scope even if one specific thing
below is blocked, do not let one blocker stop the whole session.

Flag, rather than silently proceed past, only these four things:
1. You are about to discard, overwrite, or force-push over uncommitted
   work you did not create and cannot verify is safe to lose.
2. You've found two independently-reported results that genuinely
   disagree about the same physical quantity, not just different framing
   of the same thing, and resolving which is correct requires a judgment
   call, not just more data you can go get yourself.
3. You are about to edit a canonical file outside your declared scope.
4. A genuine hard-stop case: real financial cost, an exposed credential,
   a destructive/irreversible action, or anything matching the project's
   existing standing hard rules.

When you flag one of these: write it clearly to a named file (not just an
inline comment), keep working on everything else in your scope that isn't
blocked by it, and do not treat the flag as ending the session.

Write with an engineer/scientist's discipline throughout: state
assumptions before acting on them, prefer a falsifiable test over a
plausible-sounding claim (a no-forcing control, a held-fixed comparison,
a second seed), and write up a result the same way whether it confirms or
overturns something already published.

Before any push: confirm the target branch, stage explicit paths only,
never a blanket add, and confirm the push actually landed afterward,
don't just assume the command succeeding means the remote updated.
```

---

## R4-1 — E8 LICENCE EXPOSURE (run first; blocks the paper and the DOI)
**Mac · new worktree `fork-e8-licence` · branch `claude/fork-e8-licence`**

SCOPE. Write only to `docs/E8_LICENCE_EXPOSURE_2026-08-15.md` and
`docs/E8_REMEDIATION_OPTIONS_2026-08-15.md`. NEVER touch: the register, any
`.ply`, any other branch, `CLAUDE.md`, `sim_standing.py`, `analysis/`. Do not
delete, rewrite, or force-push anything. You are producing a decision document,
not performing the remediation.

WHERE THIS LEFT OFF. D3 commit `20c06a6` on
`claude/credential-exposure-2026-08-13-DO-NOT-PUSH` found, and the coordinator
independently verified against `origin/main` at 18:02 today, that
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`, blob `46a9f730`,
**12,445,769 bytes, is on the public remote**, together with
`failed_reconstructions_2026-07-25/car_mesh.ply` (1,200,447 B),
`car_mesh_rescaled.ply` (1,200,447 B),
`yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply`, and **15 rendered
`.mp4`/`.gif`** including `figures/hero_g64_m1100.mp4` and five
`kumar_july9_update/*.mp4`.

THE RESEARCH THAT BEARS ON IT. Register E8's operative rule: do not commit
derived NCAC/CCSA geometry to the public repo without written permission or a
confirmed licence. E8 itself records the canonical Yaris's side of the
NHTSA-safe / CCSA-licence-silent line as **UNRESOLVED**. D3 records that
NHTSA-hosted copies carry a distribution statement, CCSA and GMU grant nothing,
and DOI 10.13021/G8JS5D has an **empty rights field** and resolves to a
validation slide deck rather than a waived dataset. Note the standing memory
fact: this GitHub repo is PUBLIC and GitHub has served removed blobs by SHA even
after a history rewrite, so deletion alone does not undo exposure.

FIRST STEP. Establish provenance per file, not per directory: for each of the
four `.ply`, determine whether it derives from NCAC, from CCSA, or from neither,
and cite the evidence. They may not share one answer.

DEFINITION OF DONE. One document stating, per file: origin, which licence
applies, whether the current public state violates E8, and the remediation
options with their consequences (leave, remove-from-HEAD, history rewrite,
seek written permission), including the explicit fact that a rewrite does not
retract what GitHub has already served. Recommend one. Do not execute it.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-2 — CREDENTIAL ROTATION EXECUTION LIST
**Mac · existing worktree `fork-credentials-DO-NOT-PUSH` · same branch, STAYS UNPUSHED**

SCOPE. Write only to `docs/CREDENTIAL_ROTATION_CHECKLIST_2026-08-15.md` on the
existing DO-NOT-PUSH branch. NEVER: push, print a credential value, delete an
export line, or rotate anything yourself. `ls-remote` for this branch must stay
empty.

WHERE THIS LEFT OFF. D3 `5ba182d`: sweep complete, **89/89 Mac roots**, 12
credentials, and the public repo is clean on the credential axis. `fc99e30`:
"the count is 15 not 8". `c4ef6a5`: transcript surface complete, 666 files, the
leak bounded to exactly one. **Nothing has been rotated.** Diagnosis is finished;
execution has no owner.

FIRST STEP. Convert the inventory into a numbered, ordered execution list for
Josie: one row per credential, columns for service, holding file, file mode,
whether the location is cloud-synced, whether it is in git history, and the
**exact rotation URL or CLI command** she runs. No values. Ordered by blast
radius, worst first. Put the count and the zero-rotated fact in the first line.

DEFINITION OF DONE. A checklist Josie can execute top-to-bottom without opening
any other document, plus a one-line statement of what remains exposed until she
does. Then stop: this dispatch never rotates anything.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-3 — RECONCILE THE R7 CONTROL (three sessions, three answers)
**Mac · new worktree `fork-r7-reconcile` · branch `claude/fork-r7-reconcile`**

SCOPE. Write only to `docs/R7_RECONCILIATION_2026-08-15.md` and
`simulation/r7_reconcile/` (new directory). NEVER edit `simulation/r7_mirror_sym.py`
(D4's), `sim_standing.py`, or any other branch.

WHERE THIS LEFT OFF. The same quantity has three answers and none is reconciled:
- D9 `278ea81`: monotone decreasing, 3 rungs, 200 frames.
- D11 `fae3ab6`: "third pass, **N=5 per grid: the asymmetry is NON-MONOTONE**,
  and both my earlier conclusions were wrong."
- Coordinator: monotone through g96 (0.1701 / 0.0490 / 0.0244), then a sharp
  break, g100 passing and g104 failing at 1.5810 and 1.6027.
Two further findings bear directly on all three:
- D4 `1cfa5e0` (T1, measured): the scene is **not** symmetric. `by/h` is not an
  integer at any resolution (42.809, 57.079, 85.618), `np.arange` truncates the
  +y end, the body sits low by `h*frac(by/h)/2`, predicted from lattice
  arithmetic and measured at t=0 with no physics to 6-7 significant figures.
  **D4 then refuted its own hypothesis**: symmetrising drives the t=0 offset to
  3e-09 m and leaves g48 unchanged to 0.11%.
- D11 `3b1973f` and D4 `1cfa5e0`: the **ratio is not a statistic** and "INVERTS
  with run length", because an instability inflates numerator and denominator
  together.

THE RESEARCH. The Undermind wall-penetration report establishes there is **no
formally validated force-convergence criterion** in SPH/MPM/PIC-FLIP, only
conventions, so a bespoke symmetry control is a defensible instrument **provided
its own construction is verified** — which D4 checked and it failed.

FIRST STEP. Do not run anything yet. Tabulate all three sessions' raw numbers
side by side with their n_grid, frame count, repeat count, and statistic
definition. Most of the disagreement is likely definitional.

DEFINITION OF DONE. One document that either reconciles the three into a single
statement with its scope, or states precisely which measurements are not
comparable and why. If a run is needed, use an absolute asymmetry with a
repeat-run spread, never a ratio. Report N per cell.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-4 — GET 188 COMMITS SAFE
**Mac · coordinator worktree `concurrent-session-safety-570b39`**

SCOPE. Git operations and `docs/PUSH_LEDGER_2026-08-15.md` only. NEVER: push D1
or D3, edit any session's files, or merge any branch into another.

WHERE THIS LEFT OFF. 188 commits have no remote copy across 11 branches, every
worktree is clean (dirty = 0), and no `.bundle` exists. `pushcheck` is OK on
nine branches, BLOCK on D1 (`docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`), SKIP
on D3 by design. D8 has 0 unpushed.

FIRST STEP. Before any push, `git bundle create` every one of the 11 branches to
a dated directory outside the repo and verify each with `git bundle verify`. A
bundle is the only thing that makes this work survivable if a worktree is lost,
and it needs no authorization.

DEFINITION OF DONE. 11 verified bundles on disk; a ledger naming each branch,
its commit count, its pushcheck verdict and its bundle path; and for D1, a
concrete proposal to split `FLAG_CREDENTIAL_EXPOSURE` onto its own DO-NOT-PUSH
branch so the other 12 commits become authorizable. **Push nothing without
Josie's per-branch go-ahead**, and confirm any push that is authorized with
`git ls-remote --heads origin`, never with an exit code.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-5 — PHOTOREAL RENDER, BOTH TRACKS
**Mac · existing worktree `fork-render-3class` · branch `claude/fork-render-3class`**

SCOPE. `analysis/render_*.py`, `analysis/flood_water_optics.py`,
`figures/**`. NEVER: `sim_standing.py`, the register, `simulation/`, another
branch.

WHERE THIS LEFT OFF. D6 shipped the matched-dx video (`abd5b2a`, `337bb04`) and
the warpmpm-track video (`33df3ca`), then spent the evening correcting captions
(`15f2e54`, `01b5767`, `b6eb4ee`, `7d43b97`). Four render defects remain, all
read from source by the coordinator:
1. Water invisible: `k = 1300 /m` at SSC 13000 mg/L gives black-disc visual
   range **0.00 m**, with `k EXTRAPOLATED above the 670 mg/L linear bound`, i.e.
   the optics model runs **19x past its own validity limit**.
2. The vehicle has no material model:
   `sh = clip(n @ LIGHT,0,1)*0.6 + 0.4; return sh * base` in
   `render_multigeom_rollout.py`. Lambert plus constant ambient. The **water**
   gets Schlick + Beer-Lambert + GGX; the **car** gets two lines.
3. `assets/Asphalt015_1K-JPG_Color.jpg`, `_NormalGL.jpg`, `_Roughness.jpg` are a
   complete ambientCG CC0 PBR set **already in the repo**; grep of all three
   render modules returns the HDRI at 8 sites and the asphalt maps at **0**.
4. The caption occupies roughly 70% of every frame.

THE RESEARCH. `~/Claude/reu/genesis_vs_mpmengine_fluid_research.md` Q5:
**splashsurf** (InteractiveComputerGraphics) is a marching-cubes surface
reconstructor purpose-built for SPH/MPM particle output, with weighted Laplacian
smoothing "specifically to remove the typical bumps that make raw
particle-derived surfaces look blobby". Our water is currently a per-column
max-z heightfield because warpmpm has no free-surface field. **`pysplashsurf`
was verified installing and importing on LS6 at 00:17**; wheels cover
x86_64/i686/armv7l but **not aarch64**, so LS6 not Vista. Published chain:
arXiv 2403.11156, SPH → SplashSurf → Blender. Render target: Zhou et al. 2025,
Physics of Fluids doi 10.1063/5.0276643, tire-pavement hydroplaning in MPM.

FIRST STEP. One frame, end to end: rollout particles → splashsurf on LS6 → mesh
→ render with the asphalt maps and the HDRI. Prove the chain before doing 90.

DEFINITION OF DONE. Both videos re-encoded with a real water surface, an
automotive clearcoat on the vehicle, the textured road, an SSC inside the 670
mg/L bound with its visual range stated, and a legend of at most six lines. State
in the legend that the texture is **visual only** and never implies spatially
varying friction the solver does not have.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-6 — THE OUTFLOW BC AT GRID NODES
**Mac · existing worktree `fork-scene` · branch `claude/fork-scene`**

SCOPE. `simulation/fork_scene/**` and `docs/BC_*`. NEVER: `sim_standing.py`,
the register, `analysis/`, another branch.

WHERE THIS LEFT OFF. D10 `e91b138` validated the Zhao BC on closed-form cases
3/3. Then `1905233`: "**the Zhao BC outflow works, the level does NOT hold.
Second negative.**" Then `a536aab` found the likely cause: "**the Anura3D team
impose BCs at GRID NODES; mine is particle-level.**" The fix is identified and
not implemented, and every realistic-domain result is gated behind it.

THE RESEARCH. Zhao, Bolognin, Liang, Rohe & Vardon 2019, Computers and Fluids
179:27-33, doi 10.1016/J.COMPFLUID.2018.10.007. Read alongside the companion by
the same team: **Remmerswaal, Bolognin, Vardon, Hicks & Rohe 2019,
"Implementation of non-trivial boundary conditions in MPM for geotechnical
applications"** — Bolognin, Vardon and Rohe are three of the five Zhao authors,
so this documents how that group actually implements a non-trivial BC.
Validation case: Zhao, Liang & Martinelli 2017, "Numerical Simulations of
Dam-break Floods with MPM", doi 10.1016/J.PROENG.2017.01.041. Per CLAUDE.md this
is a **translation** into warpmpm, not a port.

FIRST STEP. Read Remmerswaal 2019 and state, before writing code, exactly what
"impose at grid nodes" means in their scheme and what it changes about your
particle-level implementation.

DEFINITION OF DONE. Either a grid-node BC that holds a constant level under
steady inflow-equals-outflow, with the tolerance stated, or a documented reason
it cannot, with the closed-form evidence. Every later slope result must be able
to cite that tolerance.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-7 — EXTERNAL VALIDATION, THE FIRST ONE THIS PROJECT WOULD HAVE
**Mac · new worktree `fork-external-validation` · branch `claude/fork-external-validation`**

SCOPE. `simulation/external_validation/**` and
`docs/EXTERNAL_VALIDATION_2026-08-15.md`. NEVER: `sim_standing.py`, the
register, `analysis/`, another branch.

WHERE THIS LEFT OFF. Nowhere. This is the highest-leverage unused research
finding in the corpus. D12 `518bb3d` named the dataset — "the locked regression
case has a name" — and stopped because "it needs a record shape the module
lacked". **Nothing has ever been run against an external measurement.**

THE RESEARCH. **Kramer et al. 2021, "Highly Accurate Experimental Heave Decay
Tests with a Floating Sphere: A Public Benchmark Dataset for Model Validation of
Fluid-Structure Interaction", Energies 14(2):269, doi 10.3390/en14020269**,
approximately **0.3% experimental uncertainty**, publicly downloadable. A sphere
has an analytic displaced volume, so it isolates buoyancy plus added mass plus
damping — exactly the coupling this project cannot otherwise validate. Note it is
a **different paper** from the Kramer 2016 watertightness work already in the
register at line 228; same author, do not merge them. Context: CLAUDE.md item 6
records that **no gate in this project is a physics validation**, and the
Undermind moving-rigid report states plainly that **no validated vehicle-fording
MPM chain is identified**. Second, stronger protocol if time allows: Ransley et
al. 2020, CCP-WSI Blind Test Series 3, doi 10.17736/ijope.2020.jc774 — a
**blind** comparison, which is the direct answer to a self-consistency critique.

FIRST STEP. Obtain the dataset and characterise it: geometry, fluid properties,
release height, sampling rate, stated uncertainty. Do not touch the solver until
you can state what a pass would look like numerically.

DEFINITION OF DONE. The project's SDF-collider path run against Kramer 2021,
with the heave-decay curve compared to the published data, an error stated
against their 0.3% uncertainty, and an honest verdict either way. A failure
written up as clearly as a success. This would be the project's first external
validation of any kind.

[OPERATING PROTOCOL — paste the block above verbatim here]

---

## R4-8 — NARROW THE NOVELTY CLAIM BEFORE IT SHIPS
**Mac · new worktree `fork-novelty` · branch `claude/fork-novelty`**

SCOPE. `docs/NOVELTY_POSITIONING_2026-08-15.md` and
`docs/RELATED_WORK_DRAFT_2026-08-15.md`. NEVER: `paper/`, the register,
`CLAUDE.md`, another branch. You draft; you do not edit the paper.

WHERE THIS LEFT OFF. D2 `7e6dc51`: "**Fording HAS been simulated four times:
narrow the novelty claim before it ships on a video.**" D4 `2fbd9cd`: "fording
has been simulated four times, and MPM is already on a road", and `cce9d28`:
"resolve three fording DOIs, and the abstracts force two corrections". D13
`2ad8121`: "**I evaluated Chrono without reading Chrono's own fording paper.**"

THE RESEARCH, from the Undermind moving-rigid-body and multi-resolution
catalogs, none of it previously cited in this project:
- **Wasfy, Wasfy & Peters 2015**, DETC2015-47142, multibody + SPH vehicle water
  fording. Appears in **two** catalogs.
- **Pazouki, Jayakumar & Negrut 2016**, "Investigation of the Vehicle Mobility
  in Fording" — the **Chrono authors**, already in register A-1 for rigid
  coupling.
- **Khapane & Ganeshwade 2014**, SAE 2014-01-0936, "Wading Simulation,
  Challenges and Solutions".
- **He et al. 2026**, doi 10.1115/1.4071177, with experimental validation.
- **Zhou et al. 2025**, Physics of Fluids doi 10.1063/5.0276643, tire-pavement
  hydroplaning **in MPM**.
- **Chen et al. 2022**, DETC2022-89632, MPM deformable terrain for off-road
  mobility.
Also: the Undermind report states "**no validated vehicle-fording MPM chain is
identified**" and that the records "do not establish an experimental basis for
the 1.5 m/s rule". Both belong in limitations as citable, not asserted.

FIRST STEP. Verify each of the six DOIs against Scite or Crossref before using
it. D4 `cce9d28` found the abstracts force two corrections, and D4 `75eb2e9`
warns that the Al-Qadami Yaris datum is "the old misattribution again". Do not
inherit a citation from this document without checking it.

DEFINITION OF DONE. A related-work section positioning this project honestly
against all six, plus one paragraph stating exactly what remains novel. "Nobody
has simulated vehicle fording" must appear nowhere. The surviving claim is
narrower and should be written as such.

[OPERATING PROTOCOL — paste the block above verbatim here]
