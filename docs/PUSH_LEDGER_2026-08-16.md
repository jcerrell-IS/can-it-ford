# PUSH LEDGER, 2026-08-16

D3 SAFE-THE-WORK. Every number below was measured live on 2026-08-16 against
`/Users/josie/can-it-ford`, git 2.50.1 (Apple Git-155), in two passes: sections
1 to 7 between **15:01 and 16:02**, sections 6 (owners), 9 and the off-machine
plan between **21:00 and 21:15**. Each section names the command that produced
it, so it can be re-derived rather than trusted. Claims are tagged **read**
(direct measurement), **inferred**, or **UNREVIEWED** (no independent check run).

Counts in a repo three sessions are actively committing to are timestamps, not
constants. Where a number moved during the session, both readings are given.

### Corrections to commit 7d1ec34, made the same day

`7d1ec34`'s commit body ends "all four round-5 sessions share one worktree and
one index". **The index half is RETRACTED**, on the coordinator's independent
inode measurement and my own re-measurement, which agree exactly. The four
worktrees have four separate indexes; what they share is the object store, the
refs namespace, config and hooks. Full correction in section 7. The commit body
cannot be edited without rewriting history, so it will keep propagating the wrong
claim; cite this section, not that commit message.

Two claims in that commit body **stand**, both re-checked: the public
`FLAG_CREDENTIAL_EXPOSURE` file (section 5, now confirmed on two separate
origins) and the register merge result (section 6).

### Where to look

Sections were added as work landed, so they are not in numeric order in the
file. **If you read only one, read 12.**

| | |
|---|---|
| **12** | **RECOVERY RUNBOOK.** What to actually do when something is lost. Drilled end to end. |
| 1 | The bundles, the restore test, `refresh_bundle.sh`, and the off-machine plan awaiting Josie |
| 2 | Why "188 across 11" and "241 across 33" are both right |
| 3 | What `pushcheck` really is, and the two things it cannot check |
| 4 | Per-branch push verdicts, 33 branches |
| 5 | **The credential flag file is already public.** Confirmed on two origins |
| 6 | **Register collision: side A is orphaned.** The sequenced plan, with owners |
| 7 | Shared pane cwd, and the shared-index claim I retracted |
| 9 | Branch taxonomy, and the NCAC/CCSA material on all 30 public branches |
| 11 | Coverage boundary: one machine only, and the open TACC gap |
| 10 | What I did not do, and what is therefore still unhandled |

---

## 1. The work is bundled. 36 bundles, all verified, restore tested

**read.** Output directory, outside the repo:

    /Users/josie/can-it-ford-bundles/2026-08-16/     1.0 GB, 36 .bundle files

| artifact | contents | bytes | verify |
|---|---|---|---|
| `ALL-refs.bundle` | 147 refs, self-contained, snapshot **15:02** | 507,116,489 | OK |
| `branch~*.bundle` x 33 | one per at-risk branch, thin, snapshot **15:02** | 1,142 to 7,082,463 | OK, all 33 |
| `INCREMENTAL-all-branches-1540.bundle` | all 33 branches' unpushed commits in one thin bundle, snapshot **15:40** | 7,609,387 | OK |
| `ALL-refs-MINUS-credentials.bundle` | 118 refs, self-contained, credential branch excluded, snapshot **21:10** | 507,228,906 | OK |

**Scope, because these are snapshots of a moving repo.** The 34 bundles at 15:02
cover the **241** commits at-risk at 15:02. The single incremental bundle at 15:40
covers the state after three sibling sessions committed, including this ledger's
own commit 7d1ec34, and is the cheap way to re-take the snapshot: 7.6 MB against
507 MB, because it carries only what origin lacks. Re-run it, do not re-run
`--all`, unless full standalone recovery is the goal.
sha256 of the incremental: `54d5ccebf7db12cf3dfb5fce8cd6afc337c9142ad16e49f473254bebf4256733`

Per-branch sizes, sha256 of every file, and head SHAs are in
`/Users/josie/can-it-ford-bundles/2026-08-16/ledger.tsv` (35 lines, tab
separated). Creation and verification logs sit beside it.

### The restore test, because `git bundle verify` is not proof of recovery

**read.** `git bundle verify` only asks whether the *current* repo can satisfy
the bundle's prerequisites. That is not the question that matters. The question
is whether a machine that has never seen this project can get the work back. So:

    git clone --mirror ALL-refs.bundle <virgin dir>

- All **33** at-risk branch heads matched the source repo exactly, SHA for SHA.
- All **241** at-risk commit objects were present in the restored mirror
  (`git rev-list --branches --not --remotes` piped through `cat-file -e` in the
  clone). Missing: **0**.

### The 33 per-branch bundles are NOT independent insurance

**read**, and this is the caveat that matters. They were created with
`--not --remotes`, so they are *thin*: they carry only the unpushed commits and
name the rest as prerequisites. Verified against an empty repo:

    error: Repository lacks these prerequisite commits:
    error: 240faeb238a8507c4da12f5b31ddef389fff0675

The same bundle verifies OK against the live repo. So a thin bundle restores
only alongside a copy of `origin`. Since `origin` is a public GitHub repo the
prerequisites are recoverable in practice, but do not describe these 33 files as
34 independent backups. **`ALL-refs.bundle` is the one artifact that stands
alone.**

### A bundle carries only committed work. What was uncovered, and now is

**read.** A `git bundle` snapshots refs. Anything uncommitted is invisible to it.
So I audited every one of the **28 worktrees** for dirty state
(`git status --porcelain` per worktree, plus `git ls-files --others
--exclude-standard`). Result: **24 clean, 2 with modified tracked files, 3 with
untracked files** (one worktree appears in both counts).

The one that mattered:

    concurrent-session-safety-570b39   claude/meta-prompt-reconcile-dispatch-14a3c8
    M scripts/canford_monitor.sh   +17 -3, uncommitted

That is a live in-progress edit to **the only copy of the safety tool in the
project** (section 3), and no bundle covered it. Snapshotted to
`can-it-ford-bundles/2026-08-16/uncommitted-worktrees-snapshot/` (mode 0700),
together with the untracked files in `ctx-census` (3), `orphan-rescue-token-
rotate-d72f90` (1) and `warpmpm-flood-vehicle-investigation-1b62fa` (2). Total
76 KB, with a sha256 MANIFEST.

**Proved, not asserted.** Applying the saved patch to the committed base
reconstructs the file at 432 lines from 418, and the reconstruction is
**byte-identical to the live dirty file**, sha256
`8f46d510274633113f5ec058ed432bb7f4fbe578f80ff3c7c7e636ccb904c9a4` on both sides.
My first round-trip attempt "failed", because I applied the patch to the tree
that already contained it; that was a bad test, not a bad patch.

**read.** `git stash list` is empty in the shared repo, so no stashed work is at
risk. `ALL-refs.bundle` carries **all 77** local branches (verified by `comm`
against `git for-each-ref refs/heads`: zero live branches missing from it), plus
34 remote-tracking refs, 8 tags, HEAD and 27 worktree HEADs.

### A THIRD COVERAGE HOLE, found by D1: gitignored authored source

**read, 02:25.** A bundle covers refs. The uncommitted capture covers modified
tracked files and untracked files. **Neither covers a file that is gitignored**,
because `git ls-files --others --exclude-standard` excludes ignored paths by
definition. So there was a category of work covered by nothing at all, and D1
found a real instance sitting in it.

`deliverables/paper/overleaf/`: **28 files, 0 tracked**, hidden by a blanket
`deliverables/` rule at `.gitignore:80`, so `git status` does not even list it as
untracked. Verified independently: `git check-ignore -v` names that rule, `git
ls-files` returns 0, and **my own snapshot saw 0 of the 144 files under
`deliverables/`** while `ls-files --others` without `--exclude-standard` saw all
144. D1 reports it is the most careful version of the paper in existence
(convergence 8, uncertainty 2, GCI 1, against 3/0/0 in the compiled PDF).

**Now captured, and the capture is scanned.** 2,944 files are ignored repo-wide,
overwhelmingly generated output (1,601 under `renders/` alone), so a blanket
sweep would be wrong. The rule takes authored text extensions and excludes
generated trees:

    ignored-source-<HHMM>/ignored-source.tar.gz   157 files, 824,154 B, mode 0600
      deliverables 63   data 49   reference_docs 16   render_s2 9
      bridge 7   docs 5   files 3   paper 2   archive 2

**The first attempt was wrong and the scan caught it.** A wider rule pulled in
248 files including `_inbox/`, and **four of them matched value-shaped credential
patterns**, among them a `zshrc` section and two session logs. Rebuilt with
`_inbox/`, `session_archive/`, `logs/`, `.claude/` and `.remember/` excluded:
**0 credential matches**, paper's 8 section files present. Every rebuild is
scanned before the artifact counts.

`refresh_bundle.sh` now does this on every run, so the hole does not reopen.

**What I am NOT doing.** D1 correctly left the decision open, and it is not mine
to take: whether to un-ignore this, relocate it, or deliberately keep it out of a
public repo is Josie's call. **My job was to make sure it cannot be lost while
that is decided, and that is now true.** Note it is authored source rather than
build output, so "it is gitignored" is not by itself evidence anyone meant it to
be disposable.

### Insurance ages out. `refresh_bundle.sh`, and how to re-take it without me

**read.** The 15:40 snapshot was **12 commits stale within six hours**, because
four dispatch sessions were committing throughout:

    claude/r5-safekeeping  +4   7d1ec34 -> 5c1e99f
    claude/r5-exposure     +3   30dee69 -> ac9fb54
    claude/r5-physics      +3   cd46a42 -> cf9e85c
    claude/r5-research     +2   cf9edab -> 1b32f67

At-risk total moved **241 (15:02) -> 260 (21:21)**. A snapshot nobody re-takes is
insurance that silently ages out, so the fix is not another manual pass:

    bash /Users/josie/can-it-ford-bundles/refresh_bundle.sh          # ~8 MB, seconds
    bash /Users/josie/can-it-ford-bundles/refresh_bundle.sh --full   # also the ~507 MB standalone

It is read-only against the repo, takes no locks, touches no ref, writes only
under `can-it-ford-bundles/`, re-snapshots every dirty worktree as well, and
appends a row per artifact to `can-it-ford-bundles/refresh_log.tsv` with bytes,
sha256, ref count, at-risk count and verify verdict. **Run it at the end of any
working session.**

Current rows, both verify OK, 33 refs each:

    2026-08-16 2121  INCREMENTAL-all-branches-2121.bundle  7,617,689 B
    2026-08-16 2122  INCREMENTAL-all-branches-2122.bundle  7,610,725 B

**FAILURE PATHS NOW PRINT REMEDIES, 01:26.** A bundle failing `git bundle
verify` is a broken backup, and the script used to report that as the single
word `FAIL` in a log column. Both failure paths now say what to do: that the
bundle is not usable and must not be copied or counted as insurance, how to
diagnose it (`git fsck --strict`, then read the verify output), and where the
last known-good artifact is (the newest `OK` row in `refresh_log.tsv`).

### Two traps found while testing that, both of them mine

**1. Git bundles are not byte-reproducible. Never compare two by sha256.** The
two rows above were taken 61 seconds apart with **no commits in between**, and
differ by 6,964 bytes. Their **ref sets are identical**: all 33 tips match, and
the sorted tip-list hashes to `985fca2b...` for both. The difference is pack
encoding, nothing else. Comparing bundle checksums to decide whether content
changed would report a change that did not happen. **Compare
`git bundle list-heads`, not the file hash.** A sha256 on a bundle is for
verifying a *transfer*, which is what section 1's off-machine plan uses it for.

