"""run_provenance.py, the single run-provenance writer.

MERGE OF TWO INDEPENDENT WRITERS, 2026-08-13
  Two sessions each wrote a file at this path to close the same audit item, neither
  aware of the other. This is the reconciliation. Full working, including the term-by-term
  vocabulary mapping and the population enumeration, is in
  docs/PROVENANCE_WRITER_RECONCILIATION_2026-08-13.md.

    Mac    analysis/run_provenance.py @ 4924940 on branch warpmpm-continue, 388 lines.
           Vocabulary recorded/aliased/resolved/reconstructed. Targets *summary.json.
           Contributed: hull matching that REFUSES an unknown hull, the orphan-rollout
           refusal, atomic writes, and prior-labels-win idempotency.
    Vista   analysis/run_provenance.py + analysis/backfill_run_provenance.py, untracked at
           /work/11603/jcerrell0629/vista/can-it-ford, 13697 B + 15379 B.
           Vocabulary measured/derived/recorded/inapplicable/unknown. Targets
           data/coupling_validation*/. Contributed: the exact bulk-modulus derivation,
           the `inapplicable` category, run-script hashing, dirty-tree capture, _env.

  THE TWO WRITERS WERE NEVER WRITING ABOUT THE SAME RUNS. Their target populations are
  DISJOINT: not one file appears in both globs. That is the central finding, and it is
  why this is a union rather than a choice between them.

THE VOCABULARY, AND THE ONE WORD THAT COLLIDED
  `recorded` meant OPPOSITE things in the two originals. The Mac used it for its
  STRONGEST label, "already in the manifest, written at run time". Vista used it for a
  MIDDLE label, "copied from a pin declared in the run script". The Mac reading survives,
  because recorded-versus-reconstructed is the only axis this project actually needs to
  police, and the pin case is exactly `resolved`.

    recorded      Present in the manifest under the audited name, written at run time.
                  Untouched by this script. The strongest label.
    aliased       The same quantity, from the manifest's own value, under a different
                  key (mass_kg -> vehicle_mass, geometry.n_grid -> grid_density). Exact,
                  no inference. Vista labelled these `measured`, which overstates them:
                  nothing was measured, a key was renamed.
    derived       Computed from a value the manifest itself recorded, by a stated and
                  invertible formula. Here only bulk = c^2 * rho / gamma. Exact.
    resolved      Matched to a primary source by a measured discriminator (hull_m3 -> a
                  known hull digest), or read from a pin file. Exact if the match is.
    inapplicable  The run genuinely has no such quantity. A POSITIVE ASSERTION backed by
                  evidence in the manifest, never a synonym for absent.
    reconstructed INFERRED AFTER THE FACT, NOT evidence of what ran. Only
                  canitford_git_commit is ever this. Vista emitted this case as
                  `inferred`, a sixth value its own CONFIDENCE tuple did not declare;
                  renamed and now enforced.
    unknown       Could not be established. The value is left ABSENT and the reason is
                  recorded. Never a placeholder.

  Labels are validated at emit time (see _label). An undeclared label is a hard error,
  which is the defect that let Vista's `inferred` escape unnoticed.

  A back-filled field is NOT the same claim as a recorded one, and this project has been
  bitten by exactly that conflation: register D6a records failure_modes_by_run.json
  naming a generator that never existed, and D6h condemns failure_modes_result.json for
  carrying numbers with no run identifier. A consumer that needs real provenance must
  read the labels, not merely check that the keys exist. params_check.py's gate tests
  PRESENCE ONLY, so passing it is necessary and not sufficient. Stated here, not hidden.

TWO MANIFEST FAMILIES, DETECTED BY SHAPE AND NOT BY PATH
  Paths differ between machines, so the family test reads the document's structure.

    run_manifest         *summary.json. FLAT: hull_m3, mass_kg, n_grid, sound_speed_ms.
                         Loads a real vehicle hull, so mesh_sha256 is meaningful.
    coupling_validation  data/coupling_validation*/. NESTED: geometry.n_grid,
                         geometry.box_mass_kg, geometry.sound_speed,
                         provenance.pinned_sha. Procedural cube collider, so
                         mesh_sha256 is inapplicable.

MESH RESOLUTION REFUSES RATHER THAN GUESSES
  Three run_manifest runs are NOT the Yaris: render_s2/multigeom_2026-08-08/ holds a
  Rogue (hull_m3 4.950340735545737) and a Silverado (7.962083114517729). Stamping the
  Yaris digest across every manifest would fabricate provenance for two runs, which is
  worse than leaving the field absent. Hulls are matched by hull_m3; an unmatched hull
  leaves mesh_sha256 ABSENT with the reason recorded.

  For coupling_validation, `inapplicable` is asserted only on positive evidence: the
  manifest carries geometry.box_side_m / box_volume_m3 / box_particles_per_side and no
  mesh-shaped key anywhere. Verified live 2026-08-13 across all 21 such manifests on the
  Mac: those three keys are present in 21/21 and no "mesh"/"ply"/"obj"/"stl" key or value
  occurs in the family. Absence of hull_m3 alone is NOT accepted as evidence.

BULK MODULUS IS DERIVED, AND THE DERIVATION IS CROSS-CHECKED BEFORE IT IS TRUSTED
  Both drivers define the sound speed the same way, so the inversion is exact:
    renders/yaris_render_s1/sim_standing.py:225   c = sqrt(1.1 * bulk_modulus / rho)
    simulation/validate_coupling_force.py:18,19,22  RHO_W=1000.0, BULK=1.5e5, GAMMA=1.1
  giving bulk = c**2 * rho / gamma.

  rho and gamma are constants read from driver source, NOT from the manifest, so the
  derivation is only as good as those constants. It is therefore FALSIFIED FIRST against
  every manifest that records both quantities: verified live 2026-08-13, 29 of the 32
  run_manifests record sound_speed_ms AND bulk_modulus, and the derivation reproduces the
  recorded value in 29/29 with a worst relative error of 1.242e-16, one float ULP, and
  zero disagreements. Each emitted block carries its own cross-check result, so a future
  manifest that breaks the relation is reported instead of silently overwritten.

  The Mac writer REFUSED this field outright. That refusal was right for the 3 manifests
  it looked at and too broad for the other 21: renders/yaris_render_s1/{m1100,m1609,m2337}
  carry no sound_speed_ms at all, so they still refuse here, exactly as before, and
  register D4a records them as orphan rollouts matching no canonical run. Every
  coupling_validation manifest does record a sound speed, so for those the field is
  derivable and was being needlessly withheld.

Usage
  python analysis/run_provenance.py --backfill                      # dry run, prints a plan
  python analysis/run_provenance.py --backfill --write-sidecar      # *.provenance.json
  python analysis/run_provenance.py --backfill --write-in-place     # edits manifests
  python analysis/run_provenance.py --backfill --root /path         # manifests live elsewhere
  python analysis/run_provenance.py --backfill --family run_manifest

  The default is a dry run. The default WRITE mode is a sidecar, because these manifests
  are untracked and gitignored: there is no `git checkout --` to undo an in-place edit.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The field names the reproducibility checker looks for. Exported so a checker can import
# this instead of hardcoding the list a second time and drifting from it.
AUDIT_FIELDS = ("canitford_git_commit", "grid_density", "mesh_sha256",
                "solver_git_sha", "vehicle_mass", "bulk_modulus")

# Declared vocabulary, strongest first. _label() rejects anything not in here, so a new
# category cannot enter the output undeclared the way Vista's `inferred` did.
CONFIDENCE = ("recorded", "aliased", "derived", "resolved",
              "inapplicable", "reconstructed", "unknown")

# vehicle_geometry_research/yaris_coarse_v1l_watertight.ply, register E1.
CANONICAL_YARIS_PLY = REPO / "vehicle_geometry_research" / "yaris_coarse_v1l_watertight.ply"

# hull_m3 -> (label, sha256, source). Tolerance is absolute, in m3.
# Yaris appears at two precisions in the manifests, 3.542739 and 3.542738790016075.
KNOWN_HULLS = {
    3.542739: ("yaris_coarse_v1l_watertight.ply", None,
               "computed live from the repo file"),
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

# Water EOS constants, from driver source, NOT from any manifest. See the module
# docstring for the cross-check that validates them before they are used.
RHO_W = 1000.0
GAMMA = 1.1
RHO_GAMMA_SOURCE = ("renders/yaris_render_s1/sim_standing.py:225 (c = sqrt(1.1 * "
                    "bulk_modulus / water_density)); simulation/validate_coupling_"
                    "force.py:18,19,22 (RHO_W=1000.0, BULK=1.5e5, GAMMA=1.1)")

# Family definitions. `detect` reads document SHAPE, never the path, because the same
# family lives at different paths on different machines. Each field maps to an ordered
# list of dotted lookup paths: the first that resolves wins, and whether it is the
# audited name itself decides `recorded` versus `aliased`.
FAMILIES = {
    "run_manifest": {
        "detect": lambda d: "hull_m3" in d or "solid_volume_m3" in d,
        "glob": "*summary.json",
        "fields": {
            "vehicle_mass": ["vehicle_mass", "mass_kg"],
            "grid_density": ["grid_density", "n_grid"],
            "bulk_modulus": ["bulk_modulus"],
            "solver_git_sha": ["solver_git_sha"],
            "canitford_git_commit": ["canitford_git_commit"],
            "mesh_sha256": ["mesh_sha256"],
        },
        "sound_speed": ["sound_speed_ms"],
    },
    "coupling_validation": {
        "detect": lambda d: isinstance(d.get("geometry"), dict)
                            and "box_side_m" in d["geometry"],
        "glob": "*.json",
        "fields": {
            "vehicle_mass": ["vehicle_mass", "geometry.box_mass_kg"],
            "grid_density": ["grid_density", "geometry.n_grid"],
            "bulk_modulus": ["bulk_modulus"],
            "solver_git_sha": ["solver_git_sha", "provenance.pinned_sha"],
            "canitford_git_commit": ["canitford_git_commit"],
            "mesh_sha256": ["mesh_sha256"],
        },
        "sound_speed": ["geometry.sound_speed"],
    },
}

# Positive evidence that a collider is a procedural cube, so mesh_sha256 is genuinely
# inapplicable rather than merely missing. Verified present in 21/21 on 2026-08-13.
PROCEDURAL_BOX_KEYS = ("geometry.box_side_m", "geometry.box_volume_m3",
                       "geometry.box_particles_per_side")


def _label(kind: str) -> str:
    """Gate every confidence label through the declared vocabulary.

    Vista's backfill emitted `inferred`, which its own CONFIDENCE tuple did not declare,
    and nothing caught it: audit_block() defaulted unknown labels through silently. An
    undeclared label is a bug in this file, so it raises here rather than reaching a
    manifest.
    """
    if kind not in CONFIDENCE:
        raise ValueError(f"undeclared confidence label {kind!r}; declared: {CONFIDENCE}")
    return kind


def normalize_label(text) -> tuple[str, str | None]:
    """(controlled label, the original text if it was not already controlled).

    The first back-fill pass wrote FREE-TEXT SENTENCES into field_confidence, for example
    "aliased from mass_kg" and "RECONSTRUCTED from the manifest's mtime against git
    rev-list...". Those carry the right meaning but are not drawn from a fixed set, so a
    census over them yields one bucket per distinct sentence and cannot be summed, and no
    consumer can test them programmatically.

    Prior labels still WIN on meaning, which is what keeps a back-filled field from being
    relabelled `recorded` on a re-run. They are only re-expressed in the declared
    vocabulary, and the original sentence is preserved by the caller under
    detail[field]["prior_label"] so nothing is lost. Order matters: `reconstructed` is
    tested before the weaker prefixes because its sentence also contains other words.
    """
    if not isinstance(text, str):
        return _label("unknown"), None
    if text in CONFIDENCE:
        return text, None
    low = text.lower()
    for probe, label in (("reconstructed", "reconstructed"),
                         ("not reconstructable", "unknown"),
                         ("inapplicable", "inapplicable"),
                         ("aliased", "aliased"),
                         ("derived", "derived"),
                         ("resolved", "resolved"),
                         ("recorded", "recorded")):
        if probe in low:
            return _label(label), text
    return _label("unknown"), text


def _num(val) -> float | None:
    """A real number, or None. Never raises.

    Manifest values are arbitrary JSON, so a key can hold a dict or a string where a
    float is expected. A bare float() there raises mid-back-fill, which for a loop over
    dozens of manifests means aborting partway with some already rewritten. Returning
    None instead lets the caller record `unknown` with a reason and keep going.
    """
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        return None
    return float(val)


def dig(doc: dict, dotted: str):
    """Resolve a dotted path, returning (found, value). Absent and null are distinct."""
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def sha256_file(path) -> str | None:
    """SHA256 of a file, or None if it cannot be read."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(("git", "-C", str(repo)) + args,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return (out.stdout.strip() or None) if out.returncode == 0 else None


