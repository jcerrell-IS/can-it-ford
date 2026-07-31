# Submission Manifest

The reproducibility record for the submitted paper. Every hash, count, and number below was
re-derived live from the artifact on 2026-07-30 evening. Nothing is carried over from a session
summary, including this file's own earlier revisions.

Source of truth throughout is `git show overleaf/main:...`, never a local worktree.

## 1. Submitted commit

| Field | Value |
|---|---|
| Remote | `https://git.overleaf.com/6a5958d10484feadf65a934e`, branch `main` |
| Commit | `32b0d123c3f3ce53aa9594d995a7a86aac930cca` |
| Timestamp | 2026-07-30T19:46:19-05:00 |
| Subject | Make the Fig 4 buoyancy figure traceable to the plan area the plotted model uses |
| Parent | `ff22124983af3eb2617fce56dfdcf335df3382b7` |
| `conference_101719_1.tex` md5 | `f2d28acd7c2771f1992470d867f6fe64` |
| `can_it_ford_references_IEEE.bib` md5 | `f08c29c23801216cb7652179b1b6c740` |

**Re-derived from a clean build of the remote tree:** 7 pages, 0 LaTeX errors, 0 undefined
citations or references, 14 bibitems, braces balanced 241/241, 15 labels against 12 refs with
zero dangling.

## 2. FLAG render count: zero

The raw grep is not the render count, in either direction:

- `grep -c 'FLAG'` returns **3**: lines 11 and 13 (the explanatory comment block) and line 16
  (the `\newcommand` definition).
- `grep -c '\FLAG'` returns **2**: line 13 and line 16 only, because line 11 writes
  "FLAG / PLACEHOLDER" without a backslash.

The macro is never invoked. `pdftotext` over the compiled PDF finds **0** occurrences of
`FLAG:` and **0** of `PLACEHOLDER:`. Same result for `\PLACEHOLDER`.

## 3. Figures

Seven `\includegraphics` targets, all present in the remote tree. `file` reports the **true**
format, which is not always what the extension claims.

| # | File | md5 | Extension | True format | Generator |
|---|---|---|---|---|---|
| 1 | `pipeline_diagram_v2.pdf` | `6fd2a9b724c3eb1cf01caf1c2a579d62` | .pdf | PDF 1.7 | `analysis/paper_fig_pipeline_diagram_v2.py` |
| 2 | `l0l1_two_rules_v2.pdf` | `4faed270266265673fc0a50884eac027` | .pdf | PDF 1.7 | `analysis/paper_fig_l0l1_two_rules_v2.py` + `analysis/svg_to_paper_pdf.py` |
| 3 | `L1_three_class_corrected.png` | `5d4b1b1b3a4c93c2e82b422f9d3f63a8` | **.png** | **JPEG (JFIF 1.02)** | PROVENANCE_PARTIAL |
| 4 | `force_balance.jpg` | `c5b58510de2ace950d22b36627cd698c` | .jpg | JPEG (JFIF 1.02) | **PROVENANCE_MISSING** |
| 5 | `l2_divergence_real_v2.pdf` | `1d809c9b8d2ef8238160074e79e7016e` | .pdf | PDF 1.7 | `analysis/paper_fig_l2_divergence_v2.py` + `analysis/svg_to_paper_pdf.py` |
| 6 | `mass_grid_sweep_v2.pdf` | `a7c192b82fc986d4bcfa79b227d71f00` | .pdf | PDF 1.7 | `analysis/paper_fig_mass_grid_sweep_v2.py` + `analysis/svg_to_paper_pdf.py` |
| 7 | `l2_render_g64_m1100_f0045.png` | `688281d14e3c394de9bd8cac252541c9` | .png | PNG, 1541x664 RGB | PROVENANCE_PARTIAL |

### Extension-versus-format

**One file is mislabelled, not two.** `L1_three_class_corrected.png` carries JPEG data under a
`.png` extension. `force_balance.jpg` is JPEG data correctly named; an earlier lineage carried
those same bytes as `force_balance.png` and that was corrected before submission. pdfTeX
compiles the mislabelled file without error because its PDF backend sniffs content rather than
trusting the extension, but the mismatch is real and would break stricter toolchains.

Three further PNGs sit in the remote tree unreferenced by the tex and do not ship in the PDF:
`fig1.png` (341x297), `pipeline_diagram.png` (1613x512, superseded by `_v2`), and
`l2_divergence_real_v2.png` (1509x995, the raster predecessor of the vector PDF).

### Figure 3, PROVENANCE_PARTIAL

No script writes the filename `L1_three_class_corrected.png`. `analysis/plot_l1_three_class.py`
regenerates equivalent content from `data/scenario_sweep.csv` under a different output name and
self-verifies its counts. Those counts were re-derived directly from the CSV this pass and
match: **small_passenger 14, large_passenger 19, large_4wd 26**.

