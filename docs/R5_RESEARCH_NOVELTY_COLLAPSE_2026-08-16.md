# R5-D1 unit 7: I read the papers, and every axis I proposed is occupied

Date 2026-08-16. Branch `claude/r5-research`. Unit 6 ended by saying the right
next step was to stop counting and read the four papers that matter. This is
that, for the two that were reachable.

**Result: all three novelty axes I proposed in unit 4 are occupied, and two of
the occupying papers are already in this project's own bibliography. I am also
correcting a claim I made in unit 4 that was wrong.**

---

## 1. Al-Qadami et al. 2023, read in full

`10.3390/su151713262`, *Sustainability* 15(17) 13262. Obtained CC-BY from the
UPCommons repository copy, which is the institutional-repository route: the
publisher front end was not needed. 1,941 lines of extracted text, READ DIRECTLY.

| property | what the paper actually does |
|---|---|
| solver | **FLOW-3D v11.2**, finite volume method, k-epsilon turbulence, no-slip wall shear |
| vehicle | **full-scale** Perodua Viva, medium-size passenger car |
| geometry source | **3D model built in SolidWorks 2016**, exported to STL |
| body dynamics | **"All numerical runs in this study were conducted under coupled motion and six degrees of freedom conditions"** |
| scenario | static (stationary) flooded vehicle, subcritical and supercritical, Froude 0.09 to 2.46 |
| mesh study | four-level mesh-independence study at cell sizes 0.1, 0.075, 0.05 and 0.025 m; **0.05 m selected** |
| results | floating at 0.38 m depth; sliding once depth x velocity exceeds 0.36 m2/s |

Their stated purpose of the 6DOF setup, verbatim:

> Such a setup allows us to detect the center of mass (COM) of the vehicle at
> every time step and visualizes whether the vehicle is stable or not.

**Their validation is a three-way chain**, section 4 of the paper:

1. against the **AR&R 2011** guidelines: "the obtained numerical results under six
   degrees of freedom and coupled motion conditions strongly agree with the
   published guidelines";
2. against **Martinez-Gomariz et al. 2017** theoretical equations;
3. against **their own physical experiments** (Al-Qadami et al. 2022, same Perodua
   Viva): "both results properly aligned with each other".

They also state the gap they were filling, which is instructive because it is
close to ours: prior numerical work "did not employ the fully coupled numerical
simulation, i.e., the vehicle models were simulated as a fixed object".

## 2. Azhar et al. 2023 is a particle method, validated, and we already cite it

`10.1111/jfr3.12885`, bib key `azhar2023`. This is one of only three catalogued
DOIs actually `\cite`d in our paper. Abstract READ DIRECTLY from Crossref:

> The numerical investigation is performed using **smoothed particle
> hydrodynamics (SPH)** with the vehicle oriented perpendicular to the flow
> direction, as this is the most critical orientation. **A physical model study is
> also performed and its results are used to validate the SPH model.** The results
> confirm the current Australian Rainfall and Runoff (ARR) safety criteria for
> stationary vehicles. It also suggests that the ARR stability curve can shift
> depending on the road conditions that affect the vehicle's sliding mechanism.

SPH is a particle method. So the axis I called "particle method rather than mesh
CFD", the one I said survived in unit 4 section 1a, is occupied as well, by a
paper we cite.

This is also where our `floor_friction = 0.55` traces: Elicit row 39 extracted
"rolling friction coefficient = 0.55, measured" from this DOI. So the same paper
supplies our friction value, uses a particle method, validates against physical
experiment, and confirms AR&R for stationary vehicles.

## 3. Every axis, restated honestly

| axis I proposed in unit 4 | occupied by | already cited by us? |
|---|---|---|
| validation against experiment | He 2026 `10.1115/1.4071177`; Azhar 2023 `10.1111/jfr3.12885`; Al-Qadami 2023 (via their 2022 experiments) | Azhar **yes** |
| full scale | Al-Qadami 2023 `10.3390/su151713262` | no, see section 4 |
| stability verdict / thresholds | Al-Qadami 2023; Azhar 2023 | Azhar **yes** |
| particle method | Azhar 2023 (SPH); Zhang 2023 and Lyu 2023 (SPH) | Azhar **yes** |
| 6DOF free rigid body | Al-Qadami 2023, explicitly, and Al-Qadami 2021 before it | no |

**What is actually left, on the evidence I have.** Two things, and they are
narrower than anything I have written so far:

1. **MPM specifically, rather than SPH or FVM.** A material point method has
   different contact and history-variable behaviour from SPH. That is a real
   methodological difference, but it is a difference within particle methods, not
   a difference from them.
2. **Geometry provenance.** Al-Qadami built their vehicle in SolidWorks by hand.
   Our hull is derived from real reconstructed geometry. That is the
   reconstruction-to-simulation pipeline the arXiv 2607.00673 lineage names, and
   it is the one axis on which nothing I found competes.

