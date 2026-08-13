#!/usr/bin/env python3
"""
NON-CANONICAL, TRACK 2 EXPLORATORY. Never merge into main without a separate,
deliberate human decision. Branch track2/coupled-realism-explore, isolated worktree.

FREE-BODY variant (the C1 analogue): fully submerged, released from rest, measure
the initial vertical acceleration and infer F_buoy = m*(a + g).

WHY THIS AND NOT THE FIXED-BODY FORCE READ. The fixed-body read
(validate_genesis_buoyancy.py) converged to roughly zero-to-negative force on a
fully submerged body where analytic buoyancy is strongly positive. This run is
the independent cross-check: if the LegacyCoupler transports buoyancy at all, a
310.494 kg/m^3 body must accelerate UP. If it sinks, the defect is architectural
and not a measurement artifact of reading cfrc_coupling_vel.

This is warpmpm's C1_initial_submerged_acceleration variant, which is the one that
produced the -7.67/+7.28 percent figures, so it is the like-for-like comparison.
Register J1a, corrected 2026-08-13, is explicit that those figures are FULL
submersion (frac 1.0), so this runs fully submerged too.

Genesis convention: dx = 1/grid_density (mpm_solver.py:53), independent of bounds.
"""
import argparse
import json
import math

import numpy as np
import genesis as gs

