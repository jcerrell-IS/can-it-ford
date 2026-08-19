# CLAUDE.md sections moved out, 2026-08-19

**These are the VERBATIM sections removed from `CLAUDE.md` on 2026-08-19 by slot
d20-reader.** Nothing was edited, summarised or dropped. Every line below appeared in
`CLAUDE.md` immediately before the move, and the move was verified line by line.

Provenance: moved out of `CLAUDE.md` at repo HEAD `505aef7`,
source sha256 `0b3f4fb06e2abcde`, 171 lines across 5 sections.

**Why these five and not others.** A section was eligible only if its working is
demonstrably held elsewhere, or the condition it describes is closed:

| section | why it was safe to move |
|---|---|
| AUGUST 15 REPO-CLONE INVENTORY | its own text says the full working is in the register addendum L1 to L7, and that was verified: the register carries it from line 665 |
| AUGUST 8 CLOSED ITEMS AND GATE INVENTORY | titled CLOSED. The two still-operative parts were kept in `CLAUDE.md` as stubs |
| Nested ./can-it-ford/ duplicate, GONE | the section states the hazard no longer exists; verified by `ls -d` |
| MacOS-MCP screenshot permission | a resolved one-off configuration fix |
| A NOVELTY CLAIM ... IS REFUTED | its operative rule is duplicated in the corpus section of `CLAUDE.md`, which was checked before moving |

**What was NOT moved, and why.** The AUGUST 4 2026 AUDIT (378 lines, 38 percent of the
file) was left in place. Its items are the most-cited content in the project and several
carry corrections that INVERT their own opening paragraph (items 12, 15 and 13 all begin
with a claim their later text withdraws). Any mechanical split that keeps the first
paragraph and moves the correction would restore a withdrawn claim. Cutting it needs
paragraph-level judgement on sixteen load-bearing corrections, and that should not be done
by one session with no adversarial reviewer available. It is named as a separate unit.

---

## AUGUST 15 2026, REPO-CLONE INVENTORY AND CORPUS GAP CLOSURE

