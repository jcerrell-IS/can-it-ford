# Can It Ford?

**Autonomous vehicle flood traversability via reconstruct-to-decide world models**

[![W&B](https://img.shields.io/badge/W%26B-experiment_tracking-yellow)](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-live_demo-blue)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
[![DesignSafe](https://img.shields.io/badge/DesignSafe-PRJ--6388-orange)](https://www.designsafe-ci.org)

*Josie Cerrell — NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar)*

---

## What this does

Given a real flooded road reconstructed from video using 3D Gaussian splatting, this pipeline answers: **can a specific autonomous vehicle ford this crossing?**

The central experiment compares three abstraction levels to find the simplest physical model sufficient to answer correctly.

| Level | Model | Source |
|---|---|---|
| **L0** | Static depth threshold (d >= 0.15 m => NO-FORD) | NWS Turn Around Don't Drown |
| **L1** | AR&R hazard scalar D x V, threshold 0.60 m²/s (4WD class) | Shand et al. 2011 |
| **L2** | Genesis MPM weakly-compressible water + rigid vehicle coupling | This project |

---

## Key finding

**23 unique (depth, velocity) conditions** tested via full L2 Genesis MPM simulation on TACC Vista GH200 GPUs.

- **L1 / L2 agreement rate: 30.4%** (7 of 23 conditions)
- **16 conditions:** L1 predicts FORD, L2 produces lateral drift exceeding 0.05 m (NO-FORD)

Divergence spans depths 0.10–0.60 m at velocities 1.0–2.0 m/s, covering the entire practical wading regime. This is **mechanism failure**, not threshold miscalibration: D x V is a scalar and structurally cannot represent directional persistent lateral drag, regardless of vehicle class or threshold value.

Secondary finding: the result is **friction-invariant**. Lateral drift holds at 0.328–0.400 m across road friction coefficients 0.0–0.7, confirming the failure originates in flow dynamics, not surface modeling (see `data/mu_sweep_results.csv`).

---

## Pipeline

```
video  →  gsplat (LS6 A100)  →  PhysGaussian MPM seeding  →  Genesis MPM (Vista GH200)  →  FORD / NO-FORD
```

The three abstraction levels are evaluated at each (depth, velocity) query point. The `simulation/` directory contains the scripts for all three levels.

---

## Repo structure

```
simulation/           L0, L1, L2 scripts — run on Vista GH200 via Apptainer
analysis/             Phase space figure generation, W&B experiment logging
data/                 Experiment CSVs (L2 results, L0/L1 theoretical grid, friction sweep)
figures/              Output figures and comparison assets
scripts/              Utility: data sync, manifest generation, Vista pull
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

Each run appends one row to `data/phase_space_results.csv` with depth, velocity, verdict, peak drift, and displacement.

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

## Data

| File | Description | Rows |
|---|---|---|
| `data/phase_space_results.csv` | L2 Genesis MPM simulation results | 23 unique conditions |
| `data/scenario_sweep.csv` | Theoretical L0/L1 grid | 70 rows (depths 0.1–1.0 m x velocities 0.0–3.0 m/s) |
| `data/mu_sweep_results.csv` | Friction coefficient sensitivity at (d=0.30 m, v=1.5 m/s) | 8 conditions |

Large particle output files (`.npz`, per-run positions/velocities) are stored on TACC Vista at `/work/11603/jcerrell0629/vista/` and not committed to this repo.

---

## Framing

This pipeline provides a concrete instantiation of the Section 3 orchestrator described in Thorpe et al. (arXiv:2605.30542, Physically Viable World Models). The N=23 calibration samples exceed the N >= 19 threshold for 95% marginal coverage conformal prediction (Luo et al. IJRR 2024), enabling formal safety guarantees on L2 verdicts.

The forward direction of this pipeline (known scene + known flood properties => traversability verdict) complements the inverse direction demonstrated by Hsiao and Kumar (arXiv:2507.09005), forming a closed perception-to-action loop.

---

## External assets

- **W&B experiment tracking:** [jcerrell29-claremont-mckenna-college/can-it-ford](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
- **Live Gradio demo:** [josiecerrell/can-it-ford on HuggingFace](https://huggingface.co/spaces/josiecerrell/can-it-ford)
- **Dataset DOI:** DesignSafe PRJ-6388 (pending publication July 2026)

---

## Citation

See `CITATION.cff`. DOI will be added here upon DesignSafe publication.

## Acknowledgments

PI: Krishna Kumar (GeoElements Lab, UT Austin). Daily mentors: Hassan Iqbal, Cheng-Hsi Hsiao. Genesis container environment: Luke Smith (lsmith9003@utexas.edu). Funded by NSF SCIPE REU 2026 (Chishiki AI scholarship, GeoElements).