G = 9.81
RHO_W = 1000.0
E_WATER = 1e6
NU_WATER = 0.2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--body", choices=["cube", "yaris"], default="yaris")
    p.add_argument("--mesh", default="track2_realism/yaris_hull_centered.obj")
    p.add_argument("--grid-density", type=float, default=16.0)
    p.add_argument("--rho-body", type=float, default=310.494)
    p.add_argument("--settle", type=int, default=300)
    p.add_argument("--measure", type=int, default=120)
    p.add_argument("--dt", type=float, default=2e-3)
    p.add_argument("--substeps", type=int, default=10)
    p.add_argument("--cube-size", type=float, default=0.8)
    p.add_argument("--clear-lat", type=float, default=0.4)
    p.add_argument("--clear-bot", type=float, default=0.3)
    p.add_argument("--cover", type=float, default=0.35)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    dx = 1.0 / a.grid_density
    pad = 3.0 * dx
    eps = 1e-4
    lam = E_WATER * NU_WATER / ((1 + NU_WATER) * (1 - 2 * NU_WATER))
    c_sound = math.sqrt(lam / RHO_W)

    if a.body == "cube":
        ext = np.array([a.cube_size] * 3)
        vol = a.cube_size ** 3
        mesh_file = None
    else:
        import trimesh
        m = trimesh.load(a.mesh, process=False)
        ext = np.asarray(m.extents, dtype=np.float64)
        vol = float(m.volume)
        mesh_file = a.mesh

    mass = a.rho_body * vol
    f_analytic = RHO_W * G * vol
    a_ideal = G * (RHO_W / a.rho_body - 1.0)

    # 2 dx of air headroom above the free surface. Without it water_top lands exactly on
    # (upper_bound - pad) and seeding becomes a float coin-flip: the sibling harness
    # passed at gd16 and threw "particles outside solver boundary" at gd32.
    headroom = 2.0 * dx
    inner = np.array([ext[0] + 2 * a.clear_lat, ext[1] + 2 * a.clear_lat,
                      a.clear_bot + ext[2] + a.cover + headroom])
    dom = inner + 2 * pad
    body_c = np.array([dom[0] / 2, dom[1] / 2, pad + a.clear_bot + ext[2] / 2])
    water_top = body_c[2] + ext[2] / 2 + a.cover

    print("=" * 74, flush=True)
    print("GENESIS FREE-BODY BUOYANCY CHECK (NON-CANONICAL, TRACK 2)", flush=True)
    print("=" * 74, flush=True)
    print(f"[cfg] body={a.body} gd={a.grid_density} dx={dx:.6f} (Genesis convention)", flush=True)
    print(f"[cfg] V={vol:.6f} m^3  rho_body={a.rho_body}  mass={mass:.3f} kg", flush=True)
    print(f"[cfg] extents={ext}  domain={dom}  grid={np.round(dom*a.grid_density).astype(int)}", flush=True)
    print(f"[cfg] cover={a.cover} m = {a.cover/dx:.2f} dx   submerged frac = 1.000 (FULL)", flush=True)
    print(f"[cfg] F_analytic = {f_analytic:.4f} N", flush=True)
    print(f"[cfg] a_ideal (no added mass) = g(rho_w/rho_b - 1) = {a_ideal:.4f} m/s^2", flush=True)

    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=a.dt, substeps=a.substeps, gravity=(0.0, 0.0, -G)),
        mpm_options=gs.options.MPMOptions(lower_bound=(0.0, 0.0, 0.0),
                                          upper_bound=tuple(dom),
                                          grid_density=a.grid_density),
        show_viewer=False,
    )
    water = scene.add_entity(
        material=gs.materials.MPM.Liquid(rho=RHO_W, E=E_WATER, nu=NU_WATER),
        morph=gs.morphs.Box(lower=(pad + eps, pad + eps, pad + eps),
                            upper=(dom[0] - pad - eps, dom[1] - pad - eps, water_top)),
    )
    if a.body == "cube":
        body = scene.add_entity(material=gs.materials.Rigid(rho=a.rho_body),
                                morph=gs.morphs.Box(pos=tuple(body_c), size=tuple(ext), fixed=False))
    else:
        body = scene.add_entity(material=gs.materials.Rigid(rho=a.rho_body),
                                morph=gs.morphs.Mesh(file=mesh_file, pos=tuple(body_c),
                                                     convexify=False, decimate=False, fixed=False))
    scene.build()
    print(f"[ok] built. water particles={water.n_particles}", flush=True)
    print(f"[ok] genesis-reported body mass = {float(np.asarray(body.get_mass()).sum()):.4f} kg "
          f"(analytic rho*V = {mass:.4f})", flush=True)

    def zpos():
        q = body.get_pos()
        q = q.cpu().numpy() if hasattr(q, "cpu") else np.asarray(q)
        return float(np.asarray(q).reshape(-1)[2])

    def zvel():
        v = body.get_vel()
        v = v.cpu().numpy() if hasattr(v, "cpu") else np.asarray(v)
        return float(np.asarray(v).reshape(-1)[2])

    z0 = zpos()
    print(f"[ok] initial body z = {z0:.6f}", flush=True)

    print("-" * 74, flush=True)
    print("PHASE 1  settle (body free the whole time; a settle that MOVES the body", flush=True)
    print("         is itself the signal, so z is logged throughout)", flush=True)
    trace = []
    for s in range(a.settle):
        scene.step()
        if (s + 1) % 50 == 0:
            print(f"  [settle {s+1:4d}] z={zpos():.6f}  dz={zpos()-z0:+.6f}  vz={zvel():+.6f}", flush=True)

    print("-" * 74, flush=True)
    print("PHASE 2  measure vertical kinematics", flush=True)
    ts, zs, vs = [], [], []
    for s in range(a.measure):
        scene.step()
        ts.append((s + 1) * a.dt)
        zs.append(zpos())
        vs.append(zvel())
        if (s + 1) % 20 == 0:
            print(f"  [meas {s+1:4d}] t={ts[-1]:.4f} z={zs[-1]:.6f} vz={vs[-1]:+.6f}", flush=True)

    ts, zs, vs = np.array(ts), np.array(zs), np.array(vs)
    # acceleration from a straight-line fit to v(t); robust to per-step force ringing
    A = np.vstack([ts, np.ones_like(ts)]).T
    a_fit, v0_fit = np.linalg.lstsq(A, vs, rcond=None)[0]
    f_measured = mass * (a_fit + G)
    err = 100.0 * (f_measured - f_analytic) / f_analytic

    print("=" * 74, flush=True)
    print("RESULT  (Genesis convention: dx = 1/grid_density)", flush=True)
    print(f"  net dz over measure window = {zs[-1]-zs[0]:+.6f} m", flush=True)
    print(f"  vz first -> last           = {vs[0]:+.6f} -> {vs[-1]:+.6f} m/s", flush=True)
    print(f"  a_fit (dv/dt)              = {a_fit:+.4f} m/s^2", flush=True)
    print(f"  a_ideal                    = {a_ideal:+.4f} m/s^2", flush=True)
    # Report direction from what the body ACTUALLY did, not from the sign of a fitted
    # acceleration. A body decelerating its descent has a_fit > 0 while still sinking,
    # and an earlier version of this line printed "UP (buoyant)" for exactly that case.
    net_dz = float(zs[-1] - zs[0])
    rose = net_dz > 0 and float(vs[-1]) > 0
    print(f"  net_dz={net_dz:+.6f} m  vz_end={vs[-1]:+.6f} m/s  mean_vz={vs.mean():+.6f} m/s", flush=True)
    print(f"  DIRECTION                  = "
          f"{'ROSE' if rose else 'DID NOT RISE (sinking or oscillating)'} "
          f"[a_fit sign alone is NOT direction]", flush=True)
    print(f"  F_measured = m(a+g)        = {f_measured:.4f} N", flush=True)
    print(f"  F_analytic = rho*g*V       = {f_analytic:.4f} N", flush=True)
    print(f"  ERROR                      = {err:+.4f} %", flush=True)
    print("=" * 74, flush=True)

    out = {
        "NON_CANONICAL": True, "track": "track2/coupled-realism-explore",
        "engine": "genesis", "genesis_version": gs.__version__,
        "variant": "C1_initial_submerged_acceleration (free body)",
        "depth_resolution_convention": "genesis: dx = 1/grid_density",
        "body": a.body, "mesh": mesh_file, "volume_m3": vol, "extents_m": ext.tolist(),
        "rho_body": a.rho_body, "mass_kg": mass, "submerged_fraction": 1.0,
        "grid_density": a.grid_density, "dx_m": dx, "cover_m": a.cover, "cover_dx": a.cover / dx,
        "domain_m": dom.tolist(), "n_water_particles": int(water.n_particles),
        "dt": a.dt, "substeps": a.substeps, "sound_speed_mps": c_sound,
        "settle_steps": a.settle, "measure_steps": a.measure,
        "a_fit_mps2": float(a_fit), "a_ideal_mps2": float(a_ideal),
        "F_measured_N": float(f_measured), "F_analytic_N": float(f_analytic),
        "err_pct": float(err),
        "z_series": zs.tolist(), "vz_series": vs.tolist(), "t_series": ts.tolist(),
    }
    outpath = a.out or f"track2_realism/results_free_{a.body}_gd{int(a.grid_density)}.json"
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[saved] {outpath}", flush=True)


if __name__ == "__main__":
    main()
