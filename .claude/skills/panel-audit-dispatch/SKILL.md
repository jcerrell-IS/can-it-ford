---
name: panel-audit-dispatch
description: "Multi-pane audit-and-dispatch across Josie's tmux Claude Code sessions for Can It Ford: canitford (C0-C5) and ford (F0-F5), 12 panes. Trigger on any pasted or attached tmux capture, pane log, or screen dump with no further instruction, or on phrases like 'audit my panes,' 'panel audit,' 'run the panel dispatch,' 'check on the panels,' 'what should each pane do next,' '12 panels,' '12 outputs,' 'keep going' on a prior round, or any canitford/ford/Cn/Fn reference. Runs identically in Claude Code (live shell, pane blocks executable) and Claude.ai chat (no shell, same procedure, blocks delivered as copy-paste text); state the active surface first, always. A mandatory numbered procedure and hard-requirements gate override ad hoc judgment on this task, existing specifically to stop skipped approvals, assumed pane counts, stale research citations, and thin, under-delivered output."
---

# Panel Audit & Dispatch

## What this replaces, and the actual failure this fixes

For a while this ran as a single giant prompt (30-plus separate instruction
blocks) that had to be re-pasted by hand every round. The complaint was
"sometimes I run it and it doesn't actually deploy in the right way." That
symptom has a specific cause: a wall of standing rules with no enforced
order lets any individual rule silently get skipped under time pressure,
especially the ones near the bottom (writeback, self-check), and nothing
forced the output to actually be as thorough as it was supposed to be.
Converting it into a named skill with a strict numbered procedure and an
explicit hard-requirements gate fixes both problems by construction: step 1
cannot be skipped in favor of step 6, because step 6 isn't reached until
step 1 outputs something, and an output that fails the hard-requirements
checklist isn't finished yet. Everything from the original prompt is
preserved below, reorganized under the procedure and labeled rules.

## Surface: Claude Code vs Claude.ai chat

This skill runs the same way on both surfaces. The only thing that changes
is how a pane's block gets delivered at the end. State the detected
surface once, as the first line of the output.

**Claude Code, live shell.** Real `tmux`, `ssh`, and `git` access exist.
Topology checks, close-the-loop verification, and destructive-action gates
(Rule 16) run against real, current pane state and real command history. A
pane block may be executed directly if instructed, still gated by Rule 16.

**Claude.ai chat, no live shell (this includes the current conversation).**
Pane state comes entirely from whatever log, capture, or pasted text is
provided in Step 0, or was already provided earlier in the same
conversation. Every pane still gets a full block, no rule gets thinned out
or skipped because the shell isn't live, the block is simply labeled
clearly as copy-paste text: "Copy this into pane C2." Chat mode is not a
lesser mode. It should actively use whatever real connectors and tools are
actually available on this surface (GitHub, Slack, Otter.ai, Google Drive,
Scite, DeepWiki, Wolfram Alpha, project file search) for Rule 14's
provenance and physics pass, rather than trusting the attached log's
memory of a file's contents. A live GitHub read of a file's current state
is strictly better evidence than a log snippet claiming what that file
says. When a project-knowledge or file-search tool is available, use it to
check research-file currency (Rule 18) directly instead of assuming.

## Canonical topology, verify live, never assume

Full setup: `canitford` session, panes C0 to C5; `ford` session, panes F0
to F5. 12 panes total.

On Claude Code, verify before doing anything else:
```
tmux list-sessions
tmux list-panes -a -t canitford
tmux list-panes -a -t ford
```
On Claude.ai chat, read the pane labels directly out of whatever was
attached or pasted. Either way, output one block per pane that is actually
confirmed live, whether that's 12, 6, or 1. Do not fabricate a block for a
pane that isn't there just to hit a round number. The 12-pane target is
the canonical full setup, not a guarantee for every invocation.

## Step 0: get the input, and confirm the surface

If a log, capture, or pane dump is attached or pasted in this turn, use it
as the primary source for pane state. Treat it as a claim to verify, not a
fact (Rule 5). If nothing is attached and nothing relevant was shared
earlier in the same conversation, ask for it in one line and stop. Do not
reconstruct pane state from memory of a previous round. Confirm which
surface is active (above) before proceeding to step 1.

## The procedure, in strict order

1. Topology and surface check (above).
2. Pending-approvals sweep. Output this first, before any other content.
3. Close the loop on each pane's last prescribed task.
4. Cross-pane consistency and dedup pass.
5. Provenance, physics, and research-file gate.
6. Choose execution mode per pane.
7. Compose one block per pane.
8. Check the output against the hard-requirements gate (below). Fix
   anything that fails before proceeding.
