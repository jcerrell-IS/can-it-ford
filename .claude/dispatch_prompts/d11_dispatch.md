### DISPATCH 11, Mac, validation and the verdict for a moving vehicle

```
SCOPE DECLARATION
MACHINE: Mac, no GPU.
BRANCH: new, claude/fork-validation-<slug>, off main.
MAY WRITE TO: that branch, docs/ only.
NEVER TOUCH: main; the register (Dispatch 4 owns it); any driver or scene branch;
  the canonical stores.

THE SITUATION, ALREADY ESTABLISHED BY A 44-PAPER SEARCH AT 92% COVERAGE
No validated vehicle-fording MPM chain exists. And, importantly, the search did NOT
establish an experimental basis for the US Army FM 90-13 1.5 m/s fording rule. Treat
that rule as doctrinal until proven otherwise; do not adopt it as a validation target
on its face. Field manuals are not scholarly literature and a deep search will not
resolve them; sweep them separately as primary documents via DTIC and the Army
Publishing Directorate if you want to settle the provenance.

THE VALIDATION TARGETS THAT DO EXIST, RANKED. These are the deliverable.
TIER 1, measured vehicle experiments, the strongest anchors:
  Smith, Modra, Felder 2019, DOI 10.1111/jfr3.12527. Full-scale stability curves.
    Yaris 1045 kg: rear-axle traction 4.5-4.7 kN at 0 m falling to 0 kN at ~0.6 m.
    Nissan Patrol 2478 kg: 9.3-9.6 kN falling to 0 kN at ~0.95 m. F_F = mu*(W-B-L).
    Measured tyre mu 0.75 wet / 0.78 dry; 0.3 adopted conservatively for the curves.
    THIS IS A STATIONARY SIDEWAYS WINCH PULL-TEST. It bounds available traction; it
    does not validate propulsion. Say so every time you cite it.
  Al-Qadami 2021 full-scale flooded passenger vehicle, DOI 10.1007/s11069-021-04949-6
  Arrighi 2015 drag and lift in incipient motion, DOI 10.1016/J.JFLUIDSTRUCTS.2015.06.010
  Xia, Falconer, Xiao, Wang 2013, DOI 10.1007/s11069-013-0889-2
  Hu, Li, Wang, Fang 2023 partially submerged at different flow orientations,
    DOI 10.1016/j.jhydrol.2023.129525
  Martinez-Gomariz, Gomez, Russo, Djordjevic 2017, DOI 10.1080/1573062X.2017.1301501
  Teo, Xia, Falconer, Lin 2012, DOI 10.1080/15715124.2012.674040
TIER 2, MOVING-vehicle sources, which is our case:
  Shah, Mustaffa, Martinez-Gomariz, Yusof 2020, hydrodynamic effect on NON-STATIONARY
    vehicles at varying Froude numbers on flat roadways, DOI 10.1111/jfr3.12657, R2=0.85
  Al-Qadami 2022, vehicle MOVING perpendicular to flow, DOI 10.1111/jfr3.12828,
    critical depth 0.38 m, minimum depth x velocity 0.39 m2/s
  He et al. 2026, "Predicting Vehicle-Water Interaction in Shallow Water: Simulations
    and Experimental Validation", J. Computational and Nonlinear Dynamics,
    DOI 10.1115/1.4071177. Ranked the single closest match. READ THIS FIRST.
TIER 3, method comparison:
  Zheng Xin and Su Donghai 2021, rotating-wheel VOF/RANS against road tests,
    DOI 10.1177/0954407020942005
TIER 4, canonical transferable hydrodynamics with public reference data:
  accelerating-plate drag and free-surface effects; near-surface added mass and
  damping; dam-break obstacle pressures with openly supplied measurements and video;
  planing-hull force data; baffled-tank loads with grid-refinement evidence. One
  benchmark in this set has approximately 0.3 percent experimental uncertainty, which
  is an unusually precise public target. Identify it and use it.
EXPLICITLY EXCLUDED AS A STANDARD: SPH work is admitted ONLY as a pointer to
experimental datasets, where the dataset is the asset. Do NOT take error bands,
resolution guidance or boundary treatment from SPH. Its tolerance norms are loose for
reasons specific to SPH, and importing them would import a weaker standard. One SPH
entry in the search is flagged dataset-only for exactly this reason.

THE CONTRADICTION YOU MUST NOT AVERAGE
Al-Qadami 2022 (moving, perpendicular) gives 0.38 m and 0.39 m2/s. Al-Qadami 2023
(exposed, stationary) gives 0.38 m and 0.36 m2/s. Same group, 8 percent spread,
across exactly the moving-versus-stationary distinction this track studies. Report
both with their framings attached. Resolving which applies to a driven vehicle is a
genuine contribution.

THE VERDICT QUESTION, WHICH IS THE REAL DELIVERABLE
The AR&R and Shand thresholds describe a STATIONARY vehicle in flow, so they remove
the degree of freedom a driven vehicle has. A moving-vehicle verdict needs a different
quantity. The candidates, with what exists behind each:
  TRACTION MARGIN. F_F = mu*(W - B - L), measured depth-resolved by Smith 2019, and
    embedded in a moving balance by Shah 2018 (10.1051/matecconf/201820307003):
    0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV. Best supported. Recommend this.
  SPEED CEILING. Pregnolato 2017 (10.1016/j.trd.2017.06.020),
    v(w) = 0.0009*w^2 - 0.5529*w + 86.9448, w in mm, v in km/h, R2 0.95, DEPTH ONLY,
    flow velocity excluded, 30 cm impassable. This is the depth-only baseline to
    contrast against, and it is driver-control and serviceability, not stability.
    A graded speed surface v_max(depth, flow velocity) does not exist in the
    literature and is claimable as original.
  TOTAL HEAD. Kramer, Terheiden, Wieprecht 2016 (10.1016/J.IJDRR.2016.04.003):
    0.3 m for passenger cars, 0.6 m for emergency vehicles.
STANDING WARNING: the Australian small-car limit is a limiting STILL-WATER DEPTH of
0.3 m, NOT a D x V product of 0.3 m2/s. ARR Book 6 (Ball et al. 2019) uses limiting
depths 0.3 / 0.4 / 0.5 m for small car / large passenger / large 4WD with velocity
capped at 3 m/s. Never conflate a depth cap with a hazard product.

SCALE EFFECTS, THE LATENT VARIABLE
Most of Tier 1 is model scale. Froude scaling preserves the gravity-to-inertia ratio
but NOT friction or viscous ratios, and the verdict depends on a friction coefficient.
Tag every target model-scale or full-scale and state the scaling assumed. Note also
that model-scale watertight vehicles are documented to float too shallow.

DEFINITION OF DONE
docs/FORK_VALIDATION_TARGETS_<date>.md containing: the ranked target table with DOI,
what is measured, model or full scale, and what it can and cannot validate; an
explicit recommendation of the traction-margin verdict with its equation and
parameter provenance; the Al-Qadami contradiction stated unresolved; and a plain
statement that self-propulsion has no validation target anywhere in the literature.
Every DOI checked with Scholar Sidekick auditBibliography and Scite before it lands.
```

