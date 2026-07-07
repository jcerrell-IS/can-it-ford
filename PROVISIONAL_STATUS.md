ytes

# Provisional Status and Corrections Log

This file exists so the project's revision history is visible, not hidden. The README's "Key finding" section is kept as originally written. This file documents what has changed since, and why, so a reader can see where this started and where it is going.

Last updated: July 7, 2026 (session 5).

---

## Why this file exists

The README currently states the L2 finding (23 conditions, 16 divergence points, 30.4% L1/L2 agreement, friction-invariant drift) as settled fact. As of this update, that finding is **provisional**, pending a rebuild described below. Nothing in the README has been deleted. This file is the honest accounting layered on top.

---

## July 7 session 5: session 4's viscosity fix was itself wrong, plus the friction bug that survived four sessions untouched

**Correcting Bug D.** Session 4 set `mu=0.001` on the reasoning that real water's dynamic viscosity is 1e-3 Pa*s. That reasoning was wrong. Genesis's `SPH.Liquid` `mu` argument is not SI dynamic viscosity, it's an internal weakly-compressible-SPH viscosity coefficient, and the engine's own default is `mu=0.005`. The official Genesis tutorial uses `mu=0.02` to demonstrate a visibly more viscous liquid for comparison. `mu=0.001` was below the engine's own baseline "water" setting, an unvalidated value with no source behind it, the opposite of a fix. Caught by cross-referencing the project's own Technical Feasibility Review, which was not consulted before making the session 4 change.

```python
# session 4 (wrong)
water = scene.add_entity(
    material=gs.materials.SPH.Liquid(mu=0.001, sampler="regular"),
    ...
)
```

```python
# session 5 (corrected)
water = scene.add_entity(
    material=gs.materials.SPH.Liquid(mu=0.005, sampler="regular"),
    ...
)
```

`mu=0.005` matches Genesis's own documented engine default exactly, so this is now a defensible, citable, non-arbitrary choice rather than a guess in either direction.

**Bug E, friction coupling never actually fixed.** `coup_friction=0.0` was flagged as a problem back in the mass-bug discussion (session 2), but no session actually changed the value, it stayed hardcoded at zero through sessions 2, 3, and 4, including the milestone NO-FORD result. This means every trustworthy-looking result to date, mass and geometry and timestep all correct, still ran with zero water-to-vehicle and vehicle-to-ground friction.

```python
# before, all sessions through session 4
frictionless_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.0, rho=604)
```

```python
# after, session 5
vehicle_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.4, rho=604)
```

`coup_friction=0.4` sits inside the empirically defensible range: Azhar et al. 2023 used mu=0.55 in a matched scale model, Smith et al. 2019 measured tire-pavement friction on concrete, gravel, and sand and recommended using a worst-case value, and the general range cited across both is 0.3 to 0.6. Variable renamed from `frictionless_rigid` to `vehicle_rigid` since the old name was no longer accurate.

**Why this matters more than a routine parameter fix:** a floating, near-massless body has ground normal force N approximately 0, so Coulomb friction mu*N approximately 0 regardless of what mu is set to. The original "friction-invariant drift, 0.395-0.400m across mu 0.0-0.7" result is exactly the signature that produces. Once mass was fixed (session 2), the vehicle should rest on the ground and friction should start to matter. It never got the chance to, because coup_friction stayed at 0.0 through every subsequent session. The session 3 milestone result (d=1.0m, v=3.0m/s, 0.1836m, NO-FORD) was generated with correct mass and correct submersion but still zero friction. Whether that verdict survives non-zero friction is unknown until it's rerun.

**CSV filename changed to avoid a silent corruption.** The committed `data/phase_space_results.csv` has 6 columns, no `peak_x_disp_m`. The session 4 CSV schema change added a 7th field but wrote to the same filename. If Vista's local working copy shares that same 6-column file (likely, since it accumulated the original 31 rows), the next run would append a 7-value row under a 6-column header, misaligning every column silently, pandas and Excel shift columns rather than error on this. Output filename changed to `phase_space_results_v2.csv` so a fresh, correct 7-column header always gets written, instead of relying on remembering to delete a file on Vista.

**Nothing has been rerun yet under the corrected mu + coup_friction + CSV filename stack.** Every number in the session 3 milestone table is now known to be under-friction and needs a rerun before it means anything.

---

## July 7 session 4 (superseded by session 5's correction above, kept for the record, not deleted)

