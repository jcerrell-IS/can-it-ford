---
id: 20260724-resume-pane
title: resume_pane.sh duplicate set
tags: [provenance, git, handoff]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-claude-md, 20260724-embedded-repo]
summary: 7 copies of resume_pane.sh found; canonical is ~/can-it-ford/scripts/resume_pane.sh, hash-matched against GitHub main HEAD.
---

# resume_pane.sh duplicate set

> Summary: 7 copies found; canonical is `~/can-it-ford/scripts/resume_pane.sh`.

## Method
Canonical blob hash from GitHub: `44c8aa7313728974ddfec8d445abbb1907d7fc87`, at `scripts/resume_pane.sh`.

## Findings

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/scripts/resume_pane.sh` | **YES** | Hash matches. |
| `~/can-it-ford/can-it-ford/scripts/resume_pane.sh` | No | Older version, orphaned inside the embedded repo. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/scripts/resume_pane.sh` | No | Same older hash as the embedded-repo copy — worktree not yet rebased onto the latest script. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/scripts/resume_pane.sh` | Effectively yes | Hash matches canonical. |
| `~/can-it-ford-BACKUP-before-history-purge/scripts/resume_pane.sh` | No | Stale pre-purge backup, older version. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/scripts/resume_pane.sh` | No | Redundant nested copy. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/scripts/resume_pane.sh` | No | Redundant nested worktree copy. |

## Related
- [The embedded/orphaned nested repo incident](embedded-repo-incident.md)
