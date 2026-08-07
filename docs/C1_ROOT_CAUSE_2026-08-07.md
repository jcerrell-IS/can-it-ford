# C1 coupling-force test: root cause of the reported sign inversion

Date: 2026-08-07. Owner: the ctx-census session.

This file is ADDITIVE to `docs/COUPLING_VALIDATION_J1_2026-08-07.md` and does not
edit it. That file was owned by another session at the time of writing. Where the
two disagree, the disagreements are listed explicitly in section 6 below and this
file states why, with the primary source. Promote into the register when
ownership is settled.

## 0. Provenance tiers, read this before citing anything below

Every claim in this file carries one of three tiers. They are not interchangeable.

- **T1 READ LIVE BY THIS SESSION.** A line I opened myself at the stated path.
  Line numbers in the vendored solver are stable (pinned SHA, never edited).
  Line numbers in `simulation/validate_coupling_force.py` are NOT stable: another
  session was actively editing that file during this work, blob
  `2431d314a65ab5e867d2b5bbd741fbb47ab7b380` (869 lines) at 16:34 becoming
  `745cd488cee463437489395e3bbed95088228929` (871 lines) at 18:57. Every line
  number I give for that file is against blob `745cd488`. **Cite the symbol name,
  not the line number**, and re-locate before editing.
- **T2 MEASURED ON VISTA.** Pulled by me from the JSON on Vista at
  `$WORK/can-it-ford/data/coupling_validation/`, not transcribed from a doc.
- **T3 DERIVED.** Arithmetic I performed here, shown so it can be rerun.

Nothing in this file is tier "an agent said so". A 12-agent workflow produced the
initial hypothesis set; every load-bearing claim it made was then either verified
against source by me or is absent from this file. Two of its quantitative
predictions were falsified by the Vista data and are recorded as such in
section 6.

## 1. The mechanism (T1)

The material-8 rigid body has no equation of motion. It is kinematic.

Per-substep order, `kernels/mpm_solver_warp.py:1338-1367`, `_p2g2p_tail`:

| step | line | what it does |
|---|---|---|
| zero | `:1344-1347` | `set_vec3_to_zero` on `_rigid_linear_mom` and `_rigid_angular_mom` |
| gather | `:1349` | `rigid_g2p_accumulate` |
| integrate | `:1355` | `rigid_body_integrate` |
| restitution | `:1362` | `_apply_rigid_restitution(dt)` |
| push | `:1364` | `rigid_particle_update` |

The gather, `kernels/mpm_utils.py:1402-1412`, builds `v_interp` as a quadratic
B-spline gather of `state.grid_v_out` over 27 nodes, then:

```
1411        wp.atomic_add(rigid_linear_mom, bid, v_interp * mass_p)
```

The integrate, `kernels/mpm_utils.py:1434`, is in full:

```
1434    v_cm_new = rigid_linear_mom[b] / M
```

`M` is the sum of the same particle masses, `kernels/mpm_solver_warp.py:856`.

There is no force term, no impulse, no `v_old` term, and the accumulator carries
nothing across substeps because `:1344-1347` just zeroed it. **The body's velocity
IS the mass-weighted mean of the grid velocity at its own particles, recomputed
from scratch every substep.**

Corollary, and this is the load-bearing consequence: a quantity computed as
`m dv/dt` on this path is `(M/dt)` times the change in a local grid average. It is
kinematic, not a reaction. **`m dv/dt` cannot serve as a force proxy here.** That
is the direct answer to register A3, which correctly records that no force
accessor exists; the finding is that the workaround does not work either.

The repo's own source already says this, in the `run_c1_sdf` docstring: "no force
or impulse is ever formed, so C1's `F_buoy_from_a` is a back-computation, not a
measurement."

Supporting: material 8 carries identically zero stress. `particle_F` is set to
identity at `kernels/mpm_utils.py:1090-1091`, and no branch in the stress block
`:1106-1146` tests `mat == 8`. Rigid particles deposit mass and momentum only.

## 2. The reported numbers are 94% and 99.8% measurement artifact (T1 + T3)

`run_c1` computes every window as `np.polyfit(t[:n+1], v[:n+1], 1)[0]`, and the
headline is hardcoded to the N=3 window. **Sample 0 is included.**

`pin()` calls `set_rigid_body_velocity`, which writes only `rigid_v_cm`
(`mpm_solver_warp.py:880-885`). Nothing dynamical reads that write:
`rigid_body_integrate` at `:1355` overwrites `rigid_v_cm` before
`rigid_particle_update` at `:1364` pushes it to particles, and P2G reads
`state.particle_v` (`mpm_utils.py:888`), never `rigid_v_cm`. The pin's velocity
write is a **dynamical no-op but a reporting write**, because `rigid_state()["v"]`
returns `rigid_v_cm` verbatim. So `v_series[0] = 0.0` is a fiction and every
window straddles an artificial discontinuity.

