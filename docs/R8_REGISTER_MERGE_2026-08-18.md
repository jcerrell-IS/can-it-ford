# R8 REGISTER MERGE, 2026-08-18

Merge of `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` across two divergent lineages.
Slot d7-register, branch `claude/r8-register`. Nothing here is merged anywhere else; a human
decides where this lands.

Every count below is enumerated by a script that prints the entry identifiers it counted, not
asserted. **No verification in this document is based on a line count.** Reproduce with
`scratchpad/verify.py`, or re-derive from the two input blobs named in section 1.

---

## 0. WHY THIS WAS NOT A `git merge`, IN ONE EXAMPLE

Entry `G4b` carries measured comparanda from Shu et al. 2011, a spring-balance measurement of
tyre friction on wet carpet:

> **Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68.**

**Those three numbers exist on `claude/add-ci-checks` only.** `claude/fork-register-reconcile`'s
`G4b` is longer, better sourced and newer, and it does not contain them. A merge that took the
richer side of each contested entry, which is the obvious and defensible heuristic, drops them
without a conflict, without a warning, and without anything in the resulting file hinting that a
measurement used to be there.

This project already had the warning in the abstract: the Round 7 ledger's "a clean zero-conflict
merge that silently drops 126 lines". `G4b` is that warning with named numbers attached. It is the
answer to anyone who asks why this needed eleven judgement calls instead of one command, and it is
why the decision set had to be worked entry by entry against both sides rather than by picking a
winning lineage.

The same shape, one level up, is the identifier collision in section 4: a concatenation that
returns exactly the arithmetically-expected size would contain two item 17s, two item 18s and two
item 19s, and would pass every size check anyone thought to apply.

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
| `claude/add-ci-checks` | `59234f9`, then `785650b` | `124dd74` throughout |

`merge-base(add-ci-checks, fork-register-reconcile)` is `1a868f3`.
`git log --merges 1a868f3..claude/add-ci-checks` is empty, so no merge had happened.
`fork-register-reconcile` is **not** an ancestor of `add-ci-checks`.

**THE TARGET BRANCH MOVED TWICE DURING THIS WORK AND THE MERGE BASE NEVER DID.** The dispatch
recorded the public register at `de191b8` / 1644 lines; that was already stale on arrival. The
branch then went `59234f9` and then `785650b`. **At every one of those tips the register blob was
`124dd74`**, identical to the base this merge started from and identical to
`git hash-object` on the working file, two methods agreeing. So none of the movement touched the
register and no rebase was needed. Re-derived at each step, never assumed.

That is luck rather than a guarantee, and it is exactly why section 9.2 makes re-checking that one
blob the first gate before this lands. Note also that `origin/claude/add-ci-checks` was at
`59234f9` while the local branch was at `785650b`, so "the public copy" and "the branch" were not
the same thing during this work; section 9.4 carries the consequence for pushing.

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

**THE RULING WAS MADE ON PRINCIPLE AND IS ALSO CONFIRMED BY A COUNT, WHICH IS THE STRONGER
JUSTIFICATION.** The direction was chosen because the `add-ci-checks` numbering is public and
cited. Measuring afterwards showed it is also the cheaper direction by a wide margin:

| lineage | references to its own items 17, 18, 19 |
|---|---:|
| `claude/fork-register-reconcile` | **55**, across 26 lines |
| `claude/add-ci-checks` | **0** outside their own definitions |

So renumbering the fork side costs 55 in-file edits, all of them mechanical, all auditable in one
diff. Renumbering the public side would have cost an unknown number of edits to citations **outside
this file and outside this repo's control**, including `CLAUDE.md` and anything already written
against the pushed SHA. A bounded, countable cost against an unbounded, uncountable one. **No
`add-ci-checks` text was touched at all.**

This is worth stating plainly because "keep the public numbering" is a principle that could have
been wrong in a different distribution of cross-references. Here it was not: the count and the
principle agree, and the count is checkable.

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

## 5. ITEMS ROUTED IN, AND ONE OPEN DEFECT HANDED OUT

### 5.1 `D6f` line-number drift, routed from d3-force on `claude/r8-force`

Confirmed
independently before acceptance. `D6f` cites `failure_modes.py:127` for the `np.gradient`
construction. Live, `np.gradient` occurs **exactly once** in that file, at **line 129**. Stale by
two.

This **corroborates a known drift rather than being a new discovery**, and the corroboration is
from a separate origin: `claude/r5-research`'s `docs/R5_RESEARCH_FORCE_CONVERGENCE_2026-08-19.md:123`
(item W7) already records "`failure_modes.py:127-128` should be `:129-130`", written by a different
session about a different citation of the same construct. Read live from that branch, not relayed.

