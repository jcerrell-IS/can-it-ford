#!/bin/sh
# provision.sh: one-time HOST-side setup for the canitford-base kit.
#
# Run this on the Mac, not inside a sandbox. It stores three secrets in the
# sbx secret store and then creates the sandbox with the kit attached.
#
# NO SECRET VALUE APPEARS IN THIS FILE, in argv, or in shell history. Every
# secret is registered with `--command`, which stores the COMMAND, not the
# value, and re-resolves it on the host when a sandbox needs it. That is the
# same discipline scripts/wandb_env.sh already uses for ~/.netrc.
#
#   Success looks like: `sbx secret ls` gains three rows beyond the existing
#   anthropic row, and `sbx ls` shows a sandbox named canitford.
#   Most likely failure: `gh auth token` prompts or fails because the macOS
#   keyring is locked, which makes the github secret resolve to empty. Run
#   `gh auth status` first and fix that before running this.
#
# Verified against sbx v0.39.0 (def8cb0) on 2026-08-23.

set -eu

KIT_DIR="/Users/josie/can-it-ford/sandbox/canitford-kit"
WORKSPACE="/Users/josie/can-it-ford"
SANDBOX_NAME="${SANDBOX_NAME:-canitford}"

say() { printf '\n=== %s ===\n' "$1"; }

# ---------------------------------------------------------------------------
say "0. preflight"
# ---------------------------------------------------------------------------
command -v sbx >/dev/null 2>&1 || { echo "sbx not on PATH" >&2; exit 1; }
sbx kit validate "$KIT_DIR" || { echo "kit does not validate, fix it first" >&2; exit 1; }

if ! gh auth status >/dev/null 2>&1; then
    echo "gh is not authenticated on the host. Run 'gh auth login' first." >&2
    exit 1
fi

if [ ! -r "$HOME/.cache/huggingface/token" ]; then
    echo "no HF token at ~/.cache/huggingface/token. Run 'hf auth login' first." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
say "1. github, as a built-in service secret"
# ---------------------------------------------------------------------------
# `github` is one of sbx's built-in services, so the proxy authenticates
# api.github.com requests on the sandbox's behalf and the token never enters
# the container filesystem. The --command form below is the binary's own
# documented example: it re-reads the macOS keyring on demand.
sbx secret set github --command 'gh auth token'

# ---------------------------------------------------------------------------
say "2. HF_TOKEN, as a custom secret with a placeholder"
# ---------------------------------------------------------------------------
# wandb and huggingface are NOT built-in services (the built-in list is
# anthropic, cursor, droid, github, google, groq, mistral, nebius, openai,
# openrouter, xai), so both use set-custom. The sandbox sees a placeholder;
# the proxy substitutes the real value in headers on the way to --host.
sbx secret set-custom \
    --host huggingface.co \
    --env HF_TOKEN \
    --command 'cat "$HOME/.cache/huggingface/token"'

# ---------------------------------------------------------------------------
say "3. WANDB_API_KEY, as a custom secret with a placeholder"
# ---------------------------------------------------------------------------
# The resolver is the same stdlib netrc parse scripts/wandb_env.sh prefers,
# so a key rotation still needs exactly one edit, in ~/.netrc.
#
# CAVEAT, and it is a real one: the placeholder is substituted in header
# VALUES as a literal string. That works for the hosted MCP endpoint, which
# wants `Authorization: Bearer <key>`. It does NOT work for the wandb Python
# client, which uses HTTP Basic (auth = ("api", self.api_key) at
# wandb/sdk/internal/internal_api.py:290 and :343) and therefore base64
# encodes the key on the wire, where a literal placeholder never matches.
# So: the wandb MCP server works, `wandb` library calls from inside the
# sandbox do not. See sandbox/README.md.
sbx secret set-custom \
    --host api.wandb.ai --host wandb.ai --host mcp.withwandb.com \
    --env WANDB_API_KEY \
    --command 'python3 -c "import netrc,sys; a=netrc.netrc().authenticators(\"api.wandb.ai\"); sys.stdout.write(a[2] if a and a[2] else \"\")"'

# ---------------------------------------------------------------------------
say "4. secrets now stored"
# ---------------------------------------------------------------------------
sbx secret ls

# ---------------------------------------------------------------------------
say "5. create the sandbox"
# ---------------------------------------------------------------------------
# Bind-mounts $WORKSPACE, which is how the project CLAUDE.md, the memory
# directory and the repo-scoped skills reach the sandbox. Nothing copies them.
#
# Consider --clone instead if you want the agent's writes isolated from the
# host working tree. With a shared repo and other live sessions, --clone is
# the safer default. It is not the default here only because it changes the
# git workflow (commits come back via the sandbox-<name> remote).
if sbx ls 2>/dev/null | awk 'NR>1{print $1}' | /usr/bin/grep -qx "$SANDBOX_NAME"; then
    echo "sandbox '$SANDBOX_NAME' already exists."
    echo "To apply kit changes to it:   sbx kit add $SANDBOX_NAME $KIT_DIR"
    echo "To rebuild from scratch:      sbx rm $SANDBOX_NAME && sh $0"
else
    sbx create --name "$SANDBOX_NAME" --kit "$KIT_DIR" claude "$WORKSPACE"
fi

# ---------------------------------------------------------------------------
say "6. next step"
# ---------------------------------------------------------------------------
cat <<EOF
Verify the sandbox actually came up right:

    sbx exec $SANDBOX_NAME -- sh /workspace/sandbox/verify_sandbox.sh

If the workspace mounts somewhere other than /workspace, find it with:

    sbx exec $SANDBOX_NAME -- pwd

Then attach:

    sbx run --name $SANDBOX_NAME
EOF
