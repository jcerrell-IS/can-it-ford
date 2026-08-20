#!/usr/bin/env python3
"""
r10 acquisition, third pass, shortlist only.

Pass 2 left 57 works that Unpaywall calls open access but that returned no
bytes, because gold and bronze links mostly land on publisher hosts that refuse
a bare client. This pass tries harder, but only for the works that bear on the
open questions, because reading ten relevant papers beats collecting fifty.

Three added routes over pass 2:
  1. a full browser header set including Referer, which is what most publisher
     PDF endpoints actually check
  2. scrape the landing page for a citation_pdf_url meta tag or a pdf anchor
  3. CORE, which aggregates repository copies

As in pass 2, a file counts only if its first four bytes are %PDF.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEST = "/Users/josie/can-it-ford-refs/2026-08-19-r10"
EMAIL = "josiecerrell69@gmail.com"

# shortlist: cite key -> why it is on the list
PRIORITY = {
    "Zha19e": "in/outflow BC, open question g, named in CLAUDE.md",
    "Bau23": "MPM spatial integration errors, open question a",
    "Zha17c": "incompressible MPM free surface, open question a",
    "Cha24c": "mixed MPM stabilization and validation, open question a",
    "Yan17": "MPM smoothing with embedded solids, open question a",
    "Gar19": "pressure on submerged bodies in SPH, open question a",
    "Jou20": "gradient corrected SPH, fully resolved particle-fluid, question a/c",
    "Mon09": "SPH particle boundary forces, open question c",
    "Fou19": "LUST boundary condition, open question a",
    "Ski13": "ISPH temporal noise, body-water slam, open question a/b",
    "Tao21b": "semi-fixed ghost particle boundary, open question a",
    "Zhe17": "solid boundary treatment for wave-float, open question a",
    "Li23f": "split-pressure MPS with virtual particle, open question a",
    "Vau20": "MPM after 25 years, review",
    "Xio24": "the one bibliography entry that is never cited",
    "Azh26": "vehicle stability under unsteady flow, 2026, open question e",
    "Sha20": "non-stationary vehicle Froude, open question d",
    "Alq22": "moving vehicle in floodwater, open question d",
    "Hu23": "stability thresholds at flow orientations, open question e",
    "Mar17": "stability threshold methodology, open question e",
    "Kra16": "trafficability of inundated roads, cited by the paper",
    "Qiu22": "gigascale MPM, resolution",
    "Wan20d": "multi-GPU MPM, resolution",
    "Dav24": "axisymmetric CFD heave of a spherical buoy, open question a",
}

BROWSER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def grab(url, referer=None, timeout=60):
    h = dict(BROWSER)
    if referer:
        h["Referer"] = referer
    else:
        p = urllib.parse.urlparse(url)
        h["Referer"] = "%s://%s/" % (p.scheme, p.netloc)
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read(), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, b"", url
    except Exception:
        return 0, b"", url


def pdf_links_from_html(body, base):
    out = []
    txt = body.decode("utf-8", "replace")
    m = re.search(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', txt, re.I)
    if m:
        out.append(m.group(1))
    m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']', txt, re.I)
    if m:
        out.append(m.group(1))
    for a in re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', txt, re.I)[:5]:
        out.append(urllib.parse.urljoin(base, a))
    return out


def unpaywall_urls(doi):
    try:
        req = urllib.request.Request(
            "https://api.unpaywall.org/v2/%s?email=%s" % (urllib.parse.quote(doi), EMAIL),
            headers=BROWSER)
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return []
    locs = d.get("oa_locations") or []
    locs.sort(key=lambda l: 0 if l.get("host_type") == "repository" else 1)
    urls = []
    for l in locs:
        for u in (l.get("url_for_pdf"), l.get("url")):
            if u and u not in urls:
                urls.append(u)
    return urls


def core_urls(doi):
    try:
        req = urllib.request.Request(
            "https://api.core.ac.uk/v3/search/works?q=" + urllib.parse.quote('doi:"%s"' % doi),
            headers=BROWSER)
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return []
    out = []
    for w in (d.get("results") or [])[:2]:
        if w.get("downloadUrl"):
            out.append(w["downloadUrl"])
    return out


def main(resolved, manifest):
    doi_of = {}
    with open(resolved) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3 and p[0] in PRIORITY:
                doi_of[p[0]] = p[2]
    os.makedirs(DEST, exist_ok=True)
    have = {f.split("_")[0] for f in os.listdir(DEST) if f.endswith(".pdf")}
    log = ["cite_key\tdoi\troute\thttp\tbytes\tis_pdf\turl\twhy"]
    got = []
    for key, why in PRIORITY.items():
        if key in have:
            print("%-8s ALREADY HAVE" % key, flush=True)
            continue
        doi = doi_of.get(key, "")
        if not doi:
            log.append("\t".join([key, "", "no-doi", "", "0", "NO", "", why]))
            print("%-8s NO DOI RESOLVED" % key, flush=True)
            continue
        cands = [("unpaywall", u) for u in unpaywall_urls(doi)]
        cands += [("doi.org", "https://doi.org/" + doi)]
        cands += [("core", u) for u in core_urls(doi)]
        landed = False
        for route, url in cands[:8]:
            code, body, final = grab(url)
            if body[:4] == b"%PDF":
                fn = "%s_%s.pdf" % (key, doi.replace("/", "_"))
                open(os.path.join(DEST, fn), "wb").write(body)
                log.append("\t".join([key, doi, route, str(code), str(len(body)), "YES", url, why]))
                print("%-8s GOT via %-10s %8d bytes" % (key, route, len(body)), flush=True)
                got.append(key)
                landed = True
                break
            if body[:15].lower().startswith(b"<!doctype html") or b"<html" in body[:400].lower():
                for p2 in pdf_links_from_html(body, final)[:3]:
                    c2, b2, _ = grab(p2, referer=final)
                    if b2[:4] == b"%PDF":
                        fn = "%s_%s.pdf" % (key, doi.replace("/", "_"))
                        open(os.path.join(DEST, fn), "wb").write(b2)
                        log.append("\t".join([key, doi, route + "+scrape", str(c2), str(len(b2)), "YES", p2, why]))
                        print("%-8s GOT via %-10s %8d bytes (scraped)" % (key, route, len(b2)), flush=True)
                        got.append(key)
                        landed = True
                        break
                if landed:
                    break
            log.append("\t".join([key, doi, route, str(code), str(len(body)), "NO", url, why]))
        if not landed:
            print("%-8s no bytes from %d candidate urls" % (key, len(cands[:8])), flush=True)
        time.sleep(0.2)
    open(manifest, "w").write("\n".join(log) + "\n")
    print("\nPRIORITY PDFS THIS PASS: %d  %s" % (len(got), ", ".join(got)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
