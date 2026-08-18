# D4 job B: the first external validation attempt is INCONCLUSIVE, not a PASS

2026-08-18. **Job 917909**, `gh` partition, `RC_B=0`, `ALLDONE`, stderr 0 bytes,
13:55 elapsed, 200 frames written. It ran. It did not answer the question.

## 1. The headline: NOT GRADEABLE

The sphere never reached hydrostatic equilibrium, so there is no steady reaction to
compare against the closed form. Measured on the reaction series **[derived]**:

| window | mean Fz | std | slope |
|---|---|---|---|
| frames 0-49 | 77.780 N | 76.495 | max **342.97 N** |
| frames 50-99 | 64.841 N | 15.835 | -0.129 N/frame |
| frames 100-149 | 56.842 N | 3.019 | -0.155 N/frame |
| frames 150-199 | 50.260 N | 1.286 | -0.081 N/frame |
| frames 180-199 | 49.097 N | 0.543 | **still -0.0585 N/frame** |

`blocking.stationarity` on the retained half: `halves_stationary False`,
`trend_stationary False`, slope **-0.128 N/frame at 8.47 sigma**. The run is a monotone
decay from ~343 N toward ~49 N and was still falling when it stopped.

**Do not quote a percentage from this run.** The late-window value is 49.10 N against
69.2180 N, but it has not converged, so that number is a snapshot of a decay, not a
measurement.

## 2. My grader reported PASS. That was wrong, and the bug is instructive

The first version of `grade_job_b.py` reported **PASS at -9.806%**, mean 62.4305 N.

That mean is the average of the decay above. The cause:
`blocking.find_stationary_window` returns a **tuple** `(drop, status, detail)`, not a
dict. The grader read

```python
start = int(win.get("start", 0)) if isinstance(win, dict) else 0
```

so on real data `isinstance(win, dict)` was False, `start` silently became **0**, and an
explicit `(None, 'undecidable_too_short', ...)` verdict was discarded. It then averaged
the entire transient and landed, by coincidence, just inside the 10% PASS band.

**This is the seventh check-that-cannot-fail on this branch, and it is in the tool I
wrote to stop results being graded after the fact.** The self-test did not catch it
because all three synthetic series had genuinely stationary tails, where a start of 0 is
nearly harmless. Testing a grader only on data it can grade does not test its refusal.

## 3. What the grader does now

Two refusal gates, and a threshold chosen on measured separation:

- The tuple return is parsed properly, and an **undecidable** window search is
  distinguished from a **non-stationary** series. Refusing on undecidability alone would
  refuse every 200-frame run, which is as useless as refusing nothing; the fallback is a
  stated `DEFAULT_DROP_FRAC = 0.5` with the stationarity test as arbiter.
- `blocking.stationarity` judges the **retained** window, not the full series, so a normal
  startup transient does not fail a good run.
- `STATIONARITY_N_SIGMA = 3.0`, not the library default 2.0, which runs two tests and
  falsely refused one of three genuinely stationary self-test series. Measured separation:
  real job B fails at **8.47 sigma** and is refused at 2.0, 2.5, 3.0 **and** 4.0;
  `synth_pass` 0.27 and `synth_partial` 0.36 are accepted everywhere; `synth_fail` 2.13
  was the false refusal. **3.0 cannot change the real verdict**, so it is not a threshold
  tuned toward an answer.

Behaviour now: real job B **NOT GRADEABLE**, `synth_pass` **PASS**, `synth_partial`
**REPORTABLE PARTIAL**, `synth_fail` **FAIL**.

## 4. What the run does establish

- **The scene runs on a GPU.** First contact for `sphere_heave.py` against warpmpm:
  598,505 water particles, 82 substeps, dx 0.01875 m, 16.0 sphere cells across.
- **The SDF is accurate.** `sdf_radius_rms_err_m` **1.16e-04 m** against the closed form
  `|x| - r`, max error 2.06e-03 m, band clearance 2.14x. The collider geometry is not the
  problem.
