# R8 REGISTER MERGE, 2026-08-18

Merge of `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` across two divergent lineages.
Slot d7-register, branch `claude/r8-register`. Nothing here is merged anywhere else; a human
decides where this lands.

Every count below is enumerated by a script that prints the entry identifiers it counted, not
asserted. **No verification in this document is based on a line count.** Reproduce with
`scratchpad/verify.py`, or re-derive from the two input blobs named in section 1.

---

## 1. THE STRUCTURAL FINDING, AND WHY A ZERO-CONFLICT MERGE PROVES NOTHING HERE

**`claude/add-ci-checks` is `origin/main` verbatim for its first 656 lines plus a pure append.
`claude/fork-register-reconcile` expanded sections A to J in place and appended nothing. The two
lineages edited disjoint regions of the file.**

That single sentence explains the whole hazard. `git` reports zero conflicts because no two edits
touch the same region, and it would happily produce a file in which the sections carry one
lineage's text and the addenda carry the other's, with no signal that anything was decided. The
Round 7 ledger's warning about "a clean zero-conflict merge that silently drops 126 lines" was
pointing at this, and the collision documented in section 4 is the same failure wearing a
different disguise: `git` cannot see an identifier collision at all, because the colliding items
are nowhere near each other in the file.

Inputs, resolved live at merge time rather than from any pinned SHA:

| lineage | commit | register blob |
|---|---|---|
| `origin/main` | `c7f0a16` | `28ce0af` |
| `claude/fork-register-reconcile` | `c1235e5` | `7551d24` |
| `claude/add-ci-checks` (= `origin/claude/add-ci-checks`, pushed) | `59234f9` | `124dd74` |

`merge-base(add-ci-checks, fork-register-reconcile)` is `1a868f3`.
`git log --merges 1a868f3..claude/add-ci-checks` is empty, so no merge had happened.
`fork-register-reconcile` is **not** an ancestor of `add-ci-checks`.

The dispatch recorded the public register at `de191b8` / 1644 lines. That is stale: the public
branch is now `59234f9`. The single intervening commit did not touch the register, so its blob is
still `124dd74`, identical to the base this merge started from. Re-derived, not assumed.

---

## 2. ENTRY COUNTS, ENUMERATED

The file uses **three** entry-numbering schemes. Any count that models only one of them is wrong.

| scheme | example | `origin/main` | `fork-register-reconcile` | `add-ci-checks` | **merged** |
|---|---|---:|---:|---:|---:|
| bold letter ids | `**A1.**` | 90 | 154 | 90 | 154 |
| plain letter ids | `K0.` | 5 | 5 | 5 | 5 |
| addendum letter ids | `L1.` | 0 | 0 | 7 | 7 |
| top-level numbered | `17.` | 16 | 19 | 41 | 44 |
| **total entries** | | **111** | **178** | **143** | **210** |

Set relations, measured:

- The 90 bold ids on `add-ci-checks` are a **strict subset** of the 154 on `fork-register-reconcile`.
- 64 bold ids exist only on `fork-register-reconcile`.
- 7 ids (`L1` to `L7`) exist only on `add-ci-checks`.
- Letter-id union is **166**. The merged file contains **166**: nothing lost from either input,
  nothing invented (`LOST from fork: NONE`, `LOST from add-ci-checks: NONE`,
  `NEW (not in either input): NONE`).
- Numbered ids in the merged file are **contiguous 1 to 44**, no gaps and no duplicates.

**Fidelity of everything not contested**, verified by inverting the renumbering and comparing to
the source:

- Section J items 1 to 16 reduce exactly to `fork-register-reconcile`.
- Addendum items 17 to 41 are **byte-identical** to `add-ci-checks`.
- Items 42 to 44 reduce exactly to `fork-register-reconcile`'s items 17 to 19.
- Nine letter entries (`D9 D9a G21 G22 G23j G23l G4e G4f G7a`) changed. Inverting the repoint
  reproduces the fork text byte-for-byte in all nine, so the only delta is the cross-reference
  number. Listed here because "changed" would otherwise look like content drift.

---

## 3. THE DECISION SET: ENTRIES PRESENT IN BOTH WITH DIFFERENT CONTENT

Eleven entries, not 731 lines. Seven bold, one numbered, and a three-way identifier collision.

