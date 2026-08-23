# The Merged Research Reader Corpus, FINAL

**No date suffix. This is deliberately the last one in this lineage.**

**Built 2026-08-23 against `claude/add-ci-checks` at `badd5a2`.** It supersedes
`docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` (pass 1) and
`docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` (pass 2). Both remain on disk carrying a
SUPERSEDED banner. Nothing in either was deleted.

**It does NOT supersede `docs/CORPUS_MERGE_FINAL_2026-08-22.md`.** That file is a different
document answering a different question, and it is the more recent and more thorough of the
two lines. See section 1.

**Provenance key, applied to every claim.** `[READ]` I ran the command or read the page this
session. `[INFERRED]` computed from something tagged `[READ]`. `[RELAYED]` came from another
document or a tool summary and I did NOT re-derive it against a primary source.

**One source cited twice is not two sources.** Where two findings agree below, both origins
are named and the answer to "are they independent" is stated.

---

## 1. The lineage, measured rather than assumed

There are **two lines**, not one, and conflating them is what made the prior state look
contradictory.

| file | built | size | what question it answers | status |
|---|---|---|---|---|
| `MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | 2026-08-20 14:42 | 22,746 B | the whole-project reader | **SUPERSEDED** by pass 2 |
| `MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` | 2026-08-21 01:09 | 20,296 B | the whole-project reader, pass 2 | **SUPERSEDED** by this file |
| `CORPUS_MERGE_FINAL_2026-08-22.md` | 2026-08-22 02:48 | 65,030 B | the 138 catalogued-but-never-cited DOIs | **CURRENT AND AUTHORITATIVE on the 138** |
| `MERGED_RESEARCH_READER_CORPUS_FINAL.md` | 2026-08-23 | this file | terminal reader + what the 08-2x line missed | **CURRENT** |

`[READ]` all four `ls -la` results and all four file headers.

**Pass 2 was built by reading pass 1, not independently re-derived.** Its own opening states
"Supersedes `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md`" and its section 1 is titled
"THE DIFF: what pass 1 got wrong, what it missed, what survived", naming six specific pass-1
errors `[READ]`. **So the DOI accounting did not silently diverge between them**: pass 2 is an
extension with a named diff, which is the safe case, not the dangerous one.

### 1.1 The unpushed-branch hypothesis is REFUTED

The dispatch proposed that a corpus-lineage file written only on a local-only branch is why
prior checks did not reliably see it. **Measured, that is false for every file in this
lineage.** `[READ]`

Every commit touching `docs/MERGED_RESEARCH_READER_CORPUS*` and `docs/CORPUS_MERGE_FINAL*`
(`fc8d278`, `6b894bf`, `e9e80ad`, `7bc8c62`, `88672a0`, `6778913`) is contained in
`origin/claude/add-ci-checks`, confirmed by `git branch -a --contains` on each `[READ]`.

The three branches the dispatch named are all **pushed**: `[READ]`

- `claude/r9-gapscan` `5213f6f` pushed, **merged into HEAD**
- `claude/r9-reader` `9c19364` pushed, **merged into HEAD**
- `claude/r9-corpus-bib` `de18180` pushed, **NOT merged**, deliberately, per
  `CORPUS_MERGE_FINAL_2026-08-22.md` section 7, which diagnoses the conflict as substantive
  and reports it for a human instead of merging it. That is a decision, not an oversight.

**24 of 114 local branches have no `origin/` counterpart** `[READ]`, so unpushed branches are
a real and separate problem, listed in section 6. **They are simply not the cause here.**

---

## 2. What pass 2 (08-21) did not have, and this file adds

### 2.1 SIX Undermind deep searches existed upstream and reached no file in this repo

This is the single largest gap, and it is the same failure class CLAUDE.md already records
under "THE RESEARCH CORPUS IS NOW QUERYABLE FROM INSIDE THE REPO": work is commissioned, it
completes, and it never lands.

At session start `data/deep_searches/` held **21 search JSONs plus a MANIFEST** `[READ]`,
matching the 2026-08-20 pull. The live workspace held **26** `[READ]`. Five had been sitting
upstream since 2026-08-21 and 2026-08-22, and **none was mirrored, greppable, or reachable by
`--searches`, `--query` or `--source-audit`.**

| slug | name | created | papers |
|---|---|---|---|
| `grid-converged-force-deficit` | Grid-converged force deficit in partially submerged free-rigid MPM coupling | 2026-08-21 22:51 | 37 |
| `sink-drain-overfill` | Sink or drain boundary condition test overfills instead of draining | 2026-08-21 22:51 | 72 |
| `free-body-load-transfer` | Free Body Fluid Load Transfer Mechanisms | 2026-08-22 21:47 | 118 |
| `free-body-load-transfer-expanded` | Free Body Load Transfer Mechanisms Expanded | 2026-08-22 22:54 | 119 |
| `load-transfer-portability` | Load Transfer Portability and Contrast | 2026-08-22 23:04 | 114 |
| `verdict-invariant-grid-convergence` | Verdict invariant magnitude non monotone grid convergence MPM rigid body | 2026-08-22 23:54 | 77 |

The sixth was launched and completed **this session** `[READ]`. All six are now written to
`data/deep_searches/`, added to `MANIFEST.json`, and the index rebuilt: **27 deep searches,
332 papers unchanged** `[READ]`.

**A caveat that must travel with that count.** These six are **metadata only**. None carries a
`papers` array, so `--query`, `--doi` and `--method` still cannot match a single paper from
them. The metadata/papers split CLAUDE.md records is now **27 as metadata, 8 as papers**. Say
both numbers.

**A tooling defect found while landing them, worth knowing.** `research_index.py` resolves
searches as `idx.get("deep_searches") or load_deep_searches()`, so once the index carries a
non-empty list the **directory is never read**. Dropping a JSON into `data/deep_searches/` is
inert until `--build` runs. `[READ]` Verified: the five new slugs returned 0 grep hits through
`--searches` before the rebuild and 5 after.

### 2.2 The finding those searches contain, and its verification status

Two of the searches, run independently an hour apart with differently-worded goals, both
conclude that **this project's coupling scheme is not coupling**:

> "Assigning a mass-weighted grid velocity to a body merely imposes kinematics: it supplies
> neither a separately accumulated impulse nor a torque, so body momentum is replaced rather
> than transferred, and rotation becomes sampling-dependent. The literature explicitly rejects
> velocity equilibration for unresolved bodies, requiring a drag/load model instead [Hyd19];
> conservative impulse coupling is the corrective formulation [Akb18b]." `[READ]` of the search
> summary

That describes the material-8 free-rigid path CLAUDE.md item A-1 documents, exactly.

**IT IS TAGGED `[RELAYED]` AND MUST STAY THAT WAY UNTIL SOMEBODY READS THE PAPER.** `[READ]`
`10.1016/j.jcp.2019.03.049` (Hyde and Fedkiw 2019, "A unified approach to monolithic
solid-fluid coupling of sub-grid and more resolved solids", J. Comput. Phys. 390:490-526) is
**closed access**: scite returns `isOa: false`, `oaStatus: "closed"`, `contentDenied: true`,
purchase-only at USD 41.95, and Undermind reports no PDF. **I could not read it.** Two
deep-search summaries agreeing is **one instrument run twice**, not two sources, and both
ultimately point at the same unread paper.

**Do not write "the literature rejects velocity averaging" as an established fact.** Write
that two retrieval passes attribute that position to Hyde and Fedkiw 2019, and that the paper
has not been read.

### 2.3 One paper WAS read in full, and it cuts against adopting it

`10.1016/j.jcp.2017.06.047`, Nangia et al. 2017, "A moving control volume approach to
computing hydrodynamic forces and torques on immersed bodies", J. Comput. Phys. **Read in full
this session** `[READ]`. The deep searches rank it as a route to force and torque without
noisy surface derivatives. Reading it establishes two limits that the summaries do not:

- **It still requires a pressure field.** Its Eq. (16) and Eq. (19) both carry the `-p I` term
  over the control-volume surface. The authors note Noca proposed pressure-free expressions
  and say verbatim: "We do not analyze such expressions in this work, however." (Section 1,
  page 2) `[READ]` **So it is not directly portable to a pressureless warpmpm.**
- **It has no free-surface, floating or partially-submerged case at all.** "We consider only
  neutrally buoyant bodies to simplify the implementation" (Section 2.1, page 3) `[READ]`.
  Its free-body cases are a free-swimming eel and two sedimenting cylinders, both fully
  immersed.

**Consequence: Nan17 cannot bear on this project's partial-submersion deficit**, which is the
regime the deficit lives in. It is a contrast citation, not a fix. This is a genuine negative
and it prevents a wrong adoption.

### 2.4 Phase-2 filesystem sweep: nothing new of research value

Bounded `find -maxdepth 3 -newer` against the 08-21 file `[READ]`:

- `~/Desktop`: exactly two hits, `SNAPSHOT_CONSOLIDATION_DRYRUN.md` (2026-08-22 13:10, 66,276 B)
  and `WORKING_TREE_AND_DOWNLOADS_SCAN.md` (2026-08-22 14:20, 12,620 B). **Both are
  read-only housekeeping audits** of snapshot redundancy and working-tree status. Neither is
  research corpus material and neither is folded in beyond this line.
- `~/Documents`: **zero hits.**
- No file matching a `SENSITIVE_DO_NOT_SHIP` pattern appeared in either sweep `[READ]`.

**The D10 cross-slope premise is wrong and the correction matters.** The dispatch describes
`~/Documents/CANITFORD_D10_CROSSSLOPE_2026-08-14/` as "previously found but never analyzed".
It **has** been analyzed, in full, as **register item D22** `[READ]`, which verifies all eight
SHA256 checksums, reads the 28-field meta blocks, and reaches a finding with teeth: the
directory name is wrong, `g_vec[1]` (the lateral component) is **exactly 0.0 in all eight
runs**, so **no cross-slope was ever applied** and the set is a longitudinal grade study at
S = 0, 0.02, 0.06. D22 states its own falsifier. It is absent from all three corpus-lineage
files, which is why a corpus-only search reports it as unanalyzed. **It is register material,
correctly filed, and this file does not restate it.**

---

## 3. The coupling-defect DOI question, resolved

The dispatch asked which DOI has 4-report support alongside `10.1016/j.jcp.2016.10.064`, naming
two candidates that disagree. **The answer is `10.1016/j.cma.2022.114809`, and it is not close.**

Re-parsed live from the source catalogue,
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv`,
field 6 `in_reports` being a `+`-joined list of report names `[READ]`:

| DOI | `in_reports` (TSV) | index `n_reports` | rank |
|---|---:|---:|---|
| `10.1016/j.jcp.2016.10.064` | **4** | **5** | joint top |
| `10.1016/j.cma.2022.114809` | **4** | **5** | joint top |
| `10.1007/s00466-019-01783-3` | 2 | 3 | strictly below both |

**Exactly two of the 138 reach the maximum, and they share an identical report set** `[READ]`.
`10.1007/s00466-019-01783-3` is not one of them.

**THE COUNT IS INSTRUMENT-DEPENDENT AND THE RANKING IS NOT.** The TSV says 4, the built index
says 5. The extra report in the index is `mpm-verification` `[READ]`. Two instruments, one
human-curated catalogue from 2026-08-14 and one index built from eight report markdown files,
**agree on the ordering and disagree on the absolute number.** Quote the ranking freely; never
quote "4 reports" or "5 reports" without naming which instrument produced it. This is the same
scope-sensitivity trap CLAUDE.md item 13 records for DRIFT_THRESHOLD.

**"4 reports" IS NOT "4 INDEPENDENT SOURCES", and the dispatch's phrasing smuggles that in.**
The four are four Undermind deep searches over the same literature corpus by the same
retrieval system, run against differently-worded goals. Under this project's own rule, that is
**one instrument returning the same paper four times**. It is a strong relevance signal and it
is not corroboration.

