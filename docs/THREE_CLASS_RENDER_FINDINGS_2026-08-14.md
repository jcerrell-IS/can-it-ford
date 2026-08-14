# Three-class render and margin figures: findings, 2026-08-14

Render and figure layer only. No solver, no gate, no verdict, no coupling code
was touched. Every run drawn or plotted here is **warpmpm**, not Genesis.

Every number below is tagged by how it was obtained: **[live]** measured or read
during this session, **[committed]** read from a committed file in this
repository, **[source]** read from a primary publication PDF. Nothing is quoted
from a summary.

---

## 1. The highest-leverage fix works, and here is the before and after

The prior session's own statement of the problem: *"The rogue-hull render
currently marching-cubes an isosurface from 9135 rigid particles, because the
render script never reads a .ply. That's why the car reads as an unrecognizable
blocky shape."*

**[live]** Rendered frame 45 of `g64_rogue` twice, identical in every other
respect (same camera, same optics preset, same exposure):

| | vehicle surface | faces | what it looks like |
|---|---|---|---|
| A | marching-cubes isosurface of the 9,135 simulated rigid particles | 239,956 | a blocky loaf; no wheel arches, no glass line |
| B | the real `rogue_g96_pd8_coarse_watertight.ply`, registered to the pose | 72,520 | a recognisable SUV with wheel arches, roofline and a windscreen rake |

Both frames are in `figures/three_class_2026-08-14/E8_HOLD_DO_NOT_COMMIT/`
(withheld, see section 6).

The `--vehicle-mesh` path already existed in
`analysis/render_multigeom_shaded.py`; what did not exist was any evidence it had
been run on the Rogue or the Silverado. The prior work verified the Yaris only.

**[live] Registration now verified for all three hulls**, using the derived-yaw
method that refuses anything past 2 particle cells:

| hull | yaw | height-profile corr | extent residual | in cells |
|---|---|---|---|---|
| `yaris_coarse_v1l_watertight.ply` | 90 deg | +0.9935 | 0.0870 m | 1.18 |
| `rogue_g96_pd8_coarse_watertight.ply` | 90 deg | +0.9920 | 0.0977 m | 1.20 |
| `silverado_g96_pd8_coarse_watertight.ply` | 90 deg | +0.9910 | 0.1207 m | 1.18 |

The Yaris row reproduces the prior session's published values exactly. The Rogue
and Silverado rows are new. All three land in the 1.18 to 1.20 cell band, which
is the expected half-cell inflation of a surface drawn over particle *centres*,
not an error.

**[live] Hull digests re-measured and checked against the run's own
`00_provenance.txt`:** Rogue `c0b778e2c443...06c310b2` and Silverado
`46fba11e77cd...f7d466d7f9` match character for character. The Yaris hull is
`b379fa4472c6...`; the multigeom provenance file predates the Yaris regression
run and does not list it, but that run's log names the same path and records
`hull_m3 = 3.542739` with `hull_ref_delta_pct = -5.9e-06`, so it is the same hull
to within 6e-06 percent. The hero script refuses to draw a hull whose digest does
not match.

---

## 2. A silent decimation failure, and why the fix had to be Open3D

**[live]** On this machine `trimesh 5.0.0`'s `simplify_quadric_decimation` raises
`ModuleNotFoundError: fast_simplification`. `vehicle_mesh_transform.decimate()`
caught that and returned the mesh unchanged, printing one line. So `--max-faces
9000` was silently a no-op and the full 655,308-face Yaris hull was being handed
to matplotlib.

The fix is not to install `fast_simplification`. Project mesh qualification
records that trimesh's decimator **breaks watertightness on this exact geometry
at every level from 320k to 10k faces**, producing 49 to 172 non-manifold edges,
while Open3D preserves it. **[live] re-verified rather than trusted**, on the
canonical Yaris hull with Open3D 0.19.0:

| target faces | watertight | euler_number | volume | vs source |
|---|---|---|---|---|
| source, 655,308 | True | -442 | 3.542739 m3 | - |
| 30,000 | True | -442 | 3.519367 m3 | -0.660 % |
| 9,000 | True | -442 | 3.467026 m3 | -2.137 % |

