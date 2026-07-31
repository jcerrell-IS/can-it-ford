---
id: 20260724-claude-md
title: CLAUDE.md duplicate set
tags: [provenance, git, handoff]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-embedded-repo, 20260724-worktrees-backup]
summary: 12 copies of CLAUDE.md found across target directories; canonical is ~/can-it-ford/CLAUDE.md, hash-matched live against GitHub main HEAD (daf453e2d).
---

# CLAUDE.md duplicate set

> Summary: 12 copies found; canonical is `~/can-it-ford/CLAUDE.md`, hash-matched against GitHub `main` HEAD `daf453e2d`.

## Context
CLAUDE.md is used both as this git repo's root instructions file AND as Claude Desktop's own per-folder project-instructions filename. Several "duplicates" below are not the same lineage at all, just a filename collision.

## Method
Canonical blob hash pulled live from GitHub (`search_code filename:CLAUDE.md repo:jcerrell-IS/can-it-ford`): `ebf2b5ad0510caca5f9a932819ceedba876af334`, at repo root, HEAD `daf453e2dccc28d3d7eb8bad77ece65e2913a709`. Every local copy hashed with `git hash-object` and compared directly.

## Findings

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/CLAUDE.md` | **YES** | Hash matches exactly. Live main-branch working copy. |
| `~/can-it-ford/can-it-ford/CLAUDE.md` | No | Content matches, but lives inside the orphaned embedded repo — see `20260724-embedded-repo`. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/CLAUDE.md` | No | Different hash — worktree checked out on an older commit. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/CLAUDE.md` | Effectively yes | Hash matches canonical; worktree currently in sync with `main`. |
| `~/can-it-ford-BACKUP-before-history-purge/CLAUDE.md` | No | Stale pre-purge snapshot, frozen ~2026-07-23 12:50. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/CLAUDE.md` | No | Same stale hash, redundant nested copy inside the backup. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/CLAUDE.md` | No | Same stale hash, triple-nested redundant copy. |
| `~/Desktop/CLAUDE.md` | No | Different content entirely (1,344 bytes, last touched April 6). Not this repo — orphaned leftover from an earlier/different setup. |
| `~/Documents/Claude/reu/CLAUDE.md` (= `~/Claude/reu/CLAUDE.md`, same physical folder, see `20260724-worktrees-backup`) | No | Different project entirely — REU/session-instructions doc, not the repo's file. |
| `~/Documents/Claude/Projects/SCIENCE ENTIRETY/CLAUDE.md` | No | 0 bytes. Different project entirely, unused placeholder. |
| `~/Documents/Claude/Projects/SCIPE UT Austin baby/REU_Knowledge/newton/CLAUDE.md` | No | 11 bytes. Different project entirely, Newton-reference stub. |
| `~/Documents - Josephine's MacBook Air/Claude/CLAUDE.md` | No | Different content (5,034 bytes, July 3). Stale duplicate from an old Mac profile/migration. |

## Related
- [The embedded/orphaned nested repo incident](embedded-repo-incident.md) — explains why two of the non-canonical copies exist.
- [Worktrees and the pre-purge backup, structurally](worktrees-and-backup.md) — explains the worktree and backup entries.