| entry | winner | why |
|---|---|---|
| `A2` | fork | See below. Grafting the other side would have reintroduced a documented error. |
| `A6` | **merge of both, plus a correction** | Neither side is a superset, and the survivor contained a false clause. |
| `D6c` | fork | Strict superset. Fork adds that SLIDE's 17 and FLOAT's 1 are G-free so did not move, and that `check_claims.py` C10c deliberately does not hardcode the tally. |
| `F5` | fork | Not actually contested. The entry text is identical; fork carries a "READ BEFORE F6" preamble introducing its fork-only F6 series. |
| `G4a` | fork | Strict superset. Fork adds the Wong peak-vs-sliding distinction, the SAE 690214 terminus with its "probable, not established" caveat, and Azhar's own "could drop to 0.30". |
| `G4b` | **merge of both** | Each side holds something the other lacks. |
| `G7` | fork | Fork's `G7` + `G7a` contain the whole of the other side's `G7` verbatim, plus the year correction. |
| Section J item 15 | fork | Strict superset. The `add-ci-checks` text is fork's closing three paragraphs verbatim, wrapped in qualifiers 15a, 15b and (a) to (g). |
| Section J items 17, 18, 19 | **both kept, fork's renumbered** | Identifier collision. See section 4. |

### 3.1 `A2`: fork wins, and the graft I planned would have been a regression

My scope confirmation proposed taking fork's `A2` and grafting in the other side's citation,
`newtonian()` at `materials/__init__.py:78-83`. **That was wrong and live verification caught it.**
Fork's `A2a` already documents that citation as an error, and the source agrees:

- `def newtonian` is at `materials/__init__.py:125`, not `:78`.
- `:78` is `if self.base == "newtonian":`, the `Material.resolve()` branch, not the factory.
- The file contains **no `g` key at any line**, which is the fact that actually carries the claim.

So `:78-83` is a real and in fact stronger citation, but for a different thing, and calling it the
factory is the error `A2a` exists to correct. Fork carries both with the right roles. Taking the
"newer" side here would have reinstated a known defect.

### 3.2 `A6`: merged, and the survivor carried a false clause

Neither side is a superset.

- Only on fork: the table is marked historical, the dead-code finding for
  `analysis/viability_dashboard_scaffold.py`, the "CLOSED TWICE, INDEPENDENTLY" paragraph, and the
  pointer to `A6b`.
- Only on `add-ci-checks`: the paragraph beginning "This entry's own stated REASON is REFUTED",
  which records that `g48_m2337` sat at `ratio_topple` 1.000244, a margin **smaller** than the
  0.0342 percent change, and crossed. Its closing rule, "a conclusion reached for a refuted reason
  is not verified", exists nowhere else on any lineage.

Both are in the merged entry.

**The correction.** Fork's `A6` asserted "as of 2026-08-12, **no code site holds 9.80665**; both
were set to 9.81". Measured live 2026-08-18 with `/usr/bin/grep -rn "9\.80665"` over `*.py`,
excluding `third_party/`, `.claude/worktrees/`, `archive/` and `__pycache__/`:

- **Exactly one assignment survives**, `analysis/viability_dashboard_scaffold.py:11`, and it is
  tracked (`git ls-files` resolves it).
- `G` occurs exactly once in that file, at the assignment, so it is never read. Nothing in the repo
  imports the scaffold.
- `simulation/failure_modes.py:14` does read `G = 9.81`, unified by `e495b56`, so the first half of
  the clause was right.
- The other string occurrences are prose: a docstring at `analysis/classify_failure_modes.py:30`,
  a comment at `simulation/failure_modes.py:15`, and three message strings in
  `scripts/check_claims.py`.

The false clause also **contradicted the very next sentence of its own entry**, which describes the
surviving site as dead code. `CLAUDE.md` items 3 and 15 and `check_claims.py` Rule C6 all say one
site survives, and the live measurement agrees with them, not with fork. Corrected in place, with
the superseded wording quoted so the change is auditable. **Count assignments, not string
occurrences.**

### 3.3 `G4b`: merged, and the other side held a measured set found nowhere else

- Only on fork: Keller and Mitsch 1993 (UWRAA Report No. 69) as a fourth convention source, full
  report identifiers for Bonham and Hattersley 1967, Gordon and Stone 1973 and Shand et al. 2011,
  the verbatim Shand justification, and the point that four sources sharing one data gap is one
  convention.
