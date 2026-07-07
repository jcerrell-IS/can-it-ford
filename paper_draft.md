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

### 3.2 PVWM Framing

The three-level abstraction ladder instantiates the orchestrator described in Section 3 of Thorpe et al. (2026) as the first running implementation. The PVWM paper identifies automatic abstraction selection as the central open problem and provides no committed orchestrator code. Our orchestrate_ford_query() function represents the first concrete implementation, with the empirical divergence zone at d greater than or equal to 0.25m, v greater than or equal to 1.2 m/s, and D times V less than 0.60 m2/s defining the L1-to-L2 escalation boundary. At this boundary, the scalar criterion structurally lacks the mechanism to represent directional persistent lateral drag, independent of threshold value or vehicle class. 

---

## 5. Discussion

### 5.1 Forward-Inverse Duality

Our pipeline instantiates two complementary halves of a closed perception-to-action loop for autonomous flood traversability. Hsiao and Kumar (2025) demonstrated that the inverse problem (estimating granular material properties from visual observations via NeRF and Bayesian optimization) is tractable and achieves sub-2-degree accuracy in friction angle recovery. Our work addresses the complementary forward problem: given known scene geometry and flood hydraulic properties, what is the traversability verdict under the full dynamics of weakly-compressible water interacting with a rigid vehicle body? Together, these two directions satisfy the auditability requirement of physically viable world models (Thorpe et al. 2026).

---

## Data Availability

Simulation dataset published on DesignSafe-CI (DOI: [INSERT AFTER JULY 10]).
Code: https://github.com/jcerrell-IS/can-it-ford

---

## References

[TODO]
