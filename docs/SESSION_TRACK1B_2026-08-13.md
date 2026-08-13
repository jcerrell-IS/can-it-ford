# Track 1B session, 2026-08-13, LS6

Clone `$SCRATCH/canitford_track1b/can-it-ford`, fresh from `origin/main` at `7453c92`.
GPU work ran on LS6 A100 node `c301-003` inside allocation 3362208.

## What this session was asked to do, and what was actually true

The prompt set rung (b) of the coupling ladder as the single highest-value open item and
budgeted about a GPU-hour for it, on the premise that it was **the untested rung**. That
premise was stale by roughly twelve hours. Before running anything, a live check of
`sacct` and the register showed **five GPU jobs had already been spent on rung (b)**:

| job | what | state |
|-----|------|-------|
| 3361315 | rung (b) first run, g64 + g96 | COMPLETED, failed, root-caused |
| 3361371 | under-relaxation sweep | COMPLETED, refuted added-mass as cause |
| 3361423 | fixed-pose wrench diagnostic | COMPLETED |
| 3361443 | gated-settle rerun, "the decisive test" | COMPLETED 18:22, **never analysed** |
| 3361504 | pressure probe | COMPLETED 18:28, analysed but unpushed |

Job 3361443 finished 19 minutes AFTER the last commit that describes it was written,
which is why the register still called it "SUBMITTED and PENDING".

## The most urgent finding had nothing to do with physics

**The evidence for four GPU jobs existed on exactly one clone and was unpushed.**
`/work/11603/jcerrell0629/vista/can-it-ford` was 8 commits ahead and 166 behind
`origin/main`, with a dirty working tree. `origin/main` carried the prose ABOUT those
jobs (`6434258`, `ca9bdeb`, `d98837f`, `be20075`) while every result JSON those commits
cite was absent from the repo.

Actions taken, in order:
1. `git bundle` of the 8 unpushed commits to
   `$SCRATCH/rungb_unpushed_backup_2026-08-13.bundle`, verified, before touching anything.
2. Recovered the 26 irreplaceable artifact and driver files as pure additions in
   `8695539`. No existing path was touched, so no conflict was possible.
3. `realism_track/FINDINGS.md` had diverged on both clones from a shared base
   (`02f08eb` byte-identical to `cdcdf9d`, sha256 `185968e0`). Resolved by genuine
   three-way merge: **496 insertions, 0 deletions**, with a RECONCILIATION SEAM section
   recording which narrative supersedes which and what remains unreconciled.

Recorded as register item **J1c**. A commit is not a backup.

## The GPU result: rung (b) now has four valid measurements

The one thing genuinely blocking rung (b) was that **both g96 runs in job 3361443 were
self-declared discards**, `settle_gate_met false` at the 900-frame cap, so the controlled
refinement pair the rung exists to produce did not exist.

Job 3362208 re-ran g96 with the cap raised 900 to 3000 and nothing else changed. The gate
is met at **1030 frames (coupled)** and **1031 (fixed)**. The 900-frame cap was about
13 percent short. Not a property of g96, a property of the cap.

All four rows below are `settle_gate_met true`, scored against
`F_buoy_analytic_partial_N`, the correct reference for a partially submerged body:

| grid | mode | frames | frac_sub | err vs partial |
|------|---------|--------|----------|----------------|
| 64 | coupled | 353 | 0.7540 | -25.21 % |
| 64 | fixed | 353 | 0.7548 | -49.92 % |
| 96 | coupled | 1030 | 0.8437 | -29.64 % |
| 96 | fixed | 1031 | 0.8445 | -32.51 % |

**Two things follow.**

The divergence signature is gone. The unsettled pair read -18.9 percent at g64 and
+115.0 percent at g96 and was read as divergence. Settled, it is -25.21 and -29.64:
same sign, 4.4 points apart. The sign flip came from settling two grids for different
physical durations.

