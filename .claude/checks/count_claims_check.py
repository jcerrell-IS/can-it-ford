#!/usr/bin/env python3
"""
Guard against asserting a declaration-site COUNT that nobody re-derived.

Why this exists. The drift-tolerance count has been "settled" wrong twice, and the
second time the CORRECTION was the thing that was wrong:

  1. "16 places under four names" -> a floor, produced by a grep that skipped
     renders/ because the shell `grep` wraps ugrep with --ignore-files (register H0).
     Refuted outright. This is the only total that is simply wrong.
  2. "24 places under five names, THRESHOLD 2" -> register D7, 2026-08-11.
     D7's 24 is CORRECT. It reproduces exactly under (count the default-valued
     binding, include archive/). See CLAUDE.md item 13, RETRACTION 2026-08-12.
  3. A same-day recount declared D7's THRESHOLD 2 "cannot be reproduced" and
     propagated a bare 22 into three files. That recount was itself wrong: its
     strict `NAME = 0.05` regex could not see analysis/gp_surrogate.py:14, where
     THRESHOLD takes 0.05 as a CLI-overridable default. D7's second THRESHOLD was
     always there; the refutation was an assertion nobody re-derived either.

Every one of those was an assertion nobody re-derived before trusting, including the
refutation. That is the failure shape, not the number. So this check re-derives the
number live and refuses an assertion that matches no defensible live reading.

THREE THINGS IT MUST GET RIGHT, all learned the hard way in this repo:

  A. THE COUNT IS SCOPE-SENSITIVE. Excluding archive/ the bare-literal total is 22;
     including it, 23. Counting analysis/gp_surrogate.py:14, where THRESHOLD is bound
     to 0.05 as a CLI-overridable default rather than a bare literal, adds one more.
     Two independent binary choices give four totals, {22, 23, 24}. Each is correct
     for its scope. A checker that hardcodes one number just relocates the bug, so
     this compares against the SET of defensible live readings.

  B. QUOTING A NUMBER IN ORDER TO RETIRE IT IS CORRECT, AND MUST NOT BLOCK. This is
     the same false-positive class that makes check_claims C5 and C8 fire on their
     own refutations. A line carrying a refutation marker is skipped.

  C. THE REFUTATION MARKERS MUST NOT INCLUDE THE WORDS A CORRECT ASSERTION USES.
     This is the defect that made the first draft of this file a silent no-op. Its
     marker list contained "in scope", "excluding", "including" and "scope-sensitive",
     which are precisely the words CLAUDE.md item 13 uses to STATE its scope, as the
     file's own rule A demands. Every properly-scoped assertion in all three watched
     files was therefore skipped as if it were a refutation, and the check reported
     "0 blocking findings" without ever having extracted a single assertion.
     Markers here are narrowed to attribution and retirement language only.

HOW AN ASSERTION IS FOUND. Not by one phrase-shaped regex. Every integer in the file
is a candidate; each is classified from its immediate left and right context into
per-name, total, or neither, and only classified ones are compared. This matters
because the live phrasings are not uniform: a whitespace table in CLAUDE.md, an
inline "DRIFT_THRESHOLD 8, DRIFT_M 1, ... total 22 in-scope .py sites" in
check_claims.py, and "at 22 sites excluding archive/ or 23 including it" in
audit_integrity_guard.py. A single "declared at N sites" pattern matches none of them.

Findings carry the per-name breakdown, so a disagreement says WHICH name moved.

Modes:
  hook  reads PreToolUse JSON on stdin, inspects the Edit/Write payload, and emits a
        permissionDecision. Exits 0 always; the decision rides in the JSON.
  cli   no stdin JSON. Scans the watched files and prints findings, then a summary.
        Exit 1 if any BLOCK-level finding, else 0. Matches register_integrity.py.

Usage:
    python3 .claude/checks/count_claims_check.py
    python3 .claude/checks/count_claims_check.py --quiet
    python3 .claude/checks/count_claims_check.py --show-live
    python3 .claude/checks/count_claims_check.py --root /path/to/fixture
    echo '<PreToolUse json>' | python3 .claude/checks/count_claims_check.py
"""

import argparse
import json
import os
import re
import sys

DEFAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

NAMES = ["DRIFT_THRESHOLD_M", "L2_DRIFT_M", "DRIFT_THRESHOLD", "DRIFT_M", "THRESHOLD"]

