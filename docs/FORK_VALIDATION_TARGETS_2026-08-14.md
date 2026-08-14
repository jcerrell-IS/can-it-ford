# Fork validation targets, and the verdict quantity for a moving vehicle

Dispatch 11 of `docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md`.
Branch `claude/fork-validation`, Mac, no GPU, `docs/` only.

**Claim tagging used throughout.** `[live]` = read directly from a primary source
this session (Crossref REST, Scite, publisher landing page, or a file on this
disk). `[ctx]` = carried from the dispatch or CLAUDE.md and not independently
re-derived here. `[inf]` = inferred by me from `[live]` inputs, with the working
shown. Engine tags are given wherever a solver claim appears.

**Review status, stated tool by tool so the gaps are visible.**

| Check | Tool | Result |
|---|---|---|
| Every DOI cited by Dispatch 11 | **Crossref REST API** `[live]` | 23 of 24 resolve; the 24th is explained in section 8 and is valid |
| Editorial notices, retraction / correction / concern / erratum | **Scite** `[live]` | **None** on any of the 8 core flood-vehicle DOIs |
| Equation, units, and every percentage in section 2 | **Wolfram Language** `[live]` | Independently reproduced, see section 2 |
| Register consistency before commit | **`.claude/checks/register_integrity.py`** `[live]` | **0 blocking defects**, exit 0. 106 items, 10 sections. Its 5 WARNs are pre-existing and none is in a file I touched |
| Bibliography audit | **Scholar Sidekick `auditBibliography`** | **NOT AVAILABLE this session** |

The Definition of Done names Scholar Sidekick `auditBibliography`. **That tool is
not available in this session, so that specific check did not run.** Crossref plus
Scite plus Wolfram was substituted, every substitution is reproducible from
`docs/fork_validation_verify_dois.py`, and nothing here is asserted from memory. The
review is marked incomplete rather than faked.

---

## 0. Headline results, including three that overturn the dispatch

1. **The Qian fabrication is confirmed.** `[live]` `10.1016/j.cma.2022.114965`
   resolves to Schöller, Schneider, Herrmann, Prahs and Nestler, *Phase-field
   modeling of crack propagation in heterogeneous materials with multiple crack
   order parameters*, CMAME 395:114965 (2022). It is not Qian, not 2022 water
   entry, and not a half-buoyant cylinder. **Removed. Do not cite.**

2. **The Shah 2019-to-2021 amendment is right in substance and would be wrong if
   applied where it points.** `[live]` The Tier 2 entry `10.1111/jfr3.12657` is
   **2020** by every field Crossref carries (issued 2020-07-28, print 2020-12,
   volume 13 issue 4). There is no 2021 in that record. Two *different*
   Shah/Mustaffa/Martínez-Gomariz papers are issued-2019 / print-2021, both in
   *International Journal of River Basin Management*:
   `10.1080/15715124.2019.1566240` and `10.1080/15715124.2019.1687487`. The
   amendment belongs to those two. Applying it to the Tier 2 entry introduces an
   error where none existed.

3. **The dispatch's target list omits the closest computational analogue that
   exists, and it was already on this disk.** `[live]`
   `docs/Dynamic_Vehicle_Traction_in_Floodwater.md` is a 43-paper Undermind
   report at 98 percent coverage, dated 2026-07-21, asking almost exactly Dispatch
   11's question. It carries an entire coupled CFD/MBD and SPH/MBS *fording*
   lineage that appears nowhere in the dispatch's four tiers: Wasfy 2015, Pazouki
   2014 and 2016, Yamashita 2022, 2023 and 2024, Tison 2021, Liu 2023. He et al.
   2026, which the dispatch ranks first and says to read first, is the terminal
   paper of that lineage, not an isolated result. See section 3.

---

## 1. Ranked validation targets

Scale tags matter more than rank. Per the dispatch's own scale-effects note, and
`[live]` confirmed from the Kramer 2016 abstract, Froude scaling preserves the
gravity-to-inertia ratio but not the friction ratio, and the verdict depends on a
friction coefficient. **Every model-scale row below is therefore a target for the
hydrodynamics, not for the verdict.**

### Tier 1, measured vehicle experiments

