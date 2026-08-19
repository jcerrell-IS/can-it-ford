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
- **The corpus is silent on this whole topic** and that silence is not evidence:
  `research_index.py --query "Al-Qadami"` returns zero and both
  `--method moving-vehicle` and `--method rigid-coupling` return no match **[recv]**.
  No novelty claim in this document rests on a corpus miss.

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
