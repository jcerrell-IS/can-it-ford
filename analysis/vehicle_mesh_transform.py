"""Place a real vehicle hull mesh at the SIMULATED rigid-body pose.

SCOPE. Render layer only. Reads an existing rollout.npz and an existing .ply.
Computes no force, changes no verdict, touches no solver code.

WHY THIS EXISTS. analysis/render_multigeom_rollout.py:113-130 builds the vehicle
surface by marching cubes over the rigid particle cloud rather than reading a
.ply. Its stated reasons are that the Rogue and Silverado .ply files "do not
exist on this machine" and that register E8 leaves NCAC/CCSA redistribution
rights unresolved.

THE FIRST OF THOSE REASONS IS FALSE, corrected 2026-08-13. Byte-identical copies
of the exact hulls those runs used are at /Users/josie/Downloads/vehicle_meshes/,
outside the repo tree. Verified by sha256 against
render_s2/multigeom_2026-08-08/00_provenance.txt:
  rogue_g96_pd8_coarse_watertight.ply      c0b778e2...06c310b2
  silverado_g96_pd8_coarse_watertight.ply  46fba11e...f7d466d7f9
Both digests match character for character. So a mesh-based render IS available
for all three vehicles, not just the Yaris.

The SECOND reason still holds, and the surviving rationale is stronger than the
false one anyway: the reconstruction shows the geometry the solver actually
INTEGRATED, resolution loss included, whereas the source hull shows what the
solver was BUILT FROM. For a fidelity comparison the mesh is what you want; for
a physics figure the reconstruction is. That is why marching cubes stays the
default and this module is opt-in, under the E8 constraints in the header of
`register_mesh_to_body`.

REGISTRATION IS DERIVED, NOT ASSUMED. The body frame used by
render_multigeom_rollout.rigid_transform() is

    pv = (veh_particles_scene0 - t[0]) @ R[0],   world(f) = pv @ R[f].T + t[f]

Its origin is NOT the particle-cloud centroid: measured on
render_s2/multigeom_2026-08-08/g64_yaris_regression, t[0] sits 0.5948 m BELOW
scene0.mean(0), because the body frame is floor-referenced in z, and the hull's
long axis lies on BODY Y while the .ply's long axis lies on MESH X.

Centering the mesh on its own vertex mean, as a naive placement would, puts the
Yaris 0.6726 m BELOW the floor plane and 1.32 m / 1.23 m off in the two
horizontal axes. Since these renders are read for whether the underside touches
the floor, that failure is silent and total. `register_mesh_to_body` therefore
derives the yaw and the shift from the particle cloud itself and REFUSES to
return a transform whose residual exceeds one particle cell.

Verified 2026-08-13 against g64_yaris_regression: yaw 90 deg, height-profile
correlation +0.9935 (against +0.5847 for the 180-deg flip), world-space bbox
residual <= 0.0435 m ~ 0.59 h, hull z-min landing +0.0012 m above the floor
plane against the cloud's +0.0000 m.
"""
from __future__ import annotations

import numpy as np

# One particle stands for a cube of side h, so the true solid boundary sits up to
# h/2 outside the outermost particle CENTRE. A correctly registered mesh is
# therefore LARGER than the particle cloud by 0 to about h on each axis, and a
# difference of that order is EXPECTED rather than an error. On the canonical
# Yaris the measured difference is [0.0534, 0.0870, 0.0459] m against
# h = 0.0736 m, i.e. 0.73 to 1.18 cells. The gate is set at 2 cells so that
# legitimate half-cell inflation and a few thin protrusions the particle
# sampling missed both pass, while a DIFFERENT VEHICLE, which differs by whole
# metres, does not.
RESIDUAL_TOLERANCE_CELLS = 2.0

# The four yaw candidates are separated on bounding box alone only up to the
# 180-degree flip, which a symmetric box cannot see. The height profile does see
# it: on the Yaris the correct yaw scores +0.9935 and the flip +0.5847.
MIN_PROFILE_CORR = 0.90


# --------------------------------------------------------------------------
# mesh loading
# --------------------------------------------------------------------------

