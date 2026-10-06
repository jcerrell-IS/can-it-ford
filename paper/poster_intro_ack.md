> **Archived text of the July 2026 poster** ([`public_release/Cerrell_TACC_42x56.pdf`](../public_release/Cerrell_TACC_42x56.pdf)),
> kept as presented. Parts are superseded: the reported coupled results now come from 17 runs on the
> real Yaris hull with the `warpmpm` solver, L1 applies the full AR&R rule, and the verdicts from those 17 runs are withdrawn.
> For current results see [`README.md`](../README.md) and [`FINDINGS.md`](../FINDINGS.md).

# Introduction

**Can It Ford? Finding the Minimum Sufficient Physical Abstraction for Autonomous Vehicle Flood Traversability**

Josie Cerrell
Integrated Sciences, Claremont McKenna College

GeoElements Research Experience for Undergraduates (REU), Texas Advanced Computing Center (TACC), The University of Texas at Austin

Mentors: Krishna Kumar, Hassan Iqbal, and Cheng-Hsi Hsiao

Given a real flooded road reconstructed from video, can a specific autonomous vehicle cross it, and what is the simplest physical model that answers correctly? This work builds a pipeline from real flood footage to a binary ford / no-ford verdict, then compares three levels of physical abstraction (a static depth threshold, a depth-velocity product, and a fully coupled material point method simulation) to identify the least complex model that still captures the physics that decides the outcome.

# Acknowledgments

This work was supported by the National Science Foundation under NSF REU Site Award #2447887. Computational resources were provided by the Texas Advanced Computing Center (TACC) at The University of Texas at Austin.

The finite element vehicle models used in this work were developed by the Center for Collision Safety and Analysis (CCSA) at George Mason University (GMU) under contract with the Federal Highway Administration (FHWA) and the National Highway Traffic Safety Administration (NHTSA).
