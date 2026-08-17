# Credential rotation checklist. Run top to bottom.

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**No credential value appears in this file. Fingerprints only.**

> ### Three things to carry into every row below
>
> **1. The public surface is 35 BRANCHES, not one tree, and it GREW from 30 while
> this dispatch ran.** `origin` has 35 public branches (re-measured 2026-08-18). Any statement of the form "the repo is clean" that was established by
> scanning one tree does not cover it. Verified live 2026-08-16; this is what the
> correction in `5f01dd2` turned on, and it is the reason the "nothing is public"
> claim failed the first time.
>
> **2. The 11-of-12 gap is CLOSED, and it was my reading error, not a gap in the
> source.** The twelfth is **row 12: an unidentified 35-character secret**, mode
> `0644`, in a pane-capture export-state file. See section 0.2(a). The source had all
> twelve enumerated at its line 123 the whole time; I had skipped that section.
> **All twelve are named. None is rotated.**
>
> This does **not** make the list provably complete: see point 3, and note that the
> source itself calls 15 a **lower bound in two independent senses**.
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

> ### CORRECTION 2026-08-16: this file substantially DUPLICATES work that already existed
>
> The first revision said of `CREDENTIAL_EXPOSURE_2026-08-13.md`: *"That document is
> complete and correct; it is not runnable. This is."* **That was wrong.** It is
> runnable, and had been all along.
>
> At **line 123** it carries a section headed **`# ROTATION LIST, START HERE`** with
> **12 numbered rows ordered by blast radius**, each giving Cred, Service, Where it
> lives, Mode, Cloud-synced, In git history, and Rotate at. That is precisely the
> deliverable I was asked to produce, column for column.
>
> **I listed that heading in my own first read of the file and then never opened it.**
> I read the headings, jumped to sections 1 and 5, built a checklist from those, and
> reported a gap ("I can name 11 of a stated 12") that the section I had skipped
> answers directly in its row 12.
>
> **What this file still adds, and it is narrower than first claimed:** the public-surface
> findings (35 branches; the FLAG document public on one of them), the two-part public
> status, the divergent-copies hazard in section 0.1 below, and the three defects in
> section 0.2. **For the rotation itself, use the source document's own list**, with the
> corrections below applied to it.

This is a **companion** to `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`, not a replacement.
Row numbers below refer to **that document's** rotation list, so the two cannot drift
apart.

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
directly off `origin/main` blob `1a868f3`: `token_setup_template.md` (969 B) and
`HANDOFF_AUDIT_2026-07-24/topics/security/secrets-and-env.md` (1,936 B). **Both contain
zero token-shaped strings.** Part 1 survives. [read]

**Per-branch presence re-derived 2026-08-18 rather than renumbered**, because these are
measurements and not just a count: `token_setup_template.md` is on **34 of 35** branches
(it was on all 30, so one of the five new branches lacks it),
`secrets-and-env.md` on **32 of 35**, and the FLAG document on **1 of 35**. The value
scan is unchanged: still zero token-shaped strings in either file.

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
duplicate exports actually wins. It is on exactly **one of the 35** branches. [read,
re-measured 2026-08-18]

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

## 0.1 HAZARD: the credential document exists in two divergent copies, and the one at the obvious path is the STALE one

Verified live 2026-08-16 by reading both. [read]

| Copy | Lines | sha256 (16) | Title | Scope |
|---|---|---|---|---|
| `docs/CREDENTIAL_EXPOSURE_2026-08-13.md` **in the main checkout, UNTRACKED** | **118** | `73151d952bb572c8` | "plaintext CLAUDE_CODE_OAUTH_TOKEN in cluster shell startup" | **Vista + LS6 only.** Says "MacBook: no `~/.bashrc` exists, **0**" |
| Same path on branch `claude/credential-exposure-2026-08-13-DO-NOT-PUSH` | **1,196** | `a5740746a85fbbb6` | "plaintext tokens on Vista, LS6 and the MacBook" | All three machines, 12 credentials, 15 files |

**The 118-line copy is the superseded first revision.** It predates the entire Mac
sweep. It states the Mac is clean, when the Mac in fact holds credentials D, E, F, G,
both HF tokens, W&B and the unidentified row 12. **Anyone who opens the obvious path
and follows it will perform a two-machine rotation and believe they are finished.**

It is also **untracked**, so it has no history, no owner, and will never be updated.

**The authoritative copy is the 1,196-line one on the DO-NOT-PUSH branch.** Retrieve
it with:

```bash
cd /Users/josie/can-it-ford && git show \
  claude/credential-exposure-2026-08-13-DO-NOT-PUSH:docs/CREDENTIAL_EXPOSURE_2026-08-13.md | less
```

