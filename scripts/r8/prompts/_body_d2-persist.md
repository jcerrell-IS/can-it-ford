# SLOT d2-persist

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-persistence, branch
claude/r8-persistence (branched off claude/r7-inflow).

You may write ONLY:
  analysis/r8_persistence_frequency.py    (new)
  docs/R8_PERSISTENCE_GATE_2026-08-18.md  (new)

NEVER TOUCH: simulation/failure_modes.py. You PROPOSE the change, a human makes it.
Never write back to claude/r7-inflow; a live session owns it.

## WHERE THIS LEFT OFF
r7-inflow tip 57523c8 closed ledger item 7 and made item 9 the top-ranked open item by its own
conclusion, quoted exactly:
  "The v0.5 recycle arm reaches 0.1793 m, 3.6x the slide_m threshold and 6.2x its own closed
   control, and is still classified STUCK. A binary that will not move while the quantity under
   it moves 6x is the case for reporting gate-pass frequency instead of a persistence-gated
   pass/fail."
Ledger 3c (docs/HANDOFF_ROUND_7_2026-08-18.md, in your worktree) gives the sweep:
  g48,g64: 5 SLIDE at sf=3,4,5.  g96: 5 SLIDE / 2S3K / 0S5K.  g128: 5 SLIDE / 0S5K / 0S5K.
  g160: 0S5K at every threshold. The fragility is a fine-grid phenomenon and vanishes at g160.

## THE RESEARCH, DO NOT REDISCOVER IT
- The project's own 332-paper index returns ZERO matches for "persistence":
    python3 /Users/josie/can-it-ford/analysis/research_index.py --query persistence
- Bonham & Hattersley 1967 and Gordon & Stone 1973 restrained their models "by fine threads both
  vertically and laterally", so no motion time series existed and a duration was NOT MEASURABLE
  IN PRINCIPLE.
- Martinez-Gomariz 2017, UPCommons postprint, primary: instability is "if the model vehicle moved".
- failure_modes.py:52 is `sustain_frames = 3`, 0.1 s at 30 fps, no source. Register D6f records
  the same constant as the only thing keeping TOPPLE from firing on all 13.
- THREE literals share the numeral 0.05 across TWO units at failure_modes.py:46-48:
  slide_m = 0.05 m, slide_speed_ms = 0.05 m/s, float_m = 0.05 m. Deduplicate by NAME and UNIT.

## THE RULE THAT GOVERNS YOUR WRITE-UP
Your worktree CLAUDE.md is frozen at its branch point. The preflight prints the missing sections.
The one that governs you is "THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA": FULL
RECORD for verdicts, and no convergence claim from any extremal quantity. Removing the transient
drops SLIDE from 21 of 24 runs to 5 of 24, so do NOT remove it.

## FIRST STEP
Build the gate-pass FREQUENCY table that replaces the binary. For every local run with a
metrics.csv (37: 25 under renders/, 12 under data/g128_*), compute per frame whether the joint
slide condition holds, then report the FRACTION of frames passing, per run and per grid, instead
of a pass/fail gated on 3 consecutive frames. Use uv for numpy if you want it.

## DEFINITION OF DONE
1. A frequency table covering every local run, with the run count enumerated, not asserted.
2. An explicit statement of what changes and what does not against the published 16 SLIDE /
   1 STUCK, with the threshold triple quoted alongside every count.
3. A recommendation with its refuting mechanism NAMED: state what observation would show the
   frequency measure is worse than the binary, and show it does not fire.
4. failure_modes.py unedited.
