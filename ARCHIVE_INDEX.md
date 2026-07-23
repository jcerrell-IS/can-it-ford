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

## Safe to delete, byte-identical duplicates, awaiting approval

These were NOT moved and NOT deleted. Each pair is byte-identical (same MD5). Listed here
only as deletion candidates for a human to approve. Verify the "keep" choice before
deleting, especially for the sweep scripts, which are wired into live automation.

### Pair 1 — older sweep-script version (MD5 `f3b35fbaf51410559c170880acaa50be`)
- `_inbox/2026-07-17_canitford_inbox_sweep.sh`
- `_inbox/canitford inbox sweep 2.sh`

Both are an older version of the inbox sweep, superseded by the active script (Pair 2's
kept file). Candidate: delete both, or keep one as an "older version" reference.

### Pair 2 — current sweep script (MD5 `0adefd72944508a9321eda51b2f20542`)
- `_inbox/canitford_inbox_sweep.sh`  ← **KEEP: this is the script the launchd plist actually runs**
- `_inbox/2026-07-18_canitford_inbox_sweep.sh`  ← disposable dated twin

Candidate: delete the dated `2026-07-18_` copy. Do NOT delete `canitford_inbox_sweep.sh`;
the plist's `ProgramArguments` points at it by that exact name.

### Pair 3 — launchd plist (MD5 `8746c13e37954a33d2d7eac47d91f8ba`)
- `_inbox/com.josie.canitford-sweep.plist`
- `_inbox/2026-07-19_com.josie.canitford-sweep.plist`

Candidate: delete the dated `2026-07-19_` copy after confirming which filename the loaded
LaunchAgent references (`launchctl list | grep canitford`).

### Pair 4 — vehicle files list (MD5 `ffabeee18d096ae3f13ddc719a241739`)
- `_inbox/vehicle_files_to_pull.md`
- `files/vehicle_files_to_pull.md`

Candidate: keep one canonical copy, delete the other. Both are currently untracked.

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
- **`files/` directory** — a partial mirror of `_inbox` content (holds a duplicate of
  `vehicle_files_to_pull.md`). Whether it should be merged into `_inbox` or removed is a
  structural decision.
- **`archive/` vs `_archive/` naming** — this pass created `archive/`; a pre-existing
  `_archive/invalidated_data/` also exists. Consider consolidating to one.
- **`Instructions.docx.md`** (root, tracked) — intentionally left in place: it is the live
  REU poster/paper submission instructions (poster deadline July 27), an active reference,
  not scratch.
