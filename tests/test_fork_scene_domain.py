"""Tests for simulation/fork_scene/domain.py, and specifically for the axis trap.

WHAT MAKES THIS A TEST AND NOT A TAUTOLOGY. It would be easy to write a suite
that only asserts `grid_lim` returns what `grid_lim` returns. Every test below
is paired with a demonstration that the SAME assertion fails against
`grid_lim_naive_positional`, which is the as-ran positional form kept in the
module for exactly this purpose. If the invariant form ever silently regresses
to positional indexing, `test_naive_positional_form_is_actually_broken` and
`test_permutation_invariance` fail together and say so.

THE TRAP, RESTATED IN ONE LINE. `load_vehicle(up="z")` swaps the hull's x and
y so the long axis lands on y; the as-ran rule `max(2.2*ext[1], 3.5*ext[0], ...)`
is written for that frame; applied to raw PLY axes it multiplies the LENGTH by
3.5 instead of 2.2 and returns 14.989 m instead of 9.4217 m.

WHY THE ERROR IS EXACTLY 3.5/2.2 EVERY TIME. Whenever the `2.2*long` term wins
the max (true for all three qualified hulls) and the PLY carries its long axis
on x, the positional form computes `3.5*long` instead of `2.2*long`, so the
ratio is exactly 3.5/2.2 = 1.590909..., i.e. +59.0909%, independent of the
hull. That is asserted below, because a constant is much easier to notice in a
diff than three unrelated-looking percentages.

RUNNING IT
    python tests/test_fork_scene_domain.py     # standalone, no pytest needed
    pytest tests/test_fork_scene_domain.py     # also works
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

# `simulation/` has no __init__.py and deliberately keeps none: adding one would
# change import behaviour for every standalone script already in that directory,
# several of which other sessions own. This resolves at runtime as an implicit
# namespace package (PEP 420); static checkers that predate namespace packages
# will flag it.
from simulation.fork_scene.domain import (  # type: ignore[import-not-found]  # noqa: E402
    ANCHORS,
    CANONICAL_DEPTH_M,
    CANONICAL_YARIS_LIM_M,
    LIM_LONG_FACTOR,
    LIM_SHORT_FACTOR,
    DomainSpec,
    assert_reproduces_anchor,
    grid_lim,
    grid_lim_naive_positional,
    horizontal_extents,
)

# The canonical hull in BOTH axis orders. Same physical hull, same sha256, the
# only difference is which axis carries the 4.28 m length.
YARIS_PLY_FRAME = ANCHORS["yaris"]["ply_extent"]                 # long on x
YARIS_DRIVER_FRAME = (YARIS_PLY_FRAME[1], YARIS_PLY_FRAME[0],    # long on y
                      YARIS_PLY_FRAME[2])

# Tolerance for "the same domain". 1e-9 m is a nanometre on a ~10 m tank; the
# invariant form should be bit-identical up to float association, and is.
TOL = 1.0e-9


def test_permutation_invariance():
    """Swapping the two horizontal extents must not change the domain."""
    a = grid_lim(YARIS_PLY_FRAME, CANONICAL_DEPTH_M)
    b = grid_lim(YARIS_DRIVER_FRAME, CANONICAL_DEPTH_M)
    assert abs(a - b) < TOL, f"axis order changed lim: {a!r} vs {b!r}"


def test_naive_positional_form_is_actually_broken():
    """The paired negative control. Without this the test above proves nothing.

    If this ever passes, the positional form has been quietly fixed or replaced
    and the invariance test above has stopped being evidence of anything.
    """
    a = grid_lim_naive_positional(YARIS_PLY_FRAME, CANONICAL_DEPTH_M)
    b = grid_lim_naive_positional(YARIS_DRIVER_FRAME, CANONICAL_DEPTH_M)
    assert abs(a - b) > 1.0, (
        "the positional form no longer diverges under an axis swap, so the "
        "invariance test above is no longer testing anything")


def test_positional_error_is_the_known_59_percent():
    """The trap's magnitude, on the canonical hull, against the as-run value."""
    naive = grid_lim_naive_positional(YARIS_PLY_FRAME, CANONICAL_DEPTH_M)
    err_pct = 100.0 * (naive / CANONICAL_YARIS_LIM_M - 1.0)
    assert 59.0 < err_pct < 59.2, f"expected about +59.09%, got {err_pct:+.4f}%"


