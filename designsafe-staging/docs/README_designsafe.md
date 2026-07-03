# Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability

**Author:** Josie Cerrell (Claremont McKenna College)
**PI:** Krishna Kumar (University of Texas at Austin, GeoElements)
**Program:** NSF SCIPE REU 2026, Texas Advanced Computing Center
**License:** Open Data Commons Attribution License (ODC-By 1.0)

## Summary

This dataset supports a reconstruct-to-decide pipeline that determines whether a
specific vehicle can ford a specific flooded road. A real scene is reconstructed
from video into a 3D Gaussian splat, bridged to Material Point Method particles,
and simulated in Genesis as weakly-compressible water coupled to a rigid vehicle.
The pipeline compares three abstraction levels and reports a binary ford or
no-ford verdict.

## Abstraction levels

- L0: static depth threshold (NWS Turn Around Don't Drown, float above 0.15 m).
- L1: depth times velocity scalar hazard criterion (Australian Rainfall and
  Runoff, Shand et al. 2011). 4WD threshold 0.60 m^2/s is the project default.
- L2: full coupled Genesis MPM simulation. No-ford when peak lateral drift
  exceeds 0.05 m or vertical lift exceeds 0.02 m.

## Key result

Across 23 unique depth-velocity conditions, L1 and L2 agree on only 7 (30.4
percent agreement). L2 returns no-ford in 16 conditions where L1 predicts ford.
Agreement occurs only in still water (v = 0) and at supercritical hazard values
above the published 4WD threshold. The failure is structural: the scalar depth
times velocity criterion cannot represent directional lateral drag at any
threshold value.

## Files

- can_it_ford_L2.py: Genesis MPM coupled water-vehicle simulation.
- can_it_ford_mu_sweep.py: friction sweep confirming drift is flow-driven.
- make_phase_space.py: phase space figure generator.
- phase_space_results.csv: L2 verdicts, 23 unique conditions.
- scenario_sweep.csv: 70-row L0/L1 theoretical grid.
- figures/: phase space and validation figures.

## Validation sources

- Australian Rainfall and Runoff, Shand et al. 2011, Project 10.
- Smith, Modra, Felder 2019, Journal of Flood Risk Management, DOI 10.1111/jfr3.12527.
- NWS Turn Around Don't Drown, weather.gov.

## Reproduction

L2 simulations run on TACC Vista GH200 nodes inside the Genesis Apptainer
container. Each run takes depth and velocity as positional arguments and appends
one row to phase_space_results.csv. Figures regenerate locally from the CSV with
make_phase_space.py.
