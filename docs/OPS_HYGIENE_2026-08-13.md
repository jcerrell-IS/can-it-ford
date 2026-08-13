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

**There are 18 entries, not 11.** One primary checkout plus 17 linked worktrees,
counted live with `git worktree list`. The "eleven worktrees" figure this work was
commissioned on is stale. **The increment depends on a scope the dispatch never
stated:** if its 11 counted the primary checkout, 7 have been added; if it meant 11
*linked* worktrees, 6 have. Both readings are defensible, so the raw count is quoted
here rather than the delta.

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

Rows 6, 12, 16 are the only unambiguous no-risk retirements: zero ahead, zero dirty.
**Stated with its method:** that rests on `git status --porcelain`, which excludes
ignored paths by design, so it cannot by itself support "nothing exists only there".
Re-checked with `git status --porcelain --ignored`, each of those worktrees does
carry ignored entries, but they are build and editor droppings, `.DS_Store`,
`__pycache__/`, a `.bak`, and per-worktree `.claude/` state. No unique work. The
conclusion holds; the original one-line method did not establish it.

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

**What "retire" does and does not destroy — read this before acting on any row.**
An earlier version of this section was wrong about this, in a document whose whole
purpose is to authorise deletions, so it is stated precisely:

- `git worktree prune` removes **administrative records only**, for worktrees whose
  directories are already gone. It deletes no file and no commit.
- `git worktree remove <path>` deletes the **working directory**. It does **not**
  delete the branch ref, and therefore destroys **no commits**. It also **refuses**
  to run on a worktree containing untracked or modified files unless you add
  `--force`.
- The genuinely destructive steps are `git worktree remove --force`, a manual
  `rm -rf`, and `git branch -D`. Only those can lose work.

So the risk in every HOLD row below is **untracked files** (lost by `--force` or
`rm -rf`) and **unpushed commits** (lost only if you also delete the branch), not
worktree removal by itself.

**Row 11 is still the clearest example of why the re-verify warning exists**, though
for a narrower reason than first stated. At 17:45 it was at `be72b87`, clean, 18
behind, fully pushed, reading as a safe retirement. By 17:59 it was at `fcfdf98`
with 21 commits not on its remote, and by the time this was re-checked it had moved
again to `e22737d`. An earlier version claimed "retiring it on the 17:45 reading
would have destroyed 21 commits" — **that was false twice over**: at 17:45 those
commits did not yet exist, and worktree removal would not have destroyed them
anyway. The correct lesson is narrower: a "clean and fully pushed" reading goes
stale within minutes on this repo, so **`git branch -D` on the strength of an old
audit is the real hazard**, not the worktree removal.

**A related fact about row 11, found by an adversarial check and worth recording.**
Three commits that were once on `origin/...ad1490` — `be72b87`, `991bf13`,
`4b3bcb3a` — are currently reachable from **zero refs**. That sounds alarming and is
not: `git cherry claude/render-realism-vehicle-water-ad1490 4b3bcb3a` returns `-`
for all three, meaning **equivalent patches are present downstream**. The branch was
rebased onto `1a868f3`, and the three became `2725eb7`, `1d78d06` and `fcfdf98` with
identical subject lines. **No content is at risk and no recovery is needed.** Every
rebase orphans its pre-rebase commits; reachability alone is not evidence of loss,
and the patch-equivalence check is what settles it.

---

## 2. Flagged: uncommitted work found that the dispatch did not list

Per operating protocol point 1, these are reported and **left completely alone**.
Nothing here was read for content beyond `git status`, staged, committed, or moved.

### 2a. `friction-resolution-reconcile-84465d` was mid-merge on canonical files — now resolved

**RESOLVED DURING THIS AUDIT. Kept on the record because the hazard was real and
because it is the sharpest illustration of how fast this repo moves.**

At **17:45** this worktree had `MERGE_HEAD` present, so a merge was in progress and
not concluded, with three paths in unmerged (`UU`) state:

- `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` — **canonical**
- `scripts/check_claims.py`
- `simulation/failure_modes.py`

