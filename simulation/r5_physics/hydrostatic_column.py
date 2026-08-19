#!/usr/bin/env python3
"""Hydrostatic column: what this solver's STATIC pressure error actually is.

WHY THIS EXISTS. Criterion 3 grades a static vertical reaction against the Kramer
floating-sphere benchmark. The project's own 18 August deep search records that Kramer's
0.3 percent is "of drop height" and that it is "a motion benchmark, not a stated
static-force tolerance", and that static verification is more directly done with MPM
hydrostatic columns or SPH still-water pressure tests. So criterion 3 grades a static
quantity against a motion reference and this project has never measured the static
pressure error of its own solver. This script measures it.

WHAT IT DECIDES. Job B reads +34 to +64 percent against analytic buoyancy. If a column
with NO BODY IN IT reproduces analytic hydrostatic pressure, that error belongs to the
sphere: the coupling, the contact treatment, or the free-surface estimator. If the column
is itself tens of percent wrong, the FAIL was never about the sphere at all.

WHAT IS GRADED, AND WHY IT IS THE GRADIENT AND NOT THE PRESSURE.
The pressure at a point is rho*g*(z_surface - z), so grading pressure requires knowing
where the free surface is, which is the exact ambiguity that put criterion 3 into its
current state. THE GRADIENT dp/dz DOES NOT DEPEND ON THE SURFACE LOCATION AT ALL. It is
graded here for that reason, so this check cannot inherit the defect it was written to
investigate. The intercept is reported as a companion under both surface conventions and
is never graded.

THE COLUMN IS GENUINELY COMPRESSIBLE AND THE CORRECT ANSWER IS NOT rho0*g.
BULK = 1.5e5 Pa against a base hydrostatic pressure of rho*g*depth = 4896.17 Pa gives a
volumetric strain of 3.264 percent at the base and about 1.632 percent depth-averaged. A
CORRECT weakly-compressible column therefore reads about 1.6 percent HIGH in |dp/dz|
against the incompressible reference rho0*g. That is the expected right answer, not a
defect, and it is stated here BEFORE the run rather than discovered afterwards.

Written 2026-08-19 by slot d11-accessor. Numerics copied from sphere_heave.py so the
column is the same fluid on the same grid as job B: same GridConfig, same newtonian
material, same BULK/ETA/RHO_W, same FLOOR/WALL offsets, same slip planes at friction 0
and restitution 0, same lattice spacing h = dx/2, same substep rule. The ONLY difference
is that no sphere is created and no SDF is built.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

# Copied from sphere_heave.py rather than imported, so that a later edit to that file
# cannot silently change what this reference measured. Values verified against
# sphere_heave.py on 2026-08-19: BULK :144, ETA :145, RHO_W_BENCHMARK :160,
# G_ENGINE :146, FLOOR :478, WALL :479.
BULK = 1.5e5
ETA = 1.0e-3
RHO_W = 998.2
G_ENGINE = 9.81
FLOOR = 0.075
WALL = 0.100

# PRE-REGISTERED PASS BANDS. Fixed 2026-08-19 BEFORE the first run, committed before
# submission. Graded on |dp/dz| against the incompressible reference rho0*g.
#   within 5 percent   PASS
#   5 to 15 percent    REPORTABLE PARTIAL
#   beyond 15 percent  FAIL
# PROVENANCE OF THE BAND: a project choice, NOT a literature tolerance, and deliberately
# so. Benchmark cases transfer across methods; the tolerances one method reports for
# itself do not. The 5 percent is set to sit clear of the +1.632 percent self-compression
# the EOS genuinely produces, with room for the discretisation of a 53-layer column
# (depth/h = 0.5/0.009375 = 53.3 at g64), and tight enough that it cannot absorb job B's
# +34 percent.
BAND_PASS = 0.05
BAND_PARTIAL = 0.15
EXPECTED_COMPRESSIBLE_EXCESS = 0.01632   # see module docstring


def substeps_and_dt(dx, c=None):
    """Same acoustic CFL rule sphere_heave.py uses, reproduced for independence."""
    c = c or math.sqrt(BULK / RHO_W)
    tick = 1.0 / 60.0
    dt_max = 0.4 * dx / c
    n = max(1, int(math.ceil(tick / dt_max)))
    return n, tick / n


def build_column(n_grid, lim, depth, seed, device):
    from warpmpm.core.solver import GridConfig, Solver
    from warpmpm.materials import newtonian

    dx = lim / n_grid
    h = dx / 2.0
    surface_z = FLOOR + depth

    rng = np.random.default_rng(seed)
    lo, hi = WALL, lim - WALL
    n_lat = int(round((hi - lo) / h))
    n_z = int(round(depth / h))
    xs = lo + (np.arange(n_lat) + 0.5) * h
    zs = FLOOR + (np.arange(n_z) + 0.5) * h
    gx, gy, gz = np.meshgrid(xs, xs, zs, indexing="ij")
    pts = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
    pts += (rng.random(pts.shape) - 0.5) * (0.1 * h)     # same jitter fraction as the tank

    vol = np.full(len(pts), h ** 3, dtype=np.float32)
    s = Solver(grid=GridConfig(n_grid=n_grid, grid_lim=lim),
               device=device).load_particles(pts.astype(np.float32), vol)
    s.set_material(newtonian(eta=ETA, density=RHO_W, bulk_modulus=BULK))
    s.add_plane((0, 0, FLOOR), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
    for pt, nrm in (((WALL, 0, 0), (1, 0, 0)), ((lim - WALL, 0, 0), (-1, 0, 0)),
                    ((0, WALL, 0), (0, 1, 0)), ((0, lim - WALL, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
    s.add_domain_walls()
    return s, dx, h, surface_z, len(pts)


def pressure_profile(s, n_particles, dx, floor, surface_z, n_bins=20):
    """Bin particle pressure by height and fit dp/dz over the INTERIOR of the column.

    p = -trace(cauchy)/3. The top and bottom 2 bins are excluded from the fit: the top
    is the free surface where p -> 0 and the kernel support is truncated, the bottom is
    the floor plane's boundary layer. Both exclusions are stated here and are fixed in
    advance; the full unfitted profile is emitted so the choice can be audited.
    """
    x = s.x()[:n_particles]
    sig = s.cauchy()[:n_particles]
    p = -(sig[:, 0, 0] + sig[:, 1, 1] + sig[:, 2, 2]) / 3.0
    z = x[:, 2]
    edges = np.linspace(floor, surface_z, n_bins + 1)
    idx = np.clip(np.digitize(z, edges) - 1, 0, n_bins - 1)
    zc, pm, cnt = [], [], []
    for b in range(n_bins):
        m = idx == b
        if m.sum() < 8:
            continue
        zc.append(float(z[m].mean()))
        pm.append(float(p[m].mean()))
        cnt.append(int(m.sum()))
    zc, pm, cnt = np.array(zc), np.array(pm), np.array(cnt)
    interior = slice(2, -2) if len(zc) > 8 else slice(None)
    zi, pi = zc[interior], pm[interior]
    slope, intercept = (np.polyfit(zi, pi, 1) if len(zi) >= 3 else (float("nan"),) * 2)
    return {
        "bin_z_m": zc.tolist(), "bin_p_Pa": pm.tolist(), "bin_n": cnt.tolist(),
        "fit_dpdz_Pa_per_m": float(slope), "fit_intercept_Pa": float(intercept),
        "n_bins_fitted": int(len(zi)),
        "p_max_Pa": float(p.max()), "p_mean_Pa": float(p.mean()),
        "z_max_m": float(z.max()), "n_below_floor": int((z < floor).sum()),
    }


def band_of(rel):
    a = abs(rel)
    return "PASS" if a <= BAND_PASS else ("REPORTABLE PARTIAL" if a <= BAND_PARTIAL else "FAIL")


def run(a):
    s, dx, h, surface_z, n_p = build_column(a.n_grid, a.lim, a.depth, a.seed, a.device)
    substeps, dt = substeps_and_dt(dx)
    ref = RHO_W * G_ENGINE
    cfg = {
        "n_grid": a.n_grid, "lim_m": a.lim, "dx_m": dx, "h_m": h, "depth_m": a.depth,
        "floor_m": FLOOR, "wall_m": WALL, "surface_z_seeded_m": surface_z,
        "n_water": n_p, "substeps": substeps, "dt_substep_s": dt, "seed": a.seed,
        "bulk_Pa": BULK, "eta_Pa_s": ETA, "rho_w_kg_m3": RHO_W, "g_m_s2": G_ENGINE,
        "reference_dpdz_Pa_per_m": -ref,
        "base_hydrostatic_Pa": ref * a.depth,
        "base_volumetric_strain": ref * a.depth / BULK,
        "expected_compressible_excess": EXPECTED_COMPRESSIBLE_EXCESS,
        "prereg": {
            "graded": "fit_dpdz_Pa_per_m over the column interior",
            "why_gradient": "independent of free-surface height, so it cannot inherit "
                            "criterion 3's unstated-surface defect",
            "bands": f"within {BAND_PASS:.0%} PASS, to {BAND_PARTIAL:.0%} PARTIAL, beyond FAIL",
            "band_provenance": "PROJECT CHOICE, not a literature tolerance",
            "window": "last 50 percent of frames, matching criterion 3 as amended",
            "falsifier": "a fitted |dp/dz| within 5 percent of rho0*g with no systematic "
                         "residual curvature beyond the predicted 3.264 percent base "
                         "self-compression FALSIFIES the claim that this solver carries a "
                         "static pressure bias large enough to explain job B's +34 to +64 "
                         "percent.",
        },
    }
    print(json.dumps(cfg, indent=2, sort_keys=True), flush=True)

    rows = []
    for f in range(a.frames):
        s.step(dt, substeps)
        prof = pressure_profile(s, n_p, dx, FLOOR, surface_z)
        prof["frame"] = f
        prof["t_s"] = (f + 1) * dt * substeps
        prof["dpdz_rel_error"] = prof["fit_dpdz_Pa_per_m"] / (-ref) - 1.0
        rows.append(prof)
        if a.verbose and f % 20 == 0:
            print(f"  frame {f:4d}  dp/dz {prof['fit_dpdz_Pa_per_m']:10.2f} Pa/m  "
                  f"rel {prof['dpdz_rel_error']*100:+7.3f}%  "
                  f"below_floor {prof['n_below_floor']}", flush=True)

    tail = rows[len(rows) // 2:]
    rel = np.array([r["dpdz_rel_error"] for r in tail], float)
    verdict = {
        "window": "last 50 percent of frames",
        "n_frames_in_window": len(tail),
        "mean_dpdz_Pa_per_m": float(np.mean([r["fit_dpdz_Pa_per_m"] for r in tail])),
        "reference_dpdz_Pa_per_m": -ref,
        "mean_rel_error": float(rel.mean()),
        "mean_rel_error_pct": float(rel.mean() * 100.0),
        "std_rel_error_pct": float(rel.std() * 100.0),
        "band": band_of(float(rel.mean())),
        "expected_compressible_excess_pct": EXPECTED_COMPRESSIBLE_EXCESS * 100.0,
        "excess_beyond_compressibility_pct":
            float(rel.mean() * 100.0 - EXPECTED_COMPRESSIBLE_EXCESS * 100.0),
    }
    print("\n" + json.dumps({"verdict": verdict}, indent=2, sort_keys=True), flush=True)
    Path(a.out).write_text(json.dumps(
        {"config": cfg, "verdict": verdict, "rows": rows}, indent=1))
    print(f"\nwrote {a.out}", flush=True)


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--n-grid", type=int, default=64)
    p.add_argument("--lim", type=float, default=1.2)
    p.add_argument("--depth", type=float, default=0.5)
    p.add_argument("--frames", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="auto")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--out", default="hydrostatic_column.json")
    run(p.parse_args())


if __name__ == "__main__":
    main()
