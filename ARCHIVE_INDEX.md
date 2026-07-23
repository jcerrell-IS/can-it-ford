# ARCHIVE_INDEX.md

Index of files relocated during the repo-organize pass on 2026-07-22. This was an
organize-only pass: move and document, never delete. Nothing here was removed. If a file
seems missing from where it used to be, check this table before assuming it is gone.

Two folders exist for archived material:
- `archive/` (no underscore): created by this pass, holds relocated scratch/backup/one-off files.
- `_archive/` (leading underscore): pre-existing, holds `invalidated_data/`. Left untouched.
  Consolidating the two names is a "needs a human decision" item below.

---

## Moved files

Legend for "git": `git mv` = tracked file, history preserved. `add` = was untracked,
now newly tracked at the archive path. `disk-only` = physically moved but intentionally
kept out of git (see `.gitignore`), so the repo does not carry large session-log blobs.

| File | Original location | New location | git | Reason |
|---|---|---|---|---|
| `files.zip` | repo root | `archive/superseded_docs/files.zip` | git mv | Zip bundle of 13 dated July-13 snapshots (superseded `CLAUDE.md` variants, session audits). Pure historical bundle. `docs/session_notes/MANIFEST_july13.md` references it; that pointer now resolves here. |
| `SKILL_geoelements-tech-reference_FULL_REVISED.md` | repo root | `archive/superseded_docs/` | git mv | One-off exported copy of the `geoelements-tech-reference` skill, which is now installed in `~/.claude/skills/`. Root copy is superseded staging. |
| `SKILL_NEW_mpm-render-pipeline.md` | repo root | `archive/superseded_docs/` | git mv | One-off exported copy of the `mpm-render-pipeline` skill, now installed in `~/.claude/skills/`. Root copy is superseded staging. |
| `SESSION_STATE.md.bak_before_conflict_resolve` | repo root | `archive/superseded_docs/` | add | Backup snapshot of `SESSION_STATE.md` taken before a merge-conflict resolution. Live version is `SESSION_STATE.md` at root. |
| `box_sdf_collider_setup.py.bak_jul20` | `simulation/` | `archive/deprecated_scripts/` | add | `.bak` snapshot (3881 B) of `simulation/box_sdf_collider_setup.py`. The live script stays at its normal path; only the backup moved. |
| `2026-07-20-101436-before-making-any-change-run-and-show-me-git-st.txt` | repo root | `archive/session_logs/` | add | Loose dated session dump (a captured `git status` transcript). Not referenced by any code. |
| `LIVE_SESSION_LOG.md.bak-20260720-214428` | `_inbox/` | `archive/session_logs/` | disk-only | 10 MB backup of the live session log. Kept on disk, not tracked (`.gitignore`). Live log `_inbox/LIVE_SESSION_LOG.md` untouched. |
| `LIVE_SESSION_LOG.md.zip` | `_inbox/` | `archive/session_logs/` | disk-only | 9.4 MB zipped copy of the live session log. Kept on disk, not tracked (`.gitignore`). |
| `pane2_export.txt` | repo root | `archive/session_logs/` | disk-only | Manual tmux pane capture. Already globally gitignored (`pane*_export.txt`); stays untracked at the new path. |
| `pane4_export.txt` | repo root | `archive/session_logs/` | disk-only | Manual tmux pane capture. Already globally gitignored; stays untracked at the new path. |

The live `_inbox` sweep automation (`canitford_inbox_sweep.sh`, launched by the launchd
plist) only moves files from Downloads/Desktop into `_inbox`; it does not read any of the
files moved above, so relocating them does not affect it.

---

## 2026-07-23 `vehicle_data_master_reference` reconciliation

Separate from the 2026-07-22 organize pass. Three files shared the name
`vehicle_data_master_reference_2026-07-21.json`; they were reconciled to one canonical
file. The surprise: two of the three, despite the filename, were NOT the physical-parameter
master at all. They were the older vehicle-CLASS-COMPARISON summary (AR&R limiting depth /
DV thresholds, moving-vehicle instability literature, the proposed 4th vehicle class) and
were byte-identical to each other (MD5 `26796981b0a65c113095a291f2a267a8`). That
class-comparison content existed nowhere else in the repo, so it was archived, not dropped.

| File | Original location | New location | git | Reason |
|---|---|---|---|---|
| `vehicle_data_master_reference_2026-07-21.json` | `vehicle_geometry_research/` | `archive/superseded_docs/vehicle_class_comparison_2026-07-21.SUPERSEDED.json` | git mv (renamed) | Filename collided with the physical-parameter master but the content is the vehicle-class-comparison summary. Renamed on archive to end the collision. Byte-identical to the `.OLD-4906B` twin removed below. |

