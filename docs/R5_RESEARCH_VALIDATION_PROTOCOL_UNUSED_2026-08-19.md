# R5-D1 unit 56: the validation literature is uncited in the compiled paper

Date 2026-08-19. Branch `claude/r5-research`.

> ## HEAVILY CORRECTED after physics-skeptic returned FOUR BLOCKING issues
>
> **The lexical zeros survive and now have a positive control. Most of what I built
> on them does not.** The worst error inverts the argument: I criticised the project
> for declining to report a GCI bound, and **a GCI bound cannot be computed on this
> data, which the project had already written down.** On that point they are right
> and I was wrong. Section 5 lists every withdrawal.
>
> **The root error is one I have now made repeatedly: I measured ONE artifact and
> generalised to "the work".** There is a second, longer paper at
> `deliverables/paper/overleaf/` whose `limitations.tex`, `results.tex` and
> `future_work.tex` address precisely what I said was absent. I never looked.

---

## 1. What survives, and it is worth keeping

**In the compiled 7-page PDF** (`public_release/Cerrell_CanItFord_paper.pdf`,
pdfTeX CreationDate 2026-08-01, file mtime 2026-08-04), every one of these returns
**zero**:

```
V&V   V&V 20   UL 4600   SOTIF   ISO 21448
GCI   Richardson   "observed order"   "Grid Convergence"
Oberkampf   Roache   Celik
epistemic   aleatory   "held-out"   "safety case"
```

**The zeros now have a positive control I did not build and should have.** The
reviewer found that `pdftotext` shreds IEEE small-caps captions letter by letter
(`V EHICLE C LASS D ENSITY AT N _ G R I D =64`), which would manufacture false
zeros. A whitespace-stripped probe recovers exactly the hits an ordinary search
loses (`grid` 38 despaced vs 36 flat), and **with that control passing, all sixteen
terms above still return zero** under case-sensitive, case-insensitive and despaced
probes.

**And none of the protocol's 81 catalogued papers is cited in the compiled paper.**
Its reference list is 16 items; none is a V&V reference.

**Correction to my own control numbers:** I reported them as occurrence counts; they
are `grep -ci` **line** counts. `grid` is 36 occurrences on 32 lines, `MPM` is 21 on
19. The zeros are unaffected, since zero lines implies zero occurrences.

## 2. The document is a bibliography, not a protocol

`Physics_Simulation_Validation_Protocol.md` is 550 lines with three sections: a
Summary of Results that is one sentence and four bullets (lines 13-20), an 81-row
catalog, and abstracts. **The word "protocol" appears twice in 550 lines, both on
line 7, inside the commissioning prompt.**

**I quoted the commissioning prompt as though it were the deliverable.** "The
protocol must be achievable with an existing 36-run parameter sweep" and "the
desired result is a concrete, paper-ready validation plan" are what the project
*asked Undermind for*, not what came back. Calling the result "paper-ready" was
quoting the requisition and grading the delivery against it.

Caveats I omitted: coverage is **61%**, so roughly 39% of relevant literature was
not found; the file says "Showing top 50 of 81", so **31 entries have no abstract**;
and two same-size divergent copies exist (July 15 and July 20).

## 3. WITHDRAWN: "built to be usable with what the project already had"

The protocol's 36-run sweep is `data/track1_sweep_v2/` (verified: 36 rows, 3 classes
x 4 depths x 3 velocities, masses 1390/1990/2300). **CLAUDE.md lists that sweep under
DEPRECATED, do not read or cite**: a box proxy with 4.7352 m3 solid volume against
the real hull's 3.542739.

The canonical set is **17 runs** on one Yaris hull at 1100/1609/2337. So the protocol
was commissioned against the sweep the project has since discarded, and its held-out
layer ("reserve strata from the 3x4x3 sweep") has no 3x4x3 to reserve from.

## 4. WITHDRAWN, AND THE PROJECT IS RIGHT: the GCI criticism

