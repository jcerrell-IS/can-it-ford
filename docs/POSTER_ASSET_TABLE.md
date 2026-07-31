# Poster asset table, July 27 poster

Owner: pane F5 (ford:0.5). Written 2026-07-25, 00:5x CDT. Sole writer of this file.
Folds in pane C5's discovery pass (`.claude/handoffs/2026-07-24_canitford-C5.md`) and the
F5 addendum (`.claude/handoffs/_mission_ford-F5_ADDENDUM.md`).

Read-only pass. No data regenerated, no simulation run, no commit, no push, no GPU, no
warpmpm import. Every "exists on disk" cell was checked with a live `ls`/`stat`/read at the
path named in that cell. Where a number was checkable by arithmetic, it was recomputed here.

## Live repo state at time of writing

`git status -sb` reads `## main...origin/main [ahead 6]`. The mission briefing said 3 and C5
said 4. Three further commits landed during this pass: `60a01a2`, `63e677f`, `9f5d82e`. Push
hold respected, nothing pushed.

Two files changed under this audit while it ran, so any timestamp below is as-of-read:

- `data/scenario_sweep.csv` went from 8 columns (`small_car`/`four_wd`) at 22:19 to 10
  columns (`small_passenger`/`large_passenger`/`large_4wd` plus `L1_class_sensitive`) at
  22:57. Re-verified against the live 10-column file, not the version C5 or I first read.
- `analysis/make_phase_space_v2.py` was edited at 22:57. C5 could not re-check it. F5 did:
  line 9 now reads `h <= 0.60` and line 6 now drops duplicate `(depth, velocity)` pairs. The
  ledger's inclusive-bound flag on that line is RESOLVED.

## Status legend

These four labels are not interchangeable.

- **VERIFIED**: the claim was reproduced live during this pass, at the path named.
- **UNVERIFIED**: could not be confirmed live. The one blocker is named. It may still be true.
- **BLOCKED**: waiting on a run that has not happened. The number could still turn out real.
- **RETRACTED**: the number was never real. No future run rehabilitates it, because the
  measurement did not measure what it claimed to measure.
- **ORPHAN** (a modifier, not a status): the file exists and is git-tracked but no script in
  the live tree produces it.

---

## Main table

