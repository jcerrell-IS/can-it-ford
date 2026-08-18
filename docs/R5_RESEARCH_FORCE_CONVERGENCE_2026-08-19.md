# R5-D1 unit 71: RETRACTED. The arithmetic was right and the quantity was wrong.

Date 2026-08-19, retracted same day. Branch `claude/r5-research`. Engine **WARPMPM**.

> ## THE CONCLUSION IS WITHDRAWN. Seven blocking defects, six structural.
>
> Every number reproduced exactly under independent recompute. **That is the
> problem: the arithmetic is right and the quantity is not a force.** I verified
> the decisive defects myself before accepting them. Sections 1-3 are what the
> data actually supports; section 4 is the full list of what I withdraw.

---

## 1. What survives, and it is not nothing

**The two premise corrections stand, both independently re-verified:**

```
918247 r6rep_g128 COMPLETED | 918248 r6rep_g96 COMPLETED
918249 r6rep_g64  COMPLETED | 918250 r6rep_g48 COMPLETED
918350 r6rep_g160 PENDING   | 918351 r6rep_g192 PENDING
mass_kg = 2337.0 in 20/20 summaries
```

**FOUR grids, not six. Mass 2337 kg, not the canonical 1100.**

The arithmetic also stands: the table, the nine successive changes and the twelve
spreads all reproduce to the last digit. What they measure is the problem.

## 2. Why the quantity is not a force

`v_cm` is **overwritten**, not integrated. In the pinned solver core:
`mpm_utils.py:920-923` scatters **every** particle including rigid material 8 into
the same `grid_v_in`/`grid_m`; `:935-941` forms `v_out = grid_v_in/grid_m + dt*g`, a
mass-weighted **water+rigid mixture**; `:1402-1409` interpolates that mixed field
back at each rigid particle; `:1434` assigns `v_cm_new = rigid_linear_mom/M`.

**No force accumulator exists for the body.** So `M*dv_cm/dt` is `M/dt` times the
difference of two PIC reprojections of a blended field, not a net force. Register
**D6f** already brands this exact accessor: "`peak_surge_accel_g` is numerical, not
physical. It is `np.gradient(vel, t)` over a 30 Hz rigid-body trace." **I cited
`failure_modes.py` as precedent for the construction and omitted the register entry
that condemns it.**

**And a plausibility check I never ran, which CLAUDE.md mandates:**

```
peak_all      g48 32552 N = 1.42 x vehicle weight | g128 21028 N = 0.92 x weight
vehicle weight  m*g = 2337 * 9.81                 = 22926 N
drag anchor     0.5*rho*Cd*A*v^2, Cd=1, A=0.5028  =   566 N   -> peak_all is 36-58x
```

**A 2337 kg car in 0.29 m of water at 1.5 m/s cannot experience a horizontal force
of 1.4 times its own weight.** That alone should have stopped me.

## 3. Three uncontrolled confounds, all monotone with refinement

I wrote "nothing else confounds". Measured from the same 20 summaries:

```
grid   substeps   water_layers   depth/dx (cells)
  48       8            3             1.528
  64      11            4             2.038
  96      16            6             3.057
 128      21            8             4.076
```

**(a) Substeps rise 2.6x across the ladder.** PIC reprojection is dissipative, so
the number of dissipative reprojections per recorded frame rises monotonically with
refinement, in the same direction as every "converging" trend I reported. **Untested
as the cause.**

**(b) No level resolves the flow depth by more than 4.1 cells**, against the ~10
particles-per-depth rule of thumb that register B3 and CLAUDE.md L-3 both record.

**(c) `realized_rho` varies 642.8 to 663.6** across grids, so the `M` I multiplied by
is not even constant along the ladder.

## 4. What I withdraw

**W1. "It does not converge."** Not supportable as a statement about MPM surge
force, because the quantity is not a force (section 2) and three confounds move
monotonically with the refinement (section 3).

