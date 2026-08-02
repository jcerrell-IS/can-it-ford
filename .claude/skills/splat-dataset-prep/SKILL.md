---
name: splat-dataset-prep
description: Use this skill whenever Josie works on Tutorial 2 or any custom Gaussian Splatting dataset — turning her OWN video into a gsplat-trainable dataset. Trigger on "Tutorial 2", "my own video", "shoot a video for splatting", "custom dataset", "ffmpeg", "extract frames", "COLMAP", "camera poses", "my splat won't train", "dataset structure", "upload my dataset to LS6", "images folder", "sparse folder", or any mention of filming a scene, frame extraction, structure-from-motion, or preparing data for simple_trainer.py. Companion to geoelements-tech-reference (concepts) — this skill is the hands-on WORKFLOW for video → frames → COLMAP → gsplat. It carries shooting rules, exact commands, the expected folder layout, quality gates, and failure triage.
---

# Splat Dataset Prep (video → trainable gsplat dataset)

## Purpose
Walk Josie from "I filmed a thing on my iPhone" to "training is running on LS6 with my data." One stage per session. She runs commands; Claude diagnoses output. Never claim to have run anything.

## The pipeline (4 stages)
1. **SHOOT** — capture a good video (iPhone)
2. **FRAMES** — ffmpeg extracts still images (MacBook)
3. **POSES** — COLMAP recovers camera positions (MacBook or LS6 — see note)
4. **TRAIN** — upload to $SCRATCH, run simple_trainer.py (LS6)

Define once: **COLMAP** = structure-from-motion tool; it looks at overlapping photos and figures out where the camera was for each shot. gsplat needs those camera poses to know where to place Gaussians.

## STAGE 1 — SHOOT (iPhone)
Rules that make or break the splat:
- **Orbit the subject** slowly: full 360° if possible, 1–3 minutes, landscape.
- **Slow and steady.** Motion blur is the #1 killer. Walk like you're carrying soup.
- **High overlap:** each part of the scene should appear in many frames from different angles.
- **Lock exposure/focus** (press-and-hold on iPhone → AE/AF LOCK). Auto-exposure shifts confuse COLMAP.
- **Avoid:** moving objects (people, pets, wind-blown plants), reflective/transparent surfaces, blank textureless walls, changing light.
- Good first subjects: a statue, a rock garden, a parked bike, a textured courtyard corner.

Quality gate: scrub the video — if any 2-second stretch is blurry, reshoot that arc.

## STAGE 2 — FRAMES (MacBook Terminal)
```
mkdir -p ~/Documents/Claude/reu/datasets/<scene_name>/images
ffmpeg -i ~/Downloads/<video>.MOV -vf "fps=2" -qscale:v 2 ~/Documents/Claude/reu/datasets/<scene_name>/images/frame_%04d.jpg
```
- `fps=2` = 2 frames per second. Target **100–300 images total**; adjust fps to hit that (90s video × 2fps = 180 ✓).
- `-qscale:v 2` = high JPEG quality.
- If ffmpeg isn't installed: `brew install ffmpeg` (if no Homebrew, flag it — that's a 5-min separate step).

Quality gate: `ls ~/Documents/Claude/reu/datasets/<scene_name>/images | wc -l` → 100–300. Open a few frames; all sharp.

## STAGE 3 — POSES (COLMAP)
**(unconfirmed) Where the lab runs COLMAP:** ask Cristian/Luke whether they run it locally or on LS6 (`module spider colmap` on LS6 to check availability). Until confirmed, default = local Mac (`brew install colmap`), CPU is fine, just slow (minutes–hours).

Local GUI-free run:
```
cd ~/Documents/Claude/reu/datasets/<scene_name>
colmap automatic_reconstructor --workspace_path . --image_path ./images --camera_model SIMPLE_RADIAL --sparse 1 --dense 0
```
Expected output structure gsplat wants (MipNeRF-360 layout):
```
<scene_name>/
  images/            ← your jpgs
  sparse/0/          ← cameras.bin, images.bin, points3D.bin
```
If automatic_reconstructor puts sparse output elsewhere (e.g. `sparse/` without `0/`), move/rename to match.

Quality gate: COLMAP should register **>90% of images**. If it registers few: too much blur, too little overlap, or textureless scene → reshoot beats debugging.

## STAGE 4 — TRAIN (LS6)
Upload (MacBook):
```
scp -r ~/Documents/Claude/reu/datasets/<scene_name> jcerrell0629@ls6.tacc.utexas.edu:/scratch/<her_scratch_path>/datasets/
```
(First `ssh` in and `echo $SCRATCH` to get the literal path — scp can't expand remote $SCRATCH.)

Then mirror the verified Tutorial 1 runbook (see CLAUDE.md / geoelements-tech-reference), swapping:
```
--data_dir $SCRATCH/datasets/<scene_name>/ --data_factor 1
```
`--data_factor 1` because there are no downsampled images_2/images_4 folders — only full-res `images/`.

## FAILURE TRIAGE (most likely first)
1. **COLMAP registers few images** → capture problem. Reshoot; don't tune COLMAP flags.
2. **gsplat: "images_4 not found" or similar** → missing `--data_factor 1`.
3. **Training loss flat / splat looks like fog** → bad poses upstream; recheck COLMAP registration count.
4. **scp fails** → remote path typo; verify with `ssh` + `ls` first.
5. Stuck 15 min → Cristian.

## HARD RULES
- One stage per session. Pass the quality gate before advancing.
- She runs; Claude diagnoses. Command + what it does + success signal, every time.
- Reshooting is cheap; debugging bad capture is the rathole. Say so.

## REFRESH — living workflow
Trigger: "refresh splat-dataset-prep" or new lab facts arrive. Update in place, echo a 2-line diff.
- [ ] Confirm where the lab runs COLMAP (local vs LS6 module) — replace the (unconfirmed) block.
- [ ] Record her actual first dataset: scene, frame count, fps used, COLMAP registration %, LS6 path.
- [ ] Fold in any lab-specific preprocessing script Hassan/Cheng-Hsi/Luke provides (it supersedes the generic flow above).
- [ ] Capture real training results (steps, PSNR, output paths) as ground truth for next time.