def load_mesh(path):
    """Return (vertices, faces) for a .ply in ANY format.

    Every .ply in this repository is `format binary_little_endian 1.0`, verified
    2026-08-13 across all four files under vehicle_geometry_research/. An
    ASCII-only reader parses none of them, so trimesh is the primary path and the
    hand-rolled ASCII reader below exists only as a no-dependency fallback.
    """
    try:
        import trimesh
        m = trimesh.load(path, process=False)
        return (np.asarray(m.vertices, dtype=np.float64),
                np.asarray(m.faces, dtype=np.int64))
    except ImportError:
        return read_ascii_ply(path)


def read_ascii_ply(path):
    """Minimal ASCII .ply reader. Raises on binary rather than returning garbage."""
    with open(path, "rb") as f:
        head = f.read(256)
    if b"format ascii" not in head:
        raise ValueError(
            "%s is not an ASCII .ply (header says %r). Every .ply in this repo is "
            "binary_little_endian; install trimesh and use load_mesh()."
            % (path, head.split(b"\n")[1:2]))
    with open(path, "r") as f:
        lines = f.readlines()
    n_vert = n_face = 0
    start = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("element vertex"):
            n_vert = int(s.split()[-1])
        elif s.startswith("element face"):
            n_face = int(s.split()[-1])
        elif s == "end_header":
            start = i + 1
            break
    verts = np.array([[float(x) for x in lines[start + i].split()[:3]]
                      for i in range(n_vert)], dtype=np.float64)
    fstart = start + n_vert
    faces = np.array([[int(x) for x in lines[fstart + i].split()[1:4]]
                      for i in range(n_face)], dtype=np.int64)
    return verts, faces


# --------------------------------------------------------------------------
# body frame recovery
# --------------------------------------------------------------------------

def body_frame_particles(scene0, R, t):
    """The body frame of render_multigeom_rollout.rigid_transform(), verbatim."""
    return (np.asarray(scene0, np.float64) - np.asarray(t, np.float64)[0]) \
        @ np.asarray(R, np.float64)[0]


def _rotz(deg):
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def _height_profile(points, nbin=24):
    """Max height per bin along the body long axis (y). A car is strongly
    asymmetric front-to-back, so this discriminates the 180-degree flip that
    bounding-box matching alone cannot."""
    y = points[:, 1]
    edges = np.linspace(y.min(), y.max(), nbin + 1)
    idx = np.clip(np.digitize(y, edges) - 1, 0, nbin - 1)
    out = np.full(nbin, np.nan)
    for b in range(nbin):
        sel = points[idx == b, 2]
        if sel.size:
            out[b] = sel.max()
    ok = ~np.isnan(out)
    out[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), out[ok])
    return out


