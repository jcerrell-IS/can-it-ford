# failure_modes.py rebuild: emergent kinematics, SSF promoted to a live criterion

Scope: `simulation/failure_modes.py` rewritten to classify FORD / SLIDE / TOPPLE / FLOAT
from recorded rigid-body kinematics instead of closed-form drag and buoyancy. Companion
change: `FloodHistory.to_csv` in the mpm-engine checkout now writes the velocity and
angular-velocity columns it was already computing and discarding.

Status: **plumbing verified, no scientific result.** Everything numeric below is
synthetic. See "What is not established" at the bottom.

## Why emergent kinematics, not closed-form F_D / F_B

The classifier takes net force as `F = M * dv/dt` from the body's recorded velocity, and
uses net force, velocity, and displacement together as the SLIDE and FLOAT criteria.

The alternative was to evaluate a drag equation (F_D = 0.5 rho C_d A v^2) and a buoyancy
term (F_B = rho g V_disp) in the classifier and compare them to friction. That would be
L1's algebra wearing an L2 label: the whole claim of the L2 rung is that buoyancy and
lateral drag *emerge* from the coupled solve rather than being asserted by a formula. If
the verdict is computed from a closed-form drag law, the MPM run is decoration, and the
L1-vs-L2 divergence that is the project's core finding stops being a real comparison,
because both rungs would be running the same physics with different amounts of ceremony.

Reading force off `M * dv/dt` keeps the solver as the only source of physics. The
classifier measures the body; it does not model it. The cost is that the classifier is
only as good as the coupling, which is exactly the thing under test, and that is the
right place for the uncertainty to sit.

`C_d` never appears. That is deliberate and worth saying out loud in the writeup: no drag
coefficient was chosen, so no drag coefficient can be wrong.

## SSF is promoted from "for reference" to a live pass/fail criterion

**This is a methodological choice that needs defending, not a neutral implementation
detail.**

`vehicle_params.py` line 32 documents the `ssf` field as *"NHTSA Static Stability Factor
(unitless), for reference"*. It was carried as descriptive metadata. TOPPLE now reads it
directly via `get_vehicle(params_class)["ssf"]` and uses it as the threshold that decides
pass/fail. A field annotated "for reference" is now load-bearing.

The values (1.43 compact sedan, 1.04 midsize SUV, 1.19 light pickup) are unchanged and
still trace to the source `vehicle_params.py` already cites. What changed is their job.

It is used directly and is **not** reconstructed from track width and CG height. SSF is
defined as T / (2H), and `vehicle_params.py` does carry `cg_height_m`, so recomputing it
was possible. It was not done: there is no `track_width_m` field, so any reconstruction
would have required inventing a track width, and a derived SSF could silently drift from
the cited one. Reading the cited scalar keeps one number with one provenance.

### The defense Josie needs to be able to give

SSF is **adapted from general vehicle rollover engineering. It is not a flood criterion.**
Say this directly in the writeup, not only in the code. Anticipate it as a poster
question.

SSF is NHTSA's static rollover-resistance metric. It is the lateral acceleration, in g,
at which a rigid vehicle begins to tip about its outer wheels, and it is built for
cornering and tripped-rollover analysis. Applying it to a flood surge carries three
assumptions that the flood case does not obviously satisfy:

1. **Where the lateral force acts.** SSF assumes the lateral force is a tire reaction at
   the contact patch, so the body pivots about the outer wheels. A flood surge applies
   distributed hydrodynamic pressure over the submerged side of the body, with its own
   center of pressure that rises with depth. Same units, different load path.
2. **Sliding pre-empts toppling.** Untripped rollover needs the available lateral grip to
   exceed SSF, otherwise the vehicle slides before it tips. Buoyancy cuts the normal force
   and therefore the friction, so the flood case is biased toward sliding first. Expect
   TOPPLE to fire rarely, and treat it with suspicion when it does: a real flood rollover
   is usually *tripped* (curb, debris, soft shoulder), and none of that is in this scene.
3. **Static, not dynamic.** SSF is a quasi-static threshold. A surge front is an impulsive
   load, and a short spike above SSF is not the same event as a sustained lateral
   acceleration. Mitigated but not solved by the sustain window below.

