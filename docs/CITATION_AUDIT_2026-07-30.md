# Citation and Parameter Provenance Audit
## Live Overleaf paper, 2026-07-30. Read-only audit. No tex, no bib, nothing committed.

**Source of truth:** `git show overleaf/main:conference_101719_1.tex`
**Head audited:** `4e2fdbdf7d5bcdc0c792d447bdbda3af0f3ffc95` (2026-07-30 16:14:21 -0500)
**tex md5:** `99c697166afac5321ad7d73d2c16157c` (242 lines)
**bib md5:** `59a4251873d5733e0e7389a2f55a152c` (102 lines)

No local copy, memory file, or prior session note was used as evidence. Every row below
terminates in a live read: a `git show`, a CSV recompute, a mesh parse, a `pdftotext` of the
actual paper, or an HTTP response captured this session.

---

## STATUS COUNTS

| Status | Count |
|---|---|
| VERIFIED_PRIMARY | 10 |
| VERIFIED_SECONDARY | 3 |
| VERIFIED_INTERNAL | 42 |
| KNOWN_BAD | 4 |
| CONTRADICTED (bib metadata vs Crossref) | 2 |
| UNCITED | 6 |
| NEEDS_LITERATURE | 6 |
| UNVERIFIABLE | 2 |
| PROVENANCE_MISSING (figures) | 2 |

**Headline:** every number the paper draws from project data reproduces exactly, all 42 of
them. Zero `[?]` citations. The failures are all in the citation layer and in two figures
that have no generator.

---

## PHASE 0: TOOL AND SOURCE INVENTORY

### Available and used
| Tool | State |
|---|---|
| `git` / overleaf remote | Connected, fetched live this session |
| api.crossref.org | HTTP 200, 5 DOIs resolved |
| api.openalex.org | HTTP 200 on test DOI |
| api.unpaywall.org | HTTP 200, 3 DOIs queried |
| api.datacite.org | HTTP 200, resolved the NCAC Yaris DOI |
| `/provenance-audit` skill | Loaded. Known-Error Register applied |
| `/geoelements-tech-reference` skill | Present at `~/.claude/skills/`, not loaded (not needed) |
| zotero MCP | Responds. **My Library, 37 items, 25 PDFs in `~/Zotero/storage`** |
| `pdftotext` (poppler) | Available at `/opt/homebrew/bin/pdftotext`, used for all PDF reads |

### Not available (stated plainly, not simulated)
| Tool | State |
|---|---|
| `numpy`, `trimesh`, `pymupdf`, `pdfminer` | **Not installed.** Mesh volume computed instead with a pure-Python binary-PLY parser and the divergence theorem |
| Scite, Consensus, Elicit, PubMed, Wolfram | Not invoked. Items needing them are in `LIT_QUEUE_2026-07-30.md` |
| Wiley full text | **Cloudflare bot-challenge, HTTP 403.** Not bypassed (bot-detection bypass is out of bounds) |

### PDFs matching the named authors

**Present** (`~/Zotero/storage`): Azhar 2023, Xie PhysGaussian 2024, Kerbl 3DGS 2023,
Thorpe PVWM 2026 (x2), Hsiao and Kumar 2025 (x2), Xiong 2024 (x2), Shah 2018,
Kumar and Vantassel GNS 2022, Malone FRED 2026, Sanchez-Gonzalez 2020, Albano 2016,
Amicarelli 2015, Kovacic and Ellis 2026, Liu 2026, Zhao 2025, Bansal 2024, Rahnemoonfar 2020,
Lindemann 2025.

**Present** (repo): `citations/ARR_Project_10_Stage2_Report_Final.pdf`. Confirmed this
session to be the **vehicles** report, not the people report: title page reads
"PROJECT 10 / Appropriate Safety Criteria for Vehicles / Literature Review / STAGE 2 REPORT /
P10/S2/020 / FEBRUARY 2011".

**Absent:** Smith Modra Felder 2019, Heydinger SAE 1999-01-1336, Luo, the NCAC/CCSA Yaris
validation report. Shand is present only as the AR&R report above (no separate Shand paper).

---

## PHASE 1: CLAIM EXTRACTION FROM LIVE SOURCE

### 1A. Every `\cite` key, with line numbers

9 unique keys, 20 total uses. All 9 resolve in `overleaf/main`'s bib. **No key renders as `[?]`.**

