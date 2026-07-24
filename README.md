# Can It Ford?

**Autonomous vehicle flood traversability via reconstruct-to-decide world models**

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-green.svg)](LICENSE)
[![W&B](https://img.shields.io/badge/W%26B-experiment_tracking-yellow)](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-live_demo-blue)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
[![DesignSafe](https://img.shields.io/badge/DesignSafe-PRJ--6388-orange)](https://www.designsafe-ci.org)

*Josie Cerrell, NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar)*

---

## What this does

Given a real flooded road reconstructed from video using 3D Gaussian splatting, this pipeline answers one question: **can a specific vehicle ford this crossing?**

Three methods run side by side, from cheapest to most expensive, to find the simplest model that still gets the answer right. The interesting result is where they disagree.

| Level | Model | Source |
|---|---|---|
| **L0** | Static depth threshold (d >= 0.15 m gives NO-FORD) | [NWS Turn Around Don't Drown](https://www.weather.gov/safety/flood-turn-around-dont-drown) |
| **L1** | AR&R hazard scalar D x V, threshold 0.60 m2/s (Large 4WD class). Draft/interim criterion from the source report, not an endorsed safety standard. | [Shand et al. 2011](citations/ARR_Project_10_Stage2_Report_Final.pdf) |
| **L2** | Coupled particle simulation: weakly compressible water plus a rigid vehicle body, verdict from lateral drift | This project |

The abstraction ladder is a running instance of the Section 3 orchestrator in [Physically Viable World Models (Thorpe et al. 2026, arXiv:2605.30542)](https://arxiv.org/abs/2605.30542). Forward direction here (known scene plus known flood gives a verdict) is the sibling of the inverse direction in [Hsiao and Kumar 2025 (arXiv:2507.09005)](https://arxiv.org/abs/2507.09005), which recovers material properties from images.

---

## Pipeline

<img src="https://raw.githubusercontent.com/jcerrell-IS/can-it-ford/main/figures/can_it_ford_pipeline_diagram.svg" alt="Can It Ford pipeline diagram" width="820">

```
video  ->  gsplat (LS6 A100)  ->  splat/mesh to MPM particles  ->  MPM water + rigid vehicle coupling (Vista GH200)  ->  FORD / NO-FORD
```

The splat-to-particle bridge is intended to reuse [PhysGaussian (Xie et al. 2023, arXiv:2311.12198)](https://arxiv.org/abs/2311.12198) extraction logic on top of [3D Gaussian Splatting (Kerbl et al. 2023, arXiv:2308.04079)](https://arxiv.org/abs/2308.04079). See the Status section for which stages are actually built today.

---

## Status (July 9 snapshot, re-verified live 2026-07-23): pipeline under active rebuild

*Re-verification basis for this date: the bullets below were checked against the live tree at `daf453e` (2026-07-23), not against a summary. The P2G/`CUDA_ERROR_ILLEGAL_ADDRESS` crash is still open per `d869f93` ("Log confirmed non-fix of P2G crash post position-change"), so the "no MPM verdict" bullet stands. Key-finding numbers below were recomputed from `data/phase_space_results.csv` this pass and match `07c8c65`. The Yaris and Track 1 v2 lines were checked against disk and against Vista (`squeue`, `data/`) on 2026-07-23.*

**The authoritative technical log is [`kumar_july9_update/STATUS.md`](kumar_july9_update/STATUS.md).** The severity-ranked bug history is in [`PROVISIONAL_STATUS.md`](PROVISIONAL_STATUS.md). Read those before trusting any number in this repo. Short version:

- **The L2 solver is migrating from SPH to MPM.** The 23-condition result below was produced on synthetic box geometry with Genesis's SPH solver, as a pilot, not with the MPM pipeline the project targets. That SPH pilot is now closed.
- **The current directed L2 engine is [`kks32/mpm-engine`](https://github.com/kks32/mpm-engine)** (per Kumar's instruction), with a box/SDF collider for the vehicle. A parallel [Genesis](https://github.com/Genesis-Embodied-AI/Genesis) MPM script (`simulation/can_it_ford_L2_mpm.py`) also exists.
- **The MPM run does not yet complete at vehicle scale.** The latest attempt crashes with `CUDA_ERROR_ILLEGAL_ADDRESS` on the first coupled substep. No MPM FORD/NO-FORD verdict exists yet. Tracked in [#1](../../issues/1).
- **The vehicle is still a box proxy, not a real car mesh.** The Genesis Track 2 script (`can_it_ford_L2_mpm.py`) uses a generic `size=(1.0, 1.6, 1.5)` box; the `kks32/mpm-engine` Track 1 script (`box_sdf_collider_setup.py`) uses the real sedan bounding box `(4.66, 1.79, 1.44)`. Cited real vehicle parameters exist in `vehicle_params.py` but are not yet wired into the Genesis solver ([#7](../../issues/7)).
- **Track 1's v2 sweep is partially valid and the Yaris real-mesh sweep has produced nothing.** In [`data/track1_sweep_v2/manifest.csv`](data/track1_sweep_v2/manifest.csv) (36 rows, `kks32/mpm-engine` MPM, `n_grid=64`), **24 of 36 rows are density-plausible**: all 12 sedan and all 12 pickup rows pass, all 12 SUV rows fail at 308.13 kg/m3 (2.7 percent over the 100-300 kg/m3 band), and the schema further reduces the reportable set to 21 after excluding 3 under-resolved single-layer pickup cells at 0.15 m depth. Caveat on what "valid" means here: all 36 geometries are `truck_trimmed.ply` anisotropically warped by `fit_to_bbox` to each class bounding box, not per-class real meshes, and the failure-mode classifier rejects all 36 rows because the timeseries predate the `vx,vy,vz` columns it requires. The `--vehicle yaris` real-mesh sweep (`scripts/run_yaris_v2_prov.sbatch`, 1 vehicle x 4 depths x 3 velocities) stands at **0 of 12 runs**, verified live on Vista 2026-07-23: no `data/*yaris*` output directory, `logs/` empty apart from `.gitkeep`, and `squeue -u jcerrell0629` returning no queued or running job. No Yaris verdict exists to cite or plot.
- **No real gsplat-reconstructed flooded scene has been ingested yet**, and no PhysGaussian/Taichi splat-to-particle bridge exists in code. A candidate vehicle reconstruction (`truck_trimmed.ply`) exists in working files but was closed on July 10 as not vehicle-proportioned (extents 1.447 x 0.450 x 0.411 m), so the box proxy remains the committed geometry. It is not connected to the pipeline ([#6](../../issues/6)).
- **Coupling friction is set to 0.55, and the number is citation-accurate while the application of it is not yet justified.** Separate these two claims, they are not the same claim:
  - *The number.* 0.55 traces to Azhar, Pauwels & Bui 2023, "Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements," *Journal of Flood Risk Management* 16(2):e12885, DOI [10.1111/jfr3.12885](https://doi.org/10.1111/jfr3.12885). There it is a **physical Coulomb friction coefficient** for a passive rigid vehicle, quoted in the model setup alongside a COG height of 0.45 m and a weight of 1097 kg, for a DualSPHysics model matched to a 1:14 scale physical model. Two precision notes: the paper adopts 0.55 "in accordance with" prior literature rather than measuring it in its own scale-model traction testing (so the earlier README phrase "the exact matched-scale-model coefficient" overstated it, and is retracted here), and the verbatim setup quote is recorded in [`citations/Bibliographic and Content Verification...md`](citations/) while [`analysis/failure_mode_citations.md`](analysis/failure_mode_citations.md) still carries this as UNRESOLVED because Wiley returns 403 to crawlers and scite has no open-access full text to re-query. That is a retrieval failure, not a contradiction, but the two files disagree and the newer one has not been updated.
  - *The application.* Genesis `coup_friction` is a **numerical solver-coupling coefficient**, a different kind of quantity from Coulomb friction, not a dimensionless tyre-on-pavement ratio. Setting `coup_friction = 0.55` because Azhar's Coulomb mu is 0.55 is an **open modeling assumption, not a proven equivalence**, and no calibration establishing that the two are interchangeable has been done here. This exact conflation (a physical Coulomb coefficient fed into a numerical coupling-impulse coefficient as if they were the same quantity) is named in the provenance-audit skill's own Known-Error Register. Do not present 0.55 as a settled, sourced value for this solver parameter; the citation covers the number, not the substitution.

  Corrected from an earlier 0.4 approximation.
- **The domain is a closed, reflecting boundary, not an open channel.** Reflected waves likely contaminate long runs. This is the single most decisive untested question and applies to both SPH and MPM.

Open items are tracked as [GitHub Issues](../../issues).

---

## Key finding (provisional pilot, not the real-scene result)

**23 unique (depth, velocity) conditions** tested via L2 on the SPH box-geometry pilot, before the July 7 friction and viscosity fixes.

- **L1 / L2 agreement rate: 39.1 percent** (9 of 23 conditions)
- **14 conditions:** L1 predicts FORD, pilot L2 produces lateral drift exceeding 0.05 m (NO-FORD)
- **Friction-invariant:** drift stays roughly 0.33 to 0.40 m across friction coefficients 0.0 to 0.7

Treat the friction-invariance with suspicion: it is exactly the signature a floating, near-massless body produces (ground normal force near zero makes friction mathematically irrelevant), and the pilot ran before the vehicle mass bug was fixed. This is kept because it motivates the rebuild, not because it is trusted. The 0.05 m drift threshold itself has no direct published source and is reframed as a fraction of vehicle width in [`citations/README.md`](citations/README.md) ([#5](../../issues/5)).

<img src="https://raw.githubusercontent.com/jcerrell-IS/can-it-ford/main/can_it_ford_phase_space_v2.png" alt="L1 vs L2 phase space" width="640">

<img src="https://raw.githubusercontent.com/jcerrell-IS/can-it-ford/main/can_it_ford_validation.png" alt="Monotonic displacement validation" width="640">

---

## Vehicle parameters

`vehicle_params.py` holds three primary-sourced passenger-vehicle classes, all values from authoritative sources rather than aggregators:

| Class | Anchors | Mass | Bounding box (L x W x H, m) | Inertia source |
|---|---|---|---|---|
| `compact_sedan` | Toyota Yaris (2010, NCAC/CCSA FE model) | 1100 kg | 4.30 x 1.70 x 1.47 | uniform-box fallback (no NHTSA-measured Yaris); mass/bbox from [crash-validated FE model](https://doi.org/10.13021/G8JS5D) |
| `midsize_suv` | Toyota Highlander, Ford Explorer | 1990 kg | 4.96 x 1.93 x 1.75 | measured, NHTSA SAE 1999-01-1336 |
| `light_pickup` | Ford F-150, Toyota Tacoma/Tundra | 2300 kg | 5.89 x 2.03 x 1.96 | measured, NHTSA SAE 1999-01-1336 |

Curb weights and bounding boxes come from manufacturer spec sheets; center-of-gravity heights and full measured principal moment-of-inertia tensors (Ixx roll, Iyy pitch, Izz yaw) come from the NHTSA Light Vehicle Inertial Parameter Database. These are measured on instrumented rigs, not box estimates. Call `get_vehicle(vehicle_class)` for a simulation-ready dict. Not yet wired into the L2 scripts ([#7](../../issues/7)).

---

## Repo structure

```
simulation/            L0, L1, L2 scripts (L2 has SPH and MPM variants)
analysis/              Phase space figures, W&B logging, physical validation
render_frames.py       Headless MPM particle + rigid-box collider MP4 renderer
vehicle_params.py      Cited vehicle classes (mass, bbox, CG, inertia)
data/                  Experiment CSVs (L2 results, L0/L1 grid, friction sweep)
citations/             Full bibliography and source PDFs for every threshold used
figures/               Output figures, pipeline diagram, comparison assets
scripts/               Utility: data sync, manifest, Vista pull
kumar_july9_update/    July 9 snapshot for Kumar: 5 SPH renders + STATUS.md
designsafe-staging/    Files staged for DesignSafe DOI (PRJ-6388, pending)
```

---

## Running

**L2 on Vista (GH200 GPU):**

```bash
idev -N 1 -n 1 -p gh -t 1:30:00
module load tacc-apptainer
export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif
cd /work/11603/jcerrell0629/vista/
apptainer exec --nv $GENESIS_PATH python3 simulation/can_it_ford_L2.py <depth_m> <velocity_ms>
```

Add `--record` to save a headless video. The MPM variant is `simulation/can_it_ford_L2_mpm.py` (currently crashing, see [#1](../../issues/1)).

**L0 and L1 (local, no GPU):**

```bash
python3 simulation/can_it_ford_L0.py <depth_m>
python3 simulation/can_it_ford_L1.py <depth_m> <velocity_ms> [vehicle_class]
```

Vehicle class options: `sedan`, `large_passenger`, `large_4wd` (default).

**Render MPM particle output to MP4 (headless, no display needed):**

```bash
python3 render_frames.py --input particles.npz --output water_box.mp4 \
    --box-center 1.0 0.0 0.35 --box-size 1.0 1.6 1.5 --fps 24
```

Run with no `--input` for a synthetic demo that verifies the renderer works.

**Phase space figure (MacBook, conda env `can-it-ford`):**

```bash
python3 analysis/make_phase_space_v2.py
```

**Physical validation.** `analysis/viability_audit.py` reads final-state `.npz` particle files and reports total water momentum per run. It does **not** verify mass conservation: the former mass-integrity check was withdrawn on July 15, 2026 as tautological (it compared a value to itself and could not fail). See `docs/viability_audit_mass_retraction.md`. Per-step invariant checking is not yet implemented. SCP the `.npz` files off Vista first (they are not committed here).

---

## Data

| File | Description |
|---|---|
| `data/phase_space_results.csv` | L2 SPH pilot results (pre-fix, see Status) |
| `data/scenario_sweep.csv` | Theoretical L0/L1 grid (depths 0.1 to 1.0 m x velocities 0.0 to 3.0 m/s) |
| `data/mu_sweep_results.csv` | Friction sensitivity at (d=0.30 m, v=1.5 m/s) |
| `data/l2_results_from_wandb.csv` | Confirmed L2 runs pulled from the W&B API |
| `kumar_july9_update/phase_space_results.csv` | Snapshot sent to Kumar on July 9 |

---

## Citations

Every threshold and parameter traces to a source. Full annotated bibliography, including verification status and caveats, is in [`citations/README.md`](citations/README.md). Load-bearing sources:

- **L1 hazard threshold:** Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2. PDF in `citations/`.
- **L2 physical validation:** Smith, Modra & Felder (2019), full-scale vehicle floating/sliding tests, [DOI:10.1111/jfr3.12527](https://doi.org/10.1111/jfr3.12527).
- **Drift threshold reframing:** Xia et al. (2014) [DOI:10.1007/s11069-013-0889-2](https://doi.org/10.1007/s11069-013-0889-2); Shah et al. (2018) [DOI:10.1051/matecconf/201820307003](https://doi.org/10.1051/matecconf/201820307003).
- **Box-proxy vehicle validation:** Xiong et al. (2024), Water Resources Research, [DOI:10.1029/2023WR036739](https://doi.org/10.1029/2023WR036739).
- **Vehicle inertia:** NHTSA / Heydinger et al., SAE 1999-01-1336, [DOI:10.4271/1999-01-1336](https://doi.org/10.4271/1999-01-1336).
- **Framework and technique:** [PVWM (arXiv:2605.30542)](https://arxiv.org/abs/2605.30542), [Hsiao and Kumar (arXiv:2507.09005)](https://arxiv.org/abs/2507.09005), [PhysGaussian (arXiv:2311.12198)](https://arxiv.org/abs/2311.12198), [3DGS (arXiv:2308.04079)](https://arxiv.org/abs/2308.04079).

See [`CITATION.cff`](CITATION.cff) for citing this repository.

---

## License

Code is released under the **[BSD 3-Clause License](LICENSE)**, the license [recommended by DesignSafe-CI for research software](https://designsafe-ci.org/user-guide/curating/policies/) published in the Data Depot Repository. The associated dataset is released under ODC-By-1.0 (see `CITATION.cff` and the pending DesignSafe DOI, PRJ-6388). A dataset DOI must exist before the July 31 final paper.

Note: PhysGaussian has no detected license in its GitHub metadata. Any PhysGaussian-derived bridge code must have its licensing resolved before being committed here or submitted to DesignSafe.

---

## External assets

- **W&B:** [jcerrell29-claremont-mckenna-college/can-it-ford](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
- **Gradio demo:** [josiecerrell/can-it-ford on HuggingFace Spaces](https://huggingface.co/spaces/josiecerrell/can-it-ford)
- **Hailuo comparison:** `figures/hailuo/`, a visual-model-vs-physical-model comparison for the poster (Hailuo predicts FORD at d=0.30 m / v=1.5 m/s, pilot L2 predicts NO-FORD)
- **Dataset DOI:** DesignSafe PRJ-6388, timing under revision, see `PROVISIONAL_STATUS.md`

---

## Acknowledgments

PI: Krishna Kumar (GeoElements Lab, UT Austin). Daily mentors: Hassan Iqbal, Cheng-Hsi Hsiao, Sarah Etter. Near-peer: Cristian Moran. Genesis container: Luke Smith. Funded by NSF SCIPE REU 2026 (Chishiki AI scholarship, GeoElements).

