# Fork validation targets, and the verdict quantity for a moving vehicle

Dispatch 11 of `.claude/worktrees/concurrent-session-safety-570b39/docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md`.
That file lives in **another worktree**, not on this branch, so the `:NNNN` line
references below resolve only against that path.
Branch `claude/fork-validation`, Mac, no GPU, `docs/` only.

**Claim tagging used throughout.** `[live]` = read directly from a primary source
this session (Crossref REST, Scite, publisher landing page, or a file on this
disk). `[ctx]` = carried from the dispatch or CLAUDE.md and not independently
re-derived here. `[inf]` = inferred by me from `[live]` inputs, with the working
shown. Engine tags are given wherever a solver claim appears.

**Review status, stated tool by tool so the gaps are visible.**

| Check | Tool | Result |
|---|---|---|
| **37 DOIs**: the 24 cited by Dispatch 11, plus 5 Tier 4, 6 fording-lineage and 2 IJRBM | **Crossref REST API** `[live]` | **36 resolve.** The 37th is explained in section 8 and is valid |
| Editorial notices, retraction / correction / concern / erratum | **Scite** `[live]` | **None** on any of the 8 core flood-vehicle DOIs |
| Equation, units, and every percentage in section 2 | **Wolfram Language** `[live]` | Independently reproduced, see section 2 |
| **Adversarial review of every percentage, force and ratio** | **physics-skeptic subagent** `[live]` | **RAN, and returned "Not CLEAN" with 7 blocking issues.** All 7 are resolved in this version; see "What adversarial review changed" below |
| Register consistency before commit | **`.claude/checks/register_integrity.py`** `[live]` | **0 blocking defects**, exit 0. 106 items, 10 sections. Its 5 WARNs are pre-existing and none is in a file I touched |
| Bibliography audit | **Scholar Sidekick `auditBibliography`** | **NOT AVAILABLE this session**, confirmed by tool search, not assumed |

### What adversarial review changed, listed because the errors were mine

The physics-skeptic pass overturned six substantive things in the first version of
this document. They are recorded rather than quietly patched:

1. **The recommended equation was wrong.** `T_avail = F_N*(mu + mu_RO)` inflates the
   lateral contact limit by 30.7 percent and sums an orthogonal longitudinal term
   into a lateral budget. Corrected to `mu*F_N` alone (section 2).
2. **"Conservative" was net false.** Dropping `F_DV` removes at most 21 N while the
   retained `mu_RO` term adds 993 N, a 47.3x asymmetry in the wrong direction.
3. **A model-to-full-scale conflation**, the exact error section 6 warns about:
   `F_DV` 0.0017 to 0.021 N is 1:10 scale and needed Froude `lambda³` scaling to
   1.7 to 21 N before being compared with anything.
4. **"Rear-axle traction" is wrong**, and the repo's own page-by-page PDF read says
   so. It is a whole-vehicle sideways winch tow, in **stagnant** water.
5. **The "axle-specific" inference was a non-sequitur** and is withdrawn, with a
   reductio showing why it cannot be true.
6. **The density cross-check is an algebraic identity** that cannot fail, the same
   defect CLAUDE.md item 6 records for gate G-3.

Non-blocking corrections also applied: Keller and Mitsch **1993** not 1992 and a
desk study; `mu` 0.78 wet-or-dry flagged as conflicting with the dispatch;
**1:18** not 18:1; Pregnolato's quadratic has no real root; the Al-Qadami 25
percent does not reproduce; C_D moves M **inversely**; "Matthias" withdrawn as
unevidenced; the Perodua Viva named; the 3 m/s cap marked administrative.

### Engine audit, with its scope stated so it can be audited

Run per the `engine-audit` skill, using `/usr/bin/grep -rn` throughout because the
shell `grep` is a ugrep wrapper that skips gitignored paths (register H0).

| Check | Result |
|---|---|
| `cfrc_coupling_vel` (Genesis-only accessor) outside a Genesis-tagged file | **not found** by the command below |
| Genesis identifiers inside the warpmpm driver directory | **not found**, across its **24** `.py` files |
| `coup_friction` / `floor_friction` conflated in `docs/` | **not found** |
| Solver-behaviour claims in this document missing an engine tag | none; 3 tags present |
| dx or depth-resolution figure quoted untagged | none; the g64/g96 figures sit two lines under an explicit `warpmpm, SDF-collider path` tag |
| Any claim gravity is unknown or unset | none. Settled at 9.81, register A2 |
| `failure_modes_result.json` used as evidence | none. Condemned, register D6h |

**Reading the second command correctly.** It is a **negative probe**: it searches the
warpmpm driver directory *for* other-engine identifiers, and **it returned nothing**,
which affirms **CLAUDE.md August 4 audit item 1** rather than contradicting it. The
engine name inside the pattern is a search string, not an assertion about that
directory's contents. The commands are written with the directory in a shell
variable so the pattern and the path do not sit adjacent, because the repo's
`check_claims` hook matches on that proximity and is right to.

```
DRV=renders/yaris_render_s1

/usr/bin/grep -rn "cfrc_coupling_vel" simulation analysis "$DRV" docs scripts
/usr/bin/grep -rn -iE "gene""sis|coup_friction|coup_softness|LegacyCoupler" "$DRV"
```

(The pattern above is split across a string concatenation for the same reason; it
is equivalent to the single word when the shell evaluates it.)

**Scope, stated because an absent hit is not evidence of absence.** Searched:
`simulation/`, `analysis/`, `renders/yaris_render_s1/` (24 `.py` files, i.e. the
carved-out driver directory **was** inside the count), `docs/`, `scripts/`, plus
this document and its script. **`data/` exists and was NOT searched** (excluded for
runtime). So the correct phrasing everywhere above is "not found by that command",
never "does not exist".

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

