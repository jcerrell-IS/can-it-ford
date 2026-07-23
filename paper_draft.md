# Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability

**Author:** Josie Cerrell
**Institution:** Claremont McKenna College / GeoElements Lab, TACC/UT Austin
**Date:** July 2026

---

## Abstract

Background. Flooded roads are a leading cause of vehicle fatalities: over half of all flood-related drownings occur when a vehicle is driven into hazardous floodwater. Drivers and autonomous vehicles alike cannot judge water depth, flow velocity, or submerged road condition from appearance alone. Appearance-predictive world models share this blind spot, producing outcomes that look plausible but violate the underlying physics. Physically viable world models, which preserve the latent physics governing action outcomes, offer a principled alternative.
Objective. This project asks a deliberately narrow query: can a specific autonomous vehicle ford a specific flooded road? Rather than building the highest-fidelity simulation possible, it identifies the simplest physical abstraction sufficient to answer that query correctly, directly instantiating the query-conditioned world-model framework of Thorpe et al. (2026).
Methods. A flooded-road scene is reconstructed in 3D using Gaussian splatting. Following the PhysGaussian framework, Gaussian kernels are intended to seed a continuum particle representation that will initialize a Material Point Method (MPM) simulation in the Genesis physics engine, with rigid-MPM coupling allowing a rigid vehicle body to interact with weakly compressible floodwater. A synthetic-geometry SPH pilot currently validates the abstraction-ladder logic ahead of this migration. Three levels of physical fidelity are compared: (0) a static depth threshold derived from published flood-vehicle stability data (Smith, Modra & Felder 2019), (1) a depth-velocity stability criterion from the Australian Rainfall and Runoff guidelines, and (2) a full coupled simulation where feasible within the project timeline. All simulations run on NVIDIA A100 GPUs at TACC.
Expected Results. The coupled simulation is expected to reproduce empirical instability thresholds documented in the flood-vehicle stability literature, with vehicle float onset near published depth limits and sliding onset governed by the depth-velocity product. The central finding is expected to be that the minimal sufficient abstraction is query-dependent: a simple depth threshold correctly resolves deep, still-water scenarios, while fast, shallow flow requires the full coupled model to return a physically correct answer.
Significance. This work delivers a closed reconstruct-to-decide pipeline and a concrete, testable instantiation of query-conditioned, physically viable world models for a real safety application. It provides the first concrete instantiation of the abstraction-selection orchestrator that the PVWM framework leaves as an open problem.


---

## 3. Methods

### 3.1 Vehicle Representation

The validated coupled-simulation results (the v2 sweep, 24 of 36 cells retained after filtering) were produced with box-proxy vehicle geometry, not with a real vehicle mesh. Two passenger-vehicle classes are cited: a compact sedan and a light pickup. A midsize SUV class was also run but is excluded from all reported results because its solidified proxy is density-implausible (308.13 kg/m3, outside the 100 to 300 kg/m3 fill-quality band). Each proxy is built by scaling a single source surface anisotropically to the target class bounding box, so that per-class mass, bounding box, displaced volume, and side-on drag area are correct while the sub-bounding-box shape detail is shared rather than class-specific. Class curb mass and bounding box are drawn from manufacturer specification sheets, with center-of-gravity height and inertia from the NHTSA measured inertial-parameter database (SAE 1999-01-1336), collected in vehicle_params.py. Vehicle density is not prescribed; it is derived post hoc (class mass divided by solidified particle volume) and used only as a plausibility check.

The two cited classes are the compact sedan (1390 kg, 4.66 m length, Toyota Corolla / Honda Civic anchors) and the light pickup (2300 kg, 5.89 m length, Ford F-150 anchor).

Under the Australian Rainfall and Runoff vehicle-stability guidelines (Shand et al. 2011, AR&R Project 10, Table 3), these two proxies fall in different classes than a naive subcompact reading would imply:

- The sedan (1390 kg, 4.66 m) exceeds both the 1250 kg and 4.3 m Small Car limits, placing it in the Large passenger car class: limiting depth-velocity product D times V less than or equal to 0.45 m2/s, limiting still-water depth 0.40 m.
- The pickup (2300 kg, 5.89 m) exceeds the 2000 kg and 4.5 m limits, placing it in the Large 4WD class: limiting D times V less than or equal to 0.60 m2/s.

