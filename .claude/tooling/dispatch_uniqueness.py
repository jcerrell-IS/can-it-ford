#!/usr/bin/env python3
"""Refuse to broadcast identical assignments to multiple sessions.

WHY. On 2026-08-14 the coordinator sent byte-identical prompts to 13 sessions
six times. Josie diagnosed it before the coordinator did:

    "now each session is doing the same thing without regard to each other"

Thirteen agents duplicating one another is worse than one agent, because it
also consumes thirteen confirmation queues and thirteen context windows.

A shared ADDENDUM is legitimate (everyone needs the same machine state). An
identical ASSIGNMENT is the bug. This tool separates the two: it hashes the
per-session dispatch bodies and refuses if any two match, while allowing a
named shared-addendum file to be common to all.

Usage:
    python3 dispatch_uniqueness.py ROUND3_D*.md
    python3 dispatch_uniqueness.py --shared ROUND3_SHARED.md ROUND3_D*.md

Exit 0 = all distinct. Exit 2 = duplicates found, named on stderr.
"""
import argparse
import hashlib
import os
import re
import sys

WS = re.compile(r"\s+")


def norm(text):
    """Whitespace- and case-insensitive, so cosmetic edits do not mask a
    duplicate assignment."""
    return WS.sub(" ", text.strip().lower())


def body_hash(path, shared_text=None):
    with open(path, "r", errors="replace") as fh:
        t = fh.read()
    if shared_text:
        # remove any verbatim inclusion of the shared addendum before hashing
        t = t.replace(shared_text, "")
    return hashlib.sha256(norm(t).encode()).hexdigest()[:16]


def jaccard(a, b):
    sa = set(norm(a).split())
    sb = set(norm(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--shared", default=None,
                    help="a file legitimately common to every dispatch")
    ap.add_argument("--near", type=float, default=0.90,
                    help="warn when two dispatches share this Jaccard fraction")
    a = ap.parse_args()

    shared_text = None
    if a.shared and os.path.exists(a.shared):
        shared_text = open(a.shared, "r", errors="replace").read()

    texts = {}
    hashes = {}
    for f in a.files:
        if not os.path.isfile(f):
            continue
        if a.shared and os.path.samefile(f, a.shared):
            continue
        texts[f] = open(f, "r", errors="replace").read()
        hashes[f] = body_hash(f, shared_text)

    if not hashes:
        sys.stderr.write("no dispatch files matched\n")
        return 0

    by_hash = {}
    for f, h in hashes.items():
        by_hash.setdefault(h, []).append(f)

    dupes = {h: fs for h, fs in by_hash.items() if len(fs) > 1}

    names = sorted(texts)
    near = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s = jaccard(texts[names[i]], texts[names[j]])
            if s >= a.near and hashes[names[i]] != hashes[names[j]]:
                near.append((names[i], names[j], s))

    print("checked %d dispatch file(s)" % len(hashes))
    for f in sorted(hashes):
        print("  %s  %s" % (hashes[f], os.path.basename(f)))

    rc = 0
    if dupes:
        rc = 2
        sys.stderr.write("\nIDENTICAL ASSIGNMENTS, refusing:\n")
        for h, fs in dupes.items():
            sys.stderr.write("  %s -> %s\n" % (h, ", ".join(os.path.basename(x) for x in fs)))
        sys.stderr.write(
            "\nEach session must receive work that is ITS OWN. A shared "
            "addendum is fine: pass it with --shared and it will be excluded "
            "from the hash.\n")
    if near:
        sys.stderr.write("\nNEAR-DUPLICATES (>= %.0f%% shared tokens):\n" % (a.near * 100))
        for x, y, s in near:
            sys.stderr.write("  %.0f%%  %s  vs  %s\n"
                             % (s * 100, os.path.basename(x), os.path.basename(y)))
    if rc == 0 and not near:
        print("\nOK: every dispatch is distinct.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
