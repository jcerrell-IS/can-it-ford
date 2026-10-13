#!/usr/bin/env python3
"""Physics checks: analytical solutions, recorded-data invariants, and metamorphic relations.

    GATE 1  closed-form channel flows (Poiseuille, Couette) and a harness to compare solver output
    GATE 2  invariants of the recorded runs: finite, bounded, and holding the particle counts recorded
    GATE 3  metamorphic relations between runs that differ in one input (grid or mass)

WHAT THIS FILE CAN AND CANNOT DO
--------------------------------
Nothing here runs the GPU solver. Two consequences, both deliberate:

  * GATE 1 checks the closed-form solutions themselves (that each solves its governing equation and
    meets its boundary conditions) and holds the comparison harness. The comparison against solver
    output SKIPS, and is reported as a skip, until a solver profile is supplied. A check that passes
    when it cannot run gives false assurance.
  * GATES 2 and 3 read the recorded output of the 17 gated coupled runs, copied into `tests/data/`
    (see `tests/data/README.md`). Those runs set all the water moving in one step inside a closed
    tank, so they record a start-up surge, not a steady current, and their FORD and NO-FORD labels
    are withdrawn as verdicts (`FINDINGS.md`). The checks treat them as recorded data: they catch a
    corrupted, truncated or silently changed record. They are not evidence that the physics is right.

Poiseuille and Couette flow have exact closed-form solutions, which is why they are common
verification cases for particle fluid solvers; Sun et al. 2018 compare the material point method and
smoothed particle hydrodynamics on fluid flow problems (Progress in Computational Fluid Dynamics
18(1), doi:10.1504/PCFD.2018.089497).

Standard library only. Runs under pytest and standalone:
    python3 tests/test_physics_gates.py
Set CANFORD_RUNS_DIR to a folder of full run outputs (<run>/rollout.npz) to also re-read the
rollout files themselves.
"""
from __future__ import annotations

import ast
import csv
import json
import math
import os
import sys
import unittest
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(REPO, "tests", "data")
RUNS = os.path.join(FIXTURES, "runs")
INVENTORY = os.path.join(REPO, "data", "all_runs_inventory.csv")
FULL_RUNS = os.environ.get("CANFORD_RUNS_DIR", "")

# Physical anchors. Any drift here is itself a defect.
G_ACCEL = 9.81          # m/s^2, hardcoded in the solver core, not a default
RHO_WATER = 1000.0      # kg/m^3
RHO_HULL = 310.494      # kg/m^3: 1100 kg over the hull's 3.542739 m^3 (hull_m3 in the inventory)
SWEEP_V_MAX = 3.0       # m/s, upper end of the velocity sweep
SWEEP_D_MAX = 1.0       # m, upper end of the depth sweep

Skip = unittest.SkipTest   # pytest and the standalone runner below both report this as a skip


def _skip(msg: str) -> None:
    raise Skip(msg)


# --------------------------------------------------------------- GATE 1
# Analytical solutions. Plates at y = 0 and y = H.

def poiseuille_u(y: float, H: float, G: float, mu: float) -> float:
    """Plane Poiseuille: both plates static, driven by pressure gradient G."""
    return (G / (2.0 * mu)) * y * (H - y)


def couette_u(y: float, H: float, U: float, G: float = 0.0,
              mu: float = 1.0) -> float:
    """Plane Couette: top plate moves at U. G != 0 gives the combined profile."""
    return U * y / H + (G / (2.0 * mu)) * y * (H - y)


def test_poiseuille_satisfies_its_governing_equation():
    """mu * d2u/dy2 = -G must hold pointwise, checked by finite difference.

    This is the real verification: the closed form is only trustworthy if it
    solves the ODE it claims to solve.
    """
    H, G, mu = 0.1, 12.0, 1.0e-3
    h = H / 2000.0
    for frac in (0.2, 0.35, 0.5, 0.65, 0.8):
        y = frac * H
        d2u = (poiseuille_u(y + h, H, G, mu) - 2 * poiseuille_u(y, H, G, mu)
               + poiseuille_u(y - h, H, G, mu)) / (h * h)
        residual = mu * d2u + G
        assert abs(residual) < 1e-6 * G, (
            f"Poiseuille residual {residual:.3e} at y/H={frac}")


def test_poiseuille_no_slip_and_peak():
    """No-slip at both walls; peak at mid-channel equal to G H^2 / (8 mu)."""
    H, G, mu = 0.1, 12.0, 1.0e-3
    assert abs(poiseuille_u(0.0, H, G, mu)) < 1e-15
    assert abs(poiseuille_u(H, H, G, mu)) < 1e-15
    expect = G * H * H / (8.0 * mu)
    assert math.isclose(poiseuille_u(H / 2, H, G, mu), expect, rel_tol=1e-12)


