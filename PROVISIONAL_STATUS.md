# Provisional Status and Corrections Log

This file exists so the project's revision history is visible, not hidden. The README's "Key finding" section is kept as originally written. This file documents what has changed since, and why, so a reader can see where this started and where it is going.

Last updated: July 7, 2026.

---

## Why this file exists

The README currently states the L2 finding (23 conditions, 16 divergence points, 30.4% L1/L2 agreement, friction-invariant drift) as settled fact. As of this update, that finding is **provisional**, pending a rebuild described below. Nothing in the README has been deleted. This file is the honest accounting layered on top.

---

## Confirmed corrections, in order of severity

### 1. Vehicle mass bug (most severe, discovered July 7)

The vehicle box in `simulation/can_it_ford_L2.py` never has an explicit density set. Genesis defaults to roughly 200 kg/m3. For the box dimensions used (0.4 x 0.2 x 0.15 m), this gives a simulated vehicle mass of approximately 2.4 to 12 kg, against a real vehicle curb weight of roughly 1,400 to 1,500 kg. This is a factor of 100 to 600 too light.

**Consequence:** the vehicle floats by construction. Ground normal force is near zero, which makes `coup_friction` mathematically irrelevant regardless of its value. The reported "friction-invariant drift" result (0.395 to 0.400 m across mu 0.0 to 0.7) is therefore a likely artifact of the mass bug, not yet a confirmed physical finding. This is the single highest-priority fix before any of the current 23-point dataset can be trusted.

### 2. Solver mismatch

All 23 conditions were run on Genesis's SPH solver, not MPM. The abstract and README describe the pipeline as Genesis MPM. This has not been corrected in the running code yet.

### 3. Synthetic geometry, not a reconstructed scene

No real gsplat-reconstructed flooded scene has been ingested anywhere in the pipeline. The water and vehicle are hardcoded Box morphs on a flat plane. No PhysGaussian kernel-to-particle bridge code exists yet, it has not been written. Tutorial 2's `bench.mov` is the only proof the gsplat half of the pipeline works end to end on its own.

### 4. Live script not yet on GitHub

The script actually being edited on Vista as of July 6 is `can_it_ford_L2_new.py`, not the `can_it_ford_L2.py` currently on `main`. `can_it_ford_L2_new.py` has never been pushed. Anyone reading this repo right now, including Kumar, is reading a stale version of the sim script. The Vista working directory itself is also not a git repository, pushes have to be done deliberately from a separate synced clone, not assumed automatic.

### 5. DRIFT_THRESHOLD = 0.05m has no citation

This value drives every NO-FORD verdict in L2 and currently has no published source behind it. Candidate fix under research: express it as a percentage of a published stability criterion (Smith 2019 Eq. 6 is a lead) rather than an absolute number.

### 6. Finding framing has changed twice

First reported (June 29) as 3 divergence points from 9 runs. Currently reported (July 3, and still what's in the README) as 16 divergence points from 23 runs, 30.4% agreement. Both versions were generated under the SPH/synthetic-geometry/mass-bug conditions above, so both are provisional until the rebuild lands.

---

## Possible shortcut

Luke Smith's Tutorial 3 (`taichi_mpm` codebase) already contains a working real-gsplat-to-MPM bridge: `preprocess.py` ingests a real `.ply` file, `run_mpm.py` simulates it, demoed on a Toyota Corolla gsplat. This may reduce the rebuild scope significantly. Open question for Hassan or Cheng-Hsi: can this Taichi MPM output feed a Genesis scene on Vista, or does it require its own separate pipeline.

---

## Rebuild path (in priority order)

1. Fix vehicle density so simulated mass matches a real curb weight, rerun the (0.30, 1.5) headline case first and check whether friction now matters
2. Migrate SPH.Liquid to MPM.Liquid in the solver
3. Shoot and gsplat-reconstruct a real water-adjacent scene (or evaluate Luke's Toyota Corolla dataset as a starting point)
4. Write or adapt the PhysGaussian/Taichi bridge from real reconstructed geometry into simulatable particles
5. Rerun the full depth/velocity sweep on the corrected, real pipeline
6. Push `can_it_ford_L2_new.py` (or its corrected successor) to `main` so the repo matches what is actually running

## Deadline note

DesignSafe DOI was originally self-targeted for July 10. This is self-imposed, not an NSF requirement. Given the corrections above, publishing before the rebuild would be premature. Target is now approximately July 21 to July 24, pending explicit confirmation with Kumar. The only real hard constraint is that a DOI must exist before the July 31 final paper.