`decimate()` now tries Open3D first, reports which backend ran, and warns loudly
if it falls back to trimesh. `load_and_register()` now also reports
`volume_source_m3`, `volume_drawn_m3` and `volume_delta_pct`, and the figure
captions print them. That matters here specifically: displaced volume is the
physical quantity the whole three-class comparison rests on, so a hull that
quietly lost 2.1 percent of it in order to become drawable would misstate the
figure's own subject. At the 60,000-face cap actually used the losses are
**[live]** Yaris -0.358 %, Rogue -0.016 %, Silverado 0.000 % (below the cap,
untouched).

---

## 3. The three-class hero still

`analysis/render_three_class_hero.py`, one frame, three vehicles, real hulls,
same flood condition, common scale bar.

**[committed]** The physical setup that IS held fixed: 0.30 m nominal
still-water depth, 1.5 m/s surge, floor friction 0.55, same solver, same frame
index (45 of 90, t = 1.500 s).

**[committed]** The control it does **not** have, printed on the figure itself:

| | Yaris | Rogue | Silverado |
|---|---|---|---|
| mass | 1100.0 kg | 1609.0 kg | 2337.0 kg |
| mass source (from the run) | `vehicle_params.py mass_kg 1100.0`; also deck header line 28 | AR&R large_passenger class figure, `gates_both_scenarios.py:22` | AR&R large_4wd class figure, `gates_both_scenarios.py:23` |
| hull volume | 3.542739 m3 | 4.950341 m3 | 7.962083 m3 |
| solidified volume | 3.55138 m3 | 4.96017 m3 | 7.94366 m3 |
| realized density | 309.7 kg/m3 | 324.4 kg/m3 | 294.2 kg/m3 |
| n_grid | 64 | 64 | 64 |
| **dx** | **0.147215 m** | **0.163165 m** | **0.204186 m** |
| **depth/dx** | **2.038** | **1.839** | **1.469** |
| **water layers** | **4** | **4** | **3** |
| P-2 passthrough | 0.10668 **FAIL** | 0.09843 PASS | 0.08343 PASS |
| final \|disp\| | 0.65930 m | 0.68273 m | 0.32507 m |

Shared `n_grid` is not shared resolution, because `grid_lim` follows each hull's
extent. The panels are comparable in physical setup and **not** in numerical
resolution, and no resolution-sensitive quantity may be ranked across them. A
matched-dx set is Dispatch 5's experiment and did not exist when this was drawn.

**[live] Two hull volumes measured independently of any document**, by loading
the .ply and integrating: Rogue 4.950341 m3, Silverado 7.962083 m3. Both agree
with the dispatch's 4.9503 and 7.9621 to the digits given. Rogue face count 72,520,
which is the value named in the "not bit-reproducible" note (72520 against 72524).

### What the render honestly shows about water colour

**[live]** Decomposing the shader at the default camera (elev 30 deg, azim -62),
on a flat surface, sky sampled along the mirror direction:

| camera elevation | Fresnel F | share of the water's radiance that is REFLECTED SKY |
|---|---|---|
| 14 deg | 0.2657 | 66.5 % |
| 21 deg | 0.1269 | 45.0 % |
| **30 deg (default here)** | **0.0510** | **24.2 %** |
| 40 deg | 0.0261 | 14.4 % |

At a grazing camera most of the water's colour is sky, not sediment, even though
the Fresnel coefficient itself is small: the HDRI radiance along the mirror
direction is (1.180, 1.363, 1.428) against the sediment's diffuse return of
(0.340, 0.235, 0.130), about 4x brighter. This is physically right, it is what
real water does at a grazing angle, and it is also why the earlier drafts looked
washed out. Raising the camera to 30 degrees is a **camera choice**, changes no
physics, and is recorded here so nobody later reads the hue as a measurement.

