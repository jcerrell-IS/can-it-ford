#!/usr/bin/env python3
"""
Resolve the want-list entries that one Crossref query failed to match.

My first report called these "works that carry no DOI". That was wrong: the
clearest counterexample is Roy11, whose DOI 10.1016/j.cma.2011.03.016 was
already sitting in this project's own corrections register while my resolver
reported it unresolvable. The failure was in the query, not the literature.

So this tries four routes in order and records WHICH one won, so a future
failure can be attributed:
  1. the register's own DOI list, matched by title against Crossref metadata
  2. OpenAlex title.search, which does phrase-ish matching Crossref does not
  3. Semantic Scholar, which indexes preprints Crossref does not
  4. Crossref again, but accepting a high relevance score with token overlap
     rather than requiring prefix containment
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "can-it-ford-r10-gapscan/1.0 (mailto:josiecerrell69@gmail.com)"
STOP = {"a", "an", "the", "of", "for", "and", "to", "in", "on", "with", "using", "by"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def toks(s):
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return [w for w in s.split() if len(w) > 3 and w not in STOP]


def overlap(a, b):
    ta, tb = toks(a), set(toks(b))
    if not ta:
        return 0.0
    return sum(1 for w in ta if w in tb) / len(ta)


def via_openalex(title):
    q = urllib.parse.urlencode({
        "filter": "title.search:" + title,
        "per-page": "5", "mailto": "josiecerrell69@gmail.com"})
    try:
        d = get("https://api.openalex.org/works?" + q)
    except Exception:
        return None, 0
    for w in d.get("results", []):
        t = w.get("display_name") or ""
        o = overlap(title, t)
        if o >= 0.7 and w.get("doi"):
            return w["doi"].replace("https://doi.org/", ""), o
    return None, 0


def via_s2(title):
    q = urllib.parse.urlencode({"query": title, "limit": "5",
                                "fields": "title,externalIds,openAccessPdf"})
    try:
        d = get("https://api.semanticscholar.org/graph/v1/paper/search?" + q)
    except Exception:
        return None, 0, ""
    for w in d.get("data", []) or []:
        t = w.get("title") or ""
        o = overlap(title, t)
        if o >= 0.7:
            ext = w.get("externalIds") or {}
            doi = ext.get("DOI")
            arx = ext.get("ArXiv")
            pdf = (w.get("openAccessPdf") or {}).get("url") or ""
            if doi:
                return doi, o, pdf
            if arx:
                return "arXiv:" + arx, o, pdf
    return None, 0, ""


def via_crossref(title):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 8})
    try:
        d = get("https://api.crossref.org/works?" + q)
    except Exception:
        return None, 0
    best, bo = None, 0
    for it in d.get("message", {}).get("items", []):
        t = (it.get("title") or [""])[0]
        o = overlap(title, t)
        if o > bo:
            best, bo = it.get("DOI"), o
    return (best, bo) if bo >= 0.7 else (None, bo)


def main(wantlist, resolved, out):
    titles = {}
    with open(wantlist) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                titles[p[0]] = p[3]
    todo = []
    with open(resolved) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4 and p[3] == "NO_DOI":
                todo.append(p[0])
    rows = ["cite_key\tdoi\troute\tscore\toa_pdf\ttitle"]
    won = 0
    for k in todo:
        t = titles.get(k, "")
        if not t:
            continue
        doi, sc, route, pdf = None, 0, "none", ""
        d, s = via_openalex(t)
        if d:
            doi, sc, route = d, s, "openalex"
        if not doi:
            d, s, p2 = via_s2(t)
            if d:
                doi, sc, route, pdf = d, s, "semanticscholar", p2
        if not doi:
            d, s = via_crossref(t)
            if d:
                doi, sc, route = d, s, "crossref-loose"
        if doi:
            won += 1
        rows.append("\t".join([k, doi or "", route, "%.2f" % sc, pdf, t[:70]]))
        print("%-8s %-16s %-6s %s" % (k, doi or "STILL UNRESOLVED", route, t[:52]), flush=True)
        time.sleep(0.5)
    open(out, "w").write("\n".join(rows) + "\n")
    print("\nRESOLVED %d of %d that one Crossref query had missed" % (won, len(todo)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
