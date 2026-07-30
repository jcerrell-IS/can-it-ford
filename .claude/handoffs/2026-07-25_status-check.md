# Status check, Lane A, 2026-07-25

Session: "Identity and status check". Lane A per `docs/SESSION_DISPATCH_2026-07-25.md` PART 3.
Read-only on code and data. Files written: this one, `SESSION_STATE.md`, one append to `INDEX.md`. No SSH. No pane killed or reassigned. No script, figure, README or paper_draft touched.

## Can a poster be assembled from what exists today?

**Yes, but it is a methods-and-limitations poster, not a results poster.** Seven asset rows ship without any blocked dependency. No BLOCKED row gates the table. What cannot ship is the hero MPM render and anything resting on a Track 2 FORD verdict.

## A0. Skill inventory, verified live, not recalled

Installed on this Mac: `bug-triage-protocol`, `claude-code-prompt-install`, `connector-router`, `flood-mpm-debugging-reference`, `geoelements-tech-reference`, `mpm-render-pipeline`, `panel-audit-dispatch`, `provenance-audit`.

Named in briefs but ABSENT here, stated rather than substituted:
- `can-it-ford-science`, `can-it-ford-cluster`, `can-it-ford-output`: absent. Dispatch 0.1 is correct that `can-it-ford-science` exists nowhere.
- `directory-provenance-audit`: absent as a standalone skill. Exists only as `anthropic-skills:directory-provenance-audit`. C2 hit the same gap and flagged it instead of substituting.

## A1. Reconciliation. Four apparent conflicts, three dissolve

| Claim | Handoff A | Handoff B | Live resolution |
|---|---|---|---|
| git ahead count | C4 `:98` says 3; C2 `:59` says 2 then 6 | C5 `:32-33` says 4 | NOT a conflict. Four stale snapshots of a count that moved all night. Live `git rev-list --count origin/main..main` = **0**, everything pushed, HEAD `b00bf7b` |
| `scenario_sweep.csv` schema | F5 `:13` says 8 columns to 10 | C5 `:35-36` says 3559 B / 8 col at 22:19, 4524 B / 10 col at 22:57 | Agreement, not conflict. Live: 4524 B, 70 data rows, 10 columns, classes `small_passenger` / `large_passenger` / `large_4wd` |
| c0 crash isolation log | Chat-side dispatch called it an ORPHAN citation | Asset table `:48`, `:188`, `:316` records it Vista-side and VERIFIED | **F5 is right, the ORPHAN verdict is wrong.** Live: absent on Mac, present on Vista at 3010 B, md5 `159513563544879e19310b066c4d7d8a`. A Mac-only check produced a false negative |
| Asset table status counts | Reported as 36 rows summing to 61 statuses | n/a | **My own reporting error, not a table defect.** I gave whole-file `grep -c` counts including prose in the Notes sections. Per table row: 5 VERIFIED, 5 RETRACTED, 3 BLOCKED, 18 UNVERIFIED, 0 bare ORPHAN across 40 row-lines; the rest carry qualified labels like "VERIFIED as a diagram" and "UNVERIFIED, ESCALATED". The table reconciles. No pane should spend a round on this |

## A2. Re-stat. Nothing moved since the handoffs were written

| Path | Size | mtime |
|---|---|---|
| `data/scenario_sweep.csv` | 4524 | 07-24 22:57 |
| `docs/POSTER_ASSET_TABLE.md` | 32531 | 07-25 01:04 |
| `docs/POSTER_TEXT_BLOCKS.md` | 19121 | 07-25 01:16 |
| `docs/VERIFIED_FACTS_LEDGER_july24.md` | 40022 | 07-25 01:08 |
| `paper_draft.md` | 26197 | 07-23 08:37 |
| `figures/fig3_geometry_pipeline.pdf` | 86219 | 07-25 01:22 |
| `figures/traction_bias.pdf` | 117353 | 07-25 00:43 |

C5 warned three files changed under it mid-audit at 22:57. Re-checked: `scenario_sweep.csv` still reads 22:57, so it has been stable since. No path either handoff cites has moved.

## A3. Two ledger items closed

