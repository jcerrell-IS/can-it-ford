# R8 tooling provenance: what `.claude/tooling/` is, why nothing could see it, and
# the verdict on three background processes

Slot `d6-tooling`, branch `claude/r8-tooling`, worktree
`.claude/worktrees/r8-tooling`. Written 2026-08-18, 21:44 to 22:10 BST.

Every number below was measured live during that window. Where a figure comes from
another session it is labelled as theirs and marked as not re-derived here.

---

## 1. The directory was never added, not gitignored

This is the distinction the slot was dispatched to resolve, and it decides the fix.

| probe | result |
|---|---|
| `git check-ignore -v .claude/tooling/round5_autodispatch.py` | no output, exit 1 |
| `check-ignore` on the directory and all 17 files | no file is ignored |
| `git log --all -- .claude/tooling` | empty |
| `git ls-files -- .claude/tooling` | empty |
| `.gitignore` rules matching `.claude` | 8 rules, none covers `tooling/` |
| `.gitignore` in this worktree vs main checkout | byte-identical |

So `.claude/tooling/` was simply never `git add`ed. **`.gitignore` needed no edit and
was not touched**, even though this slot was authorised to edit it.

Why it mattered, from `CLAUDE.md` section "Hooks must fail open": anything wired to
`$CLAUDE_PROJECT_DIR/.claude/tooling/` is absent from every worktree and errors there.
This repo currently has 21 worktrees, so an untracked tool is invisible from all of them.

### 1a. The count is 17, not 19

`find .claude/tooling -type f` returns 17: 16 at top level plus `checks/r7_mirror_control.py`.
The dispatch said 19. Nothing is missing; the dispatch figure was simply high.

### 1b. Committed byte-unchanged, and proved so

Three commits, split only because `.git/hooks/pre-commit` refuses more than 8 staged
files. 6 + 6 + 5 = 17.

- `24b9c35` the two MCP servers, their two backups, `mcp_scaffold.py`, `checks/r7_mirror_control.py`
- `43968bb` the dispatch automation
- `b89ec7c` install notes and the three `MERGE_` templates

`git diff --name-status 0efe4f3 HEAD` returns **17 `A` and zero `M` or `D`**;
`git diff --stat` reads `17 files changed, 2807 insertions(+)` with no deletions.

Byte-identity was then checked a second time at the level that actually matters, the
**committed blob** rather than the working file, by piping `git cat-file blob` through
sha256 and comparing against the main checkout. 17 compared, 0 mismatches. The exec bit
survives on the two executables (`100755` on `round5_autodispatch.py` and
`round5_launch.sh`, `100644` on the rest).

A first attempt at that comparison **passed falsely** and is recorded here because the
failure mode is reusable: the check ran inside a `while read` subshell that had lost
`PATH`, so `git` and `shasum` were both "command not found", both hashes were the empty
string, and every line printed `OK`. A comparison of two empty strings is not a
comparison. The rerun used Python with an absolute `git` path and printed the digests
themselves, so a silent empty result cannot masquerade as agreement.

Manifest of what was committed (sha256 of file content):

