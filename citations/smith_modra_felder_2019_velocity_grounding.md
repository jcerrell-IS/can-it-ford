# Smith, Modra and Felder 2019, Velocity Grounding for Can It Ford Sweep

Source: Smith GP, Modra BD, Felder S. Full-scale testing of stability curves for vehicles in flood waters. J Flood Risk Management. 2019;12(Suppl. 2):e12527. DOI 10.1111/jfr3.12527
Reviewed directly from the PDF, July 2026, page by page, not summarized secondhand.

## Critical finding: this paper does not report a simple tested velocity range

The full-scale prototype tests (three vehicles: Toyota Yaris sedan 2006, Nissan Patrol GRII 4WD 1998, Ford Festiva 1992) were conducted in STAGNANT water, depth 0 to 1.0 m, towed sideways by winch to measure traction force directly. Quote from Section 2.1, page 3: the dynamic contribution of the uplift force was neglected since the prototype scale vehicle tests could only be conducted in stagnant water.

No full-scale flowing-water velocity was directly measured on the real vehicles. Velocity in this paper's stability curves (Figures 10 and 11) is a CALCULATED quantity, derived via Equation 4, a force-balance equation combining the directly measured static traction force, a drag coefficient C_D = 1.38 measured separately on a 1:18 scale model Toyota Yaris in a real flume, and friction coefficients mu = 0.3 (worst case, sand or gravel bed) or mu = 0.78 (wet or dry concrete).

## What was directly, physically measured with real flowing water

Only the small-scale model (Toyota Yaris, length ratio Lr = 18) drag-force experiments, Section 2.3, Table 2:
- Subcritical flows: Q 5 to 17.5 L/s, model depth d 0.02 to 0.05 m, Froude number 0.3 to 0.76
- Near-critical flows: Q 9 to 11.6 L/s, model depth d 0.02 to 0.03 m, Froude number 0.94 to 1.05
- Supercritical flows: Q 5.3 to 44 L/s, model depth d 0.01 to 0.03 m, Froude number 1.83 to 4.16

These are MODEL SCALE values (Lr = 18), not full-scale. Converting to a full-scale-equivalent velocity in m/s requires Froude scaling of both length and velocity, which has not been performed here and should not be treated as done until it is, checked and shown explicitly if used.

## The actually citable, exact, invertible relationship

Equation 6, page 12, the paper's own fitted limiting stability curve across all three tested vehicles:

d - d_pan = 0.414 - 0.244 x Fr   (valid for d - d_pan > 0)

where d_pan is vehicle floor pan height above ground (Table 1: Yaris 0.155 m, Patrol 0.50 m, Festiva 0.215 m) and Fr is the Froude number V / sqrt(g x d).

Recommended use for the sweep: for a chosen depth d in the sweep, solve Equation 6 for the limiting Froude number, then compute the corresponding limiting velocity V = Fr x sqrt(g x d). This produces a defensible, paper-derived velocity bound at each depth without relying on a visual read of Figure 11's scatter plot.

## Vehicle masses, cross-reference against SAE 1999-01-1336 classes (Table 1)

- Toyota Yaris Sedan 2006: mass 1,045 kg, L 4.30 m, W 1.69 m, floor pan 0.155 m
- Nissan Patrol GRII 4WD 1998: mass 2,478 kg, L 4.97 m, W 1.84 m, floor pan 0.50 m
- Ford Festiva 1992: mass 790 kg, L 3.62 m, W 1.61 m, floor pan 0.215 m

Note these are a different vehicle set than the SAE 1999-01-1336 sedan/SUV/pickup classes used elsewhere in this project. Useful as an independent cross-check, not a substitute source.

## Do not cite as

"Smith, Modra and Felder tested velocities up to X m/s" without specifying whether X came from the calculated stability-curve velocity (Eq. 4 output) or the model-scale flume Froude numbers (Table 2, unconverted). These are two different quantities from two different experimental setups within the same paper.
