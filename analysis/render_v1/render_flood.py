from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrow, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from geom_live import YARIS, load_vehicle_local, scene_grid

WATER_CMAP = "viridis"
VEH_COLOR = "#f76707"
MESH_COLOR = np.array([0.95, 0.55, 0.20])
MARK_COLOR = "#ff6b00"
ELEV = 20
AZIM = -24
LIGHT = np.array([0.4, -0.7, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def decimate(mesh, target):
    try:
        d = mesh.simplify_quadric_decimation(face_count=target)
        if d is not None and len(d.faces):
            return d
    except Exception as exc:
        print("decimate failed", type(exc).__name__, str(exc)[:120])
    return mesh


def scalebar_2d(ax, x0, y0, length, label):
    ax.add_patch(Rectangle((x0, y0), length, 0.10, facecolor="black",
                           edgecolor="black", zorder=20))
    ax.text(x0 + length / 2, y0 + 0.16, label, ha="center", va="bottom",
            fontsize=9, zorder=20)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--vmax", type=float, default=None)
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--hero", type=int, default=None)
    p.add_argument("--hero-only", action="store_true")
    p.add_argument("--mesh-faces", type=int, default=3000)
    a = p.parse_args()

    run = Path(a.run)
    outdir = Path(a.outdir)
    fdir = outdir / "_frames"
    fdir.mkdir(parents=True, exist_ok=True)

    z = np.load(run / "rollout.npz")
    summ = json.loads((run / "summary.json").read_text())
    water = z["water"]
    speed = z["speed"]
    R = z["R"]
    T = z["t"]
    lim = float(z["lim"])
    floor = float(z["floor"])
    depth = float(z["depth"])
    vel = float(z["velocity"])
    mass = float(z["mass"])
    fps = int(z["fps"])
    nframes = water.shape[0]

    v = load_vehicle_local(YARIS)
    g = scene_grid(v.extent, depth, int(z["n_grid"]))
    v.solidify(g["h"])
    pv = np.asarray(v.particles, dtype=np.float64)
    dec = decimate(v.mesh, a.mesh_faces)
    mv = np.asarray(dec.vertices, dtype=np.float64)
    mf = np.asarray(dec.faces)

    ref0 = np.asarray(z["veh_particles_scene0"], dtype=np.float64)
    pv_dumped = (ref0 - T[0]) @ R[0]
    align = (pv_dumped.min(0) + pv_dumped.max(0)) / 2.0 - (pv.min(0) + pv.max(0)) / 2.0
    mv = mv + align
    surf_v = np.asarray(v.surface, dtype=np.float64) + align
    print("DRAWN BODY = %d hull-surface points (NOT the %d MPM solid particles); "
          "surface extents %s m" % (len(surf_v), len(pv_dumped),
                                    np.round(surf_v.max(0) - surf_v.min(0), 4)))
    rec0 = pv_dumped @ R[0].T + T[0]
    err = float(np.abs(rec0 - ref0).max())
    print("POSE CHECK n_local=%d n_dumped=%d roundtrip_err=%.3e m" % (len(pv), len(ref0), err))
    print("FRAME CHECK mesh_zmin=%.5f particles_zmin_local=%.5f particles_zmin_dumped=%.5f h/2=%.5f"
          % (mv[:, 2].min(), pv[:, 2].min(), pv_dumped[:, 2].min(), float(z["h"]) / 2))
    print("FRAME CHECK mesh_xy_center=%s particles_xy_center_dumped=%s"
          % (np.round((mv.min(0) + mv.max(0))[:2] / 2, 5),
             np.round((pv_dumped.min(0) + pv_dumped.max(0))[:2] / 2, 5)))
    pv = pv_dumped

    vmax = a.vmax if a.vmax is not None else float(np.percentile(speed, 99.0))
    vmin = 0.0
    print("FIXED COLOR LIMITS speed vmin=%.3f vmax=%.3f m/s" % (vmin, vmax))

    with open(run / "metrics.csv") as fh:
        cols = fh.readline().strip().split(",")
    metr = np.loadtxt(run / "metrics.csv", delimiter=",", skiprows=1)
    missing = [c for c in ("dmag", "yaw_deg") if c not in cols]
    if missing:
        raise SystemExit("metrics.csv missing required columns %s; header is %s" % (missing, cols))
    dmag = metr[:, cols.index("dmag")]
    yawd = metr[:, cols.index("yaw_deg")]
    print("METRICS parsed by name from header:", cols)

    cx0, cy0 = float(T[0][0]), float(T[0][1])
    idxs = list(range(0, nframes, a.stride))
    hero = a.hero if a.hero is not None else nframes - 1
    if a.hero_only:
        idxs = [hero]

    written = []
    for f in idxs:
        w = water[f]
        sp = np.clip(speed[f], vmin, vmax)
        vp = surf_v @ R[f].T + T[f]
        mvp = mv @ R[f].T + T[f]
        cx, cy = float(T[f][0]), float(T[f][1])

        fig = plt.figure(figsize=(15.5, 7.0), dpi=110)
        fig.patch.set_facecolor("white")

        ax = fig.add_subplot(1, 2, 1)
        order = np.argsort(sp)
        sc = ax.scatter(w[order, 0], w[order, 1], c=sp[order], cmap=WATER_CMAP,
                        vmin=vmin, vmax=vmax, s=1.4, linewidths=0, rasterized=True)
        ax.scatter(vp[:, 0], vp[:, 1], s=0.7, c=VEH_COLOR, linewidths=0,
                   rasterized=True, zorder=6)
        ax.add_patch(Circle((cx, cy), 2.9, fill=False, edgecolor=MARK_COLOR,
                            linewidth=2.2, zorder=10))
        ax.add_patch(FancyArrow(0.35, 8.75, 1.5, 0, width=0.06, head_width=0.26,
                                head_length=0.32, facecolor="#1c7ed6",
                                edgecolor="#1c7ed6", zorder=15))
        ax.text(0.35, 9.05, "flow", fontsize=10, color="#1c7ed6")
        scalebar_2d(ax, 0.35, 0.35, 2.0, "2 m")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m), surge direction")
        ax.set_ylabel("y (m), vehicle long axis")
        ax.set_title("top-down plan", fontsize=11)
        cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
        cb.set_label("water speed (m/s), fixed limits", fontsize=9)

        ax3 = fig.add_subplot(1, 2, 2, projection="3d")
        crop = ((w[:, 0] >= cx0 - 3.6) & (w[:, 0] <= cx0 + 3.6) &
                (w[:, 1] >= cy0 - 3.2) & (w[:, 1] <= cy0 + 3.2))
        wc = w[crop]
        spc = sp[crop]
        ax3.scatter(wc[:, 0], wc[:, 1], wc[:, 2], c=spc, cmap=WATER_CMAP,
                    vmin=vmin, vmax=vmax, s=1.6, linewidths=0, alpha=0.55,
                    rasterized=True, depthshade=False)
        tri = mvp[mf]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        n = n / np.where(ln == 0, 1.0, ln)
        shade = np.clip(0.30 + 0.70 * np.abs(n @ LIGHT), 0, 1)
        cols = np.clip(MESH_COLOR[None, :] * shade[:, None], 0, 1)
        pc = Poly3DCollection(tri, facecolors=cols, edgecolors="none",
                              linewidths=0, alpha=0.45)
        ax3.add_collection3d(pc)
        ax3.scatter(vp[:, 0], vp[:, 1], vp[:, 2], s=0.5, c=VEH_COLOR,
                    linewidths=0, depthshade=False, rasterized=True)
        gx, gy = np.meshgrid(np.linspace(cx0 - 3.6, cx0 + 3.6, 2),
                             np.linspace(cy0 - 3.2, cy0 + 3.2, 2))
        ax3.plot_surface(gx, gy, np.full_like(gx, floor), color="#c9ced4",
                         alpha=0.30, shade=False, zorder=0)
        ax3.set_xlim(cx0 - 3.6, cx0 + 3.6)
        ax3.set_ylim(cy0 - 3.2, cy0 + 3.2)
        ax3.set_zlim(floor, floor + 1.9)
        ax3.set_box_aspect((7.2, 6.4, 3.4))
        ax3.view_init(elev=ELEV, azim=AZIM)
        ax3.set_xlabel("x (m)", fontsize=9)
        ax3.set_ylabel("y (m)", fontsize=9)
        ax3.set_zlabel("z (m)", fontsize=9)
        ax3.tick_params(labelsize=7)
        ax3.set_title("three-quarter oblique, elev %d" % ELEV, fontsize=11)

        t = f / fps
        fig.suptitle(
            "%s\nt = %5.2f s   |d| = %6.2f cm   yaw = %+5.2f deg   "
            "mass %.0f kg   nominal depth %.2f m   nominal surge %.1f m/s   n_grid %d   h = %.4f m\n"
            "body drawn as %d hull-surface points rigidly posed by the solved rigid-body transform; "
            "MPM solid is %d particles at h = %.4f m; water %d particles, %d layers"
            % (a.title or summ["label"], t, dmag[min(f + 1, len(dmag) - 1)] * 100,
               yawd[min(f + 1, len(yawd) - 1)], mass, depth, vel,
               int(z["n_grid"]), float(z["h"]), len(surf_v), len(pv_dumped),
               float(z["h"]), water.shape[1], summ["water_layers"]),
            fontsize=11,
        )
        fig.tight_layout(rect=(0, 0, 1, 0.90))
        pth = fdir / ("f_%04d.png" % f)
        fig.savefig(pth, facecolor="white")
        plt.close(fig)
        written.append(pth)
        if f % 10 == 0:
            print("frame", f, "of", nframes, flush=True)

    print("WROTE %d frames to %s" % (len(written), fdir))
    if a.hero_only:
        print("HERO", written[0])
    (outdir / "render_meta.json").write_text(json.dumps(
        {"vmin": vmin, "vmax": vmax, "elev": ELEV, "azim": AZIM,
         "frames": len(written), "pose_check_max_err_m": err,
         "mesh_faces_drawn": int(len(mf)), "source_run": str(run)}, indent=2))


if __name__ == "__main__":
    main()
