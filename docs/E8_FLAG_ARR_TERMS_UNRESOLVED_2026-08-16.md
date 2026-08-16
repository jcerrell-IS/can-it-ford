# FLAG: AR&R / WRL redistribution terms unresolved

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
Named flag file per the dispatch protocol: blocked after two genuinely different
approaches, recorded here, work continued on the rest of scope.

## What is blocked

The redistribution terms for **5 tracked, public files** on `origin/main`:

| File | Bytes |
|---|---|
| `citations/ARR_Project_10_Stage2_Report_Final.pdf` | 1,115,134 |
| `citations/WRL reports technical and Research/Figure 5-5 Combined flood hazard curves.png` | 543,750 |
| `citations/WRL reports technical and Research/Table 5-1 ... vulnerability thresholds.png` | 119,139 |
| `citations/WRL reports technical and Research/Table 5-2 ... classification limits.png` | 97,202 |
| `citations/ARR table 1 - guidelines and recommendations for limits for vehicle stability.png` | 237,832 |

Source: Shand, T. D., Cox, R. J., Blacka, M. J., & Smith, G. P. (2011). *Australian
Rainfall and Runoff Project 10: Appropriate Safety Criteria for Vehicles, Literature
Review, Stage 2.* AR&R Report No. P10/S2/020, Water Research Laboratory, UNSW.
[read, `citations/README.md`]

Unlike the other two PDFs in `citations/`, this is a **technical report, not a journal
article**, so it has no DOI and the scite lookup that resolved the other two does not
apply to it.

## Approaches tried, both failed

1. `WebFetch https://arr.ga.gov.au/arr-guideline/copyright` -> **HTTP 403 Forbidden.**
   Consistent with project memory, which already records `arr.ga.gov.au` as returning
   403 and notes that the mirror search engines surface is the **people** report, not
   the vehicles one. **[recalled, and reproduced live today]**
2. `WebFetch https://www.unsw.edu.au/research/wrl/our-research/technical-reports`
   -> **HTTP 404 Not Found.** Different host, different organisation, genuinely
   independent of attempt 1 rather than a retry of it.

## Why this is not just "try harder"

Both failures are at the **transport** layer, not the reasoning layer, so no amount of
re-reading what is already on disk resolves it. The terms are not in the repo: the
PDF's own text is not reachable by the tooling available here, because a `strings`
control showed **0 URLs and 0 markers extractable from this PDF**, against 413 and 199
for the two Wiley files. The AR&R PDF's text is compressed and unreadable to the
probe. That control is the one part of my withdrawn `strings` probe that still stands,
because it is a statement about the probe's reach rather than about a licence.

## Next approaches, for whoever picks this up

Ordered cheapest first. None has been attempted.

1. **Find the correct current URL.** AR&R guideline hosting moved to
   `arr.ga.gov.au`; the copyright path guessed above may simply be wrong. Try the
   book landing page rather than a `/copyright` path.
2. **Ask a tool that can read the PDF.** A PDF text extractor (`pdftotext`,
   `pypdf`) run locally would read the front matter, which for a government-programme
   report normally carries the copyright and reuse statement on page 2 or 3. **No PDF
   text extractor was available in this environment; that is the cheapest single fix.**
3. **`corpus_search` / `corpus_resolve`** across the research roots: another copy of
   this report, or a summary of its terms, may already be on disk.
4. **Commonwealth of Australia default.** AR&R is a national guideline programme;
   Commonwealth material is frequently **CC BY 4.0** by default policy. If confirmed,
   all 5 files are fine with attribution. **Do not assume this**, it is a hypothesis
   with a plausible mechanism, not a finding.
5. **Ask the authors.** WRL/UNSW contacts are reachable and the report is 15 years
   old.

## Working assumption until resolved

**Leave all 5 files in place.** Deleting on an unread licence is exactly as
unevidenced as keeping on one, and the AR&R PDF in particular is load-bearing research
evidence (see section 5 of `E8_CITATIONS_REDISTRIBUTION_AUDIT_2026-08-16.md`): it was
used tonight as a primary source, and project memory records a prior audit wrongly
calling its ISBN and Table 3 unverified and having them deleted. That is a documented
precedent for removing this specific file on a bad call.

This assumption is **labelled and reversible**, which is the point of writing it down
rather than stopping.
