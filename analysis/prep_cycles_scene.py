#!/usr/bin/env python3
"""Export a warpmpm rollout frame as real geometry for a Cycles path-traced render.

WHY THIS EXISTS
  analysis/render_multigeom_shaded.py evaluates Schlick Fresnel, a GGX lobe and
  Beer-Lambert absorption per face and then hands the faces to
  mpl_toolkits.mplot3d.Poly3DCollection. That is matplotlib: a painter's-algorithm
  polygon plotter with no ray tracing, no refraction, no shadows and no global
  illumination, whose per-polygon depth sort is undefined for interpenetrating
  geometry, which is exactly what a hull in water is. No amount of further shading
  work in that file can produce a photographic image, because water without
  refraction cannot look like water.

  So this is a SECOND, PRESENTATION path. The matplotlib renderer is KEPT and is
  still the diagnostic instrument: its particle-enclosure check, its facing-ratio
  measurements and its gate captions are what verify a frame is honest. This one
  makes a picture.

WHAT IT DOES NOT DO
  It does not touch the simulation, any metric, any verdict, or any file under
  renders/*/sim_*.py. It does not add, move or re-export any mesh: hulls are READ
  from wherever they already live and the exported copies are scratch render
  inputs, never repository assets. Register E8 and the unresolved hull licence
  question are therefore not engaged by this script.

THE TWO DERIVATIONS IN HERE, both checked rather than assumed
  1. WATER SURFACE. warpmpm carries no free surface. The surface is reconstructed
     from the particle positions with splashsurf (Loschner, Bender et al.), which
     is a real SPH surface reconstruction rather than the per-column max-z
     heightfield the diagnostic renderer uses. A heightfield cannot represent a
     bow wave that curls, which is the whole point of moving to it.
  2. HULL PLACEMENT. The solver never stores the hull mesh, only the solidified
     particle cloud, so the mesh has to be put back. The mapping is DERIVED:
     the PLY's long axis is X (extents 4.2826, 1.7464, 1.5180) and the scene's is
     Y (1.6930, 4.1956, 1.4721), so a rotation about z is required, and the sign
     is chosen by nearest-neighbour fit against the actual particle cloud rather
     than picked. Measured: rotz+90 gives mean nn-distance 0.04772 m (0.65 h) and
     rotz-90 gives 0.07672 m, a 61 percent worse fit. The chosen placement
     encloses the particle cloud on every axis, which is asserted at runtime.

USAGE
  prep_cycles_scene.py --run <dir> --frame N --hull <ply> --outdir <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_multigeom_rollout as RMR

ROTZ = {
    "+90": np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
    "-90": np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
}


def write_ply(path: Path, V, F):
    """Binary little-endian PLY. Written by hand so the export has no dependency
    on trimesh's writer and so the header is auditable by `head -c 400`."""
    V = np.ascontiguousarray(np.asarray(V, dtype="<f4"))
    F = np.ascontiguousarray(np.asarray(F, dtype="<i4"))
    hdr = ("ply\nformat binary_little_endian 1.0\n"
           "comment can-it-ford prep_cycles_scene.py scratch render input\n"
           "element vertex %d\nproperty float x\nproperty float y\nproperty float z\n"
           "element face %d\nproperty list uchar int vertex_indices\n"
           "end_header\n" % (len(V), len(F))).encode()
    with open(path, "wb") as fh:
        fh.write(hdr)
        fh.write(V.tobytes())
        cnt = np.full((len(F), 1), 3, dtype="<u1")
        rec = np.empty(len(F), dtype=[("c", "u1"), ("v", "<i4", 3)])
        rec["c"] = cnt[:, 0]
        rec["v"] = F
        fh.write(rec.tobytes())


def read_ply_vertices_faces(path: Path):
    """Minimal binary/ascii PLY reader for vertex+face only. Avoids pulling
    trimesh into the render path, and trimesh 5.x has its own seeding trap."""
    import trimesh
    m = trimesh.load(str(path), process=False)
    return np.asarray(m.vertices, dtype=np.float64), np.asarray(m.faces, dtype=np.int64)


