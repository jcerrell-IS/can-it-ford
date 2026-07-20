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
    vehicle.spacing = float("inf")
    return vehicle


spec = get_vehicle("compact_sedan")
bbox = spec["bbox_m"]
v = fit_to_bbox(load_vehicle(VEHICLE_PLY), bbox)
pts = np.asarray(v.surface, dtype=np.float64)
lo, hi = pts.min(0), pts.max(0)
print(f"cloud: {len(pts)} points   z range [{lo[2]:.3f}, {hi[2]:.3f}]")

print()
print("=== z histogram over whole cloud (fraction of points per 10% height band) ===")
zn = (pts[:, 2] - lo[2]) / (hi[2] - lo[2])
counts, edges = np.histogram(zn, bins=10, range=(0.0, 1.0))
for i in range(10):
    bar = "#" * int(round(60 * counts[i] / counts.max()))
    print(f"  z {edges[i]:.1f}-{edges[i+1]:.1f}  {counts[i]:6d} ({100*counts[i]/len(pts):5.2f}%) {bar}")

print()
print("=== central-footprint column: is there anything under the roof? ===")
cx = (lo[0] + hi[0]) / 2.0
cy = (lo[1] + hi[1]) / 2.0
for frac in [0.05, 0.10, 0.20]:
    rx = frac * (hi[0] - lo[0])
    ry = frac * (hi[1] - lo[1])
    m = (np.abs(pts[:, 0] - cx) < rx) & (np.abs(pts[:, 1] - cy) < ry)
    sel = pts[m]
    if len(sel) == 0:
        print(f"  central {frac*100:.0f}% patch: NO POINTS")
        continue
    zs = sel[:, 2]
    zsn = (zs - lo[2]) / (hi[2] - lo[2])
    print(f"  central {frac*100:.0f}% patch: {len(sel):6d} pts  "
          f"z_norm min={zsn.min():.3f} p05={np.percentile(zsn,5):.3f} "
          f"median={np.median(zsn):.3f} max={zsn.max():.3f}  "
          f"frac below z_norm 0.25 = {100*np.mean(zsn < 0.25):.2f}%")

print()
print("=== column span distribution vs h ===")
for n_grid in [32, 64, 128]:
    h = (max(2.2 * bbox[0], 3.5 * bbox[1]) / n_grid) / 2.0
    key = np.floor(pts / h).astype(np.int64)
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
    k = key[order]
    col = k[:, :2]
    starts = np.flatnonzero(np.r_[True, np.any(col[1:] != col[:-1], axis=1)])
    ends = np.r_[starts[1:], len(k)]
    zlo = k[starts, 2]
    zhi = k[ends - 1, 2]
    span_cells = zhi - zlo + 1
    span_m = span_cells * h
    ppc = ends - starts
    print(f"  n_grid={n_grid:3d} h={h:.4f}  columns={len(starts):5d}  "
          f"points/col median={int(np.median(ppc)):4d}  "
          f"span_m mean={span_m.mean():.3f} median={np.median(span_m):.3f}  "
          f"single_cell={100*np.mean(zlo == zhi):5.2f}%")
