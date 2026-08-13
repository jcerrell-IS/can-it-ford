# `simulation/coupling_force/` — force-based fluid-rigid coupling

Created 2026-08-12. **Additive module.** It does not modify, patch, or monkey-patch the
existing kinematic path. `kernels/mpm_utils.py:1434` is untouched and still reachable.

## START HERE — there is ONE surviving API

Two coupling implementations grew on two machines and were reconciled on 2026-08-13.
**Only one survives. Do not re-derive this.**

**Entry point: `from simulation.coupling_force import ...`** — i.e. `__init__.py`,
which re-exports exactly the surviving API and nothing else:

| symbol | from | role |
|---|---|---|
| `ForceCoupledBody`, `CouplingConfig`, `CouplingTrace`, `RHO_WATER` | `coupler.py` | the partitioned loop against a warpmpm `Solver` |
| `RigidBodyState`, `integrate`, `inertia_from_particles`, `quat_to_matrix`, `quat_normalize` | `rigid_body.py` | Newton-Euler state, symplectic integrator, geometry-derived inertia |

The worked driver is `rung_b_coupled.py:37-38`, which imports from that entry point.

**`force_coupling.py` is SUPERSEDED as of 2026-08-13 and must not be used for new
work.** Its `CoupledRigidState` / `step_newton_euler` / `accumulate_impulse_numpy` are
*not* re-exported by `__init__.py`, so they are unreachable through the entry point
above. Verified live 2026-08-13: a `/usr/bin/grep` across `*.py`, `*.md`, `*.json` and
`*.sbatch` (the shell `grep` here skips gitignored paths, register H0) found **no
importer anywhere in the repo**, and none on Vista or LS6 either. Vista's copy of this
directory does not contain `force_coupling.py` at all, while carrying `__init__.py`,
`coupler.py`, `rigid_body.py` and `README.md` at byte sizes identical to this tree's
pre-2026-08-13 copies (sizes compared, contents not diffed). The file is retained,
not deleted, because deletion needs explicit confirmation per `CLAUDE.md`.

Its docstring still holds two things `coupler.py` does not record, and they should be
read before anyone reimplements this: the correction that warpmpm *does* already
accumulate a force and torque (`kernels/mpm_solver_warp.py:2223-2224`, on kinematic
collider paths only), and the hard refusal of `vehicle_params.py`'s axis-transposed
`{463, 1893, 1960}` box-fallback inertia.

Physics context for the kinematic path this module was written to replace:
`docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md`.

## The defect this replaces

The free-rigid path (material 8) never forms a force:

| step | code | effect |
|---|---|---|
| gather | `kernels/mpm_utils.py:1411` | `rigid_linear_mom += v_interp * mass_p`, the mass-weighted **grid velocity** |
| mass | `kernels/mpm_solver_warp.py:856` | `mass_np[b] = float(m_b.sum())`, sum of the same particle masses |
| integrate | `kernels/mpm_utils.py:1434` | `v_cm_new = rigid_linear_mom[b] / M` |

The body therefore **adopts a mass-weighted average of the surrounding grid velocity**.
No force is integrated, so density cannot drive motion and buoyancy cannot arise.

> **CORRECTION 2026-08-13.** The three rows above are right, and the mass-weighted
> average is exact (`mpm_solver_warp.py:852-856` builds `rigid_mass[b]` from the same
> particle set `:1411` sums over). But "no force is integrated" is **too strong as a
> description of the substep**. A third stage, `mpm_solver_warp.py:887
> _apply_rigid_restitution`, runs at `:1362` between the integrate and the push-back,
> and applies normal and Coulomb friction impulses that *increment* `v_cm` and `omega`
> at `:963-964` and `:976-977`, with lever arms. It is live in all 17 gated runs:
> `:1915` gates on `restitution != 0.0` and `sim_standing.py:211`/`:214` set
> `restitution=0.05` on the floor and all four walls. What is genuinely absent is a
> **hydrodynamic** force: the net acceleration cannot be decomposed into hydrodynamic,
> contact and gravitational parts. There is also a third rigid kernel this table omits,
> `mpm_utils.py:1463 rigid_particle_update`, which is the back-reaction limb.
> Full working: `docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md`.

