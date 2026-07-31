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
| 7 | `l2_render_g64_m1100_f0045.png` | `688281d14e3c394de9bd8cac252541c9` | no (MPM render, legitimately raster) | PROVENANCE_PARTIAL, see below |

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

**Figure 7, PROVENANCE_PARTIAL.** Corrected 2026-07-30 after re-checking against
the tree: `analysis/make_poster_figures.py` exists but does not reference this
figure, and no script in the repository writes the filename
`l2_render_g64_m1100_f0045.png`. The submitted bytes are md5-identical to
`renders/yaris_render_s1/frame_check_f0045_poster_crop_no_artifact.png`, which no
script writes either and which `.gitignore` line 14 (`renders/`) excludes from the
public repo. What *is* traceable is the upstream simulation and its frame:
`renders/yaris_render_s1/render_pv3.py --run g64_m1100 --hero-only 45` renders
frame 45 of that run, and the run's own `summary.json` independently confirms every
quantity the caption states (1100 kg, requested depth 0.30 m against realized
0.2944 m, 1.5 m/s, `n_grid` 64, four water layers, 48367 water and 8905 vehicle
particles, final displacement 0.6585 m, peak passthrough 10.67 percent). The gap is
the cropping step between render and submitted file, which is unscripted, and the
fact that its immediate source is not publicly visible.

So three of the seven figures have provenance gaps, not two: 3, 4, and 7.

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
2. Figure 7's cropping step is unscripted and its source file is gitignored
   (see section 3). The upstream run and every caption quantity are traceable.
3. `data/all_runs_inventory.csv` is gitignored and not publicly visible.
4. `conference_101719.pdf` and `conference_101719_preview.pdf` on the remote are
   stale build output. The first is the untouched 2019 IEEE template (3 pages,
   "Conference Paper Title*"). The second is a 2026-07-17 build carrying 10
   rendered FLAG markers and the removed Smith-Modra-Felder "Eq. 6" attribution.
   Anyone browsing the repo sees those, not the current build.

## 8. Post-push verification against the remote

Run 2026-07-30 after the push, reading only from `git show overleaf/main:...`, never
from a local branch.

| Check | Result |
|---|---|
| Remote head (`git ls-remote overleaf main`) | `32b0d123c3f3ce53aa9594d995a7a86aac930cca` |
| Committed | 2026-07-30T19:46:19-05:00 |
| `conference_101719_1.tex` md5 on remote | `f2d28acd7c2771f1992470d867f6fe64` |
| `can_it_ford_references_IEEE.bib` md5 on remote | `f08c29c23801216cb7652179b1b6c740` |
| `\includegraphics` targets present in remote tree | 7 of 7 |
| Cite keys resolving in remote bib | 14 of 14 |
| Clean build from the remote tree | 7 pages, 0 errors, 0 undefined, 14 bibitems |
| Rendered `FLAG:` / `PLACEHOLDER:` in the PDF | 0 / 0 |
| Braces balanced, dangling `\ref` | balanced, none (15 labels, 12 refs) |

On the FLAG count specifically: `grep -c 'FLAG'` over the remote tex returns **3**,
and `grep -c '\FLAG'` returns **2**. Neither is a render count. Line 11 and line 13
are the explanatory comment block and line 16 is the `\newcommand` definition; the
macro is never invoked, so the true rendered count is **0**, confirmed by
`pdftotext` over the compiled PDF.

On the stale preview PDF: its internal `CreationDate` is Fri Jul 17 05:15:02 2026
CDT, which is the build date section 7 refers to. It was *committed* later, at
`4001460` on 2026-07-30T04:49:55Z. Both dates are correct and describe different
events.

One further note for anyone auditing the citation fix: the Modra given-name
correction is **invisible in any rendered PDF**. IEEEtran abbreviates given names to
initials, so "Brianna D." and "Benjamin D." both render as "B. D. Modra". The error
was only ever detectable in the `.bib` source. What was visibly wrong in the stale
build was the article *title*.
