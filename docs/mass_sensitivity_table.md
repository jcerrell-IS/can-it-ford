# Mass sensitivity at fixed Yaris geometry, L0 / L1 / L2

Supersedes `figures/three_class_table.md`, which is withdrawn: it used the word "class" for
rows that differ only in mass, and it reported a scenario now known to be the wrong one.

Generated 2026-07-25 from `renders/yaris_render_s1/g64_m*/summary.json`. Sims: Vista job
866266 reused via `srun --overlap`, node c642-001, GH200 120GB, exit 0 on all three.

## THE WORD "CLASS" IS NOT USED FOR THESE ROWS, AND HERE IS WHY

All three runs use the SAME 2010 Toyota Yaris hull. Only `--vehicle-mass` varies. Read live
from `vehicle_params.py:166`, AR&R classes are defined on THREE axes, not one:

| class | length (m) | kerb (kg) | ground clearance (m) |
|---|---|---|---|
| small_passenger | <= 4.3 | <= 1250 | <= 0.12 |
| large_passenger | >= 4.3 | >= 1250 | >= 0.12 |
| large_4wd | >= 4.5 | >= 2000 | >= 0.22 |

The Yaris hull is 4.2826 m long with Yaris ground clearance. The 2337 kg row therefore
violates `large_4wd` on length (4.28 < 4.5) AND on ground clearance, and clearance is the
dominant fording variable because it sets when the underbody starts taking load. The 1609 kg
row violates `large_passenger` on length by the same 0.017 m margin the Yaris clears
`small_passenger` by.

This also violates the project's own coupled-variables rule (CLAUDE.md: box dimensions,
density and mass move together or not at all). Three times. It is reported as a mass
sensitivity study, which is what it is, and NOT as a class comparison. The word "class" may
not appear unqualified for these rows until V2 real meshes exist.

## Effective density against the engine's own stated band

Quoted verbatim from the `FloodScene` docstring in `src/warpmpm/vehicle.py`:

> vehicle_density is the body's effective density (vehicles are mostly air; a car is
> roughly 100 to 300 kg/m^3 spread over its volume, which is why they float)

| mass (kg) | solid volume (m3) | realized_rho (kg/m3) | plausible vs 100-300 band |
|---|---|---|---|
| 1100 | 3.55138 | 309.74 | **NO, above** |
| 1609 | 3.55138 | 453.06 | **NO, far above** |
| 2337 | 3.55138 | 658.05 | **NO, far above** |

Even the physically correct 1100 kg Yaris is above the band, at 309.74. The band was only
ever satisfied by the retired `solidify_columns` over-fill, which diluted density to
142.90. The 1609 and 2337 rows are 1.5x and 2.2x outside it, which is the quantitative
statement of why they are not real vehicles: a 2337 kg body compressed into a Yaris hull is
not a Silverado, it is a Yaris made of something much denser than a car.

## The scenario was wrong, and fixing it changed the answer by up to 7x

The earlier runs spawned the water slab upstream with a **0.29 m dry gap** by construction
(`x1 = vx + particles[:,0].min() - 2*dx`), so they modelled a wave striking a dry parked car
in a sealed box, then draining. That is not fording, and it is not what AR&R Table 3
measures (stationary vehicle, sustained flow, water already present). Both errors biased the
same way, so those displacements were lower bounds.

Corrected scenario: water spans the full domain wall to wall, water particles occupying
vehicle solid cells are carved out by exact lattice occupancy (917 of 49284, 1.86 percent),
the car sits in water at depth D from t=0, and upstream velocity is re-imposed each frame in
the first 1.5 m of x.

| mass (kg) | dry-start abs d (m) | standing-water abs d (m) | ratio |
|---|---|---|---|
| 1100 | 0.09240 | **0.65854** | 7.13x |
| 1609 | 0.05110 | **0.31408** | 6.15x |
| 2337 | 0.03890 | **0.13556** | 3.49x |

## L0 / L1 / L2, all three rungs

