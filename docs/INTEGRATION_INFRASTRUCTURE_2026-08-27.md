# Integration infrastructure: HF, W&B, hooks, Vista seam

Written 2026-08-27, then destroyed and rewritten the same night. An earlier copy of
this file was removed by a concurrent session running `git reset --hard` plus
`git clean -fd` while it was still untracked. This version is committed, and it
supersedes the destroyed one, which nobody else read.

Routed to `docs/` rather than into `CLAUDE.md` on purpose. The "WHERE A NEW FINDING
GOES" rule says the constitution carries standing rules and environment truth, not
dated findings, because a worktree carries the `CLAUDE.md` from its own branch point.
Nothing below changes a standing rule.

Claims are tagged. **[CONFIRMED]** was measured by the command shown. **[DOC]** was
read from a primary document. **[INFERRED]** is reasoning, not measurement.

## 1. Hugging Face repo state [CONFIRMED] 2026-08-27

Anonymous `curl` against `https://huggingface.co/api/<repo>`, so this is what a
logged-out visitor sees.

| Repo | Anon HTTP | State |
|---|---|---|
| `spaces/josiecerrell/can-it-ford` | 200 | `runtime.stage = RUNNING`, public. Canonical. |
| `spaces/josiecerrell/can-it-ford-demo` | 200 | `runtime.stage = NO_APP_FILE`. Cannot run. Dead. |
| `datasets/josiecerrell/can-it-ford-results` | 401 | Private. Simulation data archive. |
| `datasets/josiecerrell/can-it-ford-speed-surface` | 200 | Public, `cardData.license = cc-by-4.0`. |
| `datasets/josiecerrell/can-it-ford-sweep-v1` | 200 | Exists, public. Superseded, do not write to. |
| `models/josiecerrell/can-it-ford-sweep-v1` | 200 | Exists, public. Superseded, do not write to. |

`sweep-v1` being two separate repos, a dataset and a model, is confirmed rather than a
duplicate listing.

## 2. The live Space MCP endpoint, and why the obvious test gets it backwards

**A `curl -sI` probe ranks these endpoints in exactly the wrong order.** `-I` sends
HEAD, which no MCP endpoint implements. [CONFIRMED]:

| URL | `curl -sI`, HEAD | POST `initialize` |
|---|---|---|
| `/gradio_api/mcp/http` | **405**, `allow: GET, POST, DELETE` | **200**, valid JSON-RPC result |
| `/gradio_api/mcp/` | **405**, `allow: GET, POST, DELETE` | **200**, valid JSON-RPC result |
| `/gradio_api/mcp/sse` | **200**, `text/event-stream` | **404** |

A HEAD probe would have selected `/sse`, the one path that does not work. The `allow:`
header on the 405 is itself the evidence that POST is accepted. Test an MCP endpoint
with the method MCP uses.

The server settles the question in its own 404 body, quoted verbatim:

    Path '/gradio_api/mcp/sse' not found. The MCP HTTP transport is available at /gradio_api/mcp.

`/gradio_api/mcp` with no trailing slash returns **307** to
`https://josiecerrell-can-it-ford.hf.space/gradio_api/mcp/` [CONFIRMED], so the
trailing-slash form is what is pinned, to avoid depending on a client following a
redirect on POST.

Handshake against it returns `protocolVersion 2025-06-18`, `serverInfo {"name": "Can
It Ford", "version": "1.29.1"}`, and no `mcp-session-id` header, so the server is
stateless. `tools/list` returns exactly **one** tool, `can_it_ford_evaluate`,
described as evaluating verdicts "for a STATIONARY vehicle at a given depth and
velocity". That stationary scope is correct and matches the standing rule that the
AR&R and Shand thresholds describe a stationary vehicle.

Landed in `.mcp.json`, commit `c62c28d`:

    "can-it-ford-live": {
      "type": "http",
      "url": "https://josiecerrell-can-it-ford.hf.space/gradio_api/mcp/"
    }

## 3. W&B badge is broken for every public visitor [CONFIRMED] 2026-08-27

`README.md:6` carries a W&B badge, repeated at `README.md:176`, linking to
`wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford`. That project is not
readable anonymously.

