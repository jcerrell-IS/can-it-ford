# Lane yaris-render, 2026-07-25: MPM flood render, three AR&R classes, three verdicts

Every number here traces to a command run in this session. Nothing is quoted from a memory
note or a prior handoff without a live re-check, and where a live check contradicted a note
the note is named and corrected.

## HEADLINE, the thing to read first

**The run contradicts the paper's divergence-zone claim for two of three classes.**

The paper asserts a divergence zone at depth >= 0.25 m, velocity >= 1.2 m/s, D x V < 0.60,
where L1 says FORD and L2 says NO-FORD. The point tested (0.30 m, 1.5 m/s, D x V 0.45) is
inside that zone on all three conditions. Measured:

| class | L1 (nominal) | L2 (MPM) | result |
|---|---|---|---|
| small_passenger, 1100 kg | NO-FORD | NO-FORD | AGREE, contradicts the zone |
| large_passenger, 1609 kg | FORD | NO-FORD | DIVERGE, as the zone predicts |
| large_4wd, 2337 kg | FORD | FORD | AGREE, contradicts the zone |

The zone as written is class-free. It cannot be: at a fixed D x V of 0.45 the L1 verdict
alone is NO-FORD, FORD, FORD across the three classes, because the AR&R hazard limits are
0.30 / 0.45 / 0.60 m2/s. Any restatement must carry a class label.

**Second headline: computing D x V honestly removes the one remaining divergence.**
Local depth at the vehicle is higher than nominal (bow wave) while local water speed is far
lower (stagnation). Honest D x V is 58 to 66 percent below nominal. Re-running L1 on local
values flips large_passenger FORD -> NO-FORD on the DEPTH limit, and then L1 and L2 agree on
all three classes.

## THE MANDATORY CAVEAT FROM THE BRIEF IS RETIRED, and this is why

The brief required a caveat stating the solidifier bridges columns so the body fills
7.71 m3 against a true hull of 3.54 m3, a 2.18x over-fill, dropping effective density to
143 kg/m3 against a true 310. **That describes code that is no longer the active path.**
Re-derived live this session, both on Vista and independently on the Mac:

| path | N at h=0.0736 m | solid volume | ratio vs hull | rho at 1100 kg |
|---|---|---|---|---|
| `solidify_columns` (retired) | 19303 | 7.698 m3 | 2.173 | 142.90 |
| `solidify_watertight` (LIVE) | 8904 | 3.5509 m3 | **1.0023** | **309.78** |

The retired-path numbers reproduce the brief's caveat to within sampling noise, which
confirms the caveat correctly described `solidify_columns`. It does not describe the run.
Writing it as a caveat on this render would have been false. The over-fill is gone, so the
bias-toward-floating argument it carried is gone too, and the NO-FORD results no longer
need it. `veh_z_min` rise is 0.000000 m in all three runs: no float is live at all.

## GATE RESULTS

### Geometry gate

| gate | measured | band | verdict |
|---|---|---|---|
| G-1 mesh extents | [1.7461, 4.2826, 1.5175] m | within 2 % of [1.746, 4.283, 1.518] | PASS (max dev 0.0299 %) |
| G-2 fill_ratio | 3.55086 / 3.542739 = 1.00229 | [0.95, 1.10] | PASS |
| G-3 effective density | 1100.0 / 3.55086 = 309.78 | within 5 % of 310.49 | PASS (dev 0.227 %) |
| G-4 drawn cloud extents, surface points | n=60000, [1.7461, 4.2826, 1.5175] | within 2 % | PASS (0.0299 %) |
| G-4 drawn cloud extents, MPM particles | n=8904, [1.6929, 4.1956, 1.4721] | within 2 % | **FAIL (3.04 %)** |
| G-5 side silhouette fill, surface points | 0.6734 | 0.5 to 0.7 car profile | PASS |
| G-5 side silhouette fill, MPM particles | 0.4448 at cell = h | above 0.85 is a loaf | not a loaf, voids preserved |
| G-6 distinct z levels, surface points | 58160 | report either way | reported |
| G-6 distinct z levels, MPM particles | 21 | report either way | reported |

