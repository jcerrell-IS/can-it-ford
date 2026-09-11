"""T4a and T4b.

T4a: sim_standing.py:100-103 builds the water lattice with np.arange(start, stop, h).
     A float stop that lands on a lattice boundary flips the count by one whole column.
T4b: P-2 per-frame series. Two independent membership tests on the SAME frames:
       AABB   : water inside the axis-aligned bounding box of the posed vehicle
       VOXEL  : water inside the vehicle's own pitch-h solid voxel set, the body the
                simulation actually integrated
     Frame 0 is pure geometry by construction. Any rise above frame 0 is penetration.
"""
from __future__ import annotations

import numpy as np

import t1_car as T


def t4a(d):
    h = float(d["h"]); dx = float(d["dx"]); lim = float(d["lim"])
    wall = 4.0 * dx
    start = wall + 0.5 * h
    stop = lim - wall - 0.5 * h
    print("T4a  WATER LATTICE FLOAT FRAGILITY")
    print(f"     dx={dx:.12f}  h={h:.12f}  wall=4dx={wall:.12f}")
    print(f"     start={start:.12f}  stop={stop:.12f}  span/h={(stop-start)/h:.9f}")
    print()
    print("     %-18s %8s %8s" % ("lim", "arange", "linspace"))
    for tag, L in [("stored float32", lim), ("independent rebuild", 9.421720),
                   ("float64 exact", 9.421742314)]:
        st = L - wall - 0.5 * h
        n_ar = len(np.arange(start, st, h))
        n_ls = int(np.floor((st - start) / h + 1e-9)) + 1
        print("     %-18s %8d %8d   (lim=%.9f)" % (tag, n_ar, n_ls, L))
    n = int(np.floor((stop - start) / h + 1e-9)) + 1
    xs = np.linspace(start, start + (n - 1) * h, n)
    print()
    print(f"     FIX: n = floor((stop-start)/h + eps) + 1 = {n}; np.linspace(start, start+(n-1)*h, n)")
    print(f"          columns per axis = {n}, water cells = {n}*{n}*layers")
    zs_n = int(np.floor((float(d['depth']) - 0.5 * h) / h + 1e-9)) + 1
    print(f"          z layers = {zs_n}, total = {n*n*zs_n} before carve; "
          f"stored n_water = {d['water'].shape[1]}")
    return n


def t4b(d, run):
    h = float(d["h"])
    R = d["R"].astype(np.float64); t = d["t"].astype(np.float64)
    pv = d["veh_particles_vehframe"].astype(np.float64)
    off = T.run_offset(d)
    water = d["water"].astype(np.float64)
    nF, nW = water.shape[0], water.shape[1]

    p0 = pv.min(0)
    vk = np.round((pv - p0) / h).astype(np.int64)
    span = vk.max(0) - vk.min(0) + 1
    occ = np.zeros(np.prod(span), dtype=bool)
    occ[np.ravel_multi_index(vk.T, span)] = True

    aabb = np.empty(nF); vox = np.empty(nF)
    for f in range(nF):
        vs = (pv + off) @ R[f].T + t[f]
        lo, hi = vs.min(0), vs.max(0)
        w = water[f]
        inside = np.all((w >= lo) & (w <= hi), axis=1)
        aabb[f] = 100.0 * inside.sum() / nW
        wv = (w - t[f]) @ R[f] - off
        k = np.round((wv - p0) / h).astype(np.int64)
        ok = np.all((k >= 0) & (k < span), axis=1)
        hit = np.zeros(nW, dtype=bool)
        if ok.any():
            hit[ok] = occ[np.ravel_multi_index(k[ok].T, span)]
        vox[f] = 100.0 * hit.sum() / nW
    return aabb, vox


if __name__ == "__main__":
    import sys
    runs = sys.argv[1:] or ["g64_m1100", "g64_m1609", "g64_m2337"]
    d0 = np.load(f"{runs[0]}/rollout.npz")
    t4a(d0)
    for run in runs:
        d = np.load(f"{run}/rollout.npz")
        aabb, vox = t4b(d, run)
        print()
        print(f"=== T4b P-2 SERIES  {run}   (percent of {d['water'].shape[1]} water particles)")
        print(f"    frame 0 baseline: AABB {aabb[0]:.4f}%   VOXEL {vox[0]:.4f}%")
        print("    f   AABB%   VOX%  |  f   AABB%   VOX%  |  f   AABB%   VOX%")
        for i in range(0, 30):
            row = []
            for j in (i, i + 30, i + 60):
                row.append(f"{j:3d} {aabb[j]:7.4f} {vox[j]:6.4f}")
            print("    " + " | ".join(row))
        print(f"    AABB  max {aabb.max():.4f}% at f={int(aabb.argmax())}   "
              f"rise above f0 = {aabb.max()-aabb[0]:+.4f}")
        print(f"    VOXEL max {vox.max():.4f}% at f={int(vox.argmax())}   "
              f"rise above f0 = {vox.max()-vox[0]:+.4f}")
