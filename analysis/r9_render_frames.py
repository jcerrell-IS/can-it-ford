#!/usr/bin/env python3
"""Render the dumped moving-vehicle frames to PNGs, with an on-frame caption.

WHY THE CAPTION IS ON THE FRAME AND NOT IN A README. A rendered fluid image is
the most persuasive artefact this project produces and the least self-describing:
nothing in a picture of water says which parts came out of the solver, which were
measured, and which were chosen to make it legible. A caption in a README travels
separately from the file and is not read. d13-renders' caption strip is the
pattern; this copies it.

THE THREE CATEGORIES ARE NAMED SEPARATELY ON EVERY FRAME:
  SOLVER      water particle positions and the hull pose, straight from the run
  MEASURED    the run's own recorded parameters, read from the npz not retyped
  DRAWN       colours, camera, and the vehicle rendered as its BOUNDING BOX,
              because the dump carries the hull centre and extents but not the
              mesh or its orientation. The box is a stand-in and saying so is the
              whole point of the strip.

AND THE RUN'S OWN WARNING TRAVELS WITH IT. These frames are a GROUND-FRAME run,
which failed this study's C4 frame check at 34 percent with an undeveloped stream
among its confounds. The sequence is a VISUALISATION. No force from it is a
measurement, and the frame says so.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def render(npz_path, outdir, stride=1, dpi=100, subsample=1, limit=None):
    z = np.load(npz_path)
    wx = z["water_xyz"]
    hc = z["hull_center"]
    fi = z["frame_index"]
    ext = np.asarray(z["hull_extent_m"], dtype=float)
    lim = float(z["lim_m"]); dx = float(z["dx_m"])
    depth = float(z["depth_m"]); floor = float(z["floor_z_m"])
    dt = float(z["frame_dt_s"]); fps = int(z["fps_nominal"])
    vcar = float(z["v_car_ms"]); vwat = float(z["v_water_ms"])
    n_part = wx.shape[1]

    # FIXED colour and axis limits across every frame. Autoscaling per frame is
    # the classic way to make a still fluid look like it is surging: the colour
    # of a given height would change frame to frame and the eye reads that as
    # motion that is not in the data.
    z_still = floor + depth
    # A flat colour range made the pool one uniform blue and the flow
    # unreadable. Anchor the scale to the STILL SURFACE so bulk water
    # sits mid-scale and both the trough and the spray have contrast.
    vmin, vmax = floor + 0.02, z_still + 0.30
    travel = float(hc[-1, 1] - hc[0, 1])

    os.makedirs(outdir, exist_ok=True)
    idx = list(range(0, len(fi) if limit is None else min(limit, len(fi)), stride))
    for k in idx:
        p = wx[k][::subsample]
        # DRAW HIGH PARTICLES LAST. Unsorted scatter paints in array order, so
        # whether a splash is visible depends on particle indexing rather than on
        # height, and the spray disappears behind bulk water at random.
        p = p[np.argsort(p[:, 2])]
        fig = plt.figure(figsize=(12.8, 9.6), dpi=dpi)
        fig.patch.set_facecolor("#0b0f14")

        # ---- plan view: x across the road (flow), y along the road (car)
        ax = fig.add_axes([0.06, 0.31, 0.60, 0.60])
        ax.set_facecolor("#070b10")
        ax.scatter(p[:, 0], p[:, 1], c=p[:, 2], s=0.5, cmap="turbo",
                   vmin=vmin, vmax=vmax, linewidths=0, rasterized=True)
        ax.add_patch(Rectangle((hc[k, 0] - ext[0] / 2, hc[k, 1] - ext[1] / 2),
                               ext[0], ext[1], fill=False, ec="#ffffff", lw=2.0))
        ax.arrow(1.0, 1.4, 2.4, 0.0, head_width=0.5, color="#ffffff", lw=1.5)
        ax.text(1.0, 2.3, "water %.1f m/s" % vwat, color="#ffffff", fontsize=9)
        ax.arrow(hc[k, 0] + 1.8, hc[k, 1] - 1.0, 0.0, 2.4, head_width=0.5,
                 color="#ffcc44", lw=1.5)
        ax.text(hc[k, 0] + 2.2, hc[k, 1], "car %.1f m/s" % vcar,
                color="#ffcc44", fontsize=9)
        ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.set_aspect("equal")
        ax.set_xlabel("x, across the road (m)", color="#9fb3c8", fontsize=9)
        ax.set_ylabel("y, along the road, the car drives this way (m)",
                      color="#9fb3c8", fontsize=9)
        ax.tick_params(colors="#9fb3c8", labelsize=8)
        for sp in ax.spines.values():
            sp.set_color("#26323f")
        ax.text(0.02, 0.975, "PLAN VIEW", transform=ax.transAxes,
                color="#e6edf3", fontsize=9, va="top", weight="bold")

        # ---- elevation: y along the road against z, so the splash is legible
        ax2 = fig.add_axes([0.71, 0.31, 0.26, 0.60])
        ax2.set_facecolor("#070b10")
        near = np.abs(p[:, 0] - hc[k, 0]) < 2.0
        ax2.scatter(p[near, 1], p[near, 2], c=p[near, 2], s=0.6, cmap="turbo",
                    vmin=vmin, vmax=vmax, linewidths=0, rasterized=True)
        # THE HULL ORIGIN IS ITS UNDERSIDE IN z, NOT ITS CENTRE.
        # canonicalize() shifts the mesh by [(lo+hi)/2, (lo+hi)/2, lo[2]], so x
        # and y ARE centred but z is shifted so the mesh minimum sits at 0. The
        # collider centre at z = floor therefore puts the WHEELS on the road.
        # Drawing this box from hc[2] - ext[2]/2, as an earlier version did, sank
        # the car 0.76 m into the roadway: the physics was right and the picture
        # was wrong, which is the more dangerous way round because the picture is
        # what people believe.
        ax2.add_patch(Rectangle((hc[k, 1] - ext[1] / 2, hc[k, 2]),
                                ext[1], ext[2], fill=False, ec="#ffffff", lw=1.8))
        ax2.axhline(z_still, color="#7a93ab", lw=0.9, ls="--")
        ax2.text(0.4, z_still + 0.02, "still surface", color="#7a93ab", fontsize=7)
        ax2.set_xlim(0, lim)
        ax2.set_ylim(floor - 0.08, max(vmax + 0.05, hc[k, 2] + ext[2] + 0.12))
        ax2.set_xlabel("y (m)", color="#9fb3c8", fontsize=9)
        ax2.set_ylabel("z (m)", color="#9fb3c8", fontsize=9)
        ax2.tick_params(colors="#9fb3c8", labelsize=8)
        for sp in ax2.spines.values():
            sp.set_color("#26323f")
        ax2.text(0.03, 0.975, "ELEVATION, within 2 m of the car",
                 transform=ax2.transAxes, color="#e6edf3", fontsize=8,
                 va="top", weight="bold")

        t = (fi[k] - fi[0]) * dt
        fig.text(0.06, 0.955, "Can It Ford: a vehicle crossing a flooded roadway",
                 color="#e6edf3", fontsize=15, weight="bold")
        fig.text(0.97, 0.955, "frame %3d / %d    t = %5.2f s" % (fi[k], fi[-1], t),
                 color="#9fb3c8", fontsize=10, family="monospace", ha="right")

        # ---- the caption strip. Lines are kept short ON PURPOSE: an earlier
        # version ran the warning off the right edge of the frame, so the words
        # "among its confounds" were cropped and the warning read as complete.
        fig.patches.append(plt.Rectangle((0.0, 0.0), 1.0, 0.265,
                                         transform=fig.transFigure,
                                         facecolor="#111820", edgecolor="#26323f",
                                         zorder=-1))
        fig.text(0.035, 0.222, "VISUALISATION, NOT A MEASUREMENT.",
                 color="#ff7b6b", fontsize=11, weight="bold")
        fig.text(0.335, 0.222,
                 "Ground frame: it FAILED this study's C4 frame check at 34 percent,",
                 color="#ff7b6b", fontsize=9.5)
        fig.text(0.035, 0.192,
                 "with an undeveloped stream among its confounds. No force from this "
                 "sequence may be quoted. The load surface is built from the "
                 "rest-frame runs.", color="#ff7b6b", fontsize=9.5)
        fig.text(0.035, 0.146, "SOLVER", color="#7ee787", fontsize=9.5, weight="bold")
        fig.text(0.115, 0.146,
                 "warpmpm MPM, NOT Genesis. Water particle positions and hull pose, "
                 "every frame. %s particles, n_grid 160, dx %.4f m."
                 % ("{:,}".format(n_part), dx), color="#c9d1d9", fontsize=9.5)
        fig.text(0.035, 0.110, "MEASURED", color="#79c0ff", fontsize=9.5, weight="bold")
        fig.text(0.115, 0.110,
                 "v_car %.1f m/s and v_water %.1f m/s on PERPENDICULAR axes. Depth "
                 "%.2f m, domain %.1f m, frame dt %.4f s, hull travel %.2f m."
                 % (vcar, vwat, depth, lim, dt, travel),
                 color="#c9d1d9", fontsize=9.5)
        fig.text(0.035, 0.074, "DRAWN", color="#d2a8ff", fontsize=9.5, weight="bold")
        fig.text(0.115, 0.074,
                 "Colour, camera, scale. The vehicle is its BOUNDING BOX "
                 "%.2f x %.2f x %.2f m, not the hull mesh: the dump carries the "
                 "centre and extents only." % (ext[0], ext[1], ext[2]),
                 color="#c9d1d9", fontsize=9.5)
        fig.text(0.035, 0.032,
                 "The body is PRESCRIBED, not free. It is driven at a commanded speed "
                 "and cannot be swept away, so nothing here is a FORD or NO-FORD "
                 "verdict.", color="#8b949e", fontsize=9)

        fig.savefig(os.path.join(outdir, "f%04d.png" % fi[k]),
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        if k % 25 == 0:
            print("  frame %d/%d" % (fi[k], fi[-1]), flush=True)
    return len(idx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz")
    ap.add_argument("outdir")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--subsample", type=int, default=1,
                    help="draw every Nth particle; 1 draws all of them")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dpi", type=int, default=100)
    a = ap.parse_args()
    n = render(a.npz, a.outdir, a.stride, a.dpi, a.subsample, a.limit)
    print("wrote %d frames to %s" % (n, a.outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
