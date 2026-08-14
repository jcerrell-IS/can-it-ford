"""fork_scene: the flooded-road scene for the moving-vehicle fork, and the
architectural constraint that decides how big it is allowed to be.

Written 2026-08-14 for Dispatch 10. Design side only: every number in this
package is computed on the Mac from a primary source (a mesh, a vendored
kernel, or data/all_runs_inventory.csv). Anything requiring the GPU solver is
labelled and lives in `runner.py`, which is meant for LS6 BATCH.

WHAT THIS PACKAGE IS FOR, IN ONE SENTENCE
    Build the smallest scene that can honestly answer "does the road's
    cross-slope change the traction margin", and state the resolution-versus-
    extent trade in numbers rather than discovering it at run time.

THE HARD ARCHITECTURAL CONSTRAINT
    warpmpm's GridConfig takes a SINGLE SCALAR domain edge, verified live at
    third_party/mpm-engine-544c93dd-solver-core/core/solver.py:48-54:

        n_grid: int = 64
        grid_lim: float = 0.4  # cubic domain edge, metres
        dx = grid_lim / n_grid

    so the domain is necessarily CUBIC and isotropic. A long shallow channel
    costs cubically. See `resolution_extent.py` for the arithmetic; the short
    version is that a 30 x 12 x 3 m road-scale scene at the validated near-floor
    resolution is 279x the canonical Yaris tank, and anisotropic grading is not
    a way out because the grid cannot express it and the explicit timestep
    follows the smallest cell anyway.

MODULES
    domain.py            domain-sizing rule, invariant to the horizontal axis
                         permutation that has already caused a +59.09% error
    cross_slope.py       the two cross-slope formulations and the traction
                         margin they move
    resolution_extent.py the resolution-versus-extent arithmetic
    scene.py             assembles a scene spec; wires the EXISTING Zhao 2019
                         in/outflow rather than writing a third copy of it
    runner.py            the only module that touches the solver; LS6 BATCH

WHAT IS DELIBERATELY NOT HERE
    No reconstructed outdoor scene. A prior reconstruction attempt produced a
    metrically wrong mesh (a car at 0.333 x 0.174 x 0.715 m, volume 0.0173 m3,
    watertight) because the splat trainer normalises median camera-to-subject
    distance to 1.0 and no scale-recovery step exists. The failure was metric,
    not geometric. Terrain fidelity is escalated to only if the cross-slope
    sensitivity says terrain matters.
"""

__all__ = ["domain", "cross_slope", "resolution_extent", "scene"]
