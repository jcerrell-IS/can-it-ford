# MCP Flapping Diagnosis: Source Verification

Written 2026-08-23. Read-only investigation. No config was changed, no server added or
removed, no Dockerfile or `.mcp.json` touched.

Verifies the claims in `~/Downloads/compass_artifact_wf-fe5433cb-89e8-54d0-897a-b178f0201a04_text_markdown.md`
("MCP Hosting for Claude Desktop + Claude Code on Apple Silicon"), referred to below as
"the prior report".

**Headline: the prior report's root cause is refuted for the only two episodes this machine
has evidence for, and its primary recommendation is contradicted by GitHub's own installation
guide. The measured cause of both 2026-08-22 failures is that the Docker daemon was not
running when the servers were spawned.**

---

## Method and its limits

All local evidence comes from `~/Library/Logs/Claude/`, which covers the **Claude Desktop**
surface only. Claude Code writes to `~/.claude/projects/*.jsonl` and is not represented here.
So every "absent from logs" statement below is evidence about Desktop, not about Claude Code.
That distinction is load-bearing and is flagged wherever it applies.

Log coverage: `main4.log` from 2026-08-07, `mcp1.log` through 2026-08-22 23:35,
`main.log` 2026-08-18 to present, per-server logs `mcp-server-*.log` spanning
**2026-07-03 to 2026-08-22** for failure events.

---

## PHASE 0: Which surface flapped

**Ambiguous from logs alone, but the topology is now pinned.** GitHub-over-Docker runs on
*both* surfaces, from the same image, under different tokens.

| | Claude Desktop | Claude Code |
|---|---|---|
| GitHub server | `github` = `docker run -i --rm ghcr.io/github/github-mcp-server`, token `github_pat_…` (93 ch) | `repo-tools`, **identical** `docker run` line, token `gho_…` (40 ch) |
| MCP_DOCKER gateway | present, log written 2026-08-23 01:59 | **0 occurrences** in `~/.claude.json` or `.mcp.json` |
| Desktop Commander | local extension `ant.dir.gh.wonderwhy-er.desktopcommandermcp` | claude.ai **remote** connector ("claude.ai Remote Desktop Commander") |

Sources, all read live 2026-08-23:
`~/Library/Application Support/Claude/claude_desktop_config.json` (6 servers);
`~/.claude.json` (10 top-level, plus per-project);
`~/Library/Application Support/Claude/Claude Extensions/`;
`ps -axo pid,ppid,command`.

At the time of measurement, 11 `github-mcp-server` containers were alive: **9 parented by
Claude Code processes** (`claude-code/2.1.237`, plus two bare `claude`), 2 by `Claude.app`.
Count fell to 6 within four minutes, so containers churn per connection rather than leak.

**Consequence for the prior report:** its inference chain requires Desktop Commander and the
GitHub server to share the Claude Desktop bridge. On the Claude Code surface Desktop Commander
is a *remote* claude.ai connector and shares nothing local with the Docker GitHub server, so
the argument does not transfer to Claude Code even in principle.

---

## PHASE 1: The Desktop Commander simultaneity claim

### Claim
> "Desktop Commander ... failed with the identical signature at the identical time. If the
> fault were inside the Docker Gateway, a non-Docker server could not be affected."

### Verdict: **REFUTED**

Extracted every `[error] Server disconnected` and `transport closed unexpectedly` event from
all 24 `mcp-server-*.log` files, deduplicated per server per second: **261 failure events,
2026-07-03 to 2026-08-22.**

Per-server totals for the three servers at issue:

| server | failures | timestamps |
|---|---|---|
| github | 4 | 2026-07-03 00:29:21, 2026-07-26 07:37:26, 2026-08-22 14:34:07, 2026-08-22 22:14:46 |
| Desktop Commander | **1** | 2026-08-08 03:48:30 |
| MCP_DOCKER | 1 | 2026-08-22 22:14:48 |

