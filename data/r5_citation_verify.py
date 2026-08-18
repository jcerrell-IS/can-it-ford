#!/usr/bin/env python3
"""Re-derive every published D1 citation count from source. Prints PASS/FAIL.

Why this exists
---------------
Unit 39 criticised an external audit because it published numbers with no script,
so nobody could reproduce them. I then did the same thing for my own citation
counts, which lived only in ad-hoc shell commands.

Units 50, 51 and 52 found three of twelve safe-to-cite rows were false, all of
them introduced when I compressed a correct unit into a one-line summary. Every
one of those would have been caught by this script, because it re-derives the
claim instead of restating it.

Usage
-----
    python3 data/r5_citation_verify.py

Exit status 0 if every claim reproduces, 1 otherwise.

Dependencies: standard library only.
"""

import csv
import os
import re
import sys

ELICIT = "citations/Elicit - extract-results-review-5e368aae-95c3-4774-a804-2dcc8899299e.csv"
TSV = ("/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/"
       "00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv")

results = []


def check(label, got, want, note=""):
    ok = got == want
    results.append((ok, label, got, want, note))
    return ok


# ---------------------------------------------------------------- Elicit CSV
def elicit_checks():
    if not os.path.exists(ELICIT):
        results.append((None, "Elicit CSV", "MISSING", ELICIT, "run from repo root"))
        return
    rows = list(csv.reader(open(ELICIT, newline="", encoding="utf-8", errors="replace")))
    data = rows[1:]
    check("Elicit data rows", len(data), 42)

    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())[:60]
    check("Elicit unique papers by title", len({norm(r[0]) for r in data if r[0].strip()}), 41)

    # A cell counts as substantive if a digit survives outside a trailing
    # "units not specified" clause. Row 40's "friction coefficient = up to 1.89,
    # units not specified" IS substantive; a naive negation regex drops it and
    # gives 8, which is the error unit 51 nearly published.
    def substantive(cell):
        if not re.search(r"\d", cell):
            return False
        body = re.split(r",?\s*units? not specified", cell, flags=re.I)[0]
        return bool(re.search(r"\d", body)) and not re.match(r"\s*not mentioned", body, re.I)

    thr = [i for i, r in enumerate(data, 1) if len(r) > 8 and substantive(r[8])]
    fri = [i for i, r in enumerate(data, 1) if len(r) > 9 and substantive(r[9])]
    check("threshold-reporting rows", len(thr), 9, f"rows {thr}")
    check("friction-reporting rows", len(fri), 9, f"rows {fri}")

    # Independent second test: the "Not mentioned..." prefix.
    nm = lambda c: bool(re.match(r"\s*not mentioned", c, re.I))
    check("threshold, 2nd test agrees", sum(1 for r in data if len(r) > 8 and not nm(r[8])), 9)
    check("friction, 2nd test agrees", sum(1 for r in data if len(r) > 9 and not nm(r[9])), 9)

    # The known duplicate pair must not be double counted.
    check("row 6 is the no-DOI twin", (data[5][6].strip(), data[5][2].strip()), ("2016", ""))
    check("row 16 carries the DOI", data[15][2].strip(), "10.1111/jfr3.12262")


# ------------------------------------------------- catalogued-but-never-cited
def tsv_checks():
    if not os.path.exists(TSV):
        results.append((None, "corpus TSV", "UNREADABLE", TSV,
                        "corpus root is partly TCC-denied; not a failure"))
        return
    rows = list(csv.reader(open(TSV, newline="", encoding="utf-8", errors="replace"), delimiter="\t"))
    data = [r for r in rows[1:] if len(r) >= 8]
    uncited = [r for r in data if r[7].strip().upper() in ("NO", "FALSE", "0", "")]
    cited = [r for r in data if r not in uncited]

    check("TSV data rows", len(data), 205)
    check("uncited anywhere", len(uncited), 138, "matches their README")
    check("cited somewhere", len(cited), 67, "matches their README")

    # Categories OVERLAP by design and must never be summed.
    cats = {
        "MPM method": r"material[- ]point|(?<![a-z])mpm(?![a-z])",
        "SPH": r"smoothed particle|(?<![a-z])sph(?![a-z])",
        "V&V / UQ": r"\bvalidat|\bverificat|uncertainty|\bV&V\b|convergence|reproducib|benchmark",
        "vehicle (loose)": r"vehicle|car\b|cars\b|automobil|truck|suv|wading",
    }
    want = {"MPM method": 37, "SPH": 12, "V&V / UQ": 30, "vehicle (loose)": 4}
    for name, pat in cats.items():
        rx = re.compile(pat, re.I)
        check(f"uncited: {name}", len([r for r in uncited if rx.search(r[1])]), want[name])

    vv = re.compile(cats["V&V / UQ"], re.I)
    vu, vc = len([r for r in uncited if vv.search(r[1])]), len([r for r in cited if vv.search(r[1])])
    check("V&V catalogued total", vu + vc, 35)
    check("V&V uncited rate, percent", round(100 * vu / (vu + vc)), 86)


