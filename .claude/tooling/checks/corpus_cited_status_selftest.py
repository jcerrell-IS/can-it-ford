#!/usr/bin/env python3
"""Self-test for corpus_cited_status, the novelty guard.

WHY THIS EXISTS. Until 2026-08-18 corpus_cited_status set cited_in_repo from a
/usr/bin/grep over docs/, paper/ and CLAUDE.md, so any DOI written into a note
counted as a citation. The four vehicle-fording prior-art papers the tool names
in its own description therefore reported "cited" while none of them was ever
\\cite'd. docs/HANDOFF_ROUND_7_2026-08-18.md called it "a check that cannot
fail" and told sessions never to use it.

A fix for a check-that-cannot-fail needs a test that CAN fail, so this file
carries a positive control (a paper that really is cited, reached by DOI through
the same resolution path) alongside the negative cases. If the function ever
regresses to always-cited or always-uncited, one of the two halves goes red.

Zero dependencies. Python 3.9 safe. Exits non-zero on any failure.
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import corpus_mcp as C  # noqa: E402

FAILS = []


def check(label, got, want):
    ok = got == want
    print("  %-58s %s" % (label, "PASS" if ok else "FAIL (got %r want %r)" % (got, want)))
    if not ok:
        FAILS.append(label)


def test_parser_guards():
    """\\nocite, commented-out cites, and optional args, on a fixture."""
    print("parser guards, synthetic fixture")
    tmp = tempfile.mkdtemp(prefix="cited_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "paper"))
        with open(os.path.join(tmp, "paper", "x.tex"), "w") as fh:
            fh.write("\\nocite{*}\n% \\cite{commentedout}\n"
                     "Real \\cite{realkey} and \\citep[see][p.~3]{secondkey}.\n")
        with open(os.path.join(tmp, "paper", "x.bib"), "w") as fh:
            fh.write("@article{realkey, doi={10.1/real}}\n"
                     "@article{secondkey, doi={10.1/second}}\n"
                     "@article{commentedout, doi={10.1/commented}}\n"
                     "@article{nevercited, doi={10.1/never}}\n")
        saved, C.REPO = C.REPO, tmp
        try:
            keys, tex, err = C._paper_cite_keys()
            check("nocite{*} does not make everything cited", "nevercited" in keys, False)
            check("commented-out cite is not a citation", "commentedout" in keys, False)
            check("citep with optional args is read", "secondkey" in keys, True)
            check("exact key set", sorted(keys), ["realkey", "secondkey"])
            check("bib parsed", len(C._bib_entries()), 4)
        finally:
            C.REPO = saved
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_unreadable_paper_is_not_not_cited():
    """An unreadable paper/ must be its own state, never a quiet 'not cited'."""
    print("absence-of-evidence guard")
    saved, C.REPO = C.REPO, os.path.join(tempfile.gettempdir(), "no_such_repo_zzz")
    try:
        keys, tex, err = C._paper_cite_keys()
        check("missing paper/ reports an error", bool(err), True)
        check("missing paper/ yields no tex files", tex, [])
    finally:
        C.REPO = saved


def test_prior_art_against_the_real_paper():
    """The four papers the guard exists for, plus a positive control."""
    print("live repo, the four prior-art works this tool names")
    keys, tex, err = C._paper_cite_keys()
    if not tex:
        print("  SKIPPED: no readable .tex under %s/paper (%s)" % (C.REPO, err))
        return
    entries = C._bib_entries()

    for label, needle in (("He 2026", "10.1115/1.4071177"),
                          ("Wasfy 2015", "DETC2015-47142"),
                          ("Khapane 2014", "10.4271/2014-01-0936"),
                          ("Pazouki 2016", "pazouki2016fording")):
        r = C.corpus_cited_status(needle)
        if not r["in_bibliography"]:
            print("  SKIPPED %s: no .bib entry on this branch" % label)
            continue
        check("%s is in the .bib but NOT cited" % label, r["cited_in_paper"], False)

    # POSITIVE CONTROL. Without this the whole file would pass if the function
    # simply answered False every time.
    doi_re = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
    ctrl = None
    for k in sorted(keys):
        m = doi_re.search(entries.get(k, ""))
        if m:
            ctrl = (k, m.group(0).rstrip(".,}"))
            break
    if ctrl is None:
        print("  SKIPPED positive control: no cited key carries a DOI")
        return
    r = C.corpus_cited_status(ctrl[1])
    check("POSITIVE CONTROL %s reads as cited" % ctrl[0], r["cited_in_paper"], True)


if __name__ == "__main__":
    test_parser_guards()
    test_unreadable_paper_is_not_not_cited()
    test_prior_art_against_the_real_paper()
    print()
    if FAILS:
        print("FAILED: %d check(s): %s" % (len(FAILS), "; ".join(FAILS)))
        sys.exit(1)
    print("ALL CHECKS PASSED")
