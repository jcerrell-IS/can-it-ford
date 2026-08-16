# R5-D1: Mining the Elicit outputs and every paper catalog

Date 2026-08-16. Branch `claude/r5-research`. Dispatch
`.claude/dispatch_prompts/round5/R5_D1_MINE_RESEARCH.md`.

Every number below was produced by a script run live on this machine during this
session and is tagged READ DIRECTLY. Nothing here is carried from a summary.
Claims I could not close are tagged UNVERIFIED and listed in section 8.

Companion data files, both written by this session:
- `data/r5_citation_xref.tsv`, 489 DOIs, cited-versus-catalogued, uncited-first sortable.
- `data/r5_citation_thresholds.tsv`, the 11 Elicit rows that carry a real number.

---

## 1. Four corrections to the dispatch's own premises

The dispatch corrected the bootstrap. Three of its corrections hold, and four of
its remaining claims do not survive a live check. All four are READ DIRECTLY.

**1a. The Elicit files are not unique copies, and one already sits in the repo.**
The dispatch states the Downloads `.bib` is "the ONLY copy on this machine". It is
not. `shasum -a 256` over a `find` of `/Users/josie` returns at least seven
byte-identical copies of the `.bib` (`e0d4d68a13e4...`) and six of the CSV
(`b90b396e34b8...`), including:

```
/Users/josie/can-it-ford/citations/Elicit - Flood-Crossing ... .bib     <- IN THE REPO
/Users/josie/Downloads/can-it-ford-main/citations/...
/Users/josie/can-it-ford-warpmpm-continue/citations/...
/Users/josie/can-it-ford-realism/citations/...
/Users/josie/can-it-ford-moving-vehicle/citations/...
/Users/josie/can-it-ford-BACKUP-before-history-purge/... (4 paths)
```

This matters beyond bookkeeping: "nobody looked at the Elicit output" is true,
but the reason is not that it was hidden in Downloads. It was in `citations/` in
the working repo the whole time. Note also that this `find` returned no Desktop
paths at all while `corpus_inventory` reports 387 files on that root, so the
Desktop tree was very likely denied by TCC during the walk. Seven is a floor,
not a total.

**1b. The 42-row correction is right, and reproduces.** `csv.reader` returns 43
records including the header, so 42 data rows, 27 columns, and every one of the
42 rows is well formed at exactly 27 fields. The file has 1,346 physical lines.
The "1,345 rows" figure in the bootstrap is the `wc -l` artifact the dispatch
says it is. Confirmed independently here.

**1c. There are 14 paper catalogs, not six.** The dispatch asks for a cross
reference over "all six Undermind catalogs". A walk for the literal heading
`## Paper Catalog (N papers)` across the Desktop corpus, Downloads and the repo
finds 14 distinct catalogs claiming 738 papers between them and yielding 472
unique DOIs. Five of the 14 exist as two copies with different sha256, so
"the report" is ambiguous for those five and a copy has to be named.

| catalog | claimed | unique DOIs | copies | distinct sha |
|---|---:|---:|---:|---:|
| Quantitative Flood Traversability Connections | 82 | 77 | 4 | 2 |
| Physics Simulation Validation Protocol | 81 | 75 | 4 | 2 |
| Reliable AI Scientific Software | 79 | 71 | 2 | 1 |
| Multi-resolution MPM for Large-domain Flooding | 78 | 73 | 2 | 1 |
| MPM Simulation Verification Provenance | 68 | 56 | 2 | 1 |
| Settling and Force Reporting in Free Surface Flow | 68 | 53 | 2 | 1 |
| Validated MPM Vehicle Water Coupling | 60 | 56 | 4 | 2 |
| Small Data Physics Surrogates at 36 Conditions | 47 | 42 | 4 | 2 |
| Moving Rigid Body Free Surface Validation | 44 | 35 | 2 | 1 |
| Dynamic Vehicle Traction in Floodwater | 43 | 34 | 25 | 1 |
| Simulation Ready Vehicle Mesh Assets | 36 | 21 | 25 | 1 |
| Optical Vehicle Collision Geometry | 23 | 20 | 5 | 2 |
| Quantitative MPM Wall Penetration | 16 | 14 | 2 | 1 |
| Trustworthy AI Assisted Scientific Simulation | 13 | 11 | 1 | 1 |

