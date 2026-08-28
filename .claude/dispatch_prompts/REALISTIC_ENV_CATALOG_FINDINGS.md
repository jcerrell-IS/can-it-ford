# THE SIXTH BLOCKER: WE NEVER READ OUR OWN CATALOG
2026-08-14 23:41 CEST. Read live from the report tables tonight, not recalled.

I answered Josie's "why no realistic environment" from the reports' **Summary of
Results** sections only. That was the wrong depth. Reading the actual **paper
catalogs** changes the answer, because the catalogs contain papers that solve or
directly address the exact problem, and **not one of them has ever been cited in
this project.**

Source tables, both read in full tonight:
`01_Solver_Physics_and_Coupling/2026-08-14_undermind-report_multi-resolution-mpm-large-domain-flooding_CURRENT.md` (78 papers)
`04_Validation_Literature_and_Citations/2026-08-14_undermind-report_moving-rigid-body-free-surface-validation_CURRENT.md` (44 papers)

## A. VEHICLE FORDING HAS BEEN SIMULATED BEFORE. FOUR TIMES. NONE IS CITED HERE.

**A1. Wasfy, Wasfy and Peters 2015, DETC2015-47142, "Coupled Multibody Dynamics
and Smoothed Particle Hydrodynamics for Modeling Vehicle Water Fording".**
Appears in BOTH catalogs (moving-rigid #38, multi-res #56). This is literally
this project's problem, solved with multibody dynamics plus SPH, eleven years
ago. It must be in the related-work section. Its architecture is also the
answer to a question this project keeps re-deriving: the vehicle is a multibody
system coupled to a particle fluid, not a free rigid blob.

**A2. Pazouki, Jayakumar and Negrut 2016, "Investigation of the Vehicle Mobility
in Fording"** (moving-rigid #39). **These are the Chrono authors.** Pazouki and
Negrut are already cited in register A-1 for rigid-coupling architecture. So the
Chrono team has published on fording, and D13's Chrono go/no-go was conducted
without reading it. This bears directly on whether Chrono is the right host for
a realistic environment.

**A3. Khapane and Ganeshwade 2014, SAE 2014-01-0936, "Wading Simulation,
Challenges and Solutions"** (moving-rigid #40). An SAE paper whose entire subject
is the challenges of simulating wading. Unread.

**A4. He et al. 2026, "Predicting Vehicle-Water Interaction in Shallow Water:
Simulations and Experimental Validation", J. Computational and Nonlinear
Dynamics, doi 10.1115/1.4071177** (moving-rigid #1). This is the He 2026 already
referenced as validating transient response at model scale. Now it has a DOI and
a journal, so it can be cited properly.

**Consequence for the paper.** The line "no validated vehicle-fording MPM chain
is identified" is still true as written, because A1 and A2 are SPH and multibody,
not MPM. But "nobody has simulated vehicle fording" is FALSE and must never be
written. The novelty claim has to be narrowed to the MPM-plus-validation
combination, and A1 through A4 have to appear as related work.

## B. MPM ON A REAL ROAD SURFACE ALREADY EXISTS. TWO PAPERS.

**B1. Zhou et al. 2025, "Analysis of tire-pavement viscous hydroplaning based on
the material point method", Physics of Fluids, doi 10.1063/5.0276643**
(multi-res #40). **MPM, a tyre, a pavement, and a water film.** This is a
realistic road environment in MPM with a vehicle contact patch. It is the single
most on-target paper in either catalog for "make the environment realistic" and
nobody has opened it.

**B2. Chen et al. 2022, DETC2022-89632, "Modeling Large Deformable Terrain With
Material Point Method for Off-Road Mobility Simulation"** (multi-res #17). MPM
terrain under a vehicle, for mobility. The terrain-plus-vehicle problem, in MPM.

Together B1 and B2 refute the framing that MPM cannot host a realistic road.
The blockers B1 through B5 in `REALISTIC_ENVIRONMENT_PLAN.md` are about **our**
implementation, not about MPM as a method. Restate them that way.

## C. THE LOCKED VALIDATION BENCHMARK NOW HAS A NAME

The "unusually precise public benchmark, approximately 0.3 percent experimental
uncertainty" is **Kramer et al. 2021, "Highly Accurate Experimental Heave Decay
Tests with a Floating Sphere: A Public Benchmark Dataset for Model Validation of
Fluid-Structure Interaction", Energies 14(2):269, doi 10.3390/en14020269**
(moving-rigid #20). A **public dataset**, a floating sphere, heave decay. That is
the standing regression case Phase 1 of the deployment order asks for, and it is
downloadable rather than something we must build.

Note this is the SAME Kramer already in the register at line 228 for the 2016
watertightness prototype finding. Different paper, same author. Do not merge them.

## D. THE ROUTE TO A LARGE DOMAIN, RANKED, WITH CITATIONS

Every one of these is in the multi-resolution catalog and none is cited here.

**D1. Hybrid 3D near-vehicle plus 2D far-field.** The only approach that makes a
road-scale domain affordable without refining everywhere.
  - Pan et al. 2023, "Variable passing method for combining 3D MPM-FEM hybrid and
    2D shallow water simulations", Int. J. Numer. Meth. Fluids, doi 10.1002/fld.5233
  - Zheng et al. 2023, "A material point/finite volume method for coupled shallow
    water flows and large dynamic deformations in seabeds", doi 10.1016/j.compgeo.2023.105673
  - Suchde 2024, "Particle-based adaptive coupling of 3D and 2D fluid flow
    models", doi 10.1016/j.cma.2024.117199
  - Fois, de Falco and Formaggia 2024, semi-conservative depth-averaged MPM,
    doi 10.1016/j.cnsns.2024.108202

**D2. Sparse and octree grids, for domain size not floor resolution.** The report
warns these do NOT reduce the smallest-cell timestep and do NOT resolve the floor
layer, so use them for extent only.
  - Qiu et al. 2022, "A Sparse Distributed Gigascale Resolution MPM", TOG, doi 10.1145/3570160
  - Zhao et al. 2026, "Unified sparse framework for large-scale MPM", arXiv 2605.28525
  - Bird, Coombs, Augarde and O'Hare 2026, implicit octree-based adaptive MPM

**D3. Moving refinement window, the thing the report says nobody has done.**
  - Luo, Li and Jiang 2026, "An Overlapping Schwarz Space-Time Refinement
    Framework for MPM", arXiv 2605.09097. Space-time refinement is the closest
    published machinery to a window that follows a vehicle.
  - Huang et al. 2021, "Ships, splashes, and waves on a vast ocean", TOG,
    doi 10.1145/3478513.3480495. A moving body in an effectively unbounded
    free-surface domain. Graphics, not validated, but it is the shape of the
    problem.
  - Gao, Tampubolon, Jiang and Sifakis 2017, adaptive GIMP, doi 10.1145/3130800.3130879

**D4. The open boundary, already chosen and now confirmed in the catalog at #7.**
  Zhao, Bolognin, Liang, Rohe and Vardon 2019, doi 10.1016/J.COMPFLUID.2018.10.007.

**D5. The PPC trap, catalogued at #4, and TESTED BY US TONIGHT.** Steffen,
Wallstedt, Guilkey, Kirby and Berzins 2008, doi 10.3970/CMES.2008.031.107. The
report calls it decisive for AMR. D9 co-refined PPC tonight and **refuted** it as
the mechanism in this scene, finding band width dominant instead. So we now have
a result the catalog does not: the trap is real in general but is not what bites
here.

## E. TWO CITATIONS THIS CONFIRMS INDEPENDENTLY

- **mu = 0.55 is Azhar, Pauwels and Bui 2023**, "Confirmation of vehicle
  stability criteria through a combination of smoothed particle hydrodynamics and
  laboratory measurements", J. Flood Risk Management, doi 10.1111/jfr3.12885
  (moving-rigid #37). This independently confirms D11's provenance chain and
  artifact 65474f37, from a third source. Note it is an **SPH** paper.
- **Bonham and Hattersley 1967 is "LOW LEVEL CAUSEWAYS"** (moving-rigid #15).
  Confirms D4's finding that the 0.3 convention is their assumption carried
  forward, and gives it a title.
- **Shah, Mustaffa, Martinez-Gomariz and Yusof 2020** (moving-rigid #4),
  doi 10.1111/jfr3.12657, **year 2020 in the catalog**, which matches the
  Crossref result of 2020-07-28 and confirms that re-dating it to 2021 was wrong,
  for the third independent time.

## WHAT TO DO WITH THIS

The environment plan in `REALISTIC_ENVIRONMENT_PLAN.md` stands, but its framing
was too pessimistic and its blockers must be restated as **implementation**
blockers rather than method blockers, because B1 and B2 prove MPM can host a
road. And the related-work position changes: this is not the first vehicle
fording simulation, it is the first that pairs MPM with validation, and A1
through A4 must be cited or a reviewer will find them.
