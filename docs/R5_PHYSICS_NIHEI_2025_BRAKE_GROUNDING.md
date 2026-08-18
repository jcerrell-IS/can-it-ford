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
