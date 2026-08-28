---
title: Can It Ford
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.24.0
app_file: app.py
pinned: false
header: mini
license: bsd-3-clause
short_description: Can a car cross a flooded road? MPM verdicts and the spread
thumbnail: https://huggingface.co/spaces/josiecerrell/can-it-ford/resolve/main/assets/thumbnail.png
tags:
  - flood
  - vehicle-stability
  - material-point-method
  - computational-fluid-dynamics
  - civil-engineering
  - gaussian-splatting
---

# Can It Ford?

**Vehicle stability in floodwater: the spread, and where the verdict flips.**

> This is not a safety tool. The stability criteria used here are the source report's
> own draft interim figures for stationary vehicles, not an endorsed safety standard.
> Nothing on this site should be used to decide whether to drive into floodwater.
> Turn around, don't drown.

## What this project evaluates, stated exactly

> This work evaluates whether a specific vehicle would remain stable if subjected to floodwater of a given depth and velocity, which is the condition a vehicle enters the moment a crossing attempt fails. The published stability criteria used for validation (Shand et al. 2011; Smith, Modra and Felder 2019) were derived exclusively from stationary vehicles restrained in flow, and no depth-velocity curve in that literature was derived for a vehicle driving under its own power. The verdict reported here is therefore a necessary condition for safe crossing rather than a sufficient one.

The published literature reports thresholds and single points. This Space shows two
things that a threshold hides:

1. **the spread**, so a result reads as an ensemble rather than a point;
2. **where a verdict flips** as a deciding threshold is moved, so a reader can see which
   results depend on a choice rather than on a measurement.

## The tabs

| tab | what it shows | data state |
|---|---|---|
| AR&R verdict calculator | the stationary-vehicle joint rule over depth, velocity and the D x V product | live, arithmetic |
| Where the verdict flips | peak surge drift for each gated run against a movable distance threshold | live, 17 runs |
| Load surface, `v_car` x `v_water` | vehicle speed and flow speed as **separate** axes, where the field usually collapses them into one relative speed | live, 368 records, 20 cells at five seeds |
| Repeat spread | two independent draws of the same configuration | live, 3 configurations |
| Validated hull (warpmpm) | the canonical Yaris hull all 17 gated runs actually loaded | live, interactive 3D |
| Reconstruction (Gaussian splat) | the drainA scene, the input end of the pipeline | live, 350k-Gaussian preview |
| Precedent & Novelty | what is prior work, what is not mine, and what is | live |
| My contribution | three items, each with the caveat that makes it survive a check | live |
| Limitations | stated as strongly as the results | live |

### The load surface panel shows three spreads, because they are not the same size

| spread | what varies | size | is it an error bar? |
|---|---|---|---|
| seed | five seeds, one cell | 0.066 to 0.338 % | yes, and it is tiny |
| split | how one \|v_rel\| divides into `v_car` and `v_water` | 76 to 128 % | **no, this is the result** |
| window | measurement window f20-60 against f250-400 | -68.9 to +83.9 % | no, the load is still changing |

A page that drew error bars from seed scatter alone would show almost nothing
and would imply the other two spreads did not exist. The vehicle in this panel
is **prescribed, not free**, so no FORD or NO-FORD verdict follows from it.

