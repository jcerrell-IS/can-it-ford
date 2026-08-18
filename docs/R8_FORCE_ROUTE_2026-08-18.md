# R8-d3 force route: the no-forcing control, PRE-REGISTERED

Date 2026-08-18. Branch `claude/r8-force`. Engine **WARPMPM** throughout.

> **THIS SECTION IS WRITTEN AND COMMITTED BEFORE ANY ZERO-VELOCITY RUN IS SUBMITTED.**
> Sections 1 to 5 contain the prediction and the pass/fail rule. Section 6 onward is
> filled in after the runs return and does not modify anything above it. A control
> graded after seeing its own output is not a control, and this project has already
> retracted one result for exactly that shape (`R5_RESEARCH_FORCE_CONVERGENCE_2026-08-19.md`).

---

## 1. Why this control, and what it is a control ON

Item 2 of the retracted document's own section 5. It has never been run.

Every resolution claim in this project compares **forced** runs at different grids. No
run has ever been executed with the forcing switched off, so nobody knows what the scene
does at those same grids with no flow at all. If the hull still drifts at zero inflow,
and if that drift varies with resolution, then some fraction of the entire resolution
story is PIC reprojection noise rather than fluid loading.

### 1a. The retracted route, recorded so it is not rediscovered

`M * dv_cm/dt` **is not a force on the free-rigid material-8 path.** `v_cm` is
overwritten, not integrated. Verified this session by direct read of the pinned engine
`third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_utils.py`
(1588 lines, md5 `4aab09353f0c155e41eff9267a42d83d`):

| line | what is there |
|---|---|
| `:820`, `:913-916` | `p2g_particle` scatters into `grid_v_in` / `grid_m` via `atomic_add`. No material gate. |
| `:920-923` | `p2g_apic_with_stress`, the launcher. Gates on `particle_selection` only, never on material, so rigid material 8 is scattered with the water. |
| `:935-941` | `grid_normalization_and_gravity`: `v_out = grid_v_in/grid_m`, then `+ dt*g`. A mass-weighted water plus rigid **mixture**. |
| `:1369`, `:1380`, `:1402-1409` | `rigid_g2p_accumulate`, gated `particle_material[p] == 8`, gathers that mixed field back at each rigid particle with quadratic B-spline weights. |
| `:1411-1412` | the accumulation itself, `atomic_add` into `rigid_linear_mom` / `rigid_angular_mom`. |
| `:1434` | `rigid_body_integrate`: `v_cm_new = rigid_linear_mom[b] / M`. An **assignment**. No force term, no `+= F*dt/M`. |

**No force accumulator exists for the body on this path.** The `:913-916` and `:1411-1412`
citations are the corrected form; the originally circulated `:920-923` and `:1402-1409`
point at the launcher and at the gather loop respectively, which is defensible but less
precise.

**The retracted quantity is already shipped on disk.** `data/failure_modes_by_run.json`
carries `peak_surge_force_n`, `peak_vertical_force_n` and `peak_surge_accel_g` for all 17
canonical runs, written by `simulation/failure_modes.py:129-130`
(`accel = np.gradient(vel, t, axis=0)` then `force = mass_kg * accel`). That **is** the
`M*dv/dt` quantity. Register **D6f** already condemns `peak_surge_accel_g` by name as
"numerical, not physical".

> **This control is deliberately NOT graded with any of those three accessors.**
> The observable is displacement. See section 3.

Two corroborations that the on-disk quantity is the retracted one, both measured live:
the R6 repeat `peak_all` at g48 (32552 N) and the canonical `g48_m2337`
`peak_surge_force_n` (32551.7156 N) agree to six significant figures, as expected under
W3 (`seed=0` hard-coded, same initial condition, g48 spread 0.000 percent). Caveat: it is
not established whether R5's `peak_all` is the surge component or a vector magnitude, so
this is consistent with surge dominating, not proof of an identical definition.

### 1b. One quantity that survives, with a constraint that was not previously stated

The sign-only observation that all three mass arms are monotone **decreasing** in
`peak_surge_force_n` under refinement reproduces exactly. But measured live this session
from the same file and the same `mass * np.gradient(vel)` construction,
`peak_vertical_force_n` is **not monotone on any arm**:

```
m1100:  1149.36 -> 4116.50 -> 1978.83     (3.58x swing, non-monotone)
m1609:  1961.44 -> 3218.02 -> 2559.39     (non-monotone)
m2337:  3059.14 -> 1911.47 -> 3432.44     (non-monotone)
```

If the surge trend were dissipation from the rising substep count acting on the body, it
should appear in both components of the same trace. It does not. The sign-only
observation is therefore a property of the surge component of a numerical artifact, and
must never be stated without that constraint.

---

## 2. The runs. Exactly one token differs from the forced set.

The forced counterparts are the **R6 repeats**, 5 draws at each of four grids, all on
Vista and all read live this session. That set is chosen over the 17 canonical runs
because it spans all four grids with everything else identical, and because it is the
exact set the retracted analysis used.

As-run invocation, read live from `$WORK/r6_rep.sh`:

```
VENV=/work/11603/jcerrell0629/vista/.venv/bin/python
DRIVER=/work/11603/jcerrell0629/vista/render_s2/sim_standing.py
cd /work/11603/jcerrell0629/vista/mpm-engine
$VENV -u $DRIVER --mass 2337 --label rep_g${GRID}_m2337_$i --out $OUT/rep_$i \
      --depth 0.30 --velocity 1.5 --frames 90 --grid $GRID \
      --eta 1.0e-3 --floor-friction 0.55
```

The control changes **`--velocity 1.5` to `--velocity 0`** and nothing else. Same driver,
same mass, same depth, same frame count, same viscosity, same floor friction, same grids,
same repeat count.

Driver provenance: sha256 `5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45`,
stamped in every forced `.out` and re-stamped in every control run. That is the 389-line
as-run driver, byte-identical to the local copy at
`analysis/render_v1/as_ran_local_copies/sim_standing.py`. It is **not** the 564-line repo
copy at `renders/yaris_render_s1/sim_standing.py` (sha `4696c3b2...`), which R5's W6
retracted every line citation for. No state of branch `claude/r8-force` can reach the
Vista driver, so nothing in this worktree can contaminate the control.

### 2a. The precondition that makes this a clean control, verified before submitting

`sim_standing.py:150` sets `term_advective = max(velocity, 1e-6) / (0.5*dx)`, and the
substep rate is the max of the acoustic, viscous and advective terms. Measured from the
forced runs' own `SUBSTEP_TERMS` lines at all four grids:

| grid | dx | acoustic | advective | acoustic/advective | substeps |
|---|---|---|---|---|---|
| 48 | 0.196286 | 233.7190 | 15.2838 | 15.29 | 8 |
| 64 | 0.147215 | 311.6253 | 20.3784 | 15.29 | 11 |
| 96 | 0.098143 | 467.4379 | 30.5676 | 15.29 | 16 |
| 128 | 0.073607 | 623.2506 | 40.7568 | 15.29 | 21 |

The acoustic term dominates by 15.29x at **every** rung. At `--velocity 0` the advective
term falls to `1e-6/(0.5*dx)`, of order `1e-5`, so the rate is unchanged and the substep
count is **identical** to the forced run at the same grid: 8, 11, 16, 21.

