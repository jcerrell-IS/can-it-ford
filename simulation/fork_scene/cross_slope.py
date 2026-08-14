#!/usr/bin/env python3
"""Road cross-slope: the two ways to express it in warpmpm, and what it moves.

THE IDENTIFICATION THAT MAKES THIS THE RIGHT TERRAIN PROPERTY TO TEST
=====================================================================
In the canonical scene the vehicle's long axis lies on y and the flow runs
along x (inflow slab at the upstream x face, renders/yaris_render_s1/
_incoming/sim_standing.py). A road's direction of travel is therefore y, and
the road's CROSS-slope, the transverse camber or superelevation perpendicular
to travel, lies along x.

    The road's cross-slope IS the bed slope of the cross-road flow.

That is why it is the one terrain property with a plausible hydraulic effect at
this scale: it is not a decoration on the floor, it is the channel's S0.

TWO FORMULATIONS, AND THEY ARE NOT EQUALLY GOOD
===============================================
T. TILTED PLANE.  add_plane(point, normal=(sin th, 0, cos th), ...)
   Arbitrary normals are supported: add_surface_collider normalises whatever it
   is given (mpm_solver_warp.py:1892-1893) and the grid test is a half-space
   dot product (:1947-1955), so nothing about a tilted plane is special-cased
   wrong. Two costs, both verified live rather than guessed:

   T-1 IT LOSES THE RESTRICTED-LAUNCH FAST PATH. mpm_solver_warp.py:1997 reads

           _axis = next((i for i in range(3) if abs(abs(normal[i]) - 1.0) < 1e-6), -1)

       and only an AXIS-ALIGNED plane gets a bounded launch box; anything else
       appends None to collider_aabbs and is labelled "plane_free" (:2013-2016),
       i.e. the collider kernel launches over the WHOLE grid every substep. The
       canonical floor sits at 3*dx with halo 1, so its bounded launch covers
       about 5 of 65 node layers. Tilting it multiplies that kernel's launch
       volume by roughly 13x. See `launch_volume_penalty()`.

   T-2 IT EATS THE TANK'S HEADROOM. A cubic domain of edge `lim` with a bed of
       slope S drops S*lim from one wall to the other. At the canonical
       lim 9.4217 m and S 0.02 that is 0.1884 m against a 0.2944 m water depth,
       i.e. 64% of the depth spent on tilt. The upstream end runs dry unless
       the tank is deepened, which changes the water volume and confounds the
       comparison. See `bed_drop_across_domain()`.

G. TILTED GRAVITY, BED-ALIGNED FRAME.  floor stays at normal (0,0,1); gravity
   becomes g' = (+g sin th, 0, -g cos th) in the frame where the bed is flat.
   The fast path survives, the water depth is uniform by construction, and the
   domain holds exactly the same water volume as the S=0 control, so the
   comparison is actually held fixed.

   THIS REQUIRES OVERRIDING GRAVITY, AND IT IS OVERRIDABLE. Checked live
   2026-08-14 against core/solver.py:159-171, which builds

       params = {**params, **overrides}
       self._sim.set_parameters_dict({"material": name, "g": [0,0,-9.81], **params}, ...)

   `**params` is spread AFTER the "g" key, so a caller-supplied g WINS. A
   direct test of that exact dict-merge returns [0.0, 0.1712, -9.8085] for a
   g= override. No engine patch is needed.

   NOTE, AND THIS CORRECTS A CANONICAL FILE THIS DISPATCH MAY NOT EDIT:
   CLAUDE.md item 3 says solver.py "hardcodes g=[0,0,-9.81] ... unconditionally".
   The word "unconditionally" is false; a keyword override wins. Everything else
   in item 3 stands: newtonian() carries no g key and the canonical driver
   passes no override, so all 17 gated runs did run at exactly 9.81 m/s2. Filed
   in docs/FORK_SCENE_FLAGGED_FOR_OWNERS_2026-08-14.md; not edited here.

RECOMMENDATION: G FOR THE PHYSICS, T ONLY AS A CROSS-CHECK. They are the same
system in two frames and must agree in the interior; they differ only in the
orientation of the domain walls (world-vertical in T, bed-normal in G), which
is a 1.15 degree difference at S=0.02. Running both is the held-fixed control
that shows the wall orientation is not carrying the result.

WHAT THE SLOPE DOES TO THE TRACTION MARGIN, IN CLOSED FORM
==========================================================
Stationary vehicle, bed-aligned frame, submerged weight (W - B):

    N   = (W - B) cos th - L            normal load
    F_F = mu * N                        traction available
    F_x = F_D + (W - B) sin th          along-bed driving force
    M   = F_F - F_x                     traction margin

With L = 0 (no lift measurement exists in this project; stated, not assumed
away) the slope-induced CHANGE is

    dM = M(th) - M(0) = -(W - B) * [ sin th + mu * (1 - cos th) ]

and it is EXACTLY INDEPENDENT OF THE DRAG, because F_D enters additively and
is unchanged by the tilt. So the static half of the cross-slope sensitivity can
be answered in closed form, on a laptop, with no simulation and no C_D. That is
the useful result, and it reframes what the MPM run is for:

    the STATIC term is exact and needs no run;
    the HYDRODYNAMIC term, whether a bed slope changes the drag or the local
    depth at the vehicle BEYOND that static tilt, is what needs the run.

PARAMETERS, WITH PROVENANCE. Do not invent these.
  mu 0.3    parked baseline, Bonham and Hattersley 1967, adopted conservatively
            for the published hazard curves
  mu 0.52   measured parallel to flow (Shah et al. 2018)
  mu 0.75   measured tyre friction, wet concrete (Smith, Modra, Felder 2019)
  NOT 0.55. floor_friction 0.55 is the SIM's grid boundary-condition friction
            for water and the rigid-contact surface, not a tyre-road mu. They
            are different quantities and must never be swapped.

  cross-slope range 1 to 6 percent: Cavdar and Uyumaz 2022, Teknik Dergi
            33(5):12663-12676, doi:10.18400/tekderg.989134 (open access,
            full-text read 2026-08-14 via Scite, no editorial notices). That
            paper sweeps 1 to 10 percent cross slope and states the ceiling is
            set by exactly the failure mode modelled here: "The steepness of
            the cross slope is limited for safety considerations (the vehicle
            tends to veer towards the low edge of the pavement)".
            SCOPE, STATED BECAUSE IT MATTERS: that paper models millimetre-
            scale rainfall sheet flow, not a 0.29 m flood. The cross-slope
            VALUES transfer because they are road geometry; its HYDRAULICS do
            not transfer and are not used here.
            The 2 percent default additionally matches AASHTO practice for
            high-type pavement. That attribution is UNVERIFIED against the
            Green Book itself, which is not on this machine; it is not
            load-bearing, because every result below is swept over S.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass

__all__ = [
    "G", "WATER_DENSITY", "CANONICAL_DEPTH_M", "CANONICAL_LIM_M",
    "MU_PARKED", "MU_PARALLEL", "MU_TYRE_WET", "SLOPES_DESIGN",
    "CrossSlope", "bed_drop_across_domain", "launch_volume_penalty",
    "submerged_volume", "VehicleState", "traction_margin",
    "margin_change_from_slope", "sensitivity_table",
]

G = 9.81
WATER_DENSITY = 1000.0
CANONICAL_DEPTH_M = 0.2944294473039918
CANONICAL_LIM_M = 9.421742313727737

MU_PARKED = 0.30        # Bonham and Hattersley 1967, conservative baseline
MU_PARALLEL = 0.52      # Shah et al. 2018, measured parallel to flow
MU_TYRE_WET = 0.75      # Smith, Modra, Felder 2019, wet concrete

# 0 is the control. 0.02 is the design default. 0.06 is a steep superelevation
# and sits at the top of the range Cavdar and Uyumaz call safe.
SLOPES_DESIGN = (0.0, 0.02, 0.06)

# Submerged volume vs waterline for the three qualified hulls, measured by the
# mesh-qualification pipeline (phase3_buoyancy.py) and read from phase3.json.
# Path is outside the repo, so every consumer below degrades gracefully if it
# is absent rather than inventing a number.
PHASE3_JSON = "/Users/josie/can-it-ford-meshes-qualified/phase3.json"
PHASE3_KEYS = {
    "yaris": "yaris_canonical",
    "rogue": "rogue_g96_pd8_coarse_watertight",
    "silverado": "silverado_g96_pd8_coarse_watertight",
}


@dataclass(frozen=True)
class CrossSlope:
    """A road cross-slope, expressible either way. S is rise over run."""

    S: float

    @property
    def theta_rad(self) -> float:
        return math.atan(self.S)

    @property
    def theta_deg(self) -> float:
        return math.degrees(self.theta_rad)

    def plane_normal(self) -> tuple[float, float, float]:
        """Formulation T: upward normal of a bed descending in +x.

        Bed surface z = z0 - x*S, so F = z - z0 + x*S, grad F = (S, 0, 1), and
        the unit upward normal is (sin th, 0, cos th).
        """
        th = self.theta_rad
        return (math.sin(th), 0.0, math.cos(th))

    def gravity_vector(self, g: float = G) -> tuple[float, float, float]:
        """Formulation G: gravity in the bed-aligned frame.

        Downslope component +g sin th on +x, bed-normal component -g cos th.
        Pass straight to Solver.set_material(material, g=...).
        """
        th = self.theta_rad
        return (g * math.sin(th), 0.0, -g * math.cos(th))

    def is_axis_aligned(self) -> bool:
        """Whether formulation T keeps the solver's restricted-launch fast path.

        Reproduces mpm_solver_warp.py:1997's own test, so this cannot drift away
        from what the engine actually does.
        """
        n = self.plane_normal()
        return any(abs(abs(c) - 1.0) < 1e-6 for c in n)


def bed_drop_across_domain(slope: CrossSlope, lim: float = CANONICAL_LIM_M,
                           depth: float = CANONICAL_DEPTH_M) -> dict:
    """Formulation T's geometric cost: how much depth the tilt spends."""
    drop = slope.S * lim
    return {"drop_m": drop, "depth_m": depth, "drop_over_depth": drop / depth}


