# Three-way reconciliation of the corrections register, 2026-08-14

Dispatch 4 of `docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md`. Branch
`claude/fork-register-reconcile`, Mac. Write scope was
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` plus this file, on this branch only.

**Claim tagging used throughout.** `[live]` means re-derived by running the command in this
session. `[read]` means read directly out of a file or a commit body. `[inferred]` means
reasoned from two or more `[live]`/`[read]` facts and not itself measured. No number in this
document is carried from a session summary or from the dispatch text without a live check,
and where the dispatch and live state disagree, both are shown.

---

## 1. What the three states actually were

`[live]` All three verified by `git show <ref>:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`:

| ref | lines | md5 | adds |
|---|---|---|---|
| `main` (`1a868f3`) | 656 | `d5f2a69d269ee7f62583ff4117ad4f5e` | baseline |
| `claude/rtfd-test-phase-1-4-569130` (`658ecfa`) | 681 | `5a4045b5c251894f0a51c02fb50945e3` | Section J items 17, 18, 19 |
| `claude/friction-resolution-reconcile-84465d` (`109ae87`) | 817 | `dbe78c0c31c366634c1f2ba497c5c69e` | A6a, A6b, D8, D8a, D8b, D8c, D9 |

The dispatch's 656 / 681 / 817 figures reproduce exactly.

**The single most useful fact about this merge, and it was not in the dispatch.** `[live]`
`git merge-base` returns `1a868f3` for **both** feature branches, which is `main`'s own HEAD.
Neither branch has diverged from a common ancestor further back; both are pure additions on
top of the current `main`. That turns what the dispatch framed as a delicate three-way
reconciliation into a mechanically checkable one: `main` **is** the merge base, so the two
deltas can be validated independently and their union verified by line arithmetic.

---

## 2. Three-column table of every item that differs

`[live]` The complete divergence set is **five loci**. `diff` reports exactly one hunk for the
rtfd delta and exactly four for the friction delta, and no other region of the file differs in
any of the three versions.

| # | Register location | `main` | rtfd branch | friction branch |
|---|---|---|---|---|
| 1 | **A6**, gravity-fork closure | 3 paragraphs: "This fork now reaches published output"; "CLOSED 2026-08-12 ... prediction was half right"; "This entry's own stated REASON is REFUTED" | identical to `main` | **rewritten and extended.** Adds the "table above is historical" note, folds the closure into one paragraph, adds "CLOSED TWICE, INDEPENDENTLY", **A6a** (the structural no-flip proof) and **A6b** (the 33-citation line-shift incident, 2 tables) |
| 2 | **D6c**, ratio vs verdict | "COUNT UPDATED 2026-08-12, from 13 to 12" | identical to `main` | same paragraph **plus** the clause that SLIDE's 17 and FLOAT's 1 did not move because both criteria are G-free, plus the `check_claims.py` C10c note |
| 3 | **Section D**, after D7a | ends at D7a | identical to `main` | **adds** "READ D9 WITH THIS ENTRY", **D8**, **D8a**, **D8b**, **D8c**, **D9** (121 lines) |
| 4 | **Section J item 15** | single paragraph, "single highest-value open item: RUN THE CANONICAL SET AT g128" | identical to `main` | **restructured.** New head "READ D9 WITH THIS ITEM"; the original paragraph demoted to an indented sub-paragraph; "67 percent" flagged for correction to 64.2 |
| 5 | **Section J items 17, 18, 19** | absent | **added** (25 lines) | absent |

Only Section J is touched by both branches, and there at different items (15 versus 17-19), so
no line modified by one branch is modified by the other.

---

## 3. Merge method, and why the result is auditable rather than trusted

`[live]` Mechanical three-way merge, `main` as base:

```
git merge-file -p --diff3 rtfd.md main.md fric.md > merged.md
```

- exit code **0**, zero conflicts
- **0** conflict markers in the output
- line arithmetic exact: 656 + 25 + 161 = **842**

Two directional diffs then confirm neither delta was dropped:

- `merged` vs `fric`: **25 added, 0 removed** — precisely the rtfd delta
- `merged` vs `rtfd`: **167 added, 6 removed** — precisely the friction delta

**The 6 removed lines are the only place content was replaced rather than appended**, so each
was checked individually rather than assumed superseded. `[live]` 18 distinguishing substrings
drawn from those 6 lines were grepped against the merged file; **all 18 survive**, including
`1.000244`, `0.999903`, `0.0244 percent`, "A conclusion reached for a refuted reason is not
verified", "3 of 33 columns", the D6c "figure is now 12" consequence, and J15's original "drift
still falls 67 percent" (retained alongside D9's correction to 64.22, so the correction stays
auditable against what it corrects).

**Nothing from any of the three versions was rejected.** The dispatch allowed "retained or
explicitly rejected-with-reason"; the rejected column is empty, because the two deltas are
complementary and disjoint. `[live]` `register_integrity.py` counts **items defined 106 -> 116**,
exactly the 10 new items (17, 18, 19, A6a, A6b, D8, D8a, D8b, D8c, D9).

---

## 4. D8c's refusal, verified rather than merely preserved

The dispatch warned that a careless merge could silently re-apply the repoint D8c refuses
(CLAUDE.md item 3's `sim_standing.py:132-137` -> `:210-211`). D8c is carried through verbatim,
and its evidence was re-derived `[live]` in the main worktree rather than taken on the entry's
word:

| file | lines | bytes | sha256 |
|---|---|---|---|
| `renders/yaris_render_s1/_incoming/sim_standing.py` | **389** | **17435** | `5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45` |
| `renders/yaris_render_s1/sim_standing.py` (top level) | **564** | | `4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9` |

Every figure matches D8c's table, and the 17435 bytes independently matches the 2026-07-25
Vista measurement D8c cites. `[live]` `git check-ignore -v` confirms the `_incoming` copy is
ignored by the `renders/yaris_render_s1/*` rule (rule re-derived by grep, not cited by line
number, per the standing `.gitignore` caution). **No repoint was applied.**

---

## 5. Corrections made, and one correction refused

### 5.1 Item 18's phrasing — corrected, but not as instructed

The dispatch instructed: correct item 18 because the sweep table "also appears in
`docs/SESSION_TRACK1B_2026-08-13.md:233`, added by `b62d554`, **44 minutes EARLIER**" than
`ed8bf8e`.

`[live]` **All three components are false.** Tested by walking every commit that has ever
touched that file and grepping each commit's own blob for `6.9669`:

| | dispatch claimed | live |
|---|---|---|
| commit that added the table | `b62d554` | **`1a868f3`** |
| direction | 44 min **before** `ed8bf8e` | **19 min 15 s AFTER** |
| `b62d554`'s own copy | contains the table | **163 lines, ZERO occurrences of `6.9669`** |

`b62d554` (05:23:47 -0500) created the file citing a *different* store,
`data/rogue_silverado_grid_sweep_2026-08-13.csv`, 8 rows. Intermediate commits `8590313` and
`5e0f764` also carry zero. The table first appears at `1a868f3` (06:54:07 -0500); `ed8bf8e` is
06:34:52 -0500.

`git blame` alone does **not** settle this, since it attributes only the last commit to touch a
line; the decisive test is per-commit content.

**The dispatch's conclusion survives; its evidence does not, and the true count is higher.**
`[live]` the measurement has **four** write-ups, not three: the `ed8bf8e` body; the
`SESSION_TRACK1B` table; **register item 15 itself**, reporting the same runs through different
columns (0.0778 m, 1.56x rather than `ratio_slide`); and the primary CSV. Write-ups 2 and 3 are
the **same commit** `1a868f3`, which touched exactly two files. So **the register is itself one
of the write-ups**, which is a sharper statement of item 18's own rule than item 18 makes.

Written into the register as **item 18a(i) and 18a(ii)**.

### 5.2 Item 18's closing sentence was stale on its own branch

`[live]` Item 18 landed in `e431877` at 2026-08-13 17:40:26 +0200 closing with "the direct g128
canonical test still has not been run." Item 19, recording that the test **has** been run for
the mass sweep, landed in `a6e42c1` at 18:30:42 +0200 **on the same branch, 50 minutes later**.
The sentence is retained unedited and superseded in place. Written in as **item 18a(iii)**.

### 5.3 Two cross-references that the merge itself makes stale

Both branches were written the same day without sight of each other, so two forward-looking
statements become stale only *once merged*. Neither branch's text was rewritten; a dated
reconciliation note was added at each site.

- **Section J item 15 head.** Its "single highest-value open item: RUN THE CANONICAL SET AT
  g128" is partly answered by item 19. Note added: 3 of 17 configurations, no verdict flips,
  item stays open with scope narrowed, and the finding has moved from the verdict to the margin.
- **D9's "OPEN, AND RANKED" list, entry (3).** Same discharge. The note records that item 19
  narrows **only** (3), and explicitly **not** (1), (2) or (4) — and that item 19 *strengthens*
  (1), because it holds `mu` fixed and walks grid, the same half of the 2 x 2 that J15 walked,
  leaving D9's crossed design still unrun.

---

## 6. A finding that exists only because the branches were merged

`[live]` Register **item 19a**, new in this reconciliation.

Item 19 stamps its g128 canonical runs with driver sha256 `4696c3b2` and stops there. D8c
independently establishes that `4696c3b2` is the **2026-08-08 revision** and that the driver
which produced the 17 gated runs is `5215c38b`. `[live]` the two facts sat on different
branches and **neither cited the other**: the rtfd register names `4696c3b2` once and
`5215c38b` never; the friction register names both and never mentions item 19.

`[inferred, from those two [live] reads]` **The g128 "canonical" replication did not run the
canonical driver.**

**The novelty is the identification, and I initially overstated it.** `[live]` item 19 already
lists "a driver and engine-checkout change" alongside Vista GH200 to LS6 A100 when explaining
its **-4.79 percent** g96 gap, so it is not unaware that the driver moved. A first draft of
19a implied otherwise and was corrected before commit. What item 19 does not say, and could
not from its own branch, is **which** driver: it names `4696c3b2` and never names `5215c38b`.
The fact that the driver it ran is a *different program* from the one that produced the 17 —
per D8c, 188 added and 13 modified lines including a `fill_ratio` denominator change — exists
only once the two branches are read together. So "same driver, finer grid" is not an available
description of this comparison.

Recorded as open and untested: whether any part of item 19's g96-arm discrepancy is
attributable to the driver change rather than to venue.

---

## 7. `register_integrity.py`

`[live]` Run on both, same checker, same worktree:

| register | items | blocking defects | warnings |
|---|---|---|---|
| `main` baseline (656) | 106 | **0** | 11 |
| reconciled (842) | 116 | **0** | 20 |

**Definition of done met: 0 blocking defects.**

The 9 new warnings were triaged rather than waved through, and **none is a real defect**:

- **6 unresolved paths**, each an evidence file cited by merged-in text. `[live]` every one
  resolves on exactly the branch that contributed the citation and on no other
  (`data/g128_canonical_slide_classification_2026-08-13.csv` and
  `docs/G128_CANONICAL_FINDINGS_2026-08-13.md` on rtfd;
  `docs/FLOOR_FRICTION_RUNG_2026-08-12.md`,
  `docs/FRICTION_RESOLUTION_RECONCILE_2026-08-13.md`,
  `docs/FRICTION_RUNG_HORIZONTAL_INSTRUMENTATION_2026-08-13.md` and
  `simulation/coupling_validation/rung_e_floor_friction.py` on friction).
- **1 unresolved path**, `renders/yaris_render_s1/_incoming/sim_standing.py`, on no branch at
  all: it is gitignored and untracked, exactly as CLAUDE.md records. It is present on disk in
  the main worktree and was hashed there (section 4).
- **2 unresolved hex tokens**, `4696c3b2` and `5215c38b`. `[live]` `git cat-file -t` resolves
  neither, correctly: they are **sha256 prefixes of file content**, not git objects. This is a
  false-positive class of the checker, not a fabricated SHA.

**Structural consequence worth stating plainly.** Merging the register alone imports 6 citations
whose evidence lives on branches this one does not carry. The reconciled register is correct as
text, but its evidence base is complete only once those two branches are themselves merged.
That is a direct consequence of the dispatch's write scope, not a defect in the merge.

---

## 8. The two main-worktree shadow risks — REPORTED, NOT FIXED

As instructed. `[live] 2026-08-14`, `git -C /Users/josie/can-it-ford status --porcelain=v1`:

| risk | live state |
|---|---|
| modified `.mcp.json` | **1** file, ` M .mcp.json` |
| untracked `renders/yaris_render_s1/*.py` | **22** files |
| whole main worktree | 25 untracked, 1 modified |

Both dispatch figures reproduce exactly (the dispatch said "~22"; it is 22). Nothing was staged,
committed, reverted or touched in the main worktree by this session. Per memory
`shared-index-sweeps-plain-commit.md` the hazard is that a bare `git commit -m` from any other
session in that worktree sweeps both in unreviewed, and per `can-it-ford-github-repo-is-public.md`
anything so swept is world-readable and permanent once pushed.

---

## 9. The check that does not exist

The dispatch named two corpus notes as the project's own guidance on this hazard, written
2026-07-24 and "never turned into a check". `[read]` Both were read
(`07_Repo_Provenance_and_Corrections/2026-07-24_provenance-note_claude-md-provenance-tracking_CURRENT.md`
and `..._worktrees-backup-provenance_CURRENT.md`). Their method is sound and directly
applicable: **content-hash every copy against a canonical live source, and do not assume a
shared filename means a shared lineage.** The register case satisfies it — all three copies are
one lineage, sharing merge-base `1a868f3`, which is the opposite of the CLAUDE.md case those
notes document, where 12 copies were mostly unrelated lineages sharing a filename.

`[live]` **The gap is confirmed and specific.** `register_integrity.py` contains zero
occurrences of `branch` or `divergen`: it validates one register file in isolation. It cannot
detect that three divergent copies of the sole corrections authority exist simultaneously,
which is the precise failure this dispatch was created to clean up. **A cross-branch divergence
check is the missing tool**, and it is cheap: for each ref carrying the register, compare blob
hashes and report any set with more than one distinct hash. Not built here, as it is outside
this dispatch's write scope.

---

## 10. Scope honoured, and what was deliberately not done

- Wrote **only** `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` and this file, on
  `claude/fork-register-reconcile`.
- **No** write to `main`, to `claude/rtfd-test-phase-1-4-569130`, or to
  `claude/friction-resolution-reconcile-84465d`. All three were read via `git show` only.
- **No** merge of the two source branches themselves. This reconciles the register file; it does
  not merge the branches, and the register items on them remain branch-only until someone takes
  that decision. Dispatch 1 was told the same.
- **No** touch of `.mcp.json`, of any `renders/*.py`, or of anything credential-related.
- **No** push. The GitHub repo is public.
- CLAUDE.md was **not** edited, though item 3 is discussed by D8c. It is outside this scope.

**Labelled assumption, reversible.** The two cross-reference notes in section 5.3 and the item
19a note in section 6 are additions I made at merge time, not text from any branch. They are
each explicitly dated and attributed to this reconciliation inside the register itself, so if a
later session disagrees with the reconciliation it can strip them without disturbing either
branch's original wording, which was preserved unedited in every case.
