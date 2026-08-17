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
