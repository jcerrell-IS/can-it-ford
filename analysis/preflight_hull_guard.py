#!/usr/bin/env python3
"""Refuse a retracted vehicle hull by CONTENT, not by filename. Standalone preflight.

WHY THIS EXISTS AS A SEPARATE SCRIPT, AND NOT AS A DRIVER PATCH.

`renders/yaris_render_s1/sim_standing.py:73` guards retracted hulls with

    RETRACTED_HULL_TOKENS = ("candidate_euler",)

matched against `path.name` at :83-89. That blocks the two filenames under
`vehicle_meshes/candidates/` and blocks NOTHING ELSE. Verified live by sha256 on
2026-08-14, both retracted hulls are byte-identical to POOL files under different
names:

    5ef646213e00c86357a6b5c983fbd7b60fe40c0c93af93e0c260de4c2b924006
        candidates/rogue_candidate_euler-32.ply
        rogue_g96_pd6_coarse_watertight.ply              <- SAME BYTES, not blocked

    c9c58ca7b931d09dc6291280b08695a5eac87cad4283b8cd2a3bb66121759ba1
        candidates/silverado_candidate_euler-82.ply
        silverado_g32_pd8_dq0.02_coarse_watertight.ply   <- SAME BYTES, not blocked

A run pointed at either pool alias silently gets a hull 47.53 / 31.40 percent
below its own converged volume, which feeds buoyancy directly, with no refusal
and a plausible-looking log.

The driver is NOT patched here, deliberately. Editing it would change the driver
sha256 that stamps the completed matched-dx runs, and several other dispatches
share that file. This runs BESIDE the driver instead: before it, changing no
stamped digest and touching no shared file. The in-driver sha256 fix is handed to
D4 as a register entry, to be applied only once the matched-dx set is final.

THE DIGESTS ARE THE GUARD. A filename list is exactly what failed, so this file
names the retracted hulls by content and must never be rewritten to match names.

Usage
    python3 analysis/preflight_hull_guard.py --pool DIR [DIR ...]
    python3 analysis/preflight_hull_guard.py --check FILE [FILE ...]
    python3 analysis/preflight_hull_guard.py --pool DIR --check FILE

Exit 0 clean, 1 if any retracted hull is reachable or an approved hull's digest
does not match, 2 on usage error. Stdlib only: it must run on a machine with no
numpy, which is the case on this Mac.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

# Retracted 2026-08-08 by vehicle_meshes/candidates/SUMMARY.md. Selected on
# euler_number closest to 2, which selects for coarseness, which erodes volume,
# which feeds buoyancy. Percentages are that file's own re-measurement.
RETRACTED = {
    "5ef646213e00c86357a6b5c983fbd7b60fe40c0c93af93e0c260de4c2b924006": (
        "rogue pd6 hull, 2.597364 m3, 47.53 percent below its converged volume; "
        "aliases: candidates/rogue_candidate_euler-32.ply, "
        "rogue_g96_pd6_coarse_watertight.ply"),
    "c9c58ca7b931d09dc6291280b08695a5eac87cad4283b8cd2a3bb66121759ba1": (
        "silverado g32 dq0.02 hull, 5.462160 m3, 31.40 percent below its converged "
        "volume, only 2108 verts / 4380 faces; aliases: "
        "candidates/silverado_candidate_euler-82.ply, "
        "silverado_g32_pd8_dq0.02_coarse_watertight.ply"),
}

# The three qualified hulls. Digests verified live on the Mac and again on LS6 at
# the paths the runs actually read.
APPROVED = {
    "b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95":
        "yaris_coarse_v1l_watertight.ply, 3.542739 m3, compact_sedan",
    "c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2":
        "rogue_g96_pd8_coarse_watertight.ply, 4.950341 m3, midsize_suv",
    "46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9":
        "silverado_g96_pd8_coarse_watertight.ply, 7.962083 m3, "
        "AR&R large_4wd / vehicle_params light_pickup",
}

# Filenames the qualified hulls are expected to carry. Used ONLY to detect a
# name/content mismatch, never as the guard itself. The mesh pipeline is not
# bit-reproducible, so a regenerated hull legitimately has a different digest
# under the same name; that is reported as UNKNOWN, not as retracted.
EXPECTED_NAME = {
    "b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95":
        "yaris_coarse_v1l_watertight.ply",
    "c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2":
        "rogue_g96_pd8_coarse_watertight.ply",
    "46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9":
        "silverado_g96_pd8_coarse_watertight.ply",
}


_APPROVED_NAMES = set(EXPECTED_NAME.values())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(path: Path):
    """Return (status, digest, note). Status is RETRACTED / APPROVED / UNKNOWN."""
    d = sha256(path)
    if d in RETRACTED:
        return "RETRACTED", d, RETRACTED[d]
    if d in APPROVED:
        note = APPROVED[d]
        want = EXPECTED_NAME.get(d)
        if want and path.name != want:
            note += ("  NAME MISMATCH: approved content under the filename %r, "
                     "expected %r. Content wins; the file has been renamed or copied."
                     % (path.name, want))
        return "APPROVED", d, note
    # INVERTED CHECK, and it is the one that matters. A file CARRYING an approved
    # filename whose digest is not the matching approved digest is an impostor:
    # either a re-encode, a truncation, or a retracted hull renamed to look right.
    # Without this the guard printed "OK" and exited 0 on a retracted hull with one
    # byte appended and the canonical filename, which is exactly the disguise a
    # digest blacklist cannot catch on its own.
    if path.name in _APPROVED_NAMES:
        return "IMPOSTOR", d, (
            "carries the approved filename %r but its digest matches NO approved hull. "
            "A digest blacklist cannot catch a re-encode, so the name/digest pairing is "
            "checked in both directions." % path.name)
    return "UNKNOWN", d, "not in the approved or retracted set"


def main():
    p = argparse.ArgumentParser(
        description="Refuse a retracted vehicle hull by content, not by filename.")
    p.add_argument("--pool", nargs="*", default=[],
                   help="directories to scan recursively for *.ply")
    p.add_argument("--check", nargs="*", default=[],
                   help="explicit hull paths a run will actually read")
    p.add_argument("--require-approved", action="store_true",
                   help="also fail if any --check path is not an approved hull")
    a = p.parse_args()

    if not a.pool and not a.check:
        p.error("give --pool and/or --check")
    if a.require_approved and not a.check:
        p.error("--require-approved only constrains --check paths; it is a no-op with "
                "--pool alone. Pass --check, or drop the flag.")

    targets = []
    for d in a.pool:
        base = Path(d)
        if not base.is_dir():
            print("FAIL  --pool %s is not a directory. Refusing to exit 0 on a path "
                  "that scanned nothing." % base)
            return 1
        # rglob does not descend symlinked directories, and is case-sensitive while
        # the loader is not (vehicle_main.py:121 lowercases the suffix). os.walk with
        # followlinks and a lowercased suffix test closes both holes.
        found = []
        for root, _dirs, files in os.walk(base, followlinks=True):
            for fn in files:
                if Path(fn).suffix.lower() == ".ply":
                    found.append(Path(root) / fn)
        targets += sorted(found)
    checks = [Path(c) for c in a.check]
    for c in checks:
        if not c.exists():
            print("FAIL  --check path does not exist: %s" % c)
            return 1
    targets += checks

    if not targets:
        print("FAIL  nothing was scanned. Refusing to report OK on an empty scan.")
        return 1

    retracted_hits, unknown_checks, seen = [], [], set()
    print("%-10s %-16s %s" % ("status", "sha256[:16]", "path"))
    for t in sorted(set(targets)):
        status, digest, note = classify(t)
        print("%-10s %-16s %s" % (status, digest[:16], t))
        if status in ("RETRACTED", "IMPOSTOR"):
            retracted_hits.append((t, digest, note))
        if t in checks and status != "APPROVED":
            unknown_checks.append((t, digest, note))
        if status == "APPROVED":
            seen.add(digest)

    print()
    rc = 0
    if retracted_hits:
        rc = 1
        print("REFUSED: %d hull(s) are retracted-by-content or impostors carrying an "
              "approved filename with a non-approved digest." % len(retracted_hits))
        for t, d, note in retracted_hits:
            print("  %s" % t)
            print("    sha256 %s" % d)
            print("    %s" % note)
        print("  These are below their own converged volume, and volume feeds buoyancy")
        print("  directly. sim_standing.py's filename guard does NOT stop the aliases.")
    else:
        print("OK: no retracted hull digest present in anything scanned.")

    if a.require_approved and unknown_checks:
        rc = 1
        print("REFUSED: %d --check path(s) are not approved hulls:" % len(unknown_checks))
        for t, d, note in unknown_checks:
            print("  %s\n    sha256 %s\n    %s" % (t, d, note))

    missing = set(APPROVED) - seen
    if a.pool and missing:
        print("NOTE: %d approved hull(s) were not found in the scanned pool. That is "
              "not a failure; they may live elsewhere." % len(missing))
        for d in sorted(missing):
            print("  %s  %s" % (d[:16], APPROVED[d]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