- **`analytic_buoyancy_N` is 69.21798679943727**, confirming the target the scene computes
  for itself matches the 69.2180 N fixed in the manifest.
- **The SDF build, not the physics, dominated the run**: ~8 to 9 minutes of the 13:55.

## 5. Next, and it is a run-length question not a physics question

The decay is still 0.0585 N/frame at frame 199. Nothing here suggests the coupling is
wrong; it suggests 200 frames is far too few for this tank to settle. The next run needs
substantially more frames, and now costs less per run: the mesh is 0.44x the builder cost
and `--sdf-cache` removes the rebuild entirely on repeats.

**UNREVIEWED.** No physics-skeptic pass has run on this document.

## 6. Diagnosis: the free surface falls, and the sphere is pinned to where it used to be

Added after section 5. The sphere never moves: `z_m = 0.575000` and `vz = 0` at frames 0,
50, 100 and 199, spanning 0.425 to 0.725 with the waterline at 0.575, i.e. exactly half
submerged **[read]**. So the sphere is not the variable. The water is.

**A falling free surface accounts for the deficit exactly** **[derived]**:

| quantity | value |
|---|---|
| deficit, target minus final | 69.2180 - 47.8554 = **21.3626 N** |
| `dF/d(surface)` = `rho*g*A_w` | 692.1799 N per metre |
| **implied surface drop** | **3.09 cm**, 6.17% of the 0.5 m column |

The sphere is held at the ORIGINAL surface height, so as the water drops it sits
progressively proud of the waterline and its submerged cap shrinks. The reaction decays
because the geometry it is measuring is changing underneath it.

**Compression explains only a quarter of it.** From the scene's own EOS constants,
`b = 0.00593475 /m`, the mean density rise over a 0.5 m column is 1.4970%, which shortens
the column by about **0.74 cm**, i.e. **23.9%** of the observed 3.09 cm. **The other 76%
is not compression** and is the thing to find: candidates are water leaving through the
floor or wall bands, or the jittered seed lattice settling into a denser packing than it
was created at.

**This reframes the whole run.** Section 5 called it a run-length problem. That is at best
half right: more frames alone would let the surface keep falling and the reaction keep
decaying, which is consistent with the extrapolation refusing to converge in section 5.1.
The scene measures a moving target.

**Two candidate fixes, neither yet implemented:**
1. Settle the water FIRST, then place the sphere at the settled surface, so the pose is
   defined against the equilibrium free surface rather than the seeded one.
2. Measure the actual free-surface height per frame and compare the reaction against the
   analytic cap volume AT THAT SURFACE, so the target tracks the geometry.

Option 2 is the better validation: it removes an assumption instead of tuning the setup to
satisfy it, and it converts a moving target into a measured one.

**The extrapolation in support of this is INCONCLUSIVE and must not be quoted.** Fitting
`A + B*exp(-t/tau)` over five late windows gives asymptotes of 13.639, 32.700, 41.547,
43.856 and 47.277 N: N=5, range [13.639, 47.277], **spread 33.638 N** against a 69.218 N
target. The model does not describe the decay and no asymptote is determined by this data.
The only robust statement is directional: every window's estimate lies well below the
target, so there is no evidence the decay is heading toward 69.218 N.

**UNREVIEWED**, including every number in this section.

## 7. The 600-frame run: the decay is the surface, and a stable +61% remains

Run on idev **917886**, node c642-032, 600 frames, `RC_B=0`, **423 s wall clock** against
13:55 for the 200-frame run: the 32x64 mesh and the SDF cache did what they were meant to,
and the cache is now on disk at 22.3 MB.

Still **NOT GRADEABLE** on the nominal criterion, but converging: the decay slope fell from
**-0.128 N/frame at 200 frames to -0.0183 at 600**, a factor of 7, still 10.30 sigma from
stationary.

**The free-surface instrumentation earns itself here** **[derived]**:

| frames | surface (m) | drop (cm) | submerged (m) | Fz (N) | analytic @ surface (N) | ratio |
|---|---|---|---|---|---|---|
| 0-99 | 0.54064 | 3.44 | 0.11564 | 71.452 | 45.946 | 1.5908 |
| 100-199 | 0.51999 | 5.50 | 0.09499 | 53.591 | 32.872 | 1.6308 |
| 200-299 | 0.51081 | 6.42 | 0.08581 | 45.941 | 27.502 | 1.6707 |
| 300-399 | 0.50702 | 6.80 | 0.08202 | 40.989 | 25.385 | 1.6145 |
| 400-499 | 0.50474 | 7.03 | 0.07974 | 38.879 | 24.145 | 1.6102 |
| 500-599 | 0.50338 | 7.16 | 0.07838 | 37.418 | 23.411 | 1.5983 |

**`Fz` falls by a factor of 1.9 across the run while the ratio against the measured
surface stays flat.** Retained half (frames 300-599, N=300): ratio mean **1.6077**, range
[1.5771, 1.6778], spread 0.1007, slope -9.6e-05 per frame. **The decay in the reaction is
almost entirely the falling surface**, which is what the instrumentation was built to
separate and what job 917909 could not.

The surface fell **7.23 cm** by the end, not the 3.09 cm measured at 200 frames. It was
still falling.

### 7.1 What remains, and the two readings I cannot yet separate

A stable **+60.8%** of the closed form at the measured surface. Two candidates, and this
document does not choose between them:

1. **The coupling over-predicts buoyancy** by roughly 60% on a shallow spherical cap.
2. **`measure_surface()` under-reads the surface.** It takes the 99th percentile outside a
   2R annulus. If the water has spread outward past the slip planes, particles sitting in
   the margin would pull the percentile down, making the cap too small and the ratio too
   large.

Reading 2 has direct arithmetic support and should be tested first. A 7.2 cm drop over the
nominal 1.0 x 1.0 m tank is **14.4% of a 0.5 m3 column**, against about 1.5% available
from EOS compression. Volume has to go somewhere. The slip planes sit at 0.1 m while the
domain runs to 1.2 m, so there is a 0.1 m margin outside them on every side; water
spreading into it conserves volume while lowering the column. Spreading to the full
1.2 x 1.2 m footprint would give 0.5/1.44 = 0.347 m, a **15.3 cm** drop, and 7.2 cm is
consistent with partial spreading.

**Next test, and it is cheap and Mac-side if the particle positions are dumped:** count
water particles outside the slip-plane footprint. If a material fraction sits in the
margin, reading 2 is confirmed and the scene needs the walls fixed, not the coupling.
Until that is done, **the +60.8% must not be reported as a coupling error**.

**UNREVIEWED**, every number in this section, settle 8 constructor-only, trimesh 4.12.2,
engine 627367e.

## 8. Physics-skeptic audit: NOT CLEAN. The +60.8% is explained, and section 7 was wrong

Four blocking issues. Section 7 stands on its tables, which reproduce exactly, and falls
on its framing.

### 8.1 BLOCKING. The excess is the collider's contact band, with no fitted parameter

`kernels/mpm_solver_warp.py:2627` sets `band = float(self.mpm_model.dx)` and `:2711` gates
the impulse on `if sd <= param.band`. **Every grid node within dx of the surface is
constrained**, so the fluid sees a sphere of radius **R + dx = 0.16875 m**, not 0.15.

Evaluating the same closed form on that body, with nothing fitted:

```
R_eff = R + dx     per-window ratio 1.0375 1.0293 1.0202 0.9708 0.9584 0.9454
                                                             mean  0.9936
```

The best-fit band that zeroes the excess is **0.986 dx**, the engine default to **1.4%**.
**A "+60.8% unexplained" residual becomes -0.6%.** Section 7.1 offered two candidates and
chose neither; it was missing the one that works, and its recommended next test was the
wrong priority.

Why this regime and not the C1-SDF box: the submerged cap is only **4.18 dx** deep at the
end of the run, so the contact band is **23.9% of the cap depth**. That is exactly where a
band-thickness inflation dominates, and it is why the box gave 7.3-7.7% and this gives 61%.

