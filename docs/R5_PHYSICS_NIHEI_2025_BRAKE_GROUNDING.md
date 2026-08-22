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

## 6. Section 5.1 is REFUTED. The factor of two was mine, not the physics.

Fifth headline overturned tonight. **Section 5.1 is withdrawn in full.** What survives is
section 1's withdrawal of "sub-physical", and the metadata correction. Nothing built on
top of them.

### 6.1 Rebuilt on the sim's own geometry the gap is 1.30, not 1.94

I listed four caveats and quantified none. Quantified, two of them absorb most of the gap:

- **Buoyancy removes 38.25% of the normal force.** Measured from `rollout.npz`: 1055 of
  8905 rigid particles submerged, `F_B = 4127.5 N` against `W = 10791.0 N`. Nihei's Eq. 8
  **drops** buoyancy, justified because his vehicle was barely wetted and stayed below its
  0.155 m ground clearance. The sim hull has **no ground clearance** and is wetted to
  0.2944 m. **The paper's own conclusion 4 says buoyancy LOWERS the sliding threshold**, so
  0.97 is an upper bound relative to the sim's regime, **by construction, in the direction
  of my "discrepancy".** I named this caveat and never stated its sign.
- **The sim is BROADSIDE, Nihei is FRONTAL only.** The kick and clamp act on x
  (`sim_standing.py:240`, `:275`) and the hull's x-extent is its **width**, so flow strikes
  the 4.2 m side. Measured submerged projected area ratio **1.750**; Nihei's limitations
  section puts it at 2.3x for his own vehicle and warns the body would **yaw rather than
  slide**, so the sliding criterion may be the wrong mode entirely.

Eq. 8 rebuilt with the sim's measured area, its 1100 kg and its buoyancy, at mu = 0.0250:
**0.651 m/s against the run's 0.5 m/s = 1.30x.** A 1.3 ratio on a closed form using a
borrowed `C_D` of 1.38 +/- 0.18 is not a reportable disagreement.

### 6.2 I labelled the WORST row "Consistent"

Applied across the whole sweep instead of the one arm I chose:

| mu | sim at 0.5 m/s | Nihei Eq. 8 | disagreement |
|---|---|---|---|
| 0.55 | STUCK, bracket (0.5, 1.0] | **4.668 m/s** | **4.7x to 9.3x** |
| 0.30 | SLIDE | 3.448 m/s | 6.9x |
| 0.0250 | SLIDE | 0.995 m/s | 2.0x |

**mu = 0.55 is the largest disagreement of the three and I called it "Consistent."** The
test I used ("3.42 is far above 0.5, so a braked vehicle should be stable") is one-sided
and **cannot fail**: any STUCK below the criterion "agrees". And I compared the 0.55 run
against a criterion computed at **mu_s = 0.30**; at 0.55 it is 4.67 m/s. I reported the
smallest of three discrepancies as the finding.

### 6.3 The novelty claim is refuted by this project's own code

"Until tonight this project had no external number to place its verdicts against at its
own depth" is **false**. AR&R's hazard product is implemented at `vehicle_params.py:209`
and forked at `gates.py:17` (`haz_m2s: 0.30`), and gives **1.0189 m/s** at the run's own
depth. **Nihei's 0.97 is 95.2% of a number the project has been computing all along** and
that is exactly the sentence I quoted at section 5 ("the AR&R criteria agree well with the
without-handbrake criteria"). Nihei adds a **brake-state label** for an existing threshold.
That is still worth having, and it is not a new external number.

### 6.4 Four further corrections

- **The unbraked curve uses mu_R = 0.0242, not 0.0250.** Stated twice: body text
  ("the smaller mu_R value obtained from the sliding cases ... i.e., 0.0242") and the
  Fig. 17 caption. At 0.0250 Eq. 8 gives 0.995, not 0.97. My section 1 headline elevates
  the value the paper itself declined to use for this calculation.
- **"To three significant figures" is refuted by the paper's own error analysis**:
  accounting for `C_D = 1.38 +/- 0.18` it states mu_R "could range from approximately
  **0.021 to 0.028**". That is +/-14%, two significant figures at best.
- **"Exactly 0.30 m" is wrong.** Realized depth is **0.2944294473039918**, and only **14 of
  17** runs sit there. 0.30 is the REQUESTED depth. Nihei's Case 2-4 at h = 0.294 m is the
  closer match and I missed it.
- **The washaway events are not a cross-check.** Eq. 6b back-calculates mu from those two
  events and Eq. 8 is Eq. 6b solved for V, so the points lie on the curve **by algebraic
  identity**.

### 6.5 The branch already predicted this, and I did not reconcile it

`R5_PHYSICS_BRAKE_STATE.md:164` scales the project's own measured bracket by sqrt(mu) and
predicts v_crit(0.0250) in **(0.107, 0.213] m/s**. I predicted 0.97. **A factor of 4.6 to
9.1, on the same branch, the same night, at the same mu**, and my document neither cites
nor supersedes it. Under the branch's own scaling, sliding at 0.5 m/s is exactly what was
expected and **there is no anomaly at all**.

That file also bounds the substitution I ignored: setting `floor_friction = 0.025`
simulates **a body sliding on a slippery floor, not a car rolling**. The hull has no
wheels. My "physically correct coefficient for exactly the condition" restores a claim a
sibling document had explicitly fenced.

### 6.6 What survives

The withdrawal of "sub-physical" (0.0250 is a literature number for an unbraked full-scale
vehicle, not an arbitrary one), the metadata correction (7 authors, Yu Bando), and the
quotations in sections 2, 3 and 5 as quotations. **Everything inferential is withdrawn.**
