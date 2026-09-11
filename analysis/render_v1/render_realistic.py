"""T1 + T2 composite: shaded Yaris mesh inside a calibrated water isosurface.

Water surfacing is Kumar's examples/common.py surface_from_cloud with ONE change,
declared loudly: the hardcoded 0.012 m pad is replaced by pad_cells*cell. On the
0.4 m dough domain 0.012 m is 3.6 cells; on this 9.42 m flood domain at
cell = h/2 = 0.036804 it is 0.326 cells, less than the sigma=1.3 blur, so the
density field never reaches zero inside the array and marching cubes returns an
OPEN surface (euler 551, volume 2.63 m3 against a true 19.29 m3). Padding changes
no physics: the histogram is zero in the pad region by construction.

Isolevel calibrated on frame 45 against n_water*h**3 = 19.2891 m3:
  0.10 -> +14.42%   0.14 -> +5.52%   0.18 -> -2.45%   0.22 -> -10.21%   0.26 -> -18.81%
level 0.18 chosen, -2.45%.
"""
from __future__ import annotations

import numpy as np
import trimesh
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes

import t1_car as T

WATER = np.array([0.24, 0.48, 0.70])
SIGMA = 1.3
ISO_FRAC = 0.90   # calibrated on frame 45: +2.42%, euler 2 (single closed body)


def water_surface(x, cell, sigma=SIGMA, iso_frac=ISO_FRAC):
    """Kumar examples/recovery/nclaw_geom_render.py::_surface, verbatim algorithm,
    pinned at SHA 544c93dd02cb9c7ead89e1155a62967243244fce. 4-cell pad, adaptive
    isolevel relative to mean nonzero density, spacing handled inside marching_cubes.

    Replaces examples/common.py surface_from_cloud, whose hardcoded 0.012 m pad is
    0.326 cells on this 9.42 m domain and returns an OPEN surface (euler 551).
    """
    lo = x.min(0) - 4 * cell
    hi = x.max(0) + 4 * cell
    dims = np.ceil((hi - lo) / cell).astype(int) + 1
    idx = np.clip(np.floor((x - lo) / cell).astype(int), 0, dims - 1)
    fld = np.zeros(dims)
    np.add.at(fld, (idx[:, 0], idx[:, 1], idx[:, 2]), 1.0)
    fld = gaussian_filter(fld, sigma)
    verts, faces, *_ = marching_cubes(fld, level=iso_frac * fld[fld > 0].mean(),
                                      spacing=(cell, cell, cell))
    vw = verts + lo
    fn = np.cross(vw[faces[:, 1]] - vw[faces[:, 0]], vw[faces[:, 2]] - vw[faces[:, 0]])
    fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9
    return vw, faces, fn


def shade(fn, base):
    """dough_surface_render.py:79 Lambertian."""
    sh = np.clip(fn @ T.LIGHT, 0, 1) * 0.6 + 0.4
    return np.clip(sh[:, None] * base, 0, 1)


def crop_faces(vw, faces, fn, lo, hi):
    """Keep faces whose centroid falls in the view box, to keep matplotlib tractable."""
    c = vw[faces].mean(1)
    k = np.all((c >= lo) & (c <= hi), axis=1)
    return faces[k], fn[k]


def render(run="g64_m1100", frame=45, out=None, half=3.0, dpi=140,
           face_budget=50_000, elev=17, azim=-62):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    d = np.load(f"{run}/rollout.npz")
    h = float(d["h"])
    cell = h / 2.0
    R = d["R"].astype(np.float64)
    t = d["t"].astype(np.float64)

    Vv, F, ext = T.mesh_in_vehframe(face_budget)
    base, cnt = T.segment(Vv, F, ext)
    off = T.run_offset(d)
    Vcar, tri_car, fc_car = T.car_frame(Vv, F, base, off, R, t, frame)

    w = d["water"][frame].astype(np.float64)
    vw, wf, wn = water_surface(w, cell)
    mesh_w = trimesh.Trimesh(vertices=vw, faces=wf, process=False)
    vol = abs(mesh_w.volume)
    v_true = d["water"].shape[1] * h ** 3

    c = Vcar.mean(0)
    lo = np.array([c[0] - half, c[1] - half, -1e9])
    hi = np.array([c[0] + half, c[1] + half, 1e9])
    wf_c, wn_c = crop_faces(vw, wf, wn, lo, hi)
    fc_w = shade(wn_c, np.repeat(WATER[None, :], len(wf_c), axis=0))

    fig = plt.figure(figsize=(10, 6.5), facecolor="white")
    ax = fig.add_subplot(111, projection="3d")

    # Ground plane at the floor, so the closed underside of the water isosurface
    # is not visible from below.
    fl = float(d["floor"])
    gx, gy = c[0], c[1]
    # Subdivided: matplotlib depth-sorts by ONE average z per polygon, so a couple of
    # giant ground triangles sort wrongly against thousands of small water triangles.
    ng = 24
    ge = np.linspace(-half, half, ng + 1)
    gt = []
    for i in range(ng):
        for j in range(ng):
            a = [gx + ge[i], gy + ge[j], fl]; b = [gx + ge[i + 1], gy + ge[j], fl]
            cc = [gx + ge[i + 1], gy + ge[j + 1], fl]; e = [gx + ge[i], gy + ge[j + 1], fl]
            gt.append([a, b, cc]); gt.append([a, cc, e])
    ground = np.array(gt)

    # ONE collection so matplotlib's per-polygon depth sort orders car and water
    # against each other. Separate collections are sorted as wholes, which paints
    # the water sheet over the entire car and fakes the waterline.
    car_rgba = np.concatenate([fc_car, np.ones((len(fc_car), 1))], axis=1)
    wat_rgba = np.concatenate([fc_w, np.full((len(fc_w), 1), 0.55)], axis=1)
    gnd_rgba = np.repeat(np.array([[0.82, 0.80, 0.76, 1.0]]), len(ground), axis=0)
    tris = np.concatenate([ground, tri_car, vw[wf_c]], axis=0)
    rgba = np.concatenate([gnd_rgba, car_rgba, wat_rgba], axis=0)
    pc = Poly3DCollection(tris, facecolors=rgba, edgecolors="none")
    ax.add_collection3d(pc)

    # T2d: particles on top at low alpha, Kumar's convention keeps them the data carrier
    k = np.all((w[:, :2] >= lo[:2]) & (w[:, :2] <= hi[:2]), axis=1)
    ws = w[k][::4]
    ax.scatter(ws[:, 0], ws[:, 1], ws[:, 2], s=1.2, c="#1b4f72", alpha=0.16,
               linewidths=0, depthshade=False)

    ax.set_xlim(c[0] - half, c[0] + half)
    ax.set_ylim(c[1] - half, c[1] + half)
    ax.set_zlim(float(d["floor"]) - 0.05, float(d["floor"]) + 2.0)
    ax.set_box_aspect((1, 1, 0.42))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(f"{run}  frame {frame}   nclaw _surface iso_frac {ISO_FRAC}  "
                 f"V={vol:.2f} m3 vs {v_true:.2f} ({100*(vol-v_true)/v_true:+.1f}%)",
                 fontsize=10)
    out = out or f"realistic_{run}_f{frame:04d}.png"
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return {"out": out, "vol": vol, "v_true": v_true, "seg": cnt,
            "water_faces_total": len(wf), "water_faces_drawn": len(wf_c),
            "watertight": bool(mesh_w.is_watertight)}


if __name__ == "__main__":
    import sys
    run = sys.argv[1] if len(sys.argv) > 1 else "g64_m1100"
    frame = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    print(render(run, frame))
