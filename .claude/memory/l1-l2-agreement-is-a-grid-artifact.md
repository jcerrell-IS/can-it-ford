---
name: l1-l2-agreement-is-a-grid-artifact
description: "Pooled, no drift threshold reconciles L1 and L2; but every single grid resolution has a perfect window and they are disjoint, so the divergence is a convergence artifact, not structural"
metadata: 
  node_type: memory
  type: project
  originSessionId: ff3e23b3-414c-4170-9c56-227f34213640
  modified: 2026-07-31T07:12:27.449Z
---

Verified 2026-07-31 on branch `analysis/failure-modes` (commit 1206091), reproducible with
`analysis/paper_fig_threshold_sensitivity.py`.

Matching the 17-run MPM sweep to the 70-scenario L1 grid on exact (depth, velocity) gives
**14 matches**, covering only **6 distinct cells, all at 0.30 m depth**. The 3 unmatched runs
sit at 0.25/0.35/0.45 m, which are off the 0.1 m scenario grid. Nine of the 14 are the same
cell (0.30, 1.5) differing only in mass and grid.

**Pooled:** no threshold makes L1 and L2 fully agree. Peak agreement 92.9% at t in
[0.26, 0.35] m; 42.9% at the paper's 0.05 m. Survives using peak drift instead of final.

**Stratified by n_grid, the result reverses.** A fully-agreeing window exists at EVERY
resolution, and the windows are pairwise disjoint:

| n_grid | n | full-agreement window (m) |
|---|---|---|
| 48 | 3 | [0.2568, 0.3507) |
| 64 | 8 | [0.3141, 0.6585) |
| 96 | 3 | [0.1560, 0.2686) |

So within any single resolution, simulated drift orders the conditions exactly as the L1
hazard product does. **The pooled disagreement is entirely resolution scatter.** At fixed
physics (D=0.30, V=1.5) drift varies 2.0x to 2.5x across the three grids, and
non-monotonically for 1100 kg (g48 0.3507, g64 0.6585, g96 0.2686). The windows are not
ordered in n_grid either. There is no sign of convergence across the three resolutions run.

**Why this matters:** do NOT write a structural L1/L2 divergence claim from this dataset. It
is contradicted by the stratification, and a reviewer who stratifies will find it in one
step. What the data supports is a grid-convergence limitation. Fixing it needs a refinement
study, not a reinterpretation of the ladder. This is the reason the failure-modes work was
NOT recommended for the paper. See [[l1-l2-divergence-is-class-dependent]] and
[[v2-timeseries-no-velocity-cols]].