For a step of size `dV` at sample 1, the least-squares slope over samples `0..N` is
exactly `6*dV/(dt*(N+1)(N+2))`. Model `a(N) = 6*dV/(dt*K) + a_s` with
`K = (N+1)(N+2)`; then `a(N)*K` is linear in `K`. My own OLS over all six
published windows (T3):

| grid | dt | fitted dV | fitted a_s | max residual |
|---|---|---|---|---|
| 64 | (1/30)/11 | -0.013574 m/s | -0.0891 m/s^2 | 1.71 % |
| 96 | (1/30)/16 | -0.103030 m/s | -0.0195 m/s^2 | 1.55 % |

Two constants per grid reproduce all twelve published window values.

**Vista then confirms the prediction (T2).** Measured `v_series`:

```
c1_g64  v[0:6] = [0.0, -0.01403,  -0.014254, -0.014481, -0.014714, -0.014954]
c1_g96  v[0:6] = [0.0, -0.102763, -0.102565, -0.102647, -0.102761, -0.102871]
```

`v[0]` is exactly 0.0, `v[1]` matches the fitted `dV` to 3.4 % (g64) and 0.26 %
(g96), and `v[2..5]` are flat. It is a step, not a ramp.

**Therefore the sign is inverted in `np.polyfit`, not in the physics.**

## 3. The physical number, and it is positive (T2)

`a_late_window` is a polyfit over the second half of the measurement window, which
excludes the release entirely. It has been computed and stored in the JSON since
the first run and appears in no table in the J.1 doc. Only stdout was filtered;
the file kept it.

| run | a_late_window | a_ideal | fraction of analytic |
|---|---|---|---|
| `c1_g64`  | **+0.1001239440643532** | +6.5400 | 1.53 % |
| `c1_g96`  | **+0.04374164213656068** | +6.5400 | 0.67 % |
| `c1_rigid_g64` | +0.10026115351478428 | +6.5400 | 1.53 % |
| `c1_rigid_g96` | +0.05508585908225538 | +6.5400 | 0.84 % |

Positive, i.e. the correct direction. The g64 trajectory actually crosses zero:
`v` runs 0.0, -0.01403, ..., -0.024325 at sample 60, then rises to +0.004059 at
sample 120. The body ends up moving upward.

**The correct claim is therefore NOT "cannot float".** It is: the path cannot
integrate a force, so it cannot sustain acceleration; it relaxes toward a
quasi-steady velocity, and the buoyant response it registers is about 1.5 % of
analytic at g64. "Cannot float regardless of density" is falsifiable by a single
run and is falsified by the table above.

## 4. The refinement comparison was never controlled (T2)

| run | settle_gate_met | frames run | vmax at release |
|---|---|---|---|
| `c1_g64` | **True** | 444 | 0.6403 m/s |
| `c1_g96` | **False** | 900 (cap) | **2.1288 m/s** |
| `c1sdf_box_g96` | **False** | 900 (cap) | 1.6405 m/s |
| `c1sdf_sdf_g96` | True | 776 | 0.6341 m/s |

The g96 free-rigid body was released into water still moving at 2.13 m/s because
it hit the 900-frame cap without meeting the gate. Comparing it against a settled
g64 run is not a controlled comparison, so **"diverges 10x under refinement" is
not supported** and cannot be used to argue "a wrong term rather than an
under-resolved one".

The gate's `ratio_target` is 20 and both free-rigid runs finished below it (16.94
and 9.31). The SDF g96 arm met the same gate at 776 frames, so the criterion is
reachable and the frame budget was the binding constraint. Any re-run should raise
the cap to ~1200 and treat a cap hit as a discard.

## 5. The discriminator fired: the defect is in the free-rigid coupling (T2)

Job `894731` ran the same cube and water as a FIXED COLLIDER. A collider does form
a real force: it accumulates `sum m*(v_free - v_new)` on the grid before
overwriting node velocity, and divides by `dt`. Analytic buoyancy
`rho_w V g = 31298.444315169316 N`.

