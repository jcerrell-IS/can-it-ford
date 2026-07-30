# C5 handoff: poster asset discovery and existence verification

Pane C5, canitford:0.5. Written 2026-07-25 00:45 CDT. All stats below taken live on this
machine between 22:50 CDT 2026-07-24 and 00:40 CDT 2026-07-25.

F5 owns `docs/POSTER_ASSET_TABLE.md`. C5 did not write, open for write, or touch that file.
C5 made no commits, no pushes, ran no simulation, imported no warpmpm, requested no GPU.
This pass was read-only.

## Search scope actually covered

Covered: `figures/`, `figures/poster_exports/`, `figures/qr_codes/`, `figures/hailuo/`,
`paper/`, `analysis/`, `scripts/`, `data/`, `data/track1_sweep_v2/`, `simulation/`,
`renders/`, `docs/`, repo root, `poster_text_draft.md`, `paper_draft.md`, `README.md`, and a
repo-wide find for every `*.png`, `*.svg`, `*.pdf`, `*.jpg`, `*.mp4` outside `.git`.

Excluded deliberately, and I confirm the exclusion: `.claude/worktrees/`. Three stale
worktrees exist there (`reconcile-vehicle-master-ref`, `physics-params-audit-541e4f`,
`eloquent-easley-3ca1ff`) and every one holds frozen duplicate copies of the analysis
scripts. They polluted my first producer greps and were filtered out of all results below.

Also excluded: `./can-it-ford/`, a full nested duplicate copy of the repo sitting inside the
repo root, real directory not a symlink, mtime 2026-07-23 16:46. Nothing under it was
counted as a live asset. Flagging it because it duplicates almost every figure path below
and will produce false hits for anyone grepping without a filter.

`PROVISIONAL_STATUS.md` is deny-listed in `.claude/settings.json`. I did not attempt to read
it. No asset row below depends on it.

## Two live corrections to the mission briefing

1. The briefing says local main is 3 commits ahead of origin/main. Live `git status -sb`
   reads `## main...origin/main [ahead 4]`. Push hold still respected, nothing pushed.
2. `data/scenario_sweep.csv` was rewritten by another pane WHILE I was auditing it. At 22:19
   it was 3559 bytes, 8 columns, classes named `small_car` / `four_wd`. At 22:57 it was 4524
   bytes, 10 columns, classes renamed to `small_passenger` / `large_passenger` / `large_4wd`
   plus a new `L1_class_sensitive` column. Row count 71 including header, that is 70 data
   cells, unchanged. Any asset row keyed to that file needs its timestamp restated at fold-in
   time, not copied from here.

## Headline: only one candidate has an intact script-plus-data chain, and it is stale

Of everything below, exactly one asset traces to a generator script that exists AND to input
data files that exist. That is `figures/phase_space_poster_figure.{png,svg}`. Every other
image in this repo is an orphan by the mission's own definition, or is blocked, or is
synthetic. Details per row.

---

## ASSET ROWS

### A1. Phase space poster figure

- **asset name**: `figures/phase_space_poster_figure.png` and `.svg`
- **what it shows**: L0 vs L1 verdict heatmap across the 70-cell depth-velocity grid, with
  AR&R iso-curves at D x V = 0.30 / 0.45 / 0.60 overlaid and L2 coupled-MPM runs plotted as
  markers sized by final drift.
- **producing script**: `analysis/build_poster_phase_space.py`, 5592 bytes, 2026-07-21 06:53.
  Verified to exist. Output stem read live from line 12, writes `.png` at line 155 and `.svg`
  at line 156.
- **input data**, both read live from lines 8 and 9, not inferred from filename:
  - `data/scenario_sweep.csv`, 4524 bytes, 2026-07-24 22:57, 70 data rows. Exists.
  - `data/track1_sweep_v2/manifest.csv`, 6000 bytes, 2026-07-16 17:10, 36 data rows. Exists.
- **exists on disk now**: YES. `figures/phase_space_poster_figure.png` 302876 bytes and
  `figures/phase_space_poster_figure.svg` 166389 bytes, both 2026-07-10 02:29. Paths checked
  directly with stat.
- **verified or unverified**: UNVERIFIED.
- **the one blocker**: the artifact on disk predates its own generator by 11 days. PNG/SVG
  mtime 2026-07-10 02:29, generator mtime 2026-07-21 06:53, primary input mtime 2026-07-24
  22:57. The file on disk was NOT produced by the script now in the tree, and cannot have
  been produced from the data now in the tree. It must be regenerated before it can be
  called current. I did not regenerate it, that is a write.