9. Append the SESSION_STATE.md writeback instruction.
10. Run the self-check silently, fix anything it catches, then output.

No step is optional and no step moves ahead of the one before it just
because its content looks more urgent. Urgent-looking pane content is
exactly what step 2 exists to catch.

---

## Rule 1: pending approvals always surface first

Before assigning any pane a next task, scan every pane's captured content
for a live, unanswered yes/no or multiple-choice prompt (Claude Code's "Do
you want to proceed?" style). These are one-line decisions waiting on
Josie, not stalled or blocked work. Surface all of them together, as a
single batch, one recommended answer per pane, before anything else in the
output. A pane sitting on an unanswered prompt gets "pending: approve or
decline this," never "next task: investigate X." If none are found, state
that explicitly rather than omitting the batch section entirely.

When an instruction tells a pane to type something via `tmux send-keys`:
send the text and the Enter keystroke as two separate `send-keys` calls
with a short pause between them. One call with a trailing Enter has
repeatedly failed to submit and instead stacked garbled text in the pane.

## Rule 2: multi-layer commands become real files

Any command involving shell variable expansion or nested quoting across
more than one layer (local shell to tmux to remote shell to Claude Code)
gets written as a real script file first: heredoc it into a `.sh` file,
`chmod +x`, test it standalone, then reference the file path in the
instruction. Do not hand-escape multi-layer quoting inline. It has failed
repeatedly and wastes rounds.

## Rule 3: git push discipline

Before any `git push`: fetch first, check for divergence with
`git log --oneline HEAD..origin/main`, and `git pull --rebase` if origin
has commits not present locally. Never let a downstream signal or wait
fire on the assumption a push succeeded. If a push was rejected, say
explicitly that the signal it would have triggered is not yet valid, and
do not treat it as done until a real successful push is confirmed.

## Rule 4: no fabrication

Pull every command, parameter, and instruction from actual file content,
actual attached output, or actual verified search results. This includes
Claude's own prior claims: tell the receiving pane to independently verify
rather than trust at face value, even claims stated by Claude earlier in
this same project. If something is genuinely ambiguous, say so and pick
the single most defensible default rather than guessing silently.

## Rule 5: stale info interception

Before any finding, number, or claim gets used to generate a new file,
commit, or instruction, check whether it's already stale or corrected
elsewhere in the project. A concrete example already on file:
`PROJECT_FILE_MAP.md` is dated 2026-07-07 and has not been confirmed
current since. Its own date is not proof of currency. Don't trust a file's
listed update date; cross-check with `ls -la`, `git log -1 -- <path>`, or
a live grep before citing it as ground truth. On Claude.ai chat, use an
available search or connector to check this directly rather than trusting
the attachment.

## Rule 6: close the loop before layering a new task

Before prescribing a pane's next task, check whether the last task
prescribed to that specific pane actually ran, and what its result was,
per the attached log. If that's unclear, confirming it is the first action
for that pane, not a fresh task stacked on an unconfirmed one.

## Rule 7: cross-pane consistency

If new evidence invalidates an assumption behind more than one pane's
instructions, correct all affected panes in the same pass, not just the
one where the evidence surfaced. State the correction explicitly, and
check whether it also touches related deliverables (paper vs. poster,
README vs. CLAUDE.md).

## Rule 8: cross-pane dedup

Before assigning a next task, check what every other pane is currently
doing or already queued for, especially panes sharing a research file. If
two panes would overlap, assign only one of them the task and give the
other a genuinely different angle or an explicit wait.

## Rule 9: dependency sequencing

When two panes must edit the same file based on a dependency, give the
downstream pane a concrete check, for example `git log --oneline -3` to
confirm the upstream commit actually landed, never a vague "wait your
turn" instruction with no verifiable condition.

## Rule 10: bounded wait

If a pane is gated on another pane's output, bound the wait. If the gate
is a genuinely open research question rather than an imminent write, stop
waiting, kill any stale watcher process, and reroute that pane to a real
task instead of leaving it idle.

## Rule 11: escalation after repeated stalls

If a specific pane's blocking issue has persisted unresolved across 3 or
more rounds of this audit, stop re-prescribing the same diagnostic step.
Flag it explicitly for Cristian Moran escalation, consistent with the
project's 15-minute-stuck rule.

## Rule 12: dual mode, every pane

Every pane's output combines both audit (confirm what's actually true
right now, from Rule 6) and jumpstart (a real, immediately executable next
step). Neither half is optional.

## Rule 13: deadline alignment

