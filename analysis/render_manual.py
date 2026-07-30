import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

RUN = sys.argv[1] if len(sys.argv) > 1 else "g64_m1100"
VIEW = sys.argv[2] if len(sys.argv) > 2 else "oblique"
WATER_MAX = 20000

ROOT = Path.home() / "can-it-ford" / "renders" / "yaris_render_s1"
OUT = ROOT / f"manual_{RUN}_{VIEW}"
OUT.mkdir(parents=True, exist_ok=True)

d = np.load(ROOT / RUN / "rollout.npz", allow_pickle=True)
water = d["water"]
speed = d["speed"]
R = d["R"].astype(np.float64)
t = d["t"].astype(np.float64)
pv = d["veh_particles_vehframe"].astype(np.float64)
ref0 = d["veh_particles_scene0"].astype(np.float64)
h = float(d["h"])
floor = float(d["floor"])
mass = float(d["mass"])
nframes = water.shape[0]

pv_from_ref = (ref0 - t[0]) @ R[0]
offset = (pv_from_ref - pv).mean(0)
resid = (pv_from_ref - pv).std(0).max()
print(f"offset {offset}  residual std {resid:.3e}")
if resid > 1e-3:
    print("WARNING offset is not a rigid translation, residual too large")

pv_corr = pv + offset

lo = pv_corr.min(0)
hi = pv_corr.max(0)
size = hi - lo
zc = pv_corr[:, 2] - lo[2]
yc = pv_corr[:, 1] - (lo[1] + hi[1]) / 2.0
is_tire = (zc < 0.30 * size[2]) & (np.abs(yc) > 0.30 * size[1])
is_glass = (zc > 0.62 * size[2]) & (~is_tire)
is_body = ~(is_tire | is_glass)
print(f"parts  tires {is_tire.sum()}  glass {is_glass.sum()}  body {is_body.sum()}  total {len(pv_corr)}")

rng = np.random.default_rng(0)
sub = rng.choice(water.shape[1], size=min(WATER_MAX, water.shape[1]), replace=False)

vmax = float(np.percentile(speed[:, sub], 99))
print(f"speed colour limit p99 {vmax:.4f}")

allx = np.concatenate([water[:, sub, 0].ravel(), t[:, 0] + pv_corr[:, 0].mean()])
xlo, xhi = float(water[:, sub, 0].min()), float(water[:, sub, 0].max())
ylo, yhi = float(water[:, sub, 1].min()), float(water[:, sub, 1].max())
zlo, zhi = floor - 0.05, float(water[:, sub, 2].max()) + 0.2

if VIEW == "top":
    elev, azim = 88, -90
else:
    elev, azim = 20, -62

for f in range(nframes):
    V = pv_corr @ R[f].T + t[f]
    W = water[f, sub]
    S = speed[f, sub]

    fig = plt.figure(figsize=(10, 6), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(W[:, 0], W[:, 1], W[:, 2], c=S, cmap="viridis",
               vmin=0.0, vmax=vmax, s=1.2, alpha=0.30, linewidths=0, depthshade=False)
    ax.scatter(V[is_body, 0], V[is_body, 1], V[is_body, 2],
               c="#B23A2E", s=3.2, alpha=0.95, linewidths=0, depthshade=False)
    ax.scatter(V[is_glass, 0], V[is_glass, 1], V[is_glass, 2],
               c="#6B8FA3", s=3.2, alpha=0.95, linewidths=0, depthshade=False)
    ax.scatter(V[is_tire, 0], V[is_tire, 1], V[is_tire, 2],
               c="#22232A", s=3.2, alpha=1.0, linewidths=0, depthshade=False)

    ax.set_xlim(xlo, xhi)
    ax.set_ylim(ylo, yhi)
    ax.set_zlim(zlo, zhi)
    ax.set_box_aspect((xhi - xlo, yhi - ylo, (zhi - zlo) * 3.0))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("x (m)", fontsize=8)
    ax.set_ylabel("y (m)", fontsize=8)
    ax.set_zlabel("z (m)", fontsize=8)
    ax.tick_params(labelsize=7)
    disp = np.linalg.norm(t[f] - t[0])
    ax.set_title(f"{RUN}   mass {mass:.0f} kg   frame {f:03d}   |d| = {disp*100:.1f} cm",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / f"f_{f:04d}.png")
    plt.close(fig)
    if f % 15 == 0:
        print(f"  frame {f}/{nframes}")

print(f"wrote {nframes} frames to {OUT}")
