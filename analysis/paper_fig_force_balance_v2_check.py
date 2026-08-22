#!/usr/bin/env python3
"""Arithmetic check for force_balance_v2.pdf, the paper's Fig. force.

WHY THIS FILE EXISTS. A repo-wide search on 2026-08-20 with /usr/bin/grep, so
gitignored paths were reached, across the working tree and the archived
_inbox/can-it-ford-main.zip snapshot, found NO script anywhere that generates
force_balance_v2.pdf. The other six figures in the Overleaf project are
regenerable: four from analysis/paper_fig_*.py, L1_three_class_corrected.pdf
from analysis/plot_l1_three_class.py, and the render frame from its own run.
This one is not.

So the figure cannot be reproduced. What CAN be done is to check that every
number its caption states follows from the inputs the caption names, which
makes the figure falsifiable even with the plotting code lost. That is what
this script does. It asserts, so it fails loudly rather than printing a wall of
numbers nobody reads.

It deliberately does NOT redraw the figure. Drawing a replacement would produce
a second, subtly different artwork under the same name, which is worse than an
honest gap.

No numpy needed, and none is installed on the authoring machine.

Run:  python3 analysis/paper_fig_force_balance_v2_check.py
"""

# --- inputs, every one of them named in the figure caption or its paragraph ---
RHO_WATER = 1000.0        # kg/m^3, CLAUDE.md physical anchor
G = 9.81                  # m/s^2, solver value, core/solver.py set_material()
MASS_KG = 1100.0          # vehicle_params.py compact_sedan mass_kg
BBOX_L, BBOX_W, BBOX_H = 4.30, 1.70, 1.47   # vehicle_params.py compact_sedan bbox_m
PRISM_FRACTION = 0.75     # caption: "a solid prism over 0.75 of the bounding-box footprint"
HULL_M3 = 3.5427          # caption, and sim_standing.py HULL = 3.542739
MESH_EXTENT_M3 = 11.3533  # caption: "the mesh's own 11.3533 m3 extent"

# --- what the caption claims ---
CLAIMED = {
    "plan_area_m2":        5.4825,
    "weight_kn":          10.791,
    "buoyancy_at_0p30_kn": 16.135,
    "flotation_depth_m":   0.201,
    "fill_vs_prism":       0.33,
    "fill_vs_extent":      0.312,
}

def check(name, got, want, tol, unit=""):
    ok = abs(got - want) <= tol
    print("%-22s computed %12.6f   caption %10.4f %-4s  %s"
          % (name, got, want, unit, "OK" if ok else "MISMATCH"))
    assert ok, "%s: computed %r, caption says %r, tolerance %r" % (name, got, want, tol)

def main():
    plan_area = BBOX_L * BBOX_W * PRISM_FRACTION
    check("plan_area_m2", plan_area, CLAIMED["plan_area_m2"], 5e-5, "m2")

    weight_n = MASS_KG * G
    check("weight_kn", weight_n / 1000.0, CLAIMED["weight_kn"], 5e-4, "kN")

    # Archimedes on a prism of constant plan area, submerged to 0.30 m.
    buoy_n = RHO_WATER * G * plan_area * 0.30
    check("buoyancy_at_0p30_kn", buoy_n / 1000.0, CLAIMED["buoyancy_at_0p30_kn"], 5e-4, "kN")

    # Flotation depth: buoyancy equals weight, so g cancels entirely.
    # d = m / (rho * A). The caption's 0.201 m therefore does not depend on g.
    d_float = MASS_KG / (RHO_WATER * plan_area)
    check("flotation_depth_m", d_float, CLAIMED["flotation_depth_m"], 5e-4, "m")

    nominal_prism = BBOX_L * BBOX_W * BBOX_H
    check("nominal_prism_m3", nominal_prism, 10.7457, 5e-5, "m3")
    check("fill_vs_prism", HULL_M3 / nominal_prism, CLAIMED["fill_vs_prism"], 5e-3, "-")
    check("fill_vs_extent", HULL_M3 / MESH_EXTENT_M3, CLAIMED["fill_vs_extent"], 5e-4, "-")

    # N = 0 at 0.30 m is what makes the friction limit vanish, which is the
    # caption's stated reason for the three 0.00 kN legend entries.
    assert buoy_n > weight_n, "caption says N is zero at 0.30 m, so buoyancy must exceed weight"
    print("\nN at 0.30 m: buoyancy %0.3f kN exceeds weight %0.3f kN, so the normal force is"
          % (buoy_n / 1000.0, weight_n / 1000.0))
    print("clamped to zero and the friction limit mu*N vanishes with it, as the caption states.")

    print("\nALL CAPTION ARITHMETIC CHECKS PASS.")
    print("This validates the caption's numbers against its own stated inputs.")
    print("It does NOT validate the figure: the plotting script is missing, the prism")
    print("assumption is the model's one unpinned choice, and the caption says so itself.")

if __name__ == "__main__":
    main()