# --------------------------------------------------------------- bibliographies
IEEE_BIB = "paper/can_it_ford_references_IEEE.bib"
LIVE_BIB = "deliverables/paper/overleaf/refs.bib"


def bib_checks():
    """Added unit 62. Its FIRST RUN falsified the unit-61 diagnosis it encoded.

    Unit 61 claimed the IEEE bib has 36 entries and that my long-reported 21 came
    from a too-strict regex (`^@[a-z]+\\{`, anchored and lowercase-only). WRONG.
    Both regexes agree on both copies. The difference is the BRANCH:

        worktree claude/r5-research   9,503 bytes   21 entries
        main     claude/add-ci-checks 16,906 bytes  36 entries

    commit ffc05d9 added 144 lines on claude/add-ci-checks, which my branch does
    not contain. So 21 was correct for this branch all along, and the "fourth
    regex failure" was a misdiagnosis. This function therefore asserts NEITHER
    number: it reports which checkout it read and flags a divergence instead.
    """
    import os as _os
    keys = {}
    for label, path in (("IEEE", IEEE_BIB), ("live", LIVE_BIB)):
        if not _os.path.exists(path):
            results.append((None, f"{label} bib", "ABSENT", path,
                            "live bib is gitignored under deliverables/; not a failure"))
            continue
        t = open(path, encoding="utf-8", errors="replace").read()
        k = re.findall(r"@\w+\{([^,]+),", t)
        keys[label] = set(k)
        blocks = re.split(r"\n(?=@)", t)
        ndoi = sum(1 for b in blocks if re.search(r"^\s*doi\s*=", b, re.I | re.M))
        nver = sum(1 for b in blocks if "VERIFY" in b)
        # NOT asserted against a fixed number: the IEEE bib differs BY BRANCH
        # (21 entries on claude/r5-research, 36 on claude/add-ci-checks).
        results.append((None, f"{label} bib entries", len(k), "branch-dependent",
                        f"{ndoi} with doi=, {nver} VERIFY. Report the branch, never a bare count"))

    if "IEEE" in keys and "live" in keys:
        check("bib keys shared by both", len(keys["IEEE"] & keys["live"]), 6)
        # The three findings that target the file the live paper does NOT use.
        for k in ("ccsa2010yaris", "alqadami2022", "martinezgomariz2018"):
            check(f"'{k}' absent from live bib", k in keys["live"], False)

    # REGRESSION GUARD, inverted from what unit 61 believed: the two regexes AGREE.
    # If they ever disagree, a genuinely too-strict pattern has crept in.
    if _os.path.exists(IEEE_BIB):
        t = open(IEEE_BIB, encoding="utf-8", errors="replace").read()
        naive = len(re.findall(r"^@[a-z]+\{([^,]+),", t, re.M))
        correct = len(re.findall(r"@\w+\{([^,]+),", t))
        check("bib regexes agree (unit 61 was a BRANCH diff, not a regex bug)",
              naive, correct, f"naive {naive} vs permissive {correct}")


elicit_checks()
tsv_checks()
bib_checks()

print(f"  {'':2} {'claim':38} {'got':>26}  {'want':>10}")
print(f"  {'-'*2} {'-'*38} {'-'*26}  {'-'*10}")
fails = 0
for ok, label, got, want, note in results:
    tag = "OK" if ok else ("--" if ok is None else "!!")
    if ok is False:
        fails += 1
    g = str(got)[:26]
    print(f"  {tag:2} {label:38} {g:>26}  {str(want)[:10]:>10}")
    if note:
        print(f"     {'':38} {note[:60]}")
print()
if fails:
    print(f"  {fails} CLAIM(S) FAILED TO REPRODUCE")
    sys.exit(1)
print("  every reproducible claim checks out")