# Always excluded: not part of any defensible scope.
#
# /.claude/checks/ is excluded for a reason that bit this file during development.
# A checker necessarily QUOTES the declarations it hunts, and a quote inside a
# module docstring does not start with "#", so a comment filter does not catch it.
# Excluding only __file__ is not enough: the moment a second copy of a checker
# exists in that directory, each counts the other and every total shifts by one.
# This is consistent with CLAUDE.md item 13's own stated scope, which counts
# "assignments of the literal only, not prose". A quoted example is prose.
HARD_SKIP = ("/.git/", "/third_party/", "/__pycache__/", "/.claude/worktrees/",
             "/can-it-ford/can-it-ford/", "/.claude/checks/")
# Scope-variable: register D7's stated scope excludes these, but D7's own number
# counted one of them. Both totals are therefore reported.
SOFT_SKIP = ("/archive/", "/_archive/", "/session_archive/")

# STRICT: a bare literal assignment, NAME = 0.05
ASSIGN = (r'(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])'
          r'\s*(?::\s*[A-Za-z_][\w\[\], ]*)?\s*[:=]\s*0\.05(?![0-9])')
# LOOSE: NAME is bound and 0.05 appears on the same line, which also catches a
# default-valued expression. The one that matters is analysis/gp_surrogate.py:14,
#   THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
# a real fifth-name declaration of the 0.05 default, CLI-overridable, and NOT a
# hard-coded constant. Whether it belongs in the count is a judgement call, and
# that judgement is the SECOND binary choice behind the moving totals.
LOOSE = (r'(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])'
         r'\s*(?::[^=\n]*)?=[^\n]*0\.05(?![0-9])')

MODES = ("strict", "loose")
SCOPES = ("excl", "incl")

SCOPE_LABEL = {"in_scope": "excl", "with_archive": "incl"}


# --------------------------------------------------------------------------
# Live re-derivation. Pure pathlib/os + re. No grep subprocess, by design:
# the shell `grep` in this environment wraps ugrep with --ignore-files and
# silently skips every gitignored path, which is register H0 and the reason
# renders/ went missing from the first count.
# --------------------------------------------------------------------------

def live_counts(root, self_path=None):
    """Return {(mode, scope): {name: count}}."""
    out = {(m, s): {n: 0 for n in NAMES} for m in MODES for s in SCOPES}
    pats = {m: [(n, re.compile(tpl % n)) for n in NAMES]
            for m, tpl in (("strict", ASSIGN), ("loose", LOOSE))}
    self_path = os.path.abspath(self_path or __file__)
    for dirpath, dirs, files in os.walk(root):
        # Test the path RELATIVE to root, never the absolute one. If root itself
        # sits under a skipped path, which it does whenever this file is installed
        # in a worktree's .claude/checks/, an absolute test prunes the entire tree,
        # reports every name as 0, and then BLOCKs a CLAUDE.md that is correct.
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        marker = "/" if rel_dir == "." else "/" + rel_dir + "/"
        if any(s in marker for s in HARD_SKIP):
            dirs[:] = []
            continue
        in_soft = any(s in marker for s in SOFT_SKIP)
        for f in files:
            if not f.endswith(".py") or ".bak" in f:
                continue
            full = os.path.join(dirpath, f)
            # Never count this file. It necessarily quotes the patterns it hunts.
            if os.path.abspath(full) == self_path:
                continue
            try:
                with open(full, encoding="utf-8", errors="ignore") as fh:
                    lines = fh.read().splitlines()
            except OSError:
                continue
            for ln in lines:
                # A commented-out declaration is prose, not a declaration.
                if ln.lstrip().startswith("#"):
                    continue
                for mode in MODES:
                    tpl = ASSIGN if mode == "strict" else LOOSE
                    for n, pat in pats[mode]:
                        if not pat.search(ln):
                            continue
                        # Longest name wins, so a _M or L2_ line is counted once.
                        if n == "DRIFT_THRESHOLD" and re.search(tpl % "DRIFT_THRESHOLD_M", ln):
                            continue
                        if n == "DRIFT_M" and re.search(tpl % "L2_DRIFT_M", ln):
                            continue
                        if n == "THRESHOLD" and any(
                                re.search(tpl % o, ln)
                                for o in ("DRIFT_THRESHOLD_M", "DRIFT_THRESHOLD")):
                            continue
                        out[(mode, "incl")][n] += 1
                        if not in_soft:
                            out[(mode, "excl")][n] += 1
                        break
    return out


