# Connecting Overleaf to Claude Code, and to Claude generally

2026-08-18. Every fact below was verified live on this machine, not recalled. Where I could
not verify something I say so.

---

## 0. What already exists, verified

| thing | state |
|---|---|
| Overleaf git remote | **configured**, `https://git.overleaf.com/6a5958d10484feadf65a934e` |
| credential embedded in that URL | **none**, confirmed by `git config --get remote.overleaf.url` |
| Overleaf MCP server | **installed and configured**, project `default` = "Can It Ford" |
| `overleaf/main` head | `6466dfa` "Update on Overleaf.", 29 commits |
| Overleaf file layout | **FLAT**: `conference_101719_1.tex`, `can_it_ford_references_IEEE.bib`, figures as bare filenames at the root |
| Git authentication token | **MISSING on this machine. This is the only thing blocking everything.** |

`mcp__overleaf__list_projects` already answers correctly, so the server is wired. Only the
token is absent:

```
git clone https://git:@git.overleaf.com/6a5958d10484feadf65a934e
fatal: Authentication failed
```

Note the `git:@`, an empty password. Overleaf wants the **token as the password**, with the
username literally `git`.

---

## 1. THE WARNING THAT COMES FIRST

**`overleaf/main` and `origin/main` share NO COMMON ANCESTOR.** Verified:
`git merge-base overleaf/main origin/main` prints nothing at all.

So `git push overleaf main` is **not a sync**. It is a non-fast-forward that either refuses,
or, if anyone reaches for `--force`, **destroys all 29 Overleaf commits** including edits made
in the Overleaf web editor that exist nowhere else.

Two further traps that follow from the flat layout:
- The paper builds from **`conference_101719_1.tex`** on Overleaf, NOT from
  `paper/conference_101719.tex` in this repo. Editing the repo copy changes nothing.
- Figure paths on Overleaf are **flat** (`force_balance_v2.pdf`), while the repo nests them.
  Copying a repo `.tex` over the Overleaf one breaks every `\includegraphics`.
- The two `.bib` files diverge on citation keys. Pushing the repo bib would break **17**
  `\cite` commands, not the 5 that the count of renamed works suggests, because
  `shand2011arr` alone is cited 11 times.

**Therefore: do not push branches to Overleaf. Move individual files, deliberately.**

---

## 2. Step 1, revoke the old token FIRST

Per CLAUDE.md, the previous token was removed from local disk but **never revoked**, so it is
still valid server-side. Revoking it is the point of this step; creating a new one is
secondary.

1. Go to <https://www.overleaf.com/user/settings>
2. Find **Git integration** / **Git authentication tokens**
3. **Delete every existing token.** If you are unsure which is the old one, delete all of them
   and issue one fresh, which is strictly safer.
4. Then **Create a new token** and copy it. Overleaf shows it exactly once.

This is yours to do; I cannot and should not handle the token value.

---

## 3. Step 2, store it in the macOS keychain, NOT in a URL

**This repository is PUBLIC.** A token pasted into a remote URL lands in `.git/config`, gets
echoed by `git remote -v`, and has previously been captured into `~/.claude/backups/` roughly
once a minute. Use the keychain helper instead, which keeps the value out of every file.

Enable the helper once:

```bash
git config --global credential.helper osxkeychain
```

Then trigger one authenticated fetch. Git will prompt: username is `git`, password is the
token you just created.

```bash
git -C /Users/josie/can-it-ford fetch overleaf
```

The keychain stores it after the first success, and neither Git nor the MCP server will prompt
again.

**Do NOT do this**, and it is worth naming because it is the obvious shortcut:

```
git remote set-url overleaf https://git:TOKEN@git.overleaf.com/...
```

That writes the token into `.git/config` in a public repo's working tree.

---

## 4. Step 3, verify, and what success looks like

```bash
git -C /Users/josie/can-it-ford fetch overleaf && git -C /Users/josie/can-it-ford log --oneline -1 overleaf/main
```

**Success:** it prints a commit line without prompting. If the Overleaf project has moved since
`6466dfa`, you will see a newer SHA, which is fine and expected.

**Most likely failure:** `Authentication failed` again. That means the token was mistyped, or
it was pasted into the *username* field. Username is `git`; the token is the password.

**Second most likely:** the keychain silently replays a stale entry. Clear it and retry:

```bash
printf 'protocol=https\nhost=git.overleaf.com\n' | git credential-osxkeychain erase
```

---

## 5. Step 4, the MCP server picks it up automatically

The Overleaf MCP server shells out to `git clone`, so once the keychain holds the token the
server works with no further configuration. Confirm with a tool that actually touches the
remote, not just one that reads local config:

- `mcp__overleaf__list_projects` works even WITHOUT a token, because it only reads config. It
  is not a valid test.
- `mcp__overleaf__status_summary` clones, so it is the real test.

That distinction matters: a check that passes without the thing it is supposed to verify is
not a check.

Once working, the useful tools are `list_files`, `read_file`, `get_sections`,
`get_section_content`, `write_file` and `write_section`. Prefer `write_section` over
`write_file` for the paper: it replaces one section rather than the whole document, so a
concurrent web-editor edit elsewhere in the file is not clobbered.

---

## 6. Claude in general, meaning claude.ai and the desktop app

**There is no first-party Overleaf connector for claude.ai.** I checked the connector registry
available to this session and Overleaf is not in it. So the options are, honestly:

1. **Claude Code / Claude Desktop with this MCP server.** Already configured here, and it is
   the only path that gives Claude direct read and write to the project. Desktop uses the same
   `.mcp.json` mechanism; the server entry can be copied across.
2. **Overleaf's own web editor plus copy-paste.** Works everywhere, no setup, no token. For
   a handful of paragraph edits this is genuinely faster than debugging auth.
3. **Overleaf "Link Sharing" read-only URL.** Gives a person or a fetch tool read access to a
   compiled PDF without any token. Useful for review, useless for writing.

Option 1 for real work, option 2 for one-off edits.

---

## 7. The safe editing loop, once connected

Because the histories are unrelated, treat Overleaf as a **separate destination**, not a branch:

1. Read the live file first, always. It may have web-editor edits that exist nowhere else.
2. Make the change against **that** content.
3. Write back with `write_section` where possible.
4. Re-read to confirm what landed.

For the `.bib` specifically, a byte-identical local copy of the Overleaf bib already exists at
`paper/canonical_2026-08-02/can_it_ford_references_IEEE.bib`, so bib edits can be **prepared
and diffed locally without any token**, and only the final write needs authentication.

---

## 8. What is genuinely blocked until you do section 2

- Adding the 6 MPM method citations the paper is missing. The paper cites **zero** MPM method
  literature; entries are drafted and none of their keys collide with the existing 15.
- Any correction to the compiled PDF.

Everything else in the paper lane can proceed offline against the canonical local copy.