G-4 is the gate doing its job. **The rendered body is the 60,000 hull-surface points, not
the 8,905 MPM solid particles**, and every frame's caption says so in words. The MPM solid
at h = 0.0736 m fails the 2 percent extent band by 3.04 percent because a voxelised fill
inscribes the hull; it is the correct physics body and the wrong thing to draw.

### Physics gate, all three runs

| gate | requirement | 1100 kg | 1609 kg | 2337 kg |
|---|---|---|---|---|
| P-1 oob particle-frames | 0 | 0 PASS | 0 PASS | 0 PASS |
| P-2 max water frac in vehicle bbox | < 10 % | 3.68 % PASS | 3.02 % PASS | 2.43 % PASS |
| P-3 veh z_min rise | <= 0.01 m | 0.000000 PASS | 0.000000 PASS | -0.000000 PASS |
| P-6 water layers | >= 4 | 4 PASS | 4 PASS | 4 PASS |

P-4, both depths, never conflated:

| class | nominal slab depth | local depth peak | local depth final |
|---|---|---|---|
| small_passenger | 0.3000 m | 0.3974 m (frame 29) | 0.1069 m |
| large_passenger | 0.3000 m | 0.4159 m (frame 29) | 0.1235 m |
| large_4wd | 0.3000 m | 0.4260 m (frame 29) | 0.1152 m |

P-5, D x V the honest way (local depth and local water speed at the peak-depth frame,
measured 3 dx to 0.5 dx upstream of the vehicle's minimum-x face across its y extent,
99.5th percentile of water z above the floor):

| class | nominal D x V | honest D x V | change | L1 nominal | L1 honest | L2 |
|---|---|---|---|---|---|---|
| small_passenger | 0.4500 | 0.1892 | -58.0 % | NO-FORD | NO-FORD | NO-FORD |
| large_passenger | 0.4500 | 0.1645 | -63.4 % | FORD | **NO-FORD** | NO-FORD |
| large_4wd | 0.4500 | 0.1530 | -66.0 % | FORD | FORD | FORD |

The large_passenger flip is on the DEPTH limit (local peak 0.4159 m exceeds 0.40 m), not on
D x V (0.1645 is far under 0.45). Caveat, because it decides a verdict: the local peak is a
transient stagnation maximum at the surge front, frame 29 of 90, and by the final frame
local depth has fallen to 0.107 to 0.124 m as the finite slab drains. Whether AR&R's D means
approach depth, stagnation peak, or a time average is unresolved and it is the whole
question for that class.

## THE VERBATIM GRID/LIM LINE

From the live Vista stdout of the 1100 kg run:

    grid 64^3 lim=9.42m  water 23532 + vehicle 8905 particles (1100.0 kg)  dt=3.03e-03 (11 substeps/frame)
    INSTRUMENT dx=0.147213 h=0.073606 floor=0.441638 lim=9.421618
    INSTRUMENT water_layers=4
    INSTRUMENT solid_volume=3.55124 m3  hull=3.54274 m3  fill_ratio=1.0024
    INSTRUMENT realized_rho=309.75 kg_m3

And the source line it comes from, `src/warpmpm/vehicle.py` in `FloodScene.__init__`:

    lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
    self.grid = GridConfig(n_grid=n_grid, grid_lim=lim)

`load_vehicle` rotates the long horizontal axis onto **y** before this runs, so `ext[1]` is
4.2826 and `lim` is 9.42163 at depth 0.30. F0's 14.9890 came from unswapped axes.

## THE TEST-FIRST RESULT: splat_positions applies the pose

`src/warpmpm/vehicle.py:491`, quoted verbatim:

    def splat_positions(self) -> np.ndarray | None:
        """The vehicle's visible splats moved rigidly with the body."""
        if self.vehicle.splat_pos is None:
            return None
        R, t = self.vehicle_pose()
        return self.vehicle.splat_pos @ R.T + t

It applies the body pose, so the brief's hypothesis was right and no Kabsch/SVD recovery was
needed. In this session I used the equivalent public path directly: dump `vehicle_pose()`
per frame, then apply `x_scene = x_veh @ R.T + t` offline to whatever point set I want to
draw. Round-trip error 1.857e-06 m.

## RUNGS USED, AND WHY EACH WAS LEFT