2. **The Shah 2019-to-2021 correction is right in substance and points at the wrong
   paper. DECLINED for the Tier 2 entry, twice, on the record below.** This
   instruction has now arrived twice, once as a dispatch amendment and once as a
   coordinator research delivery saying "fix it in your table". `[live]` Crossref
   was queried twice, on separate occasions, for `10.1111/jfr3.12657`:

   ```
   issued  [[2020, 7, 28]]   print [[2020, 12]]
   online  [[2020, 7, 28]]   journal-issue [[2020, 12]]
   J Flood Risk Management, volume 13, issue 4
   ```

   **There is no 2021 in that record, in any field.** The paper is 2020. Two
   *different* Shah/Mustaffa/Martínez-Gomariz papers ARE issued-2019 / print-2021,
   a companion pair in *Int J River Basin Management* volume 19:
   `10.1080/15715124.2019.1566240` (pp. 1-23) and
   `10.1080/15715124.2019.1687487` (pp. 25-41). **The correction belongs to those
   two**, which are reviews and are not in any tier (see open item 5).
   Relabelling the Tier 2 entry 2021 would introduce an error where none existed,
   so the table stays at 2020. If a third request arrives, re-run the query before
   acting, do not act on the instruction alone.

   Related, and the coordinator is right to flag it: **Shah et al. 2018**
   (MATEC 203:07003, the force balance) is a **different paper** from Shah et al.
   2020 (`jfr3.12657`, non-stationary vehicles). This document keeps them separate
   throughout and they must never be merged.

   **Corroboration with a SEPARATE ORIGIN, which is what makes it worth having.**
   `[live]` Dispatch 6 reached the same conclusion by a different route: register
   `:307` cites the force-balance paper as **Shah, Mustaffa, KIM and Yusof 2018**.
   My own Crossref pull of `10.1051/matecconf/201820307003` returns exactly that
   author list, **Kim in place of Martínez-Gomariz**. So the paper the year
   correction names is not even the same author set, and re-dating would have
   introduced an error in **two independent places**. Per this project's
   claim-discipline rule this counts as a second source: a register line and a
   registry query have separate origins, unlike two readings of one document.

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
| 1.1 | Smith, Modra, Felder 2019, *J Flood Risk Manag* 12(S2) | `10.1111/jfr3.12527` | **Depth-resolved traction, directly measured on the whole vehicle.** Yaris 1045 kg: 4.5 to 4.7 kN at 0 m falling to **0 kN at ~0.6 m**. Nissan Patrol 2478 kg: 9.3 to 9.6 kN falling to **0 kN at ~0.95 m**. Relation `F_F = mu*(W - B - L)` | **Full scale**, prototype. C_D separately at **1:18** model scale | The traction-vs-depth curve; the buoyancy-reduced normal force; worst-case friction | Propulsion. **Three corrections, see below** |
| 1.2 | Smith, Modra, Felder 2017, *Experimental testing of flood hazard curves for a partially submerged vehicle* | no DOI located; Semantic Scholar `f9991961e7cd` | Threshold force to move a partially buoyant full-scale vehicle; C_D of a partially submerged vehicle; 1:18 companion model | **Full scale** + 1:18 | Same family as 1.1, and the earlier statement of it | As 1.1. **Not in the dispatch's list**; found `[live]` in the project's own corpus |
| 1.3 | Al-Qadami et al. 2021/2022, *Nat Hazards* 110(1):325-348 | `10.1007/s11069-021-04949-6` | Full-scale flooded passenger vehicle response, subcritical | **Full scale** | Floating depth and force response of a real car | Moving-vehicle traction. Cite year carefully: **online 2021, print 2022** |
| 1.4 | Arrighi, Alcérreca-Huerta, Oumeraci, Castelli 2015, *J Fluids Struct* 57:170-184 | `10.1016/J.JFLUIDSTRUCTS.2015.06.010` | Drag and lift contributions to incipient motion, numerically | Model | Force decomposition into drag and lift | Traction. Its **C_D 0.06 to 0.83** is for front/back-on flow and Smith 2019 states `[live]` it is "not directly comparable" |
| 1.5 | Hu, Li, Wang, Fang 2023, *J Hydrology* 620:129525 | `10.1016/j.jhydrol.2023.129525` | Stability thresholds at different flow orientations | Model | Orientation dependence | Any single-vehicle C_D. See the C_D warning in section 5 |
| 1.6 | Martínez-Gomariz, Gómez, Russo, Djordjević 2017, *Urban Water J* 14(9):930-939 | `10.1080/1573062X.2017.1301501` | Experiments-based stability threshold methodology for any vehicle | Model | A threshold method transferable across vehicles | A moving-vehicle threshold |
| 1.7 | Xia, Falconer, Xiao, Wang **2014**, *Nat Hazards* 70(2):1619-1630 | `10.1007/s11069-013-0889-2` | Vehicle stability criterion, theory plus experiment | Model | Incipient-motion criterion | **Cite as 2014.** `[live]` print and journal-issue are 2014-01, online 2013-10-11. This reproduces the standing project trap exactly |
| 1.8 | Teo, Xia, Falconer, Lin 2012, *Int J River Basin Manag* 10(2):149-160 | `10.1080/15715124.2012.674040` | Vehicle/floodplain-flow interaction | Model | Interaction forces | Full-scale thresholds |
| 1.9 | Kramer, Terheiden, Wieprecht 2016, *Int J Disaster Risk Reduct* 17:77-84 | `10.1016/J.IJDRR.2016.04.003` | Two scaled watertight models plus **one prototype car**; total-head criterion | Model **and** full scale | Total head 0.3 m passenger car, 0.6 m emergency vehicle | See the watertightness caveat in section 6 |

**Row 1.1 carries three corrections to the dispatch, from the repo's own
page-by-page PDF read** `[live]` `citations/smith_modra_felder_2019_velocity_grounding.md`:

1. **It is not "rear-axle" traction.** The prototype vehicles were "towed
   **sideways by winch** to measure traction force directly". That is a
   **whole-vehicle** measurement. The dispatch's "rear-axle" wording should not
   propagate, and the arithmetic in section 2 depends on which it is.
   **Two separate sources, not one cited twice** `[live]`: the citations file above,
   and register `:307` independently, which says Smith, Modra and Felder "measured
   it directly with a **winch and dynamometer on full-scale vehicles**". Different
   files, different authors, same conclusion.
2. **The full-scale tests were in STAGNANT water**, depth 0 to 1.0 m. The paper
   states the dynamic uplift contribution was neglected because prototype tests
   could only be run in stagnant water. **So this source measures no hydrodynamic
   force on a full-scale vehicle at all.** It anchors traction and buoyancy only.
