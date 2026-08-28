# canitford-base sandbox kit

A Docker Sandboxes Kit that gives an `sbx` session the same MCP servers, memory
and skills as the host Claude Code setup, without handing it host privileges.

Built and validated against **sbx v0.39.0 (def8cb0)** on 2026-08-23.

```
sandbox/
├── canitford-kit/
│   ├── spec.yaml                        kit-spec v2, validates clean
│   └── files/home/.claude/CLAUDE.md     the 106-line global rules, verbatim
├── provision.sh                         host-side: secrets, then create
├── verify_sandbox.sh                    runs inside a fresh session
└── README.md
```

```bash
sh /Users/josie/can-it-ford/sandbox/provision.sh
```

Then:

```bash
sbx exec canitford -- sh /workspace/sandbox/verify_sandbox.sh
```

---

## Five premises in the brief that live state contradicted

These were checked live, not recalled. Each one changed the design.

| Brief said | Live state | Consequence |
|---|---|---|
| "CLAUDE.md is 603+ lines" | **1024 lines** | Cosmetic, but the drift constant in `verify_sandbox.sh` had to be measured, not copied. |
| "There is no separate `~/.claude/CLAUDE.md` in use, don't re-derive this" | **It exists: 106 lines of global working rules** (`sha256 6b2d14ac...`) | This is the one file that genuinely needed shipping. It is the only thing in `files/`. Had I taken the instruction not to re-derive it, the sandbox would have silently lost every global rule: the no-em-dash rule, verification discipline, shell discipline, the Safe Resume protocol. |
| Auto Memory is at `~/.claude/projects/can-it-ford/memory/` | **That path does not exist.** The real one is `<repo>/.claude/memory/`, 118 files | It is inside the workspace, so it arrives by bind mount. Nothing needed copying. |
| "user-level skills at `~/.claude/skills/` do NOT automatically travel into a sandbox" | **Exactly inverted.** All 28 user-level skills are already in the sbx store and sbx mounts it at `~/.claude/skills`. The 35 in the store are those 28 plus 7 plugin skills. | The real gap is the other direction: **10 repo-scoped skills** are absent from the store. But they are under `<repo>/.claude/skills/`, so the bind mount already delivers them. Net gap after this kit: zero. |
| Reference doc at `docs.docker.com/ai/sandboxes/kits/` | **HTTP 404** | Schema came from the kit reference embedded in the sbx binary, then every field was confirmed by running `sbx kit validate`. |

The 10 repo skills missing from the sbx store, for the record: `directory-provenance-audit`, `flood-mpm-debugging-reference`, `geoelements-tech-reference`, `git-history-rewrite`, `mpm-technical-deep-reference`, `provenance-audit`, `research-corpus`, `splat-dataset-prep`, `tacc-terminal-and-file-transfer`, `wandb-ops`. They reach the sandbox via the workspace mount. If you ever switch to `--clone` or a non-repo workspace, run `sbx skills import` to put them in the store too.

---

## The wandb decision, resolved rather than deferred

The brief asked for the uvx stdio launcher and flagged the hosted endpoint as a
maybe. Two measurements inverted that.

**1. The obvious way to "replicate the launcher" is the one thing that breaks the
security model.** `sbx mcp add --command` exists, but its own help says the
command "runs as a subprocess on the **HOST**, outside the sandbox" with "your
host user's full permissions". Wiring `scripts/wandb_mcp_launch.sh` that way
would put an uvx-fetched server on the host with full privileges. That is the
exact exposure this kit is meant to reduce, so it is rejected outright.

**2. The hosted endpoint is live and uses the auth scheme the proxy can actually
handle.** Probed 2026-08-23:

```
POST https://mcp.withwandb.com/mcp
-> {"error":"Authorization required",
    "message":"Please provide your W&B API key as a Bearer token"}
```

A Bearer header is a plain string, so an `sbx secret set-custom` placeholder can
be substituted into it. The uvx path **cannot use a placeholder at all**: the
wandb client authenticates with HTTP Basic, `auth = ("api", self.api_key)` at
`wandb/sdk/internal/internal_api.py:290` and `:343`, which base64 encodes the key
on the wire, where a literal placeholder never matches.

So the hosted endpoint is not merely simpler here, it is the only one of the two
that is compatible with keeping the real key out of the sandbox.

**Known limitation this leaves.** The wandb MCP server works. The `wandb` Python
library called from inside the sandbox will **not** authenticate, for the base64
reason above. If you need library calls in-sandbox, you have to inject the real
key (`sbx create -e WANDB_API_KEY=...`), which puts a live credential inside the
container. That is a deliberate trade, not an oversight. Do not make it silently.

**If you want the uvx path anyway**, add `pypi.org` and `files.pythonhosted.org`
to `permissions.network.allow`, add a `setup.install` step that runs
`uvx --from git+https://github.com/wandb/wandb-mcp-server --with 'mcp[cli]<2'`
(the `mcp[cli]<2` pin is load-bearing, see the comment in
`scripts/wandb_mcp_launch.sh`), and accept the real-key injection above. It runs
inside the sandbox, so it is still contained. It is just strictly worse than the
hosted endpoint on every axis measured here.

---

## The GitHub decision

