from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pyvista as pv
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
from skimage import measure

import t1_car as T

pv.OFF_SCREEN = True
SIGMA = 1.3


def surface(pts, h, sigma, iso_frac):
    lo = pts.min(0) - 4 * h
    hi = pts.max(0) + 4 * h
    dims = np.ceil((hi - lo) / h).astype(int) + 1
    idx = np.clip(np.floor((pts - lo) / h).astype(int), 0, dims - 1)
    fld = np.zeros(dims)
    np.add.at(fld, (idx[:, 0], idx[:, 1], idx[:, 2]), 1.0)
    fld = gaussian_filter(fld, sigma)
    verts, faces, *_ = measure.marching_cubes(
        fld, level=iso_frac * fld[fld > 0].mean(), spacing=(h, h, h))
    return verts + lo, faces


def to_poly(v, f):
    return pv.PolyData(v, np.hstack([np.full((len(f), 1), 3), f]).astype(np.int64).ravel())


def water_poly(pts, scalar, h, sigma, iso_frac, n_iter, pass_band):
    v, f = surface(pts, h, sigma, iso_frac)
    pd = to_poly(v, f)
    _, nn = cKDTree(pts).query(v)
    pd["speed"] = scalar[nn]
    raw_vol = float(abs(pd.volume))
    raw_open = int(pd.n_open_edges)
    if n_iter > 0:
        pd = pd.smooth_taubin(n_iter=n_iter, pass_band=pass_band)
    return pd, raw_vol, raw_open


def build_view(cx, cy, half, zfloor, ztop):
    lo = np.array([cx - half, cy - half, zfloor])
    hi = np.array([cx + half, cy + half, ztop])
    ctr = 0.5 * (lo + hi)
    diag = float(np.linalg.norm(hi - lo))
    focal = np.array([ctr[0], ctr[1], lo[2] + 0.42 * (hi[2] - lo[2])])
    return focal, 0.52 * diag, float(lo[2])


def road(cx, cy, half, zfloor, width):
    strip = pv.Plane(center=(cx, cy, zfloor + 0.002), direction=(0, 0, 1),
                     i_size=width, j_size=2.4 * half)
    dashes = []
    n = 9
    ys = np.linspace(cy - half, cy + half, n)
    for y in ys:
        dashes.append(pv.Plane(center=(cx, y, zfloor + 0.004), direction=(0, 0, 1),
                               i_size=0.14, j_size=0.9))
    return strip, dashes


