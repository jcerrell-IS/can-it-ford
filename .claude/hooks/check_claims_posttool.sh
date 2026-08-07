#!/bin/bash
# ============================================================================
# check_claims_posttool.sh  PostToolUse guard on Write/Edit.
#
# WHY
#   CLAUDE.md and the corrections register exist to stop a retired number being
#   restated as fact, but that only works if every author reads all of it every
#   time. This runs scripts/check_claims.py against the single file just
#   written and, on an ERROR-severity hit, returns exit 2 so the finding is fed
#   back for a decision rather than landing silently.
#
#   Exit 2 is a prompt to VERIFY, not an order to edit. Quoting a refuted claim
#   in order to correct it is legitimate and common in this repo, which is why
#   this never rewrites anything itself.
#
# CONTRACT
#   stdin: PostToolUse hook JSON. exit 0 clean or not applicable, exit 2 hit.
#   Never fails the tool call for an infrastructure reason: a missing checker,
#   a non-repo path or bad JSON all exit 0.
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECKER="$REPO/scripts/check_claims.py"
[ -f "$CHECKER" ] || exit 0

INPUT="$(cat)"

FILE="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
print(ti.get("file_path") or ti.get("notebook_path") or "")
' 2>/dev/null)"

[ -n "$FILE" ] || exit 0
[ -f "$FILE" ] || exit 0

# Only text formats the rule table can reason about.
case "$FILE" in
    *.md|*.py|*.tex|*.bib) ;;
    *) exit 0 ;;
esac

# Stay inside the repo, and never lint the checker against its own rule table.
case "$FILE" in
    "$REPO"/*) ;;
    *) exit 0 ;;
esac
[ "$FILE" = "$CHECKER" ] && exit 0

OUT="$(python3 "$CHECKER" "$FILE" 2>/dev/null)"
echo "$OUT" | grep -q '^ERROR' || exit 0

{
    echo "check_claims flagged a previously refuted claim in the file you just wrote."
    echo "$OUT" | grep -A3 '^ERROR' | head -40
    echo
    echo "Verify the line against its authority before changing anything. If the text"
    echo "quotes the claim in order to correct or retire it, that is correct and you"
    echo "should leave it as written."
} >&2
exit 2
