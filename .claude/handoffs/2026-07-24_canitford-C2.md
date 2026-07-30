# Handoff, pane C2, canitford:0.2, 2026-07-24 evening

Companion to `AUDIT_TABLE_2026-07-24.md` at the repo root, which holds the reconciliation tables. This file is the flag list and the narrative.

Read-only audit. Nothing deleted, moved, renamed, or edited. No `git commit`, no `git push`. `settings.json` not touched, it belongs to C1. No simulation, no warpmpm import, no idev or GPU request. All remote work was login-node file inspection only.

## Blocking issue found at the start

**The `directory-provenance-audit` skill does not exist.** Verified live: `find /Users/josie -maxdepth 6 -iname "*directory-provenance*"` returns nothing, and a grep for the literal string finds it only inside past session `.jsonl` transcripts and inside the C2 mission file itself. The closest real skill is `provenance-audit`, present and byte-identical at both `~/.claude/skills/provenance-audit/SKILL.md` and `.claude/skills/provenance-audit/SKILL.md`, 217 lines.

The mission's two specific pointers into that skill do not map onto the real one:
- "the GitHub-blob-hash method the skill specifies" is not in `provenance-audit`. No such section exists.
- "sensitive-content sweep, skill Section 7" does not match. Section 7 of `provenance-audit` is CROSS-TOOL VERIFICATION PROMPT CONSTRUCTION, about Scite, Consensus and DeepWiki prompts. It has nothing to do with secret scanning.

This did not block the work, because PART 1, 2 and 3 are fully self-specified inside the mission file. I loaded the real `provenance-audit` skill, followed its Prime Directive and its Section 10 output format, and executed the mission's own instructions for the method. Flagging it because a future mission writer will reference the same non-existent skill again unless it is either created or the reference is corrected.

## Flag list

### FLAG 1, HIGH. A personal reference is live at current HEAD and on origin/main

`SESSION_STATE.md:65` at both `HEAD` and `origin/main` contains an ADHD reference. The working tree copy has 0 occurrences, but that removal is uncommitted, so it protects nothing. The same reference is reachable at `ca91b123a:SESSION_STATE.md:13`, `daf453e:SESSION_STATE.md:13`, and at four line positions in `_inbox/LIVE_SESSION_LOG.md` under commit `4db2789`, which is an ancestor of `origin/main`.

The repo was public until 2026-07-23. It is now `private=true` with `forks=0`, which bounds the exposure, but committing the current working tree will not remove it from pushed history.

Commit `0f35620e` is titled "Remove leaked personal CLAUDE.md copies and ADHD reference from tracking", so this was attempted once and did not clear history. Per the standing constraint, no wording is reproduced here or in the audit table, only paths and line numbers.

This is a decision for Josie, not for a pane. History rewriting is out of scope tonight and would collide with fourteen contexts and a push hold. Options, not executed: leave it (private repo, 0 forks, low residual risk), or schedule a `filter-repo` pass after the July 27 poster when the tree is quiet. The project CLAUDE.md already carries a `git filter-repo` standing note that applies.

### FLAG 2, MEDIUM. The mission's BACKUP premise is contradicted by live evidence

The mission states the BACKUP holds edits to `README.md`, `SESSION_STATE.md`, `paper_draft.md` and `vehicle_params.py` "that never landed in real history." All four landed. Each hashes byte-identical to the corresponding blob in `ca91b123a`, whose commit message says it recovered exactly those files from the pre-purge filesystem backup. `ca91b123a` is an ancestor of `origin/main`, so all of it is pushed.

Only three files in the BACKUP are genuinely unique, and they are pane scrollback exports, about 628KB to 645KB each, listed in the audit table. Because they are full tmux scrollbacks they are the single most likely place for an incidentally captured secret or personal string anywhere in this audit, and they have not been content-reviewed. **The BACKUP should not be deleted until those three are reviewed.** That review is a real task and is deferred, see the deferred list.

### FLAG 3, MEDIUM. Vista carries the same nested-repo pattern, roughly 2.9G

Not in the mission scope, found while checking PART 1 items 3 and 4.

- `/work/11603/jcerrell0629/vista/can-it-ford/can-it-ford`, 888M, git repo at `0b59eea9`, confirmed ancestor of `origin/main`, 0 dirty, 0 ignored, untracked and gitignored by the outer repo. Fully redundant, same situation as the Mac copy.
- `/work/11603/jcerrell0629/vista/can-it-ford-OLD-pre-purge`, 2.0G, separate repo at `0736dc3` with **11 dirty entries that were not checked for uniqueness**. Not cleared for removal.
- `/work/11603/jcerrell0629/vista/can-it-ford-OLD-pre-purge/can-it-ford`, a third nested copy.

The Vista nested copy is as safe to remove as the Mac one. The `OLD-pre-purge` tree is not, until its 11 dirty entries are checked.

### FLAG 4, MEDIUM. Two `.env` files with real secrets, world-readable, one outside all protection

`/Users/josie/can-it-ford/.env` and `/Users/josie/can-it-ford-BACKUP-before-history-purge/.env` are byte-identical, 270 bytes, mode `-rw-r--r--`, and hold `WANDB_API_KEY` and `HF_TOKEN`. Values were fingerprinted by hash and never printed.