def pinned_solver_sha() -> tuple[str | None, str]:
    """Read the pin from its file rather than restating it, so it cannot go stale.

    Must never raise: a truncated checkout or an unmaterialised LFS pointer is a reason
    to leave solver_git_sha absent, not to abort the whole back-fill.
    """
    for rel in ("third_party/mpm-engine-544c93dd-solver-core/PINNED_SHA.txt",
                "third_party/mpm-engine-544c93dd/PINNED_SHA.txt"):
        p = REPO / rel
        if p.exists():
            toks = p.read_text(encoding="utf-8", errors="replace").strip().split()
            if toks and len(toks[0]) == 40:
                return toks[0], rel
    return None, "no usable PINNED_SHA.txt found (missing, empty, or not a 40-char sha)"


def repo_provenance(repo_root: Path) -> dict:
    """Commit state, including whether the tree was dirty.

    The dirty flag is not decoration. A bare commit SHA recorded against a run made from
    a modified tree overstates reproducibility: the SHA does not describe the code that
    ran. This repo is edited by concurrent sessions
    (docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md), so a clean-tree assumption is unsafe.
    """
    head = _git(repo_root, "rev-parse", "HEAD")
    if head is None:
        return {"commit": None, "dirty": None,
                "reason": f"not a git repo or git unavailable at {repo_root}"}
    status = _git(repo_root, "status", "--porcelain") or ""
    dirty_paths = [ln[3:] for ln in status.splitlines() if ln.strip()]
    return {
        "commit": head,
        "short": head[:10],
        "committed_at": _git(repo_root, "log", "-1", "--format=%cI"),
        "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(dirty_paths),
        "dirty_path_count": len(dirty_paths),
        "dirty_paths": dirty_paths[:40],
    }


