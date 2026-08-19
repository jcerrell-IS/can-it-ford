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
    # DEFAULT ON, and this is a correction to c0fa82b. That commit updated
    # mat_ground()'s docstring to say the maps "are now used by default" once the
    # licence was granted, but left this default at "", so the code did not do what
    # the docstring claimed. A docstring asserting behaviour the code does not have
    # is exactly the failure this project keeps finding elsewhere; caught here by
    # re-reading the argument list against the prose rather than by a render.
    # Pass --asphalt-dir "" to render without them.
    p.add_argument("--asphalt-dir",
                   default=str(Path(__file__).resolve().parent.parent / "assets"))
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
    p.add_argument("--cam-tgt-z", type=float, default=0.0,
                   help="metres above the road/floor the camera aims at (0 = 0.62)")
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
    # AMPLITUDE SET BY WHAT THE GRAZING VIEW NEEDS, not by taste. At a 3 to 7
    # degree camera elevation the Fresnel reflectance of water is above 0.8, so a
    # perfectly flat surround becomes a mirror of the bright sky while the
    # simulated patch, whose normals vary by tens of degrees, reflects the dark
    # treeline instead. The patch then reads as a black rectangular trench cut into
    # bright water. That contrast is REAL optics and not a meshing error, which is
    # why it survived three geometry fixes; the artificial part is only that the
    # transition is a sharp rectangle. Giving the surround a comparable slope
    # distribution removes the rectangle without touching the simulated surface.
    n1.inputs["Scale"].default_value = 2.2
    n1.inputs["Detail"].default_value = 12.0
    n1.inputs["Roughness"].default_value = 0.68
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = 0.85
    bmp.inputs["Distance"].default_value = 0.055
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


