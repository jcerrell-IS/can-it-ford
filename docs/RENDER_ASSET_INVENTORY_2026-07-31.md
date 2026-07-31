# Render Asset Inventory

Every PNG under `renders/yaris_render_s1/` at maxdepth 2, reconciled against what
`overleaf/main` actually ships as Figure 7. Produced under `directory-provenance-audit`:
the question is which copy is real, and the only trustworthy signal is content identity
against the shipped blob, not mtime and not file size.

Read live 2026-07-30. No file was moved, renamed, edited, or swapped.

## Headline

**pyvista was never required.** A prior session recorded Tier 5 as blocked on a missing
`pyvista` import. Finished PNGs already existed on disk, rendered on a machine that had it.
The blocker was real (`ModuleNotFoundError: No module named 'pyvista'` on all five local
interpreters, re-confirmed today) but it was blocking a re-render nobody needed.

## What overleaf/main ships

| Field | Value |
|---|---|
| Path | `l2_render_g64_m1100_f0045.png` |
| Bytes | 580782 |
| Dimensions | 1541 x 664 |
| md5 | `688281d14e3c394de9bd8cac252541c9` |
| `file` | PNG image data, 1541 x 664, 8-bit/color RGB, non-interlaced |
| Identical to | `renders/yaris_render_s1/frame_check_f0045_poster_crop_no_artifact.png`, byte for byte |

The shipped bytes are md5-identical to a local poster crop. No script in the repository
writes either filename, and `.gitignore` line 14 (`renders/`) keeps the local source out of
the public repo.

## Figure 7 candidates

`bpp` is bytes per pixel. It is the discriminator for blank renders, and it is **not** a
discriminator for water presence. See the two warnings below the table.

| File | mtime | Bytes | Dimensions | bpp | md5 | Verdict |
|---|---|---|---|---|---|---|
| `frame_check_f0045_poster_crop_no_artifact.png` | 2026-07-29 23:36 | 580782 | 1541x664 | 0.568 | `688281d1…` | **SHIPPED. Water present, header legible, colorbar labelled** |
| `frame_check_f0045_poster_crop.png` | 2026-07-29 23:36 | 601101 | 1541x686 | 0.616 | `f8f2eedb…` | Superseded by the `_no_artifact` crop, 22 px taller, retains the artifact band |
| `frame_check_f0045.png` | 2026-07-26 03:36 | 951337 | 1600x912 | 0.669 | `1b029825…` | Uncropped parent. Usable but wastes vertical space |
| `hero_g64_m1100_f45_7168.png` | 2026-07-30 17:34 | 13264788 | 7168x4032 | 0.459 | `63ca30b5…` | Water present. **Oversized** (3.4x the bloat threshold); header and colorbar ticks illegible at column width |
| `probe_7168x4032.png` | 2026-07-30 17:30 | 13264788 | 7168x4032 | 0.459 | `63ca30b5…` | **Byte-identical duplicate** of the hero 7168. Same md5 |
| `hero_g64_m1100_f45_4K_2026-07-30.png` | 2026-07-30 16:59 | 4486577 | 3840x2160 | 0.541 | `2f62eea1…` | Water present. Oversized |
| `hero_g64_m1100_f45_max.png` | 2026-07-30 17:17 | 439770 | 16384x9216 | **0.00291** | `ee743883…` | **FAILED RENDER, blank.** Do not use |
| `hero_probe.png` | 2026-07-26 01:40 | 986818 | 1600x900 | 0.685 | `8a1c793b…` | **WATER-FREE render failure.** Confirmed visually. Do not use |
| `realistic_g64_m1100_f0045.png` | 2026-07-25 21:23 | 220068 | 1400x910 | 0.173 | `f8ceefb9…` | Earlier styling pass, superseded |
| `realistic_A4_g64_m1100_f0045.png` | 2026-07-25 22:00 | 220238 | 1400x910 | 0.173 | `4fedbf2b…` | Earlier styling pass, superseded |

### The GL resolution ceiling

