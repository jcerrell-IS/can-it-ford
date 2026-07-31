---
name: l0l1-divergence-pdf-not-a-7th-figure
description: "L0_L1_divergence_corrected.pdf verified correct on 2026-07-30 but deliberately NOT added to the paper, its content is already inside fig:l0l1's right panel"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5e98f138-df3e-4c0d-ab06-2315b13b24e3
  modified: 2026-07-30T20:46:19.089Z
---

`~/Downloads/L0_L1_divergence_corrected.pdf` was verified on 2026-07-30 against
live `data/scenario_sweep.csv`. All eight of its claims recompute exactly: both
agree FORD 7, both agree NO-FORD 56, L0-stop/L1-go 7, L0-go/L1-stop 0, sum 70,
bare-to-joint 37 to 14, 23 reclassify FORD to NO-FORD, 0 reclassify the other
direction. Its 14 FORD cells match the Small Car joint rule (depth <= 0.30 m AND
D x V <= 0.30 m2/s) exactly, and the 0.30 m dashed cap line is correctly placed.

Josie decided on 2026-07-30 that it does NOT get added as a seventh figure.
The verification stands; the disposition is settled.

**Why:** its content is already inside the right panel of `fig:l0l1`
(`figures_review/l0l1_two_rules_v2.pdf`), which labels the same three regions
(both permit, L1 permits/L0 refuses, both refuse), already states "L0 permits and
L1 refuses never occurs in this dataset", and already reports total L1 permits
14 of 70. Adding it would duplicate, not add. Secondary reason: `pdfinfo` shows
Creator HeadlessChrome on Linux x86_64 and Producer Skia/PDF, so it is a browser
print-to-PDF with no generator in the repo and no provenance, unlike the figures
built through `analysis/svg_to_paper_pdf.py`.

**How to apply:** if this PDF resurfaces, do not re-verify it and do not reopen
whether it belongs in the paper. Cite this decision and move on. If someone wants
the L0-vs-L1 agreement breakdown called out more explicitly, the fix is to adjust
the existing `fig:l0l1` right panel or its caption, not to add a figure. See
[[overleaf-tex-is-canonical]] for which file any such edit must land in, and
[[l1-l2-divergence-is-class-dependent]] for the separate L1-vs-L2 question.