**This holds dt and substeps fixed between control and forced at each rung.** That
matters because "substeps rise 2.6x across the ladder" is confound (a) of the three the
retraction lists as uncontrolled. The control does not remove that confound from the
forced runs, but it does mean the control and its forced counterpart share it exactly, so
any difference between them cannot be attributed to a substep-count difference.

### 2b. `--velocity 0` is NOT "no boundary condition", and must never be described as such

- `:161` one-shot kick `v[:n_water, 0] += velocity` adds exactly zero. Forcing removed.
- `:196` per-frame Dirichlet clamp `vw[band, 0] = self.velocity` **still fires every
  frame**, now holding the upstream slab at rest instead of at 1.5 m/s.

The BC machinery is identical and only its target value changes. That is the correct
control for isolating flow loading, and it is the reason the result is a floor on
reprojection noise **plus** clamp artifact, not on reprojection noise alone.

---

## 3. The observable. The retracted accessor is barred.

The observable is the hull's **surge displacement**, `final_disp_m[0]` on SURGE_AXIS 0,
with the `dx` / `vx` time series from `metrics.csv` as the supporting trace.

Not `peak_surge_force_n`. Not `peak_vertical_force_n`. Not `peak_surge_accel_g`. Those
are the quantity section 1a establishes is not a force, and grading a control with them
would reintroduce the retracted route through the back door.

Zero forcing should give zero surge drift. Whatever it actually gives is the noise floor
that every resolution claim in this project has been measured against without anyone
knowing its size.

### 3a. The forced anchors, measured live before the control was submitted

Surge component `final_disp_m[0]`, metres, 5 repeats per grid:

| grid | rep 1 | rep 2 | rep 3 | rep 4 | rep 5 | mean | spread (max-min) |
|---|---|---|---|---|---|---|---|
| 48 | 0.180809 | 0.181400 | 0.181193 | 0.181058 | 0.181467 | 0.1811854 | 0.000658 |
| 64 | 0.132721 | 0.131341 | 0.132231 | 0.132733 | 0.131416 | 0.1320884 | 0.001392 |
| 96 | 0.085329 | 0.085722 | 0.085480 | 0.085420 | 0.084643 | 0.0853188 | 0.001079 |
| 128 | 0.067610 | 0.068758 | 0.065881 | 0.066350 | 0.067707 | 0.0672612 | 0.002877 |

The forced surge drift falls monotonically, 0.1812 to 0.0673 m, a **2.69x drop** from g48
to g128. Successive changes: g48 to g64 **-27.1%**, g64 to g96 **-35.4%**, g96 to g128
**-21.2%**. That is "the resolution effect" expressed in the displacement observable
rather than in the retracted force.

Per W3, the spread across these 5 repeats is **GPU floating-point non-determinism in
atomic P2G accumulation**, not physical uncertainty: `seed=0` is hard-coded and no
`--seed` flag exists. It is a round-off floor, and it is the correct scale against which
to judge whether a zero-velocity drift is distinguishable from nothing.

---

## 4. PREDICTION, written before any control run exists

I predict the zero-velocity surge drift is **non-zero but small, and larger at coarser
grid**, for three stated reasons:

1. The scene is not symmetric in x. The vehicle sits at `x = 5.6530` in a domain of
   `lim = 9.4217` (domain centre 4.711), so it is downstream of centre with
   `downstream_wall = 8.6366`.
2. `:196` clamps an upstream slab to zero every frame, which is a one-sided momentum sink,
   not a symmetric condition.
3. PIC reprojection error per step grows with dx, and the coarse grids also carry fewer
   particles per cell, so reprojection noise should be largest at g48.

**Numeric prediction, mean over 5 repeats, absolute surge drift:**

| grid | predicted \|D0\| |
|---|---|
| 48 | <= 0.015 m |
| 64 | <= 0.012 m |
| 96 | <= 0.008 m |
| 128 | <= 0.006 m |

**and at every rung `|D0| / |D1| <= 0.08`**, that is, zero-velocity drift is at most 8
percent of the forced drift at the same grid.

I further predict the **sign of the trend matches** the forced runs (coarse gives more
drift than fine). That is the dangerous case, not the reassuring one: a control that
trends the same way as the signal is harder to dismiss than a large random one, and it is
why the pass rule below is written on the successive **changes** and not on the levels
alone.

If I am wrong in the direction that matters, `|D0|` will be of order 0.02 to 0.05 m, which
is a third to a half of the g96-to-g128 forced difference, and the resolution story does
not survive without re-derivation.

---

## 5. PASS / FAIL RULE, fixed before any control run exists

Let `D0(g)` be the mean zero-velocity surge drift at grid g over 5 repeats, and `D1(g)`
the mean forced surge drift at the same grid from the table in 3a.

**Level contamination** at a rung: `R(g) = |D0(g)| / |D1(g)|`.

**Trend contamination** across a successive pair: with
`dD1 = D1(g2) - D1(g1)` and `dD0 = D0(g2) - D0(g1)`,

```
C(g1->g2) = |dD0| / |dD1|
```

`C` is the fraction of the observed resolution effect that is reproduced **with the flow
switched off**. It is the number this control exists to produce.

| verdict | rule |
|---|---|
| **CLEAN** | `R(g) < 0.10` at every rung **and** `C < 0.10` at every successive pair. |
| **MARGINAL** | any `0.10 <= C < 0.35`. The resolution effect is real but its magnitude needs a stated uncertainty and cannot be quoted to two significant figures. |
| **CONTAMINATED** | any `C >= 0.35`. A third or more of the resolution effect is reproduced with no flow at all, and no resolution claim in this project survives without re-derivation, the g160 SLIDE-to-STUCK flip included. |

Two additional triggers, decided now:

- **Masquerade trigger.** If `sign(dD0) == sign(dD1)` at every successive pair **and**
  any `C >= 0.20`, report MARGINAL at minimum regardless of the level test, and say
  explicitly that the noise trends in the same direction as the signal.
- **Indistinguishable-from-nothing test.** If `|D0(g)|` is smaller than the forced repeat
  spread at that grid (0.000658, 0.001392, 0.001079, 0.002877 m at g48/64/96/128), the
  control drift at that rung is not distinguishable from round-off and is reported as
  such rather than as a measured drift.

**A rung that fails to run is reported as absent, never imputed.** If fewer than three
rungs return, the trend tests `C` are not computed at all and the level test `R` is
reported alone, with the missing rungs named.

---

## 6. RESULTS, the four pre-registered rungs

**Ran 2026-08-18 on Vista GH200 node c642-071 (job 920212, `gh-dev`), 20 runs, all rc=0.**
Total GPU cost about 7 minutes. Driver sha256 `5215c38b...` re-stamped in every run and
identical to the forced set. Every run reports `velocity_ms: 0.0`.

### 6a. The substep precondition held exactly, measured not assumed

`term_advective` fell to `1.0189e-05` at g48, which is `1e-6/(0.5*dx)` to five figures,
and the substep count came back **8 / 11 / 16 / 21**, identical to the forced runs at the
same grids. dt and substeps are held fixed between control and forced at every rung, so
no difference below can be attributed to a substep-count difference.

### 6b. Level test

Surge displacement `final_disp_m[0]`, metres, 5 repeats per grid:

