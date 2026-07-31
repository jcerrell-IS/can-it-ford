---
name: l1-l2-divergence-is-class-dependent
description: "The paper's class-free L1/L2 divergence zone is wrong for 2 of 3 AR&R classes at 0.30m/1.5m/s, and computing D x V at the vehicle instead of upstream removes the third"
metadata:
  type: project
---

Measured 2026-07-25, Vista job 866266, three runs at nominal depth 0.30 m and surge 1.5 m/s,
n_grid 64, same Yaris hull, only `--vehicle-mass` varied.

The paper asserts a divergence zone at depth >= 0.25 m, velocity >= 1.2 m/s, D x V < 0.60,
where L1 says FORD and L2 says NO-FORD. The tested point is inside it on all three
conditions. Result:

| class | mass | L1 nominal | L2 (|d| vs 0.05 m) | outcome |
|---|---|---|---|---|
| small_passenger | 1100 kg | NO-FORD | NO-FORD (0.09240) | AGREE, contradicts the zone |
| large_passenger | 1609 kg | FORD | NO-FORD (0.05110) | DIVERGE, as claimed |
| large_4wd | 2337 kg | FORD | FORD (0.03890) | AGREE, contradicts the zone |

**Why the zone cannot be class-free:** AR&R's hazard limits are 0.30 / 0.45 / 0.60 m2/s for
small_passenger / large_passenger / large_4wd (`vehicle_params.py:166`, verified live). At a
fixed D x V of 0.45 the L1 verdict alone is NO-FORD, FORD, FORD. A zone defined by a D x V
band therefore names a different verdict per class and cannot be stated without one.

**Second, larger finding.** AR&R's D is the depth AT THE VEHICLE, not the upstream slab.
Measured 3 dx to 0.5 dx upstream of the vehicle's minimum-x face:

| class | nominal D x V | local D peak | local V at peak | honest D x V | change |
|---|---|---|---|---|---|
| small_passenger | 0.4500 | 0.3974 m | 0.4760 m/s | 0.1892 | -58.0 % |
| large_passenger | 0.4500 | 0.4159 m | 0.3956 m/s | 0.1645 | -63.4 % |
| large_4wd | 0.4500 | 0.4260 m | 0.3592 m/s | 0.1530 | -66.0 % |

Local depth is HIGHER than nominal (bow wave) while local speed is far LOWER (the body
stagnates the flow). Re-running L1 on local values flips large_passenger FORD -> NO-FORD, on
the DEPTH limit (0.4159 > 0.40), not on D x V. **Then L1 and L2 agree on all three classes.**

**How to apply:** never quote the divergence zone without a class label, and never feed L1
the nominal upstream slab values while calling the result an L1-vs-L2 comparison. State which
D you used. The large_passenger verdict is entirely decided by that choice, and the local peak
is a transient stagnation maximum at frame 29 of 90 that decays to 0.107-0.124 m by the end,
so "peak local depth" is itself a defensible-but-arguable choice, not an obvious one.

Standing caveat that must ride in the same sentence as any L2 verdict: DRIFT_THRESHOLD 0.05 m
has NO peer-reviewed source. large_passenger sits 2.2 percent above it and is inside its own
uncertainty. Related: [[solidify-watertight-supersedes-column-fill]].
