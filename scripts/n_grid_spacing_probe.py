from pathlib import Path
import sys
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
from vehicle_params import get_vehicle
from warpmpm.vehicle import load_vehicle

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"


def fit_to_bbox(vehicle, bbox_m):
    length, width, height = bbox_m
    target = np.array([width, length, height], dtype=np.float64)
    current = np.asarray(vehicle.extent, dtype=np.float64)
    scale = target / current
    vehicle.surface = (np.asarray(vehicle.surface, dtype=np.float64) * scale).astype(np.float32)
    if vehicle.splat_pos is not None:
        vehicle.splat_pos = (np.asarray(vehicle.splat_pos, dtype=np.float64) * scale).astype(np.float32)
    vehicle.extent = current * scale
    vehicle.spacing = float("inf")
    return vehicle


spec = get_vehicle("compact_sedan")
bbox = spec["bbox_m"]
mass = spec["mass_kg"]
lim = max(2.2 * bbox[0], 3.5 * bbox[1])

v = fit_to_bbox(load_vehicle(VEHICLE_PLY), bbox)
pts = np.asarray(v.surface, dtype=np.float64)
print(f"scaled sedan extent: {np.asarray(v.extent)}  target bbox: {bbox}")
print(f"bbox volume = {np.prod(bbox):.3f} m3 -> filled-box density = {mass / np.prod(bbox):.2f} kg/m3")
print(f"domain lim = {lim:.4f} m")

from scipy.spatial import cKDTree

tree = cKDTree(pts)
d, _ = tree.query(pts, k=2)
nn = d[:, 1]
print()
print("=== measured nearest-neighbour spacing of SCALED sedan cloud (m) ===")
print(f"  median {np.median(nn):.4f}  mean {nn.mean():.4f}  "
      f"p90 {np.percentile(nn, 90):.4f}  p99 {np.percentile(nn, 99):.4f}")
for n_grid in [16, 32, 64, 128]:
    print(f"  h at n_grid={n_grid:3d}: {(lim / n_grid) / 2.0:.4f}")

print()
print("=== extend sweep DOWN: does the exponent ever reach 3.0? ===")
prev = None
for n_grid in [8, 12, 16, 24, 32, 48, 64]:
    vv = fit_to_bbox(load_vehicle(VEHICLE_PLY), bbox)
    h = (lim / n_grid) / 2.0
    vv.solidify(h)
    n = vv.n_particles
    vol = n * h ** 3
    exp = "" if prev is None else f"{np.log(n / prev[0]) / np.log(prev[1] / h):.3f}"
    print(f"  n_grid={n_grid:3d} h={h:.4f} N={n:6d} vol={vol:7.3f} "
          f"rho={mass / vol:8.2f} exp={exp}")
    prev = (n, h)