def script_identity(script, repo_root: Path) -> dict:
    """Identity of the script that produced a run.

    Hashing it matters more than usual here: a run script UNTRACKED in git cannot be
    recovered from any commit SHA, so its content hash is the only durable pointer back
    to the code that ran. Vista's audit found exactly that case.
    """
    if script is None:
        script = sys.argv[0] if sys.argv and sys.argv[0] else None
    if not script:
        return {"path": None, "sha256": None, "reason": "no script path available"}
    p = Path(script).resolve()
    return {
        "path": str(p),
        "sha256": sha256_file(p),
        "tracked_in_git": _git(repo_root, "ls-files", "--error-unmatch", str(p)) is not None,
        "last_commit_touching": _git(repo_root, "log", "-1", "--format=%H", "--", str(p)),
    }


def commit_at_time(epoch: float, repo: Path) -> str | None:
    """Last commit at or before `epoch`, IN `repo`. RECONSTRUCTED, never recorded.

    `repo` must be the repository the manifest belongs to, which under --backfill is
    --root and NOT this script's own tree. The Vista clone shares no history with this
    one after b00bf7b, so a cross-repo id there would be unresolvable, not merely
    imprecise.

    SELF-INFLICTED HAZARD, and the reason mtime_basis_is_reliable is emitted below: an
    IN-PLACE back-fill rewrites the manifest and therefore updates its mtime. After that,
    this function resolves against the back-fill date, not the run date, and silently
    returns a later commit. The check is whether the mtime still predates the first
    back-fill; if it does not, the basis is reported unreliable rather than used quietly.
    """
    out = _git(repo, "rev-list", "-1", f"--before=@{int(epoch)}", "HEAD")
    return out or None