| Probe | Dimensions | Bytes | bpp |
|---|---|---|---|
| `probe_3200x1800.png` | 3200x1800 | 3347129 | 0.581 |
| `probe_4096x2304.png` | 4096x2304 | 4731595 | 0.502 |
| `probe_6144x3456.png` | 6144x3456 | 10040662 | 0.473 |
| `probe_6656x3744.png` | 6656x3744 | 11586961 | 0.465 |
| `probe_7168x4032.png` | 7168x4032 | 13264788 | 0.459 |
| `probe_7680x4320.png` | 7680x4320 | 96682 | **0.00291** |
| `probe_7936x4464.png` | 7936x4464 | 103232 | **0.00291** |
| `probe_8192x4608.png` | 8192x4608 | 109996 | **0.00291** |

**7168 x 4032 is the maximum working render resolution on this machine.** Everything above
it collapses to exactly 0.00291 bpp, and `hero_g64_m1100_f45_max.png` at 16384 x 9216 shares
that identical constant. Three independent failures landing on the same bpp to three
significant figures is a uniform fill, not a coincidence. Any "max resolution" asset is
blank.

### Two warnings about file size

1. **Size does not prove water.** `hero_probe.png` is a confirmed water-free failure at
   **0.685 bpp**, which is *higher* than the correct shipped render at 0.568 bpp. It carries
   an identical burn-in header, identical camera, identical vehicle and road, and a rendered
   colorbar, with the water isosurface entirely absent. Only visual inspection separates it
   from a good frame.
2. **Size does prove blankness.** The 0.00291 constant is reliable in the other direction.

## Burn-in header cross-check

Header text, read from `_hdr_crop.png` (3400 x 230, `aaf6964b…`):

```
Can It Ford  L2 coupled MPM   Yaris hull, 1100 kg
t =  1.50 s                          d =  65.94 cm    yaw = -1.74 deg
realized depth 0.2944 m (4 layers)   surge 1.5 m/s   DxV 0.4416 m2/s   n_grid 64
```

Against `_incoming/g64_m1100/summary.json` and `metrics.csv` (91 rows, t = 0.0000 to 3.0000):

| Burn-in | Source value | Agrees |
|---|---|---|
| Yaris hull, 1100 kg | `summary.json: mass_kg = 1100.0` | yes |
| surge 1.5 m/s | `velocity_ms = 1.5` | yes |
| n_grid 64 | `n_grid = 64` | yes |
| realized depth 0.2944 m (4 layers) | `water_layers = 4`, `h = 0.07360736`; 4h = 0.294429 m | yes, derived not stored |
| DxV 0.4416 m2/s | 0.294429 x 1.5 = 0.441644 | yes, uses **realized** depth, not the requested 0.30 |
| requested depth | `depth_m = 0.3` | consistent with the paper's "requested 0.30, realized 0.2944" |
| t = 1.50 s | `metrics.csv` row 45, t = 1.5000 | yes |
| d = 65.94 cm | `metrics.csv` row **46**, dmag = 65.94 cm | **off by one row** |
| yaw = -1.74 deg | `metrics.csv` row **46**, yaw = -1.7419 deg | **off by one row** |

### The off-by-one

Row 45 is t = 1.5000 s, dmag 65.68 cm, yaw -1.7199 deg. Row 46 is t = 1.5333 s, dmag
65.94 cm, yaw -1.7419 deg. The header's `d` and `yaw` both match row 46 exactly and
simultaneously; two independent variables agreeing rules out coincidence. The header prints
its timestamp from the frame index but reads its physics from the next row, a 33.3 ms
offset.

Magnitude: 0.26 cm on 65.9 cm, or **0.4 percent**. It changes no claim in the paper and is
recorded for completeness, not as a defect requiring action.

### Which frame, and is the printed displacement final?

| Quantity | Value |
|---|---|
| Frame shown | 45 of 90, t = 1.50 s |
| dmag at frame 45 | 0.656805 m |
| dmag printed in burn-in | 0.6594 m (row 46) |
| **Peak** dmag | 0.665667 m at t = 2.1667 s, row 65 |
| **Final** dmag | 0.658537 m at t = 3.0000 s |
| Frame 45 as a fraction of final | **99.7 percent** |

