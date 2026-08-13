# Render realism: real hull geometry and turbid-water optics

Supersedes `~/Downloads/d/README_flood_render_realism.md`. Render layer only: no
solver code, no force, no gate, no verdict changes. Everything below was verified
by running it against live repo assets on 2026-08-13, not carried from a summary.

## Files

| File | What it does |
|---|---|
| `analysis/vehicle_mesh_transform.py` | loads a hull `.ply` and registers it to the simulated rigid-body pose |
| `analysis/flood_water_optics.py` | suspended-sediment-driven beam attenuation and scatter colour |
| `analysis/make_hdri_cache.py` | regenerates the HDRI `.npy` cache from the `.exr` |
| `analysis/render_multigeom_shaded.py` | two new flags: `--ssc-preset` / `--ssc-mg-l`, and `--vehicle-mesh` |

Default behaviour is unchanged. With no new flags the render panels are
**bit-identical** to the pre-change output (max pixel difference 0.000e+00);
only the caption text differs, because it now states which optics mode ran.

## Running it

```bash
uv run --with numpy --with opencv-python-headless analysis/make_hdri_cache.py --exr assets/DaySkyHDRI002A_1K_HDR.exr --outdir /tmp/hdri
```

```bash
~/.venvs/canitford-mpm/bin/python analysis/render_multigeom_shaded.py --run render_s2/multigeom_2026-08-08/g64_yaris_regression --outdir /tmp/out --hdri-cache /tmp/hdri --frames 45 --exposure 1.85 --ssc-preset moderate_flood
```

Add `--vehicle-mesh vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`
for the real hull. Read the E8 section before you do.

## What was wrong with the attached modules

Four defects, each blocking or silently wrong. All measured, not inferred.

**1. The mesh loader could not read any mesh in this repository.** It parsed
ASCII `.ply` only. All four `.ply` files on disk are `binary_little_endian`.
Fixed by loading through trimesh; the ASCII reader is retained as a fallback and
now *raises* on binary instead of returning garbage.

**2. The placement recipe buried the car 0.67 m under the road.** Centring the
mesh on its vertex mean and applying `local @ R.T + com` put the hull at
`[-1.32, +1.23, -0.67] m` from the simulated body, with its underside 0.6726 m
*below* the floor plane. Two independent causes: the body frame is floor
referenced in z, not centroid referenced (`t[0]` sits 0.5948 m below
`scene0.mean(0)`), and the hull's long axis is on **body Y** while the `.ply`'s
long axis is on **mesh X**. The original claim of "centroid placement error 0.0"
held only against a synthetic symmetric stand-in.

The replacement *derives* the transform from the particle cloud rather than
assuming a convention, so it generalises to any hull. Verified on
`g64_yaris_regression`: yaw 90 deg, height-profile correlation **+0.9935**
against **+0.5847** for the 180-degree flip, extent residual 0.0870 m = 1.18
particle cells (the expected half-cell inflation, since the cloud is particle
*centres*), hull bottom landing +0.0012 m above the floor against the cloud's
+0.0000 m. It **refuses** a mesh that does not fit: the Yaris hull against the
Rogue run is rejected at 4.51 cells, against the Silverado at 15.05 cells.

**3. The water was ~45x too transparent.** The attached slope gave a green
attenuation of 0.35 1/m at 120 mg/L, a black-disc visual range of **13.6 m**,
i.e. floodwater clearer than a swimming pool. Two independent routes agree it
should be 7 to 29 1/m:

- *Clarity relationships.* Davies-Colley and Smith 2001 give `c * y_BD ~ 4.8`
  with the field relation `turbidity(NTU) * y_BD ~ 20 to 50 NTU.m`. At 120 mg/L
  that is `y_BD = 0.17 to 0.42 m`, `c = 11.5 to 28.8 1/m`, `c* = 0.096 to 0.24 m2/g`.
- *Geometric optics.* `c = 3*Q*SSC / (2*rho_s*d)`, `Q ~ 2`, `rho_s = 2650 kg/m3`.
  Silt at 5 to 50 um gives `c* = 0.023 to 0.226 m2/g`.

The two overlap on `c* ~ 0.1 m2/g`, now the default. It sits at the transparent
end of the band deliberately, so some depth cue survives.

**4. The colour mix used an invented constant and rendered grey, not brown.**
Mixing by `SSC / (SSC + 100)` gave a 0.545 fraction at 120 mg/L and produced a
neutral olive. The physically correct weight is the ratio of scattering
coefficients, `b_sediment / (b_sediment + b_water)`, which needs no fitted
constant. Sediment overwhelms molecular scattering immediately (f > 0.995 even
at 10 mg/L), so the scattered light is sediment-coloured as soon as there is
meaningful sediment, which is what muddy water actually looks like.

