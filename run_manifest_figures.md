# RUN MANIFEST, FRB-2, 2026-07-26

Accepted 2026-07-26 03:26:43 CDT. Interpreter for every step:
`/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python` (3.12.13, scipy 1.18.0,
skimage 0.26.0), verified live before Phase 0.

No git add, no commit, no push. No file deleted. No job cancelled. No Grid Convergence Index
stated. `verify_poster_numbers.py` not run.

## Task table

| task | what it did | attempts | status | artifact |
|---|---|---|---|---|
| T0.1 | Read the 4 START_HERE / triage / script-map files in full | 1 | OK | 3 contradictions found, see below |
| T0.1b | Read the 27 `A1_POSTER_CURRENT` rows from `00_FULL_AUDIT.csv` | 1 | OK | 27 rows, count matches |
| T0.2 | Inventory the 17 runs under `_incoming/` | 1 | OK | `data/all_runs_inventory.csv`, 17 rows, 42 columns; builder `analysis/build_runs_inventory.py` |
| T0.3 | Print `AR_R_STABILITY_LIMITS` verbatim | 1 | OK | `vehicle_params.py:165-183`, reproduced in chat |
| T1.1 | Back up `render_pv.py` | 1 | SATISFIED, not re-run | `render_pv.py.bak_2026-07-26` already existed and is byte-identical; not overwritten |
| T1.2 | Delete the 4 `enable_shadows` lines at 75-78 | 1 | OK | anchor verified unique (1 occurrence); `diff` confirms exactly `75,78d74` |
| T1.3 | Re-render the hero | 1 | OK | `hero_g64_m1100_FIXED.mp4`, 2.96 MB, 90 frames; `open_edges=0`, volume error +1.68 pct raw / +1.65 pct smoothed |
| T1.3b | Water visible in frames 5, 45, 85 | 2 | OK | first detector was wrong and was corrected; see below. `check_water_frames.py`, `water_check.log` |
| T1.4 | Patch the gates layer-count bug | 1 | NO-OP, already patched | `gates_both_scenarios.py:37` already reads `int(s["water_layers"]) * h`; the anchor `4.0 * h` does not exist |
| T1.4b | Re-run gates over all runs | 1 | OK | `renders/yaris_render_s1/gates_all_runs.py` -> `gates_results_all_runs.json`, 20 rows, 0 degraded |
| G1 | Velocity sweep, centre panel | 1 | OK | `figures/g1_velocity_sweep.pdf` + `.png` |
| G2 | Depth sweep, realized axis | 1 | OK | `figures/g2_depth_sweep.pdf` + `.png` |
| G3 | Four-rung matrix, all runs | 1 | OK | `figures/g3_verdict_matrix.pdf` + `.png` |
| G4 | Bow wave exceedance | 1 | OK | `figures/g4_bow_wave.pdf` + `.png` |
| G5 | Mass sensitivity | 1 | OK | `figures/g5_mass_sensitivity.pdf` + `.png` |
| G6 | Two measures of one run | 1 | OK | `figures/g6_two_measures.pdf` + `.png` |
| G7 | Geometry and gates | 1 | OK | `figures/g7_geometry_gates.pdf` + `.png` |
| G8 | Hero still, primary path | 1 | OK | `figures/g8_hero.pdf` + `.png`, frame 65, water 9.25 pct |
| G9 | Scope panel | 1 | OK | `figures/g9_scope.pdf` + `.png` |
| Phase 3 | Audit and manifest | 1 | OK | `docs/FIGURE_AUDIT_2026-07-26.md`, this file |

All nine figures built on the first attempt of the figure driver. Three subsequent rebuilds
were run to correct layout defects found by visually inspecting every rendered panel: a
mislabelled shaded region in G1, a callout colliding with tick labels in G3, a leader line in
G4 that read as a data series, an annotation sitting on the data line in G5, column overflow
in G7, and text wrapping past the panel edge in G9. Those were layout defects, not data
defects; no number changed.

## The one retry that mattered

The first water-visibility detector reported NO WATER in all three frames. That was the
detector's error, not the render's: it matched pixels against the pure viridis lookup table,
but the water is drawn at opacity 0.62 over a warm grey backdrop, so every blended pixel sits
far from pure viridis. Visual inspection of the extracted frames showed a large connected
water body in all three. The detector was rewritten to test chromaticity against the warm
backdrop (cool pixels where G-R or B-R exceeds 6, plus yellow pixels where G-B and R-B both
exceed 30) and to require a single connected blob above 2 pct of the frame. It now reports
9.97 / 9.25 / 9.44 pct. Counted as attempt 2 of 3.

## Files created this session

```
analysis/build_runs_inventory.py
analysis/make_poster_figures.py
data/all_runs_inventory.csv
docs/FIGURE_AUDIT_2026-07-26.md
figures/g1_velocity_sweep.pdf  .png
figures/g2_depth_sweep.pdf     .png
figures/g3_verdict_matrix.pdf  .png
figures/g4_bow_wave.pdf        .png
figures/g5_mass_sensitivity.pdf .png
figures/g6_two_measures.pdf    .png
figures/g7_geometry_gates.pdf  .png
figures/g8_hero.pdf            .png
figures/g9_scope.pdf           .png
renders/yaris_render_s1/check_water_frames.py
renders/yaris_render_s1/gates_all_runs.py
renders/yaris_render_s1/gates_results_all_runs.json
renders/yaris_render_s1/hero_g64_m1100_FIXED.mp4
renders/yaris_render_s1/hero_fixed.log
renders/yaris_render_s1/water_check.log
renders/yaris_render_s1/frame_check_f0005.png  f0045  f0085
run_manifest_figures.md
```

## File modified this session

`renders/yaris_render_s1/render_pv.py`, four lines deleted at 75-78. Backup at
`render_pv.py.bak_2026-07-26` predates the edit and is the unmodified original.

## Vista jobs

Checked live via `squeue` and `sacct` at 03:30 CDT. The queue for `jcerrell0629` is EMPTY.
All three named jobs are already terminal:

| job | name | state | ended |
|---|---|---|---|
| 866856 | yarisconv | CANCELLED (never started) | 2026-07-26T01:46:42 |
| 866869 | yarisconv | CANCELLED (never started) | 2026-07-26T01:46:42 |
| 866887 | yarisconv | COMPLETED, 00:04:03 | 2026-07-26T03:11:14 |

Nothing is queued and nothing is running, so there is nothing left to cancel and no
`mkdir -p` can land on a finished rollout from these jobs.
