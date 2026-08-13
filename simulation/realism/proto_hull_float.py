"""Force-coupled float test on the CANONICAL YARIS HULL, not a cube.

THE FALSIFIABLE TEST
--------------------
A free body in equilibrium has zero net vertical force, so the measured fluid wrench must
converge on the body's own weight:

    F_z  ->  M g  =  1100 * 9.81  =  10,791 N

and the displaced volume must be

    V_disp = M / rho_w = 1100 / 1000 = 1.100 m^3   (31.0 percent of the 3.542739 m^3 hull)

Neither number is tuned; both follow from mass and water density alone.

HOW THE AXIS HAZARD IS HANDLED, RATHER THAN AVOIDED
---------------------------------------------------
Measured this session, from the raw mesh: the hull's own extents are
(4.2826, 1.7464, 1.5180) - **long axis X**. The scene the 17 canonical runs use has
extents (1.7078, 4.2014, 1.4853) - **long axis Y**. The pipeline rotates the hull 90
degrees about z on load. That is the whole source of the transposition the hard
constraint warns about, and it is why writing `vehicle_params.py`'s (L,W,H)-ordered
tensor into the solver gives Ixx -69.2 percent and Iyy +379.2 percent.

This script does the correct thing rather than the convenient thing:

  * the SDF is built in the MESH frame (`hull_sdf.py` centres the decimated mesh on its
    own bbox), so the inertia tensor from the same mesh is ALSO in the mesh frame, and
    the two are consistent by construction;
  * to sit the hull broadside to +x flow like the canonical scene, the collider carries a
    90-degree quaternion about z. `DynamicSDFBody` then forms the world tensor as
    I_world^-1 = R I_body^-1 R^T every substep, which is exactly the transformation the
    naive wire omits.

So the body-frame tensor is never permuted by hand. Hand-permuting is what goes wrong.

The tensor comes from `hull_sdf.py`'s solid voxelisation, which reproduced the
assessment's particle-cloud tensor to within 1.2 percent on all three axes once the
permutation is applied. It does NOT come from `vehicle_params.py`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dynamic_body import DynamicSDFBody  # noqa: E402

RHO_W = 1000.0
G = 9.81
BULK = 9.0e5
ETA = 1.0e-3
HULL_MASS = 1100.0          # CLAUDE.md canonical, vehicle_params.py mass_kg
HULL_VOLUME = 3.542739      # register E1


def quat_z(deg):
    """warp-layout (x, y, z, w) quaternion for a rotation about +z."""
    r = math.radians(deg) * 0.5
    return (0.0, 0.0, math.sin(r), math.cos(r))


def quat_to_R(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def sdf_inside(sdf, centre, quat, pts, band=0.0):
    """Which of `pts` lie inside the collider, by querying the SDF the collider uses.

    WHY NOT A BOUNDING-BOX CARVE. The hull fills only 33.2 percent of its own bounding
    box (assessment section 1b), so a bbox carve removes about three times the water the
    hull actually displaces. That is the same error class as the fill-height bug already
    hit once this session: it silently lowers the tank's water level and therefore the
    equilibrium the test is trying to measure. Querying the SDF removes the error rather
    than bounding it.

    Mirrors the engine's own query exactly (mpm_solver_warp.py:2697-2711):
    body = quat_rotate_inv(quat, x_world - centre); fidx = (body - origin)/cell; trilerp.
    For row-vector numpy, quat_rotate_inv(q, v) == v @ R with R the body->world matrix.
    """
    R = quat_to_R(quat)
    body = (np.asarray(pts, dtype=float) - np.asarray(centre, dtype=float)) @ R
    origin = np.asarray(sdf.origin, dtype=float)
    cell = float(sdf.cell)
    vals = np.asarray(sdf.values, dtype=float)
    res = vals.shape[0]

    f = (body - origin) / cell
    ok = np.all((f >= 0.0) & (f <= res - 1.0), axis=1)
    out = np.zeros(len(body), dtype=bool)
    if not ok.any():
        return out

    fo = f[ok]
    i0 = np.floor(fo).astype(int)
    i0 = np.clip(i0, 0, res - 2)
    t = fo - i0
    v = np.zeros(len(fo))
    for dx_ in (0, 1):
        for dy_ in (0, 1):
            for dz_ in (0, 1):
                w = ((t[:, 0] if dx_ else 1 - t[:, 0])
                     * (t[:, 1] if dy_ else 1 - t[:, 1])
                     * (t[:, 2] if dz_ else 1 - t[:, 2]))
                v += w * vals[i0[:, 0] + dx_, i0[:, 1] + dy_, i0[:, 2] + dz_]
    out[ok] = v <= band
    return out


def submerged_volume(sdf, centre, quat, surface_z, level=0.0, spacing=0.02):
    """GEOMETRIC displaced volume below `surface_z`, integrated over the SDF directly.

    WHY THIS EXISTS: Fz_settled -> M g IS VERY NEARLY A TAUTOLOGY.
    ------------------------------------------------------------
    `DynamicSDFBody._step` integrates `dv = J/(M + m_add) + g*dt` (dynamic_body.py:207).
    Set dv = 0 and it rearranges to J/dt = M*g EXACTLY. So once the body stops
    accelerating, the measured wrench is forced to equal the weight by the integrator's
    own algebra, whatever the fluid is doing. The identity is exact:

        Fz_err_pct = 100 * (Fz - Mg)/Mg = 100 * a_z / g

    i.e. +0.035 percent is a residual acceleration of 3.5e-4 g. That is a real and useful
    CONVERGENCE statement ("the body has come to rest") but it is NOT a validation of
    Archimedes, and it must never be reported as one.

    The non-circular question is geometric: at the draft the hull actually settled to,
    does it displace M/rho_w = 1.100 m^3? Nothing in the integrator forces that. This
    function answers it by integrating the same SDF the collide kernel queries.

    `level` selects which isosurface counts as the hull boundary:
      * 0.0          the true mesh surface;
      * `band`       the surface the kernel ACTUALLY enforces, since it gates the whole
                     boundary condition on `if sd <= param.band`
                     (mpm_solver_warp.py:2711) and `band` defaults to the water cell size
                     `model.dx` (:2626-2627). So the effective collider is inflated by
                     roughly one water cell, and that inflation SHRINKS AS THE GRID
                     REFINES. Reporting both levels separates hull geometry from the
                     discretisation of the contact.

    Midpoint occupancy over a lattice of `spacing`, chunked to bound memory. Calibrate it
    by passing surface_z = +inf, which must return the SDF's own enclosed volume.
    """
    vals = np.asarray(sdf.values, dtype=float)
    res = vals.shape[0]
    origin = np.asarray(sdf.origin, dtype=float)
    cell = float(sdf.cell)
    ext = (res - 1) * cell
    n = int(math.ceil(ext / spacing))
    step = ext / n
    ax = [origin[k] + (np.arange(n) + 0.5) * step for k in range(3)]

    R = quat_to_R(quat)
    c = np.asarray(centre, dtype=float)
    tot = 0
    Y, Z = np.meshgrid(ax[1], ax[2], indexing="ij")
    yz = np.stack([Y.ravel(), Z.ravel()], axis=1)
    for xi in ax[0]:
        body = np.empty((len(yz), 3))
        body[:, 0] = xi
        body[:, 1:] = yz
        f = (body - origin) / cell
        i0 = np.clip(np.floor(f).astype(int), 0, res - 2)
        t = f - i0
        v = np.zeros(len(body))
        for dx_ in (0, 1):
            for dy_ in (0, 1):
                for dz_ in (0, 1):
                    w = ((t[:, 0] if dx_ else 1 - t[:, 0])
                         * (t[:, 1] if dy_ else 1 - t[:, 1])
                         * (t[:, 2] if dz_ else 1 - t[:, 2]))
                    v += w * vals[i0[:, 0] + dx_, i0[:, 1] + dy_, i0[:, 2] + dz_]
        m = v <= level
        if not m.any():
            continue
        # body -> world is the transpose of the world -> body map used in sdf_inside
        world_z = body[m] @ R[2, :] + c[2]
        tot += int((world_z <= surface_z).sum())
    return tot * step ** 3


def measure_surface(solver, n_water, centre_xy, foot, h, floor):
    """Free-surface height measured from particles AWAY from the hull.

    Carried over from proto_float.py because the fixed-fill-height assumption is wrong
    here for the same reason: the carve removes water, and the level then moves as the
    body rises. Without this the reported draft is not a measurement.
    """
    x = solver.x()[:n_water]
    d = np.abs(x[:, :2] - np.asarray(centre_xy)[None, :])
    far = (d[:, 0] > foot[0]) | (d[:, 1] > foot[1])
    if far.sum() < 200:
        far = np.ones(len(x), dtype=bool)
    return float(np.percentile(x[far, 2], 99.5) + 0.5 * h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sdf", required=True)
    ap.add_argument("--report", required=True, help="hull_sdf.py JSON, for the tensor")
    ap.add_argument("--n-grid", type=int, default=96)
    ap.add_argument("--lim", type=float, default=7.0)
    ap.add_argument("--depth", type=float, default=1.00)
    ap.add_argument("--start-draft", type=float, default=0.90,
                    help="initial submergence in metres; deeper than equilibrium so "
                         "buoyancy must lift the hull")
    ap.add_argument("--yaw-deg", type=float, default=90.0,
                    help="90 puts the hull broadside to +x, matching the canonical scene")
    ap.add_argument("--frames", type=int, default=240)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--cfl", type=float, default=0.4)
    ap.add_argument("--settle", type=int, default=40)
    ap.add_argument("--added-mass", type=float, default=0.0)
    ap.add_argument("--band", type=float, default=None,
                    help="SDF contact band in metres. LEFT UNSET the engine uses "
                         "model.dx (mpm_solver_warp.py:2626-2627), so the band tracks "
                         "the water grid and a resolution sweep varies two things at "
                         "once. Pin it to hold the contact geometry fixed and isolate "
                         "the discretisation. Must stay under the SDF's boundary_min or "
                         "the engine's own containment guard (:2639) refuses the run.")
    ap.add_argument("--vol-spacing", type=float, default=0.02,
                    help="lattice spacing for the geometric displaced-volume integral")
    ap.add_argument("--dump-hf", default=None,
                    help="write a per-frame water HEIGHTFIELD + surface-speed field here "
                         "(.npz) for rendering. A heightfield rather than raw particles "
                         "because the free surface IS a height field for this scene, and "
                         "765k particles/frame is ~9 MB/frame against ~0.26 MB for a "
                         "256^2 field. Dumped from the SAME run that is scored, so the "
                         "render shows the validated physics and not a second scene.")
    ap.add_argument("--dump-every", type=int, default=2)
    ap.add_argument("--hf-res", type=int, default=256)
    ap.add_argument("--out", default="hull_float.json")
    args = ap.parse_args()

    from warpmpm.core.solver import Solver, GridConfig
    from warpmpm.materials import newtonian
    from warpmpm.geometry import load_sdf

    sdf = load_sdf(args.sdf)
    rep = json.load(open(args.report))
    I_body = np.asarray(rep["inertia"]["I_full"], dtype=float)
    hull_ext = np.asarray(rep["decimated"]["extents_m"], dtype=float)
    hull_vol = float(rep["decimated"]["volume_m3"])

    lim, n_grid = float(args.lim), int(args.n_grid)
    dx = lim / n_grid
    h = dx / 2.0
    wall = 4.0 * dx
    floor = wall

    nxy = int(math.floor((lim - 2 * wall) / h))
    nz = int(math.floor(args.depth / h))
    lo = 0.5 * lim - 0.5 * (nxy * h)
    ax = lo + h * (0.5 + np.arange(nxy))
    az = floor + h * (0.5 + np.arange(nz))
    X, Y, Z = np.meshgrid(ax, ax, az, indexing="ij")
    water = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)

    surface = floor + args.depth
    # hull centre: its bbox mid-height sits so that `start_draft` metres are under water
    half_h = 0.5 * hull_ext[2]
    z_c = surface - args.start_draft + half_h
    centre = np.array([0.5 * lim, 0.5 * lim, z_c])

    # carve against the SDF, not the bounding box: the hull fills 33.2 percent of its
    # bbox, so a box carve would remove ~3x the displaced water and drop the tank level.
    quat = quat_z(args.yaw_deg)
    inside = sdf_inside(sdf, centre, quat, water, band=0.5 * h)
    n_carved = int(inside.sum())
    water = water[~inside]

    # bbox-carve count, reported ONLY as the comparison that justifies the SDF carve
    ex = hull_ext.copy()
    if abs(args.yaw_deg - 90.0) < 1e-9:
        ex[0], ex[1] = ex[1], ex[0]
    _d = np.abs(np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1) - centre)
    n_carved_bbox = int(np.all(_d <= (0.5 * ex + 0.5 * h), axis=1).sum())

    pos = water.astype(np.float32)
    vol = np.full(len(pos), h ** 3, dtype=np.float32)
    n_water = len(pos)

    c = math.sqrt(1.1 * BULK / RHO_W)
    dt = args.cfl * dx / c
    substeps = int(math.ceil((1.0 / args.fps) / dt))
    dt = (1.0 / args.fps) / substeps

    s = Solver(grid=GridConfig(n_grid=n_grid, grid_lim=lim), device="cuda:0")
    s.load_particles(pos, vol)
    s.set_material(newtonian(eta=ETA, density=RHO_W, bulk_modulus=BULK))
    s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
    for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                    ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
    s.add_domain_walls()

    handle = s.add_sdf_collider(sdf, centre, quat=quat, velocity=(0.0, 0.0, 0.0),
                                surface="separable", friction=0.4, band=args.band)
    band = float(s._sim.collider_params[handle].band)

    # Calibrate the volume integrator against a number it cannot influence: with the
    # waterline at +inf it must return the SDF's own enclosed volume, which is the
    # DECIMATED hull volume, not the 3.542739 m^3 source. The decimation deficit does not
    # bias the equilibrium (the target 1.100 m^3 comes from mass and rho_w alone), it just
    # seats the hull marginally deeper.
    vol_calib = submerged_volume(sdf, centre, quat, np.inf, 0.0, args.vol_spacing)

    weight = HULL_MASS * G
    print(json.dumps({"setup": {
        "n_grid": n_grid, "lim": lim, "dx": dx, "h": h, "n_water": n_water,
        "n_carved_sdf": n_carved, "n_carved_bbox_would_be": n_carved_bbox,
        "carve_volume_sdf_m3": n_carved * h ** 3,
        "carve_volume_bbox_m3": n_carved_bbox * h ** 3, "dt_sub": dt, "substeps_per_frame": substeps,
        "depth_m": args.depth, "depth_over_dx": args.depth / dx, "water_layers": nz,
        "hull_extents_mesh_frame": hull_ext.tolist(), "hull_volume_m3": hull_vol,
        "yaw_deg": args.yaw_deg, "mass_kg": HULL_MASS, "weight_N": weight,
        "target_disp_volume_m3": HULL_MASS / RHO_W,
        "target_disp_fraction": (HULL_MASS / RHO_W) / HULL_VOLUME,
        "I_body_diag": np.diag(I_body).tolist(),
        "start_draft_m": args.start_draft,
        "band_m": band, "band_is_engine_default": args.band is None,
        "band_over_dx": band / dx,
        "sdf_res": int(np.asarray(sdf.values).shape[0]),
        "sdf_cell_m": float(sdf.cell),
        "vol_integrator_calib_m3": vol_calib,
        "vol_integrator_calib_err_pct": 100.0 * (vol_calib - hull_vol) / hull_vol,
        "vol_spacing_m": args.vol_spacing,
    }}, indent=2), flush=True)

    for _ in range(args.settle):
        s.reset_sdf_force(handle)
        s.step(dt, substeps)
    w = s.sdf_wrench(handle, dt * substeps)
    print(f"[settle] wrench F = {np.asarray(w['force'])} N   weight = {weight:.1f} N",
          flush=True)

    body = DynamicSDFBody(s, handle, mass=HULL_MASS, inertia_body=I_body,
                          gravity=(0.0, 0.0, -G), added_mass=args.added_mass,
                          floor_z=floor + 0.5 * hull_ext[2]).install()

    foot = (0.5 * ex[0] + 4 * h, 0.5 * ex[1] + 4 * h)
    surface = measure_surface(s, n_water, centre[:2], foot, h, floor)
    print(f"[settle] MEASURED surface = {surface:.5f} m vs fill height "
          f"{floor + args.depth:.5f} m", flush=True)
    # ---- render dump state ------------------------------------------------------------
    hf_lo, hf_hi = float(ax.min()), float(ax.max())
    hf_R = int(args.hf_res)
    hf_frames, hf_speed, hf_pose = [], [], []

    def _heightfield():
        """Water surface height and surface speed on a regular (x, y) lattice.

        Max-z per bin, which is the free surface for a single-valued column and is what a
        refraction/specular shader needs. Surface speed is the mean |v| of the particles
        in the top layer of each bin, so a bow wave and a wake show up as fast-moving
        surface, which is what foam keys off. Empty bins come back as NaN and the renderer
        must treat them as dry, not as z = 0.
        """
        xp = np.asarray(s.x()[:n_water], dtype=np.float32)
        vp = np.asarray(s.v()[:n_water], dtype=np.float32)
        gi = np.clip(((xp[:, 0] - hf_lo) / (hf_hi - hf_lo) * hf_R).astype(np.int32), 0, hf_R - 1)
        gj = np.clip(((xp[:, 1] - hf_lo) / (hf_hi - hf_lo) * hf_R).astype(np.int32), 0, hf_R - 1)
        flat = gi * hf_R + gj
        z = np.full(hf_R * hf_R, -np.inf, dtype=np.float32)
        np.maximum.at(z, flat, xp[:, 2])
        # top layer = within one particle spacing of that column's surface
        near = xp[:, 2] >= z[flat] - h
        sp = np.zeros(hf_R * hf_R, dtype=np.float32)
        cnt = np.zeros(hf_R * hf_R, dtype=np.float32)
        np.add.at(sp, flat[near], np.linalg.norm(vp[near], axis=1))
        np.add.at(cnt, flat[near], 1.0)
        sp = np.where(cnt > 0, sp / np.maximum(cnt, 1.0), 0.0)
        z = np.where(np.isfinite(z), z + 0.5 * h, np.nan)
        return z.reshape(hf_R, hf_R), sp.reshape(hf_R, hf_R)

    t0, hist = time.time(), []
    for f in range(args.frames):
        s.step(dt, substeps)
        if args.dump_hf and f % args.dump_every == 0:
            zf, sf = _heightfield()
            hf_frames.append(zf)
            hf_speed.append(sf)
            hf_pose.append(np.concatenate([body.x, body.q]).astype(np.float32))
        if f % 10 == 0:
            surface = measure_surface(s, n_water, centre[:2], foot, h, floor)
        Fz = float(np.mean([r["F"][2] for r in body.trace[-substeps:]])) if body.trace else 0.0
        hist.append({"frame": f, "z": float(body.x[2]), "vz": float(body.v[2]),
                     "Fz_N": Fz, "draft_m": float(surface - (body.x[2] - 0.5 * hull_ext[2]))})
        if body.diverged:
            print(f"[DIVERGED] frame {f}", flush=True)
            break
        if f % 20 == 0:
            print(f"  frame {f:4d}  z={body.x[2]:.5f} vz={body.v[2]:+.4f} "
                  f"Fz={Fz:9.1f} N (weight {weight:.0f})  draft={hist[-1]['draft_m']:.4f} m",
                  flush=True)

    tail = hist[-max(1, len(hist) // 5):]
    Fz_settled = float(np.mean([r["Fz_N"] for r in tail]))
    z_settled = float(np.mean([r["z"] for r in tail]))
    target_V = HULL_MASS / RHO_W

    # THE INDEPENDENT CHECK. Everything above is force-side and therefore partly
    # self-referential (see submerged_volume's docstring). This is geometry: put the hull
    # at the pose it settled to, at the free surface that was measured, and integrate.
    centre_settled = np.array([centre[0], centre[1], z_settled])
    V_true = submerged_volume(sdf, centre_settled, body.q, surface, 0.0, args.vol_spacing)
    V_band = submerged_volume(sdf, centre_settled, body.q, surface, band, args.vol_spacing)

    # ---- water bookkeeping, so the waterline is not taken on the percentile's word ----
    # `measure_surface` is a 99.5th percentile plus half a particle spacing, which splash
    # biases upward and a depressed far field biases downward. A tank has a second, wholly
    # independent constraint: the water it still holds. Solving
    #     A * (z_s - floor) - V_sub(z_s) = V_water_retained
    # for z_s uses only conserved volume and the SDF, never a percentile. If the two
    # disagree, the percentile is the suspect measurement, and the gap is reported rather
    # than averaged away.
    xw = np.asarray(s.x()[:n_water], dtype=float)
    span_w = nxy * h
    inb = np.all((xw > 0.0) & (xw < lim), axis=1)
    V_water_ret = float(inb.sum()) * h ** 3
    A_tank = span_w ** 2

    def _resid(z):
        return A_tank * (z - floor) - submerged_volume(
            sdf, centre_settled, body.q, z, 0.0, 2.0 * args.vol_spacing) - V_water_ret

    z_lo, z_hi = floor, floor + 3.0
    for _ in range(28):
        z_mid = 0.5 * (z_lo + z_hi)
        if _resid(z_mid) < 0.0:
            z_lo = z_mid
        else:
            z_hi = z_mid
    z_massbal = 0.5 * (z_lo + z_hi)
    V_massbal = submerged_volume(sdf, centre_settled, body.q, z_massbal, 0.0,
                                 args.vol_spacing)

    out = {"wall_s": time.time() - t0, "diverged": bool(body.diverged),
           "weight_N": weight, "Fz_settled_N": Fz_settled,
           "Fz_over_weight": Fz_settled / weight,
           "Fz_err_pct": 100.0 * (Fz_settled - weight) / weight,
           "residual_accel_z_ms2": Fz_settled / HULL_MASS - G,
           "implied_disp_volume_m3": Fz_settled / (RHO_W * G),
           "target_disp_volume_m3": target_V,
           "geom_disp_volume_true_m3": V_true,
           "geom_disp_volume_band_m3": V_band,
           "geom_err_true_pct": 100.0 * (V_true - target_V) / target_V,
           "geom_err_band_pct": 100.0 * (V_band - target_V) / target_V,
           "band_m": band, "band_over_dx": band / dx, "dx": dx, "n_grid": n_grid,
           "vol_integrator_calib_m3": vol_calib,
           "vol_integrator_calib_err_pct": 100.0 * (vol_calib - hull_vol) / hull_vol,
           "n_water_initial": int(n_water),
           "n_water_retained": int(inb.sum()),
           "water_retained_frac": float(inb.sum()) / n_water,
           "V_water_initial_m3": n_water * h ** 3,
           "V_water_retained_m3": V_water_ret,
           "tank_area_m2": A_tank,
           "surface_massbal_m": z_massbal,
           "surface_massbal_minus_measured_m": z_massbal - float(surface),
           "geom_disp_volume_massbal_m3": V_massbal,
           "geom_err_massbal_pct": 100.0 * (V_massbal - target_V) / target_V,
           "settled_draft_m": float(np.mean([r["draft_m"] for r in tail])),
           "settled_z_m": z_settled,
           "final_quat": [float(v) for v in body.q],
           "measured_surface_m": float(surface),
           "fill_height_m": float(floor + args.depth),
           "settled_vz": float(np.mean([r["vz"] for r in tail])),
           "history": hist}
    print("\n=== RESULT ===")
    print(json.dumps({k: v for k, v in out.items() if k != "history"}, indent=2))
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {args.out}")

    if args.dump_hf and hf_frames:
        np.savez_compressed(
            args.dump_hf,
            height=np.stack(hf_frames), speed=np.stack(hf_speed),
            pose=np.stack(hf_pose),
            extent=np.array([hf_lo, hf_hi, hf_lo, hf_hi], dtype=np.float32),
            floor=np.float32(floor), fps=np.float32(args.fps / args.dump_every),
            dump_every=np.int32(args.dump_every),
            hull_extents=hull_ext.astype(np.float32),
            surface_settled=np.float32(surface), n_grid=np.int32(n_grid))
        print(f"wrote {args.dump_hf}  {len(hf_frames)} frames at {hf_R}^2")


if __name__ == "__main__":
    main()
