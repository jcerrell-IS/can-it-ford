# Directory and path reconciliation table, 2026-07-24 evening

Pane C2, canitford:0.2. Read-only audit. Nothing was deleted, moved, renamed, or edited. No commit, no push.

**Relationship to the existing artifact:** this file EXTENDS `HANDOFF_AUDIT_2026-07-24/AUDIT_TABLE.md` (written 2026-07-23 20:21). It does not supersede or replace it. That file is Mac-local duplicate-file reconciliation and contains zero coverage of the remote paths (`grep -ci 'vista|ls6|/work/11603|home1'` returns 0 against it). This file adds the four PART 1 paths, the remote machines, the pane working-directory confirmation, and the sensitive-content sweep. Read both. The older file's Mac duplicate tables are not re-derived here.

## Method

Per the mission: GitHub blob hash, not mtime and not file size. Canonical HEAD pulled live from the GitHub API, every local copy hashed with `git hash-object`, compared directly. Where a whole tree was involved, the stronger test was used: a clean worktree at a known commit SHA is cryptographic proof of tree identity, so `git --no-optional-locks status --porcelain` against a verified commit SHA replaces per-file hashing. `--no-optional-locks` was used throughout so no index was written in any repo, since fourteen contexts share this tree.

Canonical reference pulled live 2026-07-25 00:38 CDT:

| Item | Value |
|---|---|
| GitHub `repos/jcerrell-IS/can-it-ford` HEAD of `main` | `8e12e84d811bdd4acb26b7deb4d4dd09fdf3166d` |
| GitHub HEAD message | add node access reference |
| Repo visibility now | `private=true`, `forks=0` |
| Local `origin/main` | `8e12e84`, matches GitHub exactly |

## PART 1, path reconciliation

| # | Path | Exists? | What it actually is | Unique content at risk | Verdict |
|---|---|---|---|---|---|
| 1 | `/Users/josie/can-it-ford/can-it-ford` | YES | Full `git clone` of the same origin, reflog line is `clone: from https://github.com/jcerrell-IS/can-it-ford.git`. Worktree HEAD `ca91b123ae72f681a1c4cda1f04931a8a0dad82e`, confirmed an ancestor of `origin/main`. 887M total, 480M worktree plus 407M `.git`. Untracked by the outer repo (0 tracked paths) and ignored via `.gitignore:47`. | NONE | REDUNDANT, safe to remove, not removed |
| 2 | `/Users/josie/can-it-ford-BACKUP-before-history-purge` | YES | Real git repo, HEAD `0f35620e` (2026-07-23 06:59). 9 dirty entries: 5 staged modifications and 3 staged adds, plus its own untracked nested `can-it-ford/`. | 3 files only, see below | PARTIALLY REDUNDANT, do not delete yet |
| 3 | `/home1/11603/jcerrell0629/can-it-ford` on Vista | NO | Does not exist. Confirmed independently from Vista and from LS6. | n/a | RESOLVED, already gone |
| 4 | `/work/11603/jcerrell0629/ls6/can-it-ford` | NO | The `ls6` parent directory exists (`drwx------`, 2026-07-23 13:00) but contains only `datasets`. There is no `can-it-ford` under it. Confirmed from both machines; `/work` is shared Stockyard so both see the same tree. | n/a | RESOLVED, the two docs that disagreed are both stale; the correct answer is it does not exist |
| 5 | `/work/11603/jcerrell0629/vista/can-it-ford` | YES | The canonical Vista working repo, HEAD `8e12e84` matching `origin/main`. 9 dirty entries including a modified `simulation/can_it_ford_L2_mpm.py`. | live working state, leave alone | CANONICAL, do not touch |

### Item 1 detail, the embedded nested repo

The mission's expectation is confirmed exactly. `daf453e` ("Remove accidentally-committed embedded git repository, add to gitignore") is a genuine ancestor of both local `main` and `origin/main`, verified with `git merge-base --is-ancestor`. The gitlink is gone. What remains is only an untracked leftover directory, which is the lower-stakes situation the mission anticipated.

Content-safety proof, all four conditions met:

| Check | Result |
|---|---|
| Modified tracked files in nested worktree | 0 |
| Deleted tracked files | 1, `.claude/skills/bug-triage-protocol_SKILL.md`, recoverable from its own HEAD |
| Untracked files | 2 dirs, `bug-triage-protocol/` and `panel-audit-dispatch/`, both `SKILL.md` byte-identical to the live outer copies per `diff -rq` |
| Ignored files, invisible to plain `git status` | 3, all `.DS_Store` |
| Nested HEAD reachable from `origin/main` | YES, `ca91b123a` is an ancestor and is pushed to GitHub |

Spot-check with the prescribed method, nested worktree file against the outer repo's blob at `ca91b123a`:

| File | Nested worktree hash | Outer `ca91b123a` blob | Match |
|---|---|---|---|
| `CLAUDE.md` | `ebf2b5ad0510caca5f9a932819ceedba876af334` | same | IDENTICAL |
| `README.md` | `084258434321c948c300f9d354e65e8bd61186ae` | same | IDENTICAL |
| `SESSION_STATE.md` | `ae69e46d273b620e295781cb284a89f98e2f624c` | same | IDENTICAL |
| `vehicle_params.py` | `116002dc2a73224a5b66f3e2b85fc3f29ba963b2` | same | IDENTICAL |
| `LICENSE` | `6a4750cd32a9a59418f341ccadc8424ab6c8e0e4` | same | IDENTICAL |
| `PROVISIONAL_STATUS.md` | `8c2b928b8987ad829f1b1d72b1a8f93643c45df7` | same | IDENTICAL |

Condition satisfied, so per the mission the removal is SHOWN and STOPPED.

**SHOW ONLY. This command was NOT run, NOT staged, NOT executed.**

```
rm -rf /Users/josie/can-it-ford/can-it-ford
```

Would destroy 887M, 411 files (383 excluding `.git`), 78 directories. Top-level entries: `.DS_Store`, `.claude`, `.git`, `.gitattributes`, `.github`, `.gitignore`, `ARCHIVE_INDEX.md`, `CITATION.cff`, `CLAUDE.md`, `Instructions.docx.md`, `KICKOFF_PROMPT.md`, `LICENSE`, `PROJECT_FILE_MAP.md`, `PROVISIONAL_STATUS.md`, `README.md`, `REBUILD_REFERENCE.md`, `SESSION_STATE.md`, `_inbox`, `analysis`, `archive`, `assets`, `bridge`, `can_it_ford_phase_space_v2.png`, `can_it_ford_validation.png`, `check_dois_crossref.py`, `citations`, `crash_trace_july21.txt`, `crash_trace_july22_waterbox_fix.txt`, `crash_trace_july23.txt`, `data`, `designsafe-staging`, `docs`, `environment.yml`, `figures`, `files`, `full_scale_test.py`, `hf_space`, `kumar_july9_update`, `logs`, `out`, `paper`, `paper_draft.md`, 9 `particles_*.npz`, `phase_space_results_mpm.csv`, `phase_space_results_v2.csv`, `poster_text_draft.md`, `reference_data`, `render_frames.py`, `render_hero_shot.py`, `renders`, `scripts`, `simulation`, 3 `simulation_*.mp4`, `tests`, `vehicle_geometry_research`, `vehicle_params.py`, `viability_audit_results.csv`, `wandb_backfill.py`.

Every byte of that is recoverable from `origin/main` history on GitHub, except 3 `.DS_Store` files which are junk.

### Item 2 detail, the BACKUP directory

**The mission's premise on this one is CONTRADICTED by live evidence.** The mission states the BACKUP holds edits to `README.md`, `SESSION_STATE.md`, `paper_draft.md` and `vehicle_params.py` "that never landed in real history." All four did land. Every one of the five staged modifications hashes byte-identical to the corresponding blob in commit `ca91b123a`, whose message is "Recover README/SESSION_STATE/schema/paper_draft edits lost in filter-repo rewrite, restored from pre-purge filesystem backup." The recovery already happened, and it was restored from this exact backup.

| BACKUP file | Blob hash | Identical to `ca91b123a` blob? | In outer history? |
|---|---|---|---|
| `README.md` | `084258434321c948c300f9d354e65e8bd61186ae` | YES | YES |
| `SESSION_STATE.md` | `ae69e46d273b620e295781cb284a89f98e2f624c` | YES | YES |
| `paper_draft.md` | `9f3536adc39e3d361c162aceba1add9585ee2168` | YES | YES |
| `vehicle_params.py` | `116002dc2a73224a5b66f3e2b85fc3f29ba963b2` | YES | YES |
| `data/track1_sweep_v2/mpm_sweep_data_schema.md` | `9cd27dcc38398b3eeb2c14f44a6a330c73df3f98` | YES | YES |

