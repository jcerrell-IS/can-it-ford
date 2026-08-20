# MCP, plugin and skill audit, 2026-08-20 (SECOND PASS)

Measured live 12:34-12:52 BST, revised 13:04-13:20 BST after an adversarial recheck.
Readable version: https://claude.ai/code/artifact/097315d3-62f8-441d-ae31-d24dac1c5ae0

**THE FIRST VERSION OF THIS FILE CARRIED FOUR ERRORS AND ITS REMOVAL COMMANDS WERE
WRONG.** Previous text preserved at `MCP_CONNECTOR_AUDIT_2026-08-20.md.bak-v1-wrong-scopes`.
Do not run commands from that copy.

Does NOT supersede `docs/MCP_CONNECTOR_AUDIT_2026-08-18.md`, a different question.

## ERRATA from the first pass

1. **SCOPE LABELS WERE WRONG, 5 of 7 removal commands were wrong.** I read
   `~/.claude.json -> projects -> mcpServers` as *project* scope. Claude Code calls it
   **local**. *Project* means `.mcp.json`. Verified: `claude mcp get undermind` returns
   "Scope: Local config (private to you in this project)".
   Precedence measured across the fleet: **local > project > user**.
   `claude mcp remove scite -s project` would have deleted the `.mcp.json` copy the same
   document told you to KEEP.
2. **"20 servers connected" was off by one.** 19 connected + 1 needs auth = 20 rows.
3. **HF "PRO ends 2026-09-01" was an OVERCLAIM.** `whoami-v2` has NO `cancelAtPeriodEnd`,
   NO `plan`, NO `subscription` field, so it cannot distinguish renewal from lapse. What
   it does carry, and what the first pass missed: **`billingMode: prepaid`**, which is
   consistent with a lapse but is not proof. Check the billing page, not the API.
4. **W&B "reports: 0" was tabulated without being measured.** Now measured via the
   `allViews` GraphQL query: it IS 0. Right number, wrong method. Treat as newly
   measured, not previously confirmed.

**SURVIVED THE RECHECK:** the 591 SUs / 2026-09-30 figure came from a ~12-day-stale
cache, so it was re-run live against Vista and reproduces exactly (`BCS20003 591
2026-09-30`). Connected-is-not-authorized, the eight duplicate services, and all HF repo
states hold. The live check also surfaced **`/home1` on Vista at 89.52% full**
(20.8 of 23.3 GB), which the cache hid.

## The distinction that outlives everything else here

**CONNECTED IS NOT AUTHORIZED, and one command cannot tell you both.**
Same minute: `claude mcp list` reports `scite: OK Connected`, and the session reports
scite among servers requiring authentication before their tools can be used. Transport
handshake succeeded; OAuth grant did not. The `connector-router` skill's
OAUTH-GATED / DEAD-HEADLESS row is **STILL CORRECT**. Use `claude mcp list` to find
servers that fail to START, never to conclude one is USABLE.

## Layer 1: MCP. 19 connected, 1 needs auth, 8 services duplicated

| service | defined in | winner | keep | CORRECT command |
|---|---|---|---|---|
| hf-mcp-server | local only | local | delete, `hf` works | `-s local` |
| zotero | user + local | local | local (absolute path) | `-s user` |
| undermind | user + local | local | user | `-s local` |
| elicit | user + local | local | user | `-s local` |
| overleaf | user + local | local | user | `-s local` |
| scite | local + project | local | project (`.mcp.json`) | `-s local` |
| deepwiki | user + project | project | project | `-s user` |
| context7 | user + plugin | both load | user | plugin removal, not `mcp remove` |

OAuth tokens are stored per endpoint (Claude Code says this itself), so authorizing the
copy you can see does not authorize the copy that wins. Zotero's two definitions are
genuinely different endpoints (`zotero-mcp` vs `/Users/josie/.local/bin/zotero-mcp`), so
re-verify its auth after removal.

## Layer 2: PLUGINS. Missed entirely in the first pass

11 distinct plugins, **31 install entries**.

**`context7` has 20 install entries: 1 project + 19 LOCAL, ONE PER GIT WORKTREE.**
Every worktree re-installed it against its own path. This is the mechanism behind the
context7 duplication, and it reproduces every time you branch. Anything installed at
LOCAL scope replicates the same way.

**~9.9 MB of orphaned temp clones** in `~/.claude/plugins/cache/` from 2026-08-18
05:08 UTC: `temp_git_*_1ab17i` (6.3 MB, carries its own `skills/` and `hooks.d/`),
`temp_git_*_u19eoe` (3.4 MB), `temp_subdir_*.clone` (180 KB). Failed-install debris.

**The `github` plugin is installed at USER scope**, so it loads in every project, in
direct contradiction of the project's own standing note to use `gh` and `git` instead.

3 marketplaces registered: claude-plugins-official, claude-community, claude-code-plugins.

## Layer 3: SKILLS. 43 local

| scope | count | problem |
|---|---|---|
| project `.claude/skills/` | 15 | correct, and these travel with worktrees |
| user `~/.claude/skills/` | 28 | loads in every project |
| shadowed in both | 5 | project wins; user copy is dead weight that can drift |
| off-topic, user scope | 13 | coursework and life admin in every research session |

