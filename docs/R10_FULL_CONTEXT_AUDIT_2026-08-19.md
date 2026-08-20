# R10 full-context audit

Synthesist pass, written 2026-08-20 (the wave was commissioned 2026-08-19; the
filename keeps the commission date). Read end to end before writing the eleven
session prompts.

**Provenance tags used throughout.** `read-directly` = I ran the command or read
the file/page in this session. `inferred` = arithmetic I performed on values I
read, with the arithmetic stated. `relayed` = taken from another agent's report
or another document in this wave, not independently re-derived by me.

**Standing caveat that applies to the whole file.** The `physics-skeptic`
adversarial subagent is dead fleet-wide (CLAUDE.md, section "THE ADVERSARIAL
REVIEW PATH IS DEAD FLEET-WIDE, 2026-08-19"). Nothing in this report has been
through it. Every claim here is **UNREVIEWED**. Do not upgrade any of it to
"checked" on the strength of appearing in a synthesis document.

---

## 1. The five things that change what happens next

Ordered by how much downstream work they invalidate or unblock.

### 1.1 The submitted paper contains four citation and measurement defects, and the project already held the facts that refute three of them

`read-directly`, 2026-08-20, from `git cat-file -p overleaf/main:conference_101719_1.tex`
(this is the submitted file; `paper/conference_101719.tex` in the repo is a stale
11-key version and answers this question wrongly):

1. Line 205 reads verbatim: "We did not measure ground clearance from the mesh."
   The project measured it. `docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md:155`
   reads "**Measured native ground clearance: 0.1737 m.**" (`read-directly`),
   dated a week before the 2026-08-02 paper snapshot.
2. The same line concludes "only the 1100 kg configuration is a genuine class
   match." With the measured clearance this is false. `vehicle_params.py:211`
   sets small-passenger `ground_clearance_m_max: 0.12` (`read-directly`); the
   hull is 0.1737 m, so it fails that axis. `:216` sets large-passenger
   `length_m_min: 4.3` and the hull is 4.2826 m, so it fails that axis.
   `inferred`: **no AR&R class is satisfied on all three axes by the unscaled
   hull.** The project's own reconciliation table at `:159` already records
   small_passenger as 2/3 with clearance FAIL.
3. Line 147 attributes the 0.78 concrete friction figure and "their worst-case
   bed friction" to `\cite{shand2011arr}`. 0.78 is Smith, Modra and Felder's own
   measurement (dry and wet concrete), `relayed` from two independent reader
   passes in this wave that each read the Smith Conclusions page and the full
   30-page AR&R report and found no 0.78 anywhere in AR&R.
4. Line 147 gives Smith's drag coefficient range as "1.0 to 1.8". `relayed`,
   read from the Smith Conclusions: the reported range is 0.98 to 1.83 with mean
   1.38, and the paper's own Table 2 gives a subcritical ceiling of 1.86, so the
   source is internally inconsistent on the ceiling and the tex quotes neither
   endpoint correctly.

**What it invalidates.** Any statement that the 17 runs are AR&R-class-anchored,
and the sentence in Section-approach-C that the mass block spans "one inside each
of AR&R's three kerb-weight bounds". The verdict of the whole L1 comparison is
not invalidated, but the class label attached to it is unsupported and must
become a labelled, reversible assumption.

**Also load-bearing.** `read-directly`: the run inventory labels all three
`mass_grid` rows `small_passenger`, and `vehicle_params.L1_verdict` takes
`vehicle_class` as a defaulted string with no classifier reading length, weight
and clearance. The class is assigned by hand. `inferred`: for `g64_m1100`,
realized depth 0.2944294473039918 m times velocity 1.5 m/s gives D.V =
0.4416 m2/s, which FAILS the small-passenger limit 0.30 and PASSES the
large-passenger limit 0.45. **The canonical run's L1 verdict flips on the class
label.**

### 1.2 There is a same-vehicle, same-mass, same-friction external validation target for the buoyancy question, and running it is cheaper than any further mechanism hunting

`relayed`, from a full-text read of Azhar, Pauwels and Bui 2023
(`10.1111/jfr3.12885`), section 4.3: a 1:14 Toyota Yaris, 1097 kg full scale,
mu = 0.55, loses traction in still water at **0.35 m** in their SPH model against
**0.37 m** in the up-scaled physical model. The project's canonical hull is a
Toyota Yaris at 1100 kg with `floor_friction` 0.55 on every one of the 17 runs
(`read-directly`, `data/all_runs_inventory.csv`).

`relayed`, a second and independent flotation bracket: 0.34 to 0.57 m across
Bonham and Hattersley 1967 (measured 0.57), Gordon and Stone 1973 (inferred 0.42
rear / 0.50 front), Keller and Mitsch 1993 (0.34 to 0.42) and Shah 2018
(0.457 prototype-equivalent). Al-Qadami 2022 gives 0.38 m.

**Why this changes what happens next.** CLAUDE.md item 6 records that no existing
gate is a physics validation and that G-3 compares against a `RHO_REF` derived
from the same pipeline, so it cannot fail for a reason external to the code. A
still-water depth ladder on the canonical hull, finding the depth at which net
vertical force crosses zero, would be **the project's first gate that can fail
for an external reason**. It is quiescent, so it isolates the buoyancy path from
the drag path, and the sphere's +34 to +64 percent excess makes a falsifiable
prediction: the crossing depth should land well below 0.35 m.

### 1.3 The literature supplies a fifth candidate mechanism for open question 1 that the project's list does not carry, and it predicts exactly the observed refinement-insensitivity

`relayed`, from a direct full-text read of arXiv:2209.02466v3 (Zhao, Jiang, Choo),
section 4.1: standard MPM stress oscillations under near-incompressibility "are
not remedied by spatial refinement", and the Introduction gives the mechanism:
locking severity is driven by **the number of material points per element**, not
by cell size, so refining at fixed particles-per-cell does not relax the
constraint count.

**Citation correction, two independent origins.** The project brief calls this
"Zhao Jiang Choo CMAME 2023, arXiv 2209.02466". `relayed`: a Crossref lookup by
title and the arXiv metadata DOI field independently return *International
Journal for Numerical Methods in Engineering* 124(23):5334-5355, 2023,
`10.1002/nme.7347`. Not CMAME. The arXiv id is correct.

**Three further mechanisms, none on the project's list of four:**
- Small-cut boundary DOF starvation (Coombs, Bird, Pretti, AgMPM,
  `10.1016/j.cma.2025.118012`, abstract only, `relayed`): DOFs near a body
  boundary receive very small material-point contributions, giving artificially
  large boundary accelerations, and larger stencils make it worse.
- Under-resolved no-slip at the body surface (Albano et al 2016,
  `10.1016/j.jhydrol.2016.02.009`, `relayed` from a direct read): "using no-slip
  conditions on the solid body surfaces makes the viscous friction as well as the
  hydrodynamics forces on the floating objects to be widely overestimated". Both
  Albano and Amicarelli therefore use free-slip on the body. Independently
  corroborated from the graphics side (Wang et al, DC-APIC,
  `10.1016/j.gmod.2025.101269`, abstract only, `relayed`): shared-grid MPM is
  "inherently restricted to sticky and no-slip interactions".
- Nodal density oscillation under weak compressibility (Zhao et al 2019,
  `10.1016/j.compfluid.2018.10.007`, `relayed` from a direct full-text read of
  the accepted manuscript): finer meshes at fixed particles-per-element make
  pressure fluctuation *worse*; raising particles-per-element makes it better.

**The discriminating control all four share, and it is not another grid sweep:**
hold `dx` fixed and vary particles-per-cell. Three of the four predict the error
moves; a pure `dx` sweep at fixed PPC, which is what the project has run, cannot
separate any of them.

**Two mechanisms the project should stop reaching for, on sign grounds.** Underbody
aspiration (Bonham and Hattersley 1967, Gordon and Stone 1973, `relayed` through
the AR&R report, one secondary source for both) acts DOWNWARD. Free-surface
drawdown in flow (Kramer 2016, Azhar 2023, Al-Qadami 2022, three separate
origins, `relayed`) REDUCES effective buoyancy. Both are the wrong sign for a
positive excess.

### 1.4 The research corpus reaches 8 of 21 completed deep searches, and one of its headline numbers is inflated by a raw search dump sitting in `docs/`

`read-directly`, 2026-08-20, `data/research_corpus_index.json`: 332 records, 319
distinct normalised titles, `cited_in_repo` 76, `cited_reader_facing` 43, built
2026-08-15. Those reproduce the CLAUDE.md headline exactly.

`relayed` from `docs/r10/corpus_revision.md`, which measured them live the same
day: the workspace holds **21** completed deep searches, `REPORTS` names **8**,
so **13** reach the index by no route. Six of the thirteen have a full Undermind
markdown export on disk right now and **two of those are inside this repo**
(`docs/Dynamic_Vehicle_Traction_in_Floodwater.md`,
`vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md`). They are
invisible because `REPORTS` is hardcoded and `index_documents()` skips any `.md`
not named `compass_artifact*`.

`relayed`, same source, and this is the part that changes a published number:
`repo_cited_dois()` treats all of `docs/` as reader-facing, and
`docs/Dynamic_Vehicle_Traction_in_Floodwater.md` is a raw search dump carrying 34
DOI strings. Excluding that one file drops `cited_reader_facing` from **43 to
34**. Nine papers' only reader-facing route is a search dump. **The honest ladder
is 34 reaching written project prose, 43 counting the dump, 3 printing in the
paper.**

`read-directly`, my own check of the corpus against the 14 cite keys: of the
seven DOIs I tested, `smithmodrafelder2019`, `xia2014`, `azhar2023` and
`xiong2024` are IN the corpus; `shah2018` (`10.1051/matecconf/201820307003`),
`pregnolato2017` (`10.1016/j.trd.2017.06.020`) and `lyu2023`
(`10.1016/j.compfluid.2023.106144`) are ABSENT. The corpus is not a superset of
the bibliography, and it is missing the most-cited depth-disruption function in
flood-transport research.

### 1.5 Every dispatching session has 76 MCP connectors and every dispatched slot has 17, so the routing table has been aspirational for three waves

`relayed` from `docs/r10/connector_revision_AUDIT_d20.md`, measured off seven slot
tool manifests plus a sweep of `~/.claude/projects`: main checkout 76 prefixes
including 31 bridged claude.ai connectors; all seven R9 slots 17 prefixes and
**zero** bridged connectors. Twenty r7/r8/r9 sessions show zero.

`relayed` from `docs/r10/connector_revision.md`: Otter, Slack, Google Calendar,
Google Drive, pdf-viewer and Scholar Gateway all WORK from the coordinator
session, with quoted returns. Scholar Gateway (`mcp__88a938f6-...__semanticSearch`)
reaches **Wiley full text for the Journal of Flood Risk Management**, which is
the journal this project lives in and which Undermind (open access only) cannot
reach.

**The consequence that matters.** A coordinator can verify things no slot can,
so a relayed result cannot be independently confirmed by its recipient. That is
the precondition for the relay-fidelity failure already recorded in this
project's memory. `relayed`, and explicitly a hypothesis not an isolated cause:
the common factor across the twenty zero-connector sessions is the launcher,
`r8_launch.sh` running `claude --model opus --effort max --permission-mode
bypassPermissions`.

---

## 2. What was actually read, and what was not

### 2.1 Counts by source

All counts in this subsection are `relayed` from the individual reader reports,
except where marked.

**PDFs read from local disk.** Across `~/Downloads` (170 PDFs enumerated by
`find`, reducing to 136 distinct md5 across 23 duplicate groups) and `~/Desktop`
(2,165 PDF paths reducing to 400 unique basenames and 227 regular files), the
readers opened page 1 of 25 and 27 candidates respectively and read the following
**in substantive depth** (multi-page, numbers quoted with page or section
anchors):

| Work | Depth reached |
|---|---|
| AR&R Project 10 Stage 2 (P10/S2/020, Feb 2011) | all 30 pages |
| Smith, Davey and Cox 2014, WRL TR 2014/07 | full report, 59 pages |
| Smith, Modra and Felder 2019 (`10.1111/jfr3.12527`) | 15 pages incl. Tables 1-3, Figs 5-10 |
| Nihei et al 2025 (`10.1016/j.rineng.2025.107189`) | full, incl. sections 3.1.3-3.1.5, 4.1-4.3 |
| CCSA 2010 Yaris coarse validation (`10.13021/G8JS5D`) | 36 slides, incl. slides 7, 20, 29-36 |
| Negi and Ramachandran 2021 (arXiv 2109.09697v2) | full, incl. Figs 3, 17-25 |
| Zhou et al 2025 hydroplaning MPM (`10.1063/5.0276643`) | full, incl. eqs 18-25, Table I |
| Azhar, Pauwels and Bui 2023 (`10.1111/jfr3.12885`) | full, verified against typeset render |
| Amicarelli et al 2015 (`10.1016/j.compfluid.2015.04.018`) | full, verified against typeset render |
| Albano et al 2016 (`10.1016/J.JHYDROL.2016.02.009`) | full |
| Xiong et al 2024 (`10.1029/2023WR036739`) | full |
| Shah et al 2018 (`10.1051/matecconf/201820307003`) | full, incl. Tables 5, 7, 8 |
| Zhao et al 2019 (`10.1016/j.compfluid.2018.10.007`) | full accepted manuscript, Cambridge Apollo green OA |
| Syamlal, Celik and Benyahia 2017 (`10.1002/AIC.15868`) | full accepted manuscript, incl. Tables 1, 3 |
| Kramer, Terheiden and Wieprecht 2016 (`10.1016/J.IJDRR.2016.04.003`) | full |
| Al-Qadami et al 2022 (`10.1111/jfr3.12828`) | full publisher text |
| Azhar et al 2026 (`10.1111/jfr3.70181`) | full publisher text, incl. Tables 3, 5 |
| Thorpe et al 2026 (arXiv 2605.30542v1) | full |
| Hsiao and Kumar 2025 (arXiv 2507.09005v1) | full |
| Kerbl et al 2023 3DGS; Xie et al PhysGaussian | full |
| Zhao, Jiang and Choo (arXiv 2209.02466v3) | full text, searched locally |
| Bird et al (arXiv 2412.01565); Zong et al (arXiv 2403.13783); Chandra et al (arXiv 2402.11719) | full texts, downloaded |
| Dasallas et al 2025 (`10.1111/jfr3.70154`) | 17 pages |
| vehicle_mpm_coupling_reference.pdf (project-internal, 2026-07-08) | full |

That is **roughly 25 works read in depth**, of which about 20 are external
peer-reviewed sources. Everything else in the two PDF trees was classified from
filename, Spotlight metadata, or page 1 alone.

**Read through connectors, not as PDFs.** About 20 further works were read as
full text by Undermind `read_pdfs` sub-agents and are `relayed` at second hand
with section and page anchors: Got09b, Gen26b, Liu22f, Jan21/Jan21b, Neg21b,
Col11, Rez21, Jai20, Bri11, Che16b, Aga21, Gri19, Jun22, Mit14, Jen21, Cla24,
Oli24, Gro18, Pan17, Ste26c, Zha23i, Azh23, Das25, Sha19, Wah26.

**Deep searches inspected.** 21 completed searches in Undermind workspace
`17299f2a-8dc8-438b-8c84-5abf19395e2c`, all enumerated (`relayed`, and the count
21 was independently reproduced by two different passes in this wave). Of the
1,206 ranked paper rows across them, **409 were enumerated** (top 20 per search)
and 797 were not. `detail_level: standard` was used, so **no abstract text was
read for any of those 409**.

**Web and API sources verified.** Crossref REST (about 12 DOIs resolved live),
Unpaywall (4 OA-status checks with a working control), Semantic Scholar Graph API
(4), OpenAlex (about 10 records), Hugging Face API (`/api/spaces` 200,
`/api/datasets` 401), `claude --help` and `claude agents --help` on the installed
binary (v2.1.234), and the Claude Code docs pages for hooks, worktrees,
sub-agents, skills, headless mode, cross-session messaging and agent teams.

**Repo state read live by me in this session:** `data/all_runs_inventory.csv`
(18 lines, 17 runs, 42 columns), `data/research_corpus_index.json`,
`vehicle_params.py:131,142,211,216,221`,
`docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md:155,159`,
`overleaf/main:conference_101719_1.tex` (14 distinct cite keys),
`docs/r10/corpus_revision.md`, `docs/r10/connector_revision.md`,
`docs/r10/connector_revision_AUDIT_d20.md`.

### 2.2 What could not be read, and why

A coverage claim without its complement is not a coverage claim.

- **Four requested papers are closed with no retrievable full text**, confirmed by
  four separate origins (Undermind `read_pdfs`, Semantic Scholar
  `openAccessPdf: CLOSED`, Unpaywall `is_oa: false` with Zhao 2019 as a working
  positive control, and a Scite-schema index returning `contentDenied: true`):
  **Lyu et al 2023** `10.1016/j.compfluid.2023.106144` (no abstract available from
  any source queried), **Wasfy et al 2015** `10.1115/DETC2015-47142`, **Khapane
  and Ganeshwade 2014** `10.4271/2014-01-0936`, **He et al 2026**
  `10.1115/1.4071177`. He 2026 is the single highest-value unread item: by its
  own abstract it supplies flume-measured hydrodynamic loads on a vehicle, which
  is exactly the external validation data this project lacks.
- **Sch19e / Schulz and Sutmann 2019 image particles has no PDF and no DOI**
  through the connector, only a Semantic Scholar link. It is the paper behind one
  of the project's four named candidate mechanisms for open question 1. That
  mechanism currently rests on a title and an abstract.
- **Kra21b, the floating-sphere public benchmark dataset** (`10.3390/en14020269`,
  top-ranked in the buoyancy search) had no retrievable PDF through Undermind. It
  is published in Energies, which is fully open access, so it should be
  downloadable directly from MDPI. This is the most valuable single retrieval
  still outstanding.
- **PDF coverage through the connector is severely asymmetric and the gap falls on
  the project's own mechanisms.** Per search, no-PDF counts: 25 of 32 (buoyancy
  overestimation), 63 of 88 (free-surface estimator error), 39 of 44 (moving rigid
  body), 57 of 68 (settling and force reporting). These per-search counts overlap
  and must NOT be summed.
