from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pyvista as pv
from scipy.ndimage import binary_dilation, gaussian_filter
from scipy.spatial import cKDTree
from skimage import measure

import t1_car as T

pv.OFF_SCREEN = True
SIGMA = 1.3


def surface(pts, h, sigma, iso_frac, occl=None, grow=1):
    lo = pts.min(0) - 4 * h
    hi = pts.max(0) + 4 * h
    dims = np.ceil((hi - lo) / h).astype(int) + 1
    idx = np.clip(np.floor((pts - lo) / h).astype(int), 0, dims - 1)
    fld = np.zeros(dims)
    np.add.at(fld, (idx[:, 0], idx[:, 1], idx[:, 2]), 1.0)
    fld = gaussian_filter(fld, sigma)
    if occl is not None and len(occl):
        oi = np.floor((occl - lo) / h).astype(int)
        keep = np.all((oi >= 0) & (oi < dims), axis=1)
        oi = oi[keep]
        if len(oi):
            m = np.zeros(dims, dtype=bool)
            m[oi[:, 0], oi[:, 1], oi[:, 2]] = True
            if grow > 0:
                m = binary_dilation(m, iterations=grow)
            fld[m] = 0.0
    lev = iso_frac * fld[fld > 0].mean()
    verts, faces, *_ = measure.marching_cubes(fld, level=lev, spacing=(h, h, h))
    return verts + lo, faces


def to_poly(v, f):
    return pv.PolyData(v, np.hstack([np.full((len(f), 1), 3), f]).astype(np.int64).ravel())


def water_poly(pts, scalar, h, sigma, iso_frac, n_iter, pass_band, occl=None, grow=1):
    v, f = surface(pts, h, sigma, iso_frac, occl=occl, grow=grow)
    pd = to_poly(v, f)
    _, nn = cKDTree(pts).query(v)
    pd["speed"] = scalar[nn]
    raw_vol = float(abs(pd.volume))
    raw_open = int(pd.n_open_edges)
    if n_iter > 0:
        pd = pd.smooth_taubin(n_iter=n_iter, pass_band=pass_band)
    return pd, raw_vol, raw_open


def cam_basis(az, elev):
    a = np.deg2rad(az)
    e = np.deg2rad(elev)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    right = np.cross(np.array([0.0, 0.0, 1.0]), d)
    right /= np.linalg.norm(right)
    up = np.cross(d, right)
    up /= np.linalg.norm(up)
    return d, right, up


def fit_camera(pts, az, elev, aspect, margin):
    d, right, up = cam_basis(az, elev)
    c = 0.5 * (pts.min(0) + pts.max(0))
    q = pts - c
    hx = float(np.abs(q @ right).max())
    hy = float(np.abs(q @ up).max())
    return c, d, max(hy, hx / aspect) * margin


