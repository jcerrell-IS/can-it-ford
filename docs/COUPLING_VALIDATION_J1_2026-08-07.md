# Register J.1: coupling-force validation, method and results

Date: 2026-08-07. Owner: the coupling-validation session.

**Status: the discriminator has run and J.1 is answered on its central question.
C0 PASSES. A fixed collider recovers Archimedes on this scene to within 8 percent
at both resolutions. The free rigid body does not: on the same water, at the same
instant, it delivers 1.5 percent of the correct buoyant acceleration. The defect
is on the free rigid body path, which is the path all 17 gated runs use.**

**The reported "sign inversion" and its "divergence under refinement" are NOT
real. Both are artifacts of the C1 measurement protocol and are retracted below
with the arithmetic that retracts them.** The underlying coupling defect is real
and survives their retraction. J.1 is not yet closeable; see the last section.

This file exists because the docs survey of 2026-08-07 confirmed there is **no
document anywhere in this tree recording a completed coupling-force, buoyancy or
Archimedes validation**. Register J.1 specifies the test, register C13 records
that no such validation exists in the Genesis repository either. Register D5 and
CLAUDE.md item 6 already settle what the gates are and are not; this file does not
revisit that, it supplies the missing check they describe. This is the first such
result in the project.

Deliberately NOT written into `CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`:
another session owned that file at the time of writing (see
`CONCURRENT_SESSION_NOTICE_2026-08-07.md`). Promote from here when ownership is
settled.

## Why the test has this shape

Register A3 is the binding constraint: `rigid_state()` returns exactly
`com`, `v`, `omega`, `R`, and no force, impulse or torque accumulator exists on
the 17-run path. **The coupling force cannot be read. It can only be inferred
from motion**, as `m dv/dt`. Everything below follows from that.

Verified live against `third_party/mpm-engine-544c93dd-solver-core/` at pinned
SHA `544c93dd`. Nothing here is from a skill file or a summary.

| mechanism | source | consequence for the test |
|---|---|---|
| `v_cm_new = rigid_linear_mom / M`, no force term | `kernels/mpm_utils.py:1416-1459` | body velocity is the mass-weighted mean of grid velocity at its own particles |
| momentum gathered by B-spline from `grid_v_out` | `kernels/mpm_utils.py:1370-1412` | coupling is entirely a grid transfer |
| gravity applied per grid node | `kernels/mpm_utils.py:940` | a DRY box must free-fall at exactly -9.81, giving a free control |
| `g = [0,0,-9.81]` hardcoded | `core/solver.py:167-169` | register A2 |
| `F = I` and no stress branch for material 8 | `kernels/mpm_utils.py:1090-1091` | rigid particles deposit mass and momentum, never stress |
| `if restitution != 0.0` gates rigid contact | `kernels/mpm_solver_warp.py:1915` | planes at `restitution=0.0` are invisible to the body, isolating the coupling |
| `pressure = -bulk*(J**-gamma - 1)`, `gamma=1.1` | `kernels/mpm_utils.py:28-54` | confirms `c = sqrt(1.1 K/rho)`, and moves the Archimedes target |

## Scene

Cube, uniform density, free rigid body, still water, nothing else. No Yaris hull,
no `vehicle_params.py`, no inflow, no floor friction. All planes
`friction=0.0, restitution=0.0`, which is a deliberate, stated deviation from
`sim_standing.py:132-137` (which uses `restitution=0.05`, so the 17 runs DO have
floor and wall contact on the vehicle).

Canonical numerics are matched exactly, not approximately: `grid_lim`
9.421742313727737 m, `n_grid` 64 and 96, `dx` 0.1472147236519959 and
0.0981431491013306 m, `h = dx/2` (8 particles per cell), `bulk_modulus` 1.5e5,
`rho_w` 1000, `eta` 1e-3. The substep counts fall out at **11 and 16**, matching
the g64 and g96 rows of `data/all_runs_inventory.csv`. That is a check that the
scene is at canonical numerics rather than merely canonical-looking.

Cube side `L = 10 * dx_canonical = 1.4721472365199588 m`, fixed in metres, so
geometry is invariant across the refinement step and only the grid refines. The
lattice owns exactly `L^3`: `n_side^3 * h^3 == L^3` to 1e-12 at both resolutions
(20^3 and 30^3 particles). A cube, not a sphere, because the draft law
`d = L rho_box / rho_w` is exact and independent of cross-section, and the
displaced volume carries zero geometric error.

