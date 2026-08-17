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