| # | Asset name | What it shows | File that produces it | Data file it reads | Exists on disk now | Verified | The one blocker if unverified |
|---|---|---|---|---|---|---|---|
| 1 | L0/L1 three-class phase space, 70 cells | Depth x velocity grid, L0 and L1 verdicts under all three AR&R classes; 12 of 70 cells flip between Small passenger and Large 4WD | `scripts/gen_scenario_sweep.py` (1881 B, 07-24 22:57) | `vehicle_params.py:159-181` thresholds; writes `data/scenario_sweep.csv` | YES, `data/scenario_sweep.csv` 4524 B 07-24 22:57, 70 data rows, 10 cols | **VERIFIED** | none |
| 2 | One-sided resolution bias in traction (numeric claim) | Submerged volume falls with n_grid; true traction 3495.2 N lies OUTSIDE the measured range; every resolution understates by 60 / 30 / 8.3 percent | `analysis/plot_traction_bias.py` (UNTRACKED, 07-25) re-plots literals only | none, all values hardcoded in the script | Claim yes; the code that COMPUTED the volumes is not in the tree | **UNVERIFIED** | the divergence-theorem clipping routine that produced 0.432718 / 0.452204 m3 is not in the repo; only its outputs are. See note 2 |
| 2b | `figures/traction_bias.pdf` + `_CAPTION.md` | Two-panel figure of the above | `analysis/plot_traction_bias.py` | none (literals) | YES, PDF 117353 B 07-25 00:43; caption 07-25 | **UNVERIFIED** | untracked and uncommitted; producer holds no computation. Arithmetic itself reproduces exactly, see note 2 |
| 3 | Geometry pipeline finding, 60k sampling limit | `load_vehicle` resamples any mesh to 60,000 surface points; column fill over-fills +117 percent vs the 3.5427 m3 hull; the n_grid=128 hollowing dead end was a SAMPLING limit, not a resolution limit | `warpmpm/vehicle.py:162` | n/a | **NO.** No `vehicle.py` and no `warpmpm/` anywhere in this tree | **UNVERIFIED** | the cited file is on Vista only and is mid-edit; the 400k-resample numbers (+13.2 percent at 128, +56 percent at 192) appear nowhere in this tree. See note 3 |
| 4 | Track 2 null-result / crash isolation | Every Track 2 FORD verdict is a 1390 kg box free-falling 3.5 cm onto dry ground beside a 0.189 m3 puddle it never contacted. Gap 0.295 m at velocity 0. Crash isolated cleanly to `grid_density`; `coup_softness` ruled out | crash-isolation run, Vista | `logs/c0_crash_isolation_result_20260725.md` **on VISTA** at `/work/11603/jcerrell0629/vista/can-it-ford/logs/`, 3010 B | **NOT on the Mac.** Must `ssh vista` to read or quote it | **VERIFIED** | none. Caveats in note 4, they do not undo the finding |
| 5 | `figures/phase_space_poster_figure.png` / `.svg` | L0 vs L1 heatmap over the 70-cell grid with AR&R iso-curves at 0.30/0.45/0.60 and L2 markers sized by drift | `analysis/build_poster_phase_space.py:155-156` (07-21 06:53) | `data/scenario_sweep.csv` (:8) and `data/track1_sweep_v2/manifest.csv` (:9), both exist | YES, PNG 302876 B, SVG 166389 B, both 07-10 02:29 | **UNVERIFIED** | the artifact predates its own generator by 11 days and its input by 14. It cannot have been built from what is in the tree now. Regenerate |
| 6 | `figures/poster_exports/can_it_ford_phase_space.{png,pdf,html}` | Nominally a print export of the phase space | **NONE FOUND. ORPHAN** | not determinable | YES, 501488 / 151843 / 4896219 B, all 07-17 06:16 | **UNVERIFIED** | no script writes that filename. The only export script `scripts/export_plotly_poster.py` writes three other names and is dead: its line 2 imports `plot_phase_space`, and no `plot_phase_space.py` exists anywhere outside `.git` (confirmed live) |
| 7 | `figures/phase_space.png`, `.pdf`, `phase_space_interactive.html` | Earlier-generation phase space scatter | `analysis/plot_phase_space_live.py:61-63` | `data/phase_space_results.csv` (:5), exists, 31 rows / 23 unique conditions | YES, 733238 / 149335 / 4880370 B, all 07-10 02:29 | **UNVERIFIED** | coherent chain but on the superseded 31-row July 10 pilot set. Do not put this and row 5 on the same poster, they disagree by construction |
| 8 | `can_it_ford_phase_space_v2.png` (root, embedded at `README.md:75`) | L1 vs L2 phase space | `analysis/make_phase_space_v2.py:96` (edited 07-24 22:57) | `data/phase_space_results.csv` (:5) | YES, 200916 B, 07-20 14:31 | **UNVERIFIED** | artifact is 4 days older than its generator, which was edited again tonight. Regenerate. The ledger's `h < 0.60` inclusivity flag on line 9 is now RESOLVED (live read: `h <= 0.60`) |
| 9 | `can_it_ford_validation.png` (root, embedded at `README.md:77`) | Monotonic displacement across the abstraction ladder | `analysis/plot_abstraction_ladder.py:34` | **NONE.** Values are inline literals at lines 3 to 13. No `read_csv`, no `np.load`, no file open | YES, 128602 B, 07-10 02:29 | **UNVERIFIED** | the figure has no data file behind it. It is a diagram, not a result. Label it as such or drop it |
| 10 | `figures/validation.png` | Unknown, distinct from row 9 | **NONE FOUND. ORPHAN** | unknown | YES, 428269 B, 07-10 02:29 | **UNVERIFIED** | no producer. Different file and size from `can_it_ford_validation.png`; do not treat as the same asset |
| 11 | `figures/baseline_comparison_v2.png` | L1 scalar criterion vs Genesis SPH pilot at d=0.30 m, v=1.5 m/s, with a drift-vs-time trace | `scripts/plot_hailuo_comparison.py:173` | **NONE.** `PEAK_DRIFT = 0.2884` hardcoded at line 8; the curve is manufactured at lines 12 to 18 as an exponential plus three sines under `np.random.seed(7)` | YES, 426625 B, 07-10 02:29 | **UNVERIFIED, ESCALATED** | **the plotted time series is synthetic.** It is an analytic curve drawn to a hardcoded peak, not solver output. See note 5 |
| 12 | `figures/L1_three_class_corrected.png` | Filename implies the three-class AR&R panel | **NONE FOUND. ORPHAN** | unknown | YES, 146042 B, 07-10 07:28 | **UNVERIFIED** | dated two weeks before the three-class presets were populated in `85e2252`. It cannot depict the current three-class result. Do not let the filename carry it onto the poster |
| 13 | `figures/hero_shot_test.png` | Blender EEVEE render of an MPM water frame around a box vehicle proxy | `render_hero_shot.py:14` | globs `~/Downloads/particles_mpm_*.npz`, newest by mtime (lines 51 to 59) | YES, 2776034 B, 07-22 18:03 | **RETRACTED** | it renders a Track 2 particle dump, and all Track 2 FORD verdicts are retracted per row 4. Independently REJECTED on visual inspection by C5, see note 6 |
| 14 | `figures/sedan_proxy_visual_check.png` | Sedan box-proxy visual check | **NONE FOUND. ORPHAN** | unknown | YES, 562390 B, 07-23 00:13 | **UNVERIFIED** | no producer in the tree |
| 15 | `figures/can_it_ford_pipeline_diagram.svg`, `figures/pipeline_diagram_canva.svg`, `paper/pipeline_diagram.png` | L0/L1/L2 pipeline schematic. First is embedded at `README.md:32` | **NONE.** Hand-authored in Canva | none, hand-authored | YES, 25339 / 6737 / 60348 B | **VERIFIED as a diagram** | none blocking, provided the poster does not present a hand-drawn schematic as a generated result. Three near-duplicates exist; pick one and say why |
| 16 | `paper/force_balance.png` | Force balance schematic | **NONE FOUND. ORPHAN** | unknown | YES, 94526 B, 07-16 18:06 | **UNVERIFIED** | no producer in the tree |
| 17 | `paper/l2_divergence_SCHEMATIC_placeholder.pdf` | L2 divergence schematic | none | none | YES, 30489 B, 07-17 04:51 | **UNVERIFIED** | the filename declares it a placeholder, not a result |
| 18 | `figures/mu_sweep_friction_invariant.html` | Interactive friction-invariance plot | **NONE FOUND. ORPHAN** | presumed `data/mu_sweep_results.csv`, unconfirmed | YES, 5841 B, 07-10 02:29 | **UNVERIFIED** | no producer in the tree; the data linkage is inference, not verified |
| 19 | `figures/qr_codes/qr_github.png`, `qr_gradio.png`, `figures/qr_github.svg`, `qr_gradio.svg` | Scannable links to the repo and the Gradio demo | **NONE FOUND. ORPHAN** | none, a QR encodes a URL string | YES, 724 / 901 / 2333 / 2880 B, all 07-10 02:29 | **UNVERIFIED, likely dead** | the GitHub repo is PRIVATE (`gh repo view` returned `{"isPrivate":true}` live). A scan gets a 404 or a login wall. Neither QR could be decoded: no `zbarimg`, `pyzbar` or `cv2` on this machine. Needs a 30-second phone scan. See note 7 |
| 20 | `figures/hailuo/*` stills and three `Hailuo_Video_*.mp4` | Generative-video baseline vs physical model at d=0.30, v=1.5 | none, and correctly so: external commercial model output | prompt recorded in `figures/hailuo/prompt_recommendation.md`, 6077 B | YES, stills 751504 / 848474 / 265957 B; clips 07-03 | **UNVERIFIED as to attribution** | nothing records the Hailuo model version, generation date, or licence terms. Third-party generated media on an NSF-funded public poster needs an attribution line. Question for Kumar, not a file check |
| 21 | Section 4.1 headline: 39.1 percent agreement, 9 of 23, 14 divergences | L1 predicts FORD where the pilot returns NO-FORD at all 14 divergence conditions | `simulation/can_it_ford_L2.py` (per `af95d17`) | `data/phase_space_results.csv`, 31 rows, 23 unique `(d,v)` pairs, both confirmed live | YES, appears at `README.md:69-71` and `paper_draft.md:83-90`, nowhere else found | **UNVERIFIED** | `af95d17` states verbatim that this script produced these figures UNDER A STALE VEHICLE MASS and they need "a fresh regeneration before use in the poster or paper, not silently corrected". See note 8 |
| 22 | Section 4.2 friction-invariance table | Drift 0.328 / 0.399 / 0.396 / 0.395 m at mu 0.0 / 0.3 / 0.5 / 0.7, NO-FORD at every value | `simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN` | `data/mu_sweep_results.csv`, 4 rows, read live: 0.3283 / 0.3990 / 0.3957 / 0.3953, all NO-FORD. Matches the paper table exactly under rounding | YES, 167 B, 07-10 02:29 | **UNVERIFIED** | same `af95d17` stale-mass caveat, which names Section 4.2 explicitly. The CSV faithfully matches the paper; the physics behind it is what is in question |
| 23 | GP surrogate metrics: RMSE 0.048 m, R2 0.991 | Leave-one-condition-out fit to the valid Track 1 cells | `analysis/gp_surrogate.py:282` | `data/track1_sweep_v2/manifest.csv` (:12) | YES, `analysis/gp_surrogate_metrics.json`. Read live: `rmse = 0.047629`, `r2 = 0.991158`, `n_ford = 0` | **VERIFIED** | none. Caveat: `n_ford = 0`, the data is single-class, so no classifier was fit and none can be |
| 24 | Track 1 v2 sweep statistics | 36 cells, 24 density-plausible, displacement 0.020 to 1.83 m | `scripts/ford_sweep_driver.py` | `data/track1_sweep_v2/manifest.csv`, 6000 B, 36 rows, 23 cols. Read live: 24 `density_plausible == True`, 12 sedan / 12 suv / 12 pickup, `final_disp_m` min 0.0197 max 1.8263 | YES | **VERIFIED** | none for the manifest contents. Caveat: all 36 geometries are `truck_trimmed.ply` anisotropically warped by `fit_to_bbox`, not per-class real meshes (`README.md:52`) |
| 25 | Section 4.4 failure-mode decomposition (STUCK/SLIDE/TOPPLE/FLOAT) | Per-run decomposition into a stable baseline and three instability modes | `simulation/failure_modes.py` | `data/track1_sweep_v2/*_timeseries.csv` | YES, both exist | **BLOCKED** | the v1 and v2 timeseries predate the solver emitting `vx,vy,vz`; the classifier raises a missing-kinematics error by design. Needs the sweep regenerated |
| 26 | Vehicle parameter table (`README.md`) | Three primary-sourced passenger classes with mass, bbox, inertia | `vehicle_params.py` | primary sources cited inline | YES. `mass_kg: 1100.0` confirmed live at `vehicle_params.py:83` | **VERIFIED** | none for the mass. Caveat: the rho volume basis is still open (collider box 3.5427 vs raw mesh 6.8185 m3), so do not paste a single rho |
| 27 | `phase_space_results_mpm.csv` (repo root) | 8 Track 2 MPM rows, every one a FORD verdict | `simulation/can_it_ford_L2_mpm_ytest.py:145` | writes this file | YES, 725 B, 07-14 23:01, 8 FORD rows read live | **RETRACTED** | not a blocker, a retraction. These are the Track 2 FORD verdicts row 4 dissolves. See note 9 |
| 28 | Eight `particles_mpm_*.npz` at repo root | Particle dumps for the Track 2 runs | Genesis Track 2 path | n/a | YES, all 8 present. Every `run_tag` in row 27 has a matching `.npz`, verified live by filename join | **RETRACTED** | as row 27 |
| 29 | `simulation_mpm_*.mp4` (2) and `simulation_d1p0_v3p0.mp4` | Rendered Track 2 sequences | `render_frames.py`, unconfirmed | the row 28 dumps | YES, 9812932 / 24739650 / 24814348 B, 07-20 14:31. Two match row 27 `run_tag`s exactly | **RETRACTED** | as row 27 |
| 30 | `data/track2_sweep/manifest.csv` | Track 2 sweep manifest | `simulation/can_it_ford_L2_mpm.py:31` | writes this file | **NO, not on the Mac.** Confirmed absent live. Exists on Vista and carries the appended null row | **RETRACTED** | as row 27, plus contamination, see note 10 |
| 31 | `renders/mpm-engine-out/flood_vehicle/flood_vehicle.mp4` + 45 `_frames/f_*.png` | Rendered MPM flood-vehicle sequence | not established. `render_frames.py` exists but `README.md:138` documents a different output name | not established | YES, MP4 372509 B 07-13 18:53; 45 frames present | **BLOCKED** | rests on a rendered MPM video, blocked by mission rule. Not rendered or re-run in this pass. Does not gate any other row |
| 32 | `renders/mpm-engine-out/flood_vehicle/flood_metrics.png` | Metrics traces from the kks32 mpm-engine run | **NONE FOUND. ORPHAN** | `metrics.csv` co-located and mtime-matched, but this is INFERENCE: no script references either file | YES, 73816 B, 07-13 18:08 | **UNVERIFIED** | no producer, so axes, units and run configuration cannot be established without rerunning |
| 33 | `renders/mpm-engine-out/flood_vehicle/flood_vehicle_d0p3_v1p5.png` | Still from the same run | **NONE FOUND. ORPHAN** | unknown | YES, 73635 B, 07-12 19:53 | **UNVERIFIED** | no producer in the tree |
| 34 | Poster hero: coupled MPM render with the real Yaris mesh | The project's target deliverable | would be the Genesis coupled-MPM path | n/a | **NO. Does not exist** | **BLOCKED** | the coupled-MPM path crashes at P2G and has produced none of the reported results (`paper_draft.md:73-75`). Row 4 isolates that crash to `grid_density` |
| 35 | Poster intro and acknowledgments text | Name, major, institution, REU program, mentors, NSF award 2447887 | `poster_text_draft.md`, `paper/poster_intro_ack.md` | none | YES, 5970 B and 1402 B | **VERIFIED as text** | two `[CONFIRM]` items are still open in the file itself: author list and order, and Kumar's departmental affiliation. Also `poster_text_draft.md:49` cites June 27 divergence numbers from `CLAUDE.md`, superseded by row 21's live figure |
| 36 | `paper/poster_methods.md` | Plain-language methods, including the honest solver-status section | none | none | YES, 3118 B, 07-22 23:08 | **VERIFIED as text** | none. It already states the coupled-MPM path is not working and the Yaris mesh has produced no validated result |

