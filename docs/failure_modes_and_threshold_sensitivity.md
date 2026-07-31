# Failure modes, threshold sensitivity, and violation magnitude

Analysis branch `analysis/failure-modes`, cut from `overleaf/main` at `bbd5bd8`.
Additive only. No change to `conference_101719_1.tex`, the bib, or any remote.

Every number below carries the command that reproduces it. Data lives on the root
checkout (`/Users/josie/can-it-ford`), which `overleaf/main` does not contain, so
paths are passed explicitly.

---

## Phase 0: the interpreter

Three prior sessions declared numpy unavailable after testing only system Python.
That conclusion was wrong. Tested live:

| Interpreter | numpy | pandas | matplotlib | scipy |
|---|---|---|---|---|
| `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3` (3.12.13) | 2.5.1 | 3.0.5 | 3.11.1 | 1.18.0 |
| `/usr/bin/python3` (3.9.6) | absent | absent | absent | absent |
| `/opt/homebrew/bin/python3` (3.14.6) | absent | absent | absent | absent |
| `~/miniforge3/envs/*/bin/python3` | path does not exist (`zsh: no matches found`) | | | |

The exact failure for the two system interpreters was
`ModuleNotFoundError: No module named 'numpy'`.

**All four packages are present in the `can-it-ford` env.** Matplotlib is available, so
the hand-rolled SVG fallback used by `analysis/paper_fig_l2_divergence_v2.py` was not
needed. Everything below uses that interpreter, written `PY` from here on.

---

## Phase 1: failure-mode classification

### 1a. Column semantics, checked against the generating script

Column meanings were read from `renders/yaris_render_s1/sim_standing.py`, not inferred
from names:

- `final_disp_mag_m` = `float(np.linalg.norm(d))` (line 366)
- `final_yaw_deg` / `final_roll_deg` / `final_pitch_deg` = last history entry (lines 367 to 369)
- `C2_veh_zmin_start` = min z over vehicle particles at t=0 (line 288)
- `C2_veh_zmin_final` = `float(veh_last[:, 2].min())` (line 377)
- `C2_veh_zmin_rise` = `final - start` (line 378)

Two things the names hide:

**`C2_veh_zmin_rise` is a fall, not a rise, in 16 of 17 runs.** Range is
-0.0539 m to +5.96e-08 m. The single positive value is float32 noise at that magnitude.
No run rises.

**`C2_veh_zmin_final` equals `3*dx` in all 17 runs**, maximum absolute deviation
3.88e-08 m. That is the MPM domain padding, which warp-MPM applies inward by three
cells. The vehicle base rests exactly on the padded floor in every run. Vertical
position is therefore saturated at a boundary and carries no flotation signal.

Ranges for all 42 columns are in the profiler output. Two columns are constant across
the sweep (`C3_oob_particle_frames` = 0, `determinism_identical` = True), `frames` = 90
everywhere, and `final_pitch_deg` never exceeds 0.003 deg in magnitude, so pitch carries
no signal either. Roll and yaw are the only rotational channels that move.

### 1b. Definitional gap: what the literature actually says

The literature defines these modes by **force balance**, not by any kinematic cutoff.
Quoted with locators:

**AR&R Project 10 Stage 2** (`citations/ARR_Project_10_Stage2_Report_Final.pdf`,
extracted text lines 390 to 398):

> "The two recognised hydrodynamic mechanisms by which stability is lost include
> buoyancy or floating and friction instability or sliding"

and, on toppling:

> "this stability appears to be restricted to vehicles which are already sliding or
> floating and encounter uneven terrain. This form of instability is therefore excluded
> from further analysis."

**Shah et al. 2018** (`~/Zotero/storage/4HIZ7KZB/`, extracted line 24, line 106):
lists "sliding, floating and toppling" as the instability modes, and defines floating as
the case "when the buoyancy force together with the lift force is greater than the
vehicle weight."

**Al-Qadami et al. 2023** (DOI `10.3390/su151713262`, Phase 5) gives the only numeric
thresholds found: floating at 0.38 m depth, sliding above 0.36 m2/s.