| Key | Uses | Lines | Sentence it supports |
|---|---|---|---|
| `shand2011arr` | 7 | 78, 84, 89, 96, 124, 137, 146 | AR&R `H = D x V` hazard scalar and class thresholds; Small Car 0.30 m depth cap; the three AR&R classes |
| `nws_tadd` | 4 | 58, 84, 89, 123 | Flooded roads as leading US flood-death cause; L0 fixed depth cutoff approx 0.15 m |
| `thorpe2026pvwm` | 3 | 60 (x2), 101 | PVWM preserves latent physics; abstraction selection is a central open problem; orchestrator left unimplemented; auditability |
| `xie2023physgaussian` | 1 | 81 | Gaussian kernel covariance seeds a continuum MPM particle volume |
| `smithmodrafelder2019` | 1 | 78 | "report full-scale flotation and sliding stability curves derived from physical vehicle testing" |
| `kerbl20233dgs` | 1 | 80 | 3DGS reconstructs a photorealistic explicit scene from multi-view video |
| `hsiao2025nerfmpm` | 1 | 101 | NeRF plus Bayesian optimization recovers friction angle to within roughly two degrees |
| `heydinger1999sae` | 1 | 142 | sedan/SUV/pickup bounding-box dimensions from "NHTSA/SAE reference data" |
| `genesis2024` | 1 | 81 | Genesis is an open-source solver-agnostic physics engine |

**Specifically checked as requested:**
- `shand2011` does **not** appear anywhere in the tex. Only `shand2011arr` is used, and it is
  defined in the bib. **No mismatch. No `[?]`.**
- `hsiaokumar2025` does **not** appear anywhere. Only `hsiao2025nerfmpm` is used, and it is
  defined. **No mismatch. No `[?]`.**

### 1B. Every numeric value in body, captions, and tables

Classification key: (i) simulation output, (ii) physical parameter input,
(iii) literature-derived threshold, (iv) geometric/mesh property, (v) count.

Full recomputation results are in Phase 2.4. All 42 reproduce. Type breakdown:

| Type | Examples | Status |
|---|---|---|
| (i) simulation output | 0.658537 / 0.314076 / ... m displacements; 15.8807% passthrough; mu-sweep 0.399 / 0.3957 / 0.3953 / 0.3283 m | VERIFIED_INTERNAL |
| (ii) physical parameter input | mass 1100 / 1609 / 2337 kg; floor friction 0.55; depth 0.30 m; velocity 1.5 m/s | VERIFIED_INTERNAL (0.55 is UNCITED, see U1) |
| (iii) literature-derived threshold | D x V caps 0.30 / 0.45 / 0.60 m2/s; depth cap 0.30 m; L0 approx 0.15 m | VERIFIED_PRIMARY except L0, see **N1** |
| (iv) geometric / mesh property | hull 3.542739 m3; prism 10.7457 m3; fill 0.33; 191,107 points | hull VERIFIED, prism see **N2** |
| (v) counts | 17 runs; 70 scenarios; 37 / 14 / 23 / 5 / 10 / 8 / 7; 9 conditions; 5 of 9; 0 of 60 | VERIFIED_INTERNAL |

### 1C. Every figure, with generator status

| Figure | Line | Kind | Generator | Format on disk | Status |
|---|---|---|---|---|---|
| `pipeline_diagram_v2.pdf` | 66 | Conceptual diagram | `analysis/paper_fig_pipeline_diagram_v2.py` | PDF 1.7 | OK |
| `l0l1_two_rules_v2.pdf` | 88 | Formula evaluation | `analysis/paper_fig_l0l1_two_rules_v2.py` | PDF 1.7 | OK |
| `L1_three_class_corrected.png` | 95 | Formula evaluation | **NONE** | **JPEG named .png** | **PROVENANCE_MISSING** |
| `force_balance.png` | 136 | Analytical force balance | **NONE** | **JPEG named .png** | **PROVENANCE_MISSING** |
| `l2_divergence_real_v2.pdf` | 183 | Simulation output (9-pt SPH) | `analysis/paper_fig_l2_divergence_v2.py` | PDF 1.7 | OK |
| `mass_grid_sweep_v2.pdf` | 196 | Simulation output (17-run MPM) | `analysis/paper_fig_mass_grid_sweep_v2.py` | PDF 1.7 | OK |

See **N3** and **N4**.

### 1D. Literature-style assertions carrying NO `\cite`

See the UNCITED section (U1 to U6).

---

## PHASE 2: INTERNAL CONSISTENCY

### 2.1 Unresolved cite keys
**None.** 9 keys used, 9 defined. No `[?]` will render.

### 2.2 Bib entries never cited
Three, all live in the file and all carrying `VERIFY:` placeholders:
- `azhar2023` (see **K3**)
- `xiong2024`
- `fred2026`

They do not render (IEEEtran emits only cited entries), so they are not a display defect.
They are a correctness hazard only if someone later cites them as-is.

### 2.3 `\ref` / `\label`
14 labels defined, 11 referenced, all 11 resolve. Three labels are defined but never
referenced: `sec:prior`, `sec:conclusions`, `sec:future`. Harmless (section anchors).
**No dangling `\ref`.**

### 2.4 Every data-derived number, recomputed live

**`data/all_runs_inventory.csv`** (17 data rows + header)

