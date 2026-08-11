#!/usr/bin/env python3
"""Yield-stress (Bingham / Herschel-Bulkley) CFL analysis for the standing-flood driver.

WHY THIS EXISTS
---------------
warpmpm's `newtonian()` material composes into Bingham and Herschel-Bulkley with
`.with_yield(tau_y)` and `.with_powerlaw(K, n)`, and those arguments are NOT ignored:
they are consumed by `kirchoff_stress_newtonian`, which computes

    eta_app = eta + tau_y / gd + K * gd**(n - 1)
    gd      = sqrt(2 * dev(D):dev(D) + eps**2),   eps = 0.02   (hardcoded)
    Cauchy  = -p I + 2 * eta_app * dev(D)

Verified live 2026-08-07 by direct read of the pinned install
`.venvs/canitford-mpm/lib/python3.12/site-packages/warpmpm/kernels/mpm_utils.py:32-54`
(pip direct_url.json pins it to kks32/mpm-engine @ 544c93dd).

So switching the 17-run driver to a yield-stress fluid is a one-line material change.
The hazard is the timestep, not the material. `sim_standing.py:149` computes

    term_viscous = 6.0 * water_eta / (water_density * dx * dx)

from `water_eta`, the NEWTONIAN viscosity, not from the apparent viscosity the kernel
actually uses. Because gd is floored at eps = 0.02, the kernel's low-shear apparent
viscosity is capped at

    eta_cap = eta + tau_y / 0.02 + K * 0.02**(n - 1) = eta + 50 * tau_y + K * 0.02**(n-1)

A yield stress of only a few tens of Pa therefore raises the true viscous CFL rate by
four orders of magnitude while the driver's own substep formula does not notice. The
settle loop at `sim_standing.py:156-158` runs the water at rest, where gd sits exactly
on the eps floor by construction, so this is the FIRST thing that would go wrong, not a
corner case.

WHAT THIS SCRIPT DOES
---------------------
Read-only, host-side, no GPU and no solver import. It:
  1. reproduces the as-run substep count for every row of data/all_runs_inventory.csv
     from the driver's own formula, as a self-test that the formula here is the one
     that ran;
  2. solves for tau_y_crit, the yield stress at which the viscous term overtakes the
     acoustic term and the uncorrected driver starts silently under-resolving dt;
  3. prints the corrected substep count for a proposed tau_y ladder, so the SU cost of
     a sweep is known before submission.

Usage:  python3 analysis/bingham_cfl_crossover.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INVENTORY = REPO / "data" / "all_runs_inventory.csv"

# Driver constants, all from renders/yaris_render_s1/sim_standing.py.
GAMMA = 1.1  # sim_standing.py:147, c = sqrt(1.1 * bulk / rho)
ACOUSTIC_C = 0.28  # :148, term_acoustic = c / (0.28 * dx)
VISCOUS_C = 6.0  # :149, term_viscous = 6 * eta / (rho * dx^2)
ADVECTIVE_C = 0.5  # :150, term_advective = v / (0.5 * dx)
FPS = 30  # :76 default
EPS_GD = 0.02  # kernel regularization floor, mpm_utils.py:41. NOT a driver constant.


def sound_speed(bulk: float, rho: float) -> float:
    return math.sqrt(GAMMA * bulk / rho)


def eta_cap(eta: float, tau_y: float = 0.0, K: float = 0.0, n: float = 1.0) -> float:
    """Kernel apparent viscosity at the regularization floor gd = eps.

    This is the LARGEST eta_app the kernel can produce, so it is the right value for a
    worst-case CFL bound. tau_y=0 and K=0 return eta unchanged, which is exactly what
    the current driver assumes.
    """
    out = eta + tau_y / EPS_GD
    if K:
        out += K * EPS_GD ** (n - 1.0)
    return out


def substeps(dx: float, bulk: float, rho: float, eta: float, velocity: float,
             tau_y: float = 0.0, K: float = 0.0, n: float = 1.0,
             fps: int = FPS) -> tuple[int, dict]:
    """The driver's own substep formula, with eta replaced by the kernel's eta_cap.

    Passing tau_y=0, K=0 reproduces sim_standing.py:147-153 exactly.
    """
    c = sound_speed(bulk, rho)
    e = eta_cap(eta, tau_y, K, n)
    terms = {
        "acoustic": c / (ACOUSTIC_C * dx),
        "viscous": VISCOUS_C * e / (rho * dx * dx),
        "advective": max(velocity, 1e-6) / (ADVECTIVE_C * dx),
    }
    rate = max(terms.values())
    return int(math.ceil(rate / fps)), {**terms, "rate": rate, "c": c, "eta_cap": e}


def tau_y_crit(dx: float, bulk: float, rho: float, eta: float) -> float:
    """Yield stress at which the viscous term equals the acoustic term.

    6 * (eta + tau_y/eps) / (rho dx^2) = c / (0.28 dx)
      =>  tau_y = eps * (c * rho * dx / (0.28 * 6) - eta)

    Above this, the uncorrected driver under-resolves dt without any warning: there is
    no CFL check and no NaN guard on the fluid path in core/solver.py:429-452.
    """
    c = sound_speed(bulk, rho)
    return EPS_GD * (c * rho * dx / (ACOUSTIC_C * VISCOUS_C) - eta)


def main() -> int:
    if not INVENTORY.exists():
        print(f"MISSING: {INVENTORY}")
        print("data/* is gitignored except the un-ignored stores; see .gitignore.")
        return 1

    rows = list(csv.DictReader(INVENTORY.open()))
    print(f"# Self-test: reproduce as-run substeps for {len(rows)} runs\n")
    print(f"{'run':<22} {'n_grid':>6} {'dx':>10} {'as-run':>7} {'recomputed':>11}  ok")
    print("-" * 72)

    ok = bad = 0
    seen: dict[int, dict] = {}
    for r in rows:
        try:
            dx = float(r["dx"])
            bulk = float(r["bulk_modulus"])
            eta = float(r["water_eta"])
            vel = float(r["velocity_ms"])
            n_grid = int(r["n_grid"])
            as_run = int(r["substeps"])
        except (KeyError, ValueError) as exc:
            print(f"{r.get('run', '?'):<22} SKIPPED, missing column: {exc}")
            continue
        got, _ = substeps(dx, bulk, 1000.0, eta, vel)
        good = got == as_run
        ok, bad = ok + good, bad + (not good)
        print(f"{r['run']:<22} {n_grid:>6} {dx:>10.6f} {as_run:>7} {got:>11}  "
              f"{'ok' if good else 'MISMATCH'}")
        seen.setdefault(n_grid, {"dx": dx, "bulk": bulk, "eta": eta, "vel": vel})

    print(f"\n  {ok} reproduced, {bad} mismatched")
    if bad:
        print("  A mismatch means the formula here is NOT the one that ran. Stop and")
        print("  re-read sim_standing.py:147-153 before trusting anything below.")
        return 1

    print("\n\n# Crossover: yield stress at which the uncorrected driver under-resolves dt\n")
    print(f"{'n_grid':>6} {'dx':>10} {'acoustic':>12} {'tau_y_crit (Pa)':>17}")
    print("-" * 50)
    for n_grid in sorted(seen):
        p = seen[n_grid]
        c = sound_speed(p["bulk"], 1000.0)
        print(f"{n_grid:>6} {p['dx']:>10.6f} {c / (ACOUSTIC_C * p['dx']):>12.2f} "
              f"{tau_y_crit(p['dx'], p['bulk'], 1000.0, p['eta']):>17.2f}")
    print("\n  The threshold FALLS as the grid refines, so a tau_y that is safe at g48")
    print("  can silently under-resolve at g96. Check the finest grid, not the coarsest.")

    if 64 not in seen:
        print("\nNo g64 row found; skipping the ladder.")
        return 0

    base = seen[64]
    print("\n\n# Proposed sweep cost at the canonical baseline "
          "(g64, depth 0.30 m, velocity 1.5 m/s)\n")
    base_ss, _ = substeps(base["dx"], base["bulk"], 1000.0, base["eta"], base["vel"])
    print(f"{'tau_y (Pa)':>11} {'eta (Pa.s)':>11} {'eta_cap':>12} {'substeps':>9} "
          f"{'x baseline':>11}  regime")
    print("-" * 78)

    # tau_y-only ladder (eta held at the as-run 1e-3 so tau_y is the only variable),
    # then two eta-coupled points where tau_y and eta rise together as they do with
    # sediment concentration. Regime labels are indicative, not cited: pin them to a
    # primary source before any of this reaches the paper.
    ladder = [
        (0.0, base["eta"], "control, reproduces the as-run g64 case"),
        (0.1, base["eta"], "clear water with trace fines"),
        (1.0, base["eta"], "turbid / low-concentration"),
        (3.0, base["eta"], "hyperconcentrated, low end"),
        (10.0, base["eta"], "hyperconcentrated"),
        (30.0, base["eta"], "hyperconcentrated, high end"),
        (100.0, base["eta"], "mud flow"),
        (3.1, 0.30, "eta-coupled pair, lower sediment fraction"),
        (40.0, 2.70, "eta-coupled pair, higher sediment fraction"),
    ]
    total = 0.0
    for ty, eta, label in ladder:
        ss, d = substeps(base["dx"], base["bulk"], 1000.0, eta, base["vel"], tau_y=ty)
        total += ss / base_ss
        flag = "  <-- ABOVE CROSSOVER" if d["viscous"] > d["acoustic"] else ""
        print(f"{ty:>11.1f} {eta:>11.3f} {d['eta_cap']:>12.2f} {ss:>9} "
              f"{ss / base_ss:>11.2f}  {label}{flag}")

    print(f"\n  Total ladder cost: {total:.1f} baseline-run-equivalents "
          f"({len(ladder)} runs, baseline = {base_ss} substeps).")

    print("\n\n# Herschel-Bulkley point (exercises the K and n path, which yield alone does not)\n")
    for ty, K, n in [(10.0, 5.0, 0.8), (0.0, 5.0, 0.8)]:
        ss, d = substeps(base["dx"], base["bulk"], 1000.0, 0.0, base["vel"],
                         tau_y=ty, K=K, n=n)
        print(f"  tau_y={ty:>5.1f}  K={K}  n={n}  eta=0  ->  eta_cap={d['eta_cap']:.2f}"
              f"  substeps={ss}  ({ss / base_ss:.2f}x baseline)")

    print("\n"
          "REQUIRED PAIRED EDIT, do not ship the material change without it:\n"
          "  sim_standing.py:149 currently reads\n"
          "      self.term_viscous = 6.0 * water_eta / (water_density * dx * dx)\n"
          "  and must become\n"
          "      eta_cap = water_eta + tau_y / 0.02 + hb_K * 0.02 ** (hb_n - 1.0)\n"
          "      self.term_viscous = 6.0 * eta_cap / (water_density * dx * dx)\n"
          "  Keep the 0.02 inline with a '# kernel eps, mpm_utils.py:41' comment. Do NOT\n"
          "  lift it into a shared constant: the kernel's copy lives in a vendored engine\n"
          "  at a pinned SHA, and a shared name would imply changing one changes both.\n"
          "  It is also NOT one of the 0.05 literals in CLAUDE.md item 13; do not sweep\n"
          "  it into that deduplication.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