def far_water_multi(cx, cy, zlev, floor, rects, reach):
    """One surround slab for the whole road, with one hole per simulated patch.

    TILED ON A GLOBAL GRID, which is the third version and the first correct one.

    v1 emitted each tile of the decomposition as its own closed box. Adjacent boxes
    share a face plane, so a ray crossing between them traverses two coincident
    interfaces, refracts twice and z-fights.

    v2 emitted top and bottom quads with walls only on the real boundaries, which
    is the right idea but left T-JUNCTIONS: a full-width strip between two patches
    has one long edge running the whole width, while the row beside a patch has two
    short edges plus the hole. The strip's edge carries no vertex at the patch's x
    boundaries, so the surfaces meet along an edge that is shared geometrically but
    not topologically. The shell is then not closed, the volume leaks, and the strip
    renders as a flat white band straight across the frame. It looks like a lighting
    bug and it is a meshing bug.

    v3, here: take the union of every x boundary and every y boundary as global cut
    lines, tile the whole outer rectangle with the resulting grid, and skip the
    cells that fall inside a hole. Every cell edge then matches its neighbour's
    exactly, so there are no T-junctions anywhere and welding coincident vertices
    closes the shell.

    Holes must not overlap; that is asserted rather than assumed.
    """
    import bmesh
    rs = sorted(rects, key=lambda r: r[2])
    for p_, q_ in zip(rs, rs[1:]):
        if q_[2] <= p_[3]:
            raise SystemExit("far_water_multi: patch y-ranges overlap (%.3f..%.3f "
                             "and %.3f..%.3f). Increase --spacing."
                             % (p_[2], p_[3], q_[2], q_[3]))
    ox0, ox1 = cx - reach, cx + reach
    oy0, oy1 = cy - reach, cy + reach
    xs = sorted({ox0, ox1} | {v for r in rs for v in (r[0], r[1])})
    ys = sorted({oy0, oy1} | {v for r in rs for v in (r[2], r[3])})

    def in_hole(x, y):
        return any(r[0] < x < r[1] and r[2] < y < r[3] for r in rs)

    V, F = [], []

    def quad(a, b, c, d):
        base = len(V)
        V.extend([a, b, c, d])
        F.append((base, base + 1, base + 2, base + 3))

    ncell = 0
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            if in_hole(0.5 * (x0 + x1), 0.5 * (y0 + y1)):
                continue
            ncell += 1
            quad((x0, y0, zlev), (x1, y0, zlev), (x1, y1, zlev), (x0, y1, zlev))
            quad((x0, y0, floor), (x1, y0, floor), (x1, y1, floor), (x0, y1, floor))
    # WALLS MUST BE SPLIT ON THE SAME GRID. A wall raised as one long quad along a
    # hole edge re-creates the T-junction the grid was introduced to remove: the
    # widest patch is 9.41 m and the narrowest 7.92 m, so a wall spanning one hole
    # crosses another hole's x boundary, and the cells beside it carry a vertex
    # there that the wall does not. That was 84 non-manifold edges.
    def cuts(vals, lo, hi):
        return [v for v in vals if lo - 1e-9 <= v <= hi + 1e-9]

    for (x0, x1, y0, y1) in [(ox0, ox1, oy0, oy1)] + list(rs):
        for a, b in zip(cuts(xs, x0, x1), cuts(xs, x0, x1)[1:]):
            quad((a, y0, zlev), (b, y0, zlev), (b, y0, floor), (a, y0, floor))
            quad((b, y1, zlev), (a, y1, zlev), (a, y1, floor), (b, y1, floor))
        for a, b in zip(cuts(ys, y0, y1), cuts(ys, y0, y1)[1:]):
            quad((x1, a, zlev), (x1, b, zlev), (x1, b, floor), (x1, a, floor))
            quad((x0, b, zlev), (x0, a, zlev), (x0, a, floor), (x0, b, floor))

    me = bpy.data.meshes.new("FarWater")
    me.from_pydata(V, [], F)
    me.update()
    ob = bpy.data.objects.new("FarWater", me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    bm.to_mesh(me)
    bm.free()
    if nonman:
        print("[cycles] WARNING: surround has %d non-manifold edges; the volume "
              "will leak and the sheet may render as a bright band." % nonman)
    else:
        print("[cycles] surround shell: %d cells, closed and manifold" % ncell)
    return ob


def mat_ground(asphalt_dir, wet):
    """Asphalt. Textured if the maps are supplied, procedural otherwise.

    LICENCE, UPDATED 2026-08-19. These maps were opt-in and defaulted OFF while
    their licence was unestablished: no licence file ships in assets/ and no
    copyright or source string appears in any of the four headers, so the position
    was that the caller had to assert the right to use them. Josie confirmed by
    email on 2026-08-19 that licence permission is granted, so they are now used by
    default. The flag is KEPT so a caller can still render without them, and the
    provenance gap in the files themselves is unchanged: that was a permission
    question, and it was answered by the owner, not by the files.
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
    composite = sc.get("kind") == "road_composite"

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
    if composite:
        # A real crowned road solid replaces the infinite plane. The plane is still
        # laid far below as a ground fill so the horizon is not empty, but it is
        # 1.2 m down and never visible next to the road.
        road = imp_ply(Path(a.scene) / sc["road"], "Road")
        road.data.materials.append(mat_ground(a.asphalt_dir, a.wet))
        print("[cycles] road: %d polys, %s, width %.1f m, carriageway %.1f m, "
              "cross slope %.3f" % (len(road.data.polygons),
                                    sc.get("road_profile_source", "?"),
                                    sc.get("road_width_total", 0.0),
                                    sc.get("road_carriageway", 0.0),
                                    sc.get("road_cross_slope", 0.0)))
    # Beyond the modelled road solid the terrain is the VERGE height, not the road
    # solid's base. Laying the fill plane at that base put the countryside 1.2 m
    # below the carriageway, so the road read as a causeway across a lake and the
    # off-road water went black through 1.5 m of absorption. The verge is the
    # highest point of road_profile(), so this is the flat ground the kerb runs up
    # to, continued outward. Presentational, like everything past the domain.
    fill_z = float(sc["verge_z"]) if composite and sc.get("verge_z") is not None \
        else floor - 0.003
    bpy.ops.mesh.primitive_plane_add(size=520.0, location=(cx, cy, fill_z - 0.003))
    ground = bpy.context.object
    ground.name = "Ground"
    ground.data.materials.append(mat_ground(a.asphalt_dir, a.wet))

    # ---- vehicles and their water -----------------------------------------
    paint = tuple(float(x) for x in a.paint.split(","))
    if composite:
        # Each vehicle carries its OWN water patch, from its own run. They are
        # loaded as separate objects rather than merged: the paint / glazing / tyre
        # partition is computed in each hull's own bounding box, and merging three
        # hulls of different sizes into one mesh would compute that partition in a
        # box spanning all three and paint the wrong faces on every one of them.
        allw = []
        for k, v in enumerate(sc["vehicles"]):
            h = imp_ply(Path(a.scene) / v["hull"], "Hull%d" % k)
            assign_hull_materials(h, paint)
            h.data.polygons.foreach_set("use_smooth", [True] * len(h.data.polygons))
            h.data.update()
            w = imp_ply(Path(a.scene) / v["water"], "Water%d" % k)
            w.data.materials.append(mat_water())
            w.data.polygons.foreach_set("use_smooth", [True] * len(w.data.polygons))
            w.data.update()
            allw.append((v, w))
            print("[cycles] vehicle %d: %s, hull %d faces, water %d faces, "
                  "simulated depth %.3f m" %
                  (k, v.get("name", "?"), len(h.data.polygons),
                   len(w.data.polygons), v.get("still_water_depth_m", 0.0)))
        if a.far_water:
            # ONE surround for the whole road, with one hole per patch. Cut as a
            # separate frame per patch would leave the strips between them bare.
            zlev = float(sc["surround_z"])
            rects = [tuple(v["water_rect"]) for v, _ in allw]
            ins = a.far_inset
            rects = [(r[0] + ins, r[1] - ins, r[2] + ins, r[3] - ins) for r in rects]
            fw = far_water_multi(cx, cy, zlev, floor, rects, a.far_reach)
            fw.data.materials.append(mat_far_water())
            print("[cycles] far water: sheet at z=%.4f m with %d holes, reach "
                  "%.0f m. PRESENTATIONAL, carries no data. The %d patches sit "
                  "%.4f m apart in surface height because they are independent "
                  "runs." % (zlev, len(rects), a.far_reach, len(rects),
                             float(sc.get("surround_spread_m", 0.0))))
    else:
        hull = imp_ply(Path(a.scene) / "hull.ply", "Hull")
        assign_hull_materials(hull, paint)
        hull.data.polygons.foreach_set("use_smooth", [True] * len(hull.data.polygons))
        hull.data.update()
        if not sc.get("no_water"):
            water = imp_ply(Path(a.scene) / "water.ply", "Water")
            water.data.materials.append(mat_water())
            water.data.polygons.foreach_set("use_smooth", [True] * len(water.data.polygons))
            water.data.update()
            print("[cycles] water: %d polys" % len(water.data.polygons))
            if a.far_water:
                co = np.array([v.co[:] for v in water.data.vertices], dtype=np.float64)
                inner = tuple(sc["water_rect"]) if sc.get("water_rect") else \
                    (co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max())
                ins = a.far_inset
                inner = (inner[0] + ins, inner[1] - ins, inner[2] + ins, inner[3] - ins)
                zlev = float(sc.get("surround_z") or sc.get("still_water_z")
                             or np.median(co[:, 2]))
                fw = far_water_annulus(cx, cy, zlev, floor, inner, a.far_reach)
                fw.data.materials.append(mat_far_water())
                print("[cycles] far water: annulus at z=%.4f m, hole %.2f x %.2f m, "
                      "reach %.0f m. PRESENTATIONAL, carries no data."
                      % (zlev, inner[1] - inner[0], inner[3] - inner[2], a.far_reach))

    # ---- camera ------------------------------------------------------------
    el = math.radians(a.cam_elev)
    az = math.radians(a.cam_azim)
    d = a.cam_dist
    # For the road composite, floor is the road SOLID's base, 1.2 m under the
    # carriageway, so aiming at floor+0.62 would aim the camera into the tarmac.
    base_z = float(sc["road_crown_z"]) if composite else floor
    tgt = mathutils.Vector((cx, cy, base_z + (a.cam_tgt_z if a.cam_tgt_z else 0.62)))
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
