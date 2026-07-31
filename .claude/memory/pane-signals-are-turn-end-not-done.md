---
name: pane-signals-are-turn-end-not-done
description: "~/.pane_signals/*_done files fire on every Claude Code turn end, not on task completion, so they cannot be used as a round-completion oracle"
metadata: 
  node_type: memory
  type: project
  originSessionId: 369e0b2a-176d-4c42-bd26-4f60cfca709c
  modified: 2026-07-24T03:11:20.713Z
---

The file-based pane signaling wired into `.claude/settings.json` (commit `0042612`,
2026-07-23) writes `~/.pane_signals/<session>_<window>_<pane>_done` from a **Stop**
hook. Stop fires at every turn end, so a `*_done` file means "that pane's Claude
finished a turn", NOT "that pane finished its task". Verified empirically on
2026-07-23: pane ford:0.0 wrote `ford_0_0_done` at 22:04:25 and was still visibly
running a Crossref fetch at 22:07; pane ford:0.5 rewrote its own signal mid-task.

The signals are unreliable in **both** directions: a fresh signal can mean a pane
merely paused at an AskUserQuestion (canitford:0.1 did exactly this), and a stale
signal can sit on a pane that has since done substantial work (ford:0.3, signal
from 20:45, work continuing well past it). The hook also never clears old signal
files, so signals survive across rounds.

**Why:** the mechanism was built to replace a broken cross-machine `tmux wait-for`,
and it does solve cross-machine delivery, but Stop-hook semantics were never
task-scoped, so it reports liveness rather than completion.

**How to apply:** never treat the existence or freshness of a `*_done` file as
proof a pane's task is complete. Verify every pane claim against a real artifact
instead: `git log`/`git show` for a commit, the actual file on disk, a log file, or
`squeue -u jcerrell0629`. Compare signal mtime against round start to detect
cross-round leftovers, and read the pane itself with `tmux capture-pane` to tell an
idle-at-prompt pane from a working one. See [[provenance-audit-verify-live]].
