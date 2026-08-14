"""
render_moving_vehicle_surface.py

Surface renderer for simulation/moving_vehicle_sdf_exploratory.py.

NON-CANONICAL / EXPLORATORY. This visualizes what the water does around a moving
hull and nothing else. No FORD language, no comparison against the 17 canonical
runs.

WHAT IT DRAWS, and how that differs from the scatter it replaces
  vehicle  the ACTUAL watertight PLY surface, as a solid shaded mesh, loaded
           through the same vetted loader and the same canonicalize() the
           simulation used, so it is the identical geometry the SDF was built
           from. It is NOT a particle sample of the hull and NOT a wireframe.
  water    a reconstructed free surface: particle positions are binned into a
           density field, smoothed, and contoured with skimage marching_cubes at
           half bulk density. It is NOT a scatter of raw particles.
  floor    the bed plane at z = floor, drawn as a plane, plus the domain edges.

ON THE POSE, read this before assuming a rotation is being applied
  This scene is KINEMATIC. The hull is a prescribed-velocity SDF collider
  registered with quat (0,0,0,1) and omega (0,0,0), and nothing in the scene can
  rotate it, so there is no tracked orientation to apply and this renderer does
  not invent one. The tracked pose is a pure TRANSLATION: the per-frame collider
  centre, read back out of the engine during the run
  (collider_params[handle].center) and stored in rollout.npz as `centers`. That
  is the transform applied here, verbatim, per frame.

  This is the honest difference from a free-rigid run, where the body genuinely
  rotates and a renderer must reconstruct R and t. See
  analysis/render_multigeom_rollout.py for that case; its schema does not apply
  to a kinematic collider.

DENSITY OF THE INPUT MATTERS
  rollout.npz stores water subsampled by --particle-stride. Re-run the sim with
  --particle-stride 1 before rendering, or the reconstructed surface is built
  from half the particles and reads lumpier than the simulation actually is.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
import pyvista as pv
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes

pv.OFF_SCREEN = True

REPO = Path(__file__).resolve().parent.parent
LOADER_PATH = REPO / "analysis" / "render_v1" / "as_ran_local_copies" / "vehicle_live.py"

WATER_RGB = "#2f7fc4"
HULL_RGB = "#c8ccd2"
FLOOR_RGB = "#6b6257"


def load_hull_mesh(hull_path, mesh_seed=0):
    """Same loader, same canonicalize, same seed as the simulation, so this is the
    identical geometry the SDF was built from rather than a lookalike."""
    sys.path.insert(0, str(REPO / "simulation"))
    from moving_vehicle_sdf_exploratory import canonicalize, load_vetted_loader
    vl = load_vetted_loader()
    np.random.seed(mesh_seed)
    veh = canonicalize(vl.load_vehicle(hull_path, up="z", spacing=0.40))
    m = veh.mesh
    verts = np.asarray(m.vertices, dtype=np.float64)
    faces = np.asarray(m.faces, dtype=np.int64)
    tri = np.hstack([np.full((len(faces), 1), 3, dtype=np.int64), faces]).ravel()
    return verts, tri, m


def water_surface(pts, pitch, lo, hi, sigma=1.1, level=0.5):
    """Reconstruct a free surface from particle positions.

    Bin to a density field, smooth, contour at half bulk density. Returns a
    pyvista PolyData, or None if the field never crosses the level."""
    dims = np.maximum(np.ceil((hi - lo) / pitch).astype(int), 2)
    H, _ = np.histogramdd(pts, bins=dims, range=[(lo[d], lo[d] + dims[d] * pitch)
                                                 for d in range(3)])
    if H.max() <= 0:
        return None
    field = gaussian_filter(H.astype(np.float64), sigma=sigma)
    occupied = field[field > 0]
    if not len(occupied):
        return None
    bulk = float(np.percentile(occupied, 80))
    if bulk <= 0:
        return None
    field = field / bulk
    if field.min() >= level or field.max() <= level:
        return None
    v, f, _, _ = marching_cubes(field, level=level, spacing=(pitch, pitch, pitch))
    v = v + lo + 0.5 * pitch          # cell centres, not cell corners
    tri = np.hstack([np.full((len(f), 1), 3, dtype=np.int64), f]).ravel()
    return pv.PolyData(v, tri)


def render(rundir: Path, hull_path: str, outdir: Path, fps=30, size=(1280, 760),
           pitch_scale=1.0, sigma=1.1, level=0.5, mesh_seed=0, follow=True,
           elev_span_mm=90.0, cam_scale=1.0):
    meta = json.loads((rundir / "meta.json").read_text())
    d = np.load(rundir / "rollout.npz", allow_pickle=True)
    water = d["water"]
    centers = np.asarray(d["centers"], dtype=np.float64)
    floor = float(d["floor"])
    depth = float(d["depth"])
    lim = float(d["lim"])
    dx = float(d["dx"])
    h = 0.5 * dx
    pitch = pitch_scale * h

    hull_v0, hull_tri, hull_mesh = load_hull_mesh(hull_path, mesh_seed=mesh_seed)
    print("hull surface: %d verts %d faces watertight=%s volume %.6f m3"
          % (len(hull_v0), len(hull_tri) // 4, hull_mesh.is_watertight,
             float(hull_mesh.volume)), flush=True)
    print("pose applied per frame: TRANSLATION ONLY by rollout `centers`; the "
          "collider quat is identity and omega is zero, so there is no rotation "
          "to apply and none is invented.", flush=True)

    lo = np.array([0.0, 0.0, floor - 3.0 * pitch])
    hi = np.array([lim, lim, floor + depth + 10.0 * pitch])
    # sim_standing.py:180 puts the slip walls at 4*dx, and the water block starts
    # there, so the reconstruction rim sits just inside them
    wall = 4.0 * dx
    wall_lo, wall_hi = wall + 0.5 * dx, lim - wall - 0.5 * dx
    # the discrete free surface is the top particle layer, at floor + (layers-0.5)*h,
    # NOT floor + depth. Colouring against floor + depth would bake in a fixed offset.
    layers = max(int(np.floor((depth - 0.5 * h) / h)) + 1, 1)
    still = floor + (layers - 0.5) * h
    elev_span = float(elev_span_mm)

    outdir.mkdir(parents=True, exist_ok=True)

    def camera_for(cy):
        """Three-quarter front view. The focal point sits AHEAD of the hull so the
        water it is driving into stays in frame, which is the whole question."""
        if follow:
            focal = np.array([lim * 0.5, cy + 2.6, floor + 0.10])
        else:
            focal = np.array([lim * 0.5, lim * 0.52, floor + 0.10])
        off = cam_scale * np.array([9.0, -8.2, 4.6])
        return [tuple(focal + off), tuple(focal), (0.0, 0.0, 1.0)]

    for i in range(len(water)):
        w = np.asarray(water[i], dtype=np.float64)
        c = centers[i]

        p = pv.Plotter(off_screen=True, window_size=size)
        p.set_background("white")

        bed = pv.Plane(center=(lim / 2, lim / 2, floor), direction=(0, 0, 1),
                       i_size=lim, j_size=lim)
        p.add_mesh(bed, color=FLOOR_RGB, opacity=0.28, lighting=False)

        surf = water_surface(w, pitch, lo, hi, sigma=sigma, level=level)
        if surf is not None:
            surf = surf.smooth(n_iter=30, relaxation_factor=0.12)
            # Clip off the domain rim. The density field falls to zero at the walls,
            # so marching cubes closes the volume there and draws a raised lip that
            # is an artifact of the reconstruction, not water.
            # clip_box returns an UnstructuredGrid, so extract_surface to get PolyData back
            surf = surf.clip_box([wall_lo, wall_hi, wall_lo, wall_hi,
                                  lo[2] - 1.0, hi[2] + 1.0],
                                 invert=False).extract_surface()
            if surf.n_points:
                surf.compute_normals(inplace=True, auto_orient_normals=True)
                surf["elev_mm"] = (surf.points[:, 2] - still) * 1e3
                p.add_mesh(surf, scalars="elev_mm", cmap="RdBu_r",
                           clim=[-elev_span, elev_span], opacity=0.80,
                           smooth_shading=True, specular=0.45, specular_power=20,
                           ambient=0.22, diffuse=0.74,
                           scalar_bar_args={"title": "free surface, mm above still",
                                            "vertical": True, "position_x": 0.885,
                                            "position_y": 0.28, "height": 0.44,
                                            "width": 0.035, "title_font_size": 11,
                                            "label_font_size": 10, "color": "#222222"})

        hull = pv.PolyData(hull_v0 + c[None, :], hull_tri)
        hull.compute_normals(inplace=True, auto_orient_normals=True)
        p.add_mesh(hull, color=HULL_RGB, smooth_shading=True, specular=0.35,
                   specular_power=15, ambient=0.24, diffuse=0.72)

        p.camera_position = camera_for(c[1])
        p.add_text("NON-CANONICAL exploratory. Kinematic scene: the hull is DRIVEN "
                   "and does not respond to the water.",
                   position="upper_left", font_size=8, color="#8a1c1c")
        p.add_text("frame %d/%d   t=%.3f s   v=%.2f m/s   hull y=%.3f m   "
                   "depth %.2f m (%.1f grid cells)"
                   % (i + 1, len(water), (i + 1) / float(fps), meta["velocity_ms"],
                      c[1], depth, depth / dx),
                   position="lower_left", font_size=9, color="#222222")
        p.screenshot(str(outdir / ("frame_%04d.png" % i)))
        p.close()
        if (i + 1) % 10 == 0 or i == len(water) - 1:
            print("  rendered %d/%d" % (i + 1, len(water)), flush=True)

    pngs = sorted(outdir.glob("frame_*.png"))
    print("wrote %d frames to %s" % (len(pngs), outdir))
    mp4 = outdir / "moving_vehicle_surface.mp4"
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
                        "-i", str(outdir / "frame_%04d.png"),
                        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                        "-pix_fmt", "yuv420p", str(mp4)], check=True)
        print("wrote %s" % mp4)
    except Exception as e:
        print("ffmpeg step skipped: %s" % e)
    return outdir


def main():
    ap = argparse.ArgumentParser(description="surface render, see module docstring")
    ap.add_argument("--run", required=True, help="a run dir under out/moving_vehicle/")
    ap.add_argument("--hull", required=True, help="the same .ply the run used")
    ap.add_argument("--out", default=None)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--pitch-scale", type=float, default=1.0,
                    help="surfacing grid pitch as a multiple of the particle spacing h")
    ap.add_argument("--sigma", type=float, default=1.1)
    ap.add_argument("--level", type=float, default=0.5)
    ap.add_argument("--mesh-seed", type=int, default=0)
    ap.add_argument("--elev-span-mm", type=float, default=90.0,
                    help="symmetric colour range for free-surface elevation")
    ap.add_argument("--cam-scale", type=float, default=1.0,
                    help="camera distance multiplier")
    ap.add_argument("--no-follow", action="store_true",
                    help="fixed camera instead of one that tracks the hull")
    args = ap.parse_args()
    rundir = Path(args.run)
    outdir = Path(args.out) if args.out else rundir / "surface"
    render(rundir, args.hull, outdir, fps=args.fps, pitch_scale=args.pitch_scale,
           sigma=args.sigma, level=args.level, mesh_seed=args.mesh_seed,
           follow=not args.no_follow, elev_span_mm=args.elev_span_mm,
           cam_scale=args.cam_scale)


if __name__ == "__main__":
    main()
