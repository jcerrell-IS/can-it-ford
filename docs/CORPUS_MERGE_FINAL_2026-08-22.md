# Corpus merge, final accounting of the 138 catalogued-but-never-cited DOIs

**RESOLVED 2026-08-24, SO THE PARAGRAPH BELOW IS HISTORICAL, NOT CURRENT.**
`claude/r9-corpus-bib` `de18180` was merged into `claude/add-ci-checks` by merge commit
`a83a38b` (parents `72cfbdb` and `de18180`, 2026-08-24 17:56:42 +0100), and it is present on
`origin/claude/add-ci-checks`. Measured live 2026-08-25: `git merge-tree --write-tree`
between the two branches exits 0 naming no conflicting file, and the merge base IS
`de18180`. The flag collision was settled by RENAME rather than by choosing a winner: the
branch's reachability report became `--ingest-audit`, and `--source-audit` stayed with the
CI gate that CLAUDE.md and the register already cite, so neither side was dropped and no
external citation broke. `python3 analysis/research_index.py --help` exits 0 with all nine
flags coexisting. **Note the merge landed under a commit message about poster and paper
submission status, which is why no document recorded it and why three files went on
asserting the opposite for a day.** Read the paragraph below as the state on 2026-08-22.

**THE `claude/r9-corpus-bib` CONFLICT WAS DIAGNOSED AND DELIBERATELY NOT RESOLVED: it is
substantive, not mechanical, so it is reported for a human in section 7 and no merge was
made. It did NOT block this accounting, because the branch's content was read directly
without merging and contains no reference to the 138 or to register G25.**

**NOT FINISHED. The accounting is complete and the remainder is named: all 138 DOIs now
have a disposition and a title verified against a registry record, but 0 of 138 are cited
in the submitted paper, 103 of 138 reach neither reader prose nor any bibliography, 134 of
138 have no full text on local disk, and 136 of 138 have still not been read in full.
All 138 were audited with Scholar Sidekick: 0 fabricated titles, 0 retractions, 1 erratum.**

**Second-eyes pass added 2026-08-22 as section 6.** A separate session re-derived this
file's load-bearing claims instead of restating them. Eight reproduce exactly, including
the 138-row set membership, the push, both priority-DOI titles and the erratum. One is
corrected: the `hydrostatic` term count in section 2.2 was 1 and is 3, with the finding
it supported unaffected. One caveat is added: the shipped bibliography carries no DOI
field on any entry, so a DOI join against the 138 is vacuous and must not be used.

Built 2026-08-22 against `claude/add-ci-checks`. Measurements were taken at `d1490df` and
re-verified at `fe638d5`; the one row that moved between them is recorded in section 1.4.

**Provenance key, applied to every claim.** `[read]` I ran the command or read the page
this session. `[inferred]` I computed it from something tagged `[read]`. `[relayed]` it
came from another document and I did not re-derive it.

**One source cited twice is not two sources.** Where two findings agree below, I name both
origins and say whether they are independent.

---

## 0. The prior work exists. Finding it needed the right instrument, twice.

The dispatch asked which prior artifacts exist on local disk. The answer changed twice
during this session, both times because the first instrument was the wrong one.

