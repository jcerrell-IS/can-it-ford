#!/usr/bin/env python3
"""Render a warpmpm rollout.npz (water + free-rigid vehicle) to PNG frames.

WHY THIS EXISTS
  The multigeom 2026-08-08 runs use the Rogue and Silverado hulls. Every existing
  renderer in renders/yaris_render_s1/ draws the vehicle as a shaded mesh loaded
  from a hardcoded Yaris .ply (t1_car.py:17, render_hero_g64_m1100_2026-08-06.py:47,
  render_flood.py via geom_live), and neither non-Yaris .ply exists on this machine.
  Register E8 also forbids committing derived CCSA/NCAC geometry. So the vehicle is
  drawn here from veh_particles_scene0, the rigid particle cloud already inside the
  npz, and no mesh is loaded at all.

  The two repo-level scripts do not apply. render_frames.py matches the 0-d scalar
  key "frames" as if it were a position array and dies in _ensure_TN3; it also has
  no vehicle path, only a static --box-center/--box-size proxy. render_hero_shot.py
  is a Blender bpy still that reads pos/vel and draws a hardcoded cube.

TRANSFORM: NOT NEW CODE. Reused verbatim from gates.py, the script that produces
the published gate verdicts:
    pv     = (veh_particles_scene0 - t[0]) @ R[0]        gates.py:136
    vp(f)  = pv @ R[f].T + t[f]                          gates.py:157
Starting from veh_particles_scene0 (not veh_particles_vehframe) is what makes the
body-frame offset `off` of t1_car.py:49-58 unnecessary: gates.py derives pv from
the scene checkpoint itself, so the offset is already folded in. The reconstruction
is verified against the stored veh_check_45 and veh_check_last every run and the
script aborts if it does not reproduce them.

AXES: the hull's LONG AXIS IS Y in the gated scene (CLAUDE.md item 4c). The car
profile is therefore the (y, z) plane and the flow direction is +x, so the vehicle
is broadside to the flow. Plotting (x, z) as a "side view" shows the car's WIDTH
and makes any hull look like a tall blob.

FLOOR: the npz scalar `floor` is the ground plane, `3.0 * dx` at sim_standing.py:164,
used as the domain lower bound at :253. It is NOT the vehicle z-min, though for a
hull at rest the two coincide.

USAGE
  render_multigeom_rollout.py --run <dir with rollout.npz+summary.json> --outdir <dir>
                              [--frames all|<int>] [--caveat "..."] [--max-water N]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

BANNER = ("NON-CANONICAL   multigeom 2026-08-08   "
          "not part of the 17-run gated inventory")

VEH_COLOR = "#b3282d"
FLOOR_COLOR = "#222222"

# dough_surface_render.py:25, via t1_car.py:20-21
LIGHT = np.array([0.35, 0.55, 0.78])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
BODY = np.array([0.70, 0.13, 0.13])
TIRE = np.array([0.13, 0.13, 0.15])


def load_run(run: Path):
    d = np.load(run / "rollout.npz")
    s = json.loads((run / "summary.json").read_text())
    out = {
        "water": d["water"], "speed": d["speed"],
        "R": d["R"].astype(np.float64), "t": d["t"].astype(np.float64),
        "scene0": d["veh_particles_scene0"].astype(np.float64),
        "check45": d["veh_check_45"].astype(np.float64),
        "checklast": d["veh_check_last"].astype(np.float64),
        "floor": float(d["floor"]), "dx": float(d["dx"]), "lim": float(d["lim"]),
        "fps": int(d["fps"]), "frames": int(d["frames"]),
        "depth": float(d["depth"]), "velocity": float(d["velocity"]),
        "mass": float(d["mass"]), "n_grid": int(d["n_grid"]),
        "summary": s,
    }
    d.close()
    return out


def rigid_transform(z):
    """gates.py:136 and :157, verbatim, with a reproduction check against the
    stored checkpoints. Returns (pv, world_fn, worst_error_m, errors_by_frame)."""
    R, t = z["R"], z["t"]
    pv = (z["scene0"] - t[0]) @ R[0]

    def world(f):
        return pv @ R[f].T + t[f]

    nf = R.shape[0]
    f45 = min(45, nf - 1)
    errs = {
        0: float(np.abs(world(0) - z["scene0"]).max()),
        f45: float(np.abs(world(f45) - z["check45"]).max()),
        nf - 1: float(np.abs(world(nf - 1) - z["checklast"]).max()),
    }
    worst = max(errs.values())
    if not np.isfinite(worst) or worst > 1e-4:
        raise SystemExit(
            "TRANSFORM FAILED to reproduce the stored checkpoints: %s. "
            "Refusing to render a vehicle whose pose is not verified." % errs)
    return pv, world, worst, errs


def build_surface(pv, h, upsample=2, sigma=1.0, level=0.5, max_faces=9000):
    """Closed surface for the rigid body, built ONCE in the body frame.

    The body is rigid, so the surface is extracted once and only transformed per
    frame. No mesh is read from disk: the Rogue and Silverado .ply files do not
    exist on this machine and register E8 forbids committing them anyway. This is
    a reconstruction of the SIMULATED body, so it shows the geometry the solver
    actually integrated, resolution loss included.

    The solid is the UNION OF PARTICLE CELLS, not a blurred point set. Each MPM
    particle stands for a cell of side h, so the occupancy lattice is dilated by
    the particle half-cell before smoothing. An earlier version blurred the bare
    lattice and normalised by the field max; that eroded the extremities, putting
    209 of the Yaris hull's 8905 particles outside the reconstructed surface's own
    bounding box and lifting the rendered underside off the floor. Since floor
    contact is exactly what these renders are read for, the surface is checked
    against the particle bbox by the caller and the erosion must be ~0.
    """
    from scipy.ndimage import binary_dilation, gaussian_filter
    from skimage import measure

    g = h / float(upsample)
    lo = pv.min(0) - 4.0 * h
    hi = pv.max(0) + 4.0 * h
    dims = np.ceil((hi - lo) / g).astype(int) + 1
    occ = np.zeros(dims, dtype=bool)
    idx = np.rint((pv - lo) / g).astype(np.int64)
    idx = np.clip(idx, 0, dims - 1)
    occ[idx[:, 0], idx[:, 1], idx[:, 2]] = True

    # Calibration. summary.json solid_volume_m3 equals n_particles * h**3 to 5
    # significant figures in all three runs, so each particle IS a cube of side h
    # and the true boundary sits at particle_extreme + h/2. Marching cubes at level
    # 0.5 on a blurred binary lands half a grid cell beyond the outermost OCCUPIED
    # CELL CENTRE, so the dilation radius must be r*g = h/2 - g/2, i.e.
    # r = upsample/2 - 0.5, which is an integer exactly when upsample is odd.
    r_exact = 0.5 * upsample - 0.5
    r = max(1, int(round(r_exact)))
    if abs(r - r_exact) > 1e-6:
        print("[render]   NOTE: upsample %d is not odd, dilation rounds %.2f -> %d "
              "cells, surface offset %+.4f m instead of %+.4f m"
              % (upsample, r_exact, r, (r + 0.5) * g, 0.5 * h))
    solid = binary_dilation(occ, structure=np.ones((2 * r + 1,) * 3, dtype=bool))
    vol = gaussian_filter(solid.astype(np.float32), sigma=sigma)

    verts, faces, _, _ = measure.marching_cubes(vol, level=level)
    V = verts * g + lo

    n_before = len(faces)
    if max_faces and len(faces) > max_faces:
        try:
            import trimesh
            m = trimesh.Trimesh(vertices=V, faces=faces, process=False)
            m = m.simplify_quadric_decimation(face_count=max_faces)
            V, faces = np.asarray(m.vertices), np.asarray(m.faces)
        except Exception as exc:                     # decimation is optional
            print("[render]   decimation skipped (%s: %s)"
                  % (type(exc).__name__, exc))
    return V, np.asarray(faces), n_before


def face_normals_outward(V, F):
    """Face normals oriented away from the body centroid. Marching-cubes winding
    follows the gradient sign, which flips on concavities; a car is close enough
    to star-shaped about its centroid for this to give consistent shading."""
    tri = V[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    fc = tri.mean(1)
    flip = np.einsum("ij,ij->i", n, fc - V.mean(0)) < 0.0
    n[flip] *= -1.0
    return n, tri


def base_colours(V, F):
    """Wheels darkened by geometry in the BODY frame, so it is pose-invariant.
    Adapted from t1_car.py:61-81, but z and y are taken relative to this mesh's
    own bounds instead of assuming the load_vehicle centring, because the body
    frame here comes from gates.py's pv derivation, not from the .ply."""
    fc = V[F].mean(1)
    zlo, zhi = V[:, 2].min(), V[:, 2].max()
    ylo, yhi = V[:, 1].min(), V[:, 1].max()
    height, length = zhi - zlo, yhi - ylo
    ymid = 0.5 * (ylo + yhi)
    # t1_car.py uses 0.30 of height, tuned for a Yaris mesh whose z origin is the
    # floor. Here zlo is the reconstructed surface bottom, and 0.30 painted black
    # wedges up to 0.85 m on the Yaris, well above any tire. 0.18 keeps it to the
    # wheels on all three hulls, which differ in height by a factor of 1.3.
    tires = ((fc[:, 2] - zlo) < 0.18 * height) & (np.abs(fc[:, 1] - ymid) > 0.28 * length)
    base = np.repeat(BODY[None, :], len(F), axis=0)
    base[tires] = TIRE
    return base, int(tires.sum())


