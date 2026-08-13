#!/usr/bin/env python3
"""
NON-CANONICAL, TRACK 2 EXPLORATORY. Never merge into main without a separate,
deliberate human decision. Produced on branch track2/coupled-realism-explore in an
isolated git worktree. No canonical Track 1 script was run and mpmenv was never
activated in the session that produced this file.

Genesis LegacyCoupler buoyancy validation, built from scratch.
Register C13 records that no coupling-force validation exists anywhere in the
Genesis repository against any analytical or experimental reference; this is the
first one for this project.

METHOD, and why it is shaped this way
-------------------------------------
The body is held FIXED and the net MPM -> rigid coupling force is read directly
from `links_state.cfrc_coupling_vel`, which `rigid/abd/misc.py:715-716` writes
with `-=`, so the physical force on the body is the NEGATION of the stored value.
That field is zeroed every substep at `rigid/abd/forward_dynamics.py:1238-1240`
and consumed at `:1201/:1204`, so a read after `scene.step()` samples the LAST
substep only. It is an instantaneous sample, never a running total.

FULL SUBMERSION (fraction 1.0) is deliberate, not a convenience.
Register J1a, corrected 2026-08-13, establishes two causes for the failed warpmpm
rung-(b) attempt: (i) the water was never settled, and (ii) a partially submerged
case was compared against a FULLY submerged reference, so the 7.3-7.7 percent bar
belongs to frac 1.0 with 2.75-5.36 dx of water cover. Reproducing a partial
submersion here and scoring it against that bar would repeat exactly the error
J1a documents. So this runs fully submerged, and the settle is gated, not
step-counted.

DEPTH-RESOLUTION CONVENTION: Genesis, dx = 1/grid_density, verified live at
`genesis/engine/solvers/mpm_solver.py:53`, INDEPENDENT of domain bounds. warpmpm's
dx is domain-dependent. Every dx and cover figure printed here is the Genesis
convention. Never merge the two.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import genesis as gs

G = 9.81
RHO_W = 1000.0
E_WATER = 1e6
NU_WATER = 0.2

# Canonical Yaris hull, verified live this session:
# 327,212 verts / 655,308 faces / watertight / volume 3.542738790016076 m^3
# md5(ply) = 372a709ffb22e0c914ecf25d4f34a76c
YARIS_VOL = 3.542738790016076


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--body", choices=["cube", "yaris"], default="cube")
    p.add_argument("--grid-density", type=float, default=16.0)
    p.add_argument("--mesh", default="track2_realism/yaris_hull_centered.obj")
    p.add_argument("--settle-max", type=int, default=4000)
    p.add_argument("--settle-check", type=int, default=100)
    p.add_argument("--measure", type=int, default=1200)
    p.add_argument("--dt", type=float, default=2e-3)
    p.add_argument("--substeps", type=int, default=10)
    p.add_argument("--cube-size", type=float, default=0.8)
    p.add_argument("--clear-lat", type=float, default=0.4)
    p.add_argument("--clear-bot", type=float, default=0.3)
    p.add_argument("--cover", type=float, default=0.35)
    p.add_argument("--vmax-gate", type=float, default=20.0,
                   help="settle gate: sound_speed / vmax must exceed this")
    p.add_argument("--out", default=None)
    return p.parse_args()


def main():
    a = parse_args()
    dx = 1.0 / a.grid_density
    pad = 3.0 * dx  # measured live: MPM CubeBoundary insets exactly 3 cells per side
    eps = 1e-4

    lam = E_WATER * NU_WATER / ((1 + NU_WATER) * (1 - 2 * NU_WATER))
    c_sound = math.sqrt(lam / RHO_W)

    # ---- body geometry ----
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
        if not m.is_watertight:
            print("[FATAL] mesh not watertight", flush=True)
            sys.exit(2)

    f_analytic = RHO_W * G * vol

    # ---- domain sized around the body ----
    # 2 dx of air headroom above the free surface. Without it the water top lands
    # exactly on (upper_bound - pad) and the seeder throws "particles outside solver
    # boundary" as a float coin-flip: it passed at gd16 and failed at gd32.
    headroom = 2.0 * dx
    inner = np.array([
        ext[0] + 2 * a.clear_lat,
        ext[1] + 2 * a.clear_lat,
        a.clear_bot + ext[2] + a.cover + headroom,
    ])
    dom = inner + 2 * pad
    lo = np.zeros(3)
    hi = dom

    body_c = np.array([dom[0] / 2, dom[1] / 2, pad + a.clear_bot + ext[2] / 2])
    body_top = body_c[2] + ext[2] / 2
    water_top = body_top + a.cover
    cover_dx = a.cover / dx

    print("=" * 74, flush=True)
    print("GENESIS LegacyCoupler BUOYANCY VALIDATION  (NON-CANONICAL, TRACK 2)", flush=True)
    print("=" * 74, flush=True)
    print(f"[cfg] body={a.body} grid_density={a.grid_density} dx={dx:.6f} m (Genesis convention)", flush=True)
    print(f"[cfg] body extents={ext} V={vol:.6f} m^3", flush=True)
    print(f"[cfg] domain={dom} grid={np.round(dom*a.grid_density).astype(int)}", flush=True)
    print(f"[cfg] body center={body_c} top={body_top:.4f}", flush=True)
    print(f"[cfg] water_top={water_top:.4f} cover={a.cover:.4f} m = {cover_dx:.2f} dx", flush=True)
    print(f"[cfg] submerged fraction = 1.000 (FULL, deliberate; see J1a)", flush=True)
    print(f"[cfg] sound_speed={c_sound:.4f} m/s  settle gate c/vmax>={a.vmax_gate}", flush=True)
    print(f"[cfg] F_analytic = rho*g*V = {RHO_W}*{G}*{vol:.6f} = {f_analytic:.4f} N", flush=True)

    gs.init(backend=gs.gpu, precision="32", logging_level="warning")

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=a.dt, substeps=a.substeps, gravity=(0.0, 0.0, -G)),
        mpm_options=gs.options.MPMOptions(
            lower_bound=tuple(lo), upper_bound=tuple(hi), grid_density=a.grid_density,
        ),
        show_viewer=False,
    )

    water = scene.add_entity(
        material=gs.materials.MPM.Liquid(rho=RHO_W, E=E_WATER, nu=NU_WATER),
        morph=gs.morphs.Box(
            lower=(lo[0] + pad + eps, lo[1] + pad + eps, lo[2] + pad + eps),
            upper=(hi[0] - pad - eps, hi[1] - pad - eps, water_top),
        ),
    )

    rho_body = 310.494 if a.body == "yaris" else 500.0
    if a.body == "cube":
        body = scene.add_entity(
            material=gs.materials.Rigid(rho=rho_body),
            morph=gs.morphs.Box(pos=tuple(body_c), size=tuple(ext), fixed=True),
        )
    else:
        body = scene.add_entity(
            material=gs.materials.Rigid(rho=rho_body),
            morph=gs.morphs.Mesh(file=mesh_file, pos=tuple(body_c),
                                 convexify=False, decimate=False, fixed=True),
        )

    scene.build()
    n_particles = water.n_particles
    print(f"[ok] built. water particles={n_particles}", flush=True)

    ls = scene.sim.rigid_solver.links_state
    LINK = body.link_start

    def force():
        arr = ls.cfrc_coupling_vel.to_numpy()
        return -np.asarray(arr[LINK, 0], dtype=np.float64)

    def vmax():
        v = water.get_particles_vel()
        v = v.cpu().numpy() if hasattr(v, "cpu") else np.asarray(v)
        return float(np.abs(v).max()), float(np.linalg.norm(v, axis=-1).max())

    # ---- PHASE 1: gated settle ----
    print("-" * 74, flush=True)
    print("PHASE 1  gated settle (J1a cause (i): a step count is not a settle)", flush=True)
    settle_trace = []
    settled_at = None
    for step in range(a.settle_max):
        scene.step()
        if (step + 1) % a.settle_check == 0:
            vinf, vnorm = vmax()
            ratio = c_sound / max(vnorm, 1e-12)
            fz = force()[2]
            settle_trace.append({"step": step + 1, "vmax": vnorm, "c_over_vmax": ratio, "Fz": fz})
            print(f"  [settle {step+1:5d}] vmax={vnorm:9.5f} m/s  c/vmax={ratio:11.2f}  "
                  f"Fz={fz:14.3f} N", flush=True)
            if ratio >= a.vmax_gate and settled_at is None:
                settled_at = step + 1
                print(f"  [GATE MET] c/vmax={ratio:.2f} >= {a.vmax_gate} at step {settled_at}", flush=True)
                break

    if settled_at is None:
        print(f"  [GATE NOT MET] ran full {a.settle_max} settle steps without reaching "
              f"c/vmax>={a.vmax_gate}. Reporting anyway, flagged.", flush=True)

    # ---- PHASE 2: averaged measurement ----
    print("-" * 74, flush=True)
    print("PHASE 2  averaged force measurement (instantaneous read rings; see smoke test)", flush=True)
    fz_series, fxy_series = [], []
    for step in range(a.measure):
        scene.step()
        f = force()
        fz_series.append(f[2])
        fxy_series.append([f[0], f[1]])
        if (step + 1) % 200 == 0:
            w = np.array(fz_series)
            print(f"  [meas {step+1:5d}] running mean Fz={w.mean():12.3f} N  "
                  f"sd={w.std():10.3f}  err={100*(w.mean()-f_analytic)/f_analytic:+8.3f}%", flush=True)

    fz = np.array(fz_series)
    fxy = np.array(fxy_series)
    mean_fz, sd_fz = float(fz.mean()), float(fz.std())
    err = 100.0 * (mean_fz - f_analytic) / f_analytic

    # second half only, guards against residual settle drift contaminating the mean
    h = fz[len(fz) // 2:]
    err_h = 100.0 * (h.mean() - f_analytic) / f_analytic

    print("=" * 74, flush=True)
    print("RESULT  (Genesis convention: dx = 1/grid_density)", flush=True)
    print(f"  F_analytic          = {f_analytic:14.4f} N", flush=True)
    print(f"  F_measured  (mean)  = {mean_fz:14.4f} N   sd={sd_fz:.4f}", flush=True)
    print(f"  F_measured  (2nd h) = {h.mean():14.4f} N   sd={h.std():.4f}", flush=True)
    print(f"  peak-to-peak        = {fz.max()-fz.min():14.4f} N", flush=True)
    print(f"  ERROR full window   = {err:+.4f} %", flush=True)
    print(f"  ERROR second half   = {err_h:+.4f} %", flush=True)
    print(f"  |Fx|,|Fy| mean      = {np.abs(fxy[:,0]).mean():.4f}, {np.abs(fxy[:,1]).mean():.4f} N "
          f"(should be ~0 by symmetry)", flush=True)
    print(f"  settled_at          = {settled_at}", flush=True)
    print("=" * 74, flush=True)

    out = {
        "NON_CANONICAL": True,
        "track": "track2/coupled-realism-explore",
        "engine": "genesis",
        "genesis_version": gs.__version__,
        "depth_resolution_convention": "genesis: dx = 1/grid_density, mpm_solver.py:53",
        "body": a.body,
        "mesh": mesh_file,
        "body_volume_m3": vol,
        "body_extents_m": ext.tolist(),
        "rho_body": rho_body,
        "submerged_fraction": 1.0,
        "grid_density": a.grid_density,
        "dx_m": dx,
        "pad_m": pad,
        "domain_m": dom.tolist(),
        "cover_m": a.cover,
        "cover_dx": cover_dx,
        "n_water_particles": int(n_particles),
        "dt": a.dt,
        "substeps": a.substeps,
        "sound_speed_mps": c_sound,
        "settle_gate_c_over_vmax": a.vmax_gate,
        "settled_at_step": settled_at,
        "settle_trace": settle_trace,
        "F_analytic_N": f_analytic,
        "F_measured_mean_N": mean_fz,
        "F_measured_sd_N": sd_fz,
        "F_measured_secondhalf_N": float(h.mean()),
        "F_peak_to_peak_N": float(fz.max() - fz.min()),
        "err_pct_full": err,
        "err_pct_secondhalf": err_h,
        "measure_steps": a.measure,
        "fz_series": fz.tolist(),
    }
    outpath = a.out or f"track2_realism/results_{a.body}_gd{int(a.grid_density)}.json"
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[saved] {outpath}", flush=True)


if __name__ == "__main__":
    main()