- **The entire moving-vehicle experimental literature is abstract-only through the
  connector**: 39 of 44, including all eleven highest-relevance entries.
- **797 of 1,206 ranked deep-search rows were never enumerated**, and no abstract
  text was read for any of the 409 that were.
- **163 of 514 symlinks in the Desktop research corpus tree are broken** (31.7
  percent), 25 of them PDFs. Two whole source trees
  (`/sessions/rcw-018wosspwdgoivwo35h8ibzj/mnt`, 109 links, and
  `~/CAN_IT_FORD_ARCHIVE_2026-07-17`, 50 links) return "No such file or
  directory". The corpus index over-reports its own live coverage.
- **Non-PDF research is structurally invisible to a PDF sweep.** Smith, Modra and
  Felder 2019 exists on the Desktop only as 15 PNG page scans.
- **Personal medical, financial and identity PDFs were deliberately not opened**,
  classified from filename and metadata only. This is a partial view and is
  labelled as one.
- **Xav22b** (`10.23967/eccomas.2022.228`) is a one-page ECCOMAS abstract despite
  being flagged PDF-available. Treat it as unread.
- **Eight papers were read and found NOT to contain the evidence their titles
  imply**, recorded so nobody chases them again: Toy24, Vil24c, Xie26, Col11,
  Neg21e, Zha22l, Liu22f, Xav22b.
