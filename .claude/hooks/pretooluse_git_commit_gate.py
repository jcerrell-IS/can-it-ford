import json
import subprocess
import sys

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

if "git" in command and "commit" in command:
    result = subprocess.run(["python3", ".claude/checks/params_check.py"])
    if result.returncode != 0:
        sys.stderr.write("params_check.py FAILED, fix the flagged issues before committing\n")
        sys.exit(2)

sys.exit(0)
