"""
moving_vehicle_sdf_exploratory.py

NON-CANONICAL / EXPLORATORY. Nothing here feeds the 17 gated runs, the poster or
the paper, and nothing here extends docs/MULTIGEOM_VALIDATION_2026-08-11.md.
Branch claude/moving-vehicle-exploratory-2026-08-11.

WHAT THIS IS
A KINEMATIC scene. A real vehicle hull is loaded as a signed-distance-field
collider and DRIVEN through still water at a prescribed constant velocity. The
hull's trajectory is imposed. It does not respond to the water: no hydrodynamic
force can slow it, deflect it, lift it or rotate it, and momentum is not
conserved because an implicit reservoir drives it.

So this answers "what does the water do around a moving vehicle". It cannot
answer whether a vehicle would be swept away, because being swept away is
exactly the degree of freedom this scene removes. There is deliberately no
FORD / NO-FORD language anywhere in this file or its outputs. That verdict
belongs to the AR&R-validated stationary-vehicle criterion (CLAUDE.md L-1),
which is a different question with a different validation basis.

HOW IT DIFFERS FROM THE 17 CANONICAL RUNS, three ways, none of them cosmetic
 1. Coupling architecture. The canonical 17 use the material-8 free-rigid path,
    a mass-weighted grid velocity average in which no force is ever formed
    (register A-1). This uses the SDF collider path, which accumulates a real
    reaction wrench, force = sum m*(v_free - v_new)/dt (core/solver.py:354).
    Agreement between the two is not expected and disagreement is not a bug.
 2. Boundary condition on the vehicle. There, free rigid body. Here, prescribed
    kinematic collider.
 3. Flow orientation. The canonical scene hits a stationary hull broadside,
    surge along +x with the hull's long axis on y. A driven vehicle moves along
    its OWN long axis, so this scene drives along y. Measured from the hull,
    +y is hood first: zmax falls monotonically from 1.729 m at the cabin end to
    1.040 m at the sloping end.

WHAT IS REUSED RATHER THAN REINVENTED
 - The PLY loader is the vetted as-ran load_vehicle from
   analysis/render_v1/as_ran_local_copies/vehicle_live.py, byte-identical
   (sha256 5a5bbbab7d2e21df...) to renders/yaris_render_s1/vehicle_live.py,
   which the 17 gated runs ran. Do NOT substitute the installed
   warpmpm.vehicle.load_vehicle on a Mac: that copy is older, has no
   is_gaussian_ply gate, and routes every .ply to the Gaussian-splat branch.
   Verified live 2026-08-11 against this hull: it fails with
   ModuleNotFoundError: No module named 'plyfile'.
 - canonicalize() is verbatim from renders/yaris_render_s1/sim_standing.py:97-106.
 - The domain, water block, CFL and substep count are sim_standing.py's own
   (:159-161, :176-183, :227-233), so dx here matches the published
   class_rogue_g64 value of 0.16316 m at n_grid 64.

DELIBERATE DEVIATIONS FROM sim_standing.py, with reasons
 - Planes use friction 0.0 and restitution 0.0, not 0.55 / 0.05. There are no
   rigid PARTICLES in this scene at all, so 0.55, which is a vehicle-on-bed
   Coulomb coefficient, has nothing to act on; applying it to water would be an
   unsourced bed-friction model. simulation/validate_coupling_force.py:277-282
   makes the same deviation for the same reason.
 - Collider friction 0.4 and surface "separable" are add_sdf_collider's own
   engine defaults and are NOT tuned, matching validate_coupling_force.py:296.
 - The winding-number point-chunk inside the SDF build is reduced from the
   library default 4096 to 128. This is a memory blocking factor and is
   NUMERICALLY AN IDENTITY: the loop splits the point axis only, and each
   point's solid-angle sum still runs over all faces in the same order.
   Verified live, chunk 4096 against chunk 128 is bitwise identical. Without it
   one (4096, F, 3) float64 array is about 20 GiB at this hull's 72,520 faces.
   This is why the hull is NOT decimated: decimation is cheap on volume but
   breaks watertightness at every level tested.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parent.parent
LOADER_PATH = REPO / "analysis" / "render_v1" / "as_ran_local_copies" / "vehicle_live.py"

# sim_standing.py's own water and CFL constants, not re-derived here
WATER_DENSITY = 1000.0
WATER_ETA = 1.0e-3
BULK_MODULUS = 1.5e5
EOS_GAMMA = 1.1          # the 1.1 inside sim_standing.py:227's sound speed
FPS = 30

# add_sdf_collider engine defaults, not tuned
COLLIDER_SURFACE = "separable"
COLLIDER_FRICTION = 0.4

SDF_MARGIN_CELLS = 6.0   # box_sdf_collider_setup.py:13
WN_CHUNK = 128


def load_vetted_loader():
    """Import the as-ran vehicle_live module by path. It must be registered in
    sys.modules BEFORE exec_module or its @dataclass decorators fail."""
    if not LOADER_PATH.exists():
        raise SystemExit("vetted loader not found: %s" % LOADER_PATH)
    spec = importlib.util.spec_from_file_location("vehicle_live_asran", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vehicle_live_asran"] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "solidify_watertight") or not hasattr(mod, "is_gaussian_ply"):
        raise SystemExit("loader at %s is not the as-ran patched copy" % LOADER_PATH)
    return mod


def canonicalize(v):
    """Verbatim from renders/yaris_render_s1/sim_standing.py:97-106. Re-centres in
    x and y, puts the mesh floor at z = 0, and recomputes extent FROM THE MESH
    rather than from the 60k surface samples. That distinction is what makes dx
    reproduce the published class_rogue_g64 value."""
    mv = np.asarray(v.mesh.vertices, dtype=np.float64)
    lo, hi = mv.min(0), mv.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    mv = mv - shift
    v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces), process=False)
    v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
    v.extent = mv.max(0) - mv.min(0)
    v.spacing = float(v.extent.max()) / 32.0
    return v


def build_hull_sdf(mesh, res, cache_dir):
    """Stock warpmpm build_sdf_cached, with only the winding-number point-chunk
    reduced. See the module docstring: that change is a numerical identity."""
    from warpmpm.geometry import mesh_sdf as _ms
    _orig = _ms._winding_number
    _ms._winding_number = lambda p, vt, f, chunk=WN_CHUNK: _orig(p, vt, f, chunk=chunk)
    try:
        from warpmpm.geometry import build_sdf_cached
        return build_sdf_cached(
            np.asarray(mesh.vertices, dtype=np.float64),
            np.asarray(mesh.faces, dtype=np.int64),
            res=int(res), margin_cells=SDF_MARGIN_CELLS, cache_dir=str(cache_dir))
    finally:
        _ms._winding_number = _orig


def sdf_nearest(sdf, pts_body):
    """Nearest-cell SDF lookup, used only to carve water out of the hull interior
    at t = 0. Nearest rather than trilinear costs at most half a cell of error,
    which is small against the contact band it is compared to."""
    idx = np.rint((pts_body - np.asarray(sdf.origin)) / float(sdf.cell)).astype(np.int64)
    res = int(np.asarray(sdf.values).shape[0])
    outside = np.any((idx < 0) | (idx >= res), axis=1)
    idx = np.clip(idx, 0, res - 1)
    val = np.asarray(sdf.values)[idx[:, 0], idx[:, 1], idx[:, 2]]
    return np.where(outside, np.inf, val)


class MovingVehicleScene:
    """Still water, one prescribed-velocity hull. See module docstring."""

    def __init__(self, mesh, surface_pts, sdf, depth, velocity, n_grid,
                 device="auto", seed=0):
        ext = mesh.extents
        self.ext = np.asarray(ext, dtype=float)
        self.velocity = float(velocity)
        self.depth = float(depth)

        # domain and grid: sim_standing.py:159-161
        lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
        from warpmpm.core.solver import GridConfig, Solver
        from warpmpm.materials import newtonian
        grid = GridConfig(n_grid=int(n_grid), grid_lim=lim)
        dx = grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        wall = 4.0 * dx
        self.lim, self.dx, self.h, self.floor, self.wall = lim, dx, h, floor, wall

        # placement. x centred across the channel; y set back so the hull clears
        # both walls for the whole run. z = floor because canonicalize() put the
        # mesh floor at exactly z = 0, so center z = floor rests it on the bed.
        half_len = float(ext[1]) / 2.0
        clearance = 2.0 * dx
        self.y_start = wall + half_len + clearance
        self.center0 = np.array([0.50 * lim, self.y_start, floor], dtype=float)
        self.half_len = half_len
        self.travel_available = (lim - wall - clearance) - (self.y_start + half_len)

        # water block: sim_standing.py:176-183
        rng = np.random.default_rng(seed)
        xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        ys = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        self.water_layers = len(zs)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)
        n_before = len(water)

        # carve the hull interior out of the water
        band = dx
        inside = sdf_nearest(sdf, water - self.center0) < band
        water = water[~inside].astype(np.float32)
        self.n_carved = int(inside.sum())
        self.n_water_before_carve = int(n_before)
        self.n_water = len(water)

        vol = np.full(len(water), h ** 3, dtype=np.float32)
        s = Solver(grid=grid, device=device).load_particles(water, vol)
        s.set_material(newtonian(eta=WATER_ETA, density=WATER_DENSITY,
                                 bulk_modulus=BULK_MODULUS))
        # planes act on water only here: see module docstring
        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
        for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                        ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
        s.add_domain_walls()

        # collider enters AT REST so the settle phase is hydrostatic
        self.handle = s.add_sdf_collider(
            sdf, center=tuple(self.center0), quat=(0.0, 0.0, 0.0, 1.0),
            velocity=(0.0, 0.0, 0.0), omega=(0.0, 0.0, 0.0),
            surface=COLLIDER_SURFACE, friction=COLLIDER_FRICTION)
        self.solver = s
        self.sdf = sdf
        self.surface_pts = np.asarray(surface_pts, dtype=np.float32)

        # CFL and substeps: sim_standing.py:227-233, verbatim
        c = float(np.sqrt(EOS_GAMMA * BULK_MODULUS / WATER_DENSITY))
        self.term_acoustic = c / (0.28 * dx)
        self.term_viscous = 6.0 * WATER_ETA / (WATER_DENSITY * dx * dx)
        self.term_advective = max(self.velocity, 1e-6) / (0.5 * dx)
        rate = max(self.term_acoustic, self.term_viscous, self.term_advective)
        self.sound_speed = c
        self.substeps = int(np.ceil(rate / FPS))
        self.dt = (1.0 / FPS) / self.substeps
        self.frame_dt = 1.0 / FPS
        # the engine's own tunneling guard threshold, reported so it is visible
        self.sweep_per_substep = self.velocity * self.dt

        # band-to-depth ratio. The contact band defaults to dx, so at coarse n_grid
        # it is a large fraction of the water column and the wrench is then
        # dominated by band effects rather than by hull geometry. Reported, not hidden.
        self.band_over_depth = dx / float(depth)
        self.time = 0.0
        self.settle_trace = []

    def settle(self, frames, report_every=10):
        """Hold the collider at rest and let the water reach hydrostatic equilibrium.
        The vertical reaction here is the one quantity in this scene with an
        independent analytic target, rho*g*V_submerged, so the trace is the
        physical check on the coupling, not just a warm-up."""
        for i in range(int(frames)):
            self.solver.reset_sdf_force(self.handle)
            self.solver.step(self.dt, self.substeps)
            if (i + 1) % report_every == 0 or i == frames - 1:
                w = self.solver.sdf_wrench(self.handle, self.frame_dt)
                f = np.asarray(w["force"], dtype=float)
                p = self.surface_probe()
                rec = {"settle_frame": i + 1, "t_s": (i + 1) / FPS,
                       "force_N": f.tolist(), "fz_N": float(f[2])}
                rec.update(p)
                self.settle_trace.append(rec)
        return self.settle_trace

    def collider_center(self):
        """Read the collider's ACTUAL centre back out of the engine. This is the
        direct evidence that modify_bc advanced the pose, rather than an
        assumption that it did."""
        c = self.solver._sim.collider_params[self.handle].center
        return np.array([float(c[0]), float(c[1]), float(c[2])], dtype=float)

    def set_drive_speed(self, v):
        self.solver.set_sdf_pose(self.handle, velocity=(0.0, float(v), 0.0))

    def start_motion(self):
        self.set_drive_speed(self.velocity)

    def step_frame(self):
        s = self.solver
        s.reset_sdf_force(self.handle)
        s.step(self.dt, self.substeps)
        self.time += self.frame_dt
        return s.sdf_wrench(self.handle, self.frame_dt)

    def surface_probe(self, window=1.0, half_width=1.5, nbins=90, far_gap=3.0):
        """Free-surface anomaly ahead of the bow and behind the stern, measured
        against the INSTANTANEOUS FAR-FIELD surface in the same frame, not against
        floor + depth.

        Measuring against floor + depth is wrong and was wrong in the first smoke
        run: the discrete free surface is the top particle layer, which sits at
        floor + (layers - 0.5)*h, so floor + depth bakes in a fixed negative offset
        of -0.0281 m at n_grid 48 and -0.0145 m at n_grid 64. Referencing the
        far field removes that offset and also removes any global settling drift,
        which is what a bow wave has to be distinguished from."""
        x = self.solver.x()
        cy = self.collider_center()[1]
        lat = np.abs(x[:, 0] - self.center0[0]) < half_width
        xs = x[lat]
        edges = np.linspace(0.0, self.lim, nbins + 1)
        mid = 0.5 * (edges[1:] + edges[:-1])
        prof = np.full(nbins, -np.inf)
        if len(xs):
            idx = np.clip(np.digitize(xs[:, 1], edges) - 1, 0, nbins - 1)
            np.maximum.at(prof, idx, xs[:, 2])
        prof = np.where(np.isfinite(prof), prof, np.nan)

        far = (np.abs(mid - cy) > far_gap) & np.isfinite(prof)
        z_far = float(np.nanmedian(prof[far])) if far.any() else float("nan")
        # An MPM plane BC is enforced on GRID NODES, so particles can sit up to about
        # one cell below it. At 1.4 cells of water depth that penetration depth is a
        # large fraction of the column, which is the resolution failure this scene
        # has to report rather than hide.
        out = {"z_far_m": z_far,
               "frac_below_floor": float((x[:, 2] < self.floor).mean()),
               "zmin_m": float(x[:, 2].min()),
               "floor_penetration_dx": float((self.floor - x[:, 2].min()) / self.dx)}
        bow = (mid >= cy + self.half_len) & (mid < cy + self.half_len + window)
        stern = (mid > cy - self.half_len - window) & (mid <= cy - self.half_len)
        for name, sel in (("bow", bow), ("stern", stern)):
            v = prof[sel & np.isfinite(prof)]
            out["eta_%s_m" % name] = float(v.max() - z_far) if len(v) else float("nan")
            out["n_%s_bins" % name] = int(len(v))
        return out


def main():
    ap = argparse.ArgumentParser(
        description="NON-CANONICAL kinematic driven-hull scene, see module docstring")
    ap.add_argument("--hull", required=True, help="path to a watertight hull .ply")
    ap.add_argument("--label", default="rogue")
    ap.add_argument("--velocity", type=float, default=1.0,
                    help="prescribed drive speed along +y, m/s. 1.0 gives depth "
                         "Froude 0.583 at depth 0.30 m, comfortably subcritical.")
    ap.add_argument("--depth", type=float, default=0.30)
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--sdf-res", type=int, default=64)
    ap.add_argument("--frames", type=int, default=90)
    ap.add_argument("--settle-frames", type=int, default=60,
                    help="sim_standing.py uses 8, but 8 frames is 0.27 s against a "
                         "10.44 m / 12.85 m/s = 0.81 s acoustic transit, so the "
                         "pressure field has not equilibrated. 60 frames is 2.0 s, "
                         "about 2.5 transits.")
    ap.add_argument("--settle-only", action="store_true",
                    help="run the at-rest phase and stop. The at-rest vertical reaction "
                         "against rho*g*V_sub is the only quantity in this scene with an "
                         "independent analytic target, so this is the resolution probe.")
    ap.add_argument("--settle-report", type=int, default=10)
    ap.add_argument("--ramp-frames", type=int, default=15,
                    help="linearly ramp the drive speed from 0 over this many frames. 0 "
                         "gives a step change, which injects an added-mass impulse.")
    ap.add_argument("--mesh-seed", type=int, default=0,
                    help="seeds numpy's global RNG before load_vehicle so its 60k random "
                         "surface sampling, and therefore the SDF cache key, is "
                         "reproducible. Without this the cache never hits.")
    ap.add_argument("--fill-pitch", type=float, default=0.03,
                    help="pitch for the solidify_watertight interior fill used ONLY to "
                         "compute the analytic buoyancy anchor; it never enters the solve")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=str(REPO / "out" / "moving_vehicle"))
    ap.add_argument("--sdf-cache", default=str(REPO / "out" / "sdf_cache_rogue"))
    ap.add_argument("--dump-stride", type=int, default=1)
    ap.add_argument("--particle-stride", type=int, default=2,
                    help="subsample factor for the dumped water positions")
    args = ap.parse_args()

    print("NON-CANONICAL / EXPLORATORY. Kinematic driven-hull scene.")
    print("The vehicle is DRIVEN and does not respond to the water. No FORD verdict "
          "is implied or reportable from this scene.", flush=True)

    vl = load_vetted_loader()
    t0 = time.time()
    # SEED FIRST. load_vehicle draws 60,000 RANDOM surface samples and derives the
    # mesh shift from them, so v.mesh is not bit-reproducible across calls;
    # canonicalize cancels that shift mathematically but not bitwise and a 1 ULP
    # residue survives. Measured 2026-08-11: unseeded back-to-back loads differ by
    # 2.22e-16 m, which is physically nothing but changes build_sdf_cached's content
    # hash, so the cache NEVER hits and every run rebuilds the SDF (about 8 minutes
    # at res 32, 45 at res 64). Seeded loads are bitwise identical.
    np.random.seed(args.mesh_seed)
    # spacing only sets the interior particle fill pitch, which this kinematic
    # scene never uses; v.mesh is independent of it. Kept coarse so the load is cheap.
    veh = canonicalize(vl.load_vehicle(args.hull, up="z", spacing=0.40))
    mesh = veh.mesh
    print("hull %s: %d verts %d faces watertight=%s volume %.6f m3 (%.1f s)"
          % (Path(args.hull).name, len(mesh.vertices), len(mesh.faces),
             mesh.is_watertight, float(mesh.volume), time.time() - t0), flush=True)
    print("canonicalized extent (x,y,z) = %.6f %.6f %.6f, long axis on y"
          % tuple(veh.extent), flush=True)

    t0 = time.time()
    sdf = build_hull_sdf(mesh, args.sdf_res, args.sdf_cache)
    print("SDF res=%d cell=%.6f m sdf_max=%.4f m (%.1f s, cached at %s)"
          % (args.sdf_res, sdf.cell, sdf.sdf_max, time.time() - t0, args.sdf_cache), flush=True)

    # analytic anchor: rho*g*V_submerged, from the repo's own vetted interior fill.
    # This never enters the solve. It is the one independent target the at-rest
    # vertical reaction can be checked against.
    t0 = time.time()
    fill = vl.solidify_watertight(mesh, args.fill_pitch)
    v_fill = len(fill) * args.fill_pitch ** 3
    v_sub = float((np.asarray(fill)[:, 2] < args.depth).sum()) * args.fill_pitch ** 3
    f_buoy = WATER_DENSITY * 9.81 * v_sub
    print("interior fill at pitch %.3f m: V %.6f m3 vs mesh %.6f (%+.2f%%); submerged "
          "below z=%.2f m: %.6f m3 -> analytic buoyancy %.1f N (%.1f s)"
          % (args.fill_pitch, v_fill, float(mesh.volume),
             100.0 * (v_fill - mesh.volume) / mesh.volume, args.depth, v_sub, f_buoy,
             time.time() - t0), flush=True)

    scene = MovingVehicleScene(mesh, veh.surface, sdf, depth=args.depth,
                               velocity=args.velocity, n_grid=args.n_grid,
                               device=args.device)

    fr = args.velocity / float(np.sqrt(9.81 * args.depth))
    required = args.velocity * args.frames / FPS
    print("domain %.6f m, n_grid %d, dx %.6f m, water layers %d, %d water particles "
          "(%d carved from %d)" % (scene.lim, args.n_grid, scene.dx, scene.water_layers,
                                   scene.n_water, scene.n_carved, scene.n_water_before_carve),
          flush=True)
    print("CFL: c %.4f m/s, acoustic %.2f /s, advective %.2f /s -> substeps %d, dt %.6e s"
          % (scene.sound_speed, scene.term_acoustic, scene.term_advective,
             scene.substeps, scene.dt), flush=True)
    print("collider sweep %.3f mm/substep against contact band %.1f mm"
          % (scene.sweep_per_substep * 1e3, scene.dx * 1e3), flush=True)
    print("LIMITATION: contact band = dx = %.4f m is %.0f percent of the %.2f m water "
          "depth. At that ratio the wrench is shaped by the band as much as by the hull."
          % (scene.dx, 100.0 * scene.band_over_depth, args.depth), flush=True)
    print("depth Froude %.3f; travel needed %.3f m, available %.3f m"
          % (fr, required, scene.travel_available), flush=True)
    if required > scene.travel_available:
        raise SystemExit(
            "REFUSED: %d frames at %.2f m/s needs %.3f m of travel but only %.3f m is "
            "clear of the far wall. Reduce --frames or --velocity."
            % (args.frames, args.velocity, required, scene.travel_available))

    outdir = Path(args.out) / args.label
    outdir.mkdir(parents=True, exist_ok=True)

    print("\nsettling %d frames (%.2f s) with the collider AT REST. Fz should approach "
          "the analytic %.1f N." % (args.settle_frames, args.settle_frames / FPS, f_buoy),
          flush=True)
    for rec in scene.settle(args.settle_frames, report_every=args.settle_report):
        print("  settle f%04d t=%6.2f s  Fz=%10.2f N (%.3f x analytic)  z_far=%.4f  "
              "below_floor=%.1f%%  pen=%.2f dx"
              % (rec["settle_frame"], rec["t_s"], rec["fz_N"], rec["fz_N"] / f_buoy,
                 rec["z_far_m"], 100 * rec["frac_below_floor"],
                 rec["floor_penetration_dx"]), flush=True)
    fz_end = scene.settle_trace[-1]["fz_N"] if scene.settle_trace else float("nan")
    print("SETTLED Fz = %.2f N against analytic %.1f N, ratio %.4f  "
          "[water depth %.2f grid cells; the validated C1-SDF harness uses 18]\n"
          % (fz_end, f_buoy, fz_end / f_buoy, args.depth / scene.dx), flush=True)
    if args.settle_only:
        (Path(args.out) / args.label).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / args.label / "settle_only.json").write_text(json.dumps({
            "label": args.label, "n_grid": args.n_grid, "dx_m": scene.dx,
            "depth_cells": args.depth / scene.dx, "water_layers": int(scene.water_layers),
            "band_over_depth": scene.band_over_depth,
            "analytic_buoyancy_N": f_buoy, "v_submerged_m3": v_sub,
            "settled_fz_N": fz_end, "settled_fz_over_analytic": fz_end / f_buoy,
            "n_water": int(scene.n_water), "sdf_res": args.sdf_res,
            "settle_frames": args.settle_frames, "trace": scene.settle_trace}, indent=2))
        print("settle-only mode, no motion phase. wrote %s"
              % (Path(args.out) / args.label / "settle_only.json"), flush=True)
        return 0

    scene.time = 0.0
    if args.ramp_frames > 0:
        print("motion starts with a %d frame (%.2f s) linear ramp to %.3f m/s. A step "
              "change would inject an added-mass impulse: about %.0f kg of displaced water "
              "accelerated inside one substep. Ramp frames are marked in_ramp and are not "
              "a steady reading."
              % (args.ramp_frames, args.ramp_frames / FPS, args.velocity,
                 WATER_DENSITY * v_sub), flush=True)
        scene.set_drive_speed(args.velocity / args.ramp_frames)
    else:
        scene.start_motion()
        print("motion started, velocity (0, %.3f, 0) m/s, no ramp" % args.velocity, flush=True)

    rows = []
    frames_xyz = []
    frame_centers = []
    nonfinite = 0
    t_run = time.time()
    for i in range(args.frames):
        in_ramp = i < args.ramp_frames
        if args.ramp_frames > 0 and i < args.ramp_frames:
            scene.set_drive_speed(args.velocity * (i + 1) / args.ramp_frames)
        w = scene.step_frame()
        f = np.asarray(w["force"], dtype=float)
        tq = np.asarray(w["torque"], dtype=float)
        if not (np.all(np.isfinite(f)) and np.all(np.isfinite(tq))):
            nonfinite += 1
        c = scene.collider_center()
        probe = scene.surface_probe()
        row = {"frame": i + 1, "t_s": scene.time,
               "center_y_m": c[1], "center_y_expected_m": scene.y_start + args.velocity * scene.time,
               "force_N": f.tolist(), "torque_Nm": tq.tolist(),
               "force_mag_N": float(np.linalg.norm(f)),
               "fz_over_analytic": float(f[2] / f_buoy), "in_ramp": bool(in_ramp),
               "finite": bool(np.all(np.isfinite(f)) and np.all(np.isfinite(tq)))}
        row.update(probe)
        rows.append(row)
        if (i % args.dump_stride) == 0 or i == args.frames - 1:
            x = scene.solver.x()
            frames_xyz.append(x[::args.particle_stride].astype(np.float32))
            frame_centers.append(c.astype(np.float32))
        if i < 5 or (i + 1) % 10 == 0 or i == args.frames - 1:
            print("f%03d t=%6.3f s  y=%7.4f m  Fy=%9.2f  Fz=%10.2f (%.2fx buoy)  "
                  "eta_bow=%+.4f eta_stern=%+.4f  z_far=%.4f"
                  % (i + 1, scene.time, c[1], f[1], f[2], f[2] / f_buoy,
                     row["eta_bow_m"], row["eta_stern_m"], row["z_far_m"]), flush=True)
    wall_s = time.time() - t_run

    meta = {
        "NON_CANONICAL": True,
        "scene_type": "kinematic prescribed-velocity SDF collider, vehicle does not "
                      "respond to the water; no FORD verdict is derivable",
        "hull": str(args.hull), "label": args.label,
        "hull_faces": int(len(mesh.faces)), "hull_watertight": bool(mesh.is_watertight),
        "hull_volume_m3": float(mesh.volume),
        "extent_xyz_m": [float(q) for q in veh.extent],
        "velocity_ms": args.velocity, "drive_axis": "+y (hood first)",
        "depth_m": args.depth, "depth_froude": float(fr),
        "n_grid": args.n_grid, "grid_lim_m": scene.lim, "dx_m": scene.dx,
        "water_layers": int(scene.water_layers),
        "n_water": int(scene.n_water), "n_carved": int(scene.n_carved),
        "analytic_buoyancy_N": float(f_buoy),
        "v_submerged_m3": float(v_sub), "fill_pitch_m": args.fill_pitch,
        "fill_volume_m3": float(v_fill),
        "settled_fz_N": float(fz_end), "settled_fz_over_analytic": float(fz_end / f_buoy),
        "settle_trace": scene.settle_trace,
        "band_over_depth": float(scene.band_over_depth),
        "sdf_res": args.sdf_res, "sdf_cell_m": float(sdf.cell),
        "sdf_margin_cells": SDF_MARGIN_CELLS, "winding_chunk": WN_CHUNK,
        "collider_surface": COLLIDER_SURFACE, "collider_friction": COLLIDER_FRICTION,
        "plane_friction": 0.0, "plane_restitution": 0.0,
        "bulk_modulus": BULK_MODULUS, "water_eta": WATER_ETA,
        "water_density": WATER_DENSITY, "sound_speed_ms": scene.sound_speed,
        "substeps": int(scene.substeps), "dt_s": scene.dt, "fps": FPS,
        "frames": args.frames, "settle_frames": args.settle_frames,
        "ramp_frames": args.ramp_frames, "mesh_seed": args.mesh_seed,
        "travel_m": float(args.velocity * args.frames / FPS),
        "travel_hull_lengths": float(args.velocity * args.frames / FPS / scene.ext[1]),
        "nonfinite_frames": int(nonfinite),
        "wall_time_s": wall_s, "device": args.device,
    }
    (outdir / "meta.json").write_text(json.dumps(meta, indent=2))
    (outdir / "frames.json").write_text(json.dumps(rows, indent=2))
    np.savez_compressed(
        outdir / "rollout.npz",
        water=np.stack(frames_xyz) if len(set(len(a) for a in frames_xyz)) == 1
        else np.array(frames_xyz, dtype=object),
        centers=np.stack(frame_centers),
        hull_surface=scene.surface_pts[::4],
        floor=scene.floor, depth=args.depth, lim=scene.lim, dx=scene.dx)

    print("\n%d frames in %.1f s (%.2f s/frame). non-finite wrench frames: %d"
          % (args.frames, wall_s, wall_s / max(args.frames, 1), nonfinite), flush=True)
    print("wrote %s" % outdir, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
