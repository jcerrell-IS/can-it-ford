#!/usr/bin/env python3
"""Block a STALE scenario_sweep.csv by MEASURING it, not by demanding a magic word.

WHAT THIS REPLACED, AND WHY IT HAD TO GO. The previous eleven-line version tested
whether the tool call's text contained one of `wc -l`, `head -1`, `NF`, `awk` or
`column`, and exited 2 if not. Four defects, all measured 2026-08-20:

1. IT MADE THE FILE PERMANENTLY UNREADABLE WITH THE Read TOOL. The matcher includes
   `Read`, whose `tool_input` carries a `file_path` and NO command, so a plain Read
   could never contain `awk` and was blocked every time. Reading the file is how you
   would find out its column count; the guard forbade the thing it was demanding.
2. IT BLOCKED ANY Bash CALL THAT MERELY NAMED THE FILE. Writing a document about it,
   grepping for it, or listing it tripped the guard. That happened to this session
   twice.
3. IT TESTED FOR A SHIBBOLETH, NOT A CONDITION. `echo "# awk"` satisfied it. A caller
   who typed the magic word got through regardless of which copy they were opening,
   and a caller who had already verified the file by other means was refused.
4. NO try/except AROUND json.load(sys.stdin), so malformed input raised, exited
   non-zero, and blocked the call. A guardrail bug became a hard stop.

WHAT IT DOES NOW. It resolves every path-shaped token in the call, and for any that
exists and is named scenario_sweep*.csv it COUNTS THE HEADER COLUMNS. It blocks only
when a referenced file actually carries the stale schema. Naming the file is fine.
Reading it is always fine, and reading is how the stale ones get found.

THE CONDITION IS REAL, WHICH IS WHY THIS IS A REWRITE AND NOT A DELETION. Measured
across the whole disk on 2026-08-20: EIGHT 5-column copies survive, in
`Downloads/can-it-ford/`, two backup trees, an audit tree, a rescue tree and an
archive. CLAUDE.md's standing rule is to use the 10-column live file and never the
5-column snapshot.

AND A THIRD SCHEMA NOBODY HAS RECORDED: `~/Downloads/scenario_sweep_corrected.csv`
has NINE columns. It is neither the stale 5 nor the live 10, its name asserts it is
authoritative, and no project document mentions it. Treated here as stale-unknown and
warned about rather than blocked, because nothing establishes what it is.

FAILS OPEN. Every unexpected condition exits 0 with a note on stderr. A PreToolUse
hook that crashes blocks the tool call, and this file has already cost this project
more calls than the defect it guards.
"""
import json
import os
import re
import sys

LIVE_COLS = 10
STALE_COLS = 5
NAME = re.compile(r"scenario_sweep[\w.-]*\.csv")
PATHISH = re.compile(r"[~\w./-]*scenario_sweep[\w.-]*\.csv")


def header_cols(path):
    """Column count of the header row, or None if it cannot be read."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
    except OSError:
        return None
    if not first.strip():
        return None
    return len(first.rstrip("\n").rstrip("\r").split(","))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception as exc:                                   # noqa: BLE001
        sys.stderr.write("stale_csv_guard: unreadable hook input, allowing "
                         "(%s)\n" % exc)
        return 0

    try:
        tool = data.get("tool_name", "") or ""
        ti = data.get("tool_input", {}) or {}
        blob = " ".join(str(ti.get(k, "") or "") for k in
                        ("command", "file_path", "content", "new_string", "pattern",
                         "path", "old_string"))
        if not NAME.search(blob):
            return 0

        # Reading is always allowed. It is how a stale copy gets identified, and
        # the previous version's refusal to allow it was its worst defect.
        candidates = []
        for tok in PATHISH.findall(blob):
            p = os.path.expanduser(tok)
            if not os.path.isabs(p):
                p = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()), p)
            if os.path.isfile(p):
                candidates.append(p)

        if not candidates:
            # The name appears but resolves to no file on disk: prose, a glob, a
            # remote path, a heredoc body. Nothing to measure, nothing to block.
            return 0

        stale, odd = [], []
        for p in candidates:
            n = header_cols(p)
            if n is None:
                continue
            if n == STALE_COLS:
                stale.append((p, n))
            elif n != LIVE_COLS:
                odd.append((p, n))

        for p, n in odd:
            sys.stderr.write(
                "stale_csv_guard: NOTE %s has %d columns, neither the live %d nor "
                "the known-stale %d. No project record establishes what it is.\n"
                % (p, n, LIVE_COLS, STALE_COLS))

        if stale and tool != "Read":
            sys.stderr.write(
                "BLOCKED by measurement, not by keyword. These referenced files carry "
                "the STALE %d-column schema:\n" % STALE_COLS
                + "".join("  %s  (%d columns)\n" % (p, n) for p, n in stale)
                + "The live file has %d columns. CLAUDE.md's standing rule is to use "
                  "the 10-column live file and never the 5-column snapshot. Eight "
                  "stale copies survive on this disk. Point at the live file, or "
                  "Read this one first if you are auditing it.\n" % LIVE_COLS)
            return 2

        if stale:
            sys.stderr.write(
                "stale_csv_guard: allowing a Read of a STALE %d-column copy so you "
                "can inspect it: %s. Do not source a number from it.\n"
                % (STALE_COLS, ", ".join(p for p, _ in stale)))
        return 0
    except Exception as exc:                                   # noqa: BLE001
        sys.stderr.write("stale_csv_guard: internal error, allowing (%s)\n" % exc)
        return 0


if __name__ == "__main__":
    sys.exit(main())
