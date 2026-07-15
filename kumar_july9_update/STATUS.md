# Can It Ford — Status Log

**Last updated:** July 9, 2026
**Scope:** MPM rebuild progress since Kumar's July 7 instruction to migrate to [`kks32/mpm-engine`](https://github.com/kks32/mpm-engine).

## Contents

- [Summary](#summary)
- [Chronological Log](#chronological-log)
- [Track 1: kks32/mpm-engine](#track-1-kks32mpm-engine)
- [Track 2: Direct Genesis MPM](#track-2-direct-genesis-mpm)
- [Track Divergence](#track-divergence)
- [Vehicle Mesh](#vehicle-mesh)
- [Vehicle Physics Reference](#vehicle-physics-reference)
- [Prior Work: Genesis SPH](#prior-work-genesis-sph)
- [Citations](#citations)
- [Open Questions](#open-questions)
- [Next Steps](#next-steps)

---

## Summary

Two independent MPM tracks are running in parallel. Neither has produced a FORD/NO-FORD verdict yet. Two independent vehicle-mesh reconstruction attempts have both failed, for different reasons. No real vehicle mesh currently exists in the pipeline.

| Track | Solver | State | Blocker |
|---|---|---|---|
| [`kks32/mpm-engine`](https://github.com/kks32/mpm-engine) | `warpmpm` (Warp-based) | Env confirmed, vehicle scene wired to real sedan dimensions | Water drift during gravity settling, cause not isolated |
| Direct Genesis MPM | `gs.materials.MPM.Liquid` | Crashed before producing output | `CUDA_ERROR_ILLEGAL_ADDRESS` at step 0 |
| Genesis SPH (prior) | `gs.materials.SPH.Liquid` | Complete, already reviewed | Superseded; methods rehearsal only |
| Vehicle mesh | — | Two attempts, both closed | No usable mesh; using box proxy |

---

## Chronological Log

| Date | Event |
|---|---|
| Jul 7, AM | Sent Kumar a bug-fix summary on the SPH-era script (unset density, wrong spawn depth, unstable timestep). Cheng-Hsi flags Genesis is likely running SPH, not MPM, for water. |
| Jul 7, PM | Kumar instructs: `"can you run what Cheng-Hsi has first? kks32/mpm-engine is the MPM engine."` |
| Jul 7–8 | `kks32/mpm-engine` environment set up and verified on Vista. |
| Jul 7–8 | **Mesh Attempt 1**: marching-cubes reconstruction on Luke Smith's ls6 point cloud. Closed to genus 9, stopped. |
| Jul 8, 6:20 PM | `can_it_ford_L2_mpm.py` written (direct Genesis MPM track), generic box vehicle. |
| Jul 8–9, overnight | **Mesh Attempt 2**: Poisson reconstruction via `open3d` (`reconstruct_car.py`, separate `.venv-o3d`). Produced `car_mesh.ply`, technically watertight. |
| Jul 9, ~3:30 AM | Diagnosed `car_mesh.ply`: source point cloud was never car-sized. Not a fixable scale bug. Recommended box proxy. |
| Jul 9, 4:38 AM | `box_sdf_collider_setup.py` rewritten: real sedan bounding box, larger domain, full physics run loop. |
| Jul 9, evening | Ran `can_it_ford_L2_mpm.py` again. Crashed, `CUDA_ERROR_ILLEGAL_ADDRESS`, step 0. |
| Jul 9, evening | Sent Kumar this update; sent Hassan a technical question on the crash and the drift bug. |

---

## Track 1: `kks32/mpm-engine`

**Environment, Vista, confirmed working:**

| Component | Value |
|---|---|
| Python | `3.12.13`, venv via `uv` |
| `torch` | `2.11.0+cu128` |
| CUDA | Confirmed `True` on GH200 |
| Verified APIs | `newtonian()`, `mesh_sdf.build_sdf()`, `Solver.add_sdf_collider()` |

**Current vehicle scene** (`box_sdf_collider_setup.py`, local to Vista and to Downloads on my Mac, not yet pushed to this repo):

```python
BOX_DIMS_M = (4.66, 1.79, 1.44)   # real sedan bounding box, x=length/flow direction
DOMAIN_SIZE_M = 10.0              # cubic domain, sized for upstream/downstream room
grid = GridConfig(n_grid=192, grid_lim=DOMAIN_SIZE_M)

vehicle_center = (6.5, 5.0, floor_z + BOX_DIMS_M[2] / 2.0)
vehicle = solver.add_sdf_collider(
    sdf, center=vehicle_center, quat=(0.0, 0.0, 0.0, 1.0),
    velocity=(0.0, 0.0, 0.0), omega=(0.0, 0.0, 0.0),
    surface="separable", friction=0.55,
)
```

Run loop tracks peak contact force over a 1.0s simulated window, not just a fixed step count.

**Open bug:** water particles drift toward the low-x domain edge during gravity settling, before the vehicle is added. Not yet isolated: plane friction, water block bounds, or grid setup. This bug was described against an older, smaller version of this script; not yet reconfirmed against the current one.

---

## Track 2: Direct Genesis MPM

File: [`simulation/can_it_ford_L2_mpm.py`](https://github.com/jcerrell-IS/can-it-ford/blob/main/simulation/can_it_ford_L2_mpm.py)

**Configured parameters (verified against the live file):**

| Parameter | Value |
|---|---|
| `grid_density` | `64` |
| `coup_friction` | `0.55` |
| `rho` | `604` |
| Vehicle box | `1.0 x 1.6 x 1.5 m` (generic, not sedan-scale, see [Track Divergence](#track-divergence)) |
| `dt` / `substeps` | `4e-3` / `32` |

**Known bug in this file:** the auto-generated `run_tag` string reads `grid128_cf0p4`, implying `grid_density=128` and `coup_friction=0.4`. Neither matches the actual configured values above. Stale naming, left from an earlier version, does not affect the physics, does affect anyone reading filenames.

**Tonight's run, 0.30 m depth, 1.5 m/s:**

| Result | Value |
|---|---|
| Steps completed | Step 0 only |
| Failure | `CUDA_ERROR_ILLEGAL_ADDRESS`, raised inside the MPM solver's internal state-validity check |
| When | First post-coupling substep, vehicle beginning to settle under gravity |
| Verdict | None |
| Output written | None: no video, no `.npz`, no CSV row |
| Traceback saved | None found, anywhere: local repo, Vista, GitHub |

---

## Track Divergence

The two tracks currently use different vehicle geometry. `kks32/mpm-engine`'s vehicle box was updated to the real sedan bounding box (`4.66 x 1.79 x 1.44 m`) on July 9. `can_it_ford_L2_mpm.py` still uses the older generic box (`1.0 x 1.6 x 1.5 m`) from July 8 and has not been updated since. Flagging this so it is not mistaken for a single consistent vehicle representation across both tracks.

---

## Vehicle Mesh

Two independent reconstruction attempts, both closed, for different reasons.

| Attempt | Method | Result |
|---|---|---|
| 1 | Marching cubes, Luke Smith's ls6 point cloud (44,148 points, no faces) | Closed to genus 9. Further closure would merge the wheels into the body. Stopped rather than force a bad mesh. |
| 2 | Poisson reconstruction, `open3d`, `reconstruct_car.py` | Technically succeeded, watertight, clean. Produced `car_mesh.ply`. Diagnosed as unusable: raw source point cloud is `0.345 x 0.174 x 0.72 m`, `car_mesh.ply` is `0.33 x 0.17 x 0.71 m`, nearly identical. The reconstruction introduced no scale error; the source point cloud was never car-sized to begin with, likely a small tutorial demo asset. |

**Also checked, still open:**
- A CoRL 2026 planning-paper submission from the lab (unpublished, cites PVWM as its own reference [1]) uses a real truck splat in a flood MPM scene, the Alaska Village Scene. Asked Cheng-Hsi whether it's reusable, no answer yet.
- Cheng-Hsi's own `hicss-splat` dataset also represents its truck as a placeholder ball, not a real mesh.

**Net status:** no confirmed real vehicle mesh exists anywhere in the pipeline. Current plan: box proxy, sized to real sedan dimensions in Track 1.

---

## Vehicle Physics Reference

| Class | Mass | Bbox (L x W x H) | CG height | Ixx / Iyy / Izz (kg·m²) |
|---|---|---|---|---|
| Compact sedan (Corolla/Civic) | ~1390 kg | `4.66 x 1.79 x 1.44 m` | 0.52 m | 365 / 1617 / 1785 |

Source: NHTSA Light Vehicle Inertial Parameter Database, SAE Technical Paper 1999-01-1336. Measured on instrumented rigs, not box-estimated.

---

## Prior Work: Genesis SPH

Five renders, already reviewed by Kumar, not new evidence, listed for completeness only.

| Render | Depth | Velocity |
|---|---|---|
| `simulation_d0p3_v1p5.mp4` | 0.3 m | 1.5 m/s |
| `simulation_d0p6_v1p5.mp4` | 0.6 m | 1.5 m/s |
| `simulation_d0p6_v2p0.mp4` | 0.6 m | 2.0 m/s |
| `simulation_d0p6_v2p5.mp4` | 0.6 m | 2.5 m/s |
| `simulation_d1p0_v3p0.mp4` | 1.0 m | 3.0 m/s |

Solver: `gs.materials.SPH.Liquid`, not MPM. Methods rehearsal, not the paper's dataset.

---

## Citations

| Claim | Source | Backing on file |
|---|---|---|
| L1 hazard threshold | Shand et al. 2011, AR&R Project 10 Stage 2 | `citations/ARR_Project_10_Stage2_Report_Final.pdf` |
| Friction range (superseded) | Smith-Modra-Felder 2019 | `citations/Smith-Modra-Felder/smith2019_instability_table.png` |
| Friction `0.55` | Azhar et al. 2023 | No PDF on file, no public link confirmed |
| Vehicle mass/inertia | NHTSA LVIP Database, SAE 1999-01-1336 | No public link confirmed |
| Framework | Thorpe et al., PVWM | [arXiv:2605.30542](https://arxiv.org/abs/2605.30542) |
| `DRIFT_THRESHOLD = 0.05 m` | Numerical onset-of-motion detection tolerance, not a physically-cited threshold; approximately 2.5 to 3.4 percent of vehicle body width. Underlying incipient-motion physics: Xia et al. 2014 (DOI 10.1007/s11069-013-0889-2), Shah et al. 2018 (DOI 10.1051/matecconf/201820307003) | Resolved July 13 (framing); see `citations/README.md` |

---

## Open Questions

- [ ] Root cause of `CUDA_ERROR_ILLEGAL_ADDRESS` in `can_it_ford_L2_mpm.py`
- [ ] Root cause of water drift in `box_sdf_collider_setup.py`, and whether it still occurs in the current (sedan-scale) version
- [ ] Whether the CoRL 2026 truck mesh is reusable
- [x] Source for `DRIFT_THRESHOLD = 0.05 m` (resolved July 13: it is a numerical detection tolerance, not a physically-cited threshold; framed as approximately 2.5 to 3.4 percent of vehicle body width, with incipient-motion physics from Xia et al. 2014 and Shah et al. 2018)
- [ ] Whether the two tracks should be reconciled to one vehicle representation

## Next Steps

- [ ] Debug the CUDA crash in `can_it_ford_L2_mpm.py`; capture a full traceback next run
- [ ] Debug the water drift in `box_sdf_collider_setup.py`
- [ ] Push `box_sdf_collider_setup.py` to this repo
- [ ] Update `can_it_ford_L2_mpm.py` to the real sedan box dimensions, or document why it should stay separate
- [ ] Fix the stale `run_tag` naming in `can_it_ford_L2_mpm.py`
- [ ] Resolve vehicle mesh: CoRL truck, a sourced CC0 model, or confirm box proxy for the final result
- [x] Resolve the `DRIFT_THRESHOLD` citation (resolved July 13: numerical onset-of-motion detection tolerance, not a physically-cited threshold; framed as approximately 2.5 to 3.4 percent of vehicle body width, per Xia et al. 2014 and Shah et al. 2018)
