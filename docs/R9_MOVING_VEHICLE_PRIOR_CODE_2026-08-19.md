# Prior code for the moving-vehicle-in-flooded-channel problem

Slot d19-priorcode, branch `claude/r9-priorcode`, 2026-08-19. Written for slot
d17-moving, who is writing a moving-vehicle driver and needs to troubleshoot
against prior art rather than intuition.

Every claim below is tagged. **[read]** means I read it in the named file at the
named revision this session. **[recv]** means another session resolved it and I
did not re-derive it. **[inf]** means I inferred it from something tagged [read].
No claim here is tagged from memory.

Reference trees cloned OUTSIDE this repo, at `/Users/josie/can-it-ford-refs/2026-08-19/`.
Nothing third-party is committed here.

| tree | revision read | licence |
|---|---|---|
| Anura3D_OpenSource | `d5cdf97`, 2026-07-27, all 16 remote heads swept | LGPL-3.0 |
| projectchrono/chrono | `7689fbc`, 2026-08-18, sparse `src/chrono_fsi` | BSD-3 (upstream) |
| CB-Geo `mpm` (vendored in REU_Knowledge) | **no git metadata, revision unknown** | see tree |
| NVIDIA `newton` (vendored in REU_Knowledge) | no git metadata, revision unknown | Apache-2.0 |
| ours, pinned solver core | `third_party/mpm-engine-544c93dd-solver-core` | in-repo |

---

## 0. The headline

Three mature implementations extract the hydrodynamic force on a body three
different ways, and the difference is not cosmetic. **[read]**

| | the force is | accumulated over | zeroed by | needs a dt? |
|---|---|---|---|---|
| **ours** (warpmpm) | momentum exchange, `m (v_free - v_new)` | grid nodes **and time substeps** | **the caller**, explicitly | **yes** |
| **Anura3D** | nodal traction `n·sigma·n` from particle stress | material points in adjacent elements | per node, per step, internally | no, it is a stress |
| **Chrono::FSI** | surface-integrated force over BCE markers | markers only, **not time** | the library, adjacent to use | no, it is a force |

**Ours is the only one of the three that accumulates over time, and therefore the
only one that needs a `dt` at all.** **[inf, from the three [read] rows]** That is
precisely why the wrench-dt hazard exists in our stack and cannot exist in the
other two. It is a consequence of the accessor's design, not a bug anyone
introduced, and it will not be fixed by being careful once.

---

## 1. In/outflow: the Zhao BC is NOT in the public Anura3D

The premise I was dispatched with was "Anura3D is open source, get it and read
how they actually did it." Half of that holds. The code is open source and I have
it. **The Zhao et al 2019 in/outflow boundary condition is not in it.** **[read]**

Scope, stated because an absence claim from a partial view is worthless:

- Repository `github.com/Anura3D/Anura3D_OpenSource`, HEAD `d5cdf97` (2026-07-27).
- Whole-tree case-insensitive sweep on `main`, 827 files, excluding `.git` and PDFs:
  `inflow` 0, `outflow` 0, `open channel` 0, `Zhao` 0, `hydrograph` 0.
- Then **all 16 remote heads** individually (`2025-Release`, `Alsardi_QUADElems`,
  `Hotfix_PT_Maximum_Steps`, four `ImplicitTime_*`, `LZC_ThinRigidBodies`, six
  `NURBS_*`, `Seismic_Alsardi`, `Time_Alsardi`, `main`), each fetched at depth 1
  and grepped over `src/*` for `inflow|outflow`: **0 files on every one.**

What Anura3D does have, and what it is not: `absorbing` appears in 16 files
including `src/MPMDynViscousBoundary.FOR`, and `prescribed velocity` in 11
including `src/LagrangianPhase.FOR`. **[read]** An absorbing/viscous boundary is
not an in/outflow BC; it damps outgoing waves rather than imposing a discharge.

**Consequence for d17, and it changes the plan:** there is no reference
implementation of the Zhao BC to check ours against. Our `simulation/openchannel_bc.py`
cannot be validated by reading someone else's code, because the someone else's
code is not public. Validating it needs a physical test (a uniform-flow control
with a known discharge), not a code comparison.

### 1a. Our own openchannel_bc.py is honest about this, and its citations hold

`simulation/openchannel_bc.py` already states its relationship to Zhao et al in
its own header, and states it correctly: Zhao et al add and remove material
points at the domain edges; warpmpm cannot add or remove a particle after load
time; so ours is one-in-one-out recycling in a fixed pool, which reproduces
Zhao's **uniform** channel case (equal inflow and outflow discharge by
construction) and **not** their non-uniform case. **[read]**

That file makes five line-cited claims about the solver. This project has a
documented line-drift problem, so I checked all five live against
`third_party/mpm-engine-544c93dd-solver-core`. **All five are exact:** **[read]**

| claim in openchannel_bc.py | verified |
|---|---|
| `load_particles` at `core/solver.py:103` | yes, `def load_particles` is at :103 |
| no `add_particles` / `remove_particles` / resize anywhere in Solver | yes, zero matches |
| `periodic_x` at `core/solver.py:93`, "Incompatible with CDF colliders and rigid bodies" | yes, both the line and the comment |
| `mpm_utils.py:1086-1089` overwrites `F` with `J^(1/3) I` for mat 6/10/12 | yes, the `elif mat == 6 or mat == 10 or mat == 12` branch |
| `kirchoff_stress_newtonian` at `mpm_utils.py:28`, pressure exponent 1.1 | yes, and `gamma = 1.1` is in the function body |

Nothing to fix. I am recording the pass because "I checked and it held" is worth
the same as a correction, and because the next person should not have to redo it.

---

## 2. Force extraction: the contract, and the one-sidedness

### 2a. The dt contract

Two halves, both **[read]** from the pinned solver core:

1. `Solver.step(dt, substeps=N)` at `core/solver.py:429` advances **N·dt** of
   physical time, not `dt`. Fused branch: `p2g2p_fused_tick(dt, substeps)` then
   `_step += substeps`. Unfused branch: `for _ in range(substeps): p2g2p(dt)`.
2. The wrench accumulator is additive across substeps:
   `wp.atomic_add(param.force, 0, impulse)` at `kernels/mpm_solver_warp.py:2734-2735`,
   zeroed only by an explicit `reset_sdf_force`.

**Therefore the only correct divisor is `dt * (substeps advanced since the reset)`.**

**Attribution warning.** There are three collider wrench accumulators in that
file and they belong to different colliders. `:2084` is the axis-aligned **box**
(`tool_force`). `:2223-2224` is the **revolved/cup** collider. `:2734-2735` is the
**SDF** collider, which is the one a vehicle hull uses. Boundaries confirmed from
`add_revolved_sdf_collider` at :2121 and `add_sdf_collider` at :2621. **[read]**
Citing :2223 for the vehicle path describes cup physics. I nearly did this.

### 2b. All four live call sites are correct

Audited by hand, then independently by the tool shipped with this document
(`analysis/r9_prior_code_compare.py`). **[read]**

| file | reset | advance | divisor | verdict |
|---|---|---|---|---|
| `coupling_force/coupler.py:147-151` | :147 | Python loop, `substeps_per_pose` x `step(dt)` | `cfg.dt * cfg.substeps_per_pose` | OK |
| `box_sdf_collider_setup.py:96-98` | :96 | `step(dt, substeps=20)` | `step_dt`, which is `dt * substeps` | OK |
| `realism_track/diag_wrench_fixed_pose.py:60-62` | :60 | `step(dt, 1)` | `tank.dt` | OK |
| `validate_coupling_force.py:766-768` | :766 | `step(dt, 1)` | `tank.dt` | OK |
| `sim_road.py:173-184` | :173 | `step(dt, substeps)` | `dt * substeps` | OK |

**The trap is that two different spellings are both correct.** `step(dt,1)` + `/dt`
and `step(dt,N)` + `/(dt*N)` are each right. Copying the `diag_wrench` spelling
into a substepped loop produces `step(dt,N)` + `/dt` and inflates force by exactly
N, silently. At the `substeps=20` used in `box_sdf_collider_setup.py` that is a
20x overstatement with no warning and no error. **[inf]**

Second failure mode, same signature: `reset_sdf_force` must be **inside** the
per-tick loop. Hoisted out, the accumulator grows monotonically and the reported
force **ramps linearly in tick index**. That signature is diagnostic: a linear
ramp from zero means check the reset placement before you look at physics. **[inf]**

### 2c. The wrench is compressive-only, and here is a clean control

**[read]** In the SDF collider block (`kernels/mpm_solver_warp.py:2686-2736`),
`v_new` is initialised to `v_free`; for `surface_type == 2` (separable) the
correction sits inside `if vn < 0.0:` only; and `impulse = m * (v_free - v_new)`.
So at every banded node where material is **separating** (`vn >= 0`) the impulse
is identically zero and that node contributes nothing to force or torque.

**Every `add_sdf_collider` call site in our tree passes `surface="separable"`**:
`box_sdf_collider_setup.py:77`, `validate_coupling_force.py:296`, `sim_road.py:133`. **[read]**

The estimator can represent pressure pushing into the hull but not suction on a
ventilated lee face, and the lee face is where a bluff body's wake sets form
drag. **I am not claiming drag is under-read by any particular amount.** For a
fully wetted, nearly incompressible body the constraint may be active almost
everywhere and the effect inert. That is the point: it is testable.

**The control.** Run the same scene twice, `surface="separable", friction=0.0`
against `surface="slip"`, and difference the wrench.

I put this claim through a five-point adversarial check against the kernel before
proposing it (the physics-skeptic subagent was unavailable this session, see
section 6, so I ran the attack myself; treat it as self-attacked, not
independently reviewed). It survives, with one correction to my own first
wording. **[read, all five]**

1. **Is the Coulomb scale exactly 1 at `friction=0`?** Yes.
   `scale = wp.max(0.0, tlen + param.friction*vn)/tlen` at `:2729` becomes
   `tlen/tlen = 1`. In the guarded `tlen <= 1e-12` case the scale is skipped and
   `v_tan` stays ~0, giving `v_new ~ v_surf`; slip in the same all-normal limit
   gives the same thing. The guard does not introduce a second difference.
2. **Does `slip` really map to 1 and `separable` to 2?** Yes, explicitly:
   `surface_id = {"sticky": 0, "slip": 1, "separable": 2}[surface]` at `:2628`.
3. **Does `friction=0.0` reach the kernel unrewritten?** Yes.
   `param.friction = float(friction)` at `:2673`, with no clamp and no
   validation. (The `sticky` + nonzero-friction `ValueError` at `:1902-1903`
   belongs to a **different** collider constructor and does not apply here.)
4. **Does anything else branch on `surface_type` or `friction`?** Not in the SDF
   path. `surface_type` only at `:2720` and `:2722`, `friction` only at `:2729`,
   plus a diagnostic export at `:2935`. No second variable.
5. **What happens at `vn == 0.0` exactly?** They **agree**. Separable takes no
   branch, so `v_new = v_free`; slip gives `v_surf + (v_rel - 0) = v_free` too.

**Correction to my own first statement of this**, which I put on the board as
"vn >= 0": the two configurations differ strictly on `vn > 0`, not `vn >= 0`. The
`vn == 0` set is measure-zero and nothing physical turns on it, but the sharper
form is what makes the closed form below exact.

**The sharpening this produced, which is better than the original claim.** For
slip, `v_new = v_free - vn*n` at every banded node, so
`impulse = m(v_free - v_new) = m·vn·n` there. Hence

```
wrench(slip) - wrench(separable, friction=0) = (1/dt) * SUM over nodes with vn > 0 of  m * vn * n_world
```

The difference is not merely "the one-sided contribution" in the abstract; it is
exactly the adhesive impulse the collider would have applied to separating
material. That is a quantity d17 can predict the sign of in advance, which makes
the control falsifiable rather than merely informative. **[inf, from [read] kernel]**

Do **not** use default-friction separable against slip for this. That confounds
one-sidedness with `friction=0.4` and the result would mean nothing.

### 2d. Prior art says the stress criterion is the known alternative

Anura3D carries **both** criteria. **[read]**

- `src/MPMDynContact.FOR:274` is the standard velocity criterion, `DiffDotUn>0.0`,
  commented "greater than 0 means approaching bodies". Same one-sidedness as ours.
- `:249` gates an alternative on `CalParams%ApplyTractionContact`, the "MODIFIED
  (TRACTION) CONTACT MODEL", which calls `EntityNodeTraction` at `:250` and
  switches the contact test to `Traction < 0` (compression). Their own comment
  block at `:255-261` documents the switch, including the first-contact exception
  where all stresses are still zero and it falls back to the velocity test.
- `:346` carries an adhesion term explicitly for the separation case.
- `EntityNodeTraction` (`:443-512`) builds traction from the **particle stress
  tensor** as `n^T sigma n`, weighted by `m_p * ShapeValues`, divided by nodal
  lumped mass (`:509-511`). Two-sided by construction, because tensile stress
  gives negative traction.

Our engine offers no traction criterion at all, so this is not a knob we have.
The control in 2c is how d17 finds out whether one is needed.

---

## 3. Moving rigid body: the pose contract

