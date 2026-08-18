# Third-party notices

This repository redistributes material that this project did not author. The root `LICENSE`
(BSD 3-Clause) applies **only** to the original code and documentation authored for this project.
It does **not** apply to anything listed below.

Each entry records the licence **as found**, at the source named, on the date named. Where no
licence could be found, the entry says **UNRESOLVED** and names the routes that were tried.
**UNRESOLVED means no permission has been established. It does not mean permission is presumed.**
Silence from a rights holder is not a grant.

All entries verified 2026-08-18 against `origin/main` at commit `c7f0a16`. Full working, method
and byte-level measurements: `docs/R8_LICENCE_RECONCILE_2026-08-18.md`.

---

## 1. Vehicle finite element models, CCSA at George Mason University

**Status: UNRESOLVED. This is the most significant unresolved item in this repository.**

| | |
|---|---|
| Upstream | Center for Collision Safety and Analysis (CCSA), George Mason University, https://www.ccsa.gmu.edu/ |
| Sponsor | Federal Highway Administration (FHWA) |
| Validation reference | DOI [10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D) |
| Licence as found | **NONE. No licence file, no copyright notice, no redistribution grant, no public-domain statement.** |
| Stated obligation | Acknowledgement of CCSA at GMU and FHWA in papers and publications. See below. |