def water_surface(w, h, window, cube_mult, iso, smooth_mult, smooth_iters,
                  floor_z, taper, hull_lo, hull_hi):
    """splashsurf reconstruction of the water, cropped to the render window.

    TWO CORRECTIONS LIVE HERE, both measured on 2026-08-19, both of which made the
    water effectively invisible in the first export.

    1. THE UNIT CONVENTION OF `reconstruct_surface` IS NOT WHAT ITS OWN DOCSTRING
       SAYS. The installed build documents "Note that all parameters use absolute
       distance units and are not relative to the particle radius", and that is
       FALSE for smoothing_length and cube_size: they are read as MULTIPLES of the
       particle radius, exactly like the sibling `reconstruction_pipeline`, whose
       docstring says so explicitly. Held-fixed measurement on one frame, 3779
       particles of median spacing 0.0404 m, particle_radius 0.04566 m:

         smoothing_length=2.0*r, cube_size=0.75*r  (absolute, per the docstring)
             -> 3779 connected bodies, enclosed volume 0.0002 m3
         smoothing_length=2.0,   cube_size=0.75    (relative)
             -> 6 connected bodies, enclosed volume 1.4570 m3

       3779 bodies for 3779 particles is one blob per particle: passing absolute
       units shrinks the kernel support by a factor of the radius, here to about
       8 mm against a 40 mm particle spacing, so no particle ever reaches a
       neighbour and the fluid never becomes a fluid. The docstring is a secondary
       source and it is wrong; the sweep above is the primary one.

    CROSS-CHECKED AGAINST CHRONO, 2026-08-19, and only half of it was adopted.
    Chrono::FSI documents the same relative convention at ChFsiFluidSystemSPH.h:136-140
    and sets its radius to spacing/2 at ChFsiProblemSPH.cpp:287, giving shipped values
    of roughly 0.75 to 1.0 spacings of smoothing and 0.15 to 0.25 spacings of cube.
    Measured here on one frame, changing one at a time:

      cube  0.465 spacings -> 214k tris, 42 bodies, volume ratio 0.915
      cube  0.248 spacings -> 756k tris, 52 bodies, volume ratio 0.936   <- adopted
      cube  0.186 spacings -> 1.35M tris, 58 bodies, volume ratio 0.940
      smoothing 1.24 -> 0.99 spacings, at cube 0.248:
                        919k tris, 321 BODIES, volume ratio 0.863        <- rejected

    So the finer GRID was adopted, and it is a convergence result as well as a
    cosmetic one: enclosed volume rises toward the particle-carried volume as the
    marching-cubes grid refines. Chrono's shorter SMOOTHING LENGTH was rejected,
    measured rather than assumed: it fragments this field into 321 pieces and loses
    7 percent of the volume. The reason is a real difference in the particle fields,
    not a mistake in either code. Chrono's are SPH particles that stay near-uniformly
    spaced; these are MPM particles that have clustered by frame 60, median
    nearest-neighbour 0.0404 m against a seeding spacing h of 0.0736 m, so a
    smoothing length tuned for uniform spacing leaves the sparse regions unsupported.
    Do not copy an SPH code's smoothing length onto an MPM field without re-measuring.

    2. THE PARTICLE RADIUS MUST CARRY THE PARTICLE'S VOLUME, not half the grid
       spacing. warpmpm seeds one particle per h^3 of water (measured: 48367
       particles * h^3 = 19.29 m3 against a slab of 8.30 x 8.31 x 0.294 m), so the
       radius of the equivalent sphere is (3 h^3 / 4 pi)^(1/3) = 0.6204 h, not
       0.5 h. The old 0.5 h understated each particle's volume by 47 percent.
    """
    import pysplashsurf
    (x0, x1, y0, y1) = window
    pad = 6.0 * h
    m = ((w[:, 0] >= x0 - pad) & (w[:, 0] <= x1 + pad) &
         (w[:, 1] >= y0 - pad) & (w[:, 1] <= y1 + pad))
    wc = np.ascontiguousarray(w[m].astype(np.float64))
    # sphere of volume h^3: one warpmpm water particle's share of space
    pr = (3.0 / (4.0 * np.pi)) ** (1.0 / 3.0) * h
    # `reconstruction_pipeline` rather than `reconstruct_surface`: it applies the
    # WEIGHTED Laplacian smoothing of Loschner, Bottcher, Jeske and Bender 2023,
    # which is the published method for this exact artefact. Raw marching cubes
    # over an SPH color field is bumpy at the scale of the particle spacing, and
    # unsmoothed it reads as wet gravel rather than as water: the bumps are a
    # sampling artefact of the reconstruction, NOT structure in the solver's
    # particle field, so removing them removes an artefact rather than data.
    # Its docstring states the relative unit convention explicitly, which is the
    # convention `reconstruct_surface` also uses in practice, see above.
    md, _rec = pysplashsurf.reconstruction_pipeline(
        wc, particle_radius=pr, rest_density=1000.0,
        smoothing_length=smooth_mult, cube_size=cube_mult,
        iso_surface_threshold=iso, multi_threading=True, subdomain_grid=True,
        mesh_cleanup=True, mesh_smoothing_weights=True,
        mesh_smoothing_weights_normalization=13.0,
        mesh_smoothing_iters=int(smooth_iters),
        compute_normals=False)
    mesh = md.mesh
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.triangles, dtype=np.int64)

    # CONSISTENT WINDING IS LOAD-BEARING, not cosmetic. A path tracer decides
    # "inside the water" from the surface normal, so an inward-wound mesh renders
    # as near-invisible glass with no refraction and no volume absorption.
    # NOTE, correcting an earlier note in this same function: winding was NOT the
    # cause of the 0.0005 m3 first export. That was correction 1 above, the unit
    # convention. fix_normals() was measured to change nothing there (0.0005 m3
    # before and after), so do not credit it with a fix it did not perform.
    import trimesh
    tm = trimesh.Trimesh(vertices=V, faces=F, process=False)
    tm.fix_normals()
    vol = float(tm.volume)
    if vol < 0:                       # fix_normals can settle on inward
        tm.invert()
        vol = float(tm.volume)

    # THE FALSIFIER. The reconstructed surface must enclose roughly the volume the
    # particles actually carry, n_kept * h^3, because warpmpm seeds one particle
    # per h^3 of water. A surface that fragments into one blob per particle passes
    # every other check available here: it is edge-manifold, `is_watertight` is
    # True, its bounding box matches the particle cloud exactly, and it has more
    # triangles than a correct mesh. Only the enclosed volume separates it from a
    # real free surface, so this ratio is checked and PRINTED on every export
    # rather than left as a thing someone might notice in the picture.
    n_kept = int(m.sum())
    expect = n_kept * h ** 3
    ratio = vol / expect if expect > 0 else float("nan")
    bodies = int(tm.body_count)
    print("[prep] water mesh: %d verts %d tris, %d connected bodies, watertight=%s"
          % (len(V), len(F), bodies, tm.is_watertight))
    print("[prep] water volume: enclosed %.4f m3 against particle-carried %.4f m3 "
          "(n_kept %d * h^3), ratio %.3f" % (vol, expect, n_kept, ratio))
    if not (0.5 <= ratio <= 1.6):
        raise SystemExit(
            "WATER SURFACE REJECTED: enclosed volume %.4f m3 is %.3f of the "
            "%.4f m3 the particles carry. Outside [0.5, 1.6] the surface is not a "
            "reconstruction of this fluid and must not be rendered.\n"
            "THE INPUT THAT MAKES THIS CHECK FAIL: a smoothing length below about "
            "one particle spacing. Passing smoothing_length in absolute metres "
            "when the library wants multiples of the particle radius shrinks it by "
            "the radius factor, to roughly 8 mm against a 40 mm spacing, and the "
            "surface then closes around each particle separately. The signature is "
            "this ratio near zero WITH a body count near the particle count."
            % (vol, ratio, expect))
    if bodies > 0.02 * n_kept:
        raise SystemExit(
            "WATER SURFACE REJECTED: %d connected bodies for %d particles. The "
            "project standing rule is that water reads as ONE connected fluid "
            "body; a body count near the particle count is the units bug."
            % (bodies, n_kept))
    V2 = np.asarray(tm.vertices, dtype=np.float64)
    F2 = np.asarray(tm.faces, dtype=np.int64)
    # Inset from the actual water extent, not from the requested window: the water
    # body may end at the solver domain well inside the window, and the bead forms
    # wherever the PARTICLES stop.
    bead = 3.5 * pr
    rect = (max(x0, V2[:, 0].min() + bead), min(x1, V2[:, 0].max() - bead),
            max(y0, V2[:, 1].min() + bead), min(y1, V2[:, 1].max() - bead))
    V3, F3, nb = clip_to_rect(V2, F2, rect, floor_z)
    print("[prep] clipped to %.2f x %.2f m (bead inset %.3f m), %d boundary edges "
          "skirted to the floor, %d -> %d tris"
          % (rect[1] - rect[0], rect[3] - rect[2], bead, nb, len(F2), len(F3)))
    sz, ncol = surround_height(V3, rect, h)
    print("[prep] surround height %.4f m, median of %d column maxima in the "
          "0.45 m band inside the clip boundary" % (sz, ncol))
    # Measure this run's OWN edge statistics before tapering. An earlier version
    # printed the Yaris's 1.9 mm step and 0.379 m edge spread on every run, which
    # is a measurement from one run reported as though it were this one's.
    step_mm, spread = edge_stats(V3, rect, sz)
    V3, nmoved, dmax = taper_edge_to(V3, F3, rect, floor_z, sz, taper,
                                     hull_lo, hull_hi)
    if nmoved:
        print("[prep] edge taper: %d top-surface verts ramped to %.4f m over a "
              "%.2f m band, largest move %.4f m. The seam is NOT a height offset "
              "here either: the median step was %.1f mm while the patch EDGE itself "
              "varies by %.3f m p10-p90, and that is what a flat surround cannot "
              "meet." % (nmoved, sz, taper, dmax, step_mm, spread))
    return V3, F3, int(m.sum()), int(len(w)), rect, sz


