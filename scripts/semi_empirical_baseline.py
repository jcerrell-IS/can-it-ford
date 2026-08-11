from __future__ import annotations

import csv
import math
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_CSV = os.path.join(REPO_ROOT, "data", "scenario_sweep.csv")
OUT_CSV = os.path.join(REPO_ROOT, "data", "semi_empirical_baseline_2026-08-08.csv")

RHO_WATER = 1000.0
G = 9.81

VEHICLE_CLASS = "compact_sedan"
MASS_KG = 1100.0
HULL_VOLUME_M3 = 3.542739
HULL_LENGTH_M = 4.2826
HULL_WIDTH_M = 1.7464
HULL_HEIGHT_M = 1.5180

MU_FLOOR = 0.55

CD_LOW = 1.22
CD_HIGH = 6.82
CD_POINT = 0.5 * (CD_LOW + CD_HIGH)
CD_MEASURED_IN_REPO = 1.38

VELOCITY_CAP_MS = 3.0

PROVENANCE = {
    "RHO_WATER": "CLAUDE.md physical-anchor list, water 1000 kg/m^3",
    "G": (
        "CLAUDE.md AUGUST 4 2026 AUDIT item 3: solver hardcodes g=[0,0,-9.81] at "
        "third_party/mpm-engine-544c93dd-solver-core/core/solver.py:167-169; all 17 "
        "gated runs ran at exactly 9.81 m/s^2"
    ),
    "MASS_KG": "vehicle_params.py:125 VEHICLE_PARAMS['compact_sedan']['mass_kg'] = 1100.0",
    "HULL_VOLUME_M3": (
        "vehicle_geometry_research/failed_reconstructions_2026-07-25/README.md:17, "
        "canonical watertight mesh yaris_coarse_v1l_watertight.ply, volume 3.542739 m^3; "
        "corroborated at renders/yaris_render_s1/g0_validate.py:12 and every "
        "renders/yaris_render_s1/*/summary.json hull_m3 field"
    ),
    "HULL_EXTENTS_M": (
        "same README.md:17 row as the volume, measured extents 4.2826 x 1.7464 x 1.5180 m; "
        "taken from the mesh rather than vehicle_params.py bbox_m (4.30, 1.70, 1.47) so that "
        "the volume and the extents come from one source line"
    ),
    "MU_FLOOR": (
        "renders/yaris_render_s1/sim_standing.py:84 and :235, floor_friction=0.55, the value "
        "used across all 17 canonical runs"
    ),
    "CD_LOW/CD_HIGH": (
        "UNVERIFIED. Prescribed as 1.22 to 6.82 from a Journal of Hydrology 2023 flume study "
        "(PII S0022169423004675) cited in docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md "
        "section 2.2. That file does not exist on disk and has never existed in git history "
        "(git log --all returns empty). Neither 6.82 nor the PII appears anywhere in the repo. "
        "No primary source was reachable for these bounds. See "
        "docs/semi_empirical_baseline_findings.md"
    ),
    "CD_MEASURED_IN_REPO": (
        "docs/LIT_QUEUE_2026-07-30.md:59-60, average drag coefficient C_D = 1.38, directly "
        "measured, from the Smith, Modra and Felder full-scale traction study abstracted at "
        "docs/Dynamic_Vehicle_Traction_in_Floodwater.md. Reported here as a sourced comparator "
        "against the unsourced 1.22 to 6.82 band. NOT used for the delivered CSV"
    ),
    "REFERENCE_AREA": (
        "A_frontal(d) = HULL_WIDTH_M * min(d, HULL_HEIGHT_M), the submerged frontal projected "
        "rectangle. This is a convention choice, not a measurement. Because the C_D source "
        "could not be located, the reference area its C_D values were normalised against is "
        "also unverified"
    ),
    "SUBMERGED_FRACTION": (
        "f(d) = min(d, HULL_HEIGHT_M) / HULL_HEIGHT_M, a prismatic approximation. The hull is "
        "not prismatic: it fills 31.2 percent of its own bounding box. This is the dominant "
        "geometric approximation in the model"
    ),
    "FORMULA_PATH": (
        "FIRST-PRINCIPLES FALLBACK. Xia, Falconer, Xiao and Wang 2014 (Natural Hazards 70:1619-1630, "
        "doi 10.1007/s11069-013-0889-2) and Shu, Xia, Falconer and Lin 2011 (J. Hydraulic Research "
        "49:709-717, doi 10.1080/00221686.2011.616318) both resolved on Scite as closed access, "
        "oaStatus 'closed', contentDenied true, zero full-text excerpts, purchase-only. The "
        "published incipient-velocity formulae, including the 2014 ground-slope term, were NOT "
        "retrieved and are NOT implemented here. No reconstruction from citing papers was attempted"
    ),
}


