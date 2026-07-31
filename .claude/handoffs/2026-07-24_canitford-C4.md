# Handoff: canitford-C4, 2026-07-24 evening

Written 2026-07-25 03:50 UTC (2026-07-24 22:50 CDT) by pane canitford:0.4.

Task: replace the single shared SESSION_STATE.md write pattern with an append-only, one-file-per-session handoff pattern. Done. Nothing was committed, nothing was pushed, no simulation was run, no GPU was requested.

---

## The problem this fixes

Every pane used to Edit or Write `SESSION_STATE.md` directly. When two panes write within the same second, the second write is built on a copy of the file read before the first write landed, so the first pane's update disappears. No error is raised. Nobody finds out until a claim that was recorded is later missing, and by then it looks like the pane never did the work.

That is last-writer-wins, and with fourteen-plus concurrent contexts against one working tree at `/Users/josie/can-it-ford` it is not hypothetical. `tmux ls` at 03:37 UTC showed the twelve canitford and ford panes plus sessions `monitor` (3 panes, two running claude) and `panel_monitor` (1 pane running claude).

## The convention

### 1. One file per pane per round

```
.claude/handoffs/<YYYY-MM-DD>_<session>-<pane>.md
```

for example `.claude/handoffs/2026-07-24_canitford-C4.md`. One writer per file, so there is no contention and no possible silent loss. Write it with the Write tool, normally, no ceremony.

If you write a second handoff on the same date, suffix it: `2026-07-24_canitford-C4_b.md`. Never overwrite an existing handoff. They are the record of what was believed at a point in time, including what turned out to be wrong.

### 2. Append exactly one line to the index

```
.claude/handoffs/INDEX.md
```

Append with a shell redirect. Never Edit it, never Write it:

```bash
printf '| %s | HANDOFF | `%s` | %s | %s |\n' \
  "$(date -u '+%Y-%m-%d %H:%M')" \
  "2026-07-24_canitford-C4.md" \
  "canitford-C4" \
  "one line on what this handoff contains" \
  >> .claude/handoffs/INDEX.md
```

This matters mechanically, it is not style. `>>` opens with `O_APPEND`, so the kernel positions each write at the current end of file. Two panes appending a short line at the same moment both land, in some order. Edit and Write instead read the whole file, modify it in memory, and write it back whole, which is precisely the read-modify-write race that loses data. The index is append-only because appending is the operation that is safe under concurrency, not because rewriting is untidy.

Never rewrite or reflow an existing line, even to fix a typo in it. If a line is wrong, append a new line that corrects it.

### 3. SESSION_STATE.md is now a generated summary view

Only two panes write it: canitford-C4 owns the canitford section, ford-F5 owns the ford section, never both at the same instant. Everyone else stays out and writes a handoff instead. It is hook-gated on Edit and Write by `.claude/hooks/gate_protected_files.sh`, so touching it prompts. That prompt is the reminder that you are in a shared file.

Read order for a fresh session: `SESSION_STATE.md`, then `.claude/handoffs/INDEX.md`, then only the handoff files you actually need.

### 4. Mission files are indexed, and typed distinctly

`_mission_*.md` files are inbound task assignments from the orchestrator. I chose to index them, with type `MISSION` rather than `HANDOFF`.

Indexed, because an index that silently omits files that are sitting in the directory teaches readers not to trust it, and silent omission is a failure class this project has already been bitten by more than once.

Typed distinctly, because a mission is an instruction that has not been carried out yet, while a handoff is a report of work that has. A future session that read a mission file as if it were a report would treat unexecuted instructions as completed work, which is a worse failure than not listing it at all. The type column is what keeps those apart, and it is a column rather than a section heading because sections cannot grow by appending, only by rewriting, which is the thing this file must never do.

`ARCHIVE` is the third type: frozen snapshots, never edited after creation.

## What I changed