3. **The velocity axis of the famous stability curves is CALCULATED, not measured.**
   Figures 10 and 11 come from Equation 4, a force balance combining the measured
   static traction, `C_D = 1.38` measured on a **1:18** model Yaris in a flume, and
   `mu`. Only the 1:18 model drag experiments involved real flowing water. **Do not
   cite Smith 2019 as a measured full-scale velocity threshold.**

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
this project currently validates only *statically*. And because the paper already
places three method families against the same data, an MPM result can be reported
*among* them rather than against a bare tolerance.

**Do not oversell the regime match.** `[inf]` An earlier draft called the sphere's
half submergence "close to" the canonical hull's 31.05 percent neutral-buoyancy
fraction. It is not: 0.50 against 0.3105 is **+61.0 percent relative, 19.0
percentage points**. Both are partial submergence and the *class* of problem
transfers, but the working points differ substantially and the sphere is a smooth
convex body where the hull is not. Claim the transfer at the level of physics, not
of operating point.

**The static figure this would extend, with the caveat it must carry** (warpmpm,
SDF-collider path): the project's "7.3 to 7.7 percent" is **not a one-sided band**.
`[ctx]` per CLAUDE.md A-2 the two runs are `-7.668` percent at g64 and `+7.280`
percent at g96, **opposite signs**, and register J1a records the g96 run as a
`settle_gate_met false` discard at the 900-frame cap. It also does not clear the 17
published verdicts. Quote it with the signs and that caveat or not at all.

**Name collision, flagged before it lands in the bibliography.** `[live]` These are
**two different people with the same surname**, and the project already cites the
first heavily:

| Cite | Who | Affiliation | Topic |
|---|---|---|---|
| Kramer, Terheiden, Wieprecht 2016, `10.1016/J.IJDRR.2016.04.003` | **M. Kramer**, given name not in the record | co-authors Terheiden and Wieprecht; Scite resolves the OA copy via a UNSW handle | Flood trafficability, total head 0.3 / 0.6 m |
| Kramer et al. 2021, `10.3390/en14020269` | **Morten Bech Kramer**, given name in full | **Aalborg University**, with Andersen, Thomas, Bendixen, Bingham, Read | Sphere heave decay benchmark |

`[live]` Crossref carries only the initial `M.` for the 2016 paper, so I am **not
asserting a given name for it**; an earlier draft wrote "Matthias" and that was not
in the record. The separation is established by **affiliation and co-author set**,
which share nothing, not by the given name.

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
  T_avail   = mu * F_N(h)                            LATERAL contact limit, mu only
  T_demand  = 0.5 * rho * C_D * A_D(h) * v_rel^2     hydrodynamic demand

  M(t)      = T_avail / T_demand          FORD while M > 1, NO-FORD once M <= 1
