#!/usr/bin/env python3
"""Deny `find` over a large tree when it carries no -maxdepth bound.

WHY. An unbounded `find` rooted at /, at $HOME or at this repo walks hundreds of
thousands of inodes, and in this project the repo alone is about 407 MB over 849
files with 15 live worktrees under .claude/worktrees/. The cost is not the only
problem: the output is long enough to crowd out the answer it was run to get.
A -maxdepth bound is almost always the intended search anyway.

SCOPE, DELIBERATELY NARROW. Only Bash. Only a real `find` token, so `findutils`,
`grep find` and a path ending in /find do not match. Only when a resolved search
root is one of the known-large roots below; a bounded search under a small
project directory is none of this hook's business and is allowed untouched.

FALSE POSITIVES ARE THE KNOWN FAILURE MODE, so heredoc bodies are stripped first
via _strip_heredoc.py, exactly as gate_concurrent_write.sh does. Writing a file
whose text merely mentions an unbounded find must not be blocked; that class of
false positive was measured twice in ten minutes on 2026-08-20 against the other
two gates.

FAILS OPEN. Any unexpected exception exits 0 with a note on stderr, so a bug in
this guard can never take the session down with it. Reference: PreToolUse honours
a hookSpecificOutput decision on exit 0, which is the form the other gates in
this repo already use.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Roots big enough that an unbounded walk is never what was wanted.
LARGE_ROOTS = {
    "/", "/Users", "/System", "/Library", "/Applications",
    "/private", "/Volumes", "/opt", "/usr",
}
HOME = os.path.expanduser("~")
LARGE_ROOTS.add(HOME)


def _strip(payload_text, raw_cmd):
    try:
        from _strip_heredoc import strip_heredocs
        return strip_heredocs(raw_cmd)
    except Exception:
        # Fails toward the guard: an unstripped command can only over-match,
        # which a human sees, never silently under-match.
        return raw_cmd


def _tokens(cmd):
    try:
        import shlex
        return shlex.split(cmd, posix=True)
    except Exception:
        return cmd.split()


def _is_find(tok):
    return tok == "find" or tok.endswith("/find")


# Wrappers that may legitimately precede the `find` program name.
PREFIXES = {"sudo", "time", "nice", "command", "env", "xargs", "nohup", "stdbuf"}


def _find_cmd_index(seg):
    """Index of `find` only when it is the COMMAND WORD of the segment.

    `grep -r find /` must NOT match: there `find` is a search pattern and the
    program is grep, so denying it would be a pure false positive. Only leading
    environment assignments and the wrappers above may precede the program name.
    """
    i = 0
    while i < len(seg):
        t = seg[i]
        if _is_find(t):
            return i
        if t in PREFIXES:
            i += 1
            continue
        if "=" in t and not t.startswith("-") and t.split("=", 1)[0].isidentifier():
            i += 1
            continue
        return None
    return None


def _segments(tokens):
    """Split on shell separators so `ls && find /` is seen as its own command."""
    seps = {"&&", "||", "|", ";", "&", "(", ")", "{", "}"}
    out, cur = [], []
    for t in tokens:
        if t in seps:
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append(cur)
    return out


def offending_roots(cmd, cwd):
    """Return the large roots an unbounded find in `cmd` would walk."""
    hits = []
    for seg in _segments(_tokens(cmd)):
        idx = _find_cmd_index(seg)
        if idx is None:
            continue
        args = seg[idx + 1:]
        # An explicit depth bound of any kind is enough; so is -prune.
        if any(a in ("-maxdepth", "-depth", "-prune") for a in args):
            continue
        # Path operands are the leading args before the first predicate.
        paths = []
        for a in args:
            if a.startswith("-") or a in ("!", "(", ")"):
                break
            paths.append(a)
        if not paths:
            paths = ["."]
        for p in paths:
            try:
                r = os.path.realpath(os.path.join(cwd, os.path.expanduser(p)))
            except Exception:
                continue
            if r in LARGE_ROOTS:
                hits.append(r)
    return hits


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except Exception:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd or "find" not in cmd:
        return 0
    cwd = payload.get("cwd") or os.getcwd()
    roots = offending_roots(_strip(raw, cmd), cwd)
    if not roots:
        return 0
    where = ", ".join(sorted(set(roots)))
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Unbounded `find` over a large tree (%s). Walking that root costs "
            "minutes and buries the answer in output. Add a bound and re-run, "
            "for example: find %s -maxdepth 3 -name '<pattern>' 2>/dev/null "
            "|| true. If you genuinely need the whole tree, say so and narrow "
            "by -name or -type first." % (where, sorted(set(roots))[0])
        )}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never take the session down
        sys.stderr.write("gate_find_maxdepth: failing open: %r\n" % (exc,))
        sys.exit(0)
