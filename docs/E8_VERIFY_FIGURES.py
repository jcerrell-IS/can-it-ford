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

EXIT CODES: 0 all figures match, 1 at least one changed.

On a mismatch it prints, per figure, the grep that locates every reference to it in
the document set, so updating is mechanical rather than a hunt through nine files.

A FAILURE HERE IS NOT NECESSARILY A BUG. Several of these figures are expected to
move: the branch count grows as work continues, and per-branch file presence
moves with it. A FAIL means "the documents no longer describe the repository",
which is a prompt to re-derive and update them, not evidence that anything is
wrong with the repo.

Scope note: this verifies the SHAPE of the exposure (what is where, how big).
It cannot verify the licence positions, which rest on reported permissions and
on pages fetched at a point in time. See E8_ACTION_INDEX_2026-08-17.md.
"""

import hashlib
import os
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
}

# Per-branch counts are deliberately NOT in EXPECTED. They moved 30 -> 35 -> 36 in
# three days, and each move cost a sweep of five documents to chase a number that was
# never the finding. What is actually claimed is an INVARIANT: every public branch
# carries the full set of decks, however many branches there are. That statement does
# not go stale when someone pushes a branch, so it is checked as a relation rather
# than compared to a constant. The counts are still printed, as observations.
INVARIANTS = [
    (
        "every public branch carries all 14 CCSA decks",
        lambda m: m["branches_with_14_decks"] == m["public_branches"],
        lambda m: f'{m["branches_with_14_decks"]} of {m["public_branches"]}',
    ),
    (
        "the credential FLAG document is public on exactly one branch",
        lambda m: m["branches_with_flag_doc"] == 1,
        lambda m: f'{m["branches_with_flag_doc"]} of {m["public_branches"]}',
    ),
]

# CCSA's PUBLISHED SHA384 values, transcribed from the two ccsa.gmu.edu model pages
# on 2026-08-17. These are external reference constants, not derived state: they are
# the upstream authority the local archives are checked against, and recording them is
# what makes the byte-identity finding reproducible offline. Without them, re-checking
# the single strongest E8 claim would mean re-fetching a page that can change or vanish.
CCSA_SHA384 = {
    "vehicle_geometry_research/2010-toyota-yaris-coarse-v1l.zip":
        "4f2b837ba0c85c2ef123a75201ac341c5de6763fb2768b818d41ec4c027af921aabea83f0069bfa8b457a56c44c34ed0",
    "vehicle_geometry_research/2010-toyota-yaris-detailed-v2j.zip":
        "f68913788cbe520709323f76214054f16bdbeeb2b7ddd6dad3f4defccb15a2b6e9df62d50146d17809e4155a786082c7",
    "vehicle_geometry_research/2007-chevrolet-silverado-coarse-v3a.zip":
        "1874a7fc4709082d80d7c1d4ae2385202e69275568e1f2fe816134178eb784dda9cae8c8274a8a68bbe678a1557898c5",
    "vehicle_geometry_research/2007-chevrolet-silverado-detailed-v3e.zip":
        "662312f50a80b7c2e42fa0f5845ea8fa89e275302da1a824f44d3d3bff51a4bb19df7b1c1c4d3f72fa43804109241006",
}


def check_archive_integrity(root):
    """Recompute SHA384 for each archive and compare to CCSA's published value."""
    results = []
    for path, published in CCSA_SHA384.items():
        blob = subprocess.run(
            ["git", "-C", root, "show", "origin/main:" + path],
            capture_output=True,
        ).stdout
        if not blob:
            results.append((path, "MISSING", 0))
            continue
        got = hashlib.sha384(blob).hexdigest()
        results.append((path, "IDENTICAL" if got == published else "DIFFERS", len(blob)))
    return results


# When a figure changes, the next person has to update EVERY reference to it across
# nine documents. Naming that task without giving the means is how a handoff wastes
# someone's afternoon, so each figure carries the search that locates its references.
# Values are grep -E patterns, matched against the docs/ set.
LOCATORS = {
    "public_branches": r"[0-9]+ (public )?branch|branches",
    "branches_with_14_decks": r"[0-9]+ of [0-9]+ (public )?branches",
    "branches_with_token_template": r"token_setup_template",
    "branches_with_secrets_env": r"secrets-and-env",
    "branches_with_flag_doc": r"FLAG_CREDENTIAL_EXPOSURE|1 of [0-9]+",
    "vgr_total_bytes": r"176,252,809|176\.25",
    "vgr_total_files": r"across 30\b|30 files",
    "ccsa_verbatim_bytes_incl_readmes": r"160,322,098|160\.32",
    "ccsa_verbatim_bytes_excl_readmes": r"160,308,908",
    "archives_bytes": r"88,592,238",
    "decks_bytes": r"71,716,670",
    "all_ply_bytes": r"15,823,688|15\.82",
    "citations_total_bytes": r"19,759,424|19\.76",
    "citations_total_files": r"38 files",
    "smith_group_bytes": r"6,215,623|6\.22",
    "smith_group_files": r"16 files|16 Smith",
    "smith_screenshot_bytes": r"5,846,160|5\.85",
    "smith_screenshot_files": r"15 screenshots",
    "wrl_bytes": r"760,091|0\.76",
    "wrl_files": r"3 WRL",
    "assets_cc0_bytes": r"11,205,063",
    "assets_cc0_files": r"6 files",
}

