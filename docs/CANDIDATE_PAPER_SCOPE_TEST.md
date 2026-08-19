# The scope test: five questions to ask a candidate paper before relaying it

Written by d21-jobb, 2026-08-20, at the coordinator's request, after
`docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md` section 16 killed a relayed candidate on scope
rather than on numbers. **This file is outside my declared write scope of that document and
`analysis/r9_jobb_estimator_test.py`. It is a NEW file, additive, conflicting with nobody,
created because the coordinator asked for the test somewhere reusable.** If that is the
wrong home, move it; nothing depends on its path.

---

## Why this exists

Three relayed literature claims were checked against their papers on 2026-08-19. **All three
had the direction right and the specificity wrong**, and the failure mode was identical every
time: a headline carried with the source's confidence and without the source's scope.

| relayed as | what the paper actually said |
|---|---|
| Wal07: "for a fixed body the projection error is a CONSTANT SYSTEMATIC BIAS, not noise" | **Not in the paper.** It says accuracy "is strongly dependent on particle density and location", and adds that as simulations evolve "particles will generally move into a less favorable configuration", which is the opposite emphasis |
| Wal07: "the plateau scales as O(h)" | The plateau is real and quoted, but `O(h)` is **read off Figure 10**; the paper's own analytic reference (Vshivkov 1996) has an `h^2` grid term |
| Ami15: "a fixed body reading 10 percent above analytic, with THE BOUNDARY TREATMENT NAMED AS THE CAUSE" | The 10 percent is a peak **pressure coefficient**, not a force, and the attribution is a **comparison** against two other schemes, not a stated cause |

Ami15 also failed on three independent scope grounds, **any one of which was sufficient**,
and none of which was visible in the relay. That is what the five questions below are for.

---

## The five questions

Ask these of a candidate paper **before** it is relayed, and again before it is cited. Each
one killed a real candidate in a single night.

### 1. DISCRETISATION. Does the paper's method share the mechanism you are invoking it for?

Not "is it a particle method". **Is the specific machinery the same.** Ami15 is purely SPH:
its background grid is explicitly "coarse reference/background (non-computational)", used
only for neighbour searching. **There is no velocity projection onto grid nodes anywhere in
it**, and grid-node projection was the entire mechanism it was relayed to support.

Ask: *if I deleted the component I am blaming, would this paper's method still work?* If
yes, the paper is not about my component.

### 2. BOUNDARY OR COUPLING SCHEME. Is it the same one, named?

Ami15 uses Adami, Hu and Adams 2012 dummy wall particles with pressure extrapolated from
local fluid acceleration and gravity. The sphere scene uses a grid-node momentum difference
`sum m*(v_free - v_new)/dt` gated at `sd <= band`. **Both are "boundary treatments" and they
share nothing operational.** "Boundary treatment is to blame" is not a mechanism; it is a
category.

Ask: *name the scheme in both, in one clause each.* If the two clauses do not overlap, the
paper is a phenomenological precedent at best.

### 3. REGIME. Is the flow the same kind of flow?

Ami15's case is a 2D jet perpendicularly impinging a plate: a stagnation flow with a real
free-stream velocity. Job B is hydrostatic, `mach_peak = 0.0` in every run config. **There is
no stagnation point in the sphere scene and no stagnation pressure to over-predict**, so the
matched quantity does not exist on one side of the comparison.

Ask: *what is the dimensionless regime on each side?* Static against dynamic, or Mach 0
against a real free stream, disqualifies a quantitative match even when the number agrees.

### 4. QUANTITY. Is the number the same kind of number?

Ami15's 10 percent is a **peak pressure coefficient at a point**. Job B's 20 to 46 percent is
an **integrated vertical force on a body**. A local peak and a surface integral fail
differently and converge differently; a paper reporting one does not constrain the other.

Ask: *pressure or force? local or integrated? peak or mean?* Two of the three relayed claims
above changed meaning at this question alone.

### 5. EVIDENCE STRENGTH. Is the claim a result, a figure reading, or an aside?

Wal07's `PPC^-2` and `PPC^-3` are in the text as the authors' own words. Wal07's `O(h)` is a
slope measured off a plotted curve by a reader. Ami15's refinement evidence is **one halving
step** whose peak is read from a figure panel. All three are usable; **they are not equally
strong and they must not be quoted at the same confidence.**

Ask: *quote the sentence.* If there is no sentence, say "read off Figure N" in the citation
itself.

---

## The rule that follows

**A candidate paper must pass all five to be cited as a MECHANISM. Passing some of them makes
it a PRECEDENT, which is a weaker and still useful thing, and the write-up must say which.**

Ami15's honest use, after failing 1, 2 and 3: *particle-method boundary treatments are known
to produce percent-level, refinement-resistant over-predictions on fixed bodies* [Ami15]. That
is context for a conclusion reached on this project's own evidence. It is not a diagnosis, and
it does not convert "unexplained" into "known failure mode of this class of boundary
treatment", because it is not this class of boundary treatment.

---

## Two habits that make this cheap

**Relay the scope with the claim, or tag it unverified.** The coordinator tagged Ami15
`RELAYED AND UNVERIFIED` and said to read it before citing. That tag cost one read and saved a
citation; the four earlier untagged relays reached three sessions and had to be chased.

**A paper with a retrievable PDF should be read, not summarised.** Every one of the three
failures above was invisible in the search summary and obvious in the text. Reading Wal07 and
Ami15 took one tool call each. **Where no PDF is retrievable, say so in the citation and mark
the claim as reaching you through a summary** — as this project's notes now do for Sch19e,
which has no DOI, resolves only to a Semantic Scholar record, and has never been read by
anyone here.

---

## Worked negative example, so the test is falsifiable

Applying the five questions to a paper that **passes**: Steffen et al. 2008
(doi:10.3970/CMES.2008.031.107), cited in the job B route decision for the claim that wider
basis functions worsen geometric errors at boundaries.

1. **Discretisation**: MPM with grid-node transfers. Same machinery. Pass.
2. **Scheme**: it analyses basis functions including quadratic B-splines, which this engine
   uses. Same component. Pass.
3. **Regime**: a 1-D manufactured-solution bar and 3-D tests, not matched to a hydrostatic
   sphere. **Partial.** The claim borrowed is about basis-function support width, which is
   regime-independent, so this is survivable but must be stated.
4. **Quantity**: "geometric errors ... at boundaries", a qualitative mechanism, not a number.
   The citation must not attach a magnitude. Pass, with that constraint.
5. **Evidence**: a direct sentence, quotable: "The geometric errors are exacerbated when
   smoother, and necessarily wider, basis functions are used, such as uGIMP, or B-splines."
   Pass.

**Verdict: citable as a mechanism, with no magnitude attached and its regime stated.** That is
the shape a passing candidate should have.