### Figure 4, PROVENANCE_MISSING

No generator exists on the submitted branch. `analysis/paper_fig_force_balance_v2.py` exists
only on the unmerged branch `claude/festive-goodall-e08861` and was not grafted in. The plotted
curve cannot be regenerated from the submitted tree. This is the weakest provenance link in the
paper. See section 6 for an independent arithmetic check of its quoted quantities.

### Figure 7, PROVENANCE_PARTIAL

No script writes `l2_render_g64_m1100_f0045.png`. The submitted bytes are md5-identical to
`renders/yaris_render_s1/frame_check_f0045_poster_crop_no_artifact.png`, which no script writes
either and which `.gitignore` line 14 (`renders/`) excludes from the public repo. The upstream
simulation **is** traceable: `renders/yaris_render_s1/render_pv3.py --run g64_m1100
--hero-only 45`. The unscripted step is the crop. Full analysis in
`docs/RENDER_ASSET_INVENTORY_2026-07-31.md`.

## 4. Citations

Fourteen keys cited, all fourteen resolve in the remote bib. A fifteenth entry, `xiong2024`, is
present, correct, and uncited, so it does not print.

Every DOI-bearing entry was re-resolved live this pass and compared field by field. **Zero
mismatches in author list, title, venue, volume, issue, or pages.** Crossref `relation`,
`update-to`, and `updated-by` were checked on all seven: **no retractions, corrections, errata,
or expressions of concern anywhere in the bibliography.**

| Key | DOI / ID | Route | Verification and locator |
|---|---|---|---|
| `smithmodrafelder2019` | 10.1111/jfr3.12527 | Crossref + Scite full text | Smith; **Benjamin D.** Modra; Felder, JFRM 12(S2), print 2019-11. Equations run to **(4)**, which yields flow velocity V, not displacement. Scite tally 51 total, 1 supporting, 0 contrasting |
| `shah2018` | 10.1051/matecconf/201820307003 | Crossref + local PDF | **Syed Muzzamil** Hussain Shah, Mustaffa, Kim, Yusof. MATEC Web Conf. 203:07003. Title page of `~/Zotero/storage/4HIZ7KZB/` reads "Syed Muzzamil Hussain Shah1,\*" |
| `xia2014` | 10.1007/s11069-013-0889-2 | Crossref | **Four authors**: Junqiang Xia; Roger A. Falconer; Xuanwei Xiao; **Yejiang Wang**. Nat. Hazards **70(2) 1619-1630**. `published-print` 2014-01, `published-online` 2013-10-11. Bib's 2014 is the print year and is correct |
| `azhar2023` | 10.1111/jfr3.12885 | Crossref + local PDF | Azhar; Pauwels; Bui, JFRM 16(2). Local copy `~/Zotero/storage/6Y7VPLP7/` |
| `xiong2024` | 10.1029/2023WR036739 | Crossref + local PDF | Xiong; Liang; Zheng; Wang; Tong, WRR 60(10). Local copy `~/Zotero/storage/QTUHXT5R/`. **Uncited** |
| `heydinger1999sae` | 10.4271/1999-01-1336 | Crossref | **Six authors**: Heydinger; Bixel; Garrott; Pyne; Howe; Guenther, 1999. Full text closed, proven twice (section 5) |
| `ccsa2016yaris` | 10.13021/G8JS5D | **DataCite only** | "2010 Toyota Yaris Finite Element Model Validation Coarse Mesh", George Mason University, 2016. Crossref 404s on this DOI, confirmed; it is a DataCite registration |
| `shand2011arr` | no DOI | Local PDF | `citations/ARR_Project_10_Stage2_Report_Final.pdf`, **p.24 Table 3** for the 0.30 / 0.45 / 0.60 m²/s class caps. Title page confirms "PROJECT 10 / Appropriate Safety Criteria for **Vehicles**", not the people report |
| `nws_tadd` | no DOI | Live web, HTTP 200 | `weather.gov/safety/flood-turn-around-dont-drown`. Verbatim: "6 inches ... can knock over an adult", "12 inches ... to carry away most cars" |
| `fred2026` | arXiv:2605.22018 | Local PDF | `~/Zotero/storage/XGPFETGF/`. Title page confirms Malone, Demmel, Glaser and **arXiv:2605.22018v2 [cs.CV] 2 Jun 2026**. Preprint, no DOI |
| `genesis2024` | no DOI | Crossref + OpenAlex negative | **No peer-reviewed paper exists**, re-checked today across both indexes. `@software` is the correct form |
| `kerbl20233dgs` | arXiv:2308.04079 | Local PDF | `~/Zotero/storage/RCLCCV3Q/` |
| `xie2023physgaussian` | arXiv:2311.12198 | Local PDF + source | `~/Zotero/storage/IH89VU97/`. Backend claim confirmed at source, section 5 |
| `thorpe2026pvwm` | arXiv:2605.30542 | Local PDF | `~/Zotero/storage/ND8PGIDC/`. "autonomous orchestration remains an open research problem" |
| `hsiao2025nerfmpm` | arXiv:2507.09005 | Local PDF | `~/Zotero/storage/FL7N6U4C/`. Abstract: "error within 2 degrees" |

