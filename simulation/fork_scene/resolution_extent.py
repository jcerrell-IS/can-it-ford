#!/usr/bin/env python3
"""The resolution-versus-extent trade, computed rather than asserted.

WHY THIS FILE EXISTS. The question "can we simulate a road-scale flooded
crossing in warpmpm" has a numerical answer, and it should be produced before
anyone writes a driver, not discovered when a job dies. Everything here runs on
a laptop in under a second.

THE CONSTRAINT THAT DECIDES IT. Verified live 2026-08-14 at
third_party/mpm-engine-544c93dd-solver-core/core/solver.py:48-54:

    @dataclass
    class GridConfig:
        n_grid: int = 64
        grid_lim: float = 0.4  # cubic domain edge, metres
        dx = grid_lim / n_grid

ONE SCALAR. The domain is a CUBE and the cell is ISOTROPIC. Neither is a
default that can be overridden; there is no per-axis field to set. Two
consequences, and the second is the one usually missed:

  1. A long shallow channel costs cubically in extent.
  2. A road-shaped region of interest must be inscribed in a CUBE whose side is
     the LONGEST dimension, so most of the domain is air. For a 30 x 12 x 3 m
     road that is a 30 m cube, and the waste factor is 30^2/(12*3) = 25.0x
     before any resolution choice is made.

Point 2 is a property of the aspect ratio alone. It cannot be argued away by
picking a coarser grid, and it is the strongest single argument against an
arXiv-2607.00673-scale scene in this engine at this stage.

THE COST MODEL IS NOT CELL COUNT. Cell count is the memory story. The work
story includes the timestep, and the canonical driver's own CFL rule is read
live from renders/yaris_render_s1/_incoming/sim_standing.py:147-153 (the 389
line copy, sha256 5215c38bed607ef6...):

    c              = sqrt(1.1 * bulk_modulus / water_density)
    term_acoustic  = c / (0.28 * dx)
    term_viscous   = 6.0 * water_eta / (water_density * dx * dx)
    term_advective = max(velocity, 1e-6) / (0.5 * dx)
    substeps       = ceil(max(...) / fps)

The acoustic term dominates everywhere in the canonical sweep, and it scales as
1/dx. So per-frame work scales as

    cells * substeps  ~  n_grid^3 * (1/dx)  =  n_grid^4 / lim

REFINING BY 2x IN n_grid COSTS 16x, NOT 8x. A cells-only account understates
every refinement estimate in this project by exactly the refinement factor.
`verify_cfl_against_as_run()` below checks this model against the two recorded
substep counts before any of it is used.

A PREMISE FROM THE DISPATCH THAT DOES NOT SURVIVE CHECKING
==========================================================
The dispatch states "the validated near-floor regime is about 18 cells across
that depth, so dz = 0.01636 m", and the 246.8 M / 279x figures follow from it.
The arithmetic reproduces exactly (see `dispatch_arithmetic()`), but the 18 is
NOT a validated regime. Traced live 2026-08-14:

    docs/C1_ROOT_CAUSE_2026-08-07.md:337-347 records that commit 20dd999
    "deepened C2 to 18 cells on the argument that the box grounded out for lack
    of clearance", that scripts/c2only.sbatch:19-20 passes --depth-cells 18
    explicitly as job 894676, and that job's "four C2 arms all crashed at the
    same guard anyway". run_c2's own default is still depth_cells=10.

So 18 is a proposed fix in a validation arm that FAILED, not a validated
resolution. Nothing in this project has validated any cells-per-depth figure.
What the project has actually run is 2 cells per depth at g64 and 3 at g96
(CLAUDE.md L-3, reproduced by fork_scene.domain), against a rules-of-thumb
~10 particles per flow depth, i.e. ~5 cells at h = dx/2.

The number is therefore treated as a FREE PARAMETER here and the conclusion is
reported across its whole plausible range. That is the honest form of the
argument, and it turns out to be a stronger one: see `sweep_table()`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "CANONICAL_DEPTH_M", "BULK_MODULUS_PA", "WATER_DENSITY", "WATER_ETA",
    "EOS_GAMMA", "CFL_ACOUSTIC", "FPS", "SOUND_SPEED_MS",
    "sound_speed", "substeps_for", "verify_cfl_against_as_run",
    "SceneCost", "cube_waste_factor", "road_scale_cost", "canonical_cost",
    "dispatch_arithmetic", "sweep_table",
]

# --- canonical constants, all read live from primary sources 2026-08-14 -------
# data/all_runs_inventory.csv, rows g64_m1100 / g96_m1100
CANONICAL_DEPTH_M = 0.2944294473039918
CANONICAL_LIM_M = 9.421742313727737
BULK_MODULUS_PA = 150000.0
WATER_DENSITY = 1000.0
WATER_ETA = 0.001
SOUND_SPEED_MS = 12.84523257866513          # inventory column sound_speed_ms
CANONICAL_VELOCITY_MS = 1.5
# renders/yaris_render_s1/_incoming/sim_standing.py:147-153
EOS_GAMMA = 1.1
CFL_ACOUSTIC = 0.28
FPS = 30

# The road-scale target the dispatch names. Not a requirement, a reference shape.
ROAD_L_M, ROAD_W_M, ROAD_H_M = 30.0, 12.0, 3.0


def sound_speed(bulk_modulus=BULK_MODULUS_PA, density=WATER_DENSITY,
                gamma=EOS_GAMMA) -> float:
    """c = sqrt(gamma * K / rho). Units: sqrt(Pa / (kg/m3)) = sqrt(m2/s2) = m/s."""
    return math.sqrt(gamma * bulk_modulus / density)


def substeps_for(dx: float, velocity: float = CANONICAL_VELOCITY_MS,
                 fps: int = FPS, bulk_modulus=BULK_MODULUS_PA,
                 density=WATER_DENSITY, eta=WATER_ETA) -> int:
    """The canonical driver's substep count, verbatim from sim_standing.py:147-153."""
    c = sound_speed(bulk_modulus, density)
    term_acoustic = c / (CFL_ACOUSTIC * dx)
    term_viscous = 6.0 * eta / (density * dx * dx)
    term_advective = max(velocity, 1e-6) / (0.5 * dx)
    return int(math.ceil(max(term_acoustic, term_viscous, term_advective) / fps))


