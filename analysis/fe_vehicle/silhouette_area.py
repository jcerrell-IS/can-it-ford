#!/usr/bin/env python3
"""Silhouette area facing the flow, measured by orthographic render and pixel count.

TWO EARLIER ATTEMPTS WERE WRONG AND ARE SUPERSEDED.
  Rasterising the hull PARTICLE CLOUD returned 867 occupied cells at both 0.02 m
  and 0.01 m: one point per cell is not a silhouette.
  Rasterising surface-mesh VERTICES did not converge either; the FE area fell
  4.54 -> 4.11 -> 2.82 m^2 as the cell shrank, because gaps open between vertices
  once the cell drops below the mesh edge length.
  Both failed for the same reason: point sampling a surface. Rendering fills the
  faces, so the measurement converges under refinement. The convergence table is
  printed so that can be checked rather than assumed.

These runs are BROADSIDE: long axis on the solver's Y, inflow along X. In the FE
model's own frame the long axis is X, so the face presented to the flow is the
vehicle SIDE, the X-Z plane, and the camera looks along Y.
"""
import sys
import numpy as np
import bpy

src, kind, res, submerged_only = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
REAL_DEPTH = 0.2944294473039918

for c in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.cameras):
    for i in list(c):
        c.remove(i, do_unlink=True)

if kind == "obj":
    bpy.ops.wm.obj_import(filepath=src, use_split_objects=False,
                          forward_axis='Y', up_axis='Z')
else:
    bpy.ops.wm.ply_import(filepath=src)
obs = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.context.view_layer.objects.active = obs[0]
for o in obs:
    o.select_set(True)
if len(obs) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active

P = np.array([v.co[:] for v in ob.data.vertices])
lo, hi = P.min(0), P.max(0)

if submerged_only:
    wl = lo[2] + REAL_DEPTH
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, wl), plane_no=(0, 0, 1), clear_outer=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    hi = hi.copy(); hi[2] = wl

m = bpy.data.materials.new("flat")
m.use_nodes = True
nt = m.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (1, 1, 1, 1)
e.inputs[1].default_value = 1.0
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(e.outputs[0], o_.inputs["Surface"])
ob.data.materials.clear(); ob.data.materials.append(m)
for poly in ob.data.polygons:
    poly.material_index = 0

sc = bpy.context.scene
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[1].default_value = 0.0

cam_d = bpy.data.cameras.new("C"); cam_d.type = 'ORTHO'
span_x = hi[0] - lo[0]; span_z = hi[2] - lo[2]
scale = max(span_x, span_z) * 1.08
cam_d.ortho_scale = scale
cam = bpy.data.objects.new("C", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
cam.location = (cx, lo[1] - 40.0, cz)
cam.rotation_euler = (np.pi / 2, 0, 0)          # look along +Y
cam_d.clip_start = 0.1; cam_d.clip_end = 200.0

sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = res
sc.render.resolution_y = res
sc.render.film_transparent = False
sc.view_settings.view_transform = 'Standard'
sc.render.image_settings.file_format = 'PNG'
out = "/tmp/_sil.png"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)

img = bpy.data.images.load(out)
px = np.array(img.pixels[:]).reshape(-1, 4)
lit = int((px[:, 0] > 0.5).sum())
pix_area = (scale / res) ** 2
area = lit * pix_area
print(f"RESULT kind={kind} submerged={submerged_only} res={res} "
      f"ortho={scale:.4f} lit={lit} area_m2={area:.5f}")
