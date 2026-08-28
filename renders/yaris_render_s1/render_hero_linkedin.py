"""Hero + wide establishing render for one gated warpmpm run.

Solver provenance: the 17 gated runs in data/all_runs_inventory.csv were produced by
renders/yaris_render_s1/sim_standing.py, which imports warpmpm (kks32/mpm-engine) at
sim_standing.py:10-12. This is NOT a Genesis render path and must not be labelled as one.

Everything drawn here comes from the run's own rollout.npz / summary.json / metrics.csv.
Nothing is synthesised. The L0/L1a/L1b/L2 verdicts are computed at render time by calling
gates_all_runs.evaluate() on this run's files, so no verdict string is hardcoded.

Water surface construction (marching cubes -> Taubin smoothing -> viridis by particle speed)
is imported directly from render_pv.py so this script cannot drift from the already-validated
surface pipeline.

Visualization conventions follow the Kumar / GeoElements checklist in
.claude/skills/mpm-technical-deep-reference/references/01_render_pipeline_and_visualization.md
lines 436-536: particles stay visible under the surface, viridis for the scalar field with
limits fixed across runs, blue water / gray boundary / orange vehicle annotation, a two-view
convention, a scale bar, and physical time labelled on every frame.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_pv as RPV  # noqa: E402  (sets pv.OFF_SCREEN, owns the surface pipeline)
import t1_car as T  # noqa: E402
import gates_all_runs as GA  # noqa: E402

pv.OFF_SCREEN = True

ORANGE = "#e8761a"
GHOST = "#9aa0a6"


def chip(pl, xyz, text, color, size):
    """World-anchored label on a white chip, so annotations stay legible over water,
    road and background alike."""
    pl.add_point_labels(np.asarray([xyz]), [text], font_size=size, text_color=color,
                        bold=True, shape="rounded_rect", shape_color="white",
                        shape_opacity=0.82, margin=4, show_points=False,
                        always_visible=True)


# --------------------------------------------------------------------------- data


def load_run(run_dir: Path):
    d = np.load(run_dir / "rollout.npz")
    summ = json.loads((run_dir / "summary.json").read_text())
    with open(run_dir / "metrics.csv") as fh:
        cols = fh.readline().strip().split(",")
    metr = np.loadtxt(run_dir / "metrics.csv", delimiter=",", skiprows=1)
    return d, summ, cols, metr


def live_verdicts(run_dir: Path):
    """Recompute the gate verdicts from this run's own files at render time."""
    return GA.evaluate(run_dir, run_dir.name, None, "sim_standing.py", "live")


def global_vmax(default: float) -> float:
    p = HERE / "global_color_limits.json"
    if p.is_file():
        return float(json.loads(p.read_text())["global_vmax"])
    return default


# --------------------------------------------------------------------------- scene


def camera_for(view: str, path_xy, floor, dom_lo, dom_hi):
    """Return (focal, parallel_scale, az_deg, elev_deg) for a named view.

    hero: 3/4 oblique framed on the vehicle's own travel path.
    wide: pulled back to the full simulated tank so the boundary conditions are visible.
    """
    if view == "hero":
        cx = float(0.5 * (path_xy[:, 0].min() + path_xy[:, 0].max()))
        cy = float(path_xy[:, 1].mean())
        focal = np.array([cx, cy, floor + 0.58])
        return focal, 2.40, -118.0, 20.0
    if view == "wide":
        cx = float(0.5 * (dom_lo[0] + dom_hi[0]))
        cy = float(0.5 * (dom_lo[1] + dom_hi[1]))
        focal = np.array([cx, cy, floor + 0.55])
        return focal, 5.30, -118.0, 30.0
    raise SystemExit("unknown view %r" % view)


def place_camera(pl, focal, pscale, az, elev):
    a, e = np.deg2rad(az), np.deg2rad(elev)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    pl.enable_parallel_projection()
    pl.camera.focal_point = tuple(focal)
    pl.camera.position = tuple(focal + 40.0 * pscale * d)
    pl.camera.up = (0, 0, 1)
    pl.camera.parallel_scale = pscale


