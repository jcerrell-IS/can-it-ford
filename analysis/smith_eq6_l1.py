"""
smith_eq6_l1.py
===============
Score the 70-cell scenario grid (data/scenario_sweep.csv) with the
limiting stability curve of Smith, Modra and Felder 2019, Eq. 6, for the Toyota
Yaris, and compare it cell by cell with the L0 and L1 verdicts already in that
file.

Source paper: Smith GP, Modra BD, Felder S (2019). Full-scale testing of
stability curves for vehicles in flood waters. J Flood Risk Management
12(S2):e12527. DOI 10.1111/jfr3.12527. Pages read for this script: page 3
(Eqs. 1 to 4), page 5 (Table 1) and page 12 (Figure 10 with the Eq. 6 line).
The transcription of Eq. 6 is
citations/smith_modra_felder_2019_velocity_grounding.md, section "The
actually citable, exact, invertible relationship".

Eq. 6 (paper p. 12):   d - d_pan = 0.414 - 0.244 * Fr,  valid for d - d_pan > 0
with Fr = V / sqrt(g d) (paper p. 3, under Eq. 3).

Verdict rule used here: a cell is FORD (stable) under Eq. 6 when the point
(Fr, d - d_pan) lies strictly below the Eq. 6 line, i.e.
    d - d_pan < 0.414 - 0.244 * Fr.
This reading follows Figure 10, where the line bounds the measured instability
points from below-left; it is an interpretation of the figure, stated here so
that it can be challenged.

WHY 63 CELLS AND NOT 70. Eq. 6 is stated only for d - d_pan > 0. With the
Yaris floor pan d_pan = 0.155 m (Table 1), the seven cells at depth 0.1 m
(velocities 0.0 to 3.0 m/s) lie below the floor pan, so Eq. 6 makes no
statement there. They are reported as OUT-OF-DOMAIN, never as FORD or NO-FORD.
70 - 7 = 63.

VEHICLE IDENTITY CAVEAT. Smith Table 1 is a 2006 Yaris SEDAN (1045 kg,
d_pan 0.155 m). The project's vehicle is the 2010 Yaris (vehicle_params.py
VEHICLE_PARAMS["compact_sedan"]). vehicle_params.py has no floor-pan field
for the 2010 car. The only measured clearance for the 2010 hull is 177.4 mm
(5th percentile of column minima between the axles, measured in the
development repository, not included here). The pinned counts use the paper's 0.155 m;
the 0.1774 m variant is printed as a sensitivity line only.

Run from the repository root:
    python3 analysis/smith_eq6_l1.py
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from vehicle_params import L1_verdict  # noqa: E402  (vehicle_params.py, def L1_verdict)

SWEEP_CSV = REPO / "data" / "scenario_sweep.csv"
EXPECTED_COLUMNS = 10

# ---------------------------------------------------------------------------
# Coefficients, each with its source. Nothing here is invented; anything that
# could not be traced is listed in UNTRACED below and printed.
# ---------------------------------------------------------------------------
COEFFS = {
    "EQ6_INTERCEPT_M": (0.414, "Smith et al. 2019 Eq. 6, p. 12"),
    "EQ6_SLOPE_M": (0.244, "Smith et al. 2019 Eq. 6, p. 12"),
    "D_PAN_YARIS_2006_M": (0.155, "Smith et al. 2019 Table 1, p. 5 (Toyota Yaris Sedan 2006)"),
    "D_PAN_HULL_2010_M": (
        0.1774,
        "2010 hull underbody clearance, 177.4 mm, measured in the development "
        "repository; SENSITIVITY ONLY",
    ),
    "G_MS2": (9.81, "project standing physical anchors (g=9.81); Fr definition Smith et al. 2019 p. 3"),
}

UNTRACED = [
    "Floor-pan height of the 2010 Yaris: not in vehicle_params.py. The pinned "
    "result uses the 2006 Yaris value from Smith Table 1; the 2010 hull's "
    "measured underbody clearance (0.1774 m) is a mesh measurement, not a "
    "floor-pan definition matching Smith's.",
    "L0 rule (FORD iff depth < 0.15 m): read from the L0_verdict column of "
    "data/scenario_sweep.csv; the same 0.15 m literal sits in "
    "analysis/four_rung_ladder.py (L0_DEPTH_THRESHOLD_M) with no citation. "
    "This script does not supply a source for it.",
    "Strict '<' for Eq. 6 stability is read from Figure 10, not stated in "
    "the paper's text.",
]

FLOAT_TOL = 1e-9  # the D x V trap: 0.2 * 1.5 <= 0.30 is False in IEEE floats


def froude(depth_m: float, velocity_ms: float, g: float = COEFFS["G_MS2"][0]) -> float:
    return velocity_ms / math.sqrt(g * depth_m)


def eq6_verdict(depth_m: float, velocity_ms: float,
                d_pan_m: float = COEFFS["D_PAN_YARIS_2006_M"][0]) -> str:
    """FORD / NO-FORD / OUT-OF-DOMAIN under Smith et al. 2019 Eq. 6."""
    lhs = depth_m - d_pan_m
    if lhs <= 0.0:
        return "OUT-OF-DOMAIN"
    a = COEFFS["EQ6_INTERCEPT_M"][0]
    b = COEFFS["EQ6_SLOPE_M"][0]
    rhs = a - b * froude(depth_m, velocity_ms)
    return "FORD" if lhs < rhs - FLOAT_TOL else "NO-FORD"


def eq6_limit_velocity(depth_m: float,
                       d_pan_m: float = COEFFS["D_PAN_YARIS_2006_M"][0]) -> float | None:
    """Limiting V from Eq. 6 at a given depth (None if out of domain, 0 if none)."""
    lhs = depth_m - d_pan_m
    if lhs <= 0.0:
        return None
    a = COEFFS["EQ6_INTERCEPT_M"][0]
    b = COEFFS["EQ6_SLOPE_M"][0]
    fr = (a - lhs) / b
    return max(fr, 0.0) * math.sqrt(COEFFS["G_MS2"][0] * depth_m)


def load_grid(path: Path = SWEEP_CSV) -> list[dict]:
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        if len(reader.fieldnames or []) != EXPECTED_COLUMNS:
            raise RuntimeError(
                f"{path} has {len(reader.fieldnames or [])} columns; the live file "
                f"has {EXPECTED_COLUMNS}. Refusing to score a different file."
            )
        rows = []
        for r in reader:
            rows.append({
                "depth_m": float(r["depth_m"]),
                "velocity_ms": float(r["velocity_ms"]),
                "L0": r["L0_verdict"],
                "L1": r["L1_verdict"],
            })
    return rows


def score(rows: list[dict], d_pan_m: float = COEFFS["D_PAN_YARIS_2006_M"][0]) -> list[dict]:
    out = []
    for r in rows:
        d, v = r["depth_m"], r["velocity_ms"]
        l1_live = L1_verdict(d, v, "small_passenger")
        if l1_live != r["L1"]:
            raise RuntimeError(
                f"csv L1_verdict {r['L1']} disagrees with vehicle_params.L1_verdict "
                f"{l1_live} at ({d}, {v})"
            )
        out.append({**r, "Fr": froude(d, v), "EQ6": eq6_verdict(d, v, d_pan_m)})
    return out


def summarise(scored: list[dict]) -> dict:
    in_domain = [c for c in scored if c["EQ6"] != "OUT-OF-DOMAIN"]
    eq6_ford = [c for c in in_domain if c["EQ6"] == "FORD"]
    l1_ford = [c for c in in_domain if c["L1"] == "FORD"]
    l0_ford = [c for c in in_domain if c["L0"] == "FORD"]
    l1_inside = all(c["EQ6"] == "FORD" for c in l1_ford)
    disagree_l1 = [c for c in in_domain if c["EQ6"] != c["L1"]]
    disagree_l0 = [c for c in in_domain if c["EQ6"] != c["L0"]]
    return {
        "n_total": len(scored),
        "n_out_of_domain": len(scored) - len(in_domain),
        "out_of_domain_cells": [(c["depth_m"], c["velocity_ms"]) for c in scored
                                if c["EQ6"] == "OUT-OF-DOMAIN"],
        "n_in_domain": len(in_domain),
        "n_eq6_ford": len(eq6_ford),
        "n_l1_ford": len(l1_ford),
        "n_l0_ford": len(l0_ford),
        "l1_ford_subset_of_eq6_ford": l1_inside,
        "eq6_ford_cells": [(c["depth_m"], c["velocity_ms"]) for c in eq6_ford],
        "l1_ford_cells": [(c["depth_m"], c["velocity_ms"]) for c in l1_ford],
        "n_disagree_l1": len(disagree_l1),
        "n_disagree_l0": len(disagree_l0),
    }


def main() -> None:
    print("Smith, Modra and Felder 2019 Eq. 6 vs L0 / L1 on data/scenario_sweep.csv")
    print("Eq. 6 is a vehicle-calibrated model whose velocities come from Eq. 4 with")
    print("C_D 1.38 and mu 0.3 / 0.78 (stagnant-water traction tests), not a")
    print("flowing-water measurement. This is a comparison, not a validation.\n")
    print("Coefficients and sources:")
    for k, (val, src) in COEFFS.items():
        print(f"  {k:22s} = {val:<8} <- {src}")
    print("\nUNTRACED (stated, not invented):")
    for u in UNTRACED:
        print(f"  - {u}")

    rows = load_grid()
    scored = score(rows)
    s = summarise(scored)

    print("\nCell table (Eq. 6 with d_pan 0.155 m):")
    print(f"  {'depth':>5} {'V':>4} {'Fr':>6} {'L0':>8} {'L1':>8} {'Eq6':>14}  note")
    for c in scored:
        note = ""
        if c["EQ6"] != "OUT-OF-DOMAIN" and c["EQ6"] != c["L1"]:
            note = "Eq6 != L1"
        print(f"  {c['depth_m']:5.2f} {c['velocity_ms']:4.1f} {c['Fr']:6.3f} "
              f"{c['L0']:>8} {c['L1']:>8} {c['EQ6']:>14}  {note}")

    print("\nEq. 6 limiting velocity per depth (d_pan 0.155 m):")
    for d in sorted({c["depth_m"] for c in scored}):
        vl = eq6_limit_velocity(d)
        print(f"  d={d:4.2f} m  V_lim=" + ("out of domain" if vl is None else f"{vl:5.3f} m/s"))

    print("\nSummary:")
    print(f"  cells in grid                  : {s['n_total']}")
    print(f"  out of Eq. 6 domain (d<=d_pan) : {s['n_out_of_domain']} -> {s['out_of_domain_cells']}")
    print(f"  cells scored by Eq. 6          : {s['n_in_domain']}")
    print(f"  Eq. 6 FORD                     : {s['n_eq6_ford']} of {s['n_in_domain']}")
    print(f"  L1 (AR&R small passenger) FORD : {s['n_l1_ford']} of {s['n_in_domain']}")
    print(f"  L0 FORD                        : {s['n_l0_ford']} of {s['n_in_domain']}")
    print(f"  every L1 FORD is an Eq. 6 FORD : {s['l1_ford_subset_of_eq6_ford']}")
    print(f"  Eq. 6 vs L1 disagreements      : {s['n_disagree_l1']}")
    print(f"  Eq. 6 vs L0 disagreements      : {s['n_disagree_l0']}")

    alt = summarise(score(rows, COEFFS["D_PAN_HULL_2010_M"][0]))
    print("\nSensitivity (not pinned): d_pan = 0.1774 m (2010 hull underbody clearance)")
    print(f"  scored {alt['n_in_domain']}, Eq. 6 FORD {alt['n_eq6_ford']}, L1 FORD "
          f"{alt['n_l1_ford']}, L1 subset of Eq. 6: {alt['l1_ford_subset_of_eq6_ford']}")


if __name__ == "__main__":
    main()
