# The C2 crash is the rigid box falling through the floor plane, on z, named at last

Date 2026-08-25. Job **937476** on Vista, `gh`, 00:10:31, sacct COMPLETED 0:0.
Re-runs job `894676`'s four C2 arms against the patched P2G edge guard.
Approved by Josie as an edit to the pinned vendored engine at `544c93dd`.

## What was asked and what the answer is

The 2026-08-07 diagnostic spec asked for three things the guard did not report: per-axis
minima rather than one global figure, the offending particle and its material, and the
correct axis label instead of a hardcoded `"x"`. All three are now implemented, and the
commissioning question was whether the new output **changes the root-cause attribution**.

**It does not overturn it. It confirms it, names it, and kills a competing reading that
the old message actively invited.** The old text reported a global minimum across all
guarded columns under the label `x`. In every one of these four arms that global minimum
belongs to **z**, so the message printed z's number and called it x.

## The four arms, all four crashed, all four identical in kind

`--variant c2 --depth-cells 18 --settle-frames 600 --max-frames 2500`, the same
parameters as 894676. Read directly from the `RuntimeError` text in each arm's log.

| arm | dx | guard lower limit `1.5 dx` | z min reached | past the limit | past it, as % of dx | particle | material |
| --- | --- | --- | --- | --- | --- | --- | --- |
| g64 off0 | 0.1472 | 0.2208 | 0.2184 | 0.0024 m | 1.63 | 447260 | 8, rigid |
| g64 off2 | 0.1472 | 0.2208 | 0.2202 | 0.0006 m | 0.41 | 448880 | 8, rigid |
| g96 off0 | 0.0981 | 0.1472 | 0.1462 | 0.0010 m | 1.02 | 1535513 | 8, rigid |
| g96 off2 | 0.0981 | 0.1472 | 0.1472 | 0.0000 m | 0.00 | 1513051 | 8, rigid |

**Every arm fails on z. Every offending particle is material 8, the rigid body.** Not
water, not a lateral escape, and not resolution-dependent: g96 fails exactly as g64 does,
and the offset arm fails exactly as the zero-offset arm does.

## Why the old message pointed the wrong way

x and y are nowhere near their limits in any arm. Measured, same text:

| arm | x extent | y extent | allowed |
| --- | --- | --- | --- |
| g64 | [0.5521, 8.8697] | [0.5521, 8.8697] | [0.2208, 9.0537] |
| g96 | [0.5647, 8.8574] | [0.5644, 8.8574] | [0.1472, 9.1764] |

The smallest x is 0.5521 against a lower limit of 0.2208, so x clears its bound by 2.5x.
The old message would have printed `x in [0.2184, 8.8697]`, pairing **z's** minimum with
**x's** maximum under a single `x` label. That reads as a particle escaping laterally
toward the x wall, and it is the reason the fix advice the guard itself prints, "Enlarge
grid_lim or add a bounding box / wall collider", is the wrong advice for this failure.
Nothing here is escaping sideways.

Note that `periodic_x` is OFF in the C2 scene, so all three axes are guarded and the
label `x` was not *structurally* wrong here, only *numerically* wrong. The
periodic-x case, where the label names an axis that is not checked at all, is covered
by `tests/test_edge_guard_diagnostic.py` case 1.

## The real failure is upstream of the guard, by about a quarter of a metre

`validate_coupling_force.py` puts the floor at `floor = 3.0 * DX_CANON` with
`DX_CANON = LIM / 64.0` and `LIM = 9.421742313727737`, so **the floor plane sits at
z = 0.4416 m**, the same absolute height on both grids. It is a real collider, added as
`s.add_plane((0, 0, self.floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)`.

Against that floor, the rigid box's lowest particle when the guard fired:

| arm | floor | lowest rigid particle | **below the floor plane by** |
| --- | --- | --- | --- |
| g64 off0 | 0.4416 | 0.2184 | **0.2232 m** |
| g64 off2 | 0.4416 | 0.2202 | **0.2214 m** |
| g96 off0 | 0.4416 | 0.1462 | **0.2954 m** |
| g96 off2 | 0.4416 | 0.1472 | **0.2944 m** |