| grid | per-rep control surge | D0 mean | D0 spread | D1 forced | R = \|D0\|/\|D1\| |
|---|---|---|---|---|---|
| 48 | +0.00231 +0.00202 +0.00196 +0.00249 +0.00263 | +0.002282 | 0.000673 | 0.181186 | **0.0126** |
| 64 | +0.00255 +0.00311 +0.00349 +0.00406 +0.00267 | +0.003177 | 0.001514 | 0.132089 | **0.0241** |
| 96 | -0.00065 +0.00010 -0.00057 -0.00087 -0.00087 | -0.000571 | 0.000978 | 0.085319 | **0.0067** |
| 128 | +0.00045 +0.00008 +0.00066 +0.00038 +0.00013 | +0.000338 | 0.000574 | 0.067261 | **0.0050** |

### 6c. Trend test, the number this control exists to produce

| pair | dD1 forced | dD0 control | C = \|dD0\|/\|dD1\| | same sign |
|---|---|---|---|---|
| g48 to g64 | -0.049097 | +0.000895 | **0.0182** | no |
| g64 to g96 | -0.046770 | -0.003748 | **0.0801** | yes |
| g96 to g128 | -0.018058 | +0.000909 | **0.0503** | no |

### 6d. VERDICT: CLEAN

`R < 0.10` at every rung (worst 0.0241) and `C < 0.10` at every successive pair (worst
0.0801). The masquerade trigger did **not** fire, because it requires the same sign at
every successive pair and the control's sign alternates (no, yes, no).

**At most 8.0 percent of the observed resolution effect is reproduced with the flow
switched off.** The remaining 92 percent or more is a response to the forcing. The
resolution effect in surge displacement is real, not PIC reprojection noise.

---

## 7. What the prediction got right, and what it got wrong

Recorded plainly, and the same way it would have been recorded had it gone the other way.

**RIGHT, the magnitude bound.** Every rung came in under its pre-registered ceiling, with
room to spare:

| grid | predicted \|D0\| | measured \|D0\| | margin |
|---|---|---|---|
| 48 | <= 0.015 | 0.002282 | 6.6x under |
| 64 | <= 0.012 | 0.003177 | 3.8x under |
| 96 | <= 0.008 | 0.000571 | 14x under |
| 128 | <= 0.006 | 0.000338 | 18x under |

The `R <= 0.08` prediction also held at every rung, worst measured 0.0241.

**WRONG, the trend direction.** I predicted the control drift would fall monotonically
with refinement, matching the forced trend's sign, and said explicitly that this was the
dangerous case. It did not. The measured control means are
`+0.002282, +0.003177, -0.000571, +0.000338`: **non-monotone and sign-changing.** g64 is
larger than g48, and g96 is negative. My stated reason for expecting monotonicity, that
PIC reprojection error grows with dx, is not what governs this quantity at these scales.

That error is in the project's favour, which is exactly why it needs stating rather than
quietly dropping. A control that trended with the signal would have been much harder to
dismiss. This one does not trend at all.

**A stronger statement than the rule required.** At g96 and g128 the mean control drift is
**smaller than the control's own repeat spread** (0.000571 against 0.000978, and 0.000338
against 0.000574). At those two rungs the zero-velocity surge drift is not merely small,
it is **not distinguishable from zero** at 5 repeats.

### 7a. A new measurement: the zero-forcing noise floor, which nobody had

The control's own run-to-run spread is the same size as the forced set's:

| grid | forced spread (m) | control spread (m) |
|---|---|---|
| 48 | 0.000658 | 0.000673 |
| 64 | 0.001392 | 0.001514 |
| 96 | 0.001079 | 0.000978 |
| 128 | 0.002877 | 0.000574 |

Per W3 the forced spread is GPU floating-point non-determinism in atomic P2G
accumulation, since `seed=0` is hard-coded and no `--seed` flag exists. The control
reproduces that floor to within a factor of about 1.1 at three of four rungs. **This is
the size of the thing every resolution claim in this project has been measured against,
and until now nobody had measured it.** It is roughly 0.6 to 1.5 mm of surge, against a
forced signal of 67 to 181 mm.

### 7b. Two side observations, both measured, neither load-bearing

- **The vertical settle is essentially unaffected by the flow.** Control z at g48 is
  -0.047847 against forced -0.047957, a 0.2 percent difference. The 4.8 cm of total
  displacement at g48 is almost entirely gravity and buoyancy settle, not flow response.
  The g48 z settle of about -0.048 m is the known floor-sinking defect (all three g48
  canonical runs fail gate P-3 with a negative z rise near -0.05 m); it is present with
  the flow switched off, so it is **not** flow-driven.
- **`--velocity 0` does not disable the clamp.** The `inflow=` counter stays at 3555 to
  3601 through all 90 frames, exactly as section 2b predicted. The upstream slab is being
  actively held at zero, not left free.

---

## 8. EXTENSION to g160 and g192: prediction, written before those runs return

The four rungs above are the pre-registered result and stand on their own. The following
is an **out-of-sample extension**, decided after seeing the four-rung result and therefore
labelled as such. It is not part of the pre-registration and must never be reported as if
it were.

Two reasons for running it: the measured runtime was about 30x cheaper than the dispatch's
estimate (10 to 39 seconds per run, not 10 to 20 minutes), and the g160 rung is where the
SLIDE-to-STUCK flip that motivated this control actually sits. Forced counterparts at both
grids completed with 5 repeats each, so the comparison stays held-fixed.

Forced anchors, measured before launching the extension: g160 surge **0.051449** m
(spread 0.003102, substeps 26), g192 surge **0.045338** m (spread 0.001760, substeps 32).
Note this makes the forced ladder monotone over all six rungs, 0.1812 / 0.1321 / 0.0853 /
0.0673 / 0.0514 / 0.0453 m, with successive changes -27.1 / -35.4 / -21.2 / -23.5 / -11.9
percent, that is, still falling but flattening.

**Extension prediction, fixed now:** `|D0| <= 0.001 m` at both g160 and g192, `R <= 0.02`
at both, and the mean control drift remains **smaller than its own repeat spread** at both,
continuing the g96 and g128 behaviour rather than the g48 and g64 behaviour.

**Extension pass/fail:** the same section 5 rule, applied to the six-rung ladder. If adding
these two rungs moves any `C` above 0.10, the four-rung CLEAN verdict is downgraded and
that is reported as the headline, not as a footnote.

### 8a. EXTENSION RESULT, g160 COMPLETE at 5 repeats. Out of sample, reported separately.

**g160 is the cleanest rung in the entire ladder, and it is the one that matters most.**

The g160 rung is where the SLIDE-to-STUCK flip sits, so it is where a contaminated-noise
result would have been most damaging. It is not contaminated:

| grid | n | D0 control | D1 forced | R | D0 spread | substeps ctl/forced |
|---|---|---|---|---|---|---|
| 160 | 5 | +0.0000104 | 0.051449 | **0.0002** | 0.000640 | 26 / 26 |

Per-rep surge at g160: `+0.000313  +0.000175  -0.000177  +0.000068  -0.000327`. **The sign
changes within a single grid**, twice, and the mean (0.0000104 m) is **sixty-one times
smaller than its own repeat spread** (0.000640 m). The drift is 0.0104 mm against a 51.4 mm
forced signal.

> **Reporting note.** An earlier revision of this section reported g160 at n=4 as
> `D0 = +0.000095, R = 0.0018`, which was correct for the four repeats then available and
> was labelled n=4. The fifth repeat returned `-0.000327` and moved the mean to
> `+0.0000104`, `R = 0.0002`. The n=4 figure is superseded, not retracted: it was an honest
> partial. The direction of the change is itself informative, because a mean that collapses
> by an order of magnitude when one more sample arrives is a mean that was never
> distinguishable from zero.

