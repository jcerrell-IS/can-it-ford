"""Decode assets/DaySkyHDRI002A_1K_HDR.exr to the .npy cache the shaded renderer
reads, and derive the sun direction from the map itself.

WHY THIS EXISTS. render_multigeom_shaded.py:113-114 loads hdri_sky.npy and
hdri_sun.npy from a --hdri-cache directory, and its docstring notes the .exr is
decoded "once to .npy because no EXR backend is installed in the render venv".
That decode was previously done ad hoc in a session scratchpad. Scratchpads are
deleted, and as of 2026-08-13 no hdri_sky.npy exists anywhere on this machine, so
the shaded renderer could not be run at all. This script makes the cache
reproducible instead of ephemeral.

THE .exr IS READ, NEVER WRITTEN. This produces a derived cache alongside it.

RUNNING IT. The production venv (~/.venvs/canitford-mpm) has no EXR backend, and
this script deliberately does not ask you to add one to a shared environment. Run
it under a throwaway environment that does:

    uv run --with numpy --with opencv-python-headless \
        analysis/make_hdri_cache.py --exr assets/DaySkyHDRI002A_1K_HDR.exr \
        --outdir <cache dir>

then point --hdri-cache at <cache dir> when running the renderer with the
production venv.

CONVENTIONS, matched to render_multigeom_shaded.sample_env at :118-126:
  equirectangular, z up, polar angle measured from +z, row j = pol/pi * H,
  azimuth atan2(y, x), column i = (az/2pi + 0.5) * W.
The sun direction is the radiance-weighted mean direction of the brightest
pixels, which for a clear-sky map is the solar disc. It is written unnormalised;
the loader normalises at :115.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def read_exr(path):
    """Read an .exr to a float32 (H, W, 3) RGB array."""
    try:
        import cv2
    except ImportError as exc:
        raise SystemExit(
            "No EXR backend. Re-run under an environment that has one, e.g.\n"
            "  uv run --with numpy --with opencv-python-headless %s ...\n"
            "(underlying import error: %s)" % (__file__, exc))
    import os
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH
                     | cv2.IMREAD_ANYCOLOR)
    if img is None:
        raise SystemExit("cv2 could not decode %s" % path)
    if img.ndim == 2:
        img = np.dstack([img] * 3)
    # cv2 returns BGR
    return np.ascontiguousarray(img[:, :, :3][:, :, ::-1]).astype(np.float32)


def sun_direction(sky, mode="argmax", top_fraction=1e-4):
    """Sun direction from the map, z up.

    Inverts sample_env's mapping: row j -> polar angle, column i -> azimuth.

    TWO MODES, AND THE DEFAULT MATTERS FOR REPRODUCIBILITY.
      "argmax"   the single brightest pixel. This is what produced the sun
                 vector recorded in the shipped 2026-08-12 manifests, so it is
                 the default: regenerating the cache must reproduce published
                 frames, not quietly move every specular highlight.
      "centroid" radiance-weighted mean direction of the brightest
                 `top_fraction` of pixels, weighted by sin(polar) to undo the
                 equirectangular area distortion. Less sensitive to a single hot
                 pixel, but NOT what shipped.

    Measured on assets/DaySkyHDRI002A_1K_HDR.exr, the two differ by 1.0963 deg
    (argmax elevation 63.81 deg against centroid 64.41 deg). That is small but it
    moves every GGX highlight, so the mode is recorded in the output and should
    be recorded in the render manifest too.
    """
    H, W, _ = sky.shape
    lum = (0.2126 * sky[:, :, 0] + 0.7152 * sky[:, :, 1] + 0.0722 * sky[:, :, 2])
    lum = np.nan_to_num(lum, nan=0.0, posinf=0.0, neginf=0.0)

    if mode == "argmax":
        j, i = np.unravel_index(int(np.argmax(lum)), lum.shape)
        jj = np.array([j])
        ii = np.array([i])
        w = np.array([1.0])
    elif mode == "centroid":
        n_top = max(1, int(round(top_fraction * lum.size)))
        thresh = np.partition(lum.ravel(), -n_top)[-n_top]
        jj, ii = np.nonzero(lum >= thresh)
        w = lum[jj, ii]
    else:
        raise SystemExit("unknown --sun-mode %r, use argmax or centroid" % mode)

    pol = (jj + 0.5) / H * np.pi
    az = ((ii + 0.5) / W - 0.5) * 2.0 * np.pi
    if mode == "centroid":
        w = w * np.sin(pol)                  # equirect area weight

    d = np.stack([np.sin(pol) * np.cos(az),
                  np.sin(pol) * np.sin(az),
                  np.cos(pol)], axis=1)
    v = (d * w[:, None]).sum(0)
    n = np.linalg.norm(v)
    if n < 1e-12:
        raise SystemExit("Could not locate a sun direction: the map has no "
                         "concentrated bright region.")
    return v / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exr", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--sun-mode", choices=("argmax", "centroid"), default="argmax",
                    help="argmax (default) reproduces the sun vector in the "
                         "shipped 2026-08-12 manifests; centroid averages the "
                         "brightest --top-fraction and differs by 1.1 deg")
    ap.add_argument("--top-fraction", type=float, default=1e-4,
                    help="centroid mode only: fraction of brightest pixels "
                         "taken as the solar disc")
    a = ap.parse_args()

    exr = Path(a.exr)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    sky = read_exr(exr)
    if not np.all(np.isfinite(sky)):
        n_bad = int((~np.isfinite(sky)).sum())
        print("[hdri] NOTE: %d non-finite samples zeroed" % n_bad)
        sky = np.nan_to_num(sky, nan=0.0, posinf=0.0, neginf=0.0)
    sun = sun_direction(sky, mode=a.sun_mode, top_fraction=a.top_fraction)

    np.save(out / "hdri_sky.npy", sky.astype(np.float32))
    np.save(out / "hdri_sun.npy", sun.astype(np.float32))

    lum = 0.2126 * sky[:, :, 0] + 0.7152 * sky[:, :, 1] + 0.0722 * sky[:, :, 2]
    print("[hdri] source     %s" % exr)
    print("[hdri] sky        %s  range %.4f to %.2f  mean %.4f"
          % (sky.shape, float(lum.min()), float(lum.max()), float(lum.mean())))
    print("[hdri] sun mode   %s" % a.sun_mode)
    print("[hdri] sun dir    [%+.5f %+.5f %+.5f]  elevation %.2f deg"
          % (sun[0], sun[1], sun[2], np.degrees(np.arcsin(np.clip(sun[2], -1, 1)))))
    # Sun vector recorded in the shipped 2026-08-12 render manifests. Reproducing
    # it is the test that a regenerated cache will not move the specular
    # highlights in already-published frames.
    shipped = np.array([0.0580579936504364, -0.4375361502170563,
                        0.8973246216773987])
    sep = np.degrees(np.arccos(np.clip(float(sun @ shipped), -1.0, 1.0)))
    print("[hdri] vs shipped 2026-08-12 manifest sun: %.4f deg apart%s"
          % (sep, "  OK" if sep < 0.05 else
             "  <-- WILL NOT REPRODUCE PUBLISHED FRAMES"))
    print("[hdri] wrote      %s, %s" % (out / "hdri_sky.npy", out / "hdri_sun.npy"))
    if sun[2] <= 0:
        print("[hdri] WARNING: sun is at or below the horizon; check the map.")


if __name__ == "__main__":
    main()