Every next task traces to one of three things: the poster (July 27), the
paper (July 31), or the core goal, one verified, rendered,
physically-plausible MPM simulation with a vehicle in it. If a candidate
extension doesn't serve one of these, flag it explicitly as
optional/deferred rather than filling pane time with it.

## Rule 14: provenance and physics, call the real skills, don't reimplement

This skill does not re-derive citation-tracing, MPM/SPH debugging logic,
or connector routing inline. It calls the skills that already own that
logic, by exact name, so this file can't drift out of sync with them, and
names every one that genuinely applies to a given pane rather than
defaulting to a single generic mention:

- Any number, citation, threshold, or parameter before it gets stated as
  fact or written into a script: invoke **provenance-audit**.
- Any MPM/SPH solver behavior, vehicle mass/inertia/friction parameter,
  collider setup, or Genesis/kks32 API question: invoke
  **flood-mpm-debugging-reference**.
- Conceptual or API background on gsplat, PhysGaussian, GNS, or Genesis
  more broadly: invoke **geoelements-tech-reference**.
- A pane surfaces a fresh crash, traceback, or error log this round:
  invoke **bug-triage-protocol**.
- A task needs Otter, Slack, GitHub, DeepWiki, Scite, or Wolfram Alpha:
  invoke **connector-router** and follow its routing table rather than
  guessing which connector fits.
- Anything touching the hands-on render pipeline itself (collider setup,
  water material config, PyVista smoke test, exporting frames): invoke
  **mpm-render-pipeline**.

Fast inline sanity checks that don't need a full skill call, useful while
composing a pane block: water 1000 kg/m^3, vehicle effective density
100 to 300 kg/m^3 band, sedan mass 1000 to 1600 kg, g = 9.81, realistic
depth 0 to 1.0 m, velocity 0 to 3.0 m/s. `coup_friction` is a numerical
stability coefficient, not physical mu. Physical mu is 0.3 to 0.55 per
Azhar et al. 2023. Particle count shouldn't silently change between runs.
Buoyancy must oppose gravity. Never justify a number by physical intuition
alone; every physical claim traces to a formula, a conservation law, a
cited value, or a direct measurement.

For anything render-adjacent, check visual plausibility: water reads as
one connected fluid body, vehicle position matches its known density, no
particles outside the domain or clipped through geometry, motion
continuous across frames. If nothing has actually been rendered yet, say
that plainly instead of describing a render that doesn't exist.

`rho`, `coup_friction`, box dimensions, mass, and grid resolution are
coupled. Never flag a value as wrong by pattern-matching a bug from a
different script; recompute against this script's actual current
geometry before calling anything a regression.

## Rule 15: pane isolation

Track 1 (`kks32/mpm-engine`) never touches Apptainer. Track 2 (Genesis)
never touches the `mpmenv` venv. Divvy tasks across canitford and ford to
run in parallel, but never let two panes touch the same file, branch, or
process without explicit sequencing (Rule 9).

## Rule 16: destructive-action gate

Any `git push`, force-push, file delete, or overwrite of an existing file
gets flagged for explicit confirmation before execution, every time, no
exceptions for "probably fine."

## Rule 17: never idle, only toward the real goal

If a pane's task is genuinely done, find its next task by consulting that
pane's mapped research file (Rule 18), then filtering the result through
Rule 13 before assigning it.

## Rule 18: research file lookup, living source over frozen snapshot

The current, authoritative research-file-to-panel mapping lives in
`SESSION_STATE.md` (cross-terminal handoff, usually freshest),
`CLAUDE.md` (confirmed well-maintained as of the last live check), and
`PROJECT_FILE_MAP.md` (useful but dated, see Rule 5). Check those three,
in that order of trust, before citing any research file to a pane.

The table below is a fallback for when none of the three living files are
reachable. It is illustrative, not authoritative. Confirm a file still
exists (`ls`, `git log -1 -- <path>`, or a project-file search on
Claude.ai chat) before citing it to a pane; file names in this project
have changed before without every reference getting updated everywhere.

| Pane | Fallback research file(s) |
|---|---|
| C0 | Genesis_MPM_p2g_Crash_Root-Cause...md |
| C1 | mpm_sweep_data_schema.md, kks32_mpm_engine_complete_reference_July7.md |
| C2 | Forensic_Code_Audit_of_Friction_Parameter...md |
| C3 | vehicle_data_master_reference...json, VEHICLE_PLY_AND_PARAMETERS_REFERENCE...md |
| C4 | CONSOLIDATED_CITATION_AND_CORRECTIONS_REFERENCE.md |
| C5 | Auditing_lsdyna-mesh-reader...md, License_Analysis_of_the_Three_PhysGaussian_Repositories...md |
| F0 | Bibliographic_and_Content_Verification...md |
| F1 | CLAUDE_MD_GROUND_TRUTH.md |
| F3 | mpm_sweep_data_schema.md |
| F4 | FloodScene_6-DOF_Output_and_Failure-Mode...md |
| Track A/B/D | Genesis Terrain/Surfaces docs, AI_Research_Tools_and_Scientific-Computing...md |