`R = 0.0002` is 500x below the 0.10 threshold. The extension prediction in section 8 said
`|D0| <= 0.001 m`, `R <= 0.02`, and mean below its own repeat spread. **All three held**,
this time including the directional part.

Trend test with g160 added: `C(g128 to g160) = 0.0207`. Five-rung verdict remains **CLEAN**
at every rung and every pair (worst R 0.0241 at g64, worst C 0.0801 at g64 to g96).

**The SLIDE-to-STUCK flip at g160 is not explained by zero-forcing noise.** Whatever drives
it, it is not PIC reprojection drift. This is the out-of-sample confirmation of the
pre-registered result, at the rung where a contaminated answer would have mattered most.

*(g192 was still running when this section was written. It is reported in section 8b if it
returned before the allocation expired, and recorded as absent if it did not. A truncated
set honestly labelled beats a complete set that did not run.)*

---

## 9. A CONFOUND THE RETRACTION COULD NOT CLOSE IS NOW CLOSED BY MEASUREMENT

`docs/R5_RESEARCH_FORCE_CONVERGENCE_2026-08-19.md` section 3 lists three confounds that
move monotonically with refinement, all uncontrolled. Confound (a), verbatim:

> **(a) Substeps rise 2.6x across the ladder.** PIC reprojection is dissipative, so the
> number of dissipative reprojections per recorded frame rises monotonically with
> refinement, in the same direction as every "converging" trend I reported. **Untested
> as the cause.**

**It is now tested, and it is not the cause.**

The control runs at `--velocity 0` returned substep counts of **8 / 11 / 16 / 21 / 26** at
g48 / g64 / g96 / g128 / g160, which are **identical** to the forced runs at the same
grids. That is not a coincidence and it was predicted before submitting, in section 2a:
`term_advective = max(velocity, 1e-6)/(0.5*dx)` collapses to about `1e-5` at zero velocity
while the acoustic term dominates by 15.29x, so the substep rate is unchanged.

Because the substep count is held fixed between control and forced at every rung, the
control carries confound (a) at **exactly the same strength** as its forced counterpart.
If the rising substep count were producing the apparent convergence, the control would show
the same trend, because it has the same substep ladder. It does not: the control's surge is
non-monotone, sign-changing, and at most 2.4 percent of the forced signal.

**Rising substep count is not what produces the resolution trend in surge displacement.**
Confound (a) can be marked closed.

> **CONFOUNDS (b) AND (c) ARE NOT CLOSED AND THIS SECTION DOES NOT TOUCH THEM.**
> A reader who sees one confound closed will assume the section is finished. It is not.
> **(b)** No level of this ladder resolves the flow depth by more than about 4.1 cells,
> against the roughly 10-particles-per-depth rule of thumb that register B3 and CLAUDE.md
> L-3 both record. Untouched by this control.
> **(c)** `realized_rho` varies 642.8 to 663.6 across the ladder, so the body's own mass
> is not constant along the refinement. Untouched by this control.
> Closing (a) narrows the field of explanations. It does not clear the ladder.

---

## 10. THE ZERO-FORCING SURGE FLOOR, a new named quantity

This project has never had a number for the size of its own numerical floor. It has one now,
and it is given a name here so it can be cited rather than re-derived.

> **Zero-forcing surge floor (ZFS).** The mean surge displacement `final_disp_m[0]` of the
> canonical standing-flood scene after 90 frames with `--velocity 0` and every other
> parameter held at the canonical values (m2337, depth 0.30 m, eta 1.0e-3, floor friction
> 0.55), over 5 repeats at fixed `seed=0`.

| grid | ZFS (m) | ZFS (mm) | ZFS repeat spread (mm) | forced signal (mm) | ZFS / forced |
|---|---|---|---|---|---|
| 48 | +0.002282 | 2.28 | 0.67 | 181.19 | 1.26% |
| 64 | +0.003177 | 3.18 | 1.51 | 132.09 | 2.41% |
| 96 | -0.000571 | 0.57 | 0.98 | 85.32 | 0.67% |
| 128 | +0.000338 | 0.34 | 0.57 | 67.26 | 0.50% |
| 160 | +0.000095 | 0.095 | 0.49 | 51.45 | 0.18% |

**The citable bounding statement:** the zero-forcing surge floor never exceeds **3.2 mm** at
any resolution tested, against a forced signal of 51 to 181 mm, and it falls **below 1 mm at
every grid of g96 and finer**. At g96, g128 and g160 the mean is smaller than its own repeat
spread, so at those three rungs it is **not distinguishable from zero at 5 repeats**.

Per W3 of the retraction, the repeat spread is GPU floating-point non-determinism in atomic
P2G accumulation, not physical or model uncertainty: `seed=0` is hard-coded and no `--seed`
flag exists. The control's spread matches the forced set's to within about 1.1x at three of
four rungs (0.00067 against 0.00066, 0.00151 against 0.00139, 0.00098 against 0.00108),
which is what a shared round-off origin predicts.

**What this is for.** Any future claim in this project of the form "displacement changed by
X between resolutions" can now be checked against the floor. A claimed effect smaller than a
few millimetres of surge is inside the numerical floor and is not a result.

---

## 11. THE g48 P-3 FLOOR-SINK IS NOT FLOW-DRIVEN. Answered by control.

CLAUDE.md August 4 audit item 7 records that **all three g48 canonical runs fail gate P-3**
with a negative z rise near -0.05 m, that is, the hull sank into the floor plane. The cause
has been open.

The control answers it, because the control has no flow:

| | control (velocity 0) | forced (velocity 1.5) | difference |
|---|---|---|---|
| g48 z displacement, **5-repeat mean** | **-0.047847 m** | **-0.047920 m** | **0.15 percent** |
| g48 z, control repeat spread | 0.000077 m | 0.000049 m | |

> **Corrected 2026-08-18, same session.** An earlier revision of this row quoted the forced
> value as **-0.047957 m**, which is forced **repeat 1**, not the 5-repeat mean. The
> conclusion is unchanged and the corrected gap is 0.15 percent rather than 0.2, but
> comparing a single draw against a mean is precisely the error this document is about, and
> it is recorded here rather than silently fixed. Both figures above are now 5-repeat means,
> and the difference between them (0.000073 m) is comparable to the control's own repeat
> spread (0.000077 m), which makes the agreement stronger, not weaker.

**The g48 floor-sink is present at full strength with the flow switched off.** It is a
gravity, buoyancy and floor-boundary effect, not a hydrodynamic one. Switching the forcing
off changes it by two parts in a thousand.

Two consequences:

1. Any explanation of the g48 P-3 failure that invokes flow loading, drag, or momentum
   transfer from the water is refuted by this control. The remaining candidates are the
   floor boundary condition, the buoyancy or density treatment, and the g48 resolution
   itself, all of which are active with no flow at all.
2. The sink is resolution-dependent and largely disappears with refinement: mean control z
   is -0.047847 at g48 but -0.002913 at g64, -0.003023 at g96 and -0.000003 at g128. It is a
   coarse-grid artifact, and it is the coarse grid rather than the flow that produces it.

**THE SHORTLIST, for whoever takes this.** CLAUDE.md August 4 audit item 7 currently records
the cause of the g48 P-3 failure as open. This control does not close it, but it removes a
whole class of explanations and leaves exactly three candidates, all of which are active with
no flow at all:

1. **The floor boundary condition.** The floor plane at friction 0.55, and the restitution
   0.05 that `_apply_rigid_restitution` applies, are live in every one of these runs.
2. **The buoyancy or density treatment.** On the material-8 path the body adopts a
   mass-weighted grid velocity and no buoyant force is integrated, so density cannot drive
   motion (section 1a). A hull at realized_rho about 643 in water should not sink.
3. **g48 itself.** dx at g48 is 0.196286 m, which is larger than the hull's measured ground
   clearance, so the force-bearing feature is not resolved at all at that grid.

This also means gate P-3 at g48 is not testing what its name suggests at that resolution.

---

## 12. CAN `sdf_wrench` CARRY A FORCE-VS-RESOLUTION CURVE? Verdict: yes in principle, no today.

### 12a. What it is, and what it accumulates. Read directly from the pinned engine.

`core/solver.py:354-361`, verbatim contract:

```
force  = sum m*(v_free - v_new) / dt
torque = sum (x - center) x impulse / dt      (about the collider centre, world frame)
```

returned as `{'force': (3,), 'torque': (3,)}`. **This is a genuine force.** It is the
momentum the collider removed from the material per unit time, that is, the Newton third-law
reaction, accumulated on the grid. It is not a differentiated velocity trace.

`kernels/mpm_solver_warp.py:856` (`mass_np[b] = float(m_b.sum())`) is the rigid mass sum,
verified live, confirming the corrected citation already recorded as closed in CLAUDE.md.

### 12b. THE DECISIVE POINT: it is on a different code path from every published run

`sdf_wrench` belongs to the **SDF collider** path (`add_sdf_collider` at `:324`). All 17
canonical runs, all 20 R6 repeats, and all 24 control runs reported above use the
**free-rigid material 8** path, which has no force accumulator (section 1a).

`simulation/coupling_force/coupler.py:4-8` states the same thing independently and its
engine citations check out against the pinned source:

> "The engine's free-rigid path (material 8) never forms a force. Per step it gathers the
> mass-weighted grid velocity at each rigid particle and assigns
> `v_cm = rigid_linear_mom / M` (kernels/mpm_utils.py:1434, with M from
> kernels/mpm_solver_warp.py:856)."

So a force-vs-resolution curve built from `sdf_wrench` **would not describe the runs this
project has published.** It would describe a different scene, on a different coupling
architecture. That is not a reason against building it, but it is a reason it can never be
retrofitted as validation of the existing ladder.

### 12c. It is already implemented, and it must not be rebuilt

`simulation/coupling_force/` is committed and contains the full partitioned explicit FSI
loop. The per-tick contract at `coupler.py:142-175` is:

```
reset_sdf_force(h) -> step(dt) x substeps_per_pose -> sdf_wrench(h, tick_dt)
   -> integrate Newton-Euler -> set_sdf_pose(h, center=x_cm, quat, velocity, omega)
```

`realism_track/FINDINGS.md:152-160` records this explicitly: "This is already implemented
and must not be duplicated." Its `test_rigid_body.py` reports 14 analytic checks passing,
but those validate **the integrator, not the fluid coupling**.

### 12d. Why the answer is "no today": the force itself is not yet trustworthy in this regime

Measured, from `realism_track/coupling_accuracy.json` and `FINDINGS.md:9-21`, read live:

| regime | collider | g64 error vs analytic | g96 error vs analytic |
|---|---|---|---|
| rung (a), FULLY submerged, still | sdf | **-7.67%** | **+7.28%** |
| rung (a), fully submerged, still | box | -37.91% | -21.28% |
| rung (b), PARTIALLY submerged | sdf | **-18.9%** | **+115.0%** |

The flooded-vehicle case is partial submersion, and there the force is currently **refuted**,
not validated: the error swings 134 percentage points between two grids and the body sinks
at one while rising at 4 g at the other. `FINDINGS.md:21` is explicit: "Do not quote
-7.67%/+7.28% as a coupling-accuracy figure for a floating vehicle."

**A quantity whose own error against an analytic reference swings by 134 points across two
grids cannot be the ordinate of a convergence study.** The convergence of the measurement
must be established before the measurement can establish convergence of anything else.

Root cause of the rung (b) failure is recorded and is not exotic: the water was never settled
(`rung_b_coupled.py:83` advanced one substep per iteration where the reference advances one
frame under a quiescence gate; the 900 that ran were 23 percent at g64 and 7.2 percent at g96
of what the gate required), plus a comparison that was never like-for-like (frac 1.0 against
frac 0.5187). Fixed in `79fec32`, **not re-run**.

### 12e. What building the curve would actually require

1. **Re-run rung (b) with the `79fec32` settle fix at three or more grids.** The fix is
   committed and unexercised. Until it runs, there is no trustworthy force at any resolution.
2. **Three resolutions minimum, with successive percentage changes**, per the research
   review's recommendation 3, declaring convergence only below a stated tolerance of 5 to 10
   percent. Two points that cross zero (-7.67 to +7.28) are not a convergence curve. *(That
   review is a secondary, AI-generated source and is cited here for positioning only.)*
3. **A time-averaged observable over a demonstrated-stationary window, with a GCI**, not an
   instantaneous peak (Syamlal, Celik and Benyahia 2017, 10.1002/AIC.15868; Celik et al 2007,
   10.1115/1.2960953, already in the paper bib). This project has the tool for the stationary
   window, `analysis/stationarity.py`, and the retraction's W2 shows what happens without it:
   the discarded region held the quantity being reported in 20 of 20 runs.
4. **Fix the manifest provenance gap first.** `canitford_git_commit`, `grid_density`,
   `mesh_sha256`, `solver_git_sha` and `vehicle_mass` are absent from all 20 R6 manifests.
   A convergence curve whose rungs cannot be tied to a driver and a mesh is not auditable.
   *(Recorded in the retraction section 6; not independently re-verified here.)*

### 12f. The five traps, each checked against source rather than restated

| # | trap | status, verified live |
|---|---|---|
| 1 | **wrench-dt.** `sdf_wrench` divides by whatever `dt` it is handed, so passing the substep dt instead of the tick duration inflates the force by exactly the substep count, plausibly and silently. | **CONFIRMED**, `solver.py:361` `return {"force": f / dt, ...}`. The existing coupler gets it right: `coupler.py:151` passes `cfg.dt * cfg.substeps_per_pose`. |
| 2 | **The accumulator is never auto-zeroed.** A naive read returns the run-to-date total. | **CONFIRMED**, the only zeroing in `solver.py` is inside the explicit reset methods at `:298-299`, `:350-351` and `:417`. Nothing in `step()` clears it. The coupler gets it right at `:147`. |
| 3 | **Quaternion order differs inside one file.** | **CONFIRMED**, `add_cup` at `:256` defaults `(1,0,0,0)` and `:262` documents "``quat`` uses wxyz order", while `add_sdf_collider` at `:324` defaults `(0,0,0,1)`, xyzw. The coupler uses xyzw at `:168`, consistent with the SDF path. |
| 4 | **COM offset.** | **THE CARRIED FORM DOES NOT VERIFY HERE, AND IS WITHDRAWN.** The claim names `RigidBody6DOF` raising `NotImplementedError` on non-zero COM offset. `RigidBody6DOF` **does not exist in this repo** (searched `simulation/` and `analysis/`), and the only `NotImplementedError` in `coupling_force/` is `inflow_outflow.py:123`, about a log-law roughness height. The **verifiable** form: `sdf_wrench` reports torque about the **collider centre** (`:356-357`), while `rigid_body.py:64-84` computes inertia about the **centre of mass**. `coupler.py:172` sets `center=tuple(self.state.x_cm)`, so the two coincide **only if the SDF's own geometric origin is the COM**. `coupler.py` contains no mention of that reconciliation. It is an **unguarded assumption**, not a raised error, which is more dangerous than the carried form suggested. |
| 5 | **periodic_x.** | **CONFIRMED**, `add_cdf_collider` guards it at `:379-380` with an explicit `raise NotImplementedError`; `add_sdf_collider` at `:324-337` has **no equivalent guard**. Combining `periodic_x` with an SDF vehicle fails silently. |

