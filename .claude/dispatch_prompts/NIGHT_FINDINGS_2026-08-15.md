# VERIFIED FINDINGS, 2026-08-14 evening into 2026-08-15
Coordinator record. Every number below was produced by a run that executed
tonight or read live from source. Retractions are included, not hidden.

## 1. THE ROOT CAUSE THAT RAN THROUGH THE WHOLE NIGHT

`sim_standing.py:235` gives the vehicle **8 frames** to settle as a free rigid
body under gravity, then captures `com0` and starts recording. The kick at :239
is `v[: self.n_water, 0] += velocity`, **water only**, so the vehicle is never
pushed directly. Eight frames is a hard-coded guess. This stack rings with
roughly a **100-frame period** (D9), so eight frames is deep inside the
transient.

Josie identified this by eye, from the video, before any instrument did: "why do
the cars move at the beginning, that makes no physical sense". It does not.

**Four separate results were the transient**, and every one looked physical:

| result | at short settle | at converged settle |
|---|---|---|
| D9 traction-margin spread | 6.07x | **1.94x** |
| D9 gate-error ordering | 63.28 / 94.44 / 157.06 increasing | **72.88 / 49.75 / 34.01 decreasing** |
| D9 measured vs analytic F_N | factor of 2 gap (Yaris) | **agree to 0.6-7.7%** |
| coordinator R7 mirror ladder | 63.3x, non-monotone | **monotone decreasing, passes** |

D9's own words: *three times out of three tonight, this stack's non-monotone and
dramatic-looking results have been short integrations.*

**Rule adopted:** no number from this stack may be quoted without stating the
settle length it was measured at.

## 2. CLAUDE.md ITEM 5 SURVIVES THE CONTROL. It is real.

D9, commit `c6eb8d2`. Re-ran the canonical ladder at `settle_frames=250`, a
**31-fold** increase, everything else held:

```
                canonical (settle 8)   control (settle 250)
g48 -> g64           +87.8%                 +95.9%
g64 -> g96           -59.2%                 -56.1%
monotone?              no                     no
absolute at settle 250:  g48 0.249207, g64 0.488112, g96 0.214442 m
```

Same sign, same shape, same magnitude. The explanation that killed every other
non-monotone result does not apply. Item 5 moves from an unexplained
non-monotonicity to one with the most likely artifact **ruled out**, which is a
stronger position than it has ever held. Steffen, Kirby and Berzins 2008 remains
the citation for the phenomenon. **Nobody may now call item 5 a possible
initial-condition artifact.**

## 3. A RESOLUTION CEILING EXISTS BETWEEN g96 AND g112

R7 mirror control, coordinator runs on Vista GH200, 200-frame settle throughout.
The scene is exactly y-symmetric by construction, so any asymmetry is a defect.

```
n_grid   mirror asym (m)   determinism floor (m)
  48         0.1701              0.0139
  64         0.0490              0.0737
  96         0.0244              0.0293
 112         1.6744              0.2880
 128         2.0252              1.6936
```

Below the ceiling the control converges and **passes below the floor** at g64 and
g96. Above it, a metre-scale violation appears.

**It is an instability, not a setup error and not a transient.** Frame ladder at
g112:

```
frames    mirror asym    floor
  20        0.3608      0.00568
  50        1.0911      0.02012
 100        1.9262      0.09369
 200        1.6744      0.28795
```

It **grows with time** and saturates near 2 m, which is domain scale. A setup
error would be constant; a transient would decay. Even at f20 the ratio is
already 63x, so a short run at fine resolution can look acceptable while broken.

**Reproducibility, checked because a single measurement burned me earlier:** the
g128 mirror value reproduces to **0.14 percent** across three independent runs
(2.0252, 2.0280, 2.0272), so the break is a property of the configuration. The
**floor** at g128 does not reproduce, spanning 0.52 to 1.69 m, so run-to-run
variation there exceeds a car length.

**Scope, stated honestly:** this is the R7 symmetric test domain, not the
canonical scene, and the two have different `grid_lim`. It does NOT by itself say
the canonical g128 is broken. **Operational rule:** any result at g112 or finer,
in any scene, must carry a repeat-run determinism floor and a frame count.

## 4. THE AT-REST GATE IS TUNABLE, SO IT CERTIFIES NOTHING

D9, commit `d2c13e8`, 24 runs on the GH200, band swept 0.25 to 2.0 dx at three
resolutions, Yaris, PPC 8, all else fixed. Gate error percent, `*` passes:

```
dx        0.25   0.50   0.75   1.00   1.25   1.50   1.75   2.00
0.14721  -90.7   -6.7*   45.9   63.3   76.4   81.7   82.8   82.5
0.09814  -32.1   16.9    29.3   37.1   23.3    2.8*  -4.3*  -14.2
0.07361  -70.8  -19.9     3.9*  52.3   96.2  108.9  116.1  132.6
```

**Every resolution contains a band that passes.** A gate any grid can satisfy by
moving one free parameter is not certifying the coupling. At the engine default
`band = 1.0 dx` the errors read 63.28, 37.06, 52.27, which is exactly the
non-monotone Yaris sequence, because the default ties band to dx and refining
cuts a **diagonal across three differently-shaped curves**.

D9 also refuted the simple form of its own hypothesis: the surface does not
collapse onto one curve. Zero crossings at 0.532, then **0.414 and 1.598**, then
0.709 band/dx, constant in neither variable, middle row crossing twice. So
"error is a function of band alone" dies alongside "error is a function of PPC
alone". What survives: band is a first-order control, tied to dx by default,
surface not of one shape.

## 5. PPC IS REFUTED AS THE MECHANISM

The Undermind multi-resolution report names fixed particles-per-cell as the
mechanism for losing convergence under refinement (its ref [4], Steffen 2008).
D9 co-refined PPC and the non-monotonicity **did not flatten**. Band width is
dominant instead, with `COLLIDER_FRICTION 0.4` influential. Record as a
**refuted hypothesis with its test**, not as an open question.

## 6. THE CHRONO TERRAIN DEFECT IS GENERAL, NOT ARCHITECTURAL

D13 built and ran on both machines, same Chrono SHA
`1b90a9f9854575f1ce1287d359d957b0273c075f`, same gcc 13.2.0, cmake 4.1.1,
Eigen 3.4.0, only the ISA differing.

```
class                       samples   bad   rate     worst angle
ON-VERTEX (both on grid)      3600   3600   100.0%    88.85 deg
ON-EDGE  (one on grid)        3600      0     0.0%     1.02 deg
INTERIOR (neither)            3600      0     0.0%     1.09 deg
```

x86_64 (LS6 c301-002) matched aarch64 (Vista) to three significant figures. So
`RigidTerrain::GetNormal` is a general Chrono/Bullet defect and goes upstream;
the GO verdict needs no architecture caveat. Origin is Bullet's trimesh raycast
callback, not Chrono, which populates correctly from
`ChCollisionSystemBullet.cpp:402-403`. **A heightfield puts its vertices on a
regular grid, so realistic terrain contact fails exactly where a road is
sampled.** Mitigation: rigid or FEA tyres (they never consult `GetNormal`), or a
heightfield/box patch instead of a trimesh.

## 7. THE RENDER: FOUR DEFECTS, ALL READ FROM SOURCE

1. **Water invisible.** `k = 1300 /m` at SSC 13000 mg/L gives black-disc visual
   range **0.00 m**, and the caption admits `k EXTRAPOLATED above the 670 mg/L
   linear bound`. The optics model runs **19x past its own validity limit**.
2. **The car has no material model.** `render_multigeom_rollout.py`:
   `sh = clip(n @ LIGHT,0,1)*0.6 + 0.4; return sh * base`. Lambert plus constant
   ambient, one light, no specular, no Fresnel, no clearcoat, no shadow, one flat
   colour. The **water** gets Schlick + Beer-Lambert + GGX; the **car** gets two
   lines of diffuse.
3. **The asphalt textures are already in the repo and unused.**
   `assets/Asphalt015_1K-JPG_Color.jpg`, `_NormalGL.jpg`, `_Roughness.jpg`, a
   complete ambientCG CC0 PBR set. Grep across all three render modules returns
   the HDRI at 8 sites and the asphalt maps at **0**.
4. **The caption is the figure**, roughly 70 percent of every frame.

**The real fix exists and is verified.** `splashsurf`
(InteractiveComputerGraphics) is a marching-cubes surface reconstructor
purpose-built for SPH/MPM particle output, with weighted Laplacian smoothing
specifically to remove the blobby look our per-column max-z heightfield produces.
**Verified live 00:17: `pysplashsurf` installs and imports on LS6.** Must be LS6,
not Vista: wheels cover x86_64/i686/armv7l, not aarch64. Published chain:
arXiv 2403.11156, SPH to SplashSurf to Blender.

