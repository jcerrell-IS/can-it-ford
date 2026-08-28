# GitHub MCP and the Docker gateway, diagnosis 2026-08-25

Read-only diagnosis. **No config was modified, no process was restarted, no profile was
edited.** HEAD `0845e1c` on `claude/add-ci-checks`. Two other Claude Code sessions were
live in this repo during the pass.

**Tags**: [CONFIRMED] = command run and output seen in this session. [DOC] = read from a
file, not re-derived. [INFERRED] = reasoned, not measured.

---

## Headline: GitHub was never broken. The Docker gateway died, and it took GitHub's second path with it.

Four GitHub access paths were tested end to end. **Three work. One is down, and the one
that is down is not a GitHub problem.** [CONFIRMED]

| Path | Where | Transport | Status |
|---|---|---|---|
| `gh` CLI | shell | native | **WORKS**, authenticated as `jcerrell-IS` |
| `mcp__github__*` | Claude Code | HTTP to `api.githubcopilot.com/mcp/` | **WORKS**, verified twice, 21:44 and 21:54 |
| `github` (docker stdio) | Claude Desktop | `docker run ghcr.io/github/github-mcp-server` | **WORKS**, full handshake, 44 tools |
| `mcp__MCP_DOCKER__*` | both | `docker mcp gateway run --profile can_it_ford` | **DOWN since 21:50:11** |

**Nothing needed activating.** Both tokens are valid, both configs are correct, the image
is pulled, Docker is running, and no permission rule blocks GitHub.

---

## 1. What was ruled out, and how

Each of these was a plausible cause and each was tested rather than assumed. [CONFIRMED]

| Hypothesis | Test | Result |
|---|---|---|
| Missing `headers` block sending no token (the known 401 failure mode) | read `~/.claude.json` | **Ruled out.** `headers.Authorization` present and populated |
| Claude Code token expired | `GET api.github.com/user` | **Ruled out.** HTTP 200, `jcerrell-IS`, scopes `admin:public_key, gist, read:org, repo` |
| Copilot MCP endpoint rejecting the token | JSON-RPC `initialize` via curl | **Ruled out.** HTTP 200, full capability response |
| Claude Desktop PAT expired | `GET api.github.com/user` | **Ruled out.** HTTP 200, expires **2026-11-20** |
| `ghcr.io/github/github-mcp-server` image not pulled | `docker image ls` | **Ruled out.** Present, 74.4 MB, pulled 5 days ago |
| Docker not running | `docker version` | **Ruled out.** Server 29.7.2 |
| Desktop's github server fails to start | ran it exactly as configured, full MCP handshake | **Ruled out.** `v1.10.1`, initialize OK, **44 tools** listed |
| A deny rule blocking github MCP tools | read `.claude/settings.json` permissions | **Ruled out.** 15 deny rules, none touch github or MCP |
| `arxiv-mcp-server` breaking profile validation | `docker mcp profile server ls` | **Already fixed.** Not in either profile any more |
| deepwiki `Gone` breaking the profile | live `initialize` POST | **Transient, resolved.** HTTP 200 now |

The Claude Code `github` token is **byte-identical to the `gh` CLI token** [CONFIRMED], so
those two paths share one credential and cannot fail independently.

---

## 2. What actually failed

### 2a. The gateway died from an OAuth error with an empty provider name

From `~/Library/Logs/Claude/mcp-server-MCP_DOCKER.log` [CONFIRMED]:

```
- Token status for hugging-face: valid=true, expires_at=2026-08-26T05:46:58+01:00 ...
- SSE event received: error for
- OAuth error for  (no details)
2026-08-25T20:50:11.027Z [MCP_DOCKER] [info] Server transport closed unexpectedly ...
2026-08-25T20:50:11.027Z [MCP_DOCKER] [error] Server disconnected.
```

The provider name is **empty** in both the SSE event and the error line. The gateway had
just successfully refreshed the hugging-face OAuth token (11 tools, 155 resources
registered), then received a nameless error event and tore down the whole transport.

**Consequence:** `docker mcp gateway run` is not running at all.
`ps` for `mcp gateway run` returns nothing. [CONFIRMED]

**Reproduced live:** `mcp__MCP_DOCKER__get_me` returned a correct result at 21:44 and
`Server MCP_DOCKER unavailable` at 21:54, straddling the 21:50:11 death. [CONFIRMED]

