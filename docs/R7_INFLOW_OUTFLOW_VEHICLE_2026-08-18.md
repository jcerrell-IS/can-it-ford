# Recycling inflow/outflow in the canonical vehicle scene

Round 7, task 7. Measured 2026-08-18 on Vista, Slurm job **918506**, partition `gh`,
COMPLETED 00:13:27, ExitCode 0:0, **34 of 34 runs rc=0, `ALLDONE`**. Plumbing validated
first by job **918501**, same partition, COMPLETED 00:00:57, ExitCode 0:0. Combined cost
about 0.24 node-hours, roughly 5 SU of the 617 available; balance read 616 afterwards.

Raw tree, including the 34 `rollout.npz` files that are too large to commit:
`$WORK/r7_inflow_918506` on Vista, 5.8 GB. Everything the tables are computed from is in
`data/r7_inflow_918506/`.

Every number below is printed by `analysis/inflow_vehicle_tables.py` from the JSON that
`analysis/inflow_vehicle_stats.py --json` writes. None is transcribed by hand, for the
reason `analysis/r6_repeat_stats.py:8-11` gives: on this project every hand-derived figure
has been wrong at least once.

---

## 0. The short version

**The canonical vehicle scene is a closed tank, and the tank manufactures a free-surface
slope larger than the physics anyone would want to measure.** At the canonical horizon the
artifact, defined as closed minus recycle so the vehicle's own backwater cancels, is
**+0.0711 m/m at the g64 baseline. A 3 degree road is tan(3 deg) = 0.0524 m/m, so the tank
is 1.36x the entire signal.** It is 0.90x at g96 m2337 and 0.61x at v0.5. Recycling the
streamwise faces removes it: every recycle arm sits between -0.004 and -0.016 m/m, and the
largest slope reached anywhere in a recycle run is 9.3x, 6.6x and 50.6x smaller than in its
matched closed control.

**No canonical verdict moves.** Three configurations, two horizons, N=5 per arm: 5 of 5
SLIDE stays 5 of 5 SLIDE at the g64 baseline and at the g96 tightest-margin case, and 5 of
5 STUCK stays 5 of 5 STUCK at v0.5, the only STUCK among the 17 published runs. **That is
the headline and it is a null.** It is the useful kind: the published binary verdicts do
not depend on the reflecting streamwise walls.

**The quantity those verdicts are about moves a great deal.** Displacement at the canonical
horizon rises **+35.4, +38.3 and +15.0 percent** across the three configurations, with
closed and recycle ranges completely disjoint in every case. By row 250 it rises **+307,
+521 and +88 percent**. And the sign of the late-time motion inverts, with no exceptions at
the level of individual runs: **all 16 closed-tank runs, including the unwrapped one, end
row 250 closer to their start than they were at row 90, and all 18 recycling runs end
further.** Largest `row250/row90` ratio among the closed-tank runs is 0.8264; smallest among
the recycling runs is 1.0566. The closed tank sloshes the vehicle back; the open channel
does not.

**Bow depth, the quantity a depth criterion would read, rises 24.8 percent at g64 and 55.7
percent at g96, and its peak moves from row 50 to row 224 and from row 17 to row 201.** The
closed tank drains the upstream reservoir that feeds the bow wave, so its bow depth peaks
early and decays. The open channel keeps supplying it.

**Two things got worse and are reported here rather than buried.** The below-floor leak
roughly triples at g64 under recycling (1.54 to 5.38 percent; 0.47 to 6.53 percent at
v0.5), though at g96 it is 0.000 percent in both arms. And the recirculation reaches the
vehicle at row 64, **inside** the canonical 90-frame horizon, refuting a prediction written
into the wrapper before the runs.

---

## 1. What was ported, and what was not touched

`simulation/openchannel_bc.py` is carried into this branch at its exact `be1b138` blob,
sha256 `bef123f947e3180e85bb8cbec61fe3ba0d6328f89382ae74bb2af49d2695272d`. It is imported,
never retyped, so the translation of Zhao, Bolognin, Liang, Rohe and Vardon 2019
(Computers and Fluids 179, 27-33, doi `10.1016/j.compfluid.2018.10.007`, Anura3D) into an
engine that cannot add or remove a particle has exactly one definition in the repo. That
module had been measured on the water-only channel and had never been run with a vehicle.

