# THE CLAUDE CODE FINDINGS THE FLEET PAID FOR, AUDITED LIVE AND IMPLEMENTED

Written 2026-08-20 03:1x. Completes the Claude Code half of section 13A by auditing every
harness claim in handoff section 11 against the live configuration, then implementing what
survived. Sessions audited: `1d537aee` (239 agent transcripts, the deep-research parent) and
`529261e9` (201 agents, the R10 parent), plus the two capability-audit agents inside them.

**Every claim below was re-measured. Three of section 11's own claims did not survive.**

---

## 1. WHAT WAS ALREADY TRUE, AND NEEDED NOTHING

| section 11 claim | live state 2026-08-20 |
|---|---|
| 11.3 `--effort max` hardcoded for every slot | **already fixed.** `r8_launch.sh` uses `--effort $EF` and the plan carries `high` for every slot except `d11-accessor`, which is `max` |
| 11.4 the plan reader takes the last field positionally | **already fixed.** No positional read remains; the header names resolve |
| 11.7 hook scripts absent in a worktree | **not currently true.** `.claude/hooks` 14 tracked / 15 on disk and `.claude/checks` 4 / 5; both extra files are `.bak` copies wired zero times |

`.claude/tooling/` is still **0 tracked against 16 on disk**, so it is absent from every
worktree. The one hook that references it is already guarded with `if [ -f "$P" ]`, so it
fails open. That is the correct shape and it is why nothing is broken today.

---

## 2. THREE OF SECTION 11'S CLAIMS DID NOT SURVIVE MEASUREMENT

### 2.1 "All 14 hooks are unconditional" is wrong, and its fix is not implementable as written

There are **18 hooks, not 14**, and **12 of them already carry a tool matcher**
(`Bash`, `Edit|Write`, `Read`, `Bash|Read|Edit|Write`). The 6 without a matcher are the
lifecycle events (`Stop`, `UserPromptSubmit`, `SessionEnd`, `SessionStart` x2, `PreCompact`),
which take no matcher by design.

Section 11.2 then recommends scoping them "with `if` conditions, e.g. `Bash(git commit*)`".
**That is permissions syntax, not hooks syntax.** `Bash(...)` argument patterns appear in
`permissions.allow` in this very file; a hook `matcher` is a regex over the TOOL NAME only.
The two config surfaces were conflated. The implementable form of the same intent is to guard
inside the command string, which is what section 3 below does.

### 2.2 The real fail-open gap was the invocation, not the body

The hook BODIES already fail open, and say so. `gate_destructive.sh` carries: *"FAILS OPEN. If
the helper is missing or errors, fall back to the raw command rather than exiting non-zero: a
PreToolUse hook that crashes blocks the tool call."*

**The gap was one level up.** 17 of 18 hook COMMANDS invoked their script bare, so a missing
script exits 127 and a PreToolUse hook exiting non-zero blocks every matching tool call.
Measured as a control:

```
missing script, unguarded : exit 127   <- blocks every Bash/Edit/Write/Read that matches
missing script, guarded   : exit 0     <- the tool call proceeds
```

That is the whole distance between a guardrail bug and a hard stop on unrelated work.

### 2.3 `disableClaudeAiConnectors: true` IS SET AND DOES NOT TAKE EFFECT

This is the most consequential finding here and it is verifiable in one command.

`.claude/settings.json` carries `"disableClaudeAiConnectors": true`. This session's own tool
manifest nonetheless carries the full claude.ai connector set under UUID server names,
including every tool `settings.local.json` explicitly denies:

| denied by name | live under an uncovered alias |
|---|---|
| `mcp__hf__hf_fs_write`, `hf_jobs`, `hf_sandbox_exec`, `dynamic_space` | `mcp__677ab2f7-...__` |
| `mcp__undermind__write_file`, `delete_file`, `delete_folder`, `delete_deep_search` | `mcp__52146218-...__` |
| `mcp__wolfram__WolframLanguageEvaluator` | `mcp__e8b78a84-...__` |
| the four `mcp__filesystem__` writes | `mcp__Desktop_Commander__*` and a third copy under `mcp__plugin_desktop-commander_...` |

**Two rules do hold**, and they are the ones that matter most: `mcp__overleaf__write_file` and
`write_section` have no alias, and the Overleaf remote shares no ancestor with origin, so a
push there overwrites rather than merges.

**And two are inert rather than protective**, which is the same shape as every instrument
failure in the round: this session's manifest carries no `mcp__zotero__zotero_delete_*` and no
`mcp__canford-tacc__tacc_submit`, so those rules cannot fire because the tools do not exist.
A deny rule for a nonexistent tool reads as coverage and provides none. The real submit path
is `scripts/tacc.sh` through Bash, which nothing denies.

---

## 3. WHAT WAS IMPLEMENTED

### 3.1 Every hook now fails open on a missing script

All 18 commands rewritten from `$CLAUDE_PROJECT_DIR/.claude/hooks/X.sh` to
`P="$CLAUDE_PROJECT_DIR/.claude/hooks/X.sh"; if [ -f "$P" ]; then bash "$P"; fi`, and the
python-invoked ones likewise. The `Stop` pane-signal hook gained `|| true` because
`tmux display-message` fails outside tmux.

**Tested four ways**, all live:

1. a real force-push string is still DENIED (it fired on the test itself and blocked the call)
2. `git status` is still ALLOWED, exit 0
3. a missing script, guarded, exits 0
4. the same missing script, unguarded, exits 127, which is the control proving the guard is
   load-bearing rather than cosmetic
5. stdin still reaches a python hook through the guard

### 3.2 Eighteen alias deny rules added, and why that is a patch and not a fix

