# R5-D1 unit 3: primary-source verdicts on the two threatening papers, plus four closes

Date 2026-08-16. Branch `claude/r5-research`. Follows
`docs/R5_RESEARCH_ELICIT_AND_CATALOG_MINE_2026-08-16.md` and
`docs/R5_RESEARCH_SETTLING_AND_RESOLUTION_MINE_2026-08-16.md`.

Headline: **the proposed L-2 amendment is refuted by the AR&R primary source.
L-2 as written is correct and needs no change.** I proposed it, I tested it, it
failed. Details in section 4.

---

## 1. He et al. 2026, `10.1115/1.4071177`: the validation axis is occupied

*Journal of Computational and Nonlinear Dynamics* 21(6), 061002, 2026. He,
Matthew, Yamashita, Harwood, Swafford, Martin, Grunin, Tison, Jayakumar,
Sugiyama. Full abstract READ DIRECTLY via the Semantic Scholar record.

The authorship matters: this is a University of Iowa (IIHR Hydroscience, Harwood,
Sugiyama) plus US Army DEVCOM GVSC (Tison, Jayakumar) programme, and the same
group authors `10.1115/1.4064971` and `10.1016/j.oceaneng.2022.111607`, both
already in my fording list. This is not a stray paper; it is a sustained research
line on exactly this problem.

Verbatim from the abstract, the two sentences that matter:

> Despite advances in computational approaches for modeling vehicle-fluid
> interactions, only limited studies have been conducted regarding the validation
> of the models in real physical settings. There are few or no experimental data
> available to characterize hydrodynamic loads for the evaluation of transient
> vehicle responses in shallow water.

> Furthermore, the hydrodynamic loads on the model-scale vehicle subjected to
> incoming water flow are measured through flume experiments and used to validate
> the hydrodynamic loads predicted by the simulation model.

**Verdict by axis.**

| axis | overlap | basis |
|---|---|---|
| method | **no** | coupled multibody dynamics plus CFD, plus an LSTM data-driven surrogate. Mesh-based. Ours is MPM, a particle method. Different class. |
| scenario | **yes, strongly** | the abstract names "river crossings and water fording" explicitly. It runs *both* a free-running self-propelled vehicle in a pool *and* a vehicle subjected to incoming flow in a flume. The flume configuration is our stationary-vehicle-in-flow scenario. |
| scale | **no** | model-scale throughout ("a model-scale vehicle"). Ours is full-scale, an 1100 kg Yaris hull. |
| validation | **yes, and this is the problem** | genuine physical experimental validation of a coupled vehicle-water model, in two independent configurations (free-running pool, flume load cells). |

**Consequence for the paper.** CLAUDE.md L-7 records that the novelty is "the
validation step, not the pipeline". He 2026 states the validation gap in its own
words and then fills it, for a coupled vehicle-water interaction model, in 2026.
The project can no longer write that the validation step is unaddressed. What
survives is narrower and still defensible: full scale rather than model scale, a
particle method rather than mesh CFD, and a stability or safety verdict rather
than hydrodynamic load prediction. That sentence has to be written deliberately,
and it must cite He 2026. This is a framing correction, not a refutation of the
work.

## 2. Zhang et al. 2023, `10.1007/s11433-023-2137-5`: the method twin, but it does not validate

*Science China Physics, Mechanics and Astronomy* 66(10), 104711. Zhang H., Li X.,
Feng K., Liu M. (author list READ DIRECTLY from Crossref).

**Access limitation, stated plainly.** This paper is closed access. OpenAlex
reports `oa_status: closed` with no OA location, Unpaywall finds none, Crossref
carries no abstract, and the Springer, ADS and SciEngine routes returned a login
redirect, an empty body and a 404 respectively. I did **not** read the full text
or the abstract directly. What follows rests on the Semantic Scholar TLDR (READ
DIRECTLY) plus a search-engine rendering of the publisher abstract (weaker
source, tagged as such). Treat the validation claim as MEDIUM confidence.

TLDR, read directly:

> the adaptive spatial sort technology can significantly improve the computing
> performance of the GPU-based SPH method and promotes the GPU-based SPH method
> to be a competitive tool for the study of 3D large-scale FSI problems including
> vehicle wading.

