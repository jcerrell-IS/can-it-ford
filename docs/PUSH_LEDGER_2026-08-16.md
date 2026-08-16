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
  `2010-toyota-yaris-detailed-v2j.zip` at 42,113,905 B (section 9), whose licence
  question is unresolved. An earlier draft said "83.5 MB across 18 files"; that
  was wrong in both set and unit, see section 9.

So the destination must be **private and encrypted**. A plain cloud sync is
disqualified: this project has already had a 0644 iCloud-synced token as part of
its credential exposure.

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

    # 1. copy, with the destination named explicitly
    cp /Users/josie/can-it-ford-bundles/2026-08-16/ALL-refs.bundle \
       /Volumes/<NAME>/canford-2026-08-16/ALL-refs.bundle

    # 2. verify the bytes survived the copy. Must print exactly:
    #    7356713c619fcacf827740cbbecb3e5e5f6b359da4abffb28478c1de5ca0f897
    shasum -a 256 /Volumes/<NAME>/canford-2026-08-16/ALL-refs.bundle

    # 3. restore test AT THE DESTINATION, not here. Must print 77.
    git clone --mirror /Volumes/<NAME>/canford-2026-08-16/ALL-refs.bundle /tmp/restore-check
    git -C /tmp/restore-check for-each-ref refs/heads | wc -l

    # 4. spot-check a tip. Must print 9778aa1... (or later, if D3 committed again)
    git -C /tmp/restore-check rev-parse claude/r5-safekeeping

For option 2, substitute `ALL-refs-MINUS-credentials.bundle` and sha256
`9144eca1ea3ce789e532498222e98fbef584d828763cd0ea8a1c0697650e6698`; step 3 must
print **76**, not 77, and that difference is the check that the sanitisation held.

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

> **READ THIS FIRST. Side A of this collision is ORPHANED, and that changes what
> the plan is for.** 104 lines of register and 73 of CLAUDE.md exist only as
> uncommitted text in the main checkout. **No process owns them**: measured at
> 21:03, no `claude` session anywhere holds the main tree as its working
> directory, and the file has not changed since 15:07. Side B, by contrast, has a
> live owner still running.
>
> **An orphaned side cannot be defended by "its owner will commit it."** There is
> no owner to do so. Nobody is watching that file, nobody will notice if it
> reverts, and there is no reflog entry to recover it from if it does, because it
> was never committed. **The abort condition in step 1 and the survival test in
> step 3 below are therefore the only protection those 177 lines have.** They are
> not belt-and-braces on top of an owner's vigilance. They are the whole of it.
> If they are skipped, the loss is silent and permanent.

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

The reason is measurable, not a guess. A's entire change is one hunk,
`@@ -656,0 +657,104 @@`: a pure append past the end of the base file. B's 17
hunks all fall inside lines 19 to ~650 of the base. They cannot overlap.

### Who owns each side. Measured, not assumed

**read, 21:03.** I resolved each side to a live process rather than guessing:

| side | tree | owner | evidence |
|---|---|---|---|
| **B**, the 1455-line register | `.claude/worktrees/fork-register-reconcile` | **`D4 REGISTER-RECONCILE`, live** | pid 10363, `claude --model opus --effort max --name "D4 REGISTER-RECONCILE"`, cwd is that worktree, pane `canford:4` |
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

**Step 1. Owner: Josie, or the coordinator on her say-so. Side A goes first,
because it has no owner and side B does.**

    cd /Users/josie/can-it-ford
    git status --porcelain                       # expect exactly the 4 M lines
    wc -l docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md   # expect 760
    git commit -m "<msg>" -- CLAUDE.md docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md

  `.claude/settings.json` and `.mcp.json` are a different unit of work; commit
  them separately. Two files is well under the pre-commit hook's 8-file ceiling.
  **Abort if** `wc -l` is not 760: someone edited it since 15:07 and the merge
  arithmetic below no longer holds, so re-measure before proceeding.

**Step 2. Owner: `D4 REGISTER-RECONCILE`, and only after step 1 lands.** Merge
the **commit SHA from step 1, never the branch name**: `git merge <branch>`
silently picked up an unrelated live session's commit in this repo on
2026-08-13.

**Step 3. Owner: `D4 REGISTER-RECONCILE`. Confirm by content, not by exit code.**

    wc -l docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md   # MUST be 1559
    grep -c "^K4\." docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md   # A's block follows K4
    grep -n "9.80665" docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md | head   # B's early hunks

  **1559 = 1455 + 104.** If it reads **1455, side A vanished**. If it reads
  **760, side B vanished**. Neither loss produces a conflict marker, which is
  precisely why the line count is the test and `git merge` exiting 0 is not.

**Step 4. Standing, everyone, until step 2 lands.** Nobody runs `git checkout`,
`git restore`, or a file copy on `CLAUDE.md` or the register across trees.
CLAUDE.md needs no merge at all: blob `37983d2` at base, main HEAD and the fork
tip alike, so the only thing that can happen to it is loss.

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

### The column D2 needs: what the 30 public branches actually carry

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

**Consequence for E8, stated plainly:** the licence question is not about a
derived hull on one branch. It is about the upstream crash-model decks
themselves, published 30 times over. Deleting them from `main` would leave 29
other public branches serving the same bytes, and would still not unpublish
them. This is D2's call to act on, not mine; I have not touched any of it.

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

### THE GAP THAT REMAINS OPEN, and I could not close it tonight

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

**Both were refused by the same thing: the local tool-safety classifier was
unavailable, so no command could be issued at all.** State this precisely and do
not let it become "the clusters were down": **I did not reach TACC, therefore I
learned nothing about TACC's state.** An unreachable probe is not a measurement,
which is this project's own standing rule about `~/Downloads` and about a zero
result from one root.

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

## 10. What I did not do

- **Pushed nothing.** No `git push` was run, with or without `PUSH_OK=1`.
- **Merged nothing.** The register merge was run on scratch copies in
  `/private/tmp/.../scratchpad/merge/`, never on a real branch.
- **Edited no shared file.** No write to `CLAUDE.md`, the register,
  `sim_standing.py`, or any tree other than `r5-safekeeping`.
- **Did not copy any bundle off this machine.** See section 1.
- **Ran no physics-skeptic review.** Nothing here is a percentage, force,
  verdict count or distance; every number is a commit count, a line count, a byte
  count or a SHA, each with its command printed. The register merge result (1559
  lines) is the one number a reviewer should re-run rather than trust.