def test_poiseuille_mean_is_two_thirds_of_peak():
    """Analytic mean/peak ratio is exactly 2/3. Integrated numerically."""
    H, G, mu = 0.1, 12.0, 1.0e-3
    n = 20000
    total = sum(poiseuille_u((i + 0.5) * H / n, H, G, mu) for i in range(n))
    mean = total / n
    peak = G * H * H / (8.0 * mu)
    assert math.isclose(mean / peak, 2.0 / 3.0, rel_tol=1e-6), mean / peak


def test_couette_is_linear_without_pressure_gradient():
    """Pure Couette must be exactly linear between the plates."""
    H, U = 0.1, 0.5
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert math.isclose(couette_u(frac * H, H, U), U * frac, rel_tol=1e-12)


def test_couette_superposes_with_poiseuille():
    """Stokes flow is linear, so the combined profile is the exact sum."""
    H, U, G, mu = 0.1, 0.5, 12.0, 1.0e-3
    for frac in (0.15, 0.5, 0.85):
        y = frac * H
        assert math.isclose(
            couette_u(y, H, U, G, mu),
            couette_u(y, H, U) + poiseuille_u(y, H, G, mu), rel_tol=1e-12)


def compare_profile(sim: list[tuple[float, float]], H: float, G: float,
                    mu: float) -> float:
    """Compare (y, u) solver samples against Poiseuille. Returns L2 error %."""
    if not sim:
        _skip("no solver profile supplied")
    peak = G * H * H / (8.0 * mu)
    num = sum((u - poiseuille_u(y, H, G, mu)) ** 2 for y, u in sim)
    return math.sqrt(num / len(sim)) / peak * 100.0


def test_solver_profile_against_analytical():
    """The Poiseuille comparison against solver output. SKIPS until a profile exists.

    No solver channel-flow profile has been produced yet, so this reports a skip. To arm it, put a
    two-column CSV of (y, u) samples at `tests/data/poiseuille_profile.csv`. The solver fork has its
    own analytic benchmarks (`tests/test_analytic_benchmarks.py` in jcerrell-IS/mpm-engine: a block
    on a frictional incline, a hydrostatic column, an elastic bar); they need a GPU, and their own
    docstring says two of them route around known solver problems, so none is a free-surface channel
    flow check.
    """
    p = os.path.join(FIXTURES, "poiseuille_profile.csv")
    if not os.path.isfile(p):
        _skip("no solver Poiseuille profile at tests/data/poiseuille_profile.csv; "
              "the analytical side is checked above, the solver comparison is not")
    rows = []
    with open(p, newline="", encoding="utf-8") as fh:
        for r in csv.reader(fh):
            try:
                rows.append((float(r[0]), float(r[1])))
            except (ValueError, IndexError):
                continue
    err = compare_profile(rows, H=0.1, G=12.0, mu=1.0e-3)
    assert err < 10.0, f"Poiseuille L2 error {err:.2f}% exceeds 10%"


# --------------------------------------------------------------- GATE 2
# Invariants of the recorded runs.

def inventory() -> dict[str, dict[str, str]]:
    with open(INVENTORY, newline="", encoding="utf-8") as fh:
        return {r["run"]: r for r in csv.DictReader(fh)}


def npz_shapes(path: str) -> dict[str, list[int]]:
    """Array shapes from an .npz WITHOUT numpy, by parsing the .npy headers.

    An .npz is a zip of .npy members, and every .npy carries its shape in a literal dict header.
    """
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith(".npy"):
                continue
            with z.open(name) as f:
                if f.read(6) != b"\x93NUMPY":
                    continue
                major = f.read(2)[0]
                hlen = int.from_bytes(f.read(2 if major == 1 else 4), "little")
                hdr = ast.literal_eval(f.read(hlen).decode("latin1").strip())
                out[name[:-4]] = list(hdr["shape"])
    return out


def test_fixture_runs_match_the_inventory():
    """The fixture holds exactly the 17 runs the inventory lists, each with a full 3 s record."""
    inv = inventory()
    have = sorted(d for d in os.listdir(RUNS) if os.path.isfile(os.path.join(RUNS, d, "metrics.csv")))
    assert have == sorted(inv), f"fixture runs {have} differ from inventory runs {sorted(inv)}"
    for run in have:
        with open(os.path.join(RUNS, run, "metrics.csv"), newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.DictReader(fh))
        assert n == int(inv[run]["frames"]) + 1, f"{run}: {n} rows, expected frames + 1"


