#!/usr/bin/env python3
"""Domain sizing for the fork scene, with the axis trap closed by construction.

THE RULE IS NOT NEW. It is the as-ran rule generalised.
    lim = max(2.2 * ext_long, 3.5 * ext_short, 6.0 * depth)
It reproduces the canonical Yaris grid_lim 9.421742313727737 exactly, so it is
what the 17 gated runs actually used, not an invention. As-ran sites, read live
2026-08-14:
    renders/yaris_render_s1/_incoming/sim_standing.py:82   (canonical driver,
        389 lines, sha256 5215c38bed607ef6..., the copy register D4a names)
    renders/yaris_render_s1/sim_standing.py:160            (top-level copy has
        DRIFTED to a different line number; do not cite :82 against it)
    renders/yaris_render_s3_enhanced/sim_enhanced.py:232
    analysis/gp_surrogate.py:26

THE AXIS TRAP, AND WHY A POSITIONAL RULE CANNOT BE SAFE
=======================================================
The as-ran rule is written positionally, `max(2.2*ext[1], 3.5*ext[0], ...)`,
and it is correct ONLY in the driver frame, where `load_vehicle(up="z")` has
already permuted the hull so its long axis lies on y. Feed it raw PLY extents
and `3.5*ext[0]` becomes 3.5 x the vehicle LENGTH and wins the max.

Measured live 2026-08-14 from the canonical PLY itself
(vehicle_geometry_research/yaris_coarse_v1l_watertight.ply, 327212 vertices,
sha256 b379fa44..e9949a95), not recalled:

    PLY extents (x, y, z)      4.282609940  1.746377945  1.518008113
    lim, PLY axes face value      14.989134789 m
    lim, as-run (inventory)        9.421742314 m
    error                            +59.0909 %

A 59 percent error in `lim` silently rescales every dx, every particle count
and every realized depth in the run, and nothing in the pipeline objects.

THE FIX IS TO MAKE THE RULE INVARIANT, NOT TO REMEMBER THE AXIS ORDER.
`grid_lim()` below sorts the two HORIZONTAL extents and never reads them
positionally, so it returns the same answer whether the long axis is on x or
on y. `test_fork_scene_domain.py` proves this by feeding it the same hull in
both orders and also asserting that the naive positional form DIVERGES, so the
test is demonstrably able to fail.

SORT THE TWO HORIZONTAL EXTENTS, NOT ALL THREE. This is a real distinction and
it is currently latent rather than live. `hull_sweep.sbatch:30-33` describes
the anchor as "derived from each hull's own sorted extents". Sorting all three
would let a hull's HEIGHT supply `ext_short` whenever the hull is taller than
it is wide. Checked live against the three qualified hulls:

    yaris      x 4.282610  y 1.746378  z 1.518008   height < width, no effect
    rogue      x 4.746607  y 2.010112  z 1.729385   height < width, no effect
    silverado  x 5.939970  y 2.337686  z 2.010162   height < width, no effect

so all three agree today and the distinction changes no published number. It
would bite the first short, tall hull (a van, a box truck) that enters the
sweep, which is exactly when nobody would be looking for it. The guard costs
nothing, so it is here.

WHAT THE RULE DOES NOT DO. It is a tank-sizing heuristic, not a convergence
criterion. CLAUDE.md L-3 stands: the g64 baseline resolves the water depth with
2 grid cells and 4 particle layers against a rules-of-thumb 10 per depth. Sizing
the tank correctly does not make the tank converged.
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "LIM_LONG_FACTOR", "LIM_SHORT_FACTOR", "LIM_DEPTH_FACTOR",
    "CANONICAL_DEPTH_M", "CANONICAL_YARIS_LIM_M", "ANCHORS",
    "horizontal_extents", "grid_lim", "grid_lim_naive_positional",
    "DomainSpec", "assert_reproduces_anchor",
]

# --- the as-ran coefficients. Do not change these without a new anchor set. ---
LIM_LONG_FACTOR = 2.2
LIM_SHORT_FACTOR = 3.5
LIM_DEPTH_FACTOR = 6.0

# data/all_runs_inventory.csv, rows g64_m1100 and g96_m1100, read live 2026-08-14.
# grid_lim is identical on both because it depends only on hull and depth.
CANONICAL_DEPTH_M = 0.2944294473039918
CANONICAL_YARIS_LIM_M = 9.421742313727737

# Anchors: (hull extents as they sit in the PLY, expected lim, provenance).
# Extents measured live 2026-08-14 by reading each PLY's vertex block directly
# and taking max-min per axis in float64. Written at FULL precision on purpose:
# rounding them to 6 decimals moves lim by ~1e-6 m and trips the guard below,
# which is a rounding artefact and would waste a future session's time.
#
# sha256 heads are the artifact identity. Per the qualified-mesh MANIFEST the
# mesh pipeline is NOT bit-reproducible (same effective arguments give a
# different sha256, and at g96 even a different face count), so cite the sha of
# the file and never the command that made it. Do not regenerate a shipped hull
# to "verify" it; you will get a different file and it proves nothing.
#
# `residual_m` is the observed |rule - recorded| and is part of the record:
# rogue and silverado reproduce to 1e-10 because hull_sweep.sbatch computed
# them from these same meshes, while yaris carries 4.5e-7 m because its
# recorded value came off the as-run driver, which sizes from the LOADED
# vehicle extent (float32, post-canonicalization) rather than the raw PLY
# bounding box. 4.5e-7 m on 9.42 m is 4.7e-8 relative. That is precision, not
# disagreement, and it is stated rather than hidden by a loose tolerance.
ANCHORS = {
    "yaris": {
        "ply_extent": (4.282609939575195, 1.746377944946289, 1.5180081129074097),
        "lim_m": CANONICAL_YARIS_LIM_M,
        "sha256_head": "b379fa44",
        "residual_m": 4.5e-7,
        "source": "data/all_runs_inventory.csv g64_m1100/g96_m1100 grid_lim",
    },
    "rogue": {
        "ply_extent": (4.746607303619385, 2.0101118087768555, 1.7293853759765625),
        "lim_m": 10.442536068,
        "sha256_head": "c0b778e2",
        "residual_m": 4.0e-11,
        "source": "renders/yaris_render_s3_enhanced/hull_sweep.sbatch:37",
    },
    "silverado": {
        "ply_extent": (5.939969539642334, 2.337686061859131, 2.010161876678467),
        "lim_m": 13.067932987,
        "sha256_head": "46fba11e",
        "residual_m": 2.2e-10,
        "source": "renders/yaris_render_s3_enhanced/hull_sweep.sbatch:37",
    },
}


def horizontal_extents(extent, up_axis: int = 2):
    """Return (long, short) of the two extents perpendicular to `up_axis`.

    `up_axis` is explicit and has no safe default that can be inferred from the
    numbers alone, so it is a parameter rather than a guess. It is 2 for both
    the PLY frame and the driver frame here, because `load_vehicle(up="z")`
    permutes x and y and leaves z alone; that is checked in the tests rather
    than assumed.
    """
    if up_axis not in (0, 1, 2):
        raise ValueError("up_axis must be 0, 1 or 2")
    e = [float(v) for v in extent]
    if len(e) != 3:
        raise ValueError("extent must have three components")
    if any(v <= 0.0 for v in e):
        raise ValueError("extents must be positive")
    horiz = [e[i] for i in range(3) if i != up_axis]
    return max(horiz), min(horiz)


def grid_lim(extent, depth: float, up_axis: int = 2) -> float:
    """The as-ran domain edge, computed so the horizontal axis order cannot matter.

    Units: metres in, metres out. `depth` is the nominal still-water depth above
    the floor plane, not the realized depth (they differ; the realized depth is
    what the inventory records).
    """
    if depth <= 0.0:
        raise ValueError("depth must be positive")
    long_h, short_h = horizontal_extents(extent, up_axis=up_axis)
    return max(LIM_LONG_FACTOR * long_h,
               LIM_SHORT_FACTOR * short_h,
               LIM_DEPTH_FACTOR * float(depth))


def grid_lim_naive_positional(extent, depth: float) -> float:
    """The as-ran rule copied POSITIONALLY, i.e. the trap. Kept so the test suite
    can prove the safe form differs from it rather than asserting that it does.

    This is `max(2.2*ext[1], 3.5*ext[0], 6.0*depth)` verbatim. Correct in the
    driver frame, wrong by +59.09% on the canonical hull's own PLY axes. Never
    call this for anything but a test.
    """
    e = [float(v) for v in extent]
    return max(LIM_LONG_FACTOR * e[1],
               LIM_SHORT_FACTOR * e[0],
               LIM_DEPTH_FACTOR * float(depth))


@dataclass(frozen=True)
class DomainSpec:
    """A fully-determined cubic domain. Every field is derived, none is free.

    `wall` and `floor` reproduce the canonical scene's own offsets, read live
    from renders/yaris_render_s3_enhanced/sim_enhanced.py:232-252 and the
    canonical driver: floor = 3*dx, wall = 4*dx, particle spacing h = dx/2.
    """

    lim_m: float
    n_grid: int
    depth_m: float

    @property
    def dx(self) -> float:
        return self.lim_m / self.n_grid

    @property
    def h(self) -> float:
        """Particle spacing, dx/2, i.e. 8 particles per cell."""
        return 0.5 * self.dx

    @property
    def floor_z(self) -> float:
        return 3.0 * self.dx

    @property
    def wall(self) -> float:
        return 4.0 * self.dx

    @property
    def cells(self) -> int:
        return self.n_grid ** 3

    @property
    def cells_per_depth(self) -> float:
        """How many grid cells resolve the still-water depth.

        CLAUDE.md L-3, verified there against the inventory: this is exactly
        2.000 at the g64 baseline, against a rules-of-thumb 10 per flow depth.
        Report it with every run; it is the project's headline resolution
        limitation and it should never have to be recomputed by hand.
        """
        return self.depth_m / self.dx

    @property
    def water_span_m(self) -> float:
        """Free horizontal span of the water block, lim - 2*wall."""
        return self.lim_m - 2.0 * self.wall

    def describe(self) -> str:
        return (f"lim {self.lim_m:.9f} m, n_grid {self.n_grid}, "
                f"dx {self.dx:.9f} m, h {self.h:.9f} m, "
                f"depth/dx {self.cells_per_depth:.3f}, cells {self.cells:,}")


def assert_reproduces_anchor(name: str, tol_m: float = 1.0e-6) -> float:
    """Refuse to proceed unless the rule reproduces a recorded as-ran lim.

    This is `sim_enhanced.py` E8's discipline, made callable: anchor on the
    recorded number instead of re-deriving it from an assumed axis order. The
    yaris tolerance has to allow ~5e-7 m because the PLY stores float32
    vertices, so the extent recovered from the mesh differs from the as-run
    value in the 7th decimal. That is precision, not disagreement.
    """
    if name not in ANCHORS:
        raise KeyError(f"no anchor named {name!r}; have {sorted(ANCHORS)}")
    a = ANCHORS[name]
    got = grid_lim(a["ply_extent"], CANONICAL_DEPTH_M)
    if abs(got - a["lim_m"]) > tol_m:
        raise AssertionError(
            f"{name}: rule gives {got:.9f} m, recorded as-ran is {a['lim_m']:.9f} m "
            f"({a['source']}). Difference {got - a['lim_m']:+.3e} m exceeds {tol_m:g} m. "
            "Do NOT proceed: everything downstream of lim is rescaled by this.")
    return got


if __name__ == "__main__":
    print("fork_scene.domain self-check")
    print("=" * 72)
    for name in ("yaris", "rogue", "silverado"):
        a = ANCHORS[name]
        got = assert_reproduces_anchor(name)
        naive = grid_lim_naive_positional(a["ply_extent"], CANONICAL_DEPTH_M)
        print(f"{name:10s} sha {a['sha256_head']}  ext {a['ply_extent']}")
        print(f"           lim invariant {got:.9f} m   recorded {a['lim_m']:.9f} m"
              f"   d = {got - a['lim_m']:+.2e}")
        print(f"           lim positional {naive:.9f} m   error vs as-ran"
              f" {100.0 * (naive / a['lim_m'] - 1.0):+.4f} %")
    print("-" * 72)
    d = DomainSpec(lim_m=CANONICAL_YARIS_LIM_M, n_grid=64, depth_m=CANONICAL_DEPTH_M)
    print("canonical g64 :", d.describe())
    d96 = DomainSpec(lim_m=CANONICAL_YARIS_LIM_M, n_grid=96, depth_m=CANONICAL_DEPTH_M)
    print("canonical g96 :", d96.describe())
    print("=" * 72)
    print("All three hulls reproduce their recorded as-ran lim; the positional")
    print("form does not. The rule is safe under a horizontal axis permutation.")
