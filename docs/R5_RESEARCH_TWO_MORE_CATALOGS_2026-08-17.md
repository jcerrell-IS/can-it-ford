# R5-D1 unit 15: the two most on-topic catalogs, which I had walked past

Date 2026-08-17. Branch `claude/r5-research`.

I extracted DOIs from all 14 catalogs in unit 1 but read the *content* of only
two, the ones my dispatch named. The single most on-topic catalog title in the
whole set, **"Validated MPM Vehicle Water Coupling"** (60 papers), I never
opened. Neither did I open **"Quantitative MPM Wall Penetration"** (16 papers),
which bears on a gate seven of our runs fail.

Both are at
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/01_Solver_Physics_and_Coupling/`.
Everything quoted below is READ DIRECTLY from their `## Summary of Results`
blocks.

---

## 1. The coupling catalog names this project's exact practice as not defensible

Its opening sentence, verbatim:

> A defensible FORD / NO-FORD result requires class-specific geometry and
> experimentally anchored force-stability validation, **not a common Yaris hull
> with relabelled mass**: buoyancy, drag/lift lever arms, wheel normal loads and
> sliding/float/roll thresholds depend jointly on displaced volume, underbody
> shape, wheelbase/track and centre of mass.

**That is a description of our mass sweep.** Verified live from
`data/all_runs_inventory.csv`: the inventory carries no mesh or hull column that
varies, only `n_vehicle` (3846, 8905, 29804, which are the g48/g64/g96 particle
counts of the same hull), and **each of the three carries all three masses,
1100.0, 1609.0 and 2337.0 kg**. One geometry, three relabelled masses. CLAUDE.md
item 10 independently records that 1609 and 2337 have no source in
`vehicle_params.py`.

**This is corroboration, not a new finding, and I will not present it as one.**
CLAUDE.md **A-3** already says exactly this: "CLASS-SPECIFIC GEOMETRY, NOT MASS
ALONE ... buoyancy, drag and lift lever arms, and sliding/float/roll thresholds
depend on displaced volume, underbody shape, wheelbase, track and CoM, not mass
alone." And item 10 already forbids describing the mass sweep as spanning cited
vehicle classes.

What this catalog adds is worth having anyway:

1. **It names the practice, not just the principle.** A-3 states a general
   physical fact. This states the specific inference it forbids, in the
   project's own vocabulary, and it was sitting unread in the project's own
   corpus.
2. **It is a further source.** A-3's own note concedes that Smith/Modra/Felder
   and Arrighi were already in the register "so they are not independent
   support". This is a separate synthesis over 60 papers.
3. **It scopes what mass-only scaling is allowed to do**: "Mass alone may be
   scaled only after geometry-specific hydrostatics and inertia are established;
   regressions can supply provisional CoM/inertia estimates, not validation."
   That is a condition, not a prohibition, and the project has not met it.

## 2. A validation ladder, and it is orderable

The same summary prescribes an order, which is more actionable than a list of
gaps:

> Verify force/momentum, hydrostatic equilibrium, free-surface dam-break/slosh
> and rigid-contact convergence **before vehicle cases**. Then validate
> class-specific force histories, wheel normal/tractive forces and 6-DOF
> trajectories against gated runs or controlled tests; **report experimental,
> parameter and discretization uncertainty separately**.

Two observations, both offered to D4 rather than acted on by me:

- The prerequisite rungs (force/momentum conservation, hydrostatic equilibrium,
  dam-break, slosh, rigid-contact convergence) are exactly the kind of thing the
  C0 to C4 validator suite and the regime ladder already target, so this is a
  literature-backed ordering for work that partly exists.
- "Report experimental, parameter and discretization uncertainty **separately**"
  is a direct instruction against a single combined error bar, and it pairs with
  unit 2's blocking-and-stationarity finding.

It also lists what stays unresolved even after that ladder: "turbulence/air
entrainment, tire-water-road friction, suspension/drivetrain control, leakage,
unsteady flood fronts (which can raise drag 40-50%), and extrapolation beyond
measured depth, velocity, orientation and bed conditions."

Two of those are ours specifically: we have **no tire-road friction model at all**
(a single `floor_friction` scalar on a wheel-less particle cloud, per D4's
`cf9e85c`), and we **extrapolate beyond measured orientation**, since the canonical
runs are a single orientation.

## 3. The wall-penetration catalog says our P-2 threshold cannot be anchored