def resolve_hull(payload: dict):
    """(sha256 or None, label, source, note). Refuses on an unknown hull."""
    found, raw = dig(payload, "hull_m3")
    hull = _num(raw)
    if not found or hull is None:
        return (None, None, None,
                "manifest carries no numeric hull_m3, hull cannot be identified"
                if found else "manifest carries no hull_m3, hull cannot be identified")
    for known, (label, sha, source) in KNOWN_HULLS.items():
        if abs(hull - known) <= HULL_TOL_M3:
            if sha is None:
                if not CANONICAL_YARIS_PLY.exists():
                    return None, label, source, "canonical Yaris .ply not present in this tree"
                return sha256_file(CANONICAL_YARIS_PLY), label, source, ""
            return sha, label, source, ""
    return (None, None, None,
            f"hull_m3 {hull} matches no known hull within {HULL_TOL_M3} m3, refusing to "
            f"guess a digest. Add it to KNOWN_HULLS with a primary source first.")


def derive_bulk(payload: dict, family: dict):
    """(value or None, meta). Derives bulk = c^2 * rho / gamma and cross-checks it.

    Returns the DERIVED value only when the manifest does not already record one. Where
    both exist the recorded value wins and the derivation becomes a consistency check,
    reported in the meta, so a manifest that breaks the relation is surfaced rather than
    quietly overwritten.
    """
    c, c_src = None, None
    for path in family["sound_speed"]:
        found, val = dig(payload, path)
        if found and isinstance(val, (int, float)) and not isinstance(val, bool) and val:
            c, c_src = float(val), path
            break
    if c is None:
        return None, {"reason": "manifest records no numeric sound speed under "
                                + " or ".join(family["sound_speed"])}
    bulk = c ** 2 * RHO_W / GAMMA
    return bulk, {
        "formula": "bulk = sound_speed**2 * rho / gamma",
        "inputs": {"sound_speed": c, "sound_speed_key": c_src,
                   "rho": RHO_W, "gamma": GAMMA},
        "rho_gamma_source": RHO_GAMMA_SOURCE,
        "units": "Pa",
    }


def detect_family(payload: dict) -> str | None:
    for name, spec in FAMILIES.items():
        try:
            if spec["detect"](payload):
                return name
        except (TypeError, AttributeError):
            continue
    return None


