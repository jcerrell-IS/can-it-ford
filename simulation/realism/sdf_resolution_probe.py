"""Does the SDF's 11.8 percent volume deficit go away with SDF resolution?

WHY THIS EXISTS
---------------
The Step 2 resolution study found that the collider the kernel actually collides against
is not the hull: the trilinearly interpolated res=48 SDF encloses 3.0587 m^3 against the
3.466632 m^3 decimated mesh it was built from, -11.76 percent, and -13.66 percent against
the canonical 3.542739 m^3. That was measured on the real artifact and is converged across
a 6.7x integration-spacing sweep, so it is not a measurement artifact. What it does NOT
establish is whether the deficit is a RESOLUTION effect that a finer SDF would remove, or
something structural.

A res=96 rebuild through the engine was attempted on Vista and LOST TO AN IDEV TIMEOUT
after 86 minutes. The estimate that sent it there was mine and it was wrong: I timed
`_winding_number` at 266 pts/s on a 4,000-point batch and extrapolated linearly to
884,736 points. That extrapolation is invalid. A dense points-by-faces array at that size
would be 279 TB, so the routine must chunk internally, and it goes memory-bandwidth bound
rather than holding the small-batch rate. Never size an HPC allocation from a
cache-resident microbenchmark.

WHAT THIS DOES INSTEAD
----------------------
Reproduces the engine's SDF construction locally and cheaply, and sweeps res. It costs
zero SUs and runs on the laptop.

  grid      identical to `build_sdf`: cubic, cell = span/(res-1-2*margin_cells),
            L = cell*(res-1), origin = centre - L/2. Reproduced from source so the
            comparison is against the same geometry, not a lookalike.
  distance  scipy cKDTree over a dense surface sampling, which is exactly what the
            engine's `_unsigned_distance` does.
  sign      trimesh's `contains`, NOT the generalized winding number. This is the
            substitution that makes it cheap, and it is the only deliberate difference.

THE CONTROL THAT MAKES THE SUBSTITUTION ADMISSIBLE
--------------------------------------------------
res=48 is run first and must reproduce 3.0587 m^3, the value measured on the engine's own
`yaris_sdf_r48_v2.npz`. If it does, the sign substitution is verified inert and the rest
of the sweep can be trusted. If it does not, the sweep is reporting a different object and
must be thrown away rather than interpreted.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ENGINE_R48_VOLUME = 3.058270      # measured on yaris_sdf_r48_v2.npz, 2026-08-13
CANON_VOLUME = 3.542739


def sample_surface(verts, faces, spacing):
    """Dense point sampling of the mesh surface, matching the engine's approach."""
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    ab, ac = b - a, c - a
    area = 0.5 * np.linalg.norm(np.cross(ab, ac), axis=1)
    n = np.maximum(1, np.ceil(np.sqrt(area) / spacing).astype(int))
    pts = [a, b, c]
    for k in np.unique(n):
        m = n == k
        if k < 2:
            continue
        u, v = np.meshgrid(np.linspace(0, 1, k + 1), np.linspace(0, 1, k + 1), indexing="ij")
        u, v = u.ravel(), v.ravel()
        keep = (u + v) <= 1.0
        u, v = u[keep], v[keep]
        pts.append((a[m][:, None, :] + u[None, :, None] * ab[m][:, None, :]
                    + v[None, :, None] * ac[m][:, None, :]).reshape(-1, 3))
    return np.concatenate(pts, axis=0)


def build_sdf_local(verts, faces, res, margin_cells=4.0):
    """Engine-identical grid, cKDTree distance, trimesh sign."""
    from scipy.spatial import cKDTree
    import trimesh

    lo, hi = verts.min(axis=0), verts.max(axis=0)
    centre = 0.5 * (lo + hi)
    span = float((hi - lo).max())
    cell = span / (res - 1 - 2 * margin_cells)          # build_sdf, verbatim
    L = cell * (res - 1)
    origin = centre - 0.5 * L
    axes = [origin[d] + cell * np.arange(res) for d in range(3)]
    X, Y, Z = np.meshgrid(axes[0], axes[1], axes[2], indexing="ij")
    pts = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)

    tree = cKDTree(sample_surface(verts, faces, 0.4 * cell))
    unsigned, _ = tree.query(pts, workers=-1)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    inside = mesh.contains(pts)
    signed = np.where(inside, -unsigned, unsigned).reshape(res, res, res)
    return signed.astype(np.float64), origin.astype(np.float64), float(cell)


