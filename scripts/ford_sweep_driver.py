from pathlib import Path
import argparse
import csv
import sys
import time
import numpy as np
import wandb

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
from vehicle_params import get_vehicle

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"
DATA_ROOT = Path("/work/11603/jcerrell0629/vista/can-it-ford/data")

VEHICLE_CLASSES = {
    "sedan": "compact_sedan",
    "suv": "midsize_suv",
    "pickup": "light_pickup",
}

SWEEP_CONFIGS = {
    "v2": {
        "outdir": DATA_ROOT / "track1_sweep_v2",
        "depths": [0.15, 0.30, 0.45, 0.60],
        "velocities": [1.0, 1.5, 2.0],
        "n_grid": 64,
    },
    "v3": {
        "outdir": DATA_ROOT / "track1_sweep_v3",
        "depths": [0.10, 0.15, 0.30, 0.45, 0.60],
        "velocities": [0.5, 1.0, 1.5, 2.0],
        "n_grid": 128,
    },
}

BASE_FRAMES = 90
MAX_FRAMES = 150
PLATEAU_WINDOW = 10
PLATEAU_TOL_M = 0.01
MIN_Z_LAYERS = 2

YARIS_PLY = str(REPO_ROOT / "vehicle_geometry_research" / "yaris_coarse_v1l_watertight.ply")
YARIS_MASS_KG = 1100.0  # PRIMARY source: LS-DYNA deck header "Version 1l, 1100 kg" (yaris-coarse-v1l.key line 27). 1078 is a SECONDARY NCAC download-page "modeled weight", logged not coded. rho emerges as mass/solid_volume at runtime (see below), not hardcoded. Per CLAUDE.md Physical Plausibility Checklist item 1.

parser = argparse.ArgumentParser()
parser.add_argument("--config", choices=sorted(SWEEP_CONFIGS), default="v2")
parser.add_argument("--vehicle", choices=["box", "yaris"], default="box")
parser.add_argument("--output", default=None)
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--allow-underresolved", action="store_true")
args, _ = parser.parse_known_args()

CONFIG = SWEEP_CONFIGS[args.config]
OUTDIR = Path(args.output).expanduser().resolve() if args.output else CONFIG["outdir"]
DEPTHS = CONFIG["depths"]
VELOCITIES = CONFIG["velocities"]
N_GRID = CONFIG["n_grid"]

USE_REAL_MESH = args.vehicle == "yaris"
if USE_REAL_MESH:
    VEHICLE_ITER = [("yaris", "compact_sedan")]
    VEHICLE_SOURCE_PLY = YARIS_PLY
else:
    VEHICLE_ITER = list(VEHICLE_CLASSES.items())
    VEHICLE_SOURCE_PLY = VEHICLE_PLY

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


def has_plateaued(history):
    d = np.asarray(history.displacement)
    if len(d) < PLATEAU_WINDOW + 1:
        return False
    mag = np.linalg.norm(d, axis=1)
    recent = mag[-PLATEAU_WINDOW:]
    return float(recent.max() - recent.min()) < PLATEAU_TOL_M


def water_z_layers(bbox_m, depth, n_grid):
    length, width, height = bbox_m
    lim = max(2.2 * length, 3.5 * width, 6.0 * depth)
    dx = lim / n_grid
    h = dx / 2.0
    floor = 3.0 * dx
    return len(np.arange(floor + 0.5 * h, floor + depth, h)), dx


def preflight():
    print(f"CONFIG {args.config}: vehicle={args.vehicle} n_grid={N_GRID} depths={DEPTHS} velocities={VELOCITIES}")
    print(f"  {len(VEHICLE_ITER)} vehicles x {len(DEPTHS)} depths x {len(VELOCITIES)} velocities "
          f"= {len(VEHICLE_ITER) * len(DEPTHS) * len(VELOCITIES)} runs")
    print(f"  outdir={OUTDIR}")
    underresolved = []
    for vclass, params_key in VEHICLE_ITER:
        bbox_m = get_vehicle(params_key)["bbox_m"]
        for depth in DEPTHS:
            layers, dx = water_z_layers(bbox_m, depth, N_GRID)
            flag = "OK" if layers >= MIN_Z_LAYERS else "UNDER-RESOLVED"
            print(f"  {vclass:7s} depth={depth:.2f}m dx={dx:.4f}m water_z_layers={layers} {flag}")
            if layers < MIN_Z_LAYERS:
                underresolved.append((vclass, depth, layers))
    if underresolved:
        print(f"WARNING: {len(underresolved)} cells have < {MIN_Z_LAYERS} water particle layers.")
        print("These seed a water slab thinner than the solver can represent.")
        for vclass, depth, layers in underresolved:
            print(f"  {vclass} depth={depth:.2f}m -> {layers} layer(s)")
        if not args.allow_underresolved:
            print("REFUSING. Re-run with --allow-underresolved to proceed anyway.")
    return not underresolved or args.allow_underresolved


