#!/bin/bash
cat >/dev/null 2>&1

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)
fi
[ -n "$PROJECT_DIR" ] || exit 0

CHECK="$PROJECT_DIR/.claude/checks/register_integrity.py"
[ -f "$CHECK" ] || exit 0

LOGDIR="$HOME/.pane_signals"
mkdir -p "$LOGDIR" 2>/dev/null || exit 0
LOG="$LOGDIR/register_integrity.log"

OUT=$(python3 "$CHECK" --quiet 2>&1)
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  printf '=== %s\n' "$STAMP"
  printf '%s\n' "$OUT"
} >> "$LOG" 2>/dev/null

BLOCKS=$(printf '%s\n' "$OUT" | /usr/bin/grep -c '^BLOCK' 2>/dev/null)
case "$BLOCKS" in
  ''|*[!0-9]*) BLOCKS=0 ;;
esac

if [ "$BLOCKS" -gt 0 ]; then
  printf 'register_integrity: %s BLOCK finding(s) in the corrections register, see %s\n' "$BLOCKS" "$LOG" >&2
fi

exit 0
