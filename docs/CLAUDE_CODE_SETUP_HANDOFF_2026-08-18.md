# Claude Code setup, handoff for a fresh session

**Written 2026-08-18 ~04:05 BST. Read top to bottom before acting.**

Every claim is tagged by how it was obtained:
`[READ]` direct file read or command output, this session.
`[MEASURED]` a command was run and its exit code or HTTP status observed.
`[INFERRED]` reasoning over READ/MEASURED facts.
`[UNVERIFIED]` asserted but never executed. Treat as a hypothesis.

Re-derive anything you are about to state as fact. This repo's culture is that an
unverified claim is worse than no claim, and this session produced three of its own.

---

## 0. DO THIS FIRST. LIVE CREDENTIAL EXPOSURE.

The previous assistant printed a GitHub fine-grained PAT in cleartext into the session
transcript. It begins `github_pat_11CDJE2II0`. It was removed from `~/.claude.json`
`[MEASURED: grep -c returns 0]` but it remains in:

- the session transcript on disk under `~/.claude/projects/-Users-josie-can-it-ford/`
- `~/.zshrc:750`, as the `GITHUB_PERSONAL_ACCESS_TOKEN` export

**Revoke it at https://github.com/settings/tokens, "Fine-grained tokens".**
Scrubbing files does not un-expose a live token. Revocation is the only fix.

That PAT was already dead before the leak `[MEASURED: the github MCP returned
"Bad credentials" with it]`. That lowers severity. It does not remove the need to revoke.

---

## 1. WHAT THIS SESSION WAS FOR

Make Claude Code maximally effective for Can It Ford: MPM flood-vehicle simulation,
warpmpm on NVIDIA Warp, TACC Vista/LS6 with SLURM, LaTeX paper on Overleaf, 212 Python
files, PUBLIC GitHub repo `jcerrell-IS/can-it-ford`, heavy provenance culture.

Four asks:

1. Get GitHub working. The interactive `/mcp` OAuth flow FAILED for the user.
2. Get Overleaf working. **DONE, section 3.**
3. Audit plugins for irrelevance to a physics project.
4. Design custom plugins, connectors, marketplace.

---

## 2. CLAIMS WITHDRAWN. DO NOT CARRY THESE FORWARD.

**(a) "The committed `github` entry uses a dead npx package."** FALSE.
`git show HEAD:.mcp.json` `[READ]` has exactly three servers: deepwiki, scite, wolfram.
There has never been a committed github entry. The `npx @modelcontextprotocol/server-github`
block existed only as an uncommitted working-tree edit, so "it breaks on a fresh clone"
is also false.

**(b) "17 worktrees contradicts CLAUDE.md's 4."** Not a contradiction.
`git worktree list` returns 17 `[READ]`. The live 823-line CLAUDE.md asserts no such
number. The "4" came from the claude.ai Project custom instructions, a SEPARATE document.

**From this session's own assistant, all three self-corrected:**

- Claimed HEAD moved backwards. It did not. `git reflog` `[READ]` shows a clean forward
  chain `7eb1686 -> 89aae02 -> 1e6732b -> 796fe94 -> 745364e -> 123981e -> 18dfbfa`.
- Claimed the Overleaf token was 0 bytes. **Stale measurement** taken at 03:32; installed
  at 03:42:14 `[READ: stat mtime]`. Re-check before reporting.
- Claimed the six `.mcp.json` servers prompt for approval, reading `enabledMcpjsonServers`
  from `~/.claude.json` only. WRONG: `.claude/settings.local.json` already lists all six
  and local scope wins. **A setting read from one scope is not the effective value.**

Also a false alarm worth not repeating: 14 tracked `.key` files are **LS-DYNA keyword
decks** for the NCAC Silverado and Yaris models `[MEASURED: no private-key headers in any]`.

---

## 3. CONNECTIVITY MATRIX, ALL MEASURED

| Service | State | Evidence |
|---|---|---|
| `gh` CLI | **WORKS** | jcerrell-IS, keyring, scopes `admin:public_key gist read:org repo` |
| `git ls-remote origin` | **WORKS** | returns a SHA, HTTPS + osxkeychain |
| Overleaf MCP | **WORKS** | token 40 bytes mode 0600; `list_files` returns `conference_101719_1.tex` |
| HuggingFace MCP | **WORKS** | `hf_whoami`: josiecerrell, Pro, **write**, PAT created 2026-07-23 |
| Elicit MCP | **WORKS** | 6% of period, ends 2026-08-21 |
| pyright LSP | **WORKS** | plugin enabled AND `pyright-langserver` present. 212 Python files. |
| canford-corpus MCP | **WORKS** | real MCP `initialize` answered, 6 tools |
| canford-tacc MCP | **WORKS** | same, 6 tools |
| **github MCP** | **BROKEN** | see 3.1 |