def register_mesh_to_body(vertices, particles_body, cell_h,
                          tolerance_cells=RESIDUAL_TOLERANCE_CELLS,
                          min_profile_corr=MIN_PROFILE_CORR):
    """Derive the mesh -> body-frame transform from the particle cloud.

    Searches the four proper yaw rotations, scores each by bounding-box extent
    agreement and by height-profile correlation, and returns the winner.

    E8 CONSTRAINT. This returns transformed GEOMETRY derived from the source
    hull. Register E8 records NCAC/CCSA redistribution rights as unresolved, and
    specifically leaves open whether the canonical Yaris hull is NHTSA-hosted
    (safe) or CCSA-hosted (licence-silent). Rendering locally for internal review
    is fine. Do not commit the output geometry, or a render that reproduces it in
    recoverable form, to a public repository or a DesignSafe DOI until E8 closes.

    Returns a dict with keys: yaw_deg, rotation, shift, target, vertices_body,
    residual_m, residual_cells, profile_corr, extent_mesh, extent_cloud.
    Raises ValueError if no candidate registers within tolerance.
    """
    V = np.asarray(vertices, np.float64)
    P = np.asarray(particles_body, np.float64)
    cell_h = float(cell_h)

    target = np.array([0.5 * (P[:, 0].min() + P[:, 0].max()),
                       0.5 * (P[:, 1].min() + P[:, 1].max()),
                       P[:, 2].min()])
    cloud_profile = _height_profile(P)
    extent_cloud = P.max(0) - P.min(0)

    best = None
    for deg in (0, 90, 180, 270):
        Rz = _rotz(deg)
        Vr = V @ Rz.T
        # Horizontal axes centre on the bbox mid; z aligns the FLOOR, because the
        # body frame is floor-referenced, not centroid-referenced.
        shift = np.array([0.5 * (Vr[:, 0].min() + Vr[:, 0].max()),
                          0.5 * (Vr[:, 1].min() + Vr[:, 1].max()),
                          Vr[:, 2].min()])
        Vb = Vr - shift + target
        extent_mesh = Vb.max(0) - Vb.min(0)
        # The mesh should exceed the cloud by ~h per axis (half-cell each side).
        extent_resid = float(np.abs(np.abs(extent_mesh - extent_cloud) - cell_h).max())
        corr = float(np.corrcoef(_height_profile(Vb), cloud_profile)[0, 1])
        score = (corr, -extent_resid)
        cand = {
            "yaw_deg": deg, "rotation": Rz, "shift": shift, "target": target,
            "vertices_body": Vb, "profile_corr": corr,
            "extent_mesh": extent_mesh, "extent_cloud": extent_cloud,
            "extent_residual_m": extent_resid,
        }
        if best is None or score > best[0]:
            best = (score, cand)

    cand = best[1]

    # GATE 1, same vehicle at the same scale. The mesh may legitimately exceed
    # the particle cloud by up to about one cell per axis (half a cell each
    # side); a different vehicle differs by whole metres.
    resid = float(np.abs(cand["extent_mesh"] - cand["extent_cloud"]).max())
    cand["residual_m"] = resid
    cand["residual_cells"] = resid / cell_h

    # GATE 2, correct front-to-back orientation. Bounding boxes are blind to the
    # 180-degree flip; the height profile is not.
    corr = cand["profile_corr"]

    if cand["residual_cells"] > tolerance_cells:
        raise ValueError(
            "Mesh does not register to the simulated body: best yaw %d deg leaves "
            "a %.4f m (%.2f cell) extent mismatch, tolerance %.2f cells. The mesh "
            "and the run are probably not the same vehicle. Refusing to place a "
            "hull whose pose is not verified."
            % (cand["yaw_deg"], resid, cand["residual_cells"], tolerance_cells))
    if not np.isfinite(corr) or corr < min_profile_corr:
        raise ValueError(
            "Mesh orientation is not resolved: best yaw %d deg scores a height "
            "profile correlation of %+.4f against the simulated cloud, minimum "
            "%.2f. The hull may be reversed front-to-back. Refusing to place a "
            "hull whose pose is not verified."
            % (cand["yaw_deg"], corr, min_profile_corr))
    return cand


# --------------------------------------------------------------------------
# per-frame placement
# --------------------------------------------------------------------------

def vehicle_mesh_at_frame(vertices_body, R, t, frame):
    """World-space vertices at `frame`, matching rigid_transform()'s world()."""
    R = np.asarray(R, np.float64)
    t = np.asarray(t, np.float64)
    return np.asarray(vertices_body, np.float64) @ R[frame].T + t[frame]


def mesh_volume(vertices, faces):
    """Signed volume of a closed triangle mesh, divergence theorem, no deps.

    V = (1/6) sum_t (a x b) . c over the triangles. Returned as a magnitude, so
    a mesh whose winding is inward still reports a positive volume. Reproduces
    trimesh's `.volume` on the canonical Yaris hull to 3.542739 m3.

    THIS IS A RENDER-LAYER MEASUREMENT ONLY. The solver never sees this number:
    it works from the solidified particle cloud, whose own volume is reported as
    `solid_volume_m3` in each run's summary.json. The two are close but not
    equal, e.g. g64_yaris_regression records solid 3.5513843861695054 m3 against
    hull 3.542738790016075 m3, fill_ratio 1.0024.
    """
    V = np.asarray(vertices, np.float64)
    F = np.asarray(faces, np.int64)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    return float(abs(np.einsum("ij,ij->i", np.cross(a, b), c).sum()) / 6.0)


