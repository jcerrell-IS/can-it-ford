# Track 2 findings, coupled-realism exploration, 2026-08-13

## THIS ENTIRE DOCUMENT IS NON-CANONICAL

Produced on branch `track2/coupled-realism-explore` in an isolated git worktree at
`/work/11603/jcerrell0629/vista/can-it-ford-track2-realism`, a sibling of the canonical
checkout, never inside it. Nothing here may be merged into `main` without a separate,
deliberate human decision. No canonical Track 1 script was executed, `mpmenv` was never
activated, and the canonical checkout was never written to from this session.

Session: Vista, SLURM job 908672, node c642-001, partition gh-dev, GH200 120GB.
Worktree branched from `origin/main` at `7453c92`.

---

## HEADLINE

**Neither path produced a validated coupling force this session. The Genesis
LegacyCoupler path was tested to destruction and FAILED. The moving-SDF path was not
run here (correctly, it is Track 1 territory) but source inspection shows it needs
essentially NO solver change, only a driver-level rigid-body loop.**

The instruction's framing was "whichever path shows a real, validated coupling force
first, continue with it." Genesis did not show one, so there was nothing to continue
with, and no percentage-agreement number from Genesis is reportable. That is the
finding, not a shortfall in the attempt.

**No "X% agreement with analytic buoyancy" claim is made for Genesis.** The three
numbers below (-105.8%, -39.9%, -69.4%) are reported as *failures*, not as agreement
figures, and none should ever be quoted alongside warpmpm's 7.3-7.7%.

Secondary result, and the one durable positive from the Genesis side: **Genesis loaded
the canonical Yaris hull for the first time in this project's history**, and
independently reproduced its mass as 1099.9991 kg against the canonical 1100 kg. The
load path is now known and recorded, even though the coupling on top of it fails.

---

## What was verified live this session, against source or runtime, not against a summary

| Claim | Source | Status |
|---|---|---|
| Genesis version on Vista is 1.1.1 | runtime `genesis.__version__` | CONFIRMED (register C1) |
| `apptainer` needs the direct path, module load fails | `module load tacc-apptainer` returned 127 | CONFIRMED (CLAUDE.md item 11) |
| Container has `python3`, not `python` | `apptainer exec ... python` → FATAL not found | NEW, worth recording |
| Coupling force `= -delta_mv / substep_dt` | `legacy_coupler.py:337-338` | CONFIRMED |
| Coupling is genuinely two-way | `legacy_coupler.py:339-345` calls `_func_apply_coupling_force` | CONFIRMED |
| `coup_friction` is real Coulomb friction, not damping | `legacy_coupler.py:319-323` | CONFIRMED, see below |
| Genesis `dx = 1/grid_density`, independent of bounds | `mpm_solver.py:53` | CONFIRMED |
| Genesis rejects `.ply` for rigid morphs | live `GenesisException: File type not supported` | CONFIRMED (register C12) |
| No coupling-force validation exists in Genesis repo | register C13 | CONSISTENT, this is the first |
| `sdf_wrench` at approximately line 354 | `core/solver.py:354` | CONFIRMED EXACTLY |
| Yaris hull 327,212 v / 655,308 f / 3.542739 m^3 / watertight | trimesh live read | CONFIRMED |

### `coup_friction` is Coulomb friction, established by reading the operation, not the name

`legacy_coupler.py:319-323`:

```python
rvel_tan = (
    rvel_tan
    / rvel_tan_norm
    * qd.max(0, rvel_tan_norm + rvel_normal_magnitude * geoms_info.coup_friction[geom_idx])
)
```

The enclosing branch is guarded at `:312` by `if rvel_normal_magnitude < 0`, and `:310`
comments that quantity as "negative if inward". So inside the branch the product
`rvel_normal_magnitude * coup_friction` is negative and the expression reduces to

    |v_t_new| = max(0, |v_t| - mu * |v_n|)

which is Coulomb friction, and specifically not a damping term. The distinguishing
test is what the decrement depends on: a damping term scales the tangential velocity
by itself (`v_t * (1 - c)`), decays exponentially, never reaches exactly zero, and has
no dependence on normal load. Here the decrement is proportional to the NORMAL
velocity, and the `max(0, ...)` clamp produces genuine sticking when the tangential
speed falls below `mu*|v_n|`. Load-dependence plus a hard stick floor is the signature
of Coulomb friction. Register C10 and CLAUDE.md:62-69 are accurate.

