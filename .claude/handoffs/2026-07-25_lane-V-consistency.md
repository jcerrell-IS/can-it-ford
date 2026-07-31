# Lane V: L1 consumer consistency map, plus four audit answers

Date: 2026-07-25
Lane: V (consistency)
Working tree: /Users/josie/can-it-ford
Stance: read-only mapping pass. No consumer script edited. No commit, no push.

## 1. Scope and stance

The AR&R L1 rewrite landed across `af1db6d`, `85e2252`, `63e677f` on 2026-07-24.
`vehicle_params.py` gained a three-class, three-condition rule and
`data/scenario_sweep.csv` was regenerated to 10 columns. Nothing downstream was
migrated. The repo now carries five distinct L1 threshold regimes.

Two panes previously collided on `analysis/make_phase_space_v2.py`, one editing it
without re-reading. This lane deliberately produces the map only. Every claim below
was verified live with a file read, a grep, a git command, or a direct execution of
the live module. No claim is carried from a prior summary.

Vista was touched read-only over an existing SSH control socket: `awk`, `grep`,
`sed`, `stat`, `find` at bounded depth. No write, no merge, no allocation, no idev.

## 2. Corrections to the dispatch brief

Three items in the brief do not match the repo. They change what the fix has to do,
so they are recorded before the table.

1. `L1_verdict` is defined at `vehicle_params.py:186`, not 184.
   `AR_R_STABILITY_LIMITS` at `vehicle_params.py:165` is correct as briefed.

2. `analysis/make_phase_space_v2.py` does not read `data/scenario_sweep.csv`.
   Line 5 reads `data/phase_space_results.csv`, whose live header is
   `depth_m,velocity_ms,verdict,final_x_disp_m,final_y_disp_m,max_vel_ms`
   and which carries no L1 column at all. So it is not recomputing a column that
   already sits beside it in the same file. It is a second, independent L1 pipeline
   running over the L2 results file. The disagreement is real, but it is against
   `vehicle_params.L1_verdict`, not against the CSV. A fix scoped as "make it agree
   with the CSV" would not address it.

3. `plot_phase_space_live.py` lives at `analysis/plot_phase_space_live.py`, not
   under `designsafe-staging/scripts/`. `designsafe-staging/scripts/make_phase_space.py`
   does exist and does carry a hardcoded copy. A third hardcoded copy not named in
   the brief also exists: `analysis/make_phase_space.py:12`.

## 3. Live defect found during the sweep, not in the brief

`vehicle_params.py:198` compares an unrounded floating-point product to the cap:

    if depth_m * velocity_ms > limits["haz_m2s"]:

`scripts/gen_scenario_sweep.py:26` rounds for the emitted display column
(`haz = round(d*v, 4)`), but line 27 passes the raw `d, v` into `L1_verdict`.
Under IEEE754, `0.1 * 3.0` evaluates to `0.30000000000000004`. The bound is
therefore exclusive at exactly the grid points it was meant to include. Commit
`63e677f` states "enforce inclusive DV bound"; at the boundary it does not.

Verified by importing the live module and executing it:

| depth_m | velocity_ms | repr(d*v) | live L1 | stated rule gives |
|---|---|---|---|---|
| 0.1 | 3.0 | 0.30000000000000004 | NO-FORD | FORD |
| 0.2 | 1.5 | 0.30000000000000004 | NO-FORD | FORD |
| 0.15 | 2.0 | 0.3 | FORD | FORD |
| 0.3 | 1.0 | 0.3 | FORD | FORD |

Identical nominal D*V of 0.30, opposite verdicts.

Blast radius in the live canonical CSV: 4 of 70 rows carry a NO-FORD that the stated
inclusive rule makes FORD.

| depth_m | velocity_ms | class | repr(d*v) | cap | CSV says |
|---|---|---|---|---|---|
| 0.1 | 3.0 | small_passenger | 0.30000000000000004 | 0.30 | NO-FORD |
| 0.2 | 1.5 | small_passenger | 0.30000000000000004 | 0.30 | NO-FORD |
| 0.2 | 3.0 | large_4wd | 0.6000000000000001 | 0.60 | NO-FORD |
| 0.4 | 1.5 | large_4wd | 0.6000000000000001 | 0.60 | NO-FORD |

