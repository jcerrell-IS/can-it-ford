# Track 1: driver-level 6-DOF loop on the moving-SDF path

Date: 2026-08-13. Branch `track1/sdf-6dof-driver`, worktree
`/work/11603/jcerrell0629/vista/can-it-ford-track1-6dof`, based on `origin/main` at
`7453c92`.

Implements deferred item 1 of `track2_realism/FINDINGS_TRACK2_2026-08-13.md:495`, which
flagged this work for a Track 1 session and recorded that nothing in the solver blocks it.

## What was built

| File | What it is |
|---|---|
| `simulation/rigid6dof.py` | The integrator. Pure NumPy, imports nothing from warpmpm, no GPU. |
| `simulation/validate_coupling_force.py` | `run_c4_free_sdf` (variant `C4FREE`) plus `collider_pose`, wired to `--variant c4free`. |
| `tests/test_rigid6dof.py` | 25 tests, all runnable on a login node. |

Per-tick loop: `reset_sdf_force` -> `step` -> `sdf_wrench` -> integrate -> command
velocity and omega back through `set_sdf_pose`. No solver change, as predicted.

## Conventions, each verified live against the pinned SHA, not carried from a doc

All line numbers below were checked against
`third_party/mpm-engine-544c93dd-solver-core/` on 2026-08-13 and every one the findings
doc cited was still correct.

- **Quaternion order is xyzw, scalar last.** `add_sdf_collider` defaults `(0,0,0,1)`
  (`solver.py:324`) while `add_cup` documents wxyz and defaults `(1,0,0,0)`
  (`solver.py:256`). Crossing the two applies a wrong rotation silently rather than
  raising. `test_xyzw_not_wxyz` pins it.
- **omega is world-frame and left-multiplies**, exponential map, per
  `_omega_step_quat`'s own docstring (`mpm_solver_warp.py:198-200`).
- **The wrench must be normalised by the TICK, not the substep.** `sdf_wrench` divides by
  whatever `dt` it is handed (`solver.py:354-361`) and the accumulator spans every substep
  since the reset. Using the substep `dt` for an n-substep tick inflates the force by
  exactly n. `test_wrench_normalisation_is_by_tick_not_substep` pins it.
- **Never command a centre.** Only velocity and omega are sent; `modify_bc` integrates the
  pose itself (`mpm_solver_warp.py:2756-2760`). Passing the end-of-tick target as `center`
  double-applies the motion (`solver.py:240-246`).

## A real bug the tests caught, recorded so it is not reintroduced

The first implementation stored `omega` as the angular state and recomputed angular
momentum from it each tick as `L = I_world @ omega`. That is backwards, and it fails in a
way that looks plausible: `omega = solve(I_world, I_world @ omega)` is an identity, so
`omega` came out exactly constant while `L` drifted with the orientation. Torque-free
rigid-body motion is the opposite, `L` is conserved and `omega` varies.

The fix is that world-frame `L` is the stored state and `omega` is derived from it at the
current orientation. `test_torque_free_conserves_angular_momentum` failed on the original
and passes on the fix; `test_torque_free_tumble_actually_rotates` exists so the
conservation test cannot pass by nothing moving.

This is also why the integrator was built as a separate GPU-free module. The bug was found
on a login node in about a second, not on an allocation.

## Verification status, stated precisely

**Verified.** 25/25 tests pass. Convention equivalence is not self-consistency: the tests
extract the engine's real `_quat_mul` and `_omega_step_quat` out of the vendored source by
AST and compare against them, so a drift between this module and the engine fails the
suite. `validate_coupling_force.py` imports cleanly under the mpm-engine venv and the CLI
parses.

**NOT verified.** The loop has never been executed against the solver. No GPU run, no
allocation was used, and this session ran on a login node. Every number a `C4FREE` run
would produce is therefore unmeasured. Nothing in this document reports a force or a
percentage from this loop, because none exists yet.

**Stability is not claimed.** Register J1a's identity is that `added_mass_ratio` is exactly
1.000000 for any body floating at equilibrium, the stability limit of this scheme class,
and J1a further records that under-relaxation was tried and REFUTED (job 3361371, error
grew monotonically). No under-relaxation is applied and none is proposed. The ratio is
reported per run as a diagnostic. Whether the loop is stable near `rho_box = RHO_W` is the
open question this harness exists to answer.

**physics-skeptic was NOT available this session.** The offered agent types were `claude`,
`claude-code-guide`, `Explore`, `general-purpose`, `Plan` and `statusline-setup`. The
routing was conditional, so it was skipped rather than substituted with a generic agent,
which would have given false assurance. This is the same gap
`FINDINGS_TRACK2_2026-08-13.md:478-483` recorded for the prior session, now two sessions
running. Nothing here has been adversarially reviewed.

## Guards built into the driver

- **Pose mirror check.** Every tick the driver compares its own Python pose against the
  solver's live `collider_params` centre and raises if they diverge. If the `set_sdf_pose`
  velocity contract is not what the driver assumes, the run fails loudly instead of
  logging wrong positions.
- **Tunnelling margin.** `(|v| + |omega|*r_max)*dt_sub / band` is computed per tick, the
  same quantity `modify_bc` guards on (`mpm_solver_warp.py:2747-2749`). The engine warns
  once and then stays silent, so the driver records the maximum and by default aborts past
  1, where the wrench being integrated is no longer trustworthy.
- **COM offset refused.** The collider rotates about its centre and `sdf_wrench` reports
  torque about that same centre, so a body whose COM is offset needs the centre migrated
  each tick. That is not implemented, and the constructor raises rather than integrating
  something subtly wrong. The harness cube is centre-symmetric, so this does not bind here.

## Two findings from adjacent checks

**1. The SLIDE question is already answered; no new instrumentation is warranted.**
`data/failure_modes_by_run_classified.csv` has exactly 17 rows and reads
**16 SLIDE / 1 STUCK [READ]**, with `triggered_slide`, `max_surge_drift_m` and
`percent_over_threshold` already per run. Real `dx,dy,dz,dmag` timeseries also exist for
the separate 36-run `data/track1_sweep_v1/` sweep, where final `dmag` spans
**0.0528 m to 2.4052 m, median 0.2475 m [READ]**, and all 36 exceed the 0.05 m
DRIFT_THRESHOLD. Adding horizontal-drift instrumentation would have duplicated data that
already exists.

**2. An arithmetic contradiction in a pending Results claim.** The class tally in the
17-run store is `small_passenger 11, large_passenger 3, large_4wd 3 [READ]`. So
large_passenger + large_4wd is **6 runs**, and the claim that L1 and L2 disagree on **8**
runs "all in large_passenger/large_4wd" cannot be true as stated. This needs resolving
before any Results paragraph is written on it. Not fixed here; flagged only, because the
source of the 8 has not been traced.

## How to run it, when an allocation is available

Translation only first, which isolates heave before admitting rotation:

```
python simulation/validate_coupling_force.py --variant c4free \
    --n-grid 64 --rho-box 600 --no-free-rotation \
    --n-ticks 600 --tick-substeps 1 \
    --out data/c4free_g64_rho600_norot.json
```

Then the full 6-DOF case by dropping `--no-free-rotation`. Read
`tunneling_margin_max`, `pose_mirror_max_err_m` and `tunneled_at_tick` before reading any
force out of the result; if the margin exceeded 1 the forces past that tick are not
trustworthy.

Track 1 runs in `mpmenv`, never through Apptainer.