**Near-identical-name trap, checked deliberately.** A different researcher, **Syed *Hamid*
Hussain Shah**, publishes adjacent flood-vehicle work with overlapping co-authors (Mustaffa,
Martínez-Gomariz), including Al-Qadami et al. 2021, `10.1007/s11069-021-04949-6`. The bib has
the right person: Crossref, the local PDF's title page, and the bib all read **Muzzamil**.

## 5. Reported numbers, with the command that reproduces each

| Number | Source | Reproduced |
|---|---|---|
| 17 runs | `data/all_runs_inventory.csv` | 17 rows excluding header |
| 7 of 17 exceed the 10% passthrough gate | same | `passthrough_max_frac > 0.10` on 7 of 17 |
| 15.8807% peak passthrough | same | `max(passthrough_max_frac) = 0.158807` |
| 70 scenarios | `data/scenario_sweep.csv` | 70 rows excluding header |
| 7 of 70 FORD at 0.15 m | same | `L0_verdict == FORD` on 7 |
| 21 of 70 at 0.30 m | same | stated in Table I as the counterfactual |
| 37 of 70, bare rule | same | `L1_haz_product_only == FORD` on 37 |
| 14 of 70, joint rule | same | `L1_verdict == FORD` on 14; `L1_verdict_small_passenger` also 14, identical on all rows |
| 14 / 19 / 26 per class | same | `L1_verdict_small_passenger` 14, `_large_passenger` 19, `_large_4wd` 26 |
| 23 reclassified, split 5 / 10 / 8 | same | 37 − 14 = 23; hazard-only 5, depth-only 10, both 8 |
| 9 conditions, 5 of 9 agreement | `data/l2_results_from_wandb.csv` | 9 rows; 55.6% |
| mu sweep | `data/mu_sweep_results.csv` | 4 rows |
| hull 3.542739 m³ | `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` | constant in `analysis/plot_geometry_pipeline.py:12`, `analysis/render_v1/gates.py:11`, `g0_validate.py:12`, `s2_gridgate.py:7` |
| bbox 11.353268 m³ | same PLY | measured extent 4.2826 x 1.7464 x 1.5180 m |
| 10.7457 m³ nominal prism | `vehicle_params.py` | `"bbox_m": (4.30, 1.70, 1.47)`; 4.30 x 1.70 x 1.47 = 10.7457 |

Reproducing command for the CSV figures:

```bash
python3 -c "import csv;r=list(csv.DictReader(open('data/scenario_sweep.csv')));print(len(r), sum(1 for x in r if x['L0_verdict']=='FORD'), sum(1 for x in r if x['L1_haz_product_only']=='FORD'), sum(1 for x in r if x['L1_verdict']=='FORD'))"
```

**`data/all_runs_inventory.csv` is excluded from git by `.gitignore` line 10 (`data/*`)** and is
therefore not visible in the public GitHub repo, although the paper cites it by name in two
places. This remains the most consequential reproducibility gap.

## 6. Fig. 4 arithmetic, independently re-derived

Checked with Wolfram rather than by re-reading the caption.

| Quantity | Caption | Re-derived | Agrees |
|---|---|---|---|
| Vehicle weight, 1100 kg at g = 9.81 | 10.79 kN | **10.79 kN** (10790 N) | yes |
| Buoyancy at 0.30 m | 15.99 kN | requires waterplane area **A = 5.4332 m²**: 1000 × 9.81 × 5.4332 × 0.30 = 15990 N | yes, by construction |
| Flotation depth, buoyancy = weight | "about 0.20 m", critical velocity to zero "near 0.19 m" | `1100 / (1000 × 5.4332)` = **0.202459 m** | yes |

**The three figures are mutually consistent**, and the waterplane area they jointly imply is
**5.4332 m²**. Against the nominal 4.30 x 1.70 = 7.31 m² footprint that is a fill factor of
**0.7433**, which is what the caption's "roughly three quarters of its bounding-box footprint"
means. The caption states 5.4332 m² explicitly, so the figure is self-consistent even though its
generator is missing.

