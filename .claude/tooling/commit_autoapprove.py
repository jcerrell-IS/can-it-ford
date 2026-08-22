#!/usr/bin/env python3
"""PreToolUse hook: auto-approve provably-safe git commits, prompt otherwise.

WHY. On 2026-08-14 a 13-session fleet produced roughly 25 commit confirmation
prompts in one evening. Each blocked one session for minutes; several sat idle
at a Yes/No prompt for 15+ minutes. That was the single largest source of lost
session time in the run, and every one of those 25 was ultimately approved.

This hook NEVER blocks. It only GRANTS, and only when every condition below
holds. Anything it cannot prove safe falls through to the normal prompt, and
the existing pretooluse_git_commit_gate.py (params_check) still runs.

The predicate cannot get bored, which is the whole point: a human clicking Yes
25 times is strictly less safe than a rule that checks all five conditions
every time.

CONDITIONS, all required:
  1. path-limited form: `git commit ... -- <paths>` present
  2. no blanket staging anywhere in the command (-a, --all, add -A, add .)
  3. <= 8 paths  (matches .git/hooks/pre-commit, which refuses more)
  4. no path matching the risky-extension/credential pattern
  5. nothing staged in the index that the command does not name
     -> this is the 2026-08-07 breach guard: a bare commit sweeping another
        session's already-staged entries. See memory: shared-index-sweeps-plain-commit.
"""
import json
import os
import re
import shlex
import subprocess
import sys

MAX_PATHS = 8
RISKY = re.compile(
    r"\.(ply|obj|stl|npz|npy|env|key|pem|pth|p12|pfx)$"
    r"|secret|token|credential|id_rsa|\.netrc",
    re.I,
)
BLANKET = re.compile(r"(?:^|\s)(?:-a\b|--all\b)|git\s+add\s+(?:-A\b|\.(?:\s|$))")

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def fall_through(_reason=""):
    """Emit nothing; Claude Code proceeds to its normal confirmation."""
    sys.exit(0)


def approve(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "commit-autoapprove: " + reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        fall_through()
    cmd = (payload.get("tool_input") or {}).get("command", "") or ""

    if "git" not in cmd or "commit" not in cmd:
        fall_through()

    # 2. blanket staging anywhere in the command line
    if BLANKET.search(cmd):
        fall_through("blanket staging present")

    # 1. path-limited form. Take the LAST `--` separated segment of the
    #    git commit invocation.
    try:
        toks = shlex.split(cmd)
    except ValueError:
        fall_through("unparseable")
    if "--" not in toks:
        fall_through("not path-limited")
    paths = toks[len(toks) - 1 - toks[::-1].index("--"):][1:]
    paths = [p for p in paths if not p.startswith("-")]
    if not paths:
        fall_through("no explicit paths after --")

    # 3. count
    if len(paths) > MAX_PATHS:
        fall_through("%d paths exceeds pre-commit limit" % len(paths))

    # 4. risky content
    for p in paths:
        if RISKY.search(p):
            fall_through("risky path: %s" % p)

    # 5. index must contain nothing the command does not name.
    #    Column 1 of porcelain v1 is the INDEX state.
    cwd = (payload.get("cwd") or ROOT)
    try:
        r = subprocess.run(["git", "-C", cwd, "status", "--porcelain=v1"],
                           capture_output=True, text=True, timeout=20)
    except Exception:
        fall_through("git status failed")
    if r.returncode != 0:
        fall_through("git status rc=%d" % r.returncode)

    named = set(os.path.normpath(p) for p in paths)
    staged_foreign = []
    for ln in r.stdout.splitlines():
        if len(ln) < 4:
            continue
        index_state = ln[0]
        path = ln[3:].strip().strip('"')
        if " -> " in path:                      # rename
            path = path.split(" -> ", 1)[1]
        if index_state not in (" ", "?"):       # something is STAGED
            if os.path.normpath(path) not in named:
                staged_foreign.append(path)
    if staged_foreign:
        fall_through("index holds unnamed staged paths: %s"
                     % ", ".join(staged_foreign[:4]))

    approve("path-limited, %d file(s), no risky paths, index clean of "
            "unnamed entries" % len(paths))


if __name__ == "__main__":
    main()