def plan_for(path: Path, root: Path, first_backfill_epoch: float | None = None):
    """What this script would add to one manifest, and how it obtained each field."""
    # Strict UTF-8 on purpose. errors="ignore" would silently DROP undecodable bytes and
    # an in-place write would then persist the lossy payload over the original, which for
    # an untracked, gitignored manifest is unrecoverable. A manifest we cannot decode
    # exactly is one we must refuse to rewrite.
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return None, {"error": f"not valid UTF-8, refusing to rewrite: {exc}"}
    except (ValueError, OSError) as exc:
        return None, {"error": f"unreadable: {exc}"}
    if not isinstance(payload, dict):
        return None, {"error": "not a JSON object"}

    fam_name = detect_family(payload)
    if fam_name is None:
        return None, {"error": "matches no known manifest family, refusing to guess "
                               "its schema"}
    family = FAMILIES[fam_name]
    rel = path.relative_to(root).as_posix()
    add, how, refused, detail = {}, {}, {}, {}

    # --- fields resolvable straight out of the manifest, by name or by alias ---
    for target in ("vehicle_mass", "grid_density"):
        for src in family["fields"][target]:
            found, val = dig(payload, src)
            if found and val is not None:
                if src == target:
                    how[target] = _label("recorded")
                else:
                    add[target] = val
                    how[target] = _label("aliased")
                    detail[target] = (f"aliased from {src}; the value was always present, "
                                      f"under a name the audit did not look for")
                break
        else:
            refused[target] = _label("unknown")
            detail[target] = ("present under none of "
                              + ", ".join(family["fields"][target]))

    # --- bulk modulus: recorded wins, else derived, else refused ---
    found_bulk, bulk_val = dig(payload, "bulk_modulus")
    recorded_bulk = _num(bulk_val)
    derived, dmeta = derive_bulk(payload, family)
    if found_bulk and recorded_bulk is not None:
        how["bulk_modulus"] = _label("recorded")
        if derived is not None:
            rel_err = abs(derived - recorded_bulk) / abs(recorded_bulk or 1.0)
            detail["bulk_modulus"] = {
                "recorded_value": bulk_val,
                "cross_check_derived": derived,
                "relative_error": rel_err,
                "agrees": rel_err < 1e-9,
                **dmeta,
            }
            if rel_err >= 1e-9:
                detail["bulk_modulus"]["WARNING"] = (
                    "the recorded bulk modulus does NOT match the value derived from "
                    "this manifest's own sound speed. The recorded value is kept. One of "
                    "the two is wrong; do not publish either until resolved.")
    elif derived is not None:
        add["bulk_modulus"] = derived
        how["bulk_modulus"] = _label("derived")
        detail["bulk_modulus"] = dmeta
    else:
        orphan = any(rel == o or rel.startswith(o + "/") for o in ORPHAN_DIRS)
        refused["bulk_modulus"] = _label("unknown")
        detail["bulk_modulus"] = (
            dmeta.get("reason", "no sound speed") + ", so K = c^2*rho/gamma has no input"
            + (". Also an ORPHAN rollout per register D4a, matching no canonical run, so "
               "a value here would make it look traceable when it is not" if orphan else ""))

    # --- mesh digest: resolve by hull, or assert inapplicable on positive evidence ---
    found_mesh, mesh_val = dig(payload, "mesh_sha256")
    if found_mesh and mesh_val is not None:
        how["mesh_sha256"] = _label("recorded")
    else:
        sha, label, source, note = resolve_hull(payload)
        if sha:
            add["mesh_sha256"] = sha
            how["mesh_sha256"] = _label("resolved")
            detail["mesh_sha256"] = f"matched by hull_m3 to {label} ({source})"
        elif all(dig(payload, k)[0] for k in PROCEDURAL_BOX_KEYS):
            how["mesh_sha256"] = _label("inapplicable")
            detail["mesh_sha256"] = {
                "reason": "collider geometry is a procedural cube, so no mesh asset "
                          "exists to hash. This is a positive assertion, not a gap.",
                "evidence": list(PROCEDURAL_BOX_KEYS),
                "collider_kind": payload.get("collider_kind"),
            }
        else:
            refused["mesh_sha256"] = _label("unknown")
            detail["mesh_sha256"] = note

    # --- solver sha: the manifest's own pin first, then this tree's pin file ---
    for src in family["fields"]["solver_git_sha"]:
        found, val = dig(payload, src)
        if found and val:
            if src == "solver_git_sha":
                how["solver_git_sha"] = _label("recorded")
            else:
                add["solver_git_sha"] = val
                how["solver_git_sha"] = _label("aliased")
                detail["solver_git_sha"] = (
                    f"aliased from {src}. NOT missing: the pin was recorded on every run "
                    f"under a key name the audit did not look for.")
            break
    else:
        sha, src = pinned_solver_sha()
        if sha:
            add["solver_git_sha"] = sha
            how["solver_git_sha"] = _label("resolved")
            detail["solver_git_sha"] = f"read from the pin file {src}"
        else:
            refused["solver_git_sha"] = _label("unknown")
            detail["solver_git_sha"] = src

    # --- repo commit: the only field that is ever reconstructed ---
    found_c, cval = dig(payload, "canitford_git_commit")
    if found_c and cval:
        how["canitford_git_commit"] = _label("recorded")
    else:
        mtime = path.stat().st_mtime
        reliable = first_backfill_epoch is None or mtime < first_backfill_epoch
        c = commit_at_time(mtime, root)
        if c:
            add["canitford_git_commit"] = c
            how["canitford_git_commit"] = _label("reconstructed")
            detail["canitford_git_commit"] = {
                "basis": "the manifest's mtime, resolved with git rev-list -1 --before",
                "mtime_utc": datetime.fromtimestamp(mtime, timezone.utc).isoformat(),
                "mtime_basis_is_reliable": reliable,
                "warning": "NOT evidence of what ran. It cannot see whether the tree was "
                           "dirty, and this repo is edited by concurrent sessions. Treat "
                           "it as an upper bound on the code date, not an identity."
                           + ("" if reliable else " THIS MANIFEST'S mtime POSTDATES A "
                              "BACK-FILL, so the mtime reflects the back-fill, not the "
                              "run, and this value is resolved against the wrong date."),
            }
        else:
            refused["canitford_git_commit"] = _label("unknown")
            detail["canitford_git_commit"] = "no commit at or before the manifest mtime"

    return payload, {"rel": rel, "family": fam_name, "add": add, "how": how,
                     "refused": refused, "detail": detail}


