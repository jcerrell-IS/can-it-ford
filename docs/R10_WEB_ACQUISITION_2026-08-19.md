# R10 web acquisition and gap scan

Slot d22-gapscan, branch `claude/r9-gapscan`, night of 2026-08-19 into 2026-08-20.

Every number below is tagged. **[read]** means I ran the command or read the page.
**[relayed]** means it came from another session or a tool summary and I did not
re-derive it. **[inferred]** means I computed it from something tagged read.

Nothing in this document was checked by the physics-skeptic subagent, because
that path is still dead fleet-wide. Treat every quantity as UNREVIEWED.

---

## 1. The numbers, with their complements

### Want list

| source | distinct works | note |
|---|---|---|
| the 21 Undermind deep searches | **230** | [read] top-ranked rows of every search, inspected via the connector, not via the index |
| bibliography and corrections register DOIs found in no deep search | **31** | [read] 16 from the two `.bib` files, 21 from the register and CLAUDE.md, 6 shared |
| **want list total** | **261** | [inferred] union |

The 230 is not "every paper the searches returned". The 21 searches return **1,206
paper slots** in total [read, summed from each search's own "showing 1-N of M"
line]. I inspected the top-ranked rows of each, 313 rows, which deduplicate to
230 distinct works. Everything below 230 is a deliberate cut at relevance rank,
not a claim that the tail is empty.

**A measured corroboration of a standing CLAUDE.md claim.** The section "THE
RESEARCH CORPUS IS NOW QUERYABLE FROM INSIDE THE REPO" says the corpus "is NOT a
superset of the bibliography." Measured live tonight against the searches
themselves rather than the index: of 33 DOIs in the two bibliography files,
**17 appear in some deep search and 16 appear in none** [read]. The claim holds,
and now has a number derived from the searches directly.

### Reachability of the 230

| state | count | complement |
|---|---|---|
| full text reachable by some route | **68** | **162 have no full text by any route I found** |
| of which, Undermind already held a PDF | 52 | |
| of which, confirmed on local disk | 6 | |
| of which, I acquired from the web tonight | 28 | |
| **net new: works readable now that were not before** | **14** | |

The three sets overlap: 14 of my 28 acquisitions were already readable inside
Undermind, and I fetched them anyway before checking, which was wasted effort.
The 14 that were not is the real yield.

### Read in full

**4 papers read end to end tonight**, by me, from the PDF:

- Sch19e, Schulz and Sutmann 2019, image particles (10 pp)
- Zha19e, Zhao et al 2019, in/outflow BCs (7 pp, the accepted manuscript)
- Bau23, Baumgarten and Kamrin 2023, spatial integration errors (13 of 49 pp:
  front matter, the fluid results, and the conclusion. **Not the full 49**, so
  do not describe this one as fully read)
- Sha21, Shah et al 2021, Froude number variance (1 p, read only to settle an
  identity dispute, see section 4)

24 further PDFs were acquired and are on disk unread. Acquiring is not reading
and this report does not conflate them.

### Reached as abstract only

**222 of the 332 corpus records carry an abstract and 110 do not** [relayed,
from CLAUDE.md; not re-derived tonight]. Within my 230, the honest statement is
that for the **162 with no reachable full text**, what exists is the title, the
bibliographic metadata, and in most cases an abstract. **No claim in this
document is sourced from any of them.**

### Could not reach at all, with the barrier

Of the 230, OpenAlex classifies **105 as `closed` with no open-access location
of any kind** [read]. A further **49 never resolved to a DOI at all** [read],
which is a different barrier: these are mostly NCAC and TTI vehicle-model
reports, SAE papers, and older conference proceedings that carry no DOI.

Barriers actually hit, counted from the fetch logs [read]:

| barrier | count | what it means |
|---|---|---|
| `closed`, no OA location in Unpaywall | 105 | genuinely paywalled |
| no DOI resolvable from the title | 49 | grey literature, reports, proceedings |
| OA status but publisher host refused a plain client | 57 | 403 or an HTML wall; see below |
| repository returned HTML, no PDF behind it | included above | landing page with no file |

