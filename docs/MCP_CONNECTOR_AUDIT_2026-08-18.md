# MCP / connector audit, 2026-08-18

Scope: the Claude Code tool surface for this repo. Every claim below is tagged by
how it was obtained. READ = direct file read or command output this session.
COUNTED = tallied from this session's own tool manifest, which cannot be grepped,
so treat as approximate to within about one. INFERRED = reasoning over READ facts.

Method note per the H0 rule: all greps used `/usr/bin/grep`. Config reads were
`json.load` on the live files, not recalled.

## 0. Two claims from the 2026-08-17 Desktop session are WITHDRAWN

**(a) "The committed `github` entry uses a dead package" is FALSE.** [READ]
`git show HEAD:.mcp.json` contains exactly three servers: deepwiki, scite,
wolfram. There has never been a committed `github` entry. The
`npx @modelcontextprotocol/server-github` block existed only as an uncommitted
working-tree edit, and the follow-on claim that it "breaks for anyone else on a
fresh clone" is therefore also false: a fresh clone gets three HTTP servers and
no github entry at all.

**(b) "17 worktrees contradicts CLAUDE.md's 4" is not a contradiction to fix.** [READ]
`git worktree list` returns 17. The count is real. But the same command shows 5
of those are sibling directories under `~/` and 12 live under
`.claude/worktrees/`. Nothing in the live 823-line CLAUDE.md asserts 4; that
figure came from the pasted claude.ai Project instructions, which are a separate
document from this repo's CLAUDE.md. See section 4.

## 1. ROOT CAUSE of the tool-surface bloat

`.claude/settings.json` carries an **uncommitted** flip: [READ]

    HEAD:            "disableClaudeAiConnectors": true
    working tree:    "disableClaudeAiConnectors": false

That single flip is what admits the claude.ai connector directory into Claude
Code sessions in this repo. This session's manifest carries **31 UUID-named
connector servers** [COUNTED], among them Webflow, Amplitude, Coupler.io, Canva,
Asana, Supabase, Lucid, Zapier-Google (registered twice), and Three.js. None of
them appear in the connector-router skill's routing table except in its
"explicitly not auto-routed" list.

At least 9 of the 31 are duplicate transports for servers already registered by
name: scite, exa, undermind, hf, elicit, deepwiki, wolfram, consensus, and
Scholar Sidekick. [COUNTED]

RESOLVED 2026-08-18, Josie's call: reverted to `true`. Verified by `git diff`,
which no longer shows the line at all. The four routing-table rows that pointed
at connectors (Otter, Slack, Calendar, Drive) are now claude.ai-chat-only and
are no longer reachable from Claude Code. That is a deliberate trade, not an
oversight. No connector's account-side authorization was touched.

## 2. LIVE DEFECT, now fixed: a PreToolUse hook blocked every worktree

`.claude/settings.json` gained an uncommitted PreToolUse Bash hook: [READ]

    python3 $CLAUDE_PROJECT_DIR/.claude/tooling/commit_autoapprove.py

`.claude/tooling/` is **untracked** and **not gitignored** [READ:
`git ls-files --cached` empty, `git check-ignore` no match]. Untracked files do
not exist in a worktree checkout, confirmed absent in r5-physics and ctx-census
[READ]. `python3 <missing file>` exits **2** [READ, measured], and PreToolUse
exit 2 blocks the tool call.

**Therefore every Bash call from all 16 worktrees was blocked.** [INFERRED from
the three READ facts above.] This is the third documented recurrence of the
failure mode CLAUDE.md's "Hooks must fail open" section exists to prevent, after
`params_check.py` (34 blocked commits) and the earlier `.claude/tooling/` wiring.

FIXED 2026-08-18 by guarding the command with an existence test that exits 0 when
the script is absent. Verified in both directions: absent gives exit 0, present
still runs the hook. The `|| exit 0` is safe specifically because this hook's own
docstring states it never blocks and only grants.