## Why this removes the 9x fudge rather than adding to it

`render_multigeom_shaded.py:91-92` used real clear-water absorption
`[0.45, 0.07, 0.03] 1/m` multiplied by `VIS_GAIN = 9.0`, honestly labelled as a
display choice. The gain existed because clear water over a 0.30 m tank loses
about 13 percent of the red and nothing else, so the depth cue was invisible.
The missing physics was sediment, not gain. Supplying it makes the exaggeration
unnecessary, and the two modes are **mutually exclusive by construction**:
multiplying a sourced coefficient by an unsourced 9x would be less defensible
than either alone. At `SSC = 0` the new model reproduces the old constants
exactly, so it is a strict generalisation.

## Citation corrections

Every reference was resolved against Crossref. Four defects in the source
material, one of them the classic fabrication pattern:

1. **Alexandrov et al. 2003 had a title that does not exist at its DOI.** The
   DOI, authors, year and journal were correct; the title belonged to a
   different 2007 *Geomorphology* paper. Correct title: "Suspended sediment
   concentration and its variation with water discharge in a dryland ephemeral
   channel, northern Negev, Israel", *J. Arid Environments* 53(1) 73-84.
2. **34,000 mg/L is a six-year MEAN, not a "physical upper bound".** The same
   abstract reports individual flood maxima of 21,000 to 229,000 mg/L, 6.7x
   higher. A mean cannot be a bound. Relabelled.
3. **Stewart/Fox/Harnett 2014 was cited for linearity and reports the
   opposite** — a power law, explicitly naming nonlinearity from particle
   shadowing and multiple scattering. The citation that *does* support a linear
   regime is Stewart and Fox **2017**, doi:10.1061/(ASCE)HY.1943-7900.0001343,
   about 90 percent of data linear, **valid for 9 to 90 um grain size and
   0 to 670 mg/L**. The code now carries that bound and warns when a preset
   exceeds it.
4. **The near-bed profile cited a source that cannot support it.** The Brisbane
   campaign (correct citation: Brown, Chanson, McIntosh and Madhani 2011,
   UQ Hydraulic Model Report CH83/11, 120 pp, eSpace UQ:243550) measured a
   **falling-stage temporal** trend, not a vertical profile, using one ADV at
   two non-simultaneous elevations confounded with stage; the authors themselves
   warn the trend "might be linked with the change in ADV sampling volume
   elevation". Reattributed to Rouse 1937, with the exponential kept as the
   constant-eddy-diffusivity solution whose length scale is the physical
   quantity `eps_s / w_s`.

Also corrected: Harnett's initial is **C. K.**, not C. T.; the 2013 item is
**conference proceedings**, not a journal article; Martinez's ~100 g/m3
saturation is stated for **blue through red only**; and the "661 citations"
figure is unverifiable (databases give 540 to 679), so it is gone.

A **normalisation bug** was also fixed: the near-bed boost decayed to 1.0, making
the preset the far-field value rather than the mean, so the column average came
out **+19.0 percent** above the named preset and silently broke the tie between
the presets and the measured concentrations they cite. It is now mean-preserving
to 1e-4.

## New preset, and an honest result about what a render can show

Added `urban_road_flood = 13000 mg/L`, the midpoint of the 6,000 to 20,000 mg/L
event-mean rise measured on an actually flooded urban road (Brown and Chanson
2012, doi:10.1029/2012WR012381). This is the closest published analogue to the
modelled scenario and it is **3 to 11x higher than the old "severe" preset**.

Which produces a result worth stating plainly: at any realistic flooded-street
concentration the water is **optically opaque over the 0.30 m tank**. Visual
range is 0.40 m at 120 mg/L and 4 mm at 13,000 mg/L. Only `clear_baseline` and
`moderate_flood` leave a visible depth gradient at this scene depth. So a render
that shows the submerged hull through the water is not showing something a
camera would see. That is a limitation of what any honest render can depict
here, not a defect in the model, and it is the reason some exaggeration was
wanted in the first place. The difference now is that the trade is explicit.

## E8, and the case for keeping marching cubes as the default

The attached README called the marching-cubes hull an unintended defect causing a
"blocky shape". That characterisation is wrong. Both render scripts document it
as deliberate, for reasons that still hold:

