# MPM Sweep Data Schema for “Can It Ford?”

## Executive recommendation

Use a **BIDS-like run folder layout + HDF5 canonical particle time series + Parquet/CSV summaries + YAML configs + a top-level manifest**. The reason is practical: the GeoElements/CB-Geo MPM ecosystem already writes particle outputs in **HDF5** and visualization outputs in **VTK/PVTP**, and the DesignSafe MPM tutorial explicitly shows CB-Geo writing HDF5 particle files and parallel VTK `.pvtp` files for distributed MPM visualization ([GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)). Use **xarray as a labeled-array reader/writer layer** when the particle arrays are rectangular enough to be represented as dimensions like `time`, `particle`, and `xyz`; use **Zarr as an optional analysis cache** only when cloud/object-store access or Dask-parallel chunked reads matter more than single-file archival simplicity ([xarray 2026](https://docs.xarray.dev/en/stable/user-guide/io.html); [Zarr 2023](https://zarr.readthedocs.io/en/v2.13.6/)).

For this REU sweep, the canonical “one run” unit should contain: `config/config.yaml`, `summary/summary.json`, `summary/summary.csv`, `timeseries/particles.h5`, `timeseries/vehicle_timeseries.parquet`, optional `viz/vtk/*.pvtp|*.vtp`, `logs/`, and `metadata/provenance.json`. Keep a lightweight top-level `sweep_manifest.csv` and `sweep_manifest.parquet` for Plotly/W&B, and keep heavy particle histories out of the manifest. DesignSafe accepts broad file formats but explicitly recommends open/interoperable formats, README/data reports, documented folder structures, naming conventions, data dictionaries, software versions, and simulation workflow descriptions ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/bestpractices/); [DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/policies/)).

Runnable split:

| Task | MacBook | DesignSafe JupyterHub | Vista/LS6 cluster |
|---|---:|---:|---:|
| Generate run IDs, configs, manifests | Yes | Yes | Yes |
| Read summaries, make Plotly PDFs | Yes | Yes | Yes |
| Retrospective W&B scalar/table logging | Yes, if internet/login | Usually yes, if outbound auth works | Prefer offline logging or post-run sync |
| Load one run’s HDF5/Zarr time series for re-rendering | Yes for small/medium runs | Yes for medium/large runs | Yes |
| Run Genesis/PhysGaussian/MPM FSI simulations | No, except tiny tests | Maybe small CPU/Jupyter tests | Yes: Vista/LS6 |
| Produce full sweep particle histories | No | Possibly postprocess only | Yes |