**2. RETRACTED, a test of mine that passed by comparing nothing.** I first tried
to compare the two bundles by mirror-cloning each and hashing `git rev-list
--all`. Both returned
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, which is the
sha256 of **empty input**. Both clones were empty, because a thin bundle cannot
be cloned standalone (that is the same property section 1 documents). Two empty
sets compare equal, so the test "passed" while measuring nothing. If a hash you
are comparing is `e3b0c44...`, you hashed nothing.

### The layered restore, proved end to end

**read.** The real recovery procedure is two artifacts, and it works:

    git init --bare <dst>
    git -C <dst> fetch <ALL-refs.bundle>                'refs/heads/*:refs/heads/*'
    git -C <dst> fetch <INCREMENTAL-...-2122.bundle>    'refs/heads/*:refs/heads/*'

Result in a virgin bare repo: **77 branches**, and
`claude/r5-safekeeping` resolves to **5c1e99f**, matching the live repo exactly.
So the 15:02 standalone plus the latest incremental reconstructs current state,
which is why the cheap refresh is sufficient day to day and `--full` is only
needed before something that risks the disk.

### Remaining exposure: everything is on one disk. OFF-MACHINE PLAN, NOT EXECUTED

The bundles sit on the **same physical disk** as the repo (`/dev/disk3s5`,
1.0 GB of bundles, 546 GB free). Disk loss still loses everything. **I have not
copied anything off this machine and will not without an explicit destination
from Josie.**

**This is not a neutral backup, and that is the whole reason it needs a decision.**
`ALL-refs.bundle` carries, in one file:

- `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`, on the DO-NOT-PUSH branch, which has
  never been published anywhere;
- `docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`, which names three machines,
  a world-readable file and three OAuth tokens (section 5);
- **160,308,908 B (160.31 MB, 152.88 MiB) of NCAC/CCSA material** on `main`
  alone: 4 upstream `.zip` distribution archives plus 14 LS-DYNA `.key` decks,
  including `yaris-coarse-v1l.key` at 42,846,753 B and
  `2010-toyota-yaris-detailed-v2j.zip` at 42,113,905 B (section 9). An earlier
  draft said "83.5 MB across 18 files"; that was wrong in both set and unit, see
  section 9.

### UPDATED 2026-08-17 23:26. THE LICENCE AXIS IS CLOSED. THE DECISION IS NOW ONE AXIS

This plan originally rested on **two** load-bearing objections to shipping the
full bundle: **unresolved third-party geometry**, and **credential-bearing
content**. The first is gone.

**Both as reports, dated, artifact pending. Neither is a confirmation, because
neither the coordinator nor I has seen the paperwork.**

| grant | provenance | strength |
|---|---|---|
| NCAC/CCSA meshes, decks, derived hulls, renders, AR&R report and its images | D2 `b63201e`, then `a386704` "permission granted, global, permits republication" | **a commit I read**, verified on `claude/r5-exposure` |
| Wiley/CIWEM, the 16 Smith-Modra-Felder files | D2 `2732e2b` "last licence item closed, credentials now the only open exposure" | **a commit I read**, verified on `claude/r5-exposure` |

**SHA now attached, 23:31.** I flagged the Wiley grant as a relay with no commit
behind it; D2 committed it as `2732e2b` and I verified it. Both grants are now at
the same provenance strength.

**D2's own note is worth carrying, because it is a correction to how I framed
this.** It harmonised the wording across all three grants from "Josie confirms"
to "Josie reports", and states the reason plainly: **a second and third report
arriving does not upgrade the first. Two reports are still two reports.** Three
grants, three separate rights holders (CCSA/GMU via NHTSA, Engineers Australia,
Wiley/CIWEM), three artifacts still to be filed. Nothing here has been read by
D2, the coordinator, or me.

The Wiley item is worth one line of care: **it was never one of this plan's two
reasons.** I repeated it earlier only as a carve-out so nobody would read the
30-of-30 table as fully cleared. Its clearance therefore **does not change my
reasoning further**, and I am not restating it as though it did.

### UPDATED 00:44: credentials are DEFERRED, which settles the choice

**read, D2 `1b67080`.** Two things landed, and only one changes my reasoning.

**Does not change it:** Josie reports **blanket** permission, "everything is
permitted and nothing prohibited", extending to Wiley/CIWEM and the UNSW WRL
figures. The licence axis was already closed in this plan, so this confirms it
rather than moving it. **I am adopting D2's precision on how to say it:** outside
this repo the accurate form is **"the project reports permission from each rights
holder"**, not "this material is unrestricted". Four bodies granted separately
(CCSA/GMU, Engineers Australia, Wiley/CIWEM, UNSW WRL), all four as reports with
artifacts pending. A third party redistributing CCSA material on the strength of
a summary line in this repo would be relying on something no licence file
supports.

**Does change it, and it is the deciding fact:** **credentials are DEFERRED, not
resolved.** 12 named, **0 rotated**, deprioritised by Josie, which is hers to
decide. D2 marked it deferred rather than closed precisely so a later reader can
tell which it was.

**So the "or" in my two-line choice has collapsed.** This plan offered the full
bundle on either of two conditions: a private encrypted destination, **or the
credentials dead first**. The second is now explicitly not happening in the near
term. That leaves:

| | |
|---|---|
| **`ALL-refs-MINUS-credentials-*.bundle`** | **the practical default.** Clear on the licence axis, and it does not carry the never-published exposure document. Ships anywhere. |
| `ALL-refs-*.bundle` | **private encrypted destination only**, and that is now its sole route rather than one of two. |

Nothing about this is an argument for rotating tonight. It is an argument for
using the MINUS-credentials variant, which exists exactly so a credential
decision never has to gate a backup.

### The off-machine decision, now one axis, for Josie

**On the licence axis the full bundle no longer carries an unresolved-rights
objection.** What remains is the credential axis alone, and the instrument for
it already exists. So the choice is two lines:

- **`ALL-refs-MINUS-credentials-2251.bundle`** (507,831,989 B, 123 refs,
  verify OK, controlled by mirror-cloning and confirming
  `docs/CREDENTIAL_EXPOSURE_2026-08-13.md` is unreachable) is **shippable to an
  ordinary destination tonight, clear on both axes.**
- **`ALL-refs-2251.bundle`** (507,891,648 B, 142 refs) needs **either a private
  encrypted destination, or the credentials dead first.** D2 records the
  credentials are entirely unaffected by any permission and that **none has been
  rotated**.

Commands and checksums are below. **Nothing has been copied; that step is yours.**

So the destination must be **private and encrypted**. A plain cloud sync is
disqualified: this project has already had a 0644 iCloud-synced token as part of
its credential exposure.

#### Two facts that make option 1 concrete, measured 22:29

**read.** **No external volume is attached.** `/Volumes/` holds only
`Macintosh HD` (`Removable Media: Fixed`) and two Xcode iOS simulator images,
both 98 percent full. So option 1 is not only a decision, it has a prerequisite:
**a disk has to be plugged in first.** Worth knowing before setting aside time
for it.

**read, and it corrects a wrong impression I nearly recorded.** The source disk
**is** encrypted at rest: `fdesetup status` returns **`FileVault is On.`**
`diskutil info /Volumes/Macintosh HD` reports `Encrypted: No`, which is the
wrong tool for this question and would have supported an alarming and false
claim. **Use `fdesetup status` for FileVault, never `diskutil`'s per-volume
flag.** Same class of error as `git cat-file -e` in section 3.

#### Permissions, fixed at the source rather than just on the artifacts

**read.** The bundle directory is `drwxr-xr-x` and every bundle was created
`-rw-r--r--`. `ALL-refs*.bundle` and every incremental **carry the DO-NOT-PUSH
branch**, and therefore the never-published
`docs/CREDENTIAL_EXPOSURE_2026-08-13.md`. On a FileVault-on single-user machine
this is a modest exposure at rest, but 0644 means any process running as any
user could read it, and it would follow the file into any copy.

Confirmed which bundles are affected rather than assuming, by
`bundle list-heads | grep credential-exposure`:

    CARRIES IT   ALL-refs-2207.bundle
    clean        ALL-refs-MINUS-credentials-2207.bundle

**Ten credential-bearing bundles are now `0600`**, and the credential-free
variants deliberately stay `0644` because they carry nothing sensitive and are
the ones intended for the cheaper destinations. Verified the change broke
nothing: `ALL-refs-2207.bundle` still verifies exit 0 with 138 refs readable.

**The generator is fixed too, which is the part that matters.** Tightening the
existing files alone would have been undone by the next refresh.
`refresh_bundle.sh` now chmods 600 at creation time for any bundle whose
`list-heads` includes the credential branch.

#### To make the choice cheap, a credential-free variant already exists

**read.** `ALL-refs-MINUS-credentials.bundle`, 507,228,906 bytes, verify exit 0,
sha256 `9144eca1ea3ce789e532498222e98fbef584d828763cd0ea8a1c0697650e6698`.
Built by passing 118 refs explicitly rather than with `--not`, which would have
dropped shared ancestors. **Controlled:** a mirror clone of it contains 76
branches, and `git log --all -- docs/CREDENTIAL_EXPOSURE_2026-08-13.md` returns
**nothing**. The FLAG file is still reachable in it, which is correct and
deliberate: it is already public, and excluding it would mean dropping
`claude/rtfd-test-phase-1-4-569130` and its 13 commits of real work.

#### Options, with consequences

| # | destination | covers | consequence |
|---|---|---|---|
| **1 (recommended)** | encrypted external volume, physically attached | `ALL-refs.bundle`, everything | offline, no third party, no network. Needs the disk plugged in. |
| 2 | private GitHub repo on the same account | `ALL-refs-MINUS-credentials.bundle` | off-machine and quick, but hands 507 MB including the unresolved CCSA material to a third party, on the same account whose public repo is the existing problem. |
| 3 | TACC `$WORK` on Vista or LS6 | either | **not available**: both sockets are cold pending Josie's token. Also inadvisable on its own merits: those machines already hold the unrotated OAuth tokens this bundle documents, `$WORK` is not encrypted at rest, and it is a shared academic filesystem. |
| 4 | any plain cloud sync (iCloud, Dropbox) | none | **disqualified**, see above. |

#### Exact commands, option 1

**USE THE 00:58 ARTIFACTS. The 15:02 ones are superseded.** The refresh
mechanism is why the worktree removal in section 13 was a non-event rather than
a loss, and it is also why these filenames changed. Coverage went from **241
at-risk commits (15:02) to 292 (00:58)**, so copying the older bundle would
silently omit 51 commits of work.

    # 1. copy, with the destination named explicitly
    cp /Users/josie/can-it-ford-bundles/2026-08-17/ALL-refs-0058.bundle \
       /Volumes/<NAME>/canford-2026-08-17/ALL-refs-0058.bundle

    # 2. verify the bytes survived the copy. Must print exactly:
    #    f205159510c889919c823977503bdbb904c7a89d4f303f190b08a2c3815ed83a
    shasum -a 256 /Volumes/<NAME>/canford-2026-08-17/ALL-refs-0058.bundle

    # 3. restore test AT THE DESTINATION, not here. Must print 77.
    git clone --mirror /Volumes/<NAME>/canford-2026-08-17/ALL-refs-0058.bundle /tmp/restore-check
    git -C /tmp/restore-check for-each-ref refs/heads | wc -l

    # 4. spot-check a tip against this branch's head at bundle time
    git -C /tmp/restore-check rev-parse claude/r5-safekeeping

For option 2, substitute `ALL-refs-MINUS-credentials-0058.bundle`, 507,477,822 B,
sha256 `879d800c9c7c816d81e563414714a267934b86c2bf26025b88c4a4ad43238a38`; step 3
must print **76**, not 77, and that difference is the check that the sanitisation
held.

