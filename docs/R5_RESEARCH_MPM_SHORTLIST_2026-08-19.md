# R5-D1 unit 67: the four MPM method citations, verified and paste-ready

Date 2026-08-19. Branch `claude/r5-research`.
**For whoever owns the bibliography. This is unit 49 made usable.**

Unit 49 found the paper cites no MPM method literature and proposed a four-paper
shortlist without verifying any of it. Unit 66 confirmed the finding is genuinely new
(zero register coverage). This resolves all four against Crossref and names the trap
in each.

---

## 1. The four, verified

**Sulsky, Chen and Schreyer 1994. The founding MPM paper.**
```
doi     10.1016/0045-7825(94)90112-0            verdict matched, high confidence
title   A particle method for history-dependent materials
in      Computer Methods in Applied Mechanics and Engineering 118(1-2):179-196
cited   1,440 times (Crossref is-referenced-by-count)
```
**Trap:** Crossref lists an alias, `10.1016/0045-7825(94)00033-6`. Use the `90112-0`
form; the alias is the same paper and will confuse a dedup pass.

**Bardenhagen and Kober 2004. GIMP, the standard reference for MPM's shape-function problem.**
```
doi     10.3970/cmes.2004.005.477
title   The Generalized Interpolation Material Point Method
in      Computer Modeling in Engineering & Sciences 5(6)
```
**Trap 1: the registry record is malformed.** It returns a single author with an empty
`family` and the whole name in `given` ("S. G. Bardenhagen"), and **Kober is missing
entirely**. Do not paste the registry authors; type them.

**Trap 2, and it changes the justification. CORRECTED unit 68: warpmpm does NOT use
GIMP.** I closed my own unverified item by reading the solver, and it uses
**quadratic B-spline** transfer:

```
GIMP / "generalized interpolation" : 0 files of 30
B-spline                           : 5 files
quadratic                          : 4 files
kernels/__init__.py:5   "The base solver, quadratic B-spline transfer, and materials 0-8..."
mpm_utils.py:1383       "standard quadratic B-spline weights (same as g2p)"
```

**So my unit-67 wording, "the interpolation scheme in near-universal use, including in
warpmpm-family solvers", was wrong on the second half.** GIMP remains defensible as
background, because it is the standard reference for the shape-function problem MPM
has and is one of the two schemes any MPM reader expects to see named. **But it must
not be cited as describing what this solver does.** If only three citations are
wanted, this is the one to drop.

**de Vaucorbeil, Nguyen, Sinaie and Wu 2020. The standard review.**
```
doi     10.1016/bs.aams.2019.11.001
title   Material point method after 25 years: Theory, implementation, and applications
in      Advances in Applied Mechanics, pp. 185-398
```
**Two traps.** It is a **book chapter**, not a journal article, so `@incollection`
or `@article` matters for the style. And Crossref returns an **empty author list**,
so the names must come from the paper, not the record. Note also the DOI stem says
2019 while the issued year is **2020**.

**Sun, Huang and Zhou 2019. Benchmark for free-surface flow plus an elastic body.**
```
doi     10.1504/PCFD.2019.10018820
title   Benchmarking the material point method for interaction problems between
        the free surface flow and elastic structure
in      Progress in Computational Fluid Dynamics 19(1)
```
**Trap, and it is the worst of the four: this article has TWO DOIs.** The
`10018820` form is Inderscience's internal article ID and is what our catalogs
carry; resolving it returns a canonical URL of
`https://doi.org/10.1504/pcfd.2019.097597`, with `number: 97597`. **Both resolve to
the same paper.** Cite the `097597` form if you want the one a reader's resolver
will show, and expect a dedup pass to treat them as two papers.

## 2. Why these four and not the other thirty-three

Unit 54 found **37 uncited MPM method papers**. These four are chosen on distinct
grounds, one each:

| paper | why this one |
|---|---|
| Sulsky 1994 | the method exists because of it; omitting it is the omission a reviewer sees first |
| GIMP 2004 | the standard reference for MPM's shape-function problem. **NOT what warpmpm uses** (quadratic B-spline, unit 68). Weakest of the four; drop this one first |
| after-25-years 2020 | the standard review, and the single citation that covers the most ground |
| Sun 2019 | **free surface plus a body**, which is exactly the problem class the 17 runs solve, and it is a *benchmark* |

**I am not recommending the other 33.** A realistic addition here is four citations.

## 3. Status

UNVERIFIED:
1. **I have read none of these four papers.** I verified their bibliographic records,
   not their contents, so "GIMP is in near-universal use" and "Sun 2019 is our exact
   problem class" are judgements from titles and the corpus catalogs.
2. ~~Whether warpmpm implements GIMP I did not check.~~ **CLOSED, unit 68: it does
   not.** warpmpm uses quadratic B-spline transfer; GIMP appears in 0 of 30 source
   files. Wording corrected in section 1, and GIMP demoted to the weakest of the four.
3. Whether any of these belongs in the paper is editorial. Unit 49 establishes the
   absence; it does not establish an obligation.
4. Author lists for GIMP and the 25-years review must be typed from the papers,
   because both registry records are defective (section 1).
5. Register checked before writing, per the rule I broke in unit 64: zero hits for
   `Sulsky`, `GIMP`, `Bardenhagen`, `Vaucorbeil` in
   `CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.
