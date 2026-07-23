
## Final Confirmed State, 2026-07-23

All five project MCP connectors verified independently against their real
services (not just claude mcp list status) on all three machines:

| Machine | deepwiki | github | wandb | hf | scite |
|---|---|---|---|---|---|
| Mac | Connected | Connected | Connected | Connected | Connected |
| Vista | Connected | Connected | Connected | Connected | Connected |
| LS6 | Connected | Connected | Connected | Connected | Connected |

Root causes found and fixed this round, kept here for the next rotation:
old exposed GitHub PAT (github_pat_11CDJE...) from a July 19 chat leak was
still live and unrevoked until this session; GitHub's Copilot MCP endpoint
needs the "Copilot Requests" account permission, not just repo scopes;
/tmp on TACC nodes is not shared across idev allocations, use
~/.secrets_tmp instead; a stale "huggingface" duplicate entry (wrong URL,
?login suffix) existed alongside the working "hf" entry and was removed.