if not preflight():
    sys.exit(1)
if args.dry_run:
    print("DRY RUN: preflight only, no simulation launched.", flush=True)
    sys.exit(0)

from warpmpm.vehicle import load_vehicle, FloodScene

OUTDIR.mkdir(parents=True, exist_ok=True)
manifest_path = OUTDIR / "manifest.csv"
run_index = 0
header_written = False

for vclass, params_key in VEHICLE_ITER:
    spec = get_vehicle(params_key)
    bbox_m = spec["bbox_m"]
    vehicle_mass = YARIS_MASS_KG if USE_REAL_MESH else spec["mass_kg"]
    for depth in DEPTHS:
        for velocity in VELOCITIES:
            run_id = f"veh-{vclass}_dep-{depth:.2f}_vel-{velocity:.2f}_idx-{run_index:04d}".replace(".", "p")
            print(f"START {run_id}", flush=True)
            t0 = time.time()

            if USE_REAL_MESH:
                v = load_vehicle(VEHICLE_SOURCE_PLY)
            else:
                v = fit_to_bbox(load_vehicle(VEHICLE_SOURCE_PLY), bbox_m)
            scene = FloodScene(v, depth=depth, velocity=velocity,
                               vehicle_mass=vehicle_mass, n_grid=N_GRID)

            frames_used = BASE_FRAMES
            history = scene.run(frames_used)
            plateaued_ok = has_plateaued(history)
            while not plateaued_ok and frames_used < MAX_FRAMES:
                history = scene.run(30)
                frames_used += 30
                plateaued_ok = has_plateaued(history)

            h = scene.grid.dx / 2.0
            solid_volume = v.n_particles * h ** 3
            density = vehicle_mass / solid_volume
            density_ok = 100.0 <= density <= 300.0

            d_final = np.asarray(history.displacement[-1])
            elapsed = time.time() - t0

            row = {
                "run_id": run_id,
                "vehicle_class": vclass,
                "params_class": params_key,
                "bbox_l_m": bbox_m[0],
                "bbox_w_m": bbox_m[1],
                "bbox_h_m": bbox_m[2],
                "fitted_extent_x_m": round(float(v.extent[0]), 4),
                "fitted_extent_y_m": round(float(v.extent[1]), 4),
                "fitted_extent_z_m": round(float(v.extent[2]), 4),
                "vehicle_mass_kg": vehicle_mass,
                "solid_volume_m3": round(float(solid_volume), 4),
                "vehicle_density_kgm3": round(density, 2),
                "density_plausible": density_ok,
                "depth_m": depth,
                "velocity_ms": velocity,
                "depth_velocity_m2ps": round(depth * velocity, 4),
                "n_grid": N_GRID,
                "frames_used": frames_used,
                "plateaued_ok": plateaued_ok,
                "final_disp_m": round(float(np.linalg.norm(d_final)), 4),
                "final_yaw_deg": round(float(history.yaw[-1]), 2),
                "final_roll_deg": round(float(history.roll[-1]), 2),
                "elapsed_s": round(elapsed, 1),
            }
            mode = "a" if header_written else "w"
            with open(manifest_path, mode, newline="") as mf:
                writer = csv.DictWriter(mf, fieldnames=list(row.keys()))
                if not header_written:
                    writer.writeheader()
                    header_written = True
                writer.writerow(row)
            print(row, flush=True)

            history.to_csv(OUTDIR / f"{run_id}_timeseries.csv")

            with wandb.init(mode="offline", entity="jcerrell29", project="can-it-ford",
                            name=run_id, config=row,
                            tags=[vclass, "track1-sweep", "flood-vehicle"]) as run:
                run.summary.update(row)

            run_index += 1

print(f"DONE {run_index} runs, manifest at {manifest_path}", flush=True)
