#!/usr/bin/env python3
"""Detect interleaved (spliced) rows in the shared append-only board.

WHY THIS EXISTS
---------------
Measured 2026-08-19 by d18-platform. Eight concurrent shell processes appending
one line each to a shared file, which is exactly the board's write pattern:

    row bytes   lines written   corrupted
         200         200            0
         500         200            0
        1000         200            0
        1023         200            0
        1500         200           30
        2000         200           23
        4000         200           83

Writes chunk at EXACTLY 1024 bytes and concurrent writers interleave at that
boundary. One wrecked line read `C * 1024, A * 1024, C * 976`: writer A's row
spliced into the middle of writer C's.

THE PART THAT MAKES IT DANGEROUS: the LINE COUNT STAYS CORRECT. 200 lines went
in and 200 lines came out. Every check anyone would naturally run on an
append-only log, "did my row land", "how many rows are there", passes on a
corrupted file. Row count is NOT a detector.

WHAT THIS CHECK CAN AND CANNOT SEE
----------------------------------
It is a PARTIAL detector and says so, because a detector presented as complete
is the same defect it exists to catch.

A splice inserts another writer's 1024-byte chunk into the middle of a row.

  CATCHABLE   the inserted chunk is the START of another row, so it carries that
              row's `| YYYY-MM-DD HH:MM |` header, and the merged line then
              holds two headers.
  CATCHABLE   the displaced tail lands as its own line with no header and no
              leading pipe.
  NOT CATCHABLE  the inserted chunk is a MIDDLE chunk of another row (byte 1024
              onward), so it carries no header at all. The merged line has
              exactly one header, starts with a pipe, and looks well formed.
              `self_test` demonstrates this with a concrete input rather than
              describing it.

So a clean run means "no splice of the catchable kinds", never "the board is
intact". The oversize-row count is the leading indicator and is the number to
act on, because it is what makes any splice possible in the first place.

WHY OVERSIZE ROWS DO NOT FAIL THE CHECK
---------------------------------------
64 percent of rows already exceed 1024 bytes. Exiting non-zero on that would
make this check red on every run from birth, and the project has just finished
measuring what happens to a check that is always red: it gets wrapped in
`continue-on-error` and stops meaning anything. Splices fail the check.
Oversize rows are reported and counted.

Usage:
  python3 .claude/checks/board_splice_check.py [--board PATH]
  python3 .claude/checks/board_splice_check.py --self-test
"""

from __future__ import annotations

import argparse
import os
import re
import sys

DEFAULT_BOARD = "/Users/josie/can-it-ford/.claude/state/r8_board.md"

# A row header, e.g. "| 2026-08-19 19:12 |".
HEADER = re.compile(r"\|\s*20\d\d-\d\d-\d\d\s+\d\d:\d\d\s*\|")

# The measured boundary. Appends at or above this can interleave.
SAFE_ROW_BYTES = 1024


def load_lines(path: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"board not found: {path}")
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    if not text.strip():
        raise ValueError(f"board {path} is empty; that is a failure, not zero rows")
    return [ln for ln in text.split("\n") if ln.strip()]


def find_splices(lines: list[str]) -> list[dict]:
    """Lines carrying two or more row headers: two rows merged into one."""
    out = []
    for i, ln in enumerate(lines, start=1):
        hits = HEADER.findall(ln)
        if len(hits) > 1:
            out.append({"line": i, "headers": len(hits), "bytes": len(ln.encode()),
                        "kind": "double-header splice"})
    return out


def find_orphans(lines: list[str]) -> list[dict]:
    """Non-preamble lines that are neither a row nor markdown prose.

    The displaced tail of a spliced write lands like this. Preamble lines
    (headings, prose, list items) are excluded by shape, not by line number, so
    this survives the preamble being edited.
    """
    out = []
    for i, ln in enumerate(lines, start=1):
        s = ln.lstrip()
        if s.startswith(("|", "#", "-", "*", ">")):
            continue
        if len(s) < 200:
            # Short prose is preamble. A displaced tail is long by construction:
            # it is what is left of a >=1024-byte row after a chunk boundary.
            continue
        out.append({"line": i, "bytes": len(ln.encode()), "kind": "orphan fragment",
                    "head": s[:60]})
    return out


def oversize(lines: list[str]) -> list[dict]:
    out = []
    for i, ln in enumerate(lines, start=1):
        n = len(ln.encode())
        if n >= SAFE_ROW_BYTES and HEADER.search(ln):
            out.append({"line": i, "bytes": n})
    return out