Secondary notes F5 will want:
- The script filters L2 markers to `density_plausible == True` (line 90) and plots only
  `sedan` and `pickup` (line 101), so SUV rows are dropped. The figure's own caption text at
  line 152 says so.
- `DRIFT_THRESHOLD = 0.05` is hardcoded at line 14. Per `README.md:71` that threshold has no
  direct published source.
- The script reads the column `L1_verdict`, which survived the 22:57 rename, so the poster
  build is not broken by the column churn. Confirmed against the live header.
- The L2 markers come from the v2 sweep. Treat the v2 geometry provenance as a separate
  question for whoever owns it. I did not re-derive it and am not asserting it here.

### A2. Poster exports phase space

- **asset name**: `figures/poster_exports/can_it_ford_phase_space.{png,pdf,html}`
- **what it shows**: nominally a print-export of the phase space figure.
- **producing script**: NONE FOUND. This is an ORPHAN.
- **input data**: not determinable, no producer.
- **exists on disk now**: YES. PNG 501488 bytes, PDF 151843 bytes, HTML 4896219 bytes, all
  2026-07-17 06:16. Paths checked directly.
- **verified or unverified**: UNVERIFIED, ORPHAN.
- **the one blocker**: no script in the live tree writes any file named
  `can_it_ford_phase_space.*`. The only export script, `scripts/export_plotly_poster.py`,
  writes three different names (`phase_space.svg`, `phase_space.pdf`,
  `phase_space_preview.png`, lines 7 to 9) and is itself dead: its line 2 does
  `from plot_phase_space import make_figure`, and a repo-wide find shows NO file named
  `plot_phase_space.py` anywhere outside `.git`. That import fails on execution. So this
  asset cannot be reproduced and its provenance cannot be established from the repo.
  `SESSION_STATE.md:302` claims these three files were "built", which is a claim about the
  past, not a producer.

### A3. Live phase space, matplotlib/plotly pair

- **asset name**: `figures/phase_space.png`, `figures/phase_space.pdf`,
  `figures/phase_space_interactive.html`
- **what it shows**: earlier-generation phase space scatter.
- **producing script**: `analysis/plot_phase_space_live.py`, 2733 bytes, 2026-07-10 02:29.
  Exists. Writes all three at lines 61 to 63.
- **input data**: `data/phase_space_results.csv`, read live from line 5. Exists, 1219 bytes,
  2026-07-10 02:29, 31 data rows.
- **exists on disk now**: YES. PNG 733238 bytes, PDF 149335 bytes, HTML 4880370 bytes, all
  2026-07-10 02:29.
- **verified or unverified**: UNVERIFIED.
- **the one blocker**: the input CSV is the 31-row pilot result set from July 10, superseded
  by the v2 sweep manifest that A1 uses. This is a coherent chain but it is the old data.
  Do not put A1 and A3 on the same poster, they disagree by construction.

### A4. Root phase space v2

- **asset name**: `can_it_ford_phase_space_v2.png` (repo root)
- **what it shows**: L1 vs L2 phase space. This is the image `README.md:75` embeds.
- **producing script**: `analysis/make_phase_space_v2.py`, 4040 bytes, 2026-07-24 22:57.
  Exists. Writes at line 96.
- **input data**: `data/phase_space_results.csv`, read live from line 5. Exists, see A3.
- **exists on disk now**: YES. 200916 bytes, 2026-07-20 14:31.
- **verified or unverified**: UNVERIFIED.
- **the one blocker**: the generator was edited at 22:57 tonight by another pane, 2 days
  after the artifact was written, so the on-disk PNG is again stale relative to its script.
  Separately, `docs/VERIFIED_FACTS_LEDGER_july24.md:635` flags this exact script, line 9, as
  still computing `h < 0.60` where the AR&R source writes the criterion inclusive as
  `DV <= 0.60`, a 4-cell discrepancy. Flagged as not yet fixed as of the ledger. I did not
  re-check line 9 after the 22:57 edit, so treat the flag as possibly resolved and re-read
  before folding.

### A5. Abstraction ladder validation

- **asset name**: `can_it_ford_validation.png` (repo root)
- **what it shows**: monotonic displacement validation across the abstraction ladder. This is
  the image `README.md:77` embeds.
- **producing script**: `analysis/plot_abstraction_ladder.py`, 1623 bytes, 2026-07-10 02:29.
  Exists. Writes at line 34.
- **input data**: NONE. I read the script live. It contains no `read_csv`, no `np.load`, no
  file open. Its values are inline in the script body.
- **exists on disk now**: YES. 128602 bytes, 2026-07-10 02:29.
- **verified or unverified**: UNVERIFIED.
- **the one blocker**: the figure has no data file behind it. Whatever numbers it draws are
  literals typed into the plotting script, so the figure cannot be traced to a sweep, a run,
  or a CSV. It is a diagram, not a result. Label it as such or drop it.

