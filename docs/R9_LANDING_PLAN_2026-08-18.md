# R9 landing plan: getting nineteen branches onto a remote, and making the CI run honestly

Slot `d16-landing`, branch `claude/r9-landing`, worktree `.claude/worktrees/r9-landing`.
Written 2026-08-18 23:40 to 2026-08-19 00:20 BST, revised 2026-08-19 17:12 BST after a
seventeen-hour gap, and revised again 2026-08-19 18:20 BST (the filename keeps the dispatch
date). Each revision re-ran the whole simulation rather than patching the previous numbers.

## REVISION 3, 2026-08-19 18:20 BST: what changed, and what I got wrong

Read this before anything below it. Revision 3 was triggered by the coordinator accepting
`8c07765` and supplying three updates. Re-deriving them turned up four things, and **two of them
are errors in my own earlier revisions, not staleness.**

| # | change | status of the earlier text |
|---|---|---|
| 1 | The title said "local-only". `claude/add-ci-checks` **is on `origin`** and was pushed at 17:51 today. | WRONG when written, not stale |
| 2 | Section 3 said "**exactly one** conflicting file". There are **five**, across four merges. `.gitignore` conflicted at every tip I ever measured, including both I claimed against. | WRONG when written, not stale |
| 3 | Section 6.1 said the CI "runs nowhere". It has run **seven times on GitHub, all green**, because its trigger has no branch filter. | WRONG when written, not stale |
| 4 | Section 0's "64 ahead" carried a 2026-08-18 22:49 measurement under a 17:12 date. Live it is **67**. | stale, and mis-dated |

## REVISION 4, 2026-08-19 19:05 BST

Triggered by the coordinator's request for a mechanism-classified conflict table, a public-write
section, and the CI item reframed. Four substantive changes, and **two more of them are
corrections to me**:

| # | change | where |
|---|---|---|
| 1 | Conflicts classified by mechanism: **2 add/add** (merge-base absence) and **4 content**, which need different resolution AND different verification | 3.0, and the table above it |
| 2 | **`hf_space/` did NOT lose the joint rule.** `d18-platform` executed option A, not C. Verified five ways against the LIVE public Space, including reachability | 3.5 |
| 3 | **Five public surfaces, not two**, three written today, one of them a 36-run public model repo with a 15-byte README that nobody has named | 5.5, 5.5a |
| 4 | CI reframed: the goal is not "make it execute", it is **"make it able to fail"** | 6.2a |
| 5 | I asserted a merge mechanism from plausibility and it was refuted in one command | 3.0 |
| 6 | My "scope difference" attribution on the `make_phase_space.py` count was wrong; the reader's structural mechanism is right and I confirmed it independently | 12.1(b) |

Item 3 has a compensation worth stating: section 6.2 predicted, from a local `git archive`
simulation, that `count_claims` would exit 1 with 25 blocking defects and be masked by
`continue-on-error`. The real CI log says **exactly that**, 25 BLOCK lines and
`##[error]Process completed with exit code 1`, on a job reported green. Those are two genuinely
separate origins, so section 6.2's finding is now corroborated rather than merely simulated.

Everything the coordinator sent was checked rather than adopted; update 1 needed narrowing, and
updates 2 and 3 reproduced exactly. See section 12.

**This is a plan for Josie to approve. Nothing in it has been executed against the repository.**
No branch was merged, no ref was moved, nothing was pushed, nothing was deleted. Every merge
result below was produced by `git merge-tree --write-tree`, which writes no ref, or inside a
throwaway mirror clone under the session scratchpad.

Every claim is tagged **MEASURED** (a command was run, and the command is given so you can re-run
it), **READ** (a file or git object was read directly), or **INFERRED**. Nothing is carried from
another session's summary without an independent check. Where I checked a sibling slot's claim
and got a different answer, the difference is stated as a difference, not silently adopted.

---

## 0. The thing to fix first, because every other number in this plan sits on top of it

**`claude/add-ci-checks` is 67 commits ahead of `origin/main` AND 5 commits BEHIND it.**

MEASURED 2026-08-19 18:15:

```
git -C /Users/josie/can-it-ford rev-list --left-right --count origin/main...claude/add-ci-checks
# -> 5	67        (left = behind, right = ahead)
```

**CORRECTION TO THIS DOCUMENT, and it is the kind this document exists to catch.** Revisions 1
and 2 printed `5	64` and revision 2 presented it as re-derived "at 17:12 on 2026-08-19". It was
not. MEASURED, walking the branch reflog and re-running the count at each tip:

| tip | when the tip was created | behind / ahead |
|---|---|---|
| `af62473` | 2026-08-18 22:49 | 5 / **64** |
| `e0d2beb` | 2026-08-19 00:19 | 5 / **65** |
| `faf53d1` | 2026-08-19 17:46 | 5 / **66** |
| `7a0d08a` | 2026-08-19 18:11 | 5 / **67** |

At 17:12 the tip was `e0d2beb`, which reads **65**. The *behind* half genuinely was re-measured
at 17:12 and was right. The *ahead* half was carried from the previous night and re-dated. **A
number and its timestamp have to be re-derived together or neither is re-derived.** The behind
half is the load-bearing one and it is unchanged at 5, so no conclusion below moves; the defect
is in the evidence, not the finding.

### 0a. `claude/add-ci-checks` is NOT local-only. It is on `origin`, and was pushed today

