"""
Measure the ENCLOSED volume of an FE vehicle mesh by voxel flood fill, and in
doing so measure how ill-defined that quantity is.

WHY THIS EXISTS
  The project's hull says the Yaris displaces 3.542739 m^3. A voxel remesh of the
  same FE model says 5.77 to 5.98 m^3, a factor of 1.63 to 1.69, with no voxel
  size converging to the hull value. Displaced volume sets buoyancy and sets
  realized_rho, so a 63 percent disagreement is not cosmetic.

WHY THE TWO DISAGREE, AND WHY NEITHER IS SIMPLY WRONG
  A car is not a closed body. It has a grille, wheel wells, an open underbody and
  panel gaps. "The volume it displaces" is therefore a MODELLING CHOICE about
  which openings count as sealed, not a property you can read off the geometry.
  This script makes that explicit: flood fill from outside at a given voxel size,
  and anything the water cannot reach is counted as displaced. Coarse voxels seal
  small openings and give a large volume; fine voxels leak through them and give
  a small one. The SPREAD across voxel size IS the uncertainty.
"""
import sys
import numpy as np
from collections import deque

obj_path = sys.argv[1]
sizes = [float(x) for x in sys.argv[2].split(",")]
label = sys.argv[3] if len(sys.argv) > 3 else "vehicle"

V, F = [], []
for line in open(obj_path):
    if line.startswith("v "):
        V.append([float(x) for x in line.split()[1:4]])
    elif line.startswith("f "):
        idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
        for k in range(1, len(idx) - 1):
            F.append((idx[0], idx[k], idx[k + 1]))
V = np.asarray(V, dtype=np.float64)
F = np.asarray(F, dtype=np.int64)
print(f"{label}: {len(V):,} verts  {len(F):,} triangles")

lo, hi = V.min(0), V.max(0)
bbox_vol = float(np.prod(hi - lo))
print(f"bbox {np.round(hi-lo,4)}  = {bbox_vol:.4f} m3")

for h in sizes:
    pad = 2
    dims = np.ceil((hi - lo) / h).astype(int) + 2 * pad + 1
    if dims.prod() > 90e6:
        print(f"voxel {h}: grid {dims} too large, skipped"); continue
    occ = np.zeros(dims, dtype=bool)

    # rasterise every triangle by barycentric sampling at ~half-voxel spacing
    A, B, C = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    e1, e2 = B - A, C - A
    area2 = np.linalg.norm(np.cross(e1, e2), axis=1)
    n_s = np.clip(np.ceil(np.sqrt(area2) / (0.5 * h)).astype(int), 1, 64)
    for ns in np.unique(n_s):
        sel = n_s == ns
        a, u, v = A[sel], e1[sel], e2[sel]
        ss = np.linspace(0.0, 1.0, ns + 1)
        gu, gv = np.meshgrid(ss, ss, indexing="ij")
        m = (gu + gv) <= 1.0
        gu, gv = gu[m], gv[m]
        pts = (a[:, None, :] + gu[None, :, None] * u[:, None, :]
               + gv[None, :, None] * v[:, None, :]).reshape(-1, 3)
        ijk = np.floor((pts - lo) / h).astype(int) + pad
        np.clip(ijk, 0, np.array(dims) - 1, out=ijk)
        occ[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True

    # flood fill the free space from the padded boundary
    free = ~occ
    seen = np.zeros(dims, dtype=bool)
    q = deque()
    for ax in range(3):
        for end in (0, dims[ax] - 1):
            sl = [slice(None)] * 3
            sl[ax] = end
            blk = free[tuple(sl)]
            ii, jj = np.nonzero(blk)
            for p, qq in zip(ii, jj):
                c = [0, 0, 0]
                c[ax] = end
                rest = [k for k in range(3) if k != ax]
                c[rest[0]] = p; c[rest[1]] = qq
                t = tuple(c)
                if not seen[t]:
                    seen[t] = True; q.append(t)
    nbr = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    while q:
        x, y, z = q.popleft()
        for dx, dy, dz in nbr:
            a2, b2, c2 = x+dx, y+dy, z+dz
            if 0 <= a2 < dims[0] and 0 <= b2 < dims[1] and 0 <= c2 < dims[2]:
                if free[a2, b2, c2] and not seen[a2, b2, c2]:
                    seen[a2, b2, c2] = True; q.append((a2, b2, c2))

    enclosed = int((~seen).sum())          # shell voxels plus unreachable interior
    vol = enclosed * h ** 3
    print(f"voxel {h:5.3f}  grid {tuple(dims)}  enclosed {vol:8.4f} m3  "
          f"= {100*vol/bbox_vol:5.1f}% of bbox   shell {int(occ.sum()):>9,}")
