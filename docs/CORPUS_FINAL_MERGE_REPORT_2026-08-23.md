> **ABSORBED 2026-08-25 into `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, the single
> corpus master.** This file is kept verbatim below and nothing in it was deleted or
> rewritten. Cite it only with its date, never as current: several of its counts (the
> 332-record index, the 27-metadata / 8-papers split, the open-item list) were measured
> before the 2026-08-25 ingest fix and are stale. The master carries the live figures and
> the current status of every open item.
>
> **NEAR-IDENTICAL NAME, DIFFERENT DOCUMENT.** `CORPUS_FINAL_MERGE_REPORT_2026-08-25.md`
> is a SEPARATE session report, not a revision of this one: the two share 9 unique non-blank
> lines out of 278 and 167, and 6 of those 9 are this banner (measured 2026-08-26). THIS file
> is the corpus-lineage, bounded-sweep and proposed-bibliography session. THAT one is the
> landing-plan, flag-collision and terminal-merge session. Read both, or read neither and
> read the master instead.

---

# Corpus final merge, session report

**2026-08-23, on `claude/add-ci-checks`, base `badd5a2`.** One section per dispatch phase, each
ending DONE, BLOCKED (blocker named) or OPEN. Section 7 lists every place the dispatch's own
stated facts turned out to be wrong.

**Provenance key.** `[READ]` I ran the command or read the page this session. `[INFERRED]`
computed from something tagged `[READ]`. `[RELAYED]` came from another document or a tool
summary and was NOT re-derived against a primary source.

---

## Step zero, environment

`Josephines-MacBook-Air.local`, `/Users/josie/can-it-ford`, branch `claude/add-ci-checks`
`[READ]`. **440 commits ahead of `origin/main`** `[READ]`. `origin/main` tip
`c7f0a16ace0bf2f34b51f98bffde0c6bda33c00f` `[READ]`. Nothing was merged into `main`.

**DONE.**

---

## Phase 1, corpus lineage ground truth

All three named files exist `[READ]`:

| file | mtime | size |
|---|---|---:|
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | 2026-08-20 14:42 | 22,746 B |
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` | 2026-08-21 01:09 | 20,296 B |
| `docs/CORPUS_MERGE_FINAL_2026-08-22.md` | 2026-08-22 02:48 | 65,030 B |

**Reachability: every corpus-lineage commit is on the pushed integration branch.** `fc8d278`,
`6b894bf`, `e9e80ad`, `7bc8c62`, `88672a0`, `6778913`, each confirmed contained in
`origin/claude/add-ci-checks` by `git branch -a --contains` `[READ]`. None is local-only.

**08-20 vs 08-21: pass 2 was built by READING pass 1, not independently re-derived** `[READ]`.
Its own header says "Supersedes `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md`" and its
section 1 is "THE DIFF: what pass 1 got wrong, what it missed, what survived", enumerating six
named pass-1 errors. **The DOI accounting therefore did not silently diverge**, which is the
specific risk the dispatch raised.

**The Aug 22 reconciliation did run.** `docs/PRIOR_DISPATCH_VERIFICATION_2026-08-22.md`
(23,149 B) and `docs/CLAUDE_MD_OPEN_ITEMS_STATUS_2026-08-22.md` (29,128 B) both exist, plus
`docs/PRIOR_REPORTS_CONFIRMATION_2026-08-22.md` `[READ]`.

**Branch-push scan: 24 of 114 local branches have no `origin/` counterpart** `[READ]`. The
three the dispatch named are **all pushed**: `claude/r9-gapscan` `5213f6f` (merged into HEAD),
`claude/r9-reader` `9c19364` (merged into HEAD), `claude/r9-corpus-bib` `de18180` (pushed, NOT
merged, deliberately, per `CORPUS_MERGE_FINAL_2026-08-22.md` section 7) `[READ]`.

**DONE.** The proposed root cause is refuted; the real structure is two document lines, not one.

---

## Phase 2, bounded sweep

`find -maxdepth 3 -newer docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` `[READ]`:

- `~/Desktop`: **2 hits.** `SNAPSHOT_CONSOLIDATION_DRYRUN.md` (2026-08-22 13:10, 66,276 B), a
  read-only redundancy analysis of nine archive snapshots. `WORKING_TREE_AND_DOWNLOADS_SCAN.md`
  (2026-08-22 14:20, 12,620 B), a read-only git-status and Downloads metadata scan. **Neither
  is research corpus material.** Neither is folded in beyond being named.