def setup(p, focal, view_radius, az, elev, zfloor, ssao_frac):
    gp = pv.Plane(center=(focal[0], focal[1], zfloor), direction=(0, 0, 1),
                  i_size=8 * view_radius, j_size=8 * view_radius)
    p.add_mesh(gp, color="#b9b4aa", ambient=0.55, diffuse=0.55, specular=0.0)
    p.enable_ssao(radius=ssao_frac * view_radius, bias=0.001)
    p.enable_anti_aliasing("ssaa")
    p.set_background("white")
    p.enable_parallel_projection()
    a = np.deg2rad(az)
    e = np.deg2rad(elev)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    p.camera.focal_point = tuple(focal)
    p.camera.position = tuple(focal + 4.0 * view_radius * d)
    p.camera.up = (0, 0, 1)
    p.camera.parallel_scale = view_radius


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="g64_m1100")
    ap.add_argument("--out", default="hero_g64_m1100.mp4")
    ap.add_argument("--fps", type=int, default=18)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--half", type=float, default=3.4)
    ap.add_argument("--iso-frac", type=float, default=0.90)
    ap.add_argument("--taubin", type=int, default=18)
    ap.add_argument("--pass-band", type=float, default=0.05)
    ap.add_argument("--ssao-frac", type=float, default=0.033)
    ap.add_argument("--az", type=float, default=-62.0)
    ap.add_argument("--elev", type=float, default=18.0)
    ap.add_argument("--opacity", type=float, default=0.62)
    ap.add_argument("--vmax", type=float, default=1.896362066268921)
    ap.add_argument("--faces", type=int, default=0)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--no-road", action="store_true")
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

    masks = [(np.all(np.isclose(base, T.TIRE), axis=1), "#1f1f24", 0.10),
             (np.all(np.isclose(base, T.GLASS), axis=1), "#7d95a3", 0.55),
             (np.all(np.isclose(base, T.BODY), axis=1), "#8f1f1f", 0.42)]

    cx0, cy0 = float(t[0][0]), float(t[0][1])
    focal, vr, zf = build_view(cx0, cy0, a.half, floor, floor + 2.0)
    print("VIEW focal=%s view_radius=%.4f ssao_radius=%.4f (kumar hardcode was 0.012)"
          % (np.round(focal, 3), vr, a.ssao_frac * vr))
    print("SEGMENT", cnt)
    print("SCENE realized_depth=%.6f m (%d layers x h) D*V=%.6f m2/s mass=%.0f kg"
          % (depth_real, layers, dv, float(d["mass"])))

    metr = np.loadtxt(run / "metrics.csv", delimiter=",", skiprows=1)
    with open(run / "metrics.csv") as fh:
        cols = fh.readline().strip().split(",")
    dmag = metr[:, cols.index("dmag")]
    yawd = metr[:, cols.index("yaw_deg")]

    frames = [a.hero_only] if a.hero_only >= 0 else list(range(0, nf, a.stride))

    pl = pv.Plotter(off_screen=True, window_size=(a.width, a.height),
                    lighting="light kit", border=False)
    if a.hero_only < 0:
        pl.open_movie(a.out, framerate=a.fps, quality=8)

    strip, dashes = road(cx0, cy0, a.half, floor, 7.2)
    stats = {}

    def draw(fi):
        pl.clear()
        setup(pl, focal, vr, a.az, a.elev, zf, a.ssao_frac)
        if not a.no_road:
            pl.add_mesh(strip, color="#6f6c69", ambient=0.45, diffuse=0.6, specular=0.02)
            for q in dashes:
                pl.add_mesh(q, color="#e8e4d8", ambient=0.6, diffuse=0.5, specular=0.0)

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
        pd, raw_vol, raw_open = water_poly(wc, sc, cell, SIGMA, a.iso_frac,
                                           a.taubin, a.pass_band)
        pl.add_mesh(pd, scalars="speed", cmap="viridis", clim=[0.0, a.vmax],
                    opacity=a.opacity, smooth_shading=True,
                    ambient=0.20, diffuse=0.70, specular=0.55, specular_power=24,
                    show_scalar_bar=True,
                    scalar_bar_args=dict(title="water speed (m/s)", n_labels=4,
                                         vertical=True, position_x=0.90,
                                         position_y=0.28, height=0.46, width=0.035,
                                         title_font_size=13, label_font_size=11,
                                         color="#222222"))
        sub = wc[::6]
        pl.add_points(sub, color="#12354f", opacity=0.20, point_size=3.0,
                      render_points_as_spheres=True)

        tt = fi / float(d["fps"])
        j = min(fi + 1, len(dmag) - 1)
        pl.add_text("Can It Ford  L2 coupled MPM   Yaris hull, %.0f kg\n"
                    "t = %5.2f s    |d| = %6.2f cm    yaw = %+5.2f deg\n"
                    "realized depth %.4f m (%d layers)   surge %.1f m/s   DxV %.4f m2/s   n_grid %d"
                    % (float(d["mass"]), tt, dmag[j] * 100.0, yawd[j],
                       depth_real, layers, float(d["velocity"]), dv, int(d["n_grid"])),
                    position="upper_left", font_size=11, color="#111111")
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
            draw(fi)
            pl.write_frame()
            if fi % 10 == 0:
                print("frame", fi, "of", nf, flush=True)
    pl.close()

    print("WATER VOLUME raw=%.4f m3  smoothed=%.4f m3  target=%.4f m3  "
          "raw_err=%+.2f%%  smooth_err=%+.2f%%  open_edges=%d  faces=%d"
          % (stats["vol_raw"], stats["vol_smooth"], stats["v_true"],
             100 * (stats["vol_raw"] - stats["v_true"]) / stats["v_true"],
             100 * (stats["vol_smooth"] - stats["v_true"]) / stats["v_true"],
             stats["open"], stats["faces"]))
    print("CAVEAT passthrough_max_frac=%.4f leaked_particle_frames=%d"
          % (summ["passthrough_max_frac"], summ["leaked_particle_frames"]))
    print("DONE", a.out)


if __name__ == "__main__":
    main()