**[live] The image is optically SATURATED above about 140 mg/L.** Over this
scene's 0.30 m column, the refracted path at elev 30 is 0.3946 m, and the
max-channel transmittance falls below one 8-bit level (1/255) at **SSC = 140.1
mg/L** (131.5 mg/L at elev 21). Consequence, verified by rendering: the
`moderate_flood` (120), `severe_flood` (1800) and `urban_road_flood` (13000)
presets produce the **identical** water pixel, (0.545, 0.515, 0.471) at elev 21.
So this figure cannot be said to "show" a particular SSC above that bound. The
preset was therefore chosen on provenance grounds alone: `urban_road_flood`, the
midpoint of the 6,000 to 20,000 mg/L event mean measured on an actually flooded
urban road next to Brisbane's CBD (Brown and Chanson 2012), which is the closest
published analogue to the modelled scenario.

---

## 4. The two quantitative figures, and a naming correction they had to make

### 4.1 The dispatch's series is mislabelled, and the label matters

The task text asks for *"margin_frames collapsing 11 -> 10 -> 4 across
g48/g64/g96 for m2337"*.

**[committed]** In `data/slide_verdict_fragility_2026-08-13.csv` the column
holding 11, 10, 4 is **`longest_joint_frames`**. The column named
**`margin_frames`** holds **8, 7, 1**, because `margin_frames =
longest_joint_frames - sustain_frames_required` and `sustain_frames_required` is
3. `analysis/slide_verdict_fragility.py` uses both names correctly in its own
docstring; the relabelling happened downstream of it. Both series are drawn and
labelled on the figure so the confusion cannot survive it.

### 4.2 What the margin figure shows, with a g128 point measured here

**[live]** g128 and an in-job g96 control were measured from `metrics.csv`
committed on `claude/rtfd-test-phase-1-4-569130` (read with `git show`,
read-only), using that branch-independent script's own `longest_joint_run()` and
`k_crit()` rather than re-implementations. **[live]** That branch is fully on
origin (local and `ls-remote` both `54aa8064054e69349bc9aebe49f3b598c23b5331`),
so this is not a one-disk dependency.

| n_grid | longest_joint | margin_frames | k_crit | headroom | provenance |
|---|---|---|---|---|---|
| 48 | 11 | 8 | 0.377222 | 2.651x | [committed] fragility CSV |
| 64 | 10 | 7 | 0.523419 | 1.911x | [committed] fragility CSV |
| 96 | 4 | 1 | 0.872069 | 1.147x | [committed] fragility CSV (Vista) |
| 96 control | 4 | 1 | 0.872055 | 1.147x | **[live]** LS6 in-job control |
| **128** | **3** | **0** | **0.975883** | **1.025x** | **[live]** LS6 |

**The g128 arm clears the SLIDE criterion by exactly the minimum.** Three
consecutive frames against three required. Remove one frame and the published
verdict changes.

**[live] A cross-venue control that cuts both ways.** The LS6 in-job g96 arm and
the committed Vista g96 row agree on `k_crit` to **-0.0017 %** (0.872055 against
0.8720691949434465) while their peak drift ratios differ by **-1.61 %** (1.71427
against 1.74225, and the frozen store's 1.80047 is -4.79 % away from the LS6
value). The mechanism is visible in the figure's lower panel: **[live]** the
critical 3-frame window sits at frames 5-7 (g96) and 6-8 (g128), moments after
the surge arrives and before the trajectories diverge, whereas peak drift occurs
at frame 71 (g96) and frame 48 (g128), long after. So on this arm the *margin* is
the reproducible quantity and the *peak* is not, which is the opposite of how
they are usually quoted. This is one arm, on two venues; it is not a general
claim about the metric.

### 4.3 A verdict flips while both thresholds are still exceeded

**[committed]** `data/rogue_silverado_slide_classification_2026-08-13.csv`,
Silverado hull at 2270 kg:

| n_grid | peak drift / 0.05 m | peak speed / 0.05 m/s | onset frame | mode |
|---|---|---|---|---|
| 64 | 6.9669 | 15.427 | 3 | SLIDE |
| 96 | 1.8105 | 7.203 | 5 | SLIDE |
| **128** | **1.5557** | **4.087** | **-1** | **STUCK** |

