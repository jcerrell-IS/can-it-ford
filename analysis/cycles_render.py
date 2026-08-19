#!/usr/bin/env python3
"""Build and path-trace a flooded-roadway scene in Blender Cycles. RUNS INSIDE BLENDER.

    blender --background --python analysis/cycles_render.py -- --scene DIR --out FILE

This is the PRESENTATION renderer. analysis/render_multigeom_shaded.py stays as the
DIAGNOSTIC renderer and is not replaced: its particle-enclosure check, facing-ratio
measurements and gate captions are what establish that a frame is honest. This file
only makes the picture look like a photograph, which matplotlib structurally cannot
do because it has no ray tracing, no refraction and no shadows.

WHAT IS PHYSICS AND WHAT IS APPEARANCE, since this render is far more persuasive
than the diagnostic one and therefore far more dangerous
  PHYSICS, from the solver, unmodified:
    every water particle position, the rigid-body pose, the floor plane, and every
    number printed in the corner. The water SURFACE is a splashsurf reconstruction
    of those real particle positions.
  APPEARANCE, invented here:
    all of the optics. Cycles' refraction, absorption, reflections and shadows are
    a light-transport solution for THE SHAPES THE SOLVER PRODUCED. warpmpm computes
    no optics of any kind (register B7: not even a pressure field). Nothing here
    feeds back into any metric or verdict.
  NOT MODELLED, and stated so nobody reads it into the image:
    the hull is a single closed watertight shell with NO separate window, wheel,
    trim or light geometry. There is no cabin behind the glazing because there is
    no glazing. The dark band is an appearance approximation over solid shell, not
    transparent glass, and no refraction happens through it.
"""
import json
import math
import sys
from pathlib import Path

import bpy
import mathutils
import numpy as np


def argv():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def parse():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--scene", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--hdri", default="")
    p.add_argument("--asphalt-dir", default="")
    p.add_argument("--samples", type=int, default=256)
    p.add_argument("--res", type=int, default=1600)
    p.add_argument("--res-y", type=int, default=1000)
    p.add_argument("--cam-elev", type=float, default=11.0)
    p.add_argument("--cam-azim", type=float, default=128.0)
    p.add_argument("--cam-dist", type=float, default=11.5)
    p.add_argument("--lens", type=float, default=58.0)
    p.add_argument("--paint", default="0.42,0.05,0.06",
                   help="linear RGB base colour of the car paint")
    p.add_argument("--far-water", action="store_true",
                   help="draw a flat water surround beyond the solver domain so "
                        "the simulated patch does not read as a floating slab. "
                        "PRESENTATIONAL: it carries no data, see mat_far_water().")
    p.add_argument("--far-reach", type=float, default=240.0)
    p.add_argument("--far-inset", type=float, default=0.10,
                   help="metres the surround overlaps INTO the simulated patch, "
                        "to close the ragged-boundary slot. See main().")
    p.add_argument("--hdri-rot", type=float, default=-38.0,
                   help="degrees, rotation of the environment about z")
    p.add_argument("--wet", type=float, default=0.55,
                   help="0..1 wet-road factor: a water film mainly DROPS roughness "
                        "and RAISES reflectivity, which Cycles expresses directly")
    return p.parse_args(argv())


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def imp_ply(path, name):
    bpy.ops.wm.ply_import(filepath=str(path))
    o = bpy.context.selected_objects[0]
    o.name = name
    return o


