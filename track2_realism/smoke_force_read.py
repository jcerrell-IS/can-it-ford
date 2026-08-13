#!/usr/bin/env python3
"""
NON-CANONICAL, TRACK 2 EXPLORATORY. Never merge into main without a separate,
deliberate human decision. Produced on branch track2/coupled-realism-explore in
an isolated git worktree. No canonical Track 1 artifact was read or written.

PURPOSE: smallest possible scene that answers ONE question, empirically:
can the LegacyCoupler's MPM -> rigid coupling force be READ back from Python,
and does it match analytic buoyancy on a trivially-known geometry (a cube)?

This is API reconnaissance, NOT the validation. The cube is a control whose
analytic answer is exact, so any disagreement here is a harness bug, not physics.

Genesis convention note: dx = 1/grid_density (mpm_solver.py:53), INDEPENDENT of
domain bounds. Never merge this with warpmpm's domain-dependent dx.
"""
import sys
import numpy as np
import genesis as gs

GRID_DENSITY = 64
DX = 1.0 / GRID_DENSITY
G = 9.81
RHO_W = 1000.0

# cube fully submerged
CUBE = 0.1
CUBE_VOL = CUBE ** 3
CUBE_POS = (0.25, 0.25, 0.14)
WATER_H = 0.35

F_ANALYTIC = RHO_W * G * CUBE_VOL

# Genesis MPM applies a 3-cell safety padding inside the declared bounds, measured
# live from the boundary error: lower 0.046875 = 3*dx at dx=0.015625. Fluid seeded
# outside that inset is a hard exception, not a warning.
PAD = 3.0 * DX + 1e-4

print(f"[cfg] grid_density={GRID_DENSITY} dx={DX:.6f} m pad={PAD:.6f} m", flush=True)
print(f"[cfg] cube {CUBE} m, V={CUBE_VOL:.6f} m^3, F_analytic={F_ANALYTIC:.4f} N", flush=True)
print(f"[cfg] cube top={CUBE_POS[2]+CUBE/2:.4f}, water={WATER_H}, "
      f"cover={(WATER_H-(CUBE_POS[2]+CUBE/2))/DX:.2f} dx", flush=True)

gs.init(backend=gs.gpu, precision="32", logging_level="warning")

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=2e-3, substeps=10, gravity=(0.0, 0.0, -G)),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(0.0, 0.0, 0.0),
        upper_bound=(0.5, 0.5, 0.5),
        grid_density=GRID_DENSITY,
    ),
    show_viewer=False,
)

water = scene.add_entity(
    material=gs.materials.MPM.Liquid(rho=RHO_W),
    morph=gs.morphs.Box(lower=(PAD, PAD, PAD), upper=(0.5 - PAD, 0.5 - PAD, WATER_H)),
)

cube = scene.add_entity(
    material=gs.materials.Rigid(rho=500.0),
    morph=gs.morphs.Box(pos=CUBE_POS, size=(CUBE, CUBE, CUBE), fixed=True),
)

scene.build()
print("[ok] scene built", flush=True)

rs = scene.sim.rigid_solver
ls = rs.links_state
print(f"[probe] cfrc_coupling_vel shape={ls.cfrc_coupling_vel.shape}", flush=True)
print(f"[probe] n_links={rs.n_links}", flush=True)
try:
    print(f"[probe] cube link idx range: {cube.link_start}..{cube.link_end}", flush=True)
except Exception as e:
    print(f"[probe] link idx introspect failed: {e}", flush=True)

LINK = cube.link_start


def read_coupling_force():
    """Net coupling force on the rigid link, in Newtons.

    misc.py:715-716 stores the NEGATIVE of the applied force (-=), so the
    physical force on the body is the negation of what is stored.
    """
    arr = ls.cfrc_coupling_vel.to_numpy()
    return -np.asarray(arr[LINK, 0], dtype=np.float64)


for step in range(60):
    scene.step()
    if step % 10 == 0 or step == 59:
        f = read_coupling_force()
        fz = f[2]
        err = 100.0 * (fz - F_ANALYTIC) / F_ANALYTIC
        print(f"[step {step:3d}] Fz={fz:12.5f} N   analytic={F_ANALYTIC:10.5f} N   "
              f"err={err:+8.3f}%   Fxy=({f[0]:+.4f},{f[1]:+.4f})", flush=True)

print("[done] smoke complete", flush=True)