- Created `.claude/handoffs/2026-07-24_ARCHIVE_session-state-pre-restructure.md`, a byte-identical copy of the pre-restructure `SESSION_STATE.md`, made with `cp` before anything was touched. Verified: both md5 `565d5b308e5f9b4e90de3354e655155f`, 396 lines. Nothing from the old file is gone.
- Rewrote `SESSION_STATE.md` as a summary view: the preserved fingerprint block, the new convention, a live pane roster, live git state, and open items split into VERIFIED LIVE THIS PASS versus CARRIED FORWARD.
- Populated `.claude/handoffs/INDEX.md`, which existed but was 0 bytes.

## What I preserved

The block dated `2026-07-25 03:32 UTC (2026-07-24 22:32 CDT), orchestrator: CLAUDE.md drift fingerprint` survives byte-for-byte and is still at the top of `SESSION_STATE.md`.

It was extracted with `sed -n '13,37p'`, fingerprinted, and the same region re-extracted and re-hashed after the rewrite:

- 25 lines, 2781 bytes, md5 `d4f9d11276f0e7e29aa8947303b2b982` before
- same md5 after, `diff` clean, and it landed back on lines 13 to 37

**This block was the uncommitted change in the working tree.** `git diff SESSION_STATE.md` before I started was exactly those 26 added lines and nothing else. It exists in no commit. Had anyone overwritten `SESSION_STATE.md` without archiving first, the drift fingerprint would have been gone permanently, with no way to recover it from git. That is the single sharpest edge I found tonight and it is the reason the archive was made before the rewrite rather than after.

## Corrections made to migrated content

Migration was not a copy. Claims were re-checked before being carried forward, and one was wrong:

**The personal-profile leak claim is stale.** The old file states three copies of the personal CLAUDE.md are "tracked on public origin/main right now" and must not be labelled clean. As of 03:40 UTC that is no longer true:

- `git ls-files` returns none of them
- `git ls-tree -r origin/main` returns none of them
- `git log --all -- 'files/CLAUDE_md_*'` returns no commits at all, so they are absent from reachable history
- `.gitignore:46` carries `files/CLAUDE_md_*.md`, so `git add -A` cannot re-add them

The three files still exist untracked on disk under `files/`. Their contents were not read; they are deny-listed in `.claude/settings.json`. What remains is the historical disclosure window, roughly 2026-07-18 to 2026-07-23, and the pre-purge clones, which still carry pre-purge history. Rewritten in `SESSION_STATE.md` to say that instead.

Everything else was carried forward under a CARRIED FORWARD label meaning migrated but not re-verified this pass. The old file mixed live and stale claims with no way to tell which was which, which is how a five-day-old security claim survived as present tense.

## Found and NOT fixed

1. **Local `main` is 3 commits ahead of `origin/main`, not 2.** Tonight's briefs name `af1db6d` and `85e2252`. Live `git log origin/main..HEAD` also shows `4d2242b` "Add verified facts ledger", committed 22:36:04 CDT, after the briefs were written. The push hold therefore covers three commits. This widens the hold, it does not weaken it. Not acted on.

2. **The protected-file hook has a hole.** `gate_protected_files.sh` matches on `Edit|Write` only. A shell redirect such as `cat x > SESSION_STATE.md` is a Bash call, and `gate_destructive.sh` only matches `git push`, `filter-repo`, `git commit`, `rm -rf` and `rm -r `. So any pane can silently overwrite `SESSION_STATE.md`, `CLAUDE.md` or `README.md` from Bash with no prompt at all. I deliberately used the Write tool and took the prompt rather than `cat`, even though `cat` would have guaranteed byte-exactness more directly, because routing around a gate Josie installed is not mine to do quietly. The hook files are already modified in the working tree by another context, so I did not touch them. Worth closing.

3. **Two different files named `INDEX.md`.** `.claude/handoffs/INDEX.md` is this registry. `HANDOFF_AUDIT_2026-07-24/INDEX.md` is a separate knowledge-base index from the July 24 provenance audit, untracked, different format and purpose. Anyone told to "check the index" can land on the wrong one. Not renamed, since the audit directory is not mine.