def launch_volume_penalty(n_grid: int = 64, floor_cells: float = 3.0,
                          halo: int = 1) -> float:
    """Formulation T's engine cost: the collider kernel's launch-volume ratio.

    An axis-aligned floor at floor_cells*dx gets a launch box reaching from the
    grid base to that node plus a halo, i.e. (floor_cells + halo + 1) node
    layers of (n_grid + 1). A tilted plane is "plane_free" and launches over all
    of them. This counts NODE LAYERS in one kernel, which is exactly what
    :1997-2016 decides; it is NOT a whole-run slowdown factor and must not be
    quoted as one.
    """
    layers = n_grid + 1
    bounded = floor_cells + halo + 1
    return layers / bounded


def submerged_volume(vehicle: str, waterline_m: float = CANONICAL_DEPTH_M,
                     phase3_path: str = PHASE3_JSON) -> float | None:
    """Displaced volume at a waterline measured from the hull's own base, m3.

    The hull sits on the floor in the canonical scene, so the waterline above
    the floor and the waterline above the hull base are the same number.
    Returns None if the qualification data is not on this machine; callers must
    handle that rather than substitute a guess.
    """
    try:
        with open(phase3_path) as fh:
            data = json.load(fh)
    except OSError:
        return None
    key = PHASE3_KEYS.get(vehicle)
    if key is None or key not in data:
        return None
    curve = data[key]["curve"]
    zs = [float(z) for z, _ in curve]
    vs = [float(v) for _, v in curve]
    if waterline_m <= zs[0]:
        return vs[0]
    if waterline_m >= zs[-1]:
        return vs[-1]
    for i in range(1, len(zs)):
        if zs[i] >= waterline_m:
            t = (waterline_m - zs[i - 1]) / (zs[i] - zs[i - 1])
            return vs[i - 1] + t * (vs[i] - vs[i - 1])
    return vs[-1]