# Nothing in EXPECTED is expected to move any more: the values that grow are checked
# as invariants above instead. Kept so a future figure can be marked as growth.
EXPECTED_TO_MOVE = set()


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
    # FORCE_ABSENT=n pretends n trees are unfetched, so the refusal path above can be
    # exercised. A guard that has never been seen to fire is not a guard.
    force_absent = int(os.environ.get("FORCE_ABSENT", "0"))
    with_decks = tok = sec = flag = absent = 0
    for i, row in enumerate(rows):
        sha = row[0]
        if i < force_absent:
            absent += 1
            continue
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
    print("Invariants (these do not go stale when a branch is pushed):")
    # A branch whose tree is not present locally was never inspected, so it can neither
    # confirm nor deny an invariant about branch contents. Evaluating anyway would
    # report a missing FETCH as a missing DECK, which is a confident wrong answer.
    # Refuse instead, and say what to run. Same reasoning as D3's watcher refusing to
    # print a merge target once its single-append assumption stops holding.
    absent = m["_trees_absent_locally"]
    if absent:
        for label, _test, _fmt in INVARIANTS:
            print(f"  [ -- ] {label}: INDETERMINATE")
        print(f"         {absent} branch tree(s) were never inspected, so a shortfall")
        print("         here would be an unfetched branch, not a missing deck.")
        print("         Run:  git -C <repo> fetch origin  and re-run.")
        failures.append(("invariants_indeterminate", "evaluable", f"{absent} tree(s) unfetched"))
    else:
        for label, test, fmt in INVARIANTS:
            held = test(m)
            if not held:
                failures.append((label, "invariant", fmt(m)))
            print(f"  [{'ok  ' if held else 'FAIL'}] {label}: {fmt(m)}")
    print()
    print("Observed counts (informational, expected to grow, not checked):")
    for k in ("public_branches", "branches_with_14_decks",
              "branches_with_token_template", "branches_with_secrets_env",
              "branches_with_flag_doc"):
        print(f"        {k:<32} {m[k]}")

    print()
    print("Archive integrity, local bytes vs CCSA's published SHA384:")
    integrity_ok = True
    for path, verdict, size in check_archive_integrity(root):
        if verdict != "IDENTICAL":
            integrity_ok = False
        print(f"  [{'ok  ' if verdict == 'IDENTICAL' else 'FAIL'}] {verdict:<9} {size:>12,} B  {path.split('/')[-1]}")
    if not integrity_ok:
        print("  An archive no longer matches upstream. That is a content change, not a")
        print("  counting error: investigate before touching any document.")
        failures.append(("archive_integrity", "IDENTICAL", "mismatch"))

    print()
    if not failures:
        print("All figures match the D2 documents, and all four archives are")
        print("byte-identical to CCSA's published releases.")
        return 0

    moved = [f for f in failures if f[0] in EXPECTED_TO_MOVE]
    broken = [f for f in failures if f[0] not in EXPECTED_TO_MOVE]
    if moved:
        print(f"{len(moved)} figure(s) MOVED. These change as the repo grows and are")
        print("expected to: update EXPECTED here and the matching lines in the documents.")
    if broken:
        print(f"{len(broken)} figure(s) FAILED that were not expected to move.")
        print("Investigate before editing either the docs or this file.")

    print()
    print("TO UPDATE. For each figure above, edit EXPECTED in this file AND every")
    print("reference in the documents. These commands find the references:")
    print()
    for key, _want, _got in failures:
        pat = LOCATORS.get(key)
        if pat:
            print(f"  # {key}")
            print(f"  /usr/bin/grep -nE '{pat}' docs/E8_*.md docs/CREDENTIAL_ROTATION_CHECKLIST_*.md")
    print()
    print("Then re-run this script. A figure is not updated until it reads [ok  ] here")
    print("AND no stale value survives the grep: the two are different checks, and")
    print("only the second catches a reference you forgot existed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
