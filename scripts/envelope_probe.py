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
    vehicle.extent = current * scale
    return vehicle


spec = get_vehicle("compact_sedan")
bbox = spec["bbox_m"]
v = fit_to_bbox(load_vehicle(VEHICLE_PLY), bbox)
pts = np.asarray(v.surface, dtype=np.float64)

print("=== do columns reach the underbody? (zlo = lowest occupied cell) ===")
for n_grid in [32, 64, 128]:
    h = (max(2.2 * bbox[0], 3.5 * bbox[1]) / n_grid) / 2.0
    key = np.floor(pts / h).astype(np.int64)
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
    k = key[order]
    col = k[:, :2]
    starts = np.flatnonzero(np.r_[True, np.any(col[1:] != col[:-1], axis=1)])
    ends = np.r_[starts[1:], len(k)]
    zlo_m = k[starts, 2] * h
    zhi_m = k[ends - 1, 2] * h
    print(f"  n_grid={n_grid:3d} h={h:.4f}  cols={len(starts):5d}  "
          f"zlo_m median={np.median(zlo_m):.3f}  "
          f"frac zlo<0.15m = {100*np.mean(zlo_m < 0.15):5.1f}%  "
          f"zhi_m median={np.median(zhi_m):.3f}")

print()
print("=== per-sheet coverage: points in the LOWER 25% of body height ===")
print(f"  whole cloud: {100*np.mean(pts[:,2] < 0.25*1.44):.2f}% of points below z=0.36m")

print()
print("=== footprint coverage of underbody, h=0.04 grid ===")
h = 0.04005
gx = np.floor(pts[:, 0] / h).astype(np.int64)
gy = np.floor(pts[:, 1] / h).astype(np.int64)
low = pts[:, 2] < 0.20
allcols = set(zip(gx.tolist(), gy.tolist()))
lowcols = set(zip(gx[low].tolist(), gy[low].tolist()))
print(f"  columns with any point: {len(allcols)}")
print(f"  columns with a point below z=0.20m: {len(lowcols)} "
      f"({100*len(lowcols)/len(allcols):.1f}% of occupied columns)")

print()
print("=== convergence test: solid_volume vs h, is there a limit? ===")
from warpmpm.vehicle import solidify_columns
for n_grid in [16, 32, 64, 128, 192, 256]:
    h = (max(2.2 * bbox[0], 3.5 * bbox[1]) / n_grid) / 2.0
    p = solidify_columns(pts, h)
    vol = len(p) * h ** 3
    print(f"  n_grid={n_grid:3d} h={h:.5f} N={len(p):7d} vol={vol:7.4f} m3  "
          f"rho={1390.0/vol:8.2f}")
