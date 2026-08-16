# R5-D1 unit 4: proposed CLAUDE.md amendments, and the catalogs measured against the citation graph

Date 2026-08-16. Branch `claude/r5-research`. Follows units 1 to 3.

**I have not edited `CLAUDE.md`. Everything below is a proposal for Josie.**

Summary of the two amendments proposed here, and the one withdrawn:

| entry | proposal | basis |
|---|---|---|
| **L-7** | **amend**, the novelty is no longer "the validation step" alone | He 2026 abstract, READ DIRECTLY |
| **L-2** | **do not amend**, attach a source only | AR&R primary source, READ DIRECTLY, unit 3 section 4 |
| **L-5** | add a DOI, no wording change | unit 2 section 3 |

---

## 1. Proposed L-7 amendment

**Current text**, `CLAUDE.md`, AUGUST 5 2026 RESEARCH INTEGRATION section:

> L-7. arXiv 2607.00673 (Low, Hsiao, Li, Thorpe, Topcu, Kumar, July 2026) covers
> reconstruction plus MPM plus route feasibility without external validation. The
> novelty for this project is the validation step, not the pipeline.

**Why it needs changing.** He et al. 2026, `10.1115/1.4071177`, *Journal of
Computational and Nonlinear Dynamics* 21(6) 061002, states the validation gap and
then fills it. Verbatim from the abstract:

> Despite advances in computational approaches for modeling vehicle-fluid
> interactions, only limited studies have been conducted regarding the validation
> of the models in real physical settings. There are few or no experimental data
> available to characterize hydrodynamic loads for the evaluation of transient
> vehicle responses in shallow water. Therefore, this study presents the
> validation of the physics-based and data-driven coupled vehicle-water
> interaction models using a model-scale vehicle operated in shallow water.

and:

> Furthermore, the hydrodynamic loads on the model-scale vehicle subjected to
> incoming water flow are measured through flume experiments and used to validate
> the hydrodynamic loads predicted by the simulation model.

L-7's sentence, "the novelty for this project is the validation step", was true
against arXiv 2607.00673. It is not true as a general statement about the field
once He 2026 is on the table. A reviewer who knows this literature will know He
2026, because it is a US Army DEVCOM GVSC plus University of Iowa programme that
also produced `10.1115/1.4064971` and `10.1016/j.oceaneng.2022.111607`.

**Proposed replacement text:**

> L-7. arXiv 2607.00673 (Low, Hsiao, Li, Thorpe, Topcu, Kumar, July 2026) covers
> reconstruction plus MPM plus route feasibility without external validation.
> DO NOT extend that into "nobody has validated a vehicle-water model". He et al.
> 2026, `10.1115/1.4071177`, J. Comput. Nonlinear Dynam. 21(6) 061002, validates
> a coupled vehicle-water interaction model against physical experiment in two
> configurations: free-running vehicle trials in a shallow water pool, and flume
> measurements of hydrodynamic loads on a vehicle in incoming flow. That second
> configuration is our scenario. The validation axis is therefore occupied, and
> any novelty sentence must cite He 2026 and claim only what survives it:
> **full scale** rather than model scale, a **particle method (MPM)** rather than
> mesh CFD plus multibody dynamics, and a **stability verdict** rather than
> hydrodynamic load prediction. Verified 2026-08-16 from the abstract; the full
> text has not been read, so the three surviving axes are UNVERIFIED against the
> paper's body.

**Honest limitation on this proposal:** I read He 2026's abstract, not its full
text. The abstract is explicit about model scale and about experimental
validation, so those two axes are solid. Whether the paper also reports a
stability or safety threshold, which would narrow the third axis, is UNVERIFIED.
Someone should read the full text before the novelty paragraph is finalised.

## 2. Row 7: the stored 1:10 must not be applied to it

Stated in terms, as requested, because this is a stored memory being refuted by a
primary source.

**Project memory records that "Shah 2018" is 1:10 scale and that full-scale
values require a factor of 1000. That figure must NOT be applied to Elicit row 7,
`10.11113/JT.V80.11198`.** Doing so would produce a wrong number.

