#!/usr/bin/env python3
"""
r10 acquisition, fourth pass: apply the pass-3 technique to EVERY remaining
open-access work, not just the shortlist.

Pass 3 established that the recoverable failures are open-access works whose
Unpaywall location is a publisher endpoint that refuses a bare client. The fix
is to fetch the landing page, read its citation_pdf_url meta tag, and re-request
that with a Referer header. On the 24-work shortlist that recovered 8.

This reuses fetch_priority's routines rather than reimplementing them, so the
two passes cannot drift apart.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_priority import DEST, grab, pdf_links_from_html, unpaywall_urls, core_urls  # noqa: E402


def main(resolved, manifest):
    rows = []
    with open(resolved) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            # column 3 is oa_status from OpenAlex; skip closed and unresolved
            if len(p) >= 4 and p[2] and p[3] not in ("closed", "NO_DOI", ""):
                rows.append((p[0], p[2], p[3]))
    os.makedirs(DEST, exist_ok=True)
    have = {f.split("_")[0] for f in os.listdir(DEST) if f.endswith(".pdf")}
    log = ["cite_key\tdoi\toa_status\troute\thttp\tbytes\tis_pdf\turl"]
    got = []
    todo = [r for r in rows if r[0] not in have]
    print("open-access rows: %d, already have: %d, attempting: %d\n"
          % (len(rows), len(rows) - len(todo), len(todo)), flush=True)
    for key, doi, oa in todo:
        cands = [("unpaywall", u) for u in unpaywall_urls(doi)]
        cands += [("doi.org", "https://doi.org/" + doi)]
        cands += [("core", u) for u in core_urls(doi)]
        landed = False
        for route, url in cands[:6]:
            code, body, final = grab(url)
            if body[:4] == b"%PDF":
                fn = "%s_%s.pdf" % (key, doi.replace("/", "_"))
                open(os.path.join(DEST, fn), "wb").write(body)
                log.append("\t".join([key, doi, oa, route, str(code), str(len(body)), "YES", url]))
                print("%-9s GOT via %-10s %9d" % (key, route, len(body)), flush=True)
                got.append(key)
                landed = True
                break
            if b"<html" in body[:600].lower():
                for p2 in pdf_links_from_html(body, final)[:3]:
                    c2, b2, _ = grab(p2, referer=final)
                    if b2[:4] == b"%PDF":
                        fn = "%s_%s.pdf" % (key, doi.replace("/", "_"))
                        open(os.path.join(DEST, fn), "wb").write(b2)
                        log.append("\t".join([key, doi, oa, route + "+scrape", str(c2), str(len(b2)), "YES", p2]))
                        print("%-9s GOT via %-10s %9d (scraped)" % (key, route, len(b2)), flush=True)
                        got.append(key)
                        landed = True
                        break
                if landed:
                    break
            log.append("\t".join([key, doi, oa, route, str(code), str(len(body)), "NO", url]))
        if not landed:
            print("%-9s %-8s no bytes" % (key, oa), flush=True)
    open(manifest, "w").write("\n".join(log) + "\n")
    print("\nRECOVERED THIS PASS: %d  %s" % (len(got), ", ".join(got)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
