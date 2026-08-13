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
  individually, not trusted from the draft.
- **[PUBLISHER RECORD]** The two external papers were verified 2026-08-13 by DOI
  lookup against the publisher record (scite MCP). Both are **closed access** and
  **neither was read in full**, so every characterisation of them is
  abstract-level. Verify before the paragraph ships. Exact fields and two
  corrections: `docs/PENDING_BIB_ENTRIES_2026-08-13.md`.
- **[ENGINE TAG]** Everything here describes **warpmpm**, the engine behind all
  17 gated runs. None of it describes Genesis, which is the abandoned box-proxy
  path and has never loaded the Yaris hull.

## What the 17 gated runs actually do

The vehicle is material 8. Its coupling is two kernels.

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

So the body's new linear velocity is the **mass-weighted average of the grid
velocity sampled at its own particles**, and its angular velocity is the
corresponding average angular momentum divided through by the inertia tensor.
The velocity is *assigned*, not incremented by an acceleration: `:1434` is a
plain write of `v_cm_new`, with no `+=` and no `dt` on the right-hand side.

Three consequences follow directly, and they are the substance of the
limitation:

1. **No force is ever formed.** There is no `dp/dt`, no pressure integral over
   the hull, no contact-force accumulator on this path. This is the mechanical
   reason register A3 records that no force accessor exists here: there is no
   internal quantity that *is* the hydrodynamic load, so none can be exposed.
   Reported drag or buoyancy on this path would have to be inferred from the
   body's kinematics after the fact, not read from the solver.
2. **The exchange is a momentum mixing, not an action-reaction pair.** Rigid
   particles carry mass and momentum into P2G but contribute no stress
   divergence (`kernels/mpm_utils.py:1090`, "stationary / rigid, no
   deformation"), so the fluid feels the body only as occupancy and momentum on
   the grid. Newton's third law is satisfied through the shared grid rather than
   by construction through an explicit equal-and-opposite force pair.
3. **The inertia tensor is used, but only as a divisor.** `omega` comes from
   inverting `I_world` against an averaged angular momentum, so the tensor
   shapes the response without any torque ever being computed. Note this does
   *not* make the rotational dynamics wrong: a momentum formulation carries the
   gyroscopic term implicitly by storing angular momentum. The point is that no
   torque is available to report, not that the body tumbles incorrectly.

**[READ LIVE]** A force-capable path does exist in the same file. The CPIC
implementation of Hu et al. 2018 at `kernels/mpm_utils.py:636-646` accumulates a
genuine rigid impulse. That block's own header states it: "the rigid impulse
accumulates during G2P from the ghost substitution, `m w (v_p - ghost)`, the same
quantity Section 5.4 accumulates on the P2G side". **The 17 gated runs do not use
it**; they use the material-8 path above. The distinction matters and should not
be blurred.

## The contrast, for the limitations paragraph

> The vehicle in this study is coupled to the flow at the velocity level: each
> substep the body's linear and angular momentum are set to the mass-weighted
> average of the background grid velocity sampled at its own material points,
> and its pose is integrated from that. No hydrodynamic force or torque is ever
> assembled, which is why the solver exposes no force accessor and why drag and
> buoyancy on the vehicle can only be inferred from its trajectory rather than
> measured directly. This differs in kind, not merely in accuracy, from the
> force-based two-way formulation that is standard in the SPH literature.
> Akinci et al. [1] sample the rigid surface with boundary particles whose
> contribution is corrected for inhomogeneous sampling, compute hydrodynamic
> forces on the fluid from those particles, and apply the summed reaction force
> and torque back to the body, so the exchange is momentum-conserving by
> construction and the instantaneous load on the body is a directly reportable
> quantity. Li et al. [2] build on that same force-based structure and show that
> its gradients with respect to rigid-body state can be computed stably and
> cheaply, which is what makes fluid-driven rigid control tractable; on a
> velocity-overwrite formulation there is no assembled force with respect to
> which such a gradient could be taken, so the quantity their method
> differentiates does not exist here. The practical consequence for the present
> results is that the reported outcome is a displacement verdict, not a force
> measurement, and the coupling itself remains unvalidated against an analytic
> or experimental load.

### Wording changes made during rescue, and why

Two sentences in the draft were **corrected, not merely copy-edited**. Recording
them so the change is not silently re-reverted:

- Draft: Akinci's boundary particles carry a "density-contrast-corrected
  volume". The abstract supports a correction for **inhomogeneous boundary
  sampling** ("considering the relative contribution of a boundary particle to a
  physical quantity"), which is a different correction from density contrast.
  Reworded to track the abstract. **Confirm against the full text**, since a
  density-contrast term does also appear in this literature and the two are easy
  to conflate.
- Draft: "no analogous derivative exists for a formulation that overwrites the
  body's velocity rather than accelerating it." **This was too strong and would
  not survive review.** An overwrite map is still a differentiable function of
  its inputs, so a derivative plainly exists. What is actually true is narrower:
  there is no assembled force on this path, so the specific object Li et al.
  differentiate is absent. Reworded accordingly.

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
rigid-fluid coupling in PositionBasedDynamics, plus an overlapping-author paper
at `.remember/vista_session_2026-08-12.md:138`. So Akinci 2012 is new to the
**bibliography**, not new to the **project's reading**. Say it that way.

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
  Do not present that validation as covering this coupling.

## Owed elsewhere, deliberately NOT done here

Out of scope for this session by explicit instruction, and listed so they are
not lost:

- **No register entry** was added to
  `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.
- **No CLAUDE.md edit** was made.

Both are owed to DP-1's owner. The register entry that would be warranted is the
mechanism above: material 8 assigns `v_cm = linear_mom / M` at
`mpm_utils.py:1434` and forms no force, with `:1370`, `:1411-1412`, `:1416`,
`:1438-1439` and `:636-646` as the primary-source lines.
