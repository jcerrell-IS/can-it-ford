# SETUP GUIDE: what is built, what you do, in order

Everything in `/Users/josie/can-it-ford/.claude/tooling/` is written and smoke-tested. Nothing here has
been wired into your shared config, because `/Users/josie/can-it-ford/.mcp.json` and
`/Users/josie/can-it-ford/.claude/settings.json` both carry state I should not overwrite. Your steps are
below, shortest-first, each with a verification you can run yourself.

Total hands-on time: about 12 minutes for steps 1 to 4.

**All paths below are absolute.** An earlier version of this guide used
repo-relative paths, and a viewer resolved them against this file's own
directory, producing `.claude/tooling/.claude/settings.json`, which does not
exist. Fixed 2026-08-15.

---

## WHAT IS ALREADY DONE (no action needed)

| File | What it is | Tested |
|---|---|---|
| `mcp_scaffold.py` | zero-dependency MCP stdio server base (Python 3.9, no `mcp` package needed) | yes |
| `corpus_mcp.py` | 6 tools over the 128-artifact research corpus | yes, resolved `65474f37` to 9 copies, 8 readable |
| `tacc_mcp.py` | 6 typed tools for Vista/LS6 with stub detection and auto-`--overlap` | yes, tools list + hostinfo |
| `commit_autoapprove.py` | PreToolUse predicate: grants only provably-safe commits | yes, 6/6 cases correct |
| `dispatch_uniqueness.py` | refuses identical assignments across sessions | yes, ran on all 13 Round-3 files |
| `checks/r7_mirror_control.py` | the metamorphic control, rescued from purgeable `$SCRATCH` | preserved + annotated |
| `frame_review_app.py` | Gradio frame reviewer with flag-to-JSONL | written, needs gradio |
| `MERGE_*.{json,yml}` | paste-ready config fragments | n/a |

The monitor's main-tree baseline was rebaselined after these files landed, so
`/Users/josie/can-it-ford/.claude/tooling/` is expected and will not raise a false alarm.

---

## STEP 1 — Wire the two MCP servers (3 min)

Open `/Users/josie/can-it-ford/.mcp.json`. It currently has four servers:
`deepwiki`, `scite`, `wolfram`, `github`. Add these two **inside** the existing
`mcpServers` object, without touching the four:

```json
"canford-corpus": {
  "command": "/usr/bin/python3",
  "args": ["${CLAUDE_PROJECT_DIR}/.claude/tooling/corpus_mcp.py"]
},
"canford-tacc": {
  "command": "/usr/bin/python3",
  "args": ["${CLAUDE_PROJECT_DIR}/.claude/tooling/tacc_mcp.py"]
}
```

The same text is in `/Users/josie/can-it-ford/.claude/tooling/MERGE_mcp.json` if you prefer to copy it.

**Then restart Claude Code** (MCP servers load at startup only).

**Verify:** in any session, ask for `corpus_inventory`. It should list six roots
with per-root readable counts. If `~/Downloads` shows `PARTIAL/TCC-DENIED`, that
is correct and expected, and is exactly the condition that produced five false
"artifact missing" reports last night.

---

## STEP 2 — Add the commit auto-approval hook (1 min)

**A pre-merged, validated copy already exists**, so you do not have to hand-edit
230 lines of JSON:

```bash
cp /Users/josie/can-it-ford/.claude/tooling/settings_WITH_autoapprove.json /Users/josie/can-it-ford/.claude/settings.json
```

It is your current settings.json with exactly 9 lines appended and nothing
else changed (verified by diff). If you would rather edit by hand, do this:

Open `/Users/josie/can-it-ford/.claude/settings.json`, find `hooks.PreToolUse` (it is an array with 10
entries today), and **append** the object from `/Users/josie/can-it-ford/.claude/tooling/MERGE_settings_hook.json`:

```json
{
  "matcher": "Bash",
  "hooks": [
    { "type": "command",
      "command": "python3 $CLAUDE_PROJECT_DIR/.claude/tooling/commit_autoapprove.py" }
  ]
}
```

This hook can only **grant**. It never blocks, so your existing
`pretooluse_git_commit_gate.py` (params_check) and `banned_phrase_guard.py`
still run and still have final say.