| artifact | 15:02, superseded | **00:58, use this** |
|---|---|---|
| standalone | `ALL-refs.bundle`, 147 refs, 241 commits | **`ALL-refs-0058.bundle`, 137 refs, 292 commits** |
| credential-free | `ALL-refs-MINUS-credentials.bundle` | **`ALL-refs-MINUS-credentials-0058.bundle`** |
| incremental | `INCREMENTAL-...-1540` | **`INCREMENTAL-all-branches-0058.bundle`** |

The ref count falling 147 to 137 is **not** a loss: all 10 are
`worktrees/*/HEAD` pseudo-refs for the removed trees, and all 77 branches, 34
remotes and 8 tags are intact. Section 13 has the proof.

**Abort condition:** if step 2's sha256 differs, delete the copy and redo it. A
`cp` exit code of 0 is not evidence the bytes landed intact.

---

## 2. Corrections to the inherited counts

**read.** The round-4 reconciliation and the round-5 bootstrap both say
"**188 commits across 11 branches**". Live:

    git rev-list --count --branches --not --remotes         ->  248  (15:47)
    (per branch: git rev-list --count <b> --not --remotes)  ->  33 branches > 0

**248 commits across 33 branches**, deduplicated. Every count in this document is
a timestamp, not a constant: the repo-wide total was **241 at 15:02** and **248
at 15:47** because three sibling sessions committed while I measured. Quote the
time with the number or do not quote it.

### 188 was not arithmetically wrong. It was correct for a scope nobody stated

**read.** Splitting the 33 at-risk branches three ways:

| group | branches | commits |
|---|---|---|
| in `canford_monitor.sh`'s 13-row dispatch table | 11 | **189** |
| pre-existing, never in scope of any prior check | **17** | **55** |
| created after the round-4 check (2026-08-15 18:01) | 5 | 12 |

189 against the bootstrap's 188 is one commit of drift on the same branch set in
a day. **So the 188 reproduces.** It is not an undercount of what it measured; it
is an undercount of the repo, because 22 of 33 branches were outside a scope that
was never written down. This is the same failure CLAUDE.md item 13 already records
for DRIFT_THRESHOLD: a bare number is what is wrong, not any particular value.
189 + 55 + 12 = 256, above the deduplicated 248, because branches share commits
(777567a alone is the tip of five of them).

**The 17 pre-existing branches that were genuinely never checked**, with their
at-risk commit counts:

    claude/meta-prompt-reconcile-dispatch-14a3c8   8    <- holds canford_monitor.sh itself
    claude/fork-s3-rescue-2026-08-14               8
    paper/submission-close                         7
    paper/close-for-submission                     5
    audit/g-mergetest-2026-08-04                   5
    push-ready-2026-08-04                          4
    claude/reverent-heisenberg-fe731c              3
    analysis/failure-modes                         3
    reconcile/overleaf-base                        2
    claude/figure-validation-sources-826ba6        2
    claude/festive-goodall-e08861                  2
    warpmpm-continue                               1
    claude/verify-execute-code-changes-d89fd8      1
    claude/overleaf-gci-citations-2026-08-08       1
    claude/figure-verification-citations-f36b1c    1
    claude/can-it-ford-runs-analysis-4e93c6        1
    claude/bibliography-formatting-fix-4c3864      1

The first entry is the one that matters: the branch carrying the only copy of the
safety tool was itself outside the safety tool's scope. All 17 are bundled now,
and all 17 come back OK or FALSE_POSITIVE_ONLY in section 4.

The other 5 (`claude/add-ci-checks` at 2026-08-15 19:31, and the four `r5-*`
branches created today) post-date the round-4 check and could not have been in it.

---

## 3. What `pushcheck` actually is

This matters because "pushcheck passes on nine branches" is quoted as settled
state in both handoff documents.

**read.** There is no `pushcheck` command. It is a subcommand of
`scripts/canford_monitor.sh`, function body at lines 369-391. A `find` over
`/Users/josie` to depth 5 (excluding `Library/` and `.git/`) returned no file of
that name, and no shell rc defines it. The word appears in 7 markdown files, all
of them dispatch or tooling prose.

**read, and this is the finding.** `scripts/canford_monitor.sh` exists on
**exactly one ref out of 100+**:

    git for-each-ref refs/heads refs/remotes | while read b; do
      git ls-tree -r --name-only "$b" -- scripts/canford_monitor.sh; done
    -> claude/meta-prompt-reconcile-dispatch-14a3c8   (only)

It is **not on `main`, not on `origin/main`, and not in the main checkout's
working tree**. It is tracked on one branch that carries 8 commits existing on
no remote. Any session that ran `./scripts/canford_monitor.sh pushcheck` from
its own worktree got "No such file or directory". The tool that gates every push
decision in this project was itself the least-safe artifact in it. It is now
inside `ALL-refs.bundle` and has its own thin bundle.

### Tooling trap found while establishing that

**read, reproduced twice.** `git cat-file -e "<rev>:<path>"` returns **exit 0
for a path that does not exist in that rev**. The identical argument to
`git cat-file -t` returns 128 with `fatal: path ... does not exist`. An
existence sweep built on `cat-file -e` reported the file present on all 100+
refs; `ls-tree` reported 1. **Use `git ls-tree`, never `cat-file -e`, to ask
whether a ref contains a path.** I published the wrong answer from `cat-file -e`
mid-session before the control caught it.

### What the real rule checks, and what it cannot check

    files=$(git diff --name-only "main..$br")
    risky=$(echo "$files" | grep -iE '\.(ply|obj|stl|npz|npy|env|key|pem|pth)$|secret|token|credential|id_rsa')

Two structural limits, both **read**:

1. **Path names only.** It never opens a file. A credential pasted into a normal
   `.py` or `.md` file passes as OK. With 12 to 15 unrotated credentials live and
   the repo public, that is the gap that matters.
2. **Tip-versus-tip.** `git diff --name-only main..<br>` lists every path that
   *differs*, including paths `main` HAS and the branch LACKS. Verified on three
   flagged paths: `combine.key`, `car_mesh.ply` and `out/synthetic_test.npz` are
   all **PRESENT on main and ABSENT on `analysis/failure-modes`**. That branch is
   blocked for files it does not contain. It is blocked for deleting them.

---

## 4. The ledger, 33 branches

`atrisk` = `git rev-list --count <b> --not --remotes`.
`PATH_tip` = faithful replication of the legacy rule above.
`PATH_add` = the question that matters: paths **added** by the unpushed commits.
`CONT` = case-insensitive credential-pattern scan, both at the tip of every
touched file and across every **added line** in the unpushed range (the second
catches a secret committed and later removed, which a push still carries).

Verdict: `BLOCK_PATH` = adds a risky path. `FALSE_POSITIVE_ONLY` = the legacy
rule fires but the branch adds nothing risky. `OK` = clean on all four columns.

| branch | atrisk | PATH_tip | PATH_add | CONT | verdict |
|---|---|---|---|---|---|
| claude/fork-moving-driver | 30 | 0 | 0 | 0 | OK |
| claude/fork-protocol | 23 | 0 | 0 | 0 | OK |
| claude/fork-register-reconcile | 23 | 0 | 0 | 0 | OK |
| claude/fork-render-3class | 19 | 0 | 0 | 0 | OK |
| claude/fork-three-class | 19 | 0 | 0 | 0 | OK |
| claude/fork-scene | 16 | 0 | 0 | 0 | OK |
| claude/fork-validation | 15 | 0 | 0 | 0 | OK |
| claude/rtfd-test-phase-1-4-569130 | 13 | 1 | **0** | 0 | **FALSE_POSITIVE_ONLY** |
| claude/fork-chrono-eval | 12 | 0 | 0 | 0 | OK |
| claude/fork-vista-triage | 11 | 0 | 0 | 0 | OK |
| claude/credential-exposure-...-DO-NOT-PUSH | 8 | 1 | 1 | 0 | SKIP_BY_DESIGN |
| claude/fork-s3-rescue-2026-08-14 | 8 | 0 | 0 | 0 | OK |
| claude/meta-prompt-reconcile-dispatch-14a3c8 | 8 | 0 | 0 | 0 | OK |
| paper/submission-close | 7 | 33 | 0 | 0 | FALSE_POSITIVE_ONLY |
| audit/g-mergetest-2026-08-04 | 5 | 0 | 0 | 0 | OK |
| paper/close-for-submission | 5 | 33 | 0 | 0 | FALSE_POSITIVE_ONLY |
| push-ready-2026-08-04 | 4 | 0 | 0 | 0 | OK |
| analysis/failure-modes | 3 | 33 | 0 | 0 | FALSE_POSITIVE_ONLY |
| claude/reverent-heisenberg-fe731c | 3 | 6 | 0 | 0 | FALSE_POSITIVE_ONLY |
| **claude/r5-exposure** | **3** | 1 | **1** | 0 | **BLOCK_PATH** |
| claude/r5-research | 2 | 0 | 0 | 0 | OK |
| reconcile/overleaf-base | 2 | 33 | 0 | 0 | FALSE_POSITIVE_ONLY |
| claude/festive-goodall-e08861 | 2 | 0 | 0 | 0 | OK |
| claude/figure-validation-sources-826ba6 | 2 | 0 | 0 | 0 | OK |
| claude/overleaf-gci-citations-2026-08-08 | 1 | 33 | 0 | 0 | FALSE_POSITIVE_ONLY |
| claude/add-ci-checks, r5-physics, r5-safekeeping, bibliography-formatting-fix-4c3864, can-it-ford-runs-analysis-4e93c6, figure-verification-citations-f36b1c, verify-execute-code-changes-d89fd8, warpmpm-continue | 1 each | 0 | 0 | 0 | OK |

Tally: **24 OK, 7 FALSE_POSITIVE_ONLY, 1 BLOCK_PATH, 1 SKIP_BY_DESIGN.**
Full table with all four columns: `can-it-ford-bundles/2026-08-16/pushcheck_v3.tsv`.

### REFRESHED 00:45. A stale push ledger is a dangerous one

The table above is the **15:00** snapshot. Nine hours and roughly 60 sibling
commits later it could have been quietly wrong, and someone authorising a push
from a stale ledger is the exact failure this document exists to prevent. So it
was re-run in full. The 15:00 run is preserved for diffing at
`pushcheck_v3_1500.tsv`; the current run overwrites `pushcheck_v3.tsv`.

**Every verdict held.** 24 OK, 7 FALSE_POSITIVE_ONLY, 1 BLOCK_PATH, 1
SKIP_BY_DESIGN, unchanged. Only the four live dispatch branches moved at all:

| branch | at-risk 15:00 | at-risk 00:45 | verdict |
|---|---|---|---|
| `claude/r5-research` | 2 | **20** | OK, unchanged |
| `claude/r5-safekeeping` | 1 | **11** | OK, unchanged |
| `claude/r5-exposure` | 3 | **9** | **BLOCK_PATH**, unchanged |
| `claude/r5-physics` | 1 | **9** | OK, unchanged |

Sum of per-branch at-risk counts moved **252 to 294** (that sum double-counts
shared commits; the deduplicated repo-wide figure is **280** at 00:27). So
roughly **42 branch-commits of new work were scanned for credentials and
restricted geometry, and none was found.**

The single BLOCK_PATH is still D2's `claude/r5-exposure`, still for exactly one
added path, `docs/CREDENTIAL_ROTATION_CHECKLIST_2026-08-16.md`. It did not grow
despite that branch tripling in size, so D2's later six commits added nothing
further of that kind.

**FINAL, re-verified when D2 declared its scope complete.** That branch has since
grown to **14 at-risk commits** and adds **8 files** in total. Re-scanned at that
point:

- paths added matching the risk rule: **still exactly one**,
  `docs/CREDENTIAL_ROTATION_CHECKLIST_2026-08-16.md`
- credential-pattern hits in added lines across the whole unpushed range: **0**