Session 4 closed the CSV/NPZ logging gaps (peak_x_disp_m in the CSV, rho in the npz), both of which are still correctly closed and did not need correcting. Session 4 also set mu=0.001, which session 5 above corrects.

---

## July 7 session 3: timestep bug, first clean run, now known to be under-friction

**Bug C, timestep too coarse.** After fixing mass and geometry (session 2), a stress test (d=1.0m, v=3.0m/s) spiked to a 1m displacement with a velocity vector pointing backward against the flow, then crashed. That's a numerical blowup, not real physics. Genesis's own `flush_cubes.py` example uses `dt=4e-3, substeps=20` for MPM liquid coupling. The script was running `dt=1e-2`, 2.5x coarser.

```python
# before
sim_options=gs.options.SimOptions(dt=1e-2, substeps=10),
```

```python
# after
sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
```

Reran the same case that crashed. Clean finish, no crash, oscillatory transient, velocity components stayed bounded under 0.5 m/s the whole run. Timestep was the whole story for that specific crash.

**The session 3 result, now known to be incomplete, not just unverified:**

```
depth=1.0m velocity=3.0m/s verdict=NO-FORD peak_x_disp=0.1836m
```

Correct mass, correct submersion, correct timestep, but zero friction (coup_friction=0.0, unfixed until session 5) and an over-viscous fluid at the time (mu=0.01, later wrongly "fixed" to 0.001 in session 4, corrected to 0.005 in session 5). This number does not carry forward as trusted. It needs a full rerun under the session 5 fix stack.

**Sanity check that still holds regardless of the above:** compared the water's total x-momentum at the final step against the vehicle's estimated momentum change. Water: 320.1 kg m/s. Vehicle: roughly 1450 x 0.47 = 681.5 kg m/s. Same order of magnitude. This check is about momentum transfer plausibility, not about friction or viscosity, so it isn't invalidated by the corrections above, but it also doesn't validate the specific displacement number, which does need a rerun.

**Where this stops, stated plainly:** this SPH box scene will not become the dataset in the paper, no matter how many more bugs get fixed in it. Every fix here (mass, geometry, timestep, viscosity, friction) transfers directly to the MPM version. The dataset itself does not.

---

## Confirmed corrections, in order of discovery

### 1. Vehicle mass bug (discovered and fixed July 7, session 2)

No explicit density set. Vehicle floated by construction. Fixed with `rho=604`.

### 1b. Vehicle geometry and placement bug (discovered and fixed July 7, session 2)

Box undersized and positioned to always sit exactly at the water surface. Fixed with `size=(1.0, 1.6, 1.5)`, `pos=(1.0, 0.0, 0.75)`.

### 1c. Timestep bug (discovered and fixed July 7, session 3)

`dt=1e-2` was 2.5x coarser than Genesis's own MPM coupling example range. Fixed with `dt=4e-3`.

### 1d. Water viscosity, fixed wrong then corrected (session 4, then session 5)

Session 4 set `mu=0.001` believing it matched real water's SI viscosity. Genesis's `mu` is not SI viscosity, and 0.001 is below the engine's own default. Session 5 corrected to `mu=0.005`, the documented engine default.

### 1e. Friction coupling bug (discovered and fixed July 7, session 5)

`coup_friction=0.0` was identified as a problem during the session 2 mass-bug discussion but never actually changed until session 5. Every result from session 2 onward, including the session 3 milestone, ran with zero friction. Fixed to `coup_friction=0.4`, cited (Azhar et al. 2023, Smith et al. 2019, defensible range 0.3-0.6).

### 2. Solver mismatch

All results to date were run on Genesis's SPH solver, not MPM. Not yet corrected in the running code, an untested MPM draft exists at `simulation/can_it_ford_L2_mpm.py`.

### 3. Synthetic geometry, not a reconstructed scene

No real gsplat-reconstructed flooded scene has been ingested anywhere in the pipeline. No PhysGaussian bridge code exists yet.

### 4. Closed, reflecting domain boundary (known, still unaddressed)

Genesis's SPH solver uses a `CubeBoundary`, reflecting on all six faces, not an open channel. The domain is 2.0m long in x, the vehicle occupies roughly x=0.5 to 1.5, half the domain length, with only 0.5m of clearance to the downstream wall. At velocities up to 3.0 m/s over a 500-step horizon, reflected waves off that wall very likely reach the vehicle before the run ends. This applies to the MPM version too, Genesis has no native inlet/outlet boundary for either solver in this version. The single most decisive unresolved test: does the drift result survive an enlarged or damped domain, or does it disappear, which would mean the closed tank was generating the drift rather than the flow.