```
1390608521216d1fa58ad46990a06c8daa417b2da72995a6d324b4ad86364251  ERRORS_AND_RESOLUTIONS.md
e913f4ca8319f7332a6ff7847bec6184a4b1d04ee5a693b57ff853e6bd877839  INSTALL.md
f6202f69d2f77ae5b6bc9da90ceb585575afffb5b85c660b0d0109455381f33b  MERGE_github_workflow.yml
3c272e90e20b8877cb03508761e36d4040ea11c4ccf10cbb45b7b74c7556e6e3  MERGE_mcp.json
c83b821f0c6c454c2ab8a58952c7fe630af1877f3ce783800a5b13f45f487076  MERGE_settings_hook.json
716c3cd50ec4941d0100aa5b8e9435ac7ae1dfd170216dfd14126c31b22810bd  checks/r7_mirror_control.py
73b9815cde1f6a64352e867cda3d6bedd85c20f9cd48f95f1e97cccddf7d0e9a  commit_autoapprove.py
f40a8bd6cc88a9355fa6beb88b21af08551dd6abbdec49cfccc5d2778c51793e  corpus_mcp.py
4afb9a367b490b33197079e63344d9b7f0ee700b31035872a9497f57e2c5526b  corpus_mcp.py.bak-portability
85d3c87e1b760d06ffd050b43fda66722ca7102e08d0deeaed0a9ce6cc330d68  dispatch_uniqueness.py
8bf591165f913bb5e89dfd0fcadd100faf12bd047d7687fae66b244d91bf2ff0  frame_review_app.py
9dbd1be0bc4b2e5de3ca6e7ca13990385c617515a2dd7be53e8b6095abd27939  mcp_scaffold.py
d8c19f4509eeea4cc7ad63d0632aeb9065bffe37f559245f8c575b338d612ea2  round5_autodispatch.py
64e4492cc9ef29827440dc46b669a79af4d65ea2933705f14d8c2896e38d1399  round5_launch.sh
9df415310c8c5c1663235bfa4a1ca153477c424998d8946faa8fd6f0ca655ce5  settings_WITH_autoapprove.json
781c6791c5203aa0056f43ac86601c64237c2c43e4527a7799d609a264006270  tacc_mcp.py
c5dd6d054934f633d3bc02a564627f7de24224c22ddd090907fbf87053573008  tacc_mcp.py.bak-portability
```

`corpus_mcp.py` was changed AFTER this manifest was taken, by `51677d3` (section 5), so
its digest above is the as-tracked baseline, not the current file. That ordering was
deliberate: track first, then fix, so the fix is a reviewable diff rather than a file
that appears already modified.

### 1c. A merge hazard nobody has hit yet

The originals still sit untracked in the **main checkout's** working tree, which this slot
must not touch. When `claude/r8-tooling` is merged into `claude/add-ci-checks`, git may
refuse the checkout because untracked files occupy those exact paths.

The resolution is not `git checkout -f`. Use the manifest above to prove the untracked
originals are byte-identical first, and only then remove them:

```
cd /Users/josie/can-it-ford/.claude/tooling && shasum -a 256 -c /path/to/manifest
```

If every line reads `OK`, nothing is lost by deleting them. If any line fails, someone
edited the main checkout copy after 2026-08-18 22:00 and that edit must be read before
anything is discarded.

### 1d. The two `.bak-portability` files are the PRE-edit state

Asked because "backup" implies an ordering nobody had checked. **Timestamps cannot
answer it**: `corpus_mcp.py`, `tacc_mcp.py` and both `.bak` files all carry an identical
mtime of `2026-08-18 04:25:44`.

Content settles it. Each `.bak` differs from its live file by exactly one line replaced
by three:

```
-REPO = "/Users/josie/can-it-ford"
+REPO = os.environ.get("CANFORD_REPO") or "/Users/josie/can-it-ford"
+# ^ env override added 2026-08-18 so the server works from a plugin cache copy
+#   and from a fresh clone. Absent the env var, behaviour is byte-identical.
```

The `.bak` copies hold the hardcoded path, the live files hold the override, so the
`.bak` files are the earlier state and the naming is correct. Line counts corroborate:
258 to 260 and 270 to 272.

They are **kept, not deleted**. Deleting them is outside this slot's scope, and they are
now tracked, so a later session can remove them in a reviewable commit.

---

## 2. Verdicts on the three background processes

All three were dispatched to this slot as running. Measured at `2026-08-18 21:46:04`,
**two were already gone**, stopped by the coordinator at roughly 21:35, and the third was
not the process the dispatch described.

### 2.1 `round5_autodispatch.py`, PID 54804: STOPPED, and correctly so

Not by this session. Confirmed absent from `ps`, and corroborated from a **separate
origin**: `.claude/state/round5_autodispatch.log` ends at `21:35:46` with an mtime of
21:35, and on its 90 second interval the next entry would have been `21:37:16`, which was
never written. The `ps` table and the missing log line are independent observations of
the same fact.

What it was doing, measured from that log:

- first entry `2026-08-16 14:49:48  D1: follow-up sent (164m idle, hash d0052396d4)`
- last entry `2026-08-18 21:35:46  D3: composed message is a DUPLICATE, refusing to send`
- **1357 lines** reading `DUPLICATE, refusing to send`

It targeted tmux `canford5` panes D1, D2 and D3. Live `tmux list-panes -a` shows
`canford5` holds a shell plus D2, D3 and three Round 7 sessions. **There is no D1 pane**,
so one of its three targets had been gone for some time and a third of its work was
addressed to nothing.

**1357 and 36 are different quantities and both are real.** They were briefly treated here
as a discrepancy; they are not, and the pair is worse than either number alone.

| figure | what it counts | source |
|---|---|---|
| 1357 | messages the dispatcher COMPOSED and then REFUSED to send | this session, counting `DUPLICATE, refusing to send` in `.claude/state/round5_autodispatch.log` |
| 37 | misrouted follow-ups that actually LANDED in `r7-pinned-span` | that session's own running tally in its transcript |

So the dispatcher **refused 1357 and delivered about 37**. Its deduplication guard worked
throughout while its routing did not, which is why neither number on its own describes the
failure: a broken router behind a working guard looks quiet from the log side.

The R8 board records 36. Verified live from the receiving session's transcript
(`~/.claude/projects/-Users-josie-can-it-ford--claude-worktrees-r7-pinned-span/45445c36-...jsonl`,
1580 lines): the running tally reaches `"Thirty-seventh misroute; ignoring."` and there is
no thirty-eighth, so **the final count is 37 and 36 is the second-to-last tally line**. The
difference changes nothing about the conclusion and is recorded only because the number is
now written down in two places. Note also `"Misroutes thirty-three through thirty-five
(three arrived batched)"`, so the tally counts messages, not turns.

The script is now tracked at `43968bb`, so its behaviour is reviewable from any worktree
rather than only from the main checkout.

### 2.2 `canford_monitor.sh`, PID 98633: STOPPED, and this one deserved a closer look

Not by this session. Absent from `ps`. Per the board, a respawn loop in tmux
`canford:0-MONITOR` was interrupted at the same time. This session did not verify the
respawn loop and does not restate that half.

The reason it is worth care rather than relief is in section 3.

### 2.3 `watch_register_merge.sh`, PID 44782: **LEFT RUNNING ON PURPOSE**

The dispatched premise is stale. PID 44782 is gone. A **different** instance, PID 20392,
was running at measurement time, 9 minutes old, and it is not stale automation:

```
20392 bash watch_register_merge.sh
  -> 20389 zsh (a Claude Code Bash-tool wrapper, /tmp/claude-6065-cwd)
    -> 78633 claude, elapsed 2d 07:57
      -> 73779 -zsh  ==  tmux pane canford5:2.0
         "D3 SAFE-THE-WORK with Opus", cwd .claude/worktrees/r5-research
```

That pane is one of the five the board declared off limits to every R8 slot. Killing it
would have reached into a live sibling's session.

Ownership and age would have been enough, but the script was read before the verdict was
finalised, because "a monitor nobody reads is still a monitor someone may rely on" cuts
both ways and a monitor that is merely *old* is not automatically *stale*. Reading it
strengthened the verdict:

- It guards a **silent** failure mode. Merging the corrections register side A into side B
  can drop one side entirely without producing a conflict marker, so a wrong merge looks
  exactly like a right one. The watcher checks the arithmetic instead.
- It watches **branches, not files**, so it holds nothing and blocks no other session.
- It is actively maintained, not abandoned: its own comments record three separate
  narrowings, the last at `2026-08-18 04:43`, each one reducing what it alarms on rather
  than describing the noise better.
- Its target is live. Side B `claude/fork-register-reconcile` exists at `c1235e5`.

Its formula, and a number `d7-register` may want, computed live at 22:04:

- side A `claude/add-ci-checks` register: **2186** lines
- side B `claude/fork-register-reconcile` register: **1455** lines
- side A vs base `1a868f3`: **1 hunk**, so the single-append invariant the formula rests
  on still holds
- expected merge target `B + (A - 656)` = **2985** lines