- `~/Documents`: **0 hits.**
- **No `SENSITIVE_DO_NOT_SHIP`-pattern file appeared in either sweep** `[READ]`.

**D10 cross-slope: already analyzed, and it is not cross-slope data.** Register **D22** covers
`~/Documents/CANITFORD_D10_CROSSSLOPE_2026-08-14/` in full, verifies all eight SHA256 checksums,
and finds `g_vec[1]` (lateral) **exactly 0.0 in all eight runs**, so no lateral tilt was ever
applied and the set is a longitudinal grade sweep at S = 0, 0.02, 0.06 `[READ]`. It appears in
**0 of the 3** corpus-lineage files `[READ]`, which is why a corpus-only check reports it
unanalyzed. It is register material and correctly filed there.

**The genuinely new material was not on the filesystem at all.** It was six completed Undermind
deep searches sitting upstream and mirrored nowhere. See Phase 6.

**DONE.**

---

## Phase 3, the higher-value corpus

`00_CATALOGUED_BUT_NEVER_CITED_README_2026-08-14.md` (4,940 B) and its data file
`00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv` (48,740 B) both exist `[READ]`.

**The 138-DOI table has ALREADY been folded in, comprehensively.**
`docs/CORPUS_MERGE_FINAL_2026-08-22.md` is a 65 KB accounting of all 138 with a per-DOI
appendix, a Scholar Sidekick title audit, and a second-eyes pass. Register **G25** and **G25a**
carry the triage of the nine multi-report papers and two catalogue defects `[READ]`. Nothing
needed re-folding.

### Item 1, which DOI has the top report support

**`10.1016/j.cma.2022.114809`.** Re-parsed live from the source TSV, field 6 `[READ]`:

| DOI | TSV `in_reports` | index `n_reports` |
|---|---:|---:|
| `10.1016/j.jcp.2016.10.064` | **4** | **5** |
| `10.1016/j.cma.2022.114809` | **4** | **5** |
| `10.1007/s00466-019-01783-3` | 2 | 3 |

**Exactly two of the 138 reach the maximum, with identical report sets.**
`10.1007/s00466-019-01783-3` is strictly below both, so it is not the co-equal.

**The count is instrument-dependent; the ranking is not.** TSV 4, index 5, the extra being
`mpm-verification` `[READ]`. Quote the ranking, never a bare count.

**Corroboration, from separate origins:** register G25's independent content triage rates
`10.1016/j.cma.2022.114809` item (b) YES, and `CORPUS_MERGE_FINAL_2026-08-22.md` section 4
item 6 had already written "IFEMP, 4 reports, the joint top-ranked gap" `[READ]`.

### Item 1, the same-paper hazard

**Checked and it is a different, worse problem.** `10.1016/j.cma.2022.114965`, attributed to
"Qian et al. 2022, water entry of a half-buoyant cylinder", **resolves to an unrelated
phase-field crack-propagation paper** and was flagged as fabricated on 2026-08-14 in
`docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md` `[READ]`. It appears **nowhere in `paper/`**,
and there is **no standalone Qian bib entry**; earlier "qian" grep hits are the substring
inside **Xia Junqiang** `[READ]`. The fabricated DOI never reached the bibliography.
`10.1016/j.cma.2022.114809` (Li, Lian and Zhang, IFEMP) is a different, real, title-verified
paper.

### Item 2, submission status

**OPEN and unconfirmed.** `docs/CLAUDE_MD_OPEN_ITEMS_STATUS_2026-08-22.md` item 7 reads
"nothing confirms either submission", and records affirmative evidence against "final and
submitted" `[READ]`. **On that basis NO `.tex` file was touched.** The bibliography addition
is proposed as a reviewable diff in section 8 below, not committed.

**DONE.**

---

## Phase 4, the terminal merge

`docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` written, 305 lines `[READ]`. It states what it
supersedes and what it does **not** (the `CORPUS_MERGE_FINAL_2026-08-22.md` line is separate
and remains authoritative on the 138), folds in Phase 2 and Phase 3, and carries forward nine
named unresolved items including the competing coupling-defect mechanisms and the report-count
instrument disagreement.

