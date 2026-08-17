# R5-D1: WHAT SURVIVES

Date 2026-08-17. Branch `claude/r5-research`, 50 commits, 31 documents, 7 data files.

**This is the only document you need to read before citing anything I produced.**
The errata index lists corrections; this lists conclusions. If the two disagree,
this file is newer and wins.

**Why it exists:** this dispatch has a high withdrawal rate. Thirty errata, four
outright retractions, and two of my units were largely dismantled by adversarial
review after I published them. The surviving results are good, but they sit beside
superseded ones, and that layer is the main obstacle to using this work.

---

## A. SAFE TO CITE

Each of these was verified by primary source or by measurement, and each survived
adversarial review or was never challenged.

| # | Result | Detail in |
|---|---|---|
| A1 | **The Elicit CSV holds 41 unique papers across 42 rows.** Yields: **10/41** report a depth-velocity threshold, **9/41** a friction coefficient. Always give the denominator | `ELICIT_AND_CATALOG_MINE` |
| A2 | **CORRECTED 2026-08-18, this row was WRONG.** It read "only 3 are actually `\cite`d". True figures: **11 distinct keys** cited in `paper/conference_101719.tex`, **14** in `canonical_2026-08-02/conference_101719_1.tex`, and the **compiled PDF renders 14 references with 51 inline citations**. The "3" belonged to erratum 4, which was scoped to the **8 catalogued DOIs**; I dropped the qualifier when consolidating. See §A2a | `MPM_FOUNDATIONS_UNCITED` §A2a |
| A3 | **Catalog recall is roughly 50%**, measured three independent ways. This is the dispatch's most robust quantitative finding | `ELICIT_AND_CATALOG_MINE`, `CENSUS_ATTEMPT` |
| A4 | **The citation-graph fixpoint is NOT achievable.** Topic-bounded traversal from 32 seeds grew 32 -> 92 -> 174 and touched 3,575 works by hop 2. Independently re-confirmed 2026-08-17: mean branching **82.2**, hop-3 upper bound **3.3M** nodes. **Any count from this literature is a floor, and that is now measured rather than assumed** | `CENSUS_ATTEMPT`, section D below |
| A5 | **Scale reporting needs two labels, not one.** "State the model scale" is insufficient; a `value_basis` label is required or model-scale values get read as full-scale. Row 7 is **1:24**, and its threshold is **~118x** below the others under Froude | `THRESHOLD_TABLE`, erratum 2, 14 |
| A6 | **Four bibliography DOIs verified and supplied**, plus one year error (`ccsa2010yaris`, bib 2010 vs DataCite 2016). The year audit found the error **isolated**, 8 of 9 correct | `BIB_DOI_SUPPLEMENT` |
| A7 | **All four shipped NCAC/CCSA packages are TRACKED in the public repo**, all four carry an acknowledgement request and a liability disclaimer, **none carries any licence word**. **E8 is now CLEARED** (D2, `a386704`, permission granted) and this finding is *not* superseded: it is part of the evidence chain, because "no licence exists to confirm" is what made permission the necessary route. **The FHWA acknowledgement SURVIVES the clearance and is still unmet**, re-verified 2026-08-18: `FHWA` and `Federal Highway` appear in **0** `.tex` files while `CCSA` appears in 3. Acknowledgement is a separate obligation from redistribution rights | `NCAC_README_TERMS`, §A7a |
| A8 | **DOI `10.1111/jfr3.12262` is confirmed** for the Martinez-Gomariz state-of-the-art review (title match score 1; Crossref `issued` 2016-08-03, `published-print` 2018-02). **The `martinezgomariz2018` bib REFERENT is NOT settled**: a rival 2017 paper fits the entry's `note` equally well. See B-list | `SEALING_AND_FLAG4` §3 |
| A9 | **The experimental literature does not agree on vehicle sealing.** Across twelve studies: water-filled, foam-filled watertight, ingress-permitted and solid-rigid all appear, and two of the "sealed" entries are not physical experiments. **Sealing is NOT the cause of any headline disagreement** (see B-list) | `SEALING_AND_FLAG4` §1, §1a |
| A10 | **Hull geometry, measured directly:** volume **3.5427387900160743 m3**, watertight, `body_count` 1, euler -442 so **genus 222**. `1100/3.542739 = 310.4942`, reproducing CLAUDE.md's canonical 310.494 | `FLOODFILL_MEASURED` |
| A11 | **The audit's flood-fill volumes are not reproducible as values.** 4.5628 does not reproduce; the comparable quantity is the **sealed cavity**, where two implementations disagree **2.1x** (1.020 vs 2.161 m3); the operation is **bistable and grid-phase fragile** near 22.2 mm | `FLOODFILL_MEASURED` |
| A12 | **L-2 stands as written.** I proposed amending it and then **refuted my own amendment** from the AR&R primary source: the 3.0 m/s cap exists for human stability and occupant egress, so it is administrative, not vehicle-derived | `PROPOSED_AMENDMENTS`, erratum 3 |

