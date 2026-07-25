# Session State

POINTER FILE. Reduced to a pointer on 2026-07-25 by Lane A, per `docs/SESSION_DISPATCH_2026-07-25.md` PART 4 A4. It deliberately restates no number that lives in the ledger or a handoff, because duplicated numbers are exactly how this project has repeatedly shipped stale ones.

The real report store is `.claude/handoffs/INDEX.md`. Read that next.

---

## PRESERVED VERBATIM, DO NOT REWORD OR RELOCATE

The block below is reproduced byte-for-byte from the pre-restructure file, lines 13 to 37, md5 `d4f9d11276f0e7e29aa8947303b2b982`, 25 lines, 2781 bytes. It stays at the top of this file. If you edit it, the drift check it exists to enable stops working.

### 2026-07-25 03:32 UTC (2026-07-24 22:32 CDT), orchestrator: CLAUDE.md drift fingerprint (ADDITIVE, supersedes nothing)

Purpose: unattributed CLAUDE.md changes are this project's single most repeated failure class. This block records a fingerprint so the next divergence is caught in one command instead of investigated for an hour. Every value below was read live this pass with md5/wc/stat over ssh, not from a summary. This block does NOT supersede the 02:58 UTC block below it; it adds a reference fingerprint only.

GLOBAL `~/.claude/CLAUDE.md`, byte-identical on all three machines this pass:
- md5 `a954a8e03b76c69e1a491a437048b83c`, 2004 bytes
- headings in order: L1 `# Global working rules, applies to every project on this machine`, L3 `## Formatting, always`, L7 `## Verification, always`, L13 `## Before any destructive action`, L19 `## Response style`, L23 `## Safe Resume Protocol`
- Mac `/Users/josie/.claude/CLAUDE.md`, mtime 2026-07-15 06:50:41 CDT
- Vista `/home1/11603/jcerrell0629/.claude/CLAUDE.md`, mtime 2026-07-17 16:45:15 CDT
- LS6 `/home1/11603/jcerrell0629/.claude/CLAUDE.md`, mtime 2026-07-24 00:54:38 CDT

PROJECT `/Users/josie/can-it-ford/CLAUDE.md`:
- md5 `08a4ebac53bc85ebe3e03f7bd423d952`, 3336 bytes, mtime 2026-07-24 20:39:23 CDT, last commit `9b9cac4`
- headings in order: L1 `## Multi-Pane Standing Rules`, L43 `## git filter-repo standing note`, L51 `## File provenance, do not cite anything not on this list without checking it live`

LS6 backups `/home1/11603/jcerrell0629/.claude/backups/`:
- `CLAUDE.md.project-misfiled.2026-07-23.bak`, md5 `02377adec4329aaa3f27ada55ccb81b9`, 37733 bytes, mtime 2026-07-16 18:00:24 CDT

RESOLVED this pass: the LS6 global copy previously held the 706-line project document misfiled into the global slot (md5 `02377ade...`, 37733 bytes), meaning LS6 sessions ran with no Safe Resume Protocol, no verify-live rule, and no destructive-action pre-check. LS6 now matches Mac and Vista. The misfiled content is preserved in the backup above and its content also exists at `/work/11603/jcerrell0629/vista/CLAUDE.md`. Nothing was lost.

PROVENANCE GAP, recorded honestly rather than guessed: the LS6 replacement and that backup were made by an actor this pass could not identify. Neither of the two live Claude Code sessions (`Vista`, `Vista (fork)`) shows any LS6 write in its transcript. End state verified correct by md5; authorship unattributed.

DRIFT CHECK, one command, expect the same hash three times:
`md5sum ~/.claude/CLAUDE.md && ssh vista 'md5sum ~/.claude/CLAUDE.md' && ssh ls6 'md5sum ~/.claude/CLAUDE.md'`
Expected: `a954a8e03b76c69e1a491a437048b83c` on all three. Any mismatch means drift since 2026-07-25 03:32 UTC; diff against the headings list above to see which document replaced which.