## Analytic targets

Incompressible Archimedes, and the EOS-exact correction derived from the
verified `gamma = 1.1` EOS by hydrostatic integration:

```
s(zeta) = (1 + b zeta)^(1/(gamma-1)),   b = (gamma-1) rho_w g / (gamma K)
d_compressible = ((1 + 11 b L rho_box/rho_w)^(1/11) - 1) / b
```

For `rho_box = 600`:

| quantity | value |
|---|---|
| mass | 1914.28 kg |
| volume | 3.190463 m^3 |
| draft, incompressible | 0.883288 m (6.000 dx coarse, 9.000 dx fine) |
| draft, EOS-compressible | 0.860914 m (5.848 dx, 8.772 dx) |
| compressibility shift | **-2.53 %** |
| one particle layer | **8.33 %** of draft coarse, 5.56 % fine |
| C1 `a_ideal = g(rho_w/rho_box - 1)` | 6.5400 m/s^2 |
| C1 `F_buoy = m(a+g)` | 31298.4 N, identically `rho_w V g` |
| added-mass asymptote, Ca approx 0.67 | 3.0898 m/s^2 |
| acoustic transit `L/c` | 0.11461 s = 37.8 substeps coarse, 55.0 fine |

The closed form was checked against an independent Simpson-plus-bisection solve
of the buoyancy integral and agrees to ~1e-13. It is a derivation, not a
transcription.

**Stated in advance: at canonical resolution one particle layer (8.33 % of
draft) is over three times the physical compressibility correction (2.53 %), so
C2 cannot resolve its own EOS correction at g64.** That is a resolution-cost
finding, not an excuse assembled afterwards.

## Results so far

**C0, dry drop. PASSED on both platforms.** The rigid integrator and the
grid-gravity path are correct.

| platform | a measured | error vs -9.81 |
|---|---|---|
| Apple M5, warp 1.16.0 CPU | -9.809986697775976 | +0.00014 % |
| Vista GH200, warp 1.15.0 CUDA | -9.810047354016985 | -0.00048 % |

CPU and CUDA agree to ~6e-6 relative. The residual is float32 reduction ordering.
`rho_box_realized` = 599.9999999999999 against 600 requested, satisfying the
project's coupled-variables rule.

**Cross-platform determinism.** The identical 158-frame settle at 254,171
particles reproduced to all reported digits on both platforms:
`settle frames 158`, `vmax peak 8.1059`, `vmax final 0.6294`,
`draft after settle 0.789370`. Wall clock 364 s on CPU against 5.0 s on the
GH200, about 73x.

Re-read live 2026-08-07 from `data/coupling_validation/c0_g{64,96}.json` on Vista
(job era 04:49): `a` = -9.80999285089118 at g64 (+7.288e-5 %) and
-9.810061455934077 at g96 (-6.265e-4 %). `rho_box_realized` = 599.9999999999999
in both. These are the current on-disk artifacts; the two-platform figures above
came from an earlier submission and are retained as the cross-platform check.

## LEAD 1: the `warpmpm.coupling` package is not on the free rigid path

Fetched at pinned SHA `544c93dd` and read in full: `admittance.py` (2811 B),
`wrench.py` (2448 B), `backend.py` (4012 B). `coupling/__init__.py` is HTTP 200,
0 bytes.

**Answer: collider-only. Nothing in `coupling/` executes on the free rigid body
path, and nothing in it can invert a buoyant force, because it never sees one.**

1. `backend.py:28-34` `attach_tool` calls `solver.add_box`, the kinematic
   axis-aligned box collider. `core/solver.py:231` states the direction of the
   dependency in the engine's own words: "the coupling layer uses this collider
   for robot tools." There is no `set_material_range(..., "rigid", ...)` and no
   `finalize_rigid_bodies()` anywhere in the package. The word "rigid" does not
   appear in any of the three files.