def add_stage(pl, focal, pscale, floor, road_width, ssao_frac):
    """Ground plane, road strip and lane dashes.

    The road is decorative scene dressing, not simulated geometry: sim_standing.py:132-137
    registers a single floor plane at friction 0.55 plus four slip walls, with no road.
    The ground plane is deliberately huge so its own edge never appears in frame, which is
    what produced the gray corner artifact in the earlier renders.
    """
    span = 200.0 * pscale
    gp = pv.Plane(center=(focal[0], focal[1], floor), direction=(0, 0, 1),
                  i_size=span, j_size=span)
    pl.add_mesh(gp, color="#b9b4aa", ambient=0.55, diffuse=0.55, specular=0.0)

    reach = 4.0 * pscale
    strip = pv.Plane(center=(focal[0], focal[1], floor + 0.002), direction=(0, 0, 1),
                     i_size=road_width, j_size=2.0 * reach)
    pl.add_mesh(strip, color="#6f6c69", ambient=0.45, diffuse=0.6, specular=0.02)
    for y in np.arange(focal[1] - reach, focal[1] + reach, 1.6):
        pl.add_mesh(pv.Plane(center=(focal[0], y, floor + 0.004), direction=(0, 0, 1),
                             i_size=0.14, j_size=0.9),
                    color="#e8e4d8", ambient=0.6, diffuse=0.5, specular=0.0)

    pl.enable_ssao(radius=ssao_frac * pscale, bias=0.001)
    pl.enable_anti_aliasing("ssaa")
    pl.set_background("white")


def add_scale_bar(pl, focal, pscale, water_top, length_m=2.0):
    """Physical scale bar. Parallel projection is on, so its on-screen length is a
    faithful ruler anywhere in the frame."""
    x0 = focal[0] - 0.30 * pscale
    y0 = focal[1] - 1.16 * pscale
    z = water_top + 0.10
    bar = pv.Line((x0, y0, z), (x0 + length_m, y0, z))
    pl.add_mesh(bar.tube(radius=0.030), color="#141414", ambient=0.8, diffuse=0.2)
    for xt in (x0, x0 + length_m):
        cap = pv.Line((xt, y0 - 0.12, z), (xt, y0 + 0.12, z))
        pl.add_mesh(cap.tube(radius=0.026), color="#141414", ambient=0.8, diffuse=0.2)
    chip(pl, [x0 + 0.5 * length_m, y0 - 0.34, z + 0.06], "%.0f m" % length_m,
         "#141414", 17)


def add_flow_arrow(pl, focal, pscale, water_top, speed):
    """Flow is +x: sim_standing.py:196 clamps vw[band, 0] = velocity on the upstream
    low-x slab, and the one-shot kick at :161 adds to component 0."""
    start = (focal[0] - 0.95 * pscale, focal[1] + 0.62 * pscale, water_top + 1.15)
    arrow = pv.Arrow(start=start, direction=(1, 0, 0), scale=0.40 * pscale,
                     tip_length=0.28, tip_radius=0.085, shaft_radius=0.030)
    pl.add_mesh(arrow, color="#1f6fb2", ambient=0.5, diffuse=0.6)
    chip(pl, [start[0] + 0.20 * pscale, start[1] + 0.26, start[2] + 0.30],
         "flow %.1f m/s" % speed, "#1f6fb2", 18)


def add_vehicle(pl, V, F, masks, ghost=False):
    if ghost:
        pl.add_mesh(RPV.to_poly(V, F), color=GHOST, opacity=0.22,
                    smooth_shading=True, ambient=0.5, diffuse=0.4, specular=0.0)
        return
    for m, col, spec in masks:
        if not m.any():
            continue
        pl.add_mesh(RPV.to_poly(V, F[m]), color=col, smooth_shading=True,
                    ambient=0.28, diffuse=0.82, specular=spec, specular_power=18)