### A6. Hailuo baseline comparison

- **asset name**: `figures/baseline_comparison_v2.png`
- **what it shows**: side-by-side of the L1 scalar criterion against the Genesis SPH pilot at
  d = 0.30 m, v = 1.5 m/s, including a drift-versus-time trace.
- **producing script**: `scripts/plot_hailuo_comparison.py`, 8234 bytes, 2026-07-10 02:29.
  Exists. Writes at line 173.
- **input data**: NONE, and this one matters. Read live, lines 5 to 18: `PEAK_DRIFT = 0.2884`
  is a hardcoded constant, and the drift curve is manufactured as
  `PEAK_DRIFT * (1 - exp(-2.4t))` plus two decaying sines plus a third sine, under
  `np.random.seed(7)`. No CSV, no NPZ, no simulation output is read anywhere in the file.
- **exists on disk now**: YES. 426625 bytes, 2026-07-10 02:29.
- **verified or unverified**: UNVERIFIED, and I am escalating this one rather than just
  listing it.
- **the one blocker**: the time series in this figure is synthetic. It is an analytic curve
  drawn to land on a hardcoded peak value, not a plot of solver output. If it goes on the
  poster next to a caption implying it is a simulation trace, that is a false claim on a
  public poster. Either relabel it explicitly as a schematic, or replace the trace with a
  real timeseries from `data/track1_sweep_v2/veh-sedan_dep-0p30_vel-1p50_idx-0004_timeseries.csv`
  which exists, 18531 bytes, 2026-07-16 17:10. F5 should not fold this row silently.

### A7. Hero shot render

- **asset name**: `figures/hero_shot_test.png`
- **what it shows**: Blender EEVEE render of an MPM water frame around a rectangular vehicle
  proxy on a dark floor under an HDRI sky.
- **producing script**: `render_hero_shot.py`, 8814 bytes, 2026-07-22 18:07. Exists. Output
  path read live from line 14.
- **input data**, read live from lines 51 to 59, not inferred: the script takes an `.npz` on
  argv, and with no argv it globs `~/Downloads/particles_mpm_*.npz` and takes the newest by
  mtime. Those files exist outside the repo, for example
  `/Users/josie/Downloads/particles_mpm_d0p3_v1p5_grid128_cf0p4_20260709_190529.npz`,
  4538706 bytes, 2026-07-21 23:21. The HDRI dependency
  `assets/hdri/kloofendal_43d_clear_puresky_2k.hdr` exists, 4624289 bytes, 2026-07-22 17:35.
- **exists on disk now**: YES. 2776034 bytes, 2026-07-22 18:03.
- **verified or unverified**: UNVERIFIED, and REJECTED on visual inspection.
- **the one blocker**: I opened the PNG and looked at it rather than repeating the prior
  pane's judgment. That judgment is CORRECT and I confirm it independently. The water does
  not read as a connected fluid body. It renders as tens of thousands of discrete pastel
  cubes with visible gaps between them, which is the expected output of the script's own
  `GeometryNodeMeshToPoints` at `POINT_RADIUS = 0.020` (line 174) with no surfacing step.
  Three further defects I saw that are worth recording:
  1. The vehicle is a bevelled cube proxy, `make_vehicle` lines 122 to 139, dimensions
     hardcoded `(0.85, 0.55, 0.50)` at line 237. It is not the canonical Yaris mesh
     `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`, which exists, 12445769
     bytes, 2026-07-18 21:44.
  2. The proxy sits on top of the water slab rather than displacing it. There is no
     submergence, which contradicts any vehicle density in the 100 to 300 kg/m3 band.
  3. A detached raft of particles floats clear of the main body at lower left, with its own
     cast shadow, so the frame also fails the no-particles-outside-the-body check.
  This asset is not poster-usable in its current form. It is not merely unverified.

### A8. MPM engine flood metrics

- **asset name**: `renders/mpm-engine-out/flood_vehicle/flood_metrics.png`
- **what it shows**: metrics traces from the kks32 mpm-engine flood_vehicle run.
- **producing script**: NONE FOUND. ORPHAN. A repo-wide grep for `flood_metrics` across
  `*.py`, `*.sh`, `*.ipynb`, worktrees and the nested duplicate excluded, returns zero hits.
- **input data**: `renders/mpm-engine-out/flood_vehicle/metrics.csv` exists, 18363 bytes,
  2026-07-13 18:08, and is the obvious candidate by co-location and matching mtime, but I
  could not confirm that linkage from any script because no script references either file.
  Recording this as inference, explicitly NOT as verified.