def decimate(vertices, faces, max_faces):
    """Reduce face count for renderers that cannot carry the full hull.

    The canonical Yaris hull is 655,308 faces; render_multigeom_rollout caps its
    reconstructed surface at 9,000. Returns the input unchanged if no backend is
    available or decimation fails, so a missing optional dependency degrades the
    render rather than breaking it.

    OPEN3D IS TRIED FIRST, AND THAT ORDER IS THE POINT. The project's own mesh
    qualification found that `trimesh.simplify_quadric_decimation` BREAKS
    WATERTIGHTNESS on this exact geometry at every level from 320k to 10k faces,
    producing 49 to 172 non-manifold edges, while Open3D 0.19.0 preserves both
    watertightness and genus. Re-verified live 2026-08-14 on the canonical Yaris
    hull with Open3D 0.19.0: at 30,000 faces watertight True, euler_number -442
    (unchanged from the source), volume 3.519367 m3 against 3.542739, i.e.
    -0.660 percent; at 9,000 faces watertight True, euler -442, volume 3.467026,
    -2.137 percent.

    THAT VOLUME LOSS IS WHY THE CALLER IS TOLD ABOUT IT. Displaced volume is the
    physical quantity the three-class comparison rests on, so a hull that quietly
    lost 2.1 percent of it while being made drawable would misstate the one thing
    the figure is for. `load_and_register` records source and drawn volume and
    the percentage between them, and the caption prints it.

    Also note the trimesh fallback silently needs a THIRD package: on
    trimesh 5.0.0 `simplify_quadric_decimation` raises
    ModuleNotFoundError: fast_simplification. With neither backend installed the
    full hull is drawn, which is correct but slow.

    Returns (vertices, faces, backend_name).
    """
    faces = np.asarray(faces)
    V = np.asarray(vertices, np.float64)
    if not max_faces or len(faces) <= max_faces:
        return V, faces, "none (already at or below the cap)"
    try:
        import open3d as o3d
        m = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(V),
                                      o3d.utility.Vector3iVector(faces))
        m = m.simplify_quadric_decimation(target_number_of_triangles=int(max_faces))
        return (np.asarray(m.vertices, np.float64), np.asarray(m.triangles),
                "open3d %s" % o3d.__version__)
    except Exception as exc:
        print("[vehicle_mesh] open3d decimation unavailable (%s: %s), trying trimesh"
              % (type(exc).__name__, exc))
    try:
        import trimesh
        m = trimesh.Trimesh(vertices=V, faces=faces, process=False)
        m = m.simplify_quadric_decimation(face_count=max_faces)
        print("[vehicle_mesh] WARNING: decimated with trimesh, which is recorded "
              "as breaking watertightness on this geometry at every level tested")
        return (np.asarray(m.vertices, np.float64), np.asarray(m.faces),
                "trimesh %s (WATERTIGHTNESS NOT PRESERVED)" % trimesh.__version__)
    except Exception as exc:
        print("[vehicle_mesh] decimation skipped (%s: %s)" % (type(exc).__name__, exc))
        return V, faces, "none (no backend, full hull drawn)"


def load_and_register(ply_path, npz, max_faces=None, tolerance_cells=RESIDUAL_TOLERANCE_CELLS):
    """Convenience path: .ply + rollout data -> body-frame mesh + report.

    Accepts either shape of `npz`:
      - a raw np.load(rollout.npz), keyed "veh_particles_scene0" and "h", or
      - the dict from render_multigeom_rollout.load_run(), keyed "scene0" with
        no "h" (there, h is dx/2).
    Both appear in this codebase, and silently failing on one of them is a
    needless footgun.
    """
    V, F = load_mesh(ply_path)
    R = np.asarray(npz["R"], np.float64)
    t = np.asarray(npz["t"], np.float64)

    if "veh_particles_scene0" in npz:
        scene0 = npz["veh_particles_scene0"]
    elif "scene0" in npz:
        scene0 = npz["scene0"]
    else:
        raise KeyError("rollout data has neither 'veh_particles_scene0' nor "
                       "'scene0'; cannot recover the rigid particle cloud")

    if "h" in npz:
        cell_h = float(npz["h"])
    elif "dx" in npz:
        cell_h = 0.5 * float(npz["dx"])   # h = dx/2, render_multigeom_shaded:465
    else:
        raise KeyError("rollout data has neither 'h' nor 'dx'; cannot recover "
                       "the particle cell size")

    P = body_frame_particles(scene0, R, t)
    reg = register_mesh_to_body(V, P, cell_h, tolerance_cells)
    vol_src = mesh_volume(reg["vertices_body"], F)
    n_src = len(F)
    Vb, F, backend = decimate(reg["vertices_body"], F, max_faces)
    vol_drawn = mesh_volume(Vb, F)
    reg["vertices_body"] = Vb
    reg["faces"] = F
    reg["n_faces"] = len(F)
    reg["n_faces_source"] = n_src
    reg["decimation_backend"] = backend
    reg["volume_source_m3"] = vol_src
    reg["volume_drawn_m3"] = vol_drawn
    reg["volume_delta_pct"] = 100.0 * (vol_drawn - vol_src) / vol_src if vol_src else 0.0
    return reg