Gate P-2 caps water fraction inside the vehicle bounding box at 0.10
(`gates.py:147-148`). Seven of 17 runs fail it, including g64_m1100 at
`passthrough_max_frac = 0.10670498480368847`.

The catalog's verdict, verbatim:

> **No retrieved record reports calibration/subtraction of a smeared wall layer,
> an accepted correction protocol, or a defensible minimum number of cells across
> shallow water. Thus no single threshold - or evidence for GIMP/CPDI eliminating
> this error - can be inferred.**

So across 16 papers there is no literature basis for a numerical threshold of
P-2's kind, and the catalog states positively that none *can* be inferred from
the retrieved evidence.

This does not make P-2 wrong. It makes P-2 **the same category of object as
DRIFT_THRESHOLD**: a defensible containment heuristic with no external source.
CLAUDE.md item 6 already says no gate is a physics validation and that
`gates.py:195-196` concedes DRIFT_THRESHOLD has no peer-reviewed source. **P-2's
0.10 belongs in that same sentence and currently is not there.** That is the one
concrete, new, actionable item in this unit.

**STRENGTHENED by D4's `26971c0`, and considerably.** I argued that P-2's 0.10
has no external source. D4 then established what P-2 actually measures, and I
verified it at source: `sim_standing.py:463-465` takes the vehicle's
axis-aligned bounding box and counts the fraction of water particles inside
**that box**, not inside the hull. Since CLAUDE.md item 4b records the hull
filling only 33.2% of its own bbox, most of the box is void by construction. D4
measured the transparent-box null baseline at **11.30 to 14.90%** against a gate
of **0.10**, so the null **exceeds** the gate in **17 of 17** runs. (D4's first
figure, 10.3-11.0%, came from a reviewer; `5dbe04d` re-derives it independently
from the rollout artifacts and corrects it upward. Median share genuinely inside
the hull is 6.50%, range 3.27-22.84%.)

So P-2 is not merely an unsourced threshold, which is what I claimed. **It is a
threshold sitting on its own null baseline, measuring pile-up rather than
leakage.** That is a stronger statement than mine and it came from D4 measuring
the quantity rather than, as I did, reasoning about the threshold. The
recommendation is unchanged and now better supported: P-2 belongs in CLAUDE.md
item 6's sentence alongside DRIFT_THRESHOLD.

**One precision, checked so nobody over-corrects.** CLAUDE.md item 7 already
describes P-2 accurately as "max water fraction inside the vehicle **bounding
box**", verified live at `CLAUDE.md:218-219`. So item 7 does **not** need
rewriting on the bounding-box point; it was right. What item 7 does carry, as D4
notes, is a different mislabel: it calls 7.99 percent a "**failure rate**", when
7.99 percent is a metric value, not a rate of anything. Two separate issues, and
only the second is item 7's.

It also confirms the known negative that no wall-penetration plateau exists in
the literature, which project memory already records; I am not re-deriving that.

## 4. What I did not do

I have still read only 4 of the 14 catalogs' content. The remaining ten are
`Physics Simulation Validation Protocol` (81), `Quantitative Flood Traversability
Connections` (82), `Reliable AI Scientific Software` (79), `MPM Simulation
Verification Provenance` (68), `Moving Rigid Body Free Surface Validation` (44),
`Small Data Physics Surrogates at 36 Conditions` (47), `Dynamic Vehicle Traction
in Floodwater` (43, summary only; its catalog table I did mine), `Simulation
Ready Vehicle Mesh Assets` (36), `Optical Vehicle Collision Geometry` (23) and
`Trustworthy AI Assisted Scientific Simulation` (13).

On this unit's evidence, reading a summary costs minutes and can surface a
direct methodological criticism, so the remaining ten are worth more than I
assumed when I deprioritised them in unit 6.

## 5. Status

Nothing here is a project simulation measurement. The one project-side fact I
assert, that all three masses run on one hull geometry, was read live from
`data/all_runs_inventory.csv` this session and is stated with its evidence.

UNVERIFIED:
1. The bracketed reference numbers in both summaries point into catalog tables I
   have not resolved to specific papers, so "60 papers" and "16 papers" are the
   catalogs' own claims about their coverage, not something I checked.
2. Whether the prerequisite rungs the coupling catalog lists are already met by
   the existing C0-C4 suite is D4's call, not mine.
3. I have not opened any of the 60 or 16 underlying papers.
