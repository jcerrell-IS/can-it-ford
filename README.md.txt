# Can It Ford? Genesis MPM Flood Traversability Dataset

## Authors
Josie Cerrell, Krishna Kumar
GeoElements Lab, TACC/UT Austin, NSF SCIPE REU 2026

## Description
Phase space dataset for autonomous vehicle flood traversability assessment.
Three abstraction levels: L0 (NWS depth threshold), L1 (AR&R D x V scalar,
threshold 0.60 m2/s for 4WD), L2 (Genesis MPM weakly-compressible water
with rigid vehicle coupling on Vista GH200).

## Files
- can_it_ford_L2.py: L2 Genesis MPM simulation script
- phase_space_results.csv: 9 confirmed L2 simulation results
- scenario_sweep.csv: 70-row L0/L1 theoretical grid
- can_it_ford_validation.png: validation figure

## CSV Columns (phase_space_results.csv)
- depth_m: water depth in meters
- velocity_ms: flow velocity in meters per second
- verdict: FORD or NO-FORD
- peak_x_disp: peak lateral displacement of vehicle in meters

## Run Command
apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2.py [depth] [velocity]
Example: apptainer exec --nv $GENESIS_PATH python3 can_it_ford_L2.py 0.30 1.5

## Hardware
TACC Vista, GH200 GPU, Genesis 1.2.0, Taichi 1.7.4, Python 3.x

## License
ODC-By (Open Data Commons Attribution)

## Related Work
- Thorpe et al. arXiv:2605.30542 (PVWM framework)
- Hsiao & Kumar arXiv:2507.09005 (inverse pipeline)