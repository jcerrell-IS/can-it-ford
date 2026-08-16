# D4: the settle length has a citable answer, and it is not a frame count

2026-08-16. Branch `claude/r5-physics`. No GPU used: every number here is measured on
existing local data with `simulation/r5_physics/blocking.py`.

Claim tags: **[read]** primary source this session, **[measured]** computed here from
local data, **[recalled]** from memory or the register, **[unreviewed]** no
physics-skeptic pass.

---

## 1. Why a frame count cannot be the answer

The project's current defence of any settle length is that a longer one changed the
answer, so the shorter one was wrong. 8 was refuted by 60, 60 by 250. **That argument has
no stopping rule.** 250 can fail exactly the same way, and nothing in the argument says
when to stop lengthening. It is an infinite regress presented as a convergence study.

The settling catalog D1 mined (`e9b3717`) says no universal frame count and no universal
force-settling threshold emerges, and that the defensible protocol is to detect and
exclude the transient, demonstrate stationarity for the reported observable, and attach
uncertainty from correlated samples **[recalled from D1's commit]**. Blocking supplies the
missing stopping rule, because the estimated standard error stops growing with block size.
That converts "we ran 250 frames" into "this observable is stationary over this window and
its standard error is X".

Method: Flyvbjerg and Petersen 1989, `10.1063/1.457480`, implemented in full. Jonsson
2018, `10.1103/PhysRevE.98.043304`, gives a formal automatic block-size criterion and I
**deliberately did not implement it**: the paper is paywalled and unread, and writing its
statistic from memory would repeat the Table 1 mistake. `plateau()` uses an explicitly
stated rule of my own that achieves the same property, no hand-chosen block size, without
claiming to be his test. Grossfield et al. 2019, `10.33011/livecoms.1.1.5067`, is the
best-practice reference (2019, not 2018). Bergmann et al. 2021, `10.1115/1.4052402`, is
the closest venue match. **None of the four is cited anywhere in this repository**
**[measured]**.

---

## 2. Result: the canonical runs are too short to locate their own transient

34 series across all 17 canonical runs, `vmag` and `dmag`, 91 recorded frames each
**[measured]**:

| quantity | value |
|---|---|
| blocking converged | **34 / 34** |
| transient exclusion point | **28 to 45 frames**, median 44 |
| series hitting the 50% search cap | **14 / 34 (41%)** |
| retained window after exclusion | 46 to 63 frames |
| SE inflation over the naive estimate | 1.00x to **2.13x**, median 1.77x |
| integrated autocorrelation time | 1.0 to 4.5 frames, median 3.1 |
| not stationary after exclusion | 18 / 34 |

> **RETRACTED 2026-08-16 by adversarial review. See `R5_PHYSICS_SKEPTIC_CORRECTIONS.md`
> B1.** This section originally read "**The 41% cap-hit is the finding** ... those runs are
> not long enough to demonstrate that their own transient has ended." **That does not
> follow.** On a synthetic pure linear ramp with no transient at all, `find_transient`
> returns the cap at n = 91 **and again at n = 400**: a 4.4x longer run hits the same cap,
> because the objective minimises retained variance and any trend rewards discarding more.
> A cap hit shows a trend, not a short run.
>
> Worse, the table above **pools two observables of different character**. Ten of the
> fourteen cap hits are `dmag`, a cumulative displacement magnitude, whose windowed mean is
> not a stationary target at all. It should never have been blocked.
>
> **Corrected, `vmag` only:** cap hits **4/17 (24%)**, not 41%; not stationary **6/17**,
> not 18/34. The failure mode is now documented in `blocking.py:find_transient` with its
> control table, and `analyse()` returns `transient_hit_cap`.
>
> **Also corrected:** "converged 34/34" is near-vacuous. Plateau block size is only 1 or 4
> against `tau_int` up to 4.5, so blocks remain correlated where convergence is declared.
> Requiring block size >= 4*tau, **0 of 17 qualify**. Every blocked standard error in this
> document is a **lower bound**.

The retained text below is kept for the record. The truncation rule is capped at discarding
half the series so it cannot "converge" by throwing everything away, and `drop = 45` is a
boundary rather than a measurement in every case where it appears.

**A precision that matters and that I nearly got wrong.** The 8 settle frames happen in
`StandingFloodScene.__init__` before recording starts, and the one-shot velocity kick is
applied at `sim_standing.py:240` immediately after them. So the 91 recorded frames begin
**at the kick**, and what this analysis measures is the **post-kick transient, not the
settle transient**. The two are different quantities. What is established is that the
post-kick transient occupies 31% to 49% of every recorded run. It bounds the settle
question only indirectly, and I am not going to claim otherwise.

Per-run `vmag`, the SLIDE-relevant observable, now carries a real error bar
**[measured]**. Relative blocked SE ranges from **1.48%** (`g48_m1609`) to **22.59%**
(`sweepV_g64_v2p0`). **FIVE** runs exceed 14%, not four as first written: `sweepV_g64_v2p0`
22.591%, `sweepD_g64_d0p45` 20.609%, `sweepD_g64_d0p35` 18.732%, `sweepV_g64_v2p5` 14.993%,
and **`sweepV_g64_v3p0` 14.573%**, which was omitted. Any ordering argument across those
runs has to clear those bars first, and per the retraction above each bar is a lower bound.

---

## 3. Result: the SDF path's two headline numbers are not equally solid

The project quotes the SDF-collider buoyancy validation as "7.3 to 7.7%", treating the
two grids as one range **[recalled]**. Blocking the `f_series` in the local
`data/coupling_validation/` artifacts, 160 samples each **[measured]**:

| run | published mean | published spread | blocked result | drift over retained window |
|---|---|---|---|---|
| `c1sdf_sdf_g64` | 28898.40 N | std 828.16 | **-7.6704% +/- 0.5422%** | **+4.392%**, 0.573x the claimed error |
| `c1sdf_sdf_g96` | 33577.11 N | std 101.68 | **+7.3449% +/- 0.0750%** | -0.531%, 0.072x |
| `c1sdf_box_g64` | 19432.45 N | std 1311.28 | -37.9124% +/- 1.3882% | +22.571%, 0.595x, **cap hit** |
| `c1sdf_box_g96` | 24639.37 N | std 157.24 | -21.3386% +/- 0.1627% | +2.355%, 0.110x |

Three things, in order of importance:

1. **The point estimates barely move.** 28897.7 against a published 28898.4. This is not
   a claim that the numbers are wrong. It is that they had no valid uncertainty.
2. **They now have one, and the naive route would have been wrong by ~2.7x.** SE inflation
   is 2.45x to 2.95x, tau 6.0 to 8.7 frames. The published `F_steady_tail_std` is a
   standard deviation, not a standard error of the mean; dividing it by sqrt(n) would have
   understated the true error by that factor.
3. **The two SDF grids are not equally trustworthy and the quoted range hides it.** At
   g96 the residual drift is 0.07x the error being claimed, which is negligible. At g64 it
   is **0.57x**: the "steady" force is still drifting by more than half the size of the
   discrepancy being reported. **The g96 number is well supported; the g64 number rests on
   a window that is still moving.** Citing "7.3 to 7.7%" as a single validated range
   asserts a symmetry the data does not have.

Caveat, stated because it bounds all of the above: my truncation rule minimises the
blocked standard error, which does **not** specifically target trend removal. A rule that
minimised drift would pick different points and could change the stationarity verdicts.
"Not stationary after exclusion" is conditional on my rule, and is reported with the drift
magnitude precisely so it is not read as a bare verdict.

---

## 4. The force-window question, answered both ways

**Asked:** if any reported force is a time-mean over a window containing the velocity
kick, that mean is not a physical steady value, because water entry and slamming have no
steady force.

**Answer: no reported force is such a mean.** Two independent reasons, both verified live
**[measured]**:

1. **`simulation/failure_modes.py` takes no time-mean at all.** Every reported force and
   acceleration is a peak: `peak_surge_force_n` and `peak_surge_accel_g` are
   `np.max(np.abs(...))` at `:223` and `:225`, and `max_surge_drift_m` is `np.max` at
   `:200`. There is no `mean` over any window in the file. So the published 16 SLIDE /
   1 STUCK verdicts and their magnitudes are already peak statistics, which is what the
   slamming literature asks for.
2. **The one genuine time-mean labelled "steady" is in a scene with no kick.**
   `validate_coupling_force.py:789`, `f_steady = float(tail.mean())`, operates on a
   **fixed** collider in still water with no inflow and no kick. The code says so itself
   at `:782-785`: for a fixed collider the added-mass transient does not arise because the
   body never accelerates.

**But the gap the same literature opens is real, and it is a different one.** Peak
statistics are supposed to come with repeat-run uncertainty and be reported as
distributions, envelopes or event statistics. **The 17 canonical runs are N = 1 each**, so
every peak is a single draw of a random variable whose spread is known to be large: the
determinism floor spans 0.52 to 1.69 m across three identical g128 runs **[recalled]**.
`peak_surge_force_n` therefore has no uncertainty attached and cannot acquire one without
repeats. That is a GPU cost, not an analysis cost, and it is queued behind the socket.

---

## 5. Queued behind the TACC socket, deliberately not started

- **Repeat runs for peak-statistic uncertainty** (section 4). Batch via `tacc_submit`,
  never idev: interactive burned 98.5 to 99.1% of Vista node-hours against every gated run
  with 95 of 184 ending in TIMEOUT **[recalled]**, and 629 SU remain.
- **Whether warpmpm's P2G is order-dependent.** Non-associative, order-dependent
  reductions can produce drift and can **alter discrete gates**, which is exactly the
  observed verdict flip at fixed config; `10.3390/app14020639` and
  `10.1016/j.parco.2019.04.002`. A GPU MPM P2G scatter is an unordered non-associative
  reduction, so the mechanism transfers on its face, but whether *this* engine's P2G is in
  fact order-dependent is a solver question that needs the GPU. **Not started tonight.**
- **Gate-pass frequency instead of pass/fail.** The same section recommends repeats report
  gate-pass *frequency*. That is a much better fit for the at-rest gate already known to be
  tunable, and it needs the same repeats.

---

## 6. The anchor citation for CLAUDE.md item 5 is absent, and it is the three-author paper

Item 5 is the g48/g64/g96 non-monotonicity, the project's most durable physics result, and
CLAUDE.md L-5 names "Steffen, Kirby and Berzins 2008" as its citable mechanism
**[recalled]**. Searched independently across all 9 `.bib` files and every `.tex` outside
`.claude/` **[measured]**:

```
10.3970/CMES.2008.031.107   0 files
10.1002/nme.2360            0 files
Steffen / steffen           0 files
```

"Steffen" appears only in prose: the register, `MULTIGEOM_VALIDATION_2026-08-11.md`,
`CLAUDE.md` and `scripts/check_claims.py`. **The mechanism behind the project's headline
result is cited in no bibliography.**

**Which paper, resolved rather than guessed. THE TWO-STEFFEN TRAP.** CLAUDE.md L-5 and the
register both name "Steffen" with **no identifier**, so this distinction is restated in
`R5_PHYSICS_BRAKE_STATE.md` section 7 as well, on the assumption that a future reader hits
the bare name before either document. These are two different 2008 papers by overlapping
author groups and merging them is a known trap:

- `10.1002/nme.2360` resolves to "**Analysis and reduction of quadrature errors in the
  material point method (MPM)**" **[read, via Unpaywall title lookup]**. Three authors,
  Steffen / Kirby / Berzins, matching L-5's naming. Quadrature error growing under grid
  refinement at fixed particles-per-cell **is** the mechanism item 5 needs. Closed access.
- `10.3970/CMES.2008.031.107` is the five-author implementation-choices paper
  (Steffen / Wallstedt / Guilkey / Kirby / Berzins, CMES). Unpaywall returns no record for
  it at all, so I could not confirm its title from a primary source tonight and have not
  asserted one.

**This work relies on `10.1002/nme.2360`.** Recorded here rather than fixed: the
bibliography is not in my scope.

---

## 7. Status

`blocking.py` is committed and reproducible. Regenerate with:

```
cd /Users/josie/can-it-ford/.claude/worktrees/r5-physics
<venv>/bin/python simulation/r5_physics/blocking.py \
  --metrics /Users/josie/can-it-ford/renders/yaris_render_s1/_incoming/*/metrics.csv \
  --columns vmag dmag --out <path>.json
<venv>/bin/python simulation/r5_physics/blocking.py \
  --forces /Users/josie/can-it-ford/data/coupling_validation/c1sdf_*.json --out <path>.json
```

The local corpus is **40 `metrics.csv` in the main checkout, 71 only if worktree
duplicates are swept in**, and 26 `rollout.npz` **[measured]**. Quoting 71 without that
scope repeats the CLAUDE.md item 13 problem.

Everything above is **[unreviewed]**: no physics-skeptic pass has run. Every simulation
number states the window it was measured over, and every non-converged or cap-hit result
is labelled rather than presented as a value.