2. No sign convention in the package can reach a buoyant force.
   `wrench.py:15-46` `box_contact_wrench` is a quasi-static stress integral over
   a horizontal contact band **beneath** a pressing tool, gated to
   `cauchy[:,2,2] < 0` (`:35`). `admittance.py` is two controllers, `ForceAdmittance`
   (`:38-42`) and `Impedance1D` (`:64-71`), that map a measured reaction to a
   commanded tool velocity. Neither is invoked by `rigid_body_integrate`.
3. `core/solver.py` does not import `coupling`. The only `coupling` matches in the
   vendored core are three docstring mentions (`:4`, `:106`, `:231`). The only
   importer in the whole vendored tree is
   `third_party/mpm-engine-544c93dd/examples/dough_surface_render.py:22`. The
   dependency runs coupling -> core, never core -> coupling: `backend.py:16-17`
   imports `Solver` and `box_contact_wrench`.

This is a negative result and it is a real one: it removes the last unread
package from the suspect list. The prior session's "likely load-bearing" flag was
wrong.

## LEAD 2: the discriminator, side by side

Vista job **894731**, `j1c1sdf`, COMPLETED 2026-08-07T06:50:25, elapsed 00:07:38,
`ALLDONE_C1SDF failed=0`, warp 1.15.0. Six runs in one job at one code revision.
Every run uses the identical flags the published C1 numbers used:
`--depth-cells 18 --box-bottom-cells 3 --settle-frames 900 --measure-substeps 160`.

The control is tight, verified by reading the harness rather than trusting the
docstring. `BoxTank.__init__` seeds box particles **only** in rigid mode
(`:226-230`, `box = np.zeros((0,3))` otherwise) and calls `set_material_range` +
`finalize_rigid_bodies` **only** in rigid mode (`:273-276`). The water lattice and
the carve against the cube are unconditional (`:247-251`), and the collider surface
is placed on that same cube (`:231-233`). So the excluded volume, the water, the
seed, the settle procedure and the resolution are identical across all three arms;
only the cube's representation and the force readout differ.

Analytic target `rho_w V g` = **31298.444315169316 N** (`V` = 3.1904632329428453
m^3). All arms report `fully_submerged_at_measure`/`_at_release` true.

| arm | readout | g64 | err | g96 | err |
|---|---|---|---|---|---|
| **SDF collider, fixed** | `sdf_wrench` Fz, steady tail | **28898.40 N** | **-7.67 %** | **33577.11 N** | **+7.28 %** |
| **Box collider, fixed** | `tool_force` Fz, steady tail | 19432.45 N | -37.91 % | 24639.37 N | -21.28 % |
| **Free rigid body** | `m(a+g)` from `rigid_state` | 16028.73 N | -48.79 % | **-9540.96 N** | **-130.48 %** |

Supporting columns for the SDF arm: lateral force ratio `|F_xy|/|Fz|` is 0.0403
(g64) and 0.0121 (g96), so the readout is not leaking a spurious direction. Tail
scatter is 828 N std (2.9 %) at g64 and **101.7 N std (0.30 %)** at g96. The g96
SDF measurement is the cleanest number in the entire J.1 campaign.

Both fixed-collider readouts are positive, correctly signed, and **converge** with
refinement. The SDF arm brackets the analytic value (-7.7 %, then +7.3 %). The box
arm approaches it monotonically from below (-37.9 %, then -21.3 %), consistent
with its own documented under-read for a volumetric node-overwrite collider. Only
the free rigid body diverges and changes sign.

**Discriminator case: SDF correct, free-rigid wrong.** By the scoping in the task,
that means the defect is in the free rigid coupling, and it touches all 17 gated
runs, because they use that same path.

Two hypotheses are closed by this table alone:

- **H2 is excluded by direct measurement.** The water IS hydrostatic at
  measurement time. A fixed collider immersed in it reads Archimedes to within
  8 percent at both resolutions. The settle loop is not the problem for the water.
- **H1 is excluded by construction.** `run_c1:515-520` builds `vs` from
  `rigid_state()["v"][2]` with `ts` increasing, and takes `np.polyfit(t, v, 1)[0]`,
  which is `dv/dt` in the correct sense. `a_ideal = G*(RHO_W/rho_box - 1)` = +6.54
  is positive for a rising body. The decisive point is that `run_c0:383` uses the
  identical `np.polyfit` call on the identical accessor and returns -9.81 to seven
  significant figures. A flipped subtraction order would have flipped C0 too.