This corrects a classification error in an earlier draft, which assigned the vehicle to the Small Car class (D times V less than or equal to 0.30 m2/s, depth 0.30 m). That Small Car classification is correct only for the real 1100 kg, 4.30 m Toyota Yaris geometry, which is a separate and not-yet-validated capability: the --vehicle yaris path in ford_sweep_driver.py was wired in this week and is still under validation after a mass-assignment bug was found. It does not describe the box-proxy sedan and pickup that produced the cited results.

These AR&R thresholds serve as the L1 stability criterion, but the source itself labels them "draft, interim," not a permanently validated standard. They are treated accordingly here and are not presented as a settled regulatory limit.

<!--
SUPERSEDED DRAFT TEXT (retained for reference, not live prose, not a code comment).
The prior Section 3.1 below described the real Toyota Yaris FE mesh as the evaluated
vehicle. This was aspirational: the Yaris mesh had produced no validated result at the
time of writing, and the AR&R Small Car classification it invoked applies only to that
mesh, not to the box-proxy sedan and pickup that produced the v2 sweep. Kept verbatim in
case the Yaris capability is validated and reinstated.

The vehicle evaluated is a subcompact sedan, represented by the 2010 Toyota Yaris
finite-element model developed by the Center for Collision Safety and Analysis and
validated against full-scale crash tests. This is a real, crash-validated vehicle
geometry (measured curb mass 1100 kg, body envelope 4.30 by 1.70 by 1.47 m), not a
generic mid-size sedan placeholder. Under the Australian Rainfall and Runoff
vehicle-stability guidelines (Shand et al. 2011), a vehicle of this mass and size falls
in the Small Car class, the most conservative of the three passenger classes, with a
limiting still-water depth of 0.30 m and a limiting depth-velocity product of 0.30 m2/s.
Adopting the real subcompact geometry therefore places the L1 stability criterion in its
correct and most conservative class, rather than the more permissive class a larger
placeholder would have implied.
-->


### 3.2 PVWM Framing

The three-level abstraction ladder instantiates the orchestrator described in Section 3 of Thorpe et al. (2026) as the first running implementation. The PVWM paper identifies automatic abstraction selection as the central open problem and provides no committed orchestrator code. Our orchestrate_ford_query() function represents the first concrete implementation, with the empirical divergence zone at d greater than or equal to 0.25m, v greater than or equal to 1.2 m/s, and D times V less than 0.60 m2/s defining the L1-to-L2 escalation boundary. At this boundary, the scalar criterion structurally lacks the mechanism to represent directional persistent lateral drag, independent of threshold value or vehicle class. 

### 3.3 Rigid-Fluid Coupling in the MPM Solver

The Track 1 sweep (Section 4.3) couples the vehicle to the floodwater inside a single Material Point Method particle array, using the mpm-engine solver (kks32/mpm-engine). Water and vehicle are not separate simulation objects. The water slab and the solidified vehicle particle set are concatenated into one particle array, and the entire array is first assigned the weakly compressible newtonian fluid material.

The vehicle is then marked rigid in place, rather than added as a distinct body. set_material_range(n_water, n_total, "rigid", obj_id=0, density) re-tags the contiguous index range holding the vehicle particles as a single rigid body (obj_id 0), leaving the leading range as fluid. finalize_rigid_bodies() locks that registration before the first step. From that point the vehicle particles are slaved to one rigid-body pose: each substep, the fluid's grid momentum accumulates into the body's net force and torque, and the body translates and rotates as one piece. Sliding, floating, and overturning are therefore emergent outcomes of the two-way coupling, not prescribed behaviors.

Static boundaries are defined separately from the particle array. add_plane(point, normal, "slip", friction, restitution) places the floor and the four domain walls as slip planes. The floor carries a small restitution so the rigid body has a contact surface it cannot sink through, because the grid boundary condition alone constrains only the fluid. The water slab is seeded upstream of the vehicle with a gap, so in this solver no fluid particle is initialized inside the rigid body.

### 3.4 Open Issue in the Genesis Coupled-MPM Path