This structure supports the project’s PVWM framing: the file schema preserves the physical state needed to audit the L2 intervention query rather than only saving a visual or scalar verdict. Thorpe et al. argue that physically viable world models should preserve the structure that determines interventional outcomes and should make outputs auditable at query level ([Thorpe et al. 2026, arXiv:2605.30542](https://arxiv.org/abs/2605.30542)). Hsiao and Kumar’s NeRF-to-MPM inverse framework similarly treats reconstructed geometry as simulation initialization and compares simulated outputs against observations, so reproducibility requires storing configuration, initial state, simulation outputs, and provenance together ([Hsiao and Kumar 2025, arXiv:2507.09005](https://arxiv.org/abs/2507.09005)).

## 1. Recommended file/folder naming and storage schema

### 1.1 Design principles

1. **Use deterministic key-value filenames, not ad hoc prose names.** BIDS filenames use underscore-separated key-value entities plus a suffix and extension, with filenames intended to be both human-readable and machine-readable ([BIDS 2026](https://bids-specification.readthedocs.io/en/stable/common-principles.html)). For this project, use entities such as `veh-sedan`, `dep-0p30m`, `vel-1p50mps`, `idx-0007`, and `h-a1b2c3d4`.
2. **Store configuration as a file inside every run.** Hydra automatically creates per-run output directories and saves YAML configs, and its multirun pattern can include job number and override-derived subdirectories ([Hydra 2026](https://hydra.cc/docs/configure_hydra/workdir/)). Even if the simulation is not using Hydra, imitate that behavior.
3. **Separate heavy arrays from light summaries.** Heavy arrays belong in `timeseries/`; scalar verdicts, peak displacement, peak drag, and status belong in `summary/summary.json` and `summary/summary.csv`. This mirrors WESTPA’s HDF5 pattern of storing detailed iteration data separately from a root summary dataset ([WESTPA 2015](https://westpa.github.io/westpa/users_guide/hdf5.html)).
4. **Keep DesignSafe browsing shallow.** DesignSafe advises avoiding overly nested folders because deep hierarchy slows web browsing and confuses users, while also recommending a documented folder structure and naming convention ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/faq/)).
5. **Publish README/data dictionary/provenance, not just arrays.** DesignSafe recommends a README/data report explaining folder structure, file naming convention, data dictionary, simulation software/version, and workflow graph ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/bestpractices/)).

### 1.2 Deterministic run ID

Recommended run ID:

```text
veh-{vehicle}_dep-{depth_m_token}m_vel-{velocity_mps_token}mps_idx-{index:04d}_h-{hash8}
```

Example:

```text
veh-sedan_dep-0p30m_vel-1p50mps_idx-0007_h-a1b2c3d4
```

Rules:

- Convert decimals with `.` to `p`: `0.30` -> `0p30`; `1.50` -> `1p50`.
- Use SI units in the entity names or suffixes: `dep-*m`, `vel-*mps`.
- Use `idx-0007` for sweep ordering and stable sorting.
- Use `h-{hash8}` from a canonical JSON serialization of the full config, not just the swept parameters.
- Do **not** rely on a timestamp as the only identifier; timestamps are useful for logs but weak for reproducibility.
- If stochastic seeds matter, include `seed-0042` before the hash.

### 1.3 Concrete directory tree

```text
can-it-ford-mpm-sweep-2026/
├── README.md
├── CITATION.cff
├── dataset_description.json
├── data_dictionary.yaml
├── environment/
│   ├── conda-environment.yml
│   ├── pip-freeze.txt
│   ├── apptainer_vista_genesis.def
│   └── container_digest.txt
├── code_snapshot/
│   ├── git_commit.txt
│   ├── run_simulation.py
│   ├── postprocess_run.py
│   └── analyze_sweep.py
├── configs/
│   ├── base_config.yaml
│   └── sweep_grid.yaml
├── manifests/
│   ├── sweep_manifest.csv
│   ├── sweep_manifest.parquet
│   └── run_index.jsonl
├── summaries/
│   ├── all_runs_summary.csv
│   └── all_runs_summary.parquet
├── figures/
│   ├── phase_space_verdict.pdf
│   ├── phase_space_verdict.svg
│   └── force_balance_selected_run.pdf
└── runs/
    ├── veh-sedan_dep-0p30m_vel-1p50mps_idx-0007_h-a1b2c3d4/
    │   ├── config/
    │   │   ├── config.yaml
    │   │   └── config_resolved.json
    │   ├── metadata/
    │   │   ├── provenance.json
    │   │   ├── checksums.sha256
    │   │   └── units.yaml
    │   ├── summary/
    │   │   ├── summary.json
    │   │   └── summary.csv
    │   ├── timeseries/
    │   │   ├── particles.h5
    │   │   ├── vehicle_timeseries.parquet
    │   │   └── particles.zarr/              # optional analysis cache, not required
    │   ├── viz/
    │   │   └── vtk/
    │   │       ├── particles_000000.pvtp
    │   │       ├── particles_000050.pvtp
    │   │       └── particles_000100.pvtp
    │   ├── figures/
    │   │   └── quicklook_force_balance.png
    │   └── logs/
    │       ├── stdout.log
    │       ├── stderr.log
    │       └── performance.json
    └── veh-suv_dep-0p30m_vel-1p50mps_idx-0008_h-f6e7d8c9/
        └── ...
```

Why this works:

- `runs/*/summary/summary.csv` is easy for pandas, W&B, and humans.
- `runs/*/summary/summary.json` preserves typed nested metadata and is robust for W&B config/summary logging.
- `timeseries/particles.h5` is a single canonical heavy file per run, which is friendlier for DesignSafe/Globus upload and long-term citation than many tiny chunks.
- `timeseries/particles.zarr/` can be regenerated as an analysis cache if cloud-native or Dask-parallel reads are needed.
- `viz/vtk/` is optional but useful for ParaView; GeoElements notes that CB-Geo MPM writes parallel `.pvtp` files and recommends opening those for distributed visualizations rather than individual rank `.vtp` files ([GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)).

### 1.4 Minimum per-run metadata

`config/config.yaml` should include all inputs needed to rerun the simulation:

```yaml
project: can-it-ford
schema_version: 1
run:
  index: 7
  run_id: veh-sedan_dep-0p30m_vel-1p50mps_idx-0007_h-a1b2c3d4
  created_utc: "2026-07-08T20:21:00Z"
  seed: 42
sweep:
  vehicle_class: sedan
  water_depth_m: 0.30
  flow_velocity_mps: 1.50
physics:
  gravity_mps2: 9.81
  water_density_kgm3: 1000.0
  viscosity_pa_s: 0.001
  dx_m: 0.02
  dt_s: 0.0005
  t_end_s: 8.0
vehicle:
  mass_kg: 1500.0
  frontal_area_m2: 2.2
  wheelbase_m: 2.7
  tire_friction_coeff: 0.65
verdict_rules:
  lateral_displacement_fail_m: 0.05
  l1_depth_velocity_threshold_m2ps: 0.60
software:
  engine: genesis_or_physgaussian_taichi
  engine_version: unknown
  git_commit: replace_with_commit
  container_digest: replace_with_sha256
outputs:
  particle_format: hdf5
  summary_format: json_csv
  output_stride_steps: 100
```

`summary/summary.json` should be flat enough for pandas but may include nested provenance:

```json
{
  "schema_version": 1,
  "run_id": "veh-sedan_dep-0p30m_vel-1p50mps_idx-0007_h-a1b2c3d4",
  "vehicle_class": "sedan",
  "water_depth_m": 0.30,
  "flow_velocity_mps": 1.50,
  "depth_velocity_m2ps": 0.45,
  "l0_verdict": "NO_FORD",
  "l1_verdict": "FORD",
  "l2_verdict": "NO_FORD",
  "hazard_level": 2,
  "peak_lateral_displacement_m": 0.082,
  "final_lateral_displacement_m": 0.079,
  "peak_drag_N": 4120.0,
  "peak_buoyancy_N": 6800.0,
  "min_tire_margin_N": -350.0,
  "sim_walltime_s": 1840.2,
  "sim_status": "completed",
  "timeseries_particles_path": "../timeseries/particles.h5",
  "timeseries_vehicle_path": "../timeseries/vehicle_timeseries.parquet"
}
```

`metadata/provenance.json` should include the simulation command, hostname, cluster allocation, git commit, input checksum, output checksums, and environment/container fingerprint. DesignSafe’s policy says metadata is mapped to schemas including DataCite and PROV-O and that checksums are calculated during curation ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/policies/)).

### 1.5 Top-level manifest columns

The manifest should be one row per run and should not duplicate particle arrays. Recommended columns:

| Column | Type | Meaning |
|---|---|---|
| `run_id` | string | deterministic ID |
| `run_dir` | string | relative path from dataset root |
| `vehicle_class` | category/string | `sedan`, `suv`, `pickup` |
| `water_depth_m` | float | swept depth |
| `flow_velocity_mps` | float | swept velocity |
| `depth_velocity_m2ps` | float | L1 scalar |
| `seed` | int | random seed, if used |
| `config_hash8` | string | short hash from config |
| `sim_status` | string | `completed`, `failed`, `partial` |
| `l0_verdict` | string | static threshold verdict |
| `l1_verdict` | string | depth-velocity verdict |
| `l2_verdict` | string | MPM verdict |
| `hazard_level` | int | 0 safe, 1 marginal, 2 no-ford |
| `peak_lateral_displacement_m` | float | L2 key metric |
| `peak_drag_N` | float | force-balance metric |
| `peak_buoyancy_N` | float | force-balance metric |
| `min_tire_margin_N` | float | tire limit minus demand |
| `summary_path` | string | relative summary path |
| `particles_path` | string | relative HDF5/Zarr path |
| `vehicle_timeseries_path` | string | relative Parquet path |

## 2. Storage format comparison

### 2.1 Recommendation by downstream use

| Downstream use | Recommended format | Why |
|---|---|---|
| W&B retrospective logging | `summary.json` + `summary.csv` + optional W&B Artifact with config/summary | W&B runs can initialize with config, log metrics, and log tables from pandas DataFrames ([W&B 2025](https://docs.wandb.ai/models/ref/sdk-coding-cheat-sheet/logging)). |
| Plotly heatmaps and poster figures | Top-level `summaries/all_runs_summary.parquet` plus `all_runs_summary.csv` | Pandas reads CSV as the general flat-file workhorse and Parquet as efficient binary columnar DataFrame storage ([pandas 2026](https://pandas.pydata.org/docs/user_guide/io.html?highlight=parquet)). |
| On-demand force-balance plots | `vehicle_timeseries.parquet` per run | It is columnar, fast for selected columns, and simple for pandas/Plotly. |
| Full particle histories | `particles.h5` canonical; optional `particles.zarr/` cache | HDF5 is hierarchical, self-describing, supports groups/datasets/attributes/chunking/compression, and is already used in CB-Geo MPM outputs ([HDF Group 2026](https://support.hdfgroup.org/documentation/hdf5/latest/_h5_d_m__u_g.html); [GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)). |
| ParaView/visual inspection | `.pvtp`/`.vtp` or XDMF sidecar | GeoElements documents `.pvtp` for parallel MPM particle visualization, and meshio supports VTK plus XDMF time series with shared mesh ([GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html); [meshio 2026](https://github.com/nschloe/meshio)). |
| DesignSafe DOI publication | HDF5 + CSV/Parquet + README/data dictionary + code/environment | DesignSafe accepts all formats but recommends open/interoperable formats, documentation, file naming convention, and data dictionaries ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/bestpractices/)). |

### 2.2 Format comparison table

| Option | Standardness in comp-physics/geotech | Strengths | Weaknesses | Best use here |
|---|---|---|---|---|
| CSV per run + top-level summary CSV | Very standard for summaries, not for particle histories | Human-readable, DesignSafe-friendly, easy W&B/pandas/Plotly | Huge and slow for particle time series; weak metadata; no chunking | Scalar summaries and data dictionary examples |
| Parquet per run / all-runs | Standard in data engineering, increasingly common in Python science | Fast columnar reads, compression, pandas-native, good for summary tables | Less human-readable; not ideal for irregular multidimensional arrays | `vehicle_timeseries.parquet` and `all_runs_summary.parquet` |
| HDF5 per run | Very standard in computational physics and geotechnical MPM | Single file, hierarchical groups, attributes, chunking/compression, many language readers | Poorer cloud-object-store ergonomics than Zarr; concurrent writing needs care | Canonical `particles.h5` for DOI and reproducibility |
| Zarr per run | Standard in cloud-native geoscience/climate; newer in geotech | Chunked compressed arrays, S3/object-store friendly, concurrent chunk reads/writes, Dask/xarray friendly | Directory store may create many files; less familiar to civil/geotech reviewers | Optional analysis cache, especially for cloud/Dask workflows |
| xarray Dataset | Not a storage format; common labeled-array abstraction in geoscience | Named dimensions/coordinates/attrs, lazy loading, writes NetCDF/Zarr/HDF5 | Requires rectangular/labeled arrays; cannot represent arbitrary HDF5 hierarchy perfectly | Reader/writer layer over HDF5/Zarr when arrays are `time × particle × component` |
| VTK/PVTP/XDMF | Very standard for visualization in computational mechanics | ParaView-friendly, particle/mesh visualization ecosystem | Not ideal as canonical numeric archive; many files for time series | Optional visualization export |

### 2.3 Zarr vs HDF5 for particle time series

Use **HDF5 as the canonical per-run heavy file** for this dataset because it aligns with geotechnical MPM practice, is a single uploadable object per run, supports hierarchical metadata, and is directly supported by many scientific tools. The HDF5 data model organizes files as rooted hierarchies of groups and datasets, where datasets are multidimensional arrays and named objects can carry attributes ([HDF Group 2026](https://support.hdfgroup.org/documentation/hdf5/latest/_h5_d_m__u_g.html)). The GeoElements DesignSafe MPM tutorial explicitly states that CB-Geo MPM writes HDF5 particle data at each output time step and shows reading `particles00.h5` with pandas ([GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)).

Use **Zarr as a derived cache** when analysis needs cloud/object-store access, chunked parallel reads, or Dask. Zarr is explicitly designed for chunked, compressed N-dimensional arrays and can store arrays on disk, inside Zip files, on S3, and in other stores ([Zarr 2023](https://zarr.readthedocs.io/en/v2.13.6/)). xarray’s Zarr backend supports reading and writing Zarr datasets directly to cloud buckets and supports Dask-parallel writes to Zarr stores ([xarray 2026](https://docs.xarray.dev/en/stable/user-guide/io.html)).

Do **not** use CSV for full particle histories except for tiny debugging samples. CSV is excellent for scalar summaries and simple tabular data, and DesignSafe explicitly recommends CSV over proprietary Excel/Matlab for preservation when appropriate ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/faq/)). Particle histories are multi-dimensional and large, so HDF5/Zarr chunking and compression are the right abstraction.

### 2.4 What is actually common in MPM/geotechnical groups

The CB-Geo/GeoElements MPM workflow uses JSON input files, HDF5 particle data, and VTK/PVTP visualization files; the DesignSafe tutorial shows a `post_processing` JSON block with VTK attributes and states that the code writes HDF5 particle data readable with Python/pandas ([GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)). The CB-Geo MPM repository describes a JSON input configuration and a working-directory run command, which supports the recommendation to keep per-run `config.yaml` or `config_resolved.json` next to outputs ([CB-Geo 2026](https://github.com/cb-geo/mpm)). Older Taichi MPM examples emphasize visual outputs such as `bgeo`, `obj`, `poly`, PNG frames, and `video.mp4`, which are useful for demos but not sufficient as canonical scientific sweep data ([Hu 2018](https://github.com/yuanming-hu/taichi_mpm)). PhysGaussian’s public repo uses JSON scene configs and an `--output_path` for images/videos, which again means the REU project should add a stronger run manifest and numeric storage layer for publishable simulation data ([Xie et al. 2024](https://github.com/XPandora/PhysGaussian)).

Genesis is a general physics platform integrating rigid body, MPM, SPH, FEM, PBD, Stable Fluid, and coupled material simulation, but the repository README does not define a sweep data layout or canonical output format ([Genesis-Embodied-AI 2026](https://github.com/Genesis-Embodied-AI/Genesis)). That absence makes it safer to adopt established computational-mechanics conventions rather than inheriting demo-style output folders.

## 3. Runnable Python patterns

### 3.1 Install dependencies

MacBook or DesignSafe JupyterHub:

```bash
python -m pip install pandas pyarrow pyyaml h5py xarray zarr plotly kaleido wandb
```

Kaleido uses Chrome for static image generation, and Plotly documents `fig.write_image("images/fig1.pdf")` for PDF export after installing Kaleido ([Plotly 2026](https://plotly.com/python/static-image-export/)). If `kaleido>=1` cannot find Chrome on a cluster node, generate PDFs on the MacBook or DesignSafe JupyterHub after copying the summary files.

### 3.2 Run-ID and per-run writer utilities

```python
# file: mpm_run_schema.py
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import yaml


def token_float(x: float, ndigits: int = 2) -> str:
    """0.30 -> '0p30'; 1.5 -> '1p50'."""
    return f"{x:.{ndigits}f}".replace(".", "p")


def canonical_hash8(config: Mapping[str, Any]) -> str:
    """Stable short hash of the full resolved config."""
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]


def make_run_id(vehicle: str, depth_m: float, velocity_mps: float, index: int,
                config: Mapping[str, Any]) -> str:
    h = canonical_hash8(config)
    return (
        f"veh-{vehicle}"
        f"_dep-{token_float(depth_m)}m"
        f"_vel-{token_float(velocity_mps)}mps"
        f"_idx-{index:04d}"
        f"_h-{h}"
    )


def init_run_folder(root: Path, config: dict, index: int) -> Path:
    vehicle = config["sweep"]["vehicle_class"]
    depth_m = float(config["sweep"]["water_depth_m"])
    velocity_mps = float(config["sweep"]["flow_velocity_mps"])
    run_id = make_run_id(vehicle, depth_m, velocity_mps, index, config)
    config.setdefault("run", {})["run_id"] = run_id
    config["run"]["index"] = index

    run_dir = root / "runs" / run_id
    for sub in ["config", "metadata", "summary", "timeseries", "viz/vtk", "figures", "logs"]:
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    with open(run_dir / "config" / "config.yaml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)
    with open(run_dir / "config" / "config_resolved.json", "w") as f:
        json.dump(config, f, indent=2, sort_keys=True)

    return run_dir


def write_summary(run_dir: Path, summary: dict) -> None:
    """Write both JSON and one-row CSV summary."""
    with open(run_dir / "summary" / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    pd.DataFrame([summary]).to_csv(run_dir / "summary" / "summary.csv", index=False)
```

### 3.3 Collect many per-run summaries into one DataFrame

Save this as `analyze_sweep.py` at the dataset root and run it from MacBook, DesignSafe, or a login node after the sweep completes:

```python
# file: analyze_sweep.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import h5py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml

RUN_RE = re.compile(
    r"veh-(?P<vehicle_class>[A-Za-z0-9+]+)_"
    r"dep-(?P<depth_token>[0-9]+p[0-9]+)m_"
    r"vel-(?P<velocity_token>[0-9]+p[0-9]+)mps_"
    r"idx-(?P<index>[0-9]{4})_"
    r"h-(?P<hash8>[0-9a-fA-F]{8})$"
)


def untoken_float(tok: str) -> float:
    return float(tok.replace("p", "."))


def parse_run_id(run_id: str) -> dict[str, Any]:
    m = RUN_RE.match(run_id)
    if not m:
        return {}
    d = m.groupdict()
    return {
        "vehicle_class_from_id": d["vehicle_class"],
        "water_depth_m_from_id": untoken_float(d["depth_token"]),
        "flow_velocity_mps_from_id": untoken_float(d["velocity_token"]),
        "run_index": int(d["index"]),
        "config_hash8": d["hash8"].lower(),
    }


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def collect_summaries(dataset_root: str | Path) -> pd.DataFrame:
    root = Path(dataset_root)
    rows = []

    for summary_path in sorted(root.glob("runs/*/summary/summary.json")):
        run_dir = summary_path.parents[1]
        run_id = run_dir.name
        summary = load_json(summary_path)
        config = load_yaml(run_dir / "config" / "config.yaml")
        parsed = parse_run_id(run_id)

        sweep_cfg = config.get("sweep", {})
        run_cfg = config.get("run", {})
        row = {
            "run_id": run_id,
            "run_dir": str(run_dir.relative_to(root)),
            "summary_path": str(summary_path.relative_to(root)),
            "config_path": str((run_dir / "config" / "config.yaml").relative_to(root)),
            "particles_path": str((run_dir / "timeseries" / "particles.h5").relative_to(root)),
            "particles_zarr_path": str((run_dir / "timeseries" / "particles.zarr").relative_to(root)),
            "vehicle_timeseries_path": str((run_dir / "timeseries" / "vehicle_timeseries.parquet").relative_to(root)),
            **parsed,
            **summary,
        }

        # Fill missing metadata from config if summary is sparse.
        row.setdefault("vehicle_class", sweep_cfg.get("vehicle_class", parsed.get("vehicle_class_from_id")))
        row.setdefault("water_depth_m", sweep_cfg.get("water_depth_m", parsed.get("water_depth_m_from_id")))
        row.setdefault("flow_velocity_mps", sweep_cfg.get("flow_velocity_mps", parsed.get("flow_velocity_mps_from_id")))
        row.setdefault("seed", run_cfg.get("seed"))
        rows.append(row)

    if not rows:
        raise FileNotFoundError(f"No summary.json files found under {root / 'runs'}")

    df = pd.DataFrame(rows)
    numeric_cols = [
        "water_depth_m", "flow_velocity_mps", "depth_velocity_m2ps",
        "hazard_level", "peak_lateral_displacement_m", "peak_drag_N",
        "peak_buoyancy_N", "min_tire_margin_N", "sim_walltime_s"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "vehicle_class" in df.columns:
        df["vehicle_class"] = df["vehicle_class"].astype("category")

    out_dir = root / "summaries"
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / "all_runs_summary.csv", index=False)
    df.to_parquet(out_dir / "all_runs_summary.parquet", index=False)

    manifest_dir = root / "manifests"
    manifest_dir.mkdir(exist_ok=True)
    df.to_csv(manifest_dir / "sweep_manifest.csv", index=False)
    df.to_parquet(manifest_dir / "sweep_manifest.parquet", index=False)
    return df
```

### 3.4 Lazy loader for full time-series data

This class keeps the summary DataFrame small while allowing full data reloading for one run at a time:

```python
# append to analyze_sweep.py
class RunStore:
    def __init__(self, dataset_root: str | Path, summary_df: pd.DataFrame):
        self.root = Path(dataset_root)
        self.df = summary_df.set_index("run_id", drop=False)

    def row(self, run_id: str) -> pd.Series:
        return self.df.loc[run_id]

    def load_vehicle_timeseries(self, run_id: str, columns: list[str] | None = None) -> pd.DataFrame:
        row = self.row(run_id)
        path = self.root / row["vehicle_timeseries_path"]
        if not path.exists():
            raise FileNotFoundError(path)
        return pd.read_parquet(path, columns=columns)

    def open_particles_hdf5(self, run_id: str) -> h5py.File:
        """Caller should close the returned file, or use `with store.open_particles_hdf5(...) as h5:`."""
        row = self.row(run_id)
        path = self.root / row["particles_path"]
        if not path.exists():
            raise FileNotFoundError(path)
        return h5py.File(path, "r")

    def load_particle_step_hdf5(self, run_id: str, step_index: int) -> pd.DataFrame:
        """
        Expected HDF5 layout:
          /time                         shape (nt,)
          /particles/id                 shape (n_particles,)
          /particles/position           shape (nt, n_particles, 3)
          /particles/velocity           shape (nt, n_particles, 3)
          /particles/mass               shape (n_particles,) or (nt, n_particles)
        Adjust dataset names if the engine writes a different schema.
        """
        with self.open_particles_hdf5(run_id) as h5:
            pos = h5["/particles/position"][step_index, :, :]
            vel = h5["/particles/velocity"][step_index, :, :]
            pid = h5["/particles/id"][:]
            time_s = float(h5["/time"][step_index])
            data = {
                "particle_id": pid,
                "time_s": time_s,
                "x_m": pos[:, 0], "y_m": pos[:, 1], "z_m": pos[:, 2],
                "vx_mps": vel[:, 0], "vy_mps": vel[:, 1], "vz_mps": vel[:, 2],
            }
            if "/particles/material_id" in h5:
                data["material_id"] = h5["/particles/material_id"][:]
            return pd.DataFrame(data)

    def open_particles_zarr(self, run_id: str):
        """Optional xarray/Zarr loader. Requires `xarray` and `zarr`."""
        import xarray as xr
        row = self.row(run_id)
        path = self.root / row["particles_zarr_path"]
        if not path.exists():
            raise FileNotFoundError(path)
        return xr.open_zarr(path)
```

Recommended HDF5 layout for `particles.h5`:

```text
/
├── attrs:
│   ├── schema_version = 1
│   ├── run_id = "veh-sedan_dep-0p30m_vel-1p50mps_idx-0007_h-a1b2c3d4"
│   ├── coordinate_system = "x downstream, y lateral, z vertical"
│   └── units = "SI"
├── time                         float64 [nt]
├── particles/
│   ├── id                       int64   [np]
│   ├── material_id              int16   [np]
│   ├── position                 float32 [nt, np, 3]
│   ├── velocity                 float32 [nt, np, 3]
│   ├── stress                   float32 [nt, np, 6]    # optional
│   ├── volume                   float32 [nt, np]       # optional
│   └── active                   bool    [nt, np]       # optional
└── vehicle/
    ├── pose                     float64 [nt, 7]
    ├── velocity                 float64 [nt, 6]
    ├── force_hydro              float64 [nt, 3]
    ├── force_contact            float64 [nt, 3]
    └── lateral_displacement_m   float64 [nt]
```

### 3.5 Plotly phase-space heatmap and force-balance PDF export

```python
# append to analyze_sweep.py
def plot_phase_space(df: pd.DataFrame, out_pdf: str | Path, vehicle_class: str | None = None):
    d = df.copy()
    if vehicle_class is not None:
        d = d[d["vehicle_class"].astype(str) == vehicle_class]

    # Use the maximum hazard if duplicate seeds exist at the same grid point.
    grid = d.pivot_table(
        index="water_depth_m",
        columns="flow_velocity_mps",
        values="hazard_level",
        aggfunc="max",
        observed=False,
    ).sort_index().sort_index(axis=1)

    label = {0: "FORD", 1: "MARGINAL", 2: "NO-FORD"}
    fig = px.imshow(
        grid,
        origin="lower",
        aspect="auto",
        color_continuous_scale=[
            [0.0, "#2E7D32"],   # green
            [0.5, "#F9A825"],   # amber
            [1.0, "#C62828"],   # red
        ],
        zmin=0,
        zmax=2,
        labels={"x": "Flow velocity (m/s)", "y": "Water depth (m)", "color": "Hazard"},
        title=f"L2 MPM Ford/No-Ford Phase Space" + (f" — {vehicle_class}" if vehicle_class else ""),
    )
    fig.update_layout(
        width=900,
        height=650,
        font=dict(family="Arial", size=18),
        coloraxis_colorbar=dict(
            tickmode="array",
            tickvals=[0, 1, 2],
            ticktext=[label[0], label[1], label[2]],
        ),
    )
    fig.update_xaxes(type="category")
    fig.update_yaxes(type="category")
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(out_pdf), format="pdf")
    fig.write_image(str(out_pdf.with_suffix(".svg")), format="svg")
    return fig


def plot_force_balance(store: RunStore, run_id: str, out_pdf: str | Path):
    cols = [
        "time_s", "drag_N", "buoyancy_N", "lateral_hydro_force_N",
        "tire_friction_limit_N", "lateral_displacement_m"
    ]
    ts = store.load_vehicle_timeseries(run_id)
    missing = [c for c in cols if c not in ts.columns]
    if missing:
        raise ValueError(f"vehicle_timeseries.parquet is missing columns: {missing}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts["time_s"], y=ts["lateral_hydro_force_N"], name="Lateral hydro force", mode="lines"))
    fig.add_trace(go.Scatter(x=ts["time_s"], y=ts["tire_friction_limit_N"], name="Tire friction limit", mode="lines"))
    fig.add_trace(go.Scatter(x=ts["time_s"], y=ts["drag_N"], name="Drag", mode="lines", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=ts["time_s"], y=ts["buoyancy_N"], name="Buoyancy", mode="lines", line=dict(dash="dot")))

    fig.add_trace(go.Scatter(
        x=ts["time_s"], y=ts["lateral_displacement_m"], name="Lateral displacement (m)",
        mode="lines", yaxis="y2", line=dict(color="#000000", width=3)
    ))

    fig.update_layout(
        title=f"Force Balance and Lateral Drift — {run_id}",
        xaxis_title="Time (s)",
        yaxis_title="Force (N)",
        yaxis2=dict(title="Lateral displacement (m)", overlaying="y", side="right"),
        width=1000,
        height=650,
        font=dict(family="Arial", size=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(out_pdf), format="pdf")
    return fig


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--vehicle", default=None, help="sedan, suv, pickup, or omit for all")
    parser.add_argument("--force-run-id", default=None)
    args = parser.parse_args()

    df = collect_summaries(args.dataset_root)
    plot_phase_space(
        df,
        args.dataset_root / "figures" / "phase_space_verdict.pdf",
        vehicle_class=args.vehicle,
    )

    if args.force_run_id:
        store = RunStore(args.dataset_root, df)
        plot_force_balance(
            store,
            args.force_run_id,
            args.dataset_root / "figures" / "force_balance_selected_run.pdf",
        )
```

Run:

```bash
python analyze_sweep.py /path/to/can-it-ford-mpm-sweep-2026 --vehicle sedan
python analyze_sweep.py /path/to/can-it-ford-mpm-sweep-2026 --force-run-id veh-sedan_dep-0p30m_vel-1p50mps_idx-0007_h-a1b2c3d4
```

Plotly supports PDF/SVG export through `write_image`, and its static image documentation notes that PNG, JPEG, WebP, SVG, and PDF are supported formats ([Plotly 2026](https://plotly.com/python/static-image-export/)). Avoid Plotly WebGL traces for final poster PDFs because Plotly states that WebGL traces exported to vector formats include encapsulated rasters for some parts of the image ([Plotly 2026](https://plotly.com/python/static-image-export/)).

### 3.6 W&B retrospective logging

Use this after simulations finish, not necessarily during cluster execution. W&B documents `wandb.init(project=..., config=config)` for configs, `run.log({...})` for metrics, `wandb.Table(dataframe=...)` for tables, and Artifacts for versioning files as run inputs/outputs ([W&B 2025](https://docs.wandb.ai/models/ref/sdk-coding-cheat-sheet/logging); [W&B 2026](https://docs.wandb.ai/models/artifacts)).

```python
# file: retrospective_wandb_log.py
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import wandb
import yaml


def load_yaml(path: Path):
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def load_json(path: Path):
    with open(path, "r") as f:
        return json.load(f)


def log_one_run(dataset_root: Path, run_dir: Path, project: str, entity: str | None = None):
    config_path = run_dir / "config" / "config.yaml"
    summary_json_path = run_dir / "summary" / "summary.json"
    summary_csv_path = run_dir / "summary" / "summary.csv"

    config = load_yaml(config_path)
    summary = load_json(summary_json_path)
    run_id = summary.get("run_id", run_dir.name)

    tags = [
        str(summary.get("vehicle_class", "unknown")),
        f"depth-{summary.get('water_depth_m', 'na')}",
        f"vel-{summary.get('flow_velocity_mps', 'na')}",
        "retrospective",
    ]

    with wandb.init(
        entity=entity,
        project=project,
        name=run_id,
        id=run_id[:128],
        resume="allow",
        config=config,
        tags=tags,
        job_type="mpm-sweep-run",
    ) as run:
        scalar_keys = [
            "water_depth_m", "flow_velocity_mps", "depth_velocity_m2ps",
            "hazard_level", "peak_lateral_displacement_m", "final_lateral_displacement_m",
            "peak_drag_N", "peak_buoyancy_N", "min_tire_margin_N", "sim_walltime_s",
        ]
        metrics = {k: summary[k] for k in scalar_keys if k in summary}
        run.log(metrics)

        for k, v in summary.items():
            if isinstance(v, (int, float, str, bool)):
                run.summary[k] = v

        if summary_csv_path.exists():
            summary_df = pd.read_csv(summary_csv_path)
            run.log({"summary_table": wandb.Table(dataframe=summary_df)})

        artifact = wandb.Artifact(
            name=f"{run_id}-metadata",
            type="simulation-run",
            metadata={
                "run_id": run_id,
                "vehicle_class": summary.get("vehicle_class"),
                "water_depth_m": summary.get("water_depth_m"),
                "flow_velocity_mps": summary.get("flow_velocity_mps"),
            },
        )
        artifact.add_file(str(config_path), name="config/config.yaml")
        artifact.add_file(str(summary_json_path), name="summary/summary.json")
        artifact.add_file(str(summary_csv_path), name="summary/summary.csv")

        # Avoid uploading giant particle HDF5 files by default. Log their relative path instead.
        particles_path = run_dir / "timeseries" / "particles.h5"
        if particles_path.exists():
            run.summary["particles_h5_relative_path"] = str(particles_path.relative_to(dataset_root))

        run.log_artifact(artifact)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--project", default="can-it-ford")
    parser.add_argument("--entity", default=None)
    args = parser.parse_args()

    for run_dir in sorted((args.dataset_root / "runs").glob("veh-*")):
        if (run_dir / "summary" / "summary.json").exists():
            log_one_run(args.dataset_root, run_dir, project=args.project, entity=args.entity)


if __name__ == "__main__":
    main()
```

Run from MacBook or DesignSafe:

```bash
wandb login
python retrospective_wandb_log.py /path/to/can-it-ford-mpm-sweep-2026 --project can-it-ford
```

If running on Vista/LS6 where outbound network/auth is awkward, set offline mode during the job and sync later:

```bash
export WANDB_MODE=offline
python retrospective_wandb_log.py /path/to/can-it-ford-mpm-sweep-2026 --project can-it-ford
# later, on a machine with internet:
wandb sync wandb/offline-run-*
```

## 4. DesignSafe publication checklist

Before publishing the data DOI:

- Add a `README.md` or data report that explains the directory tree, file naming convention, data dictionary, simulation workflow, software versions, and quality-control checks; DesignSafe explicitly recommends documentation describing methodology, dataset organization, file naming convention, data dictionary, simulation software/version, and workflow graph ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/bestpractices/)).
- Include `all_runs_summary.csv` even if Parquet is the analysis-preferred file, because DesignSafe recommends open/interoperable formats and gives CSV as the preservation-friendly alternative to Excel/Matlab for tabular data ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/faq/)).
- Include `particles.h5` as the canonical heavy numeric output and document its internal schema in `data_dictionary.yaml`; HDF5 is a self-describing hierarchical file format with groups, datasets, and attributes ([HDF Group 2026](https://support.hdfgroup.org/documentation/hdf5/latest/_h5_d_m__u_g.html)).
- Include optional VTK/PVTP visualization outputs only if storage is manageable, because they are useful for ParaView but are derivative of the numeric particle histories; GeoElements recommends `.pvtp` files for visualizing distributed MPM outputs ([GeoElements 2026](https://www.geoelements.org/LearnMPM/designsafe-mpm.html)).
- Keep Zarr stores if they are genuinely used for analysis, but document that they are derived caches from HDF5 or publish both HDF5 and Zarr if the Zarr store is the active analysis format.
- Avoid publishing only compressed archives; DesignSafe says uploaded `.tar` or `.zip` files should be decompressed before curating and publishing because archives prevent users from directly viewing and understanding the data ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/bestpractices/)).
- Add related-work entries for the PVWM paper, the Hsiao/Kumar inverse MPM paper, Genesis/PhysGaussian code if used, and the GitHub commit for the REU code; DesignSafe says Related Work and Referenced Data and Software can be sent to DataCite so reused resources receive credit ([DesignSafe 2026](https://designsafe-ci.org/user-guide/curating/policies/)).

## 5. Bottom line

For “Can It Ford?”, treat every simulation as a small reproducible experiment. Save the **full physical trace** once in `particles.h5`, save the **vehicle/force time series** in Parquet, save the **verdict and scalar metrics** in JSON/CSV, and index everything in a top-level manifest. This gives W&B a clean retrospective logging path, gives Plotly a single DataFrame for poster figures, and gives DesignSafe a DOI-ready package with documented provenance and reusable heavy data.
