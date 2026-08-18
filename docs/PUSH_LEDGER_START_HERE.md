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
      watch_register_merge.sh                  <- guards the merge (watch_side_a.sh retired)
      refresh_log.tsv                          <- every artifact, bytes + sha256 + verdict
      2026-08-17/
        ALL-refs-<HHMM>.bundle                 ~508 MB  self-contained
        ALL-refs-MINUS-credentials-<HHMM>.bundle ~508 MB  no credential branch
        INCREMENTAL-all-branches-2341.bundle     8,372,242 B   33 refs  needs origin, NEWEST
        uncommitted-2341/                      dirty worktrees, patches + tarballs, mode 0700
        incoming/                              captured from Vista, mode 0700

Current at **391 at-risk commits** (commits that exist on no remote) across 33
branches, as of the 23:41 refresh. That number climbs all evening; re-run the
refresh rather than trusting it. **The `ALL-refs-*` bundle is the only one that
stands alone**; the incremental restores only alongside a copy of `origin`, and
the pair together reconstructs current state (section 1).

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
        "$(ls -1t /Users/josie/can-it-ford-bundles/*/ALL-refs-[0-9]*.bundle | head -1)" 'refs/heads/*:refs/heads/*'
    git -C /path/to/recovered.git fetch \
        /Users/josie/can-it-ford-bundles/2026-08-17/INCREMENTAL-all-branches-2341.bundle 'refs/heads/*:refs/heads/*'
    git clone /path/to/recovered.git /path/to/work -b <branch>

Lost uncommitted work instead? Snapshots are in `uncommitted-<HHMM>/<worktree>/`:

    git -C <worktree> apply <snap>/<worktree>/tracked.patch
    tar -xzf <snap>/<worktree>/untracked.tar.gz -C <worktree>

**Drilled from bundles only, borrowing nothing from the live repo:** 77 of 77
branch tips and tree objects matched, `fsck --strict` clean, all 33 thin bundles
restored, and a real checkout produced a byte-identical `sim_standing.py`
(section 12).

## 5. The register collision: 2a, then 2b

**Step 1 is DONE.** Side A was committed as `790d999` on `claude/add-ci-checks`, carrying both `CLAUDE.md` and the register. Verified: register 760 with zero uncommitted delta, `CLAUDE.md` 823 with zero delta. Side B is untouched at 1455 on `claude/fork-register-reconcile`.

**Both sides are now in git history on separate branches, so neither can silently disappear.** What is left is an ordinary two-branch merge. Re-derived from committed objects: `git merge-file` exit 0, 0 conflict markers, **1602 = 1455 + 147**.

**Step 2a, re-create side B's tree BEFORE asking pid 10363 to act.** Its working directory was deleted; the branch is fine.

    git -C /Users/josie/can-it-ford worktree add \
      .claude/worktrees/fork-register-reconcile claude/fork-register-reconcile

Never `--force` a branch checked out elsewhere.

**Step 2b, merge the SHA `790d999`, never the branch name. Then confirm by count and by content:**

    # COMPUTE the target first: side A moves, and it has moved three times tonight
    R=/Users/josie/can-it-ford
    F=docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
    A=$(git -C $R show claude/add-ci-checks:$F           | wc -l)
    B=$(git -C $R show claude/fork-register-reconcile:$F | wc -l)
    echo "expect $(( B + A - 656 ))   sideA-vanished=$B   sideB-vanished=$A"
    # then after merging, check the result against that number.
    # Neither failure raises a conflict marker, which is why the count is the test.
    # At 00:45 this was: expect 1647, sideA-vanished=1455, sideB-vanished=848.

### The watcher, and how to re-arm it

A watcher guards the **merge**: it alerts if side B's register leaves 1455 and
reports whether it landed on the computed target or on a loss. It recomputes
`B + (A - 656)` on every poll, so it stays correct as side A moves.

**It dies when the session that started it ends, and nothing restarts it.** To
re-arm, run it as a background monitor from any session:

    /Users/josie/can-it-ford-bundles/watch_register_merge.sh