The coupled-MPM target path, a rigid vehicle immersed in Genesis MPM floodwater, is not yet numerically stable and did not produce any of the results reported in Section 4. It fails with a crash at the particle-to-grid (P2G) transfer stage, which is confirmed and reproducible. Diagnosis is ongoing; the issue is open, not resolved, at the time of writing. Two hypotheses have been tested so far, and neither has been conclusively confirmed as the root cause. The first is a static starting overlap: water particles seeded inside the vehicle body at initialization. Repositioning the water slab to remove that starting overlap does not prevent the crash (under gravity the repositioned slab still slumps toward the vehicle before the P2G failure recurs), which weakens this explanation but does not eliminate it. The second is insufficient clearance between the particle configuration and the domain boundary, associated with the widened domain bounds introduced alongside the sedan-scale geometry. Neither hypothesis has been isolated cleanly enough to be called the confirmed cause, and we report this as ongoing work. The coupled-MPM traversability verdicts this path is intended to produce are correspondingly not reported here: every result in Section 4 comes from the SPH pilot, and none should be read as a coupled-MPM verdict.

---

## 4. Results

All primary structural results in this section come from the Genesis SPH pilot: a synthetic-geometry, weakly compressible SPH stand-in for the coupled MPM simulation the pipeline targets. They establish the structure of the abstraction-selection argument. They are not the final coupled-MPM traversability verdicts for a reconstructed scene, and that distinction is carried explicitly through every number reported here (Section 4.5).

### 4.1 The abstraction ladder diverges: L1 predicts safe where L2 predicts unsafe

Across 23 distinct depth-velocity conditions (water depth 0.10 to 0.60 m, flow velocity 0 to 2.0 m/s), the three abstraction levels agree only in the extremes and diverge through the middle of the operating envelope.

L0, the 0.15 m static depth threshold (NWS passenger-car depth), collapses to a near-constant verdict: it returns NO-FORD at every condition with depth at or above 0.15 m, and disagrees with the pilot in only 1 of 23 conditions (the shallow 0.10 m, 1.5 m/s case, where L0 alone returns FORD). Carrying no velocity term, L0 cannot separate still water from fast flow at equal depth.

L1, the AR&R depth-velocity product evaluated at the most permissive class threshold (D times V less than 0.60 m2/s, Large 4WD), agrees with the pilot in 9 of 23 conditions (39.1 percent) and diverges in 14 of 23 (60.9 percent). Every one of the 14 divergences runs in the same, safety-critical direction: L1 returns FORD (predicted safe) while the pilot returns NO-FORD (vehicle slides). The divergence conditions are:

| Depth (m) | Velocity (m/s) | D times V (m2/s) |
|---|---|---|
| 0.10 | 1.5 | 0.15 |
| 0.15 | 1.5 | 0.225 |
| 0.15 | 2.0 | 0.30 |
| 0.20 | 1.0 | 0.20 |
| 0.20 | 1.5 | 0.30 |
| 0.20 | 2.0 | 0.40 |
| 0.25 | 1.0 | 0.25 |
| 0.25 | 1.5 | 0.375 |
| 0.30 | 1.0 | 0.30 |
| 0.30 | 1.5 | 0.45 |
| 0.35 | 1.0 | 0.35 |
| 0.35 | 1.5 | 0.525 |
| 0.40 | 1.0 | 0.40 |
| 0.50 | 1.0 | 0.50 |

Each divergence point has a depth-velocity product below 0.60 m2/s, placing it inside the nominally safe hazard zone of even the least conservative AR&R passenger class, yet the pilot registers sustained downstream displacement past the 0.05 m onset-of-motion tolerance at all 14. The count depends on the threshold used: applying a stricter class limit (0.45 m2/s for the large passenger car, 0.30 for the small car) reclassifies some of these conditions as L1 NO-FORD and lowers the divergence count, but it does not change the direction of the disagreement or its cause. As set out in Section 3.2, at this boundary the scalar D times V criterion structurally lacks any term for directional, persistent lateral drag, independent of the threshold value or the vehicle class. The 0.30 m, 1.5 m/s condition (D times V = 0.45) is the canonical case: below every passenger-class threshold, and still an L2 NO-FORD.

### 4.2 The divergence is friction-invariant

To test whether this divergence is an artifact of the tire-ground friction value (coup_friction, a numerical coupling parameter whose primary-source provenance is still open, see Section 4.5), the pilot was re-run at a single mid-envelope divergence point (depth 0.30 m, velocity 1.5 m/s, D times V = 0.45) across four friction coefficients spanning the physically plausible range.

| coup_friction (mu) | Peak downstream drift (m) | Verdict |
|---|---|---|
| 0.0 | 0.328 | NO-FORD |
| 0.3 | 0.399 | NO-FORD |
| 0.5 | 0.396 | NO-FORD |
| 0.7 | 0.395 | NO-FORD |

