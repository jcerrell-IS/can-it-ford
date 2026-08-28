# Global working rules, applies to every project on this machine

## Formatting, always
No em-dashes, anywhere, in any response, in any file written. Use commas, colons,
parentheses, or periods instead.

## Verification, always
Do not trust a doc, a memory, or a written summary as current fact. Before stating what a
file currently contains or what a project's current state is, check it live, grep it, cat
it, run git log against it. If you have not checked live, say so explicitly instead of
stating something as confirmed.

## Before any destructive action
Before overwriting, deleting, or replacing a file with something new, check whether the
existing file already matches what you're about to write, and check whether it belongs to
a different project than the one currently being worked on. Never apply a fix intended for
one project to a same-named file in a different project without confirming first.

## Response style
State what success looks like and the most likely failure mode before moving to the next
step. Give exact commands, not vague suggestions.

## Safe Resume Protocol
Whenever a Claude Code session resumes after an interruption (`--continue`, `--resume`,
`/resume`, a reattached tmux pane, or a crashed/reopened terminal), before continuing any
prior task:

1. Restate in one line what you were mid-task on, drawn from the resumed history, not
   assumed.
2. Run `git status` and report anything staged, modified, or untracked that wasn't
   expected.
3. Check for any background process, job, or shell left running (SLURM job status, a
   still-active pane, a hung script) rather than assuming the interruption happened at a
   clean boundary.
4. If everything is clean, say so explicitly and continue exactly where you left off.
5. If anything is mid-write, mid-commit, or ambiguous, stop and report it before taking
   any further action.

This only applies on resume. Do not run this checklist on a fresh session with no prior
history, that's just friction for no reason.

## Claim discipline, always
Adopted 2026-08-13 from the RTFD dispatch protocol, which repeated it in every
dispatch. Applies to every project on this machine.

Tag every factual claim by how you got it: read directly, recalled from context, or
inferred. Never state a number from memory when you could check it live. If a subagent
or connector that would normally review a claim is unavailable, say so and mark the
claim unreviewed. Do not fake the review.

One source cited twice is not two sources. A commit with two sections is one source. A
claim plus the tool that measured it is not corroboration. Before reporting that two
findings independently agree, confirm they have separate origins.

A checkout that is behind cannot prove a file never existed, and a search that skips
ignored paths cannot prove a string is absent. Absence of evidence from a partial view
is not evidence of absence. Say which view you searched.

Prefer a labelled, reversible assumption over stopping, and state it where it will be
found again. Keep working on everything else in scope when one item is blocked.

Prefer a falsifiable test over a plausible claim: a no-forcing control, a held-fixed
comparison, a second seed. Write a result up the same way whether it confirms or
overturns something already published.

## Shell discipline
Added 2026-08-18 from a measurement of 717 local session transcripts: 34,596 tool calls,
of which 24,791 (71.7 percent) were Bash, with 1,068 Bash failures. These three rules
address the three largest failure classes, in order of size.

1. NEVER `cd`. Use absolute paths, or `git -C <path>`, or `python3 /abs/path.py`. The Bash
   tool keeps one persistent cwd for the whole session, so a single `cd` silently moves the
   ground under every later command, and relative hook paths and relative permission rules
   then stop resolving. This is not theoretical: it wedged every subsequent Bash call in
   this project on 2026-08-07, and it silently redirected two verification commands to the
   wrong directory on 2026-08-18 while measuring the very problem.

2. Exploratory `grep` and `find` get `|| true`. A search with no match exits 1, which is
   reported as a tool failure. 314 of 1,068 Bash failures (29.4 percent) were nothing but
   this. Suppress it when absence is a valid answer, so the remaining failures are real.

3. In a git worktree, keep each Bash call simple. Claude Code's own worktree isolation
   refuses commands it cannot statically prove stay inside the worktree, and it says so
   with "this command is too complex to analyse". That guard, not any project hook,
   produced 117 of the 1,068 failures. Split compound commands with variable assignment
   plus redirects into separate calls rather than fighting it.

## Hooks must fail open
A PreToolUse hook that crashes, or whose own path does not resolve, blocks the tool call.
That turns any bug in a guardrail into a hard stop on unrelated work. Two live instances
in this project: `params_check.py` raising inside `check_bbox_agreement` blocked 34 commit
attempts, and hooks wired to `$CLAUDE_PROJECT_DIR/.claude/tooling/`, which is untracked and
therefore absent from every worktree, error on every Bash call made from a worktree.

So: guard every hook command with an existence test before invoking it, wrap the body so an
unexpected exception exits 0 with a warning on stderr, and reserve exit 2 for the specific
condition the hook exists to catch. A guardrail should be able to fail without taking the
session with it. Before adding a hook, check whether its script is tracked by git; an
untracked script cannot be seen by a worktree.

## Before any push or remote write
Confirm the target branch, stage explicit paths only, never a blanket add, and confirm
the push or copy actually landed. A command exiting 0 is not evidence the remote
updated. Before overwriting a file on another machine, check that machine for local
modifications and unpushed commits first: on 2026-08-13 a routine config sync would
have destroyed 12 unpushed commits on Vista.
