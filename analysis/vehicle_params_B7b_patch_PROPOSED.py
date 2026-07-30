# PROPOSED patch for vehicle_params.py. NOT APPLIED. NOT IMPORTED BY ANYTHING.
# Rationale and the five defects this corrects: docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md
#
# Differences from the block supplied in AMENDMENT B B7b:
#   1. L1_verdict still returns str and keeps its default arg. Callers in
#      scripts/gen_scenario_sweep.py write it directly into CSV columns; a dict
#      return corrupts them silently. The dict lives in a NEW function, L1_report.
#   2. Comparison stays strict '>'. AR&R states D.V <= cap as the stability
#      equation, so exactly-at-cap is stable. '>=' flips 19 to 21 row-tests per
#      class on the live 70-row sweep and contradicts the criterion.
#   3. round(dv, 6) is retained. Dropping it flips 4 rows on binary float alone.
#   4. Old key names retained, descriptive aliases added alongside.
#   5. AR_R_SOURCE keeps the primary citation and adds the WRL reproduction.

AR_R_SOURCE = (
    "Shand, T.D., Cox, R.J., Blacka, M.J. and Smith, G.P. (2011), AR&R Revision "
    "Project 10: Appropriate Safety Criteria for Vehicles, Stage 2 Report "
    "P10/S2/020, Water Research Laboratory, UNSW. ISBN 978-0-85825-948-5, "
    "Table 3 'Proposed DRAFT Stability Criteria for Stationary Vehicles', "
    "PDF p.24 / printed p.14. Reproduced as Table 4-2 in Smith, G.P., Davey, E.K. "
    "and Cox, R. (2014), Flood Hazard, WRL Technical Report 2014/07, UNSW Water "
    "Research Laboratory; carried into ARR Book 6 (Ball et al., 2019). Values are "
    "the report's own DRAFT INTERIM figures for STATIONARY vehicles, not an "
    "endorsed safety standard."
)

AR_R_AUTHORS_STATED_LIMITATIONS = (
    "PENDING SOURCE VERIFICATION, see docs/motivation_B9b_answering_the_authors_call.md. "
    "Shand et al. (2011) are reported to state that the scaled experimental data is "
    "applied beyond its limits and that the criteria are unlikely to be reliable "
    "enough to be adopted permanently as safety criteria, citing inadequate "
    "assessment of: friction coefficients for use in flood flows; buoyancy in "
    "modern cars; the effect of vehicle orientation to flow direction including "
    "vehicle movement; and information for additional vehicle categories. This "
    "wording has NOT been checked against the report itself in-session."
)

AR_R_STABILITY_LIMITS = {
    "small_passenger": {
        "depth_m": 0.30, "velocity_ms": 3.0, "haz_m2s": 0.30,
        "still_water_depth_cap_m": 0.30, "velocity_cap_ms": 3.0, "dv_cap_m2s": 0.30,
        "high_velocity_depth_m": 0.10,
        "report_class": "Small passenger",
        "length_m_max": 4.3, "kerb_weight_kg_max": 1250, "ground_clearance_m_max": 0.12,
        "length_m": (None, 4.3), "kerb_mass_kg": (None, 1250.0),
        "ground_clearance_m": (None, 0.12),
    },
    "large_passenger": {
        "depth_m": 0.40, "velocity_ms": 3.0, "haz_m2s": 0.45,
        "still_water_depth_cap_m": 0.40, "velocity_cap_ms": 3.0, "dv_cap_m2s": 0.45,
        "high_velocity_depth_m": 0.15,
        "report_class": "Large passenger",
        "length_m_min": 4.3, "kerb_weight_kg_min": 1250, "ground_clearance_m_min": 0.12,
        "length_m": (4.3, None), "kerb_mass_kg": (1250.0, None),
        "ground_clearance_m": (0.12, None),
    },
    "large_4wd": {
        "depth_m": 0.50, "velocity_ms": 3.0, "haz_m2s": 0.60,
        "still_water_depth_cap_m": 0.50, "velocity_cap_ms": 3.0, "dv_cap_m2s": 0.60,
        "high_velocity_depth_m": 0.20,
        "report_class": "Large 4WD",
        "length_m_min": 4.5, "kerb_weight_kg_min": 2000, "ground_clearance_m_min": 0.22,
        "length_m": (4.5, None), "kerb_mass_kg": (2000.0, None),
        "ground_clearance_m": (0.22, None),
    },
}

