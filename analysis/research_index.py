#!/usr/bin/env python3
"""Build and query a single index over every external research paper we hold.

WHY THIS EXISTS
---------------
The project's research lives in eight Undermind deep-research reports, 37 Claude
artifacts, five Perplexity reports and two Elicit extracts, spread across
`~/Downloads`, `~/Claude/reu`, `~/Documents/Claude` and a Desktop corpus. Two
consequences followed, both measured:

  1. 138 of 205 DOIs the reports catalogued are cited nowhere in the repo, and
     four prior vehicle-fording works sit in our own output while `paper/` cites
     none of them.
  2. Two whole reports, `Reliable_AI_Scientific_Software` (79 papers) and
     `MPM_Simulation_Verification_Provenance` (68), were never diffed against the
     bibliography at all.

Neither is a reading-effort problem. It is a retrieval problem: nothing in the
repo could answer "what do we already hold about X" or "is this DOI already
cited". This module is that answer, and it commits its index INTO the repo so it
survives a session, a machine, and a macOS privacy denial on `~/Downloads`.

DESIGN CHOICE THAT MATTERS
--------------------------
The index is built from the source reports but STORED in the repo at
`data/research_corpus_index.json`. Query paths never touch `~/Downloads`. A
prior session lost a whole pass because `~/Downloads` returned EPERM and a
recursive search silently reported zero hits instead of erroring. Reading the
committed index cannot fail that way.

USAGE
    python3 analysis/research_index.py --build          rebuild from sources
    python3 analysis/research_index.py --stats
    python3 analysis/research_index.py --method cpdi
    python3 analysis/research_index.py --query "added mass"
    python3 analysis/research_index.py --doi 10.1002/nme.7217
    python3 analysis/research_index.py --uncited --method boundary
    python3 analysis/research_index.py --gaps            uncited, most corroborated

Pure standard library.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "data", "research_corpus_index.json")

DL = os.path.expanduser("~/Downloads")
REU = os.path.expanduser("~/Claude/Projects/SCIPE UT Austin baby/REU_Knowledge")

REPORTS = [
    ("wall-penetration", f"{DL}/Quantitative_MPM_Wall_Penetration.md"),
    ("trustworthy-ai", f"{REU}/Trustworthy_AI_Assisted_Scientific_Simulation.md"),
    ("moving-rigid-body", f"{DL}/Moving_Rigid_Body_Free_Surface_Validation.md"),
    ("validated-coupling", f"{DL}/Validated_MPM_Vehicle_Water_Coupling.md"),
    ("settling-force", f"{DL}/Settling_and_Force_Reporting_in_Free_Surface_Flow.md"),
    ("mpm-verification", f"{DL}/MPM_Simulation_Verification_Provenance.md"),
    ("multi-resolution", f"{DL}/Multi-resolution_MPM_for_Large-domain_Flooding.md"),
    ("reliable-ai", f"{DL}/Reliable_AI_Scientific_Software.md"),
]

# Method tags. Each maps to regexes searched over title + abstract. These are the
# axes the project actually makes decisions on, so a tag exists only where a
# decision hangs on it.
METHOD_TAGS: dict[str, list[str]] = {
    "cpdi": [r"\bCPDI\b", r"convected particle domain"],
    "gimp": [r"\bGIMP\b", r"generalized interpolation material point"],
    "bspline": [r"B-?spline"],
    "incompressible-mpm": [r"incompressible material point", r"\biMPM\b",
                           r"operator splitting"],
    "immersed-fem": [r"immersed finite element", r"\bIFEMP\b",
                     r"immersed interface"],
    "amr-refinement": [r"adaptive mesh refinement", r"\bAMR\b",
                       r"mesh refinement", r"local refinement",
                       r"nested grid", r"mesh grading"],
    "particles-per-cell": [r"particles?[- ]per[- ]cell", r"\bPPC\b",
                           r"particle density"],
    "boundary-treatment": [r"boundary condition", r"boundary treatment",
                           r"ghost[- ]cell", r"image particle", r"slip wall",
                           r"boundary artefact", r"boundary artifact"],
    "wall-penetration": [r"penetration", r"smeared", r"tunnel"],
    "quadrature-error": [r"quadrature", r"integration error",
                         r"grid[- ]crossing", r"ringing"],
    "stationarity-uq": [r"stationar", r"autocorrelation", r"autocovariance",
                        r"effective sample", r"bootstrap", r"blocking",
                        r"confidence interval", r"uncertainty quantification",
                        r"equilibration", r"transient"],
    "reproducibility": [r"reproducib", r"bitwise", r"non-?associat",
                        r"deterministic", r"floating[- ]point"],
    "grid-convergence": [r"grid convergence", r"Richardson", r"\bGCI\b",
                         r"convergence index", r"discretization error"],
    "added-mass": [r"added mass", r"radiation damping", r"entrainment"],
    "drag-lift": [r"\bdrag\b", r"\blift\b", r"drag coefficient"],
    "vehicle-stability": [r"vehicle stab", r"incipient", r"flood.{0,20}vehicle",
                          r"vehicle.{0,20}flood", r"trafficab"],
    "vehicle-fording": [r"fording", r"wading", r"water crossing",
                        r"amphibious"],
    "validation-dataset": [r"benchmark", r"experimental data", r"public dataset",
                           r"validation data", r"towing tank", r"flume",
                           r"repeat runs?"],
    "dam-break": [r"dam[- ]break", r"dambreak"],
    "sloshing": [r"slosh"],
    "shallow-water": [r"shallow water", r"depth[- ]averag"],
    "inflow-outflow": [r"in/?outflow", r"inflow", r"outflow", r"open channel"],
    "sph-comparison": [r"\bSPH\b", r"smoothed particle"],
    "ai-reliability": [r"\bLLM\b", r"large language model", r"AI[- ]assisted",
                       r"agent", r"code generation", r"self[- ]review"],
    "provenance-gates": [r"provenance", r"continuous integration", r"\bCI\b",
                         r"pre-?commit", r"metamorphic", r"regression test",
                         r"manifest"],
}

HEAD = re.compile(r"^(\d+)\\?\.\s*·\s*(\d+)%\s*match\s*·\s*(\d{4})?\s*·?\s*"
                  r"([\d.]+)?\s*cit/yr", re.I)
# Permissive fallback. A Details header can omit the year or the cit/yr figure,
# and a strict pattern silently drops those papers: the strict form alone found
# 187 abstracts where the permissive form finds all of them.
HEAD_LOOSE = re.compile(r"^(\d+)\\?\.\s*·")
BOLD = re.compile(r"^\*\*(.+?)\*\*\s*(?:\(\[link\]\((\S+?)\)\))?")
RULE = re.compile(r"^-{10,}\s*$")
# catalog table row: | 12 | 2019 | 5.5 | Title ([link](url)) | Authors | Journal |
ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d{4})?\s*\|\s*([\d.]*)\s*\|\s*(.+?)\s*\|"
                 r"\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
LINK = re.compile(r"\[link\]\((\S+?)\)")


def collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def norm_doi(link: str) -> str:
    if not link:
        return ""
    m = re.search(r"doi\.org/(10\.[^\s)]+)", link, re.I)
    doi = m.group(1) if m else ""
    if not doi:
        return ""
    doi = doi.lower().rstrip(".,;)")
    doi = doi.replace("%28", "(").replace("%29", ")")
    return doi


def tags_for(text: str) -> list[str]:
    low = text
    out = []
    for tag, pats in METHOD_TAGS.items():
        if any(re.search(p, low, re.I) for p in pats):
            out.append(tag)
    return out


def parse_report(slug: str, path: str) -> dict[str, dict]:
    """Return {key: record}. Catalog rows first, then abstracts merged in."""
    if not os.path.isfile(path):
        return {}
    raw = open(path, encoding="utf-8", errors="replace").read()
    lines = raw.splitlines()
    recs: dict[str, dict] = {}

    det_at = len(lines)
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("### paper details"):
            det_at = i
            break

    # ---- catalog table, gives EVERY paper including abstract-less ones
    for ln in lines[:det_at]:
        m = ROW.match(ln)
        if not m:
            continue
        idx, year, cyr, title_cell, authors, journal = m.groups()
        if not idx.isdigit():
            continue
        lk = LINK.search(title_cell)
        link = lk.group(1) if lk else ""
        title = collapse(LINK.sub("", title_cell)).rstrip("( )")
        if not title or title.lower() == "title":
            continue
        doi = norm_doi(link)
        key = doi or f"{slug}#{idx}"
        recs[key] = {
            "doi": doi, "link": link, "title": title,
            "year": year or "", "cit_per_year": cyr or "",
            "authors": collapse(authors), "journal": collapse(journal),
            "abstract": "", "reports": [slug], "report_index": {slug: int(idx)},
            "has_abstract": False,
        }

    # ---- Paper Details, adds abstracts for the top-50 subset
    blocks, cur = [], []
    for ln in lines[det_at:]:
        if RULE.match(ln):
            if cur:
                blocks.append(cur)
                cur = []
            continue
        cur.append(ln)
    if cur:
        blocks.append(cur)

    for b in blocks:
        first = next((l for l in b if l.strip()), "")
        m = HEAD.match(first.strip()) or HEAD_LOOSE.match(first.strip())
        if not m:
            continue
        idx = int(m.group(1))
        title, link = "", ""
        for l in b:
            bm = BOLD.match(l.strip())
            if bm:
                title = collapse(bm.group(1))
                link = bm.group(2) or ""
                break
        abst = collapse(" ".join(l.lstrip("> ").rstrip("\\")
                                for l in b if l.strip().startswith(">")))
        doi = norm_doi(link)
        key = doi or f"{slug}#{idx}"
        # match back to the catalog row by index when the DOI is absent
        target = recs.get(key)
        if target is None:
            for r in recs.values():
                if r["report_index"].get(slug) == idx:
                    target = r
                    break
        if target is None:
            recs[key] = {
                "doi": doi, "link": link, "title": title, "year": "",
                "cit_per_year": "", "authors": "", "journal": "",
                "abstract": abst, "reports": [slug],
                "report_index": {slug: idx}, "has_abstract": bool(abst),
            }
        else:
            if abst:
                target["abstract"] = abst
                target["has_abstract"] = True
            if not target.get("title"):
                target["title"] = title
    return recs


# ---------------------------------------------------------------- documents
# Beyond the Undermind paper catalogs, the project holds RESEARCH DOCUMENTS:
# Claude.ai artifact exports, Perplexity reports and Elicit extracts. They are
# not papers, so they do not belong in the paper table, but they carry findings
# and they cite DOIs. Indexing them here is what lets a session ask "what have we
# already investigated about X" rather than only "which paper covers X".
ARTIFACT_ROOTS = [
    os.path.expanduser("~/Claude/reu"),
    os.path.expanduser("~/Documents/Claude/reu"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Downloads/perplexity research on claude gaps"),
    os.path.join(REPO, "citations"),
]
DOI_PAT = re.compile(r"10\.\d{4,9}/[^\s\"'<>)\]},;]+")
OFFTOPIC = re.compile(r"casio|fx-cg50|nightlife|course-prep|fall 2026|fren |phil ",
                      re.I)


def doc_type(path: str) -> str:
    b = os.path.basename(path).lower()
    if b.startswith("compass_artifact"):
        return "claude-artifact"
    if "perplexity" in path.lower():
        return "perplexity-report"
    if b.startswith("elicit"):
        return "elicit-extract"
    if b.endswith(".bib"):
        return "bibliography"
    return "document"


def index_documents() -> list[dict]:
    seen_hash: set[int] = set()
    out: list[dict] = []
    for root in ARTIFACT_ROOTS:
        if not os.path.isdir(root):
            continue
        for fn in sorted(os.listdir(root)):
            fp = os.path.join(root, fn)
            if not os.path.isfile(fp):
                continue
            ext = os.path.splitext(fn)[1].lower()
            if ext not in (".md", ".bib", ".csv"):
                continue
            dt = doc_type(fp)
            if dt == "document" and not fn.startswith("compass_artifact"):
                continue
            try:
                txt = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            h = hash(txt)
            if h in seen_hash:
                continue          # macOS sync duplicates, 6 to 9 copies each
            seen_hash.add(h)
            title = ""
            for ln in txt.splitlines():
                if ln.startswith("# "):
                    title = collapse(ln[2:])
                    break
            if not title:
                title = fn
            dois = sorted({m.lower().rstrip(".,;)") for m in DOI_PAT.findall(txt)})
            out.append({
                "path": fp.replace(os.path.expanduser("~"), "~"),
                "title": title,
                "type": dt,
                "on_topic": not bool(OFFTOPIC.search(title)),
                "n_chars": len(txt),
                "dois_referenced": dois,
                "methods": tags_for(f"{title} {txt[:20000]}"),
            })
    return out


def repo_cited_dois() -> tuple[set[str], set[str]]:
    """DOIs cited in the repo. Returns (anywhere, reader_facing).

    TWO SETS ON PURPOSE, because one number here is misleading.

    `anywhere` is every DOI-shaped string in the tracked tree. `reader_facing`
    is restricted to `paper/`, `docs/`, `deliverables/` and `citations/`, which
    is what a reviewer will actually see. The corpus's own 2026-08-14 diff learned
    this the hard way: Steffen 2008 read "uncited" on a narrow scan while its DOI
    sat in 13 repo files.

    EXCLUSIONS THAT MATTER. `.claude/worktrees/` is excluded, per the standing H0
    rule. A first version of this function did not exclude it and reported 269 of
    332 papers as cited, because another session's
    `r5-research/data/r5_citation_xref.tsv` holds 489 DOIs. A worktree is another
    session's scratch space, not this repo's bibliography. The index's own output
    file is excluded too, otherwise a rebuild reads its own previous answer and
    every paper self-certifies as cited.
    """
    pat = re.compile(r"10\.\d{4,9}/[^\s\"'<>)\]},;]+")
    exts = {".md", ".tex", ".bib", ".txt", ".json", ".py", ".csv", ".tsv",
            ".yaml", ".yml"}
    skip = {".git", "__pycache__", "node_modules", "third_party", ".venv",
            "worktrees", "_archive", "archive", "session_archive"}
    reader_dirs = ("paper", "docs", "deliverables", "citations")
    anywhere: set[str] = set()
    reader: set[str] = set()
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in skip]
        rel = os.path.relpath(root, REPO)
        top = rel.split(os.sep)[0]
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in exts:
                continue
            p = os.path.join(root, fn)
            if os.path.abspath(p) == os.path.abspath(INDEX):
                continue
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            hits = {m.lower().rstrip(".,;)") for m in pat.findall(txt)}
            anywhere |= hits
            if top in reader_dirs:
                reader |= hits
    return anywhere, reader


def build() -> dict:
    merged: dict[str, dict] = {}
    per_report = {}
    for slug, path in REPORTS:
        recs = parse_report(slug, path)
        per_report[slug] = len(recs)
        for key, r in recs.items():
            if key in merged:
                m = merged[key]
                for s in r["reports"]:
                    if s not in m["reports"]:
                        m["reports"].append(s)
                m["report_index"].update(r["report_index"])
                if r["abstract"] and not m["abstract"]:
                    m["abstract"] = r["abstract"]
                    m["has_abstract"] = True
                for f in ("year", "authors", "journal", "cit_per_year", "link"):
                    if not m.get(f) and r.get(f):
                        m[f] = r[f]
            else:
                merged[key] = dict(r)

    docs = index_documents()
    cited, reader = repo_cited_dois()
    for r in merged.values():
        r["methods"] = tags_for(f"{r['title']} {r['abstract']}")
        r["n_reports"] = len(r["reports"])
        r["cited_in_repo"] = bool(r["doi"]) and r["doi"] in cited
        r["cited_reader_facing"] = bool(r["doi"]) and r["doi"] in reader

    return {
        "built": "2026-08-15",
        "source_reports": {s: p for s, p in REPORTS},
        "papers_per_report": per_report,
        "n_papers": len(merged),
        "n_with_abstract": sum(1 for r in merged.values() if r["has_abstract"]),
        "n_cited_in_repo": sum(1 for r in merged.values() if r["cited_in_repo"]),
        "n_cited_reader_facing": sum(1 for r in merged.values()
                                     if r["cited_reader_facing"]),
        "n_no_doi_undiffable": sum(1 for r in merged.values() if not r["doi"]),
        "method_tags": sorted(METHOD_TAGS),
        "papers": merged,
        "documents": docs,
        "n_documents": len(docs),
        "n_documents_on_topic": sum(1 for d in docs if d["on_topic"]),
    }


def load() -> dict:
    if not os.path.isfile(INDEX):
        sys.exit(f"no index at {INDEX}. Run with --build first.")
    with open(INDEX, encoding="utf-8") as fh:
        return json.load(fh)


def show(r: dict, verbose: bool = False) -> None:
    if r.get("cited_reader_facing"):
        flag = "IN-PAPER"
    elif r["cited_in_repo"]:
        flag = "repo-only"
    else:
        flag = "UNCITED  "
    rep = "+".join(r["reports"])
    print(f"  [{flag}] {r['title'][:88]}")
    print(f"           {r['year']}  {r['doi'] or r['link'][:60] or '(no id)'}")
    print(f"           reports: {rep}")
    if r["methods"]:
        print(f"           methods: {', '.join(r['methods'])}")
    if verbose and r["abstract"]:
        print(f"           {r['abstract'][:600]}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--method")
    ap.add_argument("--query")
    ap.add_argument("--doi")
    ap.add_argument("--uncited", action="store_true")
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--docs", action="store_true",
                    help="search research DOCUMENTS (artifacts, Perplexity, "
                         "Elicit) instead of papers")
    a = ap.parse_args()

    if a.build:
        idx = build()
        os.makedirs(os.path.dirname(INDEX), exist_ok=True)
        with open(INDEX, "w", encoding="utf-8") as fh:
            json.dump(idx, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"wrote {INDEX}")
        print(f"  papers            {idx['n_papers']}")
        print(f"  with abstract     {idx['n_with_abstract']}")
        print(f"  cited anywhere    {idx['n_cited_in_repo']}")
        print(f"  reader-facing      {idx['n_cited_reader_facing']}"
              "   (paper/ docs/ deliverables/ citations/)")
        print(f"  no DOI, undiffable {idx['n_no_doi_undiffable']}")
        print(f"  documents          {idx.get('n_documents', 0)}"
              f"  ({idx.get('n_documents_on_topic', 0)} on-topic)")
        for s, n in idx["papers_per_report"].items():
            print(f"    {s:22} {n}")
        return 0

    idx = load()
    papers = list(idx["papers"].values())

    if a.docs:
        ds = [d for d in idx.get("documents", []) if d["on_topic"]]
        if a.method:
            ds = [d for d in ds if a.method.lower()
                  in [m.lower() for m in d["methods"]]]
        if a.query:
            q = a.query.lower()
            ds = [d for d in ds if q in d["title"].lower()]
        ds.sort(key=lambda d: -len(d["dois_referenced"]))
        print(f"{len(ds)} document(s)\n")
        for d in ds[:a.limit]:
            print(f"  [{d['type']}] {d['title'][:86]}")
            print(f"      {d['path']}")
            if d["methods"]:
                print(f"      methods: {', '.join(d['methods'][:8])}")
            if d["dois_referenced"]:
                print(f"      cites {len(d['dois_referenced'])} DOI(s)")
            print()
        return 0

    if a.stats:
        print(f"index built {idx['built']}   papers {idx['n_papers']}   "
              f"abstracts {idx['n_with_abstract']}   "
              f"cited {idx['n_cited_in_repo']}")
        print()
        print(f"{'method tag':24} {'papers':>7} {'uncited':>8}")
        print("-" * 41)
        for t in idx["method_tags"]:
            hits = [r for r in papers if t in r["methods"]]
            unc = [r for r in hits if not r["cited_in_repo"]]
            if hits:
                print(f"{t:24} {len(hits):7d} {len(unc):8d}")
        return 0

    sel = papers
    if a.method:
        sel = [r for r in sel if a.method.lower()
               in [m.lower() for m in r["methods"]]]
    if a.query:
        q = a.query.lower()
        sel = [r for r in sel
               if q in r["title"].lower() or q in r["abstract"].lower()]
    if a.doi:
        d = a.doi.lower().strip()
        sel = [r for r in sel if r["doi"] == d or d in r["doi"]]
    if a.uncited or a.gaps:
        # "uncited" means it never reaches a document a reader sees. That is the
        # gap that matters, not mere absence from the whole tree.
        sel = [r for r in sel if not r.get("cited_reader_facing")]

    sel.sort(key=lambda r: (-r["n_reports"], -len(r["methods"])))
    print(f"{len(sel)} match" + (f", showing {a.limit}"
                                 if len(sel) > a.limit else ""))
    print()
    for r in sel[:a.limit]:
        show(r, verbose=a.verbose or bool(a.doi))
    return 0


if __name__ == "__main__":
    sys.exit(main())
