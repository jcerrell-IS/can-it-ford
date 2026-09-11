"""Render the MPM dough as a continuous surface, the way real dough looks.

Particles are a discretization; real dough is a continuous body. Each frame splats the
particle cloud onto a fine density grid, smooths it, and extracts an isosurface with
marching cubes: a watertight triangle mesh, shaded as dough and rendered with the
pressing plate. This is the standard surface-reconstruction path for MPM and SPH
("fluid surfacing").

Run:  python examples/dough_surface_render.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import device_cli, surface_from_cloud, write_mp4
from warpmpm import GridConfig, Solver, block, newtonian
from warpmpm.coupling.backend import WarpMPMBackend

OUT = Path(__file__).resolve().parents[1] / "out" / "surface"
LIGHT = np.array([0.35, 0.55, 0.78]); LIGHT = LIGHT / np.linalg.norm(LIGHT)
DOUGH = np.array([0.95, 0.82, 0.55])     # pizza-dough cream
DOUGH_TOP = np.array([0.86, 0.66, 0.40])  # slightly browner top

# kept under this name because experiments/surface_track_test.py imports it from here
_surface = surface_from_cloud


def _box_polys(cx, cy, cz, hx, hy, hz):
    c = np.array([[sx, sy, sz] for sx in (cx - hx, cx + hx)
                  for sy in (cy - hy, cy + hy) for sz in (cz - hz, cz + hz)])
    F = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    return [c[f] for f in F]


def run(tau_y=200.0, eta=40.0, geom=(0.16, 0.16, 0.06), n_grid=52, v_plate=0.08,
        press_strain=0.5, dt=1.0e-4, substeps=20, frame_stride=6, still_frac=0.55,
        speckle_tex=True, device="auto"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    OUT.mkdir(parents=True, exist_ok=True)
    grid = GridConfig(n_grid=n_grid, grid_lim=0.4)
    cw, cd, ch = geom
    pos, vol, floor = block(grid, size=geom, ppc=2)
    s = Solver(grid=grid, device=device).load_particles(pos, vol)
    s.set_material(newtonian(eta=eta, density=1000.0, bulk_modulus=9.0e5).with_yield(tau_y))
    s.add_plane((0, 0, floor), (0, 0, 1), "sticky")
    cx = cy = grid.grid_lim * 0.5
    bh = (0.5 * cw + 0.015, 0.5 * cd + 0.015, 0.6 * grid.dx)
    be = WarpMPMBackend(solver=s)
    z = floor + ch + bh[2]
    tool = be.attach_tool((cx, cy, z), bh)
    # per-particle MATERIAL-LOCKED speckle (flour flecks): fixed brightness per material point,
    # so the texture deforms WITH the dough (this is also what makes the surface trackable)
    speckle = np.random.default_rng(0).uniform(0.0, 1.0, len(pos))
    fdt = dt * substeps
    nf = round(press_strain * ch / v_plate / fdt)
    tmp = OUT / "_frames"; tmp.mkdir(exist_ok=True)
    for o in tmp.glob("*.png"):
        o.unlink()
    prev = z; k = 0; still_at = int(still_frac * nf)
    for f in range(nf + 1):
        zn = z - v_plate * fdt if f > 0 else z
        vz = (zn - prev) / fdt
        if f > 0:
            be.set_tool_kinematics(tool, center=(cx, cy, prev), velocity=(0, 0, vz))
            be.step(dt, substeps)
        z = zn; prev = zn
        if f % frame_stride and f != still_at:
            continue
        xp = s.x()
        vw, faces, fn = _surface(xp)
        sh = np.clip(fn @ LIGHT, 0, 1) * 0.6 + 0.4
        up = fn[:, 2] > 0.4                                    # top faces a touch browner
        base = np.where(up[:, None], DOUGH_TOP, DOUGH)
        if speckle_tex:
            _, idx = cKDTree(xp).query(vw[faces].mean(1))      # nearest material point / face
            tex = np.clip(0.6 + 0.55 * speckle[idx], 0.45, 1.2)  # flour flecks, material-locked
            fc = np.clip((sh * tex)[:, None] * base, 0, 1)
        else:
            fc = np.clip(sh[:, None] * base, 0, 1)
        fig = plt.figure(figsize=(7, 5.2), facecolor="white")
        ax = fig.add_subplot(111, projection="3d")
        tri = Poly3DCollection(vw[faces], facecolors=fc, edgecolors="none")
        tri.set_alpha(1.0); ax.add_collection3d(tri)
        # pressing plate
        pb = z - bh[2]
        plate = Poly3DCollection(_box_polys(cx, cy, pb + 0.004, bh[0], bh[1], 0.004),
                                 facecolors=(0.7, 0.72, 0.78), edgecolors="none", alpha=1.0)
        ax.add_collection3d(plate)
        ax.set_xlim(cx - 0.11, cx + 0.11); ax.set_ylim(cy - 0.11, cy + 0.11)
        ax.set_zlim(floor - 0.004, floor + 0.09); ax.set_box_aspect((1, 1, 0.5))
        ax.view_init(elev=16, azim=-58); ax.set_axis_off()
        strain = (floor + ch - pb) / ch * 100
        ax.set_title(f"pizza dough (surface)   strain {strain:4.1f}%", fontsize=11)
        fig.savefig(tmp / f"s_{k:04d}.png", dpi=130, facecolor="white"); plt.close(fig)
        if f == still_at:
            import shutil
            shutil.copy(tmp / f"s_{k:04d}.png", OUT / "dough_surface_still.png")
        k += 1
        print(f"frame {f:3d}/{nf} strain={strain:4.1f}% mesh {len(vw)} verts")
    mp4 = write_mp4(tmp, OUT / "dough_surface.mp4", fps=10, pattern="s_%04d.png")
    print("also wrote", OUT / "dough_surface_still.png")
    return {"video": str(mp4), "still": str(OUT / "dough_surface_still.png"),
            "device": device}


if __name__ == "__main__":
    args = device_cli().parse_args()
    run(device=args.device)
