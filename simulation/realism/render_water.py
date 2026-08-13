"""Water-shaded render of the force-coupled Yaris hull, three cameras, CPU raytraced.

WHY A RAYTRACER AND NOT THE EXISTING PIPELINE
---------------------------------------------
`renders/yaris_render_s1/render_hero_g64_m1100_2026-08-06.py` is the closest existing
reference and its own docstring records the blocker verbatim:

    "Water shading: screen-space PBR + depth-peeled transparency. This VTK build ships no
     OSPRay raytracing module, so there is no true refraction, transmission or caustics."

Refraction is on the list this render is asked for, so the VTK path cannot deliver it.
That path is also unavailable here: neither `pyvista` nor `vtk` is importable in any venv
on this machine (checked live, four interpreters). `render_frames.py` and
`render_frames_pyvista.py` are both pyvista-based and hit the same wall.

So this is a small dependency-light raytracer: numpy, scipy, PIL, trimesh, OpenEXR. It
does real Snell refraction, real Fresnel, and Beer-Lambert transmission, none of which
the reference path can do. No engine is forked and Genesis/Nyx is not involved.

WHAT IS PHYSICAL AND WHAT IS AN APPROXIMATION, STATED UP FRONT
--------------------------------------------------------------
PHYSICAL     Snell refraction at the air/water interface (n = 1.333), Schlick Fresnel,
             Beer-Lambert attenuation along the true refracted path length, GGX specular
             against a real captured sky, and an exact analytic intersection of the
             refracted ray with the floor plane.
APPROXIMATE  the refracted ray is intersected analytically with the FLOOR, but the hull
             seen through water is composited in screen space rather than by a second
             mesh cast. Foam is a heuristic on surface speed and surface slope; it is not
             an air-entrainment model and must not be described as one.

THE GEOMETRY IS THE SIMULATION'S OWN
------------------------------------
The heightfield comes from `proto_hull_float.py --dump-hf`, written by the SAME run that
is scored, so the render shows the validated physics rather than a second scene. The hull
is the decimated mesh the SDF was built from, placed by the pose the rigid-body integrator
actually produced, in the body frame `hull_sdf.py:233` defines
(`centred = dv - 0.5*(dv.min + dv.max)`), so render pose and collision pose agree by
construction rather than by eye.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WATER_IOR = 1.333
# Beer-Lambert extinction for clear water, per metre, RGB. Red is absorbed ~50x more
# strongly than blue, which is why deep water reads blue-green; this is the mechanism
# behind "depth-appropriate colour falloff" rather than a tinted overlay.
EXTINCTION = np.array([0.45, 0.09, 0.035], dtype=np.float32)
# Foam thresholds, set from the dumped fields rather than by eye. See shade().
FOAM_SPEED = 0.16      # m/s
FOAM_SLOPE = 1.60      # dimensionless surface gradient
# Free-surface smoothing, in heightfield cells. NOT cosmetic: the dump bins at 0.0250 m
# while the particle spacing at g96 is 0.0365 m, so a bin holds at most one particle and
# the raw max-z field carries sub-particle noise with a median slope of 2.14 (65 degrees).
# Smoothing to roughly one particle spacing is reconstruction, not beautification.
SURFACE_SIGMA = 2.0


# ----------------------------------------------------------------------------- assets
def load_exr(path):
    """Read a latlong HDR environment from OpenEXR into HxWx3 float32."""
    import OpenEXR, Imath
    f = OpenEXR.InputFile(str(path))
    dw = f.header()["dataWindow"]
    w, h = dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    chans = f.header()["channels"].keys()
    names = ["R", "G", "B"] if "R" in chans else list(chans)[:3]
    out = [np.frombuffer(f.channel(c, pt), dtype=np.float32).reshape(h, w) for c in names]
    return np.stack(out, axis=-1)


def load_srgb(path, size=None):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if size:
        im = im.resize(size, Image.BILINEAR)
    a = np.asarray(im, dtype=np.float32) / 255.0
    return a ** 2.2                      # to linear


def sample_env(env, d):
    """Equirectangular lookup. `d` is (...,3) world direction, +z up."""
    x, y, z = d[..., 0], d[..., 1], d[..., 2]
    u = (np.arctan2(y, x) / (2 * np.pi) + 0.5) % 1.0
    v = np.arccos(np.clip(z, -1.0, 1.0)) / np.pi
    H, W = env.shape[:2]
    return env[np.clip((v * (H - 1)).astype(np.int32), 0, H - 1),
               np.clip((u * (W - 1)).astype(np.int32), 0, W - 1)]


# ------------------------------------------------------------------------- geometry
def quat_to_R(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def slerp(q0, q1, t):
    q0 = q0 / np.linalg.norm(q0)
    q1 = q1 / np.linalg.norm(q1)
    d = float(np.dot(q0, q1))
    if d < 0.0:
        q1, d = -q1, -d
    if d > 0.9995:
        q = q0 + t * (q1 - q0)
        return q / np.linalg.norm(q)
    th = math.acos(d) * t
    q2 = q1 - q0 * d
    q2 /= np.linalg.norm(q2)
    return q0 * math.cos(th) + q2 * math.sin(th)


def camera_rays(eye, target, up, fov_deg, W, H):
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    ar = W / H
    th = math.tan(math.radians(fov_deg) * 0.5)
    px = (np.arange(W, dtype=np.float32) + 0.5) / W * 2 - 1
    py = 1 - (np.arange(H, dtype=np.float32) + 0.5) / H * 2
    PX, PY = np.meshgrid(px, py)
    d = (f[None, None, :] + (PX * ar * th)[..., None] * r[None, None, :]
         + (PY * th)[..., None] * u[None, None, :])
    return d / np.linalg.norm(d, axis=-1, keepdims=True)


def rasterize_mesh(verts, faces, eye, target, up, fov_deg, W, H):
    """Z-buffer rasteriser returning (depth, normal, mask).

    A rasteriser rather than a ray cast because trimesh's pure-numpy ray backend tests
    every triangle against every ray: 39k faces x ~500k rays is 2e10 operations. Back-face
    culling plus a per-triangle screen bounding box keeps this to a few seconds.
    """
    f = target - eye
    f = f / np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    M = np.stack([r, u, -f])                       # world -> camera
    cam = (verts - eye) @ M.T
    zc = -cam[:, 2]
    ar, th = W / H, math.tan(math.radians(fov_deg) * 0.5)
    with np.errstate(divide="ignore", invalid="ignore"):
        sx = (cam[:, 0] / (zc * th * ar) * 0.5 + 0.5) * W
        sy = (1 - (cam[:, 1] / (zc * th) * 0.5 + 0.5)) * H

    tri = faces
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    ok = (zc[a] > 1e-3) & (zc[b] > 1e-3) & (zc[c] > 1e-3)
    e0 = verts[b] - verts[a]
    e1 = verts[c] - verts[a]
    nrm = np.cross(e0, e1)
    nl = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = nrm / np.maximum(nl, 1e-12)
    # face away from the camera -> cull
    ctr = (verts[a] + verts[b] + verts[c]) / 3.0
    ok &= (np.einsum("ij,ij->i", nrm, eye[None, :] - ctr) > 0)
    idx = np.flatnonzero(ok)

    depth = np.full((H, W), np.inf, dtype=np.float32)
    normal = np.zeros((H, W, 3), dtype=np.float32)
    for t in idx:
        i0, i1, i2 = tri[t]
        x0, y0, z0 = sx[i0], sy[i0], zc[i0]
        x1, y1, z1 = sx[i1], sy[i1], zc[i1]
        x2, y2, z2 = sx[i2], sy[i2], zc[i2]
        xlo = max(int(math.floor(min(x0, x1, x2))), 0)
        xhi = min(int(math.ceil(max(x0, x1, x2))) + 1, W)
        ylo = max(int(math.floor(min(y0, y1, y2))), 0)
        yhi = min(int(math.ceil(max(y0, y1, y2))) + 1, H)
        if xlo >= xhi or ylo >= yhi:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue
        X, Y = np.meshgrid(np.arange(xlo, xhi) + 0.5, np.arange(ylo, yhi) + 0.5)
        l0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
        l1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
        l2 = 1.0 - l0 - l1
        inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not inside.any():
            continue
        zz = l0 * z0 + l1 * z1 + l2 * z2
        sub = depth[ylo:yhi, xlo:xhi]
        win = inside & (zz < sub)
        if win.any():
            sub[win] = zz[win]
            normal[ylo:yhi, xlo:xhi][win] = nrm[t]
    return depth, normal, np.isfinite(depth)


# ------------------------------------------------------------------------- shading
def shade(hf, speed, pose, extent, floor, env, asphalt, cam, W, H, sun_dir, exposure):
    """One frame, one camera. Returns a linear-RGB image."""
    eye, target, up, fov = cam["eye"], cam["target"], cam["up"], cam["fov"]
    d = camera_rays(eye, target, up, fov, W, H)
    o = np.broadcast_to(eye, d.shape)

    x0, x1, y0, y1 = extent
    R = hf.shape[0]
    from scipy.ndimage import gaussian_filter
    fill = float(np.nanpercentile(hf, 50))
    hf = gaussian_filter(np.nan_to_num(hf, nan=fill).astype(np.float32), SURFACE_SIGMA)
    speed = gaussian_filter(speed.astype(np.float32), SURFACE_SIGMA)

    def h_at(p):
        """Bilinear heightfield lookup; NaN outside the wet region."""
        fx = np.clip((p[..., 0] - x0) / (x1 - x0) * (R - 1), 0, R - 1)
        fy = np.clip((p[..., 1] - y0) / (y1 - y0) * (R - 1), 0, R - 1)
        i0_, j0_ = np.floor(fx).astype(np.int32), np.floor(fy).astype(np.int32)
        i1_, j1_ = np.minimum(i0_ + 1, R - 1), np.minimum(j0_ + 1, R - 1)
        tx, ty = fx - i0_, fy - j0_
        g = np.nan_to_num(hf, nan=floor)
        return ((g[i0_, j0_] * (1 - tx) + g[i1_, j0_] * tx) * (1 - ty)
                + (g[i0_, j1_] * (1 - tx) + g[i1_, j1_] * tx) * ty)

    # --- water intersection: march then bisect on f(t) = p_z - h(p_xy) ---------------
    zmax = float(np.nanmax(hf))
    with np.errstate(divide="ignore", invalid="ignore"):
        t_enter = np.where(np.abs(d[..., 2]) > 1e-9, (zmax - o[..., 2]) / d[..., 2], 1e9)
    t_lo = np.clip(t_enter, 0.0, None)
    t_hi = t_lo + 60.0
    N = 96
    ts = t_lo[..., None] + (t_hi - t_lo)[..., None] * (np.arange(N) / (N - 1))
    hit_t = np.full(d.shape[:2], np.inf, dtype=np.float32)
    prev = None
    for k in range(N):
        p = o + d * ts[..., k, None]
        fk = p[..., 2] - h_at(p)
        if prev is not None:
            cross = (prev > 0) & (fk <= 0) & np.isinf(hit_t)
            if cross.any():
                a_, b_ = ts[..., k - 1], ts[..., k]
                for _ in range(24):                    # bisect to sub-mm
                    m = 0.5 * (a_ + b_)
                    pm = o + d * m[..., None]
                    fm = pm[..., 2] - h_at(pm)
                    a_ = np.where(fm > 0, m, a_)
                    b_ = np.where(fm > 0, b_, m)
                hit_t = np.where(cross, 0.5 * (a_ + b_), hit_t)
        prev = fk
    water = np.isfinite(hit_t)
    pw = o + d * np.where(water, hit_t, 0.0)[..., None]
    inside_xy = ((pw[..., 0] > x0) & (pw[..., 0] < x1)
                 & (pw[..., 1] > y0) & (pw[..., 1] < y1))
    water &= inside_xy

    # --- water normal from the heightfield gradient ---------------------------------
    dx = (x1 - x0) / (R - 1)
    dhdx, dhdy = np.gradient(np.nan_to_num(hf, nan=floor).astype(np.float32), dx)
    def grad_at(p, g):
        fx = np.clip((p[..., 0] - x0) / (x1 - x0) * (R - 1), 0, R - 1).astype(np.int32)
        fy = np.clip((p[..., 1] - y0) / (y1 - y0) * (R - 1), 0, R - 1).astype(np.int32)
        return g[fx, fy]
    nwx, nwy = -grad_at(pw, dhdx), -grad_at(pw, dhdy)
    nw = np.stack([nwx, nwy, np.ones_like(nwx)], axis=-1)
    nw /= np.linalg.norm(nw, axis=-1, keepdims=True)

    # --- floor: analytic plane, tiled asphalt ---------------------------------------
    def floor_colour(orig, dirs):
        with np.errstate(divide="ignore", invalid="ignore"):
            tf = (floor - orig[..., 2]) / dirs[..., 2]
        good = np.isfinite(tf) & (tf > 0)
        pf = orig + dirs * np.where(good, tf, 0.0)[..., None]
        AH, AW = asphalt.shape[:2]
        ui = (np.mod(pf[..., 0] / 2.0, 1.0) * (AW - 1)).astype(np.int32)
        vi = (np.mod(pf[..., 1] / 2.0, 1.0) * (AH - 1)).astype(np.int32)
        col = asphalt[vi, ui]
        sky_up = sample_env(env, np.array([0.0, 0.0, 1.0]))
        lam = np.clip(sun_dir[2], 0.0, 1.0)
        return col * (0.30 * sky_up + 1.15 * lam), tf, good

    base, t_floor, floor_ok = floor_colour(o, d)
    img = np.where(water[..., None], 0.0, base)
    # sky where the ray escapes upward and misses the floor
    esc = (~water) & (~floor_ok)
    img = np.where(esc[..., None], sample_env(env, d), img)

    # --- hull ------------------------------------------------------------------------
    hull = shade.hull_cache
    if hull is not None:
        hdepth, hnrm, hmask = hull
        cam_f = target - eye
        cam_f = cam_f / np.linalg.norm(cam_f)
        ndl = np.clip(np.einsum("ijk,k->ij", hnrm, sun_dir), 0, 1)
        spec_h = np.clip(np.einsum("ijk,ijk->ij", hnrm, -d), 0, 1) ** 24
        car = (np.array([0.44, 0.46, 0.50], dtype=np.float32)[None, None, :]
               * (0.28 + 0.85 * ndl)[..., None]
               + 0.55 * spec_h[..., None] * sample_env(env, np.array([0.0, 0.0, 1.0])))
        # a hull sample only wins where it is in front of whatever is already there
        depth_water = np.where(water, hit_t, np.inf)
        front = hmask & (hdepth < np.where(np.isfinite(depth_water), depth_water, np.inf))
        img = np.where(front[..., None], car, img)
        water = water & ~front

    # --- the water itself -------------------------------------------------------------
    if water.any():
        cosi = np.clip(np.einsum("ijk,ijk->ij", -d, nw), 0, 1)
        # Schlick Fresnel, F0 for air->water
        F0 = ((1 - WATER_IOR) / (1 + WATER_IOR)) ** 2
        F = F0 + (1 - F0) * (1 - cosi) ** 5

        refl = d - 2 * np.einsum("ijk,ijk->ij", d, nw)[..., None] * nw
        refl_c = sample_env(env, refl)
        # GGX-ish sun glint on the reflected lobe
        hv = (-d + sun_dir[None, None, :])
        hv /= np.linalg.norm(hv, axis=-1, keepdims=True)
        ndh = np.clip(np.einsum("ijk,ijk->ij", nw, hv), 0, 1)
        a2 = 0.0025
        ggx = a2 / (np.pi * (ndh ** 2 * (a2 - 1) + 1) ** 2)
        refl_c = refl_c + (2.2 * ggx)[..., None] * np.array([1.0, 0.97, 0.90], np.float32)

        # Snell refraction, then EXACT analytic hit on the floor plane
        eta = 1.0 / WATER_IOR
        k = 1 - eta * eta * (1 - cosi ** 2)
        tdir = eta * d + (eta * cosi - np.sqrt(np.clip(k, 0, None)))[..., None] * nw
        tdir /= np.linalg.norm(tdir, axis=-1, keepdims=True)
        trans_c, t_ref, ref_ok = floor_colour(pw, tdir)
        path = np.where(ref_ok, t_ref, 0.0)
        trans_c = trans_c * np.exp(-EXTINCTION[None, None, :] * path[..., None])

        col_w = (1 - F)[..., None] * trans_c + F[..., None] * refl_c

        # --- foam: fast-moving OR steep surface, which is bow wave and wake ----------
        sp = grad_at(pw, speed)
        slope = np.sqrt(grad_at(pw, dhdx) ** 2 + grad_at(pw, dhdy) ** 2)
        # Foam keys on surface speed and on surface slope, which is where a bow wave and a
        # wake actually live. THRESHOLDS ARE SET FROM THE DATA, not by eye: for this dump
        # surface speed peaks at 0.193 m/s and the smoothed slope has p90 = 1.19, so foam
        # is correctly near-absent here. That is not a failure of the term. This is a
        # STATIC float test with no through-flow, so it HAS no bow wave; the arm that does
        # is the channel scene, and this shader is what would render it.
        foam = (np.clip((sp - FOAM_SPEED) / 0.10, 0, 1) * 0.8
                + np.clip((slope - FOAM_SLOPE) / 1.5, 0, 1))
        foam = np.clip(foam, 0, 1) ** 1.3
        foam_c = np.array([0.92, 0.95, 0.97], np.float32)[None, None, :] * (
            0.35 * sample_env(env, np.array([0.0, 0.0, 1.0]))
            + 0.9 * np.clip(sun_dir[2], 0, 1))
        col_w = (1 - foam)[..., None] * col_w + foam[..., None] * foam_c

        img = np.where(water[..., None], col_w, img)
    return img * exposure


shade.hull_cache = None


def tonemap(img):
    """ACES-ish filmic curve, then sRGB gamma."""
    x = np.clip(img, 0, None)
    a, b, c, d_, e = 2.51, 0.03, 2.43, 0.59, 0.14
    y = np.clip((x * (a * x + b)) / (x * (c * x + d_) + e), 0, 1)
    return (np.clip(y, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)


# ------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True, help="heightfield dump from --dump-hf")
    ap.add_argument("--ply", required=True)
    ap.add_argument("--hdri", required=True)
    ap.add_argument("--asphalt", required=True)
    ap.add_argument("--frame", type=float, default=-1.0,
                    help="dumped-frame index. FRACTIONAL values are interpolated, which "
                         "is how a 15 fps physics dump drives a 30 fps render.")
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--height", type=int, default=540)
    ap.add_argument("--exposure", type=float, default=1.0)
    ap.add_argument("--cameras", default="wide,tracking,hero")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--target-faces", type=int, default=39381)
    args = ap.parse_args()

    from PIL import Image
    import hull_sdf as H

    z = np.load(args.npz)
    height, speed, pose = z["height"], z["speed"], z["pose"]
    extent, floor = z["extent"], float(z["floor"])
    hull_ext = z["hull_extents"]
    nfr = len(height)
    fi = (nfr - 1) if args.frame < 0 else float(args.frame)

    # --- MOTION INTERPOLATION. The dump is every `dump_every` physics frames, so it is
    # coarser than a 30 fps render; height and speed lerp, and the pose quaternion SLERPS
    # rather than lerping, because a lerped quaternion is not a rotation.
    i0 = int(np.floor(fi)); i1 = min(i0 + 1, nfr - 1); tt = fi - i0
    hf = (1 - tt) * height[i0] + tt * height[i1]
    sp = (1 - tt) * speed[i0] + tt * speed[i1]
    pos = (1 - tt) * pose[i0][:3] + tt * pose[i1][:3]
    quat = slerp(pose[i0][3:].astype(float), pose[i1][3:].astype(float), tt)

    env = load_exr(args.hdri)
    # brightest environment texel = the sun, so lighting direction is taken FROM the
    # captured sky rather than invented
    H_, W_ = env.shape[:2]
    li = int(np.argmax(env.sum(-1)))
    vy, ux = divmod(li, W_)
    th = (vy / (H_ - 1)) * np.pi
    ph = ((ux / (W_ - 1)) - 0.5) * 2 * np.pi
    sun = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph),
                    math.cos(th)], dtype=np.float32)
    if sun[2] < 0.05:
        sun = np.array([0.35, 0.25, 0.90], np.float32)
    sun /= np.linalg.norm(sun)
    asphalt = load_srgb(args.asphalt, (512, 512))

    verts, faces = H.read_ply_binary(args.ply)
    span = float((verts.max(axis=0) - verts.min(axis=0)).max())
    dv, df = H.cluster_decimate(verts, faces, span * 0.015)
    centred = dv - 0.5 * (dv.min(axis=0) + dv.max(axis=0))     # hull_sdf.py:233 body frame
    world = centred @ quat_to_R(quat).T + pos

    cx, cy = 0.5 * (extent[0] + extent[1]), 0.5 * (extent[2] + extent[3])
    surf = float(np.nanpercentile(hf, 60))
    # Frame on the HULL, not the tank. The tank is only ~6.4 m across while the hull is
    # 4.28 m long, so a camera placed as a fraction of the domain sits inside the car.
    HL = float(np.max(hull_ext))
    hub = np.array([float(pos[0]), float(pos[1]), surf], dtype=float)

    def rig(dist, elev, azim_deg, fov, look_dz=0.0):
        a = math.radians(azim_deg)
        return dict(eye=hub + np.array([dist * math.cos(a), dist * math.sin(a), elev]),
                    target=hub + np.array([0.0, 0.0, look_dz]),
                    up=np.array([0.0, 0.0, 1.0]), fov=fov)

    CAMS = {
        # wide establishing: whole tank in frame, elevated, hull reads small in context
        "wide": rig(dist=3.4 * HL, elev=1.55 * HL, azim_deg=205.0, fov=40.0,
                    look_dz=0.15 * HL),
        # low near-water tracking: lens a hand's width above the surface, so the view
        # grazes it and Fresnel approaches 1, which is where water reads as water
        "tracking": rig(dist=2.1 * HL, elev=0.075 * HL, azim_deg=250.0, fov=46.0,
                        look_dz=0.10 * HL),
        # hero close-up at the waterline, three-quarter view on the hull
        "hero": rig(dist=1.45 * HL, elev=0.34 * HL, azim_deg=222.0, fov=34.0,
                    look_dz=0.22 * float(hull_ext[2])),
    }

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    for name in args.cameras.split(","):
        cam = CAMS[name.strip()]
        shade.hull_cache = rasterize_mesh(world, df, cam["eye"], cam["target"], cam["up"],
                                          cam["fov"], args.width, args.height)
        img = shade(hf, sp, pose, extent, floor, env, asphalt, cam,
                    args.width, args.height, sun, args.exposure)
        out = Path(args.outdir) / f"{name.strip()}_f{fi:07.2f}.png"
        Image.fromarray(tonemap(img)).save(out)
        print(f"wrote {out}  hull px {int(shade.hull_cache[2].sum())}")


if __name__ == "__main__":
    main()