plus `CLAUDE.md` in `MM` state, staged *and* further modified — **also canonical** —
and six more paths staged. The working-tree files held **zero conflict markers**, so
a session had resolved the conflicts but had not yet `git add`ed them.

By **18:2x** `MERGE_HEAD` is **gone**, the merge has concluded, there are **zero**
`UU` paths, `CLAUDE.md` is a plain `M`, and 11 paths are staged. The owning session
finished its own merge, exactly as it should have.

**Nothing in this worktree was pruned, checked out, reset, or `git add`ed by this
session, and nothing was read for content beyond `git status`.** Both canonical
files are outside this session's write scope, and interrupting a merge
mid-resolution is how the 2026-08-07 concurrent-session breach happened. The right
action was to leave it alone and it was left alone.

### 2b. Unbacked files in four other worktrees

Untracked and existing in no git object. `git worktree remove` **refuses** to touch
these without `--force` (that refusal is the safety net), so what would destroy them
is `remove --force` or a manual `rm -rf`:

- `ctx-census`: `docs/C1_ROOT_CAUSE_2026-08-07.md`,
  `docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md`, `renders_preview/`.
  The second is cited by name in `CLAUDE.md` item 4 as the location of that item's
  full working, so it is load-bearing for a canonical claim and is unbacked.
- `warpmpm-flood-vehicle-investigation-1b62fa`: `analysis/conformal_l1_vs_l2.py`,
  `docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md` (DP-5 owns).
- `semi-empirical-citations-fcc6f3`: 1 untracked file.
- `retire-coupling-module-f20ad4`: 4 modified files.

### 2c. The 24 untracked entries in the primary checkout, counted correctly

An earlier version of this section wrote "`gates.py`, `gates_all_runs.py`,
`gates_both_scenarios.py` **and 21 more**" and claimed the 24 untracked entries
*were* CLAUDE.md's 24 un-ignored `.py` files. **Both were wrong**, and the second is
a false match between two different 24s. Counted live:

- `ls renders/yaris_render_s1/*.py` = **24** files, of which **2** are tracked
  (`sim_standing.py`, `vehicle_live.py`), leaving **22 untracked**. So the three
  named above are followed by **19 more**, not 21.
- The primary checkout's 24 untracked entries = those **22** `.py` files **plus 2
  docs**: `docs/CREDENTIAL_EXPOSURE_2026-08-13.md` and
  `docs/COUPLING_VALIDATION_J1_2026-08-07.md.bak-premerge`.

The two 24s are numerically equal and refer to different sets. That coincidence is
exactly the kind of thing this project's standing rules exist to catch.

The substance is unchanged and still matters: **un-ignored is not tracked.** Those
22 files have no commit history and are one `rm` from gone, which is a real risk
given that `gates.py` defines `RHO_REF` (verified live at
`renders/yaris_render_s1/gates.py:13`, `RHO_REF = 310.49`) and the gate thresholds.
Committing them is out of this session's scope but is worth a dispatch of its own.

`docs/CREDENTIAL_EXPOSURE_2026-08-13.md` in the primary checkout was written by a
**concurrent session** and is byte-different from this session's file of the same
name. See §5. The `.bak-premerge` file is unexplained and was not investigated.

---

## 3. Vista `/home1` quota

Live, 17:5x CEST 2026-08-13, from `/usr/local/etc/taccinfo`:

| Cluster | `/home1` used | Limit | %Used | Files | SUs | Expire |
|---|---|---|---|---|---|---|
| **Vista** | **20.8 GB** | 23.3 GB | **89.14 %** | 131,255 / 500,000 | **651** | 2026-09-30 |
| LS6 | 4.6 GB | 10.0 GB | 45.66 % | 73,983 | **9,615** | 2026-09-30 |

Largest directories under Vista `$HOME`. **Figures are exact `du -sk`, not `du -sh`.**
The first version of this section used `du -sh` and its rounded column did not add
up: the six entries summed to 21.906 GB against a reported 20.8 GB used, and the
percentage column summed to 94.4 % against 89.14 %. That was a rounding artifact,
not a real inconsistency, but it made two headline numbers wrong. Corrected:

| Directory | Exact size | Share of the 23.3 GB quota |
|---|---|---|
| `~/.cache` | **15.015 GB** | 64.4 % |
| ├─ `~/.cache/uv` | **13.126 GB** | **56.3 %** |
| └─ `~/.cache/genesis` | ~1.8 GB | 7.7 % |
| `~/.vscode-server` | 3.657 GB | 15.7 % |
| `~/.local` | 1.408 GB | 6.0 % |
| `~/.claude` | 0.395 GB | 1.7 % |
| `~/.nv` | 0.152 GB | 0.7 % |
| `~/.venv_mcp_tools` | 0.141 GB | 0.6 % |
| **Sum of the six** | **20.769 GB** | |
| **`du -sk $HOME`** | **20.782 GB** | |
| **Quota-reported used** | **20.8 GB** | |

**The accounting now closes**: the six directories account for 20.769 GB of a
20.782 GB home, and the quota's own 20.8 GB agrees to within its printed precision.

**One directory is most of the problem.** `~/.cache/uv` is **13.126 GB, 56.3 %** of
the entire quota, and it is a package cache: regenerable by definition, holding no
results. Clearing it takes `/home1` from 89.14 % to roughly **33 %**.

**The reclaim is real, verified rather than assumed.** A cache symlinked to
`$SCRATCH` or `$WORK` is routine on TACC and would make the reclaim zero, so it was
checked: `~/.cache` and `~/.cache/uv` are **real directories**, `readlink -f`
resolves each to itself under `/home1`, and `df` reports both on
`192.168.16.21:/vista/home1`, the filesystem the quota measures.

```bash
scripts/tacc.sh vista 'uv cache clean'
scripts/tacc.sh vista '/usr/local/etc/taccinfo | grep home1'
```

**Verify with the quota, not with `du`.** The first version checked the result with
`du -sh ~/.cache` while stating the success criterion as a `/home1` percentage;
those measure different things. The second command above is the one that tests the
claim.

Second candidate, worth ~1.8 GB: `~/.cache/genesis`. Genesis is the abandoned
box-proxy path (`CLAUDE.md` item 1); no gated run uses it. Confirm no live Track-2
work depends on it before clearing.

**Success looks like** `/home1` reporting **about 33 %**, down from 89.14 %.
**Most likely failure mode** is a slower first `uv` install afterwards, which is the
intended cost, not a regression.

---

## 4. Proposed routing rule

### The evidence: the stored measurement is SOUND, and the method is the whole story

**CORRECTION, same day, appended after this document was first committed and
pushed. The first version of this section claimed the stored 150.35-vs-1.29
measurement "does not reproduce". That was WRONG and is withdrawn.** It reproduces
closely under its own stated method. The failure was in the re-derivation, not in
the stored figure, and the correction is recorded here rather than silently edited
because the wrong version is already in the pushed history at `a01e6e9`.

The measurement, stored in project memory as `vista-su-burn-is-idev-not-science`:
164 interactive jobs, **150.35 node-hours, 99.1 %**, against 23 batch jobs at
**1.29 node-hours**, with 80 interactive jobs ending in `TIMEOUT`. Critically, the
memory **also records its method**: `sacct -X -S 2026-07-01`, with interactive
defined as job names matching `idv*` **or `holder`**.

Re-derived live 2026-08-13, node-hours as `ElapsedRaw * NNodes / 3600`:

| # | Vista | Window | Interactive = | Int. jobs | Int. node-h | TIMEOUT | Batch jobs | Batch node-h | Int. share |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Stored, 2026-08-07** | `-S 2026-07-01` | `idv*` or `holder` | 164 | 150.35 | 80 | 23 | **1.29** | **99.1 %** |
| 2 | **Same method, today** | `-S 2026-07-01` | `idv*` or `holder` | 184 | 166.14 | 95 | 40 | **2.46** | **98.54 %** |
| 3 | Classifier changed only | `-S 2026-07-01` | `idv*` **only** | 182 | 152.23 | 94 | 42 | **16.62** | 90.16 % |
| 4 | Both changed | `-S 2026-01-01` | `idv*` only | 187 | 157.32 | 98 | 42 | 16.62 | 90.44 % |

