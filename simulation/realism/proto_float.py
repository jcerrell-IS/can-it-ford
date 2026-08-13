"""Force-coupled buoyancy prototype: does a free body find the Archimedes draft?

WHAT THIS TESTS, AND WHY IT IS FALSIFIABLE
------------------------------------------
A cube of side L and density rho_b released in water rho_w must float at draft

    d / L = rho_b / rho_w                                       (Archimedes)

with rho_b = 310.494 kg/m^3 (the canonical Yaris effective density, = 1100 /
3.542739, matching register B5) and rho_w = 1000, the target is

    d / L = 0.310494

Nothing in the solver is tuned to produce that number: it is set by the density ratio
alone, so the run either lands on it or it does not. The body starts DEEPER than
equilibrium, so a working coupling must push it UP. A body with no force coupling
cannot do this, which is the point of the comparison arm.

WHY A CUBE AND NOT THE YARIS HULL
---------------------------------
`warpmpm.geometry.build_sdf` signs its field with a generalized winding number over
every grid point against every face (`mesh_sdf.py:328-366`, `_winding_number` at :205).
The canonical hull is 655,308 faces, so at res=64 that is 262,144 * 655,308 = 1.7e11
solid-angle evaluations in numpy. That does not finish. The cube is 12 faces and builds
instantly, and it is the SAME geometry the C1-SDF validation used to establish that this
force path reads buoyancy to within 7.3-7.7 percent of analytic (register A-2, job
894731). Proving the feedback loop on validated geometry is the point; putting the hull
through this path is a separable mesh-decimation problem, not a coupling problem.

ARMS
----
  dynamic  SDF collider + DynamicSDFBody. Force-coupled free body. The prototype.
  frozen   the identical SDF collider held fixed, reporting its wrench only. This is
           the validated reference: it measures the buoyant force without moving.
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
RHO_BOX = 310.494          # canonical Yaris effective density, register B5
G = 9.81                   # solver value, register A2 (core/solver.py:167-169)
BULK = 9.0e5               # newtonian() default, materials/__init__.py
ETA = 1.0e-3               # IAPWS water, matches sim_standing.py:75


def cube_mesh(length):
    """Watertight axis-aligned cube of side `length`, centred on the ORIGIN.

    add_sdf_collider stores the field in the BODY frame and queries it as
    body = quat_rotate_inv(quat, x_world - center) (mpm_solver_warp.py:2697-2703),
    so the mesh must be origin-centred and the world placement passed as `center`.
    """
    a = 0.5 * float(length)
    verts = np.array([[-a, -a, -a], [+a, -a, -a], [+a, +a, -a], [-a, +a, -a],
                      [-a, -a, +a], [+a, -a, +a], [+a, +a, +a], [-a, +a, +a]], dtype=float)
    faces = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                      [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                      [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]], dtype=np.int64)
    return verts, faces


def sdf_margin_cells(length, dx, res, band_safety=2.0):
    """Smallest margin_cells whose SDF-grid margin clears the collider contact band.

    add_sdf_collider REFUSES the collider if the minimum stored SDF value on the grid's
    six faces does not exceed `band` (mpm_solver_warp.py:2639-2644). build_sdf sets
    cell = span/(res-1-2*margin) (mesh_sdf.py:355), so the margin distance is
    margin*span/(res-1-2*margin); requiring that to reach band_safety*dx and solving for
    margin gives the expression below. Chosen to satisfy the engine's own guard, not
    tuned against any measured value.
    """
    m = band_safety * dx * (res - 1) / (length + 2.0 * band_safety * dx)
    margin = int(math.ceil(m))
    if res - 1 - 2 * margin < 8:
        raise ValueError(f"sdf_res={res} too small: margin {margin} leaves "
                         f"{res - 1 - 2 * margin} cells across the mesh")
    return margin


def build(args):
    from warpmpm.core.solver import Solver, GridConfig
    from warpmpm.materials import newtonian
    from warpmpm.geometry import build_sdf

    lim = float(args.lim)
    n_grid = int(args.n_grid)
    dx = lim / n_grid
    h = dx / 2.0                      # 8 particles per cell, the MPM convention
    wall = 4.0 * dx
    floor = wall
    L = float(args.cube)

    # --- water lattice ------------------------------------------------------------
    lo, hi = wall, lim - wall
    nxy = int(math.floor((hi - lo) / h))
    nz = int(math.floor((args.depth - floor) / h))
    # Centre the lattice on the domain axis. Without this, `lo + h*(0.5+arange(nxy))`
    # spans lo+0.5h .. lo+(nxy-0.5)h, whose centre is lo + nxy*h/2, NOT lim/2 once the
    # floor() truncates nxy. At n_grid=24 that left the water centred on 0.4948 against
    # a cube at 0.5000, and the resulting asymmetry showed up as a spurious -15 N on BOTH
    # lateral axes in the first smoke run. Found by reading the wrench, not by inspection.
    lo = 0.5 * lim - 0.5 * (nxy * h)
    ax = lo + h * (0.5 + np.arange(nxy))
    az = floor + h * (0.5 + np.arange(nz))
    X, Y, Z = np.meshgrid(ax, ax, az, indexing="ij")
    water = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)

    # --- body placement: start DEEPER than equilibrium so buoyancy must lift it ----
    surface = args.depth
    draft0 = args.draft0 * L
    z_center0 = surface - draft0 + 0.5 * L
    center0 = np.array([0.5 * lim, 0.5 * lim, z_center0])

    # carve water out of the cube's initial footprint so it does not start interpenetrated
    d = np.abs(water - center0)
    inside = np.all(d <= (0.5 * L + 0.5 * h), axis=1)
    n_carved = int(inside.sum())
    water = water[~inside]

    pos = water.astype(np.float32)
    vol = np.full(len(pos), h ** 3, dtype=np.float32)

    # --- timestep from the acoustic CFL -------------------------------------------
    c = math.sqrt(1.1 * BULK / RHO_W)
    dt_sub = args.cfl * dx / c
    substeps = int(math.ceil((1.0 / args.fps) / dt_sub))
    dt_sub = (1.0 / args.fps) / substeps

    s = Solver(grid=GridConfig(n_grid=n_grid, grid_lim=lim), device="cuda:0")
    s.load_particles(pos, vol)
    s.set_material(newtonian(eta=ETA, density=RHO_W, bulk_modulus=BULK))
    s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
    for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                    ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
    s.add_domain_walls()

    verts, faces = cube_mesh(L)
    margin = sdf_margin_cells(L, dx, args.sdf_res)
    sdf = build_sdf(verts, faces, res=args.sdf_res, margin_cells=float(margin))
    handle = s.add_sdf_collider(sdf, center0, velocity=(0.0, 0.0, 0.0),
                                surface="separable", friction=0.4)

    mass = RHO_BOX * L ** 3
    # Solid cube inertia. This is a CUBE, so the box formula IS the exact tensor here,
    # unlike the Yaris case where vehicle_params.py's box fallback is a proxy for a hull
    # that fills only 33.2 percent of its bounding box.
    I = np.eye(3) * (mass * (L ** 2 + L ** 2) / 12.0)

    return dict(solver=s, handle=handle, dx=dx, h=h, dt=dt_sub, substeps=substeps,
                mass=mass, I=I, L=L, center0=center0, surface=surface, floor=floor,
                n_water=len(pos), n_carved=n_carved, c=c, lim=lim, n_grid=n_grid)


def measure_surface(solver, n_water, lim, cube_xy, cube_L, h):
    """Free-surface height measured from the particles, in an annulus AWAY from the body.

    The initial carve removes every water particle inside the body's footprint, so the
    tank holds LESS water than `--depth` implies and the real surface sits below it. The
    first g48 run reported draft against the hardcoded fill height and so overstated the
    draft by roughly carved_volume / free_surface_area; measuring instead removes that
    whole error class. Sampled away from the body because the local surface next to a
    floating object is depressed/raised by the body itself, which is precisely the thing
    being measured against.
    """
    x = solver.x()[:n_water]
    d = np.abs(x[:, :2] - np.asarray(cube_xy)[None, :]).max(axis=1)
    far = d > (0.5 * cube_L + 4.0 * h)
    if far.sum() < 100:
        far = np.ones(len(x), dtype=bool)
    z = x[far, 2]
    # top of the column: the free surface sits about h/2 above the topmost particle
    return float(np.percentile(z, 99.5)) + 0.5 * h


def count_leaks(solver, n_water, lim, wall, floor):
    """Water particles that have escaped the tank. A slow monotone sink with no other
    explanation is usually mass loss, so this is measured rather than assumed."""
    x = solver.x()[:n_water]
    lo = np.array([wall, wall, floor]) - 0.5 * (lim / 1e6)
    out = (x[:, 0] < lo[0]) | (x[:, 1] < lo[1]) | (x[:, 2] < lo[2]) \
        | (x[:, 0] > lim - wall) | (x[:, 1] > lim - wall)
    return int(out.sum())


def project_water(solver, n_water, lim, wall, floor, dx):
    """Clamp escaped water particles back inside the tank and kill their outward velocity.

    Without this the g48 run lost water monotonically: leaks 15,720 -> 21,904 of 239,800
    particles and the free surface fell 0.030 m, of which only ~0.012 m was the cube
    rising. The residual ~5 percent mass loss is the SAME ORDER as the 5.11 percent draft
    agreement it was being used to support, so the number could not be trusted until the
    mass was conserved. This mirrors `project_water` in the validated C1-SDF harness
    (simulation/validate_coupling_force.py:330-351) rather than inventing a new rule.

    Returns the number of particles projected this call.
    """
    x = solver.x()
    w = x[:n_water]
    eps = 0.25 * dx
    lo = np.array([wall, wall, floor], dtype=np.float32) - eps
    hi = np.array([lim - wall, lim - wall, np.inf], dtype=np.float32) + eps
    out_lo = w < lo
    out_hi = w > hi
    if not (out_lo.any() or out_hi.any()):
        return 0
    n = int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
    v = solver.v()
    vw = v[:n_water]
    np.clip(w, lo, hi, out=w)
    vw[out_lo] = np.maximum(vw[out_lo], 0.0)   # was heading further out: stop it
    vw[out_hi] = np.minimum(vw[out_hi], 0.0)
    solver.set_x(x)
    solver.set_v(v)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["dynamic", "frozen"], default="dynamic")
    ap.add_argument("--n-grid", type=int, default=48)
    ap.add_argument("--lim", type=float, default=1.0)
    ap.add_argument("--cube", type=float, default=0.30)
    ap.add_argument("--depth", type=float, default=0.50)
    ap.add_argument("--draft0", type=float, default=0.60,
                    help="initial draft as a fraction of L; > rho_b/rho_w means the "
                         "body starts too deep and must be pushed UP")
    ap.add_argument("--frames", type=int, default=150)
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--cfl", type=float, default=0.4)
    ap.add_argument("--sdf-res", type=int, default=48)
    ap.add_argument("--settle", type=int, default=15, help="frames held before release")
    ap.add_argument("--added-mass", type=float, default=0.0)
    ap.add_argument("--no-project", action="store_true",
                    help="disable the leak projection, to measure its effect")
    ap.add_argument("--out", default="proto_float_result.json")
    args = ap.parse_args()

    t0 = time.time()
    sc = build(args)
    s, handle = sc["solver"], sc["handle"]
    L, surface = sc["L"], sc["surface"]

    target_frac = RHO_BOX / RHO_W
    analytic_F_at_start = RHO_W * G * (args.draft0 * L) * L * L   # submerged vol * rho_w * g
    weight = sc["mass"] * G

    print(json.dumps({
        "setup": {
            "n_grid": sc["n_grid"], "lim": sc["lim"], "dx": sc["dx"], "h": sc["h"],
            "n_water": sc["n_water"], "n_carved": sc["n_carved"],
            "dt_sub": sc["dt"], "substeps_per_frame": sc["substeps"],
            "sound_speed": sc["c"], "cube_L": L, "mass_kg": sc["mass"],
            "rho_box": RHO_BOX, "target_draft_frac": target_frac,
            "start_draft_frac": args.draft0,
            "weight_N": weight, "buoy_at_start_N": analytic_F_at_start,
            "net_at_start_N": analytic_F_at_start - weight,
            "added_mass_kg": args.added_mass,
        }
    }, indent=2))

    # --- settle the water with the body held, so release is from a quiet state -------
    for _ in range(args.settle):
        s.reset_sdf_force(handle)
        s.step(sc["dt"], sc["substeps"])
        if not args.no_project:
            project_water(s, sc["n_water"], sc["lim"], 4.0 * sc["dx"], sc["floor"], sc["dx"])
    w = s.sdf_wrench(handle, sc["dt"] * sc["substeps"])
    print(f"[settle] wrench after {args.settle} frames: F = {np.asarray(w['force'])} N "
          f"(analytic buoyancy at this draft = {analytic_F_at_start:.1f} N, "
          f"weight = {weight:.1f} N)", flush=True)
    settle_force = np.asarray(w["force"], dtype=float).tolist()

    cube_xy = (sc["center0"][0], sc["center0"][1])
    surface = measure_surface(s, sc["n_water"], sc["lim"], cube_xy, L, sc["h"])
    leaks0 = count_leaks(s, sc["n_water"], sc["lim"], 4.0 * sc["dx"], sc["floor"])
    print(f"[settle] MEASURED free surface = {surface:.5f} m against the "
          f"--depth fill height {args.depth:.5f} m "
          f"(carve lowered it by {args.depth - surface:+.5f} m = "
          f"{(args.depth - surface) / L:.4f} in draft/L units); leaks = {leaks0}",
          flush=True)

    body = None
    if args.arm == "dynamic":
        body = DynamicSDFBody(s, handle, mass=sc["mass"], inertia_body=sc["I"],
                              gravity=(0.0, 0.0, -G), added_mass=args.added_mass,
                              floor_z=sc["floor"] + 0.5 * L).install()

    hist = []
    n_proj = 0
    for f in range(args.frames):
        if body is None:
            s.reset_sdf_force(handle)
        s.step(sc["dt"], sc["substeps"])
        if not args.no_project:
            n_proj += project_water(s, sc["n_water"], sc["lim"], 4.0 * sc["dx"],
                                    sc["floor"], sc["dx"])
        if body is not None:
            if f % 10 == 0:            # re-measure: the surface moves as the body does
                surface = measure_surface(s, sc["n_water"], sc["lim"], cube_xy, L, sc["h"])
            z = body.x[2]
            draft = max(0.0, surface - (z - 0.5 * L))
            hist.append({"frame": f, "t": (f + 1) / args.fps, "z": float(z),
                         "vz": float(body.v[2]), "surface": float(surface),
                         "leaks": count_leaks(s, sc["n_water"], sc["lim"],
                                              4.0 * sc["dx"], sc["floor"]) if f % 30 == 0 else None,
                         "draft_frac": float(draft / L)})
            if body.diverged:
                print(f"[DIVERGED] at frame {f}", flush=True)
                break
        else:
            wr = s.sdf_wrench(handle, sc["dt"] * sc["substeps"])
            hist.append({"frame": f, "t": (f + 1) / args.fps,
                         "F": np.asarray(wr["force"]).tolist()})
        if f % 15 == 0:
            print(f"  frame {f:4d}  " + (
                f"z={hist[-1]['z']:.5f} vz={hist[-1]['vz']:+.4f} "
                f"surf={hist[-1]['surface']:.5f} "
                f"draft/L={hist[-1]['draft_frac']:.4f}" if body is not None
                else f"F={hist[-1]['F']}"), flush=True)

    out = {"arm": args.arm, "wall_s": time.time() - t0,
           "settle_force_N": settle_force,
           "analytic": {"target_draft_frac": target_frac,
                        "weight_N": weight,
                        "buoy_at_start_N": analytic_F_at_start},
           "history": hist}

    if body is not None:
        tail = [r["draft_frac"] for r in hist[-max(1, len(hist) // 5):]]
        settled = float(np.mean(tail)) if tail else float("nan")
        out["result"] = {
            "diverged": bool(body.diverged),
            "start_draft_frac": args.draft0,
            "settled_draft_frac": settled,
            "target_draft_frac": target_frac,
            "abs_err": abs(settled - target_frac),
            "rel_err_pct": 100.0 * (settled - target_frac) / target_frac,
            "moved_toward_target": bool(abs(settled - target_frac) < abs(args.draft0 - target_frac)),
            "measured_surface_m": float(surface),
            "fill_height_m": float(args.depth),
            "surface_drop_from_carve_m": float(args.depth - surface),
            "leaks_start": int(leaks0),
            "leaks_end": count_leaks(s, sc["n_water"], sc["lim"], 4.0 * sc["dx"], sc["floor"]),
            "n_water": int(sc["n_water"]),
            "n_projected_total": int(n_proj),
            "projection_enabled": bool(not args.no_project),
        }
        print("\n=== RESULT ===")
        print(json.dumps(out["result"], indent=2))

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
