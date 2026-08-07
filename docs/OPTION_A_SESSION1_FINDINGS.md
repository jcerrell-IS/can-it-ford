# Option A Session 1: findings and BC design proposal

Date: 2026-08-07. Status: Session 1 complete (tasks 1 to 4 of
`docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md`). No boundary condition code written,
by design. Session 2 starts from the design section below.

Every claim here was read from `kks32/mpm-engine` at pinned SHA `544c93dd`,
now vendored and sha256-verified at
`third_party/mpm-engine-544c93dd-solver-core/` (see its `VENDORED.md`).
Line numbers refer to those vendored files. Not sourced from memory, from a
skill, or from a prior session summary.

---

## Summary

The blocking unknown was whether a real grid-face boundary condition is
reachable in warpmpm, or whether an in/outflow BC must be a particle-level trick
like `sim_standing.py`'s existing `_sustain_inflow`.

Answer: **hybrid**. A genuine node-level velocity Dirichlet condition exists and
is usable for the inflow. There is no pressure anywhere in the engine, so
Zhao et al.'s pressure-controlled outflow cannot be ported literally and must be
re-expressed as a depth-controlled outflow. The particle add/remove mechanism the
method needs already exists as a per-particle activation mask.

Two project-level corrections fell out of this, F-2 and F-1.

---

## F-1. The plan file's task 1 paths were wrong, two of three 404

| plan file path | HTTP at `544c93dd` | actual path |
|---|---|---|
| `src/warpmpm/core/solver.py` | 200 | unchanged |
| `src/warpmpm/core/mpm_solver_warp.py` | **404** | `src/warpmpm/kernels/mpm_solver_warp.py` |
| `src/warpmpm/materials.py` | **404** | `src/warpmpm/materials/__init__.py`, a package |

`src/warpmpm/kernels/mpm_utils.py` (66,538 B) is not named in the plan file and
holds the actual transfer kernels. F-6 and F-8 below are readable only there, so
vendoring the three named paths alone would have missed the decisive evidence.
The vendored directory corrects this. `src/warpmpm/coupling/` also exists
(`admittance.py`, `wrench.py`, `backend.py`), not needed for this question.

## F-2. Gravity is 9.81. Supersedes CLAUDE.md ground-truth items 3 and 15

CLAUDE.md item 3 records gravity as "a warpmpm default and its value is UNKNOWN
from this repo." It is known, and it is not a default. `core/solver.py:167-169`,
inside `Solver.set_material()`:

```python
self._sim.set_parameters_dict(
    {"material": name, "g": [0.0, 0.0, -9.81], **params}, device=self.device
)
```

The wrapper hardcodes `g = [0, 0, -9.81]` on every `set_material()` call.
`sim_standing.py:127` calls `s.set_material(newtonian(...))` and never passes
`g`. `newtonian()` resolves to `("newtonian", {E, nu, density, bulk_modulus,
plastic_viscosity, yield_stress, hardening, softening})` at
`materials/__init__.py:78-83`, with no `g` key, so nothing shadows it through
the `**params` splat. `set_material_range` (`core/solver.py:189`) never sets `g`.

**Gravity in all 17 gated runs is exactly 9.81 m/s^2 in -z.**

Consequences: `gates_all_runs.py:12` (G=9.81) matches the solver.
`failure_modes.py:14` (G=9.80665) does not, a 0.034 percent fork, numerically
immaterial but real. Item 15's instruction to "state both separately, never
merge them" is obsolete; they can be merged, on 9.81. Item 15 was formally
withdrawn 2026-08-07 on that basis.

Correction, 2026-08-07: this note originally said 0.036 percent. The true value
is (9.81 - 9.80665) / 9.80665 = 0.0342 percent. Caught by
`scripts/check_claims.py` rule C6. The wrong figure had already propagated to
CLAUDE.md item 3 and to `analysis/classify_failure_modes.py:31`.

## F-3. Task 2, the four entry points

All four named in the plan file are genuinely called by `sim_standing.py`.

- **`load_particles(pos, vol, cov=None, cov_mode="step")`**, `core/solver.py:103`,
  called `sim_standing.py:126`. Allocates `MPM_Simulator_WARP(len(pos))`.
  **Particle count is fixed here and there is no later allocation path.** This is
  the hardest constraint on any BC design.
