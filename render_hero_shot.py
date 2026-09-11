#!/usr/bin/env python
import glob
import os
import sys

import bpy
import mathutils
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
HDRI_PATH = os.path.join(
    PROJECT_ROOT, "assets", "hdri", "kloofendal_43d_clear_puresky_2k.hdr"
)
OUT_PATH = os.path.join(PROJECT_ROOT, "figures", "hero_shot_test.png")
DOWNLOADS = os.path.expanduser("~/Downloads")

RES_X, RES_Y = 1600, 1200
EEVEE_SAMPLES = 96
MAX_POINTS = 150_000
POINT_RADIUS = 0.020
SUBSAMPLE_SEED = 0

_VIRIDIS = np.array(
    [
        [0.267004, 0.004874, 0.329415],
        [0.282623, 0.140926, 0.457517],
        [0.253935, 0.265254, 0.529983],
        [0.206756, 0.371758, 0.553117],
        [0.163625, 0.471133, 0.558148],
        [0.127568, 0.566949, 0.550556],
        [0.134692, 0.658636, 0.517649],
        [0.266941, 0.748751, 0.440573],
        [0.477504, 0.821444, 0.318195],
        [0.741388, 0.873449, 0.149561],
        [0.876168, 0.891125, 0.095095],
        [0.993248, 0.906157, 0.143936],
    ],
    dtype=np.float32,
)


def viridis(t):
    stops = np.linspace(0.0, 1.0, len(_VIRIDIS), dtype=np.float32)
    t = np.clip(t, 0.0, 1.0)
    r = np.interp(t, stops, _VIRIDIS[:, 0])
    g = np.interp(t, stops, _VIRIDIS[:, 1])
    b = np.interp(t, stops, _VIRIDIS[:, 2])
    return np.stack([r, g, b], axis=1).astype(np.float32)


def resolve_frame_path():
    if len(sys.argv) > 1 and sys.argv[1].endswith(".npz"):
        return os.path.abspath(sys.argv[1])
    cands = glob.glob(os.path.join(DOWNLOADS, "particles_mpm_*.npz"))
    if not cands:
        raise FileNotFoundError(
            f"No particles_mpm_*.npz found in {DOWNLOADS} and none passed on argv."
        )
    return max(cands, key=os.path.getmtime)


def load_frame(path):
    d = np.load(path, allow_pickle=True)
    pos = np.asarray(d["pos"], dtype=np.float32)
    vel = np.asarray(d["vel"], dtype=np.float32)
    meta = {}
    for k in ("depth", "velocity", "verdict", "coup_friction", "rho", "run_tag"):
        if k in d:
            meta[k] = d[k].item() if d[k].ndim == 0 else d[k]
    return pos, vel, meta


