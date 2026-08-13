# Friction rung, horizontal instrumentation, 2026-08-13

Closes the limitation `docs/FLOOR_FRICTION_RUNG_2026-08-12.md` section 4 states as the
bound on every number that rung produced: **the harness recorded vertical motion only**,
and SLIDE is horizontal.

Engine is **warpmpm** throughout. No Genesis path is involved. [WARPMPM]

**This document was adversarially reviewed before it was committed** (`physics-skeptic`,
2026-08-13). The review returned six blocking issues. All six were independently
re-verified against source and **all six were upheld**; every one is corrected below and
each correction is marked. Three of them changed the headline. Sections 4.1, 5.2 and 5.3
exist because of that review.

## 0. Prerequisite, checked before anything else was run

Rung (b) at g96 is a **settled, non-discard** run and its result stands. [READ]

Path note: `data/coupling_validation/` is gitignored, so it exists in the `can-it-ford`
main checkout and on Vista but **not** in the `warpmpm-continue` worktree. A reader in
this worktree who cannot find `ladder_b_g96.json` has not found a missing artifact.

| field | value |
|---|---|
| `settle_gate_met` | **True** |
| `settle_frames_run` | 20, cap 1200, min 20 |
| `n_grid` | 96 |
| `a_late_window` | `+0.6080040576335208` |
| `a_ideal_partial` | `-6.571282452258303` |
| `a_late_as_fraction_of_ideal` | `-0.09252441392540853` |
| `measure_substeps_achieved` | 160, not truncated |

**Correction to how that ratio has been quoted.** `FLOOR_FRICTION_RUNG_2026-08-12.md:19`
and the rung_e docstring both render this as "**-9.25 percent** with the sign inverted."
That figure is the **ratio** `a_late / a_ideal`, not a percent error. The conventional
relative error is `(a_late - a_ideal) / |a_ideal|` = **+109.25 percent**. Both describe
the same two numbers; they are not interchangeable, and "-9.25 percent error" would read
as near-agreement when the measured acceleration is in fact the wrong sign and the
residual is larger than the analytic value itself. Quote the ratio as a ratio.

## 1. What was missing, verified rather than assumed

Walked all **55** keys of each **2026-08-12** g96 arm JSON on Vista, 2026-08-13, i.e. the
arms as they stood before this work. [READ] No body horizontal field exists in any arm.
The only `x`-named fields are `flow/inflow_x_m`, a scalar geometry constant, and
`flow/water_vx_near_box_{before,after}`, which are **water** statistics near the body, not
the body's own state.

`FLOOR_FRICTION_RUNG_2026-08-12.md:95` says "all **52** keys". The live count is **55**.
The conclusion it drew is unaffected and stands; the count was wrong and is corrected here.

**The criterion, read live** (`simulation/failure_modes.py`): [READ]

| symbol | value | line |
|---|---|---|
| `slide_m` | `0.05` (metres) | `:46` |
| `slide_speed_ms` | `0.05` (metres per second) | `:47` |
| `sustain_frames` | `3` | `:50` |
| `SURGE_AXIS` | `0`, i.e. **x** | `:16` |

SLIDE at `:179-181` is `(surge_drift >= slide_m) & (surge_speed >= slide_speed_ms)`
evaluated **pointwise per frame** and sustained 3 consecutive frames, with
`surge_drift = |disp[:, 0]|` and `surge_speed = |vel[:, 0]|`, then ANDed at `:193` with
`driven_downstream` from `:176`.

## 2. Instrumentation

`simulation/coupling_validation/rung_e_floor_friction.py`, first committed as `0a1797c`,
staged separately from any result. It wraps `tank.solver.step` and `tank.pin` on the
constructed `BoxTank` instance and records `solver.rigid_state()["com"][0]` and `["v"][0]`
after every step. `rigid_state` copies warp arrays to host numpy and writes nothing back
(`core/solver.py:200-211`), and `fused_ok` requires `n_rigid_bodies == 0` (`:444`) so
rigid scenes always take the split loop that `_apply_rigid_restitution` already forces a
host readback in. **No physics changes.** No ladder source was edited. Ladder md5 stays
`f650d762635fb3415d2cf202f5a5c979`. [READ]