Publisher-abstract rendering, weaker source: the verification is "a comparative
study of vehicle wading on a puddle between the GPU-based SPH with two pieces of
commercial software", assessed on "convergence analysis, kinematic
characteristics, and computing performance".

| axis | overlap | basis |
|---|---|---|
| method | **yes, closest of any paper found** | GPU-accelerated 3D SPH. Particle method, GPU, large-scale, vehicle in water. Same family as our GPU MPM. |
| scenario | **partial** | "vehicle wading on a puddle": standing water the vehicle drives into. Ours is a current flowing past a stationary vehicle. |
| scale | unknown | not established from the material I could reach. |
| validation | **no** | code-to-code comparison against two commercial packages, not physical experiment. Subject to the confidence caveat above. |
| output | **no** | FSI behaviour and computing performance. No stability, sliding or floating threshold. |

**Verdict.** Zhang 2023 is the strongest challenge to any claim that a GPU
particle method has not been applied to a vehicle in water, and that claim should
not be made. It does **not** occupy the validation axis and does not produce a
safety verdict, so it does not threaten the contribution the way He 2026 does.

## 3. A sixteenth simulation, catalogued nowhere

`10.1016/j.compfluid.2023.106144`, Lyu, Sun, Huang, Liu, Zha, Zhang, *Computers
and Fluids*, "Numerical investigation of vehicle wading based on an entirely
particle-based three-dimensional SPH model". Note Mou-bin Liu is a co-author of
Zhang 2023 above, so this is the same school.

**It appears in none of the 14 catalogs and is cited nowhere in the repo.** I
found it through a web search while chasing Zhang 2023, not through the corpus.
That is the finding: the catalogs are not a complete census of this literature,
so "not in the catalogs" is not evidence of absence, exactly as "not in
~/Downloads" was not. The fording count is now **at least sixteen**, and I no
longer believe any count derived from the catalogs alone is a ceiling.

## 4. L-2: my proposed amendment is REFUTED. L-2 stands.

I suggested in unit 1 that `10.1111/jfr3.12551` shows `V <= 3.0 m/s` as a stated
component of the stability criterion, and that this might make the cap
vehicle-derived rather than administrative. The coordinator asked me to verify
against the primary source before proposing an amendment. I did. **I was wrong.**

The primary source is already in the repo:
`citations/ARR_Project_10_Stage2_Report_Final.pdf`, Australian Rainfall and
Runoff Revision Project 10, "Appropriate Safety Criteria for Vehicles",
Literature Review, Stage 2 Report P10/S2/020, February 2011. Extracted with
`pdftotext -layout` and READ DIRECTLY. The rationale appears twice, once in the
summary and once in the body:

> These criteria have floating limits of 0.3 m (small passenger vehicles), 0.4 m
> (large passenger vehicles) and 0.5 m (4WD vehicles) to remain in agreement with
> experimental results and all stability criteria have a limiting velocity of
> 3.0 ms-1. **This was incorporated to provide agreement with human stability
> criteria presented within Cox, Shand and Blacka (2010) and to ensure that, in
> the event of vehicle failure, safety was not compromised once people abandoned
> their cars.**

So the 3.0 m/s cap is derived from *human* stability criteria and from occupant
egress after vehicle failure. It is not vehicle-derived. CLAUDE.md L-2 is exactly
right, and no amendment should be made.

What this pass does add, and what I recommend instead of an amendment: L-2
currently asserts the cap is administrative without naming its source. The
primary source names it. If L-2 is ever edited, the useful edit is to attach
**Cox, Shand and Blacka (2010)** and this quotation, upgrading L-2 from an
assertion to a primary-source-verified claim. That is a strengthening, not a
correction. I have not edited `CLAUDE.md`; this is a recommendation only.

**Two further primary-source results from the same PDF, both bonuses.**

**(a) AR&R itself says mu = 0.3 is assumed, and says why it cannot be refined:**

> While the assumed coefficient of friction of µ = 0.3 is likely conservative,
> the present lack of suitable data and wide range of road surfaces and tyre
> tread conditions prohibits the refinement of the coefficient.

This is a stronger source for "0.3 was never measured" than the three Elicit rows
in unit 1, because it is AR&R conceding the point in its own document.

**(b) L-1 is confirmed verbatim:** "Draft, interim criteria for **stationary
vehicle** stability are proposed for three vehicle classes". The criteria are
stationary by construction.

