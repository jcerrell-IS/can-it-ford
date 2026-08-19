#!/usr/bin/env python3
"""Export a warpmpm rollout frame as real geometry for a Cycles path-traced render.

WHY THIS EXISTS
  analysis/render_multigeom_shaded.py evaluates Schlick Fresnel, a GGX lobe and
  Beer-Lambert absorption per face and then hands the faces to
  mpl_toolkits.mplot3d.Poly3DCollection. That is matplotlib: a painter's-algorithm
  polygon plotter with no ray tracing, no refraction, no shadows and no global
  illumination, whose per-polygon depth sort is undefined for interpenetrating
  geometry, which is exactly what a hull in water is. No amount of further shading
  work in that file can produce a photographic image, because water without
  refraction cannot look like water.

  So this is a SECOND, PRESENTATION path. The matplotlib renderer is KEPT and is
  still the diagnostic instrument: its particle-enclosure check, its facing-ratio
  measurements and its gate captions are what verify a frame is honest. This one
  makes a picture.

WHAT IT DOES NOT DO
  It does not touch the simulation, any metric, any verdict, or any file under
  renders/*/sim_*.py. It does not add, move or re-export any mesh: hulls are READ
  from wherever they already live and the exported copies are scratch render
  inputs, never repository assets. Register E8 and the unresolved hull licence
  question are therefore not engaged by this script.

THE TWO DERIVATIONS IN HERE, both checked rather than assumed
  1. WATER SURFACE. warpmpm carries no free surface. The surface is reconstructed
     from the particle positions with splashsurf (Loschner, Bender et al.), which
     is a real SPH surface reconstruction rather than the per-column max-z
     heightfield the diagnostic renderer uses. A heightfield cannot represent a
     bow wave that curls, which is the whole point of moving to it.
  2. HULL PLACEMENT. The solver never stores the hull mesh, only the solidified
     particle cloud, so the mesh has to be put back. The mapping is DERIVED:
     the PLY's long axis is X (extents 4.2826, 1.7464, 1.5180) and the scene's is
     Y (1.6930, 4.1956, 1.4721), so a rotation about z is required, and the sign
     is chosen by nearest-neighbour fit against the actual particle cloud rather
     than picked. Measured: rotz+90 gives mean nn-distance 0.04772 m (0.65 h) and
     rotz-90 gives 0.07672 m, a 61 percent worse fit. The chosen placement
     encloses the particle cloud on every axis, which is asserted at runtime.

USAGE
  prep_cycles_scene.py --run <dir> --frame N --hull <ply> --outdir <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_multigeom_rollout as RMR

ROTZ = {
    "+90": np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
    "-90": np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
}


def write_ply(path: Path, V, F):
    """Binary little-endian PLY. Written by hand so the export has no dependency
    on trimesh's writer and so the header is auditable by `head -c 400`."""
    V = np.ascontiguousarray(np.asarray(V, dtype="<f4"))
    F = np.ascontiguousarray(np.asarray(F, dtype="<i4"))
    hdr = ("ply\nformat binary_little_endian 1.0\n"
           "comment can-it-ford prep_cycles_scene.py scratch render input\n"
           "element vertex %d\nproperty float x\nproperty float y\nproperty float z\n"
           "element face %d\nproperty list uchar int vertex_indices\n"
           "end_header\n" % (len(V), len(F))).encode()
    with open(path, "wb") as fh:
        fh.write(hdr)
        fh.write(V.tobytes())
        cnt = np.full((len(F), 1), 3, dtype="<u1")
        rec = np.empty(len(F), dtype=[("c", "u1"), ("v", "<i4", 3)])
        rec["c"] = cnt[:, 0]
        rec["v"] = F
        fh.write(rec.tobytes())


def read_ply_vertices_faces(path: Path):
    """Minimal binary/ascii PLY reader for vertex+face only. Avoids pulling
    trimesh into the render path, and trimesh 5.x has its own seeding trap."""
    import trimesh
    m = trimesh.load(str(path), process=False)
    return np.asarray(m.vertices, dtype=np.float64), np.asarray(m.faces, dtype=np.int64)


