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

## 6. RESULTS

*(empty at pre-registration time; filled in below after the runs return)*