- **exists on disk now**: YES. 73816 bytes, 2026-07-13 18:08.
- **verified or unverified**: UNVERIFIED, ORPHAN.
- **the one blocker**: no producer exists in the tree, so the axes, units and run
  configuration behind the plot cannot be established without rerunning something.

### A9. MPM engine flood video and frames

- **asset name**: `renders/mpm-engine-out/flood_vehicle/flood_vehicle.mp4` plus the 45-frame
  sequence in `_frames/f_0000.png` to `f_0044.png`
- **what it shows**: the rendered MPM flood-vehicle sequence.
- **producing script**: not established. `render_frames.py` exists at repo root, 10666 bytes,
  2026-07-10 02:30, and `README.md:138` documents invoking it with `--input particles.npz
  --output water_box.mp4`, but that is a different output name and I did not confirm it
  produced these files.
- **input data**: not established.
- **exists on disk now**: YES. MP4 372509 bytes, 2026-07-13 18:53. Frames present, 45 files.
- **verified or unverified**: BLOCKED.
- **the one blocker**: BLOCKED per mission rule, this rests on a rendered MPM video. Per the
  hard constraints I did not render, re-run, or open a GPU allocation to settle it. Do not
  let this gate A1 through A6.

### A10. QR codes

- **asset name**: `figures/qr_codes/qr_github.png`, `figures/qr_codes/qr_gradio.png`, plus
  `figures/qr_github.svg` and `figures/qr_gradio.svg` at the `figures/` level
- **what it shows**: scannable links to the GitHub repo and the HuggingFace Gradio demo.
- **producing script**: NONE FOUND. ORPHAN. Grep for `qrcode`, `qr_github`, `qr_gradio`
  across `*.py` and `*.sh` returns zero hits in the live tree.
- **input data**: none, a QR encodes a URL string.
- **exists on disk now**: YES, `figures/qr_codes/` exists. `qr_github.png` 724 bytes, 370x370
  1-bit grayscale. `qr_gradio.png` 901 bytes, 410x410 1-bit grayscale. Both 2026-07-10 02:29.
  SVG variants 2333 and 2880 bytes, same date.
- **verified or unverified**: UNVERIFIED, and flagged as likely dead on arrival.
- **the one blocker**: two problems, both live-checked.
  1. The GitHub repo is PRIVATE. Verified live tonight, not from a doc:
     `gh repo view jcerrell-IS/can-it-ford --json visibility,isPrivate` returns
     `{"isPrivate":true,"visibility":"PRIVATE"}`. A poster viewer scanning a QR that points at
     `github.com/jcerrell-IS/can-it-ford` gets a 404 or a login wall. Either make the repo
     public before July 27 or pull the GitHub QR off the poster.
  2. I could not decode either QR to confirm what URL it actually encodes. No decoder is
     installed on this machine: `zbarimg` not found, `pyzbar` not installed, `cv2` not
     installed. The SVGs contain only path geometry, no URL text. Someone must scan these
     two PNGs with a phone and read the destination out loud before printing. That is a
     30-second manual check and I could not do it read-only from here.

  Same-cause collateral, worth one line in F5's table: `README.md` embeds its two result
  images by absolute `raw.githubusercontent.com/jcerrell-IS/can-it-ford/main/...` URL at
  lines 32, 75 and 77. With the repo private those three images are now broken for anyone
  viewing the README outside an authenticated session.

### A11. Pipeline diagrams

- **asset name**: `figures/can_it_ford_pipeline_diagram.svg`, `figures/pipeline_diagram_canva.svg`,
  `paper/pipeline_diagram.png`
- **what it shows**: the L0/L1/L2 pipeline schematic. `README.md:32` embeds the first.
- **producing script**: NONE FOUND for any of the three. ORPHANS. The Canva filename implies
  these were authored by hand in Canva, which is legitimate for a diagram but means there is
  no reproducible chain.
- **input data**: none, hand-authored.
- **exists on disk now**: YES. `can_it_ford_pipeline_diagram.svg` 25339 bytes 2026-07-10
  02:29, `pipeline_diagram_canva.svg` 6737 bytes 2026-07-10 02:29, `paper/pipeline_diagram.png`
  60348 bytes 2026-07-17 03:51.
- **verified or unverified**: UNVERIFIED as data, but this is the benign case.
- **the one blocker**: none blocking use, provided the poster does not present a hand-drawn
  schematic as a generated result. Three near-duplicate versions exist and nothing in the
  repo says which is current. F5 should pick one and say why.

### A12. Remaining orphan images with no producer at all