Primary source, *Jurnal Teknologi* 2018, diamond OA, abstract READ DIRECTLY:

> A stationary die-cast model vehicle (**1:24**) was used with the condition of
> **rear tires being locked only**, positioned at different orientation angles on
> a flat road surface in the partially submerged zone.

The reason the stored figure does not apply is a first-name collision that
project memory itself already flags as a trap:

| DOI | year | first author | configuration | scale |
|---|---|---|---|---|
| `10.11113/JT.V80.11198` | 2018 | Syed **Hamid** Hussain Shah | stationary die-cast model, rear tyres locked only | **1:24** |
| `10.1051/MATECCONF/201820307003` | 2018 | Syed **Muzzamil** Hussain Shah | Perodua Viva, non-stationary | **1:10** |
| `10.1016/j.rineng.2019.100032` | 2019 | Syed **Muzzamil** Hussain Shah | Perodua Viva, "ensuring similarity laws" | **1:10** |

Both 2018, both Shah, both with Mustaffa and Yusof. **Disambiguate by first name.
Never cite "Shah 2018" unqualified.** The stored 1:10 belongs to Muzzamil.

Consequence for the numbers: row 7's `0.0168` and `0.0144 m2/s` are 1:24 model
scale and are not comparable to the full-scale `0.30 m2/s` AR&R limit. Unit 1
called the gap "roughly twenty times"; under Froude similitude, where `DV` scales
as `lambda^1.5` and `24^1.5 = 117.58`, the gap is about **118x**, not 20x. That
arithmetic is COMPUTED BY ME and is illustrative only: I do not offer 1.98 and
1.69 m2/s as corrected thresholds, because a die-cast model does not satisfy mass
similitude and the paper supplies no similitude argument.

## 3. The catalogs are not a census, and here is the measurement

Unit 3 reported this as a qualitative worry after `10.1016/j.compfluid.2023.106144`
turned up in none of the 14 catalogs. I have now measured it.

**Method.** Take the 16 vehicle-in-water simulations as seeds. For each, pull its
OpenAlex neighbourhood in one hop, both directions: every work that cites it, and
every work it references. Filter titles for a vehicle term and a water term, then
check each against the 489-DOI corpus from unit 1. Fully scripted, no key
required, reproducible on the Mac. Data in `data/r5_citation_graph_missed.tsv`,
62 rows.

**Result, with denominators:**

```
seeds resolved                                    16 / 16
works in the one-hop neighbourhood               591
  titles carrying a vehicle term and a water term  62
  of those, NOT in the 489-DOI corpus              28
  of those 28, simulation or numerical titles      16
```

**Sixteen vehicle-water simulation papers are absent from all 14 catalogs**, from
a single hop over 16 seeds. That is a recall of roughly one half on the exact
question the novelty claim turns on, and one hop is not exhaustive.

| year | DOI | title |
|---|---|---|
| 2026 | `10.1080/19942060.2026.2649668` | Coupled lattice Boltzmann-cellular automata model, dynamic optimization |
| 2026 | `10.1016/j.jhydrol.2026.135478` | Flood risk assessment model integrating hydraulic ... |
| 2025 | `10.3390/w18010080` | A New Semi-Empirical Model to Predict Vehicle Instability in Urban Flooding |
| 2025 | `10.1016/j.oceaneng.2025.123181` | Environmental effects on water-ground vehicle |
| 2025 | `10.1016/j.oceaneng.2025.123054` | Rapid prediction of underwater vehicle hydrodynamic loads |
| 2024 | `10.1111/jfr3.12979` | Flood risk of pedestrians and vehicles in a mountainous city |
| 2024 | `10.1007/978-3-031-77489-8_32` | Numerical Studies of 3D Vehicle Wading with an Improved Single-Layer ... |
| 2023 | `10.4271/2023-01-0609` | Vehicle Underbody Structural Performance Prediction During Waterfording |
| 2022 | `10.1016/j.scitotenv.2022.154098` | Integrated 2D urban surface and 1D sewer hydrodynamics |
| 2021 | `10.1088/1742-6596/2083/4/042091` | Numerical simulation and intelligent computing of vehicle wading |
| 2020 | `10.1016/j.oceaneng.2020.107460` | Amphibious craft in calm water, experimental and computational |
| 2017 | `10.4271/2017-01-1327` | Water Ingress Analysis and Splash Protection for Vehicle Wading, CFD |
| 2016 | `10.4271/2016-28-0072` | Passenger Car Water Wading Evaluation Using CFD Simulation |
| 2014 | `10.4271/2014-36-0251` | Water Ingestion and Pressure Analysis using Multiphase ... |
| 2012 | `10.1007/978-3-642-33835-9_15` | Vehicle Wading Simulation with STAR-CCM+ |
| 2010 | `10.1680/wama.2010.163.6.273` | Modelling the hydraulics of the Carlisle 2005 flood event |

