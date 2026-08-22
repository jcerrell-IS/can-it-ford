#!/usr/bin/env python
"""R7 MIRROR-SYMMETRY METAMORPHIC CONTROL  (promoted to a standing check)

PROVENANCE. Authored by dispatch D11 on 2026-08-14 15:55. Run by D9, D11, D4
and the coordinator that night. Preserved here because it previously existed
only on purgeable $SCRATCH and in /tmp.

WHAT IT FOUND, and no other gate in this project detects it: a resolution
ceiling. At a converged 200-frame settle the mirror asymmetry falls cleanly
(g48 0.1701, g64 0.0490, g96 0.0244 m) then breaks sharply: g100 still passes,
g104 fails at 1.5810 and 1.6027 m across two runs. Since r7_mirror.py:38 sets
lim = 9.421742313727737, the CANONICAL YARIS grid_lim, the ceiling translates
exactly into dx: between 0.090594 and 0.094217 m.

MANDATORY CAVEAT, measured by D4 (commit 1cfa5e0) and NOT optional:
the scene is NOT exactly symmetric by construction. by/h is non-integer at
every resolution (42.809, 57.079, 85.618), np.arange truncates the +y end, and
the body sits low by h*frac(by/h)/2 at t=0 with no physics. D4 then REFUTED its
own hypothesis: symmetrising drives the t=0 offset to 3e-09 m and leaves the
mirror discrepancy unchanged to 0.11%. So the defect is real and is not the
mechanism. Report this control as a RELATIVE change against its own baseline
at the same n_grid, never as an absolute guarantee.

TWO REPORTING RULES, both learned the hard way that night:
  1. NEVER quote a ratio. The determinism floor is itself a random variable
     (0.52 to 1.69 m across three identical g128 runs), so a ratio inverts with
     run length. Report the absolute asymmetry AND the floor, each with N.
  2. R7_FRAMES defaults to 20 and this stack rings with a ~100-frame period.
     A 20-frame measurement sits INSIDE the transient. Use 200.

Usage:  R7_NGRID=96 R7_FRAMES=200 python r7_mirror_control.py
Runs on VISTA only: LS6's warpmpm is a 6-line stub.
"""

_ORIGINAL_DOCSTRING = """R7 metamorphic control: mirror symmetry.

Design note, and it is the reason this is decisive:
the scene is built EXACTLY symmetric about the plane y = lim/2, by construction.
Water block, rigid body and the inflow slab are all symmetric in y; flow is +x;
gravity is -z. Therefore the exact solution is y-symmetric at every time.
Any y-asymmetry in the OUTPUT is a solver defect, with no interpretation needed
and with no mirror-transform rounding to argue about.

Run 1 and run 2 are byte-identical configs, so their difference is the
determinism / reduction-order floor (R2). The asymmetry is only meaningful
against that floor, so both are reported.
"""
import json, os, sys, time
import numpy as np

np.random.seed(12345)  # ULP cache defect: seed before any vehicle load

from warpmpm.core.solver import GridConfig, Solver
from warpmpm.materials import newtonian

DEV = "cuda"
N_GRID = int(os.environ.get("R7_NGRID", "48"))
FRAMES = int(os.environ.get("R7_FRAMES", "20"))
SETTLE = 8
DEPTH = 0.2944294473039918     # canonical realized depth
VELOCITY = 1.5                 # canonical, +x
FPS = 30.0
WATER_RHO, WATER_ETA, BULK = 1000.0, 1.0e-3, 1.5e5
VEH_RHO = 310.494              # canonical Yaris effective density
FLOOR_FRICTION = 0.55          # canonical floor value; see error-budget caveats


