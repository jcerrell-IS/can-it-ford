#!/usr/bin/env python3
"""Render MPM particle frames plus a rigid box collider to MP4, headlessly.

Primary path for Vista/DesignSafe/MacBook: Matplotlib Agg + imageio-ffmpeg.

Accepted inputs:
  1) .npz with positions under one of: positions, x, X, frames
     shape must be (T, N, 3) or (N, 3) for one frame.
     Optional velocities under one of: velocities, v, V, speeds, spd.
  2) directory containing per-frame .npz files (e.g. f_0000.npz) with x/positions.
  3) no input: generates a small synthetic water-flow demo.

Example:
  python render_frames.py --input rollout_particles.npz --output water_box.mp4 \
      --box-center 1.0 0.0 0.35 --box-size 0.45 0.30 0.30 --fps 24
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable

# Force a non-interactive backend before pyplot import. Works without DISPLAY/X11.
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


def _first_key(npz, keys: Iterable[str]):
    for k in keys:
        if k in npz.files:
            return k
    return None


def load_frames(path: str | None):
    """Return positions (T,N,3), optional velocities/speeds, and source label."""
    if path is None:
        return make_demo_frames(), None, "synthetic-demo"
    p = Path(path)
    if p.is_dir():
        files = sorted(p.glob("*.npz"))
        if not files:
            raise FileNotFoundError(f"No .npz files found in directory {p}")
        xs, vs = [], []
        for f in files:
            with np.load(f, allow_pickle=False) as d:
                kx = _first_key(d, ("positions", "x", "X", "frames"))
                if kx is None:
                    raise KeyError(f"{f} has no positions/x/X/frames array")
                xs.append(np.asarray(d[kx], dtype=np.float32))
                kv = _first_key(d, ("velocities", "v", "V", "speeds", "spd"))
                if kv is not None:
                    vs.append(np.asarray(d[kv], dtype=np.float32))
        X = np.stack(xs, axis=0)
        V = np.stack(vs, axis=0) if len(vs) == len(xs) else None
        return _ensure_TN3(X), V, str(p)
    with np.load(p, allow_pickle=False) as d:
        kx = _first_key(d, ("positions", "x", "X", "frames"))
        if kx is None:
            raise KeyError(f"{p} has no positions/x/X/frames array; keys={d.files}")
        X = _ensure_TN3(np.asarray(d[kx], dtype=np.float32))
        kv = _first_key(d, ("velocities", "v", "V", "speeds", "spd"))
        V = np.asarray(d[kv], dtype=np.float32) if kv is not None else None
        return X, V, str(p)


def _ensure_TN3(a: np.ndarray) -> np.ndarray:
    if a.ndim == 2 and a.shape[1] == 3:
        return a[None, ...]
    if a.ndim == 3 and a.shape[2] == 3:
        return a
    raise ValueError(f"Expected positions shape (T,N,3) or (N,3), got {a.shape}")


def make_demo_frames(T=140, nx=38, ny=12, nz=9):
    """Small synthetic flow around a fixed box; useful for testing the renderer."""
    rng = np.random.default_rng(4)
    xs = np.linspace(-1.0, 1.0, nx)
    ys = np.linspace(-0.35, 0.35, ny)
    zs = np.linspace(0.02, 0.34, nz)
    grid = np.array(np.meshgrid(xs, ys, zs, indexing="ij")).reshape(3, -1).T
    grid += rng.normal(scale=[0.008, 0.006, 0.004], size=grid.shape)
    out = []
    for t in range(T):
        phase = 2 * np.pi * t / T
        pts = grid.copy()
        pts[:, 0] += 1.25 * t / (T - 1)
        pts[:, 0] = ((pts[:, 0] + 1.1) % 2.6) - 1.1
        pts[:, 1] += 0.04 * np.sin(5 * pts[:, 0] + phase) * np.exp(-2 * np.abs(pts[:, 1]))
        pts[:, 2] += 0.018 * np.sin(7 * pts[:, 0] - 2 * phase)
        pts[:, 2] = np.clip(pts[:, 2], 0.005, None)
        out.append(pts.astype(np.float32))
    return np.asarray(out, dtype=np.float32)


def box_faces(center, size):
    c = np.asarray(center, dtype=float)
    h = 0.5 * np.asarray(size, dtype=float)
    x0, y0, z0 = c - h
    x1, y1, z1 = c + h
    v = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ])
    return [v[idx] for idx in ([0,1,2,3], [4,5,6,7], [0,1,5,4], [2,3,7,6], [1,2,6,5], [0,3,7,4])]


def fixed_limits(X, box_center, box_size, pad_frac=0.08):
    bfaces = np.vstack(box_faces(box_center, box_size))
    pts = np.vstack([X.reshape(-1, 3), bfaces])
    lo, hi = np.nanmin(pts, axis=0), np.nanmax(pts, axis=0)
    span = np.maximum(hi - lo, 1e-6)
    pad = pad_frac * span
    return lo - pad, hi + pad


def draw_frame(ax, pts, vel_or_speed, frame_idx, n_frames, limits, box_center, box_size, args):
    lo, hi = limits
    ax.clear()
    if args.max_points and len(pts) > args.max_points:
        idx = np.linspace(0, len(pts) - 1, args.max_points).astype(int)
        pts = pts[idx]
        if vel_or_speed is not None and len(vel_or_speed) == len(idx):
            vel_or_speed = vel_or_speed[idx]

    if vel_or_speed is None:
        colors = np.full((len(pts), 4), (0.10, 0.45, 1.0, args.water_alpha))
    else:
        val = np.linalg.norm(vel_or_speed, axis=1) if vel_or_speed.ndim == 2 else np.asarray(vel_or_speed)
        vmax = np.percentile(val, 98) if np.isfinite(val).any() else 1.0
        vmax = max(float(vmax), 1e-8)
        colors = cm.Blues(np.clip(val / vmax, 0.15, 1.0))
        colors[:, 3] = args.water_alpha

    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=args.point_size, c=colors,
               depthshade=False, edgecolors="none")

    # Rigid box collider: orange translucent solid with dark edges.
    faces = box_faces(box_center, box_size)
    poly = Poly3DCollection(faces, facecolors=(1.0, 0.45, 0.05, 0.35),
                            edgecolors=(0.25, 0.12, 0.02, 1.0), linewidths=1.2)
    ax.add_collection3d(poly)

    # Ground/water-bed plane cue.
    if args.show_floor:
        z = lo[2]
        floor = [[lo[0], lo[1], z], [hi[0], lo[1], z], [hi[0], hi[1], z], [lo[0], hi[1], z]]
        ax.add_collection3d(Poly3DCollection([np.asarray(floor)], facecolors=(0.55, 0.50, 0.42, 0.12), edgecolors="none"))

    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(np.maximum(hi - lo, 1e-6)))
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title(f"MPM water particles + rigid box collider  frame {frame_idx+1}/{n_frames}")
    if args.axis_off:
        ax.set_axis_off()


def check_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def render_movie(X, V, out_path: Path, args):
    ffmpeg_exe = check_ffmpeg()
    if ffmpeg_exe is None:
        raise RuntimeError("ffmpeg not found. Install with `pip install imageio-ffmpeg` or add system ffmpeg to PATH.")

    limits = fixed_limits(X, args.box_center, args.box_size)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmpdir = Path(tempfile.mkdtemp(prefix="mpm_frames_", dir=str(out_path.parent)))
    try:
        fig = plt.figure(figsize=(args.width / args.dpi, args.height / args.dpi), dpi=args.dpi)
        ax = fig.add_subplot(111, projection="3d")
        frame_paths = []
        for i in range(X.shape[0]):
            vi = None
            if V is not None:
                vi = V[i] if V.ndim >= 2 and len(V) == len(X) else V
            draw_frame(ax, X[i], vi, i, X.shape[0], limits, args.box_center, args.box_size, args)
            fig.tight_layout(pad=0.1)
            fp = tmpdir / f"frame_{i:05d}.png"
            fig.savefig(fp, dpi=args.dpi, facecolor="white")
            frame_paths.append(fp)
            if (i + 1) % 25 == 0 or i == X.shape[0] - 1:
                print(f"rendered {i+1}/{X.shape[0]} frames", flush=True)
        plt.close(fig)

        # Prefer direct ffmpeg: fewer Python dependencies than imageio, and works
        # with either system ffmpeg or the binary bundled by imageio-ffmpeg.
        import subprocess
        cmd = [
            ffmpeg_exe, "-y",
            "-framerate", str(args.fps),
            "-i", str(tmpdir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", str(args.crf),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            str(out_path),
        ]
        subprocess.run(cmd, check=True)
        print(f"wrote {out_path} using ffmpeg at {ffmpeg_exe}")
    finally:
        if not args.keep_frames:
            # Keep generated user outputs, remove only this script's temp folder by default.
            shutil.rmtree(tmpdir, ignore_errors=True)
        else:
            print(f"kept frame PNGs in {tmpdir}")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=None, help=".npz file or directory of per-frame .npz files; omit for demo")
    ap.add_argument("--output", default="mpm_water_box.mp4", help="output .mp4 path")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--box-center", type=float, nargs=3, default=(0.25, 0.0, 0.18), metavar=("X", "Y", "Z"))
    ap.add_argument("--box-size", type=float, nargs=3, default=(0.35, 0.28, 0.28), metavar=("SX", "SY", "SZ"))
    ap.add_argument("--point-size", type=float, default=3.0)
    ap.add_argument("--water-alpha", type=float, default=0.55)
    ap.add_argument("--max-points", type=int, default=120000, help="subsample per frame for speed; 0 disables")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--dpi", type=int, default=120)
    ap.add_argument("--elev", type=float, default=18.0)
    ap.add_argument("--azim", type=float, default=-55.0)
    ap.add_argument("--crf", type=int, default=20, help="x264 quality; lower is larger/better")
    ap.add_argument("--axis-off", action="store_true")
    ap.add_argument("--show-floor", action="store_true")
    ap.add_argument("--keep-frames", action="store_true")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    X, V, src = load_frames(args.input)
    if args.max_points == 0:
        args.max_points = None
    print(f"loaded {src}: positions shape={X.shape}; velocities={'yes' if V is not None else 'no'}")
    render_movie(X, V, Path(args.output), args)


if __name__ == "__main__":
    main()