| path | grid | F_z steady | vs analytic | F_z first-3 | vs analytic | settled |
|---|---|---|---|---|---|---|
| **SDF collider** | 64 | 28898 N | **-7.7 %** | 31806 N | **+1.6 %** | yes |
| **SDF collider** | 96 | 33577 N | **+7.3 %** | 33213 N | +6.1 % | yes |
| box collider | 64 | 19432 N | -37.9 % | 16705 N | -46.6 % | yes |
| box collider | 96 | 24639 N | -21.3 % | 24035 N | -23.2 % | **no** |
| free rigid | 64 | 16021 N back-computed | -48.8 % | | | yes |
| free rigid | 96 | -9541 N back-computed | -130.3 % | | | **no** |

The script's own discriminator table scopes this: "collider right, free-rigid
wrong -> defect is in the free rigid coupling". So:

- the water **is** hydrostatic,
- the scene and the harness are sound,
- the buoyant force **is** present and correct on the grid to within about 8 %,
- and the free-rigid body simply fails to consume it.

This is the project's first coupling measurement validated against an answer set
outside the code. Register C13 and CLAUDE.md item 6 record that no such rung
existed. **Caveat: no tolerance was pre-registered, so ±7.7 % is a measured
agreement, not a passing gate.** Do not write it as a gate.

## 6. What this supersedes in `COUPLING_VALIDATION_J1_2026-08-07.md`

Four items, each with the reason:

1. **The headline errors** (-122.03 % at g64, -325.87 % at g96) and the forces
   derived from them (16020.60 N, -9498.11 N, -48.81 %, -130.35 %) are estimator
   output, not measurements. See section 2. Mark as withdrawn, do not delete the
   record.
2. **"Refining the grid makes it worse by a factor of 10 ... the signature of a
   wrong term, not an under-resolved one."** Not supported: the g96 arm never
   settled. See section 4.
3. **Finding 6, "C1's headline must be the earliest window."** Inverted for this
   failure mode. The release-step weight is `6/((N+1)(N+2))`, which is 0.5 at N=2
   and 0.0035 at N=40, a 143x range, so the earliest window MAXIMISES the
   contamination. The late window is the clean one and it was already being
   computed and stored.
4. **"C0 shows the rigid integrator and the grid-gravity path are correct."** Too
   strong. `run_c0` builds the tank with `water=False`, so every massed node
   carries only rigid mass, the gather returns `v_body + dt*g` exactly by
   partition of unity, and the update degenerates to `v_new = v_old + dt*g`. C0
   validates gravity and B-spline partition of unity. It cannot validate the
   coupling because nothing is coupled, and it cannot validate force handling
   because there is none. It is a self-consistency check in the same category as
   `gates.py` G-3 (CLAUDE.md item 6).

**Two predictions from the analysis that Vista FALSIFIED**, recorded so they are
not repeated: the fitted `a_s` was predicted to be the sustained acceleration and
to be negative (-0.089, -0.0195). Measured `a_late_window` is POSITIVE (+0.100,
+0.0437). The early-window fit is still transient-contaminated; only the late
window is clean. Magnitude was right to within a factor of ~2, sign was wrong.

## 7. Citation defect: `mpm_solver_warp.py:851-853` is wrong (T1)

At the pinned SHA the cited range does not contain the assignment:

```
851  x_cm_np = np.zeros((self.n_rigid_bodies, 3), dtype=np.float32)
852  mass_np = np.zeros(self.n_rigid_bodies, dtype=np.float32)
853  for b in range(self.n_rigid_bodies):
854      idx = np.where((mat_np == 8) & (rid_np == b))[0]
855      m_b = m_np[idx]
856      mass_np[b] = float(m_b.sum())
```

Correct range is **`:853-856`**, or `:856` for the sum alone. 851-853 is the
allocation plus the loop header.

23 occurrences, found with `/usr/bin/grep`. THREE source sites:

- `simulation/validate_coupling_force.py`, `PROVENANCE` dict, key
  `rigid_mass_is_particle_sum` (line 37 at blob `745cd488`)
- `simulation/validate_coupling_force.py`, `run_c1_sdf` docstring (line 712 at
  blob `745cd488`; it was line 710 an hour earlier, the file is being edited)
- `scripts/c1sdf.sbatch:18`, header comment

Plus **20 stamped run artifacts** in `data/coupling_validation/` (12 top level,
8 in `smoke/`). Those cannot be fixed: the `PROVENANCE` dict is serialised into
every result file. If the source is fixed, record which side of the fix each JSON
falls on, or the record carries two provenance strings with no way to tell which
run used which.

