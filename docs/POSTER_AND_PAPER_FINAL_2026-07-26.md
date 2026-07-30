# Can It Ford: final poster and paper construction guide
**Built 2026-07-26 from live reads only.** Poster deadline Monday 2026-07-27, 09:00 CST, final.
Paper target 2026-07-31.

Every claim in this document was verified against a primary artifact tonight. Where a claim
could not be verified, it is marked and the reason is given. Sources consulted live, in order:
`sim_standing.py`, `sim_dump.py`, `third_party/mpm-engine-544c93dd/{VENDORED.md,LICENSE,PINNED_SHA.txt}`,
`render_pv.py` (plus three re-render probes), `rollout.npz` for `g64_m1100`, seventeen
`summary.json` files under `_incoming/`, `gates_results_both_scenarios.json`,
`docs/VERIFIED_FACTS_LEDGER_july24.md` Sections F and G, five PLY headers,
`failed_reconstructions_2026-07-25/README.md`, `data/track1_sweep_v2/manifest.csv` and its schema
doc, `analysis/build_poster_phase_space.py`, `analysis/plot_traction_bias.py`,
`analysis/plot_geometry_pipeline.py`, `analysis/fig2_mass_sensitivity.py`,
`analysis/plot_l1_three_class.py`, `simulation/failure_modes.py`, `vehicle_params.py`,
`docs/POSTER_COMPLIANCE_2026-07-27.md`, the CCSA and NHTSA model pages, and a live execution of
the failure-mode classifier over twenty runs. That is twenty-two independent checks.

---

## 1. The abstract

### Poster version (176 words)

> Drivers cannot see whether a flooded road is safe to cross, and published guidance reduces the
> decision to a single number: the product of water depth and velocity. That threshold comes from
> scaled physical tests of stationary vehicles, not from resolving the flow. We asked whether a
> coupled fluid-solid simulation agrees with it.
>
> Using the material point method in Krishna Kumar's `kks32/mpm-engine`, we coupled a watertight
> 2010 Toyota Yaris hull, reconstructed from a public crash-test mesh, to weakly compressible
> water in a standing-water channel with sustained inflow. Across a six-point surge sweep at a
> realized depth of 0.2944 m, simulated displacement rises monotonically from 5.8 cm at 0.5 m/s
> to 1.34 m at 3.0 m/s. The vehicle crosses from stationary to sliding between 0.5 and 1.0 m/s.
> The published small-passenger hazard cap of 0.30 m²/s is reached at 1.02 m/s, inside that
> transition. Failure is by sliding in every case tested.
>
> The work is unfinished, and the limits are stated on this board.

### Paper version (adds the limitation sentence in full)

Append to the poster abstract:

> Three limitations bound these results. One vehicle geometry passed validation, so the mass
> comparison varies mass on a fixed hull rather than simulating three vehicle classes. Between
> 8.0 and 15.9 percent of water particles pass through the hull at the tested resolution. A
> three-grid refinement study converged non-monotonically at two of three masses, so a Grid
> Convergence Index cannot be computed and no observed order of convergence is claimed.

---

## 2. What the project actually established, ranked by evidential strength

