#!/usr/bin/env python3
"""
r10 step 4: scan for recent work (2024 onward) that the project's own 21 deep
searches did not return.

Method: OpenAlex title/abstract search per topic, filtered to 2024-01-01
onward, then subtract anything already in the want list. The subtraction is
what makes a hit interesting; a paper the project already has is not news.

Matching against the want list is by normalised title, not DOI, because 49 of
the 230 want-list rows never resolved to a DOI and would otherwise look absent.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

UA = "can-it-ford-r10-gapscan/1.0 (mailto:josiecerrell69@gmail.com)"

TOPICS = [
    ("locking", '"material point method" AND (locking OR "pressure oscillation")'),
    ("locking-sph", 'SPH AND ("pressure oscillation" OR "tensile instability") AND remedy'),
    ("force-rigid", '"material point method" AND "rigid body" AND (force OR coupling)'),
    ("wellbalanced", '"well-balanced" AND (SPH OR "particle method") AND hydrostatic'),
    ("hydrostatic", 'particle method AND hydrostatic AND (equilibrium OR quiescent)'),
    ("fording", 'vehicle AND (fording OR wading) AND simulation'),
    ("floodveh", 'flood AND vehicle AND stability AND (experiment OR threshold)'),
    ("safespeed", 'vehicle AND flood AND "safe speed"'),
    ("safespeed2", 'floodwater AND vehicle AND (speed OR velocity) AND threshold AND depth'),
    ("buoyancy-err", '"buoyancy force" AND (SPH OR "material point method") AND error'),
    ("freesurf-est", '"free surface" AND (reconstruction OR elevation) AND particle AND error'),
]


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def norm(s):
    return "".join(c.lower() for c in s if c.isalnum())


def load_known(path):
    known = set()
    with open(path) as fh:
        fh.readline()
        for line in fh:
            p = line.split("\t")
            if len(p) >= 4:
                known.add(norm(p[3])[:55])
    return known


def main(wantlist):
    known = load_known(wantlist)
    print("want-list titles loaded: %d\n" % len(known))
    seen = set()
    for tag, q in TOPICS:
        params = {
            "search": q,
            "filter": "from_publication_date:2024-01-01,type:article|preprint",
            "per-page": "25",
            "sort": "relevance_score:desc",
            "mailto": "josiecerrell69@gmail.com",
        }
        try:
            d = get("https://api.openalex.org/works?" + urllib.parse.urlencode(params))
        except Exception as e:
            print("[%s] QUERY FAILED %s" % (tag, e))
            continue
        res = d.get("results", [])
        fresh = []
        for w in res:
            t = w.get("display_name") or ""
            n = norm(t)[:55]
            if not t or n in known or n in seen:
                continue
            seen.add(n)
            oa = (w.get("open_access") or {})
            best = w.get("best_oa_location") or {}
            fresh.append((t, w.get("doi") or "", w.get("publication_year"),
                          oa.get("oa_status", "?"), best.get("pdf_url") or "",
                          w.get("cited_by_count", 0)))
        print("[%s] %d returned, %d not already in the want list" % (tag, len(res), len(fresh)))
        for t, doi, yr, oa, pdf, cites in fresh:
            print("   %s (%s) oa=%s cites=%s" % (t[:96], yr, oa, cites))
            print("      %s" % (doi or "no doi"))
            if pdf:
                print("      pdf %s" % pdf[:130])
        print()
        time.sleep(0.3)


if __name__ == "__main__":
    main(sys.argv[1])
