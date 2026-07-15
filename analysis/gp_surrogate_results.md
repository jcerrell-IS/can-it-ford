# GP Surrogate for the Track 1 v2 Sweep

Generated July 15, 2026. Source data: `data/track1_sweep_v2/manifest.csv` (36 rows, SLURM job 833218, elapsed 00:01:52, exit 0).
Code: `analysis/gp_surrogate.py`. Metrics: `analysis/gp_surrogate_metrics.json`. Model: `analysis/gp_regressor.joblib`.
Environment: `/work/11603/jcerrell0629/vista/.venv`, scikit-learn 1.9.0 (installed with numpy and scipy pinned so the shared `warpmpm` build was not disturbed).

## Headline

**Regressor: fitted, and well calibrated.** LOOCV RMSE 0.0476 m, R2 0.9912, standardized residual sd 0.950 against nominal 1.0, 97.0% coverage at the nominal 95% interval.

**Classifier: not fitted, and it should not be.** After excluding the under-resolved cells identified by Session B's preflight, **zero of 33 valid runs land on the FORD side**. The label is single-class, so a GaussianProcessClassifier is not fittable. No classifier artifact is saved.

## The FORD class was an artifact, not signal

This analysis was originally requested on the understanding that 2 of 36 runs landed under 0.05 m, both pickup at 0.15 m depth, giving a thin but real positive class. That understanding does not survive contact with Session B's resolution finding (SESSION_STATE.md, 04:12).

The two runs in question were:

| Run | disp (m) | Water layers at `n_grid=64` |
|---|---|---|
| `veh-pickup_dep-0p15_vel-1p00_idx-0024` | 0.0197 | **1, under-resolved** |
| `veh-pickup_dep-0p15_vel-1p50_idx-0025` | 0.0435 | **1, under-resolved** |

Independently reproduced here from the driver's own `water_z_layers` formula:

| Class | Depth 0.15 m layers (v2) | dx (m) |
|---|---|---|
| sedan | 2 | 0.1602 |
| suv | 2 | 0.1705 |
| **pickup** | **1** | 0.2025 |

The pickup's v1 bbox (5.5 m) gave 2 layers at 0.15 m; the corrected v2 bbox (5.89 m) grows `lim = max(2.2*length, ...)`, which grows `dx`, which collapses the water slab to a single particle layer. One layer cannot represent a slab, so the near-zero drift is a discretization artifact.

**Both FORD-side points, and therefore the entire positive class, are among the three invalid pickup 0.15 m rows.** Excluding them leaves 0 positives in 33 valid runs. The apparent emergence of a FORD side between v1 and v2 was the under-resolution bug, not the mass correction.

Per the standing instruction not to force a fit on unlabeled-boundary data: the label is single-class on valid data, so the classifier stops here.

For the record, had the three invalid rows been kept, the classifier would still have failed on its own terms: leave-one-condition-out gave TP=0, FN=2, FP=1, TN=33, FORD-class recall **0.000**, and accuracy 0.9167 against a majority-class baseline of 0.9444. It lost to a constant predictor. Both conclusions agree; the data exclusion just makes the reason unambiguous.

## A prediction I got wrong, stated plainly

Before v2 existed I predicted the geometry correction would push `final_disp_m` **further above** 0.05 m, reasoning that lower density means more buoyancy means more drift. That was **wrong**. 25 of 36 runs moved down, only 11 moved up.

My error was assuming mass was fixed per class. Session B changed masses as well as geometry (sedan 1240 to 1390 kg, pickup 1930 to 2300 kg, SUV 2020 to 1990 kg), and the added mass suppressed drift more than the lower density promoted it. The bulk downward shift is real and physically coherent.

One correction to my own correction: the specific runs that appeared to create a FORD side were not the mass effect either. They were the 1-layer artifact above. I was wrong about the direction, and the evidence that looked like it explained the miss was itself invalid.

## Data caveats that carry into every number below