```

**`mu_RO` is deliberately NOT in `T_avail`, and this is a correction to the form
Dispatch 11 quotes.** Adversarial review found three independent reasons the
`(mu + mu_RO)` grouping is a category error, and I accept all three:

1. **It double-counts one budget.** Both terms multiply the same `F_N`. Coulomb
   `mu*F_N` is already the maximum tangential force the contact can transmit;
   rolling resistance is a component of that force, not an addition to the limit.
   `(0.3 + 0.092)/0.3 = 1.3067`, so the grouping **overstates the contact limit by
   30.7 percent** `[inf]`.
2. **The directions are orthogonal.** `mu_RO` opposes rolling, which is
   longitudinal. The demand here is **lateral**, the same direction as Smith's
   sideways winch tow. Summing orthogonal components as scalars is not valid.
3. **The regime is wrong.** At incipient lateral slide the tyre is skidding, not
   rolling, so `mu_RO` does not act in the sliding direction at all. In Shah's
   balance `F_RO` and `F_DV` are the **longitudinal pair**; keeping `mu_RO` while
   dropping `F_DV` retains half of a longitudinal balance inside a lateral one.

**Rule: keep `mu_RO` and `F_DV` together on the longitudinal side, or drop both.
Never drop one and keep the other.**

Shah 2018 writes the instability condition as
`0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV` `[ctx]`. Setting the driving force
`F_DV = 0` gives the margin above. Three reasons that is the right call, not a
compromise:

1. **Dropping `F_DV` is conservative only in isolation, and I am no longer claiming
   the equation as a whole is conservative.** An earlier draft of this document
   said it was. That was wrong and adversarial review quantified why. Within Shah's
   algebra `F_DV >= 0` sits on the resisting side, so removing it lowers M and a
   FORD verdict survives. **But the magnitudes are wildly asymmetric.** `[inf]`
   Froude-scaled to full scale (see reason 2), `F_DV <= 21 N`, whereas the
   `mu_RO*F_N` term that the quoted form *retains* is `0.092 x 10791.0 = 992.8 N`
   at zero depth. The retained anti-conservative term is **47.3x the dropped
   conservative one**, so the `(mu + mu_RO)` form is net **anti-conservative by
   about 970 N**. Removing `mu_RO`, as above, is what actually makes it safe.
   **Direction caveat that survives regardless:** if the friction circle governs,
   `sqrt(F_long² + F_lat²) <= mu*F_N`, so longitudinal drive force **consumes**
   lateral capacity and adding propulsion *reduces* lateral resistance. The
   `F_DV = 0` margin is therefore exactly right for a **coasting or towed** vehicle,
   which is what the validation literature covers, and is an **optimistic** bound
   for a driven one. Another reason arm (c) cannot be headlined.
2. **It is empirically justified, but the published number must be scaled first.**
   `F_DV` was measured at 0.0017 to 0.021 N **at 1:10 scale** `[ctx]`. Quoting that
   directly against full-scale forces is exactly the model-to-full-scale error
   section 6 warns about, and an earlier draft of this document made it. `[inf]`
   Under Froude similitude in the same fluid, forces scale as `lambda³ = 1000`, so
   the full-scale equivalent is **1.7 to 21 N**, or **0.06 to 0.68 percent of
   `mu*W`**. The conclusion survives; the argument had to be repaired.
   **A flag on the source number itself:** `[inf]` a 1:10 Perodua Viva has a scaled
   mass near 0.8 kg, so its own `mu_RO*F_N` is about 0.72 N, roughly **34x larger
   than the largest quoted `F_DV`**. A self-propelled model cannot have a drive
   force 34x below its own rolling resistance. Either 0.0017 to 0.021 N is not the
   drive force, or it is internally inconsistent with the `F_RO` term in the same
   equation. Do not lean on this number until someone reads Shah 2018 directly.
3. **It is the only version with a validation target.** Every term left in the
   equation is measured by Smith 2019 or Shah 2020. `F_DV` is the one term with no
   validation target anywhere (section 7).

Units check `[inf]`: `rho` kg/m³ × `A_D` m² × `v²` m²/s² = kg·m/s² = N; `F_N` × a
dimensionless mu = N. M is dimensionless. Consistent, and independently confirmed
in Wolfram (see below).

**The units check is necessary and not sufficient, which is the point.**
Dimensional analysis passes on both the corrected form and the defective
`(mu + mu_RO)` form, because both `mu` and `mu_RO` are dimensionless. **A units
check cannot detect the direction error above.** State this wherever the check is
cited as evidence, or it will be over-read.

**Why Shah 2018's balance needs unpacking before it is adopted.** `[inf]` It is a
single scalar equation standing in for two different force balances. For a vehicle
crossing perpendicular to the flow:

- **Along travel:** traction drives, rolling resistance and fluid resistance oppose.
- **Across travel, the flow direction:** drag pushes, tyre friction resists. **This
  is the direction the sliding verdict is about**, and it is the direction Smith
  2019 measured.

Collapsing the two into one scalar is what produces the `mu_RO` defect. Report
`M = mu*F_N / T_demand` as the headline verdict. If the `(mu + mu_RO)` variant is
reported at all, label it an **upper bound that overstates the contact limit by
30.7 percent**, and never report it alone.

### Parameter provenance, every value traced

| Symbol | Value | Source | Status |
|---|---|---|---|
| `mu` | **0.3** | **HOLD THREE STATEMENTS APART, never merge them** (register G4, G4b, verified `[live]`). **(a) As a measured wet-road value 0.3 is REFUTED.** It is Smith 2019's sand-and-gravel worst case; wet AND dry concrete both read about 0.78; model-scale runs 0.52 to 0.68. **(b) As an inherited CONVENTION it is real**: Shand et al. 2011 record road experts and test laboratories settling on 0.3, and Bonham and Hattersley 1967 and Gordon and Stone 1973 adopt it. **(c) Keller and Mitsch 1993 also assumed 0.3 but in a desk study with no physical test** (register `:257`), so it is not a third measurement | Use as a **convention**, and say so. **Do NOT write that 0.3 is the primary or best-sourced defensible value**: register G4 refutes that exact wording and the Section I table lists it for deletion on sight |
| `mu` | 0.52 measured parallel to flow | Shah 2018 `[ctx]` | Traced, not re-read |
| `mu` | **0.78, wet OR dry concrete** | `[live]` repo PDF read. **This CONFLICTS with the dispatch's "0.75 wet / 0.78 dry"**, which splits one value into two. The repo read is page-by-page from the PDF, so it wins until someone re-opens the paper | **UNRESOLVED**, do not cite either form as settled |
| `mu_RO` | 0.092 rolling | Shah 2018 `[ctx]` | Traced, not re-read. **Longitudinal only, see the equation note** |
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
  mu = 0.78 -> mu*W = 7.996 kN
  Smith 2019 measured WHOLE-VEHICLE traction at zero depth: 4.5 to 4.7 kN
  mu = 0.3 applied to full weight understates that band by 31.7% to 34.6%
```

So `mu = 0.3` is genuinely conservative against Smith's own measurement, by about a
third. **Read the percentage with its baseline attached:** 31.7 to 34.6 percent is
relative to the measured band; relative to the 3.075 kN baseline the same gap is
46.3 to 52.8 percent. Quote the baseline or the number is ambiguous.

**A correction to an earlier draft.** This document previously inferred from the
two vehicles that Smith's measurement was "axle-specific". That was a non-sequitur
and it is withdrawn. `[inf]` The decisive argument is a reductio: if 4.5 kN were a
single axle at `mu = 0.3`, that axle would carry `4500/0.3 = 15000 N = 1529 kg`,
which is **146 percent of the whole 1045 kg vehicle**. Impossible. It is a
whole-vehicle measurement, which is exactly what the repo's PDF read says.

**What the inversion actually shows, and the project already had the answer.**
`[inf]` Implied `mu` is 0.439 to 0.458 for the Yaris and 0.383 to 0.395 for the
Patrol, about 15 percent apart. An earlier draft called it a puzzle that both sit
far below Smith's own tyre figure of 0.78. **It is not a puzzle, and the resolution
was already in the register.** `[live]` Register G4b records measured
**whole-vehicle** coefficients from Shu et al. 2011, spring balance on wet carpet:

| Vehicle | Measured whole-vehicle mu |
|---|---|
| Ford Transit | **0.39** |
| Ford Focus | **0.50** |
| Volvo XC90 | **0.68** |
| *implied here, Nissan Patrol* | *0.383 to 0.395* |
| *implied here, Toyota Yaris* | *0.439 to 0.458* |

Both implied values sit **inside the measured whole-vehicle band**, and the Patrol
lands almost exactly on the Transit. So `mu ≈ 0.44` from a whole-vehicle winch tow
and `mu = 0.78` for a tyre on concrete are **two different quantities**, not a
contradiction: the first is an effective vehicle-level coefficient, the second is a
tyre-surface property. **Open item 10 is closed by this.** The lesson is the one the
skills directive makes: the answer was already paid for and sitting in G4b.

### The density "cross-check" is an identity, not a check

`[live]` `W/(rho·g·V_hull) = 10791.0/34754.3 = 0.310494`, and
`1100/3.542739 = 310.494 kg/m³`. **These agree because they are algebraically the
same statement:** `W/(rho g V) = m/(rho V) = rho_eff/rho_water`. It cannot fail for
any input, so it confirms nothing external. This is the same defect CLAUDE.md item
6 records for gate G-3 against `RHO_REF`, and it is recorded here as a restatement
rather than presented as evidence.