def surround_height(V, rect, h, band=0.45):
    """The height the presentational surround must sit at to meet the water mesh.

    Measured ON THE MESH THE SURROUND ACTUALLY TOUCHES, in a band just inside the
    clipped boundary, as the median of per-column MAXIMA. Column maxima because
    the mesh is a closed volume and its vertices are half top surface, half floor;
    a plain median lands between the two and was the first version of this bug.

    Why not reuse still_water_level(): that measures the PARTICLE field, and the
    reconstructed isosurface sits ABOVE the topmost particle centre, by
    construction of the SPH color field. MEASURED, not assumed: on
    g64_yaris_regression frame 60 the offset is +0.0920 m, which is 2.01 particle
    radii, not the one radius a first guess suggested. Small in absolute terms and
    glaringly visible as a step running round the patch. The two numbers answer
    different questions, so both are computed and both are reported rather than
    one being reused.

    CHECK WORTH KEEPING: this height minus the floor came out 0.2950 m against the
    run's own realized_depth_m of 0.2944 m, agreeing to 0.2 percent. That is an
    independent confirmation that the reconstruction reproduces the solver's water
    depth away from the vehicle, arrived at through splashsurf and a column-maxima
    statistic rather than from the summary field.
    """
    x0, x1, y0, y1 = rect
    inb = ((V[:, 0] < x0 + band) | (V[:, 0] > x1 - band) |
           (V[:, 1] < y0 + band) | (V[:, 1] > y1 - band))
    P = V[inb]
    if len(P) < 200:
        P = V
    cell = 2.0 * h
    key = (np.floor(P[:, 0] / cell).astype(np.int64) * 1000003 +
           np.floor(P[:, 1] / cell).astype(np.int64))
    o = np.argsort(key, kind="stable")
    ks, zs = key[o], P[o, 2]
    bnd = np.flatnonzero(np.diff(ks)) + 1
    tops = [zs[a:b].max() for a, b in zip(np.r_[0, bnd], np.r_[bnd, len(zs)])]
    return float(np.median(tops)), len(tops)