def enclosed_volume(vals, origin, cell, spacing=0.02):
    """Volume inside the TRILERP zero-isosurface, i.e. the body the kernel actually sees.

    Not a count of negative grid cells. The collide kernel trilinearly interpolates
    (mpm_solver_warp.py:2711 queries `sd = sdf_trilerp(...)`), so the interpolated zero
    level is the real boundary and it is NOT the same surface as a nearest-node
    classification: on this mesh they differ by 15 percent.
    """
    res = vals.shape[0]
    ext = (res - 1) * cell
    n = int(math.ceil(ext / spacing))
    step = ext / n
    ax = [origin[k] + (np.arange(n) + 0.5) * step for k in range(3)]
    Y, Z = np.meshgrid(ax[1], ax[2], indexing="ij")
    yz = np.stack([Y.ravel(), Z.ravel()], axis=1)
    tot = 0
    for xi in ax[0]:
        body = np.empty((len(yz), 3))
        body[:, 0] = xi
        body[:, 1:] = yz
        f = (body - origin) / cell
        i0 = np.clip(np.floor(f).astype(int), 0, res - 2)
        t = f - i0
        v = np.zeros(len(body))
        for dx_ in (0, 1):
            for dy_ in (0, 1):
                for dz_ in (0, 1):
                    w = ((t[:, 0] if dx_ else 1 - t[:, 0])
                         * (t[:, 1] if dy_ else 1 - t[:, 1])
                         * (t[:, 2] if dz_ else 1 - t[:, 2]))
                    v += w * vals[i0[:, 0] + dx_, i0[:, 1] + dy_, i0[:, 2] + dz_]
        tot += int((v <= 0.0).sum())
    return tot * step ** 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ply", required=True)
    ap.add_argument("--res", default="48,64,80,96")
    ap.add_argument("--spacing", type=float, default=0.02)
    args = ap.parse_args()

    import time
    import hull_sdf as H

    verts, faces = H.read_ply_binary(args.ply)
    span = float((verts.max(axis=0) - verts.min(axis=0)).max())
    dv, df = H.cluster_decimate(verts, faces, span * 0.015)
    mesh_vol = H.mesh_volume(dv, df)
    print(f"decimated mesh: {len(df)} faces, volume {mesh_vol:.6f} m^3 "
          f"({100 * (mesh_vol - CANON_VOLUME) / CANON_VOLUME:+.3f}% vs canonical)\n")
    print(f"{'res':>5}{'cell_m':>10}{'cells_across_width':>20}{'V_trilerp':>12}"
          f"{'vs mesh':>10}{'vs canon':>10}{'secs':>8}")
    for res in [int(r) for r in args.res.split(",")]:
        t0 = time.time()
        vals, origin, cell = build_sdf_local(dv, df, res)
        V = enclosed_volume(vals, origin, cell, args.spacing)
        wide = float(dv[:, 1].max() - dv[:, 1].min()) / cell
        print(f"{res:>5}{cell:>10.5f}{wide:>20.1f}{V:>12.6f}"
              f"{100 * (V - mesh_vol) / mesh_vol:>9.2f}%"
              f"{100 * (V - CANON_VOLUME) / CANON_VOLUME:>9.2f}%{time.time() - t0:>8.1f}",
              flush=True)
        if res == 48:
            d = 100 * (V - ENGINE_R48_VOLUME) / ENGINE_R48_VOLUME
            verdict = "SIGN SUBSTITUTION VERIFIED INERT" if abs(d) < 2.0 else \
                      "MISMATCH: this sweep measures a DIFFERENT object, discard it"
            print(f"      control vs engine's own r48 ({ENGINE_R48_VOLUME:.6f}): "
                  f"{d:+.2f}%  -> {verdict}", flush=True)


if __name__ == "__main__":
    main()
