"""Watertight road cross-section as a solid mesh, for use as an MPM SDF collider.

WHY A MESH AND NOT PLANES. The canonical scene is one infinite frictional plane
(blocker B1). warpmpm's add_plane is infinite by construction, so it cannot
express a road that has edges, and two tilted planes do NOT give a crowned road:
a slip plane pushes material to the positive side of its normal, so the union of
two opposed tilted planes is the MAXIMUM of the two, which is a valley, not a
crown. A crown needs the minimum, which infinite planes cannot express at all.

add_box (solver.py:224) is axis-aligned and volumetric, so it can make a kerb but
not a cross-slope.

What CAN express a real road is add_sdf_collider (solver.py:324), which takes a
watertight mesh as a signed distance field with a friction and a surface mode.
That is what this module builds. Nothing here needs an engine change.

THE LONGITUDINAL GRADE IS DELIBERATELY NOT IN THE MESH. It goes in as tilted
gravity (openchannel_bc.tilted_gravity), which keeps the road prismatic along x,
keeps the SDF small, and makes the grade exact rather than discretised. That is
the standard chute decomposition and it is the one the engine's own periodic_x
docstring names.

CROSS-SECTION, from the centreline outward, each half mirrored:
    crown            the high point on the centreline
    carriageway      falling at `cross_slope` (fraction, not percent)
    gutter           a dish that the cross-slope drains into
    kerb             a vertical rise
    verge            flat, above the kerb

PARAMETER PROVENANCE, stated because this project does not accept unsourced
numbers: the DEFAULTS here are conventional highway values (2 percent cross
slope, 0.15 m kerb, 3.5 m lanes) and are NOT yet traced to a primary standard in
this repo's citation base. They are design inputs, not measurements, and any
figure that turns on them must say so. `analysis/research_index.py --query
"road cross slope"` returns nothing, so the corpus does not currently support
them either.
"""

from __future__ import annotations

import numpy as np

__all__ = ["road_profile", "road_solid", "seed_film"]


def road_profile(y, width_total, carriageway=4.0, cross_slope=0.02,
                 gutter_depth=0.05, gutter_width=0.5, kerb_height=0.15,
                 crown_z=0.0):
    """Road surface height z(y) for the cross-section described in the module docstring.

    y may be an array. Returns z at the same shape. The centreline sits at
    width_total/2 and carries `crown_z`; everything else is below it, so the
    crown is the maximum of the profile by construction.
    """
    y = np.asarray(y, dtype=np.float64)
    yc = 0.5 * width_total
    r = np.abs(y - yc)                      # distance from the crown
    half_road = 0.5 * carriageway
    z = np.empty_like(r)

    # 1. carriageway: falls away from the crown at the cross slope
    on_road = r <= half_road
    z[on_road] = crown_z - cross_slope * r[on_road]

    edge_z = crown_z - cross_slope * half_road          # height at the road edge

    # 2. gutter: a dish from the road edge down to gutter_depth and back up
    g0, g1 = half_road, half_road + gutter_width
    in_gutter = (r > g0) & (r <= g1)
    t = (r[in_gutter] - g0) / max(gutter_width, 1e-9)
    z[in_gutter] = edge_z - gutter_depth * np.sin(np.pi * t) ** 0.7

    # 3. kerb face, then verge. The kerb is a near-vertical rise; a true vertical
    #    face would make degenerate triangles, so it is one cell wide.
    kerb_w = 0.06
    k0, k1 = g1, g1 + kerb_w
    on_kerb = (r > k0) & (r <= k1)
    z[on_kerb] = edge_z + kerb_height * (r[on_kerb] - k0) / kerb_w

    on_verge = r > k1
    z[on_verge] = edge_z + kerb_height
    return z


