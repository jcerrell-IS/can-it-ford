You are one of several Claude Code sessions running concurrently on Josie's MacBook on the
research project "Can It Ford" (MPM simulation of whether a specific vehicle can safely cross
floodwater; NSF REU with Krishna Kumar at TACC). You are running with bypassed permissions, so
nothing will stop you from doing damage except your own discipline. Act accordingly.

## STEP ZERO, BEFORE ANY OTHER TOOL CALL

Run your own self-audit and paste its full output as the first thing you say:

    bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d5-priorart

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

# SLOT d5-priorart

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-priorart, branch
claude/r8-priorart, branched off claude/can-it-ford-round-5-87a6d6 (NOT off add-ci-checks: the
staged bib lives on the round-5 branch and is absent from add-ci-checks and from origin/main).

You may write ONLY:
  paper/conference_101719.tex
  paper/can_it_ford_references_IEEE.bib
  docs/R8_PRIOR_ART_2026-08-18.md  (new)

NEVER TOUCH: the overleaf remote (no push); the main checkout; any other branch.

## WHERE THIS LEFT OFF, measured live
All four prior vehicle-fording works ARE in the bibliography and NONE is cited in the prose, in
either copy of the paper:
  he2026vehiclewater   10.1115/1.4071177        He et al 2026
  wasfy2015fording     10.1115/DETC2015-47142   Wasfy et al 2015
  khapane2014wading    10.4271/2014-01-0936     Khapane & Ganeshwade 2014
  alqadami2022moving   10.1111/jfr3.12828       Al-Qadami et al 2022
grep -c for each key in paper/conference_101719.tex          -> 0,0,0,0
grep -c for each key in overleaf/main:conference_101719_1.tex -> 0,0,0,0
An uncited bib entry does not appear in an IEEEtran reference list, so the paper does not cite
the prior art at all.

## THREE FURTHER FACTS FROM THE LITERATURE SWEEP, VERIFY EACH BEFORE ACTING
1. A prior-art fix already landed IN A FILE STAMPED DO-NOT-SUBMIT. Find it and establish what it
   contains before writing anything new.
2. The drafted prior-art prose cannot compile against its own paste target: reportedly 17 of its
   19 cite keys do not exist in the Overleaf bibliography. Re-derive that count yourself.
3. The corpus index NOW REPORTS all four papers as IN-PAPER, which has poisoned the project's own
   novelty gate: a document written today already repeats it. Correct the index's cited-status
   derivation in the same pass, or state precisely why it cannot be corrected from your scope.

## TWO TRAPS THAT HAVE ALREADY COST A SESSION
1. THE CANONICAL PAPER SOURCE IS NOT paper/conference_101719.tex. The paper builds from
   conference_101719_1.tex on overleaf/main with FLAT figure paths. The overleaf remote shares NO
   ancestor with origin, so `git push overleaf main` OVERWRITES rather than syncs. The local
   overleaf/main ref is 18 days stale at 6466dfa (2026-07-31). You are staging into paper/ on
   your own branch; a human moves it.
2. THE BIB KEYS DIVERGE between the repo copy and the Overleaf copy for at least six works
   (ccsa2010yaris vs ccsa2016yaris, xia2013 plus xia2010 vs the corrected xia2014). A naive
   auto-export breaks every \cite{}.

## THE RESEARCH
- D1's cross-referenced count supersedes every earlier figure: 15 vehicle-in-water simulations
  exist, 12 uncited. Authority is data/r5_citation_xref.tsv on claude/r5-research. Do not write
  "four" or "five".
- Al-Qadami et al 2022 claims a FIRST moving full-scale vehicle simulation, critical depth 0.38 m,
  minimum D x V 0.39 m2/s. Its mesh-independence detail is UNVERIFIED (MDPI 403, ledger item 18).
- The corpus review's caveat is the honest positioning: "The most detailed flooded-vehicle force
  work is CFD/VOF (Al-Qadami et al., 2023), not particle-based."
- Xia is 2014, not 2013, four authors including Yejiang Wang. An instruction insisting on 2013
  was wrong.

VERIFY EVERY DOI TITLE AGAINST THE RESOLVED RECORD. Scholar Sidekick verifyCitation, or
auditBibliography on the whole .bib in one call.

## FIRST STEP
  git -C /Users/josie/can-it-ford show overleaf/main:conference_101719_1.tex | /usr/bin/grep -n 'cite{' | head -40
Establish what the paper actually cites today before writing one word.

## DEFINITION OF DONE
1. A related-work paragraph engaging all four works, in the tex, stating what this project does
   that they do not.
2. Every bib entry audited for title-versus-DOI agreement, mismatch count stated and each named.
3. A document listing repo-versus-Overleaf key divergences so the human move does not break cites.
4. The corpus novelty-gate poisoning either fixed or precisely characterised.
5. NOTHING pushed to overleaf.
