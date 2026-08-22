#!/usr/bin/env python3
"""
Re-run resolution with LOCAL TREES in the route list.

Commissioned after the third instance in one night of "we do not have it"
turning out to be "we never looked properly at what we already own". The trees
searched here were NOT in this slot's original brief:

    ~/can-it-ford-refs/            dated subdirectories, an existing ref store
    ~/Zotero/storage/
    ~/Downloads/vehicle_meshes/    never searched at all before tonight
    ~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/

Method, and it is the same one that closed the identity problem: Spotlight finds
candidates by exact phrase, then every candidate is opened and its own text is
matched against the wanted title with the SAME matcher the fetcher uses. A phrase
hit inside another paper's reference list is not a match, and the first version
of this slot's disk pass got that wrong and reported 156 of 230 present.

Excludes ~/can-it-ford-refs/2026-08-19-r10/, which is what this slot downloaded
tonight; counting it would be circular.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_verified import pdf_text, title_matches  # noqa: E402

TREES = [
    "/Users/josie/can-it-ford-refs",
    "/Users/josie/Zotero/storage",
    "/Users/josie/Downloads/vehicle_meshes",
    "/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13",
]
MINE = "can-it-ford-refs/2026-08-19-r10"


def all_pdfs():
    out = []
    for t in TREES:
        for root, _, files in os.walk(t):
            if MINE in root:
                continue
            for f in files:
                if f.lower().endswith(".pdf"):
                    out.append(os.path.join(root, f))
    return out


def mdfind_candidates(title, pool):
    probe = " ".join(title.replace('"', "").split()[:9])
    try:
        r = subprocess.run(
            ["mdfind", 'kMDItemTextContent == "%s"' % probe],
            capture_output=True, timeout=60)
        hits = r.stdout.decode("utf-8", "replace").splitlines()
    except Exception:
        hits = []
    hits = [h for h in hits if h.lower().endswith(".pdf") and MINE not in h]
    return [h for h in hits if any(h.startswith(t) for t in TREES)] or []


def main(wantlist, unreachable, out):
    titles = {}
    with open(wantlist) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                titles[p[0]] = p[3]
    keys = [l.strip() for l in open(unreachable) if l.strip()]
    pool = all_pdfs()
    print("local pool: %d pdfs across %d trees" % (len(pool), len(TREES)))
    print("checking %d works with no full text by any earlier route\n" % len(keys), flush=True)
    rows = ["cite_key\tverdict\tevidence\tfile\ttitle"]
    found = []
    for k in keys:
        want = titles.get(k, "")
        if not want:
            continue
        cands = mdfind_candidates(want, pool)
        hit = None
        for c in cands[:6]:
            ok, why = title_matches(pdf_text(c), want, strict=True)
            if ok:
                hit = (c, why)
                break
        if hit:
            found.append(k)
            rows.append("\t".join([k, "FOUND_LOCAL", hit[1], hit[0], want[:60]]))
            print("%-9s FOUND  %s" % (k, hit[0].replace("/Users/josie/", "~/")[:96]), flush=True)
        else:
            rows.append("\t".join([k, "ABSENT", "%d phrase candidates, none verified" % len(cands), "", want[:60]]))
    with open(out, "w") as fh:
        fh.write("\n".join(rows) + "\n")
    print("\nFOUND LOCALLY: %d of %d  (%s)" % (len(found), len(keys), ", ".join(found) or "none"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
