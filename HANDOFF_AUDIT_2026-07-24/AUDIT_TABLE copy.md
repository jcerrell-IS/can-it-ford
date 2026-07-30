# Can It Ford — Directory Provenance Audit
**Date:** 2026-07-24 | **Method:** git blob hash vs GitHub canonical (not mtime, not size) | **Deletions performed:** none

## Canonical reference point

Repo: `jcerrell-IS/can-it-ford` (private), branch `main`, current HEAD `daf453e2d` (2026-07-24T00:01:44Z, "Remove accidentally-committed embedded git repository, add to gitignore").

That commit message matters: it means an embedded/nested repo copy was *just* untracked on GitHub's side. The nested folder still physically exists on disk in two places below — this audit treats it as the direct evidence of that exact incident.

Canonical blob hashes pulled live from the GitHub API (not `git ls-remote`, which only gives you a ref hash, not per-file hashes):

| File | Canonical path in repo | Canonical blob hash |
|---|---|---|
| `CLAUDE.md` | `CLAUDE.md` | `ebf2b5ad0510caca5f9a932819ceedba876af334` |
| `SESSION_STATE.md` | `SESSION_STATE.md` | `6b21ab3413b67f068f526764c007d6a6fb8fcc7a` |
| `resume_pane.sh` | `scripts/resume_pane.sh` | `44c8aa7313728974ddfec8d445abbb1907d7fc87` |
| `vehicle_data_master_reference_2026-07-21.json` | `reference_data/vehicle_data_master_reference_2026-07-21.json` | `9608d43c98a9c06c0a39303fa3589adfd4dd1875` |

Every local copy below was hashed with `git hash-object` (works with or without a `.git` folder) and compared directly against these. Two files with the same hash are byte-identical, full stop, regardless of what the timestamps say.

**Important preliminary finding:** `~/Claude/reu` and `~/Documents/Claude/reu` are not two directories. `diff` on their full listings came back identical — they're the same physical folder granted to this session under two different names. There is no separate top-level `~/Claude`; treat every "Claude/reu" reference below as one location.

---

## 1. Duplicate-file table

### CLAUDE.md

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/CLAUDE.md` | **YES** | Matches canonical hash exactly. Live main-branch working copy. |
| `~/can-it-ford/can-it-ford/CLAUDE.md` | No | Content happens to match canonical text, but this file lives inside the embedded/orphaned nested repo (see §2) that GitHub's latest commit just untracked. Orphaned duplicate — the folder itself shouldn't exist. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/CLAUDE.md` | No | Different hash — this worktree is checked out on an older/different commit. Expected for an active worktree branch, not a bug, but not canonical. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/CLAUDE.md` | Effectively yes | Hash matches canonical. Worktree branch currently in sync with `main`. |
| `~/can-it-ford-BACKUP-before-history-purge/CLAUDE.md` | No | Stale pre-purge snapshot (frozen ~2026-07-23 12:50, before 11+ additional commits landed on `main`). |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/CLAUDE.md` | No | Same stale hash as above — redundant nested copy inside the backup, mirroring the same embedded-repo pattern found in the live checkout. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/CLAUDE.md` | No | Same stale hash again — triple-nested redundant copy. |
| `~/Desktop/CLAUDE.md` | No | Completely different content (1,344 bytes, last touched April 6). Not this repo at all — orphaned leftover from an earlier/different setup. |
| `~/Documents/Claude/reu/CLAUDE.md` (= `~/Claude/reu/CLAUDE.md`) | No | Different project entirely — this is the REU/session-instructions doc for Claude sessions broadly, not the git repo's file. Shares a filename, not a lineage. |
| `~/Documents/Claude/Projects/SCIENCE ENTIRETY/CLAUDE.md` | No | Empty file (0 bytes). Different project entirely, unused placeholder. |
| `~/Documents/Claude/Projects/SCIPE UT Austin baby/REU_Knowledge/newton/CLAUDE.md` | No | 11 bytes. Different project entirely — a stub inside the Newton-physics reference notes, unrelated to the repo. |
| `~/Documents - Josephine's MacBook Air/Claude/CLAUDE.md` | No | Different content (5,034 bytes, last touched July 3). Looks like a stale duplicate from an old Mac profile/migration ("Josephine's MacBook Air" vs the active "Josie's MacBook Air"), not the live working copy. |

