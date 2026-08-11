"""
yaris_sdf_smoke.py

NON-CANONICAL / EXPLORATORY. Nothing here feeds the 17 gated runs, the poster
or the paper. Branch claude/visual-physical-realism-trial-2026-08-11.

Points build_sdf_cached at the REAL canonical Yaris hull instead of the
4.66 x 1.79 x 1.44 m box that simulation/box_sdf_collider_setup.py:10 uses, and
reports what the SDF path actually produces from it.

WHY THIS IS A GEOMETRY SMOKE TEST AND NOT THE FULL COMPARISON
The dispatch asks for one smoke test against canonical g64. That comparison
cannot be run on this Mac and this script does not pretend to:
  - warp 1.16.0 in .venvs/canitford-mpm reports "CUDA not enabled in this build",
    devices ["cpu"] only, verified live 2026-08-11.
  - box_sdf_collider_setup.py:49 runs n_grid=288 over a 10 m domain, about 2.4e7
    grid cells, for 1.0 s at dt 1e-4 with 20 substeps. That is a GPU workload.
  - The canonical g64 runs are CUDA runs on Vista. A CPU-vs-GPU delta would
    confound the float-accumulation difference with the coupling-architecture
    difference, which is the thing being measured.
So this script measures ONLY what is honest to measure on CPU: that the real
hull loads through the SDF path, is watertight, and produces an SDF whose
geometry agrees with the hull the canonical runs used.

WHAT A DELTA HERE WOULD AND WOULD NOT MEAN
The canonical 17 use the material-8 FREE-RIGID path, a mass-weighted grid
velocity average with no force accumulator. This script uses the SDF COLLIDER
path, which accumulates a reaction wrench. Those are different coupling
architectures (register A-1), so agreement is not expected and disagreement is
not a bug. Per A-2 the SDF path's own buoyancy error against analytic is 7.3 to
7.7 percent, NOT 1.6 to 7.7; do not merge those ranges.

REFERENCE VALUE
Canonical hull volume is 3.542739 m3 (register E1, yaris_coarse_v1l_watertight.ply,
327,212 verts / 655,308 faces). That is the number this script checks against.
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import trimesh

from warpmpm.geometry import build_sdf_cached

HULL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vehicle_geometry_research",
    "yaris_coarse_v1l_watertight.ply",
)

# register E1. Do not recompute this from the mesh and call it a check; it is
# the independent reference the mesh is being checked AGAINST.
CANONICAL_HULL_M3 = 3.542739

SDF_RES = 96              # matches box_sdf_collider_setup.py:12
SDF_MARGIN_CELLS = 6.0    # matches :13
SDF_CACHE_DIR = "out/sdf_cache_yaris"


def main():
    print("NON-CANONICAL / EXPLORATORY smoke test, SDF collider path")
    print("hull:", HULL)
    if not os.path.exists(HULL):
        raise SystemExit("hull not found: %s" % HULL)

    t0 = time.time()
    mesh = trimesh.load(HULL, process=False)
    print("loaded in %.2f s: %d verts, %d faces"
          % (time.time() - t0, len(mesh.vertices), len(mesh.faces)))

    print("watertight:", mesh.is_watertight)
    vol = float(mesh.volume)
    delta_pct = 100.0 * (vol - CANONICAL_HULL_M3) / CANONICAL_HULL_M3
    print("volume: %.6f m3  (canonical %.6f m3, delta %+.4f percent)"
          % (vol, CANONICAL_HULL_M3, delta_pct))

    ext = mesh.bounding_box.extents
    print("bbox extents (m): %.4f %.4f %.4f" % (ext[0], ext[1], ext[2]))
    print("  NOTE the gated scene puts the hull's LONG AXIS ON Y "
          "(CLAUDE.md item 4c), so a (L,W,H) reading of these is wrong.")

    verts = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)

    t1 = time.time()
    sdf = build_sdf_cached(
        verts, faces,
        res=SDF_RES,
        margin_cells=SDF_MARGIN_CELLS,
        cache_dir=SDF_CACHE_DIR,
    )
    print("build_sdf_cached: res=%s cell=%.6f m  (%.1f s)"
          % (sdf.res, sdf.cell, time.time() - t1))

    print("RESULT: the real Yaris hull loads through the SDF collider path.")
    print("This is a geometry check only. It is NOT a coupling comparison "
          "against canonical g64, which needs GPU.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
