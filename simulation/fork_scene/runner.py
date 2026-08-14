#!/usr/bin/env python3
"""LS6 BATCH arm: does a road cross-slope move anything the STATICS do not predict?

THE ONLY MODULE HERE THAT TOUCHES A SOLVER. Everything else in fork_scene runs
on a laptop. Run this with sbatch, never on a login node and never in idev
(idev burned 98.5-99.1% of Vista node-hours and 95 of 184 interactive jobs
ended in TIMEOUT; LS6 shows 0 batch timeouts).

WHY THIS EXPERIMENT AND NOT "SIMULATE TERRAIN"
==============================================
cross_slope.py shows the traction-margin change is exactly

    dM = -(W - B) [ sin th + mu (1 - cos th) ]

closed form, drag-independent, and needing no solver at all. So a simulation
cannot add anything to the STATIC half of the cross-slope question. What it can
answer is the leftover, and the experiment is designed as a three-way
decomposition rather than a single before/after:

  (1) STATIC        traction margin change. Exact, analytic, no run.
  (2) HYDROSTATIC   in a closed tank, tilting gravity tilts the equilibrium free
                    surface, so the depth AT THE VEHICLE changes even with no
                    hydrodynamics at all. Predicted below, not discovered.
  (3) HYDRODYNAMIC  whatever is left after (2) is subtracted, measured against
                    the run-to-run noise floor from a repeated S=0 arm.

Only (3) is a reason to care about terrain fidelity. If (3) is inside the noise,
terrain is retired as a SIMULATION concern and the static tilt can be applied as
a post-hoc correction to any flat-bed result already in hand, on either engine.
That is a strictly more useful negative than "cross-slope does nothing", which
is false.

THE HYDROSTATIC PREDICTION, DERIVED NOT FITTED
==============================================
Formulation G puts gravity at g' = (g sin th, 0, -g cos th) with a flat bed. At
equilibrium the free surface is perpendicular to g'. A plane with unit normal
n = (-sin th, 0, cos th) satisfies dz/dx = -n_x/n_z = +tan th, so

    the free surface RISES in +x with slope exactly +S,

which is the right sign: gravity's downslope component points +x, so water
piles at +x, and with a flat bed deeper water means a higher surface. Volume is
conserved, so the surface pivots about the water's x-centroid, and the depth
change at the vehicle is

    d_hydrostatic(x_veh) = S * (x_veh - x_centroid)

The vehicle sits at 0.60*lim and the water spans wall..lim-wall, centroid
0.50*lim, so x_veh - x_centroid = +0.10*lim and the predicted depth rise is
0.10*S*lim. At the canonical lim and S=0.02 that is +0.0188 m on a 0.2944 m
depth, i.e. +6.4%. Predicting it in advance is the point: measured minus
predicted is the signal, measured alone is not.

FALSIFIABLE CHECKS BUILT IN, so a broken run cannot look like a result
=====================================================================
C1 The reproduced scene must match data/all_runs_inventory.csv g64_m1100 on
   grid_lim, dx, realized depth, water_layers, n_water, n_vehicle and substeps.
   Any mismatch aborts before a single step: this is not the canonical scene and
   nothing measured in it is comparable to the 17 runs.
C2 |g'| must equal 9.81 to 1e-12. A tilt ROTATES gravity; it must never rescale
   it. A formulation bug that changes the magnitude would otherwise read as a
   physics result.
C3 The measured free-surface slope in the S>0 arms must recover +S. This is the
   direct test that the gravity override actually took effect in the kernels
   rather than being silently dropped somewhere in set_material -> set_gravity.
C4 Arm 0 and arm 1 are the SAME configuration at the SAME seed. Their spread is
   the noise floor. Register C-7 records that six metrics.csv differ at
   identical config, node and driver while every determinism_identical flag
   reports True, so the flag cannot be used for this and a repeated arm must be.

THE GRAVITY OVERRIDE IS A DEFAULT, NOT A CONSTANT. Chain verified live end to
end in the vendored solver at pinned SHA 544c93dd:
   core/solver.py:166       params = {**params, **overrides}
   core/solver.py:167-169   {"material": name, "g": [0,0,-9.81], **params}
                            -> **params expands AFTER "g", so a caller wins
   kernels/mpm_solver_warp.py:742-743   if "g" in kwargs: self.set_gravity(...)
No engine patch is needed. CLAUDE.md item 3's word "unconditionally" is wrong on
this point and its conclusion is still right, because newtonian() carries no g
key and the canonical driver passes no override, so all 17 gated runs did run at
exactly 9.81. Filed for the register's owner, not edited here.

SCOPE. Formulation G only. Formulation T (tilted floor plane) is NOT run: at
S=0.06 it drops the bed 0.5653 m across a 9.4217 m tank, 192% of the depth, so
the upstream end runs dry and the comparison is not held fixed. scene.py refuses
to build it. The cost of T is documented in cross_slope.py and is a design
finding, not something that needed a job.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, os.pardir))

from simulation.fork_scene.cross_slope import CrossSlope  # noqa: E402

# --- data/all_runs_inventory.csv, row g64_m1100. THE CONTRACT FOR CHECK C1. ---
INV_G64 = {
    "grid_lim": 9.421742313727737,
    "dx": 0.1472147236519959,
    "realized_depth_m": 0.2944294473039918,
    "water_layers": 4,
    "n_water": 48367,
    "n_vehicle": 8905,
    "substeps": 11,
    "sound_speed_ms": 12.84523257866513,
    "solid_volume_m3": 3.5513843861695054,
}
TOL_REL = 1e-9


def build_scene(vehicle, depth, velocity, mass, slope_S, n_grid=64,
                water_density=1000.0, water_eta=1.0e-3, bulk_modulus=1.5e5,
                fps=30, floor_friction=0.55, seed=0,
                inflow_len=1.5, device="auto"):
    """The canonical StandingFloodScene, reproduced verbatim, plus tilted gravity.

    Reproduced rather than imported on purpose. renders/ is gitignored and the
    canonical driver is not present in a fresh clone or on LS6 (checked live),
    so an import would be a hidden dependency on an untracked file. Reproducing
    it and then ASSERTING the result against the recorded inventory is strictly
    stronger evidence than importing would have been: if any line below has
    drifted from the original, check C1 fails.
    """
    from warpmpm.core.solver import GridConfig, Solver
    from warpmpm.materials import newtonian

    out = {}
    ext = vehicle.extent
    # Axis-trap-safe form. In the DRIVER frame load_vehicle(up="z") has already
    # put the long axis on y, so this agrees with the as-ran 2.2*ext[1] here;
    # written invariantly so it cannot silently break if the loader changes.
    lim = float(max(2.2 * max(ext[0], ext[1]), 3.5 * min(ext[0], ext[1]),
                    6.0 * depth))
    grid = GridConfig(n_grid=n_grid, grid_lim=lim)
    dx = grid.dx
    h = dx / 2.0
    floor = 3.0 * dx
    rng = np.random.default_rng(seed)

    if vehicle.spacing > 1.2 * h:
        vehicle.solidify(h)

    solid_volume = vehicle.n_particles * h ** 3
    vehicle_density = mass / solid_volume

    vx, vy = 0.60 * lim, 0.50 * lim
    place = np.array([vx, vy, floor + 0.5 * h], dtype=np.float32)
    truck = vehicle.particles + place

    wall = 4.0 * dx
    xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
    ys = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
    zs = np.arange(floor + 0.5 * h, floor + depth, h)
    water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    water = (water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)).astype(np.float32)

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

    pos = np.concatenate([water, truck])
    vol = np.full(len(pos), h ** 3, dtype=np.float32)
    n_water, n_total = len(water), len(pos)

    slope = CrossSlope(slope_S)
    g_vec = list(slope.gravity_vector())
    # CHECK C2, before anything expensive happens
    mag = math.sqrt(sum(c * c for c in g_vec))
    assert abs(mag - 9.81) < 1e-12, f"C2 FAILED: |g'| = {mag!r}, must be 9.81"

    s = Solver(grid=grid, device=device).load_particles(pos, vol)
    # THE ONLY DEPARTURE FROM THE CANONICAL SCENE: g. See module docstring.
    s.set_material(newtonian(eta=water_eta, density=water_density,
                             bulk_modulus=bulk_modulus), g=g_vec)
    s.set_material_range(n_water, n_total, "rigid", obj_id=0,
                         density=vehicle_density)
    s.finalize_rigid_bodies()
    s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
                restitution=0.05)
    for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                    ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
    s.add_domain_walls()

    c = float(np.sqrt(1.1 * bulk_modulus / water_density))
    term_acoustic = c / (0.28 * dx)
    term_viscous = 6.0 * water_eta / (water_density * dx * dx)
    term_advective = max(velocity, 1e-6) / (0.5 * dx)
    substeps = int(np.ceil(max(term_acoustic, term_viscous, term_advective) / fps))
    dt = (1.0 / fps) / substeps

    out.update(dict(solver=s, lim=lim, dx=dx, h=h, floor=floor, wall=wall,
                    n_water=n_water, n_total=n_total, n_vehicle=n_total - n_water,
                    substeps=substeps, dt=dt, sound_speed=c, place=place,
                    water_layers=len(zs), realized_depth=len(zs) * h,
                    solid_volume=solid_volume, vehicle_density=vehicle_density,
                    grid=grid, fps=fps, velocity=velocity, g_vec=g_vec,
                    inflow_x=wall + inflow_len, slope_S=slope_S))
    return out


def check_c1(sc) -> list[str]:
    """Refuse to run anything that is not the canonical scene."""
    got = {"grid_lim": sc["lim"], "dx": sc["dx"],
           "realized_depth_m": sc["realized_depth"],
           "water_layers": sc["water_layers"], "n_water": sc["n_water"],
           "n_vehicle": sc["n_vehicle"], "substeps": sc["substeps"],
           "sound_speed_ms": sc["sound_speed"],
           "solid_volume_m3": sc["solid_volume"]}
    bad = []
    for k, want in INV_G64.items():
        have = got[k]
        if isinstance(want, int):
            ok = int(have) == want
        else:
            ok = abs(have - want) <= TOL_REL * max(1.0, abs(want))
        if not ok:
            bad.append(f"{k}: reproduced {have!r}, inventory {want!r}")
    return bad


def project_water(sc):
    s = sc["solver"]
    x = s.x()
    w = x[: sc["n_water"]]
    eps = 0.25 * sc["dx"]
    lo = np.array([sc["wall"], sc["wall"], sc["floor"]], dtype=np.float32) - eps
    hi = np.array([sc["lim"] - sc["wall"], sc["lim"] - sc["wall"], np.inf],
                  dtype=np.float32) + eps
    out_lo, out_hi = w < lo, w > hi
    if not (out_lo.any() or out_hi.any()):
        return 0
    n = int(np.unique(np.nonzero(out_lo | out_hi)[0]).size)
    v = s.v()
    vw = v[: sc["n_water"]]
    np.clip(w, lo, hi, out=w)
    vw[out_lo] = np.maximum(vw[out_lo], 0.0)
    vw[out_hi] = np.minimum(vw[out_hi], 0.0)
    s.set_x(x)
    s.set_v(v)
    return n


def sustain_inflow(sc):
    s = sc["solver"]
    x, v = s.x(), s.v()
    band = x[: sc["n_water"], 0] < sc["inflow_x"]
    v[: sc["n_water"]][band, 0] = sc["velocity"]
    s.set_v(v)
    return int(band.sum())


def surface_profile(sc, n_bins=12):
    """Free-surface height vs x, and its least-squares slope.

    CHECK C3 reads this: with tilted gravity the equilibrium surface must rise
    in +x with slope +S. Uses the 99th percentile of z per bin plus half a
    particle spacing, the same estimator the project already uses for depth.
    """
    s = sc["solver"]
    w = s.x()[: sc["n_water"]]
    lo, hi = sc["wall"], sc["lim"] - sc["wall"]
    edges = np.linspace(lo, hi, n_bins + 1)
    xs, zs = [], []
    for i in range(n_bins):
        sel = (w[:, 0] >= edges[i]) & (w[:, 0] < edges[i + 1])
        if sel.sum() < 50:
            continue
        xs.append(0.5 * (edges[i] + edges[i + 1]))
        zs.append(float(np.percentile(w[sel, 2], 99.0)) + 0.5 * sc["h"]
                  - sc["floor"])
    if len(xs) < 3:
        return {"slope": float("nan"), "x": xs, "depth": zs}
    A = np.vstack([np.array(xs), np.ones(len(xs))]).T
    m, b = np.linalg.lstsq(A, np.array(zs), rcond=None)[0]
    return {"slope": float(m), "intercept": float(b), "x": xs, "depth": zs}


def local_depth_at_vehicle(sc, half_window=None):
    """Water depth in a column centred on the vehicle's spawn footprint."""
    s = sc["solver"]
    w = s.x()[: sc["n_water"]]
    cx, cy = float(sc["place"][0]), float(sc["place"][1])
    hw = half_window if half_window is not None else 1.5 * sc["dx"]
    sel = (np.abs(w[:, 0] - cx) <= hw) & (np.abs(w[:, 1] - cy) <= hw)
    if sel.sum() < 20:
        return float("nan")
    return float(np.percentile(w[sel, 2], 99.0)) + 0.5 * sc["h"] - sc["floor"]