| Paper claim | Recomputed | Match |
|---|---|---|
| 17 runs | 17 | YES |
| 3x3 mass-by-resolution block, 9 runs | `mass_grid` = 9 | YES |
| masses 1100 / 1609 / 2337 kg | `['1100.0','1609.0','2337.0']` | YES |
| n_grid 48 / 64 / 96 | `['48','64','96']` | YES |
| fixed depth 0.30 m, velocity 1.5 m/s | `['0.3']`, `['1.5']` | YES |
| three-point depth sweep | 3 rows, depths 0.25 / 0.35 / 0.45 at n_grid 64 | YES |
| five-point velocity sweep | 5 rows, v 0.5 / 1.0 / 2.0 / 2.5 / 3.0 at n_grid 64 | YES |
| three layers coarsest to six finest | water_layers = {3, 4, 6} | YES |
| 7 of 17 exceed 10% passthrough | 7 | YES |
| reaching 15.9% at 3.0 m/s | 0.158807 = 15.8807% at v=3.0, run `sweepV_g64_v3p0` | YES |
| floor friction uniform 0.55 across all 17 | single distinct value `0.55` | YES |
| real hull 3.5427 m3 | `hull_m3` single distinct value `3.542739` | YES |

**`data/scenario_sweep.csv`** (70 data rows + header)

| Paper claim | Recomputed | Match |
|---|---|---|
| all 70 (depth, velocity) scenarios | 70 rows, 70 unique pairs | YES |
| bare rule permits 37 of 70 | 37 | YES |
| 30 of them where L0 would refuse | 30 | YES |
| joint rule permits 14 of 70 | 14 | YES |
| only 7 of them beyond L0 | 7 | YES |
| 23 reclassify FORD to NO-FORD | 23 | YES |
| none reclassify the opposite direction | 0 | YES |
| 5 hazard-cap only | 5 | YES |
| 10 depth-cap only | 10 | YES |
| 8 by both | 8 | YES |
| 7 are standing water at zero velocity | 7 | YES |
| at depths 0.40 to 1.00 m | 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 | YES |
| `L1_verdict` identical to `L1_verdict_small_passenger` on all 70 | True | YES |

**`data/l2_results_from_wandb.csv`** (9 rows)

| Paper claim | Recomputed | Match |
|---|---|---|
| 9 unique (depth, velocity) conditions | 9 | YES |
| agreement 5 of 9 (55.6%) | 5 of 9 | YES |
| 3 both-FORD, 2 both-NO-FORD | 3 and 2 | YES |
| 4 divergences, all L1-permits / L2-refuses | 4, all one direction, 0 reverse | YES |
| divergence points (0.30, 1.5), (0.15, 1.5), (0.30, 1.0), (0.30, 2.0) | exactly those four | YES |
| one flagged cell where `l1_haz_score` disagrees with its own D x V | exactly one: row `L2_d0.3_v1.5`, `dv_product`=0.45 vs `l1_haz_score`=0.75 | YES |

**`data/mu_sweep_results.csv`** (4 rows)

| Paper claim | File | Match |
|---|---|---|
| 0.399, 0.3957, 0.3953 m at mu = 0.3, 0.5, 0.7 | 0.399, 0.3957, 0.3953 | YES |
| 0.3283 m at mu = 0.0 | 0.3283 | YES |
| column is *coupling* friction | column header is `coup_friction` | YES, and the paper correctly says "coupling friction", not Coulomb friction |

**`data/phase_space_results.csv`** (31 rows)

| Paper claim | Recomputed | Match |
|---|---|---|
| 23 unique (depth, velocity) pairs | 23 | YES |
| 15 of its 31 rows share a condition | 15 | YES |
| three separate (0.30, 1.5) runs | count = 3 | YES |

**Mesh and geometry** (pure-Python PLY parse, divergence theorem)

| Paper claim | Recomputed | Match |
|---|---|---|
| `truck_trimmed.ply`, 191,107 points, no interior | header: `element vertex 191107`, no `element face`, carries `f_dc_*`/`f_rest_*` splat attributes | YES |
| real hull encloses 3.5427 m3 | 3.542739 m3 | YES |
| Yaris mass 1100 kg | `vehicle_params.py:83` `"mass_kg": 1100.0` | YES |
| vehicle weight 10.79 kN | 1100 x 9.81 = 10791 N | YES |
| **10.7457 m3 bounding-box prism** | **mesh bbox = 4.282610 x 1.746378 x 1.518008 = 11.353268 m3** | **NO, see N2** |
| **fill factor 0.33** | **3.542739 / 11.353268 = 0.3120** | **NO, see N2** |

Mesh also confirmed: 327,212 vertices, 655,308 faces, all triangles.

**Hollow-vehicle diagnosis** (`docs/track1_v3_sweep_invalid_hollow_vehicle.md`)

