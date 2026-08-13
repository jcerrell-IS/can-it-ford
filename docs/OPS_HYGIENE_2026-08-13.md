# Ops hygiene: worktree audit, Vista quota, and a proposed idev routing rule

Date: 2026-08-13. Snapshot taken **17:59 CEST**.

**Nothing in this document was executed. No worktree was pruned, no branch deleted,
no file removed, no quota reclaimed.** Every entry below is a recommendation for
Josie, and every one of them needs re-verifying at the moment it is run, for the
reason in the next paragraph.

**Read this before acting on any row.** The worktree table has a short shelf life.
Between two runs of the same read-only audit script, ten minutes apart, **five
worktrees changed state**: `provenance-writer-reconcile-489192` gained a commit,
`retire-coupling-module-f20ad4` gained a commit and four modified files,
`rtfd-test-phase-1-4-569130` went from 1 commit ahead to 3,
`semi-empirical-citations-fcc6f3` gained an untracked file, and
`render-realism-vehicle-water-ad1490` moved from `be72b87` to `fcfdf98` and went
from fully pushed to **21 commits unpushed**. At least five other sessions were
writing to this repo while the audit ran. A worktree that is safe to retire at
17:59 may hold unbacked work at 18:10. Re-run the audit immediately before any
deletion.

---

## 1. Worktree audit

**There are 18 entries, not 11.** One primary checkout plus 17 linked worktrees.
The "eleven worktrees" figure this work was commissioned on is stale; seven more
have been created since. Counted live with `git worktree list`.

`behind`/`ahead` are against `main`. `unpushed` counts commits not on the branch's
own `origin/` ref, and is `n/a` where the branch has no remote at all.

| # | Worktree | Branch | Head | Behind | Ahead | Dirty | On origin | Recommendation |
|---|---|---|---|---|---|---|---|---|
| 1 | `can-it-ford` | `main` | `1a868f3` | 0 | 0 | 1 mod, 24 untracked | yes, 0 unpushed | **KEEP** — primary checkout |
| 2 | `can-it-ford-moving-vehicle` | `claude/moving-vehicle-exploratory-2026-08-11` | `feecf5f` | 50 | 0 | 4 untracked | **no** | **RETIRE, now safe** — the 4 files are preserved in `51d811d`, pushed |
| 3 | `can-it-ford-realism` | `realism-exploration` | `c4af419` | 33 | 8 | clean | yes, 0 unpushed | **KEEP** — active, fully backed up |
| 4 | `can-it-ford-visual-trial` | `claude/visual-physical-realism-trial-2026-08-11` | `9480b0a` | 50 | 1 | clean | **yes, 0 unpushed** (pushed by this session) | **RETIRE, now safe** |
| 5 | `can-it-ford-warpmpm-continue` | `warpmpm-continue` | `4924940` | 26 | 6 | clean | yes, **1 unpushed** | **KEEP** — push the 1 commit first |
| 6 | `concurrent-session-safety-570b39` | same | `13187c0` | 33 | 0 | clean | no | **RETIRE** — 0 ahead, 0 dirty, nothing to lose |
| 7 | `ctx-census` | `worktree-ctx-census` | `9d53acc` | 80 | 0 | 3 untracked | no | **HOLD** — 3 unbacked files, see §2 |
| 8 | `friction-resolution-reconcile-84465d` | same | `1a868f3` | 0 | 0 | **mid-merge**, 3 mod + 6 staged + 1 untracked | no | **DO NOT TOUCH** — see §2, flagged |
| 9 | `orphan-rescue-token-rotate-d72f90` | same | `51d811d` | 0 | 1 | 1 untracked | yes, 0 unpushed | **KEEP until this session closes**, then retire |
| 10 | `provenance-writer-reconcile-489192` | same | `a24cdec` | 0 | 1 | clean | no | **HOLD** — 1 commit exists only here |
| 11 | `render-realism-vehicle-water-ad1490` | same | `fcfdf98` | 0 | 3 | clean | yes, **21 unpushed** | **HOLD** — 21 commits not on the remote |
| 12 | `render-realism-vehicle-water-f9127a` | same | `1a868f3` | 0 | 0 | clean | no | **RETIRE** — empty, duplicate of #11's purpose |
| 13 | `retire-coupling-module-f20ad4` | same | `c4aea86` | 0 | 1 | 4 mod | yes, 0 unpushed | **HOLD** — 4 uncommitted files, active |
| 14 | `rtfd-test-phase-1-4-569130` | same | `68e4a30` | 0 | 3 | clean | no | **HOLD** — 3 commits exist only here |
| 15 | `semi-empirical-citations-fcc6f3` | same | `1a868f3` | 0 | 0 | 1 untracked | no | **HOLD** — 1 unbacked file |
| 16 | `slide-resolution-dependence-reconcile-a5bf74` | same | `1a868f3` | 0 | 0 | clean | no | **RETIRE** — empty |
| 17 | `warpmpm-flood-vehicle-investigation-1b62fa` | same | `6434258` | 16 | 0 | 2 untracked | no | **HOLD** — DP-5 owns, unbacked, see §2 |
| 18 | `warpmpm-gravity-provenance-435363` | same | `6d6544f` | 26 | 3 | clean | no | **RETIRE, verified safe** — see below |

