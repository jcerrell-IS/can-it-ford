"""DISPATCH 9 CONCRETE FIRST STEP: reproduce the exploratory run's hull geometry.

The gate, quoted from the dispatch: load `rogue_g96_pd8_coarse_watertight.ply`
(sha256 `c0b778e2...`) and confirm volume 4.950341 m3 and canonicalized extent
2.010112, 4.746607, 1.729385 with the long axis on y. "If those three numbers do not
reproduce, stop and report; everything downstream is invalid."

This runs the GATED geometry code, not a reimplementation: `load_vehicle` comes from
the vetted `vehicle_live.py` (sha256 `5a5bbbab...`) and `canonicalize` from the AS-RAN
`sim_standing.py` (sha256 `5215c38b...`), both AST-loaded with their warpmpm imports
dropped (see analysis/vetted_loader.py). No GPU and no warp are needed: this is pure
numpy and trimesh, so it runs on the Mac and on a login node.

THE SEED CONTROL, and why it is here rather than assumed. `load_vehicle` draws 60,000
RANDOM surface samples (vehicle_live.py:234) and derives its re-centring shift from
them (:251), so two things must be distinguished and the project has conflated them:

  * `VehicleBody.extent` as returned by load_vehicle is SAMPLE-derived (:253) and is
    therefore seed-dependent.
  * the CANONICALIZED extent is MESH-derived (sim_standing.py canonicalize), and is
    seed-independent up to the 1-ULP shift residue.

--repeats runs the load under several seeds and reports the spread of both, so the
claim "this reproduces" is measured rather than asserted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vetted_loader import load_as_ran_canonicalize, load_vehicle_live  # noqa: E402

# The published gate, from docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md section 2.
EXPECTED_PLY_SHA256 = "c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2"
EXPECTED_VOLUME_M3 = 4.950341
EXPECTED_EXTENT = (2.010112, 4.746607, 1.729385)
EXPECTED_VERTS = 36_074
EXPECTED_FACES = 72_520

# Tolerance for a "reproduces" verdict. The published values are quoted to 6 decimal
# places, so agreement is asserted at that precision and no tighter.
TOL = 5e-7


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure(ply: Path, seed: int | None, canonicalize, load_vehicle) -> dict:
    """One load. seed=None deliberately leaves numpy's global RNG alone."""
    if seed is not None:
        np.random.seed(seed)
    v = load_vehicle(ply, up="z")
    raw_extent = np.asarray(v.extent, dtype=float).copy()
    v = canonicalize(v)
    ext = np.asarray(v.extent, dtype=float)
    mesh = v.mesh
    return {
        "seed": seed,
        "n_verts": int(len(mesh.vertices)),
        "n_faces": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "volume_m3": float(abs(mesh.volume)),
        "extent_canonical": ext.tolist(),
        "extent_from_samples": raw_extent.tolist(),
        "long_axis": "xyz"[int(np.argmax(ext))],
        "spacing_m": float(v.spacing),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ply", required=True, type=Path,
                    help="rogue_g96_pd8_coarse_watertight.ply")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--repeats", type=int, default=3,
                    help="extra loads at seed+1.. to measure seed sensitivity")
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--allow-digest-mismatch", action="store_true",
                    help="run on a hull whose sha256 is not the published one; the "
                         "result is then not a reproduction of the gate")
    args = ap.parse_args()

    print("=" * 78)
    print("DISPATCH 9 GATE: rogue hull geometry through the vetted loader")
    print("=" * 78)

    digest = sha256_of(args.ply)
    ply_ok = digest == EXPECTED_PLY_SHA256
    print(f"\nhull      {args.ply}")
    print(f"sha256    {digest}")
    print(f"expected  {EXPECTED_PLY_SHA256}")
    print(f"           {'MATCH' if ply_ok else 'MISMATCH'}")
    if not ply_ok and not args.allow_digest_mismatch:
        print("\nSTOP: hull digest does not match the published gate. Everything "
              "downstream would be invalid. Re-run with --allow-digest-mismatch only "
              "if you intend to characterise a different hull.")
        return 2

    canonicalize = load_as_ran_canonicalize()
    mod = load_vehicle_live()
    print(f"\nloader    {mod.__file__}")
    print(f"          sha256 {mod.__vetted_sha256__}")

    runs = [measure(args.ply, args.seed, canonicalize, mod.load_vehicle)]
    for k in range(args.repeats):
        runs.append(measure(args.ply, args.seed + 1 + k, canonicalize, mod.load_vehicle))

    r0 = runs[0]
    print(f"\nmesh      {r0['n_verts']} verts, {r0['n_faces']} faces, "
          f"watertight={r0['watertight']}")
    print(f"          expected {EXPECTED_VERTS} verts, {EXPECTED_FACES} faces")

    dv = r0["volume_m3"] - EXPECTED_VOLUME_M3
    ext = r0["extent_canonical"]
    de = [ext[i] - EXPECTED_EXTENT[i] for i in range(3)]

    print(f"\n{'quantity':<26}{'measured':>16}{'published':>16}{'delta':>14}")
    print("-" * 72)
    print(f"{'volume_m3':<26}{r0['volume_m3']:>16.6f}{EXPECTED_VOLUME_M3:>16.6f}{dv:>14.2e}")
    for i, ax in enumerate("xyz"):
        print(f"{'extent_' + ax + ' (canonical)':<26}{ext[i]:>16.6f}"
              f"{EXPECTED_EXTENT[i]:>16.6f}{de[i]:>14.2e}")
    print(f"{'long_axis':<26}{r0['long_axis']:>16}{'y':>16}")

    vol_ok = abs(dv) < TOL
    ext_ok = all(abs(d) < TOL for d in de)
    axis_ok = r0["long_axis"] == "y"
    counts_ok = r0["n_verts"] == EXPECTED_VERTS and r0["n_faces"] == EXPECTED_FACES

    # Seed sensitivity: the falsifiable part. Canonical extent should be invariant;
    # the sample-derived extent should not be.
    can = np.array([r["extent_canonical"] for r in runs])
    smp = np.array([r["extent_from_samples"] for r in runs])
    vols = np.array([r["volume_m3"] for r in runs])
    can_spread = float(np.abs(can - can[0]).max())
    smp_spread = float(np.abs(smp - smp[0]).max())
    vol_spread = float(np.abs(vols - vols[0]).max())

    print(f"\nSEED CONTROL over {len(runs)} loads (seeds "
          f"{[r['seed'] for r in runs]}):")
    print(f"  max |delta| canonical extent   {can_spread:.3e} m")
    print(f"  max |delta| volume             {vol_spread:.3e} m3")
    print(f"  max |delta| sample-derived ext {smp_spread:.3e} m   <- expected nonzero")

    verdict = vol_ok and ext_ok and axis_ok
    print("\n" + "=" * 78)
    print(f"GATE: {'PASS' if verdict else 'FAIL'}   "
          f"(volume {'ok' if vol_ok else 'FAIL'}, extent {'ok' if ext_ok else 'FAIL'}, "
          f"long axis {'ok' if axis_ok else 'FAIL'}, "
          f"mesh counts {'ok' if counts_ok else 'FAIL'})")
    print("=" * 78)
    if not verdict:
        print("Per the dispatch: STOP AND REPORT. Everything downstream is invalid.")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps({
            "gate_pass": bool(verdict),
            "ply_sha256": digest,
            "ply_digest_match": ply_ok,
            "loader_sha256": mod.__vetted_sha256__,
            "expected": {"volume_m3": EXPECTED_VOLUME_M3,
                         "extent": list(EXPECTED_EXTENT),
                         "n_verts": EXPECTED_VERTS, "n_faces": EXPECTED_FACES},
            "runs": runs,
            "seed_spread": {"canonical_extent_m": can_spread,
                            "volume_m3": vol_spread,
                            "sample_extent_m": smp_spread},
        }, indent=2))
        print(f"\nwrote {args.json_out}")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