It prints one line on arming, then only on a change. If you are not running a
session, you do not need it: just compute the target with the snippet above
immediately before merging, which is the check the watcher automates rather than
replaces.

**A watcher is a convenience here, not a safety net.** Both sides are committed
on separate branches, so a bad merge is recoverable from the reflog or from
`ALL-refs-*.bundle`. This was not true earlier tonight, when side A was
uncommitted; it is true now. It dies
with its session.

## 6. The off-machine decision, Josie's

| # | destination | consequence |
|---|---|---|
| **1 (recommended)** | encrypted external volume | offline, no third party |
| 2 | private GitHub repo | quick; the licence objection is gone, so the only question left is the credential content |
| 3 | TACC `$WORK` | blocked on MFA, and those machines already hold the unrotated tokens |
| 4 | plain cloud sync | **disqualified**: this project has already had an iCloud-synced token exposed |

**UPDATED 2026-08-17 23:35: the licence axis is closed, so this is now a
one-axis decision.** Permission is **reported** granted for the NCAC/CCSA
material (D2 `a386704`) and for the Wiley/CIWEM files (D2 `2732e2b`), both
verified to exist. All three grants are **Josie's report with the artifact
pending, not confirmations**: nobody in this round has read the paperwork, and
as D2 puts it, a second and third report arriving does not upgrade the first.
Three rights holders, three artifacts still to file.

That leaves the credential axis alone, and it splits cleanly:

- **`ALL-refs-MINUS-credentials-*.bundle`** (newest, ~508 MB, controlled to
  exclude `CREDENTIAL_EXPOSURE`) is **clear on both axes and shippable to an
  ordinary destination.** It restores one fewer branch than the full bundle, and
  that difference is the check that the exclusion held.
- **`ALL-refs-*.bundle`** (newest, ~508 MB) needs **a private encrypted
  destination. That is now its ONLY route**: credentials are reported
  DEFERRED, not resolved (12 named, 0 rotated), so "the credentials dead first"
  is not a near-term option. Restore test must print **77**.

**Recommendation, since the choice has collapsed to one:** use the
MINUS-credentials variant. It exists so a credential decision never has to gate
a backup.

**Do not copy the filenames out of this page.** They change on every refresh,
and they have changed five times tonight. Let the shell pick the newest and take
the checksum from the log the refresh wrote:

    B=/Users/josie/can-it-ford-bundles
    # pick ONE of these two, see the choice above
    SRC=$(ls -1t $B/*/ALL-refs-MINUS-credentials-*.bundle | head -1)   # ships anywhere
    # SRC=$(ls -1t $B/*/ALL-refs-[0-9]*.bundle | head -1)              # private+encrypted only

    cp "$SRC" /Volumes/<NAME>/
    # the refresh logged this file's sha256 when it made it; compare, do not retype
    grep "$(basename "$SRC")" $B/refresh_log.tsv | cut -f5
    shasum -a 256 "/Volumes/<NAME>/$(basename "$SRC")" | cut -d' ' -f1
    # the two lines above MUST match

    git clone --mirror "/Volumes/<NAME>/$(basename "$SRC")" /tmp/restore-check
    git -C /tmp/restore-check for-each-ref refs/heads | wc -l
    # MINUS-credentials prints one FEWER branch than the full bundle; that
    # difference is the check that the exclusion held.

`cp` exiting 0 is not evidence the bytes landed. If the sha256 differs, delete
and redo (section 1).

---

## Open, and all three are human-gated

1. **Off-machine copy.** Needs a destination. Nothing else closes the
   one-disk exposure above.
2. **Register step 2a/2b.** Step 1 is DONE (`790d999`). What remains is
   re-creating side B's worktree and doing an ordinary merge, expecting 1602.
3. **TACC: DONE for the capture, still open for anything else.** The socket came
   back and Vista held 2 unprotected commits plus the uncommitted
   `G = 9.80665 -> 9.81` fix, all captured (section 11). Note `scripts/tacc.sh`
   **returns exit 0 even when SSH fails**, so parse its output, never `$?`.

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
