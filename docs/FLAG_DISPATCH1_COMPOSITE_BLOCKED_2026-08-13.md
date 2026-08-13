# FLAG: Dispatch 1's composite is not runnable as specified, 2026-08-13

Raised under flag rule 3-adjacent grounds: not a scope violation, but a case where
proceeding as written would have produced a number that looks like the requested answer
and is not. Written to a named file per the operating protocol. **Work continued: the
substitute test was built, submitted and is reported separately.**

## What was asked

> Pick one currently-SLIDE canonical arm. Re-run it on the force-coupled path instead
> of free-rigid, same mass, **same floor_friction=0.55**, same forcing. Report whether
> it still crosses `failure_modes.py`'s live `slide_m`/`slide_speed_ms` thresholds.

## Why it cannot be run today

**The force-coupled `DynamicSDFBody` path has no floor friction, and no floor contact
model beyond a position clamp.** [read] `simulation/realism/dynamic_body.py:216-221` is
the complete floor treatment:

```python
x_new = self.x + v_new * dt
if self.floor_z is not None and x_new[2] < self.floor_z:
    x_new[2] = self.floor_z
    if v_new[2] < 0.0:
        v_new[2] = 0.0
```

That is a z-position clamp plus a normal-velocity clamp. There is no tangential
impulse, no normal force, no `mu*N`. A case-insensitive grep for `friction`, `tangent`
or `coulomb` across `dynamic_body.py` returns **zero hits**.

Compare the canonical path [read], `renders/yaris_render_s1/sim_standing.py:210-211`:

```python
s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
            restitution=0.05)
```

which hands `mu` to the engine's own plane collider. That is where 0.55 acts, and that
mechanism has no counterpart on the force-coupled path.

**Second, independent blocker** [read]: no module under `simulation/realism/` imports
`failure_modes` or `classify_timeseries`. There is no SLIDE classification wired to the
force-coupled path at all, so even with friction present there is nothing to compare
against `slide_m` / `slide_speed_ms` without new plumbing.

**Third** [read]: the two tracks do not share a body. Track 1's friction result runs on
a **box** (`rho_box`, `box_bottom_travel_m`, and
`validate_coupling_force_ladder.py:156` explicitly excludes the Yaris hull property from
that rung). Track 2 runs the **real Yaris hull**. The dispatch treats the composite as a
coupling-path swap on a fixed body; it is not.

## What this means for the report's Phase 1 D3

Phase 1 D3 calls the composite "an unexamined gap between two now-separately-true
things" and "the most consequential item on this entire list." **The identification is
right and the framing understates it.** It is not that nobody has run them together. It
is that they **cannot** be run together without first implementing a Coulomb contact law
on the force-coupled body and wiring the classifier to it. That is new physics plus new
plumbing, each needing its own validation, not a re-run.

Cost estimate is therefore not "one GPU arm." It is: implement tangential contact on
`DynamicSDFBody`, validate it against a known analytic sliding case, port or share the
canonical scene's forcing, emit the 15-column `FloodHistory` format, and only then
classify. The ladder already has the last of those (`--emit-timeseries`, added in
`ed8bf8e`), so that piece is free.

## Assumption I proceeded on, stated so it can be reversed

**I did not implement the friction law.** Writing a contact model and running a verdict
through it in the same pass would produce a SLIDE/STUCK answer whose credibility rests
entirely on physics written minutes earlier and never validated. Given that the number
would go straight at a published result, that trade is wrong. The blocker is recorded
instead, and the substitute below tests the same published number on an axis that needs
no new physics.

## What was run instead, and why it is the right substitute

Register **J15** calls running the canonical set at g128 "the single highest-value open
item in the project," because a SLIDE verdict has already been shown to be
resolution-dependent (Silverado flips SLIDE to STUCK between g96 and g128) and
`g96_m2337` sits at a one-frame margin. Both the composite and the g128 test ask the
same question, *does the published 16 SLIDE / 1 STUCK survive?*, along different axes.
The g128 axis is testable today with the canonical driver, unmodified.

Submitted as LS6 job **3362573**, `scripts/g128_canonical.sbatch` calling
`scripts/run_g128_canonical.sh`. Six runs: masses 1100 / 1609 / 2337 at **g96 and g128
in the same job**, so the refinement comparison is within-job. That pairing is required,
not decorative:

- Register **J16**: the frozen g48/g96 margins are not reproducible; job 866887
  overwrote those directories on 2026-07-26.
- Register **J17**: this stack is non-deterministic at fixed configuration, so a
  cross-job comparison cannot separate refinement from a run-to-run draw.

Parameters are the canonical `--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3
--floor-friction 0.55`, verbatim from `run_rs_sweep.sh`, which took them from
`class_specific_2026-08-08.sbatch`, which took them from `run_s2.sh` as-ran. Confirmed
live against `data/all_runs_inventory.csv`.

## Status

**Dispatch 1 as specified: BLOCKED, not attempted, not faked.**
**Substitute test: submitted.** Neither `data/all_runs_inventory.csv` nor
`gates_results_all_runs.json` is touched by any of it.
