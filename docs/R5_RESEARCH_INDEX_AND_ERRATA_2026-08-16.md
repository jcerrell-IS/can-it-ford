# R5-D1 index and errata: read this before using any number I produced

> ## READ `R5_RESEARCH_WHAT_SURVIVES_2026-08-17.md` FIRST
>
> **That file supersedes this one as the entry point.** This document is an errata
> table: it lists *corrections*. `WHAT_SURVIVES` lists *conclusions*, split into
> safe-to-cite, retired-never-cite, and unverified. If the two disagree,
> `WHAT_SURVIVES` is newer and wins. Come here for the working behind a correction.

Date 2026-08-16, **last updated 2026-08-17 (unit 41)**. Branch
`claude/r5-research`, **51 commits** ahead of `origin/main` (`1a868f3`).
**32 documents, 7 data files.** Note that `777567a`, the base my work
sits on, is itself unpushed.

---

## THE SHORT VERSION: eight things that change what you do

Everything below this section is evidence. This is the part that is actionable.

1. **The pipeline shape is prior art and the register already says so** (G12,
   G13). Do not claim it. Position as a domain transfer.
2. **Every novelty axis I proposed got occupied**: Al-Qadami 2023 takes full scale
   and stability thresholds, Azhar 2023 takes the particle method, He 2026 takes
   solver validation. **The paper cites none of the first two.** Three orphan
   candidates survive, and the project already has code for two:
   reconstruction-to-collider, **viscoplastic mud** (`bingham_cfl_crossover.py`
   plus a branch on origin), and **GNN free rigid-body coupling** (open
   hypothesis, no measured speedup anywhere).
3. **L-2 needs no amendment.** I proposed one and the AR&R primary source killed
   it: the 3.0 m/s cap is human-derived, for occupant egress. Attach Cox, Shand
   and Blacka (2010) as its source and stop there. **L-7 does need amending**, see
   `PROPOSED_AMENDMENTS` section 1 as narrowed by 1a.
4. **No catalog-based or keyword search can bound this literature.** Measured
   three independent ways: citation graph, author clusters, and the corpus's own
   prose. Any "N fording simulations exist" number is a floor.
5. **Never quote a depth-velocity threshold without its model scale AND its value
   basis.** Six scales are in play, `lambda^1.5` spans a factor of 282, and
   Azhar 2026's "1:14" is a validation scale not a value scale. Use the rebuilt
   `data/r5_citation_thresholds.tsv`, never a prose table.
6. **FM 90-13's 1.5 m/s vehicle fording limit is in neither canonical file**, only
   a non-canonical inbox note. It is the closest vehicle-derived velocity
   criterion found, at half the AR&R cap. Record it; I have not read the manual.
7. **Bibliography, all verified, latent not live**: add four DOIs
   (`kerbl20233dgs`, `xie2023physgaussian`, `alqadami2022`, `thorpe2026pvwm`), fix
   `ccsa2010yaris` 2010 to 2016, and mind that adding PhysGaussian's CVPR DOI
   forces its year to 2024. The three entries actually cited are sound.
8. **FLAG-1 is one browser-minute of work** and unblocks the Nihei
   rolling-resistance numbers, which are currently provisional. It is gold OA
   CC-BY; only bot filtering blocks automation.

---

**Why this file exists.** I corrected myself more than twenty times across
twenty-five units.
Anyone opening a single document can act on a number I later withdrew. Section 1
is the errata: every superseded claim, what replaced it, and where. Section 2 is
the current best value of every headline number. **If a number below disagrees
with a number in an earlier unit, the number below wins.**

---


## 0. What is here, in reading order

Start with this file, then section 3 below for the four papers that matter. The
rest is grouped by what it answers.

