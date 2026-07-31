# Submission Manifest, 2026-07-31

What was submitted, and what backs every number in it. Every hash and count below
was read from the live artifact at the time of writing, not copied from a summary.

## 1. Commit

| Field | Value |
|---|---|
| Branch pushed | `paper/final-graft` to `overleaf/main` |
| Commit | `32b0d123c3f3ce53aa9594d995a7a86aac930cca` |
| Short | `32b0d12` |
| Committed | 2026-07-30 19:46:19 -0500 |
| Parent (previous remote head) | `ff22124983af3eb2617fce56dfdcf335df3382b7` |
| Build source | `conference_101719_1.tex`, NOT `paper/conference_101719.tex` |
| Local build | pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026), 7 pages, 0 errors, 0 undefined |

## 2. Source file hashes

| File | MD5 |
|---|---|
| `conference_101719_1.tex` | `f2d28acd7c2771f1992470d867f6fe64` |
| `can_it_ford_references_IEEE.bib` | `f08c29c23801216cb7652179b1b6c740` |

## 3. Figures

Seven figures, seven native LaTeX captions. Four are true vector (zero image
XObjects). Three are raster and are listed as such.

| # | File | MD5 | Vector | Generator |
|---|---|---|---|---|
| 1 | `pipeline_diagram_v2.pdf` | `6fd2a9b724c3eb1cf01caf1c2a579d62` | yes | `analysis/paper_fig_pipeline_diagram_v2.py` |
| 2 | `l0l1_two_rules_v2.pdf` | `4faed270266265673fc0a50884eac027` | yes | `analysis/paper_fig_l0l1_two_rules_v2.py` |
| 3 | `L1_three_class_corrected.png` | `5d4b1b1b3a4c93c2e82b422f9d3f63a8` | no | PROVENANCE_PARTIAL, see below |
| 4 | `force_balance.jpg` | `c5b58510de2ace950d22b36627cd698c` | no | PROVENANCE_MISSING, see below |
| 5 | `l2_divergence_real_v2.pdf` | `1d809c9b8d2ef8238160074e79e7016e` | yes | `analysis/paper_fig_l2_divergence_v2.py` |
| 6 | `mass_grid_sweep_v2.pdf` | `a7c192b82fc986d4bcfa79b227d71f00` | yes | `analysis/paper_fig_mass_grid_sweep_v2.py` |
| 7 | `l2_render_g64_m1100_f0045.png` | `688281d14e3c394de9bd8cac252541c9` | no (MPM render, legitimately raster) | `analysis/make_poster_figures.py` |

**Figure 3, PROVENANCE_PARTIAL.** No script in the repository writes the filename
`L1_three_class_corrected.png`. `analysis/plot_l1_three_class.py` regenerates
equivalent content from `data/scenario_sweep.csv` under a different output name
and self-verifies its counts (small_passenger=14, large_passenger=19,
large_4wd=26). Regenerated as a true vector PDF on 2026-07-30 and confirmed to
match; the raster file was retained to avoid a late figure swap.

**Figure 4, PROVENANCE_MISSING.** No generator exists on the submitted branch.
`analysis/paper_fig_force_balance_v2.py` exists only on the unmerged branch
`claude/festive-goodall-e08861` and was not grafted in. The plotted curve cannot
be regenerated from the submitted tree. Its quoted buoyancy of 15.99 kN at
0.30 m follows from an effective plan area of 5.4332 m2, which the caption now
states explicitly, and not from the nominal 4.30 x 1.70 m box the same caption
quotes (that box would give 16.13 kN). This is the weakest provenance link in
the paper.

## 4. Citations

Fourteen keys cited. All resolve; zero undefined citations at build.