**[read]** `set_sdf_pose` is a **start-of-tick** command. Its own docstring:
"the modify_bc integrates `center += dt*velocity` and rotates the quat by omega
every substep ... (drive with `v = (target - prev)/dt_ctrl)`". The collider
**self-advects every substep** inside `step()` (`modify` at `mpm_solver_warp.py:2740`).
So `velocity` is a **control** velocity, not necessarily the body's physical one.

`coupler.py` satisfies this correctly and by construction, not by luck: it sets
`center = state.x_cm` and `velocity = state.v_cm` after integrating, and because
`integrate()` advanced `x_cm` by exactly `v * dt_total`, the solver's own internal
advance lands on the same place. **[inf, from [read] coupler.py:170-176 and rigid_body.py `integrate`]**

**Residual, and it is negligible, checked at the values actually used.**
`integrate()` is symplectic Euler: velocity first, position from the **new**
velocity (`rigid_body.py`, docstring and body). **[read]** So the tick-boundary
mismatch is `x(k+1) - [x(k) + v(k)·dt_total] = a·dt_total²`. Evaluated at the
real settings rather than at a guess: `CouplingConfig.substeps_per_pose`
defaults to 1 (`coupler.py:68`) and `rung_b_coupled.py:118` sets it explicitly
to 1, with the shipped artifact `realism_track/rung_b_ls6_3361315/rung_b_g64.json`
recording `dt = 3.0303e-3 s`. **[read]** So `dt_total = 3.03e-3 s`, and even at a
4 g net acceleration (39.2 m/s², the magnitude the rung-b transient reached) the
per-tick teleport is `39.2 * (3.03e-3)^2 = 3.6e-4 m`, 0.36 mm, against a contact
band of order `dx`. Two orders below the band. Not a problem, and the separate
`box_sdf_collider_setup.py` path (`dt=1e-4, substeps=20`, `:82-83`) is smaller
still at 0.04 mm. **[inf]**

**Two live traps that are not negligible:** **[read]**

1. **Torque is about `param.center`, not about the body COM.** The kernel
   accumulates `wp.cross(rel, impulse)` with `rel = xw - param.center`, and
   `sdf_wrench`'s docstring says "about the collider centre". `coupler.py` passes
   `center = state.x_cm`, so the two coincide there and it is correct. A driver
   that places the SDF at the hull's **geometric** centre while integrating
   Newton-Euler about the **COM** gets torque about the wrong point. For this
   hull that lever arm is real: CLAUDE.md item 4 records the cloud CG at 0.6312 m
   above the floor against bbox mid-height 0.7427 m **[read, CLAUDE.md:209-210]**,
   an 0.11 m offset. Correct with `tau_COM = tau_center + (center - COM) x F`.
2. **The tunneling guard is a `warnings.warn`, fired once.** Both the per-substep
   sweep guard (`modify`, `mpm_solver_warp.py`) and the `set_sdf_pose` jump guard
   warn once per collider and then go quiet. In a long run with output captured
   to a log, a single early warning is easy to miss. Do not treat a silent run
   as evidence the guard was satisfied; it is evidence it warned at most once.

---

## 4. Chrono::FSI as a live comparison

**[read]** `chrono` at `7689fbc`. `ChFsiInterface::LoadSolidForces`
(`src/chrono_fsi/ChFsiInterface.cpp:259` and `:542`) does:

```
fsi_body->body->EmptyAccumulator(fsi_body->fsi_accumulator);
fsi_body->body->AccumulateForce(fsi_body->fsi_accumulator, body_forces[ibody].force,
                                fsi_body->body->GetPos(), false);
fsi_body->body->AccumulateTorque(fsi_body->fsi_accumulator, body_forces[ibody].torque, false);
```

Empty and accumulate are **adjacent lines in the same function**. On the SPH side
the same discipline: `SphBceManager.cu:530-531` zero-fills `rigid_FSI_ForcesD`
and `rigid_FSI_TorquesD` immediately before launching `CalcRigidForces_D` at
`:537`. And the quantity is a force, not an impulse:
`SphDataManager.cuh:394` documents `rigid_FSI_ForcesD` as
"surface-integrated forces to rigid bodies", accumulated over BCE markers by
`atomicAdd` (`SphBceManager.cu:375-377`), never divided by a timestep.

**This is the design lesson, and it is the actionable one.** Chrono made the
reset impossible to forget by putting it adjacent to its use, and made the dt
impossible to get wrong by never exposing one. warpmpm made both the caller's
responsibility, separated by a user-written loop. If d17 wants the hazard gone
rather than merely avoided, the fix is to wrap `reset -> step -> read` in a single
helper that owns the dt, so no future caller can spell it wrongly. `coupler.py:143-151`
is already almost exactly that helper; the gap is that nothing forces its use.

Portability is settled and not in question: Chrono::FSI-SPH is recorded as
building and running on Vista aarch64 in 94 s **[recv]**. It is a live comparison
option. It is SPH, not MPM, so a difference against warpmpm is a difference in
method family and is not by itself evidence of a defect in either.

---

## 5. Negative results, each with its scope

These are worth as much as the positives and cost real time, so they are recorded
rather than dropped.

1. **Zhao et al 2019 in/outflow is absent from all 16 branches of public Anura3D.**
   Scope in section 1. **[read]**
2. **CB-Geo `mpm` as vendored has no rigid-body support and no in/outflow.**
   Whole-tree case-insensitive: `rigid` 0 files, `inflow` 0, `outflow` 0,
   `absorbing` 0, `free surface` 0. It does carry `contact` (9) and `traction` (13).
   **Scope caveat: the vendored copy has no `.git`, so I cannot state which
   upstream revision it is, and upstream may well have moved.** **[read]**
   This matters because CB-Geo is the group's own MPM code; it is not a source of
   a moving-vehicle coupling to copy.
3. **NVIDIA `newton` (vendored, Apache-2.0, revision unknown) has `rigid` in 165
   files, `sdf` in 78, `mpm` in 29, and `inflow` in 0.** **[read]** Not surveyed
   further this session; it is the nearest thing to a same-family (Warp) prior art
   and is the obvious next tree to read.

---

## 6. What I could not verify, and what I did not do

- **I did not run anything on a GPU.** Every statement about our solver is a
  source read, not a measurement. The control in 2c is proposed, not executed.
- **I did not verify the six DOI titles myself.** Those were resolved against
  Crossref by the coordinating session and are tagged **[recv]** wherever used.
  The one substantive point I carry forward: `10.1007/s11069-021-04949-6` is
  **issued 2021, not 2022**, and there are **three** distinct Al-Qadami papers
  (`10.1007/s11069-021-04949-6`, `10.1111/jfr3.12828`, `10.3390/su151713262`),
  which have now been conflated by two separate sessions. Any prose that says
  "Al-Qadami 2022" without a DOI is ambiguous between at least two of them.
- **The physics-skeptic subagent was invoked and FAILED to run.** It terminated
  with a model-access API error ("There's an issue with the selected model"), so
  **no independent adversarial review of anything in this document took place.**
  I did not fake it and I did not skip it silently. I ran the five-point attack
  on the section 2c claim myself instead, and it is written out in full there so
  a reader can check my checking; it found one real imprecision in my own wording
  (`vn >= 0` should be `vn > 0`) and produced a closed form I did not have before.
  Self-attack is weaker than independent review. Section 2c should be re-reviewed
  when the subagent is available.
- The `a·dt²` teleport estimate was the other open item and I closed it myself:
  re-evaluated at the settings the coupled runs actually use
  (`substeps_per_pose=1`, `dt=3.03e-3`), it is 0.36 mm, recorded in section 3.
- ~~**The corpus is silent on this whole topic**~~ **WITHDRAWN 2026-08-20, see
  section 45.** This was `[recv]` and it is FALSE: **10 of the 14 prior-art works
  are in the 332-paper corpus**, measured by me. The zero it rested on was a
  correct measurement of a **broken predicate**: `--query` matches title and
  abstract only, never authors. The one thing that saved this bullet was the last
  sentence, which was and remains true: **no novelty claim in this document rests
  on a corpus miss.**

## 7. Recommended order of work for d17

1. Run `analysis/r9_prior_code_compare.py` over the new driver before trusting any
   force number out of it. It exits 1 on a FLAG. UNDECIDED is not a pass.
2. Put the `reset -> step -> read` bracket in one helper that owns the dt, on
   Chrono's pattern, rather than spelling it at each call site.
3. If the torque matters, confirm the SDF `center` is the COM, or apply the
   `(center - COM) x F` correction.
4. Run the 2c control once. It is two runs, one parameter apart, and it either
   retires the one-sidedness question or turns it into the main finding.
5. Do not plan on validating the in/outflow BC against Anura3D. It is not there.

---

# ADDENDUM, 2026-08-19 evening: wall treatment, and two corrections

Commissioned as "Schulz and Sutmann 2019, image-particle boundaries", on the
premise that grid-momentum-zeroing walls smear stress into the object and that
this is the candidate mechanism behind the seven P-2 gate failures. Both halves
of that premise turned out to need correcting before the question could be
answered. Same tagging as above: **[read]**, **[recv]**, **[inf]**.

## 8. Correction 1: the method is already implemented, run, and refuted

`simulation/image_particles.py` is **tracked**, 237 lines, committed `8bab808`
(2026-08-18 04:08), wired into `sim_channel.py` and `sim_overfall.py`. It cites
Schulz and Sutmann 2019 and carries the exact "distorts the stress multiple grid
lengths into the object" quote. Results are on disk at
`data/openchannel_2026-08-18/image_particles_scan.json`. **[read]**

Its own verdict field: **"REFUTED. Floor penetration worsens monotonically with
image count."** Floor clamps go 664372 (0 images), 650615 (500), 713498 (2000),
877972 (6000); `images_12000` crashed on a grid-edge guard three times. Its stated
mechanism is that images cannot carry their source's `J` because `F` has no
setter, so they act as a spurious pressure source, **and that was predicted in the
module docstring before the runs were made.** Its scope line is already correct
and should be preserved: it refutes *that host-side mirror implementation*, not
Schulz and Sutmann, whose method assumes the image carries the source stress state.

**Why the audit missed it, and why the audit was not wrong.** `8bab808` predates
the eight branches audited, so restricting the search to files each branch
*changed* correctly excludes it. The measurement was sound. The conclusion drawn
from it, "the ranked list is entirely untouched and you would be first", does not
follow, because "not touched last night" was reported as "untouched". That is the
same shape as citing a total without its scope.

## 9. Correction 2: P-2 is an axis-aligned bounding-box test, and its zero-penetration floor is 7.88 to 10.02 percent against a 10 percent gate

**READ THIS BEFORE THE TABLE, BECAUSE THE NUMBER IS EASY TO READ BACKWARDS.**
A floor of 7.88 to 10.02 percent against a gate of 10 percent does **not** mean
the runs comfortably satisfy P-2. It means **the gate sits inside the band the
metric occupies when there is provably zero penetration.** The seven runs
CLAUDE.md item 7 records as P-2 failures are therefore not established as
measuring a defect; on this evidence they are largely measuring the achievable
floor of an axis-aligned bounding-box test on a hull that fills a third of its own
box. `sweepD_g64_d0p25` settles it: it reads **10.02 percent at frame zero with
zero water in any hull voxel**, i.e. it is already over the gate before any physics
has happened, and it is recorded as *passing* at 9.682 only because water drains
out later. A metric that can start above its own gate at zero penetration, and
pass by draining, is not measuring what the gate name says.

**What this does and does not license.** It does not show the seven runs have no
penetration; frame-0 share of each run's recorded max is 55.1 to 89.2 percent, so
there is real dynamics in the remainder, and for `g48_m1100` the whole failure is
1.08 points of it. It does show that **P-2 cannot be quoted as a penetration
fraction**, that the 10 percent limit is not a meaningful threshold against this
estimator, and that any published statement resting on "7 of 17 runs fail P-2"
needs the floor quoted alongside it or it misleads. The fix is to score the metric
against the **hull voxels** the same file already computes at `:186-196`, not
against the bounding box.

`renders/yaris_render_s1/sim_standing.py:463-465`: **[read]**

```python
lo_v, hi_v = veh.min(0), veh.max(0)
inbox = ((w >= lo_v) & (w <= hi_v)).all(axis=1)
frac_max = max(frac_max, float(inbox.mean()))
```

That is the vehicle's **axis-aligned bounding box**, not the hull. The same file
uses a proper **voxel-occupancy** test at `:186-196` to carve water out of the
hull at load time, so the water P-2 counts is water the initialiser deliberately
leaves in the empty parts of the box: under the floorpan, around the wheels,
beside the roofline taper.

**Measured, all 17 canonical runs.** I reconstructed frame 0 from each run's
recorded `lim`, `h`, `dx`, `floor`, `depth` plus `veh_particles_scene0`, applied
the file's own carve, then applied the file's own P-2 expression. At frame 0, with
**exactly zero water in hull voxels by construction**:

| quantity | value |
|---|---|
| P-2 at frame 0, across all 17 runs | **7.88 to 10.02 percent** |
| water in hull voxels at frame 0 | **0** |
| hull volume / AABB volume | 32.7 to 37.0 percent |
| gate limit | 10 percent |

For the seven failures, frame 0 already accounts for **55.1 to 89.2 percent** of
each run's own recorded maximum. `g48_m1100` fails at 10.053 percent with 8.971
present at frame 0, so its entire failure is 1.08 points of dynamics.
`sweepD_g64_d0p25` reads **10.02 percent at frame zero, above the gate**, and is
recorded as passing at 9.682 only because water drains as the run proceeds.
Several passing runs have a frame-0 value *above* their own recorded max, so the
metric is not monotone in penetration at all.

**Two independent corroborations that the reconstruction is faithful**, neither of
which was an input to it: hull/AABB comes out 32.7 to 37.0 percent against
CLAUDE.md item 4(b)'s 33.2 percent, and the seven runs my table marks FAIL are
exactly the seven CLAUDE.md item 7 names. **[read]**

This also explains the image-particle scan: `passthrough_max_frac` is
**bit-identical at 0.0833005975148345** for 0, 500 and 2000 images, because the
metric is dominated by a structural term no wall treatment can move. **[inf]**

**Caveats, stated rather than buried.** The reconstruction omits the seeded
jitter, so particle counts are off 0.3 percent at g64 and 2.6 percent at g48.
Frame 0 uses the `scene0` pose while the recorded max is over 90 frames of a
moving vehicle, so "frame-0 share of max" is a decomposition indicator, not an
exact partition. The per-frame water field is **not** in `rollout.npz` for these
runs, so I could not recompute the metric frame by frame; that also contradicts a
note in my own memory, which is wrong and should be corrected.

Reproduce with (no GPU, needs only numpy):

```python
import numpy as np, json
R='renders/yaris_render_s1/g64_m1100/'
d=np.load(R+'rollout.npz'); s=json.load(open(R+'summary.json'))
lim,h,dx=float(d['lim']),float(d['h']),float(d['dx'])
floor,depth=float(d['floor']),float(d['depth'])
truck=np.asarray(d['veh_particles_scene0'],dtype=np.float64)
wall=4.0*dx
xs=np.arange(wall+0.5*h,lim-wall-0.5*h,h); ys=xs
zs=np.arange(floor+0.5*h,floor+depth,h)
water=np.stack(np.meshgrid(xs,ys,zs,indexing='ij'),-1).reshape(-1,3)
vk=np.floor(truck/h).astype(np.int64); wk=np.floor(water/h).astype(np.int64)
base=vk.min(0); span=(vk.max(0)-base+1)
vlin=np.ravel_multi_index((vk-base).T,span)
ins=np.all((wk>=base)&(wk<=vk.max(0)),axis=1)
wl=np.full(len(water),-1,dtype=np.int64)
wl[ins]=np.ravel_multi_index((wk[ins]-base).T,span)
w=water[~(np.isin(wl,np.unique(vlin))&ins)]          # the file's own carve
lo,hi=truck.min(0),truck.max(0)
print(((w>=lo)&(w<=hi)).all(axis=1).mean(), s['passthrough_max_frac'])
```

**What this does NOT say.** It does not say there is no passthrough. It says P-2
cannot measure it, because its zero-penetration floor sits at the gate. The
residual dynamic term for `g64_m1100` is about 1.9 points. A hull-occupancy
metric already exists in the same file and would answer the question directly.
Recommending it, not applying it: `sim_standing.py` is outside my write scope and
changing a published gate's definition is a decision, not a fix.

## 10. So how DO the three codes treat a wall

The original question, now answerable. **[read]**

| | wall mechanism | pressure support at the wall? | region affected |
|---|---|---|---|
| **ours** (warpmpm) | grid-velocity projection. `add_plane` (`mpm_solver_warp.py:1950-1990`) removes the normal component and applies friction on nodes behind the plane; `add_bounding_box` (`:2287`) is a literal `Dirichlet_collider` zeroing outward normal velocity in a hard-coded `padding = 3` cell band | **no** | half-space behind the plane; 3-cell band at each domain face |
| **Anura3D** | zero prescribed displacement on nodal DOFs, `MeshInfo.FOR:415-559`, with separate `NodalPrescibedDisp`, `...Water`, `...Gas` arrays per phase | **no** | conforming mesh boundary nodes |
| **Chrono::FSI** | BCE boundary markers whose velocity **and pressure** are modified per **Adami**, `SphBceManager.cu:61`; exposed as `enum class BoundaryMethod { ADAMI, HOLMES }` with **ADAMI the default** (`ChFsiDefinitionsSPH.h:65`, `ChFsiFluidSystemSPH.cpp:103`) | **yes** | boundary marker layers |

**Of the three, only Chrono has pressure support at the wall.** Ours and Anura3D
both impose kinematic constraints with no pressure support, which is exactly the
class Schulz and Sutmann criticise. Chrono treats boundary method as a first-class
switchable option with two literature-named choices; our `surface` parameter
offers `sticky`, `slip` and `separable`, all three of which are kinematic.

**How far the wall actually reaches into our water, computed rather than
asserted.** The transfer is a quadratic B-spline, 3x3x3 stencil, support radius
1.5 dx (`mpm_utils.py:1383-1398`, base node `floor(x/dx - 0.5)`). For `g64_m1100`
the floor sits at `3.00 dx` and water occupies four layers at 3.25, 3.75, 4.25 and
4.75 dx: **[read + computed]**

| layer | z (dx) | stencil nodes | touches a floor-modified node (index < 3)? |
|---|---|---|---|
| 0 | 3.250 | 2, 3, 4 | **yes, node 2** |
| 1 | 3.750 | 3, 4, 5 | no |
| 2 | 4.250 | 3, 4, 5 | no |
| 3 | 4.750 | 4, 5, 6 | no |

So **one of four water layers, 25 percent of the column, has stencil support on a
boundary-modified node.** The side walls are clear: water is inset `4 dx`, its
first stencil is nodes 3,4,5, and the Dirichlet band is nodes 0,1,2, so there is
no overlap. The `4 dx` inset and the `floor = 3 dx` placement both look chosen to
clear the 3-cell band, and the floor placement puts the plane exactly at the top
of it.

## 11. Why the image-particle attempt was doomed in this engine, mechanism-level

This is the part worth keeping, and it is stronger than the scan's own conclusion.

The scan says images act as a spurious pressure source because they cannot carry
their source's `J`. True. But the production remedy in Chrono **does not mirror
particles at all**: Adami's method keeps boundary markers fixed and **extrapolates
pressure onto them** from the adjacent fluid. It needs a writable pressure field
on the boundary particles.

In this warpmpm build, a fluid particle's pressure is a function of `J` alone
(`kirchoff_stress_newtonian`, `mpm_utils.py:28`, exponent 1.1), `J` comes from `F`,
and **`F` has no setter**: `Solver` exposes `F()` at `:543` and `F_torch()` at
`:625` and nothing that writes it. **[read]** So the one thing Adami's method
requires is the one thing this engine does not expose.

That reframes the remedy. It is **not** "write a better mirror". A better mirror
still cannot set the image's pressure. It is "expose a way to set particle
pressure state", which is an engine change, not a host-side one. Anyone tempted to
retry image particles in this build should read that as the blocking constraint
and cost the engine change first. **[inf, from three [read] facts]**

## 12. What I did not do

- I did **not** modify `sim_standing.py`, `gates.py`, `image_particles.py` or any
  data file, and did not rerun any simulation. Section 9 is measurement of
  existing artifacts only.
- The physics-skeptic subagent failed with a model-access API error earlier in
  this session and I did not retry it here, so **nothing in this addendum had
  independent adversarial review**. The claim most worth attacking is section 9's
  reconstruction, and the cheapest attack is to add the seeded jitter and confirm
  the frame-0 fraction does not move materially. Two things already argue it will
  not: the reconstruction independently reproduces CLAUDE.md item 4(b)'s hull/AABB
  ratio to within 0.1 points, and it independently reproduces item 7's exact list
  of seven failing runs. Neither was an input.
- Anura3D's absorbing boundary (`MPMDynViscousBoundary.FOR`) is not characterised
  here; I established only that its ordinary walls are prescribed-displacement.

---

# ADDENDUM 2, 2026-08-19 18:1x: THE CROSS-CODE NUMBER EXISTS NOW

The unit was commissioned as "build Chrono::FSI-SPH on Vista aarch64 and run one
comparison case". **The build did not need doing and the comparison case ran.**
Everything below is measured on Vista job `922255`, node `c642-091`, GH200 120GB.

## 13. Two corrections to the dispatch, both found before spending node time

**13a. An aarch64 Chrono::FSI build already exists on Vista.** The dispatch said
"Only an `ls6/chrono_x86_build` exists on disk, which is x86 for a different
machine, so an aarch64 build is genuinely new." That is false. **[read]**

```
/scratch/11603/jcerrell0629/chrono_eval_2026-08-14/     6.9 GB, 2026-08-14
  build_fsi/lib/libChrono_fsisph.so                     built
  build_fsi/bin/demo_FSI-SPH_*                          15 FSI-SPH demos
  chrono/  at 1b90a9f9854575f1ce1287d359d957b0273c075f  2026-08-13, clean tree
```

Had I followed the dispatch I would have spent the whole window rebuilding
something that was already there. **Check `$SCRATCH` before believing any
"nothing exists" claim about TACC**; the earlier session's work was on `$SCRATCH`,
and the inventory that produced the dispatch line evidently looked elsewhere.

**13b. The toolchain versions in project memory are close but not right.**
Measured live: Vista's default `nvcc` is **CUDA 12.5** (`nvidia/24.7`), and the
module that the prior build actually used is **`cuda/12.6` with `gcc/13.2.0`**,
named at `chrono_gh200_fsi_build.sbatch:53-54`. **[read]** Available gcc modules
are 13.2.0, 14.2.0, 15.1.0.

**A gotcha not in project memory at all, and it costs a run to discover: the
built binaries are not self-contained.** Running any demo without reloading the
build toolchain fails at load time, not at runtime:

```
/lib64/libstdc++.so.6: version `GLIBCXX_3.4.32' not found
  (required by .../libChrono_fsisph.so)
```

`module load gcc/13.2.0 cuda/12.6` before execution fixes it. Anyone re-using
this build needs that line.

## 14. What I ran, and the two failures before it worked

`tow_drag.cpp`, 153 lines, compiled against the existing libraries directly with
`g++` rather than through CMake (faster, and it proves the install is usable as a
library). A box is held at mid-depth in a closed water tank, settled, then towed
horizontally at constant speed; `GetFsiBodyForce` is read every meta-step.

```
domain 1.6 x 0.6 x 0.5 m,  box 0.20 x 0.16 x 0.16 m,  rho 1000, mu 1e-3
spacing 0.030 m, RK2, ADAMI BCE, artificial-unilateral viscosity, dt 1e-4 fixed
settle 0.25 s with the body held, then tow 0.6 m
```

**Two failed attempts, recorded because the failure modes are the transferable
part.** Both aborted at `SphCollisionSystem.cu:354 from calcHashD`, "position is
NaN", on the very first step.

1. **No hydrostatic initialisation.** The fluid column starts at p = 0 everywhere
   and collapses under gravity. Fix:
   `RegisterParticlePropertiesCallback(DepthPressurePropertiesCallback(fsize.z()))`.
   `demo_FSI-SPH_ObjectDrop` does this and I had dropped it.
2. **The `ChLinkMotorLinearSpeed` constraint.** This was the real one. The NaN
   particle indices were ~129,000 to 130,700, which are the **body's BCE markers**,
   not fluid particles, so the body pose went NaN first and poisoned its own
   markers. Replaced by prescribing pose and velocity directly on a `SetFixed(true)`
   body each step. That is also **closer to what our driver does**, not further
   from it, so the comparison improved.

**Diagnostic worth keeping:** when a Chrono FSI run NaNs, check whether the
reported particle indices are above the fluid count. If they are, the rigid body
is the cause and the fluid is a victim.

## 15. THE NO-FORCING CONTROL PASSES, WHICH IS WHAT LICENSES EVERYTHING ELSE

Run first, deliberately, before any number that could be flattering. **[read]**

| run | mean Fx over window | sd Fx |
|---|---|---|
| **U = 0, body held still** | **-0.196 N** | 2.088 N |
| settle window of every run | +0.189 N | (identical across runs, same seedless init) |

Fx is consistent with zero at zero forcing. The accessor is not returning
garbage and the setup has no spurious horizontal driving.

## 16. Drag at three tow speeds, and it does NOT scale as U squared

| U [m/s] | mean Fx [N] | sd Fx [N] | \|Fx\|/(½ρAU²) | tow duration [s] |
|---|---|---|---|---|
| 0.0 | -0.196 | 2.088 | control | 0.50 |
| 0.5 | -31.05 | 54.67 | 9.70 | 1.20 |
| 1.0 | -47.91 | 186.09 | 3.74 | 0.60 |
| 2.0 | -93.70 | 122.33 | 1.83 | 0.30 |

`A_ref = 0.0256 m²`. **The sign is correct**: the body is towed in +x and Fx is
negative, so the fluid opposes the motion. The magnitudes are the right order for
a bluff body of this size.

**Three things must be said with these numbers or they will be misread.**

1. **The scatter exceeds the mean at every non-zero speed.** sd/|mean| is 1.76,
   3.88 and 1.31. **Not one of these means is well determined**, and quoting any
   single one as "Chrono's drag" would be exactly the error this project keeps
   logging. What is well determined is the *sign* and the *order of magnitude*.
2. **The apparent sub-quadratic scaling is confounded and I am not claiming it.**
   4x the speed gives only 3.0x the force, which looks strongly sub-quadratic. But
   tow duration was set to `travel/U`, so the U = 2.0 run is 0.30 s against 1.20 s
   at U = 0.5, and each run starts impulsively from rest. The fast run's averaging
   window sits inside its startup transient while the slow run's does not. **The
   scaling test is not valid as run**; the fix is equal tow durations at equal
   travel-normalised windows, which is one parameter change and a rerun.
3. Closed tank, so blockage and wall proximity are present and uncorrected. These
   are apparent coefficients, not free-stream ones.

**This independently reproduces our own project's central measurement problem in a
different code.** Short records, scatter comparable to signal, and a mean whose
value depends on the window chosen. Compare the settle-length finding in CLAUDE.md
(25 of 25 runs need more than 8 frames discarded, N_eff 2.9 to 11.0). That is a
property of measuring a transient force on a body in particle-based fluid, **not a
warpmpm defect**, and the paper's limitations section can now say so citing a
second implementation.

## 17. THE ONE NUMBER WITH AN ANALYTIC ANSWER, AND CHRONO MISSES IT BY 48 PERCENT

During the settle window the body is stationary and fully submerged, so the
vertical force has a closed form: `F_z = ρ g V`.

| quantity | value |
|---|---|
| mean Fz over settle window (125 samples) | **74.355 N** (sd 10.778) |
| analytic ρgV, V = 0.20·0.16·0.16 = 0.005120 m³ | **50.227 N** |
| ratio | **1.4804** |
| error | **+48.04 percent** |

**I proposed a mechanism, tested it in the same session, and it is REFUTED.**
The hypothesis was BCE cladding: at spacing 0.030 m the box is only 5.3 spacings
across its short dimension, so the effective hydrodynamic volume exceeds the
nominal one. Inflating the box by half a spacing per face predicts 81.5 N (1.62x),
by a quarter spacing 64.6 N (1.29x), and the measured 74.4 N sits between them.
That hypothesis makes a hard prediction: **the error must fall as spacing falls,
and must fall toward 1.000.** I ran the refinement. It does the opposite.

| spacing [m] | box widths per spacing | mean Fz [N] | sd [N] | ratio to ρgV | error |
|---|---|---|---|---|---|
| 0.030 | 5.3 | 74.355 | 10.778 | 1.4804 | **+48.04 %** |
| 0.020 | 8.0 | 79.292 | 13.708 | 1.5787 | **+57.87 %** |
| 0.015 | 10.7 | run aborted | | | |
| 0.010 | 16.0 | run aborted | | | |

**The error grows by 9.8 points under a 1.5x refinement, and the scatter grows
with it.** The cladding explanation is dead as stated, and I am not substituting a
new one I have not tested.

**What I can and cannot conclude from two points.** I can say the error does not
decrease under this refinement step, which is enough to refute the hypothesis. I
**cannot** distinguish monotone divergence from non-monotone behaviour with two
points, and I will not call it either. The comparison is also confounded: `dt` was
held at 1e-4 while spacing fell, so the CFL margin shrank across the pair, and the
two finer runs died of it. Both aborted at `SphFluidDynamics.cu:712`, "A particle
density is NaN", a *different* failure from the earlier `calcHashD` one and the
signature of a CFL violation. A clean refinement study must scale `dt` with
spacing; that is the next run, and it is cheap.

**Why the negative is worth more than the positive would have been.** CLAUDE.md
item 5 records that our own g48/g64/g96 ladder is **non-monotone and unconverged**,
with `final_disp_mag_m` moving +87.8 percent then -59.2 percent for 1100 kg, and
instructs that the verdict may be cited but never the displacement magnitude.
L-5 cites Steffen, Kirby and Berzins 2008 as the mechanism for MPM losing
convergence under refinement at fixed particles-per-cell. **An independent SPH code
on the same hardware also fails to converge a body force under refinement.** That
is corroboration from a separate origin, which is the standard this project holds
itself to, and it argues the behaviour is generic to particle methods rather than
a warpmpm defect. It is two points against our three and is confounded by fixed
`dt`, so it is support, not proof.

**Why this matters more than the drag numbers.** Our project's own SDF-collider
buoyancy validation is **7.3 to 7.7 percent** (CLAUDE.md A-2, and note that the
"1.6 to 7.7" range is a conflation that item explicitly forbids). A widely used,
independently developed code gets **+48 percent** on the same quantity at coarse
resolution. Two consequences:

- **Our 7.3 to 7.7 percent is not bad.** It is far better than an established
  code at the resolution we could afford, and the comparison is now on record.
- **Force error on a submerged body is large in an established code too**, and
  refining did not fix it. CLAUDE.md L-3 records that the g64 baseline has 4
  particle layers and exactly 2.000 cells per flow depth. **This is independent
  support for L-3's "state this as a limitation, not a converged resolution"**,
  from outside our own code and on our own hardware.
- **It does NOT support L-4.** L-4 says coarse resolution usually over-predicts
  peak hydrodynamic force, so over-threshold NO-FORD verdicts are conservative.
  Here the *finer* run over-predicted more. One shape, one quantity (buoyancy, not
  drag), two points, fixed `dt`: this does not refute L-4, but it is the first
  measurement in this project that points the other way, and L-4 should not be
  cited as though nothing has ever cut against it.

Do not overstate it either: Chrono's error here is measured on **one shape at one
resolution with one BCE setting**, with no attempt to use its own recommended
resolution. It is evidence that the effect is generic, not evidence that Chrono is
inaccurate.

## 18. The vehicle-fording case is ONE BUILD TARGET AWAY, and I did not run it

A 105-paper deep search names Chrono::FSI vehicle-fording models [Paz14, Paz16,
Was15] as the closest published analogue to this project. I checked the tree I
already had, on the machine. **[read]**

- There is **no** demo named for fording, wading or amphibious operation anywhere
  in `src/demos`. The capability is not a dedicated fording case.
- The closest thing is **`src/demos/vehicle/cosimulation/demo_VEH_Cosim_WheeledVehicle_SPH.cpp`**:
  a full wheeled vehicle co-simulated against SPH terrain. That is the Pazouki
  and Wasfy lineage.
- It is **not built**. The only cosim binaries present are `demo_COSIM_data_exchange`,
  `demo_COSIM_hydraulics` and `demo_COSIM_socket`.

**But every precondition for building it is already satisfied**, which is why this
is a recommendation and not a lament:

| precondition | state |
|---|---|
| `CH_ENABLE_MODULE_VEHICLE:BOOL` | `ON` |
| `CH_ENABLE_MODULE_VEHICLE_COSIM:BOOL` | `ON` |
| `libChrono_vehicle_cosim.so` | built, 2026-08-14 |
| MPI | `/opt/apps/nvidia24/openmpi/5.0.5/bin/mpicxx` present |

So the highest-value next GPU unit is **build that one target and run it**, not
another generic demo and not a rebuild from scratch. It is the only route in this
survey that puts a *vehicle* rather than a *box* in front of an independent
solver, and the vehicle side (suspension, wheels, tire/ground contact) is exactly
what our single-rigid-body abstraction throws away.

**I did not attempt it.** The window went on getting a force number out of a
simpler case that I could fully control, and I would make the same call again: an
uncontrolled vehicle number would have been worth less than a controlled box
number with a passing no-forcing control. Recording the readiness so the next
session does not re-derive it.

## 19. Review status of this addendum: UNREVIEWED, and I tried twice

The `physics-skeptic` subagent was invoked **twice** in this session and failed
**both** times with the identical error: `There's an issue with the selected model
(deepseek-ai/DeepSeek-V4-Flash:deepinfra)`. A second attempt through a different
agent type with an explicit model override failed the same way, so this is an
environment fault, not a prompt fault.

**Nothing in sections 13 to 18 has had independent adversarial review.** I am
saying so rather than implying it happened. The claims I most want attacked, in
order:

1. **Is `rho*g*V` the right analytic target at all?** The body is submerged in a
   0.5 m column, spanning z = 0.17 to 0.33, so clearances are 0.17 m to the free
   surface and 0.17 m to the floor, both about 5.7 spacings at 0.030 m. If that is
   too close, part of the +48 percent is wall and free-surface proximity rather
   than a force-extraction error, and the headline weakens.
2. **Is 0.25 s a settled state?** With `max_velocity = 5.0` and Tait, the
   artificial sound speed is order 50 m/s, so a 1.6 m tank sees roughly 8 acoustic
   transits in the settle window. That is probably enough acoustically, but the
   gravity-wave timescale is much slower and I did not check it. sd is 14.5 percent
   of the mean, which is not the signature of a fully settled record.
3. **Are the drag means distinguishable from zero?** With sd exceeding the mean and
   serially correlated samples, the effective sample size is far below the row
   count, exactly as `stationarity.py` shows for our own runs. I did not compute
   `N_eff` here. Until someone does, treat the drag table as sign-and-order only.

**One claim I verified myself instead, since it was the highest-risk one.** Does
`GetFsiBodyForce` include the body's own weight? If it did, the buoyancy
comparison would be meaningless. It does not: `ChFsiInterface.cpp:94-96` returns
`m_fsi_bodies[i]->fsi_force`, a member initialised to `VNULL` at `:115` and
populated by a **dedicated FSI force accumulator** created at
`AddFsiBody`, `fsi_body->fsi_accumulator = fsi_body->body->AddAccumulator()`.
It is the fluid load alone, and the measured value being positive while body
weight is 100.45 N confirms it independently. **[read]** This also re-confirms on
this rev what section 2 established on another: **no `dt` appears anywhere in the
accessor path.**

---

# ADDENDUM 3: sdfibm OVERTURNS MY OWN HEADLINE, AND TWO SELF-CORRECTIONS

## 20. THE dt IS NOT IDIOSYNCRATIC. IT IS WHAT THE FORMULATION IMPLIES.

My section 2 headline, repeated on the board and carried to d17 twice, was: **ours
is the only one of three implementations that accumulates body force over time and
therefore the only one needing a caller-supplied `dt`.** A fourth code refutes it.

`sdfibm` [Zha20o], signed-distance immersed boundaries in OpenFOAM, GPL-3,
`github.com/ChenguangZhang/sdfibm` at `3627269` (2025-06-22). Read locally, not
cited from the search. **[read]** `src/solidcloud.cpp:411-451`:

```cpp
vector us    = solid.evalPointVelocity(cc);
vector force = alpha * (uf - us);          // :412-413  velocity difference
...
scalar dtINV = 1.0 / dt;                   // :425
force += f_ * cv[cellid] * dtINV;          // :441  * cell volume / dt
...
force *= m_rhof;                           // :450
```

So `F = rho_f * SUM_cells [ alpha * (u_f - u_s) * V_cell ] / dt`. Units check:
`[kg/m^3][m/s][m^3]/[s] = N`. That is **a momentum difference divided by a
timestep**, which is architecturally *our* pattern, not Anura3D's and not
Chrono's. And `dt` is **caller-supplied**, the same exposure our accessor has:
`SolidCloud::interact(scalar time, scalar dt)` at `:462` passes it straight to
`solidFluidInteract(solid, dt)`.

**Corrected architecture table, four codes, three philosophies:**

| code | force is obtained by | needs a `dt`? |
|---|---|---|
| Anura3D | nodal traction from particle stress, over nodal lumped mass | no |
| Chrono::FSI-SPH | surface integral over BCE markers | no |
| **sdfibm** | **direct-forcing IB: momentum difference / dt** | **yes** |
| **ours (warpmpm SDF collider)** | **accumulated momentum / dt** | **yes** |

**The two that need a `dt` are the two immersed-boundary/SDF formulations.** The
`dt` is not sloppiness and it is not ours alone: it is what direct forcing means.
This should *reassure* rather than alarm, and my earlier framing overstated our
isolation. [Bha19] IBAMR's "force constraints rather than surface-stress
integration" is the same family again, which I have not read and am not claiming.

**But the sharper finding survives, and it is now better targeted.** What is
idiosyncratic is **not** that we need a `dt`. It is **where we expose it.**
sdfibm zeroes its accumulators at `:465-467`, at the top of `interact()`,
*immediately* before the loop that consumes them, and overwrites the per-solid
force through `setFluidForceAndTorque` rather than accumulating across steps.
Chrono zero-fills on the line before the kernel launch. **Both codes that could
have the reset bug structure it away by putting the reset adjacent to the use.**
Ours does not: the reset and the `dt` live at call sites a caller can get wrong
independently. So the recommendation to d17 is unchanged and now rests on two
codes instead of one: **wrap reset, step and read in one helper that owns the
`dt`.** That is not a workaround, it is what both comparable implementations do.

## 21. sdfibm is GROUND-FIXED, so unclaimed ground item 1 survives contact

A live search of the whole `sdfibm` source for `MRF`, `movingMesh`, `moveMesh`,
`referenceFrame` and `frameVelocity` returns **zero hits**. **[read]** The mesh is
a stationary OpenFOAM Eulerian mesh and the solid is evaluated at fixed cell
centres, `solid.evalPointVelocity(cc)` where `cc = m_mesh.cellCentres()`.

So the single most comparable published implementation to our SDF collider does
**not** solve the frame problem d17 measured. It sidesteps it by never leaving the
ground-fixed frame. That is consistent with the search's own statement that
body-fixed formulations are established for Eulerian IB/level-set solvers but are
**not evident as a developed moving-reference formulation for MPM**, and it means
**item 1 is not closed by prior art in the nearest neighbour to our own method.**
I checked one codebase, not the field, so this narrows the gap rather than
proving it.

## 22. SELF-CORRECTION: the vehicle-fording case is NOT one build target away

Section 18 said `demo_VEH_Cosim_WheeledVehicle_SPH` was "one build target away"
because the cosim module was ON, the library existed and `mpicxx` was present. **I
then tried it and that was wrong.** **[read]**

```
make demo_VEH_Cosim_WheeledVehicle_SPH
make: *** No rule to make target 'demo_VEH_Cosim_WheeledVehicle_SPH'.  Stop.
```

`make help` knows only `Chrono_vehicle_cosim` plus the three socket-cosimulation
demos. The cache lists `BUILD_DEMOS_BASE / COSIMULATION / FEA / FSI / ROBOT` and
**no `BUILD_DEMOS_VEHICLE` at all**, because the real blocker is one line up:

```
CH_ENABLE_MODULE_VEHICLE_MODELS:BOOL=FALSE
```

Without the vehicle *models* library the vehicle demo directory is never added, so
the flag and the target never come into existence. The fix is a **CMake
re-configure** with `-DCH_ENABLE_MODULE_VEHICLE_MODELS=ON` followed by a rebuild,
not a `make` of an existing target. That is a materially bigger job than I implied
and it will not fit in a short window.

**Why I am recording the failed attempt rather than quietly fixing the sentence.**
The claim was checkable in one command and I published it without running that
command, in the same document where I criticise exactly that habit. The general
lesson is the one already in this project's rules: an inference from
preconditions ("the module is on, the lib exists, MPI is present") is not a
measurement of the outcome, and it took 40 seconds to find out.

---

# ADDENDUM 4: THE TAXONOMY, AND THE FLOOR TEST GENERALISED FOR d11-accessor

## 23. THREE FAMILIES OF FLUID-TO-RIGID FORCE EXTRACTION

Nobody in the 332-paper corpus lays this out, and it is more transferable than any
single pairwise comparison. Every code below was read at a named revision; none of
this is taken from a search summary. **[read]**

| family | what is summed | over what | needs a `dt`? | zeroing discipline |
|---|---|---|---|---|
| **A. Nodal traction from particle stress** | `n . sigma . n` from the particle stress tensor, divided by nodal lumped mass | body-adjacent **nodes** | **No.** Stress is a state variable; it exists at an instant | n/a, nothing accumulates |
| **B. Surface integral over markers** | pressure and viscous traction on boundary markers | body **surface** (BCE markers) | **No.** A surface integral of a state field | reset **adjacent to use**, zero-fill on the line before the kernel |
| **C. Momentum difference over a timestep** | `alpha * (u_f - u_s) * V_cell`, times `rho_f`, divided by `dt` | body-**overlapping cells or particles** | **Yes, structurally.** The quantity is an impulse; only `dt` converts it to a force | sdfibm resets at the top of `interact()`, immediately before the consuming loop |

Instances, with revisions:

- **A**: Anura3D, `MPMDynContact.FOR:443-512`.
- **B**: Chrono::FSI-SPH, upstream `1b90a9f`. `ChFsiInterface.cpp:94-96` returns a
  stored `fsi_force` fed by a dedicated accumulator created in `AddFsiBody`. No
  `dt` anywhere in the path, verified on two separate revisions.
- **C**: `sdfibm` at `3627269`, `solidcloud.cpp:412-450`. **And ours**, the warpmpm
  SDF collider.

**The load-bearing consequence, and it is the opposite of what I first said.**
Family C is not a defect and not an oddity. **It is a published formulation that a
signed-distance immersed-boundary method arrives at independently**, because
direct forcing computes the impulse needed to reconcile fluid and solid velocity,
and an impulse only becomes a force when divided by the interval it acted over.
Our SDF collider is in family C **because it is an SDF collider**, not because
anyone was careless. Anyone auditing our accessor should be told this before they
read the `dt` as a smell.

**What remains a real difference, narrowed to one sentence.** Both other family-C
and family-B implementations make the reset impossible to forget by placing it
immediately before the use; ours exposes reset and `dt` at call sites that can be
got wrong independently. That is an ergonomics gap, not a physics gap.

**Candidate family D, NOT verified.** [Bha19] IBAMR is described as using "force
constraints rather than surface-stress integration". If that means a Lagrange
multiplier enforcing the rigidity constraint, it is a genuinely fourth mechanism.
**I have not read IBAMR and am not claiming this.** It is the cheapest remaining
addition to this table.

## 24. THE FLOOR TEST, GENERALISED. FOR d11-accessor, ON JOB B CRITERION 3.

d11-accessor reports Job B failing at all 24 gradings and asks whether a FAIL can
be unfalsifiable. **My P-2 result is an instance of a general property, and the
general form is what d11 needs.** Stating it as a procedure rather than a result:

> **A pass/fail gate is only informative if the metric can actually reach the
> passing region under the null condition the gate names.**

P-2 is the worked example. The gate is "max water fraction inside the vehicle
bounding box <= 10 percent". The null condition is *zero penetration*. I
constructed frame 0 with **provably zero water in any hull voxel** and the metric
reads **7.88 to 10.02 percent** across the 17 runs. The passing region is
`[0, 10]`; the metric's floor at the null is `7.88` to `10.02`. **The floor
overlaps and in one run exceeds the gate.** `sweepD_g64_d0p25` reads 10.02 percent
at frame zero with zero penetration, and is recorded as *passing* at 9.682 only
because water drains out later.

**The three-step test d11 can run on criterion 3 tonight, without a GPU:**

1. **Name the null.** What state is the criterion claiming to detect the absence
   of? For P-2 it was penetration. For criterion 3 it is presumably a force-ratio
   discrepancy.
2. **Construct or identify a record that provably satisfies the null**, by
   construction rather than by trusting a run to be clean. Mine was frame 0 with
   the hull carve applied by the file's own code.
3. **Evaluate the criterion's own expression on that record.** If the value lands
   inside or above the failing region, **the criterion cannot distinguish a defect
   from its own floor, and a FAIL is uninformative rather than evidence.**

**Applied to what d11 already has.** Job B fails at all 24 gradings. If the
measured accessor's band has a nonzero floor at the null, then "FAIL at every
window" is exactly the signature of a floor, not of a robust defect: a real defect
would be expected to vary with window, and a floor would not. **d11 already has
the diagnostic evidence in hand** in the fact that the failure is window-invariant
at 0.15 sigma. That is suspicious in the same way a uniform pass is suspicious,
and this project already has the rule: a check must distinguish "equal" from
"could not evaluate".

**I am NOT claiming criterion 3 has a floor.** I have not read `sphere_heave.py`
and it is not in my scope. I am claiming the test above is cheap, is the same test
that produced the P-2 result, and that a window-invariant FAIL is the condition
under which it is most worth running.

## 25. WHY NOBODY CAN SEE ANY OF THIS, WHICH IS ITS OWN FINDING

The P-2 write-up has now been requested four times while being complete since
`a863ee7`. The cause is not the write-up. **[read]**

```
ls /Users/josie/can-it-ford/docs/R9_MOVING_VEHICLE_PRIOR_CODE_2026-08-19.md
  -> No such file or directory
git cat-file -e main:docs/R9_MOVING_VEHICLE_PRIOR_CODE_2026-08-19.md      -> ABSENT
git cat-file -e origin/main:docs/R9_MOVING_VEHICLE_PRIOR_CODE_2026-08-19.md -> ABSENT
git cat-file -e claude/r9-priorcode:docs/...                              -> PRESENT
```

The main checkout is on **`claude/add-ci-checks`**, not `main`, and this document
exists on exactly one branch, unpushed. **Anyone reading `/Users/josie/can-it-ford/docs/`
sees nothing, and correctly reports the work as missing.** This is not specific to
me: every slot's deliverable is invisible to every other slot and to the
coordinator unless the reader names the branch. Reach it with

```
git -C /Users/josie/can-it-ford show claude/r9-priorcode:docs/R9_MOVING_VEHICLE_PRIOR_CODE_2026-08-19.md
```

**The general lesson for the round:** "I cannot see your write-up" and "your
write-up does not exist" are indistinguishable from a checkout on another branch,
and the board rows carrying SHAs are the only thing that currently bridges the
gap. A reader who checks a path instead of a SHA will keep concluding the work was
never done.

---

# ADDENDUM 5: THE dt CONFOUND IS MEASURED AND ELIMINATED. THE DIVERGENCE IS REAL.

## 26. I named the weakness in my own claim, ran the control, and the claim survived

Addendum 2 reported buoyancy error growing under refinement, +48.04 percent at
spacing 0.030 to +57.87 at 0.020, and I refused to call it divergence because of a
confound **I flagged myself**: `dt` was held at 1e-4 while spacing fell, so the CFL
margin shrank across the pair, and the two finest runs died of exactly that. The
obvious alternative explanation was that the "refinement" was measuring the
shrinking CFL margin rather than the spacing.

**Control: rerun spacing 0.020 with `dt` scaled linearly with spacing**
(1e-4 x 0.020/0.030 = 6.667e-5), everything else identical. **[read]**

| run | spacing | `dt` | n | mean Fz [N] | sd | ratio to rho g V | error |
|---|---|---|---|---|---|---|---|
| baseline | 0.030 | 1.000e-4 | 125 | 74.355 | 10.778 | 1.4804 | **+48.04 %** |
| dt FIXED | 0.020 | 1.000e-4 | 125 | 79.292 | 13.708 | 1.5787 | **+57.87 %** |
| **dt SCALED** | **0.020** | **6.667e-5** | **188** | **79.332** | **13.681** | **1.5795** | **+57.95 %** |

**The two 0.020 runs agree to 0.08 percentage points**, 0.04 N out of 79 N, despite
a 1.5x change in `dt` and a 1.5x change in sample count. **The `dt` confound is not
the explanation and I am retiring that caveat rather than carrying it.** The error
growth is a property of the spatial refinement.

**The cladding hypothesis is refuted quantitatively, not just directionally.**
Backing out the effective displaced volume `V_eff = Fz/(rho g)` and solving
`(0.20+d)(0.16+d)^2 = V_eff` for the implied linear inflation `d`:

| spacing | `V_eff` [m³] | implied `d` [m] | `d` in units of spacing |
|---|---|---|---|
| 0.030 | 0.007580 | ~0.024 | **0.80** |
| 0.020 | 0.008087 | ~0.028 | **1.40** |

Cladding predicts `d` proportional to spacing, so `d` should have fallen from
0.024 to about 0.016 m and stayed near constant in spacing units. **Instead `d`
grew in absolute terms and nearly doubled in spacing units.** That is the opposite
of the prediction on both measures.

**What I still will not claim.** Two spatial points cannot distinguish monotone
divergence from non-monotone behaviour, and CLAUDE.md item 5 records our own
g48/g64/g96 ladder as non-monotone, so non-monotonicity is the live alternative
and I have no right to exclude it. Batch job **922515** runs the four-point ladder
(0.030, 0.020, 0.015, 0.010, each with `dt` scaled) and will settle it. **It was
submitted as sbatch precisely so the answer survives the interactive window**, per
the standing finding that this project burns 98.5 to 99.1 percent of node-hours on
interactive idev with 95 of 184 runs ending in TIMEOUT.

**Why this matters beyond one code.** A no-forcing control passing, a hypothesis
stated with its own falsifier, the falsifier run, and the hypothesis dying is the
full loop this project keeps asking for. The surviving claim is now: **an
established, independently developed SPH code does not converge the buoyant force
on a bluff body under spatial refinement, and this is not an artifact of the
timestep.** Set beside our own SDF-collider buoyancy validation of 7.3 to 7.7
percent, our number looks good, and CLAUDE.md L-3's instruction to state
resolution as a limitation rather than a converged result now has support from
outside our own code.

---

# ADDENDUM 6: THE TAXONOMY, SETTLED. IBAMR PROVES IT INSIDE ONE CODEBASE.

## 27. The final table, and the single best piece of evidence in it

My section 23 table was assembled across four codebases, which always leaves the
objection that the difference tracks the project, the language or the solver
family rather than the formulation. **IBAMR removes that objection by implementing
both behaviours itself.**

| family | force is obtained by | needs `dt`? | instances |
|---|---|---|---|
| **A** | nodal traction from particle stress, over nodal lumped mass | **no** | Anura3D `MPMDynContact.FOR:443-512` |
| **B** | surface integral over markers / immersed boundary | **no** | Chrono::FSI-SPH BCE (`ChFsiInterface.cpp:94-96`, rev `1b90a9f`); **IBAMR FD/BP** |
| **C** | momentum difference over a timestep | **yes, structurally** | **ours** (warpmpm SDF collider); sdfibm `3627269` (`solidcloud.cpp:412-450`); **IBAMR FD/IB** |

**IBAMR spans B and C in one codebase**: its FD/BP force is a surface integral with
`dt` **absent**, and its FD/IB force is a momentum difference that **divides by
`dt`**. Same authors, same library, same language, same solver: the only thing that
changes is the formulation, and the `dt` appears exactly when the formulation makes
the quantity an impulse. **[recv]**

**That is the whole argument, and it is now demonstrated rather than inferred:**

> The `dt` is not a property of a project, a language or a solver family. It is a
> property of the formulation. A surface integral of a state field needs no `dt`.
> A momentum difference accumulated over a step needs one, because an impulse only
> becomes a force when divided by the interval it acted over.

**Consequence for our accessor, stated so an auditor cannot misread it.** Our SDF
collider is in family C **because it is an SDF collider**. The `dt` in
`sdf_wrench` is required by the method, not evidence of a defect, and the same
line appears in two independent published implementations. My original framing,
carried on the board and to d17 twice, said ours was the only one of three needing
a caller `dt`; that was wrong and this table replaces it.

**What remains a genuine gap, and it is ergonomics not physics.** Chrono zero-fills
on the line before the kernel launch; sdfibm resets at the top of `interact()`
immediately before the consuming loop. Both make the reset impossible to forget by
placing it adjacent to the use. Ours exposes reset and `dt` at call sites that can
be got wrong independently. **The fix is unchanged and now rests on three
implementations: wrap reset, step and read in one helper that owns the `dt`.**

**PROVENANCE, STATED PLAINLY.** Families A, B (Chrono) and C (sdfibm, ours) I read
myself at named revisions. **The IBAMR row I did NOT read.** It is
`[recv]` from a sibling session's read of the primary paper, cited to Eq. 30
(s4.2.3) and Eq. 40 (s4.2.4). It is the strongest single entry in the table and it
is the one entry I cannot vouch for at first hand. IBAMR is open source, so
confirming it against `github.com/IBAMR/IBAMR` is cheap and is the first thing to
do before this table goes in a paper.

## 28. Three corrections carried in from other sessions

**28a. `[Roe23]` FloatStepper has NO heave-decay case.** It is an added-mass
implementation reference only. **Do not cite it as a validation target for the
sphere-heave work.** **[recv]** This matters because the sphere-heave grading
(d11-accessor's Job B) is exactly the kind of work that would reach for a
published heave-decay comparison, and there is not one in that paper.

**28b. "Four prior vehicle fording or wading simulations exist" is an UNDERCOUNT.**
CLAUDE.md's figure of four (He 2026, Wasfy 2015, Pazouki, Khapane and Ganeshwade
2014) is superseded. At least four more: `[Lyu23]` `10.1016/j.compfluid.2023.106144`
(particle-based 3D SPH vehicle wading, and therefore the closest published method
to ours that I now know of), `[Ols18b]`, `[Xin21b]` `10.1177/0954407020942005`, and
`[Var21]` `10.4271/2021-01-0205`. Corrected in CLAUDE.md at `c621931`. **[recv]**
**The separate claim is unaffected**: none of them prints in the paper's reference
list. Note the direction of the error, because it matters for how the paper frames
itself: the prior art is **denser** than we thought, so any novelty claim is
weaker, not stronger. `[Lyu23]` in particular should be read before anyone
describes a particle-based vehicle-wading simulation as unprecedented.

**28c. The `physics-skeptic` subagent is dead fleet-wide and an explicit `model`
override does NOT reach it.** Nine origins confirm it; recorded in CLAUDE.md at
`c621931`, verified live by me at `:925`. I hit this three times tonight, including
once through a `general-purpose` agent with an explicit `opus` override, which is
the exact combination CLAUDE.md now records as failing. **Everything in this
document from addendum 2 onward is therefore UNREVIEWED, and I will stop retrying
rather than burn attempts expecting a different result.**

## 29. Status of the refinement ladder, and a note on who is blocked

Batch job **922515** is still `PENDING (Priority)` behind d17's `922514`
(`r9_speed_surface`, now `RUNNING` on c634-111). It will settle whether the
buoyancy error diverges monotonically or is non-monotone like our own g48/g64/g96
ladder. **Until it lands, the two-point result stands as "does not converge", not
as "diverges monotonically".**

**d11-accessor is NOT blocked on me.** The full P-2 numbers, including the
per-run decomposition and the `sweepD_g64_d0p25` case that reads 10.02 percent at
zero penetration, have been inline on the shared board since 18:35, and the board
lives in the main checkout where every session can read it without checking out my
branch. The general three-step floor test is in section 24 and was also posted in
full to the board. The write-up has existed since `a863ee7`.

---

# ADDENDUM 7: RENDERING AND MOVING DOMAINS, READ FROM CHRONO'S SOURCE

Commissioned as three questions about how published work renders a free surface
and handles a domain larger than the body. Answers below are **read from
Chrono::FSI-SPH source at rev `1b90a9f` on Vista**, not from a search summary.
**[read]** Q3 I did not do and say so in section 32.

## 30. Q1: THEY RECONSTRUCT A MESH, AND THE UNITS ARE IN PARTICLE RADII

Chrono does **not** use a screen-space method. It writes the particles to JSON,
calls `splashsurf`, and writes a **Wavefront `.obj` mesh**:

```
ChFsiProblemSPH.cpp:628   std::string out_filename = dir + "/" + name + ".obj";
ChFsiProblemSPH.cpp:630   m_splashsurf->WriteParticleFileJSON(in_filename);
ChFsiProblemSPH.cpp:631   m_splashsurf->WriteReconstructedSurface(in_filename, out_filename, quiet);
```

**The units convention, which is the part that has been costing this project
time.** `ChFsiFluidSystemSPH.h:136-140` documents all three parameters
unambiguously:

```cpp
double smoothing_length;   ///< ... (in multiplies of the particle radius)
double cube_size;          ///< cube edge length used for marching cubes (in multiplies of the particle radius)
double surface_threshold;  ///< isosurface threshold for the density (in multiplies of the rest density)
```

and the radius itself is set at `ChFsiProblemSPH.cpp:287`:

```cpp
m_splashsurf->SetParticleRadius(m_spacing / 2);
```

**So particle radius is HALF the particle spacing, and the two length parameters
are relative to the radius, not to the spacing and not absolute.** Converting
Chrono's own values into spacing units:

| parameter | Chrono default | demo override | in units of **spacing** |
|---|---|---|---|
| `smoothing_length` | 1.5 radii | 2.0 radii | **0.75 to 1.0 x spacing** |
| `cube_size` | 0.5 radii | 0.3 radii | **0.25 to 0.15 x spacing** |
| `surface_threshold` | 0.6 | 0.6 | 0.6 x rest density |

**Answering the question as asked, "at what resolution relative to the particle
spacing":** the marching-cubes grid is **4 to 6.7 times finer than the particle
spacing**, and the kernel smoothing length is **about one particle spacing**.

**Why this matters here specifically.** This project has a recorded failure where
`splashsurf` produced a one-blob-per-particle mesh that passed watertight,
edge-manifold and bounding-box checks while enclosing 0.0002 m3 instead of 1.457,
traced to the docstring being unclear about absolute versus relative units. **A
one-blob-per-particle mesh is the exact signature of a smoothing length that is far
too small relative to the spacing.** Chrono's numbers are a working calibration
from an independent implementation, so the check is arithmetic rather than
guesswork: with spacing `h`, pass `particle_radius = h/2`, then `smoothing_length`
1.5 to 2.0 and `cube_size` 0.3 to 0.5 **as multiples of that radius**. If a
pipeline is passing `0.75*h` where `1.5` is expected, it is off by the radius
factor and blobs are the predicted result.

## 31. Q2: THE BODY-FOLLOWING DOMAIN EXISTS, AND ITS OWN AUTHORS FORBID IT FOR WATER

This is the important one and the answer is a negative that saves work.

Chrono ships exactly the mechanism the render blocker wants,
`ChFsiFluidSystemSPH.h:187` and `:191`:

```cpp
/// Set dimensions of the active domain AABB.
/// This value activates only those SPH particles that are within an AABB of the specified size from an object
/// interacting with the "fluid" phase.
/// Note that this setting should *not* be used for CFD simulations, but rather only when solving problems using the
/// CRM (continuum representation of granular dynamics) for terramechanics simulations.
void SetActiveDomain(const ChVector3d& box_dim);

/// Disable use of the active domain for the given duration at the beginning of the simulation (default: 0).
/// This parameter is used for settling operations where all particles must be active through the settling process.
void SetActiveDomainDelay(double duration);
```

**A body-following activation box is implemented, is used in production for
terramechanics, and is explicitly ruled out for CFD by the people who wrote it.**

**The mechanism behind the prohibition, stated as inference not as their words.**
In granular CRM, material far from the tool is genuinely static and stress is
transmitted locally, so deactivating it changes nothing. Water is different: it is
connected, nearly incompressible, and transmits pressure globally, so deactivating
distant particles severs the pressure field, the free surface and mass
conservation. **[inf]** I have not found a statement of the reason in the source
and am not attributing this argument to Chrono.

**The consequence for the render blocker, which is what was actually asked.** The
cheap route to "a water domain bigger than the camera frame", simulating only near
the vehicle, is **not** available in the one production code that implements it,
because that code restricts it to granular. So a big water domain costs what a big
water domain costs, and with warpmpm's grid forced cubic that cost is cubic. The
options that survive are: accept the cost, decouple render extent from simulated
extent (extend the *road and environment* geometry beyond the simulated water
rather than extending the water), or composite. **Extending the visible road while
leaving the water domain alone is the only one of those that is free**, and it
directly addresses the reported artifact of three floating road patches on an
infinite plane.

**This also explains why unclaimed-ground item 2 is unclaimed.** A body-following
refinement window "appears unreported" for this problem, and the nearest production
implementation says it is invalid for fluid. That is a reason, not just an absence,
and it raises the bar for anyone proposing it: the proposal now has to answer the
pressure-connectivity objection first.

**One free detail worth taking.** `SetActiveDomainDelay` exists because "all
particles must be active through the settling process". An independent code has
the same settle-transient problem this project documented across 25 of 25 runs,
and solved it by making the optimisation wait rather than by shortening the settle.

## 32. What I did not do

- **Q3 is unanswered.** I did not establish whether any published vehicle-in-water
  work releases a video or frame sequence with the paper. It needs the deep-search
  records rather than a code read, and I ran out of window. `[Lyu23]`
  `10.1016/j.compfluid.2023.106144` is the first place to look, being
  particle-based 3D SPH vehicle wading.
- **I did not read DualSPHysics or IBAMR output conventions**, so "what do they
  actually write out" is answered for Chrono only. DualSPHysics ships
  visualisation tooling and is the obvious second read.
- Nothing here is adversarially reviewed; `physics-skeptic` is dead fleet-wide per
  `c621931`, verified at `CLAUDE.md:925`.

---

# ADDENDUM 8: THE LADDER LANDED AND IT REFUTES MY OWN "DOES NOT CONVERGE"

## 33. Four points, non-monotone, and it CONVERGES

Batch job **922515** completed in 2:43 on `c612-151`, all four rungs `rc=0`.
**With `dt` scaled to spacing, the two rungs that previously died now run**, which
confirms the CFL diagnosis in addendum 2 was correct. Settle-window mean `Fz`
against analytic `rho g V` = 50.2272 N: **[read]**

| spacing | `dt` | n | mean Fz [N] | sd Fz | ratio | **error** | change |
|---|---|---|---|---|---|---|---|
| 0.030 | 1.000e-4 | 125 | 74.355 | 10.778 | 1.4804 | **+48.04 %** | |
| 0.020 | 6.667e-5 | 188 | 79.332 | 13.681 | 1.5795 | **+57.95 %** | **+9.91** |
| 0.015 | 5.000e-5 | 250 | 65.064 | 5.676 | 1.2954 | **+29.54 %** | **-28.41** |
| 0.010 | 3.333e-5 | 375 | 58.125 | 3.711 | 1.1572 | **+15.72 %** | **-13.82** |

**My claim that this code "does not converge the buoyant force under refinement"
is REFUTED by my own ladder.** It converges. The error falls from +58.0 percent to
+15.7 percent and is still falling at the finest rung. What it does *not* do is
converge **monotonically**: it rises on the first refinement step, then falls
steeply.

**The scatter converges cleanly and monotonically after the first step**: sd goes
10.78, 13.68, 5.68, 3.71. So the *noise* behaves better than the *mean*, which is
worth knowing for anyone choosing a resolution on the basis of how clean a trace
looks.

**This is the third time tonight a two-point result of mine died to a third
point, and the pattern is the lesson.** I said explicitly in addendum 2 that two
points cannot separate divergence from non-monotonicity and that I had no right to
exclude the latter. That caveat was correct and it is exactly what happened. It
also independently reproduces the structure of CLAUDE.md item 5, our own
g48/g64/g96 ladder being non-monotone: **a non-monotone convergence ladder is now
observed in two unrelated codes on the same class of problem.**

## 34. THE INPUT THAT MAKES THE CHECK FAIL, named as `e81bc9c` requires

The rule asks for the input at which two codes' errors diverge rather than
converge. For this comparison it is a single number:

> **Spacing 0.020.** That rung is the peak of the error curve (+57.95 percent).
> Any resolution study that stops at or before 0.020 sees a rising error and
> concludes divergence. Any study that reaches 0.015 sees it fall.

So the check fails on **a resolution sample that terminates on the rising limb**,
and the minimum sufficient ladder here is **four rungs spanning at least 3x in
spacing**. Two rungs is not a convergence study, and three rungs at 0.030, 0.020,
0.015 would have been ambiguous.

## 35. +48 VERSUS +50: THE COINCIDENCE IS REAL BUT THE RESOLUTION DEPENDENCE BREAKS IT

The comparison asked for, with provenance separated because the two halves are not
equally sourced.

| quantity | value | source |
|---|---|---|
| Chrono::FSI-SPH buoyancy error, spacing 0.030 | **+48.04 %** | **[read]** mine, this session |
| Chrono::FSI-SPH buoyancy error, spacing 0.010 | **+15.72 %** | **[read]** mine, this session |
| Job B measured accessor, canonical | **+50.06 %** | **[recv]** not verified by me |
| Job B, span across 24 gradings | **+34.4 to +64.2 %** | **[recv]** not verified by me |

**At spacing 0.030 the two agree strikingly**: +48.04 against +50.06, and the
Chrono value sits inside d11's +34.4 to +64.2 span. A different code, different
method, different team, different quantity, missing analytic by the same order in
the same direction.

**But the agreement is an artifact of which rung I quote, and that is the finding.**
My +48.04 is not a property of Chrono; it is a property of Chrono **at spacing
0.030**. The same code gives +15.72 percent at 0.010 and is still falling.
**Quoting "+48 versus +50" as a coincidence worth explaining requires pinning the
Chrono number to a resolution, and once pinned it stops being a constant.**

**The discriminator, and it is cheap.** If the two excesses share a cause, the
shared cause is almost certainly coarse resolution, and then **d11's number must
move under refinement the way mine does.** So:

- **If Job B's excess falls toward zero as the sphere-heave resolution is refined**,
  shared cause is supported and the right statement is "both codes over-predict
  buoyant force at coarse resolution", which is a real and citable result.
- **If Job B's excess is resolution-invariant**, the two are unrelated, the numeric
  agreement at one rung is a coincidence, and d11's FAIL localises to something
  specific to the accessor rather than to particle-method resolution.

**That test is the whole value of putting the numbers side by side, and neither
session has run it.** It requires a resolution ladder on the sphere-heave case,
which is d11's to run, not mine. **I am explicitly not claiming a shared cause.**
Two numbers agreeing at one resolution, where one of them is known to be strongly
resolution-dependent, is exactly the coincidence this project's rules warn about,
and I have not verified d11's figures at first hand.

**One asymmetry worth flagging.** Mine is a **static hydrostatic** quantity,
buoyancy on a stationary submerged box, with an exact closed form. Job B is a
**heave force ratio** on a sphere. These are not the same physical quantity, and a
shared "+50 percent" across two different quantities is weaker evidence than the
same quantity twice. **If anyone writes this up, that difference must be stated in
the same sentence as the agreement.**

## 36. Status of the vehicle-fording build

Batch job **922601** submitted, `PENDING`, 1:30:00 on `gh`, reconfiguring with
`-DCH_ENABLE_MODULE_VEHICLE_MODELS=ON` plus `_VEHICLE` and `_COSIM`, then building
`demo_VEH_Cosim_WheeledVehicle_SPH`. **It configures into a NEW directory
`build_veh`, deliberately not `build_fsi`**, because `build_fsi` is what every
buoyancy number above was produced against and reconfiguring it in place could
invalidate published results for the cost of some disk.

---

# ADDENDUM 9: A THIRD CONVERGENCE CATEGORY, AND THE VEHICLE TARGET BUILT

## 37. THREE CATEGORIES, AND ONLY TWO OF THEM ARE ABOUT THE DISCRETISATION

d15-settle's `da0e8ce` (verified live, 2026-08-19 23:11:10, 2 files) supplies a
category my convergence work did not have. Stating all three together, because the
distinction is what stops a real result being read as a solver defect:

| category | why it does or does not converge | example | what to report |
|---|---|---|---|
| **1. Converges** | discretisation error shrinks with resolution | Chrono buoyancy, +48.04 -> +15.72 across four rungs | the converged value plus the ladder |
| **2. Fails to converge, for a discretisation reason** | the scheme loses consistency under refinement at fixed particles-per-cell | Steffen, Kirby and Berzins 2008, cited at L-5 for our g48/g64/g96 | the failure, as a limitation, with the mechanism |
| **3. CANNOT converge, because of what the observable IS** | **the quantity is an unbounded functional of the state, so no record length and no resolution can stabilise it** | `final_disp_mag_m`; any displacement under non-zero mean velocity | **a different observable** |

**Category 3 is not a weaker version of category 2, and that is the whole point.**
Category 2 is a property of the *method* and might be fixed by a better scheme.
Category 3 is a property of the *question*: displacement is the time integral of
velocity, so if velocity equilibrates to any non-zero mean, displacement drifts
without bound and **no window of it is stationary at any length**. Refining the
grid cannot help. Lengthening the record cannot help. **[recv]**

**The measurement behind it**, from `da0e8ce` and not re-derived by me: in a
400-frame record `final_disp_mag_m` peaks at 0.667127 m at row 64 and **ends at
0.290845 m, 43.6 percent of its own peak**, so the same configuration reports 0.657
or 0.291 depending only on when you stop looking. And the N_eff diagnostic
separates the categories cleanly: at 400 frames `vx` and `vmag` scale as expected
(N_eff 4.33 to 58.92, and 4.12 to 201.80) while `dx` and `dmag` **saturate** (6.40
to 3.50, 6.42 to 5.59), with `dx`'s N_eff going **down** on a record 4.4x longer.
**A statistic that gets worse on a longer record is the signature of category 3.**

**What this does to CLAUDE.md item 5.** Item 5 records `final_disp_mag_m` moving
+87.8 percent then -59.2 percent across g48/g64/g96 and instructs that the verdict
may be cited but never the displacement magnitude. **That instruction was right and
now has a mechanism that is not a solver defect.** The non-monotonicity across
grids is at least partly the terminal-frame problem: three grids stopped at the
same frame index are three different points on three drifting curves. Syamlal,
Celik and Benyahia 2017 already say a transient instantaneous value has no GCI;
this reaches the same place from a stationarity statistic on our own data, which is
a **separate origin** and therefore corroboration rather than restatement.

**Where my own buoyancy result sits.** Category 1, and it is worth saying why it is
allowed to be: the settle-window mean `Fz` on a **stationary** body is a bounded
functional of an equilibrated state with an exact closed form, `rho g V`. It is not
an integral of a drifting quantity. **That is precisely why it was a legitimate
convergence target and `final_disp_mag_m` is not**, and it is the practical test to
apply before demanding convergence of anything: ask whether the observable is
bounded and whether a true value exists independent of when you stopped.

## 38. THE FLOAT32 FINDING, TURNED ON MY OWN LADDER

`da0e8ce` also reports two arms differing only in `--frames` diverging by 1.94e-02
at `vz[26]`, traced to **7.8e-08 at frame 0, float32 epsilon, amplified five orders
of magnitude by frame 26**. So two arms are **two draws**, not one trajectory seen
at two lengths. **[recv]**

**That obliges me to ask whether my four-rung ladder is two-draws-in-disguise, and
I should answer it rather than wait to be asked.** My four rungs differ in spacing,
so they are genuinely different discretisations and not repeats; but they are also
four separate runs, so rung-to-rung differences conflate resolution with
run-to-run variation, exactly as d15 warns.

**I have one bound on that variation and it is reassuring but not a repeat.** The
two spacing-0.020 runs, which differ only in `dt` (1e-4 against 6.667e-5), gave
+57.87 and +57.95 percent, **agreeing to 0.08 percentage points**. My rung-to-rung
changes are +9.91, -28.41 and -13.82 points, i.e. **124x to 355x larger than the
only variation estimate I have**. So the ladder's signal sits far above that bound
and the convergence conclusion survives.

**Stated honestly: that is a bound, not a repeat.** Those two runs differ in `dt`,
so they are not two draws of an identical configuration and cannot measure
run-to-run variation directly. **The clean test is trivially cheap and I have not
run it: rerun one rung unchanged and difference it.** Anyone quoting my ladder
should know that repeats were not done.

## 39. THE VEHICLE TARGET BUILT, AND IT IS GRANULAR, NOT WATER

Batch **922601 COMPLETED, ExitCode 0:0, in 4 minutes 36 seconds**, and it built.
**[read]**

```
CONFIGURE RC: 0
BUILD_DEMOS_VEHICLE:BOOL=ON          <- did not exist before the reconfigure
[100%] Built target demo_VEH_Cosim_WheeledVehicle_SPH
build_veh/bin/demo_VEH_Cosim_WheeledVehicle_SPH   TARGET BUILT
```

So my section 22 correction was right that it needed a reconfigure rather than a
`make`, and **wrong to imply it was a big job**: the full reconfigure plus the
entire `ChronoModels_vehicle` library took under five minutes as a batch job.

**But a qualification that matters more than the build, and it cuts against the
premise I was sent.** The demo's own header reads: *"Demo for Polaris wheeled
vehicle cosimulation on **CRM terrain**"*, and it requires **exactly 6 MPI ranks**
(`:79`), one MBS node plus one terrain node plus four tire nodes. **CRM is the
continuum representation of granular dynamics. This is a TERRAMECHANICS case, not a
fording case.** It puts a vehicle on deformable *soil*, not in *water*.

That is consistent with everything else I have found in this codebase and the
pieces now agree: there is **no demo named for fording, wading or amphibious
operation** anywhere in `src/demos` (section 18), and `SetActiveDomain` is
restricted to CRM and explicitly forbidden for CFD (section 31). **Chrono's vehicle
capability is terramechanics.** Whether `[Paz14, Paz16, Was15]` used this machinery
for water, or whether describing them as "vehicle-fording models" overstates them,
is a question about those papers that I have not read and cannot settle from the
code. **Nobody should expect a vehicle-in-water force number to fall out of this
demo.** Run submitted as batch **923199** on 6 ranks to establish that the
vehicle-scale pipeline executes end to end, which is worth knowing on its own.

---

# ADDENDUM 10: THE PINNED-OPERATING-POINT PRINCIPLE

## 40. One rule, arrived at three times by three routes

Three slots produced three non-convergence claims tonight and **all three were
withdrawn or qualified by their own authors**, each for a different reason. That is
not three incidents, it is one rule seen from three sides, so here it is as a rule.

> **A convergence claim is empty until its operating point is pinned.**
>
> Asserting that a quantity converges, or fails to, is a claim about a limit under
> refinement. It means nothing unless three things hold, and each of the three
> failed once tonight:
>
> **(1) The observable must admit a limit at all.** If the quantity is an unbounded
> functional of the state, no resolution and no record length can stabilise it and
> the question is malformed rather than the solver defective.
>
> **(2) Everything else that moves the observable must be pinned AND reported,
> including whatever moves as a side effect of refining.** Refinement is not a
> clean single-variable change; it drags other parameters with it.
>
> **(3) The refinement range must be stated**, because a non-monotone ladder
> returns opposite answers depending on where you sampled it.

**The three failures, one per clause:**

| clause | slot | what went wrong | failure signature |
|---|---|---|---|
| (1) observable admits no limit | d15-settle | `final_disp_mag_m` integrates a velocity with non-zero mean, so it drifts forever and ends at 43.6 percent of its own peak | **a statistic that gets WORSE on a longer record** (`dx` N_eff falls on a record 4.4x longer) |
| (2) side-effect parameter unpinned | d21 | the ladder's operating point moved with resolution and was never matched | **the "held fixed" quantity is not the same at each rung** |
| (3) range too narrow | **d19, me** | two rungs landed on the rising limb of a non-monotone curve; I published "does not converge" and four rungs refuted it | **a two-point ladder** |

**Each signature is a cheap pre-registered check**, which is the point of writing it
as a rule rather than three stories:

- Before demanding convergence, ask **"is this observable bounded, and does a true
  value exist independent of when I stopped looking?"** If no, change the
  observable. A time-integral of a non-zero-mean quantity never qualifies.
- Before comparing rungs, **measure the thing you believe is held fixed, at every
  rung**, and report it beside the observable. Do not assume refinement held it.
- Before concluding either way, **use at least four rungs over at least 3x in
  spacing**, and report the range. For my own ladder, three rungs at 0.030, 0.020
  and 0.015 would still have been ambiguous.

**The asymmetry that makes this worth enforcing.** A *convergence* claim that is
under-sampled usually looks noisy and invites more work. A *non-convergence* claim
that is under-sampled looks like a finding, gets written up, and propagates, because
"the solver does not converge" is more interesting than "it does". **All three
withdrawals tonight were of non-convergence claims, and none of the three was
caught by a reviewer.** Each was caught by its own author adding a data point. That
is the cheapest possible check and it is not currently required anywhere.

**Where each of the three results ended up after the rule was applied**, so nobody
reads this as everything being wrong: d15's displacement result **strengthened**, from
"non-convergent" to "cannot converge, here is the mechanism". Mine **reversed**, from
"does not converge" to "converges non-monotonically, +48.04 to +15.72 over four
rungs". d21's was **withdrawn**. The rule does not predict which way a claim moves;
it predicts that an unpinned claim is not yet a result.

---

# ADDENDUM 11: THE DEFINITIVE PRIOR-ART TABLE, FROM PRIMARY RECORDS

## 41. Fourteen works, every DOI resolved against Crossref by me tonight

**[read]** Every row below was resolved by me against the Crossref primary record
via Scholar Sidekick on 2026-08-20, not carried from any session's list and not
from the corpus index. Titles are the resolved titles, years are Crossref
`issued.year`. Citation status measured against the two tracked bibliographies and
their `.tex` files.

| # | first author, resolved title (abbrev) | DOI | **Crossref year** | method | in a repo `.bib` | **`\cite`d** |
|---|---|---|---|---|---|---|
| 1 | Al-Qadami, *Full-scale experimental investigations on the response of a flooded passenger vehicle* | `10.1007/s11069-021-04949-6` | **2021** | **experimental, full-scale** | no | no |
| 2 | Al-Qadami, *A numerical approach to understand the responses of passenger vehicles moving through floodwaters* | `10.1111/jfr3.12828` | 2022 | **numerical, moving vehicles** | paper only | **no** |
| 3 | Al-Qadami, *Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D CFD Modelling* | `10.3390/su151713262` | 2023 | 3D CFD | overleaf only | **no** |
| 4 | Shah, *Hydrodynamic effect on non-stationary vehicles at varying Froude numbers* | `10.1111/jfr3.12657` | **2020** | experimental, 1:10 scale | no | no |
| 5 | Shah, *Instability Criteria for Vehicles in Motion Exposed to Flood Risks* | `10.1051/matecconf/201820307003` | 2018 | criteria | **both** | **no** |
| 6 | Pregnolato, *The impact of flooding on road transport: A depth-disruption function* | `10.1016/j.trd.2017.06.020` | 2017 | empirical function | no | no |
| 7 | He, *Predicting Vehicle-Water Interaction in Shallow Water: Simulations and Experimental Validation* | `10.1115/1.4071177` | 2026 | **simulation + experimental validation** | paper only | **no** |
| 8 | Wasfy, *Coupled Multibody Dynamics and Smoothed Particle Hydrodynamics for Modeling Vehicle Water Fording* | `10.1115/DETC2015-47142` | 2015 | **SPH + multibody** | paper only | **no** |
| 9 | Khapane, *Wading Simulation: Challenges and Solutions* | `10.4271/2014-01-0936` | 2014 | wading simulation | paper only | **no** |
| 10 | Lyu, *Numerical investigation of vehicle wading based on an entirely particle-based three-dimensional SPH model* | `10.1016/j.compfluid.2023.106144` | **2024, NOT 2023** | **entirely particle-based 3D SPH** | no | no |
| 11 | Xin & Donghai, *Analysis and research on vehicle wading performance* | `10.1177/0954407020942005` | **2020, NOT 2021** | wading performance | no | no |
| 12 | Varshney, *CFD Method Development for Simulating Water Fording for a Passenger Car* | `10.4271/2021-01-0205` | 2021 | CFD fording | no | no |
| 13 | Zhao, *Development of in/outflow boundary conditions for MPM simulation of uniform and non-uniform open channel flows* | `10.1016/j.compfluid.2018.10.007` | 2019 | **MPM BC** | paper only | **no** |
| 14 | Azhar, *Assessment of Vehicle Stability Processes Under Unsteady Flow Conditions* | `10.1111/jfr3.70181` | 2026 | unsteady flow | no | no |

**Not resolvable and therefore not in the table:** Pazouki (Semantic Scholar
`61da26b6`, no DOI supplied) and `[Ols18b]` (no identifier supplied). **The set is
at least 14 and I am not calling it complete**, because two known items have no
resolvable identifier and my search was DOI-resolution, not a systematic sweep.

## 42. THREE CORRECTIONS, TWO OF THEM TO NUMBERS I WAS HANDED TONIGHT

**42a. `10.1016/j.compfluid.2023.106144` is Crossref year 2024, not 2023.** The DOI
string contains `2023` because that is the journal's volume year, and the label
`[Lyu23]` follows the string rather than the record. **A DOI containing a year is
not a citation year**, and this is the same class of trap as the recorded Xia
2013-versus-2014 case.

**42b. `10.1177/0954407020942005` is Crossref year 2020, not 2021**, and the label
`[Xin21b]` is wrong on the same basis: volume 235 issue 1 carries a 2021 print
cover date while Crossref `issued` is 2020.

**42c. CONFIRMED, and this one is a real trap that was flagged and is correct.**
`10.1051/matecconf/201820307003` first author is **Syed Muzzamil Hussain Shah**, not
Hamid. And `10.1111/jfr3.12657` is **2020**, so the two prior instructions to
relabel it 2021 were both wrong. Crossref agrees with the correction, not with the
instructions.

## 43. THE LIVE DEFECT: ONE KEY, TWO DIFFERENT PAPERS

**This is the finding that needs acting on and it is not a labelling nicety.**

```
paper/can_it_ford_references_IEEE.bib          alqadami2022 -> 10.1111/jfr3.12828   (2022, numerical)
overleaf_sync/can_it_ford_references_IEEE.bib  alqadami2022 -> 10.3390/su151713262  (2023, 3D CFD)
```

**The same citation key resolves to two different works in two copies of the
bibliography**, and the key asserts a year that is wrong for one of them. A
`\cite{alqadami2022}` therefore means different things depending on which bib is
compiled, and neither copy signals the conflict. This is the exact conflation the
project has been warned about, now baked into the files rather than into prose.
The two bibs also differ in size, 42 entries against 21, so they are not two copies
of one list.

**Also measured: every one of the fourteen is `\cite`d ZERO times** in both
`paper/conference_101719.tex` and `overleaf_sync/conference_101719.tex`. Six sit in
a bibliography and print nothing. **The standing claim that the paper cites none of
the prior fording work is confirmed against primary records, and the count is at
least 14, not four.**

## 44. WHICH THE PAPER MUST CITE BEFORE SUBMISSION

Ranked by how directly each threatens or positions the contribution.

**Must cite, non-negotiable:**

1. **Lyu 2024, `10.1016/j.compfluid.2023.106144`.** *Entirely particle-based
   three-dimensional SPH model* for vehicle wading. **This is the closest published
   method to ours in existence** and it is in no bibliography here. Any sentence
   describing a particle-based 3D vehicle-wading simulation as novel is unsupportable
   until this is cited and distinguished.
2. **He 2026, `10.1115/1.4071177`.** *Simulations and Experimental Validation* of
   vehicle-water interaction. **The project's stated novelty is the validation step**
   (L-7), and this paper is simulation plus experimental validation of the same
   interaction. It is in `paper/`'s bib and cited zero times. **It is the single
   biggest threat to the novelty claim and must be addressed in the text, not just
   listed.**
3. **Wasfy 2015, `10.1115/DETC2015-47142`.** *Coupled Multibody Dynamics and SPH for
   Modeling Vehicle Water Fording.* Particle method plus multibody, same problem,
   eleven years earlier.
4. **Al-Qadami 2022, `10.1111/jfr3.12828`.** Numerical, **moving** vehicles, which is
   exactly the regime d17 is working in.
5. **Al-Qadami 2021, `10.1007/s11069-021-04949-6`.** Full-scale **experimental**. This
   is the natural external validation target the project lacks, and L-1's stationary
   framing needs it.

**Should cite:** Khapane 2014 (6), Varshney 2021 (12) and Xin 2020 (11) as the
industrial CFD-fording lineage; Shah 2018 (5) and Shah 2020 (4) for the instability
criteria, with (4)'s **1:10 scale** stated whenever its drive force is quoted;
Pregnolato 2017 (6) for the depth-disruption framing; Azhar 2026 (14) for unsteady
flow. **Zhao 2019 (13) is not prior art for fording but must be cited anyway**, since
it is the source for the in/outflow BC and is currently in the bib uncited.

**One thing this table does not settle.** Whether any of these releases a video or
frame sequence, which was Q3 and is still unanswered. Nothing above was read beyond
its Crossref record: **I resolved identity, not content.** No claim here about what
any of these papers found, only about what they are and whether we cite them.

---

# ADDENDUM 12: THE CORPUS DOES HOLD MOST OF THE PRIOR ART, AND ONE WORK IS TRULY ABSENT

## 45. Measured by me, on a named tree, with the container stated

The claim I was given, that none of the six resolved DOIs is in the corpus, is
false, and my own section 6 bullet repeating a related `[recv]` zero is withdrawn
above. **Measured live 2026-08-20** on
`claude/r9-priorcode:data/research_corpus_index.json`. **[read]**

**The index blob is byte-identical across `claude/r9-priorcode`,
`claude/r9-corpus-bib` and `claude/add-ci-checks` (`d132b45f`), and is ABSENT from
`origin/main`.** So every session that has the tool is reading the same data, and a
session working from a fresh clone of main has no corpus tool at all.

| work | in `papers[]` (the 332) | in `documents[]` |
|---|---|---|
| Al-Qadami 2021 experimental | **yes** | 1 |
| Al-Qadami 2022 numerical | **yes** | 4 |
| Al-Qadami 2023 3D CFD | **yes** | 4 |
| Shah 2020 | **yes** | 2 |
| **Shah 2018** | **no** | 2 |
| **Pregnolato 2017** | **no** | 2 |
| He 2026 | **yes** | 1 |
| Wasfy 2015 | **yes** | 2 |
| Khapane 2014 | **yes** | 0 |
| **Lyu 2024** | **no** | **0** |
| Xin 2020 | **yes** | 0 |
| **Varshney 2021** | **no** | 2 |
| Zhao 2019 | **yes** | 1 |
| Azhar 2026 | **yes** | 4 |

**10 of 14 are in the 332-paper corpus.**

**THE SCOPE QUESTION, AND IT DISSOLVES THE DISAGREEMENT RATHER THAN SETTLING IT
AGAINST ANYONE.** Of the six DOIs I was handed, **4 of 6 are in `papers[]`** and the
other two, Shah 2018 and Pregnolato 2017, appear **only in `documents[]`**. So "all
six are present" is right if `documents[]` counts and wrong if it does not, on the
identical index blob. **This is exactly the container distinction d14 themselves
drew earlier for deep searches**, applied now to papers, and it is the same
scope-sensitivity as the DRIFT_THRESHOLD total: **state the container or the number
means nothing.**

**THE ONE THAT IS TRULY ABSENT, AND IT IS THE WORST ONE TO BE MISSING.**
**`10.1016/j.compfluid.2023.106144`, Lyu 2024, is in NEITHER container: 0 in
`papers[]`, 0 in `documents[]`.** It appears nowhere in the corpus, nowhere in
either bibliography, and nowhere in the repo. **It is the entirely particle-based
three-dimensional SPH vehicle-wading paper, which is the closest published method
to ours in existence.** Every other item in this table is at least known to the
project somewhere. This one is not, and it is the one that most directly constrains
a novelty claim. **That is the single most actionable line in this document.**

## 46. THREE PREDICATES DISAGREED ON THE SAME FILE AND I NEARLY PUBLISHED TWICE

Recorded because the near-misses are the transferable part and the pattern is now
the dominant failure mode of the round.

1. **`--query "Al-Qadami"` returns zero.** Correct measurement, **broken
   predicate**: it matches title and abstract only, never authors. A zero from
   `--query` is not evidence of absence.
2. **A raw `grep -c` on the index file returns 2 for Shah 2018**, which looks like
   `--doi` giving a false negative. **I nearly wrote that `--doi` is broken.** It is
   not: the grep was hitting `documents[]`, while `--doi` correctly searches
   `papers[]`. **Two predicates, two containers, both right.**
3. **My own membership test returned zero for all fourteen.** `papers` is a **dict
   keyed by DOI**, not a list of records, so `for x in papers` iterates
   *keys*, and `.get("doi")` on a string raises. An earlier version of that loop
   silently produced all-zeros, which would have published "the corpus contains
   none of the prior art", the exact inverse of the truth.

**Only one of those three was a real defect, and it was the first.** The other two
were mine, and both would have produced a confident wrong answer in the same
direction: **absence**. That is the asymmetry worth naming, and it is the same one
as in section 40: **a predicate that under-reports produces findings, and findings
propagate.** The check that caught all three was cheap and obvious in hindsight,
**make the predicate return a known-present hit before trusting a zero**, and it is
the same positive-control discipline that caught the zsh word-splitting false zero
in section 44.

## 47. Which tree each citation-status claim in this document was measured on

Required because the answer differs by tree, as asked. **[read]**

- **Prior-art table citation columns (section 41)**: measured on
  `/Users/josie/can-it-ford` working tree, currently on branch
  **`claude/add-ci-checks`**, against the two tracked bibliographies
  `paper/can_it_ford_references_IEEE.bib` and
  `overleaf_sync/can_it_ford_references_IEEE.bib` and their `.tex` siblings.
- **Corpus membership (section 45)**: measured on **`claude/r9-priorcode`**, index
  blob `d132b45f`, verified identical on `claude/r9-corpus-bib` and
  `claude/add-ci-checks`.
- **Neither was measured on `origin/main`**, where `analysis/research_index.py` does
  not exist at all, so **none of this is reproducible from a fresh clone of main**.

---

# ADDENDUM 13: THE DECISION. CANONICAL BIB, AND WHAT MUST BE CITED.

## 48. SELF-CORRECTION FIRST: I MEASURED AGAINST TWO FILES, NEITHER OF WHICH SHIPS

Section 41 reported all fourteen prior-art works `\cite`d zero times, measured
against `paper/conference_101719.tex` and `overleaf_sync/conference_101719.tex`.
**Neither of those is the file the paper builds from**, so two of my claims were
measured on the wrong artifact. Corrected live: **[read]**

```
overleaf/main tree:  conference_101719_1.tex        <- note the _1
                     can_it_ford_references_IEEE.bib  (REPO ROOT, 15 entries)
```

| claim in section 41/43 | corrected |
|---|---|
| "all fourteen are `\cite`d zero times" | **13 of 14. `shah2018` IS cited in the shipped paper.** |
| "one key points at two different papers" in a deliverable | **True, but NOT in the deliverable.** `alqadami2022` appears **0 times** on `overleaf/main`, in tex and bib alike. |

**I over-stated the collision's severity and it was relayed onward at that
severity, so I am correcting it plainly.** It is a real landmine, `paper/` and
`overleaf_sync/` disagree and whoever merges them will silently pick one, but **it
is a defect in staging files, not in the submitted paper.** Downgrade from
"correctness defect in a deliverable" to "merge hazard in two staging copies".
This is exactly the tree-provenance failure I wrote section 47 about and then
committed anyway.

## 49. THE CANONICAL BIBLIOGRAPHY IS `overleaf/main:can_it_ford_references_IEEE.bib`

Measured across every ref I can reach: **[read]**

| ref | path | entries |
|---|---|---|
| **`overleaf/main`** | **`can_it_ford_references_IEEE.bib`** (repo root) | **15** |
| `origin/main` | `paper/...bib` | 21 |
| `origin/main` | `overleaf_sync/...bib` | 21 |
| `claude/r9-priorcode`, `add-ci-checks` | `paper/...bib` | **42** |
| `claude/r9-priorcode`, `add-ci-checks` | `overleaf_sync/...bib` | 21 |

**The decision, with the reasons, so it can be overturned on evidence rather than
taste:**

1. **`overleaf/main` is the only ref carrying the tex the paper builds from**,
   `conference_101719_1.tex`. The two local `conference_101719.tex` files are not it.
2. **Its bib is the only one consistent with the shipped document.** 15 entries, 14
   distinct `\cite` keys in the tex, all 14 present in the bib, exactly one entry
   never cited (`xiong2024`, which BibTeX therefore drops). Verified live tonight,
   and it reproduces CLAUDE.md's independently recorded ladder exactly.
3. **`paper/...bib` is not stable across refs**: 21 entries on `origin/main`, 42 on
   two unmerged branches. A file that differs by 21 entries depending on checkout
   cannot be canonical.

**So: `paper/` and `overleaf_sync/` are STAGING. Neither is authoritative.** Changes
must land in `overleaf/main:can_it_ford_references_IEEE.bib` to reach the paper.
Note the standing constraint that `overleaf/main` shares no ancestor with `origin`,
so `git push overleaf main` **overwrites rather than merges**, and a fresh Overleaf
token is needed because the old one was taken off local disk but never revoked.

## 50. WHAT THE SHIPPED PAPER ACTUALLY CITES FROM THE PRIOR ART: ONE WORK

The 15 shipped keys are: `thorpe2026pvwm hsiao2025nerfmpm kerbl20233dgs
xie2023physgaussian shand2011arr smithmodrafelder2019 shah2018 xia2014 azhar2023
xiong2024 ccsa2016yaris heydinger1999sae nws_tadd genesis2024 fred2026`.

**Exactly one of my fourteen prior-art works is in it: `shah2018`
(`10.1051/matecconf/201820307003`), and it is cited.** The other **thirteen are
absent from the shipped bibliography entirely**, so they cannot be cited without
first being added.

## 51. THE DECISION: SIX MUST BE ADDED AND CITED BEFORE SUBMISSION

Ranked. Each is absent from the shipped bib, so each needs a bib entry **and** a
`\cite`, not just a listing.

| # | work | DOI | why it is non-negotiable |
|---|---|---|---|
| 1 | **Lyu 2024** | `10.1016/j.compfluid.2023.106144` | **Entirely particle-based 3D SPH vehicle wading. The closest published method to ours in existence, and absent from the corpus, both bibs and the whole repo.** No sentence calling a particle-based 3D vehicle-water simulation novel survives its existence. |
| 2 | **He 2026** | `10.1115/1.4071177` | *Simulations **and Experimental Validation*** of vehicle-water interaction. The project's stated novelty is the validation step (L-7). **This is the single largest threat to the contribution and must be distinguished in the text, not merely cited.** |
| 3 | **Wasfy 2015** | `10.1115/DETC2015-47142` | *Coupled Multibody Dynamics and SPH for Modeling Vehicle Water Fording.* Same problem, particle method, eleven years earlier. |
| 4 | **Al-Qadami 2022** | `10.1111/jfr3.12828` | Numerical, **moving** vehicles: the regime the moving-vehicle work occupies. |
| 5 | **Al-Qadami 2021** | `10.1007/s11069-021-04949-6` | **Full-scale experimental.** The external validation target this project does not have, and the natural anchor for L-1's stationary framing. |
| 6 | **Zhao 2019** | `10.1016/j.compfluid.2018.10.007` | **Not fording prior art, but a live sourcing gap**: it is the source for the in/outflow BC the project implements, and it is absent from the shipped bib. Using a method and not citing it is a worse defect than omitting a competitor. |

**Should add if space permits**, in this order: Khapane 2014, Varshney 2021 and Xin
2020 as the industrial CFD-fording lineage; Shah 2020 (`10.1111/jfr3.12657`) **with
its 1:10 scale stated wherever its drive force is quoted**; Pregnolato 2017;
Azhar 2026 (`10.1111/jfr3.70181`), noting the shipped bib already has an `azhar2023`
key whose identity I have **not** checked against this DOI and which should be
checked before adding a second Azhar entry.

**The honest summary for whoever writes the related-work paragraph.** The paper
currently ships citing **one** work from the vehicle fording and wading literature.
The literature contains **at least fourteen**. Adding the six above does not weaken
the contribution; **failing to add them makes the novelty claim unsupportable**, and
two of them (Lyu, He) constrain how that claim can be phrased at all.

---

# ADDENDUM 14: THE VEHICLE COSIM RAN, AND I SEARCHED FOR A DOI I HAD JUST WRITTEN

## 52. A vehicle-scale coupled run on a GH200 costs RTF 92.4

Batch **923199 COMPLETED, ExitCode 0:0**, 6 MPI ranks on `c609-001`. **[read]**

```
Loaded JSON ../data/vehicle/Polaris/Polaris.json
RTF: 437.076 ... 208.217 ... 128.993 ... 100.406 ... 92.3967
```

**Real-time factor settles at 92.4**, from a 437 start, monotonically decreasing as
startup cost amortises. So a **Polaris wheeled vehicle co-simulated against CRM/SPH
terrain on one GH200 runs about 92 times slower than real time.** One simulated
second costs about a minute and a half of wall clock.

**Stated plainly: this run did NOT finish its intended duration.** I wrapped it in
`timeout 1800` and the 30:09 elapsed is that timeout firing, not the demo
completing. `rc=0` in my log is the exit status of the `tail` in my pipeline, not of
the solver, which is a defect in my own script and I am not reading it as success.
What is established is that **the pipeline runs end to end on aarch64 across 6
ranks**, and the RTF, which had clearly converged.

**Why the number is worth keeping even though the run was truncated.** It is the
only vehicle-scale cost figure this project has from an independent code on its own
hardware, and it bounds what a vehicle-in-fluid coupled simulation costs before
anyone plans one. **It is CRM terrain, not water**, so it is not a fording cost, and
nobody should quote it as one.

## 53. I CLAIMED LYU 2024 APPEARS "NOWHERE IN THE REPO AT ALL". THAT WAS A SELF-REFERENCE TRAP.

A full-tree scan I had abandoned as too slow completed afterwards and returned
**31 hits** for `10.1016/j.compfluid.2023.106144`. My committed claim in section 45
was "0 in `papers[]`, 0 in `documents[]`, in neither bibliography and **nowhere in
the repo at all**". The last clause is **false as written**.

**What it actually is, with the scope stated this time:** **[read]**

| scope | Lyu 2024 |
|---|---|
| `origin/main`, tracked | **zero** |
| `claude/r9-priorcode`, tracked | **1 file, and it is my own document** |
| whole working tree, untracked included | 31 hits, all written tonight |

**I searched for a DOI I had myself introduced into the repo hours earlier.** The
31 hits are this document, the shared board, and sibling sessions' notes, all
created after I first wrote the DOI down. The defensible claim is **"absent from
`origin/main`, from the corpus index, and from all three bibliographies"**, which is
what I actually established and which is fully sufficient for the conclusion. The
sweeping version added nothing and was wrong.

**This is my fourth self-correction tonight and the third of the same class: a
count published without its scope.** The others were the DRIFT_THRESHOLD-style
container question in section 45, the tree-provenance error in section 48, and this.
**The pattern is now unambiguous enough to state as a rule of its own:** when the
thing you are counting is a string you have recently written, **a repo-wide search
measures your own activity**, and the only honest scopes are a ref that predates
your work or an explicitly tracked-file view. Neither is expensive.

## 54. One thing that DID corroborate cleanly, from two independent scans

The abandoned slow scan and the fast scoped scan were written separately and run
against different file sets, and **they agree exactly on the bibliography column**:
`10.1111/jfr3.12828`, `10.1115/1.4071177`, `10.1115/DETC2015-47142`,
`10.4271/2014-01-0936` and `10.1016/j.compfluid.2018.10.007` each appear in exactly
**1** file under `paper/`, and `10.1051/matecconf/201820307003` in **2**. The
positive control returned 10 hits repo-wide and 0 under `paper/`, so the predicate
could return a hit and did.

**That is two separate origins agreeing, which is the standard this project holds
itself to, and it is the reason the section 51 must-cite list survives everything
above.** The prior-art table's identity and citation columns are the part I would
defend; the sweeping absence claim in section 45 is the part that needed the scope.
