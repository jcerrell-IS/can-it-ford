# The Hailuo comparison claim has no producing artifact

Written 2026-08-04. Every statement below was read live from the working tree at
`/Users/josie/can-it-ford` on that date.

## The claim

`README.md` line 175:

> - **Hailuo comparison:** `figures/hailuo/`, a visual-model-vs-physical-model comparison for the poster (Hailuo predicts FORD at d=0.30 m / v=1.5 m/s, pilot L2 predicts NO-FORD)

## What `figures/hailuo/` actually contains

    Hailuo_Video_Low-angle roadside three-quart_528604257021341700.mp4      3008952 B
    Hailuo_Video_Low-angle roadside three-quarter view, ..._528605825435185156.mp4  2216715 B
    Hailuo_Video_Without changing anything just_528534639070212104.mp4       540717 B
    hailuo_frame_2.5s.png                                                    265957 B
    opening_frame_clean.png                                                  751504 B
    peak_frame.png                                                           848474 B
    prompt_recommendation.md                                                   6077 B

Three generated clips, three stills, one prompt note. There is no comparison
figure in this directory, no verdict file, no measurement, and no CSV.

## Splitting the claim in two

**"pilot L2 predicts NO-FORD" is SUPPORTED.** `data/l2_results_from_wandb.csv`
row 1 reads:

    level,depth_m,velocity_ms,divergence,dv_product,l1_haz_score,l1_verdict,l2_verdict
    L2_Genesis_SPH,0.3,1.5,True,0.45,0.75,FORD,NO-FORD

That is the exact condition, and it records `l2_verdict=NO-FORD` and
`l1_verdict=FORD`.

**"Hailuo predicts FORD" is UNSUPPORTED.** No file in this repository records a
Hailuo verdict, a Hailuo displacement, a model version, or a generation date.
The three mp4 files are unlabelled generative video. A FORD verdict from them
is a human visual judgement that was never written down in any artifact. A
repo-wide grep for `hailuo` returns exactly six files: `README.md`,
`.gitignore`, `PROJECT_FILE_MAP.md`, `docs/SESSION_DISPATCH_2026-07-25.md`,
`docs/POSTER_ASSET_TABLE.md`, and `figures/hailuo/prompt_recommendation.md`.
None of them contains a measured or derived Hailuo result.

## The figure that was supposed to carry this comparison is synthetic

`scripts/plot_hailuo_comparison.py` writes `figures/baseline_comparison_v2.png`
(line 173). It loads no Hailuo frame and reads no data file. Its imports are
`matplotlib.pyplot`, `matplotlib.patches.FancyBboxPatch`, and `numpy`, and it
contains no `read_csv`, `np.load`, `loadtxt`, `imread`, `PIL`, `cv2`, `glob`, or
bare `open()`. Its trace is manufactured:

    line  8   PEAK_DRIFT = 0.2884
    line 12   np.random.seed(7)
    line 14   base   = PEAK_DRIFT * (1 - np.exp(-2.4 * t))
    line 15   osc    = (0.032 * np.sin(3.1*t) + 0.016 * np.sin(7.2*t)) * np.exp(-0.35*t) ...

## 0.2884 matches no run in this repository

Three real time-series files exist for d = 0.30 m, v = 1.5 m/s. All three have
91 samples over 0 to 3.000 s and columns `t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg`:

| File | peak `dmag` | final `dmag` |
|---|---|---|
| `data/track1_sweep_v1/veh-sedan_dep-0p30_vel-1p50_idx-0004_timeseries.csv` | 0.252365 m | 0.252365 m |
| `data/metrics_d0p30_v1p5_check.csv` | 0.770328 m | 0.770318 m |
| `data/flood_vehicle_metrics_d0p3_v1p5.csv` | 0.770265 m | 0.770248 m |

The hardcoded `PEAK_DRIFT = 0.2884` equals none of them. It is a fourth number
whose origin is not recorded anywhere in the repository.

Those three files also disagree with each other by a factor of 3.05. That
disagreement is logged as DISPUTED and is not resolved here.

## None of the three is the Genesis SPH pilot

The claim names the pilot. The Genesis SPH pilot exists only as the nine-row
summary `data/l2_results_from_wandb.csv`, which has no time column. The three
time series above come from a different solver track. There is therefore no
drift-versus-time trace for the pilot at any condition, real or otherwise.

## What exists instead

`scripts/plot_hailuo_comparison_REAL.py` was added alongside the original,
which is unmodified (sha256
`d21f9fa45147f31ea977ef6326f84efc040e5be259bc3e0e21fa8569ef143561`). It reads a
real CSV, prints the file it read and the peak it computed, prints the competing
peaks from the other two files as DISPUTED, reads the pilot verdict from the
wandb CSV, and states on the figure itself that the trace is not the Genesis SPH
pilot. It cannot be run on this Mac: matplotlib is not installed under any
python3 on this machine, which also means the original has not been runnable
here either. Its data path was verified with a matplotlib stub and produced the
numbers in the table above.

## What would close this

1. A recorded Hailuo verdict: model version, generation date, prompt, and the
   frame-by-frame or endpoint reading that produced FORD.
2. A decision on which of the three conflicting d=0.30/v=1.5 series is canonical,
   or a statement that all three are superseded.
3. Either a pilot time series, or a README line that does not imply one exists.