L0 is the static NWS depth threshold. Inferred live from `data/scenario_sweep.csv`:
`L0_verdict` is FORD at depth 0.10 m and NO-FORD at every depth from 0.20 m up, so the
threshold sits between them (the project's stated value is roughly 0.15 m). At the 0.30 m
operating point L0 returns NO-FORD for every row.

| mass (kg) | L0 (0.30 m) | L1 nominal (DxV 0.45) | L2 standing water | L0 vs L2 | L1 vs L2 |
|---|---|---|---|---|---|
| 1100 | NO-FORD | NO-FORD | NO-FORD (0.659 m) | AGREE | AGREE |
| 1609 | NO-FORD | FORD | NO-FORD (0.314 m) | AGREE | **DIVERGE** |
| 2337 | NO-FORD | FORD | NO-FORD (0.136 m) | AGREE | **DIVERGE** |

**This is the finding.** With the correct scenario, L0 and L2 agree on all three rows and
**L1 is the divergent rung**, diverging on two rows out of three. The earlier report that L1
and L2 agreed was an artifact of the dry-start scenario suppressing displacement into the
same range as the threshold.

## The knife-edge is gone, and that is itself the result

At the dry-start operating point both middle verdicts sat on a knife edge: D x V = 0.45
exactly against a large_passenger hazard limit of 0.45 (FORD only because commit 63e677f
made the bound inclusive), and L2 at 0.0511 m against a 0.05 m threshold, 1.1 mm past. Two
binary verdicts decided by zero and by one millimetre.

Under the corrected scenario the L2 side is no longer marginal: 0.659, 0.314 and 0.136 m are
13x, 6.3x and 2.7x the threshold. The L1 side is still exactly on its bound. So the
remaining knife-edge is entirely in L1, not in the physics.

Report `abs d` continuous in cm as the primary quantity. DRIFT_THRESHOLD 0.05 m must be drawn
as a **shaded band, never a line**, labelled: "conservative numerical onset-of-motion
detector, uncited as a distance criterion, underlying physics Xia 2010 and Shah 2018."

## Failure modes, wired from the vx/vy/vz/wx/wy/wz columns

Classifier `simulation/failure_modes.py`, SSF 1.42 from `vehicle_params.py:108`, which the
file itself labels an ESTIMATE, not NHTSA-measured, with the comment "CONFIRM before use".

| mass (kg) | mode | first reached | margin past criterion |
|---|---|---|---|
| 1100 | **SLIDE** | frame 3, t = 0.1000 s | +1230.68 percent (615.3 mm past 0.05 m) |
| 1609 | **SLIDE** | frame 3, t = 0.1000 s | +542.87 percent (271.4 mm past 0.05 m) |
| 2337 | **SLIDE** | frame 4, t = 0.1333 s | +183.93 percent (91.96 mm past 0.05 m) |

Citations: SLIDE Xia et al. 2010 (drag >= friction), TOPPLE Xia et al. 2013, FLOAT Kramer et
al. 2016 (DOI 10.1016/j.ijdrr.2016.04.003). STUCK is the stable baseline, not a fourth mode.

**Modes that did NOT activate, which is a result and is stated as one:**
- **TOPPLE did not activate** in any run. Final roll is -0.0029, -0.0015 and +0.0007 deg,
  three to four orders of magnitude below any overturning angle.
- **FLOAT did not activate** in any run. `veh_z_min` rise is -0.0071, -0.0036 and 0.0000 m.
  All three are negative or zero, meaning the body settled onto the floor rather than
  lifting off it. At a realized density of 309.74 kg/m3 in 0.30 m of water the body is
  nowhere near neutral buoyancy.
- **STUCK is not the outcome** for any row; all three slid within 4 frames.

This is the first time the classifier has run on any data in this project. It was blocked
until now because v1/v2 timeseries lacked velocity columns.

## Depths, never conflated, two distinct probes

| mass (kg) | nominal slab | bow-wave probe peak | bow-wave final | footprint probe peak | footprint final |
|---|---|---|---|---|---|
| 1100 | 0.3000 | 0.3958 (frame 50) | 0.2279 | 0.3750 | 0.3298 |
| 1609 | 0.3000 | 0.4436 (frame 35) | 0.2332 | 0.3830 | 0.3221 |
| 2337 | 0.3000 | 0.4742 (frame 24) | 0.2281 | 0.2987 | 0.2761 |

The two probes are different instruments and must not be conflated. Bow-wave probe: 3 dx to
0.5 dx upstream of the vehicle's minimum-x face, across its y extent, 99.5th percentile of
water z above the floor. Footprint probe: water inside the vehicle's xy bounding box, same
percentile. The same physics reads 0.3958 and 0.3750 through the two probes at 1100 kg.
Full per-frame arrays for both are stored in `rollout.npz` as `local_depth_bow` and
`local_depth_footprint`.

## Numerics, measured not asserted

Substep terms at dx = 0.147215 m, printed by the driver:

| term | formula | eta = 1.0 (old default) | eta = 1.0e-3 (corrected) |
|---|---|---|---|
| acoustic | c / (0.28 dx) | 311.6253 | **311.6253** |
| viscous | 6 eta / (rho dx^2) | 0.2769 | **0.000277** |
| advective | v / (0.5 dx) | 20.3784 | **20.3784** |
| rate = max | | 311.6253 | 311.6253 |
| substeps = ceil(rate/fps) | | 11 | **11** |

Acoustic binds in both cases, so correcting water viscosity from the silently defaulted
1.0 Pa s (1000x too viscous) to the real 1.0e-3 Pa s costs **exactly zero** extra substeps.
Measured, not assumed. `floor_friction` was likewise silently defaulted to 0.5 and is now
passed explicitly as 0.55 (Azhar et al. 2023).

## Gate results, standing water

| gate | requirement | 1100 | 1609 | 2337 |
|---|---|---|---|---|
| P-1 oob particle-frames | 0 | 0 PASS | 0 PASS | 0 PASS |
| P-2 max water frac in vehicle bbox | < 10 % | **10.67 % FAIL** | 9.74 % PASS | 7.34 % PASS |
| P-3 veh z_min rise | <= 0.01 m | -0.007078 PASS | -0.003609 PASS | 0.000000 PASS |
| P-6 water layers | >= 4 | 4 PASS | 4 PASS | 4 PASS |
| determinism | identical across two loads | PASS | PASS | PASS |
| parity odd-column drop | measured | 0 of 1335 | 0 of 1335 | 0 of 1335 |

**P-2 FAILS on the 1100 kg row at 10.67 percent against a 10 percent limit.** See the
handoff for the hypothesis and the stop.

## Named limitations

- **Acoustic reflection.** c = sqrt(1.1 x 1.5e5 / 1000) = 12.845 m/s. Vehicle at x = 5.653,
  downstream wall at 8.833, round trip 0.4951 s, measured and printed by the driver. The runs
  are 3.0 s, so roughly six acoustic round trips. Everything after t ~ 0.5 s is
  reflection-contaminated. Not fixed; named.
- **Inflow sustains momentum, not mass.** The inflow band re-imposes velocity on particles
  already inside it; it does not inject new particles. Band population falls from 8967 at
  frame 0 to 162 at frame 89, so the upstream supply starves late in the run. Footprint depth
  still holds 0.3298 m at the end against 0.107 m for the old draining slab, so it is a large
  improvement but not a true steady state.
- **Bulk modulus 1.5e5 against real water 2.2e9.** Wave speed 12.845 m/s against 1481 m/s.
  At a 1.5 m/s surge the Mach number is 0.117, so the weakly-compressible density error is
  roughly 1.4 percent.
- **Mass 1100 kg is the MASH 1100C nominal**, taken from the LS-DYNA deck header, not this
  mesh's NCAC-modelled 1078 kg. The plausibility checklist requires that label wherever the
  number appears.
- **Water resolved by 4 layers** at n_grid 64. n_grid 96 would give 6, and the ratio gate now
  passes at every resolution, so refinement is permitted. Not run.