The 57 is the interesting failure. These works ARE open access, and Unpaywall
names a location, but the location is a publisher endpoint that refuses a bare
HTTP client. Measured host distribution of the refusals [read]: ScienceDirect 7,
MDPI 6, Wiley 6, Springer 2, Hindawi 2, Elsevier CDN 2, and a long tail. My
third pass recovered 8 of the 24 shortlisted ones by scraping the landing page
for a `citation_pdf_url` and re-requesting with a Referer header. The same trick
would probably recover a good share of the remaining 49, and that is the single
highest-yield unfinished job here.

---

## 2. Two instruments were dead and one was lying

**WebSearch is dead, with the same error that killed the Agent path.** Every
call returns `deepseek-ai/DeepSeek-V4-Flash:deepinfra` [read, twice]. CLAUDE.md's
section "THE ADVERSARIAL REVIEW PATH IS DEAD FLEET-WIDE" records this for the
subagent path only. **It is not subagent-specific.** WebSearch has no subagent
in it.

**WebFetch is half dead, which is worse than fully dead.** Its redirect
detection is mechanical and still works, so a call against `doi.org` returns a
plausible-looking redirect notice. Its actual content step runs the same broken
model and fails [read]. A session that only ever hits redirects would conclude
WebFetch works.

Everything in this document was therefore fetched with `curl` and read by me.

**DuckDuckGo silently starts returning zero results.** It worked for the first
few queries and then returned HTTP 200 with an empty result set. I only caught
it because I ran a control: a query for `material point method`, which cannot
have zero hits, also returned zero [read]. Four "no results" findings collected
just before that control are **withdrawn**, not reported. This is the failure
mode already recorded in memory as "Both arms failed, reported as agreement".

**The arXiv API silently ignores the query when `sortBy` is set.** Five sweeps
returned the newest arXiv papers overall, including radiology and conformal
field theory, rather than matches [read]. Those five sweeps are discarded. Also,
`http://export.arxiv.org` drops the query string on redirect; use `https`.

---

## 3. Findings, ordered by what they change

### 3.1 The paper this slot was sent to get does not support the claim it was relayed for

Full working in `docs/r10/schulz2019_image_particles_read.md`. Sch19e was
obtained from UPCommons (handle 2117/186795, HTTP 200, 3,740,068 bytes, sha256
`a41cc851`) after the Julich record FZJ-2019-06605 marked it closedAccess.
Every title search had missed it because UPCommons stores the title with a typo,
"using **imge** particles" [read].

The wall mechanism is real and was quoted correctly: explicit boundary
conditions "distort the stress multiple grid lengths into the object". Three
things in the paper stop it carrying the sphere's +34 to +64 percent:

1. **The measured quantity is the wrong part of the stress tensor.** The paper's
   material is an elastic solid under Hooke's law at Poisson ratio 0, and it
   reports **von Mises stress**, which is by construction blind to the
   hydrostatic part. A buoyancy force IS the hydrostatic part.
2. **Refinement fixes their artefact.** Cutting the grid width fivefold leaves
   "the stress distribution now correctly modelled inside the object" [read].
   Ours survives 24 gradings.
3. **The method is defined for boxes only.** The authors state that
   anti-symmetry "can only be satisfied for a perpendicular plane. Therefore,
   complex boundaries are not supported, but only boxes" [read]. It is undefined
   on a sphere or a hull.

**This adjudicates the board dispute** between d14-corpusbib, who flagged the
paper, and d19-priorcode, who reports `simulation/image_particles.py` refuted.
Both are correct and there is no contradiction: a refutation obtained on a
curved fluid-immersed body is evidence about this repo's use of the method, not
about the method, because the published method does not claim that domain.

**What it does bear on is question b, not question a.** Time to steady state,
read directly: explicit boundary conditions "has not converged after 1000 time
steps (0.1 s), with the main change still occurring in the boundary region";
buffer objects about 250 steps; image particles about 100. A tenfold settling
difference produced by boundary treatment alone, in a solver whose hydrostatic
column never goes quiet and whose boundaries are explicit.

### 3.2 Baumgarten and Kamrin give a cheap falsifier that runs on data already on disk

Bau23 is CC BY and freely redistributable. Their dam-break case scores MPM
variants against a **theoretical minimum on the centre of mass**: for an
incompressible fluid, `y_CM >= 2/3 m` set by the rest configuration, with
`y_CM = sum(y_p m_p) / sum(m_p)` [read, their equation 73].

