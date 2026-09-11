import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import genesis as gs

_pre_parser = argparse.ArgumentParser(add_help=False)
_pre_parser.add_argument('--depth', type=float, default=0.30)
_pre_parser.add_argument('--velocity', type=float, default=0.0)
_pre_parser.add_argument('--grid-density', type=int, default=128)
_pre_parser.add_argument('--log-every', type=int, default=25)
_pre_args, _ = _pre_parser.parse_known_args()
water_depth    = _pre_args.depth
water_velocity = _pre_args.velocity
grid_density   = _pre_args.grid_density
log_every      = _pre_args.log_every

DT                    = 4e-3
SUBSTEPS              = 32
LOWER_BOUND           = (-2.5, -1.0, -0.1)
UPPER_BOUND           = (4.5,  1.0,  2.5)
VEHICLE_POS           = (1.0, 0.0, 0.755)
VEHICLE_SIZE          = (4.66, 1.79, 1.44)
VEHICLE_RHO           = 115.7
VEHICLE_COUP_FRICTION = 0.55
INFLOW_X              = 0.14
GRAVITY_Z             = 9.81
OUTDIR                = Path("data/track2_sweep")

print(f"--- Running L2 MPM: depth={water_depth}m, velocity={water_velocity}m/s, grid_density={grid_density} ---")

import numpy as np


def to_np(x):
    if hasattr(x, "detach"):
        x = x.detach()
    if hasattr(x, "cpu"):
        x = x.cpu()
    if hasattr(x, "numpy"):
        x = x.numpy()
    return np.asarray(x)


def debatch(a, n_particles):
    a = to_np(a)
    if a.ndim >= 1 and a.shape[0] != n_particles:
        a = a[0]
    return a