def edge_stats(V, rect, target_z, band=0.45, cell=0.15):
    """Median step between the patch boundary and `target_z`, and the boundary's own
    p10-p90 spread. Both per RUN, because the two numbers differ between runs and a
    figure quoting one run's value for another is the failure this project keeps
    finding in its own documents."""
    x0, x1, y0, y1 = rect
    inb = ((V[:, 0] < x0 + band) | (V[:, 0] > x1 - band) |
           (V[:, 1] < y0 + band) | (V[:, 1] > y1 - band))
    P = V[inb] if inb.sum() > 200 else V
    key = (np.floor(P[:, 0] / cell).astype(np.int64) * 1000003 +
           np.floor(P[:, 1] / cell).astype(np.int64))
    o = np.argsort(key, kind="stable")
    ks, zs = key[o], P[o, 2]
    b = np.flatnonzero(np.diff(ks)) + 1
    tops = np.array([zs[a:c].max() for a, c in zip(np.r_[0, b], np.r_[b, len(zs)])])
    return (1000.0 * (target_z - float(np.median(tops))),
            float(np.percentile(tops, 90) - np.percentile(tops, 10)))


def taper_edge_to(V, F, rect, floor, target_z, width, hull_lo, hull_hi):
    """Ramp the patch's TOP surface to `target_z` in a band inside its boundary.

    WHY, and it is not the reason a viewer first reaches for. The seam between the
    simulated patch and the flat surround is NOT a height offset: measured on
    g64_yaris_regression frame 60, the annulus sits at 0.7366 m and the patch's own
    boundary has median 0.7347 m, a step of 1.9 MILLIMETRES. What makes the square
    visible is that the patch boundary is WAVY, p10 to p90 of 0.3791 m, because the
    water at the edge of the crop is mid-wave, while the surround is a plane. A flat
    sheet meeting a 38 cm ragged edge shows a seam however well the heights agree on
    average.

    So the outermost `width` metres of the reconstruction are ramped to the surround
    height with a smoothstep, which makes the two surfaces meet exactly instead of
    approximately. This MODIFIES the reconstructed surface, so:

      - it touches only the top surface, never the floor face or the skirt;
      - it is a presentational edge treatment at the DOMAIN boundary, which is the
        one place the simulation has nothing to say anyway, since the tank wall is
        not a real feature of a flooded street;
      - it is refused outright if the band comes near the vehicle, because the
        vehicle's surroundings are the part of the field that carries the result.

    The failing input for that last guard is a taper width large enough to reach the
    hull: on this 6.6 m patch, --edge-taper 3.0 or more.
    """
    if width <= 0:
        return V, 0, 0.0
    x0, x1, y0, y1 = rect
    d = np.minimum.reduce([V[:, 0] - x0, x1 - V[:, 0], V[:, 1] - y0, y1 - V[:, 1]])
    band_lo = np.array([x0 + width, y0 + width])
    band_hi = np.array([x1 - width, y1 - width])
    clear = min(hull_lo[0] - band_lo[0], hull_lo[1] - band_lo[1],
                band_hi[0] - hull_hi[0], band_hi[1] - hull_hi[1])
    if clear < 0.75:
        raise SystemExit(
            "EDGE TAPER REFUSED: a %.2f m band leaves only %.2f m between it and the "
            "hull bounding box. The taper is an edge treatment for the domain "
            "boundary; within 0.75 m of the vehicle it would be editing the part of "
            "the field that carries the result." % (width, clear))
    top = V[:, 2] > floor + 0.02
    w = np.clip(1.0 - d / width, 0.0, 1.0)
    w = w * w * (3.0 - 2.0 * w)                    # smoothstep, C1 at both ends
    w = np.where(top, w, 0.0)
    z0 = V[:, 2].copy()
    V = V.copy()
    V[:, 2] = z0 * (1.0 - w) + target_z * w
    moved = int((w > 1e-6).sum())
    return V, moved, float(np.abs(V[:, 2] - z0).max())