- The Rogue and Silverado `.ply` files **do not exist on this machine**. Only
  Yaris hulls do. So for two of the three multigeom vehicles a mesh swap is not
  available at all.
- It shows "the geometry the solver actually integrated, resolution loss
  included". Swapping in the source hull shows the geometry the solver was
  **built from**, not what it used. For a fidelity render that is the point; for
  a physics figure it is a misrepresentation.

Register E8 was read in full. Its operative rule is a **distribution** rule:
"do not commit any derived NCAC/CCSA geometry to the public repo, and do not
include it in a DesignSafe DOI". Nothing in E8 restricts reading, loading or
rendering, and E8 records the canonical Yaris hull's provenance as **explicitly
unresolved** between NHTSA-hosted (safe) and CCSA-hosted (licence-silent).

So `--vehicle-mesh` is available for internal review renders and is **off by
default**. When used, the in-frame caption and the manifest both state that the
frame contains derived NCAC/CCSA geometry and must not be published, so no
output of this path can be published by accident.

## Incidental fix

`render_multigeom_shaded.py`'s manifest claimed the free surface was smoothed at
"gaussian sigma=1 cell". The code computes `max(0.6, h / surf_cell)`, which is
0.60 to 0.82 for this batch and never 1.0, and the adjacent `surface_smoothing`
key already described it correctly, so the manifest contradicted itself. It now
reports the formula and the evaluated value (0.6000 for the Yaris run).

## Second pass: what adversarial verification changed

An adversarial verifier **refuted** one of my own claims, and it was right. I had
written that linear-in-SSC fails above 670 mg/L because of "particle shadowing
and multiple scattering". Both the premise and the mechanism were wrong:

- **Scattering dominance does not imply nonlinearity.** Under independent
  scattering `c = N<Q_ext pi r^2>`, so `c` is proportional to `N` for *any*
  split between scattering and absorption. Linearity is set by optical crowding,
  not by which process dominates.
- **These concentrations are mostly not crowded.** Particle volume fraction is
  `SSC/rho_s`: 2.53e-4 at 670 mg/L, **23.7x below** the ~6e-3 independent-
  scattering threshold, and 4.91e-3 (just under) at the 13,000 mg/L urban
  preset. I recomputed these independently and they match.
  One thing the verifier did not state and I did: **`extreme_bound` at 34,000
  mg/L reaches 1.28e-2 and genuinely IS crowded**, 2.1x past the threshold. So
  the crowding argument acquits every preset that matters and does *not* acquit
  that one. It is a context figure, not a render default.
- **The real driver of measured field sublinearity is a grain-size confound.**
  Since `c* ~ 3Q/(2 rho_s d)`, `c*` falls from 0.226 to 0.013 m2/g across
  d = 5 to 90 um, and high-SSC events carry coarser load, so `c*` drops as SSC
  rises. That produces apparent sublinearity with no optical mechanism at all.
- **Martinez's saturation is an apparent optical property, not an intrinsic
  one.** Reflectance saturates; Kd did not, and they fitted a linear model over
  5-620 g/m3 from 133 stations. So Martinez *supports* the linear form in range.

The bound is therefore an **empirical calibration range**, not a physical
threshold, and the module now says so. The guard stays, because the coefficient
must not be *quoted* as sourced outside its range.

**Render consequence: none.** At the bound, optical depth over 0.30 m is 20.1 and
transmittance is 1.8e-9. Even assuming a 3.3x over-prediction at 13,000 mg/L,
transmittance moves between 4e-170 and 2e-52, both far below one 8-bit level
(3.9e-3). Nobody should "fix" this as a rendering bug.

## Second pass: three more citation defects

1. **Schneider's initials are wrong and the paper disagrees with itself.** First
   author is **Ismael L. Schneider**, not "I. A. H. Schneider" (a different
   UFRGS researcher). Add 4(1):1271-1285. Its abstract says iron-oxide features
   at 470-580 and 650-850 nm; its own body text at p.1281 says 470-600 nm and a
   "concavity" at 850 nm. These are **absorption** features, measured on dried,
   sieved, organic-stripped **powder**, not a suspension.
2. **"Yang 2012" is Li and Yang 2012, and the DOI does not resolve.** Yang
   Shou-ye is the *second* author; Li Chao is first. It is a journal article
   (*Earth Science / J. China Univ. Geosciences* 37(S1), 11-19), not a thesis.
   The publisher's DOI `10.3799/dqkx.2012.S1.002` returns 404 at doi.org,
   Crossref and DataCite.
