# L1/L2 recompute under the corrected AR&R small-passenger rule

Produced 2026-07-25 by Lane P. Generator: `analysis/recompute_l1_l2.py`, read-only, edits nothing.
Interpreter: `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python`, 3.12.13.

## What this replaces

`paper_draft.md` section 4.1's divergence figures were produced by `analysis/make_phase_space_v2.py:9`:

    df['L1_verdict'] = df['L1_haz'].apply(lambda h: 'FORD' if h <= 0.60 else 'NO-FORD')

That is a bare depth-times-velocity product against a single 0.60 threshold, with no depth cap, no velocity cap, and no vehicle class. It is the Large 4WD product limit applied to a compact sedan.

This recompute does not edit that script and does not edit `paper_draft.md`. Lane V owns the paper.

## Result

| Quantity | OLD, section 4.1 | NEW, this run |
|---|---|---|
| Deduplicated conditions | 23 | 23 |
| Divergences | 14 | **6** |
| Agreement | 39.1 percent | **69.6 percent** |

Direction: **divergence decreased, agreement increased.** This matches the prediction derived from the 70-cell counts, and the mechanism is monotone: a strictly more conservative L1 can only convert DIVERGE into NOFORD_AGREE, never the reverse.

Full cross-tabulation, corrected L1 against L2:

| Cell | Count |
|---|---|
| FORD_AGREE, L2 FORD and L1 FORD | 2 |
| NOFORD_AGREE, L2 NO-FORD and L1 NO-FORD | 14 |
| DIVERGE, L2 NO-FORD and L1 FORD | 6 |
| REVERSE_DIVERGE, L2 FORD and L1 NO-FORD | 1 |
| Total | 23 |

## The finding nobody predicted, and it needs a decision

**REVERSE_DIVERGE is 1, not 0.** Section 4.1 currently states that every divergence runs in the same safety-critical direction, L1 permissive against L2 restrictive. Under the corrected rule that is no longer true: there is one condition where the corrected L1 returns NO-FORD while L2 returns FORD, meaning the abstraction is now stricter than the simulation.

That single row breaks the "every divergence runs one way" sentence in section 4.1. It does not weaken the headline, the headline gets stronger, but the sentence as written becomes false and must be revised by Lane V.

## Provenance of each verdict, stated per row rather than assumed

The two datasets only partially overlap, which was not previously recorded anywhere.

- **15 of 23 conditions: COLUMN-READ.** Matched by joining on `(depth_m, velocity_ms)` against `data/scenario_sweep.csv` and reading `L1_verdict_small_passenger`. No verdict recomputed.
- **8 of 23 conditions: RULE-APPLIED.** These conditions do not exist in the 70-cell grid at all, so no column could be read. The AR&R small-passenger rule was applied explicitly and the rows are labelled as such rather than silently dropped.

The 8 unmatched conditions and their applied verdicts:

| depth (m) | velocity (m/s) | applied verdict |
|---|---|---|
| 0.15 | 0.00 | FORD |
| 0.15 | 1.50 | FORD |
| 0.15 | 2.00 | FORD |
| 0.25 | 1.00 | FORD |
| 0.25 | 1.50 | NO-FORD |
| 0.35 | 1.00 | NO-FORD |
| 0.35 | 1.50 | NO-FORD |
| 0.45 | 1.50 | NO-FORD |

Rule, cited in the script's printed output rather than in a code comment: FORD only if depth <= 0.30 m AND velocity <= 3.0 m/s AND depth times velocity <= 0.30 m2/s. Source: Shand, Cox, Blacka and Smith 2011, AR&R Project 10 Stage 2, Report P10/S2/020, Table 3.

The grid uses depths 0.15 / 0.30 / 0.45 / 0.60 and the L2 pilot additionally ran 0.25 and 0.35 plus velocities 0.00 and 2.00. That mismatch is why a third of the conditions cannot be column-read, and it should be recorded as a limitation of any figure that overlays the two datasets.

## Inputs, verified at read time

- `data/phase_space_results.csv`, 31 raw rows, deduplicated on `(depth_m, velocity_ms)` keeping last, 23 surviving. Columns: `depth_m,velocity_ms,verdict,final_x_disp_m,final_y_disp_m,max_vel_ms`.
- `data/scenario_sweep.csv`, 70 data rows, 10 columns, 4524 bytes, mtime 2026-07-24 22:57.

## What this does not claim

It does not revalidate the L2 pilot itself. Those 23 conditions came from the SPH pilot on synthetic box geometry, and commit `af95d17` records that the generating script ran under a superseded vehicle mass. A corrected L1 compared against an unrevalidated L2 improves one side of the comparison only. The agreement figure moving from 39.1 to 69.6 percent is a statement about L1's implementation, not evidence that L2 is correct.