**A units trap worth recording.** Table 3 of the same report gives, for small
passenger cars, a limiting still-water depth of **0.3 m**, a limiting
high-velocity flow depth of **0.1 m**, a limiting velocity of **3.0 m/s**, and
`DV <= 0.3` **m2/s**. The depth limit and the DV limit are both the numeral 0.3
for the small class while being different quantities in different units. Any
find-and-replace or transcription that treats them as one number will silently
corrupt the criterion. Full table as printed:

| class | length (m) | kerb weight (kg) | ground clearance (m) | limiting still-water depth | limiting high-velocity flow depth | limiting velocity | stability equation |
|---|---|---|---|---|---|---|---|
| Small passenger | < 4.3 | < 1250 | < 0.12 | 0.3 | 0.1 | 3.0 | DV <= 0.3 |
| Large passenger | > 4.3 | > 1250 | > 0.12 | 0.4 | 0.15 | 3.0 | DV <= 0.45 |
| Large 4WD | > 4.5 | > 2000 | > 0.22 | 0.5 | 0.2 | 3.0 | DV <= 0.6 |

## 5. Nihei 2025: my inference confirmed, and a result that bears on every SLIDE verdict

`10.1016/j.rineng.2025.107189`. Abstract READ DIRECTLY via OpenAlex.

**(a) The corrigendum is real but its content is unresolved.** Crossref records
`10.1016/j.rineng.2025.107527`, type `erratum`, same seven authors, titled
"Corrigendum to ...". I could not obtain what it corrects: Crossref exposes no
abstract, the article is gold OA but Unpaywall lists only the publisher DOI,
DOAJ returns zero hits for the corrigendum, and the Elsevier routes returned 403.
**Status: OPEN.** Do not treat the numbers below as final until the corrigendum
is read. I note that the current OpenAlex abstract record still carries 0.0250 and
0.0242.

