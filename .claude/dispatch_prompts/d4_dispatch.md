### DISPATCH 4, Mac, new branch, register reconciliation

```
SCOPE DECLARATION
MACHINE: Mac. Create a NEW branch claude/register-reconcile-<slug> off main.
MAY WRITE TO: docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md and one new
findings doc, on that new branch ONLY.
NEVER TOUCH: main; claude/rtfd-test-phase-1-4-569130 or
claude/friction-resolution-reconcile-84465d (read them, never write to them);
the uncommitted .mcp.json or untracked renders/*.py in the main worktree;
anything credential-related.

WHERE THIS THREAD LEFT OFF
[live] The register, which CLAUDE.md declares "the sole authority for any factual
claim it covers", exists in THREE divergent states:
  main                                        656 lines
  claude/rtfd-test-phase-1-4-569130           681 lines  (adds Section J 17,18,19)
  claude/friction-resolution-reconcile-84465d 817 lines  (adds D8c, D9, A6b)
Commit 109ae87 already had to reconcile a register conflict by hand once and
recorded "neither side was taken wholesale". Nobody has reconciled all three.

WHAT MAKES THIS DELICATE
The three sets of additions are not redundant, they are complementary and in one
place they interact:
- rtfd branch item 18: the "two independent resolution-dependence findings" are
  ONE measurement. CORRECT ITS PHRASING: it says "one finding in one commit
  ed8bf8e". [live] ed8bf8e's commit BODY does tabulate the sweep, but the same
  table also appears in docs/SESSION_TRACK1B_2026-08-13.md:233, added by
  b62d554, 44 minutes EARLIER. Three write-ups, one measurement.
- friction branch D9: friction (D8) and refinement (J15/J16) break DIFFERENT
  clauses of the same criterion. Friction drops the drift clause outright,
  22.64x over to 0.52-0.58x under, speed still 4x over. Refinement drops
  NEITHER: at Silverado g128 drift is 1.556x and speed 4.087x, both over, and
  triggered_slide is still False because their 3-frame co-occurrence fails.
  They are SEPARATELY SUFFICIENT, NOT SHOWN INDEPENDENT: D8 walked mu at one
  grid, J15 walked grid at one mu, and the 2x2 has never been run.
- friction branch D8c REFUSES a repoint that a 2026-08-13 change had already
  propagated: the gated driver is sha256 5215c38b, 389 lines, and :132-133 IS
  its floor plane, so CLAUDE.md item 3's (:132-137) was correct. If you merge
  the branches carelessly you can silently re-apply the refused repoint.

RESEARCH FINDINGS YOU NEED
- Corpus 07_.../2026-07-24_provenance-note_claude-md-provenance-tracking_CURRENT.md
  and ..._worktrees-and-backup_CURRENT.md are the project's own guidance on this
  exact hazard, written 2026-07-24 and never turned into a check.
- CLAUDE.md's DRIFT_THRESHOLD item is the worked example of why a bare count is
  the defect: 22/23/23/24 are all defensible depending on two independent binary
  scope choices. Apply the same discipline to any count you touch.
- Memory count-check-false-blocks-in-worktree.md: count_claims_check.py reports
  25 blocking defects inside a worktree and 0 in the main checkout, because 7
  declaration-site files are untracked and a worktree cannot see them. Do not
  treat an in-worktree 25 as a real regression.

CONCRETE FIRST STEP
Extract all three register versions to separate files and diff them pairwise:
  git show main:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
  git show claude/rtfd-test-phase-1-4-569130:docs/...
  git show claude/friction-resolution-reconcile-84465d:docs/...
Produce a three-column table of every item that differs, before merging one line.

DEFINITION OF DONE
A single reconciled register on your new branch, with every item from all three
retained or explicitly rejected-with-reason, item 18's phrasing corrected, and
D8c's refusal preserved. register_integrity.py reports 0 blocking defects.
A findings doc listing every merge decision and its reason. Report, do not fix,
the two main-worktree shadow risks: modified .mcp.json and ~22 untracked
renders/yaris_render_s1/*.py, which a bare `git commit -m` from another session
would sweep in.
```

OPERATING PROTOCOL, applies to you in full:

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