| ladder | rung | outcome |
|---|---|---|
| RENDER | R1 matplotlib scatter of `.surface` | Ran, produced `car_check_points_R1.png`. Left it: at 60k points with alpha the silhouette was not crisply legible at panel scale. Not a failure, a readability limit. |
| RENDER | R2 Poly3DCollection, `simplify_quadric_decimation(8000)` | **Used.** Decisive for G1. Also used at 3000 faces as the transparent readability shell in the flood frames. R3 PyVista, R4 vtu, R5 npz-to-Mac were never needed. |
| WATER | W1 depth/speed-shaded particles, viridis, fixed limits | **Used, sufficient as predicted.** vmin 0, vmax 2.700 m/s from the 99th percentile over all frames, identical across every frame. W2 and W3 not needed. |
| ENCODE | E1 `imageio_ffmpeg` bundled binary | **Used, worked.** `ffmpeg-macos-aarch64-v7.1`. mp4 is 7.50 s, h264, 1704x770, 12 fps. |
| ENCODE | E2 Pillow GIF | **Also used**, both deliverables produced. E3, E4, E5 not needed. |
| ALLOC | A1 sbatch to gh-dev | **Not used.** squeue showed job 866266 already RUNNING. |
| ALLOC | A2 srun --overlap onto a running job after checking nvidia-smi is idle | **Used.** GPU was 0 % utilisation, 2 MiB of 97871 MiB, no compute apps. Reused it per the allocation rules rather than queueing behind it. Zero new allocations taken this session. |
| MESH | M1 current Yaris, validated | **Used.** M2/M3/M4 not needed. |

Login-node path abandoned after two attempts: `from warpmpm.vehicle import load_vehicle` on
`login1` exceeded a 240 s timeout, RC=124, twice. Worked around by AST-extracting the pure
numpy functions (`_up_rotation`, `solidify_columns`, `solidify_watertight`, `euler_zyx`) from
the live Vista `vehicle.py` and executing them on the Mac. That path was then validated
against Vista digit for digit (hull 3.542739, lim 9.42163, h 0.0736065, parity N 8904,
rho 309.78), so it is the real code, not a transcription.

## COMMANDS RUN

    ls -1 ~/.claude/skills
    cat ~/can-it-ford/.claude/settings.json; ls -la ~/can-it-ford/.claude/hooks/
    claude mcp list
    ssh vista 'hostname; squeue -u $USER ...; /usr/local/etc/taccinfo'
    ssh vista 'cd /work/11603/jcerrell0629/vista/mpm-engine && git status --porcelain; git log -1'
    ssh vista "sed -n '150,275p;328,496p' .../src/warpmpm/vehicle.py"
    ssh vista '... timeout 240 python -c "from warpmpm.vehicle import load_vehicle"'   # RC=124 twice
    scp vista:.../src/warpmpm/vehicle.py <scratchpad>/vehicle_live.py                  # md5 4c3e8b2e3870194f9ec30f5398ca8407
    python3 renders/yaris_render_s1/g0_validate.py
    python3 renders/yaris_render_s1/g1_car_check.py       # R1
    python3 renders/yaris_render_s1/g1b_car_check.py      # R2, wrote figures/car_check.png
    ssh vista 'squeue -u $USER'                            # 866266 RUNNING, idv45249, c642-001
    ssh vista 'srun --jobid=866266 --overlap -p gh-dev -N1 -n1 -t 00:02:00 bash -c "nvidia-smi ..."'
    scp renders/yaris_render_s1/{sim_dump.py,run_s1.sh} vista:/scratch/11603/jcerrell0629/render_s1/
    ssh vista 'srun --jobid=866266 --overlap -p gh-dev -N1 -n1 -t 00:25:00 .../run_s1.sh'
    scp vista:/scratch/11603/jcerrell0629/render_s1/m{1100,1609,2337}/{rollout.npz,summary.json,metrics.csv} .
    python3 renders/yaris_render_s1/gates.py --runs m1100 m1609 m2337
    python3 renders/yaris_render_s1/s2_gridgate.py
    python3 renders/yaris_render_s1/render_flood.py --run m1100 --outdir seq_m1100 --title ...
    python3 renders/yaris_render_s1/encode.py --frames seq_m1100/_frames --mp4 ... --gif ... --fps 12

