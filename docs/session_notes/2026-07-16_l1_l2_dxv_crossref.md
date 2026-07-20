# L1 (D x V hazard) vs L2 (displacement) cross-reference, v3 sweep

July 16, 2026. Source: `data/track1_sweep_v3/manifest.csv` (60 cells, 3 vehicle
classes x 20 depth-velocity points, all `plateaued_ok=True`). Script:
scratchpad `xref_l1_l2.py`.

## Method

- L2 verdict per cell: NO-FORD if `final_disp_m > 0.05` (DRIFT_THRESHOLD), else FORD.
  Note 0.05 is the solver onset-of-motion tolerance, not a calibrated safety line
  (see `citations/drift_threshold_grounding.md`), so "L2 NO-FORD" means "detectable
  incipient motion," not "washed away."
- L1 verdict per cell: NO-FORD if `depth_velocity_m2ps` exceeds the ARR Stage 2
  Table 3 per-class limit, else FORD. Class assigned by ARR's own length/mass
  criteria (`citations/dv_hazard_class_thresholds.md`):
  - sedan 4.66 m / 1390 kg -> Large passenger -> 0.45
  - suv 4.96 m / 1990 kg -> Large passenger (10 kg under the 2000 kg 4WD line,
    borderline) -> 0.45
  - pickup 5.89 m / 2300 kg -> Large 4WD -> 0.60

## Result

42/60 agree, 18/60 diverge. **Every one of the 18 divergences is the same
direction: L1 = FORD (safe), L2 = NO-FORD (motion detected). Zero cells go the
other way.** L2 is strictly more conservative than per-class D x V here; the
displacement detector never clears a cell that L1 flags.

Per class: sedan 16/20 agree, suv 15/20, pickup 11/20 (pickup diverges most because
its 0.60 threshold is the most permissive, so it clears more cells that still move).

## The physically interesting cluster: deep, SLOW water

Many divergences are at v=0.5 m/s with depth 0.45-0.60 m, where D x V is small
(0.225-0.30) so L1 rates safe, yet displacement is large:

- sedan d=0.6 v=0.5, D x V=0.30, disp=0.29 m -> L1 FORD, L2 NO-FORD
- pickup d=0.6 v=0.5, D x V=0.30, disp=0.15 m -> L1 FORD, L2 NO-FORD
- suv d=0.6 v=0.5, D x V=0.30, disp=0.11 m -> L1 FORD, L2 NO-FORD

Mechanism: deep slow water reduces the normal force through near-buoyancy, so even
weak drag moves the vehicle. A pure D x V product cannot see this, it treats depth
and velocity symmetrically and reports a low hazard when velocity is low, regardless
of how much the vehicle has floated. This is the same "L2 sees a mode L1 structurally
cannot" story as the fast-shallow core finding, but from the opposite corner of the
D x V plane, and it is a stronger example because L1 is not merely miscalibrated, it
is missing the buoyancy axis entirely.

## Caveats

- Depends on DRIFT_THRESHOLD = 0.05. The marginal cells (e.g. pickup d=0.15 v=2.0,
  disp=0.0544) would flip if the tolerance were raised. The deep-slow cells (disp
  0.11-0.29 m) are robust to any reasonable tolerance and carry the finding.
- suv class assignment is borderline (1990 vs 2000 kg). Reclassifying it as Large
  4WD (0.60) would move a few suv cells from diverge to agree but not change the
  one-directional pattern.
- WRL generic all-vehicle boundary (H1, D x V <= 0.30) agrees with L2 on 50/60, also
  all divergences one-directional (L2 more conservative).
