# R10 web acquisition and gap scan

Slot d22-gapscan, branch `claude/r9-gapscan`, night of 2026-08-19 into 2026-08-20.

Every claim is tagged. **[read]** means I ran the command or read the page.
**[relayed]** means it came from another session or a tool summary and I did not
re-derive it. **[inferred]** means I computed it from something tagged read.

Nothing here was checked by the physics-skeptic subagent, because that path is
still dead fleet-wide. Treat every quantity as UNREVIEWED.

This document was rewritten after a second working pass that went back and
settled the things the first pass had only flagged. Section 5 lists what was
closed and what was not, so the difference is auditable rather than implied.

---

## 1. The numbers, with their complements

### Want list

| source | distinct works | note |
|---|---|---|
| the 21 Undermind deep searches | **230** | [read] top-ranked rows of every search, via the connector, not the index |
| bibliography and register DOIs found in no deep search | **31** | [read] 16 from the two `.bib` files, 21 from register and CLAUDE.md, 6 shared |
| **want list total** | **261** | [inferred] union |

The 230 is not "every paper the searches returned". The 21 searches carry
**1,206 paper slots** [read, summed from each search's own "showing 1-N of M"].
I inspected the top-ranked rows of each, 313 rows, deduplicating to 230 distinct
works. The cut is at relevance rank and is deliberate, not a claim the tail is
empty.

**Measured corroboration of a standing CLAUDE.md claim.** The section "THE
RESEARCH CORPUS IS NOW QUERYABLE FROM INSIDE THE REPO" says the corpus "is NOT a
superset of the bibliography". Measured against the searches themselves rather
than the index: of 33 DOIs across the two bibliography files, **17 appear in some
deep search and 16 appear in none** [read].

### Reachability of the 230

| state | count | complement |
|---|---|---|
| full text reachable by some route | **76** | **154 have no full text by any route I found** |
| Undermind already held a PDF | 52 | |
| confirmed on local disk | 6 | |
| acquired from the web tonight, identity verified | 38 | |
| **net new: readable now, not before** | **22** | |

Sets overlap: 16 of the 38 acquisitions were already readable inside Undermind.
The 22 that were not is the real yield.

### Identity of what was acquired: fully settled

**All 38 valid files are identity-CONFIRMED against their own text** [read], plus
2 files quarantined as wrong. Zero unverified. This is the item the first pass
left open and it is now closed, by `docs/r10/verify_acquired.py` reusing the same
matcher the fetcher uses.

### DOI resolution of the 230

| outcome | count |
|---|---|
| resolved on the first Crossref pass | 181 |
| resolved on the second, multi-route pass and verified on title AND year | 16 |
| resolved by cross-checking the corrections register | 1 (Roy11) |
| **total with a verified identifier** | **198** |
| flagged NEEDS_HUMAN rather than guessed | 4 |
| resolution attempted and rejected as a wrong match | 6 |
| still unresolved by any route | 28 |

### Read

**Four papers read end to end**: Sch19e (10 pp), Zha19e (7 pp), Fou19 (16 pp of
text including all results), and Bau23 read at 13 of 49 pages covering front
matter, the fluid results and the conclusion. **Bau23 is not fully read and this
document does not claim it is.**

Abstract-plus-key-results read for a further six: Xio24, Alq23, Sha21, Zha17c,
Jou20, Gro18. Twenty-eight acquired PDFs remain unread. Acquiring is not reading.

For the **154 with no reachable full text**, what exists is metadata and usually
an abstract. **No claim in this document is sourced from any of them.**

### Barriers, counted from the fetch logs [read]

| barrier | count | what it means |
|---|---|---|
| `closed`, no OA location in Unpaywall | 105 | genuinely paywalled |
| open access but no verified PDF obtainable | ~40 | publisher serves no usable link to a plain client |
| no identifier resolved by any of four routes | 28 | mostly NCAC and TTI vehicle-model reports |

Host distribution of the refusals [read]: ScienceDirect 7, MDPI 6, Wiley 6,
Springer 2, Hindawi 2, Elsevier CDN 2, long tail.

---

## 2. Instruments that were broken, and what replaced them

**WebSearch is dead.** Every call returns `deepseek-ai/DeepSeek-V4-Flash:deepinfra`
[read]. CLAUDE.md records this error for the `physics-skeptic` subagent and the
Agent tool. **It is not subagent-specific**: WebSearch contains no subagent.

**WebFetch is half dead, which is more dangerous.** Its redirect detection is
mechanical and still returns a sensible message, so a call against `doi.org`
looks like the tool works. Its content step runs the same broken model and fails
[read].

**DuckDuckGo silently starts returning zero.** It worked for a few queries then
returned HTTP 200 with an empty result set. Caught only by a control: a query for
`material point method`, which cannot have zero hits, also returned zero [read].
**Four findings collected just before that control are withdrawn, not reported.**

**The arXiv API ignores the query when `sortBy` is set**, returning newest-overall
including radiology and conformal field theory [read]. Five sweeps discarded.
Also `http://export.arxiv.org` drops the query string on redirect; use `https`.

**What replaced them, all working** [read]: plain `curl` plus Crossref, OpenAlex
(`filter=title_and_abstract.search:`, which returns honest zero counts),
Unpaywall, CORE, Semantic Scholar, and OAI-PMH endpoints, which are usually
exempt from the JS bot walls that block the human-facing repository pages.

**And a capability that was there all along.** This Mac has no `pdftotext`, no
numpy and no PyObjC, which is why identity checking was expensive. It does have
**Swift**, so `docs/r10/pdftext.swift` extracts text through PDFKit, handling the
subset-font CMaps that defeat a stdlib zlib extractor. Papers can now be read as
text rather than rendered as page images. That single tool is what made the
second pass possible.

---

## 3. Findings, ordered by what they change

### 3.1 Sch19e does not support the claim it was relayed for

Full working in `docs/r10/schulz2019_image_particles_read.md`. Obtained from
UPCommons (handle 2117/186795, HTTP 200, 3,740,068 bytes, sha256 `a41cc851`)
after the Jülich record FZJ-2019-06605 marked it closedAccess. Every earlier
search missed it because UPCommons stores the title with a typo, "using **imge**
particles" [read].

The wall mechanism is quoted correctly: explicit boundary conditions "distort the
stress multiple grid lengths into the object". Three things stop it carrying the
sphere's +34 to +64 percent:

1. **Wrong part of the stress tensor.** Elastic solid, Hooke's law at Poisson
   ratio 0, and the reported quantity is **von Mises stress**, which is by
   construction blind to the hydrostatic part. A buoyancy force IS that part.
2. **Refinement fixes their artefact.** After a fivefold grid cut, "The stress
   distribution is now correctly modelled inside the object" [read]. Ours
   survives 24 gradings.
3. **Defined for boxes only.** "complex boundaries are not supported, but only
   boxes" [read]. Undefined on a sphere or a hull.

**This adjudicates the board dispute** between d14-corpusbib and d19-priorcode
with no contradiction: a refutation obtained on a curved fluid-immersed body is
evidence about this repo's use of the method, not about the method.

**It bears on question b, not question a.** Explicit boundary conditions "has not
converged after 1000 time steps (0.1 s)"; buffer objects about 250; image
particles about 100 [read]. A tenfold settling difference from boundary treatment
alone.

### 3.2 A falsifier with a hard floor that runs on data already on disk

Bau23 (`10.1002/nme.7217`, CC BY) scores MPM variants against a **theoretical
minimum on the fluid centre of mass**: for an incompressible fluid,
`y_CM >= 2/3 m`, with `y_CM = sum(y_p m_p)/sum(m_p)` [read, their equation 73].

"the SPH-like point adjustment and the 'delta-correction' maintain center of mass
motions consistent with this theoretical minimum, while 'Standard MPM', 'Standard
uGIMP', and the Avoid-a-void algorithm slowly accumulate significant errors"
[read]. Reading their Figure 25A, standard uGIMP ends near 0.40 against the 0.667
bound by t = 10 s.

`rollout.npz` stores every water particle for every frame in all 17 canonical
runs, so this is pure post-processing, no GPU. A falsifier with a hard floor
beats a tolerance.

### 3.3 A caution that lands on the F-bar plan

Commit 754af7f reports the solver "has no locking mitigation at all". Bau23
states the trade-off [read]:

> Smoothing algorithms and reduced quadrature methods commonly used in FEM have
> been shown to overcome this locking phenomenon. However, these approaches
> compound the latter issue producing an unfortunate type of error: aggregation
> of material point tracers and loss of accurate integration of the governing
> equations.

And: "no single approach for mitigating the errors predicted in (52) worked for
all cases" [read]. If F-bar goes in, the centre-of-mass check in 3.2 is the
control that catches the substitution.

Two unswept levers from the same paper: **basis order** ("as the basis function
order increases, all of the MPM methods begin converging"; linear worst, cubic
B-spline nearly fixes it), and Bau23 names **"the particle ringing instability"**
as a distinct MPM error mode, which is distinguishable from d11-accessor's
acoustic ringing at tau_int 1.78 and 2.51 frames, and nobody has distinguished
them.

### 3.4 The in/outflow paper describes this project's tank as what it replaced

Zha19e identity confirmed from the PDF: Zhao, Bolognin, Liang, Rohe, Vardon,
Computers and Fluids, accepted 5 October 2018, implemented in **Anura3D** [read].

1. **It requires adding and removing material points.** The driver holds particle
   count fixed at load. Not a drop-in.
2. **Their well-posedness rule classifies our setup.** "One of the BCs must
   control the kinematics... If neither BCs controls the kinematics, the problem
   is not well-posed" [read]. This project applies a per-frame Dirichlet velocity
   clamp on an upstream slab inside a domain closed by slip walls: kinematic
   control at inflow, no outflow. Momentum is injected every frame into a box
   mass cannot leave.
3. **The reference implementation has the two mitigations this solver lacks**: a
   mixed Gauss algorithm integrating at Gauss points for full elements and at
   material points for partially filled ones, which "leads to smoother stress
   fields", plus explicit "strain and pressure smoothing procedures... to
   mitigate the stress oscillations due to grid crossing" [read].

They also describe what they replaced: large reservoirs that "only approximated
steady conditions and limited the time able to be simulated" [read].

### 3.5 A published still-water pass criterion, and a fix that does NOT port

Full working in `docs/r10/fou19_still_water_read.md`. Fourtakas et al 2019
(`10.1016/j.compfluid.2019.06.009`, CC BY) measure in a still-water tank [read]:

- "the uncorrected density diffusion term shows **a dip in the pressure near the
  wall boundary on the order of 10% of the total pressure**"
- with the correction "the velocity magnitude is **reduced by an order of
  magnitude**" (analytic velocity in a still tank is zero)
- their **Figure 16 is "Kinetic energy evolution time for the 3-D still water
  with pyramid"**, which is exactly this project's question b diagnostic, used as
  a published pass criterion

**The fix does not port, and checking that is the finding.** Read live from the
vendored solver, not assumed: `materials/__init__.py:125` defines a
"Weakly-compressible generalized-Newtonian fluid (EOS + 2 eta dev D)";
`kernels/mpm_utils.py:43` forms `pressure = -bulk * (J^-gamma - 1.0)` and `:53`
assembles `cauchy = id * pressure + 2.0 * eta_app * D_dev`; and a grep for
density diffusion, delta-SPH or artificial viscosity across the whole vendored
tree **returns nothing** [read]. There is no term here to correct.

What transfers is the diagnostic, and the magnitude scale: a boundary defect in a
published SPH code bought 10 percent of total pressure, which is well short of 34
to 64 percent and weakly argues a boundary term alone is not the whole story.

### 3.6 The one bibliography entry that never prints is the closest validated prior art

CLAUDE.md records that the shipped bib has "exactly one entry never cited,
`xiong2024`. BibTeX drops it, so it does not print." Acquired and read [read]:
Xiong, Liang, Zheng, Wang and Tong (2024), Water Resources Research 60,
`10.1029/2023WR036739`, CC BY. Its own key points:

- "A new coupled model for simulation of entrainment, transport and deposition of
  vehicles driven by and interacting with flood hydrodynamics"
- "The model is used to reproduce **a flash flood event that moved over 100
  vehicles, with results consistent with post-event report and survey**"
- "Increasing number of floating vehicles alters flood hydrodynamics"

So the entry the paper carries and never cites is a vehicle-flood model validated
against a real multi-vehicle event. That is a sourcing decision worth making
deliberately rather than by BibTeX default.

### 3.7 A threshold disagreement between two papers by the same group

CLAUDE.md records "Al-Qadami et al 2022 `10.1111/jfr3.12828` separately claim a
first moving full-scale vehicle simulation, with critical depth 0.38 m and
minimum D x V 0.39 m^2/s" [relayed]. Alq23 (`10.3390/su151713262`), acquired and
read [read], reports for a full-scale medium-size passenger vehicle in 3D CFD at
Froude 0.09 to 2.46:

- floating instability "once the flow depth reached **0.38 m**"
- sliding instability "once the depth × velocity threshold function exceeded
  **0.36 m2/s**"
- "the drag force **decreased** with the increment of the Froude number and flow
  velocity"

The depth agrees exactly. **The D x V figure does not: 0.36 against the register's
0.39.** Both come from the same group a year apart. Anyone quoting a D x V
threshold from Al-Qadami should say which paper. The decreasing-drag result also
runs against the intuition behind this project's velocity sweep.

### 3.8 Nobody publishes a vehicle safe-speed surface

Tested against OpenAlex title-and-abstract, on an instrument verified to be
evaluating because neighbouring phrasings returned varied non-zero counts [read]:

| phrasing | works |
|---|---|
| safe speed floodwater vehicle | **0** |
| safe driving speed inundated road | **0** |
| maximum speed vehicle floodwater depth | 1 (road-network disruption) |
| vehicle speed threshold flood stability | 4 (none on point) |
| vehicle stability flood velocity depth threshold | 13, top hit a **stationary** threshold |

The field is threshold and binary. The negative is bounded: OpenAlex
title-and-abstract over six phrasings, not proof of non-existence. The DuckDuckGo
attempt at the same question is withdrawn per section 2.

### 3.9 Recent work no deep search returned

From an OpenAlex sweep filtered to 2024 onward, subtracted against the want list
[read]. **None of these has been read.** They are leads with DOIs.

On locking and oscillation, where 754af7f puts us:
- Reduction of stress oscillations via random grid-shift, `10.1007/s40571-025-01026-8`
- A generalized projection algorithm for volumetric locking in explicit MPM,
  `10.1016/j.compgeo.2025.107391`, a direct successor to Zha22d
- Stabilized explicit MPM for fluid flow and FSI, `10.1016/j.cma.2025.118428`
- Near-incompressibility in higher-order MPM, arXiv `2407.03826`
- Locking mitigation in implicit MPM, `10.1002/pamm.202400033`
- Arbitrary-grid MPM for nonconforming boundary conditions, `10.1002/nme.70054`
- Augmented grid points for MLS-MPM boundaries, `10.2312/egs.20241022`

On the free-surface estimator, the cheapest untested channel:
- A volume-conservation particle shifting scheme for free-surface flows (2024)

On vehicles:
- Floating body motion on shallow water with SPH, `10.3311/ppme.42722`
- "Floodwaters and vehicle hydrodynamics", `10.1016/j.rineng.2024.102540`, a
  third paper in the Results in Engineering series the register already tracks
- "Sand to Mud to Fording", Negrut and Mazhar 2017,
  `10.1007/978-3-319-56397-8_31`, prior-art fording from the same group as Paz14
  and Paz16, in no deep search and no bibliography

---

## 3.10 THE TOOL THIS SLOT BUILT, AND WHY IT MATTERS BEYOND THIS DOCUMENT

**`docs/r10/pdftext.swift`.** Named here with its path at the coordinator's
request, because the constraint it lifts silently shaped the whole night.

This Mac has **no `pdftotext`, no numpy in any interpreter, and no PyObjC**
[read]. Until tonight, the only way to read a paper here was the Read tool
rendering it as page images, at most twenty pages a call. That is expensive
enough that most sessions read abstracts and relayed summaries instead of
reading full text, which is a large part of why so little of this corpus has ever
actually been read.

macOS does ship **Swift**, and PDFKit handles the subset-font CMaps that make a
stdlib zlib extractor return pure garbage. Measured on Bau23: zlib extraction
returns unreadable bytes, PDFKit returns clean text [read]. Usage:

    swift docs/r10/pdftext.swift <file.pdf> [maxPages] [maxChars]

Everything downstream depends on it: identity verification of 40 files, the
quote check in 3.11, the local-tree sweep in 3.12, and reading Fou19's results
without rendering a single page. **A future session should reach for this rather
than rediscovering the constraint.**

One limit, found by using it: **a PDF with no text layer yields only what its
typesetter left extractable.** Sch19e returns 187 characters from page 1, the
running header and title, and no body at all. Identity still verifies, because
the title is in that layer. Quotations do not. See 3.11.

## 3.11 EVERY DIRECT QUOTATION RE-CHECKED AGAINST ITS SOURCE, AND ONE WAS WRONG

Commissioned because a 15 percent wrong-file rate on scraped PDFs conditions
every claim sourced from one. Confirming a file is the right paper is necessary
but not sufficient; the claim that actually matters is that the sentence inside
my quotation marks is in it. `docs/r10/verify_quotes.py` checks the sentence.

Thirty quotations across this slot's documents, matched whitespace- and
ligature-insensitively against the source PDFs [read]:

| outcome | count |
|---|---|
| found in the source | **21** |
| source has no extractable body text, human-read only | **9** (all Sch19e) |
| found to be misquoted | **1**, and it is inside the 21 |

**The misquote, corrected in both documents.** I had written, inside quotation
marks, "the stress distribution now correctly modelled inside the object". The
source reads "**The stress distribution is now correctly modelled inside the
object**". One dropped word, inside quotation marks, in the sentence carrying
reason 2 of three for why Sch19e cannot explain the sphere result. The
*substance* is unaffected, the *quotation* was not exact, and it is now exact.

**The nine that could not be machine-checked are all Sch19e**, and that is an
extraction limit rather than a doubt: I read those pages as rendered images and
re-read page 8 to confirm the wording above. But they are **human-read only, and
not independently re-verifiable by this tooling**, so anyone re-quoting them
should open the page rather than trust this document.

Every other paper passed at 21 of 21, including all five Zha19e quotes, all six
Bau23 quotes and all five Fou19 quotes.

## 3.12 THE LOCAL TREES DO NOT HOLD THE MISSING PAPERS: 0 OF 154

The coordinator asked whether the acquisition plan had been aimed at the wrong
place, by re-running resolution with local trees in the route list, including two
never in this slot's brief. Searched: `~/can-it-ford-refs/` and its dated
subdirectories, `~/Zotero/storage/`, `~/Downloads/vehicle_meshes/` (never
searched before tonight) and
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/`. Pool of **136 PDFs**,
excluding this slot's own downloads, which would be circular [read].

**Result: 0 of the 154 unreachable works are present as the work itself.**

The sweep first reported 3, and all three were false positives that the same
tightening caught: Mil20 and Xia13b both "matched" the Azhar 2023 PDF because
"vehicle", "stability" and "flood" appear in its opening page, and Sci19 matched
a Kramer OES Task 10 **workshop presentation**, which is from the same activity
as the wanted report but is not it [read]. Token overlap cannot separate a paper
from a paper that cites it, so `title_matches` gained a `strict` mode requiring
the match to sit in the title-page region. Under it, 154 of 154 are absent.

**This is a clean negative and it is worth having.** The acquisition effort was
aimed at the right place: the missing works are missing, not mislaid. It also
sharpens the pattern in 3.13, which is about unchecked *records*, not a hidden
library.

## 3.13 THE SAME METHOD FAILURE THREE TIMES IN ONE NIGHT

Stated once, as a finding about method rather than about any one file. Three
times tonight, "we do not have it" turned out to be "we never looked properly at
what we already own":

1. **Kramer 2021** sat at `~/can-it-ford-refs/2026-08-16/` with a full
   `PROVENANCE.txt` since 16 August, while three separate passes called it the
   most valuable unretrieved item [relayed, and the file verified present here].
2. **d15 found 35 comparable long records already on Vista** when a claim was
   believed to need new runs [relayed].
3. **Roy11's DOI, `10.1016/j.cma.2011.03.016`, is recorded in this project's own
   corrections register**, and this project's own resolver reported the work
   unfindable. I then published "49 works carry no DOI" on the strength of that
   [read, mine].

The common shape is not a missing library, which 3.12 rules out. It is that the
project's own records were not consulted before an external search was declared
to have failed. **Cheap standing fix: before recording any work as unobtainable,
grep the register and `~/can-it-ford-refs/` for its title and DOI.** That single
step would have caught all three.

## 3.14 RE-AIMING, GIVEN THAT THE ACCESSOR QUESTION SETTLED THE OTHER WAY

[relayed from the coordinator, 2026-08-20, and **explicitly flagged as under
adversarial review at the time it was relayed**: whether the two readings are
genuinely independent or two readings of the same corrupted fluid state has not
returned. Treat as strong but unreviewed. I did not re-derive any of it.]

A third accessor, `control_volume_force`, reads `cauchy()` and `vol()` only and
agrees with `sdf_wrench` to 0.9 to 1.9 percent across three boxes. The instrument
is exonerated, so **the fluid really is pushing about 1.35x analytic**, the bulk
pressure field is hydrostatic, and the disturbance is confined to the bottom
boundary.

That changes what this slot should have been acquiring, and I am recording the
correction rather than leaving the section 3 ordering to imply otherwise:

- **Section 3.1 gets stronger, for a second and independent reason.** I ruled
  Sch19e out because it measures von Mises stress and refines away. If the bulk
  field is hydrostatic and the disturbance sits at the floor, then a mechanism
  reaching "multiple grid lengths into the object" is doubly the wrong shape:
  the object is not where the problem is.
- **Section 3.5 becomes the most on-target thing I acquired, not a near miss.**
  Fou19's measured defect is *specifically* a pressure dip **near the wall
  boundary** in a **still-water tank**, which is exactly "the fluid is wrong near
  a floor". Its 10 percent is still well short of 35 percent, so it does not
  close the gap, but it is the right family and it is measured.
- **Section 3.4 gains a second reading.** Zha19e's well-posedness point was
  filed under question b. If the disturbance is at the bottom boundary, then a
  domain with kinematic control at inflow and no outflow, closed by slip walls,
  is a statement about where momentum accumulates, not only about settling.
- **What should be acquired next is narrower than what I was acquiring.** Not
  force-extraction papers, and not general locking. Papers on **wall and floor
  boundary treatment for weakly compressible particle methods with a free
  surface**, measured at the boundary. From my own want list that is Ada12,
  Val15b, Mon09, Tao21b and Mar10b, five of which are closed and none of which I
  obtained. From section 3.9 it is `10.1002/nme.70054`, arbitrary-grid MPM for
  nonconforming boundary conditions, and `10.2312/egs.20241022`, augmented grid
  points for MLS-MPM boundaries.

**I then tried to acquire those five, serially, and got none of them.** Barriers
established per paper by two independent sources, Unpaywall/OpenAlex and
Semantic Scholar's `isOpenAccess` [read]:

| paper | DOI | barrier |
|---|---|---|
| Ada12, generalized wall BC for SPH | `10.1016/j.jcp.2012.05.005` | closed, both sources agree |
| Val15b, solid wall models for WCSPH | `10.1016/j.jcp.2015.07.033` | closed, both sources agree |
| Mar10b, free-surface detection and level set | `10.1016/j.jcp.2010.01.019` | closed, both sources agree |
| Tao21b, semi-fixed ghost particle boundary | `10.3390/jmse9040416` | **nominally gold OA**, MDPI returns 403 to every client I have, with and without a Referer, versioned and unversioned |
| Mon09, SPH particle boundary forces | `10.1016/j.cpc.2009.05.008` | S2 lists an OA copy, but the figshare record `22986665` is a **metadata-only stub with no files attached** |

Three are genuinely paywalled. Two are recorded as open and are not actually
retrievable by any route available here. **Tao21b is the one worth a human
minute**: it is gold OA in a fully open MDPI journal and a browser will almost
certainly download it where curl cannot.

Separately [relayed, d23-overleaf]: the paper falls back on displacement
magnitude as its safe quantity, and that quantity is unconverged, falling on both
resolution legs at 2337 kg while rising then falling at 1100 kg, so the sign of
the resolution effect is not consistent across masses. Nothing I acquired bears
on that; recorded so it is not lost.

---

## 4. Method failures, mine included

**Filenames lie, embedded metadata lies, and they lie in opposite directions.**
`Downloads/1909.04504v3.pdf` looks like an arXiv id for Lastiwka 2009 and is
PySPH: a false positive. The file for Sha21 carries the embedded title
"APPLICATION OF DIGITAL CELLULAR RADIO FOR MOBILE LOCATION ESTIMATION" and page 1
proves it is the correct Froude-number paper: a false negative [read, both].
Only the page settles it, which is why `pdftext.swift` exists.

**My first disk matcher was wrong and its number is withdrawn: do not cite 156 of
230.** An unquoted Spotlight probe is an OR over its words. Sch19e alone "matched"
108 files and its top hit was a different paper [read]. Quoted, candidates fall to
30, of which 26 are the title sitting inside some other document. Verified figure
is **6**.

**My fetcher saved two wrong files, and one heuristic caused both.** The JCGM
metrology vocabulary was filed as Gro18, and a website Terms and Conditions page
as Arr19 [read]. Cause: when a landing page carries no `citation_pdf_url`, the
scraper fell back to the first `.pdf` anchors, which can be a cited or supporting
document. Two wrong out of thirteen scraped, a 15 percent error rate. Both are
renamed `WRONG-FILE_*` rather than deleted so the failure stays visible.

**My "49 works carry no DOI" was withdrawn.** 11 are the NCAC and TTI reports I
claimed, about 10 are agent preprints Crossref does not index, and the rest are
ordinary journal papers my query missed. The clearest case is Roy11, whose DOI
`10.1016/j.cma.2011.03.016` **is already in the corrections register** and which
Crossref confirms is the right paper [read].

**Then my fix over-corrected twice, both from text normalisation.** A strict
matcher rejected Mar19b because "vehículos" and "numérico" lose accents
differently on the two sides, and Eca20 because Crossref returns "V&amp;V 20"
where the want list has "V&V 20". Both are the same paper. NFKD accent stripping
and HTML entity decoding recover both. **A threshold that looks strict is not the
same as a comparison that is correct.**

**And token overlap alone is not sufficient in this corpus.** Six automated
resolutions were false matches sharing domain vocabulary: Neg22b matched to a
1984 AIAA compressible-flow paper, Mcc03 to a 1995 SAE paper, Kam06 to a RANS
turbulence paper sharing only "Method of Manufactured Solutions", and Paz16 to
"Sand to Mud to Fording", a real paper but a different one. Adding a publication
year test caught all six [read].

---

## 5. What was settled on the second pass, and what was not

**Settled:**

| problem | how it was closed |
|---|---|
| identity of acquired files unverified | `pdftext.swift` plus `verify_acquired.py`: **38 of 38 CONFIRMED**, 2 quarantined |
| the scraper could save a wrong file | `fetch_verified.py` writes to a temp path, reads the file's own text, and keeps it **only if the title matches**; unit-tested 6 of 6 including both known wrong files |
| a second wrong file was still in the set | found (Arr19) and quarantined |
| Gro18 was missing its real paper | re-fetched; the verifier **rejected the JCGM document twice** at token overlap 0.12, then kept the correct LiveCoMS paper |
| "49 works carry no DOI" | withdrawn; 17 now resolved and verified on title and year, 4 flagged NEEDS_HUMAN, 6 rejected, 28 genuinely unresolved |
| open-access residue unfetched | fifth pass run; recovered Zha17c, Jou20 and the correct Gro18, all verified |
| WebSearch, WebFetch, DuckDuckGo, arXiv `sortBy` | diagnosed, documented, and replaced by working API routes |
| `data/r10_acquired/` is gitignored | settled by mirroring every manifest into `docs/r10/`, which is tracked |
| were the missing papers actually on local disk? | swept 136 PDFs across 4 trees including two never in my brief: **0 of 154**, so the acquisition effort was aimed at the right place |
| do my quotations actually appear in the sources? | 21 of 21 machine-checkable found, **1 misquote caught and corrected**, 9 unverifiable because Sch19e has no body text layer |
| my matcher false-positived on same-domain papers | `title_matches` gained a `strict` mode requiring the match in the title-page region; it rejects Mil20/Xia13b against the Azhar PDF and keeps Azh23 |
| two verifiers disagreeing about the same file | `verify_acquired.sh` retired in favour of `verify_acquired.py`, which imports the fetcher's matcher, so there is one source of truth |

**Not settled, and why:**

- **The Chrome extension is not connected**, so JS-walled repositories such as
  JuSER stay unreachable through a browser. Worked around via OAI-PMH for the one
  case that mattered; not fixable from here.
- **The physics-skeptic path is still dead.** Everything here is UNREVIEWED.
- **105 works are genuinely paywalled** and need institutional access, not a
  better script. That includes Che18c, Mar10b, Ada12, Yan18 and Val15b, five
  papers sitting directly on question a, and the He26d / Was15 / Kha14 / Paz16
  prior-art fording cluster the paper cites none of.
- **28 works resolve to no identifier**, mostly NCAC and TTI vehicle-model
  reports bearing on question f. These come from the issuing body's own site, per
  report, by hand.
- **28 acquired PDFs are unread.** Now cheap to read as text, but not read.
- **Bau23 is read at 13 of 49 pages.**
- **A safe-speed surface does not exist to be acquired** (section 3.8). That is
  the one result arguing for generating data rather than fetching it.
- **Nine Sch19e quotations are human-read only.** That PDF has no extractable
  body text, so this tooling cannot re-check them. Open the page before
  re-quoting.
- **The re-aim in 3.14 is not acted on.** The accessor exoneration says the
  fluid is wrong near a floor, which makes floor and wall boundary treatment for
  weakly compressible free-surface particle methods the right target. The five
  want-list papers that sit there (Ada12, Val15b, Mon09, Tao21b, Mar10b) are all
  closed and none was obtained. That is the single most on-target unfinished
  acquisition.

---

## 6. Files

In the repo:
- `docs/R10_WEB_ACQUISITION_2026-08-19.md`, this file
- `docs/r10/schulz2019_image_particles_read.md`, full Sch19e working
- `docs/r10/fou19_still_water_read.md`, full Fou19 working
- `docs/r10/want_list_deep_searches.tsv` and `_resolved.tsv`, the 230
- `docs/r10/stragglers_resolved.tsv` and `stragglers_judged.tsv`, the 49
- `docs/r10/disk_resolution.tsv` (the withdrawn OR-matched pass, kept as evidence)
  and `disk_verified.tsv`
- `docs/r10/acquired_verified.tsv`, identity of all 40 files
- `docs/r10/pdftext.swift`, the PDFKit extractor everything else depends on
- `docs/r10/fetch_verified.py`, the fetcher that cannot save an unverified file
- `docs/r10/verify_acquired.py`, `resolve_stragglers.py`, `scan_new.py`,
  `resolve_oa.py`, `fetch_oa.sh`, `fetch_unpaywall.py`, `fetch_priority.py`,
  `fetch_all_oa.py`, `resolve_disk.sh`
- `docs/r10/*.log` and `*_manifest.tsv`, every attempt with HTTP code and bytes

Outside the repo, deliberately, because `can-it-ford` is public and licence
question E8 is unresolved:
- `~/can-it-ford-refs/2026-08-19-r10/`, 38 verified PDFs, 2 quarantined wrong
  files kept as evidence, and `PROVENANCE.txt`
