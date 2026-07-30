---
name: arr-primary-source-access
description: "How to cite the AR&R vehicle stability criteria, including the mirror that is the WRONG report"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5215ed93-edb4-438b-896d-8a1bc755df49
  modified: 2026-07-26T10:48:07.640Z
---

The Shand, Cox, Blacka & Smith (2011) vehicles report P10/S2/020 is NOT programmatically
downloadable. `arr.ga.gov.au` returns 403 to every automated request, including with a browser
user agent. It may work in a real browser.

**The trap:** `https://www.arr-software.org/pdfs/ARR_Project10_Stage1_report_Final.pdf`
resolves with HTTP 200 and search engines present it as the vehicles report. It is
**P10/S1/006, "Appropriate Safety Criteria for PEOPLE", April 2010**. A different report. Do
not cite it as the vehicles report.

**Two reproductions that ARE fetchable and reproduce Table 3 with correct attribution:**
- Smith, Davey & Cox, WRL Technical Report 2014/07, Table 4-2:
  `https://www.unsw.edu.au/content/dam/pdfs/engineering/civil-environmental/water-research-laboratory/publications/WRL-TR2014-07-Flood-hazard.pdf`
- AIDR Guideline 7-3 Flood Hazard, Figure 9:
  `https://knowledge.aidr.org.au/media/3518/adr-guideline-7-3.pdf`

Cite the primary AND a reproduction. Citing only the reproduction is a downgrade.

**Load-bearing quote, WRL TR2014/07 p.20, verified by extracting the PDF text 2026-07-26:**
"Shand et al. (2011) highlighted that the available scaled experimental data is being applied
beyond its limits to develop these draft criteria, and that the criteria are unlikely reliable
enough to be adopted permanently as safety criteria. This is due to the data not allowing
adequate assessment of: Appropriate coefficients of friction for use in flood flows; Buoyancy
in modern cars; The effect of vehicle orientation to flow direction (including vehicle
movement)."

That is the criterion's own authors naming the gaps this project's MPM work addresses. It
belongs in the motivation section quoted, not paraphrased. See also
[[l1-l2-divergence-is-class-dependent]] and `docs/VERIFIED_FACTS_LEDGER_july24.md` Section A1,
which already carries Table 3 verbatim from the primary PDF at `citations/`.
