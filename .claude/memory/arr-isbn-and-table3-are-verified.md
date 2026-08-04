---
name: arr-isbn-and-table3-are-verified
description: "The Shand 2011 ISBN and \"Table 3, page 14\" are primary-source verified locally; do not delete them as \"unverified specifics\""
metadata: 
  node_type: memory
  type: project
  originSessionId: ed992ba1-6df5-488b-93fe-9788ba57137c
  modified: 2026-07-31T21:21:54.926Z
---

An external audit (July 31, 2026) recommended deleting ISBN 978-0-85825-948-5 from the
`shand2011arr` bib entry and stripping "Table 3, page 14" from the Fig. 3 source line, on
the grounds that both were unverified specifics. Both recommendations were wrong, and both
were acted on before being checked.

Verified live against `citations/ARR_Project_10_Stage2_Report_Final.pdf`, which is in the
repo:
- Metadata page prints, on its own lines: `AR&R Report Number P10/S2/020`, `Date 21
  February 2011`, `ISBN 978-0-85825-948-5`, `Contractor Water Research Laboratory`, authors
  `T D Shand / R J Cox / M J Blacka / G P Smith`.
- PDF page 24 carries the printed page-14 marker and the `Table 3` label, surrounded by the
  draft-interim criteria text. So "Table 3, page 14" is correct as printed.

**Why:** the audit could not reach the primary source over the network and treated
"I cannot confirm this" as "this is unconfirmed." The PDF was local the whole time. Deleting
a verified specific is a real loss, not a conservative choice.

**How to apply:** before removing any citation detail as unverified, check `citations/` for
the primary PDF and grep it. In BibTeX write `{ISBN}` braced, because IEEEtran lowercases
the first letter of `note` and renders a bare `ISBN` as `iSBN`.

Related: [[xia-2014-not-2013-citation-trap]], [[overleaf-tex-is-canonical]]