`run_s1.sbatch` was written but **never submitted**, because A2 applied instead. It is kept
in the render dir as the A1 fallback.

## THREE-CLASS TABLE

Full version with sources at `figures/three_class_table.md`. Summary:

| class | mass (kg) | fill ratio | rho | final abs d (m) | yaw (deg) | L1 nominal | L2 | agree? |
|---|---|---|---|---|---|---|---|---|
| small_passenger | 1100 | 1.0024 | 309.75 | 0.09240 | +1.431 | NO-FORD | NO-FORD | AGREE |
| large_passenger | 1609 | 1.0023 | 453.13 | 0.05110 | +0.016 | FORD | NO-FORD | DIVERGE |
| large_4wd | 2337 | 1.0023 | 658.14 | 0.03890 | +0.310 | FORD | FORD | AGREE |

**V1 IS MASS-ONLY. All three use the SAME Yaris hull.** The 1609 row is not a Rogue and the
2337 row is not a Silverado. V2 real-mesh conversion was **not attempted** this session; the
budget went to the numeric gates instead after the brief was replaced mid-run.

L2 rule is final |d| vs DRIFT_THRESHOLD = 0.05 m, which **has no peer-reviewed source** and
must be described as a conservative numerical onset-of-motion tolerance in the same sentence
as any verdict. large_passenger sits 2.2 percent above it and is inside its own uncertainty.

## PROVENANCE MANIFEST ROW

| column | value |
|---|---|
| Artifact | `figures/yaris_flood.gif` (5546601 B), `figures/yaris_flood.mp4` (4962780 B), `figures/yaris_hero_frame.png` (650009 B) |
| Source data | `renders/yaris_render_s1/m1100/rollout.npz` (30294805 B, 2026-07-25 19:17), `metrics.csv` (34602 B, 92 rows x 15 cols), `summary.json` (1292 B); produced by Vista job 866266 on node c642-001, GH200 120GB, exit 0 |
| Generating script | `renders/yaris_render_s1/sim_dump.py` (sim) and `render_flood.py` + `encode.py` (render), all UNTRACKED as of writing; solver is `mpm-engine` HEAD `fd390d6` **plus an uncommitted `vehicle.py` working-tree patch** |
| Params | depth 0.30 m nominal, velocity 1.5 m/s nominal, n_grid 64, 90 frames at 30 fps, vehicle_mass 1100.0 kg, grid_lim 9.421618, dx 0.147213, h 0.0736064, floor 0.441638, water_layers 4, water_density 1000, bulk_modulus 1.5e5, water_eta 1.0, floor_friction 0.5, settle_frames 8, seed 0 |
| Solver + scene | MPM, `warpmpm` `FloodScene`, real watertight NCAC Yaris mesh (not a box proxy, not a warped mesh, not a splat), single rigid body, finite dam-break slab, closed slip walls inset 4 dx |
| What it shows | A 1100 kg small-passenger vehicle on a real hull, under a 0.30 m / 1.5 m/s surge, slides 0.0924 m and yaws +1.43 deg, does not float (z_min rise 0.000000 m), with 0 particles outside the domain and 3.68 % max water in the vehicle bbox |
| What it does NOT show | Any FLOAT or TOPPLE mode. Any steady-state flood (the slab drains; local depth falls from 0.397 m to 0.107 m). Any geometry effect between vehicle classes (mass-only). Any validated wave physics (bulk modulus softened, no benchmark exists at this scale). It is one point, not a sweep. |
| Caveat label | **MPM-REAL** |

## WHAT IS NOT DONE

- `solidify_watertight` is still UNCOMMITTED on Vista. Highest-risk item in the project.
- V2 real Silverado/Rogue meshes not converted, so the three-class result is mass-only.
- No depth/velocity sweep on corrected geometry. One point only.
- Poster does not yet carry any of these L2 assets.
- `gates.py`'s local-depth probe had a real bug found and fixed mid-session: it sampled the
  vehicle's maximum-x face (the wake) instead of the minimum-x face (the upstream stagnation
  side), which returned negative depths. Anyone reusing that probe should read the fixed
  version, not an earlier copy.