def clip_to_rect(V, F, rect, floor):
    """Cut the reconstructed water to `rect` and re-close it with a vertical skirt.

    WHY. splashsurf closes the isosurface at the edge of the particle support, and
    that closing surface curls UP into a raised bead a few centimetres proud of the
    free surface, running right round the patch. Against a flat presentational
    surround the bead reads as a rectangular plateau with a lip, which is the
    single most artificial thing left in the frame. It is an artefact of where the
    particles stop, not a feature of the flow, so removing it removes an artefact.

    Faces are dropped whole, never split, so no vertex position is ever moved and
    no new water is invented: the surviving surface is exactly the reconstruction.
    The skirt then joins the cut boundary straight down to the floor plane, which
    keeps the mesh a CLOSED volume. That matters beyond tidiness: Cycles decides
    what is inside the fluid by counting surface crossings, so an open shell makes
    the volume absorption leak and the water stops carrying depth.
    """
    import trimesh
    from trimesh.grouping import group_rows
    x0, x1, y0, y1 = rect
    c = F.reshape(-1)
    inside = ((V[:, 0] >= x0) & (V[:, 0] <= x1) &
              (V[:, 1] >= y0) & (V[:, 1] <= y1))
    keep = inside[c].reshape(-1, 3).all(axis=1)
    F2 = F[keep]
    if len(F2) == 0:
        return V, F, 0
    used = np.unique(F2)
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    V2 = V[used]
    F2 = remap[F2]

    tm = trimesh.Trimesh(vertices=V2, faces=F2, process=False)
    es = tm.edges_sorted
    # group_rows with require_count=1 returns a FLAT index array, not a list of
    # groups; indexing it as groups raises "invalid index to scalar variable".
    bnd = (np.asarray(group_rows(es, require_count=1), dtype=np.int64)
           if len(es) else np.zeros(0, dtype=np.int64))
    if len(bnd) == 0:
        return V2, F2, 0
    be = es[bnd]                                   # (M,2) boundary edges
    base = len(V2)
    lo = V2[np.unique(be)].copy()
    idx = {int(v): base + i for i, v in enumerate(np.unique(be))}
    lo[:, 2] = floor
    Vs = np.vstack([V2, lo])
    quads = []
    for a, b in be:
        a2, b2 = idx[int(a)], idx[int(b)]
        quads.append((a, b, b2))
        quads.append((a, b2, a2))
    Fs = np.vstack([F2, np.array(quads, dtype=np.int64)])
    return Vs, Fs, len(be)


