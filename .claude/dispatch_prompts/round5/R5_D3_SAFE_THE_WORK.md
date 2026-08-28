# D3 — GET 188 COMMITS SAFE, AND UNTANGLE THE REGISTER
worktree `.claude/worktrees/r5-safekeeping` · branch `claude/r5-safekeeping`
YOU OWN: `docs/PUSH_LEDGER_*`, `bundles/`. Write nowhere else.
NEVER push. NEVER merge one branch into another. NEVER overwrite a shared doc.

## WHY YOU EXIST
**188 commits across 11 branches exist in exactly one place each.** Every
worktree is clean, so it is all committed, but nothing is bundled and nothing is
pushed. A lost worktree loses a night of work. `git bundle` needs no
authorization from anyone and is the cheapest insurance available.

`pushcheck` passes on nine branches. **D1's old branch is BLOCKED** on
`docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`: the repo is public and
credentials are unrotated, so a file naming which machines hold them is a
targeting document even though it contains no values. **D3's old branch is
DO-NOT-PUSH by design.**

**The register collision, unresolved and dangerous.** A live session wrote a
2026-08-15 addendum (+96 lines, seven L-items on repo-clone sprawl) and a
CLAUDE.md correction (+73 lines) **directly in the MAIN checkout, uncommitted**,
while the old D4 worktree holds **22 unpushed register commits**. The two files
are 752 vs 1455 lines and branched from the same commit. Both edits are additive
and in different regions, so they merge cleanly IF sequenced. If anyone
checks out or copies one over the other, that side vanishes with no conflict
marker. This is the 2026-08-07 failure waiting to repeat.

## FIRST STEP
`git bundle create` every one of the 11 branches into a dated directory
OUTSIDE the repo, and `git bundle verify` each. Do this before anything else.

## DEFINITION OF DONE
(a) 11 verified bundles on disk. (b) A ledger: branch, commit count, pushcheck
verdict, bundle path, sha256. (c) A written sequencing plan for the register
that names who commits first and what each side must confirm survives. (d) A
proposal to split the credential flag file onto its own DO-NOT-PUSH branch so
the other 12 commits become authorizable. Execute nothing that pushes.

## STANDING PROTOCOL (identical for all four, read once)
Before starting: read `/Users/josie/can-it-ford/.claude/tooling/ERRORS_AND_RESOLUTIONS.md`,
then `git log`, then `/Users/josie/can-it-ford/.claude/state/round5_board.md`.
Do not duplicate a sibling; append your own row to the board after each unit.

SELF-SUFFICIENCY. Decide for yourself. If a path, file, number or citation is
uncertain, GO FIND IT rather than asking: `corpus_resolve`/`corpus_search` for
any research file, `scite` or `scholar-sidekick` for any DOI, `wolfram` for any
unit or parameter, `deepwiki` for library behaviour (treat as hypothesis, verify
against source), `canford-tacc` for anything on Vista or LS6. If blocked, try a
genuinely DIFFERENT second approach, then write a named flag file and KEEP
WORKING on the rest of your scope. One blocker never ends a session.

CLAIM DISCIPLINE. Tag every claim: read directly / recalled / inferred. Report N
and spread, never a single draw. State the settle length behind any simulation
number. Run the physics-skeptic subagent before finalising any percentage,
force, verdict count or distance; if unavailable, say so and mark it UNREVIEWED.
An import succeeding is not an environment working. An empty result from one
directory is a broken probe, not an absence.

GIT. Commit each coherent unit as you finish it, path-limited:
`git commit -m "msg" -- <paths>`, 8 files max. Never bulk-stage. NEVER push. The
repo is PUBLIC. Writing to an absolute /Users/josie/can-it-ford/... path from
your worktree lands in the MAIN checkout: use paths relative to your own tree.
Never edit CLAUDE.md, the register, or sim_standing.py.

WHEN YOU FINISH A UNIT, keep going. Pick the next highest-value item in YOUR
scope. The auto-dispatcher will also nudge you, but do not wait for it.
No em-dashes.

