from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh

from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian
from warpmpm.vehicle import FloodHistory, load_vehicle, solidify_watertight

VEHICLE_DIR = Path("/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research")
YARIS = VEHICLE_DIR / "yaris_coarse_v1l_watertight.ply"

# Published volume of the canonical Yaris hull (vehicle_geometry_research/
# WATERTIGHT_HULL_TOOL_FINDINGS.md), kept as a REFERENCE ANCHOR only.
# It must never be the fill_ratio denominator. Using it as one made every
# non-Yaris --vehicle run silently report the Yaris hull volume and a
# fill_ratio computed against the wrong denominator, while still looking
# plausible. Corrected 2026-08-08; see docs/MESH_RECONCILIATION_2026-08-08.md
# section 7. The live denominator is hull_m3, derived from the loaded mesh.
HULL_YARIS_REF = 3.542739

# --vehicle takes a short name from this registry OR an explicit .ply path. The path form
# predates the registry and still works, so no existing invocation changes.
#
# hull_m3 here is the PREFLIGHT EXPECTATION only, re-measured live 2026-08-08 with
# trimesh.load(force="mesh"), the loader the 17 gated runs actually ran. It is never a
# denominator. The denominator is always the volume of the mesh actually loaded, for the
# reason recorded against HULL_YARIS_REF above.
#
# mass_kg is the AR&R class figure, matching the class labels the Yaris runs already use
# (gates_both_scenarios.py:19-23 and gates_all_runs.py:20-21). mass_alt_kg is the
# vehicle-specific figure, carried as a labelled secondary so it is never silently dropped.
# The two disagree and are never merged.
VEHICLES = {
    "yaris": {
        "path": YARIS,
        "hull_m3": 3.542739,
        "vehicle_class": "small_passenger",
        "mass_kg": 1100.0,
        "mass_source": "vehicle_params.py mass_kg 1100.0; also Yaris deck header line 28",
        "mass_alt_kg": None,
        "mass_alt_source": None,
    },
    "rogue": {
        "path": VEHICLE_DIR / "rogue_g96_pd8_coarse_watertight.ply",
        "hull_m3": 4.950341,
        "vehicle_class": "large_passenger",
        "mass_kg": 1609.0,
        "mass_source": "AR&R large_passenger class figure (gates_both_scenarios.py:22)",
        "mass_alt_kg": 1571.3,
        "mass_alt_source": "Rogue web-sourced curb mass; the Rogue deck states no mass at all",
    },
    "silverado": {
        "path": VEHICLE_DIR / "silverado_g96_pd8_coarse_watertight.ply",
        "hull_m3": 7.962083,
        "vehicle_class": "large_4wd",
        "mass_kg": 2337.0,
        "mass_source": "AR&R large_4wd class figure (gates_both_scenarios.py:23)",
        "mass_alt_kg": 2270.0,
        "mass_alt_source": "Silverado deck header line 28 mass",
    },
}

# Retracted 2026-08-08 by vehicle_meshes/candidates/SUMMARY.md. Both were selected on
# euler_number closest to 2, which selects for coarseness, which is exactly what erodes
# volume, and volume feeds buoyancy directly: they sit 47.53 and 31.40 percent below their
# own converged volume. They were kept on disk rather than deleted, so a path can still
# reach them. This blocks that path.
RETRACTED_HULL_TOKENS = ("candidate_euler",)


def resolve_vehicle(spec):
    """Map a --vehicle value to (key, path, registry entry or None for a custom path)."""
    key = str(spec).strip().lower()
    if key in VEHICLES:
        return key, Path(VEHICLES[key]["path"]), VEHICLES[key]

    path = Path(spec)
    for tok in RETRACTED_HULL_TOKENS:
        if tok in path.name:
            raise SystemExit(
                "REFUSED retracted hull '%s'. Meshes matching '%s' were withdrawn "
                "2026-08-08 (vehicle_meshes/candidates/SUMMARY.md): they are %s below "
                "their converged volume. Use --vehicle rogue or --vehicle silverado for "
                "the converged g96_pd8 hulls." % (path.name, tok, "31 to 48 percent"))
    for k, entry in VEHICLES.items():
        if Path(entry["path"]) == path:
            return k, path, entry
    return "custom", path, None