@dataclass(frozen=True)
class VehicleState:
    """Everything the margin needs. `lift_n` is 0.0 and that is a STATED gap.

    No lift measurement exists anywhere in this project. Setting it to zero
    biases the margin OPTIMISTIC (real lift reduces the normal load), so a
    margin computed here is an upper bound on the traction available.
    """

    name: str
    mass_kg: float
    v_sub_m3: float
    mu: float = MU_PARKED
    lift_n: float = 0.0

    @property
    def weight_n(self) -> float:
        return self.mass_kg * G

    @property
    def buoyancy_n(self) -> float:
        return WATER_DENSITY * G * self.v_sub_m3

    @property
    def submerged_weight_n(self) -> float:
        return self.weight_n - self.buoyancy_n

    @property
    def buoyancy_fraction(self) -> float:
        return self.buoyancy_n / self.weight_n


def traction_margin(veh: VehicleState, slope: CrossSlope, drag_n: float) -> dict:
    """The full balance at one slope. Units: newtons throughout."""
    th = slope.theta_rad
    wb = veh.submerged_weight_n
    normal_n = wb * math.cos(th) - veh.lift_n
    friction_n = veh.mu * normal_n
    slope_force_n = wb * math.sin(th)
    driving_n = drag_n + slope_force_n
    return {
        "slope_S": slope.S,
        "theta_deg": slope.theta_deg,
        "normal_n": normal_n,
        "friction_available_n": friction_n,
        "slope_force_n": slope_force_n,
        "drag_n": drag_n,
        "driving_n": driving_n,
        "margin_n": friction_n - driving_n,
        "slides": friction_n < driving_n,
    }