Three consequences, stated plainly:

1. No source gives a displacement or rotation cutoff. **The numeric cutoffs used below
   are operational, not empirical.** They are detection tolerances for classifying a
   simulation trace, not physical instability criteria.
2. AR&R excludes toppling from its own analysis and treats it as conditional on already
   sliding or floating. The classifier below therefore requires sliding as a
   precondition for TOPPLE, which follows the report rather than inventing a convention.
3. "Stuck" is not a literature mode. It is the stable baseline, the absence of
   instability. This matches the standing project rule in the debugging skill.

### 1c. Classification of all 17 runs

Operational cutoffs: `d_cut` = 0.05 m (the paper's existing drift tolerance),
`r_cut` = 1.0 deg roll, `z_cut` = 0.01 m rise. Precedence FLOAT, then TOPPLE, then
SLIDE, then STUCK.

```
PY analysis/paper_fig_failure_modes.py \
  --inventory /Users/josie/can-it-ford/data/all_runs_inventory.csv \
  --out-pdf fig_failure_modes.pdf --out-json failure_modes.json
```

| Mode | Count |
|---|---|
| STUCK | 0 |
| SLIDE | 15 |
| TOPPLE | 2 |
| FLOAT | 0 |

The two TOPPLE runs are `sweepD_g64_d0p45` (roll -2.44 deg) and `sweepV_g64_v3p0`
(roll -2.64 deg), the deepest and the fastest condition respectively.

FLOAT is zero, and it is zero for a reason that matters more than the count: with
`C2_veh_zmin_final` pinned to `3*dx`, **flotation is not measurable in this dataset at
all.** Reporting "0 float events" as a physical finding would be wrong. The correct
statement is that the observable is saturated.

STUCK is zero because the smallest drift in the sweep, 0.0578 m, already exceeds the
0.05 m cutoff. Every run moves.

### 1d. Cutoff sweeps

Each cutoff was swept rather than chosen:

| Cutoff | Range swept | Distinct classification outcomes |
|---|---|---|
| `d_cut` | 0.01 to 1.00 m, step 0.01 | 15 |
| `r_cut` | 0.05 to 10.0 deg, step 0.05 | 5 |
| `z_cut` | 0.001 to 0.050 m, step 0.001 | 1 |

`z_cut` is perfectly stable: FLOAT is 0 at every value in the range. That is a strong
result in the negative direction, and it is a direct consequence of the `3*dx` pinning.

`r_cut` is nearly stable. Roll magnitudes cluster into two groups with a wide empty gap:
13 runs below 0.009 deg, and four at 0.357, 0.508, 2.44, and 2.64 deg. Any `r_cut`
between 0.01 and 0.35 deg gives 4 TOPPLE; between 0.51 and 2.43 gives 2. The TOPPLE
count is therefore stable at 2 across roughly a fivefold range of cutoff, which is the
defensible reading.

`d_cut` is not stable, with 15 distinct outcomes. That is expected: it partitions a
continuous 0.058 to 1.338 m spread. It is the subject of Phase 2.

### 1e. Figure

`fig_failure_modes.pdf`, three panels: mode counts, `d_cut` sweep, `r_cut` sweep.
Verified vector: `pdfimages -list` returns zero rows, `DCTDecode` count 0, image
XObject count 0.

---

## Phase 2: threshold sensitivity

```
PY analysis/paper_fig_threshold_sensitivity.py \
  --inventory /Users/josie/can-it-ford/data/all_runs_inventory.csv \
  --scenarios /Users/josie/can-it-ford/data/scenario_sweep.csv \
  --sph-wandb /Users/josie/can-it-ford/data/l2_results_from_wandb.csv \
  --sph-phase /Users/josie/can-it-ford/data/phase_space_results.csv \
  --out-pdf fig_threshold_sensitivity.pdf --out-json threshold_sensitivity.json
```

### 2a. How runs were matched, and how many matched

Exact join on `(requested_depth_m, velocity_ms)` against `(depth_m, velocity_ms)`.
L1 verdict is taken from the class-specific column matching each run's own `label`
(`L1_verdict_small_passenger`, `_large_passenger`, `_large_4wd`), not the generic
`L1_verdict`.

**14 of 17 runs matched.** The three that did not are `sweepD_g64_d0p25`,
`sweepD_g64_d0p35`, and `sweepD_g64_d0p45`, at requested depths 0.25, 0.35, and 0.45 m.
The 70-scenario grid is spaced at 0.1 m, so those depths simply do not exist in it.

The 14 matched runs cover only **6 distinct scenario cells**, all at depth 0.30 m:
velocities 0.5, 1.0, 1.5, 2.0, 2.5, 3.0. Nine of the 14 sit in the single cell
(0.30, 1.5), differing only in vehicle mass and grid resolution. **The MPM sweep does
not span the L1 phase space; it is one depth column.** Any agreement rate computed from
it is therefore a statement about one depth, not about the ladder in general.

### 2c. The three questions

**Is there any t at which L1 and L2 fully agree? Pooled, no.** The obstruction is a
single pair: `g64_m1609` (large passenger, L1 says FORD) drifts 0.3141 m, while
`g96_m1100` (small passenger, L1 says NO-FORD) drifts only 0.2686 m. Full agreement
would need t below 0.2686 and at or above 0.3141 simultaneously. This survives
substituting peak drift for final drift (0.3217 versus 0.2695).

**But this result does not survive stratification, and that is the real finding.**
At each fixed grid resolution, a fully-agreeing threshold does exist:

| n_grid | n | Full-agreement window (m) |
|---|---|---|
| 48 | 3 | [0.2568, 0.3507) |
| 64 | 8 | [0.3141, 0.6585) |
| 96 | 3 | [0.1560, 0.2686) |

All three windows are non-empty; they simply do not intersect. **The pooled
disagreement is a grid-convergence artifact, not a structural incompatibility between
L1 and L2.** Within any single resolution, drift orders the runs exactly as L1 does.
Note also that the windows are not ordered monotonically in `n_grid`: 48 sits between
96 and 64. There is no sign of convergence across the three resolutions tested.

This is a negative result for the claim the analysis was set up to support, and it is
the single most important number in this document.

**Where does agreement peak?** 92.9% (13 of 14), on t in [0.26, 0.35] on the 0.01 m
grid. Identical peak using peak drift.

**How flat is the curve near 0.05 m?** Agreement at t = 0.05 is 42.9% (6 of 14). Across
t in [0.03, 0.07] it takes two values, 42.9% and 50.0%, a spread of 7.1 percentage
points. It is exactly flat below 0.0578 m (the smallest drift in the sweep) because
every run is NO-FORD there, and steps up once above. So the conclusion at 0.05 m is
insensitive to the threshold **downward** and mildly sensitive upward. A reviewer
raising threshold-insensitivity would be correct, and the honest answer is that 0.05 m
sits far below the data: it is not near any decision boundary.

### 2d. The SPH pilot, for comparison

The pilot logged 9 conditions (`data/l2_results_from_wandb.csv`). Drift magnitudes come
from `data/phase_space_results.csv` as `hypot(final_x_disp_m, final_y_disp_m)`.
**8 of 9 are usable.** The condition (0.30, 1.5) is excluded: it appears three times
with conflicting drifts (0.0461, 0.0344, 0.0570) and conflicting verdicts, so no single
value can be assigned. On the other 8, the two files agree on every verdict, which is
what justifies treating them as the same runs.

The contrast with MPM is sharp:

| | MPM (n=14) | SPH pilot (n=8) |
|---|---|---|
| Agreement at t = 0.05 m | 42.9% | 87.5% |
| Peak agreement | 92.9% | **100%** |
| Any t with full agreement | **No** (pooled) | **Yes**, t in [0.1343, 0.2445) |
| Spread over t in [0.03, 0.07] | 7.1 pts | 0.0 pts |

The pilot admits a drift threshold that reconciles L1 and L2 perfectly. The MPM sweep,
pooled, does not. But given the per-grid result above, the correct reading is that the
pilot was run at one resolution and the MPM sweep was not, so this comparison mostly
restates the convergence problem.

One data-quality note: in `l2_results_from_wandb.csv` the field `l1_haz_score` holds
0.750 for `L2_d0.3_v1.5` while `dv_product` is 0.450 (0.450/0.6 = 0.750, a normalised
ratio), whereas all other rows store the raw product. One field, two quantities.

---

## Phase 3: violation magnitude

```
PY analysis/violation_magnitude.py \
  --inventory /Users/josie/can-it-ford/data/all_runs_inventory.csv \
  --out-json violation_magnitude.json --out-tex table_violation_magnitude.tex
```

Every run exceeds the 0.05 m threshold. Drift as a multiple of the threshold ranges from
**1.16x** (`sweepV_g64_v0p5`, 0.0578 m) to **26.77x** (`sweepV_g64_v3p0`, 1.3384 m).

**Zero runs fall within 10% of the boundary at 0.05 m.** The closest is
`sweepV_g64_v0p5` at +15.6%. A binary verdict at 0.05 m therefore misrepresents no run
in this sweep, but only because the threshold sits an order of magnitude below the bulk
of the data, not because the runs are cleanly separated. The full ordered table is in
`table_violation_magnitude.tex`.

The same script reports grid sensitivity at fixed physical conditions
(D = 0.30 m, V = 1.5 m/s), which is the Phase 2 result seen from the other side:

| Mass (kg) | g48 | g64 | g96 | max/min |
|---|---|---|---|---|
| 1100 | 0.3507 | 0.6585 | 0.2686 | **2.45x** |
| 1609 | 0.2568 | 0.3141 | 0.1560 | 2.01x |
| 2337 | 0.1875 | 0.1356 | 0.0894 | 2.10x |

Identical physics, drift varying by a factor of 2.0 to 2.5 with grid resolution, and
non-monotonically for the 1100 kg case.

---

## Phase 4: time series

`metrics.csv` exists for all 17 runs and carries per-frame `dmag`, `vmag`, and the three
Euler angles, so the 62 MB `rollout.npz` files were never opened.

```
PY analysis/timeseries_convergence.py \
  --incoming /Users/josie/can-it-ford/renders/yaris_render_s1/_incoming \
  --out-json timeseries_convergence.json
```

Columns: `t, dx, dy, dz, dmag, yaw_deg, pitch_deg, roll_deg, vx, vy, vz, vmag, wx, wy, wz`,
91 rows (frames 0 to 90).

**Onset** is frame 1 in 16 of 17 runs, frame 2 in the remaining one. The vehicle is
already moving within one frame, and `metrics.csv` row 0 shows non-zero velocity and
attitude at t=0. This is an initialisation transient, not a flow-driven onset, so onset
frame carries no useful physics here.

**Motion is not monotonic.** Only 3 runs (all `n_grid`=48) increase at every step. The
other 14 have a drift maximum in the interior of the run, and then decrease.

**5 of 17 runs have not converged by frame 90**, and they are exactly the five most
severe conditions: `sweepD_g64_d0p35`, `sweepD_g64_d0p45`, `sweepV_g64_v2p0`,
`sweepV_g64_v2p5`, `sweepV_g64_v3p0`. All five are **re-accelerating at truncation**
(terminal speed more than twice the minimum speed reached after the drift peak).

For those five, the reported `final_disp_mag_m` **understates the peak excursion** by
8.3% to 24.9%. Worst case `sweepV_g64_v3p0`: peak 1.7817 m at frame 56, reported final
1.3384 m at frame 90, an understatement of 24.9%, with speed rising from 0.068 to
0.719 m/s over the last third of the run. Median understatement across all 17 is 1.2%.

The mechanism is a reversal, not continued growth. The scenario is
`standing_water_sustained_inflow` in a closed domain, so the most likely cause is the
reflected wave returning and pushing the vehicle back. This is the closed-domain
limitation already on the project's known-risk list, now observed directly.

**Implication for the paper:** for the five severe conditions, the reported final
displacement is neither a converged steady state nor the peak excursion. It is a value
sampled mid-reversal. Any verdict derived from it for those conditions is not defensible
without either a longer run or an open boundary. The other 12 have plateaued and are
fine.

---

## Phase 5: triangulating the threshold

### 5a. Identifying the paper

`vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md` line 303 already
contained the full citation, so no search was needed. Confirmed independently through
Scite by DOI:

**Al-Qadami, E. H. H., Razi, M. A. M., Damanik, W. S., Mustaffa, Z., and
Martinez-Gomariz, E. (2023). "Understanding the Stability of Passenger Vehicles Exposed
to Water Flows through 3D CFD Modelling." *Sustainability* 15(17), 13262.
DOI 10.3390/su151713262.**

All four distinctive strings match the abstract: floating at 0.38 m, sliding once
depth x velocity exceeds 0.36 m2/s, Froude 0.09 to 2.46, full-scale medium-size
passenger vehicle. Gold OA, CC-BY. **No editorial notices** (no retraction, correction,
or expression of concern).

Scite tally: total 2, supporting 0, contrasting 0, mentioning 2, across 4 citing
publications. That is a thin citation record, and it should be described as such if the
source is ever used: it is a recent single-vehicle CFD study, not a consensus position.

Note the co-author. Martinez-Gomariz is the same author the Phase 1b routing named
separately, and the paper's own validation section compares against
Martinez-Gomariz et al. 2017 (DOI 10.1080/1573062x.2017.1301501), obtaining 0.36 m2/s
against that paper's 0.47 m2/s, a 25% difference, and 0.380 m against 0.368 m for
floating depth, a 3.2% difference.

### 5b. A third L1 variant at 0.36 m2/s

Against a pure depth x velocity rule, swapping AR&R's small-passenger 0.30 m2/s for
Al-Qadami's 0.36 m2/s **flips 3 of 70 scenarios**, all from NO-FORD to FORD:
(0.1, 3.0), (0.2, 1.5), and (0.7, 0.5), each at hazard exactly 0.30 m2/s.

Compared against the stored `L1_verdict_small_passenger`, which also carries a depth
cap, it differs on 11 of 70, but that comparison is confounded by the depth cap and the
3-scenario figure is the clean one.

### 5c. Froude cross-check

Fr = V / sqrt(g*D), g = 9.81 m/s2. Verified with Wolfram Alpha at the nominal condition:
`1.5 / sqrt(9.81 * 0.30)` = **0.874372**, matching the numpy computation to six figures.
Using the realized depth 0.294429 m gives 0.882604.

Across the nine distinct conditions in the 17-run sweep, Fr ranges **0.294 to 1.765**
(realized depths). Al-Qadami's validated envelope is 0.09 to 2.46.

**All nine conditions sit inside their envelope.** That is a genuine cross-method
validation: an independent 3D CFD study of a full-scale medium-size passenger vehicle
covers the entire Froude range this sweep occupies. It is worth stating in the paper.

For context, 58 of the 70 scenarios in the L1 grid also fall inside the envelope; the 12
outside are the shallow, fast corner where Fr exceeds 2.46 (up to 3.03 at 0.1 m, 3 m/s).

No citation was added to the paper or the bib, per instruction.

---

## Reproducing everything

```
PY=/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3
R=/Users/josie/can-it-ford
$PY analysis/paper_fig_failure_modes.py --inventory $R/data/all_runs_inventory.csv --out-pdf fig_failure_modes.pdf --out-json failure_modes.json
$PY analysis/paper_fig_threshold_sensitivity.py --inventory $R/data/all_runs_inventory.csv --scenarios $R/data/scenario_sweep.csv --sph-wandb $R/data/l2_results_from_wandb.csv --sph-phase $R/data/phase_space_results.csv --out-pdf fig_threshold_sensitivity.pdf --out-json threshold_sensitivity.json
$PY analysis/violation_magnitude.py --inventory $R/data/all_runs_inventory.csv --out-json violation_magnitude.json --out-tex table_violation_magnitude.tex
$PY analysis/timeseries_convergence.py --incoming $R/renders/yaris_render_s1/_incoming --out-json timeseries_convergence.json
```