## The "sign inversion" is a fitting artifact, and it is retracted

The free rigid arm's numbers are not a measurement of acceleration. They are the
least-squares slope of a **step**.

Read directly from `c1_rigid_g96.json` `v_series`, the first six samples of
vertical velocity in m/s:

```
i=0  t=0.000000  v= 0.0
i=1  t=0.002083  v=-0.10292938351631165
i=2  t=0.004167  v=-0.10272636264562607
i=3  t=0.006250  v=-0.10280451178550720
i=4  t=0.008333  v=-0.10291256755590439
i=5  t=0.010417  v=-0.10301814228296280
```

The velocity jumps to -0.1029 m/s in ONE substep and is then flat to four decimal
places. Nothing is accelerating. Fitting a line through a step of size `dv` over
`n+1` samples has an exact slope, `dv/dt` times 0.5, 0.3, 0.142857, 0.045455 for
`n` = 2, 3, 5, 10. Against the reported window ladder:

| window `n` | reported `a` (g96) | step model | ratio |
|---|---|---|---|
| 2 | -24.654327 | -24.703052 | 0.9980 |
| 3 | -14.794105 | -14.821831 | 0.9981 |
| 5 | -7.064481 | -7.058015 | 1.0009 |
| 10 | -2.276064 | -2.245732 | 1.0135 |

The step model reproduces the reported "acceleration" to **0.2 percent** at
`n` = 2, 3 and 5. The same test at g64 gives a step of -0.013988 m/s and ratios
1.016 and 1.038 at `n` = 2 and 3.

Three consequences, all of which correct the record:

1. **"The body sinks at -14.77 m/s^2, worse than free fall" is false.** It never
   sinks at 1.5 g. It takes one discontinuous velocity step and then sits there.
2. **"Error diverges under refinement, about 10x" is false.** The step is
   -0.013988 m/s at g64 and -0.102929 m/s at g96, a factor 7.36; `dt` falls from
   3.0303e-3 to 2.0833e-3, a factor 1.4545. Their product is 10.7, which is the
   entire reported "10x divergence." It is `step size / dt`, not a diverging term.
3. **`F_buoy_from_a` = -9540.96 N at g96 is not a negative buoyant force.** It is
   `m*(a+g)` evaluated on a fitted slope that has no physical referent.

**Why the step exists. H4 is CONFIRMED, and it is a harness defect.**
`BoxTank.pin` (`:231-236`) writes `rigid_x_cm` and calls
`set_rigid_body_velocity`, and `set_rigid_body_velocity`
(`mpm_solver_warp.py:880-885`) writes **only** `rigid_v_cm` and `rigid_omega`. It
does not touch `particle_v` or `particle_x`. The kernel that syncs particles to
body state, `rigid_particle_update` (`mpm_utils.py:1463-1493`), runs at the END of
each substep inside `_p2g2p_tail` (`mpm_solver_warp.py:1364-1367`) and is not
re-run after `pin()`. Meanwhile P2G has no material gate at all:
`p2g_apic_with_stress` (`mpm_utils.py:920-923`) gates only on
`particle_selection`, and `p2g_particle:885-916` deposits
`weight * particle_mass * (particle_v + C*dpos)` for every particle. So on the
first substep after release the box deposits its stale pre-pin velocity into the
grid and immediately reads it back through `rigid_g2p_accumulate`. The settle loop
(`:479-487`) pins once per FRAME, not once per substep, so the body free-falls
through all 11 (g64) or 16 (g96) substeps of every frame and is teleported back
900 times.

**A second contribution, also protocol, also confirmed: the g96 settle never
converged.** `c1_rigid_g96.json` reports `settle_frames_run` 900 against a cap of
900 with `settle_gate_met` **false** and `settle_vmax_final` 2.1404 m/s,
`c/vmax` = 7.55, below the harness's own target of 20 and below the project's 10x
criterion. The g64 arm met the gate at 444 frames with `vmax` 0.6405 and
`c/vmax` = 16.95. **The g96 free-rigid number was measured on water that was still
sloshing.** It should never have been reported as a refinement of the g64 number.
`c1sdf_box_g96` also missed the gate; both SDF arms met it (354 and 776 frames).

## What survives: the coupling defect is real

