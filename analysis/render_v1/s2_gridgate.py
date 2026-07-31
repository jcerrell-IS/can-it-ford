from __future__ import annotations

import numpy as np

from geom_live import YARIS, load_vehicle_local, scene_grid

HULL = 3.542739
MASS = 1100.0
DEPTH = 0.30

v = load_vehicle_local(YARIS)
print("S-2 RE-DERIVATION OF THE GRID GATE UNDER solidify_watertight (parity fill)")
print("hull %.6f m3, mass %.1f kg, depth %.2f m, lim is depth-driven so it is FIXED at %.5f m"
      % (HULL, MASS, DEPTH, scene_grid(v.extent, DEPTH, 64)["lim"]))
print()
print("%-8s %-10s %-10s %-9s %-11s %-9s %-9s %-7s %s"
      % ("n_grid", "dx (m)", "h (m)", "N", "solid (m3)", "ratio", "rho", "layers", "gates"))

for n in (32, 48, 64, 96, 128, 192):
    g = scene_grid(v.extent, DEPTH, n)
    v.solidify(g["h"])
    N = len(v.particles)
    vol = N * g["h"] ** 3
    ratio = vol / HULL
    rho = MASS / vol
    ok_ratio = 0.85 <= ratio <= 1.20
    ok_rho = 100.0 <= rho <= 300.0
    ok_band = 0.95 <= ratio <= 1.10
    tag = []
    tag.append("ratio0.85-1.20:%s" % ("PASS" if ok_ratio else "FAIL"))
    tag.append("G-2 0.95-1.10:%s" % ("PASS" if ok_band else "FAIL"))
    tag.append("rho100-300:%s" % ("PASS" if ok_rho else "FAIL"))
    print("%-8d %-10.6f %-10.7f %-9d %-11.5f %-9.4f %-9.2f %-7d %s"
          % (n, g["dx"], g["h"], N, vol, ratio, rho, g["water_layers"], "  ".join(tag)))
