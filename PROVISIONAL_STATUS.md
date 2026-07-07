# Provisional Status and Corrections Log

This file exists so the project's revision history is visible, not hidden. The README's "Key finding" section is kept as originally written. This file documents what has changed since, and why, so a reader can see where this started and where it is going.

Last updated: July 7, 2026 (session 3).

---

## Why this file exists

The README currently states the L2 finding (23 conditions, 16 divergence points, 30.4% L1/L2 agreement, friction-invariant drift) as settled fact. As of this update, that finding is **provisional**, pending a rebuild described below. Nothing in the README has been deleted. This file is the honest accounting layered on top.

---

## July 7 session 3: timestep bug, first clean NO-FORD, and where this SPH work stops

**Bug C, timestep too coarse.** After fixing mass and geometry (session 2), I pushed a stress test (d=1.0m, v=3.0m/s) and it spiked to a 1m displacement with a velocity vector pointing backward against the flow, then the session disconnected. That's the signature of a numerical blowup, not real physics. My own OSS survey already had the answer: Genesis's `flush_cubes.py` example uses `dt=4e-3, substeps=20` for MPM liquid coupling. My script was running `dt=1e-2`, 2.5x coarser.

```python
# before
sim_options=gs.options.SimOptions(dt=1e-2, substeps=10),
```

```python
# after
sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
```

Reran the same case that crashed. Clean finish, no crash, oscillatory transient (push, overshoot, partial recovery), velocity components stayed bounded under 0.5 m/s the whole run. Timestep was the whole story for the crash.

**First result I'd actually call trustworthy on this pilot scene:**

```
depth=1.0m velocity=3.0m/s verdict=NO-FORD peak_x_disp=0.1836m
```

3.7x over the 0.05m DRIFT_THRESHOLD. AR&R L1 agrees at this condition too (hazard = D x V = 3.0, far above the 0.60 threshold), a genuine cross-check pass between methods on corrected physics.

**Displacement now scales monotonically with severity for the first time this project has produced:**

| depth, velocity | AR&R hazard | peak x_disp | verdict |
|---|---|---|---|
| 0.3m, 1.5m/s | 0.45 | 0.0005m | FORD |
| 0.6m, 2.0m/s | 1.20 | 0.0125m | FORD |
| 0.6m, 2.5m/s | 1.50 | 0.0425m | FORD (close) |
| 1.0m, 3.0m/s | 3.00 | 0.1836m | NO-FORD |

**Sanity check run before trusting this, not just accepting a clean video:** compared the water's total x-momentum at the final step against the vehicle's estimated momentum change.

```python
mass_per_particle = 0.8 * 0.02**3 * 1000
total_px = (vel[:, 0] * mass_per_particle).sum()
```

Water: 320.1 kg m/s. Vehicle: roughly 1450 x 0.47 = 681.5 kg m/s. Same order of magnitude, not exact, not expected to be exact since this isn't a closed system (walls and ground absorb momentum too) and the two numbers are measured differently (final snapshot vs peak estimate). This rules out the push coming from nowhere. It does not prove the transfer is exact. I'm calling it plausible, not verified.

**One thing I still can't check:** WCSPH is only valid if the water's density stays within about 1% of rest density the whole run. My script doesn't save `rho` to the `.npz`, only `pos` and `vel`, so I can't check this retroactively for any run so far. Adding `rho` to the next save is a fix, not yet done.

**Where this stops, stated plainly:** this SPH box scene will not become the dataset in the paper, no matter how many more bugs get fixed in it. Every fix here (mass, geometry, timestep) transfers directly to the MPM version. The dataset itself does not.

---

## Confirmed corrections, in order of severity

### 1. Vehicle mass bug (discovered and fixed July 7)

The vehicle box in `can_it_ford_L2_new.py` never had an explicit density set. Genesis defaulted to an internal density giving a simulated vehicle mass far below a real curb weight of roughly 1,400-1,500 kg. The vehicle floated by construction, making `coup_friction` mathematically irrelevant regardless of its value. The originally reported "friction-invariant drift" result (0.395-0.400m across mu 0.0-0.7) is a likely artifact of this bug. Fixed by setting `rho=604` after correcting box size.

### 1b. Vehicle geometry and placement bug (discovered and fixed July 7)