def collect_run_provenance(script=None, mesh_paths=None, solver_source=None,
                           solver_pinned_sha=None, grid_density=None, vehicle_mass=None,
                           bulk_modulus=None, sound_speed=None, repo_root=None,
                           extra=None) -> dict:
    """FORWARD path. Call at run time; merge the result into the run's manifest.

    Everything here is RECORDED: the mesh is hashed from the file actually loaded, the
    commit is HEAD at the moment of the run, the solver sha is read from the pin. This is
    the only kind of provenance worth having; the back-fill path exists because these
    runs already happened without it.
    """
    root = Path(repo_root).resolve() if repo_root else REPO
    repo = repo_provenance(root)
    script_id = script_identity(script, root)

    meta, caveats = {}, []

    if mesh_paths is None:
        mesh_hashes = None
        meta["mesh_sha256"] = {
            "confidence": _label("inapplicable"),
            "reason": "caller passed mesh_paths=None: geometry is procedural, so no mesh "
                      "asset exists to hash. If a variant later loads a real hull, pass "
                      "its path and the digest is captured automatically.",
        }
    else:
        paths = [mesh_paths] if isinstance(mesh_paths, (str, os.PathLike)) else list(mesh_paths)
        mesh_hashes, missing = {}, []
        for m in paths:
            d = sha256_file(m)
            (missing.append(str(m)) if d is None
             else mesh_hashes.__setitem__(str(Path(m).resolve()), d))
        entry: dict = {
            "confidence": _label("recorded" if mesh_hashes else "unknown"),
            "source": "sha256 of the mesh files the run actually loaded",
        }
        if missing:
            entry["unreadable"] = missing
            entry["reason"] = "some mesh paths could not be read at capture time"
        meta["mesh_sha256"] = entry
        mesh_hashes = mesh_hashes or None

    solver_sha = solver_pinned_sha
    if solver_sha:
        meta["solver_git_sha"] = {"confidence": _label("recorded"),
                                  "source": "pin declared by the run script"}
    else:
        solver_sha, src = pinned_solver_sha()
        meta["solver_git_sha"] = ({"confidence": _label("resolved"), "source": src}
                                  if solver_sha else
                                  {"confidence": _label("unknown"), "reason": src})

    bulk = bulk_modulus
    if bulk is not None:
        meta["bulk_modulus"] = {"confidence": _label("recorded"),
                                "source": "constant supplied by the run script",
                                "units": "Pa"}
    elif (_c := _num(sound_speed)):
        bulk = _c ** 2 * RHO_W / GAMMA
        meta["bulk_modulus"] = {"confidence": _label("derived"),
                                "formula": "bulk = sound_speed**2 * rho / gamma",
                                "rho_gamma_source": RHO_GAMMA_SOURCE, "units": "Pa"}
    else:
        meta["bulk_modulus"] = {"confidence": _label("unknown"),
                                "reason": "neither a bulk modulus nor a sound speed given"}

    for name, val, note in (("grid_density", grid_density, "cells per axis"),
                            ("vehicle_mass", vehicle_mass, "rigid-body mass, kg")):
        meta[name] = {"confidence": _label("recorded" if val is not None else "unknown"),
                      "source": f"{note}, supplied by the run script at run time"}

    meta["canitford_git_commit"] = {
        "confidence": _label("recorded" if repo.get("commit") else "unknown"),
        "source": f"git rev-parse HEAD in {root}, read during the run",
        "tree_dirty_at_capture": repo.get("dirty"),
    }
    if repo.get("dirty"):
        caveats.append("the repo tree was DIRTY at capture: canitford_git_commit is an "
                       "exact HEAD but does not fully identify the code that ran. Use "
                       "script.sha256.")
    if script_id.get("tracked_in_git") is False:
        caveats.append(f"the run script is UNTRACKED in git ({script_id.get('path')}): no "
                       "commit SHA can recover it, and its sha256 is the only durable "
                       "pointer. This, not the field naming, is the substantive gap.")

    block = {
        "schema": "canitford.provenance/2",
        "mode": "recorded_at_run_time",
        "canitford_git_commit": repo.get("commit"),
        "grid_density": grid_density,
        "mesh_sha256": mesh_hashes,
        "solver_git_sha": solver_sha,
        "vehicle_mass": vehicle_mass,
        "bulk_modulus": bulk,
        "repo": repo,
        "script": script_id,
        "solver_source": str(solver_source) if solver_source else None,
        "_meta": meta,
        "_env": {
            "hostname": socket.gethostname(),
            "node": os.environ.get("SLURMD_NODENAME"),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "user": getpass.getuser(),
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{f"{m}_version": getattr(__import__(m), "__version__", None)
               for m in ("warp", "numpy", "torch") if _importable(m)},
        },
        "_caveats": caveats,
    }
    if extra:
        block["extra"] = dict(extra)
    return block