### 3.1 The "same paper under a different DOI" hazard: checked, and it is a different, worse problem

`10.1016/j.cma.2022.114809` is **not** the Qian paper. `[READ]`

- `10.1016/j.cma.2022.114809` = Ming-Jian Li, Yanping Lian, Xiong Zhang, "An immersed finite
  element material point (IFEMP) method for free surface fluid-structure interaction
  problems", CMAME 393:114809, 2022-04-01, 33 citations. Title verified against the registry,
  verdict `matched`, high confidence.
- `10.1016/j.cma.2022.114965`, attributed in this repo's own history to "Qian et al. 2022,
  water entry of a half-buoyant cylinder", **resolves to an unrelated phase-field
  crack-propagation paper** and was flagged as fabricated on 2026-08-14 in
  `docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md` `[READ]`.

**Confirmed clean today:** `10.1016/j.cma.2022.114965` appears **nowhere** in `paper/`, and
there is **no standalone Qian bib entry** `[READ]`. Earlier "qian" grep hits are the substring
inside **Xia Junqiang**. The fabricated DOI never reached the bibliography.

### 3.2 Register G25 already triaged this, and reaches the same ranking by a different predicate

Register **G25** triages the nine multi-report papers by **reading what each paper says**,
independently of any report count. It rates `10.1016/j.cma.2022.114809` item (b), **"YES"**,
because it "couples iMPM fluid to an FEM solid through a *sharp* immersed interface and
separately eliminates 'numerical cavities'" `[READ]`.

`CORPUS_MERGE_FINAL_2026-08-22.md` section 4 item 6 **already names it**: "`10.1016/j.cma.2022.114809`
(IFEMP, 4 reports, the joint top-ranked gap)" `[READ]`. **So the repo's own most recent
document had already answered this**, and my independent TSV re-parse reproduces it. Those two
are genuinely separate origins (a live catalogue re-parse against a written record), so this
one is corroborated.

