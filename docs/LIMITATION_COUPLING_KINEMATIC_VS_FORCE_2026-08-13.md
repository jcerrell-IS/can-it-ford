# Limitation note: velocity-level coupling vs force-based two-way coupling

Drafted 2026-08-13 for the paper's limitations section. **Prose only, no code
change proposed.**

Rescued 2026-08-13 from the untracked worktree
`.claude/worktrees/warpmpm-flood-vehicle-investigation-1b62fa`, where it sat on a
branch 16 commits behind main and was absent from main entirely. The worktree
copy is deliberately left in place, not deleted.

## Provenance of every claim below

Tagged, per the project's standing rule that a claim carried from a summary is
not a verified claim.

- **[READ LIVE]** Every warpmpm claim was re-verified on 2026-08-13 by direct
  read of the pinned vendored solver core at
  `third_party/mpm-engine-544c93dd-solver-core/`, whose `PINNED_SHA.txt` reads
  `544c93dd02cb9c7ead89e1155a62967243244fce`. Line numbers were confirmed
  individually, not trusted from the draft. **Both** `kernels/mpm_utils.py` and
  `kernels/mpm_solver_warp.py` were read, plus `core/solver.py` and the driver
  `renders/yaris_render_s1/sim_standing.py`. The draft read only the first of
  these, which is what produced its three blocking errors; a revision that reads
  only `mpm_utils.py` will reintroduce them.
- **[PUBLISHER RECORD]** The two external papers were verified 2026-08-13 by DOI
  lookup against the publisher record (scite MCP). Both are **closed access** and
  **neither was read in full**, so every characterisation of them is
  abstract-level. Verify before the paragraph ships. Exact fields and two
  corrections: `docs/PENDING_BIB_ENTRIES_2026-08-13.md`.
- **[ENGINE TAG]** Everything here describes **warpmpm**, the engine behind all
  17 gated runs. None of it describes Genesis, which is the abandoned box-proxy
  path and has never loaded the Yaris hull.

## What the 17 gated runs actually do

The vehicle is material 8. Its coupling is **three** kernels plus a host-side
contact stage, not the two the first draft of this note described. The draft read
only `kernels/mpm_utils.py` and never opened `kernels/mpm_solver_warp.py`, which
is where the substep call order and the contact resolver live. That single
omission produced three false statements, all corrected below and recorded in
"Corrections made during rescue".