- Only on `add-ci-checks`: the two-sided reader warning, and **measured comparanda, Shu et al. 2011
  spring balance on wet carpet: Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68**.

Those three numbers are the clearest single instance of what a mechanical merge would have dropped:
they are measurements, they appear on one lineage only, and nothing else in the register carries
them. Both halves are in the merged entry.

### 3.4 `G7`: fork wins, and the year is verified against a primary registry

Fork corrects the year to 2023 and strikes 2022; `add-ci-checks` keeps 2022 but adds a scope
caveat. Fork's `G7a` already contains that caveat **verbatim**, so fork is a strict superset and
nothing is lost.

This project has twice had a confident year-correction instruction turn out to be wrong, so the
year was verified independently rather than accepted. Fork verified against Scite; this merge
verified against **Crossref** via `scholar-sidekick verifyCitation`, which is a separate origin:

- verdict `matched`, confidence `high`, zero mismatch fields.
- Isik, Doruk and He, Zhaoming; *Computational Particle Mechanics* **10(3):503-517**;
  `issued` **2023**, `published-print` 2023-06; DOI `10.1007/s40571-022-00511-8`.
- `created` is **2022-08-27** against `published-print` **2023-06**, which independently confirms
  `G7a`'s stated mechanism: Springer mints the DOI at acceptance, so **the year embedded in a DOI
  is not the publication year**.

Two sources with genuinely separate origins, so this counts as corroboration.

---

## 4. THE IDENTIFIER COLLISION, AND THE RULING

Section J is a numbered list. Both lineages continued it past item 16, independently, with
unrelated content, on different dates.

| id | `fork-register-reconcile` (2026-08-13) | `add-ci-checks` (2026-08-18) |
|---|---|---|
| 17 | g64 settle gate is non-deterministic at fixed config | g128 canonical set exists, verdict survives refinement |
| 18 | the "two independent resolution-dependence findings" are one finding | g128 velocity sweep |
| 19 | item 15's direct test has been run for the mass sweep | g128 depth sweep |

A mechanical merge yields a register with two item 17s, two item 18s and two item 19s, after which
every citation of a Section J item by number is ambiguous.

**RULING, and the reason, recorded so this is not re-litigated.** The `add-ci-checks` numbering is
preserved and fork's three are renumbered **42, 43, 44**. The `add-ci-checks` numbering is the one
already cited in the wild: `CLAUDE.md` cites J15 and J16 by name, the 2026-08-18 work cites them,
and `origin/claude/add-ci-checks` is **public**, so those identifiers are world-readable at a fixed
SHA. Renumbering the public side would silently repoint every existing citation. Renumbering the
fork side breaks nothing, because `claude/fork-register-reconcile` has never been pushed and
nothing outside it cites its items 17 to 19.

**The measurement that makes this cleanly executable**: `fork-register-reconcile` references items
17, 18 or 19 in **55 places across 26 lines**; `add-ci-checks` references them **zero** times
outside their own definitions. So only fork-side text needed repointing, and no `add-ci-checks`
text was touched at all.

The three are placed in a new trailing section rather than back in Section J, so that numeric order
and file order agree for a reader scanning by number. Each body carries an explicit "this was item
N on `claude/fork-register-reconcile`" note, and the new section states plainly that these three
are **older** than items 17 to 41 despite carrying higher numbers, because the number records
identity and not chronology.

### 4.1 The cross-reference hazard, which the renumbering created and nobody had flagged

Renumbering an item is not a local edit. Fork's retained text refers to its own items by number in
55 places, including inside item 15, which is itself retained. All 55 were repointed and audited
individually. Sub-labels moved with their parents: `18a` to `43a`, `18a(ii)` to `43a(ii)`,
`18a(iv)` to `43a(iv)`, `19a` to `44a`, `19b` to `44b`.

**One reference was deliberately NOT repointed.** Line 1386 of the fork input quotes commit
`54aa806` in quotation marks: *"Item 18's own failure mode recurred inside the fix for item 18"*.
Renumbering inside a quotation would falsify the quotation. It is left verbatim and a bracketed
clarifier was added after it.