The verdict is invariant across the full range: NO-FORD at every value. Among the three gripping cases (mu 0.3 to 0.7) the peak drift varies by about 1 percent (0.399 to 0.395 m). The frictionless case drifts less, 0.328 m, but still returns NO-FORD. Every value exceeds the 0.05 m tolerance by at least a factor of six. Raising tire-ground friction from zero to 0.7 therefore neither prevents nor materially reduces the instability: within this regime it is driven by hydrodynamic drag that friction does not counter. This is consistent with the divergence being structural rather than a calibration accident, though it rests on a single condition and a single box-proxy geometry, and coup_friction is a numerical coupling-impulse coefficient rather than a physical Coulomb coefficient.

### 4.3 Multi-vehicle drift magnitudes (Track 1 MPM sweep)

The Track 1 sweep extends the pilot logic to three box-proxy vehicle classes under the mpm-engine MPM solver (n_grid = 64), reporting final downstream displacement rather than a binary verdict. Of 36 cells, 24 pass the sweep's own density-plausibility gate (100 to 300 kg/m3); all 12 midsize-SUV cells are excluded, their derived density (308.13 kg/m3) sitting 2.7 percent above the band. Of the 24 retained, 3 light-pickup cells at 0.15 m depth resolve the water slab with a single particle layer and are excluded as under-resolved, leaving 21 fully trustworthy cells (sedan 12, pickup 9). The six depth-0.15 m cells that remain sit at exactly two layers and are read as marginal.

On these cells the result is one-sided. Every cell exceeds the 0.05 m onset tolerance, so there is no FORD side. Final displacement grows monotonically with the depth-velocity product, from 0.055 m (sedan, 0.15 m, 1.0 m/s) to 1.78 m (sedan, 0.60 m, 2.0 m/s) and 1.83 m (pickup, 0.60 m, 2.0 m/s). The two sub-tolerance displacements in the 24-cell set (light pickup at 0.15 m, 0.020 and 0.044 m) are precisely the under-resolved single-layer cells, not evidence of a fordable condition.

A Gaussian-process regressor fit to the valid cells predicts final displacement with leave-one-condition-out RMSE 0.048 m and R2 0.991, and is well calibrated (standardized residual standard deviation 0.95, 97 percent coverage at the nominal 95 percent interval), with depth the dominant input by fitted length scale. A FORD/NO-FORD classifier was deliberately not fit: the valid data is single-class (zero FORD cells), so there is no positive class to learn. The regressor is the honest deliverable from this sweep.

### 4.4 Failure-mode decomposition (pending regeneration)

The failure-mode classifier (simulation/failure_modes.py) decomposes each run into a stable baseline (STUCK) and three ascending-severity hydrodynamic instability modes: SLIDE (drag overcomes tire-ground friction), TOPPLE (overturning moment exceeds the vehicle static stability factor), and FLOAT (buoyancy plus lift exceeds weight). It follows the three-mode taxonomy of Shand et al. (2011), with the slide mechanism attributed to Xia et al. (2010), topple to Xia et al. (2013), and float to Kramer et al. (2016), and reports, for the highest-severity mode reached, both percent-over-threshold and absolute exceedance in native units.

This decomposition is not yet available for the sweeps above. The v1 and v2 timeseries were written before the solver emitted per-frame velocity columns (vx, vy, vz), which the classifier requires to compute net force and to separate SLIDE from FLOAT; running it against the current v2 timeseries raises a missing-kinematics error by design. The mode breakdown will be reported once the sweep is regenerated with velocity columns present. The two Xia et al. source DOIs (10.1007/s11069-010-9639-x for slide, 10.1007/s11069-013-0889-2 for topple) and the Kramer et al. (2016) float source (10.1016/j.ijdrr.2016.04.003) were all confirmed on 2026-07-20.

### 4.5 What these results are, and are not

- The divergence (4.1) and friction-invariance (4.2) findings come from the Genesis SPH pilot with synthetic box-proxy geometry, not from a coupled MPM simulation of a reconstructed scene with a real vehicle mesh. They demonstrate that a scalar depth-velocity criterion structurally omits a failure mechanism the coupled model resolves. They do not yet quantify that mechanism for any specific real crossing.
- The Track 1 sweep (4.3) uses the MPM solver but with box proxies at n_grid = 64 and no grid-convergence study. The excluded pickup cells are direct evidence that this resolution is not adequate everywhere in the design.
- Vehicle mass and bounding box are perfectly aliased with class (three unique tuples), so nothing here supports extrapolation to an unsampled vehicle class.
- The 0.05 m verdict boundary is a numerical onset-of-motion tolerance internal to the solver, not a physically calibrated threshold from a peer-reviewed source.
- The AR&R L1 thresholds are labeled "draft, interim" by their own source and are treated as such here.
- Earlier project documents recorded an L2 finding of 16 divergence points at 30.4 percent L1/L2 agreement. The live recomputation reported here (14 divergence points, 39.1 percent agreement over 23 deduplicated conditions) supersedes that figure, which had already been marked provisional pending this rebuild.