Box was 0.4 x 0.2 x 0.15m, roughly 10x too small per dimension versus a real car, and positioned so its bottom face sat exactly at the water's top surface for every depth tested, meaning it rested on top of the water rather than in it. Confirmed by watching the render. Fixed by resizing to `size=(1.0, 1.6, 1.5)` and repositioning to `pos=(1.0, 0.0, 0.75)`, pinned to the ground independent of `water_depth`.

### 1c. Timestep bug (discovered and fixed July 7)

`dt=1e-2` was 2.5x coarser than the `dt=4e-3, substeps=20` range Genesis's own `flush_cubes.py` MPM coupling example uses. Caused a numerical blowup at an extreme test condition. Fixed by setting `dt=4e-3`.

### 2. Solver mismatch

All results to date were run on Genesis's SPH solver, not MPM. The abstract and README describe the pipeline as Genesis MPM. Not yet corrected in the running code.

### 3. Synthetic geometry, not a reconstructed scene

No real gsplat-reconstructed flooded scene has been ingested anywhere in the pipeline. No PhysGaussian kernel-to-particle bridge code exists yet. Tutorial 2's `bench.mov` is the only proof the gsplat half of the pipeline works end to end on its own.

### 4. Live script not yet on GitHub

`can_it_ford_L2_new.py`, with all three fixes above, has still not been pushed to this repo. Only the older, pre-fix `can_it_ford_L2.py` is on `main`.

### 5. DRIFT_THRESHOLD = 0.05m has no citation

Drives every NO-FORD verdict, no published source behind it yet. Candidate fix: Smith 2019 Eq. 6 as a stability-boundary fraction rather than a bare number.

### 6. Finding framing has changed twice

3 divergence points from 9 runs (June 29), then 16 from 23 (July 3). Both under the bugged conditions above.

### 7. CSV and NPZ logging gaps

`peak_x_disp`, the value the verdict is based on, is never written to `phase_space_results.csv`. `max_vel_ms` tracks initial settling speed, not flow velocity. `rho` is never saved to the `.npz`, blocking the WCSPH density-bound check described above. All three need a schema fix.

---

## What carries over to MPM, and what doesn't

**Carries over directly, already validated on this pilot scene:** `rho=604`, `size=(1.0, 1.6, 1.5)`, `pos=(1.0, 0.0, 0.75)` for the vehicle. `dt=4e-3` as a starting point, though MPM's actual stability rule is different (below).

**Does not carry over, needs its own derivation:** MPM stability depends on grid spacing, not just timestep. At Genesis's default `grid_density=64`, `dx=1/64=0.015625m`, and Genesis warns when `substep_dt > 2e-2 * dx`, meaning substep time must stay under `3.125e-4`s. `dt=4e-3` with `substeps=10` gives `substep_dt=4e-4s`, still 1.28x above that ceiling. `substeps=16-20` is the correct MPM starting point, not 10.

**Vehicle representation does not change.** It stays a `Rigid` entity coupled via `needs_coup=True`/`coup_friction`, the same pattern as today, just against `MPM.Liquid` water instead of `SPH.Liquid`. It does not become an MPM particle body itself.

**Template for the migration:** `examples/coupling/water_wheel.py --solver mpm` for emitter syntax, `examples/coupling/sand_wheel.py` for the coupling flag pattern, `examples/coupling/flush_cubes.py` for the parameter values above.

---

## Possible shortcut

Luke Smith's Tutorial 3 (`taichi_mpm` codebase) already contains a working real-gsplat-to-MPM bridge: `preprocess.py` ingests a real `.ply` file, `run_mpm.py` simulates it, demoed on a Toyota Corolla gsplat. Open question for Hassan or Cheng-Hsi: can this feed a Genesis scene on Vista.

---

## Rebuild path (in priority order)

1. Push `can_it_ford_L2_new.py` with all three fixes above to this repo
2. Fix the CSV and NPZ logging gaps
3. Migrate to `MPM.Liquid` with `grid_density=64`, `dt=4e-3`, `substeps=16-20`, vehicle stays `Rigid`
4. Shoot and gsplat-reconstruct a real water-adjacent scene
5. Write or adapt the PhysGaussian/Taichi bridge from real reconstructed geometry into simulatable particles
6. Rerun the full depth/velocity sweep on the corrected, real pipeline

## Deadline note

DesignSafe DOI was originally self-targeted for July 10. This is self-imposed, not an NSF requirement. Given the corrections above, publishing before the rebuild would be premature. Target is now approximately July 21 to July 24, pending explicit confirmation with Kumar. The only real hard constraint is that a DOI must exist before the July 31 final paper.