def submerged_fraction(depth_m: float) -> float:
    return min(depth_m, HULL_HEIGHT_M) / HULL_HEIGHT_M


def submerged_volume_m3(depth_m: float) -> float:
    return HULL_VOLUME_M3 * submerged_fraction(depth_m)


def buoyant_force_n(depth_m: float) -> float:
    return RHO_WATER * G * submerged_volume_m3(depth_m)


def normal_force_n(depth_m: float, mass_kg: float = MASS_KG) -> float:
    return max(0.0, mass_kg * G - buoyant_force_n(depth_m))


def friction_force_n(depth_m: float, mass_kg: float = MASS_KG, mu: float = MU_FLOOR) -> float:
    return mu * normal_force_n(depth_m, mass_kg)


def frontal_area_m2(depth_m: float) -> float:
    return HULL_WIDTH_M * min(depth_m, HULL_HEIGHT_M)


def drag_force_n(depth_m: float, velocity_ms: float, cd: float = CD_POINT) -> float:
    return 0.5 * RHO_WATER * cd * frontal_area_m2(depth_m) * velocity_ms * velocity_ms


def incipient_velocity_ms(
    depth_m: float,
    mass_kg: float = MASS_KG,
    mu: float = MU_FLOOR,
    cd: float = CD_POINT,
) -> float:
    area = frontal_area_m2(depth_m)
    if area <= 0.0:
        return float("inf")
    resisting = friction_force_n(depth_m, mass_kg, mu)
    if resisting <= 0.0:
        return 0.0
    return math.sqrt(2.0 * resisting / (RHO_WATER * cd * area))


def flotation_depth_m(mass_kg: float = MASS_KG) -> float:
    displaced = mass_kg / RHO_WATER
    if displaced >= HULL_VOLUME_M3:
        return float("inf")
    return HULL_HEIGHT_M * displaced / HULL_VOLUME_M3


def semi_empirical_verdict(depth_m: float, velocity_ms: float, **kw) -> str:
    v_c = incipient_velocity_ms(depth_m, **kw)
    return "NO-FORD" if velocity_ms >= v_c else "FORD"