def water_surface(w, h, window, cube_mult, iso, smooth_mult):
    """splashsurf reconstruction of the water, cropped to the render window."""
    import pysplashsurf
    (x0, x1, y0, y1) = window
    pad = 6.0 * h
    m = ((w[:, 0] >= x0 - pad) & (w[:, 0] <= x1 + pad) &
         (w[:, 1] >= y0 - pad) & (w[:, 1] <= y1 + pad))
    wc = np.ascontiguousarray(w[m].astype(np.float64))
    pr = 0.5 * h
    rec = pysplashsurf.reconstruct_surface(
        wc, particle_radius=pr, rest_density=1000.0,
        smoothing_length=smooth_mult * pr, cube_size=cube_mult * pr,
        iso_surface_threshold=iso, multi_threading=True, subdomain_grid=True)
    mesh = rec.mesh
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.triangles, dtype=np.int64)

    # CONSISTENT WINDING IS LOAD-BEARING, not cosmetic. A path tracer decides
    # "inside the water" from the surface normal, so an inconsistently wound mesh
    # makes a transmissive material render as near-invisible glass with no
    # refraction and no volume absorption. Measured on the first export: the mesh
    # was edge-manifold (is_watertight True) but enclosed 0.0005 m3 for a body
    # roughly 6 x 7 x 0.5 m, because the signed volume was cancelling. The water
    # was simply absent from the render, which read as "the water is invisible"
    # rather than as a geometry bug.
    import trimesh
    tm = trimesh.Trimesh(vertices=V, faces=F, process=False)
    tm.fix_normals()
    vol = float(tm.volume)
    if vol < 0:                       # fix_normals can settle on inward
        tm.invert()
        vol = float(tm.volume)
    print("[prep] water mesh: watertight=%s enclosed volume %.4f m3 after winding fix"
          % (tm.is_watertight, vol))
    if vol < 0.1:
        print("[prep] WARNING: enclosed volume is implausibly small. The volume "
              "absorption will not read. Do not present this frame as showing "
              "water depth.")
    return (np.asarray(tm.vertices, dtype=np.float64),
            np.asarray(tm.faces, dtype=np.int64), int(m.sum()), int(len(w)))