def report(path: str) -> int:
    lines = load_lines(path)
    splices = find_splices(lines)
    orphans = find_orphans(lines)
    big = oversize(lines)
    rows = [ln for ln in lines if HEADER.search(ln)]

    print(f"board            {path}")
    print(f"lines            {len(lines)}")
    print(f"rows (headered)  {len(rows)}")
    if rows:
        sizes = sorted(len(r.encode()) for r in rows)
        print(f"row bytes        median {sizes[len(sizes)//2]}, max {sizes[-1]}")
    print(f"oversize rows    {len(big)} at or above {SAFE_ROW_BYTES} bytes"
          f"  ({100*len(big)//max(len(rows),1)} percent), REPORTED not failed")
    print(f"splices          {len(splices)}")
    print(f"orphan fragments {len(orphans)}")

    for s in splices:
        print(f"  SPLICE line {s['line']}: {s['headers']} headers in one line, "
              f"{s['bytes']} bytes")
    for o in orphans:
        print(f"  ORPHAN line {o['line']}: {o['bytes']} bytes, starts {o['head']!r}")

    if splices or orphans:
        print("\nFAIL: the board carries at least one catchable splice.")
        print("Do NOT rewrite the board to fix it; that loses other sessions' rows.")
        print("Append a correction row naming the damaged line numbers.")
        return 1
    print("\nPASS: no catchable splice. This does NOT prove the board is intact;")
    print("a middle-chunk splice carries no header and is invisible here.")
    return 0


def self_test() -> int:
    """Every detector is exercised with an input that MAKES IT FIRE.

    The falsifier rule (register e81bc9c): a commit adding a check must name the
    input that makes it fail. A check with no such input cannot fail and is not
    a check. So each case below is that named input, and the last case names the
    input this check CANNOT catch.
    """
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    good = "| 2026-08-19 19:12 | d18-platform | claude/r9-platform | did | next | dnt |"
    other = "| 2026-08-19 19:13 | d17-moving | claude/r9-moving | other | next | dnt |"

    print("T1 THE INPUT THAT MAKES IT FAIL: two headers merged into one line")
    spliced = good[:40] + other + good[40:]
    got = find_splices([spliced])
    check("double-header splice is detected", len(got) == 1, f"{len(got)} found")

    print("T2 NEGATIVE CONTROL: clean rows must NOT fire")
    check("two separate clean rows are clean", len(find_splices([good, other])) == 0)
    check("clean rows produce no orphans", len(find_orphans([good, other])) == 0)

    print("T3 THE INPUT THAT MAKES THE ORPHAN DETECTOR FIRE")
    tail = "x" * 900  # a displaced tail: long, no header, no leading pipe
    got = find_orphans([good, tail])
    check("orphan fragment is detected", len(got) == 1, f"{len(got)} found")

    print("T4 NEGATIVE CONTROL: preamble prose must NOT be called an orphan")
    preamble = "Every session appends here after each unit of work. Read it first."
    check("short prose is not an orphan", len(find_orphans([preamble])) == 0)

    print("T5 oversize accounting fires at the measured boundary, not near it")
    pad = "| 2026-08-19 19:12 | s | b | " + "y" * 1000 + " |"
    check("a >=1024-byte row is counted", len(oversize([pad])) == 1,
          f"{len(pad.encode())} bytes")
    check("a short row is not counted", len(oversize([good])) == 0,
          f"{len(good.encode())} bytes")

    print("T6 THE BLIND SPOT, NAMED AND DEMONSTRATED, NOT DESCRIBED")
    # A middle chunk of another row carries no header. Splicing it in produces a
    # line with exactly one header that starts with a pipe and looks well formed.
    middle_chunk = "z" * 1024
    invisible = good[:40] + middle_chunk + good[40:]
    check("middle-chunk splice is NOT detected, as documented",
          len(find_splices([invisible])) == 0 and len(find_orphans([invisible])) == 0,
          "this check cannot see this corruption; the oversize count is the only warning")

    print("T7 the loader distinguishes absent and empty from clean")
    try:
        load_lines("/nonexistent/board.md")
        check("missing board raises", False)
    except FileNotFoundError:
        check("missing board raises", True)

    print(f"\n{len(fails)} failure(s)" + (": " + ", ".join(fails) if fails else ""))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="detect spliced rows in the shared board")
    ap.add_argument("--board", default=DEFAULT_BOARD)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    try:
        return report(args.board)
    except (FileNotFoundError, ValueError) as exc:
        print(f"CANNOT EVALUATE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
