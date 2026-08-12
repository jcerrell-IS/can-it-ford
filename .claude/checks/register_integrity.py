#!/usr/bin/env python3
"""
Integrity checker for docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md.

Why this exists. The register is the sole corrections authority, and it has already
suffered three defects of its own that no tool would have caught:

  1. A duplicate item number. A second item was written as E7 and collided with the
     existing E7; it was renumbered to E8 on 2026-08-08. The register is cited BY
     ITEM NUMBER, so a duplicate number is a citation defect, not a cosmetic one.
     Recorded in the register at E8.

  2. A dangling cross-reference. Item 15 of CLAUDE.md was withdrawn with a note
     pointing readers to "register A2" for two post-processing constants, and A2 did
     not contain them. Register item A6 exists only to close that dangling pointer.

  3. A citation to a file that no script writes. failure_modes_result.json was cited
     as independent confirmation from two documents; the JSON provenance field named
     scratchpad/classify_17_runs.py, a path that does not exist in the repo.
     Recorded at D6a and D6h.

All three are machine-checkable. This script checks them, plus every git SHA the
register cites, because a fabricated SHA reads exactly like a real one.

Usage:
    python3 .claude/checks/register_integrity.py
    python3 .claude/checks/register_integrity.py --register <path>
    python3 .claude/checks/register_integrity.py --quiet

Exit codes:
    0  no blocking defects
    1  at least one blocking defect
    2  the register itself could not be read

Blocking defects are duplicate item ids and cross-references to undefined items.
Unresolved file paths and unresolved SHAs are reported as WARNING, not blocking,
because the register legitimately cites paths inside the vendored solver tree and
on remote TACC filesystems that are not present on every machine.
"""

import argparse
import glob
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# The register cites four different kinds of hex token and they are not
# interchangeable. Conflating them is exactly the sort of error this file exists
# to catch, so each is resolved against its own real source:
#   git object          resolves via git cat-file in this clone
#   upstream pinned SHA lives in third_party/*/PINNED_SHA.txt, kks32/mpm-engine,
#                       and will never resolve in this clone
#   research artifact   an 8-hex id naming a file at
#                       ~/Downloads/compass_artifact_wf-<id>-*_text_markdown.md,
#                       recorded at register K0
#   unresolved          none of the above, and therefore worth a human check
RESEARCH_ARTIFACT_GLOB = os.path.expanduser(
    "~/Downloads/compass_artifact_wf-%s-*_text_markdown.md"
)
PINNED_SHA_GLOB = os.path.join(REPO_ROOT, "third_party", "*", "PINNED_SHA.txt")
DEFAULT_REGISTER = os.path.join(
    REPO_ROOT, "docs", "CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md"
)

# Where a backticked path may legitimately live besides the repo root. The register
# cites solver internals by their path inside the vendored engine, not by the
# third_party/ prefix, so a bare "kernels/mpm_solver_warp.py" is correct and must
# not be reported as missing.
PATH_SEARCH_ROOTS = [
    REPO_ROOT,
    os.path.join(REPO_ROOT, "third_party", "mpm-engine-544c93dd-solver-core"),
    os.path.join(REPO_ROOT, "renders", "yaris_render_s1"),
    os.path.join(REPO_ROOT, "simulation"),
    os.path.join(REPO_ROOT, "analysis"),
]

SECTION_RE = re.compile(r"^##\s+SECTION\s+([A-Z])\b", re.MULTILINE)
# An item header looks like: **A1. text** or **D6c. text**
ITEM_HEADER_RE = re.compile(r"^\*\*([A-Z])(\d{1,2})([a-z]?)\.", re.MULTILINE)
# Section J is a numbered list, not bold headers, so its ids are J1..Jn by position.
NUMBERED_ITEM_RE = re.compile(r"^(\d{1,2})\.\s+\S", re.MULTILINE)

# Cross-references are only counted when they carry an explicit cue word. A bare
# token like "C1" is ambiguous in this project: it is simultaneously a register
# item in section C and the name of a coupling-validation case. Cue-based matching
# keeps the check precise instead of noisy.
REF_CUE_RE = re.compile(
    r"(?:register|see|per|section|item|superseded by|covered by|closed[^.\n]{0,24}?|refuted,|recorded (?:at|in)|consistent with)\s+"
    r"(?:register\s+)?((?:[A-K]\d{1,2}[a-z]?)(?:\s*(?:,|and|to|-|through)\s*[A-K]?\d{1,2}[a-z]?)*)",
    re.IGNORECASE,
)
REF_TOKEN_RE = re.compile(r"\b([A-K]\d{1,2}[a-z]?)\b")