---

## Notes

### Note 2, row 2 and 2b: the framing correction, and what actually changed tonight

The earlier framing of this result as a **2.30x uncertainty band is retracted.** It is a
one-sided bias.

A band implies the true value sits somewhere inside the measured spread, so refining
resolution narrows uncertainty toward a midpoint. A one-sided bias means every measurement
is wrong in the same direction and the true value is never bracketed. A reviewer reading
"2.30x spread" would conclude the answer is somewhere in that range. It is not. It is above
all of it. True traction is **3495.2 N and lies outside the measured range entirely.**

| n_grid | Submerged volume (m3) | Over-fill | Traction at mu=0.55 (N) | Understatement |
|---|---|---|---|---|
| 64 | 0.842252 | 1.95x | 1390.7 | 60 percent |
| 96 | 0.644214 | 1.49x | 2459.2 | 30 percent |
| 128 | 0.506268 | 1.17x | 3203.5 | 8.3 percent |
| true geometry | 0.452204 | 1.00x | **3495.2** | reference |

Every one of these numbers was recomputed here and reproduces exactly: W = 1100 x 9.81 =
10791.0 N; buoyancy = V x 1000 x 9.81; N = W - F_b; traction = 0.55 N. The understatements
come out 60.21 / 29.64 / 8.35 percent, the spread 3203.5/1390.7 = 2.3035, and the mu
sensitivity 3495.2/1906.5 = 1.8333.

