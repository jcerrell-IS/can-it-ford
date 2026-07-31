"""A flood surge hits a splat-captured vehicle; the vehicle is one rigid body.

The vehicle loads from a 3DGS splat PLY (surface splats plus interior fill make it a
solid), the water is the weakly compressible fluid, and the fork's rigid-body coupling
turns per-substep grid momentum into a body force and torque, so pushing, floating, and
overturning come out of the physics. Per frame the run records the body's displacement
from its spawn center and its yaw/pitch/roll; warpmpm.vehicle exposes the same
FloodScene and FloodHistory for scripted studies over vehicles, depths, and velocities.

Scaling. The bundled truck splat is model scale, 1.45 m long, so the default run is a
scale model, and Froude scaling (the standard for free-surface flows) converts it to a
full-size event. With length ratio lam = L_real / L_model:

  length, depth, displacement  x lam
  velocity, time               x sqrt(lam)
  mass, force                  x lam^3

For a 5.5 m pickup, lam = 3.8: the default run (28.7 kg truck, 0.15 m depth, 2.0 m/s
surge, 0.83 m washout) reads as a 1,560 kg pickup in 0.57 m of water moving at
3.9 m/s, carried 3.2 m. Reynolds number is not matched, as in any Froude model, and
the water viscosity here is inflated for stability anyway; the vehicle response is
dominated by the inertial momentum flux rho v^2 h, which Froude scaling preserves.
To skip the conversion, run at full scale directly: load_vehicle(target_length=5.5)
with --vehicle-mass 2200 and real depth and velocity (the domain, timestep, and
substep count adapt; particle count is set by the grid, not the scale).

Run:  python examples/flood_vehicle.py                      # the z-up truck splat
      python examples/flood_vehicle.py --vehicle car.ply --up -y
      python examples/flood_vehicle.py --depth 0.20 --velocity 3.0 --frames 120
      python examples/flood_vehicle.py --no-render          # metrics only

Outputs (out/flood_vehicle/):
  metrics.csv        t, dx, dy, dz, |d|, yaw, pitch, roll per frame
  flood_metrics.png  displacement and rotation vs time
  flood_vehicle.mp4  preview render: vehicle splats + water particles
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import device_cli, write_mp4
from warpmpm.vehicle import FloodScene, load_vehicle

OUT = Path(__file__).resolve().parents[1] / "out" / "flood_vehicle"
DEFAULT_PLY = Path(__file__).resolve().parents[2] / "truck_trimmed.ply"


def _render_frame(scene, colors, path, elev=22, azim=-115):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lim = scene.grid.grid_lim
    w = scene.water_positions()
    sp = scene.splat_positions()
    fig = plt.figure(figsize=(8, 5.6), facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    step = max(1, len(w) // 25000)
    ax.scatter(w[::step, 0], w[::step, 1], w[::step, 2], s=1.2, c="#4dabf7",
               alpha=0.35, linewidths=0)
    if sp is not None:
        sstep = max(1, len(sp) // 40000)
        ax.scatter(sp[::sstep, 0], sp[::sstep, 1], sp[::sstep, 2], s=1.5,
                   c=colors[::sstep], linewidths=0)
    ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.set_zlim(0, 0.35 * lim)
    ax.set_box_aspect((1, 1, 0.35))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    d = scene.history.displacement[-1]
    ax.set_title(f"t={scene.time:4.2f}s  |d|={np.linalg.norm(d)*100:5.1f}cm  "
                 f"yaw={scene.history.yaw[-1]:+5.1f}deg  roll={scene.history.roll[-1]:+5.1f}deg",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110, facecolor="white")
    plt.close(fig)


def _metrics_figure(history, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    a = history.arrays()
    d = a["displacement"]
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(11, 4))
    a0.plot(a["t"], d[:, 0] * 100, label="dx (surge)")
    a0.plot(a["t"], d[:, 1] * 100, label="dy (along vehicle)")
    a0.plot(a["t"], d[:, 2] * 100, label="dz (up)")
    a0.plot(a["t"], np.linalg.norm(d, axis=1) * 100, "k--", lw=1, label="|d|")
    a0.set_xlabel("time (s)"); a0.set_ylabel("displacement (cm)")
    a0.legend(fontsize=8); a0.grid(alpha=0.3)
    a1.plot(a["t"], a["yaw_deg"], label="yaw")
    a1.plot(a["t"], a["pitch_deg"], label="pitch")
    a1.plot(a["t"], a["roll_deg"], label="roll")
    a1.set_xlabel("time (s)"); a1.set_ylabel("rotation (deg)")
    a1.legend(fontsize=8); a1.grid(alpha=0.3)
    fig.suptitle("rigid vehicle response to flood surge", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("wrote", path)


def run(vehicle_path=DEFAULT_PLY, up="z", depth=0.12, velocity=1.5, frames=90,
        n_grid=64, vehicle_density=250.0, vehicle_mass=None, render=True,
        render_every=2, device="auto", out=None):
    outdir = Path(out) if out is not None else OUT
    outdir.mkdir(parents=True, exist_ok=True)
    v = load_vehicle(vehicle_path, up=up)
    print(f"vehicle: {v.n_particles} solid particles, extent "
          f"{np.round(v.extent, 3)} m, spacing {v.spacing*1000:.1f} mm")
    scene = FloodScene(v, depth=depth, velocity=velocity, n_grid=n_grid,
                       vehicle_density=vehicle_density, vehicle_mass=vehicle_mass,
                       device=device)
    print(f"grid {n_grid}^3 lim={scene.grid.grid_lim:.2f}m  water {scene.n_water} + "
          f"vehicle {scene.n_total - scene.n_water} particles "
          f"({scene.vehicle_mass:.1f} kg)  "
          f"dt={scene.dt:.2e} ({scene.substeps} substeps/frame)")

    tmp = outdir / "_frames"
    if render:
        tmp.mkdir(exist_ok=True)
        for o in tmp.glob("*.png"):
            o.unlink()
    colors = v.splat_colors if v.splat_colors is not None else None
    k = 0

    def cb(f, sc, state):
        nonlocal k
        d = sc.history.displacement[-1]
        if f % 10 == 0:
            print(f"frame {f:3d}  |d|={np.linalg.norm(d)*100:5.1f}cm  "
                  f"yaw={sc.history.yaw[-1]:+5.1f}  roll={sc.history.roll[-1]:+5.1f}")
        if render and f % render_every == 0:
            _render_frame(sc, colors, tmp / f"f_{k:04d}.png")
            k += 1

    history = scene.run(frames, callback=cb)
    history.to_csv(outdir / "metrics.csv")
    print("wrote", outdir / "metrics.csv")
    _metrics_figure(history, outdir / "flood_metrics.png")
    if render and k > 0:
        write_mp4(tmp, outdir / "flood_vehicle.mp4", fps=max(2, 15 // render_every))
    d = np.asarray(history.displacement[-1])
    return {"final_disp_m": d.tolist(), "final_disp_mag_m": float(np.linalg.norm(d)),
            "final_yaw_deg": history.yaw[-1], "final_roll_deg": history.roll[-1]}


if __name__ == "__main__":
    parser = device_cli(no_render=True)
    parser.add_argument("--vehicle", default=str(DEFAULT_PLY),
                        help="3DGS splat PLY or watertight mesh of the vehicle")
    parser.add_argument("--up", default="z", choices=("x", "y", "z", "-x", "-y", "-z"),
                        help="the source file's up axis")
    parser.add_argument("--depth", type=float, default=0.12, help="flood depth (m)")
    parser.add_argument("--velocity", type=float, default=1.5, help="surge speed (m/s)")
    parser.add_argument("--frames", type=int, default=90)
    parser.add_argument("--grid", type=int, default=64)
    parser.add_argument("--vehicle-density", type=float, default=250.0,
                        help="effective body density (kg/m^3); vehicles are mostly air")
    parser.add_argument("--vehicle-mass", type=float, default=None,
                        help="total body mass (kg); overrides --vehicle-density")
    parser.add_argument("--out", default=None,
                        help="output directory (default out/flood_vehicle)")
    args = parser.parse_args()
    res = run(vehicle_path=args.vehicle, up=args.up, depth=args.depth,
              velocity=args.velocity, frames=args.frames, n_grid=args.grid,
              vehicle_density=args.vehicle_density, vehicle_mass=args.vehicle_mass,
              render=not args.no_render, device=args.device, out=args.out)
    print("final:", {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                     for kk, vv in res.items()})
