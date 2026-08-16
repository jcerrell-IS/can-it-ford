# R5-D1 unit 6: the author-cluster sweep, and a blind spot in my own filter

Date 2026-08-16. Branch `claude/r5-research`. Completes step 3 of the non-catalog
route proposed in unit 4 and left unrun in unit 5.

**Headline: three non-catalog routes, run on this laptop in one evening, found 28
distinct works absent from all 14 catalogs. Only 5 of the 28 were found by more
than one route, so the routes are complementary rather than redundant, and no
single one of them would have been enough.**

Data: `data/r5_citation_noncatalog_union.tsv`.

---

## 1. The sweep

Eight author clusters, chosen because the fording literature is a small number of
groups rather than a diffuse field. For each named researcher, resolve the
OpenAlex author record, pull their works, filter for road vehicle plus
floodwater, and check against the 489-DOI corpus **and** both earlier graph
passes, so a hit only counts as new if no route had it.

| cluster | works matched | not seen by any earlier route |
|---|---:|---:|
| Iowa plus DEVCOM GVSC | 0 (see section 2) | 0 |
| Liu and Zhang SPH school | 3 | 0 |
| Malaysia, UTP | 7 | 0 |
| Barcelona | 3 | 0 |
| UNSW | 4 | **3** |
| Xia and Falconer | 8 | **1** |
| Nihei | 4 | **3** |
| Arrighi | 2 | **1** |
| **total** | **31** | **8** |

The eight new works:

| year | DOI | cluster | title |
|---|---|---|---|
| 2025 | `10.1016/j.ijdrr.2025.105373` | Nihei | Relationship between vehicle probe data and flooding conditions |
| 2025 | `10.2208/jscejj.24-16070` | Nihei | Real-time monitoring of flood inundation |
| 2025 | `10.2208/jscejj.24-16110` | Nihei | **Flood-induced small car drifting conditions based on actual vehicle** |
| 2024 | `10.26190/unsworks/27433` | UNSW | Experimental testing of flood hazard curves for a partially submerged vehicle |
| 2023 | `10.1093/acrefore/9780199389407.013.438` | UNSW | Vehicle-related causes of flood fatalities |
| 2022 | `10.1051/e3sconf/202234704005` | Xia and Falconer | Prediction of floodwater impacts on vehicle blockages at bridges |
| 2017 | `10.4225/53/58e1dfd63f1f4` | UNSW | Expert opinion: stability of people, vehicles and buildings in floodwater |
| 2016 | `10.24355/dbbs.084-201611141038-0` | Arrighi | Vehicles, pedestrians and flood risk: incipient motion |

**The one to look at first is `10.2208/jscejj.24-16110`**, a 2025 Nihei-group
paper on flood-induced small-car drifting from actual vehicle data. Nihei 2025's
full-scale sliding experiment is already the highest-value citation this dispatch
found, and this is the same group continuing on the same failure mode, which is
our dominant mode. Not read, JSCE Japanese-language journal.

## 2. My own filter had a blind spot, and it hid the most important cluster

**The Iowa plus DEVCOM GVSC cluster returned zero matches, and the reason is my
vocabulary, not their absence.** My strict filter required a term from
`ford|fording|wading|flood|inundation|puddle`. That group does not use those
words. They write **"shallow water"**. He 2026's title is "Predicting
Vehicle-Water Interaction in **Shallow Water**", which contains no flood term at
all, so my filter scored the single most contribution-threatening paper in this
whole dispatch as a non-match.

Re-running that cluster with a widened water vocabulary
(`water|shallow water|hydrodynamic|submerged|amphibious|river crossing`):

```
Iowa + DEVCOM GVSC, v1 vocabulary : matched 0
Iowa + DEVCOM GVSC, v2 vocabulary : matched 7, of which 5 already known, 2 new
```

The two new ones are marginal: an amphibious cycloidal propeller paper and an SAE
record that duplicates the title of `10.4271/2021-01-0252`. So the cluster is in
fact well covered, **but it was covered by the citation graph, not by any keyword
filter I wrote.**

