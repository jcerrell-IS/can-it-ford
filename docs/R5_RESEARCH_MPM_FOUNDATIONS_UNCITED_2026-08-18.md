# R5-D1 unit 49: the paper cites no MPM method literature at all

Date 2026-08-18. Branch `claude/r5-research`.
**For whoever owns the bibliography. This is the most directly actionable finding
of this dispatch.**

Unit 47 reported four uncited MPM method papers from a corpus file's highlighted
list. I then read the full 205-row TSV, which I had listed as unverified. The gap
is an order of magnitude larger, and it reaches the foundations.

---

## 1. Their build reproduces exactly

Before using their data I re-derived their headline from the TSV itself:

```
total rows          : 205
uncited anywhere    : 138     README claims 138   MATCH
cited somewhere     :  67     README claims  67   MATCH
```

**Both reproduce.** That is independent verification of a sibling artifact's
headline numbers, from its own data, not from its prose.

## 2. Thirty-seven uncited MPM method papers, not four

Classifying the 138 uncited rows by title:

```
uncited MPM-method papers        : 37 of 138
  of those, free-surface         :  7
  of those, vehicle-related      :  0
  appearing in MORE THAN 1 report:  7
```

The seven multi-report ones, which are the strongest signal:

| reports | year | paper |
|---:|---:|---|
| 4 | 2017 | Incompressible material point method for free surface flow |
| 4 | 2022 | An immersed finite element material point (IFEMP) method for free-surface FSI |
| 3 | 2019 | **Benchmarking the material point method for interaction problems between the free surface and a body** |
| 3 | 2020 | Material point method after 25 years: theory, implementation, and applications |
| 2 | 2016 | Modeling of free surface flows using improved MPM and adaptive mesh refinement |
| 2 | 2017 | Numerical simulations of dam-break floods with MPM |
| 2 | 2019 | An investigation of stress inaccuracies and proposed solution in MPM |

And among the 30 single-report ones sit foundational and pathology papers:
**The Generalized Interpolation Material Point Method** (GIMP, 2004),
Multiscale simulations using GIMP (2005), **Overcoming volumetric locking in
material point methods** (2018), Decoupling and balancing of space and time errors
in MPM (2010), MPM and SPH simulations compared (2016), and
`v-p` MPM for weakly compressible problems (2018).

Re-checked against today's repo, the key ones:

| DOI | paper | repo | `.tex` | paper `.bib` |
|---|---|---:|---:|---:|
| `10.3970/cmes.2004.005.477` | **The Generalized Interpolation MPM (GIMP)** | **0** | **0** | **0** |
| `10.1016/bs.aams.2019.11.001` | Material point method after 25 years | 1 | **0** | **0** |
| `10.1504/pcfd.2019.10018820` | Benchmarking MPM, free surface plus body | 2 | **0** | **0** |
| `10.1016/j.cma.2018.01.010` | Overcoming volumetric locking in MPM | **0** | **0** | **0** |
| `10.1504/pcfd.2016.10001222` | MPM and SPH simulations compared | **0** | **0** | **0** |
| `10.3970/cmes.2005.008.135` | Multiscale simulations using GIMP | **0** | **0** | **0** |

## 3. The headline: Sulsky is absent, and so is every other MPM method citation

**Sulsky et al. is the founding MPM paper.** I probed for it six independent ways,
with positive controls to prove the probe works:

```
Sulsky / sulsky                    tex:0   bib:0
"history-dependent materials"      0        (its title)
10.1016/0045-7825(94)90112-0       0        (its DOI)
"0045-7825(94)"                    0        (DOI stem)
"Chen and Brackbill"               0        (classic collaborator)
"PIC method"                       0

POSITIVE CONTROLS
"material point"                   tex:6
MPM                                tex:3   bib:6
Yaris                              tex:5   bib:5
warpmpm                            tex:1
```

**The controls fire; Sulsky does not.** This is a real absence, not a broken probe.
(I checked this way because unit 36's failure was a false zero produced by a
malformed command.)

**The full bibliography, all 21 keys:**

```
ccsa2010yaris  thorpe2026pvwm  hsiaokumar2025  kerbl20233dgs  xie2023physgaussian
shand2011  smithmodrafelder2019  azhar2023  xiong2024  xia2010  xia2013  kramer2016
shah2018  martinezgomariz2018  alqadami2022  sae1999011336  videophy2024
mpmworlds2026  nws_tadd  genesis2024  fred2026
```

Every MPM-adjacent entry is an **application**: `hsiaokumar2025` (NeRF-to-MPM
inversion), `mpmworlds2026` (MPMWorlds), `azhar2023` (SPH plus lab measurement).

**So the paper writes "material point" six times and cites not one paper that
establishes, analyses or benchmarks the method.** No founding paper, no GIMP, no
review, no free-surface benchmark, no known-pathology paper.

## 4. What I am and am not claiming

**Claiming:** the bibliography contains zero MPM method literature, the corpus
already holds 37 uncited candidates, and the project's own catalogs surfaced the
most relevant ones repeatedly across separate reports.

**Not claiming that all 37 belong in the paper.** They plainly do not. A realistic
addition is small, and on the evidence here the defensible shortlist is:
**Sulsky** (the method), **GIMP** (the interpolation scheme in near-universal use),
**MPM after 25 years** (the review), and **Benchmarking MPM for free-surface/body
interaction** (our exact problem class). Four citations, not thirty-seven.

**Not claiming this is a defect in the physics.** It is a scholarship gap. It costs
nothing to fix and is the kind of omission a reviewer of an MPM paper notices
immediately.

## 5. Status

UNVERIFIED:
1. **Carries FLAG-6.** Every `.tex` and `.bib` count is against local copies dated
   2026-07-30 to 2026-08-02. The live Overleaf head is unreachable, so the paper may
   already cite Sulsky and I could not see it. **This is the single most likely way
   this finding is wrong**, and it is one browser login from being resolved.
2. Classification of the 37 as "MPM method papers" is a title-regex match
   (`material[- ]point|MPM`), reviewed by eye for the ones I name but not for all 37.
3. I have not read any of the 37. Titles and the corpus catalogs are my only source
   for what they contain.
4. Whether any given paper belongs in the bibliography is an editorial judgement.
5. Their TSV inherits its own README's blind spot: 37 catalog rows carry no DOI and
   are not diffable, so the uncited set is a floor, not a census.