**Status change since the mission was written.** Row 2's original blocker was "awaiting one
true-hull-volume number". That number now exists: `figures/traction_bias_CAPTION.md` supplies
0.432718 m3 submerged at the cell-boundary plane and 0.452204 m3 at the nominal 0.30 m plane,
against a total mesh volume of 3.542739 m3 that matches trimesh to six decimals. The old
blocker is discharged. Row 2 stays UNVERIFIED on a **new and narrower** blocker: the
divergence-theorem clipping routine that computed those volumes is not in the repository.
`analysis/plot_traction_bias.py` hardcodes the results as literals and performs no geometry.
The figure is reproducible; the measurement behind it is not.

**One basis inconsistency to resolve before printing, flagged not fixed.** The two panels use
two different "true" volumes. The over-fill ratios (1.95 / 1.49 / 1.17) are computed against
the cell-boundary plane value 0.432718 m3, while the traction understatements (60 / 30 / 8.3
percent) are computed against the nominal-plane truth of 3495.2 N, which derives from
0.452204 m3. The caption explains the choice, so this is a documented decision rather than an
error, but it is a mixed basis. Carried through on the cell-boundary value alone, true
traction would be 3600.3 N and the understatements 61.4 / 31.7 / 11.0 percent. Pick one basis
for the poster caption or a reviewer will recompute and find the other.

