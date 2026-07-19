# Session State

Read this before doing anything else, on any machine. Update the relevant section before you stop working, even mid-task. This file exists so a fresh terminal or a fresh chat session can pick up exactly where the last one left off, instead of re-deriving it from memory.

Last updated: July 10, 2026, 06:44 UTC (Claude chat, verified live against GitHub + Slack, not from memory).

---

## MacBook (local)

**Last command run:** n/a, seeded from chat verification, not a real terminal session.
**Current status:** Not the blocker right now. Everything blocking is on Vista.
**Next action:** none queued.

## Vista (Genesis MPM, GH200)

**Last command run:** `idev -N 1 -n 1 -p gh-dev -t 1:30:00`, landed on `c642-051`, then `cd /work/11603/jcerrell0629/vista/can-it-ford` (note: repo is one level deeper than `/work/11603/jcerrell0629/vista`, the plain path is NOT a git repo, `can-it-ford` is a subfolder of it), `git fetch origin`, `git log HEAD..origin/main --oneline` queued, output not yet reported back to chat.
**Current status:** `grid_density` (64 vs 128) has since been tested and ruled out as the crash cause. The run still crashes at step 0 regardless of grid density. The current live suspect (as of July 13) is the domain-widening commit's bounds themselves (lower_bound=(-2.5,-1.0,-0.1), upper_bound=(4.5,1.0,2.5)), independent of grid_density, box size, and vehicle position, each of which was tested and ruled out individually. This has not yet been tested in combination with the corrected vehicle mass (rho=115.7).
**Next action:** `git pull` inside `can-it-ford` (now that the path is correct), then rerun with `CUDA_LAUNCH_BLOCKING=1`, tee the full output to `logs/mpm_crash_july10.txt`. This has never been done, no traceback has ever been captured for this crash.

## Gsplat / COLMAP (real drain footage, separate Claude Code session, MacBook)