Phases are separated at the call site: **settle** = `pin()` called after the step,
**flow** = no pin and `n_substeps != 1`, **measure** = `n_substeps == 1`.

> **Correction (review, non-blocking).** An earlier revision of that comment claimed the
> split "does not depend on `substeps > 1`". **Wrong, withdrawn.** The pin flag separates
> settle only; flow and measure are separated by `n_substeps == 1` alone, so at
> `substeps == 1` a flow block would be silently absorbed into measure. Harmless at g96
> where `substeps == 16`, and the arms now record `phase_split_reliable`.

**Settle self-check, and a correction to it.** Settle drift is *not* expected to be zero:
the recorder samples post-step and pre-pin, so it captures the intra-frame excursion that
`pin()` then resets. Measured at **7.772e-05 m** peak-to-peak, oscillating and not
accumulating. That is **643x smaller than `slide_m`**. A first revision compared it
against `1e-9` as if the sample were post-pin; that criterion was wrong and failed on
every arm. Corrected, and it now passes on all arms. The displacement zero uses that last
pre-pin sample rather than `tank.spawn_com[0]`, which `pin()` actually writes; the bias is
bounded by that same 7.772e-05 m, i.e. 0.28 percent of the smallest drift reported below.

## 3. Results, g96 only

g64 is excluded deliberately: 5 of 6 g64 arms were settle discards on 2026-08-12.

### 3.1 The full SLIDE criterion is evaluable, and this is a verdict

> **Correction (review, blocking).** This document originally reported a "kinematic pair"
> and said `driven_downstream` could not be evaluated because the material-8 free-rigid
> path accumulates no contact force (register A3, CLAUDE.md A-1). **That hedge was wrong
> and is withdrawn.** `failure_modes.py:127-128` is
> `accel = np.gradient(vel, t, axis=0)` then `force = mass_kg * accel`. The classifier's
> `surge_force` is **mass times the finite-difference acceleration of the body's own
> velocity**, not a contact-force accumulator, so it is fully derivable from the `(t, vx)`
> series this harness already records. A3 is a fact about the **solver**; it does not
> transfer to this **classifier**. Applying the real criterion, `driven_downstream` is
> `True` in every arm (`:176` takes `max|surge_force|`, so it is direction-blind and only
> guards against an all-zero series) and therefore never gates anything here.

Full criterion, computed exactly as `failure_modes` does, on the per-frame flow block:

| arm | mu | seed | drift max (m) | speed max (m/s) | peak abs Fx (N) | `slide_idx` | **SLIDE** |
|---|---|---|---|---|---|---|---|
| `fric_d_g96_mu000_s0_hx2` | 0.00 | 0 | 1.132190 | 0.832565 | 4867.9 | 7 | **True** |
| `fric_d_g96_mu000_s1_hx2` | 0.00 | 1 | 1.132200 | 0.832538 | 4842.0 | 7 | **True** |
| `fric_d_g96_mu000_s2_hx2` | 0.00 | 2 | 1.131628 | 0.832653 | 4845.0 | 7 | **True** |
| `fric_f_g96_mu055_s0_hx2` | 0.55 | 0 | 0.028885 | 0.199701 | 3278.1 | -1 | **False** |
| `fric_f_g96_mu055_s1_hx2` | 0.55 | 1 | 0.028473 | 0.209157 | 3521.4 | -1 | **False** |
| `fric_f_g96_mu055_s2_hx2` | 0.55 | 2 | 0.026230 | 0.199321 | 4082.3 | -1 | **False** |

**3 of 3 SLIDE at mu = 0.00, 0 of 3 at mu = 0.55.**

### 3.2 Which clause actually flips, on a consistent pairing

> **Correction (review, blocking).** This document originally said the result "crosses
> **both** thresholds", pairing a **max** drift against a **late-window mean** speed.
> `failure_modes` computes no late-window mean and uses none; it evaluates pointwise and
> reports `max_surge_drift_m` (`:198`). On a consistent max-vs-max pairing the claim is
> **false**, and it is corrected here.