### 12g. Verdict

**`sdf_wrench` is the correct independent force measurement and it is the only real force on
a body available in this engine.** It should be the basis of any future force-convergence
work, and the machinery is already written.

**It cannot carry the curve today**, for three reasons, in order of how hard they are to fix:
its accuracy in the partial-submersion regime is currently refuted at -18.9 and +115.0
percent and must be re-established after the unexercised `79fec32` settle fix; only two
resolutions exist where at least three are needed; and it measures a different coupling
architecture from every run this project has published, so it can extend the work but can
never retroactively validate the existing ladder.

**What it is NOT is a substitute that lets `M*dv/dt` back in.** The two are not alternative
estimates of the same thing. `M*dv_cm/dt` on the material-8 path is `M/dt` times the
difference of two PIC reprojections of a blended field, and no averaging, smoothing or
window choice converts it into a force.

---

### 8b. EXTENSION RESULT, g192. THE LADDER IS CLOSED END TO END.

g192 returned before the allocation expired. **All three parts of the section 8 prediction
held again**, and the six-rung ladder is now complete.

| grid | n | D0 control | D1 forced | R | D0 spread | substeps ctl/forced |
|---|---|---|---|---|---|---|
| 192 | 5 | +0.000108 | 0.045338 | **0.0024** | 0.000380 | 32 / 32 |

Per-rep at g192: `+0.000143  -0.000036  -0.000068  +0.000187  +0.000312`. Sign changes
within the grid again, and the mean is 3.5x smaller than its own spread.

**COMPLETE SIX-RUNG RESULT, four rungs pre-registered plus two out of sample:**

| grid | D1 forced (m) | D0 control (m) | R | pair | C |
|---|---|---|---|---|---|
| 48 | 0.181186 | +0.002282 | 0.0126 | g48 to g64 | 0.0182 |
| 64 | 0.132089 | +0.003177 | **0.0241** | g64 to g96 | **0.0801** |
| 96 | 0.085319 | -0.000571 | 0.0067 | g96 to g128 | 0.0503 |
| 128 | 0.067261 | +0.000338 | 0.0050 | g128 to g160 | 0.0207 |
| 160 | 0.051449 | +0.0000104 | 0.0002 | g160 to g192 | 0.0159 |
| 192 | 0.045338 | +0.000108 | 0.0024 | | |

**VERDICT ACROSS ALL SIX RUNGS: CLEAN.** Worst R is 0.0241 at g64, worst C is 0.0801 at
g64 to g96, both under the 0.10 threshold. The masquerade trigger does not fire: the
control's sign alternates across the pairs (no, yes, no, yes, no).

**At most 8.0 percent of the resolution effect in surge displacement is reproduced with the
flow switched off, at any rung of the ladder from g48 to g192.** At four of the six rungs
the control drift is not distinguishable from its own repeat noise.

The pre-registered verdict is the four-rung one. The two extension rungs are out of sample
and are reported here as confirmation, not as part of it.

---

## 13. UNIT 2: THE UNEXERCISED SETTLE FIX, EXERCISED. THE SWING NARROWS BY 94 PERCENT.

Section 12d concluded that `sdf_wrench` cannot carry a force-convergence curve today because
its own error against analytic buoyancy swings 134 percentage points across two grids in the
partial-submersion regime. Section 12e's first prerequisite was to exercise the `79fec32`
settle fix, which was committed and had never been run. **It has now been run.**

### 13a. What was changed, and what was held

Exactly one thing changed against the runs that produced -18.9 and +115.0 percent: the
settle. `79fec32` replaced `rung_b_coupled.py:83`'s hand-rolled `tank.solver.step(tank.dt, 1)`
loop, one **substep** per iteration, with `settle_pinned(tank, settle_frames)`, one **frame**
per iteration under a quiescence gate, which is the same call the rung-(a) reference uses.

Everything else was left at the committed defaults: `--relax 1.0`, `--submersion-frac 0.80`,
`--depth-cells 18`, `--rho-box 600`, `--steps 60`, `--settle 900`. Harness shipped from this
worktree to a fresh Vista directory, md5 `8f01a66d88b4134851fd90926fa4f0d0`, verified
identical to the local copy. No existing Vista checkout was modified. Smoke-tested first at
`--settle 4 --steps 4`, which correctly returned `VALIDITY FAIL` and meaningless numbers, as
the fix commit said it should.

### 13b. THE RESULT: the swing collapses and the sign inversion disappears

| | g64 | g96 | grid-to-grid swing |
|---|---|---|---|
| **BEFORE**, settle as substeps (job 3361315) | **-18.9%** | **+115.0%** | **133.9 points** |
| **AFTER**, settle as frames (`79fec32`) | **-15.77%** | **-24.26%** | **8.5 points** |

**The swing narrows by 93.7 percent.** More important than the magnitude: **the sign
inversion is gone.** Before, the body sank at one grid and rose at 4 g at the other. Now both
grids under-predict analytic buoyancy, by 16 and 24 percent, which is a single consistent
bias rather than a contradiction.

Measured ratios, read from the run logs: g64 `RATIO measured/analytic (median) = +0.8423`,
g96 `= +0.7574`.

**This is the answer to the question section 12d left open, and it points the favourable way.**
An unsettled tank was doing most of the damage, exactly as `FINDINGS.md` diagnosed but never
demonstrated.

### 13c. IT IS STILL NOT A VALID MEASUREMENT, AND THAT MUST NOT BE SOFTENED

The harness declares both runs invalid, by its own criteria, and it is right to:

1. **The added-mass guardrail fires at both grids.** `added_mass_ratio` is **0.9353** at g64
   and **1.0628** at g96, against `coupler.py`'s own `warn_added_mass = 0.5`, with
   `relax = 1.0` so no mitigation is active. Both runs print
   `VALIDITY FAIL: ... Numbers below are NOT a valid coupling-accuracy measurement.`
   This is structural, not incidental: a floating body sits at ratio exactly 1.0 by identity,
   so the flooded-vehicle case lives permanently in the regime the module warns about. The
   blocker has **moved** from the settle to the added-mass ratio; it has not been removed.
2. **g96 did not meet its settle gate even at the cap.** `frames_run=900/900 gate_met=False`,
   `vmax_final=1.237`. g64 met the gate at `356/900`. So g96 is still under-settled and its
   -24.26 percent is an upper bound on how good it gets, not a converged value. The
   `--settle` cap needs raising above 900 frames for g96 specifically.
3. **The refinement is still not controlled.** `frac_realized` is **0.5612** at g64 and
   **0.6377** at g96, against a target of 0.80. The two grids are not at the same submersion,
   so this remains a comparison of two different physical configurations. Until
   `frac_realized` matches across grids, a difference between them cannot be attributed to
   resolution.