- **A measurement trap that produced false absences.** A first coverage probe
  reported Smith 2019 and Bonus 2025 as absent from the corpus. Both are present;
  their index titles use U+2010 HYPHEN. Any future corpus audit must normalise
  Unicode hyphens before claiming a paper is missing, and the papers it
  false-negatives on are precisely the flood-vehicle ones.
- **I did not run `list_workspaces` against every Undermind account**, so I cannot
  say whether further searches exist outside workspace `17299f2a`.
- **Not a single DOI in this report was resolved against a primary print record by
  me**; the DOI verifications are `relayed` from Crossref and OpenAlex calls made
  by other readers.

---

## 3. Gaps

### 3.1 Project claims contradicted by a source

| Project claim | Where it lives | Contradicting source | Status |
|---|---|---|---|
| "No measured Yaris tensor exists anywhere: SAE 1999-01-1336 ends Nov 1998." | CLAUDE.md item 4(a) | CCSA `10.13021/G8JS5D` slide 7, "Actual Vehicle" column: 1078 kg, roll 388, pitch 1498, yaw 1647 kg m2, CG Z 558 mm | **Premise false.** The do-not-wire conclusion survives on reasons (b) and (c). |
| "the cloud CG is 23.8 percent above the 0.51 m estimate" and implicitly conservative | CLAUDE.md item 4 | Measured CG 0.558 m (CCSA) and 0.45 m (Azhar 2023 lab, same vehicle) | Cloud 0.6312 m is +13.1 percent above CCSA measurement (`inferred`); the 0.51 m estimate is the CLOSER of the two. Conservatism argument survives, the arithmetic does not. |
| "Coarse resolution usually OVER-predicts peak hydrodynamic force. Over-threshold NO-FORD verdicts are therefore conservative." | CLAUDE.md L-4 | WRL TR 2014/07 p47: numerical model UNDER-predicted local peak velocity at 1 m, 5 m and 10 m grids against a physical model and a building that was actually demolished; the report calls it "a non-conservative result" | **Scope L-4 to MPM and to force.** The counterexample is 2D depth-averaged and about velocity, so it does not refute L-4 in its own domain, but it removes L-4's status as a general principle in exactly this geometry (bluff body, coarse grid, local velocity). |
| "Unsteady flow raises drag 40 to 50 percent, Azhar 2026" | CLAUDE.md, RESEARCH INTEGRATION V2 | Azhar 2026 Table 3: +14.0 to +40.7 percent, depending on BOTH acceleration and depth; floodfront up to +43 percent. The 50 percent is Klapp et al 2020 and FEMA P-646, quoted by Azhar, not measured by Azhar | **Rewrite.** The abstract's "40-50%" headline is the likely origin of the drift. |
| "Four prior vehicle fording or wading simulations exist ... the deep-search layer puts it at eight or nine" | CLAUDE.md prior-art block | 16 enumerated with DOIs (`relayed`, Crossref plus Undermind plus WebSearch, three named views) | **Both figures understate it.** Replace with the enumeration and name the searched views. |
| "paper/ cites NONE of them" | CLAUDE.md prior-art block | `read-directly`: the submitted tex cites `azhar2023` three times, load-bearing for `floor_friction` 0.55 | True only of the four named works. As a general statement it is false, and it understates exposure: the friction coefficient is inherited from prior SPH vehicle-flood work. |
| "the novelty for this project is the validation step, not the pipeline" | CLAUDE.md L-7 | He et al 2026 `10.1115/1.4071177` abstract: free-running model-scale vehicle experiments plus flume force measurement, validating coupled models | **Rewrite L-7.** Validation is no longer unclaimed at model scale. What remains open is MPM-specific coupling validation. |
| L-7's identifier "arXiv 2607.00673 (Low, Hsiao, Li, Thorpe, Topcu, Kumar, July 2026)" | CLAUDE.md L-7 | The PVWM paper on disk is arXiv 2605.30542v1, 28 May 2026, authors Thorpe, Tretiakov, Hsiao, Low, Li, Iqbal, Bhatt, Topcu, Kumar | Either two papers or a wrong id. Unresolved. |
| "Zhao Jiang Choo CMAME 2023" | project brief and any bib built from it | IJNME 124(23):5334-5355, `10.1002/nme.7347`, two independent origins | Venue wrong. |
| "Xiong et al. 2024 validates a simplified rigid-linked-block vehicle in SPH" | `reference_docs/briefing_vault/11_Technical_Feasibility_and_Validity_Review_UPDATED.md:24` | Xiong 2024 is 2D shallow-water finite volume plus 3D DEM multi-sphere. SPH appears only in its literature review | **Engine conflation**, the same class of error CLAUDE.md item 1 exists to prevent for this project's own runs. Also drop "validates": the paper's own conclusions call its 3-sphere vehicle an oversimplification. |
| "Amicarelli (2015), Albano (2016)" paired as two supports | `reference_docs/briefing_vault/00_MASTER_CORRECTIONS_INDEX.md:38` and `11_...:24` | Albano 2016's own conclusion opens "This research validated the Smoothed Particle Hydrodynamics model of Amicarelli et al. (2015)"; three shared authors | **One lineage, two validation campaigns.** Not two votes. |
| bib note "The exact value 0.55 is NOT confirmed in the primary full text" for `azhar2023` | `paper/can_it_ford_references_IEEE.bib` | Azhar 2023 sections 2.2 and 3.4, read from the typeset PDF at `~/Zotero/storage/6Y7VPLP7/`: 0.55 measured by spring balance on a rubber mat, stated as a SET model input | **Close the audit.** Answer is SET INPUT, lab-measured. |
| "Smith 2019 ... mu is 0.78 wet-or-dry" plus a 30.7 percent inflation warning | memory note, moving-vehicle fork | Azhar 2023 p11 attributes 0.78 to Smith et al **2017** (WRL TR 2017/07), a different report. Shah 2018's own summed form `F_N(mu_RO + mu)` is internally valid because the two coefficients are orthogonal directions, and inflates by 17.7 percent on Shah's numbers | Resolve the attribution; keep the prohibition but record why the two cases differ and that 30.7 percent does not transfer. |