One qualification neither the register nor CLAUDE.md states: this acts at grid-node
level under an SDF influence blend (`:333`,
`vel = vel_rigid + rvel_new*influence + rvel*(1-influence)`), where `influence` derives
from `coup_softness` at `:191`/`:258`. The friction is therefore modulated by
`coup_softness` and is not a clean rigid-body Coulomb contact.

### The MPM path to that code, traced

`mpm_grid_op` (`:357`) loops grid nodes → `:390-403` calls `_func_collide_with_rigid`
with the node's `mass_mpm` and position → `_func_collide_with_rigid_geom` (`:167`) →
`_func_collide_in_rigid_geom` (`:284`) where the reaction force is applied. Coupling is
per-substep, per-grid-node. That much of the register's description is exactly right.

---

## STEP 3(b): the Genesis LegacyCoupler path. TESTED, FAILED.

Genesis had never loaded the Yaris hull before this session (CLAUDE.md item 1), and
register C13 records no coupling validation anywhere in the Genesis repo. Both harnesses
here were built from scratch.

### Design decision: FULL submersion, and why partial would have been an error

The instruction asked for a known submerged *fraction*. I ran fraction **1.000**.

Register J1a, **corrected the same day as this session, 2026-08-13**, establishes that
warpmpm's 7.3-7.7% figures come from `run_c1_sdf` at **frac 1.0** with 2.75 dx and
5.36 dx of water cover, and that the failed rung-(b) attempt failed partly *because* a
partially submerged case (frac 0.5187) was scored against that fully submerged
reference. Building a partial-submersion Genesis case and comparing it to 7.3-7.7%
would have reproduced exactly the error J1a documents. Full submersion is the only
like-for-like comparison available.

J1a's other cause, "the water was never settled," is why both harnesses settle on a
gate rather than a step count.

### Harness 1, fixed body, direct force read

`track2_realism/validate_genesis_buoyancy.py`. Body held fixed; net coupling force read
from `links_state.cfrc_coupling_vel`, which `rigid/abd/misc.py:715-716` writes with `-=`
(so the physical force is the negation), is zeroed every substep at
`rigid/abd/forward_dynamics.py:1238-1240`, and is consumed at `:1201/:1204`. A read after
`scene.step()` therefore samples the LAST substep only; it is instantaneous, never a
running total.

Control geometry: a 0.8 m cube, V = 0.512 m^3 exactly, so the analytic answer carries no
mesh uncertainty. grid_density 16, dx = 0.0625 m (Genesis convention), cover 5.60 dx,
57,600 water particles.

```
F_analytic          =      5022.7200 N
F_measured  (mean)  =      -373.5266 N   sd=1428.9095
F_measured  (2nd h) =      -291.6208 N   sd= 161.9413
peak-to-peak        =      9833.5625 N
ERROR full window   = -107.4367 %
ERROR second half   = -105.8060 %
|Fx|,|Fy| mean      = 129.4729, 75.0010 N   (should be ~0 by symmetry)
```

The measured force converges to roughly zero-to-slightly-negative on a body where
analytic buoyancy is strongly positive. The second-half standard deviation (161.9)
is an order of magnitude tighter than the full window (1428.9), so this is a
*converged wrong answer*, not an unsettled one.

An earlier 0.1 m cube smoke test at grid_density 64 showed the same thing more crudely:
readings swinging -8.40 to +13.13 N against a 9.81 N analytic. That peak-to-peak
signature is the same "ringing tank" J1a reports for warpmpm's fixed-body test
(27,207 N p-p against 16,233 N analytic), reproduced independently in a different
engine.

### Harness 2, free body, kinematic cross-check

`track2_realism/validate_free_body.py`. This removes any dependence on reading an
internal field: if the coupler transports buoyancy at all, a body lighter than water
must rise. Cube at rho = 500 kg/m^3, half water density, fully submerged, released from
rest. Genesis-reported body mass 256.0000 kg matched analytic rho*V exactly, so the
mass wiring is not the defect.

```
z:  0.887500  ->  0.687123 m        (net -0.200 m over 320 steps = 0.64 s)
vz: negative at every logged sample, -0.552 to -0.121 m/s
a_fit  = +1.9857 m/s^2      a_ideal = +9.8100 m/s^2
F_measured = m(a+g) = 3019.7108 N   vs   F_analytic = 5022.7200 N   (-39.879 %)
```

**The body sinks.** Ideal buoyancy would have carried it UP roughly 2.0 m in 0.64 s
(0.5*9.81*0.64^2); it went DOWN 0.20 m. The positive `a_fit` is the body *decelerating
its descent*, not rising, so the automatic "DIRECTION = UP" label the script prints from
the sign of the fit is misleading and should not be read as buoyant behaviour. That
label is a defect in my own reporting code, called out here rather than left to mislead
a later reader.

