# Track 1 MPM Sweep, v2 manifest.csv schema

Column contract for `data/track1_sweep_v2/manifest.csv`. Generated from the live file
header and verified against actual row values on 2026-07-22. One row per swept cell.

Grid: 3 vehicle classes x 4 depths x 3 velocities = 36 rows. Solver: kks32/mpm-engine
MPM, n_grid = 64. This is the Track 1 box-proxy sweep, not the Genesis SPH pilot.

## Columns (23, in file order)

| # | Column | Type | Unit | Description |
|---|---|---|---|---|
| 1 | run_id | string | none | Unique cell id, e.g. `veh-sedan_dep-0p15_vel-1p00_idx-0000`. Encodes class, depth, velocity, index. |
| 2 | vehicle_class | string | none | One of `sedan`, `pickup`, `suv`. |
| 3 | params_class | string | none | Parameter-set key: `compact_sedan`, `light_pickup`, `midsize_suv`. |
| 4 | bbox_l_m | float | m | Nominal spec bounding-box length (sedan 4.66, pickup varies, suv 4.96). |
| 5 | bbox_w_m | float | m | Nominal spec bounding-box width. |
| 6 | bbox_h_m | float | m | Nominal spec bounding-box height. |
| 7 | fitted_extent_x_m | float | m | Fitted proxy extent along sim x (lateral). Note x carries the width, e.g. 1.79 for the sedan. |
| 8 | fitted_extent_y_m | float | m | Fitted proxy extent along sim y (downstream/length), e.g. 4.66 for the sedan. |
| 9 | fitted_extent_z_m | float | m | Fitted proxy extent along sim z (vertical/height). |
| 10 | vehicle_mass_kg | float | kg | Class curb mass. sedan 1390.0, suv 1990.0, pickup 2300.0. From manufacturer specs + NHTSA/SAE inertial database. |
| 11 | solid_volume_m3 | float | m3 | Solidified particle volume of the proxy (sedan 4.7352, suv 6.4583). |
| 12 | vehicle_density_kgm3 | float | kg/m3 | Derived post hoc: vehicle_mass_kg / solid_volume_m3. Plausibility check only, not prescribed. |
| 13 | density_plausible | bool | none | `True` if vehicle_density_kgm3 in [100, 300]. All 12 suv rows are `False` (308.13, 2.7% over band); all sedan and pickup rows `True`. 24 True / 12 False. |
| 14 | depth_m | float | m | Still-water / inflow depth. One of 0.15, 0.30, 0.45, 0.60. |
| 15 | velocity_ms | float | m/s | Target flow velocity. One of 1.0, 1.5, 2.0. |
| 16 | depth_velocity_m2ps | float | m2/s | Product depth_m x velocity_ms, the AR&R hazard index (D times V). |
| 17 | n_grid | int | none | MPM background grid resolution. 64 for every row in v2. |
| 18 | frames_used | int | none | Simulation frames retained for the final-state read (90 in sampled rows). |
| 19 | plateaued_ok | bool | none | `True` if displacement plateaued within the run window (convergence sanity flag). |
| 20 | final_disp_m | float | m | Final downstream displacement, the primary v2 outcome. Range 0.0197 (under-resolved pickup) to 1.83 (pickup 0.60/2.0). |
| 21 | final_yaw_deg | float | deg | Final yaw angle of the proxy. |
| 22 | final_roll_deg | float | deg | Final roll angle of the proxy. |
| 23 | elapsed_s | float | s | Wall-clock runtime of the cell. |

## Known limitations of this schema

### CONFIRMED BLOCKING: no failure-mode classification is possible from this sweep

Status: confirmed finding, not a suspicion. First reproduced 2026-07-23, re-verified
against the live files 2026-07-25. 36 of 36 rows rejected, 0 classifiable.

