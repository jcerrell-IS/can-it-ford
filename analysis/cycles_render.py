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
    p.add_argument("--paints", default="",
                   help="composite only: one 'r,g,b' per vehicle, ';'-separated. "
                        "Three identical vehicles in one frame is a debug look; "
                        "different classes should not share one body colour.")
    p.add_argument("--far-water", action="store_true",
                   help="draw a flat water surround beyond the solver domain so "
                        "the simulated patch does not read as a floating slab. "
                        "PRESENTATIONAL: it carries no data, see mat_far_water().")
    p.add_argument("--far-reach", type=float, default=240.0)
    p.add_argument("--city", type=int, default=0,
                   help="number of massed buildings PER SIDE. PRESENTATIONAL.")
    p.add_argument("--city-setback", type=float, default=13.0)
    p.add_argument("--city-reach", type=float, default=95.0)
    p.add_argument("--cam-tgt-z", type=float, default=0.0,
                   help="metres above the road/floor the camera aims at (0 = 0.62)")
    p.add_argument("--far-inset", type=float, default=0.10,
                   help="metres the surround overlaps INTO the simulated patch, "
                        "to close the ragged-boundary slot. See main().")
    p.add_argument("--hdri-strength", type=float, default=1.0,
                   help="world background strength. A clear-sky HDRI with no ground "
                        "carries much less total radiance than a treeline one, so "
                        "swapping environments needs this re-set, not just the file "
                        "changed.")
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
    # METALLIC HIGH, ROUGHNESS HIGH ENOUGH TO STOP IT BEING CHROME. Two earlier
    # values were both wrong for the same reason, that metallic and roughness have
    # to move together: 0.72 with roughness 0.22 turned the flanks into mirrors at
    # grazing incidence, and dropping to 0.28 fixed the chrome but lost the flake
    # depth that makes paint read as paint. Automotive basecoat is metal flake in a
    # binder under a clearcoat, so the flake fraction is genuinely high; what keeps
    # it from mirroring is the basecoat's roughness, with the coat above supplying
    # the one sharp highlight.
    b.inputs["Metallic"].default_value = 0.80
    b.inputs["Roughness"].default_value = 0.38
    for n, v in (("Coat Weight", 1.0), ("Coat Roughness", 0.06),
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


def mat_facade(seed):
    """A daylight building facade: pale render wall with dark reflective glazing.

    TWO EARLIER VERSIONS WERE BOTH A CHECKERBOARD TEST PATTERN, and both taught
    something.

    v1 mapped the windows in OBJECT space. Object coordinates run -0.5..0.5 over the
    cube whatever its scale, so a fixed cell count put the same number of windows
    across a 7 m building and a 21 m one: window size grew with the building. Any
    texture on object coordinates after a non-uniform scale has this bug.

    v2 fixed the size by driving the grid from world POSITION, and still looked like
    a test pattern, because a second coarse grid picking which windows were lit was
    itself regular and at 6 m it was the pattern the eye actually saw. A regular
    mask over a regular grid reads as the coarser of the two.

    v3 drops the lit windows entirely. The world here is a daytime clear sky, so
    interior lighting is wrong on the physics of the scene as well as ugly: at this
    exposure a lit window competes with the sun. Daylight glazing is simply DARK and
    reflective against a paler wall, which needs no second grid and cannot produce a
    checkerboard because the two materials are close in value.
    """
    m = bpy.data.materials.new("Facade%d" % seed)
    nt, out = nodes(m)
    b = principled(nt)
    wall = 0.16 + 0.10 * ((seed * 37) % 5) / 4.0
    b.inputs["Roughness"].default_value = 0.80

    # A CHECKER CANNOT BE A WINDOW GRID, which is what the first three attempts
    # missed. Checker alternates in every axis, so it is a chessboard: every cell is
    # either window or wall and there is no wall BETWEEN windows. Real glazing is a
    # grid of openings separated by spandrel, so the mask has to be built from two
    # independent one-dimensional duty cycles, not from an alternation. Horizontal
    # spacing is taken from y because these facades face across the road, which runs
    # along y; the end walls get stripes instead and are barely in view.
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])

    def mth(op, src=None, v1=None, v2=None, v3=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        if src is not None:
            nt.links.new(src, n.inputs[0])
        if v1 is not None:
            n.inputs[0].default_value = v1
        if v2 is not None:
            n.inputs[1].default_value = v2
        if v3 is not None:
            n.inputs[2].default_value = v3
        return n

    wy = mth("WRAP", src=sep.outputs["Y"], v2=1.7, v3=0.0)
    my = mth("LESS_THAN", src=wy.outputs[0], v2=1.05)      # 62 pct glazed
    wz = mth("WRAP", src=sep.outputs["Z"], v2=3.4, v3=0.0)
    mz = mth("LESS_THAN", src=wz.outputs[0], v2=2.0)       # 59 pct floor height
    win = mth("MULTIPLY", src=my.outputs[0])
    nt.links.new(mz.outputs[0], win.inputs[1])

    col = nt.nodes.new("ShaderNodeMixRGB")
    col.inputs["Color1"].default_value = (wall, wall * 0.97, wall * 0.93, 1.0)
    col.inputs["Color2"].default_value = (0.030, 0.036, 0.046, 1.0)
    nt.links.new(win.outputs[0], col.inputs["Fac"])
    nt.links.new(col.outputs[0], b.inputs["Base Color"])

    rgh = nt.nodes.new("ShaderNodeMix")
    rgh.data_type = "FLOAT"
    rgh.inputs[2].default_value = 0.82
    rgh.inputs[3].default_value = 0.16
    nt.links.new(win.outputs[0], rgh.inputs[0])
    nt.links.new(rgh.outputs[0], b.inputs["Roughness"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def add_city(cx, cy, base_z, setback, count, reach):
    """Massed roadside buildings, both sides, deterministic.

    PRESENTATIONAL in full: nothing here is simulated, nothing may be measured off
    it, and no building interacts with the water beyond standing in it. It exists
    because the scene is a flooded ROAD and every frame so far has read as a lake in
    a field, which is a statement about the setting the simulation never made either
    way.

    Deterministic from the index rather than random, so a re-render is the same city
    and two frames of a sequence cannot disagree about where a building is.
    """
    made = 0
    for side in (-1, 1):
        for i in range(count):
            k = i * 7919 + (0 if side < 0 else 104729)
            t = (i + 0.5) / count
            y = cy - reach + 2.0 * reach * t + ((k % 13) - 6) * 0.9
            w = 7.0 + (k % 11) * 1.3
            d = 8.0 + ((k // 3) % 9) * 1.6
            hgt = 7.0 + ((k // 7) % 13) * 2.4
            gap = setback + ((k // 5) % 7) * 1.1
            x = cx + side * (gap + 0.5 * w)
            bpy.ops.mesh.primitive_cube_add(size=1.0,
                                            location=(x, y, base_z + 0.5 * hgt))
            ob = bpy.context.object
            ob.scale = (w, d, hgt)
            ob.name = "Bldg_%d_%d" % (side, i)
            ob.data.materials.append(mat_facade(k % 97))
            made += 1
    print("[cycles] city: %d massed buildings, setback %.1f m from the crown, over "
          "%.0f m of road. PRESENTATIONAL, nothing measurable." %
          (made, setback, 2 * reach))
    return made


def mat_ground(asphalt_dir, wet, water_z=None, markings=None):
    """Asphalt, ROUGH, and wet only where it is actually under water.

    THE SINGLE BIGGEST TELL IN THE EARLIER FRAMES was that the road and the flood
    rendered as the same flat grey mirror, so the eye could not find the waterline.
    That was a material error, not a lighting one. The two surfaces are physically
    nothing alike:

      dry asphalt   roughness 0.6 to 0.8. It SCATTERS. It must not mirror a treeline.
      open water    roughness 0.01 to 0.05, IOR 1.333, with transmission.
      wet asphalt   the interesting middle: a film drops roughness toward 0.1 to 0.2
                    and raises reflectivity, but it is still not open water.

    So roughness and colour are now driven by HEIGHT against the waterline rather
    than by one global `wet` number: submerged road is dark and glossy, road above
    the water is pale and rough, and the transition is a band a few centimetres
    wide. That band is the visible waterline on the road, which is the cue that was
    missing. `wet` now sets only how wet the SUBMERGED surface is.

    LICENCE, UPDATED 2026-08-19. These maps were opt-in and defaulted OFF while
    their licence was unestablished: no licence file ships in assets/ and no
    copyright or source string appears in any of the four headers. Josie confirmed
    by email on 2026-08-19 that licence permission is granted, so they are used by
    default now. The provenance gap in the files is unchanged; the permission rests
    on the owner's word, not on anything recoverable from the assets.
    """
    m = bpy.data.materials.new("Asphalt")
    nt, out = nodes(m)
    b = principled(nt)
    dry_rough = 0.78
    wet_rough = 0.78 + (0.14 - 0.78) * float(wet)
    dry_rgb = (0.055, 0.055, 0.058)
    wet_rgb = tuple(c * 0.42 for c in dry_rgb)     # a film darkens asphalt hard
    b.inputs["Roughness"].default_value = dry_rough
    b.inputs["Base Color"].default_value = (*dry_rgb, 1.0)

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)      # 2 m per tile
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])

    col_out = None
    rgh_out = None
    if asphalt_dir:
        d = Path(asphalt_dir)
        col = d / "Asphalt015_1K-JPG_Color.jpg"
        rgh = d / "Asphalt015_1K-JPG_Roughness.jpg"
        nrm = d / "Asphalt015_1K-JPG_NormalGL.jpg"
        if col.exists():
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(col))
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
            # The Asphalt015 albedo is a pale grey. Real bituminous road surface is
            # far darker; left as shipped it reads as concrete and washes out.
            dk = nt.nodes.new("ShaderNodeMixRGB")
            dk.blend_type = "MULTIPLY"
            dk.inputs["Fac"].default_value = 1.0
            dk.inputs["Color2"].default_value = (0.30, 0.30, 0.32, 1.0)
            nt.links.new(t.outputs["Color"], dk.inputs["Color1"])
            col_out = dk.outputs[0]
        if rgh.exists():
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(rgh))
            t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
            mr = nt.nodes.new("ShaderNodeMapRange")
            mr.inputs["To Min"].default_value = 0.62
            mr.inputs["To Max"].default_value = 0.92
            nt.links.new(t.outputs["Color"], mr.inputs["Value"])
            rgh_out = mr.outputs[0]
        if nrm.exists():
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(nrm))
            t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
            nm = nt.nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = 0.9
            nt.links.new(t.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs[0], b.inputs["Normal"])

    if water_z is None:
        if col_out:
            nt.links.new(col_out, b.inputs["Base Color"])
        if rgh_out:
            nt.links.new(rgh_out, b.inputs["Roughness"])
        nt.links.new(b.outputs[0], out.inputs["Surface"])
        return m

    # submergence factor: 1 under the waterline, 0 above it, over a 6 cm band
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
    sub = nt.nodes.new("ShaderNodeMapRange")
    sub.inputs["From Min"].default_value = water_z + 0.03
    sub.inputs["From Max"].default_value = water_z - 0.03
    sub.inputs["To Min"].default_value = 0.0
    sub.inputs["To Max"].default_value = 1.0
    sub.clamp = True
    nt.links.new(sep.outputs["Z"], sub.inputs["Value"])

    mixc = nt.nodes.new("ShaderNodeMixRGB")
    mixc.inputs["Color1"].default_value = (*dry_rgb, 1.0)
    mixc.inputs["Color2"].default_value = (*wet_rgb, 1.0)
    if col_out:
        tint = nt.nodes.new("ShaderNodeMixRGB")
        tint.blend_type = "MULTIPLY"
        tint.inputs["Fac"].default_value = 1.0
        tint.inputs["Color2"].default_value = (0.42, 0.42, 0.44, 1.0)
        nt.links.new(col_out, tint.inputs["Color1"])
        nt.links.new(col_out, mixc.inputs["Color1"])
        nt.links.new(tint.outputs[0], mixc.inputs["Color2"])
    nt.links.new(sub.outputs["Result"], mixc.inputs["Fac"])
    nt.links.new(mixc.outputs[0], b.inputs["Base Color"])

    mixr = nt.nodes.new("ShaderNodeMapRange")
    mixr.inputs["To Min"].default_value = dry_rough
    mixr.inputs["To Max"].default_value = wet_rough
    nt.links.new(sub.outputs["Result"], mixr.inputs["Value"])
    if markings:
        # LANE MARKINGS, procedural, no asset. Two jobs beyond decoration. They tell
        # the viewer this grey ribbon is a carriageway rather than a lake, which no
        # amount of asphalt texture does on its own. And they make the CAMBER
        # visible: the crown and cross slope are real geometry imported from
        # simulation/road_geometry.road_profile, but a uniform grey surface gives
        # the eye nothing to read curvature against, so the geometry that is the
        # unevaluated part of this configuration was invisible in every frame so
        # far. A straight painted line draped over a crowned surface is the
        # cheapest possible curvature gauge.
        cx_road, half_c = markings
        geo2 = nt.nodes.new("ShaderNodeNewGeometry")
        sp2 = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo2.outputs["Position"], sp2.inputs["Vector"])

        def mnode(op, v1=None, v2=None, inp=None):
            n = nt.nodes.new("ShaderNodeMath")
            n.operation = op
            if v1 is not None:
                n.inputs[0].default_value = v1
            if v2 is not None:
                n.inputs[1].default_value = v2
            if inp is not None:
                nt.links.new(inp, n.inputs[0])
            return n

        sub_x = mnode("SUBTRACT", v2=cx_road, inp=sp2.outputs["X"])
        dx = mnode("ABSOLUTE", inp=sub_x.outputs[0])
        centre = mnode("LESS_THAN", v2=0.075, inp=dx.outputs[0])
        off = mnode("SUBTRACT", v2=half_c - 0.35, inp=dx.outputs[0])
        offa = mnode("ABSOLUTE", inp=off.outputs[0])
        edge = mnode("LESS_THAN", v2=0.075, inp=offa.outputs[0])
        yw = mnode("WRAP", inp=sp2.outputs["Y"])
        yw.inputs[1].default_value = 9.0
        yw.inputs[2].default_value = 0.0
        dash = mnode("LESS_THAN", v2=6.0, inp=yw.outputs[0])
        cdash = mnode("MULTIPLY", inp=centre.outputs[0])
        nt.links.new(dash.outputs[0], cdash.inputs[1])
        both = mnode("MAXIMUM", inp=cdash.outputs[0])
        nt.links.new(edge.outputs[0], both.inputs[1])
        onroad = mnode("LESS_THAN", v2=half_c + 0.05, inp=dx.outputs[0])
        mask = mnode("MULTIPLY", inp=both.outputs[0])
        nt.links.new(onroad.outputs[0], mask.inputs[1])

        paintmix = nt.nodes.new("ShaderNodeMixRGB")
        paintmix.inputs["Color2"].default_value = (0.52, 0.52, 0.50, 1.0)
        nt.links.new(mask.outputs[0], paintmix.inputs["Fac"])
        nt.links.new(mixc.outputs[0], paintmix.inputs["Color1"])
        nt.links.new(paintmix.outputs[0], b.inputs["Base Color"])

        rmix = nt.nodes.new("ShaderNodeMix")
        rmix.data_type = "FLOAT"
        nt.links.new(mask.outputs[0], rmix.inputs[0])
        nt.links.new(mixr.outputs[0], rmix.inputs[2])
        rmix.inputs[3].default_value = 0.42
        nt.links.new(rmix.outputs[0], b.inputs["Roughness"])
        print("[cycles] lane markings: dashed centre line at x=%.2f, edge lines at "
              "+/-%.2f m, 6 m mark and 3 m gap. Procedural, no asset. They are the "
              "only cue that makes the imported crown and camber legible."
              % (cx_road, half_c - 0.35))
    else:
        nt.links.new(mixr.outputs[0], b.inputs["Roughness"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    print("[cycles] road: dry roughness %.2f above z=%.3f m, wet roughness %.2f "
          "below it, transition band 0.06 m. Water is roughness 0.02, so the two "
          "surfaces are no longer the same mirror." % (dry_rough, water_z, wet_rough))
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
        bg.inputs["Strength"].default_value = a.hdri_strength
        print("[cycles] world HDRI: %s at strength %.2f, rotated %.0f deg"
              % (Path(a.hdri).name, a.hdri_strength, a.hdri_rot))
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
        road.data.materials.append(mat_ground(
            a.asphalt_dir, a.wet, float(sc["surround_z"]),
            markings=(float(sc["crown_x"]), 0.5 * float(sc["road_carriageway"]))))
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
    gw = sc.get("surround_z") or sc.get("still_water_z")
    ground.data.materials.append(
        mat_ground(a.asphalt_dir, a.wet, float(gw) if gw else None))

    if a.city > 0:
        add_city(cx, cy, float(sc.get("verge_z", floor)),
                 a.city_setback, a.city, a.city_reach)

    # ---- vehicles and their water -----------------------------------------
    paint = tuple(float(x) for x in a.paint.split(","))
    if composite:
        # Each vehicle carries its OWN water patch, from its own run. They are
        # loaded as separate objects rather than merged: the paint / glazing / tyre
        # partition is computed in each hull's own bounding box, and merging three
        # hulls of different sizes into one mesh would compute that partition in a
        # box spanning all three and paint the wrong faces on every one of them.
        allw = []
        plist = [tuple(float(x) for x in c.split(","))
                 for c in a.paints.split(";") if c.strip()] or [paint]
        for k, v in enumerate(sc["vehicles"]):
            h = imp_ply(Path(a.scene) / v["hull"], "Hull%d" % k)
            assign_hull_materials(h, plist[k % len(plist)])
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
