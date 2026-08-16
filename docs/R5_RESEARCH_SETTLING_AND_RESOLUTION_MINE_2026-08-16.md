# R5-D1 unit 2: the two catalogs nobody mined

Date 2026-08-16. Branch `claude/r5-research`. Follows
`docs/R5_RESEARCH_ELICIT_AND_CATALOG_MINE_2026-08-16.md`.

The dispatch names two catalogs as read-as-summary-only:
`Settling and Force Reporting in Free Surface Flow` (68 papers, 53 DOIs) and
`Multi-resolution MPM for Large-domain Flooding` (78 papers, 73 DOIs). Both are
at `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/01_Solver_Physics_and_Coupling/`,
dated 2026-08-14, `_CURRENT`.

**What was already known, and is not restated as new.** Project memory records
four negative results from these reports: no moving-vehicle refinement window, no
wall-penetration plateau, no universal settling threshold, no validated fording
chain. All four hold, and I reproduce two of them below only as context.

**What nobody extracted is the positive half.** Both reports answer their
question with a *protocol plus citations* after saying no universal constant
exists. The negative was recorded; the method was not. Every DOI in this
document is UNCITED anywhere in the repo, checked against
`data/r5_citation_xref.tsv`.

---

## 1. The settle-length problem has a citable answer, and it is not a frame count

Project state: `settle_frames = 8` is the shipped default at
`sim_standing.py:154`. It sits inside a ring of roughly 100 frames and produced
four false results (spread 6.07x collapsing to 1.94x, one gate ordering
inverted). The open question has been "what settle length is correct".

The report's own summary answers it directly, quoted verbatim:

> No universal frame count or force-settling threshold emerges: the defensible
> protocol is to detect and exclude initial/final transients, demonstrate
> stationarity for the reported observable, and attach uncertainty based on
> correlated samples.

So the question "how many frames" has no answer in the literature and will not
get one. The replacement is a stationarity test plus an effective-sample-size
estimate on a correlated record. That is a standard, citable procedure:

| ref | year | paper | DOI | role |
|---|---|---|---|---|
| [6] | 1989 | Flyvbjerg and Petersen, Error estimates on averages of correlated data | `10.1063/1.457480` | the classical blocking method; the canonical anchor |
| [56] | 2018 | Jonsson, Standard error estimation by an automated blocking method | `10.1103/PhysRevE.98.043304` | removes the hand-chosen block size |
| [7] | **2019** | Grossfield et al., Best Practices for Quantification of Uncertainty and Sampling Quality | `10.33011/livecoms.1.1.5067` | a published best-practice document, directly quotable in Methods |
| [10] | 2021 | Bergmann et al., Statistical Error Estimation for Engineering-Relevant Quantities from Scale-Resolving Simulations | `10.1115/1.4052402` | the closest venue match: engineering CFD, not molecular simulation |
| [1] | 2019 | Brouwer et al., Random uncertainty of statistical moments in testing: Mean | `10.1016/j.oceaneng.2019.04.068` | towing-tank practice for the mean of a transient record |

**Why this matters more than a longer settle.** The project's current defence of
any settle length is that a longer one changed the answer, so 8 was wrong. That
argument has no stopping rule: 250 could be wrong the same way. Blocking supplies
the stopping rule, because it reports when the estimated error stops growing with
block size. It converts "we ran 250 frames" into "the observable is stationary
over this window and its standard error is X", which is what a reviewer will ask
for. Tagged INFERRED as to fit; the methods themselves are READ DIRECTLY from
the catalog.

**Second, and separate: there is no steady force for an impact event.** The
report states that slamming, water entry and impact loading "generally have no
steady force" and should be reported as "peak distributions, impulses, envelopes
or cycle/event statistics with repeat-run uncertainty, rather than a steady
mean". The project's velocity kick after settle is a water-entry-like transient.
If any reported force is a time-mean over a window containing the kick, that mean
is not a physical steady value and the report says so.

## 2. The determinism floor has a literature, and it is a solved engineering problem

Project state: identical runs spread across 0.52 to 1.69 m, which is treated as
an unexplained noise floor and has already caused one withdrawn ratio. The
report's "Numerical reproducibility and ensembles" section names the mechanism:

> Non-associative, order-dependent reductions can produce small drift or alter
> discrete gates; fixed-order/sorted or reproducible reductions and higher-precision
> accumulation mitigate this.

"Alter discrete gates" is exactly the observed failure: a run flipping a verdict
without any parameter changing. This is a named, fixable cause, not noise.

| ref | year | paper | DOI |
|---|---|---|---|
| [36] | 2015 | Ahrens, Nguyen and Demmel, Efficient Reproducible Floating Point Summation and BLAS | (none in catalog) |
| [13] | 2024 | Siklosi, Mudalige and Reguly, Enabling Bitwise Reproducibility for the Unstructured Computational Motif | `10.3390/app14020639` |
| [12] | 2019 | Xu et al., Full-neighbor-list based numerical reproducibility for parallel molecular dynamics | `10.1016/j.parco.2019.04.002` |

A GPU MPM P2G scatter is precisely a non-associative unordered reduction, so this
transfers on its face. Whether warpmpm's P2G can be made order-stable is
UNVERIFIED and is a solver question, not a literature one; I am flagging the
mechanism and its citations, not prescribing the fix. That belongs to D4.