def setup(p, focal, dvec, scale, zfloor, ssao_frac, ground_half, shadows):
    gp = pv.Plane(center=(focal[0], focal[1], zfloor), direction=(0, 0, 1),
                  i_size=ground_half, j_size=ground_half)
    p.add_mesh(gp, color="#b0aba1", ambient=0.50, diffuse=0.60, specular=0.0)
    p.enable_ssao(radius=ssao_frac * scale, bias=0.001)
    p.enable_anti_aliasing("ssaa")
    if shadows:
        try:
            p.enable_shadows()
        except Exception:
            pass
    p.set_background("white")
    p.enable_parallel_projection()
    p.camera.focal_point = tuple(focal)
    p.camera.position = tuple(focal + 40.0 * scale * dvec)
    p.camera.up = (0, 0, 1)
    p.camera.parallel_scale = scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="g64_m1100")
    ap.add_argument("--png-dir", default="")
    ap.add_argument("--out", default="hero.mp4")
    ap.add_argument("--fps", type=int, default=18)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--half", type=float, default=2.8)
    ap.add_argument("--iso-frac", type=float, default=0.90)
    ap.add_argument("--taubin", type=int, default=18)
    ap.add_argument("--pass-band", type=float, default=0.05)
    ap.add_argument("--ssao-frac", type=float, default=0.06)
    ap.add_argument("--az", type=float, default=-62.0)
    ap.add_argument("--elev", type=float, default=20.0)
    ap.add_argument("--margin", type=float, default=1.04)
    ap.add_argument("--opacity", type=float, default=0.62)
    ap.add_argument("--vmax", type=float, default=1.896362066268921)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--carve-grow", type=int, default=1)
    ap.add_argument("--no-carve", action="store_true")
    ap.add_argument("--no-road", action="store_true")
    ap.add_argument("--no-shadows", action="store_true")
    ap.add_argument("--hero-only", type=int, default=-1)
    a = ap.parse_args()

    run = Path(a.run)
    d = np.load(run / "rollout.npz")
    summ = json.loads((run / "summary.json").read_text())

    h_flood = float(d["h"])
    cell = h_flood / 2.0
    floor = float(d["floor"])
    R = d["R"].astype(np.float64)
    t = d["t"].astype(np.float64)
    W = d["water"]
    S = d["speed"]
    nf = W.shape[0]
    layers = int(summ["water_layers"])
    depth_real = layers * h_flood
    dv = depth_real * float(d["velocity"])

    Vv, F, ext = T.mesh_in_vehframe(None)
    base, cnt = T.segment(Vv, F, ext)
    off = T.run_offset(d)
    pv0 = d["veh_particles_vehframe"].astype(np.float64)

    masks = [(np.all(np.isclose(base, T.TIRE), axis=1), "#1a1a1f", 0.10),
             (np.all(np.isclose(base, T.GLASS), axis=1), "#7d95a3", 0.55),
             (np.all(np.isclose(base, T.BODY), axis=1), "#911d1d", 0.42)]

    cx0, cy0 = float(t[0][0]), float(t[0][1])
    aspect = a.width / a.height

    pts = [np.array([cx0 - a.half, cy0 - a.half, floor]),
           np.array([cx0 + a.half, cy0 + a.half, floor + depth_real])]
    for fi in range(nf):
        V = (Vv + off) @ R[fi].T + t[fi]
        pts.append(V.min(0))
        pts.append(V.max(0))
    focal, dvec, scale = fit_camera(np.asarray(pts), a.az, a.elev, aspect, a.margin)
    ground_half = 14.0 * scale

    print("CAMERA focal=%s parallel_scale=%.4f  visible %.2f m tall x %.2f m wide"
          % (np.round(focal, 3), scale, 2 * scale, 2 * scale * aspect))
    print("SSAO   radius=%.4f m (kumar hardcode 0.012, pyvista default 0.5)"
          % (a.ssao_frac * scale))
    print("SEGMENT", cnt)
    print("SCENE  realized_depth=%.6f m (%d layers) D*V=%.6f m2/s mass=%.0f kg"
          % (depth_real, layers, dv, float(d["mass"])))

    metr = np.loadtxt(run / "metrics.csv", delimiter=",", skiprows=1)
    with open(run / "metrics.csv") as fh:
        cols = fh.readline().strip().split(",")
    dmag = metr[:, cols.index("dmag")]
    yawd = metr[:, cols.index("yaw_deg")]

    frames = [a.hero_only] if a.hero_only >= 0 else list(range(0, nf, a.stride))

    pl = pv.Plotter(off_screen=True, window_size=(a.width, a.height),
                    lighting="light kit", border=False)
    fdir = Path(a.png_dir) if a.png_dir else None
    if fdir is not None:
        fdir.mkdir(parents=True, exist_ok=True)
    if a.hero_only < 0 and fdir is None:
        pl.open_movie(a.out, framerate=a.fps, quality=8)

    stats = {}

    def draw(fi):
        pl.clear()
        setup(pl, focal, dvec, scale, floor, a.ssao_frac, ground_half,
              not a.no_shadows)

        if not a.no_road:
            strip = pv.Plane(center=(cx0, cy0, floor + 0.003), direction=(0, 0, 1),
                             i_size=7.2, j_size=4.0 * a.half)
            pl.add_mesh(strip, color="#6b6864", ambient=0.42, diffuse=0.62,
                        specular=0.02)
            for y in np.arange(cy0 - 2.0 * a.half, cy0 + 2.0 * a.half, 1.6):
                pl.add_mesh(pv.Plane(center=(cx0, y, floor + 0.006),
                                     direction=(0, 0, 1), i_size=0.13, j_size=0.85),
                            color="#ddd8c8", ambient=0.6, diffuse=0.5, specular=0.0)

        V = (Vv + off) @ R[fi].T + t[fi]
        for m, col, spec in masks:
            if not m.any():
                continue
            pl.add_mesh(to_poly(V, F[m]), color=col, smooth_shading=True,
                        ambient=0.28, diffuse=0.82, specular=spec, specular_power=18)

        w = W[fi].astype(np.float64)
        k = ((w[:, 0] >= cx0 - a.half - 0.5) & (w[:, 0] <= cx0 + a.half + 0.5) &
             (w[:, 1] >= cy0 - a.half - 0.5) & (w[:, 1] <= cy0 + a.half + 0.5))
        wc = w[k]
        sc = S[fi][k].astype(np.float64)
        occl = None if a.no_carve else ((pv0 + off) @ R[fi].T + t[fi])
        pd, raw_vol, raw_open = water_poly(wc, sc, cell, SIGMA, a.iso_frac,
                                           a.taubin, a.pass_band,
                                           occl=occl, grow=a.carve_grow)
        pl.add_mesh(pd, scalars="speed", cmap="viridis", clim=[0.0, a.vmax],
                    opacity=a.opacity, smooth_shading=True,
                    ambient=0.20, diffuse=0.70, specular=0.55, specular_power=24,
                    show_scalar_bar=True,
                    scalar_bar_args=dict(title="water speed (m/s)", n_labels=4,
                                         vertical=True, position_x=0.905,
                                         position_y=0.26, height=0.48, width=0.030,
                                         title_font_size=15, label_font_size=13,
                                         color="#1a1a1a"))
        pl.add_points(wc[::6], color="#0d2b40", opacity=0.18, point_size=2.6,
                      render_points_as_spheres=True)

        tt = fi / float(d["fps"])
        j = min(fi + 1, len(dmag) - 1)
        pl.add_text("Can It Ford   L2 coupled MPM   Yaris hull  %.0f kg\n"
                    "t = %5.2f s     |d| = %6.2f cm     yaw = %+5.2f deg\n"
                    "depth %.4f m (%d layers)   surge %.1f m/s   DxV %.4f m2/s   n_grid %d"
                    % (float(d["mass"]), tt, dmag[j] * 100.0, yawd[j],
                       depth_real, layers, float(d["velocity"]), dv, int(d["n_grid"])),
                    position="upper_left", font_size=13, color="#101010")
        stats["v_true"] = len(wc) * h_flood ** 3
        stats["vol_raw"] = raw_vol
        stats["open"] = raw_open
        stats["vol_smooth"] = float(abs(pd.volume))
        stats["faces"] = int(pd.n_cells)

    draw(frames[0])
    if a.hero_only >= 0:
        pl.screenshot(a.out.replace(".mp4", ".png"))
        print("HERO", a.out.replace(".mp4", ".png"))
    else:
        for fi in frames:
            if fdir is not None and (fdir / ("f_%04d.png" % fi)).exists():
                continue
            s0 = time.time()
            draw(fi)
            if fdir is not None:
                pl.screenshot(str(fdir / ("f_%04d.png" % fi)))
            else:
                pl.write_frame()
            print("frame %d of %d  %.1fs" % (fi, nf, time.time() - s0), flush=True)
    pl.close()

    print("WATER  raw=%.4f m3  smoothed=%.4f m3  target=%.4f m3  raw_err=%+.2f%%  "
          "smooth_err=%+.2f%%  open_edges=%d  faces=%d"
          % (stats["vol_raw"], stats["vol_smooth"], stats["v_true"],
             100 * (stats["vol_raw"] - stats["v_true"]) / stats["v_true"],
             100 * (stats["vol_smooth"] - stats["v_true"]) / stats["v_true"],
             stats["open"], stats["faces"]))
    print("CAVEAT passthrough_max_frac=%.4f leaked_particle_frames=%d"
          % (summ["passthrough_max_frac"], summ["leaked_particle_frames"]))
    print("DONE")


if __name__ == "__main__":
    main()