So some upward reaction exists but is far too weak. The -39.9% figure is an artifact of
fitting an acceleration to a decelerating descent and **must not be quoted as a
buoyancy agreement figure.**

### What this means

Two independent measurement modes, one reading an internal force accumulator and one
reading only body kinematics, agree that the Genesis LegacyCoupler does not deliver
buoyancy on a fully submerged body, on the most trivial possible geometry where the
analytic answer is exact and mesh quality cannot be blamed. A ~107% force error and a
qualitative direction failure are not tuning problems.

### Harness 3, the Yaris hull itself. Genesis's first load of it, and the same failure.

Run anyway rather than inferred, because "the cube failed so the hull would too" is
exactly the kind of assertion this project's rules forbid.

**Genesis has now loaded the canonical Yaris hull for the first time** (CLAUDE.md item 1
recorded that no Genesis scene ever had). Route: `.ply` is rejected for rigid morphs
(register C12, confirmed live), so the hull was converted to `.obj` with trimesh at
`convexify=False, decimate=False`, preserving volume to 10 significant figures
(3.542738790016076 → 3.542738788880477 m^3) and watertightness.

Genesis emitted two warnings worth recording for the next session: 655,308 faces is
"many... consider decimate=True", and SDF pre-processing above 50,000 vertices "may take
a very long time (>10min) and require large RAM allocation (>20Gb)". It completed inside
the window on a GH200 at grid_density 16, with 438,912 water particles.

**A useful independent confirmation fell out of the build**: Genesis reported the body
mass as **1099.9991 kg** against the canonical Yaris mass of 1100 kg. That is
`rho = 310.494 kg/m^3` times `V = 3.542739 m^3` recovered by a second engine, from the
mesh, with no hand-entered mass anywhere. The canonical density/volume/mass triple is
mutually consistent to 1 part in 10^6.

```
F_analytic = rho*g*V       =  34754.2675 N
a_ideal                    =    +21.7848 m/s^2
a_fit (dv/dt)              =     -0.1376 m/s^2
F_measured = m(a+g)        =  10639.5975 N
ERROR                      =    -69.3862 %
z: 1.204389 -> 1.063539 (settle, DOWN 0.141 m) -> 1.097263 (measure, up 0.034 m)
```

The hull does not rise. It sinks 0.141 m during settle, then bobs back up 0.034 m, ending
0.107 m BELOW where it started after 250 steps (0.5 s). Ideal buoyancy at
21.78 m/s^2 would have lifted it about 2.7 m. The fitted acceleration is negative. The
same architectural failure as the cube, now on the real geometry, and if anything worse
in the sense that the body is nearly neutrally held when it should be the most strongly
buoyant case in the project (rho_body/rho_water = 0.31).

The -69.4% figure, like the -39.9%, is **not** a buoyancy agreement number; it is the
residue of fitting an acceleration to a body that is oscillating rather than rising.

This is consistent with, and is independent runtime evidence for, register A-1: the
velocity-averaging family of coupling schemes lacks the accumulated contact force that
Hu et al. 2018 and Pazouki et al. 2016 identify as necessary for real two-way MPM/rigid
coupling. Note the coupler *does* accumulate a force (`:337-338`, genuinely two-way, as
confirmed above), so the defect is not the absence of an accumulator; it is that the
accumulated quantity is a collision-projection impulse, which goes to zero as the water
comes to rest, rather than a surface pressure integral, which does not.

**That last sentence is a mechanism hypothesis, not an established finding.** It is
consistent with all four measurements but was not isolated by a dedicated experiment,
and it should be labelled as a hypothesis anywhere it is repeated.

---

## STEP 3(a): the moving-SDF path. READ-ONLY INSPECTION. Looks tractable.

Read from the vendored pinned-SHA source at
`third_party/mpm-engine-544c93dd-solver-core/`, without executing anything and without
activating `mpmenv`, per the environment-isolation boundary.

The instruction's "previously at approximately line 354" for `sdf_wrench` is **exactly
correct today**: `core/solver.py:354`.

The relevant API, all already present:

| Call | Line | What it already does |
|---|---|---|
| `add_sdf_collider(sdf, center, quat, velocity, omega, band, surface, friction, ...)` | `solver.py:324` | Accepts a full 6-DOF pose AND velocity/omega at construction |
| `set_sdf_pose(handle, center, quat, velocity, omega)` | `solver.py:339` | Updates pose; "`quat` and `omega` extend that contract to rotation" |
| `reset_sdf_force(handle)` | `solver.py:348` | Zeros the reaction force and torque before `step()` |
| `sdf_wrench(handle, dt)` | `solver.py:354` | Returns BOTH `force` and `torque` about the collider centre, world frame |