def add_drift_gauge(pl, t_hist, z_gauge, thin):
    """Engineering annotation for the run's displacement.

    A gray post over the vehicle's t=0 centre of mass, an orange post over its current
    centre of mass, and a bar between them labelled with the travelled distance. Positions
    come from rollout.npz["t"], the only per-frame rigid-body position record in the run.
    """
    x0, y0 = float(t_hist[0][0]), float(t_hist[0][1])
    x1, y1 = float(t_hist[-1][0]), float(t_hist[-1][1])
    drop = 0.55

    for x, y, col in ((x0, y0, GHOST), (x1, y1, ORANGE)):
        post = pv.Line((x, y, z_gauge - drop), (x, y, z_gauge))
        pl.add_mesh(post.tube(radius=thin), color=col, ambient=0.65, diffuse=0.4)

    if abs(x1 - x0) > 1e-4:
        bar = pv.Line((x0, y0, z_gauge), (x1, y1, z_gauge))
        pl.add_mesh(bar.tube(radius=1.25 * thin), color=ORANGE,
                    ambient=0.65, diffuse=0.4)
        pl.add_mesh(pv.Sphere(radius=2.6 * thin, center=(x1, y1, z_gauge)),
                    color=ORANGE, ambient=0.65, diffuse=0.4)

    d = float(np.hypot(x1 - x0, y1 - y0))
    chip(pl, [0.5 * (x0 + x1), 0.5 * (y0 + y1), z_gauge + 0.34],
         "drift %.1f cm" % (d * 100.0), ORANGE, 22)


def add_track(pl, t_hist, z_track, thin):
    """Orange centre-of-mass polyline from t=0 to the current frame."""
    if len(t_hist) < 2:
        return
    pts = np.column_stack([t_hist[:, 0], t_hist[:, 1],
                           np.full(len(t_hist), z_track)])
    line = pv.lines_from_points(pts)
    pl.add_mesh(line.tube(radius=thin), color=ORANGE, ambient=0.65, diffuse=0.4)


# --------------------------------------------------------------------------- text


def header_text(r, d, depth_real, dv):
    return (
        "CAN IT FORD\n"
        "L2 coupled MPM (warpmpm, kks32/mpm-engine)\n"
        "Toyota Yaris hull, %.0f kg (%s), grid %d^3\n"
        "depth %.4f m,  surge %.1f m/s,  DxV %.4f m2/s"
        % (float(d["mass"]), r["arr_limit_set"], int(d["n_grid"]),
           depth_real, float(d["velocity"]), dv)
    )


def clock_text(tt, dmag_cm, yaw):
    return ("t = %5.2f s\ndrift = %6.2f cm\nyaw = %+5.2f deg" % (tt, dmag_cm, yaw))


def verdict_text(r):
    onset = r["L2_onset_frame"]
    onset_s = ("crossed at frame %d" % onset) if onset is not None else "never crossed"
    return (
        "L0 %s      L1a %s      L1b %s      L2 %s      (%d of 4 rungs NO-FORD)\n"
        "L2 rule: rigid-body drift above %.2f m, %s."
        % (r["L0_verdict"], r["L1a_verdict"], r["L1b_verdict"], r["L2_verdict"],
           r["rungs_no_ford"], GA.DRIFT_THRESHOLD_M, onset_s)
    )


def caveat_text(r, disp_npz):
    """Two known defects of this run, stated rather than hidden.

    P-2 is the containment gate at gates.py:146-148. The two disagreeing displacement
    measures are the gap recorded at gates_both_scenarios.py:71-72; every number drawn in
    the scene comes from rollout.npz, so that is the one shown live.
    """
    frac = r["passthrough_max_frac"]
    ref = r["L2_final_disp_mag_m"]
    return ("caveats: containment gate P-2 %s, peak water fraction inside the vehicle bounding box %.4f against a 0.10 limit.\n"
            "final drift %.3f m from rollout.npz (the value drawn above) against %.3f m from summary.json, %+.1f%%. "
            "road surface is scene dressing, not simulated geometry."
            % ("FAIL" if frac >= 0.10 else "PASS", frac, disp_npz, ref,
               100.0 * (ref - disp_npz) / disp_npz))