So the verdict is settled and its basis is worth stating precisely, because
"BLOCK" reads worse than the facts warrant: **no credential value appears
anywhere on that branch.** It is blocked on the filename rule alone, because a
rotation checklist naming services and machines is a targeting document on a
public repo, which is the same reasoning that applied to
`FLAG_CREDENTIAL_EXPOSURE` in section 5. Read the file before authorising the
branch; do not read the verdict as "a secret was found".

### `claude/add-ci-checks` re-scanned 23:50, because it now carries side A

This branch was one line in the table above at **1 at-risk commit**. It is now
the most consequential branch in the repo for push purposes: the main checkout
sits on it, and it carries the register work, `CLAUDE.md`, a research corpus
index and a settling criterion.

    at-risk commits          1 -> 4
    files added by them      9
    paths matching the risk rule   0
    credential-pattern hits in added lines   0
    VERDICT                  OK, unchanged

    790d999  Hardwire the research corpus into every session and into CI
    46282bc  Index the external research corpus and make it queryable in-repo
    072e4f3  Add a data-driven settling criterion and probabilistic verdicts
    777567a  Add CI running the three existing checks

**Clean on all four columns**, so if any branch is authorised first, the evidence
supports this one. That remains Josie's call, not a recommendation to push.

**Standing watch on the orphaned register, same timestamp:** main-tree
`CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` still reads **760 lines**,
`CLAUDE.md` still **749**, and `git status` still shows the same four modified
files with nothing staged. **Side A is intact and still uncommitted**, now
roughly ten hours after it was written.

### One live BLOCK, and it is new

`claude/r5-exposure` (sibling D2, committing during this session) adds
`docs/CREDENTIAL_ROTATION_CHECKLIST_2026-08-16.md`. On a public repo a rotation
checklist is a targeting document by the same logic that blocked D1. **Do not
authorise that branch without reading that file first.**

### Why CONT is 0 everywhere, and what that is worth

**read.** Zero credential-pattern hits across all 33 branches, tip and diff.
That number is only worth anything with controls, and the controls found two of
my own defects before the final run:

- **plumbing control:** the same `git grep` pipeline returned 66 hits for a
  pattern known to be present. It fires.
- **regex control:** on a synthetic file, the v2 regex matched 2 of 3 planted
  keys. It missed `ZOTERO_API_KEY = "..."` because the pattern was lowercase and
  `git grep` was called without `-i`. **Every uppercase env-var assignment, the
  commonest credential form in this project, was invisible to v2.** v3 is
  case-insensitive and matches all 3.
- an earlier `printf '%s' | wc -l` counted **0 for a single match**, so v2 also
  under-reported every one-hit branch. Fixed in v3.

**Residual limits, UNREVIEWED:** the pattern requires 20+ characters of value
after the delimiter, so a short key is missed; and it will not catch a
credential with no recognisable prefix or label.

---

## 5. The D1 block is a false positive, and the file is already public

**CONFIRMED ON TWO SEPARATE ORIGINS.** This is the one finding here that is not a
single source cited twice. I reached it via `git ls-remote` plus
`merge-base --is-ancestor` against the local remote-tracking ref. The coordinator
reached it independently by fetching and running `git ls-tree -r --name-only
FETCH_HEAD` on the fetched tree, which does not depend on my local cache being
current. Both return the same remote tip and both list the file.

**read, verified against the live remote, not the local cache.**

    git ls-remote --heads origin refs/heads/claude/rtfd-test-phase-1-4-569130
    -> aacd21f2ff2aa78856945d1830dd7809269794f4

`docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md` (5,517 bytes) is in the tree at
that remote tip. It was added by commit **e431877** (2026-08-13, "Verify the RTFD
dispatches before executing them"), and `git merge-base --is-ancestor e431877
origin/claude/rtfd-test-phase-1-4-569130` returns **YES**. It is *not* an
ancestor of `origin/main`.

Its section headings, quoted without any values:

    # FLAG: plaintext credentials on three machines, 2026-08-13
    ### Finding 1, highest severity: the Mac file is world-readable
    ### Finding 2: LS6 carries three CLAUDE_CODE_OAUTH_TOKEN exports, not one
    ### Finding 3: three distinct tokens exist across the two clusters

**read.** None of the 13 unpushed commits on that branch touches it:
`git log <b> --not --remotes -- docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`
returns empty.

Three consequences:

1. **The proposed remedy is obsolete.** Splitting the file onto its own
   DO-NOT-PUSH branch cannot unpublish what is already served from a public
   repo. This is the same lesson already recorded for the Yaris hull: deleting
   does not unpublish, and GitHub has served a removed blob by SHA after a
   `filter-repo` pass in this project before.
2. **D1's 13 commits are not blocked by it.** They add no risky path and no
   credential pattern. On the evidence they are authorizable. That is Josie's
   call, not mine.
3. **The exposure is worse than the ledger recorded**, because it was booked as
   "blocked, therefore contained". It is not contained. **A document naming which
   machines hold unrotated credentials, which file is world-readable, and how many
   distinct tokens sit on which cluster is world-readable on GitHub right now**,
   and has been since 2026-08-13. The blocked-branch bookkeeping described a file
   that had already been published three days earlier.

**What to do instead** (proposal only, nothing executed):
- Rotation first. The document's own remediation section is the work item; the
  document's publication does not change what needs rotating, it changes the
  urgency.
- Only after rotation is confirmed does removal become a cosmetic question. If
  removal is still wanted it needs history rewrite plus a GitHub support request
  to purge cached blobs, and the `git-history-rewrite` skill should be loaded
  first.
- The sibling file `docs/CREDENTIAL_EXPOSURE_2026-08-13.md` on
  `claude/credential-exposure-2026-08-13-DO-NOT-PUSH` is correctly unpushed.
  Keep it that way, and add `claude/r5-exposure` to the same treatment until its
  new checklist is reviewed.

---

## 6. Register sequencing plan, with the merge measured rather than assumed

> **STEP 1 IS DONE, 23:38. The collision has changed shape and this plan is
> re-stated for it, not deleted.**
>
> Side A was committed as **`790d999`** "Hardwire the research corpus into every
> session and into CI" on `claude/add-ci-checks`, carrying **both** `CLAUDE.md`
> and the register. Verified independently by me and by the coordinator: register
> **760 lines with zero uncommitted delta**, `CLAUDE.md` **823 with zero delta**,
> and only `.claude/settings.json` and `.mcp.json` still modified in that tree.
> Side B is untouched at 1455 on `claude/fork-register-reconcile`.
>
> **The danger this plan was built around is gone.** It existed because side A
> was uncommitted, unowned and had no reflog entry, so a stray `checkout` would
> have erased it silently. **Both sides are now in git history on separate
> branches, so neither can silently disappear.** What remains is an ordinary
> two-branch merge, which is a much smaller problem.
>
> **What the numbers now mean, because one of them is unchanged for a different
> reason.** The old abort condition was "the register must read 760 before step
> 1". It still reads 760, but that now means **760 and committed** rather than
> **760 and pending**. Do not read the unchanged number as an unchanged
> situation.

### The live state

**read.** Main checkout is on `claude/add-ci-checks` at 777567a with exactly four
modified tracked files and nothing staged:

    .claude/settings.json    +9  -0
    .mcp.json               +22  -1
    CLAUDE.md               +73  -0
    docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md  +104  -0

Line counts: register 656 at HEAD, **760** in the working tree; CLAUDE.md 676 at
HEAD, **749** in the working tree. The bootstrap says "+96" and "752 vs 1455";
the live numbers are **+104** and **760 vs 1455**, because the session holding
that tree has kept editing.

**read, and it corrects the framing.** `CLAUDE.md` is blob `37983d2` at *all
three* of: base 1a868f3, main HEAD, and `claude/fork-register-reconcile` tip.
**There is no CLAUDE.md collision.** The branch never touched it. The only
CLAUDE.md risk is that 73 lines exist solely as uncommitted text.

The register is the real two-sided case:

    BASE  1a868f3 (= origin/main)              656 lines
    A     main working tree, uncommitted       760 lines
    B     claude/fork-register-reconcile      1455 lines, 25 of its 26 commits touch it

### The merge, actually run

**read.** Three-way merge of A into B, `git merge-file -p A BASE B`:

    exit status 0        (0 = clean; a positive value would be the conflict count)
    conflict markers     0
    result               1559 lines = 1455 + 104 exactly
    SUPERSEDED 00:36     side A grew to 803; the live target is now 1602.
                         This line is kept as the original derivation, not as current.

The reason is measurable, not a guess. A's entire change is one hunk,
`@@ -656,0 +657,104 @@`: a pure append past the end of the base file. B's 17
hunks all fall inside lines 19 to ~650 of the base. They cannot overlap.

### Who owns each side. Measured, not assumed

**read, 21:03.** I resolved each side to a live process rather than guessing:

| side | tree | owner | evidence |
|---|---|---|---|
| **B**, the 1455-line register | `.claude/worktrees/fork-register-reconcile` **(SINCE DELETED, see section 13)** | **`D4 REGISTER-RECONCILE`, process still alive, working tree gone** | pid 10363, `claude --model opus --effort max --name "D4 REGISTER-RECONCILE"`, pane `canford:4`. Its cwd no longer exists |
| **A**, the +104 uncommitted | main checkout `/Users/josie/can-it-ford` | **NOBODY** | no `claude` process anywhere has the main tree as cwd. The only process there is pid 98633, `bash .../canford_monitor.sh`, the round-3/4 monitor |

**This is the finding that makes the plan necessary. Side A is orphaned.** The
session that wrote those 177 lines is gone. Nobody is going to commit them on
their own initiative, and the register has sat at 760 lines unchanged since
15:07. It will sit there until a human acts.

A second-order note: that monitor is running **from the worktree holding the
uncommitted +17/-3 edit to `canford_monitor.sh`** (section 1b). The live monitor
is executing modified, uncommitted code.

### The sequence, with an owner per step

The danger is not the merge, which is measured clean. It is that 177 lines exist
only as uncommitted text with no owner. A `git checkout -- <path>`, a
`git stash`, or a branch switch in the main tree destroys them with no conflict
marker and no reflog entry.

**Step 0. Done, needed no permission.** The uncommitted state is snapshotted at
`can-it-ford-bundles/2026-08-16/uncommitted-maintree-snapshot/` (0700): the
four-file patch, raw copies, 94 untracked files, sha256 MANIFEST. The patch
re-applies cleanly onto 777567a in a throwaway clone. **Insurance only. It does
not replace step 1**, and a snapshot outside git is not something anyone will
find in a year.

**Step 1. DONE, `790d999`, 2026-08-17 23:38.** Side A is committed on
`claude/add-ci-checks` with both files. `.claude/settings.json` and `.mcp.json`
remain uncommitted there and are a separate unit of work, unrelated to this
collision.

### Merge target: COMPUTE, do not quote

**DO NOT QUOTE A FIXED TARGET. COMPUTE IT.** Side A is under active development
and its register has moved three times in two hours: **760 -> 803 -> 848**, taking
the target with it, **1559 -> 1602 -> 1647**. Any number written into a document
here is stale within the hour, and a stale target is worse than none because it
will be checked against confidently.

**The invariant, which has held through every move:** side A's change is a single
append hunk past the end of the merge base (`@@ -656,0 +657,N @@`, one hunk, every
time), and side B has not moved. So:

    target = B + (A - 656)

Compute it immediately before merging, not from this page:

    R=/Users/josie/can-it-ford
    F=docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
    A=$(git -C $R show claude/add-ci-checks:$F            | wc -l)
    B=$(git -C $R show claude/fork-register-reconcile:$F  | wc -l)
    echo "expect $(( B + A - 656 ))   sideA-vanished=$B   sideB-vanished=$A"

**Verify the invariant too**, because the formula depends on it. This must print
**1**, a single hunk starting at 656:

    git -C $R diff --unified=0 1a868f3:$F claude/add-ci-checks:$F | grep -c '^@@'

If it ever prints more than 1, side A is no longer a pure append and the
arithmetic does not apply: run `git merge-file` on the three blobs and read the
result instead.

Last measured 00:45: A=848, B=1455, **target 1647**, `merge-file` exit 0, 0
conflict markers, 1647 lines. The watcher computes this on every poll and reports
the current target, so trust its message over this paragraph.

### Merge arithmetic RE-DERIVED from committed objects, 23:40

The original figure was computed with side A read from a **working tree**. It has
been recomputed with all three inputs read from **committed blobs**, which is the
stronger measurement, and **it holds identically**:

    merge-base                          1a868f3  (unchanged)   register  656
    A  claude/add-ci-checks                                    register  760
    B  claude/fork-register-reconcile                          register 1455

    git merge-file -p A base B   ->  exit 0, 0 conflict markers, 1602 lines

**1602 = 1455 + 147, from committed objects.** The earlier working-tree result was
not wrong, and it is no longer the basis for the claim.

**CLAUDE.md now differs between the sides, and still does not collide.** Blob
`37983d2` at both the base and B, `68ce06e2` on A. Only A changed it, so the
merge takes A's version outright. There is still nothing to reconcile.

**Step 2. AMENDED, see section 13. The named owner no longer has a working
tree.** `.claude/worktrees/fork-register-reconcile` was removed. The branch and
all 23 of its commits are intact and the register is still 1455 lines on it, so
**nothing is lost**, but step 2 cannot be done in place.

**Step 2a, and it comes BEFORE anyone asks pid 10363 to do anything.** That
process is alive with a deleted working directory: every `git` command it issues
will fail until it has a tree. Re-create one first, then tell it:

    git -C /Users/josie/can-it-ford worktree add \
      /Users/josie/can-it-ford/.claude/worktrees/fork-register-reconcile claude/fork-register-reconcile

**Do not check out a branch that is already checked out in another tree.** Git
refuses this by default, verified live:

    $ git worktree add /tmp/x claude/r5-safekeeping
    fatal: 'claude/r5-safekeeping' is already used by worktree at '...r5-safekeeping'

`--force` overrides that refusal. **Do not use it here.** Two trees on one
branch means two sessions committing to the same ref, which is the collision
this whole document is about.

**Step 2b.** Only after step 1 lands, merge the **commit SHA from step 1, never
the branch name**: `git merge <branch>` silently picked up an unrelated live
session's commit in this repo on 2026-08-13.

**Step 3. Owner: `D4 REGISTER-RECONCILE`. Confirm by content, not by exit code.**

    wc -l docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md   # MUST be 1602
    grep -c "^K4\." docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md   # A's block follows K4
    grep -n "9.80665" docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md | head   # B's early hunks

  **1602 = 1455 + 147.** If it reads **1455, side A vanished**. If it reads
  **760, side B vanished**. Neither loss produces a conflict marker, which is
  precisely why the line count is the test and `git merge` exiting 0 is not.

**Step 4. Standing, everyone, until step 2 lands.** Nobody runs `git checkout`,
`git restore`, or a file copy on `CLAUDE.md` or the register across trees.
CLAUDE.md needs no merge at all: blob `37983d2` at base, main HEAD and the fork
tip alike, so the only thing that can happen to it is loss.

### The watchdog is RETIRED and REPOINTED, 23:40

It was armed to guard something that could vanish without trace. That thing is
now committed, so **leaving it firing on a file that can no longer be lost would
train a real alarm into noise**, which is a failure this project has already had.
`watch_side_a.sh` was stopped.

**Replaced by `can-it-ford-bundles/watch_register_merge.sh`**, which guards what
is actually still at risk: the merge itself. It watches the **branches**, not a
working file, so it needs no worktree, and it reads:

| side B's register | meaning |
|---|---|
| **1455** | merge has not happened yet, the current state |
| **1602** | correct, 1455 + 104. Then confirm by content, not by the count |
| **760** | **side B vanished**, overwritten by side A's length, and no conflict marker will have appeared |
| anything else | inspect before writing to it again |

It also alerts if either branch disappears, naming `ALL-refs-*.bundle` as the
recovery path. Its arming event confirms the current state: **side B still 1455,
merge has not happened.**

**TUNED 00:25, after it alarmed three times on a non-event.** Side A's *tip*
was in the signature, and that branch is being actively worked on, so the
watcher fired repeatedly carrying "merge has not happened yet". **An alarm
that mostly reports non-events trains itself into noise**, and the next one
might be the 760 case. A-tip is dropped; A's *register length* is kept, because
if it leaves 760 the arithmetic stops holding and the watcher now says so.
The general form is worth keeping: **when an alarm fires repeatedly on the same
non-event, the fault is in its signature, not in the reader's patience.**

**Its remaining value is smaller than the first watcher's, and worth stating
honestly:** a bad merge leaves both branches intact in the reflog, so this is a
convenience alarm on an ordinary git operation, not the last line of defence the
first one was.

### HISTORICAL: the first watchdog firing, when side A was still uncommitted

**read, 23:10.** The watcher caught a real change and it justified its existence
on the first event. **Side A is bigger than this section originally described:**

| file | at HEAD | when I first measured | **now** |
|---|---|---|---|
| `CLAUDE.md` | 676 | 749 (+73) | **823 (+147)** |
| register | 656 | 760 (+104) | 760 (+104), **untouched**, sha still `ed96e72e` |
| `.gitignore` | | not modified | **now modified (+5)** |

So the uncommitted, unowned work in the main checkout has gone from **177 lines
to 251**, and a fifth file joined it. The register itself has not moved, which
is why the merge arithmetic in this section still holds: **1602 = 1455 + 147**.

**Re-snapshotted immediately**, because the 15:08 restore point was now stale
for CLAUDE.md: `can-it-ford-bundles/2026-08-17/maintree-snapshot-2310/` (0700),
five raw files plus the patch, sha256 MANIFEST, and the patch **verified to
reapply cleanly onto 777567a** in a throwaway clone.

**Step 1's abort condition is unchanged and still correct:** the register must
read **760**. It does. If you are committing side A, note you are now committing
147 lines of CLAUDE.md, not 73.

#### A defect in my own watcher, found by its own first alert

The event read `[side-A CHANGED] unchanged: register 760 lines, still
uncommitted, sha matches`, which is self-contradictory. The signature correctly
included CLAUDE.md's line count, so the change was detected, but `classify()`
only branched on the **register**, so it printed "unchanged" for a real CLAUDE.md
edit. **An alert that fires correctly and then describes itself as "unchanged" is
worse than no alert**, because the natural response is to ignore it.

Fixed: `classify()` now takes the previous signature as well and prints an
explicit `MOVED: register X->Y; CLAUDE.md X->Y; dirty-count X->Y` line before its
verdict, and the register-intact branch now says so rather than saying
"unchanged". The watcher was restarted on the corrected script.

### The original protection, armed 00:53

The blockquote at the top of this section says the abort condition and the
survival test are the only protection those 177 lines have, because nobody is
watching the file. That is no longer quite true.

`can-it-ford-bundles/watch_side_a.sh` is armed as a persistent monitor. It polls
every 60s and emits **only on a state change**, so silence means unchanged. It
classifies the transition rather than just reporting a diff:

| observed | meaning |
|---|---|
| 760 lines, still modified, sha `ed96e72e...` | unchanged, the expected state |
| 760 lines, **no longer modified** | **GOOD**, it was committed. Step 2 can proceed |
| **656 lines** | **SIDE A LOST.** 656 is the pre-edit baseline, so the 104 lines are gone with no reflog entry. The alert carries the `cp` command to restore from the snapshot |
| any other shrink | lines removed, compare against the snapshot before anyone writes again |
| file absent | restore from the snapshot |

It also emits on arming and on stop, so a dead watcher cannot be mistaken for a
quiet one. **Verified before arming:** the live signature is
`760 lines / 2 modified / ed96e72e`, matching the baseline the script expects,
and the restore path it names exists and is 90,116 bytes.

**read, 00:52.** The 15:08 snapshot is still a valid restore point: all four
files are byte-identical to live, register sha256
`ed96e72ed230dc8c0e47c38b507f9722405d103dbba2bbe99c1b53286047c7e6`.

This is a watchdog, not an owner. It cannot commit anything, and it dies when
this session does. **Step 1 still needs a human.**

**What I did not do, so the next reader does not assume it is handled:** I did
not commit side A. Committing another session's uncommitted work under my own
message is the 2026-08-07 failure, and the orphan status does not change that.
It needs a human decision about the commit message and about whether those 104
lines are finished.

---

## 7. Shared pane cwd. CORRECTED: this is NOT a shared index

**RETRACTED, same day, on the coordinator's evidence and re-measured by me.**
An earlier version of this section, and the body of commit 7d1ec34, said the
four round-5 sessions "share one worktree and one index". **The index half is
false and is withdrawn.** It matters because "one shared index" implies another
session's staged entries can ride along on your path-limited commit, and in this
layout they cannot.

**read.** Each worktree has its own git-dir and its own index, four distinct
inodes. `git rev-parse --git-path index` returns a different path per worktree:

    r5-research     .git/worktrees/r5-research/index      inode 14075666
    r5-exposure     .git/worktrees/r5-exposure/index      inode 14074323
    r5-safekeeping  .git/worktrees/r5-safekeeping/index   inode 14075592
    r5-physics      .git/worktrees/r5-physics/index       inode 14075548

Those inodes reproduce the coordinator's independent measurement exactly. The
2026-08-07 breach was several sessions inside **one** tree, which is a different
topology from four worktrees and must not be cited as a precedent for this.

**What the four genuinely do share**, and these are real:

- **the object store**, `.git/objects`, inode 1770732, identical from every
  worktree
- **the refs namespace**, so concurrent ref updates can race
- **`.git/config`**
- **`.git/hooks`**, inode 1770708, identical from every worktree: **one**
  `pre-commit` (refuses more than 8 staged files) and **one** `pre-push`
  (requires `PUSH_OK=1`) govern all four. Editing a hook changes it for everyone
  at once, with no per-worktree override.

### The residual hazard, stated precisely

**read.** All four pane shells still have cwd
`/Users/josie/can-it-ford/.claude/worktrees/r5-research`, confirmed by
`tmux list-panes -a -F '#{pane_current_path}'` and by
`lsof -a -p <pane shell pid> -d cwd` on all four. So a **bare** `git` command
typed in any pane operates on r5-research's index and r5-research's branch. The
risk is **misdirected** work, not **swept** work: a commit meant for r5-physics
would land on `claude/r5-research`, not scoop up a sibling's staging area.

**read, and it has not happened.** All four branches carry their own distinct
commits, and every commit on `claude/r5-research` is D1's own work:

    cf9edab Fix a transposed file count: jfr3.12885 is 25, not 27
    e9b3717 R5-D1 unit 2: mine the settling and multi-resolution catalogs
    e7190b7 R5-D1: mine the Elicit outputs and all 14 paper catalogs
    777567a Add CI running the three existing checks   (shared base)

`round5_launch.sh` is not the cause: its window loop passes `-c "$REPO/$dir"`
with the correct per-dispatch directory, and all four worktrees exist on their
correct branches. The panes were started somewhere other than that loop.

**I did not `cd`.** A single `cd` in this repo relocates the tracked working
directory and the relative-path PreToolUse hook then fails before every later
Bash call. Everything I wrote went to my own worktree through explicit absolute
paths and `git -C`, so I have not added to the collision.

Fix, for Josie to run, one line per window:

    tmux send-keys -t canford5:2 'cd /Users/josie/can-it-ford/.claude/worktrees/r5-exposure' Enter
    tmux send-keys -t canford5:3 'cd /Users/josie/can-it-ford/.claude/worktrees/r5-safekeeping' Enter
    tmux send-keys -t canford5:4 'cd /Users/josie/can-it-ford/.claude/worktrees/r5-physics' Enter

A running Claude session will not pick up the new directory; the session has to
be restarted in the corrected pane for it to take effect.

---

## 9. Branch taxonomy: reconciling three counts that measure three different sets

Three branch counts are live in round 5 and none had been reconciled: my **33
at-risk branches / 241 commits**, my **77 local branches** covered by
`ALL-refs.bundle`, and D2's independently verified **30 public branches**. They
disagree because they are answers to three different questions. All measured
live at 21:01.

### Set definitions and sizes

| set | definition | count |
|---|---|---|
| LOCAL | `git for-each-ref refs/heads` | **77** |
| PUBLIC | `git ls-remote --heads origin`, live network | **30** |
| LOCAL-ONLY | in LOCAL, no branch of that name on origin | **49** |
| LOCAL+PUBLIC | same branch name in both | **28** |
| PUBLIC-ONLY | on origin, no local branch of that name | **2** |
| AT-RISK | LOCAL branches with commits reachable from no remote ref | **33** |

49 + 28 = 77. 28 + 2 = 30. **D2's 30 reproduces exactly.**

The two PUBLIC-ONLY branches are `track2/coupled-realism-explore` and
`vista-realism-track-2026-08-13`. They are published, have no local counterpart,
and therefore cannot appear in any at-risk count. Being public, they are safe
from loss and are *not* a gap.

### Why AT-RISK is not a subset of LOCAL-ONLY

This is the crossing that makes the three counts look contradictory:

| at-risk branches | branches | commits |
|---|---|---|
| also published on origin, local tip ahead | **12** | 190 |
| local-only | **21** | 71 |

A branch can be public **and** carry unpushed work: 12 of them do, `local_ahead`
by 1 to 30 commits, and they hold the large majority of the unpushed work. Of
the 30 public branches, **16 are byte-identical to their local counterpart, 12
are behind their local branch, and 2 have no local branch.**

The 28 LOCAL-ONLY branches that are *not* at risk point at commits already
reachable from some remote ref under a different name, so they are unpushed
labels on published history, not unpublished work.

Commit sums exceed the deduplicated 248 in every split, because branches share
commits. Only `git rev-list --count --branches --not --remotes` gives the
deduplicated figure.

### UPDATED 00:20: origin is now 35 branches, not 30. The 5 new ones are clean

**read.** `git ls-remote --heads origin` returns **35**, against the **30**
recorded at 21:01 and stored in `public_branch_audit.tsv`. Diffed against that
file rather than against the local remote-tracking cache, which is not
authoritative for this and briefly gave me a wrong answer of "no change":

    NEW on origin   claude/fix-hf-sync-exclude        claude/review-workflow-auth
                    claude/hf-space-l1-joint-rule     claude/vercel-landing-page
                    claude/scholar-sidekick-auth-e92679
    GONE            none

**Audited all five at their live remote tips**, every tip already present in the
local object store so nothing was inferred from a stale cache:

| | result |
|---|---|
| files matching a credential pattern | **0 across all five** |
| files with "credential" in the path | **0** |
| NCAC/CCSA `.key` decks | 14 each, the same set already on every public branch |
| upstream `.zip` archives | 4 each, likewise |

**No new exposure.** The geometry is the material already covered by the reported
permission, and none of the five carries a credential. The 30-of-30 finding in
this section becomes **35 of 35** without changing its meaning.

**What did NOT happen**, checked because it would matter more: **no `r5-*` branch
and no credential branch is on origin.** `claude/r5-exposure`, my one BLOCK_PATH,
is still unpushed, and so is
`claude/credential-exposure-2026-08-13-DO-NOT-PUSH`.

**`claude/add-ci-checks` moved again**, 790d999 to `ffc05d9` "Cite the four prior
vehicle-fording works", now **5 at-risk commits**. Re-scanned: **0 risky paths, 0
credential hits.** Verdict still OK.

### Cross-checked against D2's independent re-derivation, 00:33

D2 re-derived the growth finding rather than relaying it, so where we overlap
this is **two origins, not one source cited twice**: 35 branches, 14 `.key` on
35 of 35, and `FLAG_CREDENTIAL_EXPOSURE` on exactly 1 of 35, measured separately
and agreeing. All 35 also carry exactly 4 `.zip`, which I measured and D2 did
not report.

D2 additionally tracked two files I had not: `token_setup_template.md` at 34/35
and `secrets-and-env.md` at 32/35.

**One correction, and it strengthens D2's own argument.** D2 attributed the
34/35 to "one NEW branch" lacking the file. Measured: the branch lacking it is
`worktree-reconcile-vehicle-master-ref`, which was **already public at 21:01**
and appears in `public_branch_audit.tsv`. All five genuinely new branches carry
it, checked individually. **So the deviation predates the growth**, D2's earlier
"on all 30" was already false when written, and the re-derivation caught a
pre-existing error rather than a new one. Re-deriving did not merely keep a
number current; it exposed one that had never been right.

### The column D2 needs: what the public branches actually carry

Measured with `git ls-tree -r` against each live remote tip. All 30 tips were
present in the local object store, so no fetch was required and nothing was
inferred from a stale cache.

| material | public branches carrying it |
|---|---|
| `docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md` | **1 of 30**, `claude/rtfd-test-phase-1-4-569130` only |
| **upstream NCAC/CCSA `.zip` distribution archives** | **30 of 30**, 4 files each |
| NCAC/CCSA LS-DYNA `.key` decks | **30 of 30**, 14 files each |
| `.ply` geometry | **30 of 30**, 4 files each (3 branches carry 2) |

### CORRECTED. My "83.5 MB across 18 files" was wrong twice over

**RETRACTED.** An earlier version of this section, and the body of commit
fe04620, said "83.5 MB across 18 files, public". Two independent errors, both
mine, found when the coordinator could not reproduce the figure:

1. **Wrong set.** I globbed for `.key` and `.ply` only. I never scanned for
   `.zip`, so I missed the **4 upstream distribution archives**, 88,592,238 B,
   which are the strongest form of this exposure: not derived geometry, not even
   the extracted decks, but the **original NCAC/CCSA download archives
   redistributed intact**, named
   `2010-toyota-yaris-detailed-v2j.zip` (42,113,905 B),
   `2007-chevrolet-silverado-detailed-v3e.zip` (27,865,164 B),
   `2010-toyota-yaris-coarse-v1l.zip` (11,228,299 B),
   `2007-chevrolet-silverado-coarse-v3a.zip` (7,384,870 B).
2. **Wrong unit label.** I divided bytes by 1048576 and wrote "MB". That is
   **MiB**. My own sum re-derived: 18 files, **87,540,358 B = 87.54 MB = 83.48
   MiB**. So 83.5 was MiB printed as MB, which is the identical mistake I am
   about to flag in a sibling's numbers, made first by me.

Coincidence worth naming so nobody re-derives the wrong pairing: my set and the
coordinator's are **both 18 files**, which is why a partial sum looked like the
explanation. They are different 18s. Mine was 14 `.key` + 4 `.ply`. The CCSA set
is 4 `.zip` + 14 `.key`.

### The corrected figures, on `origin/main` (= `main`, both at 1a868f3)

Byte counts from `git ls-tree -r -l origin/main -- vehicle_geometry_research/`.
**MB = 10^6 bytes, MiB = 2^20 bytes. Both are given, always.**

| extension | files | bytes | MB | MiB |
|---|---|---|---|---|
| `.zip` upstream archives | 4 | 88,592,238 | 88.59 | 84.49 |
| `.key` LS-DYNA decks | 14 | 71,716,670 | 71.72 | 68.39 |
| `.ply` derived geometry | 4 | 15,823,688 | 15.82 | 15.09 |
| `.md` | 8 | 120,213 | 0.12 | 0.11 |
| **directory total** | **30** | **176,252,809** | **176.25** | **168.09** |
| **CCSA material only** (`.zip` + `.key`) | **18** | **160,308,908** | **160.31** | **152.88** |

Every one of these reproduces the coordinator's independent measurement to the
byte. **All 30 public branches carry all 4 `.zip` and all 14 `.key`**; 24 of the
30 have a `vehicle_geometry_research/` totalling exactly 176,252,809 B, the
other 6 differing only in `.ply` and `.md`.

### D2 is not in conflict with this. D2 has a unit label to fix

D2's `6e771b6` reports **168.09 total** and **152.90 CCSA**. Those are my
**MiB** columns, to the second decimal, and D2's 91.0 percent proportion matches
160,308,908 / 176,252,809 = 90.96 percent. **D2's arithmetic is correct and its
unit label is wrong**, exactly as mine was. In MB the same quantities are 176.25
and 160.31. The gap between the two labels is 4.6 percent, which is small enough
to look like sloppiness rather than a unit convention in a licence document, and
that is the audience that will read it.

Per-branch detail: `can-it-ford-bundles/2026-08-16/public_branch_audit.tsv`.

**Consequence for E8, as originally stated:** the question was never about a
derived hull on one branch. It is about the upstream crash-model decks
themselves, published 30 times over. Deleting them from `main` would leave 29
other public branches serving the same bytes, and would still not unpublish
them.

**RESOLVED 2026-08-17, and recorded with its provenance rather than as a fact I
checked.** D2's `b63201e` records that **Josie reports she has obtained
confirmation to use the NCAC/CCSA meshes**, artifact pending. D2 filed it as her
report, not as something D2 verified, and I am carrying it the same way: **I have
not seen the artifact, so this is a report, not a confirmation.** If it holds, the
30-branch spread stops being an exposure and becomes merely an inventory, and the
removal options in D2's analysis never have to be exercised.

**UPDATED 23:26, the Wiley carve-out is closed too.** I previously flagged that
the Wiley/CIWEM material was a different rights holder with no permission
reported. Josie now reports that grant as well, covering the 16
Smith-Modra-Felder files. Same standing as the first: **her report, dated,
artifact pending, not a confirmation**, and this one reached me as a **relay with
no commit SHA**, so it is one step weaker in provenance than the geometry
clearance. Attach a SHA to it.

**One thing this still does not touch:** the **credentials are entirely
unaffected by any of these permissions and none has been rotated**, which is why
section 1's destination requirement survives on that axis alone.

**The measurement in this section is unchanged, and this is the line to keep:**
30 of 30 public branches carry all 4 `.zip` and all 14 `.key`, 160,308,908 B on
`main` across 18 files. **What changed is whether that is a problem, not what is
there.** D2's own clearance note cites 160,322,098 B across 30 branches, a
different scope from my main-only 18-file set rather than a disagreement; neither
number should be quoted without saying which it is. I have touched none of it.

---

## 11. Coverage boundary: this insurance protects one machine only

Everything in sections 1 to 9 covers **the Mac**. A `git bundle` taken here
cannot contain a commit that has never reached here. Three checks, all negative,
which is the useful kind of result:

**read.** Non-`origin` remote-tracking refs, and whether they hold anything
unprotected:

| ref | tip | status |
|---|---|---|
| `overleaf/main` | 6466dfa | in `ALL-refs.bundle`. Shares **no ancestor** with `origin/main`, as the standing record says, but 0 of its commits are unreachable from local branches, so it is covered. |
| `tacc/main` | cdcdf9d | in `ALL-refs.bundle`. **Orphaned tracking state**: no `tacc` remote exists in `git config`. Its reflog shows it was fetched on 2026-08-13 from `/private/tmp/.../scratchpad/rt.bundle`, **which no longer exists**. |

`tacc/main` is 2 commits ahead of `origin/main` ("realism_track: submit-ready
GH200 rung-b job" and "validate SDF-collider coupling path against analytic
buoyancy", both 2026-08-12). **Those 2 are already public**, contained in
`refs/remotes/origin/vista-realism-track-2026-08-13`, one of the two PUBLIC-ONLY
branches from section 9. So nothing is at risk here.

**A reading trap I fell into and corrected.** `git rev-list --count cdcdf9d
--not --branches --remotes=origin` returns **0**, and I first read that as "a
local branch has it". It does not: `git branch --contains cdcdf9d` is **empty**.
The 0 came from an `origin/*` ref, not a local branch. `git branch --contains`
lists **local** branches only; `git branch -a --contains` or
`git for-each-ref --contains` is the question you actually mean. The count was
right and my reading of it was wrong.

**read.** Three further `.bundle` files were sitting in ephemeral `/private/tmp`
scratchpads from earlier sessions (`track1_6dof_rescue_2026-08-14`,
`fork_s3_rescue_delta`, `moving_vehicle_delta`). Every tip in all three is
covered by both a local branch and an `origin` ref. Nothing unique. They can be
lost without consequence, which is not true of `can-it-ford-bundles/`.

### GAP CLOSED 22:51, and it was not empty

**The gap below was real.** It is now closed, and the closing found work that
existed nowhere else.

**How the gate opened.** A sibling's commit message said a job had been
*measured* on TACC, which contradicted my finding that MFA was blocking. That is
a testable contradiction, so I retested rather than trusting either. Vista
answered.

**What was unprotected on Vista `$WORK/can-it-ford`:**

| | |
|---|---|
| commits on no remote | **2**, on its local `main` |
| uncommitted tracked files | **4**, 50 insertions, 9 deletions |
| untracked files | 102 |

The two commits: `15275f2` "settings.json: adopt origin/main's full config as
the base, add git-push ask" and `e9f3b60` "add TACC global-rules import target,
citation-verifier subagent, git-push ask rule".

**The uncommitted change that matters.** `simulation/failure_modes.py`, one
line:

    -G = 9.80665
    +G = 9.81

That is **exactly the open action item in CLAUDE.md item 15**, which says to
close the gravity fork by setting `failure_modes.py:14` to 9.81, re-running
`analysis/classify_failure_modes.py`, and confirming the verdicts are
byte-identical. **Someone started that fix on Vista and left it uncommitted.** It
existed in exactly one place, on a cluster scratch filesystem, and no bundle
anywhere covered it. The re-run and the verdict comparison have **not** been
done, so the item is not closed, only started; do not record it as closed on the
strength of this line.

**Capture, and the transfer verified rather than assumed.**

    can-it-ford-bundles/incoming/     (0700)
      vista-capture.bundle       5,994 B   the 2 commits
      vista-uncommitted.patch    6,974 B   152 lines, the 4 modified files
      vista-status.txt                     full porcelain status
      vista-untracked.txt                  the 102 untracked paths

sha256 computed **on Vista** and **on arrival** agree exactly:
`ffab89899817bb6efc80ba10b5b881f2648173e1c3ff7ab1d610573476fcd8cb`.

Fetched into `refs/remotes/vista/*`, a new namespace that touches no branch, and
a refresh then swept it into the standalone: **`ALL-refs-2251.bundle`, 142 refs**,
up from 138. Vista's two commits are now covered by the same insurance as
everything else.

### My own Vista check was asymmetric, and fixing it found a second repo

**read.** I searched **LS6** for every repo under `$WORK` and `$HOME`, but on
**Vista** I only looked at the one path I already knew, `$WORK/can-it-ford`.
That is the failure this project has a standing rule about: a search that skips
paths cannot prove absence. Re-run symmetrically across `$HOME`, `$WORK` and
`$SCRATCH`, two levels: **10 repositories**, of which **two** hold commits on no
remote.

    $WORK/can-it-ford                              ATRISK=2  DIRTY=4   <- captured above
    $WORK/can-it-ford-OLD-pre-purge                ATRISK=2  DIRTY=5   <- NEW
    $WORK/home_archive/can-it-ford_STALE_...       ATRISK=0  DIRTY=4
    + 7 others (mpm-engine forks, genesis-world, chrono), all 0 and 0

**The second repo is a different lineage, not a duplicate.** Its two commits are
`8eab759` "Remove RayTracer from gs.Scene for headless runs; add --horizon flag"
and `0736dc3` "Add project identity/deadlines to CLAUDE.md, add repo-root
STATUS.md". Neither is the pair found in the live repo. **Both are ABSENT from
this Mac's object store**, checked with `cat-file -t`, so their content existed
in exactly one place on Earth.

**Captured as PATCHES, not as history, and the distinction is deliberate.** The
directory is named `-OLD-pre-purge`, so its history predates a credential purge.
Bundling it would have re-imported pre-purge objects into the insurance
artifacts, and this project has already had GitHub serve a removed key by SHA
after a `filter-repo` pass. `git format-patch` carries the content of those two
commits without their ancestry.

    can-it-ford-bundles/incoming/vista-prepurge/   (0700)
      0001-Remove-RayTracer-...patch    1,720 B   simulation/can_it_ford_L2_mpm.py
      0002-Add-project-identity-...patch 11,148 B  CLAUDE.md, STATUS.md, kumar_july9_update/STATUS.md
      dirty.patch                      12,885 B   its 5 uncommitted files
      stale-dirty.patch                 1,785 B   the archived repo's 4 uncommitted files
      status.txt

**Scanned before letting them sit here:** **0 credential-pattern hits**. Two
40-hex strings appear, and rather than wave them off as "probably SHAs" I
checked: they are `8eab759503e317e836984b426945eb7ac3173d02` and
`0736dc3a2683cdcb8b9dea73060974de098ecb66`, which are the two commits' own
`From ` headers. Not keys.

**Not fetched into any ref, by choice.** Those commits' parents do not exist
here, so a fetch would fail on missing prerequisites anyway, and grafting a
pre-purge lineage into a post-purge repo is not a decision to make in passing.
The content is preserved and recoverable; whether it is wanted is someone
else's call.

**LS6, checked the same way:** one git repo found across `$WORK` and `$HOME`,
`~/taichi_mpm`, which is a third-party engine clone, not this project. **0
commits on no remote**, 39 dirty files that are consistent with build output.
Nothing captured, and nothing appears to be at risk there. Stated as a bounded
search: `$WORK/*/` and `$HOME/*/` at one level, not a full filesystem sweep.

### The original gap, kept for the record

**Work committed on Vista or LS6 and never fetched to this Mac is invisible to
every bundle here.** The standing record says Vista's `$WORK` held a
`realism_track` series existing only there. `tacc/main` is a partial capture of
that, frozen at 2026-08-13 and arriving via a scratchpad bundle that has since
been deleted. **Anything committed on either cluster after 2026-08-13 is
unrepresented in this repo and therefore in no bundle.**

**Attempted, in order, and what actually blocked each:**

1. `canford-tacc` MCP, `tacc_alloc_status(vista)`.
2. The direct path the session banner advertises,
   `scripts/tacc.sh vista '<git status and log>'`. The script exists
   (3,627 B, executable) and `~/.ssh/config` has `vista`, `vista1`, `vista2`,
   `ls6`, `ls6a-c` defined. No SSH ControlMaster socket is present.

On the first attempt, **both were refused by the same thing: the local
tool-safety classifier was unavailable, so no command could be issued at all.**
That is worth separating from a cluster outage: at that point **I had not
reached TACC, therefore I had learned nothing about TACC's state.** An
unreachable probe is not a measurement, which is this project's own standing
rule about a zero result from one root.

**UPDATED 00:24, retried once the classifier recovered, and this time it is a
real measurement.** Both hosts were reached and both refused at authentication:

    jcerrell0629@vista.tacc.utexas.edu: Permission denied (keyboard-interactive).
    [tacc.sh] SSH failed to vista. The ControlMaster socket may have expired.
    jcerrell0629@ls6.tacc.utexas.edu: Permission denied (keyboard-interactive).
    [tacc.sh] SSH failed to ls6. The ControlMaster socket may have expired.

So the state is now known rather than assumed: **the clusters are reachable, the
ControlMaster sockets have expired, and TACC's MFA needs a human.** Nothing here
can be automated around it. **Josie runs this once per host, and the 6-digit
token prompt is the whole point:**

    ssh vista        # enter password, then the 6-digit TACC token
    ssh ls6

After that the socket is live for roughly 8 hours and the read-only queries
below will work unattended.

**TRAP, found live and it nearly cost the measurement.** `scripts/tacc.sh`
**returned exit code 0 for both failures.** The SSH rejection appears only in
stdout text. A caller that checks `$?` concludes the query succeeded and that
the cluster has no unpushed work, which is the strongest possible false
negative for a safety audit. **Parse the output for `Permission denied` or
`SSH failed`; do not trust `tacc.sh`'s exit status.** This is the project's own
"a command exiting 0 is not evidence the remote updated" rule, in a new place.

**To close it, when a shell is available again** (read-only, no GPU, seconds):

    /Users/josie/can-it-ford/scripts/tacc.sh vista \
      'cd $WORK/can-it-ford && git status --porcelain -uno && git rev-list --count --branches --not --remotes'
    /Users/josie/can-it-ford/scripts/tacc.sh ls6 \
      'cd $WORK/can-it-ford && git status --porcelain -uno && git rev-list --count --branches --not --remotes'

If either count is non-zero, bundle it **there** and copy the bundle back, which
is small and needs no authorisation:

    /Users/josie/can-it-ford/scripts/tacc.sh vista \
      'cd $WORK/can-it-ford && git bundle create /tmp/vista-$(date +%Y%m%d).bundle --branches --not --remotes'
    scp vista:/tmp/vista-*.bundle /Users/josie/can-it-ford-bundles/incoming/
    git -C /Users/josie/can-it-ford fetch /Users/josie/can-it-ford-bundles/incoming/vista-*.bundle \
      'refs/heads/*:refs/remotes/vista/*'

Then re-run `refresh_bundle.sh --full`, which will sweep the new
`refs/remotes/vista/*` into the standalone bundle automatically.

---

## 12. RECOVERY RUNBOOK, drilled end to end on 2026-08-17

Everything above proves the bundles *verify* and that *refs* restore. Neither is
what anyone needs at the moment something is actually lost. **This is the
procedure, and it has been run.**

### If a worktree, a branch, or the whole repo is lost

    # 1. rebuild the repository from the two bundles, newest incremental last
    git init --bare /path/to/recovered.git
    git -C /path/to/recovered.git fetch \
        /Users/josie/can-it-ford-bundles/2026-08-16/ALL-refs.bundle 'refs/heads/*:refs/heads/*'
    git -C /path/to/recovered.git fetch \
        "$(ls -1t /Users/josie/can-it-ford-bundles/*/INCREMENTAL-all-branches-*.bundle | head -1)" \
        'refs/heads/*:refs/heads/*'

    # 2. get a WORKING checkout of the branch you lost
    git clone /path/to/recovered.git /path/to/work -b <branch>

    # 3. confirm it, by tree object rather than by eye
    git -C /path/to/work rev-parse 'HEAD^{tree}'