SUPERSEDED banners added at the top of both dated files, content otherwise untouched `[READ]`.

Source-of-truth ranking updated in **`CLAUDE.md`** (one block under "Corrections authority",
per that file's own rule that a dated finding goes in `docs/` and gets a line here only when it
changes a standing rule) and in the **corrections register** as **G25b**, both in the same
commit.

**DONE.**

---

## Phase 5, implement rather than document

| action | status |
|---|---|
| Six unmirrored deep searches written to `data/deep_searches/`, `MANIFEST.json` 21 -> 27, index rebuilt | **IMPLEMENTED** this commit |
| Newly surfaced coupling DOIs in a `.bib` or Overleaf | **NOT IMPLEMENTED, deliberately.** Blocked by Phase 3 item 2; proposed as a diff in section 8 |
| Register G25 marked closed, and is that true | **NOT APPLICABLE as posed.** See below |
| `check_claims.py` banned-phrase list needs updating | **NOT APPLICABLE.** See below |
| Shipped bibliography retraction and fabrication audit | **IMPLEMENTED** this commit, as register G25c |

**G25 is not, and should not be, marked closed.** It is also not "the 138 uncited DOIs" item:
it triages the **nine multi-report subset**, and its stated falsifier is a live re-parse test
which was re-run on 2026-08-22 and **did not fire** (205 rows, 138 uncited, 9 multi-report)
`[READ]`. Its own conclusion is "Neither is established here. Both are hypotheses with a named
primary source and a distinguishing test." **An open hypothesis correctly stays open.** It was
extended, not closed, by G25b.

**No banned-phrase update is warranted.** Nothing was settled this session that a phrase guard
could enforce. The two candidate mechanisms remain undiscriminated, and the strongest new claim
is `[RELAYED]` and explicitly unverified. Adding a guard for an unverified claim would be the
error the guard exists to prevent.

**The bibliography audit closed a named open item.** `CORPUS_MERGE_FINAL_2026-08-22.md` section
4 item 11 called it "a one-call job and the obvious next use of this instrument". Run against
the 15 entries of `overleaf/main:can_it_ford_references_IEEE.bib`: **9 of 9 DOI-bearing entries
`matched` at high confidence, 0 mismatch, 0 ambiguous, 0 not_found, 0 retracted, 0 corrections,
0 concerns** `[READ]`. **Scope: 9 of 15, not 15 of 15.** Six entries carry no DOI in any field
and could not be audited by identifier.

**A tooling defect found while landing the searches.** `research_index.py` resolves searches as
`idx.get("deep_searches") or load_deep_searches()`, so a non-empty index list short-circuits
the directory read. New JSONs are **inert until `--build`** `[READ]`: 0 grep hits through
`--searches` before the rebuild, 5 after. Recorded so the next session does not repeat it.

**A destructive-action check that mattered.** `--build` silently writes a **smaller** index and
exits 0 when its `REPORTS` paths are unreadable, per that function's own docstring, and 7 of 8
live under `~/Downloads`. All 8 were confirmed present and a pre-build backup was taken before
rebuilding `[READ]`. **332 papers before, 332 after.**

**DONE.**

---

## Phase 6, Undermind

**The dispatch's gate was a false dichotomy and the answer is "both".** Undermind is **NOT in
`/Users/josie/can-it-ford/.mcp.json`**, which holds 6 servers: `canford-corpus`,
`canford-tacc`, `deepwiki`, `scite`, `wandb`, `wolfram` `[READ]`. It **IS live** as a session
connector, verified by `get_orientation` returning the connected account `[READ]`. So the
searches were run rather than written out.

**Query 1, partial-submersion pressure-offset mechanism: ALREADY RUN, 2026-08-21 22:51**, in a
form more detailed than the dispatch's, as "Grid-converged force deficit in partially submerged
free-rigid MPM coupling", **completed, 37 relevant papers** `[READ]`. It was not re-run.
Finding: a discrete interface/transfer bias, not a universal hydrostatic offset, and
**no cited paper directly documents a grid-converged underforce from grid-mass-averaged
velocity assignment**. Its 6th-ranked paper is `10.1016/j.cma.2022.114809`, which is how the
Phase 3 answer was independently corroborated.