def build(mirror=False):
    """Symmetric-by-construction scene. mirror=True applies y -> lim-y to the
    initial state; for a symmetric scene this must be a no-op physically."""
    lim = 9.421742313727737           # canonical Yaris grid_lim
    grid = GridConfig(n_grid=N_GRID, grid_lim=lim)
    dx = grid.dx
    h = dx / 2.0
    floor = 3.0 * dx
    wall = 4.0 * dx

    # --- rigid box, centred in y, canonical hull bbox proportions ---
    bx, by, bz = 1.7078, 4.2014, 1.4853
    cx, cy = lim * 0.5, lim * 0.5
    gx = np.arange(cx - bx / 2, cx + bx / 2 + 1e-9, h)
    gy = np.arange(cy - by / 2, cy + by / 2 + 1e-9, h)
    gz = np.arange(floor, floor + bz + 1e-9, h)
    B = np.stack(np.meshgrid(gx, gy, gz, indexing="ij"), -1).reshape(-1, 3)
    # force exact y-symmetry of the body about cy
    B[:, 1] = cy + (B[:, 1] - cy)

    # --- water block, symmetric in y, spanning the tank ---
    wx = np.arange(wall, lim - wall + 1e-9, h)
    wy = np.arange(wall, lim - wall + 1e-9, h)
    wz = np.arange(floor, floor + DEPTH + 1e-9, h)
    W = np.stack(np.meshgrid(wx, wy, wz, indexing="ij"), -1).reshape(-1, 3)

    # carve water inside the body bbox
    inside = ((W[:, 0] >= gx[0]) & (W[:, 0] <= gx[-1]) &
              (W[:, 1] >= gy[0]) & (W[:, 1] <= gy[-1]) &
              (W[:, 2] >= gz[0]) & (W[:, 2] <= gz[-1]))
    W = W[~inside]

    if mirror:
        W[:, 1] = lim - W[:, 1]
        B[:, 1] = lim - B[:, 1]

    pos = np.concatenate([W, B]).astype(np.float64)
    vol = np.full(len(pos), h ** 3, dtype=np.float32)
    n_water, n_total = len(W), len(pos)

    s = Solver(grid=grid, device=DEV).load_particles(pos, vol)
    s.set_material(newtonian(eta=WATER_ETA, density=WATER_RHO, bulk_modulus=BULK))
    s.set_material_range(n_water, n_total, "rigid", obj_id=0, density=VEH_RHO)
    s.finalize_rigid_bodies()
    s.add_plane((0, 0, floor), (0, 0, 1), "slip",
                friction=FLOOR_FRICTION, restitution=0.05)
    for pt, nrm in (((wall, 0, 0), (1, 0, 0)), ((lim - wall, 0, 0), (-1, 0, 0)),
                    ((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
    s.add_domain_walls()

    c = float(np.sqrt(1.1 * BULK / WATER_RHO))
    rate = max(c / (0.28 * dx), 6.0 * WATER_ETA / (WATER_RHO * dx * dx),
               VELOCITY / (0.5 * dx))
    substeps = int(np.ceil(rate / FPS))
    dt = (1.0 / FPS) / substeps
    return s, dt, substeps, n_water, n_total, lim, cy


def run(mirror=False, tag=""):
    s, dt, substeps, n_water, n_total, lim, cy = build(mirror)
    for _ in range(SETTLE):
        s.step(dt, substeps)
    v = s.v(); v[:n_water, 0] += VELOCITY; s.set_v(v)
    for _ in range(FRAMES):
        s.step(dt, substeps)
    p = np.asarray(s.x(), dtype=np.float64)
    vv = np.asarray(s.v(), dtype=np.float64)
    if mirror:                       # map back into the unmirrored frame
        p[:, 1] = lim - p[:, 1]
        vv[:, 1] = -vv[:, 1]
    return dict(pos=p, vel=vv, n_water=n_water, n_total=n_total, cy=cy, tag=tag)


def y_asymmetry(r):
    """Net y-momentum and y-centroid offset of the water. Both are exactly 0
    for a y-symmetric state, so they measure the defect directly."""
    p, v, nw, cy = r["pos"], r["vel"], r["n_water"], r["cy"]
    wy, wvy = p[:nw, 1], v[:nw, 1]
    by = p[nw:, 1]
    return dict(
        water_ycentroid_offset_m=float(np.mean(wy) - cy),
        water_net_vy_mps=float(np.mean(wvy)),
        water_abs_vy_mean_mps=float(np.mean(np.abs(wvy))),
        body_ycentroid_offset_m=float(np.mean(by) - cy),
    )


if __name__ == "__main__":
    t0 = time.time()
    out = {"n_grid": N_GRID, "frames": FRAMES, "device": DEV,
           "gpu": os.environ.get("CUDA_VISIBLE_DEVICES", "unset")}
    a1 = run(False, "A1")
    a2 = run(False, "A2")          # determinism floor, identical config
    b = run(True, "B_mirrored")

    out["A1_asymmetry"] = y_asymmetry(a1)
    out["A2_asymmetry"] = y_asymmetry(a2)
    out["B_asymmetry"] = y_asymmetry(b)
    # floor: A1 vs A2, identical inputs
    out["determinism_floor_max_abs_dpos_m"] = float(
        np.max(np.abs(a1["pos"] - a2["pos"])))
    # mirror discrepancy: A1 vs mirrored-back B
    out["mirror_max_abs_dpos_m"] = float(np.max(np.abs(a1["pos"] - b["pos"])))
    out["n_water"] = a1["n_water"]
    out["n_total"] = a1["n_total"]
    out["wall_seconds"] = round(time.time() - t0, 1)
    print("R7_RESULT_JSON " + json.dumps(out))
