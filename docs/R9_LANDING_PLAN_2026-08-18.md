# R9 landing plan: getting fifteen local-only branches onto a remote, and making the CI run

Slot `d16-landing`, branch `claude/r9-landing`, worktree `.claude/worktrees/r9-landing`.
Written 2026-08-18 23:40 to 2026-08-19 00:05 BST (the session crossed midnight; the filename
keeps the dispatch date).

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

**`claude/add-ci-checks` is 64 commits ahead of `origin/main` AND 5 commits BEHIND it.**

MEASURED:

```
git -C /Users/josie/can-it-ford rev-list --left-right --count origin/main...claude/add-ci-checks
# -> 5	64        (left = behind, right = ahead)
```

Every prior statement of this relationship in the project, including the one the session-start
banner prints, gives only the ahead half. The behind half is the one that matters for a landing,
because **thirteen of the fifteen branches in this round are based on `claude/add-ci-checks`**, so
thirteen branches are built on a base that is missing merged work.

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

## 1. Inventory: fifteen branches, not nine. Eighteen by the time I finished.

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

| phase | branch | result | files | hook |
|---|---|---|---|---|
| 1 | `origin/main` into `claude/add-ci-checks` | CLEAN | 7 | none fires |
| 2 | `claude/r8-register` | CLEAN | 2 | none fires |
| 3 | `claude/r8-licence` | CLEAN | 4 | none fires |
| 3 | `claude/r8-tooling` | CLEAN | 19 | none fires |
| 3 | `claude/r8-naming` | CLEAN | 9 | none fires |
| 3 | `claude/r8-priorart` | CLEAN | 10 | none fires |
| 4 | `claude/r8-bc-merge` | **CONFLICT**, 1 file | 2 | `pre-commit` ok |
| 4 | `claude/r8-persistence` | **CONFLICT**, 1 file | 13 | **`pre-commit` REFUSES** |
| 5 | `claude/r8-kramer` | CLEAN | 31 | none fires |
| 5 | `claude/r8-force` | CLEAN | 2 | none fires |
| 5 | `claude/r9-accessor` | no-op, contained | - | - |
| 5 | `claude/r9-kramer-extract` | no-op, contained | - | - |
| 6 | four R9 doc branches | no-op today, see 1.2 | - | - |