**1d. Varshney 2021 was never a new find, and it has a sibling.** The dispatch
says the corrected novelty statement "rests on Varshney 2021 alone". Varshney
2021 (`10.4271/2021-01-0205`) is already row 38 of
`docs/Dynamic_Vehicle_Traction_in_Floodwater.md`, a 43-paper catalog committed in
this repo. Row 37 of the same table is a second, uncounted Varshney paper:
`10.4271/2022-01-0768`, "Transient, 3D CFD, Moving Mesh Simulation of Vehicle
Water Wading in a Water Tunnel with Inclined Entry-Exit", 2022, which is a
**moving-mesh** wading simulation and therefore lands directly on the
moving-vehicle question. The unmined catalog was inside the repo, not in Elicit.

---

## 2. The real yield of the Elicit CSV: 11 rows, not 42

The two payload columns are populated in the sense of being non-empty in all 42
rows, but the overwhelming majority read `Not mentioned (the abstract does not
provide ...)`. The extraction is **abstract-level, not full-text**, and that is
the single most important property of this dataset.

Counting rows that carry an actual numeral and are not a "not mentioned" string:

| column | rows with a real value | denominator |
|---|---:|---:|
| `[08]` depth-velocity threshold or critical depth | 9 | 42 |
| `[09]` driving force or rolling friction coefficient | 9 | 42 |
| union of the two | **11** | **42** |

So the mineable corpus is 11 papers, not 42, and certainly not 1,345. Anyone
quoting this CSV must give the denominator 42 and the yield 11.

## 3. Every threshold the CSV actually reports

Full text in `data/r5_citation_thresholds.tsv`. Units as printed in the source.

| row | year | DOI | reported threshold |
|---:|---|---|---|
| 16 | 2018 | `10.1111/jfr3.12262` | small car `v*y <= 0.30`, large car `0.45`, large 4WD `0.60` m2/s |
| 35 | 2019 | `10.1111/jfr3.12551` | same three, plus depth caps `H <= 0.3/0.4/0.5` m at `V <= 3.0` m/s; and `H + V^2/2g <= 0.3` m passenger, `0.6` m rescue |
| 39 | 2023 | `10.1111/jfr3.12885` | critical depth `0.3` m small, `0.4` m large, `0.5` m 4WD; `0.35` m small in still water |
| 2 | 2022 | `10.1111/jfr3.12828` | `0.38` m critical depth, `0.39` m2/s, medium passenger vehicle |
| 37 | 2023 | `10.3390/su151713262` | `0.38` m critical depth, `0.36` m2/s, medium passenger vehicle |
| 38 | 2026 | `10.1111/jfr3.70181` | `0.45` m2/s, small passenger vehicle, unsteady flow |
| 5 | 2020 | `10.1111/jfr3.12645` | `0.60` m float depth; `< 0.70` m2/s small cars; `0.3` to `0.5` m still water; `0.10` to `0.20` m in high velocity |
| 26 | 2013 | `10.1007/s11069-013-0889-2` | incipient velocity `2.0` m/s (Honda Accord) and `4.3` m/s (Audi Q7) at `0.35` m; slope series `3.9/3.3/2.9` and `4.4/3.9/3.6` m/s |
| 7 | 2018 | `10.11113/JT.V80.11198` | `0.0168` m2/s at 0/360 deg, `0.0144` m2/s at 90/270 deg |

**Trap, row 7.** Those two values are roughly twenty times below every other
threshold in the table. They are almost certainly **model scale**, consistent
with the 1:10 scale already recorded in project memory for the Shah work. Do not
place `0.0168 m2/s` on the same axis as `0.30 m2/s` without resolving the scale
factor. This is UNVERIFIED here: I did not open the paper.

**Relevance to the project's own numbers.** The project's administrative cap is
3.0 m/s (CLAUDE.md L-2). Row 35 shows `V <= 3.0 m/s` appearing in the literature
as a **stated component of the stability criterion itself** for all three vehicle
classes. That is a much better provenance than "administrative", and it is worth
following into the primary source before the paper repeats the weaker claim.

## 4. Friction: the project's 0.55 has a measured source, and 0.3 does not

| row | year | DOI | reported friction | status as printed |
|---:|---|---|---|---|
| 39 | 2023 | `10.1111/jfr3.12885` | **0.55** | **measured** |
| 35 | 2019 | `10.1111/jfr3.12551` | 0.76 average, 0.52 to 0.62 range | experimental |
| 26 | 2013 | `10.1007/s11069-013-0889-2` | 0.25 parallel, 0.75 perpendicular | (unlabelled) |
| 16 | 2018 | `10.1111/jfr3.12262` | 0.3 assumed; 0.3 to 0.5; 0.26 to 0.65; 0.75 perp / 0.25 par | mixed, as listed |
| 2 | 2022 | `10.1111/jfr3.12828` | 0.3 | **assumed, not measured** |
| 7 | 2018 | `10.11113/JT.V80.11198` | 0.3 | **assumed, not measured** |
| 38 | 2026 | `10.1111/jfr3.70181` | 0.3 | **assumed, not measured** |
| 25 | 2025 | `10.1016/j.rineng.2025.107189` | 0.0250 and 0.0242 | measured |
| 40 | 1996 | `10.4271/961000` | up to 1.89 | measured, ATV tires |

