# Deep-search prompt: audit the 2026-08-18 open-channel work against the literature

Written 2026-08-18. Target: Undermind `launch_deep_search`, or any comprehensive
literature agent. Paste everything below the line.

**Why these questions and not others.** Each one traces to a measurement made this
session, and each was checked against `data/research_corpus_index.json` first. The
corpus holds 332 papers but is thin exactly here: `inflow-outflow` has **2** papers,
`cpdi` **1**, `immersed-fem` **1**, `incompressible-mpm` **3**, `particles-per-cell`
**3**, `grid-convergence` **4**, `wall-penetration` **6**. Schulz & Sutmann,
Remmerswaal et al 2024 and the MPM multi-material contact literature are not indexed
at all.

---

I am auditing a specific computational result and I need to know what the literature
already establishes, so that I neither claim novelty for something known nor keep
re-deriving something solved. Negative answers are as useful as positive ones: if
nobody has published on a point, say so explicitly rather than returning adjacent
work.

## The system

A GPU material point method code (NVIDIA Warp based) simulating a stationary
passenger vehicle in floodwater. Weakly compressible Newtonian fluid, 8 particles
per cell, cubic background grid, domain 9.42 m with cell size 0.147 m, water depth
0.30 m, flow 0.5 to 3.0 m/s. The vehicle is a watertight hull discretised as rigid
material points. The engine has three properties that constrain everything below:

- **Particle count is fixed at load.** There is no insertion or deletion entry point.
- **The deformation gradient F has no setter.** It can be read, not written. For the
  fluid the deviatoric part is discarded every substep, so the only carried state is
  the volumetric Jacobian J, and pressure is p = -K(J^-1.1 - 1).
- **The engine's periodic streamwise flag is documented incompatible with rigid
  bodies**, so grid-level wrapping is unavailable when a vehicle is present.

## What I already have, do not return these

Zhao, Bolognin, Liang, Rohe & Vardon 2019 `10.1016/j.compfluid.2018.10.007`;
Remmerswaal, Vardon & Hicks 2024 `10.1016/j.compgeo.2024.106494`;
Zhou et al 2025 `10.1063/5.0276643`; Nihei et al 2025 `10.1016/j.rineng.2025.107189`;
de Vaucorbeil et al 2020 `10.1016/bs.aams.2019.11.001`;
Zhang et al 2022 IFEMP `10.1016/j.cma.2022.114809`;
Kularathna & Soga 2017 `10.1016/j.jcp.2016.10.064`;
Celik et al 2007 `10.1115/1.2960953`; Roache 1994 `10.1115/1.2910291`;
Stern et al 2001 `10.1115/1.1412235`; Baumgarten & Kamrin 2023 `10.1002/nme.7217`;
Smith, Modra & Felder 2019; Martinez-Gomariz et al 2017 and 2018;
Xia et al 2011 and 2014; Shu et al 2011; Al-Qadami et al 2022;
Australian Rainfall and Runoff Project 10 (Shand et al 2011).

## The questions

**1. Particle recycling as a substitute for insertion and deletion.**
Zhao et al 2019 impose inflow and outflow by adding and removing material points. I
cannot do that, so I move a particle that crosses the outflow plane back to the
inflow plane in one operation. **Has anyone published this recycling construction for
MPM, SPH, MPS or PIC in a fixed-allocation or GPU code?** What is it called, what are
its documented artefacts, and is there a treatment of the thermodynamic-state problem
(a recycled particle carrying a stale pressure or compression state into a region
that requires a different one) when the state variable cannot be reassigned? I need
either a name and a citation for this technique, or a clear statement that it is
undocumented.

**2. Whether a recycling closure can sustain a discharge at all.**
Measured: with strict one-in-one-out recycling, the outflow discharge decays to
**0.25 to 0.29 of its initial value in every configuration tested**, near-identically
across bed slope, bed friction and grid resolution. Adding a 42 percent reserve of
spare particles with a depth-control inlet did not fix it; the reserve pool emptied
and the inlet depth still collapsed. **Is there a published analysis of why a
closed-mass recirculating particle domain cannot hold a steady free-surface
discharge, and what the minimum sufficient boundary condition is?** Specifically: is
a pressure- or traction-controlled outlet necessary, as opposed to a purely kinematic
one, and is there a worked particle-method example of a free-surface outlet that is
not simply a wall or a deletion plane?

