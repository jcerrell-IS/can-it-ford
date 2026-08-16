# FLAG: AR&R / WRL redistribution terms

**STATUS 2026-08-16: UNBLOCKED on the third approach.** The filename is retained
because other documents cite it; the flag is no longer open in the form it was
written. Dispatch R5-D2, branch `claude/r5-exposure`.

## Result

**The AR&R Project 10 Stage 2 report contains no copyright statement, no licence, and
no reuse or permission terms in its extractable text layer.** It is **licence-silent**,
the same category as the CCSA decks, and **not** Creative Commons. [read]

Term counts over the extracted text, case-insensitive:

| Term | Count |
|---|---|
| `copyright` | **0** |
| `licence` / `license` | **0** / **0** |
| `creative commons` | **0** |
| `all rights reserved` | **0** |
| `reproduc*` | **0** |
| `permission` | **0** |
| `Commonwealth` | **0** |

This **refutes hypothesis 4** of the earlier revision of this file, which reasoned that
AR&R is a national guideline programme and that Commonwealth material is frequently
CC BY 4.0 by default. There is no Creative Commons text anywhere in the report, and
the word `Commonwealth` does not appear at all. The plausible mechanism was not the
actual one.

## Facts recovered, which are useful beyond the licence question

Read directly from the report's own front matter: [read]

- **Publisher: Engineers Australia**, Engineering House, 11 National Circuit, Barton
  ACT 2600. **Contact: `arr@engineersaustralia.org.au`.** Not Geoscience Australia,
  which is where the failed web attempts pointed.
- **ISBN 978-0-85825-948-5.** This **independently confirms** the project-memory item
  recording that this PDF prints a verified ISBN, which a prior audit had wrongly
  called unverified. **[the memory was recalled; the ISBN is now read directly]**
- Report number **P10/S2/020**, dated **21 February 2011**.
- **Contractor: Water Research Laboratory, UNSW**, reference 10023.01.
- Authors: **T D Shand, R J Cox, M J Blacka, G P Smith.**
- Funding: "the Federal Government through the Department of Climate Change".

**Note the rights structure is the same shape as the CCSA case:** a government-funded
project, delivered by a **contractor** (WRL/UNSW), published by a third body
(Engineers Australia). Contractor-authored work is not automatically public domain,
which is the same reasoning register E8 applies to GMU/FHWA. Funding is not a grant.

## Method, and why its negative is trustworthy this time

The third approach, after a 403 and a 404, was to **write a PDF text extractor** using
python3's built-in `zlib`: pull every `stream ... endstream` block, `zlib.decompress`
each, and recover the show-text operands.

**It failed on the first attempt, and a control caught it.** The initial run reported
1,371,648 characters but scored **0** for `Rainfall`, `vehicle` and `stability`. The
cause: this PDF fragments text across thousands of tiny strings,
`(Austr)(ali)(a)(n )(Rainf)(all)`, and I had joined them **with a space**, which
destroys every word. Joining with the empty string fixed it.

**Control after the fix**, against words that must be present in a report with this
title:

| Probe word | Count |
|---|---|
| `vehicle` | 142 |
| `stability` | 83 |
| `Rainfall` | 15 |
| `Runoff` | 15 |
| `Shand` | 7 |
| `Water Research Laboratory` | 5 |
| `ISBN` | 1 |

**This is L-A from `E8_METHOD_LESSONS_2026-08-16.md` applied correctly, and it is the
reason this negative can be trusted where the earlier `strings` negative could not.**
The probe was validated against known positives *before* its negative was believed. It
also caught a real bug rather than rubber-stamping the method.

**One caveat, checked rather than assumed:** the 30 apparent `©` symbols in the
extracted text are **binary noise from inline image data** (`BI ... ID <compressed
bytes> EI`) decoded as latin-1, not copyright marks. Verified by printing their
context.

## The one real limitation

**The probe reads the text layer only.** This PDF has **83 streams with no text
operators and 10 `/DCTDecode` (JPEG) objects**. A copyright notice printed on a
**scanned or image-only page**, such as an inside cover, would be invisible to it.

So the correct statement is **"no copyright statement appears in the extractable text
layer"**, not "the report contains no copyright statement". To close that gap, open
the PDF in a viewer and look at the first three pages by eye. That is a ten-second
human check and it is the only remaining step.

## Recommendation

1. **Eyeball pages 1 to 3** in a PDF viewer to rule out an image-only rights page.
2. **Treat as licence-silent** until then, which means the same operative rule as the
   CCSA geometry: it may not be redistributed on the public repo without permission,
   and it should not be deleted either, because the terms are unread rather than
   adverse.
3. **There is now a named contact for asking**: `arr@engineersaustralia.org.au`,
   published in the report itself. That is the same remedy recommended for CCSA, and
   the two requests could reasonably go out the same day.
4. Keep the file locally regardless. It is load-bearing research evidence: D1 used it
   tonight as a primary source, and it is the sole source for the L1 depth-velocity
   threshold.