def test_positional_error_is_exactly_the_factor_ratio_on_every_hull():
    """3.5/2.2 - 1, hull-independent, because the 2.2*long term wins for all three."""
    expected = 100.0 * (LIM_SHORT_FACTOR / LIM_LONG_FACTOR - 1.0)
    for name, a in ANCHORS.items():
        naive = grid_lim_naive_positional(a["ply_extent"], CANONICAL_DEPTH_M)
        safe = grid_lim(a["ply_extent"], CANONICAL_DEPTH_M)
        got = 100.0 * (naive / safe - 1.0)
        assert abs(got - expected) < 1.0e-9, (
            f"{name}: positional error {got:+.6f}% is not the factor ratio "
            f"{expected:+.6f}%; the 2.2*long term may no longer be winning the "
            "max for this hull, which changes what the trap does")


def test_all_three_hulls_reproduce_their_recorded_lim():
    """The anchors. A rule that does not reproduce the as-ran number is not the rule."""
    for name in ANCHORS:
        got = assert_reproduces_anchor(name)
        rec = ANCHORS[name]["lim_m"]
        assert abs(got - rec) <= ANCHORS[name]["residual_m"] * 1.5, (
            f"{name}: residual {abs(got - rec):.3e} m exceeds the recorded "
            f"{ANCHORS[name]['residual_m']:.1e} m")


def test_anchor_guard_actually_refuses():
    """The guard must fail loudly on a wrong hull, not shrug."""
    try:
        assert_reproduces_anchor("yaris", tol_m=1.0e-12)
    except AssertionError:
        pass
    else:
        raise AssertionError(
            "assert_reproduces_anchor accepted a 4.5e-7 m residual at a 1e-12 m "
            "tolerance, so it is not actually checking anything")


def test_height_never_supplies_the_short_extent():
    """Sorting all three extents is wrong; sorting the two horizontal ones is right.

    Synthetic hull: 6.0 m long, 2.0 m wide, 2.6 m tall, i.e. taller than it is
    wide, which no qualified hull currently is. Sorting all three would take
    2.0 as long-ish and 2.0... concretely it would take the GLOBAL minimum, 2.0,
    which happens to coincide here; the failure case is the reverse, a hull
    whose height is BELOW its width is fine and one whose height is above it is
    the risk. Built explicitly so the distinction is exercised rather than
    asserted.
    """
    ext = (6.0, 2.0, 2.6)          # x long, y width 2.0, z height 2.6
    long_h, short_h = horizontal_extents(ext, up_axis=2)
    assert long_h == 6.0 and short_h == 2.0, (long_h, short_h)
    # the all-three-sorted reading would have taken 2.0 as the minimum here too,
    # so make the divergence unambiguous with a hull whose height is the middle
    ext2 = (6.0, 2.6, 2.0)         # y width 2.6, z height 2.0
    long_h2, short_h2 = horizontal_extents(ext2, up_axis=2)
    assert long_h2 == 6.0, long_h2
    assert short_h2 == 2.6, (
        f"short extent came back {short_h2}, so height (2.0) leaked into the "
        "horizontal pair; the rule must never read the up axis")


def test_horizontal_extents_rejects_bad_input():
    for bad in [(0.0, 1.0, 1.0), (-1.0, 1.0, 1.0)]:
        try:
            horizontal_extents(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted non-positive extent {bad}")
    try:
        horizontal_extents((1.0, 1.0, 1.0), up_axis=3)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted up_axis=3")


def test_depth_term_can_win_for_a_small_hull():
    """The 6.0*depth floor exists; prove it is reachable, not decorative."""
    tiny = (0.5, 0.4, 0.3)
    assert math.isclose(grid_lim(tiny, 1.0), 6.0, rel_tol=1e-12)


def test_canonical_domain_spec_matches_the_inventory():
    """dx and depth/dx at g64 and g96 must match data/all_runs_inventory.csv.

    Inventory values, read live 2026-08-14 (g64_m1100, g96_m1100):
        dx  0.1472147236519959   and 0.0981431491013306
        realized_depth_m 0.2944294473039918 on both
    depth/dx is exactly 2 and 3, which is CLAUDE.md L-3's headline limitation.
    """
    g64 = DomainSpec(CANONICAL_YARIS_LIM_M, 64, CANONICAL_DEPTH_M)
    g96 = DomainSpec(CANONICAL_YARIS_LIM_M, 96, CANONICAL_DEPTH_M)
    assert abs(g64.dx - 0.1472147236519959) < 1e-15, g64.dx
    assert abs(g96.dx - 0.0981431491013306) < 1e-15, g96.dx
    assert abs(g64.cells_per_depth - 2.0) < 1e-12, g64.cells_per_depth
    assert abs(g96.cells_per_depth - 3.0) < 1e-12, g96.cells_per_depth
    assert g96.cells == 884736, g96.cells


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc}")
        else:
            print(f"ok    {fn.__name__}")
    print("-" * 72)
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
