# Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability

**Author:** Josie Cerrell (Claremont McKenna College)
**PI:** Krishna Kumar (University of Texas at Austin, GeoElements)
**Program:** NSF SCIPE REU 2026, Texas Advanced Computing Center
**License:** Open Data Commons Attribution License (ODC-By 1.0)

## Status: provisional, staged ahead of DesignSafe submission, not yet published

This package is not yet the final dataset. The L2 results below were produced on synthetic box geometry using Genesis's SPH solver, not the MPM pipeline this project targets. No real reconstructed scene and no PhysGaussian bridge have been built yet. Full correction log: see the project repository's PROVISIONAL_STATUS.md.

## Summary

This dataset supports a reconstruct-to-decide pipeline intended to determine whether a specific vehicle can ford a specific flooded road. The target pipeline reconstructs a real scene from video into a 3D Gaussian splat, bridges it to Material Point Method particles, and simulates it in Genesis as weakly-compressible water coupled to a rigid vehicle. The current pilot data below uses simplified synthetic geometry and Genesis's SPH solver as a proof of concept for that pipeline, not the pipeline itself.

## Abstraction levels

- L0: static depth threshold (NWS Turn Around Don't Drown, float above 0.15 m).
- L1: depth times velocity scalar hazard criterion (Australian Rainfall and
  Runoff, Shand et al. 2011). 4WD threshold 0.60 m^2/s is the project default.
- L2: coupled Genesis simulation (currently SPH pilot, MPM migration in progress). No-ford when peak lateral drift exceeds 0.05 m.

## Key result (from the synthetic pilot, not yet the real-scene result)

Across 23 unique depth-velocity conditions tested on the SPH pilot scene, L1 and L2 agree on only 7 (30.4 percent agreement). L2 returns no-ford in 16 conditions where L1 predicts ford. This result predates the July 7 correction of five parameter bugs (vehicle mass, timestep, position, viscosity, friction) and should be treated as motivating evidence for the rebuild, not a validated finding.

## Files

- can_it_ford_L2.py: Genesis SPH pilot water-vehicle simulation, current bug-fixed version.
- can_it_ford_mu_sweep.py: friction sweep, result under re-evaluation pending mass fix.
- make_phase_space.py: phase space figure generator.
- phase_space_results.csv: L2 pilot verdicts, 23 unique conditions, pre-fix.
- scenario_sweep.csv: 70-row L0/L1 theoretical grid.
- figures/: phase space and validation figures.

## Validation sources

- Australian Rainfall and Runoff, Shand et al. 2011, Project 10.
- Smith, Modra, Felder 2019, Journal of Flood Risk Management, DOI 10.1111/jfr3.12527.
- NWS Turn Around Don't Drown, weather.gov.

## Reproduction

L2 simulations run on TACC Vista GH200 nodes inside the Genesis Apptainer
container. Each run takes depth and velocity as positional arguments and appends
one row to phase_space_results_v2.csv. Figures regenerate locally from the CSV with
make_phase_space.py.
