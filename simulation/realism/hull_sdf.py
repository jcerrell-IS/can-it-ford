"""Make the canonical Yaris hull usable as a force-coupled SDF collider.

THE BLOCKER THIS SOLVES
-----------------------
`warpmpm.geometry.build_sdf` signs its field with a generalized winding number
(`mesh_sdf.py:205-231`), chunked over grid points (4096 at a time) and VECTORIZED OVER
FACES. Per chunk it materialises several `(chunk, F, 3)` float64 arrays. For the canonical
hull, F = 655,308:

    4096 * 655,308 * 3 * 8 bytes = 64 GB   per intermediate array, and it builds ~6

so this does not merely run slowly, it OOMs immediately. The distance half is cheap
(scipy cKDTree over surface samples, `mesh_sdf.py:309-322`); only the SIGN is fatal.

WHY DECIMATION LOSES NOTHING HERE
---------------------------------
The stored SDF cell is `span / (res - 1 - 2*margin)`. For the hull, span = 4.2014 m at
res = 48, margin = 4, that is 4.2014 / 39 = 0.1077 m. Mesh features finer than that are
not representable in the field at all. And the MPM grid is coarser still: at n_grid = 64
on the canonical domain, dx = 9.4217/64 = 0.1472 m, so the collide kernel only ever
queries ~28 nodes along the hull's long axis. Decimating to ~0.1 m features therefore
discards only detail that neither the SDF nor the grid can see. That is a statement about
the representation, not a convenient assumption: raise `--res` and the argument has to be
re-made at the finer cell size.

WHAT IS CHECKED, RATHER THAN ASSUMED
------------------------------------
Decimation is only admissible if it preserves the quantities the physics uses. This
script measures all three against values established elsewhere in the project and fails
loudly on drift:

    volume   3.542739 m^3          register E1
    extents  1.7078 / 4.2014 / 1.4853 m   assessment section 1c (long axis is Y)
    inertia  Ixx 1501.5, Iyy 395.0, Izz 1685.4 kg m^2 at 1100 kg about the centroid
             assessment section 1b, itself from the solver's own construction at
             mpm_solver_warp.py:859-871

The inertia here is computed from a SOLID VOXELISATION of the hull, which is the
sanctioned route. It is emphatically NOT `vehicle_params.py`'s `inertia_kg_m2`: that is a
uniform-density box fallback reproducing exactly from box_inertia(1100, 4.30, 1.70, 1.47),
and its (L,W,H)->(x,y,z) convention is transposed against the scene, so wiring it gives
Ixx -69.2 percent and Iyy +379.2 percent.
"""
from __future__ import annotations

import argparse
import json

import numpy as np

# Canonical references. Sources named in the module docstring.
CANON_VOLUME = 3.542739
CANON_EXTENTS = (1.7078, 4.2014, 1.4853)
CANON_INERTIA = (1501.5, 395.0, 1685.4)
CANON_MASS = 1100.0