### 13d. Revised verdict on the `sdf_wrench` route

Section 12g said "yes in principle, no today". That stands, but the reason has changed and
the route is materially more promising than it looked:

- **What was refuted tonight:** the belief that the partial-submersion force is wildly
  grid-inconsistent. It is not. The 134-point swing was an artifact of an unsettled tank, and
  with the settle fixed the two grids agree to 8.5 points and share a sign.
- **What now blocks it:** the added-mass ratio sitting at 0.94 to 1.06 with no mitigation, an
  under-settled g96 at the current cap, and an uncontrolled `frac_realized` between grids.
  All three are addressable, none is addressed.
- **What it would take next**, in dependency order: raise the g96 settle cap until the gate
  is met; match `frac_realized` across grids; then, and only then, a third resolution and a
  time-averaged observable with a GCI per section 12e items 2 and 3. Under-relaxation is
  **not** the remedy for the added-mass problem: `FINDINGS.md` records that it makes the
  error monotonically worse at both grids, so the scheme itself is the thing to revisit.

**Honest framing of what this unit is worth.** It converts a route that was closed on a
134-point inconsistency into one that is open pending three named, tractable fixes. It does
not produce a force-convergence curve and does not claim one. Two grids that agree to 8.5
points are still two grids, and the research review's recommendation 3 asks for at least
three with successive changes below a stated tolerance.

### 13e. Provenance

Runs executed 2026-08-18 on Vista GH200 node c642-071 (job 920212, `gh-dev`), both `rc=0`.
Logs and JSON at `$WORK/r8_rungb/rungb_fixedsettle_g{64,96}.{log,json}`. Engine **warpmpm**,
SDF-collider path, which is **not** the material-8 path the 17 canonical runs use. Nothing in
the repo was modified by these runs and no existing Vista checkout was touched.


---

## 14. THE CONTROL IS CLEAN IN SURGE ONLY. IN THE VERTICAL CHANNEL, ESSENTIALLY NOTHING SURVIVES THE FLOW BEING REMOVED.

**Added 2026-08-18 after the six-rung result was written up. It corrects the wording of the
headline and it generalises section 11 from a g48 curiosity into a statement about the whole
vertical channel.**

Every verdict in sections 6, 8a and 8b is computed on `final_disp_m[0]`, the surge axis, and
is correct as stated **for that component**. The same 30 control and 30 forced runs also carry
y and z, and those were left latent in the data rather than reported. They should not have
been.

### 14a. All three components, same data, same 5-repeat means

| grid | R in **x (surge)** | R in **y** | R in **z** |
|---|---|---|---|
| 48 | 0.0126 | 0.3744 | **0.9985** |
| 64 | 0.0241 | 0.1129 | **1.0254** |
| 96 | 0.0067 | 0.1670 | **0.9985** |
| 128 | 0.0050 | 1.4048 | 1.2784 *(noise over noise, see 14c)* |
| 160 | 0.0002 | 0.8374 | 0.4807 *(noise over noise)* |
| 192 | 0.0024 | 1.1852 | 5.7802 *(noise over noise)* |

Pairwise trend contamination:

| pair | C in **x** | C in **y** | C in **z** |
|---|---|---|---|
| g48 to g64 | 0.0182 | 0.8570 | **0.9968** |
| g64 to g96 | 0.0801 | 0.0029 | 0.5888 |
| g96 to g128 | 0.0503 | 0.6982 | **0.9983** |
| g128 to g160 | 0.0207 | 3.8541 | 0.3351 |
| g160 to g192 | 0.0159 | 0.0478 | 0.0210 |

### 14b. What this means, stated plainly

**In z, at every rung where the vertical channel is doing anything at all, the control
reproduces the forced result to within about 0.2 to 2.5 percent.** `R` is 0.9985, 1.0254 and
0.9985 at g48, g64 and g96, and the pairwise `C` is 0.9968 and 0.9983. That is not
"contamination" in the sense the pass/fail rule was built to detect. It is the finding that
**vertical motion in this scene is not hydrodynamic at all.** Switching the inflow off changes
it by essentially nothing.

This generalises section 11. What was reported there as "the g48 P-3 floor-sink is not
flow-driven" is not specific to g48 and not specific to the P-3 gate: **the entire vertical
channel is flow-independent at every rung where it has any magnitude.** The g48 case is simply
the one where the magnitude is largest (48 mm rather than 3 mm) and therefore the one where a
gate noticed.

In y the picture is neither clean nor uniform: `R` spans 0.1129 to 1.4048 and `C` reaches
3.8541. y displacements are small (control means 0.6 to 3.9 mm) and no claim is made from
them beyond the negative one: **the control is not clean in y either, and any future
lateral-displacement claim must be checked against a control before it is believed.**

### 14c. The exclusion, stated so it cannot be misread as a result

At g128, g160 and g192 the z displacements are **under 15 microns on both arms**
(control means -0.000003, -0.000007, -0.000006 m). The `R` values there (1.2784, 0.4807,
5.7802) are a ratio of one near-zero number to another and carry no information. **Nothing is
claimed from those three cells.** They are shown only so the table is not silently truncated
at the point where it stops meaning anything.

### 14d. The corrected headline

The sentence that must be used, replacing any component-free version:

> **At most 8.0 percent of the resolution effect IN SURGE DISPLACEMENT is reproduced with the
> flow switched off, at any rung from g48 to g192. In the VERTICAL channel essentially 100
> percent is reproduced, so vertical motion in this scene is not hydrodynamic at all.**

The CLEAN verdict is unaffected: it was always defined on surge, in section 3, and the
pass/fail rule in section 5 names `final_disp_m[SURGE_AXIS]` explicitly. What was wrong was a
component-free restatement of it on the shared cross-session board, which has been corrected
there by a dated correction row rather than by editing the original.

### 14e. Distinguishability in surge, restated in sigma

The "not distinguishable from repeat noise" claim in sections 6b and 8b is made precise here.
Control mean divided by the control's own sample standard deviation, 5 repeats:

| grid | mean (m) | sd (m) | \|mean\|/sd |
|---|---|---|---|
| 48 | +0.002282 | 0.000292 | **7.82 sigma** |
| 64 | +0.003177 | 0.000621 | **5.12 sigma** |
| 96 | -0.000571 | 0.000401 | 1.42 sigma |
| 128 | +0.000338 | 0.000237 | 1.42 sigma |
| 160 | +0.000010 | 0.000261 | **0.04 sigma** |
| 192 | +0.000108 | 0.000159 | 0.68 sigma |

So the zero-forcing surge drift is **real and resolvable at g48 and g64** (7.8 and 5.1 sigma,
2.3 and 3.2 mm) and **not distinguishable from zero at g96 and finer** (all under 1.5 sigma).
The floor is not uniformly "noise": it is a small but genuine coarse-grid drift that vanishes
under refinement.

### 14f. Independent re-derivation

The surge table in sections 6 and 8b was re-derived independently by the coordinator from the
same 30 control and 30 forced `SUMMARY` lines, without using this document's tables, and
reproduced `R = 0.0126, 0.0241, 0.0067, 0.0050, 0.0002, 0.0024` and
`C = 0.0182, 0.0801, 0.0503, 0.0207, 0.0159` to every digit, along with the 3.177 mm maximum
of the Zero-Forcing Surge floor. The z and y decomposition in this section was raised by that
same re-derivation and was then computed again here from the raw files before being written
down. Two independent parses of one dataset is not two datasets, and this is recorded as
arithmetic agreement, not as corroboration of the physics.

