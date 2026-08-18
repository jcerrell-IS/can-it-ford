"""Flooded roadway: a real cross-section as an SDF collider, with open streamwise faces.

This is the scene the whole open-channel effort was for. It composes three things
that were separately established:

  1. the road itself, `simulation/road_geometry.py`, as an add_sdf_collider
     (solver.py:324). Crown, cross-slope, gutters, kerbs, verges. There is NO
     floor plane in this scene: the road IS the floor. That retires blocker B1,
     "the scene is one frictional plane inside a box".
  2. the streamwise faces opened by the recycler, `simulation/openchannel_bc.py`,
     so water is not piling against a wall. Register item 20 measured what a
     closed box does instead: it manufactures a free-surface slope larger than
     the bed slope of a 3 degree road.
  3. the longitudinal grade as tilted gravity, so the road stays prismatic and
     the grade is exact rather than discretised.

WHAT THIS SCENE CAN MEASURE THAT THE CANONICAL ONE CANNOT.
  - drainage: whether water actually leaves the crown and concentrates in the
    gutters, and how fast. The film is seeded at UNIFORM DEPTH so any gutter
    concentration is produced, not handed over.
  - the reaction wrench on the road, via sdf_wrench (solver.py:354). The
    material-8 free-rigid path used by the 17 canonical runs has no force
    accumulator at all (register A-1), so this is a force the canonical scene
    cannot report.

SDF RESOLUTION IS THE CONSTRAINT TO WATCH. build_sdf makes a CUBIC grid over the
mesh bbox, so a long road spends its resolution on length exactly as the MPM grid
does (blocker B2). The criterion applied here is `sdf.cell <= dx`: at or below the
MPM cell size the SDF resolves everything the water can feel, and finer buys
nothing. The run asserts it rather than assuming it.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from warpmpm.core.solver import GridConfig, Solver          # noqa: E402
from warpmpm.geometry import build_sdf                      # noqa: E402
from warpmpm.materials import newtonian                     # noqa: E402

from openchannel_bc import (                                # noqa: E402
    RecyclingChannelBC, tilted_gravity,
)
from road_geometry import road_profile, road_solid, seed_film  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--lim", type=float, default=8.0)
    p.add_argument("--grid", type=int, default=128)
    p.add_argument("--sdf-res", type=int, default=160)
    p.add_argument("--depth", type=float, default=0.12, help="uniform film depth, m")
    p.add_argument("--velocity", type=float, default=1.0)
    p.add_argument("--frames", type=int, default=240)
    p.add_argument("--grade-deg", type=float, default=0.0)
    p.add_argument("--carriageway", type=float, default=4.0)
    p.add_argument("--cross-slope", type=float, default=0.02)
    p.add_argument("--gutter-depth", type=float, default=0.10)
    p.add_argument("--gutter-width", type=float, default=0.60)
    p.add_argument("--kerb-height", type=float, default=0.15)
    p.add_argument("--road-friction", type=float, default=0.55)
    p.add_argument("--eta", type=float, default=1.0e-3)
    p.add_argument("--bulk", type=float, default=1.5e5)
    p.add_argument("--bc", choices=("closed", "recycle"), default="recycle")
    p.add_argument("--dump-water", type=int, default=0)
    a = p.parse_args()

    lim, fps = float(a.lim), 30
    grid = GridConfig(n_grid=a.grid, grid_lim=lim)
    dx = grid.dx
    h = dx / 2.0
    wall = 4.0 * dx
    W = lim                                   # the road spans the domain in y
    road_z = 0.35 * lim                       # crown height, leaves headroom below and above
    z_base = road_z - 0.25 * lim
    prof = dict(carriageway=a.carriageway, cross_slope=a.cross_slope,
                gutter_depth=a.gutter_depth, gutter_width=a.gutter_width,
                kerb_height=a.kerb_height, crown_z=road_z)

    t0 = time.time()
    verts, faces = road_solid(lim, W, z_base, n_y=100, **prof)
    # Probe a point unambiguously inside the embankment, rather than relying on the
    # centroid: the section is concave (gutters, kerbs) and a centroid-based sign
    # can land in a dish. build_sdf documents this as the fix for concave shells.
    probe = np.array([0.5 * lim, 0.5 * W, 0.5 * (z_base + road_z)])
    sdf = build_sdf(verts, faces, res=a.sdf_res, margin_cells=4.0, interior_probe=probe)
    t_sdf = time.time() - t0
    print("SDF built res=%d cell=%.5f m in %.1f s  (dx=%.5f, need cell<=dx)"
          % (sdf.res, sdf.cell, t_sdf, dx), flush=True)
    if sdf.cell > dx:
        raise SystemExit(
            "SDF cell %.5f exceeds the MPM cell %.5f, so the road is coarser than the "
            "grid the water lives on. Raise --sdf-res or shorten the road." % (sdf.cell, dx))

    def sdf_at(pts):
        """Nearest-voxel SDF lookup, for the penetration diagnostic.

        This is the direct analogue of gate P-2 for the road: P-2 counts water
        inside the vehicle bounding box, this counts water inside the road solid.
        Negative means inside. Register items 18, 19 and 24 all turn on
        penetration, and until now it could only be measured against a bounding
        box, which is a crude proxy for a hull and no proxy at all for a kerb.
        """
        idx = np.round((np.asarray(pts) - sdf.origin) / sdf.cell).astype(np.int64)
        oob = ((idx < 0) | (idx >= sdf.res)).any(axis=1)
        np.clip(idx, 0, sdf.res - 1, out=idx)
        val = sdf.values[idx[:, 0], idx[:, 1], idx[:, 2]]
        return np.where(oob, np.inf, val)      # outside the SDF box is outside the solid

    film = seed_film(lim, W, a.depth, h, x_lo=wall, x_hi=lim - wall, **prof)
    n_water = len(film)
    vol = np.full(n_water, h ** 3, dtype=np.float32)

    s = Solver(grid=grid).load_particles(film, vol)
    if s.sort_interval != 0:
        raise RuntimeError("sort_interval must be 0; water is addressed by index range")
    gravity = tilted_gravity(a.grade_deg)
    s.set_material(newtonian(eta=a.eta, density=1000.0, bulk_modulus=a.bulk), g=gravity)

    # The mesh is built in world coordinates already, so its body frame and the world
    # frame coincide and the collider centre is the mesh bbox centre.
    centre = 0.5 * (verts.min(0) + verts.max(0))
    road = s.add_sdf_collider(sdf, center=tuple(centre), surface="separable",
                              friction=a.road_friction)
    s.add_domain_walls()

    c = float(np.sqrt(1.1 * a.bulk / 1000.0))
    rate = max(c / (0.28 * dx), 6.0e-3 / (1000.0 * dx * dx), max(a.velocity, 1.0) / (0.5 * dx))
    substeps = int(np.ceil(rate / fps))
    dt = (1.0 / fps) / substeps

    bc = None
    if a.bc == "recycle":
        bc = RecyclingChannelBC(n_water=n_water, x_in=wall, x_out=lim - wall,
                                inlet_velocity=a.velocity, dx=dx, grid_lim=lim)

    yc = 0.5 * W
    half_road = 0.5 * a.carriageway
    crown_band = np.abs(film[:, 1] - yc) <= 0.25 * half_road
    gutter_band = (np.abs(film[:, 1] - yc) > half_road) & \
                  (np.abs(film[:, 1] - yc) <= half_road + a.gutter_width)
    print("SCENARIO=FLOODED_ROADWAY bc=%s grade=%.2f" % (a.bc, a.grade_deg), flush=True)
    print("INSTRUMENT lim=%.3f dx=%.5f h=%.5f crown_z=%.3f n_water=%d"
          % (lim, dx, h, road_z, n_water), flush=True)
    print("INSTRUMENT gravity=[%.4f,%.4f,%.4f] substeps=%d dt=%.3e"
          % (gravity[0], gravity[1], gravity[2], substeps, dt), flush=True)
    print("INSTRUMENT crown_band=%d gutter_band=%d particles at t=0"
          % (int(crown_band.sum()), int(gutter_band.sum())), flush=True)

    for _ in range(8):
        s.step(dt, substeps)
    v = s.v(); v[:, 0] += a.velocity; s.set_v(v)

    pen_max = 0.0
    rows = ["frame,n_crown,n_gutter,gutter_frac,crown_depth,gutter_depth,"
            "road_fx,road_fy,road_fz,n_recycled,pen_frac,pen_depth_max"]
    dump_w, dump_s, dump_f = [], [], []
    for f in range(a.frames):
        x = s.x(); vv = s.v()
        n_rec = bc.apply(x, vv) if bc else 0
        if n_rec:
            s.set_x(x); s.set_v(vv)
        s.reset_sdf_force(road)
        s.step(dt, substeps)
        w = s.x()
        r = np.abs(w[:, 1] - yc)
        in_crown = r <= 0.25 * half_road
        in_gutter = (r > half_road) & (r <= half_road + a.gutter_width)
        zr = road_profile(w[:, 1], W, **prof)
        d_crown = (float(np.percentile((w[in_crown, 2] - zr[in_crown]), 99.5))
                   if int(in_crown.sum()) >= 20 else np.nan)
        d_gut = (float(np.percentile((w[in_gutter, 2] - zr[in_gutter]), 99.5))
                 if int(in_gutter.sum()) >= 20 else np.nan)
        wr = s.sdf_wrench(road, dt * substeps)
        sv = sdf_at(w)
        inside = sv < 0.0
        pen_frac = float(inside.mean())
        pen_max = max(pen_max, pen_frac)
        pen_depth = float(-sv[inside].min()) if inside.any() else 0.0
        rows.append("%d,%d,%d,%.6f,%s,%s,%.3f,%.3f,%.3f,%d,%.6f,%.6f" % (
            f, int(in_crown.sum()), int(in_gutter.sum()),
            float(in_gutter.sum()) / n_water,
            "" if not np.isfinite(d_crown) else "%.6f" % d_crown,
            "" if not np.isfinite(d_gut) else "%.6f" % d_gut,
            wr["force"][0], wr["force"][1], wr["force"][2], n_rec,
            pen_frac, pen_depth))
        if a.dump_water and (f % a.dump_water == 0 or f == a.frames - 1):
            dump_w.append(w.astype(np.float32))
            dump_s.append(np.linalg.norm(s.v(), axis=1).astype(np.float32))
            dump_f.append(f)
        if f % 20 == 0 or f == a.frames - 1:
            print("frame %3d crown_d=%s gutter_d=%s gutter_frac=%.4f Fz=%.0f N "
                  "pen=%.4f rec=%d"
                  % (f, "nan" if not np.isfinite(d_crown) else "%.4f" % d_crown,
                     "nan" if not np.isfinite(d_gut) else "%.4f" % d_gut,
                     float(in_gutter.sum()) / n_water, wr["force"][2], pen_frac, n_rec),
                  flush=True)

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "road.csv").write_text("\n".join(rows) + "\n")
    if a.dump_water:
        np.savez_compressed(out / "rollout.npz",
                            water=np.asarray(dump_w, np.float32),
                            speed=np.asarray(dump_s, np.float32),
                            frames_dumped=np.asarray(dump_f, np.int32),
                            road_verts=verts.astype(np.float32),
                            road_faces=faces.astype(np.int32),
                            lim=np.float32(lim), dx=np.float32(dx), h=np.float32(h),
                            floor=np.float32(road_z), depth=np.float32(a.depth),
                            velocity=np.float32(a.velocity),
                            grade_deg=np.float32(a.grade_deg))
    summary = {
        "scenario": "flooded_roadway", "label": a.label, "bc": a.bc,
        "lim": lim, "n_grid": a.grid, "dx": float(dx), "h": float(h),
        "sdf_res": int(sdf.res), "sdf_cell": float(sdf.cell), "sdf_build_s": float(t_sdf),
        "sdf_cell_over_dx": float(sdf.cell / dx),
        "crown_z": road_z, "z_base": z_base, "road_width_m": float(W),
        "carriageway_m": a.carriageway, "cross_slope": a.cross_slope,
        "gutter_depth_m": a.gutter_depth, "gutter_width_m": a.gutter_width,
        "kerb_height_m": a.kerb_height, "road_friction": a.road_friction,
        "film_depth_m": a.depth, "n_water": int(n_water),
        "velocity_ms": a.velocity, "grade_deg": a.grade_deg, "gravity": gravity,
        "frames": a.frames, "substeps": int(substeps), "sound_speed_ms": c,
        "particles_per_cell": 8,
        "gutter_frac_t0": float(gutter_band.sum()) / n_water,
        "recycled_total": int(bc.recycled_total) if bc else 0,
        "clamped_y": int(bc.clamped_y) if bc else 0,
        "clamped_z": int(bc.clamped_z) if bc else 0,
        "road_penetration_max_frac": float(pen_max),
        "parameters_are_design_inputs_not_measurements": True,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s" % a.label, flush=True)


if __name__ == "__main__":
    main()
