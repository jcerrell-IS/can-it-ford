#!/bin/bash
# Rolling audit signal: emit an event when a slot COMMITS SOMETHING I HAVE NOT
# RESPONDED TO, and keep emitting a debt line while that stays true.
#
# WHY THIS AND NOT THE EXISTING IDLE DETECTOR. r8_watch.py resolves a slot's
# transcript through the session-id TSV, and for five slots that file is the
# PRE-CRASH one: d11, d12, d15, d16 and d18 all report an IDENTICAL age of
# 26311 s, which is the 2026-08-18 23:22 crash, not their real state. d11 in
# particular reports idle for seven hours while having committed at 00:06. An
# identical age across five independent sessions is the tell. So this watcher
# uses two signals that are always current instead: the branch tip, and the
# send log.
#
# WHAT IT MEASURES. Follow-up debt per slot: commits landed on that slot's
# branch since the last dispatch I sent to it. A slot with debt has produced
# auditable output that the coordinator has not read or answered. That is the
# quantity the coordination layer was missing; commit events alone say work
# happened, not that anyone owes a reply.
set -uo pipefail
REPO=/Users/josie/can-it-ford
PLAN="$REPO/scripts/r8/r8_plan.tsv"
LOG="$REPO/.claude/state/r8_send_log.md"
STATE=/private/tmp/claude-501/-Users-josie-can-it-ford/r9_debt
mkdir -p "$STATE" || exit 1

# Slot -> branch, read by column NAME. Never by position: appending a column to
# the plan silently broke a positional read tonight.
slots() {
  awk -F'\t' '
    NR==1 { for (i=1;i<=NF;i++){ if($i=="slot")s=i; if($i=="branch")b=i } ; next }
    $1 ~ /^d(1[1-9]|2[0-9])-/ { print $s "\t" $b }' "$PLAN"
}

# Timestamp of the last dispatch sent to a slot, from the send log itself, so
# the debt is measured against what was actually delivered rather than what I
# believe I sent.
last_sent_epoch() {
  local slot="$1" ts
  ts=$(/usr/bin/grep -aE "^## .*$slot" "$LOG" 2>/dev/null | tail -1 |
       /usr/bin/grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}' | tail -1)
  [ -z "$ts" ] && { echo 0; return; }
  python3 - "$ts" <<'PY' 2>/dev/null || echo 0
import sys, datetime
t = sys.argv[1].replace("T", " ")
try:
    print(int(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M").timestamp()))
except Exception:
    print(0)
PY
}

while true; do
  while IFS=$'\t' read -r slot branch; do
    [ -z "${slot:-}" ] && continue
    tip=$(git -C "$REPO" rev-parse --short "$branch" 2>/dev/null) || continue
    f="$STATE/$slot"
    seen=""; [ -f "$f" ] && seen=$(cat "$f")
    [ "$tip" = "$seen" ] && continue

    sent=$(last_sent_epoch "$slot")
    # Commits on this branch newer than the last dispatch to this slot.
    if [ "$sent" -gt 0 ]; then
      n=$(git -C "$REPO" rev-list --count --since="@$sent" "$branch" 2>/dev/null)
    else
      n="?"
    fi
    subj=$(git -C "$REPO" log -1 --format='%s' "$branch" 2>/dev/null | cut -c1-88)
    files=$(git -C "$REPO" show --stat --format='' "$branch" 2>/dev/null |
            /usr/bin/grep -cE '\|' )
    # A commit that adds a check but names no failing input is the pattern this
    # project keeps rediscovering, so flag it in the event rather than later.
    body=$(git -C "$REPO" log -1 --format='%B' "$branch" 2>/dev/null)
    flag=""
    if printf '%s' "$body" | /usr/bin/grep -qiE "check|guard|gate|assert"; then
      printf '%s' "$body" | /usr/bin/grep -qiE "falsif|failing input|makes .* fail" \
        || flag=" [CHECK-WITHOUT-FALSIFIER]"
    fi
    echo "DEBT ${slot%%-*}/${slot#*-} $tip owed=$n files=$files$flag :: $subj"
    echo "$tip" > "$f"
  done < <(slots)
  sleep 90
done
