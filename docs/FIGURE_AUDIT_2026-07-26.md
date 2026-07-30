# FIGURE AUDIT, 2026-07-26

Generated under FRB-2. Interpreter:
`/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python` (3.12.13, scipy 1.18.0,
skimage 0.26.0). Driver: `analysis/make_poster_figures.py`. Nothing was committed, nothing
was pushed, nothing was deleted.

Poster geometry: 56 x 42 in landscape. Figures are authored 15.0 to 17.5 in wide, so they
drop in at native scale with no rescaling. Minimum type is 8.5 pt at that size. All text
sits on white or on light tinted fills; no text is set on a dark background.

---

## 1. Provenance rule applied to every panel

Every number in every caption is read at render time from one of:

| source | what it carries |
|---|---|
| `data/all_runs_inventory.csv` | the 17 `_incoming` runs, one row each, emitted by `analysis/build_runs_inventory.py` |
| `renders/yaris_render_s1/gates_results_all_runs.json` | 20 rows (17 standing + 3 dry start), four rungs each, emitted by `renders/yaris_render_s1/gates_all_runs.py` |
| `renders/yaris_render_s1/gates_results.json` | the 3 dry-start rows, local depth and local speed peaks, `dv_honest` |
| `renders/yaris_render_s1/g64_m1100/rollout.npz` | hull `extent`, `h`, `velocity` |
| `renders/yaris_render_s1/hero_fixed.log` | water volume error and `open_edges` from the FIXED render |
| `docs/four_rung_ladder.md:274-280` | the 0.158 to 0.174 m measured ground-clearance band |
| `docs/render_v1_task_outputs/A2_containment_gate.output` | the 100.00 pct containment figure and its subsample caveat |

Nothing that lives in a file is hardcoded in the driver. The three AR&R caps (0.30 / 0.45 /
0.60 m2/s), the 0.05 m L2 drift threshold and the 0.15 m L0 threshold are constants of the
criteria themselves, not measurements, and are declared at the top of the driver.

---

## 2. Panel-by-panel audit

### G1 `figures/g1_velocity_sweep.pdf` / `.png`
Six points, v = 0.5 to 3.0 m/s, monotonic in |d| (0.0578, 0.2402, 0.6585, 1.0196, 1.2196,
1.3384 m). Fixed grid 64, fixed realized depth 0.294429 m, one hull at 1100 kg. Vertical
rule at v = 1.018920 m/s, computed live as 0.30 / 0.294429, not typed. FORD side shaded.
Horizontal dashed rule at the 0.05 m L2 threshold. The two divergence points (v = 0.5, 1.0)
are ringed and annotated.
**Status: OK.** This is the centre panel.

### G2 `figures/g2_depth_sweep.pdf` / `.png`
Four points on the REALIZED axis: 0.2208 / 0.2944 / 0.3680 / 0.4416 m, labelled with layer
count (3/4/5/6) and with the requested value shown only as a parenthetical. The requested
value is never plotted. Near-saturation between the last two points annotated: 0.9654 to
0.9744 m, a gain of 0.0090 m for a whole extra layer.
**Status: OK.**

### G3 `figures/g3_verdict_matrix.pdf` / `.png`
Rows L0 / L1a / L1b / L2. Twenty columns, grouped mass-x-grid (9), depth (3), velocity (5),
dry start (3). Every cell read from `gates_results_all_runs.json`. The dry-start 2337 kg
L2 = FORD cell is outlined in red and called out, so the figure cannot be read as "L2 is
uniformly NO-FORD". Caption carries the independence caveat: L0, L1a and L1b are all
functions of (depth, velocity) alone and share their entire input.
**Status: OK.** See finding F-1 below on scope.

### G4 `figures/g4_bow_wave.pdf` / `.png`
Standing series (bow probe peak, frames 50 / 35 / 24) and dry series (gates local depth
peak, frame 29) against mass. Rules at the AR&R 0.30 m cap and the 0.294429 m nominal
depth. Standing rise +0.0785 m annotated. Caption names the measurement window, states
that the two series are different probes, and records that the two dry-start peak measures
disagree (0.3974 vs 0.4105) with only one plotted.
**Status: OK.**

### G5 `figures/g5_mass_sensitivity.pdf` / `.png`
Twin axis. Left: standing 4.86x (0.658537 to 0.135559 m) and dry 2.38x (0.092399 to
0.038901 m). Right: D x V flat at 0.441644 m2/s. Bit-identity is not asserted, it is
TESTED at render time by comparing `float.hex()` across the three runs, and the annotation
text switches to "NOT bit-identical" if the test fails. It currently passes:
all three are `0x1.c43e5e9ae6667p-2`.
**Status: OK.** Caption carries the one-hull scope statement verbatim.

### G6 `figures/g6_two_measures.pdf` / `.png`
Three readings of D x V on the dry-start runs: nominal 0.45000, peak-local-depth x nominal
velocity (0.59613 / 0.62379 / 0.63903), and local D x V at the vehicle (0.18916 / 0.16451 /
0.15301). Rules at all three AR&R caps. Caption names reading A (nominal) as this project's
primary and gives the reason: it is an input to the simulation rather than an output of it,
so it is reproducible without running a simulation, which is the point of testing a cheap
criterion against L2.
**Status: OK.** Framed as disclosure, not defect.

### G7 `figures/g7_geometry_gates.pdf` / `.png`
Left: hull side view, extents 1.746378 x 4.282610 x 1.518008 m, long axis Y, clearance
drawn as a BAND (0.158 to 0.174 m), not a point value. Right: eight gates, six PASS, one
FAIL (realized rho 310 / 453 / 658 vs the 100 to 300 band), one NOTED (passthrough 7.3 to
15.9 pct, worst at v = 3.0 m/s). The FAIL is shown, not hidden.
**Status: OK.** See finding F-3 on the volume-error value.

