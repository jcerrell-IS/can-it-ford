# FLAG: TOPPLE classification may inherit the C1 coupling-force defect

Written 2026-08-07 ~19:20 by a chat-side session with visibility into both
threads below (neither Claude Code terminal session can see the other).
Additive only. Edits nothing. Not yet actioned by anyone.

## The collision

Two sessions worked today without referencing each other's output:

1. The failure-mode-classifier session (per
   `docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md`) ran
   `analysis/classify_failure_modes.py` on all 17 gated runs and produced
   `data/failure_modes_by_run_classified.csv` as the new canonical store.
2. The ctx-census session (`docs/C1_ROOT_CAUSE_2026-08-07.md`, section 8)
   established that no force, drag or hydrodynamic-load number may be
   back-computed from vehicle acceleration on the free-rigid coupling path.
   The body's velocity is a mass-weighted grid average recomputed from
   scratch every substep, not an integrated Newtonian response to a force.

## Why TOPPLE is directly implicated [READ this session]

`simulation/failure_modes.py:170`
`surge_accel_g = np.abs(kin.accel[:, SURGE_AXIS]) / G`

`simulation/failure_modes.py:182`
`topple_idx = _first_sustained_index(surge_accel_g >= ssf, th.sustain_frames)`

TOPPLE is gated on raw acceleration converted to g-force and compared against
SSF. That is exactly the class of quantity C1_ROOT_CAUSE.md section 8 names as
forbidden, at HIGH confidence.

SLIDE and FLOAT are gated on displacement and lift, which section 8 rates at
MEDIUM confidence: kinematic integrals of the same non-Newtonian velocity
field, not a back-computed force, but downstream of the same defect.

Neither `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` nor
`docs/COUPLING_VALIDATION_J1_2026-08-07.md` references C1_ROOT_CAUSE as of
this writing. `grep -l "C1_ROOT_CAUSE"` on both returns nothing.

## What this does not say

It does not say any of the 17 verdicts are wrong. C1_ROOT_CAUSE.md section 8
is explicit that the binary NO-FORD verdicts are not shown wrong by this. It
says the TOPPLE mode specifically, and to a lesser extent SLIDE and FLOAT,
need a caveat or a re-derivation before appearing in any figure, caption, or
paper text alongside the rest of the classifier's output.

## Suggested resolution, not yet actioned

Either add an explicit caveat to any use of TOPPLE classifications, matching
C1_ROOT_CAUSE section 8's language, or re-run the classifier with
`surge_accel_g` excluded from the TOPPLE gate until the free-rigid coupling
defect is fixed or worked around. Whoever owns
`analysis/classify_failure_modes.py` next should decide. This file does not
decide it.
