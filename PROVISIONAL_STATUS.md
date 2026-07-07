# Provisional Status and Corrections Log

This file exists so the project's revision history is visible, not hidden. The README's "Key finding" section is kept as originally written. This file documents what has changed since, and why, so a reader can see where this started and where it is going.

Last updated: July 7, 2026 (session 2).

---

## Why this file exists

The README currently states the L2 finding (23 conditions, 16 divergence points, 30.4% L1/L2 agreement, friction-invariant drift) as settled fact. As of this update, that finding is **provisional**, pending a rebuild described below. Nothing in the README has been deleted. This file is the honest accounting layered on top.

---

## July 7 session 2: mass and geometry bugs found and fixed, live on Vista (not yet pushed here)

This section documents same-day diagnostic work on `can_it_ford_L2_new.py`, done directly on Vista, ahead of the file itself being pushed to this repo.

**Bug A, vehicle mass unset.** Confirmed via `grep`: no `density` or `rho` anywhere in the original file. Vehicle used Genesis's internal default, giving an effective mass far below a real curb weight. Fixed by setting `rho=604` on the vehicle's `Rigid` material after also correcting the box size (see Bug B), targeting a mass-matched ~1,450 kg proxy.

**Bug B, vehicle geometry undersized and misplaced.** The vehicle box was 0.4 x 0.2 x 0.15 m, roughly 10x too small per dimension versus a real car, and was positioned with `pos=(1.0, 0.0, water_depth + 0.075)`. Given the box height of 0.15m, this placed the vehicle's bottom face exactly at the water's top surface for every depth tested, meaning the vehicle sat balanced on top of the water rather than submerged in it. Confirmed visually by watching the rendered video. Fixed by resizing to `size=(1.0, 1.6, 1.5)` and repositioning to `pos=(1.0, 0.0, 0.75)`, pinning the vehicle to the ground plane independent of `water_depth`, so shallower or deeper water submerges more or less of the vehicle the way real fording works.

**One theory ruled out, not just deprioritized.** Genesis's SPH solver defaults `particle_size` to 0.02m, giving roughly 10+ particles across even the smallest original vehicle face. This is fine resolution, not the coarse-grid failure mode Genesis issue #600 describes for MPM. The near-zero displacement seen before these fixes is attributable to Bugs A and B above, not to a weak or broken SPH-rigid coupling kernel.

**Result after both fixes, on the same synthetic box/plane scene (still SPH, not yet MPM, not yet a real gsplat scene):**
- All 24 originally-tested (depth, velocity) pairs plus a v=8.0 m/s stress test returned FORD with near-zero displacement (0.0000-0.0004m) before Bug B's fix.
- After Bug B's fix, a genuinely hazardous case (d=0.6m, v=2.0m/s, AR&R hazard D x V = 1.2, well above the 4WD threshold of 0.60) produced 0.0125m peak displacement, a real, severity-scaled result, still under the current 0.05m DRIFT_THRESHOLD (still FORD).
- A borderline-safe case (d=0.3m, v=1.5m/s, hazard = 0.45, below the 4WD threshold) produced 0.0005m, consistent with L1's own prediction that this condition is not clearly hazardous.
- An out-of-range stress test (d=1.0m, v=3.0m/s) produced a displacement spike to roughly 1m with a velocity vector pointing backward against the flow, followed by the session disconnecting. Read as a numerical instability at parameters well outside anything validated, not a real physical result. Not yet re-tested at a more moderate extension (e.g. v=2.5m/s) to find the actual stable ceiling for the current timestep.

**What this means for the original 23-point finding:** very likely was a mass-and-geometry artifact, not real physics, consistent with the "Bug 1" entry below. The corrected setup does produce real, severity-scaled displacement, which is the first physically plausible signal this project has produced. Still not the real-scene MPM pipeline described in the abstract.

**Still open:** DRIFT_THRESHOLD's citation (item 5 below), the CSV logging bugs (item 7 below), and finding the stable velocity ceiling for the current timestep before trusting any extreme-condition test.

---

## Confirmed corrections, in order of severity

### 1. Vehicle mass bug (discovered July 7, fixed same day)