| # | Source | DOI `[live]` | What is measured | Scale | Can validate | Cannot validate |
|---|---|---|---|---|---|---|
| 1.1 | Smith, Modra, Felder 2019, *J Flood Risk Manag* 12(S2) | `10.1111/jfr3.12527` | **Depth-resolved traction, directly measured.** Yaris 1045 kg: rear-axle traction 4.5 to 4.7 kN at 0 m falling to **0 kN at ~0.6 m**. Nissan Patrol 2478 kg: 9.3 to 9.6 kN falling to **0 kN at ~0.95 m**. Governing relation `F_F = mu*(W - B - L)`. Friction on concrete, gravel and sand; C_D at model scale | **Full scale** (prototype), C_D part model scale | The traction-vs-depth curve; the buoyancy-reduced normal force; worst-case friction | Propulsion. This is a **stationary sideways winch pull-test**. It bounds available traction and says nothing about a driven wheel. **Say this every time it is cited** |
| 1.2 | Smith, Modra, Felder 2017, *Experimental testing of flood hazard curves for a partially submerged vehicle* | no DOI located; Semantic Scholar `f9991961e7cd` | Threshold force to move a partially buoyant full-scale vehicle; C_D of a partially submerged vehicle; 18:1 companion model | **Full scale** + 18:1 | Same family as 1.1, and the earlier statement of it | As 1.1. **Not in the dispatch's list**; found `[live]` in the project's own corpus |
| 1.3 | Al-Qadami et al. 2021/2022, *Nat Hazards* 110(1):325-348 | `10.1007/s11069-021-04949-6` | Full-scale flooded passenger vehicle response, subcritical | **Full scale** | Floating depth and force response of a real car | Moving-vehicle traction. Cite year carefully: **online 2021, print 2022** |
| 1.4 | Arrighi, Alcérreca-Huerta, Oumeraci, Castelli 2015, *J Fluids Struct* 57:170-184 | `10.1016/J.JFLUIDSTRUCTS.2015.06.010` | Drag and lift contributions to incipient motion, numerically | Model | Force decomposition into drag and lift | Traction. Its **C_D 0.06 to 0.83** is for front/back-on flow and Smith 2019 states `[live]` it is "not directly comparable" |
| 1.5 | Hu, Li, Wang, Fang 2023, *J Hydrology* 620:129525 | `10.1016/j.jhydrol.2023.129525` | Stability thresholds at different flow orientations | Model | Orientation dependence | Any single-vehicle C_D. See the C_D warning in section 5 |
| 1.6 | Martínez-Gomariz, Gómez, Russo, Djordjević 2017, *Urban Water J* 14(9):930-939 | `10.1080/1573062X.2017.1301501` | Experiments-based stability threshold methodology for any vehicle | Model | A threshold method transferable across vehicles | A moving-vehicle threshold |
| 1.7 | Xia, Falconer, Xiao, Wang **2014**, *Nat Hazards* 70(2):1619-1630 | `10.1007/s11069-013-0889-2` | Vehicle stability criterion, theory plus experiment | Model | Incipient-motion criterion | **Cite as 2014.** `[live]` print and journal-issue are 2014-01, online 2013-10-11. This reproduces the standing project trap exactly |
| 1.8 | Teo, Xia, Falconer, Lin 2012, *Int J River Basin Manag* 10(2):149-160 | `10.1080/15715124.2012.674040` | Vehicle/floodplain-flow interaction | Model | Interaction forces | Full-scale thresholds |
| 1.9 | Kramer, Terheiden, Wieprecht 2016, *Int J Disaster Risk Reduct* 17:77-84 | `10.1016/J.IJDRR.2016.04.003` | Two scaled watertight models plus **one prototype car**; total-head criterion | Model **and** full scale | Total head 0.3 m passenger car, 0.6 m emergency vehicle | See the watertightness caveat in section 6 |

### Tier 2, moving-vehicle sources, which is our case

| # | Source | DOI `[live]` | What is measured | Scale | Notes |
|---|---|---|---|---|---|
| 2.1 | **He, Matthew, Yamashita, Harwood, Swafford, Martin, Grunin, Tison, Jayakumar, Sugiyama 2026**, *J Comput Nonlinear Dyn* 21(6) | `10.1115/1.4071177` | Free-running model vehicle in a shallow-water pool; transient cornering; flume-measured hydrodynamic loads | **Model scale, free-running** | **Read first, and it is stronger than the dispatch says.** This is the validation paper for the CFD/MBD lineage in section 3. Its own abstract states `[live]` "few or no experimental data available to characterize hydrodynamic loads for the evaluation of transient vehicle responses in shallow water" |
| 2.2 | Shah, Mustaffa, Martínez-Gomariz, Yusof **2020**, *J Flood Risk Manag* 13(4) | `10.1111/jfr3.12657` | Non-stationary 1:10 Perodua Viva, subcritical, varying Froude; incipient-velocity formula, R² = 0.85 | Model 1:10 | **2020, not 2019 and not 2021** (see headline 2). Buoyancy governed weight at depth >= 0.0457 m at model scale |
| 2.3 | Al-Qadami et al. 2022, *J Flood Risk Manag* 15(4) | `10.1111/jfr3.12828` | Full-scale car **moving perpendicular** to flow, FLOW-3D, coupled 6-DOF | Full scale, **numerical** | Critical depth 0.38 m, minimum d×v 0.39 m²/s. See section 4 |
| 2.4 | Shah, Mustaffa, Kim, Yusof 2018, *MATEC Web Conf* 203:07003 | `10.1051/matecconf/201820307003` | The only published moving force balance with an explicit driving term | Model 1:10 | Supplies the equation. Its measured driving force was 0.0017 to 0.021 N, numerically negligible `[ctx]`, so it does **not** constrain a traction budget |

### Tier 3, method comparison

| # | Source | DOI `[live]` | Note |
|---|---|---|---|
| 3.1 | Xin and Donghai **2021** (print) / 2020 (online), *Proc IMechE Part D* 235(1):3-15 | `10.1177/0954407020942005` | Rotating-wheel VOF/RANS against road tests. **Name-order caution:** Crossref records given="Zheng" family="Xin" and given="Su" family="Donghai". For Chinese names the surnames are far more likely Zheng and Su. Do not auto-generate a bib entry from Crossref for this one |

### Tier 4, canonical transferable hydrodynamics

**The ~0.3 percent benchmark is IDENTIFIED.** `[live]` It is **not** the dam-break
case. Traced to its source, `/Users/josie/Downloads/Moving_Rigid_Body_Free_Surface_Validation.md:19`,
which reads: "[20] provides an unusually precise public benchmark, with
approximately 0.3% experimental uncertainty."

> **Kramer, Andersen, Thomas, Bendixen, Bingham, Read et al. 2021**,
> *Highly Accurate Experimental Heave Decay Tests with a Floating Sphere: A Public
> Benchmark Dataset for Model Validation of Fluid-Structure Interaction*,
> **Energies 14(2):269**, DOI **`10.3390/en14020269`** `[live]` Crossref-confirmed.