Canonical kept in place and unmoved: `reference_data/vehicle_data_master_reference_2026-07-21.json`
(the physical-parameter master). It was edited in this pass to replace the single Yaris `FLAG`
string with an explicit `rho_reconciliation` block recording BOTH mass options
(1100 kg MASH nominal → rho 310.50, vs 1078 kg NCAC-modeled → rho 304.28, both at collider
box volume 3.5427 m^3), with 1078/304.28 marked RECOMMENDED (mesh's actual built geometry)
and the still-open collider-volume basis (3.5427 vs raw mesh 6.8185) noted, not silently
resolved. The class-comparison content is now ONLY at the archived path above; it was never
present in the canonical file.

### Byte-identical twin removed (MD5 `26796981b0a65c113095a291f2a267a8`)
- KEPT:    `archive/superseded_docs/vehicle_class_comparison_2026-07-21.SUPERSEDED.json` (the archived copy above)
- DELETED: `reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B` (was git-tracked; recoverable from history; byte-for-byte identical to the kept copy)

---

## Byte-identical duplicates, RESOLVED 2026-07-22

Each pair below was byte-identical (same MD5, re-verified live before deleting). The
redundant copy was removed, keeping exactly one canonical copy of each. Checksums are
recorded so the removals stay auditable. Content was preserved in every case: the kept
copy is byte-for-byte the deleted one.

### Pair 1 — older sweep-script version (MD5 `f3b35fbaf51410559c170880acaa50be`)
- KEPT:    `_inbox/2026-07-17_canitford_inbox_sweep.sh`
- DELETED: `_inbox/canitford inbox sweep 2.sh` (was git-tracked; recoverable from history)

An older version of the inbox sweep, superseded by the active script (Pair 2's kept file).
One copy retained as the "older version" reference; the awkwardly-named twin removed.

### Pair 2 — current sweep script (MD5 `0adefd72944508a9321eda51b2f20542`)
- KEPT:    `_inbox/canitford_inbox_sweep.sh` (the script the launchd plist actually runs)
- DELETED: `_inbox/2026-07-18_canitford_inbox_sweep.sh` (was git-tracked; recoverable)

The active script was kept by exact name; the dated twin removed. The live automation is
unaffected (its `ProgramArguments` still resolves).

### Pair 3 — launchd plist (MD5 `8746c13e37954a33d2d7eac47d91f8ba`)
- KEPT:    `_inbox/com.josie.canitford-sweep.plist` (git-tracked, canonical name)
- DELETED: `_inbox/2026-07-19_com.josie.canitford-sweep.plist` (was untracked)

The loaded LaunchAgent runs from `~/Library/LaunchAgents/com.josie.canitford-sweep.plist`
(confirmed via `launchctl list`), so both `_inbox` copies were only staging copies and
neither removal touched the running agent.

### Pair 4 — vehicle files list (MD5 `ffabeee18d096ae3f13ddc719a241739`)
- KEPT:    `_inbox/vehicle_files_to_pull.md` (actively-maintained inbox location)
- DELETED: `files/vehicle_files_to_pull.md` (was untracked)

Both were untracked and no code referenced either path. The copy in the actively-swept
`_inbox` was kept over the one in `files/`, whose overall fate is still an open structural
question (see below).

---

## Needs a human decision, NOT moved

Left exactly where they are. Each is plausibly scratch/misplaced but carries real
breakage risk or genuine ambiguity, so it was not moved without a human call.

- **Root simulation outputs** — `particles_d1p0_v3p0.npz`, `particles_mpm_*.npz` (9 files),
  `simulation_d1p0_v3p0.mp4`, `simulation_mpm_*.mp4` (2 files). All tracked, sitting at
  repo root instead of under `data/`. Likely read by analysis/plotting scripts; relocating
  is a content decision, not a tidy-up. Confirm no script hardcodes the root paths first.
- **Root figures** — `can_it_ford_phase_space_v2.png`, `can_it_ford_validation.png`.
  Tracked; probably referenced by the paper/poster. Move to `figures/` only after checking
  references.
- **Root result CSVs** — `phase_space_results_mpm.csv`, `phase_space_results_v2.csv`,
  `viability_audit_results.csv`. Tracked; likely produced/consumed by analysis scripts.
- **`_inbox/CAN_IT_FORD_bug_audit_july14.md`** — tracked dated audit doc. Superseded vs.
  still-cited is unclear; may still be referenced.
- **`_inbox/tonight_research_audit_and_file_map.md`** — untracked planning doc, possibly
  still active work.
- **`files/` directory** — a partial mirror of `_inbox` content. Its duplicate of
  `vehicle_files_to_pull.md` was removed during the 2026-07-22 dedup (kept copy is in
  `_inbox`). Whether the `files/` directory as a whole should be merged into `_inbox` or
  removed is still a structural decision.
- **`archive/` vs `_archive/` naming** — this pass created `archive/`; a pre-existing
  `_archive/invalidated_data/` also exists. Consider consolidating to one.
- **`Instructions.docx.md`** (root, tracked) — intentionally left in place: it is the live
  REU poster/paper submission instructions (poster deadline July 27), an active reference,
  not scratch.