| # | Claim | Evidence | Verdict |
|---|---|---|---|
| 1 | Displacement rises monotonically with surge velocity, 0.058 to 1.338 m over 0.5 to 3.0 m/s at fixed depth | 6 runs, all `determinism_identical: true`, identical `grid_lim 9.421742`, identical 4-layer depth | **VERIFIED** |
| 2 | Failure mode is SLIDE, with STUCK only at 0.5 m/s | Classifier executed live tonight, 20 of 20 runs classified | **VERIFIED** |
| 3 | The toppling criterion is exceeded transiently from 1.5 m/s but never sustained for 3 frames | `r_TOPPLE` 1.33, 1.79, 2.23, 2.66 at v = 1.5, 2.0, 2.5, 3.0 | **VERIFIED, but SSF-sensitive** |
| 4 | A float signature emerges only at the top of the range | `r_FLOAT` 0.00 through v = 2.0, then 0.23 at 2.5 and 1.07 at 3.0 | **VERIFIED** |
| 5 | L2 disagrees with L1: every run exceeds the 0.05 m onset detector | 9 mass runs plus 8 sweep runs | **VERIFIED** |
| 6 | Depth response saturates above roughly 0.37 m | 4 depth points: 0.296, 0.659, 0.965, 0.974 m | **VERIFIED, caption must use realized depth** |
| 7 | Mass ordering holds at all three grid resolutions | g48, g64, g96 each ordered 1100 > 1609 > 2337 | **VERIFIED** |
| 8 | Grid Convergence Index | Non-monotonic at 2 of 3 masses, non-uniform refinement ratios 1.333 and 1.500 | **NOT COMPUTABLE, do not claim** |

### The single most important new result

**The failure-mode classifier was blocked and is now unblocked, and nobody had noticed.**

`data/track1_sweep_v2/mpm_sweep_data_schema.md` records a CONFIRMED BLOCKING finding: all 36 v2
runs were rejected by `simulation/failure_modes.py` because `FloodHistory.to_csv` dropped the
velocity columns. The doc concludes, correctly for v2: "No failure-mode result from v2 can go on
the poster or in the paper."

That doc is dated 2026-07-25. The runs from 2026-07-26 01:54 have a different header:

```
v2  (blocked): t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg
new (passes):  t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg,vx,vy,vz,vmag,wx,wy,wz
```

`REQUIRED_COLUMNS = ("t","dx","dy","dz","vx","vy","vz")` and the optional
`OMEGA_COLUMNS = ("wx","wy","wz")` are **both fully satisfied**. I ran the classifier live:
**20 of 20 classified, against 0 of 36 for v2.** The writer-side fix the schema doc prescribed
has already landed. This is a real, presentable result that did not exist yesterday.

---

## 3. The figure slate

### TIER A, put these on the board

| Figure | Script | Source data | Status |
|---|---|---|---|
| **`figures/fig4_velocity_regime.pdf`** | `analysis/fig4_velocity_regime.py` (written tonight) | 6 × `summary.json` + `metrics.csv` under `_incoming/sweepV_*` and `g64_m1100` | **NEW. Your strongest result.** Full provenance header in the script |
| **Corrected hero render frame** | `renders/yaris_render_s1/render_pv_fixed.py` | `g64_m1100/rollout.npz` | **NEW.** Water restored, see section 5 |
| `figures/fig1_l1_three_class.pdf` | `analysis/plot_l1_three_class.py` | `data/scenario_sweep.csv`, repo-root copy, AR&R fix **PRESENT** | **VERIFIED chain** |
| `figures/fig2_mass_sensitivity.pdf` | `analysis/fig2_mass_sensitivity.py` | `gates_results_both_scenarios.json`, filtered to `standing_water_sustained_inflow` | **VERIFIED chain.** All three rows are n_grid 64, where the `4.0 * h` hardcode is correct, so this figure is unaffected by that bug |

### TIER B, ship only with the stated label

| Figure | Problem | Required label |
|---|---|---|
| `figures/phase_space_poster_figure.svg` | Reads `track1_sweep_v2/manifest.csv`, which is the **box-proxy** sweep, not mesh geometry | "Track 1 box-proxy sweep, n_grid 64." **Good news:** `build_poster_phase_space.py:90` filters `density_plausible == True`, correctly dropping all 12 SUV rows at ρ = 308.1. The figure is clean, it is just not mesh-based |
| `figures/pipeline_diagram_poster.svg` | Schematic, no data | None needed, it is a diagram |

### TIER C, do not ship