### A7a. E8 is CLEARED, and exactly one item of mine survives it

**Verified 2026-08-18 by reading D2's commit `a386704`, not by trusting the board.**
Josie granted permission; it applies globally and permits republication. D2's
reasoning turns on the rule clearing on **"written permission OR a confirmed
licence"** and on this dispatch having established across three independent sources
that no licence exists to confirm, leaving permission as the other route.

**That is the two-route clause I had truncated.** Unit 43 found and fixed it, D2
picked it up in `141d239`, and it is the pivot of the clearance argument. Worth
recording as the one case where an error of mine, once corrected, changed a
sibling's reasoning rather than only my own.

**What is now settled and must not be re-litigated:** the archives, both derived
hulls, the six renders and the AR&R report are cleared. Every remediation option is
**withdrawn**, not pending. Nothing is to be removed, untracked or history-rewritten
on E8 grounds.

**What survives, and it is easy to lose:** **the FHWA acknowledgement is still
unmet.** Re-measured today, `FHWA` and `Federal Highway` appear in **0** `.tex`
files, while the control string `CCSA` appears in **3**. The README asks for both,
verbatim at line 16: "We ask that the CCSA at GMU and the FHWA be acknowledged for
any use of this FE model resulting in papers and publications."

**Permission to redistribute is not acknowledgement.** They are different
obligations from different sentences, and clearing the first does nothing to the
second. The risk here is that "E8 cleared" reads as "the geometry paperwork is
done" and a one-word fix gets dropped at the finish line.

*(Carries FLAG-6: the `.tex` counts are for local copies only; the live Overleaf
head is unreachable, so the paper may already say FHWA and I could not see it.)*

## B. RETIRED. Do not cite these, including from my own earlier documents

Every one of these appears somewhere in my committed work as a positive claim.

| Retired claim | Correct position |
|---|---|
| "42 unique papers"; yields /42 | **41 unique**; yields **/41** |
| "8 catalogued DOIs are cited in the paper" | **3** are `\cite`d |
| "85 simulations, catalog recall 27.1%" | **WITHDRAWN**, contaminated with aircraft, water-exit and deep-sea papers |
| "137 catalog-absent DOIs, 101 uncited" | **109** and **88** |
| "strict class: 15 found, 8 missed" | **14** and **7** |
| "jfr3.12885 appears in 27 files" | **25** by the stated method |
| "row 7 is roughly twenty times below the others" | **~118x** under Froude, and it is **1:24**, not 1:10 |
| "model-scale thresholds are non-conservative" (unqualified) | **mode-dependent**: true for sliding, false for floating |
| "we already cite Al-Qadami 2023" | **WITHDRAWN**; it is a `note` on a `{{VERIFY}}` stub |
| "three novelty axes survive" | **two**: MPM-vs-SPH and geometry provenance |
| "the FORD/NO-FORD evidentiary asymmetry" | **RETIRED**; both readable references failed to support it |
| "the draft resolution claim, 3.8x better resolved" | **NOT CLEAN**, 6 blocking issues; rewritten to cell size only |
| "`10.26190/unsworks/27433` is dated 2024" | **2017**; DataCite is the registering agency, not OpenAlex |
| "g64_m1100 fails P-2, a leakage defect" | **not leakage**; P-2 counts water in the axis-aligned bbox |
| "P-2's null baseline is 10.3 to 11.0%" | **11.30 to 14.90%**, so the null exceeds the 0.10 gate in 17 of 17 |
| The **hull-density escalation** (unit 34/35) | **RETRACTED**, 5 of 8 claims wrong. Only genus 222 survives |
| The **flood-fill interpretation** (unit 39 draft) | **FOUR WITHDRAWN**: the ~6.8 agreement, the "35%" step, the cabin/window mechanism, and "density falls 11-52%" |
| "Nihei brake state bears on our 16 SLIDE verdicts" | **direction wrong**; lower friction increases sliding, so SLIDEs get more room |
| "vehicle sealing is the recorded cause of the largest disagreement in the incipient-motion literature" (unit 40 draft) | **WITHDRAWN.** The source names **incorrect density/mass scaling**; Shu's D×V shift is attributed to **friction** (mu 0.39-0.68 vs 0.3); foam-filling is one of two components of the fix. "Largest" was my own superlative and appears nowhere in the source. **I truncated the quote one clause short** |
| "our pipeline picks the fill on one line, and no gate or document records why" (unit 40 draft) | **WITHDRAWN, three ways.** `vehicle.py:175` is **automatic dispatch** on `is_watertight`, not a knob; the canonical hull is watertight so `solidify_columns` is **unreachable**; the reason is recorded at `vehicle.py:93-94` ("buoyancy is unbiased"); and `sim_standing.py:381-383` would **abort** at fill_ratio 2.16518 |
| "the Elicit CSV independently and decisively confirms the FLAG-4 referent" | **DOWNGRADED to consistent.** Its 2018 stamp is the same publisher metadata Crossref serves, so it is one source cited twice; and the **rival candidate sits in the same CSV at row 31** |