`[live]` from the abstract: a 300 mm sphere, **ballasted to half submergence** so
the waterline sits at the equator at rest, held and released from three drop
heights spanning a linear case, a moderately nonlinear case, and a highly
nonlinear case starting fully out of the water. Uncertainties were computed from
random and systematic standard uncertainties and are, at 95 percent confidence,
"on average only about **0.3% of the respective drop heights**". The dataset is
public, the test case is formulated for reuse, and the paper already compares
linear potential flow, fully nonlinear potential flow and RANS.

**Why this is the right Tier 4 target for this fork specifically** `[inf]`: it is a
**free rigid body oscillating at a free surface**, so a single test exercises
buoyancy, added mass and radiation damping together, which is exactly the coupling
this project currently validates only *statically* at 7.3 to 7.7 percent (warpmpm,
SDF-collider path). Half submergence is close to the canonical hull's 31.05 percent
neutral-buoyancy fraction computed in section 2, so the regime transfers. And
because the paper already places three method families against the same data, an
MPM result can be reported *among* them rather than against a bare tolerance.

**Name collision, flagged before it lands in the bibliography.** `[live]` These are
**two different people with the same surname**, and the project already cites the
first heavily:

| Cite | Who | Affiliation | Topic |
|---|---|---|---|
| Kramer, Terheiden, Wieprecht 2016, `10.1016/J.IJDRR.2016.04.003` | **M. Kramer** (Matthias) | UNSW / Stuttgart lineage | Flood trafficability, total head 0.3 / 0.6 m |
| Kramer et al. 2021, `10.3390/en14020269` | **Morten Bech Kramer** | Aalborg University | Sphere heave decay benchmark |

Given `b46a6ce` already had to repair one BibTeX key collision in this project
(`akinci2012`), do not let `kramer2016` and `kramer2021` imply one author. Use
distinct keys and spell the given names out.

**The rest of the Tier 4 set, all `[live]` Crossref-confirmed**

| Case | Source | DOI |
|---|---|---|
| Accelerating-plate drag | Grift, Vijayaragavan, Tummers, Westerweel 2019, *J Fluid Mech* 866:369-398 | `10.1017/jfm.2019.102` |
| Free-surface proximity, sphere accelerated from rest | Waugh and Ellis 1969, *J Hydronautics* | `10.2514/3.62822` |
| Near-surface added mass and damping | Chung 1977, *J Hydronautics* | `10.2514/3.63081` |
| Dam-break obstacle pressures, measurements and video | Kamra, Al Salami, Sueyoshi, Hu 2019, *J Fluids Struct* 86:185-199 | `10.1016/J.JFLUIDSTRUCTS.2019.01.015` |
| Planing-hull forces | Russell, Ratcliffe, Fu, Fullerton, Grimsley 2007 | no DOI; Semantic Scholar `5310a381` |
| Baffled-tank loads with grid refinement | Sames, Marcouly, Schellin 2002, *J Ship Res* | no DOI; Semantic Scholar `743b13f7` |

### Excluded as a standard, per the dispatch, and I concur on the evidence

SPH work is admitted **only** as a pointer to experimental datasets, where the
dataset is the asset. Do not import SPH error bands, resolution guidance or
boundary treatment: SPH tolerance norms are loose for reasons specific to SPH, and
importing them would import a weaker standard.

**The one dataset-only entry, identified rather than assumed.** `[live]` The source
report tags it at line 20: "[37] is **SPH, dataset-only**: useful for its laboratory
vehicle measurements, not for SPH error bands or acceptance standards." Entry 37
resolves `[live]` to **Azhar, Pauwels, Bui 2023**, *Confirmation of vehicle
stability criteria through a combination of smoothed particle hydrodynamics and
laboratory measurements*, *J Flood Risk Manag*, `10.1111/jfr3.12885`,
Crossref-confirmed. **Its asset is the laboratory vehicle measurements and nothing
else.** Do not cite it for agreement bands.

Note this is a *different* Azhar paper from `10.1111/jfr3.70181` (Azhar, Bui,
Pauwels 2026, unsteady flow), which CLAUDE.md already cites for a 40 to 50 percent
drag increase. Same first author, two years, two roles. Keep the keys distinct.

---

## 2. The recommended verdict quantity: traction margin

**Recommendation: adopt the traction margin, evaluated as a per-step diagnostic
with the propulsion term set to zero.** This is the dispatch's arm (b), and the
argument for it is stronger than "best supported": **setting the drive term to
zero is precisely what makes the verdict validatable at all.**

### The equation

Smith 2019's governing relation for available traction, and Shah 2018's moving
force balance, combine into one dimensionless margin:

```
  F_N(h)    = W - B(h) - L(h)                        buoyancy-reduced normal force
  T_avail   = F_N * (mu + mu_RO)                     available + rolling resistance
  T_demand  = 0.5 * rho * C_D * A_D(h) * v_rel^2     hydrodynamic demand

  M(t)      = T_avail / T_demand          FORD while M > 1, NO-FORD once M <= 1
```

Shah 2018 writes the instability condition as
`0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV` `[ctx]`. Setting the driving force
`F_DV = 0` gives the margin above. Three reasons that is the right call, not a
compromise:

1. **It is conservative inside Shah's algebra, and I am flagging that this is not
   the same as being conservative in reality.** `[inf]` Within the equation as
   written, `F_DV >= 0` sits in the numerator, so dropping it can only lower M, and
   a FORD verdict at `F_DV = 0` survives adding propulsion back. **But if the
   friction circle governs** (caveat 2 below), a driven wheel spends friction budget
   on traction and therefore has *less* lateral resistance than a coasting one, so
   the true margin for a driven vehicle is **lower** than the `F_DV = 0` value, not
   higher. The two readings point opposite ways and the literature does not settle
   which dominates.
   **Net position, stated so it can be checked:** the `F_DV = 0` margin is exactly
   right for a **coasting or towed** vehicle, which is precisely what the validation
   literature covers, and is an **optimistic** bound for a driven one. Report it as
   such. This is a further reason arm (c) cannot be headlined.
2. **It is empirically justified.** `F_DV` was measured at 0.0017 to 0.021 N at
   1:10 scale `[ctx]`, negligible against every other term.
3. **It is the only version with a validation target.** Every term left in the
   equation is measured by Smith 2019 or Shah 2020. `F_DV` is the one term with no
   validation target anywhere (section 7).

Units check `[inf]`: `rho` kg/m³ × `A_D` m² × `v²` m²/s² = kg·m/s² = N; `F_N` × a
dimensionless mu = N. M is dimensionless. Consistent, and independently confirmed
in Wolfram (see below).

### A caveat on the equation itself, which I am raising rather than inheriting

Shah 2018's balance is a **single scalar equation standing in for two different
force balances**, and the fork should know that before adopting it. `[inf]` For a
vehicle crossing perpendicular to the flow there are two directions:

- **Along travel:** traction drives, rolling resistance and fluid resistance oppose.
- **Across travel, the flow direction:** drag pushes, tyre friction resists. This is
  the direction the sliding verdict is about.

Two consequences, both of which cut the same way:

1. **Rolling resistance opposes rolling, not lateral sliding.** Carrying `mu_RO`
   inside the resisting budget for a *lateral* verdict is not obviously right, and
   it inflates `T_avail` by `mu_RO/mu`, which at the quoted 0.092 and 0.3 is
   **+30.7 percent** `[inf]`.
2. **Driving and resisting share one friction budget.** A tyre has a single friction
   circle, so traction spent driving forward is *not* available to resist sideways
   drag. Shah's form has `F_DV` **adding** to the resisting side, which is arguably
   the wrong sign for that physics.

**Both are removed by the same change**, which is why the recommendation is the
stricter form:

```
  M_conservative(t) = mu * F_N(h) / (0.5 * rho * C_D * A_D(h) * v_rel^2)
```

Use this as the headline verdict. Report the `(mu + mu_RO)` variant alongside it as
an upper bound, and never report only the upper bound. `[inf]` This is my own
analysis of the source equation, not a claim made by Shah 2018, and it is stated
here so it can be argued with rather than silently inherited.

### Parameter provenance, every value traced

| Symbol | Value | Source | Status |
|---|---|---|---|
| `mu` | **0.3** conservative baseline | Bonham and Hattersley 1967, adopted for the published hazard curves. `[live]` Smith 2019 states via Scite full text that B&H "suggested this single conservative friction coefficient value after a detailed review of studies by Bird and Scott and adjustments for worst-case conditions of sideway forces and slipping forces rather than braking force and taking debris into account" | Traced |
| `mu` | 0.52 measured parallel to flow | Shah 2018 `[ctx]` | Traced, not re-read |
| `mu` | 0.75 wet / 0.78 dry on concrete | Smith 2019, measured tyre friction `[ctx]`, consistent with the abstract's concrete/gravel/sand statement `[live]` | Traced |
| `mu_RO` | 0.092 rolling | Shah 2018 `[ctx]` | Traced, not re-read |
| `W` | 1100.0 kg × 9.81 = 10791.0 N | `vehicle_params.py` mass_kg, CLAUDE.md canonical | `[live]` arithmetic |
| `B` | rho·g·V_sub, V_hull = 3.542739 m³ | canonical Yaris hull | `[live]` arithmetic |
| `L` | **0 only under subcritical flow** | Shah, Mustaffa, Yusof, Nor 2018 report lift insignificant subcritically; Martínez-Gomariz 2017 states buoyancy is negligible at high velocity and lift is not `[live]` via Scite | Conditional |
| `C_D` | **unresolved, see section 5** | four incompatible published ranges | **Weakest link** |
| `A_D` | depth-dependent submerged frontal area | geometry | Must be recomputed per depth, not fixed |

### Consistency check of the recommendation against its own anchor

`[live]` arithmetic, full working reproducible:

```
Yaris kerb 1045 kg -> W = 10251.5 N
  mu = 0.30 -> mu*W = 3.075 kN
  mu = 0.75 -> mu*W = 7.689 kN
  Smith 2019 measured rear-axle traction at zero depth: 4.5 to 4.7 kN
  mu = 0.3 applied to full weight understates that band by 31.7% to 34.6%
```

So the conservative mu = 0.3 is genuinely conservative against Smith's own
measurement, by about a third. **But do not invert this into a measured mu.**
`[inf]` The same inversion on the Nissan Patrol (2478 kg, 9.3 to 9.6 kN) gives an
implied 0.383 to 0.395 against the Yaris's 0.439 to 0.458. Two different implied
values from one relation means the measured quantity is an **axle-specific** load,
not `mu*W`. Treat 4.5 to 4.7 kN as a bound to check a model against, never as a
source for mu.

### Cross-check of the canonical hull against the project's own density anchor

`[live]` `W / (rho·g·V_hull) = 10791.0 / 34754.3 = 0.3105`, and
`1100 / 3.542739 = 310.494 kg/m³`, matching CLAUDE.md's canonical effective
density to all quoted digits. The buoyancy term in the margin is therefore
consistent with the gated geometry, and neutral buoyancy sits at **31.05 percent
submerged volume**. Worked margin at mu = 0.3, L = 0:

| submerged fraction | B (N) | W - B (N) | mu(W-B) (N) |
|---|---|---|---|
| 0.0000 | 0.0 | 10791.0 | 3237.3 |
| 0.1000 | 3475.4 | 7315.6 | 2194.7 |
| 0.2000 | 6950.9 | 3840.1 | 1152.0 |
| 0.3105 | 10791.2 | -0.2 | 0.0 |

### A falsifiable test nobody has run, and it is cheap

Smith 2019's zero-traction depths are a **direct, unused check on the canonical
hull**, because traction reaching zero means `W - B - L = 0`, so at that depth the
vehicle is exactly neutrally buoyant. Setting `L = 0`, the displaced volume
required at flotation is `V_sub = m / rho_water`:

| Vehicle | Mass | Zero-traction depth (Smith 2019) | Required `V_sub` `[inf]` | As a fraction of the canonical 3.542739 m³ hull |
|---|---|---|---|---|
| Toyota Yaris | 1045 kg | ~0.60 m | **1.0450 m³** | **29.50 %** |
| Nissan Patrol | 2478 kg | ~0.95 m | **2.4780 m³** | n/a, different vehicle |

**The test:** compute the canonical hull's submerged-volume curve `V_sub(h)` and
check whether `V_sub(0.60 m) ≈ 1.045 m³`. Pass means the project's hull reproduces
a full-scale measured flotation depth, which would be the first genuinely external
check on its geometry. Fail means either the hull is not a fair stand-in for
Smith's Yaris or the flotation model is wrong, and either answer is worth having.

**State this assumption when running it:** Smith's depth is measured above the road
surface, whereas the gated scene's `z = 0` is the floor plane, so ground clearance
must be handled explicitly. Getting the datum wrong moves the answer by roughly the
clearance, which is a large fraction of 0.6 m. `[inf]` Note the target 29.50 percent
sits just below the hull's own 31.05 percent neutral-buoyancy fraction, consistent
with Smith's 1045 kg being lighter than the canonical 1100 kg, which is a weak
positive sign but not the test.

### Independent verification of the arithmetic in this section

Every number above was computed twice, in two engines, and agrees: once in Python
and once `[live]` in **Wolfram Language**, which independently confirmed that
`M = T_avail / T_demand` is dimensionless, that `rho * A_D * v²` carries dimensions
`{Length 1, Mass 1, Time -2}`, that is kg·m/s² and therefore a force, and that
`W = 10251.5 N`, `0.30 W = 3.07544 kN`, the 31.657 and 34.565 percent
understatements, the 8.333 percent d×v spread, and `W/(rho·V) = 0.310494`.

### The two contrasting quantities, kept separate

- **Speed ceiling.** Pregnolato, Ford, Wilkinson, Dawson 2017,
  `10.1016/j.trd.2017.06.020` `[live]`, `v(w) = 0.0009w² - 0.5529w + 86.9448`,
  w in mm, v in km/h, R² 0.95, **flow velocity explicitly excluded**, 30 cm
  impassable. This is **driver control and serviceability, not stability**. It is
  the depth-only baseline to contrast against. A graded surface
  `v_max(depth, flow velocity)` does not exist in the literature and is claimable
  as original `[ctx]`.
- **Total head.** Kramer, Terheiden, Wieprecht 2016 `[live]`, abstract confirms
  "total heads of h_E = 0.3 m = const. and h_E = 0.6 m = const." for passenger
  cars and emergency vehicles respectively.

**Standing warning, restated because it is the easiest error to make.** The
Australian small-car limit is a limiting **still-water depth of 0.3 m**, not a
depth-times-velocity product of 0.3 m²/s. ARR Book 6 (Ball et al. 2019) uses
limiting depths 0.3 / 0.4 / 0.5 m for small car, large passenger car and large
4WD, with velocity capped at 3 m/s `[ctx]`. Never conflate a depth cap with a
hazard product.

---

## 3. The lineage the dispatch omits, and what it does to the novelty claim

`[live]` from `docs/Dynamic_Vehicle_Traction_in_Floodwater.md`, 43 papers, 98
percent coverage, 2026-07-21, already on this disk:

| Source | DOI | Why it matters |
|---|---|---|
| Wasfy, Wasfy, Peters 2015 | `10.1115/DETC2015-47142` | MBD **plus SPH** in one solver for **vehicle water fording**. Models suspension, wheels, steering, axles, differential and **engine**. Humvee-type vehicle through a shallow pool |
| Pazouki et al. 2014 | Semantic Scholar `2a3a1ddc` | Compares four fluid-solid coupling methods, "motivated by the desire to investigate vehicle fording scenarios" |
| Pazouki, Jayakumar, Negrut 2016 | Semantic Scholar `61da26b6` | *Investigation of the Vehicle Mobility in Fording*. Two-way coupled SPH/MBS; **point-cloud discretisation of the solid** gives accurate coupling forces. This is the architecture CLAUDE.md A-1 already cites as the correct alternative to velocity averaging |
| Yamashita et al. 2022 | `10.1016/j.oceaneng.2022.111607` | Coupled MBD/CFD, amphibious vehicles in the surf zone |
| Yamashita et al. 2023, 2024 | `10.1115/detc2023-115254`, `10.1115/1.4064971` | High-fidelity CFD/MBD generates training data for an LSTM hydrodynamics surrogate |
| **He et al. 2026** | `10.1115/1.4071177` | **Validates that chain** against free-running model-vehicle experiments and flume loads |
| Tison 2021 | `10.4271/2021-01-0252` | 6-DOF body dynamics coupled to VOF (STAR-CCM+), **with drivetrain power distribution to the wheels** |
| Liu, Xu, Pan 2023 | `10.1063/5.0174148` | RANS plus terramechanics plus body-force method; explicitly analyses **self-propelled** river crossing |

