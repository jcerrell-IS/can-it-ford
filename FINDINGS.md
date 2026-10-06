# Findings, deliverables and public surfaces

Reader-facing outputs for **Can It Ford?**, NSF SCIPE REU 2026, GeoElements Lab, TACC / UT Austin.
Josie Cerrell, Claremont McKenna College.

## Interactive

| Surface | URL |
|---|---|
| Simulation records, TACC run data (live) | https://huggingface.co/datasets/josiecerrell/can-it-ford-steady-force |
| Scenario sweep dataset, browsable viewer (live) | https://huggingface.co/datasets/josiecerrell/can-it-ford-scenario-sweep |
| Gradio demo (live) | https://huggingface.co/spaces/josiecerrell/can-it-ford |
| Experiment tracking | `jcerrell29-claremont-mckenna-college/can-it-ford` on W&B, **private**, so named rather than linked |

## The result

The field decides fordability with a hazard product, depth times velocity, against a published
threshold. Two of its blind spots follow from the formula alone, and a third appeared in the early
coupled simulations.

**Established from the criterion itself, no simulation required:**

1. **It cannot see still water.** At zero velocity the product is zero whatever the depth, so a
   metre of motionless water scores zero hazard and passes any threshold.
2. **It cannot see mass.** The criterion has no mass term: across a 2.1x mass range the product is
   bit-identical at 0.441644 m²/s.
3. **The often-quoted product is only part of the rule.** Correcting this project's own encoding
   of the criterion reclassified **23 of 70 scenario cells, all toward NO-FORD, none loosened**: 11
   from restoring the depth cap with class held fixed, 12 from evaluating an 1100 kg car against
   its own published class.

**Suggested by the early coupled runs, withdrawn as verdicts:** the first 17 runs set the water
moving in one step inside a closed tank, so their motion is a start-up surge, not a steady current
(per a 2026-09-30 review). In those runs the simulation separated cases the product cannot (mass),
and the product depended on where depth is read: 0.45000 m²/s at the road against 0.189 to 0.153
at the hull, in its own bow wave, 58 to 66 percent lower and across the threshold. These are
illustrations of the gap, not steady-current results. The steady-current campaign that replaces
them has no verdict yet.

## Scope

**Established.** 20 coupled runs of a watertight 2010 Toyota Yaris hull (derived from CCSA's finite
element model): the 17 gated runs the paper reports, across three grid resolutions, three masses,
six velocities and four depths, plus 3 early dry-start runs. Vehicle loading is repeatable in the 17
runs that record it (two loads give the same particle count and domain size), but the simulated
trajectories are not bit-identical, and the 3 dry-start runs record nothing. Mesh containment 100.00 % of a 2000-particle subsample. D×V
bit-identical across the mass range, tested with `float.hex()`. Eight geometry and physics gates
reported: six pass, one fails, one noted.

**Open.** No reconstructed scene has entered a simulation. Gaussian splatting *did* run, to
1,147,694 Gaussians at PSNR 22.74 / SSIM 0.825 / LPIPS 0.311 on held-out views (drainA, 30,000
iterations), but the splat has no metric scale and the bridge from those kernels to solver
particles was never built, so **no verdict here starts from video**. No run drives the vehicle
under its own power: the hull starts at rest and is pushed by the water (peak speeds 0.34 to 1.91
m/s across the 17 runs), while the criteria themselves describe stationary vehicles. One
hull at three masses is a mass sensitivity study, not a class comparison; the hull fails the
ground-clearance axis for the class it was evaluated as. Realized particle density 302.6 to 663.6
kg/m³ across the three masses, all below water, so every configuration floats once fully
submerged; an earlier 100 to 300 kg/m³ plausibility band is retired. Grid convergence is non-monotonic, so the **direction** of the mass effect is quotable and
its **magnitude** is not (spread 1.9× to 4.9×). Particle passthrough 7.3 to 15.9 %; the zero
out-of-bounds count is a post-clamp residual, with 6,345 to 207,415 particle-frames clipped back
inside first.

## Numbers that must not be quoted

Retired by this project's own correction register, and deliberately absent from every deliverable
above: **"30.4 % agreement"**, **"23 conditions"**, **"16 divergences"**. All three come from the
closed Genesis SPH pilot on synthetic box geometry, which ran before the mass, friction and
viscosity fixes. The "23" that *is* current is a count of reclassified **scenario cells out of
70**, which is a different quantity from the retired "23 conditions"; do not merge them.

Any FORD/NO-FORD count must name the **rule** that produced it, not just the file. The canonical
implementation is `vehicle_params.L1_verdict` (depth cap **and** velocity cap **and** product, per
class); `simulation/can_it_ford_L1.py` calls it, with `small_passenger` as the default class.

## Not a safety standard

The AR&R criteria used throughout are that report's own *draft interim* figures for *stationary*
vehicles, and are explicitly not an endorsed safety standard. Its authors published the list of
gaps in them (friction coefficients in flood flows, buoyancy in modern cars, vehicle orientation
to flow), and this work aims at those gaps by name. **Nothing here is safety guidance. If a road
is flooded, turn around.**
