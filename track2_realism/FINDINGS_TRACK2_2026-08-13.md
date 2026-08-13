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

The Genesis failure is characterised, not just observed. **The decisive point: the
best-converged measurements are not the best-agreeing ones.** Under a strict settle gate
the numerical noise collapses to sd ~8 N and peak-to-peak ~50 N, and the measured force
is still wrong by -86% to -104% against analytic buoyancy. The disagreement cannot be
attributed to ringing, resolution, settling, mesh quality, mass wiring or coupler choice,
because each of those was removed or ruled out in turn. `LegacyCoupler` is the only
MPM-rigid path in Genesis 1.1.1 and exposes no scheme-level tunable. Eight runs, two
independent measurement modes, three geometries including the real hull, two grid
densities, three cover depths, two settle gates.

One sub-claim made earlier in this session was **retracted** on better data: see the
depth-independence retraction in the mechanism section.

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

### Grid refinement: the failure is resolution-independent

The instruction required at least one iteration on mesh/grid settings before accepting a
worse result. Free cube, grid_density 16 → 32, a genuine 2x refinement (water particles
57,600 → 460,800, 8x):

| grid_density | dx (m) | particles | a_fit (m/s^2) | F_measured (N) | error |
|---|---|---|---|---|---|
| 16 | 0.0625 | 57,600 | +1.9857 | 3019.7108 | -39.879 % |
| 32 | 0.03125 | 460,800 | +1.5973 | 2920.2619 | -41.859 % |

The error moves 2 percentage points, in the WRONG direction, and the body sinks at both
resolutions (gd32: z 0.793750 → 0.523660, net -0.270 m). Refinement does not converge
toward the analytic answer. This is the signature of an architectural defect, not a
discretization error, and it is consistent with register L-5 / Steffen, Kirby and Berzins
2008 on MPM losing convergence under refinement at fixed particles-per-cell, though that
mechanism is not established as the cause here.

### There is no better coupler to switch to. Checked, not assumed.

The obvious objection to everything above is "you picked the wrong coupler." Genesis
1.1.1 ships three (`engine/couplers/__init__.py`): `LegacyCoupler`, `SAPCoupler`,
`IPCCoupler`. Verified live:

- `mpm_grid_op` is defined in **`legacy_coupler.py` only**.
- `sap_coupler.py` contains **zero** occurrences of `mpm`. It is the Semi-Analytic Primal
  contact solver from Drake, for rigid/FEM contact.
- `ipc_coupler/` contains **zero** occurrences of `mpm`.
- `LegacyCouplerOptions` (`options/solvers.py:80-113`) exposes only on/off booleans
  (`rigid_mpm`, `rigid_sph`, ... all defaulting True). There is **no scheme-level
  tunable** — nothing to trade accuracy against, no alternative contact model.

**LegacyCoupler is the only MPM-rigid coupling path in Genesis 1.1.1**, and it has no
knob that could change the result. The failure cannot be attributed to a bad option
choice, and cannot be fixed from the options layer.

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

**That last sentence began as a hypothesis and was then tested. Two versions of it were
refuted and a sharper statement survived.** The working is below, kept in full because
the refutations are the useful part.

### Mechanism: two hypotheses killed, one statement survives

**Hypothesis 1, "the coupler registers the overburden (weight of water above)."
REFUTED, though the first attempt to refute it was itself wrong, see the retraction
below.** Analytic buoyancy on a fully submerged body is independent of depth, so
depth-sensitivity is a clean discriminator. Fixed cube, grid_density 16, cover swept
2.40 / 5.60 / 11.20 dx under the ORIGINAL loose settle gate (`c/vmax >= 20`):

| cover | F (2nd half) | sd | verdict |
|---|---|---|---|
| 2.40 dx | -777.5084 N | 54.2 | converged |
| 5.60 dx | -779.7575 N | 752.7 | marginal |
| 11.20 dx | -308.2206 N | 1306.3 | **not converged**, sd is 4x its own mean |

#### RETRACTION, same session: "the force is depth-independent" is WITHDRAWN

The first two rows above agree to 0.3%, and I read that as depth-independence. **That
reading was an artifact of an inadequate settle and is withdrawn.** Re-running the
matched pair under a STRICT gate (`c/vmax >= 200`, i.e. vmax <= 0.083 m/s, settle cap
6000) changes the answer:

| cover | settle gate | settled at | F (2nd half) | sd | peak-to-peak | error |
|---|---|---|---|---|---|---|
| 2.40 dx | strict | step 2750 (MET) | **-197.7128 N** | 8.21 | 63.58 N | -103.936 % |
| 11.20 dx | strict | NOT MET at 6000 | **+712.0993 N** | 8.28 | 46.59 N | -85.822 % |

Under a real settle the two covers do **not** agree: -197.7 N against +712.1 N. The
apparent depth-independence existed only in the under-settled data. This is the same
trap J1a documents, caught here in my own numbers, and it is recorded rather than
quietly overwritten.

The strict settle is dramatically better numerically: ringing collapses by roughly 150x
(peak-to-peak 8345 N → 64 N) and the standard deviation falls from 465.7 to 8.21. These
are now precise measurements.

**Hypothesis 1 stays refuted, but on better evidence.** Overburden would push the body
DOWN harder as cover deepens. Going from 2.40 to 11.20 dx adds 0.55 m of water over a
0.64 m^2 top face, an overburden weight of about 3453 N downward. The measured force
moves +909.8 N, i.e. *upward*, roughly a quarter of that magnitude and in the opposite
direction. Not overburden.

**Hypothesis 2, "the force is the weight of ~2 grid layers resting on the top face."**
Post-hoc arithmetic fitted the converged points to within 1%:
`0.64 m^2 * 2 * 0.0625 m * 1000 * 9.81 = 784.8 N` against a measured -777.5 N. Its
prediction was that halving dx halves the force, to about -392 N. **Tested and REFUTED.**

**What survived, and it is a stronger result than either hypothesis.** Fixed cube,
cover held at 0.15 m, grid_density 16 → 32:

| grid_density | particles | F (2nd half) | sd | peak-to-peak | error | settled at |
|---|---|---|---|---|---|---|
| 16 | 49,600 | -599.9761 N | 465.7 | 8345.19 N | -111.945 % | step 100 |
| 32 | 396,800 | **+123.6381 N** | 50.7 | 593.91 N | -97.538 % | step 700 |

Under refinement the spurious force collapses by roughly 5x, the ringing collapses by
14x (peak-to-peak 8345 → 594), and the measured force heads toward **zero** — not toward
the analytic 5022.72 N. The error improves only from -112% to -97.5% precisely because
-100% *is* the zero-force limit.

**THE SURVIVING STATEMENT, and it is the one to carry forward.** Every measured force,
across two grid densities, three cover depths, two settle gates and three geometries,
lands between roughly -200 N and +712 N against an analytic +5022.7 N. The errors span
-86% to -116%. Critically, **the best-converged measurements are not the best-agreeing
ones**: under the strict settle the noise falls to sd ~8 N and peak-to-peak ~50 N, and
the answer is still wrong by -86% to -104%.

That is the whole finding. The disagreement cannot be blamed on ringing (removed),
resolution (refined, twice), settling (gated strictly), mesh quality (an exact cube),
mass wiring (reproduced to 1e-6), or coupler choice (there is no other). The Genesis
LegacyCoupler simply does not transport hydrostatic buoyancy to a rigid body.

The best available mechanism reading remains register A-1's: the quantity accumulated at
`:337-338` is a collision-projection impulse, which has no reason to equal a surface
pressure integral, and the branch that produces it only fires when water moves INTO the
surface (`:312`, `if rvel_normal_magnitude < 0`). The coupler is a collision handler
being asked to do hydrostatics. **This is a reading consistent with all the data, not a
mechanism isolated by a decisive experiment**, and it should keep that label.

One supporting detail worth carrying: within a single strict-settle run, as the water
came to rest (vmax 0.438 → 0.199 m/s) the measured force decayed alongside it
(-796.7 → -393.5 N). Force tracking the residual water motion rather than the constant
displaced volume is what a collision-projection quantity does, and is not what a pressure
integral does.

Also recorded, because it is diagnostic in its own right: the gd16 number moved from
-777.5 N to -600.0 N when 2 dx of **air headroom** was added above the free surface, a
purely geometric change well away from the body. A real buoyant force is insensitive to
headroom.

`settled_at` moved 100 → 700 under refinement, echoing J1a's warpmpm observation that the
finer grid needed far more settling (3,894 substeps at g64, 12,416 at g96).

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
2. **DONE this session, no longer deferred.** The mechanism was isolated: cover sweep
   plus a grid-refinement prediction test refuted two hypotheses and established that the
   coupler converges to zero force. See the mechanism section above.