**W2. The settle claim, and it is INVERTED.** I wrote "all 90 recorded frames are
post-settle and the settle transient is not inside this measurement window."
`analysis/stationarity.py`, the project's own MSER/Chodera/Flyvbjerg tool, run on
these exact 20 runs: **discard 25 to 67 of 91 frames on `vx`, more than 8 in 20/20,
only 8/20 stationary.** My "physically meaningful" `peak_ex` at frames 3-7 sits
**inside the discard region in 20 of 20 runs**. `RESEARCH_TO_IMPLEMENTATION_2026-08-15.md:63-72`
already recorded this a day earlier. **My branch does not contain commit `072e4f3`,
so the tooling was invisible to me. That explains the miss; it does not excuse
publishing the inverse claim.**

**W3. "N=5 with error bars."** The repeats are **the same initial condition**.
As-run driver `:77` hard-codes `seed=0`; **`grep -c "add_argument.*seed"` returns 0**,
so there is no `--seed` flag; `r6_rep.sh` varies only `${SLURM_JOB_ID}` and the
repeat index. The spread measures **GPU floating-point non-determinism in atomic P2G
accumulation**, not physical or model uncertainty. **So "signal is 5-12x the noise
floor", the load-bearing argument for calling this publishable, is withdrawn.** It
proves a discretisation change exceeds round-off, which nobody doubted. The floor is
also non-stationary: `peak_all` spread runs 0.000 -> 0.000 -> 0.102 -> **2.561%**.

**W4. `integral |F| dt` is not an impulse.** It is 0.79-0.91 times mass times the
**total variation** of the sampled velocity. Forty-nine to 51% of it comes from
negative `F`, and the actual net streamwise impulse is ~100x smaller and
sign-changing (`-10.4 / +30.2 / +6.0 / -39.5 N.s`). I integrated a ringing metric and
called it a load.

**W5. Two qualitative verdicts are estimator-artifacts.** "Diverging, not
converging" fails under a **centred** difference stencil (`-17.95, -9.87, -29.23`:
the middle step is smallest). "Non-monotone, sign-changing" fails at cuts 0, 1 and 8
and under 2 of 7 equally defensible estimators; a 5-frame smoothed peak gives
`-22.73, -22.13, -14.21`, monotone **with shrinking differences**, the exact
signature I claimed was absent.

**W6. Every `sim_standing.py` line number except `:10-12` is wrong.** I cited the
564-line repo copy; the as-run driver on Vista is 389 lines with a different sha256.
Settle is `:156` not `:235-237`, the kick `:161` not `:240`. The physics is
identical, so the substantive facts hold, but every citation tagged READ resolves to
a file that did not run.

**W7. Smaller:** the kick at `:161` is `v[:n_water, 0] += velocity`, **water only** -
the vehicle is never written, so calling frame 0 "the kick differentiated at the
boundary" mis-attributes the mechanism; §5 named **gravity** as a surge contaminant
when gravity is z-only; `failure_modes.py:127-128` should be `:129-130`; and "no
shrinkage" in the impulse is contradicted by its own numbers (486.7 -> 305.9 is a
37% shrink).

## 5. What would make this real

In order of value, from the review:

1. **Rerun at `settle_frames >= 250`.** Memory records four results invalidated by
   exactly this, one of which was a "63.3x non-monotone" ladder that became
   **monotone and passing** at converged settle. This result has the same shape.
2. **A no-forcing control, `--velocity 0` at each grid.** If the curve still moves
   20-35% with no flow, it is reprojection noise and nothing else.
3. **Expose `--seed` and run 5 seeds per grid.** That is the noise floor the argument
   needed and did not have.
4. **Use `sdf_wrench`.** My own §5 item 1 already said this was the obvious
   independent measurement, and I published without it.

## 6. Provenance, unchanged and still true

Inputs pulled read-only from Vista `$WORK/r6_rep_g{48,64,96,128}_*/rep_*/`: 20
`metrics.csv` + 20 `summary.json`, 295,974 bytes. **No run was executed and nothing
on Vista was modified.** Run provenance is itself weak: `canitford_git_commit`,
`grid_density`, `mesh_sha256`, `solver_git_sha` and `vehicle_mass` are **absent from
all 20 manifests**.
