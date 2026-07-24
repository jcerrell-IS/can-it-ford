#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))")
case "$CMD" in
  *"git push --force"*|*"filter-repo"*)
    echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Force-push or history rewrite. Get explicit go in chat first."}}'
    ;;
  *"git push"*)
    echo '{"hookSpecificOutput":{"permissionDecision":"ask","permissionDecisionReason":"Rule 16: push needs explicit confirmation, every time."}}'
    ;;
  *"rm -rf"*|*"rm -r "*)
    echo '{"hookSpecificOutput":{"permissionDecision":"ask","permissionDecisionReason":"Recursive delete. Confirm the target path first."}}'
    ;;
  *)
    exit 0
    ;;
esac
exit 0
