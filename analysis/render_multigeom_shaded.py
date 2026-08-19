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
  D4 v1 smoothed with an arbitrary sigma of 1 cell. Loschner, Bender et al. 2023
     (splashsurf) give smoothing length ~2.0x particle radius for particle-to-
     surface reconstruction without volume loss; that guidance is used instead.
  D5 The right-edge "shelf" that read as a solid ramp was a consequence of D2.
Source for D3 and D4: research report b0d2664f Part 3 items 13 and 15, on disk at
~/Downloads/compass_artifact_wf-b0d2664f-*.md. That report is T2 and its Ihmsen and
Loschner citations have NOT been checked against a primary record here.

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

BANNER_NONCANON = ("NON-CANONICAL COMPANION EXPERIMENT   not part of the 17-run "
                   "gated inventory   (class_specific and hullsweep batches kept "
                   "distinct)")
BANNER_CANON = ("CANONICAL 17-RUN INVENTORY   run '%s' is row %d of "
                "data/all_runs_inventory.csv   DISPLAY RENDER, not a measurement")
INVENTORY_CSV = Path(__file__).resolve().parents[1] / "data" / "all_runs_inventory.csv"


def banner_for(run: Path) -> str:
    """The banner is DERIVED from the canonical inventory, never hardcoded.

    This module was written for the multigeom companion runs and carried a
    hardcoded "NON-CANONICAL ... not part of the 17-run gated inventory" string.
    Pointed at any of the 17 gated runs, that string is a FALSE PROVENANCE CLAIM
    printed onto the image itself. The 17-run store is data/all_runs_inventory.csv
    (CLAUDE.md August 4 audit item 8), so the run name is looked up there and the
    banner follows the answer. If the inventory cannot be read, the banner says so
    rather than asserting either way.
    """
    try:
        rows = INVENTORY_CSV.read_text().splitlines()
    except OSError as exc:
        return ("PROVENANCE UNVERIFIED   could not read %s (%s)   "
                "do not cite this frame's inventory status"
                % (INVENTORY_CSV.name, type(exc).__name__))
    names = [r.split(",", 1)[0].strip() for r in rows[1:] if r.strip()]
    if run.name in names:
        return BANNER_CANON % (run.name, names.index(run.name) + 1)
    return BANNER_NONCANON

# Water optical constants.
F0_WATER = 0.0204          # Schlick F0 for air->water, ((1.333-1)/(1.333+1))**2
IOR = 1.333
# Beer-Lambert absorption, 1/m, red absorbed hardest. Real clear-water values are
# about (0.45, 0.07, 0.03) 1/m, which over a 0.30 m tank is a ~13% red loss and is
# invisible. VIS_GAIN exaggerates it so the depth cue reads on screen. This is a
# display choice and is stated in the caption; it is not a measurement.
SIGMA_RGB = np.array([0.45, 0.07, 0.03], dtype=np.float32)
VIS_GAIN = 9.0
BOTTOM_RGB = np.array([0.050, 0.050, 0.050], dtype=np.float32)   # wet asphalt
SCATTER_RGB = np.array([0.020, 0.160, 0.200], dtype=np.float32)  # in-water tint

# Weber-number foam criterion (Ihmsen et al. 2012). ABSOLUTE physical scale, which
# is the whole point: unlike v1's per-frame percentile, still water returns zero.
RHO_W = 1000.0            # kg/m3
SIGMA_W = 0.0728          # N/m, air-water surface tension at 20 C
WE_LO, WE_HI = 8.0, 60.0  # onset and saturation. The classic critical Weber for
                          # droplet breakup is O(10); the band is stated rather
                          # than tuned per frame, and the MEASURED We range is
                          # printed and written to the manifest so it is auditable.


ASSETS = Path(__file__).resolve().parents[1] / "assets"
HDRI_EXR = ASSETS / "DaySkyHDRI002A_1K_HDR.exr"


