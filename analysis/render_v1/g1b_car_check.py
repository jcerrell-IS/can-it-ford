from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from geom_live import YARIS, load_vehicle_local, scene_grid

OUT_MESH = "/Users/josie/can-it-ford/figures/car_check.png"
OUT_PTS = "/Users/josie/can-it-ford/renders/yaris_render_s1/car_check_points_R1.png"
AZIMS = (-24, -70, -118, 160)
ELEV = 20
LIGHT = np.array([0.4, -0.7, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def decimate(mesh, target=8000):
    for kw in ({"face_count": target}, {"percent": target / max(len(mesh.faces), 1)}):
        try:
            d = mesh.simplify_quadric_decimation(**kw)
            if d is not None and len(d.faces) > 0:
                return d, "simplify_quadric_decimation(%s)" % list(kw)[0]
        except Exception as exc:
            last = exc
    print("DECIMATION FAILED", type(last).__name__, str(last)[:200])
    return None, "failed"


def limits(ax, ext):
    r = float(max(ext)) / 2.0
    ax.set_xlim(-r, r)
    ax.set_ylim(-r, r)
    ax.set_zlim(0.0, 2 * r)


v = load_vehicle_local(YARIS)
ext = v.extent
g = scene_grid(ext, 0.30, 64)
dec, how = decimate(v.mesh, 8000)
print("decimation:", how, "faces", None if dec is None else len(dec.faces))

if dec is not None:
    tri = np.asarray(dec.vertices)[np.asarray(dec.faces)]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.where(ln == 0, 1.0, ln)
    shade = np.clip(0.28 + 0.72 * np.abs(n @ LIGHT), 0, 1)
    base = np.array([0.90, 0.45, 0.10])
    cols = np.clip(base[None, :] * shade[:, None], 0, 1)
    depth_key = tri[:, :, 0].mean(1)

    fig = plt.figure(figsize=(14, 11), dpi=150)
    fig.patch.set_facecolor("white")
    for k, az in enumerate(AZIMS):
        ax = fig.add_subplot(2, 2, k + 1, projection="3d")
        order = np.argsort(depth_key * np.cos(np.radians(az)) +
                           tri[:, :, 1].mean(1) * np.sin(np.radians(az)))
        pc = Poly3DCollection(tri[order], facecolors=cols[order],
                              edgecolors="none", linewidths=0)
        ax.add_collection3d(pc)
        limits(ax, ext)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=ELEV, azim=az)
        ax.set_axis_off()
        tag = {160: "broadside", -24: "oblique", -70: "end-on-ish",
               -118: "foreshortened (the failed render)"}[az]
        ax.set_title("azim %d, elev %d\n%s" % (az, ELEV, tag), fontsize=11)
    fig.suptitle(
        "G1 geometry check, RUNG R2: decimated hull triangles, no water, no solver\n"
        "2010 Toyota Yaris NCAC coarse v1l, %d faces shown of %d, extent %.3f x %.3f x %.3f m, hull %.4f m3"
        % (len(dec.faces), len(v.mesh.faces), ext[0], ext[1], ext[2], float(v.mesh.volume)),
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT_MESH, facecolor="white")
    print("WROTE", OUT_MESH)

s = v.surface
fig2 = plt.figure(figsize=(14, 11), dpi=150)
fig2.patch.set_facecolor("white")
for k, az in enumerate(AZIMS):
    ax = fig2.add_subplot(2, 2, k + 1, projection="3d")
    ax.scatter(s[:, 0], s[:, 1], s[:, 2], s=0.6, c="#22303f",
               alpha=1.0, linewidths=0, rasterized=True, depthshade=False)
    limits(ax, ext)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=ELEV, azim=az)
    ax.set_axis_off()
    ax.set_title("azim %d, elev %d" % (az, ELEV), fontsize=11)
fig2.suptitle(
    "G1 geometry check, RUNG R1: VehicleBody.surface points only (%d points)" % len(s),
    fontsize=12,
)
fig2.tight_layout(rect=(0, 0, 1, 0.93))
fig2.savefig(OUT_PTS, facecolor="white")
print("WROTE", OUT_PTS)