### SESSION_STATE.md

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/SESSION_STATE.md` | **YES** | Matches canonical hash. |
| `~/can-it-ford/can-it-ford/SESSION_STATE.md` | No | Orphaned duplicate inside the embedded/nested repo. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/SESSION_STATE.md` | No | Different-branch worktree copy. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/SESSION_STATE.md` | Effectively yes | Hash matches canonical. |
| `~/can-it-ford-BACKUP-before-history-purge/SESSION_STATE.md` | No | Stale pre-purge backup. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/SESSION_STATE.md` | No | Redundant nested copy inside the backup. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/SESSION_STATE.md` | No | Redundant nested worktree copy inside the backup. |

*(Note: GitHub itself already archived one prior conflict copy — `archive/superseded_docs/SESSION_STATE.md.bak_before_conflict_resolve` — evidence the KILL-list-then-archive pattern has been used correctly before.)*

### resume_pane.sh

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/scripts/resume_pane.sh` | **YES** | Matches canonical hash. |
| `~/can-it-ford/can-it-ford/scripts/resume_pane.sh` | No | Older version, orphaned inside the embedded repo. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/scripts/resume_pane.sh` | No | Same older hash as the embedded-repo copy — different-branch worktree, not yet rebased onto the latest script. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/scripts/resume_pane.sh` | Effectively yes | Hash matches canonical. |
| `~/can-it-ford-BACKUP-before-history-purge/scripts/resume_pane.sh` | No | Stale pre-purge backup, older version. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/scripts/resume_pane.sh` | No | Redundant nested copy. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/scripts/resume_pane.sh` | No | Redundant nested worktree copy. |

### vehicle_data_master_reference_2026-07-21.json

**This is the one that actually matters — there are four genuinely different versions of this file on disk, not just stale copies of one.**

