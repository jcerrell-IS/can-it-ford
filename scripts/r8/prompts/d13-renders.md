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
## YOUR SLOT: d13-renders, branch `claude/r9-renders`, worktree `.claude/worktrees/r9-renders`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d13-renders` first.

### The state, verified live by the coordinator before this dispatch

`analysis/render_multigeom_rollout.py` gives the WATER a real optical treatment (Schlick Fresnel, HDRI, Beer-Lambert absorption, GGX) and gives the VEHICLE a single flat Lambert term. The whole vehicle material is the `shade()` function around line 208:

```
def shade(base, n):
    sh = np.clip(n @ LIGHT, 0.0, 1.0) * 0.6 + 0.4
    return np.clip(sh[:, None] * base, 0.0, 1.0)
```

Separately, four PBR maps ARE tracked in the repo and referenced by nothing: `assets/Asphalt015.png`, `assets/Asphalt015_1K-JPG_Color.jpg`, `assets/Asphalt015_1K-JPG_NormalGL.jpg`, `assets/Asphalt015_1K-JPG_Roughness.jpg`. Confirm that "referenced by nothing" is still true with `/usr/bin/grep -rn Asphalt015` naming `renders/` and `data/` explicitly, because the shell `grep` here skips gitignored paths and would give you a false negative.

### Your unit

Bring the vehicle and the ground up to the standard the water already has, in the same renderer, without touching the physics or any simulation output.

1. Give the vehicle a material with the same ingredients the water already uses in this file. You are not inventing a shading model, you are applying the one that is already here to a second surface.
2. Wire the asphalt PBR set to the ground plane. Tracked-and-unreferenced assets are either a gap or dead weight; resolve which.
3. Produce a BEFORE and AFTER frame from the SAME rollout data and the same camera, and send both to Josie. A claim that a render improved is worth nothing without the pair.

### Hard boundaries

- You may NOT change any simulation output, any metric, any verdict, or any file under `renders/*/sim_*.py`. If a render change appears to alter a physical quantity, stop and report it, because that means the renderer is reading something it should not.
- The canonical Yaris hull and derived meshes are already public on origin and their licence question is UNRESOLVED. Do not add, move, or re-export any mesh. Read `.claude/memory/derived-hull-already-public-on-origin.md` before touching anything mesh-shaped.
- Slot d10-licence established last night that the root BSD-3 licence was claiming third-party material it does not own, and that four sources are reproduced as images. The asphalt maps have their own licence. Establish what it is from the file or its source before you make them part of a deliverable. If you cannot establish it, wire them behind a flag and say so; do not guess.
- This Mac has NO numpy in any system interpreter. Use `/Users/josie/.local/bin/uv` or `/opt/homebrew/bin/uv run --with numpy --with matplotlib --with scikit-image python3 ...`.

This is the one slot in this wave whose output is visual. Send the images with SendUserFile rather than describing them.
