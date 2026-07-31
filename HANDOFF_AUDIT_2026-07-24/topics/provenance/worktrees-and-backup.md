---
id: 20260724-worktrees-backup
title: Worktrees and the pre-purge backup, structurally
tags: [provenance, git, structure]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-claude-md, 20260724-embedded-repo]
summary: The two .claude/worktrees/ folders are legitimate git worktrees (confirmed via gitdir pointers); the BACKUP directory is a genuine frozen pre-rewrite snapshot, not a second live project.
---

# Worktrees and the pre-purge backup, structurally

> Summary: worktrees are real, confirmed via their `.git` gitdir pointer files. The backup directory is a legitimate frozen snapshot with its own uncommitted edits, not a duplicate live project.

## Worktrees
`~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref` and `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f` each have a `.git` **file** (not directory) containing a `gitdir:` pointer to `/Users/josie/can-it-ford/.git/worktrees/<name>` — confirmed present, so these are real `git worktree` checkouts, not orphaned copies. `git status`/`rev-parse` could not be run against them from this sandboxed audit session (the absolute `/Users/josie/...` gitdir path doesn't resolve across the device-bridge mount boundary) — that's an audit-environment limitation, not evidence the worktrees are broken. Verify branch/dirty-state directly in Terminal on the Mac if precision matters.

Content-hash results (see the four file-specific notes) show:
- `physics-params-audit-541e4f` is currently in sync with `main` on all four target files.
- `reconcile-vehicle-master-ref` is behind on all four, and is the active branch for reconciling the vehicle reference JSON (see `20260724-vehicle-reference`).

## The backup directory
`~/can-it-ford-BACKUP-before-history-purge` is a real git repo, same remote (`https://github.com/jcerrell-IS/can-it-ford.git`), HEAD `0f35620e70f7fa293cbc25b3612879eba11d81ac` — 190 commits, vs. the live repo's 201. It is **not ahead** of live in any way; it's simply older (frozen ~2026-07-23 12:50-12:56), consistent with its name: a snapshot taken before a planned `git filter-repo` history rewrite that hasn't happened yet (the live repo has since received 11+ more ordinary commits, unrelated to any rewrite).

It carries its own uncommitted local edits that never reached the real history: `README.md`, `SESSION_STATE.md`, `data/track1_sweep_v2/mpm_sweep_data_schema.md`, `paper_draft.md`, `vehicle_params.py` (all modified), plus new files under `_inbox/` (see `20260724-staged-inbox`).

## Related
- [The embedded/orphaned nested repo incident](embedded-repo-incident.md) — the backup duplicates this structure too.
- [Staged raw session exports in the backup repo](../security/staged-inbox-risk.md)
