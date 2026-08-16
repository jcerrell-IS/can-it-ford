# Credential rotation checklist. Run top to bottom.

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**No credential value appears in this file. Fingerprints only.**

> ### Three things to carry into every row below
>
> **1. The public surface is 30 BRANCHES, not one tree.** `origin` has 30 public
> branches. Any statement of the form "the repo is clean" that was established by
> scanning one tree does not cover it. Verified live 2026-08-16; this is what the
> correction in `5f01dd2` turned on, and it is the reason the "nothing is public"
> claim failed the first time.
>
> **2. This list is NOT declared complete.** The source document states **12**
> credentials from the completed 89-root sweep. I can name **11**. One is
> unaccounted for **in my reading**, not in the source. Reconcile against §2.36's
> own enumeration before treating this as finished.
>
> **3. Coverage has a floor, and it is not zero.** **19 of 89 Mac roots are
> `partial`**, meaning unchecked below the per-root time cap rather than clean,
> including `~/Downloads`, `~/Library`, `~/Documents`, `~/Desktop` and `~/.claude`.
> Files over 8 MB (238 of them) were excluded by design. A credential in any of
> those would not appear in any count here.
>
> None of the three is a reason to delay Step 1. All three are reasons not to
> declare the job done after it.

## What this is, and what it is not

This is the **execution** half of `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`, which is
1,196 lines of diagnosis on an unpushed DO-NOT-PUSH branch. That document is complete
and correct; it is not runnable. This is.

Every row below is **derived by direct read** of that document's sections 1, 2.36, 3
and 5 in this session. **Nothing here was re-measured against the live filesystem**,
so treat file counts as of 2026-08-14, not as of today. Where I could not name
something from the sections I read, I say so rather than fill it in.

**Status as of this writing: ZERO of these have been revoked.** [read]

### The public status is TWO-PART. State both halves or the conclusion inverts.

**CORRECTED 2026-08-16, same day.** An earlier revision of this file, and commit
`30dee69`'s message, said "unlike the E8 geometry exposure, NOTHING here is public."
**That was a real error and it is withdrawn.** It was true of credential *values* and
false of the *exposure record*, and it stated only the reassuring half.

**Part 1, no credential VALUE is public.** All 848 tracked files scanned, 0 credential
hits; `.env` is gitignored with 0 commits adding it. [read, source doc §2.36]

Re-verified independently this session, and extended: **the repo has 30 public
branches**, so a scan of one tree is not a scan of the public surface. The two
credential-named files that appear on effectively every branch were value-scanned
directly off `origin/main` blob `1a868f3`: `token_setup_template.md` (969 B, on all 30
branches) and `HANDOFF_AUDIT_2026-07-24/topics/security/secrets-and-env.md` (1,936 B,
on 28). **Both contain zero token-shaped strings.** Part 1 survives. [read]

**Part 2, a document enumerating the HOLDERS is public.**
`docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`, blob `a7ad33e5`, 5,517 bytes, is on the
public branch `claude/rtfd-test-phase-1-4-569130` at
`aacd21f2ff2aa78856945d1830dd7809269794f4`. Found by D3, and verified here
independently: `git ls-remote` returns that exact SHA, and `git ls-tree` on the
fetched tree lists the blob. A six-pattern value scan of it returns **0 matches**, so
it leaks no value. [read]

What it does publish is the **targeting map**: host names (Vista, LS6, Mac), the
holding file (`~/.bashrc`), its mode, **the exact line numbers of the export
statements** (`:112`, `:122`, `:123`, `:124`), token fingerprints, and which of the
duplicate exports actually wins. It is on exactly one of the 30 branches. [read]

**Therefore the correct conclusion is the opposite of the one the old sentence
supported.** An attacker reading that file knows precisely which machines to aim at,
which file to read, and which token is live, and **every credential it describes is
still unrotated**. Public targeting plus live credentials raises urgency; it does not
lower it.

It also changes what Step 2 is worth. Deleting the local copies is not merely tidying,
it is now **incapable of undoing the public half**: removing the file from HEAD does
not unpublish it, and GitHub has served removed blobs by SHA after a `filter-repo`
rewrite **in this very account**. [recalled: project memory, the W&B key precedent]

The other reasons deletion cannot win, unchanged:

- Anthropic tokens A, B and C are in **TACC's backup system** (TACC backs up `$HOME`),
  which no file deletion you perform now can reach.
- Credential A is additionally in **iCloud**, via a `0644` file on the Desktop mirror.
- Credential H is in **89 `~/.zsh_sessions/*.history` files**, self-cloning on every
  new shell.

**Revocation at the issuer is the only remedy that reaches any of this.** Do Step 1
before Step 2, and do not let the deletions in Step 2 create the impression that the
public half has been handled. It has not, and it cannot be.

---

## Step 0. Before anything: confirm nothing is mid-run