### If uncommitted work is lost

Snapshots live in `can-it-ford-bundles/<date>/uncommitted-<HHMM>/<worktree>/`,
mode 0700, one directory per dirty worktree, each with `HEAD.txt`, a
`tracked.patch` for modified files, `untracked.tar.gz` plus `untracked.list`,
and a sha256 `MANIFEST.sha256`.

    git -C <worktree> apply <snap>/<worktree>/tracked.patch    # modified files
    tar -xzf <snap>/<worktree>/untracked.tar.gz -C <worktree>  # untracked files

### The drill, and what it actually established

**read, 2026-08-17 00:28.** Run from bundles only, target
`claude/fork-moving-driver`:

| check | result |
|---|---|
| branches rebuilt from the two bundles | **77** |
| working checkout tip vs live | `c96e745` = `c96e745` |
| files in the recovered worktree | **859** |
| **tree object**, recovered vs live | `cbe0c7df875c4513f9c4eb99f831174ea135b7bd`, **identical** |
| `renders/yaris_render_s1/sim_standing.py` on disk vs live | sha256 `4696c3b2d39f...`, **identical** |
| uncommitted snapshot, `ctx-census` untracked | **3 of 3 files match live byte for byte** |

That `sim_standing.py` hash is a useful independent cross-check: `4696c3b2...`
is the driver sha256 that stamps all 40 three-class runs, so the recovered file
is provably the same driver those runs were produced with.