MEASURED, a live network read, not the cached remote-tracking refs (which are stale by
construction, per the register's own warning about interrogating a clone about itself):

```
git -C /Users/josie/can-it-ford ls-remote --heads origin | wc -l          # -> 46 remote heads
git -C /Users/josie/can-it-ford ls-remote --heads origin | grep -E 'r8-|r9-'   # -> nothing
git -C /Users/josie/can-it-ford reflog show origin/claude/add-ci-checks
# -> faf53d1 ... update by push   2026-08-19 17:51:13 +0100
# -> 59234f9 ... update by push   2026-08-18 21:52:34 +0100
# -> de191b8 ... update by push   2026-08-18 06:07:44 +0100
```

So the correct statement is narrower than "nothing is pushed", and the narrower version is the
one that matters:

- **`claude/add-ci-checks` is on `origin` at `faf53d1`.** Three pushes, the most recent ten
  minutes before revision 3 began.
- **Its local tip `7a0d08a` is one commit AHEAD of the remote copy** and that commit is unpushed:
  `7a0d08a` "Register C1 was wrong about git: content ancestry and merge behaviour are
  independent". So the branch is *partly* landed, which is the state most likely to be misread in
  either direction.
- **No `r8-*` or `r9-*` branch exists on `origin` at all.** That half of the dispatch premise is
  correct and is what the rest of this plan addresses.
- `claude/r5-research`, `r5-physics`, `r5-safekeeping` and `r5-exposure` are also on `origin`, so
  "this wave's work has never reached a remote" is true of R8 and R9 and false of R5.

Two consequences. First, the disk-loss exposure is smaller than stated but not small: eighteen of
nineteen branches exist on one disk. Second, and this is section 6's whole story, **the CI file
reached GitHub the moment `add-ci-checks` was first pushed**, which is why the workflow has been
running for two days while every summary in the project said it could not.

Every prior statement of this relationship in the project, including the one the session-start
banner prints, gives only the ahead half. The behind half is the one that matters for a landing,
because **almost every branch in this round is based on `claude/add-ci-checks`**, so almost every
branch is built on a base that is missing merged work. MEASURED at 17:12 on 2026-08-19 across all
nineteen: every one reads `5` commits behind `origin/main` except `claude/r8-licence`, which reads
`0` because it is the only branch that already contains `origin/main`.

The 5 missing commits are merged pull requests, MEASURED with
`git -C /Users/josie/can-it-ford log --oneline claude/add-ci-checks..origin/main`:

| SHA | subject |
|---|---|
| `c7f0a16` | Skip the AI review when unconfigured instead of failing the PR (#14) |
| `1c71a5a` | Give Vercel something to deploy, and only that (#13) |
| `aee70ab` | hf upload --exclude takes one pattern per flag (#12) |
| `f6348c7` | Space L1 used the Large 4WD threshold for a Yaris and dropped two of three conditions (#11) |
| `647aaa0` | Sync only hf_space/ to the Space, not the whole 407MB repo (#10) |

Three of those five touch CI or Hugging Face sync. #14 in particular changes how a workflow
behaves when it is unconfigured. So a landing that ignores the behind half is landing new CI on
top of a branch that does not have the most recent CI fix, and the collision would appear in
`.github/`, which is the one directory where a silent wrong answer is hardest to notice because
nobody reads a workflow file after it goes green.

That is not a hypothetical risk. MEASURED, the incoming side changes exactly 7 files
(`git diff --name-only $(git merge-base claude/add-ci-checks origin/main)..origin/main`), and
**two of the seven are workflow files**:

```
.github/workflows/physics-consistency-review.yml
.github/workflows/sync-to-hub.yml
analysis/wandb_log_gated_runs.py
hf_space/README.md
hf_space/app.py
vercel.json
web/index.html
```

**Consequence for the plan: Phase 1 is `origin/main` into `claude/add-ci-checks`, before anything
else.** MEASURED: that merge is CLEAN.

---

## 1. Inventory: fifteen branches, not nine. Eighteen by the time I finished, nineteen a day later. Do not read a tip out of this section.

**REVISION 3 STATUS: the count is still 19 and the tips below are stale.** Two branches moved
during revision 3 (`claude/add-ci-checks`, `claude/r9-priorcode`), one of them between two
consecutive commands. Section 2 carries the 18:20 tips and section 9.1 carries the procedure that
makes both sections unnecessary. **This section is kept for its structure, the base layers and
the containment relations, not for its SHAs.** Live count, MEASURED 2026-08-19 18:15:
`git for-each-ref 'refs/heads/claude/r8-*' 'refs/heads/claude/r9-*' 'refs/heads/claude/add-ci-checks' | wc -l`
returns **19**. The whole repository holds **105** local branches, **84** of them ahead of
`origin/main`; the wave is the subset this plan is about.

The dispatch for this slot said nine. Nine is the R8 wave. Six R9 slots (`d11` to `d16`) were
running while this document was being written, on six more unpushed branches, and one of them
committed mid-session (section 8). **The exposure is fifteen branches and it is still growing.**

> **ADDENDUM, 00:20, eighteen minutes after the table below was measured.** Re-running the
> section 9.1 command as a final check returned **eighteen** branches, not fifteen. Three new
> ones exist that did not exist when I started (`claude/r9-moving-vehicle`, `claude/r9-platform`,
> `claude/r9-priorcode`, all still at `af62473`), and two more have moved:
> `claude/r9-kramer-extract` `b6fe951` -> `c2f3592`, `claude/r9-settle` `af62473` -> `0726c18`.
> I have deliberately **not** rewritten the table to say eighteen. The table is a correct
> measurement with a timestamp on it, and replacing it would hide the only thing that really
> needs to be understood about this landing: **the set is not a list, it is a rate.** Any plan
> that fixes a branch count is wrong before it is read. Section 9.1 is the inventory; section 1
> is an illustration of what section 9.1 returned at one instant.
>
> The ahead/behind counts from the same run make the section 0 point again, and now for
> eighteen branches: every one of them reads `5` on the left except `claude/r8-licence`, which
> reads `0` because it is the only branch that already contains `origin/main`. Seventeen of
> eighteen are behind by the same five merged PRs.

> **SECOND ADDENDUM, 2026-08-19 17:12, seventeen hours after the first.** The session resumed
> after a long gap (my prompt banner was reporting a stale 00:17, and the true clock was 17:12;
> the times in the first addendum are correct, the gap after it was not visible to me until I
> checked `date` against a file mtime). In those seventeen hours the set went from eighteen to
> **NINETEEN** branches and **seven R9 branches committed real work**:
>
> | branch | was | now | own commits | files |
> |---|---|---|---|---|
> | `claude/r9-accessor` | `6ed163e` | `06c7786` | 73 | 31 |
> | `claude/r9-corpus-bib` | `59c12b2` | `8bad9b4` | 2 | 4 |
> | `claude/r9-kramer-extract` | `b6fe951` | `1f126dc` | 77 | 33 |
> | `claude/r9-moving-vehicle` | `af62473` | `056ba10` | 2 | 3 |
> | `claude/r9-priorcode` | (new) | `fdf934b` | 1 | 2 |
> | `claude/r9-renders` | `af62473` | `256d013` | 1 | 2 |
> | `claude/r9-settle` | `0726c18` | `0861b52` | 2 | 4 |
>
> **I re-ran the entire landing simulation against these current tips rather than patching the
> old result, and the plan survives unchanged.** MEASURED: still exactly one conflicting file,
> still `simulation/openchannel_bc.py`, still only on `r8-bc-merge` and `r8-persistence`, still
> resolved by the same blob, still one `pre-commit` refusal at 13 files. **All seven newly
> committed R9 branches merge CLEAN**, and `claude/r9-platform` is the only remaining no-op.
> Final tree 1033 files, up from 1019, `canford-checks.yml` present. So the order in section 2 is
> robust to a full day of additional work across seven branches, which is the useful thing to
> know about it, and is a stronger claim than the original simulation could support.

### 1.4 `docs/R9_DISCREPANCY_REGISTER_2026-08-19.md` is not a sixteenth merge, and its status changed twice while I checked it

It was described to me as "a sixteenth thing to merge". MEASURED, it is not, and the reason is
worth recording because it is the same moving-state problem in a third costume:

- **00:14**: untracked. `git status` returned `?? docs/R9_DISCREPANCY_REGISTER_2026-08-19.md`,
  and a scan of every local branch found it on **none** of them. At that moment it existed only
  as a working-tree file in the **shared** main checkout: not committed, therefore in no bundle,
  therefore protected by nothing at all. That is a worse status than the branches this plan
  exists to protect, and it sat alongside 151 other untracked non-ignored files in that tree.
- **00:26**: committed as `e0d2beb` on `claude/add-ci-checks`, together with
  `scripts/r8/r8_launch.sh` and `scripts/r8/r8_plan.tsv`, 3 files, 133 insertions.

Because it landed **on the integration branch itself**, it needs no merge of its own. It arrives
with the target and is carried by phase 1. **The merge set is unchanged.**

Two consequences that are not cosmetic:

1. **`claude/add-ci-checks` moved from `af62473` to `e0d2beb`**, so every branch based on
   `af62473` is now one commit behind it. MEASURED, this changes nothing in section 2: re-running
   the merges against `e0d2beb` returns CONFLICT for `r8-bc-merge` and `r8-persistence` and CLEAN
   for `r8-register` and `r8-tooling`, identical to the results against `af62473`.
2. **d7-register's decisive precondition was re-checked against the new tip and still holds.**
   MEASURED at 17:12 on 2026-08-19, against the moved tip `e0d2beb`: the register blob on
   `claude/add-ci-checks` is still `124dd74`, so the
   `r8-register` merge remains valid. `e0d2beb` touched three files and none of them is the
   register. This is exactly the check section 9.2 says to run at the moment of merging rather
   than trusting from a document, and running it caught nothing this time, which is the point:
   it is cheap and it is the only thing standing between a moved tip and a silent re-derivation.

**The general lesson for the landing: "uncommitted in the shared main checkout" is a real and
common state here, and it is invisible to every branch-level protection in this plan.** A bundle
captures commits. It does not capture 151 untracked files. Before the landing, decide which of
those files are work and which are debris, because a `git clean` during conflict resolution
would take all of them.

MEASURED at 00:01:14 on 2026-08-19. Re-derive with the script in section 9.1; do not trust the
tips below, they are a snapshot and at least one of them was already wrong within ten minutes.

`ownCommits` counts commits reachable from the branch but not from `claude/add-ci-checks`. It is
NOT a count of that slot's own work: several branches share unpushed lineage through
`claude/can-it-ford-round-5-87a6d6` (`fbecf5d`), so the same commits are counted on more than one
row. `files` is the honest measure of what each branch changes, being
`git diff --name-only $(git merge-base claude/add-ci-checks <branch>)..<branch>`.

| branch | tip | base on add-ci-checks | ownCommits | files | declared scope (from the board) |
|---|---|---|---|---|---|
| `claude/r8-persistence` | `a363dbf` | `1a868f3` | 27 | 21 | `analysis/r8_persistence_frequency.py`, `docs/R8_PERSISTENCE_GATE_2026-08-18.md` |
| `claude/r8-force` | `ec968e6` | `777567a` | 80 | 32 | `analysis/r8_noforcing_control.py`, `docs/R8_FORCE_ROUTE_2026-08-18.md` |
| `claude/r8-bc-merge` | `598792e` | `1a868f3` | 2 | 2 | `simulation/openchannel_bc.py`, `docs/R8_OPENCHANNEL_BC_RECONCILE.md` |
| `claude/r8-priorart` | `969955d` | `1a868f3` | 21 | 10 | `docs/R8_PRIOR_ART_2026-08-18.md` (explicitly did NOT write `paper/`) |
| `claude/r8-tooling` | `ff9d605` | `0efe4f3` | 6 | 19 | `.claude/tooling/**`, `docs/R8_TOOLING_PROVENANCE.md` |
| `claude/r8-register` | `e473e7d` | `0efe4f3` | 4 | 2 | the register, `docs/R8_REGISTER_MERGE_2026-08-18.md` |
| `claude/r8-naming` | `7697695` | `0efe4f3` | 6 | 9 | `analysis/make_poster_figures*.py` and four more; NOT `public_release/` |
| `claude/r8-kramer` | `b6fe951` | `777567a` | 75 | 31 | `simulation/r5_physics/kramer_benchmark.py`, `docs/R8_KRAMER_INTERCODE_2026-08-18.md` |
| `claude/r8-licence` | `cca97f2` | `1a868f3` | 7 | 11 | `LICENSE`, `THIRD_PARTY_NOTICES.md`, `citations/README.md` |
| `claude/r9-accessor` | `6ed163e` | `777567a` | 72 | 30 | R9, live |
| `claude/r9-corpus-bib` | `59c12b2` | `af62473` | 1 | see 8 | R9, live, MOVED mid-session |
| `claude/r9-kramer-extract` | `b6fe951` | `777567a` | 75 | 31 | R9, live |
| `claude/r9-landing` | `af62473` | `af62473` | 0 | 0 | this document |
| `claude/r9-renders` | `af62473` | `af62473` | 0 | 0 | R9, live |
| `claude/r9-settle` | `af62473` | `af62473` | 0 | 0 | R9, live |

### 1.1 Four base layers, which is why order matters

MEASURED, `git merge-base claude/add-ci-checks <branch>`. The branches were cut from
`claude/add-ci-checks` at four different points, and those points are themselves in sequence
along that branch:

```
1a868f3  ->  0efe4f3  ->  777567a  ->  af62473
   |            |            |            |
r8-persistence  r8-tooling   r8-force     r9-landing
r8-bc-merge     r8-register  r8-kramer    r9-corpus-bib
r8-priorart     r8-naming    r9-accessor  r9-renders
r8-licence                   r9-kramer-extract  r9-settle
```

### 1.2 Three branches are already contained in others, so the effective merge set is smaller

MEASURED with `git merge-base --is-ancestor`:

- `claude/r8-kramer` and `claude/r9-kramer-extract` are the **same commit**, `b6fe951`. Merging
  either merges both.
- `claude/r9-accessor` (`6ed163e`) is an **ancestor of `claude/r8-force`**, and also of
  `claude/r8-kramer`. As of now it carries no unique work; it is a base point that `d11` will
  move.
- `claude/r9-landing`, `claude/r9-renders`, `claude/r9-settle` are all still exactly `af62473`,
  identical to `claude/add-ci-checks`. Merging them today is a no-op.

**This will stop being true.** These are live slots. Re-run section 9.1 at merge time; a branch
that is a no-op now becomes real work the moment its slot commits, which is exactly what
`claude/r9-corpus-bib` did at 23:58 (section 8).

### 1.3 This plan's own branch is one of the fifteen

`claude/r9-landing` is in the table above, and this document is the only thing on it. A landing
plan that leaves itself out of the landing is the same defect class that `d6-tooling` named on
`claude/r8-tooling` in commit `ff9d605`, and the two should be read together.

READ, `docs/R8_TOOLING_PROVENANCE.md` on `claude/r8-tooling`, section "The defect class, named,
because it will recur":

> **A checker whose search corpus includes its own findings cannot fail.** Any note it provokes
> becomes evidence that the thing it warned about is fine.

Theirs is an instrument that wrongly **includes** its own output in what it measures, so it can
never report a problem. Mine would be an instrument that wrongly **excludes** its own output from
what it measures, so it can never report itself as unfinished. Same fault, opposite sign: in both
cases the instrument is mis-scoped relative to the thing it is supposed to describe, and in both
cases the error is invisible from inside the instrument. `d6-tooling`'s two design rules
generalise to this document without modification, and rule 1 is the one that bites here: ground
the answer in the artifact whose state is in question, not in the commentary about it. For a
landing plan the artifact is `git`, not the plan.

---

## 2. Merge order, with the reasoning

**Target shape: consolidate all fifteen onto `claude/add-ci-checks` as an integration branch,
then take `claude/add-ci-checks` to `main` as a single merge.**

That shape is not mine. It is `d7-register`'s, READ from `docs/R8_REGISTER_MERGE_2026-08-18.md`
section 9.1 on `claude/r8-register`, and the reason given there is specific and correct:

> It should **not** be merged into `main` directly. `origin/main`'s register is the 656-line
> ancestor of both inputs, and landing there first would leave `add-ci-checks` holding a register
> that is simultaneously behind on content and ahead on commits.

MEASURED, the whole order below was simulated end to end. Script:
`scratchpad/simfinal.sh`, reproduced in section 9.3.

**REVISION 3 TABLE, MEASURED 2026-08-19 18:20 against live tips.** The simulation applies
section 3.1's resolution at step 7, so a conflict shown at step N is a real new conflict and not
step 7's carried forward. Script: `scratchpad/simres.sh`, reproduced in section 9.3. It runs
entirely inside a throwaway hardlinked mirror clone and writes nothing to the repository.

| step | incoming | tip | result | files changed | `pre-commit` |
|---|---|---|---|---|---|
| 1 | `origin/main` | `c7f0a16` | CLEAN | 7 | not invoked |
| 2 | `claude/r8-register` | `e473e7d` | CLEAN | 2 | not invoked |
| 3 | `claude/r8-licence` | `cca97f2` | CLEAN | 4 | not invoked |
| 4 | `claude/r8-tooling` | `ff9d605` | CLEAN | 19 | not invoked |
| 5 | `claude/r8-naming` | `7697695` | CLEAN | 9 | not invoked |
| 6 | `claude/r8-priorart` | `969955d` | CLEAN | 10 | not invoked |
| 7 | `claude/r8-bc-merge` | `598792e` | **CONFLICT** 1 file | 2 | passes |
| 8 | `claude/r8-persistence` | `a363dbf` | **CONFLICT** 2 files | 12 | **REFUSES** |
| 9 | `claude/r8-kramer` | `b6fe951` | CLEAN | 31 | not invoked |
| 10 | `claude/r8-force` | `ec968e6` | CLEAN | 2 | not invoked |
| 11 | `claude/r9-accessor` | `06c7786` | CLEAN | 4 | not invoked |
| 12 | `claude/r9-kramer-extract` | `1f126dc` | CLEAN | 2 | not invoked |
| 13 | `claude/r9-landing` | `8c07765` | CLEAN | 1 | not invoked |
| 14 | `claude/r9-corpus-bib` | `6ecf4e5` | **CONFLICT** 1 file | 4 | passes |
| 15 | `claude/r9-renders` | `d55ac14` | CLEAN | 4 | not invoked |
| 16 | `claude/r9-settle` | `0861b52` | CLEAN | 4 | not invoked |
| 17 | `claude/r9-moving-vehicle` | `98d4d9d` | CLEAN | 4 | not invoked |
| 18 | `claude/r9-priorcode` | `0a83b75` | CLEAN | 3 | not invoked |
| 19 | `claude/r9-platform` | `f988882` | **CONFLICT** 2 files | 9 | **REFUSES** |

Final simulated integration head: **1044 files**, `canford-checks.yml` present,
`simulation/openchannel_bc.py` at the resolved blob `61afb193`.

**What moved since the 17:12 table, and why the order still holds.** Three branches committed
real work in between (`r9-corpus-bib`, `r9-platform`, `r9-priorcode`) and two of the three now
conflict. `r9-platform` is no longer a contained no-op; it carries 9 files of change. The
*order* does not have to change, because both new conflicts are at the tail and neither blocks
anything downstream of it. What changes is that **four merges now need a human, not two**, and
**two now need a `--no-verify` override, not one**.

**`claude/r9-priorcode` moved twice during this revision**, from `a863ee7` to `f31a71f` to
`0a83b75`, the second time between two of my own commands. That is the section 1 point made
concrete: do not read the tips out of this table. Re-derive them with section 9.1.

### 2.1 Why `r8-register` goes second, and this is the one place I disagree with its own document

`d7-register`'s section 9.5 says the danger is someone running a plain
`git merge claude/fork-register-reconcile` **after** its work lands:

> It will report zero conflicts, because the lineages edit disjoint regions, and it will
> reintroduce the duplicate item 17/18/19 numbering that section 4 exists to resolve.

**The hazard is real. Its timing is the mirror image of what the document says.** MEASURED, three
merge simulations of `claude/fork-register-reconcile` (`c1235e5`) against three different targets:

| target | result |
|---|---|
| `claude/add-ci-checks`, i.e. **before** `r8-register` lands | **rc=0, ZERO CONFLICTS** |
| `claude/r8-register` tip | rc=1, CONFLICT in the register |
| the landed integration head, i.e. **after** `r8-register` lands | rc=1, CONFLICT in the register |

INFERRED, and the mechanism is mechanical rather than speculative: before the landing, the target
register is `124dd74`, which sits near the fork's own ancestor, so git auto-merges disjoint
regions and the duplicate numbering slides in silently. After the landing, the target register is
`1c900e5`, which already contains the fork's content under reconciled item numbers, so the same
regions now differ and git raises a conflict instead.

**So landing `r8-register` early is itself the mitigation.** It converts a silent corruption into
a loud one. The silent window is open right now and closes the moment phase 2 completes, which is
why phase 2 is second and not last. This does not weaken `d7-register`'s finding, it makes it
actionable: the window they warned about exists, and they were describing the wrong end of it.

### 2.2 Why phases 3 and 5 are ordered as they are

Phase 3 is the four branches whose changes are disjoint from everything else (documentation,
licence text, tooling, poster figure generators). MEASURED: all four merge clean in any order
relative to each other. They go early because each one that lands is one fewer thing that can be
lost, and none of them can complicate a later merge.

Phase 5 is the `simulation/r5_physics/` lineage. `r8-kramer` and `r8-force` share 25 files through
their common base `777567a`. MEASURED: `r8-force` + `r8-kramer` is CLEAN pairwise, and both are
clean against the accumulated tree, because their shared files are shared **history**, not
divergent edits. `r8-kramer` goes first only because `r8-force` is the longer lineage and merging
the shorter one first makes the second merge's diff easier to read if something does go wrong.

---

## 3. The conflicts, named, with resolutions

**RETRACTED, 2026-08-19 18:20. This section previously opened: "There is exactly one conflicting
file across all fifteen branches." That is FALSE. There are five, across four merges.** The
sentence stayed wrong through two revisions because of a specific methodological hole, and the
hole is more useful than the correction:

> **The pairwise table below tests feature branch against feature branch. It never tests a
> feature branch against the integration target.** `.gitignore` conflicts between
> `claude/add-ci-checks` and `claude/r8-persistence`, which is not a pair this table contains,
> so no amount of re-running it could ever have surfaced it.

MEASURED, and this is what makes it an error rather than staleness: the `.gitignore` blob on
`add-ci-checks` is `e0531b98` at **every** tip the branch has had, `af62473`, `e0d2beb`,
`faf53d1` and `7a0d08a`, and the conflict fires at all four. It was there at 00:01, it was there
at 17:12, and both revisions asserted it was not.

```
git ls-tree <tip> -- .gitignore        # e0531b98 at all four tips, 131 lines
git merge-tree --write-tree <tip> claude/r8-persistence
# -> exit 1 at all four:  .gitignore  simulation/openchannel_bc.py
```

The five conflicting files, MEASURED against live tips at 18:53, **classified by mechanism,
because the two kinds need different handling and different verification.** The test is one
command per row, `git ls-tree $(git merge-base A B) -- <path>`: if the path is absent from the
merge base, git has no base blob and the conflict is add/add.

| # | file | merge (branch pair) | merge base | in base? | mechanism | resolution |
|---|---|---|---|---|---|---|
| 1 | `simulation/openchannel_bc.py` | `add-ci-checks` + `r8-bc-merge` | `1a868f3` | **ABSENT** | **add/add** | 3.1: take `61afb193` whole |
| 2 | `simulation/openchannel_bc.py` | `add-ci-checks` + `r8-persistence` | `1a868f3` | **ABSENT** | **add/add** | 3.1: keep `61afb193` whole |
| 3 | `.gitignore` | `add-ci-checks` + `r8-persistence` | `1a868f3` | present | **content** | 3.3: union, then assert `check-ignore` |
| 4 | `.claude/skills/research-corpus/SKILL.md` | `add-ci-checks` + `r9-corpus-bib` | `af62473` | present | **content** | 3.4: union, and fix 19 to 20 |
| 5a | `hf_space/README.md` | `add-ci-checks` + `r9-platform` | `af62473` | present | **content** | 3.5: hand-merge |
| 5b | `hf_space/app.py` | `add-ci-checks` + `r9-platform` | `af62473` | present | **content** | 3.5: take `r9-platform` whole |

`hf_space/arr_verdict.py` is ABSENT from the base too, but only one side adds it, so it is a
plain add and merges clean. **Add/add needs two sides adding, not one.**

### 3.0 The two mechanisms need different handling, and the difference is where the wrong answers hide

**Add/add (rows 1 and 2). Git has no base blob, so it cannot three-way merge at all.** It marks
the entire file. There is nothing it silently decided for you, and no per-hunk resolution is
meaningful because there is no common ancestor to attribute a hunk to. So:

- **Resolve by choosing a whole blob**, never by editing hunks together.
- **Verify by whole-blob containment**, which is what section 3.1 does: `grep -Fxv` in both
  directions establishes which version is a superset. There is no base to diff against, so
  containment is the only available proof.
- The failure mode is choosing the wrong blob, which is loud: the file is either right or it is
  visibly short.

**Content conflict (rows 3, 4, 5a, 5b). Git auto-merged every non-overlapping hunk and only
showed you the overlaps.** That is the dangerous kind, and it is dangerous in the opposite
direction:

- **The parts git did NOT ask about are the ones to check.** A content conflict means git already
  made decisions on your behalf everywhere the two sides did not textually collide, and those
  decisions are invisible in the conflict markers.
- **Verify against the BASE, not against either side.** `git diff <merge-base> <resolved>` shows
  everything that changed, including what was auto-merged. Diffing the resolution against either
  parent hides exactly the half that parent contributed silently.
- The failure mode is semantic rather than textual: two non-overlapping edits can both apply
  cleanly and still contradict each other, and git reports nothing.

**A claim I wrote here ten minutes ago, tested, and had refuted. Left in because the refutation is
the useful part.** I wrote: "row 4's 19-versus-20 pair sits in different, non-overlapping parts of
the file, so git will merge it without a marker and the result will state both numbers." **That is
FALSE.** MEASURED, by taking the actual conflicted tree from step 14 and asking, for every line
mentioning either number, whether it falls inside a conflict marker:

```
INSIDE-MARKERS  line  44  ## READ THIS FIRST: the index holds 8 of the project's 20 deep searches
INSIDE-MARKERS  line 535  ...The Undermind workspace holds **19 completed deep
INSIDE-MARKERS  line 546  The nineteen, with what each actually settles:
```

**All three are inside the markers. Git does surface this one**, because both sides happened to
rewrite overlapping regions. A human resolving step 14 will see 19 and 20 side by side, which is
the good case. I asserted a mechanism from its plausibility instead of running the one command
that decides it, in a document whose whole argument is that you must not do that.

**What survives, and it is stronger than what I claimed, because it is measured:**

```
merged SKILL.md: 639 lines, 322 inside conflict markers,
                 317 AUTO-MERGED AND NEVER SHOWN (49.6 percent)
```

**Half the merged file is decided for you and never appears in a conflict marker.** Line 3 is a
concrete instance: base and `add-ci-checks` both read "the project's 332-paper external research
index", `r9-corpus-bib` reads "external research index (332 records, 319 distinct works)", and git
silently takes the latter. That particular one is a legitimate one-sided edit rather than a
disagreement, which is exactly why it is a good illustration: **you cannot tell the legitimate
silent changes from the dangerous ones without looking, and the conflict markers will not show you
either.**

So the verification rule stands, for a general reason rather than the specific one I invented:
**diff the resolution against the merge base, not against either parent.** Against a parent you
see only what the other side contributed; against the base you see all 639 lines, including the
317 nobody was asked about.

That is the reason to classify at all. For add/add there is no silent half, because there is no
base; for a content conflict the silent half here is 49.6 percent.

The original pairwise table is retained below because it is still correct about what it tested,
and because keeping it makes the hole visible:

```
r8-persistence + r8-priorart    CLEAN
r8-persistence + r8-bc-merge    CONFLICT (add/add): simulation/openchannel_bc.py
r8-persistence + r8-force       CLEAN
r8-force       + r8-kramer      CLEAN
r8-priorart    + r8-bc-merge    CLEAN
r8-tooling     + r8-register    CLEAN
r8-tooling     + r8-naming      CLEAN
r8-register    + r8-naming      CLEAN
r8-licence     + r8-tooling     CLEAN
```

**Generalisable rule, and it is the reason to write this up rather than just fix it:** a
pairwise conflict matrix over N sources is not a conflict analysis of a landing. A landing is
N merges into a moving target, and the target is a source too. **Always include the integration
branch as a row.** The same shape as *reach* versus *cited*, and *lineage* versus *merges
cleanly* in 3.1a: two predicates that feel identical and are measured differently.

### 3.1 `simulation/openchannel_bc.py`, add/add, three lineages

The file was added independently on three lineages, which is why git sees add/add rather than a
content conflict: there is no common ancestor **for the file**, even though the contents are
related. MEASURED, `git log <branch> --diff-filter=A -- simulation/openchannel_bc.py`:

| lineage | added at | tip blob | lines |
|---|---|---|---|
| `claude/add-ci-checks` | `be1b138`, then 4 more commits | `70946f61` | 714 |
| `claude/r8-persistence` | `5ecf725`, one commit | `9a94e247` | 289 |
| `claude/r8-bc-merge` | `049f7e1`, one commit | `61afb193` | 981 |

**Resolution: take `claude/r8-bc-merge`'s blob `61afb193` verbatim. Do not hand-merge, do not take
the union, do not take the richer-looking hunks.**

The three versions are linear in content, not rival implementations. MEASURED two ways:

1. Set containment by line, `/usr/bin/grep -Fxv`: only **3** lines of the 289-line version are
   absent from the 714-line version, and all three are modified-in-place lines (a signature, an
   assignment, a self-test count message). Only **1** line of the 714-line version is absent from
   the 981-line version, the `__all__ = [...]` declaration, which the 981-line version **extends**
   onto a continuation line rather than dropping.
2. Symbol coverage. `RecyclingChannelBC` 6 / 10 / 14, `OverfallBC` 0 / 4 / 7, `ReservePool`
   0 / 5 / 8, `depth_profile` 5 / 5 / 11, `inject_len` 0 / 7 / 16, across the 289 / 714 / 981
   versions respectively. The 981-line version is a strict superset on every symbol.

This corroborates `d4-bcmerge`, READ from `docs/R8_OPENCHANNEL_BC_RECONCILE.md`, which reached the
same conclusion from a different direction (blob identity plus an independently recomputed
sha256 of the module bytes r7 actually ran) and recorded that the dispatch premise it was given,
that the file "was written TWICE, independently", was false. I did not use their blob-identity
argument; I used line containment and symbol counts, so this is a second origin and not the same
source cited twice.

MEASURED: applying this resolution and continuing, the entire remaining order merges clean.

### 3.1a The conflict is real. Content ancestry does not prevent it, and the two are independent

`docs/R9_DISCREPANCY_REGISTER_2026-08-19.md` row **C1** states that the hashes show the short
copy is "a strict ancestor state ... not a rival lineage", and concludes that the add/add
conflict "is refuted" and that a resolution should not be planned for it.

**The premise is correct and I agree with it. The conclusion about git is wrong, and keeping the
resolution matters, because the conflict reproduces on demand.** These are two independent
propositions and only the first is about content:

1. **Is `9a94e247` a lineal ancestor state of the tip?** YES. C1 is right, d4-bcmerge is right,
   and section 3.1 above reaches the same answer by a third method. I never claimed rival
   lineages; section 3.1 says "linear in content, not rival implementations".
2. **Does merging the branches produce an add/add conflict?** YES. MEASURED, live, re-run against
   the current `claude/add-ci-checks` tip `e0d2beb` at 17:12 on 2026-08-19, `exit 1` for both
   `claude/r8-bc-merge` and `claude/r8-persistence`.

`add/add` is a statement about the **commit graph**, not about content. MEASURED, the mechanism
in two commands:

```
git -C <repo> merge-base claude/add-ci-checks claude/r8-bc-merge     # -> 1a868f3
git -C <repo> ls-tree 1a868f3 -- simulation/openchannel_bc.py        # -> 0 files, ABSENT
```

The path is absent from the merge base, so both sides **add** it, and git has **no base blob to
three-way-merge against**. Lineal content ancestry is invisible to git unless it is recorded in
the DAG, and here it is not: the two adds are `be1b138` and `049f7e1` on branches whose only
common ancestor predates both.

MEASURED, a minimal control that separates the two conditions (built in a scratch repo, both
arms distinguished so the result cannot be vacuous):

| both sides add the same path | blobs | merge-tree exit |
|---|---|---|
| identical content | `1275430f` = `1275430f` | **0, git resolves it cleanly** |
| differing content | differ | **1, add/add conflict** |

So add/add fires on exactly two conditions: the path is absent from the merge base, **and** the
two blobs differ. Neither condition is "the two contents are unrelated". A file can be in perfect
linear content ancestry and still conflict, which is precisely this case.

**Practical consequence: keep the resolution.** Deleting it because the lineage is linear would
send whoever executes the landing into a conflict they were told would not happen, on the one
file in eighteen branches that conflicts. The resolution is also *easier* because C1 is right:
since the contents are linear, "take `61afb193`" is provably lossless (section 3.1), which is
exactly what you cannot say when two lineages genuinely diverge.

### 3.2 The resolution trips the `pre-commit` hook, the one place needing a deliberate override

READ, `/Users/josie/can-it-ford/.git/hooks/pre-commit`:

```sh
n=$(git diff --cached --name-only | wc -l | tr -d " ")
if [ "$n" -gt 8 ]; then echo "REFUSING: $n files staged. Stage explicitly."; exit 1; fi
```

MEASURED: there is no `pre-merge-commit` hook in `.git/hooks/`, only `pre-commit` and `pre-push`.
That matters, because git invokes `pre-merge-commit` for an automatic merge commit and
`pre-commit` only when a conflicted merge is finished by hand. So:

- Every **clean** merge in section 2 bypasses the 8-file limit entirely, including the 31-file
  `r8-kramer` merge. No hook fires.
- The four **conflicted** merges are completed with `git commit`, which does fire `pre-commit`.
  MEASURED against live tips at 18:20, in the section 2 order:

  | conflicted merge | files staged | `pre-commit` |
  |---|---|---|
  | step 7 `r8-bc-merge` | 2 | passes |
  | step 8 `r8-persistence` | 12 | **REFUSES** |
  | step 14 `r9-corpus-bib` | 4 | passes |
  | step 19 `r9-platform` | 9 | **REFUSES** |

  **Two overrides are now needed, not one.** The staged count is order-dependent: merging
  `r8-persistence` straight into `add-ci-checks + origin/main` instead stages 21 files, not 12.
  Re-derive the count at the moment of the merge and read the list; do not carry a number from
  this table into a `--no-verify`.

The hook is doing its job: it exists because a shared working tree lets another session's staged
work ride along on a bare commit. Here the 13 files are all genuinely from the merge, so the
override is correct, but it must be **explicit and path-checked**, not habitual:

```
# after resolving simulation/openchannel_bc.py, and ONLY after reading the list:
git -C /Users/josie/can-it-ford diff --cached --name-only     # confirm all 13 are from r8-persistence
git -C /Users/josie/can-it-ford commit --no-verify            # the ONLY --no-verify in this plan
```

If that list contains anything not attributable to `claude/r8-persistence`, stop: another session
has staged work in the shared index, and committing would sweep it in. The same check applies
verbatim to step 19 `r9-platform`, the second override.

### 3.3 `.gitignore`, step 8, both sides appended to the same region

MEASURED, blob sizes about the merge base `1a868f3`:

| side | blob | lines |
|---|---|---|
| base `1a868f3` | `213172da` | 104 |
| `claude/add-ci-checks` | `e0531b98` | 131 |
| `claude/r8-persistence` | `fe6040b6` | 112 |

Both sides added lines to a file whose additions land at the end, so the regions overlap and git
cannot tell them apart. Five commits on `add-ci-checks` touched it (`46282bc`, `a677a59`,
`4dac5f0`, `be1b138`, `e2f985e`); one on `r8-persistence` did (`a6e534a`).

**Resolution: union, keeping both sets of added lines, then re-run the tracked-file census.**
This file is not ordinary. `CLAUDE.md`'s standing rules say twice, in two separate places, never
to cite `.gitignore` by line number because it is edited too often, and the walk-down carve-out
for `renders/yaris_render_s1/*` is the mechanism that decides which files the shell `grep`, and
therefore several audits, can see at all. A union merge is safe **only** if the carve-out's
ordering survives, because `.gitignore` is order-sensitive: a later broad rule re-ignores what an
earlier `!` exception un-ignored.

Verification to run after resolving, and it is a real test rather than an inspection:

```
git -C /Users/josie/can-it-ford check-ignore -v renders/yaris_render_s1/sim_standing.py   # expect: NOT ignored
git -C /Users/josie/can-it-ford check-ignore -v renders/yaris_render_s1/_incoming/sim_standing.py  # expect: ignored
git -C /Users/josie/can-it-ford check-ignore -v data/track1_sweep_v2/                     # expect: NOT ignored
```

If the first or third comes back ignored, the union re-ordered a rule and the resolution is
wrong. Those three are the cases `CLAUDE.md` names explicitly, so they are the ones a regression
would be quoted against.

### 3.4 `.claude/skills/research-corpus/SKILL.md`, step 14: the same defect fixed twice, and the two fixes disagree by one

This is the most interesting conflict in the set and the least mechanical. MEASURED, both sides
about the merge base `af62473`:

| side | commits touching the file | diff |
|---|---|---|
| `claude/add-ci-checks` | `faf53d1` (17:46) | +101 / -4 |
| `claude/r9-corpus-bib` | `8bad9b4`, `026f931`, `7647e6d`, `6ecf4e5` (through 17:35) | +262 / -15 |

`faf53d1` is titled "The research index never contained the project's own deep searches, and the
skill said so wrongly". `6ecf4e5` is titled "The builder cannot see 12 of the project's 20 deep
searches, and never could". **Those are the same finding, reached independently, eleven minutes
apart, and written into the same file on two branches.** The merge conflict is the symptom; the
duplicated work is the disease, and it is a coordination finding rather than a git one.

**Resolution: union, not take-one-side, and I checked rather than assumed.** MEASURED with the
same line-containment method section 3.1 used for `openchannel_bc.py`
(`/usr/bin/grep -Fxv` in both directions):

- `faf53d1` adds **75** lines relative to the base. **All 75 are absent from `r9-corpus-bib`.**
- `r9-corpus-bib` adds far more, and its additions are absent from `faf53d1`.

So neither side is a superset, and the openchannel resolution ("take the strict superset
verbatim") **does not transfer**. Taking `r9-corpus-bib` wholesale would drop the deep-search
table and the "DO NOT SAY 256 ARE CITED NOWHERE" retraction, which is itself a correction of a
published error.

**One number differs between the two sides and one of them is wrong.**

| side | claim |
|---|---|
| `claude/add-ci-checks`, `faf53d1` | "The Undermind workspace holds **19 completed deep searches**", then lists "The nineteen" |
| `claude/r9-corpus-bib`, `6ecf4e5` | "the index holds 8 of the project's **20** deep searches" |

MEASURED, live, by querying the workspace directly rather than by preferring an author:
`mcp__undermind__inspect_deep_searches(workspace_id='17299f2a-8dc8-438b-8c84-5abf19395e2c',
names=[], status_only=True)` returns **20 searches, all `completed`**.

**`20` is correct. `19` is wrong, and the mechanism is datable rather than a slip.** The twentieth,
`/moving vehicle floodwater simulation open source implementations`, was created **2026-08-19
16:29** and completed **16:31**. `faf53d1` was committed at **17:46**. So 19 was true when it was
measured and false by the time it was written, which is the same failure as section 0's `64`, in
a different file, on the same day.

**The dispatch that commissioned this slot also says "nineteen Undermind deep searches". That is
wrong too, for the same reason.** Whoever resolves this conflict should write 20 and give it a
timestamp, because it will be 21 soon enough.

Resolution, concretely: take `r9-corpus-bib`'s file as the base, graft `faf53d1`'s 75 added lines
into it, and change `19`/`nineteen` to `20`/`twenty` in the grafted block. `r9-corpus-bib` is the
base rather than the graft because its scope is this file and it is the larger, later-measured
side.

### 3.5 `hf_space/`, step 19: the decision was taken by execution, and the outcome was the safe option

**REVISION 4, 2026-08-19 18:55. Revision 3 set out options A, B and C and marked C "do not choose
without a deliberate decision". `d18-platform` then wrote to the public Space before reading that
row. I was told the overwrite had been executed. I checked the live public artifact rather than
relay it, and the report is wrong about the outcome:**

> **`d18-platform` executed option A, not option C. The AR&R joint-rule fix is LIVE, REACHABLE and
> WIRED on the public Space.** They resolved it themselves, correctly, by moving the rule into a
> new module.

MEASURED against the live public artifact, not against the repo:

```
curl -s https://huggingface.co/api/spaces/josiecerrell/can-it-ford
# private: False   sha e7a9ca9b   lastModified 2026-08-19T17:46:50Z
# siblings include:  app.py  arr_verdict.py  surface.py  speed_surface.py  data/...
```

| test | result |
|---|---|
| `AR_R` table in live `arr_verdict.py` identical to `origin/main`'s | **True** |
| `l1_verdict` body identical to `origin/main`'s | **True** |
| live `app.py` imports it | **yes**, line 20 `import arr_verdict as AV` |
| it is reachable from the UI | **yes**, `gr.Tab("AR&R verdict calculator")`, `AV.evaluate` wired to three inputs and `demo.load` |
| repo branch matches the live Space | **identical** on `app.py`, `arr_verdict.py`, `surface.py`, `speed_surface.py` |

The reachability test is the one that matters and is the one an inspection would skip. A module
that exists but is never imported is dead code, and the Space would then be d18's explorer with
the calculator silently gone. It is imported and wired, so it is not.

**Two claims here, and only one of them is true. Keep them apart:**

1. **"A published correctness fix was reverted on a public page."** **FALSE.** Tested five ways
   above. PR #11's joint rule is byte-identical and live.
2. **"A public write happened before the decision it needed was taken."** **TRUE**, and it is
   the finding. The write landed at 17:46:50Z; revision 3's board row naming the hazard was
   posted at 18:30. The right answer was reached, and it was not reached *by the process*. See
   section 5.5.

**Revised resolution, and it is now simpler than revision 3's.** The conflict at step 19 is still
live (`hf_space/README.md` and `hf_space/app.py`, both content conflicts, base `af62473`), because
phase 1 brings `origin/main`'s calculator `app.py` in and `r9-platform` replaced that file
wholesale. But the decision no longer has to be made at the conflict marker:

- **`hf_space/app.py`: take `claude/r9-platform`'s version whole.** MEASURED lossless on the
  physics by the containment method of section 3.1: of `origin/main`'s 125 lines, **20 are absent**
  from `r9-platform`'s `app.py` + `arr_verdict.py` combined, and **all 20 are superseded UI
  scaffolding**, the old top-level `gr.Blocks`, the sliders, the radio and their `.change`
  wiring, all reimplemented inside the calculator tab under `arr_depth` / `arr_vel` / `arr_class`
  / `AV.evaluate`. **Zero lines of `AR_R`, `l0_depth_threshold`, `l1_verdict`, `evaluate` or
  `_row` are lost.**
- **`hf_space/README.md`: hand-merge.** Both sides added; neither is a superset (all 22 of
  `origin/main`'s added lines are absent from `r9-platform`). This one still needs reading.
- **`hf_space/arr_verdict.py` merges clean**, one-sided add.

**Verify after resolving, and verify the claim rather than the file.** `origin/main`'s docstring
asserts parity with `vehicle_params.L1_verdict` and `gates.py:23`. That is testable and should be
tested, because a Space that disagrees with the repo is worse than no Space. I did not test it:
I established that the live rule is identical to the one `origin/main` shipped, which is a
different and weaker claim than that either is correct.

---

## 4. What must NOT be merged

### 4.1 `claude/fork-register-reconcile` must never be `git merge`d, at any point

This is the standing instruction. READ, `docs/R8_REGISTER_MERGE_2026-08-18.md` section 9.5 on
`claude/r8-register`. Its content has already been merged **by entry**, by hand, with a ruling on
a three-way item-id collision. MEASURED and this is the load-bearing fact:

```
git -C /Users/josie/can-it-ford merge-base --is-ancestor \
    claude/fork-register-reconcile claude/r8-register
# -> non-zero: NOT an ancestor
```

`claude/fork-register-reconcile` is **not** in `claude/r8-register`'s git history. The content is
there, the commits are not. So git has no way to know the merge already happened, and will
cheerfully offer to do it again. Before phase 2 completes it will do so **silently** (section
2.1). If anyone proposes that merge, the answer is that it has already been done, by entry, and
redoing it reintroduces duplicate item numbering.

### 4.2 Do not verify any of this by SHA pinned in a document, including this one

READ, same document, section 9.2, and it is emphatic that the procedure is the instruction and
the numbers are not:

> `claude/add-ci-checks` moved three times while this work was in progress: `59234f9`, `785650b`,
> `1aa4e19`. **All three times the register blob stayed `124dd74`**, so the merge base never
> actually moved. That is luck, not a guarantee, and it is the thing to check. Run the check
> against whatever the tip is when you land this, not against `1aa4e19`.

Both of its preconditions HOLD as of 00:01 on 2026-08-19. MEASURED, and note the `ls-tree` form,
which matters for the reason in section 9.2:

```
git -C /Users/josie/can-it-ford ls-tree claude/add-ci-checks \
    -- docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
# -> 124dd74...   MATCHES, this merge is still valid

git -C /Users/josie/can-it-ford rev-parse --short=7 claude/fork-register-reconcile
# -> c1235e5      unmoved since the merge was derived
```

**Re-run both immediately before phase 2.** If the first has moved, stop and re-derive the
register merge; do not resolve it by hand.

### 4.3 Nothing is merged into `main` until section 5's preconditions are answered

Four of them, and all four are Josie's decision, not a merge mechanic. See section 5.

---

## 5. Preconditions on any push, which are decisions and not obstacles to route around

The repo is **public**: `github.com/jcerrell-IS/can-it-ford`. A push is world-readable and
permanent, and GitHub has served removed blobs by SHA in this account before, so "we can take it
down" is not a mitigation.

### 5.1 The credential exposure is unrotated, and it gates pushing specifically

READ, `/Users/josie/can-it-ford/docs/CREDENTIAL_EXPOSURE_2026-08-13.md`, first line:

> **Status: OPEN. Rotation is a Josie action and has not been done.**

That document covers a plaintext `CLAUDE_CODE_OAUTH_TOKEN` in cluster shell startup files (Vista
`.bashrc` line 112, LS6 `.bashrc` lines 122 to 124, of which `sort -u` returns 2 distinct values
so at least two tokens are present and both need rotating). A broader surface, including an
active GitHub PAT, is recorded on `claude/credential-exposure-2026-08-13-DO-NOT-PUSH`.

**The relevant one for this plan is the GitHub PAT, because that is the credential a push
authenticates with.** Pushing before rotation puts a possibly-compromised credential to work
against a public repo. That is a decision, not a technical blocker, and it is stated here as a
precondition rather than assumed away.

Two verifications I did run, so the scope of the question is bounded rather than open-ended:

- MEASURED: `docs/CREDENTIAL_EXPOSURE_2026-08-13.md` is **untracked on all ten R8/CI heads**, and
  `git ls-files --error-unmatch` fails on it in the main checkout. It is correctly uncommitted.
- MEASURED: `claude/credential-exposure-2026-08-13-DO-NOT-PUSH` is **not on origin**
  (`git ls-remote --exit-code origin 'refs/heads/claude/credential-exposure*'` finds nothing).

### 5.2 The landing itself introduces no credential material, and I checked rather than assumed

This is the one part of the credential question I could settle, so I did.

MEASURED, over the **207 commits** in the landing range, not just the final tree, because a push
publishes history:

```
git -C <mirror> log --oneline -G'sk-ant-[A-Za-z0-9_-]{20,}'      simmain..<landed>   # 0
git -C <mirror> log --oneline -G'ghp_[A-Za-z0-9]{30,}'           simmain..<landed>   # 0
git -C <mirror> log --oneline -G'github_pat_[A-Za-z0-9_]{30,}'   simmain..<landed>   # 0
git -C <mirror> log --oneline -G'olp_[A-Za-z0-9]{20,}'           simmain..<landed>   # 0
git -C <mirror> log --oneline -G'AKIA[0-9A-Z]{16}'               simmain..<landed>   # 0
```

Zero on all five, in every commit of the range. MEASURED separately, of the **168 files the
landing newly adds**, zero contain even a bare credential prefix. The prefix strings that do
appear in the landed tree (`sk-ant-`, `ghp_`, `olp_` in `CLAUDE.md`, the register, and four audit
documents) are prose **about** tokens, carry no token body, and are already on `origin/main`.

No token value was printed, logged, or transmitted at any point in this check; every test was a
match-count or a filename list.

**Limitations of that check, stated so it is not over-read:** it scans text files only
(`grep -I` skips binaries), it tests the landing range and not the pre-existing public history,
and a credential that is not in one of those five shapes would not be caught. It is evidence that
the landing adds nothing, not a clean bill of health for the repository.

### 5.3 Two more open items that a push would make harder to walk back

Both are from the board, and both are already marked as needing a human.

**The poster on `origin/main` carries two false statements.** READ, `d8-naming`'s 22:5x board row:
`public_release/Cerrell_TACC_42x56.pdf`, blob `168879947da7d271e0c17da28f8719c46ee57a68`, as
committed on `origin/main`, in a public repo. Statement (A) is false only in the word
"bit-reproducible", which it inherited from a field name; its counts, its partition and its value
are all correct. Statement (B) is the Fig 2 caption "one hull at 1100 kg, all runs deterministic."
Drop-in replacement text and a standalone erratum exist in that slot's section 1.4. This is
already public and a push does not create it, but a landing is the natural moment to decide, and
the slot's own note applies: rebuilding locally does not unpublish what GitHub has served.

**The LICENSE carve-out is pending sign-off.** READ, `d10-licence`'s board rows: `LICENSE`,
`THIRD_PARTY_NOTICES.md` and `citations/README.md` are released by that slot but carry
"do not edit LICENSE while Josie's sign-off is pending", and the image exposure in `citations/` is
**four distinct third-party sources, 20 image files, 7,213,546 B**, of which the Smith, Modra and
Felder 2019 set (16 files, 6,215,623 B) is closed access. `claude/r8-licence` is in the merge set
at phase 3, so approving this plan approves landing that text.

### 5.4 Two commits at branch tips were authored by no session, and neither has been reviewed

MEASURED, `git log -1` and `git branch --contains` on each:

| commit | branch | position | files | change | authored |
|---|---|---|---|---|---|
| `98d4d9d` | `claude/r9-moving-vehicle` | **tip** | 4 | +493 / -9 | 2026-08-19 17:45:22 |
| `d55ac14` | `claude/r9-renders` | **tip** | 2 | +621 / -0 | 2026-08-19 17:45:22 |

Both are titled "RECOVERED from a crashed session", and `d55ac14`'s own subject ends **"the
Blender Cycles path, untested"**. They preserve work from the tmux-server crash rather than
representing a slot's reviewed output. `98d4d9d` touches `analysis/r9_speed_surface.py`,
`data/r9_speed_surface.tsv`, `docs/R9_MOVING_VEHICLE_2026-08-19.md` and
`simulation/moving_vehicle_channel.py`; `d55ac14` adds `analysis/cycles_render.py` and
`analysis/prep_cycles_scene.py`, 621 lines of new code by its author's own note untested.

**Precondition: both need their authoring slot's sign-off before the merge that carries them.**
They are at the tips, so merging `claude/r9-moving-vehicle` (step 17) or `claude/r9-renders`
(step 15) lands them and nothing in the merge makes that visible. Neither conflicts, which is
exactly why this needs to be a written precondition rather than something the merge will surface.

Concretely, before steps 15 and 17:

```
git -C /Users/josie/can-it-ford show --stat d55ac14
git -C /Users/josie/can-it-ford show --stat 98d4d9d
```

and ask `d17-moving` and `d13-renders` to confirm the content is theirs and is what they intended
to commit. If a slot cannot confirm, the fallback is to merge its branch at the commit *before*
the recovery commit (`056ba10` and `256d013` respectively), which loses nothing: the recovery
commits remain on the branch and in the bundle, reachable, and can be merged later.

**Do not treat "it is committed" as "it was reviewed".** Six other slots' tips are their own
authored work; these two are not, and the difference is invisible in `git log --oneline`.

### 5.5 Public writes: there are FIVE public surfaces, three were written today, and none of the writes had a decision attached

**This section exists because two public writes happened during this round without the decision
they needed being taken, and in both cases the write was discovered afterwards rather than
proposed beforehand.** Neither did harm. That is not the same as the process working.

**The inventory is five surfaces, not the two that have been named.** MEASURED live 2026-08-19
18:57 against the Hugging Face API and `git ls-remote`, not from any summary:

| # | surface | visibility | last written | state |
|---|---|---|---|---|
| 1 | `github.com/jcerrell-IS/can-it-ford` | **PUBLIC** | `c7f0a16`, 2026-08-17 | 46 remote heads |
| 2 | Space `josiecerrell/can-it-ford` | **PUBLIC** | **2026-08-19T17:46:50Z** | app replaced, section 3.5 |
| 3 | dataset `josiecerrell/can-it-ford-sweep-v1` | **PUBLIC** | **2026-08-19T17:33:22Z** | EMPTY: `.gitattributes` + README only |
| 4 | dataset `josiecerrell/can-it-ford-speed-surface` | **PUBLIC** | **2026-08-19T17:48:29Z** | 4 CSVs of real data |
| 5 | model `josiecerrell/can-it-ford-sweep-v1` | **PUBLIC** | unstamped | **36 timeseries CSVs + manifest, README 15 bytes** |

Surface 5 has not been named by anyone this round and is the one I would look at first.
MEASURED, by parsing its live `manifest.csv`:

- **36 rows, three vehicle classes**: sedan 12, suv 12, pickup 12, at `target_length_m` 4.6 / 4.8
  / 5.5.
- **`n_grid` is 64 on all 36 rows**, presented as a single column with no other resolution field.
  `CLAUDE.md` records that `grid_lim` is taken from the loaded hull's extent, so a fixed `n_grid`
  across different vehicle lengths is **not** a fixed `dx` and **not** a fixed realised depth.
  A reader of this manifest has no way to know that, and the column invites exactly the reading
  the project has already ruled out.
- **`density_plausible` is `False` on all 36 rows**, densities 306.51 to 482.61 kg/m3.
- **The README is 15 bytes.** There is no provenance, no licence, no caveat, and nothing that
  says what `density_plausible: False` means to someone who did not write it.

I am not claiming these runs are wrong. I am claiming a public artifact is serving a
cross-vehicle sweep with a resolution column that cannot be read at face value, a plausibility
flag that is False everywhere, and no README to say either thing. **That is a publication, and
nobody decided to make it.**

### 5.5a What a deliberate decision looks like

Not a checklist for its own sake. Each item is here because something in this round would have
been caught by it.

1. **Name the surface and its visibility before writing, by querying it, not by recalling it.**
   Surface 3 was described this round as "a public empty dataset nobody has mentioned"; surfaces
   4 and 5 were not mentioned at all, and 5 is the one carrying data. `curl -s
   https://huggingface.co/api/{models,datasets,spaces}?author=josiecerrell` takes one second.
2. **Say what a reader could conclude that is false.** Not "is it correct" but "what will someone
   who did not write this take away". Surface 5's `n_grid` column fails this and its numbers are
   all individually true.
3. **State what the write would overwrite, and check it.** Section 3.5's whole risk was that
   replacing `app.py` might drop PR #11's joint rule. The test is five commands and takes under a
   minute: is the rule present, is it identical, is the module imported, is it reachable from the
   UI, does the repo match what is live. **Reachability is the one that gets skipped**, and a
   module that exists but is never imported is dead code.
4. **Write it down before, not after.** The write at 17:46:50Z was correct. The board row naming
   the hazard was posted at 18:30. Correct-then-documented and documented-then-correct look
   identical in the artifact and are completely different processes, and only one of them is
   repeatable.
5. **Assume it is permanent.** `CLAUDE.md` records that GitHub served a removed credential blob by
   SHA even after the scrub that was supposed to remove it. Deleting a public HF repo does not
   unpublish what was already fetched. So the reversibility question is not "can I take it down",
   it is "am I willing for this to be the permanent record".
6. **A licence question that is open blocks a DATA write specifically.** Register E8's question
   about the derived hull is unresolved. Surface 5 carries derived run data behind a 15-byte
   README; surface 4 carries four CSVs. Neither states a licence.

**Applied to this plan:** the landing itself writes to surface 1 only, and section 5.1's rotation
question gates it. Sections 3.5 and 5.5 concern surfaces 2 to 5, which the landing does not touch,
**except for one thing.** `sync-to-hub.yml` is already on `origin/main` and syncs `hf_space/` to
surface 2 on a merge into `main`. **So landing this plan and updating the remote WILL write to a
public surface as a side effect, with nobody typing an `hf` command.** That is precondition zero
for step 8 of section 9.4, and it is not currently in section 5.1.

---

## 6. The CI question: it already runs, and it goes green while a check inside it fails

### 6.1 RETRACTED: it does NOT "run nowhere". It has run seven times, all green

**This subsection previously read "It runs nowhere today, confirmed" and concluded that the only
thing needed was for the file to reach `origin`. The premise was right and the conclusion was
wrong.** So is the identical claim printed by `scripts/orient_live.sh` at every session start, and
the one in the dispatch that commissioned this document.

The premise, still true, MEASURED 2026-08-19 18:16:

```
git -C /Users/josie/can-it-ford ls-tree -r --name-only origin/main -- .github/workflows/
# -> csv-check.yml, physics-consistency-review.yml, sync-to-hub.yml
# canford-checks.yml is ABSENT from origin/main
```

The conclusion, false, MEASURED:

```
gh run list --repo jcerrell-IS/can-it-ford --limit 20
```

| run id | branch | event | when (UTC) | result |
|---|---|---|---|---|
| `32278287331` | `claude/add-ci-checks` | push | 2026-08-19T16:51:19Z | success, 43s |
| `32184701961` | `claude/add-ci-checks` | push | 2026-08-18T20:52:36Z | success, 1m43s |
| `32101688862` | `claude/r5-research` | push | 2026-08-18T05:07:48Z | success |
| `32101687314` | `claude/r5-physics` | push | 2026-08-18T05:07:47Z | success |
| `32101687242` | `claude/r5-safekeeping` | push | 2026-08-18T05:07:47Z | success |
| `32101686913` | `claude/add-ci-checks` | push | 2026-08-18T05:07:47Z | success |
| `32101686894` | `claude/r5-exposure` | push | 2026-08-18T05:07:47Z | success |

**Seven is the complete history, not the first page.** The table above came from
`gh run list --limit 20`, which could have truncated. Re-derived with an explicit workflow filter,
`gh run list --workflow canford-checks.yml --limit 100` returns exactly **7 rows**, all `success`.
Stated because a count taken off a paginated listing is the kind of number this document keeps
catching elsewhere.

**Mechanism, READ from the workflow itself:** the trigger is a bare `on: push:` with **no branch
filter**, so GitHub runs it from whatever branch was pushed, and `canford-checks.yml` is present
on every branch cut from `add-ci-checks`. Section 0a establishes that `add-ci-checks` reached
`origin` on 2026-08-18 06:07.

**"Absent from `origin/main`" and "runs nowhere" are different claims and only the first is
true.** The error is the same shape as *reach* versus *cited* and *lineage* versus *merges
cleanly*: a true measurement carried one step too far into a conclusion nobody re-derived.

**What actually changes when it lands on `main`:** it starts gating `main` and pull requests
against `main`, and it starts appearing as a status check on PRs. Those are the things it does
not do today. That is a smaller change than "turning CI on", and it is worth saying plainly
because the plan was about to claim credit for switching something on that has been on for two
days.

### 6.1a A green run is not a passing check, and this one proves it

**MEASURED from the real CI log, not a simulation.** `gh run view 32278287331 --log`:

| step | API `conclusion` | what the log actually says |
|---|---|---|
| `params_check` | success | exit 0, 11 warnings |
| `register_integrity` | success | exit 0, 52 warnings |
| `count_claims` | **success** | **25 `BLOCK` lines and `##[error]Process completed with exit code 1`** |
| `stationarity` self-test | success | exit 0 |
| `research_index --stats` | success | exit 0 |
| physics gates | success | exit 0 |

**`gh run view --json jobs` reports `conclusion: success` for a step that exited 1.** That is
what `continue-on-error: true` does, and it means the step-conclusion field cannot distinguish
"passed" from "failed and was masked". **Only the log can.** Anyone auditing this workflow from
the API alone will get a clean bill of health for a check that fails on every single run.

This is the "a check that cannot fail is not a check" family the project has logged before, and
it is the reason section 6.3 item 1 is the highest-value change in this plan.

### 6.2 What it does, simulated in revision 2 and since CONFIRMED against the real run

**Revision 2 wrote this subsection from a local `git archive` simulation, before knowing the
workflow had ever executed. Section 6.1a has now compared it against the real GitHub log. It
holds, including the specific number.** The simulation predicted `count_claims` exit 1 with **25
blocking defects**, masked; the CI log shows 25 `BLOCK` lines and exit 1, masked. Those are two
separate origins, a macOS Python 3.14 export and an Ubuntu Python 3.11 runner, so this is
corroboration rather than one source cited twice. The rest of the subsection stands as written.

READ, the workflow: six steps, `on: push` and `on: pull_request`, `ubuntu-latest`,
`actions/setup-python@v5` at 3.11, **no dependency install step at all**.

The absence of a `pip install` looked like the obvious first failure. It is not. MEASURED: none of
the six scripts imports numpy, scipy or matplotlib anywhere, all six are tracked, and
`params_check.py`'s local import `physics_gates_literature` is tracked beside it at
`.claude/checks/physics_gates_literature.py`, so it resolves. The workflow is pure standard
library.

So I ran it. A GitHub checkout contains **tracked files only**, so the faithful simulation is a
`git archive` export, which is what I used (940 files from `claude/add-ci-checks`, 1019 from the
simulated landed tree). Each step was run with `env -C <export>` so no `cd` was needed.

Against the **landed** tree:

| step | exit | `continue-on-error` | effect on the job |
|---|---|---|---|
| `params_check` | 0 | no | pass, with 4 warnings |
| `register_integrity` | 0 | yes | pass, 0 blocking defects |
| `count_claims` | **1** | **yes** | **fails, and is masked** |
| `stationarity` self-test | 0 | no | pass, 0 failures |
| `research_index --stats` | 0 | no | pass |
| `test_physics_gates` | 0 | no | pass, **5 skips** |

**The job goes green on its first run.** That is the answer, and it is worth two caveats, because
a green check on this workflow would be substantially hollow.

**Caveat 1: `count_claims` genuinely fails and the failure is masked.** It exits 1 with **25
blocking defects**. Running the identical script in the full working tree gives **0 blocking
defects and exit 0**. MEASURED both ways. The cause is visibility: the check counts
`DRIFT_THRESHOLD` declaration sites, and several declaration-site files are untracked, so a
tracked-only checkout cannot see them. The totals it computes drop from **22/23/24** (full tree)
to **16/17** (CI view), and 22/23/24 is precisely the band `CLAUDE.md` item 13 tells it to accept.
**In CI the check is measuring a different population and grading it against the wrong band.**
`continue-on-error: true` hides that. The `continue-on-error` is currently justified in a comment
as "accepts 22/23/24 by scope", which is true of the local run and false of the CI run.

**Caveat 2: the physics gates run mostly hollow, and say so themselves.** `test_physics_gates.py`
passes with 5 skips and prints "SKIPS ARE NOT PASSES", listing: no g48 triple, no mass-paired
runs, no grid-paired runs, no `rollout.npz` under `renders/`, no solver Poiseuille profile.
MEASURED, those inputs are not in the repository: `rollout.npz` is tracked **0** times,
`tests/data/poiseuille_profile.csv` **0** times, and `renders/yaris_render_s1/` has **2** tracked
files. The data is gitignored, so no amount of CI configuration fixes this. A green
`canford-checks` badge would mean the five stdlib checks ran, not that the physics gates were
exercised.

**Caveat on my own simulation, stated because it is a real difference:** I ran Python 3.14.6 on
macOS; CI would run 3.11 on Ubuntu. Both could change a result. What the simulation reproduces
faithfully is the dominant factor, tracked-files-only visibility, and that is what produced both
caveats above.

### 6.2a Reframed: the goal is not "make CI execute", it is "make CI able to fail"

**The round's framing of this item was "the CI is not on main, so make it run". That framing is
retired.** It runs. It has run seven times. The correct framing, and it inverts the priority:

> **`canford-checks` is an instrument that reports success without being able to fail.** One of
> its six checks exits 1 on every run and is masked; two more carry `continue-on-error` and could
> fail the same way tomorrow without anyone noticing. Half the workflow cannot return a negative.

**That is worse than never having run**, and the reason is specific rather than rhetorical: a
workflow that has never run supplies no assurance and everyone knows it. This one has supplied
**false assurance for two days**, and it is the kind that is quoted. It sits behind a green tick
on a public repository.

This is the same failure the project has logged before under "a comparison where both arms failed
and the empty results matched, so the check printed a clean PASS". The general form is:

> **A check must be able to distinguish "passed" from "could not evaluate" and from "failed but
> was ignored". If it cannot, its green result is not evidence.**

`continue-on-error: true` converts a check into exactly that. And section 6.1a establishes it is
worse than it looks: the GitHub API reports `conclusion: success` for the masked step, so the
degradation is invisible to every consumer except someone reading the raw log.

**Priority consequence for whoever owns CI:** landing `canford-checks.yml` on `main` without
section 6.3 item 1 does not turn CI on, it extends a broken instrument's reach from six branches
to the trunk and to every pull request. **Item 1 should land with it or before it, not after.**

### 6.3 Three changes worth making before it lands, none of them blocking

1. **Fix `count_claims` in CI, and the fix is a third scope axis, not a threshold tweak.** This is
   the highest-value change in this plan, because today the workflow's green tick is evidence for
   a proposition nobody tested (section 6.1a).

   MEASURED, the cause, by enumerating every declaration site and asking git whether each is
   tracked (`/usr/bin/grep -rn --include='*.py'` for the five names, excluding `.git/`,
   `third_party/`, `.claude/worktrees/`, `__pycache__` and `.bak*`, then
   `git ls-files --error-unmatch` on each hit):

   **24 sites in the working tree: 17 TRACKED, 7 UNTRACKED.**

   The 7 invisible to CI are `renders/yaris_render_s1/gates.py`, `gates_all_runs.py` and
   `gates_both_scenarios.py`; the three duplicated
   `deliverables/.../make_poster_figures_accessible.py` copies; and
   `docs/session_notes/archive/mu_sweep_recovered_from_staging.py`. The first three are exactly
   the files `CLAUDE.md` item 13 warns are "un-ignored but still UNTRACKED", so this is that
   documented trap arriving through a new door.

   Local run: totals **22/23/24**, 0 blocking defects, exit 0. CI run: totals **16/17**, 25
   blocking defects, exit 1. **17 tracked sites is exactly what CI's 16/17 band reflects.** The
   check is measuring a different population and grading it against `CLAUDE.md` item 13's
   working-tree band.

   `CLAUDE.md` item 13 says the total is scope-sensitive and names **two** binary choices
   (archive in or out, `gp_surrogate`'s CLI default in or out), giving four defensible totals.
   **There is a third: tracked-only versus whole working tree.** That makes eight, and the
   tracked-only pair is 16/17. Item 13 does not currently contain them, which is why CI cannot
   pass. Two acceptable fixes, and the choice belongs to whoever owns item 13, not to this plan:

   - teach `count_claims_check.py` to detect a tracked-only tree and accept 16/17 there, or
   - have CI run it with an explicit `--scope tracked` and add 16/17 to item 13's table.

   Either way, **drop `continue-on-error` afterwards.** Leaving it masks the next real failure
   too. Do not simply widen the accepted band to include 16/17 unconditionally: that would let a
   genuine loss of six declaration sites pass silently in the full tree, which is the exact
   defect the check exists to catch.
2. `on: push` has no branch filter. With 102 local branches, if a batch of them is ever pushed,
   this fires once per branch per push, plus again for any pull request. Consider
   `on: push: branches: [main]` plus `pull_request`.
3. `.claude/tooling/MERGE_github_workflow.yml` arrives with `claude/r8-tooling` in phase 3. It is a
   template intended to be merged into the workflow. Decide whether it supersedes
   `canford-checks.yml` before landing both, or you will land two overlapping answers to the same
   question.

---

## 7. The bundle: independently restore-tested at 18:19, and stale on two heads by 18:21

**REVISION 3, and the coordinator's update 3 reproduces.** MEASURED rather than accepted:
`/Users/josie/can-it-ford-bundles/2026-08-19/R9-post-crash-1748-FINAL.bundle`, **493,971,980 B**,
mtime 2026-08-19 17:45.

```
git -C /Users/josie/can-it-ford bundle verify <bundle>   # "The bundle records a complete history"
git -C /Users/josie/can-it-ford bundle list-heads <bundle> | wc -l    # -> 19
git clone --mirror <bundle> <scratch>                    # virgin clone, no reference to the repo
git -C <scratch> fsck                                    # rc 0
```

**19 heads, all 19 restored at exactly the listed SHAs** (`diff` of the bundle listing against
`for-each-ref` on the restored mirror: identical). `fsck` clean. Both recovery commits from
section 5.4, `98d4d9d` and `d55ac14`, are present and readable from the restored clone. So update
3's claim holds on every part I could test.

**Two caveats the restore test surfaced that the claim does not carry.**

**(a) The bundle contains no `main`.** `fsck` on the restored mirror emits "HEAD points to an
unborn branch (main)", and all 19 refs are `claude/*`. Restoring from this bundle alone gives you
the wave and not the trunk. That is acceptable because `main` is on GitHub, but it means this
bundle is not a whole-project backup and should not be described as one.

**(b) It went stale on two heads within two minutes of my checking it**, MEASURED at 18:21:

```
add-ci-checks: bundle e0d2beb -> live 7a0d08a,  2 commits NOT in bundle
r9-priorcode:  bundle a863ee7 -> live 0a83b75,  2 commits NOT in bundle
```

`r9-priorcode` moved twice during this revision. One of the two uncaptured `add-ci-checks`
commits is `7a0d08a`, the register C1 correction, which is a retraction: the same preferential
loss of the newest work described below.

**The superseded revision-2 text is retained for the record:**
`/Users/josie/can-it-ford-bundles/2026-08-18/R8R9-all-heads-2350.bundle`, 493,615,746 B,
mtime 23:41, "complete history", **16 refs**, restore-tested at 23:50 with all 16 matching.

`origin/main` (`c7f0a16`) and all five PR commits are present as objects inside it, reachable via
`claude/r8-licence`, which is the only branch in the set that contains `origin/main`. So the
bundle can reconstruct the merge target as well as the sources.

**Two limits, and both matter.**

**It is on the same disk as the repo.** `/Users/josie/can-it-ford-bundles/` is a sibling of
`/Users/josie/can-it-ford`. It is protection against a bad merge, a bad rebase or a deleted
branch. It is not protection against disk loss, and it is not a remote. The problem this plan
exists to solve is not solved by it.

**It goes stale in minutes, and it did.** MEASURED at 00:01, ten minutes after the restore test:

```
claude/r9-corpus-bib   af62473 != 59c12b2   *** STALE, 1 uncaptured ***
```

`d14-corpusbib` committed `59c12b2` ("The corpus never ingested them, and the DOIs were in a field
nobody joined on") at 23:58. **Re-verify the bundle immediately before relying on it, using the
script in section 9.1. Never re-use a bundle-verification result from earlier in a session,
including this one.**

This is not hypothetical for this document. The bundle named in my own dispatch,
`R8-nine-slots-2245.bundle`, did not exist (the file is `...-2244.bundle`), and when checked it
was stale on 3 of its 10 heads with 7 commits uncaptured. The two uncaptured research commits were
`b6fe951` and `ec968e6`, which are precisely `d9-kramer`'s withdrawal of the Job B placement and
`d3-force`'s overturning of its own settle result. **A restore from that bundle would have
resurrected two claims their own authors had retracted.** That is the specific failure mode a
stale backup produces here: it does not lose work at random, it preferentially loses the newest
work, and the newest work in this project is disproportionately corrections.

---

## 8. Reading the board: later rows retract earlier ones

`/Users/josie/can-it-ford/.claude/state/r8_board.md`, 132 lines, 92,650 B, 87 rows across 10
posters. It is append-only, so a refuted claim is never edited out, it is only followed by a
correction further down. **Grep it and you will land on the refuted text first.** MEASURED, rows
carrying retraction language:

- `d9-kramer` 23:14 explicitly retracts its own 22:31 and 22:44 rows, naming the exact phrases
  ("outlier", "15.4x") so a search finds the pointer. The Job B placement is withdrawn.
- `d3-force` 23:12 corrects its own 23:02 row: the no-forcing control is clean **in surge only**;
  in the vertical channel essentially 100 percent of the resolution effect survives.
- `d3-force` 23:24 overturns its own `70f0eea` headline (93.7 percent reduction becomes 77.7
  percent), and 23:31 supersedes 23:24 in turn.
- The coordinator issued corrections to two dispatch premises (`d4-bcmerge`'s and `d5-priorart`'s)
  after the slots raised them, and one to its own 21:40 row.
- `d2-persist`, `d10-licence` and `d4-bcmerge` each self-corrected a row.

For a landing this matters in one concrete way: **the branch tips are correct and the board's
early rows are not.** Every retraction listed above is committed on its branch. Merging the tips
lands the corrected state. Reading the board top-down and stopping early does not.

---

## 9. Executable procedure

### 9.1 Re-derive everything before starting. Do not trust section 1, or section 2, or this one.

**The merge set is a rate, not a list.** During revision 3 alone, `claude/r9-priorcode` moved
twice, once between two consecutive commands of mine, and `claude/add-ci-checks` gained a commit
while I was measuring it. **Never type a branch name or a SHA out of this document into a merge
command.** Everything below discovers the set by pattern and reads its tips at the moment of use.

```bash
R=/Users/josie/can-it-ford

# 1. DISCOVER the set by pattern. Do not maintain a list; the list is what goes stale.
#    This is the definition of "the wave": add-ci-checks plus every r8-* and r9-* branch.
git -C $R for-each-ref --format='%(refname:short)' \
    'refs/heads/claude/r8-*' 'refs/heads/claude/r9-*' 'refs/heads/claude/add-ci-checks' \
    | sort > /tmp/wave.txt
wc -l < /tmp/wave.txt          # revision 3 measured 19. If this is not 19, the set MOVED.

# 2. Tips and BOTH halves of the count, for everything discovered in step 1.
while read b; do
  printf '%-30s %-9s %s\n' "$b" \
    "$(git -C $R rev-parse --short $b)" \
    "$(git -C $R rev-list --left-right --count origin/main...$b)"   # behind <TAB> ahead
done < /tmp/wave.txt

# 3. Push state, LIVE. The cached refs/remotes/ copies are stale by construction:
#    they are the clone's own record of what it last saw, not what the remote holds.
git -C $R ls-remote --heads origin | wc -l
while read b; do
  r=$(git -C $R ls-remote --heads origin "refs/heads/$b" | cut -f1)
  printf '%-30s local %s remote %s\n' "$b" \
    "$(git -C $R rev-parse --short $b)" "${r:0:7}"
done < /tmp/wave.txt

# 4. Bundle freshness, against the set discovered in step 1 rather than against the bundle.
#    A bundle can be complete and still be missing the branch that matters.
B=$(ls -t /Users/josie/can-it-ford-bundles/*/*.bundle | head -1)
git -C $R bundle list-heads "$B" | while read sha ref; do
  b=${ref#refs/heads/}; live=$(git -C $R rev-parse $b 2>/dev/null)
  n=$(git -C $R rev-list --count $sha..$live 2>/dev/null)
  [ "${n:-0}" -gt 0 ] && echo "STALE $b: $n commit(s) not in bundle"
done
# and separately: is any branch from step 1 ABSENT from the bundle entirely?
comm -23 /tmp/wave.txt <(git -C $R bundle list-heads "$B" | sed 's|.*refs/heads/||' | sort)
```

Step 4's second half is the one people skip. Revision 2's bundle listed 16 refs against a set of
19; comparing the bundle to itself says "complete history" and comparing restored heads to listed
heads says "all matched". **Neither of those detects a branch the bundle never contained.** Only
the `comm` against an independently discovered set does.

### 9.2 Verification rules, which are the part most likely to be got wrong

**BINDING RULE FOR WHOEVER EXECUTES THIS LANDING: a check that cannot tell "equal" from "could
not evaluate" is worse than no check, and must not be used to gate a merge.** This is not an
anecdote. It was the dominant failure mode of the night, and it is a property of the shell rather
than of anyone's care.

Six instances in one session, five of them zsh's handling of unquoted or specially-named
variables, and every one returned a confident answer:

| # | what was run | what it returned | why it was wrong |
|---|---|---|---|
| 1 | `set -- $pair` in my bundle comparison | clean `IN BUNDLE` for all ten heads | zsh does not word-split; both sides were EMPTY, and empty equalled empty |
| 2 | `git bundle create "$BUN" $REFS` | git rejected it | same property: sixteen ref names passed as ONE argument. Loud only by luck |
| 3 | `while IFS= read -r h path` | every external command "not found" | zsh ties `path` to `$PATH`; builtins kept working, so it read as a tool problem |
| 4 | `grep -rln ... --include=*.py` unquoted | **0 hits** | zsh tried to glob `--include=*.py`, the command failed, and a false zero is indistinguishable from a true zero |
| 5 | `pgrep -f round5_autodispatch` | a match | it matched a Claude session whose prompt quoted the script name. Blocked a whole launch wave |
| 6 | my add/add control, first attempt | `1` on **both** arms | the branch name did not exist under `git init -b base`. Caught only because uniform arms are suspicious |

Instance 6 is mine and it happened **while writing section 3.1a**, which is the strongest argument
for making this binding: I was actively hunting this failure mode, had already written it up once,
and still produced it. What caught it was not care, it was that **agreement between arms that are
supposed to differ is itself a signal**. The rebuilt harness printed
`SEPARATED: identical=0 (clean), differing=1 (conflict)` instead of a bare comparison, so a broken
run could not masquerade as a result.

There is a second, subtler form worth naming because a merge verification is full of it: a
**passing check on quantity A is not evidence about quantity B**. `d9-kramer` recorded this at
23:06 after a self-test that correctly reproduced one constant was cited as confirming a claim
that used a different one, and their note is exact, that a correct calculation attached to the
wrong claim "does not merely fail to support it, it LAUNDERS it". Verifying that a branch merged
cleanly is not evidence that it merged the tip you intended; that is what `HEAD^2` below is for.

Every comparison in a merge verification must therefore carry an explicit third outcome, and any
uniform result across arms that should differ must be treated as a harness fault until proven
otherwise:

```bash
if [ -z "$expected" ] || [ -z "$actual" ]; then
  echo "CANNOT EVALUATE (expected=${expected:-EMPTY} actual=${actual:-EMPTY})"   # NOT a pass
elif [ "$expected" = "$actual" ]; then echo "MATCH"
else echo "DIFFER"; fi
```

**Do not read a blob with `$rev:path` in this shell.** MEASURED, it bit me mid-session:
`git rev-parse "$b:$f"` returned the literal string `claude/r8-` for several branches instead of a
blob hash, because zsh applies a history-style modifier keyed on the path's first letter. Use
`git ls-tree <rev> -- <path>`, which is immune.

**Verify the register by entry, never by line count.** READ, `d7-register` section 9.3: a
concatenation that returns exactly the expected size would contain two item 17s and pass a size
check. After phase 2 the register must show **210 entries** (166 letter-ids, 44 numbered),
numbered ids contiguous 1 to 44 with no duplicates, and `register_integrity.py` with an explicit
`--register` path reporting 0 blocking defects.

**Verify what was actually merged with `git rev-parse HEAD^2`**, which names the second parent,
that is, the tip the merge actually consumed. Compare it against the tip you re-derived a moment
earlier, not against any SHA written in a document:

```bash
tip=$(git -C $R rev-parse claude/r8-register)            # re-derive NOW
# ... perform the merge ...
merged=$(git -C $R rev-parse HEAD^2)
[ "$tip" = "$merged" ] && echo MATCH || echo "DIFFER: merged $merged, expected $tip"
```

### 9.3 The dry run, which touches nothing and should be re-run before executing

The whole order in section 2 was simulated with `git merge-tree --write-tree`, which writes no
ref, no index and no working tree, chained inside a throwaway mirror clone. Re-run it after
re-deriving tips; if any branch that was CLEAN comes back CONFLICT, the plan's order is stale and
section 3 needs redoing before anything is merged. **In revision 3 exactly that happened: two
branches that were CLEAN at 17:12 came back CONFLICT at 18:20.** Scripts are in the session
scratchpad: `verify_bundle.sh`, `simfinal.sh` (revisions 1 and 2), `simrun.sh` and `simres.sh`
(revision 3).

The revision-3 script differs from its predecessors in one way that matters, and the difference
is the reason it found three conflicts they missed:

- Build the throwaway with `git clone --mirror --local <repo> <scratch>`. Hardlinked, seconds,
  and it isolates the simulation from the shared repository completely.
- Seed the chain at `claude/add-ci-checks`, merge `origin/main` FIRST, then each branch in order,
  carrying the result forward with `git commit-tree` so every step merges into the accumulated
  tree rather than into the base. **A per-branch simulation against the base is not a simulation
  of a landing.**
- **Apply section 3.1's resolution at step 7 before continuing.** Without it, step 7's unresolved
  `openchannel_bc.py` conflict propagates and every later conflict report is contaminated. This
  is what separates a real new conflict from a carried-forward one, and without it `.gitignore`
  at step 8 is indistinguishable from noise.

### 9.4 Order of operations on the day

1. Re-derive the set and tips (9.1, all four steps). Re-verify the bundle (9.1 step 4). Re-run
   the dry run (9.3).
2. Answer the **five** preconditions in section 5. **Rotation is the one that gates pushing.**
   Section 5.4's recovery-commit sign-off is the one that gates steps 15 and 17 specifically, and
   it is the only precondition no merge will surface on its own.
3. Decide section 3.5 before starting. It is a product decision about a public page and it should
   not be made at 2am with a conflict marker on screen.
4. Steps 1 to 19 locally, on `claude/add-ci-checks`, verifying each merge with `HEAD^2` (9.2).
5. **Four merges stop for a human**, not one: steps 7, 8, 14 and 19. **Two need
   `commit --no-verify`**, steps 8 and 19, and only after reading the staged list (3.2). Re-derive
   the staged count at the merge; it is order-dependent.
6. Verify the register by entry (9.2). Run the six CI checks locally against a `git archive`
   export, not against the working tree, or you will get the full-tree answer and not the CI one
   (6.2). Expect `count_claims` to exit 1 until section 6.3 item 1 is done; that is the known
   state, not a new failure.
7. Merge `claude/add-ci-checks` into `main` locally.
8. **Stop. Pushing is a separate authorisation** and requires `PUSH_OK=1`, an answered rotation
   question, and confirmation afterwards that the remote actually moved (`git ls-remote origin`),
   because a command exiting 0 is not evidence the remote updated.
9. After the push, **read the CI log, not the badge** (6.1a). A green `canford-checks` is
   compatible with `count_claims` exiting 1.

---

## 10. What I could not verify

- **That any of this succeeds when executed.** Every merge result is `merge-tree`, which is the
  same algorithm `git merge` uses but does not exercise hooks, the working tree, or the index. The
  `pre-commit` prediction in 3.2 is INFERRED from reading the hook and from git's documented rule
  that `pre-merge-commit` covers automatic merge commits, and there is no `pre-merge-commit` hook
  here. I did not run a real merge to confirm it, because I am not authorised to merge.
- ~~**The CI result on the real runner.** Simulated on Python 3.14.6 / macOS against 3.11 /
  Ubuntu (6.2). A workflow that has never executed is not known to pass, and mine is a simulation,
  not an execution.~~ **RESOLVED in revision 3.** It has executed seven times; the real log
  confirms the simulation including the 25-defect count (6.1, 6.1a).
- **Whether the R9 tips in section 1 or 2 are still current.** They are certainly not; two moved
  during revision 3 and one moved between two consecutive commands. That is why section 9.1 is a
  discovery procedure and not a list.
- **The credential question beyond the landing range.** Section 5.2 bounds what the landing adds.
  It says nothing about what is already public.
- **Whether the two recovery commits (5.4) contain what their slots intended.** I read their
  diffstats, not their content. `d55ac14` says of itself that it is untested. Only the authoring
  slots can close this.
- **Whether a union resolution of `.gitignore` (3.3) preserves the carve-out ordering.** I gave
  three `check-ignore` assertions that would detect a regression. I could not run them, because
  the resolution does not exist yet.
- **The `hf_space` decision (3.5).** Not a verification gap, a decision gap. I established that
  neither side is a superset and that one option reverts PR #11; which app the public Space should
  serve is not mine to settle.
- **That the seven canford-checks runs were all on the same workflow content.** I read the
  per-step log for `32278287331` only. The six older runs are reported green at job level; I did
  not open their logs, so "green" for those six is a run-level fact and, per 6.1a, that is exactly
  the fact which does not imply the checks passed. The *count* of seven is confirmed complete
  (workflow-filtered, limit 100); it is the six older runs' *contents* that are unread.

- **The 0.60 boundary operator, and which view I searched**, because
  `docs/R9_DISCREPANCY_REGISTER_2026-08-19.md` row C2 asks for the scope to be stated. **Scope:
  `/Users/josie/can-it-ford`, including `.claude/worktrees/`, excluding `.git/`.** In that view
  MEASURED **58 copies of `make_phase_space.py`, 2 distinct contents, split 29/29**, and
  `h < 0.60` returns **zero** files. The two variants are `h <= 0.60` and `haz > 0.60`, which are
  the same boundary rule inverted, so C2's conclusion holds in my view too: **no operator fork
  exists inside this repo**, and this search cannot see the pre-history-purge clones where
  CLAUDE.md records `h < 0.60`, so it does not refute that claim.
  **Two differences from C2 worth recording rather than smoothing over.** C2 reports **70 copies,
  35/35**; I get 58, 29/29. Same ratio, same conclusion, different totals, so this is a scope
  difference and not a disagreement about the answer, and per CLAUDE.md item 13's rule neither
  number is usable without its scope. Mine sits 56 in `.claude/worktrees/`, 1 in
  `designsafe-staging/scripts/`, 1 in `analysis/`. Separately, and this is why the row does not
  affect the landing: MEASURED, **none of the nine R8 branches touches `make_phase_space.py`**,
  so it is not in the merge set and cannot produce a conflict here.

**Review status, stated rather than implied.** The `physics-skeptic` subagent was **not** run
against this document, and no adversarial pass by another agent was performed. That is a
deliberate omission on two grounds: this session was instructed not to spawn subagents, and this
document makes no physics claim of its own. Every percentage, force, verdict count and distance
that appears here (the 93.7 against 77.7 percent settle figures, the SLIDE counts, the g96 cap
ladder) is **quoted from another slot's board row or commit as history**, attributed at the point
of use in section 8, and is not asserted by me. The claims this document does assert are git
topology, file counts, blob relationships, hook behaviour and CI exit codes, all of which are
reproducible from the commands printed beside them. Those commands are the review: re-run them.
Treat any number here that does **not** carry a command as unreviewed.

## 11. Flags raised, none of them blocking the rest of the plan

Per the operating protocol, flagged rather than silently passed:

1. **Unrotated credential exposure gating a push to a public repo** (5.1). Hard-stop class.
   Josie's decision. Everything up to and including step 7 of 9.4 proceeds without it.
2. **Two false statements already public in the poster on `origin/main`** (5.3). Not created by
   this landing. Named because a landing is the moment to decide.
3. **A masked CI failure** (6.1a, 6.2 caveat 1, 6.3 item 1). **Escalated in revision 3 from
   "simulated" to "measured in production":** it has been failing on every run for two days
   behind a green tick. Still not blocking the landing; it is the reason the landing should not
   be reported as "CI now passes".
4. **`hf_space/`: two different applications, and one option silently reverts a public physics
   fix** (3.5). NEW in revision 3. This is the one item I am flagging rather than resolving, on
   both protocol grounds: a genuine disagreement needing a judgment call, and a public artifact.
5. **Two unreviewed recovery commits at branch tips** (5.4). NEW in revision 3. Not a hard stop;
   it needs two slots to confirm their own work, and the fallback loses nothing.
6. I did **not** flag the `openchannel_bc.py` conflict as a disagreement between slots. It is not
   one: `d4-bcmerge`'s document and my independent line-containment check agree, and the third
   version is a common ancestor of both. The coordinator's register row C1 has since been
   rewritten to match (`7a0d08a`), so this is now settled on both sides.
7. I did **not** flag the `19` versus `20` deep-search disagreement (3.4), because it was
   resolvable by going and getting the data rather than by a judgment call. Answer: **20**,
   read live from the workspace, with the twentieth search timestamped after the losing claim was
   measured.

---

## 12. Audit of the three updates supplied with the revision-3 go-ahead

Each was checked rather than adopted, per the standing rule that a claim from another session is
not a second source. Two reproduced exactly. One needed narrowing, and the narrowing matters.

**Update 1: "`claude/add-ci-checks` IS NOW PUSHED and verified by `ls-remote`, and has since moved
to `7a0d08a`. Re-derive both counts; your 64 ahead is stale in the ahead direction."**

PARTLY CONFIRMED, and narrowed. MEASURED:

- Pushed: **YES**, and earlier than "now". `refs/remotes/origin/claude/add-ci-checks` records
  three pushes, 2026-08-18 06:07:44, 2026-08-18 21:52:34, and 2026-08-19 17:51:13. The branch has
  been on `origin` for two days, not since today.
- Moved to `7a0d08a`: **YES**.
- **But the remote is at `faf53d1`, not `7a0d08a`.** `git ls-remote` live: `faf53d1`. The local
  branch is **1 commit ahead of its own remote copy**, and that commit is `7a0d08a` itself, the
  register C1 correction. So "is pushed" and "is at `7a0d08a`" are both true and are not true of
  the same ref. This matters for section 6: `7a0d08a` has **not** triggered a CI run, and will
  not until it is pushed.
- 64 stale: **YES**, and worse than stale. It was mis-dated as well; see section 0.

**Update 2: "TWO RECOVERY COMMITS exist that no session authored: `98d4d9d` on r9-moving-vehicle
and `d55ac14` on r9-renders. Flag both as needing their authors' sign-off."**

CONFIRMED in full, and acted on as section 5.4. Both are at branch **tips**, which the update did
not say and which is the operative detail: they will be landed by steps 15 and 17 with nothing in
the merge to surface them. `d55ac14` describes itself as "untested" and is 621 lines of new code.

**Update 3: "`R9-post-crash-1748-FINAL.bundle` has 19 heads and was restore-tested from a virgin
mirror. Verify rather than trust; it predates today's commits."**

CONFIRMED in full, independently. 19 heads, complete history, virgin `clone --mirror` restores all
19 at the listed SHAs, `fsck` clean, both recovery commits readable from the restored clone. The
"predates today's commits" warning is correct and I quantified it: stale on **2** heads by 18:21,
`add-ci-checks` and `r9-priorcode`, 2 commits each. Two additions the update did not carry: the
bundle contains **no `main`**, so it is not a whole-project backup; and the check nobody runs is
whether a branch is **absent from the bundle entirely**, which is what revision 2's 16-ref bundle
was against a 19-branch set (9.1 step 4).

**Also acted on: "the branch set is not a list, it is a rate, so specify how to RE-DERIVE the set
at merge time rather than pinning it."** Section 9.1 is rewritten as a discovery procedure that
takes no branch name from this document. The set moved twice while revision 3 was being written,
so this is not a stylistic preference.

### 12.1 Revision 4, 2026-08-19 19:05: three corrections, two of them to me

**(a) I asserted a merge mechanism from its plausibility and it was refuted in one command.**
Section 3.0 carried, for about ten minutes, the claim that the 19-versus-20 disagreement would be
silently auto-merged. It is not: all three lines fall inside the conflict markers. The correction
and the measurement that produced it are left in section 3.0 in place, along with what actually
survives, which is stronger and which I only found because the refutation forced me to measure:
**49.6 percent of that merged file, 317 of 639 lines, is auto-merged and never shown.**

**(b) The `make_phase_space.py` copy count: my "scope difference" attribution was WRONG, and the
reader's mechanism is right.** Register C2 said 70 copies, 35/35. I measured 58, 29/29, and wrote
that the gap was "a scope difference rather than a disagreement" although both statements declared
the identical scope. The reader measured 60, 30/30 at 18:35. **All of them are right and none of
it is scope.** MEASURED independently by me at 19:02:

```
find /Users/josie/can-it-ford -name make_phase_space.py -not -path '*/.git/*' | wc -l
# -> 62
#    31  analysis/make_phase_space.py                    (haz > 0.60)
#    31  designsafe-staging/scripts/make_phase_space.py  (h <= 0.60)
```

**There are exactly TWO tracked paths and every checkout contains BOTH.** So the total is
`2 x (checkouts carrying the file)`, the split is FORCED to be exactly half, and 70 / 58 / 60 / 62
are four readings of a moving checkout count: 35 trees at 00:19, 29 at 17:15, 30 at 18:35, 31 at
19:02. **It is a time difference.** Note `git worktree list` currently returns 35 while only 31
carry the file, so do not compute this as `2 x worktree-count` either; count the files.

The register's "35 read one form, 35 read the other" invites reading two POPULATIONS of checkouts
when the truth is two FILES inside every checkout, and the two forms are the same boundary rule
inverted, so there is no operator fork between trees at all. **That framing is what needs
correcting, more than the integer.** The sting is that `ba1abbb`, in this document, established
that this class of object "is not a list, it is a rate", and I did not apply my own finding to
the next count I made. A rule you state and do not apply is not a rule.

**(c) The branch set: I report 21 by pattern, and I am not adopting "thirteen".** MEASURED
2026-08-19 18:51:

```
git for-each-ref --format='%(refname:short)' \
  'refs/heads/claude/r8-*' 'refs/heads/claude/r9-*' 'refs/heads/claude/add-ci-checks' | wc -l
# -> 21     (1 add-ci-checks + 9 r8-* + 11 r9-*)
```

`claude/r9-reader` and `claude/r9-jobb-route` are both new and both real, which is the substance
and which I confirm. The count differs from "thirteen" by whichever scope that figure uses; since
mine names its pattern and its command, use mine or restate the other with its scope, per item
13's rule. **Two structural facts about the new pair that a count does not carry:**

- **`claude/r9-jobb-route` is NOT cut from `add-ci-checks`.** It sits at `6ed163e`, which is
  exactly `claude/r5-physics`, and its merge base with `add-ci-checks` is `777567a`, the same base
  that `r8-kramer` and `r8-force` share. **It belongs in phase 5, the `simulation/r5_physics/`
  lineage, not in the R9 tail**, and it will share files with those two once it has commits of its
  own. It does carry `canford-checks.yml`, so it is inside the CI blast radius.
- **`claude/r9-reader` had no commits of its own when first measured** and was contained in
  `add-ci-checks`; it has since gained work. Re-derive rather than reusing either state.

**(d) Accepted without reservation:** the coordinator's read that my CI log analysis supersedes
the `gh run list` summary, and the skill-version check added to the preflight at `c621931`. The
union merge for `SKILL.md` (section 3.4) is mine to land and the reader's finding that the skill
exists in four states across live worktrees makes it more urgent, not less: **most sessions are
loading a copy that still asserts a claim `CLAUDE.md` has withdrawn.**
