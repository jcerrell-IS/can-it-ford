---
name: v2-timeseries-no-velocity-cols
description: "v1/v2 sweep timeseries lack vx/vy/vz so failure_modes.py cannot classify them, BUT the yaris_render_s1 17-run set does have velocity and was classified on 2026-07-31"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa34788-17cf-475b-8c0c-766cdb8cfdc7
  modified: 2026-07-31T07:12:13.390Z
---

Both `data/track1_sweep_v1/` and `data/track1_sweep_v2/` timeseries CSVs have header
`t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg` only. No velocity columns.

The rebuilt failure-mode classifier `simulation/failure_modes.py` (commit 846b970, Jul 20)
declares `REQUIRED_COLUMNS = ("t","dx","dy","dz","vx","vy","vz")` and raises
`MissingKinematicsError` ("Regenerate the run") on every row lacking vx/vy/vz. Verified
2026-07-20: `classify_manifest('data/track1_sweep_v2/manifest.csv')` returns 36 rows, 0
classified, 36 errored.

Consequence: any request to "overlay failure mode (STUCK/SLIDE/TOPPLE/FLOAT) from
failure_modes.py" onto v2 (e.g. the phase-space poster figure) is BLOCKED until the sweep
is regenerated on Vista with FloodHistory velocity columns. The manifest alone (final_disp_m,
final_yaw_deg, final_roll_deg) supports only binary FORD/NO-FORD, not the four failure modes.
Do not fake it by finite-differencing dx/dy/dz: double-differentiation for the accel-based
TOPPLE mode is noise-dominated and violates the classifier's explicit contract.

**SCOPE CORRECTION, verified live 2026-07-31.** The block above is real but applies ONLY to
`data/track1_sweep_v1/` and `data/track1_sweep_v2/`. It does NOT apply to the 17-run
`renders/yaris_render_s1/_incoming/*/metrics.csv` set, whose header is
`t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg,vx,vy,vz,vmag,wx,wy,wz` (91 rows, frames 0-90,
present for all 17 runs). Velocity IS there. Do not cite this memory to declare failure-mode
classification blocked in general.

That set was classified on branch `analysis/failure-modes` (commit 1206091): 15 SLIDE,
2 TOPPLE, 0 STUCK, 0 FLOAT. Two things learned there that outlive the classification:
FLOAT is unmeasurable in that set because `C2_veh_zmin_final` equals `3*dx` in all 17 runs
to within 4e-08 m (the solver's inward domain padding pins the vehicle base to the floor),
and 5 of the 17 runs have not converged by frame 90, re-accelerating at truncation, so their
`final_disp_mag_m` understates the peak excursion by 8.3% to 24.9%. See
[[l1-l2-divergence-is-class-dependent]].