**3. The free overfall as a particle-method benchmark, and its resolution floor.**
Rouse found the critical depth is about 1.4 times the brink depth in a horizontal
rectangular channel. Zhao et al use this to validate. My reproduction gives ratios
spanning **0.74 to 2.71** across plausible bed friction and grid choices, and the
Froude number covaries with resolution so a grid sweep changes the flow regime rather
than isolating discretisation error. **What resolution, particles per cell and
channel length do published particle-method reproductions of the free overfall
actually require to recover the end-depth ratio?** Is there a documented minimum, or
a statement that the brink region needs local refinement? Are there other cheap
free-surface benchmarks with a scale-free target ratio that would be better suited
to a coarse domain?

**4. Image or mirror particles at MPM walls, and whether they need a writable stress
state.**
Schulz & Sutmann argue that a wall implemented by zeroing grid momentum distorts the
stress several grid lengths into the body, and propose image particles. I implemented
a host-side mirror in a fixed pool and it made wall penetration **monotonically
worse**: -2.1, +7.4 and +32.2 percent at 500, 2000 and 6000 images, then instability.
My hypothesis is that the images inject spurious pressure because they cannot inherit
their source's compression state. **Does the image-particle literature require the
image to carry the source's stress or deformation state, and does any published
implementation work without that?** Please find the primary Schulz & Sutmann
reference and any independent reimplementations, plus any reported failure modes.

**5. Grid boundary conditions versus multi-material contact for a rigid body in MPM.**
Zhou et al 2025 represent a pavement as rigid material points in a multi-material,
multi-velocity-field contact framework rather than as a boundary condition on grid
nodes. My code uses a grid-node velocity condition on a plane, and separately offers
a signed-distance-field collider. **What is the published comparison of these three
approaches for fluid-rigid contact in MPM, in terms of penetration, spurious stress
and force accuracy?** I want the contact-algorithm lineage (Bardenhagen, Nairn,
Huang and successors) assessed for which one is appropriate when the rigid body is
free to move under the fluid load, not kinematically prescribed.

**6. Sub-grid roughness for terrain when the texture is far smaller than a cell.**
Zhou et al resolve pavement micro-protrusions explicitly, but their domain is a water
film 0.3 by 0.22 m and under 1 mm thick. My cell is 0.147 m and a real road texture
depth is a few millimetres, roughly one fiftieth of a cell, so explicit resolution is
impossible. **Is there a published sub-grid or effective-roughness treatment for MPM
or SPH over terrain, and has anyone quantified what is lost by replacing resolved
roughness with an effective friction coefficient in a free-surface flow over a
road-like surface?** A negative answer here is a genuine result for me.

**7. Artificial sound speed and whether it can change a rigid-body outcome.**
My scheme uses a reduced bulk modulus giving a numerical sound speed of 12.85 m/s,
which is below the common requirement that it exceed ten times the maximum flow
velocity for flows at and above 1.5 m/s. Zhou et al by contrast use the real 1480 m/s
with a Grueneisen equation of state. **What is published on the sensitivity of
rigid-body motion outcomes, specifically incipient sliding or flotation, to the
artificial sound speed in weakly compressible particle methods?** Is the ten-times
rule attributable to a specific primary source with a derivation, and is there a
documented case where a discrete outcome such as "moves or does not move" flipped
with the sound speed alone?

**8. Which friction coefficient applies to a wheel-less solidified hull.**
Three values are in play for what is nominally the same interface: 0.7 for a rolling
tire on pavement, 0.30 measured for locked wheels, 0.0242 measured for a free-rolling
vehicle at washaway, and my code uses an unsourced 0.55 as a Coulomb coefficient in a
grid boundary condition acting on a hull with no wheels at all. **Is there published
guidance on what the correct effective coefficient is when a vehicle is modelled as a
solid body without wheels or suspension?** Has anyone modelled the wheel contact
explicitly in a flood-vehicle simulation, and if so what difference did it make to
the incipient-motion threshold?

**9. Whether the bounded-domain artefact is documented.**
Measured: in a closed box with an upstream velocity forcing, water piles against the
downstream wall and produces a spurious free-surface slope of 0.093 m/m at zero bed
slope, which is 1.8 times the true bed slope of a 3 degree road. The artefact exceeds
the signal it would mask. **Has this been quantified in any published particle-method
study, and is there a standard minimum domain length, expressed in flow depths or
body lengths, for a free-surface simulation intended to resolve a bed slope?**

## What I want back

For each numbered question: whether the literature settles it, the best two or three
primary sources with DOIs, the specific quantitative result or method if there is
one, and an explicit "no published treatment found" where that is the honest answer.
Prefer primary sources over reviews. Flag any paper that reports a failure or a
negative result, because those are more useful to me here than success stories.
Where a source is paywalled, say whether an open-access version exists.
