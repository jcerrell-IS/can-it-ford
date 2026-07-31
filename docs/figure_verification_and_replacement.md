# Figure verification and replacement

Read-only on the paper. `conference_101719_1.tex` and the bib are untouched, nothing
pushed. Branch `analysis/failure-modes`, cut from `overleaf/main` at `bbd5bd8`.

`PY` = `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3`.
`R` = `/Users/josie/can-it-ford`.

---

## 1. Confirming the prior verification

Live Mac copy `data/scenario_sweep.csv`, **10 columns**, 70 rows. The 5-column
project-knowledge copy was not used.

```
md5 $R/data/scenario_sweep.csv
```

**md5 = `890984346a52ed4a6ae0803894131e6e`**, 4435 bytes, mtime 2026-07-29 18:25:47.

The current Fig. 3 footer reads, via `pdftotext -layout L1_three_class_corrected.pdf`:

> Data: data/scenario_sweep.csv, md5 890984346a52, 4435 bytes, 2026-07-29 18:25:47 CDT.

All three fields match the live file. **The figure is not stale.**

Counts read from the stored `L1_verdict_*` columns, never recomputed:

| Quantity | Expected | Measured | |
|---|---|---|---|
| small passenger FORD | 14 | 14 | match |
| large passenger FORD | 19 | 19 | match |
| large 4WD FORD | 26 | 26 | match |
| all three ford | 14 | 14 | match |
| 4WD + large only | 5 | 5 | match |
| 4WD only | 7 | 7 | match |
| no class fords | 44 | 44 | match |
| class-sensitive | 12 | 12 | match |
| small subset-of large subset-of 4WD | TRUE | TRUE | match |

Partition sums to 70. Zero mismatches.

### A trap found while building Section 5

The instruction to read stored columns rather than recompute has a concrete technical
justification, which the new script's assertion surfaced independently. Recomputing the
hazard product inline as `depth_m * velocity_ms` gives, in IEEE754 double precision:

```
0.1 * 3.0 = 0.30000000000000004      (fails <= 0.30)
0.2 * 1.5 = 0.30000000000000004      (fails <= 0.30)
0.2 * 3.0 = 0.6000000000000001       (fails <= 0.60)
0.4 * 1.5 = 0.6000000000000001       (fails <= 0.60)
```

The stored `L1_haz` column holds exactly `0.3` and `0.6`, so it compares correctly.
Anyone rebuilding this figure by recomputing the product silently gets
**12 / 19 / 24** instead of 14 / 19 / 26. The new generator records this as
`float_trap_cells_if_product_recomputed_inline` and asserts against the stored columns.

---

## 2. The force-balance friction finding

### 2a. Arithmetic

Wolfram Alpha, `979/2796` = **0.35014306...**, so mu = **0.350**.

The figure legend is internally consistent, which is worth stating because it means the
0.35 is a deliberate parameter and not a plotting slip. With the caption's own numbers,
weight 1100 kg x 9.81 = 10791 N and effective plan area 5.4332 m2:

Wolfram, `1000 * 9.81 * 5.4332 * 0.15` = **7994.95 N** buoyancy at 0.15 m.
Then N = 10791 - 7994.95 = **2796.05 N**, matching the legend's 2796 N exactly, and
0.35 x 2796 = 978.6 N, matching the legend's 979 N.

### 2b. These are different quantities

**0.55 is a solver boundary parameter.** `renders/yaris_render_s1/sim_standing.py:76`:

```
fps=30, floor_friction=0.55, settle_frames=8, device="auto",
```

applied at line 132 to the MPM ground plane:

```
s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
```

and re-declared as the CLI default at line 227 (`--floor-friction`, default 0.55). The
column `floor_friction` is 0.55 on all 17 rows of `data/all_runs_inventory.csv`.

**0.35 is an analytical Coulomb coefficient.** It exists only as the ratio
F_fric/N = 979/2796 implied by `force_balance.jpg`'s own legend. It is a tyre-road
friction coefficient in a hand force balance, not a boundary condition on a grid.

Both sit inside the 0.3 to 0.55 physical band that project CLAUDE.md attributes to
Azhar et al. 2023, so neither is implausible. They are simply not the same number doing
the same job, and the paper currently states only 0.55.

### 2c. Where 0.35 came from: no generator survives