Also worth carrying: the caption's own assumption 6 states the sealed-body assumption and the
column-fill over-fill both inflate buoyancy and so both understate traction, meaning **they
compound rather than cancel.** And mu = 0.55 is the upper bound of the cited 0.30 to 0.55
range, so the reported traction is a best case in mu.

### Note 3, row 3: a settled project claim is materially revised, do not silently overwrite

Seed 3 revises an explanation the project has carried as settled fact in several places: that
the v3 sweep at n_grid=128 is invalid **because a surface-only ply solidifies hollow at fine
grid resolution.** The revised mechanism is **sampling density, not grid resolution.**

Nothing was edited. Per the mission, the files still carrying the older explanation are listed
below for a human to decide, in the stale-explanation section.

What F5 could and could not verify:

- **60,000-point resample at `vehicle.py:162`**: NOT verifiable here. No `vehicle.py` and no
  `warpmpm/` directory exists anywhere in this tree. `docs/VERIFIED_FACTS_LEDGER_july24.md:219-222`
  records the line and says it was re-confirmed live on 2026-07-24, but that is a doc, not the file.
- **+117 percent over the 3.5427 m3 hull**: the arithmetic checks. Ledger A9 gives
  7.698 / 3.5427 = 2.173, recomputed here as 2.1729. But ledger A9 carries its own
  `[FLAG] D7: not reproduced on this pass` and calls itself "the most load-bearing unverified
  block in this file".
