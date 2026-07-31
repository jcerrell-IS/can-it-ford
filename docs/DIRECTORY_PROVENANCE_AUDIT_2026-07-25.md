# Directory Provenance Audit — 2026-07-25

Scope: the granted `can-it-ford` folder plus every duplicate-tree location found inside it —
the nested independent clone `can-it-ford/can-it-ford`, and the three linked git worktrees
under `.claude/worktrees/`. Canonical reference is the live GitHub tip of
`jcerrell-IS/can-it-ford` main, confirmed via the GitHub API (`list_commits`, `get_file_contents`)
at commit `b00bf7b6f24097c3779be2952ea8b96437ca697c`, cross-checked against local `git
hash-object` blob hashes. Never trusted mtime or file size as the deciding signal.

**Important caveat on method:** this sandbox cannot authenticate to `github.com` for a live
`git fetch` (no credentials), so blob comparisons for most files rely on each repo's locally
*cached* `origin/main` ref rather than a fresh pull. The outer repo's cache was spot-verified
against the live GitHub API for `CLAUDE.md` and matched exactly, and its cached tip commit
(`b00bf7b`) matches the API's live `list_commits` result exactly — so its cache is currently
trustworthy. The nested clone's cache is NOT current (see flag below) — treat its self-reported
"pushed" status as unreliable until it does a real `git fetch`.

## Locations swept