**Query 2, verdict-invariant but magnitude-non-monotone grid convergence: LAUNCHED AND
COMPLETED this session**, 77 relevant papers `[READ]`. It returns a concrete four-step ordered
diagnostic: separate coupling from discretization first (a persistent 25 to 30 percent deficit
is model-form error, not resolution); then isolate MPM error, noting that at fixed
particles-per-cell smaller cells mean more crossings so error can **increase**; then remove
transient contamination and converge time-averaged or event-based observables rather than one
final displacement; then treat three non-monotone values as **diagnostic, not GCI data**, since
Richardson/GCI assumes an asymptotic error model.

**Query 3, git workflow for consolidating unpushed branches: NOT RUN, and deliberately.**
Undermind searches the **scholarly literature**. Git branch-consolidation practice is not a
research literature question, and a deep search on it would return noise while consuming a
search slot. Running it would have been a category error dressed as compliance. The question is
answered directly from measured local state instead: **24 of 114 local branches unpushed**,
listed in `MERGED_RESEARCH_READER_CORPUS_FINAL.md` section 6, with
`claude/credential-exposure-2026-08-13-DO-NOT-PUSH` flagged as one that **must stay unpushed**
because the repo is public.

All six searches are saved under `data/deep_searches/` rather than `docs/undermind/`, because
that is where this repo's 21 existing search records already live and where
`research_index.py --searches` and `--source-audit` look. Putting them in a new directory would
have made them invisible to the project's own tooling.

**DONE.**

---

## 7. Where the dispatch's stated facts were wrong

Every item below was stated as fact or strong presumption in the dispatch and is corrected
against live state.

1. **"whether a single authoritative merged corpus reader has ever actually been produced".**
   One has, twice over. `MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` is an explicit
   supersession of the 08-20 pass, and `CORPUS_MERGE_FINAL_2026-08-22.md` is a 65 KB terminal
   accounting of the 138. **The problem was never that no merge existed. It was that two
   different document lines were being read as one.**
2. **`docs/CORPUS_MERGE_FINAL_2026-08-22.md` framed as possibly absent.** It exists and is the
   **largest and most thorough** of the three, larger than the other two combined.
3. **"the branch-push situation ... is likely the actual root cause".** Refuted. Every
   corpus-lineage commit is reachable from `origin/claude/add-ci-checks`.
4. **"check whether r9-gapscan, r9-reader, and r9-corpus-bib are in that unpushed list".** None
   is. All three are pushed; two are merged into HEAD; the third is unmerged by a documented
   decision.
5. **"the DOI accounting may have silently diverged ... if it was re-derived rather than
   extended".** It was extended, with a named six-item diff. No silent divergence.
6. **"`CANITFORD_D10_CROSSSLOPE_2026-08-14/` (cross-slope/camber run data, previously found but
   never analyzed)".** Wrong twice. It **was** analyzed, in full, as register D22. And it is
   **not cross-slope data**: the lateral gravity component is exactly 0.0 in all eight runs, so
   the directory name describes an experiment that was never run.
7. **"Confirm live which DOI actually has 4-independent-report support".** The DOI is
   `10.1016/j.cma.2022.114809`. But **"4-independent-report" is itself a mis-framing**: the
   reports are four deep searches by one retrieval system, so they are a relevance signal, not
   four independent sources. And **the count is 4 by the catalogue TSV and 5 by the built
   index**, so a bare "4" cannot be quoted without its instrument.
8. **"whether either is actually the same paper as the Qian et al. 2022 cma.2022.114965-class
   citation already in the coupling writeup".** The premise fails: `10.1016/j.cma.2022.114965`
   is a **known fabricated attribution**, flagged 2026-08-14, and it is **not in the coupling
   writeup, not in `paper/`, and not in any `.bib`**. There is no Qian entry anywhere; the grep
   hits are the substring inside "Junqiang".
9. **"Check whether Undermind is wired in `.mcp.json`. If yes ... If Undermind is not wired
   locally, do not attempt to fake it."** False dichotomy. It is **not** in `.mcp.json` and
   **is** live as a session connector. Under a literal reading of the gate the phase would have
   been skipped with working tooling in hand.
