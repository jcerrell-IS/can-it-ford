#!/usr/bin/env python3
"""
Guard against asserting a declaration-site COUNT that nobody re-derived.

Why this exists. The drift-tolerance count has been "settled" wrong three times:

  1. "16 places under four names"  -> a floor, produced by a grep that skipped
     renders/ because the shell `grep` wraps ugrep with --ignore-files (register H0).
  2. "24 places under five names, THRESHOLD 2" -> register D7, 2026-08-11.
  3. A same-day recount that asserted D7's 24 "does not reproduce" and propagated a
     bare 22 into three files.

Reading 3 was ALSO WRONG, and finding out why is what this file encodes. D7's 24 is
correct. It reproduces exactly under (count the default-valued binding, include
archive/). The recount missed analysis/gp_surrogate.py:14,

    THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05

a genuine fifth-name declaration of the 0.05 default that a strict `NAME = 0.05`
regex does not match. That is D7's second THRESHOLD, and it was called
unreproducible by a check that could not see it.

Every one of these was an assertion nobody re-derived before trusting, including the
refutation. That is the failure shape, not the number.

TWO THINGS IT MUST GET RIGHT, both learned the hard way in this repo:

  A. THERE ARE TWO INDEPENDENT BINARY CHOICES, not one, so there are FOUR defensible
     totals, and 23 is reachable by two different routes. That is exactly why two
     prior counts appeared to agree while disagreeing about what they counted:
         22  bare literals only, archive/ excluded
         23  bare literals only, archive/ included
         23  plus the gp_surrogate default, archive/ excluded
         24  plus the gp_surrogate default, archive/ included
     A checker that hardcodes one number just relocates the bug, so this compares
     against the SET of live totals and passes if the assertion matches any of them.
     A bare number with no scope is what is actually wrong, not any one value.

  B. QUOTING A NUMBER IN ORDER TO RETIRE IT IS CORRECT, AND MUST NOT BLOCK. This is
     the same false-positive class that makes check_claims C5 and C8 fire on their
     own refutations. A line carrying a refutation marker is skipped.

Modes:
  hook  reads PreToolUse JSON on stdin, inspects the Edit/Write payload, and emits a
        permissionDecision. Exits 0 always; the decision rides in the JSON.
  cli   no stdin JSON. Scans the watched files and prints findings.
        Exit 1 if any BLOCK-level finding, else 0.

Usage:
    python3 .claude/checks/count_claims_check.py
    python3 .claude/checks/count_claims_check.py --show-live
    echo '<PreToolUse json>' | python3 .claude/checks/count_claims_check.py
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

WATCHED = (
    "CLAUDE.md",
    "scripts/check_claims.py",
    ".claude/hooks/audit_integrity_guard.py",
)

NAMES = ["DRIFT_THRESHOLD_M", "L2_DRIFT_M", "DRIFT_THRESHOLD", "DRIFT_M", "THRESHOLD"]

# Always excluded: not part of any defensible scope.
HARD_SKIP = ("/.git/", "/third_party/", "/__pycache__/", "/.claude/worktrees/",
             "/can-it-ford/can-it-ford/")
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

# "declared as a literal in 24 places", "declared at 23 sites", "24 declaration sites"
COUNT_CLAIM = re.compile(
    r'declared\s+(?:as\s+a\s+literal\s+)?(?:in|at)\s+(?:\*\*)?(\d{1,3})(?:\*\*)?\s+(?:places|sites)'
    r'|(?:\*\*)?(\d{1,3})(?:\*\*)?\s+declaration\s+sites',
    re.IGNORECASE,
)

# A line that retires, quotes or disputes a number is not asserting it.
REFUTATION = re.compile(
    r"does not reproduce|cannot be reproduced|was wrong|refut|retract|stale|supersed|"
    r"corrected|previously|earlier|D7's|register D7|unproven|hypothesis|do not cite|"
    r"never quote|floor|disagree|scope-sensitive|in scope|excluding|including",
    re.IGNORECASE,
)

# The claim must actually be about the drift tolerance, not some unrelated count.
TOPIC = re.compile(r"DRIFT_THRESHOLD|L2_DRIFT_M|DRIFT_M|drift[ _-]?toleran|drift[ _-]?threshold",
                   re.IGNORECASE)


def live_counts():
    """Return {(mode, scope): {name: count}} for mode in strict/loose and
    scope in excl/incl (archive)."""
    out = {(m, s): {n: 0 for n in NAMES}
           for m in ("strict", "loose") for s in ("excl", "incl")}
    pats = {m: [(n, re.compile(tpl % n)) for n in NAMES]
            for m, tpl in (("strict", ASSIGN), ("loose", LOOSE))}
    for dirpath, dirs, files in os.walk(REPO_ROOT):
        marker = dirpath + "/"
        if any(s in marker for s in HARD_SKIP):
            dirs[:] = []
            continue
        in_soft = any(s in marker for s in SOFT_SKIP)
        for f in files:
            if not f.endswith(".py") or ".bak" in f:
                continue
            # Never count this file. It necessarily quotes the patterns it hunts.
            if os.path.abspath(os.path.join(dirpath, f)) == os.path.abspath(__file__):
                continue
            try:
                lines = open(os.path.join(dirpath, f), encoding="utf-8",
                             errors="ignore").read().splitlines()
            except OSError:
                continue
            for ln in lines:
                # A commented-out or quoted declaration is prose, not a declaration.
                # This file itself quotes gp_surrogate.py:14 in its own header, and
                # without this guard the checker counts its own documentation as a
                # sixth site. That is the exact failure class it exists to catch.
                if ln.lstrip().startswith("#"):
                    continue
                for mode in ("strict", "loose"):
                    tpl = ASSIGN if mode == "strict" else LOOSE
                    for n, pat in pats[mode]:
                        if not pat.search(ln):
                            continue
                        # longest name wins, so a _M or L2_ line is counted once
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


def defensible_totals():
    """Every total a careful person could defend, and the per-name detail.

    There are TWO independent binary choices, and they are why this number has
    moved three times:
      1. include the archive/ copy, or honour register D7's stated exclusion
      2. count only bare literals, or also count the gp_surrogate.py default
    Two choices give four totals, and 23 is reachable by two different routes,
    which is precisely why two prior counts appeared to agree while disagreeing
    about what they were counting. Any of these is defensible WITH its scope
    stated; a bare number is not.
    """
    c = live_counts()
    totals = {k: sum(v.values()) for k, v in c.items()}
    return sorted(set(totals.values())), totals, c


def scan_text(text, allowed):
    """Return list of (line_no, asserted, line) that match no defensible total."""
    bad = []
    for i, ln in enumerate(text.splitlines(), 1):
        if not TOPIC.search(ln) or REFUTATION.search(ln):
            continue
        for m in COUNT_CLAIM.finditer(ln):
            asserted = int(m.group(1) or m.group(2))
            if asserted not in allowed:
                bad.append((i, asserted, ln.strip()[:120]))
    return bad


def describe(totals):
    """One line per defensible reading, so the scope is never implicit."""
    label = {("strict", "excl"): "bare literals only, archive/ excluded",
             ("strict", "incl"): "bare literals only, archive/ included",
             ("loose", "excl"): "plus the gp_surrogate default, archive/ excluded",
             ("loose", "incl"): "plus the gp_surrogate default, archive/ included"}
    return ["%d  (%s)" % (totals[k], label[k]) for k in sorted(totals, key=lambda k: totals[k])]


def hook_mode(data):
    ti = data.get("tool_input", {}) or {}
    path = ti.get("file_path", "") or ""
    rel = os.path.relpath(path, REPO_ROOT) if path.startswith(REPO_ROOT) else path
    if not any(rel.endswith(w) or w in rel for w in WATCHED):
        sys.exit(0)
    payload = (ti.get("new_string", "") or "") + "\n" + (ti.get("content", "") or "")
    if not payload.strip():
        sys.exit(0)
    # Cheap pre-filter: only walk the repo if the payload actually asserts a count.
    if not COUNT_CLAIM.search(payload) or not TOPIC.search(payload):
        sys.exit(0)

    allowed, totals, _ = defensible_totals()
    bad = scan_text(payload, allowed)
    if not bad:
        sys.exit(0)
    detail = "; ".join("asserts %d" % a for _, a, _ in bad)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "count_claims_check: this edit to %s %s, but no defensible live reading "
            "gives that. The live readings are: %s. This assertion has been wrong "
            "three times (16, then a same-day 22, then a bare 24), every time because "
            "nobody re-derived it and nobody stated which scope they meant. There are "
            "TWO independent binary choices, archive/ in or out, and whether to count "
            "analysis/gp_surrogate.py:14 where THRESHOLD defaults to 0.05 without "
            "being a bare literal. Quote a total WITH its scope, or state the "
            "enumeration instead of a number. If you are quoting a number in order to "
            "retire it, say so on the same line and this check will step aside."
            % (rel, detail, "; ".join(describe(totals)))),
    }}))
    sys.exit(0)


def cli_mode(show_live):
    allowed, totals, per = defensible_totals()
    print("live re-derivation, 0.05 declarations in *.py")
    for n in NAMES:
        se, si = per[("strict", "excl")][n], per[("strict", "incl")][n]
        le = per[("loose", "excl")][n]
        extra = []
        if si != se:
            extra.append("%d with archive/" % si)
        if le != se:
            extra.append("%d counting the default-valued binding" % le)
        print("  %-20s %d%s" % (n, se, ("   (" + ", ".join(extra) + ")") if extra else ""))
    print("")
    print("  defensible totals, all four readings:")
    for line in describe(totals):
        print("    %s" % line)
    print("  accepted set: %s" % ", ".join(str(a) for a in allowed))
    if show_live:
        return 0
    print("")
    findings = 0
    for w in WATCHED:
        p = os.path.join(REPO_ROOT, w)
        if not os.path.exists(p):
            print("BLOCK   [missing-watched-file] %s does not exist" % w)
            findings += 1
            continue
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError as exc:
            print("BLOCK   [unreadable] %s: %s" % (w, exc))
            findings += 1
            continue
        for i, asserted, ln in scan_text(text, allowed):
            print("BLOCK   [stale-count] %s:%d asserts %d, no defensible reading gives that (%s)\n        %s"
                  % (w, i, asserted, ", ".join(str(a) for a in allowed), ln))
            findings += 1
    print("")
    print("count_claims_check: %d blocking finding(s)" % findings)
    return 1 if findings else 0


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
    show_live = "--show-live" in sys.argv
    data = None if "--cli" in sys.argv else read_stdin_json()
    if isinstance(data, dict) and "tool_input" in data:
        hook_mode(data)
        sys.exit(0)
    sys.exit(cli_mode(show_live))


if __name__ == "__main__":
    main()