**HELD OUT OF THE MERGE DELIBERATELY, THEN APPLIED SEPARATELY AS `ce1cca8`.** `D6f` is
byte-identical on both lineages, so it is outside the merge decision set. Folding a content fix
into `704b6b8` would have silently converted a verifiable merge into an unverifiable one: a reader
could no longer tell which differences were merge decisions and which were edits. The ordering is
the deliverable, so **`ce1cca8` must never be squashed backwards into `704b6b8`.**

**THE FIX IS TWO SITES, NOT ONE, AND THAT IS WHY BOTH SURVIVED.** The routing named `D6f` only. A
grep of the merged register for the same construct found a second stale citation with different
provenance:

| entry | was | now | provenance |
|---|---|---|---|
| `D6f` | `failure_modes.py:127` | `:129` | byte-identical on both lineages; the routed one |
| `D8` | `failure_modes.py:127-128` | `:129-130` | fork-only entry |

Live: `:129` is `accel = np.gradient(vel, t, axis=0)`, `:130` is `force = mass_kg * accel`.

**`D8`'s `:127-128` form is exactly what W7 named.** So W7 and the d3-force routing were pointing
at two *different* sites of one defect. Each report therefore looked already-known to the other,
which is precisely how both stayed live. Fixing only the routed site would have left the identical
defect one entry away from the one being corrected. `ce1cca8` changes exactly 2 lines and leaves 0
residual `:127` citations.

### 5.2 Ledger item 16 is CLOSED, not open

My dispatch prescribed it as work. It was closed by the
coordinator at **`cb13f88`** on `claude/add-ci-checks` and pushed, and `check_claims.py` Rule C6
now reads "9.80665 survives at exactly ONE site, and it is DEAD CODE", verified live at
`scripts/check_claims.py:151`. Recorded as done with its SHA rather than prescribed as work, which
is precisely the defect C6 itself had. `check_claims.py` is d1-safe's file and was not touched from
here.

### 5.3 OPEN DEFECT, NOT FIXED HERE: a paraphrase presented as a quotation in item 43

**This is stated in full so it can be fixed without re-deriving it.**

Item **43** (formerly item 18 on `claude/fork-register-reconcile`) quotes commit **`54aa806`**
inside quotation marks, introduced with the words "in its own words". The two texts differ:

| | text |
|---|---|
| **register says** | "Item 18's own failure mode **recurred** inside the fix for item 18" |
| **`54aa806` actually says** | "because it is item 18's own failure mode **recurring** inside the fix for item 18" |

Read live from the commit body, not relayed. The tense is changed and the sentence is
re-capitalised and clipped, so it is a paraphrase wearing quotation marks.

**Not fixed here, for the same reason `D6f` was held out of the merge**: item 43's body is
otherwise a verbatim carry from `fork-register-reconcile`, and editing its prose inside the merge
would break the property that lets a reader verify the carry. It also is not a line-number slip
that a follow-on commit disposes of in two lines; it is a wording judgement about someone else's
entry.

**Why it matters more than it looks.** Item 43 is *about* miscounting and misciting sources, and
its own fix already miscited its evidence at `43a(ii)`. This makes the entry's third recurrence of
its own failure mode, and the entry already says "a correction is not exempt from the defect it
corrects". Whoever owns that entry should either restore the verbatim wording or drop the
quotation marks and attribute it as a paraphrase. **Both forms are recorded above, so no further
digging is needed.**

---

## 6. THREE METHOD DEFECTS FOUND IN THIS PASS, TWO OF THEM MINE

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