**Fixed and coupled converge under refinement**, 24.71 points apart at g64 and 2.87
points apart at g96. A deficit that both an SDF-fixed collider and a free-rigid
force-coupled body reproduce to within 2.9 points at the finer grid is **not primarily an
artifact of the free-rigid coupling**. At g64 the framing is actually backwards: the
fixed collider is the worse of the two by 24.7 points.

Not established, and stated so the entry is not over-read: the pair is confounded,
realized submersion is 0.754 at g64 against 0.844 at g96, so a clean refinement test at
matched submersion has not been run. And the deficits as pressure (2747, 5444, 3613,
3967 Pa) are not the resolution-independent constant the job-3361504 offset model
predicts, nor its roughly 6.2 kPa. That discrepancy is open.

Recorded as register item **J1b**.

## The matched-submersion follow-up, which reversed the mechanism

The four-row result above carries an explicit confound: realized submersion moves with
the grid (0.754 at g64, 0.844 at g96). With allocation time left, that confound was
removed by varying submersion with `--depth-cells` at fixed grid. Ten gate-met points.

Fitting the g64 rows against submersion and evaluating at each g96 row's realized
submersion isolates grid as the only remaining difference:

| mode | at frac | g64 interpolates | g96 measures | grid gap |
|------|---------|------------------|--------------|----------|
| coupled | 0.7800 | -26.47 % | -24.96 % | **1.51 pts** |
| coupled | 0.8437 | -29.54 % | -29.64 % | **0.10 pts** |
| fixed | 0.7757 | -48.95 % | -29.88 % | **19.07 pts** |
| fixed | 0.8445 | -45.76 % | -32.51 % | **13.25 pts** |

**The force-coupled path is grid-converged between g64 and g96. The fixed SDF collider
is not, by 13 to 19 points.**

This corrects the mechanism reported earlier in this same session. The coupled path does
NOT degrade under refinement; that was the confound. The convergence between the two
paths at g96 is real, but the fixed collider is converging toward the coupled path's
already-stable value, not both meeting at a shared answer.

It does not say the coupled path is correct: it carries a residual deficit of about -25
percent at frac 0.78 rising to about -30 percent at frac 0.86. It says that deficit is
grid-converged, so a finer grid will not remove it, and that the ladder's working framing
(coupled broken, fixed collider trustworthy) is reversed at partial submersion on the
grid-convergence criterion.

Driver property worth knowing: **submersion is quantized.** `--depth-cells` 18.78 and
18.89 both realize frac 0.856 to 0.857 because water seeds in whole layers. The two
near-duplicate g64 rows act as a repeat measurement and agree to 0.04 and 0.06 points,
bounding run-to-run scatter far below every gap above.

Register item **J1d**.

## STEP 6, Rogue and Silverado grid sweep, non-canonical

`data/rogue_silverado_grid_sweep_2026-08-13.csv`, 8 rows. Nothing was written to
`data/all_runs_inventory.csv` or `gates_results_all_runs.json`, per register Part 2.7.

Matched to the canonical Yaris point behind the 17 gated runs: `--depth 0.30
--velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55`. Masses are the ones the
existing g64 runs used, Rogue 1571.3 (WEB-SOURCED, the Rogue deck states no mass) and
Silverado 2270.0 (deck header, primary), not the registry AR&R defaults of 1609 / 2337.
Hull tripwire passed on every run: `yaris_ref_delta_pct` +39.732 and +124.744.

| vehicle | g64 | g96 | g128 |
|---------|-----|-----|------|
| Rogue passthrough | 9.951 % | 10.716 % | 9.876 % |
| Silverado passthrough | 8.362 % | 8.950 % | 9.679 % |
| Rogue displacement | 0.7118 m | 0.5686 m | 0.2477 m |
| Silverado displacement | 0.3462 m | 0.0905 m | 0.0763 m |

**Answer to the question as posed: no. P-2 passthrough does not improve with resolution
for either hull.** Silverado worsens monotonically, 8.36 to 9.68. Rogue is non-monotonic
and ends where it started.