**The decisive test is a resolution sweep, not a particle count.** The band hypothesis
predicts the excess at fixed submergence falls with dx: **+97.4% at g48, +69.1% at g64,
+43.5% at g96, +31.7% at g128**. A wall-leak hypothesis predicts **no dx dependence at
all**. One g96 rerun separates them.

### 8.2 BLOCKING. The pre-registered criterion says FAIL, and the tool had never said so

`rel_error` on the measured-surface ratio is **0.6077** against pre-registered bands of
0.10 / 0.25 that this project declared "set in advance and are not to be moved". **That is
a FAIL**, and the word does not appear anywhere in section 7.

Worse, and this is mine: the grader's refusal path **dropped the very key** the file
promises will be "reported ALONGSIDE the nominal grade, never instead of it". Both real
runs refuse, so **the tool had never emitted that criterion for any real run**, and the
+60.8% in section 7 was computed by hand **outside the tool built to stop hand-computed
grading**. Fixed: the refusal path now carries it, and prints
`measured-surface ratio 1.6077 (+60.77% from 1.0) BAND: FAIL`.

### 8.3 BLOCKING. Section 7.1's mechanism is refuted, and there is a real scene bug instead

The percentile argument is dead: adding a fraction f of low-z margin particles moves p99 by
**0.84 mm**, and about **24 mm** is needed, short by a factor of 28. It is also a category
error, because a genuine leak lowers the true surface, which `measure_surface` then reports
and `buoyancy_at` is evaluated at, so a leak **cannot bias the ratio at all**.

The 7.16 cm drop is **63% explained without any water leaving**:

| term | cm |
|---|---|
| estimator: top particle centre is h/2 below the fill line | 0.469 |
| EOS compression | 0.742 |
| **floor BC one cell low: the node at 4 dx is exempt from its own plane** | **1.829** |
| wall BC acting 0.625 cm outside the nominal wall on each side | 1.499 |
| **total explained** | **4.539** |
| residual, genuinely unexplained | ~2.6 (5.5% of the water, not 14.4%) |

**The floor term is a scene bug worth fixing on its own**: `mpm_solver_warp.py:1955` gates
on `dotproduct < 0.0`, and `FLOOR = 0.075` is exactly 4 dx, so the node lying *on* the
floor plane receives no boundary condition. And **frame 0 is reconstructible to 0.20 mm**
from seeding plus one tick of free fall, so 0.78 cm of the headline 7.23 cm is present
before any physics runs.

### 8.4 BLOCKING. "Converging" is contradicted by the gate's own statistic

Section 7 reports the slope falling 7x and calls it converging. The **test statistic rose**:
8.47 sigma at 200 frames, 10.30 at 600, and **19.75 on the last 100 frames**. Reporting the
raw slope as the story while the gate's own number moves the other way is choosing the
flattering statistic.

### 8.5 Also found

- **Claim 1's physics HOLDS and is now independently supported**: `d lnFz / d ln(sub)` over
  the six windows is **1.6524** against the exact spherical-cap law's **1.6542**. Fz follows
  the cap law, not an area law. Only the headline sentence was wrong: it welded a full-run
  factor of 1.9 to a last-half stability statistic, and over frames 300-599 Fz falls only
  1.095x. Across the full run the ratio is **not** flat and not monotone, wobbling 5.3%.
- **Over-precision.** 1 mm of surface error is 2.28% of ratio; the estimator's own
  quantisation h/2 = 4.69 mm is **10.70%**. Quoting "+60.8%" and "spread 0.1007" from that
  estimator is over-precise by an order of magnitude. The h/2 offset is a one-line fix.
- **The "~10 percent" false-refusal rate in `grade_job_b.py` is wrong**: measured
  **15 to 39%** on stationary AR(1), and still 1.7 to 19.3% at 3.0. The test is
  mis-calibrated at every threshold; 3.0 halves a problem it does not fix. **3.0 still
  cannot flip either real verdict**, which was the only load-bearing part.
