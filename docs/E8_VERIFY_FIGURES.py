#!/usr/bin/env python3
"""
Re-derive every headline figure in the D2 (E8 / credentials) document set.

WHY THIS EXISTS. Across this dispatch, stale or hand-computed figures were the
dominant defect: MiB labelled MB, a 14-file count that was 15, two hand-summed
totals, and 17 branch-count references that went stale when origin grew from 30
branches to 35 mid-dispatch. Each was caught by hand, late, and one of them was
caught only because a sibling session happened to mention a number.

So the figures are made falsifiable instead of trusted. Run this and every
numeric claim in the D2 documents is re-derived from git and compared against
what those documents say. It needs no network and no credentials.

    python3 docs/E8_VERIFY_FIGURES.py            # check against expected values
    python3 docs/E8_VERIFY_FIGURES.py --show     # just print what is measured

EXIT CODES: 0 all figures match, 1 at least one drifted.

A FAILURE HERE IS NOT NECESSARILY A BUG. Several of these figures are expected to
move: the branch count grows as work continues, and per-branch file presence
moves with it. A FAIL means "the documents no longer describe the repository",
which is a prompt to re-derive and update them, not evidence that anything is
wrong with the repo.

Scope note: this verifies the SHAPE of the exposure (what is where, how big).
It cannot verify the licence positions, which rest on reported permissions and
on pages fetched at a point in time. See E8_ACTION_INDEX_2026-08-17.md.
"""

import subprocess
import sys

REPO_HINT = "run from anywhere; the script locates the repo from its own path"

# Values as published in the D2 documents. Update these together with the docs.
EXPECTED = {
    "vgr_total_bytes": 176_252_809,
    "vgr_total_files": 30,
    "ccsa_verbatim_bytes_incl_readmes": 160_322_098,
    "ccsa_verbatim_bytes_excl_readmes": 160_308_908,
    "archives_bytes": 88_592_238,
    "archives_count": 4,
    "decks_bytes": 71_716_670,
    "decks_count": 14,
    "all_ply_bytes": 15_823_688,
    "all_ply_count": 4,
    "citations_total_bytes": 19_759_424,
    "citations_total_files": 38,
    "smith_group_bytes": 6_215_623,
    "smith_group_files": 16,
    "smith_screenshot_bytes": 5_846_160,
    "smith_screenshot_files": 15,
    "wrl_bytes": 760_091,
    "wrl_files": 3,
    "assets_cc0_bytes": 11_205_063,
    "assets_cc0_files": 6,
    # Measurements EXPECTED to change as the repo grows.
    "public_branches": 35,
    "branches_with_14_decks": 35,
    "branches_with_token_template": 34,
    "branches_with_secrets_env": 32,
    "branches_with_flag_doc": 1,
}

EXPECTED_TO_MOVE = {
    "public_branches",
    "branches_with_14_decks",
    "branches_with_token_template",
    "branches_with_secrets_env",
    "branches_with_flag_doc",
}


