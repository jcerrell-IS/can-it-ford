import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path

RUN = sys.argv[1] if len(sys.argv) > 1 else "g64_m1100"
VIEW = sys.argv[2] if len(sys.argv) > 2 else "oblique"
DPI = int(sys.argv[3]) if len(sys.argv) > 3 else 130
ONLY = int(sys.argv[4]) if len(sys.argv) > 4 else -1

PAD_XY = 3.4
BODY = "#B23A2E"
TIRE = "#1A1B20"
WATER_PLANE = "#4C7FA8"

ROOT = Path.home() / "can-it-ford" / "renders" / "yaris_render_s1"
OUT = ROOT / f"tier2_{RUN}_{VIEW}_dpi{DPI}"
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
ngrid = int(d["n_grid"])
nframes = int(water.shape[0])
depth_nom = 4.0 * h

pv_ref = (ref0 - t[0]) @ R[0]
offset = (pv_ref - pv).mean(0)
resid = float((pv_ref - pv).std(0).max())
print(f"offset {offset}   residual std {resid:.3e}")
if resid > 1e-3:
    print("STOP: offset is not a rigid translation")
    sys.exit(1)
pvc = pv + offset


def shell(P, cell):
    keep = set()
    for ax in range(3):
        o = [a for a in range(3) if a != ax]
        gi = np.floor(P[:, o[0]] / cell).astype(np.int64)
        gj = np.floor(P[:, o[1]] / cell).astype(np.int64)
        key = gi * 1000003 + gj
        order = np.lexsort((P[:, ax], key))
        ks = key[order]
        first = np.ones(len(ks), bool)
        first[1:] = ks[1:] != ks[:-1]
        last = np.ones(len(ks), bool)
        last[:-1] = ks[1:] != ks[:-1]
        keep.update(order[first].tolist())
        keep.update(order[last].tolist())
    return np.array(sorted(keep), dtype=np.int64)


sh = shell(pvc, h * 0.9)
pvs = pvc[sh]
print(f"shell {len(pvs)} of {len(pvc)} particles ({100*len(pvs)/len(pvc):.1f} pct)")

lo, hi = pvs.min(0), pvs.max(0)
size = hi - lo
print(f"vehicle extent {size}")
zc = pvs[:, 2] - lo[2]
yc = pvs[:, 1] - (lo[1] + hi[1]) / 2.0
tire = (zc < 0.30 * size[2]) & (np.abs(yc) > 0.30 * size[1])
body = ~tire
print(f"parts  wheels {tire.sum()} ({100*tire.sum()/len(pvs):.1f} pct)   "
      f"body {body.sum()} ({100*body.sum()/len(pvs):.1f} pct)")
if tire.sum() < 0.02 * len(pvs):
    print("WARNING wheel group under 2 percent, thresholds need adjusting")

vmax = float(np.percentile(speed, 99))
wsurf = floor + depth_nom
elev, azim = (72, -90) if VIEW == "top" else (16, -58)
print(f"speed vmax {vmax:.4f}   water plane z={wsurf:.4f}   frames {nframes}")

frames = [ONLY] if ONLY >= 0 else range(nframes)
for f in frames:
    V = pvs @ R[f].T + t[f]
    cx, cy = V[:, 0].mean(), V[:, 1].mean()
    xlo, xhi = cx - PAD_XY, cx + PAD_XY
    ylo, yhi = cy - PAD_XY, cy + PAD_XY
    zlo, zhi = floor - 0.04, floor + 2.05

    W = water[f]
    S = speed[f]
    m = ((W[:, 0] > xlo) & (W[:, 0] < xhi) & (W[:, 1] > ylo) & (W[:, 1] < yhi))
    W, S = W[m], S[m]

    fig = plt.figure(figsize=(10.5, 6.4), dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")

    corners = [[xlo, ylo, wsurf], [xhi, ylo, wsurf], [xhi, yhi, wsurf], [xlo, yhi, wsurf]]
    ax.add_collection3d(Poly3DCollection([corners], facecolor=WATER_PLANE,
                                         alpha=0.16, edgecolor="none", zorder=1))

    sc = ax.scatter(W[:, 0], W[:, 1], W[:, 2], c=S, cmap="viridis", vmin=0.0, vmax=vmax,
                    s=2.6, alpha=0.50, linewidths=0, depthshade=False, zorder=2)
    ax.scatter(V[body, 0], V[body, 1], V[body, 2], c=BODY, s=6.5,
               alpha=1.0, linewidths=0, depthshade=False, zorder=4)
    ax.scatter(V[tire, 0], V[tire, 1], V[tire, 2], c=TIRE, s=6.5,
               alpha=1.0, linewidths=0, depthshade=False, zorder=5)

    ax.set_xlim(xlo, xhi); ax.set_ylim(ylo, yhi); ax.set_zlim(zlo, zhi)
    ax.set_box_aspect((1.0, 1.0, 0.40))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("x (m)", fontsize=8, labelpad=2)
    ax.set_ylabel("y (m)", fontsize=8, labelpad=2)
    ax.set_zlabel("z (m)", fontsize=8, labelpad=2)
    ax.tick_params(labelsize=7)
    ax.grid(False)
    ax.xaxis.pane.set_alpha(0.04); ax.yaxis.pane.set_alpha(0.04); ax.zaxis.pane.set_alpha(0.04)

    cb = fig.colorbar(sc, ax=ax, shrink=0.52, pad=0.02, aspect=22)
    cb.set_label("water speed (m/s)", fontsize=8)
    cb.ax.tick_params(labelsize=7)

    disp = float(np.linalg.norm(t[f] - t[0]))
    ax.set_title(f"Toyota Yaris hull, {mass:.0f} kg, MPM n_grid={ngrid}\n"
                 f"still-water depth {depth_nom:.3f} m, flow 1.5 m/s   |   "
                 f"t = {f/30.0:.2f} s, lateral drift = {disp*100:.1f} cm",
                 fontsize=10, pad=14)
    fig.tight_layout()
    fig.savefig(OUT / f"f_{f:04d}.png", facecolor="white")
    plt.close(fig)
    if ONLY < 0 and f % 15 == 0:
        print(f"  {f}/{nframes}")

print(f"wrote to {OUT}")
