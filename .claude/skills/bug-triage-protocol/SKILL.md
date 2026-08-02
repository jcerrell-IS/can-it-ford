---
name: bug-triage-protocol
description: "Use this skill whenever Josie pastes a bug list, error log, crash traceback, session log, or terminal screenshot and wants a full triage — root cause, independence/priority ranking, file mapping, and exact runnable commands across as many parallel work streams as the problem actually has (not a fixed pane count). Trigger on \"triage this\", \"audit this\", \"bug-triage\", \"figure out what to do from here\", any pasted error/crash output, or any request to split debugging work across multiple terminal panes or shells. Applies to any coding/debugging problem, not just this project. Also trigger proactively — without being asked — whenever a bug gets resolved, a root cause is confirmed, or a load-bearing new fact surfaces during an otherwise unrelated conversation, to offer logging it before moving on."
---

## Coupled-variable check, run this before declaring any fix complete
When a fix changes one parameter (a dimension, a resolution, a mass, a mesh), before committing, explicitly list every OTHER value in the same file or system that is computed FROM or ALONGSIDE the thing just changed, and check each one, not just the one that was the original target. This project's worst repeat bug (grid_density/domain bounds/dx/water-layer-count/density, all silently coupled in ford_sweep_driver.py and can_it_ford_L2_mpm.py) came from fixing one named dependent and missing another that shared the same upstream cause. A green exit code or a clean-looking number is not evidence the coupled variables were checked, only that the one you were looking at wasn't obviously broken.

# Bug Triage Protocol

Built July 13, 2026. Section 0 and the panel-count logic are universal — usable on any coding problem. Section 0b is this project's specific accumulated trap list; skip it entirely when debugging something unrelated to Can It Ford.

## 0. Universal pre-flight — every time, any project

1. **Ground in current reality before triaging pasted material.** Check `recent_chats`/`conversation_search` for anything since the pasted material's timestamp — a bug might already be resolved, a hypothesis already tested, a path already corrected. Don't re-litigate a solved problem because the pasted log is stale. This is the single most time-saving check and the easiest to skip by accident.
2. **Path assumption.** Is the file actually where the last-known-good doc says it is? Run `pwd` and a broad `find`/`ls` before trusting any hardcoded path.
3. **Storage-tier / environment confusion.** Don't trust a shared ID number (project number, allocation number) as proof of which tier/environment something's in. Confirm the relevant variable is actually set (`echo $VARNAME`) before trusting a negative search result.
4. **Printed value ≠ actual value.** Never treat an echoed confirmation or a status line as proof of correct behavior — cross-check against what was actually passed in, especially for argument parsing.
5. **Has this exact symptom been "fixed" before?** Check history (`git log --all --follow --oneline -- "<filename>"`) before assuming a fresh root cause. A silent regression looks identical to a virgin bug.
6. **Is more than one shell/pane about to touch the same file?** Assign single-writer ownership before starting, not after duplicate work has already happened.

## 0b. Can-It-Ford-specific known traps (skip if this isn't that project)

`~/can-it-ford` does not exist on Vista — canonical path is `/work/11603/jcerrell0629/vista/can-it-ford`. `gocryptfs`/quadrant warnings on every `apptainer` call are cosmetic, ignore them. Bare `pip install torch` silently resolves CPU-only on aarch64/GH200 — always use the explicit `--index-url`. This repo's layout has drifted between flat and `simulation/`-subdirectory before. `grid_density` has flip-flopped between 64 and 128 across multiple commits — never trust a remembered value, grep it fresh. `idev` allocations rotate to a new compute-node hostname every time — a prior session's node/SSH-alias/tmux-attach may no longer point anywhere valid.

## 1. The request skeleton

```
CONTEXT: [paste the raw material — log, bug list, error output, screenshot]

I want you to:
1. Triage/rank by pressing-vs-not
2. Map dependency/independence between items
3. Root cause + exact files impacted, for each item
4. Determine N genuinely independent work streams and assign commands to each — not a fixed pane count
5. Exact runnable commands per stream, minimum count, bottom-of-the-bug to top-of-the-bug, each starting with a state-check

STANCE: Don't trust prior docs or your own framing as complete — verify against live sources first.
SCOPE: Use project knowledge search, relevant skills, Slack, and web/live docs — check more than one source.
DELIVERABLE: [file / chat], [length or count constraint if any]
```