## C. UNVERIFIED, and why

1. **I have read none of the twelve primary flood-stability studies.** A9 is a
   transcription of one corpus document's table, not my reading of Xia or Shu.
2. **The corpus is only partly readable.** `corpus_inventory` reports the main root
   **TCC-denied in part, 308 of 387 files**. **79 files, 20.4%, are invisible to
   every search in this dispatch.** No absence claim from corpus search is complete.
3. **`solidify_watertight` n=8890 is inherited, not mine**, and disagrees with the
   inventory's 8905 (register E3) by -0.168%. The reviewer who produced it could
   not close the gap.
4. **The shell correction `filled - 0.5*surf`** behind A11's 2.161 is a first-order
   heuristic, validated on an icosphere and on the open branch only.
5. **Five Elicit rows carry no DOI** and were not resolved.
6. **Three full texts remain closed-access** (He 2026, Zhang 2023, Lyu 2023) and the
   **Nihei corrigendum** needs one browser-minute; it is gold OA but bot-filtered.

## D. The judgement call, recorded

The coordinator offered a fixpoint citation traversal or this consolidation, and
asked for a reason rather than momentum. **I chose consolidation, because option
one is not untried: it was run in unit 5 and recorded as not achievable in erratum
9.** The coordinator's framing that I "ran only ONE HOP of it" is not what happened;
unit 5 ran a topic-bounded bidirectional traversal for two complete rounds and I
stopped a third in progress. Read directly from that run log:

```
round 1:  expanded 32   nodes 1092   vehicle+water 124   next frontier  92
round 2:  expanded 124  nodes 3575   vehicle+water 298   next frontier 174
round 3:  stopped by me, in progress
```

**The frontier grew at every round with the topic filter already applied.** I
re-measured from the raw-graph side on 2026-08-17 as an independent check: mean
out-degree 35.2, in-degree 47.0, **branching 82.2**, giving hop-1 493, hop-2 40,508
and hop-3 **3,328,421** nodes.

Two independent measurements, one filtered and one raw, agree it does not converge.
And the filtered variant cannot deliver the property that made it attractive: a
relevance test applied at every node is not a closed operation, so its recall is
exactly as unmeasurable as the keyword catalogs it was meant to replace.

**What that buys, and it is not nothing:** "N fording simulations exist and N is a
floor" is now a **measured** limitation with a growth curve behind it, rather than
an assumption. That is a citable statement about the literature's structure.

## E. Handed off, not mine to close

- **D4**: the P-2 null baseline of 11.30-14.90%; the MPM boundary-condition cluster.
  **NOT the sealing axis**: I withdrew that handoff. `vehicle.py:175` is automatic
  dispatch, `solidify_columns` is unreachable for a watertight hull and would abort
  the preflight guard, and the reason is already recorded at `vehicle.py:93-94`.
  What is left for the paper is one limitations sentence: the hull is deliberately
  built underbody-open, and no gate tests that against an external measurement.
- **D2 / E8**: the NCAC README terms and the DataCite rights evidence.
- **Paper owner**: the FHWA acknowledgement one-word fix; four verified DOIs; the
  `xie2023physgaussian` 2023-vs-2024 decision.
