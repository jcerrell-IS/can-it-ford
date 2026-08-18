#!/usr/bin/env python3
"""corpus MCP server for can-it-ford.

WHY THIS EXISTS, precisely. On 2026-08-14 five separate dispatch sessions
(D1, D2, D7, D9, D11) each independently reported research artifacts as
unreadable, because each checked ~/Downloads only, where macOS TCC denies
access. Every one of those artifacts existed in full at /Users/josie/Claude/reu.
That is a five-instance false-negative class caused purely by lookup method.

It also answers the question that cost the most credibility that night: four
vehicle-fording papers sat in our own Undermind catalogs, uncited, while the
project prepared to claim novelty. cited_status() makes that a single call.

Zero dependencies. Python 3.9 safe.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_scaffold import Server  # noqa: E402

REPO = os.environ.get("CANFORD_REPO") or "/Users/josie/can-it-ford"
# ^ env override added 2026-08-18 so the server works from a plugin cache copy
#   and from a fresh clone. Absent the env var, behaviour is byte-identical.

# Ordered by reliability. ~/Downloads is LAST and flagged, because it is the
# one root that intermittently returns "Operation not permitted".
ROOTS = [
    "/Users/josie/Claude/reu",
    "/Users/josie/Documents/Claude/reu",
    "/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13",
    "/Users/josie/Documents/Claude",
    "/Users/josie/Documents/CAN_IT_FORD_ARCHIVE_2026-07-17",
    "/Users/josie/Downloads",
]

ID8 = re.compile(r"\b([0-9a-f]{8})\b")
DOI = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")

srv = Server("canford-corpus")


def _walk(root, maxdepth=6):
    if not os.path.isdir(root):
        return
    base = root.rstrip("/").count("/")
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath.count("/") - base >= maxdepth:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in
                       (".git", "__pycache__", "node_modules", ".venv")]
        for fn in filenames:
            if fn.endswith(".md") or fn.endswith(".tsv"):
                yield os.path.join(dirpath, fn)


def _readable(p):
    try:
        with open(p, "rb") as fh:
            fh.read(1)
        return True
    except OSError:
        return False


def _title(p):
    try:
        with open(p, "r", errors="replace") as fh:
            for _ in range(80):
                ln = fh.readline()
                if not ln:
                    break
                if ln.startswith("# "):
                    return ln[2:].strip()
    except OSError:
        return ""
    return ""


@srv.tool(
    "corpus_resolve",
    "Resolve an 8-hex artifact id to EVERY readable path on disk. Use this "
    "before ever reporting a research artifact as missing or unreadable: an "
    "absence from ~/Downloads is not an absence.",
    {"type": "object",
     "properties": {"id8": {"type": "string",
                            "description": "8-hex artifact id, e.g. 65474f37"}},
     "required": ["id8"]},
)
def corpus_resolve(id8):
    id8 = id8.strip().lower()
    hits = []
    for root in ROOTS:
        for p in _walk(root):
            if id8 in os.path.basename(p).lower():
                hits.append({"path": p,
                             "readable": _readable(p),
                             "bytes": os.path.getsize(p) if _readable(p) else None,
                             "title": _title(p) if _readable(p) else None,
                             "tcc_risk": p.startswith("/Users/josie/Downloads")})
    if not hits:
        return {"id8": id8, "found": 0,
                "verdict": "NOT FOUND in any of %d roots" % len(ROOTS),
                "roots_searched": ROOTS}
    readable = [h for h in hits if h["readable"]]
    return {"id8": id8, "found": len(hits), "readable": len(readable),
            "verdict": "READABLE" if readable else "PRESENT BUT UNREADABLE",
            "use_this_path": readable[0]["path"] if readable else None,
            "hits": hits}


@srv.tool(
    "corpus_search",
    "Search every research artifact title and body for a query string. "
    "Returns file, title and matching line numbers. Searches all roots, not "
    "just the one you happened to think of.",
    {"type": "object",
     "properties": {
         "query": {"type": "string"},
         "max_files": {"type": "integer", "default": 25},
         "titles_only": {"type": "boolean", "default": False}},
     "required": ["query"]},
)
def corpus_search(query, max_files=25, titles_only=False):
    q = query.lower()
    out = []
    seen_names = set()
    for root in ROOTS:
        for p in _walk(root):
            name = os.path.basename(p)
            if name in seen_names:
                continue
            if not _readable(p):
                continue
            t = _title(p)
            if titles_only:
                if q in t.lower():
                    seen_names.add(name)
                    out.append({"path": p, "title": t})
                continue
            try:
                with open(p, "r", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError:
                continue
            hits = [i + 1 for i, ln in enumerate(lines) if q in ln.lower()]
            if hits:
                seen_names.add(name)
                out.append({"path": p, "title": t, "n_hits": len(hits),
                            "first_lines": hits[:8]})
            if len(out) >= max_files:
                return {"query": query, "files": out, "truncated": True}
    return {"query": query, "files": out, "truncated": False}


@srv.tool(
    "corpus_read",
    "Read a slice of an artifact by line range, so a 3.4 MB manifest or a "
    "600-line report never has to be read whole. On 2026-08-14 a session "
    "reported the 6,241-row research manifest as unreadable when the real "
    "problem was a whole-file size limit.",
    {"type": "object",
     "properties": {"path": {"type": "string"},
                    "start": {"type": "integer", "default": 1},
                    "count": {"type": "integer", "default": 120}},
     "required": ["path"]},
)
def corpus_read(path, start=1, count=120):
    if not _readable(path):
        return {"path": path, "error": "not readable (TCC denial or missing)"}
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    sl = lines[max(0, start - 1): max(0, start - 1) + count]
    return {"path": path, "total_lines": len(lines),
            "range": [start, start + len(sl) - 1],
            "text": "".join(sl)}


@srv.tool(
    "corpus_headings",
    "List the markdown headings of an artifact so you can pick a section "
    "instead of reading the whole file.",
    {"type": "object", "properties": {"path": {"type": "string"}},
     "required": ["path"]},
)
def corpus_headings(path):
    if not _readable(path):
        return {"path": path, "error": "not readable"}
    out = []
    with open(path, "r", errors="replace") as fh:
        for i, ln in enumerate(fh, 1):
            if ln.startswith("#"):
                out.append({"line": i, "heading": ln.rstrip()})
    return {"path": path, "headings": out}


# --- citation resolution -------------------------------------------------
# A DOI appearing in a file is NOT a citation. corpus_cited_status returned
# "cited" for exactly that until 2026-08-18, which made the novelty guard a
# check that could not fail: the act of writing "these four papers are uncited"
# into docs/ put their DOIs in docs/, which flipped them to "cited".
# The only thing that means cited is a key inside a \cite command in the
# submitted LaTeX. Everything else is availability or prose.

CITE_RE = re.compile(r"\\([a-zA-Z]*cite[a-zA-Z]*)\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")
BIBKEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
COMMENT_RE = re.compile(r"(?<!\\)%.*$")


def _strip_tex_comments(text):
    """Drop LaTeX comments so a commented-out \\cite is not counted."""
    return "\n".join(COMMENT_RE.sub("", ln) for ln in text.splitlines())


def _paper_cite_keys():
    """Keys actually inside a \\cite command in the submitted LaTeX.

    Returns (keys, tex_files, error). `error` is non-None when paper/ could not
    be read at all, so an unreadable tree is a DISTINCT state rather than a
    silent "not cited". Absence of evidence from a partial view is not evidence
    of absence, and this function is the one place that rule can be violated
    invisibly.

    \\nocite is EXCLUDED on purpose. \\nocite{*} pulls the whole .bib into the
    bibliography without citing anything, so counting it would restore the very
    always-true behaviour this function exists to remove.
    """
    pdir = os.path.join(REPO, "paper")
    keys, files = set(), []
    if not os.path.isdir(pdir):
        return keys, files, "no such directory: %s" % pdir
    try:
        names = sorted(os.listdir(pdir))
    except OSError as e:
        return keys, files, "cannot list %s: %s" % (pdir, e)
    tex = [os.path.join(pdir, n) for n in names if n.endswith(".tex")]
    if not tex:
        return keys, files, "no .tex file under %s" % pdir
    unread = []
    for p in tex:
        try:
            with open(p, "r", errors="replace") as fh:
                body = _strip_tex_comments(fh.read())
        except OSError as e:
            unread.append("%s (%s)" % (p, e))
            continue
        files.append(p)
        for cmd, group in CITE_RE.findall(body):
            if cmd == "nocite":
                continue
            for k in group.split(","):
                if k.strip():
                    keys.add(k.strip())
    if not files:
        return keys, files, "no .tex file was readable: %s" % "; ".join(unread)
    return keys, files, ("partially unreadable: %s" % "; ".join(unread)) if unread else None


def _bib_entries():
    """bib key -> raw entry text, for every .bib under paper/."""
    pdir = os.path.join(REPO, "paper")
    entries = {}
    if not os.path.isdir(pdir):
        return entries
    for n in sorted(os.listdir(pdir)):
        if not n.endswith(".bib"):
            continue
        try:
            with open(os.path.join(pdir, n), "r", errors="replace") as fh:
                body = fh.read()
        except OSError:
            continue
        marks = [(m.start(), m.group(1).strip()) for m in BIBKEY_RE.finditer(body)]
        for i, (pos, key) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
            entries[key] = body[pos:end]
    return entries


@srv.tool(
    "corpus_cited_status",
    "Is this DOI or citation key CITED IN THE PAPER, merely sitting in the "
    ".bib, or only mentioned in notes? THIS IS THE NOVELTY GUARD. On "
    "2026-08-14 four vehicle-fording papers (Wasfy 2015 DETC2015-47142, "
    "Pazouki 2016, Khapane 2014 SAE 2014-01-0936, He 2026 10.1115/1.4071177) "
    "sat in our own catalogs uncited while the project prepared to claim "
    "nobody had simulated fording. All four have .bib entries and NONE is "
    "\\cite'd, so a tool that cannot tell those apart cannot answer the "
    "question it exists for.",
    {"type": "object",
     "properties": {"needle": {"type": "string",
                               "description": "DOI, SAE number, author-year, or bib key"}},
     "required": ["needle"]},
)
def corpus_cited_status(needle):
    cite_keys, tex_files, paper_err = _paper_cite_keys()
    entries = _bib_entries()

    nl = needle.lower()
    bib_keys = sorted(k for k, v in entries.items() if nl in v.lower())
    if needle in entries and needle not in bib_keys:
        bib_keys.append(needle)
    matched = sorted(set(bib_keys) & cite_keys)
    if needle in cite_keys and needle not in matched:
        matched.append(needle)

    # Prose mentions. NOT evidence of citation, reported only so a "not cited"
    # answer says where the thing does appear.
    # /usr/bin/grep, never the shell function: the shell grep is a ugrep
    # wrapper with --ignore-files and silently skips gitignored paths.
    cmd = ["/usr/bin/grep", "-rIl", "--", needle,
           os.path.join(REPO, "docs"), os.path.join(REPO, "CLAUDE.md")]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        notes = [x for x in r.stdout.splitlines() if x.strip()]
    except Exception as e:
        notes = ["<grep failed: %s>" % e]

    corpus = corpus_search(needle, max_files=10)

    if paper_err and not tex_files:
        verdict = ("CANNOT ANSWER: the paper could not be read (%s). "
                   "This is not a 'not cited' result." % paper_err)
    elif matched:
        verdict = "CITED IN THE PAPER as %s" % ", ".join(matched)
    elif bib_keys:
        verdict = ("IN THE BIBLIOGRAPHY BUT NEVER \\cite'd (%s). This is the "
                   "novelty-gate failure case: it will render in no reference "
                   "list and a reviewer will not see it." % ", ".join(bib_keys))
    elif notes or corpus["files"]:
        verdict = ("MENTIONED IN NOTES OR PRESENT IN CORPUS, NOT CITED AND NOT "
                   "IN THE BIBLIOGRAPHY, investigate")
    else:
        verdict = "not found either place"

    return {"needle": needle,
            "cited_in_paper": bool(matched),
            "cite_keys_matched": matched,
            "in_bibliography": bool(bib_keys),
            "bib_keys": bib_keys,
            "mentioned_in_notes": bool(notes),
            "note_files": notes,
            "present_in_corpus": len(corpus["files"]) > 0,
            "corpus_files": [f["path"] for f in corpus["files"]],
            "tex_files_read": tex_files,
            "paper_read_error": paper_err,
            "verdict": verdict}


@srv.tool(
    "corpus_inventory",
    "Count artifacts per root and report which roots are currently readable. "
    "Run this first in any session that will touch research, so a TCC denial "
    "is visible as a denial rather than as an absence.",
    {"type": "object", "properties": {}},
)
def corpus_inventory():
    out = []
    for root in ROOTS:
        exists = os.path.isdir(root)
        n = 0
        readable = 0
        if exists:
            for p in _walk(root, maxdepth=6):
                n += 1
                if _readable(p):
                    readable += 1
        out.append({"root": root, "exists": exists, "files": n,
                    "readable": readable,
                    "STATUS": ("OK" if exists and readable == n else
                               "PARTIAL/TCC-DENIED" if exists else "ABSENT")})
    return {"roots": out,
            "rule": "A zero or partial count is a BROKEN PROBE, not evidence "
                    "that an artifact does not exist."}


if __name__ == "__main__":
    srv.run()