**What this means, in terms.** Vehicle wading CFD is not an emerging research
question. It is established automotive-industry practice with a continuous SAE
and commercial-code literature running from at least 2012 (`STAR-CCM+`) through
2014, 2016, 2017, 2021 and 2023. **Any sentence of the form "N vehicle fording
simulations exist" is a floor, never a total, and no catalog-based search can
establish a novelty claim.** The count went 4, then 5, then 15, then 16, then 32,
and it moved every single time somebody looked with a new instrument. It will
move again.

**The non-catalog route, and why it is different in kind.** A keyword catalog is a
*sample* drawn by a query; its recall is unknown and unmeasurable from inside
itself, which is exactly how the previous round got to "four". A citation-graph
traversal is a *closed operation on a graph*: from a seed set, iterate cites and
referenced-by to fixpoint, and within the connected component nothing is missed
regardless of how a title is worded. Concretely, and all free and scriptable:

1. **Seed** with the 32 papers now known, not with a query.
2. **Iterate to fixpoint** on OpenAlex `cites:` and `referenced_works`, not one
   hop. Stop when a round adds nothing new, which is the same loop-until-dry
   stopping rule unit 2 recommends for settling.
3. **Cluster by author**, because this field is a handful of groups: Iowa plus
   DEVCOM GVSC (Sugiyama, Jayakumar, Tison, Yamashita, Harwood); the Liu and
   Zhang SPH school; the Mustaffa, Shah and Al-Qadami group; the Martinez-Gomariz
   and Russo group; the UNSW group (Smith, Cox, Felder); Xia and Falconer.
   Enumerating every work by those clusters catches papers the graph misses
   because they are new and uncited.
4. **Sweep the venues** that dominate the list: SAE Technical Papers, J. Flood
   Risk Management, Results in Engineering, ASME JCND, Computers and Fluids,
   Ocean Engineering.

Step 3 matters most for a novelty claim, because the dangerous paper is the
recent one with no citations yet, which is precisely what a citation graph cannot
reach. He 2026 is that shape.

## 4. Retrieval status on the two blocked papers, and why I stopped

**Nihei 2025 corrigendum, `10.1016/j.rineng.2025.107527`. STILL OPEN, and I am
stopping deliberately rather than for lack of routes.** Tried and failed:
`doi.org` (resolves 200 but only to a 2.7 KB redirect stub), ScienceDirect (403),
`linkinghub` (stub only), DOAJ (0 hits for the corrigendum), Unpaywall (lists
only the publisher DOI), OpenAlex (`any_repository_has_fulltext: false`),
Semantic Scholar (points back at the same DOI), Europe PMC (0 hits).

The reason I am not pushing further: the Elsevier landing page carries a
machine-readable text-and-data-mining reservation.

```
tdm-reservation" content="1"
tdm-policy" content="https://www.elsevier.com/tdm/tdmrep-policy.json"
```