At g128 **both** ratios are still above 1 and the classified mode is still
STUCK. Nothing fell below a threshold. **[committed]**
`simulation/failure_modes.py:181-183` requires `|drift| >= 0.05 m` **AND**
`|speed| >= 0.05 m/s` **simultaneously for 3 consecutive frames**; at g128 no
such window exists, `onset_frame_slide` is -1, and `triggered_slide` is False.
This is CLAUDE.md item 12(a)'s general warning (triggered_* is the verdict,
ratio_* is a peak magnitude) caught in the act on a real verdict.

### 4.4 The two figures are two different vehicles, and must not be merged

**[committed]** From `data/all_runs_inventory.csv`: `g48/g64/g96_m2337` all
record `hull_m3 = 3.542739`, i.e. the **canonical Yaris hull** carrying an AR&R
`large_4wd` **class mass** of 2337 kg, realized densities 642.8 / 658.1 / 663.6
kg/m3. That is not a Silverado. The Silverado figure is the real Silverado hull,
7.9621 m3, at 2270 kg. The two agree in direction and are not one series.

---

## 5. Optics: what was retrieved from full text, and what is still chosen

### 5.1 First, two of the task's three gaps had already been closed

The task text lists three admissions in `flood_water_optics.py`. **[live]** Two
of them describe a state the file is no longer in:

- *"the attenuation-coefficient-per-mg/L slope is TUNED for visual
  plausibility"*. Superseded. Commit `1d78d06` records: *"the 'tuned for visual
  plausibility' slope was refuted, not carried forward."* The current file
  derives a band from two independent routes and states that the point chosen
  within that band is a choice. That is a materially stronger position than
  "tuned", and conflating them would understate the file.
- *"`floor_boost` encodes the DIRECTION of the Brisbane finding but not its
  magnitude"*. **[live]** `floor_boost` does not exist anywhere in `analysis/` or
  `docs/`; a `/usr/bin/grep` returns zero hits. The near-bed treatment is now
  `near_bed_ssc()` with `VERTICAL_PROFILE_BASIS` attributed to Rouse 1937, and
  the module's own docstring records why the Brisbane attribution was withdrawn:
  that campaign measured a falling-stage **temporal** trend with one ADV at two
  non-simultaneous elevations, not a vertical profile.

The third, the sediment RGB, stands exactly as written: `SEDIMENT_ALBEDO_RGB`
is a qualitative colour consistent with the cited iron-oxide behaviour and is
**not** a colorimetric conversion. Nothing retrieved this session changes that,
and the module's own `REFERENCES["colour_gap"]` already states the reason: no
source in the set measures the colour of a sediment suspension in a water
column, which is what a fluid shader needs.

### 5.2 What was retrieved

| source | outcome | what it gave |
|---|---|---|
| **Guillen, Palanques, Puig, Durrieu de Madron, Nyffeler 2000**, Sci. Mar. 64(4) 427-435, doi:10.3989/scimar.2000.64n4427 | **RETRIEVED IN FULL** [source] | The primary citation for ROUTE B, which this module previously stated with no source; measured slopes; and the grain-size scaling |
| Stewart and Fox 2017, doi:10.1061/(ASCE)HY.1943-7900.0001343 | **NOT RETRIEVED** | Scite returns `contentDenied`, `oaStatus: closed`, no full-text excerpts; only access route offered is purchase |
| Stewart, Fox and Harnett 2013 / 2014 | not retrieved this session | already cited in the module with their correct roles (2013 supports decay with path length; 2014 reports the power law and is cited as the bound on linearity, not support for it) |
| Undermind connector | **UNAVAILABLE** | token expired mid-session; reported, not worked around |

Retrieval route worth recording: `WebFetch` failed on the publisher with
`unable to verify the first certificate`, twice, on both the DOI redirect and the
article page. `curl` on the same host succeeded (HTTP 200, `application/pdf`,
466,289 bytes, sha256 `98f0f082cd64...`), then `pdftotext -layout`. The paper is
diamond open access, CC-BY.

**[source] What Guillen et al. 2000 actually says**, read from the PDF:

- Their eq. 4: `SSC = (2 rho_s D / 3Q) alpha_p = B alpha_p`, after Spinrad et al.
  1983. This is exactly this module's ROUTE B, inverted, with `c* = 1/B`.
- Their eq. 5: `B = k D`, with `k` from 1.12 to 3.4 across laboratory grain-size
  fractions (Moody et al. 1987; Wiberg et al. 1994).
- Measured: BAC 0.4 to 14 1/m over six western-Mediterranean campaigns;
  per-campaign slope `B` 1.32 to 1.71 g/m2; pooled fit
  `SSC = 1.43 alpha_(p+w) - 0.26`, r2 = 0.85, stated as representative of shelf
  and slope areas that *"usually have suspended sediment concentrations lower
  than 5 mg/l"*. Their separate FTU calibration spans 0.1 to 700 mg/L with
  slopes 0.24 to 1.71.

### 5.3 Why the coefficient still cannot be upgraded

**[live]** Converting the retrieved numbers to `c* = 1/B`:

| route | c* (m2/g) | vs the module's 0.10 |
|---|---|---|
| pooled field fit, B = 1.43 | 0.699 | **7.0x above** |
| per-campaign range, B = 1.32 to 1.71 | 0.585 to 0.758 | 5.9 to 7.6x above |
| eq. 5 at 25 um (Brown and Chanson's measured median grain size for the flooded Brisbane road), k = 1.12 to 3.4 | 0.012 to 0.036 | **2.8 to 8.5x below** |
| eq. 4 direct, rho_s 2650 kg/m3, Q = 2, D = 25 um | 0.045 | 2.2x below |
| eq. 5 at 5 um, k = 1.12 to 3.4 | 0.059 to 0.179 | brackets it |

The retrieved evidence **brackets** the chosen 0.10 from both sides across a
factor of about 60, and the spread is explained rather than contradictory:
`c* ~ 1/D`, their water is marine shelf water usually under 5 mg/L carrying fine
river sediment, and a flood carries a coarser load. So **0.10 m2/g remains a
CHOSEN central value and is still labelled as one.** Quoting either retrieved
endpoint as "the published value" would be less defensible than the choice.

**[live] Unit check, independently confirmed with Wolfram:**
`2 * 2650 kg/m3 * 25 um / (3 * 2) = 22.08 g/m2`, dimensions
`[mass][length]^-2`, which is `SSC (g/m3) / alpha (1/m)` as required, so `c* =
1/B` is dimensionally sound.

**[live] Scope of the open question.** Because the render saturates above about
140 mg/L, every `c*` in the 60x span above produces the identical image at the
`severe_flood` and `urban_road_flood` presets. The coefficient only moves pixels
at `clear_baseline`, and at `moderate_flood` for the lower values. The open
question is real for a citation and nearly irrelevant for this figure.

The only change made to `analysis/flood_water_optics.py` is documentation: a new
`REFERENCES["geometric_optics_route"]` entry and a comment block recording the
bracket. **[live]** No coefficient changed and the shader output is unchanged
(`optics_from_ssc(120)` still returns k = (12.4, 12.1, 12.0) 1/m).

---

## 6. FLAG: register E8 blocks publishing the hero still

Raised under operating-protocol flag 4, a project standing hard rule.

**[committed]** Register E8's operative rule: *"do not commit any derived
NCAC/CCSA geometry to the public repo, and do not include it in a DesignSafe
DOI, without written permission or a confirmed licence."* **[committed]** Commit
`1d78d06`, 2026-08-13, re-checked this from the source zips: they carry an
embedded README, a CCSA GMU banner, a warranty disclaimer and an attribution
request, and **no redistribution grant**, so *"E8 is OPEN and a real-mesh render
may NOT go in a public deliverable."* And this GitHub repository is **public**.

**Consequence, and it is a partial non-delivery of the stated Definition of
Done.** The three-class hero still and the Rogue before/after pair exist, are
finished, and are **not committed**. They are in
`figures/three_class_2026-08-14/E8_HOLD_DO_NOT_COMMIT/`, which carries its own
`.gitignore` ignoring everything but itself, so the block is mechanical as well
as documentary. The two quantitative figures contain no hull geometry and are
committed normally.

To release the hero: close E8 with a written licence or permission, delete that
`.gitignore` (rather than force-adding around it, so the change shows in
history), and commit the images.

---

## 7. Poster-grade or diagnostic-only: an explicit answer

Nobody had assessed this. The answer differs by figure.

**The two quantitative figures are poster-grade now.** Self-contained, every
value traceable to a committed file or a stated live measurement, honest caption
blocks, no hull geometry so no E8 block. `fig_silverado_verdict_flip.png` is the
stronger of the two for a poster: one panel, one counter-intuitive result, and
the mechanism is legible without the reader knowing the codebase.

**The three-class hero is NOT poster-grade yet.** It is a good internal review
still and it is the first time these three have been in one frame. Four things
stand between it and a poster, in order of severity:

1. **E8.** Unpublishable at all until the licence question closes. This dominates
   the other three.
2. **The panels are not at matched dx.** The figure's caption says so, but a
   poster reader will still read three panels side by side as one comparison.
   Dispatch 5's matched-dx set fixes this and re-rendering is cheap.
3. **The renderer is matplotlib.** `docs/RENDER_REALISM_2026-08-13.md` already
   records matplotlib's painter-order limitation as the root cause of the v1
   "sliced car" defect, worked around by merging water and hull into one
   collection. That workaround holds only because the hull footprint is cut out
   of the water sheet, which leaves a visible notch beside each vehicle. A real
   renderer removes the constraint instead of managing it.
4. **The water reads as a flat sheet.** The free surface is a per-column max-z
   reconstruction with no spray, no bow wave geometry and no wake; foam is a
   post-hoc Weber-number diagnostic, **[live]** 2.0 percent mean foam fraction
   over wet cells on the Rogue frame. That is honest and it is also visually
   thin.

None of 2 to 4 is a physics defect. They are all render-layer, and 1 is not a
render problem at all.

---

## 8. Requests to files this thread does not own

- **`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`** (Dispatch 4 owns it).
  Two candidates from this session, neither written by me:
  (a) the `longest_joint_frames` / `margin_frames` naming correction in 4.1, and
  (b) the g128 margin-zero result in 4.2, if the register carries the J15/J16
  line at all.
- **`analysis/slide_verdict_fragility.py`** is unowned by this thread's scope and
  was **not** modified. Its `BASE` path is hard-coded to Vista
  (`/work/11603/jcerrell0629/vista/render_s2`), so it cannot be re-run on the Mac
  or against the g128 set; `analysis/make_resolution_margin_figures.py` imports
  its two metric functions instead of copying them, which is the safe half of a
  fix, not the fix.

---

## 9. Reproducing everything here

```bash
# venv (no Mac system python has numpy)
uv venv venv --python 3.12 && VIRTUAL_ENV=$PWD/venv uv pip install \
    numpy scipy matplotlib scikit-image trimesh open3d

# HDRI cache; prints "0.0000 deg apart  OK" against the shipped 2026-08-12 sun
uv run --with numpy --with opencv-python-headless analysis/make_hdri_cache.py \
    --exr assets/DaySkyHDRI002A_1K_HDR.exr --outdir <cache>

# the two committed figures
venv/bin/python analysis/make_resolution_margin_figures.py \
    --outdir figures/three_class_2026-08-14 --tmpdir <scratch>

# the hero still, E8: output must not be committed
venv/bin/python analysis/render_three_class_hero.py \
    --runs-root <...>/render_s2/multigeom_2026-08-08 \
    --rogue-ply <...>/rogue_g96_pd8_coarse_watertight.ply \
    --silverado-ply <...>/silverado_g96_pd8_coarse_watertight.ply \
    --hdri-cache <cache> --outdir <E8 hold dir> --frame 45 \
    --ssc-preset urban_road_flood
```

The run data read is `render_s2/multigeom_2026-08-08/{g64_yaris_regression,
g64_rogue,g64_silverado}`, which lives in the main checkout and is gitignored;
it was read, never written.