**Independence check, and it changes how much this lineage is worth.** `[live]` I
pulled the full author lists from Crossref rather than reading the titles, and
**five of the eight rows are one research group**, the University of Iowa and US
Army GVSC collaboration. The recurring names are Yamashita, Sugiyama, Martin,
Tison, Grunin, Jayakumar and Harwood:

| Row | Authors `[live]` |
|---|---|
| Yamashita 2022 | Yamashita; Arnold; Carrica; Noack; Martin; Sugiyama; Harwood |
| Yamashita 2023 | Yamashita; Martin; Sugiyama; Tison; Grunin; Jayakumar |
| Yamashita 2024 | Yamashita; Martin; Tison; Grunin; Jayakumar; Sugiyama |
| **He 2026** | He; Matthew; **Yamashita**; **Harwood**; Swafford; **Martin**; **Grunin**; **Tison**; **Jayakumar**; **Sugiyama** |
| Tison 2021 | Tison (sole author) |

Only Wasfy 2015, the Pazouki papers and Liu 2023 are genuinely separate groups.
**Per this project's own claim-discipline rule, one group's five papers are one
source, not five.** So the "validated fording chain" is a single unreplicated
program, and He 2026 is that program validating its own model rather than an
independent check on it. `[inf]` This makes the state of the art thinner than the
row count suggests, which **strengthens** rather than weakens the case for the fork.

**Effect on the novelty claim: the claim is correct as written, and I checked
whether it was.** `[live]` The dispatch says "No validated vehicle-fording **MPM**
chain exists" at both `:1120` and `:1491`. It is correctly scoped to MPM in both
places, none of the eight rows above is MPM, and so **nothing here contradicts it.**
I record this because my first reading dropped the word "MPM" and treated the claim
as refuted; it is not, and an unscoped paraphrase of it would have been the error.

What the eight rows *do* change is the **target list, not the claim**. The gap is
that this validated lineage is the closest methodological analogue the fork has and
it is absent from all four tiers. Two concrete consequences:

- **He 2026 is a comparison class, not just a paper to read.** It validates
  transient cornering response and flume loads at model scale. That is what
  "validated" currently means in this problem, and it is the bar an MPM result
  will be read against.
- **The honest novelty sentence** is therefore: the validated fording chain that
  exists is coupled CFD/MBD with a VOF or SPH fluid, at model scale, validating
  transient response rather than a stability verdict; no MPM equivalent exists,
  and no chain of either kind produces a validated fording go/no-go verdict.

---

## 4. The Al-Qadami contradiction: stated unresolved, and re-framed

**As the dispatch states it** `[ctx]`: Al-Qadami 2022 (moving, perpendicular)
gives 0.38 m and 0.39 m²/s; Al-Qadami 2023 (exposed, stationary) gives 0.38 m and
0.36 m²/s; an 8 percent spread across the moving-versus-stationary distinction.

**Both number pairs are confirmed** `[live]` from the two abstracts via Scite. But
three things change the reading, and all three cut the same way:

1. **The depths do not disagree at all.** Both report floating at **0.38 m**,
   identical. The entire spread is in the d×v sliding threshold: 0.39 against
   0.36 m²/s, `[inf]` a ratio of 1.083, so 8.3 percent. Describing this as an
   8 percent spread without saying *in which quantity* implies a depth
   disagreement that does not exist.
2. **These are not two independent measurements.** `[live]` Both are numerical,
   both by the same author group, and Al-Qadami 2023's own methods section states
   it used **FLOW-3D v11.2 under coupled motion and six degrees of freedom**, the
   same code family as the 2022 study. Per this project's own claim-discipline
   rule, one group running one code twice is one source, not two. The 8.3 percent
   cannot be attributed to the moving-versus-stationary distinction until someone
   controls for the model.
3. **A larger discrepancy sits inside the same paper and is not being quoted.**
   `[live]` Al-Qadami 2023 compares its own 0.36 m²/s against Martínez-Gomariz
   2017's Equation 12, which gives **0.47 m²/s**, and reports the gap itself as
   **25 percent**. The theory-versus-model gap is three times the
   moving-versus-stationary gap.

**A fourth number exists and should travel with the other three.** `[live]` Via
Scite, Al-Qadami 2022 records that the full-scale *experimental* floating depth
from the companion study was **0.40 m** against its own numerical 0.38 m, a 5
percent difference, and separately that its floating depth differs from Shah 2020
by **16 percent**, which that paper attributes to "the uncertainty of the
measurements and sealing capacity of the scaled-down vehicle." Scite classifies
that last citation as **contrasting**, the only contrasting citation in the whole
core set.

**Verdict: unresolved, as instructed, and do not average.** Report all four with
their framings attached: 0.38 m numerical moving, 0.38 m numerical stationary,
0.40 m full-scale experimental, and a 16 percent offset against the 1:10 model.
Resolving which applies to a **driven** vehicle remains a genuine contribution.
The cheap decisive experiment is a single held-fixed comparison: same code, same
mesh, same vehicle, moving versus held stationary, changing nothing else.

---

## 5. The drag coefficient is the dominant uncertainty, and the sources genuinely disagree

Flagged per operating-protocol item 2: independently reported results that
disagree about the same physical quantity.

