# D4: what the adversarial physics-skeptic pass changed

2026-08-16. Branch `claude/r5-physics`. This is the review the dispatch required before any
D4 number could be finalised. It found **seven blocking issues**, two of which contradicted
assertions I had already committed as passing tests. Everything is recorded here including
the items where I was wrong, and the corrections are applied in the files named.

**Status change: the earlier documents move from UNREVIEWED to REVIEWED-WITH-CORRECTIONS.**
Claims not listed here survived the pass; claims listed here are corrected or retracted.

---

## Blocking issues, and what was done

### B1. The 41% cap-hit was not the finding I said it was. RETRACTED.

`R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md` led with "14/34 (41%) hit the 50% search cap ...
**The 41% cap-hit is the finding** ... those runs are not long enough to demonstrate that
their own transient has ended."

**That does not follow, and the review proved it with a control I should have run myself.**
On a synthetic pure linear ramp with **no transient at all**, `find_transient` returns the
cap at n = 91 **and again at n = 400**. A 4.4x longer run hits the same cap. The objective
minimises the blocked standard error, and on any trending series discarding more always
lowers the retained variance, so the cap is what the rule returns for a trend, not for a
short run.

Compounding it: **10 of the 14 cap hits were `dmag`**, a cumulative displacement magnitude.
Blocking estimates the standard error of the mean of a *stationary* process; the windowed
mean of an accumulated distance is not a physically meaningful target. I should not have
blocked it at all.

**Corrected figures, `vmag` only, which is a velocity and therefore a legitimate target:**

| | pooled, as published | corrected |
|---|---|---|
| cap hits | 14/34 = 41% | **4/17 = 24%** |
| not stationary | 18/34 | **6/17** |

The failure mode is now documented in `blocking.py:find_transient` with the full control
table, and `analyse()` returns `transient_hit_cap` so a boundary can never again be read as
a measurement. I found the `dmag` half of this independently before the review returned;
the n = 400 control, which is the part that actually kills the interpretation, is the
review's.

### B2. "No SLIDE verdict can flip" was argued without the mechanism that decides it.

`R5_PHYSICS_BRAKE_STATE.md` argued only about sliding. But `simulation/failure_modes.py:33`
and `:230-234` show the reported mode is a **severity-ranked competition**, with
`MODE_SEVERITY = (SLIDE, TOPPLE, FLOAT)` and `mode = reached[-1]`. A SLIDE verdict does not
need sliding to stop in order to flip; it only needs a higher-ranked mode to trigger. Lower
friction raises net surge acceleration, and TOPPLE gates on `surge_accel_g >= ssf`. **My
argument did not address the only mechanism that could have refuted it.**

**The conclusion survives, on a bound I had not computed.** The review computed it: every
run's peak surge acceleration is a 1- or 2-frame spike, and the sustained 3-frame level is
0.08 to 0.51 of `ssf`. The worst case is `sweepV_g64_v3p0` at `T3 = 0.721`. The absolute
maximum acceleration increase from removing friction entirely is `mu*(1+e) = 0.55 x 1.05 =
0.578 g`, giving `0.721 + 0.578 = 1.299 < 1.42 = ssf`. **No run can reach TOPPLE by
friction removal alone.** FLOAT is further away: only `sweepV_g64_v3p0` ever clears the
lift gate, with zero frames where lift and vertical speed hold together, and friction is
tangential so there is no first-order lift mechanism.

So the claim stands and its warrant is now the bound, not the direction argument alone.
That distinction matters: an argument that reaches the right answer without engaging the
refuting mechanism is not a verified argument.

### B3. The reflection window used the wrong wave speed, and this changed a design decision.

I asserted that radiated **energy** travels at the group velocity, and dismissed
`sqrt(g*h)` as "the wrong wave speed". **Kramer 2021 section 3.5, p.16, does this exact
calculation with the PHASE celerity and says why**, verbatim: "This can be considered a
conservative estimate, as the main wave front of radiated waves would have propagated with
the group velocity rather than the phase velocity."