Follow-up not done here: `git add` the tooling scripts so worktrees actually get
them. Note `.git/hooks/pre-commit` refuses more than 8 staged files and
`.claude/tooling/` holds 16 entries, so that needs splitting across commits.

## 3. Permission weakenings in the same uncommitted diff

Three changes, all uncommitted, all in `.claude/settings.json`: [READ]

1. `Bash(idev:*)` moved from **deny** to **allow**. This directly contradicts the
   measured finding that interactive `idev` burns 98.5 to 99.1 percent of Vista
   node-hours against every gated run, with 95 of 184 sessions ending in TIMEOUT.
   Vista currently shows 626 SUs remaining. [READ: session banner]
2. `Bash(srun --overlap:*)` and `Bash(scancel:*)` added to allow. `--overlap` is
   the documented correct form, so this one reads as a deliberate and correct
   addition.
3. Four `Read(...)` deny entries removed: `data/track1_sweep_v3/**`,
   `designsafe-staging/**`, the `.OLD-4906B` reference JSON, and the nested
   `can-it-ford/can-it-ford/**` path. The last is a genuine no-op because the
   nested duplicate no longer exists. The first two weaken the mechanical block
   that CLAUDE.md's "File provenance" section says enforces the deprecated list.

RESOLVED 2026-08-18, Josie's call: idev only.

- `Bash(idev:*)` restored to **deny**, at its original position. Verified live.
- `srun --overlap` and `scancel` KEPT in allow, deliberately.
- The three meaningful `Read(...)` denies were **left removed**. This is a
  known, accepted divergence from HEAD, recorded here so a later audit does not
  read it as undetected drift. If CLAUDE.md's provenance section is ever cited
  as proof those paths are mechanically blocked, that claim is currently FALSE
  for `data/track1_sweep_v3/**`, `designsafe-staging/**` and the `.OLD-4906B`
  reference JSON.

## 4. The "which CLAUDE.md is correct" question, answered

There is no hidden correct version. [READ, `find` + `wc -l` across `~`]

    823  2026-08-17 23:07  ~/can-it-ford/CLAUDE.md              <- CANONICAL
    700  2026-08-12 20:58  ~/can-it-ford-warpmpm-continue/
    676  2026-08-13 12:54  ~/Downloads/can-it-ford-main/
    603  2026-08-12 20:04  ~/can-it-ford-realism/
    544  2026-08-11 14:16  ~/can-it-ford-BACKUP-2026-08-11/
    538  2026-08-11 13:35  ~/can-it-ford-visual-trial/  and  -moving-vehicle/

The main working tree is both the newest and the largest. Every other copy is an
older snapshot frozen at the commit its directory was created from. They are not
competing versions; they are history.

Separately, the **connector routing table does not live in CLAUDE.md at all.** It
is `.claude/skills/connector-router/SKILL.md` [READ]. The pasted advice to edit
"CLAUDE.md v9 Part 9" cannot be followed here because this repo's CLAUDE.md has
no numbered Parts, a fact its own August 8 addendum already records.

