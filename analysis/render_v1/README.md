# analysis/render_v1

Archived snapshot, 2026-07-25, of the RENDER-v1 / AMENDMENT A work.

**Why this directory exists:** the live working directory is
`renders/yaris_render_s1/`, and `renders/` is gitignored (`.gitignore:14`).
Nothing in there is visible to git or to any repo-based backup. These are copies
so the work survives.

Full narrative, with every measurement and its provenance tag, is in
[`docs/RENDER_V1_AMENDMENT_A_PROCESS_2026-07-25.md`](../../docs/RENDER_V1_AMENDMENT_A_PROCESS_2026-07-25.md).

## This is a snapshot, not the working copy

If you edit anything here it will not affect a render. Edit
`renders/yaris_render_s1/` and re-copy. If the two ever disagree, the working
directory is authoritative.

## Contents

### Written during this session

| file | what it does |
|---|---|
| `t1_car.py` | Reproduces `load_vehicle`'s orientation so the mesh lands in the same frame as `veh_particles_vehframe`. Includes the long-axis-to-Y `Rz` that RENDER-v1's T1c omitted. Also does geometric body/glass/tyre segmentation in the vehicle frame, so it is pose-invariant. |
| `render_realistic.py` | The composite render. Water surfacing is Kumar's `nclaw_geom_render.py::_surface` at `iso_frac = 0.90`, chosen by measurement. Car and water share one `Poly3DCollection` so matplotlib's per-polygon depth sort orders them against each other. |
| `t4_defects.py` | `t4a` the water-lattice `np.arange` fragility and its `linspace` fix. `t4b` the P-2 discriminator, AABB versus the vehicle's own pitch-`h` voxel occupancy, over all 90 frames. |

### Supporting scripts carried along

`gates.py`, `gates_both_scenarios.py`, `geom_live.py`, `g0_validate.py`,
`g1_car_check.py`, `g1b_car_check.py`, `s2_gridgate.py`, `sim_dump.py`,
`encode.py`, `render_flood.py`, plus their `*_results.json` and `*.log` outputs.

### `as_ran_local_copies/`

The **patched local** code that actually executed, pulled from Vista. This is
**not** upstream and diverges from it in two ways that matter (PLY dispatch and
`solidify_watertight` versus `solidify_columns`). See A0 in the process
document. Upstream at the pinned SHA is archived separately under
`third_party/mpm-engine-544c93dd/`.

Contains `vehicle_live.py`, `common.py`, `sim_standing.py`, `run_s1.sbatch`,
`run_s1.sh`, `run_s2.sh`.

`sim_standing.py` is the actual driver. It uses `StandingFloodScene`, not
Kumar's `FloodScene`, which is why claims about `flood_vehicle.py::run` do not
govern these runs.

## Running these

There is no checked-in venv. The interpreter used was uv-managed CPython 3.12.

```bash
cd /Users/josie/can-it-ford/renders/yaris_render_s1 && uv run --python 3.12 --with numpy --with trimesh --with scikit-image --with scipy --with fast-simplification python render_realistic.py g64_m1100 45
```

Success looks like: a PNG written, `watertight True`, and a printed volume within
about 3% of 19.2891 m3. The most likely failure is a `ModuleNotFoundError`,
because no system python on this machine has numpy. Use the `uv run` line above
rather than `python3`.

Note `trimesh.ray.has_embree` is **False** here, so any `mesh.contains` work is
slow enough that it needs subsampling or a background job.

## Not archived

`renders/yaris_render_s1/*/rollout.npz`, 397 MB across six runs. Raw simulation
data, still on disk in the gitignored working directory. Every number in the
process document came from `g64_m1100/rollout.npz`.
