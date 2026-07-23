---
name: bug-triage-protocol
description: Use whenever Josie pastes a bug list, crash traceback, error log, tmux pane output, or session log from Can It Ford debugging and wants a full triage: root cause, independence ranking, file ownership across parallel panes, and exact runnable commands. Trigger on "triage", "bug list", "panel plan", "pane", "rabbit hole", "what should I run", multi-terminal debugging, CUDA crashes, argparse bugs, mass or density bugs, or any request matching the CONTEXT/STANCE/SCOPE/DELIVERABLE skeleton below. Also trigger proactively before executing multi-step fixes across Vista, LS6, or MacBook, to catch known failure classes (silent success, split-attention bugs, path drift, stale RESOLVED notes, Track 1 vs Track 2 environment conflation, git rebase ambiguity) before they cause wasted work.
---

# Bug Triage Protocol

Built July 13, 2026, out of a real multi-pane debugging session on Can It Ford. This is not a bare template, it has that night's actual failure classes baked in, because the same shapes of mistake are the ones most likely to recur.

## Where this runs

Claude Code only. This protocol assumes live SSH into Vista or LS6, live tmux panes, live git, live file edits. Chat Claude can plan with this skill and can search project knowledge and past sessions, but cannot SSH, cannot see tmux, cannot run the commands it recommends. Skills do not sync between Claude.ai chat and Claude Code, this file has to be installed in both places if both should have it. Chat Claude can still read this file if it is in project knowledge and reason from it, but should say so explicitly rather than pretending it ran anything.

## The reusable request skeleton

Use this shape to invoke the protocol on any future bug dump:

```
CONTEXT: [paste the raw material, log, bug list, error output]
I want you to:
1. [triage/rank operation]
2. [dependency/independence operation]
3. [root cause + file mapping operation]
4. [assignment/plan operation]
5. [exact commands/deliverable operation, with a minimum count and format]
STANCE: Don't trust [prior doc/my framing/your own memory] as complete.
Verify against [project files / live sources / connector] before answering.
SCOPE: Use [project knowledge search, Slack, web, etc], check more than one source.
DELIVERABLE: [file / chat / specific format], [length or count constraint]
```

## Step-by-step protocol

1. **Read the raw material cold, in full, before doing anything else.** Not a summary of it, not a memory of what it probably says. If it's a log, read the whole log. If it's a bug list, read every entry once before ranking any of them.
2. **Cluster by severity times independence, not severity alone.** A high-severity bug that depends on another bug's outcome should not jump the queue ahead of an independent lower-severity one, since the dependent one cannot actually be worked yet.
3. **For every bug: root cause, exact file, minimum reproduction.** No bug gets a fix assigned until it has a named file and a way to confirm it's actually present, not just plausible.
4. **File ownership map, before assigning any pane.** One file, one owner, for the duration of the session. Running the same script with different CLI args from two panes is fine. Two panes editing the same file at the same time is the exact thing that wasted effort on July 12.
5. **Sequence by dependency, not by discovery order.** Independent bugs run in parallel across panes. Dependent bugs wait, explicitly, with the dependency named.
6. **Deliverable: numbered commands per pane, minimum count specified, copy-paste ready.** Not vague suggestions. Each command should state what success looks like and the most likely failure mode before moving to the next one.

## Known failure class list

Recognize these on sight, they are not one-off mistakes, they are shapes that recur.