- **`set_material_range(start, end, material, **overrides)`**, `core/solver.py:173`,
  called `sim_standing.py:129`. Half-open index range. Rejects tabulated
  materials (global-only). Rigid needs `obj_id` then `finalize_rigid_bodies()`.
- **`add_plane(point, normal, surface, friction, restitution)`**, `core/solver.py:212`,
  called 5x at `sim_standing.py:132` and `:136`. Docstring line 216: **"Grid
  boundary conditions do not affect rigid particles."** Independently confirms
  CLAUDE.md item 3's claim that the vehicle is a free rigid body.
  `restitution > 0` also registers the plane as a rigid contact surface.
- **`add_domain_walls(start_time, end_time)`**, `core/solver.py:315`, called
  `sim_standing.py:137`. See F-7; adversarial to any outflow.

## F-4. Task 3a. A real node-level velocity Dirichlet BC exists

`Solver.add_box()` (`core/solver.py:224`) routes to `set_velocity_on_cuboid()`
(`kernels/mpm_solver_warp.py:2028`), whose kernel hard-overwrites grid node
velocity inside an axis-aligned box (`:2076-2085`):

```python
m = state.grid_m[grid_x, grid_y, grid_z]
v_free = state.grid_v_out[grid_x, grid_y, grid_z]
wp.atomic_add(param.force, 0, m * (v_free - param.velocity))
state.grid_v_out[grid_x, grid_y, grid_z] = param.velocity
```

A true velocity Dirichlet condition at grid nodes: time-windowed by
`start_time`/`end_time`, skipping massless nodes, accumulating the exact reaction
impulse before overwriting so `tool_force()` (`core/solver.py:420`) reads back
`sum m*(v_free - v_imposed)/dt`. A thin box spanning the inflow face is a
legitimate grid-face velocity BC, with force readback included.

## F-5. Task 3b. There is no pressure anywhere. The outflow cannot be pressure-controlled

`grep -ci pressure kernels/mpm_solver_warp.py` returns **0** across 3,181 lines.
No pressure field, no pressure array, no pressure BC, no node-level pressure
hook. The 19 hits in `kernels/mpm_utils.py` are all inside constitutive/EOS
stress code, not a boundary interface.

Pressure exists only implicitly: the weakly-compressible EOS derives it per
particle from `J = det(F)` and `bulk_modulus`. There is nothing to Dirichlet.

**Most consequential finding for Option A.** Zhao et al.'s outflow condition is
pressure-controlled and that half of the method has no target to bind to in
warpmpm. It must be re-expressed. See D-3.

## F-6. `particle_selection` is the add/remove mechanism, and it already exists

Zhao et al. add and remove material points at the domain edges. warpmpm cannot
allocate particles after `load_particles`. But it has a per-particle activation
mask gating every core kernel, in `kernels/mpm_utils.py`:

| line | kernel | gate |
|---|---|---|
| 922 | `p2g_apic_with_stress` | `if state.particle_selection[p] == 0:` |
| 1049 | `g2p` | `if state.particle_selection[p] == 0:` |
| 1157 | `compute_stress_from_F_trial` | `if state.particle_selection[p] == 0:` |
| 1173 | `g2p_stress_p2g` (fused path) | `if state.particle_selection[p] == 0:` |

Polarity: **0 is active, nonzero is inert.** A particle with `selection != 0`
scatters no mass or momentum to the grid, gathers nothing back, and gets no
stress update. Functionally removed while still holding its array slot.

Advection `x_new = particle_x[p] + dt*new_v` lives inside `g2p_particle`
(`kernels/mpm_utils.py:1026`), so a deactivated particle also **freezes in
place**. Recycling therefore needs an explicit teleport via `Solver.set_x()`
(`core/solver.py:520`); it will not drift on its own.

Exposed at `kernels/mpm_solver_warp.py:1679`
(`import_particle_selection_from_torch`) and `:1849` (export). **Not exposed on
the typed `Solver` wrapper**, so a BC must reach through `solver._sim`. Isolate
that behind one helper rather than scattering private-attribute access.

## F-7. `add_domain_walls` is what blocks an outflow, and it is one-way

`add_bounding_box` (`kernels/mpm_solver_warp.py:2287`) is a 3-cell band at each
of the six faces zeroing only the **outward** component:

```python
padding = 3
if grid_x < padding and state.grid_v_out[...][0] < 0:                      # zero vx
if grid_x >= model.grid_dim_x - padding and state.grid_v_out[...][0] > 0:  # zero vx
```

