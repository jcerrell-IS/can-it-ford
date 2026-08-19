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


# ---------------------------------------------------------------------------
# BIBLIOGRAPHY AUDIT  (--bib-audit)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS, and what defect it is built to avoid.
#
# This index could not answer a question about itself: "is the corpus a superset
# of the bibliography the paper actually ships?" It is not. But the reason
# nobody could check that claim was subtler than the claim itself.
#
# The shipped bib carries its DOIs inside `note = {doi: ...}` fields, not `doi =`
# fields. Exactly ONE of its 15 entries uses a real `doi =` key. So any audit
# that joins on the `doi` field alone sees one identifier and silently treats the
# other fourteen works as having no DOI at all. A previous census reported "11 of
# 14 cited works are absent from the 332" without recording HOW it matched, and
# that unrecorded matching step is what decided the answer.
#
# The defect class this avoids is the opposite of the one `d6-tooling` recorded
# in `docs/R8_TOOLING_PROVENANCE.md`: a checker whose corpus INCLUDES its own
# output, so everything self-certifies. Here the risk runs the other way, a
# checker whose corpus EXCLUDES the bibliography it is meant to audit, so
# everything reads as a gap. Both produce a confident number that measures the
# checker's own scope rather than the world.
#
# So every row this emits states the ROUTE by which the work was matched or
# failed to match, and carries the best rejected candidate with its score. A row
# reading "absent" is worth little. A row reading "absent, searched by DOI, by
# normalised title against all 332 records and against every catalogue row in all
# eight reports, and by first-author surname plus year, best candidate 0.31" is
# auditable by someone who was not here.

BIB_REF_DEFAULT = "overleaf/main:can_it_ford_references_IEEE.bib"
TEX_REF_DEFAULT = "overleaf/main:conference_101719_1.tex"

# Same-work threshold and related-work threshold, over title token Jaccard.
# Deliberately two numbers, not one. Anything between them is reported as
# UNCERTAIN rather than forced into present or absent, because the Shand 2011
# case is genuinely ambiguous: the corpus holds a 2011 Shand/Smith/Cox/Blacka
# work that is NOT the AR&R Stage 2 report the paper cites.
SAME_WORK = 0.75
RELATED = 0.40

_STOP = {"a", "an", "and", "for", "of", "the", "in", "on", "to", "with", "by",
         "via", "using", "from", "at", "as", "its", "is", "are", "a", "study"}

_DOI_ANY = re.compile(r"10\.\d{4,9}/[^\s\"'<>)\]},;]+")


def _toks(s: str) -> set:
    words = re.sub(r"[^a-z0-9]+", " ", s.lower()).split()
    return {w for w in words if len(w) > 2 and w not in _STOP}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _git_show(spec: str) -> str:
    """Read `rev:path` out of the repo. FATAL if the ref or path is absent."""
    import subprocess
    try:
        out = subprocess.run(["/usr/bin/git", "-C", REPO, "show", spec],
                             capture_output=True, text=True, timeout=60)
    except OSError as exc:
        sys.stderr.write(f"FATAL: cannot run git for {spec!r}: {exc}\n")
        raise SystemExit(2)
    if out.returncode != 0:
        sys.stderr.write(f"FATAL: `git show {spec}` failed rc={out.returncode}\n"
                         f"{out.stderr.strip()}\n"
                         "Name the ref explicitly. Bibliography counts differ "
                         "between origin/main, claude/add-ci-checks and "
                         "overleaf/main, so a bare count is wrong on two of the "
                         "three.\n")
        raise SystemExit(2)
    if not out.stdout.strip():
        sys.stderr.write(f"FATAL: {spec} is empty. Refusing to audit against an "
                         "empty bibliography, which would report every work as "
                         "absent.\n")
        raise SystemExit(2)
    return out.stdout