**A correction to the question's premise.** It cited Yaris improving "7.99 % to 15.88 %,
reversing direction at high speed". Those two numbers are the **velocity** sweep
(`sweepV_g64_v0p5` to `v3p0`), not a resolution sweep. Yaris passthrough against
resolution at fixed mass is non-monotonic in all three mass series: 10.05 / 10.67 / 9.69
(m1100), 9.34 / 9.74 / 8.93 (m1609), 9.10 / 7.34 / 8.24 (m2337) at g48 / g64 / g96. So
there is no "partial improvement with resolution" baseline for Yaris to compare against.

**The larger effect is displacement, not passthrough.** Both hulls lose most of their
motion under refinement: Rogue 0.71 to 0.25 m (65 percent), Silverado 0.35 to 0.076 m
(78 percent). Against the classifier's `slide_m` threshold of 0.05 m
(`simulation/failure_modes.py:48`), Silverado's margin falls from 6.9x to 1.5x. This is
indicative only: `final_disp_mag_m` is a total magnitude, whereas the classifier keys on
downstream surge drift with a sustained speed condition, and **the classifier was not
re-run on these rollouts**. Doing so is the obvious next step.

**Cross-machine reproduction, a free result.** The g64 rows were run on both the Vista
GH200 (job 896273, 2026-08-07) and the LS6 A100 this session. Seeding is bit-identical:
`n_vehicle`, `n_water`, `hull_m3` and `realized_rho` match exactly. Dynamics diverge over
90 frames by 0.020 to 0.388 percent in passthrough and 0.115 to 1.021 percent in
displacement. Same-machine determinism does not imply cross-machine determinism, and the
gap is about 1 percent for this pipeline.

## STEP 5, verified live rather than from the commit message

`e495b56` landed. Checked against the live artifacts, not the prose:
`simulation/failure_modes.py:14` is `G = 9.81`; `data/failure_modes_by_run_classified.csv`
has 17 rows, **16 SLIDE / 1 STUCK**; `triggered_topple` is true in **0 of 17**;
`ratio_topple >= 1` in **12**, matching the corrected count and not the stale 13. So
16 SLIDE / 1 STUCK is validated against the solver's own precision.

## Environment notes for the next LS6 session

- The warpmpm venv already exists at `$SCRATCH/warpmpm_ls6_env`, warp 1.12.1, torch
  2.8.0+cu128. No first-time setup was needed, contrary to the prompt's expectation.
- `trimesh` was MISSING from it and `sim_standing.py` needs it. Installed this session
  with `--no-deps`, deliberately, so numpy would not be upgraded under a running job.
- **Two `mpm-engine` trees exist on /work and they are not interchangeable.**
  `vista/can-it-ford/mpm-engine` is what the rung-b coupling work uses; its
  `warpmpm.vehicle` has **no `solidify_watertight`**, so `sim_standing.py` fails on it.
  `vista/mpm-engine` has it and is the one the g64 anchor runs resolved to. Use
  `vista/mpm-engine/src` for anything touching `sim_standing.py`.
- First import on a compute node took about 8 minutes, cold Lustre cache. This reads
  exactly like a hang. Register K2 already says this; it applies to this venv too.
- `gpu-a100-dev` enforces **QOSMaxJobsPerUserLimit = 1 running job**. A second idev sits
  PENDING behind the first for its full 2 hours. Two panes each opening an idev will
  starve one of them.

## Open, carried forward

1. DONE this session, see J1d. The matched-submersion test ran and reversed J1b's
   mechanism.
2. The pressure discrepancy: force-residual deficits (2747 to 5444 Pa, grid-dependent)
   against the direct probe's roughly 6.2 kPa resolution-independent offset.
3. Re-run the failure-mode classifier on the Rogue/Silverado rollouts, since displacement
   falls 65 to 78 percent under refinement and the SLIDE margin narrows sharply.
4. Rungs (c) floor contact and (d) flow, still unattempted.
5. `FINDINGS.md` is merged but still two voices. The seam says so explicitly.