| Key | DOI / ID | Status |
|---|---|---|
| `smithmodrafelder2019` | 10.1111/jfr3.12527 | Crossref-verified 2026-07-30. Title and author corrected this session: was "Full-Scale Testing of Vehicle Floatation and Stability in Flowing Floodwater" / "Modra, Brianna D."; actual is "Full-scale testing of stability curves for vehicles in flood waters" / "Modra, Benjamin D." |
| `shah2018` | 10.1051/matecconf/201820307003 | Crossref-verified 2026-07-30 |
| `xia2014` | 10.1007/s11069-013-0889-2 | Crossref-verified 2026-07-30. Print issue Nat. Hazards 70(2) 2014; Crossref issued date is 2013 (online first) |
| `azhar2023` | 10.1111/jfr3.12885 | Crossref-verified 2026-07-30. Placeholder author/title replaced with Azhar, Pauwels, Bui |
| `ccsa2016yaris` | 10.13021/G8JS5D | DataCite-verified per `docs/CITATION_AUDIT_2026-07-30.md` |
| `heydinger1999sae` | 10.4271/1999-01-1336 | DOI present; scope narrowed in text at tex lines 96 and 142 |
| `shand2011arr` | ISBN 978-0-85825-948-5 | Report read directly; depth limits 0.3 / 0.4 / 0.5 m confirmed against page text |
| `nws_tadd` | URL | Both the 6-inch and 12-inch figures now stated in Table I |
| `thorpe2026pvwm` | arXiv:2605.30542 | per `docs/CITATION_AUDIT_2026-07-30.md` |
| `hsiao2025nerfmpm` | arXiv:2507.09005 | per `docs/CITATION_AUDIT_2026-07-30.md` |
| `kerbl20233dgs` | arXiv:2308.04079 | per `docs/CITATION_AUDIT_2026-07-30.md` |
| `xie2023physgaussian` | arXiv:2311.12198 | per `docs/CITATION_AUDIT_2026-07-30.md` |
| `genesis2024` | no DOI | Project-maintainer citation format; no peer-reviewed paper exists |
| `fred2026` | see bib | per `docs/CITATION_AUDIT_2026-07-30.md` |

`xiong2024` (10.1029/2023WR036739) remains in the bib but is cited zero times,
so it does not render. Not an error; noted so a reader does not expect it.

## 5. Data backing the reported numbers

| File | Rows | MD5 | Backs |
|---|---|---|---|
| `data/scenario_sweep.csv` | 70 | `890984346a52ed4a6ae0803894131e6e` | Fig 2 (37 bare, 14 joint, 23 reclassified as 5 hazard / 10 depth / 8 both, 0 reverse, 7 standing water), Fig 3 (14 / 19 / 26), Table I L0 gates (7 at 0.15 m, 21 at 0.30 m) |
| `data/l2_results_from_wandb.csv` | 9 | `a4620ad5105041801e31946754fbe18b` | Fig 5, L1 vs L2 agreement 5 of 9 (55.6%) |
| `data/all_runs_inventory.csv` | 17 | `6d9125aaf297a1b6b6d39d13bdf70221` | Fig 6 and Section IV-C: 9 `sweep=mass_grid` rows, masses 1100/1609/2337 kg at n_grid 48/64/96, 7 of 17 over the 10% passthrough gate, max 15.9% at 3.0 m/s |
| `data/mu_sweep_results.csv` | 4 | `849800817e089a88db963074bc45d782` | The friction sweep: 0.399, 0.3957, 0.3953 m at mu 0.3/0.5/0.7; 0.3283 m at mu 0.0 |

`data/all_runs_inventory.csv` is excluded from git by `.gitignore` line 10
(`data/*`) and is therefore NOT visible in the public GitHub repo, though the
paper cites it by name in two places. Resolving that is an open item.

## 6. Remaining FLAGs

**Zero.** Raw `grep -n '\FLAG'` on the submitted tex returns 2 lines: the
`\newcommand` definition on line 16 and a comment on line 13 that names the macro
in prose. Neither renders. Same for `\PLACEHOLDER`: 2 lines, 0 rendered. Verified
against the compiled PDF, which contains zero occurrences of the string `FLAG:`.

## 7. Known gaps at submission

1. Figure 4 has no generator on the submitted branch (see section 3).
2. `data/all_runs_inventory.csv` is gitignored and not publicly visible.
3. `conference_101719.pdf` and `conference_101719_preview.pdf` on the remote are
   stale build output. The first is the untouched 2019 IEEE template (3 pages,
   "Conference Paper Title*"). The second is a 2026-07-17 build carrying 10
   rendered FLAG markers and the removed Smith-Modra-Felder "Eq. 6" attribution.
   Anyone browsing the repo sees those, not the current build.