**This is the third filter defect I have caught in two units**, after the
`\bcar` boundary bug that matched Carlisle and Carolina, and the contaminated
pool that produced the withdrawn 27.1%. The pattern is consistent and worth
stating plainly: **a keyword filter's misses are invisible from inside it.** The
only reason I found this one is that a cluster I *knew* contained relevant work
returned zero, which is a check that only exists when you already know the
answer. That is not a method, it is luck, and it is exactly the failure mode that
produced "four fording simulations" in the first place.

The practical consequence: the citation graph and the author sweep are
**complementary, and both are needed**. The graph reaches work whose vocabulary
you did not anticipate. The author sweep reaches recent work the graph cannot,
because it is too new to be cited. Neither alone is sufficient.

## 3. Consolidated: what the non-catalog routes found

```
489-DOI corpus (14 catalogs plus both Elicit outputs)
distinct works found by non-catalog routes and absent from all of it :  28
  by route:  graph 1-hop            16
             graph 2-hop strict      7
             author cluster          8
             author cluster v2       2
  found by more than one route       5
```

Only 5 of 28 overlap between routes. If any single route had been run alone, most
of these would still be missing.

**Honest caveat on the 28.** They span the two class definitions used in units 4
and 5 plus the author-sweep definition, so relevance varies across them: some are
core vehicle-wading simulations, some are flood-risk or fatality studies that
mention vehicles. **None of the 28 has been read.** The number is a count of
"catalogued nowhere in this project and plausibly relevant", not a count of
direct competitors.

## 4. Unit 5's borderline case is resolved, and the strict recall is exactly half

Unit 5 flagged `10.1007/s11431-022-2393-2` as borderline. Its full title, READ
DIRECTLY from OpenAlex, is "Exploring impact of street layout on urban flood risk
of people and vehicles under extreme rainfall based on numerical experiments".
That applies stability criteria inside an urban flood model; it does not simulate
vehicle-water interaction. **Excluded.**

Updating unit 5's strict class accordingly:

```
strict road-vehicle-in-floodwater simulations, 2 hops : 14   (was 15)
  present in the 489-DOI corpus                       :  7
  MISSED by all 14 catalogs                           :  7   (was 8)
  catalog recall                                      :  7/14, exactly one half
```

All 8 of unit 5's originally-listed misses were separately confirmed to resolve
via Crossref, **8 of 8**, closing unit 5's UNVERIFIED item 3.

So the recall figure now stands at 16/32 in unit 4's loose class at one hop and
7/14 in unit 5's strict class at two hops. **Two different class definitions, two
different depths, and both give exactly one half.**

## 5. What this does and does not settle for the paper

It settles the method question: **no catalog, and no keyword search, can bound
this literature, and that includes the keyword searches I wrote.** Any sentence
of the form "N vehicle fording simulations exist" should not appear in the paper.

It does not settle the novelty question, and I want to be careful not to
overclaim in the other direction. Of everything found across all six units, the
papers that actually bear on the contribution remain the small set already
identified: Al-Qadami 2023 `10.3390/su151713262` (full scale, stability
thresholds, already in our bibliography), He 2026 `10.1115/1.4071177` (validation
axis), Zhang 2023 `10.1007/s11433-023-2137-5` and Lyu 2023
`10.1016/j.compfluid.2023.106144` (particle method). The other 28 mostly widen
the field rather than threaten the claim. **The correct next step is reading
those four, not counting more.**

## 6. UNVERIFIED

1. **None of the 28 has been read.** Titles and DOIs only.
2. The 8 author-sweep works are not Crossref-verified; they resolved inside
   OpenAlex only. Unit 4's 16 and unit 5's 8 were verified, 16/16 and 8/8.
3. `10.2208/jscejj.24-16110`, the Nihei small-car drifting paper, is the highest
   priority of the 28 and is in a Japanese-language JSCE journal I have not
   opened.
4. The author clusters were chosen by me from the authorships I had already seen.
   A group with no paper in my current set is still invisible, and I have no way
   to measure that from inside.
5. Still blocked from earlier units: the Nihei corrigendum content (publisher TDM
   reservation), Zhang 2023 full text (closed, no OA anywhere), He 2026 full text
   (closed, no OA anywhere).

No project simulation number, force, distance or verdict count is asserted here.
Every figure is a bibliometric count over a scripted procedure with its data file
committed, so the physics-skeptic gate does not apply.