| Figure | Why |
|---|---|
| `figures/traction_bias.pdf` | **Every number is hardcoded in `plot_traction_bias.py`.** `TRACTION_N = [1390.7, 2459.2, 3203.5]` appears with no source file, and the same values are frozen a second time in `verify_poster_numbers.py`. Two copies, zero primary artifact. **ORPHAN provenance.** Separately, `POSTER_COMPLIANCE` D2 records that this framing is superseded: parity fill now converges to 1.0023 at n_grid 64 |
| `figures/fig3_geometry_pipeline.pdf` | Same defect. `VOL_60K`, `VOL_400K`, `HULL_M3` all hardcoded, no input file. **ORPHAN provenance** |
| `hero_probe.png`, `hero_g64_m1100.mp4` as shipped | No water in any frame. Superseded by the fixed render |
| Anything captioned "three vehicles" | One hull. See section 6 |
| Any GCI or observed order of convergence | Not computable |
| Any failure-mode result from the v2 sweep | 0 of 36 classified. Use the new runs instead |

**On Tier C:** hardcoded-constant figures are not necessarily wrong. They are un-auditable. If
you want either back, the fix is to find the log or CSV those numbers came from and make the
script read it. If that artifact no longer exists, the figure cannot ship under your own
provenance rules.

---

## 4. The framing: honest unfinished research

Dr. Kumar's group runs on provenance discipline, and your own `CLAUDE.md` and verified-facts
ledger are stricter than most published work. **Lean into that.** The most impressive thing you
can hand him is not a finished result, it is a correctly bounded one.

### The one-sentence framing

> A coupled MPM simulation of a real vehicle hull in flood flow reproduces the qualitative
> behaviour the published hazard criterion encodes, disagrees with it quantitatively near the
> threshold, and the disagreement is bounded by three limitations we can name precisely.

### Say these out loud on the board

1. **One mesh, not three.** "We evaluate all three AR&R class thresholds against one validated
   hull. That is legitimate: the classes are properties of the criterion, not of the simulation.
   We do not claim to have simulated three vehicles." This is your ledger's Section G1 wording
   and it is the correct scientific position.
2. **The 0.05 m threshold is ours.** It is an internal numerical onset detector. It is **not**
   attributable to Smith, Modra and Felder 2019 or to any peer-reviewed drift criterion. Your
   ledger Section B already retracted that attribution. Retracting it publicly on the poster is
   a strength, not a weakness.
3. **Passthrough is 8.0 to 15.9 percent.** State it as the headline limitation, with the number.
4. **Convergence is unresolved.** "Three grids, non-monotonic at two of three masses, so no GCI.
   What survives refinement is the sign and the ordering, not the magnitude."
5. **Effective density sits above the plausible band.** 309.7 kg/m³ at 1100 kg against a
   100 to 300 band. Every `gates_results_both_scenarios.json` row carries
   `"density_plausible": false`. Do not hide this.

### What Kumar will most appreciate

Based on the discipline already encoded in your repo: **the retraction list.** A short block
titled "What we retracted" listing the DRIFT_THRESHOLD misattribution, the v3 hollow-mesh sweep,
and the three-vehicle claim, each with the check that caught it. That block demonstrates the
thing an REU is supposed to teach, and almost no undergraduate poster has one.

---

## 5. Poster: exact actions, in order, before Monday 09:00

Your poster is `poster.html` printed to PDF via Chrome. `Cerrell_TACC_42x56.pdf` at repo root is
403,657 B, mtime 07-25 17:45. It is **already compliant** on 19 of 21 checked requirements per
`docs/POSTER_COMPLIANCE_2026-07-27.md`.

1. **Send one message about orientation.** The poster is 56 in wide by 42 in tall, landscape. The
   instruction says preferred 42x56 and maximum 42" x 60", and never says width or height. Ask
   Rosalia Gomez or TACC Education and Outreach whether landscape is acceptable. **This is the
   only hard-requirement risk and it costs one message.** Do not rotate on a guess: `poster.html`
   is a fixed-dimension CSS grid and re-flowing it is a layout rebuild.
