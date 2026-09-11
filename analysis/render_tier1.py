import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

RUN = sys.argv[1] if len(sys.argv) > 1 else "g64_m1100"
VIEW = sys.argv[2] if len(sys.argv) > 2 else "oblique"
DPI = int(sys.argv[3]) if len(sys.argv) > 3 else 120
ONLY = int(sys.argv[4]) if len(sys.argv) > 4 else -1
WATER_MAX = 22000

ROOT = Path.home() / "can-it-ford" / "renders" / "yaris_render_s1"
OUT = ROOT / f"tier1_{RUN}_{VIEW}_dpi{DPI}"
OUT.mkdir(parents=True, exist_ok=True)

d = np.load(ROOT / RUN / "rollout.npz", allow_pickle=True)
water = d["water"]
speed = d["speed"]
R = d["R"].astype(np.float64)
t = d["t"].astype(np.float64)
pv = d["veh_particles_vehframe"].astype(np.float64)
ref0 = d["veh_particles_scene0"].astype(np.float64)
floor = float(d["floor"])
mass = float(d["mass"])
nframes = int(water.shape[0])

pv_ref = (ref0 - t[0]) @ R[0]
offset = (pv_ref - pv).mean(0)
resid = float((pv_ref - pv).std(0).max())
print(f"offset {offset}   residual std {resid:.3e}")
if resid > 1e-3:
    print("STOP: offset is not a rigid translation")
    sys.exit(1)
pvc = pv + offset

lo, hi = pvc.min(0), pvc.max(0)
size = hi - lo
zc = pvc[:, 2] - lo[2]
yc = pvc[:, 1] - (lo[1] + hi[1]) / 2.0
tire = (zc < 0.30 * size[2]) & (np.abs(yc) > 0.30 * size[1])
glass = (zc > 0.62 * size[2]) & (~tire)
body = ~(tire | glass)
n = len(pvc)
print(f"parts  tires {tire.sum()} ({100*tire.sum()/n:.1f}%)  "
      f"glass {glass.sum()} ({100*glass.sum()/n:.1f}%)  "
      f"body {body.sum()} ({100*body.sum()/n:.1f}%)")
for nm, m in (("tires", tire), ("glass", glass), ("body", body)):
    if m.sum() < 0.02 * n:
        print(f"WARNING {nm} group under 2 percent, segmentation likely failed")

rng = np.random.default_rng(0)
sub = rng.choice(water.shape[1], size=min(WATER_MAX, water.shape[1]), replace=False)
vmax = float(np.percentile(speed[:, sub], 99))
xlo, xhi = float(water[:, sub, 0].min()), float(water[:, sub, 0].max())
ylo, yhi = float(water[:, sub, 1].min()), float(water[:, sub, 1].max())
zlo, zhi = floor - 0.05, float(water[:, sub, 2].max()) + 0.20
elev, azim = (88, -90) if VIEW == "top" else (20, -62)
print(f"speed vmax {vmax:.4f}   frames {nframes}   dpi {DPI}")

frames = [ONLY] if ONLY >= 0 else range(nframes)
for f in frames:
    V = pvc @ R[f].T + t[f]
    W = water[f, sub]
    S = speed[f, sub]
    fig = plt.figure(figsize=(10, 6), dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(W[:, 0], W[:, 1], W[:, 2], c=S, cmap="viridis", vmin=0.0, vmax=vmax,
               s=1.1, alpha=0.28, linewidths=0, depthshade=False)
    ax.scatter(V[body, 0], V[body, 1], V[body, 2], c="#B23A2E", s=3.4,
               alpha=0.95, linewidths=0, depthshade=False)
    ax.scatter(V[glass, 0], V[glass, 1], V[glass, 2], c="#6B8FA3", s=3.4,
               alpha=0.95, linewidths=0, depthshade=False)
    ax.scatter(V[tire, 0], V[tire, 1], V[tire, 2], c="#22232A", s=3.4,
               alpha=1.0, linewidths=0, depthshade=False)
    ax.set_xlim(xlo, xhi); ax.set_ylim(ylo, yhi); ax.set_zlim(zlo, zhi)
    ax.set_box_aspect((xhi - xlo, yhi - ylo, (zhi - zlo) * 3.0))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("x (m)", fontsize=8); ax.set_ylabel("y (m)", fontsize=8)
    ax.set_zlabel("z (m)", fontsize=8); ax.tick_params(labelsize=7)
    disp = float(np.linalg.norm(t[f] - t[0]))
    ax.set_title(f"{RUN}   {mass:.0f} kg   n_grid {int(d['n_grid'])}   "
                 f"frame {f:03d}   |d| = {disp*100:.1f} cm", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / f"f_{f:04d}.png")
    plt.close(fig)
    if ONLY < 0 and f % 15 == 0:
        print(f"  {f}/{nframes}")

print(f"wrote to {OUT}")