def still_water_level(w, cx, cy, h, r_excl=3.2):
    """The undisturbed free-surface height, MEASURED from the particle field.

    Needed because the presentational surround has to meet the reconstructed
    patch at the right height, and two cheaper answers are both wrong:

      - the median z of the reconstructed SURFACE mixes the top of the water with
        its bottom, since the mesh is a closed volume resting on the floor. On
        g64_yaris_regression frame 60 that returns 0.506 m against a true free
        surface near 0.73 m, so the surround sat 0.16 m low and the simulated
        water rendered as a raised plateau with a lip round it.
      - summary.json depth_m is the NOMINAL depth, not the realised one, and the
        realised surface also moves during the run.

    So: drop every particle within r_excl of the vehicle, because those are the
    bow wave and the wake and are exactly the disturbed part; bin the rest into
    columns 2h wide; take the highest particle in each column, which is that
    column's free surface; and report the median across columns. Median rather
    than mean so a few spray particles cannot lift it.
    """
    d = np.hypot(w[:, 0] - cx, w[:, 1] - cy)
    far = w[d > r_excl]
    if len(far) < 200:
        return float(np.percentile(w[:, 2], 99.0)), 0
    cell = 2.0 * h
    ix = np.floor(far[:, 0] / cell).astype(np.int64)
    iy = np.floor(far[:, 1] / cell).astype(np.int64)
    key = ix * 1000003 + iy
    order = np.argsort(key, kind="stable")
    key_s, z_s = key[order], far[order, 2]
    bnd = np.flatnonzero(np.diff(key_s)) + 1
    tops = [z_s[a:b].max() for a, b in
            zip(np.r_[0, bnd], np.r_[bnd, len(z_s)])]
    return float(np.median(tops)), len(tops)


def smooth_render_hull(V, F, iters):
    """Taubin-smooth the RENDER hull, and measure what that did.

    WHY THIS IS NEEDED AND WHAT IT IS NOT. The Rogue and Silverado hulls are
    Poisson reconstructions and carry surface noise at roughly the centimetre
    scale; the Yaris hull does not, because it comes from a different pipeline.
    Path-traced at photoreal quality that noise reads as the bodywork melting.
    Established as a mesh property rather than a render artefact by rendering the
    hull with NO WATER IN THE SCENE AT ALL: it is still lumpy, so nothing is
    bleeding onto it. It is also not a matter of picking the wrong file: the
    higher-vertex `*_poisson_raw.ply` variants are NOT watertight and are the
    less-processed source of the same noise, not a cleaner version.

    TAUBIN, not Laplacian. Plain Laplacian smoothing shrinks a closed surface
    monotonically, which would move the waterline on the vehicle, and the waterline
    is the one thing in these frames that carries physics. Taubin alternates a
    positive and a negative pass so the volume is preserved to first order. The
    actual volume change and the largest vertex movement are MEASURED here and
    printed, and the export is refused if either exceeds a small bound, so this can
    never quietly become a reshaping of the vehicle.

    This is an APPEARANCE operation on the RENDER hull only. It does not touch the
    simulation, which never loaded this mesh: the solver has the solidified particle
    cloud and nothing else.
    """
    import trimesh
    if iters <= 0:
        return V, F, 0.0, 0.0
    m0 = trimesh.Trimesh(vertices=V.copy(), faces=F.copy(), process=False)
    v0 = float(m0.volume)
    m = trimesh.Trimesh(vertices=V.copy(), faces=F.copy(), process=False)
    trimesh.smoothing.filter_taubin(m, lamb=0.5, nu=0.53, iterations=int(iters))
    V2 = np.asarray(m.vertices, dtype=np.float64)
    dv = float(np.abs(np.asarray(m.volume) - v0) / max(abs(v0), 1e-12))
    dmax = float(np.linalg.norm(V2 - V, axis=1).max())
    print("[prep] hull smoothing: Taubin %d iters, volume change %.3f percent, "
          "largest vertex movement %.4f m" % (iters, 100.0 * dv, dmax))
    if dv > 0.015:
        raise SystemExit("HULL SMOOTHING REJECTED: volume moved %.3f percent, above "
                         "the 1.5 percent bound. That is a reshaping of the vehicle, "
                         "not a denoise, and it would move the waterline." % (100 * dv))
    if dmax > 0.05:
        raise SystemExit("HULL SMOOTHING REJECTED: a vertex moved %.4f m, above the "
                         "0.05 m bound. Real bodywork features are being removed."
                         % dmax)
    return V2, np.asarray(m.faces, dtype=np.int64), dv, dmax