`renders/yaris_render_s1/sim_standing.py` is **not edited**. Its sha256
`4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9` stamps the 17 published
runs, it was confirmed live on both the Mac and Vista before the runs, and
`scripts/inflow_vehicle_wrapper.py` **refuses any other driver by sha** unless explicitly
overridden. Note that `$WORK/render_s2/sim_standing.py` on Vista is a *different*,
pre-registry copy (`5215c38b...`); the canonical copy there is
`$WORK/render_s2/multigeom_2026-08-08/sim_standing.py`. Their `StandingFloodScene` bodies
differ by exactly one line, `self.bulk_modulus = float(bulk_modulus)`, which records a
value and changes no physics. Diffed live, not assumed.

The wrapper imports the driver and calls its `main()` unmodified, patching two module
globals. The precedent is register D5 and `scripts/pinned_span_wrapper.py`.

| patched | what it does | applied when |
|---|---|---|
| `Solver` | subclass whose `add_plane` drops the two x-normal slip walls | `--bc recycle` only |
| `StandingFloodScene` | subclass that recycles at the outflow plane instead of clamping x, and records the per-frame instrumentation | always; behaviour changes only under `--bc recycle` |

`periodic_x` is not the route and is not used: `core/solver.py:93` documents it
"Incompatible with CDF colliders and rigid bodies" and the gated vehicle is a rigid body.

### Three design decisions that are choices, not defaults

1. **The settle phase clamps x in both arms.** `sim_standing.py` runs 8 settle frames
   before the velocity kick and before history row 0. Without the clamp the recycle arm's
   block slumps out of the channel at the dam-break speed 2*sqrt(g*d) = 3.4 m/s, about
   0.9 m in those 8 frames. With it, both arms reach t=0 as the same rectangular block and
   the boundary condition is the only thing that differs afterwards. It is **not** a
   bit-reproduction of the canonical settle: the closed arm also has grid-node slip planes
   acting during those frames and the recycle arm does not.
2. **The upstream velocity band is kept by default.** `_sustain_inflow` overwrites vx for
   every water particle upstream of `wall + 1.5 m`. That is a velocity-controlled inflow in
   Zhao's sense, over a slab rather than a plane, and it is the scene's only momentum
   source. Keeping it holds the forcing identical between arms. `--no-band` removes it,
   which is the faithful `sim_channel.py` recycle mode, and it is run as a sensitivity arm.
3. **The outflow plane sits exactly on the closed arm's downstream wall**, at
   `grid_lim - 4*dx`, not backed off from it, so the two arms share a streamwise extent.
   That is safe by construction, not by luck: `core/solver.py:430-431` runs the P2G edge
   guard at the *start* of `Solver.step`, and `sim_standing.py`'s `step()` calls
   `_project_water`, which now contains the recycler, *before* `solver.step`. At the instant
   the guard reads the array nothing is past `grid_lim - 4*dx`, and the guard trips at
   `grid_lim - 2.5*dx`. Measured largest single-tick overshoot across all runs is
   0.039 to 0.055 m against a 1.5*dx margin of 0.221 m at g64. See T6.

---

## 2. Validation, all of it done before any physics was read

**The classifier reproduces every published verdict it will be used to judge.** Run against
`renders/yaris_render_s1/_incoming/` with the published mass and SSF 1.42, classified to
metrics row 90:

| run | rows | verdict | published | |
|---|---|---|---|---|
| `g64_m1100` | 91 | SLIDE | SLIDE | match |
| `sweepV_g64_v0p5` | 91 | STUCK | STUCK | match |
| `g96_m2337` | 91 | SLIDE | SLIDE | match |

The classifier's `G` reads **9.81**, not the 9.80665 that CLAUDE.md item 15 and register A6
describe: `simulation/failure_modes.py:14` was unified to 9.81 on 2026-08-12 and says so in
its own comment. Read live, not carried.

**Job 918501, the g48 smoke test**: 4 of 4 runs rc=0, `ALLDONE`, and 11 of 11 plumbing
assertions PASS, including that the recycle arm drops exactly the two x-normal planes, that
the closed arm drops none, that the water count is identical in every arm, and that the
outflow plane lands exactly where the closed arm's downstream wall is. It measures no
physics and is not quoted as a result anywhere below.