### 3.2 Project claims nobody has checked

- **`sustain_frames = 3` at `simulation/failure_modes.py:52` is unsourced and gates
  16 of 17 published verdicts.** Smith 2019 p6 now supplies a third, independent
  argument that the criterion is the wrong *shape*: peak traction occurs at the
  onset of slip and "it is unlikely that a vehicle will regain stability after an
  initial loss of traction" (`relayed`). That argues for lowering it toward 1,
  which flips verdicts, so it must be run as a labelled sensitivity.
- **The three 0.05 literals in `failure_modes.py` (`slide_m` metres,
  `slide_speed_ms` metres per second, `float_m` metres) have never been jointly
  perturbed and published.** The memory record says only a joint perturbation
  finds the flips, and that a one-at-a-time sweep already produced a published
  and retracted false negative.
- **Nobody has checked whether the P-2 passthrough failure-rate trend (7.99
  percent at 0.5 m/s rising monotonically to 15.88 percent at 3.0 m/s) has a
  break at the Moore and Power 2002 regime boundary V = 1.81 m/s.** The sweep
  points bracket it and the data is on disk.
- **Nobody has checked whether the hull submerges before it slides**, which is
  the observable signature WRL names for the Xia 2011 density-scaling error that
  got Xia excluded from the AR&R reanalysis. The 17 runs realise 302.55 to 663.58
  kg/m3 and return `density_plausible False` on every row.
- **Nobody has checked whether the pinned solver at
  `third_party/mpm-engine-544c93dd-solver-core/` does mixed Gauss integration or
  any stress smoothing.** Zhao's Anura3D has both, so a like-for-like comparison
  against his clean pressure fields is not valid until this is settled.
- **Nobody has checked what tangential condition the coupler imposes at the rigid
  body surface.** Albano's overestimate mechanism only applies if it is
  effectively no-slip.
- **Nobody has recorded the realised body-particle acceleration in g for the
  sphere case.** Amicarelli and Albano both clamp it at 10 g precisely because the
  interface pressure reconstruction goes bad above that, and both report their
  realised values (4-8 g, 2-5 g) as evidence of validity.
- **`realized_rho` is 309.7383668982256 in the inventory against CLAUDE.md's
  canonical 310.494** (`read-directly` for both). A 0.24 percent drift, too small
  to change a verdict, exactly the kind the register exists to catch.
- **`gates_results.json` holds no pass/fail field and gate verdicts exist only in
  `gates.py` stdout, which is never persisted.** Nobody has checked what the
  current verdicts are, because there is nothing to check them against.
- **The GitHub MCP token is stale** (`Bad credentials`, `relayed`), and the
  mechanism recorded in the repo skill (missing `headers` block) is wrong for this
  server: it comes from the Claude Desktop config with an `env` block.

### 3.3 Source findings nobody has acted on

- **Negi and Ramachandran's one-timestep packed-configuration MMS test** detects a
  discretization defect with no settling, transient or stationarity confound.
  That confound has already cost this project four results. Cost: minutes of CPU.
- **The O(Mach^2) prediction gives a decisive, cheap control on artificial sound
  speed.** `inferred` from the inventory read live: c = 12.845 m/s on all 17 runs,
  and nominal Mach runs 0.0389 (v=0.5) to 0.2336 (v=3.0), so **15 of 17 runs sit
  above the Ma <= 0.1 accuracy ceiling** that Amicarelli 2015 p215 and Azhar 2023
  p6 both state (and both attribute, ultimately, to Monaghan, so they are two
  restatements and not two origins). Density error scales as Ma^2: 1.4 percent at
  baseline, 5.5 percent at v=3.0. That does NOT explain a 34 to 64 percent excess,
  which is itself useful: it rules the magnitude out as a sole cause. Zhao 2019
  cleared the same rule by roughly 116x.
- **Zhao 2019's A-A versus B-B fixity diagnostic** (recompute the force from
  particles sampled one grid cell away from the constrained surface) needs no new
  simulation, because `rollout.npz` stores every water particle for every frame in
  all 17 canonical runs.
- **Amicarelli's flat-plate jet benchmark** (D = 0.028 m, u = 19.61 m/s, dx =
  0.001 m, analytic stagnation Cp = 1.0, their result +10 percent) is the
  cleanest analytic-truth force benchmark found and is 2D and cheap. Porting it
  would separate "generic particle-method peak-pressure bias of order 10 percent"
  from "our fixed-body vertical accessor is broken by nearly a factor of two".
- **Syamlal's record-length criterion is failed by the project's own data.**
  `relayed`: continue the autocorrelation summation until K >= 6 tau, and if that
  cannot be met before K = N the record is not long enough. `inferred` from
  CLAUDE.md's N_eff 2.9 to 11.0 on N = 91: tau_int is 8.3 to 31.4 frames, so
  6 tau is 25 to 94 frames, and at the correlated end **6 tau exceeds N**. A
  5-percent-accurate tau would need N of order 10^4 tau, i.e. roughly 83,000 to
  314,000 frames.
- **Syamlal's phase-shift finding** gives a second, separately-originated
  mechanism for the non-monotone g48/g64/g96 ladder (Steffen 2008 is the first,
  and they are genuinely independent). It is testable: extract
  `final_disp_mag_m` as a time series rather than an end-state scalar and check
  whether the three traces are phase-shifted rather than differently valued.
- **Syamlal also shows a transient quantity moves under iteration tolerance and
  time step alone, with no grid change.** Before attributing the +87.8/-59.2
  percent swing to resolution, hold the grid fixed and vary only tolerance and dt.
- **Amicarelli and Albano both prescribe ensemble averaging over repeats** as the
  remedy for weak-compressibility pressure noise. The project already has repeat
  distributions built for `probabilistic_verdict.py`, so the ingredient exists.
- **pyMSER's ADF test is a different companion statistic from the reverse-
  arrangement test** the project uses, and the same source measures truncation
  points differing by nearly 3x across methods on one dataset.
- **Pan 2017 gives the reverse-arrangement test a reliability floor of N >= 10.**
  With N_eff of 2.9 to 11.0, several runs sit at or below it, so the stationarity
  verdict on those runs may not be reliable in principle.
- **AR&R's own recommendations 2 to 5 ask for exactly this project's work** and
  name friction coefficients, buoyancy in modern cars, orientation and vehicle
  movement as its unassessable gaps. Nihei 2025 delivered recommendation 2
  fourteen years later. That is a stronger framing than novelty, which is refuted.
- **Nihei's washaway sequence** (vibration, 37 s of intermittent creep, then
  sudden acceleration) is external experimental support for the project's
  full-record-for-verdicts rule, from a separate origin.
- **Nihei's two washaway events land 3.9 and 6.0 percent above the AR&R
  small-passenger D.V threshold of 0.30** (`inferred`: 0.289 x 1.10 = 0.3179;
  0.294 x 1.06 = 0.3116). Fully specified vehicle and conditions. Caveat: 74
  percent channel blockage.
- **Nihei measured unbraked rolling resistance at 0.0250 and 0.0242** against a
  mu_s of about 0.30, and shows the AR&R small-passenger criterion agrees with the
  UNBRAKED curve. The project's floor at 0.55 is neither regime.
- **Pregnolato 2017 is the field-standard depth-disruption function** (over 560
  citations by one count, 634 citing publications by another) and appears nowhere
  in this repository outside the corpus index, and is not in the corpus.

---

## 4. The most validated route forward

### 4.1 For the physics

**The route: a still-water flotation ladder on the canonical Yaris hull, graded
against Azhar 2023's 0.35 m SPH / 0.37 m physical pair, run before any further
sphere mechanism work.**

Why this is *most validated* rather than most appealing:

1. **The comparison is same-vehicle, same-mass, same-friction.** Azhar's vehicle
   is a Toyota Yaris at 1097 kg with mu = 0.55; the project's canonical hull is a
   Toyota Yaris at 1100 kg with `floor_friction` 0.55 on all 17 runs
   (`read-directly`). No other benchmark in the whole corpus matches on all three.
2. **It is quiescent.** Every flow-dependent confound the literature names
   (free-surface drawdown, Karman shedding, unsteady drag, underbody suction) is
   absent by construction, so a residual disagreement is numerical.
3. **It has an external falsifier with a stated number**, which CLAUDE.md item 6
   says the project's entire gate set currently lacks.
4. **It is corroborated by a second, separate-origin bracket**, 0.34 to 0.57 m
   across four independent experiments, so a result inside the band is not
   resting on Azhar alone.
