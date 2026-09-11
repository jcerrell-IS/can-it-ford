from pathlib import Path
import numpy as np
from warpmpm.vehicle import load_vehicle, FloodScene

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"
OUTDIR = Path("/work/11603/jcerrell0629/vista/can-it-ford/data/track1_fullscale")
OUTDIR.mkdir(parents=True, exist_ok=True)

v = load_vehicle(VEHICLE_PLY, target_length=5.5)
print(f"vehicle extent: {v.extent} m")

scene = FloodScene(v, depth=0.30, velocity=1.5, vehicle_mass=1930)
print(f"vehicle mass: {scene.vehicle_mass:.1f} kg  grid lim: {scene.grid.grid_lim:.2f} m")

history = scene.run(90)
history.to_csv(OUTDIR / "metrics_fullscale_single.csv")

d = np.asarray(history.displacement[-1])
print(f"final displacement: {d}  magnitude: {np.linalg.norm(d):.3f} m")
print(f"final yaw: {history.yaw[-1]:.2f} deg  roll: {history.roll[-1]:.2f} deg")