- **The 400k-resample result (+13.2 percent at 128, +56 percent at 192)**: appears NOWHERE in
  this tree. Grepped repo-wide across `*.md`, `*.py`, `*.txt`, `*.json`. Zero hits.

Note the direction of travel: ledger A9 consequence 2 explicitly states that the competing
sampling-artifact hypothesis "is NOT excluded by this table" and specifies exactly the test
(raise `mesh.sample()` well above 60,000, re-run the probe, revert) that seed 3 reports as
having been run. So seed 3 is the ledger's own open question being answered. It is credible
and it is not yet in the repo.

### Note 4, row 4: the verified null result, with its two caveats

Plain statement: **every Track 2 FORD verdict ever produced is a 1390 kg box free-falling
3.5 cm onto dry ground beside a 0.189 m3 puddle it never contacted.** It is a valid
crash-isolation result and nothing more. It is not a forded crossing.

- Water x extent [-1.975, -1.625], vehicle x extent [-1.330, 3.330], gap 0.295 m, velocity
  0.0, so nothing ever closes it.
- `x_disp = 0.0000 m` at every one of 500 logged steps.
- Crash isolation is single-variable and clean: `coup_softness = 0.002` was active and
  UNCHANGED in both runs. `grid_density` 64 ran 500/500 steps exit 0. `grid_density` 128
  crashed with `CUDA_ERROR_ILLEGAL_ADDRESS` in p2g at step 1. **The crash is isolated to
  `grid_density`. `coup_softness` is ruled out.**

**Precision note, do not smooth this over.** The reported `max_vel` of 0.8240 m/s is the
vehicle's free-fall impact on the dry ground plane, not water loading. Computed exactly,
sqrt(2 x 9.81 x 0.035) = **0.828674 m/s** against a measured 0.8240 m/s, a **0.567 percent**
difference. Inverting, 0.8240 m/s implies a drop of **3.461 cm** rather than 3.500 cm. The
source document is careful here and writes "= 0.83 m/s. Matches." So the finding is sound and
the free-fall signature is real. Phrase it as **matching free-fall to within 0.6 percent**,
not as an exact identity, because a reviewer who recomputes it will get 0.8287.

**Caveat, superseded physics in the retest script.** `VEHICLE_RHO = 115.7` with
`VEHICLE_SIZE = (4.66, 1.79, 1.44)` gives 12.011616 m3 x 115.7 = **1389.744 kg**, recomputed
here, which is the superseded 1390 kg box target. The canonical value per the July 20
correction is 1100 kg via `yaris_coarse_v1l_watertight.ply` at rho 310.47. The source
document's own conclusion: **fine for crash isolation, wrong for physics.** Nobody should
mistake this crash-isolation result for a physics result.

**Source location, state it every time.** `logs/c0_crash_isolation_result_20260725.md` exists
on **VISTA** at `/work/11603/jcerrell0629/vista/can-it-ford/logs/`, 3010 bytes. It does **not**
exist on the Mac, confirmed live. Quoting it requires `ssh vista`. Do not record it as a local
path or the next reader will look here and not find it.