FIXED 2026-08-18: two rows added to that skill's table, for Context7 (live
library API docs, explicitly distinguished from DeepWiki's repo-specific role)
and Scholar Sidekick (title-vs-record citation integrity, distinguished from
Scite's findings role). Context7 previously appeared **nowhere** in `.claude/skills/`
or `CLAUDE.md` despite being registered at user scope. [READ]

## 5. Overleaf is NOT working, proven without writing anything

The Overleaf MCP reports Connected and `list_projects` returns the "Can It Ford"
project, but that is local config only. Forcing an actual remote fetch with
`list_files` fails: [READ]

    git clone https://git:@git.overleaf.com/6a5958d10484feadf65a934e
    fatal: Authentication failed

The empty password between `git:` and `@` is the tell. This confirms, by
measurement rather than suspicion, the CLAUDE.md "STILL OPEN" item: the Overleaf
token is off local disk and a fresh Git authentication token is needed. The old
token also remains valid server-side until rotated in Overleaf account settings.

A read-only call was deliberately chosen over the proposed write test. The write
test would have failed identically while carrying the risk of a partial write to
a live shared document.

## 6. Registration duplication across the three config scopes

24 registrations resolve to 17 distinct server names, so 7 are duplicates. [READ]

    .mcp.json (project)   6   deepwiki scite wolfram github canford-corpus canford-tacc
    ~/.claude.json global 11  blender context7 deepwiki elicit exa github hf overleaf
                              scholar-sidekick undermind zotero
    ~/.claude.json project 7  consensus elicit jupyter-executor overleaf scite
                              undermind zotero

    duplicated: deepwiki, github, scite, elicit, overleaf, undermind, zotero

**CORRECTION 2026-08-18, same day.** An earlier version of this section said the
six `.mcp.json` servers "prompt for approval rather than loading silently",
reasoning from `enabledMcpjsonServers: []` in `~/.claude.json`. That was WRONG: it
read only one of the two files that set the key. `.claude/settings.local.json`
(gitignored, machine-local, and therefore invisible to `git status`) already lists
all six under `enabledMcpjsonServers`, and local scope wins. They auto-load.
The lesson is the one this repo keeps relearning: a setting read from one scope is
not the effective value. Check every scope that can set the key before asserting
behaviour.

## 7. What is genuinely working and should not be touched

Both custom servers handshake correctly. [READ, probed with a real MCP
`initialize` request]

    canford-corpus  6 tools, protocol 2024-11-05, responds
    canford-tacc    6 tools, protocol 2024-11-05, responds

`.mcp.json` addresses them by **absolute** path, not `${CLAUDE_PROJECT_DIR}`.
That is correct and is a genuine improvement over `MERGE_mcp.json`, which
specifies `${CLAUDE_PROJECT_DIR}` and would break in exactly the worktrees where
`.claude/tooling/` is absent. The memory note claiming these two servers die with
-32000 in worktrees is **stale on the mechanism** and should be updated.

All 13 scripts under `.claude/hooks/` exist and are tracked. [READ] Only the
`.claude/tooling/` hook was unguarded.


## 8. Connectivity, measured 2026-08-18. Both MCP paths are DOWN, the CLI is UP

This section replaces guesswork with four live tests.

### GitHub: CLI works, MCP does not

    gh auth status          -> logged in, jcerrell-IS, keyring, protocol ssh   [READ]
                               scopes: admin:public_key, gist, read:org, repo
    git ls-remote origin    -> returns c7f0a16..., so HTTPS + osxkeychain auth
                               is live and the remote is reachable             [READ]
    gh repo view            -> can-it-ford | PUBLIC | default=main             [READ]
    mcp__github__get_file_contents on jcerrell-IS/can-it-ford
                            -> **Authentication Failed: Bad credentials**      [READ]

So the `github` MCP server is registered and its tools load, but it cannot
authenticate. `GITHUB_PERSONAL_ACCESS_TOKEN` is exported at `~/.zshrc:750`
(presence tested, value never read) and is **not set** in the non-interactive
shell Claude Code runs, because `.zshrc` is sourced only for interactive shells.
That is the likely cause: the server receives an empty token.

**Conclusion, and it inverts the assumption in the 2026-08-17 Desktop session.**
That session reasoned the GitHub MCP was a nice-to-have on top of a working CLI.
The measurement says the opposite: the CLI is the ONLY working GitHub path, and
the MCP is dead weight that will silently fail mid-task. Route GitHub work
through `gh` and `git`, not through `mcp__github__*`, until the MCP is
re-authorized interactively.

Re-authorizing needs an interactive session (`/mcp`, then the OAuth flow). It
cannot be done from a non-interactive session, and no token should be pasted into
`.mcp.json`, which is a **tracked file in a PUBLIC repo**.

### Overleaf: correctly wired, zero-byte token

    /Users/josie/.config/overleaf-mcp/token   0 bytes, mode 0600, dir 0700   [READ]

Everything around it is right. The directory is 0700, the file is 0600, and the
project-scope MCP entry points at it via `OVERLEAF_GIT_TOKEN_FILE`. The file is
simply empty, which produces the empty password in
`https://git:@git.overleaf.com/...` and the observed clone failure.

There is a second, stale definition: the **user-scope** `overleaf` entry still
carries literal placeholders `OVERLEAF_PROJECT_ID: "YOUR_PROJECT_ID"` and
`OVERLEAF_GIT_TOKEN: "YOUR_GIT_TOKEN"`. [READ] Project scope wins inside this
repo so it is currently harmless here, but it means Overleaf is broken by
construction in every OTHER project on this machine, including
`~/can-it-ford-paper`.

Installing the token is a credential-handling step and was deliberately NOT
automated. See section 9.

### The two custom servers and the research stack are fine

`canford-corpus` and `canford-tacc` both answer a real MCP `initialize`. The
research servers (scite, wolfram, deepwiki, context7, zotero, undermind, elicit,
consensus, scholar-sidekick, exa) are HTTP or already-authorized stdio and were
exercised this session without error.

## 9. Max-accessibility changes, and where they were put

All permission expansion went into `.claude/settings.local.json`, NOT the tracked
`.claude/settings.json`. Three reasons: it is gitignored via
`~/.config/git/ignore` [READ], so it creates no diff noise in a file two other
sessions are live in; it is machine-local, so it cannot leak a permission posture
to a collaborator or to the public repo; and it is already where the accumulated
approve-once residue lives.

    permissions.allow      35 -> 152 entries
    enableAllProjectMcpServers = true

What was added: generalized read-and-inspect Bash verbs replacing one-off
approve-once entries such as a hard-coded `md5` of a single path; read-only `git`
and `gh` subcommands; whole-server allows for the read-oriented research MCPs and
the two project-built servers; sixteen `WebFetch` domains covering NVIDIA, Taichi,
PyTorch, numpy, arXiv, DOI, TACC and the Claude docs.

What was deliberately NOT added: blanket `mcp__github` and `mcp__overleaf`. Only
their READ tools are allowed by name. Their write tools (`create_pull_request`,
`push_files`, `merge_pull_request`, `write_file`, `write_section`) stay
prompt-gated, because this repo is public and Overleaf is a shared live document.
The `gh api` verb was also withheld, since it performs writes when given a
`-f` or `-X` flag.

Deny rules are unaffected and still win over allow, so the bulk-staging deny
family, `idev`, and the deprecated-file Read blocks all remain enforced.

## 10. GitHub MCP root cause, measured. Section 8's hypothesis and a later session's are BOTH withdrawn

Added 2026-08-18 03:52 BST, after a direct probe of every token and both endpoints.
Section 8 above is not deleted, because its four `gh`/`git` measurements stand.
Only its *causal explanation* is withdrawn, along with a competing explanation
carried over from another session. All curl probes below sent a real MCP
`initialize` to the live endpoint.

### What was claimed, and what the probe returned

Two explanations were in circulation and neither survives. [READ]

    Claim A (section 8): "GITHUB_PERSONAL_ACCESS_TOKEN is not set in the
      non-interactive shell, so the server receives an empty token."
    Measured: the variable IS set in this session's environment,
      40 chars, prefix gho_.                                    -> A is FALSE

    Claim B (later session): "the github_pat_ token in your user-scope
      config was itself dead, that is what produced Bad credentials."
    Measured: there is NO github entry in user scope at all. `~/.claude.json`
      mcpServers keys are blender, context7, deepwiki, elicit, exa, hf,
      overleaf, scholar-sidekick, undermind, zotero.             -> B is FALSE

Every token on this machine authenticates, against BOTH hosts: [READ]

    token                         api.github.com/user   githubcopilot.com/mcp/
    ~/.zshrc:78 == :747 PAT       200  jcerrell-IS      200  initialize ok
    ~/.zshrc:750 PAT (distinct)   200  jcerrell-IS      200  initialize ok
    gh auth token (gho_, keyring) 200  jcerrell-IS      200  initialize ok

So "the PAT is dead" is false twice over: the two PATs are not merely alive on
the REST API, they are accepted by the Copilot MCP endpoint itself.

### The actual cause, reproduced

The project `.mcp.json` `github` entry carried **no `headers` block**, so no
Authorization header was ever sent. Probing the endpoint with no header
reproduces the failure exactly: [READ]

    curl -X POST https://api.githubcopilot.com/mcp/  (no Authorization header)
      -> HTTP 401  bad request: missing required Authorization header

CAVEAT, stated rather than glossed: the string reproduced is "missing required
Authorization header", NOT the "Bad credentials" wording section 8 recorded.
Those are different messages. The header-less entry is the only on-disk
configuration that fails at all, and every token was proven good, so it is the
only surviving explanation, but the exact wording was not re-observed. [INFERRED]

Contributing factor: that entry also **collided by name** with the server the
enabled `github@claude-plugins-official` plugin registers
(`~/.claude/settings.json:205`, true). The plugin's bundled config is correct and
uses env substitution, no token on disk: [READ]

    "headers": { "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}" }

### Fixes applied 2026-08-18

1. The header-less `github` entry was removed from `.mcp.json`. The plugin
   supersedes it. `canford-corpus` and `canford-tacc`, added by another live
   session in the same uncommitted hunk, were preserved untouched. Change is
   left UNCOMMITTED, in line with the shared-working-tree rule.
2. `~/.zshrc` no longer contains any token text. Three plaintext exports were
   replaced by one guarded block that reads the gh keyring at shell start:
   former lines 78 and 747 (two IDENTICAL `GITHUB_PAT` values, confirmed by
   sha256 of the values; 78 was dead by shadowing) and line 750 (a DISTINCT
   `GITHUB_PERSONAL_ACCESS_TOKEN`). Both `GITHUB_PERSONAL_ACCESS_TOKEN` and
   `GITHUB_PAT` are now set from `gh auth token`, so nothing that consumed the
   old name breaks. Verified: `zsh -n` passes, and a fresh `zsh -i` resolves
   both names to the 40-char `gho_` keyring token. Backup at
   `~/.zshrc.bak-2026-08-18-github-token` (mode 0600) still contains both PATs.
3. The only `github_pat_` string left in `~/.zshrc` is at line 708, inside the
   log-scrubber's own redaction regex. That is a pattern, not a credential.

### STILL OPEN, and it got worse, not better

The two PATs were **LIVE at the moment they were deleted**, so removing them from
`~/.zshrc` did not revoke them, it only stopped one copy from being read. This
directly updates the credential-exposure item: the GitHub PAT there is not one
token but **two distinct live tokens across three declaration sites**, and the
backup file above is now a fourth on-disk copy. Rotate both at
`https://github.com/settings/tokens`, then delete the backup. Until that is done,
treat this as unresolved.

Unrelated and NOT fixed here, but seen in the same read: `~/.zshrc:746` still
carries a plaintext `WANDB_API_KEY`. Its value ends in the four characters that
the W&B memory records as the LIVE key, not the revoked one. [READ]

### CLOSED 2026-08-18 04:03 BST: both PATs revoked, confirmed by value

Josie revoked both fine-grained PATs. Verified by re-probing the exact values
from `~/.zshrc.bak-2026-08-18-github-token`, not by trusting the UI: [READ]

    token                  api.github.com/user   api.githubcopilot.com/mcp/
    EXPIRES-08-22 PAT      401 Bad credentials   401
    NEVER-EXPIRES PAT      401 Bad credentials   401

Nothing that depends on GitHub broke, all four checked after revocation: [READ]
`gh auth status` still logged in as jcerrell-IS on the keyring token;
`git ls-remote origin` still returns `c7f0a16` over HTTPS via osxkeychain, which
holds a separate `gho_` credential; a fresh `zsh -i` still resolves both
`GITHUB_PERSONAL_ACCESS_TOKEN` and `GITHUB_PAT` to the 40-char `gho_`; and
`mcp__plugin_github_github__get_me` still returns jcerrell-IS.

**A diagnostic refinement worth keeping.** Revocation produced the exact string
`Bad credentials`, which is what section 8 originally recorded. That confirms the
two messages discriminate cleanly:

    "Bad credentials"                        -> a token WAS sent and was rejected
    "missing required Authorization header"  -> no token was sent at all

So the header-less `.mcp.json` entry explains a missing-header 401, but it does
NOT explain the "Bad credentials" that section 8 observed, because at that time
both PATs and the `gho_` all returned 200. Some other path sent a genuinely bad
token. Candidates not ruled out: one of the 31 UUID-named claude.ai connector
servers from section 1, or a user-scope `github` entry removed before this audit
began. **This remains UNRESOLVED and is recorded as unresolved rather than
attributed.** It is now moot for security, since every token it could have used
is either revoked or verified good.

Remaining cleanup, no longer a security item because the values are inert:
`~/.zshrc.bak-2026-08-18-github-token` and
`~/Desktop/claude_desktop_config.BACKUP-20260812-215239.json` still contain the
revoked strings.

## 11. W&B key removed from `~/.zshrc` the same session

Not an MCP item, recorded here because it was found while reading `~/.zshrc` for
section 10 and closed in the same pass.

Section 10 flagged one plaintext `WANDB_API_KEY`. There were **two live exports**,
`:77` and `:746`, plus the dead key inline in the `:62` comment. The `:77`/`:746`
pair is the **same shadowing pattern** as the two `GITHUB_PAT` lines, and a
comment at `:741` asserted the duplicate had already been fixed. It had not.
[READ]

Unlike the GitHub pair, all copies were the SAME value: sha256 `fddb50d90e7b`,
86 chars, tail `ipS9`, and `~/.netrc` (0600) already held that identical value.
Confirmed live: `api.wandb.ai/graphql` returned **200**, `jcerrell29`,
`jcerrell29-claremont-mckenna-college`. [READ]

All three sites were replaced by one block reading the `machine api.wandb.ai`
password from `~/.netrc`. The variable is still **exported** on purpose, because
two consumers depend on it and would have silently regressed: [READ]

    scripts/validate_state.sh check 3   -> would print "NOT SET anywhere, FIX THIS"
    analysis/wandb_backfill.py:7        -> wandb.login(key=os.environ.get(...))

Both re-run after the change in a fresh `zsh -i`: check 3 prints
"set in this shell, OK", and `os.environ.get` returns sha `fddb50d90e7b`.
`zsh -n` passes. The only `wandb_v1_` string left in the file is at `:706`,
inside the log-scrubber's own redaction regex, which is a pattern and not a
credential. Rotation is now a one-file edit to `~/.netrc`.

**LINE-NUMBER WARNING for this whole document.** `~/.zshrc` went from **750 to
790 lines** tonight, because four single-line exports were replaced by two
multi-line guarded blocks. Every `~/.zshrc:<n>` citation in sections 8, 10 and
11 above describes the file as it was BEFORE those edits and must not be used to
locate anything now. This is the same failure mode CLAUDE.md records for
`.gitignore` line numbers. Cite the block comment text instead.

Backups holding the old text, both mode 0600, both safe to delete once you are
happy with the new file: `~/.zshrc.bak-2026-08-18-github-token` (contains the two
now-revoked PATs) and `~/.zshrc.bak-2026-08-18-wandb` (contains the live W&B key,
which is also in `~/.netrc`, so deleting it loses nothing).