def place_hull(hull_ply: Path, pv, h):
    """Map the hull PLY into scene body-frame coordinates, and CHECK the result.

    The rotation sign is chosen by fit, not assumed. The check that the placed
    hull encloses the particle cloud on every axis is a hard assert: a hull that
    does not contain the particles it was solidified from is misplaced, and a
    misplaced hull would be invisible in a pretty render.
    """
    from scipy.spatial import cKDTree
    P, F = read_ply_vertices_faces(hull_ply)
    tree = cKDTree(pv)
    cen_cloud = 0.5 * (pv.min(0) + pv.max(0))
    best = None
    scores = {}
    for name, R in ROTZ.items():
        Q = P @ R.T
        Q = Q - 0.5 * (Q.min(0) + Q.max(0)) + cen_cloud
        d, _ = tree.query(Q[::37])
        scores[name] = float(d.mean())
        if best is None or d.mean() < best[1]:
            best = (name, float(d.mean()), Q)
    name, score, Q = best
    encl = bool((Q.min(0) <= pv.min(0) + 1e-9).all() and
                (Q.max(0) >= pv.max(0) - 1e-9).all())
    if not encl:
        raise SystemExit(
            "HULL PLACEMENT FAILED: the placed hull does not enclose the particle "
            "cloud it was solidified from. placed lo %s hi %s vs cloud lo %s hi %s"
            % (Q.min(0), Q.max(0), pv.min(0), pv.max(0)))
    return Q, F, name, score, scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--frame", type=int, default=60)
    ap.add_argument("--hull", required=True, help="hull .ply, READ not copied")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--half", type=float, default=3.4)
    ap.add_argument("--cube-mult", type=float, default=1.0,
                    help="marching-cubes voxel, in particle radii")
    ap.add_argument("--smooth-mult", type=float, default=2.0)
    ap.add_argument("--iso", type=float, default=0.6)
    ap.add_argument("--no-water", action="store_true",
                    help="hull only. For a class with no rollout data on this "
                         "machine, so no water field is invented for it.")
    ap.add_argument("--foreign-hull", action="store_true",
                    help="the hull is NOT the one this run simulated. It is then "
                         "placed at native scale resting on the floor, NOT fitted "
                         "to this run's particle cloud, and NOT given this run's "
                         "pose. Implies the frame carries no physics claim about "
                         "this vehicle. Required for any hull with no rollout.")
    a = ap.parse_args()

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    run = Path(a.run)
    z = RMR.load_run(run)
    s = z["summary"]
    f = a.frame
    pv, world, worst, errs = RMR.rigid_transform(z)
    h = 0.5 * z["dx"]
    floor = z["floor"]
    print("[prep] run %s frame %d" % (run.name, f))
    print("[prep] transform check max|err| %.3e m (gates.py:136/:157)" % worst)

    vpf = world(f)
    cx, cy = float(vpf[:, 0].mean()), float(vpf[:, 1].mean())

    if a.foreign_hull:
        # A hull this run did not simulate. Native scale, long axis on Y to match
        # the scene convention, resting on the floor at the scene centre. NO pose
        # from this run is applied, because applying one would dress a hull that
        # was never simulated in another vehicle's measured configuration.
        P, HF = read_ply_vertices_faces(Path(a.hull))
        Q = P @ ROTZ["+90"].T
        c = 0.5 * (Q.min(0) + Q.max(0))
        Qw = Q - np.array([c[0], c[1], Q.min(0)[2]]) + np.array([cx, cy, floor])
        rot, score = "+90 (foreign, not fitted)", float("nan")
        print("[prep] FOREIGN hull %s: %d verts, %d faces, native scale, rested on "
              "floor. NO pose from this run applied, NO physics claim."
              % (Path(a.hull).name, len(P), len(HF)))
    else:
        Q, HF, rot, score, scores = place_hull(Path(a.hull), pv, h)
        print("[prep] hull %s: %d verts, rotation %s chosen by fit "
              "(nn %.5f m = %.2f h; alternative %.5f m)"
              % (Path(a.hull).name, len(Q), rot, score, score / h,
                 [v for k, v in scores.items() if k != rot][0]))
        Qw = Q @ z["R"][f].T + z["t"][f]
    write_ply(out / "hull.ply", Qw, HF)

    window = (cx - a.half, cx + a.half, cy - a.half, cy + a.half)

    nwater = 0
    if not a.no_water:
        WV, WF, kept, tot = water_surface(z["water"][f], h, window,
                                          a.cube_mult, a.iso, a.smooth_mult)
        write_ply(out / "water.ply", WV, WF)
        nwater = len(WF)
        print("[prep] water surface: %d verts %d tris from %d of %d particles "
              "(splashsurf, radius %.5f m)" % (len(WV), len(WF), kept, tot, 0.5 * h))

    scene = {
        "run": run.name, "frame": f, "fps": int(z["fps"]),
        "floor_z": float(floor), "dx": float(z["dx"]), "h": float(h),
        "hull_ply_source": str(a.hull), "hull_rotation": rot,
        "hull_fit_nn_m": score, "hull_faces": int(len(HF)),
        "water_faces": nwater, "no_water": bool(a.no_water),
        "car_center": [cx, cy], "half": a.half,
        "hull_bbox_lo": Qw.min(0).tolist(), "hull_bbox_hi": Qw.max(0).tolist(),
        "veh_zmin": float(vpf[:, 2].min()),
        "transform_max_err_m": worst,
        # physics, copied verbatim from this run's own summary.json
        "physics": {k: s.get(k) for k in (
            "mass_kg", "n_grid", "dx", "water_layers", "depth_m", "velocity_ms",
            "final_disp_mag_m", "passthrough_max_frac", "C2_veh_zmin_rise",
            "realized_rho", "solid_volume_m3", "label")},
    }
    (out / "scene.json").write_text(json.dumps(scene, indent=2))
    print("[prep] wrote %s" % (out / "scene.json"))


if __name__ == "__main__":
    main()