def sample_fields(water, vehicle, m_p, step):
    state = water.get_state()
    n     = int(water.n_particles)

    pos    = debatch(state.pos, n)
    vel    = debatch(state.vel, n)
    F      = debatch(state.F, n)
    active = debatch(state.active, n)

    try:
        water._queried_states.clear()
    except Exception:
        pass

    J = np.linalg.det(F)

    momentum = m_p * vel.sum(axis=0)
    ke       = 0.5 * m_p * float((vel * vel).sum())
    pe       = m_p * GRAVITY_Z * float((pos[:, 2] - LOWER_BOUND[2]).sum())

    lo_dom = np.asarray(LOWER_BOUND)
    hi_dom = np.asarray(UPPER_BOUND)
    in_dom = np.all((pos >= lo_dom) & (pos <= hi_dom), axis=1)

    centre = to_np(vehicle.get_pos()).ravel()[:3]
    half   = np.asarray(VEHICLE_SIZE) / 2.0
    lo_veh = centre - half
    hi_veh = centre + half
    inside = np.all((pos > lo_veh) & (pos < hi_veh), axis=1)
    n_pen  = int(inside.sum())
    if n_pen > 0:
        depths  = np.minimum(pos[inside] - lo_veh, hi_veh - pos[inside]).min(axis=1)
        pen_max = float(depths.max())
    else:
        pen_max = 0.0

    return {
        "t":                 round(step * DT, 6),
        "step":              step,
        "water_px":          float(momentum[0]),
        "water_py":          float(momentum[1]),
        "water_pz":          float(momentum[2]),
        "water_ke_J":        ke,
        "water_pe_J":        pe,
        "J_min":             float(J.min()),
        "J_max":             float(J.max()),
        "J_mean":            float(J.mean()),
        "n_active":          int(np.count_nonzero(active)),
        "n_in_domain":       int(np.count_nonzero(in_dom)),
        "n_penetrating":     n_pen,
        "penetration_max_m": pen_max,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vis",    action="store_true", default=False,
                        help="Open interactive viewer window (requires display)")
    parser.add_argument("-r", "--record", action="store_true", default=False,
                        help="Save headless video of the simulation (works on Vista)")
    args, _ = parser.parse_known_args()

    gs.init(precision="32", logging_level="warning")

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=DT, substeps=SUBSTEPS),
        mpm_options=gs.options.MPMOptions(
            grid_density=grid_density,
            lower_bound=LOWER_BOUND,
            upper_bound=UPPER_BOUND,
        ),
        vis_options=gs.options.VisOptions(visualize_mpm_boundary=True),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.5, -3.15, 2.42),
            camera_lookat=(1.0, 0.0, 0.5),
            camera_fov=40,
        ),
        show_viewer=args.vis,
        renderer=gs.renderers.RayTracer(),
    )

    vehicle_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=VEHICLE_COUP_FRICTION, rho=VEHICLE_RHO)

    measured_rho  = float(vehicle_rigid.rho)
    measured_cf   = float(vehicle_rigid.coup_friction)

    plane   = scene.add_entity(
        morph=gs.morphs.Plane(),
        surface=gs.surfaces.Rough(color=(0.35, 0.33, 0.30), roughness=0.85),
    )

    water   = scene.add_entity(
        material=gs.materials.MPM.Liquid(),
        morph=gs.morphs.Box(
            pos=(-1.8, 0.0, water_depth / 2.0),
            size=(0.35, 1.8, water_depth),
        ),
        surface=gs.surfaces.Water(),
    )

    vehicle = scene.add_entity(
        material=vehicle_rigid,
        morph=gs.morphs.Box(
            pos=VEHICLE_POS,
            size=VEHICLE_SIZE,
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

    n_particles     = int(water.n_particles)
    total_mass      = float(to_np(water.get_mass()).ravel()[0])
    m_p             = total_mass / n_particles

    print(f"Water: n_particles={n_particles}, total_mass={total_mass:.4f}kg, m_p={m_p:.6e}kg")

    initial_pos     = vehicle.get_pos()
    max_x_disp      = 0.0
    max_vel_mag      = 0.0
    DRIFT_THRESHOLD  = 0.05

    kinematics_rows = []
    field_rows      = []

    if cam is not None:
        cam.start_recording()

    horizon = 500 if "PYTEST_VERSION" not in os.environ else 5
    for i in range(horizon):
        scene.step()

        inflow_dpx = 0.0
        if water_velocity > 0.0:
            pts  = water.get_particles_pos()
            mask = pts[:, 0] < INFLOW_X
            if mask.any():
                vel              = water.get_particles_vel()
                prev_x           = to_np(vel[mask, 0])
                inflow_dpx       = m_p * float((water_velocity - prev_x).sum())
                vel[mask, 0]     = water_velocity
                water.set_particles_vel(vel)

        if cam is not None:
            cam.render()

        current_pos = vehicle.get_pos()
        vehicle_vel = vehicle.get_vel()
        dx          = float(current_pos[0]) - float(initial_pos[0])
        dy          = float(current_pos[1]) - float(initial_pos[1])
        dz          = float(current_pos[2]) - float(initial_pos[2])
        dmag        = (dx * dx + dy * dy + dz * dz) ** 0.5
        x_disp      = abs(dx)
        vel_mag     = float((vehicle_vel[0]**2 + vehicle_vel[1]**2 + vehicle_vel[2]**2)**0.5)
        max_x_disp  = max(max_x_disp, x_disp)
        max_vel_mag = max(max_vel_mag, vel_mag)

        kinematics_rows.append({
            "t":          round(i * DT, 6),
            "dx":         dx,
            "dy":         dy,
            "dz":         dz,
            "dmag":       dmag,
            "veh_vx":     float(vehicle_vel[0]),
            "veh_vy":     float(vehicle_vel[1]),
            "veh_vz":     float(vehicle_vel[2]),
            "inflow_dpx": inflow_dpx,
        })

        if i % log_every == 0 or i == horizon - 1:
            field_rows.append(sample_fields(water, vehicle, m_p, i))

        if i % 50 == 0:
            print(f"Step {i}: x_disp={x_disp:.4f}m  vel={vehicle_vel}")

    depth_str = str(water_depth).replace(".", "p")
    vel_str   = str(water_velocity).replace(".", "p")
    cf_str    = str(measured_cf).replace(".", "p")
    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_tag   = f"d{depth_str}_v{vel_str}_grid{grid_density}_cf{cf_str}_{run_stamp}"

    if cam is not None:
        video_path = f"simulation_mpm_{run_tag}.mp4"
        cam.stop_recording(save_to_filename=video_path, fps=60)
        print(f"Saved video: {video_path}")

    final_pos = vehicle.get_pos()
    final_xd  = abs(float(final_pos[0]) - float(initial_pos[0]))
    final_yd  = abs(float(final_pos[1]) - float(initial_pos[1]))
    verdict   = "NO-FORD" if max_x_disp > DRIFT_THRESHOLD else "FORD"

    pos_final = to_np(water.get_particles_pos())
    vel_final = to_np(water.get_particles_vel())
    npz_path  = f"particles_mpm_{run_tag}.npz"
    np.savez(npz_path, pos=pos_final, vel=vel_final,
             depth=water_depth, velocity=water_velocity,
             verdict=verdict, peak_x_disp=max_x_disp, rho=measured_rho,
             coup_friction=measured_cf, grid_density=grid_density,
             n_particles=n_particles, total_mass_kg=total_mass,
             particle_mass_kg=m_p, dx_cell=1.0 / grid_density,
             lower_bound=np.asarray(LOWER_BOUND), upper_bound=np.asarray(UPPER_BOUND),
             dt=DT, substeps=SUBSTEPS, horizon=horizon, run_tag=run_tag)
    print(f"Saved particle state: {npz_path}")

    OUTDIR.mkdir(parents=True, exist_ok=True)

    kin_path = OUTDIR / f"{run_tag}_timeseries.csv"
    with open(kin_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(kinematics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(kinematics_rows)
    print(f"Saved kinematics timeseries: {kin_path} ({len(kinematics_rows)} rows)")

    fld_path = OUTDIR / f"{run_tag}_fields.csv"
    with open(fld_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(field_rows[0].keys()))
        writer.writeheader()
        writer.writerows(field_rows)
    print(f"Saved field timeseries: {fld_path} ({len(field_rows)} rows)")

    manifest_path   = OUTDIR / "manifest.csv"
    manifest_exists = manifest_path.is_file()
    with open(manifest_path, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["run_tag", "grid_density", "dx_cell", "n_particles", "depth_m",
                        "velocity_ms", "peak_x_disp_m", "verdict", "rho", "coup_friction",
                        "total_mass_kg", "dt", "substeps", "horizon"]
        )
        if not manifest_exists:
            writer.writeheader()
        writer.writerow({
            "run_tag":       run_tag,
            "grid_density":  grid_density,
            "dx_cell":       1.0 / grid_density,
            "n_particles":   n_particles,
            "depth_m":       water_depth,
            "velocity_ms":   water_velocity,
            "peak_x_disp_m": max_x_disp,
            "verdict":       verdict,
            "rho":           measured_rho,
            "coup_friction": measured_cf,
            "total_mass_kg": total_mass,
            "dt":            DT,
            "substeps":      SUBSTEPS,
            "horizon":       horizon,
        })
    print(f"Appended GCI manifest row: {manifest_path}")

    print(f"\n=== RESULT ===")
    print(f"depth={water_depth}m  velocity={water_velocity}m/s  verdict={verdict}")
    print(f"peak x_disp={max_x_disp:.4f}m  final x_disp={final_xd:.4f}m  final y_disp={final_yd:.4f}m  max_vel={max_vel_mag:.4f}m/s")
    print(f"run_tag={run_tag}")

    csv_path    = "data/phase_space_results_mpm.csv"
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
