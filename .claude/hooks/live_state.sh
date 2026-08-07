#!/bin/bash
# ============================================================================
# live_state.sh  UserPromptSubmit: inject generated state, every single turn.
#
# THE PROBLEM THIS SOLVES
#   The recurring failure in this project is not that Claude lacks information.
#   It is that Claude carries STALE information: a fact learned at session start,
#   or read out of a summary, that stopped being true while the session ran. In
#   one session alone that produced: editing files another session held, calling
#   a queue empty two minutes before sacct showed a running job, and concluding
#   the git remotes were deleted when the shell had simply changed directory.
#
#   A SessionStart hook cannot fix that, because it fires once and the world
#   moves. This fires on EVERY prompt, and it reports only things it just
#   measured. Nothing here is remembered, quoted, or carried forward.
#
# BUDGET
#   Runs on every prompt, so it must be fast and silent on failure. Everything
#   here is local: git plumbing, stat on session files, and the status-line
#   cache. It NEVER opens an ssh connection. TACC numbers come from the cache
#   the status line already refreshes in the background, and their age is
#   printed so a stale number is never mistaken for a fresh one.
# ============================================================================
set -uo pipefail

REPO="${CLAUDE_PROJECT_DIR:-/Users/josie/can-it-ford}"
cd "$REPO" 2>/dev/null || exit 0

OUT=""
add() { OUT="${OUT}$1"$'\n'; }

# --- git, the cheap authoritative facts -----------------------------------
HEAD=$(git rev-parse --short HEAD 2>/dev/null || echo "?")
BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "?")
add "HEAD ${HEAD} on ${BR}, ${AHEAD} unpushed"

# --- who else is live in this repo right now ------------------------------
# Every Claude Code session appends to its own transcript. A transcript touched
# in the last 3 minutes is an active session. This is the single most useful
# fact to have before editing anything, and it is the one nothing else reports.
SESS_DIR="$HOME/.claude/projects/-Users-josie-can-it-ford"
ME="${CLAUDE_SESSION_ID:-}"
NOW=$(date +%s)
OTHERS=0
if [ -d "$SESS_DIR" ]; then
    for f in "$SESS_DIR"/*.jsonl; do
        [ -f "$f" ] || continue
        b=$(basename "$f" .jsonl)
        [ -n "$ME" ] && [ "$b" = "$ME" ] && continue
        mt=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)
        [ $((NOW - mt)) -lt 180 ] && OTHERS=$((OTHERS + 1))
    done
fi
if [ "$OTHERS" -gt 0 ]; then
    add "CONCURRENT: ${OTHERS} other session(s) active in this repo in the last 3 min."
    add "  Do not edit a file listed dirty below without checking it is not theirs."
fi

# --- uncommitted, and how recently each was touched -----------------------
DIRTY=$(git status --porcelain 2>/dev/null | grep -vE '^\?\? ' | awk '{print $NF}')
if [ -n "$DIRTY" ]; then
    N=$(printf '%s\n' "$DIRTY" | wc -l | tr -d ' ')
    HOT=""
    while IFS= read -r f; do
        [ -f "$f" ] || continue
        mt=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)
        # Touched in the last 10 minutes: likely another session's live work.
        [ $((NOW - mt)) -lt 600 ] && HOT="${HOT}${f} "
    done <<< "$DIRTY"
    add "DIRTY ${N} tracked file(s) uncommitted."
    [ -n "$HOT" ] && add "  CHANGED IN LAST 10 MIN (treat as someone else's live work): ${HOT}"
fi

# --- TACC, from cache only, with its age stated ---------------------------
CACHE="$HOME/.cache/canitford/tacc_status"
if [ -f "$CACHE" ]; then
    mt=$(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null || echo 0)
    AGE=$(( (NOW - mt) / 60 ))
    LINE=""
    while IFS=: read -r host su jobs idle; do
        [ -n "${host:-}" ] || continue
        seg="${host} ${su}SU"
        [ "${jobs:-0}" -gt 0 ] && seg="${seg} ${jobs}job"
        [ "${idle:-0}" -gt 0 ] && seg="${seg} ${idle}IDLE-IDEV"
        LINE="${LINE}${seg}; "
    done < "$CACHE"
    add "TACC (cache ${AGE}m old, re-check before acting): ${LINE}"
fi

[ -n "$OUT" ] || exit 0
printf '<live-state generated="%s">\n%s</live-state>\n' "$(date +%H:%M:%S)" "$OUT"
exit 0
