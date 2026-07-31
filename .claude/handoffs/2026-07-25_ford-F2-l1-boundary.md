# F2: L1 float-boundary fix at the D*V threshold

Date: 2026-07-25
Lane: ford-F2 (L1 boundary)
Working tree: /Users/josie/can-it-ford
Gate: read `.claude/handoffs/2026-07-25_lane-V-consistency.md` Section 3 in full first. Present, 18469 bytes, mtime 17:01.
Files edited: exactly two. `vehicle_params.py` (one line) and `data/scenario_sweep.csv` (regenerated).
Not committed, not pushed. `d43081a` remains unpushed on main.

## Headline

`figures/fig1_l1_three_class.pdf`, the recommended poster hero, carried four wrong
cells, and all four sat exactly on the D*V = 0.30 and 0.60 threshold lines the figure
exists to show.

## Two line-number corrections

Both the F2 brief and the Lane V handoff carried the same off-by-one. Recorded so the
next lane does not edit the wrong line.

- The comparison is `vehicle_params.py:197`, not 198. Line 198 is the `return`.
- The `round(d*v, 4)` display rounding is `scripts/gen_scenario_sweep.py:25`, not 26.

Line 27 is correct as briefed: it passes raw `d, v` into `L1_verdict`. The defect
itself is exactly as Lane V described. Only the two line numbers move by one.

Verbatim, pre-fix:

    197	    if depth_m * velocity_ms > limits["haz_m2s"]:
    198	        return "NO-FORD"

    25	        haz = round(d*v, 4)
    26	        l1_haz_product_only = "FORD" if haz <= L1_HAZ_PRODUCT_ONLY_THRESHOLD else "NO-FORD"
    27	        l1 = L1_verdict(d, v, vehicle_class=args.vehicle_class)

## STEP 0: baseline git state, verbatim

    === git status --porcelain | head -40 ===
     M .claude/hooks/gate_destructive.sh
     M .claude/hooks/gate_protected_files.sh
     M .claude/settings.json
     M README.md
     M data/track1_sweep_v2/mpm_sweep_data_schema.md
     M figures/phase_space_poster_figure.png
     M figures/phase_space_poster_figure.svg
    ?? .claude/handoffs/
    ?? .claude/settings.json.bak.20260723231255
    ?? AUDIT_TABLE_2026-07-24.md
    ?? Cerrell_TACC_42x56.pdf
    ?? HANDOFF_AUDIT_2026-07-24/
    ?? "_inbox/can it ford master orchestration prompt 2026-07-24.pdf"
    ?? _inbox/can-it-ford-HANDOFF-AUDIT-2026-07-24.zip
    ?? analysis/plot_geometry_pipeline.py
    ?? analysis/plot_l1_three_class.py
    ?? analysis/plot_traction_bias.py
    ?? analysis/recompute_l1_l2.py
    ?? docs/DIRECTORY_PROVENANCE_AUDIT_2026-07-25.md
    ?? docs/L1_L2_RECOMPUTE_2026-07-25.md
    ?? docs/PANE_BUS.md
    ?? docs/POSTER_ASSET_TABLE.md
    ?? docs/POSTER_TEXT_BLOCKS.md
    ?? figures/fig1_CAPTION.md
    ?? figures/fig1_l1_three_class.pdf
    ?? figures/fig1_l1_three_class.svg
    ?? figures/fig3_geometry_pipeline.pdf
    ?? figures/pipeline_diagram_poster.svg
    ?? figures/traction_bias.pdf
    ?? figures/traction_bias.svg
    ?? figures/traction_bias_CAPTION.md
    ?? poster.html

    === git diff --stat | tail -5 ===
     README.md                                     |   6 +-
     data/track1_sweep_v2/mpm_sweep_data_schema.md |  84 +++++++++++++++++++++-----
     figures/phase_space_poster_figure.png         | Bin 302876 -> 500257 bytes
     figures/phase_space_poster_figure.svg         |   2 +-
     7 files changed, 115 insertions(+), 36 deletions(-)

The +5,916 / -356 figure reported across three prior rounds does NOT reproduce at this
commit. Live is 115 insertions, 36 deletions across 7 files. Nothing was stashed,
reverted, cleaned, committed or pushed to produce that number. Treat the earlier figure
as unexplained and probably measured with a different command or against a different
ref, not as a description of the current tree.