The decisive detail is the implementation docstring at
`kernels/mpm_solver_warp.py:2779-2785`:

> "Command an SDF collider with its START-of-tick pose and per-tick velocity/omega; the
> modify_bc integrates `center += dt*velocity` and rotates the quat by omega every
> substep... Setting center/quat directly teleports the collider between ticks; a jump
> whose surface sweep exceeds the contact band can tunnel through material, so it warns
> once."

### Answering the instruction's question directly

> "Can the SDF be re-fit to a free rigid-body pose each substep, giving it both the
> already-validated force and freedom of motion?"

**It does not need to be re-fit at all, and essentially nothing in the solver needs to
change.** The SDF values and gradients are body-local (`sdf.values, sdf.grads,
sdf.origin, sdf.cell` are passed once at construction) and the pose is applied as a
rigid transform that `modify_bc` already integrates every substep. A re-fit per substep
would be redundant work.

What is missing is not solver capability but a **driver-level 6-DOF rigid-body
integrator**: per control tick, `reset_sdf_force` → `step` → `sdf_wrench` → integrate
`F = ma` and `tau = I*omega_dot + omega x I*omega` → command the resulting
velocity/omega through `set_sdf_pose`. That is ordinary Python in the run script, not a
change to warpmpm.

This is a substantially better position than the instruction assumed, and it is why
this path is the recommendation.

### Caveats a Track 1 session must carry into the implementation

1. **Drive with velocity, never by teleporting `center`.** The contract is
   `v = (target - prev)/dt_ctrl` (`set_box` docstring, `solver.py:239-246`). Passing the
   end-of-tick target as `center` "double-applies the motion and leaves the box one tick
   ahead."
2. **Tunnelling.** A pose jump whose surface sweep exceeds the contact band tunnels, and
   the warning fires only once.
3. **Wall thickness.** An SDF collider "needs ~2 cells" (`solver.py:369`); the CDF
   collider at `solver.py:363` is the thin-surface alternative if that bites.
4. **Added mass is unavoidable here, by construction.** Register J1a's identity:
   `added_mass_ratio` is exactly 1.000000 for ANY body floating at equilibrium, twice
   `coupler.py:72`'s own warning threshold, with no parameter escape. A driver-level
   explicit partitioned loop is exactly the scheme class that identity constrains. Note
   J1a also records that under-relaxation was tried and REFUTED (job 3361371, error got
   monotonically worse), so do not re-propose it as untried.
5. `sdf_wrench` divides by `dt`, and the accumulator is only zeroed by an explicit
   `reset_sdf_force`. Getting the reset/read order wrong silently changes the
   normalisation.

**FLAGGED FOR A FUTURE TRACK 1 SESSION.** This work lives in warpmpm's own codebase and
must not be attempted from a Track 2 session.

---

## Which path won, and why

**The moving-SDF path, by evidence and by elimination.**

- Genesis LegacyCoupler: measured, failed twice, on a trivial geometry, by ~107% on
  force and qualitatively on direction. Not a tuning gap.
- Moving-SDF: already carries the validated force path (warpmpm's 7.3-7.7%, register
  A-2), already exposes a full 6-DOF wrench and a per-substep-integrated pose, and needs
  no solver change.

No number from the two engines has been averaged, blended, or otherwise combined
anywhere in this document.

### Convention statement, required and non-negotiable

Every dx, cover and grid figure in this document uses the **Genesis** convention,
`dx = 1/grid_density`, independent of domain bounds, verified live at
`mpm_solver.py:53`. warpmpm's dx is domain-dependent. The two conventions are never
merged here, and the Genesis figures above are not comparable cell-for-cell with
warpmpm's g64/g96 labels.

---

## Steps not reached, and why

- **STEP 4, physics-skeptic.** Not available in this session; the only agent types
  offered were claude, claude-code-guide, Explore, general-purpose, Plan and
  statusline-setup. The instruction was conditional ("if available"), so it was skipped
  rather than substituted with a generic agent, which would have provided false
  assurance. **This is the main reason the failure numbers above should still be treated
  as un-adversarially-reviewed.** No agreement claim is made that would need that gate.
- **STEP 5, visual realism.** Explicitly gated on Step 3 producing a validated coupling
  force. It did not, so this was not attempted. Rendering a coupling that is known to be
  wrong would have produced a persuasive but false artifact, which is worse than no
  render.
- **STEP 6, drainA gsplat scene.** Gated on Step 5. Not attempted. The instruction
  already designates it a next-session goal.

