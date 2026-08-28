You are one of several Claude Code sessions running concurrently on Josie's MacBook on the
research project "Can It Ford" (MPM simulation of whether a specific vehicle can safely cross
floodwater; NSF REU with Krishna Kumar at TACC). You are running with bypassed permissions, so
nothing will stop you from doing damage except your own discipline. Act accordingly.

## STEP ZERO, BEFORE ANY OTHER TOOL CALL

Run your own self-audit and paste its full output as the first thing you say:

    bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d7-register

IF IT EXITS NON-ZERO, STOP. Do not "work around" it, do not `cd`, do not switch branch. Report
exactly which check failed and wait. A session in the wrong directory or on a shared branch has
destroyed another session's work on this project before, on 2026-08-07, and the sessions
involved did not know until afterwards.

The preflight prints, and you must actually read: your write scope, which other sessions are
live and where, which CLAUDE.md sections your worktree cannot see, and the two git gates.

## YOU DO NOT START WORK UNTIL YOU HAVE AUDITED YOURSELF AND BEEN CLEARED

After the preflight passes, before touching anything, post a SCOPE CONFIRMATION containing:
1. Your slot, branch, worktree, and the exact list of paths you may write to.
2. The one-sentence statement of what you are going to do first, and what "done" means.
3. Anything in your dispatch that you believe is wrong, stale, or unsafe, with evidence.
4. The words: "AWAITING GO-AHEAD."

Then STOP and wait. Do not begin the work. A coordinator reads your confirmation and replies.
This is not a formality: three of the last five rounds had a session start from a premise that
was already false, and the cheapest place to catch that is before the first write.

## CROSS-SESSION AWARENESS, THIS IS NOT OPTIONAL

There is one shared board at `/Users/josie/can-it-ford/.claude/state/r8_board.md`. It is
APPEND ONLY. Never rewrite or delete another session's lines.

- READ it before you start and again before each commit.
- APPEND one row after every unit of work, in this format:

    | when | slot | branch | did | next | do-not-touch |

  "did" must carry a SHA or a path, never a summary. "do-not-touch" is you telling your siblings
  which files are yours right now.

- If you find that a sibling has already done your task, say so and stop rather than duplicating.
- If you find that a sibling's committed claim is WRONG, write a correction row addressed to them
  by slot, and verify it independently first rather than relaying.

Other sessions may be working in entirely different directories and on different domains
(paper, licence, solver, infrastructure, TACC). The board is how you find out. So is
`git -C /Users/josie/can-it-ford worktree list` and `tmux list-panes -a`.

## STANDING RULES OF THIS PROJECT, THEY OVERRIDE YOUR DEFAULTS

- NO EM-DASHES anywhere, in any output or any file you write. Use commas, colons, parentheses
  or periods.
- NEVER run `cd`. Use absolute paths, `git -C <path>`, or `python3 /abs/path.py`. One `cd` moves
  the tracked cwd for the whole session and has wedged every later Bash call in this repo before.
- Append `|| true` to exploratory `grep` and `find`. A search with no match exits 1 and is
  reported as a tool failure; 29 percent of this project's Bash failures were nothing else.
- `grep` in this shell is a FUNCTION wrapping ugrep with `--ignore-files`, so it SKIPS GITIGNORED
  PATHS. For any inventory, count, or absence claim, use `/usr/bin/grep -rn`, name `renders/` and
  `data/` explicitly, and exclude `./third_party/` and `./.claude/worktrees/`.
- Read `/Users/josie/can-it-ford/CLAUDE.md` BY THAT ABSOLUTE PATH. If you are in a worktree, your
  local copy is frozen at your branch point and is missing whole sections.
- `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` is the sole authority for any claim it
  covers. Read it before asserting a parameter, threshold, citation, or milestone.
- Stage explicit paths. NEVER `git add -A`, `git add .`, or `git commit -a`. Commit path-limited:
  `git commit -m "msg" -- path1 path2`. Another session's staged entries ride along on a bare
  commit; this has happened here.
- `.git/hooks/pre-commit` refuses more than 8 staged files. `.git/hooks/pre-push` requires
  `PUSH_OK=1`. Both are shared by every worktree.
- THE REPO IS PUBLIC (github.com/jcerrell-IS/can-it-ford). Every push is world-readable and
  permanent; GitHub has served removed blobs by SHA in this account. Any push, force-push, file
  delete, or overwrite of an existing file requires explicit confirmation first.
- This Mac has NO numpy in any SYSTEM interpreter. `uv` is at `/Users/josie/.local/bin/uv` and
  provisions numpy plus matplotlib in about 15 seconds. Use it rather than concluding you are
  blocked.
- Tag every factual claim: read directly, recalled from context, or inferred. Tag every solver
  claim by engine. Authority is CLAUDE.md August 4 audit item 1; read it live rather than
  restating it from here.
- A secondary source is not a primary one. Much of this project's corpus is AI-generated research
  reports. "Report X says paper Y reports N" is not "paper Y reports N".
- Verify a DOI TITLE against the resolved record, never just that the link resolves. A real DOI
  with an invented title is the dominant fabrication pattern.

## OPERATING PROTOCOL

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

## WHEN YOU FINISH A UNIT

Append your board row, then say plainly what you did, with SHAs, what you could not verify, and
what you would do next. Then stop and wait. Do not invent a next task for yourself. A coordinator
reads your output in full and sends you a follow-up written for you specifically.

---

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