| Path | Canonical? | Reasoning |
|---|---|---|
| `~/can-it-ford/reference_data/vehicle_data_master_reference_2026-07-21.json` | **YES** | Matches canonical hash. |
| `~/can-it-ford/can-it-ford/vehicle_geometry_research/vehicle_data_master_reference_2026-07-21.json` | No | Different content AND different path (`vehicle_geometry_research/` is a superseded location, `reference_data/` is where it lives now). This is the pre-move version, orphaned inside the embedded repo. |
| `~/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/reference_data/vehicle_data_master_reference_2026-07-21.json` | No | Yet another distinct hash — this is the in-progress WIP version on the branch literally named for reconciling this file. Not old, not new, actively mid-edit. |
| `~/can-it-ford/.claude/worktrees/physics-params-audit-541e4f/reference_data/vehicle_data_master_reference_2026-07-21.json` | Effectively yes | Hash matches canonical. |
| `~/can-it-ford-BACKUP-before-history-purge/reference_data/vehicle_data_master_reference_2026-07-21.json` | No | A fourth distinct hash — oldest version captured in the pre-purge snapshot. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/vehicle_geometry_research/vehicle_data_master_reference_2026-07-21.json` | No | Same hash as the embedded-repo's old-path copy — redundant. |
| `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/.claude/worktrees/reconcile-vehicle-master-ref/reference_data/vehicle_data_master_reference_2026-07-21.json` | No | Same hash as the WIP-branch copy — redundant. |
| `~/Downloads/vehicle_data_master_reference_2026-07-21.json` | No | Same hash as the oldest backup version (mtime July 21) — an orphaned loose export in Downloads, matches the oldest of the four versions. |

**Bottom line:** before any script reads this file by a bare filename search, confirm which path it's pulling from. `reference_data/` in the live `~/can-it-ford` root is the only one that matches GitHub `main` right now.

---

## 2. What's actually going on structurally (context for the table above)

- **Embedded/orphaned nested repo:** `~/can-it-ford/can-it-ford/` is a full separate git checkout (its own `.git`, HEAD `ca91b123a`, tracking the same GitHub remote but frozen at an older commit) sitting inside the real repo. GitHub's most recent commit (`daf453e2d`, today) is titled "Remove accidentally-committed embedded git repository, add to gitignore" — this folder is that exact incident's leftover. It's now gitignored on the canonical side but still physically present. Same structure is duplicated again inside the backup at `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/`.
- **Worktrees are legitimate**, confirmed via their `.git` files pointing to real `gitdir` entries (`/Users/josie/can-it-ford/.git/worktrees/reconcile-vehicle-master-ref` and `/physics-params-audit-541e4f`). I couldn't run `git status` on them directly from this sandboxed view (the mount boundary can't resolve that absolute path), so branch/dirty-state should be double-checked directly in Terminal on the Mac if precision matters there — but content-hash comparison above is unaffected by that limitation.
- **The backup is genuinely a backup**, not a duplicate project: same remote, older HEAD (`0f35620e7`, 190 commits vs. live's 201), with its own uncommitted local edits (README.md, SESSION_STATE.md, `data/track1_sweep_v2/mpm_sweep_data_schema.md`, `paper_draft.md`, `vehicle_params.py`) that never made it into the real history. Treat it as a frozen safety snapshot, not a second live copy.

---

## 3. Sensitive / personal / secret content flags

**No genuine personal or health content found** in `~/can-it-ford`, the backup, or `~/Documents/Claude/reu`. I grepped all three for therapy/medication/mental-health/SSN-shaped keywords; every hit (183 total across the big session-log exports) traced to the word **"diagnostic/diagnose"** in an engineering-debugging context — zero real hits on therapist, medication, prescription, mental health, panic attack, or SSN patterns. I sampled-verified this rather than taking the raw grep count at face value, since "diagnos-" is exactly the kind of false positive that would otherwise get over-reported.

Real findings, ranked by what needs action:

1. **`.env` files exist in both `~/can-it-ford/.env` and `~/can-it-ford-BACKUP-before-history-purge/.env`**, holding `WANDB_API_KEY`, `HF_TOKEN`, and `hub_key`. Both are correctly listed in `.gitignore` and confirmed untracked (`git ls-files` returns nothing for either) — not currently leaking. Flagging anyway because this is the exact category of the prior incident.
2. **Unconfirmed rotation status on the prior incident itself.** Your own CLAUDE.md Known-Error Register notes a WANDB key was exposed in commit `50eff29` and rotation was "claimed but never confirmed." I couldn't resolve `50eff29` as an object in either the live repo or the backup's git history from this session — it may have already been scrubbed by an earlier rewrite, or the short hash doesn't resolve from this environment. I can't confirm from here whether the key currently sitting in `.env` was ever rotated away from that exposed value. Recommend checking the key's issue date directly on wandb.ai rather than trusting the "claimed" rotation.
3. **Staged-for-commit risk in the backup repo:** `git status` on `~/can-it-ford-BACKUP-before-history-purge` shows `_inbox/export_canitford_0_0_20260723_054340.md`, `..._5_5_20260723_054343.md`, and `..._5_5_20260723_054351.md` as **staged additions** (`A`, not just untracked) — these are raw session-transcript exports, 600+KB each. `_inbox/LIVE_SESSION_LOG.md` itself (2.4MB) is correctly `.gitignore`d and not at risk, but the three staged exports are not covered by the same gitignore rule and are one `git commit` away from landing in history. This is precisely the mechanism the project has already had one incident from. Nothing in them was personal (verified — pure "diagnostic" false positives), but the pattern (raw, unreviewed session dumps entering the index) is the actual risk, not this specific content.
4. **Loosely-organized, outside the four target directories but noticed en route:** a folder literally named `Health docs` is granted to this Cowork session at the home-directory level. I did not open it (empty top-level listing, 0 items currently — nothing to read), but its existence as a granted folder is worth a conscious decision on your end: revoke access if Cowork doesn't need it, rather than leaving it granted by default. Separately, `~/Documents - Josie's MacBook Air - 1/` (one of three overlapping "Documents" folders from what looks like old Mac migrations) contains actual grade-report PDFs (report cards, semester summaries) sitting loose — not part of this project, but a real educational record sitting in an unstructured backup folder.

---

## 4. Not touched

Per instructions, nothing was deleted, moved, or modified. Every row above is a report-only finding. Recommended next human decisions (not executed):
- Delete the two orphaned embedded `can-it-ford/can-it-ford/` nested repos.
- Decide which `vehicle_data_master_reference_2026-07-21.json` version is actually correct and reconcile the `reconcile-vehicle-master-ref` worktree before merging it.
- Unstage (or explicitly `.gitignore`) the three `_inbox/export_canitford_*.md` files in the backup before any commit runs there.
- Confirm WANDB key rotation directly on wandb.ai.
- Review whether Cowork still needs access to `Health docs`.
