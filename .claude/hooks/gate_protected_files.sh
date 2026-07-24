#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")
case "$FILE" in
  */CLAUDE.md|*/SESSION_STATE.md|*/README.md)
    echo '{"hookSpecificOutput":{"permissionDecision":"ask","permissionDecisionReason":"Shared coordination file, multiple panes read this. Confirm before editing."}}'
    ;;
  *DEPRECATED*|*SUPERSEDED*|*.OLD-*|*_OLD_*)
    echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Marked deprecated. Use the canonical file instead, see CLAUDE.md."}}'
    ;;
  *)
    exit 0
    ;;
esac
exit 0