The good news, verified: neither is tracked, the live one is ignored via `.gitignore:9`, and `git log --all -- '*.env'` shows no commit ever added one. This is a local filesystem permissions matter, not a repo exposure.

Suggested and NOT applied, since it is a file mutation and this audit is read-only: `chmod 600` on both. For C1 or a later session.

### FLAG 5, LOW. Mission's own state claims were stale within minutes

Three numbers in the mission were already wrong when I checked them live, which is worth recording because it is the recurring failure class this project keeps hitting:

| Mission claim | Live value |
|---|---|
| "Local main is 2 commits ahead of origin/main (af1db6d, 85e2252)" | 3 ahead at 22:4x, then **6 ahead** by 00:38. New commits `60a01a2`, `63e677f`, `9f5d82e` landed during the audit |
| "these twelve tmux panes" | **16 panes** across 4 sessions. `monitor` (3) and `panel_monitor` (1) are not accounted for |
| "The embedded nested repo ... previously frozen at ca91b123a" | Correct, confirmed exactly |

The commit count moving from 3 to 6 mid-audit confirms the designated committer is active. Nothing I did touched it.

### FLAG 6, LOW. PAT fingerprint confirmed exactly as described

`token_setup_template.md:14`, tracked. The token-shaped string is 17 characters total, `github_pat_` plus 6, so it is a fingerprint and not a usable credential. Present in 4 commits (`3e9ff8c`, `ee82867`, `fd307d2`, `4db2789`) and in 4 additional worktree or handoff copies, all hashing to the same fingerprint. Confirmed live, no action needed beyond awareness. Zero hits for every other credential pattern tested.

### FLAG 7, INFORMATIONAL. `resume_pane.sh` was not re-audited

The mission listed it under "already resolved" and asked for live verification of non-Vista handling. I deprioritized it in favor of the four PART 1 paths, PART 2 and PART 3, all of which were explicitly assigned. It remains unverified by me. Stating that rather than implying coverage.

## Decision on the existing audit artifact

The mission asked me to say which I chose. **I extended, I did not supersede.**

`HANDOFF_AUDIT_2026-07-24/AUDIT_TABLE.md` (2026-07-23 20:21, 14,160 bytes) is Mac-local duplicate-file reconciliation. Tested live: `grep -ci 'vista|ls6|/work/11603|home1'` against it returns **0**. It has no remote coverage at all, so there is nothing in it for me to overwrite or contradict. My `AUDIT_TABLE_2026-07-24.md` adds the four PART 1 paths, both remote machines, the pane cwd confirmation and the sensitive sweep, and it cross-references the older file rather than re-deriving its tables. Two complementary files, not a third overlapping one.

While checking it I confirmed the duplication the mission mentioned, and it is worse than described:

| Item | Finding |
|---|---|
| `handoff_kb 2/topics/` vs `topics/` | Byte-identical trees, `diff -rq` clean apart from one `.DS_Store`. 321 lines duplicated across 14 files |
| `AUDIT_TABLE copy.md` vs `AUDIT_TABLE.md` | Byte-identical, 14,160 bytes each |
| `handoff_kb/` | Completely empty directory |
| `can-it-ford-HANDOFF-AUDIT-2026-07-24.zip` | 21,360 bytes, mode `-rw-------`, a zip of the same content, duplicated again at `_inbox/can-it-ford-HANDOFF-AUDIT-2026-07-24.zip` |

Not cleaned up, per hard constraint 1. Flagged for a later session.

## For C1 specifically

Two items imply a `settings.json` change. I did not touch the file.

1. The deny rules cannot cover `/Users/josie/can-it-ford-BACKUP-before-history-purge` because it is outside the project root. PART 2 shows no pane is currently sitting there, so the immediate risk is not live, but cwd only bounds relative paths and any pane can still reach it absolutely. If a deny rule can be written against the absolute path, it is worth adding.
2. The same applies to the `.env` at the BACKUP path.

## Deferred and optional

Filtered against tonight's three anchors: poster July 27, paper July 31, one verified rendered physically plausible MPM simulation with a vehicle.

**Serves an anchor, worth doing:**
- Review the three unique BACKUP scrollback exports for captured secrets or personal strings, then archive or discard deliberately. Serves the exposure-cleanup thread that FLAG 1 opens. Roughly 1.9MB of text, needs a targeted grep rather than a full read.

**Does not serve an anchor, deferred:**
- Removing the Mac nested clone, 887M. Shown, not run. Pure disk hygiene.
- Removing the Vista nested clone, 888M. Same.
- Auditing `can-it-ford-OLD-pre-purge` on Vista, 2.0G with 11 unchecked dirty entries.
- Deduplicating `HANDOFF_AUDIT_2026-07-24/`.
- `chmod 600` on both `.env` files.
- Verifying `resume_pane.sh` non-Vista handling, FLAG 7.
- Any history rewrite for FLAG 1. Explicitly should NOT happen before July 27, it would collide with the shared tree and the push hold.

Per the mission's instruction not to invent work, I stopped here rather than starting any of the deferred items.