def require_source_reports() -> list:
    """Load all eight Undermind reports, or exit 2. Never returns partial.

    THIS ASSERTION IS FATAL ON PURPOSE. Seven of the eight reports live under
    `~/Downloads`. A macOS privacy denial there has previously made recursive
    search report ZERO hits silently while direct reads errored, and the standing
    `/usr/bin/grep` fix does not help with that failure mode, because the failure
    is at the directory-listing layer rather than in the shell `grep` function.

    A partial load would silently reclassify every work in the unread reports
    from "ingested then dropped" to "never ingested", which is the exact
    distinction this audit exists to make. So: all eight, non-empty, each parsing
    to at least one catalogue record, or nothing.

    Reachability is checked AT READ TIME, not at session start. Eight reports
    readable twenty minutes ago is not eight reports readable now.
    """
    loaded, problems = [], []
    for slug, path in REPORTS:
        if not os.path.isfile(path):
            problems.append(f"{slug:20} MISSING      {path}")
            continue
        try:
            txt = open(path, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            problems.append(f"{slug:20} UNREADABLE   {path}  ({exc})")
            continue
        if not txt.strip():
            problems.append(f"{slug:20} EMPTY        {path}")
            continue
        recs = parse_report(slug, path)
        if not recs:
            problems.append(f"{slug:20} ZERO RECORDS {path}")
            continue
        loaded.append({"slug": slug, "path": path, "text": txt,
                       "ntext": txt.lower(), "recs": recs})
    if problems or len(loaded) != len(REPORTS):
        sys.stderr.write(
            "FATAL: the eight source reports are not all reachable, so the "
            "never-ingested / dropped-in-merge distinction cannot be made.\n"
            "This is a hard stop, not a warning: a partial read would report "
            "works from the unread reports as never ingested.\n\n")
        for p in problems:
            sys.stderr.write("  " + p + "\n")
        sys.stderr.write(
            "\nIf these sit under ~/Downloads, check macOS privacy access for "
            "the terminal. A denial there returns zero hits silently.\n")
        raise SystemExit(2)
    return loaded


def parse_bib(text: str) -> list:
    """Parse BibTeX entries. Tolerant, brace-aware, standard library only."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key = m.group(1).lower(), m.group(2).strip()
        i, depth = m.start(), 0
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        entries.append({"type": etype, "key": key,
                        "fields": _bib_fields(text[m.end():i])})
    return entries


def _bib_fields(body: str) -> dict:
    out, i = {}, 0
    while i < len(body):
        m = re.compile(r"([A-Za-z]+)\s*=\s*").search(body, i)
        if not m:
            break
        name, j = m.group(1).lower(), m.end()
        if j < len(body) and body[j] == "{":
            depth, k = 0, j
            while k < len(body):
                if body[k] == "{":
                    depth += 1
                elif body[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            val, i = body[j + 1:k], k + 1
        else:
            k = body.find(",", j)
            k = k if k != -1 else len(body)
            val, i = body[j:k].strip().strip('"'), k + 1
        out[name] = collapse(val)
    return out


def bib_title(fields: dict) -> str:
    t = fields.get("title", "")
    t = re.sub(r"\\[a-zA-Z]+\s*", "", t)
    t = t.replace("{", "").replace("}", "")
    t = t.replace("---", " ").replace("--", "-")
    return collapse(t)


def bib_doi(fields: dict) -> str:
    """DOI from ANY field, not just `doi =`.

    THIS IS THE UNRECORDED MATCHING STEP. Nine of the fifteen shipped entries
    carry their DOI inside `note = {doi: 10.xxxx/yyyy}`; exactly one uses a real
    `doi =` key. A join on the `doi` field alone finds 1 of 15 and reports the
    other 14 as identifier-free, which is how a census can conclude "absent"
    about works whose DOI is sitting in the file.
    """
    for name in ("doi", "note", "url", "howpublished"):
        m = _DOI_ANY.search(fields.get(name, ""))
        if m:
            return m.group(0).lower().rstrip(".,;)")
    return ""


def bib_surname(fields: dict) -> str:
    a = fields.get("author", "").strip()
    if not a:
        return ""
    if a.startswith("{"):
        return collapse(a.strip("{} "))
    first = a.split(" and ")[0]
    if "," in first:
        return collapse(first.split(",")[0])
    parts = first.split()
    return collapse(parts[-1]) if parts else ""


def source_kind(e: dict) -> str:
    """What KIND of source this is. The explanatory column.

    An Undermind deep search returns peer-reviewed literature and preprints. It
    does not return a GitHub repository, a government safety campaign page, a
    crash-test finite-element model, or a 1999 SAE technical report. Absence of
    those from the corpus is a category boundary, not a sourcing defect, and
    reporting them in the same bucket as a missed journal paper inflates the gap.
    """
    f = e["fields"]
    blob = " ".join(f.values()).lower()
    if "arxiv" in blob:
        return "preprint"
    if "github.com" in blob:
        return "software"
    if e["type"] == "misc" and ("weather.gov" in blob or "howpublished" in f
                                and "url" in f.get("howpublished", "")):
        return "webpage"
    if e["type"] == "misc":
        return "model-or-dataset"
    if e["type"] == "techreport":
        return "techreport-or-standard"
    return "peer-reviewed"


def _best_by_title(want: set, cands: list) -> tuple:
    """(score, title, tag) of the closest candidate by title token Jaccard."""
    best = (0.0, "", "")
    for title, tag in cands:
        s = _jaccard(want, _toks(title))
        if s > best[0]:
            best = (s, title, tag)
    return best


def index_self_defects() -> list:
    """Defects the index can detect IN ITSELF, without leaving the repo.

    Found while auditing the bibliography, and worth a permanent detector because
    the failure is silent and it demotes a paper rather than erroring.

    `parse_report` pulls a DOI out of a catalogue row with a `[link](url)` regex.
    Two things defeat it together: some reports escape the brackets as
    `\\[link\\]`, and an ASCE-style DOI legitimately CONTAINS parentheses, so a
    non-greedy match to the first `)` truncates it. The row still becomes a
    record, but with an empty `doi` and the raw markdown left inside the `title`.

    Why that matters more than it looks. Cited-status is computed as
    `bool(r["doi"]) and r["doi"] in cited`, so a record with an empty DOI can
    NEVER be marked cited, however many times the repo cites it. The paper is
    silently moved into the "no DOI, undiffable" bucket and reads as unreached
    forever.
    """
    idx = load()
    out = []
    doi_in_text = re.compile(r"10\.\d{4,9}/\S+")
    for key, r in sorted(idx["papers"].items()):
        title = r.get("title", "")
        if r.get("doi"):
            continue
        m = doi_in_text.search(title)
        if not m:
            continue
        import urllib.parse
        # Strip the markdown tail without eating the DOI's OWN parentheses.
        # An ASCE DOI legitimately ends in `)`, so a blind rstrip(")") truncates
        # it. Peel trailing characters only while the parens are UNBALANCED.
        rec = urllib.parse.unquote(m.group(0)).lower()
        rec = rec.rstrip("\\")
        while rec and rec[-1] in ")\\" and rec.count(")") > rec.count("("):
            rec = rec[:-1].rstrip("\\")
        out.append({"key": key, "recovered_doi": rec,
                    "title": re.split(r"\s*\(?\\?\[link", title)[0].strip(),
                    "reports": ",".join(r.get("reports", []))})
    return out


# Snapshot of the Undermind workspace, read live 2026-08-19 from
# `inspect_deep_searches` on workspace 17299f2a-8dc8-438b-8c84-5abf19395e2c.
# THIS IS A DATED SNAPSHOT, NOT A LIVE VIEW, and it will go stale the next time
# anyone runs a deep search. It is recorded anyway because the alternative was
# nothing: the builder has no way to see the workspace, so without this the gap
# is invisible from inside the repo. Re-derive rather than trust:
#     inspect_deep_searches(workspace_id=..., names=[], status_only=True)
WORKSPACE_SNAPSHOT_DATE = "2026-08-19"
WORKSPACE_DEEP_SEARCHES = [
    # (name, created, relevant-paper count, ingested-as-slug or None)
    ("moving vehicle floodwater simulation open source implementations",
     "2026-08-19", 105, None),
    ("how computational researchers audit and defend simulation credibility",
     "2026-08-18", 92, None),
    ("MPM SPH buoyancy force overestimation and hydrostatic validation benchmarks",
     "2026-08-18", 32, None),
    ("GPU particle solver portability scaling and surrogate fidelity",
     "2026-08-18", 56, None),
    ("which realism effects change a flood vehicle stability verdict",
     "2026-08-18", 47, None),
    ("moving vehicle floodwater GPU particle simulation",
     "2026-08-18", 48, None),
    ("Moving Rigid Body Free Surface Validation", "2026-08-14", 44,
     "moving-rigid-body"),
    ("Settling and Force Reporting in Free Surface Flow", "2026-08-14", 68,
     "settling-force"),
    ("Quantitative MPM Wall Penetration", "2026-08-14", 16, "wall-penetration"),
    ("Multi-resolution MPM for Large-domain Flooding", "2026-08-14", 78,
     "multi-resolution"),
    ("Trustworthy AI Assisted Scientific Simulation", "2026-08-08", 13,
     "trustworthy-ai"),
    ("MPM Simulation Verification Provenance", "2026-08-07", 68,
     "mpm-verification"),
    ("Reliable AI Scientific Software", "2026-08-07", 79, "reliable-ai"),
    ("Validated MPM Vehicle Water Coupling", "2026-07-30", 60,
     "validated-coupling"),
    ("Simulation Ready Vehicle Mesh Assets", "2026-07-21", 36, None),
    ("Dynamic Vehicle Traction in Floodwater", "2026-07-21", 43, None),
    ("Small Data Physics Surrogates at 36 Conditions", "2026-07-15", 47, None),
    ("Physics Simulation Validation Protocol", "2026-07-15", 81, None),
    ("Quantitative Flood Traversability Connections", "2026-07-15", 82, None),
    ("Optical Vehicle Collision Geometry", "2026-07-15", 23, None),
]


def report_coverage() -> int:
    """What this index DOES and DOES NOT contain, as a ladder of containers.

    Exists because the containers get confused for one another. A session
    checked deep-search names against the `documents` list, found nothing, and
    concluded the deep searches were absent. `documents` holds Claude artifacts,
    Perplexity reports, Elicit extracts and bibliographies, and NEVER holds a
    deep search: those live in `source_reports`. Three of the eight it reported
    absent were in fact ingested.
    """
    idx = load()
    built = idx["built"]
    ingested = {slug for slug in idx["source_reports"]}
    print("CONTAINER COVERAGE. Five rungs, five questions. Never one number.\n")
    print(f"  index built {built}   workspace snapshot "
          f"{WORKSPACE_SNAPSHOT_DATE}\n")

    have = [w for w in WORKSPACE_DEEP_SEARCHES if w[3]]
    miss = [w for w in WORKSPACE_DEEP_SEARCHES if not w[3]]
    stale = [w for w in miss if w[1] > built]
    gap = [w for w in miss if w[1] <= built]

    print(f"  RUNG 1  deep searches      {len(have)} of "
          f"{len(WORKSPACE_DEEP_SEARCHES)} ingested")
    print(f"            never ingested   {len(gap)}  (predate the build: a real "
          "ingestion gap)")
    print(f"            newer than index {len(stale)}  (postdate the build: "
          "staleness, not a defect)")
    from collections import Counter
    kinds = Counter(d.get("type", "?") for d in idx.get("documents", []))
    print(f"  RUNG 2  documents          {idx.get('n_documents', 0)}  "
          f"{dict(kinds)}")
    print("            NOTE: holds ZERO deep searches, by construction. Do not "
          "test deep-search")
    print("            membership against this list; use source_reports.")
    print(f"  RUNG 3  papers             {idx['n_papers']} distinct")
    print("  RUNG 4  shipped bib         run --bib-audit")
    print("  RUNG 5  reference list      run --bib-audit\n")

    if gap:
        print("  NEVER INGESTED AND OLDER THAN THE INDEX, so nothing explains "
              "these away:")
        for name, created, n, _ in gap:
            print(f"    {created}  {n:>4} papers  {name}")
        print(f"    subtotal {sum(w[2] for w in gap)} relevant-paper slots\n")
    if stale:
        print("  CREATED AFTER THE INDEX WAS BUILT, so rebuild rather than "
              "blame the merge:")
        for name, created, n, _ in stale:
            print(f"    {created}  {n:>4} papers  {name}")
        print(f"    subtotal {sum(w[2] for w in stale)} relevant-paper slots\n")

    print("  THOSE SLOT COUNTS ARE NOT A PAPER COUNT. They overlap each other "
          "and the existing")
    print("  corpus by an unmeasured amount; the ingested layer merged 426 raw "
          "rows into 332")
    print("  distinct, and the builder details only each report's top 50.\n")
    print("  STRUCTURAL LIMIT, and it is the actual defect: REPORTS is a "
          "hardcoded list of")
    print("  eight local file paths. The builder has no directory scan, no glob "
          "and no API")
    print("  call, so --build CANNOT discover or reach a new deep search. "
          "Adding one means")
    print("  exporting it to markdown in the catalogue-table format and editing "
          "the REPORTS")
    print("  literal by hand. Nothing notices when a new search appears, so "
          "this gap grows")
    print("  silently every time anyone runs one.")
    return 0


def _evaluable_summary(doi: str, author_evaluable: bool) -> str:
    """Which of the five routes COULD have returned a hit for this work.

    An absence measured by a predicate that cannot fire is not a measurement.
    This column exists so that a NEVER_INGESTED verdict can be weighed by how
    many independent routes actually ran, rather than trusted because the word
    looks definite.
    """
    out = ["title-index", "title-reports"]          # always evaluable
    if doi:
        out += ["doi-index", "doi-reports"]
    if author_evaluable:
        out.append("author-index")
    return "+".join(out)


def audit_bibliography(bib_spec: str, tex_spec: str) -> dict:
    """Census every shipped bib entry against the corpus AND its source reports.

    Returns a dict with `rows` and `scope`. Every row records the route.
    """
    idx = load()
    papers = idx["papers"]
    reports = require_source_reports()

    bib_text = _git_show(bib_spec)
    tex_text = _git_show(tex_spec)

    cited = set()
    for m in re.finditer(r"\\cite[tp]?\{([^}]+)\}", tex_text):
        cited |= {k.strip() for k in m.group(1).split(",") if k.strip()}

    idx_by_doi = {r["doi"]: r for r in papers.values() if r.get("doi")}
    idx_titles = [(r["title"], k) for k, r in papers.items()]
    rep_titles = {rp["slug"]: [(r.get("title", ""), rp["slug"])
                               for r in rp["recs"].values()]
                  for rp in reports}

    rows = []
    for e in parse_bib(bib_text):
        f = e["fields"]
        key = e["key"]
        title = bib_title(f)
        doi = bib_doi(f)
        surname = bib_surname(f)
        year = f.get("year", "")
        want = _toks(title)
        routes, notes = [], []

        # ---- route 1, DOI against the index -------------------------------
        hit = idx_by_doi.get(doi) if doi else None
        routes.append("doi-exact-index:" + ("HIT" if hit else
                                            ("miss" if doi else "n/a-no-doi")))

        # ---- route 2, normalised title against all 332 index records ------
        it_score, it_title, it_key = _best_by_title(want, idx_titles)
        routes.append(f"title-jaccard-index:{it_score:.2f}")

        # ---- route 3, first-author surname against the index --------------
        # SPLIT INTO TWO, because they mean different things. A same-author
        # SAME-YEAR record may be the same document under a different title, so
        # it blocks a NEVER_INGESTED verdict. A same-author OTHER-YEAR record
        # cannot be the same document, but it is the single most informative
        # thing in this census: it proves the literature search REACHED this
        # author and did not return this work, which separates a real sourcing
        # gap from a topic the corpus was never pointed at.
        # EVALUABILITY IS RECORDED SEPARATELY FROM THE RESULT.
        # A surname of 3 characters or fewer is not searched, because substring
        # matching on a short name is overwhelmingly false-positive: "Xia"
        # returns 23 records, nearly all of them hits inside GIVEN names
        # ("Lingxiao", "Xiao-Guang", "Xiaomin"). The guard is right. What was
        # WRONG until 2026-08-19 is that the skip was silent, so the route
        # reported "0 matches" when it had not run. Zero-because-not-run and
        # zero-because-absent are different facts and must never share a cell.
        author_evaluable = bool(surname) and len(surname) > 3 and bool(year)
        if author_evaluable:
            same_auth = [r for r in papers.values()
                         if surname.lower() in r.get("authors", "").lower()]
            ay_same_year = [r for r in same_auth if r.get("year") == year]
            ay_other = sorted({r.get("year", "") for r in same_auth
                               if r.get("year") != year} - {""})
            routes.append(f"author-index:same-year={len(ay_same_year)},"
                          f"other-years={len(same_auth) - len(ay_same_year)}")
        else:
            same_auth, ay_same_year, ay_other = [], [], []
            why = ("surname too short to search" if surname and len(surname) <= 3
                   else "no surname" if not surname else "no year in bib entry")
            routes.append(f"author-index:NOT-EVALUABLE({why})")

        # ---- route 4, DOI as a raw string in each of the eight reports ----
        doi_reports = [rp["slug"] for rp in reports
                       if doi and doi in rp["ntext"]]
        routes.append("doi-in-reports:" +
                      (",".join(doi_reports) if doi_reports else
                       ("none" if doi else "n/a-no-doi")))

        # ---- route 5, title against every catalogue row in every report ---
        rt_score, rt_title, rt_slug = 0.0, "", ""
        for slug, cands in rep_titles.items():
            s, t, _ = _best_by_title(want, cands)
            if s > rt_score:
                rt_score, rt_title, rt_slug = s, t, slug
        routes.append(f"title-jaccard-reports:{rt_score:.2f}")

        # ---- verdict ------------------------------------------------------
        in_index = bool(hit) or it_score >= SAME_WORK
        in_reports = bool(doi_reports) or rt_score >= SAME_WORK

        if in_index:
            verdict = "IN_CORPUS"
            how = "doi-exact" if hit else f"title-jaccard {it_score:.2f}"
        elif in_reports:
            verdict = "DROPPED_IN_MERGE"
            how = ("doi in " + ",".join(doi_reports)) if doi_reports \
                else f"title-jaccard {rt_score:.2f} in {rt_slug}"
        elif max(it_score, rt_score) >= RELATED or ay_same_year:
            verdict = "UNCERTAIN_RELATED_WORK"
            if ay_same_year:
                how = (f"{len(ay_same_year)} corpus record(s) share this "
                       f"first-author surname AND the year {year}, so a "
                       "same-document-different-title match cannot be excluded "
                       f"(best title score {max(it_score, rt_score):.2f})")
                notes.append("CANDIDATE(S): " + " || ".join(
                    f"{r.get('title', '')[:80]} [{r.get('authors', '')[:60]}]"
                    for r in ay_same_year[:3]))
            else:
                how = (f"best candidate {max(it_score, rt_score):.2f}, below the "
                       f"{SAME_WORK} same-work threshold and above the {RELATED} "
                       "related-work threshold")
            notes.append("NOT forced to present or absent. A human must decide "
                         "whether the candidate is the same document.")
        else:
            verdict = "NEVER_INGESTED"
            how = ("searched by DOI, by normalised title against all "
                   f"{len(idx_titles)} index records and every catalogue row in "
                   "all eight reports, and by first-author surname plus year; "
                   f"best candidate {max(it_score, rt_score):.2f}")

        rows.append({
            "bib_key": key,
            "source_kind": source_kind(e),
            "cited_in_tex": "yes" if key in cited else "no",
            "year": year,
            "first_author": surname,
            "doi": doi or "(none in bib)",
            "doi_field_used": ("doi" if _DOI_ANY.search(f.get("doi", ""))
                               else "note" if _DOI_ANY.search(f.get("note", ""))
                               else "url" if _DOI_ANY.search(f.get("url", ""))
                               else "(no doi anywhere)"),
            "verdict": verdict,
            "matched_how": how,
            "best_index_score": f"{it_score:.2f}",
            "best_index_candidate": it_title[:110],
            "reports_with_doi": ",".join(doi_reports) or "-",
            "best_report_score": f"{rt_score:.2f}",
            "best_report_candidate": rt_title[:110],
            "best_report_slug": rt_slug or "-",
            "same_author_other_years": ",".join(ay_other) or "-",
            "routes_evaluable": _evaluable_summary(doi, author_evaluable),
            "n_routes_evaluable": str(2 + int(bool(doi)) * 2
                                      + int(author_evaluable)),
            "routes": " | ".join(routes),
            "notes": " ".join(notes) or "-",
            "title": title,
        })

    return {
        "rows": rows,
        "scope": {
            "bib_ref": bib_spec,
            "tex_ref": tex_spec,
            "index_built": idx["built"],
            "n_index_papers": idx["n_papers"],
            "n_index_no_doi": idx["n_no_doi_undiffable"],
            "n_reports_read": len(reports),
            "same_work_threshold": SAME_WORK,
            "related_threshold": RELATED,
            "worktrees_excluded": True,
        },
    }


TSV_COLUMNS = ["bib_key", "source_kind", "cited_in_tex", "year", "first_author",
               "doi", "doi_field_used", "verdict", "matched_how",
               "best_index_score", "best_index_candidate", "reports_with_doi",
               "best_report_score", "best_report_candidate",
               "best_report_slug", "same_author_other_years",
               "routes_evaluable", "n_routes_evaluable", "routes",
               "notes", "title"]


def write_census_tsv(res: dict, path: str) -> None:
    sc = res["scope"]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"# bibliography-to-corpus census, written by "
                 f"analysis/research_index.py --bib-audit\n")
        fh.write(f"# SCOPE, stated with the numbers because it decides them: "
                 f"bib_ref={sc['bib_ref']} tex_ref={sc['tex_ref']} "
                 f"index_built={sc['index_built']} "
                 f"index_papers={sc['n_index_papers']} "
                 f"reports_read={sc['n_reports_read']}/8 "
                 f"same_work_threshold={sc['same_work_threshold']} "
                 f"related_threshold={sc['related_threshold']} "
                 f".claude/worktrees excluded=yes\n")
        fh.write("\t".join(TSV_COLUMNS) + "\n")
        for r in res["rows"]:
            fh.write("\t".join(str(r[c]).replace("\t", " ")
                               for c in TSV_COLUMNS) + "\n")


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
    ap.add_argument("--bib-audit", action="store_true",
                    help="census the SHIPPED bibliography against this corpus "
                         "and against the eight source reports, recording the "
                         "route by which each work matched or failed to match")
    ap.add_argument("--bib-ref", default=BIB_REF_DEFAULT,
                    help=f"rev:path of the bibliography (default "
                         f"{BIB_REF_DEFAULT}). Name it explicitly: the entry "
                         "count differs between origin/main, "
                         "claude/add-ci-checks and overleaf/main.")
    ap.add_argument("--tex-ref", default=TEX_REF_DEFAULT,
                    help=f"rev:path of the paper source (default "
                         f"{TEX_REF_DEFAULT})")
    ap.add_argument("--tsv", help="also write the census as TSV to this path")
    ap.add_argument("--coverage", action="store_true",
                    help="what this index does and does not contain, as a "
                         "ladder of containers")
    a = ap.parse_args()

    if a.coverage:
        return report_coverage()

    if a.bib_audit:
        res = audit_bibliography(a.bib_ref, a.tex_ref)
        sc, rows = res["scope"], res["rows"]
        print("BIBLIOGRAPHY-TO-CORPUS CENSUS")
        print(f"  bib ref            {sc['bib_ref']}")
        print(f"  tex ref            {sc['tex_ref']}")
        print(f"  index built        {sc['index_built']}  "
              f"({sc['n_index_papers']} papers, {sc['n_index_no_doi']} with no "
              "DOI and therefore unmatchable by the DOI route)")
        print(f"  source reports     {sc['n_reports_read']}/8 read at audit "
              "time, all non-empty, all parsing to >0 records")
        print(f"  thresholds         same-work {sc['same_work_threshold']}, "
              f"related {sc['related_threshold']} (title token Jaccard)")
        print("  scope              .claude/worktrees/ excluded")
        print()
        cited = [r for r in rows if r["cited_in_tex"] == "yes"]
        print(f"  {len(rows)} bib entries, {len(cited)} of them \\cite'd\n")
        for v in ("IN_CORPUS", "DROPPED_IN_MERGE", "UNCERTAIN_RELATED_WORK",
                  "NEVER_INGESTED"):
            grp = [r for r in rows if r["verdict"] == v]
            gc = [r for r in grp if r["cited_in_tex"] == "yes"]
            print(f"  {v:24} {len(grp):2d} entries, {len(gc):2d} cited")
        print()
        for v in ("IN_CORPUS", "DROPPED_IN_MERGE", "UNCERTAIN_RELATED_WORK",
                  "NEVER_INGESTED"):
            grp = [r for r in rows if r["verdict"] == v]
            if not grp:
                continue
            print(f"--- {v} ---")
            for r in grp:
                print(f"  {r['bib_key']:22} [{r['source_kind']:22}] "
                      f"cited={r['cited_in_tex']}")
                print(f"      {r['title'][:100]}")
                print(f"      doi {r['doi']}  (from `{r['doi_field_used']}` "
                      "field)")
                print(f"      {r['matched_how']}")
                if r["best_index_score"] != "0.00":
                    print(f"      nearest in corpus  {r['best_index_score']}  "
                          f"{r['best_index_candidate']}")
                if v != "IN_CORPUS" and r["same_author_other_years"] != "-":
                    print(f"      SURNAME {r['first_author']!r} also appears "
                          f"in corpus records for year(s) "
                          f"{r['same_author_other_years']}. Surname substring "
                          "only, NOT an author-identity claim, but it means "
                          "the searches reached that name and returned other "
                          "work, not this one")
                if r["notes"] != "-":
                    print(f"      NOTE {r['notes']}")
            print()
        print("--- WAS EACH ABSENCE MEASURED BY A PREDICATE THAT COULD FIRE? ---")
        print("  An absence found by a search that cannot match is not a")
        print("  measurement. Five routes exist; not all are evaluable for every")
        print("  work. A DOI-less bib entry loses both DOI routes; a surname of")
        print("  3 characters or fewer is not searched because substring")
        print("  matching on a short name is overwhelmingly false-positive.")
        absent = [r for r in rows if r["verdict"] == "NEVER_INGESTED"]
        for r in sorted(absent, key=lambda r: int(r["n_routes_evaluable"])):
            flag = "  <-- WEAK" if int(r["n_routes_evaluable"]) <= 2 else ""
            print(f"    {r['bib_key']:22} {r['n_routes_evaluable']} of 5   "
                  f"{r['routes_evaluable']}{flag}")
        weak = [r for r in absent if int(r["n_routes_evaluable"]) <= 2]
        print(f"  absences resting on 2 routes or fewer: "
              f"{len(weak)}{' (' + ', '.join(r['bib_key'] for r in weak) + ')' if weak else ''}")
        print()
        defects = index_self_defects()
        print("--- INDEX SELF-CHECK ---")
        if not defects:
            print("  no records with a recoverable DOI hidden in the title")
        else:
            print(f"  {len(defects)} record(s) carry an EMPTY doi while a DOI is "
                  "still recoverable from the mangled title. Cited-status is "
                  "gated on bool(doi), so these can never be marked cited "
                  "however often the repo cites them.")
            for d in defects:
                print(f"    {d['key']:22} {d['recovered_doi']}")
                print(f"      {d['title'][:96]}   [{d['reports']}]")
        print()
        if a.tsv:
            write_census_tsv(res, a.tsv)
            print(f"wrote {a.tsv}")
        return 0

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
        # SEARCHES AUTHORS TOO, AND THAT IS A FIX, NOT A FLOURISH.
        # This clause read `title or abstract` until 2026-08-19. An author-name
        # query therefore returned a STRUCTURALLY FALSE ZERO: the field being
        # queried was never read, and 0 matches is indistinguishable from "not
        # in the corpus". Measured that day: `--query "Al-Qadami"` returned 0
        # while 5 records carry Al-Qadami in `authors`, among them
        # 10.1111/jfr3.12828, the project's closest prior art. A coordinating
        # session used that zero as evidence the corpus was silent on it.
        # This is the tool whose whole purpose is to stop absence claims, so a
        # false zero here is worse than no tool.
        q = a.query.lower()
        pool = list(sel)
        sel = [r for r in sel
               if q in r["title"].lower() or q in r["abstract"].lower()
               or q in r.get("authors", "").lower()]
        # STATE THE SEARCH DEPTH WITH THE RESULT.
        # This is a LITERAL SUBSTRING match. It does not stem, does not handle a
        # paraphrase, and for any record without an abstract it is title-only.
        # 110 of the 332 have no abstract, so for a third of the corpus a topic
        # query can only match words that appear in the title. A zero here is
        # weak evidence of absence and the tool should say so rather than let
        # the reader infer certainty from an empty list.
        _no_abs = sum(1 for r in pool if not r.get("abstract"))
        sys.stderr.write(
            f"[--query is a literal substring match over title+abstract+authors. "
            f"{_no_abs} of {len(pool)} searched records have NO abstract and were "
            f"matched on title and authors only. A paraphrase will miss. Do not "
            f"read 0 matches as absence without a second route.]\n")
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