The same section also states that repeated runs "should report outcome spread and
gate-pass frequency" and that "independent-start ensembles are the stronger
convergence check". The project already reports spread by standing rule. The
gate-pass-frequency framing is new and is a better fit for a tunable at-rest gate
than a pass or fail.

**Caveat on this catalog, stated in the report itself:** "DOI/arXiv identifiers
are absent from the supplied records." That is why 68 papers yield only 53 DOIs.
Four of the references above therefore need a manual lookup before use, and three
of the five in section 1 carry DOIs only because I matched them by title.

## 3. Multi-resolution: the decisive finding, and a citation gap in CLAUDE.md L-5

The report's decisive claim, verbatim:

> [4] is decisive: fixed particles-per-cell can lose convergence under grid
> refinement. Methods must co-refine/control PPC; otherwise AMR silently changes
> quadrature and transfer conditioning.

Catalog entry [4] is **Steffen, Wallstedt, Guilkey, Kirby and Berzins 2008,
"Examination and Analysis of Implementation Choices within the Material Point
Method", `10.3970/CMES.2008.031.107`**.

This is the mechanism CLAUDE.md L-5 invokes for the g48/g64/g96 non-monotonicity
in item 5, which is the project's most durable physics result (it survived a
31-fold settle control). Two problems, both READ DIRECTLY:

1. **Neither Steffen 2008 DOI appears anywhere in the repo outside `.claude/`.**
   `10.1002/nme.2360` and `10.3970/CMES.2008.031.107` each return zero files
   across `*.md`, `*.bib`, `*.tex`. The name "Steffen" does appear, in
   `CLAUDE.md`, `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` and
   `docs/MULTIGEOM_VALIDATION_2026-08-11.md`, but never with an identifier.
2. **Neither is in the paper bibliography.** `paper/`, `overleaf_sync/` and
   `deliverables/` return zero hits for "steffen", "nme.2360" or "CMES.2008".

So the single citation that explains the project's headline convergence result is
not in the bibliography and has no DOI recorded anywhere a build could use.

**Do not resolve this by picking one.** Project memory already records that two
distinct Steffen 2008 papers exist and the project refers to both: L-5's
three-author form (Steffen, Kirby, Berzins) is `10.1002/nme.2360`, while the
dispatches and this catalog use the five-author form
`10.3970/CMES.2008.031.107`. Crossref 404s the CMES DOI because Tech Science
Press is not indexed there; the DOI is nonetheless valid. Only the five-author
paper is in any catalog: `10.1002/nme.2360` appears in none of the 14. Whichever
is cited, the quadrature-error argument and the implementation-choices argument
are different papers and should not be merged into one reference.

## 4. Supporting multi-resolution entries, all uncited

| ref | year | paper | DOI |
|---|---|---|---|
| [1] | 2016 | Mao et al., Free surface flows, improved MPM and dynamic adaptive mesh | `10.1061/(ASCE)EM.1943-7889.0000981` |
| [5] | 2020 | Sun et al., A local grid refinement scheme for B-spline MPM | `10.1002/nme.6312` |
| [14] | 2023 | Pan et al., Variable passing for 3D MPM-FEM hybrid and 2D shallow water | `10.1002/fld.5233` |
| [16] | 2023 | Zheng et al., MPM/finite-volume for coupled shallow water and large deformation | `10.1016/j.compgeo.2023.105673` |
| [29] | 2007 | Wallstedt and Guilkey, Improved Velocity Projection for MPM | `10.3970/CMES.2007.019.223` |

Confirming the known negative, verbatim from the summary: "no demonstrated MPM
study was found that follows a rigid vehicle with a refinement window through a
large flood domain". That negative stands, and [1] remains the closest fluid
precedent (dynamic AMR for free-surface waves, no vehicle).

## 5. Status

No project simulation number, force, distance or verdict count is asserted here,
so the physics-skeptic gate does not apply. Every quantity is either an external
citation or a verbatim quotation from a catalog.

**Verification run, 2026-08-16, `scholar-sidekick auditBibliography`, 8 of 8
`matched`, zero retracted:** `10.1063/1.457480`, `10.1103/PhysRevE.98.043304`,
`10.33011/livecoms.1.1.5067`, `10.1115/1.4052402`, `10.3390/app14020639`,
`10.1016/j.parco.2019.04.002`, `10.1002/nme.6312`, `10.1002/nme.2360`.

Two results from that pass:
- **Grossfield et al. is 2019, not 2018.** The catalog's year is wrong and the
  table above is corrected. Confidence dropped to `medium` on the year alone;
  title and identifier match.
- **`10.1002/nme.2360` resolves to "Analysis and reduction of quadrature errors
  in the material point method (MPM)".** That confirms live what project memory
  records: the three-author L-5 form is the quadrature-errors paper, a different
  work from the five-author implementation-choices paper at
  `10.3970/CMES.2008.031.107`. The two-Steffen trap is real and now checked
  against the registry rather than recalled.

UNVERIFIED and needing a primary-source read before any of this enters the paper:
1. `10.3970/CMES.2008.031.107` was NOT in the verified set: Crossref does not
   index Tech Science Press, so an audit call cannot resolve it. Its validity is
   carried from project memory, not confirmed here.
2. Whether blocking transfers cleanly to a 250-frame MPM rollout, whose record is
   far shorter than the molecular-simulation records these methods assume.
3. Whether warpmpm's P2G reduction is in fact order-dependent on GPU.
4. The four settling references with no DOI in the catalog need manual lookup.