def test_rollouts_hold_the_particle_counts_each_run_recorded():
    """Every frame of every rollout holds the particle counts the run wrote at load.

    Two separate records are compared: the array shapes inside each run's `rollout.npz` (pinned in
    `tests/data/rollout_shapes.json`, re-read from the files when CANFORD_RUNS_DIR is set) and the
    counts the run wrote to its summary, carried in `data/all_runs_inventory.csv`. A truncated
    rollout, a dropped frame or a mismatched run folder fails here.
    """
    inv = inventory()
    with open(os.path.join(FIXTURES, "rollout_shapes.json"), encoding="utf-8") as fh:
        pinned = json.load(fh)
    assert sorted(pinned) == sorted(inv)
    for run, rec in pinned.items():
        shapes = rec["arrays"]
        n_w, n_v, frames = (int(inv[run][k]) for k in ("n_water", "n_vehicle", "frames"))
        assert shapes["water"] == [frames, n_w, 3], (run, shapes["water"], n_w, frames)
        assert shapes["speed"] == [frames, n_w], (run, shapes["speed"])
        assert shapes["R"] == [frames, 3, 3] and shapes["t"] == [frames, 3], run
        assert shapes["veh_particles_scene0"] == [n_v, 3], (run, shapes["veh_particles_scene0"], n_v)
    if FULL_RUNS:
        for run, rec in pinned.items():
            p = os.path.join(FULL_RUNS, run, "rollout.npz")
            assert os.path.isfile(p), f"CANFORD_RUNS_DIR set but {p} is missing"
            assert npz_shapes(p) == rec["arrays"], f"{run}: rollout differs from the pinned shapes"