Reading `54aa806` live to check the quotation surfaced a separate, pre-existing defect: the
commit's actual closing words are "because it is item 18's own failure mode **recurring** inside
the fix for item 18". The register renders it in quotation marks with the tense changed, so it is a
paraphrase presented as a quotation. **Flagged, not silently rewritten**, because fixing it is a
content edit outside this merge's decision set. Both forms are now recorded in the entry so a named
owner can decide. Note the irony is load-bearing rather than decorative: the entry is about
miscounting and misciting sources, and it miscites its own.

---

## 5. TWO ITEMS ROUTED IN FROM SIBLINGS

**5.1 `D6f` line-number drift, routed from d3-force on `claude/r8-force`.** Confirmed
independently before acceptance. `D6f` cites `failure_modes.py:127` for the `np.gradient`
construction. Live, `np.gradient` occurs **exactly once** in that file, at **line 129**. Stale by
two.

This **corroborates a known drift rather than being a new discovery**, and the corroboration is
from a separate origin: `claude/r5-research`'s `docs/R5_RESEARCH_FORCE_CONVERGENCE_2026-08-19.md:123`
(item W7) already records "`failure_modes.py:127-128` should be `:129-130`", written by a different
session about a different citation of the same construct. Read live from that branch, not relayed.

**NOT APPLIED IN THIS PASS, and this is a deliberate scope call.** `D6f` is an entry that is
byte-identical on both lineages, so it is outside the merge decision set, and editing it here would
mix a content correction into a merge whose whole value is that every non-contested entry is
provably unchanged. It should be applied as a separate one-line commit, by whoever owns the
register after this lands. Recorded here so it is not lost.

**5.2 Ledger item 16 is CLOSED, not open.** My dispatch prescribed it as work. It was closed by the
coordinator at **`cb13f88`** on `claude/add-ci-checks` and pushed, and `check_claims.py` Rule C6
now reads "9.80665 survives at exactly ONE site, and it is DEAD CODE", verified live at
`scripts/check_claims.py:151`. Recorded as done with its SHA rather than prescribed as work, which
is precisely the defect C6 itself had. `check_claims.py` is d1-safe's file and was not touched from
here.

---

## 6. TWO METHOD DEFECTS FOUND IN MY OWN PROCESS

**6.1 A comparison whose two arms both failed reported "SAME".** The first content probe used
`md5 -q`, which errored under this shell on both sides; both arms returned identically empty and
the probe reported six entries as identical, including `A6`, which is one of the most divergent
entries in the file. **A comparison must fail loudly when its inputs are unreadable, and a "SAME"
that two empty strings can produce is not a comparison.** This is the most dangerous shape on this
project, because it is exactly how a silent drop passes a verification step. Caught before it
reached a claim, and the comparison was redone in Python.

**6.2 An entry parser that swept trailing section headings into the last entry of each section.**
The first pass reported **12** contested entries. Five of them (`B8 D7a G16 H8 K4`) were artifacts:
those entries are last in their section on one lineage but not the other, so the parser attached
the following `## SECTION ...` heading to one copy and not the other. Ending an entry at the next
heading as well as at the next entry cut the real decision set from 12 to **7**.

Both defects have the same shape as the thing this register exists to prevent, which is why they
are recorded rather than quietly fixed: a measurement artifact that would have been published as a
finding.

---

## 7. WHAT I COULD NOT VERIFY

- **The substance of the 64 fork-only and 7 `add-ci-checks`-only entries.** They were carried in
  because they are additive and exist on exactly one lineage. Their claims were not re-derived
  against primary source in this pass. Merging is not auditing, and this document should not be
  read as certifying their content.
- **Whether items 42 to 44's evidence is reachable.** Item `44b` says so itself: the g128 evidence
  lives on branches that are not merged here, so those numbers are checkable only by someone with
  those branches. That caveat is retained in the entry.
- **Items 17 to 41's underlying runs.** Byte-identical passthrough from `add-ci-checks`. Not
  re-measured.
- **The `54aa806` tense discrepancy** is verified as a discrepancy, but I did not determine whether
  any other quotation in the register is a paraphrase presented as a quotation. That is a
  register-wide audit, not a merge task.

---

## 8. STATE

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` on `claude/r8-register` now holds the merged
register: 210 entries, letter-id union complete, numbered ids contiguous 1 to 44.

**This branch is not merged anywhere and has not been pushed.** A human decides where it lands.
The obvious question for whoever does is whether `claude/fork-register-reconcile` should be
retired once this is in, since its content is now wholly contained here under different item
numbers, and leaving it live invites a fourth lineage.