Three findings.

**4a. `floor_friction = 0.55` now has a same-valued measured citation.** Row 39,
`10.1111/jfr3.12885`, reports a rolling friction coefficient of exactly 0.55,
tagged measured, and that DOI is **already cited in the repo, including the paper
bibliography** (25 files by the section 6 method, which excludes the catalog
files themselves; 26 if they are counted). The project has been carrying 0.55 while a paper
reporting 0.55 as measured was already in its own reference list. This
corroborates, and does not merely fail to contradict, the round-4 finding that
0.55 is not an outlier.

**4b. "0.3 was never measured" is now supported by three independent rows.**
Rows 2, 7 and 38 each carry the string "assumed not measured" against 0.3, and
row 16 lists 0.3 as assumed while listing three other ranges as measured. That is
convergent, and it strengthens the existing Bonham and Hattersley provenance
note.

**4c. Do not merge row 25 into this column. It is a different quantity.**
Nihei 2025 reports 0.0250 and 0.0242, an order of magnitude below everything else
here. Values near 0.02 are the standard **rolling resistance** coefficient of a
free-rolling tire; values from 0.25 to 0.76 are **sliding or limiting friction**
coefficients. The Elicit column header conflates them by asking for
"rolling friction coefficient" in one field. Averaging this column, or treating
0.025 as a low-end estimate for the project's Coulomb `coup_friction`, would be
a units error of the exact kind CLAUDE.md item 13 warns about: deduplicate by
name and unit, never by value. Tagged INFERRED from the magnitudes; I did not
open Nihei 2025 to confirm which quantity it reports.

## 5. Motion state, and what it does to L-1

Column `[11]`, counted programmatically over all 42 rows:

```
18  stationary
14  self-propelled
10  (unstated)
 0  towed
```

