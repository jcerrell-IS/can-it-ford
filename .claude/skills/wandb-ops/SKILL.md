---
name: wandb-ops
description: Use for ANY Weights & Biases work in can-it-ford: logging a run, versioning data as an artifact, publishing a report to wandb.ai, querying the 106 existing runs, or debugging W&B auth. Trigger on "log this to W&B", "wandb", "weights and biases", "version this dataset", "make a report", "which runs did X", "wandb says 401", or any request to publish results to wandb.ai.
---

# W&B operations for can-it-ford

## The account, measured 2026-08-20

| Fact | Value |
|---|---|
| user | `jcerrell29` |
| entity | `jcerrell29-claremont-mckenna-college` |
| project | `can-it-ford` (the only project) |
| runs | 106, all `finished` |
| runs with tags | 97 of 106 |
| runs with `group` and `job_type` | 18 of 106 |
| user artifacts | 1 (`failure_modes_classified`), created when this wiring was verified |
| sweeps | 0 |

Re-measure before quoting any of these. `scripts/wb --py analysis/wb.py doctor` prints
all of them live.

## Never do these

- **Never put the API key in a tracked file.** This repo is PUBLIC. GitHub has served a
  removed key by SHA even after a `filter-repo` purge. The key lives in `~/.netrc` only.
- **Never read `~/.netrc` directly.** `.claude/settings.local.json` carries an explicit
  `Read(//Users/josie/.netrc)` deny. `scripts/wandb_env.sh` extracts the key in a
  subprocess at launch, which is a different thing and is how `wandb` and `curl -n`
  already work.
- **Never call a bare `wandb`.** It is NOT on PATH. It lives in
  `~/.venvs/canitford-mpm/bin/wandb`, so `which wandb` reports "not found" and a bare call
  fails. Go through `scripts/wb`.
- **Never `import pandas` in `analysis/wb.py`.** That venv has numpy, scipy and matplotlib
  but no pandas and no pyarrow. The helper is stdlib `csv` plus numpy by design.

## Commands

```
scripts/wb --doctor                       # full chain: binary, key, auth, entity, uvx, helper
scripts/wb login --verify                 # identity only
scripts/wb --py analysis/wb.py doctor     # account state: runs, tags, artifacts
scripts/wb --py analysis/wb.py runs --limit 10 [--tag gated-17]
scripts/wb --py analysis/wb.py artifact-list
scripts/wb --py analysis/wb.py artifact-put --path data/x.csv --name x --type dataset
scripts/wb --py analysis/wb.py artifact-get --name x:latest --out /tmp/x
scripts/wb --py analysis/wb.py log-csv --path data/x.csv --name x
scripts/wb --py analysis/wb.py snapshot   # version every canonical store at once
```

`scripts/wb <anything else>` forwards straight to the real `wandb` CLI with auth set.

## From python

```python
import wb                       # analysis/ must be on sys.path
with wb.run(job_type="analysis", tags=["r10"], group="r10-2026-08-20") as r:
    r.log({"drift_m": 0.041})
    wb.put_artifact(r, "data/all_runs_inventory.csv", "all_runs_inventory", "dataset")
```

`wb.run()` stamps `git_sha` and `git_dirty` into every run's config automatically, so a
run always answers "which code produced this". A DIRTY tree means the run is not
reproducible from its recorded sha; `snapshot` warns on stderr when that happens.

## Run conventions, and why they are not optional

Set `job_type`, `group` and `tags` on every run. Only 18 of 106 existing runs carry
`job_type` or `group`, which is exactly why those runs cannot be grouped or filtered in
the UI and have to be picked out by name. `wb.run()` makes `job_type` a required argument
for that reason.

- `job_type`: what the run did (`gated-backfill`, `load-surface`, `snapshot`,
  `artifact-publish`, `table-publish`, `analysis`)
- `group`: the batch it belongs to (`gated-17`, `speed-surface-2026-08-19`)
- `tags`: engine and scope (`warpmpm`, `L2`, `n_grid_64`, `gated-17`)

Tag the engine. The 17 canonical runs are **warpmpm, not Genesis**, and a mislabelled run
propagates that error into a figure caption.

## Reports go through MCP, not through wb.py

`wandb_workspaces` is NOT installed in the canitford venv, so `analysis/wb.py` cannot
create reports. The W&B MCP server bundles its own copy, so use
`mcp__wandb__create_wandb_report_tool` instead. It is on the `ask` list, not `allow`,
because a report is an outward-facing publish.

## The MCP server

Registered in `.mcp.json` as `wandb`, launched by `scripts/wandb_mcp_launch.sh`. It serves
**22 tools**, measured by handshake on 2026-08-20; the upstream README documents only 16,
so do not treat that README as the tool inventory. Read tools are auto-allowed. The two
write tools (`create_wandb_report_tool`, `log_analysis_to_wandb`) prompt every time.

**The launcher pins `mcp[cli]<2` and must keep doing so.** `wandb-mcp-server` declares
`mcp[cli]>=1.0.0` with no upper bound; uv resolves that to `mcp` 2.0.0, which no longer
ships `mcp.server.fastmcp`, and the server then dies at import with `ModuleNotFoundError`
before serving one tool. If the server ever goes silent, test that first:

```
/opt/homebrew/bin/uvx --from git+https://github.com/wandb/wandb-mcp-server wandb_mcp_server --help
```

Failing there and succeeding with `--with 'mcp[cli]<2'` confirms the same bug.

## Failure modes, in the order they actually happen

| Symptom | Cause | Fix |
|---|---|---|
| `wandb: command not found` | not on PATH, lives in the venv | use `scripts/wb` |
| `401` on any call | key rotated | `scripts/wb login --relogin`, then `scripts/wb --doctor` |
| `wandb_env: no key for api.wandb.ai` | `~/.netrc` block missing or malformed | `scripts/wb login --relogin` rewrites it |
| MCP tools absent after config change | Claude Code caches MCP at startup | restart Claude Code |
| `ModuleNotFoundError: mcp.server.fastmcp` | `mcp` 2.0 resolved | the `<2` pin was dropped, restore it |
| `AttributeError: 'ArtifactCollection' object has no attribute 'versions'` | wandb 0.28.2 uses `.artifacts()` | `_collection_versions()` in `wb.py` handles both |

## Key rotation

The key has rotated at least twice (the one ending `iNbz` is dead, the live one ends
`ipS9`). Rotation is one command and needs no repo change, because nothing in the repo
stores the key:

```
scripts/wb login --relogin      # rewrites ~/.netrc
scripts/wb --doctor             # confirms the new key authenticates
```
