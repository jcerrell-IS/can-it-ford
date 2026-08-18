#!/usr/bin/env python3
"""Grade the Job B boundary-fix A/B: job 918240 (control) against job 918450 (treatment).

THE TREATMENT IS ONE LINE OF ENGINE. A copy of the engine at $WORK/mpm-engine-bcfix-src
with mpm_solver_warp.py:1955 changed from `if dotproduct < 0.0:` to `<= 0.0:`. Verified
live 2026-08-18 by `diff -rq -x __pycache__` over the two trees: exactly one source file
differs and its diff is exactly one line. The pinned engine is untouched, so every
published run's provenance holds. Scene, config and driver are otherwise identical.

GRADE AGAINST THE PRE-REGISTERED PREDICTION, NOT AGAINST HINDSIGHT. The prediction is in
the treatment's own run script, $WORK/run_jobBbc.sh, written before the run:

    "n_below_floor should FALL but not vanish, the surface drop should shrink by roughly
     1.8 cm of 5.6, and fz_over_analytic_measured should move toward 1.0 without reaching
     it. If the leak is UNCHANGED the defect-2 hypothesis is refuted. If it vanishes
     entirely, the mass-deficiency story was wrong and that is more interesting still."

So there are three graded outcomes and this script names which one fired:
    REFUTED      leak unchanged
    CONFIRMED    leak falls but survives, i.e. the partial fix behaved as predicted
    OVERTURNED   leak vanishes, the mass-deficiency story was wrong

THE ACCESSOR. `fz_over_analytic_measured`. The designation is a source comment reading
"is the number job B should actually be graded on", at sphere_heave.py:804-805, with the
quoted "a falling free surface no longer masquerades" sentence at :806-807 and the field
itself at :818, on branch claude/r5-physics. NOT at :669-670 as the round-7 handoff and task
text both state: :669 is "mach_peak" and measure_surface begins at :676. Verified live
2026-08-18; the line numbers had drifted.

BANDS, from R5_PHYSICS_BATCH_MANIFEST.md criterion 3: within 10 percent PASS, 10 to 25
REPORTABLE PARTIAL, beyond 25 FAIL. "These bands are set now and will not be moved."

DO NOT REPORT NOT GRADEABLE. grade_job_b.py sets its TOP-LEVEL `band` key to NOT GRADEABLE
by refusing fz_N for non-stationarity, but manifest criterion 5 says in terms that a
NOT-STATIONARY verdict here is "expected, not disqualifying". This script therefore always
produces a band verdict and reports stationarity beside it as context.

CORRECTED 2026-08-18, and an earlier version of this docstring implied otherwise: grade_job_b.py
DOES compute and band the designated accessor. It emits it on the refusal path, under
`measured_surface_criterion`, with the same FAIL and the same +50.06 / +34.35 percent this
script produces. grade_job_b.py:199-205 records that defect as already found and already fixed
("It is emitted on the refusal path too now."). The remaining defect is narrow: only the
TOP-LEVEL band key is nominal-derived, so a machine reading `band` misses the FAIL. Do not
repeat the claim that this tool never reaches the designated accessor; run it instead.

Needs numpy. No system python on this Mac has it:
    /opt/homebrew/bin/uv run --with numpy python3 analysis/r7_jobb_bcfix_ab.py \\
        --control <control.json> --treatment <treatment.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

WINDOWS = (20, 40, 80, 100, 150, 200)
LATE_START = 100  # the grader's late-window start


def find_blocking(explicit: Path | None) -> Path:
    """blocking.py lives on claude/r5-physics, NOT on every branch. Locate it rather
    than assume it, and fail with the branch name instead of an ImportError. Same
    approach as r6_repeat_stats.find_blocking."""
    cands = []
    if explicit:
        cands.append(explicit)
    cands.append(REPO / "simulation" / "r5_physics")
    for root in (REPO.parent, REPO / ".claude" / "worktrees"):
        if root.is_dir():
            for d in sorted(root.iterdir()):
                cands.append(d / "simulation" / "r5_physics")
    for c in cands:
        if (c / "blocking.py").is_file():
            return c
    raise SystemExit(
        "blocking.py not found. It lives in simulation/r5_physics/ on branch\n"
        "claude/r5-physics. Pass --blocking-dir <path to simulation/r5_physics>."
    )


def band(pct: float) -> str:
    a = abs(pct)
    return "PASS" if a <= 10 else ("REPORTABLE PARTIAL" if a <= 25 else "FAIL")


def load(p: Path) -> tuple[dict, list, dict]:
    doc = json.loads(p.read_text())
    return doc["config"], doc["rows"], doc.get("provenance", {})


def col(rows: list, name: str):
    import numpy as np
    return np.array([r[name] for r in rows], dtype=float)


def leak_block(label: str, cfg: dict, rows: list) -> dict:
    """The leak counters at the LAST frame, which is what the prediction is about."""
    last = rows[-1]
    n_water = cfg.get("n_water_particles") or cfg.get("n_water") or None
    if n_water is None:
        # Fall back to the manifest's measured seeding count for this scene.
        n_water = 598505
    below = last["n_below_floor"]
    outside = last["n_outside_walls"]
    return dict(
        label=label,
        n_water=n_water,
        n_below_floor=below,
        pct_below=below / n_water * 100.0,
        n_outside_walls=outside,
        pct_outside=outside / n_water * 100.0,
        surface_drop_cm=last["surface_drop_m"] * 100.0,
        water_z_min=last["water_z_min_m"],
        floor_m=cfg["floor_m"],
    )


def config_identity(cfg_a: dict, cfg_b: dict) -> None:
    """The A/B only means anything if the scene is identical. The control's job log
    predates the sha256 echo lines in run_jobBbc.sh, so the as-run scene file cannot be
    hash-compared for 918240. Comparing the emitted config blocks is the stronger check
    anyway: it tests what the scene actually built, not what file was on disk."""
    print("=" * 78)
    print("0. SCENE IDENTITY. The A/B is meaningless if anything but the engine moved.")
    print("=" * 78)
    keys = sorted(set(cfg_a) | set(cfg_b))
    diffs = []
    for k in keys:
        va, vb = cfg_a.get(k, "<absent>"), cfg_b.get(k, "<absent>")
        if isinstance(va, float) and isinstance(vb, float):
            same = abs(va - vb) <= 1e-12 * max(1.0, abs(va))
        else:
            same = va == vb
        if not same:
            diffs.append((k, va, vb))
    print(f"\n  {len(keys)} config keys compared")
    if not diffs:
        print("  ALL IDENTICAL. Engine is the only difference.")
    else:
        print(f"  {len(diffs)} DIFFER:")
        for k, va, vb in diffs:
            print(f"    {k:38s} {va!r:>22}  ->  {vb!r}")
    print()


def print_leak(a: dict, b: dict) -> None:
    print("=" * 78)
    print("1. THE LEAK, at the last frame. This is what the prediction is about.")
    print("=" * 78)
    print(f"\n  {'quantity':<26} {'control 918240':>16} {'bcfix 918450':>16} {'change':>14}")
    def row(name, ka, kb, fmt):
        va, vb = a[ka], b[kb]
        d = vb - va
        rel = f"{(vb / va - 1) * 100:+.1f} %" if va else "n/a"
        print(f"  {name:<26} {va:>16{fmt}} {vb:>16{fmt}} {rel:>14}")
        return d
    row("n_below_floor", "n_below_floor", "n_below_floor", "d")
    row("  as % of water", "pct_below", "pct_below", ".3f")
    row("n_outside_walls", "n_outside_walls", "n_outside_walls", "d")
    row("  as % of water", "pct_outside", "pct_outside", ".3f")
    row("surface drop (cm)", "surface_drop_cm", "surface_drop_cm", ".3f")
    row("water_z_min (m)", "water_z_min", "water_z_min", ".5f")
    print(f"  {'floor plane (m)':<26} {a['floor_m']:>16.5f} {b['floor_m']:>16.5f}")
    print(f"  {'n_water seeded':<26} {a['n_water']:>16d} {b['n_water']:>16d}")


def verdict_on_prediction(a: dict, b: dict) -> None:
    print()
    print("=" * 78)
    print("2. THE PRE-REGISTERED PREDICTION, graded")
    print("=" * 78)
    drop_a, drop_b = a["surface_drop_cm"], b["surface_drop_cm"]
    shrink = drop_a - drop_b
    below_rel = b["n_below_floor"] / a["n_below_floor"] - 1.0 if a["n_below_floor"] else float("nan")
    print(f"\n  predicted: n_below_floor FALLS but does not vanish")
    print(f"    measured: {a['n_below_floor']} -> {b['n_below_floor']}  "
          f"({below_rel * 100:+.1f} %)")
    if b["n_below_floor"] == 0:
        out = "OVERTURNED. The leak VANISHED, so the mass-deficiency story was wrong."
    elif abs(below_rel) < 0.02:
        out = "REFUTED. The leak is unchanged within 2 %, so defect 2 is not the cause."
    elif below_rel < 0:
        out = "CONFIRMED. The leak fell but survived, exactly the partial fix predicted."
    else:
        out = ("UNPREDICTED. The leak GREW. Neither branch of the pre-registered "
               "prediction covers this.")
    print(f"    -> {out}")

    print(f"\n  predicted: surface drop shrinks by roughly 1.8 cm of {drop_a:.3f}")
    print(f"    measured: {drop_a:.3f} cm -> {drop_b:.3f} cm, shrink {shrink:+.3f} cm")
    print(f"    -> {'as predicted' if 0.9 <= shrink <= 2.7 else 'OUTSIDE the predicted ~1.8 cm'}"
          f" (band taken as half to 1.5x of 1.8 cm)")


def grade(label: str, rows: list, bdir: Path) -> None:
    sys.path.insert(0, str(bdir))
    import blocking as B

    print()
    print("=" * 78)
    print(f"3. CRITERION 3 GRADED, {label}, {len(rows)} frames")
    print("   accessor fz_over_analytic_measured (sphere_heave.py:804-805, :818)")
    print("   bands: <=10 PASS, 10-25 REPORTABLE PARTIAL, >25 FAIL")
    print("=" * 78)
    for name, note in (("fz_over_analytic_measured", "THE DESIGNATED ACCESSOR"),
                       ("fz_over_analytic_nominal", "nominal, reported for contrast only")):
        y = col(rows, name)
        verdicts = set()
        print(f"\n  {name}   ({note})")
        for n in WINDOWS:
            if n > len(y):
                continue
            pct = (y[-n:].mean() - 1) * 100
            verdicts.add(band(pct))
            print(f"    last {n:3d} frames {pct:+7.2f} %  -> {band(pct)}")
        note2 = "WINDOW-ROBUST" if len(verdicts) == 1 else "<-- SWINGS ON WINDOW CHOICE"
        print(f"    verdicts across windows: {sorted(verdicts)}   {note2}")

    print("\n  criterion 5, stationarity. Manifest: NOT-STATIONARY here is "
          "'expected, not disqualifying'.")
    for name in ("fz_N", "fz_over_analytic_measured", "surface_z_measured_m"):
        r = B.stationarity(col(rows, name)[LATE_START:])
        print(f"    {name:28s} halves={str(r['halves_stationary']):5s} "
              f"trend={str(r['trend_stationary']):5s} slope_n_sigma={r['slope_n_sigma']:.2f}")
    y = col(rows, "fz_over_analytic_measured")[LATE_START:]
    se = B.blocked_se(y)
    print(f"    late-window mean {y.mean():.6f} +/- {se['se_blocked']:.6f} "
          f"(blocked SE, converged={se['converged']}), "
          f"{(y.mean() - 1) * 100:+.3f} % from the closed form")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--control", type=Path, required=True,
                    help="sphere_fixed_g64.json from job 918240")
    ap.add_argument("--treatment", type=Path, required=True,
                    help="sphere_fixed_bcfix.json from job 918450")
    ap.add_argument("--blocking-dir", type=Path, default=None)
    a = ap.parse_args()

    bdir = find_blocking(a.blocking_dir)
    print(f"[blocking.py from {bdir}]\n")
    cfg_a, rows_a, _ = load(a.control)
    cfg_b, rows_b, _ = load(a.treatment)
    config_identity(cfg_a, cfg_b)
    la = leak_block("control 918240", cfg_a, rows_a)
    lb = leak_block("bcfix 918450", cfg_b, rows_b)
    print_leak(la, lb)
    verdict_on_prediction(la, lb)
    grade("CONTROL 918240", rows_a, bdir)
    grade("TREATMENT 918450 (bcfix)", rows_b, bdir)


if __name__ == "__main__":
    main()