| Probe | Result |
|---|---|
| Anon GraphQL, `jcerrell29-claremont-mckenna-college/can-it-ford` | `{"data":{"project":null}}` |
| Anon GraphQL, `jcerrell29/can-it-ford` | `{"data":{"project":null}}` |
| Anon GraphQL, `stacey/estuary`, known public, CONTROL | returns a real record |
| Anon GraphQL, a nonexistent project, CONTROL | `{"data":{"project":null}}` |

The public control proves the anonymous path works, so `null` is not an artifact of
being logged out. The nonexistent control proves `null` means "not visible to you".
The project demonstrably exists, 174 runs as of 2026-08-26.

**A browser check misses this.** `https://wandb.ai/<entity>/<project>` returns
**HTTP 200 even for a project that does not exist** [CONFIRMED], so the badge renders
and clicks through with no error code, and only the login wall or the probe above
reveals it.

**UNRESOLVED, and deliberately so.** Two fixes exist and they differ in what they
publish: make the W&B project public, which exposes every run and artifact in it
permanently and is not undone by re-privating since the linking repo is already
public, or leave it private and change the badge. `README.md` was not modified.

## 4. Hooks: two claims corrected, one gap closed [CONFIRMED] 2026-08-27

An earlier report described `audit_integrity_guard.py` and `stop_signal_and_check.sh`
as both "present but unwired". Both halves were wrong.

- **`audit_integrity_guard.py` was already wired**, as `PreToolUse` with matcher
  `Bash|Edit|Write`, and already guarded per the fail-open rule with an existence test
  before invocation. No change was needed and none was made.

- **`stop_signal_and_check.sh` did not exist in this checkout.** A repo-wide `find`
  located exactly one copy, at
  `.claude/worktrees/ctx-census/.claude/hooks/stop_signal_and_check.sh`. It was absent,
  not unwired, and the worktree copy runs a six-section deliverable format check, not
  `register_integrity.py`. Reading a worktree and reporting it as the main tree is the
  known trap here.

A script was therefore written rather than wired, commit `b39325f`, and added to the
`Stop` array **alongside** the existing tmux pane-signal hook, commit `424213d`. Stop
now runs two hooks, verified 1 tmux hook before and 1 after.

It fails open by design: it exits 0 when `CLAUDE_PROJECT_DIR` or the check script is
absent, and never returns nonzero, so it cannot wedge a session. Verified by running
it with a deliberately bogus project dir. `register_integrity.py` takes 580 ms and
currently exits 0 with warnings only. Findings append to
`~/.pane_signals/register_integrity.log`; only a BLOCK count reaches stderr.

Still true: hooks in `~/.claude/settings.json` at user level do not reach GitHub
Actions or cloud runners. Anything that must run in CI belongs in the repo-level
`.claude/settings.json`.

## 5. CARRIED, UNVERIFIED. Do not cite as measured.

Not re-measured. Useful, unproven here.

**W&B offline sync on Vista.** Premise that Vista GPU nodes have no outbound internet
was not tested. `export WANDB_MODE=offline`, then
`sbatch --dependency=afterok:$SLURM_JOB_ID sync_wandb.sh` running
`for d in wandb/offline-run-*; do wandb sync "$d"; done`. See
`docs/TRACKIO_OFFLINE_VISTA_2026-08-27.md` for why Trackio can drop the dependent job.

**GitHub Actions.** `anthropics/claude-code-action@v1` automation mode via
`workflow_dispatch`, `schedule` or `push`. Secrets `ANTHROPIC_API_KEY` and
`CLAUDE_GITHUB_APP_TOKEN`. A hosted runner has no route into the TACC filesystem.

**Claude Code headless.** `claude -p "prompt" --allowedTools "Read,WebSearch"
--output-format json`, bounded with `--max-turns 8`. The workspace trust dialog is
skipped under `-p`, which matters on a shared filesystem.

**HF Hub webhook to an HF Job.** Watch `can-it-ford-results` for `repo.update`, payload
arrives as `WEBHOOK_PAYLOAD`.

**Provenance framing**, from an Undermind sweep of 187 papers not re-run here: treat
every Vista job as a provenance-bearing object, recording job ID, git SHA, input
checksums and hardware identity at run time rather than reconstructing afterward. HF,
W&B and GitHub Actions are dissemination layers, not results stores.