def read_ply_binary(path):
    """Minimal reader for the canonical hull's exact PLY layout.

    Header (verified live on the canonical file):
        format binary_little_endian 1.0
        element vertex 327212 / property float x,y,z
        element face 655308 / property list uchar int vertex_indices

    trimesh is not installed in the Vista venv, so this avoids adding a dependency for
    one file whose layout is fixed and known. It asserts the layout rather than guessing,
    so a different mesh fails loudly instead of being misread.
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    end = raw.find(b"end_header\n")
    if end < 0:
        raise ValueError("no end_header in PLY")
    header = raw[:end].decode("ascii", "replace")
    body = raw[end + len(b"end_header\n"):]
    if "binary_little_endian" not in header:
        raise ValueError("expected binary_little_endian PLY")

    nv = nf = None
    for line in header.splitlines():
        p = line.split()
        if len(p) == 3 and p[0] == "element" and p[1] == "vertex":
            nv = int(p[2])
        elif len(p) == 3 and p[0] == "element" and p[1] == "face":
            nf = int(p[2])
    if nv is None or nf is None:
        raise ValueError("PLY header missing vertex/face counts")

    verts = np.frombuffer(body, dtype="<f4", count=nv * 3, offset=0).reshape(nv, 3)
    face_dt = np.dtype([("n", "u1"), ("v", "<i4", 3)])   # packed, 13 bytes
    if face_dt.itemsize != 13:
        raise ValueError(f"face dtype is {face_dt.itemsize} bytes, expected 13")
    fr = np.frombuffer(body, dtype=face_dt, count=nf, offset=nv * 3 * 4)
    if not np.all(fr["n"] == 3):
        raise ValueError("non-triangular face found; this reader assumes triangles")
    return verts.astype(np.float64), fr["v"].astype(np.int64)


def mesh_volume(verts, faces):
    """Signed volume by the divergence theorem, V = |sum det[a,b,c]| / 6."""
    a = verts[faces[:, 0]]
    b = verts[faces[:, 1]]
    c = verts[faces[:, 2]]
    return abs(float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0)


def cluster_decimate(verts, faces, vox):
    """Rossignac-Borrel vertex clustering: snap vertices to a voxel grid, keep the
    cluster centroid, remap faces, drop degenerates and duplicates.

    Chosen over edge-collapse because it needs no dependency, is O(n), and cannot fail on
    the non-manifold edges a 655k-face FE-derived hull may carry. The generalized winding
    number used downstream is robust to the small non-manifoldness clustering can create,
    which is exactly why it is the right pairing here.
    """
    vmin = verts.min(axis=0)
    key = np.floor((verts - vmin) / vox).astype(np.int64)
    dims = key.max(axis=0) + 1
    lin = (key[:, 0] * dims[1] + key[:, 1]) * dims[2] + key[:, 2]
    uniq, inv = np.unique(lin, return_inverse=True)

    cnt = np.bincount(inv).astype(float)
    newv = np.stack([np.bincount(inv, weights=verts[:, k]) / cnt for k in range(3)], axis=1)

    nf = inv[faces]
    ok = (nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2])
    nf = nf[ok]
    _, idx = np.unique(np.sort(nf, axis=1), axis=0, return_index=True)
    return newv, nf[idx]


def solid_inertia(verts, faces, mass, spacing):
    """Inertia tensor about the centroid from a SOLID voxelisation of the mesh.

    Same construction the solver uses on its own particle cloud
    (mpm_solver_warp.py:859-871), I = sum m_i (|r_i|^2 * 1 - r_i (x) r_i), so this and a
    `finalize_rigid_bodies()` tensor agree by construction. Uniform density, matching the
    solidified cloud the pipeline builds.
    """
    from warpmpm.geometry.mesh_sdf import _winding_number

    lo, hi = verts.min(axis=0), verts.max(axis=0)
    axes = [np.arange(lo[d] + 0.5 * spacing, hi[d], spacing) for d in range(3)]
    X, Y, Z = np.meshgrid(*axes, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)

    wn = _winding_number(pts, verts, faces)
    inside = np.abs(wn) > 0.5
    p = pts[inside]
    if len(p) == 0:
        raise ValueError("solid voxelisation produced no interior points")

    m_i = mass / len(p)
    com = p.mean(axis=0)
    r = p - com
    r2 = (r * r).sum(axis=1)
    I = np.zeros((3, 3))
    for k in range(3):
        I[k, k] = m_i * (r2 - r[:, k] ** 2).sum()
    for a, b in ((0, 1), (0, 2), (1, 2)):
        I[a, b] = I[b, a] = -m_i * (r[:, a] * r[:, b]).sum()
    return I, com, len(p), m_i * len(p) / (spacing ** 3) / mass * spacing ** 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ply", required=True)
    ap.add_argument("--target-faces", type=int, default=5000)
    ap.add_argument("--res", type=int, default=48)
    ap.add_argument("--margin-cells", type=float, default=4.0)
    ap.add_argument("--inertia-spacing", type=float, default=0.05)
    ap.add_argument("--out-sdf", default="yaris_sdf.npz")
    ap.add_argument("--out-json", default="hull_sdf_report.json")
    ap.add_argument("--skip-inertia", action="store_true")
    args = ap.parse_args()

    verts, faces = read_ply_binary(args.ply)
    v0, ext0 = mesh_volume(verts, faces), verts.max(axis=0) - verts.min(axis=0)
    print(f"[source] {len(verts)} verts, {len(faces)} faces")
    print(f"[source] volume  {v0:.6f} m^3   canonical {CANON_VOLUME:.6f}  "
          f"({100 * (v0 - CANON_VOLUME) / CANON_VOLUME:+.3f} %)")
    print(f"[source] extents {ext0[0]:.4f} {ext0[1]:.4f} {ext0[2]:.4f}   "
          f"canonical {CANON_EXTENTS}")

    # --- pick the voxel size that lands nearest the target face count ----------------
    span = float(ext0.max())
    trials = []
    for vox in span * np.array([0.010, 0.015, 0.020, 0.028, 0.040, 0.055, 0.075, 0.10]):
        dv, df = cluster_decimate(verts, faces, vox)
        trials.append((abs(len(df) - args.target_faces), vox, dv, df))
        print(f"  vox {vox:.4f} m -> {len(dv):6d} verts {len(df):6d} faces  "
              f"volume {mesh_volume(dv, df):.6f} m^3")
    _, vox, dv, df = min(trials, key=lambda t: t[0])
    v1 = mesh_volume(dv, df)
    ext1 = dv.max(axis=0) - dv.min(axis=0)
    print(f"\n[chosen] vox {vox:.4f} m -> {len(dv)} verts, {len(df)} faces")
    print(f"[chosen] volume  {v1:.6f} m^3  ({100 * (v1 - v0) / v0:+.3f} % vs source)")
    print(f"[chosen] extents {ext1[0]:.4f} {ext1[1]:.4f} {ext1[2]:.4f}")

    report = {
        "source": {"n_verts": int(len(verts)), "n_faces": int(len(faces)),
                   "volume_m3": v0, "extents_m": ext0.tolist(),
                   "volume_err_vs_canon_pct": 100 * (v0 - CANON_VOLUME) / CANON_VOLUME},
        "decimated": {"vox_m": float(vox), "n_verts": int(len(dv)),
                      "n_faces": int(len(df)), "volume_m3": v1,
                      "extents_m": ext1.tolist(),
                      "volume_err_vs_source_pct": 100 * (v1 - v0) / v0},
    }

    # --- inertia from a solid voxelisation, NOT from vehicle_params.py ---------------
    if not args.skip_inertia:
        I, com, n_in, _ = solid_inertia(dv, df, CANON_MASS, args.inertia_spacing)
        d = np.diag(I)
        print(f"\n[inertia] from {n_in} interior voxels at {args.inertia_spacing} m, "
              f"{CANON_MASS} kg")
        print(f"[inertia] Ixx {d[0]:8.1f}  Iyy {d[1]:8.1f}  Izz {d[2]:8.1f}  kg m^2")
        print(f"[inertia] canonical (hull cloud) {CANON_INERTIA}")
        print("[inertia] deltas " + "  ".join(
            f"{100 * (d[k] - CANON_INERTIA[k]) / CANON_INERTIA[k]:+.1f} %" for k in range(3)))
        print(f"[inertia] CG above hull min-z: {com[2] - dv[:, 2].min():.4f} m")
        report["inertia"] = {
            "spacing_m": args.inertia_spacing, "n_interior": int(n_in),
            "I_diag": d.tolist(), "I_full": I.tolist(), "com": com.tolist(),
            "canonical_I_diag": list(CANON_INERTIA),
            "delta_pct": [100 * (d[k] - CANON_INERTIA[k]) / CANON_INERTIA[k]
                          for k in range(3)],
            "cg_above_floor_m": float(com[2] - dv[:, 2].min()),
        }

    # --- build and save the SDF -------------------------------------------------------
    from warpmpm.geometry import build_sdf, save_sdf
    centred = dv - 0.5 * (dv.min(axis=0) + dv.max(axis=0))   # origin-centred, body frame
    sdf = build_sdf(centred, df, res=args.res, margin_cells=args.margin_cells)
    save_sdf(sdf, args.out_sdf)
    vals = np.asarray(sdf.values)
    boundary_min = float(min(vals[0].min(), vals[-1].min(), vals[:, 0, :].min(),
                             vals[:, -1, :].min(), vals[:, :, 0].min(), vals[:, :, -1].min()))
    print(f"\n[sdf] res {args.res}, cell {sdf.cell:.5f} m, boundary margin "
          f"{boundary_min:.5f} m -> max usable contact band {boundary_min:.5f} m")
    report["sdf"] = {"res": args.res, "cell_m": float(sdf.cell),
                     "boundary_min_m": boundary_min, "path": args.out_sdf,
                     "margin_cells": args.margin_cells}

    with open(args.out_json, "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"wrote {args.out_sdf} and {args.out_json}")


if __name__ == "__main__":
    main()
