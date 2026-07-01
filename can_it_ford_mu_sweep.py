import csv
import os
import sys

import genesis as gs

water_depth    = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
water_velocity = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
coup_friction  = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

print(f"--- mu_sweep: depth={water_depth}m  vel={water_velocity}m/s  mu={coup_friction} ---")


def main():
    gs.init(precision="32", logging_level="warning")

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=1e-2, substeps=10),
        sph_options=gs.options.SPHOptions(
            lower_bound=(0.0, -1.0, 0.0),
            upper_bound=(2.0, 1.0, 2.4),
        ),
        vis_options=gs.options.VisOptions(visualize_sph_boundary=True),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.5, -3.15, 2.42),
            camera_lookat=(1.0, 0.0, 0.5),
            camera_fov=40,
        ),
        show_viewer=False,
    )

    vehicle_material = gs.materials.Rigid(needs_coup=True, coup_friction=coup_friction)

    plane = scene.add_entity(morph=gs.morphs.Plane())

    water = scene.add_entity(
        material=gs.materials.SPH.Liquid(mu=0.01, sampler="regular"),
        morph=gs.morphs.Box(
            pos=(1.0, 0.0, water_depth / 2.0),
            size=(1.8, 1.8, water_depth),
        ),
        surface=gs.surfaces.Default(color=(0.5, 0.7, 0.9, 1.0)),
    )

    vehicle = scene.add_entity(
        material=vehicle_material,
        morph=gs.morphs.Box(
            pos=(1.0, 0.0, water_depth + 0.075),
            size=(0.4, 0.2, 0.15),
            fixed=False,
        ),
    )

    scene.build()

    water.set_velocity(gs.tensor([water_velocity, 0.0, 0.0]))

    initial_pos  = vehicle.get_pos()
    max_x_disp   = 0.0
    DRIFT_THRESHOLD = 0.05

    horizon = 500
    for i in range(horizon):
        scene.step()

        if water_velocity > 0.0:
            pts = water.get_particles_pos()
            mask = pts[:, 0] < 0.3
            if mask.any():
                vel = water.get_particles_vel()
                vel[mask, 0] = water_velocity
                water.set_particles_vel(vel)

        current_pos = vehicle.get_pos()
        x_disp = abs(float(current_pos[0]) - float(initial_pos[0]))
        max_x_disp = max(max_x_disp, x_disp)

        if i % 50 == 0:
            print(f"  step {i}: x_disp={x_disp:.4f}m  max_so_far={max_x_disp:.4f}m")

    verdict = "NO-FORD" if max_x_disp > DRIFT_THRESHOLD else "FORD"

    print(f"\n=== RESULT: mu={coup_friction}  max_x_disp={max_x_disp:.4f}m  verdict={verdict} ===")

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mu_sweep_results.csv")
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["depth_m", "velocity_ms", "coup_friction", "max_x_disp_m", "verdict"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "depth_m":       water_depth,
            "velocity_ms":   water_velocity,
            "coup_friction": coup_friction,
            "max_x_disp_m":  round(max_x_disp, 4),
            "verdict":       verdict,
        })
    print(f"Saved to {csv_path}")


if __name__ == "__main__":
    main()
