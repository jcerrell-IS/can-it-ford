# Can It Ford?

**Autonomous vehicle flood traversability via reconstruct-to-decide world models**

[![W&B](https://img.shields.io/badge/W%26B-experiment_tracking-yellow)](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-live_demo-blue)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
[![DesignSafe](https://img.shields.io/badge/DesignSafe-PRJ--6388-orange)](https://www.designsafe-ci.org)

*Josie Cerrell — NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar)*

---

## What this does

Given a real flooded road reconstructed from video using 3D Gaussian splatting, this pipeline answers: **can a specific autonomous vehicle ford this crossing?**

Three methods run side by side to find the simplest one that still gets the answer right.

| Level | Model | Source |
|---|---|---|
| **L0** | Static depth threshold (d >= 0.15 m => NO-FORD) | NWS Turn Around Don't Drown |
| **L1** | AR&R hazard scalar D x V, threshold 0.60 m²/s (4WD class) | Shand et al. 2011 |
| **L2** | Genesis MPM weakly-compressible water + rigid vehicle coupling | This project |

---

## Status: pipeline under active correction (July 7, 2026)

The 23-condition L2 result below was run on synthetic box geometry using Genesis's SPH solver, not the MPM pipeline this repo describes. No real gsplat-reconstructed scene and no PhysGaussian bridge have been built yet. Full severity-ranked log: [`PROVISIONAL_STATUS.md`](PROVISIONAL_STATUS.md).

Three bugs found and fixed this session, in the order I found them:

**Bug 1: vehicle had no mass set.**

```python
# before
frictionless_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.0)
```

No `rho` argument means Genesis falls back to its internal default. For the original box size (0.4 x 0.2 x 0.15 m) that gave an effective mass somewhere in the 2.4-12kg range depending on what the true default resolves to, against a real curb weight of roughly 1,400-1,500kg. The vehicle floated. `coup_friction` was mathematically irrelevant at any value because ground normal force was near zero.

```python
# after
frictionless_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.0, rho=604)
```

**Bug 2: vehicle spawned on top of the water, not in it.**

```python
# before
vehicle = scene.add_entity(
    material=frictionless_rigid,
    morph=gs.morphs.Box(
        pos=(1.0, 0.0, water_depth + 0.075),
        size=(0.4, 0.2, 0.15),
        fixed=False,
    ),
)
```

The water box is centered at `water_depth / 2.0` with height `water_depth`, so its top surface sits at exactly `z = water_depth`. The vehicle's `pos.z = water_depth + 0.075` with box height 0.15 puts its bottom face at exactly `z = water_depth` too, every single depth tested. I confirmed this visually by rendering `simulation_d0p6_v1p5.mp4` before the fix: the vehicle sits balanced on the surface, not submerged.

```python
# after
vehicle = scene.add_entity(
    material=frictionless_rigid,
    morph=gs.morphs.Box(
        pos=(1.0, 0.0, 0.75),
        size=(1.0, 1.6, 1.5),
        fixed=False,
    ),
)
```

Pinned to the ground plane instead of to `water_depth`, so shallow water partially submerges it and deep water submerges more of it, the way fording actually works. Also scaled the box up from a 10x-undersized proxy to something closer to real vehicle dimensions, and recomputed `rho` for the new volume to keep the mass target the same (~1,450kg for the new 2.4 m³ box: `1450 / 2.4 = 604`).

**Bug 3: timestep too coarse.**

```python
# before
sim_options=gs.options.SimOptions(dt=1e-2, substeps=10),
```

After fixing mass and geometry, a stress test (d=1.0m, v=3.0m/s) spiked to a 1m displacement with a velocity vector pointing backward against the flow, then crashed. That's a numerical blowup, not real physics. Genesis's own `flush_cubes.py` example uses `dt=4e-3, substeps=20` for MPM liquid coupling, 2.5x finer than what this script was running.

```python
# after
sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
```

Reran the same case that crashed. Clean finish, no crash, oscillatory transient (push, overshoot, partial recovery), velocity components stayed bounded under 0.5 m/s the whole run.

**Result after all three fixes, still on SPH, still on the synthetic box/plane scene:**

| depth, velocity | AR&R hazard | peak x_disp | verdict |
|---|---|---|---|
| 0.3m, 1.5m/s | 0.45 | 0.0005m | FORD |
| 0.6m, 2.0m/s | 1.20 | 0.0125m | FORD |
| 0.6m, 2.5m/s | 1.50 | 0.0425m | FORD (close) |
| 1.0m, 3.0m/s | 3.00 | 0.1836m | NO-FORD |

Displacement now scales monotonically with severity, for the first time this project has produced that. The 1.0m/3.0m/s case is 3.7x over the 0.05m `DRIFT_THRESHOLD`, and it agrees with the AR&R L1 hazard flag at that same condition (hazard=3.0, far above the 0.60 threshold), a real cross-check pass between the two methods on corrected physics.

Sanity-checked this before trusting it: compared the water's total x-momentum at the final step against the vehicle's estimated momentum change. Water: 320.1 kg·m/s. Vehicle: roughly 1450 x 0.47 = 681.5 kg·m/s. Same order of magnitude, not exact, not expected to be exact since this isn't a closed system. Rules out the push coming from nowhere, doesn't prove the transfer is exact.

**One theory ruled out, checked against Genesis's actual source, not assumed:** SPH `particle_size` defaults to 0.02m, giving 10+ particles across even the original undersized vehicle face. That's fine resolution. The near-zero displacement was Bugs 1 and 2 above, not a weak SPH-rigid coupling kernel.

**Still open:** `DRIFT_THRESHOLD=0.05m` has no citation. `peak_x_disp`, the value the verdict is actually based on, is never written to `phase_space_results.csv`, only printed to terminal and saved per-run in `.npz`. `max_vel_ms` in the CSV tracks the vehicle's initial settling speed, not flow velocity. `rho` isn't saved to the `.npz` either, blocking a WCSPH density-bound check. None of these are fixed yet.

---

## Key finding (from the synthetic pilot, not yet the real-scene result)

**23 unique (depth, velocity) conditions** tested via L2 on the SPH/box-geometry pilot scene, before the July 7 mass, geometry, and timestep fixes above.

- **L1 / L2 agreement rate: 30.4%** (7 of 23 conditions)
- **16 conditions:** L1 predicts FORD, L2 produces lateral drift exceeding 0.05 m (NO-FORD)
- **Friction-invariant:** drift stays at 0.328-0.400 m across friction coefficients 0.0-0.7

This is very likely a mass-bug artifact, not a physics result. See the Status section above. Kept here, unedited, because it's the reason the rebuild exists, not because it's trusted.

---

## Pipeline

```
video  →  gsplat (LS6 A100)  →  PhysGaussian MPM seeding  →  Genesis MPM (Vista GH200)  →  FORD / NO-FORD
```

The `simulation/` directory has scripts for all three abstraction levels.

---

## Repo structure

```
simulation/           L0, L1, L2 scripts — run on Vista GH200 via Apptainer
analysis/             Phase space figures, W&B logging, physical validation
data/                 Experiment CSVs (L2 results, L0/L1 grid, friction sweep)
figures/              Output figures and comparison assets
scripts/              Utility: data sync, manifest, Vista pull
designsafe-staging/   Files staged for DesignSafe DOI (PRJ-6388, pending publication)
```

---

## Running the simulation

**L2 on Vista (GH200 GPU):**

```bash
idev -N 1 -n 1 -p gh -t 1:30:00
module load tacc-apptainer
export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif
cd /work/11603/jcerrell0629/vista/
apptainer exec --nv $GENESIS_PATH python3 simulation/can_it_ford_L2.py <depth_m> <velocity_ms>
```

Add `--record` to save a headless video:

```bash
apptainer exec --nv $GENESIS_PATH python3 simulation/can_it_ford_L2.py 0.30 1.5 --record
```

Each run appends one row to `data/phase_space_results.csv`.

**L0 and L1 (local, no GPU needed):**

```bash
python3 simulation/can_it_ford_L0.py <depth_m>
python3 simulation/can_it_ford_L1.py <depth_m> <velocity_ms> [vehicle_class]
```

Vehicle class options: `sedan`, `large_passenger`, `large_4wd` (default).

**Phase space figure (MacBook, conda env `can-it-ford`):**

```bash
python3 analysis/make_phase_space.py
```

---

## Physical validation

`analysis/viability_audit.py` checks mass conservation and momentum transfer from `.npz` particle files, not just that a run finished.

```bash
scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/particles_d*.npz .
python3 analysis/viability_audit.py
```

Writes `viability_audit_results.csv`, one row per `.npz` file: run conditions, particle count, total mass, x/z momentum.

`.npz` files stay on Vista, not committed here. SCP before running.

---

## Data

| File | Description | Rows |
|---|---|---|
| `data/phase_space_results.csv` | L2 pilot results (pre-fix, see Status) | 23 unique conditions |
| `data/scenario_sweep.csv` | Theoretical L0/L1 grid | 70 rows (depths 0.1-1.0 m x velocities 0.0-3.0 m/s) |
| `data/mu_sweep_results.csv` | Friction sensitivity at (d=0.30 m, v=1.5 m/s) | 8 conditions |
| `data/l2_results_from_wandb.csv` | Confirmed L2 runs pulled from W&B API | 9 conditions |

---

## Framing

This pipeline is a running version of the Section 3 orchestrator in Thorpe et al. (arXiv:2605.30542, Physically Viable World Models). N=23 exceeds the N >= 19 threshold for 95% marginal-coverage conformal prediction (Luo et al. IJRR 2024), useful once the corrections in `PROVISIONAL_STATUS.md` are resolved.

Forward direction: known scene + known flood properties => traversability verdict. Hsiao and Kumar (arXiv:2507.09005) handle the inverse direction: images => material properties via Bayesian optimization.

---

## External assets

- **W&B:** [jcerrell29-claremont-mckenna-college/can-it-ford](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
- **Gradio demo:** [josiecerrell/can-it-ford on HuggingFace Spaces](https://huggingface.co/spaces/josiecerrell/can-it-ford)
- **Hailuo comparison:** [`figures/hailuo/`](figures/hailuo/), Hailuo predicts FORD at d=0.30m/v=1.5m/s, pilot L2 predicts NO-FORD, visual-model-vs-physical-model comparison for poster Panel 4
- **Dataset DOI:** DesignSafe PRJ-6388, timing under revision, see `PROVISIONAL_STATUS.md`

---

## Citation

See `CITATION.cff`. DOI added upon DesignSafe publication.

## Acknowledgments

PI: Krishna Kumar (GeoElements Lab, UT Austin). Daily mentors: Hassan Iqbal, Cheng-Hsi Hsiao, Sarah Etter. Genesis container: Luke Smith (lsmith9003@utexas.edu). Funded by NSF SCIPE REU 2026 (Chishiki AI scholarship, GeoElements).