def run_arm(vehicle, slope_S, frames, label, outdir, seed=0, n_grid=64):
    t0 = time.time()
    sc = build_scene(vehicle, depth=0.3, velocity=1.5, mass=1100.0,
                     slope_S=slope_S, n_grid=n_grid, seed=seed)
    bad = check_c1(sc) if n_grid == 64 else []
    if bad:
        raise SystemExit("C1 FAILED, this is not the canonical scene:\n  "
                         + "\n  ".join(bad))
    s = sc["solver"]
    com0 = s.rigid_state()["com"].copy()

    # settle, exactly as the canonical driver does, before the velocity kick
    for _ in range(8):
        project_water(sc)
        s.step(sc["dt"], sc["substeps"])
    v = s.v()
    v[: sc["n_water"], 0] += sc["velocity"]
    s.set_v(v)
    com0 = s.rigid_state()["com"].copy()

    rows, leaked = [], 0
    for f in range(frames):
        leaked += project_water(sc)
        sustain_inflow(sc)
        s.step(sc["dt"], sc["substeps"])
        st = s.rigid_state()
        d = st["com"] - com0
        prof = surface_profile(sc)
        rows.append({
            "frame": f + 1,
            "t": (f + 1) / sc["fps"],
            "disp_x": float(d[0]), "disp_y": float(d[1]), "disp_z": float(d[2]),
            "disp_mag": float(np.linalg.norm(d)),
            "v_x": float(st["v"][0]), "v_y": float(st["v"][1]),
            "v_z": float(st["v"][2]),
            "local_depth_m": local_depth_at_vehicle(sc),
            "surface_slope": prof["slope"],
        })

    meta = {
        "label": label, "slope_S": slope_S, "seed": seed, "frames": frames,
        "n_grid": n_grid, "grid_lim": sc["lim"], "dx": sc["dx"],
        "realized_depth_m": sc["realized_depth"], "water_layers": sc["water_layers"],
        "n_water": sc["n_water"], "n_vehicle": sc["n_vehicle"],
        "substeps": sc["substeps"], "dt": sc["dt"],
        "sound_speed_ms": sc["sound_speed"], "g_vec": sc["g_vec"],
        "g_magnitude": float(np.linalg.norm(sc["g_vec"])),
        "x_vehicle": float(sc["place"][0]),
        "x_water_centroid": 0.5 * sc["lim"],
        "predicted_hydrostatic_depth_change_m":
            slope_S * (float(sc["place"][0]) - 0.5 * sc["lim"]),
        "predicted_surface_slope": slope_S,
        "leaked_particle_events": leaked,
        "c1_checked_against_inventory": n_grid == 64,
        "wall_time_s": time.time() - t0,
    }
    Path(outdir).mkdir(parents=True, exist_ok=True)
    with open(Path(outdir) / f"{label}.json", "w") as fh:
        json.dump({"meta": meta, "series": rows}, fh, indent=1)
    print(f"[{label}] S={slope_S} seed={seed} done in {meta['wall_time_s']:.1f}s  "
          f"final disp {rows[-1]['disp_mag']:.6f} m  "
          f"surf slope {rows[-1]['surface_slope']:+.5f} (predict {slope_S:+.5f})  "
          f"local depth {rows[-1]['local_depth_m']:.5f} m", flush=True)
    return meta, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ply", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--frames", type=int, default=90)
    ap.add_argument("--n-grid", type=int, default=64)
    args = ap.parse_args()

    import trimesh
    from warpmpm.vehicle import load_vehicle

    def canonicalize(v):
        mv = np.asarray(v.mesh.vertices, dtype=np.float64)
        lo, hi = mv.min(0), mv.max(0)
        shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
        mv = mv - shift
        v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces),
                                 process=False)
        v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
        v.extent = mv.max(0) - mv.min(0)
        v.spacing = float(v.extent.max()) / 32.0
        return v

    print("=== fork_scene.runner: cross-slope sensitivity, formulation G ===",
          flush=True)
    print(f"ply     {args.ply}", flush=True)
    print(f"outdir  {args.outdir}", flush=True)

    # ARMS. 0 and 1 are the SAME config and seed: their spread IS the noise
    # floor (check C4). Register C-7 records that determinism_identical reports
    # True on runs that differ, so it cannot be used for this.
    arms = [
        ("S000_rep0", 0.00, 0),
        ("S000_rep1", 0.00, 0),
        ("S002", 0.02, 0),
        ("S006", 0.06, 0),
    ]
    for label, S, seed in arms:
        veh = canonicalize(load_vehicle(args.ply, up="z"))
        run_arm(veh, S, args.frames, label, args.outdir, seed=seed,
                n_grid=args.n_grid)
    print("=== all arms complete ===", flush=True)


if __name__ == "__main__":
    main()
