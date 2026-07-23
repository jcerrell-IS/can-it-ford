# Session State

Read this before doing anything else, on any machine. Update the relevant section before you stop working, even mid-task. This file exists so a fresh terminal or a fresh chat session can pick up exactly where the last one left off, instead of re-deriving it from memory.

Last updated: 2026-07-23, 11:30 UTC (Claude Code, MacBook, verified live. Repo made PRIVATE at 11:30 via `gh repo edit`, verified `isPrivate=true`, containing the public leak but NOT fully resolving it (see the security block). This pass wrote the full-round reconciliation subsection at the top of CURRENT ROUND: SECURITY leak labeled honestly (not "clean"), phantom hash f623cd2 corrected to 936026e + b141c48, phantom research file noted, master-ref JSON reconciliation flagged in-progress, RayTracer collision recorded resolved with LuisaRender/crash caveats, Yaris mass logged as a 1078/304.28 recommendation not a fact. Earlier 10:19 pass reconciled the v3-sweep-validity contradiction to INVALID per `docs/v3_invalidation_status.md`. Committed base synced 0/0, but tree has uncommitted multi-pane edits and this SESSION_STATE.md edit is itself uncommitted. Not from memory. Older sections below are retained history; this top block is the current state.)

---

## CURRENT ROUND (2026-07-23) READ THIS FIRST

### 2026-07-23 ~11:07 UTC full-round reconciliation (newest; extends and corrects the 05:13 items below)

**SECURITY, personal-profile leak, STILL PUBLIC, do NOT label this "clean".** Three full copies of the personal CLAUDE.md are tracked on public `origin/main` right now: `files/CLAUDE_md_CANONICAL_july13.md`, `files/CLAUDE_md_FINAL_july13.md`, `files/CLAUDE_md_corrected_july13.md` (each carries "WHO JOSIE IS", ADHD, processing-speed detail; added in `b141c48`, 2026-07-18). Also `.claude/skills/geoelements-tech-reference/SKILL.md` (~line 214, "Keep it short (ADHD)"). The 41-line tracked `CLAUDE.md` is the sanitized "Multi-Pane Standing Rules" file and IS clean; name/major/institution in poster/paper files is intended-public, not a leak. DECISION (Josie, 2026-07-23): make the repo PRIVATE. STATUS: DONE at 11:30 UTC. Ran `gh repo edit jcerrell-IS/can-it-ford --visibility private --accept-visibility-change-consequences` on Josie's explicit go; verified `isPrivate=true`, `visibility=PRIVATE`. Public reads are now blocked. STILL OPEN, do not mark the leak fully resolved: (1) the files were public from 2026-07-18 (`b141c48`) to 2026-07-23, ~5 days, so treat the ADHD/profile content as already-disclosed (may be cached, cloned, or forked); (2) private only walls off the public, but any collaborator with repo access (Kumar, Hassan, Luke, Cheng-Hsi) can still read `files/CLAUDE_md_*.md`, which is exactly who the PRIVACY rule meant to keep it from, so removing those files from the repo (git rm + commit) is still warranted; (3) history purge (git filter-repo + force-push across the Vista and LS6 clones) is the durable fix. The local `git rm --cached` staging option was NOT chosen and was NOT run.

**Git facts corrected.** The 05:13 block below ("0 ahead / 0 behind, 11 commits") was true then; the tree has since taken more pulls/commits. Committed state is currently synced (0/0), but there are uncommitted multi-pane edits: `README.md`, `paper_draft.md`, `vehicle_params.py`, `data/track1_sweep_v2/mpm_sweep_data_schema.md`, `SESSION_STATE.md`. `71d4958` is NOT a merge commit (single parent `b291499`, verified twice); the repo is not mid-merge.

**Phantom commit hash corrected.** `f623cd2` does not exist in this repo (confirmed via `git cat-file`). The real v3 provenance is `936026e` ("Add v3 sweep scaffold; document n_grid=128 hollow-vehicle invalidation") plus `b141c48` (archive of the invalidated v3 data). Cite those, never `f623cd2`. Separately, 8 hex hashes in this file are not objects in this Mac repo: 4 are cross-clone and expected absent (Vista `7d60a05`/`c98e0af`, LS6 `41eb656`/`0b84cb7`); 4 are stated as on main but absent here (`50eff29`, `cbba280`, `fecaaa0`, `101f266`), verify against the clone that created each before citing as current.