def road_solid(length, width_total, z_base, n_y=160, n_x=2, **profile_kw):
    """Watertight solid whose top face is the road profile, extruded along x.

    Returns (vertices, faces). The solid is closed: top surface, flat base at
    z_base, four side walls. n_x=2 is enough because the section does not vary
    along x, and a small face count keeps the SDF build cheap.

    Watertightness is checked by the caller; it is not optional, because an open
    mesh has no interior and the SDF sign is then undefined.
    """
    xs = np.linspace(0.0, length, n_x)
    ys = np.linspace(0.0, width_total, n_y)
    zs = road_profile(ys, width_total, **profile_kw)
    if not (zs.min() > z_base):
        raise ValueError("z_base %.4f is not below the whole profile (min %.4f)"
                         % (z_base, zs.min()))

    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Ztop = np.broadcast_to(zs[None, :], X.shape)
    top = np.stack([X, Y, Ztop], -1).reshape(-1, 3)
    bot = np.stack([X, Y, np.full_like(X, z_base)], -1).reshape(-1, 3)
    verts = np.vstack([top, bot])
    nt = len(top)

    def qid(i, j):
        return i * n_y + j

    faces = []
    for i in range(n_x - 1):
        for j in range(n_y - 1):
            a, b, c, d = qid(i, j), qid(i + 1, j), qid(i + 1, j + 1), qid(i, j + 1)
            faces += [[a, b, c], [a, c, d]]                       # top, +z out
            A, B, C, D = a + nt, b + nt, c + nt, d + nt
            faces += [[A, C, B], [A, D, C]]                       # base, -z out
    for j in range(n_y - 1):                                      # x = 0 and x = L walls
        a, d = qid(0, j), qid(0, j + 1)
        faces += [[a, d + nt, d], [a, a + nt, d + nt]]
        b, c = qid(n_x - 1, j), qid(n_x - 1, j + 1)
        faces += [[b, c, c + nt], [b, c + nt, b + nt]]
    for i in range(n_x - 1):                                      # y = 0 and y = W walls
        a, b = qid(i, 0), qid(i + 1, 0)
        faces += [[a, b, b + nt], [a, b + nt, a + nt]]
        d, c = qid(i, n_y - 1), qid(i + 1, n_y - 1)
        faces += [[d, c + nt, c], [d, d + nt, c + nt]]
    verts = verts.astype(np.float64)
    faces = np.asarray(faces, dtype=np.int64)

    # NORMALISE THE WINDING, and do not skip this. A closed mesh with inward or
    # mixed winding is still WATERTIGHT, so is_watertight does not catch it: the
    # first build here was watertight with volume -28.36 m3, and a global flip
    # then gave positive volume with is_winding_consistent still False. An SDF
    # built from either would have a wrong or ambiguous sign, and the solver would
    # treat the inside of the embankment as free space and drive water into it.
    #
    # Deriving every side-wall winding by hand is exactly the kind of sign bookkeeping
    # that fails silently, so it is delegated to trimesh, which this project already
    # depends on for the vehicle hulls (sim_standing.py imports it). fix_normals
    # orients from the volume sign, so it needs the mesh to be closed, which it is.
    import trimesh
    m = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    m.fix_normals()
    if not m.is_watertight:
        raise RuntimeError("road solid is not watertight; the SDF sign is undefined")
    if m.volume <= 0 or not m.is_winding_consistent:
        raise RuntimeError("road solid winding could not be normalised (volume %.4f, "
                           "consistent %s)" % (m.volume, m.is_winding_consistent))
    return np.asarray(m.vertices, dtype=np.float64), np.asarray(m.faces, dtype=np.int64)


def seed_film(length, width_total, depth, h, x_lo=None, x_hi=None, rng=None,
              **profile_kw):
    """Water as a film of uniform DEPTH following the road surface, not a flat slab.

    A flat slab over a crowned road is already half the answer: it would start
    deep at the gutters and dry at the crown before a single step is taken. A
    uniform film starts the run with no drainage pattern at all, so any gutter
    concentration that appears is something the simulation produced rather than
    something it was handed.
    """
    rng = rng or np.random.default_rng(0)
    x_lo = 0.0 if x_lo is None else x_lo
    x_hi = length if x_hi is None else x_hi
    xs = np.arange(x_lo + 0.5 * h, x_hi - 0.5 * h, h)
    ys = np.arange(0.5 * h, width_total - 0.5 * h, h)
    zs_road = road_profile(ys, width_total, **profile_kw)
    pts = []
    for j, y in enumerate(ys):
        col = np.arange(zs_road[j] + 0.5 * h, zs_road[j] + depth, h)
        if not len(col):
            continue
        XX, ZZ = np.meshgrid(xs, col, indexing="ij")
        blk = np.stack([XX, np.full(XX.shape, y), ZZ], -1).reshape(-1, 3)
        pts.append(blk)
    p = np.concatenate(pts)
    p = p + rng.uniform(-0.2 * h, 0.2 * h, p.shape)
    # The jitter moves y as well as z, and the road is not flat in y. On the kerb
    # face the profile rises 0.15 m over 0.06 m, a gradient of 2.5, so a y-jitter of
    # 0.2h shifts the surface under a particle by more than the 0.5h clearance it was
    # seeded with, and it lands INSIDE the solid. Re-evaluate the surface at the
    # jittered y and drop those. Dropping rather than lifting, because lifting would
    # stack them into an artificial ridge along the kerb, which is precisely the
    # drainage feature the run is supposed to produce rather than be handed.
    keep = p[:, 2] > road_profile(p[:, 1], width_total, **profile_kw) + 0.05 * h
    return p[keep].astype(np.float32)