Each of these exists on disk, is git-tracked, and has ZERO producing script anywhere in the
live tree. I grepped `*.py`, `*.sh` and `*.ipynb` repo-wide for each filename stem with
worktrees and the nested duplicate filtered out, and got no hits.

| asset | path checked | size | mtime | status |
|---|---|---|---|---|
| L1 three-class figure | `figures/L1_three_class_corrected.png` | 146042 | 2026-07-10 07:28 | ORPHAN |
| Sedan proxy visual check | `figures/sedan_proxy_visual_check.png` | 562390 | 2026-07-23 00:13 | ORPHAN |
| Validation figure | `figures/validation.png` | 428269 | 2026-07-10 02:29 | ORPHAN |
| Force balance | `paper/force_balance.png` | 94526 | 2026-07-16 18:06 | ORPHAN |
| Flood vehicle still | `renders/mpm-engine-out/flood_vehicle/flood_vehicle_d0p3_v1p5.png` | 73635 | 2026-07-12 19:53 | ORPHAN |

Note on `figures/L1_three_class_corrected.png`: the name suggests it is the three-class AR&R
panel, which is exactly the panel
`docs/VERIFIED_FACTS_LEDGER_july24.md:601-618` argues earns its space on the poster (12 of 70
cells class-sensitive, table enumerated there and confirmed live in the ledger). But the file
is dated 2026-07-10 07:28, two weeks before the three-class presets were populated in commit
`85e2252`. It cannot depict the current three-class result. Do not let the filename carry
it onto the poster. If a three-class panel is wanted, it needs generating from the live
`data/scenario_sweep.csv`, which as of 22:57 tonight now carries all three
`L1_verdict_small_passenger` / `_large_passenger` / `_large_4wd` columns plus
`L1_class_sensitive`. That is a build, not a discovery, so it is out of C5's scope.

Note on `figures/validation.png` versus `can_it_ford_validation.png` at repo root: these are
different files at different sizes, 428269 versus 128602 bytes. Only the root one has a
producer (A5). The `figures/` one is an orphan. Do not treat them as the same asset.

### A13. Hailuo source stills and clips

- **asset name**: `figures/hailuo/opening_frame_clean.png`, `peak_frame.png`,
  `hailuo_frame_2.5s.png`, plus three `Hailuo_Video_*.mp4` clips
- **what it shows**: frames from the Hailuo generative video model, used per `README.md:193`
  as the visual-model-versus-physical-model comparison at d = 0.30 m, v = 1.5 m/s.
- **producing script**: none, and correctly so. These are outputs of an external commercial
  model, not of this repo.
- **input data**: the prompt is recorded in `figures/hailuo/prompt_recommendation.md`, 6077
  bytes, 2026-07-17 05:11. Exists.
- **exists on disk now**: YES. PNGs 751504, 848474 and 265957 bytes, all 2026-07-10 02:29.
  MP4s 3008952, 2216715 and 540717 bytes, 2026-07-03.
- **verified or unverified**: UNVERIFIED as to attribution.
- **the one blocker**: nothing in the repo records the Hailuo model version, generation date
  or licence terms for poster reuse. Third-party generated media on an NSF-funded public
  poster needs an attribution line. That is a question for Kumar, not a file check.

### A14. Duplicated staging copies, do not double-count

`designsafe-staging/figures/` holds five files with the same names as live figures:
`opening_frame_clean.png`, `peak_frame.png`, `phase_space_poster_figure.png`,
`phase_space_poster_figure.svg`, `pipeline_diagram_canva.svg`. These are a staging mirror,
not separate assets. Excluded from the rows above. Recording them so F5 does not add them as
duplicate table rows if they run their own find.

---

## Caveat that must be attached to specific rows, per mission

Commit `af95d17` is confirmed live. I read the full commit message rather than the summary.
Verbatim from it:

> can_it_ford_L2.py is the script that generated paper_draft.md Section 4.1/4.2's current
> 14-divergence/39.1%-agreement figures, so those numbers were produced under the stale mass
> and should be treated as needing a fresh regeneration before use in the poster or paper,
> not silently corrected here.

Rows inheriting this caveat: any poster panel that states the 39.1 percent agreement, the
9-of-23, or the 14-divergence figures. Confirmed live tonight, those figures currently appear
at `README.md:69-71` and `paper_draft.md:83-90` and nowhere else that I found. Section 4
exists at lines 79 to 145 with 4.1 through 4.5 present, confirmed live, it is not a stub.
`paper_draft.md` contains NO figure references at all, so no image asset is pulled in by the
paper draft. Every asset above is poster-side only.