**Repeats are genuinely different draws.** `determinism_identical` reads **true** on all 17
published runs, checked live against every `summary.json` under `_incoming/`. It is not a
reproducibility flag: `sim_standing.py:389` defines it as
`(v1.n_particles == v2.n_particles) and (lim1 == lim2)`, so it says the hull load is
bit-identical and nothing more. Measured here, the within-arm spread of displacement at row
90 is 0.46 to 4.78 percent of the mean and **no two repeats in any arm are identical**. So
N=5 was warranted, and every closed-versus-recycle difference reported below is far outside
that spread.

**Against the published runs themselves.** Two of three published `final_disp_mag_m` values
fall inside this job's closed-arm range: `g64_m1100` 0.65854 against 0.6563 to 0.6594, and
`sweepV_g64_v0p5` 0.05781 against 0.0563 to 0.0585. The third, `g96_m2337` 0.08944, sits
**3.2 percent above** the closed-arm range 0.0844 to 0.0866. That is roughly one
spread-width, the published value is a single draw, and I did not chase it. Stated, not
smoothed over.

---

## 3. The matrix

250 frames per run, so the wall-reflection window is inside the record rather than beyond
it, and every verdict is taken separately at metrics row 90, the canonical horizon, and at
row 250. Depth 0.30 m nominal (0.2944294 m realized at every grid), eta 1.0e-3, floor
friction 0.55, hull `yaris_coarse_v1l_watertight.ply`.

| config | grid | mass, kg | velocity, m/s | why this one |
|---|---|---|---|---|
| `g64m1100v1p5` | 64 | 1100 | 1.5 | the canonical baseline; carries the `bare` inertness control and the `--no-band` sensitivity arm |
| `g64m1100v0p5` | 64 | 1100 | 0.5 | `sweepV_g64_v0p5` is the **only STUCK** among the 17 published runs |
| `g96m2337v1p5` | 96 | 2337 | 1.5 | the **tightest published margin**, register J15, and R6 measured that margin as a random variable spanning 0 to 1 rather than a scalar |

Repeating comfortable cases measures nothing, so the two non-baseline configs are the two
boundary cases the project already knows about.

---

## 4. The wrapper is inert when it is supposed to be

### T1. Wrapper inertness: the unwrapped driver against the wrapped control

| config | quantity | bare, N=1 | closed wrapped, N | bare inside closed range |
|---|---|---|---|---|
| g64m1100v1p5 | `final_disp_mag_m` | 0.255990 | 0.257685 +/- 0.001925 (N=5, range 0.255246 to 0.260185) | yes |
| g64m1100v1p5 | `local_depth_bow_peak` | 0.395731 | 0.395777 +/- 0.000123 (N=5, range 0.395614 to 0.395923) | yes |
| g64m1100v1p5 | `passthrough_max_frac` | 0.107015 | 0.106899 +/- 0.000141 (N=5, range 0.106767 to 0.107118) | yes |
| g64m1100v1p5 | `leaked_particle_frames` | 341775 | 341733 +/- 82 (N=5, range 341629 to 341810) | yes |
| g64m1100v1p5 | `n_water` | 48367 | 48367 +/- 0 (N=5, range 48367 to 48367) | yes |

Five of five. The wrapped closed arm is the unwrapped driver plus read-only instrumentation,
so the closed control below is a matched control produced by the same code path as the
treatment rather than a different script.

---

## 5. The result: a closed tank manufactures a free-surface slope, and it is bigger than a road

### T3. Free-surface slope, m/m. Positive means water piled downstream.

| config | arm | rows 60-89 (pre) | rows 120-149 | rows 220-249 | drained bins of 12, rows 60-89 |
|---|---|---|---|---|---|
| g64m1100v0p5 | closed (wrapped control) | +0.02583 +/- 0.00002 | +0.02057 +/- 0.00001 | +0.00321 +/- 0.00001 | [0] |
| g64m1100v0p5 | recycle | -0.00633 +/- 0.00001 | -0.00479 +/- 0.00002 | -0.00821 +/- 0.00009 | [0] |
| g64m1100v1p5 | closed (wrapped control) | +0.06742 +/- 0.00003 | +0.01373 +/- 0.00002 | -0.01356 +/- 0.00003 | [2] |
| g64m1100v1p5 | recycle | -0.00372 +/- 0.00002 | -0.03185 +/- 0.00006 | -0.02532 +/- 0.00012 | [0] |
| g64m1100v1p5 | recycle, no inflow band | -0.00068 +/- 0.00001 | -0.00846 +/- 0.00002 | -0.00865 +/- 0.00005 | [0] |
| g96m2337v1p5 | closed (wrapped control) | +0.03098 +/- 0.00001 | +0.02513 +/- 0.00000 | +0.01785 +/- 0.00001 | [1] |
| g96m2337v1p5 | recycle | -0.01615 +/- 0.00005 | -0.02580 +/- 0.00006 | -0.02261 +/- 0.00006 | [0] |