Concurrency note: the tree moved during this session. `poster.html`,
`Cerrell_TACC_42x56.pdf`, `figures/fig1_l1_three_class.svg`, `figures/traction_bias.svg`
and `figures/pipeline_diagram_poster.svg` appeared as new untracked files, and
`data/track1_sweep_v2/mpm_sweep_data_schema.md` became modified, between the Lane V pass
at 17:01 and this pass. Another lane is writing to this working tree concurrently.

Post-fix state, for comparison:

    data/scenario_sweep.csv                       |   8 +--
    data/track1_sweep_v2/mpm_sweep_data_schema.md |  84 +++++++++++++++++++++-----
    figures/phase_space_poster_figure.png         | Bin 302876 -> 500257 bytes
    figures/phase_space_poster_figure.svg         |   2 +-
    vehicle_params.py                             |   2 +-
     9 files changed, 120 insertions(+), 41 deletions(-)

Delta attributable to F2: `vehicle_params.py` 1 line, `data/scenario_sweep.csv` 4 rows.

## STEP 1: four-row verification, pre-fix

Command and output, verbatim:

    0.1 3.0 small_passenger 0.30000000000000004 cap 0.3 -> NO-FORD
    0.2 1.5 small_passenger 0.30000000000000004 cap 0.3 -> NO-FORD
    0.2 3.0 large_4wd 0.6000000000000001 cap 0.6 -> NO-FORD
    0.4 1.5 large_4wd 0.6000000000000001 cap 0.6 -> NO-FORD

Four NO-FORD where the stated inclusive rule gives FORD. Premise confirmed
independently of Lane V's numbers.

Post-fix, same command:

    0.1 3.0 small_passenger 0.30000000000000004 cap 0.3 -> FORD
    0.2 1.5 small_passenger 0.30000000000000004 cap 0.3 -> FORD
    0.2 3.0 large_4wd 0.6000000000000001 cap 0.6 -> FORD
    0.4 1.5 large_4wd 0.6000000000000001 cap 0.6 -> FORD

## STEP 2: figure impact, the reason this task existed

Consumer wiring, verified live:

- `analysis/plot_l1_three_class.py:59,82` read `L1_verdict_{c}` for all three classes.
  The figure therefore carries every per-class error.
- `analysis/build_poster_phase_space.py:8,30,35` read `GRID_CSV = data/scenario_sweep.csv`
  and consume only the single default-class `L1_verdict` column.

Counted cell by cell against a corrected reimplementation of the rule:

| Figure | Wrong cells | Which |
|---|---|---|
| `figures/fig1_l1_three_class.pdf` | **4** | 2 in the small_passenger panel (0.1/3.0 and 0.2/1.5), 2 in the large_4wd panel (0.2/3.0 and 0.4/1.5) |
| `figures/phase_space_poster_figure.svg` | **2** | both small_passenger (0.1/3.0 and 0.2/1.5) |

All four wrong cells fall exactly on the D*V = 0.30 and 0.60 threshold lines. Two
compute to 0.30, two compute to 0.60. That is the worst possible placement: the
threshold boundary is precisely what these figures are drawn to communicate, and every
error sat on it.

Both artifacts postdate the CSV they were built from, so both carry the defect:
`fig1_l1_three_class.pdf` mtime 2026-07-25 06:17, `phase_space_poster_figure.svg`
mtime 2026-07-25 07:23, `data/scenario_sweep.csv` was 2026-07-24 22:57.

