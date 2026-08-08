#!/bin/bash
# gate_concurrent_write.sh
#
# Two guards that the existing hooks do not cover.
#
# 1. BULK STAGING. CLAUDE.md forbids `git add -A`, `git add .` and `git commit -a`
#    in this repo, because the working tree is shared by several live Claude Code
#    sessions and a bulk stage captures another session's in-progress edits and
#    commits them unreviewed. This is not hypothetical: it happened on 2026-08-07
#    (commits 0797b08 and 3470ff9). gate_destructive.sh gates `git push`,
#    `git commit` and `rm -r`, but it never looks at `git add`, so the exact
#    command that caused the breach was ungated. This closes that.
#
# 2. FILE CLAIMS. Before an Edit or Write, record which session touched which
#    path. If a different session claimed the same path recently, ask instead of
#    silently writing over an edit that is still in flight somewhere else.
#
# Claims live under .claude/state/locks/, which .gitignore already excludes.
# They are advisory and TTL-based: this is a collision warning, not a mutex.
#
# Wire with matcher "Bash" and matcher "Edit|Write" under PreToolUse.

INPUT=$(cat)

TOOL=$(printf '%s' "$INPUT" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("tool_name",""))' 2>/dev/null)
SESSION=$(printf '%s' "$INPUT" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("session_id","") or "unknown")' 2>/dev/null)
FILE=$(printf '%s' "$INPUT" | python3 -c 'import json,sys;print((json.load(sys.stdin).get("tool_input",{}) or {}).get("file_path",""))' 2>/dev/null)
CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys;print((json.load(sys.stdin).get("tool_input",{}) or {}).get("command",""))' 2>/dev/null)

deny() {
  python3 -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": sys.argv[1]}}))' "$1"
  exit 0
}

ask() {
  python3 -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": sys.argv[1]}}))' "$1"
  exit 0
}

# ---- guard 1: bulk staging -------------------------------------------------
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ]; then
  # Normalise so `git   add   -A` and `git -C . add -A` still match.
  NORM=$(printf '%s' "$CMD" | tr '\n' ' ' | tr -s ' ')
  case "$NORM" in
    *"git add -A"*|*"git add --all"*|*"git add ."*|*"git add -a"*|\
    *"git add"*" -A"*|*"git add"*" --all"*|\
    *"git commit -a"*|*"git commit --all"*|*"git commit -am"*)
      deny "Bulk staging is forbidden in this repo (CLAUDE.md standing rule). The working tree is shared by several live Claude Code sessions, so 'git add -A', 'git add .' and 'git commit -a' capture another session's uncommitted work and commit it unreviewed under your message. This already happened on 2026-08-07 in 0797b08 and 3470ff9. Stage explicit paths instead: git add -- <path> ... then git commit -F <msgfile> -- <path> ..."
      ;;
  esac
  exit 0
fi

# ---- guard 2: cross-session file claims ------------------------------------
[ "$TOOL" = "Edit" ] || [ "$TOOL" = "Write" ] || exit 0
[ -n "$FILE" ] || exit 0

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0
LOCKDIR="$ROOT/.claude/state/locks"
mkdir -p "$LOCKDIR" 2>/dev/null || exit 0

TTL=1800   # 30 min; older claims are treated as finished work, not a live edit
NOW=$(date -u +%s)
KEY=$(printf '%s' "$FILE" | shasum | cut -c1-40)
LOCK="$LOCKDIR/$KEY"

if [ -f "$LOCK" ]; then
  OWNER=$(cut -d'|' -f1 "$LOCK" 2>/dev/null)
  WHEN=$(cut -d'|' -f2 "$LOCK" 2>/dev/null)
  case "$WHEN" in ''|*[!0-9]*) WHEN=0 ;; esac
  AGE=$((NOW - WHEN))
  if [ -n "$OWNER" ] && [ "$OWNER" != "$SESSION" ] && [ "$AGE" -lt "$TTL" ]; then
    # refresh so repeated prompts do not stack up, then ask once
    printf '%s|%s|%s\n' "$SESSION" "$NOW" "$FILE" > "$LOCK" 2>/dev/null
    ask "Another Claude Code session (id ${OWNER%%-*}...) wrote $(basename "$FILE") $((AGE / 60))m ${AGE}s ago and $(ls /proc 2>/dev/null >/dev/null; pgrep -x claude 2>/dev/null | wc -l | tr -d ' ') claude processes are live in this tree. Per CLAUDE.md, if edits appear in a file you did not write, assume ANOTHER SESSION, not a linter and not the user. Re-read the file before overwriting, and confirm this edit is not clobbering work still in flight."
  fi
fi

printf '%s|%s|%s\n' "$SESSION" "$NOW" "$FILE" > "$LOCK" 2>/dev/null
exit 0