Water-only channel at the same grid, grid_lim, depth and velocity, no vehicle (commit
`be1b138`): closed +0.09268 +/- 0.00161, 2 of 12 bins drained; recycle -0.00284 +/- 0.00029,
0 of 12 drained. A 3 degree road is tan(3 deg) = 0.05241 m/m; a 1 degree road is 0.01746.

**Isolating the artifact.** The recycle arm still carries a real slope, because a vehicle
blocking half the channel width produces genuine backwater upstream and drawdown
downstream. That physical component is common to both arms, so the difference is the
bounded-domain artifact alone:

| config | closed | recycle | artifact = closed - recycle | as a multiple of tan(3 deg) |
|---|---|---|---|---|
| g64m1100v1p5 | +0.06742 | -0.00372 | **+0.07114** | **1.36x** |
| g96m2337v1p5 | +0.03098 | -0.01615 | **+0.04713** | **0.90x** |
| g64m1100v0p5 | +0.02583 | -0.00633 | **+0.03216** | **0.61x** |

The water-only channel found the closed box making +0.0927 at zero grade, 1.77x tan(3 deg).
**With a vehicle in it the artifact is smaller but the same phenomenon**, and at the
canonical velocity it still exceeds a 3 degree road. The drained-bin column carries the
other half of the channel's result unchanged: the closed arm empties 2 of 12 streamwise
bins at the g64 baseline and 1 of 12 at g96; **no recycle arm ever drains a bin.**

### T7. The same slope as a time series, fitted at every profile row

| config | arm | slope at row 89 | at row 149 | at row 249 | max over the record | first sustained sign reversal |
|---|---|---|---|---|---|---|
| g64m1100v0p5 | closed (wrapped control) | +0.01297 +/- 0.00001 | +0.01085 +/- 0.00003 | +0.00081 +/- 0.00002 | +0.03026 +/- 0.00001 | none |
| g64m1100v0p5 | recycle | -0.00744 +/- 0.00007 | -0.00458 +/- 0.00007 | -0.00833 +/- 0.00023 | +0.00457 +/- 0.00000 | [47, 47, 47, 47, 47] |
| g64m1100v1p5 | closed (wrapped control) | +0.06023 +/- 0.00004 | +0.00758 +/- 0.00006 | -0.01624 +/- 0.00003 | +0.06960 +/- 0.00002 | [179, 179, 179, 179, 179] |
| g64m1100v1p5 | recycle | -0.01136 +/- 0.00016 | -0.02999 +/- 0.00017 | -0.02487 +/- 0.00034 | +0.00746 +/- 0.00000 | [68, 68, 68, 69, 69] |
| g64m1100v1p5 | recycle, no inflow band | -0.00308 +/- 0.00004 | -0.00871 +/- 0.00001 | -0.00769 +/- 0.00015 | +0.01424 +/- 0.00000 | [71, 71, 71] |
| g96m2337v1p5 | closed (wrapped control) | +0.02863 +/- 0.00002 | +0.02399 +/- 0.00003 | +0.01656 +/- 0.00001 | +0.03296 +/- 0.00000 | none |
| g96m2337v1p5 | recycle | -0.02034 +/- 0.00023 | -0.02857 +/- 0.00013 | -0.02319 +/- 0.00040 | +0.00065 +/- 0.00000 | none |

**The largest positive slope any run ever reaches** is the parameter-free summary:

| config | closed max | recycle max | reduction |
|---|---|---|---|
| g64m1100v1p5 | +0.06960 | +0.00746 | **9.3x** |
| g64m1100v0p5 | +0.03026 | +0.00457 | **6.6x** |
| g96m2337v1p5 | +0.03296 | +0.00065 | **50.6x** |

The sign-reversal column is only meaningful where the slope starts strongly positive, which
is the closed arms; the early reversals in the recycle arms are a small opening transient
crossing zero and should not be read as a basin event.