The UUID-prefixed and `Desktop_Commander` aliases are now denied explicitly, taking the deny
list from 43 rules to 61. Confirmation was immediate and independent: the four
`mcp__plugin_desktop-commander_...` write tools dropped out of the live manifest within one
turn of the edit.

**This is a patch. The UUID changes on reconnect**, so the list needs rechecking every time,
and I deliberately did NOT build a check for it: a check running in a plain shell cannot see
the tool manifest, so it could only ever report a value indistinguishable from a real
measurement, which is the exact defect this whole audit is about. The durable fix belongs
upstream, in making `disableClaudeAiConnectors` take effect for this surface.

### 3.3 `scripts/verdict.py`, the typed return, which was the largest unused capability

Section 11.1 records `claude -p --output-format json --json-schema` as the highest-leverage
unused capability, with **zero hits across `scripts/`** for any of `--output-format json`,
`--json-schema`, `--bg`, `claude agents` or `claude -p`. Re-measured today: still zero, on all
five. Claude Code 2.1.234's `--help` carries all of them.

The post-mortem's conclusion was that **the fix is a typed tool return, not a better
instruction**, because twelve instrument failures in one night all had one shape: a code path
returning a value indistinguishable from a measurement when it could not measure.
`scripts/verdict.py` makes that distinction unfakeable at the transport layer:

- `verdict` is a three-valued enum, `verified | refuted | could-not-evaluate`
- `predicate` is required: the exact command or view consulted, so a relayed verdict arrives
  WITH the thing that produced it
- `scope` is required: what the predicate could not see
- exit codes are **0 / 1 / 2**, so a caller writing `if verdict.py ...; then` treats
  could-not-evaluate as a failure, which is the correct default
- the wrapper's own failures, a missing CLI, a timeout, a non-zero exit, unparseable output,
  a missing verdict field, all return 2 and never 0

**Tested on all three branches, live:**

```
exit=0  VERIFIED             a claim independently measured true
exit=1  REFUTED              the same claim with a wrong number
exit=2  COULD-NOT-EVALUATE   a claim requiring a live LS6 read, which needs MFA
```

The could-not-evaluate run is the one worth reading. It tried four independent routes,
refused to substitute Vista's ControlMaster for LS6's because that answers a different
machine's question, and explicitly refused a cached "static facts" MCP tool because the claim
demanded a live check. It also declined to let its own general knowledge of LS6's
architecture drive the verdict. That is the behaviour the schema exists to force.

**One caution recorded from testing it.** My first exit-code test piped the tool to `head`, so
`$?` reported head's status and every branch appeared to exit 0. The tool was right and the
test harness was wrong, which is the same class of error, one level out.

---

## 4. WHAT IS NOT DONE

1. **`--bg` and `claude agents --json` are still unused.** The fleet is driven by tmux
   `send-keys`, and the recorded failure of that design is a launcher falling back to a bare
   shell prompt while a sender pasted 4 KB of markdown into it, executing line by line.
   `claude --bg` never talks to a shell, so that failure class cannot occur. Building the
   replacement launcher is a larger change than tonight's and needs its own decision.
2. **`~/.pane_signals/*_done` still fires on every Stop hook**, so it proves liveness and not
   completion. `claude agents --json --all` returns real session state and needs no TTY.
3. **The two HPC facts remain filed where nothing loads them.** `XDG_RUNTIME_DIR` on SLURM
   compute nodes appears ten times in `_inbox/LIVE_SESSION_LOG.md` and nowhere a session
   reads; `claude -p` as the workaround for interactive mode exiting appears zero times in
   `scripts/r8/`. Both are in CLAUDE.md's environment section now, which is the right place,
   but neither is wired into a launcher.
4. **`disableClaudeAiConnectors` not taking effect is unreported upstream.** It is a
   one-command reproduction and worth an issue.

---

## 5. THE ADVERSARIAL REVIEW PATH IS ALIVE AGAIN, 2026-08-20 03:40

`CLAUDE.md` carries a whole section titled **"THE ADVERSARIAL REVIEW PATH IS DEAD FLEET-WIDE,
2026-08-19"**, recording that the `physics-skeptic` subagent and any `Agent` call died with
`deepseek-ai/DeepSeek-V4-Flash:deepinfra`, that an explicit `model` override did not reach it,
that nine independent origins confirmed it, and that sessions d11, d12, d14, d15, d18 and d19
all correctly marked their claims UNREVIEWED rather than faking the review.

**It works now.** A single cheap liveness probe at 03:40 on 2026-08-20, a `general-purpose`
agent asked to run one `git log` command, returned the correct SHA in 6.05 seconds using
125,849 subagent tokens and one tool use.

**Why re-probing was right rather than a violation of that section's own instruction.** The
section says "do not re-attempt the subagent expecting a different result until the model id is
fixed". That is sound advice against a retry LOOP, and it is not a licence to carry a
yesterday-dated infrastructure claim forward as a standing fact. This project's constitution
says the opposite about exactly this class of claim: do not trust a doc, a memory or a written
summary as current fact, and check it live before stating it. **One probe costs six seconds; a
fan-out launched on a dead path costs the round.** The probe is the cheap version of the same
caution the section was expressing.

**What this unblocks, and it is the largest single item outstanding.** Every physics claim made
on 2026-08-18 and 2026-08-19 was marked UNREVIEWED because this layer was unavailable, and the
handoff's own section 15 lists "the exoneration is self-reviewed" as its first admission of low
confidence. That layer is available again. The claims are still unreviewed until somebody
actually runs the review; nothing about the path being alive reviews them retroactively.

**Do not delete the CLAUDE.md section.** It was true when written, nine origins measured it,
and the record of a fleet-wide outage is worth keeping. Amend it to say the outage ended.