**Search warning, this cost two sessions a round trip each.** `grep` in this
environment is a shell function wrapping ugrep with `--ignore-files`, and
`.gitignore` has `data/*`, so a bare `grep -rn "851-853" .` returns 3 and hides
all 20 artifacts. `/usr/bin/grep` returns 23. Separately, zsh expands a bare
`--include=*.py` to "no matches found" so the search never executes at all, which
reads exactly like a clean result. Confirm a search actually ran before treating
an empty result as absence.

## 8. Scope limit: do NOT extrapolate to the 17 gated runs

The 17 runs are on this same path. `renders/yaris_render_s1/sim_standing.py`
registers the vehicle via `set_material_range(self.n_water, self.n_total,
"rigid", obj_id=0, density=vehicle_density)`, and
`mpm_solver_warp.py:854` keys on `mat_np == 8`. That link is established (T1).

What follows at HIGH confidence: no force, drag or hydrodynamic-load number may be
back-computed from vehicle acceleration in those runs. If any figure, caption or
paper text does so, withdraw it.

What follows at MEDIUM confidence and should be checked, not assumed: the
SLIDE/STUCK classification reads displacement and pitch/roll, which are integrals
of this same non-Newtonian velocity, so the verdicts may inherit the defect.
`simulation/failure_modes.py` `surge_accel_g` and `weight_n` are exactly the kind
of derived force quantity the previous paragraph forbids.

What is **NOT** claimed: that the binary NO-FORD verdicts are wrong, or that the
17 runs "should have floated". Three blocking objections, all live:

1. **Regime gap.** C1 is a uniform cube, FULLY submerged, in STILL water, with
   every plane at `restitution=0.0`, which `mpm_solver_warp.py:1915`
   (`if restitution != 0.0`) makes invisible to the rigid body. The 17 runs are a
   partially submerged vehicle in flowing water with `restitution=0.05` on the
   floor and all four walls, so `_apply_rigid_restitution` at `:1362` DOES modify
   the vehicle's velocity a second time, after the kinematic assignment. C1
   deliberately removed the very mechanism that may dominate there.
2. **Waterline resolution.** CLAUDE.md L-3: `realized_depth_m / dx` is exactly
   2.000 with 4 particle layers. A free surface cannot be resolved in 2 grid
   cells. A static hydrostatic calculation at exact hull geometry and an MPM run
   at 2-cell depth are not obviously comparable.
3. **Self-consistency is not validation.** Reproducing a mesh volume to 0.0000 %
   tests that a hydrostatics calculation matches another calculation of the same
   geometry. It does not test that the SIM should agree with it. Same structural
   gap as C0.

Closing this needs the regime gap walked one variable at a time from C1 toward the
gated scene: (a) fully submerged, still, no planes [have this]; (b) **partially
submerged, still, no planes** [do not skip, every number we have is for a fully
submerged body and the 17 runs never are]; (c) partial + floor at
`restitution=0.05`; (d) add flow. Restitution cannot be an independent rung and
cannot be tested on C1 at all: the body is mid-tank, so 0.0 and 0.05 read
identically there and would produce a false negative.

Note also that the collider path gives FORCE, not VERDICTS. A fixed collider
cannot slide, so it can never reproduce a SLIDE outcome. It can establish that the
load is wrong by a factor of N; it cannot say which way any individual verdict
flips. Direction of bias on the 16 SLIDE verdicts is UNKNOWN and untested.

## 9. Open

- The 7.59x ratio in `dV` between g96 and g64 is unexplained as physics, and given
  section 4 it may not require a physical explanation at all.
- C2, the primary Archimedes test, has still never produced a number at any
  resolution: every invocation raises "particles within 2 cells of the grid edge"
  at `core/solver.py:508`. Until it runs, nothing tests equilibrium buoyancy.
- C3 cannot produce a number until its zero-`a_ideal` metric is replaced with an
  absolute tolerance.
- `run_c1_sdf` and its helpers `cube_mesh`, `sdf_margin_cells`, `build_box_sdf`
  exist in NO COMMIT as of HEAD `9d53acc`; `scripts/c1sdf.sbatch` and
  `scripts/c2c3diag.sbatch` are untracked. That is the code behind job `894731`,
  the only externally-validated measurement in the project. Reconciling that diff
  is owned by another session and is deliberately not done here.

## 10. Reproduce

Vista, login node, no GPU:

```
cd $WORK/can-it-ford/data/coupling_validation
python3 -c "
import json
for f in ('c1_g64.json','c1_g96.json'):
    d=json.load(open(f))
    print(f, d['a_late_window'], d['v_series'][:6],
          d['settle']['settle_gate_met'], d['settle']['settle_vmax_final'])
"
```

The step-plus-slope fit of section 2 is pure arithmetic on the published window
table and needs no cluster access.