Rows 6, 12, 16 are the only unambiguous no-risk retirements: zero ahead, zero dirty,
nothing that exists only there.

**Row 18, verified independently rather than taken on the dispatch's word.**
`6d6544f` is an ancestor of both local `warpmpm-continue` and
**`origin/warpmpm-continue`** (`git merge-base --is-ancestor`, both returned true).
Its 3 commits are therefore already published and the branch needs no push. Safe to
retire. Note `origin/warpmpm-continue` is at `66912e3` while local is at `4924940`,
which is the separate 1-unpushed-commit item in row 5.

**Row 2's premise changed during this session.** The four untracked files are now
committed and pushed as `51d811d` on `claude/orphan-rescue-token-rotate-d72f90`,
confirmed by `git ls-remote`. The source worktree was not modified: it still shows
the same four files untracked. Retiring it now loses nothing.

**Row 11 is the clearest example of why the re-verify warning exists.** At 17:45
this worktree was at `be72b87`, clean, 18 behind, and fully pushed, which read as a
safe retirement. By 17:59 it was at `fcfdf98` with 21 commits not on
`origin/...ad1490` (remote still at `4b3bcb3a`). Retiring it on the 17:45 reading
would have destroyed 21 commits.

---

## 2. Flagged: uncommitted work found that the dispatch did not list

Per operating protocol point 1, these are reported and **left completely alone**.
Nothing here was read for content beyond `git status`, staged, committed, or moved.

### 2a. `friction-resolution-reconcile-84465d` is mid-merge, on canonical files

The most serious item in this audit.

`MERGE_HEAD` is present in
`.git/worktrees/friction-resolution-reconcile-84465d`, so a merge is **in progress
and not concluded**. Three paths are in unmerged (`UU`) state in the index:

- `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` — **canonical**
- `scripts/check_claims.py`
- `simulation/failure_modes.py`

plus `CLAUDE.md` in `MM` state, staged *and* further modified — **also canonical**.
Six more paths are staged.

The working-tree files contain **zero conflict markers**, so a session has resolved
the conflicts in the files but has not yet `git add`ed them to clear the unmerged
index entries. That is a session actively mid-operation, not abandoned wreckage.

**Do not prune, checkout, reset, or `git add` anything in this worktree.** Both
canonical files (`CLAUDE.md` and the corrections register) are explicitly outside
this session's write scope, and interrupting a merge mid-resolution is how the
2026-08-07 concurrent-session breach happened. Leave it to whichever session owns
it. If it is still in this state with no session attached, the owner should finish
or `git merge --abort` it themselves.

### 2b. Unbacked files in four other worktrees

Untracked and existing in no git object, so a prune would destroy them:

- `ctx-census`: `docs/C1_ROOT_CAUSE_2026-08-07.md`,
  `docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md`, `renders_preview/`.
  The second is cited by name in `CLAUDE.md` item 4 as the location of that item's
  full working, so it is load-bearing for a canonical claim and is unbacked.
- `warpmpm-flood-vehicle-investigation-1b62fa`: `analysis/conformal_l1_vs_l2.py`,
  `docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md` (DP-5 owns).