If that hunk count ever leaves 1, the formula stops applying and the watcher says so
itself rather than printing a confident wrong target.

**Verdict: leave running. It is a live sibling's active safety tool, and stopping it would
remove a guard on the register merge at exactly the moment the register is being worked
on by another R8 slot.**

---

## 3. `scripts/canford_monitor.sh` is still a single-disk copy

Definition-of-done item 3. This slot may not commit on another session's behalf, and did
not.

Measured live:

- worktree `.claude/worktrees/concurrent-session-safety-570b39`, branch
  `claude/meta-prompt-reconcile-dispatch-14a3c8`
- `git status` shows ` M scripts/canford_monitor.sh`, a **+17/-3** uncommitted edit
- the file is tracked on **exactly one branch**, that one, and that branch is local only
- no live Claude pane occupies that worktree
- the diff is unchanged since 2026-08-16, so nobody is mid-write on it

D3 flagged this on 2026-08-16 and asked whoever was live there to commit it. Nobody has.

### 3a. A correction to this slot's own first reading

`find /Users/josie/can-it-ford-bundles -name 'canford_monitor.sh'` returns **nothing**,
which reads as "the snapshot claim is false and the edit is unbacked". That conclusion was
wrong and is withdrawn before it was acted on.

The edit **is** backed up, as a **patch** rather than as a file copy, at
`can-it-ford-bundles/2026-08-16/uncommitted-worktrees-snapshot/concurrent-session-safety-570b39/tracked.patch`.
A fresh `git diff` of that worktree was taken and byte-compared against it:

```
5c82afecbfdd1e6121f1f1062a4017567f8c5f2d70a368c8a5c1c35fef253b8d  (live git diff)
5c82afecbfdd1e6121f1f1062a4017567f8c5f2d70a368c8a5c1c35fef253b8d  (2026-08-16 snapshot)
```

Identical. So a search by filename cannot see a backup stored as a diff, and "I searched
and found nothing" was a statement about the search, not about the world.

**Accurate statement of the risk: single DISK, not single COPY.** The committed base is in
`branch~claude~meta-prompt-reconcile-dispatch-14a3c8.bundle` and the uncommitted +17/-3 is
in the patch above, but both live on the same machine as the original. A disk failure
loses all three. Committing the edit is still the right fix; it is just not an emergency.

---

## 4. METHOD NOTE: a comparison whose both arms failed, reported as agreement

Three sessions hit this in one night, with three different tools. It is a pattern, not
three anecdotes, and this slot owns tooling, so it is written up here.

**The shape.** A check compares two things. Both sides fail to produce a value. The two
failures are equal to each other, so the comparison returns "same" and the check reports a
clean pass. Nothing errors. The output is not just wrong, it is *reassuring*.

### The three instances

**(a) `d6-tooling`, this session, a hash comparison of 17 files.** Verifying that the
committed blobs matched the main checkout, the comparison ran inside a `while read`
subshell that had lost `PATH`. `git` and `shasum` were both "command not found", so both
digests were the empty string, `[ "$a" = "$b" ]` was trivially true, and **all 17 lines
printed `OK`**. See section 1b. The rerun used Python with an absolute `git` path and
printed the digests themselves.

**(b) `d7-register`, a content probe over register copies.** Read directly from that
session's transcript, not relayed: "My first content probe used `md5 -q`, which errored on
both sides under this shell; both sides returned identically empty and the probe reported"
SAME. That session called both arms erroring and being reported as agreement "the single
most dangerous shape on this project". The count of affected entries (six) is the
coordinator's figure and was not re-derived here.

**(c) `coordinator`, a process-respawn check.** A process was killed, a **six second**
window was observed, nothing came back, and "verified no respawn" was written to the board.
Six seconds cannot detect a process that a live session relaunches on its own cadence. The
absent evidence was read as evidence of absence. Refuted in section 2.3; the coordinator
found and corrected it themselves at 22:05, re-measuring independently rather than
accepting this session's report, so section 2.3 corroborates rather than claims it.