What the FloodScene sweep writes. Every cell is produced by
`scripts/ford_sweep_driver.py`, which imports `FloodScene` from `warpmpm.vehicle`
(line 169) and persists the run with `history.to_csv(...)` (line 243). That writer emits
exactly one header for every cell:

    t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg

Verified live 2026-07-25: all 36 `{run_id}_timeseries.csv` files in this directory exist,
and `sort -u` over their header rows returns that single line, no variants.

What the classifier demands. `simulation/failure_modes.py` sets
`REQUIRED_COLUMNS = ("t", "dx", "dy", "dz", "vx", "vy", "vz")` at line 20, and
`load_timeseries()` gates on it at lines 106 to 111 before any physics runs.

The rejection. Every one of the 36 manifest rows resolves to an existing timeseries file,
so this is NOT a "timeseries missing" failure. Each file then fails the kinematics gate
with an identical missing set, `['vx', 'vy', 'vz']`, and `classify_manifest()` records the
classifier's own message per row:

    missing ['vx', 'vy', 'vz']. This timeseries predates the FloodHistory.to_csv
    velocity columns; net force cannot be computed from it. Regenerate the run.

Counts, reproduced 2026-07-25 over `manifest.csv` plus all sibling timeseries: 36 rows in,
0 timeseries missing on disk, 36 rejected at the `REQUIRED_COLUMNS` gate, 0 reaching
`classify_kinematics()`. `get_vehicle()` resolves `compact_sedan`, `light_pickup`, and
`midsize_suv` and each carries an `ssf`, so the classifier does not die earlier for an
unrelated reason: it reaches the kinematics gate and is turned away there.

Downstream consequence. Zero STUCK / SLIDE / TOPPLE / FLOAT verdicts exist for this
sweep. `final_disp_m`, `final_yaw_deg`, and `final_roll_deg` (columns 20 to 22) are
end-state scalars, not a failure-mode label, and cannot be substituted for one. No
failure-mode result from v2 can go on the poster or in the paper.

### The data is captured but discarded at write time

Sharpening the above, from `citations/vehicle(kks32).py` (the local copy of the writer):
`FloodHistory.append()` already stores per-frame linear velocity and angular velocity,
`self.v.append(state["v"])` and `self.omega.append(state["omega"])` at lines 207 to 208,
and `arrays()` exposes both at lines 217 to 218. `to_csv()` at lines 221 to 227 then
column-stacks only t, displacement, displacement magnitude, and the three Euler angles,
so v and omega are dropped on the way to disk.

This is a writer-side omission of already-computed state, not missing instrumentation.
The velocity was in memory during every one of the 36 runs and was never persisted.

Caveat on what was checked where: `warpmpm` is not installed on the Mac, so the deployed
module was not read directly. The evidence that the deployed writer matches this copy is
that the header string literal at line 226 is byte-identical to the header found in all 36
files on disk.

### CONCRETE UNBLOCK

1. Extend `FloodHistory.to_csv` to emit `vx,vy,vz` from `arrays()["v"]`. Emit `wx,wy,wz`
   from `arrays()["omega"]` in the same edit: those are the classifier's optional
   `OMEGA_COLUMNS` (line 21), they are absent from all 36 current files, and without them
   `kinematics_from_columns()` silently substitutes a zero omega array. Adding them costs
   nothing now and avoids a second re-run later.
2. Re-run all 36 cells. The fix is not retroactive: the existing files cannot be repaired,
   because the velocity was never written.

Adding columns to this `manifest.csv` does not help. The classifier reads the per-run
timeseries, not the manifest. This is the single change that unblocks failure-mode
classification, and nothing else in the pipeline has to move for it.

### Other limitations
- Retention for reported results: 24 density-plausible cells, further reduced to 21
  fully trustworthy after excluding 3 under-resolved single-layer pickup cells at
  depth 0.15 m. See paper_draft.md Section 4.3.
- vehicle_density_kgm3 is diagnostic, not an input. Do not read it as a prescribed
  material density.