---

## 15. THE g96 SETTLE CAP LADDER. IT PARTLY OVERTURNS SECTION 13, AND THE CORRECTION IS AGAINST MY OWN FAVOURABLE NUMBER.

Section 13 left one question and section 13d named it first in the dependency order: **raise
the g96 settle cap until the gate is met.** Done, 2026-08-18, Vista GH200 c642-071, job
920212, ascending caps at g96 with everything else held at the section 13a defaults.

### 15a. The gate IS reachable at g96, and it needs 2.9x the cap that was in use

| cap (frames) | frames_run | gate_met | vmax_final | frac_realized | added_mass_ratio |
|---|---|---|---|---|---|
| 900 | 900/900 | **False** | 1.237 | 0.6377 | 1.063 |
| 1800 | 1800/1800 | **False** | 1.018 | 0.6459 | 1.077 |
| 2700 | **2596**/2700 | **TRUE** | 0.623 | 0.6498 | 1.083 |

`vmax_final` falls monotonically and the quiescence gate trips at **2596 frames**, which is
**2.9x the 900-frame cap** previously used and **7.3x the 356 frames g64 needed**. So
`gate_met=False` at g96 was an artifact of the cap choice after all, not a property of the
configuration. The settle length **is** tunable at g96; it is simply far longer than anyone
had allowed for.

### 15b. AND THE MEASURED FORCE GETS WORSE THE MORE YOU SETTLE

| cap | gate_met | RATIO measured/analytic | error |
|---|---|---|---|
| 900 | False | 0.7574 | -24.26% |
| 1800 | False | 0.6790 | -32.10% |
| 2700 | **TRUE** | **0.5431** | **-45.69%** |

The error grows monotonically with settle length and is **worst at the converged settle.**
`gate_met=True` does **not** mean the measured force has converged: the trend is still moving
when the gate trips.

### 15c. THE CORRECTION TO SECTION 13, AND IT IS AGAINST MY OWN HEADLINE

Section 13b reported the post-fix swing as **8.5 points** and a **93.7 percent** reduction.
**That comparison was not like-for-like and the figure is withdrawn.** It paired g64 at a
**met** gate (356/900) against g96 at an **unmet** gate (900/900). It is the same defect the
original rung-b work was criticised for, in a new place, and I introduced it.

| comparison | g64 | g96 | swing |
|---|---|---|---|
| BEFORE, both unsettled, settle counted in substeps | -18.9% | +115.0% | **133.9 pts**, sign inversion |
| WITHDRAWN, g64 gate met against g96 gate NOT met | -15.77% | -24.26% | 8.5 pts |
| **CORRECT, both gates met** | **-15.77%** (356 frames) | **-45.69%** (2596 frames) | **29.9 pts** |

**The honest result: the swing narrows from 133.9 points to 29.9 points, a 77.7 percent
reduction, not 93.7 percent.** What survives unchanged from section 13b is the qualitative
half, and it is the more important half: **the sign inversion is gone.** Both grids now
under-predict analytic buoyancy rather than one sinking while the other rises at 4 g.

### 15d. What this does to the section 12 and 13 verdict

It moves it back toward the pessimistic reading, and the three blockers are now better
characterised rather than removed:

1. **Added-mass is confirmed structural and settle-independent.** `added_mass_ratio` is
   1.063, 1.077, 1.083 across the cap ladder, that is, it **rises slightly** with better
   settling and never approaches the 0.5 warn threshold from below. `VALIDITY FAIL` fires at
   every cap. Settling harder does not help and cannot.
2. **`frac_realized` does not converge to the same value on the two grids.** It creeps
   0.6377, 0.6459, 0.6498 at g96 while g64 sits at 0.5612, so the two grids settle to
   **different submersion fractions**, both short of the 0.80 target. This is therefore
   **not** a settle artifact and will not be fixed by longer settling. Until it is understood,
   a g64-to-g96 difference cannot be attributed to resolution, and section 13c item 3 is
   upgraded from a caveat to a blocker in its own right.
3. **The force has not converged even at a met gate**, per 15b, so a single converged-settle
   run is not yet a defensible rung of any convergence curve.

**Revised bottom line on the `sdf_wrench` route.** Section 13d called it "open pending three
named tractable fixes". One of the three (settle length at g96) is now shown tractable but
much more expensive than assumed. The other two are worse than they looked: added-mass is
structural, and the submersion mismatch is not a settle artifact. The route is **not closed**,
because the sign inversion is genuinely gone and 29.9 points is a real improvement on 133.9,
but it is further from a publishable force-convergence curve tonight than section 13 implied.

### 15e. THE 3600 RUNG DID RETURN, WITH THREE MINUTES OF ALLOCATION LEFT, AND IT IS THE MOST IMPORTANT ROW

Section 15e previously recorded this rung as absent. It completed at 23:28, `rc=0`, with 3:10
remaining on the node. The full ladder:

| cap | frames_run | gate_met | ratio | error | swing vs g64 |
|---|---|---|---|---|---|
| 900 | 900/900 | False | 0.7574 | -24.26% | 8.5 pts |
| 1800 | 1800/1800 | False | 0.6790 | -32.10% | 16.3 pts |
| 2700 | 2596/2700 | **True** | 0.5431 | -45.69% | 29.9 pts |
| 3600 | **3280**/3600 | **True** | **0.4553** | **-54.47%** | **38.7 pts** |

**TWO RUNS BOTH MET THE GATE AND DISAGREE BY 8.8 POINTS.** The gate tripped at 2596 frames in
one and at 3280 frames in the other, same grid, same configuration, and they return -45.69 and
-54.47 percent. The error is still falling monotonically at the deepest settle run, with no
plateau anywhere in the ladder.

**This is a stronger negative result than section 15b, and it changes the recommendation.**
The quiescence gate (`sound_speed/vmax >= 20`) **does not identify a converged state.** It is a
threshold on a noisy quantity, so where it trips varies run to run by 26 percent in frame
count, and the underlying force has not stopped moving when it fires. `settle_gate_met=True`
is therefore not a validity criterion for a coupling-accuracy measurement, and any artifact
that carries it should not be read as converged.

**The swing does not narrow toward a limit, it widens with settle depth:** 8.5, 16.3, 29.9,
38.7 points as g96 settles longer. The 29.9-point figure in 15c is itself provisional and is
better stated as **at least 29.9 points and still growing**, because the g96 arm has not
converged. The only claim from unit 2 that survives all four caps is the qualitative one:
**the sign inversion is gone**, at every cap, and both grids under-predict.

**What should be tuned instead.** Not the settle length. The three candidates the ladder
leaves are the added-mass regime (structural, 15d item 1), the submersion mismatch (not a
settle artifact, 15d item 2), and the convergence criterion itself, since the current gate
demonstrably passes non-converged states. Whoever picks this up should treat "raise the settle
cap" as **answered and exhausted**: it is reachable, it is expensive, and it makes the number
worse rather than better.

Provenance: `$WORK/r8_rungb/rungb_cap{1800,2700,3600}_g96.{log,json}`, all `rc=0`, engine
**warpmpm**, SDF-collider path, not the material-8 path the 17 canonical runs use.

Provenance: `$WORK/r8_rungb/rungb_cap{1800,2700,3600}_g96.{log,json}`, engine **warpmpm**,
SDF-collider path, not the material-8 path the 17 canonical runs use.