class Readings:
    """Every reading a careful person could defend, per name and in total."""

    def __init__(self, per):
        self.per = per
        self.totals = {k: sum(v.values()) for k, v in per.items()}

    def name_allowed(self, name, scope):
        scopes = (SCOPE_LABEL[scope],) if scope in SCOPE_LABEL else SCOPES
        return sorted({self.per[(m, s)][name] for m in MODES for s in scopes})

    def total_allowed(self, scope):
        scopes = (SCOPE_LABEL[scope],) if scope in SCOPE_LABEL else SCOPES
        return sorted({self.totals[(m, s)] for m in MODES for s in scopes})

    def breakdown(self, scope=None):
        s = SCOPE_LABEL[scope] if scope in SCOPE_LABEL else "excl"
        parts = []
        for n in NAMES:
            lo = self.per[("loose", s)][n]
            st = self.per[("strict", s)][n]
            parts.append("%s %d%s" % (n, st, ("/%d loose" % lo) if lo != st else ""))
        return ", ".join(parts)

    def describe(self):
        label = {("strict", "excl"): "bare literals only, archive/ excluded",
                 ("strict", "incl"): "bare literals only, archive/ included",
                 ("loose", "excl"): "plus the gp_surrogate default, archive/ excluded",
                 ("loose", "incl"): "plus the gp_surrogate default, archive/ included"}
        keys = sorted(self.totals, key=lambda k: (self.totals[k], label[k]))
        return ["%d  (%s)" % (self.totals[k], label[k]) for k in keys]


# --------------------------------------------------------------------------
# Assertion extraction.
# --------------------------------------------------------------------------

NAME_ALT = r"(?:DRIFT_THRESHOLD_M|L2_DRIFT_M|DRIFT_THRESHOLD|DRIFT_M|THRESHOLD)"

# An integer that is not part of a decimal and not glued to an identifier.
# "0.05" yields nothing: "0" is followed by ".0", "05" is preceded by ".".
INT = re.compile(r"(?<![A-Za-z0-9_.])(\d{1,4})(?!\d)(?!\.\d)")

# NAME immediately before the number:  "DRIFT_THRESHOLD_M  5"
LEFT_NAME = re.compile(r"(" + NAME_ALT + r")(?![A-Za-z0-9_])[ \t]*$")
# Same name continued into its with-archive figure: "DRIFT_THRESHOLD 8 in scope, 9"
# NOT case-insensitive. The captured text is used as a dict key into the live
# per-name readings, which are keyed by the exact-case NAMES; a lowercased capture
# would raise KeyError mid-report. Membership is re-checked at use anyway.
LEFT_NAME_CONT = re.compile(
    r"(" + NAME_ALT + r")(?![A-Za-z0-9_])\s+\d+\s+in[-\s]scope,\s*$")
# NAME ... at N sites:  "L2_DRIFT_M is the second most common at 7 sites"
LEFT_NAME_AT = re.compile(
    r"(" + NAME_ALT + r")(?![A-Za-z0-9_])[^.\n]{0,80}?\bat\s+$")
# "total 22", "TOTAL   22", "giving 22", "accepts 22", "four defensible totals, 22"
LEFT_TOTAL = re.compile(
    r"\b(?:totals?|giving|accepts?|accepting)\b[^A-Za-z0-9\n]{0,20}$", re.IGNORECASE)
# A line that is nothing but "N   <words> archive/ excluded|included" is a row of a
# totals table. Shape-based, so it survives the wording changing again.
TABLE_ROW = re.compile(r"^\s*$")
RIGHT_TABLE = re.compile(r"^[^\n]{0,70}?archive/?\s*(excluded|included)\b", re.I)
# Continuation of a list of totals already begun on this line: "22, 23 or 24",
# "22 / 23 / 23 / 24". Only honoured AFTER a total was classified on the same line,
# so "Lines 46, 47 and 48 all read 0.05" cannot be swept in.
LEFT_LIST = re.compile(r"\d\s*(?:,|/|\bor\b)\s*$")