**Files redistributed here** (all under `vehicle_geometry_research/`, 22 files, 160,322,098 bytes,
91.0 percent of that directory's tracked bytes):

| Path | Bytes |
|---|---|
| `2010-toyota-yaris-coarse-v1l/2010-toyota-yaris-coarse-v1l/yaris-coarse-v1l.key` | 42,846,753 |
| `2010-toyota-yaris-detailed-v2j.zip` | 42,113,905 |
| `2007-chevrolet-silverado-coarse-v3a/2007-chevrolet-silverado-course-v3a/silverado-coarse-v3a.key` | 28,611,724 |
| `2007-chevrolet-silverado-detailed-v3e.zip` | 27,865,164 |
| `2010-toyota-yaris-coarse-v1l.zip` | 11,228,299 |
| `2007-chevrolet-silverado-coarse-v3a.zip` | 7,384,870 |
| plus 16 smaller `set-*.key`, `wall.key`, `combine.key` and `README.md` files | 271,383 |

> **Duplication, recorded as a fact about the current state.** `yaris-coarse-v1l.key`
> (42,846,753 bytes) is the single largest verbatim upstream artefact here and it is public
> **twice**: once as the extracted file above, and again inside `2010-toyota-yaris-coarse-v1l.zip`
> (11,228,299 bytes compressed). The Silverado coarse deck has the same structure. This is noted
> so it is not rediscovered as new; it is not a proposal to delete either copy.

**The upstream terms paragraph, verbatim**, from
`vehicle_geometry_research/2010-toyota-yaris-coarse-v1l/2010-toyota-yaris-coarse-v1l/README.md`
lines 14 to 20. The identical paragraph appears in all four upstream models:

> Users of the model must verify their own simulations. Neither CCSA or FHWA
> assume any responsibility for the validity, accuracy, or applicability of
> results obtained from this model.
>
> We ask that the CCSA at GMU and the FHWA be acknowledged for any use of this FE
> model resulting in papers and publications.

**How the absence of a licence was established.** `/usr/bin/grep -r -i -E
"licen|distribut|copyright|public domain|permission|all rights|redistribut"` across all four
upstream `README.md` files returns zero hits. `find` for `*licen*` or `*copying*` across the four
extracted trees returns nothing. `unzip -l` on each of the four archives finds no licence file
inside any archive. The material ships with no rights statement of any kind.

**Open sub-question**, carried from the corrections register: whether the canonical Yaris model is
NHTSA-hosted (NHTSA copies carry a "public information and may be distributed or copied"
statement) or CCSA-hosted (licence-silent). This has not been settled and cannot be settled from
the files on disk. Do not assume the favourable branch.

**Obligation status: the acknowledgement is currently UNMET.** Drafted text ready to paste is in
`docs/R8_LICENCE_RECONCILE_2026-08-18.md` section 2.

### 1a. Derived geometry from the above

| Path | Bytes | Status |
|---|---|---|
| `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` | 12,445,769 | Derived from the CCSA Yaris coarse v1l deck. **Inherits the unresolved status of its source.** |
| `vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` | 977,025 | Same, deprecated |
| `vehicle_geometry_research/failed_reconstructions_2026-07-25/car_mesh.ply` | 1,200,447 | Reconstruction attempt, superseded |
| `vehicle_geometry_research/failed_reconstructions_2026-07-25/car_mesh_rescaled.ply` | 1,200,447 | Same |

A derived work does not acquire a licence its source never granted.

---

## 2. warpmpm / mpm-engine, vendored solver

**Status: CLEAN.**

| | |
|---|---|
| Upstream | `kks32/mpm-engine`, pinned at SHA `544c93dd02cb9c7ead89e1155a62967243244fce` |
| Licence as found | **MIT**, `LICENSE` file present in both vendored trees |
| Copyright line | `Copyright (c) 2026 The mpm-engine authors (see AUTHORS.md)` |
| Paths | `third_party/mpm-engine-544c93dd/`, `third_party/mpm-engine-544c93dd-solver-core/` |

MIT permits redistribution provided the copyright notice and permission notice are retained. Both
`LICENSE` files are present in-tree, so that condition is satisfied. Note that the copyright
holder is **not** the holder named in the root `LICENSE`.

## 3. mpm-engine reference scripts under `citations/`

**Status: CLEAN.**

| | |
|---|---|
| Paths | `citations/vehicle(kks32).py` (18,329 bytes), `citations/splat_sim(kks32).py` (11,841 bytes) |
| Licence as found | **MIT**, full header in lines 1 to 17 of each file |
| Copyright line | `Copyright (c) 2026 The mpm-engine authors (see AUTHORS.md)` |

The licence travels with the files, which is why these are clean. Same copyright-holder note as
entry 2.

## 4. Asphalt PBR texture set, ambientCG

**Status: CLEAN.**

| | |
|---|---|
| Upstream | ambientCG, asset `Asphalt015` |
| Licence as found | **CC0 1.0** (ambientCG's blanket release for its asset library) |
| Paths | `assets/Asphalt015.png`, `assets/Asphalt015_1K-JPG_Color.jpg`, `assets/Asphalt015_1K-JPG_NormalGL.jpg`, `assets/Asphalt015_1K-JPG_Roughness.jpg` |

CC0 waives all rights, so no attribution is required and no licence file needs to accompany the
files. Provenance is recorded here because the filenames alone are the only evidence of origin
in-tree.

---

## 5. Published articles and reproductions under `citations/`

Licences resolved per DOI through Unpaywall on 2026-08-18. **The root BSD-3 licence must not be
read as applying to any of these.**

### 5a. Wang and Marsooli 2021, *Water Resources Research*

**Status: CC BY-NC-ND. Incompatible with an unrestricted BSD-3 claim.**

| | |
|---|---|
| Path | `citations/Water Resources Research - 2021 - Wang and Marsooli - Physical Instability of Individuals Exposed to Storm-Induced Coastal Flooding.pdf` (7,399,829 bytes) |
| DOI | [10.1029/2020WR028616](https://doi.org/10.1029/2020WR028616) |
| Licence as found | **CC BY-NC-ND**, published version, hybrid OA |

CC BY-NC-ND permits redistribution of the unmodified work with attribution, for non-commercial
purposes only, and forbids derivatives. BSD-3 grants commercial use and modification. The root
`LICENSE` therefore purports to grant rights this project does not hold in this file. The scope
carve-out in `LICENSE` addresses the false grant; it does not change this article's terms.

### 5b. Dasallas 2025, *Journal of Flood Risk Management*

**Status: CC BY. Redistribution permitted with attribution.**

| | |
|---|---|
| Path | `citations/J Flood Risk Management - 2025 - Dasallas - Integration of Stability Functions Into a Transport Flood Risk Modelling.pdf` (3,484,612 bytes) |
| DOI | [10.1111/jfr3.70154](https://doi.org/10.1111/jfr3.70154) |
| Licence as found | **CC BY**, published version, gold OA |

The cleanest item in this section. Attribution is required and is provided by this entry and by
`citations/README.md`.

### 5c. Smith, Modra and Felder 2019, *Journal of Flood Risk Management*

**Status: CLOSED ACCESS, all rights reserved. Most exposed item in `citations/`.**

| | |
|---|---|
| Paths | `citations/Smith-Modra-Felder/`, **16 image files**: 15 screen captures plus `smith2019_instability_table.png`, 6,215,623 bytes total |
| DOI | [10.1111/jfr3.12527](https://doi.org/10.1111/jfr3.12527) |
| Title | *Full-scale testing of stability curves for vehicles in flood waters* |
| Licence as found | **None granted.** Unpaywall reports `isOa: false`, `oaStatus: closed`, zero OA locations. Crossref records the licence URL as Wiley `termsAndConditions#vor`. |

Sixteen reproductions of figures and tables from a closed-access article are published here to a
public repository. No permission for this has been established. Flagged, not removed: removal is
outside this round's authorisation, and deletion would not unpublish material already served from
a public remote.

### 5d. Australian Rainfall and Runoff, Project 10 Stage 2

**Status: UNRESOLVED.**

| | |
|---|---|
| Paths | `citations/ARR_Project_10_Stage2_Report_Final.pdf` (1,115,134 bytes) |
| Publisher | Engineers Australia, Engineering House, Barton ACT |
| Report number | P10/S2/020, February 2011. ISBN 978-0-85825-948-5 |
| Contractor | Water Research Laboratory, UNSW |
| Authors | T D Shand, R J Cox, M J Blacka, G P Smith |
| Licence as found | **NONE FOUND** |

**Routes tried, both inconclusive:** (1) full text of all 29 pages extracted with `pypdf` and
scanned case-insensitively for `copyright`, `©`, `licen[cs]`, `all rights reserved`,
`may be reproduced` and `permission`: **zero matches on every page**; (2) the report prints no
DOI, so the Unpaywall route used for entries 5a to 5c is unavailable.

### 5e. AR&R Table 1, reproduced as an image

**Status: UNRESOLVED, inherited from entry 5d.**

| | |
|---|---|
| Path | `citations/ARR table 1 - guidelines and recommendations for limits for vehicle stability.png` (237,832 bytes) |
| Source | **Table 1, page 14** of the AR&R Project 10 Stage 2 report at entry 5d |
| Licence as found | **NONE FOUND**, same document, same silence |

Identified by matching the filename against the table caption in the extracted page text: page 14
carries "Table 1 / Guidelines and recommendations for limits for vehicle stability". This image is
a reproduction of a document **already published in this same directory**, so it adds no exposure
beyond entry 5d, but it is listed separately because a reader should not have to infer that a
table image and a report PDF are the same rights question.

### 5f. WRL Technical Report 2014/07, reproduced as images

**Status: UNRESOLVED. A distinct fourth source, not present in this repository as a document.**

| | |
|---|---|
| Paths | `citations/WRL reports technical and Research/`, 3 image files, 760,091 bytes |
| Files | `Figure 5-5 Combined flood hazard curves.png`; `Table 5-1 Combined hazard curves - vulnerability thresholds.png`; `Table 5-2 Combined hazard curves - vulnerability thresholds classification limits.png` |
| Source | **WRL Technical Report 2014/07, FINAL, September 2014**, Water Research Laboratory, UNSW |
| Content | The H1 to H6 combined flood hazard vulnerability classification |
| Licence as found | **NONE FOUND** |

**How the source was identified.** The images carry their own provenance: the `Table 5-1` capture
includes the page footer "WRL Technical Report 2014/07   FINAL   September 2014" and the page
number 38. This is **not** the AR&R Stage 2 report at entry 5d: that report numbers its figures
and tables flat (Figures 1 to 11, Tables 1 to 3, confirmed by extracting every figure and table
reference from all 29 pages), whereas these use chapter-prefixed numbering. The two are separate
documents and separate rights questions, and the report itself is not in this repository.

**Routes tried, all four inconclusive:** (1) no PDF of WRL TR 2014/07 is in the repository, so no
full-text scan of its front matter is possible; (2) the images carry no DOI, so the Unpaywall
route is unavailable; (3) `WebSearch` was unavailable in the session that made this
determination (upstream model routing error), so no search route was run; (4) direct fetches
returned `https://www.unsw.edu.au/research/wrl/our-research/technical-reports` HTTP 404,
`https://arr.ga.gov.au/arr-guideline` HTTP 403 (reproducing a standing project note that this
host 403s), and `https://knowledge.aidr.org.au/resources/australian-rainfall-and-runoff/`
HTTP 404.

**Lead for whoever closes this, not a finding.** The H1 to H6 classification in these figures was
subsequently adopted into Australian Rainfall and Runoff Book 6. If that adopted version carries a
usable licence, it would be a cleaner source for the same content than the WRL technical report.
**This has not been verified** and must not be relied on until someone reads the ARR terms
directly; it is recorded only so the next person does not have to rediscover the possibility.

---

## 5g. Summary: four distinct third-party sources are reproduced as images

Twenty image files in `citations/` reproduce figures or tables from **four separate third-party
sources**. A table lifted from a report is the same class of object as a screen capture of a
paywalled paper, and all of it is on a public repository.

| Source | Files | Bytes | Rights verdict |
|---|---|---|---|
| Smith, Modra and Felder 2019 (entry 5c) | 16 | 6,215,623 | **CLOSED, all rights reserved. No permission established.** Worst case of the four. |
| WRL Technical Report 2014/07 (entry 5f) | 3 | 760,091 | **UNRESOLVED**, four routes tried |
| AR&R Project 10 Stage 2, Table 1 (entry 5e) | 1 | 237,832 | **UNRESOLVED**, inherited; source PDF also published here |
| **Total** | **20** | **7,213,546** | |

None of these is deleted, and deletion is not the proposed remedy. Deletion does not unpublish:
this repository is public and GitHub has served removed blobs by SHA in this account. The remedy
is a decision by the repository owner, and possibly a permission request to each rights holder.
The purpose of this section is to make that decision possible by stating exactly what is exposed
and under what terms.

---

## 6. PhysGaussian, algorithm only

**Status: no upstream source redistributed. Upstream itself is UNLICENSED.**

| | |
|---|---|
| Upstream | `XPandora/PhysGaussian` |
| Licence as found | **NONE.** GitHub API returns `"license": null`; no `LICENSE`, `LICENCE` or `COPYING` in the root listing; `raw.githubusercontent.com/.../main/LICENSE` returns HTTP 404. Verified 2026-08-18. |
| Published algorithm | Xie et al., *PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics*, arXiv:2311.12198 |

`bridge/` implements the published algorithm and **does not** contain upstream source. Measured by
comparing `bridge/filling.py` and `bridge/extract.py` against the fetched upstream
`particle_filling/filling.py` and `gs_simulation.py`, after stripping comments and normalising
whitespace:

| Comparison | Shared function names | Longest identical run | Line similarity |
|---|---|---|---|
| `bridge/filling.py` vs upstream `filling.py` | none | 1 line | 0.0215 |
| `bridge/extract.py` vs upstream `gs_simulation.py` | none | 1 line | 0.0099 |

The two differ in framework (upstream Taichi and PyTorch, `bridge/` pure NumPy) and in algorithm
(upstream ray casting, `bridge/` six-direction prefix-max scans).

**Limit of this check:** two upstream files were compared, the two that `bridge/README.md` names
as the ones not to copy. The other nine upstream Python files were not diffed. This clears the
specific flagged risk; it is not a clean-room audit.

---

## 7. Summary table

| Asset | Upstream | Licence as found | Status |
|---|---|---|---|
| CCSA/GMU FE vehicle models (4) | CCSA at GMU, FHWA-sponsored | none | **UNRESOLVED**, acknowledgement unmet |
| Derived Yaris hull and other `.ply` | derived from the above | none | **UNRESOLVED**, inherited |
| mpm-engine vendored solver | `kks32/mpm-engine` @ `544c93dd` | MIT | clean |
| `citations/*(kks32).py` | mpm-engine authors | MIT | clean |
| Asphalt015 PBR set | ambientCG | CC0 1.0 | clean |
| Wang and Marsooli 2021 | AGU / Wiley | **CC BY-NC-ND** | conflicts with unrestricted BSD-3 |
| Dasallas 2025 | Wiley | CC BY | clean, attribution required |
| Smith, Modra and Felder 2019, 16 images | Wiley | **closed, all rights reserved** | **no permission established** |
| AR&R Project 10 Stage 2 report | Engineers Australia | none found | **UNRESOLVED**, 2 routes tried |
| AR&R Table 1 image (1) | Engineers Australia | none found | **UNRESOLVED**, inherited from the report |
| WRL Technical Report 2014/07 figures (3) | Water Research Laboratory, UNSW | none found | **UNRESOLVED**, 4 routes tried |
| PhysGaussian | `XPandora/PhysGaussian` | none (upstream unlicensed) | algorithm only, no source redistributed |

---

## 8. If you are the rights holder

If you hold rights in anything listed above and object to its inclusion, please open an issue at
https://github.com/jcerrell-IS/can-it-ford or contact the repository owner. Note that this
repository is public and its history is world-readable, so removal from the current tree does not
by itself remove material already published.