| # | Location | Type | HEAD |
|---|---|---|---|
| 1 | `can-it-ford/` (granted root) | canonical working repo | `d43081a` (1 ahead of origin/main, unpushed) |
| 2 | `can-it-ford/can-it-ford/` | independent clone, own `.git`, same `origin` URL | `ca91b123` |
| 3 | `.claude/worktrees/eloquent-easley-3ca1ff/` | linked git worktree (shares object store with #1) | `daf453e`, detached HEAD |
| 4 | `.claude/worktrees/physics-params-audit-541e4f/` | linked git worktree | `daf453e`, branch `claude/physics-params-audit-541e4f` |
| 5 | `.claude/worktrees/reconcile-vehicle-master-ref/` | linked git worktree | `761ff84`, branch `worktree-reconcile-vehicle-master-ref` |

All three worktrees (#3–5) report `prunable` under `git worktree list`, which can be a
mount-path artifact of this audit's sandbox rather than a real problem on Josie's actual Mac —
worth a `git worktree repair` check locally rather than trusting this audit's read on that
point alone.

## Provenance table

Canonical column = the live GitHub blob hash at `b00bf7b`.

| File | Canonical? | #1 outer | #2 nested clone | #3 eloquent-easley | #4 physics-params-audit | #5 reconcile-vehicle-master-ref |
|---|---|---|---|---|---|---|
| `CLAUDE.md` | `56f258c…` | ✅ match | ❌ `ebf2b5a…` | ❌ `ebf2b5a…` | ❌ `ebf2b5a…` | ❌ `aab2fd2…` |
| `SESSION_STATE.md` | `ccdaf4e…` | ⚠️ `69aeb89…` (newer, unpushed — see note) | ❌ `ae69e46…` | ❌ `6b21ab3…` | ❌ `6b21ab3…` | ❌ `4cd4dfc…` |
| `README.md` | `1bce3f2…` | ⚠️ HEAD matches canonical; working tree has an **uncommitted** edit (`bf8053e…`) | ❌ `0842584…` | ❌ `0842584…` | ❌ `0842584…` | ❌ `7835328…` |
| `paper_draft.md` | `9f3536a…` | ✅ match | ✅ match | ✅ match | ✅ match | ❌ `0dbacb6…` |
| `vehicle_params.py` | `15e3126…` | ✅ match | ❌ `116002d…` | ❌ `116002d…` | ❌ `116002d…` | ❌ `b4d8007…` |
| `docs/VERIFIED_FACTS_LEDGER_july24.md` | `3c72eeb…` | ✅ match | **absent** | **absent** | **absent** | **absent** |
| `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` (canonical mesh) | `46a9f73…` | ✅ match | ✅ match | ✅ match | ✅ match | ✅ match |
| `vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` | `8405f47…` | ✅ match | ✅ match | ✅ match | ✅ match | ✅ match |
| `docs/SESSION_DISPATCH_2026-07-25.md` | not tracked anywhere (`.gitignore:19`, `session_*.md`) | present (local-only working note) | absent | absent | absent | absent |

### One-line reasoning per non-canonical copy

- **#2 nested clone — CLAUDE.md, SESSION_STATE.md, README.md, vehicle_params.py:** all four are
  stale, pre-rewrite versions. Its own HEAD commit message is literally "Recover
  README/SESSION_STATE/schema/paper_draft edits lost in filter-repo rewrite, restored from
  pre-purge filesystem backup" — this clone is a recovery snapshot frozen at that point, not a
  live working copy. Its cached `origin/main` ref is also stale (points to that same recovery
  commit, not the live tip), so anything it thinks is "pushed" needs re-verification after a
  real fetch.
- **#3/#4 eloquent-easley & physics-params-audit — same four files:** identical blob hashes to
  each other and closely related to (but not identical to) the nested clone's versions.
  Same-vintage stale worktrees, both sitting at `daf453e`, both prunable, likely created for a
  task that finished or was abandoned before the current `CLAUDE.md`/`vehicle_params.py`
  revisions landed.
- **#5 reconcile-vehicle-master-ref — CLAUDE.md, SESSION_STATE.md, README.md, paper_draft.md,
  vehicle_params.py:** a *third*, distinct set of blob hashes on every file checked, including
  `paper_draft.md` (the only worktree where that file is stale too). Its branch name says
  exactly what it is — WIP on reconciling the vehicle mass/geometry reference — so a stale
  `vehicle_params.py` here is expected mid-task, not necessarily a bug, but it means anyone
  who `cd`s into this worktree is working from an old paper draft and an old CLAUDE.md too.
- **`VERIFIED_FACTS_LEDGER_july24.md` absent from all four non-canonical locations:** the
  ledger didn't exist yet when any of these four snapshots were frozen. Practically: CLAUDE.md's
  own standing rule says to read this ledger before asserting any parameter as fact — a session
  operating inside any of these four directories cannot do that at all, silently.
- **#1 outer SESSION_STATE.md marked ⚠️, not ❌:** this is the *frontier*, not a stale copy — it's
  today's rewrite (matches the task run in this same session block), committed locally as
  `d43081a` but not yet pushed. Once pushed, it becomes canonical.
- **#1 outer README.md marked ⚠️:** HEAD matches canonical exactly; the divergence is a live,
  uncommitted working-tree edit in progress right now, not staleness.

## Sensitive-content sweep

**Personal/health keywords** (`therap`, `medicat`, `diagnos`, `prescription`, `mental health`,
`panic attack`, `anxiety`, `depress`, `ssn`): raw grep returned nonzero counts, but every single
match traced to one of two things — (a) `diagnos-` used in an engineering-debugging sense
("diagnostic script"), or (b) a *prior* audit's own methodology text quoting these exact
keywords as its search list (`HANDOFF_AUDIT_2026-07-24/...`, `_inbox/LIVE_SESSION_LOG.md`).
**Zero genuine personal/health disclosures found**, consistent with the prior 2026-07-24 audit's
own conclusion. `ssn` / social-security-shaped strings: zero hits.

**Secret-shaped strings** (`ghp_`, `sk-` API-key pattern, AWS `AKIA`, PEM private-key headers):
clean across all five locations.

**`.env`:** untracked everywhere it exists (only in #1), keys are `WANDB_API_KEY`, `HF_TOKEN`,
`hub_key` — not committed, `git ls-files` returns nothing for it. No action needed.

### Flag: one real hit

`_inbox/session_archive/LIVE_SESSION_LOG_2026-07-17.md`, three occurrences of a raw, live-format
`CLAUDE_CODE_OAUTH_TOKEN` value in plaintext (`export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...`).
Value not reproduced here. This is not a new discovery — a later note in the current
`_inbox/LIVE_SESSION_LOG.md` (searched, not quoted) records that this was already found and
"left untouched per Josie's choice." Re-flagging per this audit's standing rule regardless of
that prior decision, since the file is still sitting there in plaintext today. Whether that
token is still live can only be checked by comparing it against Vista's `~/.bashrc` value,
which is outside this sandbox's reach (that's exactly the live task at PART 5 B6 of
`SESSION_DISPATCH_2026-07-25.md`).

## Recommended next human decisions (not taken by this audit)

1. Decide whether `can-it-ford/can-it-ford`, and the three `.claude/worktrees/*`, should be
   deleted, archived, or `git worktree remove`'d. This audit did not touch any of them.
2. If any of them still has in-progress work worth keeping (most likely
   `reconcile-vehicle-master-ref`, given its branch name and its distinct `vehicle_params.py`),
   pull that work out deliberately before removing the directory — don't let a bulk cleanup
   silently discard it.
3. Push the outer repo's local `d43081a` (`SESSION_STATE: reduce to pointer...`) so
   `SESSION_STATE.md` on GitHub stops being one commit stale — a lane-scoped decision per
   `SESSION_DISPATCH_2026-07-25.md` PART 0.6 ("never push" unless your lane says so), not
   something to do reflexively.
4. Decide what to do about the plaintext OAuth token in the 07-17 archive log — leave as
   documented history, or scrub the three lines now that it's been re-flagged twice.
5. Run `git worktree repair` on the outer repo (or just re-verify on the real Mac, outside this
   sandbox) to check whether the `prunable` status on the three worktrees is a real problem or
   an artifact of this audit running inside a mounted sandbox copy.