def subsample(pos, vel, cap, seed):
    if len(pos) <= cap:
        return pos, vel
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(pos), size=cap, replace=False)
    return pos[idx], vel[idx]


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_world_hdri(hdri_path, strength=0.9, z_rotation_deg=200.0):
    if not os.path.isfile(hdri_path):
        raise FileNotFoundError(f"HDRI not found: {hdri_path}")
    world = bpy.data.worlds.new("hero_world")
    world.use_nodes = True
    bpy.context.scene.world = world
    nt = world.node_tree
    nt.nodes.clear()

    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value[2] = np.radians(z_rotation_deg)
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdri_path)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputWorld")

    nt.links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def make_floor(z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.9, 0.0, z))
    floor = bpy.context.active_object
    floor.name = "floor"
    mat = bpy.data.materials.new("floor_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.045, 0.05, 0.06, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.55
    floor.data.materials.append(mat)
    return floor


def make_vehicle(center, dims):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    veh = bpy.context.active_object
    veh.name = "vehicle_proxy"
    veh.scale = (dims[0], dims[1], dims[2])
    bev = veh.modifiers.new("bevel", "BEVEL")
    bev.width = 0.03
    bev.segments = 2
    bpy.ops.object.shade_smooth()

    mat = bpy.data.materials.new("vehicle_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.18, 0.21, 0.26, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.6
    bsdf.inputs["Roughness"].default_value = 0.32
    veh.data.materials.append(mat)
    return veh


def make_water(pos, vel):
    speed = np.linalg.norm(vel, axis=1)
    lo, hi = np.percentile(speed, 1.0), np.percentile(speed, 99.0)
    tnorm = (speed - lo) / (hi - lo + 1e-9)
    rgb = viridis(tnorm)
    rgba = np.concatenate([rgb, np.ones((len(rgb), 1), np.float32)], axis=1)

    me = bpy.data.meshes.new("water_mesh")
    me.from_pydata([tuple(p) for p in pos.tolist()], [], [])
    col = me.color_attributes.new(name="speed_col", type="FLOAT_COLOR", domain="POINT")
    col.data.foreach_set("color", rgba.ravel())
    ob = bpy.data.objects.new("water", me)
    bpy.context.collection.objects.link(ob)

    mat = bpy.data.materials.new("water_mat")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "speed_col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.25
    if "Emission Color" in bsdf.inputs:
        nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 0.35

    ng = bpy.data.node_groups.new("water_gn", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    m2p = ng.nodes.new("GeometryNodeMeshToPoints")
    m2p.inputs["Radius"].default_value = POINT_RADIUS
    setm = ng.nodes.new("GeometryNodeSetMaterial")
    setm.inputs["Material"].default_value = mat
    ng.links.new(gi.outputs[0], m2p.inputs["Mesh"])
    ng.links.new(m2p.outputs["Points"], setm.inputs["Geometry"])
    ng.links.new(setm.outputs["Geometry"], go.inputs[0])
    mod = ob.modifiers.new("gn_points", "NODES")
    mod.node_group = ng
    return ob


def make_area_light(location, target, power=1200.0, size=3.0):
    light_data = bpy.data.lights.new("key", type="AREA")
    light_data.energy = power
    light_data.size = size
    light = bpy.data.objects.new("key_light", light_data)
    bpy.context.collection.objects.link(light)
    light.location = location
    _aim(light, target)
    return light


def make_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("hero_cam")
    cam_data.lens = lens
    cam_data.clip_end = 1000.0
    cam = bpy.data.objects.new("hero_cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    _aim(cam, target)
    bpy.context.scene.camera = cam
    return cam


def _aim(obj, target):
    direction = mathutils.Vector(target) - mathutils.Vector(obj.location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_render():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = EEVEE_SAMPLES
    sc.render.resolution_x = RES_X
    sc.render.resolution_y = RES_Y
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = OUT_PATH


def main():
    frame_path = resolve_frame_path()
    pos, vel, meta = load_frame(frame_path)
    print(f"[hero] frame       : {frame_path}")
    print(f"[hero] particles   : {len(pos)}")
    print(f"[hero] meta        : {meta}")

    pos, vel = subsample(pos, vel, MAX_POINTS, SUBSAMPLE_SEED)
    print(f"[hero] rendering   : {len(pos)} points (cap {MAX_POINTS})")

    floor_z = float(pos[:, 2].min())

    veh_dims = (0.85, 0.55, 0.50)
    veh_center = (1.05, 0.0, floor_z + veh_dims[2] / 2.0)

    cam_target = (0.9, 0.0, floor_z + 0.12)
    cam_loc = (2.7, -2.6, 1.7)
    light_loc = (2.2, -1.6, 3.0)

    reset_scene()
    make_world_hdri(HDRI_PATH)
    make_floor(z=floor_z)
    make_water(pos, vel)
    make_vehicle(veh_center, veh_dims)
    make_area_light(light_loc, veh_center)
    make_camera(cam_loc, cam_target)
    configure_render()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    print(f"[hero] engine      : {bpy.context.scene.render.engine}")
    print(f"[hero] output      : {OUT_PATH}")
    bpy.ops.render.render(write_still=True)
    print("[hero] done.")


if __name__ == "__main__":
    main()
