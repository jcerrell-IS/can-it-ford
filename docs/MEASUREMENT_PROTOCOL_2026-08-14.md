# The measurement protocol: stationarity, uncertainty, and a probabilistic verdict

Dispatch 12 Part A. Written 2026-08-14 on branch `claude/fork-protocol`.

Every claim below is tagged by how it was obtained: **[read]** direct source read,
**[measured]** run live on this Mac today, **[cited]** external literature not
re-verified against a primary record here, **[inferred]** reasoning from the other
three. No number in this document was carried from a summary.

---

## 1. The premise, and why there is nothing to look up

A 68-paper search at 91 percent coverage returned no universal frame count and no
universal force-settling threshold for free-surface flow **[cited]**. That is a
negative result about the field, not a gap in our reading of it, and it means the
question "how many frames until the force settles" has no answer to find. What the
literature does supply is a procedure. The procedure is the deliverable.

1. Detect and **exclude** initial and final transients.
2. **Demonstrate** stationarity for the specific observable being reported.
3. Attach uncertainty computed from **correlated** samples, not from raw sample count.
4. If there is no steady state, **say so and report something else**.

Implemented in `analysis/stationarity.py`, tested by `tests/test_stationarity.py`
(33 known-answer tests, **33 passed / 0 failed** **[measured]**).

## 2. Sources, and what each is actually doing

| Source | DOI | Role here |
|---|---|---|
| Chodera 2015, automated equilibration detection | 10.1101/021659 | Step 1. Chooses the discard point t0 that maximises `N_eff = (T - t0) / g(t0)`. Also supplies the statistical inefficiency `g = 1 + 2*tau`. |
| Flyvbjerg and Petersen 1989, error estimates on averages of correlated data | 10.1063/1.457480 | Step 3. Repeated pairwise block averaging; the standard error rises and plateaus, and the plateau is the correct error. |
| Brouwer, Sloof and van Walree 2019 | 10.1016/J.OCEANENG.2019.04.068 | Random uncertainty of statistical moments in a towing tank. |
| Jentzsch, Schmidt and Woszidlo 2021 | 10.1007/s00348-021-03151-5 | Steady and unsteady towing-tank velocities. |
| Thomas, Renilson and Bose 2007 | 10.1080/14484846.2007.11464528 | Water stilling between runs; the **first sloshing mode** governs the inter-run offset time. |

All five are **[cited]**. They have not been checked against a primary record in this
session, and none should enter the paper without that check.

## 3. What the tests caught

The tests are the reason to trust the module, so what they caught is worth stating
plainly. Every anchor is analytic (an AR(1) with `g = (1+phi)/(1-phi)`, white noise
with `g = 1`, a half-sine pulse with impulse exactly `2T/pi`), never a value recorded
from a previous run of this same code. Three real defects surfaced **[measured]**:

1. **The trend test was wrong by a factor of sqrt(12).** It compared the implied
   end-to-end drift against the standard error of the *mean*. For OLS on `n` points
   `S_tt -> n^3/12`, so `SD(drift) -> sqrt(12) * SEM`. Over 40 stationary AR(1)
   records the ratio `|drift|/SEM` had median **3.44** against `sqrt(12) = 3.464`, so
   the test rejected essentially every genuinely stationary series. The slope is now
   compared against its own standard error, with the residual autocorrelation folded
   in. Pinned by `test_trend_test_scales_with_slope_error_not_sem` and by a
   false-rejection-rate test over 20 seeds.

2. **Chodera's maximiser will discard the whole record if the record never settles.**
   On a pure ramp of 1500 samples it discarded **1484**, and the surviving 16-sample
   tail then *passed* the stationarity test, so the pipeline reported a steady
   `mean = 20.013 +/- 0.060` for a series with no steady value at all. That is exactly
   the fabrication this module exists to prevent. A retention floor now caps the
   discard at 90 percent and raises `equilibration_hit_cap`, which forces the
   non-stationary route regardless of what the tail looks like. Hitting the floor is
   information, not an inconvenience: it means the record does not equilibrate within
   its own length.

3. **The zero-variance guard was absolute rather than relative.** `np.mean` of 500
   identical float64 values is not bitwise exact, leaving a ~9e-16 residue whose
   autocorrelation is 1.0 at every lag, so a constant series reported `g = 500.0`.

   Additionally: **symmetric window trimming is provably blind to a linear trend.** On
   `x = 3 + 0.5t` over `[2, 8]`, symmetric trims of 0, 5, 10 and 20 percent all give
   exactly `5.500000`, while one-sided trims give 5.575, 5.650 and 5.800 **[measured]**.
   A sensitivity report built from symmetric trims alone would certify a drifting
   window as insensitive, so one-sided trims were added and are reported separately.

## 4. Demonstrated on real canonical output

Run on `renders/yaris_render_s1/_incoming/g64_m1100/metrics.csv`, 91 frames at 30 fps
**[measured]**. This is the tool applied to project data, not to synthetic input.

| Observable | Discarded | g | N_eff | Result |
|---|---|---|---|---|
| `dmag` displacement magnitude | 42 of 91 | 5.79 | **8.5** | 0.662916 +/- 0.000855 m, naive bar **1.43x too small** |
| `vmag` speed | 46 of 91 | 2.99 | 15.1 | 0.0252523 +/- 0.00183 m/s, naive bar 1.37x too small |
| `yaw_deg` | 39 of 91 | 8.55 | **6.1** | -1.76166 +/- 0.0128 deg, naive bar 1.42x too small |
| `roll_deg` | 3 of 91 | 1.00 | 88.0 | 8.07e-05 +/- 0.00105 deg, uncorrelated |