**Where the published horizon sits relative to the artifact.** The closed arm's slope peaks
at profile row 76 (g64 baseline), row 17 (g96 m2337) and row 53 (v0.5). At row 89, the
canonical horizon, it is at **86.5, 86.9 and 42.9 percent of its own peak**. So the 17
published runs stop while the bounded-domain artifact is near maximum, not after it has
relaxed.

---

## 6. What it does to the vehicle

### T4. Vehicle motion, with the row window named beside every magnitude

| config | arm | dmag at row 90, m | dmag at row 250, m | row250 / row90 | bow depth peak, m | bow peak row |
|---|---|---|---|---|---|---|
| g64m1100v0p5 | closed (wrapped control) | 0.0575 +/- 0.0009 | 0.0289 +/- 0.0013 | 0.502 +/- 0.015 | 0.2954 +/- 0.0001 | 23 +/- 3 |
| g64m1100v0p5 | recycle | 0.0795 +/- 0.0015 | 0.1793 +/- 0.0045 | 2.256 +/- 0.057 | 0.2954 +/- 0.0001 | 24 +/- 1 |
| g64m1100v1p5 | bare (unwrapped driver) | 0.6574 | 0.2560 | 0.389 | 0.3957 | 50 |
| g64m1100v1p5 | closed (wrapped control) | 0.6579 +/- 0.0014 | 0.2577 +/- 0.0019 | 0.392 +/- 0.003 | 0.3958 +/- 0.0001 | 50 +/- 0 |
| g64m1100v1p5 | recycle | 0.8909 +/- 0.0028 | 1.0491 +/- 0.0039 | 1.178 +/- 0.003 | 0.4941 +/- 0.0024 | 224 +/- 13 |
| g64m1100v1p5 | recycle, no inflow band | 0.7080 +/- 0.0038 | 0.7509 +/- 0.0048 | 1.061 +/- 0.005 | 0.3738 +/- 0.0006 | 30 +/- 1 |
| g96m2337v1p5 | closed (wrapped control) | 0.0854 +/- 0.0008 | 0.0697 +/- 0.0013 | 0.816 +/- 0.010 | 0.5093 +/- 0.0003 | 17 +/- 0 |
| g96m2337v1p5 | recycle | 0.0982 +/- 0.0015 | 0.1309 +/- 0.0017 | 1.333 +/- 0.013 | 0.7933 +/- 0.0035 | 201 +/- 1 |

Three things in that table.

**One. Opening the streamwise faces increases the displacement at the canonical horizon in
every configuration**, by +35.4 percent (g64 baseline), +38.3 percent (v0.5) and +15.0
percent (g96 m2337). The closed and recycle ranges are completely disjoint in all three;
the within-arm spread is at most 4.78 percent and the smallest effect is 15.0 percent.

**Two. The `row250 / row90` column has no exceptions, and not only in the means.**
Checked run by run: all 16 closed-tank runs are below 1, largest 0.8264, and all 18
recycling runs are above 1, smallest 1.0566. By arm the means are 0.392, 0.502 and 0.816,
plus 0.389 for the bare unwrapped driver, against 1.178, 2.256, 1.333 and 1.061 for the
no-band arm. The closed tank returns the
vehicle towards where it started; the open channel keeps pushing it. By row 250 the
displacement is +307, +521 and +88 percent higher in the recycle arms. **Any magnitude read
off a long closed-tank run is reading the tank.**

**Three. The bow depth, which is what a depth-threshold criterion would read, is
systematically understated by the closed tank at the higher velocity**: +24.8 percent at
the g64 baseline and +55.7 percent at g96 m2337, with the peak moving from row 50 to row
224 and from row 17 to row 201. The mechanism is visible in T3: the closed arm drains 2 of
12 and 1 of 12 streamwise bins, so the upstream reservoir that feeds the bow wave empties
and the bow depth peaks early and decays. The recycle arm drains nothing and the bow wave
keeps building. At v0.5 the two arms agree to -0.0 percent, which is consistent with the
same explanation: at v0.5 the closed arm drains no bins either.

The `--no-band` sensitivity arm separates the boundary from the drive. It moves the
displacement +7.6 percent at row 90 rather than +35.4, and its bow depth is *below* the
closed arm's. So roughly a fifth of the baseline displacement effect survives removing
`sim_standing`'s velocity band and most of it does not: the recycling boundary and the
sustained inflow act together, and this document does not attribute the effect to the
boundary alone.

