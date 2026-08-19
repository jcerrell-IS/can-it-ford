#!/usr/bin/env python3
"""Read a PreToolUse hook payload on stdin, print the Bash command with heredoc
BODIES removed.

WHY THIS EXISTS. The gates already read tool_input.command, which is the correct
field, so the usual advice to "inspect the command not the content" was already
followed. The defect is subtler: a heredoc puts the FILE'S CONTENT INSIDE the
command string. Writing a file whose text merely mentions a dangerous command is
therefore indistinguishable, to a substring match, from running one.

Measured 2026-08-20, twice in ten minutes, both false positives that blocked real
work: a heredoc writing a dispatch containing the words for a history rewrite was
denied by gate_destructive.sh, and a heredoc writing a session prompt containing
the bulk-staging string was denied by gate_concurrent_write.sh. Neither command
ran anything of the kind.

Stripping the body keeps the guard's teeth on the part of the line that is
actually executed, which is what the gate was always meant to inspect.

FAILS TOWARD THE GUARD, NOT AWAY FROM IT. On any parse problem this prints the
raw command unchanged, so a bug here can only cause a false positive that a human
sees, never a silent miss of a real destructive command.
"""
import json
import re
import sys


def strip_heredocs(cmd: str) -> str:
    # <<EOF, <<-EOF, <<'EOF', <<"EOF"
    marker_re = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
    lines = cmd.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        markers = [m.group(2) for m in marker_re.finditer(line)]
        i += 1
        for marker in markers:
            # Consume the body up to and including the terminator line.
            while i < len(lines) and lines[i].strip() != marker:
                i += 1
            if i < len(lines):
                i += 1  # drop the terminator itself
    return "\n".join(out)


def main() -> int:
    raw = sys.stdin.read()
    try:
        cmd = json.loads(raw).get("tool_input", {}).get("command", "")
    except Exception:
        print("")
        return 0
    try:
        print(strip_heredocs(cmd))
    except Exception:
        print(cmd)  # never weaken the guard because the stripper broke
    return 0


if __name__ == "__main__":
    sys.exit(main())
