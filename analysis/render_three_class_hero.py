#!/usr/bin/env python3
"""Three-class hero still: Yaris, Rogue and Silverado on their REAL hulls.

SCOPE. Render layer only, and this file adds nothing to that boundary: it
IMPORTS the shading, free-surface and pose code rather than copying it, so every
verified property of those modules carries over unchanged. It reads three
existing rollouts and three existing .ply files and turns them into pixels. No
solver, no force, no gate, no verdict, no re-simulation. Engine for all three
runs is warpmpm, not Genesis.

WHY THIS EXISTS. The three converged hulls, the placement code and the
sediment-driven optics all exist and are individually verified, and nobody had
put them in one frame. The point of the frame is the one thing a table of
numbers hides: these three vehicles differ in DISPLACED VOLUME by 2.25x
(3.5427 / 4.9503 / 7.9621 m3) while their densities span only 285 to 317 kg/m3,
which is exactly the regime where a mass-only account of flood stability and a
geometry-aware one diverge (CLAUDE.md addendum A-3, after Smith, Modra and
Felder 2019; Martinez-Gomariz et al. 2017; Arrighi et al. 2015).

THE CONTROL THIS FIGURE DOES NOT HAVE, STATED FIRST BECAUSE IT IS THE THING
MOST LIKELY TO BE MISREAD. These three runs share n_grid = 64. Shared n_grid is
NOT shared resolution: `grid_lim` follows the loaded hull's extent, so dx comes
out 0.147215 / 0.163165 / 0.204186 m and the water resolves at 4 / 4 / 3 layers.
The panels are therefore comparable in PHYSICAL SETUP (0.30 m nominal depth,
1.5 m/s surge, same solver, same floor friction) and NOT comparable in numerical
resolution. Every panel prints its own dx and depth/dx so the difference cannot
be lost. A matched-dx set is a separate experiment and does not exist yet.

WHAT IS MEASURED AND WHAT IS DRAWN, kept apart as the rest of this repo does:
  MEASURED, straight from each run's rollout.npz and summary.json: particle
    positions, particle speeds, the rigid-body pose, the floor plane, dx, water
    layers, depth, surge, mass, passthrough, displacement, verdict.
  DRAWN, invented in the render layer for legibility: the free surface (a
    per-column max-z reconstruction, warpmpm carries no surface tracker), its
    optical shading (Schlick + Beer-Lambert + GGX against an HDRI), and the
    vehicle SURFACE, which here is the source hull registered to the simulated
    pose rather than the marching-cubes reconstruction of the rigid particles.

REGISTER E8 APPLIES TO EVERY OUTPUT OF THIS SCRIPT. The frames contain derived
NCAC/CCSA hull geometry. E8's operative rule is a DISTRIBUTION rule: do not
commit derived NCAC/CCSA geometry to the public repo and do not put it in a
DesignSafe DOI without a confirmed licence. E8 was re-checked from the source
zips on 2026-08-13 and is OPEN, not resolved: the zips carry a CCSA banner, a
warranty disclaimer and an attribution request, and NO redistribution grant. So
these stills are for internal review, and the script writes an E8 stamp into
both the figure and the manifest so an output cannot be published by accident.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_multigeom_rollout as RMR      # pose reconstruction, hull shading
import render_multigeom_shaded as RMS       # free surface, water shading, optics
import vehicle_mesh_transform as VMT        # .ply loading and registration

# The three converged, watertight, sha256-anchored hulls. Anchored BY DIGEST,
# never by path: the mesh pipeline is not bit-reproducible (the same effective
# arguments give a different sha256, and at g96 even a different face count,
# 72520 against 72524), so regenerating a hull to "verify" it proves nothing.
# The two files under vehicle_meshes/candidates/ are excluded on purpose: they
# are the two WORST hulls by volume convergence, 47.5 and 31.1 percent below
# converged, which would show a visibly wrong vehicle AND imply a wrong
# displaced volume, the very quantity this figure is about.
HULL_SHA256 = {
    "yaris": "b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95",
    "rogue": "c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2",
    "silverado": "46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9",
}
# Rogue and Silverado digests are the ones recorded in the run's own
# 00_provenance.txt, i.e. the hulls those runs actually loaded on Vista. The
# Yaris digest was measured on the in-repo file 2026-08-14; the multigeom
# provenance file predates the Yaris regression run and does not list it, but
# that run's log names the same path and reports hull_m3 3.542739 with
# hull_ref_delta_pct -5.9e-06, so it is the same hull to within 6e-06 percent.

AR_R_CLASS = {
    "yaris": "small_passenger",
    "rogue": "large_passenger",
    "silverado": "large_4wd",
}
# These are the classes the RUNS themselves recorded, read from each
# summary.json "label" field, not the ones a reader might expect. Note the Rogue
# runs as large_passenger here while the project's vehicle-class table calls the
# Rogue a midsize_suv; the run's own label is what is printed, because the mass
# it used (1609 kg) came from the AR&R large_passenger row.


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_case(run_dir, ply_path, max_faces, expect_key=None):
    """One vehicle: rollout + registered hull + every number the caption needs.

    Every value here is READ from the run, not retyped. The hull digest is
    measured on the file about to be read, then checked against the recorded
    digest, and a mismatch is fatal rather than a warning: a hero figure built
    on the wrong hull is exactly the failure this project keeps catching.
    """
    z = RMR.load_run(Path(run_dir))
    s = z["summary"]
    key = s["vehicle_key"]
    if expect_key and key != expect_key:
        raise SystemExit("run %s is vehicle %r, expected %r" % (run_dir, key, expect_key))

    digest = sha256_of(ply_path)
    want = HULL_SHA256.get(key)
    if want and digest != want:
        raise SystemExit(
            "hull digest mismatch for %s\n  file     %s\n  measured %s\n  expected %s\n"
            "Refusing to draw a hull that is not the recorded one."
            % (key, ply_path, digest, want))

    reg = VMT.load_and_register(str(ply_path), z, max_faces=max_faces)
    pv, world, worst, _ = RMR.rigid_transform(z)
    return {
        "key": key, "z": z, "reg": reg, "pv": pv, "world": world,
        "transform_err_m": float(worst), "hull_sha256": digest,
        "ply": str(ply_path), "run": str(run_dir),
    }


def panel(ax, case, frame, sky, sun, k_water, scatter_water, args, view):
    """Draw one vehicle into one 3D axes. Returns the numbers it drew with."""
    z, reg, world = case["z"], case["reg"], case["world"]
    water, speed = z["water"], z["speed"]
    floor, dx = z["floor"], z["dx"]
    hpart = 0.5 * dx
    Vb, Fb = reg["vertices_body"], reg["faces"]

    vp = world(frame)
    w, sp = water[frame], speed[frame]
    # Centre each panel on its OWN vehicle, with the SAME half-window for all
    # three, so the panels share a scale and the size difference is the signal.
    #
    # THEN CLAMP THE WINDOW INSIDE THE WATER BODY. The three domains differ in
    # size (grid_lim 9.422 / 10.443 / 13.068 m) and the upstream slab has already
    # advanced by the frame drawn, so a window centred on the vehicle can run off
    # the water and put a wedge of bare floor in the corner of the frame. That
    # wedge is REAL, it is the edge of the tank, but in a three-panel comparison
    # it reads as a rendering artefact and it differs per panel for a reason that
    # has nothing to do with the vehicle. The clamp only slides the window; it
    # never rescales it, so the shared scale bar stays valid and the panels stay
    # directly comparable. The shift applied is reported in the manifest.
    cx_veh, cy_veh = float(vp[:, 0].mean()), float(vp[:, 1].mean())
    cx, cy = cx_veh, cy_veh
    if args.clamp_to_water:
        for axis, c in ((0, cx_veh), (1, cy_veh)):
            lo, hi = float(w[:, axis].min()), float(w[:, axis].max())
            if hi - lo >= 2.0 * args.half:
                c = min(max(c, lo + args.half), hi - args.half)
            else:                        # water narrower than the window: centre it
                c = 0.5 * (lo + hi)
            if axis == 0:
                cx = c
            else:
                cy = c

    X, Y, Hh, S, wet = RMS.free_surface(w, sp, cx, cy, args.half, floor,
                                        args.surf_cell, hpart)
    wrgb, foam, We = RMS.shade_water(X, Y, Hh, S, floor, view, sky, sun,
                                     hpart, args.exposure,
                                     k_rgb=k_water, scatter_rgb=scatter_water)
    occ = RMS.hull_footprint_mask(vp, X, Y, args.surf_cell)
    wq, wc = RMS.surface_quads(X, Y, np.where(wet, Hh, np.nan), wrgb, occ | ~wet)

    Vw = Vb @ z["R"][frame].T + z["t"][frame]
    nrm, tri = RMR.face_normals_outward(Vw, Fb)
    base, n_tire = RMR.base_colours(Vb, Fb)
    fcol = RMR.shade(base, nrm)

    # D1, inherited: water quads and hull faces go into ONE collection so
    # matplotlib's painter's sort runs over all faces together. Ordering
    # BETWEEN artists is by artist order, not depth, which is what sliced the
    # car in half in the v1 renders. Valid only because the hull footprint is
    # cut out of the sheet above, so the two sets never interpenetrate.
    polys = wq + list(tri)
    pcol = np.vstack([wc, fcol]) if len(wq) else fcol
    ax.add_collection3d(Poly3DCollection(polys, facecolors=pcol, edgecolors="none",
                                         linewidths=0, shade=False, zsort="average"))

    zhi = floor + args.z_span
    ax.set_xlim(cx - args.half, cx + args.half)
    ax.set_ylim(cy - args.half, cy + args.half)
    ax.set_zlim(floor - 0.05, zhi)
    # zoom fills the axes box. A flat, wide scene inside matplotlib's cubic 3D
    # axes otherwise leaves a large empty band above and below the water, which
    # in a three-panel figure is most of the page.
    ax.set_box_aspect((1.0, 1.0, (zhi - floor + 0.05) / (2.0 * args.half)),
                      zoom=args.zoom)
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_axis_off()
    ax.set_facecolor("none")

    ext = vp.max(0) - vp.min(0)
    return {
        "frame": frame, "cx": cx, "cy": cy,
        "window_shift_from_vehicle_m": [cx - cx_veh, cy - cy_veh],
        "half_m": args.half,
        "foam_frac_wet": float(foam[wet].mean()) if wet.any() else 0.0,
        "We_p99_wet": float(np.nanpercentile(We[wet], 99.0)) if wet.any() else 0.0,
        "particle_extent_m": [float(v) for v in ext],
        "veh_zmin_above_floor_m": float(vp[:, 2].min() - floor),
    }


def scale_bar(ax, cx, cy, floor, half, length=2.0):
    """A metre scale drawn in the scene, so the panels stay quantitative with
    the axes off. Placed on the floor plane at the near edge of the window."""
    x0 = cx - 0.5 * length
    y = cy - 0.86 * half
    ax.plot([x0, x0 + length], [y, y], [floor, floor],
            color="0.15", lw=2.0, solid_capstyle="butt", zorder=1e6)
    ax.text(cx, y - 0.16 * half, floor, "%.0f m" % length,
            color="0.15", fontsize=7, ha="center", va="top", zorder=1e6)


def vehicle_caption(case, drew):
    """Per-panel caption. Every number read from this run's own files."""
    s = case["z"]["summary"]
    reg = case["reg"]
    key = s["vehicle_key"]
    dx = s["dx"]
    depth_over_dx = s["depth_m"] / dx
    p2 = s["passthrough_max_frac"]
    vol_hull = reg["volume_source_m3"]
    rho = s["mass_kg"] / s["solid_volume_m3"]
    lines = [
        "%s   AR&R %s" % (key.upper(), AR_R_CLASS.get(key, s.get("label", "?"))),
        "%.1f kg   hull %.4f m$^3$   solidified %.4f m$^3$   rho %.1f kg/m$^3$"
        % (s["mass_kg"], vol_hull, s["solid_volume_m3"], rho),
        "mass source: %s" % s["mass_source"],
        "n_grid %d   dx %.6f m   depth/dx %.3f   %d water layers"
        % (s["n_grid"], dx, depth_over_dx, s["water_layers"]),
        "hull sha256 %s...   %d of %d faces drawn (%s)   drawn volume %+.3f%%"
        % (case["hull_sha256"][:12], reg["n_faces"], reg["n_faces_source"],
           reg["decimation_backend"].split(" (")[0], reg["volume_delta_pct"]),
        "registered yaw %d deg   height-profile corr %+.4f   extent residual "
        "%.4f m = %.2f cells" % (reg["yaw_deg"], reg["profile_corr"],
                                 reg["residual_m"], reg["residual_cells"]),
        "final |disp| %.5f m   P-2 passthrough %.5f (%s, limit <0.10)   verdict "
        "NO-FORD" % (s["final_disp_mag_m"], p2, "PASS" if p2 < 0.10 else "FAIL"),
    ]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True,
                    help="directory holding g64_yaris_regression, g64_rogue and "
                         "g64_silverado")
    ap.add_argument("--yaris-ply", default="vehicle_geometry_research/"
                                           "yaris_coarse_v1l_watertight.ply")
    ap.add_argument("--rogue-ply", required=True)
    ap.add_argument("--silverado-ply", required=True)
    ap.add_argument("--hdri-cache", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--frame", type=int, default=45)
    ap.add_argument("--half", type=float, default=3.15)
    ap.add_argument("--z-span", type=float, default=2.05)
    ap.add_argument("--surf-cell", type=float, default=0.125)
    ap.add_argument("--exposure", type=float, default=0.80)
    ap.add_argument("--elev", type=float, default=30.0)
    ap.add_argument("--azim", type=float, default=-62.0)
    ap.add_argument("--zoom", type=float, default=1.42,
                    help="matplotlib 3D box zoom; fills the axes with the flat "
                         "wide scene instead of padding it")
    ap.add_argument("--max-faces", type=int, default=60000)
    ap.add_argument("--no-clamp-to-water", dest="clamp_to_water",
                    action="store_false",
                    help="draw the window centred on the vehicle even where it "
                         "runs off the edge of the water body")
    ap.set_defaults(clamp_to_water=True)
    ap.add_argument("--width", type=int, default=2400)
    ap.add_argument("--height", type=int, default=1240)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--ssc-preset", default="urban_road_flood",
                    choices=sorted(RMS.FWO.SSC_PRESET_MG_L))
    ap.add_argument("--tag", default="three_class_hero")
    a = ap.parse_args()

    root = Path(a.runs_root)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    sky, sun = RMS.load_hdri(Path(a.hdri_cache))
    ssc = RMS.FWO.preset_ssc(a.ssc_preset)
    k_water, scatter_water, optics_frag, optics_prov = RMS.optics_from_ssc(ssc)

    spec = [("yaris", root / "g64_yaris_regression", a.yaris_ply),
            ("rogue", root / "g64_rogue", a.rogue_ply),
            ("silverado", root / "g64_silverado", a.silverado_ply)]
    cases = []
    for key, run, ply in spec:
        c = load_case(run, ply, a.max_faces, expect_key=key)
        cases.append(c)
        r = c["reg"]
        print("[hero] %-10s sha %s  yaw %d  corr %+.4f  resid %.4f m (%.2f cells)  "
              "F %d->%d  vol %+.3f%%  transform max|err| %.2e m"
              % (key, c["hull_sha256"][:12], r["yaw_deg"], r["profile_corr"],
                 r["residual_m"], r["residual_cells"], r["n_faces_source"],
                 r["n_faces"], r["volume_delta_pct"], c["transform_err_m"]))

    nf = min(c["z"]["water"].shape[0] for c in cases)
    frame = min(a.frame, nf - 1)
    fps = cases[0]["z"]["fps"]
    print("[hero] frame %d of %d, t = %.3f s, optics: %s"
          % (frame, nf, frame / float(fps), optics_frag))

    el, az = np.radians(a.elev), np.radians(a.azim)
    view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])

    fig = plt.figure(figsize=(a.width / a.dpi, a.height / a.dpi), dpi=a.dpi)
    fig.patch.set_facecolor("white")
    drew = []
    for i, c in enumerate(cases):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.set_position([-0.010 + i * 0.3350, 0.395, 0.3520, 0.575])
        d = panel(ax, c, frame, sky, sun, k_water, scatter_water, a, view)
        scale_bar(ax, d["cx"], d["cy"], c["z"]["floor"], a.half)
        drew.append(d)
        cap = vehicle_caption(c, d)
        fig.text(0.014 + i * 0.3350, 0.372, cap[0], fontsize=10.5, weight="bold",
                 va="top", ha="left")
        fig.text(0.014 + i * 0.3350, 0.348, "\n".join(cap[1:]), fontsize=6.4,
                 va="top", ha="left", linespacing=1.62, family="DejaVu Sans")

    fig.text(0.5, 0.986,
             "Three AR&R vehicle classes on their real converged hulls, same "
             "flood condition, frame %d of %d (t = %.2f s)"
             % (frame, nf, frame / float(fps)),
             fontsize=13, ha="center", va="top", weight="bold")
    fig.text(0.5, 0.958,
             "0.30 m nominal still-water depth, 1.5 m/s surge, warpmpm MPM, "
             "floor friction 0.55.   Displaced volume spans 2.25x (3.5427 / "
             "4.9503 / 7.9621 m$^3$) while density spans only 285 to 317 "
             "kg/m$^3$.",
             fontsize=9, ha="center", va="top", color="0.25")

    honest = [
        RMS.BANNER,
        "SHARED n_grid IS NOT SHARED RESOLUTION. All three runs use n_grid 64, "
        "but grid_lim follows each hull's extent, so dx is 0.147215 / 0.163165 / "
        "0.204186 m and the water resolves at 4 / 4 / 3 layers. The panels are "
        "comparable in PHYSICAL SETUP and NOT in numerical resolution; a "
        "matched-dx set is a separate experiment that does not exist yet. Per "
        "CLAUDE.md L-3 the g64 baseline sits at depth/dx = 2.0 against a rule of "
        "thumb of ~10 per flow depth, so no arm here is a converged resolution.",
        "MEASURED (warpmpm, unmodified): particle positions and speeds, the "
        "rigid-body pose, the floor plane, and every number in the three panel "
        "captions, each read from that run's own rollout.npz and summary.json. "
        "The pose is reconstructed by the same code the gates use, max|err| "
        "%.1e m across the three runs."
        % max(c["transform_err_m"] for c in cases),
        "DRAWN (display only, invented in the render layer): the free surface is "
        "a per-column max-z of the water particles, Gaussian-smoothed as a 2D "
        "heightfield; warpmpm has no free-surface field, no air phase and no "
        "pressure field (register B7), so this is a reconstruction for drawing. "
        "Water optics are analytic Schlick + Beer-Lambert + GGX against "
        "assets/DaySkyHDRI002A_1K_HDR.exr, %s. These pixels are not a "
        "light-transport solution." % optics_frag,
        "VEHICLE SURFACE IS THE SOURCE HULL, not the simulated particle cloud. "
        "It is registered to the simulated pose by a yaw derived from the cloud "
        "itself and REFUSED if the extent residual exceeds 2 particle cells; all "
        "three land at 1.18 to 1.20 cells, the expected half-cell inflation of a "
        "surface over particle centres. It shows the geometry the solver was "
        "BUILT FROM, not the geometry it INTEGRATED. Per register E2 the solver "
        "samples the mesh to 60,000 surface points before solidifying, so "
        "watertightness does not propagate into the simulation.",
        "REGISTER E8: these frames contain derived NCAC/CCSA hull geometry and "
        "MUST NOT be committed to the public repo or included in a DesignSafe "
        "DOI. E8 was re-checked from the source zips on 2026-08-13 and is OPEN: "
        "the zips carry a CCSA banner and an attribution request and NO "
        "redistribution grant.",
    ]
    fig.text(0.012, 0.196, honest[0], fontsize=8.5, weight="bold", color="#8b1a1a",
             va="top", ha="left")
    fig.text(0.012, 0.174, "\n".join(honest[1:]), fontsize=6.3, va="top",
             ha="left", linespacing=1.6, wrap=True)

    stem = "%s_f%04d" % (a.tag, frame)
    png = out / (stem + ".png")
    fig.savefig(png, dpi=a.dpi, facecolor="white")
    plt.close(fig)
    print("[hero] wrote %s" % png)

    manifest = {
        "figure": str(png),
        "generated_by": "analysis/render_three_class_hero.py",
        "engine": "warpmpm (NOT Genesis); render layer reads solver output only",
        "canonical_status": "NON-CANONICAL companion experiment, not part of the "
                            "17-run gated inventory",
        "frame": frame, "n_frames": int(nf), "fps": int(fps),
        "t_seconds": frame / float(fps),
        "resolution_control": {
            "held_fixed": ["nominal depth 0.30 m", "surge 1.5 m/s",
                           "n_grid 64", "floor friction 0.55", "solver",
                           "frame index"],
            "NOT_held_fixed": ["dx", "realized water layers", "grid_lim"],
            "dx_m": {c["key"]: c["z"]["summary"]["dx"] for c in cases},
            "water_layers": {c["key"]: c["z"]["summary"]["water_layers"]
                             for c in cases},
            "warning": "Shared n_grid is not shared resolution. Do not average "
                       "or rank these three on any resolution-sensitive "
                       "quantity.",
        },
        "optics": optics_prov,
        "ssc_preset": a.ssc_preset,
        "ssc_mg_per_l": ssc,
        "camera": {"elev": a.elev, "azim": a.azim, "half_m": a.half,
                   "z_span_m": a.z_span, "exposure": a.exposure},
        "vehicles": [],
        "E8": "Derived NCAC/CCSA geometry. DO NOT publish this figure or commit "
              "it to the public repo. Register E8 is OPEN as of 2026-08-13.",
    }
    for c, d in zip(cases, drew):
        s = c["z"]["summary"]
        r = c["reg"]
        manifest["vehicles"].append({
            "key": c["key"], "ar_r_class_from_run_label": s.get("label"),
            "run": c["run"], "hull_ply": c["ply"], "hull_sha256": c["hull_sha256"],
            "mass_kg": s["mass_kg"], "mass_source": s["mass_source"],
            "hull_volume_m3": r["volume_source_m3"],
            "drawn_volume_m3": r["volume_drawn_m3"],
            "drawn_volume_delta_pct": r["volume_delta_pct"],
            "decimation_backend": r["decimation_backend"],
            "faces_source": r["n_faces_source"], "faces_drawn": r["n_faces"],
            "solid_volume_m3": s["solid_volume_m3"],
            "realized_rho_kg_m3": s["mass_kg"] / s["solid_volume_m3"],
            "n_grid": s["n_grid"], "dx_m": s["dx"],
            "depth_over_dx": s["depth_m"] / s["dx"],
            "water_layers": s["water_layers"],
            "registration": {"yaw_deg": r["yaw_deg"],
                             "height_profile_corr": r["profile_corr"],
                             "extent_residual_m": r["residual_m"],
                             "extent_residual_cells": r["residual_cells"]},
            "pose_transform_max_err_m": c["transform_err_m"],
            "final_disp_mag_m": s["final_disp_mag_m"],
            "passthrough_max_frac": s["passthrough_max_frac"],
            "P2_pass": bool(s["passthrough_max_frac"] < 0.10),
            "drawn": d,
        })
    mpath = out / (stem + "_manifest.json")
    mpath.write_text(json.dumps(manifest, indent=2) + "\n")
    print("[hero] wrote %s" % mpath)


if __name__ == "__main__":
    main()
