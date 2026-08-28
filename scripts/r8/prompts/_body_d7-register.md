# SLOT d7-register

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-register, branch
claude/r8-register (off claude/add-ci-checks).

You may write ONLY:
  docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
  docs/R8_REGISTER_MERGE_2026-08-18.md  (new)

NEVER TOUCH: CLAUDE.md (d1-safe owns it); any other branch; the main checkout; anything
under .claude/.

## WHERE THIS LEFT OFF
Round 7 ledger item 12, "not started", and the target has MOVED since the warning was written.
MEASURED LIVE, three lineages, none containing another:
  origin/main and all R5/R7 branches   656 lines
  claude/fork-register-reconcile      1455 lines   NOT an ancestor of add-ci-checks
  claude/add-ci-checks (local)        2186 lines   public copy 1644, so 542 lines unpushed
  merge-base(add-ci-checks, fork-register-reconcile) = 1a868f3
  `git log --merges 1a868f3..claude/add-ci-checks` returns EMPTY, so no merge has happened.

THE LEDGER'S WARNING, verbatim: "Merge the CURRENT tip, re-derived at the moment of merging,
NEVER 790d999, which is a clean zero-conflict merge that silently drops 126 lines. Verify with
`git rev-parse HEAD^2` equalling the pinned SHA, not with a line count."

A ZERO-CONFLICT MERGE IS NOT EVIDENCE OF A CORRECT MERGE. D3 measured on 2026-08-16 that
`git merge-file` returned exit 0 with 0 conflict markers and 1559 = 1455 + 104. That arithmetic
was for a 104-line delta. The delta is now 731 lines. RE-DERIVE IT; do not carry D3's figure.

## THE DISCIPLINE, from CLAUDE.md
The register "is the sole authority for any factual claim it covers: solver identity, gravity,
force accessors, resolution, thresholds, citations, repo state. It is T1, read from live source."
And: "Before archiving or superseding any dated audit file, pull its VERIFIED-tier findings into
the register first, the file can go stale, the facts inside it should not disappear with it."

## KNOWN STALENESS TO FIX WHILE YOU ARE IN THERE, both verified live
- Register A6 and CLAUDE.md items 3 and 15: the 9.80665 fork is CLOSED. failure_modes.py:14
  reads 9.81, unified by e495b56 on 2026-08-12. Exactly ONE 9.80665 site survives,
  analysis/viability_dashboard_scaffold.py:11, assigned and never read.
- Ledger item 16: check_claims.py Rule C6 is stale. You do NOT fix check_claims.py (d1-safe
  owns it). Record that the register's corresponding entry needs updating and say who should.

## FIRST STEP, enumerate before merging
  git -C /Users/josie/can-it-ford show claude/fork-register-reconcile:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md > /tmp/reg_fork.md
  git -C /Users/josie/can-it-ford show claude/add-ci-checks:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md > /tmp/reg_ci.md
  diff <(/usr/bin/grep -n '^#' /tmp/reg_fork.md) <(/usr/bin/grep -n '^#' /tmp/reg_ci.md)
Work at the level of REGISTER ENTRIES, not lines. Two entries with the same identifier and
different content are the real decisions; everything else is concatenation.

## DEFINITION OF DONE
1. A merged register where every entry present in either input is present in the output, with
   the entry count of each input and of the output enumerated, not asserted.
2. A document naming every entry that existed in both with different content, and which won and why.
3. NO line-count-based verification anywhere in your report. Count entries.
4. Your branch is not merged anywhere. A human decides where it lands.
