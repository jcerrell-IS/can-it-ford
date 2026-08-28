# SLOT d1-safe

SCOPE. Worktree /Users/josie/can-it-ford, the MAIN checkout. Branch claude/add-ci-checks.
You do NOT create a branch and you do NOT switch branch.

You may write ONLY these six already-modified tracked files:
  CLAUDE.md
  .claude/settings.json
  .claude/hooks/orient_live.sh
  .claude/checks/params_check.py
  .claude/skills/connector-router/SKILL.md
  scripts/check_claims.py

NEVER TOUCH: any other branch; anything under .claude/worktrees/; /Users/josie/can-it-ford-*;
.claude/tooling/ (slot d6-tooling owns it); docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
(d7-register owns it); simulation/openchannel_bc.py (d4-bcmerge owns it); anything under paper/
(d5-priorart owns it); hf_space/ (see below).

OTHER SESSIONS SHARE THIS WORKING TREE. Re-run `git status --porcelain` in the SAME tool call
as any `git commit`, never from an earlier turn.

## WHERE THIS LEFT OFF
Tip ee7c512 "A 22-agent adversarial pass refuted my own item 41 within the hour", 2026-08-18
08:06. FIFTEEN commits unpushed (origin/claude/add-ci-checks is de191b8), 32 files, 4672
insertions. Of those 15, 14 were authored by one session and 1 (ad6f169) by another; two further
sessions committed nothing and left their whole output uncommitted in this tree.

## THE THING THAT MUST NOT BE LOST, AND IT IS IN NO COMMIT ANYWHERE
Working-tree CLAUDE.md is 855 lines. Committed: 823 here, 785 on claude/r7-ladder, 676 on
claude/r5-research and origin/main. `git stash list` is EMPTY. Two verified corrections exist
ONLY in the working copy:
  - items 3 and 15: the 9.80665 post-processing fork is CLOSED. failure_modes.py:14 was unified
    to 9.81 by e495b56 on 2026-08-12. Exactly ONE 9.80665 site survives,
    analysis/viability_dashboard_scaffold.py:11, where G is assigned and never read.
  - item 14: EXT_REF's comparand is vehicle_params.py:131, not :89. :89 is docstring prose.
One `git checkout -- CLAUDE.md` by any live session destroys both. COMMIT CLAUDE.md ALONE, FIRST,
BEFORE ANYTHING ELSE.

## ALSO IN SCOPE
(a) The uncommitted .claude/settings.json diff REMOVES four Read-deny entries, including
    `Read(data/track1_sweep_v3/**)` and `Read(designsafe-staging/**)`. CLAUDE.md's own provenance
    section says the deprecated files "are also blocked mechanically by the Read deny rules in
    .claude/settings.json". Establish whether that removal was deliberate. If you cannot,
    RESTORE the two entries and say so in the commit message. designsafe-staging/ is the
    publication-bound tree and carries a known one-byte fork on the 0.60 boundary operator.
(b) scripts/check_claims.py Rule C6 is HALF-FIXED and uncommitted: working copy line 149 now
    reads "9.80665 survives at exactly ONE site", the committed copy at ee7c512:151 still says
    "TWO sites". Committing this file closes Round 7 ledger item 16.

## DO NOT "FIX" hf_space/
hf_space/app.py and hf_space/README.md on this branch are STALE relative to origin/main, which
carries the joint-rule calculator and the warpmpm README. Verified: origin/main blob e746b7a
versus this branch's 22faea6, and `git diff --name-only origin/main...claude/add-ci-checks --
hf_space/` is EMPTY, so this branch never modified them and a normal merge keeps main's version.
Editing them here would CREATE a divergence where none exists. Leave them. Note it in your board
row so nobody else is misled by reading them from this checkout.

## FIRST STEP
  git -C /Users/josie/can-it-ford status --porcelain
  git -C /Users/josie/can-it-ford diff --stat -- CLAUDE.md
Then commit CLAUDE.md alone, path-limited.

## DEFINITION OF DONE
1. Zero modified TRACKED files in this working tree.
2. `git rev-list --count origin/claude/add-ci-checks..claude/add-ci-checks` is 0 after
   `PUSH_OK=1 git push origin claude/add-ci-checks`, AND you re-verified with
   `git ls-remote --heads origin claude/add-ci-checks` that the remote SHA equals your local SHA.
   A zero exit code is not evidence.
3. You state whether the settings.json deny-rule removal was deliberate or restored.
DO NOT delete the *.bak-20260818-045233 files. Diff them, report, leave them.
