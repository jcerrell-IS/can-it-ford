# Session State

Read this before doing anything else, on any machine. Update the relevant section before you stop working, even mid-task. This file exists so a fresh terminal or a fresh chat session can pick up exactly where the last one left off, instead of re-deriving it from memory.

Last updated: July 10, 2026, 06:44 UTC (Claude chat, verified live against GitHub + Slack, not from memory).

---

## MacBook (local)

**Last command run:** n/a, seeded from chat verification, not a real terminal session.
**Current status:** Not the blocker right now. Everything blocking is on Vista.
**Next action:** none queued.

## Vista (Genesis MPM, GH200)

**Last command run:** `python3 simulation/can_it_ford_L2_mpm.py 0.30 1.5` inside the Apptainer container, July 9 evening (per Slack + kumar_july9_update/STATUS.md).
**Current status:** Crashes at step 0, `CUDA_ERROR_ILLEGAL_ADDRESS`, first coupled substep. Zero output (no video, no npz, no CSV row). This is the single highest-priority open blocker in the whole project.
**Next action:** rerun with `CUDA_LAUNCH_BLOCKING=1` and save the FULL traceback to `logs/mpm_crash_july10.txt` before doing anything else to this script. No traceback has ever been saved for this crash (confirmed, STATUS.md). Two just-fixed items already live: `run_tag` string now correctly says `grid64_cf0p55` instead of the stale `grid128_cf0p4` label; `PROVISIONAL_STATUS.md`'s session-6 "clean MPM run" claim is now marked unconfirmed at the top of that file. Do not re-trust that 0.0038m number without a fresh, logged run.

## LS6 (gsplat, A100)

**Last command run:** unknown, not confirmed this session.
**Current status:** Piece 1 of the rebuild (shoot + reconstruct a real water-adjacent scene) has not started. `box_sdf_collider_setup.py` (the kks32/mpm-engine track) is further along than direct Genesis MPM: real sedan-scale vehicle box wired in, but has an unresolved water-drift bug during gravity settling, before the vehicle is even added.
**Next action:** confirm current state directly (`ls`, `git status`) before assuming anything here, do not trust old chat summaries.

## Rotating / fourth pane

**Current status:** undefined. Ask what this pane is actually used for day to day (a second Vista render pane, a live log tail, or a git/GitHub pane) before building a fixed tmux layout around it.
**Next action:** decide this once, then it stops being a question.

---

## Cross-cutting, not tied to one machine

- **W&B API key:** confirmed still present in `wandb_backfill.py`'s git history (commit `50eff29`), per `PROJECT_FILE_MAP.md`. Removing it from the current file does not remove it from history. Rotate on wandb.ai today regardless of current-file state.
- **Poster board size:** not confirmed anywhere (Slack, calendar, or files, all checked). Ask Rosie or Luke directly, do not guess or default to 42x56/48x36/42x60.
- **Poster session date:** master doc says July 30, one external note claims July 29. Neither independently confirmed via calendar in this session. Confirm directly before building anything date-specific.
- **10 AM meeting:** Kumar, Josie, Josue Ortiz confirmed via Slack for "tomorrow" relative to July 9, i.e. today, July 10.
