# Findings, deliverables and public surfaces

Reader-facing outputs for **Can It Ford?** — NSF SCIPE REU 2026, GeoElements Lab, TACC / UT Austin.
Josie Cerrell, Claremont McKenna College.

> Add a link to this file from `README.md` if you want it on the repository front page.

## Interactive

| Surface | URL |
|---|---|
| Findings site (overview) | https://jcerrell-is.github.io/can-it-ford/ |
| Verdict Explorer — drive the four-rung ladder | https://jcerrell-is.github.io/can-it-ford/verdict-explorer.html |
| Silent Failure Catalogue — the methods record | https://jcerrell-is.github.io/can-it-ford/failure-catalogue.html |
| Same site, mirrored on Hugging Face | https://huggingface.co/spaces/josiecerrell/can-it-ford-findings |
| Scenario sweep dataset (browsable viewer) | https://huggingface.co/datasets/josiecerrell/can-it-ford-scenario-sweep |
| Gradio demo | https://huggingface.co/spaces/josiecerrell/can-it-ford |
| Experiment tracking | https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford |

Pages are served from `docs/` on `main`. They are compiled bundles — regenerate them from source
rather than hand-editing. Each fetches `docs/_ds/josie-design-system-…/_ds_bundle.js` at runtime;
everything else is inlined. `docs/.nojekyll` is what stops GitHub Pages hiding that underscore
directory.

## The result, in three lines

The field decides fordability with a hazard product, depth times velocity, against a published
threshold. Checked against a coupled material-point simulation of the same scenario, it fails
three separable ways:

1. **It cannot see still water.** At zero velocity the product is zero whatever the depth, so a
   metre of motionless water scores zero hazard and passes any threshold. Arithmetic — no
   simulation required.
2. **It cannot see mass.** Bit-identical at 0.441644 m²/s across a 2.1× mass range, because the
   criterion has no mass term. The simulation separates the same cases.
3. **It reads the wrong depth.** The criterion needs a value of *D* and never defines which for a
   transient surge. At the road: 0.45000 m²/s. At the hull, in its own bow wave: 0.189 to 0.153 —
   58 to 66 percent lower, and across the threshold.

Correcting this project's own encoding of the criterion reclassified **23 of 70 scenario cells,
all toward NO-FORD, none loosened** — 11 from restoring the depth cap with class held fixed, 12
from evaluating an 1100 kg car against its own published class.

## Scope

**Established.** 20 coupled runs of a crash-validated 2010 Toyota Yaris hull across three grid
resolutions, three masses, five velocities and three depths. Determinism verified on 17 of 20; the
3 dry-start runs carry no record. Mesh containment 100.00 % of a 2000-particle subsample. D×V
bit-identical across the mass range, tested with `float.hex()`. Eight geometry and physics gates
reported: six pass, one fails, one noted.

**Open.** No reconstructed scene has entered a simulation — Gaussian splatting *did* run, to
676,452 Gaussians at PSNR 21.05 / SSIM 0.727 / LPIPS 0.442, but the bridge from those kernels to
solver particles was never built, so **no verdict here starts from video**. Vehicle velocity is
zero throughout, a stationary-vehicle study, which is what the criteria themselves measure. One
hull at three masses is a mass sensitivity study, not a class comparison; the hull fails the
ground-clearance axis for the class it was evaluated as. Realized particle density 302.6–663.6
kg/m³, above this project's own 100–300 band, reported as a failed gate rather than explained
away. Grid convergence is non-monotonic, so the **direction** of the mass effect is quotable and
its **magnitude** is not (spread 1.9× to 4.9×). Particle passthrough 7.3–15.9 %; the zero
out-of-bounds count is a post-clamp residual, with 6,345 to 207,415 particle-frames clipped back
inside first.

## Numbers that must not be quoted

Retired by this project's own correction register, and deliberately absent from every deliverable
above: **"30.4 % agreement"**, **"23 conditions"**, **"16 divergences"**. All three come from the
closed Genesis SPH pilot on synthetic box geometry, which ran before the mass, friction and
viscosity fixes. The "23" that *is* current is a count of reclassified **scenario cells out of
70**, which is a different quantity from the retired "23 conditions" — do not merge them.

Any FORD/NO-FORD count must name the **rule** that produced it, not just the file. The canonical
implementation is `vehicle_params.L1_verdict` (depth cap **and** velocity cap **and** product, per
class); `simulation/can_it_ford_L1.py` is product-only and is **not** the full rule.

## Not a safety standard

The AR&R criteria used throughout are that report's own *draft interim* figures for *stationary*
vehicles, and are explicitly not an endorsed safety standard. Its authors published the list of
gaps in them — friction coefficients in flood flows, buoyancy in modern cars, vehicle orientation
to flow — and this work aims at those gaps by name. **Nothing here is safety guidance. If a road
is flooded, turn around.**