| Paper claim | Source | Match |
|---|---|---|
| job 833349, `--config v3`, July 15 2026 | "Job 833349, partition gh, node c611-132. State COMPLETED, ExitCode 0:0" | YES |
| particle count scaled 4.31x not 8x | "Particle scaling is 4.31x, not 8x ... 9,216 particles at h=0.08009; n_grid=128 -> 39,738" | YES |
| 0 of 60 passed density plausibility | "density_plausible True: 0/60" | YES |
| all three roughly doubled, 1.84 to 1.87x | 1.86 / 1.87 / 1.84 | YES |
| Sedan 293.55, Pickup 242.12, SUV 308.13 kg/m3 | table rows 35 to 37 | YES |
| SUV 2.7% over the band | 308.13 / 300 = 2.71% over | YES |
| superseded 36-run sweep, 1390 kg box, 4.7352 m3 | `CLAUDE.md:69`, and doc table sedan row `1390.0 | 4.7352` | YES |

### 2.5 Paper parameters vs the code that produced the results

| Parameter | Paper | Code / data | Verdict |
|---|---|---|---|
| Floor friction | 0.55, uniform, all 17 runs | `renders/yaris_render_s1/sim_standing.py:76` default `floor_friction=0.55`; inventory column single-valued `0.55` | MATCH |
| Mass overrides | 1100 / 1609 / 2337 kg mapped to small_passenger / large_passenger / large_4wd | `gates_both_scenarios.py:18-23` exactly those triples with exactly those labels | MATCH |
| Vehicle mass | 1100 kg from LS-DYNA deck header "Version 1l, 1100 kg" | `vehicle_params.py:82-83` same string, same value | MATCH |
| L0 depth cutoff | approx 0.15 m | `analysis/make_poster_figures.py:30` `L0_DEPTH_M = 0.15`; `four_rung_ladder.py:9` same. Data: L0 cutoff lies in (0.10, 0.20] m | MATCH to code, **but see N1 for the citation** |

**One inconsistency worth knowing, not an error in the paper:**
`renders/yaris_render_s1/vehicle_live.py:343` defaults `floor_friction=0.5`, while
`sim_standing.py:76` defaults `0.55`. The 17-run inventory records `0.55` on every row, so
the paper's statement is correct for what was actually run. The 0.5 default is a latent trap
for any future run launched through `vehicle_live.py`.

---

## PHASE 3: LOCAL AND OPEN-SOURCE VERIFICATION

### VERIFIED_PRIMARY

**P1. `shand2011arr` bibliographic metadata.**
Read live from `citations/ARR_Project_10_Stage2_Report_Final.pdf`.
Title page: "Australian Rainfall & Runoff Revision Projects / PROJECT 10 / Appropriate Safety
Criteria for Vehicles / Literature Review / STAGE 2 REPORT / P10/S2/020 / FEBRUARY 2011".
Authors page: "T D Shand", "R J Cox", "M J Blacka", "G P Smith".
Bib entry matches on author list, title, number, institution, and year. **Accurate.**

**P2. AR&R class thresholds.**
Same PDF, page 24 (Table 3, "Proposed DRAFT Stability Criteria for Stationary Vehicles"):
"DV <= 0.3", "DV <= 0.45", "DV <= 0.6", against classes "Small passenger", "Large passenger",
"Large 4WD". The paper's 0.30 / 0.45 / 0.60 m2/s and its Small Car 0.30 m depth cap match.
The bib's note that the criteria are labeled draft is confirmed by the table title itself.

**P3. `thorpe2026pvwm`, abstraction selection is the central open problem.**
`~/Zotero/storage/ND8PGIDC/...pdf`:
> "This construction is useful only if the abstraction and components can be selected
> automatically, which remains the central open problem."

and in the open-problems section:
> "autonomous orchestration remains an open research problem."

The paper's line 60 claim is exact. **Accurate.**

**P4. `hsiao2025nerfmpm`, friction angle within two degrees.**
`~/Zotero/storage/FL7N6U4C/...pdf`, abstract:
> "friction angle can be estimated with an error within 2 degrees"

and in results: "angles remained within 2 degrees of ground truth across multiple test
cases", with per-case mean absolute errors of 0.64 to 1.38 degrees.
The paper's "to within roughly two degrees of ground truth" is exact. **Accurate.**

**P5. `xie2023physgaussian`, Gaussians as continuum discretization.**
`~/Zotero/storage/IH89VU97/...pdf`: "These Gaussians are viewed as the discretization of the
scene to be simulated", and "through continuum mechanics principles and a custom Material
Point [Method]". The paper's line 81 claim is supported. **Accurate.**

**P6. `heydinger1999sae` bibliographic metadata.**
Crossref `10.4271/1999-01-1336`: authors Heydinger, Bixel, Garrott, Pyne, Howe, Guenther;
title "Measured Vehicle Inertial Parameters-NHTSA's Data Through November 1998"; SAE
International; 1999. The bib entry matches field for field. Crossref types it
`proceedings-article` while the bib uses `@techreport`; cosmetic only.
**The metadata is right. The use of it is not, see K2.**