## 8. CORPUS: THE ANSWERS WERE ALREADY ON THIS MACHINE

128 unique research artifacts across four roots. Reading the actual **paper
catalogs** rather than the summaries surfaced six papers directly on this problem
that have never been cited here:

- **Wasfy, Wasfy & Peters 2015**, DETC2015-47142, multibody + SPH **vehicle water
  fording**. In two separate catalogs.
- **Pazouki, Jayakumar & Negrut 2016**, vehicle mobility in fording. **The Chrono
  authors**, already in register A-1.
- **Khapane & Ganeshwade 2014**, SAE 2014-01-0936, wading simulation.
- **He et al. 2026**, doi 10.1115/1.4071177, with experimental validation.
- **Zhou et al. 2025**, Physics of Fluids doi 10.1063/5.0276643, **tire-pavement
  hydroplaning in MPM**. A tyre, a pavement, a water film.
- **Chen et al. 2022**, DETC2022-89632, MPM deformable terrain for vehicles.

So "nobody has simulated vehicle fording" is FALSE. "No validated vehicle-fording
**MPM** chain" survives, because those are SPH and multibody. And MPM **can** host
a real road, so our blockers are implementation blockers, not method blockers.

**Locked regression case, downloadable:** Kramer et al. 2021, Energies 14(2):269,
doi 10.3390/en14020269, public heave-decay dataset for a floating sphere at
approximately **0.3 percent** experimental uncertainty.

**We are below a threshold nobody had named.** `H/dp >= 5` is the DualSPHysics
minimum to capture the largest wave **at all** (Roselli 2018, Altomare 2017).
Canonical g64 runs at depth/dx = **2.000**; the matched-dx set at **3.500**. Both
below the minimum-wave-capture heuristic, which is sharper than L-3's wording.
There is **no formally validated force-convergence criterion** in SPH/MPM/PIC-FLIP
at all. Coarse over-predicts peak force via kernel truncation, boundary-particle
deficiency and neglected air cushioning, **but** over-fine can trigger premature
wave breaking and under-predict, so L-4 must not be written as a law.

## 9. RETRACTIONS I OWE

**My R7 mirror headline.** I reported 63.3x and a "third independent instance of
non-monotonicity" from a **single 20-frame run** measured inside the transient I
had diagnosed an hour earlier. D9 refuted it by sweeping `R7_FRAMES`; my own
four-rung 200-frame ladder confirmed the refutation. Both withdrawn.

**My mu = 0.55 framing.** I told six sessions it was an anomalous lab
rubber-mat value. **Martinez-Gomariz et al. 2017 measured 0.52 to 0.62** on a wet
metallic surface by spring balance and tilt angle across 12 model cars, which
brackets 0.55 by the same method. The real gap is between **measured** values and
the **adopted** 0.3, not between us and the field.

**The 0.3 convention's actual derivation**, which nobody had: Bonham & Hattersley
did not measure it. They took a braking coefficient of 0.5 and reduced it 10
percent for sideways, 20 for slip, 20 for debris. Smith 2019 measured **0.75 wet
/ 0.78 dry** and still adopted 0.3 for the published curves.

**Also new:** the critical orientation is **45 degrees** (Kramer 2016), not 0 or
90, and it is the axis nobody sweeps. A full-scale **Toyota Yaris** floated at
**0.40 m** under ~11 kN buoyancy (Al-Qadami et al. 2021, Natural Hazards).

## 10. STATE AT CLOSE

169 unpushed commits across 10 branches. `pushcheck` clean on nine; **D1 blocked**
on `docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md` because the repo is public and
D3 reports credentials still unrotated. D3's branch is DO-NOT-PUSH by design.
Main tree frozen at exactly **26** dirty entries all night, so nothing leaked
between worktrees across 13 concurrent sessions.

**LS6 cannot run warpmpm.** Its only copy is a 6-line stub that raises
`RuntimeError("stub: solver not needed for the PLY format check")`. Anything
warpmpm goes to Vista. LS6 is x86 and is the machine for Chrono and splashsurf.

**`--overlap` is mandatory** on `srun --jobid=` into an idev allocation, or the
step hangs behind the idev shell and dies. Launch detached with
`setsid nohup ... < /dev/null > log 2>&1 & disown` or a socket drop kills it.