| arm | drift vs `slide_m` | speed **max** vs `slide_speed_ms` |
|---|---|---|
| mu = 0.00, 3 seeds | **22.63 to 22.64x over** | **16.65x over** |
| mu = 0.55, 3 seeds | **0.525 to 0.578x, under** | **3.99 to 4.18x, OVER** |

**The gated arm is about 4x OVER the speed threshold. It fails the joint criterion on the
drift clause alone.** One clause crosses, not two. Any statement that friction pushes both
quantities below threshold is wrong.

### 3.3 Still water, no inflow (rungs c / e), seed 0

| arm | mu | drift (m) | speed max (m/s) |
|---|---|---|---|
| `fric_c_g96_mu000_s0_hx2` | 0.00 | 0.00022984 | 0.006031 |
| `fric_e_g96_mu055_s0_hx2` | 0.55 | 0.00642443 | 0.189937 |

Neither meets the criterion, because drift is 0.005 to 0.13x of `slide_m`. Note the
ordering is **inverted** here: friction *increases* drift 28x and peak speed 31x, and the
mu=0.55 peak speed is **3.8x over `slide_speed_ms`**. With no flow there is no horizontal
driving force and both are numerical jitter against the criterion, but the inversion is
real and is reported rather than smoothed over.

## 4. What this says

**Adding the gated floor friction flips the SLIDE verdict at g96**, 3/3 to 0/3, under the
full criterion including `driven_downstream`. This is the number
`FLOOR_FRICTION_RUNG_2026-08-12.md` section 4 said the rung could not produce.

**The mechanism is genuine Coulomb friction on the rigid body, verified at source.**
[WARPMPM] [READ] `enable_floor_restitution` (`validate_coupling_force_ladder.py:190-199`)
does **not** call `add_surface_collider`; it appends the entry directly to
`sim.rigid_surface_colliders`. So `collider_param.friction`, the water-side grid BC, is
never touched, and `BoxTank`'s floor stays at `friction=0.0` in **both** arms
(`validate_coupling_force.py:277`). The 0.55 reaches exactly one place,
`kernels/mpm_solver_warp.py:967-977`:

```python
J_t = min(v_t_mag / denom_t, mu * J_n)
v_cm_np[b]  = v_cm_np[b] - (J_t / M) * t_hat
```

**The water-field difference is a consequence, not a cause.** Near-box water `vx` reads
`+0.4671` m/s at mu=0.0 against `-0.1154` m/s at mu=0.55. Friction never reaches the water
in these arms, per the source read above; the difference is the body having moved 1.1 m.

**Draft moves the other way and is therefore not the explanation.** The mu=0.55 arms sit
*deeper* (`submerged_frac` 0.21452 against 0.20625). Deeper means more buoyancy and less
normal force, so *less* `mu*N`, a 2.1 percent change against a 40x displacement change.

### 4.1 The falsification test, run rather than deferred

The review's strongest objection was that the mu=0 baseline might be a frictionless coast
on a one-shot slosh rather than a driven slide, so that the ratio measures **absence of
drag** in the control as much as presence of friction in the treatment. That objection is
well founded, because the forcing is not what "sustained inflow" implies:

> **Correction (review, blocking).** `kick_water` (`ladder:402`) adds +1.5 m/s to **all
> 163,944** water particles **once**; `sustain_inflow` then clamps **220 per frame**,
> **0.134 percent**. The default flow block is a slosh transient, and it decays: mean
> `|vx|` per 10-frame block runs `0.271, 0.531, 0.709, 0.808, 0.781, 0.301`, final sample
> **0.1135 m/s**. The previously quoted "late-window surge speed 0.6303 m/s" is the mean
> of a decaying transient and must not be cited as a characteristic speed. This is the
> magnitude-versus-verdict trap CLAUDE.md item 5 exists for: **cite the verdict**.

So the test was run: `--no-kick`, making `sustain_inflow` the only forcing, over 200 flow
frames to allow transit (`n_kicked = 0`, confirmed in the artifacts).