def _selftest():
    W, L, ZB = 6.0, 8.0, -0.6
    ys = np.linspace(0, W, 601)
    z = road_profile(ys, W)
    yc = 0.5 * W
    # 1. the crown is the maximum OF THE CARRIAGEWAY and sits on the centreline.
    #    Not of the whole section: in a real urban cross-section the kerb and the
    #    footway behind it stand ABOVE the carriageway crown, and they do here too
    #    (kerb 0.15 m against a crown-to-edge fall of 0.02 * 2.0 = 0.04 m). The
    #    first version of this check asserted the GLOBAL maximum and failed on
    #    correct geometry, which is the right way round for a test to fail.
    car = np.abs(ys - yc) <= 2.0
    assert abs(ys[car][int(np.argmax(z[car]))] - yc) < 0.02, ys[car][int(np.argmax(z[car]))]
    assert z.max() > z[car].max(), "kerb and verge should stand above the crown"
    # 2. the carriageway really falls at the cross slope
    z_edge = road_profile(np.array([yc + 2.0]), W)[0]
    assert abs((z[np.argmin(np.abs(ys - yc))] - z_edge) - 0.02 * 2.0) < 1e-6
    # 3. the gutter is BELOW the road edge, which is the whole point of a gutter
    z_gut = z[(np.abs(ys - yc) > 2.0) & (np.abs(ys - yc) < 2.5)].min()
    assert z_gut < z_edge - 0.03, (z_gut, z_edge)
    # 4. the kerb is above the road edge by kerb_height
    z_verge = road_profile(np.array([yc + 2.9]), W)[0]
    assert abs((z_verge - z_edge) - 0.15) < 1e-9, (z_verge, z_edge)
    # 5. the profile is symmetric about the crown
    assert np.allclose(road_profile(ys, W), road_profile(W - ys, W), atol=1e-12)

    v, f = road_solid(L, W, ZB, n_y=120)
    import trimesh
    m = trimesh.Trimesh(vertices=v, faces=f, process=False)
    assert m.is_watertight, "road solid is not watertight; the SDF sign would be undefined"
    assert m.volume > 0, m.volume
    # 6b. and the winding is outward, not merely closed: a sign-inverted SDF
    #     would push water INTO the embankment and still pass is_watertight
    assert m.is_winding_consistent, "inconsistent winding"
    assert abs(m.bounds[0][2] - ZB) < 1e-9 and abs(m.bounds[1][1] - W) < 1e-9

    film = seed_film(L, W, 0.30, 0.05)
    zr = road_profile(film[:, 1], W)
    # 6. every seeded particle is ABOVE the road it sits on, none inside the solid
    assert (film[:, 2] > zr - 1e-6).all(), "film particle seeded inside the road"
    assert (film[:, 2] < zr + 0.31).all()
    # 7. a uniform film means the depth does not depend on y at t=0
    import collections
    per_y = collections.defaultdict(list)
    for yy, zz, zzr in zip(film[:, 1], film[:, 2], zr):
        per_y[round(float(yy), 3)].append(zz - zzr)
    tops = np.array([max(v) for v in per_y.values()])
    assert tops.std() < 0.02, ("film is not uniform in depth at t=0", tops.std())
    print("road_geometry selftest: 8 checks PASS (crown, camber, gutter, kerb, "
          "symmetry, watertight, uniform film)")


if __name__ == "__main__":
    _selftest()