def repo_root():
    here = __file__.rsplit("/docs/", 1)[0]
    out = subprocess.run(
        ["git", "-C", here, "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit("not inside a git repository: " + here)
    return out.stdout.strip()


def git(root, *args):
    return subprocess.run(
        ["git", "-C", root] + list(args), capture_output=True, text=True
    ).stdout


def tree(root, ref, path):
    """Return {path: size}. Tab-aware: several filenames contain spaces."""
    out = git(root, "ls-tree", "-r", "--long", ref, path)
    result = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        meta, name = line.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 4 and parts[3].isdigit():
            result[name] = int(parts[3])
    return result


def measure(root):
    m = {}

    vgr = tree(root, "origin/main", "vehicle_geometry_research/")
    m["vgr_total_bytes"] = sum(vgr.values())
    m["vgr_total_files"] = len(vgr)

    zips = {k: v for k, v in vgr.items() if k.endswith(".zip")}
    keys = {k: v for k, v in vgr.items() if k.endswith(".key")}
    up_readmes = {
        k: v for k, v in vgr.items()
        if k.endswith("README.md") and "failed_reconstructions" not in k
    }
    plys = {k: v for k, v in vgr.items() if k.endswith(".ply")}

    m["archives_bytes"], m["archives_count"] = sum(zips.values()), len(zips)
    m["decks_bytes"], m["decks_count"] = sum(keys.values()), len(keys)
    m["all_ply_bytes"], m["all_ply_count"] = sum(plys.values()), len(plys)
    m["ccsa_verbatim_bytes_excl_readmes"] = m["archives_bytes"] + m["decks_bytes"]
    m["ccsa_verbatim_bytes_incl_readmes"] = (
        m["ccsa_verbatim_bytes_excl_readmes"] + sum(up_readmes.values())
    )

    cit = tree(root, "origin/main", "citations/")
    m["citations_total_bytes"] = sum(cit.values())
    m["citations_total_files"] = len(cit)

    smith = {k: v for k, v in cit.items() if "Smith-Modra-Felder/" in k}
    shots = {k: v for k, v in smith.items() if "/Screenshot" in k}
    wrl = {k: v for k, v in cit.items() if "WRL reports" in k}
    m["smith_group_bytes"], m["smith_group_files"] = sum(smith.values()), len(smith)
    m["smith_screenshot_bytes"] = sum(shots.values())
    m["smith_screenshot_files"] = len(shots)
    m["wrl_bytes"], m["wrl_files"] = sum(wrl.values()), len(wrl)

    assets = tree(root, "origin/main", "assets/")
    m["assets_cc0_bytes"], m["assets_cc0_files"] = sum(assets.values()), len(assets)

    # Per-branch presence. Local trees only; absent trees are reported, not skipped.
    rows = [ln.split() for ln in git(root, "ls-remote", "--heads", "origin").splitlines() if ln.strip()]
    m["public_branches"] = len(rows)
    with_decks = tok = sec = flag = absent = 0
    for row in rows:
        sha = row[0]
        have = subprocess.run(
            ["git", "-C", root, "cat-file", "-e", sha + "^{tree}"],
            capture_output=True,
        ).returncode == 0
        if not have:
            absent += 1
            continue
        names = set(git(root, "ls-tree", "-r", "--name-only", sha).splitlines())
        if sum(1 for n in names if n.startswith("vehicle_geometry_research/") and n.endswith(".key")) == 14:
            with_decks += 1
        if "token_setup_template.md" in names:
            tok += 1
        if "HANDOFF_AUDIT_2026-07-24/topics/security/secrets-and-env.md" in names:
            sec += 1
        if "docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md" in names:
            flag += 1
    m["branches_with_14_decks"] = with_decks
    m["branches_with_token_template"] = tok
    m["branches_with_secrets_env"] = sec
    m["branches_with_flag_doc"] = flag
    m["_trees_absent_locally"] = absent
    return m


def main():
    root = repo_root()
    m = measure(root)
    show_only = "--show" in sys.argv

    if m["_trees_absent_locally"]:
        print(
            f"NOTE: {m['_trees_absent_locally']} branch tree(s) not present locally and "
            "were not inspected. Run `git fetch origin` first for full coverage.\n"
        )

    width = max(len(k) for k in EXPECTED)
    failures = []
    for key, want in EXPECTED.items():
        got = m[key]
        if show_only:
            print(f"  {key:<{width}}  {got:,}")
            continue
        ok = got == want
        if not ok:
            failures.append((key, want, got))
        tag = "ok  " if ok else ("MOVED" if key in EXPECTED_TO_MOVE else "FAIL")
        note = "" if ok else f"   documented {want:,}, measured {got:,}"
        print(f"  [{tag}] {key:<{width}}  {got:,}{note}")

    if show_only:
        return 0

    print()
    if not failures:
        print("All figures match the D2 documents.")
        return 0

    moved = [f for f in failures if f[0] in EXPECTED_TO_MOVE]
    broken = [f for f in failures if f[0] not in EXPECTED_TO_MOVE]
    if moved:
        print(f"{len(moved)} figure(s) MOVED. These change as the repo grows and are")
        print("expected to: update EXPECTED here and the matching lines in the documents.")
    if broken:
        print(f"{len(broken)} figure(s) FAILED that were not expected to move.")
        print("Investigate before editing either the docs or this file.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