Removing an export does not disturb an already-running process (its environment is
inherited and fixed), but any session that restarts loses the token.

```bash
cd /Users/josie/can-it-ford && scripts/tacc.sh vista --status; scripts/tacc.sh ls6 --status
```

Expected: both queues empty. If a job is running, either wait or accept that a
restart of that job will fail auth.

---

## Step 1. REVOKE, ordered by blast radius

Do these **in a browser, yourself**. Do not delegate any of them to a Claude Code
session, and do not paste any replacement value into a chat, a transcript or a commit.

Blast radius here means impact if abused, weighted by how far the value has already
spread. Grouped by issuer page where the ordering allows, because that is how it is
actually executed.

### GitHub. Highest impact: write access to a PUBLIC repository.

Page: **github.com, Settings, Developer settings, Personal access tokens.**

| # | ID | Kind | Holding location | Mode | Cloud-synced | In git history | Notes |
|---|---|---|---|---|---|---|---|
| 1 | **E** `1d115dbf7486af29` | PAT, fine-grained, 93 ch | Mac, 2 files, exported into **every shell** | see §2.3 of source doc | no | **no** | **Do this first.** Write access to the public repo. Revoking breaks the `github` MCP server until replaced; that is expected. Mint the replacement fine-grained and scoped to only the repos that need it. |
| 2 | **F** `see source §2.35` | PAT, classic, 40 ch | Mac, captured from `gh auth token` output into a saved shell log | n/a | no | **no** | May be the token backing `gh` itself. If `gh` stops working after this, that is the cause: fix with `gh auth login`. |
| 3 | **D** `91be9947de2a3b43` | PAT, classic, 40 ch | Mac, 2 files | see §2.3 | no | **no** | Marked `dead-credential`: superseded in bash's resolution order, **still valid at the issuer**. Revoke anyway. |

### Copilot / MCP. Widest spread of any single credential.

| # | ID | Kind | Holding location | Mode | Cloud-synced | In git history | Notes |
|---|---|---|---|---|---|---|---|
| 4 | **H** | Copilot MCP `Bearer` | **92 files**: 89 × `~/.zsh_sessions/*.history`, plus 7 `.claude.json` backups | n/a | no | **no** | Issuer: github.com Copilot, or the MCP endpoint that issued it. The source doc calls revoking H **"the highest-leverage single action available"** because every zsh session that touched it wrote it into its own history. 137 such history files exist, 38 MB total. Deleting files cannot win against a self-cloning mechanism; revocation can. |

### Anthropic. In TACC backups and iCloud, both beyond the reach of file deletion.

Page: **Settings, then Claude Code.** The listing shows issued tokens with a
**trash-can icon per token**. Revoke **all three**: revoking one leaves the others
live.

| # | ID | Kind | Holding location | Mode | Cloud-synced | In git history | Notes |
|---|---|---|---|---|---|---|---|
| 5 | **A** `017b17c44218d178` | OAuth, 108 ch | Vista (2 files), Mac (1 file) | **`0644`** on `~/Desktop/new_token.txt` | **YES, iCloud** | **no** | Worst spread of the three: world-readable mode **and** cloud-synced **and** in TACC backups. Identity across Vista and Mac is a digest match, not an inference. |
| 6 | **C** `dce91aa99860205d` | OAuth, 108 ch | LS6, 8 files | see §2.2 | no (TACC backups) | **no** | The token LS6 actively uses. Revoking it will break LS6 sessions until re-auth. |
| 7 | **B** `1e4bf74a8655e9bb` | OAuth, 108 ch | LS6, 8 files | see §2.2 | no (TACC backups) | **no** | `dead-credential`, still valid at the issuer. |

**Re-authenticate with `/login`, NOT `claude setup-token`.** This account is
`organizationType = "claude_max"`, `seatTier = None`, read from `~/.claude.json`.
`setup-token` is an Enterprise path and does not apply. (`organizationRole = admin`
means admin of a Max org, and misleads here.) [read from source doc §5]

**Do not write the new token to `~/Desktop/new_token.txt`.** That is exactly how
credential A reached a `0644` file and then iCloud.

### Remaining issuers, one action each