---

## 7. Verdicts: nothing moves

### T2. Verdicts. Tallied, never meaned.

| config | arm | N | verdict at metrics row 90 (canonical horizon) | verdict at metrics row 250 |
|---|---|---|---|---|
| g64m1100v0p5 | closed (wrapped control) | 5 | 5 STUCK | 5 STUCK |
| g64m1100v0p5 | recycle | 5 | 5 STUCK | 5 STUCK |
| g64m1100v1p5 | bare (unwrapped driver) | 1 | 1 SLIDE | 1 SLIDE |
| g64m1100v1p5 | closed (wrapped control) | 5 | 5 SLIDE | 5 SLIDE |
| g64m1100v1p5 | recycle | 5 | 5 SLIDE | 5 SLIDE |
| g64m1100v1p5 | recycle, no inflow band | 3 | 3 SLIDE | 3 SLIDE |
| g96m2337v1p5 | closed (wrapped control) | 5 | 5 SLIDE | 5 SLIDE |
| g96m2337v1p5 | recycle | 5 | 5 SLIDE | 5 SLIDE |

Thresholds: `slide_m` 0.05, `slide_speed_ms` 0.05, `float_m` 0.05, `float_speed_ms` 0.02,
`sustain_frames` 3, SSF 1.42, G 9.81. Stock, unmodified.

**Not one verdict moves, in either direction, at either horizon, in any configuration.**
The v0.5 case is the sharpest test and the most instructive: its recycle arm reaches
**0.1793 m** of displacement by row 250, more than three times the 0.05 m `slide_m`
threshold and six times its own closed control, and is still classified **STUCK**. That is
`sustain_frames` and the joint displacement-AND-speed condition doing exactly what handoff
3c says they do. It is independent support for 3c's recommendation to report gate-pass
frequency rather than a persistence-gated binary: here a binary that does not move is
sitting on top of a quantity that moved 6x.

So the correct summary is **not** "the boundary condition does not matter". It is: **the
published binary verdicts are robust to the streamwise boundary condition, and the margins
behind them are not.**

---

## 8. The leaks

### T5. Water budget, percent of water outside the canonical box at the last frame

Measured pre-clamp against the SAME reference box in both arms, so the columns are
commensurable even though the recycle arm no longer walls the x faces.

| config | arm | below floor, % | outside y walls, % | outside x band, % | deepest floor penetration, m |
|---|---|---|---|---|---|
| g64m1100v0p5 | closed (wrapped control) | 0.471 +/- 0.001 | 1.926 +/- 0.002 | 0.9912 +/- 0.0024 | 0.0402 +/- 0.0000 |
| g64m1100v0p5 | recycle | 6.527 +/- 0.024 | 1.547 +/- 0.007 | 0.0000 +/- 0.0000 | 0.0477 +/- 0.0000 |
| g64m1100v1p5 | closed (wrapped control) | 1.536 +/- 0.003 | 1.940 +/- 0.001 | 0.1298 +/- 0.0017 | 0.0465 +/- 0.0000 |
| g64m1100v1p5 | recycle | 5.380 +/- 0.024 | 1.377 +/- 0.010 | 0.0037 +/- 0.0017 | 0.0477 +/- 0.0000 |
| g64m1100v1p5 | recycle, no inflow band | 19.975 +/- 0.069 | 1.661 +/- 0.005 | 3.2384 +/- 0.0150 | 0.0477 +/- 0.0000 |
| g96m2337v1p5 | closed (wrapped control) | 0.000 +/- 0.000 | 0.842 +/- 0.009 | 0.1130 +/- 0.0020 | -0.0029 +/- 0.0000 |
| g96m2337v1p5 | recycle | 0.000 +/- 0.000 | 0.757 +/- 0.009 | 0.0000 +/- 0.0000 | 0.0142 +/- 0.0002 |

**This diagnoses caveat 5 of the channel study**, which recorded `leaked_particle_frames`
running 2 to 3x higher in recycle mode and called it undiagnosed. The per-face split says
the excess is **entirely the floor**: below-floor rises 1.54 to 5.38 percent (g64 baseline)
and 0.47 to 6.53 percent (v0.5), while the y-wall leak *falls* in every recycle arm and the
x-band count falls essentially to zero, which is correct because the recycler holds all
water inside `[x_in, x_out]` by construction. The closed arm's non-zero x-band count is
water pressing on walls that the recycle arm does not have.

