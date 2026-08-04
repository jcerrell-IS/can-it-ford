---
name: xia-2014-not-2013-citation-trap
description: "Xia/Falconer/Xiao/Wang is FOUR authors and cites as 2014 (print), not three authors and 2013; a confident 'it's 2013 NOT 2014' instruction was wrong and would have broken the bib"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 84ba0bac-f92c-4dda-b2c6-ffcb8557bed0
  modified: 2026-07-31T00:43:49.023Z
---

Crossref `10.1007/s11069-013-0889-2`, verified live 2026-07-30:

- Title: "Criterion of vehicle stability in floodwaters based on theoretical and
  experimental studies"
- Authors: **four**, Junqiang Xia, Roger A. Falconer, Xuanwei Xiao, **and Yejiang
  Wang**
- Natural Hazards, vol **70**, issue **2**, pp **1619-1630**
- `published-online` 2013-10-11, `published-print` **2014, January**

Cite as **2014** with **all four authors**. The volume/issue carried in the entry
is the 2014 print issue, so 2014 is the internally consistent year.

On 2026-07-30 a briefing instructed, in bold, "note: 2013, NOT 2014" and listed
only three authors, omitting Yejiang Wang. Both were wrong. Two independent panes
had already written `xia2014` with four authors, correctly, and following the
instruction would have introduced an error into a paper due the next day.

Adjacent trap on the companion citation: the local PDF is **Syed MUZZAMIL Hussain
Shah** (`10.1051/matecconf/201820307003`, MATEC Web Conf 203:07003, 2018,
"Instability Criteria for Vehicles in Motion Exposed to Flood Risks", with
Mustaffa, Kim, Yusof). A different **Syed HAMID Hussain Shah** authored adjacent
2018/2019 flood-vehicle papers. Different people, near-identical name strings,
same subfield.

**Why:** an assertive correction from a summary or a briefing is not evidence. The
"online-first year vs print year" split is exactly the kind of detail that makes a
confident wrong correction sound authoritative, and both DOIs here resolve fine,
so the fabrication-by-resolvable-DOI check would not catch it either.

**How to apply:** resolve the DOI at `api.crossref.org/works/{DOI}` and read
`author`, `volume`, `issue`, `published-print` and `published-online` before
changing any year or author list, including when the change is requested
confidently and in bold. Prefer `published-print` for the year when a volume and
issue are being cited. Related: [[overleaf-tex-is-canonical]].