def shade(base, n):
    sh = np.clip(n @ LIGHT, 0.0, 1.0) * 0.6 + 0.4   # dough_surface_render.py:79
    return np.clip(sh[:, None] * base, 0.0, 1.0)


def caption_lines(z, zmin, floor, caveat: str, sub_note: str) -> list[str]:
    """Every number here is read from this run's own summary.json / rollout.npz or
    measured from its own verified transform. Nothing is retyped and nothing is
    taken from another run's row."""
    s = z["summary"]
    rise = s["C2_veh_zmin_rise"]
    nf = len(zmin)
    l2 = ("%s hull, %.1f kg, n_grid %d, dx %.5f m, %d water layers, depth %.2f m, "
          "surge %.1f m/s, %d frames at %d fps"
          % (s["vehicle_key"], s["mass_kg"], s["n_grid"], s["dx"],
             s["water_layers"], s["depth_m"], s["velocity_ms"], nf, z["fps"]))
    l3 = ("final |disp| %.5f m   P-2 passthrough %.4f (%s, limit <0.10)   "
          "P-3 z-min rise %+.5f m (%s, limit |rise|<=0.01)"
          % (s["final_disp_mag_m"], s["passthrough_max_frac"],
             "PASS" if s["passthrough_max_frac"] < 0.10 else "FAIL",
             rise, "PASS" if abs(rise) <= 0.01 else "FAIL"))
    l4 = ("z-min above floor (3dx = %.5f m): frame 0 %+.1f mm, frame %d %+.1f mm, "
          "drop across the rendered frames %+.1f mm; deepest excursion below floor "
          "%+.4f mm. Gate C2 rise %+.1f mm is NOT this drop: C2 starts one solver "
          "step before frame 0 (sim_standing.py:445 vs the step at :448)."
          % (floor, (zmin[0] - floor) * 1e3, nf - 1, (zmin[-1] - floor) * 1e3,
             (zmin[-1] - zmin[0]) * 1e3, (zmin - floor).min() * 1e3, rise * 1e3))
    lines = [BANNER, l2, l3, l4]
    if caveat:
        lines.append(caveat)
    if sub_note:
        lines.append(sub_note)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--frames", default="all", help="'all' or a single frame index")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--max-water", type=int, default=0, help="0 = no subsample")
    ap.add_argument("--caveat", default="")
    ap.add_argument("--width", type=int, default=1800)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--elev", type=float, default=16.0)
    ap.add_argument("--azim", type=float, default=-62.0)
    ap.add_argument("--half", type=float, default=3.9, help="3D view half-width (m)")
    ap.add_argument("--slab-cells", type=float, default=3.0,
                    help="profile-slab half-width in grid cells")
    ap.add_argument("--vehicle-style", choices=("mesh", "points"), default="mesh")
    ap.add_argument("--upsample", type=int, default=3, help="odd values are exact")
    ap.add_argument("--sigma", type=float, default=1.0, help="smoothing, grid cells")
    ap.add_argument("--max-faces", type=int, default=9000)
    a = ap.parse_args()

    run = Path(a.run)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    z = load_run(run)
    pv, world, worst, errs = rigid_transform(z)
    print("[render] run            : %s" % run)
    print("[render] transform check: max|err| %.3e m" % worst)
    for f, e in sorted(errs.items()):
        print("[render]   frame %-3d      %.3e m" % (f, e))

    Vb = Fb = base = None
    surf_note = ""
    surf_meta = {"style": a.vehicle_style}
    if a.vehicle_style == "mesh":
        hpart = 0.5 * z["dx"]          # particle lattice spacing, h = dx/2
        Vb, Fb, n_raw = build_surface(pv, hpart, upsample=a.upsample,
                                      sigma=a.sigma, max_faces=a.max_faces)
        base, n_tire = base_colours(Vb, Fb)
        surf_meta.update({
            "particles": int(len(pv)), "lattice_h_m": hpart,
            "grid_spacing_m": hpart / a.upsample, "sigma_cells": a.sigma * a.upsample,
            "faces_raw": int(n_raw), "faces_drawn": int(len(Fb)),
            "vertices": int(len(Vb)), "tire_faces": n_tire,
        })
        print("[render] surface        : %d particles -> %d faces (%d before "
              "decimation), %d verts, %d wheel faces"
              % (len(pv), len(Fb), n_raw, len(Vb), n_tire))
        # A closed surface must enclose every particle it was built from.
        # The surface must ENCLOSE the particles it was built from. Erosion here
        # would lift the rendered underside off the floor, which is the one thing
        # these frames are read for, so it is measured, not assumed.
        outside = int(((pv < Vb.min(0) - 1e-9) | (pv > Vb.max(0) + 1e-9)).any(1).sum())
        mlo = (pv.min(0) - Vb.min(0))    # >0 means surface extends below particles
        mhi = (Vb.max(0) - pv.max(0))
        print("[render] surface bbox   : encloses %d/%d particles; margin lo "
              "[%+.4f %+.4f %+.4f] hi [%+.4f %+.4f %+.4f] m"
              % (len(pv) - outside, len(pv), mlo[0], mlo[1], mlo[2],
                 mhi[0], mhi[1], mhi[2]))
        if outside:
            print("[render] WARNING       : surface is ERODED, %d particles lie "
                  "outside its bbox" % outside)
        surf_meta["particles_outside_surface_bbox"] = outside
        surf_meta["bbox_margin_lo_m"] = [float(v) for v in mlo]
        surf_meta["bbox_margin_hi_m"] = [float(v) for v in mhi]
        surf_meta["bbox_margin_target_m"] = 0.5 * hpart
        # Quantitative faithfulness check: the enclosed volume must match the
        # solver's own solid_volume_m3, which is n_particles * h**3.
        try:
            import trimesh
            # Unsigned: marching-cubes winding follows the gradient, so trimesh's
            # signed volume comes out negative for this isosurface convention.
            mvol = abs(float(trimesh.Trimesh(vertices=Vb, faces=Fb,
                                             process=False).volume))
            sv = float(z["summary"]["solid_volume_m3"])
            print("[render] surface volume : %.6f m3 vs solver solid_volume_m3 "
                  "%.6f m3 (%+.2f %%); bbox margin target %.4f m"
                  % (mvol, sv, 100.0 * (mvol - sv) / sv, 0.5 * hpart))
            surf_meta["surface_volume_m3"] = mvol
            surf_meta["solver_solid_volume_m3"] = sv
            surf_meta["surface_volume_error_pct"] = 100.0 * (mvol - sv) / sv
        except Exception as exc:
            print("[render]   volume check skipped (%s)" % exc)
        surf_note = ("vehicle surface is a marching-cubes isosurface of the %d "
                     "SIMULATED rigid particles (lattice h = dx/2 = %.5f m, grid "
                     "%.5f m, %d faces). It is the body the solver integrated, not "
                     "the source .ply, so hull resolution loss is shown, not hidden."
                     % (len(pv), hpart, hpart / a.upsample, len(Fb)))

    water, speed = z["water"], z["speed"]
    nf = water.shape[0]
    floor, dx = z["floor"], z["dx"]

    zmin = np.array([world(f)[:, 2].min() for f in range(nf)])
    print("[render] veh z-min      : f0 %.6f  f%d %.6f  drop %+.6f m"
          % (zmin[0], nf - 1, zmin[-1], zmin[-1] - zmin[0]))
    print("[render] floor (3*dx)   : %.6f   min excursion below floor %+.6f m"
          % (floor, (zmin - floor).min()))

    smp = speed[::5].ravel()
    vlo, vhi = float(np.percentile(smp, 1.0)), float(np.percentile(smp, 99.0))
    if vhi <= vlo:
        vhi = vlo + 1e-6

    v0, vL = world(0), world(nf - 1)
    zhi = max(float(water[:, :, 2].max()), v0[:, 2].max(), vL[:, 2].max()) * 1.02
    zlo = floor - 0.10
    # Follow the hull: it translates downstream, so a fixed window would drift off.
    cx = 0.5 * (v0[:, 0].mean() + vL[:, 0].mean())
    cy = float(v0[:, 1].mean())
    ylo_p, yhi_p = v0[:, 1].min() - 1.6, v0[:, 1].max() + 1.6

    rng = np.random.default_rng(0)
    sub, sub_note = None, ""
    if a.max_water and a.max_water < water.shape[1]:
        sub = rng.choice(water.shape[1], size=a.max_water, replace=False)
        sub_note = ("water subsampled for display: %d of %d particles drawn"
                    % (a.max_water, water.shape[1]))

    cap = caption_lines(z, zmin, floor, a.caveat,
                        "; ".join(n for n in (surf_note, sub_note) if n))
    idx = list(range(0, nf, a.stride)) if a.frames == "all" else [int(a.frames)]
    slab = a.slab_cells * dx

    for f in idx:
        w, sp = water[f], speed[f]
        if sub is not None:
            w, sp = w[sub], sp[sub]
        vp = world(f)
        vx = float(vp[:, 0].mean())

        if Vb is not None:
            Vw = Vb @ z["R"][f].T + z["t"][f]
            nrm, tri = face_normals_outward(Vw, Fb)
            fcol = shade(base, nrm)
            # 2D panels look along -x from downstream. Plain painter's algorithm
            # over EVERY face, near drawn last. Back-face culling was tried first
            # and tore holes in the silhouette: faces near-tangent to the view have
            # an ill-conditioned normal, and the centroid-outward orientation fix
            # is unreliable inside the wheel arches. The projection of a closed
            # surface fills its own silhouette, so sorting without culling cannot
            # leave gaps.
            order = np.argsort(tri.mean(1)[:, 0])
            tri_yz = tri[:, :, 1:3][order]
            fcol_yz = fcol[order]

        fig = plt.figure(figsize=(a.width / a.dpi, a.height / a.dpi), dpi=a.dpi)
        gs = GridSpec(3, 2, figure=fig, width_ratios=[1.12, 1.0],
                      height_ratios=[1.0, 0.55, 0.62],
                      left=0.02, right=0.975, top=0.945, bottom=0.215,
                      wspace=0.13, hspace=0.55)

        # ---- oblique 3D, followed to the hull, data-proportional aspect -------
        ax = fig.add_subplot(gs[:, 0], projection="3d")
        keep = (np.abs(w[:, 0] - cx) < a.half) & (np.abs(w[:, 1] - cy) < a.half)
        ax.scatter(w[keep, 0], w[keep, 1], w[keep, 2], c=sp[keep], cmap="viridis",
                   vmin=vlo, vmax=vhi, s=1.6, alpha=0.24, linewidths=0,
                   depthshade=False, rasterized=True)
        if Vb is not None:
            pc = Poly3DCollection(tri, facecolors=fcol, edgecolors="none",
                                  linewidths=0, shade=False, zsort="max")
            pc.set_zorder(10)
            ax.add_collection3d(pc)
        else:
            ax.scatter(vp[:, 0], vp[:, 1], vp[:, 2], c=VEH_COLOR, s=2.6, alpha=0.95,
                       linewidths=0, depthshade=False, rasterized=True)
        ax.set_xlim(cx - a.half, cx + a.half)
        ax.set_ylim(cy - a.half, cy + a.half)
        ax.set_zlim(zlo, zhi)
        ax.set_box_aspect((1.0, 1.0, (zhi - zlo) / (2.0 * a.half)))
        ax.view_init(elev=a.elev, azim=a.azim)
        ax.set_xlabel("x, flow direction (m)", fontsize=8)
        ax.set_ylabel("y (m)", fontsize=8)
        ax.set_zlabel("z (m)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title("frame %03d / %d    t = %.3f s    (true aspect)"
                     % (f, nf - 1, f / z["fps"]), fontsize=10)

        # ---- car profile, (y, z), equal aspect --------------------------------
        ax2 = fig.add_subplot(gs[0, 1])
        m = np.abs(w[:, 0] - vx) < slab
        ax2.scatter(w[m, 1], w[m, 2], c=sp[m], cmap="viridis", vmin=vlo, vmax=vhi,
                    s=3.2, alpha=0.5, linewidths=0, rasterized=True)
        if Vb is not None:
            ax2.add_collection(PolyCollection(tri_yz, facecolors=fcol_yz,
                                              edgecolors="none", zorder=4,
                                              rasterized=True))
        else:
            ax2.scatter(vp[:, 1], vp[:, 2], c=VEH_COLOR, s=2.2, alpha=0.9,
                        linewidths=0, rasterized=True)
        ax2.axhline(floor, color=FLOOR_COLOR, lw=1.5, zorder=5)
        ax2.set_xlim(ylo_p, yhi_p)
        ax2.set_ylim(zlo, zhi)
        ax2.set_aspect("equal")
        ax2.set_xlabel("y, vehicle long axis (m)", fontsize=8)
        ax2.set_ylabel("z (m)", fontsize=8)
        ax2.tick_params(labelsize=7)
        ax2.set_title("car profile, water slab |x - x_veh| < %.2f m; "
                      "black line = floor" % slab, fontsize=9)

        # ---- magnified hull underside against the floor -----------------------
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.scatter(w[m, 1], w[m, 2], c=sp[m], cmap="viridis", vmin=vlo, vmax=vhi,
                    s=5.0, alpha=0.5, linewidths=0, rasterized=True)
        if Vb is not None:
            ax4.add_collection(PolyCollection(tri_yz, facecolors=fcol_yz,
                                              edgecolors="none", zorder=4,
                                              rasterized=True))
        else:
            ax4.scatter(vp[:, 1], vp[:, 2], c=VEH_COLOR, s=5.0, alpha=0.95,
                        linewidths=0, rasterized=True)
        ax4.axhline(floor, color=FLOOR_COLOR, lw=1.5, zorder=5)
        ax4.set_xlim(ylo_p, yhi_p)
        ax4.set_ylim(floor - 0.012, floor + 0.060)
        ax4.set_xlabel("y (m)", fontsize=8)
        ax4.set_ylabel("z (m)", fontsize=8)
        ax4.tick_params(labelsize=7)
        ax4.set_title("underside magnified: hull z-min is %+.1f mm above the floor"
                      % ((zmin[f] - floor) * 1e3), fontsize=9)

        # ---- z-min against the floor plane ------------------------------------
        ax3 = fig.add_subplot(gs[2, 1])
        ax3.plot(np.arange(nf), (zmin - floor) * 1e3, color=VEH_COLOR, lw=1.5)
        ax3.axhline(0.0, color=FLOOR_COLOR, lw=1.2)
        ax3.plot([f], [(zmin[f] - floor) * 1e3], "o", color="black", ms=5)
        ax3.set_xlim(0, nf - 1)
        ax3.set_xlabel("frame", fontsize=8)
        ax3.set_ylabel("z-min above floor (mm)", fontsize=8)
        ax3.tick_params(labelsize=7)
        ax3.grid(alpha=0.25, lw=0.5)
        ax3.set_title("z-min above floor: f0 %+.1f mm  ->  f%d %+.1f mm"
                      % ((zmin[0] - floor) * 1e3, nf - 1, (zmin[-1] - floor) * 1e3),
                      fontsize=9)

        for i, line in enumerate(cap):
            fig.text(0.02, 0.175 - i * 0.0295, line,
                     fontsize=9.0 if i == 0 else 7.5,
                     color="#8a1010" if i == 0 else "#222222",
                     weight="bold" if i == 0 else "normal", wrap=True)

        fig.savefig(out / ("frame_%04d.png" % f), dpi=a.dpi, facecolor="white")
        plt.close(fig)
        if f % 10 == 0 or f == idx[-1]:
            print("[render]   wrote frame_%04d.png" % f, flush=True)

    manifest = {
        "run": str(run),
        "outdir": str(out),
        "script": os.path.abspath(__file__),
        "frames_written": len(idx),
        "fps_from_npz": z["fps"],
        "transform_source": "gates.py:136 and gates.py:157, reused verbatim",
        "transform_max_reconstruction_error_m": worst,
        "transform_errors_by_frame_m": {str(k): v for k, v in errs.items()},
        "floor_plane_m": floor,
        "floor_definition": "3.0*dx, sim_standing.py:164",
        "veh_zmin_frame0_m": float(zmin[0]),
        "veh_zmin_final_m": float(zmin[-1]),
        "veh_zmin_drop_over_rendered_frames_m": float(zmin[-1] - zmin[0]),
        "veh_zmin_min_excursion_below_floor_m": float((zmin - floor).min()),
        "summary_C2_veh_zmin_start": z["summary"]["C2_veh_zmin_start"],
        "summary_C2_veh_zmin_rise": z["summary"]["C2_veh_zmin_rise"],
        "surface": surf_meta,
        "caption": cap,
    }
    (out / "render_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("[render] frames written : %d" % len(idx))
    print("[render] manifest       : %s" % (out / "render_manifest.json"))


if __name__ == "__main__":
    main()
