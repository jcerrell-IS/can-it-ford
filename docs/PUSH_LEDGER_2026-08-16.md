# PUSH LEDGER, 2026-08-16

D3 SAFE-THE-WORK. Every number below was measured live on 2026-08-16 between
15:01 and 15:35 local, against `/Users/josie/can-it-ford`, git 2.50.1
(Apple Git-155). Each section names the command that produced it, so it can be
re-derived rather than trusted. Claims are tagged **read** (direct measurement),
**inferred**, or **UNREVIEWED** (no independent check run).

---

## 1. The work is bundled. 34 bundles, all verified, restore tested

**read.** Output directory, outside the repo:

    /Users/josie/can-it-ford-bundles/2026-08-16/     512 MB, 34 .bundle files

| artifact | contents | bytes | verify |
|---|---|---|---|
| `ALL-refs.bundle` | 147 refs, self-contained | 507,116,489 | OK |
| `branch~*.bundle` x 33 | one per at-risk branch, incremental | 1,142 to 7,082,463 | OK, all 33 |

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

### Remaining exposure, not fixed by me

The bundles are on the **same physical disk** as the repo (`/dev/disk3s5`,
408 GB used of 926 GB). Disk loss still loses everything. Copying
`ALL-refs.bundle` off-machine is the obvious next step, but it is an outward
move of 507 MB that includes the credential-exposure documents, so it needs an
explicit destination decision. Not done, deliberately.

---

## 2. Corrections to the inherited counts

**read.** The round-4 reconciliation and the round-5 bootstrap both say
"**188 commits across 11 branches**". Live:

    git rev-list --count --branches --not --remotes         ->  241
    (per branch: git rev-list --count <b> --not --remotes)  ->  33 branches > 0

**241 commits across 33 branches**, deduplicated. The 11-branch figure came from
the 13-row dispatch table baked into `canford_monitor.sh` (see section 3), not
from the branch list. **22 of the 33 at-risk branches were never in scope of any
previous safety check.** Several are old and small (`analysis/failure-modes` 3,
`audit/g-mergetest-2026-08-04` 5, `paper/submission-close` 7), which is probably
why they were dropped, but "188 across 11" should not be repeated.

Note the count moves under your feet: `claude/r5-exposure` went 1 -> 3 and
`claude/r5-research` 1 -> 2 during this session, because sibling sessions were
committing while I measured. Any total here is a timestamp, not a constant.

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
   "blocked, therefore contained". It is not contained. It is live on a public
   repo with the credentials it describes still unrotated.

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

### The sequence

The danger is not the merge. It is that 177 lines exist only as uncommitted text
in a working tree that four live sessions share. A `git checkout -- <path>`, a
`git stash`, or a branch switch by any of them destroys it with no conflict
marker and no reflog entry.

1. **Already done, needs no permission:** the uncommitted state is snapshotted
   outside the repo at
   `can-it-ford-bundles/2026-08-16/uncommitted-maintree-snapshot/` (mode 0700):
   the four-file patch, raw copies, all 94 untracked files as a tarball, and a
   sha256 MANIFEST. **Verified:** the patch re-applies cleanly onto 777567a in a
   throwaway clone. This is insurance only; it does not replace step 2.
2. **Whoever owns the main tree commits first**, path-limited, on its own branch:

       cd /Users/josie/can-it-ford && \
       git commit -m "<msg>" -- CLAUDE.md docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md

   Separately for `.claude/settings.json` and `.mcp.json`, which are a different
   unit of work. Four files is under the pre-commit hook's 8-file ceiling.
3. **Then, and only then**, merge that commit into `claude/fork-register-reconcile`.
   Merge the **SHA**, not the branch name: `git merge <branch>` picked up an
   unrelated live session's commit in this repo on 2026-08-13.
4. **Confirm survival by content, not by exit code.** After the merge the
   register must be **1559 lines**, and must contain both:
   - a line from A's appended block (the last 104 lines, which begin after the
     existing `K4.` entry), and
   - a line from B's early hunks (its edits at base lines 19-64, the gravity and
     9.80665 corrections).

   If it is 1455 lines, A vanished. If it is 760, B vanished. Neither loss
   produces a conflict marker.
5. **Nobody `git checkout`s, copies, or `git restore`s either file across trees**
   until step 3 lands.

---

## 7. Live hazard, outside my scope but reported here because it is a safety issue

**read.** All four round-5 dispatch sessions are running in the **same working
tree on the same branch**:

    tmux list-panes -a -F '#{session_name}:#{window_index} #{pane_current_path}'
    canford5:1  /Users/josie/can-it-ford/.claude/worktrees/r5-research
    canford5:2  /Users/josie/can-it-ford/.claude/worktrees/r5-research
    canford5:3  /Users/josie/can-it-ford/.claude/worktrees/r5-research
    canford5:4  /Users/josie/can-it-ford/.claude/worktrees/r5-research

Confirmed independently by `lsof -a -p <pane shell pid> -d cwd` on all four.
`round5_launch.sh` is not the cause: its window loop passes `-c "$REPO/$dir"`
with the correct per-dispatch directory, and all four worktrees exist on their
correct branches. The panes were started somewhere other than that loop.

This is the exact 2026-08-07 failure: one shared index, so a bare `git commit`
from any session sweeps another's staged work, and CLAUDE.md's standing rule
against `git add -A` is not sufficient protection on its own.

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

## 8. What I did not do

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