This is the split-attention failure class from `bug-triage-protocol`: the rounding
was applied to the display path and not to the decision path, in the same file, in
the same loop body.

## 4. Every L1 consumer and its live threshold

Five regimes. Regime A is canonical.

| # | File:line | How L1 is obtained | Live threshold | Depth cap | Regime |
|---|---|---|---|---|---|
| 1 | `vehicle_params.py:165`, `:186` | canonical definition | 0.30 / 0.45 / 0.60 m2/s; depth 0.30 / 0.40 / 0.50 m; velocity 3.0 m/s | yes | A canonical |
| 2 | `scripts/gen_scenario_sweep.py:9,27,28` | imports `L1_verdict` | canonical | yes | A |
| 3 | `analysis/build_poster_phase_space.py:35` | reads `row["L1_verdict"]` from `data/scenario_sweep.csv` | inherits canonical | inherits | A pass-through |
| 4 | `wandb_backfill.py:14-15` (repo root) | reads CSV columns | inherits canonical | inherits | A pass-through |
| 5 | `analysis/plot_l1_three_class.py:23-24` | own dicts, values match canonical | 0.30 / 0.45 / 0.60 plus depth 0.30 / 0.40 / 0.50 | yes | A by value, duplicated not imported |
| 6 | `tests/test_csv_schema.py:5-8` | asserts the 10-column schema | schema only | n/a | A |
| 7 | `scripts/gen_scenario_sweep.py:11,26` | own const `L1_HAZ_PRODUCT_ONLY_THRESHOLD` | 0.60 product-only | no | B legacy, intentional |
| 8 | `analysis/make_phase_space_v2.py:9` | inline lambda | 0.60 | no | C stale |
| 9 | `designsafe-staging/scripts/make_phase_space.py:9` | inline lambda, same logic | 0.60 | no | C stale |
| 10 | `analysis/make_phase_space.py:12` | inline | 0.60 | no | C stale, not in brief |
| 11 | `analysis/plot_phase_space_live.py:7` | inline lambda, lowercase column names | 0.60 | no | C stale |
| 12 | `analysis/build_phase_space_plotly.py:35` | inline `if haz > 0.60` | 0.60 | no | C stale, inputs missing |
| 13 | `analysis/wandb_backfill.py:2,24` | `from thresholds import L1_HAZ_THRESHOLD_4WD` | 0.60, defined at `scripts/thresholds.py:2` | no | C stale, via shared module |
| 14 | `hf_space/app.py:4-5` | own consts | 0.60 hazard, 0.30 safe zone | no | C stale |
| 15 | `simulation/can_it_ford_L1.py:3-6,13` | own dict, key is `"sedan"` | 0.30 / 0.45 / 0.60 product-only | no | D wrong key name, no caps |
| 16 | `analysis/recompute_l1_l2.py:8,10` | own consts | DV 0.30, depth 0.30 | yes | E single-class only |
| 17 | `figures/poster_exports/can_it_ford_phase_space.html` | baked output | 0.60 x7, 0.45 x4, 0.30 x1 | baked | stale artifact |

Notes that change the fix:

- Item 12 is already dead. `analysis/build_phase_space_plotly.py:25` reads
  `analysis/scenario_sweep.csv` and line 75 reads `analysis/phase_space_results.csv`.
  Neither file exists. The script cannot run today. Confirm before spending effort
  migrating it.

- Item 15 uses the class key `"sedan"`. Canonical renamed that key to
  `small_passenger` in `63e677f`. A caller passing `small_passenger` into
  `ford_L1` raises `KeyError`; a caller passing `sedan` into the canonical
  `L1_verdict` raises `ValueError` at `vehicle_params.py:187-191`. The two modules
  are now mutually incompatible by key name, not merely by threshold.

- Item 13 is the one consumer fixable without editing the consumer. It imports from
  `scripts/thresholds.py`, whose entire content is two lines:
  `L0_DEPTH_THRESHOLD = 0.15` and `L1_HAZ_THRESHOLD_4WD = 0.60`.
  `analysis/wandb_backfill.py` also carries a duplicated import block at lines 2 and 6.