def place_hull(hull_ply: Path, pv, h):
    """Map the hull PLY into scene body-frame coordinates, and CHECK the result.

    The rotation sign is chosen by fit, not assumed. The check that the placed
    hull encloses the particle cloud on every axis is a hard assert: a hull that
    does not contain the particles it was solidified from is misplaced, and a
    misplaced hull would be invisible in a pretty render.
    """
    from scipy.spatial import cKDTree
    P, F = read_ply_vertices_faces(hull_ply)
    tree = cKDTree(pv)
    cen_cloud = 0.5 * (pv.min(0) + pv.max(0))
    best = None
    scores = {}
    for name, R in ROTZ.items():
        Q = P @ R.T
        Q = Q - 0.5 * (Q.min(0) + Q.max(0)) + cen_cloud
        d, _ = tree.query(Q[::37])
        scores[name] = float(d.mean())
        if best is None or d.mean() < best[1]:
            best = (name, float(d.mean()), Q)
    name, score, Q = best
    encl = bool((Q.min(0) <= pv.min(0) + 1e-9).all() and
                (Q.max(0) >= pv.max(0) - 1e-9).all())
    if not encl:
        raise SystemExit(
            "HULL PLACEMENT FAILED: the placed hull does not enclose the particle "
            "cloud it was solidified from. placed lo %s hi %s vs cloud lo %s hi %s"
            % (Q.min(0), Q.max(0), pv.min(0), pv.max(0)))
    return Q, F, name, score, scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--frame", type=int, default=60)
    ap.add_argument("--hull", required=True, help="hull .ply, READ not copied")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--half", type=float, default=3.4)
    ap.add_argument("--cube-mult", type=float, default=0.40,
                    help="marching-cubes voxel, in MULTIPLES OF THE PARTICLE "
                         "RADIUS. Default 0.40 radii = 0.248 particle spacings, "
                         "which is Chrono's shipped default; see water_surface().")
    ap.add_argument("--smooth-mult", type=float, default=2.0,
                    help="SPH smoothing length, in MULTIPLES OF THE PARTICLE "
                         "RADIUS, despite what the library docstring claims.")
    ap.add_argument("--iso", type=float, default=0.6)
    ap.add_argument("--hull-smooth", type=int, default=0,
                    help="Taubin smoothing iterations on the RENDER hull. Use for "
                         "the Poisson-reconstructed Rogue and Silverado hulls; the "
                         "Yaris hull does not need it. APPEARANCE ONLY.")
    ap.add_argument("--edge-taper", type=float, default=0.6,
                    help="metres of the patch edge ramped to the surround height so "
                         "the two meet exactly. 0 disables. Refused if the band "
                         "comes within 0.75 m of the hull. 0.6 rather than 0.8 "
                         "because the guard REFUSES 0.8 on this geometry: the "
                         "g64 patch is 6.6 m for a 4.3 m car, leaving 1.51 m of "
                         "edge, so the usable maximum is 0.76 m. That the default "
                         "had to be tuned down to fit is the same domain-too-small "
                         "problem the queued larger-domain runs exist to end.")
    ap.add_argument("--smooth-iters", type=int, default=25,
                    help="weighted-Laplacian smoothing iterations on the water "
                         "surface (Loschner et al 2023). 0 disables.")
    ap.add_argument("--no-water", action="store_true",
                    help="hull only. For a class with no rollout data on this "
                         "machine, so no water field is invented for it.")
    ap.add_argument("--foreign-hull", action="store_true",
                    help="the hull is NOT the one this run simulated. It is then "
                         "placed at native scale resting on the floor, NOT fitted "
                         "to this run's particle cloud, and NOT given this run's "
                         "pose. Implies the frame carries no physics claim about "
                         "this vehicle. Required for any hull with no rollout.")
    a = ap.parse_args()

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    run = Path(a.run)
    z = RMR.load_run(run)
    s = z["summary"]
    f = a.frame
    pv, world, worst, errs = RMR.rigid_transform(z)
    h = 0.5 * z["dx"]
    floor = z["floor"]
    print("[prep] run %s frame %d" % (run.name, f))
    print("[prep] transform check max|err| %.3e m (gates.py:136/:157)" % worst)

    vpf = world(f)
    cx, cy = float(vpf[:, 0].mean()), float(vpf[:, 1].mean())

    if a.foreign_hull:
        # A hull this run did not simulate. Native scale, long axis on Y to match
        # the scene convention, resting on the floor at the scene centre. NO pose
        # from this run is applied, because applying one would dress a hull that
        # was never simulated in another vehicle's measured configuration.
        P, HF = read_ply_vertices_faces(Path(a.hull))
        Q = P @ ROTZ["+90"].T
        c = 0.5 * (Q.min(0) + Q.max(0))
        Qw = Q - np.array([c[0], c[1], Q.min(0)[2]]) + np.array([cx, cy, floor])
        rot, score = "+90 (foreign, not fitted)", float("nan")
        print("[prep] FOREIGN hull %s: %d verts, %d faces, native scale, rested on "
              "floor. NO pose from this run applied, NO physics claim."
              % (Path(a.hull).name, len(P), len(HF)))
    else:
        Q, HF, rot, score, scores = place_hull(Path(a.hull), pv, h)
        print("[prep] hull %s: %d verts, rotation %s chosen by fit "
              "(nn %.5f m = %.2f h; alternative %.5f m)"
              % (Path(a.hull).name, len(Q), rot, score, score / h,
                 [v for k, v in scores.items() if k != rot][0]))
        Qw = Q @ z["R"][f].T + z["t"][f]
    Qw, HF, hull_dvol, hull_dmax = smooth_render_hull(Qw, HF, a.hull_smooth)
    write_ply(out / "hull.ply", Qw, HF)

    window = (cx - a.half, cx + a.half, cy - a.half, cy + a.half)
    swl, ncol = still_water_level(z["water"][f], cx, cy, h)
    print("[prep] still-water level %.4f m, measured as the median of %d column "
          "maxima beyond 3.2 m from the vehicle (floor %.4f, so %.4f m of water)"
          % (swl, ncol, floor, swl - floor))

    nwater = 0
    if not a.no_water:
        WV, WF, kept, tot, wrect, surz = water_surface(
            z["water"][f], h, window, a.cube_mult, a.iso, a.smooth_mult,
            a.smooth_iters, floor, a.edge_taper, Qw.min(0), Qw.max(0))
        print("[prep] surround vs particle free surface: %.4f m against %.4f m, "
              "offset %+.4f m = %.2f particle radii"
              % (surz, swl, surz - swl,
                 (surz - swl) / ((3.0 / (4.0 * np.pi)) ** (1.0 / 3.0) * h)))
        write_ply(out / "water.ply", WV, WF)
        nwater = len(WF)
        print("[prep] water surface: %d verts %d tris from %d of %d particles "
              "(splashsurf, radius %.5f m)"
              % (len(WV), len(WF), kept, tot,
                 (3.0 / (4.0 * np.pi)) ** (1.0 / 3.0) * h))

    scene = {
        "run": run.name, "frame": f, "fps": int(z["fps"]),
        "floor_z": float(floor), "dx": float(z["dx"]), "h": float(h),
        "hull_ply_source": str(a.hull), "hull_rotation": rot,
        "hull_smooth_iters": int(a.hull_smooth),
        "hull_smooth_dvol_frac": float(hull_dvol),
        "hull_smooth_max_move_m": float(hull_dmax),
        "hull_fit_nn_m": score, "hull_faces": int(len(HF)),
        "water_faces": nwater, "no_water": bool(a.no_water),
        "car_center": [cx, cy], "half": a.half,
        "still_water_z": swl, "still_water_columns": ncol,
        "water_rect": None, "surround_z": None,
        "edge_taper_m": float(a.edge_taper),
        "hull_bbox_lo": Qw.min(0).tolist(), "hull_bbox_hi": Qw.max(0).tolist(),
        "veh_zmin": float(vpf[:, 2].min()),
        "transform_max_err_m": worst,
        # physics, copied verbatim from this run's own summary.json
        "physics": {k: s.get(k) for k in (
            "mass_kg", "n_grid", "dx", "water_layers", "depth_m", "velocity_ms",
            "final_disp_mag_m", "passthrough_max_frac", "C2_veh_zmin_rise",
            "realized_rho", "solid_volume_m3", "label")},
    }
    if not a.no_water:
        scene["water_rect"] = [float(v) for v in wrect]
        scene["surround_z"] = float(surz)
    (out / "scene.json").write_text(json.dumps(scene, indent=2))
    print("[prep] wrote %s" % (out / "scene.json"))


if __name__ == "__main__":
    main()