Measured live 2026-08-15 by a local Claude Code session. Full working in
docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md addendum L1 to L7, and in
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/` files
`05_Repo_Clone_Inventory_2026-08-15.tsv`,
`06_Phase_C_Near_Duplicates_2026-08-15.tsv` and
`07_Sprint6_REU_Knowledge_RepoLevel_2026-08-15.tsv`.
Nothing was deleted, moved or renamed anywhere in this pass.

1. THE SPRAWL IS 28 LOCATIONS AND 31.6 GB. 15.9 GB of that, almost exactly
   half, is non-canonical. Split: 17 NON_GIT_COPY, 4 ORPHANED_CLONE, 3
   STALE_BACKUP, 3 CANONICAL, 1 VENV_EXCLUDE. `~/can-it-ford` is canonical and
   sits exactly at origin/main `1a868f3`. A self-documenting pointer now
   exists at `<corpus>/00_CANONICAL_REPO`.
   DO NOT test clone provenance by asking each clone whether HEAD is an
   ancestor of origin/main. That reads the CLONE'S OWN cached remote ref,
   which is stale by construction in a backup. Four clones answer "0 ahead, 0
   behind" while sitting at four different commits. Resolve the canonical SHA
   once from the live remote, then interrogate the canonical repo's object
   database about the others.
   "3 CANONICAL" is not three copies of one repo. `can-it-ford-demo` and
   `can-it-ford-paper` are canonical for DIFFERENT remotes.

2. THE CLAUDE.AI PROJECT'S GITHUB SYNC DOES NOT REACH THIS REPO. Its two
   synced sources live under `jcerrell-IS/mpm-engine`, confirmed by
   `gh repo view` to be a fork of `kks32/mpm-engine`. This repo is
   `jcerrell-IS/can-it-ford`. Committing into `docs/` here will NOT appear in
   the Project's knowledge base, so do not plan a handoff around that.

3. TWO UNPUSHED COMMITS SIT OUTSIDE THIS REPO. `~/can-it-ford-demo` `4d228d9`
   is SINGLE-COPY and not on GitHub, and by its own commit message it is the
   joint-AR&R-rule fix, so the public demo repo still serves the superseded
   bare-hazard-product rule. `~/can-it-ford-warpmpm-continue` `4924940` is one
   ahead of its remote branch but is duplicated on a local branch here, so it
   is not at risk.

4. `make_phase_space.py` FORKS ON THE 0.60 BOUNDARY OPERATOR. Seven copies
   including this repo carry `'FORD' if h <= 0.60`; two pre-history-purge
   trees carry `h < 0.60`. `data/scenario_sweep.csv` has exactly 4 rows at
   L1_haz == 0.60, so the operator decides 4 of 70. NOT CLAIMED that any
   published verdict count turns on it: the live 10-column CSV reads NO-FORD
   at all four, and its L1_verdict split is 14 FORD against 56 NO-FORD, which
   is the joint AR&R rule and not this script's bare-product rule. The
   exposure is that `designsafe-staging/` is the publication-bound tree. The
   two files differ by ONE BYTE of length, 4267 against 4266, so no
   size-delta pass can see this and a checksum pass says only "different".

5. THE LONG-BLOCKED `CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07` WAS NEVER
   BLOCKED, ONLY MISFILED. Real path is
   `~/Archive/_ZZZ_DELETE_THESE_2026-07-17/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07`.
   6 files, 44 KB, 2 of them .DS_Store. Of the 4 real files exactly 1 is new
   content. Do not re-open this as a gap.

6. REU_Knowledge IS A VENDORED-CODE CACHE, NOT A RESEARCH STORE, so the
   "1,296 unread items" gap is re-scoped rather than ground through. Live
   count is 1,541 files and 30 MB across 15 subtrees, and the extension
   profile is 817 .py, 172 .h, 73 .cc, 48 .rst, 35 .tcc against only 276 .md.
   Upstream identity confirmed from LICENSE/README/pyproject, not from folder
   names: `newton` is NVIDIA Newton, `mpm` is CB-Geo MPM, plus genesis-world,
   gsplat, gns, diffmpm, lbm, x2sim and Kumar's own LearnMPM. The research
   layer at its root was already fully indexed by the 2026-08-14 Round 3
   provenance audit, 37 union artifact ids, zero unique to that location.
   It is now indexed at repository level, 16 rows for 1,541 files.

---

## AUGUST 8 2026 CLOSED ITEMS AND GATE INVENTORY

Every SHA below was verified live with git log / git show on 2026-08-08, not
carried from a summary. PRJ-3702 is deliberately absent: zero hits in docs/
and in this file, confirmed twice, so there was no open item to remove.

CLOSED
- Rigid-mass citation :851-853 -> :856, commit 35b7ed0. The mass sum is
  kernels/mpm_solver_warp.py:856; 851 and 852 are the np.zeros allocations
  and 853 is the loop header, so the old range cited allocation plus a loop
  header rather than the sum itself. Three sites fixed. Stamped artifacts
  under data/coupling_validation/ still carry the old range by design.
- Failure-mode classifier has run on all 17 canonical runs, commit fae3388.
  841d666 then tracked data/failure_modes_by_run.json and
  data/all_runs_inventory.csv, both silently gitignored until then.
- four_rung_ladder.md and _GRIDAWARE.md no longer cite
  failure_modes_result.json as independent confirmation, commit 841d666.
  Verified live: both now read the claim as a measurement, not a confirmation.
- simulation/validate_coupling_force.py is committed. TWO SHAs, do not
  conflate: 541d832 first ADDED the file, 057b3e9 landed the C1-SDF/C3
  harness content including the working C3 nan-guard.
- Warp MPM figure label, commit b844118. Commit 7390168 makes the IDENTICAL
  change on branch claude/verify-execute-code-changes-d89fd8 and is not an
  ancestor of main, so cherry-picking it returns empty, which is success and
  not a conflict. Do not re-attempt it.

GATE INVENTORY, do not rebuild these from scratch
.claude/checks/params_check.py already runs four literature-cited gate
categories, landed by aa754dc (NOT 720d1e2, which is a later inertia-re-wire
block): lit:geometry_bbox, lit:sound_speed_cfl, lit:resolution_convergence_gci
and lit:manifest_provenance. TRAP: only three exist as literal strings.
lit:resolution_convergence_gci is assembled at runtime by
params_check.py:259 from the gate= argument at :417, so grep -F for it
returns nothing and a naive audit concludes the gate is missing. It is not.
Run the script and read its output instead of grepping for the tag.
SECOND TRAP: four is the count of literature-cited TAGS, not of gates. Six
lit: tags exist (also lit:floor_restitution and lit:mass_inertia_cog), and
the four gate= categories are a DIFFERENT four: floor_restitution,
geometry_bbox, mass_inertia_cog, resolution_convergence_gci. Grepping gate=
returns names that do not match this list; that is expected, not drift.
Line numbers verified live 2026-08-08 by running the script.

STILL OPEN, not closed
- The Overleaf token is off local disk but NOT revoked. ~/can-it-ford-paper
  was deleted 2026-08-08 after confirming local main and overleaf/main were
  both 92ce4de, nothing ahead of the remote, no stashes, so Overleaf retained
  all 5 commits. Verified the same day: no .git/config under ~ contains an
  olp_ string, and this repo's own overleaf remote URL carries no credential.
  Two consequences: a push to overleaf now PROMPTS for credentials, so a
  fresh Overleaf Git authentication token is needed before the next push; and
  the old token stays valid server-side until rotated in Overleaf account
  settings.
  **CORRECTED 2026-08-15, the deletion half of this item is STALE.**
  `~/can-it-ford-paper` EXISTS. Directory birth 2026-08-08 05:13, 40 files,
  HEAD `6466dfa` "Update on Overleaf." (2026-07-31), which is four commits
  PAST the `92ce4de` recorded above. It is clean, 0 ahead and 0 behind its own
  origin/main, and equals this repo's `overleaf/main` ref. The CREDENTIAL half
  above still holds and was re-verified 2026-08-15: all five
  `can-it-ford*/.git/config` files are free of any `olp_` string, tested for
  presence only, no value read. See register L4.

---

## Nested ./can-it-ford/ duplicate directory, GONE as of 2026-08-12

**STATUS CHANGE, verified live 2026-08-12 by `ls -d /Users/josie/can-it-ford/can-it-ford`:
the nested duplicate NO LONGER EXISTS.** Every exclusion of `./can-it-ford/` in this
file, in skill files and in audit scripts is now a no-op rather than a load-bearing
guard. Do not conclude from a passing grep that the duplicate was handled; there is
nothing left to handle. The section below is retained as history, because the hazard
returns the moment anyone re-clones into the repo root, and because several committed
scripts still carry the exclusion. Do not cite it as a live hazard without re-running
that `ls` first.

### Historical, when the duplicate existed

There is a second copy of this project nested at ./can-it-ford/ inside the repo
root. It is NOT a synced mirror. Verified live 2026-07-29 by filecmp: paper/
conference_101719.tex and paper/can_it_ford_references_IEEE.bib are byte-identical
between root and nested, but data/scenario_sweep.csv, vehicle_params.py and
scripts/ford_sweep_driver.py all DIFFER. Root is canonical for every one of them.
Always confirm pwd is /Users/josie/can-it-ford, not the nested copy, before
reading a parameter or a verdict count, and exclude ./can-it-ford/ from repo-wide
greps or you will get two conflicting answers and no way to tell which is live.

---

## MacOS-MCP screenshot permission, 2026-08-06

MacOS-MCP `Snapshot` with `use_vision=true` fails with `cannot identify
image file`. Cause: macOS Screen Recording permission not granted to
Claude Desktop / its helper process. Fix: System Settings > Privacy &
Security > Screen Recording > enable Claude, then relaunch the app.
`Snapshot` without vision (accessibility tree: open apps, windows,
interactive elements) works without this permission and needed no fix.

---

## A NOVELTY CLAIM IN THIS PROJECT'S OWN TOOLING CORPUS IS REFUTED

The corpus document "AI Research Tools and Scientific-Computing Infrastructure" states that
"no published Material Point Method (or SPH) simulation of a road vehicle in floodwater yet
exists ... so Can It Ford is genuinely first-of-kind". It attributes that to a SUBAGENT
ABSENCE RESULT and names its own falsifier.

**The falsifier has been met.** This file already records four prior fording or wading
simulations, and the 2026-08-19 deep-search layer adds at least four more, including
`[Lyu23]` `10.1016/j.compfluid.2023.106144`, an entirely particle-based 3D SPH vehicle
wading model. A document that shaped this project's priorities rested a novelty claim on an
absence found by a search nobody could inspect. Do not cite that claim.

---