**Last command run (as best reconstructed from a garbled terminal paste):** SD card mounted at `/Volumes/Untitled/DCIM/891_0709/`, 5 MP4s found, 4 usable (2954 is 1.5s, discarded). Classified as 2 drains: **Drain A** = 2955/2957/2959 (limestone wall, metal railing, P18 sign; best orbit = 2957), **Drain B** = 2956 (plaza, red Adirondack chairs). Files renamed to `drainA.MP4`/`drainB.MP4`, frames extracted via `ffmpeg -vf fps=2` for both (Drain B expected ~354 frames from its 177s duration). Session then moved to COLMAP: was instructed to SSH to `ls6.tacc.utexas.edu`, but the terminal prompt actually shown was `(vista) c609-122[gh]`, meaning it ended up on a Vista compute node, not LS6. `echo $SCRATCH` confirmed `/scratch/11603/jcerrell0629`, `mkdir -p $SCRATCH/datasets` succeeded. One command failed on a stray leading `- ` character (`-bash: -: command not found`), harmless typo, not yet re-run clean.
**Current status:** THIS IS REAL PROGRESS ON PIECE 1 (real gsplat scene) for the first time in the project. Not yet run: `scp` the extracted frames to `$SCRATCH/datasets/drainA` (and B), then COLMAP `feature_extractor` + `exhaustive_matcher` + `mapper` (CPU-only mode, `--SiftExtraction.use_gpu 0 --SiftMatching.use_gpu 0`, per the session's own plan) to get camera poses. Health check to watch for: the mapper's `Registered images: X / Y` line, expect most of the ~354+ frames to register or the reconstruction is unusable (motion blur suspected as the failure mode if it's low).
**Next action:** re-run the `$SCRATCH` setup cleanly (drop the stray `- `), scp Drain A's frames over, run COLMAP on Drain A first, report the registered-image count before touching Drain B or spending a gsplat training run on it. Also unresolved: confirm whether staying on Vista (vs the originally planned LS6) is fine for this, or whether gsplat training specifically needs LS6's tested environment.

**[Jul 15, verified on Vista by direct `ls`/`find`, not from memory]** `/scratch/11603/jcerrell0629/datasets/drainA` and `drainB` both exist but are **EMPTY (0 files)**. The frames were never scp'd, so COLMAP has never run on either drain, and **no gsplat-trained splat of Drain A or Drain B exists on Vista**. A filesystem-wide search found **zero** gsplat checkpoints: no `point_cloud.ply`, no `.sog`, no `hicss-splat`. The only `.ply` files present are vehicle assets (`truck_trimmed.ply`, `car_mesh.ply`, `car_mesh_rescaled.ply`) plus Genesis's own bundled URDF samples. Piece 1 is therefore still at step 0, and the "REAL PROGRESS" note above overstates it: frame extraction happened on the MacBook only and never reached the cluster. Anything downstream that needs a real scene splat is blocked on this, not on the bridge.

## Rotating / fourth pane

**Current status:** undefined. Ask what this pane is actually used for day to day (a second Vista render pane, a live log tail, or a git/GitHub pane) before building a fixed tmux layout around it.
**Next action:** decide this once, then it stops being a question.

---

## Cross-cutting, not tied to one machine

- **W&B API key:** confirmed still present in `wandb_backfill.py`'s git history (commit `50eff29`), per `PROJECT_FILE_MAP.md`. Removing it from the current file does not remove it from history. Rotate on wandb.ai today regardless of current-file state. **[Jul 10, 08:08 UTC, MacBook]** Repo confirmed **PUBLIC** on GitHub (`4bd2967` + `50eff29` are on `origin/main`), so the historical key is compromised. Current file `analysis/wandb_backfill.py` verified clean (reads `os.environ`; a dangling `wandb.login(key=API_KEY)` on line 22 references an undefined name — harmless, worth deleting). User reports creating a new key, but the **revoke of the exposed key is still UNCONFIRMED** — do not mark rotated until verified on wandb.ai.
- **Poster board size:** not confirmed anywhere (Slack, calendar, or files, all checked). Ask Rosie or Luke directly, do not guess or default to 42x56/48x36/42x60.
- **Poster session date:** master doc says July 30, one external note claims July 29. Neither independently confirmed via calendar in this session. Confirm directly before building anything date-specific.
- **10 AM meeting:** Kumar, Josie, Josue Ortiz confirmed via Slack for "tomorrow" relative to July 9, i.e. today, July 10.
- **Local repo note:** `~/can-it-ford/kumar_july9_update/` was committed and pushed from the MacBook (commit `cbba280`), separately from and prior to the GitHub-API-side edits made in Claude chat today. Both landed on the same `main`, no conflict, but it's worth knowing two different tools have been writing to this repo today.

**Bridge scaffold (bridge/):** landed on main via rebase, 13:49 UTC. extract.py, gaussian_io.py, genesis_particles.py applied clean, no conflicts in the actual code.

**[Jul 15] Bridge is still a scaffold. Commits `fecaaa0` and `101f266` are documentation-only.** Both touch `bridge/README.md` and `.gitignore` and contain **zero code changes**. They confirm one narrow API fact (Genesis `MPMEntity.set_particles_pos(pos)`, shape `(M,N,3)`, called after `scene.build()` before the first step, with particle count `N` fixed by the seeding morph). They do **not** constitute a splat-loading integration. Three stages still raise `NotImplementedError`: `gaussian_io.load_gaussian_checkpoint` (TODO-1, stage 1, so the bridge cannot ingest a splat at all), `filling.fill_internal_particles` (TODO-5), and `genesis_particles.to_genesis_scene` (TODO-6, stage 9).

**Doc/code drift to fix in `bridge/genesis_particles.py`:** README TODO-6 and Open Question 1 now say pre-positioned seeding is confirmed supported, but the live `to_genesis_scene` stub still carries the pre-`fecaaa0` text ("Genesis v1.2.0 may only support the per-step emitter pattern ... Verify BEFORE building this"). The doc was updated, the stub was not. Do not read that stub as an open question, it is stale.

**Two separate engines, do not conflate (this bit a session on Jul 15):** `load_gaussians_ply` is real and working, but it lives in **Track 1's mpm-engine** (`src/warpmpm/splats/io.py`), not in the Track 2 Genesis bridge. `examples/splat_sim.py` already demonstrates the full splat -> `SplatScene` -> warpmpm `Solver` path with a material (`--ply`, materials `dough`/`elastic`/`sand`; `newtonian()` is available for a fluid). `vehicle.py:load_vehicle` also reads a splat PLY, but that is the **vehicle** body, not scene geometry.

**`FloodScene` structurally cannot take a scene splat as water/road geometry.** Its `__init__` accepts only a `VehicleBody`. Water is generated procedurally as an analytic meshgrid slab, and the road is a flat implicit floor at `z = 3*dx`. There is no scene-geometry input to feed. Loading a reconstructed splat as water/road would require changing `vehicle.py` itself (a real design change, not a new script), so any task phrased as "load the splat into FloodScene without modifying vehicle.py" is not achievable as stated.

## Track 1 vehicle density fix (Jul 15, sweep v2)

**The bug was NOT in `solidify_columns`.** That function is correct. The bug was in `scripts/ford_sweep_driver.py`: all three vehicle classes loaded the same `truck_trimmed.ply` and were scaled by `load_vehicle(target_length=...)`, which rescales **uniformly** on all three axes. Every class was one truck at a different zoom. Proof: v1 produced `n_particles = 7454` and `fill = 0.429` identically for sedan, SUV and pickup.

**Fix applied (in `ford_sweep_driver.py` only, Kumar's `mpm-engine` untouched):** new `fit_to_bbox()` scales the splat surface anisotropically to each class's real bounding box, then re-solidifies at the scene pitch. Masses and bboxes now come from `vehicle_params.py` via `get_vehicle()` (NHTSA/SAE cited) instead of hand-typed values. Old driver values were sedan 1240 kg / L=4.6, SUV 2020 / 4.8, pickup 1930 / 5.5, none of which matched the cited file.

**Measured results, sweep v2, SLURM job 833218, 36/36 runs, all plateaued:**

| class | mass kg | bbox L,W,H | n particles | volume m3 | density kg/m3 | in 100-300 |
|---|---|---|---|---|---|---|
| sedan | 1390 | 4.66, 1.79, 1.44 | 9216 | 4.7352 | 293.55 | yes |
| suv | 1990 | 4.96, 1.93, 1.75 | 10424 | 6.4583 | 308.13 | **no** |
| pickup | 2300 | 5.89, 2.03, 1.96 | 9156 | 9.4993 | 242.12 | yes |

Was sedan 336.61 / SUV 482.61 / pickup 306.51, all implausible. Particle counts now differ per class, confirming three distinct bodies. GPU results reproduced the login-node prediction to the decimal.

**SUV at 308.13 is 2.7% over and was deliberately NOT tuned under the line.** Cause: the truck splat shell is holey, so column fill reaches only ~39% of the bbox. Forcing it under 300 would require either changing the cited mass or inflating the volume estimate, both dishonest. The 100-300 band is a soft heuristic from `FloodScene`'s own docstring, not a physical threshold; nothing in the physics keys off it and the SUV floats regardless. Recorded honestly as `density_plausible=False`.

**Known remaining limitation, state this in the poster/paper:** each class is a truck silhouette stretched to that class's bbox. Bounding box, volume, buoyancy and side-on drag area are now correct per class, but the shape detail is still a pickup. This is "truck shell fit to a sedan bbox", NOT a sedan. Fixing it properly needs a per-class mesh, which the project does not have.

**SuGaR was evaluated and rejected.** It converts one trained splat into one mesh, so it would still yield one truck and cannot manufacture sedan/SUV geometry; it does not address this bug. It also requires the COLMAP dataset and source images, and only `truck_trimmed.ply` exists (no `sparse/`, no `cameras.bin`, no images). Arch was a secondary concern: SuGaR pins torch 2.0.1/CUDA 11.8, and CUDA 11.8 does support sm_90, but no aarch64 wheels exist for that stack so torch, pytorch3d, diff-gaussian-rasterization and simple-knn would all be source builds. Confirmed this node is NVIDIA GH200 120GB, compute capability 9.0.

**There is no FORD/NO-FORD verdict column, in v1 or v2.** The Track 1 driver has never computed a verdict; it records kinematics only (`final_disp_m`, `final_yaw_deg`, `final_roll_deg`). Any claim of an "all-36 NO-FORD baseline" is not backed by the manifest and must not be repeated as if it were.

### DRIFT_THRESHOLD, approved reframe (Jul 15)

`DRIFT_THRESHOLD` stays, but is reframed as a **conservative numerical onset-of-motion detector**, internal to the solver. It is NOT a physical criterion and NOT a literature threshold.

- The **0.05 m number itself has no peer-reviewed basis and never will.** Do not cite anything for it. In particular do not cite "Smith et al. 2019, Eq. 6"; that equation does not exist in that paper.
- Cite **Xia et al. 2014** (DOI 10.1007/s11069-013-0889-2) and **Shah et al. 2018** (DOI 10.1051/matecconf/201820307003) for the **underlying incipient-motion physics only**, never as a source for 0.05 m.
- For scale, 0.05 m is roughly 2.5-3.4% of representative vehicle body width.

### Threshold sensitivity check (run Jul 15 against both manifests on disk)

Verdict rule tested: `final_disp_m > threshold` -> NO-FORD. 36 matched cells in both sweeps.

| threshold | v1 NO-FORD / FORD | v2 NO-FORD / FORD | runs flipping v1 -> v2 |
|---|---|---|---|
| 0.02 m | 36 / 0 | 35 / 1 | 1 |
| 0.05 m | 36 / 0 | 34 / 2 | 2 |
| 0.10 m | **30 / 6** | **27 / 9** | 3 |

**The verdict is NOT threshold-robust, and this is the important result.** The "all-36 NO-FORD" claim survives only at thresholds <= 0.05 m. At 0.10 m, v1 itself breaks to 30/6, so the baseline was an artifact of the chosen tolerance, not a property of the physics. Doubling the tolerance from 0.05 to 0.10 moves v2 from 34 NO-FORD to 27, a 7-run swing.

**Every flip is at depth = 0.15 m**, the shallowest condition, and all are toward FORD in v2 (heavier cited masses resist drag):

- 0.02 m: pickup 0.15/1.0 (0.0877 -> 0.0197)
- 0.05 m: adds pickup 0.15/1.5 (0.1035 -> 0.0435)
- 0.10 m: pickup 0.15/1.5, pickup 0.15/2.0 (0.1335 -> 0.0524), sedan 0.15/2.0 (0.1140 -> 0.0781)

**Fragility is concentrated, and it is large.** 8 of 36 v2 runs sit within 2x of the 0.05 m threshold (between 0.025 and 0.100 m), and 14 of 36 sit within 2x of 0.10 m. So a substantial fraction of the dataset is close enough to the tolerance that its classification is decided by the tolerance rather than by the flow.

**Honest reading for the poster/paper:** at depth 0.15 m the Track 1 verdict is threshold-dominated and should not be reported as a physics result. The verdict is only defensible at the deeper and faster conditions, where displacement exceeds any of these tolerances by an order of magnitude. Report the sensitivity table rather than a single threshold's verdict count.

### CRITICAL: the v2 depth=0.15 m rows are under-resolved, verdict flips are NOT established (found Jul 15, after the sweep)

The `--dry-run` preflight added to the driver **refuses the v2 config outright**:

```
pickup  depth=0.15m dx=0.2025m water_z_layers=1 UNDER-RESOLVED
REFUSING: 1 cells have < 2 water particle layers.
```

**This is a regression introduced by the density fix itself.** Scaling the pickup to its cited length (5.5 m -> 5.89 m) grows `lim = max(2.2*length, ...)`, which grows `dx = lim/n_grid`, which coarsens the water. At depth 0.15 m and `n_grid=64` the pickup's water slab went from 2 particle layers (v1) to **1** (v2). One layer cannot represent a slab.

| class | v1 layers @0.15 m | v2 layers @0.15 m | dx v1 -> v2 |
|---|---|---|---|
| sedan | 2 | 2 | 0.1581 -> 0.1602 |
| suv | 2 | 2 | 0.1650 -> 0.1705 |
| pickup | 2 | **1 UNDER-RESOLVED** | 0.1891 -> 0.2025 |

This is the coupled-variable failure CLAUDE.md warns about (`grid_density <-> domain bounds <-> dx`). Changing the vehicle bbox silently changed the water resolution. The dependents named at edit time were box/density/mass; `dx` and water-layer count were missed.

**Consequences, be strict about these:**

- **Every verdict flip reported above is at depth 0.15 m**, which is exactly the marginal/invalid band. The pickup 0.15 flips (0.0877 -> 0.0197 and 0.1035 -> 0.0435) are driven by the water slab collapsing from 2 layers to 1, NOT by the corrected mass. **Do not report these flips as a physics finding.**
- The three pickup depth-0.15 rows in `data/track1_sweep_v2/manifest.csv` (velocities 1.0, 1.5, 2.0) are **invalid** and should be treated as missing data.
- The six sedan/SUV depth-0.15 rows sit at exactly 2 layers, the bare minimum, so they are marginal at best.
- **Densities are unaffected.** 293.55 / 308.13 / 242.12 come from vehicle geometry, not water resolution, and stand as reported.
- Depths >= 0.30 m have 3+ layers and are fine.

**Fix, not yet run:** the `v3` config (`--config v3`, `n_grid=128`, depths from 0.10) passes preflight on every cell (pickup at 0.15 m gets 3 layers, worst case anywhere is 2). Re-run at v3 before any depth-0.15 claim is made. `python scripts/ford_sweep_driver.py --config v3` on a GH200 node; v2 took 1:52 at n_grid=64, so v3 at 128 with 60 runs will take substantially longer.

**Process lesson:** the preflight caught this, the sweep did not. It ran to `DONE 36 runs` and `PYTHON_EXIT=0` while quietly simulating a 1-layer puddle. A green exit code proved nothing here, the same way SLURM's `COMPLETED 0:0` proved nothing for jobs 833156 and 833194.

**Displacements shifted, physically coherently.** Sedan and pickup got heavier under cited masses (1240 to 1390, 1930 to 2300) and move noticeably less (sedan d=0.6/v=1.5: 1.9416 to 1.1991). The SUV got slightly lighter (2020 to 1990) and is essentially unchanged to slightly higher. v1 is preserved at `data/track1_sweep_v1/`; v2 is at `data/track1_sweep_v2/`.

**SLURM gotchas hit while running this, worth remembering.** `gh` and `gh-dev` are genuinely distinct partitions (resolves the open question in CLAUDE.md). The allocation is `BCS20003`, and lowercase `bcs20003` is rejected by the submit filter, so just omit `-A` and let it resolve. Two jobs reported `COMPLETED 0:0` while doing nothing: job 833156 wrote `#SBATCH -o` to login-node-local `/tmp` which does not exist on the compute node, and job 833194 hit `ModuleNotFoundError: wandb` but exited 0 because the script's last line was an `echo`. End SLURM scripts with `exit $rc`. Also: the sweep needs `/work/11603/jcerrell0629/vista/.venv` (wandb 0.28.0, warp 1.15.0), NOT `mpm-engine/.venv` (no wandb, warp 1.14.0). The repo's own `wandb/` directory shadows the real package if the repo root is put on `sys.path[0]`, so the driver appends it instead.

## 2026-07-19: full session consolidation, MCP/data/decisions/infra
MCP: deepwiki, github, wandb, huggingface(hf) connected in Claude Code CLI on
Mac and Vista (user scope). LS6 in progress, confirm with `claude mcp list`
before trusting. .claude/settings.json WebFetch allowlist (48 domains)
committed and pushed on Mac and Vista; confirm LS6's copy matches, not just
exists.
W&B KEY ROTATION CONFIRMED DONE (git log --all -p | grep wandb_v1_ proves the
50eff29-exposed key is a third, dead key). Supersedes any prior "unconfirmed"
note.
DATA: data/track1_sweep_v3/ (n_grid=128) CONFIRMED INVALID, do not cite, do not
plot, do not read from it in any new session. data/track1_sweep_v2/ (n_grid=64)
is the protected valid source, ~24/36 rows valid (sedan+pickup only, SUV
excluded, density-implausible).
RESULT: figures/poster_exports/can_it_ford_phase_space.{png,pdf,html} built
from validated v2 data. L2 calls NO-FORD in 22/24 valid cells where L1 says
FORD. This is a real, citable divergence result.
DECIDED: SUV excluded from plotted markers, one caption line added naming the
exclusion reason, not marked-distinct on-figure. DECIDED: Yaris mesh repair via
mesh2sdf, not fill_holes, per repo's own findings note (919 zero-thickness
interior parts risk sealing the underbody, corrupting buoyancy). Yaris
confirmed 1100kg via deck header, distinct from 1390kg sedan class, do not
conflate.
TASK DASHBOARD (~/can-it-ford agent view) showed 4 awaiting input as of 7/18:
deploy canonical CLAUDE.md (5d), reconcile nine open items (5d), Yaris mesh
(now decided above), process SD card frames for COLMAP (8d+, this is Piece 1
of the real-scene rebuild, highest actual priority, not infra work).
INFRA: Vista repeatedly lands on the login node; when idev did succeed (nodes
c642-011, c642-022) the SSH session died within seconds before any Genesis
command ran. ControlMaster/ControlPersist/ServerAlive added to ~/.ssh/config
for vista and ls6, confirm this actually fixes the drop pattern before relying
on it. tmux session "cif" was only running 4 of 6 intended panes as of last
check, fix given, confirm live.
NEW invisible-parallel-work sources beyond tmux panes and separate CLI
sessions: Claude Code's own dispatched agent-view task dashboard, and
com.josie.canitford-sweep.plist (install-sweep), a Downloads-folder LaunchAgent
running roughly every 2 hours.
STILL OPEN: paper_draft.md two-version reconciliation (root vs paper/, newer
one has Yaris "Small Car class" section, adopt newer, not yet executed), second
Vista clone at /home1/11603/jcerrell0629/can-it-ford still undiagnosed.
