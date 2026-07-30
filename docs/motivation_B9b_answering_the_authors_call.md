# Motivation: the L1 criteria's own authors called for exactly this work

Written 2026-07-25 per AMENDMENT B item B9b.

## SOURCE VERIFICATION STATUS: READ THIS FIRST

**I have not read Shand et al. (2011) or WRL Technical Report 2014/07 at source
in this session.** The quoted limitations and the Table 4-2 values below were
supplied to me in the AMENDMENT B briefing. Under this project's own rule, and
under AMENDMENT B's rule "never write a number into a file that you have not
measured or read at source in this session", that makes this document
**provisional**.

What I *did* verify independently this session:

- The internal arithmetic of the table. `0.10 x 3.0 = 0.30`,
  `0.15 x 3.0 = 0.45`, `0.20 x 3.0 = 0.60`. All three consistent. This confirms
  the "high velocity depth" column is the corner where the D.V hyperbola meets
  the 3.0 m/s velocity cap, not a fourth independent constraint.
- That the live `vehicle_params.py` already carries all three class-membership
  axes (length, kerb weight, ground clearance) and already cites Shand et al.
  (2011) P10/S2/020 Table 3 directly, with ISBN and page. See the reconciliation
  note in `docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md`.

**Before this text goes on the poster or into the paper, do this:** obtain WRL
TR2014-07, confirm Section 4.2 contains the limitation language quoted below, and
confirm Table 4-2 matches. If the wording differs, fix it here first. Do not
propagate a quotation I have not seen.

## The argument

The standard L1 criterion for vehicle stability in floodwater is the depth,
velocity and D.V envelope from Shand et al. (2011), carried into ARR Book 6. It
is the rule that flood guidance and road-closure practice rest on.

Per the AMENDMENT B briefing, the authors of that criterion stated in the same
report that the scaled experimental data underlying it **is being applied beyond
its limits**, and that the criteria are **unlikely to be reliable enough to be
adopted permanently as safety criteria**. They attributed this to the data not
supporting adequate assessment of four things:

1. appropriate coefficients of friction for use in flood flows
2. buoyancy in modern cars
3. the effect of vehicle orientation to flow direction, including vehicle movement
4. information for additional vehicle categories

Both SCARM (2000) and Shand et al. (2011) are reported to recommend a
comprehensive testing programme before definitive design guidelines are
developed.

**Three of those four gaps are precisely what a coupled MPM simulation computes
directly rather than infers.**

| authors' stated gap | what L2 provides |
|---|---|
| friction coefficients in flood flows | `floor_friction` is an explicit, sweepable Coulomb parameter on the ground plane, measured at 0.55 in these runs |
| buoyancy in modern cars | buoyancy is emergent from the coupled pressure field acting on the solidified vehicle volume, not assumed from a lumped density |
| orientation to flow, including vehicle movement | the vehicle is a free rigid body; yaw, pitch, roll and displacement are outputs, not inputs |
| additional vehicle categories | **not** addressed by the current sweep, see the confound below |

## The framing this replaces

The weaker framing is "L1 gets it wrong and L2 catches it out". That invites the
obvious rebuttal that a scalar screening criterion is *supposed* to be
conservative and cheap, and that divergence from a full simulation is expected
rather than damning.

The stronger framing, which is also the honest one, is: **the criterion's own
authors said the underlying data could not resolve friction, buoyancy and
orientation, and asked for a testing programme. This work supplies a
computational instance of that programme for three of the four gaps.** That
claim does not depend on L1 being wrong. It survives even if every L1 verdict
turns out to be correct, because the contribution is the resolved mechanism, not
the disagreement.

## What must be said in the same breath

Two limits, both measured this session, both of which belong next to the claim
rather than buried:

1. **The fourth gap is not addressed, and worse, the obvious attempt at it is
   confounded.** Producing a three-class table by rescaling one mesh via
   `target_length` changes the domain size, which changes `dx`, which changes the
   water layer count: measured **4, 4 and 3 layers** for small passenger, large
   passenger and large 4WD. The 4WD row would discretize the water column 25%
   coarser than the other two, so its displacement would conflate mass, length
   and water resolution. Until the layer count is held fixed, "additional vehicle
   categories" is not a gap this work closes.

2. **Class membership is not satisfied on all axes anyway.** Ground clearance
   measured from the canonical mesh is **0.1737 m**. Small passenger requires
   clearance below 0.12 m, so the baseline class fails that axis. Large 4WD
   requires above 0.22 m and reaches only 0.2109 m at lam 1.214, so it fails too.
   Large passenger is the only class satisfied on all three axes. Full table in
   `docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md`.

Stating both up front is what makes the main claim credible. A poster that claims
to answer the authors' call for "additional vehicle categories" while quietly
running one mesh at three masses would be making exactly the kind of
beyond-its-limits extrapolation the authors warned about.