**Row 2 reproduces row 1.** Every difference is six additional days of jobs:
+20 interactive jobs, +15.79 node-hours, +15 timeouts, +17 batch jobs, +1.17 batch
node-hours. The share moved 99.1 % → 98.54 %, which is drift, not disagreement.

**Row 3 isolates the cause, holding the window fixed.** An earlier version of this
section asserted the classifier was responsible while showing only rows 2 and 4,
which differ in classifier *and* window, so nothing was held fixed. Row 3 was added
to close that: same window, only the classifier changed. Batch node-hours go
**2.46 → 16.62, a 6.76x inflation, from the classifier alone.** Widening the window
(row 3 → row 4) adds almost nothing, 16.62 → 16.62.

**The mechanism is two jobs.** An `idv*`-only classifier reclassifies `holder` jobs
as **batch**; `holder` jobs are interactive placeholders and they are large. Only
**2** jobs move between categories (184 → 182 interactive, 40 → 42 batch), and they
carry about **14 node-hours** between them. Two misfiled jobs are the entire
difference between a 98.5 % and a 90.2 % answer.

This is the same failure mode `CLAUDE.md` already documents for the
`DRIFT_THRESHOLD` count: **the number is scope-sensitive, so a bare number without
its method is what is wrong, not any particular value.** The memory got this right
by storing its method alongside its figure. Quote the figure only with
`-S 2026-07-01` and `idv*|holder` stated, and re-derive rather than trusting either
number in isolation.

**The conclusion is stronger than the first version of this section allowed.**
Interactive work is **98.5 to 99.1 %** of Vista's burn, not 90 %, and it fails
constantly: **95 of 184 interactive jobs ended in TIMEOUT**, against **0 of 40**
batch jobs. All figures in that sentence are row 2, one method, one window. (An
earlier version paired "95 of 184" with "1 of 42", which takes the interactive
count from row 2 and the batch count from row 4 — two scopes in one sentence, the
exact defect this section's own rule forbids.)

**55 interactive jobs recorded zero elapsed time**, out of 65 zero-elapsed jobs
overall. The stored memory says 58, over the same window; that specific sub-count
does not reproduce today and neither figure has been traced to a scope that explains
the other. Treat 55-of-65 as the measured value and the memory's 58 as unresolved.

**LS6 differs from Vista in one specific, robust way, and the framing here is
narrower than the first version's.** Batch node-hours exceed interactive on LS6
under both methods tried: **45.09 %** interactive under the memory's method (41.64
against 50.71 node-hours, **0 of 21** batch jobs timing out) and 47.41 % under the
wider `idv*`-only method. But those two LS6 figures differ in **both** window and
classifier, so nothing was held fixed and "method-robust" overstates what was tested.

**"LS6 is healthy, Vista is not" is also too strong.** On interactive *failure rate*
the two machines are close: LS6 24/53 = **45.3 %**, Vista 95/184 = **51.6 %**, a
6.3-point gap. The real difference is the **ratio of batch to interactive
node-hours**, which is a property of how each machine has been used, not of the
hardware. That is still the right reason to route work to LS6, but it is a usage
argument, not a machine-quality argument.

Live queue at snapshot time: Vista is running `909166 idv52247` with 1:40 left of a
2-hour interactive reservation against a 651-SU balance. LS6 is running
`3362561 idv46807` with `3362573 g128canon` queued behind it. Vista job `908982`,
cited in the dispatch as "exit code 137", is recorded by the scheduler as
**`idv55386`, State `TIMEOUT`, ExitCode `0:0`, 1806 s (30.1 min) on 1 node**.

