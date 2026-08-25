"""
Render a warpmpm flood run with the REAL NHTSA finite-element vehicle in place of
the single-shell watertight hull.  RUNS INSIDE BLENDER.

    blender --background --python canitford_fe_render.py -- \
        --run <dir with rollout.npz> --obj <FE parts .obj> --frame 60 --out out.png

WHAT IS PHYSICS AND WHAT IS APPEARANCE
  PHYSICS, taken from rollout.npz unmodified:
    every water particle position at the chosen frame, the rigid-body rotation R
    and translation t at that frame, the floor plane, dx, and the run scalars
    printed in the provenance block.
  GEOMETRY, from the NCAC/CCSA LS-DYNA model, unmodified:
    905 named parts with real glazing, wheels, lamps, trim and underbody. This is
    the part that differs from analysis/cycles_render.py, whose own docstring
    records that its hull has "NO separate window, wheel, trim or light geometry".
  FITTED, and reported so it can be audited:
    one rotation about Z and one translation, chosen by matching the FE mesh's
    height profile to the solver's own vehicle particle cloud. No scaling is
    applied, so the 2.5 percent length disagreement between the two stays visible
    rather than being hidden by a fit.
  APPEARANCE, invented here and carrying no data:
    all optics, the paint colour, the lighting, and the water surface, which is a
    Blender points-to-volume isosurface of the real particles and is NOT the
    splashsurf reconstruction the existing pipeline uses. Two different
    reconstructions of the same particles; neither is the solver's own surface,
    because warpmpm computes no surface at all.
"""
import sys, os, json, math, time
import bpy, numpy as np
from mathutils import Matrix, Vector


def argv():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def parse():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--run", default="", help="run dir with rollout.npz; omit for --dry")
    p.add_argument("--dry", action="store_true",
                   help="no flood field: place the vehicle on a studio floor")
    p.add_argument("--obj", required=True)
    p.add_argument("--frame", type=int, default=60)
    p.add_argument("--out", required=True)
    p.add_argument("--half", type=float, default=3.4, help="water crop half-width, m")
    p.add_argument("--voxel", type=float, default=0.026, help="isosurface voxel, m")
    p.add_argument("--radius", type=float, default=0.135, help="particle radius, m")
    p.add_argument("--engine", default="EEVEE", choices=["EEVEE", "CYCLES"])
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--res", type=int, default=1920)
    p.add_argument("--paint", default="0.62,0.13,0.16", help="body paint linear RGB")
    p.add_argument("--label", default="")
    p.add_argument("--cam", default="-7.4,1.8,1.35",
                   help="camera offset from the rigid-body centre, m")
    p.add_argument("--lens", type=float, default=58.0)
    return p.parse_args(argv())


# ----------------------------------------------------------------- scene reset
def wipe():
    for c in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
              bpy.data.lights, bpy.data.cameras, bpy.data.node_groups,
              bpy.data.collections, bpy.data.volumes):
        for item in list(c):
            c.remove(item, do_unlink=True)


