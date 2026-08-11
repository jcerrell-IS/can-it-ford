#!/usr/bin/env python3
"""Ground-clearance resolution audit for the canonical Yaris hull, and the CPIC verdict.

WHY THIS EXISTS
---------------
The project's limitations text says the smallest force-bearing feature is ground
clearance, not vehicle length, and that it is unresolved. warpmpm ships
`Solver.add_cdf_collider`, a CPIC thin-boundary collider whose docstring cites Hu et al.
2018 Section 5, and CPIC is the standard answer to thin features. The obvious move is to
reach for it.

That move is wrong, for three reasons, and this script exists so the first one cannot be
argued from intuition.

  1. CATEGORY ERROR. CPIC severs particle-node transfers across a zero-thickness sheet.
     That removes the need to RESOLVE A WALL. Ground clearance is a GAP, not a wall.
     Flow through a gap still needs grid cells across the gap no matter what the collider
     is made of, and warpmpm's quadratic B-spline transfer stencil is 3 cells wide, so a
     particle in the gap only has a stencil contained within the gap once the gap spans
     3 cells. This script computes how far the g64 baseline is from that.

  2. CLOSED HULL. Every CDF entry point specifies an OPEN oriented mid-surface. This
     script counts boundary edges to show the canonical hull is closed.

  3. KINEMATIC-ONLY (the decisive one, and not checkable here). `rigid_g2p_accumulate`
     (mpm_utils.py:1370-1412) gathers grid_v_out with NO CPIC masking, and
     `cdf_reaction_force` is only zeroed and read out, never applied to a body. A CDF
     collider is pose-driven by `set_cdf_pose`; it cannot be attached to a free rigid
     body. Attaching a sheet to the hull would block the hull's p2g deposits while
     leaving its g2p gather unmasked, which is momentum non-conserving.

Read-only. No solver, no GPU, no trimesh. numpy only.

Run with the venv interpreter, the system python3 has no numpy:
    /Users/josie/.venvs/canitford-mpm/bin/python3 analysis/verify_cpic_ground_clearance.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
PLY = REPO / "vehicle_geometry_research" / "yaris_coarse_v1l_watertight.ply"

# From renders/yaris_render_s1/sim_standing.py.
#   :82  lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)
#   :84  dx  = grid.dx = lim / n_grid
#   :85  h   = dx / 2.0     (particle spacing)
DEPTH_CANON = 0.30
STENCIL_CELLS = 3  # quadratic B-spline support, mpm_utils.py:1396-1400


def read_ply(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Parse a binary_little_endian PLY with float32 xyz verts and uchar+int32 faces."""
    raw = path.read_bytes()
    marker = b"end_header\n"
    end = raw.find(marker)
    if end < 0:
        raise SystemExit(f"{path}: no end_header, not a PLY this parser handles")
    header = raw[:end].decode("ascii", "replace")
    body_at = end + len(marker)

    if "binary_little_endian" not in header:
        raise SystemExit(f"{path}: not binary_little_endian; parser would misread it")

    n_vert = n_face = 0
    for line in header.splitlines():
        f = line.split()
        if len(f) >= 3 and f[0] == "element" and f[1] == "vertex":
            n_vert = int(f[2])
        elif len(f) >= 3 and f[0] == "element" and f[1] == "face":
            n_face = int(f[2])
    if not n_vert:
        raise SystemExit(f"{path}: no vertex element in header")

    verts = np.frombuffer(raw, dtype="<f4", count=n_vert * 3,
                          offset=body_at).reshape(n_vert, 3).astype(np.float64)

    # faces: uchar count + count*int32. Assume all triangles, then verify.
    face_at = body_at + n_vert * 3 * 4
    rec = np.dtype([("n", "u1"), ("v", "<i4", 3)])
    faces_raw = np.frombuffer(raw, dtype=rec, count=n_face, offset=face_at)
    if not np.all(faces_raw["n"] == 3):
        raise SystemExit(f"{path}: not all faces are triangles; parser assumes tris")
    return verts, faces_raw["v"].astype(np.int64)


