from pathlib import Path
import csv
import time
import numpy as np
import wandb
from warpmpm.vehicle import load_vehicle, FloodScene

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"
OUTDIR = Path("/work/11603/jcerrell0629/vista/can-it-ford/data/track1_sweep_v1")
OUTDIR.mkdir(parents=True, exist_ok=True)

VEHICLE_CLASSES = {
    "sedan": {"target_length": 4.6, "vehicle_mass": 1240.0},
    "suv": {"target_length": 4.8, "vehicle_mass": 2020.0},
    "pickup": {"target_length": 5.5, "vehicle_mass": 1930.0},
}

DEPTHS = [0.15, 0.30, 0.45, 0.60]
VELOCITIES = [1.0, 1.5, 2.0]
N_GRID = 64
BASE_FRAMES = 90
MAX_FRAMES = 150
PLATEAU_WINDOW = 10
PLATEAU_TOL_M = 0.01

def has_plateaued(history):
    d = np.asarray(history.displacement)
    if len(d) < PLATEAU_WINDOW + 1:
        return False
    mag = np.linalg.norm(d, axis=1)
    recent = mag[-PLATEAU_WINDOW:]
    return float(recent.max() - recent.min()) < PLATEAU_TOL_M

manifest_path = OUTDIR / "manifest.csv"
run_index = 0
header_written = False

for vclass, vparams in VEHICLE_CLASSES.items():
    for depth in DEPTHS:
        for velocity in VELOCITIES:
            run_id = f"veh-{vclass}_dep-{depth:.2f}_vel-{velocity:.2f}_idx-{run_index:04d}".replace(".", "p")
            print(f"START {run_id}", flush=True)
            t0 = time.time()

            v = load_vehicle(VEHICLE_PLY, target_length=vparams["target_length"])
            scene = FloodScene(v, depth=depth, velocity=velocity,
                               vehicle_mass=vparams["vehicle_mass"], n_grid=N_GRID)

            frames_used = BASE_FRAMES
            history = scene.run(frames_used)
            plateaued_ok = has_plateaued(history)
            while not plateaued_ok and frames_used < MAX_FRAMES:
                history = scene.run(30)
                frames_used += 30
                plateaued_ok = has_plateaued(history)

            h = scene.grid.dx / 2.0
            solid_volume = v.n_particles * h ** 3
            density = vparams["vehicle_mass"] / solid_volume
            density_ok = 100.0 <= density <= 300.0

            d_final = np.asarray(history.displacement[-1])
            elapsed = time.time() - t0

            row = {
                "run_id": run_id,
                "vehicle_class": vclass,
                "target_length_m": vparams["target_length"],
                "vehicle_mass_kg": vparams["vehicle_mass"],
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