- `semi-empirical-citations-fcc6f3`: 1 untracked file.
- `retire-coupling-module-f20ad4`: 4 modified files.

### 2c. The 24 untracked files in the primary checkout are a known state, not new

`renders/yaris_render_s1/*.py` — `gates.py`, `gates_all_runs.py`,
`gates_both_scenarios.py` and 21 more. This matches `CLAUDE.md`'s own standing note
that the 2026-08-12 `.gitignore` carve-out un-ignored 24 `.py` files of which only
2 (`sim_standing.py`, `vehicle_live.py`) are tracked. **Un-ignored is not tracked.**
These have no commit history and are one `rm` from gone, which is a real risk given
that `gates.py` defines `RHO_REF` and the gate thresholds. Committing them is out of
this session's scope but is worth a dispatch of its own.

Also untracked in the primary checkout: `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`,
written by a **concurrent session**, byte-different from this session's file of the
same name. See §5.

---

## 3. Vista `/home1` quota

Live, 17:5x CEST 2026-08-13, from `/usr/local/etc/taccinfo`:

| Cluster | `/home1` used | Limit | %Used | Files | SUs | Expire |
|---|---|---|---|---|---|---|
| **Vista** | **20.8 GB** | 23.3 GB | **89.14 %** | 131,255 / 500,000 | **651** | 2026-09-30 |
| LS6 | 4.6 GB | 10.0 GB | 45.66 % | 73,983 | **9,615** | 2026-09-30 |

Largest directories under Vista `$HOME`, `du -sh` sorted:

| Directory | Size | Share of the 23.3 GB quota |
|---|---|---|
| `~/.cache` | **16 GB** | 69 % |
| ├─ `~/.cache/uv` | **14 GB** | **60 %** |
| └─ `~/.cache/genesis` | 1.8 GB | 7.7 % |
| `~/.vscode-server` | 3.7 GB | 16 % |
| `~/.local` | 1.5 GB | 6.4 % |
| `~/.claude` | 405 MB | 1.7 % |
| `~/.nv` | 156 MB | 0.7 % |
| `~/.venv_mcp_tools` | 145 MB | 0.6 % |

**One directory is the whole problem.** `~/.cache/uv` alone is 14 GB, 60 % of the
entire quota, and it is a package cache: it is regenerable by definition and holds
no results. Clearing it takes `/home1` from 89.14 % to roughly **29 %** in one
command, with no risk to any run output.

```bash
scripts/tacc.sh vista 'uv cache clean; du -sh ~/.cache'
```

Second candidate, worth 1.8 GB: `~/.cache/genesis`. Genesis is the abandoned
box-proxy path (`CLAUDE.md` item 1); no gated run uses it. Confirm no live Track-2
work depends on it before clearing.

**Success looks like** `/home1` reporting under 30 % and `uv` re-downloading
packages on next use. **Most likely failure mode** is a slower first `uv` install
afterwards, which is the intended cost, not a regression.

---

## 4. Proposed routing rule

### The evidence, and an honest problem with it

The dispatch asked for this rule to cite the recorded measurement of **150.35 vs
1.29 node-hours** (164 interactive jobs at 99.1 % of the total against 23 batch jobs
that produced every gated result, 80 interactive jobs ending in `TIMEOUT`), stored in
project memory as `vista-su-burn-is-idev-not-science`.

**That measurement does not reproduce, and the discrepancy is a method difference,
not the passage of time.** Re-derived live from `sacct -X` on 2026-08-13, node-hours
computed as `ElapsedRaw * NNodes / 3600`, jobs classed interactive by an `idv*` name:

| Vista, scope | Interactive jobs | Interactive node-h | TIMEOUTs | Batch jobs | Batch node-h | Interactive share |
|---|---|---|---|---|---|---|
| All 2026 (live today) | 187 | 157.32 | 98 | 42 | 16.62 | **90.44 %** |
| Cut off at 2026-08-08 | 174 | 147.72 | 89 | 42 | 16.62 | **89.89 %** |
| Recorded in memory | 164 | 150.35 | 80 | 23 | **1.29** | **99.1 %** |