Shadowed 5: `bug-triage-protocol`, `claude-code-prompt-install`, `connector-router`,
`mpm-render-pipeline`, `panel-audit-dispatch`. Two copies of a file encoding standing
rules is the divergence hazard the CLAUDE.md constitution rule exists to prevent, one
level down.

Off-topic 13: `sci-30-*` (five), `casio-exam-mastery`, `fhs-010-course-assistant`,
`claremont-life-navigator`, `job-application-tailor`, `canva-design-assistant`,
`youtube-media-processor`, `email-comms-hub`.

**OPEN, not diagnosed:** an `anthropic-skills:` namespace duplicates ~11 project skills
in the session listing, and `find` locates no such directory under `~/.claude` or the
repo. Arriving from the managed side, not removable by local edit.

## Layer 4: claude.ai connectors

UUID-addressed connectors duplicate local servers: Google/Zapier (TWO byte-identical,
~62 tools each), Scholar Sidekick (3 copies), Undermind (2), HF (3), Desktop Commander
(2), Figma / pdf-viewer / deepwiki / elicit / consensus / wolfram (2 each).

Order of 170 duplicate tool schemas. **COUNTED BY READING THE SESSION TOOL LISTING, NOT
COMPUTED FROM A MANIFEST.** Direction is not in doubt; the total is soft. Count properly
before quoting.

**OPEN, not diagnosed:** `.claude/settings.json` sets `"disableClaudeAiConnectors": true`
and the UUID connectors are present anyway. Do not restate as a Claude Code bug
without testing.

## Accounts

### Hugging Face
`isPro: true`, `billingMode: prepaid`, `periodEnd` 2026-09-01, `cancelAtPeriodEnd`
ABSENT. HF Jobs is LIVE and already used (job `6a83fa07e55292eada79bfb4`, 2026-08-18,
`python:3.12`, tensorboard).

**HF Jobs is compute that does not spend Vista SUs.** 591 SUs confirmed live, expiring
2026-09-30, on a machine where most node-hours go to interactive `idev`. Every CPU-only
analysis pass is a candidate to move.

Repos needing a decision: `spaces/can-it-ford-demo` is PUBLIC with NO_APP_FILE.
`datasets/can-it-ford-sweep-v1` and `can-it-ford-speed-surface` are PUBLIC while the
derived-hull licence question (register E8) is unresolved. Deleting does not unpublish.

### Weights & Biases
107 runs (88 with no `job_type` or `group`), 1 of 4 canonical stores versioned, 0 sweeps,
0 reports (measured this pass), 0.6 MB storage, `isTeam: true`, `memberCount: 1`,
`defaultAccess: PRIVATE`.

**Sweeps are the pointed gap.** The grid_density / depth / velocity space already exists
implicitly in scripts and run names (`sweepV_g64_v3p0`). Declaring it as a W&B sweep costs
one YAML file, re-runs nothing, changes no physics, and buys the parameter-importance and
parallel-coordinates views that make the non-monotone g48/g64/g96 displacement legible.

## The rotation

Three things behave differently in a worktree:
- **Plugins re-install per worktree** (19 context7 entries prove it).
- **Project skills travel, user skills do not carry project context.** Argument for
  pushing the 5 shadowed skills DOWN to project scope and deleting the user copies.
- **A worktree carries the CLAUDE.md from its branch point.** Same is true of a skill
  file; duplicated skills make it worse.

Shape: **project scope for can-it-ford specifics, user scope for genuinely cross-project
tools only, local scope for nothing you intend to keep.** Local is the scope that
silently multiplies.

## Fix sequence

TWO OTHER SESSIONS WERE LIVE IN THIS REPO THROUGHOUT BOTH PASSES. Config is shared.
Run when the fleet is quiet.

```
claude mcp remove hf-mcp-server -s local
claude mcp remove undermind     -s local
claude mcp remove elicit        -s local
claude mcp remove overleaf      -s local
claude mcp remove scite         -s local
claude mcp remove deepwiki      -s user
claude mcp remove zotero        -s user
claude mcp list                 # expect 19 rows, 0 needing auth
```

Then, not scriptable:
- inspect and clear `~/.claude/plugins/cache/temp_*`
- delete the 5 shadowed user-scope skills; move the 13 off-topic ones out
- disable duplicated claude.ai connectors in claude.ai connector settings
- update `.claude/skills/connector-router/SKILL.md` with connected-vs-authorized
- decide the HF billing question before 2026-09-01

## Do not add

- A seventh literature tool. The constraint is ROUTING, not coverage.
- GitHub MCP. The measured note stands, and the plugin is currently installed at user
  scope in contradiction of it.
- Chat-surface connectors (Slack, Otter, Google Calendar). Not reachable from Claude Code.

## Reproduce

```
claude mcp list
claude mcp get <server>            # the scope check the first pass skipped
scripts/tacc.sh --status
scripts/wb --py analysis/wb.py doctor
python3 -m json.tool ~/.claude/plugins/installed_plugins.json
```
