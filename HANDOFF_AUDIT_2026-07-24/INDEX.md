# Can It Ford — Handoff Knowledge Base — Index

Built 2026-07-24. Purpose: let a fresh Claude Code session (or Josie) figure out which copy of a duplicated file is real, without re-running this whole audit.

## How to use this KB (for agents)
1. Read this index first. Pick notes by their descriptions, open only those.
2. `AUDIT_TABLE.md` (sibling to this file) has the flat one-table answer if you just need "which file is canonical" fast. The notes below are the atomic, linkable version of the same findings, for when you need the reasoning or a specific sub-question.
3. Cite the note `id` when you use information from it.
4. Nothing in this KB or the audit deletes, moves, or edits anything in `~/can-it-ford`, `~/can-it-ford-BACKUP-before-history-purge`, or `~/Documents/Claude/reu`. Every action recommended below is still pending a human decision.

## How to update this KB (for agents)
- New finding → new atomic note. Same finding changed → edit in place, bump `updated`.
- Any create/rename/delete MUST update this registry and the topic's `_topic.md` in the same change.
- Use only tags from the controlled vocabulary below; add a new tag here before using it.

## Controlled tags
`provenance`, `git`, `handoff`, `security`, `secrets`, `personal-content`, `structure`

## Registry

### provenance
- `20260724-claude-md` — **CLAUDE.md duplicate set** — `topics/provenance/claude-md.md` — 12 copies found; canonical is `~/can-it-ford/CLAUDE.md`, hash-matches GitHub `main` HEAD.
- `20260724-session-state` — **SESSION_STATE.md duplicate set** — `topics/provenance/session-state.md` — 7 copies; canonical is `~/can-it-ford/SESSION_STATE.md`.
- `20260724-resume-pane` — **resume_pane.sh duplicate set** — `topics/provenance/resume-pane.md` — 7 copies; canonical is `~/can-it-ford/scripts/resume_pane.sh`.
- `20260724-vehicle-reference` — **vehicle_data_master_reference_2026-07-21.json duplicate set** — `topics/provenance/vehicle-reference.md` — 8 copies, 4 genuinely different content versions, the highest-risk file in this audit.
- `20260724-embedded-repo` — **The embedded/orphaned nested repo incident** — `topics/provenance/embedded-repo-incident.md` — why `can-it-ford/can-it-ford/` exists and what GitHub's latest commit already did about it.
- `20260724-worktrees-backup` — **Worktrees and the pre-purge backup, structurally** — `topics/provenance/worktrees-and-backup.md` — what's legitimate vs. what's a stale snapshot.

### security
- `20260724-secrets-env` — **Secrets and .env files** — `topics/security/secrets-and-env.md` — WANDB/HF keys present but gitignored; unresolved prior-incident rotation status.
- `20260724-staged-inbox` — **Staged raw session exports in the backup repo** — `topics/security/staged-inbox-risk.md` — the live risk in this audit; three large files one `git commit` away from entering history.
- `20260724-personal-sweep` — **Personal/health content sweep result** — `topics/security/personal-content-sweep.md` — clean, with the false-positive rate documented so it doesn't need re-litigating.
- `20260724-outside-scope` — **Findings outside the four target directories** — `topics/security/outside-scope.md` — the `Health docs` grant and a stray grade-report backup, noticed en route, not acted on.