- **Silent success.** Wrong output that looks like right output. The argparse bug printed plausible-looking values while a positional-arg mismatch meant the real CLI flags never reached the script. Nothing crashed, nothing looked wrong, days of runs were quietly using the wrong inputs.
- **Split-attention bugs.** A fix touches two files, only one gets updated. The vehicle mass bug: the box was resized in one commit for geometry reasons, the density recalculation that should have gone with it lived in a different file (`CLAUDE.md`'s calibration note) that nobody had open at the same time.
- **Manual-arithmetic-required bugs.** Geometry or overlap bugs that only surface if someone assembles coordinates from multiple sources by hand. The water/vehicle overlap bug needed the water-box tuple from one grep and the vehicle-box tuple from a different grep, at different times, compared by hand across three axes. Nothing flags this automatically.
- **Path and storage-tier drift.** `~/can-it-ford` versus the canonical `/work/11603/jcerrell0629/vista/can-it-ford`. Scratch versus work tier. A script assuming flat-layout paths after the repo moved into a `simulation/` subdirectory.
- **Environment conflation.** Track 1 (`kks32/mpm-engine`, the `mpmenv` venv, never through Apptainer) and Track 2 (Genesis, always through Apptainer, never `mpmenv`) are different runtimes. Running one script under the other track's environment produces confusing errors that look like a code bug instead of an environment mismatch.
- **Stale RESOLVED notes.** A doc states a bug is fixed or a layout is settled, and reality has since moved past it. `CLAUDE.md` carried a "RESOLVED July 7: flat layout, no simulation/ subdirectory" note well after the repo had grown a real `simulation/` subdirectory. A resolved note is a claim, not a fact, until re-checked live.
- **Git rebase `--ours` ambiguity.** In a rebase conflict, `--ours` silently keeps the side you don't expect depending on which branch is rebasing onto which. At least one real fix was lost this way and had to be re-applied.
- **Multi-line SSH paste freezing.** `python3 -c "..."` with multi-line content hangs the SSH session. Use a heredoc (`cat > /tmp/script.py << 'PYEOF'`) instead, every time, not just when the freeze has already happened once.
- **Mass-scale mismatch across a sweep.** Mixing a model-scale default mass and a full-scale override mass across different runs of the same sweep invalidates the whole sweep, even if each individual run looks clean. The FloodScene depth sweep that found a "crossover" did this, the crossover claim had to be retracted and rerun with one consistent mass.
- **Multi-session global-file regression, invisible until you diff two point-in-time checks.** A file outside any repo, a global skill, a global CLAUDE.md, gets confirmed correct by one session's md5 or byte count, then a different concurrent session silently overwrites it with an older or different version. Nothing errors, nothing looks wrong in isolation, the file just quietly stops being the one that was verified. The only way to catch this is comparing the same file's fingerprint across two different points in time, not trusting a single snapshot. This happened to this exact skill file the same night it was written.
- **A stored reference value can itself be the wrong thing to trust.** A validation check passing only proves live state matches whatever constant is hardcoded as the expected value, not that the constant is correct. A one-character typo in an expected md5, or a doc's own byte-count note written against an older draft and never updated, both look like solid ground truth until someone asks where the reference value came from.

## Rabbit-hole checklist

Run this before going deeper on any single bug, not after.

- Have I read the raw log or traceback myself, cold, top to bottom, or am I pattern-matching off a summary someone else wrote?
- Is this bug actually independent of the others, or am I fixing it before its real dependency is resolved?
- Am I about to edit a file another pane owns tonight?
- Have I verified this specific claim against live output, grep, cat, an actual rerun, or am I trusting a doc, a memory, or a prior session's summary?
- Have I spent more than 15 minutes on one bug with no new information? That is the stop signal, not a reason to push harder alone, ping Cristian.
- Before calling anything fixed: did I rerun it and watch the fix actually work, not just read the diff and assume?
- When a check passes or fails against a hardcoded reference value, have I confirmed the reference itself is correct and current, or only that live state matches it? A passing check against a stale or mistyped reference is not a real pass.

## Project files this protocol should check every time

Read these fresh at the start of a triage session, do not assume memory of their contents is current:

- `CLAUDE.md` (source-of-truth framing, check every RESOLVED or STATUS line against live reality before trusting it)
- `SESSION_STATE.md` (cross-terminal handoff file, if present)
- The most recent bug-triage-and-panel-execution-plan markdown in the repo (there may be more than one dated version, use the newest by filename date)
- `simulation/can_it_ford_L2_mpm.py` and `simulation/box_sdf_collider_setup.py` or `examples/flood_vehicle.py` (whichever track is live tonight)
- `vehicle_params.py`
- `kks32_mpm_engine_complete_reference_July7.md` (or its current-dated successor if one exists)

## July 13, 2026 reference case

A worked example, kept for pattern-matching, not for blind reuse. Bug numbers and statuses below are a point-in-time snapshot, re-verify current status live before assuming any of these are still open or still fixed.

**Bugs found, by cluster:**

- **Cluster A, blocking, sequential:** B01 Genesis CUDA_ERROR_ILLEGAL_ADDRESS crash at P2G (needs B02/B03 tested first), B02 vehicle mass roughly 5x too heavy (rho left uncorrected after a sedan resize), B03 water particles seeded inside the vehicle body at t=0.
- **Cluster B, parallel-safe, independent:** B04 ffmpeg missing from the mpm-engine env, B05 FloodScene vehicle scale mismatch (this is Kumar's actual ask), B10 an unexplained new file (`can_it_ford_L2_mpm_ytest.py`) that could be hiding a real bug.
- **Cluster C, repo and citation hygiene, zero execution risk:** B06 confirm whether two July 10 commits survived a rebase, B13 scrub a wrong citation attribution for DRIFT_THRESHOLD wherever it still appears, not only in one file.
- **Cluster D, comms and hygiene, touches nothing in simulation code:** B07 three drafted Kumar updates, zero sent, B08/B09 MacBook shell environment issues, B15 an unrevoked-versus-rotated API key ambiguity, resolve before any script touches real W&B data.
- **Decision item, not a bug, do not "fix" it, decide after evidence exists:** B11, three vehicle representations now exist across the two tracks (kinematic-only box, full-6-DOF box, mesh-based FloodScene), the right move is deciding which to carry forward after B01 and B05 have real results, not before.

**File ownership map used that night:** `can_it_ford_L2_mpm.py` was Pane-0.7-only. `STATUS.md` was Pane-0.4-only. The Kumar Slack message was Pane-0.3-only, gated on results from Panes 0.7 and 0.0. All other panes wrote to scratch files, never to each other's owned files.

**The meta-finding that made this session worth writing down as a skill:** none of the bugs above were hidden. Every fact needed to catch them was already sitting in a log or in `CLAUDE.md`. They survived because live multi-pane debugging under time pressure rewards reacting to the newest error over cross-referencing older facts. The fix that generalizes: make scripts print their derived numbers at startup (actual mass, an overlap check), not just the raw parameters they were given, and run the rabbit-hole checklist above before going deep on any one thread.