| arm | mu | drift max (m) | speed max (m/s) | `slide_idx` | **SLIDE** |
|---|---|---|---|---|---|
| `fric_d_g96_mu000_s0_nokick` | 0.00 | 1.161353 | 0.625181 | 29 | **True** |
| `fric_f_g96_mu055_s0_nokick` | 0.55 | 0.017969 | 0.190140 | -1 | **False** |

**The flip survives.** Ratio 64.6x, larger than with the kick. Under clamp-only forcing
the control's `|vx|` no longer decays to zero but oscillates around a sustained level
(20-frame means `0.009, 0.285, 0.601, 0.484, 0.274, 0.095, 0.273, 0.413, 0.288, 0.211`),
which is what a sustained inflow should look like, while the treatment arm stays at
0.005-0.02 throughout. The verdict flip is therefore **not** an artefact of the one-shot
kick. It reproduces under two independent forcing regimes.

## 5. What this does NOT say, and the limits that bound it

1. **This is not the coupling defect's effect.** It measures **friction**. It establishes
   that the route section 5.3 posited, from a buoyancy error into the normal force and
   thence into `mu*N`, is not merely live but **dominant** in the horizontal channel. It
   does not quantify how much the rung-b buoyancy error moves a verdict. Still open.
2. **The body is a cube, not the Yaris hull.** `RHO_BOX = 600.0 kg/m^3`, against the
   canonical hull's 310.494; realized box mass 1914.28 kg. Nothing transfers numerically
   to the 17 gated runs; only the mechanism does.
3. **Do not read this as contradicting the 16 SLIDE verdicts** (register D6b). Different
   body, domain and duration. The valid comparison is between these two arms.

### 5.1 Fidelity gap: the rung reproduces only half the gated floor

The gated floor is `add_plane(..., "slip", friction=0.55, restitution=0.05)`
(`sim_standing.py:210-211`), which drives **both** channels: `collider_param.friction` at
`:1913` for the water grid BC, and the `restitution != 0.0` gate at `:1915` appending the
plane to `rigid_surface_colliders` for the body. This rung's `enable_floor_restitution`
path drives **only the rigid half**. The gated runs therefore have a frictional floor
under the *water* as well, which these arms do not.

### 5.2 The harness's own arrival gate FAILS in the treatment arms

> **Correction (review, blocking).** `flow_reached_body` was not disclosed. It is
> **False** for all three mu=0.55 arms (`water_vx_near_box_after` mean `-0.1154`,
> `-0.1188`, `-0.1156` m/s) and False for **both** `--no-kick` arms. It is True only for
> the three kicked mu=0.0 arms.

The gate is `vx_near_box > 0.25 * velocity` (`ladder:238-239`). It cannot be read as a
clean between-arm comparison, because "near box" **follows the box**: in the control the
box has travelled 1.1 m downstream and samples water it is moving with, while in the
treatment the box stayed put and samples water that has sloshed back. But the honest
statement is that **by the harness's own arrival test, 5 of the 8 inflow arms do not
qualify**, and no arm here should be described as measured under a verified-arrived flow.

### 5.3 Three further limits the review surfaced

- **Single grid.** Only g96 was run for the horizontal channel. **No grid-refinement check
  of the horizontal result exists.** Given register B-section non-monotonicity and L-5,
  that is a real gap, not a formality.
- **Artificial sound speed.** `BULK = 1.5e5`, gamma 1.1, giving `c = 12.845 m/s`, about
  118x below real water, and 8.6x the 1.5 m/s forcing. Isik and He 2022 record that
  artificial sound speed can qualitatively flip a rigid-body outcome, and it has never
  been swept here. Every number in this document sits on that value.
- **"416x separation" measures repeatability, not physical uncertainty.** Seeds perturb
  only the water-lattice jitter, and the mu=0 drifts agree to 5 significant figures. It
  shows the result is not a seed draw; it does not bound physical uncertainty.
- **`J_n` is a restitution impulse** from the approach velocity, not a weight-supported
  steady normal force, so "sliding resistance is `mu*N`" is a useful heuristic and not the
  code's model.
- **Provenance is incomplete.** Arms record `arm_provenance.code_md5` but no
  `solver_git_sha`, no repo commit and no environment capture. `wp.atomic_add`
  (`mpm_utils.py:1411-1412`) makes runs non-reproducible bitwise at fixed seed regardless.

