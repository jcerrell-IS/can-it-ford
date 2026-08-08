import math
import re

LITERATURE_GATES = {
    "mass_inertia_cog": "Brannon Kamojjala Sadeghirad 2011; Allen Klyde Rosenthal Smith 2003 SAE 2003-01-0966",
    "geometry_bbox": "Kamojjala Brannon Sadeghirad Guilkey 2013 doi:10.1007/s00366-013-0342-x",
    "sound_speed_cfl": "Ni Zhang 2020 doi:10.1002/nme.6506; Bai Schroeder 2022 doi:10.1111/cgf.14620; Sun Shinar Schroeder 2020 doi:10.1111/cgf.14101; Isik He 2022 doi:10.1007/s40571-022-00511-8",
    "energy_conservation": "Bardenhagen 2002 doi:10.1006/JCPH.2002.7103",
    "resolution_convergence_gci": "Roache 1994 doi:10.1115/1.2910291; Celik Ghia Roache Freitas 2007 doi:10.1115/1.2960953",
    "manifest_provenance": "Huber et al 2020 doi:10.1038/s41597-020-00638-4; Dhruv Dubey Barba Gesing 2023 doi:10.1109/MCSE.2023.3314288",
}

def gate_mass_declared(vehicle_mass, known_masses=(1100, 1609, 2337)):
    if round(vehicle_mass) not in known_masses:
        return False, "vehicle_mass %s not in AR&R class set %s, confirm override is intentional" % (vehicle_mass, known_masses)
    return True, "mass %s kg matches declared AR&R class" % vehicle_mass

def gate_inertia_not_read_by_solver(solver_source_text):
    forbidden = ["inertia_tensor", "cg_height", "vehicle_params.inertia", "vehicle_params.cg"]
    hits = [f for f in forbidden if f in solver_source_text]
    if hits:
        return False, "solver now references %s, inertia and CoG previously never reached the solver, confirm this is an intentional change" % hits
    return True, "solver still reads mass only, inertia and CoG correctly excluded per known finding"

def gate_hull_volume(measured_volume_m3, expected_volume_m3=3.542739, tol=0.002):
    delta = abs(measured_volume_m3 - expected_volume_m3)
    if delta > tol:
        return False, "hull volume %.6f m3 differs from canonical %.6f m3 by %.6f, check solidify_watertight ran" % (measured_volume_m3, expected_volume_m3, delta)
    return True, "hull volume matches canonical fixed value within tolerance"

def gate_floor_restitution(sim_source_text):
    matches = re.findall(r"add_plane\([^)]*restitution\s*=\s*([0-9.]+)", sim_source_text)
    if not matches:
        return False, "no add_plane restitution argument found, cannot confirm floor_friction is registering as contact, resolve open item 31 before trusting SLIDE verdicts"
    if all(float(m) == 0.0 for m in matches):
        return False, "all floor restitution values are 0.0, floor_friction may be functionally inert per mpm_solver_warp.py:1915 gate"
    return True, "floor restitution %s confirms floor_friction registers as rigid contact" % matches

def gate_sound_speed_cfl(bulk_modulus, gamma, rho0, v_max):
    c = math.sqrt(bulk_modulus * gamma / rho0)
    ratio = c / v_max if v_max else float("inf")
    if ratio < 10.0:
        return False, "sound speed %.4f m/s is only %.2fx v_max, below Monaghan 10x convention, outcome may be sound-speed sensitive per Isik and He 2022 and Bai and Schroeder 2022" % (c, ratio)
    return True, "sound speed %.4f m/s is %.2fx v_max, meets Monaghan 10x convention" % (c, ratio)

def gate_resolution_convergence_gci(grid_densities, displacements, safety_factor=1.25):
    if len(grid_densities) < 3 or len(displacements) < 3:
        return False, "need at least three grid resolutions for a GCI estimate, have %d" % len(grid_densities)
    pairs = sorted(zip(grid_densities, displacements))
    g1, f1 = pairs[-1]
    g2, f2 = pairs[-2]
    g3, f3 = pairs[-3]
    h1, h2, h3 = 1.0 / g1, 1.0 / g2, 1.0 / g3
    r21 = h2 / h1
    r32 = h3 / h2
    eps21 = f2 - f1
    eps32 = f3 - f2
    if eps21 == 0:
        return True, "displacement identical between the two finest grids, fully converged at %s" % g1
    if eps32 == 0 or abs(r21 - r32) > 1e-6:
        return False, "grid refinement ratio is not constant or eps32 is zero, cannot compute apparent order p, report the raw non-monotone spread instead of a GCI band"
    ratio = eps32 / eps21
    if ratio <= 0:
        return False, "displacement is non-monotone across the finest three grids (f1=%.6f f2=%.6f f3=%.6f), verdict may still be grid-invariant but no GCI band can be computed, cite Roache 1994 and report non-monotonicity explicitly rather than a point estimate" % (f1, f2, f3)
    p = math.log(ratio) / math.log(r21)
    gci21 = safety_factor * abs(eps21 / f1) / (r21 ** p - 1)
    return True, "apparent order p=%.3f, GCI_fine=%.4f percent, cite Celik et al 2007 ASME for reporting convention" % (p, gci21 * 100)

def gate_manifest_completeness(summary_json, required_fields=("vehicle_mass", "mesh_sha256", "grid_density", "bulk_modulus", "solver_git_sha", "canitford_git_commit")):
    missing = [f for f in required_fields if f not in summary_json]
    if missing:
        return False, "summary.json missing %s, run cannot be traced back to code plus data plus environment" % missing
    return True, "manifest complete, run is fully traceable"

def gate_output_sensitivity(baseline_value, perturbed_value, param_name, tol=1e-9):
    if abs(perturbed_value - baseline_value) < tol:
        return False, "%s changed but output did not move at all, output may not actually depend on this input, this is the comprehension-generation gap pattern per Song et al 2026 doi:10.48550/arXiv.2605.09360" % param_name
    return True, "%s changed and output moved by %.6g, output is sensitive to this input" % (param_name, perturbed_value - baseline_value)

LITERATURE_GATES["output_sensitivity"] = "Song et al 2026 doi:10.48550/arXiv.2605.09360, PDE-grounded intent verification"