Plain `gh`, as asked, and no GitHub MCP server at all. `verify_sandbox.sh`
asserts that zero GitHub-ish MCP servers are registered, which is the
`MCP_DOCKER` and `repo-tools` duplication the brief wanted avoided.

The token comes from the built-in `github` service secret, provisioned as:

```bash
sbx secret set github --command 'gh auth token'
```

That form is the sbx binary's own documented example. It re-reads the macOS
keyring on demand, so no token is stored on disk or baked into the kit.

**One expected wrinkle.** `github` is proxy-injected: the token is swapped into
outbound `api.github.com` requests and is never present inside the container. So
`gh auth status` may report no local credential while `gh api user` works fine.
`verify_sandbox.sh` tests both and treats that combination as a warning, not a
failure. Note also that the host `gh` account is **jcerrell-IS**, not
`josiecerrell`, which is the HF username.

---

## Egress allowlist

Seven domains, no "Balanced" profile:

```
github.com  api.github.com  raw.githubusercontent.com
huggingface.co
mcp.withwandb.com  api.wandb.ai  wandb.ai
```

The six Anthropic domains are not repeated because the base `claude` agent kit
already supplies them (confirmed with `sbx policy inspect` against the existing
`canitford-test` sandbox).

Excluded on purpose, each with the cost it buys:

- `codeload.github.com`, `objects.githubusercontent.com`: `git clone` over https
  and `gh release download` will fail. `gh api` does not need them.
- `pypi.org`, `files.pythonhosted.org`: no pip or uvx inside the sandbox. This is
  what makes the "no real key in the container" property hold for wandb.
- `cdn-lfs.huggingface.co`, `*.hf.co`: `hf download` of real weights will fail.
- The hf CLI is consequently **not installed**, since installing it needs pypi.
  `verify_sandbox.sh` falls back to `curl https://huggingface.co/api/whoami-v2`,
  which asserts the same identity over an already-allowed domain. If you want the
  real CLI, add the two pypi domains and a `pip install huggingface_hub` step.

`verify_sandbox.sh` step 7 proves the allowlist is real by requiring that
`api.github.com` succeeds **and** `pypi.org` fails. An untested allowlist is a
comment.

---

## Open decisions for you

**1. TACC (`vista.tacc.utexas.edu`, `ls6.tacc.utexas.edu`). Currently blocked.**
Two reasons to leave it that way, one of which is new. Your own note is that MFA
does not work over non-interactive SSH. On top of that, the sbx policy layer is
an HTTP/HTTPS proxy and the rules are `host:port` pairs, so it is not clear SSH
on port 22 is proxied at all rather than simply dropped. Keeping TACC work on the
host through `scripts/tacc.sh` also matches the architecture the 2026-08-19 audit
already endorsed. Say the word and I will add them plus test whether port 22
egress is even expressible here.

**2. Bind mount versus `--clone`. Currently bind mount.** This is the bigger one.
A bind-mounted sandbox writes straight through to `/Users/josie/can-it-ford`, so
a sandboxed agent can modify the live working tree that other sessions are using,
and the concurrency hazard CLAUDE.md documents applies unchanged. `--clone` gives
the agent an in-container copy and returns commits via a `sandbox-<name>` git
remote. Given a shared tree with other live sessions, `--clone` is arguably the
correct default. It is not the default here only because it changes your git
workflow, which is your call, not mine.

**3. The global CLAUDE.md snapshot will drift.** `files/home/.claude/CLAUDE.md`
is a copy taken at `sha256 6b2d14ac...`. `verify_sandbox.sh` compares against that
hash and warns on mismatch. Refresh with:

```bash
cp /Users/josie/.claude/CLAUDE.md /Users/josie/can-it-ford/sandbox/canitford-kit/files/home/.claude/CLAUDE.md
```

then update `HOST_GLOBAL_SHA` in `verify_sandbox.sh`.

---

## What is genuinely unverified

- **The base image contents.** `docker/sandbox-templates:claude-code` was not
  pulled locally, so whether it ships `gh`, `curl`, `jq` or `hf` is unknown. The
  kit's first install step writes a probe to `~/.canitford-toolprobe` and
  `verify_sandbox.sh` prints it. First run tells you the truth; adjust then.
- **No sandbox has been created with this kit.** The kit validates and inspects
  correctly (`7 allow, 4 variables, 3 install, 1 home file`), but I did not run
  `provision.sh`, because it writes secrets to the sbx store and creates a
  container, and neither is mine to do unasked. Every runtime claim in
  `verify_sandbox.sh` is a prediction until you run it.
- **The `claude mcp add --header` expansion path.** The header is expanded by the
  shell at install time to the placeholder literal, which is what the proxy
  expects. That is the intended mechanism but it is untested end to end here.
  Step 3 of the verify script is what catches it if wrong.

## Security note

The OX Security STDIO finding in the brief is exactly why step 2 of the wandb
decision matters: `sbx mcp add --command` would have kept a stdio MCP server on
the host with full user privileges. Both MCP servers in this kit are remote HTTP,
so no MCP server process runs on the host or in the sandbox at all, and no real
credential is present in the container. The remaining host-privilege exposure
from roughly 13 parallel panes is unchanged by this kit; the kit only ensures a
sandboxed session is not a fourteenth.
