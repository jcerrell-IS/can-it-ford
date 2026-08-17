# START HERE: the work is safe, on one disk

One page. Everything here is measured, and the detail with its evidence is in
`docs/PUSH_LEDGER_2026-08-16.md`, cited by section number rather than repeated.

---

## Read this before the reassuring parts

**This insurance protects ONE MACHINE. Every bundle sits on the same physical
disk as the repository it protects.** A single disk failure loses the repo and
its insurance together, and nothing below prevents that.

The round produced a lot of comforting artifacts: verified bundles, a drilled
recovery, a watchdog, a refresh script. **None of them survives the disk.** The
one step that changes it is the off-machine copy, and that is Josie's call and
has not been executed. Until it is, treat everything below as protection against
a deleted worktree, a bad `checkout`, or a lost branch, **not** against losing
the machine.

Work on Vista and LS6 that was never fetched here is also outside all of this
(ledger section 11).

---

## 1. What the insurance is, and where

    /Users/josie/can-it-ford-bundles/          <- outside the repo, on the same disk
      refresh_bundle.sh                        <- re-take the snapshot
      watch_side_a.sh                          <- guards the orphaned register
      refresh_log.tsv                          <- every artifact, bytes + sha256 + verdict
      2026-08-17/
        ALL-refs-2207.bundle                   507,790,278 B  138 refs  self-contained
        ALL-refs-MINUS-credentials-2207.bundle 507,748,793 B  119 refs  no credential branch
        INCREMENTAL-all-branches-2207.bundle     8,079,152 B   33 refs  needs origin
        uncommitted-2207/                      dirty worktrees, patches + tarballs, mode 0700

Current at **349 at-risk commits** (commits that exist on no remote), across 33
branches. **`ALL-refs-2207.bundle` is the only one that stands alone**; the
incremental restores only alongside a copy of `origin` (section 1).

Older dated artifacts are superseded, not deleted. Always use the newest.

## 2. Re-take it, one command

    bash /Users/josie/can-it-ford-bundles/refresh_bundle.sh          # ~8 MB, seconds
    bash /Users/josie/can-it-ford-bundles/refresh_bundle.sh --full   # + the ~508 MB standalone

Read-only against the repo, takes no locks, touches no ref, also snapshots every
dirty worktree. **Run it at the end of any working session.** It went 12 commits
stale within six hours once (section 1).

## 3. Verify it

    git -C /Users/josie/can-it-ford bundle verify <bundle>          # exit 0
    git -C /Users/josie/can-it-ford bundle list-heads <bundle> | wc -l

**Do not compare two bundles by sha256.** Git bundles are not byte-reproducible:
two taken 61 seconds apart with no commits between differed by 6,964 bytes while
their ref sets were identical. Compare `list-heads`. A bundle's sha256 is for
verifying a **transfer** (section 1).

## 4. Restore, drilled end to end

    git init --bare /path/to/recovered.git
    git -C /path/to/recovered.git fetch \
        /Users/josie/can-it-ford-bundles/2026-08-17/ALL-refs-2207.bundle 'refs/heads/*:refs/heads/*'
    git clone /path/to/recovered.git /path/to/work -b <branch>

Lost uncommitted work instead? Snapshots are in `uncommitted-<HHMM>/<worktree>/`:

    git -C <worktree> apply <snap>/<worktree>/tracked.patch
    tar -xzf <snap>/<worktree>/untracked.tar.gz -C <worktree>

**Drilled from bundles only, borrowing nothing from the live repo:** 77 of 77
branch tips and tree objects matched, `fsck --strict` clean, all 33 thin bundles
restored, and a real checkout produced a byte-identical `sim_standing.py`
(section 12).

## 5. The register collision: 2a, then 2b

Two additive edits to one file in two places. **Side A is orphaned**: 104
register lines and 73 CLAUDE.md lines sit uncommitted in the main checkout with
no session owning them. **Side B's branch is intact but its worktree was
deleted**, and its process (pid 10363) is still alive with a dead working
directory (section 13).

The merge itself is measured clean: `git merge-file` exit 0, zero conflict
markers, **1559 = 1455 + 104**. CLAUDE.md has no collision at all.