### G8 `figures/g8_hero.pdf` / `.png`
Frame 65 of 90 from `hero_g64_m1100_FIXED.mp4`, selected as the peak-displacement frame from
`metrics.csv` (|d| = 0.665667 m at t = 2.167 s). Water visibility was measured before saving:
9.25 pct of the cropped frame is viridis-mapped water surface. The degraded path
(`figures/render_v1/realistic_A4_g64_m1100_f0045.png` plus the depth-sort caveat) is coded
and was NOT taken.
**Status: OK, primary path.**

### G9 `figures/g9_scope.pdf` / `.png`
Two-column text panel for Canva. ESTABLISHES 6 items, DOES NOT 8 items, both as specified.
**Status: OK.**

---

## 3. POSTER SHORTLIST

Poster is 56 in wide x 42 in tall, landscape. Suggested panel order left to right, top to
bottom. Total 9 panels; if space forces a cut, cut from the bottom of the list.

| order | panel | file | width at print | role |
|---|---|---|---|---|
| 1 | **CENTRE** | `figures/g1_velocity_sweep.pdf` | 16 to 18 in | The argument. The criterion fails on its own axis at 2 of 6 points. |
| 2 | hero | `figures/g8_hero.pdf` | 14 to 16 in | The image that proves a coupled simulation actually ran and rendered. |
| 3 | receipt | `figures/g3_verdict_matrix.pdf` | 16 to 17.5 in | All 20 runs, all four rungs, including the one L2 FORD cell. |
| 4 | mechanism | `figures/g5_mass_sensitivity.pdf` | 14 to 15 in | Why L1 fails: D x V is mass-blind, L2 is not. |
| 5 | mechanism | `figures/g4_bow_wave.pdf` | 14 to 15 in | Why L1 fails the other way: the flow at the vehicle is not the flow in the criterion. |
| 6 | honesty | `figures/g7_geometry_gates.pdf` | 16 to 17.5 in | Gates including the density FAIL. Do not cut this to save space. |
| 7 | honesty | `figures/g9_scope.pdf` | 16 to 17.5 in | Scope panel. Do not cut this to save space. |
| 8 | supporting | `figures/g2_depth_sweep.pdf` | 13 to 15 in | Depth axis and the quantization disclosure. |
| 9 | supporting | `figures/g6_two_measures.pdf` | 13 to 15 in | The definitional open question. Strong for conversation at the board. |

**Use the PDF, not the PNG, for anything vector.** The PNGs are 300 dpi and exist for Canva
placement previews and for slide decks. `g8_hero` is a raster panel either way.

**Superseded by this set.** `figures/fig2_mass_sensitivity.pdf` is superseded by G5, which
adds the dry series and tests bit-identity at render time instead of asserting it. The older
`figures/fig1_l1_three_class.*`, `figures/fig3_geometry_pipeline.pdf`,
`figures/fig4_velocity_regime.*` and `figures/traction_bias.*` were not regenerated this
session and were not audited here; do not mix them with the G-series without re-checking
their numbers against `data/all_runs_inventory.csv`.

---

## 4. Findings raised during the build

**F-1. The 17-run inventory contains no dry-start run.** All 17 `_incoming` runs are
`standing_water_sustained_inflow`. The three dry-start runs (`m1100`, `m1609`, `m2337`) live
one level up in `renders/yaris_render_s1/` and carry no `scenario` field. G3, G4, G5 and G6
all require dry-start data. Resolution: `all_runs_inventory.csv` is exactly the 17 runs as
specified, and `gates_all_runs.py` reads the 3 dry-start runs additionally, tagging them
`origin = top_level` and `scenario = dry_start`. G3 therefore has 20 columns, not 17.

**F-2. Particle count is not constant across the 17 runs.** `n_vehicle` is 3846 at grid 48,
8905 at grid 64 and 29804 at grid 96. The "8904 to 8905 particles" statement is true only of
the grid-64 runs. G5 plots only grid-64 runs, so its caption is correct as written, but it
is scoped explicitly to "all six runs plotted here" rather than to all 17.

**F-3. The measured water volume error is +1.68 pct raw / +1.65 pct smoothed, not +3.0 pct.**
G7 reports the live value read from `hero_fixed.log` for the FIXED render built this session.

**F-4. `fill_ratio` is not a single value.** It is 1.0024 at grid 64, 1.0262 at grid 48 and
0.9941 at grid 96. All three sit inside the 0.95 to 1.10 band, so the gate still passes.
G7 reports the grid-64 value and the full 17-run range.

**F-5. The containment gate is a subsample.** 100.00 pct of 2000 sampled solid particles,
because `trimesh.ray.has_embree` is False on this machine. The four-rotation relative gate
that would discriminate the pose chain is still outstanding. Both facts are in the G7 caption.

**F-6. `docs/four_rung_ladder.md` is stale on one point.** It states "all six rollouts are
`n_grid = 64`" and that no grid convergence study exists. There are now grid 48, 64 and 96
runs. The grid comparison is still not a convergence study (the change is non-monotonic), but
the sentence as written is no longer accurate.

---

## 5. What was NOT done, and why

- No `git add`, no commit, no push. Forbidden by the directive.
- No file deleted, no `rm`. Forbidden by the directive.
- No Grid Convergence Index stated anywhere. Forbidden by the directive, and in any case the
  g64-to-g96 change is negative and non-monotonic so no GCI is computable.
- `verify_poster_numbers.py` was not run. Forbidden by the directive.
- No Vista job cancelled. All three named jobs were already terminal before the session
  reached that step; see the run manifest.
