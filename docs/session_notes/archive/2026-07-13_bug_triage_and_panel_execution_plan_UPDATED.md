# Can It Ford — Bug Triage, Root Cause Map, and 8-Panel Execution Plan
## July 13, continuation of last night's session

---

## 0. What I actually checked before writing this (read this before trusting anything below)

You asked me not to just trust my own prior audit. Here's what I did instead of that:

- **Re-derived the overlap math myself from the raw tuples**, not from the prior summary. Water box: pos=(0.275, 0, depth/2), size=(0.35, 1.8, depth) → x∈[0.10, 0.45], y∈[-0.90, 0.90], z∈[0, depth]. Vehicle box: pos=(1.0, 0, 0.755), size=(4.66, 1.79, 1.44) → x∈[-1.33, 3.33], y∈[-0.895, 0.895], z∈[0.035, 1.475]. All three axes overlap at every tested depth ≥0.035m. This checks out independently, not just inherited.
- **Read `box_sdf_collider_setup.py` directly** (it's a project file, not just a transcript quote) — confirmed it's Track 1's *original* box+SDF approach, now superseded by `flood_vehicle.py`/FloodScene.
- **Pulled `kks32_mpm_engine_complete_reference_July7.md`, `CLAUDE.md`, `Slack_Links_Reality_Check_July7.md`, `mpm_render_report.md`** — confirmed the ffmpeg fix, confirmed the API history (`add_sdf_collider` was "planned/empty stub" as of July 7 per the live README at that time, meaning `flood_vehicle.py`'s working mesh-loading capability is new since then — almost certainly Kumar's own push, not something you built).
- **Pulled the drift-threshold citation research fresh** (both the original research doc and its independent follow-up verification doc) — confirms the fix is real, confirms the false "Smith 2019 Eq. 6" attribution is real and needs removing everywhere, not just in one file.
- **Searched the open-source video-to-mesh survey** for a "CoRL 2026 truck mesh" — didn't find one. The `CoRL_2026___Physically_Viable_Planning.pdf` project file is about terrain/flood MPM route-planning on drone-reconstructed splats, not a vehicle mesh asset. I think "CoRL 2026 truck mesh" in STATUS.md is most likely a mislabel for `truck_trimmed.ply`, whose actual provenance is unconfirmed — flagged as its own item below (Bug 14), not assumed resolved.
- **Live-checked Slack** for anything sent to Kumar since last night. Last message is still July 7. Confirms Bug 7 (three drafts, zero sent) is still accurate right now, not stale.
- **Tried to fetch your live GitHub repo directly**, twice, including via the exact URL from your July 7 Slack message. Both attempts were blocked — I don't have live read access to `jcerrell-IS/can-it-ford` from this chat. **Every command below is written for you (or Claude Code over SSH) to run** — I'm giving you a diagnostic sequence, not asserting an outcome I haven't seen.

**One thing this exercise changed my mind on:** the "fix" for the water/vehicle overlap (Bug 3) is *not* simply "move the vehicle." Your July 7 Slack message to Kumar shows the vehicle's z-position was deliberately set to 0.755 (a fixed partial-submersion height) specifically *because* Kumar's own diagram feedback said it should sit half-in the water, not float on top. So the overlap isn't a design bug — a car fording *should* have a wet underbody. The bug is that nothing carves the vehicle's footprint out of the water particle seeding at t=0, so particles get born literally inside the rigid body. That's a seeding-exclusion problem, not a positioning problem — see Bug 3 below for the distinction, because it changes what the real fix looks like.

---

## 1. Full bug inventory — triage table

Severity = how much this blocks a real deliverable. Independent = can be worked without waiting on another bug's outcome.

| ID | Bug | Severity | Independent? | Files |
|---|---|---|---|---|
| **B01** | `CUDA_ERROR_ILLEGAL_ADDRESS` crash, Track 2 (`can_it_ford_L2_mpm.py`) | Critical | **No** — needs B02/B03 tested first | `can_it_ford_L2_mpm.py` |
| **B02** | Vehicle mass ~5x too heavy (rho=604 uncorrected after sedan resize) | High | **Yes** | `can_it_ford_L2_mpm.py` |
| **B03** | Water/vehicle box overlap at t=0 (particles seeded inside rigid body) | High | **Yes** (of B02; test both, combine after) | `can_it_ford_L2_mpm.py` |
| **B04** | `ffmpeg` missing from mpm-engine's uv env, render fails exit 127 | Medium | **Yes** | mpm-engine venv/uv env, `examples/flood_vehicle.py` |
| **B05** | FloodScene vehicle is small-scale (~0.45m), mass/geometry mismatch | High (this is literally Kumar's ask) | **Yes** | `examples/flood_vehicle.py`, `vehicle.py` |
| **B06** | `bridge/` scaffold (PhysGaussian→Genesis, commits `3d3ebbc`/`c97767f`) — unknown if it survived | Medium | **Yes** (read-only check) | repo-wide, `bridge/` |
| **B07** | 3 Kumar-update drafts, 0 sent | Medium | **Soft dependency** — draft now, hold send until B01+B05 results are in | N/A (Slack) |
| **B08** | Local Mac conda env broken for `trimesh` under `conda run` | Low | **Yes** | MacBook shell/conda config, not project code |
| **B09** | `~/.zshrc` has 2-3 redundant `update_log`/`clean_logs` copies | Trivial | **Yes** | MacBook `~/.zshrc` |
| **B10** | `can_it_ford_L2_mpm_ytest.py` purpose unknown (168 lines, new tonight) | Low-but-could-hide-a-real-bug | **Yes** | `can_it_ford_L2_mpm_ytest.py` |
| **B11** | Track 1 vs Track 2 reconciliation decision (3 vehicle representations now exist) | Medium | **No** — decide *after* B01 and B05 have real results | decision only, no file |
| **B12** | Which mesh does `flood_vehicle.py` actually load by default? | Medium | **Yes** (read-only check) | `examples/flood_vehicle.py`, `vehicle.py`, `data/*.ply` |
| **B13** | `DRIFT_THRESHOLD=0.05m` citation — solved in research, not applied | Medium (paper/poster risk) | **Yes** — zero new research needed | `kumar_july9_update/STATUS.md`, poster/paper text |
| **B14** | "CoRL 2026 truck mesh" in STATUS.md likely a mislabel for `truck_trimmed.ply` | Low | **Yes** (read-only check, folds into B12) | `kumar_july9_update/STATUS.md`, `data/truck_trimmed.ply` |
| **B15** | W&B key rotation status unconfirmed; `wandb_backfill.py` untracked | Low | **Yes** | git history, `wandb_backfill.py`, `analysis/wandb_backfill.py` |

**Read this table as two independent problems, not one.** B01/B02/B03/B10 are Track 2 (the interesting crash, GitHub issue #1, not what Kumar literally asked for). B04/B05/B12/B14 are Track 1 (less glamorous, boring env/scale fixes, **is** what Kumar literally asked for). Don't let the crash's novelty pull focus off Track 1 tonight — B05 is higher business-priority than B01 even though B01 is the harder puzzle.

---

## 2. Root cause deep-dive, by cluster

### Cluster A — Track 2 crash (B01, B02, B03, B10)

**B02 root cause, precisely:** `CLAUDE.md` documents `rho=604` was calibrated to hit ~1,450 kg on the *original* `1.0×1.6×1.5m` box. Commit `67915be` resized the box to the real sedan bbox (`4.66×1.79×1.44m` = 12.012 m³) to satisfy the July-10 ask, but the density constant lives on the same line and nobody recalculated it, because the geometry change and the mass-calibration note live in two different files that were never open side by side. Current mass: 604 × 12.012 = **7,255 kg**. Corrected rho: **120.7** for a 1,450 kg target, or **115.7** for a 1,390 kg target.

**Open decision you need to make before fixing this:** Track 2's historical target is 1,450 kg (reverse-engineered from `rho=604` on the old box). Track 1's `vehicle_params.py` uses 1,390 kg, sourced from NHTSA/SAE 1999-01-1336 — a real citation, not a reverse-engineered range. These are ~4% apart. Pick one and use it in both tracks tonight; don't leave two silently different "real sedan mass" numbers in the project. **My recommendation: use 1,390 kg (rho=115.7) everywhere** — it has an actual citation behind it, 1,450 kg was just "close enough to a curb-weight range."

**B03 root cause, precisely:** the vehicle's z-position (0.755) is a fixed constant that doesn't depend on `water_depth`, and nothing in the water-particle-seeding loop excludes the vehicle's occupied volume. At initialization, water particles are very likely instantiated at positions that are literally inside the rigid body. This is a textbook double-occupancy init state, and it fits every symptom from last night: crash is immediate, happens even at velocity=0 (rules out flow-induced numerical blowup), and was untouched by grid_density/dt/substeps/domain-bound changes (none of those touch initialization). Genesis's own issue tracker (`#2071`, `#1291`) documents MPM-rigid coupling failing around exactly this kind of overlap.

**The nuance that matters (see §0):** the overlap itself — car underbody wet during fording — is physically correct. The *bug* is the lack of exclusion logic in the seeding step, not the vehicle's position. Confirm the hypothesis with a temporary reposition (moves the vehicle somewhere clearly wrong, just to test causality), but if confirmed, the real fix is either (a) exclude the vehicle's SDF/box footprint when generating water particle positions, or (b) spawn the vehicle above the water and let it settle for N steps before the timed portion of the sim starts. Don't ship "vehicle permanently moved away from water" as the fix — that's not the scenario you're simulating.

**B10:** nobody has actually opened this file. Until someone diffs it against `can_it_ford_L2_mpm.py`, you don't know if it's a duplicate that will independently reproduce B01 (meaning the fix needs applying twice), a Y-axis variant, or dead scaffolding. Cheap to resolve, assigned below.

**B01 is downstream of B02 and B03**, not a separate thing to debug in parallel — this is why it's marked "not independent." Testing B02 and B03 in isolation (each alone), then combined, is the fastest path to actually closing B01.

### Cluster B — Track 1 / FloodScene (B04, B05, B12, B14)

**B04 root cause:** `kks32/mpm-engine`'s own `pyproject.toml` declares `imageio-ffmpeg` as an optional `render` dependency, but it was never installed in the uv env being used tonight, so `flood_vehicle.py`'s render step calls a `ffmpeg` that isn't on PATH and dies with exit 127. Fix is one command (`uv add imageio-ffmpeg`) — this is the same pattern `render_frames.py` already handles gracefully via a `check_ffmpeg()` fallback; worth confirming `flood_vehicle.py`'s own render call has the same fallback logic, or it'll break again the next time PATH changes.

**B05 root cause:** default FloodScene geometry is a ~0.45m scale model. Last night mixed this small model with (a) an arbitrary default mass (~28.7-29.5kg) — not dynamically meaningful either way — then (b) a `--vehicle-mass 1390` override on the *same small geometry*, which puts a full-scale mass on a toy-scale body. Neither is a coherent physical setup. The script already documents the correct call: `load_vehicle(target_length=4.66)` runs at full scale directly. Nobody tried it.

**B12/B14:** `flood_vehicle.py` is loading *some* real mesh via `plyfile` (confirmed — not a box). Which one is unconfirmed. `truck_trimmed.ply` (47.4MB) already sits in `~/can-it-ford/data/` and is the most likely candidate, but "most likely" isn't "confirmed." This one grep answers whether tonight's "vehicle" has ever actually been a car.

### Cluster C — Repo/citation hygiene (B06, B13)

**B06:** pure git archaeology, zero risk. The two commits from July 10 either survived, got rebased into different SHAs, or never got pushed — `git log --all` vs `git log --oneline -20` distinguishes "not on this branch" from "actually gone."

**B13:** fully solved in research already. `Xia et al. 2014` (DOI 10.1007/s11069-013-0889-2) and `Shah et al. 2018` (DOI 10.1051/matecconf/201820307003) support framing `DRIFT_THRESHOLD=0.05m` as a conservative numerical onset-of-motion detector (~2.5-3.4% of vehicle body width), explicitly *not* a citation to "Smith et al. 2019, Eq. 6" — that equation doesn't exist; a follow-up verification doc independently confirmed the same negative finding. This needs to be scrubbed everywhere it appears, not just in `STATUS.md` — see Pane 0.2 command 5.

### Cluster D — Comms and hygiene (B07, B08, B09, B15)

None of these touch simulation code. B07 is a process gap (drafted three times, sent zero). B08/B09 are your MacBook shell environment, isolated from Vista. B15 is a security-adjacent open item (unrevoked-vs-rotated key ambiguity) that should be resolved before anyone runs `wandb_backfill.py` against real data.

### Decision items (not bugs, don't assign a "fix" — assign a "decide after")

**B11 — track reconciliation.** You now have three vehicle representations: `box_sdf_collider_setup.py`'s box+SDF (Track 1, older, kinematic-only, structurally can't produce yaw/roll/lateral drift), `can_it_ford_L2_mpm.py`'s box proxy (Track 2, full 6-DOF once B01 resolves), and `flood_vehicle.py`'s mesh-based FloodScene (Track 1, current, already 6-DOF). The honest move is to decide this *after* tonight's B01 and B05 results exist, not before — you'll have actual evidence for which one is worth carrying forward instead of guessing.

---

## 3. File ownership map — who may *edit* what tonight

This is the actual fix for the "three panes redid the same work" problem from last night. Running the same script from two panes with different CLI args is fine. **Editing the same file from two panes at the same time is what caused the wasted effort.**

| File | Sole editing owner tonight | Everyone else |
|---|---|---|
| `can_it_ford_L2_mpm.py` | **Pane 0.7 only** | Read-only for everyone else until 0.7 reports done |
| `examples/flood_vehicle.py` / mpm-engine env | **Pane 0.0** (env/render fixes) then **0.1** (sweep, args-only, no source edits) | — |
| `kumar_july9_update/STATUS.md` | **Pane 0.4 only, one consolidated write at the end** | Everyone else writes findings to their own `logs/paneX_result.md` scratch file instead of touching STATUS.md directly — Pane 0.4 pulls from those |
| Kumar Slack message | **Pane 0.3 only**, gated on 0.7 + 0.0/0.1 results (see §5, Pane 0.3) | — |
| `~/.zshrc`, local conda env | **Pane 0.3** (MacBook-local, no Vista collision risk) | — |

---

## 4. Should you open Pane 0.7?

**Yes, still — same conclusion as last night, and it still holds.** It's the one test tonight that could close GitHub issue #1 in under 15 minutes, it's fully independent of the FloodScene sweep running in parallel in Pane 0.0/0.1, and giving it a dedicated pane keeps it from getting buried the way it did last night when Pane 0.0 was doing two unrelated things at once.

Don't open more than one new pane. The bottleneck last night wasn't pane count — it was three panes (0.3/0.4/0.6) independently redoing the same Kumar-draft and argparse-scope work. The file ownership map in §3 is the actual fix for that, not more parallelism.

---

## 5. Panel-by-panel commands

Every command block assumes you're starting from a clean state — run the first "confirm current state" command in each pane before anything else, since files may have drifted since last night and I can't see live Vista/repo state from here.

### Pane 0.7 (NEW) — B01/B02/B03 isolated crash test

```bash
cd /work/11603/jcerrell0629/vista/can-it-ford
grep -n "rho=" can_it_ford_L2_mpm.py
grep -n "pos=(1.0, 0.0, 0.755)" can_it_ford_L2_mpm.py
grep -n "pos=(0.275" can_it_ford_L2_mpm.py
```
Confirms the two values the whole hypothesis rests on haven't changed since last night. If either grep comes back empty, stop and re-locate the current lines before proceeding — don't run the sed below against stale assumptions.

```bash
idev -p gh-dev -N 1 -n 1 -t 00:30:00
module load tacc-apptainer
export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif
cd /work/11603/jcerrell0629/vista/can-it-ford
CUDA_LAUNCH_BLOCKING=1 apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2_mpm.py --depth 0.30 --velocity 0.0 2>&1 | tee logs/mpm_crash_baseline_july13.txt
```
Reproduce the known-failing case fresh, before touching anything, so you have a clean "before" log.

```bash
cp can_it_ford_L2_mpm.py can_it_ford_L2_mpm_test_overlap.py
sed -i 's/pos=(1.0, 0.0, 0.755)/pos=(6.0, 0.0, 0.755)/' can_it_ford_L2_mpm_test_overlap.py
grep -n "pos=(6.0" can_it_ford_L2_mpm_test_overlap.py
CUDA_LAUNCH_BLOCKING=1 apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2_mpm_test_overlap.py --depth 0.30 --velocity 0.0 2>&1 | tee logs/mpm_test_overlap_only_july13.txt
```
**Isolation test A: overlap fix only, mass left broken.** x=6.0 just needs to be clear of the water box's x∈[0.10,0.45] range and inside the domain bounds — check the printed domain extent in the crash log if this value turns out to be out of bounds.

```bash
cp can_it_ford_L2_mpm.py can_it_ford_L2_mpm_test_mass.py
sed -i 's/rho=604/rho=115.7/' can_it_ford_L2_mpm_test_mass.py
python3 -c "print(115.7 * 4.66 * 1.79 * 1.44)"
CUDA_LAUNCH_BLOCKING=1 apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2_mpm_test_mass.py --depth 0.30 --velocity 0.0 2>&1 | tee logs/mpm_test_mass_only_july13.txt
```
**Isolation test B: mass fix only, overlap left in place.** Using 115.7 (the 1,390kg-target rho) per the recommendation in §2 — swap to 120.7 if you decide to standardize on 1,450kg instead, just be consistent with Pane 0.0's number.

```bash
cp can_it_ford_L2_mpm.py can_it_ford_L2_mpm.py.bak_july13
sed -i 's/rho=604/rho=115.7/' can_it_ford_L2_mpm.py
grep -n "rho=" can_it_ford_L2_mpm.py
CUDA_LAUNCH_BLOCKING=1 apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2_mpm.py --depth 0.30 --velocity 0.0 2>&1 | tee logs/mpm_test_combined_july13.txt
CUDA_LAUNCH_BLOCKING=1 apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2_mpm.py --depth 0.60 --velocity 2.0 2>&1 | tee logs/mpm_test_combined_hard_july13.txt
```
**Combined test, on the real file this time** — deliberately only fixes mass, keeps the physically-correct overlap in place. If this kills the crash, mass alone was sufficient and you keep the correct physics. If it still crashes, the overlap needs a real seeding-exclusion fix (§2), not a permanent reposition.

```bash
diff can_it_ford_L2_mpm.py.bak_july13 can_it_ford_L2_mpm.py > logs/pane0.7_diff_july13.txt
cat > logs/pane0.7_result.md << 'EOF'
Baseline (rho=604, overlap present): CRASHED / DID NOT CRASH
Overlap-fix only (pos moved, rho=604): CRASHED / DID NOT CRASH
Mass-fix only (rho=115.7, overlap present): CRASHED / DID NOT CRASH
Combined (rho=115.7, overlap present, physically correct): CRASHED / DID NOT CRASH at depth=0.30 v=0.0 and depth=0.60 v=2.0
EOF
```
Fill in the actual outcomes, don't leave the placeholders. This scratch file is what Pane 0.4 pulls from for the consolidated STATUS.md write — don't edit STATUS.md directly from this pane.

Also do B10 while you're already in this file:
```bash
diff can_it_ford_L2_mpm.py can_it_ford_L2_mpm_ytest.py | head -60
git log --oneline -- can_it_ford_L2_mpm_ytest.py
```
If it's a near-duplicate, note in `logs/pane0.7_result.md` whether the mass/overlap fix needs applying there too.

---

### Pane 0.0 — B04, B05, B12: Track 1 environment fixes + full-scale reference run (Kumar's literal ask)

```bash
cd /work/11603/jcerrell0629/vista/mpm-engine
uv run python3 -c "from warpmpm.vehicle import load_vehicle; help(load_vehicle)"
grep -n "target_length\|load_gaussians_ply\|default" examples/flood_vehicle.py 2>/dev/null
```
Confirm the actual `load_vehicle` signature and whether `target_length` is exposed as a CLI flag or only as a Python parameter — don't guess this in step 3.

```bash
uv add imageio-ffmpeg
uv run python3 -c "import shutil, imageio_ffmpeg; print('system ffmpeg:', shutil.which('ffmpeg')); print('imageio-ffmpeg exe:', imageio_ffmpeg.get_ffmpeg_exe())"
```
B04 fix. Both prints should return a real path; if both are `None`, the install itself failed.

```bash
grep -n "\.ply\|load_gaussians_ply" examples/flood_vehicle.py src/warpmpm/vehicle.py 2>/dev/null
ls -la /work/11603/jcerrell0629/vista/can-it-ford/data/*.ply
```
B12/B14. This tells you whether `truck_trimmed.ply` is actually what's loading, or something else.

```bash
idev -p gh-dev -N 1 -n 1 -t 00:45:00
cd /work/11603/jcerrell0629/vista/mpm-engine
uv run python3 examples/flood_vehicle.py --depth 0.30 --velocity 1.5 --target-length 4.66 --vehicle-mass 1390 2>&1 | tee logs/floodscene_fullscale_ref_july13.txt
```
The full-scale reference run. If `--target-length` isn't a real CLI flag (step 1 will show this), edit the script's `load_vehicle(...)` call directly instead of passing a flag that silently gets ignored — this is exactly the argparse failure mode from last night, don't repeat it.

```bash
uv run python3 examples/flood_vehicle.py --render-only --input <output_npz_from_step_4> --output floodscene_fullscale_d0p3_v1p5.mp4 2>&1 | tee logs/floodscene_render_july13.txt
```
Match the actual render entrypoint flags shown by `help()` in step 1 rather than assuming `--render-only`/`--input`/`--output` exist verbatim.

```bash
cat > logs/pane0.0_result.md << 'EOF'
ffmpeg fix: WORKED / FAILED
target_length flag exposed: YES / NO (edited load_vehicle() call directly instead)
Default mesh confirmed: truck_trimmed.ply / other: ___
Full-scale reference run (0.30/1.5, 4.66m, 1390kg): displacement=___m, yaw=___, roll=___
Render: SUCCEEDED / FAILED
EOF
```

---

### Pane 0.1 — Full-scale depth sweep (args-only, no source edits — safe to run parallel to 0.0)

```bash
cd /work/11603/jcerrell0629/vista/mpm-engine
cat logs/pane0.0_result.md 2>/dev/null
```
Wait for Pane 0.0 to confirm the ffmpeg fix and full-scale run work before starting the sweep — no point sweeping six depths on a broken render path.

```bash
for d in 0.15 0.22 0.30 0.38 0.45 0.60; do
  uv run python3 examples/flood_vehicle.py --depth $d --velocity 1.5 --target-length 4.66 --vehicle-mass 1390 2>&1 | tee logs/floodscene_sweep_d${d}_july13.txt
done
```
Same mass/scale choice for every depth this time — last night's sweep mixed model-scale-default-mass and model-scale-28.7kg runs, which invalidates any "crossover depth" claim drawn from it.

```bash
grep -h "yaw\|roll\|displacement" logs/floodscene_sweep_d*_july13.txt
```
Quick eyeball of the crossover pattern before building the full plot.

```bash
mkdir -p /work/11603/jcerrell0629/vista/can-it-ford/data/floodscene_fullscale_july13
cp *.npz *.csv /work/11603/jcerrell0629/vista/can-it-ford/data/floodscene_fullscale_july13/
cd /work/11603/jcerrell0629/vista/can-it-ford
git pull --rebase
git add data/floodscene_fullscale_july13/
git commit -m "FloodScene full-scale sweep (target_length=4.66, mass=1390kg), depth 0.15-0.60 at v=1.5"
git push
```
Pull the outputs into the repo and commit before the compute node's local files disappear at job end.

```bash
cat > data/floodscene_fullscale_july13/README.md << 'EOF'
All runs: target_length=4.66m, vehicle_mass=1390kg, velocity=1.5 m/s.
Depths swept: 0.15, 0.22, 0.30, 0.38, 0.45, 0.60.
This supersedes the mixed-mass sweep from July 12 — do not average across the two.
EOF
```
This one-file README is what makes the sweep reproducible from git history instead of only from your memory of what you ran.

---

### Pane 0.2 — B06, B13: bridge scaffold check + drift citation fix + README audit

```bash
cd /work/11603/jcerrell0629/vista/can-it-ford
git log --all --oneline | grep -i bridge
git log --all --oneline | grep -E "3d3ebbc|c97767f"
ls -la bridge/ 2>&1
```
Read-only, zero risk. Establishes whether the July 10 bridge scaffold survived.

```bash
git branch -a --contains 3d3ebbc 2>&1
git branch -a --contains c97767f 2>&1
```
If the commits show up here but not in `git log --oneline -20` on main, they're just unmerged, not lost.

```bash
grep -n "DRIFT_THRESHOLD\|Smith.*2019\|Eq\. 6\|not cited" kumar_july9_update/STATUS.md
```
Locate every place the false citation or the "not cited" placeholder appears.

Hand-edit STATUS.md's citation entry to read (use this exact language, it's the already-verified replacement):
> "DRIFT_THRESHOLD = 0.05 m is a conservative numerical onset-of-motion detection tolerance internal to the coupled MPM solver, used to classify a vehicle as having begun to move once its lateral displacement exceeds this value. It is not a peer-reviewed physical instability criterion. The underlying physical concept follows Xia et al. (2014, DOI 10.1007/s11069-013-0889-2) and Shah et al. (2018, DOI 10.1051/matecconf/201820307003), corresponding to roughly 2.5-3.4% of representative vehicle body width."

Remove any line attributing the value to "Smith et al. 2019, Eq. 6" — that equation does not exist in that paper.

```bash
grep -rn "Smith.*2019.*Eq\|Eq\. 6\|Eq 6" --include="*.md" --include="*.py" .
```
Confirm the false citation isn't hiding somewhere other than STATUS.md — poster text, `PROVISIONAL_STATUS.md`, paper draft.

```bash
grep -n -i "MPM\|SPH" README.md
grep -n "gs.materials" can_it_ford_L2.py can_it_ford_L2_mpm.py 2>&1
cat > logs/pane0.2_result.md << 'EOF'
bridge/ commits: FOUND on main / FOUND unmerged / NOT FOUND
DRIFT_THRESHOLD citation fix: APPLIED to STATUS.md, N other places
README MPM/SPH audit: clean / found stale claim at ___
EOF
```

---

### Pane 0.3 — B07, B08, B09, B15: Kumar update (gated), local env, W&B check

```bash
diff can_it_ford_L2_mpm.py.bak_july13 can_it_ford_L2_mpm.py 2>/dev/null
cat /work/11603/jcerrell0629/vista/can-it-ford/logs/pane0.7_result.md 2>/dev/null
cat /work/11603/jcerrell0629/vista/mpm-engine/logs/pane0.0_result.md 2>/dev/null
```
Draft the Kumar message now, but **hold sending it until both of these come back non-empty** — that's the actual bug from last night (three retracted-in-spirit drafts), and it's exactly what happens if you send before the crash-test and full-scale-run results exist.

```bash
git log -p --all -S "wandb" -- '*.py' | grep -i "api_key\|WANDB_API_KEY" | head -5
echo ${WANDB_API_KEY:0:8}
```
B15: confirm the exposed key from commit `50eff29` is actually revoked, not just "the code no longer references it."

```bash
conda env list
which python3
conda run -n can-it-ford which python3
conda run -n can-it-ford python3 -c "import trimesh; print(trimesh.__file__)"
```
B08: this sequence will show whether `conda run` is resolving to a different interpreter than the one that has trimesh installed.

```bash
grep -n "^update_log\|^clean_logs" ~/.zshrc
```
B09: count how many redundant copies actually exist before consolidating.

```bash
scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/data/floodscene_sweep_d0p22*.csv ~/can-it-ford/data/ 2>&1
scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/data/floodscene_sweep_d0p38*.csv ~/can-it-ford/data/ 2>&1
scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/data/floodscene_sweep_d0p60*.csv ~/can-it-ford/data/ 2>&1
```
Any old-sweep CSVs still stranded on Vista from *last* night (before this sweep gets superseded by Pane 0.1's clean rerun) — pull them only if you want the mixed-mass data preserved for comparison, otherwise skip and let Pane 0.1's clean sweep be the only record.

```bash
cat > logs/pane0.3_result.md << 'EOF'
Kumar message: SENT / STILL HOLDING (waiting on: ___)
W&B key 50eff29: CONFIRMED REVOKED / STILL UNCONFIRMED
conda trimesh: FIXED / diagnosis: ___
zshrc redundant functions: N copies found, consolidated Y/N
EOF
```

---

### Pane 0.4 — Single owner of `STATUS.md`, B12/B14 disambiguation, B11 decision

```bash
grep -n -i "al-qadami\|Al Qadami\|Engineering Letters" "Smith__Modra_and_Felder__2019__Vehicle_Flood_Stability__Findings_and_Debunking_the_0_05_m_Drift_Threshold_Attribution.md"
```
Confirms this citation is already sitting in a local project file, not something that needs a new search.

```bash
grep -n -i "truck\|mesh" CoRL_2026*.pdf 2>/dev/null
grep -rn "truck_trimmed" . --include="*.py" --include="*.md" 2>/dev/null
```
B14: this should confirm (or disconfirm) that "CoRL 2026 truck mesh" was a mislabel for `truck_trimmed.ply`.

```bash
cat /work/11603/jcerrell0629/vista/can-it-ford/logs/pane0.7_result.md 2>/dev/null
cat /work/11603/jcerrell0629/vista/mpm-engine/logs/pane0.0_result.md 2>/dev/null
cat /work/11603/jcerrell0629/vista/can-it-ford/logs/pane0.2_result.md 2>/dev/null
cat /work/11603/jcerrell0629/vista/can-it-ford/logs/pane0.5_result.md 2>/dev/null
```
Wait for these before doing anything below — this pane is the single STATUS.md writer, and it should write once, consolidated, not incrementally.

```bash
cd /work/11603/jcerrell0629/vista/can-it-ford
git pull --rebase
```
Hand-edit `kumar_july9_update/STATUS.md`'s checklist using the four scratch files above: mark B01/B02/B03 resolved-or-not, B04/B05 done, B06/B12/B14 confirmed, B13 applied.

```bash
git add kumar_july9_update/STATUS.md
git commit -m "STATUS.md: consolidate July 13 findings across all panes"
git push
```

Write one short paragraph on B11 (track reconciliation) directly into STATUS.md's Open Questions, now that you have real evidence from both tracks — this is a decision, not a code change, so it belongs in prose, not a diff.

---

### Pane 0.5 — Verification/QA: confirm nothing regressed, resolve B10, feed Pane 0.4

```bash
cd /work/11603/jcerrell0629/vista/can-it-ford
grep -c "startswith" simulation/*.py can_it_ford_L2*.py 2>/dev/null
```
Re-confirm the argparse fix's scope is still exactly the three files it was fixed in, and L0/L1 remain untouched, after tonight's edits.

```bash
diff wandb_backfill.py analysis/wandb_backfill.py 2>&1
```
Confirms which `wandb_backfill.py` is current before Pane 0.3 runs one of them.

```bash
git log --oneline --since="2026-07-09" > logs/pane0.5_commit_summary_july13.txt
cat logs/pane0.5_commit_summary_july13.txt
```

```bash
git status > logs/pane0.5_result.md
git log -10 >> logs/pane0.5_result.md
git diff HEAD~5 --stat >> logs/pane0.5_result.md
```
This is the single clean summary block Pane 0.4 and the Kumar update both quote from — don't make either of them regenerate this independently.

```bash
python3 -c "
import ast
for f in ['can_it_ford_L2_mpm.py', 'can_it_ford_L2_mpm_ytest.py']:
    with open(f) as fh:
        tree = ast.parse(fh.read())
    print(f, [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
"
```
Function-level diff between the two files, a faster way to see if `_ytest.py` is a real variant or a near-duplicate than reading 168 lines top to bottom.

---

### Pane 0.6 — Output pulling, visualization QA, SESSION_STATE.md / PROVISIONAL_STATUS.md maintenance

```bash
scp -r jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/data/floodscene_fullscale_july13 ~/can-it-ford/data/
```
Wait until Pane 0.1 marks the sweep done before pulling — no point pulling partial data twice.

```bash
open ~/can-it-ford/data/floodscene_fullscale_july13/*.mp4
```
Manually check against Kumar's documented conventions: viridis on displacement/velocity, particles visible not a smooth surface, fixed camera + fixed colorbar across the set, two-camera (top-down + 3/4 oblique) convention. Flag for re-render if it doesn't match, don't ship it silently wrong.

```bash
cd /work/11603/jcerrell0629/vista/can-it-ford
cat SESSION_STATE.md
```
Confirm it still exists and reflects today, not just July 10 — update it if not.

```bash
grep -n -A5 "CORRECTION" PROVISIONAL_STATUS.md
```
Locate the existing correction banner so tonight's crash-test outcome (whatever it is) gets appended in the same format, keeping the "verify before trusting" discipline that caused the banner to exist in the first place.

```bash
cat /work/11603/jcerrell0629/vista/can-it-ford/logs/pane0.7_result.md 2>/dev/null
```
Once this is non-empty, append the definitive root-cause entry to `PROVISIONAL_STATUS.md` and `logs/`.

---

## 6. Sequencing — what actually gates what

```
Pane 0.7 (crash test)  ──┐
Pane 0.0 (full-scale)  ──┼──→ Pane 0.3 (send Kumar update)
                          │
Pane 0.7 + 0.0 + 0.2     ──→ Pane 0.4 (single STATUS.md write) ──→ Pane 0.6 (PROVISIONAL_STATUS.md correction entry)
                          │
Pane 0.0 (ffmpeg+full-scale confirmed) ──→ Pane 0.1 (sweep) ──→ Pane 0.6 (pull + visual QA)
```

Everything else (0.2's bridge check and citation fix, 0.5's verification, 0.3's B08/B09/B15 side items) is fully independent and can start immediately, in parallel, with no gating.

---

## 7. How to actually expedite this

- **I can't run any of the above from this chat** — no SSH, no live Vista/repo access. If you want active help executing rather than a pre-written command list, that's Claude Code on your MacBook over SSH, per your own established workflow — paste this file in as context there and it can watch output and adapt in real time, which I can't do here.
- **The single biggest speed lever tonight isn't more parallelism, it's the file-ownership map in §3.** Three panes rewriting the same Kumar draft last night wasn't a tooling problem, it was a coordination problem — this plan fixes it by giving every shared file exactly one writer and funneling everyone else through scratch files.
- **Pane 0.7's result is the most valuable single output tonight** — it's the one test that could close a real GitHub issue in 15 minutes. If you only have bandwidth to actively babysit one pane, make it that one.
- **Don't let Pane 0.7's interesting puzzle pull time from Pane 0.0/0.1** — the full-scale FloodScene run is what Kumar actually asked for by name; the crash fix is valuable but secondary to that.

---

## STATUS UPDATE, July 13, later pass (append, do not rewrite the original above)

Bug B03 (water/vehicle overlap): RESOLVED AS A HYPOTHESIS, not as a fix, tested
directly and ruled out as the crash cause. Do not run Pane 0.7's overlap
isolation test as originally written, it's already been answered by a
different, equivalent test.

Bug B02 (mass): target resolved to 1390kg, rho=115.7. Fix-applied status to the
live file still unconfirmed.

New live suspect for the crash, not present anywhere in the original triage
above: the domain-widening commit itself (lower_bound=(-2.5,-1.0,-0.1),
upper_bound=(4.5,1.0,2.5)). This should become the new B01 test target,
replacing the overlap/mass isolation matrix originally specified for Pane 0.7.

Two new bugs found since this document was written: viability_audit.py's glob
mismatch (see above), and the confirmed root cause of Bug B08 (conda/trimesh
on Mac, `conda run` resolves to system Python, not the environment's
interpreter, the actual fix of getting `conda run` to activate correctly has
not been confirmed applied).

Current canonical status for the crash, all fixes, the full KNOWN DEAD ENDS
list, and the prioritized STILL OPEN list now lives in CLAUDE.md (Vista:
/work/11603/jcerrell0629/vista/CLAUDE.md, Mac: ~/can-it-ford/CLAUDE.md). This
document remains useful as historical record of the original triage
reasoning, but CLAUDE.md is the file Claude Code actually reads automatically,
this one is not. Do not rely on this file alone for current status going
forward.