**Verify:** ask a session to commit one file with the path-limited form. It
should commit without a Yes/No prompt. Ask it to commit a `.ply` and the prompt
should still appear.

Expected effect, based on last night's counts: roughly 25 blocking prompts
become roughly 3.

---

## STEP 3 — Warm the SSH sockets (1 min, and you must do this)

I cannot do this: TACC requires an interactive token.

```bash
ssh vista
```

```bash
ssh ls6
```

Leave both terminals open. `ControlPersist` is 8h, so one login covers a working
day. **The `canford-tacc` MCP server is what makes this last:** all sessions go
through its single pooled connection instead of 13 competing ones, which is what
saturated the socket and took LS6 down for the whole fleet last night.

**Verify:** ask a session for `tacc_env_probe(host="ls6", module="warpmpm")`.
It should return `is_stub: true` with `module_lines: 6`. That single field is
the fix for the several hours lost to a stub that imported cleanly.

---

## STEP 4 — Authenticate Undermind (3 min)

Undermind is configured but not authenticated, so six deep-research reports can
only be grepped as text. Reading their **catalogs** rather than their summaries
is what surfaced four uncited vehicle-fording papers.

In an interactive terminal:

```bash
claude mcp
```

Select Undermind and complete the browser OAuth. I cannot run this flow: this
session is non-interactive and I must never handle credentials.

**Verify:** the server appears without an "authentication required" note.

---

## STEP 5 — Add CI (5 min, optional but recommended)

```bash
cp /Users/josie/can-it-ford/.claude/tooling/MERGE_github_workflow.yml /Users/josie/can-it-ford/.github/workflows/canford-checks.yml
```

This runs `params_check.py`, `register_integrity.py` and
`count_claims_check.py` on every push. Today those run only as local hooks, so
they protect one machine; Vista's checkout has four modified tracked files
including `CLAUDE.md` and `failure_modes.py` that nothing currently checks.

**Note before you push it:** the repo is public and D1's branch is blocked on a
credential-flag file. Land this on a branch, not directly on main.

---

## STEP 6 — The frame reviewer (5 min, and I would do this one)

```bash
python3 -m venv ~/.venvs/canford-review
```

```bash
~/.venvs/canford-review/bin/pip install gradio
```

Then point it at the frames from last night's matched-dx render:

```bash
~/.venvs/canford-review/bin/python /Users/josie/can-it-ford/.claude/tooling/frame_review_app.py --frames "/Users/josie/can-it-ford/.claude/worktrees/fork-render-3class/figures/three_class_matched_2026-08-14/E8_HOLD_DO_NOT_COMMIT/animation/frames"
```

It opens in your browser, scrubs the 90 frames, shows each frame's own numbers
beside it, and has a checklist pre-loaded with the ten defect classes this
project has actually had, including the settle transient you found by eye.
Flags append to `/Users/josie/can-it-ford/.claude/state/frame_review_flags.jsonl`
(created on your first flag, so it does not exist yet), which a dispatch can
then read and act on.

---

## WHAT I STILL CANNOT DO, AND WHY

| Item | Why not | Who |
|---|---|---|
| Rotate the 12 to 15 credentials | I must never handle credential values | you, from D3's checklist |
| `ssh vista` / `ssh ls6` | interactive TACC token | you, step 3 |
| Undermind OAuth | interactive browser flow | you, step 4 |
| Push any branch | 188 commits await your per-branch go-ahead; the repo is public | you |
| Resolve the E8 licence question | needs a written permission decision about NCAC/CCSA reuse | you, and see dispatch R4-1 |
| Edit `/Users/josie/can-it-ford/.mcp.json` / `settings.json` | both carry another session's or shared state | you, steps 1 and 2 |

---

## ORDER I WOULD DO THEM IN

1. **Step 3** (sockets) — unblocks every cluster tool immediately.
2. **Step 1** (MCP) — the corpus server pays for itself on the first artifact lookup.
3. **Step 2** (auto-approve) — biggest recovery of session time.
4. **Step 6** (frame reviewer) — the highest-value human instrument this project has.
5. **Step 4** (Undermind), then **Step 5** (CI).