If a pane's actual current task doesn't match its fallback row above,
trust the live task over the table and note the mismatch once rather than
silently overriding either.

## Rule 19: maximize density, real content only

Pack as many real, verified commands into each pane's block as the
situation actually supports. Density is not just command count: before
finalizing a block, check whether any available connector, skill, or tool
would add real verification value to this specific pane's task, and use
it if so. Do not default to the narrowest sufficient toolset when a
broader, more rigorous pass is genuinely available and would help. The
only real limits are cross-pane collision (Rule 15) and unverified claims
(Rule 4), never an artificial cap on length, thoroughness, or how many
tools get used.

## Rule 20: signaling between panes

Prefer event-driven signaling over polling. Same machine: `tmux wait-for
-S <name>` paired with `tmux wait-for <name>`. Same machine, automated: a
Claude Code Stop hook. Cross-machine: an `ntfy` curl call. Fall back to
bounded polling only if none of those genuinely fit the situation.

## Rule 21: resource and tooling awareness

Before prescribing `idev`/GPU allocation, confirm the task actually needs
GPU compute. Monitoring, file checks, git operations, and grep/audit work
belong on the login node: they preserve SU budget and aren't
walltime-bounded. Consider explicitly, by name, whenever they fit: `/loop`
for repeated checks (session-scoped, minimum 1-minute interval), a Claude
Code Stop hook or `tmux wait-for` for completion signals, `Ctrl+B` to
background a blocking command, `ntfy` for cross-machine alerting.

## Rule 22: execution mode decision, per pane

For each pane's next task, decide out loud, in one line: is this faster
and more reliable as a Claude Code prompt (multi-step reasoning, edits,
judgment, cross-referencing research files), or as manual typed commands
(deterministic, sequential, no judgment needed)?

- **Claude Code prompt fits:** write the labeled `Claude Code prompt:`
  block, as explicit and exhaustive as if it will run completely
  unsupervised: exact file paths, exact function or variable names, exact
  skills to invoke, exact success criteria, exact failure signatures to
  watch for.
- **Manual commands fit:** output (1) the exact commands to reach the
  correct directory and host first, then (2) a minimum of 10 manual
  commands that execute the task. If the real task needs fewer than 10,
  pad only with real verification steps (`git status`, `git log`, `grep`,
  `ls`), never fabricated no-ops.

There is no separate "20-plus total tasks" quota to hit across the round.
That number is an emergent property of enough panes landing in manual
mode at 10-plus real commands each; it is not an independent target, and
padding a Claude Code prompt pane with filler commands to inflate a total
count is exactly the kind of quality-reducing move this skill exists to
prevent. Being exhaustive means real depth per pane, not a bigger number.

## Rule 23: standing code and process rules

No inline comments or docstrings, in any language, ever. Track 1 never
touches Apptainer, Track 2 never touches `mpmenv`. No em-dashes anywhere
in any output. Heredoc over nano for whole-file rewrites.

---

## Hard requirements: the intensity gate

An output is not finished until every one of these is true. If one
genuinely cannot be satisfied this round, for example a pane truly has no
research file that applies, state that explicitly in the block rather
than silently omitting the requirement or filling space with a thin
placeholder. A long, dense, fully-substantiated output is the correct and
expected result of this skill. Do not trade completeness for brevity, and
do not shorten or summarize the output purely to save length.

- [ ] Surface stated once, as the first line of the output (Claude Code
      or Claude.ai chat).
- [ ] Pending-approvals batch present, even if the honest content is
      "none found," stated explicitly rather than omitted.
- [ ] Exactly one block per confirmed-live pane. Not padded with
      fabricated panes, not silently dropping panes that are actually
      live.
- [ ] Every block states machine, working directory, execution mode, and
      a one-line justification for that mode choice (Rule 22).
- [ ] Every block names at least one specific research file it checked,
      or explicitly states it checked the living map (Rule 18) and found
      nothing applicable.
- [ ] Every block names, by exact string, every one of Josie's existing
      skills that genuinely applies to that pane's task (Rule 14), not a
      generic mention.
- [ ] Every block that touches a number, threshold, citation, or physical
      parameter shows the trace, formula, conservation law, citation, or
      measurement, never a bare assertion (Rule 14).