| artifact | status | note |
|---|---|---|
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` | EXISTS, 348 lines | `[read]` pass 2; sections 4, 5, 6 read in full |
| `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md` | EXISTS, 773 lines | `[read]` committed in `bc45db8` |
| `docs/R10_WEB_ACQUISITION_2026-08-19.md` | EXISTS, 614 lines | `[read]` **was invisible at session start, see below** |
| `docs/r10/` | EXISTS, 43 files | `[read]` manifests, fetch logs, scripts |
| `~/can-it-ford-refs/2026-08-19-r10/` | EXISTS, 38 verified PDFs | `[read]` deliberately outside the public repo |
| `data/r10_acquired/` | DOES NOT EXIST | `[read]` gitignored; R10 section 5 records the mirror into `docs/r10/` |
| `docs/CORPUS_MERGE_FINAL_2026-08-22.md` | this file | new |

### 0.1 R10 was never missing. My search was.

At 01:23 a `find` across the main checkout and all 12 worktrees returned nothing for
`R10_WEB_ACQUISITION_2026-08-19.md` `[read]`. At 01:30 the file was present `[read]`.

Nothing was created in between. The file had been sitting on branch `claude/r9-gapscan`
since 2026-08-20, reachable from a ref the whole time, and `git branch -a --contains`
confirms it `[read]`. There was no `r9-gapscan` worktree, so no filesystem path held it.
A concurrent session then merged five `r9/*` branches into `claude/add-ci-checks` at
01:30:02 to 01:30:03, per the reflog `[read]`, and the file materialised.

This is the standing rule in CLAUDE.md under "Claim discipline" doing exactly what it
says: a checkout that is behind cannot prove a file never existed, and absence of evidence
from a partial view is not evidence of absence. **A filesystem `find` is not a repository
search.** The correct instrument is `git log --all --diff-filter=A -- <path>` or
`git branch -a --contains`.

Consequence for this document: every count below was re-derived **after** the merge, at
`d1490df`. The pre-merge numbers are discarded, not reported.

### 0.2 The same error, a second time, on the priority read

I recorded `10.1016/j.jcp.2016.10.064` as unobtainable after its only open-access location
returned HTTP 500 to curl, HTTP 403 to a second route, and a Cloudflare bot check in the
browser, which I did not attempt to bypass `[read]`. That was true of **tonight's web
routes** and false as a statement about availability: the PDF had been acquired on
2026-08-20 and sits at
`~/can-it-ford-refs/2026-08-19-r10/Zha17c_10.1016_j.jcp.2016.10.064.pdf` `[read]`. My disk
sweep covered Downloads, Desktop, Documents, Zotero and `citations/`, and did not cover
`~/can-it-ford-refs/`, which is the one tree built to hold acquired papers.

Both misses share a shape: a negative result stated without naming the view it was taken
from. Both are recorded here rather than quietly corrected.

---

## 1. The accounting: all 138, by what they actually reach

Source list: `Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv`.
Re-counted live: 205 data rows, 138 with `cited_anywhere_in_repo=NO`, all 138 DOIs
distinct, 67 `YES` `[read]`. The 138 is confirmed, not relayed.

**Scope, stated because this count is scope-sensitive.** Tree walked: `/Users/josie/can-it-ford`
at `d1490df`, extensions `.md .tex .bib .txt .json .py .csv .tsv .yaml .yml .sh`, 1,591
files. Excluded: `.git/`, `third_party/`, `__pycache__/`, `archive/`, `_archive/`,
`session_archive/`, `.claude/worktrees/`, and `*.bak*`. The worktree exclusion is
load-bearing: 28 worktrees under `.claude/worktrees/` would multiply every hit.

| status | count | what it means |
|---|---|---|
| `BIB` | **3** | has an entry in `paper/can_it_ford_references_IEEE.bib` |
| `PROSE` | **32** | DOI appears in a `.md` or `.tex` under `docs/`, `paper/`, `deliverables/`, `citations/` |
| `MANIFEST` | **22** | reaches a reader-facing directory only as a machine `.tsv`, `.json` or `.log`, all of them R10 acquisition manifests |
| `INDEX` | **79** | reaches only `data/research_corpus_index.json` or an internal `.claude/` file |
| `ABSENT` | **2** | DOI string appears nowhere in the scoped tree |
| **total** | **138** | |

Full row-by-row table in the appendix. **No DOI is dropped: the five buckets sum to 138
and every DOI is printed by name.**

### 1.1 The number that matters: zero

`overleaf/main:conference_101719_1.tex` carries **14 distinct `\cite` keys** `[read]`, and
its shipped bibliography holds **15 entries** `[read]`. This is the canonical submitted
paper, per the standing note that the Overleaf tex is canonical.

**None of the 138 is among them.** `[read]`

The three `BIB` rows are entries in the **repo-local** `paper/can_it_ford_references_IEEE.bib`,
which holds 42 entries, not the shipped 15. Their keys are `khapane2014wading`,
`syamlal2017uncertainty` and `bergmann2021mser`, and none is `\cite`d in either tex
`[read]`. They are staged, not printed.

So the honest top of the ladder is: **138 catalogued, 3 staged in a non-shipped
bibliography, 0 printing in the paper.**

### 1.2 Why `MANIFEST` is separated from `PROSE`

A naive reader-facing count returns 54. Splitting prose from machine files returns 32 plus
22 `[read]`. The 23 reach `docs/r10/*.tsv`, which are R10's own acquisition manifests: a
row recording that a fetch returned HTTP 500 is not a citation.

This is the same inflation CLAUDE.md already records for the research corpus, where a raw
connector dump inflated a reader-facing count by exactly 9. Reporting 54 here would repeat
that error with a different file. **Both numbers are correct and they answer different
questions; a bare number is what is wrong.**

### 1.3 The caveat that most limits this whole accounting

**"Uncited" throughout means "DOI string absent". It does not mean the project does not
know the work.**

Worked counter-example, confirmed `[read]`: `10.1061/(asce)0733-9429(2002)128:12(1069)`,
Dancey et al 2002, "Probability of Individual Grain Movement and Threshold Condition",
is classified `INDEX` because its DOI appears in no prose. Yet "Dancey" appears in
`CLAUDE.md`, in `docs/HANDOFF_2026-08-18_REALISTIC_ENVIRONMENT.md`, in
`docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md`, and in `analysis/probabilistic_verdict.py`,
whose entire design rests on that paper's probability-of-movement criterion.

Scale of the gap, as an **upper bound**: of the 101 rows where the resolved first-author
surname is long enough to search, 46 have that surname somewhere in reader prose, and 19
of those sit in the 79 `INDEX` rows `[read]`. A bare surname cannot distinguish this paper
from a different paper by an author of the same name, and surnames like Zhang, Li and Chen
are common in this corpus, so **46 is an upper bound with a high false-positive rate, not
a count.** The Dancey case is the one I confirmed individually.

### 1.4 Two measurement hazards, both hit during this pass

**The tree moved while I measured it.** A concurrent session merged `r9/*` branches into
this branch three times during this session, at `d1490df` and again at `fe638d5` `[read,
reflog]`. Re-deriving the ladder at `fe638d5` moved exactly one row:
`10.1016/j.compfluid.2018.09.005`, "v-p material point method for weakly compressible
problems", went from `MANIFEST` to `PROSE` because the `r9-jobb-route` merge brought in
`docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md`, which names it. The table below is the
`fe638d5` state. Any re-run on a later commit may differ again, and that is a property of a
shared working tree, not an error.

**This document contaminates its own measurement.** The appendix prints all 138 DOIs in
`docs/`, so a naive re-run of the diff scores 138 of 138 as reaching reader prose and 0 as
absent `[read, observed]`. Any future re-run **must exclude
`docs/CORPUS_MERGE_FINAL_2026-08-22.md`**, exactly as the corpus index must be excluded for
the same reason. Every count in this file was produced with that exclusion in place.

---

## 2. The two priority reads

### 2.1 `10.1007/s00466-019-01783-3` READ IN FULL, and no prior slot had touched it

González Acosta, Vardon, Remmerswaal and Hicks, "An investigation of stress inaccuracies
and proposed solution in the material point method", Computational Mechanics 65(2)
555-581, published online 2019-11-14, print 2020-02, CC-BY-4.0. Title verified against
Crossref, verdict `matched`, confidence high `[read]`.

**This DOI appears nowhere in `docs/r10/`, in any R10 manifest, or in
`R10_WEB_ACQUISITION_2026-08-19.md` `[read]`.** The d22-gapscan slot never reached it. So
this read is new work, not a repeat, and it was pending precisely because no want list
contained it.

Read in full via the Undermind connector `[read]`. What it establishes:

- Stress oscillation in MPM has three named causes: poor force and stiffness integration,
  stress recovery inaccuracies, and cell crossing.
- Cell crossing corrupts the **distribution of internal nodal forces**, not only their
  magnitude. In the paper's Fig 11d the analytic vertical force is zero while the computed
  horizontal nodal forces take both positive and negative values. That is a **sign** error
  in a nodal force, not a magnitude error.
- The errors are mesh-position dependent, so refining the grid without a fix **increases**
  the frequency of cell-crossing events, which the paper names as the source of its "large
  imbalance" and "large oscillations".
- GIMP alone makes stiffness integration **worse**, a maximum decrease of -33.95 percent
  against regular MPM's -7.38 percent, at 4 material points per cell.

### 2.2 `10.1016/j.jcp.2016.10.064` READ IN FULL, from the copy already on disk

Fan Zhang, Xiong Zhang, Kam Yim Sze, Yanping Lian, Yan Liu, "Incompressible material point
method for free surface flow", J. Comput. Phys. 330:92-110, 2017. Title verified against
Crossref, verdict `matched`, confidence high `[read]`. Identity of the PDF confirmed
against its own first page, which carries the title, the five authors, the citation and
the CC-BY-NC-ND licence `[read]`. 36 pages, the HKU submitted version.

R10 reached this one at abstract level only and logged HTTP 500 from the same handle I hit
`[read]`. My curl attempt three days later returned the identical 500. Those are two
independent origins, R10's fetch log and my own run, so the barrier is corroborated. It is
also now moot, because the fifth-pass acquisition recorded in R10 section 5 succeeded and
the file is on disk.

What it establishes, all read from the paper's own text:

- Its stated purpose is "to overcome the shortcomings of the weakly compressible material
  point method (WCMPM)". The canonical solver here is weakly compressible.
- It names two specific WCMPM defects. First, the EOS "relates pressure to density of the
  fluid by an artificial sound speed, which is normally taken as 10 times higher than the
  maximum fluid velocity in order to reduce the density fluctuation down to 1%". Second,
  "the material surface is not explicitly tracked in MPM, so it is difficult to accurately
  impose the pressure boundary condition".
- On its dam-break case: "due to the weakly compressible equation of state and
  crossing-cell noise, the pressure obtained by WCMPM soon shows high-frequency
  oscillations", and critically "the WCGIMP ... has little contribution to eliminate the
  high-frequency pressure oscillation and non-physical spray over time".
- **It contains no buoyancy test and no rigid body.** Live term counts over the extracted
  text: "buoyan" 0, "still water" 0, "hydrostatic" 3, "rigid" 2 `[read]`. **The
  `hydrostatic` figure read 1 until 2026-08-22 and was corrected to 3 by an independent
  re-derivation from the PDF on disk; see section 6.3, which also shows why the finding is
  unaffected.** Both "rigid"
  hits describe the background grid being "rigidly attached to the particles". Its
  numerical examples are dam break, oscillation of a cubic liquid drop, and droplet impact
  into a deep pool.

**A limit on the transfer, stated because it cuts against the argument.** Zha17c's WCMPM
baseline uses Morris's EOS, `p = c^2 rho`, its Eq. 20, at a numerical sound speed of
50 m/s `[read]`. This project's solver uses `pressure = -bulk*(J**-gamma - 1)` with
`gamma = 1.1`, which is the Monaghan/Tait family, its Eq. 19, and at a different exponent
from the `gamma = 7` Zha17c quotes for water. The two are both weakly compressible and
they are not the same closure. The qualitative finding transfers to the class; the
specific numbers do not transfer to this solver.

### 2.3 Do either change `docs/COUPLING_VALIDATION_J1_2026-08-07.md`?

**One sentence in J.1 is weakened. The verdict is not.**

J.1 concludes that C0 passes, C1 ran and failed with the sign inverted at both resolutions
and diverging under refinement from -122.03 to -325.87 percent, C2 produced no number at
any resolution, C3's metric is undefined by construction, and J.1 is not closeable `[read,
from the file]`. **Nothing in either paper touches any of that, and none of it changes.**
C2 is blocked by a P2G edge guard, which is a scene-geometry problem no literature can
resolve, and C3 is a divide-by-zero in the test's own criterion.

What does change is one **inferential step**. J.1 argues: "Refinement moving the answer
away from the target is the signature of a wrong term, not an under-resolved one."

That inference is now less safe. Aco19 documents the opposite case in standard MPM:
because its errors are mesh-position dependent, refining the grid increases cell-crossing
frequency and therefore increases the imbalance `[read]`. Divergence under refinement is
therefore **also** the documented signature of an unfixed cell-crossing and quadrature
error, not uniquely of a wrong term. The project already accepts this mechanism in the
other direction: CLAUDE.md's L-5 cites Steffen, Kirby and Berzins 2008 as the citable
mechanism for MPM losing convergence under refinement, and uses it for the g48/g64/g96
displacement non-monotonicity. Aco19 cites Steffen 2008 twice in its own deposited
reference list `[read, from the Crossref deposit]`. **So this is the argument the project
already accepts for displacement, extended to the force and stress path.** J.1's sentence
should be softened to say that divergence under refinement is consistent with a wrong
term and also with an unfixed quadrature error, and that the two are not separated by the
data in hand.

Why this is a live candidate here specifically, and not a generic caution. J.1 records
that material 8 particles carry `F = I` with no stress branch, so the rigid body's own
particles deposit mass and momentum and never stress, and that `v_cm_new = rigid_linear_mom / M`
with no force term `[read, from the file]`. **The buoyant force reaching the body is
therefore transmitted entirely through the water particles' nodal internal forces**, which
is exactly the quantity Aco19 shows can be sign-wrong and mesh-position dependent at cell
boundaries. That is a specific, literature-backed candidate mechanism for a sign-inverted
buoyant force, where J.1 currently has only "a wrong term".

Zha17c independently reaches the same pair of causes from the fluid side: it names the
weakly compressible EOS **and** crossing-cell noise together as the cause of WCMPM pressure
oscillation `[read]`. Aco19 (solid mechanics, implicit, quasi-static) and Zha17c (free
surface fluid, explicit) are different groups, different regimes and different journals,
converging on cell crossing. **That is genuine corroboration with separate origins.** It
also constrains the remedy: Zha17c reports that GIMP does not eliminate the pressure
oscillation, and Aco19 reports that GIMP alone makes stiffness integration worse. Neither
supports "switch to GIMP" as a fix.

**Three reasons this does not overturn J.1, stated so the argument is not oversold.**

1. Neither paper's regime matches J.1's scene. Aco19 is implicit, quasi-static,
   single-phase solid geomechanics. Zha17c has no rigid body at all. The transfer is by
   mechanism, not by matching configuration, and is therefore `[inferred]`, not a result.
2. The magnitudes do not obviously reach. Aco19 quantifies stiffness-magnitude error at
   -7.38 to -33.95 percent. J.1's C1 error is -122 to -326 percent with an inverted sign
   on the net force. Cell crossing is not shown to be sufficient to produce that.
3. Neither paper supplies a buoyancy validation target, so neither closes J.1's C2, which
   is the Archimedes test J.1 names first and which has never produced a number.

**Net: J.1 stays open, its verdict stands, and it gains one named candidate mechanism plus
a correction to one inferential sentence.** Recorded here rather than edited into
`COUPLING_VALIDATION_J1_2026-08-07.md`, because that file belongs to the coupling session
and this is a claim about it, not a measurement of it.

**Both reads are UNREVIEWED.** The physics-skeptic path is recorded in CLAUDE.md as having
been dead fleet-wide on 2026-08-19 and alive again on 2026-08-20. I did not run it, so per
the same section's own rule I mark these claims unreviewed rather than assume either state.

---

## 3. Title verification: no fabrications, no retractions, one erratum

Two passes were run, and the second is the one the dispatch actually asked for.

**Pass A, raw registry plus a similarity ratio.** Crossref first, DataCite for the
failures, comparing catalogued title to resolved title with a `difflib` ratio `[read]`.
136 of 138 resolved. This is a proxy for the real check and it cannot see retractions.

**Pass B, Scholar Sidekick `auditBibliography`, 6 batches of at most 25, all 138 `[read]`.**
This is the named instrument. It runs the Topaz fabrication check, a real-DOI-plus-invented-
title cross-check that `resolveIdentifier` cannot catch, plus a retraction lookup.

| verdict | count | meaning |
|---|---|---|
| `matched` | **134** | claim agrees with the resolved record |
| `mismatch` | **0** | the fabrication pattern. **None found.** |
| `ambiguous` | **3** | see below, all three benign |
| `not_found` | **0** | |
| errored | **1** | tool-side, see below |
| **retracted** | **0** | |
| expression of concern | **0** | |
| **has corrections** | **1** | see below |

### 3.1 The one actionable result: an erratum nobody had found

`10.1016/j.joes.2018.05.002`, "Water entry and exit of axisymmetric bodies by CFD
approach", carries a publisher-recorded **Erratum at `10.1016/j.joes.2020.11.003`, dated
2021-03-01** `[read]`. Not retracted, no expression of concern.

This is the payoff of running the named instrument rather than a similarity ratio, which
is blind to it. **No prior pass in this project has ever checked retraction or correction
status on any of these papers.** The paper is on water entry and exit of a body, which is
the J.1 problem class, so if it is ever cited the erratum must be cited with it.

### 3.2 The 3 `ambiguous` verdicts are a search artifact, not citation errors

All three are ASCE Journal of Hydraulic Engineering DOIs carrying parentheses. In every
one the **top candidate returned by the tool's own title search is the DOI I supplied,
with an identical title**, at confidence `high` `[read]`. The verdict is `ambiguous` only
because the title search also returned unrelated low-relevance candidates, for instance
"Do magnetars really exist?" against "Do Critical Stresses for Incipient Motion and
Erosion Really Exist?". Identifier and title agree in all three. Read as 137 clean.

The 1 errored entry is the Springer chapter `10.1007/978-3-319-22997-3_11`, which resolved
normally in pass A `[read]`, so the error is the tool's, not the DOI's.

### 3.3 Pass A's three low-similarity rows, explained

The same 3 ASCE rows. Their catalogued titles carry a trailing markdown fragment,
`(\[link\](https://doi.org/...`, glued on by the TSV builder. Stripped of it they match
their resolved records exactly: Dancey 2002, Lavelle 1987 and Papanicolaou 2002 `[read]`.
A builder defect, not a fabrication, and pass B confirms it independently.

### 3.4 Two DOIs are unregistered, and that has a consequence beyond these rows

`10.3970/cmes.2004.005.477` and `10.3970/cmes.2005.008.135`, both Tech Science Press CMES.
The prefix resolves in neither registry. **The works are real**: the first is Bardenhagen
and Kober 2004, the foundational GIMP paper, and it appears as a full reference in Aco19's
own Crossref deposit, "Bardenhagen SG, Kober EM (2004) The generalized interpolation
material point method. Comp Model Eng Sci 5(6):477-495" `[read]`. A third party's deposited
reference list is an independent origin from the catalogue row.

CLAUDE.md's L-5 rests on Steffen, Kirby and Berzins 2008 at `10.3970/CMES.2008.031.107`,
the same undeposited prefix. **Any future citation audit that treats "DOI does not resolve"
as "citation is bad" will flag L-5 wrongly.** It is not bad; the publisher does not deposit.

---

## 3.5 Register G25, checked against its own falsifier

G25 sits in the corrections register and triages these same nine multi-report papers. It
states its own falsifier: it "dies if the catalogue is re-parsed and yields other than 205
data rows, 138 uncited, or other than 9 uncited rows whose `in_reports` field contains a
`+`". Re-parsed live: **205, 138, 9** `[read]`. **The falsifier does not fire.**

G25a records two catalogue defects. Both are confirmed here and one is extended.

- **`khapane2014wading` is in the bib and not cited.** G25a says state it as "in the .bib,
  not yet cited in the body", never as "cited". Confirmed independently: the key appears in
  no `\cite` in either `paper/conference_101719.tex` or `overleaf/main` `[read]`. Two
  separate origins agree.
- **`10.1504/pcfd.2019.10018820` is a pre-publication Inderscience id**, redirecting to the
  article of record `10.1504/PCFD.2019.097597`. Confirmed: direct Crossref returns HTTP 301
  and `doi.org` lands on `PCFD.2019.097597` `[read]`.
- **EXTENDING G25a: there is a second one, which G25a does not name.**
  `10.1504/pcfd.2016.10001222` behaves identically, HTTP 301 at Crossref, resolving to
  **`10.1504/PCFD.2018.089497`** `[read]`. Note the year moves too, catalogue 2016 against
  article of record 2018, a larger discrepancy than the first. **The appendix below prints
  the catalogue's pre-publication form for both rows.** Cite the article of record.

## 3.6 Three premises in the dispatch, checked rather than assumed

- **"11 of 14 works the paper cites are absent from the 332."** CONFIRMED, 11 absent and 3
  present `[read]`, but **only by title matching**. A DOI diff is impossible: all 14 cited
  entries in the shipped bib carry **no `doi` field at all** `[read]`. The 3 present are
  exactly the flood-vehicle-stability works, `smithmodrafelder2019`, `xia2014` and
  `azhar2023`. The 11 absent split cleanly into the reconstruction and engine stack (3DGS,
  PhysGaussian, NeRF-MPM, Genesis, PVWM, FRED) and the primary-source documents (AR&R,
  NHTSA inertia, CCSA Yaris validation, NWS TADD, shah2018). **The corpus covers this
  project's flood-stability literature and none of the method stack it actually runs on.**
- **"The index does not contain roughly 13 of the ~21 deep searches."** `data/deep_searches/`
  now holds **22** search JSONs and **0 of the 22 carries a `papers` array** `[read]`, so no
  paper record can enter the index from any of them. The index's own `deep_searches` list
  holds 21 `[read]`.
- **"Nothing past Aug 13 reached the remote."** FALSE as of now. `origin/claude/add-ci-checks`
  exists and its tip carries work from 2026-08-22, including this file `[read]`.

---

## 4. What is still open, named

1. **0 of 138 are cited in the submitted paper**, and the corpus is still not a superset
   of the bibliography. This is unchanged by anything here.
2. **136 of 138 have not been read in full.** Only 4 have full text on local disk, and I
   read 2 of those 4 this session. Acquiring is not reading, and cataloguing is neither.
3. **Open access, measured `[read]`:** 50 of 138 are open access by Unpaywall, 74 are
   closed, and 14 returned no Unpaywall answer, 11 of those being 2025-2026 arXiv DOIs
   that Unpaywall does not cover. **The 74 closed need institutional access, not a better
   script**, which independently reproduces R10's own finding of 105 closed across its
   larger 230-item want list.
4. **The 2 `ABSENT` rows** are Lavelle 1987 and Papanicolaou 2002, both incipient-motion
   sediment-transport papers, both `closed` access, both single-report. They are the only
   two of the 138 with no trace of any kind in the repo.
5. **The cheapest remaining read is already on disk and unread**:
   `10.1016/j.proeng.2017.01.041`, "Numerical simulations of dam-break floods with MPM",
   one of the nine highest-signal gaps, at
   `~/can-it-ford-refs/2026-08-19-r10/Zha17_10.1016_j.proeng.2017.01.041.pdf` `[read, file
   exists]`.
6. **Two of the nine highest-signal gaps remain unobtained and closed**:
   `10.1016/j.cma.2022.114809` (IFEMP, 4 reports, the joint top-ranked gap) and
   `10.1504/pcfd.2019.10018820` (benchmarking MPM for free-surface-plus-body, 3 reports).
   The second is a benchmark for exactly the configuration J.1 fails on.
7. **A cluster nobody has triaged.** 11 of the 138 are 2025-2026 arXiv papers on AI agents
   for scientific computing, including "Can Coding Agents Reproduce Findings in
   Computational Materials Science?", "AInsteinBench", and "Bridging the Gap on AI-Assisted
   Scientific Software Development Through Transparency and Traceability" `[read]`. These
   bear on the reproducibility-record contribution, not on flood physics, and no document
   in this repo engages them. Whether they belong in the paper is a scope decision, not a
   research one.
8. **Unreviewed.** No claim in this file was checked by the physics-skeptic path.
9. **The surname figure of 46 is an upper bound**, not a count. Resolving it properly needs
   per-row inspection, which was not done.
10. **The erratum is unactioned.** `10.1016/j.joes.2018.05.002` has an erratum at
    `10.1016/j.joes.2020.11.003`. Nothing cites the paper yet, so nothing is wrong today,
    but the pairing must travel with it if it is ever cited.
11. **Retraction status is now known for these 138 and for nothing else.** The paper's own
    15-entry bibliography has never been run through a retraction check. That is a one-call
    job and it is the obvious next use of this instrument.
12. **Two appendix rows carry pre-publication DOIs**, per section 3.5. They resolve, and they
    are not the form to print in a bibliography.
13. **The catalogue itself is now 8 days stale.** It was built 2026-08-14 against a tree that
    has since absorbed roughly 20 branch merges. Re-running its builder is the honest way to
    keep this accounting alive, and the builder lives in a prior session's scratchpad, so it
    may no longer exist.

---

## 5. Files and how to re-derive

Working files, session scratchpad, not committed: `rediff.py` (the tree diff),
`verify138.py` (Crossref plus DataCite plus Unpaywall), `rediff.json`, `verify138.json`.

Re-derive the 138 from the source list:

    /usr/bin/awk -F'\t' 'NR>1 && $8=="NO" {print $1}' \
      "$HOME/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv" \
      | sort -u | wc -l

Re-derive the paper's cite keys, which is the only test of what actually prints:

    git -C ~/can-it-ford show overleaf/main:conference_101719_1.tex \
      | /usr/bin/grep -o '\\cite{[^}]*}' | sed 's/\\cite{//;s/}//' | tr ',' '\n' | sort -u

---

## 6. Second-eyes verification pass, 2026-08-22, and one erratum in this file

Run by a separate session against the committed file, measured at `88672a0` and re-checked
at `ef2395e`. The purpose was to test this document's own load-bearing claims rather than
repeat them, on the principle stated at the top of this file that one source cited twice is
not two sources. Every row below is `[read]`, run this session.

### 6.1 What reproduced exactly

| claim in this file | how I re-derived it, independently | verdict |
|---|---|---|
| 205 TSV rows, 138 with `cited_anywhere_in_repo=NO`, all distinct | `csv.DictReader` over the source TSV, `Counter` on the column: 205 rows, NO=138, YES=67, 138 distinct, 0 duplicates | reproduces |
| all 138 printed by name, none dropped | parsed the appendix: 138 numbered rows, 138 distinct DOIs, set difference against the TSV computed both directions | reproduces, **0 missing, 0 extra** |
| committed and pushed | local `HEAD` and `refs/heads/claude/add-ci-checks` on `origin` were both `88672a09c24efeac74e3d0ad3374d0594444f350`, and `ls-tree` finds the file in that commit | reproduces |
| `10.1007/s00466-019-01783-3` title is genuine | Scholar Sidekick `verifyCitation`: `matched`, confidence high | reproduces |
| `10.1016/j.jcp.2016.10.064` title is genuine | Scholar Sidekick `verifyCitation`: `matched`, confidence high | reproduces |
| Aco19 cites Steffen 2008 twice | read the Crossref deposit: keys `1783_CR26` and `1783_CR27` are two distinct Steffen 2008 papers | reproduces |
| Aco19's three named causes of oscillation | the Crossref abstract names poor force and stiffness integration, stress recovery inaccuracies, and cell crossing, verbatim | reproduces |
| the erratum | `checkRetraction` on `10.1016/j.joes.2018.05.002`: not retracted, one erratum at `10.1016/j.joes.2020.11.003`, dated 2021-03-01 | reproduces |
| 14 cite keys, 15 bib entries, `xiong2024` never cited | parsed `overleaf/main:conference_101719_1.tex` and its bib live | reproduces |
| Zha17c term counts | `pdftotext` over the PDF on disk, then `/usr/bin/grep -o -i` | **3 of 4 reproduce, see 6.3** |

### 6.2 One claim strengthened, by a second and genuinely independent predicate

Section 1.1 establishes that none of the 138 is cited in the paper using **cite keys**. I
tested the same claim using **title similarity**, a different predicate over the same two
sets: each of the 14 cited works was fuzzy-matched against all 138 resolved titles.

The highest similarity any pair reaches is **0.52**, and nothing crosses 0.60. Zero pairs
approach a match. Cite-key identity and title similarity have separate origins, so this is
corroboration rather than the same source counted twice.

**A caveat section 1.3 does not cover, and the reason this test had to be run on titles.**
All 14 entries in the shipped bibliography carry **no `doi` field whatsoever** `[read]`. A
DOI join between the 138 and the paper is therefore **vacuous**: it returns zero by
construction, and would still return zero if the paper cited every one of the 138. Section
1.3's caveat is that a DOI string can be absent from the repo tree while the work is known,
which is a different failure. Anyone re-testing "does the paper cite this work" must match
on title or on key, and must never match on DOI until the bib gains DOI fields.

### 6.3 ERRATUM: the `hydrostatic` count in section 2.2 was 1 and is 3

Section 2.2 reported live term counts over the extracted text of Zha17c as
`"buoyan" 0, "still water" 0, "hydrostatic" 1, "rigid" 2`.

Re-derived from `~/can-it-ford-refs/2026-08-19-r10/Zha17c_10.1016_j.jcp.2016.10.064.pdf`
with `pdftotext`, then `/usr/bin/grep -o -i` `[read]`:

    "buoyan"       0    agrees
    "still water"  0    agrees
    "hydrostatic"  3    DISAGREES, this file said 1
    "rigid"        2    agrees

This is not a counting-semantics artifact. `grep -c`, which counts lines, and `grep -o`,
which counts occurrences, both return 3, because the three hits sit on three separate
lines. The likeliest mechanism is that the two passes extracted the PDF with different
tools, so the original figure is not reproducible from the copy on disk.

**The conclusion of section 2.2 is unaffected, stated explicitly so this erratum is not
read as larger than it is.** The count was offered as evidence for "it contains no buoyancy
test and no rigid body". All three `hydrostatic` hits were read in context:

1. The constitutive decomposition of stress into deviatoric plus hydrostatic pressure,
   `sigma_ij = -p delta_ij + s_ij`, which is generic MPM formulation text.
2. The initial pressure distribution in the dam-break case, at the very beginning of the run.
3. Hydrostatic pressure being dominant in low-viscosity flow, in the comparison against
   Lobovsky's experimental data.

None of the three is a buoyancy test and none involves a rigid body. Both `rigid` hits were
also read and both are the background-grid sentence section 2.2 already describes. **The
number is corrected and the finding stands.**

Recorded here rather than silently patched, per this document's own rule in the appendix
preamble: quietly editing a number so a claim reads clean is the exact defect this file
exists to detect.

### 6.4 What this pass did NOT do, so its scope is not overstated

It did not re-read either priority paper end to end, and so does not independently confirm
the interpretive claims in sections 2.1, 2.2 and 2.3 beyond the specific items listed in
6.1. It did not re-run the 138-row Crossref, DataCite and Unpaywall sweep, so the `id` and
`OA` columns of the appendix are `[relayed]`, not re-derived. It did not re-check the
`INDEX` versus `PROSE` bucket assignment of any individual row; the appendix test was set
membership only, which proves no DOI was dropped and proves nothing about which bucket each
landed in. It did not run the physics-skeptic path, so section 4 item 8 stands unchanged:
**no claim in this file has been adversarially reviewed.**

---

## 7. The `claude/r9-corpus-bib` conflict, diagnosed 2026-08-22, and NOT resolved

Every claim in this section is `[read]` from a live command against the main checkout at
`/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `3262118`, unless tagged
otherwise. This is the dependency no prior dispatch named, and nobody had stated what the
conflict actually was.

### 7.1 What conflicts, exactly

Merge base `af62473`. The deprecated three-argument `git merge-tree` reports **zero**
conflict markers here and is misleading; the authoritative form is
`git merge-tree --write-tree`, which exits 1 and names three files `[read]`:

| file | conflict | hunks |
|---|---|---|
| `.claude/skills/research-corpus/SKILL.md` | content | 4 |
| `analysis/research_index.py` | content | 4 |
| `data/deep_searches/vehicle-mesh-assets.json` | **add/add** | 1 |

The add/add is a genuine content difference, compared by md5 rather than by size per the
standing rule: `3e192cb7e9706a555bfc66cf7365c256` (3,020 bytes) on `add-ci-checks` against
`1d1567868e887cd1225de0b281402cc3` (12,085 bytes) on the branch `[read]`.

**Three of the branch's six files are clean adds and carry no conflict at all**:
`docs/R9_CORPUS_BIB_GAP_2026-08-18.md` (1,711 lines), `data/r9_bib_corpus_census.tsv`, and
`data/deep_searches/buoyancy-overestimation.json`, the last confirmed absent from
`add-ci-checks` by `git cat-file -e` returning `does not exist` `[read]`. So the branch's
content is readable in full without merging, which is the route taken here.

### 7.2 Verdict: SUBSTANTIVE. Reported, not resolved.

The dispatch's test is whether this is mechanical (two sessions touching one file in
non-overlapping ways) or substantive (claims that disagree). It is substantive, for three
measured reasons, and the third is the one that decides it.

**(a) `--source-audit` is declared on both sides with different semantics.** Ours reports
`deep searches known: 21`, `reaching the corpus AS PAPERS: 8 of 21`, and exits `FAIL (13
problem(s))` `[read]`, which is exactly what CLAUDE.md documents as current behaviour. The
branch's own tip commit says its `--source-audit` "still exits 1 naming 11 unreachable
searches" `[read]`. Same flag name, two predicates, two counts. A naive union raises
`argparse.ArgumentError` on the duplicate; choosing changes what the tool reports and makes
one of the two documents describing it false.

**(b) Neither side is a superset today.** `--searches` exists only on ours and is absent
from the branch entirely `[read]`. `--bib-audit`, `--coverage`, `--identifier-audit`,
`--ingest-check`, `--against-slug` and `--out` exist only on the branch `[read]`. A
take-mine on `research_index.py` drops the metadata ingest that makes 21 of 21 searches
reachable and the 2026-08-21 predicate change, both of which CLAUDE.md publishes as
current. A take-theirs drops the branch's whole bibliography census.

**(c) The branch's own landing plan is now false, and it is the plan a lander would
follow.** Part 5 section 33 states `analysis/research_index.py` on `add-ci-checks` is
"untouched, blob `b775b31` identical to base", concluding "the file that fixes `--query`
lands without a conflict at all", and its procedure at section 34 says "EXPECT A CONFLICT
IN SKILL.md AND ONLY THERE" `[read]`. Live, all three parts are false: the blob is
`7d8c46e`, **three** commits touched that file after the base (`de891a9`, `3400e2b`,
`924c180`), and **three** files conflict rather than one `[read]`.

That is not an error by the branch. It was true when written on 2026-08-20 and
`add-ci-checks` invalidated it afterwards. The branch dissolved the union deliberately,
recording "the cheapest move was to make the measurement false"; `add-ci-checks` then
re-created it. **A merge plan is a measurement and it goes stale like any other.**

### 7.3 The three claims the branch says a naive merge would reintroduce, checked one by one

The branch warns "DO NOT take `add-ci-checks`' SKILL.md content", naming three refuted
claims. Checked individually rather than accepted as a block, because the warning is the
load-bearing reason not to take our side:

1. **"256 are cited nowhere": FALSE POSITIVE, the two sides agree.** `add-ci-checks` does
   not assert it. Its SKILL.md reads **"DO NOT SAY '256 ARE CITED NOWHERE'. That clause was
   WITHDRAWN 2026-08-18"** `[read]`. A string match found the numeral and not the polarity
   of the sentence around it. This is the same defect the branch documents elsewhere as an
   inflated count travelling further than an empty one.
2. **"nineteen completed deep searches" against 21: CONFIRMED, and our own instrument is
   the witness.** Our SKILL.md says the workspace holds "19 completed deep searches"
   `[read]`, while our own `--source-audit` prints "deep searches known: 21" `[read]`, and
   `data/deep_searches/` holds 22 files of which one is `MANIFEST.json`, leaving 21
   searches `[read]`. `add-ci-checks` is internally inconsistent and the branch is right.
3. **`df52bee` against `50b70c0`: CONFIRMED.**
   `git log --all --diff-filter=A -- tests/test_physics_gates.py` returns **`50b70c0`**
   `[read]`. `df52bee` is a real commit but did not add that file, so our SKILL.md line
   attributing it is wrong.

So two of the three warnings hold and one does not. **That distinction matters for the
resolution**: it means our side carries two known defects rather than three, and one of the
branch's stated reasons for a wholesale take-mine does not survive checking.

### 7.4 Effect on the 138: none, and this is measured rather than assumed

`docs/R9_CORPUS_BIB_GAP_2026-08-18.md` contains **zero** occurrences of "138" and **zero**
of "G25" `[read]`. Its subject is the 15-entry shipped bibliography against the corpus,
which is a different set from register G25's 138 catalogued-but-uncited DOIs. Both priority
DOIs appear in it, at lines 1170 and 1647, but as list mentions inside other arguments and
not as reads `[read]`.

**Therefore the conflict did not block the accounting.** Sections 1 through 6 and the
appendix stand exactly as they were, and the branch's content was read in full without
merging. What the conflict blocks is the landing of the corpus tooling, not this document.

### 7.5 What needs Josie, stated so it is not mistaken for done

The branch's section 37 already says "what needs a human, and what I will not decide", and
this session agrees with it and adds one item. Nothing below was executed. No merge, no
branch, no push of any of it.

1. **Which `--source-audit` survives**, ours (paperless predicate, 13 problems) or the
   branch's (unreachable predicate, 11). They cannot both keep the flag name.
2. **Whether to land onto `add-ci-checks` at all**, or hold both for `origin/main`, which
   carries none of this tooling. Relayed from the branch's section 37, not re-derived.
3. **Whether to rebuild the index during the landing.** The branch measured a rebuild as
   moving 332 to 319 and cited-anywhere 76 to 66, and recommends landing the tooling
   without rebuilding so the code fix and the number change stay separately revertable.
   Relayed, not re-derived.
4. **New here:** the branch's landing procedure must be re-measured before it is run. It
   was written against a tree that has since moved, and following it as written would meet
   a conflict in two files it says will not conflict.

One hazard the branch measured and this session did not re-test, relayed so it is not lost:
`.git/hooks/pre-commit` refuses more than 8 staged files and there is no `pre-merge-commit`
hook, so a **conflicted** merge is expected to be refused by the hook while a clean one of
any size passes. Do not read that refusal as a merge failure.

---

### 7.6 Independent spot-check of the title verification, and what it does not prove

This session did not re-audit all 138. It re-ran `verifyCitation` on a **4-row sample**
against the resolved registry record, not merely checking that the link resolves: the two
priority DOIs plus appendix rows 1 and 47. All four returned `verdict: matched`,
`confidence: high`, resolved via Crossref, with an empty `mismatches` array `[read]`:

| row | DOI | resolved title | verdict |
|---|---|---|---|
| 1 | `10.4271/2014-01-0936` | Wading Simulation - Challenges and Solutions | matched |
| 47 | `10.1063/1.449733` | Statistical errors in molecular dynamics averages | matched |
| 2.1 | `10.1007/s00466-019-01783-3` | An investigation of stress inaccuracies and proposed solution in the material point method | matched |
| 2.2 | `10.1016/j.jcp.2016.10.064` | Incompressible material point method for free surface flow | matched |

**Two honest limits on that.** All four responses carried `_cache: "hit"`, so they are the
same registry lookups the earlier full audit made rather than a fresh independent
resolution; this corroborates that the audit happened but it is **not a second origin**.
And 4 of 138 is a sample, so section 3's claim of 0 fabrications across all 138 is
**reproduced on a sample, not re-derived in full**. Anyone needing the stronger statement
should re-run the full pass rather than cite this subsection for it.

---

## Appendix. All 138, by name

`status`: BIB has a bibliography entry, PROSE reaches reader prose, MANIFEST reaches a
machine manifest only, INDEX reaches the corpus index or an internal file only, ABSENT
appears nowhere. `rpts` is how many Undermind reports surfaced it. `id` is Y when the DOI
resolved in Crossref or DataCite and its title matched. `OA` is the Unpaywall status,
`?` when Unpaywall returned no answer. `pdf` is Y when full text is on local disk.

Titles are reproduced verbatim from the resolved registry record. Row 28 therefore carries
an em-dash, which the house style bans in prose. It is left in place because it is part of
a published title, and silently editing a title to satisfy a style rule is the exact defect
this document exists to detect.

| # | status | rpts | DOI | title (resolved record) | id | OA | pdf |
|---|---|---|---|---|---|---|---|
| 1 | BIB | 2 | `10.4271/2014-01-0936` | Wading Simulation - Challenges and Solutions | Y | closed |  |
| 2 | BIB | 1 | `10.1002/aic.15868` | Quantifying the uncertainty introduced by discretization and time‐averaging... | Y | green |  |
| 3 | BIB | 1 | `10.1115/1.4052402` | Statistical Error Estimation Methods for Engineering-Relevant Quantities Fr... | Y | bronze |  |
| 4 | PROSE | 4 | `10.1016/j.cma.2022.114809` | An immersed finite element material point (IFEMP) method for free surface f... | Y | closed |  |
| 5 | PROSE | 4 | `10.1016/j.jcp.2016.10.064` | Incompressible material point method for free surface flow | Y | green | Y |
| 6 | PROSE | 3 | `10.1016/bs.aams.2019.11.001` | Material point method after 25 years: Theory, implementation, and applications | Y | green |  |
| 7 | PROSE | 3 | `10.1504/pcfd.2019.10018820` | Benchmarking the material point method for interaction problems between the... | Y | closed |  |
| 8 | PROSE | 2 | `10.1007/s00466-019-01783-3` | An investigation of stress inaccuracies and proposed solution in the materi... | Y | hybrid |  |
| 9 | PROSE | 2 | `10.1016/j.proeng.2017.01.041` | Numerical Simulations of Dam-break Floods with MPM | Y | gold | Y |
| 10 | PROSE | 2 | `10.1061/(asce)em.1943-7889.0000981` | Modeling of Free Surface Flows Using Improved Material Point Method and Dyn... | Y | closed |  |
| 11 | PROSE | 2 | `10.1115/1.4044632` | Experimentally Measured Hydroelastic Effects on Impact-Induced Loads During... | Y | closed |  |
| 12 | PROSE | 1 | `10.1002/cav.70024` | An Adaptive Boundary Material Point Method With Surface Particle Reconstruc... | Y | closed |  |
| 13 | PROSE | 1 | `10.1002/nag.3731` | Mapped material point method for large deformation problems with sharp grad... | Y | hybrid |  |
| 14 | PROSE | 1 | `10.1007/s11433-023-2137-5` | 3D large-scale SPH modeling of vehicle wading with GPU acceleration | Y | closed |  |
| 15 | PROSE | 1 | `10.1016/j.cma.2011.03.016` | A comprehensive framework for verification, validation, and uncertainty qua... | Y | closed |  |
| 16 | PROSE | 1 | `10.1016/j.jcp.2024.113457` | Mixed material point method formulation, stabilization, and validation for ... | Y | hybrid |  |
| 17 | PROSE | 1 | `10.1016/j.jfluidstructs.2018.06.012` | Drag, added mass and radiation damping of oscillating vertical cylindrical ... | Y | hybrid |  |
| 18 | PROSE | 1 | `10.1016/j.jnnfm.2021.104678` | Numerical investigation of non-Newtonian power law flows using B-spline mat... | Y | closed |  |
| 19 | PROSE | 1 | `10.1016/j.parco.2019.04.002` | Full-neighbor-list based numerical reproducibility method for parallel mole... | Y | closed |  |
| 20 | PROSE | 1 | `10.1017/jfm.2021.846` | Air entrapment and its effect on pressure impulses in the slamming of a fla... | Y | hybrid |  |
| 21 | PROSE | 1 | `10.1021/acs.jctc.4c00417` | pyMSER─An Open-Source Library for Automatic Equilibration Detection in Mole... | Y | closed |  |
| 22 | PROSE | 1 | `10.1021/acs.jctc.4c01359` | Robust Automated Truncation Point Selection for Molecular Simulations | Y | hybrid |  |
| 23 | PROSE | 1 | `10.1061/(asce)0733-9429(2002)128:12(1069)` | Probability of Individual Grain Movement and Threshold Condition | Y | closed |  |
| 24 | PROSE | 1 | `10.1080/00268978600100071` | Estimation of statistical errors in molecular simulation calculations | Y | closed |  |
| 25 | PROSE | 1 | `10.1080/17445302.2010.522372` | Comparison of experimental and numerical sloshing loads in partially filled... | Y | bronze |  |
| 26 | PROSE | 1 | `10.1080/17445302.2019.1615705` | Analysis of surge added mass of planing hulls by model experiment | Y | closed |  |
| 27 | PROSE | 1 | `10.1103/physreve.98.043304` | Standard error estimation by an automated blocking method | Y | bronze |  |
| 28 | PROSE | 1 | `10.1115/1.1412235` | Comprehensive Approach to Verification and Validation of CFD Simulations—Pa... | Y | closed |  |
| 29 | PROSE | 1 | `10.1175/jtech-d-17-0038.1` | On Determining Stationary Periods within Time Series | Y | closed |  |
| 30 | PROSE | 1 | `10.1504/pcfd.2016.10001222` | Material point method and smoothed particle hydrodynamics simulations of fl... | Y | closed |  |
| 31 | PROSE | 1 | `10.17736/ijope.2020.jc774` | A Blind Comparative Study of Focused Wave Interactions with Floating Struct... | Y | green |  |
| 32 | PROSE | 1 | `10.23967/eccomas.2022.228` | Quantification of time-averaging uncertainties in turbulence simulations | Y | hybrid |  |
| 33 | PROSE | 1 | `10.33011/livecoms.1.1.5067` | Best Practices for Quantification of Uncertainty and Sampling Quality in Mo... | Y | gold | Y |
| 34 | PROSE | 1 | `10.3390/app14020639` | Enabling Bitwise Reproducibility for the Unstructured Computational Motif | Y | gold | Y |
| 35 | MANIFEST | 1 | `10.1002/nme.70210` | Validating High‐Performance Multi‐GPU MPM for Debris‐Fluid‐Structure Intera... | Y | closed |  |
| 36 | MANIFEST | 1 | `10.1007/s00348-016-2211-z` | Statistical processing and convergence of finite-record-length time-series ... | Y | closed |  |
| 37 | MANIFEST | 1 | `10.1007/s00466-024-02510-3` | A displacement-based material point method for weakly compressible free-sur... | Y | closed |  |
| 38 | MANIFEST | 1 | `10.1016/j.cma.2012.06.015` | An adaptive finite element material point method and its application in ext... | Y | closed |  |
| 39 | MANIFEST | 1 | `10.1016/j.cma.2015.02.020` | A mesh-grading material point method and its parallelization for problems w... | Y | closed |  |
| 40 | MANIFEST | 1 | `10.1016/j.cma.2025.118264` | An improved MPM formulation for free surface flow problems based on finite ... | Y | closed |  |
| 41 | MANIFEST | 1 | `10.1016/j.commatsci.2026.114839` | Evaluating LLM-generated code for domain-specific languages: Molecular dyna... | Y | closed |  |
| 42 | MANIFEST | 1 | `10.1016/j.compfluid.2014.07.025` | Sloshing impact simulation with material point method and its experimental ... | Y | closed |  |
| 43 | PROSE | 1 | `10.1016/j.compfluid.2018.09.005` | v-p material point method for weakly compressible problems | Y | closed |  |
| 44 | MANIFEST | 1 | `10.1016/j.jcp.2018.05.013` | A differential variational approach for handling fluid–solid interaction pr... | Y | closed |  |
| 45 | MANIFEST | 1 | `10.1016/j.oceaneng.2019.106685` | Accurate experimental benchmark study of a catamaran in regular and irregul... | Y | closed |  |
| 46 | MANIFEST | 1 | `10.1016/j.oceaneng.2021.108983` | Quantifying uncertainty in turbulence resolving ship airwake simulations | Y | closed |  |
| 47 | MANIFEST | 1 | `10.1063/1.449733` | Statistical errors in molecular dynamics averages | Y | closed |  |
| 48 | MANIFEST | 1 | `10.1080/23863781.2019.1685921` | Estabilidad de vehículos frente a inundaciones: estudio numérico-experimental | Y | gold |  |
| 49 | MANIFEST | 1 | `10.1115/1.3241818` | Contributions to the Theory of Single-Sample Uncertainty Analysis | Y | closed |  |
| 50 | MANIFEST | 1 | `10.1115/1.4063010` | Analysis of Roll Decay for Surface-Ship Model Experiments With Uncertainty ... | Y | closed |  |
| 51 | MANIFEST | 1 | `10.1115/omae2015-41250` | Uncertainty Analysis in Ship-Model Resistance Test | Y | closed |  |
| 52 | MANIFEST | 1 | `10.1115/vvs2020-8826` | On the Interpretation and Scope of the V&amp;V 20 Standard for Verification... | Y | green |  |
| 53 | MANIFEST | 1 | `10.48550/arxiv.2512.21373` | AInsteinBench: Benchmarking Coding Agents on Scientific Repositories | Y | ? |  |
| 54 | MANIFEST | 1 | `10.48550/arxiv.2602.11666` | PhyNiKCE: A Neurosymbolic Agentic Framework for Autonomous Computational Fl... | Y | ? |  |
| 55 | MANIFEST | 1 | `10.48550/arxiv.2603.00214` | Agentic Scientific Simulation: Execution-Grounded Model Construction and Re... | Y | ? |  |
| 56 | MANIFEST | 1 | `10.48550/arxiv.2603.15976` | An Agentic Evaluation Framework for AI-Generated Scientific Code in PETSc | Y | ? |  |
| 57 | MANIFEST | 1 | `10.48550/arxiv.2605.08941` | MDGYM: Benchmarking AI Agents on Molecular Simulations | Y | ? |  |
| 58 | INDEX | 1 | `10.1002/nme.2787` | Decoupling and balancing of space and time errors in the material point met... | Y | closed |  |
| 59 | INDEX | 1 | `10.1002/nme.5956` | Conservative Taylor least squares reconstruction with application to materi... | Y | hybrid |  |
| 60 | INDEX | 1 | `10.1002/nme.6588` | Distillation of the material point method cell crossing error leading to a ... | Y | closed |  |
| 61 | INDEX | 1 | `10.1002/nme.70206` | Smoothed Particle Hydrodynamics With Anisotropic Adaptive Spatial Resolution | Y | closed |  |
| 62 | INDEX | 1 | `10.1007/978-3-319-22997-3_11` | Integration of FULLSWOF2D and PeanoClaw: Adaptivity and Local Time-Stepping... | Y | green |  |
| 63 | INDEX | 1 | `10.1007/s11340-012-9619-z` | Study on the Parameters Influencing the Accuracy and Reproducibility of Dyn... | Y | closed |  |
| 64 | INDEX | 1 | `10.1007/s13344-020-0032-6` | Uncertainty Analysis for Ship-Bank Interaction Tests in A Circulating Water... | Y | closed |  |
| 65 | INDEX | 1 | `10.1007/s40571-014-0016-5` | A particle-based multiscale simulation procedure within the material point ... | Y | bronze |  |
| 66 | INDEX | 1 | `10.1016/j.apor.2018.10.020` | Multi-resolution MPS for incompressible fluid-elastic structure interaction... | Y | closed |  |
| 67 | INDEX | 1 | `10.1016/j.cag.2018.10.007` | A hybrid Eulerian-DFSPH scheme for efficient surface band liquid simulation | Y | closed |  |
| 68 | INDEX | 1 | `10.1016/j.cma.2017.06.010` | A consistent multi-resolution smoothed particle hydrodynamics method | Y | green |  |
| 69 | INDEX | 1 | `10.1016/j.cma.2018.01.010` | Overcoming volumetric locking in material point methods | Y | hybrid |  |
| 70 | INDEX | 1 | `10.1016/j.cma.2018.06.029` | A multi-domain approach for smoothed particle hydrodynamics simulations of ... | Y | green |  |
| 71 | INDEX | 1 | `10.1016/j.cma.2018.10.049` | A consistent spatially adaptive smoothed particle hydrodynamics method for ... | Y | green |  |
| 72 | INDEX | 1 | `10.1016/j.cma.2021.114184` | Development of adaptive multi-resolution MPS method for multiphase flow sim... | Y | closed |  |
| 73 | INDEX | 1 | `10.1016/j.cma.2022.115013` | Border mapping multi-resolution (BMMR) technique for incompressible project... | Y | green |  |
| 74 | INDEX | 1 | `10.1016/j.cma.2022.115019` | Efficient and accurate adaptive resolution for weakly-compressible SPH | Y | green |  |
| 75 | INDEX | 1 | `10.1016/j.cma.2022.115356` | A block-based adaptive particle refinement SPH method for fluid–structure i... | Y | green |  |
| 76 | INDEX | 1 | `10.1016/j.cma.2023.116644` | Stabilized mixed material point method for incompressible fluid flow analysis | Y | hybrid |  |
| 77 | INDEX | 1 | `10.1016/j.compgeo.2018.04.001` | Large scale parallelisation of the material point method with multiple GPUs | Y | closed |  |
| 78 | INDEX | 1 | `10.1016/j.compgeo.2020.103716` | Reseeding of particles in the material point method for soil–structure inte... | Y | closed |  |
| 79 | INDEX | 1 | `10.1016/j.compgeo.2020.103859` | Development of an implicit contact technique for the material point method | Y | hybrid |  |
| 80 | INDEX | 1 | `10.1016/j.cpc.2019.01.002` | Adaptive resolution for multiphase smoothed particle hydrodynamics | Y | green |  |
| 81 | INDEX | 1 | `10.1016/j.cpc.2022.108377` | Parallel adaptive weakly-compressible SPH for complex moving geometries | Y | green |  |
| 82 | INDEX | 1 | `10.1016/j.enganabound.2020.02.003` | Particle transport velocity correction for the finite volume particle metho... | Y | hybrid |  |
| 83 | INDEX | 1 | `10.1016/j.jcp.2017.12.042` | Multi-resolution MPS method | Y | hybrid |  |
| 84 | INDEX | 1 | `10.1016/j.jcp.2018.09.043` | Simulation of high density ratio interfacial flows on cell vertex/edge-base... | Y | hybrid |  |
| 85 | INDEX | 1 | `10.1016/j.jcp.2022.111762` | Multi-level adaptive particle refinement method with large refinement scale... | Y | green |  |
| 86 | INDEX | 1 | `10.1016/j.jfluidstructs.2021.103342` | A 3D Lagrangian meshfree projection-based solver for hydroelastic Fluid–Str... | Y | closed |  |
| 87 | INDEX | 1 | `10.1016/j.joes.2018.05.002` | Water entry and exit of axisymmetric bodies by CFD approach | Y | gold |  |
| 88 | INDEX | 1 | `10.1016/j.oceaneng.2011.09.008` | A set of canonical problems in sloshing. Part 0: Experimental setup and dat... | Y | closed |  |
| 89 | INDEX | 1 | `10.1016/j.oceaneng.2016.03.059` | Experimental drop test investigation into wetdeck slamming loads on a gener... | Y | green |  |
| 90 | INDEX | 1 | `10.1016/j.oceaneng.2019.03.006` | Sampling rate effect on wedge pressure record in water entry by experiment | Y | closed |  |
| 91 | INDEX | 1 | `10.1016/j.oceaneng.2020.107823` | Uncertainty analysis for measurement of added resistance in short regular w... | Y | closed |  |
| 92 | INDEX | 1 | `10.1016/j.piutam.2015.11.005` | A Self-organizing Adaptive-resolution Particle Method with Anisotropic Kernels | Y | hybrid |  |
| 93 | INDEX | 1 | `10.1016/j.sandf.2020.09.006` | Arbitrary particle domain interpolation method and application to problems ... | Y | gold |  |
| 94 | INDEX | 1 | `10.1016/s0045-7825(01)00377-2` | Hierarchical, adaptive, material point method for dynamic energy release ra... | Y | closed |  |
| 95 | INDEX | 1 | `10.1029/2020ms002277` | A Generalized Interpolation Material Point Method for Shallow Ice Shelves. ... | Y | gold |  |
| 96 | INDEX | 1 | `10.1061/(asce)ir.1943-4774.0000252` | Nonintrusive Method for Detecting Particle Movement Characteristics near Th... | Y | closed |  |
| 97 | INDEX | 1 | `10.1063/1.1638996` | Free energy simulations: Use of reverse cumulative averaging to determine t... | Y | closed |  |
| 98 | INDEX | 1 | `10.1063/1.4902608` | A steady-state convergence detection method for Monte Carlo simulation | Y | closed |  |
| 99 | INDEX | 1 | `10.1063/5.0178642` | Experimental study of viscous effects on long-duration sloshing characteris... | Y | closed |  |
| 100 | INDEX | 1 | `10.1063/5.0230381` | Numerical investigation of the damping rates of free oscillations in fluid ... | Y | closed |  |
| 101 | INDEX | 1 | `10.1063/5.0302483` | Efficient and flexible adaptive particle refinement for free-surface flows ... | Y | hybrid |  |
| 102 | INDEX | 1 | `10.1080/09377255.2023.2252232` | The resistance of a trans-critically accelerating ship in shallow water | Y | hybrid |  |
| 103 | INDEX | 1 | `10.1093/bioinformatics/btag044` | Bit-reproducible parallel phylogenetic tree inference | Y | gold |  |
| 104 | INDEX | 1 | `10.1103/physrev.182.280` | Statistical Error Due to Finite Time Averaging in Computer Experiments | Y | closed |  |
| 105 | INDEX | 1 | `10.1109/access.2022.3157904` | Framework for Vehicle Dynamics Model Validation | Y | gold |  |
| 106 | INDEX | 1 | `10.1109/correctness51934.2020.00011` | A Statistical Analysis of Error in MPI Reduction Operations | Y | closed |  |
| 107 | INDEX | 1 | `10.1109/ipdps.2010.5470481` | Improving numerical reproducibility and stability in large-scale numerical ... | Y | closed |  |
| 108 | INDEX | 1 | `10.1109/tvcg.2014.2307873` | Large-Scale Liquid Simulation on Adaptive Hexahedral Grids | Y | closed |  |
| 109 | INDEX | 1 | `10.1115/1.1767847` | Verification, validation, and predictive capability in computational engine... | Y | closed |  |
| 110 | INDEX | 1 | `10.1115/1.1906269` | Statistical Approach for Estimating Intervals of Certification or Biases of... | Y | closed |  |
| 111 | INDEX | 1 | `10.1115/detc2022-89632` | Modeling Large Deformable Terrain With Material Point Method for Off-Road M... | Y | closed |  |
| 112 | INDEX | 1 | `10.1115/imece2013-64652` | An Adaptive-Grid Projection Method for High Density Ratio Interfacial Flows | Y | closed |  |
| 113 | INDEX | 1 | `10.1115/omae2015-41850` | Behavior of the Residual Wave Components in a 3D Wave Basin After the Termi... | Y | green |  |
| 114 | INDEX | 1 | `10.1115/omae2019-96262` | Efficacy of Analysis Techniques in Assessing Broken Wave Loading on a Cylin... | Y | closed |  |
| 115 | INDEX | 1 | `10.1142/s0219876218500615` | Improved Incompressible Material Point Method Based on Particle Density Cor... | Y | closed |  |
| 116 | INDEX | 1 | `10.1145/3386569.3392460` | A practical octree liquid simulator with adaptive surface resolution | Y | closed |  |
| 117 | INDEX | 1 | `10.1145/3414685.3417794` | RBF liquids | Y | closed |  |
| 118 | INDEX | 1 | `10.1146/annurev-fluid-010816-060121` | Slamming: Recent Progress in the Evaluation of Impact Pressures | Y | closed |  |
| 119 | INDEX | 1 | `10.1146/annurev-fluid-011212-140753` | Water Entry of Projectiles | Y | closed |  |
| 120 | INDEX | 1 | `10.17077/etd.jgq7s29l` | Phase-averaged stereo-PIV flow field and force/moment/motion measurements f... | Y | closed |  |
| 121 | INDEX | 1 | `10.2312/localchapterevents/tpcg/tpcg09/069-076` | An Adaptive Sampling Approach to Incompressible Particle-Based Fluid | Y | ? |  |
| 122 | INDEX | 1 | `10.2514/6.2009-6148` | Unified Solver for Modeling and Simulation of Nonlinear Aeroelasticity and ... | Y | closed |  |
| 123 | INDEX | 1 | `10.2514/6.2010-1464` | Material Point Method Applied to Fluid-Structure Interaction (FSI)/Aeroelas... | Y | closed |  |
| 124 | INDEX | 1 | `10.3390/app11051983` | Statistical Validation Framework for Automotive Vehicle Simulations Using U... | Y | gold |  |
| 125 | INDEX | 1 | `10.3744/snak.2014.51.5.396` | Uncertainty Study of Added Resistance Experiment | Y | bronze |  |
| 126 | INDEX | 1 | `10.3970/cmes.2004.005.477` | The Generalized Interpolation Material Point Method | N | ? |  |
| 127 | INDEX | 1 | `10.3970/cmes.2005.008.135` | Multiscale Simulations Using Generalized Interpolation Material Point (GIMP... | N | ? |  |
| 128 | INDEX | 1 | `10.4208/cicp.080815.240316a` | A Probabilistic Automatic Steady State Detection Method for the Direct Simu... | Y | closed |  |
| 129 | INDEX | 1 | `10.48550/arxiv.2512.01010` | Chain of Unit-Physics: A Primitive-Centric Approach to Scientific Code Synt... | Y | ? |  |
| 130 | INDEX | 1 | `10.48550/arxiv.2605.00803` | Can Coding Agents Reproduce Findings in Computational Materials Science? | Y | ? |  |
| 131 | INDEX | 1 | `10.48550/arxiv.2605.09097` | An Overlapping Schwarz Space-Time Refinement Framework for Material Point M... | Y | ? |  |
| 132 | INDEX | 1 | `10.48550/arxiv.2605.13245` | It's not the Language Model, it's the Tool: Deterministic Mediation for Sci... | Y | ? |  |
| 133 | INDEX | 1 | `10.48550/arxiv.2605.17675` | Bridging the Gap on AI-Assisted Scientific Software Development Through Tra... | Y | ? |  |
| 134 | INDEX | 1 | `10.48550/arxiv.2605.28525` | Unified sparse framework for large-scale simulations using the material poi... | Y | ? |  |
| 135 | INDEX | 1 | `10.5614/j.eng.technol.sci.2021.53.2.1` | Toward Improvement of Resistance Testing Reliability | Y | gold |  |
| 136 | INDEX | 1 | `10.5957/attc-1992-008` | Run Length and Statistical Error Estimation for Seakeeping Tests and Trials | Y | closed |  |
| 137 | ABSENT | 1 | `10.1061/(asce)0733-9429(1987)113:3(370)` | Do Critical Stresses for Incipient Motion and Erosion Really Exist? | Y | closed |  |
| 138 | ABSENT | 1 | `10.1061/(asce)0733-9429(2002)128:4(369)` | Stochastic Incipient Motion Criterion for Spheres under Various Bed Packing... | Y | closed |  |