Or just say "run bug-triage-protocol" and paste the raw material — this skill is the expansion, you don't need to write the fields out.

## 2. Panel count is never fixed — determine N from the actual work

Don't default to any particular number of panes. After triage:

- Count the genuinely independent items (can start immediately, don't wait on another item's result). That count is N.
- If N is more than the panels currently open, say so explicitly and give the exact command to open more — this is always available, not a constraint to work around:
```bash
tmux list-panes -t ford
tmux split-window -h -t ford
tmux split-window -v -t ford
tmux new-window -t ford -n <short_task_name>
```
- If some items are genuinely sequential (B needs A's result), don't force them into separate panels — keep them as one panel's ordered task list.
- If fewer independent streams exist than panels open, say that too — don't manufacture busywork to fill four panels if the real answer is two.

## 3. Every pane's command block starts with a state-check, never an action

This is a hard rule, not a suggestion. Re-running `ssh` into a session you're already in, or running `idev` from the wrong node type, produces confusing errors, not helpful ones.

**First line, always:**
```bash
hostname; pwd
```
Then route based on what comes back, never assumed:

- **`login1$` / `login2$`-style prompt, hostname is the Vista login node** → you're on the login node. Next step is `idev` — do NOT run `ssh` again, you're already connected.
- **`c###-###[gh](NNN)$`-style prompt** → you're on a Vista compute node inside an active `idev` allocation. Next step: confirm the environment is still live (`echo $GENESIS_PATH`) and `cd` to the work directory. Do NOT run `ssh` or `idev` again.
- **`josie@Josephines-MacBook-Air ... %`** → you're on the local Mac. This is the only case where `ssh jcerrell0629@vista.tacc.utexas.edu` is the correct next command.
- **Doesn't match any of these, or you're not sure** → run `hostname` and `echo $HOSTNAME` and report back before running anything else. Never chain `ssh ... && idev ...` blindly in one block without confirming which of the above is true first.

## 4. Rabbit-hole prevention ritual

- Two failed hypotheses in a row → stop, lay them out side by side with what would distinguish them, before testing a third blind.
- Any environment-level error (`No such file or directory`, connection errors) → diagnose the environment before working around it. Never wrap a broken assumption in a new command.
- Before any destructive command (`sed -i`, `mv`, `rm`, `git reset --hard`, `git clean -fd`) — confirm current live state with a fresh check immediately beforehand, not from earlier in the conversation, and confirm a backup exists.
- Three rounds of testing without forward progress → flag it and ask about escalating rather than continuing to iterate solo.

## 5. Knowledge sources, in priority order

1. Project knowledge search — first, always, for claims about project state, citations, or history.
2. Companion skills (`mpm-technical-deep-reference`, `mpm-render-pipeline`, `tacc-terminal-and-file-transfer`, `reu-research-log` for this project; whatever's relevant for anything else) — should auto-load; name explicitly if a response seems to be missing something one would know.
3. Slack — for what's actually been communicated, not what was drafted.
4. `conversation_search` / `recent_chats` — continuity with past sessions.
5. Git archaeology, prescribed as commands — first-class diagnostic tool, not a last resort.
6. Web search — for external facts that shouldn't be trusted from memory.

This skill's job is to gather missing context itself through these sources rather than requiring a perfect, fully-specified prompt. If something's still missing after exhausting these, ask one specific clarifying question — don't silently guess, and don't demand the full skeleton be filled in by hand first.

## 6. Deliverable conventions

Long-form triage tables, root-cause maps, and full command sets → a downloadable file. Direct answers and short updates → chat, TL;DR first. Append to an existing file for the same debugging thread rather than creating a new one each time. Every command is written for the person (or Claude Code) to run — never claimed as already executed from a surface with no live SSH/filesystem access.

## 7. Session-close reminder — proactive, not gated on being asked

If a bug gets resolved, a root cause confirmed, or a load-bearing fact corrected during the conversation, offer a one-line addition to the relevant status file before moving to the next task, even without being asked to wrap up. Keep the offer to one line — declinable, not mandatory.