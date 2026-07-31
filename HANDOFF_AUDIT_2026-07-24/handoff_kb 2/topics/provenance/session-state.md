---
id: 20260724-session-state
title: SESSION_STATE.md duplicate set
tags: [provenance, git, handoff]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-claude-md, 20260724-embedded-repo]
summary: 7 copies of SESSION_STATE.md found; canonical is ~/can-it-ford/SESSION_STATE.md, hash-matched against GitHub main HEAD.
---

# SESSION_STATE.md duplicate set

> Summary: 7 copies found; canonical is `~/can-it-ford/SESSION_STATE.md`.

## Method
Canonical blob hash from GitHub: `6b21ab3413b67f068f526764c007d6a6fb8fcc7a`, repo root. GitHub also already holds an archived prior-conflict copy at `archive/superseded_docs/SESSION_STATE.md.bak_before_conflict_resolve` — evidence the archive-don't-delete pattern has been used correctly before.

## Findings

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/SESSION_STATE.md` | **YES** | Hash matches. |
| `~/can-it-ford/can-it-ford/SESSION_STATE.md` | No | Orphaned duplicate inside the embedded/nested repo. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/SESSION_STATE.md` | No | Different-branch worktree copy. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/SESSION_STATE.md` | Effectively yes | Hash matches canonical. |
| `~/can-it-ford-BACKUP-before-history-purge/SESSION_STATE.md` | No | Stale pre-purge backup. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/SESSION_STATE.md` | No | Redundant nested copy inside the backup. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/SESSION_STATE.md` | No | Redundant nested worktree copy inside the backup. |

## Related
- [CLAUDE.md duplicate set](claude-md.md) — same structural pattern.
- [The embedded/orphaned nested repo incident](embedded-repo-incident.md)