**6.3 `register_integrity.py` silently graded a different file than the one I was holding.** Its
`--register` default is built from the repo root, so run from a worktree it checks the **main
checkout's** register regardless of which file you are editing. Its first run here reported "0
blocking defects" for a file this branch had not touched. Caught because a cited hex token it
warned about sat at line 1877 in the main checkout and line 2607 in mine. The passing result quoted
in section 8 is from an explicit
`--register .claude/worktrees/<wt>/docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.
**Anyone running that checker from a worktree must pass `--register` explicitly, or they are
grading someone else's file.**

All three have the same shape as the thing this register exists to prevent, which is why they are
recorded rather than quietly fixed: a measurement artifact that would have been published as a
finding. 6.1 and 6.3 are the *same* underlying failure, a check that reports success while
measuring the wrong thing or nothing at all. 6.2 is the distinct one: a real measurement of a real
file, whose *unit* was wrong.

**6.1 IS AN INSTANCE OF A REPO-WIDE PATTERN, NOT A ONE-OFF.** Three tools failed this way in one
night: this `md5` probe; d6-tooling's `while`-read subshell losing `PATH`, so `git` and `shasum`
were both command-not-found and 17 comparisons of two empty strings printed `OK`; and the
coordinator's own board row claiming "verified no respawn" from a six-second window. **A comparison
whose both arms failed, reported as agreement.** d6-tooling owns the consolidated method note since
it owns tooling, and the `md5` instance is named there. Recorded here too because the register is
where this project's method rules live.

---

## 7. WHAT I COULD NOT VERIFY

- **THE SUBSTANCE OF THE 64 FORK-ONLY AND 7 `add-ci-checks`-ONLY ENTRIES. MERGING IS NOT AUDITING.**
  This is the most important caveat in the document and it should stay attached to any citation of
  the 210 figure. Those 71 entries were carried in **because they are additive and exist on exactly
  one lineage**, which is a statement about provenance, not about truth. Their claims were not
  re-derived against primary source in this pass. **A merged register is a complete register, not a
  verified one**, and this document certifies only that nothing was lost, not that anything is
  right. Three of the entries it does touch, `A2`, `A6` and `G7`, each turned out to contain
  something false or stale once actually checked, at a rate that should discourage anyone from
  reading the untouched 71 as sound.
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

`claude/r8-register` carries two commits, and **the order is load-bearing**:

| commit | what | why separate |
|---|---|---|
| `704b6b8` | the merge: 210 entries, letter-id union complete, numbered ids contiguous 1 to 44 | every non-contested entry provably byte-identical to its source |
| `ce1cca8` | `D6f` and `D8` citation fix, `:127` to `:129` | a content fix, held out so the merge stays verifiable |

**`ce1cca8` MUST NOT BE SQUASHED INTO `704b6b8`.** Squashing them destroys the only property that
makes the merge auditable, because a reader can then no longer separate merge decisions from
edits. If a rebase or squash is ever proposed for this branch, this is the reason to refuse it.

Not pushed. Not merged. `origin` has no `claude/r8-register`.

---

## 9. LANDING PLAN

Written for someone who was not here. **Do not treat any SHA below as current; every one of them
moves.** The instruction is the procedure, not the numbers.

### 9.1 Where it should land

**`claude/r8-register` should merge into `claude/add-ci-checks`**, which is what it branched from
(`0efe4f3`), and which is the lineage whose numbering this merge deliberately preserved.
`claude/add-ci-checks` then reaches `main` by whatever route Josie chooses for it; that is a
separate decision and this branch does not depend on it.

It should **not** be merged into `main` directly. `origin/main`'s register is the 656-line
ancestor of both inputs, and landing there first would leave `add-ci-checks` holding a register
that is simultaneously behind on content and ahead on commits.

### 9.2 What must be re-verified AT THE MOMENT OF MERGING, not now

`claude/add-ci-checks` moved twice while this work was in progress: `59234f9`, then `785650b`.
**Both times the register blob stayed `124dd74`**, so the merge base never actually moved. That is
luck, not a guarantee, and it is the thing to check.

```
# 1. THE ONE THAT DECIDES EVERYTHING: has the register moved on the target?
git -C <repo> rev-parse claude/add-ci-checks:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
#    == 124dd74  -> this merge is still valid, proceed
#    != 124dd74  -> STOP. Someone edited the register on the target branch. The
#                   merge must be re-derived; do not resolve it by hand.

# 2. Has the fork side moved off the tip this merge consumed?
git -C <repo> rev-parse claude/fork-register-reconcile      # was c1235e5
#    moved -> new fork content exists that is NOT in this merge. Re-run section 2's
#             enumeration against the new tip before landing.
```

### 9.3 How to verify the landing, and how NOT to

**Verify by entry, never by line count.** A concatenation that returns exactly the expected size
would contain two item 17s and pass a size check (section 4). After merging, the register must
show:

- **210 entries**: 166 letter-ids and 44 numbered.
- Letter-id set equal to the union of both inputs: nothing lost, nothing invented.
- Numbered ids **contiguous 1 to 44**, no duplicates. `git grep -n '^[0-9]\+\. ' <file>` and check
  for a repeated number is the cheap version of this.
- `register_integrity.py` **with an explicit `--register` path** (section 6.3), 0 blocking defects.

### 9.4 Two decisions for a human, which I am not making

1. **Retire `claude/fork-register-reconcile` once this lands.** Its register content is now wholly
   contained here, under different item numbers for three items. Leaving it live invites a fourth
   lineage and a second collision, and the next person to "reconcile the register" will find two
   plausible sources again. Retiring it is a branch deletion, which is irreversible-ish on a public
   repo, so it is Josie's call and not mine.
2. **Pushing is a separate authorisation.** The repo is public, `origin/claude/add-ci-checks` is
   currently behind its local branch, and `.git/hooks/pre-push` requires `PUSH_OK=1`. Nothing here
   should be pushed as a side effect of landing it locally.

### 9.5 The one thing that would silently undo this work

Someone running a plain `git merge claude/fork-register-reconcile` into `add-ci-checks` at any
point after this lands. It will report zero conflicts, because the lineages edit disjoint regions,
and it will reintroduce the duplicate item 17/18/19 numbering that section 4 exists to resolve. If
that merge is ever proposed, the answer is that it has already been done, here, by entry.