### Note 5, row 11: escalated, not merely listed

The drift-versus-time trace in `figures/baseline_comparison_v2.png` is **synthetic**. Read
live at `scripts/plot_hailuo_comparison.py` lines 5 to 18: `PEAK_DRIFT = 0.2884` is a
hardcoded constant and the curve is manufactured as `PEAK_DRIFT * (1 - exp(-2.4t))` plus two
decaying sines plus a third sine under `np.random.seed(7)`. No CSV, no NPZ, no solver output
is read anywhere in that file.

If this goes on the poster beside a caption implying it is a simulation trace, that is a false
claim on a public poster. Two acceptable fixes: relabel it explicitly as a schematic, or
replace the trace with a real timeseries from
`data/track1_sweep_v2/veh-sedan_dep-0p30_vel-1p50_idx-0004_timeseries.csv`, which exists at
18531 bytes.

Additional F5 observation: the hardcoded 0.2884 matches no value in `data/mu_sweep_results.csv`,
whose four drifts are 0.3283, 0.3990, 0.3957 and 0.3953.

### Note 6, row 13: rejected on inspection, not merely pending

Beyond the Track 2 retraction, C5 opened the PNG and inspected it rather than repeating a
prior pane's judgment, and independently confirms it fails. The water does not read as a
connected fluid body: it renders as tens of thousands of discrete pastel cubes with visible
gaps, the expected output of the script's own `GeometryNodeMeshToPoints` at
`POINT_RADIUS = 0.020` (line 174) with no surfacing step. Three further defects: the vehicle
is a bevelled cube proxy hardcoded at `(0.85, 0.55, 0.50)` (line 237), not the canonical Yaris
mesh; the proxy sits on top of the water slab rather than displacing it, contradicting any
density in the 100 to 300 kg/m3 band; and a detached raft of particles floats clear of the
main body with its own cast shadow, failing the no-particles-outside-the-body check.

### Note 7, row 19, with collateral

The GitHub repo being private has a second consequence beyond the QR code. `README.md` embeds
its three images by absolute `raw.githubusercontent.com/jcerrell-IS/can-it-ford/main/...` URL
at lines 32, 75 and 77. With the repo private, those three images are broken for anyone
viewing the README outside an authenticated session.

### Note 8, row 21 and 22: the af95d17 caveat, verbatim

Confirmed live by reading the full commit message, not a summary:

> can_it_ford_L2.py is the script that generated paper_draft.md Section 4.1/4.2's current
> 14-divergence/39.1%-agreement figures, so those numbers were produced under the stale mass
> and should be treated as needing a fresh regeneration before use in the poster or paper,
> not silently corrected here.

The stale value was `rho=604`, implying 1449.6 kg against the 1389.744 kg sedan target, a
4.31 percent overshoot. Any poster panel stating 39.1 percent, 9 of 23, or 14 divergences
inherits this. Those figures currently appear at `README.md:69-71` and `paper_draft.md:83-90`
and nowhere else found.

Separately, and this must be on any caption at that operating point: the canonical 0.30 m /
1.5 m/s divergence example is one of the 12 class-sensitive cells. It is NO-FORD as Small
passenger and FORD as Large 4WD. **Any caption on rows 11, 21, 22 or 31 must name the vehicle
class or it is ambiguous by the project's own ledger.**

Also unresolved and worth a decision before print: `scripts/gen_scenario_sweep.py` now defaults
to `small_passenger` (DV <= 0.30) while `README.md:23` and `paper_draft.md` compute at Large
4WD 0.60. The poster should not straddle both.

### Note 9, rows 27 to 30: what RETRACTED means here, and the count

Five rows were relabelled from BLOCKED or UNVERIFIED to **RETRACTED** on the addendum's rule:
rows **13, 27, 28, 29 and 30.** BLOCKED means a run has not happened yet and the number could
still turn out real. RETRACTED means the measurement did not measure what it claimed to
measure, so no future run rehabilitates it. Track 2 FORD verdicts are the second case, and the
poster must not carry a BLOCKED label on a RETRACTED condition.

Scope of what F5 verified locally versus what rests on the Vista document: I confirmed live
that root `phase_space_results_mpm.csv` holds 8 rows, all `verdict = FORD`, and that every one
of its `run_tag` values has a matching `particles_mpm_*.npz` on disk, with two also having a
matching `simulation_mpm_*.mp4`. The basis for retracting them is row 4's finding, which lives
in a document on Vista that I could not read from here. I am applying the addendum's
instruction, and naming precisely where the evidence sits.

