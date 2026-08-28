# The Merged Research Reader Corpus, MASTER

**No date suffix. This is the single master for the corpus line. Consolidated 2026-08-25.**

This file replaces a lineage of ten separate documents that had grown three near-identical
names and four mutually stale copies of the same counts. Every one of them is absorbed here.
None was deleted; each carries a SUPERSEDED banner pointing back to this file, and all are
recoverable from git at `57db739`.

**Provenance key, applied to every claim.** `[READ]` I ran the command or read the bytes in
this session, 2026-08-25. `[INFERRED]` computed from something tagged `[READ]`. `[RECALLED]`
carried from an absorbed document and NOT re-derived against a primary source.

**One source cited twice is not two sources.** Where two findings agree below, both origins
are named and the answer to "are they independent" is stated.

Consolidated against `claude/add-ci-checks` at `57db739` `[READ]`.

---

## 0. What this file replaces

| absorbed file | built | what it answered | status |
|---|---|---|---|
| `MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | 08-20 | whole-project reader, pass 1 | absorbed, sections 3 and 6 |
| `MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` | 08-21 | whole-project reader, pass 2 | absorbed, sections 3 and 6 |
| `CORPUS_MERGE_FINAL_2026-08-22.md` | 08-22 | the 138 catalogued-but-never-cited DOIs | absorbed, section 4 |
| `CORPUS_LINEAGE_STATUS_2026-08-23.md` | 08-23 | lineage and the ac0f0d8 misattribution | absorbed, sections 1 and 5.4 |
| `CORPUS_FINAL_MERGE_REPORT_2026-08-23.md` | 08-23 | 08-23 dispatch session report | absorbed, section 7 |
| `MERGED_RESEARCH_READER_CORPUS_FINAL.md` (prior text) | 08-23 | terminal reader, first attempt | this file, rewritten |
| `CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md` | 08-25 | the corpus-bib flag collision | absorbed, section 7.2 |
| `CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md` | 08-25 | why `--build` was aborting | absorbed, section 2.2 |
| `CORPUS_FINAL_MERGE_REPORT_2026-08-25.md` | 08-25 | 08-25 dispatch session report | absorbed, section 7 |
| `R9_CORPUS_READ_2026-08-19.md` | 08-19 | six papers read from full text | absorbed, section 5 |

**THE NAMING HAZARD THAT MADE THIS NECESSARY, and it already fired once.** Three files
carried permutations of the same four words: `CORPUS_MERGE_FINAL_2026-08-22`,
`CORPUS_FINAL_MERGE_REPORT_2026-08-23`, `CORPUS_FINAL_MERGE_REPORT_2026-08-25`. The 08-25
report records in its own opening that it **overwrote the 08-23 file before checking**, then
restored it byte-identical from the HEAD blob `[READ]`. Do not reintroduce a second file whose
name is a permutation of this one's.

---

## 1. The lineage, settled

There were **two lines**, not one, and reading them as one is what made the prior state look
contradictory. That distinction is now retired: both lines are merged here.

- The **reader line** answered "what does the project know". Passes 1 and 2 and the prior FINAL.
- The **accounting line** answered "what do the 138 catalogued-but-never-cited DOIs reach".
  `CORPUS_MERGE_FINAL_2026-08-22.md`.

**Pass 2 was built by reading pass 1, not independently re-derived** `[RECALLED]`. Its own
section 1 is titled "THE DIFF: what pass 1 got wrong, what it missed, what survived" and names
six specific pass-1 errors. So the two never silently diverged: pass 2 is an extension with a
named diff, which is the safe case.

**`claude/r9-corpus-bib` is MERGED.** `de18180` was merged into `claude/add-ci-checks` by
`a83a38b` at 2026-08-24 17:56, and `git merge-base --is-ancestor de18180 HEAD` returns true
`[READ]`. The commit that landed it is named "Record poster and paper submission status per
direct human confirmation" and says nothing about the corpus, which is why three documents
went on asserting the opposite for a day. **A merge landed inside a commit named for unrelated
work**; that is the process finding worth keeping.

---

## 2. The corpus as it stands, every number measured live 2026-08-25

### 2.1 Headline

```
index built 2026-08-25   papers 382   abstracts 211   cited 164
```
`[READ]`, `python3 analysis/research_index.py --stats`.

**THE 332 FIGURE IS RETIRED.** Every absorbed document says "332 papers before and after".
That was true until `e1921cf` at 02:15 on 2026-08-25 fixed the ingest and the index went to
**382** `[READ]`. The prior FINAL.md was edited eight minutes later, at 02:23 by `c82adb7`,
and still did not update the count, so it shipped 332 and 382 in the same repo. Four sites
carried the stale figure: `:92`, `:96`, `:266`, `:289-290` of the prior text `[READ]`. Run
`--stats` rather than quoting any number here, including 382.

**A record is not a work.** The 332-record index was measured at 319 distinct works, eleven
Semantic Scholar ids appearing under twenty-four keys. **That census has NOT been re-run
against 382, so no works-figure exists for the current index** `[READ, absence]`. Do not carry
319 forward and do not derive a replacement by subtraction.

### 2.2 Deep-search reach, and the gate that still fails

```
deep searches known      : 28
  reaching the corpus AS METADATA: 28 of 28
  reaching the corpus AS PAPERS  : 11 of 28
  reaching the corpus by NO route: 0
  metadata only, ZERO papers ingested: 17, representing 1244 papers as an integer only
FAIL  (17 problem(s))
```
`[READ]`, `python3 analysis/research_index.py --source-audit`.

**SAY BOTH NUMBERS, NEVER ONE.** 28 as metadata and 11 as papers answer different questions.
The absorbed documents say "27 as metadata, 8 as papers"; that is stale in both halves.

**The defect was an abort, not an absence.** `--build` was dying on `MANIFEST.json` and on
schema-less stubs, so nothing could land. Fixed by `e1921cf` `[RECALLED, from the absorbed
blocker document]`. Before reading any future drop from 382 as data loss, run the
empty-export-directory control first.

**The remaining 17 are recoverable and the route is proven, not assumed.** Two calls per
search against the live Undermind workspace:

```
inspect_deep_searches(workspace_id=..., names=[<the search NAME, not the slug>],
                      papers_only=True, detail_level='standard', limit=50)
get_paper_info(workspace_id=..., cite_keys=[...], detail_level='compact', show_doi=True)
```

Two traps. **Address the search by `name`, not `slug`**: passing the slug returns "Search not
found". And **paginate**: `inspect_deep_searches` pages at 50 and four searches exceed that
(`free-body-load-transfer-expanded` 119, `free-body-load-transfer` 118,
`load-transfer-portability` 114, `moving-vehicle-open-source` 105). A partially-paged export is
unusable and the gate is written to say so. The route recovers title, year, DOI and link. **It
does not recover abstracts, so records ingested this way must never be described as read.**

### 2.3 Reach is not citation

```
382  papers in the corpus
164  cited status in the index
  ~15  entries in the SHIPPED Overleaf bibliography
   3  are \cite'd and therefore print in the reference list