AR_R_CLASS_ORDER = ("small_passenger", "large_passenger", "large_4wd")

MEASURED_MESH_GROUND_CLEARANCE_M = 0.1737
MEASURED_MESH_LENGTH_M = 4.2826
MEASURED_MESH_SOURCE = (
    "vehicle_geometry_research/yaris_coarse_v1l_watertight.ply, measured 2026-07-25 "
    "in the vehicle frame (floor at z=0) over the central underbody strip "
    "|x| < 0.30*halfwidth, |y| < 0.25*length, which excludes the wheels. Underbody "
    "verified as real geometry, not a watertighting cap: only 4.3 percent of strip "
    "vertices lie within 20 mm of the minimum, z std 3.86 mm."
)


def _require_class(vehicle_class):
    if vehicle_class not in AR_R_STABILITY_LIMITS:
        raise ValueError(
            f"no AR&R stability limits sourced for vehicle_class={vehicle_class!r}; "
            f"only {list(AR_R_STABILITY_LIMITS)} are populated"
        )
    return AR_R_STABILITY_LIMITS[vehicle_class]


def L1_verdict(depth_m: float, velocity_ms: float,
               vehicle_class: str = "small_passenger") -> str:
    limits = _require_class(vehicle_class)
    if depth_m > limits["depth_m"]:
        return "NO-FORD"
    if velocity_ms > limits["velocity_ms"]:
        return "NO-FORD"
    if round(depth_m * velocity_ms, 6) > limits["haz_m2s"]:
        return "NO-FORD"
    return "FORD"


def L1_report(depth_m: float, velocity_ms: float,
              vehicle_class: str = "small_passenger") -> dict:
    limits = _require_class(vehicle_class)
    d, v = float(depth_m), float(velocity_ms)
    dv = round(d * v, 6)
    binding = []
    if d > limits["depth_m"]:
        binding.append("depth_cap")
    if v > limits["velocity_ms"]:
        binding.append("velocity_cap")
    if dv > limits["haz_m2s"]:
        binding.append("dv_cap")
    return {
        "verdict": "NO-FORD" if binding else "FORD",
        "dv_m2s": dv,
        "binding_constraints": binding,
        "depth_margin_m": limits["depth_m"] - d,
        "velocity_margin_ms": limits["velocity_ms"] - v,
        "dv_margin_m2s": limits["haz_m2s"] - dv,
        "vehicle_class": vehicle_class,
        "source": AR_R_SOURCE,
    }


def _within(value, bounds):
    lo, hi = bounds
    if value is None:
        return None
    if lo is not None and value <= lo:
        return False
    if hi is not None and value >= hi:
        return False
    return True


def audit_vehicle_class(vehicle_class, length_m=None, kerb_mass_kg=None,
                        ground_clearance_m=None) -> dict:
    spec = _require_class(vehicle_class)
    checks = {
        "length_m": (length_m, spec["length_m"], _within(length_m, spec["length_m"])),
        "kerb_mass_kg": (kerb_mass_kg, spec["kerb_mass_kg"],
                         _within(kerb_mass_kg, spec["kerb_mass_kg"])),
        "ground_clearance_m": (ground_clearance_m, spec["ground_clearance_m"],
                               _within(ground_clearance_m, spec["ground_clearance_m"])),
    }
    tested = [c[2] for c in checks.values() if c[2] is not None]
    return {
        "vehicle_class": vehicle_class,
        "checks": checks,
        "n_axes_tested": len(tested),
        "n_axes_passed": sum(1 for t in tested if t),
        "fully_satisfied": len(tested) == 3 and all(tested),
        "source": AR_R_SOURCE,
    }