def test_metrics_are_finite_and_physically_bounded():
    """Every logged history is finite and inside a physical band.

    A NaN or a runaway velocity is the signature of a blown-up run, and a label read from the
    record would happily classify one.
    """
    bad = []
    n = 0
    for run in sorted(os.listdir(RUNS)):
        p = os.path.join(RUNS, run, "metrics.csv")
        if not os.path.isfile(p):
            continue
        with open(p, newline="", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                n += 1
                for k, v in row.items():
                    if v in (None, ""):
                        continue
                    try:
                        x = float(v)
                    except ValueError:
                        continue
                    if math.isnan(x) or math.isinf(x):
                        bad.append(f"{run}:{k}=non-finite")
                    # 10 m/s is 3.3x the sweep cap, so this catches a blow-up
                    # without firing on ordinary transient overshoot.
                    if k in ("vmag", "vx", "vy", "vz") and abs(x) > 10.0:
                        bad.append(f"{run}:{k}={x:.3g}")
    assert n > 0, "no metrics rows read"
    assert not bad, f"{len(bad)} violations, first 5: {bad[:5]}"


def test_unit_anchors_are_self_consistent():
    """The declared constants must satisfy the relations they take part in.

    Catches a units slip: the drift threshold of 0.05 m and the speed threshold of 0.05 m/s share a
    numeral, so an edit by value can silently change a label.
    """
    assert 9.7 < G_ACCEL < 9.9
    assert math.isclose(RHO_WATER, 1000.0)
    # The hull must float-or-sink consistently with its own density ratio.
    ratio = RHO_HULL / RHO_WATER
    assert 0.0 < ratio < 1.0, "hull denser than water would never float"
    # Submerged fraction at neutral buoyancy equals the density ratio.
    assert math.isclose(ratio, 0.310494, rel_tol=1e-6)
    inv = inventory()
    for run, r in inv.items():
        assert math.isclose(float(r["hull_m3"]), 3.542739, rel_tol=1e-9), run
    assert math.isclose(1100.0 / 3.542739, RHO_HULL, rel_tol=1e-6)
    # The sweep bounds must bracket the canonical realized depth of 0.2944294 m.
    assert 0.0 < 0.2944294 < SWEEP_D_MAX
    assert SWEEP_V_MAX == 3.0


# --------------------------------------------------------------- GATE 3
# Metamorphic relations. A metamorphic test asserts a RELATION between runs,
# which is how you test a solver whose exact answer is unknown.

def load_metric(path: str, col: str) -> list[float]:
    out = []
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            try:
                out.append(float(row[col]))
            except (KeyError, TypeError, ValueError):
                pass
    return out


def slide_margin(run_dir: str) -> int | None:
    """Longest run of frames with drift > 0.05 m AND speed > 0.05 m/s, minus the 3 frames required.

    A margin of 0 or more is the recorded "moved" label; below 0 is "stayed".
    """
    p = os.path.join(run_dir, "metrics.csv")
    if not os.path.isfile(p):
        return None
    d, v = load_metric(p, "dmag"), load_metric(p, "vmag")
    if len(d) < 12 or len(v) < 12:
        return None
    best = run = 0
    for a, b in zip(d, v):
        if a > 0.05 and b > 0.05:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best - 3


def _grid_dirs(mass: str) -> dict[str, str]:
    return {g: os.path.join(RUNS, f"{g}_{mass}")
            for g in ("g48", "g64", "g96")
            if os.path.isdir(os.path.join(RUNS, f"{g}_{mass}"))}


def test_recorded_move_label_is_the_same_on_all_three_grids():
    """Same scene, three grids: the recorded move-or-stay label must not differ between them.

    This pins the recorded start-up surge labels (withdrawn as verdicts), so a change to the records
    or to the rule that reads them is caught here rather than discovered in a figure. The size of the
    motion does change with the grid, by 1.9 to 4.9 times, and is not checked here.
    """
    ran = 0
    for mass in ("m1100", "m1609", "m2337"):
        dirs = _grid_dirs(mass)
        margins = {g: slide_margin(p) for g, p in dirs.items()}
        margins = {g: m for g, m in margins.items() if m is not None}
        if len(margins) < 2:
            continue
        labels = {g: ("moved" if m >= 0 else "stayed") for g, m in margins.items()}
        ran += 1
        assert len(set(labels.values())) == 1, (
            f"{mass}: recorded label differs across grids {labels} (margins {margins})")
    if not ran:
        _skip("no grid-paired runs available")


def test_heavier_vehicle_moves_no_more():
    """Mass ordering. Same hull, more mass: more net weight on the floor, so more friction.

    With the hull volume fixed, buoyancy is the same at every mass, so the net normal load rises
    with mass. At a fixed grid, the margin by which the record meets the move rule must therefore
    not increase with mass. This is a monotonicity relation independent of the absolute answer.
    """
    ran = 0
    # g48 IS EXCLUDED, on evidence. Measured margins:
    #     g48   m1100 22   m1609 25   m2337 19    NOT monotone
    #     g64   m1100 41   m1609 28   m2337  8    monotone
    #     g96   m1100 16   m1609  7   m2337  1    monotone
    # All three g48 runs fail the floor check P-3 (FINDINGS.md): the hull's lowest point drops about
    # 0.05 m into the floor plane. A run whose floor contact is broken cannot be expected to follow
    # a friction-derived ordering, because the normal force the ordering depends on is not resolved.
    # The next test pins the g48 anomaly so it cannot change silently.
    for g in ("g64", "g96"):
        seq = []
        for mass in ("m1100", "m1609", "m2337"):
            d = os.path.join(RUNS, f"{g}_{mass}")
            m = slide_margin(d) if os.path.isdir(d) else None
            if m is not None:
                seq.append((mass, m))
        if len(seq) < 2:
            continue
        ran += 1
        for (ma, va), (mb, vb) in zip(seq, seq[1:]):
            assert vb <= va, (
                f"{g}: margin rose with mass, {ma}={va} -> {mb}={vb}. "
                "A heavier vehicle moving MORE contradicts the friction model.")
    if not ran:
        _skip("no mass-paired runs available")


def test_g48_mass_ordering_is_a_known_violation():
    """Pin the g48 anomaly so it cannot drift silently in either direction.

    If g48 ever starts obeying the ordering, something changed and the exclusion above needs
    revisiting. If a different grid starts violating it, the test above catches that.
    """
    seq = []
    for mass in ("m1100", "m1609", "m2337"):
        d = os.path.join(RUNS, f"g48_{mass}")
        m = slide_margin(d) if os.path.isdir(d) else None
        if m is not None:
            seq.append(m)
    if len(seq) < 3:
        _skip("g48 triple not available")
    monotone = all(b <= a for a, b in zip(seq, seq[1:]))
    assert not monotone, (
        f"g48 margins {seq} are now monotone. The documented anomaly has "
        "changed; re-examine whether the P-3 floor-penetration failure was "
        "fixed, and reinstate g48 in the ordering test if so.")


# --------------------------------------------------------------- runner

def main() -> int:
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    fails, skips = [], []
    print(f"physics gates: {len(tests)} tests\n")
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Skip as e:
            skips.append(f"{name}: {e}")
            print(f"  SKIP  {name}: {e}")
        except AssertionError as e:
            fails.append((name, str(e)))
            print(f"  FAIL  {name}\n        {e}")
        except Exception as e:  # noqa: BLE001
            fails.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ERROR {name}\n        {type(e).__name__}: {e}")
    print()
    print(f"failures {len(fails)}   skips {len(skips)}")
    if skips:
        print("SKIPS ARE NOT PASSES. Outstanding:")
        for s in skips:
            print(f"  - {s}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
