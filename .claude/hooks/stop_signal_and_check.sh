#!/bin/bash
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null)
[ -z "$CWD" ] && CWD=$(pwd)

SIGNAL_DIR=~/.pane_signals
mkdir -p "$SIGNAL_DIR" 2>/dev/null
SAFE_NAME=$(echo "$CWD" | sed 's#[/ ]#_#g')
echo "$(date -u +%s)" > "$SIGNAL_DIR/${SAFE_NAME}_done" 2>/dev/null

RECENT=$(find "$CWD" -maxdepth 3 -name '*.md' -newermt '-2 hours' 2>/dev/null | grep -v -i 'CLAUDE.md\|README.md\|SESSION_STATE.md\|CONFIRMED_FACTS_LEDGER.md')

MISSING=""
for f in $RECENT; do
  if grep -q '^## VERIFIED' "$f" 2>/dev/null; then
    HAS_ALL=1
    for section in UNVERIFIED "CLAIMS I ALMOST MADE" "WALLS HIT" "ACTION REQUIRED FROM JOSIE" "STALE RECORDS FOUND"; do
      grep -q "## $section" "$f" 2>/dev/null || HAS_ALL=0
    done
    [ "$HAS_ALL" = "0" ] && MISSING="$MISSING $f"
  fi
done

if [ -n "$MISSING" ]; then
  LOGFILE=~/.pane_signals/incomplete_deliverables.log
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $CWD partial six-section format:$MISSING" >> "$LOGFILE"
fi

exit 0
