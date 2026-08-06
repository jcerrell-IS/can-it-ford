# Three AR&R vehicle classes, three verdicts

Generated 2026-07-25 from `renders/yaris_render_s1/gates_results.json`. Every number below
traces to a command run in that session: the sims are Vista job 866266 (reused idle GPU,
node c642-011/c642-001, GH200 120GB, exit 0 on all three), the gates are
`renders/yaris_render_s1/gates.py`.

## READ THIS FIRST: what varies and what does not

**V1 is a MASS-ONLY sensitivity study. All three runs use the SAME 2010 Toyota Yaris
hull.** Only `--vehicle-mass` changes. The 1609 kg row is NOT a Nissan Rogue and the
2337 kg row is NOT a Chevrolet Silverado. They are a Yaris hull carrying that class's
kerb mass. Real Silverado and Rogue meshes exist as NCAC LS-DYNA decks but are not
converted (see the gap manifest). Do not label these rows with vehicle names in any
figure, poster, or paper.

Geometry warping was NOT used. `fit_to_bbox` produced a 4.6x divergence and is on the
do-not-ship list.

## AR&R stability limits, read live from `vehicle_params.py:166`

Source string, verbatim from `AR_R_SOURCE` at `vehicle_params.py:158`:

> Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2, P10/S2/020,
> ISBN 978-0-85825-948-5, Table 3 'Proposed DRAFT Stability Criteria for
> Stationary Vehicles', PDF p.24 / printed p.14. Values are the report's own
> DRAFT INTERIM figures for STATIONARY vehicles, not an endorsed safety standard.

| class | depth limit (m) | velocity limit (m/s) | D x V limit (m2/s) | length (m) | kerb (kg) |
|---|---|---|---|---|---|
| small_passenger | 0.30 | 3.0 | 0.30 | <= 4.3 | <= 1250 |
| large_passenger | 0.40 | 3.0 | 0.45 | >= 4.3 | >= 1250 |
| large_4wd | 0.50 | 3.0 | 0.60 | >= 4.5 | >= 2000 |

Class-to-mass mapping from `reference_data/vehicle_data_master_reference_2026-07-21.json`:
2010 Toyota Yaris, MASH 1100C, deck header 1100 kg -> small_passenger.
2020 Nissan Rogue, 1609 kg -> large_passenger. 2007 Chevrolet Silverado, MASH 2270P,
2337 kg -> large_4wd.

## The runs

Common to all three: nominal depth 0.30 m, nominal surge 1.5 m/s, n_grid 64,
90 frames at 30 fps, grid_lim 9.4216 m, dx 0.147213 m, h 0.0736064 m, 4 water layers,
23532 water particles, hull volume 3.542739 m3.

| class | mass (kg) | fill ratio (n_grid=64) | rho (kg/m3) | final abs d (m) | final yaw (deg) | L1 nominal | L2 (MPM) | agree? |
|---|---|---|---|---|---|---|---|---|
| small_passenger | 1100 | 1.0024 | 309.75 | 0.09240 | +1.431 | NO-FORD | NO-FORD | AGREE |
| large_passenger | 1609 | 1.0023 | 453.13 | 0.05110 | +0.016 | FORD | NO-FORD | **DIVERGE** |
| large_4wd | 2337 | 1.0023 | 658.14 | 0.03890 | +0.310 | FORD | FORD | AGREE |

fill_ratio is grid-dependent and must not be quoted without its n_grid. The three values
above are render_s1 at n_grid=64. Across grids in render_s2 it is 1.026243 at g48,
1.002440 at g64 and 0.994089 at g96. Particle count moves with it: 3846 / 8905 / 29804.

L2 verdict rule: final displacement magnitude vs DRIFT_THRESHOLD = 0.05 m.
**DRIFT_THRESHOLD 0.05 m has no peer-reviewed source.** It is a conservative numerical
onset-of-motion detection tolerance, not a literature stability criterion. The
large_passenger row sits 2.2 percent above it (0.05110 vs 0.05000), so that single
NO-FORD is inside the threshold's own uncertainty and must not be presented as a robust
result.

## Physics gate, all three runs