**Desktop is not auto-recovering.** The log's last write is 21:50:11 and no retry has
occurred in the minutes since, unlike the retry storm it produced at 02:37 to 03:07 today.
[CONFIRMED]

### 2b. Claude Desktop is running a config that is two hours stale

| Event | Time |
|---|---|
| Claude Desktop (PID 98811) started | **19:27:23** |
| its MCP gateway helper spawned | 19:28:59 |
| `claude_desktop_config.json` last modified | **21:39:46** |

[CONFIRMED] Desktop reads that file only at launch, so **any change made at 21:39 is not
loaded**. If a GitHub setting was edited then, that edit has never taken effect.

### 2c. Two GitHub servers are enabled in one profile

`docker mcp profile server ls` and the gateway's own startup output both show the
`can_it_ford` profile enabling **`github` AND `github-official`**, from two different
images (`mcp/github` and `ghcr.io/github/github-mcp-server`). [CONFIRMED]

```
- Those servers are enabled: context7, exa, sequentialthinking, paper-search,
  github-official, hugging-face, github
```

Claude Desktop then adds a **third** GitHub server of its own (`github`, direct
`docker run` of the same image). Three GitHub MCP servers, two of them inside one gateway,
all exposing identically-named tools such as `get_me`. This is a standing collision risk
and the likely source of the historical "GitHub MCP path changed 3x in 16h" churn.

---

## 3. Pre-flight: a restart will come back clean

Before recommending a restart, the profile was activated manually to check it would not
fail on the way back up. [CONFIRMED]

```
- Those servers are enabled: context7, exa, sequentialthinking, paper-search,
  github-official, hugging-face, github
> Images verified in 1.219580459s
  > sequentialthinking: (1 tools)
```

**The profile activates cleanly. No validation failure.** The `arxiv-mcp-server`
`storage_path` defect that broke activation at 02:35 and 02:58 today is gone, because that
server has been removed from the profile.

---

## 4. Why this was not fixed in the session that found it

**Claude Desktop PID 98811 is the parent process of the running Claude Code sessions.**
Verified by walking the process tree: `zsh` -> `claude-code/2.1.241/claude` ->
`Claude.app/Contents/Helpers/disclaimer` -> `Claude.app/Contents/MacOS/Claude` (98811).
[CONFIRMED]

Restarting Claude Desktop therefore **terminates every live Claude Code session**, which
at the time of writing was three. That is a user decision, not an agent one, so no restart
was performed.

---

## 5. What to do

**Nothing is blocked right now.** `mcp__github__*` works and is independent of Docker; use
it for GitHub work until the gateway is back.

To restore the gateway, quit and reopen Claude Desktop. That single action also loads the
21:39 config edit. Expect all live Claude Code sessions to end.

Optional cleanup, worth doing before the restart so it comes back without the collision:
remove one of the two GitHub servers from the `can_it_ford` profile. `github-official`
(`ghcr.io/github/github-mcp-server`) is the first-party image and is the one Claude Desktop
also uses directly, so **`github` (`mcp/github`) is the redundant one**. [INFERRED, from
image provenance, not from a functional comparison of the two tool sets.]

Unresolved and outside this machine: whether the **claude.ai web GitHub connector** points
at this repo. Project memory records it targeting `jcerrell-IS/mpm-engine`, which does not
reach `can-it-ford`. [DOC] The web log shows `github:` tool calls succeeding as recently as
2026-08-25 19:11 but with `approvalRequired: true`, where 2026-08-23 and 2026-08-24 calls
were mostly `approvalRequired: false`. [CONFIRMED] A tool call awaiting approval looks
exactly like a broken connector from the user's side, and is worth checking first if the
symptom recurs in the web client.

---

## 6. Credential note

While reading the Desktop config, a redaction in one diagnostic command failed and a live
`github_pat_` value was printed into the session transcript. The token authenticates as
`jcerrell-IS` and is valid until **2026-11-20**. **It should be rotated.** [CONFIRMED]

A scan of that config found **exactly one** secret-shaped value, so the exposure is bounded
to that single token and no other credential in the file was printed. [CONFIRMED]

Rotate at `github.com/settings/personal-access-tokens`, then update
`~/Library/Application Support/Claude/claude_desktop_config.json` at
`mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN`. That file is mode `0600` and lives
outside the repository, so it is not committed and not published; the exposure is the
transcript, not the repo.