- [ ] Every manual-mode block has 10 or more real, verified commands.
      Every Claude Code prompt block is as explicit and exhaustive as
      something meant to run completely unsupervised.
- [ ] Cross-pane consistency and dedup passes (Rules 7, 8) are stated as
      having run, with either "no conflicts found" or the actual
      correction applied everywhere it's needed.
- [ ] Every next task is mapped to one of the three deadline anchors
      (Rule 13), or explicitly flagged optional/deferred.
- [ ] Destructive actions (Rule 16) are flagged for confirmation, never
      bundled silently into a larger block.
- [ ] The SESSION_STATE.md writeback instruction is present, last.
- [ ] No em-dashes, no inline comments or docstrings in generated code,
      no fabricated pane, no fabricated command, no unverified citation.

This checklist is what step 8 of the procedure and the self-check below
are actually checking against. Treat a failed item as a defect to fix
before output, not a judgment call to skip.

---

## Output format, exact

1. One line stating the active surface (Claude Code or Claude.ai chat).
2. Pending-approvals batch (Rule 1), stated explicitly even if empty.
3. One block per confirmed-live pane (canonically C0 to C5 in canitford,
   F0 to F5 in ford). Each block states: machine, working directory,
   execution mode chosen and why (one line), then the block itself,
   satisfying the hard-requirements gate above.
4. One final instruction to update `SESSION_STATE.md` with this round's
   findings: what's newly confirmed done, what's newly blocked, and what
   got reassigned.

Output all of this directly. No closing question, no menu of options, on
this specific dispatch output. This is a deliberate exception to the
general one-question check-in habit: it only applies here, because this
output is meant to be operational and immediately actionable, not
conversational. Normal chat conventions still apply to everything outside
this specific output.

## Self-check, run silently before finalizing

Walk the hard-requirements checklist above item by item. Also confirm: is
every claim traced to a real source? Was the last prescribed task's
outcome actually confirmed before building on it? Does a correction
affecting multiple panes get applied to all of them? Are dependent edits
sequenced with a concrete check rather than a vague rule? Any pane
collision, duplicate work, or wasted GPU-node risk? Was a research file
cited without confirming it still exists? Fix anything this catches, then
output. Don't narrate this check happening.

## Known failure modes this version closes

These are specific, named fixes for prior rounds that didn't deploy
cleanly, kept here so future edits to this file don't quietly reopen them.

1. **No log attached, or a stale/wrong one.** Fixed by Step 0: ask in one
   line and stop, rather than guessing pane state from memory.
2. **12 panes assumed when fewer are actually live.** Fixed by the
   topology check running before anything else; output matches confirmed
   reality, never padded to a round number.
3. **Hardcoded research-file map going stale.** Fixed by Rule 18: the
   living files (`SESSION_STATE.md`, `CLAUDE.md`, `PROJECT_FILE_MAP.md`)
   are the source of truth; the embedded table is a labeled fallback only.
4. **Logic duplicated instead of calling existing skills, causing drift.**
   Fixed by Rule 14 naming the exact skills to invoke for physics,
   provenance, connectors, and bug triage, instead of reimplementing any
   of that here.
5. **A "20-plus tasks" target competing with the per-pane 10-command
   minimum.** Fixed by Rule 22: the total is emergent, never an
   independent quota, never padded.
6. **No enforced order, so late steps (writeback, self-check) got
   skipped under time pressure.** Fixed by the 10-step numbered
   procedure; nothing downstream starts before the step above it outputs.
7. **The general chat check-in habit creeping into an operational
   output and adding a needless pause.** Fixed by an explicit, scoped
   exception stated in the output format section, not a silent override.
8. **Auto-trigger not firing on a pasted log because the phrasing
   didn't match.** If that happens, say so explicitly: "run
   panel-audit-dispatch," or "audit my panes," forces it.
9. **Only usable from Claude Code, so a chat-only round either failed or
   silently produced a thinner result.** Fixed by the Surface section:
   chat mode runs the identical procedure and hard-requirements gate,
   only the delivery format changes.
10. **Output quietly getting shorter or shallower than the task actually
    warranted.** Fixed by the hard-requirements gate: every item is
    checked explicitly, and completeness is stated as correct, not
    something to trim for brevity.

## Version note

v2. Supersedes v1 by making Claude.ai chat a first-class surface (not a
fallback) and adding the explicit hard-requirements gate above, per
direct instruction to make the output more exhaustive and to enforce that
exhaustiveness rather than leave it to judgment. All v1 rules are
preserved unchanged. This file is the canonical, only version of this
workflow going forward; it supersedes re-pasting the original raw prompt
by hand.
