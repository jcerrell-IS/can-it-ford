You are one of several Claude Code sessions running concurrently on Josie's MacBook on the
research project "Can It Ford" (MPM simulation of whether a specific vehicle can safely cross
floodwater; NSF REU with Krishna Kumar at TACC). You are running with bypassed permissions, so
nothing will stop you from doing damage except your own discipline. Act accordingly.

## STEP ZERO, BEFORE ANY OTHER TOOL CALL

Run your own self-audit and paste its full output as the first thing you say:

    bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh <SLOT>

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

## IF YOU ARE GIVEN A VISTA GPU NODE, THIS IS THE ONLY srun FORM THAT WORKS

Measured live 2026-08-19. Vista's wrapper rejects a partial invocation and reveals the
missing flag ONE AT A TIME, so a wrong form costs three round trips to diagnose:

    srun -p gh -N 1 -n 1 -t 00:30:00 --overlap --jobid=<JOBID> <command>

All five are required: `-p` partition, `-N` nodes, `-n` tasks, `-t` a time limit, and
`--overlap`. Without `--overlap` a step into a live idev kills it.

CHECK THAT THE GPU IS ACTUALLY DOING SOMETHING, do not assume it is:

    srun -p gh -N 1 -n 1 -t 00:05:00 --overlap --jobid=<JOBID> \
      nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader

A GH200 reporting `0 %, 3 MiB, 97871 MiB` means your allocation is being wasted. That is
the measured state a node sat in for 21 minutes of a 2-hour window on 2026-08-19 because
the srun line was wrong. The card has 98 GB; do not default to canonical grid sizes out
of habit and leave most of it idle.

## THE RESEARCH INDEX IS INCOMPLETE AND ITS SEARCH IS WEAKER THAN IT LOOKS

`analysis/research_index.py --query` is a literal substring match over `title` and
`abstract` ONLY. It cannot match an author, a method tag, or any paraphrase, and 110 of
332 records have no abstract. **A zero from `--query` is not evidence of absence.**

The index also does NOT contain the project's nineteen Undermind deep searches. Query
those directly in workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c` with
`inspect_deep_searches` before concluding the project has not researched something.
Load the `research-corpus` skill; it now carries both facts.

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
## YOUR SLOT: d15-settle, branch `claude/r9-settle`, worktree `.claude/worktrees/r9-settle`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d15-settle` first.

### The contradiction, already measured, never acted on

`sim_standing.py` uses `settle_frames=8`. `analysis/settle_audit.py` applied `analysis/stationarity.py` to all 25 local runs, using the 15-column `metrics.csv` files already on disk, no GPU needed, and found:

- **25 of 25 runs need MORE than 8 frames discarded.** Min 29, median 48, max 80, out of 91 total frames.
- **N_eff is 2.9 to 11.0.** A 91-frame record holds roughly 3 to 11 independent samples, so any uncertainty computed from N=91 is overstated by about 3x to 5x.
- 12 of 25 retained windows are still non-stationary at 5 percent.

Read the live CLAUDE.md section headed "THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA" at `/Users/josie/can-it-ford/CLAUDE.md` by absolute path, and re-run the audit yourself rather than quoting those numbers from this dispatch.

### The trap that makes this hard, and it is already documented

**DO NOT REMOVE THE TRANSIENT BEFORE A SLIDE VERDICT.** Incipient motion is an EVENT, not a steady state. Removing the transient drops SLIDE from 21 of 24 runs to 5 of 24 and would silently contradict the published 16 SLIDE / 1 STUCK. `probabilistic_verdict.py` defaults to the full record for exactly this reason and `--stationary-window` is a robustness diagnostic only.

So the honest position is asymmetric and your write-up must carry it: **full record for verdicts, demonstrated-stationary window for any convergence or uncertainty claim.** Anyone who applies one rule to both cases gets a wrong answer in one of them.

Also: **MSER minimises standard error, which is not stationarity.** A settle length chosen to stabilise a mean is not evidence the record is stationary; a residual trend can survive inside the MSER-optimal window and only the reverse-arrangement test catches it. `stationarity.py` reports both and carries a self-test for this trap.

### Your unit

Turn a measured contradiction into an executable recommendation.

1. State what `settle_frames` should be, per run or as a rule, with the evidence and the failure mode of the choice.
2. State which published quantities would move and which would not, and quantify it. If the answer is that no verdict moves, that is a strong and publishable result; say it plainly rather than burying it.
3. Say explicitly what CANNOT be fixed by any settle length, namely that a 91-frame record carrying 3 to 11 independent samples is short, which reaches the same conclusion as register D9's 250-frame finding by a different route.

### Boundaries

**Do NOT edit `sim_standing.py`.** It is canonical, it is the driver for all 17 gated runs, and slot d8-naming already holds `renders/**/sim_standing.py` in its write scope. Produce the recommendation and the patch as a diff inside your document. Changing the driver is a separate decision with a re-run cost attached.

Relatedly, slot d3-force measured last night that a DIFFERENT settle mechanism (the pinned-settle quiescence gate in the coupling-force rung, not this one) needs about 2596 frames against a 900 cap to meet its gate. Those are two different settles in two different scenes. Do not merge them into one claim.

No GPU. Everything is on disk.
