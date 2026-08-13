# FLAG: plaintext credentials on three machines, 2026-08-13

Raised under dispatch flag rule 4, "an exposed credential". Written to a named file
rather than left inline, per the operating protocol. **Work continued on everything
else in scope; this flag does not end the session.**

**No secret value appears in this file.** Values are identified only by a truncated
SHA-256 fingerprint, which is enough to tell two secrets apart and to confirm a
rotation landed, and is not reversible to the secret.

## What I cannot do, stated plainly

I cannot rotate any of these. Rotation means signing into Anthropic, Weights & Biases
and GitHub account settings and handling the credential values directly, which is
outside what I am permitted to do regardless of authorization. **Every remediation
below is a command for you to run.** I have verified the current state live and given
exact commands; the account-side revocation step is yours.

## Live state, verified 2026-08-13 by direct read

The pasted RTFD report flagged one item here: "Vista OAuth token in plaintext
`~/.bashrc`. Flagged twice in this transcript. Not rotated." That is true and it is
**the least severe of the three findings.** The other two are new.

| host | file | mode | lines | variables |
|---|---|---|---|---|
| **Mac** | `~/.zshrc` | **644, world-readable** | 4 | `WANDB_API_KEY` x3 (:62, :77, :746), `GITHUB_PERSONAL_ACCESS_TOKEN` (:750) |
| **LS6** | `~/.bashrc` | 700 | 3 | `CLAUDE_CODE_OAUTH_TOKEN` x3 (:122, :123, :124) |
| **Vista** | `~/.bashrc` | 700 | 1 | `CLAUDE_CODE_OAUTH_TOKEN` (:112) |

`~/.netrc` is clean of these patterns on all three hosts (Mac 600, LS6 600, Vista 600).
No group- or world-readable dotfile was found in either cluster home.

### Finding 1, highest severity: the Mac file is world-readable

`~/.zshrc` is mode **644**. Every other file in this audit is 600 or 700. Any local
account or any process running as another user can read a W&B key and a GitHub personal
access token. That is a weaker boundary than either cluster, and the report did not
mention it at all.

The GitHub PAT is the one to treat as most valuable: this repo pushes to
`https://github.com/jcerrell-IS/can-it-ford.git` over HTTPS, so a PAT with write scope
is push access to the project.

Prior context worth re-checking rather than trusting: memory `wandb-key-401-broken`
records the Mac W&B key as resolved on July 13 with an exposure scan clean, but also
records that **revocation of the old key on wandb.ai was never confirmed.** Three
copies of `WANDB_API_KEY` in one file is consistent with an old value never having been
removed.

**Fix the permission first. It is one command, instant, and reversible:**

```bash
chmod 600 ~/.zshrc
```

### Finding 2: LS6 carries three CLAUDE_CODE_OAUTH_TOKEN exports, not one

Lines 122, 123 and 124 of `~/.bashrc` are three separate `export` statements for the
same variable. Fingerprints show **two distinct secrets**: `8268cab1` on :122 and :123
(the same value written twice), and `4dbb662c` on :124.

Shell semantics mean **:124 wins**, so the effective LS6 token is `4dbb662c` and the two
`8268cab1` lines are dead code that still leaves a live secret on disk.

### Finding 3: three distinct tokens exist across the two clusters

| host | line | fingerprint | effective |
|---|---|---|---|
| Vista | :112 | `c7274155` | yes |
| LS6 | :122 | `8268cab1` | no, overridden |
| LS6 | :123 | `8268cab1` | no, overridden |
| LS6 | :124 | `4dbb662c` | yes |

**These are three different secrets, so rotating one does not cover the others.** The
report's framing, a single Vista token, would have left `8268cab1` and `4dbb662c` in
place. Re-check the fingerprints after any rotation to confirm which lines actually
changed.

## Remediation, in order

1. **Permissions, immediately.** `chmod 600 ~/.zshrc` on the Mac. The cluster files are
   already 700.

2. **Revoke, account side, by you.** Anthropic account settings for both
   `CLAUDE_CODE_OAUTH_TOKEN` values, wandb.ai settings for the W&B key, GitHub developer
   settings for the PAT. Until this is done the values stay valid no matter what the
   files say. This is the step that actually closes the exposure; deleting the line only
   removes the copy.

3. **Remove the dead LS6 duplicates.** Lines 122 and 123 are overridden and serve no
   purpose. Back up first, and edit rather than truncate:

   ```bash
   ssh ls6 'cp ~/.bashrc ~/.bashrc.bak-2026-08-13 && sed -i "122,123d" ~/.bashrc && grep -c CLAUDE_CODE_OAUTH_TOKEN ~/.bashrc'
   ```

   Expect `1`. If it prints anything else, restore from `~/.bashrc.bak-2026-08-13` and
   re-inspect, because the line numbers will have moved.

4. **Prefer a mode-600 secrets file over a dotfile that is read by every shell.** Move
   each export into `~/.config/secrets.env` at 600 and source it. This does not reduce
   exposure on its own, but it stops the next credential from landing in a file that has
   already been world-readable once.

5. **Re-audit.** Re-run the fingerprint check after rotation and confirm every value
   changed:

   ```bash
   ssh ls6 'grep -E "^export CLAUDE_CODE_OAUTH_TOKEN=" ~/.bashrc | sed -E "s/^[^=]*=//" | tr -d "\"" | while read v; do printf "%s" "$v" | sha256sum | cut -c1-8; done'
   ```

## Status

**OPEN.** Nothing above has been changed by me. This is the third recorded mention of
the Vista token and the first of the other two, so the count in any future summary
should be "three hosts, four credential types, none rotated," not "the Vista token."