# Right-context cues that make a bare integer a TOTAL. Ordered; first wins.
# Deliberately NOT a bare "N sites": "at 7 sites, six of them poster generators"
# is a per-name figure for L2_DRIFT_M, and reading it as a total is a false BLOCK.
RIGHT_TOTAL = (
    (re.compile(r"^\s*in[-\s]scope\b", re.I), "in_scope"),
    (re.compile(r"^\s*(?:\.py\s+)?sites\s+excluding\b", re.I), "in_scope"),
    (re.compile(r"^\s*(?:\.py\s+)?sites\s+including\b", re.I), "with_archive"),
    (re.compile(r"^\s*including\s+it\b", re.I), "with_archive"),
    (re.compile(r"^\s*(?:with|counting)\s+(?:the\s+)?archive", re.I), "with_archive"),
    (re.compile(r"^\s*places\b", re.I), None),
    (re.compile(r"^\s*(?:\.py\s+)?declaration\s+sites\b", re.I), None),
    # "22 strict/no-archive, 23 strict/archive, 23 loose/no-archive, 24 loose/archive"
    (re.compile(r"^\s*(?:strict|loose)\s*/\s*no-archive\b", re.I), "in_scope"),
    (re.compile(r"^\s*(?:strict|loose)\s*/\s*archive\b", re.I), "with_archive"),
)

SCOPE_CUES = (
    (re.compile(r"^\s*(?:in[-\s]scope\b|(?:\.py\s+)?sites\s+excluding\b|excluding\s+archive)", re.I), "in_scope"),
    (re.compile(r"^\s*(?:with\s+archive|counting\s+(?:the\s+)?archive|including\s+it|if\s+archive|(?:\.py\s+)?sites\s+including)", re.I), "with_archive"),
)

# A line that retires, attributes or disputes a number is not asserting it.
# NARROW BY DESIGN. See rule C in the module docstring: scope words such as
# "in scope", "excluding" and "including" belong to CORRECT assertions and must
# never appear here.
REFUTATION = re.compile(
    r"D7'?s\b|cannot be reproduced|does not reproduce|do not cite|never quote|"
    r"supersed|\bearlier\b|\bpreviously\b|hypothesis|unproven|refut|retract|"
    r"\bstale\b|was wrong|Neither the old|\bformerly\b|used to (?:read|say)",
    re.IGNORECASE,
)

# The claim must actually be about the drift tolerance, not some unrelated count.
TOPIC = re.compile(
    r"DRIFT_THRESHOLD|L2_DRIFT_M|DRIFT_M|drift[ _-]?toleran|drift[ _-]?threshold|"
    r"FIVE names|five names",
    re.IGNORECASE,
)
# Wide on purpose. CLAUDE.md item 13's four-row totals table sits more than six
# lines from the nearest drift-family word, so a tight window skipped the most
# authoritative assertion in the file before any integer was even looked at. The
# anchor is a backstop against unrelated sections; the per-integer cues are what
# actually discriminate.
ANCHOR_WINDOW = 20


class Assertion:
    def __init__(self, line_no, kind, label, asserted, scope, raw):
        self.line_no = line_no
        self.kind = kind          # "per-name" | "total"
        self.label = label        # a NAME, or "TOTAL"
        self.asserted = asserted
        self.scope = scope        # "in_scope" | "with_archive" | None
        self.raw = raw


def _scope_from(right):
    for pat, scope in SCOPE_CUES:
        if pat.search(right):
            return scope
    return None


