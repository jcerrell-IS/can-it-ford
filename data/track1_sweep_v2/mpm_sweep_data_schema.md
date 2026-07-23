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

- No per-frame velocity columns (vx, vy, vz). v2 stores final-state kinematics only, so
  `simulation/failure_modes.py` cannot classify SLIDE vs FLOAT from this manifest. The
  mode decomposition requires a regenerated sweep with per-frame velocities present.
- Retention for reported results: 24 density-plausible cells, further reduced to 21
  fully trustworthy after excluding 3 under-resolved single-layer pickup cells at
  depth 0.15 m. See paper_draft.md Section 4.3.
- vehicle_density_kgm3 is diagnostic, not an input. Do not read it as a prescribed
  material density.