I wrote that the protocol asks for GCI intervals "so that an unconverged result can
still be reported credibly with a bound, rather than by omission", and that "silence
and a reported interval are different things". **Both halves are wrong.**

**(a) No GCI band is computable, for a reason that precedes monotonicity.** The
grids are 48, 64, 96, so the refinement ratios are **not constant**:

```
r21 = (1/64)/(1/96) = 1.500000
r32 = (1/48)/(1/64) = 1.333333      |r21 - r32| = 0.1667
```

An apparent order `p` requires a constant ratio. The project's own gate encodes
exactly this at `.claude/checks/physics_gates_literature.py:60-64`, and running
`params_check.py` returns, for all three masses, "grid refinement ratio is not
constant ... cannot compute apparent order p, report the raw non-monotone spread
instead of a GCI band".

**(b) It was not silence. The project already published the reason.**
`deliverables/paper/overleaf/sections/limitations.tex:13`:

> "**No Grid Convergence Index is computable.** Grid resolutions 48, 64 and 96 were
> run, but the g64 to g96 change is negative and non-monotonic, and **GCI requires
> monotone refinement behavior**. The resolution results are reported as measured
> rather than compressed into an observed order of convergence the data does not
> support."

`future_work.tex:66-83` is a subsection titled "Grid convergence is non-monotonic, so
no uncertainty can be quoted".

**So I criticised them for omitting something that cannot be done and that they had
already explained.** That is the worst kind of error in this dispatch: not a
miscount, but a criticism aimed at correct work.

**(c) A detail my summary flattened.** Non-monotone is true at 1100 kg
(0.3507, 0.6585, 0.2686) and 1609 kg (0.2568, 0.3141, 0.1560) but **2337 kg is
monotone** (0.1875, 0.1356, 0.0894). Register B2 records this; my one-line
"non-monotone" erased it.

## 5. Other withdrawals

**W1. "Nothing from it reached the paper." WITHDRAWN.** Three of the 81 catalog DOIs
are in `paper/can_it_ford_references_IEEE.bib`: `10.1115/1.4071177` (He 2026),
`10.1002/AIC.15868`, `10.1002/nme.7217`. Two sit under the header at `:287`,
**"% NUMERICS AND UNCERTAINTY: methods used or recommended by this work"**, so
someone deliberately filed them. The defensible narrow claim is that **none is
`\cite`d and none appears in the compiled PDF's reference list.**

**W2. "The paper never once uses the word convergence." WITHDRAWN.** `not
grid-converged` appears **three times** in the PDF, and each time it is used to
*refuse* a magnitude: "the lines do not overlay, so the effect size is not
grid-converged", "no ratio or multiplier is reported because the magnitude is not
grid-converged". I reported a string result as a conceptual one.

**W3. "Register item 5." WITHDRAWN as a miscitation.** That is CLAUDE.md's August-4
audit item 5. The register's own entry is **B2** at
`CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:76-79`. Under this project's authority
rules those are different tiers.

**W4. "Celik 2007." WITHDRAWN: Celik et al. 2008**, J. Fluids Eng. 130(7):078001. I
inherited the year from the catalog without checking, which is the exact failure my
own memory records as "Xia is 2014, not 2013".

**W5. "Named in 1 repo file." WITHDRAWN:** 2 in the main tree today, and the one
genuine hit is an `ls -l` directory listing inside a session log, not a citation.

## 6. Status

UNVERIFIED:
1. **I measured the 7-page PDF only.** A different, longer paper exists at
   `deliverables/paper/overleaf/` and I never examined it. Any statement here about
   "the paper" means that one PDF.
2. Carries FLAG-6: the live Overleaf head is unreachable, token file still 0 bytes.
3. I read the protocol's goal, summary and part of its catalog, not its 550 lines.
4. Whether the compiled paper *should* cite V&V references is editorial. I establish
   only that it does not.
5. The reviewer flagged its own limit: it could not read the Celik/Roache text, so
   "GCI assumes monotone convergence" is recalled from the literature, not read. It
   does not matter here, because the non-constant refinement ratio bars the
   apparent-order step regardless.