def margin_change_from_slope(veh: VehicleState, slope: CrossSlope) -> dict:
    """dM = -(W - B) [ sin th + mu (1 - cos th) ], exactly independent of drag.

    Returned alongside a direct difference of two full balances at an arbitrary
    drag, as a numerical proof that the drag really does cancel.
    """
    th = slope.theta_rad
    wb = veh.submerged_weight_n
    closed_form = -wb * (math.sin(th) + veh.mu * (1.0 - math.cos(th)))
    probe_drag = 1234.5           # arbitrary; the point is that it cancels
    direct = (traction_margin(veh, slope, probe_drag)["margin_n"]
              - traction_margin(veh, CrossSlope(0.0), probe_drag)["margin_n"])
    return {
        "closed_form_n": closed_form,
        "direct_difference_n": direct,
        "drag_cancels": abs(closed_form - direct) < 1e-9,
        "as_pct_of_available_traction": 100.0 * closed_form / (veh.mu * wb),
        "first_order_n": -wb * slope.S,
        "second_order_share_pct": (
            100.0 * (closed_form - (-wb * slope.S)) / closed_form
            if closed_form != 0.0 else 0.0),
    }


def sensitivity_table(vehicles=("yaris", "rogue", "silverado"),
                      slopes=SLOPES_DESIGN, mu: float = MU_PARKED) -> list[dict]:
    masses = {"yaris": 1100.0, "rogue": 1571.3, "silverado": 2270.0}
    rows = []
    for name in vehicles:
        v_sub = submerged_volume(name)
        if v_sub is None:
            rows.append({"vehicle": name, "error": "phase3.json unavailable"})
            continue
        veh = VehicleState(name, masses[name], v_sub, mu=mu)
        for S in slopes:
            d = margin_change_from_slope(veh, CrossSlope(S))
            rows.append({
                "vehicle": name,
                "slope_S": S,
                "W_minus_B_n": veh.submerged_weight_n,
                "buoyancy_pct": 100.0 * veh.buoyancy_fraction,
                "traction_available_n": mu * veh.submerged_weight_n,
                "dM_n": d["closed_form_n"],
                "dM_pct_of_traction": d["as_pct_of_available_traction"],
                "drag_cancels": d["drag_cancels"],
            })
    return rows


