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
| **L1** | AR&R hazard scalar D x V, threshold 0.60 m²/s (4WD class), draft/interim criterion per the source report, not an endorsed safety standard | Shand et al. 2011 |
| **L2** | Genesis MPM weakly-compressible water + rigid vehicle coupling | This project |

---

## Status: pipeline under active correction (July 7, 2026, session 5)

The 23-condition L2 result below was run on synthetic box geometry using Genesis's SPH solver, not the MPM pipeline this repo describes. No real gsplat-reconstructed scene and no PhysGaussian bridge have been built yet. Full severity-ranked log, including two corrections made after an initial fix turned out to be wrong: [`PROVISIONAL_STATUS.md`](PROVISIONAL_STATUS.md).

Five bugs found and fixed across five sessions today, two of them (viscosity, friction) not caught until a source-cross-validated audit against this project's own technical review documents:

**Bug 1, vehicle had no mass set.** No `rho` argument meant the vehicle floated by construction. Fixed with `rho=604` on a resized box, holding the vehicle at roughly 1,450kg.

**Bug 2, vehicle spawned on top of the water, not in it.** Position was pinned to `water_depth`, so the vehicle's bottom face sat exactly at the surface at every depth tested. Fixed by pinning to the ground plane instead, `pos=(1.0, 0.0, 0.75)`.

**Bug 3, timestep too coarse.** `dt=1e-2` was 2.5x above Genesis's own MPM coupling example range, caused a numerical blowup at an extreme test case. Fixed with `dt=4e-3`.

**Bug 4, water viscosity, fixed wrong then corrected.** An earlier pass set `mu=0.001`, reasoning it matched real water's SI viscosity. That reasoning doesn't hold, Genesis's `mu` isn't SI dynamic viscosity, it's an internal WCSPH coefficient, and the engine's own default is `mu=0.005`. Corrected to `mu=0.005`, the documented default, not a guess in either direction.

**Bug 5, friction coupling never actually fixed.** `coup_friction=0.0` was flagged as a concern back when the mass bug was found, but the value itself was never changed until today. Every result up to and including the milestone table below ran with zero water-to-vehicle and vehicle-to-ground friction. Fixed to `coup_friction=0.4`, cited (Azhar et al. 2023, Smith et al. 2019, defensible range 0.3-0.6). Variable renamed from `frictionless_rigid` to `vehicle_rigid` since the old name was no longer accurate.

**Result below is from before bugs 4 and 5 were corrected, kept for the record, not yet re-trusted:**

| depth, velocity | AR&R hazard | peak x_disp | verdict |
|---|---|---|---|
| 0.3m, 1.5m/s | 0.45 | 0.0005m | FORD |
| 0.6m, 2.0m/s | 1.20 | 0.0125m | FORD |
| 0.6m, 2.5m/s | 1.50 | 0.0425m | FORD (close) |
| 1.0m, 3.0m/s | 3.00 | 0.1836m | NO-FORD |

Displacement scaled monotonically with severity, a genuine first for this project, but every row here ran with zero friction and an unvalidated viscosity value. This table needs a full rerun under the corrected 5-bug stack before any of these specific numbers are trusted or shown to anyone as a result. Output CSV filename also changed to `phase_space_results_v2.csv` to avoid a silent header-schema collision with the existing 6-column `data/phase_space_results.csv`.

**Also confirmed and still open, not yet fixed:** the domain is a closed, reflecting `CubeBoundary`, not an open channel, and the vehicle occupies roughly half the domain's length. Reflected waves off the downstream wall likely contaminate any run of meaningful length. This applies to the MPM version too. The single most decisive untested question: does the drift result survive an enlarged or damped domain.

Full detail on all five bugs, the boundary-condition question, and what carries over to the MPM migration: [`PROVISIONAL_STATUS.md`](PROVISIONAL_STATUS.md).

---

## Key finding (from the synthetic pilot, not yet the real-scene result)

**23 unique (depth, velocity) conditions** tested via L2 on the SPH/box-geometry pilot scene, before any of the July 7 fixes above.

- **L1 / L2 agreement rate: 30.4%** (7 of 23 conditions)
- **16 conditions:** L1 predicts FORD, L2 produces lateral drift exceeding 0.05 m (NO-FORD)
- **Friction-invariant:** drift stays at 0.328-0.400 m across friction coefficients 0.0-0.7

This is very likely a mass-bug artifact, not a physics result: a floating, near-massless body has ground normal force approximately zero, so friction is mathematically irrelevant regardless of its value, exactly the signature reported here. See the Status section above. Kept here, unedited, because it's the reason the rebuild exists, not because it's trusted.

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
citations/            Full bibliography and source PDFs for every threshold used
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

Each run appends one row to `phase_space_results_v2.csv`.

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

See `CITATION.cff` for citing this repository. See [`citations/README.md`](citations/README.md) for the full bibliography of sources this project's parameters and thresholds trace back to. DOI added upon DesignSafe publication.

## Acknowledgments

PI: Krishna Kumar (GeoElements Lab, UT Austin). Daily mentors: Hassan Iqbal, Cheng-Hsi Hsiao, Sarah Etter. Genesis container: Luke Smith (lsmith9003@utexas.edu). Funded by NSF SCIPE REU 2026 (Chishiki AI scholarship, GeoElements).