2. **Resolve the duplicate PDF.** Two files share the required filename:
   `Cerrell_TACC_42x56.pdf` (403,657 B, 17:45) and `figures/Cerrell_TACC_42x56.pdf`
   (404,092 B, 17:13). Keep the newer root copy, rename the other. Two files with the same
   required name is how the wrong one gets uploaded at 08:55.
3. **Update the Results section.** `POSTER_COMPLIANCE` D2 is right that the board predates your
   best work. Concretely: Result 2's "truth is outside the measured range" is the pre-fix
   framing; Result 5 says no L2 verdict exists, and one now does.
4. **Place `fig4_velocity_regime.pdf`.** D3 notes there is no L2 figure on the board at all.
   This is the one to add. It is your strongest result and it is the one a general audience reads.
5. **Add the corrected hero frame** if space allows. A red car in visible water outperforms any
   plot for a passer-by.
6. **Add the "What we retracted" block.** Section 4.
7. **Fill the logo slots.** Both `.logo-slot` divs at `poster.html:237,243` and `.qr-reserve` at
   `:368` are empty and no logo asset exists in the repo. You need the poster resources folder.
8. **Reprint** with Chrome, and re-verify the file is under 40 MB (currently 0.39 MB, no risk).
9. **Sign up for the mock presentation slot** and build a 5-minute track. The instruction is
   explicit that you do not read from the board.

---

## 6. Tooling: the honest answer

**Do not move the poster to Canva.** You have a working, compliant, version-controlled
`poster.html` that already passes 19 of 21 requirements, and a hard deadline about thirty hours
out. Rebuilding in Canva would discard the compliance audit, break the figure-to-script
provenance chain that is the whole point of this project, and produce a file nobody can
regenerate. HTML plus Chrome print is also strictly better for a research poster: the figures are
vector PDFs placed at native resolution, and the source is diffable.

**For the paper, Overleaf is the right call**, for a different reason than convenience: it gives
you BibTeX, which is how the citation discipline you have been maintaining becomes machine
checkable. Your figures are already PDF with `pdf.fonttype = 42` set in the plotting scripts,
which is exactly what LaTeX wants.

Two connector notes: the Canva and Notion connectors on this machine are not authorized in this
session, and several plugin MCP servers (Asana, Atlassian, Datadog, Linear, Notion, PagerDuty,
Slack) need authorization through your claude.ai connector settings or an interactive `claude mcp`
session before they can be used at all. None of them are needed for this work.

---

## 7. Paper structure, and what fills each section

| Section | Content that exists and is verified |
|---|---|
| 1. Introduction | The flooded-road decision problem. `docs/motivation_B9b_answering_the_authors_call.md` |
| 2. Related work | AR&R (Shand et al. 2011, P10/S2/020, Table 3, DRAFT INTERIM, stationary vehicles). Xia et al. 2014, Shah et al. 2018 for the underlying physics. **Do not cite Smith 2019 for a drift threshold** |
| 3. Method | The L0 / L1 / L2 ladder. `kks32/mpm-engine` @ `544c93dd`, MIT. Weakly compressible water, `c = sqrt(1.1 · K / ρ)`. The `solidify_watertight` divergence from upstream, which is a genuine contribution: exact vertical ray parity gives 100.00 percent mesh containment where upstream's `solidify_columns` would give a partial value |
| 4. Results | 4.1 velocity sweep (fig4). 4.2 depth sweep with realized depths. 4.3 mass sensitivity (fig2). 4.4 failure-mode classification, 20 of 20. 4.5 grid refinement, reported honestly without a GCI |
| 5. Limitations | `docs/limitations_B9a_scaling_and_solver.md` plus the five items in section 4 above |
| 6. Retractions | The block from section 4. Rare and valuable |
| 7. Future work | Three-mesh study via CCSA MASH triple, section 8 below |

