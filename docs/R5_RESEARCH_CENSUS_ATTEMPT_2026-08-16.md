# R5-D1 unit 5: I ran the census I proposed, and it did not reach fixpoint

Date 2026-08-16. Branch `claude/r5-research`. Follows unit 4, which proposed
"iterate to fixpoint rather than one hop" as the non-catalog route. This unit is
me doing that and reporting what actually happened, including two of my own
errors caught before publication.

**Bottom line: the fixpoint was NOT reached. I stopped the traversal deliberately
in round 3. The catalog-recall conclusion from unit 4 survives, and is now robust
across two independent definitions and two traversal depths, but the census
itself is incomplete and should not be described as one.**

---

## 1. What was run

Seeded with all 32 papers known at the end of unit 4 (the 16 catalog-derived plus
the 16 graph-derived). Bidirectional traversal on OpenAlex: for each node, every
work citing it and every work it references. Only nodes whose titles matched a
vehicle term and a water term were expanded, to keep the traversal
topic-bounded. Script and per-round snapshots in the session scratchpad.

**Growth curve, READ DIRECTLY from the run log:**

```
seeds resolved                              32 / 32
round 1:  expanded 32   nodes 1092   vehicle+water 124   next frontier  92
round 2:  expanded 124  nodes 3575   vehicle+water 298   next frontier 174
round 3:  stopped by me, in progress
```

The frontier **grew** at every round, 32 to 92 to 174. Two hops from 32 seeds
already touches 3,575 works. This does not look like it converges at any depth I
can reach with a polite-pool API and no key, and each additional hop degrades
precision (section 3). That is the honest result: **the connected component of
this literature is large, and "iterate to fixpoint" is not free advice, which is
a correction to what I recommended in unit 4.**

## 2. Two errors of mine, caught before they were reported

**(a) A regex false positive that manufactured an entire fake cluster.** My first
strict filter used `\b(vehicle|car|cars|...)` with **no trailing word boundary**,
so `car` matched **Carlisle** and **Carolina**. That pulled in the whole Carlisle
2005 urban-flood hydraulics literature and a Hurricane Floyd paper for North
Carolina, none of which are vehicle simulations, and it inflated the count. Fixed
to `\b(vehicles?|cars?|automobiles?|...)\b`. **The strict count fell from 34 to
15 on that fix alone.**

**(b) A contaminated intermediate number I am discarding rather than reporting.**
An intermediate pass gave "85 road-vehicle-in-water simulations, catalog recall
23/85 = 27.1%". Hand-inspection of its output showed it contained aircraft tire
hydroplaning, water-exit of submersible aerial vehicles, deep-sea mining
vehicles, and waterjet propulsion. **That 27.1% is withdrawn and must not be
quoted.** It measured a pool, not a class. I am recording it here only so that
nobody rediscovers it in a scratchpad and treats it as a result.

Both errors point the same way: a title-regex over a citation graph has poor
precision, and any number from it needs hand-inspection of the actual output
before it is stated. Neither error reached a commit or a claim.

## 3. The measurement that survives

Strict class, defined as: a **road vehicle** (car, truck, SUV, sedan, automotive)
in **floodwater or standing water** (flood, fording, wading, inundation, puddle),
studied **numerically**. Explicitly excluded, because hand-inspection showed the
graph supplies all of them: underwater and marine craft, amphibious vehicles,
aircraft and runway work, tire hydroplaning, water-entry and water-exit
dynamics, deep-sea mining, waterjet propulsion, pedestrian evacuation, sewer
network modelling, and agent-based flood-risk models.

Over the 3,575-node two-hop neighbourhood, data in
`data/r5_citation_graph_strict.tsv`:

```
road-vehicle-in-floodwater simulations found : 15
  present in the 489-DOI corpus              :  7
  MISSED by all 14 catalogs                  :  8
```

**The eight the catalogs missed**, all hand-checked against their titles:

| year | DOI | relevance on hand-check |
|---|---|---|
| 2024 | `10.1007/978-3-031-77489-8_32` | clear, 3D vehicle wading, improved single-layer scheme |
| 2023 | `10.1007/s11431-022-2393-2` | **borderline**, street layout and urban flood risk; likely applies criteria rather than simulating fluid-structure interaction |
| 2022 | `10.1007/978-981-19-3379-0_28` | clear, drag force in a deep-water wading simulation |
| 2021 | `10.1088/1742-6596/2083/4/042091` | clear, numerical simulation of vehicle wading |
| 2021 | `10.2208/jscejhe.77.2_i_1441` | clear, flooding and vehicle stability, JSCE |
| 2017 | `10.4271/2017-01-1327` | clear, Jaguar Land Rover wading CFD, water ingress and splash |
| 2016 | `10.4271/2016-28-0072` | clear, passenger car water wading CFD |
| 2012 | `10.1007/978-3-642-33835-9_15` | clear, vehicle wading simulation (record title reads "STRA-CCM+") |

So **seven clear and one borderline**, giving catalog recall of 7/15 on the
strict class, or 8/15 if the borderline one is counted as ours.

## 4. Why this is stronger than unit 4's number, not weaker

Unit 4 measured a **looser** class, "vehicle plus water plus simulation" at one
hop, and found 16 known against 16 missed. This unit measures a **stricter**
class at two hops and finds 7 present against 8 missed. Different definitions,
different depths, hand-checked separately:

| pass | class | depth | in corpus | missed | recall |
|---|---|---|---|---|---|
| unit 4 | vehicle + water + simulation | 1 hop | 16 | 16 | 16/32 |
| unit 5 | road vehicle in floodwater, strict | 2 hops | 7 | 8 | 7/15 |

**Both land near one half.** The conclusion is therefore robust to how the class
is drawn and to how deep the traversal goes, which is a much better-supported
claim than either number alone. The load-bearing sentence from unit 4 stands:
**no catalog-based search can establish the novelty claim, and any "N fording
simulations exist" figure is a floor.**

What I would now add, against my own unit-4 recommendation: "iterate to fixpoint"
is not achievable here at acceptable precision. The practical route is the
**author-cluster sweep**, step 3 of unit 4's proposal, which is bounded, high
precision, and reaches the recent uncited papers a citation graph structurally
cannot. That is the step I would do next, and it is not done.

## 5. Status

Not asserted anywhere here: any project simulation number, force, distance or
verdict count. Everything is a bibliometric count over a named, scripted
procedure with its data file committed, so the physics-skeptic gate does not
apply.

UNVERIFIED, honest list:
1. **The traversal did not converge.** Rounds 1 and 2 only. Round 3 was killed by
   me. Anything beyond two hops is unmeasured.
2. **All 15 strict-class papers are titles and DOIs, not reads.** None opened. The
   one marked borderline needs its abstract read to settle whether it belongs.
3. The eight missed papers are **not** DOI-verified against Crossref in this unit.
   Unit 4's separate 16 were verified 16/16; these eight were not, beyond
   resolving inside OpenAlex.
4. The strict exclusion list was built by hand-inspecting output, so it is tuned
   to what this particular traversal surfaced and may exclude a relevant paper
   whose title uses one of the excluded words incidentally. That is the mirror of
   error 2(a) and I have not tested for it.
5. The author-cluster sweep is proposed, not run.
