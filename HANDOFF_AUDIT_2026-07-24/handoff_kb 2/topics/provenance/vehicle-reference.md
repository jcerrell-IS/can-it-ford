---
id: 20260724-vehicle-reference
title: vehicle_data_master_reference_2026-07-21.json duplicate set
tags: [provenance, git, handoff]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-embedded-repo, 20260724-worktrees-backup]
summary: 8 copies found, spanning 4 genuinely different content versions (not just stale copies of one file) — the highest-risk finding in this audit.
---

# vehicle_data_master_reference_2026-07-21.json duplicate set

> Summary: 8 copies, **4 distinct content versions**. This is the one to actually act on before any script reads this file by bare filename.

## Method
Canonical blob hash from GitHub: `9608d43c98a9c06c0a39303fa3589adfd4dd1875`, at `reference_data/vehicle_data_master_reference_2026-07-21.json`.

## Findings

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/reference_data/vehicle_data_master_reference_2026-07-21.json` | **YES** | Hash matches. |
| `~/can-it-ford/can-it-ford/vehicle_geometry_research/vehicle_data_master_reference_2026-07-21.json` | No | Different content AND different path (`vehicle_geometry_research/` is superseded; `reference_data/` is current). Pre-move version, orphaned inside the embedded repo. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/reference_data/vehicle_data_master_reference_2026-07-21.json` | No | A third distinct hash — in-progress WIP version, on the branch literally named for reconciling this file. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/reference_data/vehicle_data_master_reference_2026-07-21.json` | Effectively yes | Hash matches canonical. |
| `~/can-it-ford-BACKUP-before-history-purge/reference_data/vehicle_data_master_reference_2026-07-21.json` | No | A fourth distinct hash — oldest version, pre-purge snapshot. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/vehicle_geometry_research/vehicle_data_master_reference_2026-07-21.json` | No | Same hash as the embedded-repo's old-path copy. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/reference_data/vehicle_data_master_reference_2026-07-21.json` | No | Same hash as the WIP-branch copy. |
| `~/Downloads/vehicle_data_master_reference_2026-07-21.json` | No | Same hash as the oldest backup version (mtime July 21) — orphaned loose export in Downloads. |

## Why this matters more than the other three files
The other three duplicated files are mostly "stale copy of the same thing." This one is four *different* datasets under one filename. `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref` exists specifically to reconcile this — don't merge that branch or trust any of its numbers until the reconciliation is finished and re-verified against a live source, per the parent `provenance-audit` skill's source-tier rules.

## Related
- [The embedded/orphaned nested repo incident](embedded-repo-incident.md)
- [Worktrees and the pre-purge backup, structurally](worktrees-and-backup.md)