def read_sweep(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def build_rows(sweep: list[dict], cd: float = CD_POINT, mass_kg: float = MASS_KG) -> list[dict]:
    rows = []
    for r in sweep:
        depth = float(r["depth_m"])
        vel = float(r["velocity_ms"])
        l1 = r["L1_verdict"]
        v_c = incipient_velocity_ms(depth, mass_kg=mass_kg, cd=cd)
        se = "NO-FORD" if vel >= v_c else "FORD"
        rows.append(
            {
                "depth_m": r["depth_m"],
                "velocity_ms": r["velocity_ms"],
                "L1_verdict": l1,
                "incipient_velocity_ms": f"{v_c:.6f}" if math.isfinite(v_c) else "inf",
                "semi_empirical_verdict": se,
                "agrees_with_L1": str(se == l1),
            }
        )
    return rows


def write_rows(path: str, rows: list[dict]) -> None:
    fields = [
        "depth_m",
        "velocity_ms",
        "L1_verdict",
        "incipient_velocity_ms",
        "semi_empirical_verdict",
        "agrees_with_L1",
    ]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def units_check() -> list[str]:
    out = []
    rho_vehicle = MASS_KG / HULL_VOLUME_M3
    out.append(f"effective vehicle density = {rho_vehicle:.3f} kg/m^3 (CLAUDE.md anchor 310.494)")
    out.append(f"flotation depth = {flotation_depth_m():.6f} m")
    out.append(
        "F_drag [kg/m^3 * m^2 * m^2/s^2 = kg*m/s^2 = N]; "
        "F_fric [N]; V_c = sqrt(2*mu*N / (rho*Cd*A)) [sqrt(m^2/s^2) = m/s]"
    )
    d_float = flotation_depth_m()
    out.append(
        f"consistency: submerged_volume(d_float) = {submerged_volume_m3(d_float):.6f} m^3 "
        f"vs mass/rho_water = {MASS_KG / RHO_WATER:.6f} m^3"
    )
    out.append(
        f"consistency: buoyant_force(d_float) = {buoyant_force_n(d_float):.3f} N "
        f"vs weight = {MASS_KG * G:.3f} N"
    )
    out.append(f"hull bbox fill fraction = {HULL_VOLUME_M3 / (HULL_LENGTH_M * HULL_WIDTH_M * HULL_HEIGHT_M):.4f}")
    return out


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    agree = sum(1 for r in rows if r["agrees_with_L1"] == "True")
    disagree = [r for r in rows if r["agrees_with_L1"] != "True"]
    return {
        "n": n,
        "agree": agree,
        "rate": agree / n if n else 0.0,
        "disagreements": disagree,
        "se_ford": sum(1 for r in rows if r["semi_empirical_verdict"] == "FORD"),
        "l1_ford": sum(1 for r in rows if r["L1_verdict"] == "FORD"),
    }


def main() -> int:
    sweep = read_sweep(SWEEP_CSV)
    rows = build_rows(sweep)
    write_rows(OUT_CSV, rows)

    print("PROVENANCE")
    for k, v in PROVENANCE.items():
        print(f"  {k}: {v}")
    print()

    print("UNITS AND CONSISTENCY")
    for line in units_check():
        print(f"  {line}")
    print()

    print(f"CD_LOW={CD_LOW}  CD_POINT={CD_POINT}  CD_HIGH={CD_HIGH}")
    print(f"MU={MU_FLOOR}  MASS={MASS_KG} kg  V_HULL={HULL_VOLUME_M3} m^3")
    print()

    print("INCIPIENT VELOCITY BY DEPTH (m/s), columns are Cd=1.22 / Cd=4.02 / Cd=6.82")
    print("  (higher Cd means more drag, so a LOWER incipient velocity)")
    depths = sorted({float(r["depth_m"]) for r in sweep})
    for d in depths:
        at_cd_low = incipient_velocity_ms(d, cd=CD_LOW)
        at_cd_point = incipient_velocity_ms(d, cd=CD_POINT)
        at_cd_high = incipient_velocity_ms(d, cd=CD_HIGH)
        flag = "  <- point estimate exceeds 3.0 m/s sweep cap" if at_cd_point > VELOCITY_CAP_MS else ""
        print(f"  d={d:.1f}  {at_cd_low:8.4f}  {at_cd_point:8.4f}  {at_cd_high:8.4f}{flag}")
    print()

    s = summarise(rows)
    print(f"ROWS={s['n']}  AGREE={s['agree']}  RATE={100.0 * s['rate']:.2f}%")
    print(f"semi-empirical FORD={s['se_ford']}  L1 FORD={s['l1_ford']}")
    print()
    print("DISAGREEMENTS")
    for r in s["disagreements"]:
        print(
            f"  depth={r['depth_m']} m  velocity={r['velocity_ms']} m/s  "
            f"L1={r['L1_verdict']}  semi_empirical={r['semi_empirical_verdict']}  "
            f"V_c={r['incipient_velocity_ms']}"
        )
    print()

    print("SENSITIVITY, agreement rate against L1")
    for label, cd in (
        ("Cd low 1.22 (unsourced)", CD_LOW),
        ("Cd mid 4.02 (unsourced)", CD_POINT),
        ("Cd high 6.82 (unsourced)", CD_HIGH),
        ("Cd 1.38 (MEASURED, docs/LIT_QUEUE_2026-07-30.md:59-60)", CD_MEASURED_IN_REPO),
    ):
        sr = summarise(build_rows(sweep, cd=cd))
        print(f"  {label}: {sr['agree']}/{sr['n']} = {100.0 * sr['rate']:.2f}%")
    for label, mu in (("mu 0.30", 0.30), ("mu 0.55", MU_FLOOR), ("mu 0.78", 0.78)):
        sr = summarise([
            {
                "depth_m": r["depth_m"],
                "velocity_ms": r["velocity_ms"],
                "L1_verdict": r["L1_verdict"],
                "incipient_velocity_ms": "",
                "semi_empirical_verdict": semi_empirical_verdict(
                    float(r["depth_m"]), float(r["velocity_ms"]), mu=mu
                ),
                "agrees_with_L1": str(
                    semi_empirical_verdict(float(r["depth_m"]), float(r["velocity_ms"]), mu=mu)
                    == r["L1_verdict"]
                ),
            }
            for r in sweep
        ])
        print(f"  {label}: {sr['agree']}/{sr['n']} = {100.0 * sr['rate']:.2f}%")
    for label, m in (("mass 1100 kg", 1100.0), ("mass 1990 kg", 1990.0), ("mass 2300 kg", 2300.0)):
        sr = summarise(build_rows(sweep, mass_kg=m))
        print(f"  {label} (Yaris hull volume, geometry NOT rescaled): "
              f"{sr['agree']}/{sr['n']} = {100.0 * sr['rate']:.2f}%")
    print()

    print(f"wrote {OUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
