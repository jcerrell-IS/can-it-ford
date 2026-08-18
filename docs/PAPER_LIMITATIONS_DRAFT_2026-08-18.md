# Limitations, draft prose for the paper, 2026-08-18

**WHERE THIS GOES.** NOT into `paper/conference_101719.tex`. The paper builds from
`conference_101719_1.tex` on `overleaf/main`, which shares no ancestor with local
`main`, so editing the local copy forks the text instead of changing the paper.
Paste these into Overleaf, or apply them in `~/can-it-ford-paper`, which sits at the
Overleaf head.

**EVERY `\cite` KEY BELOW EXISTS** in `paper/can_it_ford_references_IEEE.bib` as of
commit `123981e`, except the two marked MISSING KEY, which need adding first.

---

## L1. The verdict is necessary, not sufficient, and the threshold literature disagrees

> The stability criteria used here describe a stationary vehicle subjected to flow
> \cite{shand2011}, so a NO-FORD verdict is a necessary condition for an unsafe
> crossing rather than a sufficient one: a vehicle that is unstable while stationary
> cannot safely be driven through, but stability while stationary does not establish
> that driving through is safe. Two further limits apply to the criteria themselves.
> The Australian Rainfall and Runoff guidance rests on vehicle tests predating 1993
> \cite{shah2019guidelines}, and published stability thresholds from different
> experimental programmes do not agree with one another \cite{bocanegra2019review}.
> We are therefore reporting a verdict against a criterion whose own spread is not
> smaller than several of the effects we resolve.

## L2. The velocity cap is administrative

> The 3.0 m/s upper bound on the velocity sweep was chosen to remain below published
> human-stability curves and is not derived from vehicle data. We are not aware of an
> experimental basis in the reviewed literature for the 1.5 m/s figure used as the
> canonical condition, and we do not present it as one.

## L3. Grid refinement is not expected to converge an instantaneous quantity

> Final displacement magnitude is non-monotone across grid refinement. This is the
> documented expected behaviour of an instantaneous quantity rather than evidence of
> a solver defect \cite{syamlal2017uncertainty}: a grid convergence index applies to
> a time-averaged observable over a window demonstrated to be stationary, not to a
> value read off the last frame. We therefore report the binary verdict, which is
> invariant from g48 through g128 across three masses, five velocities and three
> depths, and we do not report a convergence order for the displacement.

## L4. Uncertainty is computed from the effective sample size, not the frame count

> Each 91-frame record contains far fewer independent samples than frames. Applying
> MSER truncation \cite{bergmann2021mser}, the reverse-arrangement test and blocking
> analysis \cite{flyvbjerg1989blocking}, together with the random uncertainty of the
> mean \cite{brouwer2019rum}, the effective sample size is between 2.9 and 11.0. All
> 25 runs require more than the eight settle frames used by the driver to be
> discarded, with a median of 48. Uncertainties quoted from the frame count would be
> overstated by roughly three to five times, so all uncertainties here use the
> effective sample size.
>
> One consequence is reported rather than hidden. In a separate open-channel
> experiment, the same configuration run to 90 and to 300 frames returned free-surface
> slopes that differ in sign for two of three cases. A within-record uncertainty
> measures scatter inside one record; it is not evidence that the mean has converged,
> and re-running at a different record length is the control that establishes whether
> it has.

## L5. Added mass is not constant while the vehicle is accelerating

> The incipient-motion event on which the SLIDE verdicts rest is a period of
> sustained acceleration, and drag during prolonged acceleration is not captured by a
> single added-mass coefficient; an entrainment rate is required, and steady drag
> rises by about 45 percent at one-fifth-height submergence \cite{grift2019acceleratingplate}.
> Our coupling carries no explicit added-mass term, so the surge loading is expected
> to be underestimated in exactly the regime the verdict is taken in.

## L6. Unsteady flow is not modelled, and a realistic environment worsens this

> Unsteady flow has been reported to raise drag by 40 to 50 percent relative to the
> steady equivalent \cite{azhar2023}. Our inflow condition prescribes a steady
> velocity, so this contribution is absent. It is not conservative: adding realistic
> unsteadiness would increase the load, so the present verdicts are optimistic in this
> respect while being conservative in the resolution respect noted below.

## L7. The domain is the boundary condition, and we measured how much