---

## Where truth lives, in order

1. Live code, live CSV, live git. Nothing below outranks a read you do yourself.
2. `.claude/handoffs/` per-pane HANDOFF files. A `MISSION` file is an inbound assignment that may never have been carried out, so never read one as a report. Only HANDOFF files are reports.
3. `docs/VERIFIED_FACTS_LEDGER_july24.md`, Sections A through G. It supersedes this file wherever they conflict.
4. `paper_draft.md` at REPO ROOT. `paper/paper_draft.md` is a redirect stub.
5. `docs/SESSION_DISPATCH_2026-07-25.md` for lane assignment and the universal contract.

## Git

HEAD `b00bf7b`. `git rev-list --count origin/main..main` returns 0, everything pushed. Verified live 2026-07-25 by Lane A.

Handoffs written earlier tonight record "ahead 2", "ahead 3", "ahead 4" and "ahead 6". Those are four stale snapshots of a count that moved during the night, not four disagreements to adjudicate. Do not treat them as a conflict.

Modified uncommitted: `.claude/hooks/gate_destructive.sh`, `.claude/hooks/gate_protected_files.sh`, `.claude/settings.json`.

## Pane roster, live 2026-07-25

Four tmux sessions, sixteen panes, all Mac-local. Per-pane status lives in that pane's handoff file, not here. This roster is who exists, not what finished.

| Session | Pane | Role | State |
|---|---|---|---|
| canitford | 0.0 | C0-CRASH-RETEST | zsh, Claude exited |
| canitford | 0.1 | C1-TOCSV-FIX-SWEEP | claude running |
| canitford | 0.2 | C2-DESIGNSAFE-FIX | claude running |
| canitford | 0.3 | C3-MASS-RECONCILE | zsh, Claude exited |
| canitford | 0.4 | canitford-C4 | claude running |
| canitford | 0.5 | C5-MESH-COMPLETE | claude running |
| ford | 0.0 | F0-XIA-CITATION | claude running |
| ford | 0.1 | F1-VISTA-CLAUDEMD | claude running |
| ford | 0.2 | F2-PROJECT-INSTR | zsh, Claude exited |
| ford | 0.3 | F3-TRACK1-HOLLOW | zsh, Claude exited |
| ford | 0.4 | F4-COUPLING-DOC | claude running |
| ford | 0.5 | F5-SESSION-STATE | claude running |
| monitor | 0.0, 0.1, 0.2 | poster assembly since Jul 23 22:57; 0.0 reports 9 awaiting input | 0.0 and 0.1 running. Do not duplicate, do not kill |
| hero | 0.0 | holds an ssh | not Lane A's |

A `~/.pane_signals/*_done` file proves a turn ended, not that a task completed. `canitford_0_7_done` exists for a pane that does not exist. Never read those as status.

## Human decisions, no lane may make these

Full text in `docs/SESSION_DISPATCH_2026-07-25.md` PART 8.

1. Title A or Title B. Blocks C4, C6 and `monitor:0.1`.
2. Traction basis, cell-boundary or nominal-plane. The two give different understatement percentages and the current caption mixes them.
3. The three `[CONFIRM]` blocks in `poster_text_draft.md`, author list and affiliation. Needs Kumar.
4. Wording for the four stale-explanation files in dispatch PART 7.
5. Whether `paper_draft.md` section 4.2 stays as written, narrows, or retracts.

## Deadlines

Poster PDF upload Mon Jul 27 09:00 CST, `Cerrell_TACC_42x56.pdf`, PDF only, under 40 MB. Mock poster Tue Jul 28. Poster session Jul 30. Final paper Fri Jul 31. Full table in dispatch PART 9.

## Where the pre-restructure history went

All 396 lines of the pre-restructure file are preserved byte-for-byte at `.claude/handoffs/2026-07-24_ARCHIVE_session-state-pre-restructure.md`, md5 `565d5b308e5f9b4e90de3354e655155f`. Nothing was deleted.