`ca91b123a` is an ancestor of `origin/main`, so all five are pushed and safe on GitHub.

The only genuinely unique content in the BACKUP is three staged tmux scrollback exports whose blobs do not exist anywhere in the outer object database:

| File | Size | Status |
|---|---|---|
| `_inbox/export_canitford_0_0_20260723_054340.md` | 628,187 bytes | UNIQUE to backup |
| `_inbox/export_canitford_5_5_20260723_054343.md` | 645,418 bytes | UNIQUE to backup |
| `_inbox/export_canitford_5_5_20260723_054351.md` | 645,342 bytes | UNIQUE to backup |

The two `5_5` exports are near-duplicates but not identical, they first differ at byte 24,835. None of the three exist anywhere under the project root. They are full pane scrollbacks, so they are the highest-probability location for incidentally captured secrets or personal content in this entire audit. Do not delete the BACKUP until these three are reviewed and either archived or discarded deliberately.

### New finding not in the mission scope, Vista carries the same nested-repo pattern

| Path | Size | State |
|---|---|---|
| `/work/11603/jcerrell0629/vista/can-it-ford/can-it-ford` | 888M | Git repo at `0b59eea9`, confirmed ancestor of `origin/main`. 0 dirty, 0 ignored. Untracked and ignored by the outer repo via the same `.gitignore:47`. Fully redundant. |
| `/work/11603/jcerrell0629/vista/can-it-ford-OLD-pre-purge` | 2.0G | Separate git repo, HEAD `0736dc3` (2026-07-23 06:00), 11 dirty entries. Not audited for unique content. |
| `/work/11603/jcerrell0629/vista/can-it-ford-OLD-pre-purge/can-it-ford` | included above | A third nested copy. |
| `/work/11603/jcerrell0629/vista/can-it-ford-claude-sessions-2026-07-23.tar.gz` | not measured | Session archive tarball. |

Roughly 2.9G of redundant copies sit on Vista `$WORK`. The Vista nested copy is as safe to remove as the Mac one. The `OLD-pre-purge` tree has 11 uncommitted entries that were NOT checked for uniqueness, so it is not cleared for removal by this audit.

## PART 2, working-directory confirmation

`tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_path}'`, run live.

**16 panes across 4 sessions, not the 12 the mission assumes.** Two additional sessions exist, `monitor` (3 panes) and `panel_monitor` (1 pane).

| Session | Panes | cwd | Outside project root? |
|---|---|---|---|
| `canitford:0.0` to `0.5` | 6 | `/Users/josie/can-it-ford` | No |
| `ford:0.0` to `0.5` | 6 | `/Users/josie/can-it-ford` | No |
| `monitor:0.0` | 1 | `/Users/josie/can-it-ford` | No |
| `monitor:0.1`, `monitor:0.2` | 2 | `/Users/josie/can-it-ford/paper` | Not exactly the root, but inside it |
| `panel_monitor:0.0` | 1 | `/Users/josie/can-it-ford` | No |

**Zero panes have a cwd outside `/Users/josie/can-it-ford`.** No pane is sitting in the BACKUP directory. The two `monitor` panes in `paper/` are inside the project root, so a relative-path `rm` from either still cannot reach the BACKUP. The specific risk the mission was guarding against is not currently live.

Caveat, stated because it was not verified: cwd only bounds relative paths. Any pane can still reach the BACKUP with an absolute path, and the deny rules in `settings.json` cannot cover it because it is outside the project root.

## PART 3, sensitive-content sweep

Per the standing constraint, locations and classifications only. No personal or health content and no credential value is reproduced anywhere in this file.

### Credential-shaped strings

| Pattern | Hits in project root (nested clone excluded) |
|---|---|
| `AKIA[0-9A-Z]{16}` | 0 |
| `sk-ant-[A-Za-z0-9_-]{20,}` | 0 |
| `ghp_[A-Za-z0-9]{36}` | 0 |
| `gho_[A-Za-z0-9]{36}` | 0 |
| `hf_[A-Za-z0-9]{34}` | 0 |
| `BEGIN [A-Z ]*PRIVATE KEY` | 0 |
| 40-hex W&B-key-shaped in tracked `.md`/`.py`/`.sh` | 0 |