**P7. `azhar2023` correct identity (Phase 4 confirmation, not re-derivation).**
Crossref `10.1111/jfr3.12885`: first author **Fatima Azhar**, with Pauwels and Bui; title
"Confirmation of vehicle stability criteria through a combination of smoothed particle
hydrodynamics and laboratory measurements"; JFRM 16(2), 2023.
Matches the Phase 4 specification exactly.

**P8. Azhar's 0.55 is a physical tyre-road Coulomb coefficient.**
`~/Zotero/storage/6Y7VPLP7/...pdf`:
> "rubber tyres on a wet asphalt surface have a coefficient of friction ranging from 0.50 to
> 0.70. In this experiment, a rubber mat has been used as a representative of the road
> surface with a wet coefficient of friction of 0.55."

and the results compare "SPH Model (mu = 0.30)", "SPH model (mu = 0.55)", "SPH Model
(mu = 0.78)". The 0.30 to 0.55 range in the bib note is real, and it is unambiguously a
physical tyre-on-road coefficient. This confirms the Phase 4 guard rather than re-testing it.

### VERIFIED_SECONDARY

**S1. `kerbl20233dgs`.** Standard, uncontroversial characterization of 3DGS. PDF is present in
Zotero; the claim was not separately quote-checked because nothing in the paper depends on a
specific 3DGS number.

**S2. `genesis2024`.** The bib note claims no peer-reviewed paper existed as of July 16 2026.
Not re-checked this session. Citing project-maintainer-specified format for software is
standard practice.

**S3. `nws_tadd` for the death-cause claim.** Live fetch of
`https://www.weather.gov/safety/flood-turn-around-dont-drown` (HTTP 200) returns:
> "Each year, more deaths occur due to flooding than from any other thunderstorm related
> hazard. The Centers for Disease Control and Prevention report that over half of all
> flood-related drownings occur when a vehicle is driven into hazardous flood water."

The paper's line 58 ("Flooded roads kill more people in the United States each year than any
other flood-related hazard") is *defensible* from the "over half of all flood-related
drownings" sentence, but it fuses two distinct NWS statements. NWS's "more deaths than any
other" claim is scoped to **thunderstorm-related** hazards, not flood-related ones.
Recommend tightening the sentence to track the CDC "over half" figure directly.
**The threshold citation on the same source is a different matter, see N1.**

---

## PHASE 4: KNOWN-BAD GUARD, RESULTS

### K1. Smith-Modra-Felder Eq. 6 attributed to a displacement criterion. **LIVE ERROR.**

`conference_101719_1.tex` line 125, inside Table I (`tab:ladder`), the L2 row:

> `\FLAG{Threshold currently 0.05\,m with no independent citation; being reframed relative to`
> `Smith-Modra-Felder (2019) Eq.~6.}`

This is the exact attribution Phase 4 prohibits. That equation is a limiting Froude number
relation, not a lateral-displacement criterion, and no peer-reviewed flood-vehicle source
defines instability by an absolute drift distance near 0.05 m.

**Aggravating detail:** this text sits inside `\FLAG{}`, which is defined at line 16 as
`\textcolor{red}{...}`. It therefore **renders in red in the compiled PDF**. The false
attribution is currently visible to any reader of the built paper, not hidden in a comment.

**Root-cause conflation (Known-Error Register, row 2):** "there must be a paper for this" led
to attaching a plausible equation number to an internally chosen numerical detector.

**Correct reframing:** 0.05 m is an internal numerical onset-of-motion detector. Xia et al.
2014 and Shah et al. 2018 can be cited for the underlying sliding physics, not for the number.

### K2. SAE 1999-01-1336 cited as a matched sedan/SUV/pickup parameter set. **LIVE ERROR.**

`conference_101719_1.tex` line 142:

> "Three vehicle classes (sedan, SUV, pickup) are each a single rescaled base silhouette
> stretched to that class's real bounding-box dimensions from NHTSA/SAE reference data
> `\cite{heydinger1999sae}`."

Phase 4 prohibits exactly this. The project's own `vehicle_params.py:93-94` states the reason
in its own comment:

> "the measured NHTSA inertial DB (SAE 1999-01-1336) ends Nov 1998 and has no Yaris."

The ledger's Section F2 is consistent: the sedan/SUV/pickup rows are Corolla/Civic,
Highlander/Explorer, and F-150/Tacoma anchors, described there as "measured masses,
footprints, and inertia tensors ... **not** meshes", and the class rows are project-assembled
representative values, not a matched triple published by Heydinger et al.