`summary.json: final_disp_mag_m = 0.6585370302200317` matches the `metrics.csv` final row
exactly, an independent cross-check that the two files describe the same run.

The printed 65.94 cm is the **in-frame** value, not the final and not the peak. The paper's
caption states exactly this, so the caption is correct as written. Worth noting for context:
the run has essentially finished sliding by t = 1.5 s, and the peak exceeds frame 45 by only
1.3 percent, so "mid-run" is accurate but the frame is not visually unrepresentative.

## Sizing against IEEE two-column

Single column is roughly 3.4 in. At 300 dpi that needs about 1050 px. Past roughly 2100 px
is bloat.

| File | Width px | dpi at 3.4 in | Status |
|---|---|---|---|
| `frame_check_f0045_poster_crop_no_artifact.png` | 1541 | 453 | **In band** |
| `frame_check_f0045.png` | 1600 | 471 | In band |
| `realistic_*` | 1400 | 412 | In band |
| `hero_probe.png` | 1600 | 471 | In band but water-free |
| `car_check_points_R1.png` | 2100 | 618 | At the limit |
| `hero_..._4K...png` | 3840 | 1129 | Oversized |
| `hero_..._7168.png`, `probe_7168x4032.png` | 7168 | 2108 | Oversized, 3.4x |
| `hero_..._max.png` | 16384 | 4819 | Oversized and blank |

## Remaining PNGs at maxdepth 2

| File | Dimensions | Bytes | bpp | md5 | Note |
|---|---|---|---|---|---|
| `_full_view.png` | 1434x807 | 865314 | 0.748 | `40fcd7db…` | Uncropped view, diagnostic |
| `_hdr_crop.png` | 3400x230 | 424646 | 0.543 | `aaf6964b…` | Header crop used for the check above |
| `car_check_points_R1.png` | 2100x1650 | 330520 | 0.095 | `c807d78a…` | Particle-placement diagnostic, not a scene render |
| `frame_check_f0005.png` | 1600x912 | 976174 | 0.669 | `b7c82c47…` | Frame 5, early |
| `frame_check_f0085.png` | 1600x912 | 944340 | 0.647 | `cd7acd3b…` | Frame 85, late |
| `gate.png` | 1920x1000 | 1125363 | 0.586 | `584658cb…` | Gate diagnostic |
| `t1_car_f45.png` | 1170x780 | 76414 | 0.084 | `fc9d6d75…` | Low-detail tier-1 pass |
| `f_0000.png` .. `f_0089.png` | 1200x720 | varies | varies | sequence | 452 files across 5 sequence directories, animation frames |

## Recommendation, one only

**Keep the shipped figure. Do not swap.**

`frame_check_f0045_poster_crop_no_artifact.png` is the only candidate that satisfies every
constraint at once. It is the sole crop whose burn-in header and colorbar tick labels stay
legible at single-column width; at 1541 px it sits at 453 dpi, inside the 1050-to-2100 band
rather than 3.4x past it; its water isosurface renders correctly, unlike `hero_probe.png`;
and it is not blank, unlike every asset above the 7168 GL ceiling. The higher-resolution
heroes are not better source material for this figure, they are the same frame with the
legend rendered too small to read and three times the file weight.

The two things worth knowing, neither of which justifies a swap: the burn-in's `d` and `yaw`
are one row ahead of its `t`, a 0.4 percent discrepancy; and the crop step that produced the
shipped bytes is unscripted, with its immediate source gitignored, so Figure 7's provenance
is PARTIAL. The upstream run is fully traceable via
`renders/yaris_render_s1/render_pv3.py --run g64_m1100 --hero-only 45` and every caption
quantity is independently confirmed by `summary.json` and `metrics.csv`.

Swapping is Pane 1's call, not this pane's. Nothing here was changed.