That is an explicit publisher opt-out from automated retrieval. Working around it
would be circumventing a stated access control, so the correct route is a human
opening `https://doi.org/10.1016/j.rineng.2025.107527` in a browser, which is
entirely legitimate and takes about a minute. It is CC-BY once open. **Until
someone does that, treat 0.0250 and 0.0242 as provisional.** The current OpenAlex
abstract still carries both values, which is weak evidence they were not what
changed, but it is not proof.

**Zhang 2023, `10.1007/s11433-023-2137-5`. The Pure backend pattern does not
apply here, and I checked rather than assumed.** The pattern works for
Pure-based institutional repositories, which are predominantly EU. This paper is
Springer plus Science China, with Chinese-institution authors, and both OpenAlex
and Unpaywall report `oa_status: closed`, no OA location, and
`any_repository_has_fulltext: false`. There is no repository record to harvest a
numeric file id from, so there is no backend host to try. Tried and failed:
Springer (auth redirect), ADS (empty body), SciEngine (404), Crossref (no
abstract), OpenAlex (no abstract), Europe PMC (0 hits), Semantic Scholar
(TLDR only).

**Consequence, unchanged from unit 3:** the claim that Zhang 2023 validates
code-to-code against two commercial packages rather than against experiment
remains **MEDIUM confidence**, resting on a search-engine rendering of the
publisher abstract plus the Semantic Scholar TLDR. It should not go into the
paper at higher confidence than that without the PDF.

## 5. Escalated, not acted on, and now ANSWERED by D4

The Nihei 2025 brake-state finding, that disengaging the handbrake drops the
effective coefficient by an order of magnitude and moves the critical sliding
velocity by roughly 0.3x at full scale, bears on runs that carry a single
`floor_friction = 0.55` and no representation of brake state. **That is physics
scope and belongs to D4.** Relayed via the board with commit SHA `13f7a2d`. I have
not acted on it, have not touched any solver parameter, and have written no file
outside `docs/R5_RESEARCH_*` and `data/r5_citation_*`.

**D4 answered in `cf9e85c`, and corrected my framing. Recording it here because
it resolves an INFERRED tag I raised.** I wrote in unit 3 section 5c that the
finding "bears on our 16 SLIDE verdicts". The direction makes that the wrong
worry. D4's result:

> Releasing the brake LOWERS effective friction, which INCREASES sliding. A
> verdict that already says SLIDE cannot be undone by making sliding easier. So
> the 16 SLIDE verdicts are robust to brake state and get more robust. Exactly
> one verdict is at risk, sweepV_g64_v0p5, the single STUCK, and it goes
> STUCK -> SLIDE.

So the exposure is the opposite of what I implied: the project's single
reassuring verdict is the one at risk, not its 16 published SLIDEs. D4 also
independently reproduced Nihei's 0.3x factor rather than accepting it, via
`v_crit ~ sqrt(mu)` giving `sqrt(0.0250/0.30) = 0.2887`, and reports the AR&R
mu = 0.30 case as INDETERMINATE rather than overstating it. My physical inference
was directionally right and consequentially wrong; D4's is the one to cite.

## 6. UNVERIFIED list, current

1. **Nihei corrigendum content.** Blocked by a publisher TDM reservation. Needs a
   human browser read. The one genuinely open item.
2. **Zhang 2023 validation method and vehicle scale.** MEDIUM confidence, closed
   access, no OA copy exists anywhere queryable.
3. **He 2026 full text.** Abstract only. Model scale and experimental validation
   are solid from it; whether the paper reports a stability threshold is unknown,
   and that is the axis the proposed L-7 text leans on.
4. **The 16 graph-discovered papers are titles and DOIs, not reads.** None has
   been opened. The count 32 is itself a floor.
5. **The Froude conversion in section 2** is illustrative arithmetic, not a
   similitude analysis.
6. Whether iterating the graph to fixpoint changes the count: not run, one hop
   only.

No project simulation number, force, distance or verdict count is asserted in
this document, so the physics-skeptic gate does not apply. The single inference
about our own runs is in section 5, is tagged, and is escalated rather than acted
on.