3. **The 565/505/435 nm figures are first-derivative peaks, not reflectance
   peaks** — the steepest points of the absorption edge. At a true reflectance
   maximum `dR/dlambda` is zero by definition. Read as reflectance maxima they
   predict yellow-green, green-cyan and **violet-blue**, so the argument "these
   are the peaks, therefore brown" points the wrong way. Goethite is yellow-brown
   *because* it absorbs at 435 nm. The module now explains the colour by the
   position of the absorption edge.

Also: **Bartolucci's depth finding is inverted in the source material.** The
paper says the bottom did *not* influence the response once water was **deeper
than** 30 cm; the attachment wrote "below 30 cm depth", the opposite. And its
"about 6 percent" is unit-ambiguous in the original, so it must not become an
RGB multiplier.

**The honest gap: no source in this set measures the colour of a sediment
suspension in a water column.** Two measure dried mineral powder (an upper bound
on suspension colour, not equal to it) and the third reports magnitude, not
colour. Cited honestly they support "iron oxides absorb short wavelengths and
reflect long ones, and turbid water is brighter than clear water in the red" —
consistent with a brown render, not a derivation of one.

## The attachments' preview figure should not be used

`flood_water_optics_preview.png` plots the **refuted** coefficients: its
transmittance curves are the ones implying 13.6 m visibility at 120 mg/L. It is
superseded.

It also carries a mislabel worth catching separately. Its dashed line reads
"0.30 m AR&R small-passenger still-water cap". The **number is right**
(`vehicle_params.py:209`, `small_passenger depth_m 0.30`, Shand et al. 2011
Table 3), but "still-water" is wrong: these are limits for a **stationary
vehicle subjected to flow**, which is the exact confusion CLAUDE.md L-1 warns
about. `vehicle_params.py:201-204` also records them as the report's own DRAFT
INTERIM figures, not an endorsed safety standard.

## Third pass: two bugs of mine, and E8 answered

**A live broadcasting bug that my own test masked.** `sediment_extinction_rgb`
multiplied a `(3,)` spectral vector by an `(N,)` concentration array. That raises
for every N except **1 and 3**, and at N = 1 or 3 it *silently* returned shape
`(3,)`, treating one concentration per colour channel instead of one per
particle. My array test passed a 3-element array, so it exercised exactly the
size that fails silently. Fixed with an explicit particle axis, and verified at
N = 1, 2, 3, 4, 100, 8905. Fixing it exposed a second instance of the same class
in `transmittance` (k is `(...,3)`, path is `(...)`); also fixed and tested.

**The regenerated HDRI sun was 1.10 deg off the shipped renders.** My first
version averaged the brightest 0.01% of pixels; the sun vector in the committed
`renders/multigeom_2026-08-12_render/*/render_manifest.json` came from a bare
argmax. 1.1 deg moves every GGX highlight, so regenerating the cache would have
silently failed to reproduce published frames. `make_hdri_cache.py` now defaults
to `--sun-mode argmax` and prints its angular separation from the shipped vector:
it now reads **0.0000 deg apart, OK**.

**"The Rogue and Silverado .ply files do not exist on this machine" is FALSE.**
Byte-identical copies of the exact hulls those runs used are at
`/Users/josie/Downloads/vehicle_meshes/`, outside the repo tree:

| file | sha256 | matches `00_provenance.txt` |
|---|---|---|
| `rogue_g96_pd8_coarse_watertight.ply` | `c0b778e2...06c310b2` | yes |
| `silverado_g96_pd8_coarse_watertight.ply` | `46fba11e...f7d466d7f9` | yes |

I had repeated this claim from `render_multigeom_rollout.py:116-118`. It is
corrected in `vehicle_mesh_transform.py`. The *rationale* for marching cubes
survives, and is the stronger half anyway: the reconstruction shows what the
solver integrated, the mesh shows what it was built from.

## E8: the open question is now answered, from the zips on disk

Register E8 records as "UNRESOLVED and load-bearing" whether the canonical Yaris
is NHTSA-hosted (safe to redistribute) or CCSA-hosted (licence-silent). The
original CCSA zips are in `vehicle_geometry_research/`, and `b0d2664f` explicitly
recommended opening them to check for an embedded licence. That had not been
done. It has now.

**It is CCSA-hosted.** Three independent confirmations:
- The zip's own banner: *"2010 Toyota Yaris Coarse Finite Element Model / Center
  for Collision Safety and Analysis / George Mason University"*.
