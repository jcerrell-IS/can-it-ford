#!/usr/bin/env python3
"""Shaded-water re-render of the NON-CANONICAL multigeom Rogue / Silverado runs.

Written 2026-08-12. Companion to analysis/render_multigeom_rollout.py, which it
IMPORTS rather than copies: load_run(), rigid_transform(), build_surface(),
base_colours() and face_normals_outward() are reused verbatim so the verified
gates.py:136/:157 pose reconstruction and the surface-enclosure checks carry over
unchanged. Nothing about the physics, the gates or the verdicts is touched here.

WHAT IS PHYSICS AND WHAT IS DISPLAY, because this repo cares about the difference
=================================================================================
PHYSICS (from the solver, unmodified):
  particle positions, particle speeds, the rigid-body pose, the floor plane,
  every number in the caption panel. All read from this run's own rollout.npz
  and summary.json.

DISPLAY ONLY (invented here, in this file, for legibility):
  the water free surface, its optical shading, and the foam.

  - The free surface is a per-column MAX-Z of the water particles. warpmpm carries
    no free-surface field and no surface tracker, so this is a reconstruction for
    drawing, not a simulated interface.
  - Refraction, reflection and specular highlights are an analytic shading model
    (Schlick Fresnel, Beer-Lambert absorption, GGX specular) evaluated against the
    HDRI environment. warpmpm computes NO optics of any kind. These pixels are not
    a light-transport solution and must never be described as one.
  - FOAM IS A POST-HOC DIAGNOSTIC. There is no air phase, no air-entrainment model
    and no surface tension anywhere in warpmpm (register B7 records there is not
    even a pressure field). Foam is computed here from a WEBER NUMBER criterion,
    We = rho |v_rel|^2 L / sigma, following the standard unified spray/foam/bubble
    model of Ihmsen, Akinci, Akinci and Teschner 2012, which spawns secondary
    particles on a Weber/energy criterion. It marks where whitewater would
    plausibly form; the solver did not form any.

VERSION 2, 2026-08-12, after auditing the v1 output frame by frame. FIVE DEFECTS
were found in v1 and are fixed here. Recorded because two of them MISREPRESENTED
THE DATA, which is worse than an ugly frame:
  D1 SEVERE. The vehicle was SLICED IN HALF by the water sheet. matplotlib
     composites BETWEEN artists by artist order, not by per-face depth, so water
     quads lying behind the car were painted over it. Fixed by merging the water
     quads and the hull faces into ONE Poly3DCollection, so matplotlib's painter's
     sort runs over all faces together. Legitimate here only because the hull
     footprint is cut out of the sheet, so the two never interpenetrate.
  D2 SEVERE. v1 drew WATER WHERE THERE IS NO WATER: empty columns were filled with
     the floor height (`np.where(mask, Hh, floor)`), so the sheet spanned the whole
     window including dry ground. Fixed: dry columns are dropped entirely.
  D3 SEVERE. v1's foam was normalised by the CURRENT FRAME's 88th percentile of
     steepness. Self-normalising, so it produced foam at t=0 on still water and
     looked identical at t=2.33 s. It was an unfalsifiable decoration. Replaced by
     the Weber-number criterion above, with a FIXED physical scale.
  D4 v1 smoothed with an arbitrary sigma of 1 cell. The LENGTH SCALE is now taken
     from the splashsurf guidance (Loschner, Bender et al. 2023), ~2.0x particle
     radius. READ THE NEXT PARAGRAPH BEFORE CITING THIS AS A SPLASHSURF METHOD.
  D5 The right-edge "shelf" that read as a solid ramp was a consequence of D2.
Source for D3 and D4: research report b0d2664f Part 3 items 13 and 15, on disk at
~/Downloads/compass_artifact_wf-b0d2664f-*.md. That report is T2 and its Ihmsen and
Loschner citations have NOT been checked against a primary record here.

WHAT IS AND IS NOT BORROWED FROM SPLASHSURF. Corrected 2026-08-13, because the
earlier wording invited the reading that this is a splashsurf reconstruction.
It is not. splashsurf runs marching cubes over a 3D SPH DENSITY FIELD and then
applies weighted Laplacian MESH smoothing. free_surface() at :242 bins particles
into (x,y) columns, takes a per-column max-z, and Gaussian-blurs the resulting
2D HEIGHTFIELD. Those are different objects, and swapping one for the other is a
rewrite, not a drop-in. ONLY THE LENGTH SCALE IS BORROWED, by analogy.

The numeric value is nonetheless correctly derived, and here is the derivation so
it can be audited instead of trusted. Every rollout .npz stores BOTH `dx` and `h`,
and `h` is the particle SPACING: verified 2026-08-13 across g64_rogue, g64_silverado
and g64_m1100, where h/dx = 0.500000 exactly, and the frame caption prints
"h = dx/2". A splashsurf particle RADIUS is half the spacing, so radius = h/2, and
2.0 x radius = h. `hpart = 0.5*dx = h` is what :473 passes, so the cited 2.0x IS
what the code applies, on nominal spacing.

Three caveats that a reader is entitled to, none of which the number alone shows:
  (a) A Gaussian sigma is not an SPH kernel support radius. Equating them is an
      approximation of convenience; splashsurf's smoothing length is not a sigma.
  (b) Measured, the water is denser than nominal. Median nearest-neighbour
      distance at frame 0 is 0.816 to 0.820 x h (0.0669 m rogue, 0.0837 m
      silverado, 0.0601 m yaris), because the water compacts during the settle
      phase. Against MEASURED spacing the applied smoothing is 1.22x the
      2x-radius target, not 1.00x. That is inside the 1.4-1.6x latitude b0d2664f
      item 13 itself quotes for the related particle-radius parameter, so it is
      recorded, not treated as a defect.
  (c) The max(0.6, .) floor at :276 binds for exactly one geometry at the default
      --surf-cell 0.125: yaris 0.5889 -> 0.60, a +1.9 percent effect. Rogue
      (0.6527) and silverado (0.8168), the two this script actually renders, are
      unclamped.

Register B7: no pressure field exists in warpmpm. Register A3: no force accessor
exists on this path. Neither is used or implied here.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_multigeom_rollout as RMR          # proven transform + surface code
import flood_water_optics as FWO                # SSC -> beam attenuation, see :87

BANNER = ("NON-CANONICAL COMPANION EXPERIMENT   not part of the 17-run gated "
          "inventory   (class_specific and hullsweep batches kept distinct)")

# Water optical constants.
F0_WATER = 0.0204          # Schlick F0 for air->water, ((1.333-1)/(1.333+1))**2
IOR = 1.333
# Beer-Lambert extinction, 1/m, red absorbed hardest. TWO MUTUALLY EXCLUSIVE
# MODES, selected by --ssc-mg-l.
#
#   LEGACY (--ssc-mg-l < 0, the default). Clear-water absorption multiplied by
#     VIS_GAIN so the depth cue reads on screen. Real clear-water values are
#     about (0.45, 0.07, 0.03) 1/m, which over a 0.30 m tank is a ~13% red loss
#     and is invisible; the gain makes it visible. A display choice, stated in
#     the caption, not a measurement. Effective k = (4.05, 0.63, 0.27) 1/m.
#
#   TURBID (--ssc-mg-l >= 0). k = clear-water absorption + sediment beam
#     attenuation at the given suspended-sediment concentration, and the
#     in-water tint comes from the same concentration. VIS_GAIN IS NOT APPLIED.
#     Multiplying a sourced coefficient by an unsourced 9x would be less
#     defensible than either alone, so the modes are exclusive by construction.
#
# NEITHER MODE IS A MEASUREMENT OF THIS SCENE. There is no site, no water sample
# and no measured SSC for these runs. The preset is a SCENARIO CHOICE, and the
# caption and manifest say so in both modes.
SIGMA_RGB = np.array([0.45, 0.07, 0.03], dtype=np.float32)
VIS_GAIN = 9.0
BOTTOM_RGB = np.array([0.050, 0.050, 0.050], dtype=np.float32)   # wet asphalt
SCATTER_RGB = np.array([0.020, 0.160, 0.200], dtype=np.float32)  # in-water tint


def optics_from_ssc(ssc_mg_l):
    """-> (k_rgb 1/m, scatter_rgb, caption_fragment, provenance dict).

    ssc < 0 or None selects legacy mode. FWO reproduces SIGMA_RGB and
    SCATTER_RGB exactly at SSC = 0, so the turbid branch is a strict
    generalisation of the legacy one rather than a competing model.
    """
    if ssc_mg_l is None or ssc_mg_l < 0.0:
        return (SIGMA_RGB * VIS_GAIN), SCATTER_RGB, (
            "absorption exaggerated %.0fx (CLEAR-water sigma, display choice, "
            "no sediment modelled)" % VIS_GAIN), {
            "mode": "legacy_exaggerated_clear_water",
            "sigma_rgb_1_per_m": SIGMA_RGB.tolist(),
            "vis_gain": VIS_GAIN,
            "effective_k_1_per_m": (SIGMA_RGB * VIS_GAIN).tolist(),
            "STATUS": "DISPLAY ONLY, hand-tuned exaggeration, not a measurement",
        }
    ssc = float(ssc_mg_l)
    k = np.asarray(FWO.extinction_coefficient_rgb(ssc, warn=False), dtype=np.float32)
    tint = np.asarray(FWO.scatter_albedo_rgb(ssc), dtype=np.float32)
    extrapolated = ssc > FWO.LINEAR_REGIME_MAX_SSC_MG_L
    frag = ("turbid water at SSC %g mg/L, beam attenuation k = (%.1f, %.1f, %.1f) "
            "1/m, black-disc visual range %.2f m, NO display exaggeration"
            % (ssc, k[0], k[1], k[2], FWO.visual_range_m(ssc)))
    if extrapolated:
        frag += "; k EXTRAPOLATED above the %.0f mg/L linear bound" % \
            FWO.LINEAR_REGIME_MAX_SSC_MG_L
    prov = {
        "mode": "turbid_ssc_driven",
        "ssc_mg_l": ssc,
        "ssc_is": "ASSUMED SCENARIO INPUT, not measured for this run",
        "effective_k_1_per_m": k.tolist(),
        "in_water_scatter_rgb": tint.tolist(),
        "black_disc_visual_range_m": float(FWO.visual_range_m(ssc)),
        "vis_gain_applied": False,
        "extrapolated_beyond_linear_regime": bool(extrapolated),
        "NOT_DERIVED": (
            "c* = %.3f m2/g is a central value from a %.3f to %.3f m2/g band "
            "bounded by clarity relationships and geometric-optics scattering; "
            "the point within the band is a choice, and grain size, the dominant "
            "control, is not modelled. The scatter RGB is a chosen colour "
            "consistent with iron-oxide spectral behaviour, not a colorimetric "
            "conversion." % ((FWO.SEDIMENT_CSTAR_M2_PER_G,)
                             + FWO.SEDIMENT_CSTAR_BAND_M2_PER_G)),
    }
    prov.update({"references": FWO.REFERENCES})
    return k, tint, frag, prov

# Weber-number foam criterion (Ihmsen et al. 2012). ABSOLUTE physical scale, which
# is the whole point: unlike v1's per-frame percentile, still water returns zero.
RHO_W = 1000.0            # kg/m3
SIGMA_W = 0.0728          # N/m, air-water surface tension at 20 C
WE_LO, WE_HI = 8.0, 60.0  # onset and saturation. The classic critical Weber for
                          # droplet breakup is O(10); the band is stated rather
                          # than tuned per frame, and the MEASURED We range is
                          # printed and written to the manifest so it is auditable.


def load_hdri(cache_dir: Path):
    """Load the cached equirect HDRI and its sun direction.

    assets/DaySkyHDRI002A_1K_HDR.exr is READ, never regenerated. It is decoded
    once to .npy because no EXR backend is installed in the render venv; the
    decode step is a read of the asset, not a rewrite of it.
    """
    sky = np.load(cache_dir / "hdri_sky.npy").astype(np.float32)
    sun = np.load(cache_dir / "hdri_sun.npy").astype(np.float32)
    return sky, sun / (np.linalg.norm(sun) + 1e-12)


def sample_env(sky, d):
    """Equirectangular lookup. d is (...,3), unit, z up. v=0 is +z (zenith)."""
    x, y, z = d[..., 0], d[..., 1], d[..., 2]
    pol = np.arccos(np.clip(z, -1.0, 1.0))
    az = np.arctan2(y, x)
    H, W, _ = sky.shape
    i = np.clip(((az / (2 * np.pi) + 0.5) * W).astype(np.int32), 0, W - 1)
    j = np.clip(((pol / np.pi) * H).astype(np.int32), 0, H - 1)
    return sky[j, i]


def surface_quads(X, Y, Hh, rgb, drop):
    """Heightfield -> (list of 4x3 quads, Nx3 colours), skipping dropped cells.

    D1 FIX. These quads are handed to the SAME Poly3DCollection as the hull faces
    so matplotlib's painter's sort runs over water and vehicle together. In v1 the
    water was a separate plot_surface artist, and matplotlib orders BETWEEN artists
    by artist order rather than by depth, so water behind the car was painted over
    it and the hull came out sliced in half. Merging is valid here only because the
    hull footprint is cut out of the sheet, so no water quad intersects a hull face.

    D2 FIX. `drop` carries dry columns as well as the hull footprint, so a quad is
    emitted only where water actually exists. v1 filled dry columns with the floor
    height and drew a sheet across the entire window, including dry ground.
    """
    nx, ny = Hh.shape
    ok = np.isfinite(Hh) & ~drop
    q = ok[:-1, :-1] & ok[1:, :-1] & ok[1:, 1:] & ok[:-1, 1:]
    ii, jj = np.nonzero(q)
    if ii.size == 0:
        return [], np.zeros((0, 3))
    c00 = np.stack([X[ii, jj], Y[ii, jj], Hh[ii, jj]], axis=1)
    c10 = np.stack([X[ii + 1, jj], Y[ii + 1, jj], Hh[ii + 1, jj]], axis=1)
    c11 = np.stack([X[ii + 1, jj + 1], Y[ii + 1, jj + 1], Hh[ii + 1, jj + 1]], axis=1)
    c01 = np.stack([X[ii, jj + 1], Y[ii, jj + 1], Hh[ii, jj + 1]], axis=1)
    quads = np.stack([c00, c10, c11, c01], axis=1)          # (nq,4,3)
    return list(quads), rgb[ii, jj]


def hull_footprint_mask(vp, X, Y, cell, pad_cells=1):
    """Cells whose (x,y) column is occupied by the hull.

    The free surface is CUT OUT there, for two reasons that agree. Physically the
    vehicle displaces the water, so a surface spanning the hull footprint is
    wrong. Practically, matplotlib's 3D painter's algorithm does not honour zorder
    between a plot_surface and a Poly3DCollection, so an uncut sheet draws over
    the hull and hides the one thing these frames are read for.
    """
    from scipy.ndimage import binary_dilation
    nx, ny = X.shape
    x0, y0 = X[0, 0], Y[0, 0]
    ix = np.clip(np.rint((vp[:, 0] - x0) / cell).astype(np.int64), 0, nx - 1)
    iy = np.clip(np.rint((vp[:, 1] - y0) / cell).astype(np.int64), 0, ny - 1)
    occ = np.zeros((nx, ny), dtype=bool)
    occ[ix, iy] = True
    if pad_cells > 0:
        occ = binary_dilation(occ, np.ones((2 * pad_cells + 1,) * 2, dtype=bool))
    return occ


def free_surface(w, sp, cx, cy, half, floor, cell, smooth_len_m):
    """Per-column max-z of the water particles -> (X, Y, Hh, S, wet).

    DISPLAY ONLY. warpmpm has no free-surface field; this is a reconstruction.
    Empty columns are marked and later filled from the neighbourhood so the sheet
    stays continuous rather than sprouting holes where the sampling is thin.
    """
    x0, x1 = cx - half, cx + half
    y0, y1 = cy - half, cy + half
    nx = max(8, int(np.ceil((x1 - x0) / cell)))
    ny = max(8, int(np.ceil((y1 - y0) / cell)))

    ix = np.clip(((w[:, 0] - x0) / (x1 - x0) * nx).astype(np.int64), 0, nx - 1)
    iy = np.clip(((w[:, 1] - y0) / (y1 - y0) * ny).astype(np.int64), 0, ny - 1)
    inside = (w[:, 0] >= x0) & (w[:, 0] < x1) & (w[:, 1] >= y0) & (w[:, 1] < y1)
    ix, iy = ix[inside], iy[inside]
    zz, ss = w[inside, 2], sp[inside]

    flat = ix * ny + iy
    Hh = np.full(nx * ny, -np.inf, dtype=np.float64)
    np.maximum.at(Hh, flat, zz)
    # speed of the surface-most particle, approximated by the per-column max-speed
    S = np.zeros(nx * ny, dtype=np.float64)
    np.maximum.at(S, flat, ss)
    Hh = Hh.reshape(nx, ny)
    S = S.reshape(nx, ny)
    wet = np.isfinite(Hh)          # D2: this is the ONLY place water exists

    from scipy.ndimage import gaussian_filter
    # D4. Smoothing LENGTH SCALE borrowed from the splashsurf guidance (Loschner,
    # Bender et al. 2023, via research report b0d2664f item 13): ~2.0x the particle
    # radius, not the arbitrary 1 cell v1 used. The .npz stores h as the particle
    # SPACING (h/dx = 0.5 exactly in every run), so the radius is h/2 and
    # 2.0*(h/2) = h metres, expressed here in cells. Smoothing is what turns a
    # particle staircase into a sheet that can carry a surface normal at all.
    #
    # THIS IS NOT A SPLASHSURF RECONSTRUCTION. splashsurf marching-cubes an SPH
    # density field in 3D; this Gaussian-blurs a 2D column-max heightfield, and a
    # Gaussian sigma is not an SPH kernel support radius. Only the length is
    # borrowed. See the module docstring for the measured 1.22x against ACTUAL
    # (post-settle, compacted) spacing and for which geometry the floor below
    # binds.
    sig_cells = max(0.6, smooth_len_m / cell)
    # NORMALISED convolution: smooth only over wet cells and divide by the smoothed
    # indicator, so dry ground never leaks into the surface height. A plain
    # gaussian over a floor-filled array is what produced D2's phantom sheet.
    ind = wet.astype(np.float64)
    Hz = np.where(wet, Hh, 0.0)
    Sz = np.where(wet, S, 0.0)
    ind_s = gaussian_filter(ind, sigma=sig_cells)
    with np.errstate(invalid="ignore", divide="ignore"):
        Hh = np.where(ind_s > 1e-6, gaussian_filter(Hz, sigma=sig_cells) / ind_s, np.nan)
        S = np.where(ind_s > 1e-6, gaussian_filter(Sz, sigma=sig_cells) / ind_s, 0.0)
    # D2: a cell is water only if it actually held particles. Smoothing may not
    # invent wet area. Keep the ORIGINAL occupancy as the authority.
    Hh = np.where(wet, Hh, np.nan)

    xs = x0 + (np.arange(nx) + 0.5) * (x1 - x0) / nx
    ys = y0 + (np.arange(ny) + 0.5) * (y1 - y0) / ny
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    return X, Y, Hh, S, wet


def shade_water(X, Y, Hh, S, floor, view, sky, sun, h_particle, exposure,
                k_rgb=None, scatter_rgb=None):
    """Analytic water shading. DISPLAY ONLY, see the module docstring.

    Returns (rgb, foam, We) with rgb already tone-mapped and gamma-encoded.
    Hh may carry NaN in dry columns (D2); gradients are taken on a NaN-filled
    copy and the caller drops the dry quads, so no colour is invented there.
    """
    # Legacy defaults preserved, so an unparameterised call behaves as before.
    k_rgb = (SIGMA_RGB * VIS_GAIN) if k_rgb is None else np.asarray(k_rgb, np.float32)
    scatter_rgb = SCATTER_RGB if scatter_rgb is None else \
        np.asarray(scatter_rgb, np.float32)

    dry = ~np.isfinite(Hh)
    Hf = np.where(dry, np.nanmedian(Hh) if np.isfinite(Hh).any() else floor, Hh)
    gx = np.gradient(Hf, X[1, 0] - X[0, 0], axis=0)
    gy = np.gradient(Hf, Y[0, 1] - Y[0, 0], axis=1)
    Hh = Hf
    n = np.stack([-gx, -gy, np.ones_like(Hh)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12

    v = view / (np.linalg.norm(view) + 1e-12)
    ndotv = np.clip(np.einsum("ijk,k->ij", n, v), 1e-4, 1.0)

    # ---- Fresnel (Schlick) ------------------------------------------------
    F = F0_WATER + (1.0 - F0_WATER) * (1.0 - ndotv) ** 5

    # ---- reflection: sample the HDRI along the mirror direction -----------
    r = 2.0 * ndotv[..., None] * n - v[None, None, :]
    r /= np.linalg.norm(r, axis=-1, keepdims=True) + 1e-12
    refl = sample_env(sky, r)

    # ---- refraction: Snell, then Beer-Lambert over the path in water ------
    eta = 1.0 / IOR
    k = 1.0 - eta * eta * (1.0 - ndotv * ndotv)
    cos_t = np.sqrt(np.clip(k, 1e-4, 1.0))
    depth = np.clip(Hh - floor, 0.0, None)
    path = depth / np.clip(cos_t, 0.2, 1.0)
    trans = np.exp(-k_rgb[None, None, :] * path[..., None])
    refr = BOTTOM_RGB[None, None, :] * trans + scatter_rgb[None, None, :] * (1.0 - trans)

    # ---- foam: WEBER-NUMBER criterion, Ihmsen et al. 2012 (D3 fix) ---------
    # We = rho |v_rel|^2 L / sigma. Inertia over surface tension: above a critical
    # We the surface breaks up and entrains air. Ihmsen, Akinci, Akinci and
    # Teschner 2012 spawn secondary spray/foam/bubble particles on exactly this
    # criterion, and it is the standard model (research report b0d2664f item 15).
    #
    # THIS IS THE FIX FOR v1's WORST METHODOLOGICAL DEFECT. v1 normalised surface
    # steepness by the CURRENT FRAME's 88th percentile, so some cell was always at
    # full foam no matter how still the water was: it produced foam at t=0 on a
    # flat surface. A Weber number is an ABSOLUTE scale. If the flow is too gentle
    # to entrain air, this returns zero foam, and that is the correct answer.
    #
    # v_rel is the local departure of the speed field from its neighbourhood mean,
    # the discrete analogue of Ihmsen's neighbour velocity difference. L is the
    # particle spacing h. Units: kg/m3 * (m/s)^2 * m / (N/m) = dimensionless. OK.
    from scipy.ndimage import gaussian_filter as _gf
    v_rel = np.abs(S - _gf(S, sigma=2.0))
    We = RHO_W * v_rel ** 2 * h_particle / SIGMA_W
    foam = np.clip((We - WE_LO) / (WE_HI - WE_LO), 0.0, 1.0) ** 0.9

    # ---- specular: GGX against the HDRI sun, roughened by foam ------------
    l = sun
    h = l[None, None, :] + v[None, None, :]
    h /= np.linalg.norm(h, axis=-1, keepdims=True) + 1e-12
    ndoth = np.clip(np.einsum("ijk,ijk->ij", n, h), 0.0, 1.0)
    rough = 0.055 + 0.55 * foam            # foam scatters, so it kills the glint
    a2 = np.clip(rough * rough, 1e-5, 1.0) ** 2
    D = a2 / (np.pi * ((ndoth * ndoth) * (a2 - 1.0) + 1.0) ** 2)
    spec = (F * D * 0.030)[..., None] * np.array([1.0, 0.98, 0.94], dtype=np.float32)

    rgb = refr * (1.0 - F[..., None]) + refl * F[..., None] + spec
    rgb = rgb * (1.0 - 0.78 * foam[..., None]) + 0.78 * foam[..., None] * np.array(
        [0.93, 0.955, 0.97], dtype=np.float32)

    rgb = rgb * exposure
    rgb = rgb / (1.0 + rgb)                       # Reinhard tone map
    rgb = np.clip(rgb, 0.0, 1.0) ** (1.0 / 2.2)   # gamma
    return rgb, foam, We


def caption_lines(z, zmin, floor, extra: str, optics_frag: str = None) -> list[str]:
    """Numbers from this run's OWN summary.json / rollout.npz. Nothing retyped."""
    s = z["summary"]
    rise = s["C2_veh_zmin_rise"]
    nf = len(zmin)
    p2, p3 = s["passthrough_max_frac"], abs(rise) <= 0.01
    l2 = ("%s hull, %.1f kg, n_grid %d, dx %.5f m, %d water layers, depth %.2f m, "
          "surge %.1f m/s, %d frames at %d fps"
          % (s["vehicle_key"], s["mass_kg"], s["n_grid"], s["dx"], s["water_layers"],
             s["depth_m"], s["velocity_ms"], nf, z["fps"]))
    l3 = ("final |disp| %.5f m   P-2 passthrough %.4f (%s, limit <0.10)   "
          "P-3 z-min rise %+.5f m (%s, limit |rise|<=0.01)   verdict NO-FORD"
          % (s["final_disp_mag_m"], p2, "PASS" if p2 < 0.10 else "FAIL",
             rise, "PASS" if p3 else "FAIL"))
    lines = [BANNER, l2, l3]
    if not p3:
        lines.append(
            "P-3 FAIL RECURS. Measured from the verified transform: hull z-min "
            "starts %+.1f mm above the floor plane and reaches it, deepest excursion "
            "BELOW the floor is %+.4f mm. The hull SETTLED ONTO the floor plane, it "
            "did not penetrate it. Displacement from a P-3 FAIL run is not citable."
            % ((zmin[0] - floor) * 1e3, (zmin - floor).min() * 1e3))
    lines.append(
        "Gate C2 rise %+.1f mm is NOT the drop drawn here (%+.1f mm): C2 starts one "
        "solver step before frame 0 (sim_standing.py:445 vs the step at :448)."
        % (rise * 1e3, (zmin[-1] - zmin[0]) * 1e3))
    lines.append(
        "WATER SHADING IS DISPLAY ONLY. warpmpm computes no optics, no free surface "
        "and no air phase (register B7: not even a pressure field). Surface = "
        "per-column max-z of the particles, Gaussian-smoothed as a 2D heightfield "
        "at a length borrowed from splashsurf (Loschner et al. 2023), ~2x particle "
        "radius = h; NOT a splashsurf reconstruction, which marching-cubes a 3D SPH "
        "density field. Drawn ONLY where particles exist. Optics = Schlick + "
        "Beer-Lambert + GGX against assets/DaySkyHDRI002A_1K_HDR.exr, %s. FOAM is a "
        "POST-HOC Weber-number diagnostic, We = rho|v_rel|^2 L/sigma, onset We %.0f "
        "(Ihmsen et al. 2012): the solver entrained no air, and no verdict depends "
        "on any of this."
        % (optics_frag or ("absorption exaggerated %.0fx" % VIS_GAIN), WE_LO))
    if extra:
        lines.append(extra)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--hdri-cache", required=True)
    ap.add_argument("--frames", default="all")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--width", type=int, default=1800)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--elev", type=float, default=16.0)
    ap.add_argument("--azim", type=float, default=-62.0)
    ap.add_argument("--half", type=float, default=3.9)
    ap.add_argument("--slab-cells", type=float, default=3.0)
    ap.add_argument("--surf-cell", type=float, default=0.125,
                    help="free-surface reconstruction cell size, m. Must be >= the "
                         "particle spacing h = dx/2, or most columns hold 0-1 "
                         "particles and the sheet comes out speckled rather than "
                         "smooth. Rogue h = 0.0816 m, Silverado h = 0.1021 m.")
    ap.add_argument("--exposure", type=float, default=1.45)
    ap.add_argument("--upsample", type=int, default=3)
    ap.add_argument("--sigma", type=float, default=1.0)
    ap.add_argument("--max-faces", type=int, default=9000)
    ap.add_argument("--ssc-mg-l", type=float, default=-1.0,
                    help="suspended-sediment concentration, mg/L. Negative (the "
                         "default) keeps the legacy exaggerated clear-water "
                         "optics. Zero or more switches to turbid optics with no "
                         "exaggeration. Presets: %s"
                         % ", ".join("%s=%g" % kv
                                     for kv in sorted(FWO.SSC_PRESET_MG_L.items(),
                                                      key=lambda kv: kv[1])))
    ap.add_argument("--ssc-preset", default=None,
                    choices=sorted(FWO.SSC_PRESET_MG_L),
                    help="named SSC preset; overrides --ssc-mg-l")
    ap.add_argument("--vehicle-mesh", default=None,
                    help="path to the source hull .ply. Default (omitted) keeps "
                         "the marching-cubes reconstruction of the simulated "
                         "particles. Supplying a mesh registers it to the "
                         "simulated pose and REFUSES if it does not fit. "
                         "REGISTER E8: the resulting frame contains derived "
                         "NCAC/CCSA geometry and must not be published.")
    a = ap.parse_args()
    if a.ssc_preset:
        a.ssc_mg_l = FWO.preset_ssc(a.ssc_preset)

    run, out = Path(a.run), Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    sky, sun = load_hdri(Path(a.hdri_cache))

    z = RMR.load_run(run)
    pv, world, worst, errs = RMR.rigid_transform(z)
    print("[shade] run             : %s" % run)
    print("[shade] transform check : max|err| %.3e m  (gates.py:136/:157 reused)" % worst)

    hpart = 0.5 * z["dx"]
    if a.vehicle_mesh:
        # E8 PATH. Register E8 forbids DISTRIBUTION of derived NCAC/CCSA
        # geometry ("do not commit any derived NCAC/CCSA geometry to the public
        # repo, and do not include it in a DesignSafe DOI"), and records the
        # canonical Yaris hull's provenance as UNRESOLVED between an
        # NHTSA-hosted (safe) and a CCSA-hosted (licence-silent) origin. Nothing
        # in E8 restricts reading or rendering. So this path is available for
        # internal review renders, and the caption and manifest both say loudly
        # that the frame contains source hull geometry, so no output of this
        # path can be published by accident.
        import vehicle_mesh_transform as VMT
        reg = VMT.load_and_register(a.vehicle_mesh, z, max_faces=a.max_faces)
        Vb, Fb = reg["vertices_body"], reg["faces"]
        n_raw = reg["n_faces"]
        veh_prov = {
            "source": "REAL HULL MESH, %s" % a.vehicle_mesh,
            "yaw_deg": reg["yaw_deg"],
            "height_profile_corr_vs_particles": reg["profile_corr"],
            "extent_residual_m": reg["residual_m"],
            "extent_residual_cells": reg["residual_cells"],
            "faces": int(len(Fb)),
            "E8": "Derived NCAC/CCSA geometry. Register E8: DO NOT commit this "
                  "frame or the derived geometry to a public repo or a "
                  "DesignSafe DOI. Yaris hull provenance (NHTSA vs CCSA) is "
                  "recorded as UNRESOLVED in E8. Internal review only.",
        }
        veh_caption = (
            "vehicle surface = REAL SOURCE HULL %s, registered to the simulated "
            "body by derived yaw %d deg (height-profile corr %+.4f), extent "
            "residual %.4f m = %.2f particle cells, %d faces. THIS FRAME "
            "CONTAINS DERIVED NCAC/CCSA GEOMETRY: register E8 forbids "
            "publishing it. It shows the hull the solver was BUILT FROM, not "
            "the geometry it integrated."
            % (Path(a.vehicle_mesh).name, reg["yaw_deg"], reg["profile_corr"],
               reg["residual_m"], reg["residual_cells"], len(Fb)))
        print("[shade] vehicle mesh    : %s, yaw %d deg, corr %+.4f, residual "
              "%.4f m (%.2f cells), %d faces"
              % (Path(a.vehicle_mesh).name, reg["yaw_deg"], reg["profile_corr"],
                 reg["residual_m"], reg["residual_cells"], len(Fb)))
        print("[shade] E8 WARNING      : frame contains derived source-hull "
              "geometry, do not publish")
    else:
        Vb, Fb, n_raw = RMR.build_surface(pv, hpart, upsample=a.upsample,
                                          sigma=a.sigma, max_faces=a.max_faces)
        veh_prov = {
            "source": "marching-cubes isosurface of the SIMULATED rigid particles",
            "faces": int(len(Fb)),
            "E8": "No .ply is read, so register E8 is not engaged.",
        }
        veh_caption = ("vehicle surface = marching-cubes isosurface of the %d "
                       "SIMULATED rigid particles (h = dx/2 = %.5f m, %d faces); "
                       "no .ply is read, so register E8 is not engaged."
                       % (len(pv), hpart, len(Fb)))
    base, n_tire = RMR.base_colours(Vb, Fb)
    outside = int(((pv < Vb.min(0) - 1e-9) | (pv > Vb.max(0) + 1e-9)).any(1).sum())
    print("[shade] surface         : %d faces, encloses %d/%d particles"
          % (len(Fb), len(pv) - outside, len(pv)))
    if outside:
        print("[shade] WARNING        : surface ERODED, %d particles outside bbox" % outside)

    water, speed = z["water"], z["speed"]
    nf, floor, dx = water.shape[0], z["floor"], z["dx"]
    zmin = np.array([world(f)[:, 2].min() for f in range(nf)])
    print("[shade] veh z-min       : f0 %.6f  f%d %.6f  min excursion %+.3e m"
          % (zmin[0], nf - 1, zmin[-1], (zmin - floor).min()))

    smp = speed[::5].ravel()
    vlo, vhi = float(np.percentile(smp, 5.0)), float(np.percentile(smp, 97.0))
    if vhi <= vlo:
        vhi = vlo + 1e-6

    v0, vL = world(0), world(nf - 1)
    zhi = max(float(water[:, :, 2].max()), v0[:, 2].max(), vL[:, 2].max()) * 1.02
    zlo = floor - 0.10
    cx = 0.5 * (v0[:, 0].mean() + vL[:, 0].mean())
    cy = float(v0[:, 1].mean())
    ylo_p, yhi_p = v0[:, 1].min() - 1.6, v0[:, 1].max() + 1.6

    # matplotlib camera: azim from +x toward +y, elev from the xy-plane toward +z.
    el, az = np.radians(a.elev), np.radians(a.azim)
    view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])

    k_water, scatter_water, optics_frag, optics_prov = optics_from_ssc(a.ssc_mg_l)
    print("[shade] water optics    : %s" % optics_frag)

    cap = caption_lines(z, zmin, floor, veh_caption, optics_frag=optics_frag)
    idx = list(range(0, nf, a.stride)) if a.frames == "all" else [int(a.frames)]
    slab = a.slab_cells * dx
    foam_stats, we_stats = [], []

    for f in idx:
        w, sp = water[f], speed[f]
        vp = world(f)
        vx = float(vp[:, 0].mean())
        hull_xy = (vp[:, 0].min(), vp[:, 0].max(), vp[:, 1].min(), vp[:, 1].max())

        Vw = Vb @ z["R"][f].T + z["t"][f]
        nrm, tri = RMR.face_normals_outward(Vw, Fb)
        fcol = RMR.shade(base, nrm)
        order = np.argsort(tri.mean(1)[:, 0])
        tri_yz, fcol_yz = tri[:, :, 1:3][order], fcol[order]

        X, Y, Hh, S, wet = free_surface(w, sp, cx, cy, a.half, floor,
                                        a.surf_cell, hpart)
        wrgb, foam, We = shade_water(X, Y, Hh, S, floor, view, sky, sun,
                                     hpart, a.exposure,
                                     k_rgb=k_water, scatter_rgb=scatter_water)
        # foam and We reported over WET cells only; averaging over dry ground
        # would silently dilute both and make the diagnostic unreadable.
        foam_stats.append(float(foam[wet].mean()) if wet.any() else 0.0)
        we_stats.append(float(np.nanpercentile(We[wet], 99.0)) if wet.any() else 0.0)
        # Cut the sheet out of the hull footprint: the vehicle displaces the water.
        # Shading is computed on the full field first so the cut cannot bias it.
        occ = hull_footprint_mask(vp, X, Y, a.surf_cell)
        drop = occ | ~wet
        wq, wc = surface_quads(X, Y, np.where(wet, Hh, np.nan), wrgb, drop)

        fig = plt.figure(figsize=(a.width / a.dpi, a.height / a.dpi), dpi=a.dpi)
        gs = GridSpec(3, 2, figure=fig, width_ratios=[1.12, 1.0],
                      height_ratios=[1.0, 0.55, 0.62],
                      left=0.02, right=0.975, top=0.945, bottom=0.235,
                      wspace=0.13, hspace=0.55)

        # ---- oblique 3D: shaded water sheet + solid hull ---------------------
        ax = fig.add_subplot(gs[:, 0], projection="3d")
        # D1: ONE collection carrying water quads AND hull faces, so the painter's
        # sort is over all faces together instead of between two artists.
        polys = wq + list(tri)
        pcol = np.vstack([wc, fcol]) if len(wq) else fcol
        pc = Poly3DCollection(polys, facecolors=pcol, edgecolors="none",
                              linewidths=0, shade=False, zsort="average")
        ax.add_collection3d(pc)
        ax.set_xlim(cx - a.half, cx + a.half)
        ax.set_ylim(cy - a.half, cy + a.half)
        ax.set_zlim(zlo, zhi)
        ax.set_box_aspect((1.0, 1.0, (zhi - zlo) / (2.0 * a.half)))
        ax.view_init(elev=a.elev, azim=a.azim)
        ax.set_xlabel("x, flow direction (m)", fontsize=8)
        ax.set_ylabel("y (m)", fontsize=8)
        ax.set_zlabel("z (m)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title("frame %03d / %d    t = %.3f s    shaded free surface "
                     "(display model)" % (f, nf - 1, f / z["fps"]), fontsize=10)

        # ---- car profile, (y, z), equal aspect, PARTICLES not the sheet ------
        ax2 = fig.add_subplot(gs[0, 1])
        m = np.abs(w[:, 0] - vx) < slab
        ax2.scatter(w[m, 1], w[m, 2], c=sp[m], cmap="viridis", vmin=vlo, vmax=vhi,
                    s=3.2, alpha=0.5, linewidths=0, rasterized=True)
        ax2.add_collection(PolyCollection(tri_yz, facecolors=fcol_yz,
                                          edgecolors="none", zorder=4, rasterized=True))
        ax2.axhline(floor, color="#222222", lw=1.5, zorder=5)
        ax2.set_xlim(ylo_p, yhi_p)
        ax2.set_ylim(zlo, zhi)
        ax2.set_aspect("equal")
        ax2.set_xlabel("y, vehicle long axis (m)", fontsize=8)
        ax2.set_ylabel("z (m)", fontsize=8)
        ax2.tick_params(labelsize=7)
        ax2.set_title("car profile, raw particles, slab |x - x_veh| < %.2f m "
                      "(unshaded: this is the data)" % slab, fontsize=9)

        # ---- foam field, plan view -------------------------------------------
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.pcolormesh(X, Y, np.where(wet, foam, np.nan), cmap="bone",
                       vmin=0.0, vmax=1.0, rasterized=True)
        ax4.plot([hull_xy[0], hull_xy[1], hull_xy[1], hull_xy[0], hull_xy[0]],
                 [hull_xy[2], hull_xy[2], hull_xy[3], hull_xy[3], hull_xy[2]],
                 color="#b3282d", lw=1.2)
        ax4.set_aspect("equal")
        ax4.set_xlabel("x (m)", fontsize=8)
        ax4.set_ylabel("y (m)", fontsize=8)
        ax4.tick_params(labelsize=7)
        ax4.set_title("foam from Weber number (Ihmsen 2012), We_99 = %.0f; "
                      "red = hull footprint" % we_stats[-1], fontsize=9)

        # ---- z-min against the floor plane -----------------------------------
        ax3 = fig.add_subplot(gs[2, 1])
        ax3.plot(np.arange(nf), (zmin - floor) * 1e3, color="#b3282d", lw=1.5)
        ax3.axhline(0.0, color="#222222", lw=1.2)
        ax3.plot([f], [(zmin[f] - floor) * 1e3], "o", color="black", ms=5)
        ax3.set_xlim(0, nf - 1)
        ax3.set_xlabel("frame", fontsize=8)
        ax3.set_ylabel("z-min above floor (mm)", fontsize=8)
        ax3.tick_params(labelsize=7)
        ax3.grid(alpha=0.25, lw=0.5)
        ax3.set_title("z-min above floor: f0 %+.1f mm -> f%d %+.1f mm"
                      % ((zmin[0] - floor) * 1e3, nf - 1, (zmin[-1] - floor) * 1e3),
                      fontsize=9)

        for i, line in enumerate(cap):
            fig.text(0.02, 0.198 - i * 0.0272, line,
                     fontsize=9.0 if i == 0 else 7.2,
                     color="#8a1010" if i in (0, 3) else "#222222",
                     weight="bold" if i in (0, 3) else "normal", wrap=True)

        fig.savefig(out / ("frame_%04d.png" % f), dpi=a.dpi, facecolor="white")
        plt.close(fig)
        if f % 10 == 0 or f == idx[-1]:
            print("[shade]   wrote frame_%04d.png" % f, flush=True)

    manifest = {
        "run": str(run), "outdir": str(out), "script": os.path.abspath(__file__),
        "reuses": "analysis/render_multigeom_rollout.py (transform, surface, colours)",
        "canonical_status": "NON-CANONICAL companion experiment; not in the 17-run "
                            "gated inventory; class_specific and hullsweep batches "
                            "kept distinct per register E3a",
        "frames_written": len(idx), "fps_from_npz": z["fps"],
        "vehicle_surface": veh_prov,
        "transform_source": "gates.py:136 and gates.py:157, reused verbatim",
        "transform_max_reconstruction_error_m": worst,
        "transform_errors_by_frame_m": {str(k): v for k, v in errs.items()},
        "floor_plane_m": floor, "floor_definition": "3.0*dx, sim_standing.py:164",
        "veh_zmin_frame0_m": float(zmin[0]), "veh_zmin_final_m": float(zmin[-1]),
        "veh_zmin_min_excursion_below_floor_m": float((zmin - floor).min()),
        "summary_C2_veh_zmin_rise": z["summary"]["C2_veh_zmin_rise"],
        "P2_passthrough": z["summary"]["passthrough_max_frac"],
        "P2_pass": bool(z["summary"]["passthrough_max_frac"] < 0.10),
        "P3_pass": bool(abs(z["summary"]["C2_veh_zmin_rise"]) <= 0.01),
        "water_shading": {
            "STATUS": "DISPLAY ONLY, not simulated optics",
            # Was "gaussian sigma=1 cell". That was stale and contradicted the
            # adjacent surface_smoothing key: the smoothing is computed at :276
            # as max(0.6, h / surf_cell), which is never 1.0 for any run in this
            # batch (0.60 to 0.82 at --surf-cell 0.125).
            "free_surface": "per-column max-z of water particles, gaussian "
                            "sigma = max(0.6, h / surf_cell) = %.4f cells; "
                            "warpmpm has no free-surface field"
                            % max(0.6, hpart / a.surf_cell),
            "fresnel": "Schlick, F0=%.4f (IOR %.3f)" % (F0_WATER, IOR),
            "absorption": optics_prov,
            "specular": "GGX against the HDRI sun direction",
            "environment": "assets/DaySkyHDRI002A_1K_HDR.exr, READ not regenerated",
            "sun_dir_xyz": sun.tolist(),
            "foam": "POST-HOC Weber-number diagnostic, We = rho|v_rel|^2 L/sigma, "
                    "rho=%.0f sigma=%.4f L=particle spacing h, onset We=%.0f "
                    "saturation We=%.0f. Model: Ihmsen, Akinci, Akinci and Teschner "
                    "2012 unified spray/foam/bubble, per research report b0d2664f "
                    "item 15 (T2, NOT checked against a primary record). NOT an "
                    "air-entrainment simulation: warpmpm has no air phase and no "
                    "surface tension. v1 used a per-frame steepness percentile, "
                    "which self-normalised and produced foam on still water at t=0; "
                    "that is defect D3 and is retired."
                    % (RHO_W, SIGMA_W, WE_LO, WE_HI),
            "foam_mean_over_wet_by_frame": foam_stats,
            "We_p99_over_wet_by_frame": we_stats,
            "surface_smoothing": "normalised Gaussian convolution over WET cells "
                                 "only, on a 2D column-max heightfield. Length "
                                 "scale ~2x particle radius = h BORROWED from "
                                 "splashsurf (Loschner/splashsurf, report b0d2664f "
                                 "item 13, T2, not checked against a primary "
                                 "record). NOT a splashsurf reconstruction: "
                                 "splashsurf marching-cubes a 3D SPH density field "
                                 "and a Gaussian sigma is not an SPH kernel support "
                                 "radius, so only the length is taken. h is the "
                                 "particle SPACING (h/dx = 0.5 exactly), so the "
                                 "radius is h/2. Against MEASURED post-settle "
                                 "spacing (0.82h) the applied smoothing is 1.22x "
                                 "the 2x-radius target, not 1.00x. Dry columns are "
                                 "DROPPED, not floor-filled; floor-filling was "
                                 "defect D2.",
            "v2_defects_fixed": [
                "D1 vehicle sliced by the water sheet (separate matplotlib artists)",
                "D2 water drawn on dry ground (floor-filled empty columns)",
                "D3 foam self-normalised per frame, appeared on still water",
                "D4 arbitrary 1-cell smoothing vs splashsurf guidance",
                "D5 right-edge shelf, a consequence of D2",
            ],
            "exposure": a.exposure, "tone_map": "Reinhard, gamma 2.2",
            "surface_cell_m": a.surf_cell,
        },
        "caption": cap,
    }
    (out / "render_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("[shade] frames written  : %d" % len(idx))
    print("[shade] mean foam frac  : %.4f" % float(np.mean(foam_stats)))


if __name__ == "__main__":
    main()
