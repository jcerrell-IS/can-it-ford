"""
run_provenance.py

Closes the gap `docs/REMEDIATION_PLAN_AUDIT_2026-08-12.md` calls "the largest single
obstacle to a reproducibility claim": across 32 run manifests, `params_check.py` reports
`canitford_git_commit`, `grid_density`, `mesh_sha256`, `solver_git_sha` and
`vehicle_mass` missing in ALL 32, and `bulk_modulus` in 3.

Two entry points, deliberately in one file so the backward and forward paths cannot
drift apart:

  collect_provenance()   FORWARD. A driver calls this at run time and merges the result
                         into its summary.json. Every field is then RECORDED, not
                         reconstructed, which is the only kind of provenance worth
                         having.
  --backfill             BACKWARD. Repairs manifests that already exist, and labels
                         every field with how it was obtained.

THE RULE THIS FILE ENFORCES, AND WHY IT IS THE WHOLE POINT
  A back-filled field is NOT the same claim as a recorded one, and this project has been
  bitten by exactly that conflation before: register D6a records `failure_modes_by_run.json`
  naming a generator that never existed, and D6h condemns `failure_modes_result.json` for
  carrying numbers with no run identifier. Writing a plausible value into a manifest and
  letting it read as measured is how those defects were born.

  So every field this script adds is stamped in a `_provenance_backfill` block with one
  of four confidence labels:

    recorded      already in the manifest, untouched
    aliased       the same quantity under the manifest's existing name (mass_kg ->
                  vehicle_mass, n_grid -> grid_density). Exact, no inference.
    resolved      matched to a primary source by a measured discriminator, here hull_m3
                  against the known hull volumes. Exact if the match is exact.
    reconstructed INFERRED AFTER THE FACT and NOT evidence of what actually ran. Only
                  canitford_git_commit is ever this, and it is derived from the file's
                  mtime against git log, which cannot see whether the tree was dirty.

  A consumer that needs real provenance must check the labels, not just the presence of
  the keys. `params_check.py`'s gate only tests presence, so passing it is necessary and
  not sufficient. That limitation is stated here rather than hidden.

MESH RESOLUTION IS PER RUN AND REFUSES RATHER THAN GUESSES
  3 of the 32 manifests are NOT the Yaris. `render_s2/multigeom_2026-08-08/` holds a
  Rogue (hull_m3 4.950340735545737) and a Silverado (7.962083114517729), verified live
  2026-08-12. Stamping the Yaris digest across all 32 would fabricate provenance for two
  runs, which is worse than leaving the field absent. Hulls are therefore matched by
  hull_m3, and an unmatched hull leaves mesh_sha256 ABSENT with the reason recorded.

  Yaris digest is computed live from the file. Rogue and Silverado digests are quoted
  from docs/MULTIGEOM_VALIDATION_2026-08-11.md section 1, which records them as verified
  live by sha256sum over all four paths on 2026-08-11; those two .ply files live on Vista
  and are not in this repo, so they cannot be recomputed here.

BULK MODULUS IS NOT RECONSTRUCTED
  The 3 manifests without it are renders/yaris_render_s1/{m1100,m1609,m2337}/, which
  register D4a identifies as ORPHAN ROLLOUTS matching no canonical run. They also carry
  no sound_speed_ms, so K = c^2 * rho / gamma has no input. Both facts are recorded and
  the field is left absent. Guessing it would make an orphan look canonical.

Usage
  python analysis/run_provenance.py --backfill                 # dry run, prints a plan
  python analysis/run_provenance.py --backfill --write         # apply
  python analysis/run_provenance.py --backfill --root /path    # manifests live elsewhere
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# vehicle_geometry_research/yaris_coarse_v1l_watertight.ply, register E1.
CANONICAL_YARIS_PLY = REPO / "vehicle_geometry_research" / "yaris_coarse_v1l_watertight.ply"

# hull_m3 -> (label, sha256, source). Tolerance is absolute on m3.
# Yaris appears at two precisions in the manifests, 3.542739 and 3.542738790016075.
KNOWN_HULLS = {
    3.542739: ("yaris_coarse_v1l_watertight.ply", None, "computed live from the repo file"),
    4.950340735545737: (
        "rogue_g96_pd8_coarse_watertight.ply",
        "c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2",
        "docs/MULTIGEOM_VALIDATION_2026-08-11.md section 1, verified live 2026-08-11"),
    7.962083114517729: (
        "silverado_g96_pd8_coarse_watertight.ply",
        "46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9",
        "docs/MULTIGEOM_VALIDATION_2026-08-11.md section 1, verified live 2026-08-11"),
}
HULL_TOL_M3 = 1e-5

# Register D4a: these match no canonical run. Recorded so a back-fill cannot make an
# orphan look traceable.
ORPHAN_DIRS = ("renders/yaris_render_s1/m1100", "renders/yaris_render_s1/m1609",
               "renders/yaris_render_s1/m2337")

ALIASES = {"vehicle_mass": "mass_kg", "grid_density": "n_grid"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pinned_solver_sha() -> tuple[str | None, str]:
    """Read the pin from its file rather than restating it, so it cannot go stale."""
    for rel in ("third_party/mpm-engine-544c93dd-solver-core/PINNED_SHA.txt",
                "third_party/mpm-engine-544c93dd/PINNED_SHA.txt"):
        p = REPO / rel
        if p.exists():
            sha = p.read_text().strip().split()[0]
            if len(sha) == 40:
                return sha, rel
    return None, "no PINNED_SHA.txt found"


def head_commit() -> str | None:
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def commit_at_time(epoch: float) -> str | None:
    """Last commit at or before `epoch`. RECONSTRUCTED, never recorded.

    This cannot see whether the working tree was dirty when the run executed, and this
    repo is edited by concurrent sessions (docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md),
    so a clean-tree assumption is not safe. Treat the result as an upper bound on what
    the code could have been, not as what it was.
    """
    r = subprocess.run(
        ["git", "-C", str(REPO), "rev-list", "-1", f"--before=@{int(epoch)}", "HEAD"],
        capture_output=True, text=True)
    out = r.stdout.strip()
    return out or None


def resolve_hull(payload: dict):
    """(sha256 or None, label, source, note). Refuses on an unknown hull."""
    hull = payload.get("hull_m3")
    if hull is None:
        return None, None, None, "manifest carries no hull_m3, hull cannot be identified"
    for known, (label, sha, source) in KNOWN_HULLS.items():
        if abs(float(hull) - known) <= HULL_TOL_M3:
            if sha is None:
                if not CANONICAL_YARIS_PLY.exists():
                    return None, label, source, "canonical Yaris .ply not present in this tree"
                return sha256_file(CANONICAL_YARIS_PLY), label, source, ""
            return sha, label, source, ""
    return (None, None, None,
            f"hull_m3 {hull} matches no known hull within {HULL_TOL_M3} m3, refusing to "
            f"guess a digest. Add it to KNOWN_HULLS with a primary source first.")


def collect_provenance(vehicle_mass=None, grid_density=None, bulk_modulus=None,
                       mesh_path=None):
    """FORWARD path. Call at run time; merge the result into summary.json.

    Everything here is RECORDED: the mesh is hashed from the file actually loaded, the
    commit is HEAD at the moment of the run, the solver sha is read from the pin.
    """
    solver_sha, solver_src = pinned_solver_sha()
    mesh = Path(mesh_path) if mesh_path else CANONICAL_YARIS_PLY
    out = {
        "vehicle_mass": vehicle_mass,
        "grid_density": grid_density,
        "bulk_modulus": bulk_modulus,
        "mesh_sha256": sha256_file(mesh) if mesh.exists() else None,
        "solver_git_sha": solver_sha,
        "canitford_git_commit": head_commit(),
        "_provenance_backfill": {
            "mode": "recorded_at_run_time",
            "mesh_file": str(mesh),
            "solver_sha_source": solver_src,
            "note": "every field recorded during the run, none reconstructed",
        },
    }
    return {k: v for k, v in out.items() if v is not None}


def plan_for(path: Path, root: Path):
    """What this script would add to one manifest, and how it obtained each field."""
    try:
        payload = json.loads(path.read_text(errors="ignore"))
    except (ValueError, OSError) as exc:
        return None, {"error": f"unreadable: {exc}"}
    if not isinstance(payload, dict):
        return None, {"error": "not a JSON object"}

    rel = path.relative_to(root).as_posix()
    add, how, refused = {}, {}, {}

    for target, src in ALIASES.items():
        if target in payload:
            how[target] = "recorded"
        elif src in payload:
            add[target] = payload[src]
            how[target] = f"aliased from {src}"
        else:
            refused[target] = f"neither {target} nor {src} present"

    if "bulk_modulus" in payload:
        how["bulk_modulus"] = "recorded"
    else:
        orphan = any(rel.startswith(o) for o in ORPHAN_DIRS)
        refused["bulk_modulus"] = (
            "absent and NOT reconstructable: no sound_speed_ms, so K = c^2*rho/gamma "
            "has no input" + (". Also an ORPHAN rollout per register D4a, matching no "
                              "canonical run, so a value here would make it look "
                              "traceable when it is not" if orphan else ""))

    if "mesh_sha256" in payload:
        how["mesh_sha256"] = "recorded"
    else:
        sha, label, source, note = resolve_hull(payload)
        if sha:
            add["mesh_sha256"] = sha
            how["mesh_sha256"] = f"resolved by hull_m3 -> {label} ({source})"
        else:
            refused["mesh_sha256"] = note

    if "solver_git_sha" in payload:
        how["solver_git_sha"] = "recorded"
    else:
        sha, src = pinned_solver_sha()
        if sha:
            add["solver_git_sha"] = sha
            how["solver_git_sha"] = f"resolved from the pin, {src}"
        else:
            refused["solver_git_sha"] = src

    if "canitford_git_commit" in payload:
        how["canitford_git_commit"] = "recorded"
    else:
        c = commit_at_time(path.stat().st_mtime)
        if c:
            add["canitford_git_commit"] = c
            how["canitford_git_commit"] = (
                "RECONSTRUCTED from the manifest's mtime against git rev-list. NOT "
                "evidence of what ran: it cannot see a dirty tree, and this repo is "
                "edited by concurrent sessions. Upper bound only.")
        else:
            refused["canitford_git_commit"] = "no commit at or before the manifest mtime"

    return payload, {"rel": rel, "add": add, "how": how, "refused": refused}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true", required=True)
    ap.add_argument("--write", action="store_true", help="apply; default is a dry run")
    ap.add_argument("--root", default=str(REPO))
    a = ap.parse_args()
    root = Path(a.root).resolve()

    files = sorted(p for p in root.rglob("*summary.json")
                   if ".git" not in p.parts and "worktrees" not in str(p)
                   and not p.relative_to(root).as_posix().startswith("can-it-ford/"))
    print(f"root      {root}")
    print(f"manifests {len(files)}")
    print(f"mode      {'WRITE' if a.write else 'DRY RUN, nothing will be modified'}\n")

    added_counts, refused_counts, changed = {}, {}, 0
    for p in files:
        payload, plan = plan_for(p, root)
        if payload is None:
            print(f"  SKIP {p}: {plan['error']}")
            continue
        for k in plan["add"]:
            added_counts[k] = added_counts.get(k, 0) + 1
        for k in plan["refused"]:
            refused_counts[k] = refused_counts.get(k, 0) + 1
        if not plan["add"]:
            continue
        changed += 1
        if a.write:
            payload.update(plan["add"])
            block = payload.get("_provenance_backfill")
            if not isinstance(block, dict):   # never assume a pre-existing field's type
                block = {}
            block.update({"mode": "backfilled_after_the_fact",
                          "date": "2026-08-12",
                          "script": "analysis/run_provenance.py",
                          "field_confidence": plan["how"],
                          "refused": plan["refused"],
                          "warning": "fields labelled RECONSTRUCTED are inferred, not "
                                     "recorded. params_check only tests presence, so "
                                     "passing that gate is necessary and not sufficient."})
            payload["_provenance_backfill"] = block
            p.write_text(json.dumps(payload, indent=2, default=float) + "\n")

    print("fields that WOULD BE ADDED" if not a.write else "fields ADDED")
    for k, v in sorted(added_counts.items()):
        print(f"  {k:<24} {v}/{len(files)}")
    print("\nfields REFUSED, with the reason recorded per manifest")
    for k, v in sorted(refused_counts.items()):
        print(f"  {k:<24} {v}/{len(files)}")
    print(f"\nmanifests affected: {changed}/{len(files)}")
    if not a.write:
        print("\nDRY RUN. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