- Item 3 is the poster path and it is correct. `build_poster_phase_space.py:8` sets
  `GRID_CSV` to `data/scenario_sweep.csv` and line 35 reads the canonical
  `L1_verdict` column through. The modified `figures/phase_space_poster_figure.png`
  and `.svg` in `git status` came from this good path.

- Copies outside the main tree. Three git worktrees under `.claude/worktrees/`
  (`eloquent-easley-3ca1ff`, `physics-params-audit-541e4f`,
  `reconcile-vehicle-master-ref`) each carry their own copies of items 8, 9, 11, 12,
  13, 14 and 15, and a nested clone at `can-it-ford/can-it-ford/` carries another
  set. That is roughly 29 additional stale copies. Fixing the main tree does not fix
  any of them.

## 5. TASK 2: which scenario_sweep.csv is current, and what else is stale

The 10-column file is current: `data/scenario_sweep.csv`, 4524 bytes, mtime
2026-07-24 22:57, 70 data rows. Header verified live:

    depth_m,velocity_ms,L0_verdict,L1_haz,L1_haz_product_only,L1_verdict,
    L1_verdict_small_passenger,L1_verdict_large_passenger,L1_verdict_large_4wd,
    L1_class_sensitive

It was written by `scripts/gen_scenario_sweep.py` at commit `63e677f`, which is
timestamped 22:57:59, the same minute as the file mtime.

The 5-column copy is stale, and the mechanism is a nested clone still sitting on
disk: `/Users/josie/can-it-ford/can-it-ford/data/scenario_sweep.csv`, 5 columns,
mtime 2026-07-23 08:44.