def canonicalize(v):
    mv = np.asarray(v.mesh.vertices, dtype=np.float64)
    lo, hi = mv.min(0), mv.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    mv = mv - shift
    v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces), process=False)
    v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
    v.extent = mv.max(0) - mv.min(0)
    v.spacing = float(v.extent.max()) / 32.0
    return v


def count_odd_columns(mesh, h):
    v = np.asarray(mesh.vertices, dtype=np.float64)
    f = np.asarray(mesh.faces)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    lo, hi = v.min(0), v.max(0)
    nx = int(np.ceil((hi[0] - lo[0]) / h)); ny = int(np.ceil((hi[1] - lo[1]) / h))
    ox, oy = lo[0] + h / 2, lo[1] + h / 2
    tlo = np.minimum(np.minimum(a, b), c); thi = np.maximum(np.maximum(a, b), c)
    i0 = np.clip(np.ceil((tlo[:, 0] - ox) / h).astype(np.int64), 0, nx - 1)
    i1 = np.clip(np.floor((thi[:, 0] - ox) / h).astype(np.int64), 0, nx - 1)
    j0 = np.clip(np.ceil((tlo[:, 1] - oy) / h).astype(np.int64), 0, ny - 1)
    j1 = np.clip(np.floor((thi[:, 1] - oy) / h).astype(np.int64), 0, ny - 1)
    ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0)
    cnt = ni * nj
    idx = np.flatnonzero(cnt > 0)
    CI, CJ, CT = [], [], []
    for s0 in range(0, len(idx), 20000):
        blk = idx[s0:s0 + 20000]
        n = cnt[blk]
        off = np.arange(int(n.sum())) - np.repeat(np.cumsum(n) - n, n)
        njr = np.repeat(nj[blk], n)
        CI.append(np.repeat(i0[blk], n) + off // njr)
        CJ.append(np.repeat(j0[blk], n) + off % njr)
        CT.append(np.repeat(blk, n))
    ci = np.concatenate(CI); cj = np.concatenate(CJ); ct = np.concatenate(CT)
    px = ox + ci * h; py = oy + cj * h
    a2, b2, c2 = a[ct], b[ct], c[ct]
    d = (b2[:, 1] - c2[:, 1]) * (a2[:, 0] - c2[:, 0]) + (c2[:, 0] - b2[:, 0]) * (a2[:, 1] - c2[:, 1])
    ok = np.abs(d) > 1e-14
    dd = np.where(ok, d, 1.0)
    w0 = np.where(ok, ((b2[:, 1] - c2[:, 1]) * (px - c2[:, 0]) + (c2[:, 0] - b2[:, 0]) * (py - c2[:, 1])) / dd, -1.0)
    w1 = np.where(ok, ((c2[:, 1] - a2[:, 1]) * (px - c2[:, 0]) + (a2[:, 0] - c2[:, 0]) * (py - c2[:, 1])) / dd, -1.0)
    w2 = 1.0 - w0 - w1
    hit = ok & (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    ci, cj = ci[hit], cj[hit]
    col = ci * ny + cj
    col = np.sort(col)
    starts = np.flatnonzero(np.r_[True, col[1:] != col[:-1]])
    runs = np.diff(np.r_[starts, len(col)])
    n_odd = int((runs % 2 != 0).sum())
    return n_odd, int(len(runs))


class StandingFloodScene:
    def __init__(self, vehicle, depth, velocity, vehicle_mass, n_grid=64,
                 water_density=1000.0, water_eta=1.0e-3, bulk_modulus=1.5e5,
                 fps=30, floor_friction=0.55, settle_frames=8, device="auto",
                 seed=0, inflow_len=1.5):
        self.vehicle = vehicle
        self.fps = fps
        self.velocity = velocity
        ext = vehicle.extent
        lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
        self.grid = GridConfig(n_grid=n_grid, grid_lim=lim)
        dx = self.grid.dx
        h = dx / 2.0
        floor = 3.0 * dx
        rng = np.random.default_rng(seed)

        if vehicle.spacing > 1.2 * h:
            vehicle.solidify(h)

        solid_volume = vehicle.n_particles * h ** 3
        vehicle_density = vehicle_mass / solid_volume
        self.vehicle_mass = vehicle_density * solid_volume

        vx, vy = 0.60 * lim, 0.50 * lim
        self._place = np.array([vx, vy, floor + 0.5 * h], dtype=np.float32)
        truck = vehicle.particles + self._place

        wall = 4.0 * dx
        xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        ys = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
        zs = np.arange(floor + 0.5 * h, floor + depth, h)
        water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        water = (water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)).astype(np.float32)
        n_before = len(water)

        vk = np.floor(np.asarray(truck, dtype=np.float64) / h).astype(np.int64)
        wk = np.floor(np.asarray(water, dtype=np.float64) / h).astype(np.int64)
        base = vk.min(0)
        span = (vk.max(0) - base + 1).astype(np.int64)
        vlin = np.ravel_multi_index((vk - base).T, span)
        inside = np.all((wk >= base) & (wk <= vk.max(0)), axis=1)
        wlin = np.full(len(water), -1, dtype=np.int64)
        wlin[inside] = np.ravel_multi_index((wk[inside] - base).T, span)
        occupied = np.isin(wlin, np.unique(vlin)) & inside
        water = water[~occupied]
        self.n_carved = int(occupied.sum())
        self.n_water_before_carve = int(n_before)

        pos = np.concatenate([water, truck])
        vol = np.full(len(pos), h ** 3, dtype=np.float32)
        self.n_water = len(water)
        self.n_total = len(pos)

        s = Solver(grid=self.grid, device=device).load_particles(pos, vol)
        s.set_material(newtonian(eta=water_eta, density=water_density,
                                 bulk_modulus=bulk_modulus))
        s.set_material_range(self.n_water, self.n_total, "rigid", obj_id=0,
                             density=vehicle_density)
        s.finalize_rigid_bodies()
        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
                    restitution=0.05)
        for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                        ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
            s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
        s.add_domain_walls()
        self.solver = s
        self.floor = floor
        self.h = h
        self.dx = dx
        self._wall = wall
        self._lim = lim
        self.leaked = 0
        self._inflow_x = wall + inflow_len

        c = float(np.sqrt(1.1 * bulk_modulus / water_density))
        self.term_acoustic = c / (0.28 * dx)
        self.term_viscous = 6.0 * water_eta / (water_density * dx * dx)
        self.term_advective = max(velocity, 1e-6) / (0.5 * dx)
        rate = max(self.term_acoustic, self.term_viscous, self.term_advective)
        self.sound_speed = c
        self.bulk_modulus = float(bulk_modulus)
        self.substeps = int(np.ceil(rate / fps))
        self.dt = (1.0 / fps) / self.substeps

        for _ in range(settle_frames):
            self._project_water()
            s.step(self.dt, self.substeps)

        v = s.v()
        v[: self.n_water, 0] += velocity
        s.set_v(v)

        self.com0 = s.rigid_state()["com"].copy()
        self.time = 0.0
        self.history = FloodHistory()
        self.history.append(0.0, s.rigid_state(), self.com0)

    def _project_water(self):
        s = self.solver
        x = s.x()
        w = x[: self.n_water]
        eps = 0.25 * self.grid.dx
        lo = np.array([self._wall, self._wall, self.floor], dtype=np.float32) - eps
        hi = np.array([self._lim - self._wall, self._lim - self._wall, np.inf],
                      dtype=np.float32) + eps
        out_lo = w < lo
        out_hi = w > hi
        if not (out_lo.any() or out_hi.any()):
            return
        self.leaked += int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
        v = s.v()
        vw = v[: self.n_water]
        np.clip(w, lo, hi, out=w)
        vw[out_lo] = np.maximum(vw[out_lo], 0.0)
        vw[out_hi] = np.minimum(vw[out_hi], 0.0)
        s.set_x(x)
        s.set_v(v)

    def _sustain_inflow(self):
        s = self.solver
        x = s.x()
        v = s.v()
        band = x[: self.n_water, 0] < self._inflow_x
        vw = v[: self.n_water]
        vw[band, 0] = self.velocity
        s.set_v(v)
        return int(band.sum())

    def step(self):
        self._project_water()
        self.n_inflow = self._sustain_inflow()
        self.solver.step(self.dt, self.substeps)
        self.time += 1.0 / self.fps
        st = self.solver.rigid_state()
        self.history.append(self.time, st, self.com0)
        return st

    def vehicle_pose(self):
        st = self.solver.rigid_state()
        com_veh = self.com0 - self._place
        R = st["R"]
        t = st["com"] - R @ com_veh
        return R, t


