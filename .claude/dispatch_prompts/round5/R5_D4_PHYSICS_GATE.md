# D4 — THE PHYSICS GATE
worktree `.claude/worktrees/r5-physics` · branch `claude/r5-physics`
YOU OWN: `simulation/r5_physics/`, `docs/R5_PHYSICS_*`. Write nowhere else.
NEVER edit `sim_standing.py`: its sha256 stamps every published run. Fork it.

## WHY YOU EXIST
Two gates block everything downstream. Pick ONE and finish it; say which and why.

**Option A, the outflow BC.** A bounded domain physically cannot measure a
slope, because conserving volume forces redistribution larger than the effect
being measured (measured: excursion 0.664, 0.937, 1.562 m with slope; a margin
sized at S=0 is wrong by 2.35x at S=0.06). The fix is an open channel with a
real mass sink: Zhao, Bolognin, Liang, Rohe & Vardon 2019, Computers and Fluids
179:27-33, doi 10.1016/J.COMPFLUID.2018.10.007. It was wired and validated 3/3
on closed-form cases, then **the level did NOT hold under steady inflow equals
outflow**. Cause identified, not implemented: **the Anura3D team impose BCs at
GRID NODES; ours is particle-level.** Read the companion by the same team,
Remmerswaal, Bolognin, Vardon, Hicks & Rohe 2019, "Implementation of
non-trivial boundary conditions in MPM", before writing code.

**Option B, the first external validation this project would ever have.**
Kramer et al. 2021, Energies 14(2):269, doi 10.3390/en14020269: a PUBLIC
downloadable heave-decay dataset for a floating sphere at ~0.3% experimental
uncertainty. A sphere has an analytic displaced volume, so it isolates buoyancy
plus added mass plus damping, which is exactly the coupling nothing here
validates. CLAUDE.md item 6 records that **no gate in this project is a physics
validation**, and the at-rest gate was shown to be **tunable** (every resolution
contains a passing band). Note Kramer 2021 is a DIFFERENT paper from the Kramer
2016 watertightness work already in the register; same author, do not merge them.

## CONSTRAINTS YOU MUST RESPECT
Vista is aarch64 and the ONLY host with `set_sdf_pose`; LS6 has no usable
warpmpm and is the x86 machine for Chrono and pysplashsurf. Use `tacc_submit`,
which injects `--overlap` and detaches. A resolution ceiling sits at dx
0.0906 to 0.0942 m, reproducible and time-growing, so any run finer than that
needs a repeat-run determinism floor beside it. `settle_frames=8` is a guess
inside a ~100-frame ring and produced four false results; use a converged settle
and state it.

## DEFINITION OF DONE
Option A: a grid-node BC that holds a constant level, with its tolerance stated,
or a documented reason it cannot with the closed-form evidence. Option B: the
SDF-collider path run against Kramer 2021 with the heave-decay curve compared to
published data and an error stated against their 0.3%, written up identically
whether it passes or fails.

## STANDING PROTOCOL (identical for all four, read once)
Before starting: read `/Users/josie/can-it-ford/.claude/tooling/ERRORS_AND_RESOLUTIONS.md`,
then `git log`, then `/Users/josie/can-it-ford/.claude/state/round5_board.md`.
Do not duplicate a sibling; append your own row to the board after each unit.

SELF-SUFFICIENCY. Decide for yourself. If a path, file, number or citation is
uncertain, GO FIND IT rather than asking: `corpus_resolve`/`corpus_search` for
any research file, `scite` or `scholar-sidekick` for any DOI, `wolfram` for any
unit or parameter, `deepwiki` for library behaviour (treat as hypothesis, verify
against source), `canford-tacc` for anything on Vista or LS6. If blocked, try a
genuinely DIFFERENT second approach, then write a named flag file and KEEP
WORKING on the rest of your scope. One blocker never ends a session.

CLAIM DISCIPLINE. Tag every claim: read directly / recalled / inferred. Report N
and spread, never a single draw. State the settle length behind any simulation
number. Run the physics-skeptic subagent before finalising any percentage,
force, verdict count or distance; if unavailable, say so and mark it UNREVIEWED.
An import succeeding is not an environment working. An empty result from one
directory is a broken probe, not an absence.

GIT. Commit each coherent unit as you finish it, path-limited:
`git commit -m "msg" -- <paths>`, 8 files max. Never bulk-stage. NEVER push. The
repo is PUBLIC. Writing to an absolute /Users/josie/can-it-ford/... path from
your worktree lands in the MAIN checkout: use paths relative to your own tree.
Never edit CLAUDE.md, the register, or sim_standing.py.

WHEN YOU FINISH A UNIT, keep going. Pick the next highest-value item in YOUR
scope. The auto-dispatcher will also nudge you, but do not wait for it.
No em-dashes.

