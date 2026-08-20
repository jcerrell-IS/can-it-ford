#!/usr/bin/env python3
"""
r10 acquisition, FIFTH pass, and the one that cannot save a wrong file.

The earlier passes saved two documents that were not the requested paper: the
JCGM metrology vocabulary filed as Gro18, and a website Terms and Conditions
page filed as Arr19. Both came through the landing-page scrape, whose fallback
took the first .pdf anchor on the page when no citation_pdf_url meta tag existed.
Two wrong files out of thirteen scraped is a 15 percent error rate, and a
filename is exactly the thing that hides it.

THE FIX IS NOT A BETTER HEURISTIC. It is that nothing is saved until its own
text has been read and matched against the wanted title. A candidate that cannot
be verified is discarded, not renamed and kept. That makes a wrong file
impossible rather than unlikely.

Title matching tolerates two things learned the hard way:
  - PDFKit drops ligatures, so "trafficability" comes back as "traf cability"
    and "floodings" as "oodings". Comparison therefore strips the letters that
    ligatures eat rather than requiring an exact substring.
  - Published titles drift from index titles by small function words, e.g.
    "to define the stability threshold" against "to define stability threshold".
    So the test is token overlap, not prefix containment.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_priority import DEST, grab, unpaywall_urls, core_urls  # noqa: E402

SWIFT = os.path.join(HERE, "pdftext.swift")
STOP = {"a", "an", "the", "of", "for", "and", "to", "in", "on", "with", "using", "by"}


def pdf_text(path, pages=2, chars=4000):
    try:
        r = subprocess.run(["swift", SWIFT, path, str(pages), str(chars)],
                           capture_output=True, timeout=120)
        return r.stdout.decode("utf-8", "replace")
    except Exception:
        return ""


def toks(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return [w for w in s.split() if len(w) > 3 and w not in STOP]


def squash(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def title_matches(text, want):
    """True if the PDF's own opening text carries the wanted title."""
    if not text.strip():
        return False, "no text"
    # route 1: squashed containment, survives ligature loss only if none occur
    if squash(want)[:40] and squash(want)[:40] in squash(text):
        return True, "squashed containment"
    # route 2: token overlap, survives ligature loss and function-word drift
    wt = toks(want)
    if not wt:
        return False, "no usable tokens"
    tt = set(toks(text[:3000]))
    hit = sum(1 for w in wt if w in tt)
    # a ligature-damaged word will simply miss; require a clear majority
    frac = hit / len(wt)
    return (frac >= 0.6), "token overlap %d/%d = %.2f" % (hit, len(wt), frac)


def pdf_links(body, base):
    txt = body.decode("utf-8", "replace")
    out = []
    for pat in (r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']'):
        m = re.search(pat, txt, re.I)
        if m:
            out.append(m.group(1))
    for a in re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', txt, re.I)[:6]:
        out.append(urllib.parse.urljoin(base, a))
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def try_save(body, key, doi, want, route, url, log):
    """Write to a temp path, verify by reading it, keep only if it matches."""
    tmp = os.path.join(DEST, ".candidate_%s.pdf" % key)
    with open(tmp, "wb") as fh:
        fh.write(body)
    ok, why = title_matches(pdf_text(tmp), want)
    if ok:
        final = os.path.join(DEST, "%s_%s.pdf" % (key, doi.replace("/", "_")))
        os.replace(tmp, final)
        log.append("\t".join([key, doi, route, "KEPT", why, str(len(body)), url]))
        return True, why
    os.remove(tmp)
    log.append("\t".join([key, doi, route, "REJECTED", why, str(len(body)), url]))
    return False, why


def main(resolved, wantlist, manifest, only=None):
    titles = {}
    with open(wantlist) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                titles[p[0]] = p[3]
    rows = []
    with open(resolved) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4 and p[2] and p[3] not in ("closed", "NO_DOI", ""):
                rows.append((p[0], p[2]))
    have = {f.split("_")[0] for f in os.listdir(DEST)
            if f.endswith(".pdf") and not f.startswith("WRONG-FILE")}
    todo = [r for r in rows if r[0] not in have and (only is None or r[0] in only)]
    log = ["cite_key\tdoi\troute\toutcome\treason\tbytes\turl"]
    kept, rejected = [], []
    print("attempting %d\n" % len(todo), flush=True)
    for key, doi in todo:
        want = titles.get(key, "")
        if not want:
            continue
        cands = [("unpaywall", u) for u in unpaywall_urls(doi)]
        cands += [("doi.org", "https://doi.org/" + doi)]
        cands += [("core", u) for u in core_urls(doi)]
        done = False
        for route, url in cands[:6]:
            code, body, final = grab(url)
            if body[:4] == b"%PDF":
                ok, why = try_save(body, key, doi, want, route, url, log)
                if ok:
                    print("%-9s KEPT     via %-10s %s" % (key, route, why), flush=True)
                    kept.append(key)
                    done = True
                    break
                print("%-9s rejected via %-10s %s" % (key, route, why), flush=True)
                rejected.append(key)
                continue
            if b"<html" in body[:600].lower():
                for p2 in pdf_links(body, final)[:4]:
                    c2, b2, _ = grab(p2, referer=final)
                    if b2[:4] != b"%PDF":
                        continue
                    ok, why = try_save(b2, key, doi, want, route + "+scrape", p2, log)
                    if ok:
                        print("%-9s KEPT     via %-10s %s" % (key, route + "+scrape", why), flush=True)
                        kept.append(key)
                        done = True
                        break
                    print("%-9s rejected via %-10s %s" % (key, route + "+scrape", why), flush=True)
                    rejected.append(key)
                if done:
                    break
        if not done:
            print("%-9s no verified pdf" % key, flush=True)
    with open(manifest, "w") as fh:
        fh.write("\n".join(log) + "\n")
    print("\nKEPT %d, REJECTED-AS-WRONG %d" % (len(kept), len(set(rejected))))
    print("kept: %s" % ", ".join(kept))


if __name__ == "__main__":
    only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    main(sys.argv[1], sys.argv[2], sys.argv[3], only)
