### DISPATCH 2, Mac, new branch off `main`

```
SCOPE DECLARATION
MACHINE: Mac. Create a NEW worktree/branch: claude/vista-realism-triage-<slug>,
off main.
MAY WRITE TO: that new branch only, and only docs/ within it.
NEVER TOUCH: main; claude/rtfd-test-phase-1-4-569130 (Dispatch 1); the
corrections register (Dispatch 4); Vista's filesystem; any credential file.

WHERE THIS THREAD LEFT OFF
Vista's 12 realism_track commits were reported this week as existing on one
filesystem only. That is now STALE and the correction matters:
  [live] origin/vista-realism-track-2026-08-13 = 4b38aa3, 12 commits ahead of
  main. origin/track2/coupled-realism-explore = 3e66d8a.
  Vista's own clone is now 1 ahead / 5 behind and 1e4c6d5 / 4b38aa3 NO LONGER
  RESOLVE there (it was re-synced after pushing).
So nothing is at risk, but 12 commits are parked on a branch that has never been
reviewed or merged, and commit 68e4a30 plus the memory file
vista-unpushed-realism-commits.md both still say they are unpushed.

WHAT THIS THREAD IS FOR
Produce a merge/park/discard recommendation for those 12 commits, per commit,
with evidence. Do not merge anything.

RESEARCH FINDINGS YOU NEED
- track2/coupled-realism-explore carries track2_realism/FINDINGS_TRACK2_2026-08-13.md,
  the Genesis LegacyCoupler result. It is a FAILURE, not a validation:
    F_analytic 5022.7200 N, F_measured second half -291.6208 N, ERROR -105.8060%
    free body: sank 0.887500 -> 0.687123 m, a_fit +1.9857 vs a_ideal +9.8100,
    reported as -39.879%
  That document states in its own words that no "X% agreement with analytic
  buoyancy" claim is made for Genesis, and that neither number "should ever be
  quoted alongside warpmpm's 7.3-7.7%". The -39.9% is "an artifact of fitting an
  acceleration to a decelerating descent". Preserve that framing exactly.
- THREE buoyancy numbers exist for three different things and must never be
  merged: 7.3 to 7.7% (warpmpm SDF collider, canonical), +0.035% (NOT a buoyancy
  figure, it is a residual-acceleration identity, see commit d8a479f), and
  -105.8% / -39.9% (Genesis, failures).
- Register J1a records that the 7.3-7.7% figures come from run_c1_sdf at
  frac 1.0. Vista deliberately ran fraction 1.000 to avoid repeating J1a's
  documented error of scoring a partially submerged case against a fully
  submerged reference. Do not "correct" that choice.

CONCRETE FIRST STEP
git -C /Users/josie/can-it-ford log --oneline main..origin/vista-realism-track-2026-08-13
then, for each of the 12, read the full body with --format=%B and classify:
already-superseded-on-main / merge-candidate / exploratory-park / retraction.
Two of the 12 are explicit retractions per 68e4a30; find them and say what they
retract.

DEFINITION OF DONE
docs/VISTA_REALISM_TRIAGE_<date>.md on your new branch, one row per commit with
a recommendation and the evidence for it, plus an explicit correction notice
that 68e4a30 and the memory file are stale on the "one filesystem" claim.
Committed to your branch with explicit paths. No merge performed, no push to
main.
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
