# The corpus is not a superset of the bibliography: it is a sourcing gap, not a
# dropped merge, and the gap is one paper wide rather than eleven

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

**It is a sourcing gap, not a dropped merge.** DERIVED: the DOIs and titles of
the 11 absent works appear nowhere in the **raw text** of any of the eight source
reports. The raw text is upstream of the index, so this is not an artefact of how
the index was built. They were never returned by any search.

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

## 5. `shah2018` is a real sourcing gap, and it is not a random miss

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
neighbourhood, which strengthens rather than weakens the claim that missing it is
a genuine sourcing gap.

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