The vehicle box in `can_it_ford_L2_new.py` never had an explicit density set. Genesis defaulted to an internal density giving a simulated vehicle mass far below a real curb weight of roughly 1,400 to 1,500 kg. The vehicle floated by construction, making `coup_friction` mathematically irrelevant regardless of its value. The originally reported "friction-invariant drift" result (0.395 to 0.400 m across mu 0.0 to 0.7) is a likely artifact of this bug, not a confirmed physical finding. Fixed July 7 by setting explicit density; see session 2 section above for the full fix and result.

### 1b. Vehicle geometry and placement bug (discovered and fixed July 7, same session as above)

See session 2 section above. Vehicle was undersized and spawned resting on top of the water surface rather than submerged in it, independent of the mass bug. Both bugs needed fixing before any displacement number was trustworthy.

### 2. Solver mismatch

All results to date were run on Genesis's SPH solver, not MPM. The abstract and README describe the pipeline as Genesis MPM. Not yet corrected in the running code.

### 3. Synthetic geometry, not a reconstructed scene

No real gsplat-reconstructed flooded scene has been ingested anywhere in the pipeline. The water and vehicle are hardcoded Box morphs on a flat plane. No PhysGaussian kernel-to-particle bridge code exists yet. Tutorial 2's `bench.mov` is the only proof the gsplat half of the pipeline works end to end on its own.

### 4. Live script not yet on GitHub

`can_it_ford_L2_new.py`, the file with all of the July 7 fixes described above, has still not been pushed to this repo. Only the older, pre-fix `can_it_ford_L2.py` is on `main`. The Vista working directory is flat (not a `simulation/` subdirectory) and is not itself a git repository, so pushes have to be done deliberately from a separate synced clone.

### 5. DRIFT_THRESHOLD = 0.05m has no citation

This value drives every NO-FORD verdict in L2 and currently has no published source behind it. Now more consequential than before, since it is deciding verdicts on physically plausible displacement numbers rather than obviously-broken ones. Candidate fix under research: express it as a percentage of a published stability criterion (Smith 2019 Eq. 6 is a lead) rather than an absolute number.

### 6. Finding framing has changed twice

First reported (June 29) as 3 divergence points from 9 runs. Later reported (July 3) as 16 divergence points from 23 runs, 30.4% agreement. Both versions were generated under the mass-and-geometry-bugged conditions described above.

### 7. CSV logging bugs (discovered July 7)

`peak_x_disp`, the value the FORD/NO-FORD verdict is actually based on, is never written to `phase_space_results.csv`, only printed to terminal and saved in per-run `.npz` files. The CSV cannot verify its own verdicts. Separately, the `max_vel_ms` column tracks the vehicle's initial settling speed, not flow-driven velocity, and is not a meaningful physics measurement as currently computed. Both need a schema fix (a new CSV, not a patch to the existing one, since the old file's rows are already written under the old column set).

---

## Possible shortcut

Luke Smith's Tutorial 3 (`taichi_mpm` codebase) already contains a working real-gsplat-to-MPM bridge: `preprocess.py` ingests a real `.ply` file, `run_mpm.py` simulates it, demoed on a Toyota Corolla gsplat. This may reduce the rebuild scope significantly. Open question for Hassan or Cheng-Hsi: can this Taichi MPM output feed a Genesis scene on Vista, or does it require its own separate pipeline.

---

## Rebuild path (in priority order)

1. Push `can_it_ford_L2_new.py`, with the mass and geometry fixes, to this repo so it matches what is actually running
2. Find the stable velocity ceiling for the current timestep, then fix the CSV logging bugs (both independent of the items below, can happen any time)
3. Migrate SPH.Liquid to MPM.Liquid in the solver
4. Shoot and gsplat-reconstruct a real water-adjacent scene (or evaluate Luke's Toyota Corolla dataset as a starting point)
5. Write or adapt the PhysGaussian/Taichi bridge from real reconstructed geometry into simulatable particles
6. Rerun the full depth/velocity sweep on the corrected, real pipeline

## Deadline note

DesignSafe DOI was originally self-targeted for July 10. This is self-imposed, not an NSF requirement. Given the corrections above, publishing before the rebuild would be premature. Target is now approximately July 21 to July 24, pending explicit confirmation with Kumar. The only real hard constraint is that a DOI must exist before the July 31 final paper.