| C_D | Source | Conditions |
|---|---|---|
| 1.1 to 1.15 | Keller and Mitsch 1992; Shu et al. 2011 `[live]` via Smith 2019 | Assumed from cylinder/rectangle analogy, not measured |
| **0.06 to 0.83** | Arrighi et al. 2015 `[live]` | Front/back-on flow. Smith 2019 states these "are not directly comparable" |
| **1.38 average** | Smith, Modra, Felder 2019 `[live]` via Scite | Measured, used for their published stability curves |
| ~1.7 | Hoerner 1965 flat plate `[live]` via Smith 2019 | Submerged flat-plate reference |
| **1.22 to 6.82** | Hu et al. 2023 `[ctx]` | A **joint envelope** over three vehicles and all flow orientations |

`[inf]` The published values span 0.06 to 6.82, more than two orders of
magnitude, and `T_demand` is linear in C_D, so C_D alone can move the margin M by
that same factor. **Consequences for the fork, both mandatory:**

- **Sweep C_D, never pick one.** Any single-value verdict is an artefact of the
  choice. The defensible product is a verdict *band*.
- **Do not quote the 4.02 midpoint of the Hu 2023 envelope as an estimate for any
  vehicle** `[ctx]`, and do not quote a 95.71 percent agreement figure until the
  per-vehicle table is read. A midpoint of a joint envelope over three vehicles
  and all orientations is not an estimate for one vehicle at one orientation.

---

## 6. Scale effects and watertightness, the latent variables

- **Most of Tier 1 is model scale.** Froude scaling preserves gravity-to-inertia
  but not friction or viscous ratios, and this verdict depends on a friction
  coefficient `[ctx]`. Every row in section 1 is scale-tagged for this reason.
- **Model-scale watertight vehicles float too shallow, confirmed at source.**
  `[live]` Kramer 2016's abstract: "the prototype experiments indicate that
  floating water depths are higher in prototype than in model scale, which is due
  to the use of a watertight vehicle model." So a watertight model reaches
  flotation at a **lower** depth than the real car.
- **This does not license pairing watertightness with the solver.** Register E2
  records that `FloodScene vehicle.py:162` samples the mesh to 60,000 surface
  points before solidifying `[ctx]`, so watertightness does not propagate into the
  simulation. The Kramer 2016 and Azhar 2026 (`10.1111/jfr3.70181` `[live]`)
  watertightness pairing stays blocked until E2 resolves.

---

## 7. Self-propulsion, stated plainly, with the boundary drawn honestly

**There is no validation target for a self-propelled vehicle fording a flood in
the flood-vehicle stability literature.** Every source in Tier 1 and Tier 2 treats
the vehicle as passive under drag, buoyancy and friction, or imposes prescribed
kinematics. Shah 2018 is the sole published force balance carrying an explicit
drive term, and that term measured 0.0017 to 0.021 N at 1:10 scale, so it supplies
an equation and constrains nothing.

**One necessary correction to the dispatch's F1, which claims no source anywhere
applies propulsion in a coupled fluid-vehicle simulation.** `[live]` That is too
strong. In the **amphibious and military** literature:

- Tison 2021 couples a 6-DOF solver to VOF with **drivetrain power distribution to
  the wheels** and terramechanics at the wheel/ramp contact.
- Liu, Xu, Pan 2023 explicitly analyses **self-propulsion** and self-propelled
  river crossing.
- Wasfy 2015 carries an **engine** in the multibody model, coupled to SPH, for
  vehicle water fording.

`[inf]` So self-propulsion coupled to a fluid solver **has been modelled**. What
has not been done is validating it against flood-vehicle stability data: those
three model ramp egress, launch and trans-media capability, and none is validated
against a fording stability threshold. **The accurate statement, which I recommend
for the paper:**

> Coupled self-propelled vehicle-fluid simulation exists in the amphibious-vehicle
> literature but has never been validated against flood-vehicle stability data,
> and no source applies engine torque to a road passenger car in a coupled flood
> simulation. Arm (c) is therefore exploratory and unvalidatable by construction.

**The FM 90-13 1.5 m/s rule stays doctrinal.** `[ctx]` The 44-paper search did not
establish an experimental basis for it. Field manuals are not scholarly literature
and a deep search will not resolve them; settle the provenance separately via DTIC
and the Army Publishing Directorate as primary documents, or do not cite it as a
target at all.

**Chrono does not change this.** `[ctx]` Chrono's fording capability is a physics
demonstration and visualisation, not a benchmark validated against experimental
fording data; its rigorously validated off-road work is soil and terramechanics.
This **strengthens** the novelty position: even the strongest existing stack, the
only one shipping both accumulated-force two-way coupling and a self-propelled
multibody vehicle, has not validated a fording verdict.

---

## 8. Citation hygiene: what changed, and the traps that remain

**Removed**
- `10.1016/j.cma.2022.114965`, "Qian et al. 2022, water entry of a half-buoyant
  cylinder". `[live]` Fabricated attribution. Resolves to a phase-field crack
  propagation paper by Schöller et al.

**Added as confirmed**
- Zhang, Zhao, Chen, Zhao 2026, *Stabilized explicit material point method for
  fluid flow and fluid-structure interaction simulations using dual high-order
  B-spline volume averaging*, CMAME 448:118428, `10.1016/j.cma.2025.118428`
  `[live]`. Title and journal confirmed exactly.
  **Trap:** Crossref records the first author as given="Zhang" family="Cheng".
  Given co-authors Shiwei Zhao, Hao Chen and Jidong Zhao, the first author is
  almost certainly **Cheng Zhang** and the Crossref record is transposed. An
  auto-generated bib entry will render "Cheng, Z." and be wrong. Set this one by
  hand.