Measured consequence, from the 2026-08-08 multigeom runs (`render_s2/multigeom_2026-08-08/*/summary.json`):

| case | `realized_rho` kg/m³ | `C2_veh_zmin_rise` m | `passthrough_max_frac` |
|---|---|---|---|
| rogue | 324.38 | **-0.0220** | 0.0984 |
| silverado | 294.20 | **-0.0003** | 0.0834 |

Both hulls sit near one third of water density. Neither rises. A body at ρ≈300 kg/m³
should float hard.

## The scheme

Contrary to the briefing note that "no force/impulse/torque accumulator exists anywhere
in this engine", warpmpm **does** accumulate a true reaction wrench, but only for
*fixed* colliders:

- `core/solver.py:354` `sdf_wrench(handle, dt)` → `force = Σ m(v_free - v_new)/dt`,
  `torque = Σ (x - c) × impulse / dt`
- `core/solver.py:348` `reset_sdf_force(handle)` zeroes the accumulators
- `core/solver.py:341` `set_sdf_pose(handle, center, quat, velocity, omega)`

What was missing is a force path for a **free** body. So this module carries the vehicle
as an SDF collider and closes the loop itself:

```
reset_sdf_force(h)                 # zero accumulators
step(dt)                           # MPM advances, impulse accumulates
F, tau = sdf_wrench(h, dt)         # real reaction wrench
integrate(state, F, tau, dt)       # M dv/dt = F + Mg ; I dw/dt = tau - w x (Iw)
set_sdf_pose(h, center, quat, ...) # feed the new pose back
```

This is a standard **partitioned (weakly coupled) explicit FSI** scheme.
Buoyancy is nowhere modelled or prescribed: it emerges as the resolved pressure
integral over the wetted hull.

## What is honest about its limits

- **Partitioned explicit, not monolithic.** As displaced fluid mass approaches body
  mass, the explicit update over-predicts and can diverge. That regime is exactly a
  near-neutrally-buoyant vehicle. `ForceCoupledBody.added_mass_ratio()` reports it and
  warns past a threshold rather than hiding it. Optional constant under-relaxation
  (`CouplingConfig.relax`) damps the transient; it does **not** move the equilibrium.
- **Velocity clamps are guards, not stabilisation.** They stop a diverging run from
  producing `inf`. Every clamp is recorded and reported, so a run is never silently
  truncated into looking converged.
- **SDF colliders need ~2 cells of wall thickness.** For a thin-walled hull the CDF
  collider path (`add_cdf_collider` / `cdf_wrench` / `set_cdf_pose`) has the identical
  interface and is the correct swap. The coupler only needs the three method names.

## Inertia provenance, a deliberate refusal

This module **never imports `vehicle_params`**. Its `inertia_kg_m2` and `cg_height_m`
are an axis-transposed box fallback carrying a documented 379% error on the pitch axis
(`docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md` §1). Wiring it into a solver would
silently corrupt every rotational result.

Inertia is instead either passed explicitly by the caller or computed by
`inertia_from_particles()` from the actual particle cloud, so it inherits the hull's real
axis lengths. Verified against the analytic solid-box tensor to within 2%.

## Verification status

`test_rigid_body.py` — 14 analytic checks, all passing as of 2026-08-12, CPU only,
no GPU and no solver required:

| test | checks |
|---|---|
| free fall | `z(t)`, `v(t)` against closed form incl. the symplectic O(dt) offset |
| neutral buoyancy | `F = -Mg` produces zero drift in position and velocity |
| Archimedes SHM | half-buoyant box oscillates at `sqrt(rho g A / M)`; period matched to 2% |
| inertia | `inertia_from_particles` vs analytic box, all three axes to 2% |
| torque-free top | `|L|` and `E` conserved to 2e-3; `R` stays orthonormal to 1e-16 |