def build_hdri_cache(cache_dir: Path):
    """Decode assets/DaySkyHDRI002A_1K_HDR.exr to the .npy pair load_hdri reads.

    WHY THIS EXISTS. `--hdri-cache` was a required argument and NOTHING IN THE
    REPOSITORY PRODUCED THE CACHE: a live check on 2026-08-19 found this module is
    the only file in the tracked tree that names hdri_sky.npy, and it only reads
    it. So the renderer could not be run from a clean checkout, and the four
    committed manifests under renders/multigeom_2026-08-08_render/ were produced
    from a cache built by something no longer in the tree. This closes that hole.

    The EXR is READ and decoded to .npy. The asset is never written.

    SUN DIRECTION is derived, not typed: the luminance-weighted, solid-angle
    weighted centroid of the brightest 0.01 percent of texels. Measured on the
    shipped file this gives elevation 64.4 deg. Taking the bare argmax instead
    lands on one texel of a 53-texel sun disc and is noisier.
    """
    try:
        import OpenEXR
    except ImportError:
        raise SystemExit(
            "Cannot decode %s: the OpenEXR module is not installed and no cache "
            "exists at %s. Install it (uv pip install OpenEXR) or point "
            "--hdri-cache at a directory holding hdri_sky.npy and hdri_sun.npy."
            % (HDRI_EXR.name, cache_dir))
    if not HDRI_EXR.exists():
        raise SystemExit("HDRI asset missing: %s" % HDRI_EXR)
    f = OpenEXR.File(str(HDRI_EXR))
    sky = np.asarray(f.parts[0].channels["RGBA"].pixels)[:, :, :3].astype(np.float32)
    sky = np.clip(sky, 0.0, None)          # the shipped file carries a small
    H, W, _ = sky.shape                    # negative epsilon, -0.0054
    lum = sky @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    m = lum >= np.percentile(lum, 99.99)
    jj, ii = np.nonzero(m)
    pol = (jj + 0.5) / H * np.pi
    az = ((ii + 0.5) / W - 0.5) * 2.0 * np.pi
    w = lum[m] * np.sin(pol)               # solid-angle weight
    d = np.stack([np.sin(pol) * np.cos(az), np.sin(pol) * np.sin(az),
                  np.cos(pol)], axis=1)
    sun = (d * w[:, None]).sum(0)
    sun /= np.linalg.norm(sun) + 1e-12
    cache_dir.mkdir(parents=True, exist_ok=True)
    np.save(cache_dir / "hdri_sky.npy", sky)
    np.save(cache_dir / "hdri_sun.npy", sun.astype(np.float32))
    print("[shade] hdri cache      : built from %s, %dx%d, sun elev %.1f deg"
          % (HDRI_EXR.name, W, H, np.degrees(np.arcsin(sun[2]))))
    return sky, sun.astype(np.float32)


def load_hdri(cache_dir: Path):
    """Load the cached equirect HDRI and its sun direction, building it if absent.

    assets/DaySkyHDRI002A_1K_HDR.exr is READ, never regenerated. It is decoded
    once to .npy because no EXR backend is installed in the render venv; the
    decode step is a read of the asset, not a rewrite of it.
    """
    sky_p, sun_p = cache_dir / "hdri_sky.npy", cache_dir / "hdri_sun.npy"
    if not (sky_p.exists() and sun_p.exists()):
        sky, sun = build_hdri_cache(cache_dir)
    else:
        sky = np.load(sky_p).astype(np.float32)
        sun = np.load(sun_p).astype(np.float32)
    return sky, sun / (np.linalg.norm(sun) + 1e-12)