5. **The competing route, more grid refinement, is refuted three times over.**
   Zhao Jiang Choo state locking is not remedied by spatial refinement; Zhao 2019
   measures a brink-depth error plateau at 3.44 / 1.90 / 1.88 percent across a 6x
   mesh range; Syamlal 2017 states transient quantities cannot be grid-converged
   at all. The project has already spent a grid ladder and got a non-monotone
   result. A fourth grid sweep is the least validated thing available.

**The immediately following control, and it is not a grid sweep:** hold `dx`
fixed and vary particles-per-cell. Three of the five live candidate mechanisms
(volumetric locking, nodal density oscillation, small-cut starvation) predict the
force error moves with PPC; the current `dx`-only sweep cannot separate any of
them.

### 4.2 For the deliverable

**The route: correct the four submitted-paper defects, replace the class claim
with a labelled two-class sensitivity, and reframe the contribution against AR&R
Project 10's own recommendations 3 and 4 rather than against novelty.**

Why most validated:

1. **Three of the four defects are refuted by files already inside this repo**
   (`read-directly`): the measured clearance, the class table, and the run
   inventory. No new work is required to establish that they are wrong.
2. **The class flip is arithmetically forced, not a judgement call.** D.V = 0.4416
   for `g64_m1100` sits between the two class limits (`inferred`). A referee can
   reproduce it in one line.
3. **The novelty framing is refuted from multiple directions**: 16 enumerated
   prior vehicle-water simulations; a corpus document's own first-of-kind claim
   with its named falsifier met; He 2026 and Azhar 2026 both making 2026 priority
   claims in this exact space. Continuing to lead on novelty is the highest-risk
   available framing.
4. **The AR&R framing is supported by a verbatim primary sentence** (`relayed`,
   read from the report): "an analytical solution (computational model) using
   manufacturer specifications should be suitable for determining stability if
   correct coefficients of friction and drag are selected and the computational
   model is able to be verified against experimental data", followed by a
   five-item recommendation list whose items 3 and 4 are this project. The same
   report disowns its own criteria as "unlikely reliable enough to be adopted
   permanently as safety criteria", which converts "our simulation disagrees with
   AR&R" from a defect into a research question the criteria's own authors named.
5. **The surviving, narrow, defensible technical claim** is: no MPM simulation of
   a full road vehicle in floodwater was found, in two named searched views, with
   the adjacent MPM-vehicle-water precedent being tyre hydroplaning (Zhou 2025,
   Zhou 2026). The SPH half of the old claim is dead and must never be restated.

---

## 5. Per-session prescriptions

Eleven slots. Each names the task, the evidence it rests on, GPU need and
walltime, and the falsifier that kills it. Slots 1 to 6 need no GPU at all and can
run entirely on the Mac against data already on disk.

### Slot 1: flotation ladder against the Azhar benchmark
- **Task.** Run the canonical Yaris hull at 1100 kg in still water across a depth
  ladder bracketing 0.30 to 0.45 m and find the depth at which net vertical force
  on the hull crosses zero (loss of floor contact). Report the crossing depth with
  its resolution and its Mach number.
- **Evidence.** Azhar 2023 section 4.3, 0.35 m SPH against 0.37 m physical, same
  vehicle, same mass, same mu (`relayed`, full text). Independent bracket 0.34 to
  0.57 m from four experiments (`relayed`). CLAUDE.md item 6: no current gate can
  fail for an external reason.
- **GPU and walltime.** GPU required. Batch, not idev. 8 to 10 short quiescent
  runs, request 2 hours on one GH200; a single canonical run is far shorter than
  the 17-run gated sweep because there is no inflow phase.
- **Falsifier.** A crossing depth inside 0.30 to 0.45 m supports the buoyancy path
  being sound and localises the sphere excess to the sphere configuration. A
  crossing far below 0.30 m reproduces the sphere bias on the hull and makes it a
  solver property, not a sphere property. Either outcome is publishable; there is
  no null result.