**Step 1, side A, needs a human.** Abort if the count is not 760.

    cd /Users/josie/can-it-ford
    wc -l docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md      # MUST be 760
    git commit -m "<msg>" -- CLAUDE.md docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md

**Step 2a, re-create the tree BEFORE asking pid 10363 to do anything.**

    git -C /Users/josie/can-it-ford worktree add \
      .claude/worktrees/fork-register-reconcile claude/fork-register-reconcile

Never `--force` a branch that is checked out elsewhere.

**Step 2b, merge the SHA from step 1, never the branch name. Then confirm:**

    wc -l docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md      # MUST be 1559

**1455 means side A vanished. 760 means side B did. Neither raises a conflict
marker**, which is why the line count is the test and `git merge` exiting 0 is
not (section 6).

A watchdog is running on side A and alerts on any change with a restore command
attached. **It is a watchdog, not an owner: it cannot commit, and it dies with
its session.**

## 6. The off-machine decision, Josie's

| # | destination | consequence |
|---|---|---|
| **1 (recommended)** | encrypted external volume | offline, no third party |
| 2 | private GitHub repo | quick, but hands 508 MB incl. unresolved CCSA material to a third party |
| 3 | TACC `$WORK` | blocked on MFA, and those machines already hold the unrotated tokens |
| 4 | plain cloud sync | **disqualified**: this project has already had an iCloud-synced token exposed |

**UPDATED 2026-08-17 23:26: the licence axis is closed, so this is now a
one-axis decision.** Permission is reported granted for the NCAC/CCSA material
(D2 `a386704`, verified to exist) and for the Wiley/CIWEM files (relayed, no SHA
yet). Both are **Josie's report with the artifact pending, not confirmations**.

That leaves the credential axis alone, and it splits cleanly:

- **`ALL-refs-MINUS-credentials-2251.bundle`** (507,831,989 B, 123 refs,
  controlled to exclude `CREDENTIAL_EXPOSURE`) is **clear on both axes and
  shippable to an ordinary destination tonight.** Restore test must print **76**.
- **`ALL-refs-2251.bundle`** (507,891,648 B, 142 refs) still needs **a private
  encrypted destination, or the credentials dead first** (none rotated). Restore
  test must print **77**.

    cp .../ALL-refs-2207.bundle /Volumes/<NAME>/canford-2026-08-17/
    shasum -a 256 /Volumes/<NAME>/canford-2026-08-17/ALL-refs-2207.bundle
    # MUST print 50596650be7efd516e0039237ba1e1385fdb33d61e519b7c7827bb60be714083
    git clone --mirror <copied bundle> /tmp/restore-check
    git -C /tmp/restore-check for-each-ref refs/heads | wc -l     # MUST print 77

`cp` exiting 0 is not evidence the bytes landed. If the sha256 differs, delete
and redo (section 1).

---

## Open, and all three are human-gated

1. **Off-machine copy.** Needs a destination. Nothing else closes the
   one-disk exposure above.
2. **Register step 1.** Orphaned side, no owner, unchanged since it was written.
3. **TACC.** `ssh vista` and `ssh ls6`, once each with the 6-digit token; both
   hosts are reachable and only MFA is blocking. Note `scripts/tacc.sh`
   **returns exit 0 even when SSH fails**, so parse its output, never `$?`
   (section 11).

Also unhandled, and not mine to do: `scripts/canford_monitor.sh` is still
uncommitted in `concurrent-session-safety-570b39`, and it is the only copy of
that tool in the project (section 3).

---

## Two traps that cost time here

**Never trust an exit code you did not check directly.** `scripts/tacc.sh`
returns 0 on SSH failure; `cmd | head` reports `head`'s status, not `cmd`'s.
Both produced a confident wrong answer in this round.

**Session-relative time is unreliable, and only when a session has been parked at
a permission prompt.** Wall-clock sources here (`date`, `stat`, git author
stamps) are reliable and mutually consistent. When a session's sense of elapsed
time conflicts with them, **the session is wrong**. A 21-hour block once read as
"minutes ago" and nearly became a false clock-anomaly finding (section 13).
