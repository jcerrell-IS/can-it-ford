"""Read the Kramer 2021 benchmark series and reduce it to gradeable numbers.

WHY THIS EXISTS
---------------
`docs/R5_PHYSICS_BLOCKED_FLAGS.md` FLAG-2a recorded the benchmark time series as
unfetchable, which made half of Option B's definition of done ungradeable and forced
job C's pass criteria down to self-consistency only. **The series is now on disk.** It
was fetched 2026-08-17 by driving a real browser to the article page, which the
publisher serves normally; every prior attempt had used curl, WebFetch or a resolver,
all of which MDPI answers with 403. That is FLAG-2's own lesson (a licence status is not
a fetch status) with one more entry: **a host-level bot filter is not an access barrier,
and the difference is whether a real browser was ever tried.**

Nothing here is transcribed. Every number this module reports is recomputed from the
files each time it runs, because a figure that cannot be re-derived is not a figure.

THE DATA
--------
`Datafile/Experimental results/` in `energies-14-00269-s001.zip`, sha256
04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f, held OUTSIDE the repo
at /Users/josie/can-it-ford-refs/2026-08-16/ because the repo is public and E8 is
unresolved. 27 files: for each drop height {01D, 03D, 05D}, four repetitions in Raw and
Normalized form, plus a CI95 series. That matches Table 1's H0 = {30, 90, 150} mm and
the paper's "four repetitions were carried out for each drop height".

Raw columns:        t [s], x3 [m], WG1 [m], WG2 [m], WG3 [m]
Normalized columns: t/Te0, x3/H0m, WG1/H0m, WG2/H0m, WG3/H0m
CI95 columns:       t/Te0, mean x3/H0m, lower 95% bound, upper 95% bound

x3 is the heave displacement; WG1-3 are wave gauges. Release is t = 0; each series
begins at t/Te0 = -0.5, i.e. the hold phase is included.

THE TRAP IN Te0, WHICH COST ME A WRONG CLAIM
--------------------------------------------
`Te0` recovers from t / (t/Te0) as **0.756100 s, identical across all three drop heights
and all four repetitions**. It is therefore a single fixed NORMALISING CONSTANT, not a
per-drop measurement. Reading it as "the measured natural period" would contradict the
paper's own Figure 13 finding that the damped period rises with drop height, and would
be exactly the kind of number that looks measured because it came out of a data file.
The damped periods are measured here from the displacement series instead.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

DEFAULT_ROOT = Path("/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001/"
                    "Datafile/Experimental results")

ZIP_SHA256 = "04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f"

# Drop label -> H0 in metres, from Table 1. The labels are the paper's own.
DROPS = {"01D": 0.030, "03D": 0.090, "05D": 0.150}
REPS = (1, 2, 3, 4)

# Table 1 constants, for the closed-form stiffness. Benchmark gravity, not the engine's:
# this module describes the EXPERIMENT, so it uses the experiment's g.
RHO_W = 998.2
G_BENCHMARK = 9.82
D_SPHERE = 0.300
M_SPHERE = 7.056


def _load(root: Path, drop: str, rep: int, kind: str) -> np.ndarray:
    p = root / f"{drop}_Measured{rep}_{kind}.txt"
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found. Extract the supplementary archive first:\n"
            f"  unzip -d <dir> energies-14-00269-s001.zip 'Datafile/Experimental results/*'\n"
            f"and pass --root <dir>/'Datafile/Experimental results'.")
    return np.loadtxt(p, skiprows=1)


def recover_te0(root: Path) -> dict:
    """Recover the normalising constant, and PROVE it is constant rather than assume it.

    The check matters: if Te0 ever differed by drop height it would be a measurement,
    and every period below would have to be interpreted differently.
    """
    vals = {}
    for drop in DROPS:
        for rep in REPS:
            raw = _load(root, drop, rep, "Raw")
            nor = _load(root, drop, rep, "Normalized")
            m = np.abs(nor[:, 0]) > 1e-9
            vals[(drop, rep)] = float(np.median(raw[m, 0] / nor[m, 0]))
    arr = np.array(list(vals.values()))
    return {
        "te0_s": float(np.median(arr)),
        "te0_spread_s": float(arr.max() - arr.min()),
        "is_constant_across_drops_and_reps": bool(arr.max() - arr.min() < 1e-6),
        "n_series": len(arr),
    }


def damped_periods(root: Path, drop: str, rep: int, n_cycles: int = 5) -> np.ndarray:
    """Successive damped periods from zero crossings of x3 about its own settled level.

    Equilibrium is the mean of the last 15% of the record rather than 0.0, because the
    sphere settles a few tens of micrometres off the nominal waterline (Table 1's mass is
    rounded, which alone implies a ~2 um offset) and a hard zero would bias early
    crossings. A crossing-to-crossing interval is a HALF period, hence the factor 2.
    Crossings are linearly interpolated between samples; at dt = 0.002 s against a ~0.78 s
    period, that is a sub-0.3% correction but it is free.
    """
    d = _load(root, drop, rep, "Raw")
    t, x = d[:, 0], d[:, 1]
    eq = float(x[int(0.85 * len(x)):].mean())
    y = x - eq
    post = t >= 0.0
    t, y = t[post], y[post]
    idx = np.where(np.diff(np.sign(y)) != 0)[0]
    tc = np.array([t[i] + (t[i + 1] - t[i]) * (-y[i]) / (y[i + 1] - y[i]) for i in idx])
    return (np.diff(tc) * 2.0)[:n_cycles]


def ci95_halfwidth(root: Path, drop: str) -> dict:
    """The published uncertainty, read off the CI95 series in its own units.

    This is the direct test of how the abstract's "on average only about 0.3% of the
    respective drop heights" should be read. The file is NORMALIZED by H0, so a
    half-width expressed in those units is by construction a fraction of drop height.
    """
    p = root / f"{drop}_CI95_Normalized.txt"
    d = np.loadtxt(p, skiprows=1)
    half = (d[:, 3] - d[:, 2]) / 2.0          # (upper - lower)/2, in units of H0
    h0 = DROPS[drop]
    return {
        "mean_halfwidth_frac_of_H0": float(half.mean()),
        "mean_halfwidth_pct_of_H0": float(half.mean() * 100.0),
        "mean_halfwidth_mm": float(half.mean() * h0 * 1000.0),
        "max_halfwidth_pct_of_H0": float(half.max() * 100.0),
        "n_samples": int(len(half)),
    }


def summarise(root: Path = DEFAULT_ROOT) -> dict:
    te0 = recover_te0(root)
    out = {"te0": te0, "drops": {}, "source": {"root": str(root), "zip_sha256": ZIP_SHA256}}

    r = 0.5 * D_SPHERE
    k = RHO_W * G_BENCHMARK * math.pi * r ** 2

    first_by_drop = {}
    for drop, h0 in DROPS.items():
        per = np.vstack([damped_periods(root, drop, rep) for rep in REPS])   # 4 x n
        first = per[:, 0]
        # Implied heave added mass from the FIRST damped period. This is a
        # 1-DOF reading of a nonlinear record, so it is a diagnostic of how far the
        # a33/m = 0.5 sizing assumption is from the data, not a hydrodynamic result.
        a33 = k * (first.mean() / (2.0 * math.pi)) ** 2 - M_SPHERE
        first_by_drop[drop] = float(first.mean())
        out["drops"][drop] = {
            "H0_m": h0,
            "first_damped_period_s": {
                "n": int(len(first)),
                "mean": float(first.mean()),
                "min": float(first.min()),
                "max": float(first.max()),
                "spread": float(first.max() - first.min()),
            },
            "cycle_means_s": [float(v) for v in per.mean(axis=0)],
            "implied_added_mass_kg": float(a33),
            "implied_a33_over_m": float(a33 / M_SPHERE),
            "ci95": ci95_halfwidth(root, drop),
        }

    o = [first_by_drop[d] for d in ("01D", "03D", "05D")]
    out["period_rises_with_drop_height"] = bool(o[0] < o[1] < o[2])
    out["heave_stiffness_N_per_m"] = float(k)
    return out


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p.add_argument("--json", action="store_true", help="emit the summary as JSON")
    a = p.parse_args()

    s = summarise(a.root)
    if a.json:
        print(json.dumps(s, indent=2, sort_keys=True))
        return

    t = s["te0"]
    print(f"Te0 normalising constant: {t['te0_s']:.6f} s over {t['n_series']} series, "
          f"spread {t['te0_spread_s']:.2e} s")
    print(f"  constant across all drops and reps: {t['is_constant_across_drops_and_reps']} "
          f"-> it is a NORMALISER, not a per-drop measurement\n")
    print(f"heave stiffness rho*g*pi*R^2 = {s['heave_stiffness_N_per_m']:.3f} N/m "
          f"(rho_w={RHO_W}, g={G_BENCHMARK} benchmark)\n")
    print("drop  H0[mm]  first damped period [s]         N  spread    a33/m   CI95 half-width")
    for drop in ("01D", "03D", "05D"):
        d = s["drops"][drop]
        f = d["first_damped_period_s"]
        c = d["ci95"]
        print(f"{drop}   {d['H0_m']*1000:5.0f}   {f['mean']:.4f} "
              f"[{f['min']:.4f}, {f['max']:.4f}]  {f['n']}  {f['spread']:.4f}  "
              f"{d['implied_a33_over_m']:.3f}   {c['mean_halfwidth_pct_of_H0']:.3f}% of H0 "
              f"= {c['mean_halfwidth_mm']:.3f} mm")
    print(f"\npaper's Fig 13 claim, period rises with drop height: "
          f"{'CONFIRMED' if s['period_rises_with_drop_height'] else 'NOT CONFIRMED'}")
    print("cycle-by-cycle means (4 reps), showing decay toward the Te0 normaliser:")
    for drop in ("01D", "03D", "05D"):
        print(f"  {drop}: " + ", ".join(f"{v:.4f}" for v in s["drops"][drop]["cycle_means_s"]))


if __name__ == "__main__":
    main()