Full dataset and card:
[josiecerrell/can-it-ford-speed-surface](https://huggingface.co/datasets/josiecerrell/can-it-ford-speed-surface)

## Engine

The gated runs use **warpmpm**, a material point method solver, via
`renders/yaris_render_s1/sim_standing.py`.

**They are not Genesis.** Genesis was an earlier box-proxy path that never loaded the
vehicle hull. An earlier version of this page labelled the physics level with the
Genesis engine name; that was wrong and is corrected here.

## Geometry on this page

**Vehicle mesh:** NCAC/CCSA 2010 Toyota Yaris coarse FE deck, DOI
[10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D). The PLY served here is a derived
surface reconstruction rather than the FE deck itself, and its sha256 is
`b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95`.

**Reconstruction:** drainA scene, trained with `gsplat` to 30,000 iterations, merged
from three rank shards (399,491 + 374,677 + 373,526) to **1,147,694 Gaussians**.
Validation at step 29,999: PSNR 22.74, SSIM 0.825, LPIPS 0.311.

The viewer loads a **decimated preview, not the full reconstruction.** The merged
artifact is 258.3 MB, which no browser should be asked to fetch and parse. The preview
keeps **350,000 Gaussians**, chosen by opacity times footprint after discarding the
233,999 whose opacity falls below 0.1, and carries spherical-harmonic degree 0 only.
Its bounding box is identical to the full artifact's on all six bounds, so it is a
thinned scene rather than a cropped one. It is built by
`analysis/build_splat_preview.py`; the full file remains the artifact of record.

## Attribution

The **physically viable world model** and **query-conditioned world model** framing
that situates this project belongs to Thorpe et al.,
[arXiv:2605.30542](https://arxiv.org/abs/2605.30542), co-authored by Hassan Iqbal and
Cheng-Hsi Hsiao at GeoElements. The closest prior full pipeline is Low, Hsiao, Li,
Thorpe, Topcu and Kumar, [arXiv:2607.00673](https://arxiv.org/abs/2607.00673). The
contribution claimed here is the applied pipeline and the external validation step,
not the framework. See the Precedent & Novelty tab.

## Corrections to previous versions of this page

Recorded rather than quietly removed.

1. The physics engine was labelled with the **Genesis** engine name. The gated runs
   are warpmpm. Corrected above.
2. **"a corrected density of rho = 115.7, giving the roughly 1390 kg target mass used
   across the project."** Neither figure is canonical. The canonical vehicle mass is
   **1100 kg**, and the canonical hull effective density is **310.494 kg/m^3**. The 115.7
   value belongs to a superseded box-proxy path, and the 1390 kg box comes from a sweep
   the project marks deprecated and instructs not to source figures from.
3. **"L2 is being rebuilt and has not produced a published verdict."** Stale. Seventeen
   gated runs exist with classified outcomes. What remains true, and is stated in the app,
   is that none of the gates is a physics validation.
4. **"live, 348 records"** on the load-surface panel. The manifest's own `records` key is
   **368**, and `load_surface.csv` carries 368 data rows. Corrected in the table above.

## Limitations, stated as strongly as the results

- **Resolution is not converged.** The water column is resolved by roughly 2 grid cells
  and 4 particle layers, against a rule of thumb of about 10 particles per flow depth.
  Displacement magnitude is non-monotone under grid refinement, so cite the verdict and
  never the magnitude.
- **Coarse resolution usually over-predicts peak hydrodynamic force**, which makes
  over-threshold verdicts conservative for safety. That does not make them converged.
- **No gate is a physics validation.** The gates are self-consistency and numerical
  containment checks. Several compare against a reference derived from the same pipeline,
  so they cannot fail for a reason external to the code.
- **`sustain_frames = 3` has no published source.** No vehicle-stability criterion
  reviewed for this project uses a persistence count at all, yet it gates every verdict.
- **The load-surface vehicle is prescribed, not free.** The body is held on a path and
  the reaction load is measured. It cannot be swept away.
  **No FORD or NO-FORD verdict is derivable from it.**
- **The scenario is a stationary vehicle in flow**, which matches the validated stability
  criterion. The word "ford" implies motion; it is the title that mismatches, not the
  setup.
- **1609 kg and 2337 kg are AR&R class figures, not vehicle measurements.** The full
  statement, including why the Silverado is not the Dodge Ram 1500 and why 2270P is not
  2270.0 kg, is on the Limitations tab.
- **Rogue: companion geometry, stale-flagged, plotted nowhere on this page.** An earlier
  version of this page said the Rogue "has no NCAC or CCSA finite-element provenance."
  That was wrong and is withdrawn: register E6a records a CCSA model, VIN
  5N1AT2MT6LC742896, v3 August 2024, 3,240,729 elements. What it lacks is a deck-header
  mass, so its 1571.3 kg is web-sourced rather than deck-derived. Its runs are
  non-canonical, and a 2026-08-25 roll result was withdrawn as a hull artifact on
  2026-08-26 (roll 0.1 sigma once the hull is isolated at fixed `n_grid` 96).

## Programmatic access

The AR&R calculator is exposed as a single MCP tool endpoint, `/arr_verdict`. Every other
event on this page is `api_visibility="private"`. **The endpoint has no built-in rate
limiting** and this Space is public.

## Running locally

```
pip install -r requirements.txt
python app.py
```

Regenerate `data/` from the canonical repository with:

```
python3 analysis/hf_dataset_publish.py --out hf_space/data
```

Test the logic without a browser:

```
python3 hf_space/surface.py
```

## About

**Josie Cerrell**, NSF SCIPE REU 2026, GeoElements Lab, UT Austin. PI Krishna Kumar.
