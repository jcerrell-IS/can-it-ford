"""
render_moving_vehicle_placeholder.py

PLACEHOLDER VISUALIZATION, NOT A FINISHED RENDER. A minimal matplotlib scatter of
the water and hull particles from simulation/moving_vehicle_sdf_exploratory.py.

Dispatch A had not established a transform or render path for this scene as of
2026-08-11 (its simulation/yaris_sdf_smoke.py is a geometry check with no render),
so there was nothing to reuse exactly. The existing renderers under
renders/yaris_render_s1/ read the canonical free-rigid rollout schema, which is
not the schema this scene writes. This is a diagnostic plot to answer one
question, whether the water piles up ahead of the hull and disturbs behind it.
It is not lit, not surfaced, and not poster or paper artwork.

Panels
  top     plan view, water coloured by free-surface anomaly z - (floor + depth).
          A bow wave reads as a positive band ahead of the hull.
  bottom  centreline elevation profile, max water z in y bins within a lateral
          window, against the undisturbed level.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def render(rundir: Path, outdir: Path, half_width: float = 1.5, nbins: int = 90,
           fps: int = 30, dpi: int = 110):
    meta = json.loads((rundir / "meta.json").read_text())
    d = np.load(rundir / "rollout.npz", allow_pickle=True)
    water = d["water"]
    centers = d["centers"]
    hull = d["hull_surface"]
    floor = float(d["floor"])
    depth = float(d["depth"])
    lim = float(d["lim"])
    still = floor + depth

    outdir.mkdir(parents=True, exist_ok=True)
    # fixed colour range across frames so motion is not confused with rescaling
    span = float(np.nanpercentile(np.abs(np.concatenate([w[:, 2] for w in water]) - still), 99.5))
    span = max(span, 1e-3)

    for i in range(len(water)):
        w = np.asarray(water[i])
        c = np.asarray(centers[i])
        hw = hull + c[None, :]
        eta = w[:, 2] - still

        fig, (ax0, ax1) = plt.subplots(
            2, 1, figsize=(11.0, 8.2), height_ratios=[2.0, 1.0],
            gridspec_kw={"hspace": 0.28})

        sc = ax0.scatter(w[:, 1], w[:, 0], c=eta, s=3.0, cmap="RdBu_r",
                         vmin=-span, vmax=span, linewidths=0)
        ax0.scatter(hw[:, 1], hw[:, 0], s=1.2, c="0.15", linewidths=0, alpha=0.55)
        ax0.axvline(c[1], color="0.35", lw=0.7, ls=":")
        ax0.set_xlim(0, lim); ax0.set_ylim(0, lim); ax0.set_aspect("equal")
        ax0.set_xlabel("y, drive direction (m)"); ax0.set_ylabel("x (m)")
        ax0.set_title("plan view, free-surface anomaly. frame %d/%d, t=%.3f s, "
                      "hull y=%.3f m, v=%.2f m/s"
                      % (i + 1, len(water), (i + 1) / float(fps),
                         c[1], meta["velocity_ms"]), fontsize=9)
        cb = fig.colorbar(sc, ax=ax0, fraction=0.030, pad=0.015)
        cb.set_label("z - (floor + depth), m", fontsize=8)
        cb.ax.tick_params(labelsize=7)

        lat = np.abs(w[:, 0] - lim * 0.5) < half_width
        edges = np.linspace(0, lim, nbins + 1)
        idx = np.clip(np.digitize(w[lat, 1], edges) - 1, 0, nbins - 1)
        prof = np.full(nbins, np.nan)
        for b in range(nbins):
            m = idx == b
            if m.any():
                prof[b] = w[lat][m][:, 2].max()
        mid = 0.5 * (edges[1:] + edges[:-1])
        ax1.axhline(still, color="0.55", lw=0.9, ls="--", label="undisturbed level")
        ax1.plot(mid, prof, color="#1f5fa8", lw=1.4, label="max water z, centreline")
        hl = np.abs(hw[:, 0] - lim * 0.5) < half_width
        ax1.scatter(hw[hl, 1], hw[hl, 2], s=1.0, c="0.55", linewidths=0,
                    label="hull surface, centreline slab")
        ax1.set_xlim(0, lim)
        ax1.set_ylim(floor - 0.02, still + max(4 * span, 0.25))
        ax1.set_xlabel("y (m)"); ax1.set_ylabel("z (m)")
        ax1.legend(fontsize=7, loc="upper left", framealpha=0.9)
        ax1.tick_params(labelsize=8)
        ax0.tick_params(labelsize=8)

        fig.suptitle("PLACEHOLDER VISUALIZATION, NOT A FINISHED RENDER   |   "
                     "NON-CANONICAL kinematic scene: the hull is DRIVEN and does not "
                     "respond to the water   |   no FORD verdict is derivable",
                     fontsize=8.5, y=0.985, color="#8a1c1c")
        fig.savefig(outdir / ("frame_%04d.png" % i), dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    pngs = sorted(outdir.glob("frame_*.png"))
    print("wrote %d frames to %s" % (len(pngs), outdir))
    mp4 = outdir / "moving_vehicle_placeholder.mp4"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
             "-i", str(outdir / "frame_%04d.png"),
             "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p", str(mp4)],
            check=True)
        print("wrote %s" % mp4)
    except Exception as e:
        print("ffmpeg step skipped: %s" % e)
    return outdir


def main():
    ap = argparse.ArgumentParser(description="placeholder render, see module docstring")
    ap.add_argument("--run", required=True, help="a run dir under out/moving_vehicle/")
    ap.add_argument("--out", default=None)
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()
    rundir = Path(args.run)
    outdir = Path(args.out) if args.out else rundir / "frames"
    render(rundir, outdir, fps=args.fps)


if __name__ == "__main__":
    main()
