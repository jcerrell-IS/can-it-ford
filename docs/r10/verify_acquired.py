#!/usr/bin/env python3
"""
Verify every acquired PDF is the paper its filename claims, reusing the SAME
matcher the fetcher uses so the two cannot disagree.

This replaces verify_acquired.sh, whose own shell matcher reported Kra16 and
Mar17 as mismatches when both are correct: PDFKit drops the "ffi" in
"trafficability", and the published Mar17 title says "define stability
threshold" where the index says "define the stability threshold". Two tools with
two matchers produced two answers about the same file, which is the thing to
avoid.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_verified import pdf_text, title_matches  # noqa: E402


def main(wantlist, dest, out):
    titles = {}
    with open(wantlist) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                titles[p[0]] = p[3]
    rows = ["cite_key\tverdict\tevidence\tfile"]
    tally = {}
    for fn in sorted(os.listdir(dest)):
        if not fn.endswith(".pdf"):
            continue
        if fn.startswith("WRONG-FILE"):
            rows.append("\t".join(["-", "QUARANTINED", "kept as evidence of a fetch defect", fn]))
            tally["QUARANTINED"] = tally.get("QUARANTINED", 0) + 1
            continue
        key = fn.split("_")[0]
        if key == "Schulz2019":
            key = "Sch19e"
        want = titles.get(key, "")
        if not want:
            rows.append("\t".join([key, "NO_WANTED_TITLE", "not in want list", fn]))
            tally["NO_WANTED_TITLE"] = tally.get("NO_WANTED_TITLE", 0) + 1
            continue
        ok, why = title_matches(pdf_text(os.path.join(dest, fn)), want)
        v = "CONFIRMED" if ok else "MISMATCH"
        rows.append("\t".join([key, v, why, fn]))
        tally[v] = tally.get(v, 0) + 1
        print("%-9s %-10s %s" % (key, v, why), flush=True)
    with open(out, "w") as fh:
        fh.write("\n".join(rows) + "\n")
    print("\n" + "  ".join("%s=%d" % kv for kv in sorted(tally.items())))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
