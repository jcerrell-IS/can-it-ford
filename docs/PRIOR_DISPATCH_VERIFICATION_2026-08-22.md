# Prior-dispatch verification, 2026-08-22

Checked 2026-08-22 14:20 to 14:26 BST from `Josephines-MacBook-Air.local`,
`/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `1780169`, main
checkout (`.git` is a real directory, not a worktree file).

Scope: verify two prompts dispatched in a prior session, and resolve four open
ambiguities from an external audit. **No new research. No subagents. Nothing was
merged, pushed or deleted.**

Claims are tagged `[read live]` where I ran the command and read the output this
session, and `[inferred]` where I reasoned from those reads. Where a prior
document is the source rather than my own measurement, it is named.

**Headline: both dispatched prompts ran. Neither needs to be re-run.** The
premise behind item 2 is refuted by a live cluster query. See Part 3.

---

## Verdict summary

| # | Item | Verdict |
|---|---|---|
| 1 | README landing patch (Prompt 1) committed | **PASS**, `1780169` |
| 2 | r7-inflow smoke test (Prompt 2 Unit 1) ran | **PASS**, and the premise is refuted |
| 3 | `docs/R10_WEB_ACQUISITION_2026-08-19.md` exists | **EXISTS**, tracked and on HEAD |
| 4 | `hf_space/` matches the live Hub Space | **11 files both sides**, 10 of 11 byte-identical at HEAD, 1 uncommitted |
| 5 | `can-it-ford-demo` Space identity | **Abandoned earlier version, already a redirect stub** |
| 6 | Two `R9_LOOP_CLOSURE` runs | **Extended, not duplicated.** One file, single coherent version |

---

## 1. README landing patch: PASS

`git log --oneline -- README.md` `[read live]`. The landing patch is committed as
**`1780169`**, "README: the demo is live and the dataset licence is CC-BY-4.0",
authored 2026-08-22 03:54:10 +0100, 3 insertions and 2 deletions across 3 hunks.

`git diff HEAD -- README.md` is **empty**, so the working tree matches the commit
and nothing is left pending on this file `[read live]`.

### The seven items, and which seven they are

The dispatch scoped five claims. The pass that answered it,
`docs/CROSS_PLATFORM_CONSISTENCY_2026-08-22.md`, found two more. That is the
seven. Stating the mapping explicitly, because "seven items" is not self-evident
from the document's own section numbering: its sections 7 and 9 are patch
mechanics and a re-derivation of section 6, not separate claims.

| # | Item | Verdict in that doc | Required a README edit? | Landed in `1780169`? |
|---|---|---|---|---|
| 1 | W&B badge path, owner/org, run count | VERIFIED-CURRENT | no | n/a |
| 2 | `data/l2_results_from_wandb.csv`, 9 conditions | VERIFIED-CURRENT, not undercounting | no | n/a |
| 3 | "Gradio demo: not yet deployed" | FOUND-STALE, stale 5 days | **yes** | **yes**, `README.md:175` |
| 4 | Corpus merge vs the Citations section | NO CHANGE | no | n/a |
| 5 | DesignSafe "staged, not yet published" | VERIFIED-CURRENT | no | n/a |
| 6 | HF Space understates its own dataset by 20 | finding, no patch proposed | no, it is not a `README.md` defect | n/a, still open, see 4.3 |
| 7 | Dataset licence `ODC-By-1.0` stale | FOUND-STALE | **yes** | **yes**, `README.md:166` |

Two of the seven required a `README.md` edit. Both are in `1780169`, verified by
reading the live file `[read live]`:

- `README.md:166` reads "released under CC-BY-4.0".
- `README.md:175` reads the full live-Space bullet, not "not yet deployed".
- A HuggingFace badge was added at `README.md:7`, which is part of hunk 1 of the
  same patch.

**So item 1 is a clean pass**, and it closes the open action that document's
third pass named. That pass ended by recording both fixes as "corrected in the
working tree and both UNCOMMITTED", with the remaining action a commit rather
than an edit. The commit happened 21 minutes later.

**One caveat, so the pass is not over-read.** Item 6 was deliberately not
patched, on the stated ground that `hf_space/**` was another session's active
working set. It is still open. See 4.3.

---

## 2. `docs/R10_WEB_ACQUISITION_2026-08-19.md`: IT EXISTS

**Resolved. The file is real, tracked, and present on HEAD** `[read live]`.

| Test | Result |
|---|---|
| `git log --all --oneline -- 'docs/R10_WEB_ACQUISITION*'` | 4 commits, `c469252` added it |
| `git ls-files` | `docs/R10_WEB_ACQUISITION_2026-08-19.md`, tracked |
| `git cat-file -e HEAD:docs/R10_WEB_ACQUISITION_2026-08-19.md` | present on HEAD |
| `ls -la` on the path | 33,530 bytes, mtime 2026-08-22 01:30 |
| `git branch -a --contains 52e7d7f` | `claude/add-ci-checks`, `claude/r9-gapscan`, `origin/claude/add-ci-checks` |

The four commits touching it, newest first: `52e7d7f`, `57ab55a`, `47ab55a`,
`c469252`.

**Why the earlier search reported it absent.** I did not reproduce that search,
so I cannot state its mechanism as read. What I can state is that the sessions
citing the file were right and the search that missed it was wrong, and that a
bounded ref-scoped query settles it in one command. `git log --all -- <pathspec>`
is the correct instrument here because it searches **refs**, not the filesystem,
so it is immune to both the gitignore blind spot in this shell's `grep` function
and to a file being reachable only from a branch with no worktree.

The board row at `.claude/state/r8_board.md` from d22-gapscan cites
"docs/R10_WEB_ACQUISITION_2026-08-19.md section 3.13" as its own deliverable
path, which is independent corroboration from the slot that wrote it.

---

## 3. r7-inflow smoke test: IT RAN, AND THE PREMISE IS REFUTED

**This was flagged as potentially the single highest-priority item in the
project. It is not, because it already ran, five days ago, and it succeeded.**

Queried Vista live this session via `scripts/tacc.sh` `[read live]`:

```
JobID                       JobName      State    Elapsed ExitCode                 End
918501              r7_inflow_smoke  COMPLETED   00:00:57      0:0 2026-08-17T23:18:15
918506                    r7_inflow  COMPLETED   00:13:27      0:0 2026-08-17T23:33:16
```

The smoke test is job **918501**, JobName literally `r7_inflow_smoke`, **COMPLETED,
ExitCode 0:0**. The full run it gated, job **918506**, also COMPLETED with
ExitCode 0:0.

### The results exist and are committed

On branch `claude/r7-inflow` `[read live]`:

- `data/r7_inflow_918506/profiles.npz`
- `data/r7_inflow_918506/runs.json`
- `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md`
- `docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md`

The result document's own header, read from the branch `[read live]`, states 34
of 34 runs `rc=0` and `ALLDONE`, roughly 5 SU of the 617 then available. Its
headline is a null on the verdicts and a large move in the quantity underneath
them: no canonical verdict changes across three configurations at two horizons,
5 of 5 SLIDE stays SLIDE and 5 of 5 STUCK stays STUCK, while displacement at the
canonical horizon rises 15.0 to 38.3 percent and the closed tank is measured at
1.36x a 3 degree road at the g64 baseline.

### The check as specified could not have answered this

The dispatched command was `git log claude/r8-bc-merge --oneline -5`. That branch
is a **different** piece of work. Its own tip commit `049f7e1` opens: "The task
this branch was opened for does not exist", and records that
`simulation/openchannel_bc.py` was committed twice from one lineage with a
byte-identical blob `9a94e247` `[read live]`. `r8-bc-merge` carries no r7 job
record, so no reading of its log could have shown the smoke test's state either
way. The instrument that settles it is `sacct` on Vista, which is what I ran.

### What IS actually open here

Not the run. The **landing**.

| Test | Result |
|---|---|
| `claude/r7-inflow` merged into `claude/add-ci-checks` | **NO** `[read live]` |
| `claude/r7-inflow` on `origin/main` | **NO** `[read live]` |
| `claude/r7-inflow` pushed to origin as its own branch | **YES**, `origin/claude/r7-inflow` `[read live]` |

So the work is backed up on the remote but invisible to anyone reading the
integration branch or `main`. That is the same stranding pattern
`docs/R9_LOOP_CLOSURE_2026-08-22.md` Part 5.5 records for three r9 branches, and
`r7-inflow` is a fourth instance of it, not covered by that document's table.

---

## 4. `hf_space/` versus the live Hub Space

**The desync the prior session diagnosed is 10/11 closed. One file remains, and
it is closed on disk and open in git.**

That session's reported state was 11 live files against 3 in git. Live now
`[read live]`: **11 files on the Hub, 11 files tracked at HEAD, same eleven
names.** The three commits that closed it are `adb5634`, `e91ab13` and `ca5ee11`,
all 2026-08-22 03:29 to 03:31.

### 4.1 File-by-file byte comparison

Method: `curl -sSL` each file from
`huggingface.co/spaces/josiecerrell/can-it-ford/resolve/main/<path>` into the
scratchpad, then `md5` against the working tree and against
`git cat-file blob HEAD:hf_space/<path>` `[read live]`.

| file | live vs working tree | live vs HEAD blob |
|---|---|---|
| `.gitattributes` | match | match |
| **`README.md`** | **match** | **DIFFER** |
| `app.py` | match | match |
| `arr_verdict.py` | match | match |
| `ingest_speed_surface.py` | match | match |
| `requirements.txt` | match | match |
| `speed_surface.py` | match | match |
| `surface.py` | match | match |
| `data/canonical_runs.csv` | match | match |
| `data/load_surface.csv` | match | match |
| `data/load_surface_manifest.json` | match | match |

**Ten of eleven are byte-identical on all three copies.** The exception is
`hf_space/README.md`: live and working tree are both md5 `8d0a270d...` at 5,617
bytes; the HEAD blob is md5 `ece27406...` at 4,056 bytes.

`git status --porcelain -- hf_space/` reports ` M hf_space/README.md`, a
**106 insertion / 45 deletion uncommitted change** `[read live]`.

**So the answer to "does git now match the live Space" is: on disk yes, in git
no, by exactly one file.** The remaining action is a commit, not an edit. This is
structurally the same state item 1 was in before `1780169`, on a different file.

Worth noting because a memory note warns about it: the `*.csv text eol=lf` rule
in `.gitattributes` did **not** break byte-identity here. Both CSVs match on all
three copies `[read live]`.

### 4.2 The count on both sides

- **Live Hub Space:** 11 files plus one `data` directory entry.
- **git HEAD:** 11 files (`git ls-tree -r`), 9 entries at the top level because
  `hf_space/data` is a tree.

State the recursive count. A non-recursive `ls-tree` returns 9 and reads as a
mismatch against the Hub's 11 when there is none.

### 4.3 Item 6 from Prompt 1 is still open, and committing would bake it in

Independently reproduced this session `[read live]`:

- `hf_space/data/load_surface.csv`: **368 records** plus header (`awk 'END{print NR-1}'`).
- `hf_space/data/load_surface_manifest.json`: `"rows_checked": 368`.
- `hf_space/README.md:40`, working tree **and** deployed: "live, **348** records,
  20 cells at five seeds".

Three measurements say 368; the page says 348; the gap of 20 equals the cell
count in the same sentence, which is what makes a transposition or a
copy-from-the-wrong-token the likely origin `[inferred]`.

**Consequence for the pending commit in 4.1:** committing
`hf_space/README.md` as it stands closes the git/Hub desync and simultaneously
commits the 348. Fix the number first, then commit once. That also fixes the
public page, since the deployed copy carries the same error.

---

## 5. `josiecerrell/can-it-ford-demo`: an abandoned earlier version, already redirected

**Answer: it is an abandoned, never-finished earlier Space. It has already been
converted into a redirect stub pointing at the working demo. No further action is
required, and the residual items below are cleanup, not repair.**

Live Hub API `[read live]`, `api/spaces/josiecerrell/can-it-ford-demo`:

| field | value |
|---|---|
| `private` | `False` (public) |
| `createdAt` | 2026-08-18T06:11:25Z |
| `lastModified` | 2026-08-20T23:58:57Z |
| `runtime.stage` | **`NO_APP_FILE`** |
| `cardData` | `{"title": "Can It Ford Demo", "sdk": "gradio"}` |
| `siblings` | `.gitattributes`, `README.md`, `phase_space_results.csv` |

**There is no `app.py`.** The runtime stage confirms it independently of the file
listing, so this is two separate reads agreeing rather than one read restated.

### 5.1 Its README is already a correct redirect

Read live in full. It carries no `app_file` and no licence, and its body says the
Space moved, names `josiecerrell/can-it-ford` as the working demo, states that
this one was never finished and has no `app.py`, cites `NO_APP_FILE` as
confirmation, and explains it is being kept up rather than deleted in case it is
already linked somewhere.

**Every factual claim in that redirect notice is true**, verified against the live
API and file listing above rather than taken on the page's own word `[read live]`.

### 5.2 What changed, and when

`docs/SECOND_EYES_AUDIT_2026-08-20_1200.md` records this Space at 2026-08-20
12:00 as reading `cardData.license` = `bsd-3-clause`, with a README declaring
`app_file: app.py` and no `app.py` present, and calls it "publicly erroring for
two days" and "an orphaned broken page under Josie's name, not a broken user
journey", severity "not urgent".

Live `cardData` today has **no `license` key at all** `[read live]`. Combined with
`lastModified` 2026-08-20T23:58:57Z, the card was rewritten that evening,
replacing the broken full card with the redirect stub `[inferred]`. **So the
audit's recommendation was acted on the same day it was written**, by redirect
rather than by deletion, which is the option that document listed second.

### 5.3 Two residual items, neither urgent

**(a) It still publicly serves `phase_space_results.csv` with no provenance.**
Byte-identical (md5 `bee11bf183cef9b2cda73717bf4958dc`) to the repo's tracked
`data/phase_space_results.csv` and to `kumar_july9_update/phase_space_results.csv`
`[read live]`. That is the **July-era box-proxy pilot lineage, not the 17 gated
warpmpm runs.** 31 data rows. It carries three rows at the identical condition
`(0.3, 1.5)` with **contradictory verdicts**: one `FORD` and two `NO-FORD`, with
three different displacements. A reader who finds this file has no way to know it
is superseded, because the redirect README does not mention it.

**(b) It now carries no licence field**, where it declared `bsd-3-clause` on
2026-08-20. Reading the `tags` array will not catch this: the Hub does not emit a
`license:` tag for Spaces the way it does for datasets and models, so
`cardData.license` is the field to read.

### 5.4 Recommendation

**Documented as intentionally separate is already the de facto state and is the
right one.** Nothing in `README.md`, `docs/`, `hf_space/` or `CLAUDE.md` links to
it as a live demo; the only mentions are audit rows describing it as a stub
`[read live]`. The redirect preserves any external link that may exist.

Two optional follow-ups, both requiring Josie's go-ahead because they are public
writes:

1. **Delete `phase_space_results.csv` from the Space, or name it in the redirect
   README as superseded pilot data.** Naming it is the cheaper and safer option.
   Deleting from HEAD does **not** unpublish it: the Hub serves prior revisions,
   the same property already recorded for this project's Space history.
2. **Restore a `license` field to the card** so the public artifact is not
   licence-silent.

Do **not** delete the Space. Its own README gives the reason, and it is a good
one: an unknown external link would break with nothing to redirect to.

### 5.5 A name collision worth knowing about

`~/can-it-ford-demo` is a **separate local git repository**, not a clone of this
Space `[read live]`. It holds `app.py`, `requirements.txt`, `cached_results/` and
`scripts/`, and is `main...origin/main [ahead 1]`, tip `4d228d9`, which fixes the
L1 verdict to the joint AR&R rule. **The local repo has the `app.py` the Space
lacks**, and the two are not connected. Do not treat one as a backup of the other.

---

## 6. The two `R9_LOOP_CLOSURE_2026-08-22.md` runs: the second EXTENDED the first

**Answer: one file, one coherent version. The second run appended and corrected;
it did not supersede and did not duplicate.**

Two commits touch the path `[read live]`:

| commit | time | subject |
|---|---|---|
| `1a1099d` | 2026-08-22 01:42:16 +0100 | R9 loop closure: ten unanswered decisions addressed to Josie, and one of thirteen branches reached a deliverable |
| `3262118` | 2026-08-22 02:27:10 +0100 | Second pass on R9 closure: an eleventh decision for Josie, and two corrections |

`git diff 1a1099d 3262118 -- docs/R9_LOOP_CLOSURE_2026-08-22.md` is a **pure
append**: one hunk, `@@ -405,3 +405,156 @@`, **156 lines added and zero removed**
`[read live]`. Parts 1 to 4 are untouched byte for byte. The appended block is
"PART 5. SECOND-PASS VERIFICATION", which states its own method in its opening
line: a different session re-derived the load-bearing claims from git rather than
from the document.

`git diff HEAD 3262118` on that path is empty, and `git diff` on it is empty, so
**the committed version, HEAD, and the working tree are all the same file**
`[read live]`. There is nothing to reconcile and no second copy to diff.

### What the second pass changed substantively

Recorded here so the extension is not mistaken for a rubber stamp. It carries two
explicit corrections and one addition:

- **C1.** `r9-corpus-bib` has **three** conflicted paths, not two. Part 2 named
  `SKILL.md` and `research_index.py`; live `merge-tree --write-tree` also reports
  an `add/add` on `data/deep_searches/vehicle-mesh-assets.json`.
- **C2.** The K3 caveat is narrower than Part 1.2 implies: of three card
  renderers in `analysis/hf_dataset_publish.py`, one carries the retired
  `odc-by` value and two are already `cc-by-4.0`.
- **J11**, an eleventh open decision Part 1 does not carry: whether to mint a
  citable DOI, whose only stated blocker was cleared on 2026-08-20.

It also declines to restate the 187 / 140 figure as a bare number, giving three
scoped alternatives (177, 326/254, 327/254) instead. **Both passes are marked
UNREVIEWED**; the second explicitly inherits rather than lifts that status.

**So: extended.** The correct citation form is the file plus a part number, since
Parts 1 to 4 and Part 5 were written by different sessions and Part 5 corrects
two Part 1 and Part 2 claims in place-by-reference rather than by rewrite.

---

## 7. Which of the two dispatched prompts still needs to run

**Neither. Both ran and both produced committed deliverables.**

| Prompt | Unit | Ran? | Deliverable | Residual |
|---|---|---|---|---|
| 1 | README landing fix | **YES** | `docs/CROSS_PLATFORM_CONSISTENCY_2026-08-22.md` plus commit `1780169` | none on `README.md`; item 6 lives in `hf_space/README.md`, see 4.3 |
| 2 | Unit 1, r7-inflow status | **YES**, jobs completed 2026-08-17 | `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md` on `claude/r7-inflow` | branch unmerged; no 2026-08-22 status report was written |
| 2 | Unit 2, corpus lineage duplication | **YES** | `docs/CORPUS_MERGE_FINAL_2026-08-22.md` section 7, commit `e9e80ad` | **diagnosed, not resolved**, by design |

### On Prompt 2 Unit 1, a distinction worth keeping

The **jobs** ran and the **analysis** is written. What does **not** exist is a
2026-08-22 status report reconciling that against the integration branch. The
only mention of `r7_inflow` in any 2026-08-22 document is a single line in
`docs/CLUSTER_STATE_AUDIT_2026-08-22.md:509`, listing it among job families
absent from W&B `[read live]`. This document is now that reconciliation, and its
answer is Part 3: the run succeeded, the branch is pushed, the branch is
unmerged.

### On Prompt 2 Unit 2, "ran" and "fixed" are different

`e9e80ad` states its own outcome in its first line: "DIAGNOSED, NOT RESOLVED, AND
THAT IS THE FINDING", and records that nothing was executed, no merge, no branch,
no force-push `[read live]`. That is a completed unit, not an abandoned one.

**The duplication itself is still live**, measured independently this session
against `data/research_corpus_index.json` `[read live]`:

- **332** paper records.
- **11** identifiers appearing more than once, accounting for **13** extra
  records.
- **319** distinct works, by DOI-or-link and by title independently, which agree.

11 works under 24 record keys, reproducing `CLAUDE.md`'s recorded figure exactly
and from a separate origin. `docs/CORPUS_MERGE_FINAL_2026-08-22.md` records a
rebuild as moving 332 to 319 and cited-anywhere 76 to 66, and **recommends
landing the tooling without rebuilding, so the code fix and the number change
stay separately revertable**. That is a decision waiting on Josie, listed there
as item 3 of four.

---

## 8. What is actually open, ranked

Nothing found here is a re-run. Everything is a landing or a one-line fix.

1. **`hf_space/README.md` is uncommitted, and carries a wrong number.** Fix
   `348` to `368` at line 40, then commit that one path. Closes the last file of
   the Hub desync and Prompt 1's item 6 together. Also republish so the public
   page stops understating its own dataset by 20.
2. **`claude/r7-inflow` is unmerged.** Completed work, ExitCode 0:0, pushed to
   origin, invisible from the integration branch and from `main`. A fourth
   instance of the stranding pattern `R9_LOOP_CLOSURE` Part 5.5 tabulates for
   three r9 branches.
3. **The corpus duplication decision.** 332 versus 319 is measured and stable.
   Four questions in `CORPUS_MERGE_FINAL` section 7 are addressed to Josie.
4. **`can-it-ford-demo` cleanup**, optional and public-write, see 5.4.

---

## Limits of this pass, stated so nothing here is over-read

- **A shared-tree reading expires.** `git status` reported 8 modified tracked
  files and one other session recently active in this repo at session start. Every
  working-tree statement above is timestamped to 14:20 to 14:26 BST and carries a
  blob hash or an md5 so it can be re-derived rather than trusted. This document's
  own predecessor was overtaken three times in one hour on exactly this point.
- **I did not reproduce the failing search** that reported
  `R10_WEB_ACQUISITION` absent. I established that the file exists; I did not
  establish why that search missed it, and I do not assert a mechanism.
- **I did not open `profiles.npz` or re-derive any r7 physics number.** Part 3's
  physics figures are quoted from `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md`
  as read from its branch. What I verified independently is the **job state**, via
  `sacct` on Vista, and the presence of the committed artifacts.
- **NOT ADVERSARIALLY REVIEWED.** No subagent was spawned, per the dispatch. The
  numbers in Parts 4, 5 and 7 are single-session measurements. Per the standing
  rule, they are marked unreviewed rather than presented as checked. Every one of
  them names the command that produced it, so each is cheaply refutable.
- **The Hub is a live third-party surface.** Its file listings and API fields were
  read at 14:2x BST. A push to either Space invalidates them.

*Written 2026-08-22 by a session that verified rather than re-ran. No merge, no
push, no delete, no branch created. One file staged and committed: this one.*
