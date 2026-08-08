import json
import os
import subprocess
import sys

# Resolve every path against the project root, never against the shell's cwd.
# The Bash tool keeps one persistent cwd across a session, so a single call that
# left the repo (cd /tmp) used to make this hook die on its own relative path and
# wedge EVERY subsequent Bash call for the rest of the session. Observed live
# 2026-08-07. Same bug applied to the params_check.py path on line 9.
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
CHECK = os.path.join(ROOT, ".claude", "checks", "params_check.py")

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

if "git" in command and "commit" in command:
    if not os.path.exists(CHECK):
        sys.stderr.write(f"params_check.py not found at {CHECK}, refusing to pass the gate\n")
        sys.exit(2)
    result = subprocess.run([sys.executable, CHECK], cwd=ROOT)
    if result.returncode != 0:
        sys.stderr.write("params_check.py FAILED, fix the flagged issues before committing\n")
        sys.exit(2)

sys.exit(0)
