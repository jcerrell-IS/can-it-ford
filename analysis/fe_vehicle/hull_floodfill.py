"""
Build a watertight simulation hull whose ENCLOSED VOLUME is the flood-fill volume
at a stated sealing scale. RUNS INSIDE BLENDER.

WHY, IN ONE CASE
  The project's Silverado hull encloses 7.962 m^3. Flood fill of the same FE model
  at a 50 mm sealing scale gives 5.148 m^3. The three cars in the pool sit at 34
  to 36 percent of their bounding box; the pickup sits at 22.6 percent. The
  difference is the OPEN CARGO BED, which a surface fit bridges at the rim and
  counts as buoyant. That overstates the truck's displaced volume by 55 percent,
  in the direction that makes it float.

METHOD
  1. Rasterise every FE triangle into an occupancy grid at the sealing scale.
  2. Flood fill the free space from outside. Anything unreachable is "displaced".
     An open bed IS reachable from above, so it is correctly left out.
  3. Isosurface those voxels back into a closed mesh.
  The sealing scale is an argument, not a constant, because displaced volume is a
  modelling choice about which openings count as sealed, not a property of the
  geometry. 50 mm reproduces the project's existing Yaris hull to 3 percent and
  its Rogue hull to 6 percent, which is what calibrates it.
"""
import sys, json, math
import numpy as np
import bpy, bmesh
from collections import deque


def argv():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def parse():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--obj", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seal", type=float, default=0.05, help="sealing scale, m")
    p.add_argument("--out-voxel", type=float, default=0.0,
                   help="isosurface voxel; 0 = seal/2")
    p.add_argument("--radius-mult", type=float, default=0.87,
                   help="point radius as a multiple of the sealing scale")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--smooth", type=int, default=2)
    p.add_argument("--label", default="")
    return p.parse_args(argv())


def load_obj(path):
    V, F = [], []
    for line in open(path):
        if line.startswith("v "):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            for k in range(1, len(idx) - 1):
                F.append((idx[0], idx[k], idx[k + 1]))
    return np.asarray(V, np.float64), np.asarray(F, np.int64)


def occupancy(V, F, h, pad=2):
    lo, hi = V.min(0), V.max(0)
    dims = np.ceil((hi - lo) / h).astype(int) + 2 * pad + 1
    occ = np.zeros(dims, bool)
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
    return occ, lo, dims, pad


def outside_mask(occ, dims):
    free = ~occ
    seen = np.zeros(dims, bool)
    q = deque()
    for ax in range(3):
        for end in (0, dims[ax] - 1):
            sl = [slice(None)] * 3
            sl[ax] = end
            ii, jj = np.nonzero(free[tuple(sl)])
            rest = [k for k in range(3) if k != ax]
            for p, r in zip(ii, jj):
                c = [0, 0, 0]; c[ax] = end; c[rest[0]] = p; c[rest[1]] = r
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
    return seen


def isosurface(points, out_voxel, radius, smooth, threshold=0.5):
    me = bpy.data.meshes.new("hull_pts")
    me.from_pydata([tuple(p) for p in points], [], [])
    me.update()
    ob = bpy.data.objects.new("Hull", me)
    bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new("hullnodes", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = ng.nodes.new("NodeGroupInput")
    m2p = ng.nodes.new("GeometryNodeMeshToPoints")
    p2v = ng.nodes.new("GeometryNodePointsToVolume")
    v2m = ng.nodes.new("GeometryNodeVolumeToMesh")
    go = ng.nodes.new("NodeGroupOutput")
    def S(n, k, v):
        if k in n.inputs:
            n.inputs[k].default_value = v
    S(p2v, "Resolution Mode", 'Size'); S(p2v, "Voxel Size", out_voxel)
    S(p2v, "Radius", radius); S(p2v, "Density", 1.0)
    S(v2m, "Resolution Mode", 'Size'); S(v2m, "Voxel Size", out_voxel)
    S(v2m, "Threshold", threshold); S(v2m, "Adaptivity", 0.0)
    L = ng.links.new
    L(gi.outputs[0], m2p.inputs["Mesh"]); L(m2p.outputs["Points"], p2v.inputs["Points"])
    L(p2v.outputs["Volume"], v2m.inputs["Volume"]); L(v2m.outputs["Mesh"], go.inputs[0])
    md = ob.modifiers.new("gn", 'NODES'); md.node_group = ng
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    if smooth > 0:
        sm = ob.modifiers.new("sm", 'SMOOTH'); sm.factor = 1.0; sm.iterations = smooth
        bpy.ops.object.modifier_apply(modifier=sm.name)
    return ob


def mesh_stats(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.edges.ensure_lookup_table()
    b = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    nm = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    vol = abs(bm.calc_volume(signed=True)); bm.free()
    return b, nm, vol


def main():
    a = parse()
    for c in (bpy.data.objects, bpy.data.meshes, bpy.data.node_groups):
        for i in list(c):
            c.remove(i, do_unlink=True)
    V, F = load_obj(a.obj)
    h = a.seal
    occ, lo, dims, pad = occupancy(V, F, h)
    seen = outside_mask(occ, dims)
    inside = ~seen
    n_in = int(inside.sum())
    target = n_in * h ** 3
    ii, jj, kk = np.nonzero(inside)
    pts = lo + (np.stack([ii, jj, kk], 1) - pad + 0.5) * h

    ov = a.out_voxel if a.out_voxel > 0 else h / 2.0
    ob = isosurface(pts, ov, a.radius_mult * h, a.smooth, a.threshold)
    bnd, nonm, vol = mesh_stats(ob)

    import os
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    bpy.ops.wm.ply_export(filepath=a.out, export_selected_objects=False, ascii_format=False)

    P = np.array([v.co[:] for v in ob.data.vertices])
    out = {
        "label": a.label or os.path.basename(a.obj),
        "seal_scale_m": h, "out_voxel_m": ov, "threshold": a.threshold, "radius_m": a.radius_mult * h,
        "floodfill_voxels_inside": n_in,
        "floodfill_volume_m3": float(target),
        "mesh_verts": len(ob.data.vertices), "mesh_faces": len(ob.data.polygons),
        "boundary_edges": bnd, "nonmanifold_edges": nonm,
        "watertight": bool(bnd == 0 and nonm == 0),
        "mesh_volume_m3": float(vol),
        "mesh_over_floodfill": float(vol / target) if target else None,
        "fe_bbox_span_m": [float(x) for x in (V.max(0) - V.min(0))],
        "hull_bbox_span_m": [float(x) for x in (P.max(0) - P.min(0))],
        "out_ply": a.out,
    }
    print("HULLJSON " + json.dumps(out))
    with open(a.out.replace(".ply", "_stats.json"), "w") as fh:
        json.dump(out, fh, indent=1)


main()