4. **Finder-style duplicates in `HANDOFF_AUDIT_2026-07-24/`:** `handoff_kb` (empty) alongside `handoff_kb 2` (populated), and `AUDIT_TABLE copy.md` alongside `AUDIT_TABLE.md`, both 14160 bytes. Untracked. Deletion is Josie's call.

5. **`.claude/settings.json.bak.20260723231255`** is sitting untracked in the tree next to a modified `settings.json`. Someone should decide whether it is still needed.

6. **W&B key contradiction is unresolved and I did not resolve it.** The archive asserts rotation CONFIRMED DONE in the 2026-07-19 block and asserts the revoke is still UNCONFIRMED in the cross-cutting block. Both are in the same file. Confirming it requires wandb.ai, which I did not touch. Carried forward as an explicit contradiction rather than picked.

7. **`~/.pane_signals/canitford_0_7_done` exists**, dated Jul 24 12:20, but there is no pane `canitford:0.7` in the live roster. Stale signal from an earlier layout. Harmless, but it is another reason not to read signal files as completion.

8. **Mission files are undated.** `_mission_canitford-C4.md` carries no date in its name, so a second round's mission to the same pane would overwrite the first. Suggest `_mission_2026-07-24_canitford-C4.md` going forward. Not renamed, the orchestrator owns those.

## Optional or deferred, filtered against tonight's three anchors

None of these serve the poster (July 27), the paper (July 31), or a verified rendered physically plausible MPM simulation with a vehicle, so none were done:

- Deleting the nested `can-it-ford/can-it-ford/`, the pre-purge clones, or the `.bak` files. Housekeeping, needs Josie's explicit confirmation, serves no anchor.
- Closing the Bash-redirect hook hole in item 2. Protects the anchors rather than advancing them. Recommended but optional, and the hook files are held by another context.
- Resolving the W&B contradiction and the Vista `CLAUDE_CODE_OAUTH_TOKEN` rotation. Security, genuinely important, but neither is on an anchor and both need credentials I should not be handling.

## The tree moved during this pass, which is the argument for the whole convention

Between starting and finishing, without any coordination and without a single conflict:

- HEAD moved from `85e2252` to `9f5d82e`. Four commits landed from other panes during the pass (`4d2242b`, `60a01a2`, `63e677f`, `9f5d82e`), so the ahead-count went 2, then 3, then 6. Any of the three numbers would have been correct when written and wrong minutes later.
- Five new `_mission_*.md` files appeared, for C1, C2, C5, F5, and an F5 addendum.
- C5 wrote `2026-07-24_canitford-C5.md`, a full poster-asset handoff, at 05:41 UTC.

Under the old pattern C5 and I would both have been editing `SESSION_STATE.md` in that window, and one of us would have lost the work silently. Under the new pattern C5 wrote its own file, I wrote mine, and I appended index rows for both. Nothing collided and nothing needed merging.

C5 did not append its own index row, because it finished before this convention existed. I backfilled rows for its handoff and for the five mission files, and appended a `NOTE` row saying so, rather than passing the backfill off as their own entries. From here each pane appends its own.

I also needed a type the header did not define (`NOTE`). Rather than edit the type list, which the rule forbids, I appended a line defining it. That is the correction mechanism working as intended on its first real use.

Because the count kept moving, the git section of `SESSION_STATE.md` now says to re-run `git log --oneline origin/main..HEAD` before quoting a number, instead of trusting the one written there.

## For the next pane

Write your own file, append one line to the index, stay out of `SESSION_STATE.md` unless you are C4 or F5. If you need a parameter, a citation or a threshold, read `docs/VERIFIED_FACTS_LEDGER_july24.md` first; it supersedes both `SESSION_STATE.md` and the archive where they conflict, and its Section B lists claims already proven false so you do not re-derive them.
