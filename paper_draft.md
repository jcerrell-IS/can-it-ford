# Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability

**Author:** Josie Cerrell
**Institution:** Claremont McKenna College / GeoElements Lab, TACC/UT Austin
**Date:** July 2026

---

## Abstract

Background. Flooded roads are a leading cause of vehicle fatalities: over half of all flood-related drownings occur when a vehicle is driven into hazardous floodwater. Drivers and autonomous vehicles alike cannot judge water depth, flow velocity, or submerged road condition from appearance alone. Appearance-predictive world models share this blind spot, producing outcomes that look plausible but violate the underlying physics. Physically viable world models, which preserve the latent physics governing action outcomes, offer a principled alternative.
Objective. This project asks a deliberately narrow query: can a specific autonomous vehicle ford a specific flooded road? Rather than building the highest-fidelity simulation possible, it identifies the simplest physical abstraction sufficient to answer that query correctly, directly instantiating the query-conditioned world-model framework of Thorpe et al. (2026).
Methods. A flooded-road scene is reconstructed in 3D using Gaussian splatting. Following the PhysGaussian framework, Gaussian kernels are intended to seed a continuum particle representation that will initialize a Material Point Method (MPM) simulation in the Genesis physics engine, with rigid-MPM coupling allowing a rigid vehicle body to interact with weakly compressible floodwater. A synthetic-geometry SPH pilot currently validates the abstraction-ladder logic ahead of this migration. Three levels of physical fidelity are compared: (0) a static depth threshold derived from published flood-vehicle stability data, (1) a depth-velocity stability criterion from the Australian Rainfall and Runoff guidelines, and (2) a full coupled simulation where feasible within the project timeline. All simulations run on NVIDIA A100 GPUs at TACC.
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

[TODO]