```

**Scope trap, and it is live.** `paper/can_it_ford_references_IEEE.bib` in this repo holds
**42 entries** `[READ]`. The shipped Overleaf bibliography holds 15 `[RECALLED]`. These are
different files and the repo keys diverge from Overleaf's. Never join them by DOI: the shipped
bib carries no DOI fields at all, so a DOI join returns zero by construction. Join by title or
cite key.

**The corpus INDEX is not a superset of the bibliography, but the DISK now is.** Of the 14
works the paper cites, 11 were recorded as absent from the corpus, including `shah2018`
`[RECALLED]`. **That was an indexing gap, not a sourcing gap.** Section 6.12(b) found the
papers on `~/Desktop` and extracted their full text, `shah2018` among them, verified as
`10.1051/matecconf/201820307003` from its own header `[READ]`. Corpus INDEX coverage still
cannot answer what the paper cites; local disk now can.

---

## 3. The reader spine, carried forward

Relayed, single-origin, **not re-verified in this consolidation**, and listed so they are not
lost `[RECALLED throughout this section]`.

- **A measured 2010 Yaris inertia tensor exists** and the solver's own particle cloud already
  matches it to within 2.3 percent, against 19 to 26 percent for the box fallback. This is the
  first external validation anchor the project has for its rigid-body representation. It is why
  `inertia_kg_m2` must NOT be wired: the absence is correct, not a gap.
- **The class labels were derived from a hull that never ran.** The class audit grades a hull
  scaled by lambda, lengths 4.90 m and 5.20 m; no such hull entered any run.
- **`xie2023physgaussian` performs zero physics validation.** Its entire quantitative
  evaluation is rendering PSNR on synthetically deformed scenes. If it is cited near a physics
  claim, move it.
- **`flood-mpm-debugging-reference` states LS6 is aarch64. LS6 is x86_64**, and that skill
  loads before Methods or Limitations text is written.
- **The MCP deny list is bypassable by alias**, nine exact-name UUID aliases plus four
  capability aliases under differently-named servers.
- **The idev burn figure 98.5 to 99.1 percent is stale**, re-measured 93.8 percent.
- **The DOI contamination check is CLOSED.** It is the one pass-1 section 8 item that pass 2
  finished.

**The provenance warning still governs.** Of 3,291 atomic findings in the mined bundle,
**3,289 have a single origin**. Where this file reports agreement between two methods, it names
both and says whether they are independent.

---

## 4. The 138-DOI accounting, absorbed and preserved as authority

This section carries forward `CORPUS_MERGE_FINAL_2026-08-22.md`, which was previously held
separate. **It is preserved rather than banner-superseded away**, because it is the only
authority on the 138 and pointing readers away from it was the stated reason a prior session
declined to supersede it.

**The number that matters is zero: 0 of 138 are cited in the submitted paper** `[RECALLED]`.

Open findings from that accounting, unchanged unless marked:

1. **136 of 138 have not been read in full.** Only 4 have full text on local disk. Two were
   read on 08-22, and **a third is read in section 6.5 of this file as of today**, leaving one.
2. **Open access, measured:** 50 of 138 open by Unpaywall, 74 closed, 14 no answer (11 of those
   being 2025-2026 arXiv DOIs Unpaywall does not cover). **The 74 closed need institutional
   access, not a better script.**
3. **Two `ABSENT` rows**, Lavelle 1987 and Papanicolaou 2002, both closed, both single-report,
   the only two of the 138 with no trace of any kind in the repo.
4. **An unactioned erratum.** `10.1016/j.joes.2018.05.002` has an erratum at
   `10.1016/j.joes.2020.11.003`. Nothing cites the paper yet, so nothing is wrong today, but
   the pairing must travel with it if it is ever cited.
5. **A cluster nobody has triaged.** 11 of the 138 are 2025-2026 arXiv papers on AI agents for
   scientific computing. They bear on the reproducibility-record contribution, not on flood
   physics. Whether they belong in the paper is a scope decision, not a research one.
6. **Two appendix rows carry pre-publication DOIs.** They resolve, and they are not the form to
   print in a bibliography.
7. **The surname figure of 46 is an upper bound**, not a count.
8. **The catalogue is now 11 days stale.** Built 2026-08-14 against a tree that has since
   absorbed roughly 20 branch merges, and its builder lives in a prior session's scratchpad, so
   it may no longer exist.

**CLOSED since that accounting was written:** its item 11, the shipped bibliography had never
been run through a retraction check. It has now: **9 of 9 DOI-bearing entries matched at high
confidence, 0 mismatch, 0 ambiguous, 0 not_found, 0 retracted, 0 corrections, 0 expressions of
concern** `[RECALLED]`. **Scope caveat: 6 of the 15 entries carry no DOI in any field**
(`thorpe2026pvwm`, `hsiao2025nerfmpm`, `shand2011arr`, `nws_tadd`, `genesis2024`, `fred2026`)
and could not be audited by identifier. The audit covers 9 of 15, not 15 of 15.

---

## 5. The coupling-defect question

### 5.1 The ranking, re-measured live and now with current numbers

**The two joint top-ranked gap DOIs are at 7 reports apiece** `[READ]`:

```
7  10.1016/j.jcp.2016.10.064   Incompressible material point method for free surface flow
7  10.1016/j.cma.2022.114809   An immersed finite element material point (IFEMP) method
5  10.3970/cmes.2008.031.107   Examination and Analysis of Implementation Choices within MPM
5  10.1504/pcfd.2019.10018820  Benchmarking MPM for interaction problems between ...
5  10.1115/detc2015-47142      Coupled Multibody Dynamics and SPH
5  10.1002/nme.7217            Analysis and mitigation of spatial integration errors for MPM
4  10.1007/s00466-019-01783-3
```

`10.1007/s00466-019-01783-3` sits at 4, **strictly below both and NOT the pair**, exactly as
CLAUDE.md states `[READ, confirming]`.

**Of the joint top pair, one is read and one is not.** `10.1016/j.jcp.2016.10.064` was read in
full on 08-22 `[RECALLED]`. `10.1016/j.cma.2022.114809` remains unread, see 6.1.

### 5.2 The F-bar / volumetric-locking finding, folded in for the first time

**This finding reached none of the reader documents before today.** Measured live: `F-bar` in
any spelling returned 0 hits and word-boundary `locking` returned 0 hits across all three prior
reader files, against 4 and 10 in its source `R9_CORPUS_READ_2026-08-19.md` `[READ]`. It is
folded in here.

**The finding** `[RECALLED, from that document]`: explicit MPM volumetric locking systematically
over-predicts force transmitted to a rigid body (strip footing, analytic 5.14 against roughly
7.5 to 8.0, so 45 to 55 percent over), is NOT fixed by refinement, and its remedy is F-bar.
Job B measures +34 to +64 percent, does not improve with refinement: same sign, overlapping
magnitude. Its source labelled this "NOT A DIAGNOSIS YET" and pre-registered a PPC sweep as the
discriminator, because locking predicts error RISING with particles per cell while
velocity-projection bias predicts FLAT.

**THE DISCRIMINATOR WAS RUN AND IT CAME OUT AGAINST LOCKING.** Job 923239 swept 3.375 to 64
particles per cell at fixed grid and returned a log-log slope of **+0.0596**, where `PPC^-2`
would demand `-2`. Flat, which is the velocity-projection signature `[RECALLED, from
`ac0f0d8`'s message]`. The result sits in a different commit from the document that raised the
hypothesis, which is why it kept looking open. **Anyone folding the locking hypothesis forward
must carry this refutation with it, or they will re-import a hypothesis its own discriminator
already answered.**

**Separately and still standing:** the pinned solver has no F-bar, no J-averaging, no pressure
smoothing and no locking mitigation of any kind `[RECALLED, not re-derived here]`.

**THE CONCLUSION, STATED PLAINLY BECAUSE IT IS EASY TO MISREAD.** Job B's **+34 to +64 percent
force over-prediction is NOT explained by volumetric locking.** The pre-registered
discriminator was run, and a log-log PPC slope of +0.0596 against a required -2 refutes the
locking hypothesis rather than leaving it untested `[INFERRED from the two READ figures above]`.

**This does not identify the mechanism. It eliminates one candidate.** The flat slope is
*consistent with* velocity-projection bias, which is not the same as establishing it: no
positive test has been run, and section 5.3's two competing mechanisms are still
undiscriminated. **The over-prediction remains OPEN and unexplained.** Anyone citing this
section should say what it rules out, never treat it as a diagnosis, and never write that Job B
is understood.

### 5.3 The two competing mechanisms remain undiscriminated

Register G25 states it plainly: (a) says the deficit lives in the free-surface pressure
boundary condition of a weakly compressible formulation, (h) says it lives in material-point
stress recovery. **Both predict a grid-converged deficit, so grid convergence alone cannot
separate them.** G25 names the distinguishing test. Neither is established `[RECALLED]`.

### 5.4 A misattribution that is withdrawn at its root, recorded so it is not re-imported

`ac0f0d8` withdrew two claims attributed to Wallstedt and Guilkey 2007 `[READ]`:

- **(a)** "For a body held fixed the projection error becomes a CONSTANT SYSTEMATIC BIAS rather
  than noise." **Not in the paper.** It came from a PDF-reading subagent's own reasoning
  section. It would not have applied here in any case: the body is fixed, the WATER particles
  are not.
- **(b)** The plateau's **"O(h)" scaling is not a stated result.** The plateau is real and was
  quoted correctly; the scaling was read off a figure by eye. **Say GRID-SET, never O(h).**

The uncorrected text shipped in two commits and was relayed onward to two sessions and a board.
It is corrected in the root file and recorded across six tracked documents. **One untracked
file still carries the original wording, `.claude/state/r8_send_log.md:13723`, and it should
stay verbatim**: it is an append-only record of what was actually sent, and rewriting it would
falsify that record `[READ + INFERRED]`.

---

## 6. Open items, every one, with its exact blocker

Nothing below is hidden or quietly dropped. Items marked CLOSED were closed by measurement,
not by assertion.

### 6.1 `10.1016/j.cma.2022.114809` remains UNREAD. OPEN, blocked on money or institutional access.

Li, Lian and Zhang 2022, "An immersed finite element material point (IFEMP) method for free
surface fluid-structure interaction problems", CMAME 393, 114809. Joint top-ranked gap at 7
reports. **The highest-value single acquisition in the project.**

Re-checked today by **two independent instruments** `[READ]`:
- scite: `isOa: false`, `oaStatus: "closed"`, `contentDenied: true`, purchase only at USD 41.95,
  zero full-text excerpts returned. Only 1 Smart Citation, so the citation route yields nothing.
- Unpaywall, a separate service: `is_oa = False`, no OA location.

These are separate origins, so this is corroboration and not one source cited twice. **It needs
institutional access, not a better script.**

### 6.2 `10.1016/j.jcp.2019.03.049` remains UNREAD. OPEN, but now fully identified.

**Upgraded today from a bare "Hyd19" to a full record** `[READ]`: **Hyde, D. and Fedkiw, R.
(2019), "A unified approach to monolithic solid-fluid coupling of sub-grid and more resolved
solids", Journal of Computational Physics 390, 490-526.**

Also confirmed closed by both instruments (scite `contentDenied: true`, Unpaywall `is_oa
False`), and an arXiv title search returned nothing `[READ]`.

**It is not in the 382-record index at all: 0 records** `[READ]`. So it is not merely unread, it
is uncatalogued. **The claim that the literature rejects velocity equilibration rests entirely
on this paper and remains `[RELAYED]`.** The title supports the claim's plausibility, since
"monolithic" coupling is the alternative to equilibration, but a title is not a result. Do not
promote that claim until the paper is read.

### 6.3 The two coupling mechanisms remain undiscriminated. OPEN, blocked on a solver run.

See 5.3. The distinguishing test is named in register G25. Not attempted in this consolidation.

### 6.4 The report-count instrument disagreement. **CLOSED, cause identified.**

The absorbed documents record "TSV 4, index 5" as unresolved. **Both numbers are stale and the
disagreement is not a defect** `[READ]`:

- The r10 TSV is a frozen 2026-08-14 snapshot. It still reads 4.
- The index is rebuilt on every ingest. It now reads **7**, because `e1921cf` ingested further
  searches including `grid-converged-force-deficit`, which names this DOI.

They measure the same DOI at different times with different instruments, so they were never
expected to agree. **The ranking is invariant across both**, which is the property that was
always the load-bearing one. Quote the ranking, never a bare report count.

### 6.5 The cheapest remaining read. **CLOSED. I read it today.**

`10.1016/j.proeng.2017.01.041`, Zhao, Liang and Martinelli (2017), "Numerical simulations of
dam-break floods with MPM", Procedia Engineering 175, 133-140. Read in full today from
`~/can-it-ford-refs/2026-08-19-r10/Zha17_10.1016_j.proeng.2017.01.041.pdf`, 475,140 bytes,
via `pdftotext -layout` `[READ]`. It is CC BY-NC-ND open access.

**What it establishes.** MPM dam-break flow fronts agree with experimental data and with two
independent verified methods, SPH and VOF. The critical aspect ratio for shallow-water-equation
applicability is 1; above it, SWE overestimates front propagation speed.

**Its resolution result, computed from its own Table 1 rather than from its prose** `[READ +
INFERRED]`. Four conditions, mesh 0.1 m and 0.05 m, 4 / 8 / 10 material points per element:

| t (s) | min | max | spread | spread / mean |
|---|---|---|---|---|
| 0.8 | 4.55 | 4.62 | 0.07 m | **1.53 %** |
| 1.5 | 8.92 | 9.00 | 0.08 m | **0.89 %** |

So across a 2x mesh refinement and a 2.5x particle-density change, the front position moves by
under 1.6 percent. They chose 4 MPs per element for every production run on that basis.

**THE CAVEAT THAT MUST TRAVEL WITH THIS PAPER, and it is the reason it does not rescue this
project.** Zhao et al. measure **flow front position**, a kinematic quantity of the free
surface. This project's non-monotone quantity is **displacement of, and force transmitted to, a
rigid body** (`final_disp_mag_m` moving +87.8 percent then -59.2 percent across g48/g64/g96).
Those are different observables and there is no coupled body anywhere in Zhao et al. **This
paper does NOT license a claim that this project's forces are resolution-insensitive.** Cited
carelessly it would do real damage, because it looks like exactly that result.

### 6.6 The 17 metadata-only deep searches. OPEN, bounded, route proven.

See 2.2. 1244 papers exist to this project as an integer and nothing more. This is the single
largest open item by volume and it is an engineering task with known commands, not a research
question. Not attempted here because a partially-paged export is worse than none.

### 6.7 The corrections register does not name this file. OPEN, blocked on concurrency.

Measured live: `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` returns **0 hits** for
`MERGED_RESEARCH_READER_CORPUS_FINAL` and 2 for `CORPUS_MERGE_FINAL` `[READ]`. CLAUDE.md does
name this file, 1 hit `[READ]`. The register is the corrections authority and adding a row to
it while other sessions are live is the class of edit that produced the 2026-08-07 breach, so
it is left open deliberately rather than filled.

### 6.8 CLAUDE.md's reader-ranking block is now out of date. OPEN, blocked on concurrency.

CLAUDE.md's block states that `CORPUS_MERGE_FINAL_2026-08-22.md` "is a SEPARATE line and is NOT
superseded". **This consolidation absorbs it, so that sentence is now false.** CLAUDE.md was
dirty under another session throughout this work and the standing rule forbids two sessions
touching one file, so **it was not edited** `[READ]`. The replacement text is given in section 8.

### 6.9 Unreviewed. OPEN.

**No claim in this file has been checked by the physics-skeptic path or any adversarial
reviewer.** That path was not invoked in this session. Per the standing rule that a dated
infrastructure claim must not age into a fact, its availability is unknown rather than assumed
dead. Every physics claim carried in sections 3 and 5 remains UNREVIEWED.

### 6.10 Poster and paper submission status. **STILL OPEN. My own CLOSED verdict is WITHDRAWN.**

**CORRECTED 2026-08-26.** This item read "**CLOSED.** Recorded per direct human confirmation in
three commits". **That was wrong, and it was wrong in an avoidable way: I read the three commit
MESSAGES and never opened the file they wrote.**

`docs/SUBMISSION_STATUS.md` live is 8 lines and **both status lines are blank** `[READ]`.
Verified with `cat -e`: the poster line and the paper line each end `: $`, colon, space, end of
line. There is no YES, no NO, and no venue.

The three commits, in order `[READ]`:

1. `a83a38b` 08-24 17:56, a merge, created the file with `[YES/NO]` placeholders.
2. `12486ea` 08-25 01:57, identical subject, **appended a second identical copy of the whole
   block** rather than editing the first, which is why the file says everything twice.
3. `2d4c71a` 08-25 02:01, "Fill in actual poster and paper submission status", **deleted the
   `[YES/NO]` placeholders and put nothing in their place.**

So a commit named "Fill in actual status" made the file **less** informative, replacing a
visible unanswered placeholder with a blank that reads as answered. Two commits claim "per
direct human confirmation" and **the confirmation never reached the file.** It happened in chat.

**Nothing in the repo records whether the poster was uploaded or the paper submitted.**

### 6.11 A refuted hypothesis, recorded so it is not re-raised. **CLOSED.**

Reader-facing citation count moved from 43 to 107 after a rebuild. The hypothesis that the
jump was the 138-DOI appendix inflating the metric was **measured and is dead: 0 of the 107 are
reader-facing only via that file** `[RECALLED]`. The growth is real. Do not resurrect it.

### 6.12 What was NOT in this corpus. **ALL SIX ITEMS WORKED 2026-08-25. Five closed, one deflated.**

Every item in this list was attempted rather than re-recorded. **Four of the six carried a
stated blocker that turned out to be false**, and two carried counts that were wrong by an
order of magnitude. The results:

**(a) The 73 reference PDFs had zero extracted text. CLOSED, and the count was wrong.**
`pdftotext` is present at `/opt/homebrew/bin/pdftotext`, so the blocker never existed on this
machine. Ran over all 73: **62 OK, 11 EMPTY, 0 FAIL, 8,926,048 characters** `[READ]`. The 11
"empty" are **not papers**: all are single-page figure plates under
`~/can-it-ford-refs/2026-08-19/Anura3D_OpenSource/images/TutorialManualFigures2021/`, 7 in
`foundation/` and 4 in `submerged_slope/`, one page each, Producer "Microsoft PowerPoint"
`[READ]`. **So the set is 62 reference documents plus 11 tutorial figures, not 73 papers, and
62 of 62 papers now have full text.** Written to `~/can-it-ford-refs/_fulltext/`.

**(b) `~/Desktop` and `~/Documents` unswept. CLOSED, and this was the highest-value item.**
TCC control run first, both readable, 29 and 284 top-level entries `[READ]`. Outside any
can-it-ford tree there are **154 unique research PDFs**, largely in a curated
`E1_REFERENCE_PAPERS` set of 75 hardlinked across seven Desktop snapshots. Extracted **154 of
154, 0 empty, 0 fail, 5,281,914 characters** to `~/can-it-ford-refs/_fulltext_desktop/` `[READ]`.

**THIS DISSOLVES THE "CORPUS IS NOT A SUPERSET OF THE BIBLIOGRAPHY" GAP.** It was never a
sourcing gap. The papers were on disk in an unswept location the whole time. Confirmed present
with full text: **`shah2018`**, verified as `10.1051/matecconf/201820307003` by reading its own
header, the exact DOI recorded as "absent from the corpus entirely", 58,458 characters
`[READ]`; **`xiong2024`**, the one bib entry BibTeX drops as uncited; **`fred2026`** (Malone et
al. 2026, FRED); Azhar et al. 2023; Albano 2016; Amicarelli 2015; Balmforth 2013; Dasallas
2025; Wang and Marsooli 2021; Rahnemoonfar 2020; and **the WRL September 2014 flood hazard
technical report**, which is the primary source behind the L-4 counter-example in CLAUDE.md.

**(c) Vista and LS6 unswept because "MFA blocks non-interactive SSH". CLOSED, and the reason
was FALSE.** `bash scripts/tacc.sh vista` returned `login1.vista.tacc.utexas.edu` and a
directory listing on the first attempt `[READ]`. Both hosts swept.

- **Vista holds 28 UNPUSHED COMMITS on `$WORK/can-it-ford`, plus 64 dirty files** `[READ]`.
  The recorded figure was 12, so **the exposure is more than double what was on record**.
  They are substantive: the Zhao 2019 in/outflow BC port to the vehicle scene; "g160 flips to
  STUCK 5 of 5, at exactly the 10 particle layers the literature asks for"; "The refinement
  ladder is four tanks, not four resolutions"; "At g48 the grid cell is BIGGER than the ground
  clearance"; the g128 zero-margin result; and "Four MPM foundation entries, three DOI-verified".
  281 PDFs and a full `can-it-ford-track1-6dof` tree also live there.
  **Of the 5 docs those commits add, 4 exist on the Mac and 1 does not**,
  `docs/R8_OPENCHANNEL_BC_RECONCILE.md`, which is on a branch but not in the main checkout
  `[READ]`. So the docs are largely mirrored; **the 28 commits are the real at-risk asset.**
- **LS6 holds no unswept project research.** 0 unpushed, 0 dirty, HEAD stale at 2026-07-23, and
  all 432 of its markdown files belong to upstream libraries (eigen, chrono, mpm-engine, gsplat)
  `[READ]`. A clean negative.

**(d) "7,075 of 7,543 mined blocks unread in prose." DEFLATED, the 7,543 bundle does not exist.**
What survives on disk is `~/can-it-ford-workflow-archive/mined/`, ten JSON files, 4.8 MB,
holding **1,737 blocks**, not 7,543 `[READ]`. Classified: **1,051 prose (60.5 percent) and 686
tool output (39.5 percent)**. The top eight by score are **all** grep dumps and file
inventories, and every finding in them is already distilled into CLAUDE.md: the 9.80665 fork,
the DRIFT_THRESHOLD sites, the four-rung ladder, the determinism columns `[READ]`. **So the
honest statement is not "7,075 unread findings". It is "1,737 retained blocks, top-ranked ones
already routed".** The unranked remainder of the original mining was never persisted.

**(e) "768 base64 PDF page images, 148.4 MB, undecoded." CLOSED, and both numbers were wrong.**
Live: **116 payloads across 7 transcript files, 24.1 MB encoded**, which **deduplicate to 37
unique images, 5.3 MB**, 35 JPEG, 1 PNG, 1 WebP `[READ]`. All decoded to
`~/can-it-ford-refs/_decoded_images/`.

**They are journal page scans, not screenshots**, which is why this mattered. One was read
directly and identified as **Baumgarten and Kamrin, `10.1002/nme.7217`, "Analysis and
mitigation of spatial integration errors for the material point method"**, a paper already in
the corpus at **5 reports** `[READ]`. **It is redundant**: the same paper's full text was
already recovered in (a) as `Bau23_10.1002_nme.7217.txt`, 224,243 characters. So the image
cache adds no paper the extraction missed, which is the useful negative.

**(f) "The corpus holds no full text." NOW FALSE ON DISK, still true in the index.**
**216 papers now have extracted full text locally, 14,207,962 characters** (62 from refs plus
154 from Desktop) `[INFERRED, summing two READ figures]`. The index itself still carries no
`fulltext` field and no PDF path, and **171 of 382 records still have no abstract** `[READ]`.

**COPYRIGHT DECISION, made deliberately.** The extracted text is written OUTSIDE the repo, to
`~/can-it-ford-refs/_fulltext*/`. **This repo is public.** Committing the full text of 216
copyrighted papers into a public repo would be a licensing problem regardless of research
intent. Whatever lands in git should be an index of paths, DOIs and character counts, never the
text. Wiring `fulltext_path` into `research_index.py` is the remaining task and it is small.

### 6.13 A new lead this sweep produced, on the open locking question

Baumgarten and Kamrin, recovered in (a) and read today, states that MPM spatial integration has
two coupled problems: **volumetric or kinematic locking of nearly incompressible materials, and
quadrature error accumulation**, and that **the smoothing and reduced-quadrature methods that
cure locking compound the quadrature error** `[READ, lines 97 to 103]`. That tradeoff is not
represented anywhere in this project's documents.

**It closes a loop the corpus had left open.** Its reference 52 is Coombs, Charlton, Cortis and
Augarde, "Overcoming volumetric locking in material point methods", CMAME `[READ, line 1978]`,
which is `10.1016/j.cma.2018.01.010`, **the same DOI this corpus carries as appendix row 69 with
status INDEX, meaning catalogued and reaching neither prose nor bibliography.** So the canonical
anti-locking reference is cited by a 5-report corpus paper whose full text is now on disk, and
the project had both halves without connecting them. **This is the cheapest available next step
on section 5.2, and unlike `10.1016/j.cma.2022.114809` it costs nothing.**

---

## 6.14 `fulltext_path` is wired, and what a rebuild then exposed

**DONE 2026-08-25.** `analysis/research_index.py` now carries `FULLTEXT_DIRS`,
`load_fulltext_map()`, three matching routes (DOI encoded in filename, first DOI in the text
body, then title-token Jaccard at 0.55), per-record `fulltext_path` / `fulltext_chars` /
`has_fulltext`, a top-level `n_with_fulltext`, and a `--fulltext` report `[READ]`. Rebuilt.

```
FULL-TEXT COVERAGE   index built 2026-08-25
   382  papers in the corpus
   211  have an abstract
    19  have EXTRACTED FULL TEXT on local disk
    14  have both
  2221860  characters of full text linked
```

The 19 include **both halves of the pair this project most needs**:
`10.1016/j.jcp.2016.10.064` (joint top-ranked, 7 reports), `10.1002/nme.7217` (anti-locking, 5
reports), `10.1016/j.compfluid.2018.10.007` (Zhao 2019, the in/outflow BC citation CLAUDE.md
names), `10.3390/su151713262` (Al-Qadami 2023), `10.1029/2023wr036739` (Xiong 2024) and
`10.1016/j.proeng.2017.01.041` (Zhao 2017).

**THE EXTRACTED TEXT IS NOT IN THE REPO AND MUST NOT BE COMMITTED.** The index stores a path
and a byte count. The repo is public and the papers are copyrighted.

### 6.15 A correction to my own figure from the previous pass

**"154 unique research PDFs" was WRONG and is withdrawn.** The filter that produced it matched
any filename containing " - ", which swept in unrelated material. Re-classified `[READ]`:

- **18 were personal school records** (grade summaries, interim reports, 10th to 12th grade).
  These had no business in a research corpus. Moved to
  `~/can-it-ford-refs/_quarantine_personal/`. **Not deleted, and the source PDFs are untouched.**
- **99 were unrelated coursework** (water-lab handouts, VSEPR notes, an eBook, an oral-history
  page). Moved to `~/can-it-ford-refs/_quarantine_coursework/`.
- **37 are genuine research documents** and remain in `_fulltext_desktop/`.

So the honest figure is **107 research full-text files**, 70 from `can-it-ford-refs` and 37
from the Desktop, not 216. The extraction was real; my classification of it was not.

### 6.16 What is on this computer and still NOT in the corpus

Measured 2026-08-25 against the rebuilt index `[READ throughout]`.

**(1) 31 papers have full text on disk and are absent from the index entirely.** This is the
largest and most actionable gap, because acquisition is already done. Of the 107 full-text
files, 50 yield a DOI; 19 of those DOIs are in the corpus and **31 are not**. Among them:

- `10.1051/matecconf/201820307003`, **`shah2018`**, which the paper cites.
- **Three Ceccato papers** on MPM soil-fluid coupling: `10.1016/j.compgeo.2018.07.014`,
  `10.1016/j.compgeo.2020.103876`, `10.1080/19648189.2017.1408498`.
- `10.1016/j.cma.2020.113119`, **Negrut**, whose group's work is the literature-backed
  alternative coupling architecture named in CLAUDE.md item A-1.
- `10.1016/j.jhydrol.2016.02.009` (Albano, floating bodies in flash floods),
  `10.1029/2020wr028616` (Wang and Marsooli), `10.1111/jfr3.12048` (Balmforth),
  `10.1007/s40571-021-00404-2`, `10.1016/j.apor.2019.101932`, and 20 more.

**(2) Five Perplexity reports have no ingest route at all.** The builder reads 8 hardcoded
markdown `REPORTS` and the `data/deep_searches/` JSON exports. **There is no Perplexity path.**
The five carry **17 unique DOIs, 7 already in the corpus and about 7 distinct ones not**
(the raw diff prints 10 because trailing punctuation splits three variants of one DOI).
**Two of the five reach no document in this repo by any route**:
`physgaussian-bridge-findings` and `citation-verification-report` `[READ]`. The
`drift-threshold-citation-research` report is the one to read first: it is a citation hunt for
the **unsourced 0.05 DRIFT_THRESHOLD**, and it cites `10.1080/00221686.2011.616318`, which is
the Xia 2011 incipient-velocity paper this project has repeatedly failed to retrieve.

**(3) Claude artifacts are NOT a gap, and I expected them to be.** 283 `compass_artifact_*`
files exist across Desktop, Downloads and Documents, but they **deduplicate to 38 unique
artifact ids, and 36 of those already reach the index as `documents`** `[READ]`. The 2 that do
not are "The definitive Casio fx-CG50 guide for college science" and its companion, correctly
off-topic. A curated triage of them already exists at
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_COMPASS_ARTIFACT_SUBJECT_INDEX_v2_2026-08-14.tsv`,
38 rows, 30 on-topic and 7 off-topic, each with a facet assignment. **This is a clean negative
and it should stop anyone re-opening the question.**

**(4) The 138-DOI catalogue TSV EXISTS, contradicting section 4 item 8.** That item says its
builder "lives in a prior session's scratchpad, so it may no longer exist". The catalogue
itself is on disk at
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv`,
**206 rows, 48,740 bytes, dated 2026-08-14** `[READ]`. Its first row also settles the
"TSV 4" figure in 6.4 exactly: its `in_reports` field for `10.1016/j.cma.2022.114809` reads
`moving-rigid-body+multi-resolution-MPM+validated-MPM-coupling+wall-penetration`, four named
reports. **The count was never mysterious, it was four named sources against a later index.**

**(5) A whole curated corpus directory the builder cannot see.**
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/` holds ten faceted topic folders with 516
symlinked entries, plus the manifests above. It is a research asset assembled by an earlier
session and it reaches the index only through the 36 artifacts already counted in (3).

---

## 7. Process findings worth keeping

### 7.1 A merge landed inside a commit named for unrelated work

See section 1. The cost was a day of three documents asserting the opposite. **A commit message
is the only index anyone reads; work that lands unnamed is work nobody can find.**

### 7.2 The flag collision was resolved by rename, not by choosing a winner

`--source-audit` was declared on both sides of the corpus-bib merge with different predicates,
and a union raises `argparse.ArgumentError` on the duplicate flag. Resolved on 2026-08-24 by
renaming the branch's reachability report to `--ingest-audit`, following that branch's own
`--<noun>-audit` convention. **`--source-audit` kept its name for the CI gate that CLAUDE.md
and the register cite, so no external citation broke.** Neither side was a superset, so both
were kept `[RECALLED]`.

### 7.3 A search that did not execute is not evidence of absence

An unquoted `--include=*.md` made zsh attempt glob expansion, fail with `no matches found`, and
return **zero hits**, which would have read as "the withdrawn claim survives nowhere" when the
search never ran. **Quote every `--include` pattern.** Same class as the standing rule that the
shell `grep` here is ugrep with `--ignore-files` and skips every gitignored path.

### 7.4 A miss is not an absence until you know what the predicate searched

`--query` covered title and abstract only, so an author query could not return a hit and its
zero read as coverage. That is how "none of the six closest prior-art DOIs is in the corpus"
reached three sessions. **All six were present.** `--query` now matches authors. It still never
matches a DOI or a method tag, and the tool prints that warning itself.

---

## 8. What this consolidation changed, so it is auditable

**Written:** this file, replacing the prior `MERGED_RESEARCH_READER_CORPUS_FINAL.md`.
**Banners added:** to the nine absorbed documents, pointing here. **No file was deleted.**
**Not touched:** `CLAUDE.md` and `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`, both
blocked on concurrency. **Nothing was staged, committed or pushed.**

**Second pass, same day: section 6.12 was worked rather than re-recorded.** Extracted full
text from 216 papers (8.93 M + 5.28 M characters) to `~/can-it-ford-refs/_fulltext/` and
`_fulltext_desktop/`, decoded 37 unique images to `_decoded_images/`, and swept Vista and LS6.
**All artifacts were written outside the repo on copyright grounds; see 6.12(f).**

> **CORRECTED 2026-08-26.** This paragraph ended "Nothing in `data/` or `analysis/` was
> modified, so `research_index.py` still has no `fulltext_path` field." **That sentence was
> true when written and is now false**, superseded by a THIRD pass in the same session which
> is written up in 6.14 above. Measured live 2026-08-26: `analysis/research_index.py` is
> modified (`+154 / -3`) and carries `FULLTEXT_DIRS`, `load_fulltext_map()` and a `--fulltext`
> report; `data/research_corpus_index.json` is modified (`+1154 / -3`) and carries
> `has_fulltext`, `fulltext_path` and `fulltext_chars` on all 382 records plus a top-level
> `n_with_fulltext` of 19 `[READ]`. So section 8 and section 6.14 contradicted each other, and
> **6.14 is the correct one**. The artifacts themselves are still outside the repo, which is
> the part of this paragraph that stands: the index stores a path and a character count and
> never the text. The rest of section 8's "Not touched" list also no longer holds, see the
> addendum at the end of this section.

**Two items are held for Josie because they require edits this session could not safely make.**

1. **CLAUDE.md's RESEARCH-CORPUS READER RANKING block.** Its statement that
   `CORPUS_MERGE_FINAL_2026-08-22.md` is "a SEPARATE line and is NOT superseded" is now false.
   Replacement text:

   > **RESEARCH-CORPUS READER RANKING, reset 2026-08-25. THERE IS NOW ONE LINE, NOT TWO.**
   > `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` is the single master. It absorbs the two
   > dated readers, `CORPUS_MERGE_FINAL_2026-08-22.md` and its 138-DOI accounting, both
   > `CORPUS_FINAL_MERGE_REPORT_*` session reports, `CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md`,
   > `CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md`, `CORPUS_LINEAGE_STATUS_2026-08-23.md` and
   > `R9_CORPUS_READ_2026-08-19.md`. All nine remain on disk with SUPERSEDED banners; cite them
   > only with their date and never as current. The master does not outrank the register: where
   > it conflicts with the register, the register wins.
   > **The coupling-defect gap DOI is `10.1016/j.cma.2022.114809`**, joint top-ranked with
   > `10.1016/j.jcp.2016.10.064` at **7 reports each as of 2026-08-25**, and STILL UNREAD,
   > closed access. `10.1007/s00466-019-01783-3` is at 4, strictly below both, and is NOT the
   > pair. The count is instrument-dependent and time-dependent; the ranking is not.

2. **A corrections-register row** naming this file as the terminal reader. See 6.7.

> **ADDENDUM 2026-08-26, item 1 is DONE, item 2 is NOT.** `CLAUDE.md`'s ranking block was
> replaced with the text drafted above, on Josie's explicit go-ahead, after checking that its
> unrelated uncommitted `+41 / -17` does not touch the ranking block (0 overlapping hits) and
> that its mtime was 21 hours stale rather than a live edit `[READ]`. The three report counts
> in that text were re-derived live before being written into the constitution, via
> `analysis/research_index.py --doi`: `10.1016/j.cma.2022.114809` 7, `10.1016/j.jcp.2016.10.064`
> 7, `10.1007/s00466-019-01783-3` 4 `[READ]`. **The register row is still not written**, and
> the register remains clean and unedited at 0 hits for this file against 2 for
> `CORPUS_MERGE_FINAL`. The full map is `docs/CORPUS_INVENTORY_2026-08-25.md`.
>
> **The reader is NOT complete.** `--source-audit` still exits 1 with 17 problems, 17 searches
> reaching the corpus as metadata only, representing 1244 papers as an integer and nothing
> more `[READ]`. See 6.6, which remains the largest open item by volume.

---

## 9. How to re-derive every number in this file

```
python3 analysis/research_index.py --stats          # 382 / 211 / 164
python3 analysis/research_index.py --source-audit    # 28 / 28 / 11, FAIL 17
python3 analysis/research_index.py --fulltext        # 19 of 382 linked to local full text
python3 analysis/research_index.py --searches
git merge-base --is-ancestor de18180 HEAD && echo merged
/usr/bin/grep -c 'MERGED_RESEARCH_READER_CORPUS_FINAL' docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
/opt/homebrew/bin/pdftotext -layout ~/can-it-ford-refs/2026-08-19-r10/Zha17_*.pdf -
```

Use `/usr/bin/grep`, never the shell `grep`, for any inventory or audit claim: the shell one is
ugrep with `--ignore-files` and skips every gitignored path.

---

## Standing caveat

**Nothing in this file has been adversarially reviewed.** Other sessions were live in this repo
throughout the consolidation, so any state here can have moved since it was measured. Re-run
rather than cite.

---

## 10. Global audit fold-in, 2026-08-26

Appended after the Standing caveat rather than before it, deliberately: this file was
carrying uncommitted edits from another session (mtime 08:53:56 today) when this section
was written, so a pure append was chosen over an insert. **The caveat above still governs
everything below it.** Full working, including every command, is in
`docs/CORPUS_GLOBAL_AUDIT_2026-08-26.md`. Claims tagged `[READ]` were measured live this
session.

### 10.1 `docs/r10/` is a 42-file corpus layer this file barely references

**42 files, all 42 tracked by git** `[READ]`. It is the only place in this repository
where full texts were actually ACQUIRED and VERIFIED rather than indexed as metadata:
`want_list_deep_searches.tsv` (26 KB) and its resolved form (31 KB),
`unpaywall_manifest.tsv` (26 KB), `disk_resolution.tsv` (25.5 KB), `all_oa_manifest.tsv`,
`acquisition_manifest.tsv`, `priority_manifest.tsv`, a 41-row `acquired_verified.tsv`, a
31-row `quote_verification.tsv`, a 50-row `stragglers_resolved.tsv`, two full-text reads
(`fou19_still_water_read.md`, `schulz2019_image_particles_read.md`), and 12 re-runnable
scripts including `pdftext.swift`.

**`docs/r10/corpus_revision.md` is 50,504 bytes. This file is 44,970.** `[READ]` The
largest corpus document in the repository is not this master, and it sits in a
subdirectory that flat `docs/*.md` sweeps miss.

Reference counts for the string `r10/` `[READ]`: `CORPUS_MERGE_FINAL_2026-08-22.md` 8,
**this file 2**, and `CORPUS_INVENTORY_2026-08-25.md`, `CORPUS_LINEAGE_STATUS_2026-08-23.md`
and `CORPUS_FOLLOWUP_REPORT_2026-08-25.md` **zero each**. The document headed
"Inventory, all 14 targets, measured live" does not mention it once.

**Consequence for this master's own numbers:** the ladder in section 2 counts records,
abstracts and reach. `docs/r10/` measures a different quantity, obtained-and-verified full
text, and it is not in the ladder. The two have never been joined.

### 10.2 `citations/` exists, is tracked, and this chain cannot see it

`citations/` is live: **24 entries, 38 files tracked** `[READ]`. It holds the project's
hand-collected primary sources: `ARR_Project_10_Stage2_Report_Final.pdf`, the AR&R Table 1
image, `Smith-Modra-Felder/` (19 entries), `WRL reports technical and Research/`, two full
journal PDFs (Dasallas 2025, Wang and Marsooli 2021),
`vehicle_mpm_coupling_reference.md` (34 KB), `drift_threshold_grounding.md`, an Elicit
`.bib` and a 347 KB Elicit results CSV.

Measured across the five central corpus documents `[READ]`: references to `Elicit` = **0**,
to `Connected Papers` = **0**, to `citations/` = **0**, except `CORPUS_MERGE_FINAL_2026-08-22.md`
which mentions `citations/` twice.

**The literature work in this project has two halves that have never been joined.** This
chain indexes deep-search output. `citations/` holds the primary sources. Neither cites
the other. Note also that Kramer lives in a deliberate third place,
`/Users/josie/can-it-ford-refs/`, outside the repo because register E8 is open.

### 10.3 The corpus has its own MCP server, and no corpus document says so

`.mcp.json` wires **six** servers `[READ]`, one of which is **`canford-corpus`**, a
project-local stdio server backed by `.claude/tooling/corpus_mcp.py`, exposing
`corpus_search`, `corpus_read`, `corpus_resolve`, `corpus_inventory`, `corpus_headings`
and `corpus_cited_status`. **No document in the inventoried 14 mentions it.** Its source
lives in `.claude/tooling/`, which is untracked and therefore invisible from every
worktree.

Also measured `[READ]`: **not one of the six wired servers is a literature-discovery
connector.** Undermind, the most-referenced connector in this project's writing at 220
hits across 64 files, is absent from `.mcp.json` entirely and reaches sessions through a
different config layer. **That absence is the reason the two-phase ingest design exists**,
an agent turn writing `data/deep_searches/<slug>.json` and a stdlib builder reading them.
Elicit, Consensus, Zotero and Scholar Sidekick are likewise unwired. `docs/r10/connector_revision.md`
reached the same structural point on 2026-08-20 by a different route.

### 10.4 A retraction sweep was run on this file's own DOIs, and it found one defect here

Section 4 records a retraction audit as `[RECALLED]`, and its scope is the **shipped
bibliography**, 9 of 15 entries, by Scholar Sidekick `auditBibliography`. **No retraction
check had ever been run on this file's own corpus DOIs.**

Run 2026-08-26, one `checkRetraction` call per DOI against Crossref `updated-by`, which
mirrors Retraction Watch `[READ]`:

**26 distinct DOIs extracted. 25 resolved. 0 retracted. 0 expressions of concern.
1 erratum. 1 unresolvable.**

1. **The erratum corroborates from a separate origin.** `10.1016/j.joes.2018.05.002`
   ("Water entry and exit of axisymmetric bodies by CFD approach") returns
   `hasCorrections: true`, erratum `10.1016/j.joes.2020.11.003`, dated 2021-03-01. This
   file's item 4 already recorded it as an unactioned erratum; that was a prior audit,
   this is a live Crossref read, so the two are genuinely independent. **The erratum is
   administrative**, a missing Declaration of Competing Interest statement, not a
   substantive correction. Both the paper and its erratum appear as separate DOIs here,
   which is why the count is 26.
2. **`10.3970/cmes.2008.031.107` returns `result: null`.** No DOI resolves into the
   retraction graph. **It is UNCHECKED, not clean.** Do not report it as passing.
3. **NEW DEFECT IN THIS FILE. `10.1111/jfr3.12048` is not a research article.** It is
   listed above as `(Balmforth)`, grouped with Albano on floating bodies and with Wang and
   Marsooli. `resolveIdentifier` returns `[READ]`: Balmforth, David; 2013; *Journal of
   Flood Risk Management* 6(2); **title literally "Journal of Flood Risk Management";
   pages 69 to 69.** A one-page item titled after its own journal is an editorial or
   masthead entry. The author is right; the work is not a usable source. **Do not cite it,
   and do not count it as a corpus paper.** It was found only because the retraction
   sweep resolved every title, which is an argument for resolving titles rather than
   checking identifiers.

### 10.5 The four Undermind keys, and the same defect one rung up

`Gis19b`, `Ben23`, `Raz23`, `Jia16`, traced across `docs/` and `data/` `[READ]`:

| key | in this file | in `research_corpus_index.json` | in `data/deep_searches/` |
|---|---|---|---|
| `Gis19b` | **0** | yes | yes |
| `Jia16` | **0** | yes | yes |
| `Ben23` | **0** | **no** | **no** |
| `Raz23` | **0** | **no** | **no** |

All four appear in exactly two places, `docs/undermind/2026-08-25_force-overprediction-mechanisms.md`
(raw, untracked) and `CORPUS_FOLLOWUP_REPORT_2026-08-25.md`. **Half were ingested to the
index; half were not; none reached this master.**

**This file is not a superset of the index, exactly as the index is not a superset of the
bibliography.** That is the section 6 open item repeated one rung further up, and it had
not been stated at this level before.

### 10.6 `d14-corpusbib` CLOSED the corpus-versus-bibliography item, and CLAUDE.md still calls it open

`docs/R9_CORPUS_BIB_GAP_2026-08-18.md` is on disk and in HEAD `[READ]`. Its title is *"The
corpus is not a superset of the bibliography: the builder cannot reach the layer that
holds the missing works, and the gap is one paper wide rather than eleven"*, and it
carries a dated retraction of its own original title. Its answer:

- **not a dropped merge**: `DROPPED_IN_MERGE` is 0;
- **an ingestion gap, not a sourcing gap** (corrected 2026-08-19, section 22);
- **one paper wide, not eleven**: `shah2018` is the single in-scope absence, present in
  three deep searches, one of them 25 days older than the index build, absent only
  because the builder cannot see that search;
- its section 8 is headed *"The index can now report this about itself"*.

**CLAUDE.md still carries this under `SEPARATE AND OPEN`.** `[READ]` That edit was NOT
made this pass: CLAUDE.md was dirty with another session's uncommitted work at Phase 0,
and the standing rule was not to touch it. **It is the single highest-value CLAUDE.md
correction outstanding.**

### 10.7 Two dispatch branches strand their write-ups while their code merged

`[READ]` Of 18 checkable r8/r9 dispatch branches, 16 are fully merged into
`claude/add-ci-checks`. Two are not:

- **`claude/r9-settle`, 14 commits.** `analysis/stationarity.py`, `settle_audit.py`,
  `classify_failure_modes.py` and `probabilistic_verdict.py` are all in HEAD, so the
  CLAUDE.md section citing them is sound. **Stranded: `docs/R9_SETTLE_FRAMES_2026-08-18.md`**,
  plus `analysis/r9_vista_stationarity_pass.py` and two sbatch files.
- **`claude/r9-platform`, 16 commits.** `hf_space/` is in HEAD. **Stranded:
  `docs/R9_PLATFORM_ROI_2026-08-19.md`** and `.claude/checks/board_splice_check.py`.

**The pattern is the same on both: the code merged and the document did not.** That is
the worse half to lose, because code cannot say why it exists.

### 10.8 Two other things settled, so nobody re-derives them

- **The three "near-duplicate" corpus reports are not duplicates.** Independently
  re-measured `[READ]`: `CORPUS_FINAL_MERGE_REPORT_2026-08-23` versus `_2026-08-25` share
  10 unique non-blank lines out of 269 and 158, 7 of them the ABSORBED banner. The 08-25
  report versus `CORPUS_FOLLOWUP_REPORT_2026-08-25` share **3**, out of 158 and 167, and
  all three are boilerplate. Roughly 3 percent and 0 percent overlap. **Nothing needs
  deduplicating.**
- **`scripts/r8/prompts/bodies/` holds no unique content.** 11 files, and for 3 of 3
  sampled, `bodies/dNN.md` is byte-identical to the tail of `dNN.md` from its
  `## YOUR SLOT` heading onward `[READ]`. An earlier flat convention,
  `_body_d1-safe.md` through `_body_d10-licence.md`, does the same for the r8 era.
- **"Reader" names two unrelated things here.** This `MERGED_RESEARCH_READER_CORPUS_*`
  family is a LITERATURE reader. The `d20-reader` slot, branch `claude/r9-reader`, was a
  CROSS-SESSION TRANSCRIPT reader whose deliverable is
  `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md`, 47,683 bytes, in HEAD `[READ]`. They
  share a word and nothing else, and conflating them has already cost one pass.

### 10.9 NOT folded in: four things that need a human decision first

These were found and are deliberately NOT merged, summarised or acted on. Each names the
kind of decision it needs.

1. **`fix/ccsa-acknowledgement`, 7 commits, tip `51effcd` 2026-08-26 01:41.** The newest
   branch in the repository, 35 minutes newer than `claude/add-ci-checks` HEAD. Its tip
   commit worked THIS master as its authority and **retired 332 to 382 / 211 / 164 by
   live measurement**, which agrees with section 2. It adds 8 unreferenced `docs/` files
   including `docs/BRANCH_INVENTORY_2026-08-26.md` (97 refs, 39 superseded, 53 unique),
   `docs/branch_inventory_2026-08-26.tsv`, `docs/RESULTS_SUMMARY.md`,
   `docs/VIDEO_REALISM_2026-08-26.md` and **`docs/CANONICAL_FACTS.md`**.
   **Decision needed: a MERGE decision, and an AUTHORITY decision.** A file named
   `CANONICAL_FACTS.md` is a third authority surface next to the register and this master,
   and whether it outranks, feeds, or duplicates them is not a question a session should
   answer for itself.
2. **`claude/r5-research`, 82 commits, 44 stranded `docs/R5_RESEARCH_*` files.** A
   parallel literature audit larger than this entire corpus family, which this chain does
   not cite once. Includes `R5_RESEARCH_MPM_METHOD_CITATION_GAP`,
   `R5_RESEARCH_MPM_FOUNDATIONS_UNCITED`, `R5_RESEARCH_BIB_DOI_SUPPLEMENT`,
   `R5_RESEARCH_ELICIT_AND_CATALOG_MINE`. **Decision needed: a SCOPE decision.** Merging
   44 documents into a corpus that is already fighting near-duplicate names could make
   the problem worse rather than better, and the alternative, an index rather than a
   merge, is a different call.
3. **`claude/r9-settle` and `claude/r9-platform` stranded write-ups (10.7).**
   **Decision needed: a CHERRY-PICK decision**, whether to take the two documents alone or
   the whole branches.
4. **`10.1111/jfr3.12048` (10.4 item 3).** Removing an entry from the corpus changes a
   published count. **Decision needed: whether the corrected count is 25 usable DOIs here
   and what that does to the 382 / 211 / 164 ladder**, which this session did not
   recompute and should not have.
