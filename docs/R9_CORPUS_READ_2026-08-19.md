# What the corpus actually says, read from full text, 2026-08-19

Six papers read in FULL TEXT tonight via the Undermind connector's `read_pdfs`, not via
`analysis/research_index.py`. That distinction is the point of this document: the index
holds no full text and never did, so every prior "the corpus says" in this project came
from titles, abstracts and an AI-written summary. See d14's `6ff3f14` and the memory
`corpus-holds-no-full-text.md`.

Source: workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`, 21 deep searches, of which the
index reads 8. Everything below comes from the 13 it does not read.

## 1. The strongest candidate yet for Job B: VOLUMETRIC LOCKING

Zhao, Jiang and Choo, "Circumventing volumetric locking in explicit material point
methods: a simple, efficient, and general approach", CMAME 2023, arXiv 2209.02466.

Explicit MPM is called INHERENTLY VULNERABLE to volumetric locking because it carries
many material points per element, each imposing an incompressibility constraint. Three
properties matter here, all read from the paper:

1. It SYSTEMATICALLY OVER-PREDICTS THE FORCE TRANSMITTED TO A RIGID BODY. Their strip
   footing case is a rigid body on a nearly incompressible medium; analytic normalised
   bearing capacity 5.14 against about 7.5 to 8.0 for standard GIMP, an over-prediction
   of roughly 45 to 55 percent.
2. IT IS NOT FIXED BY REFINEMENT. The paper states the non-physical oscillations are
   "not remedied by spatial refinement", and in the strip footing case a FINER grid gave
   a LARGER over-prediction.
3. The remedy is an assumed deformation gradient (F-bar) built on the transfer scheme
   already present, with no extra grid and no new parameter, modifying only the stress
   update in the G2P stage. Algorithm 1 is five steps.

Job B measures +34 to +64 percent on a rigid body, does not improve with refinement, and
at g96 the E1 correction moved the wrong way. Same sign, overlapping magnitude, same
refinement signature.

NOT A DIAGNOSIS YET, and the caveat travels with the claim: their strip footing is an
elastoplastic solid, not weakly compressible water, and a magnitude overlap is not a
cause. Two other channels are live, and one PPC sweep separates two of them, because
they predict OPPOSITE things:

| channel | prediction under a PPC sweep at fixed grid |
|---|---|
| volumetric locking (Zha22d) | error RISES with PPC, and is insensitive or adverse to grid refinement |
| velocity-projection bias (Wal07) | error FLAT in PPC, plateau set by h |

## 2. The velocity projection carries a constant bias for a FIXED body

Wallstedt and Guilkey, "Improved Velocity Projection for the Material Point Method",
CMES 19(3) 223-232, 2007.

The mass-weighted projection is equivalent to trapezoidal integration and is exact only
for linear fields under symmetric particle placement; off-centre particles destroy the
cancellation. FOR A BODY HELD FIXED the particle distribution relative to the grid is
static, so the projection error becomes a CONSTANT SYSTEMATIC BIAS rather than noise.
For non-linear fields, increasing PPC does not remove it: the error reaches a plateau
scaling roughly as O(h), while the linear-field part converges as PPC^-2 for bilinear
and PPC^-3 for GIMP. Vshivkov's bound carries one PPC^-2 term and one h^2 term.

Our force accessor is accumulated projection impulse divided by dt on a fixed body,
which is exactly the configuration this applies to.

## 3. Quadrature error is NOT the explanation, and that is worth having

Steffen, Wallstedt, Guilkey, Kirby and Berzins, "Examination and Analysis of
Implementation Choices within the Material Point Method", CMES 31(2) 107-127, 2008.

Analyses B-spline quadrature error at length: O(dx^2) when particle width is below the
smoothing length, degrading toward O(dx) above it, with error falling as PPC rises. It
EXPLICITLY DOES NOT REPORT A ONE-SIGNED BIAS, characterising the errors as "force kicks"
and noise. So quadrature can be set aside as a candidate for a systematic offset, which
narrows the field rather than widening it.

## 4. The published standard for a static column, which ours would fail

Quinlan, "Extensions of the meshless Finite Volume Particle Method (FVPM) for static and
dynamic free-surface flows", Computers & Fluids 2018.

Hydrostatic validation is a tank of width 2H filled to depth H, plus an irregular tank,
plus one with non-uniform particles from dx/H = 1/10 to 1/40. The reported pass
condition: total kinetic energy normalised by gravitational potential energy decays to
10^-13 to 10^-18, described as MACHINE ZERO; max velocity approaching equilibrium of
order 10^-4 sqrt(gH); steady pressure converging SECOND ORDER, RMS non-dimensional
pressure error about 10^-7 at H/dx = 100.

A well-balanced scheme goes quiet on a static column. Ours drains. Both can be true at
once and stating both is stronger than stating either; d11 is running `r9_quiesce`
against this.

## 5. Boundary-condition verification, and how far a wall reaches

Negi and Ramachandran, "How to train your solver: Verification of boundary conditions
for smoothed particle hydrodynamics", arXiv 2208.10848.

Method of manufactured solutions rather than a hydrostatic test, so it does not give an
acceptable static error. What it does give is a distortion depth: the PRESSURE GRADIENT
stays second-order accurate with ZERO ghost layers, while the VELOCITY LAPLACIAN needs
at least TWO layers, because second-order Laplacian formulations need gradients on all
neighbours. Of the wall treatments tested, Marrone et al 2011 was second order on all
three conditions; Adami et al 2012 failed to converge for no-slip (order 0.09).

## 6. A third channel nobody has tested: wall momentum zeroing

From the deep search "free surface elevation estimator error in particle method buoyancy
validation", run 2026-08-19 17:44, 88 papers, top-ranked Schneider et al 2019, "A
Consistent Boundary Method for the Material Point Method, Using Image Particles to Reduce
Boundary Artefacts". The search summary states that TRADITIONAL MPM WALL MOMENTUM ZEROING
CAN DISTORT STRESS SEVERAL GRID LENGTHS INTO AN OBJECT, and that image-particle
boundaries reduce it. No PDF is retrievable; it needs uploading in the web app before it
can be read rather than cited from a summary.

THAT SEARCH ALSO PRESCRIBED THE CONTROLS THE FLEET RAN HOURS LATER, independently:
nested exclusion radii including zero, local vertical columns, geometric or level-set
reconstruction, and "a body-off hydrostatic run provides the estimator bias independently
of body loading". d21 ran the no-body control and d11 ran the body-off column. Both were
right; both paid to rediscover it.

## 7. What the literature says actually changes a flood verdict

From "which realism effects change a flood vehicle stability verdict", 2026-08-18, whose
goal text is this project's own configuration down to the 0.15 m cell and c = 13 m/s.

WITH threshold evidence: bed condition and friction (full-scale tests measured materially
different coefficients on concrete, gravel and sand, requiring a worst case); road slope
and flow orientation; watertightness. Unsteady flow raises simulated drag 40 to 50
percent, but that is not a discrete verdict comparison.

WITHOUT any demonstrated verdict shift: air entrainment, spray, surface tension,
turbulence closure, REDUCED SOUND SPEED, and OUTLET BOUNDARY CHOICE. The ten-times-flow-
speed rule for sound speed has NO PRIMARY DERIVATION in the retrieved literature; it is
convention.

AND THE GAP THIS PROJECT IS ALREADY FILLING: no retrieved study quantifies a CROWNED OR
CAMBERED ROAD against a flat plane. Job 922593 ran one tonight in 7:31. To fill the gap
it must be a PAIRED comparison against a flat plane at otherwise identical conditions.

A separate search, "Dynamic Vehicle Traction in Floodwater", adds that tire-scale flooded
pavement work supplies a DEPTH AND SPEED DEPENDENT tire-force law rather than a fixed
friction coefficient, which is what `floor_friction = 0.55` currently is.

## 8. THE SOLVER HAS NO LOCKING MITIGATION, read live from the pinned source

Added 2026-08-19 after section 1, because a hypothesis about our solver should be
checked against our solver rather than argued from a paper. Read from
`third_party/mpm-engine-544c93dd-solver-core/`, the pinned vendored core.

A search of the whole vendored tree for `fbar|f_bar|volumetric lock|locking|jbar|
j_bar|assumed deformation|volume.averag` returns exactly ONE hit, and it is the word
"blocking" inside a comment about merging wheel wells into the solid. A second search
for pressure smoothing, projection, averaging or filtering returns only velocity and
collision projection sites. So THERE IS NO F-BAR, NO J-AVERAGING, NO PRESSURE
SMOOTHING AND NO LOCKING MITIGATION OF ANY KIND.

And the fluid stress update is precisely the per-particle form F-bar replaces
(`kernels/mpm_utils.py`, the `mat == 6 or mat == 10 or mat == 12` branch):

    J = wp.determinant(state.particle_F_trial[p])
    Jcbr = J**(1.0 / 3.0)
    state.particle_F[p] = wp.mat33(Jcbr,0,0, 0,Jcbr,0, 0,0,Jcbr)

J is taken PER PARTICLE from that particle's own trial deformation gradient. Zha22d's
Algorithm 1 changes exactly this: it volume-averages the Jacobian to the nodes,
`Jbar_i = sum_p w_ip V_p (Jbar_p dJ_p) / V_i`, and pulls back before the stress
update. The branch already computes J and already builds an isotropic F, so the
remedy lands on these three lines.

ONE NUANCE THAT MUST TRAVEL WITH THE CLAIM, so it is not overstated. The fluid's F is
FORCED ISOTROPIC here, discarding the deviatoric part, so the classical
deviatoric-locking picture does not apply directly. What applies is the other half of
the same failure, the per-particle pressure evaluation that produces spurious pressure
oscillation, which is what J-averaging cures and what Chen et al 2018's v-p MPM paper
names when it says WCMPM exhibits volumetric locking AND interface pressure
oscillation. State it as the pressure-oscillation channel, not as deviatoric locking.

WHY THIS MATTERS FOR d11's COLUMN. A column whose kinetic energy GROWS rather than
decays, 11 orders above the well-balanced reference, immune to a boundary fix that
repaired 96.4 percent of the mass loss, is what a per-particle pressure evaluation
with no smoothing would be expected to produce. The column is a better test bed than
the sphere scene because it has no body, no coupling and no surface estimator to
confound it.
