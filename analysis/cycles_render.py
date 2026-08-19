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
    b.inputs["Metallic"].default_value = 0.72
    b.inputs["Roughness"].default_value = 0.22
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
        if fz < 0.18 and fy > 0.28:
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
        mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(-38.0))
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
    bpy.ops.mesh.primitive_plane_add(size=260.0, location=(cx, cy, floor))
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