def main():
    p = argparse.ArgumentParser()
    # --mass stays optional-with-a-registry-default rather than required, so a named
    # --vehicle cannot be paired with the wrong class mass by omission. An explicit
    # --mass still wins, and every existing invocation passes one, so nothing changes.
    p.add_argument("--mass", type=float, default=None)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--depth", type=float, default=0.30)
    p.add_argument("--velocity", type=float, default=1.5)
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--eta", type=float, default=1.0e-3)
    p.add_argument("--floor-friction", type=float, default=0.55)
    p.add_argument("--vehicle", default="yaris",
                   help="yaris (default), rogue, silverado, or an explicit .ply path")
    a = p.parse_args()

    vkey, vpath, ventry = resolve_vehicle(a.vehicle)
    if not vpath.exists():
        raise SystemExit("PREFLIGHT FAIL hull not found: %s" % vpath)

    if a.mass is not None:
        mass = float(a.mass)
        mass_source = ("explicit --mass"
                       if ventry is None or abs(mass - ventry["mass_kg"]) > 1e-9
                       else ventry["mass_source"])
    elif ventry is not None:
        mass = float(ventry["mass_kg"])
        mass_source = ventry["mass_source"]
    else:
        raise SystemExit("--mass is required for a --vehicle path outside the registry")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    v1 = canonicalize(load_vehicle(vpath, up="z"))
    v2 = canonicalize(load_vehicle(vpath, up="z"))

    # Hull volume of the mesh ACTUALLY loaded via --vehicle, not a Yaris literal.
    # canonicalize() applies a pure translation, so mesh volume is invariant under it.
    # abs() guards an inverted winding, which trimesh reports as a negative volume.
    hull_m3 = float(abs(v1.mesh.volume))
    hull_watertight = bool(v1.mesh.is_watertight)
    hull_ref_delta_pct = 100.0 * (hull_m3 - HULL_YARIS_REF) / HULL_YARIS_REF

    h_probe = float(max(2.2 * v1.extent[1], 3.5 * v1.extent[0], 6.0 * a.depth)) / a.grid / 2.0
    v1.solidify(h_probe)
    v2.solidify(h_probe)

    # PREFLIGHT. Everything here is decided from the loaded mesh BEFORE the solver is
    # built, so a wrong or damaged hull costs seconds instead of a full GPU rollout.
    # h_probe is the same h the scene derives (lim / n_grid / 2), so preflight_fill_ratio
    # is the fill_ratio the run will report, not an approximation of it.
    preflight_solid_volume = v1.n_particles * h_probe ** 3
    preflight_fill_ratio = preflight_solid_volume / hull_m3
    print("PREFLIGHT vehicle=%s class=%s hull=%s" % (
        vkey, ventry["vehicle_class"] if ventry else "unregistered", vpath), flush=True)
    print("PREFLIGHT watertight=%s hull_m3=%.6f solid_volume=%.6f fill_ratio=%.4f"
          % (hull_watertight, hull_m3, preflight_solid_volume, preflight_fill_ratio),
          flush=True)
    print("PREFLIGHT mass=%.1f kg source=%s  realized_rho=%.2f kg/m3"
          % (mass, mass_source, mass / preflight_solid_volume), flush=True)
    if ventry is not None and ventry["mass_alt_kg"] is not None:
        print("PREFLIGHT mass_alt=%.1f kg source=%s  realized_rho_alt=%.2f kg/m3"
              % (ventry["mass_alt_kg"], ventry["mass_alt_source"],
                 ventry["mass_alt_kg"] / preflight_solid_volume), flush=True)

    if not hull_watertight:
        raise SystemExit("PREFLIGHT FAIL hull is not watertight: %s. Volume, and therefore "
                         "buoyancy, is undefined for an open mesh." % vpath)
    if ventry is not None:
        pub = ventry["hull_m3"]
        dev = abs(hull_m3 - pub) / pub
        print("PREFLIGHT published_hull_m3=%.6f deviation=%.4f%%" % (pub, 100.0 * dev),
              flush=True)
        if dev > 1e-3:
            raise SystemExit(
                "PREFLIGHT FAIL hull volume %.6f m3 disagrees with the published %.6f m3 "
                "for '%s' by %.3f%%. The file on disk is not the registered hull."
                % (hull_m3, pub, vkey, 100.0 * dev))
    # solidify() fills the hull, so this ratio sits near 1.0 for every gated run so far
    # (0.994 to 1.026 across the 17). This band is a broken-solidify tripwire, deliberately
    # far wider than that spread, and it is NOT a physics gate: gates.py remains the
    # authority on pass and fail.
    if not (0.5 <= preflight_fill_ratio <= 2.0):
        raise SystemExit("PREFLIGHT FAIL fill_ratio %.4f outside [0.5, 2.0]; solidify did "
                         "not fill the hull." % preflight_fill_ratio)

    lim1 = float(max(2.2 * v1.extent[1], 3.5 * v1.extent[0], 6.0 * a.depth))
    lim2 = float(max(2.2 * v2.extent[1], 3.5 * v2.extent[0], 6.0 * a.depth))
    print("DETERMINISM load1 n=%d lim=%.9f" % (v1.n_particles, lim1), flush=True)
    print("DETERMINISM load2 n=%d lim=%.9f" % (v2.n_particles, lim2), flush=True)
    # RENAMED 2026-08-18. Old names: the variable was det_ok and the summary key was
    # determinism_identical. This compares two loads of the SAME hull on a particle COUNT and a
    # grid LIMIT, and on nothing else. It is a hull-load reproducibility check, not a trajectory
    # check, and it cannot detect solver non-determinism: a different random surface sample of
    # the same watertight hull preserves both quantities while placing every particle
    # differently. Repeats at fixed configuration produce bit-different trajectories while this
    # stays True, so the old name asserted something the value never measured. Do not rename it
    # back, and do not read it as evidence that a run is reproducible; compare metrics.csv
    # between repeats for that.
    # The "DETERMINISM " stdout prefix is DELIBERATELY unchanged: scripts/run_three_class_*.sh
    # capture solver logs with an anchored /usr/bin/grep -E '^(...|DETERMINISM|...)', and those
    # scripts are outside this change's scope. Renaming the prefix would silently drop these
    # lines from every captured log.
    hull_load_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
    print("DETERMINISM hull_load_identical=%s (hull load only, NOT trajectory)"
          % hull_load_ok, flush=True)

    n_odd, n_cols = count_odd_columns(v1.mesh, h_probe)
    print("PARITY_ODD_COLUMNS dropped=%d of %d columns (%.4f percent)"
          % (n_odd, n_cols, 100.0 * n_odd / max(n_cols, 1)), flush=True)

    v = v1
    scene = StandingFloodScene(v, depth=a.depth, velocity=a.velocity,
                               vehicle_mass=mass, n_grid=a.grid,
                               water_eta=a.eta, floor_friction=a.floor_friction)

    lim = scene.grid.grid_lim
    dx, h, floor = scene.dx, scene.h, scene.floor
    n_water = scene.n_water
    n_veh = scene.n_total - n_water
    solid_volume = n_veh * h ** 3
    layers = int(len(np.arange(floor + 0.5 * h, floor + a.depth, h)))
    gridline = ("grid %d^3 lim=%.2fm  water %d + vehicle %d particles (%.1f kg)  "
                "dt=%.2e (%d substeps/frame)"
                % (a.grid, lim, n_water, n_veh, scene.vehicle_mass, scene.dt, scene.substeps))
    print("SCENARIO=STANDING_WATER_SUSTAINED_INFLOW", flush=True)
    print(gridline, flush=True)
    print("INSTRUMENT dx=%.6f h=%.6f floor=%.6f lim=%.6f" % (dx, h, floor, lim), flush=True)
    print("INSTRUMENT water_layers=%d" % layers, flush=True)
    print("INSTRUMENT solid_volume=%.5f m3 hull=%.5f fill_ratio=%.4f realized_rho=%.2f"
          % (solid_volume, hull_m3, solid_volume / hull_m3,
             scene.vehicle_mass / solid_volume), flush=True)
    # Hull provenance. yaris_ref_delta_pct is the tripwire that --vehicle took effect:
    # ~0 percent is the Yaris, ~+39.7 the Rogue, ~+124.7 the Silverado.
    print("INSTRUMENT hull_source=%s hull_m3=%.6f watertight=%s yaris_ref_delta_pct=%+.3f"
          % (vpath, hull_m3, hull_watertight, hull_ref_delta_pct), flush=True)
    print("INSTRUMENT carved %d of %d water particles from vehicle cells (%.2f percent)"
          % (scene.n_carved, scene.n_water_before_carve,
             100.0 * scene.n_carved / max(scene.n_water_before_carve, 1)), flush=True)
    print("SUBSTEP_TERMS eta=%.3e acoustic=%.4f viscous=%.6f advective=%.4f -> rate=%.4f substeps=%d"
          % (a.eta, scene.term_acoustic, scene.term_viscous, scene.term_advective,
             max(scene.term_acoustic, scene.term_viscous, scene.term_advective),
             scene.substeps), flush=True)
    print("ACOUSTIC c=%.4f m/s  vehicle_x=%.4f  downstream_wall=%.4f  round_trip=%.4f s"
          % (scene.sound_speed, 0.60 * lim, lim - 4.0 * dx,
             2.0 * (lim - 4.0 * dx - 0.60 * lim) / scene.sound_speed), flush=True)
    print("FLOOR_FRICTION=%.3f  WATER_ETA=%.3e" % (a.floor_friction, a.eta), flush=True)

    pv0 = np.asarray(v.particles, dtype=np.float64)
    W, S, RR, TT = [], [], [], []
    ld_bow, ld_foot = [], []
    checkpoints = {}
    # Frame 45 does not exist when frames <= 45, and the npz write below indexed it
    # unconditionally, so any such run died with KeyError after all the compute was
    # already spent. The npz KEY NAME veh_check_45 is deliberately unchanged:
    # render_hero_g64_m1100_2026-08-06.py:72 reads it by that exact name.
    # At the canonical frames=90 this is min(45, 89) = 45, so nothing changes.
    f_check = min(45, a.frames - 1)
    oob_total = 0
    frac_max = 0.0
    zmin_start = float(scene.solver.x()[n_water:][:, 2].min())

    for f in range(a.frames):
        scene.step()
        x = scene.solver.x()
        vel = scene.solver.v()
        w = x[:n_water]
        veh = x[n_water:]
        R, t = scene.vehicle_pose()

        W.append(w.astype(np.float32))
        S.append(np.linalg.norm(vel[:n_water], axis=1).astype(np.float32))
        RR.append(np.asarray(R, dtype=np.float32))
        TT.append(np.asarray(t, dtype=np.float32))
        if f in (0, f_check, a.frames - 1):
            checkpoints[str(f)] = veh.astype(np.float32)

        oob_total += int(((x < 0.0) | (x > lim)).any(axis=1).sum())
        lo_v, hi_v = veh.min(0), veh.max(0)
        inbox = ((w >= lo_v) & (w <= hi_v)).all(axis=1)
        frac_max = max(frac_max, float(inbox.mean()))

        xf = veh[:, 0].min()
        sel_bow = ((w[:, 0] >= xf - 3.0 * dx) & (w[:, 0] <= xf - 0.5 * dx) &
                   (w[:, 1] >= lo_v[1]) & (w[:, 1] <= hi_v[1]) & (w[:, 2] >= floor))
        ld_bow.append(float(np.percentile(w[sel_bow, 2], 99.5)) - floor
                      if sel_bow.sum() >= 20 else np.nan)
        sel_ft = ((w[:, 0] >= lo_v[0]) & (w[:, 0] <= hi_v[0]) &
                  (w[:, 1] >= lo_v[1]) & (w[:, 1] <= hi_v[1]) & (w[:, 2] >= floor))
        ld_foot.append(float(np.percentile(w[sel_ft, 2], 99.5)) - floor
                       if sel_ft.sum() >= 20 else np.nan)

        if f % 10 == 0 or f == a.frames - 1:
            dd = scene.history.displacement[-1]
            print("frame %3d  |d|=%7.2fcm  yaw=%+6.2f  roll=%+6.2f  ld_bow=%.4f ld_foot=%.4f oob=%d inflow=%d"
                  % (f, float(np.linalg.norm(dd)) * 100, scene.history.yaw[-1],
                     scene.history.roll[-1], ld_bow[-1], ld_foot[-1], oob_total,
                     getattr(scene, "n_inflow", -1)), flush=True)

    scene.history.to_csv(out / "metrics.csv")
    np.savez_compressed(
        out / "rollout.npz",
        water=np.asarray(W, dtype=np.float32), speed=np.asarray(S, dtype=np.float32),
        R=np.asarray(RR, dtype=np.float32), t=np.asarray(TT, dtype=np.float32),
        veh_particles_scene0=checkpoints["0"],
        veh_check_45=checkpoints[str(f_check)], veh_check_last=checkpoints[str(a.frames - 1)],
        veh_particles_vehframe=pv0.astype(np.float32),
        local_depth_bow=np.asarray(ld_bow, dtype=np.float32),
        local_depth_footprint=np.asarray(ld_foot, dtype=np.float32),
        extent=np.asarray(v.extent, dtype=np.float32),
        lim=np.float32(lim), dx=np.float32(dx), h=np.float32(h), floor=np.float32(floor),
        depth=np.float32(a.depth), velocity=np.float32(a.velocity),
        mass=np.float32(scene.vehicle_mass), n_grid=np.int32(a.grid),
        frames=np.int32(a.frames), fps=np.int32(scene.fps),
    )

    d = scene.history.displacement[-1]
    veh_last = scene.solver.x()[n_water:]
    ldb = np.asarray(ld_bow); ldf = np.asarray(ld_foot)
    pk = int(np.nanargmax(ldb))
    summary = {
        "scenario": "standing_water_sustained_inflow",
        "label": a.label, "mass_kg": float(scene.vehicle_mass),
        "depth_m": a.depth, "velocity_ms": a.velocity, "n_grid": a.grid,
        "frames": a.frames, "grid_lim": float(lim), "dx": float(dx), "h": float(h),
        "water_layers": layers, "n_water": int(n_water), "n_vehicle": int(n_veh),
        "n_carved": scene.n_carved, "water_eta": a.eta,
        "floor_friction": a.floor_friction,
        "bulk_modulus": float(scene.bulk_modulus),
        "substeps": int(scene.substeps), "sound_speed_ms": float(scene.sound_speed),
        "term_acoustic": float(scene.term_acoustic),
        "term_viscous": float(scene.term_viscous),
        "term_advective": float(scene.term_advective),
        "solid_volume_m3": float(solid_volume), "hull_m3": hull_m3,
        "fill_ratio": float(solid_volume / hull_m3),
        "hull_source": str(vpath),
        "hull_watertight": hull_watertight,
        "hull_yaris_ref_m3": HULL_YARIS_REF,
        "hull_ref_delta_pct": float(hull_ref_delta_pct),
        "realized_rho": float(scene.vehicle_mass / solid_volume),
        # Vehicle selection and mass provenance. mass_kg above is the PRIMARY (AR&R class)
        # figure the run actually used. mass_alt_kg is the vehicle-specific figure, kept as
        # a labelled secondary: the two disagree and must never be merged or dropped.
        "vehicle_key": vkey,
        "vehicle_class": ventry["vehicle_class"] if ventry else None,
        "mass_source": mass_source,
        "mass_alt_kg": (float(ventry["mass_alt_kg"])
                        if ventry and ventry["mass_alt_kg"] is not None else None),
        "mass_alt_source": ventry["mass_alt_source"] if ventry else None,
        "realized_rho_mass_alt": (float(ventry["mass_alt_kg"] / solid_volume)
                                  if ventry and ventry["mass_alt_kg"] is not None else None),
        "hull_m3_published": (float(ventry["hull_m3"]) if ventry else None),
        "preflight_fill_ratio": float(preflight_fill_ratio),
        "parity_odd_columns_dropped": n_odd, "parity_total_columns": n_cols,
        # FORWARD-ONLY WRITE: new key only. Every summary.json written before
        # 2026-08-18 keeps "determinism_identical"; readers accept both.
        "hull_load_identical": bool(hull_load_ok),
        "final_disp_m": [float(q) for q in d],
        "final_disp_mag_m": float(np.linalg.norm(d)),
        "final_yaw_deg": float(scene.history.yaw[-1]),
        "final_roll_deg": float(scene.history.roll[-1]),
        "final_pitch_deg": float(scene.history.pitch[-1]),
        "C3_oob_particle_frames": int(oob_total),
        "local_depth_bow_peak": float(np.nanmax(ldb)),
        "local_depth_bow_peak_frame": pk,
        "local_depth_bow_final": float(ldb[-1]),
        "local_depth_footprint_peak": float(np.nanmax(ldf)),
        "local_depth_footprint_final": float(ldf[-1]),
        "C2_veh_zmin_start": zmin_start,
        "C2_veh_zmin_final": float(veh_last[:, 2].min()),
        "C2_veh_zmin_rise": float(veh_last[:, 2].min()) - zmin_start,
        "passthrough_max_frac": frac_max,
        "leaked_particle_frames": int(scene.leaked),
        "grid_lim_line_verbatim": gridline,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s" % a.label, flush=True)


if __name__ == "__main__":
    main()