**Recommended:** replace the stale main-checkout copy with a one-line pointer to the
branch, or delete it. **Not executed:** it is an untracked file in the main checkout,
which is another session's tree, and deleting it needs Josie's go-ahead. Note that the
`fork-credentials-DO-NOT-PUSH` **worktree** has already been removed; the branch and
the blob both survive, so nothing was lost, but the convenient way to read it is gone.

---

## 0.2 Three defects in the source's own rotation list

Found by reading it against the rest of its own document. All three affect execution.

**(a) Row 12 is the credential I could not previously name.** It closes the 11-of-12
gap: **unidentified, 35 characters**, in
`~/<redacted path>/_inbox/.export_state/panes/today-work__0.1.txt`, mode **`0644`**,
echoed into a pane capture. Not cloud-synced, not in git history. The source's own
instruction is **"identify before acting. Shorter than a full token, may be
truncated."** Treat it as a credential until shown otherwise: 35 characters is short
for a modern token but ample for an API key.

**(b) RESOLVED 2026-08-16, and the resolution overturns what I wrote here first.
Row 1 is CORRECT. Revoke H exactly where it says.** [read]

The earlier revision of this section called row 1 "the worst single defect here",
on the grounds that three places in the source call H a Copilot MCP bearer while
only row 1 calls it a GitHub fine-grained PAT, and that revoking the wrong issuer
would leave H live. **That is withdrawn. Row 1 was right and I was wrong.**

Settled from the primary source, the config file itself:

| Evidence | Result |
|---|---|
| Endpoint the `Bearer` header is sent to | **`https://api.githubcopilot.com/mcp/`** |
| Secret length | **93 characters** |
| Secret prefix class | **`github_pat_`** |

`api.githubcopilot.com` is a **GitHub** domain, and a 93-character `github_pat_`
value is the GitHub **fine-grained PAT** format exactly. It matches the source's own
93-character figure for H at its line 432.

**So the two descriptions were never in conflict.** H *is* a GitHub fine-grained PAT
(what it is), *used as* a Bearer token against GitHub's Copilot MCP endpoint (how it
is used). Line 444's "a `copilot.com` MCP endpoint" is imprecise about the host, which
is what made it look like a different issuer. **Row 1's destination, github.com ->
Developer settings -> Fine-grained tokens, is the right place.**

Expect one side effect: revoking H **breaks the `github` MCP server** until a
replacement is minted. That is correct behaviour, not a symptom.

**My method was the error, and it is worth naming.** I counted mentions, three against
one, and treated the majority as evidence. Mentions are not independent sources: all
four were describing the same credential, and three of them were describing its
*usage*. One look at the primary source settled in a single step what no amount of
weighing secondary descriptions could. This is the project's own "one source cited
twice is not two sources" rule, met from an unfamiliar direction.

**No credential value was read to establish any of this.** See L-C in
`E8_METHOD_LESSONS_2026-08-16.md`: hostnames were extracted with `grep -o`, which emits
only the matched substring, and the format was reported as length plus prefix-class
plus entropy, never as characters.

**Bonus negative, recorded so nobody adds a phantom 13th item.** The same file has a
*second* `github` MCP entry pointing at the same endpoint, whose Bearer value is **15
characters**. It is **not a credential**: uppercase-and-underscore only, no digits, no
lowercase, 12 distinct characters, Shannon entropy **3.51 bits/char** against roughly
5.5 to 6.0 for a random token. That is a **placeholder string**. The count stays at 12.

**(c) The source's rotation list repeats the "nothing is public" overstatement.** Line
131 reads: *"**Nothing here is public.** Every item below is local or on TACC."* The
correction in `5f01dd2` applies to the source document too, not only to this file: no
credential **value** is public, **and** a document enumerating the holders is public on
one of 35 branches. Whoever owns the source should carry that correction across.

---

## 0.3 The exposure is cloning itself RIGHT NOW. Measured, not recalled.

The source document says the exposure "is growing on its own". That is testable, so I
tested it, at 2026-08-16 ~22:30 local: [read]

| Measurement | Value |
|---|---|
| `~/.claude/backups/.claude.json.backup.*` files present | **5** |
| Of those, carrying a real token format (`github_pat_`, `ghp_`, `hf_`, `sk-ant-`) | **5 of 5** |
| Age of the newest | **57 seconds** |
| Span across all five | **6 minutes** |

**N = 5, all five positive, spread 57 s to ~7 min.** Every one of those files was
written by ordinary Claude Code activity, and each carries a live credential format.
The set rolls continuously.

**This is the strongest single argument for revoking rather than deleting.** You cannot
win a deletion race against a process that writes a fresh copy every minute or two, and
the older copies have already propagated into backups and history. Revocation at the
issuer ends it in one action; deletion cannot.

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