**The headline number is N_eff, and it is small.** A 91-frame canonical record carries
about **8.5** effectively independent samples of displacement and **6.1** of yaw. Any
error bar computed as `sigma/sqrt(91)` on these observables is too small by roughly
40 percent, and any statement of the form "averaged over 90 frames" is really
averaging over eight or nine independent ones **[measured]**.

Note the window mean `0.662916` is not `final_disp_mag_m`; the canonical stores record
0.658537 in `summary.json` and 0.637019 in `rollout.npz` for this run, a disagreement
already on file as a known 3.4 percent gap. A post-equilibration window mean and a
final-frame value are different quantities and must not be compared as if they were
the same one.

## 5. The finite moving passage

For a moving vehicle there is no infinite stationary record, so towing-tank practice
applies: declare a constant-speed interior window **in advance**, then report its mean
together with **window sensitivity** and **filter sensitivity** alongside the
correlated error bar. `prespecified_window()` returns all four, plus
`sensitivity_exceeds_stderr`, which is the flag that matters: when it is True the
quoted uncertainty is dominated by the analyst's choice of window and filter rather
than by the simulation, and must be reported that way.

This is a **protocol, not a transferable run length**. Acceleration waves and force
oscillations can persist inside a nominally constant-speed window **[cited]**.

## 6. If there is no steady state

Slamming, water entry and impact loading generally have no steady force, and the
accepted practice is peak distributions, impulses, envelopes, or cycle and event
statistics with repeat-run uncertainty **[cited]**. Our own moving scene shows Fz
oscillating by a factor of two or more at 150 frames with no steady value, so this is
the likely outcome for the moving-vehicle work **[cited, from the dispatch; not
re-measured here because Dispatch 9 has not yet produced an output on its branch]**.

`no_steady_state_report()` returns peak and its time, minimum, peak-to-peak, impulse
and absolute impulse, zero-crossing rate and dominant frequency. It deliberately does
**not** compute repeat-run uncertainty, because a single record cannot supply it; the
key `repeat_runs_required: True` is returned as a standing reminder. **An impulse is a
legitimate result. A fabricated steady force is not.**

## 7. The verdict, reframed as a probability

Incipient motion is probabilistic and record-length dependent; the literature defines a
movement probability or activity rate with detection uncertainty, not a single critical
stress **[cited]**. Our criterion is a joint condition held for 3 consecutive frames,
and the register already records one canonical arm at `margin_frames` 0 and another one
frame from flipping. A binary that can be flipped by one frame is not a binary.

`verdict_probability()` reports the activity rate, the longest satisfied run, the
margin in frames, and `p_trigger` from a **moving-block bootstrap**. Blocks, not
individual frames: an i.i.d. frame bootstrap destroys the autocorrelation that makes a
consecutive-frame criterion easy to satisfy and would report a `p_trigger` far too low.
That property has its own test, `test_verdict_block_bootstrap_preserves_correlation`,
which checks that a clustered condition scores higher than a scattered one at the same
activity rate.

Demonstrated on `g64_m1100` with a SLIDE-shaped criterion, `vmag > 0.05 m/s` held for
3 frames **[measured]**:

```
record_frames        91
activity_rate        0.5055
longest_run          46
margin_frames        0
triggered            True
p_trigger            0.9938
bootstrap_block_len  22
```

`p_trigger` is conditional on this record length and this autocorrelation. It is not a
property of the physics alone and **must never be quoted without `record_frames`**.

Two cautions on that demonstration. The 0.05 threshold is `slide_speed_ms` from
`simulation/failure_modes.py:47`, which is a **speed in m/s** that happens to share a
numeral with two distances at `:46` and `:48`; it is used here only to give the
bootstrap a realistically-shaped condition, and this is **not** a re-derivation of the
published SLIDE verdict, which uses a joint condition this single inequality does not
reproduce. Separately, `analysis/stationarity.py` computes nothing about failure modes
and reads no canonical store.

## 8. Provenance rule added by this dispatch

**For any historical extreme-flood grounding, pull the USGS `nwis/peak` record, never
`nwis/iv` alone** **[cited]**. The continuous instantaneous-values feed returned zero
data points during the 2013-10-31 06:00 to 09:00 rise at gauge 08159000, Onion Creek at
US-183, because the sensor gapped during the event, and surrounding hours gave a
misleading 11.5 ft "peak". The dedicated peak-flow record gives 2013-10-31 08:30, gage
height 40.13 ft, discharge 135,000 cfs. Using `nwis/iv` alone would have understated the
crest by about 3.5x. That gauge also publishes stage (00065) and discharge (00060) only,
with **no velocity parameter at all**, so velocity must be derived from discharge over
cross-sectional area rather than pulled.

## 9. How Dispatch 9 uses this

`analysis/stationarity.py` takes a plain time series and a timestep and returns a
`StationarityResult`. It imports only numpy, so it runs anywhere the solver runs.

```python
from stationarity import analyse, prespecified_window, verdict_probability
r = analyse(fz_series, dt=1.0/fps)
print(r.summary())
if not r.stationary:
    report_impulse(r.fallback["impulse"])       # do not invent a steady force
```

**Scope note, stated because it bears on the definition of done.** Dispatch 9's branch
`claude/fork-moving-driver` was at `1a868f3`, identical to `main`, when this was written
**[measured, `git worktree list`]**, so it has produced no output for this module to
consume yet. The module is therefore demonstrated against real canonical outputs
(section 4) rather than against Dispatch 9's, and the integration is an interface this
document specifies, not one that has been exercised end to end.