Zero rows were classified towed, even though the extraction schema offered the
category. (A regex for "tow" hits 37 rows, but only inside the reasoning column,
where it is echoing the question's own wording. It is not a classification.)

CLAUDE.md L-1 records that the AR&R and Shand thresholds describe a stationary
vehicle, and that the tank scenario is therefore the correct match. Nothing here
contradicts L-1. What this does show is that a third of this sample is
self-propelled work, so "the literature is stationary" is not a safe summary of
the field even though it is a correct statement about the specific thresholds
the project adopts. Caveat, and it matters: several self-propelled rows (30, 32,
33, 42) are fatality reviews and behavioural studies, not experiments. The count
of self-propelled **experiments or simulations** is smaller than 14 and I did not
finish separating them.

## 6. Cross-reference: 489 DOIs, 37 cited, 8 in the paper

`data/r5_citation_xref.tsv`. Method: one pass over 772 repo text files
(`.bib .tex .md .py .csv .json .txt .yaml .yml .cff`), excluding `.git`,
`third_party`, `renders`, `node_modules`, `.claude`, the Elicit source files, and
the two catalog files themselves so a catalog cannot count as its own citation.

```
unique DOIs across 14 catalogs plus both Elicit outputs : 489
  cited anywhere in the repo                            :  37   ( 7.6%)
  cited in paper/ overleaf_sync/ deliverables/          :   8   ( 1.6%)
  uncited anywhere                                      : 452   (92.4%)
```

## 7. The novelty statement is wrong by an order of magnitude

The dispatch asks me to confirm "five fording simulations, not four, unless you
find more". I found more. Filtering all 14 catalogs for titles carrying a vehicle
term **and** a water term gives 48 papers; of those, 15 carry an explicit
simulation or numerical term.

| year | DOI | paper | cited in repo |
|---|---|---|---|
| 2011 | `10.1016/j.envsoft.2011.02.017` | Numerical assessment of flood hazard risk to people and vehicles | no |
| 2015 | `10.1115/DETC2015-47142` | Coupled MBD and SPH for vehicle water fording (Wasfy) | no |
| 2018 | `10.1115/DETC2018-85006` | In-plane truck tire / flooded surface, FEA-SPH | no |
| 2020 | `10.1115/1.4047393` | Hydroplaning potential, coupled FE-CFD | no |
| 2021 | `10.4271/2021-01-0252` | Amphibious vehicle water egress, CFD | no |
| 2021 | `10.4271/2021-01-0205` | CFD water fording, passenger car (Varshney) | no |
| 2022 | `10.1111/jfr3.12828` | Passenger vehicles moving through floodwaters (Al-Qadami) | mention only |
| 2022 | `10.1016/j.oceaneng.2022.111607` | Coupled MBD-CFD, amphibious, surf zone | no |
| 2022 | `10.4271/2022-01-0768` | Transient 3D CFD moving-mesh water wading (Varshney) | no |
| 2023 | `10.3390/su151713262` | Passenger vehicle stability, 3D CFD (Al-Qadami) | **paper** |
| 2023 | `10.1007/s11433-023-2137-5` | **3D large-scale SPH modeling of vehicle wading, GPU accelerated** | no |
| 2024 | `10.1115/1.4064971` | Vehicle mobility in shallow water, data-driven hydrodynamics | mention only |
| 2024 | `10.1029/2023WR036739` | Full-process dynamics of floating vehicles in flash floods | **paper** |
| 2026 | `10.1115/1.4071177` | **Vehicle-water interaction, simulations and experimental validation** (He) | no |
| 2026 | `10.3390/app16073433` | Vehicle tire hydroplaning, numerical plus full-scale | no |

**Twelve of the fifteen are uncited anywhere in the repo. Two reach the paper.**

Two of these are pointed directly at the project's stated contribution.

- `10.1007/s11433-023-2137-5`, 2023, is a GPU-accelerated large-scale **particle
  method** simulation of **vehicle wading**. That is the same class of method on
  the same problem. It is uncited.
- `10.1115/1.4071177`, He et al. 2026, is titled "Simulations **and Experimental
  Validation**". CLAUDE.md L-7 records that the project's novelty is "the
  validation step, not the pipeline". A 2026 paper offering simulation plus
  experimental validation of vehicle-water interaction is the single most direct
  threat to that framing, and it is uncited. It was already sitting at row 2 of
  the repo's own `Dynamic_Vehicle_Traction_in_Floodwater.md`.

I am not claiming the contribution is dead. Any of these may differ in scenario,
scale or method once read. I am claiming that the sentence "four (or five)
vehicle fording simulations exist" cannot be written in the paper as it stands,
and that the novelty paragraph must be rewritten against at least these fifteen.

## 8. Verification status and what I did not close

Verified with `scholar-sidekick auditBibliography`, all 8 returned
`verdict=matched`, `confidence=high`, zero retracted:
`10.1007/s11433-023-2137-5`, `10.1115/1.4071177`, `10.1029/2023WR036739`,
`10.4271/2022-01-0768`, `10.4271/2021-01-0205`, `10.1016/j.rineng.2025.107189`,
`10.1111/jfr3.12885`, `10.1115/1.4064971`. One flag: Nihei 2025
(`10.1016/j.rineng.2025.107189`) returns `hasCorrections = true`. Resolve the
correction notice before quoting its 0.0250 / 0.0242 figures.

UNVERIFIED, and each needs a primary-source read:
1. Row 7's `0.0168 m2/s` scale factor. Model scale is inferred from magnitude.
2. Whether Nihei 2025's 0.025 is rolling resistance rather than limiting friction.
3. Whether `10.1007/s11433-023-2137-5` and `10.1115/1.4071177` genuinely overlap
   the contribution, which needs the full text of both.
4. How many of the 14 self-propelled rows are experiments rather than reviews.
5. The remaining 452 uncited DOIs are catalogued and cross-referenced, not read.
6. The five catalogs with two divergent sha256 copies: I used one copy per
   catalog, so a DOI present only in the other copy is not in the 472.

No physics number, force, distance or verdict count is asserted in this document,
so the physics-skeptic gate does not apply to it. Every simulation-derived
quantity referenced here belongs to an external paper, not to a project run.

## 9. Reproduce

```bash
cd /Users/josie/can-it-ford/.claude/worktrees/r5-research
python3 - <<'EOF'
import csv
p="/Users/josie/Downloads/can-it-ford-main/citations/Elicit - extract-results-review-5e368aae-95c3-4774-a804-2dcc8899299e.csv"
rows=list(csv.reader(open(p,newline='',encoding='utf-8-sig')))
print(len(rows)-1, "data rows", len(rows[0]), "columns")
EOF
sort -t$'\t' -k2,2 data/r5_citation_xref.tsv | head -20   # uncited first
```
