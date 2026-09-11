"""B2b: relative containment gate over FOUR candidate rotations.

The gate is RELATIVE, per AMENDMENT B: the source Rz must be the clear maximum.
An absolute threshold is not used, because upstream solidify_columns would put
wheel-well fill outside the surface by construction. These runs used
solidify_watertight (see B0a), but the relative test is valid either way.

B2a: trimesh.ray.has_embree is printed first. If False the particle set is
subsampled and that is stated.

B3: the gate runs against the FULL 655,308-face mesh. No decimation.

IMPLEMENTATION NOTE, and why this is not a shortcut.
The obvious form builds a rotated mesh per candidate. That is four 655k-face
meshes each with its own spatial index, and on this machine it was killed for
memory before producing a single row. The equivalent form below builds ONE mesh
and moves the particles instead:

    mesh_rot = (V @ rot.T) - shift(rot)
    p in mesh_rot  <=>  (p + shift(rot)) @ rot  in  mesh_raw

because q = v @ rot.T - shift  =>  v = (q + shift) @ rot, and rot is orthonormal.
The test is therefore identical, not approximated, and it builds one index.
shift(rot) is computed exactly as load_vehicle computes it: centre x and y on the
rotated bounding box, put the floor at z = 0.
"""
from __future__ import annotations

import sys
import time

import numpy as np
import trimesh

sys.path.insert(0, "/Users/josie/can-it-ford/analysis/render_v1")
import t1_car as T

RUN = "g64_m1100"
NPZ = f"/Users/josie/can-it-ford/renders/yaris_render_s1/{RUN}/rollout.npz"

RZ = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
ROT180 = np.array([[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]])

CANDIDATES = [
    ("source Rz    (x,y,z)->(-y,x,z)", RZ),
    ("Rz inverse   (x,y,z)->(y,-x,z)", RZ.T),
    ("identity                      ", np.eye(3)),
    ("180 about z  (x,y,z)->(-x,-y,z)", ROT180),
]


def main(n_sample=5000, seed=0):
    print("B2b FOUR-ROTATION RELATIVE GATE")
    print(f"    run = {RUN}")
    print(f"B2a trimesh.ray.has_embree = {trimesh.ray.has_embree}", flush=True)

    raw = trimesh.load(T.PLY, force="mesh")
    Vraw = np.asarray(raw.vertices, dtype=np.float64)
    mesh = trimesh.Trimesh(vertices=Vraw, faces=np.asarray(raw.faces), process=False)
    print(f"    single raw mesh: {len(mesh.faces)} faces, watertight={mesh.is_watertight}")
    print("    candidates evaluated by transforming PARTICLES into the raw frame,")
    print("    which is exactly equivalent and builds one spatial index.", flush=True)

    d = np.load(NPZ)
    pv = d["veh_particles_vehframe"].astype(np.float64)
    n_all = len(pv)

    if not trimesh.ray.has_embree:
        n = min(n_sample, n_all)
        rng = np.random.default_rng(seed)
        pts = pv[rng.choice(n_all, n, replace=False)]
        print(f"    embree ABSENT, so SUBSAMPLED to {n} of {n_all} solid particles "
              f"(seed={seed}). Stated per B2a.", flush=True)
    else:
        pts = pv
        print(f"    embree present, using all {n_all} particles.", flush=True)

    print()
    print(f"    {'candidate rotation':<33}{'frac inside':>13}{'seconds':>9}")
    results = []
    for name, rot in CANDIDATES:
        Vr = Vraw @ rot.T
        lo, hi = Vr.min(0), Vr.max(0)
        shift = np.array([(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2]])
        probe = (pts + shift) @ rot          # back into the raw mesh frame
        t0 = time.time()
        frac = float(mesh.contains(probe).mean())
        dt = time.time() - t0
        results.append((name, frac))
        print(f"    {name:<33}{frac:>13.4f}{dt:>9.1f}", flush=True)

    print()
    order = sorted(results, key=lambda r: -r[1])
    best, second = order[0], order[1]
    margin = best[1] - second[1]
    print(f"    MAX      : {best[0].strip()}  at {best[1]:.4f}")
    print(f"    RUNNER-UP: {second[0].strip()}  at {second[1]:.4f}")
    print(f"    MARGIN   : {margin:+.4f}")
    print()
    if best[0].startswith("source Rz") and margin > 0.05:
        print("    GATE PASS: source Rz is the clear maximum.")
    elif best[0].startswith("source Rz"):
        print(f"    GATE MARGINAL: source Rz wins by only {margin:.4f}. Report, do not rely.")
    else:
        print("    GATE FAIL: source Rz is NOT the maximum. STOP AND REPORT per B2b.")
    return results


if __name__ == "__main__":
    main()