None of this makes SSF the wrong choice. It is the only cited, per-class, dimensionless
overturning threshold available, and inventing a flood-specific one is out of scope. But
it is a **borrowed criterion**, and the honest framing is "adapted from rollover
engineering, sensitive to the load-path assumption", not "the standard flood overturning
threshold".

Related precedent: the `DRIFT_THRESHOLD = 0.05 m` correction already recorded in CLAUDE.md.
That value was nearly mis-cited to a paper that contains no such equation. The same
failure is available here. Do not let "SSF" acquire a flood-literature citation it does
not have.

## Severity precedence replaced max-ratio ranking (caught by the smoke test)

The previous classifier picked the mode with the largest `value / threshold` ratio. The
ratios are not commensurable. SLIDE divides drift by a 0.05 m numerical tolerance, so a
real washout scores 300x or more. TOPPLE divides lateral acceleration by an O(1) physical
SSF, so it scores near 1. Because a vehicle that topples has also slid, SLIDE outranked
TOPPLE essentially always and **TOPPLE was close to unreachable**. The old code carried
the same flaw.

Modes are now resolved by fixed physical severity, first match wins:

    TOPPLE > FLOAT > SLIDE

Rationale: a rolled vehicle is a worse outcome than a floated one, which is worse than a
displaced one. All three ratios and all three sustained flags are still reported on every
result, so nothing is hidden by the choice of label. This is a judgement call and should
be stated as one.

## Criteria as implemented

Axes follow the `FloodHistory` docstring: x = surge direction, y = vehicle long axis,
z = up. Roll is about the long axis, so a side-hit rollover reads as roll.

- **SLIDE**: sustained (|dx| >= `slide_m` AND |vx| >= `slide_speed_ms`), gated on a
  non-zero peak surge force, so a settling artifact with no driving force cannot register
  as a slide.
- **FLOAT**: sustained (dz >= `float_m` AND vz >= `float_speed_ms`), gated on a positive
  peak vertical force, that is, net upward load actually exceeding weight.
- **TOPPLE**: sustained (|a_x| / g >= `ssf`).
- **FORD**: nothing sustained; reports the worst ratio as margin.

"Sustained" means the condition holds for `sustain_frames` consecutive frames (default 3),
which suppresses single-frame numerical spikes. Thresholds stay parameterized on
`FailureThresholds`, unchanged in spirit from the previous version.

`peak_vertical_force_n` is reported next to `weight_n` (M*g) so the buoyancy margin is
readable without the classifier ever computing a buoyancy term.

### STUCK is now unreachable, deliberately

`FailureMode.STUCK` is kept in the enum but is never returned. STUCK means "immobilized
but not swept", which requires a notion of forward propulsion. `FloodScene` spawns a
parked body and hits it with a surge; there is no drive. A body that does not move is
FORD in this scene, and emitting two labels for one physical state would be worse than
admitting the gap. If a driven crossing scene arrives later, STUCK becomes reachable and
`forward_velocity_ms` comes back with it.

## Engine change: `FloodHistory.to_csv`

`FloodHistory` already recorded `v` and `omega` every frame and already exposed them from
`arrays()`. Only `to_csv` dropped them. No physics, solver, or recording change:

    old: t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg
    new: t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg,vx,vy,vz,vmag,wx,wy,wz

New columns are **appended**, so any existing reader that indexes by position is
unaffected.

**This file lives in Kumar's repo, not Josie's.** `/work/11603/jcerrell0629/vista/mpm-engine`
is a separate git repo with remote `kks32/mpm-engine`, sitting clean on `origin/main` with
no local commits. The edit is left uncommitted there on purpose. Committing to that
checkout is a decision about Kumar's repo (fork, PR, or carry as a local patch) and is not
made here. **The edit is also unpushed and unbacked-up: anything that resets that checkout
silently reverts it, and every future sweep goes back to writing no velocity columns.**

## Blocking dependency: no run on disk can feed this classifier

Both sweeps predate the writer change, so every timeseries in `data/track1_sweep_v2/` and
`data/track1_sweep_v3/` stops at `roll_deg`. There is no `vx` column anywhere on disk.
`M * dv/dt` cannot be computed from any existing run.