State `TIMEOUT` at 1806 s against a 1800 s limit establishes **wall-clock expiry**,
so "not an OOM kill" is sound and the job should not be diagnosed as a memory
problem. **The specific "137 = 128+9 SIGKILL" reading is inference, not a reading:**
`ExitCode 0:0` records no signal at all, and a 6-second overshoot is shorter than
SLURM's default `KillWait=30`, under which a shell would more typically report 143
(128+15, SIGTERM). Settle it before quoting the mechanism:

```bash
scripts/tacc.sh vista 'sacct -j 908982 --format=JobID,JobName,State,ExitCode,DerivedExitCode,Timelimit,Elapsed'
```

### The rule, three lines

1. **Open `idev` only for work that needs an interactive GPU *and* has a stated exit
   condition and a wall time set to it.** File checks, git operations, `grep`, quota
   and `squeue` monitoring, and anything CPU-only run on the **login node**. 95 of
   184 Vista interactive jobs died on the clock, so an `idev` without a written exit
   condition is a timeout that has not happened yet.
2. **GPU work goes to LS6, not Vista.** LS6 holds **9,615 SUs** against Vista's
   **651**, both expiring 2026-09-30, and `$SCRATCH/warpmpm_ls6_env` is already
   standing there (warp 1.12.1, torch 2.8.0+cu128, x86_64, so the aarch64 failure
   class does not apply). Spend Vista's remaining 651 SUs **only** on work that
   genuinely requires GH200 or aarch64; everything else is an LS6 job.
3. **Anything unattended, longer than ~15 minutes, or reproducible is `sbatch` via
   `scripts/tacc_submit.sh`, never `idev`.** On Vista the batch path produced every
   gated result for **2.46 node-hours** while interactive burned **166.14** for
   none, a **67.5x** ratio, at a **0-in-40** batch failure rate against
   **95-in-184** interactive. All four figures are row 2, one method, one window.

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

---

## 6. Reproducing every number in this document

**No figure in sections 3 or 4 has an on-disk primary source in this repo.** A
search for `*sacct*`, `*taccinfo*` and `*node_hour*` artifacts, and a grep for
`ElapsedRaw`, both return empty. The method is recorded, the raw output is not.
That is a real weakness, and the mitigation is that every command is written out
here verbatim so any figure can be re-derived rather than trusted.

Burn table, rows 1 to 4. Vary `-S` and the classifier per the row:

```bash
scripts/tacc.sh vista 'sacct -X -S 2026-07-01 -o JobName%20,State,ElapsedRaw,NNodes --noheader | awk "{ nh=(\$3*\$4)/3600; if (\$1 ~ /^idv/ || \$1 ~ /^holder/) {i++; ih+=nh; if (\$2==\"TIMEOUT\") it++} else {b++; bh+=nh; if (\$2==\"TIMEOUT\") bt++} } END { printf \"int %d %.2f %d | batch %d %.2f %d | %.2f%%\n\", i,ih,it,b,bh,bt,100*ih/(ih+bh) }"'
```

Node-hours are `ElapsedRaw * NNodes / 3600`. **The SU charge multiplier was never
verified**, so these are node-hours, not SUs, and the 651/9,615 balances come from
`taccinfo` independently.

Quota and directory sizes, exact rather than `du -sh` rounded:

```bash
scripts/tacc.sh vista '/usr/local/etc/taccinfo | grep -A4 quota; du -sk $HOME $HOME/.cache $HOME/.cache/uv; ls -ld $HOME/.cache; readlink -f $HOME/.cache'
```

Worktree table, run from `/Users/josie/can-it-ford`:

```bash
git worktree list --porcelain | awk '/^worktree /{print $2}' | while read -r wt; do echo "$wt $(git -C "$wt" rev-parse --abbrev-ref HEAD) $(git -C "$wt" rev-list --left-right --count main...HEAD | tr '\t' '/') $(git -C "$wt" status --porcelain | wc -l)"; done
```

Two figures that superseded stored values and should be treated as the current ones:
Vista **651** SUs (memory says 673) and LS6 **9,615** (memory says 9,656).