**It is a g64 phenomenon, not a property of the boundary condition.** At g96 the below-floor
fraction is 0.000 percent in *both* arms, and the closed arm's deepest excursion is
-0.0029 m, meaning no particle ever went below the floor at all. A plausible mechanism
consistent with these numbers, offered as a hypothesis and not a demonstration: the closed
arm drains bins and so has less wetted floor to leak through, and its downstream pile is
deep and slow, while the recycle arm sustains flow over the whole floor.

**Do not read these against job 918240's 4.505 percent below-floor and 2.410 percent outside
walls.** That job is `sphere_heave.py` at `lim` 1.2 with no vehicle and a different depth;
it is a different scene, and the closed arm here is not a reproduction of it. What can be
said is that the vehicle scene at g64 brackets those figures and the vehicle scene at g96
does not produce them at all.

The `--no-band` arm's 19.975 percent below-floor and 3.238 percent outside the x band are a
warning about that arm specifically, not about recycling: with no sustained inflow the flow
decelerates, the column sags and spreads, and the arm should be treated as a sensitivity
probe rather than a candidate configuration.

---

## 9. What got worse, and one prediction that was refuted

### T6. Recycling and how far the recirculation reaches

| config | arm | particles recycled, total | fraction ever recycled by row 250 | first row a recycled particle is inside the vehicle window | largest single-tick overshoot, m |
|---|---|---|---|---|---|
| g64m1100v0p5 | recycle | 24681 +/- 5 | 0.510 +/- 0.000 | [161, 162, 162, 162, 162] | 0.0400 +/- 0.0007 |
| g64m1100v1p5 | recycle | 36500 +/- 5 | 0.663 +/- 0.000 | [64, 64, 64, 64, 64] | 0.0546 +/- 0.0001 |
| g64m1100v1p5 | recycle, no inflow band | 26992 +/- 2 | 0.556 +/- 0.000 | [92, 92, 92] | 0.0446 +/- 0.0000 |
| g96m2337v1p5 | recycle | 62766 +/- 10 | 0.339 +/- 0.000 | [70, 70, 70, 70, 70] | 0.0391 +/- 0.0000 |

**The prediction written into `scripts/inflow_vehicle_wrapper.py` before any run was that
the recirculation would need about 130 frames to reach the vehicle and would therefore stay
outside the canonical 90-frame horizon. It is refuted.** At the g64 baseline the first
recycled particle enters the vehicle's streamwise window at **row 64**, identically in all
five repeats, and at g96 at **row 70**. Only the v0.5 case behaves as predicted, at row
161-162, and the no-band arm lands at row 92, just outside. This is why the tag was
instrumented rather than assumed, and it is the reason the "first sustained sign reversal"
and displacement claims above are anchored to measured rows rather than to that estimate.

What the tag does and does not mean. A tagged particle has crossed the outflow plane and
been re-inserted at the inflow plane with its (y, z) preserved and its velocity prescribed
to the inlet value. Downstream of re-insertion it is indistinguishable from fresh inflow
water except in its cross-stream position. So the number measures **how far the
recirculation has propagated, not how badly the result is contaminated**. It is the
signature of the uniform-channel translation: Zhao's uniform case has inflow discharge equal
to outflow discharge by construction, and the non-uniform case, which would need a spare
particle reservoir, is not expressible in a fixed pool and is not implemented.

By row 250, 34 to 66 percent of all water has been round the loop at least once.

**Overshoot is comfortable.** The largest single-tick excursion past the outflow plane is
0.055 m against the 1.5*dx = 0.221 m P2G guard margin at g64 and 0.147 m at g96, a factor of
4 and 3.8 respectively. The guard never fired in any of the 34 runs.

### The "wall reflection at frame 112.3" is reproducible but is probably mis-mechanised

`analysis/r6_repeat_stats.py:20-21` carries "the first wall reflection is predicted at frame
112.3 and observed at 112, 125 and 126" with no derivation anywhere in the repo. It is
reconstructible: a still-water shallow-water round trip, `2*(lim - 4*dx - 0.60*lim)/sqrt(g*d)`
with d = 0.2944294 m, gives **112.26 frames**, matching to 0.04 of a frame.

