# The hero shot: you already ran it, you rendered a different one, and here is what to say

Written 2026-08-26 against a live sweep of the repo, Vista and the render tree. Written because
the honest version of this story is better than the one currently on the poster, and because the
image most likely to be used as the hero shot is mislabelled in a way a reviewer would catch.

---

## 1. The catch: the beautiful render is NOT the high-resolution run

`renders/r9_cycles_2026-08-19/canitford_g160_no_surround.png` is a genuinely hero-quality
Cycles render, and its own burned-in caption reads:

```
MOVING VEHICLE, n_grid 160, 22 m domain: NO presentational surround, NO edge taper
PHYSICS, from the solver: nominal depth 0.3 m   inflow 1 m/s   n_grid 160
                          dx 0.13750 m    4 water layers
```

**`n_grid 160` with `dx 0.13750 m` and 4 water layers.** The actual high-resolution run has
`dx 0.05889 m` and **10** water layers. The render is on a 22 m domain, so the same `n_grid`
buys a much coarser cell.

**`n_grid` is not a resolution.** `grid_lim` follows the domain extent, so two runs labelled
`g160` can differ by 2.3x in `dx`. At `dx 0.1375` this render sits in the same resolution class
as the published `g64` (`dx 0.1472`), not above it.

**If that image is captioned "our highest-resolution simulation", the claim is false**, and the
falsifying evidence is printed on the image itself. The caption already does the right thing by
naming `dx` and the layer count; the risk is a voiceover that says "160" and lets the viewer
infer the rest.

---

## 2. The good news: the hero simulation already ran, and its data is intact

**Job 918350, `r6rep_g160`, COMPLETED in 00:06:21 on 2026-08-17** on a Vista GH200 [CONFIRMED
live via `sacct`].

| property | value |
|---|---|
| configuration | `g160_m2337`, 5 repeats, 90 frames, canonical driver |
| `dx` | 0.05889 m |
| water layers | **10** |
| `n_water` | **906,806** |
| verdict | **STUCK 5 of 5**, all five `metrics.csv` bit-distinct |
| joint frames | [0, 0, 0, 0, 0], margin [-3, -3, -3, -3, -3] |

**The data survives.** `/work/11603/jcerrell0629/vista/r6_rep_g160_918350` holds **5.5 GB**
across `rep_1` through `rep_5`, each with `rollout.npz`, `metrics.csv` and `summary.json`
[CONFIRMED live 2026-08-26]. This is Vista `$WORK`, which is not purged on atime the way LS6
`$SCRATCH` is, so it is not at immediate risk.

**It has never been rendered.** No frame sequence, no video, nothing in `renders/` corresponds to
it.

So the honest statement is not "I do not have a hero-worthy simulation." It is: **the hero
simulation ran nine days ago, it is 5x larger than anything on the poster, it produces a more
interesting result, and nobody has pointed a camera at it.**

---

## 3. Why it is the better story

The published headline is 16 SLIDE / 1 STUCK across g48 to g96, which is 3 to 6 particle layers.
The only depth-based resolution convention the literature offers is roughly **10 particle layers
across the flow depth** (Reis et al. 2021, `10.1016/j.engstruct.2021.113280`). Every published
run sits below it.

Extending the ladder for the heaviest vehicle, 5 repeats per rung:

| grid | water layers | verdict (N=5) | margin |
|---|---|---|---|
| g48 | 3 | SLIDE 5/5 | 8 |
| g64 | 4 | SLIDE 5/5 | 6 |
| g96 | 6 | SLIDE 5/5 | 0 to 1 |
| g128 | 8 | SLIDE 5/5 | 0 |
| **g160** | **10** | **STUCK 5/5** | **-3** |

`g192` is a second STUCK, so it is not one rung misbehaving.

**The prediction was written into the job's own sbatch header before the run**, on the argument
that coarse resolution over-predicts hydrodynamic force and the whole published ladder sat below
the convention. That is a pre-registered prediction that fired. **For a video, that is worth more
than a clean result**: it is the difference between showing an answer and showing a method.