def extract_assertions(text):
    """Classify every integer in the text. Unclassifiable integers are ignored."""
    lines = text.splitlines()
    found = []
    for idx, line in enumerate(lines):
        lo = max(0, idx - ANCHOR_WINDOW)
        hi = min(len(lines), idx + ANCHOR_WINDOW + 1)
        if not TOPIC.search("\n".join(lines[lo:hi])):
            continue
        if REFUTATION.search(line):
            continue
        nxt = lines[idx + 1] if idx + 1 < len(lines) else ""
        total_on_line = False
        for m in INT.finditer(line):
            left = line[:m.start()]
            # Two of the three watched files are Python, so an assertion routinely
            # wraps across adjacent string literals and the continuation begins
            # with a quote. Blanking quotes lets "23 " + '"loose/no-archive' read as
            # one phrase; no cue depends on quote characters.
            right = (line[m.end():] + " " + nxt)[:140].replace('"', " ").replace("'", " ")
            kind = label = None
            scope = _scope_from(right)

            # Order matters. A right-hand TOTAL cue outranks LEFT_NAME_AT, or
            # "DRIFT_THRESHOLD is declared at 22 declaration sites" reads as a
            # per-name figure of 22 and BLOCKs a correct sentence.
            hit = LEFT_NAME.search(left)
            hit_cont = LEFT_NAME_CONT.search(left) if not hit else None
            if hit:
                kind, label = "per-name", hit.group(1)
            elif hit_cont:
                kind, label, scope = "per-name", hit_cont.group(1), "with_archive"
            else:
                for pat, sc in RIGHT_TOTAL:
                    if pat.search(right):
                        kind, label = "total", "TOTAL"
                        scope = scope or sc
                        break
                if kind is None and LEFT_TOTAL.search(left):
                    kind, label = "total", "TOTAL"
                if kind is None and TABLE_ROW.match(left):
                    row = RIGHT_TABLE.match(right)
                    if row:
                        kind, label = "total", "TOTAL"
                        scope = ("in_scope" if row.group(1).lower() == "excluded"
                                 else "with_archive")
                if kind is None:
                    hit_at = LEFT_NAME_AT.search(left)
                    if hit_at:
                        kind, label = "per-name", hit_at.group(1)
                    elif total_on_line and LEFT_LIST.search(left):
                        kind, label, scope = "total", "TOTAL", scope

            if kind is None:
                continue
            # A per-name label is used as a dict key into the live readings. Never
            # trust a capture to be a known name; an unknown one is a silent KeyError.
            if kind == "per-name" and label not in NAMES:
                continue
            if kind == "total":
                total_on_line = True
            found.append(Assertion(idx + 1, kind, label, int(m.group(1)),
                                   scope, line.strip()[:130]))
    return found


# --------------------------------------------------------------------------
# Registry. One claim type today; a second is a new entry, not a redesign.
# --------------------------------------------------------------------------

class CountClaim:
    def __init__(self, claim_id, quantity, files, recompute, extractor, authority):
        self.claim_id = claim_id
        self.quantity = quantity
        self.files = files
        self.recompute = recompute
        self.extractor = extractor
        self.authority = authority


REGISTRY = [
    CountClaim(
        claim_id="CC1",
        quantity="DRIFT_THRESHOLD 0.05 declaration sites in *.py",
        files=("CLAUDE.md",
               "scripts/check_claims.py",
               ".claude/hooks/audit_integrity_guard.py"),
        recompute=lambda root, self_path=None: Readings(live_counts(root, self_path)),
        extractor=extract_assertions,
        authority="CLAUDE.md item 13; register D7 and D7a",
    ),
]


class Finding:
    def __init__(self, level, code, message):
        self.level = level
        self.code = code
        self.message = message

    def __str__(self):
        return "%-7s [%s] %s" % (self.level, self.code, self.message)


def check_claim(claim, root, self_path=None):
    readings = claim.recompute(root, self_path)
    findings = []
    checked = 0
    for rel in claim.files:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            findings.append(Finding(
                "BLOCK", "missing-watched-file",
                "%s: watched file %s does not exist, so its count assertion cannot be "
                "verified." % (claim.claim_id, rel)))
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError as exc:
            findings.append(Finding(
                "BLOCK", "unreadable", "%s: cannot read %s: %s" % (claim.claim_id, rel, exc)))
            continue
        for a in claim.extractor(text):
            checked += 1
            if a.kind == "per-name":
                allowed = readings.name_allowed(a.label, a.scope)
            else:
                allowed = readings.total_allowed(a.scope)
            if a.asserted in allowed:
                continue
            findings.append(Finding(
                "BLOCK", "stale-count",
                "%s %s:%d asserts %s = %d (%s), but the live re-derivation gives %s. "
                "Live per-name breakdown, %s scope: %s. This number has been wrong "
                "three times because nobody re-derived it; re-run this check and quote "
                "the enumeration, or state the scope you mean. Authority: %s.\n"
                "        %s"
                % (claim.claim_id, rel, a.line_no, a.label, a.asserted,
                   a.scope or "scope unstated",
                   " or ".join(str(x) for x in allowed),
                   a.scope or "in_scope",
                   readings.breakdown(a.scope),
                   claim.authority, a.raw)))
    return findings, checked, readings


# --------------------------------------------------------------------------
# Hook mode
# --------------------------------------------------------------------------