`force_balance.jpg` (md5 `c5b58510de2ace950d22b36627cd698c`, 94526 bytes, 1568x672
JPEG) has **no generator on `overleaf/main`**. Three of the repo's own audit documents
reached this independently:

- `docs/CITATION_AUDIT_2026-07-30.md:485` "has no generator and is a JPEG"
- `docs/SUBMISSION_MANIFEST_2026-07-31.md:69` `PROVENANCE_MISSING`
- `docs/POSTER_ASSET_TABLE.md:60` "NONE FOUND. ORPHAN", "no producer in the tree"

The only candidate generator anywhere in the tree is
`.claude/worktrees/amazing-kowalevski-9df04d/analysis/paper_fig_force_balance_v2.py`.
It **did not produce this figure**:

| Constant | v2 generator | Shipped figure implies |
|---|---|---|
| `MU_PRIMARY` | 0.30 | 0.350 |
| `C_D` | 1.38 | approx 1.06 |

Its `MU_BAND` is (0.30, 0.78) and its `C_D` carries the attribution "Smith, Modra &
Felder 2019, 1:18 scale Toyota Yaris flume measurement", which is the same C_D=1.38
regime attribution already committed as a known failure under `a0ea6e7` (DO-NOT-MERGE).
So the v2 script is a later, differently-parameterised rebuild, not the provenance of
the shipped asset, and it is not a drop-in replacement either.

**Conclusion: the 0.35 has no surviving generator or citation. It is recoverable only
by inference from the figure's own legend.**

### 2d. Draft clause for the Fig. 4 caption, not applied

> The friction coefficient implied by this figure's own legend, $\mu = F_{\text{fric}}/N
> = 979/2796 = 0.350$, is a tyre-road Coulomb coefficient internal to this analytical
> model, and is not the $0.55$ MPM ground-plane boundary friction used by the 17 coupled
> runs reported in Section~\ref{subsec:sweep}; the two are different parameters in
> different models and are not interchangeable.

---

## 3. The C_D cross-validation

### 3a and 3b. Froude at the nominal condition

Wolfram, `1.5 / sqrt(9.81 * 0.30)` = **0.874372**. Below 1, therefore **subcritical**.

The repo's CFD abstract states the drag coefficient is "less than 1 for supercritical
flows and more than 1 for subcritical flows". At Fr = 0.874 the expectation is
C_d > 1, and the figure's implied C_d is just above 1. Reading the left panel at
v = 3.0 m/s with the model's own 1.70 m reference width:

| Depth | Drag read (kN) | Frontal area (m2) | Implied C_d (Wolfram) |
|---|---|---|---|
| 0.15 | 1.22 | 0.255 | **1.0632** |
| 0.60 | 4.85 | 1.020 | **1.0566** |

Consistent to within 0.7% across a fourfold depth change, which confirms a single
constant C_d is in use. My reading gives **1.06**, marginally above the 1.05 in the
brief; the difference is within the roughly 3% precision of reading a 1568-px raster.

**This is a genuine consistency result.** An independent 3D CFD study, using the finite
volume method and a different solver, predicts C_d > 1 in subcritical flow, and this
project's analytical model independently lands at 1.06 at Fr = 0.874.

### 3c. Froude across all 17 runs

```
PY -c "... velocity_ms / sqrt(9.81 * realized_depth_m) ..."   (full command in the doc history)
```

All 17 runs, 9 distinct conditions. Fr computed on both requested and realized depth:

| Condition (D req, V) | Fr requested | Fr realized | Inside 0.09 to 2.46 |
|---|---|---|---|
| 0.30, 0.5 | 0.2915 | 0.2942 | yes |
| 0.30, 1.0 | 0.5829 | 0.5884 | yes |
| 0.30, 1.5 (x9 runs) | 0.8744 | 0.8826 | yes |
| 0.30, 2.0 | 1.1658 | 1.1768 | yes |
| 0.30, 2.5 | 1.4573 | 1.4710 | yes |
| 0.30, 3.0 | 1.7487 | 1.7652 | yes |
| 0.25, 1.5 | 0.9578 | 1.0191 | yes |
| 0.35, 1.5 | 0.8095 | 0.7894 | yes |
| 0.45, 1.5 | 0.7139 | 0.7206 | yes |

**17 of 17 inside the validated envelope**, on both requested and realized depth.
Fr spans 0.2942 to 1.7652 against a validated 0.09 to 2.46. This is cross-method
validation, not a limitation, and it belongs in the paper.

