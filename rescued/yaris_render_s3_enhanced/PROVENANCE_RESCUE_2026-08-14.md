# Provenance, rescued copy of `renders/yaris_render_s3_enhanced/`

Recovered 2026-08-14 under Dispatch 8.1. Every statement below was read or measured
live on that date, not carried from a summary.

## Why this directory exists here and not at its original path

The original tree is `renders/yaris_render_s3_enhanced/` in the main worktree. It was
reachable from **zero git refs**:

```
git log --oneline --all -- renders/yaris_render_s3_enhanced/   -> EMPTY
git check-ignore -v renders/yaris_render_s3_enhanced/sim_enhanced.py
  -> .gitignore:31:renders/*
```

Line 31 was re-derived live with `/usr/bin/grep -n`, not quoted positionally. The
`.gitignore` walk-down at lines 31-34 re-includes `renders/yaris_render_s1/*.py`
only, so nothing under `yaris_render_s3_enhanced/` was ever trackable.

The copy sits under `rescued/`, a path no `.gitignore` rule matches
(`git check-ignore` exits 1 on it). **No carve-out was added under `renders/`.** The
walk-down pattern has already gone wrong three times in this project, and adding a
fourth exception to preserve one directory would trade a recoverable problem for a
structural one.

## What was recovered, and proof the copy is faithful

13 files, 112 KB. sha256 computed on both sides on 2026-08-14; all 13 match
byte-for-byte. Nothing was edited, renamed or reformatted.

| sha256 | file |
|---|---|
| `f11f559b3c48c539d1ded1f9ec1f32d12e9c326540719a6ee0e8c98af600dcd8` | `NOTES_2026-08-07.md` |
| `a4b46c4f6952fcfce14a47915cc50983f7d90b03db6bb3bb12c5ee2e45870c7e` | `sim_enhanced.py` |
| `99cb1b4be0a14f49678c2494b0eedbb7fb9de2816919005ebd9fe48c9f055f3e` | `run_enhanced.py` |
| `cc733e818be930adc955fd0396763e85daf721ed2cd1bc3ec1e1f39af1ee3e10` | `enhanced_ladder.sbatch` |
| `4aa9ed57a2df3bafd49dff160f5f03e1ab774c624f0e2ff6e84dabc838544485` | `realwater_ladder.sbatch` |
| `a1ae1d08c10ebdd2823f9ca329a63a2287b242d17ce0e58f07cc8bd220a472f8` | `hull_sweep.sbatch` |
| `66237e9470823b21637072dbda9e814ad1d45008c2bff2c3a46cb8864bcf2124` | `hull_sweep_hullsweepdir.sbatch` |
| `92d871cbc9c3eea07ceda76297be852a8ba94b0444d454e19eaa76e69ea68084` | `results/ctrl_g64_summary.json` |
| `90d20a3a8a1be62333a0843a692adb290a18dcc401f490a9521c74251d8eafc4` | `results/enh_g96_summary.json` |
| `2a7eb0511f2c52b0f909204589638ad18c484b2553075e0fba422de580ba4d56` | `results/enh_g96_c10_summary.json` |
| `a498276cb58ad9fb54df2b0820637dc6f05264fcbfb50a719cad9b7b3312c4a8` | `results/enh_g96_real_summary.json` |
| `30d028437e2fd6de890426e2cbdfec7ba18c9541548f3b6215c96b5eb39a625e` | `results/enh_g128_c10_summary.json` |
| `3a31962a3910fcb955f4c6fc7937c90d5a4cd8df82655cc9707c19ab1370db4d` | `results/enh_g128_real_summary.json` |

The original tree is left in place, untouched. This is a second copy, not a move.

## What the payload is

Six completed runs from two Vista GH200 batch jobs, recorded in `NOTES_2026-08-07.md`
sections "Jobs submitted" and "FINAL RESULTS, all six runs": job **895330**
(`enhanced_ladder.sbatch`, elapsed 00:02:09) and job **895378**
(`realwater_ladder.sbatch`, elapsed 00:21:23). This is the sound-speed sweep that the
project records as done; the primary record of it was, until today, on one laptop disk
and on no git ref.

Read the NOTES for the findings themselves. Two are worth flagging here because they
are easy to quote wrongly:

- **The sound-speed response is non-monotone.** At fixed g96, displacement is 0.26921 m
  at c = 12.85, 0.48839 m at c = 128.45, and 0.28232 m at c = 1480.98. The intermediate
  value is the outlier, not the endpoint, so no partial correction can be extrapolated
  toward the physical answer.
- **All six are NO-FORD**, 0.26921 to 0.67768 m against the 0.05 m DRIFT_THRESHOLD. The
  verdict is invariant because the margin is large, not because the knobs do not matter.

## Standing caveats that travel with any number from these runs

Carried verbatim in intent from the NOTES, and restated here so a reader who opens
`results/` first still sees them:

1. **NOT CANONICAL.** Every summary carries its own
   `"NOT_CANONICAL": "Enhanced-physics run, not one of the 17 gated runs"`. Never merge
   these into `data/all_runs_inventory.csv`, into
   `renders/yaris_render_s1/gates_results_all_runs.json`, or into any figure that
   describes the 17 gated runs.
2. **`canitford_git_commit` in every summary is RECONSTRUCTED, not recorded.** The
   files' own `_provenance_backfill.field_confidence` block says so:
   *"RECONSTRUCTED from the manifest's mtime against git rev-list. NOT evidence of what
   ran: it cannot see a dirty tree, and this repo is edited by concurrent sessions.
   Upper bound only."* The backfill ran 2026-08-12/13 and rewrote these six files;
   their mtimes are the backfill's, not the runs'.
3. **Resolution is unconverged at every point on this ladder**, 2.038 to 4.076 cells
   per flow depth against a rule of thumb near 10.

## Two provenance gaps found during the rescue, neither resolved here

**A. The rescued `sim_enhanced.py` post-dates the six results.** All six summaries
existed by 2026-08-07 20:21 (the NOTES mtime, and NOTES tabulates all six). The
`sim_enhanced.py` in this copy has mtime 2026-08-08 03:46, and
`hull_sweep.sbatch` states in its own header that *"TWO PREREQUISITE FIXES LANDED
2026-08-08, BOTH IN sim_enhanced.py"*. So this file is a **later revision than the one
that produced `results/`**, and no summary records a sha256 of the driver that ran (the
`derived_from` field names the parent `sim_standing.py`, sha256 `5215c38bed607ef6`, not
the enhanced driver). Preserving the later revision is still strictly better than
preserving nothing, but a diff of these six results against a re-run of this file is
not a determinism test. Recorded as an assumption to revisit, not as a defect fixed.

**B. The hull sweep has scripts here and no results anywhere in this tree.**
`hull_sweep.sbatch` and `hull_sweep_hullsweepdir.sbatch` (2026-08-08) describe
themselves as *"the first run in this project where vehicle GEOMETRY actually varies"*.
`NOTES_2026-08-07.md` predates them and mentions `hull_sweep` **zero** times. The two
files differ only in output directory, `$WORK/render_s3_enhanced` against
`$WORK/render_s3_hullsweep`. Whether either was ever submitted, and where its outputs
are, is **not answerable from the Mac**: it needs a read of `$WORK/render_s3_hullsweep`
on Vista, which was unreachable during this rescue (see the recovery doc for the
transport failure). Untested either way.