def prefilter_env(sky, levels=(0.0, 6.0, 28.0)):
    """Roughness pyramid of the equirect environment: sharp, glossy, diffuse.

    This is the split-sum approximation's prefiltered-environment half (Karis
    2013): a rough surface reflects an average over a lobe, so instead of one
    mirror sample it takes one sample from a pre-blurred copy. The blur is done
    in the equirect domain with WRAP in azimuth and REFLECT in polar, which is
    approximate near the poles and exact enough at the horizon, where every
    reflection in this scene lands.

    NOT NEW INGREDIENTS. The water already samples this same environment along
    its mirror direction (sample_env at the reflection step). All this adds is
    the ability to sample it at a roughness, which is what lets a car body and
    an asphalt road use the same environment as the water instead of a constant.
    """
    from scipy.ndimage import gaussian_filter
    out = []
    for s in levels:
        if s <= 0.0:
            out.append(sky)
            continue
        # wrap azimuth so the seam at +/-pi does not darken
        pad = int(np.ceil(3.0 * s))
        pad = min(pad, sky.shape[1] // 2 - 1)
        w = np.concatenate([sky[:, -pad:], sky, sky[:, :pad]], axis=1)
        b = np.stack([gaussian_filter(w[:, :, c], sigma=s, mode="nearest")
                      for c in range(3)], axis=-1)
        out.append(b[:, pad:pad + sky.shape[1]])
    return out


def env_at_roughness(sky_p, d, rough):
    """Sample the prefiltered pyramid, blending between levels by roughness."""
    lo = sample_env(sky_p[0], d)
    mid = sample_env(sky_p[1], d)
    hi = sample_env(sky_p[2], d)
    r = np.clip(np.asarray(rough, dtype=np.float32), 0.0, 1.0)[..., None]
    a = np.clip(r / 0.35, 0.0, 1.0)          # sharp -> glossy over 0.00-0.35
    b = np.clip((r - 0.35) / 0.65, 0.0, 1.0)  # glossy -> diffuse over 0.35-1.0
    return lo * (1.0 - a) + mid * a * (1.0 - b) + hi * b


def ggx_spec(n, l, v, rough, F):
    """GGX/Trowbridge-Reitz D term against a single direction, Smith-free.

    IDENTICAL FORM to the water's specular lobe (shade_water, GGX step): same D,
    same half-vector, same Fresnel weighting. Only the roughness differs. Kept as
    a shared function so the two surfaces cannot drift apart.
    """
    h = l + v
    h = h / (np.linalg.norm(h, axis=-1, keepdims=True) + 1e-12)
    ndoth = np.clip(np.einsum("...i,...i->...", n, h), 0.0, 1.0)
    a2 = np.clip(rough * rough, 1e-5, 1.0) ** 2
    D = a2 / (np.pi * ((ndoth * ndoth) * (a2 - 1.0) + 1.0) ** 2)
    return (F * D)[..., None] * np.array([1.0, 0.98, 0.94], dtype=np.float32)


def tonemap(rgb, exposure):
    """Reinhard + gamma 2.2. The SAME output transform the water already used.

    This is the fix for a real defect, not a flourish: shade_water returned
    tone-mapped, gamma-encoded values while RMR.shade returned raw clamped
    linear ones, and both were pushed into the SAME Poly3DCollection. Water and
    vehicle were being composited in two different colour spaces in one image.
    """
    rgb = np.asarray(rgb, dtype=np.float32) * exposure
    rgb = rgb / (1.0 + rgb)
    return np.clip(rgb, 0.0, 1.0) ** (1.0 / 2.2)


def sample_env(sky, d):
    """Equirectangular lookup. d is (...,3), unit, z up. v=0 is +z (zenith)."""
    x, y, z = d[..., 0], d[..., 1], d[..., 2]
    pol = np.arccos(np.clip(z, -1.0, 1.0))
    az = np.arctan2(y, x)
    H, W, _ = sky.shape
    i = np.clip(((az / (2 * np.pi) + 0.5) * W).astype(np.int32), 0, W - 1)
    j = np.clip(((pol / np.pi) * H).astype(np.int32), 0, H - 1)
    return sky[j, i]


# ---------------------------------------------------------------------------
# Vehicle material. Same ingredients as the water: Schlick Fresnel, a GGX lobe
# against the HDRI sun, and the HDRI itself for both reflection and irradiance.
# ---------------------------------------------------------------------------
# Dielectric F0. Car clearcoat and rubber are both dielectrics; 0.04 is the
# standard n=1.5 value, ((1.5-1)/(1.5+1))**2 = 0.04. Not a tuned number.
F0_DIELECTRIC = 0.04
ROUGH_BODY = 0.22          # clearcoat over paint: glossy, not a mirror
ROUGH_TIRE = 0.80          # rubber: nearly diffuse
SPEC_GAIN = 0.030          # same lobe gain the water uses, kept equal on purpose


def smooth_face_normals(V, F, flat):
    """Area-weighted vertex normals, averaged back onto faces.

    WHY THIS IS NEEDED AND WHY IT IS NOT CHEATING. The vehicle is a marching-cubes
    isosurface of a particle lattice, so its facets are an artifact of the
    RECONSTRUCTION, not of the hull. With flat facet normals the Schlick term
    swings the full 0.04-to-1.0 range between neighbouring faces, and since F=1
    means "pure environment reflection", the car came out patched with sky-grey
    like crumpled foil. The old single-Lambert model hid this because a clamped
    dot product has no grazing-angle response at all.

    Smoothing the NORMAL is the correct fix rather than damping the Fresnel: the
    true hull is smooth, so the smooth normal is the better estimate of it. The
    GEOMETRY is untouched, so every silhouette, the floor contact and the bbox
    enclosure check all still see the exact reconstructed surface.
    """
    tri = V[F]
    area = 0.5 * np.linalg.norm(
        np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    vn = np.zeros_like(V, dtype=np.float64)
    for k in range(3):
        np.add.at(vn, F[:, k], flat * area[:, None])
    vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
    sm = vn[F].mean(axis=1)
    sm /= np.linalg.norm(sm, axis=1, keepdims=True) + 1e-12
    # Keep the smoothed normal on the same side as the flat one.
    sm[np.einsum("ij,ij->i", sm, flat) < 0.0] *= -1.0
    return sm


def shade_vehicle(nrm, base, tire, view, sky_p, sun, exposure):
    """Fresnel + GGX + HDRI vehicle material, replacing a single Lambert term.

    WHAT THIS REPLACES. render_multigeom_rollout.shade() was, in full:
        sh = clip(n . LIGHT, 0, 1) * 0.6 + 0.4
        return clip(sh[:, None] * base, 0, 1)
    One clamped dot product against a hardcoded direction, no environment, no
    Fresnel, no specular, no tone map, in a figure whose water had all four.

    WHAT THIS IS NOT. It is not a new shading model and it is not a measurement.
    Every term here already existed in this file and was being applied to the
    water only. warpmpm computes no optics for either surface (register B7).

    Diffuse irradiance is approximated by one sample of the heavily blurred
    environment along the normal. That is the standard cheap irradiance estimate,
    and it is why the underside of the hull goes dark and the roof picks up sky:
    the old model lit both identically from a fixed vector.
    """
    n = nrm
    v = view / (np.linalg.norm(view) + 1e-12)
    # FACING RATIO, absolute. A back-facing normal must not be clamped toward
    # zero: Schlick sends F -> 1 there, i.e. "pure mirror", so every back face
    # would render as sky-grey. Measured on this hull at the default camera,
    # np.clip(n@v, 1e-4, 1) put 54.9 percent of the 9000 faces at F > 0.9 and
    # 77.4 percent of those were back faces. Back faces are culled by the caller,
    # and taking |n.v| keeps any that survive shading as a two-sided surface.
    ndotv = np.clip(np.abs(n @ v), 1e-4, 1.0)

    rough = np.where(tire, ROUGH_TIRE, ROUGH_BODY).astype(np.float32)

    # Fresnel (Schlick), identical form to the water's
    F = F0_DIELECTRIC + (1.0 - F0_DIELECTRIC) * (1.0 - ndotv) ** 5

    # diffuse: irradiance from the environment along the normal
    irr = env_at_roughness(sky_p, n, np.ones_like(rough))
    diff = base * irr

    # reflection: environment along the mirror direction, blurred by roughness
    r = 2.0 * ndotv[:, None] * n - v[None, :]
    r /= np.linalg.norm(r, axis=-1, keepdims=True) + 1e-12
    refl = env_at_roughness(sky_p, r, rough)

    # specular: GGX against the HDRI sun
    spec = ggx_spec(n, sun[None, :], v[None, :], rough, F) * SPEC_GAIN

    rgb = diff * (1.0 - F[:, None]) + refl * F[:, None] + spec
    return tonemap(rgb, exposure)


# ---------------------------------------------------------------------------
# Ground. THERE WAS NO GROUND. Dry columns are dropped entirely (the D2 fix), so
# outside the wet footprint the 3D view showed empty white paper.
# ---------------------------------------------------------------------------
GROUND_FALLBACK_ALBEDO = np.array([0.085, 0.085, 0.090], dtype=np.float32)
GROUND_FALLBACK_ROUGH = 0.70
ASPHALT = {
    "color": ASSETS / "Asphalt015_1K-JPG_Color.jpg",
    "rough": ASSETS / "Asphalt015_1K-JPG_Roughness.jpg",
    "normal": ASSETS / "Asphalt015_1K-JPG_NormalGL.jpg",
}
ASPHALT_LICENCE = (
    "assets/Asphalt015*: LICENCE NOT ESTABLISHED. No licence file ships in "
    "assets/, and none of the four files carries a copyright, licence or source "
    "string in its header (checked 2026-08-19). The naming scheme matches "
    "ambientCG, whose library is CC0, but provenance by naming convention is "
    "INFERENCE, not proof that these bytes came from there. Gated off by default "
    "for that reason.")


def load_ground_maps(kind: str, tile_m: float, cells: int):
    """Return (albedo_fn, rough_fn, normal_fn) sampling the ground maps in metres.

    kind='none' returns the untextured fallback and READS NOTHING from assets/,
    which is the default. kind='asphalt' reads the three Asphalt015 maps. See
    ASPHALT_LICENCE: their licence could not be established from the files, so
    the texture is opt-in and the caption says so on any frame that uses it.

    TILE SCALE IS A DISPLAY CHOICE, NOT A MEASUREMENT. The files carry no
    physical scale, so tile_m is stated in the caption rather than implied.
    """
    if kind == "none":
        return None
    import matplotlib.image as mpimg
    miss = [str(p) for p in ASPHALT.values() if not p.exists()]
    if miss:
        raise SystemExit("--ground-texture asphalt: missing %s" % ", ".join(miss))

    def rd(p, srgb):
        a = mpimg.imread(str(p)).astype(np.float32)
        if a.max() > 1.5:
            a /= 255.0
        if a.ndim == 2:
            a = a[:, :, None].repeat(3, axis=2)
        a = a[:, :, :3]
        return a ** 2.2 if srgb else a      # colour is sRGB-encoded; data maps

    return {                                # are linear and must NOT be degamma'd
        "color": rd(ASPHALT["color"], True),
        "rough": rd(ASPHALT["rough"], False),
        "normal": rd(ASPHALT["normal"], False),
        "tile_m": float(tile_m),
    }


def sample_tex(tex, X, Y, tile_m):
    """Nearest-neighbour tiled lookup, X/Y in metres."""
    h, w = tex.shape[:2]
    u = np.mod(X / tile_m, 1.0)
    v = np.mod(Y / tile_m, 1.0)
    i = np.clip((u * w).astype(np.int32), 0, w - 1)
    j = np.clip((v * h).astype(np.int32), 0, h - 1)
    return tex[j, i]


def ground_maps_at(gm, X, Y):
    """(albedo, roughness, normal) on the X/Y grid, in world units."""
    if gm is None:
        alb = np.broadcast_to(GROUND_FALLBACK_ALBEDO, X.shape + (3,)).copy()
        rgh = np.full(X.shape, GROUND_FALLBACK_ROUGH, dtype=np.float32)
        nrm = np.zeros(X.shape + (3,), dtype=np.float32)
        nrm[..., 2] = 1.0
        return alb, rgh, nrm
    t = gm["tile_m"]
    alb = sample_tex(gm["color"], X, Y, t)
    rgh = sample_tex(gm["rough"], X, Y, t)[..., 0]
    # NormalGL: tangent-space, +Y up (OpenGL convention, as the filename says).
    # Encoded 0..1 -> -1..1. z is the surface normal here because the ground is
    # flat and axis-aligned, so tangent space IS world space up to a swap.
    nt = sample_tex(gm["normal"], X, Y, t) * 2.0 - 1.0
    nrm = np.stack([nt[..., 0], nt[..., 1], np.abs(nt[..., 2])], axis=-1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-12
    return alb, rgh, nrm


def shade_ground(alb, rgh, nrm, view, sky_p, sun, exposure, wet_tint=None):
    """Ground material, same ingredients again: Fresnel + GGX + HDRI."""
    v = view / (np.linalg.norm(view) + 1e-12)
    ndotv = np.clip(np.einsum("ijk,k->ij", nrm, v), 1e-4, 1.0)
    F = F0_DIELECTRIC + (1.0 - F0_DIELECTRIC) * (1.0 - ndotv) ** 5
    irr = env_at_roughness(sky_p, nrm, np.ones_like(rgh))
    diff = alb * irr
    r = 2.0 * ndotv[..., None] * nrm - v[None, None, :]
    r /= np.linalg.norm(r, axis=-1, keepdims=True) + 1e-12
    refl = env_at_roughness(sky_p, r, rgh)
    spec = ggx_spec(nrm, sun[None, None, :], v[None, None, :], rgh, F) * SPEC_GAIN
    rgb = diff * (1.0 - F[..., None]) + refl * F[..., None] + spec
    return tonemap(rgb, exposure)


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
    # D4. Smoothing length from the splashsurf guidance (Loschner, Bender et al.
    # 2023, via research report b0d2664f item 13): ~2.0x the particle radius, not
    # the arbitrary 1 cell v1 used. particle radius ~ h/2, so 2.0*h/2 = h metres,
    # expressed here in cells. Smoothing is what turns a particle staircase into a
    # sheet that can carry a surface normal at all.
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
                bottom_rgb=None):
    """Analytic water shading. DISPLAY ONLY, see the module docstring.

    Returns (rgb, foam, We) with rgb already tone-mapped and gamma-encoded.
    Hh may carry NaN in dry columns (D2); gradients are taken on a NaN-filled
    copy and the caller drops the dry quads, so no colour is invented there.
    """
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
    trans = np.exp(-(SIGMA_RGB * VIS_GAIN)[None, None, :] * path[..., None])
    # The riverbed seen THROUGH the water. BOTTOM_RGB was a flat 0.05 grey whose
    # own comment read "wet asphalt"; when the ground is textured, the actual
    # ground albedo is used here, so the road reads continuously from dry, through
    # the shallow margin, into the deep water where Beer-Lambert absorbs it away.
    bot = BOTTOM_RGB[None, None, :] if bottom_rgb is None else bottom_rgb
    refr = bot * trans + SCATTER_RGB[None, None, :] * (1.0 - trans)

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


def caption_lines(z, zmin, floor, extra: str, banner: str) -> list[str]:
    """Numbers from this run's OWN summary.json / rollout.npz. Nothing retyped."""
    s = z["summary"]
    rise = s["C2_veh_zmin_rise"]
    nf = len(zmin)
    p2, p3 = s["passthrough_max_frac"], abs(rise) <= 0.01
    # The 17 gated runs carry no 'vehicle_key': that field is a multigeom addition.
    # Fall back to 'label', then to the run directory name, rather than crashing or
    # inventing a hull name.
    vkey = s.get("vehicle_key") or s.get("label") or z.get("run_name", "unknown")
    l2 = ("%s hull, %.1f kg, n_grid %d, dx %.5f m, %d water layers, depth %.2f m, "
          "surge %.1f m/s, %d frames at %d fps"
          % (vkey, s["mass_kg"], s["n_grid"], s["dx"], s["water_layers"],
             s["depth_m"], s["velocity_ms"], nf, z["fps"]))
    l3 = ("final |disp| %.5f m   P-2 passthrough %.4f (%s, limit <0.10)   "
          "P-3 z-min rise %+.5f m (%s, limit |rise|<=0.01)   verdict NO-FORD"
          % (s["final_disp_mag_m"], p2, "PASS" if p2 < 0.10 else "FAIL",
             rise, "PASS" if p3 else "FAIL"))
    lines = [banner, l2, l3]
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
        "per-column max-z of the particles, smoothed at ~2x particle radius per "
        "Loschner/splashsurf; drawn ONLY where particles exist. Optics = Schlick + "
        "Beer-Lambert + GGX against assets/DaySkyHDRI002A_1K_HDR.exr, absorption "
        "exaggerated %.0fx. FOAM is a POST-HOC Weber-number diagnostic, "
        "We = rho|v_rel|^2 L/sigma, onset We %.0f (Ihmsen et al. 2012): the solver "
        "entrained no air, and no verdict depends on any of this."
        % (VIS_GAIN, WE_LO))
    if extra:
        lines.append(extra)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--hdri-cache", default=None,
                    help="directory holding hdri_sky.npy / hdri_sun.npy. Built "
                         "from assets/DaySkyHDRI002A_1K_HDR.exr if absent. "
                         "Defaults to <outdir>/_hdri_cache. NO LONGER REQUIRED: "
                         "it used to be, and nothing in the repo produced it.")
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
    ap.add_argument("--ground-texture", choices=("none", "asphalt"), default="none",
                    help="'asphalt' reads assets/Asphalt015_1K-JPG_*. DEFAULT OFF: "
                         "those files carry no licence record, see ASPHALT_LICENCE.")
    ap.add_argument("--ground-tile-m", type=float, default=2.0,
                    help="physical size of one texture tile, m. A DISPLAY CHOICE: "
                         "the files carry no scale, so it is captioned not implied.")
    ap.add_argument("--cull-backfaces", action="store_true",
                    help="drop faces pointing away from the camera. Formally "
                         "correct for a closed body, but the hull has genus ~100 "
                         "so its tunnels become see-through. Off by default.")
    ap.add_argument("--hero", action="store_true",
                    help="3D view only, full canvas, caption kept. The diagnostic "
                         "panels are dropped; the provenance banner is not.")
    ap.add_argument("--legacy-vehicle-shading", action="store_true",
                    help="restore the single-Lambert vehicle and draw no ground, "
                         "i.e. the pre-2026-08-19 appearance, for A/B comparison.")
    ap.add_argument("--upsample", type=int, default=3)
    ap.add_argument("--sigma", type=float, default=1.0)
    ap.add_argument("--max-faces", type=int, default=9000)
    a = ap.parse_args()

    run, out = Path(a.run), Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    sky, sun = load_hdri(Path(a.hdri_cache) if a.hdri_cache
                         else out / "_hdri_cache")
    sky_p = prefilter_env(sky)
    gmaps = None if a.legacy_vehicle_shading else load_ground_maps(
        a.ground_texture, a.ground_tile_m, 0)
    if a.ground_texture == "asphalt" and not a.legacy_vehicle_shading:
        print("[shade] ground texture  : assets/Asphalt015_1K-JPG_* at %.2f m/tile"
              % a.ground_tile_m)
        print("[shade] LICENCE         : %s" % ASPHALT_LICENCE)

    z = RMR.load_run(run)
    z["run_name"] = run.name
    pv, world, worst, errs = RMR.rigid_transform(z)
    print("[shade] run             : %s" % run)
    print("[shade] transform check : max|err| %.3e m  (gates.py:136/:157 reused)" % worst)

    hpart = 0.5 * z["dx"]
    Vb, Fb, n_raw = RMR.build_surface(pv, hpart, upsample=a.upsample,
                                      sigma=a.sigma, max_faces=a.max_faces)
    base, n_tire = RMR.base_colours(Vb, Fb)
    # Which faces base_colours painted as tire, recovered from the colour it
    # assigned rather than by re-deriving the geometric test, so the two can
    # never disagree about which face is rubber and which is paint.
    tire_face = np.all(np.isclose(base, RMR.TIRE[None, :]), axis=1)
    # Base colours are authored as sRGB-ish display values; the new material
    # pipeline works in linear light and gamma-encodes at the end, so decode
    # them once here. Without this the car comes out washed out. Kept SEPARATE
    # from `base` so --legacy-vehicle-shading reproduces the old frame exactly.
    base_lin = base.astype(np.float32) ** 2.2
    # The body is RIGID, so smoothed normals are computed ONCE in the body frame
    # and rotated per frame. Exact, and it keeps the per-frame cost unchanged.
    nrm_body_flat, _ = RMR.face_normals_outward(Vb, Fb)
    nrm_body = smooth_face_normals(Vb, Fb, nrm_body_flat)
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

    cap = caption_lines(z, zmin, floor,
                        "vehicle surface = marching-cubes isosurface of the %d "
                        "SIMULATED rigid particles (h = dx/2 = %.5f m, %d faces); "
                        "no .ply is read, so register E8 is not engaged."
                        % (len(pv), hpart, len(Fb)),
                        banner_for(run))
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
        if a.legacy_vehicle_shading:
            fcol = RMR.shade(base, nrm)
        else:
            fcol = shade_vehicle(nrm_body @ z["R"][f].T, base_lin, tire_face,
                                 view, sky_p, sun, a.exposure)
        # BACK-FACE CULLING. The hull is a closed opaque body, so a face pointing
        # away from the camera is never visible and drawing it can only leak
        # through gaps in matplotlib's painter's sort. It is also half the mesh:
        # 4584 of 9000 faces at the default camera. The old flat-Lambert model
        # made the leak hard to see because its darkest possible value was still
        # 0.4*base, a dark red; an environment-lit model paints the same leaked
        # faces sky-grey. Culling fixes the cause, not the symptom.
        # Culled in the 3D panel only. The profile panel is an ORTHOGRAPHIC view
        # along +x drawn in ascending-x order, so the painter's order there is
        # already exact and back faces are overpainted by near ones; culling on a
        # staircase surface would instead punch holes wherever a near face has
        # n_x == 0 exactly, which on a marching-cubes lattice is most of them.
        # OFF BY DEFAULT, and the reason is a measured property of the hull, not
        # a preference. The reconstructed isosurface is CLOSED (0 boundary edges
        # at every decimation level tested) but has GENUS ~100: about a hundred
        # tunnels pass through it, gaps the particle lattice never closed. Culling
        # is formally correct for a closed body and it makes those tunnels
        # see-through, which at hero framing reads as a broken car. Drawing the
        # back faces fills them with the far interior surface. The silhouette,
        # the floor contact and the particle-enclosure check are identical either
        # way; only the tunnel interiors differ.
        keep3 = ((nrm @ view) > 0.0 if (a.cull_backfaces
                                        and not a.legacy_vehicle_shading)
                 else np.ones(len(tri), dtype=bool))
        tri3, fcol3 = tri[keep3], fcol[keep3]
        order = np.argsort(tri.mean(1)[:, 0])
        tri_yz, fcol_yz = tri[:, :, 1:3][order], fcol[order]

        X, Y, Hh, S, wet = free_surface(w, sp, cx, cy, a.half, floor,
                                        a.surf_cell, hpart)
        # Ground first: its albedo is what the water refracts against, so the
        # riverbed under the flood is the same surface as the dry road beside it.
        if a.legacy_vehicle_shading:
            g_bottom = None
        else:
            g_alb, g_rgh, g_nrm = ground_maps_at(gmaps, X, Y)
            g_bottom = g_alb
        wrgb, foam, We = shade_water(X, Y, Hh, S, floor, view, sky, sun,
                                     hpart, a.exposure, bottom_rgb=g_bottom)
        # foam and We reported over WET cells only; averaging over dry ground
        # would silently dilute both and make the diagnostic unreadable.
        foam_stats.append(float(foam[wet].mean()) if wet.any() else 0.0)
        we_stats.append(float(np.nanpercentile(We[wet], 99.0)) if wet.any() else 0.0)
        # Cut the sheet out of the hull footprint: the vehicle displaces the water.
        # Shading is computed on the full field first so the cut cannot bias it.
        occ = hull_footprint_mask(vp, X, Y, a.surf_cell)
        drop = occ | ~wet
        wq, wc = surface_quads(X, Y, np.where(wet, Hh, np.nan), wrgb, drop)

        # Ground quads at the floor plane, drawn only where the water is NOT, so
        # the two never z-fight. Under the hull footprint the ground IS drawn:
        # the car sits on the road, and leaving a hole there was what made the
        # old frame read as a hull floating over blank paper.
        gq, gc = [], np.zeros((0, 3), dtype=np.float32)
        if not a.legacy_vehicle_shading:
            grgb = shade_ground(g_alb, g_rgh, g_nrm, view, sky_p, sun, a.exposure)
            Zg = np.full(X.shape, floor, dtype=np.float32)
            gq, gc = surface_quads(X, Y, Zg, grgb, wet & ~occ)

        fig = plt.figure(figsize=(a.width / a.dpi, a.height / a.dpi), dpi=a.dpi)
        if a.hero:
            # HERO: the 3D view only, at full canvas. Same scene, same camera,
            # same caption block. The diagnostic panels are dropped, NOT the
            # caption: a render that loses its provenance line is exactly the
            # artifact this project has already been burned by.
            gs = GridSpec(1, 1, figure=fig, left=0.03, right=0.97,
                          top=0.955, bottom=0.20)
        else:
            gs = GridSpec(3, 2, figure=fig, width_ratios=[1.12, 1.0],
                          height_ratios=[1.0, 0.55, 0.62],
                          left=0.02, right=0.975, top=0.945, bottom=0.235,
                          wspace=0.13, hspace=0.55)

        # ---- oblique 3D: shaded water sheet + solid hull ---------------------
        ax = (fig.add_subplot(gs[0, 0], projection="3d") if a.hero
              else fig.add_subplot(gs[:, 0], projection="3d"))
        # D1: ONE collection carrying water quads AND hull faces, so the painter's
        # sort is over all faces together instead of between two artists.
        polys = gq + wq + list(tri3)
        pcol = np.vstack([c for c in (gc, wc, fcol3) if len(c)])
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
        if a.hero:
            # A 3D axes reserves ~20 percent margin around its box, and this
            # scene's box is a flat slab (7.8 x 7.8 x ~1.5 m), so the default
            # leaves most of a hero canvas empty. Overscan the axes rectangle.
            ax.set_position([-0.06, 0.13, 1.12, 0.90])

        # HERO drops the three diagnostic panels. The caption block below
        # is NOT dropped: provenance travels with the image.
        if not a.hero:
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
            "free_surface": "per-column max-z of water particles, gaussian sigma=1 "
                            "cell; warpmpm has no free-surface field",
            "fresnel": "Schlick, F0=%.4f (IOR %.3f)" % (F0_WATER, IOR),
            "absorption": "Beer-Lambert sigma_rgb=%s 1/m, exaggerated %.1fx for "
                          "legibility" % (SIGMA_RGB.tolist(), VIS_GAIN),
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
            "surface_smoothing": "normalised convolution over WET cells only, "
                                 "smoothing length ~2x particle radius "
                                 "(Loschner/splashsurf, report b0d2664f item 13). "
                                 "Dry columns are DROPPED, not floor-filled; "
                                 "floor-filling was defect D2.",
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
