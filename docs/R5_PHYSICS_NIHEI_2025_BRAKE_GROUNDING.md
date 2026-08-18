# Nihei et al. 2025 read from the PDF: my "sub-physical" mu = 0.0250 is a MEASURED value

2026-08-18. Josie supplied the original paper. All numbers below are **[read]** directly
from it, not from a resolver.

**Nihei, Onomura, Bando, Inoue, Kashiwada, Yoshikawa & Tanaka (2025), "Full-scale
experimental assessment of passenger vehicle stability in flooding flow", Results in
Engineering 28:107189.** sha256 of the supplied PDF
`9b0f01fe4229b0148da47972e2ff20d330b788fe338139a7ca8bd7570d6086d1`.

**Metadata correction, and it is a warning about the resolver.** `R5_PHYSICS_BLOCKED_FLAGS.md`
recorded "three authors (Nihei, Onomura, Bando), not et al.", read from scite. **The paper
has SEVEN authors**, and scite's third name is wrong: the PDF gives **Yu Bando**, scite
gave "Yoshinori Bando". A metadata resolver is not a primary source, which is the same
lesson that produced the Kramer Table 1 corrections.

## 1. The finding that changes my own job A interpretation

**Measured rolling-resistance coefficients, handbrake DISENGAGED, from full-scale
washaway cases:**

| case | mu_R |
|---|---|
| Case 1-2 | **0.0250** |
| Case 2-4 | **0.0242** |

**My job A brake sweep used mu = 0.55 / 0.30 / 0.0250.** I described the 0.0250 arm as
"22x below canonical wet-road friction, so the flip is sub-physical", and the
physics-skeptic audit agreed, recording that it "has no vehicle-physical basis".

**Both of us were wrong. 0.0250 is Nihei's measured value, to three significant figures,
for a full-scale vehicle washed away with the handbrake off.** It is not an arbitrary
small number and not sub-physical. It is the physically correct coefficient for exactly
the condition the brake-state question was asking about.

**So the measured STUCK to SLIDE flip at mu = 0.0250 is the handbrake-disengaged case**,
which is the whole point of job A1 rather than a curiosity at an implausible parameter.
The "sub-physical" caveat in `R5_PHYSICS_JOB_B_RESULT.md` section 8.5 and in the job A
commit is **WITHDRAWN**.

## 2. Independent traction-force measurements, with N and spread

From separate traction tests, four road conditions (old/dry, new/dry, old/wet, new/wet),
five experimenters **[read]**:

| vehicle | mu_R |
|---|---|
| Wagon R | **0.0382 +/- 0.0081** |
| Voxy | **0.0206 +/- 0.0060** |

A t-test gives a **statistically significant difference between the two vehicles,
p < 0.01**, so rolling resistance is vehicle-dependent and a single value should not be
transferred between classes. The washaway values above (0.0250, 0.0242) sit inside this
range.

Also reported: mu_R is initially high and falls rapidly to a steady state at
**approximately 40% of its initial maximum**, so a single quoted mu_R must say whether it
is peak or steady.

## 3. Static friction: a LOWER BOUND, not a measurement

For Case 3 (handbrake **engaged**) **washaway did not occur**, so the experiment yields
only **mu_s > 0.038** by Eq. 6a. That is a bound, not a value, and it must not be quoted
as "Nihei measured 0.038".

Literature values the paper cites for mu_s: **0.30**; 0.39, 0.5, 0.68; and 0.26, 0.42.

**Bearing on this project's canonical `floor_friction = 0.55`:** it sits above the most
commonly cited 0.30 and inside the upper spread (0.39 to 0.68). I state that as a
comparison only. A sibling raised and then retracted a related claim, so I am not
asserting anything beyond what this PDF says.

## 4. Why this paper matters beyond the brake question

It is a **full-scale outdoor open-channel experiment on prototype passenger vehicles**
with frontal flow, hydraulic measurements and high-resolution vehicle accelerometry, and
the authors describe it as among the first to quantify the dynamic interplay between
hydraulic forces and vehicle response. It also reports that **flood-induced vibrations
trigger downstream displacement before abrupt washaway**, which is a qualitative match to
the drift-then-slide behaviour the classifier scores, and it achieves high Reynolds
numbers "unlike typical scaled model tests".

**Still outstanding:** this is the ORIGINAL. The **corrigendum**
(doi:10.1016/j.rineng.2025.107527) is still unfetched, and until it is read none of the
numbers above are final. FLAG-2b stays open.

**UNREVIEWED**: no physics-skeptic pass on this document.

## 5. Critical sliding velocities at the project's EXACT canonical depth

All **[read]** from section 3.3 of the paper.

**First a correction to section 1 above, before it propagates.** The vehicle in the
*flooding* experiments is the **Mira e:S X**. The Suzuki Wagon R and Toyota Voxy were the
*traction-force* tests. I nearly conflated them; the 0.0382 / 0.0206 figures are traction,
the 0.0250 / 0.0242 washaway figures are the flooding prototype.

**Stability criteria for the sliding mode, from Eq. 8, `V = sqrt(2 mu M g / (rho A_w C_D))`:**

| water depth | critical V, handbrake OFF | critical V, handbrake ON |
|---|---|---|
| **0.30 m** | **0.97 m/s** | **3.42 m/s** |
| 0.40 m | 0.78 m/s | 2.74 m/s |

Measured washaway events, for cross-check: Case 1-2 at **h = 0.289 m, V = 1.10 m/s**, and
Case 2-4 at **h = 0.294 m, V = 1.06 m/s**, both consistent with a 0.97 m/s criterion at
0.30 m.

**And the paper states: "the AR&R criteria agree well with the 'without handbrake'
stability criteria."** That is an external, full-scale corroboration of the AR&R
thresholds this project uses for L1, and it identifies which brake state they correspond
to, which the project's own L1 discussion has never specified.

### 5.1 A discrepancy against my own job A, stated but NOT resolved

**0.30 m is exactly the canonical depth of the 17 gated runs**, and `sweepV_g64_v0p5`
runs at **0.5 m/s**.

- At `mu = 0.55` my run gave **STUCK**. Nihei's braked criterion is **3.42 m/s**, far above
  0.5, so a braked vehicle should be stable. **Consistent.**
- At `mu = 0.0250` my run gave **SLIDE**. Nihei's unbraked criterion is **0.97 m/s**, about
  **twice** the run's 0.5 m/s, so an unbraked vehicle at this depth and velocity should
  **not** wash away. **The simulation slides at roughly half the experimentally required
  velocity.**

**I am not calling that a validation failure, and it must not be quoted as one.** At least
four things differ before any conclusion is available: the vehicle is a Mira e:S X and not
the Yaris hull; Nihei's criterion is a force-balance closed form (Eq. 8) using measured
`C_D` and `A_w`, not a simulation; the scene's own numbers are contaminated by the
reflection window and the leaking tank recorded elsewhere in this branch; and Nihei's
Eq. 8 explicitly neglects lift and buoyancy, which the simulation does not.

**What it does establish is that a comparison now EXISTS.** Until tonight this project had
no external number to place its verdicts against at its own depth. It now has one, with a
brake state attached, and the first look at it is a factor-of-two disagreement in the
direction of the simulation being less stable than the experiment.

**This is the single most checkable external claim available to this project and it should
be the next thing reviewed.** UNREVIEWED, and given four of four headlines were overturned
tonight, treat the factor of two as a lead, not a finding.
