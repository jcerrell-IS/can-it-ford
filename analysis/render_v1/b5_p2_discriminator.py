"""B5: P-2 discriminator over all 90 frames, AABB versus posed-mesh contains.

Naive form is infeasible here. Measured on this machine: mesh.contains costs
~15 ms per point against the full 655,308-face mesh with embree ABSENT.
90 frames x 48,367 water particles = 4.35M tests = about 18 hours. That is why
the earlier attempt produced a header and no rows.

Restructured, without weakening the test:

  The posed mesh is a strict subset of its own axis-aligned bounding box, so any
  water particle inside the mesh is necessarily inside the AABB. Testing only
  AABB-inside particles therefore loses nothing. Within that set we subsample
  and scale, which makes column (ii) an UNBIASED estimator of the true
  mesh-inside percentage:

      mesh_pct[f] = aabb_pct[f] * (contains_hits / n_sampled)

  Binomial standard error on the inner fraction is reported per frame so the
  reader can see the noise floor rather than trust a bare number.

Column (i) is exact: every water particle is tested against the AABB.
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
N_PER_FRAME = 260


def main(seed=0):
    print("B5 P-2 DISCRIMINATOR: AABB versus POSED-MESH CONTAINS, 90 frames")
    print(f"    run = {RUN}")
    print(f"    trimesh.ray.has_embree = {trimesh.ray.has_embree}")
    print(f"    column (i)  AABB      : EXACT, all water particles every frame")
    print(f"    column (ii) mesh-inside: AABB-restricted, <= {N_PER_FRAME} sampled/frame, "
          f"scaled. Unbiased, SE reported.")
    print()

    d = np.load(NPZ)
    R = d["R"].astype(np.float64)
    t = d["t"].astype(np.float64)
    pv = d["veh_particles_vehframe"].astype(np.float64)
    off = T.run_offset(d)
    water = d["water"].astype(np.float64)
    nF, nW = water.shape[0], water.shape[1]

    Vv, F, _ = T.mesh_in_vehframe(None)
    static = trimesh.Trimesh(vertices=Vv, faces=F, process=False)
    print(f"    gate mesh: {len(F)} faces (FULL, per B3), watertight={static.is_watertight}")
    print("    containment tested in the VEHICLE frame against one static mesh, which is")
    print("    identical to posing the mesh per frame (the pose is rigid) but builds the")
    print("    spatial index once instead of 90 times.")
    print()

    rng = np.random.default_rng(seed)
    aabb_pct = np.zeros(nF)
    mesh_pct = np.zeros(nF)
    mesh_se = np.zeros(nF)
    t0 = time.time()

    print(f"    {'frame':>5}{'AABB %':>10}{'MESH %':>10}{'+/- SE':>9}{'n_aabb':>9}{'n_smp':>7}")
    for f in range(nF):
        vs = (pv + off) @ R[f].T + t[f]
        lo, hi = vs.min(0), vs.max(0)
        w = water[f]
        inside = np.all((w >= lo) & (w <= hi), axis=1)
        n_in = int(inside.sum())
        aabb_pct[f] = 100.0 * n_in / nW

        if n_in == 0:
            mesh_pct[f] = 0.0
            mesh_se[f] = 0.0
        else:
            cand = w[inside]
            k = min(N_PER_FRAME, n_in)
            sel = cand[rng.choice(n_in, k, replace=False)] if k < n_in else cand
            # Map the water into the VEHICLE frame instead of posing the mesh into the
            # scene. The pose is rigid, so containment is identical either way, but this
            # builds the 655k-face rtree ONCE instead of once per frame.
            sel_v = (sel - t[f]) @ R[f] - off
            hits = int(static.contains(sel_v).sum())
            p = hits / k
            mesh_pct[f] = aabb_pct[f] * p
            mesh_se[f] = aabb_pct[f] * np.sqrt(max(p * (1 - p), 0.0) / k)

        if f % 5 == 0 or f == nF - 1:
            print(f"    {f:>5}{aabb_pct[f]:>10.4f}{mesh_pct[f]:>10.4f}"
                  f"{mesh_se[f]:>9.4f}{n_in:>9}{min(N_PER_FRAME, n_in):>7}", flush=True)

    print()
    print(f"    elapsed {time.time()-t0:.0f} s")
    print(f"    AABB  frame0 {aabb_pct[0]:.4f}%   max {aabb_pct.max():.4f}% at f={int(aabb_pct.argmax())}"
          f"   rise above f0 {aabb_pct.max()-aabb_pct[0]:+.4f} pp")
    print(f"    MESH  frame0 {mesh_pct[0]:.4f}%   max {mesh_pct.max():.4f}% at f={int(mesh_pct.argmax())}"
          f"   rise above f0 {mesh_pct.max()-mesh_pct[0]:+.4f} pp")
    print(f"    MESH  mean SE across frames {mesh_se.mean():.4f} pp (noise floor)")
    print()
    rise_mesh = mesh_pct.max() - mesh_pct[0]
    if rise_mesh <= 3.0 * mesh_se.mean():
        print("    VERDICT: column (ii) is FLAT within noise. The P-2 failure is an")
        print("             AABB artifact, not tunnelling.")
    else:
        print("    VERDICT: column (ii) rises beyond the noise floor. Real penetration")
        print("             exists on top of the AABB artifact. Magnitude above.")
    np.savez("/Users/josie/can-it-ford/analysis/render_v1/b5_p2_series.npz",
             aabb_pct=aabb_pct, mesh_pct=mesh_pct, mesh_se=mesh_se)
    return aabb_pct, mesh_pct


if __name__ == "__main__":
    main()