**Mining the corpus**
| doc | what it establishes |
|---|---|
| `R5_RESEARCH_ELICIT_AND_CATALOG_MINE_2026-08-16.md` | the Elicit CSV (42 rows, 41 unique papers), 14 catalogs, the 489-DOI cross-reference |
| `R5_RESEARCH_SETTLING_AND_RESOLUTION_MINE_2026-08-16.md` | settle length has no constant but a citable protocol; the determinism floor has a named cause |
| `R5_RESEARCH_TWO_MORE_CATALOGS_2026-08-17.md` | "not a common Yaris hull with relabelled mass"; P-2 has no anchorable threshold |
| `R5_RESEARCH_REMAINING_TEN_CATALOGS_2026-08-17.md` | the other ten summaries. **Its section 1 is RETIRED**, see erratum 19 |
| `R5_RESEARCH_COUPLING_TABLE_AND_P2_UPDATE_2026-08-17.md` | the coupling table; the GCI gate's sources are already documented (a negative) |
| `R5_RESEARCH_PROSE_CORPUS_SWEEP_2026-08-17.md` | 109 DOIs in corpus prose that no catalog holds, 88 uncited |
| `R5_RESEARCH_PRIOR_ART_ALREADY_INTEGRATED_2026-08-17.md` | the prior-art assessment; the register already had it as G12/G13 |
| `R5_RESEARCH_FRICTION_AUDIT_AND_MUD_GAP_2026-08-17.md` | friction is known; **the viscoplastic-mud gap is not**, and we have code |
| `R5_RESEARCH_GNN_AND_MESH_LICENCE_2026-08-17.md` | DataCite answers E8's open question; a third novelty candidate |
| `R5_RESEARCH_BIB_DOI_SUPPLEMENT_2026-08-17.md` | **four verified DOIs the bibliography lacks**, and its year audit |
| `R5_RESEARCH_UNCITED_AUDIT_2026-08-17.md` | audit of my own uncited method; it mostly holds |
| `R5_RESEARCH_HULL_VOLUME_CONFLICT_2026-08-17.md` | **RETRACTED escalation.** Read section 0 only; the rest is kept as a worked error |
| `R5_RESEARCH_WHAT_SURVIVES_2026-08-17.md` | **START HERE.** Safe-to-cite / retired / unverified in one page. Supersedes this index |
| `R5_RESEARCH_SEALING_AND_FLAG4_2026-08-17.md` | **for D4**: the literature's vehicle-sealing split; and FLAG-4 closed (`martinezgomariz2018` = `10.1111/jfr3.12262`) |
| `R5_RESEARCH_FLOODFILL_MEASURED_2026-08-17.md` | **the measurement that closes the above.** The audit's 4.5628 does not reproduce; sealed cavity disagrees **2.1x**; operation is bistable near **22.2 mm**. Ships its script |
| `R5_RESEARCH_NCAC_README_TERMS_2026-08-17.md` | **for D2**: the NCAC READMEs are tracked, carry an acknowledgement request, and no licence |
| `R5_RESEARCH_MPM_BOUNDARY_CLUSTER_2026-08-17.md` | **for D4**: the BC anchor and a 2024 paper on the open BC question |

**Novelty and the papers that matter**
| doc | what it establishes |
|---|---|
| `R5_RESEARCH_PRIMARY_SOURCE_VERDICTS_2026-08-16.md` | L-2 amendment refuted at the AR&R primary source; He 2026 and Zhang 2023 verdicts |
| `R5_RESEARCH_PROPOSED_AMENDMENTS_2026-08-16.md` | proposed L-7 amendment; catalog recall measured |
| `R5_RESEARCH_NOVELTY_COLLAPSE_2026-08-16.md` | every novelty axis I proposed is occupied; only MPM-vs-SPH and geometry provenance survive |
| `R5_RESEARCH_CENSUS_ATTEMPT_2026-08-16.md` | the census did **not** reach fixpoint; two of my own errors caught pre-publication |
| `R5_RESEARCH_AUTHOR_SWEEP_2026-08-16.md` | author-cluster sweep; my own filter hid the most important cluster |

**Thresholds, scale and terminology traps**
| doc | what it establishes |
|---|---|
| `R5_RESEARCH_SCALE_TRAP_2026-08-16.md` | six model scales, `lambda^1.5`, and the rebuilt threshold table |
| `R5_RESEARCH_KRAMER_CONFIRMED_MODE_DEPENDENT_2026-08-17.md` | model-vs-prototype bias is **mode-dependent with opposite signs** |
| `R5_RESEARCH_WATERTIGHT_TWO_SENSES_2026-08-17.md` | "watertight" is two different properties; A-4 straddles them |
| `R5_RESEARCH_NIHEI_DRIFTING_AND_CSV_DUPLICATE_2026-08-17.md` | the full-scale drifting paper; the CSV duplicate |