The benchmark deliberately takes the **faster** speed because it bounds contamination
earlier. My choice was the least conservative of three, presented as the most physical.

| `lim` | group | **Kramer phase** | `sqrt(g*h)` bound |
|---|---|---|---|
| 1.2 m | 2.12 T | **1.06 T** | 0.58 T |
| 2.0 m | 3.82 T | **1.91 T** | 1.05 T |
| 2.2 m | 4.24 T | **2.12 T** | 1.16 T |

**`lim = 1.2` buys 1.06 clean periods, not the 2.12 I claimed.** Two periods on the
benchmark's own convention needs `lim >= 2.085 m`. `PLANNED_CONFIGS` now carries
`(2.0, 107)` and `(2.2, 117)`, `reflection_windows()` reports all three speeds so the
convention is visible rather than embedded, and the default is Kramer's.

**This was also a self-chosen operating point passing its own test**, which is the exact
failure mode `R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md` claims to have eliminated. The
committed assertion "the SMALLEST planned domain still buys two clean natural periods"
passed only because it used my convention. It now asserts that some domain clears two
periods **on Kramer's convention**, and separately that the smallest is honestly labelled
sub-two-period.

### B4. Job C's grading criterion was unworkable. Fixed before it ran.

I proposed grading against absolute tolerances of 0.090 / 0.270 / 0.450 mm at nominal
`H0`. But Kramer Table 4, p.17, gives the **measured** drop heights as
**{29.16, 89.18, 150.06} mm**, and p.21 states results are normalised "with respect to the
measured drop height in each repetition". At 0.1D the nominal-versus-measured gap is
**0.84 mm, which is 9.6x the tolerance I proposed to grade against**.

Corrected criterion: compare on **normalised** `x3/H0`, or on absolute displacement with
each run's `H0` set to its **measured** value. The manifest's whole value is that criteria
are fixed in advance, so this had to be fixed before Job C, not after.

### B5. "Four runs exceed 14%" is five.

`sweepV_g64_v3p0` at **14.573%** was omitted. Re-measured: 22.591, 20.609, 18.732, 14.993,
**14.573**. Trivial, and exactly the kind of countable claim that should never be wrong.

### B6. The register J.1 caveat was missing from every R5 document.

Two documents invoked "the path validated to 7.3-7.7%" as a warrant while none carried the
three recorded reasons that validation **does not clear the 17 canonical runs**: the 17 use
restitution 0.05 where C1 used 0.0 everywhere, they resolve depth at 2 grid cells, and
self-consistency is not validation. Added to `sphere_heave.py`'s COUPLING section, with the
note that the narrowness of that warrant is precisely why an external benchmark is worth
building.

### B7. The Nihei corrigendum is not carried.

D1's own source record (`13f7a2d`) says verbatim: "**Status: OPEN.** Do not treat the
numbers below as final until someone with publisher access reads the corrigendum." The
corrigendum `10.1016/j.rineng.2025.107527` exists and is unread. `R5_PHYSICS_BRAKE_STATE.md`
built four quantitative rows on those numbers without that caveat. Also flagged: "0.3x
lower" is ambiguous between a factor of 0.3 and a 30% reduction; D1 and I chose the same
reading, and **one source read twice is not corroboration**.

---

## Corrections I accept but did not treat as blocking

- **The 0.140 g / 1.98 um result is not a finding.** Kramer Table 4, p.17, gives
  `u(m) = 1 g`, `u(D) = 0.1 mm`, `u(rho_w) = 0.4`, which propagate to about **7.6 g** on
  the half-submergence mass. The 0.140 g residual is **54x below** the paper's own
  uncertainty. It stays as a transcription guard; the phrase "something real" is withdrawn.
- **The `converged` flag is near-vacuous and I leaned on it.** Measured plateau block size
  is only 1 or 4 against `tau_int` up to 4.5, so blocks are still correlated where
  convergence is declared. `analyse()` now returns `converged_is_trustworthy`, requiring
  block size >= 4*tau. Measured on the canonical runs: **0 of 17 qualify**, against 17/17
  for the bare flag. **Every blocked SE I have reported is a lower bound.**
