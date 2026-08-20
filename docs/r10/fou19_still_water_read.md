# Fou19 read from full text: a 10 percent boundary pressure error in still water, and why its fix does not port

Slot d22-gapscan, 2026-08-20. Read from the acquired PDF using the Swift PDFKit
extractor in `docs/r10/pdftext.swift`, not from an abstract.

Fourtakas, Dominguez, Vacondio and Rogers (2019), "Local uniform stencil (LUST)
boundary condition for arbitrary 3-D boundaries in parallel smoothed particle
hydrodynamics (SPH) models", Computers and Fluids 190, 346-361,
`10.1016/j.compfluid.2019.06.009`. **CC BY**, so redistributable.

## Why it matters here

Two of this project's open questions are a vertical force that reads 34 to 64
percent above analytic buoyancy, and a hydrostatic column whose kinetic energy
grows instead of decaying. Fou19 measures both symptoms in a still-water tank
and traces them to one term.

**Read directly from section 6.2**, a 1 x 1 x 1.2 m tank, water depth 1 m,
gravity only, a pyramid on the floor to force corners and slopes, three
resolutions to 869,450 particles:

- "the uncorrected density diffusion term shows **a dip in the pressure near the
  wall boundary on the order of 10% of the total pressure**", eliminated by
  their correction.
- with the correction "results obtained ... are in agreement with the analytical
  solution and **the velocity magnitude is reduced by an order of magnitude**".
  In a still tank the analytic velocity is zero, so that is spurious motion an
  order of magnitude too large before the fix.
- their Figure 16 is **"Kinetic energy evolution time for the 3-D still water
  with pyramid"**. That is precisely this project's question b diagnostic, used
  as a pass criterion by a published group.
- convergence orders once corrected: about 1.3 for velocity, 1.1 for pressure.

The mechanism, equations 15 to 17: the density diffusion term must operate on
the **dynamic** density, `rho_D = rho_T - rho_H`, because "only the hydrostatic
part of the pressure is needed". Left on total density, the term diffuses the
hydrostatic component across the wall and produces the pressure dip.

## THE FIX DOES NOT PORT, AND SAYING SO IS THE POINT

Checked live against the vendored solver rather than assumed:

- `third_party/mpm-engine-544c93dd-solver-core/materials/__init__.py:125`
  defines `newtonian` as a "Weakly-compressible generalized-Newtonian fluid
  (EOS + 2 eta dev D)".
- `kernels/mpm_utils.py:43` forms `pressure = -bulk * (J^-gamma - 1.0)` and
  `:53` assembles `cauchy = id * pressure + 2.0 * eta_app * D_dev`.
- A `/usr/bin/grep -rniE "density.?diffusion|delta.?sph|artificial.?visc"` over
  the whole vendored tree returns **nothing**.

So the solver is a Tait equation of state plus a Newtonian deviatoric term and
**carries no density diffusion term at all**. Fou19's correction has nothing to
correct here. Do not write it up as an available fix, and do not let the 10
percent figure migrate into a claim about this solver.

## What DOES transfer

1. **The diagnostic and its pass criterion.** A still-water tank with kinetic
   energy plotted against time is an established published test, and the
   expected behaviour is decay. This project's column does the opposite. That
   makes question b a documented failure of a standard test rather than an
   internal curiosity.
2. **The magnitude scale.** A boundary treatment defect in a still tank bought
   10 percent of total pressure and a factor of ten in spurious velocity in a
   published SPH code. That is the right order to expect from a boundary defect,
   and it is well short of 34 to 64 percent, which weakly argues that a boundary
   term alone is not the whole of this project's force excess.
3. **Arbitrary geometry is solved, and it is the thing Sch19e cannot do.** LUST
   handles "complex arbitrary geometries without the need of special treatments
   for corners and curvature", using triangles plus ray tracing. Sch19e's image
   particles support "only boxes". If this project ever wants a principled
   boundary treatment on the hull rather than the tank walls, LUST is the
   family that admits curvature, and Sch19e is not.

INFERRED, NOT READ, and flagged as such: MPM's analogue of Fou19's total-versus-
dynamic density split is the Jacobian J, since pressure here comes entirely from
J. Whether the grid transfer mixes hydrostatic and dynamic parts of J across a
boundary in the way Fou19 describes for SPH is a real question, but no source in
this document establishes it and nobody has tested it.