**These validate the integrator, not the fluid coupling.** The separation is deliberate:
if a coupled run later shows no buoyant rise, these tests establish that the integrator
is not the cause.

## Item 6 — rung (b) through the force path, RUN 2026-08-12

`rung_b_coupled.py` drives `BoxTank(box_mode="collider_sdf")` from
`validate_coupling_force.py` (imported, not copied, so geometry, water seeding, carve,
planes, dt and substeps are identical to the published C1/C1b runs) through
`ForceCoupledBody`. Results in `data/coupling_force_2026-08-12/`.
`n_grid=64`, 445,184 particles, `rho_box=600`, `dt=3.030e-03`. The tank refuses
`n_grid < 64` on its P2G edge guard, so 32 is not available.

**The gate is passed: the force path produces a non-zero, upward buoyant wrench where the
kinematic path produces none.**

| settle=1500 | measured | analytic | |
|---|---|---|---|
| `Fz` median, relax=1.0 | **+22,809 N** | +16,697 N | ratio 1.366 |
| `Fz` median, relax=0.4 | +22,598 N | +16,702 N | ratio 1.353 |
| `a` first 3 substeps | **-1.2378 m/s²** | -1.0876 m/s² | **13.8%, correct sign** |

The sign is right: settled `frac` is 0.5335, below the neutral 0.600, so the body should
sink slightly. The 0.9% spread between `relax=1.0` and `relax=0.4` confirms under-relaxation
does not move the equilibrium, ruling out the force being an artifact of the scheme.

**Do NOT quote the 1.37 ratio as a result.** Four reasons: the requested 0.80 submersion was
**not realised** (settled 0.5335); surface IQR *grew* from 7.7e-2 at settle=100 to 3.02e-1 at
settle=1500, so the tank is still sloshing; `added_mass_ratio=0.889` sits at the
partitioned-explicit stability limit and the coupler warns on it; and no dt or grid
refinement study was run. The 37% force excess is an open question, not a measurement.

**Cost:** 42 s wall for settle=1500 + 80 coupled steps on the GH200, against the ~1 GPU-hour
budgeted. A proper convergence study fits comfortably in one allocation.

## Released-code search, 2026-08-12

Performed before implementing, as instructed.

- **Zhang et al. 2026** — *located*. "Stabilized explicit material point method for fluid
  flow and fluid-structure interaction simulations using dual high-order B-spline volume
  averaging", CMAME, ScienceDirect `S0045782525007005` (HKUST). **No public code.** The
  record states simulation scripts are *available on request*. The paper's stabilisation
  (dual B-spline volume averaging, blended APIC/FLIP, δ-correction, pressure smoothing) is
  a solver-internal change to warpmpm's transfers, out of scope for an additive module;
  what is carried over here is its framing of explicit-FSI stability limits.
- **Qian et al. 2022** — *not located*. No CMAME 2022 paper by that author on water entry
  of a half-buoyant cylinder/box surfaced. Searches returned adjacent work (IB-LBM water
  entry, ULPH water entry, mixed-MPM free-surface/seepage) but not the cited paper. The
  half-buoyant box configuration is nonetheless used as the `test_rigid_body.py` SHM
  benchmark. **Treat the Qian citation as unverified until the DOI is supplied.**

## Files