---

## 8. The three-vehicle path, for the paper not the poster

Verified live tonight: **there is exactly one usable vehicle mesh.** `truck_trimmed.ply` is not a
mesh at all, it is a Gaussian splat (191,107 vertices, no face element, `f_dc_*` and `f_rest_*`
spherical-harmonic properties). `car_mesh.ply` and `car_mesh_rescaled.ply` are documented failed
reconstructions. The deprecated low-res sedan has a bridged-shut underbody.

The clean future-work paragraph, and it is genuinely strong:

> CCSA/GMU publishes the full AASHTO MASH test-vehicle triple: the 2010 Toyota Yaris (1100C,
> 1100 kg), the 2012 and 2015 Toyota Camry (1500A, 1452 kg), and the 2007 Chevrolet Silverado
> (2270P, 2337 kg). These map one-to-one onto the three AR&R stability classes. Notably, the
> 2337 kg figure used for the large-4WD class in this work is the published mass of the CCSA 2007
> Silverado. Extending the study to three genuinely distinct hulls requires converting
> LS-DYNA shell decks to watertight solids, and licensing must be resolved: none of the CCSA model
> pages carries a stated licence, so the geometry is usable for computation but not
> redistributable.

`DrivAerML` (CC-BY-SA 4.0, watertight STL, 1:1 scale, on Hugging Face) is the one openly licensed
option and covers the large-passenger class only.

---

## 9. Provenance manifest, for the appendix and for Kumar

| Artifact | Script | Source data | Solver / scene | Caveat label |
|---|---|---|---|---|
| `fig4_velocity_regime.pdf` | `analysis/fig4_velocity_regime.py` | 6 runs, `summary.json` + `metrics.csv` | MPM, standing water, n_grid 64 | **MPM-REAL** |
| `fig2_mass_sensitivity.pdf` | `analysis/fig2_mass_sensitivity.py` | `gates_results_both_scenarios.json` | MPM, standing water, n_grid 64 | **MPM-REAL** |
| `fig1_l1_three_class.pdf` | `analysis/plot_l1_three_class.py` | `data/scenario_sweep.csv` | criterion only, no simulation | **CRITERION** |
| `phase_space_poster_figure.svg` | `analysis/build_poster_phase_space.py` | `scenario_sweep.csv` + `track1_sweep_v2/manifest.csv` | MPM, **box proxy**, n_grid 64 | **BOX-PROXY** |
| hero render | `renders/yaris_render_s1/render_pv_fixed.py` | `g64_m1100/rollout.npz` | MPM, standing water | **MPM-REAL** |
| `traction_bias.pdf` | `analysis/plot_traction_bias.py` | **none, hardcoded** | unknown | **ORPHAN, do not ship** |
| `fig3_geometry_pipeline.pdf` | `analysis/plot_geometry_pipeline.py` | **none, hardcoded** | unknown | **ORPHAN, do not ship** |

---

## 10. What to send Kumar

One zip or one repo link containing:

1. `docs/POSTER_AND_PAPER_FINAL_2026-07-26.md`, this file
2. `docs/VERIFIED_FACTS_LEDGER_july24.md`, which is the thing that will impress him
3. `analysis/fig4_velocity_regime.py` and its two outputs
4. `analysis/fig2_mass_sensitivity.py`, `analysis/plot_l1_three_class.py`
5. `renders/yaris_render_s1/{sim_standing.py, render_pv_fixed.py}`
6. `third_party/mpm-engine-544c93dd/VENDORED.md`, which documents your divergence from his upstream
7. The 17 `summary.json` files, which are small and make everything reproducible
8. **Not** the Yaris `.ply`. Licence unresolved, and he knows the provenance already

The cover note should lead with the `solidify_watertight` divergence and the failure-mode unblock.
Those are the two places where you did something to his engine rather than just running it.
