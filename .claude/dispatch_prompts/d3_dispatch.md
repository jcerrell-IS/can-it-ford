### DISPATCH 3, credentials, Mac plus remote read-only

```
SCOPE DECLARATION
MACHINE: Mac, driving Vista and LS6 read-only via scripts/tacc.sh.
BRANCH: claude/credential-exposure-2026-08-13-DO-NOT-PUSH (exists, 2 commits).
MAY WRITE TO: docs/CREDENTIAL_EXPOSURE_2026-08-13.md on that branch ONLY.
NEVER: push this branch (the GitHub repo is PUBLIC); print, echo, log or commit
any credential VALUE; rotate or revoke anything; delete an export line (it can
lock out a running headless session); touch any other branch.

HARD RULE FOR THIS THREAD
Rotation and revocation are Josie's account actions. You diagnose and prepare;
you do not execute. If you believe a step requires her, write it as an exact
command she can run and stop there.

WHERE THIS THREAD LEFT OFF
Commit 253b904 is diagnosis only, in its own words: "Nothing rotated, nothing
revoked, no export line removed, no credential value printed or logged."
It corrected three premises: LS6's three exports are NOT one token repeated
(lines 122/123 are one value, 124 is a DIFFERENT one, and bash takes the last,
so 122/123 are a dead credential on disk in three files); ~/.bashrc is 0700 on
both clusters, so the real defect is a file the earlier dispatch never named,
Vista ~/.env_mcp at 0644; and the exposure is 8 files, not 2.
[live] 2026-08-14, re-verified for this dispatch, names only, no values read:
  Vista ~/.bashrc   mode=700  matching-export-lines=1
  Vista ~/.env_mcp  mode=644  matching-export-lines=1
Still unrotated. This is the THIRD time it has been raised.

A COLLISION YOU MUST RESOLVE FIRST
docs/CREDENTIAL_EXPOSURE_2026-08-13.md exists in three states:
  118 lines, md5 2bbd337f, UNTRACKED in /Users/josie/can-it-ford (main worktree)
  268 lines, md5 727cc81b, UNTRACKED in worktrees/orphan-rescue-token-rotate-d72f90
  268 lines, md5 727cc81b, COMMITTED on this branch (identical to the second)
The 118-line file is unique and tracked nowhere. Determine whether it is an
earlier draft or independent content BEFORE touching anything. Do not delete it.

RESEARCH FINDINGS YOU NEED
- docs/SECURITY_ACTIONS_2026-07-31.md does NOT mention this exposure (verified,
  zero hits). Its lesson transfers and is the single most important sentence
  here: rotation without revocation left the W&B key live. Deleting an export
  line is not revocation.
- Corpus: 07_Repo_Provenance_and_Corrections/2026-07-24_security-note_secrets-env-
  credential-handling_CURRENT.md and ..._staged-inbox-risk_CURRENT.md are the
  project's own policy documents. Read both before writing remediation steps.
- Memory can-it-ford-github-repo-is-public.md: GitHub served a removed W&B key
  by SHA even after filter-repo. Nothing about this file goes to a remote.
- 253b904 records a measurement artifact worth not repeating: the first
  classifier regex reported ZERO real values on Vista, which was false, because
  the character class died on the opening quote. Matching the variable NAME is a
  different test from matching the VALUE.
- Bounded checks must be reported as bounded: a full recursive grep of Vista
  $HOME (20.8 GB) exceeded the transport timeout and was never completed.

CONCRETE FIRST STEP
Resolve the three-way file collision (diff the 118 against the 268 and say
plainly which content is unique to the shorter one). Then re-verify the 8-file
inventory live, by NAME and MODE only, and mark each row rotated / not-rotated /
dead-credential.

DEFINITION OF DONE
One reconciled docs/CREDENTIAL_EXPOSURE_2026-08-13.md on this branch containing:
the 8-file inventory with live modes as of today, an explicit "unrotated, third
mention" status line, and a numbered, copy-pasteable remediation sequence for
Josie that puts REVOCATION before line-deletion. Committed to the DO-NOT-PUSH
branch with explicit paths. Nothing pushed. The chmod 600 on Vista ~/.env_mcp is
the one action you may propose as a single command, but do not run it.
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
