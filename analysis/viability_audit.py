import numpy as np
import glob
import pandas as pd

RHO0 = 1000.0
WATER_BOX_X = 0.35
WATER_BOX_Y = 1.8
results = []

for npz_file in sorted(glob.glob("particles_*.npz")):
    data       = np.load(npz_file)
    pos        = data["pos"]
    vel        = data["vel"]
    depth      = float(data["depth"])
    velocity   = float(data["velocity"])
    verdict    = str(data["verdict"])
    n_particles = len(pos)

    if "particle_mass_kg" in data.files:
        particle_mass = float(data["particle_mass_kg"])
        mass_source   = "solver"
    else:
        particle_mass = RHO0 * (WATER_BOX_X * WATER_BOX_Y * depth) / n_particles
        mass_source   = "box-geometry"

    momentum = particle_mass * vel.sum(axis=0)

    results.append({
        "file":         npz_file,
        "depth_m":      depth,
        "velocity_ms":  velocity,
        "verdict":      verdict,
        "n_particles":  n_particles,
        "particle_mass_kg": particle_mass,
        "mass_source":  mass_source,
        "momentum_x":   round(float(momentum[0]), 4),
        "momentum_z":   round(float(momentum[2]), 4),
    })
    print(f"{npz_file}: n={n_particles}, m_p={particle_mass:.3e}kg ({mass_source}), mom_x={momentum[0]:.3f}, verdict={verdict}")

if results:
    df = pd.DataFrame(results)
    df.to_csv("viability_audit_results.csv", index=False)
    print(f"\nSaved {len(df)} rows to viability_audit_results.csv")
    print("NOTE: mass-conservation reporting withdrawn July 15, 2026 as tautological.")
    print("      See docs/viability_audit_mass_retraction.md")
else:
    print("No NPZ files found. SCP from Vista first:")
    print("  scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/particles_d*.npz .")