Notice also that the margin column collapses monotonically, 8, 6, 0-1, 0, then -3. The verdict
does not lurch; it walks to the boundary and crosses it. And the `sustain_frames` fragility that
makes the published verdicts threshold-sensitive **vanishes** at g160: with 0 joint frames it is
STUCK at every threshold tested.

---

## 4. What you must NOT say, and what you can say instead

### Do not claim the forces are physically accurate

The settled vertical force is grid-converged at about **1.8x analytic static buoyancy**:
1.6823 at g96, 1.7662 at g128, 1.7944 at g160, with under one percent spread inside each rung
[CONFIRMED, `data/r9_speed_surface.tsv`]. It converges, and it converges to 1.8 rather than to 1.

**But do not call it a bug either, because two hypotheses were tested and both died:**

- **Not a misread.** A third accessor sharing no code, no grid nodes and no knowledge of the
  collider agrees with the primary one to 0.9 to 1.9 percent. The fluid really is pushing that
  hard.
- **Not volumetric locking.** A particles-per-cell sweep over a 19x span returned a slope flat at
  0.41 sigma where locking demands `PPC^-2`. Refuted on its own signature.

**Where it actually lives:** the disturbance is confined to the floor and the bulk pressure field
is hydrostatic. Read from the pinned solver, the floor `add_plane` registers a *grid* collider
that projects out the normal velocity component and writes it back to a grid node. **It writes
velocity, never pressure, and there is no boundary particle of any kind.**

**Sayable, and true:** "The force instrumentation is verified by three independent accessors
agreeing to under two percent. The force itself sits about 1.8 times analytic static buoyancy,
and that excess is localized to the floor boundary treatment, which writes a velocity rather than
a pressure. Whether that treatment is right is an open question, and it does not go away with
refinement, because the ratio is already converged."

### The line that makes it credible rather than weak

**The validated coupling path is not the one the results run on.** The SDF-collider path
validates against analytic buoyancy to **7.3 to 7.7 percent**. The free-rigid material-8 path,
which is what all 17 gated runs and the g160 ladder use, is the one showing 1.8x. Two coupling
architectures in the same solver, and the accurate one is not the one in production.

That is a specific, checkable, fixable statement. It also gives the video an ending.

### Do not imply a reconstruction fed a simulation

**No Gaussian splat has ever entered a simulation.** The splat pipeline (PSNR 22.7356,
1,147,694 Gaussians) was trained and validated in isolation. If splat footage and simulation
footage are cut together, say in the voiceover that they are two stages that are not connected.
The poster already says this under Scope; the video should match its words.

---

## 5. The three things to do, in order

**1. Render job 918350. This is the whole gap.** The run is done, the rollout is on disk, and the
render pipeline already exists and has produced hero-quality output. Pull `rep_1/rollout.npz`
from `/work/11603/jcerrell0629/vista/r6_rep_g160_918350/` and run the same Cycles path that made
`canitford_g160_no_surround.png`. Keep the burned-in caption convention, and this time `dx` will
read 0.05889 and the layer count will read 10.

**2. Caption it with the ladder, not with a single number.** The image that lands is the one
showing `g96 SLIDE, margin 0-1` beside `g160 STUCK, margin -3`. A single frame of a car in water
is a screensaver. A frame of a car in water beside the rung where the answer changed is a result.

**3. Do not re-render the 22 m image as the hero.** Keep it, it is a good moving-vehicle shot,
but caption it as the 4-layer moving case it is.

---

## 6. If there is time for one more run

Run the g160 configuration on the **SDF-collider path** instead of the free-rigid path. That is
the single experiment that would let you say "physically accurate" about a force rather than
about an instrument, because the SDF path is the one already validated to 7.3 to 7.7 percent.
Job 918350 took **6 minutes 21 seconds**, so the cost is small and the allocation exists.

**If it agrees with the free-rigid verdict, the STUCK result is coupling-independent and that is
a much stronger claim than anything currently on the poster. If it disagrees, that is a bigger
finding still.** Either outcome is publishable and either outcome is a better ending than the
current one.
