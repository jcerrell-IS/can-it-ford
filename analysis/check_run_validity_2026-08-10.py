#!/usr/bin/env python3
"""Post-hoc validity gate for sim_enhanced.py runs.

WHY THIS EXISTS. sim_enhanced.py:40 states in its own header that the driver has
"no NaN guard, so the failure mode is silent degradation, not a crash". Every gate
in renders/yaris_render_s1/gates.py is a self-consistency or containment check and
none of them tests whether the integration stayed stable (CLAUDE.md item 6). So a
run that blows up numerically can still write a complete summary.json, a full
metrics.csv and a well-formed rollout.npz, and be read as a result.

That gap matters most for any run that RAISES the artificial sound speed. Raising
bulk_modulus raises term_acoustic linearly (sim_enhanced.py:195), and the substep
count is chosen from it (:199), so if the CFL mirror in the driver disagrees with
the kernel's real stability limit the run destabilises quietly. This script is the
independent check on that.

THIS IS NOT A PHYSICS VALIDATION. Every test here asks "did the integrator stay
sane", not "is the answer right". A run can pass every check and still be
physically wrong for the reasons in CLAUDE.md L-3, L-4 and A-1. Do not cite a PASS
here as validation of anything.

numpy only, no warpmpm import, so it is safe and cheap on a login node.

Usage:
    python3 check_run_validity_2026-08-10.py <run_dir> [<run_dir> ...]
    python3 check_run_validity_2026-08-10.py --json <run_dir> ...

Exit code 0 if every run passes, 1 if any run fails or errors.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

# Rotation matrices from a rigid body must stay orthonormal. Drift away from
# det(R) = 1 or from R @ R.T = I is the clearest signal that the rigid solve is
# degrading, and it appears well before values become non-finite. The tolerance is
# a NUMERICAL one on float32 accumulation over 90 frames, not a physical bound.
R_ORTHONORMAL_TOL = 1e-3

# Water speed ceiling. The scenes run at velocity <= 3.0 m/s (CLAUDE.md L-2, the
# administrative cap) with gravity 9.81 over a sub-second fall, so any water
# particle above this is not a flow feature, it is an instability. Deliberately
# loose: this catches blowups, it does not police physics.
MAX_PLAUSIBLE_WATER_SPEED_MS = 50.0

# Mach number against the run's OWN artificial sound speed. Weakly compressible
# schemes target M near 0.1 so density fluctuation stays near 1 percent. Above
# this the compressibility error is large enough that the run should be reported
# with the caveat, not silently pooled with low-M runs.
MACH_WARN = 0.10


def _finite(x) -> bool:
    a = np.asarray(x, dtype=np.float64)
    return bool(np.isfinite(a).all())


def check_summary(run: Path, res: dict) -> None:
    """Every numeric leaf in summary.json must be finite."""
    p = run / "summary.json"
    if not p.exists():
        res["fail"].append("summary.json missing")
        return
    try:
        s = json.loads(p.read_text())
    except Exception as e:
        res["fail"].append(f"summary.json unreadable: {type(e).__name__}: {e}")
        return
    res["summary"] = s

    bad = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, (list, tuple)):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
        elif isinstance(node, bool):
            return
        elif isinstance(node, (int, float)):
            if not math.isfinite(float(node)):
                bad.append(f"{path}={node}")

    walk(s, "")
    if bad:
        res["fail"].append("non-finite in summary.json: " + ", ".join(bad[:8]))
    else:
        res["ok"].append("summary.json all-finite")

    oob = s.get("C3_oob_particle_frames")
    if oob is None:
        res["warn"].append("C3_oob_particle_frames absent")
    elif int(oob) != 0:
        res["fail"].append(f"C3 out-of-domain particle-frames = {oob}, expected 0")
    else:
        res["ok"].append("C3 oob = 0")

    # BACKWARD-COMPATIBLE READ. Renamed 2026-08-18; summaries written before then carry
    # the old key and are not being rewritten.
    # NOTE what this warning does and does not mean. The flag compares two loads of the
    # same hull on particle count and grid limit only, so False means the HULL LOAD was
    # not reproducible. True does NOT mean the run is reproducible: repeats at fixed
    # configuration give bit-different trajectories while this reads True.
    hull_load = s.get("hull_load_identical", s.get("determinism_identical"))
    if hull_load is False:
        res["warn"].append("hull_load_identical is False (hull load, not trajectory)")


def check_rollout(run: Path, res: dict) -> None:
    """Finiteness, rigid-pose orthonormality, and a water-speed ceiling."""
    p = run / "rollout.npz"
    if not p.exists():
        res["warn"].append("rollout.npz missing, array checks skipped")
        return
    try:
        d = np.load(p)
    except Exception as e:
        res["fail"].append(f"rollout.npz unreadable: {type(e).__name__}: {e}")
        return

    for key in ("water", "speed", "R", "t"):
        if key not in d:
            res["warn"].append(f"rollout.npz has no '{key}'")
            continue
        if not _finite(d[key]):
            n = int((~np.isfinite(np.asarray(d[key], dtype=np.float64))).sum())
            res["fail"].append(f"rollout.npz['{key}'] has {n} non-finite entries")
        else:
            res["ok"].append(f"{key} finite")

    # The strongest silent-degradation detector available: a rigid body's rotation
    # must stay orthonormal with det = +1. Drift here precedes visible blowup.
    if "R" in d and _finite(d["R"]):
        R = np.asarray(d["R"], dtype=np.float64)
        if R.ndim == 3 and R.shape[1:] == (3, 3):
            dets = np.linalg.det(R)
            det_err = float(np.abs(dets - 1.0).max())
            eye = np.eye(3)
            orth_err = float(
                np.abs(np.einsum("fij,fkj->fik", R, R) - eye).max()
            )
            res["metrics"]["max_det_error"] = det_err
            res["metrics"]["max_orthonormality_error"] = orth_err
            if det_err > R_ORTHONORMAL_TOL or orth_err > R_ORTHONORMAL_TOL:
                res["fail"].append(
                    f"rigid pose degraded: max|det(R)-1|={det_err:.3e}, "
                    f"max|R Rt - I|={orth_err:.3e}, tol={R_ORTHONORMAL_TOL:.0e}"
                )
            else:
                res["ok"].append(
                    f"rigid pose orthonormal (det err {det_err:.2e}, "
                    f"orth err {orth_err:.2e})"
                )
        else:
            res["warn"].append(f"R has unexpected shape {R.shape}, pose check skipped")

    if "speed" in d and _finite(d["speed"]):
        vmax = float(np.asarray(d["speed"], dtype=np.float64).max())
        res["metrics"]["max_water_speed_ms"] = vmax
        if vmax > MAX_PLAUSIBLE_WATER_SPEED_MS:
            res["fail"].append(
                f"max water speed {vmax:.2f} m/s exceeds the "
                f"{MAX_PLAUSIBLE_WATER_SPEED_MS:.0f} m/s instability ceiling"
            )
        else:
            res["ok"].append(f"max water speed {vmax:.3f} m/s")

        c = (res.get("summary") or {}).get("sound_speed_ms")
        if c:
            mach = vmax / float(c)
            res["metrics"]["realized_mach"] = mach
            if mach > MACH_WARN:
                res["warn"].append(
                    f"realized Mach {mach:.4f} exceeds {MACH_WARN}, so the "
                    f"weakly-compressible density error is NOT small here"
                )
            else:
                res["ok"].append(f"realized Mach {mach:.5f}")


def check_metrics(run: Path, res: dict) -> None:
    p = run / "metrics.csv"
    if not p.exists():
        res["warn"].append("metrics.csv missing")
        return
    txt = p.read_text()
    low = txt.lower()
    for tok in ("nan", "inf"):
        if tok in low:
            n = low.count(tok)
            res["fail"].append(f"metrics.csv contains '{tok}' x{n}")
    if "nan" not in low and "inf" not in low:
        res["ok"].append("metrics.csv free of nan/inf")


def check_run(run: Path) -> dict:
    res = {"run": str(run), "ok": [], "warn": [], "fail": [], "metrics": {},
           "verdict": "FAIL"}
    if not run.is_dir():
        res["fail"].append("not a directory")
        return res
    check_summary(run, res)
    check_rollout(run, res)
    check_metrics(run, res)
    res["verdict"] = "FAIL" if res["fail"] else ("WARN" if res["warn"] else "PASS")
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    a = ap.parse_args()

    results = [check_run(r) for r in a.runs]

    if a.json:
        print(json.dumps(results, indent=2, default=float))
    else:
        for r in results:
            print(f"\n########## {Path(r['run']).name}  ->  {r['verdict']} ##########")
            for m in r["fail"]:
                print(f"  FAIL  {m}")
            for m in r["warn"]:
                print(f"  WARN  {m}")
            for m in r["ok"]:
                print(f"  ok    {m}")
            if r["metrics"]:
                print("  metrics: " + ", ".join(
                    f"{k}={v:.6g}" for k, v in r["metrics"].items()))
        n_fail = sum(1 for r in results if r["verdict"] == "FAIL")
        n_warn = sum(1 for r in results if r["verdict"] == "WARN")
        print(f"\n{len(results)} run(s): {len(results)-n_fail-n_warn} PASS, "
              f"{n_warn} WARN, {n_fail} FAIL")
        print("Reminder: these are stability checks, NOT physics validation.")

    return 1 if any(r["verdict"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
