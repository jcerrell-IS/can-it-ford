# Provisional Status and Corrections Log

This file exists so the project's revision history is visible, not hidden. The README's "Key finding" section is kept as originally written. This file documents what has changed since, and why, so a reader can see where this started and where it is going.

Last updated: July 10, 2026 (correction added below; nothing in the session 6 entry deleted, per this file's own convention).

---

## July 10 correction: the session 6 "first clean MPM run" below was never independently confirmed, and the direct-Genesis-MPM track has since crashed with zero output

I flagged this to myself on July 8 and could not reproduce it (grep on Vista at the time showed both L2 scripts still running `SPH.Liquid`), and retracted the claim in that day's session. I did not come back and correct this file after that retraction.

Then on July 9, running the actual current `can_it_ford_L2_mpm.py` (the file the July 7 session 6 entry below describes) produced: step 0 only, `CUDA_ERROR_ILLEGAL_ADDRESS` on the first coupled substep, no verdict, no video, no `.npz`, no CSV row. Full write-up: `kumar_july9_update/STATUS.md`, Track 2. Kumar was told this directly the same night, honestly, not as a "success."

So the specific numbers in the July 7 entry below (`verdict=FORD peak_x_disp=0.0038m`) are not confirmed to have come from a real run of this pipeline. They may be a real result from an earlier, different version of the script, a mis-transcribed number, or a hallucinated one. I don't know which, and I'm not deleting the entry, I'm flagging it as unconfirmed until someone (me, on Vista, with a saved terminal log) reproduces it.

**Current true state, as of July 9 (see `kumar_july9_update/STATUS.md` for full detail):** two MPM tracks running in parallel, neither has produced a FORD/NO-FORD verdict. Direct Genesis MPM (Track 2) crashes at step 0. `kks32/mpm-engine` (Track 1) is further along (real sedan-scale vehicle box wired in) but has an unresolved water-drift bug during gravity settling, before the vehicle is even added.

---

## Why this file exists

The README currently states the L2 finding (23 conditions, 16 divergence points, 30.4% L1/L2 agreement, friction-invariant drift) as settled fact. As of this update, that finding is **provisional**, pending a rebuild described below. Nothing in the README has been deleted. This file is the honest accounting layered on top.

---

## July 7 session 6: first clean MPM run

`can_it_ford_L2_mpm.py`'s first attempt crashed on `add_entity`, MPM pads whatever domain you specify inward by `3*dx` (confirmed exactly `0.046875m` at `grid_density=64`), and the water box's floor sat exactly on `z=0`, outside that padded interior. Not a bug in the fix stack, a solver-specific domain requirement SPH doesn't have. Fixed by expanding the domain from `(0,-1,0)-(2,1,2.4)` to `(-0.1,-1,-0.1)-(2.1,1,2.5)`. Full writeup in `REBUILD_REFERENCE.md`.

**First result on real MPM, same fix stack as session 5 (rho=604, coup_friction=0.4), grid_density=64, substeps=20:**

```
depth=0.3m velocity=1.5m/s verdict=FORD peak_x_disp=0.0038m final_x_disp=0.0038m max_vel=0.1167m/s
```

Agrees with AR&R L1 at this condition (hazard = 0.3*1.5 = 0.45, below the 0.60 threshold, both say FORD). **Not yet directly comparable to the SPH result at the same condition**, the only SPH run under the full 5-bug fix stack so far was the d=1.0/v=3.0 headline case, not this milder one. A same-condition SPH rerun at d=0.3/v=1.5 under the full stack is the natural next comparison, not yet done.

**Still open before this counts as more than a smoke test:** `grid_density=64` is below the `128` minimum flagged for real car geometry (issue #600 tunneling risk), acceptable for now since the vehicle is still a box proxy, not yet acceptable once a real mesh is in place. Domain is still the small synthetic-scale box, not the real-scene rule-of-thumb size. Only one condition tested, not a sweep.

**(See the July 10 correction at the top of this file: this result is now unconfirmed, not verified fact.)**

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

**Note added July 10:** the live code as of today actually runs `coup_friction=0.55` (Azhar et al. 2023's own value directly, not the 0.4 blended estimate described above). See `kumar_july9_update/STATUS.md` for the current, verified-against-the-live-file parameter table.

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

`coup_friction=0.0` was identified as a problem during the session 2 mass-bug discussion but never actually changed until session 5. Every result from session 2 onward, including the session 3 milestone, ran with zero friction. Fixed to `coup_friction=0.4` (later moved to `0.55`, see July 10 note above), cited (Azhar et al. 2023, Smith et al. 2019, defensible range 0.3-0.6).

### 1f. MPM boundary safety padding (discovered and fixed July 7, session 6)

MPM pads the specified domain inward by `3*dx` on every face, SPH does not do this. The SPH-sized domain crashed on first MPM use. Fixed by expanding the domain with margin.

### 2. Solver mismatch, now partially resolved

SPH results were run on Genesis's SPH solver. MPM draft crashes at step 0 as of July 9 (see July 10 correction at top), not yet a clean sweep, not yet a single confirmed verdict.

### 3. Synthetic geometry, not a reconstructed scene

No real gsplat-reconstructed flooded scene has been ingested anywhere in the pipeline. No PhysGaussian bridge code exists yet.

### 4. Closed, reflecting domain boundary (known, still unaddressed)

Genesis's SPH solver uses a `CubeBoundary`, reflecting on all six faces, not an open channel. Applies to MPM too, confirmed no inlet/outlet API exists in v1.2.0. The single most decisive unresolved test: does the drift result survive an enlarged or damped domain.

### 5. DRIFT_THRESHOLD = 0.05m, citation resolved, code unchanged

No published paper defines a fixed 0.05m displacement threshold. Reframed as roughly 2.5-3.4% of representative vehicle body width (Xia et al. 2014, Shah et al. 2018). Full writeup in `citations/README.md`.

### 6. Vehicle geometry is a proxy, not a documented consistent scale

Current box is 1.0 x 1.6 x 1.5m, 2.4 cubic meters. Real vehicle mass better sourced now via EPA 2025 Automotive Trends Report (~1975-2014 kg average), see `REBUILD_REFERENCE.md`. As of July 9, the `kks32/mpm-engine` track uses the real sedan bounding box (4.66 x 1.79 x 1.44m, NHTSA/SAE 1999-01-1336) but `can_it_ford_L2_mpm.py` has not been updated to match, see `kumar_july9_update/STATUS.md`, "Track Divergence."

### 7. CSV and NPZ logging gaps (resolved July 7, sessions 4-5)

`peak_x_disp_m` is now written to the CSV. `rho=604` is now saved to the `.npz`. Output filename changed in session 5 to `phase_space_results_v2.csv`.

---

## What carries over to MPM, and what doesn't

**Carries over directly, validated on the pilot scene, confirmed working as of session 6:** `rho=604`, `size=(1.0, 1.6, 1.5)`, `pos=(1.0, 0.0, 0.75)` for the vehicle (box-proxy scale, see item 6 above for the sedan-scale divergence). `coup_friction` (0.4 in this entry, 0.55 in the live file as of July 10). `dt=4e-3, substeps=20` (substeps=32 in the live file as of July 9).

**Does not carry over:** `mu` has no MPM.Liquid equivalent. MPM domains need `3*dx` safety padding beyond the geometry, SPH domains don't.

**Vehicle representation does not change.** Stays a `Rigid` entity, `needs_coup=True`/`coup_friction`, against `MPM.Liquid` instead of `SPH.Liquid`. As of July 10: wired correctly, has not yet produced a completed run, see correction at top.

**Template for the migration:** `examples/coupling/water_wheel.py --solver mpm`, `examples/coupling/sand_wheel.py`, `examples/coupling/flush_cubes.py`.

---

## Possible shortcut

Cheng-Hsi already has a real flood scene splat dataset with a vehicle (`chhsiao93/hicss-splat` on Hugging Face), status of the vehicle as real mesh vs placeholder unconfirmed, asked him directly July 7. Luke Smith's Tutorial 3 (`taichi_mpm` codebase) also has a working real-gsplat-to-MPM bridge, demoed on a Toyota Corolla.

---

## Rebuild path (in priority order)

1. ~~Push the corrected script (mass, geometry, timestep) to this repo~~ **Done, July 7.**
2. ~~Fix the CSV and NPZ logging gaps~~ **Done, July 7.**
3. ~~Fix friction coupling and correct the viscosity overcorrection~~ **Done, July 7, session 5.**
4. ~~Get the MPM draft running on at least one condition~~ **Not actually done, see July 10 correction at top. Still the current top priority.**
5. Rerun all SPH conditions with the full corrected fix stack (mass, geometry, timestep, viscosity, friction, new CSV filename)
6. Sweep the MPM script across the full condition set, not just one, once it can complete even one condition
7. Test whether the drift result survives an enlarged/damped domain, the single most decisive open test on the closed-boundary question
8. Shoot and gsplat-reconstruct a real water-adjacent scene, or prototype against Cheng-Hsi's existing flood splat if confirmed usable
9. Write or adapt the PhysGaussian/Taichi bridge from real reconstructed geometry into simulatable particles
10. Rerun the full depth/velocity sweep on the corrected, real pipeline

See `kumar_july9_update/STATUS.md` for the current, fuller, actively-maintained version of this tracking table.

## Deadline note

DesignSafe DOI was originally self-targeted for July 10. This is self-imposed, not an NSF requirement. Given the corrections above, publishing before the rebuild would be premature. Target is now approximately July 21 to July 24, pending explicit confirmation with Kumar. The only real hard constraint is that a DOI must exist before the July 31 final paper.