`load_timeseries` raises `MissingKinematicsError` on these files by design. It does not
fall back to finite-differencing `dx` into a velocity. That fallback was considered and
rejected: double-differentiating displacement to get acceleration amplifies
discretization noise, and the result would look like recorded velocity while being a
numerically distinct quantity. Verified against a real v2 file (check 7 below).

**Consequence: v3 cannot simply be re-read, it must be re-run.** The plan this work came
from assumed v3 only needed confirming. It needs regenerating, after the writer change is
in place.

## v3 is already disqualified on independent grounds

Per `logs/v3_launch_result.md`, the v3 sweep (job 833349) completed cleanly, 60/60 rows,
rc=0, and is **not usable**. The vehicle body hollows out at n_grid=128: `solidify_columns`
degenerates to a shell once grid pitch outruns the splat's native point spacing, particle
count scales 4.31x instead of the 8x a solid body requires, and all three vehicle classes
shift by an identical ~1.86x factor, which is a discretization signature, not geometry.
0 of 60 rows pass `density_plausible`.

This matters specifically for this classifier: the hollow body is under-buoyant and porous,
so it accumulates less lateral drag and less lift. **Both errors push toward FORD.** The
SLIDE and FLOAT criteria added here are exactly the measurements that bug corrupts, and it
corrupts them in the flattering direction. Running this classifier over v3 would produce a
clean, confident, wrong FORD-heavy phase space.

So there is currently **no reportable run**, and re-running v3 unchanged would not fix it.
Vehicle solidification has to be fixed first (see the three options in
`v3_launch_result.md`), then v3 re-run with the writer patch in place, and only that run is
reportable.

## Smoke test: plumbing only, NOT a result

Ran on the login node, CPU, no GPU, no solver. Synthetic `FloodHistory` states with
analytically known kinematics, pushed through the real `to_csv` and the real classifier.
This validates wiring and arithmetic. **It validates no physics and is not evidence about
any vehicle, depth, or velocity. Do not cite it, do not chart it, do not put it on the
poster.**

1. `to_csv` emits the 15-column header. PASS
2. `vx` and `wz` populate and round-trip through `load_timeseries`. PASS
3. Net force recovers analytic `M*a`: 2780.00 N vs 2780.00 N for M=1390 kg, a=2.0 m/s^2,
   relative error 3.6e-15. PASS
4. `ssf` is read straight off `get_vehicle("compact_sedan")["ssf"]` = 1.43, not
   reconstructed. PASS
5. Verdict formatting and the ratio/sustained reporting render. PASS
6. Forcing lateral acceleration to 1.93 g (above SSF 1.43) returns TOPPLE, ratio 1.35.
   This check is what exposed the max-ratio flaw above; it returned SLIDE before the
   severity fix. PASS
7. A real v2 file (`veh-pickup_dep-0p15_vel-1p00_idx-0024_timeseries.csv`) raises
   `MissingKinematicsError` rather than fabricating force. PASS

Smoke script kept out of the repo (session scratchpad). It is a wiring check, not a test
suite; it is not a substitute for a real run.

## What is not established

- No physical claim of any kind. Every number above is synthetic.
- The SLIDE / FLOAT / STUCK threshold defaults (0.05 m, 0.05 m/s, 0.02 m/s, 3 frames) are
  **uncited numerical tolerances**, inherited in spirit from the previous version. They are
  onset-of-motion detection tolerances, not physical criteria. Same standing as
  `DRIFT_THRESHOLD`. If they end up on a poster they need the Xia 2014 / Shah 2018 framing
  already recorded in CLAUDE.md, not a fabricated citation.
- Whether TOPPLE ever fires on real data is unknown, and per the sliding-pre-empts-toppling
  argument it may fire rarely or never. That would be a finding, not a bug.
- The classifier has never been run against real coupled output, because no such output
  with velocity columns exists yet.

## Next, in order

1. Fix vehicle solidification (blocks everything downstream).
2. Re-run v3 with the patched writer so timeseries carry `vx..wz`.
3. Run `classify_manifest` over the regenerated v3. Only that is reportable.
4. Decide what happens to the `to_csv` patch in Kumar's repo before that checkout is
   reset or re-pulled and the change is lost.
