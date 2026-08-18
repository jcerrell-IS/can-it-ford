# RETRACTED: "Job B is not running the benchmark it cites"

**This document's original central claim was WRONG and is withdrawn in full.** It was
committed in `5955a54` and pushed to a public repo before I read the manifest that defines
Job B. What follows is the retraction, then the part of the investigation that survives.

## 1. WHAT I CLAIMED, AND WHY EACH PART IS WRONG

I claimed Job B "does not run the benchmark it cites" on four deviations. Read live from
`docs/R5_PHYSICS_BATCH_MANIFEST.md:173-241` and `sphere_heave.py:55-95`, three of the four
are deliberate, documented design choices and the fourth is the opposite of a defect.

| my claim | what the source actually says |
|---|---|
| "held fixed instead of released" | `MANIFEST:204-206`: Job B is kept at `lim = 1.2` deliberately as "a **cheap hydrostatic pilot where reflections do not matter**: the sphere is pinned and the quantity is a steady reaction, not a decay." The pinning is the point of the rung. |
| "tank depth wrong by 1.8x" | `sphere_heave.py:73-75` records it as deviation 2 with a quantified justification: at 500 mm, `kh = 3.333`, `tanh(kh) = 0.99746`, deep-water to 0.25 %. "Stated as a quantified approximation, not asserted as equivalent." |
| "graded a static force, not the benchmark's motion" | `MANIFEST:242`: **Job C IS** "Kramer free heave decay, three drops", already specified, with a corrected domain because "Job C cannot use this domain". B is its precursor, not its replacement. |
| "tolerance is self-set, with no source" | `MANIFEST:3` derives the bands from the project's own box-SDF prior of 7.3 to 7.7 %, and marks that provenance `[recalled]`. Internal rather than external, but stated and reasoned, not invented silently. |

**And the manifest already makes my own headline argument, against me.** `MANIFEST:236-240`:
"Explicitly not graded here: the 0.090 / 0.270 / 0.450 mm per-drop-height tolerances. Those
are **displacement** tolerances and apply only to the free-decay drops in Job C. A
hydrostatic force check cannot be graded against a displacement tolerance, which is the
category error section 3.2 of the test-case doc warns about."

So the thing I presented as a discovery, that Kramer's 0.3 percent is a motion tolerance and
cannot grade a static force, is exactly what the manifest says, and it says it as the reason
NOT to do what I implied should have been done. My recommendation "run Kramer's actual case"
reduces to "run Job C", which was already planned and is deliberately gated on B.

## 2. HOW I GOT IT WRONG

I read the run config and the driver, and inferred intent from a mismatch between the config
and the cited paper. I did not read the document that states the intent, and it was one grep
away. This is the project's own rule 12 failure: I named a mechanism that would refute me
only after committing, not before. The refuting artifact was a file in the same repo.

The narrower discipline it violates: a deviation from a source is only a defect if the
deviation is undocumented. I checked the deviation and not the documentation.

## 3. WHAT SURVIVES

**The measurement, unchanged.** Job B reads `fz_over_analytic_measured` at +50.06 percent,
and after both boundary fixes +34.35 / +35.92 percent. All four 2x2 cells FAIL criterion 3.
That is in `R7_JOBB_2X2_COMBINATION_2026-08-18.md` and none of it depended on this document.

**The literature, which was the point of the search and is not affected.** Deep search over
the scholarly literature, [workspace](https://app.undermind.ai/projects/17299f2a-8dc8-438b-8c84-5abf19395e2c).
Every DOI resolved and its title checked against the resolved record.

- **Weakly compressible MPM is known to behave badly exactly at a free surface**, which is
  where a half-submerged sphere sits. Zhang et al. 2017, *Incompressible material point
  method for free surface flow*, J. Comput. Phys., `10.1016/j.jcp.2016.10.064`, introduces a
  projection formulation for that reason. Companion: Chen et al. 2018, *v-p material point
  method for weakly compressible problems*, `10.1016/J.COMPFLUID.2018.09.005`.
- **Hydrostatic tests are the standard probe for MPM integration and quadrature error**, and
  quadratic B-splines reduce but do not remove particle-location sensitivity. Baumgarten and
  Kamrin 2023, `10.1002/nme.7217`; Steffen, Kirby and Berzins (no DOI on record).
- **Accumulated contact force is the published alternative to velocity projection.** Akinci
  et al. 2012, `10.1145/2185520.2185558`; Hu et al. 2018, `10.1145/3197517.3201293`. The
  second is already in CLAUDE.md A-1; the first appears to be new to the project.
- **The field rarely cross-checks impulse exchange against a pressure-surface integral**, and
  rarely reports force-extraction windows or particles-per-cell convergence for the body.
  That remains a genuine diagnostic gap and the most useful thing on this list.

**The effective-radius hypothesis, already self-refuted in the original.** A one-cell skin
fits all four cells at 0.85 to 1.18 dx, but the vehicle SDF validation reads -7.668 at g64
and +7.280 at g96 (`docs/CONTEXT_CENSUS_2026-08-07.md:1049-1052`), wrong sign and wrong
magnitude against the roughly +54 percent a universal skin predicts. Still worth one cheap
`n_grid` sweep on the fixed sphere to close it, and that sweep is now the ONLY new experiment
this investigation justifies.

## 4. WHAT ACTUALLY FOLLOWS

1. **The Job B decision is unchanged and is still Josie's**: accept the FAIL and stop the
   ladder per `MANIFEST:214`, or amend criterion 3 in writing before Job C. There is no third
   option, because the "run the real benchmark" option I proposed is Job C and is gated.
2. **The one cheap experiment worth running** is the fixed-sphere `n_grid` sweep at 64, 96,
   128, which closes the skin hypothesis either way for 1 to 2 SU.
3. **The pressure-surface cross-check** is the diagnostic the literature says is missing, and
   it is a Mac-side analysis of an existing run if the pressure field is dumped.
