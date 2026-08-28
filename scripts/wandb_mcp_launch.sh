#!/bin/sh
# Launcher for the official W&B MCP server (wandb/wandb-mcp-server), stdio transport.
# Referenced by .mcp.json. Not meant to be run by hand, though doing so is harmless:
# it will just sit waiting for MCP protocol traffic on stdin.
#
# TWO THINGS THIS WRAPPER EXISTS TO DO, both of which a plain uvx line cannot:
#
# 1. KEEP THE KEY OUT OF .mcp.json. That file is tracked and this repo is PUBLIC.
#    The key is read from ~/.netrc at launch by wandb_env.sh instead.
#
# 2. PIN mcp[cli] BELOW 2.0. Measured 2026-08-20: wandb-mcp-server declares
#    `mcp[cli]>=1.0.0` with no upper bound, uv resolves that to mcp 2.0.0, and
#    2.0.0 no longer ships `mcp.server.fastmcp`. The server then dies at import
#    with ModuleNotFoundError before serving a single tool. `--with 'mcp[cli]<2'`
#    forces a working resolution. Revisit once upstream adds the upper bound;
#    the symptom of a stale pin would be uvx resolving an old mcp unnecessarily,
#    which is harmless, so this is safe to leave in place.

set -e
HERE=$(dirname "$0")
. "$HERE/wandb_env.sh"

UVX=$(command -v uvx 2>/dev/null || echo /opt/homebrew/bin/uvx)
if [ ! -x "$UVX" ]; then
    echo "wandb_mcp_launch: uvx not found, cannot start W&B MCP server" >&2
    exit 1
fi

# Default the server's own tracing project to this project, so any MCP call it
# traces lands somewhere expected rather than in a stray weave-mcp-server project.
export MCP_WEAVE_ENTITY="${MCP_WEAVE_ENTITY:-$WANDB_ENTITY}"

exec "$UVX" \
    --from git+https://github.com/wandb/wandb-mcp-server \
    --with 'mcp[cli]<2' \
    wandb_mcp_server "$@"
