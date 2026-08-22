# Sch19e read from full text, and it does not support the claim it was relayed for

Slot d22-gapscan, 2026-08-19/20. Everything below is READ DIRECTLY from the PDF
unless tagged otherwise.

## Acquisition

Schulz, Stephan and Sutmann, Godehard (2019). "A Consistent Boundary Method for
the Material Point Method - Using Image Particles to Reduce Boundary Artefacts."
PARTICLES 2019, VI International Conference on Particle-Based Methods:
Fundamentals and Applications, Barcelona, 28-30 October 2019. CIMNE, Barcelona,
pp. 522-531. ISBN 978-84-121101-1-1.

Undermind holds no PDF for it, Semantic Scholar has no DOI for it (CorpusId
235273972 only), and the Julich repository record FZJ-2019-06605 marks it
`info:eu-repo/semantics/closedAccess`. It was obtained anyway, from UPCommons
(Universitat Politecnica de Catalunya), which hosts the whole PARTICLES 2019
proceedings openly:

    handle   2117/186795
    uuid     66d81f4b-635b-40aa-b71b-75b0732496eb
    file     Particles_2019-47-A consistent boundary method.pdf
    HTTP 200, application/pdf, 3,740,068 bytes
    sha256   a41cc8516469d472c4a3b70aac0b7ae8f525c6e261dd9bd6e506eae5ce8d873a
    saved    ~/can-it-ford-refs/2026-08-19-r10/Schulz2019_ImageParticles_Particles2019_522-531.pdf

Why every title search missed it: UPCommons records the title with a typo,
"using **imge** particles". Matching on the corrected title returns nothing.

## What the paper actually says

CONFIRMED, and the relayed wording was right. The abstract states that explicit
boundary methods "such as setting the grid momentum to zero for grid nodes
inside a fixed wall" cause stress artefacts for an object in touch with the
wall, and that these "distort the stress multiple grid lengths into the object."
Section 3.1 repeats it: the oscillations "are quite wide and reach multiple grid
widths into the material."

The penetration depth is not free. The paper ties it to the interpolation
stencil: the buffer object is "two grid widths deep, which equals the
penetration of the used transfer function." So the artefact depth is set by the
transfer function support, not by the physics of the problem.

## THREE REASONS IT CANNOT CARRY THE +34 TO +64 PERCENT SPHERE RESULT

**1. The material is an elastic solid, not a fluid, and the measured quantity is
deviatoric.** Section 3 uses Hooke's law, equation (16), with Young's modulus
Y = 1x10^4 Pa and Poisson ratio nu = 0 (Table 1). The two cases are a cube under
a body force between no-slip walls, and simple shear. There is no fluid, no free
surface, no buoyancy and no immersed body anywhere in the paper. The reported
quantity is von Mises stress, equation (17), which is by construction blind to
the hydrostatic part of the stress tensor. A buoyancy force is a pressure
integral, that is, the volumetric part. The paper measures the component that a
buoyancy error is not made of.

**2. Refinement fixes the Schulz artefact, and refinement does not fix ours.**
Section 3.1, read directly: reducing the grid width by a factor of five, from
dh = 0.05 m to dh = 0.01 m (64,000 particles to 8,000,000) gives this, quoted
exactly: "The stress distribution is now correctly modelled inside the object." The project's sphere
excess persists across 24 gradings under refinement. A mechanism that refines
away cannot be the mechanism behind an error that does not.

**3. The method is defined only for boxes, so it cannot be applied to the
sphere or the hull.** Stated by the authors: image charges work by
anti-symmetry, a second boundary "must also be anti symmetric to the first,"
which "can only be satisfied for a perpendicular plane. Therefore, complex
boundaries are not supported, but only boxes." Unaligned planar boundaries are
possible at extra cost; curved ones are not addressed at all.

## Adjudication of the board dispute

d14-corpusbib flagged a tension: a deep search cites [Sch19e] for wall momentum
zeroing distorting stress, while d19-priorcode reports `simulation/image_particles.py`
implemented, run, and REFUTED. Both can be true with no contradiction. The
published method is defined for planar, axis-aligned walls bounding an elastic
solid. The project needs a curved, fluid-immersed body. If the implementation
was exercised on the sphere or the hull, it was exercised outside the domain of
validity the authors state in the paper. The refutation is evidence about this
repo's use of the method, not about the method.

## What it DOES bear on, and it is not the buoyancy question

**Settling time, which is open question b.** Time to steady state, read directly
from the end of section 3.1: the explicit boundary condition "has not converged
after 1000 time steps (0.1 s), with the main change still occurring in the
boundary region of large artefacts"; the buffer object reaches it in about 250
steps; image particles in about 100 steps. A ten-fold difference in settling
time driven purely by boundary treatment, with the explicit method still moving
at 1000 steps. The project's hydrostatic column never goes quiet and its
boundaries are explicit. That is a shared symptom and a testable one, and it is
a better use of this paper than the force claim.

**A direct warning about boundary objects changing forces**, section 2.3.3:
"since the boundary is defined using the acceleration of the boundary layer
particles, the thickness and width changes the total force acting on the object.
Care must be taken when setting up the system to get the desired forces." This
applies to the boundary-object method, not to image particles.

## Cost, as reported

Buffer object: about 50 percent longer run time than explicit. Image particles:
difference from explicit "within the margin of error", because no new particles
are created, the transfer is just duplicated with sign changes.