### 5. DRIFT_THRESHOLD = 0.05m, citation resolved, code unchanged

No published paper defines a fixed 0.05m displacement threshold. Reframed as roughly 2.5-3.4% of representative vehicle body width (Xia et al. 2014, Shah et al. 2018). Full writeup in `citations/README.md`.

### 6. Vehicle geometry is a proxy, not a documented consistent scale

Current box is 1.0 x 1.6 x 1.5m, 2.4 cubic meters. A real vehicle's external envelope is closer to 10-12 cubic meters, or the scene would need a consistently applied 1:10 scale (Froude-similarity-adjusted depth and velocity too, not just the vehicle). Box-proxy vehicles are supported in the literature (Xiong et al. 2024), this specific undersized aspect ratio without a stated scale convention is not yet.

### 7. CSV and NPZ logging gaps (resolved July 7, sessions 4-5)

`peak_x_disp_m` is now written to the CSV. `rho=604` is now saved to the `.npz`. Output filename changed in session 5 to `phase_space_results_v2.csv` to avoid a header-schema collision with the existing 6-column committed file.

---

## What carries over to MPM, and what doesn't

**Carries over directly, validated on this pilot scene as of session 5:** `rho=604`, `size=(1.0, 1.6, 1.5)`, `pos=(1.0, 0.0, 0.75)` for the vehicle. `coup_friction=0.4` as a starting point, same citation basis applies to MPM-rigid coupling. `dt=4e-3` as a starting point only, MPM's actual stability rule is different (below).

**Does not carry over as-is:** MPM stability depends on grid spacing, not just timestep. At Genesis's default `grid_density=64`, `dx=1/64=0.015625m`, Genesis warns when `substep_dt > 2e-2 * dx`, so substep time must stay under `3.125e-4`s. `dt=4e-3` needs `substeps=16-20` for MPM, not 10. The `mu=0.005` SPH viscosity value has no direct MPM equivalent, `MPM.Liquid` defaults to `viscous=False` and derives its stress response from `E=1e6, nu=0.2`, not a viscosity coefficient in the SPH sense, do not carry `mu` over to the MPM script.

**Vehicle representation does not change.** Stays a `Rigid` entity, `needs_coup=True`/`coup_friction`, against `MPM.Liquid` instead of `SPH.Liquid`.

**Template for the migration:** `examples/coupling/water_wheel.py --solver mpm`, `examples/coupling/sand_wheel.py`, `examples/coupling/flush_cubes.py`.

---

## Possible shortcut

Luke Smith's Tutorial 3 (`taichi_mpm` codebase) already contains a working real-gsplat-to-MPM bridge: `preprocess.py` ingests a real `.ply` file, `run_mpm.py` simulates it, demoed on a Toyota Corolla gsplat. Open question for Hassan or Cheng-Hsi: can this feed a Genesis scene on Vista.

---

## Rebuild path (in priority order)

1. ~~Push the corrected script (mass, geometry, timestep) to this repo~~ **Done, July 7.**
2. ~~Fix the CSV and NPZ logging gaps~~ **Done, July 7.**
3. ~~Fix friction coupling and correct the viscosity overcorrection~~ **Done, July 7, session 5.**
4. Rerun all conditions with the full corrected fix stack (mass, geometry, timestep, viscosity, friction, new CSV filename)
5. Test whether the drift result survives an enlarged/damped domain, the single most decisive open test on the closed-boundary question
6. Migrate to `MPM.Liquid` with `grid_density=64`, `dt=4e-3`, `substeps=16-20`, vehicle stays `Rigid`, draft exists untested at `simulation/can_it_ford_L2_mpm.py`
7. Shoot and gsplat-reconstruct a real water-adjacent scene
8. Write or adapt the PhysGaussian/Taichi bridge from real reconstructed geometry into simulatable particles
9. Rerun the full depth/velocity sweep on the corrected, real pipeline

## Deadline note

DesignSafe DOI was originally self-targeted for July 10. This is self-imposed, not an NSF requirement. Given the corrections above, publishing before the rebuild would be premature. Target is now approximately July 21 to July 24, pending explicit confirmation with Kumar. The only real hard constraint is that a DOI must exist before the July 31 final paper.