> A bounded domain cannot represent a flooded roadway. Conserving volume in a closed
> box forces a redistribution that is larger than the slope being sought: at zero
> grade our closed configuration manufactures a free-surface slope of about
> 0.093 m/m, against a bed slope of 0.052 m/m for a 3 degree road, and it drains its
> upstream bins entirely. Opening the streamwise faces, by a fixed-pool translation of
> the add-and-remove in/outflow conditions of \cite{zhao2019inoutflow}, reduces the
> residual to below 0.009 m/m in every case measured, at both record lengths and all
> grades tested. We report that bound and the separation rather than a single residual
> value, because the residual itself is not resolved by these records.
>
> The translation is a limitation in its own right. The engine allocates its particles
> once and exposes no way to add or remove one, so inflow and outflow are realised as
> strict one-in-one-out recycling. That reproduces the uniform-channel case exactly
> and cannot express the non-uniform case, which requires a net flux imbalance. The
> pressure-controlled half of the outflow condition is likewise not implemented; the
> prescribed-traction machinery for it exists \cite{remmerswaal2024neumann} and is
> future work.

## L8. Water penetrates the boundaries, and refinement does not fix it

> Water crosses the vehicle boundary at a rate the gate limits to 10 percent of the
> bounding box. Refinement from g64 to g128 increased this in all eleven cases and
> converted one passing case to failing, so resolution is not the remedy. A distinct
> contribution comes from the domain: opening the streamwise faces reduced the same
> quantity from 0.107 to 0.083, across the gate limit, with the hull, mass and script
> unchanged. Boundary penetration therefore has at least two separable causes, and we
> attribute the residual to the grid boundary treatment rather than to resolution.
> The same defect appears at the floor, where sustained flow produces about thirty
> times the penetration of a stagnant pile in the same scene.

## L9. Mass alone does not determine the thresholds

> Two of the three masses in the sweep are not traceable to a measured vehicle in our
> sources, and the class-specific quantities that actually govern the published
> thresholds, displaced volume, underbody shape, wheelbase, track and centre of mass,
> are not gated \cite{smithmodrafelder2019, martinezgomariz2018}. Cross-vehicle runs
> reported here additionally do not share a resolution: at fixed grid count a
> different hull changes both the cell size and the realised water depth, giving 2.9
> to 4.1 water layers across the three vehicles.

## L10. The numerical sound speed is below the convention

> The artificial bulk modulus gives a numerical sound speed of 12.85 m/s. The
> convention adopted in the in/outflow work we follow is that the numerical sound
> speed should exceed ten times the maximum flow velocity \cite{zhao2019inoutflow}.
> That is satisfied at 0.5 and 1.0 m/s and not at 1.5 m/s and above, where the ratio
> falls to 4.3 at the top of the sweep. The consequence is excess compressibility
> rather than instability, and we have not tested whether any verdict turns on it.

## L11. Prior art we do not extend

> Four prior vehicle fording or wading simulations exist
> \cite{he2026vehiclewater, wasfy2015fording, pazouki2016fording, khapane2014wading},
> and a moving full-scale vehicle simulation has been reported with a critical depth
> of 0.38 m \cite{alqadami2022moving}. A tire-water film-pavement model in the
> material point method with a rolling tire has also been published
> \cite{zhou2025hydroplaning}, which establishes that this method can host a real road
> surface. Our contribution is not the pipeline; it is the boundary condition and the
> validation, and the road geometry we add is a cross-section rather than a rolling
> contact problem.

---

## MISSING KEYS, add before using these two sentences

Order-dependent floating-point reductions can change a discrete outcome, and
SLIDE / STUCK / FLOAT is a discrete outcome. Two citations for this are named in the
project notes but are NOT in the bib: `10.1016/J.PARCO.2019.04.002` (Xu et al 2019)
and `10.3390/app14020639` (Siklosi et al 2024). Verify both with Scholar Sidekick
before adding, then a limitation can be written that the verdict has not been tested
for reduction-order sensitivity.

## What is deliberately NOT claimed here

- No statement that the free-overfall end-depth ratio has been reproduced. That test
  is implemented but had not returned at the time of writing.
- No statement that image-particle boundaries were implemented. They were not.
- No statement about the pavement representation in \cite{zhou2025hydroplaning}
  beyond what its abstract supports; the full text was not obtainable.
