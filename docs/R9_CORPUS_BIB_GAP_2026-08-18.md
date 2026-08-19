# The corpus is not a superset of the bibliography: the builder cannot reach the
# layer that holds the missing works, and the gap is one paper wide rather than
# eleven

> **THIS TITLE WAS CORRECTED 2026-08-19 AND THE ORIGINAL IS RETRACTED.** It read
> "it is a **sourcing gap**, not a dropped merge". It is an **ingestion** gap:
> `shah2018` is in three deep searches, one of them 25 days OLDER than the index
> build, and it is absent from the corpus only because the builder cannot see
> that search. The "not a dropped merge" half stands (`DROPPED_IN_MERGE` is 0)
> and the "one paper wide" half stands. **Section 22 has the full retraction,
> including how the wrong inference was made and why it matters.** Read it
> before quoting section 1.

Slot `d14-corpusbib`, branch `claude/r9-corpus-bib`, worktree
`.claude/worktrees/r9-corpus-bib`. Written 2026-08-18, 23:39 to 00:0x BST.

Every number below was produced by `analysis/research_index.py --bib-audit`
during that window and regenerates from the two commands in section 9. Claims are
tagged READ (read live from a file or a resolved external record this session),
DERIVED (computed here from files read this session), or RECALLED (carried from
another session's write-up and not independently re-derived).

`CLAUDE.md`, section "AUGUST 15 2026, THE RESEARCH CORPUS IS NOW QUERYABLE FROM
INSIDE THE REPO", records this as open and assigned to nobody: "the corpus is NOT
a superset of the bibliography ... Whether that is a sourcing gap or a dropped
merge is unresolved and belongs to whoever owns the index build." This document
resolves it.

---

## 1. The answer, in four lines

**It is not a dropped merge.** DERIVED: `DROPPED_IN_MERGE` is 0, and the DOIs and
titles of the 11 absent works appear nowhere in the **raw text** of any of the
eight source reports. That measurement stands.

~~They were never returned by any search.~~ **WITHDRAWN 2026-08-19, see section
22.** Eight reports cannot testify about twenty searches. `shah2018` was returned
by a search dated 2026-07-21, twenty-five days before the index was built, and by
two more since. The gap is an **ingestion** gap: the builder cannot reach the
layer holding the work. Nobody needs to go and find this paper.

**The gap is far narrower than eleven.** DERIVED: of the 11 cited works absent
from the corpus, exactly **one** is peer-reviewed flood-vehicle literature inside
the corpus's topical scope. That one is `shah2018`. The other ten are absent for
reasons of category, not sourcing. Section 4.

**The reason nobody could check the eleven was an unrecorded matching step**, and
that step is the more reusable finding. Section 2.

**A separate defect turned up on the way, and it is the most actionable thing
here:** three papers ARE in the index with an empty DOI and a mangled title
because of a parse bug, and one of them is Dancey et al 2002, which this project
relies on for a live claim. Because cited-status is gated on `bool(doi)`, those
three can never be marked cited however often the repo cites them. Section 7.

### 1a. A claim of mine that did not survive my own check

An earlier draft of this section read "across 57 bib entries audited on two
different refs, zero works appear in a source report and fail to appear in the
index. Nothing was ingested and lost." **That was overstated and is withdrawn in
that form.**

The index is BUILT from the same eight reports, so "present in a report, absent
from the index" is close to unreachable by construction, and a zero result there
is nearly circular. I measured the check's power rather than assuming it:
DERIVED, 275 distinct DOI-shaped strings appear in the raw report text and 269 of
them are already in the index. A test that the subject passes 269 times out of
275 by construction is weak evidence, whatever it returns.

What survives, and is not circular, is the **raw-text** result stated above:
absence from the reports themselves is upstream of the index build. That is the
sentence to quote.

And the check turned out to have more power than the 269/275 suggests, because
the remaining 6 are not noise: 3 are URL-encoding artefacts of my own extraction,
and **3 are a genuine drop**, which is section 7.

---

## 2. The finding that decides the answer: the DOIs are in the wrong field

READ, from `overleaf/main:can_it_ford_references_IEEE.bib` at `6466dfa`, 144
lines: the shipped bibliography has **exactly one `doi =` field**, on `xiong2024`
at line 99. Nine further entries carry a DOI, all of them inside a
`note = {doi: 10.xxxx/yyyy}` field. Five carry no DOI anywhere.

READ, from `analysis/research_index.py` in the `repo_cited_dois` and `build`
paths: the index computes cited-status purely by DOI string membership, and
records with an empty `doi` are excluded by construction.

So a census that joins the bibliography to the corpus on the bib's `doi` field
sees **one identifier out of fifteen** and treats the other fourteen works as
identifier-free. The previously published "11 of 14 absent" therefore could not
have come from a DOI join, and no record survives of what it did come from. That
missing step is what decided the number, and its absence is why the eleven could
not be checked by anyone who was not there.

This is the mirror of the defect `d6-tooling` recorded in
`docs/R8_TOOLING_PROVENANCE.md` on `claude/r8-tooling` (READ this session): a
checker whose corpus **includes** its own output, so every item self-certifies.
The risk here runs the other way, a checker whose corpus **excludes** the
bibliography it is meant to audit, so every item reads as a gap. Both emit a
confident integer that measures the checker's own scope rather than the world.
The fix in section 8 is built to fail in neither direction, by recording the
route on every row instead of only the outcome.

---

## 3. What the census actually found

Scope, stated with the numbers because it decides them: `bib_ref =
overleaf/main:can_it_ford_references_IEEE.bib`, `tex_ref =
overleaf/main:conference_101719_1.tex`, index built 2026-08-15 holding 332
papers of which 60 carry no DOI and are unmatchable by the DOI route, all 8
source reports read at audit time, `.claude/worktrees/` excluded.

| verdict | entries | of which cited |
|---|---|---|
| `IN_CORPUS` | 4 | 3 |
| `DROPPED_IN_MERGE` | **0** | **0** |
| `UNCERTAIN_RELATED_WORK` | 1 | 1 |
| `NEVER_INGESTED` | 10 | 10 |

DERIVED. The 4 / 3 rungs reproduce the published ladder exactly, independently
and by a stated method: `smithmodrafelder2019`, `xia2014` and `azhar2023` are
cited and in the corpus, `xiong2024` is in the corpus and in the bib but never
`\cite`d so BibTeX drops it.

11 cited works are absent, which reproduces the published figure. **The integer
is the least interesting part of the result**, and section 4 is why.

---

## 4. The eleven are not eleven of the same thing

DERIVED, from the `source_kind` column of the census. Splitting the 11
absent-and-cited works by what KIND of source they are:

| kind | n | works |
|---|---|---|
| peer-reviewed | 3 | `kerbl20233dgs`, `xie2023physgaussian`, **`shah2018`** |
| preprint | 3 | `thorpe2026pvwm`, `hsiao2025nerfmpm`, `fred2026` |
| techreport or standard | 2 | `shand2011arr`, `heydinger1999sae` |
| model or dataset | 1 | `ccsa2016yaris` |
| software | 1 | `genesis2024` |
| webpage | 1 | `nws_tadd` |

An Undermind deep search returns published literature. It does not return a
GitHub repository (`genesis2024`), a National Weather Service safety campaign
page (`nws_tadd`), a George Mason crash-test finite-element model
(`ccsa2016yaris`), or a 1999 SAE technical report (`heydinger1999sae`). Their
absence is a **category boundary, not a sourcing defect**, and counting them
alongside a missed journal paper is what inflates the gap to eleven.

Of the 3 peer-reviewed absences, two are computer graphics: Kerbl et al's 3D
Gaussian Splatting and Xie et al's PhysGaussian. Eight deep searches scoped to
MPM, free-surface flow, flood-vehicle stability and simulation provenance would
not be expected to return SIGGRAPH and CVPR rendering papers, and did not. The
three preprints include two of the group's own arXiv postings.

**That leaves exactly one.**

---

## 5. `shah2018` is the one in-scope absence, and it is not a random miss

> **HEADING CORRECTED 2026-08-19.** This read "is a real **sourcing** gap".
> It is an **ingestion** gap: section 22. Everything else in this section,
> including the citation-neighbourhood evidence below, stands and in fact
> reads better under the corrected framing.

READ, verified this session against the resolved Crossref record via
`scholar-sidekick verifyCitation`, verdict `matched`, confidence `high`:
`10.1051/matecconf/201820307003` is "Instability Criteria for Vehicles in Motion
Exposed to Flood Risks", MATEC Web of Conferences vol 203 p 07003, 2018, first
author **Syed Muzzamil Hussain Shah**. The bibliography entry is correct in every
field checked, including the given names. This matters because a name-variant
trap is already on record for this author, and the bib is on the right side of it.

READ, from the eight source reports: the DOI `10.1051/matecconf/201820307003`
appears in **none** of them. DERIVED: its title scores 0.17 against its nearest
corpus neighbour, far below the 0.75 same-work threshold.

DERIVED, and this is what makes it a gap rather than an accident: **7 corpus
records carry the surname Shah, and 6 of them are from that same Malaysian
flood-vehicle group.** Five have Syed Hamid Hussain Shah as first author, "Hazard
risks pertaining to partially submerged non-stationary vehicle" (2019),
"Criterion of vehicle instability in floodwaters: past, present and future"
(2019), "A review of safety guidelines for vehicles in floodwaters" (2019),
"Hydrodynamic effect on non-stationary vehicles at varying Froude numbers"
(2020), and "Froude number variance with respect to the hydrodynamic response of
a non-static vehicle" (2021). The sixth is Al-Qadami et al 2021 with him as a
co-author. The searches reached that name and that subject repeatedly, across
four years and five journals, and returned other work, not this one.

The seventh record is **a different person**: S. Shah, Hopfgartner and Bleier
2026, "Automating Computational Reproducibility in Social Science". It is the
sole reason 2026 appears in the census's year list for this row, and it supports
nothing above.

Caveat, stated because the evidence does not support more: the corpus renders the
author as "Syed **Hamid** Hussain Shah" while Crossref renders the 2018 paper as
"Syed **Muzzamil** Hussain Shah". Surname substring matching is what the census
uses, and it is **not** an author-identity claim. Whether those strings denote
one person is not resolved here.

Bonus corroboration, READ from the Crossref record's own reference list:
`shah2018` cites at R11 "Shand T.D., Cox R.J., Blacka M.J., and Smith G.P. (2011)
Appropriate safety criteria for vehicles. Australian Rainfall and Runoff,
P10/S2/020. ISBN:978-0-85825-948-5", which is the `shand2011arr` entry of this
bibliography with a matching report number and ISBN. It also cites at R18 Bonham
and Hattersley (1967) "Low level causeways", which **is** in the corpus as
`moving-rigid-body#15`. So `shah2018` sits directly in this corpus's citation
neighbourhood, which strengthens rather than weakens the claim that missing it
matters. CORRECTED 2026-08-19: this sentence ended "a genuine sourcing gap" and
that is withdrawn per section 22. Note how much better the evidence fits the
corrected reading: a paper whose own reference list overlaps this corpus is
exactly what you expect the project's searches to have RETURNED, and they did,
on 2026-07-21.

---

## 5a. An offered corroboration that is REFUTED, and the false zero behind it

**RETRACTED AT SOURCE, 2026-08-19.** The coordinating session that offered the
claim below has since withdrawn it independently, before reading this section,
and its retraction reproduces this refutation from separate evidence: it read the
`doi` and `authors` fields of the index directly rather than running the query
tool, and got the same 4-of-6 present and the same 5 Al-Qadami records. So the
claim is retracted by both its author and its auditor, by two different methods.
It is kept here in full rather than deleted, because the *reason* it was wrong is
the reusable part and a deleted error teaches nobody.

Two corrections to that retraction, both minor and both verified live here. It
cites the defect at `analysis/research_index.py:518-521`; on this branch that
code was already fixed in commit `8bad9b4` and the clause now sits near `:1067`,
so the line reference points at an unfixed ref (`origin/main` or similar), not at
this branch. And it adds a fact I had not established, which is a real widening
of the defect and is carried into section 5b: **110 of the 332 records have no
abstract at all**, so for a third of the corpus `--query` was title-only
substring matching even for topic queries, not just author queries.

Added 2026-08-19. A coordinating session offered this as corroboration: six
flood-vehicle DOIs were resolved against Crossref, `research_index.py --query
"Al-Qadami"` returned zero matches, and therefore "not one of them is in the 332",
making the gap cover "the literature the project most needs". I was asked to
verify it rather than take it on trust. **It does not survive.**

DERIVED, checking the six DOIs directly against the index instead of through
`--query`: **4 of the 6 are in the corpus.**

| DOI | in the 332? |
|---|---|
| `10.1007/s11069-021-04949-6` | **yes**, Al-Qadami et al 2021 |
| `10.1111/jfr3.12828` | **yes**, Al-Qadami et al 2022 |
| `10.3390/su151713262` | **yes**, 2023 |
| `10.1111/jfr3.12657` | **yes**, Shah et al 2020 |
| `10.1051/matecconf/201820307003` | no, this is `shah2018` |
| `10.1016/j.trd.2017.06.020` | no |

READ, the mechanism, from `analysis/research_index.py` at the `--query` clause
before I changed it:

```python
sel = [r for r in sel
       if q in r["title"].lower() or q in r["abstract"].lower()]
```

**The `authors` field is never read.** So an author-name query returns zero
whatever the corpus contains. It is not a weak search, it is a search that cannot
succeed. DERIVED: `--query "Al-Qadami"` returned `0 match` while **5** records
carry Al-Qadami in `authors`. `10.1111/jfr3.12828` is among them, and it is the
paper `CLAUDE.md` names as claiming the first moving full-scale vehicle
simulation, with critical depth 0.38 m and minimum D x V 0.39 m^2/s. The corpus
is not silent on the project's closest prior art. It holds it, and marks it
`IN-PAPER`.

This is the exact failure the same dispatch warned me about in the same message,
a search that errors or cannot match returning 0, and a false zero being
indistinguishable from a true one. It reached a conclusion opposite to the truth
in a single step.

**Fixed**, since `analysis/research_index.py` is in my scope: `--query` now
searches `authors` as well, and `--query "Al-Qadami"` returns 5. The comment at
that line records the measured before-and-after so the fix cannot be silently
reverted as a tidy-up.

**What survives, and it strengthens section 5 rather than weakening it.** The
corpus holds 5 Al-Qadami papers and 6 papers from the Shah/Mustaffa group, all
of them in-scope flood-vehicle work, and still does not hold `shah2018`. The
searches did not miss this neighbourhood. They worked it repeatedly and returned
eleven of its papers. That makes a single in-scope absence a sharper finding than
a claim of blanket silence would have been, because blanket silence would have
been explained by scope and this cannot be.

---

## 5b. Turning the same test on my own census, which is where it bit

The retraction came with an instruction worth more than the retraction: *before
any absence number goes in the census, establish whether it was measured with a
predicate that could have returned a hit, and apply that to your own numbers as
much as to the ones you are auditing.* Applied here, it found a hole in my own
tool within one command.

**My author route silently skipped two entries.** The route guards with
`len(surname) > 3`. DERIVED: that excluded `xie2023physgaussian` (surname "Xie")
and `xia2014` (surname "Xia"). `xia2014` is harmless, it matched by DOI. But
`xie2023physgaussian` was published in section 4 as `NEVER_INGESTED` **while one
of its three index routes had never run**, and the census cell said "0 matches"
rather than "did not run". That is the same shape as the `--query` defect: a
predicate that cannot fire, reported as a measurement.

**The guard itself is correct and I kept it.** DERIVED: searching "Xia" as a
substring of the authors field returns **23** records, and nearly all are hits
inside *given* names, "Lingxiao", "Xiao-Guang", "Xiaomin", "Xiaoguang". A
three-character surname substring is overwhelmingly false-positive. The bug was
never the guard. The bug was that the skip was **silent**.

**Did it change the answer? No, and I checked rather than assumed.** DERIVED:
the corpus contains **0** records with "Xie" in the authors field, so the route
would have returned nothing had it run. `xie2023physgaussian` stays
`NEVER_INGESTED`. The verdict survives, but it survived by luck until this check,
and that distinction is the whole point.

**The fix, and it is the one this project keeps re-learning.** Evaluability is now
recorded separately from result. A route that cannot run reports
`NOT-EVALUABLE(reason)`, never `0`. Two new census columns, `routes_evaluable`
and `n_routes_evaluable`, say which of the five routes *could* have fired for
each work, and `--bib-audit` prints the breakdown for every absence.

| absent work | routes that could fire |
|---|---|
| `thorpe2026pvwm`, `hsiao2025nerfmpm`, `nws_tadd`, `genesis2024`, `fred2026` | 3 of 5 (no DOI in the bib, so both DOI routes are lost) |
| `xie2023physgaussian` | 4 of 5 (author route not evaluable, short surname) |
| `kerbl20233dgs`, **`shah2018`**, `ccsa2016yaris`, `heydinger1999sae` | **5 of 5** |

**No absence in this census rests on fewer than three independent routes, and
`shah2018`, the one load-bearing absence, rests on all five.** That is now a
printed property of the tool rather than a claim in prose.

Note what the 3-of-5 rows are: every one of them is a preprint, a web page or a
software repository, that is, exactly the category-boundary group from section 4
whose absence is already explained without needing a search at all. The works
where the absence claim has to carry weight are the ones where it is strongest.

### The general rule this project keeps paying for

Three independent instances tonight, in three different tools:

1. `--query` matched `title` and `abstract` only, so an author query returned a
   structurally guaranteed zero.
2. My author route skipped short surnames and reported the skip as zero.
3. A `grep` of mine failed on an unquoted zsh glob mid-session; the shell errored
   and the pipeline would have read as zero had I not seen the error text.

All three are the same failure: **a cell that cannot distinguish "no" from "could
not ask".** The remedy is not more care, it is a schema in which the two cannot
share a value, which is what `routes_evaluable` and `NOT-EVALUABLE(reason)` are.

---

## 5c. The gap is a LADDER OF CONTAINERS, and the deep-search rung is the big one

Added 2026-08-19, after a coordinating session reported that the index is missing
the project's own Undermind deep searches. **The substance is right and it is a
bigger finding than the bibliography gap I was sent for. Three of its specifics
are wrong, and the way they are wrong is the same false-absence pattern this
document is about, so they are corrected rather than quietly fixed.**

### What the check got wrong, and why

It reported "eight of eight absent", having checked the deep-search names against
the index's `documents` list. **`documents` is the wrong container.** DERIVED,
from the index: `documents` holds 44 entries and by type they are 35
`claude-artifact`, 5 `perplexity-report`, 2 `bibliography` and 2
`elicit-extract`. **Zero deep searches, by construction.** Deep searches live in
a different key, `source_reports`.

Checked against `source_reports`, **three of those eight are INGESTED**:

| reported ABSENT | actually |
|---|---|
| Moving Rigid Body Free Surface Validation | **ingested** as `moving-rigid-body` |
| Quantitative MPM Wall Penetration | **ingested** as `wall-penetration` |
| Multi-resolution MPM for Large-domain Flooding | **ingested** as `multi-resolution` |

Searching a container that cannot hold the thing you are looking for, and
reporting the empty result as absence, is the same defect as `--query` never
reading `authors` (section 5a) and my own author route reporting a skip as zero
(section 5b). That is the **fourth** instance tonight, and the first one where I
was the recipient rather than the author.

The workspace also holds **20** completed deep searches, not 19. READ, live from
`inspect_deep_searches` on workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`.

### The ladder, which is what was asked for

Five containers, five different questions. Never merge them into one number.

| rung | container | ingested | not |
|---|---|---|---|
| 1 | **Undermind deep searches** in the workspace | **8 of 20** | **12** |
| 2 | `documents` (artifacts, Perplexity, Elicit, bib) | 44 indexed | holds no deep searches at all |
| 3 | `papers` merged from rung 1 | 332 distinct, from 426 raw rows | anything in the 12 un-ingested searches |
| 4 | shipped bibliography, `overleaf/main` | 4 of 15 in the corpus | 11 |
| 5 | reference list, what prints | 3 | 12 |

**Rung 1 splits in two, and the split changes who owns the fix.** DERIVED, by
comparing each search's creation date against the index build date of 2026-08-15:

- **6 searches PREDATE the build and were never ingested.** This is the genuine
  ingestion gap: `Simulation Ready Vehicle Mesh Assets` (Jul 21, 36 relevant
  papers), `Dynamic Vehicle Traction in Floodwater` (Jul 21, 43), `Small Data
  Physics Surrogates at 36 Conditions` (Jul 15, 47), `Physics Simulation
  Validation Protocol` (Jul 15, 81), `Quantitative Flood Traversability
  Connections` (Jul 15, 82), `Optical Vehicle Collision Geometry` (Jul 15, 23).
  **312 relevant-paper slots.**
- **6 searches POSTDATE the build**, all Aug 18 and Aug 19, totalling **380
  slots**, the largest being `moving vehicle floodwater simulation open source
  implementations` (Aug 19, 105) and `how computational researchers audit and
  defend simulation credibility` (Aug 18, 92). These are **not an ingestion
  defect at all**, they are staleness: the index cannot contain research that did
  not exist when it was built.

Merging those two would repeat exactly the error this document opens with.

**Do not read 692 as "692 missing papers."** Those are per-search relevant-paper
slots with unknown overlap between searches and with the existing 332. The only
calibration available is the ingested layer itself, where 426 raw rows merged to
332 distinct, a 22 percent reduction. And the builder details only each report's
top 50, so even full ingestion would not create a record per slot. The honest
statement is that the un-ingested layer is **comparable in size to the entire
current corpus**, and that its exact unique contribution is unmeasured.

### The structural defect, which is the real finding

READ, from `analysis/research_index.py`: `REPORTS` is a **hardcoded
module-level list of eight local file paths**, iterated at `:372` inside
`build()`. There is no directory scan, no glob, and no API call anywhere in the
builder.

**So `--build` cannot ingest a nineteenth or twentieth deep search, and it never
could.** It cannot discover one, and it cannot reach the workspace. Adding a
search requires two manual steps that nothing in the repo automates or checks:
export the search to markdown in the catalogue-table format `parse_report`
expects, and edit the `REPORTS` literal. **The count is the symptom; the fixed
eight-entry list is the defect.** No mechanism exists that would ever notice a
new search, so this gap grows silently by construction every time anyone runs a
deep search.

### It has already cost real work, and it reaches into my own census

The coordinating session re-derived the vehicle-mesh provenance problem by hand,
when `Simulation Ready Vehicle Mesh Assets` had answered it on 21 July. READ,
live from that search: it covers the CCSA/NCAC LS-DYNA models, records the MASH
designations (`Extended Validation of the Finite Element Model for the 2010
Toyota Yaris Passenger Sedan (MASH 1100kg Vehicle)`, and the 2007 Silverado as
MASH 2270kg), and carries the explicit negative finding that **no citable,
publicly redistributable OBJ/PLY/glTF/USD conversion of the Yaris, Silverado or
Rogue models is verified**. DERIVED: `--query` returns **0** for `Silverado`,
`Camry` and `Toyota Yaris`.

That 1100 kg Yaris is this project's canonical vehicle and canonical mass.

**SELF-CORRECTION TO SECTION 4.** I classified `ccsa2016yaris` as absent for a
category reason, on the argument that "an Undermind deep search returns published
literature, it does not return a George Mason crash-test finite-element model."
**That argument is too strong and I withdraw it for this row.** A deep search DID
return exactly that class of work, in depth, including the validation reports for
this very model. The model's own DOI may still be absent, but the literature
about it exists and was commissioned by this project. The correct statement for
`ccsa2016yaris` is not "outside what a literature search returns", it is
**"covered by a deep search that was never ingested"**, which moves it from the
category-boundary group to the ingestion-gap group.

That does not change the headline. `shah2018` remains the one in-scope absence
from the corpus **as built**. But the count of works whose absence is explained by
category drops from ten to nine, and `ccsa2016yaris` joins the rung-1 gap.

---

## 6. `shand2011arr` is uncertain to the tool, and a human read resolves it

The census returns `UNCERTAIN_RELATED_WORK` for `shand2011arr` and refuses to
force it into present or absent. DERIVED: one corpus record shares the first
author surname and the year 2011, "Development of Appropriate Criteria for the
Safety and Stability of Persons and Vehicles in Floods", T. Shand, Gp Smith,
R. Cox and M. Blacka, Semantic Scholar `a2948cce`, no DOI. Its title scores 0.27
against the bib entry, below the related-work threshold, so **the title route
alone would have wrongly reported it as never ingested.** The author-plus-year
route is what caught it.

Resolved by human read, not by the tool, and recorded as such: they are
**different documents**. The bib entry is the Australian Rainfall and Runoff
Project 10 Stage 2 **vehicles** literature review, report P10/S2/020, ISBN
978-0-85825-948-5. The corpus record is a 2011 conference-style paper covering
**persons and vehicles**, whose abstract opens on "the safety of people in
floods". A standing trap in this project is that AR&R Project 10 has a people
report and a vehicles report and search engines return the people one, which is
the same confusion in a different form.

I did not tune the threshold to make this row come out right. The tool still
reports it as uncertain, because from titles and years alone it is uncertain, and
a threshold chosen after seeing the answer is not a measurement.

---

## 7. A real drop, found on the way, and it hits a paper this project uses

DERIVED, and this is the most actionable finding in the document.

Measuring whether `DROPPED_IN_MERGE` was reachable at all (section 1a) turned up
6 DOIs that appear in a report's raw text and not in the index. Three are
URL-encoding artefacts of my own extraction and decode to records that are
present. **The other three are a genuine drop**, and they are catalogue rows 11,
29 and 30 of the `settling-force` report:

| index key | recovered DOI | title |
|---|---|---|
| `settling-force#11` | `10.1061/(ASCE)0733-9429(2002)128:12(1069)` | Probability of Individual Grain Movement and Threshold Condition |
| `settling-force#29` | `10.1061/(ASCE)0733-9429(2002)128:4(369)` | Stochastic incipient motion criterion for spheres under various bed packing conditions |
| `settling-force#30` | `10.1061/(ASCE)0733-9429(1987)113:3(370)` | Do Critical Stresses for Incipient Motion and Erosion Really Exist |

They are not missing from the index. They are **in** it, with `doi = ""` and with
the raw markdown left inside the title field, for example
`"Probability of Individual Grain Movement and Threshold Condition (\[link\](htt..."`.

**Cause**, READ from `parse_report`: the DOI is pulled from a catalogue row with a
`\[link\]\((\S+?)\)` regex. Two things defeat it together. The `settling-force`
report escapes its brackets as `\[link\]`, and an ASCE DOI legitimately CONTAINS
parentheses, so a non-greedy match to the first `)` truncates it. The row still
becomes a record, silently, with no DOI.

**Consequence**, READ from the build path: cited-status is computed as
`bool(r["doi"]) and r["doi"] in cited`. A record with an empty DOI **can never be
marked cited**, however many times the repo cites it. These three are silently
parked in the "60 with no DOI, undiffable" bucket and read as unreached forever.
So 3 of that 60 are undiffable because of a parse bug, not because the source
lacks a DOI. The other 57 genuinely carry no DOI.

**Why it matters beyond bookkeeping.** `settling-force#11` is Dancey, Diplas,
Papanicolaou and Bala 2002. `CLAUDE.md`, section "AUGUST 15 2026, THE FIXED SETTLE
LENGTH IS CONTRADICTED BY OUR OWN DATA", rests a live project claim on it: "17 of
24 runs flip verdict somewhere in p >= 0.01 to 0.50, per Dancey et al 2002's
probability-of-movement criterion." So a paper the project actively depends on
sits in its own research index with no identifier and a corrupted title, and any
"is this cited?" query about it returns the wrong answer by construction.

READ, verified this session: the recovered DOI is the one Crossref and OpenAlex
both return for that paper, top candidate at score 1.0, authors Dancey, Diplas,
Papanicolaou, Bala, Journal of Hydraulic Engineering, 2002. Direct identifier
lookup did not resolve and it resolved by title search instead, which is expected
for a DOI containing parentheses in a URL path and is not evidence against the
DOI.

**Detector, not fix.** `--bib-audit` now ends with an INDEX SELF-CHECK that
reports exactly this class, with the recovered DOI, using balanced-paren
stripping so an ASCE DOI is not truncated by one character on the way out.

**I did not repair the data, deliberately.** Repairing it means editing the
`[link]` regex and running `--build`, which rewrites
`data/research_corpus_index.json` and would move the 332, the 60 and the 76/43
rungs that other sessions are quoting tonight. That file is outside my declared
write scope. Flagging it and leaving the data untouched is the correct move, and
this paragraph is the flag. The one-line fix and the three affected keys are
recorded above so whoever owns the index build can apply it without re-deriving
any of this.

## 8. The index can now report this about itself

`analysis/research_index.py --bib-audit` is new in this unit. Design points that
are not obvious:

1. **Every row records the route, not just the outcome.** Five routes run per
   work: DOI against the index, normalised title against all 332 index records,
   first-author surname against the index split into same-year and other-year,
   the DOI as a raw string in each of the eight reports, and the title against
   every catalogue row in every report. A row reading "absent" carries the best
   rejected candidate and its score, so it is checkable by someone who was not
   here.
2. **DOIs are pulled from any field**, `doi`, `note`, `url` and `howpublished`,
   and the row records **which field** the DOI came from. That single change is
   what turns the census from unauditable into auditable, per section 2.
3. **Two thresholds, not one.** 0.75 same-work and 0.40 related-work, with the
   band between them reported as `UNCERTAIN_RELATED_WORK` rather than resolved.
   A same-author same-year record also blocks a `NEVER_INGESTED` verdict.
4. **The eight-report load is a fatal assertion, not a warning.** Exercised, not
   assumed: running with `HOME` pointed elsewhere exits **2** with all eight
   paths named. Seven reports live under `~/Downloads`, where a macOS privacy
   denial has previously made recursive search report zero hits silently while
   direct reads errored, and the standing `/usr/bin/grep` remedy does not help
   because the failure is at the directory-listing layer. A partial load would
   silently reclassify works from the unread reports as never ingested, which is
   the exact distinction this audit exists to make.
5. **Reachability is checked at read time**, inside the audit, not at session
   start. Eight reports readable twenty minutes ago is not eight reports readable
   now. At the moment this document's numbers were produced, all eight were
   readable, non-empty, and each parsed to more than zero catalogue records.
6. **The ref is a required part of every answer** and is printed in the header of
   both the console output and the TSV.

---

## 9. Reproducing this, and the cross-check that shows the ref matters

```
python3 analysis/research_index.py --bib-audit \
    --tsv data/r9_bib_corpus_census.tsv

python3 analysis/research_index.py --bib-audit \
    --bib-ref "claude/add-ci-checks:paper/can_it_ford_references_IEEE.bib" \
    --tex-ref "claude/add-ci-checks:paper/conference_101719.tex"
```

READ, by `git show` piped to a count of `^@` entry openers, three refs, three
answers:

| ref | entries |
|---|---|
| `origin/main:paper/can_it_ford_references_IEEE.bib` | 21 |
| `claude/add-ci-checks:paper/can_it_ford_references_IEEE.bib` | 42 |
| `overleaf/main:can_it_ford_references_IEEE.bib` | 15 |

**Never quote a bibliography count without its ref.** A bare number is wrong on
two of the three. This is consistent with what `d5-priorart` established, which
is RECALLED here and not re-derived beyond the entry counts above.

DERIVED, the cross-check result on the 42-entry working bibliography:

| verdict | entries | of which cited |
|---|---|---|
| `IN_CORPUS` | 25 | 2 |
| `DROPPED_IN_MERGE` | **0** | **0** |
| `UNCERTAIN_RELATED_WORK` | 2 | 1 |
| `NEVER_INGESTED` | 15 | 8 |

This is the strongest single piece of evidence in the document, and it reframes
the whole open item. **The corpus overlaps the project's working bibliography
heavily, 25 of 42, and the shipped bibliography barely, 4 of 15.** The corpus is
not disjoint from what this project cites. It is disjoint from what this project
**shipped**, because the shipped bibliography is a short pipeline-and-software
list while the corpus is topical flood and MPM literature. Reading "4 of 15" as
evidence that the corpus is poorly sourced gets the direction wrong.

`DROPPED_IN_MERGE` is 0 on both refs. Per section 1a that is WEAK evidence taken
alone, because the index is built from the same eight reports. The load-bearing
result is the raw-text absence, not this.

---

## 10. What I could not verify, and what I did not touch

- **Whether "Syed Hamid Hussain Shah" and "Syed Muzzamil Hussain Shah" are the
  same person.** Not resolved. The census uses surname substring only and labels
  it as such. It affects nothing above, because `shah2018` is absent under every
  route regardless.
- **Whether the corpus SHOULD contain `shah2018`.** That is a judgment about
  search scope, not a measurement, and it belongs to whoever commissions the
  deep searches. What is measured is that it is absent and that six sibling works
  are present.
- **The 76 and 43 rungs of the published ladder.** Not re-derived here. This unit
  audited the bibliography end of the ladder only. Note for whoever re-derives
  them: 60 of the 332 records carry no DOI and are excluded from those counts by
  construction, so the denominator for a DOI-join statement is 272, not 332.
- **`analysis/research_index.py --build` was not run.** The index was read, never
  rebuilt, so `data/research_corpus_index.json` is untouched and no other
  session's view of the corpus changed.
- Nothing in `paper/`, no `.bib`, no Overleaf write, no push. `d5-priorart` owns
  those paths and its branch `claude/r8-priorart` was read, not modified.

## 11. One thing worth stealing

The census reproduced the published "11 of 14" exactly. Had I stopped there, the
honest-looking conclusion would have been "confirmed, the corpus has an
eleven-paper sourcing hole", and it would have been wrong in the way that
matters: ten of the eleven are absent because a literature search does not return
software repositories, government web pages and crash-test models, and the
eleventh is a real miss sitting next to six of its own siblings.

The integer was right and the predicate underneath it was doing no work. That is
the same shape as the withdrawn "256 are cited nowhere", which took the
complement of *reach* and reported it as *cited*. **An integer that reproduces is
not thereby a finding.** What made the difference here was carrying a
`source_kind` column that nobody asked for, because it was the only column that
could distinguish a category boundary from a defect.

---

# PART 2, 2026-08-19: WHAT IT WOULD TAKE FOR THE BUILDER TO SEE THE DEEP SEARCHES

Part 1 established that `--build` cannot reach a deep search and never could.
That is a diagnosis, not a fix, and a diagnosis nobody can act on is worth
little. This part says what the fix is, proves the mechanism works before
recommending it, and corrects three claims, one of them mine.

Everything below was measured on 2026-08-19 against the live workspace
`17299f2a-8dc8-438b-8c84-5abf19395e2c` and the committed index. Tags as before:
READ, DERIVED, RECALLED.

## 12. The one-line answer

**A two-part adapter: a session-side exporter that has the connector, and a
build-side reader that does not.** The builder is pure standard library and
runs outside any MCP session, so it cannot call Undermind itself. That is not
an incidental limitation to engineer around, it is the constraint that picks
the design: the fetch has to happen where the connector lives, the build has to
happen where it does not, and the only thing that can cross between them is a
file.

Implemented this unit, in `analysis/research_index.py`:

```
python3 analysis/research_index.py --source-audit
python3 analysis/research_index.py --identifier-audit
python3 analysis/research_index.py --ingest-check FILE.json
python3 analysis/research_index.py --ingest-check FILE.json --against-slug SLUG
```

The exporter half is NOT implemented, and section 18 says why and what it costs.

## 13. The control, run before the recommendation

An adapter fed by the API must first reproduce what the markdown route already
produced, on a search that went through the markdown route. Otherwise "ingest
the other twelve" is a proposal to add 692 unverified records to the instrument
every session is told to trust.

DERIVED, three checks, increasing in strength:

**Check 1, cardinality on all eight ingested searches.** The API's
relevant-paper count against the index's `papers_per_report`:

| slug | index | API |
|---|---|---|
| wall-penetration | 16 | 16 |
| trustworthy-ai | 13 | 13 |
| moving-rigid-body | 44 | 44 |
| validated-coupling | 60 | 60 |
| settling-force | 68 | 68 |
| mpm-verification | 68 | 68 |
| multi-resolution | 78 | 78 |
| reliable-ai | 79 | 79 |

Eight of eight, and they sum to **426**, which is exactly the raw-row count the
markdown route produced before merging to 332. Equal counts are not equal sets,
so this is necessary and not sufficient.

**Check 2, membership at rank 1.** The top-ranked paper of each of the eight is
present in the index by DOI. Eight of eight.

**Check 3, a full export compared record by record.** All 44 papers of
`Moving Rigid Body Free Surface Validation` were pulled from the API, written in
the interchange format, and compared against the index's 44 records for that
slug:

```
  in both          35
  same paper, different key   9
  export only, unpaired       0
  index only, unpaired        0
  SET-IDENTICAL, KEY SCHEME DIFFERS.
```

35 match on DOI. The other 9 are the DOI-less records, which the index keys
positionally (`moving-rigid-body#15`) and the adapter keys by Semantic Scholar
id (`s2:598636f5...`). They pair one-to-one by title with nothing left over on
either side. **The API route reproduces the markdown route's paper set exactly.**

That is the evidence for the recommendation. Without it, "use the API" would be
a plausible claim rather than a tested one.

### The control failed twice first, and both were my bugs

Worth recording, because a gate that passes first time has usually not been
exercised. `--ingest-check` rejected all 44 papers as unjoinable, then flagged a
legitimate title as mangled.

1. `norm_doi` only parses `doi.org/...` URLs, because that is the form the
   markdown reports carry. An API export carries the bare string
   `10.1115/1.4071177`, so every DOI normalised to empty and every record looked
   identifier-less. The symptom presented as a finding about the data. Fixed by
   `norm_doi_field`, which accepts either form.
2. The mangled-title signature included `\)\s*$`, which flags any title legitimately
   ending in a parenthesis, such as `... (CCP-WSI Blind Test Series 3)`.

Both were found by running the gate on 44 real records. Neither would have been
found by reading it.

## 14. The interchange format

One JSON file per search, in a tracked directory, discovered by glob.

```json
{
  "schema": "canford.deep_search/1",
  "workspace_id": "17299f2a-8dc8-438b-8c84-5abf19395e2c",
  "search_path": "/Simulation Ready Vehicle Mesh Assets",
  "slug": "vehicle-mesh",
  "created": "2026-07-21",
  "exported": "2026-08-19",
  "exported_by": "slot d14-corpusbib, inspect_deep_searches + get_paper_info",
  "n_relevant": 36,
  "goal": "...the search's stated research goal...",
  "summary": "...the search's synthesis prose...",
  "papers": [
    {"cite_key": "Mar13", "rank": 1, "relevance": 1.480,
     "title": "...", "year": 2013, "authors": "...", "journal": "...",
     "doi": "", "s2": "347f2ce0...", "link": "https://...",
     "citations": 16, "cit_per_year": 1.2, "abstract": ""}
  ]
}
```

Two design points that are not cosmetic.

**`goal` and `summary` are first-class, not decoration.** They are the part a
paper index structurally cannot hold, and section 17 shows they are the part
that actually answered the question this whole thread started from.

**The join key has a precedence, and the positional fallback is an error rather
than a default.** DOI first, because it is what the repo cites with. Semantic
Scholar id second, because it is stable across rebuilds and re-rankings. A
positional `slug#rank` key is refused, because it is not an identifier: re-run a
search, it re-ranks, and every positional key silently moves to a different
paper.

## 15. The gates, each one from an observed failure

`validate_search_export` refuses an import rather than degrading it. Every gate
exists because the failure was seen in the live payload on 2026-08-19, not
because it seemed prudent.

| gate | refuses | observed |
|---|---|---|
| G1 | `n_relevant` disagreeing with `len(papers)` | `inspect_deep_searches` pages at 50 and reports the true total in its header, so a one-page export of a 105-paper search looks complete |
| G2 | a paper with neither DOI nor S2 id | it would enter as a permanent orphan, which is the present state of `settling-force#11`, `#29`, `#30` |
| G3 | raw markdown in a title | the exact signature of the parse defect in section 7 |
| G4 | (warns) authors with no comma, initial or "and" | the Undermind record for the 2012 Camry model truncates its title at "...for the 2012 Toyota" and puts "Camry Passenger Sedan" in the author field |
| G5 | a slug colliding with a `REPORTS` slug | silent double-ingestion |

G4 warns rather than errors because it is upstream data, not ours, and throwing
it away loses a real record.

## 16. The identifier finding, which is section 2 again in a new place

Part 1 opened with "the DOIs were in a field nobody joined on". Building the
adapter surfaced the same shape a second time, and this one is larger.

DERIVED, `--identifier-audit`, scope `data/research_corpus_index.json` as built
2026-08-15, `.claude/worktrees/` excluded:

```
  332  records
  272  keyed by DOI
   57  no DOI, but a Semantic Scholar id ALREADY SITTING IN `link`
    3  neither, and therefore unidentifiable
```

**Only 3 of 332 records are genuinely unidentifiable, and all 3 are the parse
defect from section 7.** The other 57 carry a stable identifier that nothing
joins on.

**This corrects a line of my own.** The `--bib-audit` header prints "60 with no
DOI and therefore unmatchable by the DOI route". That is true as written and
invites a false conclusion, because a reader takes "no DOI" for
"unidentifiable". Sixty are unmatchable *by the DOI route*. Three are
unidentifiable. The header now says which.

### It also means the headline count is overstated

DERIVED: **11 Semantic Scholar ids appear under 24 different record keys**, and
in all 11 groups the members carry a byte-identical title. So the index's 332
records represent **319 distinct works**, an excess of 13.

The mechanism is exactly the positional key. These papers have no DOI, the merge
dedups on DOI, and the same paper appearing in three reports became three
records. `Experimental testing of flood hazard curves for a partially submerged
vehicle` is in there three times; so is `A method for automated regression test
in scientific computing`.

**So "332 distinct external papers", which `CLAUDE.md` states and every session
reads at launch, is high by 13.** State it as 332 records / 319 distinct works,
or re-derive with the S2 join. This does not move the 76, 43, 4 or 3 rungs,
which are DOI-keyed and unaffected.

### The worked example is not hypothetical

`CLAUDE.md` names four prior vehicle fording works the paper cites none of, and
identifies one of them only by a Semantic Scholar prefix, `61da26b6`. That paper
is **in this index**, as `moving-rigid-body#39`, "Investigation of the Vehicle
Mobility in Fording", Pazouki et al 2016.

Three independent mechanisms each individually guarantee the index cannot tell
you it holds it:

- `--doi` cannot find it, because it has no DOI.
- `--query "Pazouki"` cannot find it, because `--query` matches title and
  abstract only, never authors.
- cited-status cannot mark it, because it is gated on `bool(doi)` at `:396-397`.

An absence found by a search that cannot match is not an absence. This is that
sentence with a name attached.

## 17. A paper-only adapter would NOT have prevented the loss

This is the part that surprised me and it changes the recommendation's shape.

The motivating incident is that a session re-derived the CCSA/NCAC vehicle-model
answer by hand, at the cost of a full turn, when
`Simulation Ready Vehicle Mesh Assets` had answered it on 21 July. The obvious
inference is "ingest that search's 36 papers and the loss goes away". DERIVED,
that inference is wrong.

Of the 36 papers in that search, 22 carry a DOI and 14 do not. Of the 22,
**6 are already in the index**: Smith 2019, Al-Qadami 2021, 2022 and 2023,
Wasfy 2015, and Allen 2003. Those are every flood-vehicle and prior-art work in
the set, and they arrived through other searches. So the papers that matter most
were never missing.

What was missing is in two places the paper layer does not reach:

- **The synthesis.** "The NHTSA-grade assets are the 2010 Yaris, 2012 Camry and
  2007 Silverado; the Rogue is not among them; no public PLY conversion of any
  of them is verified to exist" is a conclusion drawn across the set. It lives
  in the search's `summary`, and a paper index has nowhere to put it.
- **The DOI-less grey literature.** The 14 without DOIs are the NCAC and MASH
  validation reports themselves, which are the documents that answer the
  question. Under the current schema they could only enter positionally, and
  would be unjoinable and permanently uncited.

**So the recommendation is not "ingest the papers". It is "ingest the search",
with `goal` and `summary` as first-class fields and an identifier scheme that
admits DOI-less reports.** A paper-only adapter would have imported 16 new
crash-test and CFD-dataset records and still not answered the question.

## 18. What it costs, and what is not done

READ, from the tool schemas: `inspect_deep_searches` pages at 50 papers per
call, `get_paper_info` accepts 50 cite keys per call and is the only route to a
DOI (the search listing carries none).

DERIVED, for the 12 invisible searches at their measured sizes (105, 92, 82, 81,
56, 48, 47, 47, 43, 36, 32, 23):

- about **18** `inspect_deep_searches` calls for the paper lists,
- about **18** `get_paper_info` calls for DOIs and S2 ids,
- **12** more for each search's goal and summary.

Roughly **50 connector calls, one session, no GPU.** That is the whole cost of
the exporter half.

**NOT DONE, and it is a scope boundary rather than a judgement.** My declared
write scope is four paths. Creating `data/deep_searches/` and the 12 export
files is outside it, so this unit ships the reader, the gates and the control,
and the directory does not exist. `--source-audit` therefore prints

```
  RUNG 2, exported deep searches discovered by glob: 0
    NONE. The directory does not exist or is empty, so this
    adapter contributes nothing today.
```

which is deliberate: a source audit that printed a clean eight-of-eight would be
the exact false all-clear this tool exists to prevent. Whoever picks this up
needs one decision (where the exports live) and one session.

The demonstration export used for check 3 is real, built from the live API, and
lives in this session's scratchpad rather than the repo for the same reason.

## 19. The hardcoded snapshot is the same defect one level up

`WORKSPACE_DEEP_SEARCHES` in `analysis/research_index.py` is a hardcoded list of
20. It cannot notice search 21, which is precisely the criticism this document
levels at `REPORTS`. Building a second fixed list to describe the first one's
staleness would be absurd, so `--source-audit` ends by printing the exact call
that re-derives it and the count to compare against. The constant is auditable
rather than trusted. It is still a snapshot, and it should be replaced by the
manifest once the export directory exists.

## 20. Three corrections, one of them to a live file

**(a) `Moving Rigid Body Free Surface Validation` is INGESTED, not invisible.**
The coordinator's message of 2026-08-19 cited it as one of the twelve the
builder cannot see, and named `[Kra21b]` as an instrument d11-accessor needs.
READ, live: that search is `moving-rigid-body`, one of the eight in `REPORTS`,
44 papers, and Kramer et al 2021 is in the index right now as
`10.3390/en14020269`, `reports: ['moving-rigid-body']`, `cited_in_repo: True`.
**d11-accessor can find it today** with
`python3 analysis/research_index.py --doi 10.3390/en14020269`. The twelve
invisible searches are listed in full by `--source-audit`; that one is not among
them. `Simulation Ready Vehicle Mesh Assets` is, so the other half of the message
holds.

**(b) `faf53d1` misattributes the physics test.** It says `df52bee` added
`tests/test_physics_gates.py`. READ, `git log --diff-filter=A -- tests/test_physics_gates.py`
returns `50b70c0` ("Add the three physics gates: analytical, conservation,
metamorphic"); `df52bee` changed it by +23/-7. This matters because `faf53d1` is
on `claude/add-ci-checks`, which is the checked-out state of the main tree, so
the skill every session loads at launch carries the wrong SHA.

**(c) `faf53d1` carries the count I already refuted.** It states nineteen
searches and "eight checked by name are all absent". Live: twenty, of which
eight are ingested and twelve are not. The coordinator has accepted this; the
file has not been updated, and it is the one every session reads.

## 21. What I could not verify, and what I did not touch

- **`shand2011arr` is still not resolved to present, and I nearly got this
  wrong.** The census flagged it `UNCERTAIN_RELATED_WORK` with a same-author
  same-year candidate at title score 0.27, and refused to force a verdict. The
  adapter run surfaced that candidate as `moving-rigid-body#44`, Shand, Smith,
  Cox and Blacka 2011, "Development of Appropriate Criteria for the Safety and
  Stability of Persons and Vehicles in Floods". The bibliography cites the AR&R
  Project 10 **literature review**. Reading both titles, these are two different
  documents by the same team in the same year, so the entry stays absent and
  **the "4 of 15" rung is unchanged**. This is a human read, not a measurement.
- **Set equality was demonstrated on one search of the eight, not all eight.**
  Checks 1 and 2 cover all eight at lower strength. A full export of the other
  seven would close it.
- **Nothing was rebuilt.** `--build` was not run,
  `data/research_corpus_index.json` is untouched, and no other session's view of
  the corpus changed. `data/r9_bib_corpus_census.tsv` regenerated
  byte-identically, which is the reproducibility check on the Part 1 numbers.
- Nothing in `paper/`, no `.bib`, no Overleaf write, no push.

---

# PART 3, 2026-08-19: THE EXPORTER, AND THE RETRACTION OF THIS DOCUMENT'S HEADLINE

## 22. RETRACTED: "it is a sourcing gap, not a dropped merge"

Part 1's title says the corpus/bibliography gap is **a sourcing gap**, and
section 1 says of the 11 absent works "**They were never returned by any
search.**"

**That sentence is WITHDRAWN.** It is false, and it is false by the exact
mechanism this document is named after.

READ, live 2026-08-19 from the workspace: `shah2018`
(`10.1051/matecconf/201820307003`) is `[Sha18c]` and it appears in **three**
completed deep searches:

| deep search | created | relative to the 2026-08-15 index build |
|---|---|---|
| `Dynamic Vehicle Traction in Floodwater` | 2026-07-21 | **PREDATES it by 25 days** |
| `moving vehicle floodwater GPU particle simulation` | 2026-08-18 | postdates |
| `moving vehicle floodwater simulation open source implementations` | 2026-08-19 | postdates |

The first one settles it. The project had sourced this paper **25 days before
the index was built**, and it is absent from the corpus only because
`Dynamic Vehicle Traction in Floodwater` is not in the hardcoded `REPORTS` list.

**So it is an INGESTION gap, not a sourcing gap.** Nobody needs to go and find
this paper. It has been found, twice more since, and the reader has now read its
full text.

### How I got it wrong, which is the point

The evidence I offered was: the DOI and title appear nowhere in the raw text of
any of the **eight source reports**. That measurement is correct and I would
make it again. The inference from it was not.

**Eight reports cannot testify about twenty searches.** I searched the container
that the builder can see, found nothing, and reported it as absence from the
project's research. That is an absence found by a search that could not have
matched, committed by me, in the document that names the rule, one commit after
I wrote the rule into the skill every session loads.

It is also the same argument I made correctly elsewhere. Commit `6ecf4e5`
reasons that `ccsa2016yaris` is invisible because the builder cannot reach the
layer holding it. I applied that to the vehicle-mesh case and not to
`shah2018`, in the same document, on the same day.

The two framings have very different consequences, which is why this matters
rather than being a wording quibble:

- *sourcing gap* means someone must commission a search and go find the paper.
- *ingestion gap* means the paper is already in the workspace and the builder
  cannot see it, so the fix is the adapter in Part 2 and nothing else.

**The corrected headline: the corpus is not a superset of the bibliography
because the builder cannot reach the layer that holds the missing works.**
The "one paper wide, not eleven" finding in section 4 SURVIVES unchanged: ten of
the eleven are absent for reasons of category, and `shah2018` is the one
in-scope work. What changes is why it is absent.

### A metadata trap on the same record

The workspace gives the first author as **Syed Hamid Hussain Shah**. Crossref,
resolved live via `verifyCitation`, gives **Syed Muzzamil Hussain Shah**, with
Mustaffa, Kim and Yusof, "Instability Criteria for Vehicles in Motion Exposed to
Flood Risks", MATEC Web of Conferences 203, 07003, 2018. Verdict `matched`,
confidence high, zero field mismatches.

So the authoritative given name is **Muzzamil** and the WORKSPACE record carries
the variant. This project has recorded the Muzzamil/Hamid variant before. State
the direction when you use it: an author-route census keyed on the workspace
spelling will silently miss this work.

## 23. The exporter exists, and two searches are through it

Part 2 shipped the reader and said the exporter was the missing half. It is
written now, in the only place it can be: a session that holds the connector.

**The procedure, which is the deliverable, not the two files:**

1. `inspect_deep_searches(workspace_id, names=['/NAME'])` gives the search's
   `goal`, its results `summary`, and the ranked paper list. Page at 50.
2. `get_paper_info(workspace_id, cite_keys=[...50 max...], show_doi=True)` is the
   **only** route to a DOI. The search listing carries none.
3. Write the `canford.deep_search/1` object from section 14 to
   `data/deep_searches/<slug>.json`.
4. `--ingest-check` it. Do not hand-fix a rejection; fix the export.

Two searches are exported and both pass the gates:

```
  RUNG 2, exported deep searches discovered by glob: 2
    OK      buoyancy-overestimation.json             32 papers
    OK      vehicle-mesh-assets.json                 36 papers
  RUNG 3: 20 known, 8 ingested as markdown, 2 exported, 10 still invisible
```

**AN EXPORT IS NOT AN INGESTION**, and `--source-audit` now says so in those
words. The files are on disk and pass the gates; `--build` has not consumed
them, so the corpus is unchanged and a `--query` still cannot reach them.
Wiring `parse_search_export` into `build()` moves the 332, the 60 and the 76/43
rungs, and whoever owns the index build should do that deliberately rather than
as a side effect of this unit.

### A third identifier type, found by running it

`[Miy23]` carries an **arXiv** link rather than a Semantic Scholar one, and the
S2-only key scheme rejected it as unjoinable when it is perfectly identifiable.
`join_key` now has three types in precedence order: `doi`, `s2:<40 hex>`,
`arxiv:<id>`, positional last and refused. Found by exporting 32 real records,
not by review. That is the second time this unit that running the gate on real
data found a gap in the gate.

## 24. FOR d11-accessor AND d21-jobb-route, what the buoyancy search actually says

`data/deep_searches/buoyancy-overestimation.json` carries the full goal and
summary. Four findings bear directly on how Job B is graded. These are the
search's conclusions, RECALLED from its summary and NOT independently verified
against the 32 primary sources.

1. **The literature does NOT establish that impulse-exchange force extraction
   intrinsically double-counts gravity**, and does not establish a universal
   50 percent bias. So a large positive buoyancy bias cannot be attributed to
   the accessor on the literature's authority; it has to be shown.
2. **A positive bias is more plausibly a discrete hydrostatic and
   interface-coupling error than a tank-size effect.** That is consistent with
   the pinned-span control this project already ran, which found the tank effect
   small.
3. **Kramer's 0.3 percent is a MOTION benchmark, not a static-force tolerance.**
   The search states this explicitly. Grading a static force against a number
   quoted from a heave-decay experiment is a category error, and this is the
   instrument d11-accessor is grading Job B against.
4. **The literature rarely reports force-extraction windows, pressure-surface
   versus impulse-exchange cross-checks, or systematic particles-per-cell
   convergence.** This project has TWO force accessors that disagree by roughly
   a factor of two and even on sign. That disagreement is not an anomaly to be
   embarrassed by; it is the diagnostic the field under-reports, and reporting
   both is publishable rather than disqualifying.

Also in that search and already in the corpus: Steffen's quadrature-error work,
Bauer 2023 on spatial integration errors (`10.1002/nme.7217`), Zhang 2017 on
incompressible MPM for free surfaces (`10.1016/j.jcp.2016.10.064`), and Hu 2018
CPIC (`10.1145/3197517.3201293`), which `CLAUDE.md` A-1 already names as the
literature-backed alternative coupling architecture.

## 25. Still open after this unit

- **10 of 20 searches remain unexported**, including the 105-paper
  `moving vehicle floodwater simulation open source implementations` and the
  43-paper `Dynamic Vehicle Traction in Floodwater` that holds `shah2018`.
  Roughly 40 connector calls at the rates in section 18.
- **`build()` does not read the export directory.** The reader, the gates and
  the discovery glob exist and are exercised; the wiring into `build()` is one
  function call and a rebuild, and it moves published counts.
- **The two exports carry no abstracts.** `detail_level='full'` returns them at
  a smaller page size; without them, `tags_for` under-tags every record, exactly
  the metadata-only limitation the skill already warns about.
- **The section 24 findings are the search's own conclusions**, one remove from
  the 32 papers. An AI research report saying a paper says X is not that paper
  saying X.

## 26. THE EXPORT DIRECTORY IS GITIGNORED, AND THAT NEARLY ATE THE WHOLE FIX

Found at commit time, not design time. `data/*` in `.gitignore` matches
`data/deep_searches/`, so both export files were **invisible to `git status`**.
Re-derive the rule rather than trusting a line number, which this project's
standing rules require for `.gitignore` specifically:

```
git check-ignore -v data/deep_searches/buoyancy-overestimation.json
```

Had I committed without checking, the outcome would have been the exact failure
this unit exists to fix: an adapter that works on my disk, a `--source-audit`
that reports two exports on my machine and zero everywhere else, and a sibling
session told the buoyancy search was available when its checkout has no such
file. A local-only artifact reported as a shared one.

**What I did:** `git add -f` on the two files, so they are tracked and reachable
by d11-accessor and d21-jobb-route now.

**What I did NOT do, and it needs doing.** `git add -f` tracks *these two* files
and leaves the DIRECTORY ignored, so the eleventh export anyone writes will be
silently dropped again. The durable fix is an un-ignore pair for
`data/deep_searches/` in `.gitignore`. **`.gitignore` is outside this slot's
declared write scope and it is a file this project has already recorded three
stale line-number citations against in one day, so I have not edited it.**
Whoever owns it should add the pair and verify with `git check-ignore -v`.
Until then, every export needs `-f` and nothing warns you.


---

# PART 4, 2026-08-19 23:20: THE INGEST PATH IS WIRED, AND THE INDEX HOLDS NO FULL TEXT

## 27. THE HEADLINE THAT SHOULD HAVE BEEN FIRST: nothing here has been read

VERIFIED against the schema, not relayed. A record in
`data/research_corpus_index.json` has exactly **15 fields**: `title`, `authors`,
`journal`, `year`, `doi`, `link`, `abstract`, `methods`, `reports`,
`report_index`, `n_reports`, `cit_per_year`, `has_abstract`, `cited_in_repo`,
`cited_reader_facing`.

**There is no full-text field, no body field and no PDF field.**

- 222 of 332 records carry a non-empty `abstract`. **110 carry nothing but
  bibliographic metadata.**
- The single largest text blob anywhere in the file is **3,477 characters**.
  The median non-empty abstract is **1,305**.

A research paper is tens of thousands of characters. So the most this index has
ever held of any paper is its abstract, and for a third of the corpus not even
that. **"The corpus was read" has never been true of any session and could not
have been.** Every method claim, novelty claim and "nobody has done this" this
project has sourced from the index has been sourced from titles, abstracts and
an AI-written summary, one to three removes from the paper.

That is not a reason to distrust the index. It is a reason to state what it is:
a **discovery** instrument, not a reading one. Reading means
`mcp__undermind__read_pdfs` against the workspace and nothing else does. This is
now the first paragraph of the skill every session loads.

## 28. It is 21 searches and 13 absent, and the count outran two documents today

READ, live 2026-08-19 23:20, all 21 completed. A twenty-first landed at 17:44:
`free surface elevation estimator error in particle method buoyancy validation`,
88 papers.

| when | searches | in the corpus | absent |
|---|---|---|---|
| 2026-08-18 | 19 | 8 | 11 |
| 2026-08-19 18:00 | 20 | 8 | 12 |
| **2026-08-19 23:20** | **21** | **8** | **13** |

**The ingested number has not moved in five weeks while the total has moved
three times in two days.** My own Part 2 said "12 of 20" and was correct when
written and stale within five hours. `WORKSPACE_DEEP_SEARCHES` is updated to 21
and carries a comment saying not to trust its length.

The durable answer is not a better constant. `--source-audit` now **exits 1**
when a completed search reaches the corpus by no route, and prints the connector
call that re-derives the list. Nothing can ingest a search the moment it
completes, because the builder cannot call the connector. What can happen the
moment it completes is that a check goes red. Wire `--source-audit` into
preflight or CI and a new search stops being discovered by accident three days
later.

## 29. `build()` now reads the exports, and doing it found a real defect first

`build()` takes the eight markdown reports as before and then merges every
export in `data/deep_searches/`, through the same `_merge_into` both routes
share. The markdown path is kept because eight searches exist only in that form.

**The first wiring was wrong, and the control I built in Part 2 is what caught
it.** A trial build put Pazouki et al 2016 under **three** keys with identical
titles: `moving-rigid-body#39`, `validated-coupling#15` and
`s2:61da26b6...`. The markdown parser keys a DOI-less record positionally, the
export route keys it by Semantic Scholar id, so the same paper entered twice
more instead of merging. **The export route made an existing duplication worse.**

The fix is `canonicalise_keys`, applied to both routes before merging: wherever
a stable identifier exists it replaces the positional key. After it, the trial
build has **zero titles under more than one key**, and Pazouki is one record
carrying `['moving-rigid-body', 'validated-coupling', 'vehicle-mesh-assets']`.

### What a rebuild would change, measured and decomposed

Run with `--out` to a scratch path. **The committed index was NOT overwritten.**

| | committed | + dedup only | + the 2 exports |
|---|---|---|---|
| papers | 332 | **319** | 369 |
| with abstract | 222 | 211 | 211 |
| cited anywhere | 76 | 66 | 98 |
| reader-facing | 43 | 52 | 52 |
| no DOI | 60 | 47 | 64 |

Three things worth reading carefully.

**319 reproduces exactly, by a route independent of how it was first derived.**
Part 2 got 319 by counting Semantic Scholar groups in the committed file. This
gets 319 by actually rebuilding with the duplicates collapsed. Two different
methods, same integer.

**`cited anywhere` FALLS from 76 to 66 under dedup alone.** The published 76 was
inflated by the same duplicate counting as the 332: one paper cited once was
counted several times. That number is used in the ladder.

**`reader-facing` RISES from 43 to 52 under dedup alone, and this one is a
measurement change I introduced, not new research.** `_merge_into` now fills a
missing `doi` from a merged sibling, so a record that was positional and
DOI-less can inherit a DOI and become diffable. It is a correct improvement, but
it means the 43-to-52 move says the measurement got better, NOT that nine more
papers reached the reader. **Do not republish 52 as a reach figure without
re-deriving it deliberately.**

**I did not run `--build` against the committed index.** Every session reads that
file and `CLAUDE.md` publishes the 332 / 60 / 76 / 43 rungs from it. The rebuild
moves all four, and one of them in a direction that needs review. That is a
decision for whoever owns the index and the CLAUDE.md text, not a side effect of
my unit. `--build` now prints a warning when its target is the committed index.

## 30. FOR d21-jobb-route: the new search says the error may be in the DENOMINATOR

`free surface elevation estimator error in particle method buoyancy validation`,
run at 17:44 today, 88 papers, **not exported** (see section 31). Its goal text
carries d21's configuration exactly, including the 35 to 64 percent excess over
six runs and four windows. RECALLED from its summary, NOT checked against its 88
sources.

**It reframes the problem as three separable channels rather than one "MPM
buoyancy error": surface reconstruction, pressure and hydrostatics, and
body-boundary coupling.**

The first is the one this project has not tested and it is the cheapest:

> Near-body exclusion is **not established as a benign operation**. A cheap
> discriminator is to recompute elevation with **nested exclusion radii
> including zero**, local vertical columns, and a geometric or level-set
> reconstruction, then compare the resulting analytic buoyancy against the same
> raw force. **A body-off hydrostatic run gives the estimator bias independently
> of body loading.**

If the surface estimator excludes an annulus of two sphere radii, that annulus is
exactly where the surface is deformed by the body and where the pressure
generating the vertical force acts. A surface-elevation offset under two
centimetres, about one grid cell, would account for the entire discrepancy **with
no solver error at all**. Both discriminators run on existing data, no GPU.

One more, and it collides with something another slot has already concluded:
the search cites `[Sch19e]` for **traditional MPM wall momentum zeroing
distorting stress several grid lengths into an object, with image-particle
boundaries reducing the artifact.** Slot d19-priorcode has reported
`simulation/image_particles.py` as implemented, run and **refuted**. Those two
statements are about the same mechanism and point opposite ways. **Not resolved
here, and I am flagging rather than adjudicating it:** one of them is about a
method's potential and the other about this repo's implementation of it, which
is exactly the distinction that gets collapsed. Whoever owns the boundary
treatment should read `[Sch19e]` before the refutation is treated as settled.

## 31. What I did not do, stated so it is not mistaken for done

- **11 of 21 searches are still unexported**, including the 88-paper one this
  section is about and the 105-paper open-source one. I exported 2 of 13 and
  stopped; the remaining 11 are roughly 40 connector calls. `--source-audit`
  exits 1 naming every one of them, so this is loud rather than silent.
- **The 88-paper search is quoted from its own summary**, not exported and not
  read. Its `[Wal07]` (Wallstedt and Guilkey 2007, `10.3970/CMES.2007.019.223`)
  is reported by the coordinator to give the mechanism for Job B; that is a
  `read_pdfs` result I have not independently reproduced, and it is already in
  the corpus and in the buoyancy export.
- **The committed index is untouched**, so no other session's view changed
  during this unit. Everything in section 29 is from `--out` builds.
- **`data/deep_searches/` is still gitignored** by `data/*` and needs an
  un-ignore pair. Section 26. Every export still needs `git add -f`.

---

# PART 5, 2026-08-20: WHAT IT WOULD TAKE TO LAND THIS BRANCH ONTO `claude/add-ci-checks`

**SCOPE ONLY. NOTHING IN THIS PART HAS BEEN EXECUTED.** No merge, no rebase, no
push, no branch created. Every command below is written to be read before it is
run.

## 32. Why it is urgent, measured across all 36 worktrees

The corrections do not propagate, and the damage is timed. `--query` was fixed
at 00:21 on 2026-08-19; `d17-moving` committed the pre-fix claim at 00:43.

Measured live 2026-08-20 by content hash over every worktree:

| content | lines | copies | what it is |
|---|---|---|---|
| `05eff121` | 670 | **1** | this branch, the only corrected copy |
| `c8e98889` | 249 | 3 | `faf53d1`, the coordinator's version |
| `057e5d6d` | 152 | 9 | the **pre-`faf53d1` base**, corrected by nobody |
| absent | 0 | 23 | the branch has no such file |

**And the root of it: `origin/main` carries NEITHER `analysis/research_index.py`
NOR `.claude/skills/research-corpus/SKILL.md` NOR
`data/research_corpus_index.json`.** Verified by `git ls-tree`, all three return
nothing. So a fresh clone has no corpus tool at all, and the landing target
`claude/add-ci-checks` has a half-fixed one: 88 commits ahead of `origin/main`
and still author-blind in `--query`.

This is not a documentation problem. Nine worktrees are sitting on a copy that
predates even the coordinator's corrections, and no amount of writing in my copy
reaches them.

## 33. What actually conflicts is ONE file, and it is smaller than reported

Merge base `af62473`, which is a commit on this branch. Since then:
`claude/add-ci-checks` has 23 commits, this branch 9.

**This branch touches 6 files. `claude/add-ci-checks` has touched exactly 1 of
them.**

| file | their side since the base | resolution |
|---|---|---|
| `analysis/research_index.py` | **untouched, blob `b775b31` identical to base** | clean take-mine |
| `docs/R9_CORPUS_BIB_GAP_2026-08-18.md` | does not exist there | clean add |
| `data/r9_bib_corpus_census.tsv` | does not exist there | clean add |
| `data/deep_searches/*.json` (2) | do not exist there | clean add, but see 35 |
| `.claude/skills/research-corpus/SKILL.md` | **101 lines added** | the only real merge |

`research_index.py` being byte-identical to the merge base on their side is the
single most useful fact here: **the file that fixes `--query` lands without a
conflict at all.**

### The SKILL.md union, re-measured after this turn

`d16` measured SKILL.md as a genuine union where neither side is a superset, all
of `add-ci-checks`' added lines absent from mine. **That was true when measured
and it is no longer true, because I closed the gap in this turn.**

Line-level, their 101 added lines are 70 substantive, of which 54 do not appear
verbatim in mine. That number is misleading on its own: a line-level diff cannot
see rewording, and I rewrote most of that material. Checked **by theme** instead,
which is what actually decides a merge:

**13 of 13 themes from `claude/add-ci-checks` are now carried here**, including
the CCSA/NCAC vehicle answer, the hard negative on public PLY conversions, the
workspace query recipe, and the physics-regression-test correction.

The last gap was the **measured hull vertex counts**, which existed only on their
side. I did not copy them. I re-read `element vertex` from all five PLY headers
on 2026-08-20 and **all five match**: yaris 327,212, rogue_g96 31,357,
silverado_g32 2,108, and the two unused hulls at 66,987 and 48,706. Added here
with one correction: the circulating "155x coarser" is Yaris-against-Silverado,
a **cross-vehicle** comparison that cannot support a claim about either vehicle's
resolution. The within-vehicle figures are **23.1x** for the Silverado and
**2.14x** for the Rogue, against better hulls already sitting on disk.

**So the merge is now take-mine on both files, not a union.** That is a
consequence of work done this turn and it should be re-verified rather than
trusted: the acceptance test in section 36 is exactly that check.

**DO NOT take `add-ci-checks`' SKILL.md content in the merge.** Eight of its
added lines are claims this branch refuted with evidence: the withdrawn "256 are
cited nowhere", "nineteen completed deep searches" against the measured 21, and
`df52bee` as the commit that added `tests/test_physics_gates.py` when
`git log --diff-filter=A` returns `50b70c0`. **A `-X theirs` or a naive union
would reintroduce all three and undo the reason for landing.**

## 34. The procedure, if a human says go

Written for review, not for pasting unread. Steps 4 and 6 are the ones that can
lose work.

```
# 1. Confirm nobody else is mid-write on the target.
git -C /Users/josie/can-it-ford status --porcelain
tmux list-panes -a | grep add-ci-checks

# 2. Record the pre-state so the acceptance test has a baseline.
git -C /Users/josie/can-it-ford rev-parse claude/add-ci-checks
git -C /Users/josie/can-it-ford ls-tree claude/add-ci-checks -- analysis/research_index.py

# 3. Work on a throwaway branch, never on add-ci-checks directly.
git -C /Users/josie/can-it-ford branch land-corpus-trial claude/add-ci-checks

# 4. Merge. EXPECT A CONFLICT IN SKILL.md AND ONLY THERE.
git -C /Users/josie/can-it-ford merge --no-commit --no-ff claude/r9-corpus-bib

# 5. Resolve SKILL.md by taking THIS branch's copy wholesale, having first
#    re-run the acceptance test in section 36 to prove it is a superset.
git -C /Users/josie/can-it-ford checkout claude/r9-corpus-bib -- \
    .claude/skills/research-corpus/SKILL.md

# 6. The two exports are gitignored by data/*, so a merge will NOT carry them
#    silently. Add explicitly, or they vanish without a warning.
git -C /Users/josie/can-it-ford add -f \
    data/deep_searches/buoyancy-overestimation.json \
    data/deep_searches/vehicle-mesh-assets.json

# 7. Commit the merge, then run every check before anything is pushed.
```

## 35. Five hazards, each one measured rather than anticipated

1. **A CONFLICTED MERGE IS REFUSED BY THE PRE-COMMIT HOOK.** Verified live:
   `.git/hooks/pre-commit` refuses more than 8 staged files, and there is **no
   `pre-merge-commit` hook**. So a CLEAN merge of any size passes, while a
   CONFLICTED merge runs `pre-commit` against a large staged set and is blocked.
   This merge stages 6+ files. **Expect the commit to be refused and do not
   interpret that as a merge failure.**
2. **`data/deep_searches/` is gitignored** by the `data/*` rule. Re-derive it
   with `git check-ignore -v <path>`, never by line number. Without step 6 the
   exports are dropped silently, which is the exact failure mode section 26
   records.
3. **`git checkout <branch> -- <path>` in step 5 is a wholesale overwrite.** It
   is correct ONLY if the acceptance test passes first. If it does not, the
   resolution is a hand-merge and this plan is void.
4. **`claude/add-ci-checks` is a live branch with 23 commits since the base and
   other sessions on it.** Its HEAD may move between reading this and running
   it. Step 2 exists so a moved HEAD is detected rather than merged over.
5. **THE REPO IS PUBLIC and `pre-push` requires `PUSH_OK=1`.** Nothing in this
   plan pushes. A push is a separate decision and needs its own confirmation.

## 36. The acceptance test, which is falsifiable and runs before the merge

The claim the whole plan rests on is "this branch's SKILL.md is a superset". Test
it, do not trust section 33:

```
python3 - <<'EOF'
import subprocess, re
R = "/Users/josie/can-it-ford"
def show(ref):
    return subprocess.run(["git","-C",R,"show",
        ref + ":.claude/skills/research-corpus/SKILL.md"],
        capture_output=True, text=True).stdout
theirs, mine = show("claude/add-ci-checks"), show("claude/r9-corpus-bib")
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
mn = norm(mine)
missing = [l for l in theirs.split("\n")
           if len(norm(l).split()) >= 5 and norm(l) not in mn]
print(f"{len(missing)} substantive lines of theirs absent VERBATIM from mine")
for l in missing[:60]: print("   ", l[:100])
EOF
```

A non-zero count is expected and is not a failure: I rewrote that material. The
test is to read the list and confirm every entry is either **(a)** present in
reworded form or **(b)** a claim this branch refuted, listed in section 33.
**Any line that is neither must be carried across before the merge.** As of
2026-08-20 the answer is 13 of 13 themes present and the only unique content was
the hull counts, now carried.

Then, after merging and before pushing:

```
python3 analysis/research_index.py --query "Al-Qadami"      # must be 5, not 0
python3 analysis/research_index.py --identifier-audit       # 272 / 57 / 3
python3 analysis/research_index.py --source-audit; echo $?  # must exit 1
python3 analysis/research_index.py --bib-audit              # exit 0
python3 .claude/checks/count_claims_check.py                # 0 in a full checkout
grep -c "WITHDRAWN QUOTE" .claude/skills/research-corpus/SKILL.md   # must be 1
```

**`--query "Al-Qadami"` returning 5 rather than 0 is the single check that
proves the landing did what it was for.**

## 37. What needs a human, and what I will not decide

- **Whether to land onto `claude/add-ci-checks` at all, or to wait and land both
  onto `origin/main` together.** `origin/main` has none of this tooling, so
  landing on `add-ci-checks` fixes 3 of 36 worktrees now and the rest only when
  they rebase. That is a real improvement and it is not the fix.
- **Whether to rebuild the index as part of the landing.** Part 4 measured what
  a rebuild changes: 332 to 319 papers, cited-anywhere 76 to 66, and a
  reader-facing 43 to 52 that is a measurement change rather than new research.
  `CLAUDE.md` publishes those rungs. **My recommendation is to land the tooling
  WITHOUT rebuilding**, so the code fix and the number change are separately
  reviewable and separately revertable.
- **Whether `data/deep_searches/` gets an un-ignore pair in `.gitignore`.**
  Outside my scope, and every export needs `-f` until it happens.
- **The 11 unexported searches.** Roughly 40 connector calls. `--source-audit`
  exits 1 naming each, so this stays loud.

## 38. One thing this exercise showed that is worth keeping

`d16` measured the merge honestly and reported neither side a superset. That was
correct. Acting on it directly would have meant a hand-built union of two large
files, which is the highest-risk operation available here and the one most likely
to reintroduce a withdrawn claim.

**The cheaper move was to make the measurement false**: find the content that was
genuinely unique, verify it independently rather than copying it, and carry it
across, until the union collapsed to a take-mine. It cost five PLY header reads.

The general form: when two documents conflict, check whether the conflict can be
**dissolved by making one of them complete** before planning how to resolve it.
A merge you no longer have to make cannot go wrong.
