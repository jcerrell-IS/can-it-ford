# GATES
Values read from renders/yaris_render_s1/g64_m1100/summary.json unless noted.

| gate | measured | verdict |
|---|---|---|
| G0 analytic Coulomb benchmark | `pytest tests/test_analytic_benchmarks.py -k incline` on c642-091 (GH200), 2026-07-26 00:2x CDT: **2 passed, 2 deselected in 30.60s**, pytest 9.1.1, Python 3.12.13 | **PASS** |
| G1 determinism | two loads in one process gave identical results (`determinism_identical: true`) | PASS |
| G2 parity | 0 of 1335 columns dropped (`parity_odd_columns_dropped: 0`) | PASS |
| G3 domain containment | 0 particle-frames outside the domain (`C3_oob_particle_frames: 0`) | PASS |
| G4 solidification | fill ratio 1.00244, solid volume 3.5514 m3 vs hull 3.5427 m3; the hull matches the canonical yaris_coarse_v1l_watertight.ply volume exactly | PASS |
| G5 penetration | max water fraction in vehicle AABB 10.67 pct (standing water) vs 3.71 pct (dry start), band is under 10 pct | FAIL, artifact hypothesis |
| G6 density plausibility | realized rho 309.74 kg/m3 against a 100 to 300 band | FAIL by 3.2 pct |
| G7 grid convergence | n_grid 64 vs 128 at nominally identical configuration: final dx 0.090317 m vs 0.032420 m, a 64.1 pct change. Water volume differs by 19.8 pct between the two runs, so this is NOT yet a validated single-variable comparison. See docs/g64_vs_g128_2026-07-26.txt | **OPEN** |

## G0, what it establishes
`tests/test_analytic_benchmarks.py` contains two closed-form Coulomb benchmarks shipped with
kks32/mpm-engine: a sliding block on an incline at mu = 0.3 asserted against the analytic
a = g(sin theta - mu cos theta) within 15 pct, and a static-hold case at mu = 0.8 asserting
|v_x| < 0.02 after 70 steps. Both pass on the GH200 in the project's own venv. This is a code
verification result in the ASME V&V 20 sense: the solver reproduces an analytic solution with a
known answer. It says nothing about whether the flood configuration is right, only that the
Coulomb contact model is implemented correctly.

Run route: nested SSH to c642-091, the node holding allocation 866601. Under that route
SLURM_JOB_ID and SLURM_PARTITION are empty, so this ran on the allocated node but not inside the
job step. Recorded here rather than claimed as in-allocation accounting.

## G5, why the failure is most likely a metric artifact
The metric tracks displacement, not resolution. Dry start moves 0.090 m and reads 3.71 pct.
Standing water moves 0.659 m and reads 10.67 pct. An axis-aligned bounding box sweeps up water
legitimately outside the hull as the body translates, and the parity fill deliberately leaves the
wheel wells and underbody void empty. Genuine tunnelling would track grid resolution and contact
stiffness, not translation distance. Corroborating: zero out-of-bounds particles in both runs.
The discriminating test is a mesh-containment count instead of an AABB count; not yet run.

## G6, context
309.74 kg/m3 is 3.2 pct above the project's 100 to 300 plausibility band (CLAUDE.md:14-15). It is
the closest to plausible of the three masses; 1609 kg and 2337 kg on the same hull give 453 and 658.
All runs share identical geometry, so the mass sweep is a mass sensitivity study, not a vehicle
class comparison.

## G7, what is open
The n_grid 128 run (out/yaris_v2_eta1e3_g128) is complete: 90 frames, h = 0.036803 exactly half of
the 64 run's 0.073607, floor = 6h in both, vehicle solid volume differing by 0.11 pct. But n_water
is 225616 against 23532, a 9.59x scaling where an identical physical water region would give exactly
8.00x, and total water volume differs by 19.8 pct. Until the per-frame local_depth traces are
compared, the 64 pct displacement change cannot be attributed to discretization alone.