### Slot 2: particles-per-cell control at fixed dx, on the sphere
- **Task.** Hold `dx` constant at the g64 value 0.1472147236519959 m
  (`read-directly`) and vary particles-per-cell across at least three levels.
  Measure the vertical force error against analytic buoyancy at each. Separately,
  recompute the force integral from particles sampled ONE grid cell away from the
  constrained sphere surface (Zhao 2019's A-A versus B-B diagnostic) using stored
  `rollout.npz` output.
- **Evidence.** Zhao, Jiang, Choo arXiv 2209.02466v3: locking severity is driven
  by material points per element and refinement does not remedy it. Zhao 2019
  section 5.3.1: finer mesh at fixed PPE makes pressure fluctuation worse, raising
  PPE makes it better; section 5.3.2: kinematic fixity over-predicts pressure and
  the contamination is confined to about one element.
- **GPU and walltime.** The B-B re-integration is a Mac job on stored data, zero
  GPU. The PPC sweep needs GPU: batch, 3 hours, one node.
- **Falsifier.** If the force error is flat across PPC at fixed `dx`, volumetric
  locking and nodal density oscillation are both largely ruled out and the
  candidate list shortens by two. If the B-B integral shrinks the excess, the
  fixity is implicated and the mechanism is localised.

### Slot 3: Mach and sound-speed sweep
- **Task.** Sweep artificial sound speed on the fixed-sphere case at fixed
  everything else, and test whether the force error scales as 1/c^2. Separately,
  extract realised maximum water-particle speed from `rollout.npz` for all 17 runs
  and recompute the realised Mach number, which is currently known only from the
  imposed clamp.
- **Evidence.** `inferred` from the inventory read live: c = 12.845 m/s on all 17
  runs, nominal Mach 0.0389 to 0.2336, so 15 of 17 runs sit above the Ma <= 0.1
  ceiling. Amicarelli 2015 p215 and Azhar 2023 p6 both state that ceiling (two
  restatements of one Monaghan lineage, NOT two origins). Negi and Ramachandran:
  WCSPH error is O(M^2). Isik and He 2022 (already in CLAUDE.md): sound speed can
  qualitatively flip a rigid-body outcome, never swept here. Zhao 2019 cleared the
  rule by roughly 116x.
- **GPU and walltime.** The realised-Mach extraction is a Mac job on stored data.
  The `c` sweep needs GPU: batch, 3 hours.
- **Falsifier.** If the force error does not scale as 1/c^2, artificial
  compressibility is ruled out as the mechanism and the list shortens by one. The
  O(M^2) result is stated for WCSPH, so its transfer to weakly compressible
  Newtonian MPM is an inference and must be labelled as one.

### Slot 4: force-accessor reconciliation on a purely hydrostatic configuration
- **Task.** Run both force accessors on a zero-velocity hydrostatic
  configuration, with no flow and no body motion. Record the realised
  body-particle acceleration in g. Determine whether the two accessors differ in
  bandwidth (one effectively low-pass filtered) before concluding either is wrong.
- **Evidence.** Chen et al 2016 `10.1016/J.JFLUIDSTRUCTS.2016.01.008` section
  2.4.1: grid-scale integration "may not be guaranteed" to preserve hydrostatics
  for floating bodies because pressure cell centres are not aligned with the solid
  boundary, and names the static case as the discriminator (`relayed`). Jain et al
  `10.1017/jfm.2021.846`: two legitimate routes to the same impact load differ by
  about 25 percent, with the physical and instrumental causes separated
  (`relayed`). Brizzolara et al `10.1080/17445302.2010.522372`: pressure
  integration "acts like a low-pass filter" (`relayed`, separate origin from Jain).
  Amicarelli and Albano both hard-clamp body-particle acceleration at 10 g because
  the interface pressure reconstruction is unreliable above it, and both report
  realised values (4-8 g, 2-5 g) as evidence of validity.
- **GPU and walltime.** GPU, batch, 2 hours. The bandwidth comparison on stored
  time series is a Mac job.
- **Falsifier.** If both accessors agree on the hydrostatic case, the disagreement
  is a flow or transient artefact, not an accessor defect. If the realised
  acceleration exceeds 10 g, the project is operating in a regime two published
  schemes declared unreliable.

### Slot 5: stationarity and record-length, with two new diagnostics
- **Task.** Add Syamlal's two record-length diagnostics to
  `analysis/stationarity.py`: report whether the autocorrelation summation reached
  K >= 6 tau before K = N, and report `eps_tau/tau = sqrt(2(2K+1)/N)`. Add an
  Augmented Dickey-Fuller test alongside the existing reverse-arrangement test.
  Re-run `analysis/settle_audit.py` on all 25 local runs and report how many fail
  the not-long-enough criterion.
- **Evidence.** Syamlal, Celik and Benyahia 2017 `10.1002/AIC.15868` p21
  (`relayed`, direct read of the accepted manuscript). `inferred`: with CLAUDE.md's
  N_eff 2.9 to 11.0 on N = 91, tau_int is 8.3 to 31.4 frames and 6 tau is 25 to 94
  frames, so the correlated end fails. Oliveira et al pyMSER
  `10.1021/acs.jctc.4c00417` for ADF and for the near-3x spread in truncation
  points across methods. Chodera-family: Clark 2024 `10.1021/acs.jctc.4c01359`
  states MSER truncation is not equilibration detection, which is the primary
  source for a caveat CLAUDE.md already carries. Pan 2017
  `10.1175/JTECH-D-17-0038.1`: reverse-arrangement reliability floor is N >= 10.
- **GPU and walltime.** None. Pure Mac, `metrics.csv` files already on disk.
  30 minutes.
- **Falsifier.** If every run meets K >= 6 tau before K = N, the record-length
  concern dies and the existing N_eff figures stand unqualified. If several runs
  have N_eff below 10, the reverse-arrangement verdicts on those runs are
  unreliable in principle and must be withdrawn.

### Slot 6: the four submitted-paper corrections, plus the class sensitivity
- **Task.** On `overleaf/main:conference_101719_1.tex`: (a) delete "We did not
  measure ground clearance from the mesh" and insert 0.1737 m with its method;
  (b) replace "only the 1100 kg configuration is a genuine class match" with the
  three-axis result and a labelled reversible assumption; (c) re-cite 0.78 and
  "worst-case bed friction" to `smithmodrafelder2019`; (d) change "1.0 to 1.8" to
  "0.98 to 1.83, mean 1.38". Then report the L1 verdict split under BOTH
  small_passenger and large_passenger as a sensitivity, and reconcile the
  `label` column in `data/all_runs_inventory.csv` against
  `docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md`.
- **Evidence.** All four `read-directly` this session; see section 1.1. The class
  audit at `:159` grades a hull SCALED by lam (lengths 4.90 and 5.20 m), and no
  such hull ever entered a run: `n_vehicle` and `solid_volume_m3` are identical
  across all three masses at every grid (`read-directly`).
- **GPU and walltime.** None. 2 hours including the sensitivity recompute.
- **Falsifier.** If a live re-measurement of the hull PLY gives a clearance below
  0.12 m, the class straddle dissolves and (b) is unnecessary. Re-measure before
  editing; 0.1737 m is read from a project document, not from the mesh, in this
  session.

### Slot 7: corpus ingest of the thirteen missing deep searches
- **Task.** Apply `docs/r10/corpus_revision.md` section 2.2 first (six lines added
  to `REPORTS`, zero risk, no parser change), then the phase-1 export procedure
  for the seven searches that exist only in the workspace, then the JSON ingest
  path. Separately, fix the `cited_reader_facing` inflation by excluding raw
  search dumps from `repo_cited_dois()`, and fix the silent-zero in
  `parse_report()`.
- **Evidence.** `relayed` from `docs/r10/corpus_revision.md`, measured
  2026-08-20: 21 completed searches, 8 in `REPORTS`, 13 unreached; 6 of 13 have an
  export on disk and 2 are inside this repo; excluding one raw dump drops
  `cited_reader_facing` from 43 to 34. `read-directly` by me: the 332/319/76/43
  headline reproduces exactly.
- **GPU and walltime.** None. The phase-1 export needs an agent turn with the
  Undermind connector, which a slot may not have (see slot 10). 3 hours.
- **Falsifier.** The check proposed in corpus_revision section 4 goes RED when a
  completed deep search reaches the corpus by no route. If it goes GREEN before
  the ingest lands, the check is wrong, not the corpus.

### Slot 8: prior-art and novelty ledger
- **Task.** Replace CLAUDE.md's "four ... eight or nine" sentence with the
  enumerated 16 prior vehicle-water simulations and their DOIs, naming the three
  searched views (Crossref bibliographic query, Undermind global-corpus semantic
  search, WebSearch). Narrow the surviving claim to "no MPM simulation of a full
  road vehicle in floodwater was found in these views", and cite Zhou 2025
  `10.1063/5.0276643` and Zhou 2026 `10.1016/j.ast.2025.111482` as the adjacent
  MPM-vehicle-water precedent. Rewrite L-7 against He et al 2026. Add Pregnolato
  2017 `10.1016/j.trd.2017.06.020` to the bib and the corpus.
- **Evidence.** `relayed`: 16 enumerated with resolved DOIs. `read-directly`:
  `shah2018`, `pregnolato2017` and `lyu2023` are all ABSENT from the corpus, and
  the paper cites `shah2018`. `relayed`: three independent gap statements
  (Dasallas 2025, Shah 2019, Waheed 2026) that no v_max(depth, velocity) surface
  is published.
- **GPU and walltime.** None. 3 hours.
- **Falsifier.** The MPM-only claim dies the moment anyone finds one MPM road-
  vehicle-in-floodwater paper. Write it so that finding one is cheap, by naming
  the views searched.

### Slot 9: CLAUDE.md and register corrections
- **Task.** Apply, each with its evidence line: item 4(a) premise withdrawal plus
  the CCSA tensor; the CG arithmetic correction (0.6312 m is +13.1 percent above
  the measured 0.558 m, and 0.51 m is the closer estimate); L-4 re-scoped to MPM
  and force with the WRL counterexample named; the Azhar 2026 drag figure replaced
  with +14.0 to +40.7 percent and the 50 percent re-attributed to Klapp 2020 and
  FEMA P-646; L-2 upgraded to primary-source-quoted; L-3 given its two citations
  (Altomare 2017 H/10 minimum, Tafuni 2018 H/25 = 2 percent); L-5's Steffen
  citation resolved to a DOI and a year; L-8 softened to what was actually
  established; the Xiong 2024 SPH mis-description in
  `reference_docs/briefing_vault/11_...:24` corrected to SWE plus DEM-MSM; the
  Amicarelli/Albano pairing collapsed to one lineage; the `azhar2023` bib note
  closed as SET INPUT; the `realized_rho` 309.738 versus 310.494 drift reconciled.
- **Evidence.** Each item is sourced in section 3.1 above.
- **GPU and walltime.** None. 3 hours.
- **Falsifier.** Every item names a file and a number; each dies to a live read of
  that file. Re-read before editing, because this file changes several times a
  night and item text moves.

### Slot 10: fleet infrastructure, the 17-versus-76 connector tier and the launcher
- **Task.** (a) Test the one untried lever on the dead adversarial subagent:
  `CLAUDE_CODE_SUBAGENT_MODEL` is documented as FIRST in the subagent model
  resolution order, ahead of the per-invocation parameter and the frontmatter,
  and the two measurements recorded in CLAUDE.md used levels 2 and 3 only. (b)
  Determine whether `r8_launch.sh`'s flags cause the zero-bridged-connector
  manifest, and either fix the launch or split the routing table into two tiers
  and mark which rows a slot cannot use. (c) Prototype one slot as
  `claude --bg --name <slot> --worktree <slot>` driven by `claude agents --json`
  and `claude logs`, replacing tmux `send-keys`. (d) Give each dispatch a
  `--json-schema` requiring `{claim, evidence, verdict: enum
  verified|refuted|could-not-evaluate, command_run}`.
- **Evidence.** `relayed`, seven slot manifests plus a twenty-session sweep:
  17 prefixes and zero bridged connectors in every R9 slot, 76 and 31 in the main
  checkout. `read-directly` on the installed binary v2.1.234: `claude agents
  --json` exists and "does not require a TTY"; `--bg`, `attach`, `logs`, `stop`,
  `daemon status` and `--json-schema` all exist; a live grep of
  `/Users/josie/can-it-ford/scripts/` for `claude -p`, `claude --bg`,
  `claude agents` or `output-format` returns zero hits.
- **GPU and walltime.** None. 4 hours.
- **Falsifier.** (a) dies if the env-var override still produces
  `deepseek-ai/DeepSeek-V4-Flash:deepinfra`, which would make it a third
  independent lever tested and strengthen the CLAUDE.md finding. (b) dies if any
  R9 slot manifest contains a `mcp__[0-9a-f]{8}-` prefix. (d) dies if the schema
  is rejected: since v2.1.205 an invalid schema hard-fails rather than silently
  degrading.

### Slot 11: the moving-vehicle fork and the friction regime
- **Task.** State explicitly which friction regime each SLIDE verdict claims to
  represent, and run a floor-friction sensitivity across the measured envelope.
  Then set up the Nihei 2025 replication case as the moving/sliding validation
  target, and separately check whether the P-2 passthrough trend breaks at
  V = 1.81 m/s and whether the hull submerges before it slides.
- **Evidence.** `relayed`: Nihei measured unbraked rolling resistance 0.0250 and
  0.0242 against mu_s about 0.30, and the AR&R small-passenger criterion agrees
  with the UNBRAKED curve, not the braked one; critical sliding velocity at 0.30 m
  depth is 0.97 m/s unbraked against 3.42 m/s braked. `read-directly`: the project
  uses `floor_friction` 0.55 on all 17 runs, which is above even the unfactored
  0.50 that AR&R's whole 0.5 -> 0.45 -> 0.36 -> 0.30 safety chain starts from, and
  roughly 22x the measured unbraked value. `relayed`: AR&R's 0.30 is safety-
  factored, not measured, with a documented 40 percent net reduction and a 20
  percent debris-collision factor of safety; measured stationary flooded-road
  values are 0.85 to 1.15 (Yandell 1973) and Smith 2019 measured 0.36 (wet gravel)
  to 0.78 (dry concrete). Moore and Power 2002 put the buoyancy/drag regime switch
  at V = 1.81 m/s, which the project's velocity sweep straddles.
- **GPU and walltime.** The friction sweep needs GPU: batch, 6 hours for a
  5-point sweep at g64. The P-2 trend break and the submerge-before-slide check are
  Mac jobs on `rollout.npz` and the inventory.
- **Falsifier.** If the SLIDE count is flat across 0.30 to 0.78, friction is not
  the lever and the L1/L2 divergence must be attributed elsewhere. Note this is a
  single-parameter sweep and the memory record says a one-at-a-time sweep already
  produced a published-and-retracted false negative, so pair it with the joint
  perturbation of `slide_m`, `slide_speed_ms` and `sustain_frames`.

---

## 6. Vista execution

All of this section is `relayed` from CLAUDE.md and the project memory index,
re-stated here so the eleven prompts do not each have to rediscover it. **None of
it was re-verified against Vista in this session.**

- **Batch, not idev, and this is measured.** Interactive burns 98.5 to 99.1
  percent of Vista node-hours against every gated run, and 95 of 184 interactive
  jobs ended in TIMEOUT. That measurement was re-verified 2026-08-13 and it
  reproduces. LS6 is the opposite: 45 percent interactive, zero batch timeouts.
  **Route GPU work to LS6 where the software stack allows.** The blocker is that
  LS6's `warpmpm` was a 6-line stub and is now simply absent, so anything needing
  `warpmpm` runs on Vista.
- **Do not use idev for file checks, git operations or monitoring.** Those belong
  on the login node. CLAUDE.md states this as a standing rule.
- **A hard login-node blocker.** `from warpmpm.vehicle import load_vehicle`
  BLOCKS on Vista `login1` (600 s wall, 0.75 s CPU, RC=124) and completes in
  78.9 s on a compute node. Near-zero CPU proves a blocking call, not contention.
  Any geometry work that can be done in pure numpy should be AST-extracted and run
  on the Mac instead, validated against known live numbers first.
- **`srun` into a live allocation needs five flags**, revealed one at a time:
  `-p gh -N 1 -n 1 -t <time> --overlap --jobid=<X>`. Without `--overlap` a step
  into a live idev dies. A wrong form left a GH200 at 0 percent utilisation and
  3 MiB of 97,871 MiB for 21 minutes.
- **Apptainer: do not `module load`.** `module load tacc-apptainer` fails over
  non-interactive ssh. Use `/opt/apps/tacc-apptainer/1.4.1/bin/apptainer`
  directly. Genesis on Vista is 1.1.1, not 1.2.0. Note that the 17 canonical runs
  are `warpmpm`, not Genesis, so most of this wave's work needs no container at
  all.
- **Walltime rule.** Request the walltime the job actually needs plus a margin,
  and route anything over an hour to batch. `su_remaining` was 595 at the last
  probe (`relayed`, `canford-tacc` connector, and it moved 597 -> 595 between two
  probes 35 minutes apart, which is the cleanest available proof the connector
  reads live). At 595 SUs the wave's four GPU slots (2 + 3 + 3 + 2 + 6 = 16 node
  hours if all run) are affordable but not unlimited. Allocation expires
  2026-09-30.