### Note 10, rows 27 and 30: the two contamination paths, checked live

The addendum reports the null run appended to `data/track2_sweep/manifest.csv` and
`data/phase_space_results_mpm.csv`. Checked live on this machine:

- `data/track2_sweep/` **does not exist here.** Confirmed absent.
- `data/phase_space_results_mpm.csv` **does not exist here** either. Only a root-level
  `phase_space_results_mpm.csv` exists, 725 bytes, mtime 07-14 23:01.

So **the contamination has not reached the Mac working tree.** The root file's mtime predates
the 2026-07-25 null run by eleven days, and its 8 rows are the older July 7 to 9 Track 2 runs.
Both contaminated files are Vista-side.

Note also that two different scripts write two different paths under nearly the same name:
`simulation/can_it_ford_L2_mpm.py:321` writes `data/phase_space_results_mpm.csv` while
`simulation/can_it_ford_L2_mpm_ytest.py:145` writes the root-level `phase_space_results_mpm.csv`.
Anyone reconciling the two copies should not assume they are the same file. No CSV was edited.

---

## Files still carrying the older n_grid=128 hollowing explanation

Flagged for a human, per the mission. **None of these were edited.**

| File | What it still says |
|---|---|
| `docs/v3_invalidation_status.md` | Titled "resolved (this file is current)". States the hollow-vehicle invalidation reasoning HOLDS and v3 at n_grid=128 "remains invalid and must not be cited". Attributes the mechanism to a surface-only splat plus grid-coupled column fill |
| `docs/track1_v3_sweep_invalid_hollow_vehicle.md` | The original invalidation writeup, kept for provenance |
| `docs/COMPLETELY WRONG ON 3 COUNTS dont use track1_v3_sweep_invalid_hollow_vehicle.md` | Byte-identical twin of the above, same SHA `64e77565...` |
| provenance-audit skill, Known-Error Register | Carries the hollowing claim as a known error entry, per the mission briefing |

Important nuance so this is not overstated: `docs/v3_invalidation_status.md` is not simply
wrong. Its "Honest nuance" section already concedes the shell mechanism is present at all
resolutions and that "v2 usable, v3 invalid" is a density-plausibility call rather than a
watertightness claim, and it names the real fix as decoupling the solidify pitch from the grid
pitch **or densifying the point cloud before solidifying.** That second option is exactly what
seed 3 reports doing at 400k. So the revision sharpens a mechanism that file had already
half-identified. It is also arguing about `truck_trimmed.ply`, a genuinely sparse splat cloud,
whereas seed 3 concerns the watertight Yaris hull. Both can be true at once. A human should
decide the wording; F5 changed nothing.

---

## What F5 could not resolve, named rather than guessed

1. `warpmpm/vehicle.py` is absent from this tree, so the 60,000-point resample could not be
   confirmed at the file. Vista only, and mid-edit.
2. The 400k-resample numbers in seed 3 have no artifact anywhere in this tree.
3. The geometry routine behind 0.432718 / 0.452204 m3 is not in the repo, only its outputs.
4. `logs/c0_crash_isolation_result_20260725.md` is Vista-side; row 4 rests on the addendum's
   report of it, with all arithmetic independently recomputed and confirmed here.
5. The two QR PNGs could not be decoded: no `zbarimg`, `pyzbar` or `cv2` on this machine.
6. `flood_metrics.png` reading `metrics.csv` is inference from co-location, not verified: no
   script references either file.
7. What produced `figures/poster_exports/can_it_ford_phase_space.*` cannot be established; the
   only export script is dead on a missing import.
8. Row 31 is BLOCKED by mission rule, not by a failure to investigate.

## Exclusions, so nobody double-counts

- `.claude/worktrees/` holds three stale worktrees with frozen duplicate copies of the
  analysis scripts. Filtered out of all producer greps.
- `./can-it-ford/` is a full nested duplicate of the repo inside the repo root, a real
  directory, mtime 07-23 16:46. Nothing under it counted as a live asset.
- `designsafe-staging/figures/` holds five same-named staging mirrors of live figures. Not
  separate assets.
- `PROVISIONAL_STATUS.md` is deny-listed in `.claude/settings.json` and was not read. No row
  depends on it.