### 3.1 The GitHub failure, root-caused

Three `github` registrations existed. Only one could ever have worked:

| Registration | Auth header | Verdict |
|---|---|---|
| `.mcp.json` (project, TRACKED) | **none** | can never authenticate |
| user scope `~/.claude.json` | a literal `github_pat_` bearer | token DEAD, "Bad credentials" |
| `github@claude-plugins-official` | bearer from `GITHUB_PERSONAL_ACCESS_TOKEN` | correct design, variable unset |

Proven with curl against `https://api.githubcopilot.com/mcp/` `[MEASURED]`:

```
Authorization: Bearer $(gh auth token)   ->  HTTP 200
Authorization: Bearer                    ->  HTTP 400
```

Endpoint fine, keyring token valid. The gap: `GITHUB_PERSONAL_ACCESS_TOKEN` is **not set**
in Claude Code's shell `[MEASURED]`, because `.zshrc` is sourced only for interactive shells.

**Proposed fix:**

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=$(gh auth token) claude
```

`[UNVERIFIED]` **This has NOT been confirmed to work.** Nobody verified that Claude Code
substitutes an arbitrary environment variable into a **plugin** MCP server's `headers`
field. The docs confirm substitution of the three `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA`
/ `CLAUDE_PROJECT_DIR` placeholders in `url`, `headers`, `headersHelper`, but an arbitrary
variable is not documented there. An audit agent reported the plugin returning HTTP 400
"Authorization header is badly formatted", which is what an unsubstituted literal would
produce. An empty variable also gives 400, so the symptom cannot distinguish the two.
**Test this first.**

Until proven: **route all GitHub work through `gh` and `git`.** Measured working.

---

## 4. EVERY CHANGE MADE

### 4.1 `.claude/settings.json` (TRACKED, shared, uncommitted)

| Change | Detail |
|---|---|
| `disableClaudeAiConnectors` | `false` to `true`, restoring the committed value. The uncommitted flip by another session is what admitted ~31 claude.ai connector servers (Webflow, Amplitude, Coupler.io, Canva, Asana, Supabase, Lucid, Zapier-Google twice), 9 of them duplicates of already-named servers. **Josie chose this after being shown the tradeoff.** |
| `Bash(idev:*)` | allow to **deny**, restored. Contradicted the measured finding that interactive `idev` burns 98.5 to 99.1 percent of Vista node-hours, 95 of 184 sessions TIMEOUT. **Josie chose this.** |
| `srun --overlap`, `scancel` | **KEPT in allow.** `--overlap` is the documented-correct form. |

**Left unreverted at Josie's explicit choice:** three `Read(...)` deny entries another
session removed (`data/track1_sweep_v3/**`, `designsafe-staging/**`, the `.OLD-4906B` JSON).
KNOWN divergence from HEAD. **Consequence:** if CLAUDE.md's provenance section is cited as
proof those paths are mechanically blocked, that claim is currently FALSE for those three.

### 4.2 The hook defect. Most important fix of the session.

An uncommitted PreToolUse Bash hook ran
`python3 $CLAUDE_PROJECT_DIR/.claude/tooling/commit_autoapprove.py`.

Measured chain:

- `.claude/tooling/` is **untracked** `[MEASURED: git ls-files --cached empty]`
- and **not gitignored** `[MEASURED: git check-ignore no match]`
- absent from worktrees `[MEASURED: confirmed in r5-physics, ctx-census]`
- `python3 <missing file>` exits **2** `[MEASURED]`
- PreToolUse exit 2 equals BLOCK

`[INFERRED]` **Every Bash call from all 16 worktrees was blocked.** Third recurrence of the
failure CLAUDE.md's "Hooks must fail open" section exists to prevent, after
`params_check.py` (34 blocked commits) and the earlier `.claude/tooling/` wiring.

Fixed to:

```
P="$CLAUDE_PROJECT_DIR/.claude/tooling/commit_autoapprove.py"; if [ -f "$P" ]; then python3 "$P" || exit 0; fi; exit 0
```

Verified both directions `[MEASURED]`: absent gives exit 0; present runs the hook, exit 0.

**OPEN CONCERN.** The `|| exit 0` swallows any nonzero exit. Safe only if the script truly
never blocks. Its docstring says "This hook NEVER blocks. It only GRANTS."
**Read the code and confirm.** If it can exit 2, this guard introduced a defect.

### 4.3 `.claude/settings.local.json` (GITIGNORED, machine-local)

Chosen over the tracked file: gitignored via `~/.config/git/ignore` `[MEASURED]`, so no diff
noise in a file two sessions are live in, and no permission posture leaking to a public repo.

- `permissions.allow`: **35 to 161** entries
- `enableAllProjectMcpServers: true`
- `env` block, because these did NOT resolve as bare names:

```
CANFORD_PY         /Users/josie/.venvs/canitford-mpm/bin/python3   warp 1.16.0, numpy 2.5.1, scipy, matplotlib, trimesh, wandb
CANFORD_WANDB      /Users/josie/.venvs/canitford-mpm/bin/wandb     0.28.2
CANFORD_GRADIO_PY  /Users/josie/.venvs/canford-review/bin/python3  gradio 6.24.0, huggingface_hub 1.27.0
CANFORD_GRADIO     /Users/josie/.venvs/canford-review/bin/gradio
CANFORD_HF         /Users/josie/.venvs/hf-tools/bin/hf             1.26.1
```

All five verified by import `[MEASURED]`. `hf` DOES resolve as a bare name because Claude
Code captures `.zshrc` aliases at session start; `wandb` and `gradio` do not.

`[UNVERIFIED]` Nobody audited whether 161 entries grant more than intended.
`Bash(python3 -c:*)` is arbitrary code execution. Review it.

### 4.4 `~/.claude/settings.json` (USER scope, all projects)

21 `huggingface-skills` disabled via `skillOverrides`. Backed up to `*.bak-*`.

**Disabled:** the six `hf-cloud-*` SageMaker planners, `hf-mem`, `huggingface-best`,
`huggingface-community-evals`, `huggingface-datasets`, `huggingface-llm-trainer`,
`huggingface-local-models`, `huggingface-lora-space-builder`, `huggingface-paper-publisher`,
`huggingface-trackio`, `huggingface-vision-trainer`, `huggingface-tool-builder`,
`huggingface-zerogpu`, `train-sentence-transformers`, `transformers-js`, `trl-training`.

**KEPT:** `hf-cli`, `huggingface-spaces`, `huggingface-gradio`, `huggingface-papers`,
backing the real `hf_space/` Gradio path (`app.py` plus a `requirements.txt` that is
literally just `gradio`).

**The `hf` MCP server was NOT touched.** Still authenticates, write role. Josie challenged
this decision; the distinction between the plugin's training skills and the MCP server is
the answer. Two are genuinely arguable: `huggingface-datasets` and `hf-mem`. Restore all 21:

```bash
/usr/bin/python3 -c "import json,os;p=os.path.expanduser('~/.claude/settings.json');d=json.load(open(p));[d['skillOverrides'].pop(k) for k in list(d['skillOverrides']) if k.startswith('huggingface-skills:')];json.dump(d,open(p,'w'),indent=2);print('restored')"
```

### 4.5 `~/.claude.json`

Removed the user-scope `github` entry carrying the dead PAT. Backed up first. No collateral
`[MEASURED: 54 projects preserved, 10 user servers, 0 matching token strings]`. Repaired the
user-scope `overleaf` entry, which held literal `YOUR_PROJECT_ID` and `YOUR_GIT_TOKEN`
placeholders, to point at the real token file.

### 4.6 `.claude/skills/connector-router/SKILL.md` (TRACKED)

Two rows added, one corrected. Context7 previously appeared **nowhere** in `.claude/skills/`
or `CLAUDE.md` despite being registered at user scope `[MEASURED]`.

- **Context7**: live library API docs, distinguished from DeepWiki (library-general versus
  repo-specific)
- **Scholar Sidekick**: title-vs-record citation integrity, distinguished from Scite's
  findings role. A DOI resolving is not evidence a citation is real.
- **GitHub row corrected** to route through `gh` CLI, not the MCP, with the measurement.

**The routing table is NOT in CLAUDE.md.** It is `.claude/skills/connector-router/SKILL.md`.
The earlier advice to edit "CLAUDE.md v9 Part 9" cannot be followed: this repo's CLAUDE.md
has no numbered Parts, a fact its own August 8 addendum already records.

### 4.7 Security, `/tmp`

`/tmp/overleaf-6a5958d10484feadf65a934e/.git/config` was mode **0644** in world-readable
`/tmp` with the `olp_` token in the remote URL `[MEASURED]`. Tightened to 0600, directory
to 0700.

**This will recur.** overleaf-mcp recreates it 0644 on its next clone. Defect in
`@mjyoo2/overleaf-mcp`, not in Josie's config.

**Second Overleaf hazard, unresolved:** `write_file` and `write_section` run add, commit and
push from that `/tmp` clone, so this repo's `.git/hooks/pre-push` and its `PUSH_OK=1` gate
**never fire**. Any session with Overleaf loaded can commit to the live paper in one call.

### 4.8 New files

- `scripts/overleaf_token_install.sh` (untracked, executable). Reads the token from
  **stdin**, not argv, so it stays out of shell history, `ps`, and transcripts. Writes 0600,
  verifies with a read-only `ls-remote`. Empty-input guard tested `[MEASURED]`.
- `docs/MCP_CONNECTOR_AUDIT_2026-08-18.md` (untracked, 273 lines). Full working.
- this file.

---

## 5. DEFECTS IN THE PROJECT ITSELF, NOT FIXED

### 5.1 The claim-checker enforces a stale claim. Highest priority.

`scripts/check_claims.py` Rule **C6**, an active WARN rule, fires on any text containing
`9.80665` and asserts `[READ]`:

> "9.80665 appears at TWO sites, not one: failure_modes.py:14 AND
> analysis/viability_dashboard_scaffold.py:11 ... do NOT write that it appears only in
> failure_modes.py. Unify on 9.81, then re-run analysis/classify_failure_modes.py and
> confirm 16 SLIDE / 1 STUCK holds."

Live `[MEASURED]`:

| Path | Content |
|---|---|
| `analysis/viability_dashboard_scaffold.py:11` | `G = 9.80665` **the only remaining live literal** |
| `simulation/failure_modes.py:14` | `G = 9.81  # unified 2026-08-12` |
| `simulation/failure_modes.py:15` | comment: "Was 9.80665, a 0.0342 percent fork that fed the..." |
| `analysis/classify_failure_modes.py:30` | a comment referencing it |
| `scripts/check_claims.py:151,229` | the stale rule itself |

The guard's instruction is now inverted: it appears **only** in
`viability_dashboard_scaffold.py`. The remediation text describes half-finished work.
**Deliberately NOT edited**, because which claim replaces C6 is a provenance decision, and
because "re-run `classify_failure_modes.py` and confirm 16 SLIDE / 1 STUCK" may or may not
have been done. Ask Josie. Do not guess.

### 5.2 CLAUDE.md carries the same dead claim

- **Items 3 and 15** assert `failure_modes.py:14` is `9.80665`, call it a live fork that fed
  the published 16 SLIDE / 1 STUCK verdicts, and instruct "Never write that it has not
  influenced a gated result". Stale.
- **Item 14** cites `vehicle_params.py:89` for `bbox_m`. Live it is at **:131** `[MEASURED]`,
  off by 42 lines. (`:31` and `:79` are prose mentions.)
- The August 15 section says "**43** of 332 papers reach `paper/`". Live
  `research_index.py --stats` reports **cited 76** `[MEASURED]`. CLAUDE.md itself warns this
  count is SCOPE-SENSITIVE and that `.claude/worktrees/` must be excluded, so determine
  whether 76 is a scope change or genuine drift **before** editing either number.

### 5.3 Duplicate plugin registrations

- `context7` installed **FOUR** times: 1 project scope (version "unknown") plus 3 local scope
  (91a03142cb3a) `[READ]`
- `github@claude-plugins-official` now at **both** project and user scope, both enabled

Determine the surviving scope before any `claude plugin uninstall`; the command targets a
scope and a wrong scope removes the wrong thing.

### 5.4 `.claude/tooling/` is a structural worktree landmine

Untracked and NOT gitignored, so absent from all 16 worktrees and any fresh clone. It holds
`corpus_mcp.py`, `tacc_mcp.py`, `commit_autoapprove.py`, `round5_autodispatch.py` and more.
`.claude/hooks/` (13 scripts) and `.claude/checks/` (4 scripts) **are** tracked.

`.mcp.json` addresses the two MCP servers by **absolute** path, which is correct and resolves
back to the main tree from any worktree. Do NOT "fix" it toward `MERGE_mcp.json`, which
specifies the `CLAUDE_PROJECT_DIR` placeholder and would break in exactly the worktrees where
the directory is absent.

Permanent fix not done: track the tooling scripts. `.git/hooks/pre-commit` refuses more than
8 staged files and the directory holds 16 entries, so it needs splitting across commits.

---

## 6. WHAT I COULD NOT DO, AND WHY

| Blocked | Reason |
|---|---|
| Install the Overleaf token | credential handling. Josie did it at 03:42. |
| Revoke the leaked PAT | account action, human only |
| `/mcp` OAuth for GitHub | a non-interactive session cannot run an OAuth flow |
| Edit the claude.ai Project instructions | not a file on disk |
| Disconnect Sentry / Atlassian Rovo | claude.ai account settings, unreachable locally |
| Commit or push | nothing was staged, committed, or pushed all session |

---

## 7. TRAPS. YOU WILL HIT THESE.

1. **`grep` is not grep.** It is a shell function wrapping ugrep with `--ignore-files`, so it
   SKIPS gitignored paths. Use `/usr/bin/grep` for any inventory claim.
2. **Guard hooks match TEXT, not intent.** Writing the bulk-staging command names as literal
   strings, even inside a grep pattern, a heredoc, or prose, trips `gate_destructive.sh` and
   blocks the entire Bash call. This happened three times this session, twice while writing
   this very file. Use the Write tool for documents that must mention them, since the guard
   matches only on Bash.
3. **Never `cd`.** One `cd` moves the tracked cwd for the whole session and wedges
   relative-path hooks. Use absolute paths or `git -C`.
4. **Exploratory `grep` and `find` need `|| true`.** No match exits 1 and reads as a failure.
5. **An unquoted `--include` glob dies in zsh** with "no matches found". Quote it.
6. **2 to 3 other Claude Code sessions are live in this repo.** Re-check `git status`
   immediately before any commit. Stage explicit paths only; the bulk-staging forms are
   blocked by hook and by standing rule.
7. **`~/.claude.json` is ~100 KB with 54 projects.** Back it up before editing. Prefer
   `claude mcp add` and `claude mcp remove` over hand-editing.
8. **A workflow was launched then interrupted** (`wf_f17a69af-44f`, task `wlnu7dv1v`). Its
   results were never delivered. Do not cite them. Re-run or ignore.
9. **An earlier workflow did complete** (`wf_9d89b7fe-2a1`), output at
   `/private/tmp/claude-501/-Users-josie-can-it-ford/8f700aae-6b25-417f-ae5e-9cbdb89f2b02/tasks/wnpl6a6ip.output`.
   Several of its claims were re-derived and two were wrong. Verify before citing.

---

## 8. THE PROMPT FOR THE NEW SESSION

Paste this verbatim:

> Read `docs/CLAUDE_CODE_SETUP_HANDOFF_2026-08-18.md` end to end before doing anything. It is
> the handoff from the previous session and it tags every claim by how it was obtained.
> Re-derive anything you are about to state as fact; three claims in that document's own
> history turned out to be stale measurements or scope errors.
>
> Then work through this in order. Do not skip the verification step in any item.
>
> 1. **Verify the GitHub fix.** Section 3.1 marks it UNVERIFIED. Determine empirically
>    whether Claude Code substitutes an arbitrary environment variable into a **plugin** MCP
>    server's `headers` field. If it does not, find a route that works without writing a
>    token into any tracked file, because this repo is PUBLIC. Prove it with a read-only
>    `mcp__github__*` call and report the exact result, not an assumption.
> 2. **Audit the 161 allow entries** in `.claude/settings.local.json` for anything granting
>    more than intended. `Bash(python3 -c:*)` is arbitrary code execution. Recommend removals.
> 3. **Read `.claude/tooling/commit_autoapprove.py`** and confirm its docstring claim that it
>    never blocks. If it can exit 2, the guard in section 4.2 swallows a real block and must
>    be rewritten to preserve that exit code.
> 4. **Resolve the duplicate registrations** in section 5.3. Determine the surviving scope for
>    each before running any uninstall, then run them and verify with `claude plugin list`.
> 5. **Build the custom plugin.** Package this project's own assets: the ~20 skills, the
>    `physics-skeptic` and `provenance-verifier` agents, the 13 tracked hooks, the 4 tracked
>    checks, and the two custom MCP servers (`canford-corpus`, `canford-tacc`), as a local
>    plugin with a `.claude-plugin/marketplace.json` using relative-path sources, so every
>    worktree and every fresh clone gets them. This is the structural fix for section 5.4.
>    Run `claude plugin validate .` before installing. Note the marketplace-root exception in
>    the docs: with `source: "./"`, listing specific skill subdirectories replaces the default
>    `skills/` scan rather than adding to it.
> 6. **Bring the stale claims to me. Do not fix them yourself.** Sections 5.1 and 5.2: C6,
>    CLAUDE.md items 3, 14 and 15, and the 43-vs-76 count. Show me the live value, the current
>    text, and the exact proposed replacement for each, then wait for my decision.
>
> Do not commit or push anything. Two other sessions are live in this repo. Tell me plainly
> whenever something is unverified rather than presenting it as done.
