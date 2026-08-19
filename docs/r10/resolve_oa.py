#!/usr/bin/env python3
"""
r10 acquisition resolver.

For each want-list title: resolve a DOI via Crossref title query, then ask
OpenAlex whether an open-access full-text location exists, and record the URL.

Deliberately stdlib only: this Mac has no numpy in any interpreter
(see memory note "No Mac python has numpy"), so nothing here may import one.

Writes a TSV. It does NOT download anything; downloading is a separate,
reviewable step so that a licence decision is made per file.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

UA = "can-it-ford-r10-gapscan/1.0 (mailto:josiecerrell69@gmail.com)"


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def norm(s):
    return "".join(c.lower() for c in s if c.isalnum())


def crossref_doi(title, year):
    """Return (doi, matched_title, score) or (None, None, 0)."""
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 5})
    try:
        d = get("https://api.crossref.org/works?" + q)
    except Exception as e:
        return None, "CROSSREF_ERR:%s" % e, 0
    items = d.get("message", {}).get("items", [])
    want = norm(title)
    for it in items:
        t = (it.get("title") or [""])[0]
        if not t:
            continue
        got = norm(t)
        # accept on containment either way, which tolerates subtitle drift
        if want[:60] in got or got[:60] in want:
            return it.get("DOI"), t, it.get("score", 0)
    if items:
        t = (items[0].get("title") or [""])[0]
        return None, "NOMATCH_top=%s" % t[:70], items[0].get("score", 0)
    return None, "NORESULT", 0


def openalex_oa(doi):
    """Return (oa_status, best_pdf_url, landing, license)."""
    try:
        d = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi))
    except Exception as e:
        return "OA_ERR:%s" % e, "", "", ""
    best = d.get("best_oa_location") or {}
    oa = d.get("open_access") or {}
    pdf = best.get("pdf_url") or ""
    if not pdf:
        for loc in d.get("locations") or []:
            if loc.get("pdf_url"):
                pdf = loc["pdf_url"]
                break
    return (oa.get("oa_status", "?"), pdf,
            best.get("landing_page_url") or "", best.get("license") or "")


def main(path):
    rows = []
    with open(path) as fh:
        header = fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            rows.append(p)
    out = ["cite_key\tyear\tdoi\toa_status\tlicense\tpdf_url\tmatched_title"]
    for p in rows:
        key, year, have, title = p[0], p[1], p[2], p[3]
        doi, mt, _ = crossref_doi(title, year)
        if doi:
            oa, pdf, land, lic = openalex_oa(doi)
        else:
            oa, pdf, lic = "NO_DOI", "", ""
        out.append("\t".join([key, year, doi or "", oa, lic, pdf, (mt or "")[:90]]))
        print(out[-1], flush=True)
        time.sleep(0.12)
    with open(path.replace(".tsv", "_resolved.tsv"), "w") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