---

## 5. Discussion

### 5.1 Forward-Inverse Duality

Our pipeline instantiates two complementary halves of a closed perception-to-action loop for autonomous flood traversability. Hsiao and Kumar (2025) demonstrated that the inverse problem (estimating granular material properties from visual observations via NeRF and Bayesian optimization) is tractable and achieves sub-2-degree accuracy in friction angle recovery. Our work addresses the complementary forward problem: given known scene geometry and flood hydraulic properties, what is the traversability verdict under the full dynamics of weakly-compressible water interacting with a rigid vehicle body? Together, these two directions satisfy the auditability requirement of physically viable world models (Thorpe et al. 2026).

---

## Data Availability

Simulation dataset published on DesignSafe-CI (DOI: pending, target July 21-24 2026).
Code: https://github.com/jcerrell-IS/can-it-ford

---

## References

Entries below map to `paper/can_it_ford_references_IEEE.bib` (bib key in brackets). Items flagged VERIFY in that file are not yet confirmed against the primary source.

- **Genesis Authors (2024).** Genesis: A Universal and Generative Physics Engine for Robotics and Beyond. https://github.com/Genesis-Embodied-AI/Genesis `[genesis2024]`
- **Hsiao, C.-H., & Kumar, K. (2025).** NeRF-to-MPM Inversion for Granular Material Property Estimation. arXiv:2507.09005 `[hsiaokumar2025]`
- **Kerbl, B., Kopanas, G., Leimkühler, T., & Drettakis, G. (2023).** 3D Gaussian Splatting for Real-Time Radiance Field Rendering. arXiv:2308.04079 `[kerbl20233dgs]`
- **Kramer, M., Terheiden, K., & Wieprecht, S. (2016).** Safety criteria for the trafficability of inundated roads in urban floodings. *International Journal of Disaster Risk Reduction*, 17, 77-84. Float-mode source. https://doi.org/10.1016/j.ijdrr.2016.04.003 `[kramer2016]`
- **National Weather Service (2026).** Turn Around Don't Drown. https://www.weather.gov/safety/flood-turn-around-dont-drown `[nws_tadd]`
- **SAE International (1999).** Vehicle Inertial Parameters, Mass Properties, and Static Stability Factor. SAE 1999-01-1336. `[sae1999011336]`
- **Shand, T. D., Cox, R. J., Blacka, M. J., & Smith, G. P. (2011).** Appropriate Safety Criteria for Vehicles: Project 10, Stage 2 Literature Review (P10/S2/020). Water Research Laboratory, Australian Rainfall and Runoff Revision Project. `[shand2011]`
- **Smith, G. P., Modra, B. D., & Felder, S. (2019).** Full-scale testing of stability curves for vehicles in flood waters. Journal of Flood Risk Management, 12. https://doi.org/10.1111/jfr3.12527 `[smithmodrafelder2019]`
- **Thorpe, A., Iqbal, H., Hsiao, C.-H., et al. (2026).** Physically Viable World Models: A Case for Query-Conditioned Embodied AI. arXiv:2605.30542 `[thorpe2026pvwm]`
- **Xia, J., Teo, F. Y., Lin, B., & Falconer, R. A. (2010).** Formula of incipient velocity for flooded vehicles. Natural Hazards, 58(1), 1-14. https://doi.org/10.1007/s11069-010-9639-x `[xia2010]`
- **Xia, J., Falconer, R. A., Xiao, X., & Wang, Y. (2013).** Criterion of vehicle stability in floodwaters based on theoretical and experimental studies. Natural Hazards, 70(2), 1619-1630. https://doi.org/10.1007/s11069-013-0889-2 `[xia2013]`
- **Xie, T., Zong, Z., Qiu, Y., Li, X., Feng, Y., Yang, Y., & Jiang, C. (2023).** PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics. arXiv:2311.12198 `[xie2023physgaussian]`