I am not saying the work has no contribution. I am saying the contribution is the
**pipeline and the method**, not the result, and that every sentence claiming
otherwise is now refutable from papers in our own bibliography.

## 4. CORRECTION to unit 4: we do NOT cite Al-Qadami 2023

Unit 4 stated that `10.3390/su151713262` "is already cited in
`paper/can_it_ford_references_IEEE.bib`, one of only 8 catalogued DOIs that reach
the paper at all". **That was wrong, and I am withdrawing it.** My cross-reference
matched the DOI as a string anywhere under `paper/`. It is not a bibliography
entry. It appears only inside the `note` field of a *different* entry, for the
2022 paper, and that note is itself a flag of uncertainty:

```bibtex
@article{alqadami2022,
  author = {Al-Qadami and others},
  title  = {{VERIFY: exact title}},
  year   = {2022},
  note   = {... A separate Al-Qadami et al. 2023 (Sustainability, DOI
            10.3390/su151713262) also appears in project notes; confirm which is
            the correct rollover-literature citation.}
}
```

So the true position is worse than what I reported, not better: **the paper does
not cite the closest comparable study at all**, and the entry that mentions it
has a placeholder where its title should be.

## 5. The real count of catalogued DOIs reaching the paper is 3, not 8

Unit 1 section 6 reported "cited in paper bib/tex: 8". That counted DOI strings
appearing anywhere under `paper/`, `overleaf_sync/` and `deliverables/`, which
includes notes, comments and superseded copies. Recomputed against bibliography
structure and actual `\cite` keys across the 3 `.tex` files (18 distinct cite
keys):

```
of the 489 catalogued DOIs:
  present in a real  doi = {...}  field of a bib entry :  7
  present ONLY inside a note or comment                :  1
  actually \cited in any .tex                          :  3
```

The three genuinely cited: `shah2018` (`10.1051/matecconf/201820307003`),
`smithmodrafelder2019` (`10.1111/jfr3.12527`), `azhar2023`
(`10.1111/jfr3.12885`). All three verified this session against Crossref:
authors, titles, years and DOIs all match. **The three live citations are sound.**

The four with a `doi =` field but never cited: `xia2010`, `xia2013`,
`kramer2016`, `xiong2024`.

**Use 3 for "reaches the paper", 7 for "has a real bib entry", and 8 only for
"the string appears somewhere under paper/". Unit 1's 8 should be read as the
third of those.**

## 6. A bibliography defect worth fixing before submission

`paper/can_it_ford_references_IEEE.bib` has **21 entries, of which 9 contain a
`VERIFY` marker**, and **two have a literal title of `{{VERIFY: exact title}}`**:
`alqadami2022` and `martinezgomariz2018`.

Both are currently cited in **zero** `.tex` files, so BibTeX will not emit them
and they cannot reach a compiled PDF today. That makes this a latent defect
rather than a live one: the moment somebody writes `\cite{alqadami2022}`, the
bibliography prints "VERIFY: exact title".

I can supply both titles from work already verified this session:
- `alqadami2022` is `10.1111/jfr3.12828`, "A numerical approach to understand the
  responses of passenger vehicles moving through floodwaters", Al-Qadami,
  Mustaffa, Al-Atroush, Martinez-Gomariz, Teo, El-Husseini, 2022.
- `martinezgomariz2018` is most likely `10.1111/jfr3.12262`, "Stability criteria
  for flooded vehicles: a state-of-the-art review", 2018, but I have **not**
  confirmed that this is the work the project intended, because the entry carries
  no title, no DOI and no journal to disambiguate against. Do not guess it.

I have not edited the bibliography. It is outside my declared scope
(`docs/R5_RESEARCH_*`, `data/r5_citation_*`) and it belongs to whoever owns the
paper.

## 7. A caveat on the verification tool itself

Earlier in this dispatch I ran `auditBibliography` with the title "...smoothed
particle hydrodynamics and **experimental data**" for `10.1111/jfr3.12885`. It
returned `matched` with `high` confidence. The real subtitle is "...and
**laboratory measurements**". The bibliography had it right and my paraphrase had
it wrong, and the tool did not catch the difference. That is worth knowing: a
`matched` verdict tolerates a materially different trailing phrase, so it
confirms identity, not exact wording. Do not use it to certify a title string.

## 8. UNVERIFIED

1. **He 2026 and Zhang 2023 and Lyu 2023 full texts remain unread.** All three
   are closed access with no OA location on any route tried. The axis table in
   section 3 rests on abstracts for those three.
2. `martinezgomariz2018`'s intended referent is unknown; my suggestion is a
   guess and is labelled as one.
3. The resolution comparison between Al-Qadami's 0.05 m mesh and our g64 grid is
   **held pending an adversarial review** and is deliberately not stated here.
4. Whether MPM versus SPH is a defensible novelty axis is a physics judgement,
   not a bibliographic one. It is D4's call, not mine.
