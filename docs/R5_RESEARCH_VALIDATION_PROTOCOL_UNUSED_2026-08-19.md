# R5-D1 unit 56: a paper-ready validation protocol was commissioned for this project and never used

Date 2026-08-19. Branch `claude/r5-research`.
**For the paper. This is the strongest form of the unit 54 finding.**

Unit 54 established that 86% of the catalogued validation literature is uncited while
CLAUDE.md's L-7 names validation as the project's novelty. Following that into the
corpus found something more specific: **the validation plan already exists, written
for this exact project, and nothing from it reached the paper.**

---

## 1. The document

`04_Validation_Literature_and_Citations/Physics_Simulation_Validation_Protocol.md`,
550 lines, an Undermind deep search dated **2026-07-15**, **81 papers**, estimated
coverage 61%. Its stated research goal is this project, not a generic one:

> "Develop an actionable validation protocol for a research pipeline that
> reconstructs a real flooded road with 3D Gaussian Splatting, simulates
> vehicle-water interaction with the Material Point Method, and produces a graded
> FORD / NO-FORD decision by comparing six-degree-of-freedom vehicle outcomes with
> civil-engineering flood hazard thresholds. **The protocol must be achievable with
> an existing 36-run parameter sweep** ... it should not assume new physical
> experiments, new field-sensor deployment, or a multi-year certification program."

It was commissioned to be usable with the sweep the project already had, and it
delivers a four-layer evidence chain: component verification, calibration versus
validation, numerical and parametric uncertainty, and held-out stress testing. Its
governing sentence:

> "**Decision credibility, not numerical agreement, is the governing endpoint**: a
> FORD claim requires validated six-DOF outcomes and a conservative margin to the
> hazard threshold, whereas a NO-FORD claim may be issued whenever uncertainty spans
> or exceeds that boundary."

## 2. None of it reached the paper

Measured on the compiled PDF (`public_release/Cerrell_CanItFord_paper.pdf`,
2026-08-04, 7 pages, 41,649 characters extracted).

**Controls first, and they are strong**, so the zeros below are real absences and
not a broken probe:

```
grid 32   resolution 18   NO-FORD 12   particle 14   Warp 5   MPM 19   g64 1
```

**Every element of the protocol's vocabulary:**

```
V&V 0        V&V 20 0      UL 4600 0      SOTIF 0       ISO 21448 0
GCI 0        Richardson 0  observed order 0             Grid Convergence 0
Oberkampf 0  Roache 0      Celik 0
epistemic 0  aleatory 0    held-out 0     safety case 0
convergence 0              uncertainty 0
```

**The paper discusses `grid` 32 times and `resolution` 18 times, and never once uses
the word `convergence` or the word `uncertainty`.**

The protocol document itself is named in **1** repo file.

## 3. What this does and does not establish

**It does establish** that the project commissioned a paper-ready validation plan
matched to its own sweep, that the plan sits in the corpus unused, and that the
paper contains none of the standard verification-and-validation apparatus the plan
prescribes: no convergence reporting, no uncertainty interval, no observed order or
GCI, no evidence-tiering vocabulary.

**A fair counterweight, and it is a real one.** Register item 5 records that the
project's three-grid study (g48/g64/g96) is **non-monotone and unconverged**, and
that the displacement magnitude moves by tens of percent between grids while the
binary verdict does not. **Declining to write "convergence" about an unconverged
study is honest, not negligent.** The register also already tells people to cite the
verdict and never the displacement magnitude.

**But that is precisely the case the protocol addresses.** Its numerical-uncertainty
layer asks for observed order, Richardson/GCI intervals and separated
aleatory/epistemic uncertainty *so that* an unconverged result can still be reported
credibly with a bound, rather than by omission. Silence and a reported interval are
different things, and only one of them survives review.

**Not established:** that any specific recommendation is right for this paper, or
that the 81 papers should be cited. I have read the protocol's summary and catalog
head, not its 550 lines, and I am not the paper's author.

## 4. The overlap with unit 54 is not a coincidence

Papers in this protocol's own catalog that unit 54 independently found uncited:

| catalog # | paper | status |
|---:|---|---|
| 11 | Material point method after 25 years | uncited |
| 19 | Numerical simulations of dam-break floods with MPM | uncited |
| 20 | Mixed MPM formulation, stabilization, **and validation** | uncited |
| 21 | Benchmarking MPM for free-surface/elastic-structure interaction | uncited |
| 5 | He 2026, **Predicting vehicle-water interaction ... and experimental validation** | zero `.tex` |

Also in its catalog and uncited: Roy and Oberkampf 2011, Oberkampf 2004,
Eca/Dowding/Roache on V&V 20, Stern 2001, Celik 2007, Roache 1994. **These are the
canonical V&V references**, and they were retrieved for this project a month ago.

## 5. Status

UNVERIFIED:
1. **Carries FLAG-6.** The paper measurements are on the 2026-08-04 compiled PDF.
   The live Overleaf head is unreachable and the token file is still 0 bytes, so the
   current paper may differ.
2. **I read the protocol's goal, summary and the first 23 catalog entries**, not all
   550 lines or all 81 papers.
3. Whether the paper *should* adopt V&V 20 or UL 4600 vocabulary is an editorial and
   scientific judgement, not a fact I establish. The protocol itself says to treat
   them as "structural constraints and vocabulary, not as certification targets".
4. `params_check.py` already runs a `lit:resolution_convergence_gci` gate per
   CLAUDE.md, so **GCI is present in the repo's tooling even though the word is
   absent from the paper**. The gap is in the write-up, not necessarily in the work.
5. Word-frequency absence is not proof a concept is missing; a paper can report an
   uncertainty without using the word. I checked sixteen distinct terms plus five
   canonical author names to reduce that risk, but it remains a lexical test.