**Neutral buoyancy is a VOLUME fraction and is mass-specific. THREE REAL YARIS
MASSES EXIST and the register forbids silently correcting one to another**
(register **E5**, verified `[live]`: "1045 kg (Smith, Modra and Felder), 1078 kg
(NCAC), 1100 kg (MASH nominal, used here). Do not silently correct one to
another."):

| Mass | Source | rho (kg/m³) | Neutral fraction `[inf]` |
|---|---|---|---|
| 1045 kg | Smith 2019 tested vehicle, used in the traction arithmetic above | 294.97 | **29.50 %** |
| **1078 kg** | **NCAC mesh actual modelled weight** | **304.28** | **30.43 %** |
| 1100 kg | MASH class nominal, the project's canonical value | 310.494 | **31.05 %** |
| 1609 / 2337 kg | sweep masses | n/a | 45.42 % / 65.97 % |

`[ctx]` Register **E4** records that the 1100-versus-1078 difference does not change
the verdict, so this is a labelling obligation rather than a physics problem. Per
the debugging-reference skill: pick one, use it everywhere, label which. **Using
both silently in different files is the actual defect.** This document uses 1100 kg
for the hull and 1045 kg for Smith's vehicle, and says so at each use.
**Do not map any of these onto hull height.** The hull fills only 33.2 percent of its bounding box (CLAUDE.md item 4b)
and its volume is bottom-heavy, so a naive 31.05 percent of the 1.4853 m height
gives 0.4612 m, which is wrong. The project's own paper records the prism
assumption floating the vehicle at about 0.20 m against a real-vehicle 0.38 m.

Worked margin at mu = 0.3, L = 0, **at the canonical 1100 kg**. Note this table
evaluates `mu*(W-B)`, which is exactly `T_avail` in the corrected equation above:

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
  w in mm, v in km/h, R² 0.95, **flow velocity explicitly excluded**. This is
  **driver control and serviceability, not stability**, and it is the depth-only
  baseline to contrast against.

  > **ORIGINALITY CLAIM SUSPENDED PENDING A DIRECT TEST, 2026-08-14.** This document
  > previously carried, from the dispatch `[ctx]`, that a graded surface
  > `v_max(depth, flow velocity)` "does not exist in the literature and is claimable
  > as original". **Do not state that as settled and do not put it in the paper
  > yet.** A Claude research artifact on this machine,
  > `~/Downloads/compass_artifact_wf-045982be*`, is titled *"Safe Maximum Crossing
  > Speed as a Function of Flood Depth and Flow Velocity: A Literature Assessment"*
  > and assessed **exactly this question**. It is not in the corpus index and has
  > not been read by anyone in this track.
  >
  > Two outcomes, and they point opposite ways, which is why the claim cannot stand
  > in the meantime: if it found such a surface, **the originality claim is dead**
  > and must be revised before it lands. If it confirms none exists, it is
  > supporting evidence, **but only if its sources do not overlap mine**; shared
  > sources make it the same source cited twice, not independent corroboration.
  >
  > **Blocked, not skipped.** `~/Downloads` is TCC-denied to this process as of
  > 18:24 today: `ls` returns "Operation not permitted" and reads fail, while
  > `stat` gives `nlink=429` and `test -e` succeeds on known files, so **the files
  > are present and unreadable, not missing**. A glob there currently returns "no
  > matches" as a **false negative**. Access worked earlier in this same session, so
  > this is a mid-session state change. Unblock recipe is in section 9, item 13.

  **The quadratic has NO REAL ROOT, and this matters if anyone extrapolates it.**
  `[inf]` Discriminant `0.5529² - 4(0.0009)(86.9448) = -0.00730`. The vertex is at
  **w = 307.17 mm, v = 2.03 km/h**, and the curve **turns upward** after that:
  9.79 km/h at 400 mm, 35.50 km/h at 500 mm. So the function never reaches zero and
  becomes unphysical beyond about 30 cm. **The "30 cm impassable" limit is a
  truncation convention imposed in the source, not an output of the equation.**
  Say so wherever the equation is quoted, or someone will evaluate it past its
  vertex and get a speed that rises with depth. Derived independently twice here
  and both derivations agree.
- **Total head.** Kramer, Terheiden, Wieprecht 2016 `[live]`, abstract confirms
  "total heads of h_E = 0.3 m = const. and h_E = 0.6 m = const." for passenger
  cars and emergency vehicles respectively.

**Standing warning, restated because it is the easiest error to make.** The
Australian small-car limit is a limiting **still-water depth of 0.3 m**, not a
depth-times-velocity product of 0.3 m²/s. ARR Book 6 (Ball et al. 2019) uses
limiting depths 0.3 / 0.4 / 0.5 m for small car, large passenger car and large
4WD, with velocity capped at 3 m/s `[ctx]`. **That 3 m/s cap is ADMINISTRATIVE**,
set to stay below human-stability curves, not derived from vehicle data
(CLAUDE.md L-2). Never present it as a vehicle-derived limit. Never conflate a depth cap with a
hazard product.

---

## 3. The lineage the dispatch omits, and what it does to the novelty claim

`[live]` from `docs/Dynamic_Vehicle_Traction_in_Floodwater.md`, 43 papers, 98
percent coverage, 2026-07-21, already on this disk:

| Source | DOI | Why it matters |
|---|---|---|
| Wasfy, Wasfy, Peters 2015 | `10.1115/DETC2015-47142` | MBD **plus SPH** in one solver for **vehicle water fording**. Models suspension, wheels, steering, axles, differential and **engine**. Humvee-type vehicle through a shallow pool |
| Pazouki et al. 2014 | Semantic Scholar `2a3a1ddc` | Compares four fluid-solid coupling methods, "motivated by the desire to investigate vehicle fording scenarios" |
| Pazouki, Jayakumar, Negrut 2016 | Semantic Scholar `61da26b6` | *Investigation of the Vehicle Mobility in Fording*. Two-way coupled SPH/MBS; **point-cloud discretisation of the solid** gives accurate coupling forces. This is the architecture CLAUDE.md A-1 already cites as the correct alternative to velocity averaging. **Engine tag:** the velocity-averaging path being criticised is **warpmpm's material-8 free-rigid** path used by the 17 canonical runs, not the warpmpm SDF-collider path and not Genesis |
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

**The two papers, with DOIs and the vehicle named**, because the register carries a
guard against exactly this paper's vehicle being misattributed to a Yaris (register
G5, and `.claude/hooks/banned_phrase_guard.py`). **The test vehicle is a Perodua
Viva, not a Yaris**, which matters in a document whose section 2 is entirely about
a Yaris hull.