def verify_cfl_against_as_run() -> list[tuple[str, int, int, bool]]:
    """Falsifiable check: does the model reproduce the two RECORDED substep counts?

    data/all_runs_inventory.csv records substeps 11 for g64_m1100 and 16 for
    g96_m1100. Those were produced by the as-run driver, not by this file, so
    reproducing them is real evidence that the cost model below is the one the
    project actually pays. Nothing downstream should be trusted if this fails.
    """
    out = []
    for label, n_grid, recorded in (("g64_m1100", 64, 11), ("g96_m1100", 96, 16)):
        dx = CANONICAL_LIM_M / n_grid
        got = substeps_for(dx)
        out.append((label, recorded, got, got == recorded))
    return out


@dataclass(frozen=True)
class SceneCost:
    """Everything that decides whether a scene is runnable, in one place."""

    label: str
    lim_m: float                 # cubic domain edge
    dx_m: float

    @property
    def n_grid(self) -> int:
        return int(math.ceil(self.lim_m / self.dx_m))

    @property
    def cells(self) -> int:
        return self.n_grid ** 3

    @property
    def substeps(self) -> int:
        return substeps_for(self.dx_m)

    @property
    def work_per_frame(self) -> float:
        """cells * substeps. The quantity that actually scales, not cells alone."""
        return float(self.cells) * self.substeps

    @property
    def cells_per_depth(self) -> float:
        return CANONICAL_DEPTH_M / self.dx_m

    def row(self) -> str:
        return (f"{self.label:<26} n_grid {self.n_grid:>6}  dx {self.dx_m:9.6f}  "
                f"cells {self.cells:>16,}  substeps {self.substeps:>6}  "
                f"work/frame {self.work_per_frame:.3e}")