Retracting the sign inversion does not rescue the coupling. Take the g64 arm,
where the settle gate PASSED and the water is demonstrably hydrostatic:

| quantity | value | correct value |
|---|---|---|
| late-window acceleration | **+0.10026 m/s^2** | +6.5400 m/s^2 |
| fraction of correct | **1.53 %** | 100 % |
| `v` after 160 substeps (0.4848 s) | +0.00143 m/s | +3.171 m/s |

At g96, late-window acceleration is +0.05509 m/s^2, **0.84 %** of correct. The
body does rise, in the right direction, at roughly one percent of the right rate.

On the identical water at the identical instant, the SDF collider reads the
buoyant force to within 7.7 percent. **The force is present in the fluid and is
measurable. The free rigid body simply does not receive it.** The SDF arm's own
`a_free_body_implied`, which is `(F_steady - weight)/mass`, is +5.286 m/s^2 at g64
and +7.730 m/s^2 at g96, bracketing the ideal +6.540. That is what the body would
do if the measured force were actually applied to it.

**Mechanism, from source, not inferred from the numbers.**
`rigid_body_integrate` (`mpm_utils.py:1434`) sets `v_cm_new = rigid_linear_mom / M`,
where `rigid_linear_mom` is `sum_p m_p * v_interp` accumulated by B-spline gather
from `grid_v_out` (`:1402-1411`) and `M = rigid_mass[b]` is the sum of those same
particle masses (`mpm_solver_warp.py:851-853`). Expanding the gather,
`M v_cm_new = sum_i m_i^R v_i`, where `m_i^R` is the rigid contribution to nodal
mass. **The body's velocity is a mass-weighted AVERAGE of the grid velocity at its
own particles. No force, impulse or torque is ever formed, and no momentum is
integrated.** The body is kinematically slaved to the grid.

That is why buoyancy cannot be delivered. Rigid particles deposit mass and
momentum but never stress (`mpm_utils.py:1090-1091`, `F = I` for material 8, and
no stress branch assigns material 8), so grid nodes in the cube's interior carry
only rigid mass and see only gravity. Water pressure reaches the body solely
through the shell of nodes where water and rigid mass coexist, and even there only
in the ratio `m_i^R / m_i`, because the nodal stress force is normalized by TOTAL
nodal mass. The free-falling interior dominates the average. This is structural in
the fork's design, not a typo, and no parameter in this project's control changes it.

## Does this touch the 17 gated runs? Yes.

The 17 runs build the vehicle with `set_material_range(..., "rigid", obj_id=...)`
followed by `finalize_rigid_bodies()`, then step. That is the same free rigid body
path, the same `rigid_body_integrate`, the same velocity-averaging coupling
measured above. **Every displacement in `data/all_runs_inventory.csv` was produced
by a coupling that, on a case with an exact analytic answer, delivers about
1.5 percent of the correct rigid-body response to a fluid load.** That has to be
stated in the paper, the register, the README and any public artifact. It is not
softened by anything found here.

What does NOT carry over: the pin-release step and the failed g96 settle are
properties of the C1 measurement protocol, and the 17 runs have neither. Per
CLAUDE.md item 3 the vehicle is registered once at `sim_standing.py:129-131` and
never written again, so there is no pin and no teleport. The retraction of the
sign inversion is therefore a retraction about C1, not a clearance for the 17 runs.

**Do not reach for the conservatism argument here.** The literature that says
coarse resolution over-predicts peak hydrodynamic force (Wei and Dalrymple 2016;
St-Germain, Nistor and Townsend 2012; Jian et al. 2016; Kleefsman et al. 2005) is
about the FLUID load, and the SDF arm shows the fluid load on this scene is
already close to right. The defect found here is in the body's RESPONSE to that
load and points the other way: the body under-responds. Those are different
mechanisms in opposite directions and must not be netted against each other. The
honest statement is that the direction of the net effect on the 17 runs' verdicts
has not been tested and is not known from this work.

What is genuinely not at stake, and is separately sourced: CLAUDE.md item 5
records that the binary verdict is grid-invariant across g48/g64/g96, all nine
NO-FORD, and that the project already cites the verdict and never the displacement
magnitude. That standing instruction limits the blast radius. It does not remove
the obligation to state the defect.

## Findings produced by building the test

