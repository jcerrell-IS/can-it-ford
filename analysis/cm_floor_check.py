#!/usr/bin/env python3
"""An EXTERNAL falsifier with a hard floor, run on data already on disk.

WHY THIS EXISTS. CLAUDE.md's AUGUST 4 AUDIT item 6 records that no gate in this
project is a physics validation: every one is a self-consistency or numerical
containment check, and G-3 compares against a constant derived from the same
pipeline, so it cannot fail for a reason external to the code. This one can.

THE CRITERION, AND ITS SOURCE. Baumgarten, Couchman and Kamrin (`10.1002/nme.7217`,
CC BY) grade MPM variants against a THEORETICAL MINIMUM on the fluid centre of
mass, their equation 73, with `y_CM = sum(y_p m_p) / sum(m_p)`. In their
collapsing-column benchmark the bound is `y_CM >= 2/3 m`; reading their Figure
25A, standard uGIMP ends near 0.40 against that 0.667 bound by t = 10 s while
the SPH-like point adjustment and the delta-correction stay consistent with it.

DO NOT COPY THEIR NUMBER. The 2/3 belongs to their geometry. What transfers is
the METHOD: for a fluid of fixed volume confined above a floor, the centre of
mass has a floor set by volume conservation and the container, and nobody
chooses a tolerance. Here that floor is the centre of mass of the same volume
lying perfectly flat over the tank:

    h_flat  = V_water / A_tank
    z_cm_min = z_bottom + h_flat / 2

Every configuration with a free surface, a wave or a displaced body sits higher.

FOUR THINGS THAT MAKE THE BOUND CONSERVATIVE, ON PURPOSE. Each was found by the
bound failing 23 of 23 runs on a first pass, which is the uniform-result
signature this project has learned to distrust:

1. `V_water` is `(A_tank - A_hull) * depth`, taken from the driver's own
   initialisation. An earlier version voxelised frame 0 and counted occupied
   cells, which overcounts by the partially-filled boundary layer: measured
   18.4 percent high at g64, and that alone manufactured a violation.
2. `A_hull` is the hull's plan area inside the water band, measured from
   `veh_particles_scene0`, not assumed. Ignoring it inflates `V_water` by about
   11 percent and inflates the bound with it.
3. `z_bottom` is the MEASURED minimum water z at frame 0, not the `floor`
   scalar. The driver clamps particles at `floor - 0.25*dx`, so 2334 of 48367
   particles at g64 sit below `floor` at rest, before any dynamics. `floor` is
   not the bottom of the water column and using it as the datum is wrong.
4. The fluid is WEAKLY COMPRESSIBLE, sound speed about 13 m/s, so a small
   negative margin is physical compression and not a fault. The margin is
   therefore reported as a fraction of depth, and its resolution dependence is
   the diagnostic: a compression effect should be resolution-independent, a
   discretisation artifact should shrink with dx.

A PASS IS NOT A VALIDATION. It is a failure to falsify against a deliberately
weak bound. That is still more than any existing gate offers, because this bound
comes from outside the pipeline.

THE MINIMUM IS AN EXTREMAL QUANTITY. Per the settle work's third-class rule,
classify the quantity before choosing a window: an extremum is not a mean and
carries no convergence claim. Both the full-record minimum and the
post-transient minimum are reported, and they answer different questions.

RUN IT WITH BLENDER'S PYTHON, the only interpreter on this Mac carrying numpy
(2.3.4, verified 2026-08-20; all five system interpreters fail `import numpy`):

    /opt/homebrew/bin/blender -b --python analysis/cm_floor_check.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTLE_FRAMES = 8       # the driver's own settle length, sim_standing.py:154
INVENTORY = os.path.join(REPO, "data", "all_runs_inventory.csv")


def canonical_runs() -> set[str]:
    """The 17 gated runs, read from the inventory rather than pattern-matched.

    This matters for the headline. `renders/yaris_render_s1/m1100`, `m1609` and
    `m2337` sit on disk beside the canonical runs, are NOT among the 17, and are
    the three largest violations in the set by a factor of three. Reporting
    "14 of 20 violate" without that split would put non-canonical runs into a
    statement about the gated ones.
    """
    if not os.path.isfile(INVENTORY):
        return set()
    out = set()
    with open(INVENTORY, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i == 0:
                continue
            name = line.split(",")[0].strip()
            if name:
                out.add(name)
    return out


def scalar(z, key, default=None):
    if key not in z:
        return default
    v = z[key]
    return float(v) if v.shape == () else v


def plan_area(pts_xy: np.ndarray, cell: float) -> float:
    """Occupied plan area, by binning xy at `cell` and counting unique bins."""
    if len(pts_xy) == 0 or not cell:
        return 0.0
    b = np.floor(pts_xy / cell).astype(np.int64)
    return len(np.unique(b, axis=0)) * cell * cell


def analyse(path: str) -> dict:
    z = np.load(path)
    if "water" not in z:
        return {"skipped": path}
    w = z["water"]
    nfr, npart, _ = w.shape
    dx = scalar(z, "dx")
    depth = scalar(z, "depth")
    floor = scalar(z, "floor", 0.0)
    if not dx or not depth:
        return {"skipped": path}

    f0 = w[0]
    z_bottom = float(f0[:, 2].min())
    a_tank = plan_area(f0[:, :2], dx)

    # Hull plan area inside the water band, measured from the rigid cloud.
    a_hull = 0.0
    if "veh_particles_scene0" in z:
        v = z["veh_particles_scene0"]
        band = v[(v[:, 2] >= z_bottom) & (v[:, 2] <= z_bottom + depth)]
        a_hull = plan_area(band[:, :2], dx)

    v_water = max(a_tank - a_hull, 0.0) * depth
    h_flat = v_water / a_tank if a_tank else float("nan")
    z_cm_min = z_bottom + h_flat / 2.0

    z_cm = w[:, :, 2].mean(axis=1)
    margin = z_cm - z_cm_min
    tail = margin[SETTLE_FRAMES:] if nfr > SETTLE_FRAMES else margin

    clamp = floor - 0.25 * dx
    below_clamp = (w[:, :, 2] < clamp).sum(axis=1)
    below_floor0 = int((f0[:, 2] < floor).sum())

    return {
        "run": os.path.basename(os.path.dirname(path)),
        "path": os.path.relpath(path, REPO),
        "frames": int(nfr), "n_water": int(npart),
        "dx": round(dx, 6), "depth": round(depth, 6),
        "z_bottom_m": round(z_bottom, 6),
        "floor_scalar_m": round(floor, 6),
        "A_tank_m2": round(a_tank, 4), "A_hull_in_band_m2": round(a_hull, 4),
        "V_water_m3": round(v_water, 4), "h_flat_m": round(h_flat, 6),
        "z_cm_min_bound_m": round(z_cm_min, 6),
        "z_cm_first_m": round(float(z_cm[0]), 6),
        "z_cm_last_m": round(float(z_cm[-1]), 6),
        "margin_full_record_m": round(float(margin.min()), 6),
        "margin_full_record_frac_depth": round(float(margin.min()) / depth, 5),
        "margin_min_frame": int(margin.argmin()),
        "margin_post_settle_m": round(float(tail.min()), 6),
        "violates_full_record": bool(margin.min() < 0),
        "violates_post_settle": bool(tail.min() < 0),
        "particles_below_floor_scalar_frame0": below_floor0,
        "max_particles_below_clamp": int(below_clamp.max()),
        "frac_below_clamp_max": round(float(below_clamp.max()) / npart, 6),
    }


def main() -> int:
    canon = canonical_runs()
    seen, rows = set(), []
    for p in sorted(glob.glob(os.path.join(REPO, "renders", "**", "rollout.npz"),
                              recursive=True)):
        r = analyse(p)
        if "skipped" in r:
            continue
        if r["run"] in seen:          # the same run appears under two paths
            continue
        seen.add(r["run"])
        r["canonical"] = r["run"] in canon
        rows.append(r)

    print("CENTRE-OF-MASS FLOOR CHECK")
    print("method after Baumgarten, Couchman & Kamrin 10.1002/nme.7217 eq 73")
    print("bound: z_cm >= z_bottom + (A_tank - A_hull)*depth / (2*A_tank)\n")
    hdr = (f"{'run':22} {'canon':>6} {'dx':>7} {'z_cm(0)':>8} {'bound':>8} "
           f"{'margin':>8} {'/depth':>8} {'@fr':>4} {'verdict':>9}")
    print(hdr)
    print("-" * len(hdr))
    viol = 0
    for r in sorted(rows, key=lambda r: (not r["canonical"], r["dx"], r["run"])):
        v = "VIOLATES" if r["violates_full_record"] else "ok"
        viol += r["violates_full_record"]
        print(f"{r['run'][:22]:22} {'yes' if r['canonical'] else 'NO':>6} "
              f"{r['dx']:7.4f} {r['z_cm_first_m']:8.4f} "
              f"{r['z_cm_min_bound_m']:8.4f} {r['margin_full_record_m']:8.4f} "
              f"{r['margin_full_record_frac_depth']:8.4f} "
              f"{r['margin_min_frame']:4d} {v:>9}")
    cr = [r for r in rows if r["canonical"]]
    print()
    print(f"CANONICAL runs on disk                        : {len(cr)} of 17")
    print(f"  violating over the FULL record              : "
          f"{sum(r['violates_full_record'] for r in cr)}")
    print(f"  violating after the settle transient        : "
          f"{sum(r['violates_post_settle'] for r in cr)}")
    print(f"  worst canonical margin, fraction of depth   : "
          f"{min((r['margin_full_record_frac_depth'] for r in cr), default=0):.4f}")
    print(f"NON-canonical runs also on disk               : {len(rows)-len(cr)}")
    print(f"  violating over the FULL record              : "
          f"{viol - sum(r['violates_full_record'] for r in cr)}")
    print()
    print("A pass is NOT a validation. It is a failure to falsify against a")
    print("bound made conservative four separate ways, listed in the docstring.")
    print("The margin is signed and comparable across runs as a fraction of")
    print("depth; its resolution dependence is the diagnostic, not its sign.")

    out = os.path.join(REPO, "data", "cm_floor_check.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({
            "criterion": "z_cm >= z_bottom + (A_tank - A_hull)*depth/(2*A_tank)",
            "source": "10.1002/nme.7217 eq 73, method transferred not number",
            "settle_frames_discarded_for_post_settle": SETTLE_FRAMES,
            "n_runs": len(rows),
            "n_canonical": sum(1 for r in rows if r["canonical"]),
            "n_violating_full_record": viol,
            "n_canonical_violating_full_record":
                sum(1 for r in rows if r["canonical"] and r["violates_full_record"]),
            "n_canonical_violating_post_settle":
                sum(1 for r in rows if r["canonical"] and r["violates_post_settle"]),
            "n_violating_post_settle": sum(r["violates_post_settle"] for r in rows),
            "runs": rows}, fh, indent=1)
        fh.write("\n")
    print(f"\nwrote {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