# ------------------------------------------------------------------- materials
def mat(name, base, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = tuple(base) + (1.0,)
    for k, v in kw.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return m


def build_materials(paint_rgb):
    M = {}
    M["paint"]    = mat("FE_paint", paint_rgb, Metallic=0.45, Roughness=0.22,
                        **{"Coat Weight": 1.0, "Coat Roughness": 0.03})
    M["glass"]    = mat("FE_glass", (0.55, 0.60, 0.62), Roughness=0.02, IOR=1.46,
                        **{"Transmission Weight": 1.0})
    M["rubber"]   = mat("FE_rubber", (0.028, 0.028, 0.030), Roughness=0.88)
    M["rim"]      = mat("FE_rim", (0.80, 0.81, 0.83), Metallic=1.0, Roughness=0.16)
    M["interior"] = mat("FE_interior", (0.16, 0.15, 0.145), Roughness=0.75)
    M["lamp"]     = mat("FE_lamp", (0.86, 0.87, 0.90), Roughness=0.06, IOR=1.52,
                        **{"Transmission Weight": 0.85})
    M["chrome"]   = mat("FE_chrome", (0.90, 0.90, 0.91), Metallic=1.0, Roughness=0.07)

    w = bpy.data.materials.new("FE_water")
    w.use_nodes = True
    nt = w.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.30, 0.42, 0.40, 1.0)
    b.inputs["Roughness"].default_value = 0.012
    b.inputs["IOR"].default_value = 1.333
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = 1.0
    out = nt.nodes["Material Output"]
    ab = nt.nodes.new("ShaderNodeVolumeAbsorption")
    ab.inputs["Color"].default_value = (0.42, 0.58, 0.50, 1.0)
    ab.inputs["Density"].default_value = 1.1
    nt.links.new(ab.outputs["Volume"], out.inputs["Volume"])
    w.use_screen_refraction = True
    if hasattr(w, "use_raytrace_refraction"):
        w.use_raytrace_refraction = True
    M["water"] = w

    M["chassis"] = mat("FE_chassis", (0.075, 0.072, 0.068), Metallic=0.55, Roughness=0.62)
    M["ground"]  = mat("FE_ground", (0.035, 0.036, 0.038), Roughness=0.42)
    return M



def set_material(ob, m):
    """Assign into slot 0. convert(target='MESH') leaves ONE EMPTY slot behind, so
    append() lands at index 1 while every polygon still points at the empty slot 0
    and the object renders as Blender's default grey. This bit once already."""
    if len(ob.data.materials):
        ob.data.materials[0] = m
    else:
        ob.data.materials.append(m)
    for poly in ob.data.polygons:
        poly.material_index = 0


import re

# Part-name vocabularies differ between NCAC models. The Yaris uses
# "doorrearwindow" / "tirefrontleft"; the Silverado uses "ob-window-front-right",
# a bare "rim" and a bare "tire". These rules are written to cover both, and
# assign() reports its counts so a misclassification is visible rather than silent.
LAMP     = re.compile(r'(headlight|taillight|headlamp|taillamp|lamplens|lightlens)', re.I)
GLASSY   = re.compile(r'(windshield|window|glass)', re.I)
NOTGLASS = re.compile(r'(wheelwell|mech|motor|brkt|bkrt|rail|bar|adhesive|support|'
                      r'washinger|regulator|frame|garnish|weatherstrip)', re.I)
TIREY    = re.compile(r'(tire|tyre)', re.I)
NOTTIRE  = re.compile(r'(rim|mount|wheelwell|hub|disk|carrier|brkt)', re.I)
CHASSIS  = re.compile(r'(^\d+_fr-|frame|crossmember|xmember|leafspring|axle|driveshaft|'
                      r'exhaust|suspension|control-?arm)', re.I)
INTERIOR = re.compile(r'(seat|trim|carpet|dash|instrpanel|headliner|console|sunvisor|'
                      r'glovebox|ip-|interior)', re.I)
CHROME   = re.compile(r'(chrome|grille|grill|badge|emblem|bezel)', re.I)


def is_rim(n):
    """'rim' is a substring of 'trim', so require either a wheel context or a
    separator immediately before it. Covers Yaris 'tirefrontrim', Silverado
    '2000301_rim' and 'mc-rimFrontL', and rejects interior 'trimrear'."""
    low = n.lower()
    if 'rim' not in low or 'bladerim' in low:
        return False
    return ('tire' in low or 'wheel' in low) or bool(re.search(r'[_\-]rim', low))


def classify(n):
    if LAMP.search(n):                                   return "lamp"
    if GLASSY.search(n) and not NOTGLASS.search(n):      return "glass"
    if TIREY.search(n) and not NOTTIRE.search(n):        return "rubber"
    if is_rim(n):                                        return "rim"
    if CHROME.search(n):                                 return "chrome"
    if CHASSIS.search(n):                                return "chassis"
    if INTERIOR.search(n):                               return "interior"
    return "paint"


