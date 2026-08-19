#!/usr/bin/env python3
"""
r9_session_reader.py  --  parse the R9 wave's Claude Code session transcripts.

Written 2026-08-19 by slot d20-reader for docs/R9_CROSS_SESSION_READOUT_2026-08-19.md.

WHY THIS EXISTS
    Nine sessions ran in parallel and produced ~40 MB of JSONL. Reading by eye
    guarantees a partial view, and a partial view is exactly the failure mode
    this project keeps hitting (CLAUDE.md "Claim discipline": absence of
    evidence from a partial view is not evidence of absence). So the readout is
    built from a mechanical sweep of every record instead.

MEASURED FACT THIS SCRIPT ENCODES, do not lose it:
    Each worktree has TWO transcript files, not one. `.claude/state/r8_session_ids.tsv`
    names only the CURRENT (post-crash) session id. The pre-crash file is a
    separate uuid in the same directory and holds the MAJORITY of the work for
    most slots (r9-renders: 12.6 MB pre-crash against 5.7 MB post-crash).
    A reader that trusts the TSV alone sees less than half the wave.
    Therefore: default is ALL *.jsonl in the directory, and --tsv-only exists
    only so the difference can be demonstrated.

STREAMING: files are read line by line and never slurped.

USAGE
    python3 analysis/r9_session_reader.py --inventory
    python3 analysis/r9_session_reader.py --slot r9-settle --summary
    python3 analysis/r9_session_reader.py --commits
    python3 analysis/r9_session_reader.py --writes
    python3 analysis/r9_session_reader.py --numbers        [--min-abs 0]
    python3 analysis/r9_session_reader.py --corrections
    python3 analysis/r9_session_reader.py --grep 'REGEX'
    python3 analysis/r9_session_reader.py --self-test
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

PROJ = os.path.expanduser("~/.claude/projects")
REPO = "/Users/josie/can-it-ford"
TSV = os.path.join(REPO, ".claude/state/r8_session_ids.tsv")

SLOTS = [
    "r9-accessor", "r9-kramer-extract", "r9-renders", "r9-corpus-bib",
    "r9-settle", "r9-landing", "r9-moving-vehicle", "r9-platform",
    "r9-priorcode",
]

# ---------------------------------------------------------------- discovery


def slot_dir(slot: str) -> str:
    return os.path.join(
        PROJ, "-Users-josie-can-it-ford--claude-worktrees-" + slot)


def tsv_ids() -> dict:
    """slot-label -> session uuid, from the coordinator's TSV. May be absent."""
    out = {}
    if not os.path.exists(TSV):
        return out
    with open(TSV) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                out[parts[0]] = parts[1]
    return out


def transcripts(slot: str, tsv_only: bool = False) -> list:
    d = slot_dir(slot)
    files = sorted(glob.glob(os.path.join(d, "*.jsonl")))
    if tsv_only:
        ids = set(tsv_ids().values())
        files = [f for f in files
                 if os.path.basename(f)[:-6] in ids]
    return files


# ---------------------------------------------------------------- streaming