Additional live cross-check F5 should not skip: `docs/VERIFIED_FACTS_LEDGER_july24.md:620-622`
records that the 0.30 m / 1.5 m/s cell, which is the canonical divergence example in
`paper_draft.md` 4.1 and the exact operating point of assets A6 and A9, is class-sensitive.
It is NO-FORD as Small passenger and FORD as Large 4WD. Any caption on any of those assets
must name the vehicle class or it is ambiguous by the project's own ledger.

## What C5 did not resolve, named rather than guessed

1. Cannot decode the two QR PNGs. No decoder installed. Needs a phone scan.
2. Cannot confirm `flood_metrics.png` reads `metrics.csv`. No producer exists to read.
3. Cannot establish what produced `figures/poster_exports/can_it_ford_phase_space.*`. The
   only export script is dead on a missing import.
4. Did not re-read `analysis/make_phase_space_v2.py:9` after another pane edited that file at
   22:57, so the ledger's `h < 0.60` inclusivity flag may or may not still hold.
5. A9 left BLOCKED by rule, not by failure.

## Recommendation to F5, one line

Only A1 is worth building the poster's central result panel around, and it needs regenerating
first. A6 needs relabelling or replacing before it goes anywhere public. A7 is rejected, not
pending. A10 is likely dead until the repo goes public or the QR is pulled.

---
---

# SECOND PASS, appended 2026-07-25 01:05 CDT

Everything above stands unchanged. This section adds assets and defects found after the first
pass was written. Same rules: live checks only, worktrees and the nested `./can-it-ford/`
duplicate excluded.

## B1. No assembled poster file exists anywhere in the repo

Searched the whole tree for `*Cerrell*`, `*42x56*` and `*poster*`. Full result set: five text
and script files, `figures/poster_exports/` (contents already covered as A2),
`figures/phase_space_poster_figure.{png,svg}` (A1), and the two `designsafe-staging` mirrors
(A14). There is NO `Cerrell_TACC_42x56.pdf` and no assembled poster document of any kind.

`poster_text_draft.md:4` states the deliverable is `Cerrell_TACC_42x56`, PDF, under 40 MB,
due Monday July 27 9am CST. As of this check the deliverable file does not exist. That is a
scope fact for F5's table, not an asset row.

## B2. Poster body text assets, previously unlisted

These are real poster deliverables and belong in the table alongside the images.

| asset | path checked | size | mtime | status |
|---|---|---|---|---|
| Poster title/authors/intro/ack draft | `poster_text_draft.md` | 5970 | 2026-07-15 04:24 | EXISTS, carries 3 unresolved [CONFIRM] blocks |
| Poster Methods section | `paper/poster_methods.md` | 3118 | 2026-07-22 23:08 | EXISTS |
| Poster intro and acknowledgments | `paper/poster_intro_ack.md` | 1402 | 2026-07-22 20:17 | EXISTS |

- **producing script**: none, hand-written prose. Correct for this asset type.
- **input data**: none.
- **verified or unverified**: UNVERIFIED on specific factual claims, see below.
- **the one blocker on `poster_text_draft.md`**: it carries three self-flagged `[CONFIRM]`
  blocks that no file in the repo can settle, at lines 24, 33 and 49. Author list and order
  are explicitly labelled a guess. Kumar's departmental affiliation is unverified. Line 49
  flags the L1/L2 divergence numbers as sourced from `CLAUDE.md` and needing re-verification.
  That third one is now partly answered: the live numbers are 39.1 percent, 9 of 23, 14
  divergences, confirmed tonight at `README.md:69-71` and `paper_draft.md:83-90`, and they
  carry the `af95d17` stale-mass caveat recorded in the first pass. The author-list and
  affiliation questions remain open and are a Kumar question, not a file check.

`paper/poster_methods.md` is the single most useful honest-disclosure text in the repo and
F5 should not lose it. Read live, it already states in the author's own voice that the
results use a box-proxy vehicle and not a car mesh, that the runs are a compact sedan at
1390 kg and a light pickup at 2300 kg, that the midsize SUV was dropped for implausible
density, that the sedan lands in the Large passenger class and not Small Car, and that the
2010 Toyota Yaris mesh has not produced a validated result and is not a claim on this poster.
Those disclosures line up with what A1's generator actually does, which filters to
`density_plausible == True` and plots only sedan and pickup.

## B3. Vehicle mass: two different numbers, both legitimate, easy to conflate on a poster

Verified live, not from memory:

- `vehicle_params.py:83` gives `mass_kg: 1100.0` for the Yaris class, with the comment at
  line 82 sourcing it to the FE deck header "Version 1l, 1100 kg". Confirmed as the briefing
  said it should read. Other classes at lines 112 and 134 are `midsize_suv` 1990.0 and
  `light_pickup` 2300.0.