### 3d. Identifying the CFD paper

Crossref REST API, queried first as instructed:

```
https://api.crossref.org/works?query.bibliographic=Understanding+the+Stability+of+Passenger+Vehicles+Exposed+to+Water+Flows+through+3D+CFD+Modelling&rows=3
```

Top three hits, verbatim in order:

1. **Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D
   CFD Modelling**, DOI `10.3390/su151713262`, Al-Qadami, Razi, Damanik, Mustaffa,
   Martinez-Gomariz, *Sustainability* 15(17):13262, 2023.
2. Stocks, Flows, and Distribution of Critical Metals in Embedded Electronics in
   Passenger Vehicles, DOI `10.1021/acs.est.6b05743.s001` (ACS). Unrelated.
3. Road vehicles. Passenger-car and trailer combinations. Lateral stability test,
   DOI `10.3403/30202467` (BSI). Unrelated.

Hit 1 is an exact title match on the first attempt, so Consensus and Scholar Gateway
were not needed. All five authors, journal, volume, issue, and page match the local
record at `vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md` line 303.
Independently confirmed earlier this session through Scite: gold OA, CC-BY, no editorial
notices, tally 2 total (0 supporting, 0 contrasting, 2 mentioning) across 4 citing
publications, which is a thin record and should be described as such if used.

---

## 4. The SPH annotation on an analytical figure

### 4a. Confirmed, and more strongly than stated

`data/l2_results_from_wandb.csv` holds 9 rows, `level = L2_Genesis_SPH`, at depths
{0.15, 0.30, 0.45, 0.60} and velocities {0.0, 1.0, 1.5, 2.0}.

- 4 of 9 rows are at v = 1.5 m/s, the pilot's principal test velocity.
- 4 rows have `divergence = True`: (0.30, 1.5), (0.15, 1.5), (0.30, 1.0), (0.30, 2.0).
  Three of the four are at depth 0.30 m.

So "L2 test velocity = 1.5 m/s" and "Divergence depth = 0.30 m" both trace to this
9-condition SPH pilot.

The stronger evidence is the left panel's own depth series. It plots **0.15, 0.30, 0.45,
0.60 m**, which is exactly the SPH pilot's depth set. The 17-run MPM sweep uses
{0.25, 0.30, 0.35, 0.45} and contains **no 0.15 m and no 0.60 m run at all**. The
analytical figure's depth sampling is inherited from the SPH pilot, not from the MPM
sweep the paper's results section reports.

### 4b. The caption does not disclose it

The Fig. 4 caption (line 137) opens "Analytical force-balance calculation, not
simulation output" and discusses buoyancy, plan area, hull volume, and fill factor. It
never mentions SPH, never cites `data/l2_results_from_wandb.csv`, and never explains
where the two annotated values come from. A reader is left to assume they are properties
of the analytical model. They are not: they are summary statistics of a separate
9-condition SPH pilot overlaid on an analytical plot.

Draft clause, not applied:

> The annotated divergence depth of $0.30$\,m and test velocity of $1.5$\,m/s are not
> outputs of this analytical model: they summarise the separate 9-condition SPH pilot of
> \texttt{data/l2\_results\_from\_wandb.csv}, in which 3 of the 4 L1/L2 divergences occur
> at $0.30$\,m and 4 of the 9 conditions were run at $1.5$\,m/s. The four depths plotted
> in the left panel are that pilot's depth set, not the 17-run MPM sweep's.

---

## 5. The replacement figure

`analysis/paper_fig_l1_dv_curves.py`, producing `fig_l1_dv_curves.pdf`.

```
PY analysis/paper_fig_l1_dv_curves.py \
  --scenarios $R/data/scenario_sweep.csv \
  --out-pdf fig_l1_dv_curves.pdf --out-json l1_dv_curves.json
```

Requirements as built:

- **(a) Boundary curves.** For class c the FORD region is D <= D_cap AND D*V <= H_cap,
  so the boundary is V = H_cap/D clipped at V = 3.0, terminating in a vertical drop at
  D = D_cap. Note the literal instruction, `min(depth cap, hazard cap / D)`, mixes metres
  with metres per second, so it was read as the dimensionally consistent form above.
  The V = 3.0 clip is not arbitrary: AR&R Table 3 assigns a limiting velocity of
  3.0 m/s to all three classes.