**The control that makes the drill mean anything.** A git clone can silently
borrow objects from a nearby repo through `objects/info/alternates`, which would
make a bundle look sufficient when it was not. Checked explicitly: **neither the
recovered bare repo nor the working clone has an `alternates` file.** The 498 MB
bare repo and 565 MB checkout were reconstructed from the bundles alone, with no
access to `/Users/josie/can-it-ford`.

### LIMIT NOW CLOSED: all 77 branches and all 33 thin bundles, 00:36

The first drill checked one branch of 77. Re-run across everything:

| check | result |
|---|---|
| branch tips, recovered vs the tip the bundle records | **77 match, 0 mismatch, 0 missing** |
| tree objects | **77 match, 0 mismatch** |
| `git fsck --strict --no-dangling` on the recovered repo | **exit 0, zero output lines** |
| branches whose complete file list resolves from the recovered store | **77 of 77** |
| the 33 thin per-branch bundles, each fetched and tip-compared | **33 restored, 0 failed** |

**Race-free by construction, and this matters.** Sibling sessions commit
continuously, so comparing a recovered repo against a *live* tip reports false
mismatches for any branch that moved after the bundle. Every comparison above is
against the tip **the bundle itself records**, which is immutable.

### Object-set equivalence, with the residual fully explained

The strongest form of "nothing is missing" is to compare the object sets, not
the refs:

    objects reachable from refs/heads, recovered : 5,066
    objects reachable from refs/heads, live      : 5,079
    in live but absent from recovered            :    13
    in recovered but absent from live            :     0