Their result: "the SPH-like point adjustment and the 'delta-correction' maintain
center of mass motions consistent with this theoretical minimum, while 'Standard
MPM', 'Standard uGIMP', and the Avoid-a-void algorithm slowly accumulate
significant errors" [read]. Reading their Figure 25A, standard uGIMP falls to
roughly 0.40 against the 0.667 bound by t = 10 s, so it ends about 40 percent
BELOW a bound it cannot physically cross.

**This is directly runnable here with no GPU.** `rollout.npz` stores every water
particle for every frame in all 17 canonical runs. Computing `y_CM` per frame
and comparing against the rest-configuration bound is pure post-processing. It
is a falsifier with a hard floor, which is rarer and better than a tolerance.

### 3.3 A caution that lands squarely on the F-bar plan

Commit 754af7f on this branch reports the solver "has no locking mitigation at
all, and its fluid update is the exact line F-bar replaces". Bau23 states the
trade-off explicitly [read]:

> Smoothing algorithms and reduced quadrature methods commonly used in FEM have
> been shown to overcome this locking phenomenon. However, these approaches
> compound the latter issue producing an unfortunate type of error: aggregation
> of material point tracers and loss of accurate integration of the governing
> equations.

And their conclusion: "no single approach for mitigating the errors predicted in
(52) worked for all cases" [read]. So adopting an anti-locking fix alone can
trade a locking error for a quadrature error. If F-bar goes in, the centre-of-mass
check in 3.2 is the control that would catch the substitution.

Two further levers from the same paper, neither swept here:
- **Basis order.** "as the basis function order increases, all of the MPM
  methods begin converging" to the reference [read]. Linear elements are worst;
  cubic B-splines nearly fix it.
- **Named pathology.** Bau23 names "the particle ringing instability" as a known
  MPM error mode [read]. d11-accessor measured ringing with tau_int 1.78 and
  2.51 frames and attributed it to acoustics. Those are distinguishable, and
  nobody has distinguished them.

### 3.4 The in/outflow paper says this project's tank is the configuration it was written to replace

Zha19e identity confirmed from the PDF: Zhao, Bolognin, Liang, Rohe, Vardon,
Computers and Fluids, accepted 5 October 2018, implemented in **Anura3D** [read].
Three things bear directly on this project:

1. **It requires adding and removing material points.** The project's driver
   holds particle count fixed at load and creates or destroys nothing. Adopting
   this BC breaks that invariant; it is not a drop-in.
2. **Their well-posedness rule classifies our setup.** "One of the BCs must
   control the kinematics... If both the inflow and outflow conditions control
   kinematics, physically impossible situations may arise... If neither BCs
   controls the kinematics, the problem is not well-posed" [read]. This project
   applies a per-frame Dirichlet velocity clamp on an upstream slab inside a
   domain closed by slip walls: kinematic control at inflow, and no outflow at
   all. Momentum is injected every frame into a box mass cannot leave. That is a
   candidate mechanism for a column that never goes quiet.
3. **The reference implementation has the two mitigations this solver lacks.**
   Anura3D uses a mixed Gauss algorithm, integrating "at the elements' Gauss
   point locations for fully filled element, and at material points for
   partially filled elements, e.g. at fluid surfaces", which "leads to smoother
   stress fields", plus explicit "strain and pressure smoothing procedures... to
   mitigate the stress oscillations due to grid crossing" [read]. The canonical
   MPM open-channel implementation in the literature differs from ours in
   exactly the two places that govern pressure oscillation.

They also state what they replaced: large reservoirs that "only approximated
steady conditions and limited the time able to be simulated" [read]. That is a
description of this project's tank.

### 3.5 Nobody publishes a vehicle safe-speed surface, measured with a working instrument

CLAUDE.md and memory both carry the belief that `v_max(depth, flow_velocity)` is
the open gap. Tested tonight against OpenAlex title-and-abstract search, which
was verified to be evaluating properly by returning varied non-zero counts on
neighbouring phrasings [read]:

| phrasing | works |
|---|---|
| safe speed floodwater vehicle | **0** |
| safe driving speed inundated road | **0** |
| maximum speed vehicle floodwater depth | 1 (road-network disruption, not a vehicle) |
| vehicle speed threshold flood stability | 4 (none on point) |
| vehicle stability flood velocity depth threshold | 13, top hit Mar17, a **stationary** threshold |

The literature is threshold and binary, expressed as stability curves for a
stationary or towed vehicle. The negative holds, and it is now bounded: this is
OpenAlex title-and-abstract over six phrasings, not a proof of non-existence.
The DuckDuckGo attempt at the same question is withdrawn per section 2.

### 3.6 Recent work the project's own searches never returned

From an OpenAlex sweep filtered to 2024 onward and subtracted against the want
list [read]. Highest relevance to open question a first:

- **Reduction of stress oscillations in the material point method based on the
  random grid-shift technique** (2025), `10.1007/s40571-025-01026-8`, hybrid OA.
- **A generalized projection algorithm for overcoming volumetric locking in
  explicit material point methods** (2025), `10.1016/j.compgeo.2025.107391`.
  A direct successor to Zha22d, which is already a live candidate mechanism.
- **Stabilized explicit material point method for fluid flow and
  fluid-structure interaction simulations** (2025), `10.1016/j.cma.2025.118428`.
  Explicit MPM, fluid, FSI, stabilisation: the exact intersection.
- **Treatment of near-incompressibility and volumetric locking in higher order
  material point methods** (2024), arXiv `2407.03826`.
- **Mitigation Techniques for Volumetric Locking in the Implicit Material Point
  Method** (2024), `10.1002/pamm.202400033`, hybrid OA.
- **An Efficient Arbitrary Grid Material Point Method for Problems With
  Nonconforming Boundary Conditions** (2025), `10.1002/nme.70054`, bronze OA.
- **Accurate Boundary Condition for Moving Least Squares Material Point Method
  using Augmented Grid Points** (Toyota and Umetani, Eurographics 2024),
  `10.2312/egs.20241022`.
- **A volume-conservation particle shifting scheme for moving particle method
  simulating free-surface flows** (2024). Same family as the delta-correction
  in 3.2.
- **Smoothed particle hydrodynamics for free-surface and multiphase flows: a
  review** (2025), `10.1088/1361-6633/ada80f`, 31 citations.
- **Reconstruction of 3D Floating Body Motion on Shallow Water Flows Using SPH**
  (2026), `10.3311/ppme.42722`, diamond OA. Floating body, shallow water, SPH.
- **Floodwaters and vehicle hydrodynamics: a deep dive into risk mitigation
  unravelling vehicle stability** (2024), `10.1016/j.rineng.2024.102540`, gold OA.
  Third paper in the Results in Engineering series the register already tracks.
- **Sand to Mud to Fording** (Negrut and Mazhar 2017),
  `10.1007/978-3-319-56397-8_31`. Prior-art fording simulation from the same
  group as Paz14 and Paz16, in no deep search and in no bibliography.

None of these has been read. They are leads with DOIs, not results.

---

## 4. Method notes that cost me real time, so they are worth carrying

**Filenames lie, and so does embedded PDF metadata, in opposite directions.**
`Downloads/1909.04504v3.pdf` looks like an arXiv id for Lastiwka 2009 and its
embedded title is "PySPH: a Python-based framework for smoothed particle
hydrodynamics", a different paper: a **false positive** [read]. In the other
direction, the file I fetched for Sha21 carries the embedded title "APPLICATION
OF DIGITAL CELLULAR RADIO FOR MOBILE LOCATION ESTIMATION", which is stale
journal-template metadata; reading page 1 shows it IS the correct Froude-number
paper: a **false negative** [read]. Neither the name nor the metadata is
sufficient. Only the page is.

**My first disk matcher was wrong and its number is withdrawn.** An unquoted
Spotlight probe is an OR over the words, so it reported **156 of 230 present on
disk**. Sch19e alone "matched" 108 files and its top hit was a different paper
[read]. Quoting the probe makes Spotlight do phrase matching and the candidate
count falls to 30, of which 26 are the title appearing inside some OTHER
document: this project's own paper, the research dossier, or another paper's
reference list. **Do not cite 156.** The verified figure is 6, and it is a lower
bound because of the metadata false negatives above.

