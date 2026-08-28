#!/bin/sh
# Single source of truth for Weights & Biases auth in can-it-ford.
#
# SOURCE this, do not execute it:   . scripts/wandb_env.sh
#
# It exports, and prints nothing on success:
#   WANDB_PY       absolute python that has the wandb library
#   WANDB_BIN      absolute wandb CLI
#   WANDB_API_KEY  pulled from ~/.netrc at runtime, never stored in the repo
#   WANDB_ENTITY   jcerrell29-claremont-mckenna-college
#   WANDB_PROJECT  can-it-ford
#
# WHY THE KEY COMES FROM ~/.netrc AND NOWHERE ELSE
# This repo is PUBLIC. A key committed here is world-readable and permanent:
# GitHub has served a removed key by SHA even after a filter-repo purge. ~/.netrc
# is mode 0600, is already the store `wandb login` writes and `curl -n` reads, and
# is covered by an explicit Read-deny rule in .claude/settings.local.json so no
# agent reads it directly. A key rotation therefore needs one edit, in one file,
# and every consumer below picks it up with no further change.
#
# This script NEVER echoes the key. Keep it that way.

# --- the venv that actually has wandb -----------------------------------------
# Measured 2026-08-20: wandb 0.28.2 / python 3.12.13 lives here and is NOT on
# PATH, which is why a bare `wandb` or `which wandb` reports "not found".
WANDB_VENV="${WANDB_VENV:-$HOME/.venvs/canitford-mpm}"
WANDB_PY="$WANDB_VENV/bin/python"
WANDB_BIN="$WANDB_VENV/bin/wandb"

if [ ! -x "$WANDB_PY" ]; then
    echo "wandb_env: no python at $WANDB_PY" >&2
    echo "wandb_env: set WANDB_VENV to a venv that has the wandb library" >&2
    return 1 2>/dev/null || exit 1
fi

# --- key, resolved at runtime from ~/.netrc ------------------------------------
# Python's stdlib netrc parser is used first because it handles both the
# multi-line and the single-line netrc forms. awk is the fallback for the case
# where the file has a macdef or a stray token that makes the strict parser raise.
if [ -z "$WANDB_API_KEY" ]; then
    WANDB_API_KEY=$(/usr/bin/python3 - <<'PY' 2>/dev/null
import netrc, sys
try:
    auth = netrc.netrc().authenticators("api.wandb.ai")
    sys.stdout.write(auth[2] if auth and auth[2] else "")
except Exception:
    sys.stdout.write("")
PY
)
fi

if [ -z "$WANDB_API_KEY" ] && [ -r "$HOME/.netrc" ]; then
    WANDB_API_KEY=$(awk '
        { for (i = 1; i <= NF; i++) {
            if ($i == "machine")  { inblock = ($(i+1) == "api.wandb.ai") }
            if (inblock && $i == "password") { print $(i+1); exit }
        } }
    ' "$HOME/.netrc")
fi

if [ -z "$WANDB_API_KEY" ]; then
    echo "wandb_env: no key for api.wandb.ai in ~/.netrc" >&2
    echo "wandb_env: fix with   $WANDB_BIN login --relogin" >&2
    return 1 2>/dev/null || exit 1
fi

# --- project identity ----------------------------------------------------------
WANDB_ENTITY="${WANDB_ENTITY:-jcerrell29-claremont-mckenna-college}"
WANDB_PROJECT="${WANDB_PROJECT:-can-it-ford}"

# Silence the per-call "Loaded credentials from /Users/josie/.netrc" banner, which
# otherwise contaminates any script that parses wandb stdout.
WANDB_SILENT="${WANDB_SILENT:-true}"

export WANDB_PY WANDB_BIN WANDB_API_KEY WANDB_ENTITY WANDB_PROJECT WANDB_SILENT
