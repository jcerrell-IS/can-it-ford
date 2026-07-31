# Limitations

Opened 2026-07-25. Append-only. One entry per known limitation, each with the artifact that
establishes it. An entry here is a thing we know and have chosen not to fix yet, not a
thing we have not noticed.

---

## L-1. The L0 boundary test is inconsistent across three call sites

| file | test | verdict at exactly d = 0.15 m |
|---|---|---|
| `simulation/can_it_ford_L0.py:6` | `depth_m < 0.15` gives FORD | NO-FORD |
| `scripts/gen_scenario_sweep.py:24` | `d <= 0.15` gives FORD | FORD |
| `analysis/make_phase_space.py:10` | `d > 0.15` gives NO-FORD | FORD |

0.15 m is a live grid depth in `data/scenario_sweep.csv`, so the disagreement is realized,
not hypothetical. Two of three call sites return FORD at the boundary and one returns
NO-FORD.

Does not touch the 0.29443 m operating point and changes nothing in
`docs/four_rung_ladder.md`. **Deliberately not fixed on 2026-07-25**: a code change to a
verdict function at that hour carries risk with no payoff before the deadline. Reconcile
before the sweep figure is captioned.

---

## L-2. Two L1 implementations exist and only one is authoritative

- `vehicle_params.py:186` `L1_verdict`: full AR&R rule, depth cap **and** velocity cap
  **and** D x V product, per class. **This is the authoritative one. Use it for every
  number that reaches a figure, a caption or a message.**
- `simulation/can_it_ford_L1.py:3`: per-class D x V product only, no depth cap, no
  velocity cap. **Must not be used for reported numbers.**

They agree at the current operating point only because 0.29443 m clears every class depth
cap. They diverge generally, for example at d = 0.35 m, v = 0.8 m/s: the product is 0.28,
which clears the small-passenger 0.30 limit, but 0.35 exceeds the 0.30 depth cap, so the
full rule returns NO-FORD and the product-only rule returns FORD.

Captions must name which rule produced the verdict.

---

## L-3. The three masses are not three vehicle classes

All six rollouts share `extent = [1.746378, 4.282610, 1.518008] m`. Only `--vehicle-mass`
varies. Measured against the three AR&R axes, the single Yaris hull is 4.2826 m long with
measured ground clearance 0.158 to 0.174 m
(`.claude/handoffs/2026-07-25_vista.md:158-162`, five independent sampling bands; the
coarse `v1l` FE deck probably lacks low-hanging exhaust and suspension, so the measurement
likely overestimates true clearance).

It therefore **fails** `small_passenger` on clearance (needs <= 0.12 m), **fails**
`large_4wd` on both length (needs >= 4.5 m) and clearance (needs >= 0.22 m), and satisfies
only `large_passenger`.

Per `docs/mass_sensitivity_table.md`, this is reported as a mass sensitivity study and not
as a class comparison, and the word "class" may not appear unqualified for these rows until
V2 real meshes exist. The class column in the gate outputs names which AR&R *limit set* was
applied, nothing more. Write "4WD-scale mass", never "a 4WD".

---

## L-4. Realized vehicle density is above the project's plausibility band in every run

310, 453 and 658 kg/m3 for 1100, 1609 and 2337 kg, against the 100 to 300 kg/m3 anchor at
`CLAUDE.md:14-15`. All three exceed it; the heaviest by a factor of 2.2. Every run here is
denser than a plausible car. Whether that band originates in the engine's `FloodScene`
docstring is UNRESOLVED, since no local clone of `kks32/mpm-engine` exists on this Mac.

---

## L-5. The dry-start and standing-water runs are not a controlled pair

`sim_dump.py` (dry start) and `sim_standing.py` (standing water) differ in at least six
respects beyond the initial condition, so the 7.1x / 6.2x / 3.2x displacement difference
between them **cannot be attributed to the initial condition**. Full detail in
`.claude/handoffs/2026-07-25_CORRECTIONS.md` C15. The dominant confound is that
`sim_standing.py:190-196` re-imposes the inflow velocity every step, making it a
continuously forced system, while `sim_dump.py` applies velocity once at t = 0.

`water_eta`, `floor_friction` and `bulk_modulus` are recorded for the standing-water runs
and **absent** from the dry-start summaries, so they cannot be compared without a re-run.

Converting this into a real paired comparison needs one re-run of `sim_standing.py` with
`_sustain_inflow` disabled. Vista work, not a tonight job.

---

## L-6. Two displacement measures disagree under standing water

`summary.json` `final_disp_mag_m` (equivalently `metrics.csv` `dmag` at t = 3.0 s, 91 rows)
and the npz `t` array (90 frames) agree to about 1e-4 under dry start but differ by 2 to
9 percent under standing water. Detail and the table in
`.claude/handoffs/2026-07-25_CORRECTIONS.md` C14. **Chosen measure: `summary.json`
`final_disp_mag_m`.** The npz `t` array is used only for onset-frame detection. The cause
of the standing-water divergence is not yet diagnosed.

---

## L-7. Closed reflecting domain

No outlet, drain, absorption zone or periodic boundary exists.
`sim_standing.py:132-136` adds a floor plane and four slip side walls with
`restitution = 0.05`. Results are a fixed-volume transient, a dam-break or surge, not
steady open-channel flow. Acoustic round trip 0.4951 s over a 3.0 s run is about six
reflections. This is a solver-class limitation, not a bug: neither MPM nor SPH liquid in
this solver class provides an outlet.

---

## L-8. The Kramer total-head formula is not read at source

The h_E values 0.30 m (passenger car) and 0.60 m (emergency vehicle) are SOURCE-verified
from the abstract of DOI 10.1016/j.ijdrr.2016.04.003. The defining equation is not in the
abstract. `h_E = h + v^2/2g` is standard hydraulic total head and is HYPOTHESIS-grade here.
This matters more than the 36 percent margin suggests: the still-water term alone
(0.29443 m) is *below* the 0.30 m limit, so the entire L1b verdict is produced by the
velocity-head term.

---

## L-9. The Lazzarin quotation is unverified and is excluded from all captions

DOI 10.1016/j.jhydrol.2022.127485 and its title are verified. The sentence attributed to it
about the depth-velocity product was not retrieved (ScienceDirect HTTP 403). The same point
is made instead from AR&R's own separate limiting depth, read directly at
`vehicle_params.py:165-181`, which is a primary read rather than a quote from a paywalled
paper.

---

## L-10. Single resolution, no grid convergence

All six rollouts are `n_grid = 64`. No grid-convergence study and therefore no Roache GCI
exists. Queued as Vista work.
