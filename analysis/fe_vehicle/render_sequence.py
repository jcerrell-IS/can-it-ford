"""
Render a warpmpm run to a frame sequence with the real NHTSA FE vehicle.
RUNS INSIDE BLENDER. The vehicle is imported ONCE and re-posed per frame; only
the water isosurface is rebuilt, because only the water moves independently.

Every frame's water particle positions and rigid pose come from rollout.npz
unmodified. The optics, the paint and the isosurface reconstruction are invented
here and carry no data. warpmpm computes no surface and no optics of any kind.
"""
import sys, os, json, math, time
import bpy, bmesh, numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, "/Users/josie/blender_nhtsa")

# Shared helpers first: this file's parse() must WIN, and the shared module
# defines one too. Exec order is the only thing deciding that.
base = open("/Users/josie/blender_nhtsa/canitford_fe_render.py").read()
exec(base.split("# ------------------------------------------------------------------------ main")[0]
     .split('"""', 2)[2])




def argv():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def parse():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--obj", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=-1)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--half", type=float, default=5.0)
    p.add_argument("--voxel", type=float, default=0.032)
    p.add_argument("--radius", type=float, default=0.115)
    # DEFAULT CHANGED TO CYCLES 2026-08-26, measured not assumed. On Blender
    # 5.2.0 LTS the EEVEE path of this script renders this scene almost black:
    # the vehicle reads as a silhouette and the water surface loses its
    # refraction entirely, at every camera angle tried. It is NOT a bad engine
    # id -- `BLENDER_EEVEE` is the only entry in RenderSettings.engine's enum on
    # 5.2 and it assigns cleanly -- so EEVEE is selected correctly and simply
    # does not light this scene, most likely because a transmissive isosurface
    # with no light probe falls back to near-black. Cycles renders the identical
    # scene correctly at 11.6 s/frame at 1600 px / 64 samples on this Mac, which
    # is only about 2.5x the EEVEE cost, so there is no reason to prefer EEVEE.
    # Pass --engine EEVEE to get the old behaviour.
    p.add_argument("--engine", default="CYCLES")
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--res", type=int, default=1280)
    p.add_argument("--paint", default="0.10,0.13,0.16")
    p.add_argument("--cam", default="-11.0,4.6,2.3")
    p.add_argument("--lens", type=float, default=58.0)
    p.add_argument("--decimate", type=float, default=0.0)
    return p.parse_args(argv())


def main():
    a = parse()
    d = np.load(os.path.join(a.run, "rollout.npz"))
    W, R, T = d["water"], d["R"], d["t"]
    vf = d["veh_particles_vehframe"].astype(np.float64)
    floor = float(d["floor"])
    nfr = W.shape[0]
    end = nfr - 1 if a.end < 0 else min(a.end, nfr - 1)
    os.makedirs(a.outdir, exist_ok=True)

    wipe()
    scene = bpy.context.scene
    M = build_materials([float(x) for x in a.paint.split(",")])

    before = set(bpy.data.objects.keys())
    bpy.ops.wm.obj_import(filepath=a.obj, use_split_objects=True,
                          forward_axis='Y', up_axis='Z', validate_meshes=True)
    parts = [bpy.data.objects[n] for n in (set(bpy.data.objects.keys()) - before)]
    V = np.asarray([v.co[:] for o in parts for v in o.data.vertices])
    sign, Rz, off, ep, em = fit_fe_to_hull(V, vf)
    print("FIT rotation %+d deg  profile err %.5f vs %.5f" % (90 * sign, ep, em), flush=True)
    Mfit = Matrix.Translation(Vector(off)) @ Matrix.Rotation(math.pi / 2 * sign, 4, 'Z')
    counts = assign(parts, M)
    print("MATERIALS", counts, flush=True)

    if a.decimate > 0:
        for o in parts:
            if len(o.data.polygons) > 400:
                m = o.modifiers.new("dec", 'DECIMATE'); m.ratio = a.decimate
    rest = {o.name: o.matrix_world.copy() for o in parts}

    # camera and lights are placed once, on the frame-0 vehicle centre
    cx, cy = float(T[a.start][0]), float(T[a.start][1])
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
    scene.collection.objects.link(sun)
    sun.data.energy = 3.4; sun.data.angle = math.radians(2.5)
    sun.rotation_euler = (math.radians(52), 0, math.radians(38))
    key = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'AREA'))
    scene.collection.objects.link(key)
    key.data.energy = 2400; key.data.size = 12
    key.location = (cx + 7, cy - 9, 7); key.rotation_euler = (math.radians(52), 0, math.radians(38))
    w = bpy.data.worlds.new("W"); scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.38, 0.45, 0.56, 1.0); bg.inputs[1].default_value = 1.0

    bpy.ops.mesh.primitive_plane_add(size=140, location=(cx, cy, floor))
    g = bpy.context.active_object; g.name = "Floor"; set_material(g, M["ground"])

    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(cam); scene.camera = cam
    cam.data.lens = a.lens
    ox, oy, oz = [float(v) for v in a.cam.split(",")]
    cam.location = (cx + ox, cy + oy, floor + oz)
    emp = bpy.data.objects.new("Aim", None); scene.collection.objects.link(emp)
    emp.location = (cx, cy, floor + 0.55)
    c = cam.constraints.new('TRACK_TO'); c.target = emp
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

    scene.render.resolution_x = a.res
    scene.render.resolution_y = int(a.res * 9 / 16)
    scene.render.image_settings.file_format = 'PNG'
    if a.engine == "CYCLES":
        scene.render.engine = 'CYCLES'; scene.cycles.samples = a.samples
        scene.cycles.use_denoising = True
        try:
            pr = bpy.context.preferences.addons['cycles'].preferences
            pr.compute_device_type = 'METAL'; pr.get_devices()
            for dv in pr.devices: dv.use = True
            scene.cycles.device = 'GPU'
        except Exception as e:
            print("cycles cpu:", e)
    else:
        scene.render.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = a.samples
        scene.eevee.use_raytracing = True; scene.eevee.use_shadows = True

    t0 = time.time(); n_done = 0
    for f in range(a.start, end + 1, a.step):
        for o in bpy.data.objects:
            if o.name.startswith(("Water", "Surround")):
                bpy.data.objects.remove(o, do_unlink=True)
        Mpose = Matrix.Translation(Vector(T[f].astype(float))) @ Matrix(R[f].astype(float).tolist()).to_4x4()
        Mall = Mpose @ Mfit
        for o in parts:
            o.matrix_world = Mall @ rest[o.name]
        wat = W[f].astype(np.float64)
        fx, fy = float(T[f][0]), float(T[f][1])
        m = (np.abs(wat[:, 0] - fx) < a.half) & (np.abs(wat[:, 1] - fy) < a.half)
        wpts = wat[m]
        wob = water_surface(wpts, a.voxel, a.radius, name="Water%04d" % f)
        set_material(wob, M["water"])
        sz = float(np.percentile(wpts[:, 2], 97))
        bpy.ops.mesh.primitive_plane_add(size=160, location=(cx, cy, sz))
        sur = bpy.context.active_object; sur.name = "Surround%04d" % f
        set_material(sur, M["water"])
        scene.render.filepath = os.path.join(a.outdir, "f%04d.png" % f)
        bpy.ops.render.render(write_still=True)
        n_done += 1
        print("FRAME %d/%d  %.1f s elapsed  water %d pts  surround_z %.4f"
              % (f, end, time.time() - t0, len(wpts), sz), flush=True)
    print("SEQDONE %d frames in %.1f s" % (n_done, time.time() - t0), flush=True)


main()
