---
id: 20260724-secrets-env
title: Secrets and .env files
tags: [security, secrets]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-staged-inbox]
summary: WANDB_API_KEY, HF_TOKEN, and hub_key exist in .env files in both the live repo and the backup, correctly gitignored and untracked; the prior WANDB-key-exposure incident's rotation status remains unconfirmed.
---

# Secrets and .env files

> Summary: not currently leaking, but one open question inherited from a documented prior incident.

## Findings
- `~/can-it-ford/.env` and `~/can-it-ford-BACKUP-before-history-purge/.env` both exist, holding `WANDB_API_KEY`, `HF_TOKEN`, and `hub_key`.
- Both are listed in their respective `.gitignore` (line 9 in both: `.env`) and confirmed untracked via `git ls-files` (empty result for `.env` in both repos). Not currently at risk.
- **Unresolved:** the project's own Known-Error Register notes a WANDB key was exposed in commit `50eff29`, with rotation "claimed but never confirmed." Commit `50eff29` could not be resolved as a git object in either the live repo or the backup's history from this session (`git cat-file -t 50eff29` → "Not a valid object name" in both). This may mean it was already scrubbed by an earlier rewrite, or the short hash doesn't resolve in this environment's view of the object database.
- Could not confirm from here whether the key currently in `.env` was ever rotated away from the historically-exposed value. Values were never compared or printed in this audit; only hashes would be compared if a source for the exposed value is located.

## Recommended human decision (not executed)
Check the WANDB key's issue/rotation date directly on wandb.ai rather than trusting the "claimed" note in CLAUDE.md's Known-Error Register.

## Related
- [Staged raw session exports in the backup repo](staged-inbox-risk.md) — the actual live risk found in this audit, a different mechanism than this one.
