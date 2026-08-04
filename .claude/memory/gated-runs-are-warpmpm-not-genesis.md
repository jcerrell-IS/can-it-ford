---
name: gated-runs-are-warpmpm-not-genesis
description: "The 17 gated runs came from warpmpm, the 9-condition pilot from Genesis SPH; fully corrected in text and artwork 2026-07-31, Genesis kept only where it reads as design intent"
metadata: 
  node_type: memory
  type: project
  originSessionId: bf457dae-d4f4-4ee4-83af-0a4635dc08b1
  modified: 2026-08-04T17:59:56.407Z
---

Verified live 2026-07-31 from
`renders/yaris_render_s1/_incoming/sim_standing.py`, which is the driver for the
17-run gated inventory:

```python
from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian
from warpmpm.vehicle import FloodHistory, load_vehicle, solidify_watertight
```

The package is `warpmpm`. `StandingFloodScene` is a class defined locally in that
same file, not an import, so do not attribute it to kks32/mpm-engine without
checking that separately.

Two different engines are in play:
- the 17 gated runs in `all_runs_inventory.csv` are **warpmpm** (Warp MPM)
- the 9 divergence runs in `l2_results_from_wandb.csv` carry `level=L2_Genesis_SPH`,
  which is **SPH, not MPM**

No reported result came from a Genesis MPM simulation.

**FULLY RESOLVED 2026-07-31 on `overleaf/main`**, across five commits. Josie's
call was to distinguish the designed engine from the one that ran:

- `6e3c13b` ladder table row now "Coupled rigid-body/MPM simulation"; the sweep
  subsection states outright that the 17 ran on warpmpm and the 9-condition pilot
  on Genesis SPH
- `d126d4d` Fig 1 caption and the numbered pipeline (stage 3) now separate design
  intent from provenance
- `e312809` Fig 1 artwork itself relabelled to "Warp MPM (rigid-fluid coupling)",
  and the orphaned `force_balance.jpg` deleted from the project
- `c880f14` the abstract and Section II-B, the last two holdouts (see below)
- `61b9b7b` abstract rewritten to IEEE length; still names no engine

The deciding argument on the artwork: the generator's own docstring defines a
SOLID box as a stage the 17 gated runs realized, so a solid box naming Genesis
asserted a provenance that is false for both datasets. Every other box names its
real tool, so the convention was already against it.

**The abstract and Section II-B were briefly logged here as "deliberately left
naming Genesis". That is superseded.** Both were corrected in `c880f14`:
- the abstract simply drops the engine credit rather than restating the design
  target a fourth time, since the Fig 1 caption, the pipeline description, and
  the sweep subsection all carry it and there is no page budget
- Section II-B also had a **contradiction that predated the whole pass**: it said
  the PhysGaussian-to-Genesis bridge "is built here rather than adopted" while
  the Fig 1 caption says that bridge is "designed and not yet built" and the
  figure draws the stage dashed. It now reads "has to be built rather than
  adopted, and it is not built yet."

Every surviving Genesis mention is legitimate: the `genesis2024` citation, the
pilot's Genesis SPH solver, and design-intent statements in the Fig 1 caption,
the pipeline description, and the sweep subsection.

**OPEN: two divergent fixes to the same generator, neither on `main`.**
`analysis/paper_fig_pipeline_diagram_v2.py` hard-codes
`REPO = Path('/Users/josie/can-it-ford')`, so running it from any of the 28
worktrees writes into the root checkout. Two panes fixed it differently:
- `0b386bc` on `claude/figure-validation-sources-826ba6` uses
  `os.environ.get('CANITFORD_REPO', '/Users/josie/can-it-ford')`
- `f302ce0` on `claude/bibliography-formatting-fix-4c3864` uses
  `Path(__file__).resolve().parents[1]`, and also fixes the stale docstring
  pointer to the superseded `paper/conference_101719.tex`

Both also set box 4 to "Warp MPM". The root checkout on `main` (6ae618c) still
has the hard-coded path AND still says `["Genesis MPM", ...]`, so **regenerating
Fig 1 from `main` silently reverts the published artwork.** Pick one fix and land
it; they will conflict.

Re-verified live 2026-08-04, all three still true: `main` emits `["Genesis MPM"`
with `REPO = Path('/Users/josie/can-it-ford')`, and both branch fixes are intact.

**Land `f302ce0`, not `0b386bc`.** They solve the same problem and `f302ce0` is
the better of the two: `Path(__file__).resolve().parents[1]` resolves to whatever
checkout the script is sitting in, automatically, whereas `0b386bc`'s
`CANITFORD_REPO` env var only works when the caller remembers to set it, which is
the same failure mode as the original bug. `f302ce0` also fixes the docstring's
stale pointer to the superseded `paper/conference_101719.tex`. This is a
recommendation from comparing the two, not a decision that has been made.

Kumar-facing: he wrote the Warp MPM code, so the paper now credits it correctly.
See [[overleaf-tex-is-canonical]] and [[git-show-mangles-binary-blobs]].