| # | ID | Kind | Holding location | Mode | Cloud-synced | In git history | Where to revoke |
|---|---|---|---|---|---|---|---|
| 8 | `WANDB_API_KEY` | W&B API key | backup repo `.env`; `~/.secrets_tmp/wandb_token.txt` | **`0644`** in a `0700` dir | no | **no** | wandb.ai, Settings. **Precedent worth not repeating:** per `docs/SECURITY_ACTIONS_2026-07-31.md` a W&B key was once rotated but never revoked and stayed live. Revoke, do not merely replace. |
| 9 | `HF_TOKEN` #1 | Hugging Face | `~/can-it-ford/.env` and backup copies; `~/.secrets_tmp/hf_*.txt` | **`0644`** in a `0700` dir | no | **no** (`.env` gitignored, 0 commits add it) | huggingface.co, Settings, Access Tokens |
| 10 | `HF_TOKEN` #2 | Hugging Face, **a second, distinct token** | see source §2.36 | see source | no | **no** | huggingface.co, same page. Easy to miss because it looks like a duplicate of #9. It is not. |
| 11 | **G** `hub_key` | unknown issuer | `~/can-it-ford/.env` and the backup repo's `.env` | n/a | no | **no** | **Identify the issuer from the `.env` first**, then revoke there. This is the one row that needs a lookup before it can be executed. |

**Count discipline.** Source doc §2.36 states **12 credentials** from the completed
89-root Mac sweep. I can name **11** from the sections I read (A through H, two HF
tokens, W&B). **One is unaccounted for in my reading**, not in the source. Before
declaring this list complete, reconcile against §2.36's own enumeration. Do not treat
11 as the total.

Also note the source's own bound: **15 is a lower bound in two independent senses**
(§2.4, §718), and 19 of 89 Mac roots are `partial`, meaning unchecked below the
cap rather than clean, including `~/Downloads`, `~/Library`, `~/Documents` and
`~/Desktop`.

---

## Step 2. Only after Step 1 confirms the old values are dead: remove the copies

Full per-file removal commands are in source doc §5 Step 2 and are not duplicated
here, because they must be run against the live filesystem and this file is a day
older than that one. Two things worth carrying forward:

- Fix Vista `~/.env_mcp` mode while you are there. It is `0644`. It is currently
  protected only by `$HOME` being `drwx------`, and `/work/11603/jcerrell0629/vista`
  is already `drwx-----x`, so a copy to `$WORK` turns a latent defect into an active
  leak.
- `~/.secrets_tmp/` has the same shape: three `0644` files protected only by a `0700`
  directory.

### Step 2b. The public branch. Decide, do not drift.

`claude/rtfd-test-phase-1-4-569130` carries the targeting document described above.
**Nothing here has been executed; deleting a remote branch is a destructive remote
action and needs your explicit go-ahead.** The options, with what each actually buys:

| Option | Effect | Honest limit |
|---|---|---|
| Leave it | no action | targeting stays public and indexable while the credentials are live |
| Delete the remote branch | removes it from the branch list and from search | **does not unpublish.** The commit SHA still resolves, and GitHub has served removed blobs by SHA in this account before |
| Delete the branch **and** ask GitHub Support to purge unreferenced objects | the only path that actually removes it | needs a support ticket; still no guarantee against anything already crawled |
| Revoke everything in Step 1 first | makes the map worthless | **this is the one that works.** A targeting document that points at dead credentials is a liability of a much lower order |

**Recommendation: do Step 1, then treat the branch as a cleanup item rather than an
emergency.** Revocation defuses the public half far more completely than any deletion
can, and it is the only action here whose effect is not partly outside your control.

## Step 3. Decide the replacement path BEFORE deleting anything

Source doc §5 Step 3. If you delete first and decide after, you lock yourself out of
the machine you need in order to fix the machine.

## Step 4. Verify

Source doc §6. The verification that matters is **at the issuer**, not on disk: a
value can be absent from every file you know about and still be live in a backup.

---

## What I did not do

- **I did not re-run the filesystem sweep.** Every file count and mode here is as of
  2026-08-14, read from the source document. If files have moved since, this list is
  stale in the direction of undercounting.
- **I DID re-verify the public-surface claim live**, this session, and that is the one
  claim in this file not inherited: `git ls-remote` for the branch and SHA,
  `git ls-tree` on the fetched tree for the blob, and six-pattern value scans of the
  three credential-named files that are public. This is also the claim I got wrong in
  the first revision, which is why it is the one I re-derived rather than carried.
- **The branch sweep inspected trees already present locally.** All 30 resolved, but a
  branch whose tree was absent would have been reported as not inspected rather than
  silently passed. None was. The sweep matched on **filename**, so a credential sitting
  in a file with an unrelated name on a non-main branch would not appear; the
  value-based negative comes from the source doc's scan of tracked files, not from
  this one.
- **I did not print, read or resolve any credential value.** Reads of the source
  document were passed through a redaction filter for token-shaped strings, because
  the source itself records that a prior session leaked a token into its own
  transcript while investigating, which made that transcript a credential-bearing
  location. That failure mode is the reason this file carries fingerprints only.
- **I did not revoke, delete, or modify anything.** Diagnosis only, per dispatch.
- **I did not verify the `~/.claude.json` account-type read** that makes `/login`
  correct rather than `setup-token`. It is the source doc's live read from
  2026-08-14, and it matches project memory. Re-check on the clusters if either
  authenticates as a different account.
