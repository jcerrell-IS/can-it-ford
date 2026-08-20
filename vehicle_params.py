"""
vehicle_params.py
=================
Cited engineering parameters for three passenger-vehicle classes, for seeding
rigid bodies in MPM flood-crossing simulations (Genesis genesis-world / NVIDIA
Warp mesh-to-SDF coupling).

Project: "Can It Ford?" — NSF SCIPE REU 2026, TACC/UT Austin (Josie Cerrell).

ALL physical values are from PRIMARY / authoritative sources, not aggregators:
  - Curb weight & bounding box: manufacturer official spec sheets
    (Toyota media/UK, Honda Canada, Ford media/Europe), and, for the
    compact_sedan class, the crash-validated 2010 Toyota Yaris NCAC/CCSA
    LS-DYNA FE model (mass from deck header, bbox measured from the FE mesh).
  NOTE: the compact_sedan class was switched from a Corolla/Civic placeholder
    to the real 2010 Yaris. Its cg_height_m, inertia_kg_m2, and ssf are
    ESTIMATES (uniform-box fallback / subcompact-typical), NOT NHTSA-measured:
    the SAE 1999-01-1336 database ends Nov 1998 and contains no Yaris. Replace
    with measured Yaris values before relying on L2 overturning dynamics.
  - CG (center-of-gravity) height AND full moment-of-inertia tensor
    (Ixx roll, Iyy pitch, Izz yaw): NHTSA Light Vehicle Inertial Parameter
    Database, published as SAE Technical Paper 1999-01-1336
    (Heydinger, Bixel, Garrott, Pyne, Howe & Guenther,
     "Measured Vehicle Inertial Parameters — NHTSA's Data Through Nov 1998",
     DOI 10.4271/1999-01-1336). These are MEASURED (IPMD/VIMF), not estimated.
    Full listing (Auburn Univ., D. Bevly):
      https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf

UNITS (SI throughout, ready for Genesis/Warp which are metric):
  - mass_kg            : kg
  - bbox_m             : (length, width, height) in meters. Axis convention:
                         x = length (fore-aft, roll axis)
                         y = width  (lateral,  pitch axis)   [EXCLUDES mirrors]
                         z = height (vertical, yaw axis)
  - cg_height_m        : measured CG height above ground, meters
  - inertia_kg_m2      : dict of principal moments {Ixx, Iyy, Izz}, kg*m^2
                         Ixx = roll (about x), Iyy = pitch (about y),
                         Izz = yaw (about z).
                         NOT MEASURED FOR EVERY CLASS. For VEHICLE_PARAMS
                         ["compact_sedan"] it is a box fallback; read note 3
                         below before using it.
                         NB two taxonomies live in this file and they are NOT
                         interchangeable: VEHICLE_PARAMS keys are
                         compact_sedan / midsize_suv / light_pickup, whereas
                         AR_R_STABILITY_LIMITS keys are the AR&R classes
                         small_passenger / large_passenger / large_4wd.
  - ssf                : NHTSA Static Stability Factor (unitless), for reference

IMPORTANT PHYSICS NOTES for lateral-flow / overturning behavior (L2):
  1. Measured CG sits WELL BELOW h/2. Do NOT default the rigid-body CG to the
     bounding-box center — use `cg_height_m`. A too-high CG overstates the
     overturning moment arm under lateral flood drag.
  2. The uniform-density box tensor (see box_inertia()) OVERESTIMATES Iyy/Izz
     because real vehicle mass hugs the floor and center. Prefer a genuinely
     MEASURED `inertia_kg_m2` when the target model matches one of these
     classes; fall back to box_inertia() only for models with no NHTSA match.
     Read note 3 first: the compact_sedan tensor IN THIS FILE is a box
     fallback, not a measurement. Corrected 2026-08-20: a measured tensor for
     an actual 2010 Yaris DOES exist, on slide 7 of DOI 10.13021/G8JS5D
     (1078 kg; roll 388, pitch 1498, yaw 1647 kg m^2; CG Z 558 mm). It is not
     in this file, and note 3 says why wiring this file's numbers is still
     wrong: they are 19 to 26 percent off that measurement, while the solver's
     own particle cloud is within 2.3 percent.

  3. DO NOT WIRE `inertia_kg_m2` INTO THE MPM SOLVER FOR compact_sedan.
     Verified 2026-08-08 against live source and measured rollout data; see
     docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md section 1 for the full working.

     (a) It is not measured. {463.0, 1893.0, 1960.0} reproduces EXACTLY from
         box_inertia(1100, 4.30, 1.70, 1.47), i.e. a solid rectangular box. A
         measured tensor for an actual 2010 Yaris DOES exist (DOI 10.13021/G8JS5D,
         slide 7), but it is not in this file. Wiring this file's box values would
         introduce 19 to 26 percent error against that measurement, while the
         solver's own particle cloud is already within 2.3 percent. See note 3
         above for the full comparison.

     (b) The solver already computes a strictly better one. warpmpm derives the
         tensor from the actual hull particle cloud at
         kernels/mpm_solver_warp.py:859-871. Measured about the true centroid
         from the 8905 rigid particles of g64_m1100:
             hull cloud  Ixx 1501.5   Iyy  395.0   Izz 1685.4
             box (this)  Ixx 1893.0   Iyy  463.0   Izz 1959.8   <- axis-corrected
         The box overstates every principal moment by +16.3% to +26.1%. The hull
         fills only 33.2% of its own bounding box, so a solid box MUST overstate
         the mass spread. Wiring this is a regression on all three axes.

     (c) THE AXES ARE TRANSPOSED RELATIVE TO THE SCENE. This block documents
         bbox_m as (L,W,H) -> (x,y,z), but the gated scene puts the hull's LONG
         AXIS ON Y. Measured particle extents at frame 0 of g64_m1100:
             x 1.7078 m    y 4.2014 m    z 1.4853 m
         So a naive write of Ixx=463 / Iyy=1893 lands roll inertia on the pitch
         axis: Ixx -69.2% and Iyy +379.2% against the hull truth above. A 379%
         pitch-axis error, introduced by a change intended to improve realism.

     What IS usable here: cg_height_m as a COMPARISON, not a value to write. The
     cloud CG sits 0.6312 m above the floor, already below bbox mid-height
     0.7427 m, and 23.8% above the 0.51 m estimate. A too-high CG biases toward
     TOPPLE, and the 17 gated runs report zero topples, so the no-topple result
     is conservative. That is reportable at zero cost and requires no code change.

Each class stores a representative point estimate plus a (min, max) range.
Ranges span trims/model-years; point estimates are a sensible mid value.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Source URLs (kept as constants so they travel with the data)
# ---------------------------------------------------------------------------
SRC = {
    "nhtsa_sae_1999_01_1336": "https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf",  # DOI 10.4271/1999-01-1336
    "sae_mobilus_1999_01_1336": "https://saemobilus.sae.org/papers/measured-vehicle-inertial-parameters-nhtsas-data-november-1998-1999-01-1336",
    "ncac_yaris_fe": "https://doi.org/10.13021/G8JS5D",  # 2010 Toyota Yaris coarse FE model, CCSA/GMU + FHWA (NCAC), crash-validated
    "toyota_uk_corolla": "https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210127M-Corolla-Tech-Spec.pdf",
    "honda_ca_civic": "https://www.honda.ca/-/media/Brands/Honda/Models/CIVIC-SEDAN/2025/PDF/2025-Honda-Civic-Sedan-Specifications---EN_v2.pdf",
    "toyota_uk_highlander": "https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210321M-Highlander-Tech-Spec.pdf",
    "ford_f150_2021": "https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2021/specs/2021-F-150-Technical-Specs.pdf",
    "ford_f150_europe": "https://f150europe.com/-/media/Project/Hedin/Navigo/F150EuropeSite/PDF/EN-MY23-F-150-Technical-Specs-Europe.pdf",
}

# ---------------------------------------------------------------------------
# Vehicle class parameters
# ---------------------------------------------------------------------------
VEHICLE_PARAMS = {
    "compact_sedan": {
        # Subcompact sedan class, represented by the real 2010 Toyota Yaris
        # NCAC/CCSA crash-validated LS-DYNA FE model (George Mason Univ. + FHWA),
        # NOT a generic mid-size sedan placeholder. Geometry measured directly
        # from the coarse FE deck (yaris-coarse-v1l), mm rescaled to m; mass from
        # the deck header. Maps to the AR&R "Small Car" stability class (0.30 m
        # depth cap, 0.30 m2/s D*V cap), per Shand et al. 2011 / EMA 1999.
        "anchors": ["Toyota Yaris (2010, NCAC/CCSA coarse FE model)"],
        # curb weight, FE deck header ("Version 1l, 1100 kg"); matches published Yaris
        "mass_kg": 1100.0,
        "mass_kg_range": (1045.0, 1120.0),
        "mass_source": SRC["ncac_yaris_fe"],
        # bounding box (L, W-no-mirrors, H) meters, measured from the FE mesh
        # (raw 4.299 x 1.696 x 1.468 m) and consistent with Toyota spec
        # (4300 x 1695 x 1470 mm)
        "bbox_m": (4.30, 1.70, 1.47),
        "bbox_m_range": {"L": (4.29, 4.31), "W": (1.69, 1.71), "H": (1.46, 1.49)},
        "bbox_source": SRC["ncac_yaris_fe"],
        # cg_height and ssf below are ESTIMATES, not NHTSA-measured: the measured
        # NHTSA inertial DB (SAE 1999-01-1336) ends Nov 1998 and has no Yaris.
        # cg ~ 0.35 x body height (subcompact-typical). CONFIRM before L2/collider.
        "cg_height_m": 0.51,
        "cg_height_m_range": (0.49, 0.53),
        "cg_source": "estimate (no NHTSA-measured 2010 Yaris; subcompact-typical)",
        # inertia: uniform-density box fallback from Yaris mass+bbox. A measured
        # 2010 Yaris tensor DOES exist (DOI 10.13021/G8JS5D slide 7) and is not
        # this; see note 3(a). box_inertia() OVERESTIMATES Iyy/Izz; upper bound.
        "inertia_kg_m2": {"Ixx": 463.0, "Iyy": 1893.0, "Izz": 1960.0},
        "inertia_kg_m2_range": {
            "Ixx": (430.0, 500.0),
            "Iyy": (1750.0, 2050.0),
            "Izz": (1800.0, 2100.0),
        },
        "inertia_source": "uniform-density box fallback (measured 2010 Yaris tensor exists at DOI 10.13021/G8JS5D slide 7; not used here, see note 3)",
        "inertia_reference_vehicle": "uniform-density box (2010 Yaris mass+bbox; no NHTSA measured entry)",
        "ssf": 1.42,  # estimate: track/(2*cg), subcompact-typical; CONFIRM before use
    },
    "midsize_suv": {
        "anchors": ["Toyota Highlander", "Ford Explorer"],
        "mass_kg": 1990.0,
        "mass_kg_range": (1880.0, 2100.0),
        "mass_source": SRC["toyota_uk_highlander"],
        "bbox_m": (4.96, 1.93, 1.75),
        "bbox_m_range": {"L": (4.95, 4.97), "W": (1.93, 1.93), "H": (1.73, 1.76)},
        "bbox_source": SRC["toyota_uk_highlander"],
        "cg_height_m": 0.70,
        "cg_height_m_range": (0.68, 0.74),
        "cg_source": SRC["nhtsa_sae_1999_01_1336"],
        # representative: 1998 Ford Explorer (measured)
        "inertia_kg_m2": {"Ixx": 740.0, "Iyy": 3561.0, "Izz": 3682.0},
        "inertia_kg_m2_range": {
            "Ixx": (700.0, 860.0),
            "Iyy": (2900.0, 5100.0),
            "Izz": (3100.0, 5400.0),
        },
        "inertia_source": SRC["nhtsa_sae_1999_01_1336"],
        "inertia_reference_vehicle": "1998 Ford Explorer (measured, SAE 1999-01-1336)",
        "ssf": 1.04,  # 1998 Explorer-class
    },
    "light_pickup": {
        "anchors": ["Ford F-150", "Toyota Tacoma/Tundra"],
        "mass_kg": 2300.0,
        "mass_kg_range": (1825.0, 2600.0),
        "mass_source": SRC["ford_f150_2021"],  # + ford_f150_europe
        # short-bed SuperCrew; length spans short->long bed
        "bbox_m": (5.89, 2.03, 1.96),
        "bbox_m_range": {"L": (5.89, 6.19), "W": (2.03, 2.03), "H": (1.92, 2.01)},
        "bbox_source": SRC["ford_f150_2021"],
        "cg_height_m": 0.69,
        "cg_height_m_range": (0.65, 0.72),  # Tacoma-class ~0.57-0.60
        "cg_source": SRC["nhtsa_sae_1999_01_1336"],
        # representative: 1990 Ford F150 (measured)
        "inertia_kg_m2": {"Ixx": 839.0, "Iyy": 5067.0, "Izz": 5070.0},
        "inertia_kg_m2_range": {
            "Ixx": (500.0, 850.0),
            "Iyy": (2900.0, 5500.0),
            "Izz": (3000.0, 5400.0),
        },
        "inertia_source": SRC["nhtsa_sae_1999_01_1336"],
        "inertia_reference_vehicle": "1990 Ford F150 (measured, SAE 1999-01-1336)",
        "ssf": 1.19,  # F150-class
    },
}


AR_R_SOURCE = (
    "Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2, P10/S2/020, "
    "ISBN 978-0-85825-948-5, Table 3 'Proposed DRAFT Stability Criteria for "
    "Stationary Vehicles', PDF p.24 / printed p.14. Values are the report's own "
    "DRAFT INTERIM figures for STATIONARY vehicles, not an endorsed safety standard."
)

AR_R_STABILITY_LIMITS = {
    "small_passenger": {
        "depth_m": 0.30, "velocity_ms": 3.0, "haz_m2s": 0.30,
        "report_class": "Small passenger",
        "length_m_max": 4.3, "kerb_weight_kg_max": 1250, "ground_clearance_m_max": 0.12,
    },
    "large_passenger": {
        "depth_m": 0.40, "velocity_ms": 3.0, "haz_m2s": 0.45,
        "report_class": "Large passenger",
        "length_m_min": 4.3, "kerb_weight_kg_min": 1250, "ground_clearance_m_min": 0.12,
    },
    "large_4wd": {
        "depth_m": 0.50, "velocity_ms": 3.0, "haz_m2s": 0.60,
        "report_class": "Large 4WD",
        "length_m_min": 4.5, "kerb_weight_kg_min": 2000, "ground_clearance_m_min": 0.22,
    },
}

AR_R_CLASS_ORDER = ("small_passenger", "large_passenger", "large_4wd")


def L1_verdict(depth_m: float, velocity_ms: float, vehicle_class: str = "small_passenger") -> str:
    if vehicle_class not in AR_R_STABILITY_LIMITS:
        raise ValueError(
            f"no AR&R stability limits sourced for vehicle_class={vehicle_class!r}; "
            f"only {list(AR_R_STABILITY_LIMITS)} are populated"
        )
    limits = AR_R_STABILITY_LIMITS[vehicle_class]
    if depth_m > limits["depth_m"]:
        return "NO-FORD"
    if velocity_ms > limits["velocity_ms"]:
        return "NO-FORD"
    if round(depth_m * velocity_ms, 6) > limits["haz_m2s"]:
        return "NO-FORD"
    return "FORD"


# ---------------------------------------------------------------------------
# Uniform-density box fallback (for models with no NHTSA match)
# ---------------------------------------------------------------------------
def box_inertia(mass_kg: float, length_m: float, width_m: float, height_m: float) -> dict:
    """Principal moments of inertia (kg*m^2) of a uniform-density rectangular
    box about its own center of mass.

    Axis convention (matches bbox_m):
        x = length (fore-aft, roll)   -> Ixx = (1/12) m (w^2 + h^2)
        y = width  (lateral, pitch)   -> Iyy = (1/12) m (L^2 + h^2)
        z = height (vertical, yaw)     -> Izz = (1/12) m (L^2 + w^2)

    NOTE: this OVERESTIMATES Iyy/Izz vs. measured vehicles (real mass hugs the
    floor/center). Use only when no measured tensor is available for the model.
    """
    L, w, h, m = length_m, width_m, height_m, mass_kg
    return {
        "Ixx": (1.0 / 12.0) * m * (w * w + h * h),
        "Iyy": (1.0 / 12.0) * m * (L * L + h * h),
        "Izz": (1.0 / 12.0) * m * (L * L + w * w),
    }


def get_vehicle(vehicle_class: str, use_measured_inertia: bool = True) -> dict:
    """Return a flat, simulation-ready parameter dict for a vehicle class.

    Args:
        vehicle_class: one of 'compact_sedan', 'midsize_suv', 'light_pickup'.
        use_measured_inertia: if True (default) use the measured NHTSA tensor;
            if False, compute the uniform-density box tensor from bbox + mass.

    Returns dict with keys: class, mass_kg, bbox_m (L,W,H), cg_height_m,
        inertia_kg_m2 {Ixx,Iyy,Izz}, inertia_model, ssf, sources.
    """
    if vehicle_class not in VEHICLE_PARAMS:
        raise KeyError(
            f"Unknown vehicle_class {vehicle_class!r}; "
            f"choose from {list(VEHICLE_PARAMS)}"
        )
    v = VEHICLE_PARAMS[vehicle_class]
    L, W, H = v["bbox_m"]
    if use_measured_inertia:
        inertia = dict(v["inertia_kg_m2"])
        inertia_model = f"measured NHTSA ({v['inertia_reference_vehicle']})"
    else:
        inertia = box_inertia(v["mass_kg"], L, W, H)
        inertia_model = "uniform-density box approximation"
    return {
        "class": vehicle_class,
        "anchors": v["anchors"],
        "mass_kg": v["mass_kg"],
        "bbox_m": v["bbox_m"],
        "cg_height_m": v["cg_height_m"],
        "inertia_kg_m2": inertia,
        "inertia_model": inertia_model,
        "ssf": v["ssf"],
        "sources": {
            "mass": v["mass_source"],
            "bbox": v["bbox_source"],
            "cg_height": v["cg_source"],
            "inertia": v["inertia_source"]
            if use_measured_inertia
            else "computed (uniform box)",
        },
    }


def inertia_tensor_diag(vehicle_class: str, use_measured_inertia: bool = True):
    """Return the 3x3 diagonal inertia tensor as a nested list [[Ixx,0,0],...],
    ready to hand to a rigid body. Off-diagonal products of inertia are taken as
    zero (principal-axis assumption; the NHTSA roll-yaw products are small).
    """
    v = get_vehicle(vehicle_class, use_measured_inertia)
    I = v["inertia_kg_m2"]
    return [
        [I["Ixx"], 0.0, 0.0],
        [0.0, I["Iyy"], 0.0],
        [0.0, 0.0, I["Izz"]],
    ]


if __name__ == "__main__":
    # Quick self-check / demo: print measured vs box tensors for all classes.
    for cls in VEHICLE_PARAMS:
        meas = get_vehicle(cls, use_measured_inertia=True)
        box = get_vehicle(cls, use_measured_inertia=False)
        L, W, H = meas["bbox_m"]
        print(f"\n=== {cls}  ({', '.join(meas['anchors'])}) ===")
        print(f"  mass       : {meas['mass_kg']:.0f} kg")
        print(f"  bbox (LxWxH): {L:.2f} x {W:.2f} x {H:.2f} m")
        print(f"  CG height  : {meas['cg_height_m']:.2f} m   (box mid = {H/2:.2f} m)")
        print(f"  SSF        : {meas['ssf']:.2f}")
        print("  inertia (kg*m^2):")
        print(
            f"    measured : Ixx={meas['inertia_kg_m2']['Ixx']:7.0f}  "
            f"Iyy={meas['inertia_kg_m2']['Iyy']:7.0f}  "
            f"Izz={meas['inertia_kg_m2']['Izz']:7.0f}"
        )
        print(
            f"    box      : Ixx={box['inertia_kg_m2']['Ixx']:7.0f}  "
            f"Iyy={box['inertia_kg_m2']['Iyy']:7.0f}  "
            f"Izz={box['inertia_kg_m2']['Izz']:7.0f}"
        )