10. **Phase 6 query 1 presented as work to be done.** It had already been run on 2026-08-21, in
    a more detailed form, and had completed with 37 papers. Re-running it would have duplicated
    a completed search.
11. **"Pull the corpus's own recommended-actions section (if either lineage file has one)".**
    Neither dated file carries one. The actionable open-items list lives in the **other** line,
    `CORPUS_MERGE_FINAL_2026-08-22.md` section 4, with 13 numbered items.
12. **"Is register item G25 (138 uncited DOIs) marked closed".** G25 is not the 138 item; it
    triages the **nine multi-report subset**. It is not marked closed, and correctly so: it
    holds two competing hypotheses with a stated distinguishing test.

**And one of my own, recorded to the same standard.** I hypothesised that the reader-facing
citation count moving from 43 to 107 was `CORPUS_MERGE_FINAL_2026-08-22.md`'s 138-DOI appendix
inflating the metric, the same class as the `Dynamic_Vehicle_Traction_in_Floodwater.md` dump.
**Measured: 0 of the 107 are reader-facing only via that file** `[READ]`. **The hypothesis is
refuted.** The growth is real, from absorbed r9/r10 merges.

---

## 8. Proposed, NOT committed: bibliography additions for review

Blocked by Phase 3 item 2 (submission status unconfirmed). **No `.tex` was touched.** These are
seven coupling-mechanism DOIs that currently appear in **zero** files anywhere in the repo
`[READ]`, surfaced by the three load-transfer searches. They are offered for a human decision,
not added:

```
10.1016/j.jcp.2019.03.049     Hyde & Fedkiw 2019, JCP 390:490-526. Monolithic solid-fluid
                              coupling of sub-grid and resolved solids. THE paper the
                              "velocity averaging is not coupling" claim rests on. UNREAD,
                              closed access.
10.1145/3197517.3201345       Akbay et al. 2018, TOG. Extended partitioned method for
                              CONSERVATIVE solid-fluid coupling. Named as the corrective
                              formulation. UNREAD.
10.1145/3687959               Chen et al. 2024, TOG. Solid-Fluid Interaction on Particle Flow
                              Maps. Impulse-to-velocity transfer. PDF AVAILABLE, unread.
10.1145/3197517.3201309       Gao et al. 2018, TOG. Momentum exchange through two MPM
                              background grids. Portable to a pressureless MPM.
10.1016/J.COMPGEO.2021.104069 Nakamura et al. 2021, Computers and Geotechnics. Particle-to-
                              surface frictional contact for MPM via weighted least squares.
10.1016/j.jcp.2017.02.050     Jiang, Schroeder & Teran 2016, JCP. APIC. Angular-momentum-
                              conserving particle-grid transfer. PDF AVAILABLE.
10.1145/3386569.3392438       Fang et al. 2020, TOG. IQ-MPM, interface quadrature.
```

**One of these was read in full and the read argues AGAINST a related adoption.**
`10.1016/j.jcp.2017.06.047` (Nangia et al. 2017, moving control volume for hydrodynamic forces
and torques) is ranked by the searches as a way to get force and torque without noisy surface
derivatives. Read directly `[READ]`: its Eq. (16) and Eq. (19) **both retain the pressure
term**, and the authors state "We do not analyze such expressions in this work, however"
about the pressure-free alternative (Section 1, page 2). It also considers **only neutrally
buoyant, fully immersed bodies** ("We consider only neutrally buoyant bodies to simplify the
implementation", Section 2.1, page 3), with **no free-surface, floating or partially submerged
case**. **It therefore cannot bear on this project's partial-submersion deficit and is a
contrast citation, not a fix.**

`10.1016/j.cma.2022.114809` is **not** in this list because it is already present in 10 repo
documents. What it needs is **acquisition**, not a citation entry, and it is closed access at
USD 41.95 with no PDF by any route available here.

**OPEN**, pending a human decision on submission status.

---

## 9. Definition of done

- `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` exists and is the single authoritative reader
  pointer. **DONE**
- Both dated predecessors carry a SUPERSEDED banner, content otherwise intact. **DONE**
- This report exists with one section per phase. **DONE**
- Explicit list of wrong dispatch facts. **DONE**, section 7, twelve items plus one of my own.
- Nothing merged into `main`; no force push; no `git add -A`; no `.tex` touched. **DONE**