if __name__ == "__main__":
    print("fork_scene.cross_slope")
    print("=" * 92)

    print("\n1. THE TWO FORMULATIONS AT THE DESIGN SLOPES")
    hdr = (f"   {'S':>6} {'theta deg':>10} {'plane normal (T)':>34} "
           f"{'axis-aligned?':>14}")
    print(hdr)
    print("   " + "-" * (len(hdr) - 3))
    for S in SLOPES_DESIGN:
        cs = CrossSlope(S)
        n = cs.plane_normal()
        print(f"   {S:>6.3f} {cs.theta_deg:>10.4f} "
              f"({n[0]:+.9f}, {n[1]:+.1f}, {n[2]:+.9f}) "
              f"{'YES' if cs.is_axis_aligned() else 'NO':>14}")
    print(f"\n   gravity vector (G) at S=0.02: "
          f"{tuple(round(c, 9) for c in CrossSlope(0.02).gravity_vector())}")
    print(f"   |g'| = {math.hypot(*CrossSlope(0.02).gravity_vector()):.10f} m/s2 "
          f"(must equal {G} exactly; a tilt rotates gravity, it does not rescale it)")

    print("\n2. WHAT FORMULATION T COSTS")
    pen = launch_volume_penalty(64)
    print(f"   collider-kernel launch volume, tilted vs axis-aligned floor at g64: "
          f"{pen:.1f}x")
    print(f"   (one kernel's node-layer count, not a whole-run slowdown)")
    for S in SLOPES_DESIGN[1:]:
        b = bed_drop_across_domain(CrossSlope(S))
        print(f"   S={S:.2f}: bed drops {b['drop_m']:.4f} m across the "
              f"{CANONICAL_LIM_M:.4f} m tank = {100 * b['drop_over_depth']:.1f}% "
              f"of the {b['depth_m']:.4f} m depth")
    print("   -> formulation G is preferred: fast path kept, water volume held fixed.")

    print("\n3. THE STATIC SENSITIVITY, CLOSED FORM, NO SIMULATION NEEDED")
    rows = sensitivity_table()
    if rows and "error" in rows[0]:
        print("   phase3.json unavailable on this machine; cannot compute buoyancy.")
    else:
        hdr = (f"   {'vehicle':<11}{'S':>6}{'W-B (N)':>12}{'B/W %':>8}"
               f"{'mu(W-B) (N)':>13}{'dM (N)':>11}{'dM % of traction':>18}")
        print(hdr)
        print("   " + "-" * (len(hdr) - 3))
        for r in rows:
            print(f"   {r['vehicle']:<11}{r['slope_S']:>6.2f}"
                  f"{r['W_minus_B_n']:>12.1f}{r['buoyancy_pct']:>8.1f}"
                  f"{r['traction_available_n']:>13.1f}{r['dM_n']:>11.1f}"
                  f"{r['dM_pct_of_traction']:>17.2f}%")
        assert all(r["drag_cancels"] for r in rows), "drag did not cancel"
        print("\n   Every row: closed form == direct difference of two full balances")
        print("   at an arbitrary drag, so the drag term provably cancels and this")
        print("   sensitivity does NOT depend on the unresolved C_D envelope.")

    y = VehicleState("yaris", 1100.0, submerged_volume("yaris") or 0.0)
    d2 = margin_change_from_slope(y, CrossSlope(0.02))
    print(f"\n4. LEADING ORDER. At S=0.02 the first-order term -(W-B)*S is "
          f"{d2['first_order_n']:.1f} N")
    print(f"   against the exact {d2['closed_form_n']:.1f} N, so the "
          f"cos-th correction contributes {d2['second_order_share_pct']:.2f}%.")
    print("   The normal-load loss is second order in th; the added downslope")
    print("   weight is FIRST order. The slope term dominates, and it dominates")
    print("   for any mu, because mu multiplies only the second-order part.")
    print("=" * 92)