(c) is the same family rather than literally two failed arms: the *sample* was too narrow
to contain the phenomenon, and a clean sample was generalised into a verified absence. In
all three the tool exited cleanly and the **probe** was what failed.

A fourth, closely related instance appears in section 3a of this document: a
`find -name canford_monitor.sh` that returned nothing because the backup exists as a
**patch** rather than a file copy. That one produced a false *alarm* rather than a false
pass, which is the same defect with the sign flipped, and it is the safer direction to fail.

### The rule

**A check must distinguish "equal" from "could not evaluate".** Those are different
answers and only one of them is a pass. Concretely:

- **Print what the probe saw, not just its verdict.** Two empty strings are visibly not two
  digests. A verdict alone hides its own inputs.
- **Verify the probe on a known-different pair before trusting it on an unknown one.** A
  comparator that cannot produce a FAIL has not been shown to work.
- **Treat a run of uniform passes as evidence to distrust.** This is what caught (a): every
  line passed, including files there was no reason yet to trust.
- **Say which view you searched.** A negative result is a statement about the probe's
  reach, not about the world, until the reach is stated.

This is the same discipline the positive control in section 5 enforces for
`corpus_cited_status`: a fix for a check that cannot fail needs a test that can fail, and
the way to know it can is to make it go red on purpose.

---

## 5. `corpus_cited_status`: a checker whose corpus included its own output

Routed here by `d5-priorart` because the file is this slot's. Fixed in **`51677d3`**.

### The defect class, named, because it will recur

**A checker whose search corpus includes its own findings cannot fail.** Any note it
provokes becomes evidence that the thing it warned about is fine. The feedback is positive
and silent: the more diligently the problem is documented, the more confidently the checker
reports that there is no problem.

That is the general form. The specific instance is worse than the general one:

`corpus_cited_status` calls itself THE NOVELTY GUARD and names the four vehicle-fording
prior-art works in its own tool description. It then answered the question by running
`/usr/bin/grep -rIl` over `docs/`, `paper/` and `CLAUDE.md` and setting
`cited_in_repo = len(hits) > 0`. It never opened a `.tex` file.

Reproduced from source before reading anyone else's report. Needle `10.1115/1.4071177`
returns **6 files: four `docs/` notes, the `.bib`, and `CLAUDE.md` itself**.

`CLAUDE.md`'s own sentence, verified live at lines 746 to 750 on 2026-08-18 and quoted
here as the anchor because line numbers in that file go stale, reads "Four prior vehicle
fording or wading simulations exist and `paper/` cites NONE of them:" and then lists the
four DOIs, `10.1115/1.4071177` among them. **That sentence is one of the six hits.** So the canonical record that these papers are uncited is part of what made the
guard answer "cited". The project wrote down the problem, and writing it down is what hid it.

Two design rules follow, and they generalise past this file:

1. **A checker must not read the tree it is warning about.** Ground the answer in the
   artifact whose state is in question, here the submitted LaTeX, not in commentary about it.
2. **Distinguish the artifact from the discussion of the artifact.** A DOI in a note, a DOI
   in a `.bib` and a `\cite` key in the tex are three different claims. Collapsing them into
   one boolean is what made "cited" unfalsifiable.

### What the old check actually measured

Parsing the LaTeX instead: `paper/conference_101719.tex` carries 21 cite commands and 11
distinct keys. All four prior-art works have `.bib` entries among the 42, and **none of the
four is `\cite`d**:

| work | bib key | in .bib | cited in tex |
|---|---|---|---|
| He 2026 `10.1115/1.4071177` | `he2026vehiclewater` | yes | no |
| Wasfy 2015 `DETC2015-47142` | `wasfy2015fording` | yes | no |
| Khapane 2014 `10.4271/2014-01-0936` | `khapane2014wading` | yes | no |
| Pazouki 2016 | `pazouki2016fording` | yes | no |

**Three separate origins** agree, which is why this is treated as established rather than
as one session's claim: `d5-priorart` reported it this round; the committed
`docs/HANDOFF_ROUND_7_2026-08-18.md:528-529` already called it "a check that cannot fail"
and told sessions never to use the tool; and this session reproduced it from source
without having read either. Separate origins, so this is corroboration and not one source
cited three times.