**Method, verification and blockers**
| doc | what it establishes |
|---|---|
| `R5_RESEARCH_RESOLUTION_COMPARISON_2026-08-16.md` | the resolution claim an adversarial review killed, and the corrected version |
| `R5_RESEARCH_ASYMMETRY_DOWNGRADED_2026-08-17.md` then `R5_RESEARCH_ASYMMETRY_RETIRED_2026-08-17.md` | how my best finding was downgraded, then retired |
| `R5_RESEARCH_NIHEI_ROUTES_AND_AUTHOR_TRAP_2026-08-16.md` | ten routes to the corrigendum; the Bando author trap |
| `R5_RESEARCH_FLAG_BLOCKED_2026-08-17.md` | **the 5 blocked items and exactly what unblocks each** |

## 1. ERRATA. Every claim of mine that was corrected or withdrawn

| # | claim as first written | where | status now | authority |
|---|---|---|---|---|
| 1 | jfr3.12885 appears in 27 files | unit 1 §4a | **25** by the stated method, 26 counting catalogs | `cf9edab`, transposed from another DOI |
| 2 | row 7 is "roughly twenty times below" the other thresholds | unit 1 §3 | **~118x** under Froude, and it is 1:24 not the remembered 1:10 | unit 3 §6 |
| 3 | jfr3.12551 makes the 3.0 m/s cap vehicle-derived, so amend L-2 | unit 1 §3 | **REFUTED.** AR&R says it exists for human stability and occupant egress. **L-2 is correct; do not amend** | unit 3 §4, AR&R primary source |
| 4 | 8 catalogued DOIs are cited in the paper | unit 1 §6 | **3** are `\cite`d; 7 have a real `doi=` field; 8 was string presence | unit 7 §5 |
| 5 | caveat: divergent catalog copies may hide DOIs | unit 1 §8 | **closed at zero**, all five pairs have identical DOI sets | unit 3 §7 |
| 6 | Nihei brake state "bears on our 16 SLIDE verdicts" | unit 3 §5c | **direction wrong.** Lower friction increases sliding, so SLIDEs get *more* robust; the single STUCK run is what is endangered | D4 `cf9e85c`, recorded unit 4 §5 |
| 7 | three novelty axes survive: full scale, particle method, stability verdict | unit 4 §1 | **all occupied.** Only MPM-vs-SPH and geometry provenance remain | unit 4 §1a, then unit 7 §3 |
| 8 | we already cite Al-Qadami 2023 | unit 4 §1a | **WITHDRAWN.** The DOI is in a `note` of a stub entry titled `{{VERIFY: exact title}}`, cited in zero `.tex` | unit 7 §4 |
| 9 | the fix is to iterate the citation graph to fixpoint | unit 4 §3 | **not achievable.** Frontier grew 32→92→174; I stopped it | unit 5 §1 |
| 10 | strict class: 15 found, 8 missed | unit 5 §3 | **14 found, 7 missed** after the borderline was excluded | unit 6 §4 |
| 11 | 85 simulations, catalog recall 27.1% | unit 5 working | **WITHDRAWN.** Contaminated with aircraft, water-exit, deep-sea and waterjet papers. Never quote it | unit 5 §2b |
| 12 | draft resolution claim, "3.8x better resolved", 7.6 vs 2.000 cells per depth | unit 8, never published | **NOT CLEAN, 6 blocking issues.** Rewritten to cell size only | unit 8 §1 |
| 13 | Al-Qadami Table 1 series, carried from the review | unit 8 §4 | **independently verified**, review reproduces exactly | `4140127` |
| 14 | "state the model scale" is the rule | unit 9 §2 | **insufficient.** Needs a second label, `value_basis`, or Azhar 2026 gets inflated 52x | `66f7427`, unit 9 §2b |
| 15 | the CSV holds 42 unique papers; yields are 10/42 and 9/42 | units 1, 9 | **41 unique papers.** Rows 6 and 16 are the same paper (`10.1111/jfr3.12262`, online 2016 vs print 2018). Yields are **10/41** and **9/41**; numerators unchanged | unit 12 §2 |
| 16 | `10.26190/unsworks/27433` is dated 2024 | unit 6, and `data/r5_citation_noncatalog_union.tsv` | **2017.** OpenAlex was wrong; DataCite is the registering agency. **Superseded by erratum 17: it was not the only one, and the TSV is now fixed** | unit 12 §3, then unit 13 |
| 17 | one wrong year, documented but left in the data file | erratum 16 | **two wrong years, both now CORRECTED in the TSV.** `10.26190/unsworks/27433` 2024→**2017** and `10.4225/53/58e1dfd63f1f4` 2017→**2015**. All 28 union rows re-checked against the registering agency: **0 errors in the 25 Crossref-registered DOIs, 2 errors in the 3 DataCite-registered ones** | unit 13 |
| 18 | "never take titles, authors or years from aggregators" | unit 13 | **too broad.** Field-specific: titles 28/28 correct, years wrong only on DataCite deposits, author `display_name` unreliable because it is a disambiguation product | unit 14 |
| 19 | the FORD/NO-FORD evidentiary asymmetry is "the single most valuable thing found in this whole dispatch" | unit 16 §1 | **RETIRED, superseding unit 17's downgrade.** Both readable references now read in FULL: Easterling 2001 has zero hits across 2,818 lines, and Eca/Dowding/Roache 2020 states the pass/fail accept-reject aspect "is not included in V&V20-2009". **Contradicted by one of its own cited sources.** Do not use it. Survivors: Easterling's "model validation is not binary", and a V&V 20 scope limit on extrapolation | units 17, 18 |
| 20 | the Nihei corrigendum is "blocked on publisher access" | unit 3 §5a, §8 | **overstated, withdrawn.** It is **gold OA, CC-BY, publishedVersion**. The barrier is host-level bot filtering plus `tdm-reservation`, a **fetch** status, not a **licence** status. My own flag file already had this right; unit 3 was never brought into line | D4 `7acb95f`, corrected unit 3 |
| 21 | "model-scale thresholds are non-conservative", unqualified | unit 12 §1b | **mode-dependent.** True for sliding, **false for floating**: Kramer finds prototype flotation depths *higher* than model. Our dominant mode is SLIDE, the unsafe-erring side | unit 20 §2 |
| 22 | g64_m1100 "fails gate P-2", disclosed as a leakage defect | unit 8 §2 | **not leakage.** P-2 counts water in the vehicle's axis-aligned **bounding box**, and the hull fills only 33.2% of it. It is a pile-up test | D4 `26971c0`, unit 24 |
| 23 | P-2's transparent-box null baseline is 10.3 to 11.0% | unit 24 | **11.30 to 14.90%**, so the null **exceeds** the 0.10 gate in **17 of 17** runs. D4 re-derived their own figure upward | D4 `5dbe04d`, unit 25 |
| 24 | 137 catalog-absent DOIs in corpus prose, 101 uncited | unit 29 first pass | **109 and 88.** The regex captured bare journal stubs, and `10.1111/jfr3` matched 47 files as a substring; a later over-correction then dropped two real DOIs | unit 29 §1 |
| 25 | the live bibliography regressed against the 2026-08-02 snapshot | unit 32 hypothesis | **false.** Live has 9 DOIs / 21 entries vs the snapshot's 1 / 15. The snapshot parks one DOI in a `note` field, which live drops entirely | unit 32 §1 |
| 26 | "the project does not cite its closest comparator" (board wording) | units 7, 27 relays | **too loose.** The *bibliography* does not cite Al-Qadami 2023; the register names Al-Qadami in G5 and G8 as a misattribution hazard | unit 28 §2 |
| 27 | the hull-density escalation: B5 contradicted, finding unintegrated, D4's P-2 qualified | units 34, 35 | **RETRACTED, 5 of 8 claims wrong.** B5 has a 2nd sentence I never read and AGREES; `genus` 33 and `mesh2sdf` 337 hits, not zero; `MESH_RECONCILIATION:196,201` already resolves 1609/2337; my "independent" 31.2% shares its numerator with item 4(b)'s 33.2%; and `5dbe04d` already measured in-hull water at median 6.50% rising 12x. **Survives: genus 222, which I finally measured myself** | unit 36, physics-skeptic |
| 28 | "no Mac interpreter here has numpy", my reason for not verifying | unit 34 §7 | **false.** `~/Downloads/vehicle_meshes/mesh_venv` has trimesh 4.12.2 and numpy 2.5.1, documented at `MESH_RECONCILIATION_2026-08-08.md:39`. Verifying was a ten-minute job; I escalated instead of measuring | unit 36 |
| 29 | the flood-fill interpretation: agreement with the audit's ~6.8 bound, a "35%" step, a cabin/window mechanism, and "density falls 11-52%" | unit 39 first draft | **FOUR WITHDRAWN.** The 6.8 is the *deprecated lowres* mesh (6.8185, genus 32) the audit itself calls "the misleading one"; the step is **+53.75%**, not 35% (I switched denominators mid-document); the leak aperture is **≲40 mm** seams, not windows (one 20 mm dilation seals it); and at 10/15/20 mm the fill seals **nothing**, so the density drop was half-voxel shell overhang. **Survives: the numbers reproduce exactly, and the sealed cavity disagrees 2.1x (1.020 vs 2.161 m3)** | unit 39, physics-skeptic |
| 30 | my own "parameter-free apart from pitch" criticism of the audit | unit 39 §3(b) draft | **I had just committed it.** `binary_fill_holes` defaults to 6-connectivity and I never said so; 18- or 26-connectivity seals **nothing**, moving my headline by **3.25x**. I also shipped no script while criticising the audit for shipping none. Both fixed in the revision | unit 39 |
| 31 | vehicle sealing is "the recorded cause of the largest disagreement" in the incipient-motion literature | unit 40 first draft | **WITHDRAWN, and the reason is bad practice not bad luck: I cut the source quote one clause short.** The sentence continues "...**because model density/mass was not correctly scaled**". Shu's higher D×V is attributed to **friction** (mu 0.39-0.68 vs 0.3), and foam-filling is one of TWO components of the fix. "Largest" is my own superlative, absent from the source. **Second truncated-quote error of this dispatch** after unit 36's register B5 | unit 42, physics-skeptic |
| 32 | "our pipeline picks the fill on one line, and no gate or document records why" | unit 40 first draft | **WITHDRAWN three ways.** `vehicle.py:175` is **automatic dispatch** on `is_watertight`, not a knob; the canonical hull is watertight (`WATERTIGHT_HULL_TOOL_FINDINGS.md:159`) so `solidify_columns` is **unreachable**; the reason is recorded at `vehicle.py:93-94` ("buoyancy is unbiased"); and `sim_standing.py:381-383` aborts outside fill_ratio [0.5,2.0], where the column fill gives **2.16518**. Also: my hedge that bulk density is not the governing quantity argued against my own case | unit 42, physics-skeptic |
| 33 | FLAG-4 "CLOSED", with the Elicit CSV as independent decisive confirmation | unit 40 first draft | **DOI certain, REFERENT NOT SETTLED.** `10.1111/jfr3.12262` is confirmed, but the bib entry carries a `note` I never reported ("floating/sliding, not toppling") that fits the rival 2017 paper equally well; the CSV's 2018 stamp is the same publisher metadata Crossref serves, so it is one source twice; and **the rival sits in the same CSV at row 31**, undisclosed | unit 42, physics-skeptic |

