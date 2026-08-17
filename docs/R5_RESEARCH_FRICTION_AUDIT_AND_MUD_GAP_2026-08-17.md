# R5-D1 unit 30: the friction audit nobody opened, and a novelty axis the project already has work on

Date 2026-08-17. Branch `claude/r5-research`.

Unit 29 flagged `Ground-Material Friction and Road-Camber Physics for
Flood-Traversability Simulation: A Provenance-Grade Literature Audit` as the
highest-value never-opened corpus document, because friction is the parameter
this dispatch has worked hardest. I read it, and per unit 27's lesson I checked
the register **before** treating anything in it as new.

**Most of its friction content is already in the register. Its mud finding is
not, and it points at a novelty axis where the project has already done work.**

---

## 1. Already known: check first, as K0 says

| audit finding | register / CLAUDE.md status |
|---|---|
| mu = 0.3 traces to Bonham and Hattersley 1967 | **known**, 2 register hits |
| mu_dry = 0.68 (Martinez-Gomariz 2017, Shu 2011) | **known**, 3 register hits, 1 in CLAUDE.md |
| Smith, Modra and Felder 2019 measured across bed materials | **known**, and it is one of only 3 DOIs actually cited in the paper |
| the scene has no camber | **known**, register **F1**: "No road, camber, channel or terrain" |

So the friction half of this audit largely confirms what the project holds. I am
not restating it as a discovery.

Two details worth carrying anyway, both quotable:

- The audit gives the **verbatim rationale** for 0.3, via Hu et al. 2024: "After
  consulting with various test laboratories and road experts, Bonham and
  Hattersley (1967) choose a friction coefficient of 0.3, which is satisfactory
  for several surface types and is considered likely to be conservative."
- It gives the **field's two-value convention and spread**: mu_wet approximately
  0.3, mu_dry approximately 0.68, with a published cross-study range of
  **0.25 to 0.75** (Xiong et al. 2024, `10.1029/2023WR036739`, which is in our
  paper bibliography).

**A discrepancy to resolve, flagged not settled.** Project memory records that
Bonham and Hattersley "derived 0.3 from a braking coefficient of 0.5 reduced 10%
sideways, 20% slip, 20% debris". This audit says they "choose" 0.3 after
consulting laboratories and road experts. These are not necessarily in conflict,
a consultation could have produced the 0.5-and-reductions route, but they are
different levels of specificity about the same number and only one can be quoted
as the origin. Both are secondary; the primary is Bonham and Hattersley 1967,
which neither I nor the audit has read.

**Where our 0.55 sits.** The field convention is 0.3 wet and 0.68 dry. Our
`floor_friction = 0.55` is between them, inside the 0.25 to 0.75 range but at
neither convention. Unit 1 found Azhar 2023 reports 0.55 *measured*, and D4
records 0.55 as 1.83x AR&R's assumed 0.30. So 0.55 is defensible and sourced, but
it is **not** the flood-literature wet-bed convention, and a paper that says
"we use 0.55" without that context invites the question.

## 2. NOT known: the viscoplastic mud gap, and we have work on it

Checked live, both canonical files:

```
term            register   CLAUDE.md   repo-wide (excl .claude)
Bingham            0           0            15
Herschel           0           0             9
viscoplastic       0           0             1
```

**Neither canonical file mentions Bingham, Herschel-Bulkley or viscoplastic
rheology at all**, yet the repo contains:

- `analysis/bingham_cfl_crossover.py`
- `renders/yaris_render_s3_enhanced/sim_enhanced.py`
- a dedicated branch `claude/bingham-material-sweep-2026-08-07`, present on
  **origin** as well as locally

So the project has done Bingham material work and neither authority records it.

What the audit adds is the reason that work might matter. Its verdict, verbatim:

> **No published model couples a genuine yield-stress mud rheology to
> *wheel/tire* dynamics, and no flood-vehicle model uses a viscoplastic bed
> rather than a rigid bed with Coulomb friction.**

and its recommendation:

> Since no wheel/tire + yield-stress-mud coupling exists, "Can It Ford" adding a
> Bingham/Herschel-Bulkley (or mu(I)) mud bed to a coupled MPM fluid/rigid-body
> vehicle model would be **a genuine research novelty, not a replication**.

**Why this matters given everything else I have found.** Units 7, 16, 25 and 27
progressively closed the novelty axes: He 2026 and Azhar 2023 occupy validation,
Al-Qadami 2023 occupies full scale and stability thresholds, Azhar 2023 occupies
the particle method, and register G12 already establishes the pipeline shape as
prior art. Against that, a **documented orphan area on which the project already
has committed code and a pushed branch** is worth surfacing.

I am **not** claiming this is the novelty. Three reasons for caution, two of them
the audit's own:

1. The audit calls this "a bounded negative result from an extensive but finite
   search", to be logged as ORPHAN rather than proven-nonexistent.
2. Its strongest counter-example, Bertani et al. 2025 tracked-vehicle
   Herschel-Bulkley CFD, is "a lower-tier open-access journal ... rigid track at
   uniform velocity", so the gap is narrower than a clean absence.
3. Our vehicle has **no wheels at all**. It is a rigid particle cloud with a
   single `floor_friction` scalar, per D4's `cf9e85c`. A "wheel/tire plus mud"
   novelty claim does not obviously transfer to a wheel-less hull, and whether it
   does is a physics judgement, not mine.

The actionable form is narrow: **the register records neither the Bingham work
nor the literature gap that would make it interesting.** Both belong there, and
whoever owns the register should decide how to frame them.

## 3. Camber: a scene limitation the register has, and a field gap it does not

Register **F1** already records that our scene has "no road, camber, channel or
terrain". The audit adds the other half: camber-in-D-times-V is **also**
unaddressed in the literature. Its verdict is that camber is well established as
a civil drainage variable, that it demonstrably changes inundation depth across
lanes, and that **no located study folds transverse camber into a depth-velocity
hazard product or a vehicle-stability threshold**. Longitudinal slope, by
contrast, is in the flood-vehicle literature: Xia et al. 2014 reports incipient
velocity about 25% lower on a 1:50 slope, which is Elicit row 26 in my own
threshold table.

So F1's framing is "our scene lacks this". The audit's framing is "the field
lacks this too". Those are different statements and the second is not recorded.

## 4. Status

UNVERIFIED:
1. **I have not read Bonham and Hattersley 1967**, and neither had the audit; both
   accounts of the 0.3 origin are secondary.
2. The audit's own caveat applies to its two negatives: bounded search, not proven
   absence, and several numerics confirmed via abstracts rather than paywalled
   full texts.
3. I did not open `analysis/bingham_cfl_crossover.py` or the
   `bingham-material-sweep` branch. I established that they exist and that the
   canonical files do not mention them; I have not assessed what they contain or
   whether the sweep produced anything.
4. Whether a wheel-and-mud novelty argument transfers to a wheel-less rigid
   particle cloud is a physics question for D4.
5. This is one of 92 corpus prose documents carrying DOIs. The second one unit 29
   flagged, on GNN surrogates and NCAC/CCSA geometry, is still unread.
