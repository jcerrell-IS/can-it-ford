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
**Current status:** `grid_density` bumped 64->128 on GitHub (per Genesis issue #600, car-scale tunneling risk), not yet pulled or tested on Vista. Still crashes at step 0 as of the last confirmed run (July 9, grid_density=64). Whether 128 fixes it is unconfirmed.
**Next action:** `git pull` inside `can-it-ford` (now that the path is correct), then rerun with `CUDA_LAUNCH_BLOCKING=1`, tee the full output to `logs/mpm_crash_july10.txt`. This has never been done, no traceback has ever been captured for this crash.

## Gsplat / COLMAP (real drain footage, separate Claude Code session, MacBook)

**Last command run (as best reconstructed from a garbled terminal paste):** SD card mounted at `/Volumes/Untitled/DCIM/891_0709/`, 5 MP4s found, 4 usable (2954 is 1.5s, discarded). Classified as 2 drains: **Drain A** = 2955/2957/2959 (limestone wall, metal railing, P18 sign; best orbit = 2957), **Drain B** = 2956 (plaza, red Adirondack chairs). Files renamed to `drainA.MP4`/`drainB.MP4`, frames extracted via `ffmpeg -vf fps=2` for both (Drain B expected ~354 frames from its 177s duration). Session then moved to COLMAP: was instructed to SSH to `ls6.tacc.utexas.edu`, but the terminal prompt actually shown was `(vista) c609-122[gh]`, meaning it ended up on a Vista compute node, not LS6. `echo $SCRATCH` confirmed `/scratch/11603/jcerrell0629`, `mkdir -p $SCRATCH/datasets` succeeded. One command failed on a stray leading `- ` character (`-bash: -: command not found`), harmless typo, not yet re-run clean.
**Current status:** THIS IS REAL PROGRESS ON PIECE 1 (real gsplat scene) for the first time in the project. Not yet run: `scp` the extracted frames to `$SCRATCH/datasets/drainA` (and B), then COLMAP `feature_extractor` + `exhaustive_matcher` + `mapper` (CPU-only mode, `--SiftExtraction.use_gpu 0 --SiftMatching.use_gpu 0`, per the session's own plan) to get camera poses. Health check to watch for: the mapper's `Registered images: X / Y` line, expect most of the ~354+ frames to register or the reconstruction is unusable (motion blur suspected as the failure mode if it's low).
**Next action:** re-run the `$SCRATCH` setup cleanly (drop the stray `- `), scp Drain A's frames over, run COLMAP on Drain A first, report the registered-image count before touching Drain B or spending a gsplat training run on it. Also unresolved: confirm whether staying on Vista (vs the originally planned LS6) is fine for this, or whether gsplat training specifically needs LS6's tested environment.

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
