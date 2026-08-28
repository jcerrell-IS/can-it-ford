#!/usr/bin/env bash
# Install an Overleaf Git authentication token for the overleaf MCP server and
# for `git push overleaf`.
#
# WHY THIS EXISTS. Measured 2026-08-18: /Users/josie/.config/overleaf-mcp/token
# is 0 bytes, which makes the MCP clone as https://git:@git.overleaf.com/... with
# an empty password. The MCP reports "Connected" anyway, so the failure only
# surfaces on the first real fetch. See docs/MCP_CONNECTOR_AUDIT_2026-08-18.md s5.
#
# The token is read from STDIN, never from argv. That keeps it out of shell
# history, out of `ps`, and out of any Claude transcript.
#
# USAGE
#   1. Generate a token: overleaf.com -> Account Settings -> Git integration
#   2. Run:   ./scripts/overleaf_token_install.sh
#   3. Paste the token, press Return, then Ctrl-D
set -euo pipefail

TOKEN_FILE="${OVERLEAF_TOKEN_FILE:-$HOME/.config/overleaf-mcp/token}"
PROJECT_ID="6a5958d10484feadf65a934e"

umask 077
mkdir -p "$(dirname "$TOKEN_FILE")"
chmod 700 "$(dirname "$TOKEN_FILE")"

if [ -t 0 ]; then
  printf 'Paste the Overleaf Git authentication token, then Return, then Ctrl-D:\n' >&2
fi

TOKEN="$(cat)"
TOKEN="${TOKEN//[$'\t\r\n ']/}"

if [ -z "$TOKEN" ]; then
  echo "ERROR: empty input, nothing written. Token file left as-is." >&2
  exit 1
fi
case "$TOKEN" in
  YOUR_GIT_TOKEN|olp_) echo "ERROR: that is a placeholder, not a token." >&2; exit 1 ;;
esac

printf '%s' "$TOKEN" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"
unset TOKEN
echo "wrote $(wc -c < "$TOKEN_FILE" | tr -d ' ') bytes to $TOKEN_FILE (mode $(stat -f '%Lp' "$TOKEN_FILE"))" >&2

echo "verifying against Overleaf, read-only..." >&2
if GIT_TERMINAL_PROMPT=0 git ls-remote \
     "https://git:$(cat "$TOKEN_FILE")@git.overleaf.com/$PROJECT_ID" HEAD >/dev/null 2>&1; then
  echo "OK: Overleaf authenticates. Restart Claude Code so the MCP server picks it up." >&2
else
  echo "FAILED: token written but Overleaf rejected it." >&2
  echo "  Most likely the token was revoked, or copied with a character missing." >&2
  echo "  Generate a fresh one and re-run. Nothing else on disk was changed." >&2
  exit 1
fi
