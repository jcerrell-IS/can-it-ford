#!/bin/bash
# ============================================================================
# statusline.sh  keep the binding constraint on screen.
#
# WHY
#   Vista had 673 SUs left on 2026-08-07, expiring 2026-09-30, and 99.1% of all
#   node-time since July went to interactive sessions nobody was attached to.
#   That is a budget problem you cannot see from the prompt, so it kept being
#   rediscovered after the fact. This puts SUs and live job count in front of
#   every turn.
#
# WHY IT READS A CACHE
#   The status line re-renders constantly. An ssh round trip per render would
#   make the UI crawl and hammer the login node. This reads a cache file and, if
#   the cache is older than TTL, kicks off ONE detached refresh and keeps going.
#   It never blocks, and it never leaves the prompt waiting on the network.
#
# stdin: Claude Code status line JSON. stdout: one line.
# ============================================================================
set -uo pipefail

CACHE_DIR="$HOME/.cache/canitford"
CACHE="$CACHE_DIR/tacc_status"
LOCK="$CACHE_DIR/tacc_status.lock"
TTL=600           # seconds before the cache is considered stale
mkdir -p "$CACHE_DIR" 2>/dev/null

INPUT="$(cat)"

# Tab-delimited, because display_name contains a space ("Opus 5") and default
# word-splitting silently shifts every field after it.
IFS=$'\t' read -r MODEL CTX BRANCH <<<"$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("?\t0\t-"); raise SystemExit
m = (d.get("model") or {}).get("display_name") or "?"
cw = d.get("context_window") or {}
pct = cw.get("used_percentage")
w = d.get("workspace") or {}
br = w.get("git_worktree") or "-"
print(f"{m}\t{int(pct) if pct is not None else 0}\t{br}")
' 2>/dev/null)"
MODEL="${MODEL:-?}"; CTX="${CTX:-0}"; BRANCH="${BRANCH:--}"

# --- refresh the cache in the background if stale -------------------------
refresh_needed=1
if [ -f "$CACHE" ]; then
    now=$(date +%s)
    mt=$(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null || echo 0)
    [ $((now - mt)) -lt "$TTL" ] && refresh_needed=0
fi
if [ "$refresh_needed" -eq 1 ] && mkdir "$LOCK" 2>/dev/null; then
    (
        TACC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/tacc.sh"
        out=""
        for h in vista ls6; do
            su=$("$TACC" "$h" '/usr/local/etc/taccinfo 2>/dev/null | awk "/BCS20003/{print \$3}"' 2>/dev/null | tr -dc '0-9')
            jobs=$("$TACC" "$h" 'squeue -u $USER -h -o "%j" | wc -l' 2>/dev/null | tr -dc '0-9')
            idle=$("$TACC" "$h" 'squeue -u $USER -h -o "%j" | grep -cE "^(idv|holder)" || true' 2>/dev/null | tr -dc '0-9')
            out="${out}${h}:${su:-?}:${jobs:-0}:${idle:-0}"$'\n'
        done
        printf '%s' "$out" > "$CACHE".tmp && mv "$CACHE".tmp "$CACHE"
        rmdir "$LOCK" 2>/dev/null
    ) >/dev/null 2>&1 &
    disown 2>/dev/null || true
fi

# --- render ---------------------------------------------------------------
R=$'\033[0m'; DIM=$'\033[2m'; RED=$'\033[31m'; YEL=$'\033[33m'; GRN=$'\033[32m'; CYA=$'\033[36m'

TACC_SEG="${DIM}tacc ?${R}"
if [ -f "$CACHE" ]; then
    vsu=$(awk -F: '/^vista/{print $2}' "$CACHE"); vjb=$(awk -F: '/^vista/{print $3}' "$CACHE")
    vidle=$(awk -F: '/^vista/{print $4}' "$CACHE")
    if [ -n "${vsu:-}" ]; then
        # 673 SUs on 2026-08-07 and every gated run costs 1-4 minutes, so the
        # red band is about the allocation ending, not about a single job.
        if   [ "$vsu" -lt 300 ];  then c="$RED"
        elif [ "$vsu" -lt 1000 ]; then c="$YEL"
        else c="$GRN"; fi
        TACC_SEG="${c}vista ${vsu} SU${R}"
        [ "${vjb:-0}" -gt 0 ] && TACC_SEG="${TACC_SEG} ${DIM}${vjb}job${R}"
        # An idle interactive allocation is the specific failure mode here.
        [ "${vidle:-0}" -gt 0 ] && TACC_SEG="${TACC_SEG} ${RED}${vidle} IDEV${R}"
    fi
fi

if   [ "$CTX" -ge 80 ]; then cc="$RED"
elif [ "$CTX" -ge 60 ]; then cc="$YEL"
else cc="$DIM"; fi

printf '%s%s%s %s|%s %sctx %s%%%s %s|%s %s %s|%s %s%s%s' \
    "$CYA" "$MODEL" "$R" "$DIM" "$R" "$cc" "$CTX" "$R" \
    "$DIM" "$R" "$TACC_SEG" "$DIM" "$R" "$DIM" "$BRANCH" "$R"
