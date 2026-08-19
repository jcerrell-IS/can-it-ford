# R9 coordinator and fleet-design audit, 2026-08-19

**Snapshot 19:26 BST**, clock from `date`. Sessions were still committing: `e81bc9c`
landed at 19:22 and `77c274c` at 19:18. Written by slot d20-reader. Write scope: this
file and `analysis/r9_session_reader.py`.

This audits the coordinator and the fleet design, not the sessions. It measures the
setup against five documents in the project's own corpus that were not consulted when the
fleet was built.

## Sources

| doc | file | bytes |
|---|---|---|
| **D1** Claude Code, Used Correctly (multi-pane HPC) | `~/Downloads/Claude Code for Multi-Pane HPC Simulation Workflows_...md` | 30,546 |
| **D2** Configuration and Remediation Plan | `compass_artifact_wf-aae75abf-...md` | 42,709 |
| **D3** Configuring Claude Across Five Surfaces | `compass_artifact_wf-2c1e05ae-...md` | 34,466 |
| **D4** Optimal Tooling Stack (3-week sprint) | `compass_artifact_wf-7b8dbc33-...md` | 30,435 |
| **D5** AI Research Tools & Infrastructure | `compass_artifact_wf-62a7f8e6-...md` | 27,153 |

All five read. Duplicate copies of D2 and D3 exist in `~/Downloads` and are
**byte-identical by md5**, so the known divergent-copy hazard does not apply here.

---

# The three most actionable items

## A1. The single worst-configured thing is the one the coordinator controls directly, and it is measurable

`scripts/r8/r8_launch.sh:108` hard-codes:

    CMD="claude --model opus --effort max --permission-mode bypassPermissions"

Measured across all 18 transcripts: **878 records carry `bypassPermissions` and ZERO
carry `plan`.** Every session, for the whole round, in bypass, and Plan Mode was never
entered once by any of eleven sessions.

D3 §2.5 is explicit: "Verification/research in plan mode; edits in default/acceptEdits;
**never bypassPermissions on laptop or cluster login nodes**." D1 lists Plan Mode
discipline among the six practices that correlate with success.

**The fair mitigation, which matters and which D3's blanket phrasing hides.** D2 Feature 6
records, verified against the official permissions docs, that **deny rules and explicit
ask rules apply in every mode including bypassPermissions**; only `allow` rules become
irrelevant. This repo's `.claude/settings.json` carries **15 deny rules and 6 ask rules**,
so the destructive-command guardrails were live all round. What bypass actually cost was
the 23 `allow` rules becoming inert, and the loss of the confirmation step.

**So the accurate charge is not "you disabled the guardrails". It is that
`defaultMode` is unset, so there is no configured fallback, and the launcher overrides
per-session judgement with a single global setting.** Fix: set
`"defaultMode": "acceptEdits"` in `.claude/settings.json`, drop
`--permission-mode bypassPermissions` from the launcher, and let a slot that genuinely
needs bypass request it.

## A2. The subagent capability was not "barely used", it had a 0 percent success rate, and seven sessions each paid to discover that separately

The coordinator's self-criticism ("used subagents almost not at all") understates it in
the direction that matters. Measured:

| slot | Agent calls | failure signature in transcript |
|---|---|---|
| r9-kramer-extract | 3 | 25 |
| r9-settle | 5 | 24 |
| r9-reader (me) | 2 | 21 |
| r9-priorcode | 3 | 16 |
| r9-accessor | 3 | 12 |
| r9-platform | 3 | 12 |
| r9-corpus-bib | 1 | 4 |
| r9-renders | 0 | 0 |
| r9-landing | 0 | 0 |
| r9-moving-vehicle | 0 | 0 |

**The correlation is perfect: every session that attempted a subagent hit the error, and
the three showing zero are exactly the three that never attempted one.** Twenty
invocations, zero successes, `deepseek-ai/DeepSeek-V4-Flash:deepinfra`, and an explicit
`model` override does not reach it (I tested that myself).

D3 §1.2 specifies the `physics-skeptic` subagent as the primary Failure-Class-2 control,
and `.claude/agents/physics-skeptic.md` exists and matches that spec almost verbatim. So
the fleet **did** implement the recommended control and then ran an entire round with it
silently dead. That is worse than never having built it, because every dispatch told
sessions to use it and every session that complied lost turns.

**This is the round's ninth instrument failure and the most expensive one**: a control
that fails closed would have blocked; this one failed by being absent while appearing
available.