- `data/track1_sweep_v2/manifest.csv` gives `vehicle_mass_kg = 1390.0` for every sedan row.
  `paper/poster_methods.md` says 1390 kg. Commit `af95d17`'s message derives against a
  1389.744 kg sedan target.

These are not in conflict. 1390 kg is the box-proxy compact sedan that actually produced the
v2 sweep. 1100 kg is the Yaris mesh that has not produced a validated result. The risk is a
caption: if any poster panel built from A1 is labelled "Toyota Yaris", it is wrong, because
those markers are 1390 kg box-proxy runs. `paper/poster_methods.md` already draws this
distinction correctly. Keep that wording.

Note the pickup agrees at 2300 kg across both sources.

## B4. The IEEE conference paper will not build, two figures do not exist

`paper/conference_101719.tex`, 23546 bytes, 2026-07-17 07:49. It loads `graphicx` at line 5
and sets NO `\graphicspath`, so all five `\includegraphics` targets resolve relative to
`paper/`. Checked each target with find across the live tree:

| line | target | found at | verdict |
|---|---|---|---|
| 66 | `pipeline_diagram.pdf` | nowhere | MISSING. `paper/pipeline_diagram.png` exists, wrong extension |
| 90 | `L0_L1_phase_space_divergence.png` | nowhere in the repo | MISSING entirely |
| 97 | `L1_three_class_corrected.png` | `figures/`, not `paper/` | WRONG DIRECTORY, tex will not find it |
| 138 | `force_balance.png` | `paper/force_balance.png` | OK |
| 177 | `l2_divergence_SCHEMATIC_placeholder.pdf` | `paper/` | OK, and self-labelled a placeholder |

So three of five figure includes fail. `paper/conference_101719_preview.pdf`, 531871 bytes,
2026-07-17 13:24, therefore cannot have been built from the tex as it currently stands, or
was built when those files were present and they have since moved. Either way the preview PDF
is not reproducible from the tree.

This is paper-side, not poster-side, so it does not block July 27. Recording it because
`L0_L1_phase_space_divergence.png` is named as if it were the central result figure and it
does not exist anywhere. If anyone reaches for it by name for the poster, they will not find
it.

## B5. Additional orphans confirmed with no producer

- `figures/mu_sweep_friction_invariant.html`, 5841 bytes, 2026-07-10 02:29. ORPHAN. Grep for
  the filename stem across `*.py` and `*.sh` in the live tree returns zero hits. The only
  mu-sweep code is `designsafe-staging/scripts/can_it_ford_mu_sweep.py`, which writes a CSV
  next to itself and does not write this HTML. The root copy is deliberately disabled, named
  `simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN`, 3258 bytes, 2026-07-10 23:56. This asset
  backs the friction-invariance claim at `README.md:72`, which the README itself says to
  treat with suspicion as the signature of a floating near-massless body. Low priority.
- `data/mu_sweep_results.csv`, 167 bytes, 2026-07-10 02:29, exists, but it is not read by any
  live script I could find.

## B6. Assets with a producer whose input is outside the repo

- `viability_audit_results.csv`, 1015 bytes, 2026-07-14 23:01. Produced by
  `analysis/viability_audit.py`, 1718 bytes, exists, writes at line 43. Its input, read live
  at line 10, is `glob.glob("particles_*.npz")` relative to the working directory. Those NPZ
  files exist at repo root, nine of them, 4.5 MB to 23 MB each, all mtime 2026-07-20 14:31.
  So the chain closes, but only if the script is run from the repo root. Not a figure, listed
  because it is the only audit artifact with a working chain.
- `analysis/gp_surrogate.py` writes `gp_regressor.joblib` and `gp_classifier.joblib` to an
  OUTDIR at lines 268 and 278. `analysis/gp_regressor.joblib` exists, 18427 bytes,
  2026-07-16 17:10. `gp_classifier.joblib` does NOT exist in `analysis/`. Produces no figure.
  Not a poster asset.
- `analysis/viability_dashboard_scaffold.py`, 10276 bytes, 2026-07-23 05:00, writes no image
  and reads no CSV path I could resolve. Its only file-shaped string is an error message at
  line 81 about timeseries predating `FloodHistory.to_csv`. It is a scaffold, not a producer.
  Not a poster asset.

## B7. Corrected count of what is actually poster-ready

After both passes, across every image in the repo:

- Complete chain, script exists AND data exists: **1** asset (A1), and its on-disk artifact
  is stale against both its generator and its input.
- Chain exists but reads superseded data: **2** (A3, A4).
- Producer exists but reads no data at all, values hardcoded: **2** (A5, A6), one of which
  (A6) is a synthesised curve presented as a solver trace.
