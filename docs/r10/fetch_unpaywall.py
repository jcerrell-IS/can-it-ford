#!/usr/bin/env python3
"""
r10 acquisition, second pass.

The first pass used OpenAlex best_oa_location and hit 6 of 71, because that
field usually names a PUBLISHER endpoint and ScienceDirect, MDPI, Wiley and
Springer all refuse a plain client. This pass asks Unpaywall for EVERY oa
location and walks them repository-first, which is the half that tends to
serve bytes.

Destination is outside the git repo on purpose: can-it-ford is public and
licence question E8 is unresolved.

Every attempt is logged with its HTTP code and whether the bytes actually
begin %PDF, so "reached the URL" is never recorded as "got the paper".
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EMAIL = "josiecerrell69@gmail.com"
DEST = "/Users/josie/can-it-ford-refs/2026-08-19-r10"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.getcode(), r.read()


def unpaywall_locations(doi):
    url = "https://api.unpaywall.org/v2/%s?email=%s" % (
        urllib.parse.quote(doi), EMAIL)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return [], "UNPAYWALL_ERR:%s" % e
    locs = d.get("oa_locations") or []
    # repository first: institutional hosts serve a plain client, publishers mostly do not
    locs.sort(key=lambda l: 0 if l.get("host_type") == "repository" else 1)
    out = []
    for l in locs:
        for u in (l.get("url_for_pdf"), l.get("url")):
            if u:
                out.append((u, l.get("host_type") or "?", l.get("license") or "",
                            l.get("version") or ""))
    return out, d.get("oa_status", "?")


def main(resolved, manifest):
    rows = []
    with open(resolved) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3 and p[2]:
                rows.append((p[0], p[2]))
    os.makedirs(DEST, exist_ok=True)
    have = {f.split("_")[0] for f in os.listdir(DEST) if f.endswith(".pdf")}
    out = ["cite_key\tdoi\toa_status\thost_type\tlicense\tversion\thttp\tis_pdf\tbytes\tfile\turl"]
    got = 0
    for key, doi in rows:
        if key in have:
            print("%-9s SKIP already have" % key, flush=True)
            continue
        locs, oa = unpaywall_locations(doi)
        if not locs:
            out.append("\t".join([key, doi, str(oa), "", "", "", "", "NO", "0", "", ""]))
            print("%-9s %-8s no oa location" % (key, oa), flush=True)
            continue
        landed = False
        for url, host, lic, ver in locs[:4]:
            try:
                code, body = fetch(url)
            except urllib.error.HTTPError as e:
                code, body = e.code, b""
            except Exception:
                code, body = 0, b""
            ispdf = body[:4] == b"%PDF"
            if ispdf:
                fn = "%s_%s.pdf" % (key, doi.replace("/", "_"))
                with open(os.path.join(DEST, fn), "wb") as fh:
                    fh.write(body)
                got += 1
                landed = True
            else:
                fn = ""
            out.append("\t".join([key, doi, str(oa), host, lic, ver, str(code),
                                  "YES" if ispdf else "NO", str(len(body)), fn, url]))
            print("%-9s %-8s %-11s http=%-4s pdf=%-3s %8d" % (
                key, oa, host, code, "YES" if ispdf else "no", len(body)), flush=True)
            if ispdf:
                break
        if not landed:
            pass
        time.sleep(0.15)
    with open(manifest, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("\nNEW PDFS THIS PASS: %d" % got)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