- **Architecture rule, keep it.** Run Claude Code on the Mac and reach Vista over
  `ssh` and `scripts/tacc.sh`. That is why the `XDG_RUNTIME_DIR` compute-node bug
  (Claude Code issue #21026) did not apply on 2026-08-19. If anyone ever does run
  Claude Code on a compute node, first line is
  `export XDG_RUNTIME_DIR="/tmp/xdg_runtime_${USER}" && mkdir -p "$XDG_RUNTIME_DIR"`.
- **Before overwriting anything on Vista**, check that machine for local
  modifications and unpushed commits first. Twelve unpushed `realism_track`
  commits exist only on Vista's `$WORK` (`relayed`, memory), and a routine config
  sync would have destroyed 12 unpushed commits on another machine on 2026-08-13.
- **`ssh` ControlMaster saturation.** Roughly 7 concurrent sessions saturate the
  single ControlMaster and drop the whole fleet. With eleven slots, stagger any
  Vista contact rather than having all eleven reach out at once.

---

## 7. Corpus and connector revisions

Both files exist and were read in this session.

### 7.1 `/Users/josie/can-it-ford/docs/r10/corpus_revision.md`

Proposal only; nothing in `analysis/research_index.py`,
`.claude/skills/research-corpus/SKILL.md` or `data/` was edited by that pass. It
proposes, in the order it recommends applying them:

1. **A zero-risk immediate fix**: six lines added to the `REPORTS` constant,
   picking up the six missing searches whose Undermind exports already sit on
   disk. No parser change, no schema change.
2. **A two-phase, connector-out-of-band ingest path** for the seven searches that
   exist only in the workspace. Phase 1 runs inside an agent turn (which has MCP)
   and writes `data/deep_searches/<slug>.json`; phase 2 is the existing plain-shell
   `--build`, which reads that directory. It states plainly that
   `research_index.py` is pure standard library and **cannot call an MCP
   connector**, so any design where the builder fetches from Undermind is not
   implementable.
3. **A fix for the silent zero** in `parse_report()`, which currently returns `{}`
   on a missing path and lets `--build` write a smaller index with no error and no
   non-zero exit. Seven of the eight current `REPORTS` paths live under
   `~/Downloads` and zero live inside the repo.
4. **Replacement text for the `research-corpus` skill**, whose headline claims are
   stale: the skill says 19 completed searches, the live count is 21, and the skill
   implies the deep searches were not exported when six of the thirteen were.
5. **A check that goes RED when a completed deep search reaches the corpus by no
   route**, with source, a named failing input, and a manifest.

The one number in it that changes a published figure: **`cited_reader_facing`
drops from 43 to 34** once the raw Undermind dump in `docs/` is excluded, so the
honest ladder is 34 / 43 / 3.

### 7.2 `/Users/josie/can-it-ford/docs/r10/connector_revision.md`

A correction sheet for both copies of `connector-router/SKILL.md`, probed
2026-08-19 23:12 to 23:22 UTC from the main checkout. It proposes:

1. **Recognising four config layers, not two** (project `.mcp.json`, global
   `~/.claude.json` `mcpServers`, per-project `projects[cwd].mcpServers`, the
   Claude Desktop config, plus 31 bridged claude.ai connectors that are in no
   local file). Grepping `.mcp.json` and concluding a connector is absent is a
   partial view.
2. **Promoting Scholar Gateway to a first-class row.** It reaches Wiley full text
   for the Journal of Flood Risk Management, which Undermind cannot.
3. **Recording the duplicate-surface trap.** Scholar Sidekick exists three times
   and only the lowercase stdio one and the claude.ai one work;
   `mcp__Scholar_Sidekick__` (capitals) returns "You are not subscribed to this
   API", which reads exactly like a dead connector. Scite is dead as a server and
   alive as content by two routes (`mcp__zotero__scite_*`, needing no key, and a
   Scite-schema `search_literature` that returns full-text excerpts when `dois`
   and `term` are passed together).
4. **Correcting the GitHub failure mechanism** (stale token in an `env` block, not
   a missing `headers` block) while keeping the verdict (use `gh`).
5. **Correcting the global skill's "checked, not a fit" list**, most of which is
   not present at all, so listing it as checked overstates what was checked.

### 7.3 The audit of the connector revision, and it matters

`docs/r10/connector_revision_AUDIT_d20.md` accepts most of the above and refutes
its most prominent instruction. The connector file says, in bold, "RETRACT THAT
ROW" for Otter, Slack, Calendar, Drive and pdf-viewer. **Its probes are genuine
and its correction does not transfer**: it probed a session with 76 MCP servers,
and every session that reads the skill it corrects has 17.

The right wording is neither file's: "Absent from every R9 slot session, measured
on seven manifests. Present in the main-checkout session, which has 76 servers.
Do not route a slot to these."

Both files scoped their probe. Only one scoped its conclusion. **That is scope-loss
between measurement and instruction, appearing inside the workflow's own output.**
The eleven prompts must not repeat it: any capability claim in a prompt needs to
say which session tier it applies to.

---

## 8. Platform and Claude Code

### 8.1 Claude Code: the highest-leverage unused capability

**Typed, schema-constrained returns from background sessions.**
`claude --bg` plus `claude agents --json` plus `claude -p --output-format json
--json-schema '<schema>'` (all `read-directly` from `claude --help`,
`claude agents --help` on v2.1.234 and the headless docs). A live grep of
`/Users/josie/can-it-ford/scripts/` for any of `claude -p`, `claude --bg`,
`claude agents` or `output-format` returns **zero hits**.

**Concrete cost of not using it, measured rather than asserted:**
- The current fleet is driven by tmux `send-keys` through `scripts/r8/`. On
  2026-08-19 nine windows fell back to a bare zsh prompt and a sender pasted 4 KB
  of markdown into a shell, which executed it line by line. `claude --bg` never
  talks to a shell, so that failure class cannot occur.
- `~/.pane_signals/*_done` fires on every Stop hook, so it proves liveness and not
  completion, and every pane claim has to be verified against a real artifact.
  `claude agents --json --all` returns actual session state and explicitly does
  not require a TTY.
- The recorded coordinator post-mortem concluded "the fix is a typed tool return,
  not a better instruction". `--json-schema` with a required
  `verdict: verified|refuted|could-not-evaluate` enum makes the distinction
  between "equal" and "could not evaluate" unfakeable at the transport layer.
  That is precisely the defect behind three separate incidents in one night where
  both arms of a comparison errored and the check printed a clean PASS.

**Runner-up, cheap and immediate:** hook `if` conditions. All 14 hooks in
`.claude/settings.json` are unconditional `type: command`, so four Python scripts
run on every Bash, Read, Edit and Write call. `params_check.py` raising inside
`check_bbox_agreement` blocked 34 commit attempts; scoping it to
`Bash(git commit*)` bounds the blast radius without weakening the guard.

### 8.2 Platforms: the highest-leverage unused capability of each

**Weights and Biases: Artifacts and lineage.** `read-directly` from a grep of
`analysis/`, `scripts/` and `simulation/`: `wandb.init` 5, `wandb.log` 4,
`wandb.summary.update` 2, `wandb.login` 2, `wandb.finish` 2, and **zero**
`wandb.Artifact`, `log_artifact`, `use_artifact`, `link_artifact` or sweep
configs. Cost of not using it: CLAUDE.md item 8 records that gate verdicts exist
only in `gates.py` stdout and are never persisted, and item 5 records two
disagreeing displacement measures for the same run (`summary.json` 0.658537
against `rollout.npz` 0.637019 for `g64_m1100`, a 3.4 percent gap). A versioned
artifact with a producing run makes both auditable. Separately, `relayed`: 106
W&B runs each carry exactly ONE history row, so the 91-frame time series that
every stationarity and settle-length finding rests on **has never been logged**.

**GitHub: nothing gates `main`.** `read-directly`: `canford-checks.yml` runs six
checks and marks two (`register_integrity`, `count_claims`) `continue-on-error:
true`, so they cannot fail the build; all four workflows pin actions by mutable
tag; no workflow declares `concurrency`. `relayed`: 461 commits sit unmerged on
origin and 440 more never left this laptop, including the branch carrying the
research-corpus index, the physics-gate test suite and the 6-check CI workflow,
none of which exist on `main`. The unused capability with the best ratio is
`$GITHUB_STEP_SUMMARY` plus `actions/upload-artifact`: it would render the gate
table into the PR where a reviewer sees it and persist the raw stdout past the
log expiry. Note the trap: the `continue-on-error` mask is currently load-bearing,
because `count_claims_check.py` false-BLOCKs in a tracked-only tree. Fix the check
to report NOT-EVALUABLE before removing the mask.

**Hugging Face: the flagship dataset viewer is broken and the Space status note is
stale.** `read-directly`, live API: the Space `josiecerrell/can-it-ford` EXISTS,
is public, is RUNNING on cpu-basic, last modified 2026-08-19T17:46:50Z, and ships
`data/canonical_runs.csv` and `data/load_surface.csv`. The memory note recording
"a Space that never existed" and "kept private until two README claims are
corrected" is stale on the first half and the gate on the second half appears to
have been lifted without confirmation. `relayed`: the public dataset's viewer is
broken by a schema cast error, so its real 35-column data file is invisible and a
4-row summary is being previewed in its place. Also `read-directly` from the HF
docs: **HF DOIs go through DataCite, not Zenodo**, and are documented for models
and datasets only, not Spaces, so the run data must move out of the Space before a
DOI is mintable. And `CITATION.cff` declares ODC-By-1.0 while the Space card
declares bsd-3-clause: two licences are published right now for the same project.

---

## 9. What I am not confident about

Stated explicitly, because a report with no uncertainty section is hiding
something.

1. **Most of this report is second-hand.** I read, live, in this session: the run
   inventory, the corpus index, `vehicle_params.py`, the L1 reconciliation, the
   submitted tex, and the three `docs/r10/` files. Everything about the twenty-odd
   external papers is `relayed` from other readers' reports. I did not open a
   single external PDF. If a reader mis-transcribed a page number or a
   coefficient, I have propagated it.
2. **Nothing here has been adversarially reviewed.** The `physics-skeptic` path is
   dead. Six sessions on 2026-08-18 and 2026-08-19 correctly marked their claims
   UNREVIEWED; this report joins them.
3. **The 16-prior-simulations count is not stable.** It came from three searched
   views and grew from four to eight or nine to sixteen across three passes in
   this project. I would not bet that sixteen is the ceiling. Report it with its
   views named, and expect it to move again.
4. **The paper-defect claims in section 1.1 are strong on items (a) and (b), which
   I verified against live repo files, and weaker on (c) and (d)**, which rest on
   two readers each reporting an absence in a 30-page PDF I did not open. An
   absence in a document I have not read is exactly the kind of claim this project
   warns about. Re-read the AR&R report for the string 0.78 before editing the
   citation.
5. **The 0.1737 m clearance is read from a project document, not from the mesh.**
   The whole class-straddle finding turns on it. Re-measure from
   `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` before it enters
   the paper.
6. **I do not know whether the g64 hull cloud inertia figures (Ixx 1501.5,
   Iyy 395.0, Izz 1685.4) are current.** They are read from CLAUDE.md, not
   recomputed from `kernels/mpm_solver_warp.py:859-871`. Every percentage
   comparison against the CCSA measurement inherits that.
7. **The candidate-mechanism ranking for open question 1 is my judgement, not a
   measurement.** Five mechanisms are live and none has been tested. I have ranked
   volumetric locking first because it has an explicit published statement of
   refinement-insensitivity, which is the project's own observed symptom, but that
   is pattern-matching on a symptom and the project's rules warn against exactly
   that.
8. **The 15-of-17-runs-above-Mach-0.1 figure is a LOWER bound.** It uses the
   imposed clamp velocity, not the realised maximum water-particle speed. If surge
   exceeds the clamp, more runs move up, and I have not extracted the realised
   speeds.
9. **The launcher hypothesis for the 17-versus-76 connector gap is a hypothesis.**
   `relayed`, and its own author says so: which flag or launch path causes it has
   not been isolated.
10. **I did not verify the Vista section against Vista.** All of section 6 is
    relayed from CLAUDE.md and the memory index. `su_remaining` 595 was current at
    a probe roughly a day ago and will have moved.
11. **The GPU walltime estimates in section 5 are guesses.** I have no timing data
    for a quiescent flotation run or a PPC sweep on this hull. Treat them as
    request sizes to be revised after the first job, not as predictions.
12. **The eleven-slot decomposition is a design choice, not a finding.** Slots 2,
    3 and 4 all touch the sphere and could collide; slots 6, 8 and 9 all edit
    documents in overlapping territory and MUST be sequenced, not parallelised,
    given the standing rule against two panes touching one file. If the wave runs
    all eleven concurrently against a shared working tree, the 2026-08-07 breach
    (one session committing another's uncommitted edits) is the expected failure.