**The box is a fifth to a third of a metre below a floor it should be resting on.** The
P2G edge guard is not detecting the failure; it is a backstop that trips a long way
after the failure has already happened, once the box has fallen far enough to approach
z = 0. That is why the excursion past the guard is sub-millimetre to 2.4 mm: the guard
fires on the crossing, so the number it reports measures one step of travel, not the
severity of anything.

This is the same conclusion `20dd999` reached by its own route, and its commit message
says so in as many words: "Deepen C2 water to 18 cells; the box was sinking through the
floor plane". `--depth-cells 18` was the response, it is what these arms run, and **it
does not prevent the fall.** `docs/C1_ROOT_CAUSE_2026-08-07.md` unified C1 and C2 on
box-fall with restitution 0, and the floor here is indeed `restitution=0.0`.

So three routes now agree, and they have separate origins: a commit-message diagnosis
from 2026-08-07, the C1 root-cause analysis, and this per-particle instrument. What this
run adds that neither had is the **material tag**: the offender is confirmed material 8,
the free-rigid path, in all four arms.

## The mechanism, stated as an inference and labelled as one

VERIFIED by direct read: the floor plane exists, its parameters are
`slip / friction 0.0 / restitution 0.0`, and the rigid box is far below it.

INFERRED, not instrumented here: a plane collider writes a **grid-node** velocity
condition. Material 8 is the free-rigid path, which per CLAUDE.md item A-1 is a
mass-weighted grid velocity average with **no force accumulator**, and the body's
particles are placed by its own rigid transform. A grid-node velocity BC therefore has no
guaranteed route by which to arrest a rigid body integrated that way, which would explain
a clean pass-through rather than a bounce or a rest. **This has not been measured**, and
it should not be quoted as established. The falsifiable test is direct: log the rigid
body COM z per frame against the floor height and check whether the plane ever changes
its velocity at all.

The `com_frame` trace in `c2diag_g64_off0.log` shows COM z descending monotonically
(1.3387, 1.3337, 1.3290, 1.3246 over frames 257 to 260) with no inflection at the floor,
which is consistent with pass-through and inconsistent with contact. That is one arm's
trace read by eye, not a fitted result.

## Two things that reproduced exactly

**The COMPLETED-vs-crashed contradiction is still live.** `sacct` reports 937476
COMPLETED with ExitCode 0:0 while all four python invocations raised. The sbatch wrapper
does not propagate the failure, exactly as recorded for 894676 in
`docs/CONTEXT_CENSUS_2026-08-07.md`. **Never take sacct COMPLETED as evidence a C2 arm
produced anything.**

**No JSON was produced by any arm**, same as 894676. The run dies before the writer.

## What changed in the engine, and how to undo it

Patched: `core/solver.py`, `_update_grid_box` and a new `_edge_violation_report` helper.
**No numerical behaviour changes.** The guard condition is unchanged; the new code runs
only inside the `raise` path and builds a different string. Any arm that crashed before
still crashes, which is what makes it usable for attribution rather than a repair.

The vendored mirror in this repo was confirmed byte-identical to Vista's live engine
before the change: both hashed `45279890562eac6c31107a5854354c8a`, engine clean at the
pin `544c93dd02cb9c7ead89e1155a62967243244fce` with no unpushed commits. The patched file
hashes `bd3a41f5e74efb1cbb691e3258006124` in both places.

**Vista's engine is currently PATCHED and therefore no longer matches its pin hash.**
That is a deliberate end state, not an oversight: the diagnostic is worth having for the
next crash. The original is preserved and the revert is one command:

```
cp $WORK/can-it-ford/mpm-engine/src/warpmpm/core/solver.py.bak-20260825-c2diag \
   $WORK/can-it-ford/mpm-engine/src/warpmpm/core/solver.py
```

Job script: `$WORK/can-it-ford/scripts/c2diag.sbatch`, a copy of `c2only.sbatch` with
identical arms and a 00:25:00 walltime instead of 01:30:00, because 894676 asked 90
minutes and ran in 11 and an oversized walltime blocks backfill for nothing. Outputs are
named `c2diag_*` so the 2026-08-07 artifacts are untouched.

## What this does not settle

The guard's own comment names kernel-side index clamping as the fix "if a real scene ever
hits this". A real scene has now hit it four times out of four. But clamping the index
would only stop the crash; it would not stop the box falling through the floor, and a
silently-clamped rigid body below its floor is worse than a crash. **Fix the floor
contact, not the guard.** The guard is doing its job.
