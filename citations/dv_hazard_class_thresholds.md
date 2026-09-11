# Depth-Velocity (D x V) Hazard Class Thresholds, quick reference

Real, citable, per-vehicle-class D x V product limits (units m^2/s). These are a
DIFFERENT quantity from `DRIFT_THRESHOLD = 0.05` (which is metres of lateral
displacement, a solver-internal onset tolerance, not citable, see
`drift_threshold_grounding.md`). These D x V limits ground the L1-style hazard
verdict, not the L2 displacement detector.

Extracted from full sources July 16, 2026. Both source families label their numbers
as informal or as hazard-classification bands, quote that caveat whenever used.

## ARR Project 10 Stage 2 (Shand, Cox, Blacka, Smith 2011), Table 3

Printed p.14 / PDF p.24. "Proposed DRAFT Stability Criteria for Stationary Vehicles."
The report calls these "Draft, interim, informal" and states they are "unlikely
reliable enough to be adopted permanently as safety criteria."

| Class | Length | Kerb weight | Ground clearance | D x V limit (m^2/s) |
|---|---|---|---|---|
| Small passenger | < 4.3 m | < 1250 kg | < 0.12 m | 0.30 |
| Large passenger | > 4.3 m | > 1250 kg | > 0.12 m | 0.45 |
| Large 4WD | > 4.5 m | > 2000 kg | > 0.22 m | 0.60 |

The 0.60 figure is the Large 4WD row specifically, NOT a generic all-vehicle cutoff.
Do not confuse it with the OLD ARR87 "0.6 to 0.7 depending on vehicle size" generic
value (printed p.3 / PDF p.13, Table 1), which this same report criticises as
non-conservative.

## WRL Technical Report 2014/07, Table 5-2 (p.38)

Combined flood hazard classification. Generic (not per-vehicle-model) hazard bands.

| Class | D x V limit (m^2/s) | Limiting depth D | Limiting velocity V | Vehicle meaning |
|---|---|---|---|---|
| H1 | <= 0.30 | 0.3 m | 2.0 m/s | Generally safe for all vehicles |
| H2 | <= 0.60 | 0.5 m | 2.0 m/s | Unsafe for small vehicles |
| H3 | <= 0.60 | 1.2 m | 2.0 m/s | Unsafe for all vehicles |
| H4 | <= 1.00 | 2.0 m | 2.0 m/s | Unsafe for all vehicles and people |
| H5 | <= 4.00 | 4.0 m | 4.0 m/s | Unsafe, buildings vulnerable |
| H6 | > 4.00 | none | none | Unsafe, all buildings vulnerable |

WRL's 0.60 (H2, boundary where SMALL vehicles become unsafe) and ARR's 0.60 (Large
4WD upper limit) are numerically equal by coincidence, not the same criterion. Always
state source and class when quoting 0.60.