1. **The cold-start transient is violent and this is structural.** At `t=0`,
   `F = I` everywhere, so `J = 1`, so `pressure = -K(1 - 1) = 0`. There is no
   pressure field, therefore no buoyancy, and a body released at `t=0` free-falls
   at exactly `-g` regardless of density. The water column collapses dam-break
   style before hydrostatic pressure establishes. Measured: `vmax` peaks at
   **8.1059 m/s**, `c/vmax = 1.58`, and it takes **158 frames (5.27 s)** to decay
   to `c/vmax = 20`. For most of that settle the 10x sound-speed criterion is
   violated, worse than the 4.28 minimum register B8 records for the canonical
   runs. **Consequence: C1 cannot be measured from a cold start**, and any future
   scene that starts water at rest inherits this transient.
2. **The 10x criterion is a settle-phase problem too, not only a sweep problem.**
   Register B8 covers the canonical runs' velocity sweep. This adds that the
   initialization transient alone drives the ratio to 1.58.
3. **Volume bookkeeping against an assumed tank area is not safe.** A rind of
   water up to ~1.04 dx thick sits outside the wall planes (6.8 % of particles
   beyond a 0.5 dx tolerance), so the true footprint exceeds the nominal
   `A_tank` by roughly 7 %, comparable to the 8.33 % measurement floor. The draft
   estimator was changed to a per-column median of `vol()/bin_area` over free
   columns, which uses only measured quantities and is immune to the rind. The
   assumed-area result is retained as a labelled cross-check.
4. **The P2G edge guard bounds the usable resolution from below.** With the wall
   inset fixed in metres so geometry stays invariant under refinement, the guard
   (`1.5 dx` low, `LIM - 2.5 dx` high) fails at `n_grid = 32`. 48, 64 and 96 pass.
5. **A false-pass mode exists for C2 and must be controlled.** A coupling broken
   in the "frozen" direction, where the body simply holds whatever grid velocity
   it sits in, would pass a C2 started at the analytic draft. C2 therefore runs
   from two initial drafts, the analytic value and analytic + 2 dx, and requires
   both to converge. Without that control C2 is not a valid test.
6. ~~**C1's headline must be the earliest window.**~~ **RETRACTED 2026-08-07 by
   the job 894731 data.** The reasoning was that on the first substeps the body
   has not moved, so there is no added-mass reaction and the measured
   acceleration should sit near `a_ideal`. The argument is sound in continuum
   terms and wrong for this harness. The earliest window is the MOST contaminated,
   not the most honest, because the pin-release velocity step lands entirely
   inside it: the step model reproduces the `n` = 2 and `n` = 3 windows to
   0.2 percent at g96 (see the retraction section above). The earliest window
   measures the pin, not the fluid. On this harness the LATE window is the only
   one with physical content, and it reads +0.100 m/s^2 at g64 against +6.540
   ideal. Any future C1-shaped test must either release from a state where
   particle and body arrays agree, or drop the acceleration inference entirely
   and use a collider wrench.

7. **`realized_rho` is a tautology and cannot test H3.** The harness computes
   `realized_rho = mass / (n_side^3 * h^3)` (`BoxTank:195`) while `mass` is itself
   `rho_box * length^3` (`:172`) and `length = n_side * h` (`:135`), guarded by an
   exact-multiple check at `:132`. It therefore reduces algebraically to `rho_box`
   at every resolution. Measured: **599.9999999999999 at both g64 and g96**, in
   every one of the ten result JSONs, against 600 requested. The figure is
   reported here because it was asked for, and it does satisfy the project's
   coupled-variables rule, but it has no diagnostic power: it could not detect a
   grid-coupled density even if one existed. H3 is therefore neither confirmed nor
   excluded by this quantity. It is separately made irrelevant by the SDF arm,
   which has no mass at all and still reads the correct buoyant force, so no
   density error can explain the free-rigid result.

8. **The seeded lattice is exact at both resolutions**, which removes a second
   candidate. `n_side` is 20 at g64 and 30 at g96, `n_side * h == L_BOX` to
   `rel_tol` 1e-12 in both cases, and the cube spans exactly 10.0 and 15.0 cells.
   Recomputed independently from the harness constants, not read from a summary.

## Repo defects found while surveying, not yet in the register