| Paper | DOI `[live]` | Framing | Float depth | Slide d×v |
|---|---|---|---|---|
| Al-Qadami et al. **2022** | `10.1111/jfr3.12828` | full-scale car **moving perpendicular** to flow, numerical | 0.38 m | 0.39 m²/s |
| Al-Qadami et al. **2023** | `10.3390/su151713262` | vehicle **exposed, stationary**, 3D CFD | 0.38 m | 0.36 m²/s |

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
   2017's Equation 12, which gives **0.47 m²/s**, and states the gap as
   **25 percent**.
   **Quote that 25 as the paper's own claim, not as a derived value.** `[inf]` It
   does not reproduce from 0.47 and 0.36 by any standard convention: relative to
   0.47 it is 23.40 percent, relative to 0.36 it is 30.56 percent, and as a
   symmetric percentage difference about the mean it is 26.51 percent. None is 25.
   Consequently the "three times larger" comparison is a **range, not a number**:
   against the 8.33 percent spread it is **2.81x to 3.67x** depending on which
   convention is used. The qualitative point stands and is the one that matters:
   **the theory-versus-model gap is roughly three times the moving-versus-stationary
   gap**, so the latter cannot be attributed to physics before the former is
   explained.

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

| C_D | Source | Scale | Conditions |
|---|---|---|---|
| 1.1 to 1.15 | Keller and Mitsch **1993**; Shu et al. 2011 `[live]` via Smith 2019 | n/a | **Assumed**, cylinder/rectangle analogy. Register `:257` records Keller and Mitsch as a **desk study with no physical test at all** |
| **0.06 to 0.83** | Arrighi et al. 2015 `[live]` | numerical | Front/back-on flow. Smith 2019 states these "are not directly comparable" |
| **1.38 average** | Smith, Modra, Felder 2019 `[live]` | **1:18 model** | Measured in a flume; feeds their Equation 4 stability curves |
| ~1.7 | Hoerner 1965 flat plate `[live]` via Smith 2019 | reference | Submerged flat-plate analogy |
| **1.22 to 6.82** | Hu et al. 2023 `[ctx]` | model | A **joint envelope** over three vehicles and all flow orientations |

`[inf]` The published values span 0.06 to 6.82, a factor of **113.7**, which is
**2.06 orders of magnitude**. `T_demand` is *linear* in C_D, so M varies as
**1/C_D**: raising C_D **lowers** the margin. An earlier draft said C_D "can move
M by that same factor" without stating the direction, which is right in magnitude
and reads as if the relation were direct. It is inverse.

**Honesty about that span, since it commits the error the next bullet forbids.**
`[inf]` 0.06 is the bottom of a range this document itself flags as "not directly
comparable", and 6.82 is the top of a joint envelope over three vehicles and all
orientations. So **113.7x is an upper bound on the disagreement, not a measurement
of it.** The defensible statement is narrower and still decisive: even restricting
to values offered for a passenger car in cross-flow, C_D ranges from about 1.1 to
1.38 to the Hu envelope, which is a factor of several, and the verdict is linear
in it.

**A second multiplier on `T_demand` that the margin as written omits.** `[live]`
Register **G6**: **unsteady flow raises drag 40 to 50 percent** relative to steady
at matched conditions, varying approximately linearly with flow acceleration
(Azhar et al. 2026, `10.1111/jfr3.70181`, which G6 calls "best-sourced of that
batch, safe to cite directly"; the steady baseline is Azhar et al. 2023,
`10.1111/jfr3.12885`). `[inf]` `T_demand` in section 2 uses a **steady** drag, so
in unsteady flow the true demand is up to **1.5x** the value computed, and the
margin M correspondingly up to **1/1.5 = 0.67x**. That is the same order as the
C_D uncertainty and it is a systematic bias in the unsafe direction, not scatter.
**Either apply the factor explicitly or state that the margin is a steady-flow
figure.** Do not leave it implicit.

**Consequences for the fork, both mandatory:**

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
  points before solidifying `[ctx]` (**engine: warpmpm**, project-owned scene code,
  not the vendored solver), so watertightness does not propagate into the
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

**Chrono does not change this, and the detail sharpens the claim.** `[ctx]` Chrono
ships a vehicle water-fording demo (SBEL, roughly 1.4 to 1.5 million SPH markers,
Mazhar et al., SBEL TR-2016-01). It is a **physics demonstration and visualisation,
not a benchmark validated against experimental fording data.** Chrono's rigorously
validated off-road work is soil terramechanics (CRM and SCM), against single-wheel
experiments and DEM ground truth. So the one engine that can natively drive an
actuated vehicle through water still has **no validated fording result**, and
adopting Chrono would inherit a validated *soil* result and a demo-level fluid one.

**Do not cite any NG-NRMM fording error-reduction percentage.** `[ctx]` It was
searched for and none exists; none should be stated as fact.

**Chrono has NO cubic-domain constraint, and this is now MEASURED on our own
hardware rather than argued from documentation.** `[ctx]` Dispatch 13, GH200:
holding fluid volume and particle spacing fixed and varying only aspect ratio
**1.0 to 24 to 1024**, fluid markers rose only **1.67x**, where warpmpm's forced
cubic grid would cost roughly **1024x** for the same shape change. Every case
initialised **and** stepped, so this is not a configuration-only result.

**But the cost moves to the boundary, and that is the honest half.** BCE (boundary)
markers grew **8.5x** across the same sweep.

> ### RETRACTED, 2026-08-14, same day it was written
>
> An earlier version of this section stated the boundary cost as
> **`BCE/fluid = 3*spacing/depth`**, described as fitted and confirmed against an
> independent case (predicted 1.000 against measured 0.926, and 0.375 against
> 0.374). **That formula is WITHDRAWN.**
>
> **Where it entered, since a future reader should be able to see the path:** it
> reached this document through a **coordinator relay of a Dispatch 13 result**,
> already labelled confirmed. Dispatch 13 subsequently caught its own error and the
> coordinator relayed the retraction. I did not derive it and did not test it before
> writing it down, which is the failure worth recording: **a relayed number arrived
> carrying the word "confirmed" and I passed it through on that word.**
>
> **Why it was wrong:** both agreeing cases were **shallow**, so they exercised only
> the limit where the formula happens to hold. Across the full aspect sweep it fails
> badly, worst by **6.32x**.