## A3. The coordinator is the only writer that violated file-domain separation, and it did so on the authority file

Measured across the wave window, per-branch, excluding shared ancestry:

    distinct files written by the wave : 65
    files with MORE THAN ONE writer    : 1   (1.5 percent)
      .claude/skills/research-corpus/SKILL.md  <- COORDINATOR and r9-corpus-bib

D1's robust combination is "worktrees + explicit non-overlapping file-domain assignment
per pane". **The slots achieved that essentially perfectly.** The one collision in 65
files is the coordinator writing `SKILL.md` in `faf53d1` while d14-corpusbib was writing
the same file on its own branch, and it is the same file that d16-landing later found
conflicting at merge with **neither side a superset**, and the same file at the centre of
yesterday's C-17 finding.

D1 warns exactly this: "worktrees solve *isolation*, not *coordination*; conflicts on
hotspot shared files just move to merge time with no warning." The prediction landed on
the one file the coordinator touched outside its lane.

---

# 1. Practices followed, and practices violated

## 1a. Followed, and worth stating because the audit is not a hit piece

| practice (source) | evidence |
|---|---|
| **Git worktrees per write-heavy pane** (D1 rec 3) | 11 sessions, 11 worktrees, 34 worktrees total on disk |
| **Non-overlapping file domains** (D1) | 65 files, 1 collision, 1.5 percent |
| **Hooks as deterministic guardrails, not prose** (D1, D3 §0.3) | `.claude/settings.json` carries **11 PreToolUse matcher blocks** plus Stop, PostToolUse, UserPromptSubmit, SessionStart x2, SessionEnd, PreCompact |
| **`params_check.py` as the single consistency gate** (D3 §0.4) | exists at `.claude/checks/params_check.py`, wired into hooks and CI |
| **A `physics-skeptic` subagent committed to git** (D3 §1.2) | `.claude/agents/physics-skeptic.md` exists and matches the spec |
| **Commit after every meaningful unit** (D1 rec 5) | 119 commits in the window, every session clean at multiple checkpoints |
| **Git as the single cross-surface source of truth** (D3 §3) | skills, hooks, CLAUDE.md, `.mcp.json` all committed |
| **SessionStart context injection** (D3 §0.3) | `orient_live.sh` runs and injects live state |
| **A test oracle** (D1 rec, Anthropic blueprint) | `tests/test_physics_gates.py`, 12 test functions |

That is a genuinely strong configuration. Most of D3's Tier 0 and Tier 1 backbone is
built. The failures below are not "nothing was set up", they are **specific,
individually cheap gaps in an otherwise good setup**.

## 1b. Violated, with measured cost

| # | violation | source | measured cost |
|---|---|---|---|
| V1 | **bypassPermissions everywhere, Plan Mode never** | D3 §2.5, D1 | 878 records bypass, 0 plan. See A1 for the fair mitigation |
| V2 | **CLAUDE.md at 939 lines against a <200 ceiling** | D1, D3 §2.2 | 676 at wave base, 855, 906, now **939 uncommitted**. It grew **263 lines, +39 percent, during the round**. That is 4.7x the ceiling |
| V3 | **One shared handoff file, the pattern D1 names as the thing to replace** | D1 rec 3 | `.claude/state/r8_board.md`, 226 KB, one file, 11 concurrent appenders |
| V4 | **The board is UNTRACKED by git** | D3 §3 (git is the only source of truth) | `git ls-files --error-unmatch` fails on it. The single coordination artifact of an 11-session round is in no commit, on no branch, and in no bundle. The tmux server died twice tonight |
| V5 | **Session length far past the documented degradation point** | D1 | 614 to 1061 messages per slot. D1's failure marker is "50+ messages" in one session and "reliable in the 0-20 percent context range" |
| V6 | **Coordinator wrote outside its lane onto a hotspot file** | D1 | see A3 |
| V7 | **A hard-won environment fact stored where no session loads it** | D1 rec 4 | see §5 |

### On V2, the one where I disagree with the source

D1's "<200 lines" is quoted from a single practitioner and D1 itself labels community
evidence "uneven". This project's CLAUDE.md is not bloat: it is a corrections register
whose entries repeatedly stopped real errors, and several sessions cited specific items
tonight. **The defensible criticism is not the length, it is that D3 §0.2 and D2 Feature 1
both give the fix and it was not taken**: keep a short constitution and `@import` the
register. `@import` supports max depth 4 and is verified in D2. The file currently does
the job of both, which is why it grows and why a worktree freezing it at a branch point
does so much damage.