Verified live 2026-08-07. These are recorded here because the register was owned
by another session; promote them when ownership is settled.

- **Register item 13 undercounts DRIFT_THRESHOLD.** 17 declaration sites under
  the four listed names, not 16. The likely missed one is
  `docs/session_notes/archive/mu_sweep_recovered_from_staging.py:60`. Plus
  `simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN:60`, which a `.py` filter misses.
- **A fifth, undocumented name exists: `L2_DRIFT_M = 0.05`, 7 further sites**
  across `analysis/make_poster_figures*.py` and three `deliverables/` copies.
- **`simulation/failure_modes.py` has three `0.05` literals, not two.** `:46`
  `slide_m` and `:48` `float_m` are metres; **`:47` `slide_speed_ms` is m/s**. A
  naive find-and-replace would silently convert a speed into a distance.
- **`scripts/check_claims.py:154` asserts five `9.81` sites; there are 7.** The
  two `9.80665` sites are correct. Unifying on 9.81 is the consistent direction
  since the solver hardcodes it.
- **`grep -r <pattern> .` silently skips `renders/` in this sandbox.** Any prior
  audit using recursive-grep-from-dot has undercounted that subtree. Use
  `find ... -print0 | xargs -0 grep`.
- **`renders/yaris_render_s1/failure_modes_result.json` is untracked by git**, in
  addition to the defects register D6h already records.
- The register's claim that `four_rung_ladder*.md:136` still miscite that file is
  **stale**; commit `841d666` repointed both, and register line 147 already says so.
- **`check_claims.py` rule C13 has no agreement exemption.** It fired three times
  on this file for sentences that RESTATE its authority correctly, not contradict
  it, because it substring-matches the claim text. Verified live against
  `CLAUDE.md:150` and register `D5` at `:126`; both agree with what was written.
  The hook's own message says to leave text that quotes a claim in order to
  correct or retire it, but agreeing restatements hit the same matcher. Worth an
  exemption for lines that also cite the authority. Flagged for the rule's owner
  rather than edited, since `check_claims.py` belongs to another session.

## Process items, recorded not fixed

**a. A green Slurm status is not evidence the science ran.** `sacct` reported
COMPLETED for jobs in which 4 of 9 invocations raised uncaught exceptions, because
the wrapper had no `set -e` and Slurm sees only the wrapper's exit code. Verified
live: `run_coupling_validation.sbatch`, `c1only.sbatch`, `c2only.sbatch` and
`c1sdf.sbatch` all carry `set -u` and none carries `set -e`. The fix already
exists and is better than `set -e`: `c1sdf.sbatch:45-62` captures each
invocation's `rc`, echoes a `STATUS <tag> rc=<n> OK|FAILED` line, counts failures,
and exits `$((FAILED > 0))`, so one crash neither hides nor cancels the rest. That
is why job 894731 could report `ALLDONE_C1SDF failed=0` and have it mean
something. Propose adopting that `run()` helper as the standard wrapper and adding
the rule to CLAUDE.md beside "a commit message is not a register edit" and "a
status line is not a results read."

**b. The scripts that produced every surviving J.1 number were not in git.**
Broader than first scoped. Missing from the repo and present only on Vista:
`c1only.sbatch`, `c2only.sbatch`, `c1sdf.sbatch`, `c1sdf_smoke.sbatch`, and
`run_silverado_hull.sbatch`. **All four `c*` files are retrieved and tracked by
this commit.** Not yet resolved: `simulation/validate_coupling_force.py` on Vista
is **869 lines** against the repo's **618**, sha256
`ff64e25421b0ae8fa290490cb322107254d3e3f1c6ac33248382d8129d92e813`. It adds
`cube_mesh`, `sdf_margin_cells`, `build_box_sdf` and `run_c1_sdf`, and it modifies
`BoxTank` in six hunks to carry `box_mode`. The rigid path is unchanged in
substance, evidenced by `c1_rigid_g64` reproducing `c1_g64` at -1.4367 against
-1.4410 and `c1_rigid_g96` reproducing `c1_g96` at -14.794 against -14.772. It is
retrieved to scratchpad but **NOT committed**, because landing it overwrites a
tracked file while other sessions are live, which needs explicit confirmation.

