from pathlib import Path
import csv
import sys
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
from vehicle_params import get_vehicle
from warpmpm.vehicle import load_vehicle

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"
OUT_CSV = REPO_ROOT / "logs" / "n_grid_solidify_sweep.csv"

VEHICLE_CLASSES = {
    "sedan": "compact_sedan",
    "suv": "midsize_suv",
    "pickup": "light_pickup",
}

N_GRIDS = [32, 48, 64, 96, 128]
MAX_SWEEP_DEPTH = 0.60


def fit_to_bbox(vehicle, bbox_m):
    length, width, height = bbox_m
    target = np.array([width, length, height], dtype=np.float64)
    current = np.asarray(vehicle.extent, dtype=np.float64)
    if np.any(current <= 0.0):
        raise ValueError(f"degenerate vehicle extent {current}")
    scale = target / current
    surface = np.asarray(vehicle.surface, dtype=np.float64) * scale
    vehicle.surface = surface.astype(np.float32)
    if vehicle.splat_pos is not None:
        vehicle.splat_pos = (np.asarray(vehicle.splat_pos, dtype=np.float64)
                             * scale).astype(np.float32)
    vehicle.extent = current * scale
    vehicle.spacing = float("inf")
    return vehicle


def domain_lim(bbox_m, depth):
    length, width, height = bbox_m
    return max(2.2 * length, 3.5 * width, 6.0 * depth)


def column_stats(pos, h):
    key = np.floor(np.asarray(pos, dtype=np.float64) / h).astype(np.int64)
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
    k = key[order]
    col = k[:, :2]
    starts = np.flatnonzero(np.r_[True, np.any(col[1:] != col[:-1], axis=1)])
    ends = np.r_[starts[1:], len(k)]
    zlo = k[starts, 2]
    zhi = k[ends - 1, 2]
    span = zhi - zlo + 1
    return {
        "n_columns": int(len(starts)),
        "n_single_cell_columns": int(np.count_nonzero(zlo == zhi)),
        "frac_single_cell": float(np.count_nonzero(zlo == zhi) / len(starts)),
        "cells_filled": int(span.sum()),
        "mean_span_cells": float(span.mean()),
    }


base = load_vehicle(VEHICLE_PLY)
print(f"splat: {len(base.surface)} surface points, native spacing {base.spacing:.5f} m")
print(f"raw extent (x,y,z) = {np.asarray(base.extent)}")
print()

rows = []
for vclass, params_key in VEHICLE_CLASSES.items():
    spec = get_vehicle(params_key)
    bbox_m = spec["bbox_m"]
    mass = spec["mass_kg"]

    lim = domain_lim(bbox_m, MAX_SWEEP_DEPTH)
    lim_no_depth = max(2.2 * bbox_m[0], 3.5 * bbox_m[1])
    depth_binds = lim != lim_no_depth

    print(f"=== {vclass}  bbox={bbox_m}  mass={mass} kg  lim={lim:.4f} m  "
          f"depth_term_binds={depth_binds}")

    prev = None
    for n_grid in N_GRIDS:
        v = fit_to_bbox(load_vehicle(VEHICLE_PLY), bbox_m)
        dx = lim / n_grid
        h = dx / 2.0
        v.solidify(h)

        n_particles = v.n_particles
        solid_volume = n_particles * h ** 3
        density = mass / solid_volume
        stats = column_stats(v.surface, h)

        if prev is None:
            exponent = float("nan")
            n_ratio = float("nan")
        else:
            n_ratio = n_particles / prev["n_particles"]
            exponent = np.log(n_ratio) / np.log(prev["h"] / h)

        row = {
            "vehicle_class": vclass,
            "n_grid": n_grid,
            "dx_m": round(dx, 6),
            "h_m": round(h, 6),
            "n_particles": n_particles,
            "solid_volume_m3": round(solid_volume, 5),
            "vehicle_density_kgm3": round(density, 2),
            "density_plausible": 100.0 <= density <= 300.0,
            "n_columns": stats["n_columns"],
            "frac_single_cell": round(stats["frac_single_cell"], 4),
            "mean_span_cells": round(stats["mean_span_cells"], 3),
            "n_ratio_vs_prev": round(n_ratio, 4) if prev else "",
            "scaling_exponent": round(float(exponent), 4) if prev else "",
        }
        rows.append(row)

        assert stats["cells_filled"] == n_particles, (
            f"column fill cross-check failed: {stats['cells_filled']} != {n_particles}")

        print(f"  n_grid={n_grid:3d} h={h:.5f} N={n_particles:7d} "
              f"vol={solid_volume:7.4f} rho={density:8.2f} "
              f"plaus={str(row['density_plausible']):5s} "
              f"single_cell_cols={stats['frac_single_cell']*100:5.1f}% "
              f"mean_span={stats['mean_span_cells']:6.2f} "
              f"exp={row['scaling_exponent']}")

        prev = {"n_particles": n_particles, "h": h}
    print()

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_CSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote {OUT_CSV} ({len(rows)} rows)")