def hook_mode(data, root):
    ti = data.get("tool_input", {}) or {}
    path = ti.get("file_path", "") or ""
    rel = os.path.relpath(path, root) if path.startswith(root) else path
    claim = next((c for c in REGISTRY
                  if any(rel.endswith(w) or w in rel for w in c.files)), None)
    if claim is None:
        sys.exit(0)
    payload = (ti.get("new_string", "") or "") + "\n" + (ti.get("content", "") or "")
    if not payload.strip() or not TOPIC.search(payload):
        sys.exit(0)
    asserts = claim.extractor(payload)
    if not asserts:
        sys.exit(0)
    readings = claim.recompute(root, None)
    bad = []
    for a in asserts:
        allowed = (readings.name_allowed(a.label, a.scope) if a.kind == "per-name"
                   else readings.total_allowed(a.scope))
        if a.asserted not in allowed:
            bad.append((a, allowed))
    if not bad:
        sys.exit(0)
    detail = "; ".join(
        "%s = %d, live gives %s" % (a.label, a.asserted, " or ".join(str(x) for x in al))
        for a, al in bad)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "count_claims_check: this edit to %s asserts %s. Live per-name breakdown: "
            "%s. Defensible totals: %s. This assertion has been wrong three times (16, "
            "then a bare 24), every time because nobody re-derived it and nobody stated "
            "which scope they meant. There are TWO independent binary choices: archive/ "
            "in or out, and whether to count analysis/gp_surrogate.py:14 where THRESHOLD "
            "defaults to 0.05 without being a bare literal. Quote a total WITH its scope, "
            "or state the enumeration instead of a number. If you are quoting a number in "
            "order to retire it, say so on the same line and this check steps aside."
            % (rel, detail, readings.breakdown(None),
               ", ".join(str(t) for t in sorted(set(readings.totals.values()))))),
    }}))
    sys.exit(0)


def read_stdin_json():
    """Read hook JSON from stdin WITHOUT hanging when there is no piped input.

    sys.stdin.isatty() is False whenever the process is launched from a script or a
    background shell, not only when something is piped in, so gating on isatty()
    alone makes a plain CLI run block forever on read(). select() with a short
    timeout distinguishes "no input coming" from "input not written yet".
    """
    if sys.stdin.isatty():
        return None
    try:
        import select
        ready, _, _ = select.select([sys.stdin], [], [], 0.25)
        if not ready:
            return None
    except Exception:
        return None
    raw = sys.stdin.read()
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("COUNT_CLAIMS_ROOT", DEFAULT_ROOT),
                    help="repo root to scan; overridable so fixtures never touch the repo")
    ap.add_argument("--quiet", action="store_true", help="print only findings, no summary")
    ap.add_argument("--show-live", action="store_true", help="print the live re-derivation and stop")
    ap.add_argument("--cli", action="store_true", help="force CLI mode, never read stdin")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    data = None if args.cli else read_stdin_json()
    if isinstance(data, dict) and "tool_input" in data:
        hook_mode(data, root)
        return 0

    all_findings, total_checked, last = [], 0, None
    for claim in REGISTRY:
        findings, checked, readings = check_claim(claim, root)
        all_findings.extend(findings)
        total_checked += checked
        last = readings
        if args.show_live:
            print("live re-derivation, %s" % claim.quantity)
            for n in NAMES:
                se = readings.per[("strict", "excl")][n]
                si = readings.per[("strict", "incl")][n]
                le = readings.per[("loose", "excl")][n]
                extra = []
                if si != se:
                    extra.append("%d with archive/" % si)
                if le != se:
                    extra.append("%d counting the default-valued binding" % le)
                print("  %-20s %d%s" % (n, se, ("   (" + ", ".join(extra) + ")") if extra else ""))
            print("")
            for line in readings.describe():
                print("    %s" % line)
    if args.show_live:
        return 0

    blocking = [f for f in all_findings if f.level == "BLOCK"]
    for f in all_findings:
        print(f)

    if not args.quiet:
        print("")
        print("count_claims_check.py summary")
        print("  root              %s" % root)
        print("  claims in registry %d (%s)" % (len(REGISTRY), ", ".join(c.claim_id for c in REGISTRY)))
        print("  assertions found  %d, classified and compared" % total_checked)
        if last is not None:
            print("  live per-name     %s" % last.breakdown(None))
            print("  defensible totals %s"
                  % ", ".join(str(t) for t in sorted(set(last.totals.values()))))
            for line in last.describe():
                print("      %s" % line)
        print("  blocking defects  %d" % len(blocking))

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