> **CORRECTED, 2026-08-17, after D4 checked this premise rather than inheriting
> it (`7acb95f`).** The phrase this paragraph originally used, "someone with
> publisher access", **overstates the barrier and is withdrawn.** The corrigendum
> is **gold open access, CC-BY, publishedVersion**, re-confirmed live via
> Unpaywall. No institutional access is required. What blocks automated retrieval
> is host-level bot filtering plus the `tdm-reservation`, which is a **fetch**
> status, not a **licence** status. D4's rule is correct and I have adopted it:
> **a licence status and a fetch status are different things, and recording the
> second as the first inflates the blocker.** My own later flag file already had
> this right (`FLAG_BLOCKED_2026-08-17.md` FLAG-1 says "open it in a browser,
> about one minute, CC-BY once open"); this earlier document was never brought
> into line, and it is the one D4 read.

**(b) My unit-1 inference is confirmed by the primary abstract.** I wrote, tagged
INFERRED, that 0.0250 and 0.0242 are rolling resistance and must not be merged
with limiting-friction values near 0.3 to 0.76. The abstract says so explicitly:

> handbrake disengagement reduces the rolling resistance coefficient (=0.0250 and
> 0.0242) by approximately an order of magnitude than the typical static friction
> coefficient (approximately 0.30)

That upgrades unit 1 section 4c from INFERRED to READ DIRECTLY. The paper itself
draws the same contrast I did.

**(c) The result that matters most to this project.** From the abstract's
highlights and body:

> No handbrake reduced effective friction reduced by an order of magnitude.
> Critical sliding velocity approximately 0.3x lower for unbraked vs. braked
> vehicles.

This is a full-scale experimental finding that the **brake state**, not the
vehicle, sets the effective friction, and that it moves the critical sliding
velocity by roughly a factor of three. Our runs carry a single `floor_friction`
of 0.55 with no representation of brake state, and 16 of our 17 canonical
verdicts are SLIDE.

> **DIRECTION CORRECTED by D4 `cf9e85c`.** Releasing the brake *lowers* friction,
> which *increases* sliding, so a SLIDE verdict cannot be undone by it and the 16
> become **more** robust. The run actually at risk is the single STUCK one,
> `sweepV_g64_v0p5`, which goes STUCK to SLIDE. My inference below is
> directionally right and consequentially wrong.

So our SLIDE verdicts implicitly assume a braked vehicle, and
Nihei 2025 is direct experimental evidence that an unbraked one slides at
substantially lower velocity. Tagged INFERRED as to the consequence for our runs;
the experimental result itself is READ DIRECTLY.

This also makes Nihei 2025 the closest experimental analogue to our actual
published result. The abstract notes most prior full-scale work "focused
predominantly on floating instability" whereas this study targets sliding, which
is our dominant mode. It is uncited. I would rank it the single highest-value
citation found in this whole dispatch.

## 6. Row 7 closed: it is 1:24, not 1:10, and there are two different Shahs

`10.11113/JT.V80.11198`, *Jurnal Teknologi* 2018, diamond OA. Abstract READ
DIRECTLY via OpenAlex:

> A stationary die-cast model vehicle (**1:24**) was used with the condition of
> **rear tires being locked only**, positioned at different orientation angles on
> a flat road surface in the partially submerged zone.

So the 0.0168 and 0.0144 m2/s values are 1:24 model scale, stationary, with only
the rear tyres locked. They are not full-scale thresholds and must never sit on
the same axis as 0.30 m2/s.

**The name trap, and it would have produced a wrong number.** Project memory
records "Shah 2018 is 1:10 scale, multiply by 1000 for full scale". Applying that
here would be wrong, because these are two different first authors:

| DOI | year | first author | vehicle | scale |
|---|---|---|---|---|
| `10.11113/JT.V80.11198` | 2018 | Syed **Hamid** Hussain Shah | die-cast model, stationary | **1:24** |
| `10.1051/MATECCONF/201820307003` | 2018 | Syed **Muzzamil** Hussain Shah | Perodua Viva, non-stationary | **1:10** |
| `10.1016/j.rineng.2019.100032` | 2019 | Syed **Muzzamil** Hussain Shah | Perodua Viva, "ensuring similarity laws" | **1:10** |

Both are 2018, both are Shah, both are with Mustaffa and Yusof at the same
institution, and the scales differ. Memory already flags a "Muzzamil/Hamid Shah
name-variant trap"; this is that trap producing a concrete numerical consequence.
Disambiguate by first name, never by "Shah 2018".

**On converting row 7 to full scale.** Under Froude similitude, which is the
standard for free-surface gravity flows, depth scales as the length ratio and
velocity as its square root, so the product DV scales as lambda^1.5. For
lambda = 24 that factor is 117.58, giving 1.98 and 1.69 m2/s. I am **not**
offering those as corrected thresholds. They sit about 6.6x above the AR&R
small-car limit of 0.30 m2/s, which is a strong hint that mass similitude is not
satisfied: a die-cast model is far denser than a scaled real car, and a heavier
model is more stable. The defensible statement is the negative one: row 7 is not
comparable to full-scale thresholds without a similitude argument the paper does
not supply. The lambda^1.5 arithmetic is COMPUTED BY ME and is illustrative only.

This also corrects unit 1, which called row 7 "roughly twenty times below" the
other thresholds. Under Froude the gap is about 118x, not 20x. The direction of
my warning was right, the magnitude was wrong.

## 7. Catalog union: caveat 6 from unit 1 is closed at zero

Unit 1 listed as an open caveat that five catalogs exist as two copies with
different sha256, so a DOI present only in the second copy would be missing from
my 472. Recomputed per copy and unioned: all five pairs have **identical DOI
sets**. The divergences are not bibliographic. Union total is 472, the same
number, and **zero DOIs were missed**. Caveat closed.

## 8. Status

UNVERIFIED and still open:
1. **The Nihei corrigendum content.** Blocked on **automated fetch**, not on
   licence and not on effort: it is gold OA CC-BY (see the correction in section
   5a). Ten routes tried across this dispatch. A browser closes it in about a
   minute.
2. **Zhang 2023's validation method** rests on a search-engine rendering of a
   closed-access abstract, corroborated only by a TLDR. MEDIUM confidence.
   Getting the PDF would settle it.
3. Zhang 2023's vehicle scale is unknown.
4. Whether `10.1016/j.compfluid.2023.106144` overlaps further: abstract not
   exposed by any API I tried.
5. The Froude conversion in section 6 is illustrative arithmetic, not a
   similitude analysis of that experiment.

No project simulation number is asserted anywhere in this document. Every
quantity is an external published value or a verbatim quotation, so the
physics-skeptic gate does not apply. The one inference about our own runs, in
section 5c, is tagged INFERRED and is a statement about interpretation, not a
measurement.
