# FLAG: the Round 5 D4 PHYSICS-GATE dispatch is firing into a session that is not D4

**Raised 2026-08-18 by the r7-collect session, branch `claude/r7-collect`, HEAD `f8d22fe`.**
Filed on my own branch because I own nothing else. **No action taken on D4's scope.**

## What is happening

An `AUTO-FOLLOW-UP for D4 PHYSICS-GATE` has now fired **twice** into this session (05:14 and
05:46 BST). It opens "Your branch claude/r5-physics is at: 6ed163e" and assigns the mission
"grid-node outflow BC, or first external validation against Kramer 2021", scoped to
`simulation/r5_physics/` and `docs/R5_PHYSICS_*`.

**This session is not D4.** It is the r7-collect session on `claude/r7-collect`, dispatched to
collect Round 7 ledger items 2 and 3 (jobs 918351 and 918450). That work is finished and
committed at `b6e4de3` and `f8d22fe`.

## D4 does not exist. Verified from three views, on 2026-08-18

State the view searched, per CLAUDE.md, because absence of evidence from a partial view is not
evidence of absence. All three agree:

1. **Agent registry.** `ListAgents` returns 14 peer sessions. Two are `r5-research`, none is
   `r5-physics`. Live siblings include `r7-pinned-span-a3` (busy) and `r7-inflow-16` (idle).
2. **tmux pane cwd.** No pane anywhere has a `pane_current_path` under `r5-physics`.
3. **Process cwd.** `lsof -a -p <pid> -d cwd` over every live `claude` process returns no cwd
   under `r5-physics`.

This is consistent with the Round 7 handoff section 11b, which records that Round 6 "deployed
four daughter sessions and then cleared them". **The R5 dispatcher appears to still be running
and is now firing D4's follow-up at whichever session occupies the pane D4 used to hold.**

## Why I did not simply do the work

Three reasons, in order of weight:

1. **`claude/r5-physics` is checked out in another worktree**, `.claude/worktrees/r5-physics`,
   clean at `6ed163e`. Git will not let a second worktree check out the same branch, so any work
   I did would land on `claude/r7-collect` instead, where D4 would never find it.
2. **Writing into `simulation/r5_physics/` via absolute paths would write into that live tree
   directly**, which is the 2026-08-07 concurrent-session breach exactly. 2 to 3 other sessions
   have been active in this repo throughout.
3. **The round5 board assigns that scope to D4** and says "Append only; never rewrite another
   session's lines."

Adopting an abandoned mission is a decision for Josie or the coordinator, not for a session that
was dispatched to do something else.

## What D4's successor needs to know before touching the ghost-layer work

All three are measured, committed at `f8d22fe`, and were re-verified independently by this
session after a `physics-skeptic` pass returned "Not CLEAN".

1. **THE SACRIFICIAL SUB-FLOOR IS AIMED AT THE TERM THAT IS NOW MINOR.** Job 918450's one-line
   boundary fix (`mpm_solver_warp.py:1955`, `< 0.0` to `<= 0.0`) cut the floor leak by 96.3
   percent, 26964 to 1002 particles. The residual floor leak is **0.167 percent of the water and
   buys 0.014 cm of surface**. The wall leak is now dominant at 15868 particles, 2.651 percent,
   and it GREW 10 percent under the fix. Mass balance: leakage explains at most **58 percent** of
   the 2.384 cm physical surface fall, the rest closing against the elastic compression term
   `sphere_heave.py`'s own `water_budget` docstring already bounds at 0.742 cm.
   **The mass-deficiency argument now has to be made at the WALLS, not the floor.**

2. **JOB 918461 `d4_ghost` COMPLETED AND IS UNCOLLECTED.** 00:02:14, ExitCode 0:0,
   `SUMMARY failed=0`, `ALLDONE`. Both arms written to `$WORK/d4_ghost_918461/`:
   `sphere_ghost0.json` and `sphere_ghost3.json`, 300 frames each. **Check the configuration
   before trusting it:** 2x300 frames in 2:14, against job 918450's 200 frames in 6:53 on the
   same `sphere_cells_across 16.0 / substeps 82` scene, is roughly 9x faster per frame. That gap
   suggests a smaller configuration than intended. I did not collect or analyse it; it is D4's.

3. **`grade_job_b.py` IS NOT MISSING THE DESIGNATED ACCESSOR.** An earlier version of my own
   document claimed it was, and that claim is retracted at `f8d22fe`. Running the tool emits
   `measured-surface ratio 1.3435 (+34.35% from 1.0) BAND: FAIL` on the refusal path, and
   `grade_job_b.py:199-205` records the defect as already fixed. The real, narrow defect is that
   only the **top-level `band` key** is nominal-derived. Do not "fix the accessor"; promote the
   measured criterion to the top-level band.

**Job B still FAILS its pre-registered criterion after the boundary fix**, +34.35 percent against
a 25 percent FAIL band, window-robust. `R5_PHYSICS_BATCH_MANIFEST.md:214`, "Any FAIL stops the
ladder." **The ladder is still stopped and Job C is still gated.** Note the A/B is **N=1 against
N=1** with no repeat for the sphere scene anywhere in the data, so the direction is safe and the
magnitude is not.

## Requested action

**From the coordinator or Josie:** either stop the R5 dispatcher, or re-point D4's follow-up at a
session that actually holds `claude/r5-physics`. It is currently consuming a session dispatched
to other work, and will keep firing.

**Not urgent for the science.** D4's branch is clean at `6ed163e` with 73 commits unpushed and
HELD, and nothing is mid-write.