| file | role |
|---|---|
| `__init__.py` | **the entry point.** Re-exports the surviving API and nothing else. |
| `rigid_body.py` | Newton-Euler state + symplectic integrator + geometry-derived inertia. No warpmpm import. |
| `coupler.py` | `ForceCoupledBody`, the partitioned loop against a warpmpm `Solver`. |
| `test_rigid_body.py` | analytic self-tests, CPU only. |
| `rung_b_coupled.py` | worked driver, item 6 below. Imports the entry point at `:37-38`. |
| `force_coupling.py` | **SUPERSEDED 2026-08-13, imported by nothing.** Reference only, see "START HERE" above. Its CPU self-test still passes (re-run 2026-08-13). |
| `inflow_outflow.py` | item 7 below, Zhao et al. 2019 in/outflow. Unrelated to the coupling API split. |

---

# Item 7 — velocity-controlled inlet + recycling outflow

`inflow_outflow.py`, added 2026-08-12.

**Reference verified 2026-08-12.** Zhao, Bolognin, Liang, Rohe & Vardon (2019),
*Development of in/outflow boundary conditions for MPM simulation of uniform and
non-uniform open channel flows*, Computers & Fluids **179**:27-33,
DOI `10.1016/j.compfluid.2018.10.007`, ScienceDirect `S004579301830728X`. The paper
pairs a velocity-controlled inflow with a pressure-controlled outflow and states that
material points must be added and removed *"with appropriate kinematic properties"*.

## Ported

The **velocity-controlled inlet**, directly: a band at the upstream face has its particle
velocity prescribed to `u_in` every step.

## Not ported, and why a literal port is impossible

**Two independent blockers, both structural:**

1. **No pressure field.** Pressure exists only inside the constitutive update as an EOS
   evaluation, `p = -bulk*(J^-1.1 - 1)` at `kernels/mpm_utils.py:43`, computed and consumed
   inside the stress kernel. It is never assembled as a nodal or particle field a boundary
   condition could read or drive.
2. **No particle add/remove.** `Solver.load_particles` fixes the count for the run. The only
   write paths are `set_x` / `set_v` and the `_sim.import_particle_{F,C}_from_torch`
   internals. Zhao's add/remove of material points therefore has no API to target.

Blocker 2 was not in the brief but is the more restrictive of the two: it rules out the
add/remove half of Zhao's scheme independently of the pressure question.

## The substitute: position- or velocity-keyed recycling

A particle meeting the outflow criterion is teleported into the inlet band and
re-initialised. Given a fixed particle array this is the **only** scheme that can sustain
indefinite throughflow, and it conserves mass **exactly** by construction.

**Stated cost:** recycling cannot represent a net mass change in the domain. It models a
channel in steady throughflow and **cannot** model filling, draining, or a rising free
surface. `report()` returns `can_model_net_mass_change: False` so this cannot be forgotten.

## "Appropriate kinematic properties"

Zhao's phrase is load-bearing. A recycled particle keeping its outlet deformation gradient
re-enters carrying stale compression: for a Newtonian fluid the EOS reads `J = det(F)`, so
recycling with `J != 1` injects a spurious pressure pulse **at the inlet**. The module
resets `F -> I` and `C -> 0` on every recycle. That requires reaching past the public
Solver API into `_sim.import_particle_F_from_torch`; the same internal-access pattern has
precedent here (see `validate_coupling_force.py`'s `internal_access` note on `pin()`).
If the reset path fails the module **warns loudly and once**, telling the caller to treat
any pressure or free-surface result as invalid, rather than degrading silently.

## Verification status

`test_inflow_outflow.py` — 21 logic checks, all passing 2026-08-12, CPU only, against a
stub solver:

| test | checks |
|---|---|
| recycling | count conserved, recycled == flagged, none left past outlet, all land in band |
| index safety | particles at index >= `n_fluid` (a rigid body) never touched |
| inlet | band velocity == `u_in`, particles outside the band not forced |
| velocity-keyed mode | flags on velocity, not position |
| steady throughflow | rate settles positive over 400 steps, count never drifts |
| placement | inlet band and cross-section bounds respected, not stacked |

**Not run: the module against a live warpmpm solver.** The `F`/`C` reset path in particular
is unexercised, since it needs a real `_sim`. That is the first thing to test next session.
