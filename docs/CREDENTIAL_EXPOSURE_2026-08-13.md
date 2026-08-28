# Credential exposure: plaintext CLAUDE_CODE_OAUTH_TOKEN in cluster shell startup

**Status: OPEN. Rotation is a Josie action and has not been done.**
**This file is deliberately UNCOMMITTED. It contains no secret, but it names
exact paths and line numbers, and committing it pushes that to GitHub. Commit
only after rotation is complete, or not at all.**

Diagnosed 2026-08-13 ~17:35 CEST. Every line below was verified live by
running the check. **No token value was ever printed, logged, or transmitted
during this diagnosis.** All value comparisons were done by hashing or by
length, never by display.

Prior record: `.remember/today-2026-08-13.md` flagged this twice on 2026-08-13,
at the 12:35 entry ("security: plaintext token in ~/.bashrc needs rotation")
and again at 12:48 ("rotate token on Vista"). No action followed.
`docs/SECURITY_ACTIONS_2026-07-31.md` does not mention it.

## What is exposed, exactly

| Host | File | Lines | Occurrences |
|------|------|-------|-------------|
| Vista | `/home1/11603/jcerrell0629/.bashrc` | 112 | 1 |
| LS6 | `/home1/11603/jcerrell0629/.bashrc` | 122, 123, 124 | 3 |
| MacBook | no `~/.bashrc` exists | n/a | **0** |

**The three LS6 lines are not duplicates of one value.** `sort -u` over the
three matching lines returns **2** distinct lines, so at least two different
token values sit in that file. Bash applies them in order, so the line 124
value is the one that takes effect, and the other is dead but still on disk.
**Both must be rotated.** Rotating only the active one leaves a live
credential in the file.

## What is NOT exposed

Checked and clean, so the blast radius is smaller than the flag implies:

- **Permissions are already tight.** Both `.bashrc` files are `-rwx------`
  (0700), owner `jcerrell0629`, group `G-819066`, and both home directories
  are `drwx------` (0700). Not group-readable, not world-readable. No other
  TACC user can read this through the filesystem.
- **No other dotfile carries it.** On both clusters, `.bash_profile`,
  `.profile`, `.bash_logout`, `.netrc`, `.env` and `.zshrc` all return 0
  occurrences. On the Mac, `.bashrc`, `.bash_profile`, `.profile`, `.zshrc`,
  `.zprofile`, `.netrc` and `.env` all return 0.
- **No value leaked into any work area.** A recursive scan for the token
  prefix `sk-ant-` across `$HOME`, `/work/11603/jcerrell0629` and
  `/scratch/11603/jcerrell0629` returned, excluding `.bashrc` itself:
  - Vista: **nothing**, in all three roots.
  - LS6: nothing in `/work` or `/scratch`. In `$HOME`, only
    Anthropic-shipped artifacts (`~/.claude/remote/ccd-cli/2.1.227`,
    `~/.local/share/claude/versions/2.1.220`, and
    `~/.claude/remote/plugins/*/tests/test_{haiku,log_sh,umask}.py`) plus one
    session plan file, `~/.claude/plans/before-writing-anything-this-gentle-scroll.md`
    (12,296 B, `-rw-------`, mtime 2026-07-20). **That plan file is a false
    positive**: the longest `sk-ant-` match in it is **7 characters**, which is
    the bare prefix with no token body. The binaries contain the prefix as a
    string constant. No file outside `.bashrc` holds a token value.
- **Shell history is clean of values.** Vista `.bash_history` (0600) contains
  **1** mention of the variable NAME and **0** occurrences of a value. LS6
  `.bash_history` contains 0 of each.

## The one residual risk that rotation is the only fix for

The token is inherited by **every process launched from a login shell** on
both clusters, including every `sbatch` job that sources the environment. A
job that dumps `env`, or a script that prints its environment on error, would
write the token into a SLURM `.out` file. Those often land in `/scratch`, where
directory permissions are looser than `$HOME`. No such leak was found today,
but the exposure window covers every job run since the export was added.

Second residual: **TACC backs up `$HOME`.** The Lonestar6 MOTD states a full
`$HOME` backup every few months and an incremental every few days. So both
token values are in TACC's backup system, outside the reach of any file edit
you make now. Rotation at the issuer is the only action that invalidates them.

## Remediation, in this order. Order matters.

**Step 1, rotate at the issuer, before touching any file.** Rotating first
means the on-disk values are already dead when you edit, so a stray backup
copy or a snapshot cannot hurt you. Reissue the Claude Code token from your
account, then reissue a second time if you want the older LS6 value
definitively retired as well. **This is an account action. Do it yourself; do
not delegate it to a Claude Code session, and do not paste the new value into
a chat.**

**Step 2, only after step 1 completes, strip the lines.** Run yourself:

```bash
ssh vista 'cp ~/.bashrc ~/.bashrc.pre-token-strip && sed -i "/CLAUDE_CODE_OAUTH_TOKEN/d" ~/.bashrc && echo -n "remaining on vista: " && grep -c CLAUDE_CODE_OAUTH_TOKEN ~/.bashrc'
```

```bash
ssh ls6 'cp ~/.bashrc ~/.bashrc.pre-token-strip && sed -i "/CLAUDE_CODE_OAUTH_TOKEN/d" ~/.bashrc && echo -n "remaining on ls6: " && grep -c CLAUDE_CODE_OAUTH_TOKEN ~/.bashrc'
```

Expected output on each: `remaining on <host>: 0`. Most likely failure mode:
`grep -c` returns 0 and exits non-zero, which reads as an error but is the
success case. The `.pre-token-strip` backups still contain the old values, and
that is safe **only because step 1 already revoked them**; delete them once
you have confirmed a new login shell works.

**Step 3, expect something to break, and know what.** The export was almost
certainly added so non-interactive Claude Code works on the clusters. Removing
it may break headless runs. The replacement is a per-node
`claude setup-token`, or a 0600 file sourced only where it is needed, rather
than a global export in `.bashrc`. Decide that before you strip, so you are
not debugging it under time pressure inside an allocation.

## Verification after remediation

```bash
ssh vista 'grep -c CLAUDE_CODE_OAUTH_TOKEN ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null; ls -la ~/.bashrc.pre-token-strip 2>/dev/null'
```

Success is 0 on every dotfile and no leftover `.pre-token-strip`. Then append
a dated line to `docs/SECURITY_ACTIONS_2026-07-31.md` recording the rotation,
since that file is where this project's security actions belong and it
currently has no entry for this.
