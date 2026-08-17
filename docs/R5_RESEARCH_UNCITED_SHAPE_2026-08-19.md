# R5-D1 unit 54: the shape of what this project has not read

Date 2026-08-19. Branch `claude/r5-research`.
**For the novelty statement and the bibliography.**

Unit 49 classified the 138 uncited catalogued papers only for MPM. This is the rest
of the classification, and it has a clear and useful shape.

---

## 1. The shape

Classifying all 138 uncited rows by title. **Categories overlap** (a paper can be
both MPM and validation), so these do not sum to 138 and must not be added.

| category | uncited |
|---|---:|
| MPM method | **37** |
| **V&V / UQ / validation methodology** | **30** |
| SPH | 12 |
| any vehicle word, loose probe | **4** |
| reconstruction (splat, NeRF, SfM) | 3 |
| ML / surrogate | 1 |

**The single most informative number is the validation one, taken as a rate rather
than a count:**

```
V&V / UQ papers catalogued : 35
  UNCITED                  : 30
  cited                    :  5
  => 86% of the catalogued validation literature is uncited
```

## 2. Why that matters more than the raw counts

CLAUDE.md's L-7 states the project's position directly:

> "arXiv 2607.00673 ... covers reconstruction plus MPM plus route feasibility
> without external validation. **The novelty for this project is the validation
> step, not the pipeline.**"

**So the claimed contribution is validation, and 86% of the catalogued validation
literature has never been cited.** Four of those are directly on target, and I
re-checked every one against today's repo:

| DOI | paper | repo | `.tex` | paper `.bib` |
|---|---|---:|---:|---:|
| `10.1109/access.2022.3157904` | **Framework for Vehicle Dynamics Model Validation** | **0** | **0** | **0** |
| `10.3390/app11051983` | **Statistical Validation Framework for Automotive Vehicle Simulations** | **0** | **0** | **0** |
| `10.1002/nme.70210` | **Validating High-Performance Multi-GPU MPM** for debris-fluid-structure interaction | **0** | **0** | **0** |
| `10.1016/j.jcp.2024.113457` | Mixed MPM formulation, stabilization, **and validation** | 1 | **0** | **0** |

**Control, so the zeros mean something:** the paper does discuss the topic.
`verification` appears in **5** `.tex` files, `validation` in 1, `uncertainty` in 1.
The subject is present; the literature is not.

## 3. The contrast, which is the actual finding

**The flood-vehicle application literature is almost fully cited. The method and
validation-methodology literature is almost entirely uncited.**

A strict probe (a vehicle word and a water word, both in the title) finds exactly
**1** uncited paper in 138. A loose probe (any vehicle word) finds **4**. Against
that, 37 MPM and 30 validation papers sit uncited.

**So this project has read its application domain thoroughly and its method and
validation domains barely at all, while claiming its contribution in the latter.**
That is a sharper and more useful statement than unit 49's, which reported only the
MPM half.

**A fair reading in the project's favour**, which I want on the record: near-total
coverage of the application literature is a real strength, and it is what the
catalogs were built to support. The gap is not carelessness across the board; it is
specific and it is fixable with a small number of citations.

## 4. What the other 88 are

The uncategorised remainder is dominated by particle-method and free-surface
hydrodynamics: multi-resolution MPS, incompressible projection solvers, sloshing and
slamming benchmarks, water entry and exit, ship hydrodynamics uncertainty. Several
are canonical benchmark-and-uncertainty papers (`A set of canonical problems in
sloshing`, `A comprehensive framework for verification, validation, and uncertainty
quantification`).

These are plausibly *not* required citations for this paper. I list them so the
88 is not mistaken for 88 more gaps.

## 5. Status

UNVERIFIED:
1. **Carries FLAG-6.** All `.tex` and `.bib` counts are against local copies dated
   2026-07-30 to 2026-08-04 (the compiled PDF). The live Overleaf head is
   unreachable; the token file is still 0 bytes.
2. **Classification is title-regex only**, and titles are a weak proxy for content.
   I read the titles of every paper I name, and none of the others.
3. **Categories overlap and must not be summed.** `Validating Multi-GPU MPM` is
   counted in both MPM and V&V, correctly.
4. The 86% is a rate over the **35 catalogued** V&V papers, not over the validation
   literature as a whole, which nothing here measures.
5. Their TSV's own blind spot applies: **37 catalog rows carry no DOI** and are not
   diffable, so every uncited count is a floor.
6. Whether any of these belong in the paper is an editorial judgement. The two
   vehicle-validation frameworks are the strongest candidates on relevance grounds,
   and I have not read either.
