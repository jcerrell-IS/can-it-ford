# Can It Ford?

**Autonomous vehicle flood traversability via reconstruct-to-decide world models**

[![W&B](https://img.shields.io/badge/W%26B-experiment_tracking-yellow)](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-live_demo-blue)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
[![DesignSafe](https://img.shields.io/badge/DesignSafe-PRJ--6388-orange)](https://www.designsafe-ci.org)

*Josie Cerrell — NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar)*

---

> **Status (July 7, 2026): the finding below is provisional.** It was produced on synthetic box geometry using Genesis's SPH solver, with a vehicle mass bug that makes the simulated vehicle roughly 100 to 600 times lighter than a real car, so it floats by construction. This means the friction-invariant result below is a likely artifact, not yet a confirmed physical finding. Nothing below has been changed or deleted. Full corrections, severity ranking, and rebuild plan: [`PROVISIONAL_STATUS.md`](PROVISIONAL_STATUS.md).

---

## What this does

Given a real flooded road reconstructed from video using 3D Gaussian splatting, this pipeline answers: **can a specific autonomous vehicle ford this crossing?**

The experiment runs three methods side by side to find the simplest one that still gets the answer right.

| Level | Model | Source |
|---|---|---|
| **L0** | Static depth threshold (d >= 0.15 m => NO-FORD) | NWS Turn Around Don't Drown |
| **L1** | AR&R hazard scalar D x V, threshold 0.60 m²/s (4WD class) | Shand et al. 2011 |
| **L2** | Genesis MPM weakly-compressible water + rigid vehicle coupling | This project |

---

## Key finding

**23 unique (depth, velocity) conditions** tested via L2 Genesis MPM simulation on TACC Vista GH200 GPUs.

- **L1 / L2 agreement rate: 30.4%** (7 of 23 conditions)
- **16 conditions:** L1 predicts FORD, L2 produces lateral drift exceeding 0.05 m (NO-FORD)

Divergence covers depths 0.10–0.60 m at velocities 1.0–2.0 m/s, the entire practical wading range. This is a **structural failure**, not a tuning issue: D x V is a scalar and cannot represent directional persistent lateral drag, no matter what threshold or vehicle class you use.

Secondary finding: the result is **friction-invariant**. Lateral drift stays at 0.328–0.400 m across road friction coefficients 0.0–0.7, so the failure comes from the flow dynamics, not how the road surface is modeled (see `data/mu_sweep_results.csv`).

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

Add `--record` to save a headless video of the simulation (answers "what does the drift actually look like"):

```bash
apptainer exec --nv $GENESIS_PATH python3 simulation/can_it_ford_L2.py 0.30 1.5 --record
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

## Physical validation

`analysis/viability_audit.py` checks that the Genesis MPM runs are physically consistent, not just that they finished and produced an output.

Run it from the repo root after pulling `.npz` particle files from Vista:

```bash
scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/particles_d*.npz .
python3 analysis/viability_audit.py
```

The script loads particle positions and velocities from each run and checks two invariants:

- **Mass conservation:** total water mass is computed from particle count and fluid density (RHO0 = 1000 kg/m3). Flagged PASS or FAIL against the expected RHO0 x depth x width x length volume budget.
- **Momentum:** x and z momentum are summed across all particles at the end of each run. The x component shows how much lateral impulse the water transferred to the vehicle, which is what drives the drift verdict.

Results write to `viability_audit_results.csv` with one row per `.npz` file, covering: run conditions (depth, velocity, verdict), particle count, total mass, and x/z momentum.

The `.npz` files (per-run particle positions, velocities, and metadata) stay on Vista at `/work/11603/jcerrell0629/vista/` and are not committed to this repo. SCP them locally before running the audit.

---

## Data

| File | Description | Rows |
|---|---|---|
| `data/phase_space_results.csv` | L2 Genesis MPM results | 23 unique conditions |
| `data/scenario_sweep.csv` | Theoretical L0/L1 grid | 70 rows (depths 0.1–1.0 m x velocities 0.0–3.0 m/s) |
| `data/mu_sweep_results.csv` | Friction sensitivity at (d=0.30 m, v=1.5 m/s) | 8 conditions |

---

## Framing

This pipeline is a running version of the Section 3 orchestrator described in Thorpe et al. (arXiv:2605.30542, Physically Viable World Models). The N=23 tested conditions exceed the N >= 19 threshold for 95% marginal coverage conformal prediction (Luo et al. IJRR 2024), which is enough to build a formal safety certificate on L2 verdicts, once the corrections in `PROVISIONAL_STATUS.md` are resolved.

This pipeline handles the forward direction (known scene + known flood properties => traversability verdict). Hsiao and Kumar (arXiv:2507.09005) handle the inverse direction (images => material properties via Bayesian optimization). Together they form a closed perception-to-action loop.

---

## External assets

- **W&B experiment tracking:** [jcerrell29-claremont-mckenna-college/can-it-ford](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford) — 23+ L2 runs logged with depth, velocity, verdict, peak drift, and displacement
- **Live Gradio demo:** [josiecerrell/can-it-ford on HuggingFace Spaces](https://huggingface.co/spaces/josiecerrell/can-it-ford) — enter any (depth, velocity, vehicle class) and get L0/L1/L2 verdicts
- **Hailuo AI comparison:** [`figures/hailuo/`](figures/hailuo/) — three frames from a Hailuo AI video generation of a sedan in d=0.30 m, v=1.5 m/s flood conditions. Hailuo predicts FORD (visually plausible). L2 Genesis MPM predicts NO-FORD (lateral drift 0.328 m). This is the visual model vs physical model comparison for poster Panel 4.
- **Dataset DOI:** DesignSafe PRJ-6388 — pending publication, timing under revision (see `PROVISIONAL_STATUS.md`).

---

## Citation

See `CITATION.cff`. DOI will be added here upon DesignSafe publication.

## Acknowledgments

PI: Krishna Kumar (GeoElements Lab, UT Austin). Daily mentors: Hassan Iqbal, Cheng-Hsi Hsiao, Sarah Etter. Genesis container environment: Luke Smith (lsmith9003@utexas.edu). Funded by NSF SCIPE REU 2026 (Chishiki AI scholarship, GeoElements).