That nested directory is a full repo copy frozen at 2026-07-23 08:44. It is listed
at `.gitignore:47` as `can-it-ford/`, so `git status` reports nothing for it and it
is invisible to every ordinary check. Commits `cdc6037` ("Clean up nested clone")
and `daf453e` ("Remove accidentally-committed embedded git repository, add to
gitignore"), both 2026-07-23, removed it from version control but left the directory
in place. Anything read or uploaded from there is silently two days behind.

Everything in it is stale by the same mechanism. Verified mtime comparison:

| File | Live | Nested copy |
|---|---|---|
| `README.md` | 07-25 07:29 | 07-23 08:44 |
| `SESSION_STATE.md` | 07-25 05:52 | 07-23 08:44 |
| `paper_draft.md` | 07-23 08:37 | 07-23 08:44 |
| `poster_text_draft.md` | 07-15 04:24 | 07-23 08:44 |
| `PROVISIONAL_STATUS.md` | 07-15 00:45 | 07-23 08:44 |

The nested copy also carries its own `analysis/`, `scripts/`, `docs/`, `figures/`,
`hf_space/`, `tests/`, `simulation/`, `.claude/`, `_inbox/`, `archive/`, `out/`,
plus `phase_space_results_v2.csv`, `phase_space_results_mpm.csv`, and its own
`docs/track1_v3_sweep_invalid_hollow_vehicle.md`.

Warning before any cleanup: `paper_draft.md` and `poster_text_draft.md` are NEWER in
the nested copy than live. Do not blanket-delete. Diff those two first.

## 6. TASK 3: Vista plaintext OAuth token

Method: read-only over the pre-existing SSH control socket at
`~/.ssh/sockets/jcerrell0629@vista.tacc.utexas.edu-22`, opened 15:28 with
`ControlPersist 4h`. Landed on `login1.vista.tacc.utexas.edu`. Only line numbers and
boolean shape checks were emitted. No token value was ever printed or logged.

- Line 117: NO. It does not match `CLAUDE_CODE_OAUTH_TOKEN`.
- Line 112: YES. The export is still present, moved up five lines.

Shape of line 112, established without printing it: not commented out, contains
`export`, contains no command substitution or file indirection, 141 characters long.
That is a live plaintext secret assignment.

Context: `~/.bashrc` is mode 700, owner `jcerrell0629`, 170 lines, mtime
2026-07-24 20:27:31. The restrictive mode is the only mitigating factor.

Cross-check: the `2026-07-25_vista.md` handoff row in `INDEX.md` independently
reports "token still at ~/.bashrc:112". Two lanes agree, arrived at separately.

The "line 117" figure in the earlier session is stale by five lines. Answering the
literal yes/no question as posed would have returned a false all-clear.

## 7. TASK 4: AUDIT_RECONCILIATION_july17.md

Located, not missing. `/Users/josie/Downloads/AUDIT_RECONCILIATION_july17.md`,
14446 bytes, mtime 2026-07-19 19:55. A byte-identical duplicate sits beside it as
`AUDIT_RECONCILIATION_july17_1.md`, mtime 2026-07-19 19:56. Both md5
`0715d144b8aa96e73b10a7bb0c49545f`.

Why F0 could not find it: it is not in the Mac repo, not in the Vista repo, and not
in git history. `find` at `-maxdepth 3` on `/work/11603/jcerrell0629/vista/can-it-ford`
and on the Vista home both returned empty. `git log --all --diff-filter=A` for the
path returned empty. The file is unversioned and lives outside every repo, so a
repo-scoped search at any depth would have missed it.

The 4.31x claim is present verbatim at line 78:

    Evidence: particle count scales 4.31x between n_grid=64->128, not the 8x a

Better citation target. This document is a reconciliation summary, which is T3 under
the provenance hierarchy. Its own lines 90 and 115 point to the primary source, and
that primary file is in the repo and readable:
`docs/track1_v3_sweep_invalid_hollow_vehicle.md`. Cite the primary. Use the Downloads
file only to show where the claim entered.

## 8. TASK 5: the 7 commits pushed at 03:43:17

The push is real and confirmed at the reflog, which is a T1 artifact:

    b00bf7b refs/remotes/origin/main@{2026-07-25 03:43:17 -0500}: update by push

It advanced `origin/main` from `8e12e84` to `b00bf7b`.
`git rev-list --count 8e12e84..b00bf7b` returns exactly 7.

| Hash | Authored | Author | Subject |
|---|---|---|---|
| `af1db6d` | 2026-07-24 21:50:09 | Josie Cerrell | L1: apply AR&R depth and velocity caps jointly, fix generator output path |
| `85e2252` | 2026-07-24 22:20:44 | Josie Cerrell | L1: populate all three AR&R presets from Shand et al. 2011 Table 3 |
| `4d2242b` | 2026-07-24 22:36:04 | Josie Cerrell | Add verified facts ledger with intake corrections |
| `60a01a2` | 2026-07-24 22:54:36 | Josie Cerrell | Ledger: correct A3/E referent to the pre-2011 guidelines |
| `63e677f` | 2026-07-24 22:57:59 | Josie Cerrell | L1: rename class keys to Table 3 names, enforce inclusive DV bound |
| `9f5d82e` | 2026-07-25 00:36:20 | Josie Cerrell | log_l2_run: add Section G5 provenance fields |
| `b00bf7b` | 2026-07-25 01:09:12 | Josie Cerrell | Ledger F4: record Track 2 VEHICLE_SIZE as a superseded-placeholder |

Authored across 21:50 to 01:09, then pushed together at 03:43:17.

No Claude Code pane ran the push. Search was `~/.claude/projects` at `-maxdepth 2`,
bounded to files modified between 2026-07-25 00:00 and 07:00. Seven session files
matched the window. Four contain the string `git push`. Every hit is a prohibition
or a hook definition. None is an execution. Verbatim context:

- `00a185a7`: `2. DO NOT run git commit. DO NOT run git push. Fourteen contexts currently share the single working tree at /Users/josie/can-it-ford`
- `00a185a7`: `Read-only audit. Nothing deleted, moved, renamed, or edited. No \`git commit\`, no \`git push\`. \`settings.json\` not touched, it belongs to C1.`
- `4aaf5420`: `1. DO NOT run git commit. DO NOT run git push. Not once, not after asking. Fourteen contexts currently share the single working tree at /Users/josie/can-it`
- `4aaf5420`: `*"git push --force"*|*"filter-repo"*)` then `*"git push"*)` with `"permissionDecision":"ask"` and `"Rule 16: push needs explicit confirmation, every time."`
- `7a1910ed`: `2. DO NOT run git commit. DO NOT run git push. Fourteen contexts share the single working tree at /Users/josie/can-it-ford, including two live Claude Code`
- `214d00e8`: identical string to `7a1910ed`

Supporting evidence. No session file has an mtime at or near 03:43; they cluster at
02:44, 02:59, 03:01 and 06:10. `.claude/hooks/gate_destructive.sh:8-10` intercepts
any command containing `git push` and returns `permissionDecision: ask`, so a pane
push would have required an interactive approval that would appear in a transcript.
None does.

Conclusion: the push was made by a human at a terminal, outside Claude Code. It is
not unattributed automation. Nothing was deleted, and the search was not widened.

Related, worth acting on: `d43081a` (2026-07-25 05:54:09, "SESSION_STATE: reduce to
pointer, correct pane roster") is still unpushed. `origin/main..HEAD` contains that
one commit.

## 9. Named not guessed

Named from a live read, quoted with file:line above:
every row of the consumer table; the CSV headers of both
`data/scenario_sweep.csv` and `data/phase_space_results.csv`; the reflog line;
the seven commit hashes and their author dates; the Vista line numbers 112 and 117
and the shape booleans for 112; the md5 pair on the two Downloads copies; every
mtime in the nested-clone table; `.gitignore:47`; the two hook files.

Named from direct execution, not from reading:
the float boundary table in Section 3 and the 4-of-70 count, both produced by
importing the live `vehicle_params` module and iterating the live CSV. The
`git rev-list --count` result of 7.

NOT verified. Do not restate any of these as fact without checking:

- Whether the LS6 tree carries the same stale consumers. Not checked, out of lane.
- Who physically ran the 03:43:17 push. Established only by elimination across
  Claude Code transcripts in `~/.claude/projects` at `-maxdepth 2` in a bounded
  window. A push from another host, another project directory, or a shell outside
  Claude Code would not appear in that search. The conclusion is well supported but
  it is an inference, not a captured command.
- Whether the three worktrees under `.claude/worktrees/` are live or abandoned.
  Their file contents were listed; their status was not checked.
- Whether the nested clone at `can-it-ford/can-it-ford/` is referenced by any
  running process or by Claude project knowledge upload config. Only its on-disk
  state and mtimes were established.
- Whether `analysis/make_phase_space.py` and `analysis/build_phase_space_plotly.py`
  are still intended to exist at all. They were mapped, not adjudicated.
- The contents of `designsafe-staging/scripts/make_phase_space.py` beyond the
  grep hits at lines 8, 9, 12, 13, 14, 24, 29, 30, 31, 38, 67, 68, 72. The
  permission gate blocked a full read of that path, so its input CSV was not
  established.

## 10. Suggested fix order, not executed

Recorded for whoever owns the fix. Nothing here was done.

1. Single-source `L1_verdict` before touching any plotter. Seventeen consumers
   across five regimes will not converge by patching them one at a time, and the
   two prior collisions on `make_phase_space_v2.py` happened during exactly that
   kind of one-at-a-time pass.
2. Fix the float comparison at `vehicle_params.py:198` in the same edit that
   single-sources it, otherwise every migrated consumer inherits the boundary bug.
   Regenerating `data/scenario_sweep.csv` afterward will change 4 of 70 rows.
3. Resolve the `"sedan"` versus `small_passenger` key collision in
   `simulation/can_it_ford_L1.py` explicitly. It currently fails loudly rather than
   silently, which is the one good thing about it. Do not paper over it with a
   fallback that restores silent disagreement.
4. Decide whether `analysis/build_phase_space_plotly.py` and
   `analysis/make_phase_space.py` are retired. Migrating a script whose inputs do
   not exist is wasted work.
5. Assign one owner per file for the duration, per the file-ownership rule in
   `bug-triage-protocol`. The worktree and nested-clone copies need a separate
   decision and should not be swept into the same pass.