def assign(objs, M):
    count = {}
    for o in objs:
        key = classify(o.name)
        o.data.materials.clear()
        o.data.materials.append(M[key])
        count[key] = count.get(key, 0) + 1
    return count


# ---------------------------------------------------------------- water surface
def water_surface(pts, voxel, radius, name="Water"):
    """Blender points-to-volume isosurface of real particle positions."""
    me = bpy.data.meshes.new(name + "_pts")
    me.from_pydata([tuple(p) for p in pts], [], [])
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)

    ng = bpy.data.node_groups.new(name + "_nodes", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out='INPUT',  socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi  = ng.nodes.new("NodeGroupInput");  gi.location  = (-600, 0)
    m2p = ng.nodes.new("GeometryNodeMeshToPoints"); m2p.location = (-380, 0)
    p2v = ng.nodes.new("GeometryNodePointsToVolume"); p2v.location = (-160, 0)
    v2m = ng.nodes.new("GeometryNodeVolumeToMesh");   v2m.location = (100, 0)
    sss = ng.nodes.new("GeometryNodeSetShadeSmooth"); sss.location = (300, 0)
    go  = ng.nodes.new("NodeGroupOutput"); go.location = (520, 0)

    def setsock(node, sockname, value):
        if sockname in node.inputs:
            node.inputs[sockname].default_value = value

    setsock(p2v, "Resolution Mode", 'Size')
    setsock(p2v, "Voxel Size", voxel)
    setsock(p2v, "Radius", radius)
    setsock(p2v, "Density", 1.0)
    setsock(v2m, "Resolution Mode", 'Size')
    setsock(v2m, "Voxel Size", voxel)
    setsock(v2m, "Threshold", 0.28)
    setsock(v2m, "Adaptivity", 0.0)

    L = ng.links.new
    L(gi.outputs[0], m2p.inputs["Mesh"])
    L(m2p.outputs["Points"], p2v.inputs["Points"])
    L(p2v.outputs["Volume"], v2m.inputs["Volume"])
    L(v2m.outputs["Mesh"], sss.inputs["Geometry"])
    if "Shade Smooth" in sss.inputs:
        sss.inputs["Shade Smooth"].default_value = True
    L(sss.outputs["Geometry"], go.inputs[0])

    md = ob.modifiers.new(name + "_gn", 'NODES')
    md.node_group = ng

    # Realise the isosurface before shading it. Calling shade_smooth() on the
    # source point mesh silently does nothing, because the geometry the renderer
    # sees is generated by the modifier, not stored in the mesh. Left flat-shaded
    # the isosurface returns a specular highlight per facet and reads as snow.
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    sm = ob.modifiers.new(name + "_smooth", 'SMOOTH')
    sm.factor = 1.0
    sm.iterations = 16
    bpy.ops.object.modifier_apply(modifier=sm.name)
    ob.data.shade_smooth()
    print("WATER isosurface: %d verts %d faces, shade_smooth applied"
          % (len(ob.data.vertices), len(ob.data.polygons)))
    return ob


# ------------------------------------------------------------------------- fit
def fit_fe_to_hull(V, vf):
    """Rotation about Z (+/-90) chosen by height-profile match, then bbox-centre offset."""
    def profile(P, axis, nb=24):
        a = P[:, axis]
        e = np.linspace(a.min(), a.max(), nb + 1)
        z0, z1 = P[:, 2].min(), P[:, 2].max()
        out = np.zeros(nb)
        for i in range(nb):
            m = (a >= e[i]) & (a <= e[i + 1])
            out[i] = (P[m, 2].max() - z0) if m.any() else 0.0
        return out / (z1 - z0)

    pv, pn = profile(vf, 1), profile(V, 0)
    ep, em = np.abs(pn - pv).mean(), np.abs(pn[::-1] - pv).mean()
    sign = +1 if ep < em else -1
    th = math.pi / 2 * sign
    Rz = np.array([[math.cos(th), -math.sin(th), 0],
                   [math.sin(th),  math.cos(th), 0], [0, 0, 1]])
    Vr = V @ Rz.T
    off = (vf.min(0) + vf.max(0)) / 2 - (Vr.min(0) + Vr.max(0)) / 2
    return sign, Rz, off, float(ep), float(em)


# ------------------------------------------------------------------------ main
def main():
    a = parse()
    t0 = time.time()
    if a.dry:
        d = None
        f = -1
        water = np.zeros((0, 3))
        R, t = np.eye(3), np.zeros(3)
        vf = None
        floor = 0.0; dx = float("nan")
    else:
        d = np.load(os.path.join(a.run, "rollout.npz"))
        f = a.frame
        water = d["water"][f].astype(np.float64)
        R, t  = d["R"][f].astype(np.float64), d["t"][f].astype(np.float64)
        vf    = d["veh_particles_vehframe"].astype(np.float64)
        floor = float(d["floor"]); dx = float(d["dx"])

    wipe()
    scene = bpy.context.scene
    M = build_materials([float(x) for x in a.paint.split(",")])

    # ---- vehicle: import, fit to the solver's own hull, then apply the solver pose
    before = set(bpy.data.objects.keys())
    bpy.ops.wm.obj_import(filepath=a.obj, use_split_objects=True,
                          forward_axis='Y', up_axis='Z', validate_meshes=True)
    parts = [bpy.data.objects[n] for n in (set(bpy.data.objects.keys()) - before)]

    V = np.asarray([v.co[:] for o in parts for v in o.data.vertices])
    if vf is None:
        sign, ep, em = 1, float("nan"), float("nan")
        Rz  = np.eye(3)
        off = -np.array([(V[:, 0].min() + V[:, 0].max()) / 2,
                         (V[:, 1].min() + V[:, 1].max()) / 2, V[:, 2].min()])
    else:
        sign, Rz, off, ep, em = fit_fe_to_hull(V, vf)
    Vfit = V @ Rz.T + off

    ang = (math.pi / 2 * sign) if vf is not None else 0.0
    Mfit  = Matrix.Translation(Vector(off)) @ Matrix.Rotation(ang, 4, 'Z')
    Mpose = Matrix.Translation(Vector(t)) @ Matrix(R.tolist()).to_4x4()
    Mall  = Mpose @ Mfit
    veh = bpy.data.collections.new("FE_vehicle")
    scene.collection.children.link(veh)
    for o in parts:
        o.matrix_world = Mall @ o.matrix_world
        for c in list(o.users_collection):
            c.objects.unlink(o)
        veh.objects.link(o)
    counts = assign(parts, M)

    cx, cy = float(t[0]), float(t[1])

    # ---- water: crop to the render window, then isosurface
    if a.dry:
        wpts = np.zeros((0, 3))
        surround_z = floor
    else:
        m = ((np.abs(water[:, 0] - cx) < a.half) & (np.abs(water[:, 1] - cy) < a.half))
        wpts = water[m]
        wob = water_surface(wpts, a.voxel, a.radius)
        set_material(wob, M["water"])

    # ---- surround: flat water beyond the solver domain, APPEARANCE ONLY
    if not a.dry:
        surround_z = float(np.percentile(wpts[:, 2], 97))
        bpy.ops.mesh.primitive_plane_add(size=140, location=(cx, cy, surround_z))
        sur = bpy.context.active_object; sur.name = "Surround"
        set_material(sur, M["water"])

    # ---- ground at the solver's own floor plane
    bpy.ops.mesh.primitive_plane_add(size=120, location=(cx, cy, floor))
    g = bpy.context.active_object; g.name = "Floor"
    set_material(g, M["ground"])

    # ---- lights
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
    scene.collection.objects.link(sun)
    sun.data.energy = 3.6; sun.data.angle = math.radians(2.5)
    sun.rotation_euler = (math.radians(52), 0, math.radians(38))
    key = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'AREA'))
    scene.collection.objects.link(key)
    key.data.energy = 2600; key.data.size = 12
    key.location = (cx + 7, cy - 9, 7); key.rotation_euler = (math.radians(52), 0, math.radians(38))

    w = bpy.data.worlds.new("W"); scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.38, 0.45, 0.56, 1.0); bg.inputs[1].default_value = 1.0

    # ---- camera, low three-quarter so the waterline reads
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(cam); scene.camera = cam
    cam.data.lens = a.lens
    _cx, _cy, _cz = [float(v) for v in a.cam.split(",")]
    cam.location = (cx + _cx, cy + _cy, floor + _cz)
    emp = bpy.data.objects.new("Aim", None); scene.collection.objects.link(emp)
    emp.location = (cx, cy, floor + 0.55)
    c = cam.constraints.new('TRACK_TO'); c.target = emp
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

    # ---- render
    scene.render.resolution_x = a.res
    scene.render.resolution_y = int(a.res * 9 / 16)
    scene.render.filepath = a.out
    scene.render.image_settings.file_format = 'PNG'
    if a.engine == "CYCLES":
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = a.samples
        scene.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type = 'METAL'
            prefs.get_devices()
            for dv in prefs.devices:
                dv.use = True
            scene.cycles.device = 'GPU'
        except Exception as e:
            print("cycles GPU unavailable, CPU:", e)
    else:
        scene.render.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = a.samples
        scene.eevee.use_raytracing = True
        scene.eevee.use_shadows = True

    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)

    prov = {
        "run": os.path.basename(os.path.normpath(a.run)),
        "frame": f,
        "engine": a.engine,
        "fe_obj": os.path.basename(a.obj),
        "fe_parts_rendered": len(parts),
        "material_counts": counts,
        "fit_rotation_deg_about_z": 90 * sign,
        "fit_profile_err_plus": ep,
        "fit_profile_err_minus": em,
        "fit_offset_m": [float(x) for x in off],
        "fe_span_m_fitted": [float(x) for x in (Vfit.max(0) - Vfit.min(0))],
        "solver_hull_span_m": ([float(x) for x in (vf.max(0) - vf.min(0))]
                               if vf is not None else None),
        "span_ratio_fe_over_solver": ([float(x) for x in
                                       ((Vfit.max(0) - Vfit.min(0)) / (vf.max(0) - vf.min(0)))]
                                      if vf is not None else None),
        "bbox_residual_lo_m": ([float(x) for x in (Vfit.min(0) - vf.min(0))]
                               if vf is not None else None),
        "bbox_residual_hi_m": ([float(x) for x in (Vfit.max(0) - vf.max(0))]
                               if vf is not None else None),
        "water_particles_total": int(water.shape[0]),
        "water_particles_in_window": int(wpts.shape[0]),
        "isosurface": {"voxel_m": a.voxel, "radius_m": a.radius,
                       "method": "blender points-to-volume, NOT splashsurf"},
        "solver_scalars": ({k: float(d[k]) for k in
                            ("dx", "floor", "depth", "velocity", "mass", "h", "lim")}
                           if d is not None else "DRY: no rollout loaded, no solver data"),
        "surround_z_m": surround_z,
        "n_grid": (int(d["n_grid"]) if d is not None else None),
        "rigid_t_m": [float(x) for x in t],
        "dry": bool(a.dry),
        "seconds": round(time.time() - t0, 1),
    }
    with open(os.path.splitext(a.out)[0] + "_provenance.json", "w") as fh:
        json.dump(prov, fh, indent=2)
    print(json.dumps(prov, indent=2))


main()