def cube_waste_factor(length=ROAD_L_M, width=ROAD_W_M, height=ROAD_H_M) -> float:
    """How much of a cubic domain is wasted on a box-shaped region of interest.

    side = max(L, W, H); factor = side^3 / (L*W*H). Depends only on the aspect
    ratio, so no grid choice can reduce it. This is the cubic constraint stated
    as a number.
    """
    side = max(length, width, height)
    return side ** 3 / (length * width * height)


def canonical_cost(n_grid: int = 96) -> SceneCost:
    return SceneCost(f"canonical yaris tank g{n_grid}", CANONICAL_LIM_M,
                     CANONICAL_LIM_M / n_grid)


def road_scale_cost(cells_per_depth: float, length=ROAD_L_M, width=ROAD_W_M,
                    height=ROAD_H_M) -> tuple[SceneCost, SceneCost]:
    """Return (hypothetical anisotropic box, the CUBE warpmpm actually forces).

    The first entry is what the region of interest would cost if the engine
    could grade the grid. It is reported only to size the penalty; warpmpm
    cannot express it, so it is never an option.
    """
    dz = CANONICAL_DEPTH_M / cells_per_depth
    nx, ny, nz = (int(math.ceil(length / dz)), int(math.ceil(width / dz)),
                  int(math.ceil(height / dz)))
    box = SceneCost(f"road box @ {cells_per_depth:g} cells/depth", length, dz)
    object.__setattr__(box, "_box_cells", nx * ny * nz)
    cube = SceneCost(f"forced CUBE @ {cells_per_depth:g} cells/depth",
                     max(length, width, height), dz)
    return box, cube


def dispatch_arithmetic() -> dict:
    """Reproduce the dispatch's own numbers exactly, so they can be audited.

    Reported whether or not the 18-cells premise survives, because a figure that
    is already circulating needs to be reproducible before it can be corrected.
    """
    cpd = 18.0
    dz = CANONICAL_DEPTH_M / cpd
    iso_cells = (ROAD_L_M / dz) * (ROAD_W_M / dz) * (ROAD_H_M / dz)
    g96 = canonical_cost(96)
    dxy_aniso, dz_aniso = 0.08, dz
    aniso_cells = (ROAD_L_M / dxy_aniso) * (ROAD_W_M / dxy_aniso) * (ROAD_H_M / dz_aniso)
    return {
        "cells_per_depth": cpd,
        "dz_m": dz,
        "road_box_isotropic_cells": iso_cells,
        "canonical_g96_cells": g96.cells,
        "ratio_vs_g96": iso_cells / g96.cells,
        "aniso_cells": aniso_cells,
        "aniso_reduction": iso_cells / aniso_cells,
    }


def sweep_table(cells_per_depth_values=(2.0, 3.0, 5.0, 10.0, 18.0)) -> list[dict]:
    """The conclusion across the whole plausible resolution range.

    2 and 3 are what the 17 gated runs actually ran at (g64, g96). 5 is the
    ~10-particles-per-depth rule of thumb at h = dx/2. 10 is run_c2's own
    default. 18 is the dispatch's figure. Reporting all five is what makes the
    conclusion independent of the unvalidated 18.
    """
    g96 = canonical_cost(96)
    rows = []
    for cpd in cells_per_depth_values:
        box, cube = road_scale_cost(cpd)
        rows.append({
            "cells_per_depth": cpd,
            "dz_m": cube.dx_m,
            "box_cells": getattr(box, "_box_cells"),
            "cube_n_grid": cube.n_grid,
            "cube_cells": cube.cells,
            "cube_substeps": cube.substeps,
            "cube_work": cube.work_per_frame,
            "cube_cells_vs_g96": cube.cells / g96.cells,
            "cube_work_vs_g96": cube.work_per_frame / g96.work_per_frame,
        })
    return rows