**Clusters containing both `github` and `Desktop Commander`: 0 at a 10-second window, 0 at a
60-second window.** Desktop Commander's single failure in 51 days is 13 days after the nearest
github failure and 14 days before the next. The simultaneity the prior report rests on does
not exist in these logs.

### The co-failure that *did* happen pairs the two Docker servers

github failed at `22:14:46.931`, MCP_DOCKER at `22:14:48.575`, **1.64 s apart**. Both are the
Docker-backed servers. This is the opposite pairing from the one the prior report inferred.

### Controlled comparison, 2026-08-22 22:14:44 restart window

All servers reinitialized in the same second, same client, same bridge:

| outcome | count | servers |
|---|---|---|
| failed | **2** | `github`, `MCP_DOCKER` |
| succeeded | **15** | Desktop Commander, filesystem, memory, sequential-thinking, overleaf, Figma, Control Chrome, MacOS-MCP, Blender, AWS API MCP Server, Scholar Sidekick, PDF Tools, PowerPoint, Word, pdf-viewer |

The failures sort **perfectly by command binary**: the only two servers whose
`Using MCP server command:` line reads `/usr/local/bin/docker` are the only two that failed.
A shared client-side bridge fault cannot sort its victims by which binary they exec.

### Counter-evidence, reported because it cuts the other way

Two earlier windows *are* multi-server cascades that include non-Docker servers:

- **2026-07-26 07:37:26**: 18 servers active, **9 failed** (AWS API, Blender, MacOS-MCP,
  ToolUniverse, filesystem, github, memory, sequential-thinking, wolfram-alpha)
- **2026-07-03 00:29:21**: 5 servers active, **5 failed** (filesystem, github, memory,
  sequential-thinking, wolfram-alpha)

These are consistent with a shared-client event and are the strongest surviving support for
the prior report's general theory. But neither includes Desktop Commander, and neither carries
the #65643 signature (below). They read as app shutdown cascades.

### The #65643 protocol signature is absent

Issue #65643 specifies `MCP error -32001: Request timed out` with a client
`notifications/cancelled` at exactly +4:00.

| probe | scope | result |
|---|---|---|
| `-32001` | `mcp.log`, `mcp1.log`, all 24 `mcp-server-*.log` | **0** |
| `"local MCP server"` | entire `~/Library/Logs/Claude/` | **0 files** |
| `notifications/cancelled` | `mcp.log` / `mcp1.log` | 0 / **1** (Desktop Commander, 2026-07-26 00:11:14) |
| `"timed out"` | `mcp.log`, `mcp1.log` | 0 |

The four `"unresponsive"` hits in `main*.log` are all
`Main webview is unresponsive, will kill and reload`, the Electron renderer, not MCP
(2026-08-11 x3, 2026-08-18 x1). The 29 `[client-timeout]` entries in `main1.log` are all SSH
handshake timeouts to Vista.

---

## PHASE 1b: What actually caused both 2026-08-22 failures

**Docker Desktop was not running.**

`~/Library/Containers/com.docker.docker/Data/log/host/Docker.log`, read live:

```
time="2026-08-21T23:28:07Z" msg="AppDelegate: terminating..."
time="2026-08-22T22:14:50Z" msg="AppDelegate: launching..."
```

Docker Desktop was down for roughly 23 hours. Reconstructed timeline for 2026-08-22:

| time | event | source |
|---|---|---|
| 22:14:44.296 | Claude Desktop initializes all 17 MCP servers | `mcp-server-*.log` |
| 22:14:46.485/.495 | both Docker servers report "Server started and connected successfully" | `mcp-server-github.log`, `mcp-server-MCP_DOCKER.log` |
| 22:14:46.931 | github: transport closed unexpectedly, `[error] Server disconnected` | `mcp-server-github.log` |
| 22:14:48.575 | MCP_DOCKER: same | `mcp-server-MCP_DOCKER.log` |
| **22:14:50** | **Docker Desktop launches** | `Docker.log` |
| 22:14:53.065 | "VM has started" | `com.docker.backend.log` |
| 22:14:53.150 | virtualization watchdog starts | `com.docker.virtualization.log` |