def nodes(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return nt, out


def principled(nt, **kw):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    for k, v in kw.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return b


def mat_paint(rgb):
    """Automotive clearcoat over a coloured metallic base. Two-layer, which is what
    makes car paint read as car paint: a coloured metallic flake layer under a
    smooth dielectric coat that supplies the sharp white highlight."""
    m = bpy.data.materials.new("CarPaint")
    nt, out = nodes(m)
    b = principled(nt)
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    # Metallic 0.72 was too high and read as chrome, not paint: at the grazing
    # angles this camera uses, a near-metal Principled surface mirrors the sky and
    # the flank of the vehicle turns into a mirror. Automotive basecoat is a
    # dielectric binder carrying metal flake, so the flake fraction belongs low
    # with the clearcoat above supplying the sharp highlight.
    b.inputs["Metallic"].default_value = 0.28
    b.inputs["Roughness"].default_value = 0.30
    for n, v in (("Coat Weight", 1.0), ("Coat Roughness", 0.035),
                 ("Coat IOR", 1.5)):
        if n in b.inputs:
            b.inputs[n].default_value = v
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_glazing():
    """Dark, glossy, OPAQUE. NOT glass, and deliberately not: the hull is a solid
    shell, so a transmissive material here would refract through a block of resin
    and invent a cabin that does not exist in the geometry."""
    m = bpy.data.materials.new("Glazing")
    nt, out = nodes(m)
    b = principled(nt)
    b.inputs["Base Color"].default_value = (0.012, 0.014, 0.017, 1.0)
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Roughness"].default_value = 0.055
    b.inputs["IOR"].default_value = 1.52
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.85
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_rubber():
    m = bpy.data.materials.new("Rubber")
    nt, out = nodes(m)
    b = principled(nt)
    b.inputs["Base Color"].default_value = (0.016, 0.016, 0.018, 1.0)
    b.inputs["Roughness"].default_value = 0.72
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_water():
    """Real refraction plus a real volumetric. This is the single biggest reason
    for moving off matplotlib: Beer-Lambert here is a Volume Absorption node that
    the path tracer integrates along the actual path length through the actual
    surface, instead of an analytic exp(-sigma*d) evaluated per face against a
    heightfield depth."""
    m = bpy.data.materials.new("Water")
    nt, out = nodes(m)
    b = principled(nt)
    b.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b.inputs["Roughness"].default_value = 0.02
    b.inputs["IOR"].default_value = 1.333
    b.inputs["Transmission Weight"].default_value = 1.0
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    # Flood water, not swimming-pool water: silt-tinted, absorbing red hardest.
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (0.30, 0.42, 0.34, 1.0)
    vol.inputs["Density"].default_value = 2.6
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return m


def mat_far_water():
    """The presentational surround, NOT a reconstruction of anything.

    A flat sheet at the still-water level with a water surface but NO volume node.
    Two reasons it is deliberately not the same material as the reconstructed
    patch. First, a volumetric needs a closed volume and this is an open sheet.
    Second, and the point: this surface carries NO DATA. The solver domain is
    finite, so beyond the tank wall there is no water field to reconstruct, and
    anything drawn out there is invention. It exists only so the simulated patch
    does not read as a slab of jelly floating in a void, which is how the first
    Cycles frame did read. Nothing may be measured off it.
    """
    m = bpy.data.materials.new("FarWater")
    nt, out = nodes(m)
    b = principled(nt)
    b.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b.inputs["Roughness"].default_value = 0.02
    b.inputs["IOR"].default_value = 1.333
    b.inputs["Transmission Weight"].default_value = 1.0
    # The SAME Beer-Lambert volume as the simulated patch. Matching the surface
    # and not the volume is what left the boundary legible as a colour change.
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (0.30, 0.42, 0.34, 1.0)
    vol.inputs["Density"].default_value = 2.6
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    # A DEAD FLAT SURROUND IS ITS OWN TELL. The reconstructed patch is rippled and
    # the surround is a plane, so even at matched height the eye reads the texture
    # change as an edge and the simulated water still looks like an inserted tile.
    # These ripples are PROCEDURAL and carry no data, exactly like the sheet they
    # sit on. They are deliberately finer and lower in amplitude than anything the
    # solver resolves, so they cannot be mistaken for simulated waves: the solver's
    # cell is 0.147 m and its water is 4 particle layers deep, so it cannot express
    # a 0.05 m ripple at all.
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 5.5
    n1.inputs["Detail"].default_value = 10.0
    n1.inputs["Roughness"].default_value = 0.62
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = 0.42
    bmp.inputs["Distance"].default_value = 0.022
    nt.links.new(tc.outputs["Object"], n1.inputs["Vector"])
    nt.links.new(n1.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def far_water_annulus(cx, cy, zlev, floor, inner, reach):
    """A closed rectangular FRAME-SHAPED SLAB of water surrounding the simulated
    patch: top ring at zlev, bottom ring on the floor, inner and outer walls.

    Three earlier versions of this were each wrong in a way worth recording,
    because each looked like a material problem and was actually geometry.

      v1, a full plane: it passed straight through the reconstructed water volume
        and put a flat refracting interface inside the fluid, which Cycles renders
        as a glass shelf cutting through the bow wave.
      v2, an annulus with a hole: no intersection, but the hole was taken from the
        mesh BOUNDING BOX, which is set by whichever splash droplet flew furthest,
        so a ring of bare ground showed between the two surfaces.
      v3, an annulus at the exact clip rectangle: geometrically correct and still
        visibly a different substance, because a zero-thickness sheet has no
        volume for the absorption to act over. The simulated patch attenuated
        light through 0.3 m of water and the surround did not, so the boundary
        stayed legible as a change of colour rather than of height.

    A closed slab of the SAME material fixes v3: identical IOR, identical
    Beer-Lambert path, so the two surfaces differ only where the solver says they
    differ. Still presentational, still carrying no data.
    """
    import bmesh
    x0, x1, y0, y1 = inner
    ox0, ox1, oy0, oy1 = cx - reach, cx + reach, cy - reach, cy + reach
    top_o = [(ox0, oy0, zlev), (ox1, oy0, zlev), (ox1, oy1, zlev), (ox0, oy1, zlev)]
    top_i = [(x0, y0, zlev), (x1, y0, zlev), (x1, y1, zlev), (x0, y1, zlev)]
    bot_o = [(x, y, floor) for x, y, _ in top_o]
    bot_i = [(x, y, floor) for x, y, _ in top_i]
    V = top_o + top_i + bot_o + bot_i          # 0-3, 4-7, 8-11, 12-15
    F = []
    for k in range(4):
        j = (k + 1) % 4
        F.append((k, j, 4 + j, 4 + k))          # top ring
        F.append((8 + k, 12 + k, 12 + j, 8 + j))  # bottom ring
        F.append((4 + k, 4 + j, 12 + j, 12 + k))  # inner wall
        F.append((k, 8 + k, 8 + j, j))            # outer wall
    me = bpy.data.meshes.new("FarWater")
    me.from_pydata(V, [], F)
    me.update()
    ob = bpy.data.objects.new("FarWater", me)
    bpy.context.scene.collection.objects.link(ob)
    # Volume absorption needs consistent outward normals to know what is inside;
    # hand-authored winding is easy to get wrong, so let bmesh settle it.
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    return ob


def mat_ground(asphalt_dir, wet):
    """Asphalt. Textured if the maps are supplied, procedural otherwise.

    THE MAPS ARE OPT-IN. assets/Asphalt015* carry no licence record: no licence
    file ships in assets/ and no copyright or source string appears in any of the
    four headers. Passing --asphalt-dir is the caller asserting they may be used.
    """
    m = bpy.data.materials.new("Asphalt")
    nt, out = nodes(m)
    b = principled(nt)
    # A water film drops roughness and raises reflectivity. That is the whole of
    # "wet road" as a material, and Cycles expresses it directly.
    dry_rough, wet_rough = 0.86, 0.13
    rough = dry_rough + (wet_rough - dry_rough) * wet
    b.inputs["Roughness"].default_value = rough
    b.inputs["Base Color"].default_value = (0.021, 0.021, 0.023, 1.0)
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.5 + 0.5 * wet

    if asphalt_dir:
        d = Path(asphalt_dir)
        col = d / "Asphalt015_1K-JPG_Color.jpg"
        rgh = d / "Asphalt015_1K-JPG_Roughness.jpg"
        nrm = d / "Asphalt015_1K-JPG_NormalGL.jpg"
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)   # 2 m per tile
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        if col.exists():
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(col))
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
            # darken toward wet: a water film makes asphalt read much darker
            mix = nt.nodes.new("ShaderNodeMixRGB")
            mix.blend_type = "MULTIPLY"
            mix.inputs["Fac"].default_value = 1.0
            k = 1.0 - 0.72 * wet
            mix.inputs["Color2"].default_value = (k, k, k, 1.0)
            nt.links.new(t.outputs["Color"], mix.inputs["Color1"])
            nt.links.new(mix.outputs[0], b.inputs["Base Color"])
        if rgh.exists():
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(rgh))
            t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
            mr = nt.nodes.new("ShaderNodeMapRange")
            mr.inputs["To Min"].default_value = max(0.02, rough - 0.10)
            mr.inputs["To Max"].default_value = min(1.0, rough + 0.10)
            nt.links.new(t.outputs["Color"], mr.inputs["Value"])
            nt.links.new(mr.outputs[0], b.inputs["Roughness"])
        if nrm.exists():
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(nrm))
            t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
            nm = nt.nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = 0.85 * (1.0 - 0.5 * wet)
            nt.links.new(t.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs[0], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def assign_hull_materials(obj, paint_rgb):
    """Split the single closed shell into paint / glazing / rubber by geometry.

    The mesh carries no semantic groups, so this is a geometric partition in the
    hull's own local bbox, the same idea as render_multigeom_rollout.base_colours()
    but with a greenhouse band added. It is an APPEARANCE decision and is not
    claimed to identify real parts.
    """
    me = obj.data
    for m in (mat_paint(paint_rgb), mat_glazing(), mat_rubber()):
        me.materials.append(m)
    vs = [v.co for v in me.vertices]
    zs = [v.z for v in vs]
    ys = [v.y for v in vs]
    zlo, zhi = min(zs), max(zs)
    ylo, yhi = min(ys), max(ys)
    H = zhi - zlo
    L = yhi - ylo
    ymid = 0.5 * (ylo + yhi)
    xs = [v.x for v in vs]
    xlo, xhi = min(xs), max(xs)
    Wd = xhi - xlo
    xmid = 0.5 * (xlo + xhi)
    n_g = n_r = 0
    for p in me.polygons:
        c = p.center
        fz = (c.z - zlo) / H if H > 0 else 0.0
        fy = abs(c.y - ymid) / L if L > 0 else 0.0
        # HEIGHT ALONE CANNOT SEPARATE GLASS FROM ROOF: on a sedan the roof panel
        # and the side windows occupy the SAME height band, so a band test paints
        # the roof black. The face NORMAL separates them: a roof panel points up
        # (|nz| high), a window points outward (|nz| low). Measured on the first
        # attempt, the band alone claimed 118638 faces, 18 percent of the hull,
        # and the roof came out dark grey.
        nz = abs(p.normal.z)
        fx = abs(c.x - xmid) / Wd if Wd > 0 else 0.0
        # WHEELS NEED THE OUTBOARD TEST TOO. fz/fy alone also selects the floor
        # pan between the axles, which is not rubber; a wheel is low AND fore/aft
        # of centre AND outboard. The band was also too shallow at 0.18: on this
        # hull the tyre sidewall reaches 0.30 of hull height, so a third of every
        # tyre was being painted body colour.
        if fz < 0.30 and fy > 0.24 and fx > 0.34:
            p.material_index = 2          # wheels
            n_r += 1
        elif 0.58 < fz < 0.95 and fy < 0.36 and nz < 0.55:
            p.material_index = 1          # greenhouse glazing, not the roof
            n_g += 1
        else:
            p.material_index = 0
    print("[cycles] hull materials: %d glazing, %d rubber, %d paint of %d faces"
          % (n_g, n_r, len(me.polygons) - n_g - n_r, len(me.polygons)))


def main():
    a = parse()
    sc = json.loads((Path(a.scene) / "scene.json").read_text())
    clear()

    S = bpy.context.scene
    S.render.engine = "CYCLES"
    S.cycles.samples = a.samples
    S.cycles.use_denoising = True
    S.render.resolution_x = a.res
    S.render.resolution_y = a.res_y
    S.render.film_transparent = False
    S.view_settings.view_transform = "AgX"      # filmic response, not clipped sRGB
    S.view_settings.look = "AgX - Medium High Contrast"
    try:
        S.cycles.device = "GPU"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
    except Exception as exc:
        print("[cycles] GPU unavailable (%s), falling back to CPU" % exc)
        S.cycles.device = "CPU"

    # ---- world: the HDRI this asset was always for -------------------------
    W = bpy.data.worlds.new("W")
    S.world = W
    W.use_nodes = True
    wnt = W.node_tree
    wnt.nodes.clear()
    wout = wnt.nodes.new("ShaderNodeOutputWorld")
    bg = wnt.nodes.new("ShaderNodeBackground")
    if a.hdri and Path(a.hdri).exists():
        env = wnt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(a.hdri)
        mp = wnt.nodes.new("ShaderNodeMapping")
        tc = wnt.nodes.new("ShaderNodeTexCoord")
        mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(a.hdri_rot))
        wnt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
        wnt.links.new(mp.outputs[0], env.inputs["Vector"])
        wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 1.0
        print("[cycles] world HDRI: %s" % Path(a.hdri).name)
    else:
        bg.inputs["Color"].default_value = (0.28, 0.36, 0.48, 1.0)
        bg.inputs["Strength"].default_value = 1.6
        print("[cycles] world: procedural sky (no HDRI supplied)")
    wnt.links.new(bg.outputs[0], wout.inputs["Surface"])

    cx, cy = sc["car_center"]
    floor = sc["floor_z"]

    # ---- ground ------------------------------------------------------------
    # THE ROAD SITS 3 mm BELOW THE WATER'S FLOOR, and that offset is load-bearing.
    # The reconstructed water is a closed volume whose bottom face lies exactly on
    # the floor plane, and the surround slab's bottom does too, so a road at the
    # same z is coplanar with both. Cycles then has two surfaces at identical
    # depth and picks between them per ray, which mottles the simulated patch and
    # makes it read as a different, darker substance than the surround. That
    # looked like a water material problem for three iterations and was a
    # z-fighting problem. 3 mm is far below anything the solver resolves: its grid
    # cell here is 0.147 m, so the offset is 2 percent of one cell.
    bpy.ops.mesh.primitive_plane_add(size=260.0, location=(cx, cy, floor - 0.003))
    ground = bpy.context.object
    ground.name = "Ground"
    ground.data.materials.append(mat_ground(a.asphalt_dir, a.wet))

    # ---- hull --------------------------------------------------------------
    hull = imp_ply(Path(a.scene) / "hull.ply", "Hull")
    paint = tuple(float(x) for x in a.paint.split(","))
    assign_hull_materials(hull, paint)
    hull.data.polygons.foreach_set("use_smooth", [True] * len(hull.data.polygons))
    hull.data.update()

    # ---- water -------------------------------------------------------------
    if not sc.get("no_water"):
        water = imp_ply(Path(a.scene) / "water.ply", "Water")
        water.data.materials.append(mat_water())
        water.data.polygons.foreach_set("use_smooth", [True] * len(water.data.polygons))
        water.data.update()
        print("[cycles] water: %d polys" % len(water.data.polygons))
        if a.far_water:
            co = np.array([v.co[:] for v in water.data.vertices], dtype=np.float64)
            # The hole is the EXACT rectangle prep clipped the water to, not the
            # mesh bounding box. They differ: the bbox is set by whichever stray
            # splash droplet flew furthest, so a bbox hole leaves a ring of bare
            # ground between the two surfaces.
            inner = tuple(sc["water_rect"]) if sc.get("water_rect") else \
                (co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max())
            # AND THEN PULL THE HOLE IN. prep drops a triangle if ANY of its three
            # vertices falls outside the clip rectangle, so the surviving boundary
            # is ragged and lies INSIDE that rectangle by up to one triangle. A
            # hole cut at the rectangle therefore leaves a slot a few centimetres
            # wide running all the way down to the road, which renders as a bright
            # or dark step round the patch and was the last thing in these frames
            # that still looked built rather than photographed. Overlapping inward
            # costs a thin band where two water volumes coincide; since both are
            # the same material that is invisible, whereas the slot is not.
            ins = a.far_inset
            inner = (inner[0] + ins, inner[1] - ins, inner[2] + ins, inner[3] - ins)
            # HEIGHT OF THE SURROUND. Use the free-surface level MEASURED from
            # the particle field by prep_cycles_scene.still_water_level(), not
            # any statistic of the reconstructed mesh. The mesh is a CLOSED
            # volume resting on the floor, so its vertices are half top surface
            # and half bottom; a median over them lands between the two. That
            # error was 0.16 m here and it is what made the simulated patch read
            # as a raised plateau with a lip round it in the first two frames.
            zlev = float(sc.get("surround_z") or sc.get("still_water_z")
                         or np.median(co[:, 2]))
            print("[cycles] surround height %.4f m from the measured free "
                  "surface (%d columns); the mesh-vertex median would have been "
                  "%.4f m, low by %.3f m"
                  % (zlev, int(sc.get("still_water_columns", 0)),
                     float(np.median(co[:, 2])),
                     zlev - float(np.median(co[:, 2]))))
            fw = far_water_annulus(cx, cy, zlev, floor, inner, a.far_reach)
            fw.data.materials.append(mat_far_water())
            print("[cycles] far water: annulus at z=%.4f m, hole %.2f x %.2f m, "
                  "reach %.0f m. PRESENTATIONAL, carries no data." %
                  (zlev, inner[1] - inner[0], inner[3] - inner[2], a.far_reach))

    # ---- camera ------------------------------------------------------------
    el = math.radians(a.cam_elev)
    az = math.radians(a.cam_azim)
    d = a.cam_dist
    tgt = mathutils.Vector((cx, cy, floor + 0.62))
    loc = tgt + mathutils.Vector((d * math.cos(el) * math.cos(az),
                                  d * math.cos(el) * math.sin(az),
                                  d * math.sin(el)))
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = a.lens
    cam = bpy.data.objects.new("Cam", cam_data)
    S.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    S.camera = cam
    print("[cycles] camera at %s looking at %s, %.0f mm"
          % (tuple(round(v, 2) for v in loc), tuple(round(v, 2) for v in tgt), a.lens))

    S.render.filepath = a.out
    S.render.image_settings.file_format = "PNG"
    print("[cycles] rendering %d samples at %dx%d on %s"
          % (a.samples, a.res, a.res_y, S.cycles.device))
    bpy.ops.render.render(write_still=True)
    print("[cycles] wrote %s" % a.out)


if __name__ == "__main__":
    main()