def edge_stats(faces: np.ndarray) -> dict:
    """Boundary and non-manifold edge counts, from face adjacency alone."""
    e = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    e = np.sort(e, axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    return {
        "unique_edges": int(counts.size),
        "boundary_edges": int((counts == 1).sum()),  # an OPEN mesh has these
        "manifold_edges": int((counts == 2).sum()),
        "nonmanifold_edges": int((counts > 2).sum()),
    }


def underbody_clearance(verts: np.ndarray, n_cols: int = 120) -> dict:
    """Lowest point of the body over the central longitudinal strip between the wheels.

    DEFINITION MATTERS AND IS STATED, NOT ASSUMED. The wheels reach the ground, so the
    raw min z of the whole hull is ~0 and is NOT the clearance. We take the central
    band in y (|y - y_mid| < 0.30 * width, i.e. the middle 60 percent, which lies inside
    the wheel tracks), bin it into columns in x, take the minimum z per column, and
    report the distribution. The clearance is reported as the MEDIAN of those column
    minima, with the 10th percentile alongside as the pessimistic figure.
    """
    z0 = verts[:, 2].min()
    v = verts.copy()
    v[:, 2] -= z0  # canonicalize: floor at z = 0, as sim_standing.py:20-23 does

    y_mid = 0.5 * (v[:, 1].min() + v[:, 1].max())
    width = v[:, 1].max() - v[:, 1].min()
    central = np.abs(v[:, 1] - y_mid) < 0.30 * width
    vc = v[central]

    x_lo, x_hi = vc[:, 0].min(), vc[:, 0].max()
    # trim the extreme 10 percent at each end: bumpers overhang and are not underbody
    span = x_hi - x_lo
    keep = (vc[:, 0] > x_lo + 0.10 * span) & (vc[:, 0] < x_hi - 0.10 * span)
    vc = vc[keep]

    # np.ptp(arr), not arr.ptp(): the method was removed in numpy 2.0
    idx = np.clip(((vc[:, 0] - vc[:, 0].min())
                   / max(float(np.ptp(vc[:, 0])), 1e-12) * (n_cols - 1)).astype(int),
                  0, n_cols - 1)
    mins = np.full(n_cols, np.inf)
    np.minimum.at(mins, idx, vc[:, 2])
    mins = mins[np.isfinite(mins)]

    return {
        "n_columns": int(mins.size),
        "clearance_median": float(np.median(mins)),
        "clearance_p10": float(np.percentile(mins, 10)),
        "clearance_min": float(mins.min()),
        "central_band_frac": float(central.mean()),
    }


def main() -> int:
    if not PLY.exists():
        print(f"MISSING: {PLY}")
        return 1

    verts, faces = read_ply(PLY)
    ext = verts.max(0) - verts.min(0)

    print("# Canonical hull")
    print(f"  file          {PLY.relative_to(REPO)}")
    print(f"  vertices      {len(verts)}")
    print(f"  faces         {len(faces)}")
    print(f"  extent (m)    x={ext[0]:.6f}  y={ext[1]:.6f}  z={ext[2]:.6f}")

    es = edge_stats(faces)
    print("\n# Blocker 2: is the hull open (a mid-surface) or closed?")
    for k, v in es.items():
        print(f"  {k:<20} {v}")
    closed = es["boundary_edges"] == 0
    print(f"  -> {'CLOSED' if closed else 'OPEN'}. "
          f"{'CDF wants an OPEN oriented mid-surface, so the canonical hull does not qualify.' if closed else 'Open, so a CDF sheet is at least geometrically admissible.'}")

    cl = underbody_clearance(verts)
    gap = cl["clearance_median"]
    print("\n# Blocker 1: ground clearance as a GAP, and how many cells span it")
    print(f"  columns sampled          {cl['n_columns']}")
    print(f"  clearance, median (m)    {gap:.6f}   <-- used below")
    print(f"  clearance, p10 (m)       {cl['clearance_p10']:.6f}")
    print(f"  clearance, min (m)       {cl['clearance_min']:.6f}")

    # AXIS TRAP, verified live 2026-08-07. sim_standing.py:82 reads
    #   lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)
    # but ext there is VehicleBody.extent AFTER load_vehicle(up="z") permutes axes, so
    # the driver's ext[1] is this PLY's x (the 4.28 m LENGTH), not its y. Taking the
    # PLY axes at face value gives lim = 3.5*4.2826 = 14.989 m, which is wrong by 59
    # percent and silently rescales every dx below. Anchor on the recorded value
    # instead of re-deriving it from an assumed axis order.
    lim_recorded = None
    inv = REPO / "data" / "all_runs_inventory.csv"
    if inv.exists():
        import csv
        for r in csv.DictReader(inv.open()):
            if r.get("run") == "g64_m1100":
                lim_recorded = float(r["grid_lim"]) if "grid_lim" in r \
                    else float(r["dx"]) * 64
                break

    lim_naive = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * DEPTH_CANON))
    lim_permuted = float(max(2.2 * ext[0], 3.5 * ext[1], 6.0 * DEPTH_CANON))
    lim = lim_recorded if lim_recorded else lim_permuted

    print(f"\n  lim, PLY axes at face value   {lim_naive:.9f}  (WRONG, see AXIS TRAP)")
    print(f"  lim, driver axis order        {lim_permuted:.9f}  (= 2.2 * x-extent)")
    if lim_recorded:
        agree = abs(lim_permuted - lim_recorded) < 1e-6
        print(f"  lim, as-run (inventory g64)   {lim_recorded:.9f}  "
              f"{'MATCHES' if agree else 'DISAGREES, investigate'}")
    print(f"  -> using lim = {lim:.9f} m")

    print(f"\n{'n_grid':>7} {'dx (m)':>10} {'h=dx/2':>10} {'cells/gap':>10} "
          f"{'particle layers':>16}  status")
    print("-" * 78)
    for n_grid in (48, 64, 96, 128, 192, 256, 384):
        dx = lim / n_grid
        cells = gap / dx
        if cells >= STENCIL_CELLS:
            status = "stencil fits inside the gap"
        elif cells >= 2.0:
            status = "gap resolved, stencil still straddles it"
        elif cells >= 1.0:
            status = "sub-stencil, gap barely exists on the grid"
        else:
            status = "gap is smaller than one cell"
        mark = "  <-- BASELINE" if n_grid == 64 else ""
        print(f"{n_grid:>7} {dx:>10.6f} {dx / 2:>10.6f} {cells:>10.3f} "
              f"{gap / (dx / 2):>16.2f}  {status}{mark}")

    print(f"\n  Sensitivity to the clearance definition (dx at g64 = {lim / 64:.6f} m):")
    for name, val in (("median", gap), ("p10", cl["clearance_p10"]),
                      ("min", cl["clearance_min"])):
        print(f"    clearance {name:<7} = {val:.6f} m -> {val / (lim / 64):.3f} cells "
              f"at g64, needs n_grid >= {lim * 2.0 / val:.0f} for 2 cells")

    need2 = lim * 2.0 / gap
    need3 = lim * STENCIL_CELLS / gap
    print(f"\n  n_grid for 2 cells across the gap:  >= {need2:.1f}  "
          f"(~{(need2 / 64) ** 3:.0f}x the g64 cell count)")
    print(f"  n_grid for a {STENCIL_CELLS}-cell stencil inside:  >= {need3:.1f}  "
          f"(~{(need3 / 64) ** 3:.0f}x the g64 cell count)")

    print("\n# Verdict")
    print("  CPIC does not change any number in the table above. It makes a thin WALL")
    print("  watertight; it does not put cells inside a GAP. The clearance is unresolved")
    print("  at g64 and stays unresolved under CPIC. Combined with the closed hull and")
    print("  with CDF colliders being kinematic-only (rigid_g2p_accumulate applies no CPIC")
    print("  masking, and cdf_reaction_force is never applied to a body), item 4 should be")
    print("  closed as assessed-and-rejected, not attempted.")
    print("\n  This is a LIMITATION to state honestly in the paper, not a defect to fix.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
