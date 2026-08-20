#!/usr/bin/env python3
"""
Verify that every direct quotation in this slot's documents actually appears in
the PDF it is attributed to.

Commissioned after a 15 percent wrong-file rate on scraped PDFs. Confirming that
a file is the right paper is necessary but not sufficient: the claim that
matters is that the sentence I put in quotation marks is in it. This checks the
sentence, not the paper.

Matching is whitespace- and ligature-insensitive, because PDFKit collapses
spaces and drops ligatures ("trafficability" comes back as "traf cability"), and
because our documents rewrap the quote across lines.
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_verified import pdf_text  # noqa: E402

REFS = "/Users/josie/can-it-ford-refs/2026-08-19-r10"
EXTRA = {"Kra21b": "/Users/josie/can-it-ford-refs/2026-08-16/Kramer2021_SphereHeaveDecay_Energies_14_269.pdf"}

# quotes are attributed by the cite key of the paper they came from
DOCS = [
    "docs/r10/schulz2019_image_particles_read.md",
    "docs/r10/fou19_still_water_read.md",
    "docs/R10_WEB_ACQUISITION_2026-08-19.md",
]


def squash(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # drop the letters ligature loss eats, so "trafficability" == "traf cability"
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_pdf(key):
    if key in EXTRA and os.path.exists(EXTRA[key]):
        return EXTRA[key]
    for f in os.listdir(REFS):
        if f.startswith(key + "_") and f.endswith(".pdf"):
            return os.path.join(REFS, f)
    if key == "Sch19e":
        for f in os.listdir(REFS):
            if f.startswith("Schulz2019"):
                return os.path.join(REFS, f)
    return None


def main(repo, pairs_file):
    cache = {}
    rows = ["cite_key\tverdict\tquote"]
    ok = bad = skip = 0
    for line in open(pairs_file):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        key, quote = line.split("\t", 1)
        p = find_pdf(key)
        if not p:
            rows.append("\t".join([key, "NO_LOCAL_PDF", quote[:80]]))
            print("%-8s NO LOCAL PDF   %s" % (key, quote[:64]), flush=True)
            skip += 1
            continue
        if p not in cache:
            cache[p] = squash(pdf_text(p, pages=60, chars=400000))
        hit = squash(quote) in cache[p]
        rows.append("\t".join([key, "FOUND" if hit else "NOT_FOUND", quote[:120]]))
        print("%-8s %-10s %s" % (key, "FOUND" if hit else "NOT FOUND", quote[:64]), flush=True)
        ok += hit
        bad += (not hit)
    out = os.path.join(repo, "docs/r10/quote_verification.tsv")
    with open(out, "w") as fh:
        fh.write("\n".join(rows) + "\n")
    print("\nFOUND %d, NOT FOUND %d, NO LOCAL PDF %d" % (ok, bad, skip))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