**G25 names (a) `10.1016/j.jcp.2016.10.064` and (h) `10.1007/s00466-019-01783-3` as "the two
candidates worth acting on", and the 08-22 session read exactly those two.** That was correct
under G25's content predicate. Under the report-count predicate it left the joint-top-ranked
paper unread. **Both readings are defensible; neither is wrong; the predicate has to be
stated.**

### 3.3 Why it is still unread, measured

`10.1016/j.cma.2022.114809` is **closed access and unobtainable by any route available here**:
Undermind reports no PDF and `read_pdfs` returns "Could not get PDF"; scite returns
`isOa: false`, `oaStatus: "closed"`, `contentDenied: true`, purchase-only at USD 41.95 `[READ]`.
**It needs institutional access, not a better script.** This independently reproduces
`CORPUS_MERGE_FINAL` section 4 item 3, which found 74 of 138 closed by Unpaywall.

---

## 4. Carried forward, unresolved

Nothing below is closed. Each is carried rather than dropped.

1. **`10.1016/j.cma.2022.114809` remains UNREAD.** Joint top-ranked gap, closed access. The
   highest-value single acquisition in the project.
2. **`10.1016/j.jcp.2019.03.049` (Hyd19) remains UNREAD and closed.** The claim that the
   literature rejects velocity equilibration rests entirely on it and is `[RELAYED]`.
3. **The two competing coupling-defect mechanisms remain undiscriminated.** G25 states this
   plainly: (a) says the deficit lives in the free-surface pressure boundary condition of a
   weakly compressible formulation, (h) says it lives in material-point stress recovery. Both
   predict a grid-converged deficit, so grid-convergence alone cannot separate them. G25 names
   the distinguishing test. **Neither is established.**
4. **The report-count instrument disagreement**, section 3, is unresolved: TSV 4, index 5. Both
   are defensible; the ordering is invariant.
5. **The six new deep searches are metadata only.** 27 as metadata, 8 as papers.
6. **`claude/r9-corpus-bib` is still unmerged**, deliberately, with a substantive conflict
   documented in `CORPUS_MERGE_FINAL_2026-08-22.md` section 7. It needs a human.
7. **Poster and paper submission status is OPEN**, per
   `docs/CLAUDE_MD_OPEN_ITEMS_STATUS_2026-08-22.md` item 7, "nothing confirms either
   submission" `[READ]`. **No `.tex` file was touched this session** on that basis.
8. **Unreviewed.** No claim in this file was checked by the physics-skeptic path.
9. **A hypothesis of mine that was REFUTED, recorded so it is not re-raised.** Reader-facing
   citation count moved from CLAUDE.md's 43 to **107** after the rebuild. I hypothesised the
   jump was `CORPUS_MERGE_FINAL_2026-08-22.md`'s 138-DOI appendix inflating the metric, the
   same class as the `Dynamic_Vehicle_Traction_in_Floodwater.md` dump inflating it by 9.
   **Measured: 0 of the 107 are reader-facing only via that file** `[READ]`. Every one appears
   in at least one other reader-facing document. The growth is real, from absorbed r9/r10
   merges. **The inflation hypothesis is dead; do not resurrect it.**

---

## 5. What this session changed, so it is auditable

- `data/deep_searches/` +6 JSONs, `MANIFEST.json` 21 -> 27 with a `pull_history` field.
- `data/research_corpus_index.json` rebuilt. **332 papers before and after**, deep searches
  21 -> 27. A pre-build backup was taken and all 8 `REPORTS` source paths were confirmed
  present first, because `--build` silently writes a smaller index and exits 0 when they are
  not, per that function's own docstring `[READ]`.
- SUPERSEDED banners on the two dated corpus files.
- Source-of-truth ranking updated in `CLAUDE.md` and the corrections register.
- **The shipped bibliography was audited for fabrication and retraction**, closing
  `CORPUS_MERGE_FINAL_2026-08-22.md` section 4 item 11. Result: **9 of 9 DOI-bearing entries
  `matched` at high confidence, 0 mismatch, 0 ambiguous, 0 not_found, 0 retracted, 0
  corrections, 0 expressions of concern** `[READ]`. **Scope caveat: 6 of the 15 entries carry
  no DOI in any field** (`thorpe2026pvwm`, `hsiao2025nerfmpm`, `shand2011arr`, `nws_tadd`,
  `genesis2024`, `fred2026`) and therefore could not be audited by identifier. The audit
  covers 9 of 15, not 15 of 15.

---

## 6. The unpushed-branch inventory, since it was asked for and is real

**24 of 114 local branches have no `origin/` counterpart** `[READ]`. Not the cause of the
corpus-lineage confusion, but a live risk to attribution. One is named
`claude/credential-exposure-2026-08-13-DO-NOT-PUSH` and **must stay unpushed**: the repo is
public. See section 4 item 6 for the one unmerged branch that matters to this document.