---

# 2. Capabilities available and unused

| capability | used? | does the corpus say it would have helped here? |
|---|---|---|
| **Plan Mode** | never, 0 of 878 | **Yes, narrowly.** D1 scopes it to "multi-file/refactor tasks where it catches wrong-problem mistakes before any edit" and says "skip it for one-line fixes". At least four sessions started from a false dispatch premise tonight (d12 `c2f3592`, d19 `a863ee7`, d17 `d3e52fd`, d14 `6ecf4e5`). Every one of those is a wrong-problem catch, which is precisely Plan Mode's stated value |
| **Subagents** | 20 calls, **0 successes** | **Yes, and it was configured.** See A2. D3's caveat is worth keeping: "a scoped single reviewer can beat a noisy multi-agent one" (SWR-Bench). The fix is one working reviewer, not more agents |
| **Agent Teams** | never piloted | **Only as a pilot, and probably not here.** D1 rec 6: "Pilot native Agent Teams on a small subset of panes needing shared live task state", *confidence medium*, with "~3-4x token overhead" and the threshold "adopt only if coordination overhead is measurably costing you time". With a 1.5 percent file-collision rate, coordination overhead was **not** the binding constraint. **The corpus does not support adopting it here**, and this is one place the coordinator's self-criticism is harsher than the evidence |
| **`/clear` and `/compact` session hygiene** | not observed | **Yes.** D1 names it among the six success practices. Both crashes forced the equivalent by accident |
| **Codex CLI in 2-4 panes** | never | **Yes, medium-high confidence** (D1 rec 2), with a stated threshold: shift panes to Codex if usage repeatedly hits rate limits or exceeds ~$200/mo. Not measured here, so I cannot say the threshold was met |
| **`@import` in CLAUDE.md** | not used | **Yes** (D2 Feature 1, D3 §0.2). Direct fix for V2 |
| **DeepWiki MCP** | available, lightly used | **Yes, top recommendation of D5** ("the standout code-adjacent tool"). d19-priorcode read Anura3D, Chrono and sdfibm **by hand** this round. That is exactly DeepWiki's stated use case, though d19's direct source reads are stronger evidence than DeepWiki would have been |
| **Undermind deep searches** | 8 of 20 reachable from the index | **Yes**, and this is the largest unused-capability finding, already documented as C-12 yesterday |

## The correction to the corpus that this round produced

D5's headline novelty claim is **now refuted by this project's own work**:

> "no published Material Point Method (or SPH) simulation of a road vehicle in floodwater
> yet exists ... so 'Can It Ford' is genuinely first-of-kind"

