"""Offscreen render of an open-channel or canonical MPM rollout.

Reads either format:
  canonical  renders/.../rollout.npz  -- water (F,N,3), speed (F,N),
             veh_particles_scene0, R, t, lim, dx, floor
  channel    simulation/sim_channel.py --dump-water  -- water, speed, vehicle,
             frames_dumped, lim, dx, floor, x_in, x_out, grade_deg

The point of rendering here is NOT prettiness. It is to make the streamwise free
surface visible, because that is the quantity the closed-vs-open comparison turns
on, and a number in a table is easy to mistrust and hard to sanity-check. The
camera therefore looks along -y by default, so the surface profile is the silhouette.

Water is coloured by speed on a fixed scale passed in by the caller, so two runs
rendered for comparison are actually comparable; an autoscaled colour bar would
make a fast run and a slow run look identical.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def load(path):
    d = np.load(path)
    water = d["water"]
    speed = d["speed"] if "speed" in d else np.zeros(water.shape[:2], np.float32)
    veh = None
    if "vehicle" in d and d["vehicle"].size:
        veh = d["vehicle"]
    elif "veh_particles_scene0" in d:                     # canonical: static checkpoint
        veh = np.repeat(d["veh_particles_scene0"][None], len(water), axis=0)
    meta = {k: (float(d[k]) if d[k].ndim == 0 else d[k])
            for k in ("lim", "dx", "floor", "depth", "velocity", "grade_deg",
                      "x_in", "x_out") if k in d}
    return water, speed, veh, meta


def render(path, out_png, frame=-1, vmax=None, azimuth=None, elevation=None,
           window=(1400, 900), title=None):
    import pyvista as pv
    pv.OFF_SCREEN = True

    water, speed, veh, meta = load(path)
    f = frame if frame >= 0 else len(water) - 1
    w, sp = water[f], speed[f]
    lim = meta.get("lim", float(w.max()))
    floor = meta.get("floor", 0.0)
    if vmax is None:
        vmax = float(np.percentile(sp, 99)) or 1.0

    pl = pv.Plotter(off_screen=True, window_size=list(window))
    pl.set_background("white")

    cloud = pv.PolyData(w.astype(np.float64))
    cloud["speed"] = sp
    pl.add_mesh(cloud, scalars="speed", cmap="viridis", clim=[0.0, vmax],
                point_size=4.0, render_points_as_spheres=True,
                scalar_bar_args=dict(title="speed m/s", color="black", n_labels=4))

    if veh is not None and veh.shape[1]:
        pl.add_mesh(pv.PolyData(veh[min(f, len(veh) - 1)].astype(np.float64)),
                    color="#b03030", point_size=5.0, render_points_as_spheres=True)

    bed = pv.Plane(center=(lim / 2, lim / 2, floor), direction=(0, 0, 1),
                   i_size=lim, j_size=lim)
    pl.add_mesh(bed, color="#d9d2c5", opacity=0.55, show_edges=False)

    # Mark the two planes the BC acts on, so a reader can see where the water is
    # being taken out and put back rather than having to trust the caption.
    for key, col in (("x_in", "#1f77b4"), ("x_out", "#d62728")):
        if key in meta:
            xv = float(meta[key])
            pl.add_mesh(pv.Plane(center=(xv, lim / 2, floor + 0.12 * lim),
                                 direction=(1, 0, 0), i_size=0.24 * lim, j_size=lim),
                        color=col, opacity=0.30)

    pl.camera_position = "xz"                    # look along -y: surface as silhouette
    if azimuth:
        pl.camera.azimuth = azimuth
    if elevation:
        pl.camera.elevation = elevation
    pl.camera.zoom(1.35)
    if title:
        pl.add_text(title, position="upper_left", font_size=11, color="black")
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    pl.screenshot(str(out_png))
    pl.close()
    return dict(png=str(out_png), frame=f, n_water=int(w.shape[0]), vmax=float(vmax),
                surface_max_z=float(np.percentile(w[:, 2], 99.5)) - floor)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("npz")
    p.add_argument("out")
    p.add_argument("--frame", type=int, default=-1)
    p.add_argument("--vmax", type=float, default=None)
    p.add_argument("--azimuth", type=float, default=None)
    p.add_argument("--elevation", type=float, default=None)
    p.add_argument("--title", default=None)
    a = p.parse_args()
    print(render(a.npz, a.out, a.frame, a.vmax, a.azimuth, a.elevation, title=a.title))


if __name__ == "__main__":
    main()
