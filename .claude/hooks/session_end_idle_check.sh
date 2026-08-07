#!/bin/bash
# ============================================================================
# session_end_idle_check.sh  SessionEnd guard against walking away from a
#                            live interactive allocation.
#
# WHY
#   80 of 164 interactive Vista jobs since 2026-07-01 ended in TIMEOUT, meaning
#   they ran to the wall limit with nobody attached, and they account for 99.1%
#   of all node-time against 0.9% for every gated run. The moment that happens
#   is exactly this one: the session ends and the job keeps billing.
#
#   Reads the status-line cache rather than opening an ssh connection, so
#   quitting is never slowed down or blocked by the network. A stale cache says
#   so instead of guessing.
# ============================================================================
set -uo pipefail

CACHE="$HOME/.cache/canitford/tacc_status"
[ -f "$CACHE" ] || exit 0

now=$(date +%s)
mt=$(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null || echo 0)
age=$((now - mt))

idle_total=0
while IFS=: read -r host su jobs idle; do
    [ -n "${host:-}" ] || continue
    idle_total=$((idle_total + ${idle:-0}))
done < "$CACHE"

[ "$idle_total" -gt 0 ] || exit 0

echo
echo "  ============================================================"
echo "  ${idle_total} interactive TACC allocation(s) still running."
if [ "$age" -gt 900 ]; then
    echo "  (cache is ${age}s old, so confirm before acting on it)"
fi
while IFS=: read -r host su jobs idle; do
    [ "${idle:-0}" -gt 0 ] && echo "    ${host}: ${idle} idev/holder job(s), ${su} SUs left"
done < "$CACHE"
echo
echo "  These bill whether or not anything is attached. Check and reclaim:"
echo "    scripts/tacc_idle_check.sh"
echo "    scripts/tacc.sh vista 'scancel <jobid>'"
echo "  ============================================================"
exit 0