def _importable(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def in_scope(p: Path, root: Path) -> bool:
    """Scope test on the path RELATIVE to root, never the absolute path.

    Testing the absolute path made the filter depend on where root happens to live: any
    --root beneath a directory named `worktrees` (every git worktree under
    .claude/worktrees/, and this project's own scratchpad) matched the substring test on
    EVERY descendant, so the run found zero manifests, printed `manifests 0` and exited 0.
    A silent no-op that reads as "provenance already complete" is the worst possible
    failure for this script, so the test is anchored to root.
    """
    rel = p.relative_to(root)
    return (".git" not in rel.parts and "worktrees" not in rel.parts
            and not rel.as_posix().startswith("can-it-ford/")
            and not p.name.endswith(".provenance.json"))


def render(payload: dict, plan: dict) -> tuple[str, dict]:
    """(exact text a manifest should hold after back-fill, the block it will carry).

    A pure function, so the dry run and the write agree by construction and an
    already-correct manifest can be detected and left alone. The block is returned as
    well so callers report the EFFECTIVE labels after the prior-wins merge, not the
    fresh plan. Reporting the fresh plan would relabel an already-back-filled
    `reconstructed` field as `recorded` in the census while the file itself still says
    `reconstructed`: a census that overstates confidence is the exact defect this module
    exists to prevent, so there is only one place the merge happens.
    """
    out = dict(payload)
    out.update(plan["add"])
    prior = out.get("_provenance_backfill")
    block = dict(prior) if isinstance(prior, dict) else {}

    # A PRIOR BLOCK'S LABELS WIN. plan["how"] is computed from the manifest's CURRENT
    # contents, so once a field has been back-filled it is present and would be relabelled
    # `recorded` on any re-run. That is false: it was aliased, derived, resolved or
    # RECONSTRUCTED, and erasing the distinction would destroy the one thing this block
    # exists to carry. Keeping prior labels also makes re-running a no-op.
    def _merge(p, fresh):
        merged = dict(fresh)
        merged.update(p if isinstance(p, dict) else {})
        return merged

    # Prior meaning wins, but is re-expressed in the declared vocabulary, and whatever
    # free text it carried is preserved in detail[field]["prior_label"].
    #
    # `refused` is folded in so field_confidence carries ALL of AUDIT_FIELDS. A consumer
    # that reads one dict must not silently miss a field just because it was refused:
    # that would make an absent, unestablished value indistinguishable from one nobody
    # looked at. The `refused` key is still emitted separately, so the reason survives.
    refused_now = _merge(block.get("refused"), plan["refused"])
    conf, detail = {}, _merge(block.get("detail"), plan["detail"])
    for field, raw in {**refused_now,
                       **_merge(block.get("field_confidence"), plan["how"])}.items():
        label, original = normalize_label(raw)
        conf[field] = label
        if original is not None:
            d = detail.get(field)
            detail[field] = (dict(d) if isinstance(d, dict) else
                             {"note": d} if d is not None else {})
            detail[field]["prior_label"] = original

    block.update({
        "mode": "backfilled_after_the_fact",
        "date": "2026-08-13",
        "script": "analysis/run_provenance.py",
        "family": plan["family"],
        "field_confidence": conf,
        # Only fields that are STILL unestablished. A prior refusal must not outlive the
        # evidence: once a field becomes derivable (say an orphan gains a sound speed),
        # carrying the stale refusal alongside a `derived` label would make the block
        # contradict itself, and a reader cannot tell which half to believe.
        "refused": {k: normalize_label(v)[0] for k, v in refused_now.items()
                    if conf.get(k) == "unknown"},
        "detail": detail,
        "vocabulary": list(CONFIDENCE),
        "warning": "fields labelled `reconstructed` are INFERRED, not recorded. "
                   "params_check only tests presence, so passing that gate is necessary "
                   "and not sufficient. Read field_confidence, not just the keys.",
    })
    out["_provenance_backfill"] = block
    return json.dumps(out, indent=2, default=float) + "\n", block


def write_atomic(path: Path, text: str) -> None:
    """Temp file in the same directory, then os.replace.

    These manifests are untracked and gitignored, so there is no `git checkout --` to undo
    a partial write. A truncate-then-write interrupted by Ctrl-C, an OOM or a serialisation
    error leaves a permanently truncated manifest. os.replace is atomic within a
    filesystem, so a reader sees either the old file or the new one, never a fragment.
    """
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def discover(root: Path, family: str | None = None) -> list[Path]:
    """Every manifest under root, of either family, deduplicated and sorted."""
    seen: dict[Path, None] = {}
    globs = {"*summary.json"} | ({"*.json"} if family != "run_manifest" else set())
    for g in globs:
        for p in root.rglob(g):
            if g == "*.json" and "coupling_validation" not in p.as_posix():
                continue
            if in_scope(p, root):
                seen[p] = None
    return sorted(seen)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backfill", action="store_true", required=True)
    ap.add_argument("--write-sidecar", action="store_true",
                    help="write <manifest>.provenance.json; does NOT touch the manifest")
    ap.add_argument("--write-in-place", action="store_true",
                    help="edit the manifests themselves (atomic, but irreversible: they "
                         "are untracked and gitignored)")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--family", choices=sorted(FAMILIES), default=None,
                    help="restrict to one manifest family")
    a = ap.parse_args()

    if a.write_sidecar and a.write_in_place:
        print("choose one of --write-sidecar or --write-in-place, not both", file=sys.stderr)
        return 2
    root = Path(a.root).resolve()
    files = discover(root, a.family)

    # The mtime of the earliest existing back-fill marks the point after which an mtime
    # can no longer be trusted as a run date; see commit_at_time.
    stamps = [p.stat().st_mtime for p in files
              if b"_provenance_backfill" in p.read_bytes()[:1 << 20]]
    first_backfill = min(stamps) if stamps else None

    mode = ("WRITE SIDECARS" if a.write_sidecar else
            "WRITE IN PLACE" if a.write_in_place else
            "DRY RUN, nothing will be modified")
    print(f"root      {root}")
    print(f"manifests {len(files)}")
    print(f"mode      {mode}\n")

    fam_counts, conf_census, changed, written = {}, {}, 0, 0
    for p in files:
        payload, plan = plan_for(p, root, first_backfill)
        if payload is None:
            print(f"  SKIP {p.relative_to(root)}: {plan['error']}")
            continue
        fam_counts[plan["family"]] = fam_counts.get(plan["family"], 0) + 1
        new_text, block = render(payload, plan)

        # The EFFECTIVE label, after the prior-wins merge, never the fresh plan.
        for field in AUDIT_FIELDS:
            label = (block["field_confidence"].get(field)
                     or block["refused"].get(field) or "unknown")
            conf_census.setdefault(field, {})
            conf_census[field][label] = conf_census[field].get(label, 0) + 1

        if a.write_sidecar:
            merged = json.loads(new_text)
            side = p.with_name(p.name.removesuffix(".json") + ".provenance.json")
            body = json.dumps({**block,
                               **{k: merged[k] for k in AUDIT_FIELDS if k in merged}},
                              indent=2, default=float) + "\n"
            if not (side.exists() and side.read_text(encoding="utf-8") == body):
                if a.write_sidecar:
                    write_atomic(side, body)
                written += 1
            continue
        try:
            if new_text == p.read_text(encoding="utf-8"):
                continue                      # already correct, so a re-run is a no-op
        except (OSError, UnicodeDecodeError):
            pass
        changed += 1
        if a.write_in_place:
            write_atomic(p, new_text)

    print("manifests by family")
    for k, v in sorted(fam_counts.items()):
        print(f"  {k:<24} {v}")

    print("\nper-field confidence census")
    width = max(len(f) for f in AUDIT_FIELDS)
    for field in AUDIT_FIELDS:
        cens = conf_census.get(field, {})
        detail = ", ".join(f"{k}={v}" for k, v in
                           sorted(cens.items(), key=lambda kv: (-kv[1], kv[0])))
        print(f"  {field:<{width}}  {detail}")

    if a.write_sidecar:
        print(f"\nsidecars written or updated: {written}/{len(files)}")
    else:
        print(f"\nmanifests that would change: {changed}/{len(files)}")
    if not (a.write_sidecar or a.write_in_place):
        print("\nDRY RUN. Nothing was modified. --write-sidecar is the safe apply; "
              "--write-in-place edits the manifests irreversibly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