The `docker run` commands were issued **four seconds before Docker Desktop launched** and
**seven seconds before the VM was up**.

The 14:34 failure is the same mechanism: github failed at `14:34:07.734`, and
`com.docker.virtualization.log` records `starting watchdog` at `14:34:07.767`, **33 ms later**.

Both servers also emitted:
`Couldn't start this server for Cowork and Code sessions (they run their own copy of it)`,
which independently confirms Claude Code spawns its own containers.

This is a **cold-start race**, the class described in `docker/mcp-gateway#336`, not the
in-session bridge wedge of `#65643`.

---

## PHASE 2: The GitHub connector scope claim

### Claim
> "Migrate GitHub off the Docker-hosted server toward Anthropic/GitHub's **hosted remote
> connector** ... This removes the Docker daemon + Gateway from the GitHub critical path
> entirely."

### Verdict: **REFUTED for Claude Desktop, VERIFIED for Claude Code**

Primary source: `github/github-mcp-server`, `docs/installation-guides/install-claude.md`,
last modified commit `fab5fc5ff`, **2026-06-26** ("docs: lead local/stdio install with OAuth
login (#2776)"). 58 days old, borderline on the 60-day staleness rule.

The document's own section structure settles it:

| client | remote HTTP section? | local Docker section? | binary, no Docker? |
|---|---|---|---|
| Claude Code CLI | **yes** (line 29) | yes (line 63) | **yes** (line 88) |
| Claude Desktop | **no such section** | yes (line 145) | no |
| Xcode (Claude Agent) | yes (line 226) | yes (line 250) | no |

Verbatim, from the Claude Desktop section:

> "Claude Desktop supports MCP servers that are both local (stdio) and remote ("connectors").
> Remote servers can generally be added via Settings → Connectors → "Add custom connector".
> However, the GitHub remote MCP server requires OAuth authentication through a registered
> GitHub App (or OAuth App), which is not currently supported. **Use the local Docker setup
> instead.**"

### Finding the prior report omits entirely

The same section opens with:

> "⚠️ **Note**: Some users have reported compatibility issues with Claude Desktop and
> Docker-based MCP servers. We're investigating. If you experience issues, try using another
> MCP host, while we look into it!"

GitHub documents a known Claude Desktop plus Docker-MCP incompatibility. This is tier 1 and it
independently corroborates the Docker-specific failure sorting measured in Phase 1. The prior
report cites this repo but not this warning.

### Source contradiction, reported rather than resolved

`README.md` line 27 lists "Claude Desktop" among hosts "with remote server support". That is
reconcilable with the above (Desktop supports remote MCP generally; the *GitHub* remote server
specifically needs an OAuth app Desktop lacks), but the README line read alone is misleading,
and it is likely what the prior report relied on.

### The three paths, separated by client

1. **Claude Code, remote HTTP + PAT.** Supported and documented.
   `claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'`
   (install-claude.md line 36; requires Claude Code >= 2.1.1, installed here is **2.1.237**).
   `claude.com/connectors/github` (HTTP 200, title "GitHub MCP Connector | Claude by Anthropic")
   documents exactly one command, `claude mcp add --transport http github https://api.githubcopilot.com/mcp/`,
   and mentions "Claude Code" 13 times and "Claude Desktop" **0** times.
2. **Claude Code, local binary, no Docker.** install-claude.md line 88: download the release
   binary, then
   `claude mcp add-json github '{"command":"github-mcp-server","args":["stdio"],"env":{...}}'`.
3. **Claude Desktop: local Docker only**, per the quote above.

### The OAuth connector: **UNCONFIRMED**

`https://github.com/apps/claude-github-mcp-connector` returns HTTP 200, title
"GitHub Apps - Claude Github MCP Connector", so the GitHub App is real and registered. It is a
distinct mechanism from PAT/Bearer HTTP. I could **not** confirm from any primary source which
client surfaces it or whether it reaches Claude Desktop chat. The GitHub App page renders no
install metadata unauthenticated. Do not assert it works in Desktop.

---

## PHASE 3: Memory pressure as a third candidate

### Verdict: **condition VERIFIED, causal role UNCONFIRMED and currently unsupported**

Machine: 16.0 GB physical (`sysctl hw.memsize`). Docker VM: **7.75 GiB**, ~50% of host, which
is the macOS default; `settings-store.json` has **no `MemoryMiB` key**, so it is unconfigured.

Two snapshots, 2026-08-23:

| | 02:19 | 02:26 |
|---|---|---|
| swap used / total | 8.93 GB / 10.24 GB | 8.53 GB / 10.24 GB |
| pages free | 548 MB | **114 MB** |
| compressor | 4.53 GB | **5.72 GB** |
| containers | 11 then 6 | 7 |

Aggregate RSS: all `claude`-matching processes **3.29 GB across 91 procs**; bare `claude` CLI
**1.89 GB across 11 procs**; `Claude.app` 2.29 GB across 53 procs; `docker*` 0.60 GB.

**The negative control matters more than the numbers.** The machine spent this entire session
at 114 to 548 MB free with ~8.5 GB swapped, and there were **zero MCP failures today**
(`grep "2026-08-23.*\[error\] Server disconnected"` across all per-server logs returns none).
Heavy memory pressure is present and is not producing flapping.

Nor is there any kill signature. `docker/desktop-feedback#434` specifies
`monitor exited: signal: killed` in `com.docker.backend.log`. Across **all ten** backend logs
on this machine that string appears **0 times**; the only matches for
`killed|oom|panic|fatal|watchdog` are routine `starting watchdog` and `VM has started` lines.

### Documented reports

- **`docker/desktop-feedback#434`**, "Docker Desktop backend exits while GUI remains running;
  docker-mcp can block restart on macOS". OPEN, created 2026-06-03, **last updated
  2026-06-04, 80 days, STALE**. Tier 1 venue, single reporter, Apple Silicon, macOS 26.5,
  Docker Desktop 4.76.0. Mechanism is backend exit first, virtualization exit second.
  Symptom overlaps this machine's 23-hour Docker outage but the diagnostic string is absent
  here, so it is **not** established as the same fault.
- **`docker/mcp-gateway#336`**, "Claude Code to MCP Toolkit is timing out". OPEN, created
  2026-01-12, **last updated 2026-01-27, 208 days, STALE**. Tier 1 venue.
- **`docker/for-mac#6120`**, "Docker process doesn't free up memory, macOS, Apple Silicon,
  Virtualization.framework". OPEN since 2022-01-03, last updated 2026-05-01. Tier 1 venue,
  relevant to memory retention, **not** to MCP.
- **`docker/for-mac#6128`**, high memory usage. **CLOSED 2022-06-13.** Surfaced by search;
  four years stale; do not cite.
- Tier 2/3 guidance that 8 GB to Docker on a 16 GB M-series Mac is workable but requires
  watching host pressure: oneuptime.com, published **2026-02-08**.

No source, at any tier, documents MCP timeouts *caused by* memory pressure on 16 GB Apple
Silicon. That specific link remains unsupported.

---

## PHASE 4: Status of the two load-bearing issues

| issue | prior report said | verified state (2026-08-23) |
|---|---|---|
| `anthropics/claude-code#65643` | open, Windows, no staff reply, no fix | **VERIFIED.** OPEN. Created 2026-06-05, updated **2026-08-19**. Title: "[BUG] Claude Desktop (Windows): MCP tool calls hard-terminated and bridge wedge after repeated timeouts". Labels `bug`, `platform:windows`, `area:mcp`, `area:desktop`. 8 comments, **every one `authorAssociation: NONE`**, so zero maintainer engagement. No linked fix. |
| `docker/mcp-gateway#412` | open | **VERIFIED.** OPEN. Created 2026-02-14, updated **2026-07-14**, 1 comment. "Streamable HTTP sessions are unstable, causing clients without auto-reconnect to fail". |
| `docker/mcp-gateway#312` | open | **VERIFIED.** OPEN. Created 2025-12-22, updated 2026-02-04. **STALE, 200 days.** |

Note `#65643`'s title and labels scope it to **Claude Desktop on Windows**, `area:desktop`.
It is not a Claude Code issue.

### Versions: prior report is stale, this machine is fully current

| component | prior report | installed here |
|---|---|---|
| Docker Desktop | "latest is 4.87.0 (Aug 17 2026)" | **4.87.0**, matches |
| `docker mcp` plugin | "around v0.42.x (v0.41.0 latest tag vs v0.42.2 bundled)" | **v0.43.3**, released **2026-07-16**, which is the newest release in `docker/mcp-gateway` |
| Docker Engine | not stated | 29.7.2 |

**There is no version to upgrade to.** `#412` is open with no fix, and the installed gateway
plugin is already two minor versions past what the prior report described. Its
"if Anthropic ships a fix on #65643, re-enable" trigger has not fired.

---

## PHASE 5: Real sbx numbers

### Verdict: **cold-start UNCONFIRMED; the memory-competition risk is REAL and contraindicates sbx on this machine**

**Cold start latency: no measured figure found at any tier.** Searched; every hit describes
architecture, none benchmarks it. The prior report asserts none either, so nothing is refuted,
but nothing supports a latency claim.

**Memory: sbx defaults to 50% of host RAM (max 32 GiB).** Corroborated across multiple
independent tier 2/3 2026 write-ups (ajeetraina.com, msbiro.net, andrewlock.net,
learn.arm.com). No tier 1 confirmation obtained: `docs.docker.com/ai/sandboxes/` and
`/ai/sandboxes/architecture/` were both fetched and **neither states a default**.

**Source contradiction, reported not resolved.** `docker/sbx-releases#56` (tier 1),
created **2026-02-09**, CLOSED, updated 2026-04-21, states: "the memory limit for Docker
Sandbox is hardcoded at around 4 GB". That contradicts the 50% figure. Most likely a version
change (hardcoded 4 GB early 2026, later percentage-based with `--cpus` / `--memory` flags,
which is consistent with the issue being closed), but that reconciliation is **inferred, not
sourced**. Treat any sbx memory number as version-dependent.

**Phase 5.2, do Docker Desktop's VM and sbx compete?** On the stated defaults, **yes, and
severely on this hardware.** Docker Desktop's VM already holds 7.75 GiB of 16 GB at its own
50% default. An sbx microVM at *its* 50% default would target another ~8 GB, i.e. the two
would jointly target essentially all physical RAM, on a machine already running ~8.5 GB of
swap. Tier 2/3 sources also state sandboxes have **no swap**, so processes are OOM-killed at
the limit. A tier 1 user report on `docker/sbx-releases#56` describes exactly this outcome:
"Claude crashed 20+ times yesterday because I was trying to do too much in the same sandbox"
(user comment, so tier 3 content in a tier 1 venue).

---

## Consolidated verdict table

| # | Claim in the prior report | Verdict | Source, dated |
|---|---|---|---|
| 1 | Root cause is the Claude Desktop client-side bridge defect #65643 | **REFUTED** for both 2026-08-22 episodes | `Docker.log` + `mcp-server-*.log`, read 2026-08-23 |
| 2 | GitHub and Desktop Commander failed simultaneously | **REFUTED** | 261 events, 2026-07-03 to 2026-08-22; 0 co-clusters at 10 s and 60 s |
| 3 | The #65643 signature (`-32001`, +4:00 cancel) | **ABSENT** from this machine | 0 hits across `mcp.log`, `mcp1.log`, 24 per-server logs |
| 4 | Desktop Commander is a non-Docker stdio child of Desktop | **VERIFIED**, different mechanism (Desktop *extension*), and it is a *remote* connector on Claude Code | `Claude Extensions/`, `~/.claude.json`, 2026-08-23 |
| 5 | Move Claude Desktop's GitHub to the hosted remote connector | **REFUTED** | install-claude.md `fab5fc5ff`, 2026-06-26: "Use the local Docker setup instead" |
| 6 | "Recommended path does not require Docker Desktop at all" | **SPLIT**: true for Claude Code, false for Claude Desktop | same doc, section structure |
| 7 | (omitted by the prior report) GitHub documents a Desktop + Docker-MCP incompatibility | **NEW, VERIFIED** | same doc, Claude Desktop section warning |
| 8 | #65643 open, Windows, no staff reply | **VERIFIED** | `gh issue view`, updated 2026-08-19 |
| 9 | #412 and #312 remain open | **VERIFIED**, #312 stale 200 days | `gh issue view`, 2026-08-23 |
| 10 | Gateway plugin "around v0.42.x" | **STALE**; installed is v0.43.3, the newest release | `docker mcp version`; `gh release list`, 2026-07-16 |
| 11 | Docker Desktop latest is 4.87.0 | **VERIFIED**, and installed | `Info.plist`, 2026-08-23 |
| 12 | Install sbx for Claude Code isolation | **CONTRAINDICATED here** | sbx and Docker Desktop both default to 50% of a 16 GB host |
| 13 | sbx cold start / RAM footprint | **UNCONFIRMED**, no measured figure at any tier | searched 2026-08-23 |
| 14 | Memory pressure is a candidate cause | **condition real, cause unsupported** | 114 MB free, 8.5 GB swap, **zero** failures today |
| 15 | (new) Actual cause: Docker daemon down at spawn time | **ESTABLISHED** | `Docker.log`: terminated 2026-08-21 23:28, launched 2026-08-22 22:14:50 |

---

## What changes about the fix

The prior report's Stage 1 (restart Desktop, trim servers) targets a wedge that leaves no
trace in these logs. Its Stage 2 (move Desktop's GitHub to hosted) is the change GitHub's own
guide tells you not to make. Its Stage 3 (install sbx) would add a second VM defaulting to
half of an already-swapping 16 GB machine. Stage 4 (W&B) is moot on Claude Code: W&B is
already wired twice, as an HTTP server under the `/Users/josie` project scope in
`~/.claude.json` and as a stdio launcher in `.mcp.json`, and it connected in this session.

What the evidence actually supports is narrower and cheaper. The failures were Docker
cold-start races, and **9 of the 11 GitHub containers belong to Claude Code**, which is the
one surface where GitHub officially supports a Docker-free remote transport.

## Updated recommendation

**Move only the Claude Code GitHub server (`repo-tools`) to the GitHub-hosted HTTP endpoint,
and change nothing else.**

That single change removes the Docker daemon from the GitHub path on the surface that
generates ~9 of the 11 containers, eliminates the cold-start race that produced both measured
failures, and drops the per-session container spawn entirely. It is the path GitHub documents
for Claude Code, and Claude Code 2.1.237 is well past the 2.1.1 minimum.

Explicitly do **not**: touch Claude Desktop's `github` entry, because GitHub's guide directs
Desktop users to Docker and says the remote server's OAuth requirement is unsupported there;
remove `MCP_DOCKER` as a fix, because it is already absent from Claude Code and removing it
from Desktop would not take GitHub off Docker (the Desktop `github` entry is a separate direct
`docker run`); or install sbx on this machine at default resources.

Separately and regardless: the `gho_` GitHub token sits in cleartext in `~/.claude.json`
under `repo-tools.env`, and it was echoed to a terminal during this investigation. **Rotate
it.** This is consistent with the existing credential-exposure record rather than a new
finding.

### What would overturn this

A single flapping episode captured with Docker Desktop **verified up beforehand**
(`docker info` succeeding), showing `-32001` in `~/Library/Logs/Claude/mcp.log`. That would
move the diagnosis back to `#65643` and make this file's conclusion wrong. Nothing in
51 days of logs shows it yet.