**[READ LIVE]** `kernels/mpm_utils.py:1370` `rigid_g2p_accumulate` walks each
rigid particle, interpolates the grid velocity with the same quadratic B-spline
used by the fluid G2P (the kernel's own comment at `:1383` says "same as g2p"),
and accumulates, at `:1411-1412`:

```
linear_mom  += m_p * v_interp(x_p)          # wp.atomic_add(rigid_linear_mom, ...)
angular_mom += r_p x (m_p * v_interp(x_p))  # wp.atomic_add(rigid_angular_mom, ...)
```

**[READ LIVE]** `kernels/mpm_utils.py:1416` `rigid_body_integrate` then sets, at
`:1434` and `:1438-1439`:

```
v_cm   = linear_mom / M                     # M = rigid_mass[b]
omega  = I_world_inv * angular_mom          # I_world_inv = R I_body_inv R^T
```

So the body's linear velocity **at the exit of that kernel** is the
**mass-weighted average of the grid velocity sampled at its own particles**. That
much is exact, not approximate: `kernels/mpm_solver_warp.py:852-856` forms
`rigid_mass[b]` as `m_np[np.where((mat_np == 8) & (rid_np == b))].sum()`, the
identical particle set the `:1411` accumulator loops over, so
`v_cm = Sum(m_p v_interp) / Sum(m_p)` with units (kg m/s)/kg = m/s. Both
accumulators are zeroed every substep at `kernels/mpm_solver_warp.py:1344-1347`,
so neither momentum is a persistent state variable: both are discarded and
re-read from the grid each substep.

**A third stage then runs, and the first draft of this note missed it.**
`kernels/mpm_solver_warp.py:887` `_apply_rigid_restitution` executes at `:1362`,
between the integrate above and the push-back below, and it applies a normal
impulse `J_n = -(1+e) v_n / denom` (`:960`, with a proper effective-inverse-mass
denominator at `:957`) and a Coulomb friction impulse
`J_t = min(v_t_mag/denom_t, mu*J_n)` (`:975`). It **increments** the body state:

```
:963  v_cm  += (J_n / M) * n
:964  omega += I_world_inv @ (J_n * r_cross_n)
:976  v_cm  -= (J_t / M) * t_hat
:977  omega -= I_world_inv @ (J_t * r_cross_t)
```

plus a positional projection `x_cm += push` at `:941`. **This stage is live in
all 17 gated runs.** `:1915` gates it on `restitution != 0.0`, and
`renders/yaris_render_s1/sim_standing.py:211` registers the floor with
`friction=floor_friction` (0.55, `:154`) and `restitution=0.05`, while `:214`
registers all four walls with `restitution=0.05`. CLAUDE.md's addendum A-1
independently records the same fact ("the 17 runs use restitution 0.05 on floor
and walls where C1 used 0.0 everywhere").

**[READ LIVE]** Finally `kernels/mpm_utils.py:1463` `rigid_particle_update`
writes `v_cm + omega x r` back onto the rigid particles at `:1490` and after,
which is what carries the body's motion into the next P2G. This is the
back-reaction limb; a description that omits it describes a one-way path.

So "the velocity is overwritten, never incremented by an acceleration" is **false
as a statement about the substep**. It is true only of `:1434` in isolation, and
`Delta v = J/M` at `:963` is an increment by definition.

Three consequences follow directly, and they are the substance of the
limitation:

1. **No *hydrodynamic* force is ever formed.** There is no `dp/dt` and no
   pressure integral over the hull. Contact impulses against the registered
   planes *are* computed, with lever arms, at
   `kernels/mpm_solver_warp.py:957-977`, so the blanket claim "no force is ever
   formed" is wrong; but those are contact impulses, not the fluid load, and
   they are not exposed either. This is the mechanical reason register A3
   records that no force accessor exists on this path. The net force is
   recoverable as `M (v_cm_new - v_cm_old) / dt`, but it **cannot be decomposed**
   into hydrodynamic, contact and gravitational parts, so no hydrodynamic load
   can be reported. That decomposability, not the existence of a number, is the
   limitation.
2. **The exchange is a momentum mixing, and it is not conservative.** Rigid
   particles do enter P2G and deposit both mass and momentum:
   `kernels/mpm_utils.py:921` filters only on `particle_selection`, with no
   material filter. They carry zero stress, but the supporting line is
   `:1100` (`stress` zero-initialised) plus the absence of any `mat == 8` branch
   through `:1104-1146`, **not** `:1090`, which merely sets `particle_F = I`.
   The body's gather at `:1407` reads `grid_v_out` and writes nothing back,
   while the fluid gathers from the same array at `:1003`. The PIC momentum
   identity holds only for a reduction over *all* particles depositing to a
   node, so a reduction over the rigid subset alone takes momentum the grid
   never gives up. Newton's third law is therefore **not** enforced here, and
   momentum is not conserved across the interface. The magnitude of that
   imbalance has not been measured. Note also that the fluid does not see the
   body merely as occupancy: `:1490` sets `particle_C = skew(omega)`, so the
   body's full rigid velocity field, rotation included, enters the next P2G.
3. **Angular momentum is not a state variable.** `omega` comes from applying
   `I_world_inv` to an averaged angular momentum, an orientation-dependent
   linear map rather than a division. There is no gyroscopic `omega x (I omega)`
   term in `rigid_body_integrate`, and correctly so: a momentum formulation does
   not need one, so this is not a defect and the body does not tumble
   incorrectly. The real rotational limitation is sharper: `_rigid_angular_mom`
   is zeroed at `kernels/mpm_solver_warp.py:1347` and re-gathered from the grid
   every substep, so the body retains no independent rotational memory, and
   whatever persists is filtered through a P2G/G2P round trip.

**[READ LIVE]** A force-capable path does exist in the same file. The CPIC
implementation of Hu et al. 2018 accumulates a reaction impulse and torque into
`cdf_reaction_force` and `cdf_reaction_torque` at `kernels/mpm_utils.py:908` and
`:910`, from the momentum deposit the thin boundary blocks.

**Cite the code, not the comment.** The block comment at `:643-645` says the
impulse "accumulates during G2P from the ghost substitution, `m w (v_p -
ghost)`". A `/usr/bin/grep` for `cdf_reaction_force|cdf_reaction_torque` in the
pinned file returns **only** `:908` and `:910`, both on the P2G side, and the
quantity accumulated there is `v_in_add`, not `m w (v_p - ghost)`. The first
draft of this note quoted that comment as though it were the implementation. No
`m w (v_p - ghost)` accumulation exists anywhere in the pinned file.

**The 17 gated runs do not use this path**: it is gated on `model.n_cdf > 0` at
`:852` and `:973`, and the driver registers no CDF collider. They use the
material-8 path above. The distinction matters and should not be blurred.

## The contrast, for the limitations paragraph

> The vehicle in this study is coupled to the flow at the velocity level: each
> substep the body's linear and angular momentum are set to the mass-weighted
> average of the background grid velocity sampled at its own material points,
> its pose is integrated from that, and contact impulses against the floor and
> tank walls are then applied. No *hydrodynamic* force or torque is ever
> assembled. The body's net acceleration is recoverable from its own kinematics,
> but it cannot be decomposed into hydrodynamic, contact and gravitational
> parts, which is why the solver exposes no force accessor and why drag and
> buoyancy on the vehicle cannot be measured directly. The gather is also
> one-sided: the body draws momentum from the grid without the grid being
> debited, so momentum is not conserved across the interface by construction.
> This differs in kind, not merely in accuracy, from the force-based two-way
> formulations standard in both the SPH and MPM literature. Akinci et al. [1]
> sample the rigid surface with boundary particles whose volumes are derived
> from the local boundary-sampling density, so a particle's contribution is
> independent of how unevenly the surface is sampled, compute pressure and
> friction forces on the fluid from those particles, and apply the summed
> reaction force and torque back to the body, making the exchange
> momentum-conserving and the instantaneous load a directly reportable quantity.
> Li et al. [2] build on that same force-based structure and show that its
> gradients with respect to rigid-body state can be computed stably and cheaply,
> which is what makes fluid-driven rigid control tractable. The velocity-level
> map used here is itself differentiable, being linear in the grid velocities,
> so the obstruction is not one of smoothness: it is that the formulation
> exposes no applied force to serve as a control variable, and that its contact
> stage executes on the host as a NumPy round trip, which severs any device-side
> tape. Within MPM, the CPIC formulation of Hu et al. is the corresponding
> force-based alternative and is present in this solver but unused by these
> runs. The practical consequence for the present results is that the reported
> outcome is a displacement verdict, not a force measurement, and the coupling
> itself remains unvalidated against an analytic or experimental load.

### Corrections made during rescue, and why

An adversarial review of the draft on 2026-08-13 returned three **blocking**
findings. Each was then re-verified independently against the pinned source
before being accepted, per the standing rule that another agent's report is a
hypothesis, not a second source. All three were confirmed and are fixed above:

1. **The contact-impulse resolver was missing entirely.** The draft asserted "no
   force is ever formed", "without any torque ever being computed", and
   "overwritten each substep, not incremented by an acceleration". All three are
   falsified by `_apply_rigid_restitution`, which is live in every one of the 17
   runs. A reviewer opening the solver would have found a textbook impulse-based
   contact resolver with lever arms. This was the most damaging defect.
2. **"Newton's third law is satisfied incidentally through the shared grid" was
   an overclaim**, and the code supports a stronger, opposite statement: nothing
   debits the grid, so momentum is *not* conserved across the interface.
3. **The DiffFR sentence was backwards.** See below.

Root cause, worth recording: the draft cited `kernels/mpm_utils.py` throughout
and **never opened `kernels/mpm_solver_warp.py`**, which holds the substep call
order, the rigid-mass construction and the contact resolver. The draft's header
claimed live-read coverage it did not have. Anyone revising this note must read
both files.

Three further sentences were **corrected, not merely copy-edited**. Recording
them so the change is not silently re-reverted:

- Draft: Akinci's boundary particles carry a "density-contrast-corrected
  volume". The abstract supports a correction for **inhomogeneous boundary
  sampling** ("considering the relative contribution of a boundary particle to a
  physical quantity"), which is a different correction from density contrast.
  Reworded to track the abstract. **Confirm against the full text**, since a
  density-contrast term does also appear in this literature and the two are easy
  to conflate.
- Draft: "no analogous derivative exists for a formulation that overwrites the
  body's velocity rather than accelerating it." **This was exactly backwards and
  a graphics reviewer would catch it on sight.** The map at `:1411` is *linear*
  in `grid_v_out`, with a closed-form Jacobian
  `d v_cm / d v_i = (1/M) Sum_p m_p w_i(x_p) I`, and the quadratic B-spline makes
  it C1 in particle position, so it is if anything *easier* to differentiate
  than a force-based scheme. My first rescue pass narrowed this to "no assembled
  force to differentiate", which is true but still incomplete. The two genuine
  obstructions are that the formulation exposes no applied force to serve as a
  control variable, and that the contact stage runs on the host as a NumPy round
  trip (`kernels/mpm_solver_warp.py:893-901`, `:982-987`), severing any
  device-side tape. Reworded to both.

- Draft: Akinci's exchange is "conservative by construction". Akinci's scheme
  includes **friction**, which is not conservative in the mechanics sense. The
  abstract's own word is "momentum-conserving". Changed to that.

## Citations

**[PUBLISHER RECORD]**, verified by DOI 2026-08-13. Neither carries a
retraction, correction, or expression of concern in the record returned.

[1] N. Akinci, M. Ihmsen, G. Akinci, B. Solenthaler, and M. Teschner,
"Versatile rigid-fluid coupling for incompressible SPH," *ACM Transactions on
Graphics*, vol. 31, no. 4, pp. 1-8, Jul. 2012, doi: 10.1145/2185520.2185558.

[2] Z. Li, Q. Xu, X. Ye, B. Ren, and L. Liu, "DiffFR: Differentiable SPH-based
fluid-rigid coupling for rigid body control," *ACM Transactions on Graphics*,
vol. 42, no. 6, pp. 1-17, Dec. 2023 (SIGGRAPH Asia 2023), doi:
10.1145/3618318.

The draft gave Akinci as **Aug.** 2012. The publisher record dates it
**2012-07-01**, consistent with ACM TOG 31(4) being the SIGGRAPH 2012 issue.
Corrected to July. The draft also omitted DiffFR's page range, now `1-17`.

BibTeX keys are **not** in `paper/can_it_ford_references_IEEE.bib`, and this
session could not put them there: `.claude/hooks/gate_protected_files.sh` denies
every write under `*/paper/*` unconditionally. The exact entries and the apply
command Josie needs are in `docs/PENDING_BIB_ENTRIES_2026-08-13.md`.

Scope correction to the draft's novelty claim: the draft said a live grep for
"akinci" across `docs/`, `paper/`, `citations/` and `CLAUDE.md` returned zero
hits. That is **true as scoped**, and both keys really are absent from the
`.bib`. But a whole-repo `/usr/bin/grep` on 2026-08-13 finds Akinci et al. 2012
already cited at `_inbox/Can It Ford? — Comparative Engine, Model, and GH200
Build-Feasibility Sweep for Vehicle-in-Floodwater Simulation.md:56`, for
rigid-fluid coupling in PositionBasedDynamics. So Akinci 2012 is new to the
**bibliography**, not new to the **project's reading**. Say it that way.

**KEY COLLISION HAZARD, caught on review.** There are **two different 2012
papers with an Akinci author** live in this repo. Besides the coupling paper
above, `analysis/render_multigeom_shaded.py:31`, `:270` and `:562` cite
"Ihmsen, Akinci, Akinci and Teschner 2012" for the foam/spray diagnostic, and
`.remember/vista_session_2026-08-12.md:138` cites the same for a Weber-number
criterion. A naive `akinci2012` key would collide with the foam citation and
invite readers to conflate them. **Use disambiguated keys**:
`akinciN2012coupling` for the rigid-fluid coupling paper, and `ihmsen2012foam`
if the foam paper is ever added. `docs/PENDING_BIB_ENTRIES_2026-08-13.md` has
been updated to the disambiguated key.

Neither SPlisHSPlasH nor DiffFR is installed or vendored, and neither is
proposed as a dependency. This note is reading and citation only.

## Agreement with CLAUDE.md's August 8 addendum

Checked explicitly, because a note that contradicted the addendum would be worse
than no note.

- **A-1.** The addendum already establishes Hu et al. 2018 CPIC
  (doi 10.1145/3197517.3201293) and Pazouki, Jayakumar and Negrut 2016 as the
  documented force-based alternative, and confirms material 8 IS the rigid
  material by three live source reads. This note agrees and adds no competing
  claim: it supplies the *mechanism* (which two kernels, and what they compute)
  behind A-1's architectural framing. Akinci and DiffFR are additional SPH-side
  citations, not replacements for Hu or Pazouki.
- **A-2.** The SDF-collider validation range is **7.3 to 7.7 percent**, never
  1.6 to 7.7. The stray 1.6 comes from the free-rigid late-window fit, which
  measures the path being criticised rather than the validated one. This note
  keeps the two apart and does not quote a merged range.

## Open, deliberately not resolved here

- Whether the material-8 averaging is *quantitatively* wrong for these runs is
  untested. It is structurally different from a force-based scheme; that is not
  the same as being inaccurate for a displacement verdict, and the paragraph
  above is worded to avoid claiming it. **A falsifiable test exists and was not
  run:** drive the same geometry through `simulation/coupling_force/` (the force
  path) and the material-8 path with everything else held fixed, and compare the
  displacement verdicts, not the magnitudes. Until that is run, "differs in kind"
  is the strongest defensible claim.
- The SDF-collider path validated to 7.3 to 7.7 percent against analytic
  buoyancy is a **different** path from the material-8 one used by the 17 runs.
  Do not present that validation as covering this coupling. Three further
  reasons it does not clear the 17 verdicts, per CLAUDE.md addendum A-1 and
  `docs/REGIME_LADDER_DISPATCH_2026-08-07.md:28-33`: that run used
  `restitution=0.0` on every surface where the 17 runs use 0.05, it resolves the
  water depth with 2 grid cells, and self-consistency is not validation. The
  review also reports that the g64 case settled cleanly while the g96 case hit a
  900-frame settle cap, so the two ends of the range would not be equally
  reliable. **I have not verified that g64/g96 split independently**; treat it
  as flagged, not established, and check it before quoting either end alone.
- **How weight and buoyancy reach the vehicle at all** is worth one sentence if
  this goes in the paper, because a reader cannot otherwise tell.
  `core/solver.py:168` sets `g = [0, 0, -9.81]` and
  `kernels/mpm_utils.py:935-940` applies it to every node carrying mass,
  including nodes carrying rigid-particle mass. So the body's weight and its
  buoyant response both arrive through the shared grid, not through any
  body-frame force term.
- **Run provenance is an open gap, not a disclosed limitation.** The review
  reports that `canitford_git_commit`, `grid_density`, `mesh_sha256`,
  `solver_git_sha` and `vehicle_mass` are absent from all 32 manifests. If any
  revision claims this note's solver reading is reproducible against the runs it
  describes, that claim fails until those fields exist. Not independently
  verified here.

## Owed elsewhere, deliberately NOT done here

Out of scope for this session by explicit instruction, and listed so they are
not lost:

- **No register entry** was added to
  `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.
- **No CLAUDE.md edit** was made.

Both are owed to DP-1's owner. The register entry that would be warranted is the
mechanism above: material 8 assigns `v_cm = linear_mom / M` at
`mpm_utils.py:1434`, forms **no hydrodynamic** force, and then applies contact
impulses on the host. Primary-source lines: `mpm_utils.py:1370`, `:1411-1412`,
`:1416`, `:1438-1439`, `:1463`, `:1490`, `:908-910`, `:1100`; and
`mpm_solver_warp.py:852-856`, `:887`, `:941`, `:957-977`, `:1344-1367`, `:1915`;
and `sim_standing.py:211`, `:214`.

A second register-worthy item surfaced during review and is **not** recorded
anywhere yet: register A3's allocation list for the rigid momentum accumulators
("`:497-502, 822-830`") appears to omit `:503-504` and `:831-832`. Flagged, not
independently verified here.
