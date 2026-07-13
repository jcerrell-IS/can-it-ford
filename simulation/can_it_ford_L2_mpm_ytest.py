import argparse
import csv
import os
import sys
from datetime import datetime

import genesis as gs

_pre_parser = argparse.ArgumentParser(add_help=False)
_pre_parser.add_argument('--depth', type=float, default=0.30)
_pre_parser.add_argument('--velocity', type=float, default=0.0)
_pre_args, _ = _pre_parser.parse_known_args()
water_depth    = _pre_args.depth
water_velocity = _pre_args.velocity

print(f"--- Running L2 MPM: depth={water_depth}m, velocity={water_velocity}m/s ---")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vis",    action="store_true", default=False,
                        help="Open interactive viewer window (requires display)")
    parser.add_argument("-r", "--record", action="store_true", default=False,
                        help="Save headless video of the simulation (works on Vista)")
    args, _ = parser.parse_known_args()

    gs.init(precision="32", logging_level="warning")

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=4e-3, substeps=32),
        mpm_options=gs.options.MPMOptions(
            grid_density=128,
            lower_bound=(-0.1, -1.1, -0.1),
            upper_bound=(2.1,  1.1, 2.5),
        ),
        vis_options=gs.options.VisOptions(visualize_mpm_boundary=True),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.5, -3.15, 2.42),
            camera_lookat=(1.0, 0.0, 0.5),
            camera_fov=40,
        ),
        show_viewer=args.vis,
    )

    vehicle_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.55, rho=604)

    plane   = scene.add_entity(morph=gs.morphs.Plane())

    water   = scene.add_entity(
        material=gs.materials.MPM.Liquid(),
        morph=gs.morphs.Box(
            pos=(0.275, 0.0, water_depth / 2.0),
            size=(0.35, 1.8, water_depth),
        ),
        surface=gs.surfaces.Default(color=(0.5, 0.7, 0.9, 1.0)),
    )

    vehicle = scene.add_entity(
        material=vehicle_rigid,
        morph=gs.morphs.Box(
            pos=(1.0, 0.0, 0.755),
            size=(1.0, 1.6, 1.5),
            fixed=False,
        ),
    )

    cam = None
    if args.record:
        cam = scene.add_camera(
            res=(1280, 960),
            pos=(3.5, -3.15, 2.42),
            lookat=(1.0, 0.0, 0.5),
            fov=40,
            GUI=False,
        )

    scene.build()

    water.set_velocity(gs.tensor([water_velocity, 0.0, 0.0]))

    initial_pos     = vehicle.get_pos()
    max_x_disp      = 0.0
    max_vel_mag      = 0.0
    DRIFT_THRESHOLD  = 0.05

    if cam is not None:
        cam.start_recording()

    horizon = 500 if "PYTEST_VERSION" not in os.environ else 5
    for i in range(horizon):
        scene.step()

        if water_velocity > 0.0:
            pts  = water.get_particles_pos()
            mask = pts[:, 0] < 0.14
            if mask.any():
                vel              = water.get_particles_vel()
                vel[mask, 0]     = water_velocity
                water.set_particles_vel(vel)

        if cam is not None:
            cam.render()

        current_pos = vehicle.get_pos()
        vehicle_vel = vehicle.get_vel()
        x_disp      = abs(float(current_pos[0]) - float(initial_pos[0]))
        y_disp      = abs(float(current_pos[1]) - float(initial_pos[1]))
        vel_mag     = float((vehicle_vel[0]**2 + vehicle_vel[1]**2 + vehicle_vel[2]**2)**0.5)
        max_x_disp  = max(max_x_disp, x_disp)
        max_vel_mag = max(max_vel_mag, vel_mag)

        if i % 50 == 0:
            print(f"Step {i}: x_disp={x_disp:.4f}m  vel={vehicle_vel}")

    depth_str = str(water_depth).replace(".", "p")
    vel_str   = str(water_velocity).replace(".", "p")
    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_tag   = f"d{depth_str}_v{vel_str}_grid128_cf0p55_{run_stamp}"

    if cam is not None:
        video_path = f"simulation_mpm_{run_tag}.mp4"
        cam.stop_recording(save_to_filename=video_path, fps=60)
        print(f"Saved video: {video_path}")

    final_pos = vehicle.get_pos()
    final_xd  = abs(float(final_pos[0]) - float(initial_pos[0]))
    final_yd  = abs(float(final_pos[1]) - float(initial_pos[1]))
    verdict   = "NO-FORD" if max_x_disp > DRIFT_THRESHOLD else "FORD"

    import numpy as np
    pos_final = water.get_particles_pos().cpu().numpy()
    vel_final = water.get_particles_vel().cpu().numpy()
    npz_path  = f"particles_mpm_{run_tag}.npz"
    np.savez(npz_path, pos=pos_final, vel=vel_final,
             depth=water_depth, velocity=water_velocity,
             verdict=verdict, peak_x_disp=max_x_disp, rho=604,
             coup_friction=0.55, grid_density=128, run_tag=run_tag)
    print(f"Saved particle state: {npz_path}")

    print(f"\n=== RESULT ===")
    print(f"depth={water_depth}m  velocity={water_velocity}m/s  verdict={verdict}")
    print(f"peak x_disp={max_x_disp:.4f}m  final x_disp={final_xd:.4f}m  final y_disp={final_yd:.4f}m  max_vel={max_vel_mag:.4f}m/s")
    print(f"run_tag={run_tag}")

    csv_path    = "phase_space_results_mpm.csv"
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["depth_m", "velocity_ms", "verdict", "peak_x_disp_m", "final_x_disp_m", "final_y_disp_m", "max_vel_ms", "run_tag"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "depth_m":         water_depth,
            "velocity_ms":     water_velocity,
            "verdict":         verdict,
            "peak_x_disp_m":   round(max_x_disp, 4),
            "final_x_disp_m":  round(final_xd, 4),
            "final_y_disp_m":  round(final_yd, 4),
            "max_vel_ms":      round(max_vel_mag, 4),
            "run_tag":         run_tag,
        })
    print(f"Saved to {csv_path}")


if __name__ == "__main__":
    main()