3. **DONE this session, no longer deferred.** Grid refinement ran on both harnesses
   (free body gd16 vs gd32, fixed body gd16 vs gd32). The failure is
   resolution-independent in direction and converges to zero in magnitude.
4. **DONE this session, no longer deferred.** The deepest cover point was re-run under a
   strict gate. It overturned the depth-independence sub-claim, which is retracted above.
5. **DONE this session.** The loose `c/vmax >= 20` gate was replaced by `>= 200` and the
   difference is large: ringing fell ~150x and one conclusion was overturned. **Standing
   recommendation: `c/vmax >= 20`, inherited from warpmpm via J1a, is not fit for
   purpose in Genesis and should not be ported again.** Note that even `>= 200` was NOT
   reached at 11.20 dx cover within 6000 steps, so deep tanks need a different strategy
   than brute-force settling.
6. **DONE this session.** The misleading `DIRECTION` label in `validate_free_body.py` now
   reports direction from net displacement and end velocity, and explicitly states that
   the sign of `a_fit` is not direction. The free-body results above were produced BEFORE
   this fix, so their printed `DIRECTION` lines are the old, misleading ones; the
   underlying z and vz series in the JSON are unaffected.
7. **DONE this session.** The 2 dx air-headroom fix was added to `validate_free_body.py`
   as well. The free-body results above predate it; the change affects domain height only
   and those runs did not trip the boundary.
8. **Re-running the free-body cases under the strict gate is NOT needed to support the
   conclusion**, and the force balance is why. The largest upward force measured under
   any strict-settle configuration is **+712.1 N**. The bodies weigh:

   | body | mass | weight | max measured upward force | shortfall |
   |---|---|---|---|---|
   | cube, rho 500 | 256.0 kg | 2511.4 N | +712.1 N | 3.5x too small |
   | Yaris hull, rho 310.494 | 1100.0 kg | 10790.9 N | +712.1 N | 15.2x too small |

   A body cannot rise while the upward force on it is a third to a fifteenth of its
   weight, so "bodies do not rise" follows from the strict-settle force measurements
   directly and does not depend on the loosely-settled free-body runs. Those runs remain
   useful as an independent qualitative cross-check, not as the load-bearing evidence.
   A direct strict-gate free-body run is still worth doing for completeness, and is noted
   as optional rather than blocking. It is also intrinsically awkward: a free body drifts
   during any settle, so "settle then release" is not cleanly definable for it, which is
   the reason the fixed-body measurement is the primary one here.

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

## Appendix: rigid-mass citation check (mid-session request, verified, no edits made)

Asked mid-session to confirm commit `35b7ed0` had already repointed the rigid-mass
citation from `:851-853` to `:856`. Verified, read-only:

- `35b7ed0` "Correct the rigid-mass citation from :851-853 to :856 in the C1/C3 harness",
  Sat Aug 8 2026, confirmed an ancestor of this branch's HEAD.
- All three sites read `:856`, checked in BOTH the committed `origin/main` state and the
  LIVE canonical working tree: `simulation/validate_coupling_force.py` (two sites) and
  `scripts/c1sdf.sbatch:18`.
- **Line drift worth noting**: the second site is at `:740` in the committed file but
  `:908` in the live canonical working tree. A concurrent Track 1 session has ~168 lines
  of uncommitted edits above it. This is CLAUDE.md's "do not cite line numbers
  positionally" hazard occurring live, in the very file being audited for a line-number
  citation.
- No stale `:851-853` remains in `simulation/`, `scripts/`, `analysis/` or `renders/`.
  The only remaining occurrences outside `data/coupling_validation/` are three `.bak*`
  snapshots (`.bak-c1trace2`, `.bak-preboundingbox`, `.bak-preC1b-20260807T194258`).
  CLAUDE.md item 13 already excludes `.bak*` from scope; they are pre-fix historical
  snapshots and were **not** edited, on the same reasoning that protects the stamped
  artifacts.
- **Nothing under `data/coupling_validation/` was read for modification or written.**
  Those 37 files are stamped run provenance.

This check was requested as a gate before "Step 4". Step 4 (physics-skeptic) did not
fire, for the reasons in the section above: the agent is unavailable in this session and
no agreement claim exists for it to scrutinise.

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
