### DISPATCH 1, Mac, `claude/rtfd-test-phase-1-4-569130`

```
SCOPE DECLARATION
MACHINE: Mac. WORKTREE: /Users/josie/can-it-ford/.claude/worktrees/rtfd-test-phase-1-4-569130
BRANCH: claude/rtfd-test-phase-1-4-569130 (already checked out there).
MAY WRITE TO: that branch only, and a bundle file under $TMPDIR.
NEVER TOUCH: main; any other worktree or branch; data/all_runs_inventory.csv;
renders/yaris_render_s1/gates_results_all_runs.json; the uncommitted .mcp.json
and untracked renders/*.py in the main worktree (another session's, unreviewed);
docs/CREDENTIAL_EXPOSURE_2026-08-13.md anywhere (Dispatch 3 owns it).

WHERE THIS THREAD LEFT OFF
Nine commits sit on this branch and are reachable from NO remote ref. Verified
with: git rev-list claude/rtfd-test-phase-1-4-569130 --not --remotes=origin
They are e431877, 5ca6c6b, 68e4a30, a6e42c1, then f2cdbeb, 9ddd648, 53d54e3,
8182719, 658ecfa (five "Preserve g128/g96 run artifacts" commits).
a6e42c1 answers register Section J item 15, the project's own stated single
highest-value open item. It also carries 29 tracked paths including
data/g128_canonical_2026-08-13/{canon_g128_m1100,m1609,m2337}/{metrics.csv,
summary.json}, analysis/classify_g128_canonical.py, and register items 17, 18
and 19, which exist on no other branch (grep for them in main's register
returns 0).
The session that made them stated: "Nothing was pushed; the standing rule
requires your confirmation, and .git/hooks/pre-push needs PUSH_OK=1."

WHY THIS IS URGENT, NOT HOUSEKEEPING
Those artifacts were force-added past .gitignore:10 precisely because register
item 16 records six canonical margins becoming permanently unverifiable when
job 866887 overwrote the g48/g96 run directories on 2026-07-26 with no tracked
copy anywhere. The failure mode item 16 documents is live again right now.

RESEARCH FINDINGS YOU NEED, DO NOT RE-DERIVE
- Steffen, Kirby and Berzins 2008 is the citable mechanism for MPM losing
  convergence under grid refinement at fixed particles-per-cell. a6e42c1
  records PPC constant at 8, which is exactly that paper's case. Cite it in the
  register entry, not just the commit body.
- Al-Qadami 2023 is named in project notes as the field's only mesh-independence
  study for a flood-vehicle result, and is the precedent for how to write this
  up. It is NOT in the research corpus index (zero hits across the 115-row
  manifest), so treat it as UNVERIFIED until you retrieve it. Do not cite it as
  settled. Scite or Consensus first.
- Register item 17 (on this branch) states the g64 settle gate is
  non-deterministic and that item 15's test "should be run at g96 and above, or
  repeated at several seeds". a6e42c1 complied. Keep that scope statement.

CONCRETE FIRST STEP
1. git -C <worktree> status --porcelain=v1 and confirm clean.
2. Create a backup bundle BEFORE anything else:
     git -C <worktree> bundle create "$TMPDIR/rtfd_g128_$(date +%s).bundle" \
       claude/rtfd-test-phase-1-4-569130
   then verify it with: git bundle verify <file>. Report the path and size.
3. Only then push, explicitly and with the gate:
     PUSH_OK=1 git -C <worktree> push -u origin claude/rtfd-test-phase-1-4-569130
4. Confirm it LANDED with git ls-remote --heads origin, not with the exit code.
5. Re-run the orphan test; it must now return zero commits.

DEFINITION OF DONE
git rev-list claude/rtfd-test-phase-1-4-569130 --not --remotes=origin returns
EMPTY, ls-remote shows the branch at 658ecfa, and a verified bundle exists as a
second copy. Plus one short note in the branch's own docs/ recording that
register items 17, 18 and 19 are still branch-only and need a deliberate merge
decision (do NOT merge them yourself, Dispatch 4 owns register reconciliation).
Correct register item 18's phrase "one finding in one commit" to "one
measurement": the same table also appears in docs/SESSION_TRACK1B_2026-08-13.md,
added by b62d554, 44 minutes before ed8bf8e. Three write-ups, one measurement.
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