# A backticked token is treated as a path only if it looks like one.
PATH_RE = re.compile(r"`([^`\n]+)`")
PATH_LOOKS_LIKE = re.compile(r"^[\w./_-]+/[\w./_-]+\.(py|md|csv|json|ply|tex|txt|sh|yml|yaml|sbatch)$")

SHA_RE = re.compile(r"`([0-9a-f]{7,40})`")

# Section letters whose items are bold headers. Section J is numbered.
NUMBERED_SECTIONS = {"J"}


class Finding:
    def __init__(self, level, code, message):
        self.level = level
        self.code = code
        self.message = message

    def __str__(self):
        return "%-7s [%s] %s" % (self.level, self.code, self.message)


def read_register(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        sys.stderr.write("register_integrity.py: cannot read %s: %s\n" % (path, exc))
        sys.exit(2)


def split_sections(text):
    """Return [(letter, body_text, start_line), ...] in document order."""
    marks = [(m.group(1), m.start()) for m in SECTION_RE.finditer(text)]
    out = []
    for idx, (letter, start) in enumerate(marks):
        end = marks[idx + 1][1] if idx + 1 < len(marks) else len(text)
        line_no = text.count("\n", 0, start) + 1
        out.append((letter, text[start:end], line_no))
    return out


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def collect_defined_items(text, sections):
    """Return (defined_set, duplicates_list). duplicates are (item_id, [lines])."""
    seen = {}
    for m in ITEM_HEADER_RE.finditer(text):
        item_id = "%s%s%s" % (m.group(1), m.group(2), m.group(3))
        seen.setdefault(item_id, []).append(line_of(text, m.start()))

    # Numbered sections contribute <letter><n>.
    for letter, body, sect_line in sections:
        if letter not in NUMBERED_SECTIONS:
            continue
        for m in NUMBERED_ITEM_RE.finditer(body):
            item_id = "%s%s" % (letter, m.group(1))
            seen.setdefault(item_id, []).append(sect_line + body.count("\n", 0, m.start()))

    duplicates = [(k, v) for k, v in sorted(seen.items()) if len(v) > 1]
    return set(seen), duplicates


def normalize_item_id(tok):
    """A1 / d6a / D6A all name the same item. Section letter upper, suffix lower."""
    m = re.match(r"^([A-Za-z])(\d{1,2})([A-Za-z]?)$", tok)
    if not m:
        return tok
    return "%s%s%s" % (m.group(1).upper(), m.group(2), m.group(3).lower())


def collect_references(text):
    """Return {item_id: [line numbers]} for cue-anchored cross-references."""
    refs = {}
    for m in REF_CUE_RE.finditer(text):
        span = m.group(1)
        line = line_of(text, m.start())
        for tok in REF_TOKEN_RE.findall(span):
            refs.setdefault(normalize_item_id(tok), []).append(line)
    return refs


def resolve_path(candidate):
    for root in PATH_SEARCH_ROOTS:
        if os.path.exists(os.path.join(root, candidate)):
            return True
    return os.path.exists(candidate)


def collect_paths(text):
    out = {}
    for m in PATH_RE.finditer(text):
        raw = m.group(1).strip()
        if not PATH_LOOKS_LIKE.match(raw):
            continue
        out.setdefault(raw, []).append(line_of(text, m.start()))
    return out


def load_pinned_shas():
    """Upstream solver SHAs. These name kks32/mpm-engine commits and will never
    resolve in this clone, so resolving them here prevents a false alarm.

    Two real sources, both read live rather than hardcoded, so this list cannot go
    stale the way a maintained allowlist would:
      third_party/*/PINNED_SHA.txt     the pin itself
      */geom_live.py "repo_head"       the engine head a run was captured against
    """
    out = set()
    for path in glob.glob(PINNED_SHA_GLOB):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    tok = line.strip()
                    if re.fullmatch(r"[0-9a-f]{7,40}", tok):
                        out.add(tok)
        except OSError:
            continue
    for path in glob.glob(os.path.join(REPO_ROOT, "**", "geom_live.py"), recursive=True):
        if "/.claude/worktrees/" in path or "/can-it-ford/can-it-ford/" in path:
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for m in re.finditer(r'"repo_head"\s*:\s*"([0-9a-f]{7,40})"', fh.read()):
                    out.add(m.group(1))
        except OSError:
            continue
    return out


def git_object_exists(sha):
    try:
        res = subprocess.run(
            ["git", "-C", REPO_ROOT, "cat-file", "-e", sha + "^{object}"],
            capture_output=True,
            text=True,
        )
        return res.returncode == 0
    except Exception:
        return None


def classify_hex_token(sha, pinned):
    """Return one of: git, pinned, artifact, unresolved."""
    for p in pinned:
        if p.startswith(sha) or sha.startswith(p):
            return "pinned"
    if len(sha) == 8 and glob.glob(RESEARCH_ARTIFACT_GLOB % sha):
        return "artifact"
    if git_object_exists(sha):
        return "git"
    return "unresolved"


def collect_shas(text):
    out = {}
    for m in SHA_RE.finditer(text):
        sha = m.group(1)
        # A bare run of hex that is really a number, a DOI fragment, or a hash of
        # something else would be a false positive. Require at least one letter so
        # a pure-digit token like `1015` is not treated as a SHA.
        if not re.search(r"[a-f]", sha):
            continue
        if len(sha) < 7:
            continue
        out.setdefault(sha, []).append(line_of(text, m.start()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--register", default=DEFAULT_REGISTER)
    ap.add_argument("--quiet", action="store_true", help="print only findings, no summary counts")
    ap.add_argument("--no-git", action="store_true", help="skip git SHA resolution")
    args = ap.parse_args()

    text = read_register(args.register)
    sections = split_sections(text)
    defined, duplicates = collect_defined_items(text, sections)
    refs = collect_references(text)
    paths = collect_paths(text)
    shas = {} if args.no_git else collect_shas(text)

    findings = []

    for item_id, lines in duplicates:
        findings.append(
            Finding(
                "BLOCK",
                "dup-item",
                "item id %s is defined %d times, at lines %s. The register is cited by "
                "item number, so a duplicate number is a citation defect. Renumber one, "
                "the way the second E7 became E8."
                % (item_id, len(lines), ", ".join(str(x) for x in lines)),
            )
        )

    for item_id in sorted(refs):
        if item_id in defined:
            continue
        lines = sorted(set(refs[item_id]))
        findings.append(
            Finding(
                "BLOCK",
                "dangling-ref",
                "cross-reference to %s at line(s) %s, but no item %s is defined. This is "
                "the A6 defect class: a withdrawal note pointed at register A2 for two "
                "constants A2 did not contain."
                % (item_id, ", ".join(str(x) for x in lines), item_id),
            )
        )

    missing_paths = []
    for candidate in sorted(paths):
        if not resolve_path(candidate):
            missing_paths.append((candidate, sorted(set(paths[candidate]))))
    for candidate, lines in missing_paths:
        findings.append(
            Finding(
                "WARN",
                "unresolved-path",
                "cited path %s at line(s) %s does not resolve under the repo root, the "
                "vendored solver tree, or the run directories. It may be a remote TACC "
                "path or a gitignored artifact. Confirm before citing it as evidence."
                % (candidate, ", ".join(str(x) for x in lines)),
            )
        )

    pinned = load_pinned_shas()
    kinds = {"git": 0, "pinned": 0, "artifact": 0, "unresolved": 0}
    unresolved_shas = []
    for sha in sorted(shas):
        kind = classify_hex_token(sha, pinned)
        kinds[kind] += 1
        if kind == "unresolved":
            unresolved_shas.append((sha, sorted(set(shas[sha]))))
    for sha, lines in unresolved_shas:
        findings.append(
            Finding(
                "WARN",
                "unresolved-hex",
                "cited hex token %s at line(s) %s resolves as none of: a git object in this "
                "clone, an upstream pinned solver SHA in third_party/*/PINNED_SHA.txt, or a "
                "research artifact at ~/Downloads/compass_artifact_wf-%s-*. It may live on an "
                "unfetched remote, or it may be fabricated. A fabricated SHA reads exactly "
                "like a real one, so resolve it before citing it as evidence."
                % (sha, ", ".join(str(x) for x in lines), sha),
            )
        )

    blocking = [f for f in findings if f.level == "BLOCK"]

    for f in findings:
        print(f)

    if not args.quiet:
        print("")
        print("register_integrity.py summary")
        print("  register          %s" % os.path.relpath(args.register, REPO_ROOT))
        print("  sections          %d (%s)" % (len(sections), ", ".join(s[0] for s in sections)))
        print("  items defined     %d" % len(defined))
        print("  cross-references  %d distinct, cue-anchored" % len(refs))
        print("  paths checked     %d backticked, %d unresolved" % (len(paths), len(missing_paths)))
        if args.no_git:
            print("  hex tokens        skipped (--no-git)")
        else:
            print(
                "  hex tokens        %d cited: %d git, %d upstream-pinned, %d research-artifact, %d unresolved"
                % (len(shas), kinds["git"], kinds["pinned"], kinds["artifact"], kinds["unresolved"])
            )
        print("  blocking defects  %d" % len(blocking))

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