- **(b)** Three distinct hues from the Okabe-Ito colourblind-safe set (`#0072B2`,
  `#D55E00`, `#009E73`), each with a distinct line style (solid, dashed, dash-dot), so
  the figure survives greyscale printing.
- **(c)** No near-white swatches; the lightest legend element is `#8A8A8A`.
- **(d)** All 70 grid points drawn as small grey markers; the 12 class-sensitive cells
  ringed in open black.
- **(f)** Vector confirmed: `pdfimages -list` returns zero rows, `DCTDecode` count 0,
  image XObject count 0. Fonts are CID TrueType (`pdf.fonttype 42`), matching the
  current Fig. 3 rather than matplotlib's default Type 3.
- **(g)** Hard assertions on 14/19/26, on class-sensitive = 12, on the nesting, and on
  the drawn boundary reproducing all three stored verdict columns exactly. The script
  exits non-zero with `VERIFICATION FAILED` on any mismatch. This fired for real during
  development and caught the float trap in Section 1.
- **(h)** No inline comments, no docstrings.

### 5e. The AR&R length criterion, verified before writing the caption

AR&R Table 3, page 14, extracted with `pdftotext -layout`:

| Class | Length (m) | Kerb weight (kg) | Ground clearance (m) | Still-water depth | Limiting velocity | Stability |
|---|---|---|---|---|---|---|
| Small passenger | < 4.3 | < 1250 | < 0.12 | 0.3 | 3.0 | DV <= 0.3 |
| Large passenger | > 4.3 | > 1250 | > 0.12 | 0.4 | 3.0 | DV <= 0.45 |
| Large 4WD | > 4.5 | > 2000 | > 0.22 | 0.5 | 3.0 | DV <= 0.6 |

This confirms the caps the figure uses (0.30/0.30, 0.40/0.45, 0.50/0.60) against the
primary source.

Hull extents measured live from `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`
(327,212 vertices, binary little-endian):

**4.2826 x 1.7464 x 1.5180 m**, matching the value already in the Fig. 4 caption.

| Class | Length rule | Hull 4.2826 m | Mass rule | Override used |
|---|---|---|---|---|
| Small passenger | < 4.3 | **PASS** | < 1250 | 1100 kg, pass |
| Large passenger | > 4.3 | **FAIL** | > 1250 | 1609 kg, pass |
| Large 4WD | > 4.5 | **FAIL** | > 2000 | 2337 kg, pass |

The mass overrides satisfy AR&R's kerb-weight rule for all three classes, but the single
hull violates the length rule for both upper classes at every mass. **Only the 1100 kg
configuration is a genuine AR&R class match.** The claim is verified and safe to write.

Draft caption for the replacement, not applied:

> AR\&R stationary-vehicle stability boundaries for the three published classes, drawn as
> depth-velocity curves in the convention AR\&R itself uses. Each boundary is
> $V = H_{\text{cap}}/D$ clipped at the limiting velocity of $3.0$\,m/s and terminated at
> the class still-water depth cap. **This is a direct evaluation of a published formula,
> not simulation output.** Grey markers are the 70 sampled scenarios of
> \texttt{data/scenario\_sweep.csv}; ringed markers are the 12 whose verdict depends on
> vehicle class. FORD counts (14, 19, 26) are read from the stored
> \texttt{L1\_verdict\_*} columns, not recomputed. Caps and class definitions from
> \cite{shand2011arr}, Table 3, page 14, which the report itself labels draft and
> interim. The diagnostic hull measures $4.2826$\,m, which satisfies AR\&R's
> $<4.3$\,m length rule for small passenger but fails the $>4.3$\,m and $>4.5$\,m rules
> for large passenger and large 4WD; the mass overrides meet the kerb-weight rule for all
> three classes, so only the $1100$\,kg configuration is a genuine class match and the
> two heavier configurations are mass-only analogues.

---

## 6. Survey of the alternatives already on disk

