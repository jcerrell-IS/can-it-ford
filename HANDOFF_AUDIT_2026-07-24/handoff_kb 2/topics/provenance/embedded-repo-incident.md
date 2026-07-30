---
id: 20260724-embedded-repo
title: The embedded/orphaned nested repo incident
tags: [provenance, git, structure]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-claude-md, 20260724-session-state, 20260724-resume-pane, 20260724-vehicle-reference]
summary: ~/can-it-ford/can-it-ford/ is a full stale git checkout embedded inside the real repo; GitHub's newest commit already untracked it, but the folder is still physically on disk in two places.
---

# The embedded/orphaned nested repo incident

> Summary: a full separate git checkout sits inside the real repo at `~/can-it-ford/can-it-ford/`, and again inside the backup at `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/`. GitHub already fixed its own tracking of this; the disk copies are the leftover.

## Context
GitHub `jcerrell-IS/can-it-ford` HEAD (`daf453e2dccc28d3d7eb8bad77ece65e2913a709`, 2026-07-24T00:01:44Z) has the commit message: **"Remove accidentally-committed embedded git repository, add to gitignore."** That's a direct, dated confirmation this exact structure was a known incident, fixed today on the GitHub side only.

## Details
- `~/can-it-ford/can-it-ford/` has its own `.git`, remote pointed at the same GitHub repo, but HEAD frozen at `ca91b123ae72f681a1c4cda1f04931a8a0dad82e` — an older commit than the live repo's `daf453e2d`.
- It has its own uncommitted local diffs (a deleted `bug-triage-protocol_SKILL.md`, new untracked `bug-triage-protocol/` and `panel-audit-dispatch/` skill folders) that never reached the real history.
- The exact same structure is duplicated a third time inside `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/`, meaning the backup was made by copying the already-broken directory wholesale.
- Every duplicate file traced to this folder in `20260724-claude-md`, `20260724-session-state`, and `20260724-resume-pane` originates here.

## Not acted on
Per the audit's no-delete rule, these folders were not removed. Recommended human decision: delete both `~/can-it-ford/can-it-ford/` and `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/can-it-ford/` (the nested one inside the backup is the same path, one level in), since GitHub's own gitignore change confirms they're not supposed to exist.

## Related
- [vehicle_data_master_reference_2026-07-21.json duplicate set](vehicle-reference.md) — the file with the highest-stakes divergence traced to this folder.
