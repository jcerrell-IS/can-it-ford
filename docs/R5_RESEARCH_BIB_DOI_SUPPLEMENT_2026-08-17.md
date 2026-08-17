# R5-D1 unit 32: a bibliography year audit, and four verified DOIs it lacks

Date 2026-08-17. Branch `claude/r5-research`. **For whoever owns
`paper/can_it_ford_references_IEEE.bib`. I have not edited it.**

Unit 31 found one wrong year in the bibliography. Unit 13's lesson says finding
one instance is no reason to assume it is the only one, so I audited all of them.

---

## 1. The year audit: the error is isolated

Every entry carrying a DOI, checked against its registering agency (Crossref
first, DataCite fallback):

```
bib entries                      : 21
  with a DOI                     :  9
  without a DOI                  : 12
years matching the agency        :  8 / 9
years MISMATCHED                 :  1 / 9   (ccsa2010yaris, bib 2010 vs DataCite 2016)
unresolved                       :  0
```

**So the year defect is isolated, not systemic.** The one bad entry is the one
unit 31 already found. That is a clean negative and worth recording so nobody
repeats the audit.

I also tested a hypothesis and it was wrong. Unit 29's sweep had reported two DOIs
inside `paper/canonical_2026-08-02/...bib`, which looked like the live bib might
have regressed. It has not: the live bib has **9** DOIs across 21 entries against
the snapshot's **1** across 15. The live file is the better one.

What the snapshot does contain is `note = {doi: 10.1145/3592433}` on the Kerbl
entry, a DOI parked in a free-text note rather than a `doi =` field, which is why
my field-based extractor did not count it. **The live bib dropped it entirely, in
any form.** That is a real gap, just not the regression I hypothesised.

## 2. Four DOIs the bibliography lacks, all verified

Of the 12 entries with no DOI, four are resolvable now. All four verified this
session via `scholar-sidekick auditBibliography`: **4 of 4 matched, high
confidence, none retracted.**

| bib key | DOI or identifier | resolved title | resolved year |
|---|---|---|---|
| `kerbl20233dgs` | `10.1145/3592433` | 3D Gaussian Splatting for Real-Time Radiance Field Rendering | 2023 |
| `xie2023physgaussian` | `10.1109/CVPR52733.2024.00420` | PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics | **2024** |
| `alqadami2022` | `10.1111/jfr3.12828` | A numerical approach to understand the responses of passenger vehicles moving through floodwaters | 2022 |
| `thorpe2026pvwm` | arXiv `2605.30542` | Physically Viable World Models: A Case for Query-Conditioned Embodied AI | 2026 |

Two notes on these.

**`alqadami2022` also fixes a placeholder.** That entry's title is currently the
literal string `{{VERIFY: exact title}}` (unit 7 section 6). The verified title
above resolves it. Its sibling placeholder, `martinezgomariz2018`, still cannot be
resolved: it carries no title, DOI or journal, so its referent is genuinely
ambiguous and I will not guess it. That remains FLAG-4.

**`xie2023physgaussian` has a year consequence, and it is a real decision.** The
entry says `year = {2023}` but the CVPR DOI resolves to **2024**. PhysGaussian was
an arXiv preprint in 2023 and a CVPR paper in 2024, so both years are defensible
depending on which version is cited. **Adding the CVPR DOI without changing the
year would make the entry internally inconsistent.** Either cite the CVPR version
with 2024 and that DOI, or cite the arXiv version with 2023 and the arXiv ID. Pick
one deliberately.

This is the same online-first versus print-issue split that produced the Elicit
CSV's only duplicate, where rows 6 and 16 are one paper at 2016 and 2018 (unit
12). Third time this pattern has bitten in this dispatch, after that duplicate and
`ccsa2010yaris`.

## 3. Consolidated bibliography state

Pulling together what this dispatch has established about that one file, so it is
in one place:

```
entries                                   : 21
  carrying a DOI                          :  9   (8 correct years, 1 wrong)
  no DOI                                  : 12   (4 now resolvable, see above)
  containing a VERIFY marker              :  9   (unit 7)
  with a literal {{VERIFY: exact title}}  :  2   (alqadami2022, martinezgomariz2018)
actually \cited in any .tex               :  3   (unit 7: shah2018,
                                                  smithmodrafelder2019, azhar2023)
```

The three that are actually cited were verified clean in unit 7: authors, titles,
years and DOIs all match Crossref. **The compiled paper's citations are sound.**
Everything above is latent, affecting entries BibTeX does not currently emit.

## 4. Status

I did not edit the bibliography. It is outside my declared scope
(`docs/R5_RESEARCH_*`, `data/r5_citation_*`) and belongs to whoever owns the paper.

UNVERIFIED:
1. Whether `xie2023physgaussian` should cite the CVPR or the arXiv version is an
   editorial decision, not a fact I can settle.
2. The other 8 DOI-less entries (`hsiaokumar2025`, `shand2011`, `videophy2024`,
   `mpmworlds2026`, `nws_tadd`, `genesis2024`, `fred2026`, and
   `martinezgomariz2018`) I did not resolve. Several may legitimately have no DOI:
   `nws_tadd` is a National Weather Service page and `shand2011` is a technical
   report whose PDF is already in `citations/`.
3. `videophy2024`, `mpmworlds2026` and `fred2026` carry `VERIFY AUTHOR LIST` or
   near-placeholder titles. I have not attempted them because a partial title plus
   no author is exactly the input that produces a confident wrong match.