**All 13 are accounted for, not waved away.** Exactly two branches advanced
after the 00:27 bundle: `claude/r5-research` (+2 commits, 3e51dc8 to 907f5d8)
and `claude/r5-safekeeping` (+1, 82896ca to de97a4c). The set of objects
introduced after the bundled tips is **13**, and the intersection with the 13
live-only objects is **13**. **Unexplained: 0.**

### A defect in my own first drill, corrected

The first run printed `fsck exit=0`, and that number was meaningless: I had
piped fsck through `head`, so `$?` was **head's** exit status, not fsck's. Re-run
without the pipe, fsck genuinely exits 0 with zero output lines. **Any
`cmd | head` followed by `$?` reports the pager, not the command.**

**Remaining limit, honestly:** these checks are object-level and structural. I
byte-compared on-disk file content for one branch (section 12 above) rather than
all 77; for the other 76 the guarantee rests on git's content addressing plus a
clean `fsck`, which is strong but is not the same measurement.

---

## 13. EVENT: ten worktrees were removed mid-session. Nothing was lost

Caught by re-taking the standalone bundle and noticing its ref count had fallen
from **147 to 137**. That is the kind of number it would have been easy to shrug
at, so it was chased down.

### What happened

**read.** The worktree count went from **28 to 17**. Ten were removed:

    fork-chrono-eval          fork-render-3class     fork-three-class
    fork-credentials-DO-NOT-PUSH   fork-s3-rescue-2026-08-14   fork-validation
    fork-protocol             fork-scene             fork-vista-triage
    fork-register-reconcile

These are exactly the round-3/4 dispatch trees. Two further worktrees
(`render-realism-vehicle-water-f9127a`, `retire-coupling-module-f20ad4`) are now
on a detached HEAD at 1a868f3 rather than on their old branches; both branches
carried 0 at-risk commits, so that costs nothing.

### Nothing was lost, and here is why that is a measurement and not a hope

1. **Every branch survives with its commit count unchanged**, verified
   individually: `fork-register-reconcile` 23, `fork-moving-driver` 30,
   `fork-protocol` 23, `fork-three-class` 19, `fork-render-3class` 19,
   `fork-scene` 16, `fork-validation` 15, `fork-chrono-eval` 12,
   `fork-vista-triage` 11, `fork-s3-rescue` 8,
   `credential-exposure-...-DO-NOT-PUSH` 8. Side B's register is still
   **1455 lines** on its branch.
2. **The 10 lost refs were all `worktrees/<name>/HEAD` pseudo-refs**, never
   branches. The new standalone still carries 77 `refs/heads`, 34
   `refs/remotes`, 8 `refs/tags`, identical to the old one.
3. **Every commit those pseudo-refs pointed at is present in the new bundle.**
   Checked by fetching the new standalone into a virgin bare repo and testing
   each of the 27 old worktree-HEAD SHAs: **absent 0**.
4. **None of the 10 ever held uncommitted work.** Across six snapshots spanning
   the session, the only dirty trees were ever the main checkout,
   `concurrent-session-safety-570b39`, `ctx-census`,
   `orphan-rescue-token-rotate-d72f90`,
   `warpmpm-flood-vehicle-investigation-1b62fa`, and later `r5-exposure` and
   `r5-research`. **No deleted worktree appears in any snapshot index.**
5. **The removal was clean.** `.git/worktrees/` holds **no stale metadata** for
   any of the ten, so they were pruned rather than `rm -rf`d. That matters
   because `git worktree remove` **refuses a dirty tree** without `--force`, so a
   clean removal is itself independent evidence there was nothing uncommitted in
   them.

### 25 branches now have commits but no tree. Which of them a plan depends on

**read.** The removal made `fork-register-reconcile` the visible case, but it is
not special. Across all 33 at-risk branches:

| | branches | at-risk commits |
|---|---|---|
| has a working tree | 8 | 132 |
| **no working tree** | **25** | **222** |

So **two thirds of the unpushed work has no checkout**. That is not a danger to
the commits, which live in refs and are bundled, but it strands any plan that
assumes someone can just start working. Each needs a `git worktree add` first,
and the removal above stranded one mid-plan.

**The one an active plan in this document depends on:**

- **`claude/fork-register-reconcile` (23)** is step 2 of section 6. Stranded.
  Command in step 2a.

**The rest, largest first, so a future step does not get stranded silently.**
None currently blocks anything written down, but several carry the round-4 work
most likely to be resumed:

    claude/fork-moving-driver          30      claude/fork-chrono-eval          12
    claude/fork-protocol               23      claude/fork-vista-triage         11
    claude/fork-three-class            19      claude/credential-exposure-...    8  <- E8, D2's
    claude/fork-render-3class          19      claude/fork-s3-rescue-2026-08-14  8
    claude/fork-scene                  16      paper/submission-close            7
    claude/fork-validation             15      paper/close-for-submission        5

plus 11 smaller ones (`push-ready-2026-08-04` 4, `analysis/failure-modes` 3,
`claude/reverent-heisenberg-fe731c` 3, `reconcile/overleaf-base` 2,
`claude/figure-validation-sources-826ba6` 2, `claude/festive-goodall-e08861` 2,
and five at 1 each).

Two worth flagging by name rather than by size:

- **`claude/credential-exposure-2026-08-13-DO-NOT-PUSH` (8)** is the E8 and
  rotation work, and it is the one branch whose tree must **not** be casually
  re-created in a shared location: it holds the never-published
  `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`.
- **`claude/fork-three-class` (19)** carries the three-class matched-dx
  deliverable whose own handoff lists unfinished follow-ups, so it is the most
  likely of these to be picked up next.

### LOOP CLOSED: nothing the stranded sessions wrote was lost

I flagged that ten worktrees were removed while sessions wrote into the main
checkout all evening, and that the uncommitted work there had no owner. **The
outcome is now known and it is clean.** Two of those files,
`analysis/research_index.py` and `data/research_corpus_index.json`, are committed
in `790d999` and `46282bc`, and `790d999` also carried `CLAUDE.md` and the
register. **Nothing that landed in that tree has been lost.**

**One concrete instance where this document's insurance covered a gap in the
coordinator's**, recorded because it is the only way to tell whether either net
was worth having. The coordinator's stray capture holds 9 **untracked** files but
does **not** cover modified **tracked** files. `CLAUDE.md` and the register were
modified tracked files throughout that window. What actually covered them was
`can-it-ford-bundles/2026-08-17/maintree-snapshot-2310/`, whose patch was
verified to reapply cleanly onto 777567a.

That is a gap in the coordinator's net rather than a failure of it, and it cost
nothing in the end because the work was committed. It is worth recording only
because the two nets turn out to be complementary: **untracked files and modified
tracked files are different exposures and need different captures**, and a future
session should take both rather than assume either is sufficient.

### The consequence that does need action

**`D4 REGISTER-RECONCILE` (pid 10363) is still running, and its working
directory no longer exists.** It is the named owner of step 2 in section 6. Its
branch is intact, so its work is safe, but it cannot run a `git` command from a
deleted cwd. Section 6 step 2 is amended with the `git worktree add` needed to
give it a tree back.

### RESOLVED: there was no clock anomaly. Do not inherit "the clock is unreliable"

**CORRECTED, and the correction matters more than the original claim.** An
earlier version of this section said "the system clock is inconsistent with this
session's own timestamps" and refused to date the removal on that basis. **The
machine's clock is fine and always was.**

The coordinator supplied the fact I could not see from inside the session: I was
**parked at a `gate_destructive` Yes/No prompt for 21 hours**, and nothing
cleared it until 21:52 BST. From inside a session, no time passes while a prompt
is pending, so a commit made a day ago feels like it was made minutes ago.

Verified from my own commit stamps rather than taken on trust:

    01b5ec6  2026-08-17 00:53:02 +0100
    9bff60e  2026-08-17 21:59:44 +0100     -> 21 h 06 m apart
    date now 2026-08-17 22:01:55 BST       -> 9bff60e is 2 minutes old

`date`, `stat` and the commit stamps **agree with each other and always did**.
The `touch`-then-`stat` control was correct, the commit stamps were correct, and
they never disagreed. The missing variable was the block.

**Record the right lesson.** A future reader who inherits "this machine's clock
is unreliable" will distrust good evidence, which is worse than the original
error. The correct statement is narrower:

> **Session-relative time is unreliable, and only when a session has been parked
> at a permission prompt.** Wall-clock sources on this machine (`date`, `stat`,
> git author stamps) are reliable and mutually consistent. When a session's
> sense of elapsed time conflicts with them, **the session is wrong**, not the
> clock.

**The removal window, now stateable.** Bounded, still not a point time: after
**2026-08-16 15:37:30 +0200**, when commit 9778aa1 recorded the audit that found
28 worktrees, and before **2026-08-17 21:52 BST**, when the prompt was cleared
and I re-took the standalone. Nobody should narrow that further from directory
mtimes without knowing what else was running.

---

## 10. What I did not do

- **Pushed nothing.** No `git push` was run, with or without `PUSH_OK=1`.
- **Merged nothing.** The register merge was run on scratch copies in
  `/private/tmp/.../scratchpad/merge/`, never on a real branch.
- **Edited no shared file.** No write to `CLAUDE.md`, the register,
  `sim_standing.py`, or any tree other than `r5-safekeeping`.
- **Did not copy any bundle off this machine.** See section 1.
- **Ran no physics-skeptic review.** Nothing here is a percentage, force,
  verdict count or distance; every number is a commit count, a line count, a byte
  count or a SHA, each with its command printed. The register merge result
  (**1602** lines as of 00:36, recomputed after side A grew from 760 to 803) is
  the one number a reviewer should re-run rather than trust, **and it moves every
  time side A gains lines**. The live formula is `B + (A - 656)`; the watcher
  computes it rather than storing it, precisely because a hardcoded 1559 would
  have blessed a wrong merge an hour after it was written.