An independent literature cross-check is now available and was not previously: Al-Qadami et al.
2023 (`10.3390/su151713262`) reports **floating instability at 0.38 m** for a full-scale
medium-size passenger vehicle, with an analytic form h_b = M_c/(ρ l_c b_c) + GC. That formula
needs vehicle **ground clearance**, which remains unverified (ledger flag A5), so the comparison
cannot be completed yet. See `docs/LIT_QUEUE_2026-07-30.md` item 8.

## 7. Known limitations, in the paper's own words

- On Fig. 4: "This figure should therefore be read as establishing the *shape* of the
  drag-versus-friction argument, not as a calibrated flotation prediction."
- On the L2 threshold: "an internal numerical detector for onset of motion ... not itself an
  empirical stability criterion."
- On the mass block: "the block is a controlled mass-sensitivity study on one geometry rather
  than a comparison of three vehicles ... only the 1100 kg configuration is a genuine class
  match."
- On grid convergence: "no single multiplier characterizes the mass effect and none is quoted
  here. Any mass-sensitivity claim from this work is therefore directional only."
- On passthrough: "7 of the 17 runs exceed a 10% particle-passthrough gate, reaching 15.9% at
  3.0 m/s; these are flagged, not excluded."
- On the pilot CSV: "it is not cleanly enough run-labelled to use as it stands. Reconciling that
  file against an explicit L1 calculation remains outstanding."
- On the silhouette asset: "all three classes share one silhouette, so cross-class comparisons
  involving this asset reflect scaled mass and footprint, not distinct vehicle geometry."

## 8. Self-corrections made 2026-07-30

Four errors were found and fixed in the paper on this date. Recorded because a manifest that
only lists what is right is not a provenance record.

1. **The Smith Eq. 6 misattribution.** Table I attributed the 0.05 m L2 threshold to
   "Smith-Modra-Felder (2019) Eq. 6." That paper's equations run to (4), and Equation (4) yields
   a flow velocity, not a displacement. The attribution was removed and the threshold reframed
   as a solver-internal detector, cited to Shah 2018 and Xia 2014 for the underlying sliding
   physics rather than for the number. The bib entry additionally carried the wrong given name
   ("Modra, Brianna D.") and the wrong title; both were corrected against Crossref.
2. **The NWS pedestrian-versus-vehicle depth.** L0's 0.15 m cutoff was presented as a vehicle
   threshold. It is the NWS **pedestrian** figure; the vehicle figure is twice that at 0.30 m.
   The paper now states both, justifies 0.15 m as the deliberate conservative bound, and
   quantifies the cost as 7 of 70 admitted instead of 21.
3. **The heydinger scope narrowing.** The sedan/SUV/pickup grouping was implied to come from
   NHTSA/SAE. The source is a per-vehicle inertial database through November 1998 with no Yaris
   and no matched triple. Lines 96 and 142 now say the grouping "is ours" and "carries no
   authority from the source beyond the per-vehicle measurements themselves."
4. **The nominal-versus-measured prism.** The 10.7457 m³ prism was presented as the hull's
   bounding box. It is the vehicle's published nominal specification (4.30 x 1.70 x 1.47 m). The
   hull's own measured extent is 4.2826 x 1.7464 x 1.5180 m, or 11.3533 m³, giving a fill factor
   of 0.312 rather than 0.33. Both are now stated, with a note that the distinction does not
   change the conclusion because both prisms overstate displacement.

**A correction invisible in any rendered PDF.** IEEEtran abbreviates given names to initials, so
"Brianna D." and "Benjamin D." both render as "B. D. Modra". Item 1's author error was only ever
detectable in the `.bib` source. What was visibly wrong in the pre-correction build was the
article *title*.

## 9. Stale artifacts on the remote, not part of this submission

The Overleaf git bridge does not commit build output, so the two PDFs in the project tree are
hand-uploaded. Both were last touched at commit `4001460`, 2026-07-30T04:49:55Z.

- `conference_101719.pdf` is 3 pages and is the **unmodified IEEE template**: it opens
  "Conference Paper Title\*" with authors "1st Given Name Surname". It is not this paper.
- `conference_101719_preview.pdf` is 5 pages, a genuine but superseded build. Its internal
  `CreationDate` is **Fri Jul 17 05:15:02 2026 CDT**, so it was built 13 days before it was
  committed. It renders **10 `[FLAG:` markers**, still contains the "Eq. 6" attribution, still
  reads "Department of Integrated Sciences" without "Kravis", and its reference [4] carries the
  superseded title "Full-scale testing of vehicle floatation and stability in flowing
  floodwater".

Anyone browsing the repository sees those PDFs, not the current build. Neither was rebuilt or
replaced during this pass.