**c. C3 is undefined by construction and should be replaced, not repaired.** For a
neutrally buoyant body `a_ideal = g(1000/1000 - 1) = 0`, and
`validate_coupling_force.py:549` computes a percent error against it, so the
ZeroDivisionError is the specification, not a crash. Recommend replacing the
relative test with an absolute tolerance in m/s^2, since the quantity under test
is an acceleration that should be zero and has a natural absolute scale: assert
`|a_measured| <= tol` with `tol` stated in m/s^2 and justified against `g` and the
substep count. `run_c3:570-573` already computes `a_expected_compressible` from the
EOS, which is the correct non-zero reference and is the better target than 0.

**d. C2's edge-guard death is a symptom of the same defect, not a separate bug.**
C2 has produced zero numbers in four attempts, dying at `core/solver.py:508`. The
guard at `:507` raises when any particle is within 2 cells of the grid edge. It is
not the water and not the initial placement: recomputed independently, the water
lattice spans [0.6109, 8.8108] m at g64 against a guard window of (0.2208, 9.0537),
and [0.6036, 8.8182] against (0.1472, 9.1764) at g96, so `guard_ok` is true at both
and nothing is near the edge at `t = 0`. **It is the box.** `core/solver.py:216-218`
states that grid boundary conditions do not affect rigid particles, and a plane is
registered as a rigid contact surface only when `restitution != 0.0`
(`mpm_solver_warp.py:1915`). Every plane in this harness is added with
`restitution=0.0` (`BoxTank:184-189`), a deliberate choice recorded in the script's
own `PROVENANCE` under `deviation_from_canonical`, so the floor is invisible to the
body. The body therefore sinks, per the defect above, passes through the floor
plane, and trips the guard. Commit `20dd999` ("Deepen C2 water to 18 cells; the box
was sinking through the floor plane") had already reached the same diagnosis.
**C2 cannot produce a number until the coupling delivers buoyancy, or until the
floor is given `restitution > 0` so the body is caught.** Deepening the water
cannot fix it, because the sink rate is not bounded by depth.

## Is J.1 closeable?

**No. It is closeable on its central question and not on its stated scope.**

Answered, with primary-source evidence: the coupling force is wrong on the free
rigid body path; it is not a sign inversion; the fluid load itself is close to
correct; the defect touches all 17 gated runs. That is more than J.1 asked for on
the diagnostic side.

Missing before it can close:

1. **C2, the Archimedes equilibrium-draft test, still has zero results.** J.1 names
   it FIRST. It cannot run until item (d) is resolved. This is the single largest
   gap and no amount of C1 analysis substitutes for it.
2. **A clean C1 at g96.** The published g96 free-rigid number was measured on
   unsettled water (`settle_gate_met` false, `c/vmax` 7.55). It must be re-run with
   a settle cap high enough to meet the gate before any g64-to-g96 statement is
   made. Until then there is exactly ONE trustworthy free-rigid data point, g64.
3. **C3 needs the redefinition in item (c)** before it can produce a verdict.
4. **The pin must be made state-consistent, or abandoned.** Any future C1 must
   sync `particle_x` and `particle_v` when it writes `rigid_x_cm` and
   `rigid_v_cm`, or the release step returns. The public `set_x`/`set_v` on the
   wrapper are sufficient for this; no solver change is required.
5. **The direction of the defect's effect on the 17 runs' verdicts is untested.**
   Stated as unknown above. Closing J.1 without testing it would leave the paper
   claim unsupported in either direction.

Not attempted here, deliberately: no solver fix, and no change to
`run_c0`/`run_c1`/`run_c2`/`run_c3`/`BoxTank`.

## Reproduce

```
sbatch scripts/c1sdf.sbatch                 # the discriminator, job 894731, 7m38s
sbatch scripts/run_coupling_validation.sbatch
```

`scripts/c1sdf.sbatch` requires the 869-line `validate_coupling_force.py` that is
still Vista-only; see process item (b). The repo's 618-line copy has no `c1sdf`
variant and will fail on `--variant c1sdf`.

Analytic layer, no GPU required, exercises the real module with stubbed
device imports: see the verifier described in the commit message. Asserts the
lattice identity, the canonical substep counts 11 and 16, geometry invariance
across the refinement step, and both draft formulas against an independent
numerical solve.
