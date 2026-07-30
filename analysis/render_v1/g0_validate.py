from __future__ import annotations

import numpy as np

from geom_live import YARIS, load_vehicle_local, scene_grid

DEPTH = 0.30
N_GRID = 64
MASS = 1100.0

TARGETS = {
    "hull_volume": 3.542739,
    "extent": np.array([1.7464, 4.2826, 1.518]),
    "lim": 9.42164,
    "h": 0.0736066,
    "wt_particles": 8904,
    "wt_volume": 3.55094,
    "wt_ratio": 1.0023,
    "wt_rho": 309.78,
    "col_particles": 19338,
    "col_ratio": 2.1769,
}

v = load_vehicle_local(YARIS)
m = v.mesh
hull = float(m.volume)

print("SOURCE", v.source)
print("is_watertight", bool(m.is_watertight))
print("faces", len(m.faces), "vertices", len(m.vertices))
print("hull_volume_m3 %.6f" % hull, " target %.6f" % TARGETS["hull_volume"])
print("extent_m", np.round(v.extent, 4), " target", TARGETS["extent"])

g = scene_grid(v.extent, DEPTH, N_GRID)
print("lim %.5f" % g["lim"], " target %.5f" % TARGETS["lim"])
print("dx %.6f  h %.7f" % (g["dx"], g["h"]), " target h %.7f" % TARGETS["h"])
print("floor %.6f  water_layers %d" % (g["floor"], g["water_layers"]))

v.solidify(g["h"])
n_wt = len(v.particles)
vol_wt = n_wt * g["h"] ** 3
print("PARITY  N %d (target %d)  vol %.5f (target %.5f)  ratio %.4f (target %.4f)  rho %.2f (target %.2f)"
      % (n_wt, TARGETS["wt_particles"], vol_wt, TARGETS["wt_volume"],
         vol_wt / hull, TARGETS["wt_ratio"], MASS / vol_wt, TARGETS["wt_rho"]))

v.solidify(g["h"], force_columns=True)
n_col = len(v.particles)
vol_col = n_col * g["h"] ** 3
print("COLUMNS N %d (target %d)  vol %.5f  ratio %.4f (target %.4f)  rho %.2f"
      % (n_col, TARGETS["col_particles"], vol_col, vol_col / hull,
         TARGETS["col_ratio"], MASS / vol_col))

ok = (
    abs(hull - TARGETS["hull_volume"]) < 1e-4
    and np.allclose(v.extent, TARGETS["extent"], atol=2e-3)
    and abs(g["lim"] - TARGETS["lim"]) < 1e-3
    and abs(g["h"] - TARGETS["h"]) < 1e-6
    and n_col == TARGETS["col_particles"]
)
print("VALIDATION", "PASS" if ok else "FAIL")