**A reference store already exists outside the repo and it was not in my brief.**
`~/can-it-ford-refs/` holds dated directories with a `PROVENANCE.txt` recording
the exact URL, HTTP code, byte count and every URL that failed first. It was set
up deliberately because "the repo is PUBLIC and E8 is unresolved". I followed
that convention rather than my instructions, see section 5.

---

## 5. One deliberate deviation from the brief, and one blocked path

**PDFs went to `~/can-it-ford-refs/2026-08-19-r10/`, not `data/r10_acquired/`.**
Reason: `can-it-ford` is a public GitHub repo, licence question E8 is
unresolved, and most of these 28 files are publisher PDFs that are free to read
but not free to redistribute. Committing them would republish them worldwide and
permanently. An earlier slot reached the same conclusion and built
`~/can-it-ford-refs/` for it. The manifests and provenance are in the repo; the
bytes are not. This is reversible: the CC BY subset, Bau23 among them, could be
moved in deliberately if someone decides to.

**`data/r10_acquired/` cannot be tracked anyway.** `data/*` is gitignored,
re-derived live rather than cited by line number [read]. Anything written there
is invisible to git. The manifests are therefore mirrored into `docs/r10/`,
which is tracked. The assigned write scope named a path the repo cannot record.

---

## 6. What is still missing, and what it would take

Ordered by value per unit effort.

1. **The 49 open-access works whose publisher host refused a plain client.**
   These are already known to be free. The landing-page scrape plus Referer
   trick in `docs/r10/fetch_priority.py` recovered 8 of 24 on the shortlist; run
   it over the rest. Half a session, no GPU, no new tooling.

2. **The 13 deep searches that have never been ingested into the index.**
   21 searches exist and 8 are in `data/research_corpus_index.json` [relayed
   from CLAUDE.md and the board; I read the 21 live but did not audit which 8].
   I worked from the connector directly, so this report is not limited by that
   gap, but every other slot's corpus queries are.

3. **Che18c, Mar10b, Ada12, Yan18, Val15b.** Five closed papers that sit
   directly on question a: weakly-compressible MPM pressure oscillation, SPH
   free-surface detection and level sets, and wall boundary conditions. The
   level-set one, Mar10b, is the one that bears on the denominator hypothesis,
   which is the cheapest of the three candidate explanations to test. Route:
   interlibrary loan, or a UT Austin proxy, neither of which I have.

4. **He26d, Was15, Kha14, Paz16.** The prior-art fording cluster that
   `paper/` cites none of. All closed. He26d is ASME, Was15 is ASME DETC, Kha14
   is SAE, Paz16 has no DOI at all. These need institutional access, not a
   better script.

5. **The 49 want-list entries with no DOI.** Mostly NCAC and TTI vehicle-model
   reports bearing on question f, the mesh licence question. These are usually
   free from the issuing body's own site rather than from any aggregator, so the
   route is per-report, by hand.

6. **A safe-speed surface does not exist to be acquired.** Section 3.5 is a
   negative, and it is the one result here that argues for generating data
   rather than fetching it. The project's repeat distributions are the right
   ingredient and nobody else has published the surface.

7. **Adversarial review of everything above.** Still unavailable. Every number
   in this document is UNREVIEWED.

---

## 7. Files

In the repo:
- `docs/R10_WEB_ACQUISITION_2026-08-19.md`, this file
- `docs/r10/schulz2019_image_particles_read.md`, the full Sch19e working
- `docs/r10/want_list_deep_searches.tsv`, 230 works with source search and PDF state
- `docs/r10/want_list_deep_searches_resolved.tsv`, plus DOI, OA status, licence
- `docs/r10/disk_verified.tsv`, the 30 disk candidates and their verdicts
- `docs/r10/resolve_oa.py`, `fetch_oa.sh`, `fetch_unpaywall.py`,
  `fetch_priority.py`, `scan_new.py`, `resolve_disk.sh`, `verify_disk_matches.sh`
- `docs/r10/*.log`, every fetch attempt with its HTTP code and byte count

Outside the repo, deliberately:
- `~/can-it-ford-refs/2026-08-19-r10/`, 28 PDFs, 143 MB
