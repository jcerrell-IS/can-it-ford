#!/usr/bin/env python3
"""Render an enhanced-pipeline rollout.npz, water and vehicle rendered as
what they actually are, not a fake box.

Schema this expects (confirmed 2026-08-08 against ctrl_g64 and enh_g128_real):
  water                    (frames, n_water, 3)   per-frame water particle positions
  speed                    (frames, n_water)      per-particle speed magnitude
  R                        (frames, 3, 3)         vehicle rotation matrix per frame
  t                        (frames, 3)            vehicle translation per frame
  veh_particles_vehframe   (n_vehicle, 3)         vehicle particles in body frame
  veh_particles_scene0     (n_vehicle, 3)         vehicle particles at frame 0, world frame
  veh_check_mid            (n_vehicle, 3)         export script's own reconstruction at checkpoint_frames[1]
  veh_check_last           (n_vehicle, 3)         export script's own reconstruction at checkpoint_frames[2]
  checkpoint_frames        (3,) int               frame indices for scene0/mid/last
  local_depth_bow          (frames,)              bow-wave local depth over time
  local_depth_footprint    (frames,)              footprint local depth over time
  depth, velocity, mass, n_grid, dx, h, floor, lim, extent, fps   scalars/metadata

Vehicle position at frame i is reconstructed as:
  veh_particles_vehframe @ R[i].T + t[i]

The script verifies this reconstruction against veh_check_mid/veh_check_last
before rendering a single frame, and refuses to proceed silently if the
reconstruction does not match the export script's own numbers.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np


VEHICLE_COLOR = (1.0, 0.45, 0.05, 0.85)   # categorical orange, Kumar convention


def reconstruct_vehicle(veh_vehframe: np.ndarray, R: np.ndarray, t: np.ndarray, frame_idx: int) -> np.ndarray:
    return veh_vehframe @ R[frame_idx].T + t[frame_idx]


def calibrate_and_verify(d: dict, post_tol_m: float = 0.005) -> np.ndarray:
    """Solve for the constant reference-frame offset between this script's
    R/t convention and whatever convention the export script used, using
    frame 0 where ground truth (veh_particles_scene0) is known directly.
    Then confirm that single offset, applied unchanged, also explains the
    mid and last checkpoints. If it does not, this is not a constant-offset
    situation and the script refuses to guess further.
    """
    veh_vehframe = d["veh_particles_vehframe"]
    R, t = d["R"], d["t"]
    ckpt = d["checkpoint_frames"]

    naive0 = reconstruct_vehicle(veh_vehframe, R, t, 0)
    raw_err0 = np.abs(naive0 - d["veh_particles_scene0"]).max()
    offset = (d["veh_particles_scene0"] - naive0).mean(axis=0)
    print(f"raw (uncorrected) error at frame 0: {raw_err0:.6f} m")
    print(f"calibrated offset (from frame 0):   {offset}")

    checks = [("mid", ckpt[1], d["veh_check_mid"]), ("last", ckpt[2], d["veh_check_last"])]
    for label, frame_idx, expected in checks:
        naive = reconstruct_vehicle(veh_vehframe, R, t, int(frame_idx))
        raw_err = np.abs(naive - expected).max()
        corrected_err = np.abs((naive + offset) - expected).max()
        print(f"checkpoint [{label}] frame={frame_idx}  raw_err={raw_err:.6f} m  "
              f"post_calibration_err={corrected_err:.6f} m")
        if corrected_err > post_tol_m:
            raise RuntimeError(
                f"After calibrating a constant offset from frame 0, checkpoint "
                f"[{label}] still disagrees by {corrected_err:.6f} m, more than "
                f"{post_tol_m} m. This is not a simple constant-offset situation, "
                f"refusing to render rather than guess further."
            )
    print(f"calibration confirmed at both checkpoints, applying offset to all {d['frames']} frames")
    return offset


def fixed_limits(water: np.ndarray, veh_vehframe: np.ndarray, R: np.ndarray, t: np.ndarray, offset: np.ndarray, pad_frac: float = 0.08):
    n_frames = R.shape[0]
    veh_all = np.stack([reconstruct_vehicle(veh_vehframe, R, t, i) + offset for i in range(n_frames)], axis=0)
    pts = np.vstack([water.reshape(-1, 3), veh_all.reshape(-1, 3)])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    pad = pad_frac * span
    return lo - pad, hi + pad, veh_all


def _ffmpeg_actually_runs(exe: str) -> bool:
    try:
        result = subprocess.run([exe, "-version"], capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def check_ffmpeg():
    """Return a working ffmpeg path, not just one that exists. A binary can
    be present on PATH and still fail at runtime, e.g. a missing shared
    library, so existence alone is not enough."""
    exe = shutil.which("ffmpeg")
    if exe and _ffmpeg_actually_runs(exe):
        return exe
    if exe:
        print(f"found ffmpeg at {exe} but it failed to run, trying imageio-ffmpeg instead")
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if _ffmpeg_actually_runs(exe):
            return exe
        print(f"imageio-ffmpeg's bundled binary at {exe} also failed to run")
    except Exception:
        pass
    return None


def draw_frame(ax_3d, ax_depth, water_i, speed_i, veh_i, floor_z, limits, vmax_speed,
               t_arr, bow, footprint, frame_idx, n_frames, args):
    lo, hi = limits
    ax_3d.clear()

    pts = water_i
    val = speed_i
    if args.max_water_points and len(pts) > args.max_water_points:
        idx = np.linspace(0, len(pts) - 1, args.max_water_points).astype(int)
        pts = pts[idx]
        val = val[idx]

    colors = cm.viridis(np.clip(val / vmax_speed, 0.0, 1.0))
    colors[:, 3] = args.water_alpha
    ax_3d.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=args.point_size, c=colors,
                  depthshade=False, edgecolors="none")

    ax_3d.scatter(veh_i[:, 0], veh_i[:, 1], veh_i[:, 2], s=args.point_size * 1.3,
                  c=[VEHICLE_COLOR], depthshade=False, edgecolors="none")

    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    floor_poly = [[lo[0], lo[1], floor_z], [hi[0], lo[1], floor_z],
                  [hi[0], hi[1], floor_z], [lo[0], hi[1], floor_z]]
    ax_3d.add_collection3d(Poly3DCollection([np.asarray(floor_poly)],
                            facecolors=(0.55, 0.50, 0.42, 0.12), edgecolors="none"))

    ax_3d.set_xlim(lo[0], hi[0]); ax_3d.set_ylim(lo[1], hi[1]); ax_3d.set_zlim(lo[2], hi[2])
    ax_3d.set_box_aspect(tuple(np.maximum(hi - lo, 1e-6)))
    ax_3d.view_init(elev=args.elev, azim=args.azim)
    ax_3d.set_xlabel("x (m)"); ax_3d.set_ylabel("y (m)"); ax_3d.set_zlabel("z (m)")
    ax_3d.set_title(
        f"depth={args.depth_label:.2f} m  velocity={args.velocity_label:.2f} m/s  "
        f"mass={args.mass_label:.0f} kg  n_grid={args.n_grid_label}   frame {frame_idx+1}/{n_frames}",
        fontsize=9,
    )

    ax_depth.clear()
    ax_depth.plot(t_arr, bow, color="#1f6fb2", lw=1.4, label="bow")
    ax_depth.plot(t_arr, footprint, color="#c0602a", lw=1.4, label="footprint")
    ax_depth.axvline(t_arr[frame_idx], color="black", lw=1.0)
    ax_depth.set_xlabel("frame")
    ax_depth.set_ylabel("local depth (m)")
    ax_depth.legend(loc="upper right", fontsize=7, frameon=False)
    ax_depth.set_xlim(t_arr[0], t_arr[-1])


def render(npz_path: Path, out_path: Path, args):
    d = dict(np.load(npz_path, allow_pickle=False))
    offset = calibrate_and_verify(d, post_tol_m=args.verify_tol_m)

    water = d["water"]
    speed = d["speed"]
    veh_vehframe = d["veh_particles_vehframe"]
    R, t = d["R"], d["t"]
    n_frames = water.shape[0]
    floor_z = float(d["floor"])
    depth_label = float(d["depth"])
    velocity_label = float(d["velocity"])
    mass_label = float(d["mass"])
    n_grid_label = int(d["n_grid"])
    fps = int(d["fps"]) if args.fps is None else args.fps

    print(f"loaded {npz_path}: {n_frames} frames, water={water.shape}, vehicle={veh_vehframe.shape}")

    lo, hi, veh_all = fixed_limits(water, veh_vehframe, R, t, offset)
    limits = (lo, hi)
    vmax_speed = max(float(np.percentile(speed, 98)), 1e-6)
    t_arr = np.arange(n_frames)
    bow = d["local_depth_bow"]
    footprint = d["local_depth_footprint"]

    args.depth_label = depth_label
    args.velocity_label = velocity_label
    args.mass_label = mass_label
    args.n_grid_label = n_grid_label

    ffmpeg_exe = check_ffmpeg()
    if ffmpeg_exe is None:
        raise RuntimeError("ffmpeg not found. pip install imageio-ffmpeg or add system ffmpeg to PATH.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmpdir = Path(tempfile.mkdtemp(prefix="mpm_render_", dir=str(out_path.parent)))
    encode_succeeded = False
    try:
        fig = plt.figure(figsize=(args.width / args.dpi, args.height / args.dpi), dpi=args.dpi)
        ax_3d = fig.add_axes([0.03, 0.22, 0.94, 0.75], projection="3d")
        ax_depth = fig.add_axes([0.08, 0.05, 0.84, 0.13])

        for i in range(n_frames):
            draw_frame(ax_3d, ax_depth, water[i], speed[i], veh_all[i], floor_z, limits,
                       vmax_speed, t_arr, bow, footprint, i, n_frames, args)
            fp = tmpdir / f"frame_{i:05d}.png"
            fig.savefig(fp, dpi=args.dpi, facecolor="white")
            if (i + 1) % 10 == 0 or i == n_frames - 1:
                print(f"rendered {i+1}/{n_frames} frames", flush=True)
        plt.close(fig)

        cmd = [
            ffmpeg_exe, "-y",
            "-framerate", str(fps),
            "-i", str(tmpdir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-threads", "1",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            "-crf", str(args.crf),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            str(out_path),
        ]
        subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)
        print(f"wrote {out_path} using ffmpeg at {ffmpeg_exe}")
        encode_succeeded = True
    finally:
        if encode_succeeded and not args.keep_frames:
            shutil.rmtree(tmpdir, ignore_errors=True)
        elif not encode_succeeded:
            print(f"ffmpeg step failed, frames were NOT deleted, they're at {tmpdir}")
            print(f"once ffmpeg is fixed, re-encode directly without re-rendering:")
            print(f"  ffmpeg -y -framerate {fps} -i {tmpdir}/frame_%05d.png "
                  f"-c:v libx264 -threads 1 -preset slow -pix_fmt yuv420p -crf {args.crf} "
                  f"-vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' {out_path}")
        else:
            print(f"kept frame PNGs in {tmpdir}")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="rollout.npz path")
    ap.add_argument("--output", default="rollout_render.mp4")
    ap.add_argument("--fps", type=int, default=None, help="override npz's own fps field")
    ap.add_argument("--point-size", type=float, default=3.0)
    ap.add_argument("--water-alpha", type=float, default=0.55)
    ap.add_argument("--max-water-points", type=int, default=60000, help="subsample per frame; 0 disables")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=960)
    ap.add_argument("--dpi", type=int, default=120)
    ap.add_argument("--elev", type=float, default=22.0)
    ap.add_argument("--azim", type=float, default=-55.0)
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--keep-frames", action="store_true")
    ap.add_argument("--verify-tol-m", type=float, default=0.005,
                     help="max allowed error after constant-offset calibration, meters")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    render(Path(args.input), Path(args.output), args)


if __name__ == "__main__":
    main()