**Phantom research file noted.** `vehicle_class_research_summary_2026-07-21.json` is referenced in the tonight-audit block ("keep for history") but exists nowhere on disk. Do not cite it as present. The master-ref JSON exists in two tracked locations plus a worktree (see next item).

**JSON reconciliation outcome: IN PROGRESS, not done.** The two `vehicle_data_master_reference_2026-07-21.json` copies DIFFER (`vehicle_geometry_research/` sha `8255e12` vs `reference_data/` sha `89b8d50`). A locked git worktree `.claude/worktrees/reconcile-vehicle-master-ref` (`777945b`) is mid-reconciliation. Do NOT treat either copy as canonical until that worktree lands; `d5f8729` also left a `.OLD-4906B` backup of the reference_data copy.

**RayTracer collision resolution.** Per `d5f8729`'s own message, the "collision" was two parallel edits to `simulation/can_it_ford_L2_mpm.py` (Vista's water-box reposition `pos 0.275 -> -1.8`, and the Mac's RayTracer/material work: `renderer=gs.renderers.RayTracer()`, plane `surface=Rough`, water `surface=Water()`). Non-overlapping lines, merged with NO git conflict, resolved cleanly. CAVEAT: that water-box reposition does NOT fix the CUDA crash (see the 07-22 status blocks, it re-crashed), and Genesis's RayTracer renderer is LuisaRender-backed; LuisaRender/LuisaRenderPy is a confirmed arm64 build failure (debugging skill / Genesis issue #42), and both Mac and Vista are arm64, so whether the wired RayTracer actually renders on these nodes is UNCONFIRMED. The confirmed-working render path is bpy/EEVEE (the hero shot), not Genesis RayTracer.

**Yaris mass, RECOMMENDATION only, not a fact until confirmed in code.** Recommend 1078 kg / rho 304.28 (NCAC actual modeled weight over solid_volume 3.5427 m3), per CLAUDE.md's "most defensible" option and the `YARIS_MASS_KG=1078` direction already in `scripts/ford_sweep_driver.py` (commit `3a4e82e`). A conflicting earlier instruction this round proposed 1100 / 3.5427 / 310.47 (MASH nominal); both appear in CLAUDE.md's checklist (1078 = most defensible, 1100 = acceptable if labeled). This stays a RECOMMENDATION. `vehicle_params.py` is being edited by another pane right now (uncommitted); confirm its live Yaris value before treating any number as fact. Coupled edit (mass <-> volume <-> rho); do not paste rho into a box-proxy path.

### Push: DONE and verified live
- Josie ran her own push sequence; Claude Code held out of git entirely per instruction. Verified at 05:13 UTC: `main...origin/main` = 0 ahead / 0 behind, `origin/main..HEAD` empty. The 11 previously-unpushed commits are on origin/main. Working tree clean apart from untracked files listed at the bottom.
- Top two commits this round:
  - `a4e7486`: poster figure output cleanup; `coup_friction=0.55` citation audit (`analysis/failure_mode_citations.md`); hero-shot render script (`render_hero_shot.py`) + `figures/hero_shot_test.png`; poster intro/ack (`paper/poster_intro_ack.md`); export tooling (`scripts/export_session_log.sh`, `split_session_log.py`, `launch_cif6.sh`); sweep schema (`data/track1_sweep_v2/mpm_sweep_data_schema.md`); vehicle pull notes (`_inbox/vehicle_files_to_pull.md`, `_inbox/tonight_research_audit_and_file_map.md`); `analysis/build_poster_phase_space.py`.
  - `c308108`: gitignore the export-tool auto-generated logs. `_inbox/LIVE_SESSION_LOG.md` and the `_inbox/.sweep*`/`.export*` files are now untracked + ignored (out of git, not deleted from disk). Also discarded a redundant local diff on `simulation/can_it_ford_L2_mpm.py` because it was superseded by a Vista commit (the Mac's copy of that diff was stale).
- Note for the next session: the session-start local diff on SESSION_STATE.md itself was discarded inside that push, so before this rewrite the file had reverted to the older `5974de6` version. This block is the fresh state on top of it.

### Hero-shot render (this round)
- `render_hero_shot.py` built and run with `~/blender-render-env/bin/python` -> `figures/hero_shot_test.png` (1600x1200, EEVEE). Water = MPM particle cloud colored by speed via viridis (Kumar convention); vehicle = box proxy; CC0 Poly Haven HDRI in `assets/hdri/`.
- ENV CHANGE flagged: `~/blender-render-env` was empty and on Python 3.14 (no bpy wheels), rebuilt in place on Python 3.11 with `bpy 5.0.1` + numpy. That is a change to that env, recorded here because it was not explicitly requested.
- Honest look note: with no arg the script auto-picked the grid64 972k-particle `d0p3_v1p5` frame (verdict FORD), subsampled to 150k. In EEVEE the points read pastel and cube-ish; Cycles would make them true spheres and read truer. NOT yet re-rendered in Cycles. Pass a path as `argv[1]` to pin a specific frame.
- House-rule compliance: script stripped of comments/docstrings, forbidden-import grep (taichi/genesis) CLEAN, parses cleanly.

### Tonight's research audit (`_inbox/tonight_research_audit_and_file_map.md`)
- Load-bearing output: `vehicle_data_master_reference_2026-07-21.json` is now the single file every vehicle-parameter decision should check against. It SUPERSEDES `vehicle_class_research_summary_2026-07-21.json` (stale, keep for history only).
- Settles Dodge Neon inertia: Ixx 441 / Iyy 1748 / Izz 1945 is correct; the Perplexity 2618/515/2684 is wrong. Do not re-litigate.
- NHTSA vPIC JSON files confirmed to hold zero physical data (name lookups only). Stop treating them as a physics source.
- OPEN CONFLICT, do NOT silently fix: the audit states NCAC Yaris modeled weight is 1078 kg -> rho = 1078 / 3.5427 = 304.28 kg/m3. This does NOT match this file's own 2026-07-20 entry (Yaris 1100 kg, mesh vol 6.8185 m3, rho 161.33) or the 2026-07-19 entry (enclosed vol 3.543 m3, 1100 kg). Three volume figures (3.5427 / 3.543 / 6.8185) and two masses (1078 / 1100) are in play and unreconciled. Do NOT paste any single rho into code until the mass/volume pair is settled against a live grep of the actual mesh plus the master reference. This is a coupled edit (mass <-> volume <-> rho), not a one-liner.

### panel_monitor "/loop": SET UP, NOT YET LIVE (verified live 05:13 UTC, flag before trusting)
- INTENT (per Josie): panel_monitor is meant to be the ongoing status source going forward, replacing manual SESSION_STATE updates.
- ACTUAL live state: the `panel_monitor` tmux session holds a Claude Code session FROZEN at a permission-approval dialog for its first baseline command (`tmux ls`). It has created `scripts/pane_check.sh` (untracked) but has NOT run the baseline, NOT scheduled its once-a-minute monitoring cron, and has produced NO status output. So it is not an operational status source yet.
- To make it live: in the panel_monitor pane, approve the pending `tmux ls` prompt (option 1 or 2). Until that happens, THIS file remains the current status source, not panel_monitor. Recheck panel_monitor's live state before citing it as the source of truth anywhere.

### Untracked, decide next session
- `assets/hdri/` (hero-shot HDRI) and `scripts/pane_check.sh` (panel_monitor's monitor script) are untracked. Decide whether to commit or gitignore each. The HDRI is CC0; committing the binary is optional.

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

**Fix proposed here is SUPERSEDED, do NOT re-run at v3.** This Jul 15 note originally proposed the `v3` config (`n_grid=128`) as the cure for the depth-0.15 water under-resolution. v3 was later found INVALID on independent grounds (hollow-vehicle shell artifact), so refining the grid to v3 does not fix the vehicle, it makes it worse. Authoritative resolution: `docs/v3_invalidation_status.md` (2026-07-22), fresh scaling diagnostic gives `p_exp ~ 2.1` (area scaling, a shell signature, not solid `n_grid^3`), density leaves the 100-300 band at n_grid=128; this closes the "COMPLETELY WRONG ON 3 COUNTS" dispute (that twin was byte-identical, carried no counter-argument). The depth-0.15 under-resolution therefore stays OPEN. The real fix is to decouple the body's solidify pitch from the grid pitch, or densify the point cloud before solidifying, NOT to refine the water grid. Make no depth-0.15 claim from either sweep until that is done.

**Process lesson:** the preflight caught this, the sweep did not. It ran to `DONE 36 runs` and `PYTHON_EXIT=0` while quietly simulating a 1-layer puddle. A green exit code proved nothing here, the same way SLURM's `COMPLETED 0:0` proved nothing for jobs 833156 and 833194.

**Displacements shifted, physically coherently.** Sedan and pickup got heavier under cited masses (1240 to 1390, 1930 to 2300) and move noticeably less (sedan d=0.6/v=1.5: 1.9416 to 1.1991). The SUV got slightly lighter (2020 to 1990) and is essentially unchanged to slightly higher. v1 is preserved at `data/track1_sweep_v1/`; v2 is at `data/track1_sweep_v2/`.

**SLURM gotchas hit while running this, worth remembering.** `gh` and `gh-dev` are genuinely distinct partitions (resolves the open question in CLAUDE.md). The allocation is `BCS20003`, and lowercase `bcs20003` is rejected by the submit filter, so just omit `-A` and let it resolve. Two jobs reported `COMPLETED 0:0` while doing nothing: job 833156 wrote `#SBATCH -o` to login-node-local `/tmp` which does not exist on the compute node, and job 833194 hit `ModuleNotFoundError: wandb` but exited 0 because the script's last line was an `echo`. End SLURM scripts with `exit $rc`. Also: the sweep needs `/work/11603/jcerrell0629/vista/.venv` (wandb 0.28.0, warp 1.15.0), NOT `mpm-engine/.venv` (no wandb, warp 1.14.0). The repo's own `wandb/` directory shadows the real package if the repo root is put on `sys.path[0]`, so the driver appends it instead.

**July 16 (Vista):** RESOLVED: `DRIFT_THRESHOLD=0.05` grounded in `citations/drift_threshold_grounding.md`, it is a solver-internal onset-of-motion tolerance (metres of lateral drift), NOT citable to ARR/WRL/Smith (all define D×V incipient-motion limits in m²/s, no displacement distance), value stays 0.05, no source citation on the number, and the paper draft does not reference 0.05 yet; committed. OPEN: the Luo et al. IJRR consistency check could not be run here, no Luo/IJRR citation and no "skill file 03" exist anywhere in the repo, paper draft, or `~/.claude/skills/` on Vista (likely Mac-only, verify there).

## 2026-07-18 evening: SSH auth + MCP cleanup, all machines
- MacBook, Vista, LS6: github/wandb/hf MCP servers reconfigured with real tokens via ~/.env_mcp, verified with `claude mcp list`
- CLAUDE_CODE_OAUTH_TOKEN corruption diagnosed (multiline paste broke Bearer header) and fixed via `read -r` pattern, safe going forward
- SSH keys added to GitHub: Vista (`id_ed25519_github`, already registered), LS6 (`id_rsa`, newly added, labeled "LS6")
- All three git remotes switched HTTPS -> SSH, confirmed via real `git fetch`:
  - Vista `vista/can-it-ford`: 7d60a05..c98e0af
  - LS6 `vista/can-it-ford` (shared /work path): same commit, confirmed separately
  - LS6 `ls6/can-it-ford`: 41eb656..0b84cb7
- Found: `/work/11603/jcerrell0629/ls6/can-it-ford` and `/work/11603/jcerrell0629/vista/can-it-ford` are TWO SEPARATE CLONES at the same commit, not diverged, but worth deciding whether ls6/can-it-ford should be deleted in favor of always using the shared vista path, not resolved tonight

## 2026-07-18 (Vista, Kumar low-velocity sweep task) findings, steps 1-3 read live from simulation/can_it_ford_L2_mpm.py
- Vehicle density/mass CONFIRMED live: `rho=115.7` on box `(4.66, 1.79, 1.44)` (volume 12.01 m3) gives 1390 kg, matches the sedan-class target. No fix needed.
- Simulation domain CONFIRMED live (the question nobody could answer in the Friday meeting): `lower_bound=(-2.5, -1.0, -0.1)`, `upper_bound=(4.5, 1.0, 2.5)`, i.e. 7.0 m (x) x 2.0 m (y) x 2.6 m (z), `grid_density=128`.
- Water render is RAW PARTICLES, not a reconstructed surface: water is `gs.materials.MPM.Liquid()` with `surface=gs.surfaces.Default(color=...)` and no reconstruction/vis_mode set; the camera renders particles directly. Surface-reconstruction fix still pending (verify exact Genesis keyword via container grep before editing).
- NOTE: `can_it_ford_L2_mpm.py` carries a 189-line uncommitted diff (instrumentation + `data/track2_sweep` manifest), file mtime 2026-07-16 13:52, never run (`data/track2_sweep` does not exist), no live process. Low-velocity sweep to be built on it pending confirmation it is safe to keep.

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
plot, do not read from it in any new session. Authoritative record, and the
reconciliation of this against the Jul 15 "re-run at v3" note above (which is now
marked superseded): docs/v3_invalidation_status.md (p_exp ~ 2.1 area scaling,
hollow-vehicle reasoning holds, supersedes the byte-identical "COMPLETELY WRONG"
twin). data/track1_sweep_v2/ (n_grid=64) is the protected valid source, ~24/36
rows valid (sedan+pickup only, SUV excluded, density-implausible).
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

2026-07-19  Yaris coarse v1l watertight hull CONFIRMED via direct-card-parse (*NODE/*ELEMENT_SHELL, no Deck() hang) + mesh2sdf 256^3 padded SDF, +17mm offset. is_watertight=True, winding-consistent. bbox 4.283 x 1.746 x 1.518 m (subcompact Yaris, NOT Civic 4.66m). V=327,212 F=655,308, enclosed vol=3.543 m^3, underbody kept open. Mass 1100 kg per deck header (tons,mm,N,sec). Do NOT apply 1390 kg Civic mass. Output: vehicle_geometry_research/yaris_coarse_v1l_watertight.{obj,ply}

## 2026-07-20 (Vista, Yaris watertight mesh confirmed + mass correction)
- `yaris_sedan_watertight.ply` CONFIRMED real on the Mac (977025 bytes, Jul 17 06:07, mesh2sdf output: watertight=True, 1 component, volume 6.8185 m3); NOT present anywhere on Vista (repo-wide and `/work/11603/jcerrell0629/vista` `find -iname '*.ply'` both return zero), so it must be synced to Vista before any Vista run can load it.
- Yaris target mass corrected to 1100 kg (this specific NCAC FE deck's own stated curb mass, a primary source for this exact geometry), superseding the 1050 kg generic-subcompact estimate and the 1390 kg Civic/Corolla figure that was never this vehicle's mass; mesh-based rho = 1100 / 6.8185 = 161.33 kg/m3, to be used only once the mesh is wired in.
- Mesh-wiring into `simulation/can_it_ford_L2_mpm.py` and `simulation/can_it_ford_L2_mpm_ytest.py` INTENTIONALLY DEFERRED: both still use `gs.morphs.Box()` (L2_mpm.py VEHICLE_RHO=115.7, ytest.py hardcoded rho=604), and switching to `gs.morphs.Mesh()` makes the grid_density=128 hollow-vehicle risk live (Genesis issue #600), a deliberate design decision, not a quiet rho edit. gs.morphs calls left untouched this session.

Mon Jul 20 05:58:43 CDT 2026: drain_2956 COLMAP complete, 265/267 registered (99.25%), 62.9min runtime. Winner for gsplat training. drain_2957 blur-culled (261 clean frames) but COLMAP not yet run.

---

## 2026-07-22 19:53 CDT: consolidated four-pane status pass

Written from live artifacts (grep/cat/git of the files, plus `tmux capture-pane` of each pane), not from memory or from any pane's summary. Each block states only what is confirmed on disk right now.

### 1. Water-box overlap fix (pane canitford.0, Vista, CUDA crash)

**NOT FIXED. Still open, in-progress as of 2026-07-22 19:53 CDT.** Moving the water box was tested and does not resolve the crash: it either re-crashes identically or produces a fake "success" (no real coupled run). The overlap hypothesis (B03) was never even confirmed as the crash cause; the live suspect remains the domain-widening bounds (`lower=(-2.5,-1.0,-0.1)`, `upper=(4.5,1.0,2.5)`), consistent with CLAUDE.md. No CUDA traceback has been captured yet. Next proposed action (not yet run, awaiting go): test `coup_softness` on the vehicle material. Do not report the coupled MPM sim as running.

### 2. Yaris flood-sweep numbers (pane canitford.1, Vista)

**NO NUMBERS EXIST. Run FAILED, in-progress as of 2026-07-22 19:53 CDT.** Latest attempt failed at 0/12 runs on a mesh-vs-splat loader bug; no output was produced. Confirmed on disk: no `data/track2_sweep/`, no Yaris sweep manifest anywhere; the only sweep manifests present are `data/track1_sweep_v1/manifest.csv` and `data/track1_sweep_v2/manifest.csv` (both truck-shell, not Yaris). The failure was logged honestly. Blocker: the Yaris asset/loader must be fixed first (smallest version: export the watertight hull to `.obj` and repoint `YARIS_PLY`) before any real Yaris (C1) result can exist. Do not cite or plot any Yaris sweep verdict.

### 3. designsafe-staging parity check (staging vs main sim script)

**PARITY CHECK DONE. RECONCILIATION NOT DONE.** Live grep confirms the staging copy is stale on two coupled parameters:

| parameter | main `simulation/can_it_ford_L2_mpm.py` | staging `designsafe-staging/scripts/can_it_ford_L2.py` |
|---|---|---|
| coup_friction | 0.55 (line 28) | 0.4 (lines 40, 132) |
| vehicle rho | 115.7 (line 27) | 604 (line 40) |

The staging `rho=604` is the pre-resize regression value CLAUDE.md flags (old box density never recomputed). `git status` shows no local change to the staging script, so no fix has been applied. Do not run or cite anything from the staging copy claiming friction=0.55 until it is reconciled.

### 4. Methods section status (pane ford.0, paper_draft.md)

**Section 3.3 "Rigid-Fluid Coupling in the MPM Solver" ADDED to the root `paper_draft.md` (grep-confirmed present; file is uncommitted, `git status` shows ` M`).** It correctly attributes the Section 4.3 sweep to the Track 1 mpm-engine solver, not Genesis. The water-box-overlap paragraph was DELIBERATELY HELD (grep confirms it is absent): there is no confirmation anywhere that the overlap bug is fixed (see block 1), so writing it would overclaim. Correct call. Canonical draft is the root `paper_draft.md` (newest, has the full Results section); `paper/paper_draft.md` is stale (Jul 17, 5.5 KB) and should not be edited. Still to do: commit the root draft.

**One-line rollup:** blocks 1 and 2 are still-open/in-progress (crash unresolved, Yaris run has zero output); block 3 is a confirmed mismatch with the fix not yet applied; block 4 is the only real forward progress (coupling subsection written, uncommitted, overlap paragraph correctly held).

---

## 2026-07-22 21:38 CDT: consolidated status re-check (supersedes 19:53 pass)

Written from live artifacts (git log/status, grep of on-disk scripts, `tmux capture-pane` of canitford.0/1/2 and ford.0/2) at 21:38 CDT, not from any pane's summary. Repo is moving during this check (designsafe-staging HEAD advanced de4391e -> ab11309 mid-pass) and SESSION_STATE.md still has uncommitted edits from another pane.

### 1. Water-box fix outcome (pane canitford.0, Vista MPM crash)
**NOT FIXED. In-progress as of 21:38 CDT.** Local `simulation/can_it_ford_L2_mpm.py:145` still reads `pos=(0.275, 0.0, water_depth/2.0)`. The Vista working tree has an UNCOMMITTED reposition to `pos=(-1.8, ...)` and a NEW `crash_trace_july22_water*` file appeared, i.e. it re-crashed. No CUDA traceback captured on this machine. Local and Vista diverge; nothing committed. Do not report the coupled MPM sim as running.

### 2. Yaris sweep numbers (pane canitford.1, Vista)
**NO NUMBERS EXIST. In-progress as of 21:38 CDT.** On disk: only `data/track1_sweep_v1/manifest.csv` and `track1_sweep_v2/manifest.csv` (both truck-shell). No `data/track2_sweep/`, no Yaris manifest anywhere. No Yaris sweep verdict exists to cite or plot.

### 3. designsafe-staging parity check (pane canitford.2)
**PARITY MISMATCH STANDS; RECONCILIATION NOT DONE. In-progress as of 21:38 CDT.** `designsafe-staging` is a working clone of github.com/jcerrell-IS/can-it-ford.git, currently ahead 4 and UNPUSHED (not in parity with origin/main). Staging `scripts/can_it_ford_L2.py` still carries the stale coupled params (coup_friction=0.4, rho=604) flagged at 19:53; git shows no fix applied. Pane canitford.2 is blocked waiting on a "C0" entry that was never written; the reconciliation never ran.

### 4. Methods section status (panes ford.0 / ford.2)
**PAPER METHODS: DONE. POSTER METHODS PANEL: NOT DONE (in-progress as of 21:38 CDT).** Paper Methods 3.4 committed (de4391e, honest open-issue note) and 3.3 committed earlier (e173175), both real in staging history. Poster Methods panel is NOT saved: `paper/poster_methods.md` does not exist on disk; pane ford.2 is waiting for a go and flags an unresolved 1078-vs-1100 kg mass conflict between the draft and Abstract/section 3.1.

**Rollup:** only item 4's paper-side is confirmed done. Items 1, 2, 3 and the poster panel are all still open/in-progress at 21:38 CDT.
