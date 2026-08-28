### DISPATCH 8, Mac, PREFLIGHT: three artifact sets exist on one machine each

```
SCOPE DECLARATION
MACHINE: Mac, plus read/write to Vista via /Users/josie/can-it-ford/scripts/tacc.sh.
BRANCHES YOU MAY WRITE TO: claude/moving-vehicle-exploratory-2026-08-11 (existing,
  four uncommitted files), and one NEW branch claude/fork-s3-rescue-<slug> off main.
NEVER TOUCH: main; the canonical stores data/all_runs_inventory.csv and
  renders/yaris_render_s1/gates_results_all_runs.json; claude/rtfd-test-phase-1-4-569130
  (Dispatch 1 owns it); realism-exploration (verified SAFE, see below, do not "rescue" it);
  any credential file (Dispatch 3 owns those).

NOTHING ELSE IN THE FORK STARTS UNTIL THIS IS DONE. Register item 16 exists because
six canonical margins became permanently unverifiable when run directories were
overwritten with no tracked copy. Three artifact sets are in that same state now.

8.1 renders/yaris_render_s3_enhanced/ IS ON ZERO GIT REFS AND IS GITIGNORED.
  git check-ignore -v renders/yaris_render_s3_enhanced/sim_enhanced.py
    -> .gitignore:31:renders/*
  git log --oneline --all -- renders/yaris_render_s3_enhanced/
    -> EMPTY. No ref in this clone contains it.
  The tree holds sim_enhanced.py (36359 bytes), NOTES_2026-08-07.md (17334 bytes),
  four .sbatch files, and results/ with SIX completed run summaries: ctrl_g64,
  enh_g96, enh_g96_c10, enh_g96_real, enh_g128_c10, enh_g128_real.
  ACTION: copy the tree out, then commit it into a NON-IGNORED path on your new
  branch. Do NOT add a .gitignore carve-out under renders/. The walk-down carve-out
  pattern has already gone wrong three times per CLAUDE.md and .gitignore line numbers
  have been wrong three times in one day; re-derive any line number you cite with
  /usr/bin/grep -n, never quote it positionally.

8.2 THE MOVING-VEHICLE WORK IS NOT EVEN COMMITTED.
  git -C /Users/josie/can-it-ford-moving-vehicle rev-parse --abbrev-ref HEAD
    -> claude/moving-vehicle-exploratory-2026-08-11 at feecf5f
  git ls-remote --heads origin | /usr/bin/grep -c moving-vehicle  -> 0
  Four untracked files: analysis/render_moving_vehicle_placeholder.py,
  analysis/render_moving_vehicle_surface.py,
  docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md,
  simulation/moving_vehicle_sdf_exploratory.py
  The branch is not on the remote AND the files are not committed to it. This is the
  seed of the entire fork.
  ACTION: stage the four by EXPLICIT PATH, commit, push. Never git add -A in that tree.
  KNOWN INCOMPLETE, carry it forward: that document has three unfilled placeholders,
  <!--LADDER--> at :143, <!--BOWWAVE--> at :164, <!--COST--> at :205, so its sections
  5, 6 and 8 are unfinished. Section 5 states a negative finding whose supporting
  table is one of those placeholders. Do not cite sections 5, 6 or 8 until filled.

8.3 THE VISTA 6-DOF DRIVER IS UNPUSHED.
  simulation/rigid6dof.py, run_c4_free_sdf in validate_coupling_force.py, and
  tests/test_rigid6dof.py with 25/25 tests passing, exist only at
  /work/11603/jcerrell0629/vista/can-it-ford-track1-6dof at local commit a231a73.
  git ls-remote --heads origin returns 17 branches, none named track1/sdf-6dof-driver.
  (track2/coupled-realism-explore IS present at 3e66d8a.)
  ACTION: recover over scripts/tacc.sh. That script exists, 3627 bytes, executable,
  with a host allowlist for vista/ls6 over ControlMaster sockets and an exit-3 refusal
  list. One survey claimed Vista is unreachable non-interactively because of MFA; a
  live ControlPersist socket contradicts that. TEST IT, do not assume either way. Exit
  255 means the socket expired and one interactive ssh restores it.
  IF BLOCKED: say so plainly and proceed. Dispatch 9 can use DynamicSDFBody instead.

8.4 DO NOT "RESCUE" THE REALISM TRACK. It is already safe and a survey got this wrong.
  git -C /Users/josie/can-it-ford-realism ls-files simulation/realism/ returns all
  nine modules including dynamic_body.py, outflow_deactivate.py, render_water.py; the
  tree is clean; branch realism-exploration is on origin at c4af419, matching local
  HEAD. Spend no recovery effort there.

DEFINITION OF DONE
All three artifact sets reachable from origin. For each: the branch name, the commit
SHA, and ls-remote output proving it landed, not an exit code. A short doc listing
what was recovered, what was already safe, and anything still blocked with the reason.
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