The interactive side is close (164 vs 174 jobs, 150.35 vs 147.72 node-hours). **The
batch side is off by more than 12x and does not converge at any cutoff** — batch is
16.62 node-hours across 42 jobs both today and before 2026-08-08, so no amount of
new work explains a stored figure of 1.29 across 23 jobs. The stored figure was
probably scoped to can-it-ford job names only, or computed in SUs rather than
node-hours, or windowed to one allocation period. The method was not recorded with
it, so it cannot be re-derived.

**Cite the conclusion, not the 99.1 %.** The qualitative finding is robust under
every scope tested: interactive work dominates Vista's burn (90 % live, 99 % as
recorded) and it fails constantly, **98 of 187 interactive jobs ended in TIMEOUT**
against 1 of 42 batch jobs. Do not quote "99.1 %" or "1.29 node-hours" again without
re-deriving them and recording the method.

**LS6 is a different machine in this respect, and that is new.** Interactive share
there is only **47.41 %** (47.43 interactive node-hours against 52.62 batch), with
**27 of 56** interactive jobs timing out but **0 of 26** batch jobs. LS6 already has
the healthier pattern, which strengthens the case for sending work there.

Live queue at snapshot time: Vista is running `909166 idv52247` with 1:40 left of a
2-hour interactive reservation against a 651-SU balance. LS6 is running
`3362561 idv46807` with `3362573 g128canon` queued behind it. Vista job `908982`,
cited in the dispatch as "exit code 137", is recorded by the scheduler as
**`idv55386`, State `TIMEOUT`, ExitCode `0:0`, 1806 s (30.1 min) on 1 node**. The
137 the session saw is `128+9`, the SIGKILL at wall-clock expiry. It was **not** an
OOM kill, which is what 137 usually suggests, so do not diagnose it as a memory
problem.

### The rule, three lines

1. **Open `idev` only for work that needs an interactive GPU *and* has a stated exit
   condition and a wall time set to it.** File checks, git operations, `grep`, quota
   and `squeue` monitoring, and anything CPU-only run on the **login node**. 98 of
   187 Vista interactive jobs died on the clock, so an `idev` without a written exit
   condition is a timeout that has not happened yet.
2. **GPU work goes to LS6, not Vista.** LS6 holds **9,615 SUs** against Vista's
   **651**, both expiring 2026-09-30, and `$SCRATCH/warpmpm_ls6_env` is already
   standing there (warp 1.12.1, torch 2.8.0+cu128, x86_64, so the aarch64 failure
   class does not apply). Spend Vista's remaining 651 SUs **only** on work that
   genuinely requires GH200 or aarch64; everything else is an LS6 job.
3. **Anything unattended, longer than ~15 minutes, or reproducible is `sbatch` via
   `scripts/tacc_submit.sh`, never `idev`.** On Vista the batch path produced every
   gated result for 16.62 node-hours while interactive burned 157.32 for none, at a
   1-in-42 failure rate against 98-in-187.

---

## 5. Cross-reference: the credential finding is deliberately not in this document

The plaintext OAuth token exposure on Vista and LS6 is written up separately in
`docs/CREDENTIAL_EXPOSURE_2026-08-13.md`. That file is **committed on a local-only
branch, `claude/credential-exposure-2026-08-13-DO-NOT-PUSH`, and deliberately not
pushed**, because `jcerrell-IS/can-it-ford` is a **public** repository and the
credentials are not yet rotated. `docs/SECURITY_ACTIONS_2026-07-31.md` records that
GitHub keeps serving unreferenced commit objects by SHA even after a `filter-repo`
rewrite, so publishing that map is effectively irreversible. It should be pushed
only after rotation, or never.

A **concurrent session independently produced its own**
`docs/CREDENTIAL_EXPOSURE_2026-08-13.md` in the primary checkout, byte-different
from this session's, and reached the same conclusion in its own header: deliberately
uncommitted, commit only after rotation or not at all. Two sessions arriving at that
independently is the strongest evidence available that not pushing is the right
call. **Reconcile the two files before either is committed** — they are different
documents with the same filename, which is exactly the duplicate-filename hazard the
directory-provenance rules exist for.