**EVERY ORIGINAL IS NOW MARKED IN PLACE, unit 23.** This index only helps a
reader who opens *it*. D4 read unit 3 directly and picked up a stale claim
(erratum 20), which proved the index alone is not enough. I audited all twenty
errata against their original locations and found **seven** that had been
corrected here but never marked at the source: the /42 denominators, the
divergent-copy caveat, the "8 cited in the paper" count, the "we already cite
Al-Qadami" paragraph, the iterate-to-fixpoint recommendation, the strict 15/8
counts, and the brake-state direction. All seven now carry an in-place
correction block pointing at the unit that superseded them. **A reader landing on
any single document now gets the correction without needing this file.**

**Three of these matter most.** #3, because I proposed the L-2 amendment and my
own test killed it. #8, because it means the paper does not cite its closest
comparator at all. #11, because a contaminated percentage is exactly the kind of
number that survives into a draft if nobody writes down that it was withdrawn.

**A standing rule from #20, which D4 stated and I have adopted: a LICENCE status
and a FETCH status are different things.** `oa_status` tells you what you are
permitted to read; a 403 tells you what one client got from one host on one
attempt. Recording the second as the first inflates a blocker and can send
someone hunting for institutional access they do not need. Checked across my own
flag file: FLAG-2 (He, Zhang, Lyu) and FLAG-3 (Nihei JSCE) are genuine **licence**
blocks, `oa_status: closed`, so "institutional access" is correct there. FLAG-1
was the only conflation.

