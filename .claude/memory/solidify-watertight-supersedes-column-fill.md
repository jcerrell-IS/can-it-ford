---
name: solidify-watertight-supersedes-column-fill
description: "solidify_watertight (ray parity) replaced solidify_columns; fill_ratio is 1.0023 not 2.17, rho is 310 not 143, and every 2.18x/7.71m3/143 figure in older notes is retired"
metadata:
  type: project
---

`solidify_columns` filled every (x,y) column floor to ceiling, bridging the ground clearance
and wheel wells shut. `solidify_watertight(mesh, h)` replaces it with exact vertical ray
parity: collect every z where the column axis crosses the surface, sort, fill only between
successive entry/exit pairs. It is live at
`/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py:88` and
`VehicleBody.solidify` dispatches to it when `mesh is not None and mesh.is_watertight`.
**It is still UNCOMMITTED** (HEAD is `fd390d6`, the file shows ` M`).

Measured live 2026-07-25 at n_grid=64, h=0.0736065 m, hull 3.542739 m3, on both Vista and
independently on the Mac, agreeing to the digit:

| path | N | solid volume | ratio | rho at 1100 kg |
|---|---|---|---|---|
| solidify_columns (retired) | 19303 | 7.698 m3 | 2.173 | 142.90 |
| solidify_watertight (live) | 8904 | 3.5509 m3 | 1.0023 | 309.78 |

**Why:** every number the project carried about vehicle volume, buoyancy bias and effective
density was a measurement of the retired algorithm. The "bridging biases the sim toward
floating, so NO-FLOAT survives the defect" argument is now moot: `veh_z_min` rise is
0.000000 m, no float is live at all.

**How to apply:** if you see fill_ratio 2.17 or 2.18, over-fill 7.71 m3 or 8.55 m3, or
density 143 kg/m3 or 128.69 kg/m3, you are reading a retired-path number. Correct it, do not
propagate it. Two consequences that are easy to miss:

1. **The ratio gate now passes at every resolution.** Re-derived at n_grid 32/48/64/96/128/192:
   ratio 1.0698 / 1.0262 / 1.0023 / 0.9942 / 1.0013 / 1.0012. F0's "no n_grid passes the band,
   raising n_grid still forbidden" measured the function and concluded about the vehicle. It
   is retired; see the correction block appended to
   `.claude/handoffs/2026-07-25_ford-F0-gridgate.md`.
2. **Raising n_grid is now the fix for the 4-layer water limitation.** Layers go 4 -> 6 -> 8 -> 12
   at n_grid 64 -> 96 -> 128 -> 192 with volume error staying inside 0.6 percent.
3. **The 100-300 kg/m3 plausibility band is now the wrong thing.** Correct density is
   1100 / 3.5427 = 310.5, above the band. The band was only ever satisfied because the
   over-fill diluted density. Widen or restate the band; do not adjust the vehicle to
   re-enter it.

Related: [[v2-geometry-warped-invalid]], [[l1-l2-divergence-is-class-dependent]].