OPERATING PROTOCOL, applies to you in full:

```
OPERATING PROTOCOL:

Before starting: check git log, .remember/ files, and the research
citations you were given, in that order. Do not duplicate work already
done elsewhere in this bundle.

When you hit an obstacle: try a fix. If it doesn't work, try a second,
genuinely different approach, not a variation of the same one. Before
concluding you're stuck, check whether an available connector or subagent
resolves it:
  - DeepWiki, for any question about how a library/repo actually behaves.
    Treat its answer as a hypothesis to verify against source, not fact.
  - The physics-skeptic subagent, before finalizing any claim involving a
    percentage, force, verdict count, or distance. If it's unavailable this
    session, say so explicitly and mark the claim unreviewed, do not fake
    the review.
  - Wolfram, for any physical parameter, unit conversion, or equation
    before it becomes a stated claim.
  - Scite, for any citation, DOI, or threshold before it's written as
    settled.
  - register_integrity.py (or the project's equivalent), before any commit.

Prefer proceeding on a clearly-labeled, reversible assumption over
stopping. State the assumption explicitly, in the commit message or the
write-up, so it can be revisited later without re-deriving it from
scratch.

Tag every factual claim by its source: read directly, recalled from
context, or inferred. Tag every solver/engine claim by which engine it
applies to. Never state a number from memory when you could check it live.

Keep working on everything else in your scope even if one specific thing
below is blocked, do not let one blocker stop the whole session.

Flag, rather than silently proceed past, only these four things:
1. You are about to discard, overwrite, or force-push over uncommitted
   work you did not create and cannot verify is safe to lose.
2. You've found two independently-reported results that genuinely
   disagree about the same physical quantity, not just different framing
   of the same thing, and resolving which is correct requires a judgment
   call, not just more data you can go get yourself.
3. You are about to edit a canonical file outside your declared scope.
4. A genuine hard-stop case: real financial cost, an exposed credential,
   a destructive/irreversible action, or anything matching the project's
   existing standing hard rules.

When you flag one of these: write it clearly to a named file (not just an
inline comment), keep working on everything else in your scope that isn't
blocked by it, and do not treat the flag as ending the session.

Write with an engineer/scientist's discipline throughout: state
assumptions before acting on them, prefer a falsifiable test over a
plausible-sounding claim (a no-forcing control, a held-fixed comparison,
a second seed), and write up a result the same way whether it confirms or
overturns something already published.

Before any push: confirm the target branch, stage explicit paths only,
never a blanket add, and confirm the push actually landed afterward,
don't just assume the command succeeding means the remote updated.
```
