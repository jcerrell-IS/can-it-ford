# R7: Job B is not running the benchmark it cites, and its pass criterion has no source

Investigated 2026-08-18 after the boundary 2x2 showed that eliminating 99.8 percent of the
floor leak removes only 30 percent of the force error, which means a third error source
dominates. This is what that investigation found. Literature via an Undermind deep search,
[workspace link](https://app.undermind.ai/projects/17299f2a-8dc8-438b-8c84-5abf19395e2c).
Every DOI below was resolved and its title checked against the resolved record, not merely
followed.

## 1. THE FINDING

`sphere_heave.py` names its benchmark in its own provenance block:

```
benchmark_doi   10.3390/en14020269
testcase_read   D=300mm; m=7.056kg; CoG=(0,0,-34.8)mm; g=9.82; H0={30,90,150}mm;
                rho_w=998.2; d=900mm; 4 repetitions per drop height
```

That is Kramer et al. 2021, *Highly Accurate Experimental Heave Decay Tests with a Floating
Sphere: A Public Benchmark Dataset for Model Validation of Fluid-Structure Interaction*,
Energies. **The benchmark choice is correct and well made.** A 300 mm sphere ballasted to
half submergence, with a public time-series dataset and quantified experimental uncertainty,
is close to ideal for this project.

**Job B does not run its case.** Read live from the run config of job 918526:

| | Kramer 2021 specifies | Job B ran |
|---|---|---|
| body | **released from rest** at H0 = 30, 90, 150 mm | `free = False`, `h0_over_d = 0.0`, held fixed |
| tank depth | **900 mm** | `depth_m = 0.5`, i.e. 500 mm |
| graded quantity | **heave decay time series** | a **static force ratio** vs analytic buoyancy |
| tolerance | **0.3 % of drop height** (0.09 / 0.27 / 0.45 mm absolute) | a self-set 10 / 25 % band |

**So Job B holds the sphere still in a tank of the wrong depth and grades a quantity the
benchmark does not report, against a tolerance the benchmark does not state.** The criterion
it fails is one the project invented. That is the systematic defect, and it is upstream of
every mechanism the last two rounds chased.

**This does not make the FAIL go away.** A +36 percent error against a closed-form hydrostatic
result is still a real disagreement and still needs explaining. What it does mean is that
"the ladder is stopped by criterion 3" is stopped by a criterion with no external warrant,
while the actual published validation, which has an external warrant and public data, has
never been run.

## 2. WHAT THE LITERATURE SAYS ABOUT THE MECHANISM

Deep search over the scholarly literature. The honest headline is that **it does not supply a
mechanism that predicts a 50 percent positive bias**, and it explicitly does not establish
that velocity-projection impulse exchange double counts gravity for a fixed body.

What it does support:

- **Weakly compressible MPM is known to behave badly exactly at a free surface.** Zhang et al.
  2017, *Incompressible material point method for free surface flow*, J. Comput. Phys.,
  `10.1016/j.jcp.2016.10.064`, introduces a projection/incompressible MPM specifically because
  the weakly compressible formulation performs poorly there. A half-submerged sphere lives on
  the free surface, so this is the most directly relevant strand. Chen et al. 2018, *v-p
  material point method for weakly compressible problems*, Computers & Fluids,
  `10.1016/J.COMPFLUID.2018.09.005`, is the companion.
- **Hydrostatic tests are the standard probe for MPM integration and quadrature error**, and
  quadratic B-splines reduce but do not eliminate particle-location sensitivity. Steffen,
  Kirby and Berzins, *Analysis and Reduction of Quadrature Errors in the Material Point
  Method*, IJNME (no DOI on record, Semantic Scholar `da8e9159`), and Baumgarten and Kamrin
  2023, *Analysis and mitigation of spatial integration errors for the material point method*,
  IJNME, `10.1002/nme.7217`.
- **The force-extraction route is a real design choice with published alternatives.** Akinci
  et al. 2012, *Versatile rigid-fluid coupling for incompressible SPH*, ACM TOG,
  `10.1145/2185520.2185558`, and Hu et al. 2018, *A moving least squares material point method
  with displacement discontinuity and two-way rigid body coupling*, ACM TOG,
  `10.1145/3197517.3201293`, both accumulate contact force rather than reading a velocity
  projection. Li et al. 2022, `10.1016/j.cma.2022.114809`, is the immersed-FEM route.
- **The gap in the field is our diagnostic list.** The search reports that published work
  rarely states force-extraction windows, rarely cross-checks impulse exchange against a
  pressure-surface integral, and rarely presents particles-per-cell convergence for the body.
  Those three are exactly what this case needs and exactly what it lacks.

## 3. A CANDIDATE MECHANISM I TESTED AND COULD NOT SUSTAIN

Recorded because it was close to persuasive and it is worth not re-deriving.

A half-submerged sphere's buoyancy scales as radius cubed, so a collider whose EFFECTIVE
radius is inflated by a skin of thickness delta reads high by `(1 + delta/r)^3 - 1` while the
analytic target, computed from the true radius, does not move. Solving for delta from each
measured cell:

| cell | ratio | implied delta |
|---|---|---|
| control 918240 | 1.5122 | 22.17 mm = **1.18 dx** |
| engine fix | 1.35233 | 15.88 mm = **0.85 dx** |
| ghost fix | 1.38029 | 17.01 mm = **0.91 dx** |
| combination | 1.35918 | 16.16 mm = **0.86 dx** |

All four land within about one grid cell, which is the SDF band (1.00 dx) and the quadratic
B-spline support half-width (1.50 dx). The sphere spans only 16 cells across its diameter, so
a one-cell skin is a 36 percent volume error.

**REFUTED as a general mechanism, by the only other SDF-collider buoyancy measurement in the
project.** Read live from `docs/CONTEXT_CENSUS_2026-08-07.md:1049-1052`, the vehicle hull
gives `err_steady_vs_analytic_pct` of **-7.668 at g64 and +7.280 at g96**, and the box
collider **-37.912 and -21.276**. A universal one-cell skin predicts a large POSITIVE bias
scaling with dx over body radius, which for the hull at g64 would be roughly +54 percent. The
measured value is negative, and the sign flips between two grids. A hypothesis fitted with one
free parameter to four similar numbers, that then fails to transfer and gets the sign wrong,
is not established.

**It is still worth ONE cheap test**, because the sphere and the hull are different scenes and
different code paths. Hold everything and sweep `n_grid` 64, 96, 128 on the fixed sphere. The
skin hypothesis predicts +37.7, +24.2, +17.8 percent, a clear fall roughly as dx. It is refuted
if the error is flat in `n_grid`, and refuted differently if it falls faster than first order.
At `n_grid` 128 this is about 4.8 M particles and a few minutes, so it costs 1 to 2 SU.

## 4. WHAT TO REPLICATE, in order

1. **Run Kramer's actual case.** Free sphere, released from H0 = 30, 90, 150 mm, tank depth
   900 mm, and compare the heave time series against the public dataset using the paper's own
   0.3-percent-of-drop-height uncertainty. This replaces an invented criterion with an
   external one and tests the dynamic response, added mass and damping, rather than a static
   number. The driver already supports `--h0-over-d` and free mode, so the code exists.
2. **Fix the tank depth** to 900 mm regardless of anything else. It is a one-argument change
   and it is currently wrong by a factor of 1.8 against the cited source.
3. **Cross-check the force accessor** against a pressure-surface integral on the same run. The
   deep search reports this cross-check is rare in the literature, which makes it both a real
   diagnostic here and a small publishable contribution.
4. **Sweep `n_grid` on the fixed sphere**, to close out section 3 either way.
5. Only then revisit the static-force criterion, and if it is kept, state in writing that it is
   a project-internal criterion with no source in the cited benchmark.

## 5. WHAT THIS DOES AND DOES NOT CHANGE

- It does **not** overturn the +36 percent measurement, which stands and is reproducible.
- It does **not** reinstate "Job B is NOT GRADEABLE", which remains refuted.
- It **does** mean the sentence "any FAIL stops the ladder" is currently being enforced by a
  criterion with no external warrant, applied to a run that is not the benchmark case.
- The Job B decision is therefore better framed as a third option alongside accept-the-FAIL and
  amend-the-criterion: **run the benchmark that was actually cited**, and grade against its own
  published tolerance.