- **Mach at the largest drop is understated.** Kramer Figure 17b, p.15, shows a measured
  peak heave speed near 1.3 m/s, giving **Ma ~ 0.10**, against my linear estimate 0.0944.
  The committed assertion "stays below Ma 0.1" passed on the estimator most favourable to
  passing; it now reports both and asserts only that they straddle the limit.
- **Added-mass ratio 0.5 is unsourced and propagates** into the period, the wavelength,
  both wave speeds and every reflection window. `sphere_reference()` now returns the
  sensitivity: a33/m = 0.83 lengthens T_n about 10% and shortens every window in periods.
- **`c1sdf_box_g96` failed its settle gate** (`settle_gate_met false`, 900/900 frames) yet
  draws the best box drift ratio, 0.110x. So the drift ratio does not track the engine's
  own settle verdict. Also, my "no stationarity was demonstrated" was too strong: a
  velocity settle gate was applied and its per-run status is recorded.
- **Sphere particle count** was 606,814 in the manifest; replicating the seeding block gives
  **598,505** at `--h0-over-d 0.0` after the carve. My figure exceeded even the uncarved
  lattice ceiling. Cost impact 1.4%.
- **Throughput anchor is water-only** (8.94e6 recomputed; all-particle is 1.04e7) and I
  **double-counted startup**, adding 80-120 s on top of an anchor that already amortises
  six process startups.
- **Drift-ratio normalisation is partly loaded**: dividing by the error under test lets a
  large error mask a large drift. The conclusion survives and strengthens: on the actually
  published back-half window, g64's drift is **1.18x** the error claimed, i.e. it exceeds
  it. My criticism was understated, not overstated.

---

## What survived unchanged

- The STUCK mechanism, **every digit**: speed gate open frames 1-8, drift gate first at
  frame 37, zero overlapping frames, speed 0.128x its gate when drift clears.
- The Flyvbjerg-Petersen estimator and the pairwise transform, confirmed correct against
  the 1989 paper.
- All Kramer Table 1 arithmetic: 69.2180 N, 692.180 N/m, g bias -0.1018%, period bias
  +0.05096%, and the exact g-independence of the submerged fraction.
- The two-Steffen distinction, including the refusal to assert the five-author CMES title.
- `v_crit ~ sqrt(mu)`. The review's own challenge, that `N = W - B` should change it,
  **fails**: N is mu-independent so the ratio is unchanged. The reviewer recorded that
  against itself.
- The corpus scope discipline, 40 / 71 / 26, verified live.

---

## Two things the reviewer corrected against itself, worth carrying

1. **Its brief said the g96 SDF result hit the 900-frame settle cap and is less trustworthy
   than g64.** The artifacts contradict that: `c1sdf_sdf_g96.log` shows 776/900 with the
   gate met, `c1sdf_sdf_g64.log` shows 354 with the gate met, and the run that hit the cap
   is `c1sdf_box_g96`. **My ordering, g96 better supported than g64, is the one the data
   supports.** The reviewer flagged its own brief as stale rather than grading me against
   it. That stale statement is in the register and should be corrected there before it
   propagates; not my scope.
2. Its `N = W - B` challenge to the sqrt(mu) scaling, which it raised and then refuted
   itself.

---

## Status

Applied in this commit: B1, B2, B3, B5, B6, and the non-blocking code items. B4 is applied
to the manifest's criterion. B7 is recorded as a caveat; it cannot be closed without
publisher access to the corrigendum, which is a Josie or coordinator action.

Two further gaps the review raised that I have **not** closed: no R5 document tags claims
GENESIS/WARPMPM/BOTH (all are WARPMPM, but the tag is absent), and the sound-speed caveat
does not reference the completed sweeps, jobs 895330 and 895378.

The STUCK-to-SLIDE flip remains **INFERRED** until the brake sweep measures it.