No usable live credential is present in tracked project files.

### The PAT fingerprint, confirmed live

| Question | Answer |
|---|---|
| Still in the tracked file? | YES, `token_setup_template.md:14`, tracked |
| Length of the token-shaped string | 17 chars total, that is `github_pat_` plus 6 characters |
| Usable as a credential? | NO. A real GitHub fine-grained PAT is far longer. This is a fingerprint, not a secret |
| In git history? | YES, 4 commits: `3e9ff8c`, `ee82867`, `fd307d2`, `4db2789` |
| Other copies in the worktree | `.claude/worktrees/physics-params-audit-541e4f/token_setup_template.md:14`, `.claude/worktrees/eloquent-easley-3ca1ff/token_setup_template.md:14`, plus 2 handoff docs |

All five copies hash to the same fingerprint, `sha256(first16)=06cb3e234d009da2`. Confirmed exactly as the mission described.

### Live `.env` files, real secrets, not committed

| Path | Contents | Tracked? | In history? |
|---|---|---|---|
| `/Users/josie/can-it-ford/.env` | 2 variables, `WANDB_API_KEY` and `HF_TOKEN` | NO, ignored via `.gitignore:9` | NO, never committed |
| `/Users/josie/can-it-ford-BACKUP-before-history-purge/.env` | byte-identical to the above | NO | NO |

Both files are mode `-rw-r--r--`, world-readable on disk. Values were fingerprinted by hash and never printed. The good news is these were never committed and never public. The BACKUP copy sits outside every deny rule.

### Personal and health keyword sweep

| Term | Tracked files hit | Classification |
|---|---|---|
| `therapy`, `medication`, `prescription`, `disability`, `accommodation`, `anxiety`, `depression`, `psychiatr` | 0 | no hits |
| `diagnos` | 34 | FALSE POSITIVE, domain vocabulary. Sampled `CLAUDE.md`, `TACC_NODE_ACCESS.md`, `data/track1_sweep_v2/mpm_sweep_data_schema.md`, all engineering usage. This is exactly the false-positive class the mission warned about |
| `insurance` | 1 | FALSE POSITIVE, `vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md:170`, quoted crashworthiness FEM literature |
| `ADHD` | see below | MIXED, one false positive and one true positive |

**ADHD, false positive:** `figures/phase_space_interactive.html`. A case-insensitive grep hits twice, but the case-sensitive count of `ADHD` is **0**. Both hits are lowercase or mixed-case substrings inside base64 payload in a 4.9MB plotly figure with 20 `bdata`/`base64`/`dtype` markers. Not personal content. No action.

**ADHD, TRUE POSITIVE, and it is live:**

| Location | Line | Tracked / reachable |
|---|---|---|
| `SESSION_STATE.md` working tree copy | n/a, 0 occurrences | removal is uncommitted only |
| `SESSION_STATE.md` at `HEAD` | 65 | TRACKED at current HEAD |
| `SESSION_STATE.md` at `origin/main` | 65 | PUSHED to GitHub |
| `SESSION_STATE.md` at `ca91b123a` | 13 | reachable in history |
| `SESSION_STATE.md` at `daf453e` | 13 | reachable in history |
| `_inbox/LIVE_SESSION_LOG.md` at `4db2789` | 87967, 87976, 123951, 123960 | file untracked at HEAD, but `4db2789` is an ancestor of `origin/main`, so content persists in history |
| `.claude/worktrees/physics-params-audit-541e4f/SESSION_STATE.md` | 13 | worktree checkout |
| `.claude/worktrees/eloquent-easley-3ca1ff/SESSION_STATE.md` | 13 | worktree checkout |
| `.claude/handoffs/2026-07-24_ARCHIVE_session-state-pre-restructure.md` | 91 | untracked |

The working tree no longer contains it, but that removal is **uncommitted**, so `HEAD` and `origin/main` both still carry it at `SESSION_STATE.md:65`. The repo was public until 2026-07-23. It is `private=true` with `forks=0` now, which bounds the blast radius, but the content is still reachable in pushed history and a commit of the current working tree would not remove it from history.

Note that commit `0f35620e` in the BACKUP repo is titled "Remove leaked personal CLAUDE.md copies and ADHD reference from tracking", so a removal was attempted once. It did not clear history, and the reference is present at current HEAD.