# --------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(HERE / "g64_m1100"))
    ap.add_argument("--view", choices=("hero", "wide"), default="hero")
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--still", type=int, default=-1, help="render one frame to PNG")
    ap.add_argument("--iso-frac", type=float, default=0.90)
    ap.add_argument("--taubin", type=int, default=18)
    ap.add_argument("--pass-band", type=float, default=0.05)
    ap.add_argument("--opacity", type=float, default=0.50)
    ap.add_argument("--ssao-frac", type=float, default=0.033)
    ap.add_argument("--az", type=float, default=None)
    ap.add_argument("--elev", type=float, default=None)
    ap.add_argument("--pscale", type=float, default=None)
    ap.add_argument("--hold", type=int, default=0,
                    help="extra copies of the final frame appended to the movie")
    ap.add_argument("--no-caveat", action="store_true")
    ap.add_argument("--point-stride", type=int, default=6)
    a = ap.parse_args()

    run_dir = Path(a.run).resolve()
    d, summ, cols, metr = load_run(run_dir)
    r = live_verdicts(run_dir)

    floor = float(d["floor"])
    h_flood = float(d["h"])
    cell = h_flood / 2.0
    layers = int(summ["water_layers"])
    depth_real = layers * h_flood
    dv = depth_real * float(d["velocity"])
    vmax = global_vmax(float(np.percentile(d["speed"], 99)))

    R = d["R"].astype(np.float64)
    t = d["t"].astype(np.float64)
    W, S = d["water"], d["speed"]
    nf = W.shape[0]
    yawd = metr[:, cols.index("yaw_deg")]
    # Drawn geometry and the live drift readout share one source: the rollout.npz rigid
    # translations. metrics.csv / summary.json carry a separate measure of the same
    # quantity that disagrees by a few percent, surfaced in the caveat line instead.
    dmag_npz = np.linalg.norm(t - t[0], axis=1)

    Vv, F, ext = T.mesh_in_vehframe(None)
    base, cnt = T.segment(Vv, F, ext)
    off = T.run_offset(d)
    masks = [(np.all(np.isclose(base, T.TIRE), axis=1), "#1f1f24", 0.10),
             (np.all(np.isclose(base, T.GLASS), axis=1), "#7d95a3", 0.55),
             (np.all(np.isclose(base, T.BODY), axis=1), "#8f1f1f", 0.42)]

    dom_lo = W.reshape(-1, 3).min(0)
    dom_hi = W.reshape(-1, 3).max(0)
    focal, pscale, az, elev = camera_for(a.view, t[:, :2], floor, dom_lo, dom_hi)
    if a.pscale is not None:
        pscale = a.pscale
    if a.az is not None:
        az = a.az
    if a.elev is not None:
        elev = a.elev
    water_top = floor + depth_real

    print("RUN        %s" % run_dir)
    print("VIEW       %s focal=%s parallel_scale=%.3f az=%.1f elev=%.1f"
          % (a.view, np.round(focal, 3), pscale, az, elev))
    print("SEGMENT    %s" % cnt)
    print("SCALARS    viridis, clim=[0, %.9f] (global_color_limits.json)" % vmax)
    print("VERDICTS   L0=%s L1a=%s L1b=%s L2=%s (%d/4)"
          % (r["L0_verdict"], r["L1a_verdict"], r["L1b_verdict"], r["L2_verdict"],
             r["rungs_no_ford"]))

    frames = [a.still] if a.still >= 0 else list(range(0, nf, a.stride))

    # Two renderers: the 3D scene on top, a flat caption band underneath so the verdict
    # line never has to compete with the water for contrast.
    pl = pv.Plotter(off_screen=True, window_size=(a.width, a.height),
                    lighting="light kit", border=False,
                    shape=(2, 1), row_weights=[0.855, 0.145])
    if a.still < 0:
        # macro_block_size=1 keeps the encoded frame at exactly the requested size.
        # The imageio default of 16 silently rescales 1920x1080 to 1920x1088, which
        # changes the aspect ratio away from 16:9.
        pl.open_movie(a.out, framerate=a.fps, quality=9, macro_block_size=1)

    # frame-0 ghost pose, reused every frame as the displacement reference
    V0 = (Vv + off) @ R[0].T + t[0]
    veh_top = float(((Vv + off) @ R[0].T + t[0])[:, 2].max())
    z_gauge = veh_top + 0.62
    thin = 0.030 * (pscale / 3.05)

    def draw(fi):
        pl.clear()
        pl.subplot(0, 0)
        place_camera(pl, focal, pscale, az, elev)
        add_stage(pl, focal, pscale, floor, 6.4, a.ssao_frac)

        add_vehicle(pl, V0, F, masks, ghost=True)

        # Whole water body every frame, never a windowed subset: a clipped box leaves a
        # hard square wall in the marching-cubes surface that reads as a physical edge.
        w = W[fi].astype(np.float64)
        wc, sc = w, S[fi].astype(np.float64)
        pd, _, _ = RPV.water_poly(wc, sc, cell, RPV.SIGMA, a.iso_frac,
                                  a.taubin, a.pass_band)
        pl.add_mesh(pd, scalars="speed", cmap="viridis", clim=[0.0, vmax],
                    opacity=a.opacity, smooth_shading=True,
                    ambient=0.20, diffuse=0.70, specular=0.55, specular_power=24,
                    show_scalar_bar=True,
                    scalar_bar_args=dict(title="water speed (m/s)", n_labels=5,
                                         vertical=True, position_x=0.905,
                                         position_y=0.16, height=0.60, width=0.032,
                                         title_font_size=18, label_font_size=16,
                                         bold=True, color="#0d0d0d",
                                         fmt="%.2f"))
        # Kumar convention: the material points stay visible, the surface is readability
        # only and must not be the sole data carrier.
        pl.add_points(wc[:: a.point_stride], color="#12354f", opacity=0.20,
                      point_size=3.0, render_points_as_spheres=True)

        V = (Vv + off) @ R[fi].T + t[fi]
        add_vehicle(pl, V, F, masks)

        add_track(pl, t[: fi + 1], z_gauge, 0.6 * thin)
        add_drift_gauge(pl, t[: fi + 1], z_gauge, thin)
        add_scale_bar(pl, focal, pscale, water_top)
        add_flow_arrow(pl, focal, pscale, water_top, float(d["velocity"]))

        j = min(fi + 1, len(yawd) - 1)
        pl.add_text(header_text(r, d, depth_real, dv), position=(0.012, 0.825),
                    font_size=14, color="#111111", viewport=True)
        pl.add_text(clock_text(fi / float(d["fps"]), dmag_npz[fi] * 100.0, yawd[j]),
                    position=(0.012, 0.655), font_size=16, color="#1b1b1b",
                    viewport=True)

        pl.subplot(1, 0)
        pl.set_background("#f4f3f0")
        pl.add_text(verdict_text(r), position=(0.012, 0.50), font_size=15,
                    color="#8f1f1f", viewport=True)
        if not a.no_caveat:
            pl.add_text(caveat_text(r, float(dmag_npz[-1])), position=(0.012, 0.10),
                        font_size=10, color="#5a5a5a", viewport=True)

    if a.still >= 0:
        draw(a.still)
        pl.screenshot(a.out)
        pl.close()
        print("STILL", a.out)
        return 0

    for n, fi in enumerate(frames):
        draw(fi)
        pl.write_frame()
        if n % 10 == 0:
            print("frame %d/%d" % (n, len(frames)), flush=True)
    for _ in range(a.hold):
        pl.write_frame()
    pl.close()
    print("DONE", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