**A standing caution that came out of #16 and #17.** Four separate metadata
defects in this dispatch all came from bibliographic aggregators rather than from
publishers: the Bando given name (OpenAlex and scite say "Yoshinori", the
publisher deposit says "Yu" in both DOIs), the Azhar subtitle that
`auditBibliography` passed as `matched` while the trailing phrase differed, and
two wrong publication years. The years split cleanly by registering agency:
**0 wrong in 25 Crossref-registered DOIs, 2 wrong in 3 DataCite-registered
ones.** N is only 3 on the DataCite side, so treat that as a signal to check
repository deposits against DataCite directly, not as a rate.

**REFINED, and my first version of this rule was too broad.** I wrote "never take
author names, titles and years from aggregators", then tested it against my own
data. All 28 titles in `data/r5_citation_noncatalog_union.tsv`, which came from
OpenAlex, were re-checked against Crossref or DataCite: **28 of 28 match** at
0.995 similarity or better. OpenAlex transcribes titles faithfully. The defect is
**field-specific**, not blanket:

| field, from an aggregator | evidence in this dispatch | verdict |
|---|---|---|
| title | 28 / 28 exact against the registering agency | **reliable** |
| year | 0 wrong of 25 Crossref-registered; 2 wrong of 3 DataCite-registered | **check DataCite deposits** |
| author given name | `display_name` "Yoshinori BANDO" against deposit "Yu Bando"; OpenAlex's own `raw_author_name` holds the correct string | **unreliable: `display_name` is a disambiguation product, not a transcription** |