- Size 11,228,299 bytes = 11.2 MB, matching CCSA's published figure for coarse
  v1l, and the `v1l` version string matches the canonical hull's filename.
- The embedded `README.md`: *"developed by Center for Collision Safety and
  Analysis researchers at George Mason University."*

**And the licence is NOT silent, contrary to what the research artifacts record.**
`289743f7` states "No terms-of-use, license, disclaimer, or copyright statement
exists on the CCSA model pages or in the validation PDF. (Absence confirmed by
inspection, not inferred.)" That is true of the *pages and the PDF* and false of
the *distributed zip*. The embedded README carries, verbatim:

> "The effort was sponsored by the Federal Highway Administration."
>
> "Users of the model must verify their own simulations. Neither CCSA or FHWA
> assume any responsibility for the validity, accuracy, or applicability of
> results obtained from this model."
>
> "We ask that the CCSA at GMU and the FHWA be acknowledged for any use of this
> FE model resulting in papers and publications."

So: a disclaimer plus an **attribution request**, with **no redistribution grant
and no redistribution prohibition** — the same shape as the historic NCAC release
statement. E8's conservative operative rule therefore still stands, but the path
to closing it is now concrete rather than open-ended:

1. **Acknowledge CCSA at GMU and FHWA** in the paper and poster. This is an
   explicit request from the model authors and currently is not being honoured.
2. **Written permission has named addressees**, from the same README: Dhafer
   Marzougui, Fadi Tahan and Steve Kan, with GMU emails and phone numbers.
3. FHWA sponsorship is worth citing in the request, though it does not by itself
   confer public-domain status: 17 U.S.C. 105 covers federal *employees*, and
   these are university contractors.

The Silverado and detailed-Yaris zips carry the identical CCSA/GMU banner and
terms, so the same treatment covers all of them.

**A possible escape hatch nobody has recorded.** CarCrashNet (MIT + Toyota
Research Institute, 2026, **CC BY 4.0**, github.com/Mohamedelrefaie/CarCrashNet)
re-derives Yaris and Silverado geometry in OpenRadioss/VTKHDF. A CC BY 4.0
geometry would carry clear redistribution rights and would dissolve E8 for
render purposes entirely. Unverified by me; worth one hour before assuming E8
blocks publication permanently.

## Renderer architecture: matplotlib is the root cause of D1

`hpc_render_stack_comparison.md:60` identifies why the vehicle was sliced in half:
`mplot3d` uses a **painter's-algorithm depth sort, not a real z-buffer**, so
incorrect occlusion between fluid particles and vehicle mesh is a known
limitation, not a bug in this script. The current fix (merging water and hull
into one `Poly3DCollection`) works but is a workaround for a renderer that cannot
do the job.

That report recommends **PyVista** (VTK-based, first-class conda-forge
`linux-aarch64` builds, EGL hardware off-screen in VTK 9.5 with no Xvfb) for
poster-quality output. It also **contradicts `b0d2664f`** on Blender: `b0d2664f`
claims "official ARM64 Linux builds", while blender.org publishes none and there
is no `linux-aarch64` `bpy` wheel. The project's own `mpm-render-pipeline` skill
already resolved this: *"Blender: no official Linux-aarch64 build, skip."* Treat
`b0d2664f`'s render-stack claims as unreliable; it self-flags its OSPRay claim
and is independently wrong on Blender.

Two smaller items from the same sweep, both unaddressed: the shader's
`WE_LO, WE_HI = 8.0, 60.0` is **not** from `b0d2664f` (that report gives no Weber
numbers), so it is currently unsourced; and the water colormap is `cm.Blues`
where Kumar's own GNS/CB-Geo work uses **viridis**.

## Still open

- `c* = 0.10 m2/g` is a central value from a derived band, not a measured
  quantity. Grain size, the dominant control, is not modelled. Brown and Chanson
  2012 report a median of about 25 um for the Brisbane flood, which would let
  someone pin this down for that scenario.
- `SEDIMENT_ALBEDO_RGB` is a chosen colour consistent with iron-oxide spectral
  behaviour, not a colorimetric conversion. A real conversion needs CIE
  colour-matching functions and an illuminant choice.
- The full-text regression coefficients in Stewart and Fox 2017 were not
  retrieved (paywalled). Their dimensionless attenuation number does not convert
  to a 1/m per mg/L slope without sediment density and particle size, so it will
  not drop straight into a shader constant.
- Whether the canonical Yaris hull is NHTSA- or CCSA-hosted, per E8. This gates
  publishing anything from the `--vehicle-mesh` path.