## STEP 3: the fix, one line, one file

    diff --git a/vehicle_params.py b/vehicle_params.py
    index 15e3126..4a77ac4 100644
    --- a/vehicle_params.py
    +++ b/vehicle_params.py
    @@ -194,7 +194,7 @@ def L1_verdict(depth_m: float, velocity_ms: float, vehicle_class: str = "small_p
             return "NO-FORD"
         if velocity_ms > limits["velocity_ms"]:
             return "NO-FORD"
    -    if depth_m * velocity_ms > limits["haz_m2s"]:
    +    if round(depth_m * velocity_ms, 6) > limits["haz_m2s"]:
             return "NO-FORD"
         return "FORD"

No tolerance epsilon, no `Decimal`, no import added, no threshold VALUE changed,
`scripts/gen_scenario_sweep.py` untouched. Six decimal places is safe against the sweep
grid, which steps depth by 0.1 and velocity by 0.5; the smallest nonzero gap between a
product and a cap on that grid is 0.05, seven thousand times the rounding granularity.

COUPLED-VARIABLES RULE observed: box dimensions, particle density and mass were not
touched. This fix is confined to a verdict comparison and reaches none of them.

## STEP 4: CSV regeneration and audit

Backup taken to `/tmp/scenario_sweep_PREFIX.csv` before regenerating.

Generator stdout:

    Wrote 70 rows to /Users/josie/can-it-ford/data/scenario_sweep.csv
    L1_verdict column reflects vehicle_class=small_passenger
    23 rows changed verdict vs product-only baseline
    12 rows class-sensitive
      small_passenger: FORD=14
      large_passenger: FORD=19
      large_4wd: FORD=26

Diff, verbatim:

    8c8
    < 0.1,3.0,FORD,0.3,FORD,NO-FORD,NO-FORD,FORD,FORD,True
    ---
    > 0.1,3.0,FORD,0.3,FORD,FORD,FORD,FORD,FORD,False
    12c12
    < 0.2,1.5,NO-FORD,0.3,FORD,NO-FORD,NO-FORD,FORD,FORD,True
    ---
    > 0.2,1.5,NO-FORD,0.3,FORD,FORD,FORD,FORD,FORD,False
    15c15
    < 0.2,3.0,NO-FORD,0.6,FORD,NO-FORD,NO-FORD,NO-FORD,NO-FORD,False
    ---
    > 0.2,3.0,NO-FORD,0.6,FORD,NO-FORD,NO-FORD,NO-FORD,FORD,True
    26c26
    < 0.4,1.5,NO-FORD,0.6,FORD,NO-FORD,NO-FORD,NO-FORD,NO-FORD,False
    ---
    > 0.4,1.5,NO-FORD,0.6,FORD,NO-FORD,NO-FORD,NO-FORD,FORD,True

Exactly four rows: 8, 12, 15, 26. Gate checked programmatically, not by eye:

    rows with any verdict change: 4
    NO-FORD -> FORD transitions: 6
    FORD -> NO-FORD transitions: 0
    GATE PASS

Six cell transitions across four rows because rows 8 and 12 each move two columns
(`L1_verdict` and `L1_verdict_small_passenger`) while rows 15 and 26 each move one
(`L1_verdict_large_4wd`). Zero rows loosened in the disallowed direction.

The `L1_class_sensitive` flips are derived consequences, not verdict changes: rows 8
and 12 go True to False, rows 15 and 26 go False to True.

## STEP 4b: schema test

`python3 -m pytest tests/test_csv_schema.py -q` could not run:

    /opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest

`pandas`, which `tests/test_csv_schema.py:1` imports, is also absent. Rather than skip
the gate, both test functions' assertions were replicated in stdlib `csv` and executed:

    test_scenario_sweep_schema
      columns match expected: True
      depth_m all float: True
      velocity_ms all float: True
      L1_haz all float: True
      rows: 70

    test_l2_results_schema
      missing required columns: none

    SCHEMA GATE: PASS

The 10-column schema is intact. Recorded honestly: this is an equivalent stdlib
reimplementation of the assertions, not a pytest run. The pytest run remains blocked on
the same missing-environment problem as Step 6.

## STEP 5: tripwire, NOT updated, awaiting go

F0's design is correct and it will stop rather than silently redraw. Current hardcoded
values, verbatim:

    26	EXPECTED_FORD = {"small_passenger": 12, "large_passenger": 19, "large_4wd": 24}
    27	EXPECTED_SENSITIVE = 12
    28	EXPECTED_ROWS = 70

Counted from both CSVs directly:

| Key | Before | After | Change |
|---|---|---|---|
| small_passenger | 12 | 14 | 12 -> 14 |
| large_passenger | 19 | 19 | same |
| large_4wd | 24 | 26 | 24 -> 26 |
| SENSITIVE | 12 | 12 | same |
| ROWS | 70 | 70 | same |

F0's 12 / 19 / 24 / 12 was exactly right before the fix. Required change is line 26
only:

    EXPECTED_FORD = {"small_passenger": 14, "large_passenger": 19, "large_4wd": 26}

Lines 27 and 28 need no change.

Trap worth naming before anyone edits the caption. The class-sensitive COUNT is
unchanged at 12, so the narrative text at `plot_l1_three_class.py:175`
("Vehicle class decides the verdict in 12 of 70 scenarios") and the legend at line 193
("Hatched: class-sensitive (12)") both remain numerically correct and need no edit. But
the SET changed: rows 8 and 12 lost sensitivity, rows 15 and 26 gained it. Four hatched
cells move even though the number does not. Anyone checking only the "12" and concluding
the figure is unaffected would be wrong. The figure must still be redrawn.

The `[:12]` at line 217 is an md5 string slice, not a count. Do not touch it. There is
no hardcoded md5 in the `verify()` gate, so no provenance constant needs updating.

Nothing at lines 26-28 was edited and no figure was regenerated. Waiting on explicit go.

## STEP 6: environment reality check

No interpreter reachable from this shell has matplotlib.

- Default `python3` is `/opt/homebrew/bin/python3`, Python 3.14.6. No matplotlib, no
  pandas, no pytest.
- `/usr/bin/python3`: no matplotlib.
- `/opt/homebrew/bin/python3.13`: no matplotlib.
- `conda` resolves only to a shell function. `$CONDA_EXE` and `$CONDA_PREFIX` are both
  empty. No `~/miniforge3`, `~/miniconda3`, `~/anaconda3` or `~/mambaforge` exists.
- No `can-it-ford` conda env at either path checked.
- No `.venv`, `venv` or `env` in the repo.
- `find /Users/josie -maxdepth 3 -name matplotlib -type d` returns nothing.

F0's report is confirmed. Figure regeneration is blocked on the missing environment,
not on this fix. The fix itself is complete and verified at the data layer.

Unresolved discrepancy, flagged rather than guessed. `figures/fig1_l1_three_class.pdf`
carries this metadata:

    /Creator (Matplotlib v3.11.1, https://matplotlib.org)
    /Producer (Matplotlib pdf backend v3.11.1)

So a working Matplotlib 3.11.1 produced that PDF at 06:17 today, yet no matplotlib is
findable from this shell at bounded search depth. Either the producing environment lives
outside `/Users/josie` at depth 3, or the PDF was built elsewhere and transferred, or an
environment was removed between 06:17 and now. Not determined. Whoever regenerates the
figures needs to find that interpreter first, and it is worth knowing which, because the
figure must be reproducible for the paper.

## Named not guessed

Verified by live read or execution: both line-number corrections; the pre-fix and
post-fix four-row runs; the per-figure wrong-cell counts, computed cell by cell against
a corrected reimplementation rather than inferred; the CSV diff and the transition-
direction gate; the before and after tripwire counts, computed from both CSV files; every
negative result in Step 6; the fig1 PDF producer metadata.

NOT verified, do not restate as fact:

- Why `+5,916 / -356` was ever reported. It does not reproduce; the cause was not found.
- Where the Matplotlib 3.11.1 that built fig1 lives. Searched at bounded depth only.
- Whether `figures/fig1_l1_three_class.svg` and the other new untracked figures carry the
  same four wrong cells. They appeared mid-session from another lane and were not audited
  here. `fig1_l1_three_class.svg` almost certainly does, since it shares a generator with
  the PDF, but that was not checked.
- Whether any consumer outside the two named files reads the four changed rows. Out of
  scope by instruction; Lane V's map stands.
- Whether `poster.html`, which appeared mid-session, embeds any of the affected figures.

## What remains, in order

1. Get an interpreter with matplotlib. Everything below is blocked on it.
2. Apply the one-line tripwire change to `plot_l1_three_class.py:26`. Do not touch 27, 28,
   175, 193 or 217.
3. Regenerate `fig1_l1_three_class.pdf` and `.svg`, and `phase_space_poster_figure.svg`
   and `.png` via `build_poster_phase_space.py`.
4. Confirm the four cells moved and that the hatching relocated as described above.
5. Check whether `poster.html` embeds stale copies.
