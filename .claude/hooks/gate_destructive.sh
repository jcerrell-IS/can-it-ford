#!/bin/bash
# PreToolUse gate on genuinely destructive git and filesystem commands.
#
# INSPECTS THE COMMAND WITH HEREDOC BODIES REMOVED. tool_input.command already was
# the right field, but a heredoc carries the file's CONTENT inside the command
# string, so writing a file that merely MENTIONS a dangerous command was
# indistinguishable from running one. That produced two false denials on
# 2026-08-20 within ten minutes, both blocking real work. See _strip_heredoc.py.
#
# FAILS OPEN. If the helper is missing or errors, fall back to the raw command
# rather than exiting non-zero: a PreToolUse hook that crashes blocks the tool
# call, which is how a guardrail bug becomes a hard stop on unrelated work.
INPUT=$(cat)
HELPER="$(dirname "$0")/_strip_heredoc.py"
CMD=""
if [ -f "$HELPER" ]; then
  CMD=$(printf '%s' "$INPUT" | python3 "$HELPER" 2>/dev/null)
fi
if [ -z "$CMD" ]; then
  CMD=$(printf '%s' "$INPUT" | python3 -c "import json,sys
try: print(json.load(sys.stdin).get('tool_input',{}).get('command',''))
except Exception: print('')" 2>/dev/null)
fi

case "$CMD" in
  *"git push --force"*|*"filter-repo"*)
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Force-push or history rewrite. Get explicit go in chat first."}}'
    ;;
  *"git push"*)
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Rule 16: push needs explicit confirmation, every time."}}'
    ;;
  *"git commit"*)
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Any commit needs explicit confirmation before it runs, same as push."}}'
    ;;
  *"rm -rf"*|*"rm -r "*)
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Recursive delete. Confirm the target path first."}}'
    ;;
  *)
    exit 0
    ;;
esac
exit 0