| Asset | Found at | Dimensions | True format (`file`) | Vector? | Generator in `analysis/` | What it plots | Verdict vs current Fig. 3 |
|---|---|---|---|---|---|---|---|
| `L0_L1_phase_space_divergence.png` | NOT in repo. Only `~/Documents/CAN_IT_FORD_ARCHIVE_2026-07-17/paper_and_writing/CURRENT/` | 1568 x 700 | **JPEG**, despite `.png` | No | None found | L0 vs L1 divergence, two panels | **Loses.** Raster, extension mismatch, outside the repo, superseded by `l0l1_two_rules_v2.pdf` which is already Fig. 2 |
| `can_it_ford_phase_space.png` | `figures/poster_exports/` | 2400 x 1800 | PNG, RGBA | No | `make_phase_space.py`, `make_phase_space_v2.py` | Poster phase space | **Loses.** Raster at poster scale, duplicates Fig. 2/3 territory |
| `phase_space_poster_figure.png` | `figures/` and `designsafe-staging/figures/` | 2400 x 1800 | PNG, RGBA | No | `build_poster_phase_space.py` | L1 grid plus L2 overlay | **Disqualified.** Its generator reads `data/track1_sweep_v2/manifest.csv`, which project CLAUDE.md bars from sourcing any paper figure |
| `two_panel_figure.pdf` | **Does not exist** anywhere under `/Users/josie/can-it-ford`, `~/Desktop`, `~/Documents` | | | | | | Cannot be evaluated |
| `can_it_ford_figure.pdf` | **Does not exist** | | | | | | Cannot be evaluated |
| `newplot.png` | **Does not exist** | | | | | | Cannot be evaluated |

Three of the six named assets do not exist. Of the three that do, all are raster, none
has a vector sibling in use, and one is disqualified by a standing project rule.
**No existing asset beats the current Fig. 3.**

---

## 7. Recommendation

**Keep the current Fig. 3. Add one caption clause to Fig. 4. Do not swap either figure.**

The current `L1_three_class_corrected.pdf` already satisfies almost everything the
replacement brief asked for, which only became clear on rendering it at true printed
size:

- Three boundary curves, one per class, already present.
- Three distinct hues with three distinct line styles (solid red, dashed gold, dash-dot
  green), already greyscale-safe.
- The 12 class-sensitive cells already hatched.
- Vector: zero image XObjects, CID TrueType fonts.
- A provenance footer already stamping the source md5, byte count, and mtime.
- Its generator exists, at `analysis/plot_l1_three_class.py`, so it is not orphan.

It also carries information my replacement does not. Its four filled regions
(14 / 5 / 7 / 44) make the class nesting directly visible as area, which is the actual
finding, whereas my version leaves the reader to infer nesting from curve order. Its
declarative title states the result. Rendered at 3.5 in and 300 dpi it is fully legible;
my initial concern that the 18.7 in canvas would shrink the type was wrong, because the
fonts were authored to scale.

Its one real defect is the criterion (c) violation: `FILL[0] = "#F4F3EE"` is the
near-white swatch for "No class fords (44 cells)" against a `#FFFFFF` legend background.
That is a one-line change in a generator that already exists, not a reason to replace the
figure. I have not made that change, because the paper is submission-ready and the
swatch does carry a `#B0B0A8`-class border that keeps it visible.

Against that, my `fig_l1_dv_curves.pdf` is cleaner and more compact, and it is the AR&R
house convention. But swapping it in would trade a richer figure for a plainer one, spend
an edit on a clean submission-ready branch, and lose the region decomposition. That is a
bad trade at this stage.

The Fig. 4 caption clauses are a different matter and are worth more than the Fig. 3
swap. Two undisclosed facts currently sit in that figure: it uses mu = 0.350 where the
paper states 0.55 everywhere else, and it carries two annotations derived from the SPH
pilot on a figure the caption presents as purely analytical. Both are small, both are
one clause, and both are the kind of thing a careful reviewer finds. Of the two, the
**friction disclosure is the higher priority**, because the number contradicts a value
stated elsewhere in the same paper.

The Al-Qadami Froude result (17 of 17 inside a validated envelope, and an independent
C_d > 1 in subcritical flow matching this project's 1.06) is the strongest positive
finding here and the best candidate for a genuine addition. It needs a new citation,
which is out of scope for this pass.

### Priority order

1. Fig. 4 caption, friction clause. Highest value, resolves an internal contradiction.
2. Fig. 4 caption, SPH-annotation clause. Resolves a provenance gap.
3. Fig. 3 legend swatch, `FILL[0]` darkened in `analysis/plot_l1_three_class.py`.
   Cosmetic, one line, only if the figure is being regenerated for another reason.
4. Everything else: hold.