**But the still-water assumption is wrong for this scene.** The canonical velocity is
1.5 m/s over that depth, so sqrt(g*d) = 1.6995 m/s and the Froude number is 0.88. An
upstream-travelling shallow-water wave against that current makes 1.6995 - 1.5 = 0.1995 m/s
in the lab frame and needs roughly **478 frames**, not 112, to cover the 3.18 m back from
the wall. Arithmetic that reproduces a number is not the same as arithmetic that explains it.

The measured behaviour is also not wave-like on that timescale. The closed g64 baseline's
slope peaks at row 76, decays through row 149 and reverses sign at **row 179, identically in
all five repeats**; the closed g96 and v0.5 arms have not reversed by row 250. That looks
like a slow basin-scale redistribution, and the fundamental seiche period for this basin,
`2L/sqrt(g*d)` with L = 8.24 m, is 9.70 s or 291 frames, giving a half period of about 145
frames, which is the right order. **That is a consistency check, not a demonstration**, and
no mechanism is claimed here.

A separate detector was tried and failed. `reflection_arrivals()` fits each bin's depth
linearly over rows 40-89 and flags departures beyond 4 residual sigmas; it fires at row 91
in the closed arm and row 93 in the recycle arm, i.e. immediately, because that fit does not
extrapolate past row 89 in either arm. It is kept in the code with its docstring saying so,
because deleting a failed detector leaves the impression none was attempted.

---

## 10. What is not claimed

- **Not a bit-reproduction of the settle phase.** See section 1, decision 1. The two arms
  are geometry-matched at t=0, not bit-identical.
- **Not Zhao's non-uniform case, and not their validation case.** This is the uniform
  channel: one particle in, one particle out, discharges equal by construction. Their free
  overfall and its end-depth ratio (Rouse, critical depth about 1.4x brink depth) is not
  tested here, exactly as the channel study said of itself.
- **Not a resolution result.** The g96 arm is one grid, run to answer a verdict question at
  the tightest published margin. The refinement-ladder confound recorded in handoff section
  2 is untouched by anything here.
- **Not a claim that the closed-tank artifact is the largest error in the scene.** The
  4-particle-layer depth resolution, the 177 mm underbody clearance that no reachable grid
  resolves, and the material-8 velocity-averaging coupling are all still there and none of
  them is addressed by changing a boundary condition.
- **Not an attribution of the displacement effect to the boundary alone.** The `--no-band`
  arm shows most of the g64 baseline effect goes away when the sustained inflow is removed.
- **Not a re-measurement of job 918240.** Different scene. See section 8.
- **The mach margin is inherited and is below Zhao's criterion.** The canonical
  `bulk_modulus` 1.5e5 gives a numerical sound speed of 12.845 m/s, a margin of 8.56 over
  the 1.5 m/s flow, below the >10x that Zhao et al apply. That is a property of the
  canonical scene, not of this port, and it is unchanged in both arms.

---

## 11. Reproduction

```
# 1. plumbing, partition gh, about 1 minute
sbatch $WORK/r7_inflow_src/scripts/r7_inflow_smoke.sh

# 2. the matrix, partition gh, 13 minutes for 34 runs
sbatch $WORK/r7_inflow_src/scripts/r7_inflow_matrix.sh

# 3. pull the small files only; rollout.npz is 170 to 650 MB per run and stays on Vista
rsync -a --include='*/' --include='metrics.csv' --include='summary.json' \
  --include='inflow_summary.json' --include='inflow_instrument.npz' --exclude='*' \
  vista:$WORK/r7_inflow_918506/ <local>/

# 4. reduce, and regenerate every table in this document
/opt/homebrew/bin/uv run --with numpy python3 analysis/inflow_vehicle_stats.py \
  --runs <local> --json data/r7_inflow_918506/runs.json \
  --npz data/r7_inflow_918506/profiles.npz
/opt/homebrew/bin/uv run --with numpy python3 analysis/inflow_vehicle_tables.py \
  --json data/r7_inflow_918506/runs.json --npz data/r7_inflow_918506/profiles.npz
```

The numpy-only checks run on the Mac with no GPU:

```
/opt/homebrew/bin/uv run --with numpy python3 scripts/inflow_vehicle_wrapper.py --selftest
/opt/homebrew/bin/uv run --with numpy python3 simulation/openchannel_bc.py
```