So the usable rule is narrower and more actionable than what I first wrote:
**take author names from `raw_author_name` or the registering agency, and
re-check years for any DataCite-registered repository deposit. Titles from
OpenAlex are fine.** Separately, `auditBibliography` returned `matched` with
`high` confidence on a title whose trailing phrase was materially wrong, so it
confirms identity, not wording.

## 2. Current best value of every headline number

All read live this session. Denominators stated, as required.

**The Elicit outputs**
```
.bib entries                                            8
CSV: data rows 42, columns 27, every row well formed at 27 fields
CSV UNIQUE PAPERS                                      41   (rows 6 and 16 are one paper)
rows carrying a real threshold value          10 / 41   (9 in the summary column, +1 recovered from quotes)
rows carrying a real friction value            9 / 41   (0 hidden in quote columns)
rows carrying RAW MODEL-SCALE values           2 / 12   (rows 7 at 1:24, 23 at 1:10)
motion state                          18 stationary / 14 self-propelled / 10 unstated / 0 towed
copies of each Elicit file on this machine    >=7 and >=6, including inside the repo at citations/
```
Both yields are **lower bounds**, not point values: the duplicated paper was
extracted twice and returned a full threshold set in one row and "Not mentioned"
in the other, so the extraction demonstrably misses values it elsewhere finds.
The "1,345 rows" figure is a `wc -l` artifact of newlines inside quoted fields.
Never use it.

**The catalogs**
```
distinct paper catalogs                        14   (not 6)
papers they claim between them                738
unique DOIs they yield                        472   (union over divergent copies; identical sets)
unique DOIs incl. both Elicit outputs         489
  cited anywhere in the repo                   37
  in a real doi= field of the paper bib         7
  actually \cited in a .tex                     3
```

**Coverage, the load-bearing methodological result**
```
works found by non-catalog routes, absent from all 14 catalogs   28
  found by more than one route                                    5   (routes are complementary)
catalog recall, loose class, 1-hop graph                        16 / 32
catalog recall, strict class, 2-hop graph                        7 / 14
```
Both land at exactly one half, under different class definitions and different
depths. **No catalog-based or keyword-based search can bound this literature, and
that includes the keyword filters I wrote.** Any "N fording simulations exist"
figure is a floor.

**Vehicle-in-water simulations**: at least 16 from the catalogs, plus 16 more from
one graph hop, plus 8 from the author sweep. Treat as a floor, never a total.