Line 96 (Fig. `fig:threeclass` caption) repeats the framing ("the sedan/SUV/pickup NHTSA/SAE
classes"), so the fix has two sites.

### K3. Azhar bib entry, reported verbatim as required.

Live entry in `overleaf/main:can_it_ford_references_IEEE.bib`, lines 54 to 61, verbatim:

```bibtex
@article{azhar2023,
  author  = {Azhar, {\relax and others}},
  title   = {{VERIFY: exact title}},
  journal = {Journal of Flood Risk Management},
  doi     = {10.1111/jfr3.12885},
  year    = {2023},
  note    = {VERIFY: confirm full citation before submission. Used as the source for coup\_friction / physical friction coefficient (mu approx 0.3-0.55).}
}
```

Two defects against the Phase 4 specification:
1. `author` is the placeholder `{Azhar, {\relax and others}}`, not **F. Azhar**.
2. `title` is the literal string `VERIFY: exact title`, not the real title.

Crossref supplies both correctly (see P7). The entry is **uncited**, so it does not currently
render. It is a loaded gun, not a live misfire.

Also note the `note` field asserts Azhar is "Used as the source for coup_friction". Per Phase 4
and confirmed at P8, Genesis/mpm-engine coupling friction is not Azhar's tyre-road Coulomb
coefficient. See **N6**.

### K4. NCAC/CCSA Yaris deck, DOI 10.13021/G8JS5D. **NOT CITED ANYWHERE.**

Searched the full tex and bib: the DOI does not appear, and no bib entry exists for it.

This is the canonical vehicle for every result in Section IV-C (the 17-run sweep) and for
Table II's replacement asset. The paper leans on it three times without a citation:
- line 146: "A crash-validated, watertight 2010 Toyota Yaris hull ... mass 1100 kg from the
  LS-DYNA deck header"
- line 218 (Future Work): "NHTSA/NCAC publishes free, government-funded, crash-validated
  finite-element vehicle models (e.g., a 2010 Toyota Yaris sedan ...)"
- `vehicle_params.py:75-76` sources the whole `compact_sedan` block to it.

**The DOI resolves.** DataCite, HTTP 200:
- Title: "2010 Toyota Yaris Finite Element Model Validation Coarse Mesh"
- Creator: "Center For Collision Safety And Analysis"
- Publisher: George Mason University, 2016
- URL: `https://www.ccsa.gmu.edu/wp-content/uploads/2016/11/2010-toyota-yaris-coarse-validation-v1.pdf`

It is Crossref-404 because it is a DataCite DOI. There is no obstacle to citing it.

---

## NEW FINDINGS (not in the Phase 4 register)

### N1. The L0 0.15 m threshold is sourced to NWS's **pedestrian** figure. **HIGH SEVERITY.**

Table I, line 123: "L0 & Depth & Fixed depth cutoff ($\approx$0.15\,m `\cite{nws_tadd}`)".

Live fetch of the cited NWS page returns two depth figures, and they are about different things:
> "A mere **6 inches** of fast-moving flood water can knock over **an adult**. It takes just
> **12 inches** of rushing water to **carry away most cars** and just 2 feet of rushing water
> can carry away SUVs and trucks."

- 6 in = 0.1524 m. This is the figure for **knocking over a person**.
- 12 in = 0.3048 m. This is the figure for **vehicles**, which is what L0 models.

The paper's vehicle depth cutoff of approx 0.15 m therefore cites a NWS statement about
pedestrians. The code carries the same attribution: `analysis/make_poster_figures.py:249`
labels the rung `"L0  static depth\n(NWS 0.15 m)"`.

Confirmed against the data: `scenario_sweep.csv` L0 verdicts flip between 0.10 m and 0.20 m,
consistent with a 0.15 m cutoff being the one actually applied.

This is structurally the same error as K1: a real number from a real source, attached to the
wrong quantity. It also matters materially, because L0 being "markedly over-conservative"
(line 84) is partly an artifact of using a pedestrian threshold to judge cars. At the NWS
vehicle figure of 0.30 m, L0 would permit 21 of 70 scenarios rather than 7.

### N2. The 10.7457 m3 prism is spec dimensions, not the mesh's bounding box.

Fig. 4 caption, line 137:
> "The real hull encloses 3.5427 m3 against a 10.7457 m3 bounding-box prism, a fill factor of
> only 0.33"

- 3.542739 m3 is genuinely the mesh volume. Confirmed by direct parse.
- **10.7457 m3 is not the mesh's bounding box.** It is `vehicle_params.py:89`
  `"bbox_m": (4.30, 1.70, 1.47)`, and 4.30 x 1.70 x 1.47 = 10.7457 exactly.
- The **actual** mesh bounding box is 4.282610 x 1.746378 x 1.518008 = **11.353268 m3**.
- True fill factor is **0.312**, not 0.33.

The sentence reads as though both numbers describe the same object. One is measured from the
hull, the other is a rounded nominal spec. `vehicle_params.py:87-88` even records a third set
("raw 4.299 x 1.696 x 1.468 m") that matches neither. Width and height each differ from the
live mesh by about 0.05 m, plausibly the watertight-solidify step inflating the hull, but that
is a hypothesis and is not verified.

Not fatal (the caption's own numbers are self-consistent, 3.542739/10.7457 = 0.3297), but it
is a mixed-provenance figure presented as a single measurement.

### N3. `force_balance.png` has no generator and is a JPEG.

- **No generating script exists.** Searched every `.py`, `.md`, `.sh` in the repo. The string
  `force_balance` appears only in the tex files, a handoff note, and `POSTER_ASSET_TABLE.md`.
  Nothing produces it.
- `file` on the blob from `overleaf/main` reports **"JPEG image data, JFIF standard 1.02"**
  despite the `.png` extension.

Consequences: the caption's 15.99 kN buoyant force, 10.79 kN weight, 0.19 m critical-velocity
zero-crossing, and "roughly three quarters of its bounding-box footprint" cannot be
reproduced or corrected. I could confirm 10.79 kN independently (1100 x 9.81). I could not
reproduce 15.99 kN from either bounding box: it implies an effective waterplane area of
5.433 m2, which is 0.743 of the spec footprint (7.31 m2) or 0.726 of the mesh footprint
(7.479 m2). Both are "roughly three quarters", so the caption is not wrong, but the exact
figure is untraceable. The paper's own line 132 FLAG asks for precisely this and cannot be
answered without the script.

### N4. `L1_three_class_corrected.png` has no generator and is a JPEG.

`analysis/plot_l1_three_class.py` exists, but line 230 writes
`figures/fig1_l1_three_class.pdf`, and line 222 forces `format="pdf"`. It does not produce
`L1_three_class_corrected.png`, by name or by format. The Overleaf file is again
**JPEG data with a `.png` extension**.

### N5. "no class-mapping needed" overstates the AR&R match.

Line 190: "masses 1100/1609/2337 kg directly matching AR&R's small passenger/large
passenger/large 4WD classes, no class-mapping needed".

AR&R Table 3 (read at primary source, P2) defines classes on **four** attributes, not one:
kerb weight, length, ground clearance, and the DV equation. Against the measured hull:

| AR&R class | Kerb weight | Length | Hull at that mass |
|---|---|---|---|
| Small passenger | < 1250 kg | < 4.3 m | 1100 kg PASS, 4.2826 m PASS |
| Large passenger | > 1250 kg | > 4.3 m | 1609 kg PASS, 4.2826 m **FAIL** |
| Large 4WD | > 2000 kg | > 4.5 m | 2337 kg PASS, 4.2826 m **FAIL** |

The mass override changes mass only. The geometry stays a 4.2826 m subcompact, which fails the
length criterion for both upper classes. The ledger's own A1 flags that AR&R gives no
tie-break rule when attributes disagree. The method is defensible as a controlled
mass-sensitivity study on one hull; "no class-mapping needed" is the part that is not.

**Side benefit: this settles ledger flag A5/D4.** A5 recorded the hull length as contested
(4.2826 m in the ledger vs 4.30 m in `paper_draft.md`, a 1.7 cm margin that "decides the
class") and asked for a direct bbox measurement. Measured live this session:
**4.282610 m**. The ledger figure is correct, `paper_draft.md` is not, and the hull is Small
passenger by length.

### N6. Floor friction 0.55 is uncited and numerically identical to Azhar's physical value.

Line 190: "Floor friction is held uniform at 0.55 across all 17 runs." No citation.

The value in code is `sim_standing.py:76` `floor_friction=0.55`, passed to
`s.add_plane(..., "slip", friction=floor_friction, ...)`. That is a solver boundary-plane
friction parameter. Azhar's 0.55 is a measured rubber-on-wet-asphalt Coulomb coefficient
(P8). They are numerically equal and physically different, and the bib note for `azhar2023`
explicitly claims Azhar is the source for it.

Right now this is **safe in the rendered paper**, because `azhar2023` is never cited, so no
false attribution appears. It becomes a Phase 4 violation the moment anyone resolves the
`\FLAG` at line 132 by adding `\cite{azhar2023}`. Flagging pre-emptively: the correct move is
to state 0.55 as a chosen modeling assumption informed by Azhar's measured range, not as a
cited parameter.

---

## CONTRADICTED: bib metadata vs Crossref

### C1 and C2. `smithmodrafelder2019` has two wrong fields.

Crossref `10.1111/jfr3.12527`, live, HTTP 200:

| Field | Bib entry | Crossref (authoritative) | Verdict |
|---|---|---|---|
| author 2 | `Modra, Brianna D.` | **Modra, Benjamin D.** | **WRONG given name** |
| title | `Full-Scale Testing of Vehicle Floatation and Stability in Flowing Floodwater` | **Full-scale testing of stability curves for vehicles in flood waters** | **WRONG title** |
| author 1 | Smith, Grantley P. | Smith, Grantley P. | OK |
| author 3 | Felder, Stefan | Felder, Stefan | OK |
| journal | Journal of Flood Risk Management | Journal of Flood Risk Management | OK |
| year | 2019 | 2019 | OK |
| vol/issue | absent | 12(S2) | missing, not wrong |

Both errors will print in the reference list as written. No retraction, correction, or
`update-to` relation is recorded on the DOI.

The *claim* the paper attaches to this citation (line 78, "report full-scale flotation and
sliding stability curves derived from physical vehicle testing") is consistent with the true
title and is treated as VERIFIED_SECONDARY: the full text is Cloudflare-blocked, so the
specific curves were not read.

### Other bib entries checked against Crossref

| Entry | Crossref | Verdict |
|---|---|---|
| `heydinger1999sae` | exact match on all fields | OK (metadata), see K2 for the use |
| `xiong2024` | Xiong, Liang, Zheng, Wang, Tong; "Simulation of the Full-Process Dynamics of Floating Vehicles Driven by Flash Floods"; WRR 60(10) 2024 | Bib has correct journal/year/DOI but placeholder author and title. **Uncited**, so it does not render. PDF is in Zotero if it is ever needed |
| `azhar2023` | see K3 | placeholder, uncited |
| No retractions, corrections, or `update-to` relations on any resolved DOI | | clean |

---

## UNCITED (asserted with no source)

| ID | Location | Assertion | Note |
|---|---|---|---|
| U1 | line 190 | "Floor friction is held uniform at 0.55 across all 17 runs" | See N6. Needs to be framed as a modeling assumption |
| U2 | line 146 | "crash-validated, watertight 2010 Toyota Yaris hull ... mass 1100 kg from the LS-DYNA deck header" | See K4. DOI 10.13021/G8JS5D resolves and is citable today |
| U3 | line 218 | "NHTSA/NCAC publishes free, government-funded, crash-validated finite-element vehicle models (e.g., a 2010 Toyota Yaris sedan and a 2007 Chevrolet Silverado pickup)" | Same source as U2 |
| U4 | Table II, line 154 | "In heuristic band?" with an implicit 100 to 300 kg/m3 band | The band is a project heuristic from `CLAUDE.md`, not a literature value. The 2.7% arithmetic is correct (308.13/300 = 2.71%) but the band itself has no source |
| U5 | line 132 (self-flagged) | The drag-force equation behind Fig. 4 | The paper's own FLAG requests this. Unanswerable while N3 stands |
| U6 | line 137 (self-flagged) | "measured critical flow depth of about 0.38 m for a full-scale passenger vehicle" | **Correctly handled.** Explicitly not cited and explicitly flagged as an unverified placeholder. Listed for completeness, not as a defect |

---

## FULL STATUS TABLE

| # | Item | Status |
|---|---|---|
| 1 | `shand2011arr` metadata | VERIFIED_PRIMARY |
| 2 | AR&R DV caps 0.30/0.45/0.60 | VERIFIED_PRIMARY |
| 3 | AR&R Small Car 0.30 m depth cap | VERIFIED_PRIMARY |
| 4 | AR&R criteria are "draft" | VERIFIED_PRIMARY |
| 5 | `thorpe2026pvwm` abstraction selection open problem | VERIFIED_PRIMARY |
| 6 | `thorpe2026pvwm` orchestrator unimplemented | VERIFIED_PRIMARY |
| 7 | `hsiao2025nerfmpm` 2-degree friction angle | VERIFIED_PRIMARY |
| 8 | `xie2023physgaussian` continuum discretization | VERIFIED_PRIMARY |
| 9 | `heydinger1999sae` metadata | VERIFIED_PRIMARY |
| 10 | Azhar identity + 0.55 as physical Coulomb | VERIFIED_PRIMARY |
| 11 | `kerbl20233dgs` claim | VERIFIED_SECONDARY |
| 12 | `genesis2024` no peer-reviewed paper | VERIFIED_SECONDARY |
| 13 | `nws_tadd` death-cause claim | VERIFIED_SECONDARY |
| 14-55 | All 42 project-data numbers (Phase 2.4) | VERIFIED_INTERNAL |
| 56 | Smith-Modra-Felder Eq. 6 drift attribution | **KNOWN_BAD** |
| 57 | SAE 1999-01-1336 as matched class set | **KNOWN_BAD** |
| 58 | `azhar2023` placeholder bib entry | **KNOWN_BAD** |
| 59 | NCAC Yaris deck uncited | **KNOWN_BAD** |
| 60 | `smithmodrafelder2019` author name | CONTRADICTED |
| 61 | `smithmodrafelder2019` title | CONTRADICTED |
| 62-67 | U1 to U6 | UNCITED |
| 68 | `force_balance.png` generator | PROVENANCE_MISSING |
| 69 | `L1_three_class_corrected.png` generator | PROVENANCE_MISSING |
| 70-75 | LIT_QUEUE items 1 to 6 | NEEDS_LITERATURE |
| 76-77 | LIT_QUEUE items 7 to 8 | UNVERIFIABLE |