- **Unreported replication, in the run's favour**: the 200- and 600-frame runs agree on
  window means to 0.27 / 0.11 / 0.13 / 0.01%, correlation 0.999991. Strongest evidence in
  the dataset and section 7 never mentioned it.
- **Unreported regression, against it**: the mesh coarsening raised
  `sdf_radius_rms_err_m` 1.159e-04 -> 2.201e-04, **1.90x**. Immaterial to the excess but it
  should have been stated, and "the collider geometry is not the problem" is a non-sequitur
  when the live candidate is the band, a coupling parameter.
- **"The sphere never moves `[read]`"** is configuration, not observation: `free=False`
  means `advance()` cannot integrate it. **Dead literal**: `RHO_W = 1000.0` at
  `sphere_heave.py:136` is read by nothing. **Timing**: neither JSON carries a wall clock,
  so 423 s and 13:55 came from the job log's TIMING_ANCHOR pair on Vista, not from an
  artifact on this host.

**Net: the run is better than section 7 said about the physics and worse than it said
about the verdict.** The coupling is not showing a 61% error; it is showing a band-inflated
sphere, which is a known, quantified engine behaviour. The pre-registered criterion is a
FAIL and must be reported as one.

## 9. The g96 discriminating run: band CONFIRMED, wall-leak REFUTED

Job fired into idev 917886, g96, 300 frames, `RC_B96=0`, **496 s**, 2,019,044 water
particles at dx 0.0125. Everything else held identical to the g64 run on purpose, so the
only variable is resolution.

**The predictions were opposed and quantitative, and were stated before this run existed**
(section 8.1): contact band gives **+69.1% at g64 and +43.5% at g96**; a wall leak gives
**no dx dependence at all**.

Measured at **matched submergence** (0.07898 to 0.10093 m, the overlap of the two runs),
which is the like-for-like the prediction is about **[derived]**:

| | N | ratio | range | excess | band-corrected |
|---|---|---|---|---|---|
| **g64** (dx 0.01875) | 391 | 1.6320 | [1.5458, 1.7582] | **+63.20%** | **0.9937** |
| **g96** (dx 0.0125) | 214 | 1.4313 | [1.0540, 1.9728] | **+43.13%** | **1.0230** |

**g96 measured +43.13% against a predicted +43.5%: a hit to 0.4 percentage points, with
nothing fitted.** The excess falls with dx exactly as the band model requires, so **the
wall-leak hypothesis is refuted**: it predicts no resolution dependence and the excess
moved 20 points.

Correcting each run for its own band puts both within **2.3% of unity** (0.9937 and
1.0230), at two different resolutions. That is the strongest evidence in this chain that
**the coupling is not in error**: the fluid is seeing a sphere inflated by one cell,
which is documented engine behaviour at `mpm_solver_warp.py:2627` and `:2711`, not a
defect in the buoyancy response.

### 9.1 What this does NOT establish, stated plainly

- **g96 is much noisier.** Last-quarter spread is 0.5450 against g64's 0.0344, and the
  matched-window range runs [1.0540, 1.9728]. The mean is the result; the spread is wide,
  and 300 frames is half the g64 run. A repeat at g96 with more frames is needed before
  the +43.13% is quoted as a settled number rather than a single run's mean.
- **The band correction fixes the level, not the trend**, as section 8 already recorded.
  Its slight over-correction at g96 (1.0230 against g64's 0.9937) is consistent with that
  and is not explained here.
- **Neither run is stationary**, so the nominal criterion still refuses both, and the
  pre-registered measured-surface criterion still reports **FAIL** on the uncorrected
  ratio. Confirming the band explanation does not convert a FAIL into a PASS: it explains
  what the number is, and the criterion was fixed against the uncorrected quantity.
- The floor-BC bug from section 8.3 is untouched and still real in both runs.

**UNREVIEWED**: this section has not been through the physics-skeptic. Settle 8
constructor-only, trimesh 4.12.2, engine 627367e.
