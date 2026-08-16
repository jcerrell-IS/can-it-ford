# R5-D1 unit 16: the remaining ten catalog summaries

Date 2026-08-17. Branch `claude/r5-research`. Unit 15 concluded the remaining ten
summaries were worth more than I assumed when I deprioritised them. This is that
read. All 14 catalogs' summaries are now read.

**The single most valuable thing found in this whole dispatch is in section 1,
and it is favourable to the project.**

---

## 1. The evidentiary burden is ASYMMETRIC, and it favours our result

`Physics Simulation Validation Protocol`, 81 papers. Opening sentence, verbatim:

> Decision credibility, not numerical agreement, is the governing endpoint: **a
> FORD claim requires validated six-DOF outcomes and a conservative margin to the
> hazard threshold, whereas a NO-FORD claim may be issued whenever uncertainty
> spans or exceeds that boundary.**

This matters more than anything else I have found, because **our verdicts are
NO-FORD**. CLAUDE.md item 5, verified live at line 203: "The binary verdict is
grid-invariant, all nine are NO-FORD."

Read plainly, that sentence says a NO-FORD call is defensible **precisely when
uncertainty is large**, which is the condition this project is in and has been
treating as a weakness. Every limitation catalogued in this dispatch (2 cells per
depth, a 115x sound-speed discrepancy, an unconverged grid study, a tunable
at-rest gate, a determinism floor) argues *for* the admissibility of a NO-FORD
verdict under this criterion, not against it.

**Do not overread it.** It does not say the runs are validated, and it does not
convert a NO-FORD into a positive safety claim. It says the *decision* is
issuable under uncertainty. The project's existing "necessary not sufficient"
framing is compatible with it and should probably be stated in these terms.
That framing choice is not mine to make, so I am flagging it, not asserting it.

The same summary also prescribes the component chain: test the reconstruction
against surveyed road geometry, test MPM separately on analytical flow,
dam-break, contact and rigid-obstacle cases, and "report conservation residuals,
contact penetration, interface position, pressure/force histories, and
convergence, not merely visual plausibility". It names MPM particle/grid
crossing, locking and stress oscillation as requiring explicit checks, and notes
that published dam-break and FSI datasets "can substitute for new experiments",
which is directly relevant given no GPU is available tonight.

## 2. The reconstruction pipeline is a real gap, which supports the one surviving novelty axis

`Optical Vehicle Collision Geometry`, 23 papers:

> Photo-derived vehicle meshes can already support rigid-body collision
> simulation when their exterior envelope is tessellated adequately, but **the
> literature contains little vehicle-specific end-to-end work linking
> reconstruction, collision-proxy repair, and validated inertial properties**.

Unit 7 concluded that after He 2026, Al-Qadami 2023 and Azhar 2023, the only
surviving novelty axes were MPM-specifically and **geometry provenance**. This is
independent support for the second one, from the project's own corpus. It is the
first evidence I have found that *supports* rather than narrows the contribution.

It also supplies the pipeline vocabulary: metrically anchored exterior geometry,
then "extract or repair a physics representation rather than use rendering
geometry directly", noting that surface-aligned Gaussian splatting supports
Poisson mesh extraction and that non-manifold inputs can be converted to
volumetric collision proxies without watertight preprocessing. That last clause
bears on register E2's `solidify_watertight` question, though I have not chased
it.

## 3. Effective sample size is the conditions, not the frames

`Small Data Physics Surrogates at 36 Conditions`, 47 papers:

> its uncertainty is directly relevant to interpolation and **its effective
> sample size is the 36 conditions, not the 90 frames or mesh/particle count**

and

> There is **no transferable numerical "minimum N"**: adequacy depends on fill
> distance, response smoothness/nonstationarity, output discontinuities, and the
> required error near the FORD boundary.

Two consequences. It is a direct statement of claim discipline for any surrogate
built on the sweep, and it recommends a Gaussian-process response surface with a
separate classifier for the FORD state over a trajectory-level neural model,
which is what `analysis/gp_surrogate.py` already is. The "no minimum N" finding
is the same shape as unit 2's "no universal settle length" and unit 15's "no
defensible near-wall threshold": **the third time this corpus has answered a
request for a magic number with a protocol instead.**

## 4. An independent statement of my own units trap

`Moving Rigid Body Free Surface Validation`, 44 papers:

> [6] proposes total-head criteria of 0.3 m for passenger cars and 0.6 m for
> emergency vehicles. **Still-water depth limits must not be conflated with
> depth-velocity products.**

That is unit 9's trap, reached independently. It is also exactly the AR&R Table 3
hazard I recorded in unit 3 section 4, where the small-passenger row carries a
still-water depth limit of **0.3 m** and a `DV` limit of **0.3 m2/s**, the same
numeral in different units.

The same summary states the known negative, "no validated vehicle-fording MPM
chain is identified", which project memory already records; I am not re-deriving
it. It also flags that the 0.38 m and 0.39 m2/s figures are "case-specific
agreements, not universal tolerances", which is the third independent warning
against treating the Al-Qadami numbers as general.

## 5. NCAC/CCSA assets: I checked for a conflict with item 4 and there is none

`Simulation Ready Vehicle Mesh Assets`, 36 papers, opens by describing the
NCAC/CCSA reverse-engineered LS-DYNA vehicles (2010 Yaris, 2012 Camry, 2007
Silverado) as tied to "teardown/scanning, **measured or calibrated** mass/inertial
and subsystem behavior".

That phrasing looked like it might contradict CLAUDE.md item 4(a), which states
flatly that no measured Yaris inertia tensor exists anywhere. **It does not.**
Reading the body rather than the headline:

> The **Camry** was dismantled part-by-part; parts were catalogued, scanned,
> thickness-measured and material-classified, with **model mass and inertia
> checked against the production vehicle**. **Yaris and Silverado** include
> functioning suspension/steering and **extended impact validation**.

The inertia-checked claim is made for the **Camry**. For the Yaris the claim is
suspension, steering and impact validation. So item 4(a) stands as written, and
the guard at `params_check.py check_inertia_wired()` should not be relaxed on the
strength of this summary. Recording the check because the headline sentence
invites exactly the wrong inference.

## 6. Two catalogs about AI-assisted science, which is what this project is

`Reliable AI Scientific Software` (79) and `Trustworthy AI Assisted Scientific
Simulation` (13) are not about flooding at all, which is presumably why nobody
read them. They are about this project's own method, and they carry hard numbers:

> Execution is not correctness: MDGYM reports at most 21% success on easy
> molecular-dynamics tasks and under 10% on harder ones, while **39-40% of
> runnable multiphysics cases still solve the wrong PDE**.

> only **68.3%** of agent-generated projects ran cleanly, with 13.5x more runtime
> than declared dependencies, whereas Guix/Apptainer plus AiiDA achieved
> bit-identical cross-cluster results.

> LLM-generated simulation inputs **can run and converge while encoding the wrong
> equations**.

These are citable for a Methods or Limitations paragraph on AI-assisted
simulation, and they are the literature form of a rule this project already runs
on ("an import succeeding is not an environment working"). The Guix/Apptainer
plus AiiDA bit-identical result is also a concrete pointer for the determinism
problem unit 2 raised.

## 7. A reframing I am recording but not endorsing

`Quantitative Flood Traversability Connections`, 82 papers, argues the pipeline is
"most valuable as a calibrated, probabilistic link-performance model, **not a new
binary closure rule**", yielding a probability of a limit state given depth,
velocity, slope, vehicle and time "rather than deterministic depth-velocity
bands".

Our output is a binary verdict. This is a coherent alternative framing with 82
papers behind it, and it is a scope decision for Josie and Kumar, not a defect.
Recorded so the option is visible.

## 8. Status

All 14 catalog summaries are now read. Their paper catalogs are mined for DOIs
(unit 1) but only two catalogs' tables were mined for content.

UNVERIFIED:
1. Every bracketed reference in section 1 to 7 points into a catalog table I have
   not resolved to specific papers. **None of the underlying papers has been
   opened.** These are the catalogs' syntheses, not primary sources.
2. Section 1's reading of the FORD/NO-FORD asymmetry is my plain reading of one
   sentence. Before it is used in the paper, the underlying references [2, 3, 17]
   should be resolved and read, because it would be a load-bearing claim.
3. The AI-software percentages in section 6 are quoted from the summary, not from
   MDGYM, PDEAgent-Bench or AutoMat directly.
4. I did not chase the `solidify_watertight` / register E2 connection in section 2.

No project simulation number is asserted here. The one project fact used, that
the canonical grid study's verdicts are NO-FORD, is CLAUDE.md item 5 verified
live at line 203.