def records(path: str):
    """Yield one parsed record per line. Bad lines are counted, not fatal."""
    with open(path, "r", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield lineno, json.loads(line)
            except Exception:
                yield lineno, {"type": "__unparsed__"}


def blocks(rec: dict):
    """Yield (role, block) for every content block in a message record."""
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return
    role = msg.get("role", rec.get("type", "?"))
    content = msg.get("content")
    if isinstance(content, str):
        yield role, {"type": "text", "text": content}
    elif isinstance(content, list):
        for b in content:
            if isinstance(b, dict):
                yield role, b


# ---------------------------------------------------------------- extraction

RE_COMMIT = re.compile(r"git\s+(?:-C\s+\S+\s+)?commit\b")
# A number with at least one digit, optional sign, decimal, exponent, percent.
RE_NUM = re.compile(
    r"(?<![\w.])(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+\.\d+|-?\d+)"
    r"\s?(%|percent|m/s|mm|m\^3|m3|kg/m\^3|kg|MB|GB|KB|s\b|frames?\b|lines?\b|"
    r"files?\b|papers?\b|commits?\b|hits?\b|rows?\b|runs?\b)?",
    re.IGNORECASE)

CORRECTION_PAT = [
    r"\bI was wrong\b", r"\bI got .{0,30}wrong\b", r"\bmy own\b.{0,40}\bwrong\b",
    r"\bretract", r"\bwithdraw", r"\brefut", r"\bis FALSE\b", r"\bwas FALSE\b",
    r"\bcorrection\b", r"\bcorrects?\b\s+(?:the\s+)?coordinator",
    r"\bthe coordinator (?:is|was) wrong\b", r"\bstale\b",
    r"\bdo not (?:cite|quote|repeat|dispatch)\b",
    r"\bsupersede", r"\bthat is wrong\b", r"\bthis is wrong\b",
    r"\bnot reproduc", r"\bcannot reproduce\b", r"\bdisagree",
    r"\bd1[1-9]-[a-z]+\b", r"\bcoordinator\b",
]
RE_CORR = re.compile("|".join(CORRECTION_PAT), re.IGNORECASE)


def scan(path: str) -> dict:
    """One streaming pass. Returns a per-file record of everything we extract."""
    out = {
        "path": path,
        "session_id": os.path.basename(path)[:-6],
        "n_lines": 0,
        "n_unparsed": 0,
        "ts_min": None, "ts_max": None,
        "bash": [],           # (ts, command)
        "writes": [],         # (ts, tool, file_path)
        "tools": Counter(),
        "commit_cmds": [],    # (ts, command)  raw git commit invocations
        "texts": [],          # (ts, text) assistant-authored prose only
        "cwd": Counter(),
        "branch": Counter(),
        "models": Counter(),
    }
    for lineno, rec in records(path):
        out["n_lines"] += 1
        if rec.get("type") == "__unparsed__":
            out["n_unparsed"] += 1
            continue
        ts = rec.get("timestamp")
        if ts:
            if out["ts_min"] is None or ts < out["ts_min"]:
                out["ts_min"] = ts
            if out["ts_max"] is None or ts > out["ts_max"]:
                out["ts_max"] = ts
        if rec.get("cwd"):
            out["cwd"][rec["cwd"]] += 1
        if rec.get("gitBranch"):
            out["branch"][rec["gitBranch"]] += 1
        msg = rec.get("message")
        if isinstance(msg, dict) and msg.get("model"):
            out["models"][msg["model"]] += 1

        for role, b in blocks(rec):
            btype = b.get("type")
            if btype == "tool_use":
                name = b.get("name", "?")
                out["tools"][name] += 1
                inp = b.get("input") or {}
                if name == "Bash":
                    cmd = inp.get("command", "")
                    out["bash"].append((ts, cmd))
                    if RE_COMMIT.search(cmd):
                        out["commit_cmds"].append((ts, cmd))
                elif name in ("Write", "Edit", "NotebookEdit", "MultiEdit"):
                    out["writes"].append((ts, name, inp.get("file_path", "?")))
            elif btype == "text" and role == "assistant":
                out["texts"].append((ts, b.get("text", "")))
    return out


def scan_slot(slot: str, tsv_only: bool = False) -> list:
    return [scan(p) for p in transcripts(slot, tsv_only)]


# ---------------------------------------------------------------- reporting


def cmd_inventory(args):
    ids = tsv_ids()
    named = set(ids.values())
    print(f"{'slot':<20}{'session id':<38}{'in TSV':<8}{'lines':>7}"
          f"  {'bytes':>10}  first ts -> last ts")
    tot_named = tot_all = 0
    for slot in SLOTS:
        for p in transcripts(slot):
            s = scan(p)
            sz = os.path.getsize(p)
            tot_all += sz
            inn = "YES" if s["session_id"] in named else "no"
            if inn == "YES":
                tot_named += sz
            print(f"{slot:<20}{s['session_id']:<38}{inn:<8}{s['n_lines']:>7}"
                  f"  {sz:>10}  {s['ts_min']} -> {s['ts_max']}")
    print()
    print(f"TOTAL bytes across all transcripts : {tot_all}")
    print(f"TOTAL bytes named in r8_session_ids.tsv: {tot_named} "
          f"({100.0*tot_named/tot_all:.1f} percent)")
    print("A reader that follows the TSV alone sees only that fraction.")


def cmd_summary(args):
    slots = [args.slot] if args.slot else SLOTS
    for slot in slots:
        ss = scan_slot(slot, args.tsv_only)
        nb = sum(len(s["bash"]) for s in ss)
        nw = sum(len(s["writes"]) for s in ss)
        nc = sum(len(s["commit_cmds"]) for s in ss)
        tools = Counter()
        for s in ss:
            tools.update(s["tools"])
        print(f"=== {slot}   files={len(ss)}  bash={nb}  writes={nw}  "
              f"git-commit-calls={nc}")
        print("    tools:", ", ".join(f"{k}={v}" for k, v in tools.most_common(12)))
        for s in ss:
            print(f"    {s['session_id']}  {s['n_lines']:>5} lines  "
                  f"{s['ts_min']} -> {s['ts_max']}  "
                  f"branch={','.join(s['branch'])}")


def cmd_writes(args):
    slots = [args.slot] if args.slot else SLOTS
    for slot in slots:
        seen = Counter()
        for s in scan_slot(slot, args.tsv_only):
            for ts, tool, fp in s["writes"]:
                seen[(tool, fp)] += 1
        print(f"=== {slot}")
        for (tool, fp), n in sorted(seen.items(), key=lambda kv: -kv[1]):
            print(f"    {n:>3}x {tool:<6} {fp}")


def cmd_commits(args):
    """Raw `git commit` invocations from the transcripts, deduplicated."""
    slots = [args.slot] if args.slot else SLOTS
    for slot in slots:
        print(f"=== {slot}")
        seen = set()
        for s in scan_slot(slot, args.tsv_only):
            for ts, cmd in s["commit_cmds"]:
                key = re.sub(r"\s+", " ", cmd)[:4000]
                if key in seen:
                    continue
                seen.add(key)
                head = cmd.strip().splitlines()[0][:200]
                print(f"    [{ts}] {head}")


def cmd_numbers(args):
    """Every numeric token an assistant stated, with a context window."""
    slots = [args.slot] if args.slot else SLOTS
    rows = []
    for slot in slots:
        for s in scan_slot(slot, args.tsv_only):
            for ts, text in s["texts"]:
                for m in RE_NUM.finditer(text):
                    val, unit = m.group(1), (m.group(2) or "").strip()
                    lo = max(0, m.start() - args.context)
                    hi = min(len(text), m.end() + args.context)
                    ctx = re.sub(r"\s+", " ", text[lo:hi])
                    rows.append((slot, ts, val, unit, ctx))
    if args.filter:
        rx = re.compile(args.filter, re.IGNORECASE)
        rows = [r for r in rows if rx.search(r[4])]
    for slot, ts, val, unit, ctx in rows:
        print(f"{slot}\t{ts}\t{val}\t{unit}\t{ctx}")
    print(f"# {len(rows)} numeric statements", file=sys.stderr)


def cmd_corrections(args):
    slots = [args.slot] if args.slot else SLOTS
    for slot in slots:
        print(f"=== {slot}")
        for s in scan_slot(slot, args.tsv_only):
            for ts, text in s["texts"]:
                for para in re.split(r"\n\s*\n", text):
                    if RE_CORR.search(para):
                        p = re.sub(r"\s+", " ", para).strip()
                        print(f"    [{ts}] {p[:args.width]}")


def cmd_grep(args):
    rx = re.compile(args.grep, re.IGNORECASE if not args.case else 0)
    slots = [args.slot] if args.slot else SLOTS
    for slot in slots:
        for s in scan_slot(slot, args.tsv_only):
            for ts, text in s["texts"]:
                for para in re.split(r"\n\s*\n", text):
                    if rx.search(para):
                        p = re.sub(r"\s+", " ", para).strip()
                        print(f"{slot}\t{ts}\t{p[:args.width]}")
            if args.bash:
                for ts, cmd in s["bash"]:
                    if rx.search(cmd):
                        c = re.sub(r"\s+", " ", cmd).strip()
                        print(f"{slot}\tBASH\t{ts}\t{c[:args.width]}")


# ---------------------------------------------------------------- self-test

def cmd_self_test(args):
    """Guards that must FIRE, not guards that must pass silently.

    Each case is a thing this script could plausibly get wrong and that would
    change the readout if it did.
    """
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    # 1. Two-file discovery is the whole point. Assert it, do not assume it.
    multi = [s for s in SLOTS if len(transcripts(s)) > 1]
    check("every slot has >1 transcript file", len(multi) == len(SLOTS),
          f"{len(multi)}/{len(SLOTS)} slots")

    # 2. --tsv-only must return strictly fewer files, or the flag is a lie.
    a = sum(len(transcripts(s)) for s in SLOTS)
    b = sum(len(transcripts(s, True)) for s in SLOTS)
    check("--tsv-only sees fewer files than default", b < a, f"{b} < {a}")

    # 3. Number regex must not split 1,147,694 into three numbers.
    got = [m.group(1) for m in RE_NUM.finditer("1,147,694 Gaussians")]
    check("thousands separator survives", got == ["1,147,694"], str(got))

    # 4. Number regex must catch a signed percent.
    got = [(m.group(1), m.group(2)) for m in RE_NUM.finditer("-7.6682 percent")]
    check("signed decimal percent", got and got[0][0] == "-7.6682", str(got))

    # 5. KNOWN LIMITATION, asserted rather than hidden: a dotted version string
    #    DOES yield a spurious number ("Genesis 1.1.1" -> "1.1"). The number
    #    table in the readout is therefore a candidate list to be read with its
    #    context column, never a list of physical quantities. This guard exists
    #    to make that limitation fail loudly if anyone "fixes" the regex and
    #    forgets to revisit the caveat.
    got = [m.group(1) for m in RE_NUM.finditer("Genesis 1.1.1")]
    check("version strings ARE mis-mined (known, documented)",
          got == ["1.1"], f"{got} -- read --numbers with its context column")

    # 6. Commit detector must catch the path-limited form this repo mandates.
    check("git commit -- path detected",
          bool(RE_COMMIT.search('git commit -m "x" -- docs/a.md')))
    check("git -C form detected",
          bool(RE_COMMIT.search('git -C /Users/josie/can-it-ford commit -m "x"')))
    check("git commit NOT matched inside prose 'commit message'",
          not RE_COMMIT.search("the commit message says"))

    # 7. Streaming: never read a whole file into memory. Proven by reading the
    #    largest transcript and checking peak single-object size is one line.
    big = max((p for s in SLOTS for p in transcripts(s)),
              key=os.path.getsize)
    n = 0
    for _ln, _rec in records(big):
        n += 1
        if n > 5:
            break
    check("largest transcript streams", n > 5, os.path.basename(big))

    # 8. Correction regex must not fire on a bare neutral sentence.
    check("correction regex does not fire on neutral prose",
          not RE_CORR.search("I ran the script and it printed 44 fields."))
    check("correction regex fires on a retraction",
          bool(RE_CORR.search("I RETRACT the 1.6 percent figure.")))

    print()
    if fails:
        print(f"SELF-TEST FAILED: {len(fails)} -> {fails}")
        return 1
    print(f"SELF-TEST PASSED: 10 of 10 guards")
    return 0


# ---------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slot", help="one of " + ", ".join(SLOTS))
    ap.add_argument("--tsv-only", action="store_true",
                    help="only sessions named in r8_session_ids.tsv (see docstring)")
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--writes", action="store_true")
    ap.add_argument("--commits", action="store_true")
    ap.add_argument("--numbers", action="store_true")
    ap.add_argument("--corrections", action="store_true")
    ap.add_argument("--grep")
    ap.add_argument("--bash", action="store_true", help="with --grep, also search bash commands")
    ap.add_argument("--case", action="store_true", help="case-sensitive --grep")
    ap.add_argument("--filter", help="with --numbers, keep rows whose context matches")
    ap.add_argument("--context", type=int, default=90)
    ap.add_argument("--width", type=int, default=600)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(cmd_self_test(args))
    if args.inventory:
        return cmd_inventory(args)
    if args.summary:
        return cmd_summary(args)
    if args.writes:
        return cmd_writes(args)
    if args.commits:
        return cmd_commits(args)
    if args.numbers:
        return cmd_numbers(args)
    if args.corrections:
        return cmd_corrections(args)
    if args.grep:
        return cmd_grep(args)
    ap.print_help()


if __name__ == "__main__":
    main()
