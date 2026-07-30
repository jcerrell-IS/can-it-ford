---
name: v2-timeseries-no-velocity-cols
description: "v1/v2 sweep timeseries lack vx/vy/vz, so the rebuilt failure_modes.py cannot classify STUCK/SLIDE/TOPPLE/FLOAT on any existing run"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa34788-17cf-475b-8c0c-766cdb8cfdc7
  modified: 2026-07-20T23:06:45.825Z
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