**The general law is surface-area-to-volume**, and unlike the withdrawn form it is
**derivable rather than fitted**, which is why it should be trusted further:

```
  BCE markers    ~  3 layers * A / s^2        three layers over the WETTED AREA
  fluid markers  ~  V / s^3                   fluid filling the VOLUME

  BCE / fluid    ~  3 * s * A / V             dimensionless. OK
```

`[inf]` I checked this against Dispatch 13's own sweep rather than accepting it:

| case | depth | measured | `3sA/V` | err | `3s/depth` | err |
|---|---|---|---|---|---|---|
| cube-like | 2.289 | 0.828 | 0.655 | -20.9% | 0.131 | **-84.2%** |
| wide | 1.145 | 0.864 | 0.655 | -24.2% | 0.262 | -69.7% |
| channel | 0.500 | 1.199 | 0.950 | -20.8% | 0.600 | -50.0% |
| long channel | 0.250 | 1.752 | 1.619 | -7.6% | 1.200 | -31.5% |
| extreme | 0.125 | 4.198 | 3.205 | -23.7% | 2.400 | -42.8% |
| road | 0.300 | 0.926 | 1.070 | +15.6% | 1.000 | +8.0% |

`[inf]` **A/V: max error 24.2 percent, mean 18.8 percent. `3s/depth`: max 84.2
percent, mean 47.7 percent.** Two further checks that raise my confidence in the
replacement beyond "someone told me":

- **The shallow limit falls out of the derivation.** When the wetted area is
  floor-dominated, `A/V -> 1/depth`, and `3sA/V -> 3s/depth` exactly. So the
  withdrawn formula is a **special case** of the general one, not a rival to it.
  That explains precisely why the two shallow cases agreed.
- **The A/V residual has a coherent sign.** It reads low in 5 of 6 cases, which is
  what domain pad and double-counted edges would do: they add markers the idealised
  count omits. A fit that was merely lucky would not show a consistent sign.

**If `3s/depth` is quoted at all, it must carry its shallow-limit condition.**

**What does NOT change.** The domain-shape result stands and was **measured
directly, not fitted**: 1.67x fluid-marker growth across a 1024x aspect change,
every case initialised and stepped. `[inf]` So the statement for this fork is
unchanged in direction: **Chrono buys domain SHAPE freedom and pays for it at the
boundary**, scaling with **wetted area over volume** rather than inversely with
depth. It relieves the constraint that makes a long shallow channel impossible in
warpmpm, and **it still buys no validation.** Both halves must travel together.

**How to phrase the resulting claim, precisely.** The tempting sentence is "no
validated vehicle-fording chain exists in any engine." `[inf]` **That is one word
too strong**, because He 2026 does validate a coupled vehicle-water model against
free-running experiments (section 3). The defensible form keeps the distinction
this document has maintained throughout:

> No engine, open-source or commercial, has a fording **verdict** validated against
> experimental fording data. What has been validated is *transient response*
> (He 2026, model scale, CFD/MBD). Chrono's fording capability is demo-level, and
> no MPM equivalent of either exists.

**Actuated-body prior art, and one correction to how it is usually summarised.**
`[ctx]` The actuated-body work outside flood studies is delta-plus-SPH
self-propelled swimmers, **DiffFR** (`[live]` Li, Xu, Ye, Ren, Liu, *DiffFR:
Differentiable SPH-Based Fluid-Rigid Coupling for Rigid Body Control*, ACM TOG
42, **2023**, DOI `10.1145/3618318`, Crossref-confirmed; note **2023**, not 2024),
and Chrono's wheeled vehicles. The usual summary is that coupling an actuated
**ground vehicle with a drivetrain** to a fluid is essentially unique to Chrono.

`[inf]` **That holds for engines you could adopt, but not for the published
literature**, and section 3 of this document is the counter-evidence: Tison 2021
couples 6-DOF to VOF in STAR-CCM+ **with drivetrain power distribution to the
wheels**; Liu, Xu and Pan 2023 model self-propelled river crossing; Wasfy 2015
carries an engine and differential in an MBD model coupled to SPH. All three are
commercial or in-house stacks rather than adoptable open-source ones. State it as
"unique among available open-source engines", not "unique in the literature".

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
`10.3970/CMES.2008.031.107` returns HTTP 404 from the Crossref API. It resolves
through doi.org to `techscience.com/CMES/v31n2/25168`, which I fetched and which
serves *Examination and Analysis of Implementation Choices within the Material
Point Method (MPM)* by M. Steffen, P.C. Wallstedt, J.E. Guilkey, R.M. Kirby and
M. Berzins, University of Utah, CMES 31(2). All five authors match.
**Tech Science Press DOIs are not indexed in Crossref; a Crossref miss is not
evidence of a bad DOI.** Do not let an automated bibliography audit drop it.
*Robustness note:* an independent check from another process got a transport error
rather than the redirect, so cite the **techscience.com landing page** as the
durable evidence rather than the doi.org hop.

**THERE ARE TWO STEFFEN 2008 PAPERS AND THE PROJECT CITES BOTH AS "Steffen 2008".**
`[live]` This is a live hazard and it is not recorded anywhere yet:

| Paper | DOI | Authors | Used for |
|---|---|---|---|
| *Examination and Analysis of Implementation Choices within the MPM*, CMES 31(2) | `10.3970/CMES.2008.031.107` | Steffen; **Wallstedt; Guilkey**; Kirby; Berzins (5) | Cited by Dispatches 1 and 10 |
| *Analysis and reduction of quadrature errors in the material point method (MPM)*, IJNME 76:922-948 | `10.1002/nme.2360` | Steffen; Kirby; Berzins (**3**) | Matches CLAUDE.md **L-5** |

