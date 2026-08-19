#!/bin/bash
# Fleet watcher: r9 branch commits, session digests, and Vista batch state.
#
# WHY THIS EXISTS AS A FILE. The previous inline version captured squeue output
# as Q=$(ssh ... 2>/dev/null) and then treated an EMPTY Q as "no jobs remain".
# An unreachable host also yields an empty Q, so when the ControlMaster socket
# expired on 2026-08-19 it announced "every allocation has ended" while two jobs
# were RUNNING. A check must distinguish "measured zero" from "could not
# measure"; this one keeps the ssh exit status and reports LINK-DOWN instead.
#
# NO ASSOCIATIVE ARRAYS. /bin/bash here is 3.2.57, which has no `declare -A`.
# The inline version only worked because the tool shell is zsh; running the same
# text as `bash script.sh` exited immediately and silently. State is one small
# file per key instead, which also survives a restart.
set -uo pipefail
cd /Users/josie/can-it-ford 2>/dev/null || exit 1
S="/private/tmp/claude-501/-Users-josie-can-it-ford/r9_watch_state"
mkdir -p "$S" || exit 1
PREVJOBS=""
LINK="up"
key() { echo "$1" | tr -c 'A-Za-z0-9._-' '_'; }
while true; do
  for b in $(git branch --list 'claude/r9-*' --format='%(refname:short)' 2>/dev/null); do
    h=$(git rev-parse --short "$b" 2>/dev/null)
    s=$(git log -1 --format='%s' "$b" 2>/dev/null | cut -c1-90)
    f="$S/br.$(key "$b")"
    old=""; [ -f "$f" ] && old=$(cat "$f")
    if [ -n "$h" ] && [ "$old" != "$h" ]; then
      [ -n "$old" ] && echo "COMMIT ${b#claude/} $h :: $s"
      echo "$h" > "$f"
    fi
  done
  for d in $(ls -t .claude/state/r8_digests/*.md 2>/dev/null | head -3); do
    m=$(stat -f '%m' "$d" 2>/dev/null)
    f="$S/dg.$(key "$(basename "$d")")"
    old=""; [ -f "$f" ] && old=$(cat "$f")
    if [ "$old" != "$m" ]; then
      [ -n "$old" ] && echo "IDLE-DIGEST $(basename "$d")"
      echo "$m" > "$f"
    fi
  done
  # The login banner can prepend lines like `/work is mounted not "FULL"...` to
  # stdout. Those are not jobs; keep only rows whose first field is a job id, or
  # the watcher reports a filesystem notice as a running allocation.
  Q=$(ssh -o BatchMode=yes -o ConnectTimeout=10 vista \
        "squeue -u jcerrell0629 -h -o '%i|%j|%T|%L'" 2>/dev/null)
  RC=$?
  Q=$(echo "$Q" | awk -F'|' '$1 ~ /^[0-9]+(_[0-9]+)?$/')
  if [ $RC -ne 0 ]; then
    # COULD NOT MEASURE. Say so; do not reinterpret it as zero jobs, and leave
    # PREVJOBS alone so the real state is still there when the link returns.
    if [ "$LINK" = "up" ]; then
      echo "LINK-DOWN vista unreachable (ssh rc=$RC), job state UNKNOWN not empty. Run: ssh vista"
      LINK="down"
    fi
  else
    if [ "$LINK" = "down" ]; then echo "LINK-UP vista reachable again"; LINK="up"; fi
    if [ -n "$Q" ]; then
      CUR=$(echo "$Q" | awk -F'|' '{print $1$3}' | sort | tr '\n' ' ')
      if [ "$CUR" != "$PREVJOBS" ]; then
        echo "$Q" | awk -F'|' '{printf "JOB %s %s %s left=%s\n",$1,$2,$3,$4}'
        PREVJOBS="$CUR"
      fi
    elif [ -n "$PREVJOBS" ]; then
      echo "JOBS-EMPTY squeue answered with zero rows: every allocation has ended"
      PREVJOBS=""
    fi
  fi
  sleep 120
done