Final simulated integration head: 1019 files, `canford-checks.yml` present, register blob
`1c900e5` (the `r8-register` merged product, not `add-ci-checks`'s `124dd74`).

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

**There is exactly one conflicting file across all fifteen branches.** MEASURED, every pair that
shares a path was simulated:

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
- The two **conflicted** merges are completed with `git commit`, which does fire `pre-commit`.
  `r8-bc-merge` stages 2 files and passes. **`r8-persistence` stages 13 files and is REFUSED.**

The hook is doing its job: it exists because a shared working tree lets another session's staged
work ride along on a bare commit. Here the 13 files are all genuinely from the merge, so the
override is correct, but it must be **explicit and path-checked**, not habitual:

```
# after resolving simulation/openchannel_bc.py, and ONLY after reading the list:
git -C /Users/josie/can-it-ford diff --cached --name-only     # confirm all 13 are from r8-persistence
git -C /Users/josie/can-it-ford commit --no-verify            # the ONLY --no-verify in this plan
```

If that list contains anything not attributable to `claude/r8-persistence`, stop: another session
has staged work in the shared index, and committing would sweep it in.

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

---

## 6. The CI question: what it would take to run, and what it would do

### 6.1 It runs nowhere today, confirmed

MEASURED:

```
git -C /Users/josie/can-it-ford ls-tree -r --name-only origin/main -- .github/workflows/
# -> csv-check.yml, physics-consistency-review.yml, sync-to-hub.yml
# canford-checks.yml is ABSENT
```

`.github/workflows/canford-checks.yml` exists only on `claude/add-ci-checks` and the branches cut
from it. GitHub Actions only ever reads workflows from the repository on GitHub. **What it takes
for it to run is exactly one thing: the file has to reach `origin`.** Section 2's phase 1 plus the
final `add-ci-checks` to `main` merge does that, and nothing else is required. There is no
runner configuration, secret, or permission to arrange first.

### 6.2 What it would do the first time, measured rather than predicted

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

### 6.3 Three changes worth making before it lands, none of them blocking

1. Add `--register` style explicitness or drop `continue-on-error` from `count_claims` and instead
   teach it that a tracked-only tree is a different scope. Masking a real failure is worse than
   not running the check, because the green tick is then evidence for a proposition nobody tested.
2. `on: push` has no branch filter. With 102 local branches, if a batch of them is ever pushed,
   this fires once per branch per push, plus again for any pull request. Consider
   `on: push: branches: [main]` plus `pull_request`.
3. `.claude/tooling/MERGE_github_workflow.yml` arrives with `claude/r8-tooling` in phase 3. It is a
   template intended to be merged into the workflow. Decide whether it supersedes
   `canford-checks.yml` before landing both, or you will land two overlapping answers to the same
   question.

---

## 7. The bundle: verified, and it went stale while this was being written

MEASURED. `/Users/josie/can-it-ford-bundles/2026-08-18/R8R9-all-heads-2350.bundle`, 493,615,746 B,
mtime 23:41. `git bundle verify` reports "The bundle records a complete history" and lists **16
refs**. I restore-tested it independently: `git clone --mirror` into a scratch directory, then
compared all 16 restored heads against the live tips. All 16 matched at 23:50.

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

### 9.1 Re-derive everything before starting. Do not trust section 1.

```bash
R=/Users/josie/can-it-ford
B=/Users/josie/can-it-ford-bundles/2026-08-18/R8R9-all-heads-2350.bundle   # or the newest

# every branch tip, live
git -C $R for-each-ref --format='%(objectname:short=7) %(refname:short)' \
    'refs/heads/claude/r8-*' 'refs/heads/claude/r9-*' 'refs/heads/claude/add-ci-checks'

# the ahead AND behind counts, both halves, for every branch
for b in $(git -C $R for-each-ref --format='%(refname:short)' 'refs/heads/claude/r8-*' 'refs/heads/claude/r9-*'); do
  printf '%-28s %s\n' "$b" "$(git -C $R rev-list --left-right --count origin/main...$b)"
done
```

### 9.2 Verification rules, which are the part most likely to be got wrong

**A check that cannot tell "equal" from "could not evaluate" is worse than no check.** My first
bundle comparison printed a clean `IN BUNDLE` for all ten heads. It was wrong: zsh does not
word-split unquoted variables, both sides of every comparison evaluated to the empty string, and
empty equalled empty. A silent false PASS. The coordinator hit the same shell property in the same
ten minutes from the other direction, passing sixteen ref names to `git bundle create` as one
argument, which was loud only because git happened to reject it. This project has now logged four
instances of a comparison whose both arms failed being reported as agreement.

Every comparison in a merge verification must therefore carry an explicit third outcome:

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
ref, no index and no working tree, chained inside a throwaway mirror clone of the bundle. Re-run
it after re-deriving tips; if any branch that was CLEAN comes back CONFLICT, the plan's order is
stale and section 3 needs redoing before anything is merged. Scripts are in the session
scratchpad: `verify_bundle.sh`, `simfinal.sh`.

### 9.4 Order of operations on the day

1. Re-derive tips (9.1). Re-verify the bundle (9.1). Re-run the dry run (9.3).
2. Answer the four preconditions in section 5. **Rotation is the one that gates pushing.**
3. Phase 1 to 6 locally, on `claude/add-ci-checks`, verifying each merge with `HEAD^2` (9.2).
4. Only `claude/r8-persistence` needs `commit --no-verify`, and only after reading the staged list
   (3.2).
5. Verify the register by entry (9.2). Run the six CI checks locally against a `git archive`
   export, not against the working tree, or you will get the full-tree answer and not the CI one
   (6.2).
6. Merge `claude/add-ci-checks` into `main` locally.
7. **Stop. Pushing is a separate authorisation** and requires `PUSH_OK=1`, an answered rotation
   question, and confirmation afterwards that the remote actually moved (`git ls-remote origin`),
   because a command exiting 0 is not evidence the remote updated.

---

## 10. What I could not verify

- **That any of this succeeds when executed.** Every merge result is `merge-tree`, which is the
  same algorithm `git merge` uses but does not exercise hooks, the working tree, or the index. The
  `pre-commit` prediction in 3.2 is INFERRED from reading the hook and from git's documented rule
  that `pre-merge-commit` covers automatic merge commits, and there is no `pre-merge-commit` hook
  here. I did not run a real merge to confirm it, because I am not authorised to merge.
- **The CI result on the real runner.** Simulated on Python 3.14.6 / macOS against 3.11 / Ubuntu
  (6.2). A workflow that has never executed is not known to pass, and mine is a simulation, not an
  execution.
- **Whether the R9 tips in section 1 are still current.** They are certainly not; one moved during
  writing. That is why section 9.1 exists.
- **The credential question beyond the landing range.** Section 5.2 bounds what the landing adds.
  It says nothing about what is already public.
- **Anything about the four R9 branches' content.** Three were still no-ops at 00:01 and one had
  one commit. Their merges are predicted from structure, not measured against real work.

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
   Josie's decision. Everything up to and including step 6 of 9.4 proceeds without it.
2. **Two false statements already public in the poster on `origin/main`** (5.3). Not created by
   this landing. Named because a landing is the moment to decide.
3. **A masked CI failure** (6.2, caveat 1). Not blocking; the job goes green either way, which is
   the problem.
4. I did **not** flag the `openchannel_bc.py` conflict as a disagreement between slots. It is not
   one: `d4-bcmerge`'s document and my independent line-containment check agree, and the third
   version is a common ancestor of both.