D5 attributes this to a subagent ("subagent found none") and names its own falsifier ("If
you find a genuine MPM-vehicle-flood paper ... reprioritize"). CLAUDE.md already records
four prior fording or wading simulations, and yesterday's readout added at least four
more including `[Lyu23]` `10.1016/j.compfluid.2023.106144`, an entirely particle-based 3D
SPH vehicle-wading model. **A tooling-stack document that shaped this project's priorities
rests a novelty claim on a subagent absence result**, which is the exact failure class the
fleet spent the whole round on. The falsifier it named has been met.

---

# 3. Was the eleven-session structure justified?

**Yes on the criterion the document actually sets, and the evidence is stronger than the
coordinator assumed.**

D1's test is not a headcount. It is: "the user's 12 sessions are more defensible than
typical because they are *heterogeneous* ... rather than 12 agents all editing the
mpm-engine core; heterogeneous, mostly-read or mostly-isolated panes scale far better than
12 concurrent writers." And separately: "**Cap concurrent *writers* on the mpm-engine core
at ~3-5**; let the other panes be read/monitor/audit", confidence medium-high.

Note the qualifier: **on the mpm-engine core**. The 3-5 ceiling is scoped to the shared
solver core, not to session count.

Measured against both halves:

| test | result |
|---|---|
| Concurrent writers **on the solver core** | `simulation/r5_physics/sphere_heave.py` and `grade_job_b.py`: **1 branch each in the wave window** (r9-accessor). `simulation/moving_vehicle_channel.py`: **1** (r9-moving-vehicle). `analysis/settle_audit.py`: **1**. No solver-core file had two writers |
| File-domain overlap across all 65 files | **1 collision, 1.5 percent**, and it is a skill file, not code |
| Heterogeneity of function | render, corpus/bibliography, settle statistics, landing/merge, moving-vehicle GPU, platform/publication, prior-code survey, Kramer data extraction, accessor specification, job-B route, and one pure reader. **Eleven distinct domains** |
| Read-only or write-light panes | d16-landing wrote **1 file**, d20-reader **2**, d19-priorcode **3**, d21-jobb **2**. Four of eleven were effectively audit/read panes, which is the composition D1 asks for |

**Verdict: the structure passes D1's stated test.** "I ran eleven writers" is the wrong
self-description. Eleven sessions ran; the number of concurrent writers *on any single
shared file* was one, everywhere except a skill file the coordinator itself touched.

**Where the count did cost something, and it is not merge complexity.** D1 says "beyond
~3-5 agents on the same shared codebase the human becomes the merge/review bottleneck."
That is exactly what happened, but the bottleneck was **review, not merge**:

- Nobody had read the round until a twelfth session was added to do it.
- Eight of nine sessions could not see a sibling's corrections to the authority skill.
- Seven sessions each independently rediscovered that the reviewer subagent was dead.
- Two sessions independently rediscovered the same zsh word-splitting trap.

**So the honest finding is: parallelism was correctly structured and under-instrumented.**
The failure was not too many writers, it was that nothing propagated sideways between
them except an untracked 226 KB file.

---

# 4. What the coordination layer should have been

Specific enough to implement. Ordered by cost.

**4.1 Replace the single board with append-only per-session files plus an index.**
This is D1's single named highest-impact upgrade and its rationale is exact: "if all chats
write to a single HANDOFF.md, last writer wins and earlier handoffs vanish". Implement as:

    .claude/handoffs/2026-08-19_d17-moving.md      one file per session, append-only
    .claude/handoffs/INDEX.md                      append-only, one line per append

**and track all of it in git**, which fixes V3 and V4 together. Cost: hours, near-zero
risk. The current board is conflict-free only by convention; per-file is conflict-free by
construction.

**4.2 Add a skills-drift check to `r8_preflight.sh`.** It already compares CLAUDE.md line
counts between the worktree and the main checkout. Extend the same three lines to
`.claude/skills/*/SKILL.md`. Measured yesterday: four distinct states of the authority
skill across nine worktrees, two of them with no file at all. Cost: minutes.

**4.3 Make the reviewer failure loud.** A dispatch that instructs "use physics-skeptic
before finalizing any claim involving a percentage" must not be satisfiable by a silent
failure. Either the preflight probes the subagent path once and prints its status in the
banner, or the Stop hook refuses a turn that states a percentage without either a review
record or an explicit UNREVIEWED marker. Sessions were already writing UNREVIEWED by hand
and by discipline; that should not depend on discipline.

**4.4 Split CLAUDE.md.** Short constitution plus `@import` of the register, per D2
Feature 1 and D3 §0.2. This is the structural fix for the frozen-at-branch-point problem:
a 60-line constitution that changes rarely diverges far less across worktrees than a
939-line file edited several times a night.

**4.5 Give the launcher a per-slot permission mode.** `r8_plan.tsv` already carries a row
per slot. Add a column. Read panes get `plan`, write panes get `acceptEdits`, and bypass
becomes an explicit opt-in rather than the global default.

**4.6 One thing I would NOT do.** Do not adopt Agent Teams or an orchestrator for
correctness. D1 is explicit that no orchestrator solves the shared-state problem and that
they are worth adopting "only for observability, not for correctness". With a 1.5 percent
collision rate, correctness was not the problem.

---

# 5. The two HPC bugs

## 5.1 Bug #21026, XDG_RUNTIME_DIR on compute nodes. Does not explain anything tonight, and the project already knew about it.

D1: "the bash tool can fail on SLURM *compute* nodes with `EACCES ... mkdir '/run/user/...'`
because it hard-codes a runtime dir and ignores `XDG_RUNTIME_DIR` (works on login nodes)".

**It cannot have applied tonight.** Every one of the eleven sessions ran Claude Code on the
Mac; `cwd` in all 18 transcripts is under `/Users/josie/`. No session ran Claude Code on a
Vista compute node. Sessions reached Vista through `ssh` and `scripts/tacc.sh`, which is
the right architecture for exactly this reason.

**But the more interesting finding is that the project already paid for this lesson and
filed it where nothing reads it.** The workaround appears **ten times** in
`_inbox/LIVE_SESSION_LOG.md`, including as an instruction that reads "First line on the
node: `export XDG_RUNTIME_DIR="/tmp/xdg_runtime_${USER}" && mkdir -p "$XDG_RUNTIME_DIR"`".
Measured occurrences elsewhere:

| location | hits |
|---|---|
| `_inbox/LIVE_SESSION_LOG.md` | 10 |
| `CLAUDE.md` | **0** |
| every file under `.claude/skills/` | **0** |
| `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` | **0** |

D1's recommendation 4 names this exact category: "encode environment truth in per-cluster
CLAUDE.md ... and the two known HPC Claude Code bugs". The knowledge exists, in the one
file no session loads. **This is V7 and it is a one-line fix.**

## 5.2 Bug #12507, interactive mode exiting and `claude -p` as the workaround. The symptom matched tonight. The recorded mechanism does not. Unresolved.

D1: "interactive mode can exit immediately on some HPC interactive sessions because stdin
is consumed by shell-detection subprocesses, leaving `claude -p` non-interactive mode as
the workaround".

**Tonight's relaunch produced that symptom precisely.** From the project's own memory
record of the 17:40 crash: Claude Code refused to start, "all nine windows fell back to a
bare zsh prompt", and `r8_send.py` then pasted 4 KB of markdown into a shell, which
executed it line by line. The record notes prompt text contains backticks and redirects,
so this was arbitrary code execution, and that no damage occurred.

**The recorded mechanism is different**: session-id reuse, because `r8_launch.sh` reuses
the id from `.claude/state/r8_session_ids.tsv` and Claude Code refuses an id that already
has a transcript.

**I have not resolved which is correct and I am not going to guess.** Two things are true
regardless, and both are actionable:

1. `claude -p` appears **zero times** in `scripts/r8/`, so the documented workaround for
   this symptom class was not available to the launcher whatever the mechanism.
2. **The real defect is not either bug. It is that a launcher failure degraded into
   pasting a prompt into a shell.** That is a fail-open path in the one piece of
   automation that touches every session. The fix already landed (`r8_send.py` now refuses
   a pane whose foreground command is not claude/node), and it is the right fix. But the
   general rule belongs in the audit: **a launcher must verify what it is talking to
   before it speaks, and D1's `claude -p` note should be in CLAUDE.md so the next person
   debugging a non-starting session does not have to rediscover the bug number.**

---

# Method, and the failures in my own measurement

Every number here was measured live, not recalled. The transcript figures come from
`analysis/r9_session_reader.py` (self-test 10 of 10). Git figures come from `git log`
with explicit scopes.

**I produced two false results before getting A3 right, both the same class, both mine.**
Measuring "which branch wrote which file":

1. First attempt used `git log <branch> --since` and credited every branch with the
   coordinator's files, because those commits are **ancestors** of the r9 branches. Caught
   only because it credited my own branch with `CLAUDE.md`, which I know I never touched.
2. Second attempt used `<branch> ^<all others>` and returned **zero** collisions, because
   `r9-reader` descends from `add-ci-checks` and therefore cancelled the integration
   branch entirely.
3. The correct form needs **both** the exclusion and the time window: 65 files, 1
   collision.

That is instrument failure number nine of this round and it has the round's signature
exactly: **a query that cannot distinguish "this branch wrote it" from "this branch
contains it"**, returning a plausible number either way. A reviewer would have caught it;
there was no reviewer (A2).

## What I could not verify

- Whether bug #12507 or session-id reuse caused the relaunch failure. Both fit the
  symptom; I did not reproduce either.
- Cost and rate-limit figures, so D1's Codex threshold is untested here.
- Whether Plan Mode would in fact have caught the four false dispatch premises. That is
  D1's claim about the feature, applied by me to cases it did not see. Marked as inference.
- **No adversarial review of this document.** The subagent path is dead, which is A2.
  Self-audited only.

## Falsifiers

- **A3** dies if any file in the wave window has two writing branches other than
  `SKILL.md`. Re-derive with the exclusion **and** the `--since` window; without both you
  get 0 or 31, and neither is right.
- **A2** dies if any Agent call in any of the 18 transcripts returned a usable result.
  Test: `grep -c 'DeepSeek-V4-Flash'` per transcript against Agent call counts; the three
  zero-error sessions are exactly the three with zero Agent calls.
- **V4** dies if `git ls-files --error-unmatch .claude/state/r8_board.md` succeeds.
- **§5.1** dies if any session's `cwd` in any transcript is on a Vista compute node.