## 3. The four papers that actually matter

Everything else widens the field. These bear on the contribution.

| paper | status | what it takes |
|---|---|---|
| `10.3390/su151713262` Al-Qadami 2023 | **full text READ** (CC-BY via UPCommons) | full scale, 6DOF fully coupled, stability thresholds, validated vs AR&R + theory + own experiments. **We do not cite it.** |
| `10.1111/jfr3.12885` Azhar 2023 | abstract read; **we DO cite it** | SPH particle method, validated against a physical model study, confirms AR&R for stationary vehicles. Also the source of our 0.55 friction |
| `10.1115/1.4071177` He 2026 | abstract only, **closed access** | experimental validation of a coupled vehicle-water model, free-running pool + flume |
| `10.1007/s11433-023-2137-5` Zhang 2023 and `10.1016/j.compfluid.2023.106144` Lyu 2023 | abstract/TLDR only, **closed access** | GPU SPH vehicle wading |

Add `10.1111/jfr3.70181` Azhar 2026 as a fourth particle-method paper, and
`10.2208/jscejj.24-16110` (2025 Nihei, small-car drifting from real vehicle data)
as the highest-priority unread item.

## 4. Blocked, and exactly what would unblock each

1. **Nihei 2025 corrigendum** `10.1016/j.rineng.2025.107527`. Eight routes tried.
   The Elsevier landing page carries `tdm-reservation: 1`, a machine-readable
   opt-out from automated retrieval, so I stopped on principle rather than work
   around it. **Unblocks in about a minute**: open
   `https://doi.org/10.1016/j.rineng.2025.107527` in a browser. It is CC-BY once
   open. Until then treat 0.0250 and 0.0242 as provisional.
2. **He 2026, Zhang 2023, Lyu 2023 full texts.** All `oa_status: closed`, no OA
   location in Unpaywall or OpenAlex, no repository deposit. **Unblocks with
   institutional access only.**
3. **`martinezgomariz2018` bib entry.** Has no title, DOI or journal, so its
   intended referent is genuinely ambiguous. I refused to guess. **Unblocks by
   asking whoever wrote the entry.**
4. **The 28 non-catalog works.** Titles and DOIs only, none read. Unblocks with
   time; unit 6 judged the yield low relative to reading the four above.

## 5. Recommendations, none of which I acted on

- **L-2: do not amend.** Attach Cox, Shand and Blacka (2010) as its source. My
  own proposal to amend it was refuted by the primary source.
- **L-7: amend**, per unit 4 §1 as narrowed by unit 4 §1a and unit 7 §3. Do not
  claim full scale, a stability verdict, or "a particle method" as novel.
- **L-5: add a DOI.** Neither Steffen 2008 DOI appears anywhere in the repo
  outside `.claude/`, and neither is in the paper bibliography.
- **Bibliography**: 9 of 21 entries carry a `VERIFY` marker and two have literal
  placeholder titles. Latent, not live, because both are cited nowhere.
- **Threshold table**: use the rebuilt `data/r5_citation_thresholds.tsv` with its
  `model_scale` and `value_basis` columns, never unit 1 §3's table.

I edited no file outside `docs/R5_RESEARCH_*` and `data/r5_citation_*`. I did not
touch `CLAUDE.md`, the register, the bibliography, or any solver file. Nothing is
pushed.

## 6. Consolidated UNVERIFIED

1. Nihei corrigendum content, and therefore whether 0.0250 / 0.0242 are final.
2. He 2026, Zhang 2023, Lyu 2023 full texts. Zhang 2023's "validates code-to-code
   not experimentally" is MEDIUM confidence on a search-engine rendering.
3. None of the 28 non-catalog works has been read.
4. The three model scales 1:14, 1:18, 1:43 are second-hand from a quote column.
5. Their vehicle mass (Perodua Viva) is unpublished; no mass normalisation.
6. Al-Qadami's reported 25% gap against Martinez-Gomariz does not reproduce
   (23.40 / 26.51 / 30.56 depending on denominator).
7. Whether MPM versus SPH is a defensible novelty axis is a physics judgement for
   D4, not a bibliographic one.
8. My author clusters were drawn from authorships I had already seen, so a group
   absent from my set stays invisible and I cannot measure that from inside.
