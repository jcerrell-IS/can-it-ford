#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")
TOOL=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_name',''))")

case "$FILE" in
  *DEPRECATED*|*SUPERSEDED*|*.OLD-*|*_OLD_*)
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Marked deprecated. Use the canonical file instead, see CLAUDE.md."}}'
    exit 0
    ;;
esac

if [ "$TOOL" = "Edit" ] || [ "$TOOL" = "Write" ]; then
  case "$FILE" in
    */CLAUDE.md|*/SESSION_STATE.md|*/README.md|CLAUDE.md|SESSION_STATE.md|README.md)
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Shared coordination file, multiple panes read this. Confirm before editing."}}'
      ;;
    *)
      exit 0
      ;;
  esac
fi
exit 0