Inward motion is untouched, so it is no-penetration and otherwise free-slip.
`sim_standing.py:137` calls it, which is why the current tank recirculates
rather than draining: the downstream face cancels outflow velocity every
substep. An outflow BC must skip this call or use a variant leaving the +x face
open. The `_update_grid_box` guard at `core/solver.py:507` then becomes binding:
it raises if any particle comes within 2 cells of the grid edge.

## F-8. A real periodic streamwise BC exists but is unusable here

`Solver.periodic_x` (`core/solver.py:90-93`) wraps the x node index in both p2g
(`kernels/mpm_utils.py:871`) and g2p (`:999`), and wraps particle x in advection
(`:1027-1032`). A genuine periodic boundary, built for "steady chute flows." Its
docstring: **"Incompatible with CDF colliders and rigid bodies."** Consistent
with the code, `g2p` skips materials 7 and 8 (stationary/rigid) and rigid bodies
integrate separately via `rigid_body_integrate`, which has no wrap.

The vehicle is a rigid body, so the engine's one built-in sustained-flow
mechanism is off the table for this scene. Worth stating in the paper's
limitations: "the engine has periodic flow, why not use it" is the obvious
reviewer question.

## F-9. `add_sdf_collider` is real at this SHA, closing a skill's open dispute

The `mpm-technical-deep-reference` skill lists as live dispute #1 whether
`add_sdf_collider()`/`build_sdf()` work or are "planned, empty stubs." At
`544c93dd` they are real: `core/solver.py:324` dispatches to
`kernels/mpm_solver_warp.py:2621`, alongside `set_sdf_pose`, `reset_sdf_force`,
and `sdf_wrench` (calibrated force and torque). `add_cdf_collider` is also real
(`core/solver.py:363`), documented as CPIC per Hu et al. 2018 Section 5, and its
docstring confirms the skill's "CDF under-reports, ~1/3 for a node-aligned
sheet, use SDF for calibrated force" claim. Resolved as "works," at this SHA.
Neither is used by the 17 gated runs.

## F-10. `add_box`/`set_box` drifts; do not use it naively as a fixed inflow window

`modify()` at `kernels/mpm_solver_warp.py:2090-2096` advances
`param.point += dt*param.velocity` **every substep**. A box added with
`velocity=(U,0,0)` marches downstream at U and leaves the inflow face within a
fraction of a second. Holding a stationary inflow window requires re-pinning
`center` every control tick via `set_box()`, whose docstring
(`core/solver.py:240-246`) states exactly this contract. The failure would
present as "the inflow worked for 20 frames then stopped."

## F-11. OPEN, not established: the 10x sound-speed criterion appears violated

The plan file calls Zhao et al.'s softened-bulk-modulus note directly reusable:
reduced bulk modulus is valid so long as numerical sound speed stays above 10x
maximum flow velocity. Applying it using `sim_standing.py:147` verbatim:

```
c = sqrt(1.1 * bulk_modulus / water_density)
  = sqrt(1.1 * 1.5e5 / 1000) = 12.845 m/s
```

`bulk_modulus=1.5e5` is the `StandingFloodScene` default (`sim_standing.py:75`),
not overridden at the construction site (`:251-253`), and recorded as `1.5e5` in
`summary.json`.

The criterion therefore caps admissible velocity at **1.284 m/s**. The velocity
sweep runs 0.5 to 3.0 m/s with a 1.5 m/s baseline, so the baseline and every
faster run exceed it, the 3.0 m/s runs at a ratio of 4.3 rather than 10.

**This is arithmetic from live source, not yet cross-checked per-run against
`data/all_runs_inventory.csv`. Do not cite it until that check is done.** If it
holds it is a limitation to state plainly, and an argument for Option A rather
than against it.

---

# Design proposal (propose only, not implemented)

The engine supports a hybrid: a real grid-face velocity Dirichlet condition at
the inflow, plus particle-level recycling for mass. It supports no
pressure-controlled outflow in any form.

## D-1. Inflow: grid-face velocity Dirichlet plus particle reinjection

Two cooperating parts, because the grid BC moves momentum but supplies no mass.