### The fix

Citation is now resolved from the LaTeX rather than from a file listing. The verdict
separates **CITED IN THE PAPER**, **IN THE BIBLIOGRAPHY BUT NEVER `\cite`d**, and
**MENTIONED IN NOTES**. A `docs/` hit can no longer produce "cited"; it is reported
separately and never drives the verdict.

Three traps handled, each of which would have restored the always-true behaviour:

- `\nocite{*}` excluded. It pulls the whole `.bib` in without citing anything, so counting
  it would mark every entry cited.
- LaTeX comments stripped, so a commented-out `\cite` is not a citation.
- a missing or unreadable `paper/` returns **CANNOT ANSWER**, never a quiet "not cited".

`cited_in_repo` was **removed rather than redefined**, so a caller written against the old
meaning breaks loudly instead of silently getting a different question answered. No code
caller exists; the callers are sessions.

`d5-priorart`'s ready-to-apply diff had not landed when this was written (their worktree
was clean at `fbecf5d`), so this implementation is independent. **If that diff appears
later, diff it against `51677d3` rather than applying it on top.**

### The test

`.claude/tooling/checks/corpus_cited_status_selftest.py`, committed alongside. A fix for a
check-that-cannot-fail needs a test that can, so it carries a **positive control**, a paper
that really is cited, reached by DOI through the same resolution path, next to the four
negatives. 13 checks, all passing.

Mutation-tested in both degenerate directions so the test is not itself vacuous:

| mutation | checks that go red |
|---|---|
| reinstate the old always-cited behaviour | 4 |
| always answer "not cited" | 1, the positive control |

---

## 6. Flagged, not changed: `analysis/research_index.py` shares the shape

Outside this slot's scope, so it was read and left alone.

`repo_cited_dois()` computes two sets from "every DOI-shaped string" found in the tree,
with `cited_reader_facing` restricted to `paper/`, `docs/`, `deliverables/` and
`citations/`. Its docstring is honest about what it measures, but the **field names**
`cited_in_repo` and `cited_reader_facing` say "cited", and a `docs/` mention or a bare
`.bib` entry satisfies both. The four prior-art works above would count as reader-facing.

`CLAUDE.md`'s headline is derived from this and is worded carefully: "43 of 332 papers
**reach** `paper/`, `docs/`, `deliverables/` or `citations/`". **Reach** is accurate and
should not be read as **cited**. The 43 is not challenged here.

The open question for whoever owns `analysis/`: how many of the 43 are actually `\cite`d
in the submitted paper? The tex carries 11 distinct cite keys, so the answer is at most 11
and the gap between 11 and 43 is the whole of the exposure. That is a measurement, not a
defect claim, and it has not been made.

---

## 7. What this session did not verify

- ~~The board's "36 misroutes into `r7-pinned-span`"~~ NOW VERIFIED, and corrected to **37**,
  from the receiving session's own transcript. See section 2.1.
- The board's claim that a respawn loop in tmux `canford:0-MONITOR` was driving
  `canford_monitor.sh`, and that it was interrupted. Absence from `ps` is confirmed; the
  loop is not.
- Whether `d5-priorart`'s independently authored diff agrees with `51677d3`. It had not
  landed.
- Whether any hook or MCP config currently points at `.claude/tooling/`. Tracking the
  directory is correct either way, but the blast radius of a future change to these files
  has not been mapped.
- Whether git will in fact refuse the checkout described in 1c. The manifest makes that
  question safe to answer the slow way rather than the forced way, but the behaviour was
  not tested.

---

## 8. Scope compliance

- `.claude/settings.json` **unedited**. Main checkout mtime `2026-08-18 03:09:05`, this
  worktree's copy `21:39:17`, both before this session began at 21:44, and the two are
  byte-identical at sha256 `7f60d1a9...`.
- `.gitignore` untouched, because section 1 showed it is not what hid the directory.
- No write outside `.claude/tooling/**` and this file.
- No tmux pane signalled, no key sent, no process stopped by this session.
- Nothing pushed. The repo is public and a push is a separate authorisation.