**Three rows excluded as invalid.** All three pickup depth-0.15 m rows (velocities 1.0, 1.5, 2.0), 1 water layer each. n drops from 36 to 33. The exclusion is applied in `analysis/gp_surrogate.py` via `water_z_layers`, matching the driver's formula, with `MIN_Z_LAYERS = 2`.

**The six remaining depth-0.15 m rows sit at exactly 2 layers**, the bare minimum. They are marginal, and every depth-0.15 m number below should be read with that in mind. Depths >= 0.30 m have 3 or more layers and are fine.

**The SUV is still flagged physically implausible.** `density_plausible` is False for all 12 SUV rows (308.13 kg/m3 against the driver's 100 to 300 band, 2.7% over). Sedan (293.55) and pickup (242.12) now pass. So roughly a third of the training data still fails the sweep's own plausibility gate. Much improved over v1, where all 36 failed, but not clean.

**Mass and dimensions remain perfectly aliased with vehicle class.** Still only 3 unique `(mass, l, w, h)` tuples. The fitted ARD length scales confirm it: `bbox_w_m` and `bbox_h_m` both railed to the 1e3 upper bound, meaning the optimizer switched those inputs off as redundant. Nothing in this design varies mass and dimensions independently.

**Only 3 vehicle classes exist.** Nothing here supports extrapolation to a 4th.

**All runs are `n_grid=64`.** No resolution convergence check exists, and the excluded rows are direct evidence that grid 64 is not adequate everywhere in this design.

## GaussianProcessRegressor: `final_disp_m`

Inputs: `depth_m`, `velocity_ms`, `vehicle_mass_kg`, `bbox_l_m`, `bbox_w_m`, `bbox_h_m`. Standardized. Kernel: Constant * Matern(nu=2.5, ARD) + White. `normalize_y=True`, 8 restarts. n=33.

Fitted kernel:
```
2.88**2 * Matern(length_scale=[2.36, 8.21, 5.62, 14.7, 1e+03, 1e+03], nu=2.5)
        + WhiteKernel(noise_level=1e-09)
```
Length scales in feature order: depth 2.36, velocity 8.21, mass 5.62, bbox_l 14.7, bbox_w and bbox_h railed off. Depth has the shortest length scale and is the most informative input, consistent with the physics. The noise term railed to its 1e-9 floor, so the GP treats the solver as deterministic and interpolates training points exactly. In-sample fit is therefore meaningless; only the cross-validation below carries information.

### Leave-one-condition-out (33 folds, every valid point held out once)

Raw target space is primary because it calibrates better than log10:

| Space | RMSE (m) | MAE (m) | R2 | z mean | z sd | max abs z | 68% cov | 95% cov |
|---|---|---|---|---|---|---|---|---|
| **raw (primary)** | 0.0476 | 0.0370 | 0.9912 | +0.031 | **0.950** | 2.45 | 81.8% | **97.0%** |
| log10 | 0.0799 | 0.0637 | 0.9690 | -0.025 | 1.452 | 3.35 | 54.5% | 87.9% |

The raw model's standardized residuals have sd 0.950 against nominal 1.0, and 97.0% of points fall inside the nominal 95% interval. That is close to textbook calibration, very slightly conservative. The log10 variant is overconfident (sd 1.452, 87.9% coverage at 95% nominal, and 54.5% at 68% nominal) and was rejected despite the target spanning two orders of magnitude.

### Leave-one-depth-row-out

| Depth (m) | Regime | n test | RMSE (m) | max abs z | 95% cov |
|---|---|---|---|---|---|
| 0.15 | **EXTRAPOLATION** | 6 | 0.0501 | 0.15 | 100% |
| 0.30 | interpolation | 9 | 0.1208 | 0.52 | 100% |
| 0.45 | interpolation | 9 | 0.2415 | 1.75 | 100% |
| 0.60 | **EXTRAPOLATION** | 9 | 0.5132 | 2.96 | 89% |

The depth grid is {0.15, 0.30, 0.45, 0.60}, so only **0.30 and 0.45 are interior and count as interpolation**. Removing 0.15 or 0.60 asks the model to predict past the edge of its training range: those are labelled extrapolation, not interpolation, and the 0.60 fold shows the expected penalty (RMSE 0.5132 m, max abs z 2.96, the only fold to drop below nominal coverage). The 0.15 fold has n=6 rather than 9 because the three invalid pickup rows were removed from it.

### Leave-one-velocity-column-out

| Velocity (m/s) | Regime | n test | RMSE (m) | max abs z | 95% cov |
|---|---|---|---|---|---|
| 1.0 | **EXTRAPOLATION** | 11 | 0.0867 | 1.24 | 100% |
| 1.5 | interpolation | 11 | 0.0642 | 0.75 | 100% |
| 2.0 | **EXTRAPOLATION** | 11 | 0.2446 | 2.41 | 91% |

The velocity grid is {1.0, 1.5, 2.0}, so **there is exactly one interior velocity level**. Leave-one-velocity-column-out for interior levels is a **single fold**. One fold is not a validation curve. The 1.5 m/s result (RMSE 0.0642 m) is a single favourable data point, not evidence of general interpolation skill in velocity.

A caution on the group folds: coverage is 100% in five of seven folds with max abs z well under 1. That is not precision, it is the model widening its intervals substantially once a whole row is removed. The model correctly knows it does not know, but those intervals are too wide to support a tight decision.

## What can and cannot be claimed

Supported:
- A GP regressor predicts `final_disp_m` across the valid sampled envelope with LOOCV RMSE 0.0476 m and near-nominal interval calibration (residual sd 0.950, 97.0% coverage at 95% nominal).
- Depth is the dominant input by fitted length scale, consistent with the physics.
- Interpolation in depth at 0.30 and 0.45 m holds up, with the expected accuracy loss at the 0.15 and 0.60 m boundaries.

Not supported:
- **Any FORD/NO-FORD classifier claim whatsoever.** Zero valid runs land on the FORD side. There is no positive class to learn.
- **Any claim that v2 demonstrates a fordable condition.** The runs that appeared to show one are 1-layer artifacts.
- Any generalization to a 4th vehicle class. Only 3 exist, mass and dimensions are aliased with class, and width and height were switched off by the fit.
- Any claim of velocity interpolation skill from more than one fold.
- Any claim of grid independence. Everything is `n_grid=64`, and that resolution is demonstrably inadequate for the pickup at 0.15 m.
- Clean physical plausibility across the board, because all 12 SUV rows remain `density_plausible=False`.

## Threshold sensitivity, and why it is now moot

Pane 2's threshold sensitivity check was expected to move the class boundary. On the 33 valid rows it cannot rescue the classifier at any nearby cutoff, because the entire FORD side was the excluded rows. For reference, the lowest valid displacements are `veh-sedan_dep-0p15_vel-1p00` at 0.0550 m and `veh-suv_dep-0p15_vel-1p00` at 0.0571 m, and both of those sit in the marginal 2-layer band. A threshold above roughly 0.055 m would begin to admit positives, but they would be drawn entirely from the least trustworthy rows in the sweep.

The 0.05 m value is in any case a numerical onset-of-motion tolerance internal to the solver, not a physical criterion from any peer-reviewed source. It was never calibrated to sit where the class balance is informative.

## Recommended next step

The classifier needs FORD-side data from cells that are adequately resolved. Session B's `v3` config (`--config v3`, `n_grid=128`, depths from 0.10 m) reportedly passes preflight on every cell, with a worst case of 2 layers and the pickup at 0.15 m getting 3. Running v3 addresses both problems at once: it resolves the water properly and extends the depth grid downward into the region where a FORD side could genuinely exist.

Rerun this analysis against v3 by pointing `MANIFEST` at `data/track1_sweep_v3/manifest.csv` and setting `N_GRID = 128`. The exclusion filter will then pass every cell, and the classifier will fit automatically if and only if a real positive class exists.

Until v3 exists, the honest deliverable from this sweep is the regressor alone.
