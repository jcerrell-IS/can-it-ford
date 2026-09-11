from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np

from geom_live import YARIS, load_vehicle_local, scene_grid

OUT = "/Users/josie/can-it-ford/figures/car_check.png"
AZIMS = (-24, -70, -118, 160)
ELEV = 20
DEPTH = 0.30
N_GRID = 64

v = load_vehicle_local(YARIS)
s = v.surface
ex, ey, ez = (float(t) for t in v.extent)
g = scene_grid(v.extent, DEPTH, N_GRID)

print("surface points", len(s))
print("extent m", np.round(v.extent, 4))
print("watertight", bool(v.mesh.is_watertight), "volume %.6f" % float(v.mesh.volume))
print("lim %.5f dx %.6f h %.7f layers %d" % (g["lim"], g["dx"], g["h"], g["water_layers"]))

fig = plt.figure(figsize=(13, 11), dpi=150)
fig.patch.set_facecolor("white")

for k, az in enumerate(AZIMS):
    ax = fig.add_subplot(2, 2, k + 1, projection="3d")
    ax.scatter(s[:, 0], s[:, 1], s[:, 2], s=0.30, c=s[:, 2],
               cmap="viridis", alpha=0.55, linewidths=0, rasterized=True)
    ax.set_box_aspect((ex, ey, ez))
    ax.view_init(elev=ELEV, azim=az)
    ax.set_xlabel("x (m)", fontsize=8)
    ax.set_ylabel("y (m)", fontsize=8)
    ax.set_zlabel("z (m)", fontsize=8)
    ax.tick_params(labelsize=7)
    view = "broadside" if az in (160,) else ("oblique" if az == -24 else "foreshortened")
    ax.set_title("azim %d, elev %d  (%s)" % (az, ELEV, view), fontsize=10)
    ax.grid(True, alpha=0.25)

fig.suptitle(
    "G1 geometry check: VehicleBody.surface only, no water, no solver\n"
    "2010 Toyota Yaris NCAC coarse v1l, %d surface points, extent %.3f x %.3f x %.3f m, hull %.4f m3"
    % (len(s), ex, ey, ez, float(v.mesh.volume)),
    fontsize=11,
)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(OUT, facecolor="white")
print("WROTE", OUT)