1. **Momentum.** One `add_box()` slab spanning the full y and z extent of the
   wetted inflow face, one to two cells thick in x, imposing `(U, 0, 0)`. Re-pin
   its center every control tick with `set_box()` per F-10. Bonus:
   `tool_force(handle, dt)` gives the injected momentum flux, a directly
   reportable diagnostic and a mass-balance check.
2. **Mass.** Reactivate recycled particles (D-2) inside the slab on the seeding
   lattice `sim_standing.py:101-105` already uses (`h = dx/2`, jittered), with
   `v = (U, 0, 0)`, `F = I`, `C = 0`.

Strictly stronger than the current `_sustain_inflow`
(`sim_standing.py:190-198`), which overwrites velocity on whatever particles
happen to sit in the band and adds no mass at all.

## D-2. Outflow: deactivate and recycle, mass-conserving by construction

Per control tick, after `step()`:

1. Read `x = solver.x()`; find water particles with `x[:,0] > x_outflow`, with
   `x_outflow` placed inside the 3-cell guard band, not on it.
2. Mark those `selection = 1` via
   `solver._sim.import_particle_selection_from_torch`. They go inert and freeze
   (F-6).
3. Teleport the same indices into the inflow slab with `solver.set_x()`, reset
   velocity with `solver.set_v()`, then set `selection = 0`.

Recycling rather than free add/remove is forced by the fixed allocation (F-3),
and it is an advantage here: **inflow rate equals outflow rate identically**, so
total mass is conserved to machine precision and cannot drift. Zhao et al. reach
the same steady state by balancing two independent boundaries; this gets it by
construction.

Requires dropping or replacing `add_domain_walls()` on the +x face (F-7). The
`core/solver.py:507` edge guard then sets how close to `grid_lim` the outflow
plane may sit.

**Open question for Session 2, do not guess.** Whether `F` and `C` also need
resetting on a recycled particle. `set_x`/`set_v` are on the wrapper;
`import_particle_F_from_torch` and `import_particle_C_from_torch` exist at
`kernels/mpm_solver_warp.py:1658` and `:1669` but are not. A recycled particle
carrying a stale deformation gradient would inject spurious stress. Needs a
direct test.

## D-3. What "pressure-controlled outflow" maps to, given F-5

It does not map to a pressure BC, because there is no pressure to control.

The honest translation: Zhao et al.'s pressure-controlled outflow exists to hold
a prescribed downstream water depth, with hydrostatic pressure at the outlet
following from that depth. In a weakly-compressible EOS code the equivalent is
to control depth directly and let the EOS generate the pressure: at the outflow
plane, deactivate only particles whose z exceeds the target free surface
`z_target = floor + depth`, retaining those below, so the outlet column
self-regulates toward the prescribed depth.

That is a **depth-controlled outflow**, not a pressure-controlled one, and it
must be described that way in the paper. Claiming a pressure BC in an engine
with no pressure field is exactly the class of overclaim
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` exists to prevent.

## D-4. Where the code goes

New file `simulation/sim_channel_bc.py`, per the plan file's guardrail that all
new BC code lives in `simulation/` as new files.
`renders/yaris_render_s1/sim_standing.py` is not touched and the 17 gated runs
stay reproducible. The new scene class reuses `StandingFloodScene`'s seeding,
carving, and substep-rate logic rather than reimplementing it.

One helper should own every `solver._sim` reach-through (selection get/set, and
`F`/`C` reset if D-2 needs it), so the private-API surface is a single auditable
function.

---

# Reproducing these findings

From `third_party/mpm-engine-544c93dd-solver-core/`:

1. Path correction (F-1): `curl -o /dev/null -w '%{http_code}'` on the three
   plan-file paths at the SHA. Expect 200, 404, 404.
2. Gravity (F-2): `grep -n '"g"' core/solver.py` gives one hit, line 168;
   `grep -n gravity materials/__init__.py` gives none.
3. No pressure (F-5): `grep -ci pressure kernels/mpm_solver_warp.py` returns 0.
4. Activation gate (F-6): `grep -n particle_selection kernels/mpm_utils.py`
   returns the six lines listed.
5. Vendoring integrity: re-fetch each file at the pinned SHA and compare sha256
   against the table in `VENDORED.md`.

F-11 is the only item here that still needs work, a per-run cross-check against
`data/all_runs_inventory.csv`.

# Not yet applied

F-2 supersedes CLAUDE.md August 4 ground-truth items 3 and 15, and belongs in
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`. That edit is deliberately
NOT made here and is pending review.
