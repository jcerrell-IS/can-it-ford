# renders_preview — read before using either file

Added 2026-08-08 by the ctx-census session. Additive; does not modify either
artifact.

## Contents

| file | what it is |
|---|---|
| `g64_m1100_live_2026-08-07.mp4` | 1920x1080, 180 frames, 6.000 s, H.264. Annotated diagnostic dashboard for gated run `g64_m1100`. |
| `j1_force_comparison.png` | 69 KB force comparison figure for register J.1. |

## THE VIDEO IS UNREPRODUCIBLE

Its generator does not exist on this machine. Searched the dashboard's own
strings (`"Verified state"`, `"Plan view"`, `"a real cross-section"`) across the
repo, `~/Downloads`, and `~/canitford_census_2026-08-07/`: no hit. The nearest
candidate in the tree, `renders/yaris_render_s1/render_hero_g64_m1100_2026-08-06.py`,
is a different render (marching-cubes free surface, L0/L1a/L1b/L2 verdict strip,
no dashboard panels). `analysis/render_rollout.py` is NOT it either: that targets
the s3 enhanced-pipeline schema and builds a single 3-D axis. A Vista-side search
timed out at 60 s and is inconclusive.

Consequence: **the caption cannot be corrected by re-rendering.** The caveat below
must travel with the video into any poster, figure caption, or paper text.

This is the same un-regenerable-artifact defect the register records for
`c1only.sbatch` and `c2only.sbatch`, now applied to the project's one headline
visual deliverable. If the generator is recovered, commit it immediately.

## REQUIRED CAVEAT

The video's "Verified state" panel contains two lines that do not hold. Both
predate the C1 root-cause finding (video rendered 18:13, finding committed 20:41
on 2026-08-07).

> `floats? no: buoyancy 4.5 kN < weight 10.8 kN` is a **static analytic**
> calculation. It sits in a panel headed "Verified state" beside genuine solver
> outputs, which implies the simulation verified it. It did not, and on the
> material-8 rigid path it could not.
>
> `verdict SLIDE` rests on a displacement curve produced by a coupling that forms
> no force. `rigid_body_integrate` assigns
> `v_cm_new = rigid_linear_mom[b] / M` (`kernels/mpm_utils.py:1434`) from an
> accumulator zeroed every substep, so the body adopts a mass-weighted mean of
> grid velocity rather than integrating a force. Measured, it registers about
> **1.5 % of the analytic buoyant response**
> (`docs/C1_ROOT_CAUSE_2026-08-07.md` section 3).

Minimum text to place beside the video:

> Buoyancy shown is analytic, not measured. The material-8 rigid path forms no
> force and registers about 1.5 % of analytic buoyant response, so the
> displacement trace and the SLIDE verdict inherit that defect.

## WHAT THE VIDEO GETS RIGHT

Worth stating, because most of it is unusually well sourced and should not be
discarded with the two lines above. It embeds, correctly: the engine identity
(Warp MPM, not Genesis), the under-resolution (`4 water layers, depth/dx = 2.0`),
the realized density 309.74 with fill ratio 1.0024, the rollout-vs-summary
displacement disagreement of 3.38 %, the gate P-2 failure at 10.67 % against a
10 % limit over 34 of 90 frames, the AR&R stationary-vehicle caveat, and an md5
provenance line stating nothing was re-simulated.

One qualification on that list. The video annotates `DRIFT_THRESHOLD` as having
no peer-reviewed source and being "declared 16x under 4 names". The
no-peer-reviewed-source half is correct and is the important half. **The count is
not.** CLAUDE.md item 13 states 16 sites under four names and then says
explicitly to *"treat both counts as floors"*, register D7 disagrees at three
names, and the J.1 survey found 17 sites plus a fifth undocumented name
(`L2_DRIFT_M`, 7 further sites). So read the video's 16x/4 as a lower bound, not
a total, and do not quote it as a count anywhere.

## ONE MORE LIMITATION NOT SHOWN ON THE VIDEO

The header reads `depth 0.30 m`. That is the initial condition, not the
experiment. Measured from the same run's `rollout.npz`
(`docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md` section 4):

| probe | min | max | excursion vs nominal |
|---|---|---|---|
| bow | 0.2279 m | 0.3958 m | **-24.0 % to +31.9 %** |
| footprint | 0.2260 m | 0.3750 m | -24.7 % to +25.0 % |

**Only 20 of 90 frames sit within +/-10 % of the nominal depth.** Water piles 2.5x
against the closed downstream wall by frame 45. The streamwise fetch is 2.2 hull
lengths. It is a tank that fills and sloshes, not a channel that conveys.