- Producer exists, input lives outside the repo, output visually rejected: **1** (A7).
- ORPHAN, no producer anywhere: **13** files across A2, A8, A10, A11, A12, B5.
- BLOCKED on a rendered MPM video: **1** (A9).

## B8. Still unresolved after the second pass

Carrying forward items 1 through 5 from the first pass, unchanged, plus:

6. Cannot confirm what built `paper/conference_101719_preview.pdf`, given three of its five
   figure includes do not resolve today.
7. `L0_L1_phase_space_divergence.png` is referenced by name in the tex and exists nowhere.
   I could not determine whether it was deleted, renamed, or never created.
8. Did not attempt to settle the `poster_text_draft.md` author-list or affiliation
   `[CONFIRM]` blocks. Those need Kumar, not a grep.

---
---

# THIRD PASS, appended 2026-07-25 01:20 CDT

One asset appeared in the working tree at 00:43 tonight, after my second pass was written,
created by another pane. Adding it rather than leaving F5 to find it cold.

### C1. Traction bias figure, NEW tonight

- **asset name**: `figures/traction_bias.pdf`
- **what it shows**: two panels arguing a one-sided resolution bias, that every tested grid
  over-fills solidified volume and therefore understates traction. Left panel plots
  solidified volume against n_grid with a true-mesh reference line. Right panel is a friction
  coefficient sensitivity.
- **producing script**: `analysis/plot_traction_bias.py`, 4104 bytes, 2026-07-25 00:43.
  Exists. Output default read live from line 21, writes at line 87.
- **input data**: NONE. Read the script live. It has no `read_csv`, no `np.load`, no file
  open of any kind. Every value is a module-level literal at lines 10 to 18.
- **exists on disk now**: YES. `figures/traction_bias.pdf`, 117353 bytes, 2026-07-25 00:43,
  validated as a 1-page PDF v1.4. Both files are UNTRACKED in git.
- **verified or unverified**: UNVERIFIED, and I am flagging a specific numeric conflict
  rather than passing it through.
- **the one blocker**: the hardcoded volumes do not match the only measured volume table in
  the repo, and I cannot tell which is right.

  `analysis/plot_traction_bias.py:10-13` asserts, for n_grid 64 / 96 / 128, solidified volume
  0.842252 / 0.644214 / 0.506268 m3 against a true watertight mesh volume of 0.432718 m3,
  giving inflation factors 1.95 / 1.49 / 1.17.

  `docs/VERIFIED_FACTS_LEDGER_july24.md:248-255`, section A9, records for the same three
  grids solidified volumes 7.698 / 7.096 / 6.356 m3 against a trimesh hull truth of 3.5427
  m3, giving 2.17x / 2.00x / 1.79x.

  These disagree on every value, by roughly a factor of nine on volume and materially on the
  inflation ratios. I grepped the ledger for all seven of the script's literals and got zero
  hits, so the new numbers are not drawn from A9. They may be a fresh measurement on
  different geometry, in which case the ledger is the stale side; or they may be
  unsubstantiated. I could not resolve it read-only, and settling it means running the
  resolution probe, which the hard constraints forbid me.

  Relevant context F5 should carry: the ledger itself flags A9 as
  "**[FLAG] D7: not reproduced on this pass** ... the most load-bearing unverified block in
  this file", so this is a conflict between two unverified sources, not a new figure
  contradicting a verified one. Neither number should go on the poster until one of them is
  measured. Whoever owns this figure needs to state which mesh and which basis, bounding box
  or hull, its 0.432718 m3 refers to.

  One point in the figure's favour, checked live: its `MU_SENSITIVITY` values at line 17 are
  0.30, 0.40 and 0.55, which sit exactly on the physical friction band that `CLAUDE.md`
  records as 0.3 to 0.55 per Azhar et al. 2023. That part is consistent with project
  standing rules.

## Amendment to the B7 count

C1 adds one more row to the "producer exists but reads no data at all, values hardcoded"
bucket, taking it from 2 to 3 (A5, A6, C1). The single-complete-chain count is unchanged at
1 (A1).

## Note on tree churn during this audit

Three separate files changed under me while I worked, all by other panes:
`data/scenario_sweep.csv` at 22:57, `analysis/make_phase_space_v2.py` at 22:57, and
`scripts/gen_scenario_sweep.py` at 22:57, then `analysis/plot_traction_bias.py` and
`figures/traction_bias.pdf` newly created at 00:43. Every size and mtime in this handoff is
stamped to when I read it. F5 should re-stat anything it folds rather than trusting my
timestamps as current at fold-in time.