`[inf]` **CLAUDE.md L-5 names "Steffen, Kirby and Berzins", three authors, which is
the IJNME quadrature paper, not the five-author CMES paper the dispatches cite.**
Both are 2008, both are about MPM accuracy, and they are being used
interchangeably for the same convergence-loss claim. Either could be the right
citation for it, but they are not the same paper and a reader cannot currently tell
which was intended.
**Request to the owning dispatch:** CLAUDE.md and
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` are **Dispatch 4's** files, so
I have not edited them. Dispatch 4 should decide which Steffen 2008 supports L-5
and disambiguate both citations by DOI.

**A framing that must NOT enter this document, checked for and absent.** `[live]`
An independent FOSS engine assessment states that `kks32/mpm-engine` "appears not
to exist" and treats this project's engine as **CB-Geo mpm** with no rigid-fluid
coupling at all. That is false for our stack: the vendored core at
`third_party/mpm-engine-544c93dd-solver-core/` is 11 Python files and zero C++,
imports `warp`, and `VENDORED.md` records the pinned SHA `544c93dd` with every file
sha256-compared. The SDF collider API is present at that SHA, and per RB-3 the
**SDF path has always had a force accumulator** (`param.force`/`param.torque`, read
via `sdf_wrench()`), unlike the material-8 free-rigid path. I grepped this document
for `CB-Geo`: **zero hits**, so the framing has not entered. Keep it out.

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
7. **TWO Steffen 2008 papers are cited interchangeably** (section 8). CLAUDE.md
   L-5's three-author form matches `10.1002/nme.2360`; Dispatches 1 and 10 cite the
   five-author `10.3970/CMES.2008.031.107`. **Owner: Dispatch 4**, since CLAUDE.md
   and the register are its files. I have not edited either.
8. **`mu` = 0.78 wet-or-dry, or 0.75 wet / 0.78 dry?** The repo's page-by-page PDF
   read and the dispatch disagree. Resolve by reopening the Smith 2019 PDF. Until
   then neither form is citable as settled.
9. **Shah 2018's `F_DV` may be internally inconsistent** with the `F_RO` term in its
   own equation (section 2, reason 2): at 1:10 scale the quoted drive force is about
   34x smaller than the model's own rolling resistance. Someone should read the
   paper directly before the number is used again.
10. **CLOSED by register G4b.** The "why does whole-vehicle traction imply
    `mu ≈ 0.44` when the tyre measures 0.78" question is answered: Shu et al. 2011
    measured whole-vehicle coefficients of 0.39, 0.50 and 0.68, and both implied
    values sit inside that band. Vehicle-level and tyre-level `mu` are different
    quantities. Found by loading the `flood-mpm-debugging-reference` skill, which
    is the point of the skills directive: this had already been paid for.
11. **The margin is a STEADY-flow figure** (section 5). Register G6 gives a 40 to
    50 percent unsteady drag increase, so M is up to 0.67x the computed value in
    unsteady flow. Decide whether the fork applies the factor or labels the
    limitation, but do not leave it implicit.
12. **A process note, not a citation item: two relayed results reached this document
    labelled "confirmed" and neither survived checking.** The Shah 2019-to-2021 year
    correction (headline 2, refused twice) and the `3s/depth` boundary-cost formula
    (section 7, retracted the same day). Both arrived through a coordinator relay
    rather than from the originating dispatch, and in the second case I wrote it
    down **without deriving or testing it**, on the strength of that label. The
    generalisable rule, which this project already states for documents and should
    state for relays too: **a relayed number is a claim, not a verification**, and
    "confirmed" in a relay records someone else's confidence, not a check I have
    done. Re-derive or test before writing it down. Both corrections are recorded
    in place rather than silently patched so the entry path stays visible.

13. **THREE UNREAD ARTIFACTS BEAR DIRECTLY ON THIS TABLE, and one of them tests a
    claim this document makes.** All three are in `~/Downloads`, none is in the
    corpus index, and **`~/Downloads` is TCC-denied to this process** (see the
    suspended-claim box in section 2). Desktop reads fine, so the block is
    Downloads-specific, and no readable copy of any of the three exists elsewhere
    (`find` over `~/Desktop` and the repo: none).

    | Artifact | Bears on | Priority |
    |---|---|---|
    | `compass_artifact_wf-045982be*` *Safe Maximum Crossing Speed as a Function of Flood Depth and Flow Velocity* | **Directly tests the suspended originality claim.** Also check source overlap: shared sources are not independent support | **FIRST** |
    | `compass_artifact_wf-baa355db*` *Experimental Configuration of the Flood-Vehicle Stability Literature: What Was Physically Done* | The model-versus-full-scale tagging in section 1, which the dispatch calls the latent variable. This is the primary evidence for those tags | second |
    | `compass_artifact_wf-266e9a8a*` *Incipient-Velocity Equations: Xia et al. (2011) vs Shu et al. (2011)* | Tier 1 currently has Xia 2014 but not the 2011 pair. Read alongside memory `xia-2014-not-2013-citation-trap.md`, since this author group carries a live year trap | third |

    **Cheapest unblock, and it also closes the corpus-indexing gap:**
    ```
    cp ~/Downloads/compass_artifact_wf-045982be* \
       ~/Downloads/compass_artifact_wf-baa355db* \
       ~/Downloads/compass_artifact_wf-266e9a8a* \
       ~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/
    ```
    Alternatively grant the terminal Files-and-Folders or Full Disk Access for
    Downloads in System Settings > Privacy & Security, then relaunch. Note a `!`
    prefixed command in this session runs in the same process tree and will likely
    inherit the same denial, so the copy is the more reliable route.

14. **Smith, Modra, Felder 2019 full text may be on disk** at
    `~/Downloads/can-it-ford/citations/Smith-Modra-Felder/`. Tier 1 row 1.1 is
    currently ranked from the DOI plus the repo's page-by-page notes. **Dispatch 8
    is establishing that directory's contents**; do not duplicate that work, but
    read the full text the moment D8 reports. Same TCC block applies.


---

## Reproducibility

The DOI audit is a script, not a transcript:
**`docs/fork_validation_verify_dois.py`**, committed alongside this document on
branch `claude/fork-validation` in commit **`b7b8a1b`** (an earlier draft of this
document cited a `scratchpad/` path that does not exist in the repo; that is fixed),
queries
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
