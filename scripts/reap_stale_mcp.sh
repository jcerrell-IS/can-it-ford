#!/bin/bash
# Reap MCP server processes older than a threshold, macOS/BSD safe.
#
# Why this exists: the obvious one-liner is wrong twice on macOS.
#   ps -o etimes   -> "keyword not found". etimes is GNU procps-ng, Linux only.
#   ps -o etime    -> exists, but returns [[dd-]hh:]mm:ss as a STRING, so a
#                     numeric awk test coerces "11-00:00:01" to 11 and silently
#                     never fires. That failure mode is worse than the error.
# This parses etime into real seconds instead.
#
# Usage:  reap_stale_mcp.sh <pattern> [max_age_seconds] [--kill]
#         Default is a DRY RUN. Nothing dies without --kill.
set -uo pipefail

PATTERN="${1:?usage: reap_stale_mcp.sh <pattern> [max_age_seconds] [--kill]}"
MAXAGE="${2:-86400}"
DOKILL="${3:-}"

ps -eo pid=,etime=,command= \
| grep -F -- "$PATTERN" \
| grep -v -- 'reap_stale_mcp' \
| awk -v maxage="$MAXAGE" '
    function secs(e,   n, a, b, d, t) {
        d = 0
        n = split(e, a, "-")
        if (n == 2) { d = a[1]; e = a[2] }
        n = split(e, b, ":")
        if (n == 3) t = b[1]*3600 + b[2]*60 + b[3]
        else        t = b[1]*60   + b[2]
        return d*86400 + t
    }
    { age = secs($2); if (age > maxage) printf "%s %s %s\n", $1, age, $2 }
'
