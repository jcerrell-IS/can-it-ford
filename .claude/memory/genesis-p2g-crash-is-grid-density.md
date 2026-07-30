---
name: genesis-p2g-crash-is-grid-density
description: "Track 2 Genesis P2G CUDA_ERROR_ILLEGAL_ADDRESS is driven by grid_density (crashes >=96, runs at 64), not coup_softness, CFL, overlap, or 3*dx padding"
metadata: 
  node_type: memory
  type: project
  originSessionId: f757b3cb-cd6c-49bc-88dd-9934cd779aea
  modified: 2026-07-24T03:49:52.148Z
---

Measured on Vista GH200 (idev job 862053, node c642-042) on 2026-07-23, full log at
`logs/mpm_crash_retest_2026-07-23.txt` in the Vista repo.

The `CUDA_ERROR_ILLEGAL_ADDRESS` crash in `can_it_ford_L2_mpm.py` is at
`mpm_solver.py:592 substep_pre_coupling -> self.p2g(...)`, on the SECOND `scene.step()`
(t=0.008s). It is a function of `grid_density` alone:

- grid_density=64: full 500-step run completes, exit 0, real artifacts written.
- grid_density=96: crashes.
- grid_density=128 (the script default): crashes.

Ruled out by direct test, do not re-test these:
- coup_softness: 0.002, 0.01, 0.1 all crash identically at gd=128. Not the cause.
  (This closes the July 22 proposal recorded in SESSION_STATE.md.)
- CFL/timestep: gd=96 with SUBSTEPS=64 (substep_dt halved to 6.25e-5) still crashes.
- 3*dx domain padding: at every tested gd the vehicle and water clear the padded
  boundary. Tightest face is y at 0.0816m (gd=128). See [[genesis-3dx-padding-margin]].
- t=0 water/vehicle overlap (old B03): water spans x [-1.975,-1.625], vehicle starts at
  x -1.33, a 0.295m gap. No overlap in the live file.
- Pass-through causing the crash: n_penetrating is 0 at t=0 and the crash is at t=0.008s.

**Why:** this is the real bind for Track 2. Genesis issue #600's documented fix for MPM
particles passing through a thin rigid body is to raise grid_density to 128 or 256, and
that is exactly the setting that triggers the P2G crash. The two known problems have
opposite fixes.

**How to apply:** gd=64 is the only currently-runnable Track 2 setting, and its output is
NOT physically clean, see [[gd64-runs-have-heavy-particle-passthrough]]. Do not present a
gd=64 Genesis run as a validated result. Next diagnostic should target grid cell count /
indexing (gd=128 over this 7.0 x 2.0 x 2.6 m domain is 76.4M cells vs 9.6M at gd=64), not
stability coefficients.