## 6. Reproduction

Vista node `c642-001`, allocation `908672`, 2026-08-13, on an allocation already running,
so marginal SU cost was zero. Eight arms `rc=0` in 37.92 s, plus four `--no-kick` arms.

```
source /work/11603/jcerrell0629/vista/.venv/bin/activate
cd $WORK/can-it-ford
python simulation/coupling_validation/rung_e_floor_friction.py \
  --out-dir $WORK/can-it-ford/data/coupling_validation --device cuda:0 \
  --g96-only --g96-df-seeds 3 --tag-suffix _hx2
python simulation/coupling_validation/rung_e_floor_friction.py \
  --out-dir $WORK/can-it-ford/data/coupling_validation --device cuda:0 \
  --g96-only --g96-df-seeds 1 --flow-frames 200 --no-kick --tag-suffix _nokick
```

Artifacts in `$WORK/can-it-ford/data/coupling_validation/` (persistent Lustre):
`fric_index_hx2.json`, `fric_index_nokick.json`, `fric_*_g96_*_{hx2,nokick}.json`,
`fric_run_{hx2,nokick}.log`. The `_hx` suffix is a superseded first pass, kept.

**RETRACTED 2026-08-13, same day, second pass. This paragraph was WRONG and its "fix" made
things worse; see register D8c.** It read: every arm JSON before this correction carries
`arm_provenance.friction_source` naming `sim_standing.py:132`, that line is
triangle-rasterisation arithmetic, and the gated floor is `:210-211`.

**`:132-133` was CORRECT.** It is the floor `add_plane` in the driver that produced the 17,
sha256 `5215c38b...`, 389 lines, preserved at
`renders/yaris_render_s1/_incoming/sim_standing.py` and recorded on-node at
`renders/yaris_render_s1/_incoming/conv_2026-07-26_idev/00_provenance.txt:6`. `:210-211` is
the floor in the **2026-08-08 revision** that later overwrote the top-level path and ran none
of the 17. The repoint has been reversed in
`simulation/coupling_validation/rung_e_floor_friction.py`. **Arm JSONs stamped between
2026-08-13 and that reversal carry `:210-211` and are the ones now mislabelled**; arms stamped
before it carry `:132` and were right all along. The *value* 0.55 was correct throughout, so
no arm's physics is affected and nothing is retro-edited.

**Cross-job comparability.** `simulation/validate_coupling_force.py` on Vista carries an
uncommitted `provenance_v2` block added after the 2026-08-12 arms ran. It is **confined to
`main()`**, which `run_rung` never calls. Every arm is paired with its own control in the
same job on the same node and revision, so nothing depends on that.

**How well the 2026-08-12 arms reproduce, measured rather than asserted.** [READ]

| quantity | c / e (still water) | d / f (inflow) |
|---|---|---|
| `submerged_frac` | 0.0000 % | 0.0013 to 0.0276 % |
| `submerged_frac_at_end` | 0.0001 to 0.0011 % | 0.0040 to 0.1113 % |
| `box_bottom_travel_dx` | 0.0000 to 0.0146 % | **71 to 165 %** |
| `a_late_window` | 0.0994 to 0.1247 % | **189 to 354 %** |

The quantities with physical magnitude reproduce to three or four significant figures. The
two that do not **do not even reproduce in sign**, and that is expected: both are
numerically **zero**. `a_late_window` moves between `+0.012098` and `-0.010736` against an
analytic `-6.437`, a run-to-run difference of **0.355 percent of analytic** for the d pair
and **0.407 percent** for the f pair. The body is resting, where section 5.3 already
establishes the correct vertical acceleration IS zero. `box_bottom_travel_dx` moves
between `-7.5e-05` and `-2.2e-05` cells. **Relative error is meaningless on a quantity
whose true value is zero**, and an earlier draft wrongly claimed "about three significant
figures" across the board.

None of this touches the horizontal result: surge drift is 1.132 m, not a near-zero
quantity, and reproduces across three seeds to 0.05 percent.