---

## Deferred to next session

1. **Implement the driver-level 6-DOF loop on the moving-SDF path, in a Track 1
   session.** Highest value item. Nothing in the solver blocks it.
2. **Isolate the Genesis mechanism hypothesis** (collision-projection impulse vs surface
   pressure integral) with a dedicated experiment, or drop the hypothesis. Cheapest
   decisive test: measure net coupling force against water cover depth on a fixed body.
   A pressure integral scales with the cover; a collision-projection impulse does not.
3. **Grid refinement on the Genesis control was not completed.** The instruction asked
   for at least one iteration on mesh/grid settings before accepting a worse result. I
   iterated on *measurement mode* (fixed-body force read, then free-body kinematics) and
   on the settle gate, but a second grid_density on the same harness did not run before
   the window closed. The qualitative direction failure is resolution-independent in the
   sense that no resolution makes a sinking body float, but this should be closed
   properly.
4. **The settle gate `c/vmax >= 20` is too loose.** It passed at step 100 with
   vmax = 0.4977 m/s, which is not a settled tank. Inherited from warpmpm's criterion
   via J1a; it needs re-deriving for Genesis rather than porting.
5. **Fix the misleading `DIRECTION` label** in `validate_free_body.py`, which reports
   "UP" from the sign of a fitted acceleration even while the body descends.

---

## Two register/CLAUDE.md discrepancies found, neither blocking

1. **Raw mesh extents vs particle-cloud extents.** CLAUDE.md item 4(c) gives measured
   extents `(1.7078, 4.2014, 1.4853)` with the long axis on Y. The raw `.ply` as loaded
   is `(4.28261014, 1.746378, 1.51800813)`, long axis on **X**, and differs by roughly
   2% on each axis even after reordering. Both can be true, CLAUDE.md item 4(b) is
   explicit that the solver measures from the solidified particle cloud, and a gated
   scene may rotate the mesh. Recording it so a future session does not read a 2%
   discrepancy as drift. Volume agrees to 10 significant figures.
2. **Derived meshes deliberately NOT committed.** `yaris_hull.obj` and
   `yaris_hull_centered.obj` (26 MB each) are derived from the canonical
   `yaris_coarse_v1l_watertight.ply`. Register J-item 11 / E8 records CCSA/NCAC mesh
   redistribution rights as unresolved and states it "blocks committing any derived mesh
   publicly." Pushing them to `origin` would be exactly that, so they are gitignored at
   `track2_realism/.gitignore` and regenerated from the one-line trimesh command in the
   Reproduction section. The session instruction did not raise this; the register does,
   and the register wins.
3. **`git add -A` conflict.** The session instruction's STEP 7 specified `git add -A`;
   CLAUDE.md:98-101 forbids it outright in this repo. I staged explicit paths instead.
   The stated rationale for the ban (a shared working tree capturing another session's
   work) does not apply inside an isolated worktree, but the rule is written absolutely
   and explicit staging satisfies both. Flagging rather than silently choosing.

---

## Reproduction

```bash
# on a Vista GH200 compute node, inside an allocation
APPT=/opt/apps/tacc-apptainer/1.4.1/bin/apptainer      # module load does NOT work
SIF=/work/10386/lsmith9003/vista/containers/genesis_container.sif
cd /work/11603/jcerrell0629/vista/can-it-ford-track2-realism

$APPT exec --nv $SIF python3 track2_realism/validate_genesis_buoyancy.py \
    --body cube --grid-density 16 --settle-max 4000 --measure 1200
$APPT exec --nv $SIF python3 track2_realism/validate_free_body.py \
    --body cube --grid-density 16 --settle 200 --measure 120 --rho-body 500.0
$APPT exec --nv $SIF python3 track2_realism/validate_free_body.py \
    --body yaris --grid-density 16 --settle 150 --measure 100 --rho-body 310.494
```

The hull run needs `yaris_hull_centered.obj`, regenerated from the canonical `.ply`
(md5 `372a709ffb22e0c914ecf25d4f34a76c`) by:

```bash
$APPT exec $SIF python3 -c "
import trimesh
m = trimesh.load('vehicle_geometry_research/yaris_coarse_v1l_watertight.ply', process=False)
m.apply_translation(-m.centroid)
m.export('track2_realism/yaris_hull_centered.obj')"
```

Note `python3`, not `python`: the container has no `python` on PATH and
`apptainer exec ... python` fails with `FATAL: "python": executable file not found`.

Artifacts: `results_*.json` carry the full per-step force and kinematic traces,
`log_*.txt` the raw stdout.