if __name__ == "__main__":
    print("fork_scene.resolution_extent")
    print("=" * 96)

    print("\n1. CFL model checked against the AS-RUN substep counts "
          "(data/all_runs_inventory.csv)")
    ok_all = True
    print(f"   c = sqrt({EOS_GAMMA} * {BULK_MODULUS_PA:g} / {WATER_DENSITY:g}) "
          f"= {sound_speed():.14f} m/s   inventory {SOUND_SPEED_MS:.14f}")
    assert abs(sound_speed() - SOUND_SPEED_MS) < 1e-12, "sound speed does not reproduce"
    for label, recorded, got, ok in verify_cfl_against_as_run():
        ok_all &= ok
        print(f"   {label:<12} recorded substeps {recorded:>3}   model {got:>3}   "
              f"{'MATCH' if ok else 'MISMATCH'}")
    if not ok_all:
        raise SystemExit("CFL model does not reproduce the as-run substeps; stop here.")

    print("\n2. The dispatch's stated arithmetic, reproduced verbatim")
    d = dispatch_arithmetic()
    print(f"   cells across depth        {d['cells_per_depth']:.0f}  -> dz {d['dz_m']:.5f} m")
    print(f"   30 x 12 x 3 m box, isotropic dz   {d['road_box_isotropic_cells']:>18,.0f} cells")
    print(f"   canonical yaris tank at g96       {d['canonical_g96_cells']:>18,} cells")
    print(f"   ratio                             {d['ratio_vs_g96']:>18.1f}x")
    print(f"   anisotropic dxy 0.08 / dz {d['dz_m']:.5f}  {d['aniso_cells']:>15,.0f} cells"
          f"   ({d['aniso_reduction']:.1f}x reduction)")
    print("   -> the dispatch's 246.8 M, 884,736 and 279x all reproduce.")

    print("\n3. THE PREMISE DOES NOT SURVIVE. 18 cells/depth is not validated;")
    print("   it is commit 20dd999's --depth-cells 18 for C2, job 894676, whose")
    print("   four arms all crashed (docs/C1_ROOT_CAUSE_2026-08-07.md:337-347).")
    print("   So the trade is reported across the range instead.\n")

    g96 = canonical_cost(96)
    print("   " + canonical_cost(64).row())
    print("   " + g96.row())
    print()
    hdr = (f"   {'cells/depth':>11} {'dz (m)':>9} {'ROI box cells':>16} "
           f"{'CUBE n_grid':>12} {'CUBE cells':>18} {'substeps':>9} "
           f"{'cells vs g96':>13} {'work vs g96':>12}")
    print(hdr)
    print("   " + "-" * (len(hdr) - 3))
    for r in sweep_table():
        print(f"   {r['cells_per_depth']:>11.0f} {r['dz_m']:>9.5f} "
              f"{r['box_cells']:>16,} {r['cube_n_grid']:>12,} {r['cube_cells']:>18,} "
              f"{r['cube_substeps']:>9,} {r['cube_cells_vs_g96']:>12,.0f}x "
              f"{r['cube_work_vs_g96']:>11,.0f}x")

    print(f"\n4. The cubic waste factor for a {ROAD_L_M:g} x {ROAD_W_M:g} x "
          f"{ROAD_H_M:g} m road: {cube_waste_factor():.1f}x")
    print("   This depends only on the aspect ratio. No grid choice reduces it.")
    print("\n5. Anisotropy is not a way out, for two independent reasons:")
    print("   (a) GridConfig is a single scalar, so it cannot be expressed at all;")
    print("   (b) even if it could, the explicit timestep follows the SMALLEST cell")
    print("       dimension, so grading buys memory and per-step work, NOT step count.")
    print("   Anisotropy is therefore a reason to change engine or patch the grid.")
    print("=" * 96)