| gate | requirement | 1100 kg | 1609 kg | 2337 kg |
|---|---|---|---|---|
| P-1 particles outside domain | 0 | 0 PASS | 0 PASS | 0 PASS |
| P-2 max water frac in vehicle bbox | < 10 % | 3.68 % PASS | 3.02 % PASS | 2.43 % PASS |
| P-3 veh z_min rise | <= 0.01 m | 0.000000 PASS | 0.000000 PASS | -0.000000 PASS |
| P-6 water layers | >= 4 | 4 PASS | 4 PASS | 4 PASS |

No FLOAT is live in any run. All three are slide-regime with sub-decimetre drift.

## P-5: D x V computed the honest way changes the L1 comparison

AR&R's D is the depth AT THE VEHICLE, not the upstream slab. Measured in a window
3 dx to 0.5 dx upstream of the vehicle's minimum-x face, spanning the vehicle's y extent,
99.5th percentile of water z above the floor plane. Water speed is the mean over the
same window at the frame of peak local depth.

| class | nominal D x V | local D peak (m) | local V at peak (m/s) | honest D x V | change |
|---|---|---|---|---|---|
| small_passenger | 0.30 x 1.5 = 0.4500 | 0.3974 (frame 29) | 0.4760 | 0.1892 | -58.0 % |
| large_passenger | 0.30 x 1.5 = 0.4500 | 0.4159 (frame 29) | 0.3956 | 0.1645 | -63.4 % |
| large_4wd | 0.30 x 1.5 = 0.4500 | 0.4260 (frame 29) | 0.3592 | 0.1530 | -66.0 % |

Local depth is HIGHER than nominal (bow-wave pile-up against the body) while local speed
is far LOWER than nominal (the body stagnates the flow). The product falls by roughly
three fifths.

**Re-running L1 on the honest local values flips large_passenger from FORD to NO-FORD,
and then L1 and L2 agree on all three classes.** The flip is caused by the DEPTH limit
(local peak 0.4159 m exceeds the 0.40 m large_passenger limit), not by D x V
(0.1645 is far under the 0.45 limit).

| class | L1 nominal | L1 honest local | L2 | agreement on honest values |
|---|---|---|---|---|
| small_passenger | NO-FORD | NO-FORD | NO-FORD | AGREE |
| large_passenger | FORD | NO-FORD | NO-FORD | AGREE |
| large_4wd | FORD | FORD | FORD | AGREE |

Caveat on that flip, stated because it decides a verdict: the local peak is a transient
stagnation maximum at the surge front (frame 29 of 90), not a sustained flood depth. By
the final frame local depth has fallen to 0.107 to 0.124 m as the finite slab drains
downstream. Whether AR&R's D means the approach depth, the stagnation peak, or a
time-averaged depth is a modelling decision this run cannot settle, and the
large_passenger verdict depends entirely on which is chosen.

## Contradiction with the paper's current claim

The paper asserts an empirical divergence zone at depth >= 0.25 m, velocity >= 1.2 m/s,
D x V < 0.60, in which L1 says FORD and L2 says NO-FORD. The nominal point tested here
(0.30 m, 1.5 m/s, D x V 0.45) is inside that zone on all three conditions.

The zone claim does not hold as written:

1. **small_passenger contradicts it.** L1 says NO-FORD, not FORD, because the
   small_passenger hazard limit is 0.30 m2/s and 0.45 exceeds it. Both levels say
   NO-FORD, so this point is agreement, not divergence.
2. **large_4wd contradicts it.** Both levels say FORD. Agreement, not divergence.
3. **large_passenger is the only class that behaves as the paper claims**, and only when
   L1 is fed nominal rather than local values.

The zone as written is class-free. It cannot be, because the AR&R limits it is compared
against are class-specific. At a fixed D x V of 0.45 the L1 verdict alone is NO-FORD,
FORD, FORD across the three classes. Any restatement of the divergence zone must carry a
class label.

## Standing caveats

- Water is 4 particle layers at n_grid 64. Depth dependence is claimable but coarse.
- Bulk modulus is deliberately softened for timestep stability, so the acoustic wave
  speed is not physical water. State in Limitations.
- This is a finite dam-break slab, not a sustained flood. Local depth decays through the
  run. A steady-inflow boundary would be a different experiment.
- Single depth-velocity point only. No sweep on the corrected geometry.
