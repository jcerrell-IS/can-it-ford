import numpy as np
import glob
import pandas as pd

RHO0 = 1000.0
results = []

for npz_file in sorted(glob.glob("particles_d*.npz")):
    data       = np.load(npz_file)
    pos        = data["pos"]
    vel        = data["vel"]
    depth      = float(data["depth"])
    velocity   = float(data["velocity"])
    verdict    = str(data["verdict"])
    n_particles = len(pos)

    particle_mass = RHO0 * (depth * 2.0 * 1.0) / n_particles
    masses        = np.ones(n_particles) * particle_mass
    mass_sum      = masses.sum()
    momentum      = (masses[:, None] * vel).sum(axis=0)

    expected_mass = RHO0 * depth * 2.0 * 1.0
    mass_err      = abs(mass_sum - expected_mass) / expected_mass if expected_mass > 0 else float("inf")
    mass_label    = "PASS" if mass_err < 1e-6 else f"FAIL(err={mass_err:.2e})"

    results.append({
        "file":         npz_file,
        "depth_m":      depth,
        "velocity_ms":  velocity,
        "verdict":      verdict,
        "n_particles":  n_particles,
        "mass_sum_kg":  round(mass_sum, 4),
        "mass_integrity": mass_label,
        "momentum_x":   round(float(momentum[0]), 4),
        "momentum_z":   round(float(momentum[2]), 4),
    })
    print(f"{npz_file}: n={n_particles}, mass_err={mass_err:.2e}, mass={mass_label}, mom_x={momentum[0]:.3f}, verdict={verdict}")

if results:
    df = pd.DataFrame(results)
    df.to_csv("viability_audit_results.csv", index=False)
    print(f"\nSaved {len(df)} rows to viability_audit_results.csv")
    passes = (df["mass_integrity"] == "PASS").sum()
    print(f"Mass conservation: {passes}/{len(df)} runs PASS")
else:
    print("No NPZ files found. SCP from Vista first:")
    print("  scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/particles_d*.npz .")