**Year traps, all confirmed `[live]`, all of the same class (online year differs
from issue year)**

| Citation | Online | Print / issue | Cite as |
|---|---|---|---|
| Xia, Falconer, Xiao, Wang | 2013-10-11 | **2014**-01 | **2014** |
| Al-Qadami et al., *Nat Hazards* | 2021-07-26 | 2022 | 2021 with the print year noted |
| Xin and Donghai, *IMechE D* | 2020-07-27 | **2021**-01 | 2021 |
| Shah et al., *J Flood Risk Manag* | 2020-07-28 | 2020-12 | **2020**, never 2019 or 2021 |
| Shah et al., *IJRBM* (two papers) | 2019 | **2021** | the 2019-to-2021 amendment applies **here** |
| Garoosi et al., *Int J Mech Sci* | 2021 | **2022**-02 | 2022 |

**The Shah given-name conflict, resolved.** `[live]` Crossref **and** Scite both
give the first author of `10.1111/jfr3.12657` as **Syed Muzzamil Hussain Shah**.
The project's own corpus document, sourced from Semantic Scholar, gives "Syed
Hamid Hussain Shah". Two registries against one, so **Muzzamil** is better
supported. `[inf]` The likely mechanism is cross-contamination with the co-author
**Ebrahim Hamid Hussein Al-Qadami**, whose given names are exactly the intruding
string. This closes the standing project trap.

**A DOI that fails Crossref but is entirely valid.** `[live]`
`10.3970/CMES.2008.031.107` returns HTTP 404 from the Crossref API, but resolves
through doi.org (302) to techscience.com and serves *Examination and Analysis of
Implementation Choices within the Material Point Method (MPM)* by M. Steffen,
P.C. Wallstedt, J.E. Guilkey, R.M. Kirby and M. Berzins, University of Utah,
CMES 31(2). All five authors match. **Tech Science Press DOIs are not indexed in
Crossref; a Crossref miss is not evidence of a bad DOI.** Do not "correct" this
citation and do not let an automated bibliography audit drop it.

**Do not cite Smith 2019 for a drift threshold.** `[live]` The project already
records that "Smith et al. 2019, Eq. 6" does not exist, and that the
`DRIFT_THRESHOLD = 0.05 m` framing traces to Xia et al. 2014 and Shah et al. 2018
instead. Smith 2019 is the traction anchor here and nothing else.

**Editorial notices.** `[live]` Scite returned **no retraction, correction,
concern or erratum** on any of the eight core flood-vehicle DOIs checked.

---

## 9. Open items handed on

1. **CLOSED this session.** The Tier 4 ~0.3 percent benchmark is Kramer et al.
   2021, `10.3390/en14020269`. Method note worth keeping: two literature searches
   failed to find it and reading the source report's own line 19 found it in one
   step. **When a figure comes from a report, read the report, do not re-derive
   the figure.**
2. **C_D disagreement unresolved** (section 5). Needs the Hu 2023 per-vehicle
   table read before any single value or agreement percentage is quoted.
3. **Al-Qadami spread unresolved** (section 4). The decisive test is a held-fixed
   moving-versus-stationary comparison in one code.
4. **Smith 2017 has no DOI located.** Tier 1 row 1.2 currently rests on a Semantic
   Scholar identifier only.
5. **Two IJRBM Shah papers are the real subject of the year amendment** and were
   not previously in any target list. `[live]` They are a **companion pair in one
   volume**, consecutive in pagination, both issued 2019 and printed 2021:
   - `10.1080/15715124.2019.1566240`, *Criterion of vehicle instability in
     floodwaters: past, present and future*, IJRBM **19:1-23**
   - `10.1080/15715124.2019.1687487`, *A review of safety guidelines for vehicles
     in floodwaters*, IJRBM **19:25-41**

   Both are reviews rather than new measurements, so they are context and
   provenance sources, not validation targets. Recommendation: cite them for the
   history of the instability criterion, keep them out of the ranked tiers, and
   cite them as **2021**.
6. **Scholar Sidekick `auditBibliography` was unavailable this session.** Every
   DOI here is Crossref-verified and the core set is Scite-verified, but the
   specific tool named in the Definition of Done did not run. Marked, not faked.

---

## Reproducibility

The DOI audit is a script, not a transcript:
**`docs/fork_validation_verify_dois.py`**, committed alongside this document, queries
the Crossref REST API for **37 DOIs** and prints title, online year, print year,
journal, type, authors and any `update-to` flag for each. That is the 24 cited by
Dispatch 11, plus the five Tier 4 benchmark DOIs identified here, plus the six
CFD/MBD fording-lineage DOIs from section 3, plus the two IJRBM Shah papers the year
amendment actually refers to. Run `python3 docs/fork_validation_verify_dois.py`.

**Last run: 36 OK, 1 unresolved.** Two results look like failures and are not:

- `10.3970/CMES.2008.031.107` returns HTTP 404 because Tech Science Press is not
  indexed in Crossref. The DOI is valid and resolves through doi.org (section 8).
  **This is the only non-OK line and it is expected.**
- `10.1016/j.cma.2022.114965` returns `OK`. That is the point: it resolves
  *successfully* to the **wrong paper**, which is the fabricated-attribution finding
  (headline 1). A script that only checks whether a DOI resolves would pass it.
  **Read the returned title, never just the exit status.**

The Scite editorial-notice check and the smart-citation evidence in sections 4 and
5 are not in the script; they were run interactively against the Scite MCP and are
reproducible by querying the same eight core DOIs.