**1. Divergence figures, ledger Section C line 392, "BOTH UNVERIFIED".** Settled. Live `paper_draft.md:89` states 39.1 percent agreement, 9 of 23 conditions, 14 divergences of 23. Live `paper_draft.md:144` explicitly records that this supersedes the earlier 16 / 30.4 figure, which had already been marked provisional. Verdict: **14 / 39.1 is VERIFIED and live; 16 / 30.4 is SUPERSEDED.** The row belongs in Section A citing `paper_draft.md:89` and `:144`. Every surviving mention of 16 / 30.4 elsewhere is already correctly labelled superseded, provisional or stale.

**2. B8 item 7, `L0_L1_phase_space_divergence.png`.** Confirmed **absent** from the repo: `find . -maxdepth 3 -name "L0_L1*"` returns nothing. Per the dispatch it is present in Josie's Claude project knowledge, so it existed and became detached from the repo rather than never existing. Recoverable by re-adding, which may also close one of the two missing tex includes in B4. Recorded as the answer; not acted on, Lane A does not write figures.

## A3-extra. Ledger G3 independently recounted

Dispatch 1.4 says count these yourself before citing. Counted from the live CSV with stdlib `csv`:

- `L1_verdict_small_passenger` FORD = **12**
- `L1_verdict_large_passenger` FORD = **19**
- `L1_verdict_large_4wd` FORD = **24**
- `L1_class_sensitive`: True **12**, False 58, total **70**

Matches ledger G3 exactly. G3 is confirmed at T1, not carried forward.

## A4. SESSION_STATE.md rewritten as a pointer

Reduced from a 14030-byte mixed state file to a pointer. It now carries only: where truth lives in order, live git state, the sixteen-pane roster, the five human decisions, deadlines, and where the pre-restructure archive went. It restates no ledger or handoff number.

**One deliberate deviation from A4, stated rather than done silently.** A4 says rewrite as a pointer. C4's guarded block says the CLAUDE.md drift fingerprint "stays at the top of this file. If you edit it, the drift check it exists to enable stops working." I preserved that block byte-for-byte at the top rather than relocating it. It is not a duplicated ledger number; it is a drift detector that exists nowhere else, and moving it would break the one-command check it was built for. Both instructions are satisfied.

## A5. Poster readiness

**Ships now, seven rows, no blocked dependency** (asset table row numbers): 1 three-class L1 phase space, 4 Track 2 null result, 23 GP surrogate metrics, 24 Track 1 v2 sweep statistics, 26 vehicle parameter table, 35 intro and acknowledgments text, 36 plain-language methods.

**Blocked, and does not gate the rest:** row 34 the coupled-MPM hero render, which does not exist; row 31 the mpm-engine flood sequence; row 25 the failure-mode decomposition, which needs the sweep regenerated with `vx,vy,vz`.

**Retracted, never real, must not be relabelled as merely blocked:** the 8 Track 2 FORD rows and their `.npz` dumps and `.mp4` renders, plus the row 13 hero shot. Separately row 11, `figures/baseline_comparison_v2.png`, whose time series is manufactured analytically under `np.random.seed(7)` to a hardcoded `PEAK_DRIFT`. That file and its generator `scripts/plot_hailuo_comparison.py` are both tracked and are now on `origin/main`.

**Two silent-failure traps already caught:** row 5 `phase_space_poster_figure.png/.svg` is dated 07-10 while its generator is 07-21 and its input 07-24, so it cannot have been built from what is in the tree. Row 19 QR codes point at a repo that is currently private, so a scan returns 404 or a login wall.

## Not resolved, named rather than guessed

- Whether the three `.claude/worktrees/*` stale checkouts should be pruned. They hold frozen duplicates of `paper_draft.md`, `README.md` and `PROVISIONAL_STATUS.md` and pollute any repo-wide grep. Lane A does not delete.
- The five PART 8 human decisions. None is Lane A's to make.
- Whether the retracted-but-pushed synthetic figure needs a follow-up commit and push to remove it from the default branch. That is a push decision, and no lane may push.
- A plaintext credential was pasted into a chat transcript this session. Rotation is the user's action. Never printed here; not searched for in the repo by Lane A, since that is C5's sweep.
