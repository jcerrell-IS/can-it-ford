# Dispatch: close the regime gap between C1 and the 17 gated runs

Written 2026-08-07 ~19:35 by a chat-side session, for a fresh Claude Code
session to execute. Read this file in full before doing anything. This file
is a plan, not an authority. `docs/C1_ROOT_CAUSE_2026-08-07.md` and
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` outrank it if they
disagree with anything below.

## 0. Why this exists

`docs/C1_ROOT_CAUSE_2026-08-07.md` [READ, T1 for that session] established:

- The C1 "sinks not floats" headline (-122%/-326%) was a `np.polyfit`
  measurement artifact, not a real defect. The polyfit closed-form claim in
  its section 2, `slope = 6*dV/(dt*(N+1)*(N+2))` for a step at sample 1 over
  window `0..N`, was checked symbolically for N=1 through 8 by this chat
  session using the Wolfram Language and matches exactly, zero residual at
  every N. That is now independently confirmed, not just internally
  consistent.
- The clean number (late-window fit) is positive: +1.5% and +0.7-0.8% of
  analytic buoyant acceleration at g64/g96. Weak, right direction.
- An SDF-collider run (894731) gives the project's first externally-validated
  force measurement, within 7.3-7.7% of analytic buoyancy. The grid physics
  is roughly right. The free-rigid body simply does not consume it, because
  it has no force or inertia term, its velocity is a mass-weighted grid
  average recomputed from scratch every substep.
- This does **not** clear the 17 published verdicts. Three reasons why, all
  in that doc's section 8: different restitution (17 runs have 0.05 on floor
  and walls, C1 has 0.0 everywhere, which the coupling code makes invisible
  to the rigid body); 2-grid-cell depth resolution; self-consistency is not
  validation.
- Section 8's own prescribed close: walk the regime one variable at a time
  from C1 toward the gated scene. (a) fully submerged, still, no planes
  [done, this is C1]. (b) partially submerged, still, no planes [not done,
  do not skip]. (c) partial + floor restitution 0.05 [not done]. (d) add
  flow [not done].

This dispatch is (b), (c), (d), plus two small fixes the doc's section 9
already specified.

`docs/FLAG_topple_accel_risk_2026-08-07.md` [written by the chat session]
additionally flags that `simulation/failure_modes.py`'s TOPPLE classification
gates directly on `surge_accel_g`, exactly the forbidden quantity. That is a
separate, already-flagged problem. This dispatch does not fix it. Do not
conflate the two.

## 1. Concurrency, read this before touching anything

This repo had 7 to 10 live Claude Code sessions in it as of today, sharing
one working tree. Two things already went wrong once each, both documented:

- `docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md`: one session's `git add -A`
  swept another session's uncommitted edits into its own commits, unreviewed.
- A `git worktree prune` earlier today wiped 28 worktree registry entries.

Rules, non-negotiable for this dispatch:

1. Read `docs/SESSION_CLAIMS.md` in full before any write. It is a
   convention, not a lock, per its own header, but read it anyway.
2. Append your own claim block to `docs/SESSION_CLAIMS.md` before starting.
   Claim `simulation/validate_coupling_force_ladder.py` (new file, see
   section 3) and this file's own follow-on sections. Do not claim
   `simulation/validate_coupling_force.py` or `docs/C1_ROOT_CAUSE_2026-08-07.md`.
3. `git status -sb` first. As of this writing, `.claude/checks/params_check.py`,
   `docs/C1_ROOT_CAUSE_2026-08-07.md`, and `simulation/validate_coupling_force.py`
   are modified and uncommitted by another live session. **Do not edit these
   three files.** Check again live, this state moves fast.
4. Never `git add -A` or `git commit -a`. Stage explicit paths only.
5. Only one session submits Vista jobs at a time. Claim `VISTA: mine` in
   `docs/SESSION_CLAIMS.md` before the first `sbatch`. Use `sbatch`, never
   `idev`, for every run in this dispatch. Recalled but not re-verified this
   session: Vista had roughly 670 SU left as of an earlier session today,
   against 9644 on LS6, and most of today's burn came from idle interactive
   sessions rather than batch jobs. Check the live balance yourself
   (`/usr/local/etc/taccinfo` or the TACC portal) before assuming headroom.
6. Do not touch `run_c1_sdf` and its helpers (`cube_mesh`, `sdf_margin_cells`,
   `build_box_sdf`) if you find them. Section 9 of C1_ROOT_CAUSE.md records
   they exist in no commit as of HEAD `9d53acc`. They are the only
   externally-validated result in the project. Check whether they have since
   been committed (`git log --all --oneline -- simulation/validate_coupling_force.py`
   for a commit touching those symbols); if still uncommitted, say so loudly
   in your own session output and do not let anything you do risk them.

## 2. Provenance discipline for this dispatch

Tag every number you produce T1 (you read it), T2 (you measured it on
Vista), or T3 (you derived it). No untagged claims. When section 8's ladder
is closed, write the result as an ADDITIVE new file, do not edit
`C1_ROOT_CAUSE.md` or `COUPLING_VALIDATION_J1_2026-08-07.md` directly, both
are owned by other sessions as of this writing. Name it
`docs/REGIME_LADDER_RESULTS_2026-08-0X.md` with the actual date. Promote into
the register only after ownership of the register is settled, per
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`'s own header if it has one.

## 3. The ladder, rungs (b), (c), (d)

Implementation location: a new file, `simulation/validate_coupling_force_ladder.py`,
that imports whatever helpers it needs from `simulation/validate_coupling_force.py`
(read-only import, do not edit that file) and from `renders/yaris_render_s1/sim_standing.py`
for the actual 17-run configuration values (floor friction 0.55, wall
restitution 0.05, floor restitution, the velocity-clamp mechanism). Read both
files fully before writing anything. If an import fails because the target
file changed shape under you, re-read it, do not guess its current interface.

For every rung, before treating a result as usable:

- The run must reach `settle_gate_met=True` before the measurement window
  starts. Section 4 of C1_ROOT_CAUSE.md found the g96 comparison in C1 was
  invalid for exactly this reason (unsettled, still moving at 2.13 m/s at
  release). Raise `frames` cap to ~1200 if needed. A cap-hit is a discard,
  not a result. Say so explicitly if it happens, do not report it as data.
- Use `a_late_window` as the headline number, not the raw first-N-samples
  polyfit. Section 6 of C1_ROOT_CAUSE.md item 3 explains why the early
  window is the contaminated one. If you add a new headline metric, compute
  it the same way: exclude the release transient, fit the second half of the
  window.
- Run at both g64 and g96 for every rung. Report both. Do not average them
  into a single number, the project already has one unresolved open item
  about why they differ (section 9's 7.59x dV ratio) and that question stays
  open here too, note it rather than paper over it.

### Rung (b): partially submerged, still water, no planes

Modify the spawn so the rigid body floats at the free surface rather than
fully submerged (matching C1's existing submerged-spawn pattern from commit
`2cdf618`, but at partial depth instead). Still water (no velocity clamp,
no inflow). All planes at restitution 0.0, matching C1, so this rung isolates
exactly one variable: submersion fraction.

Acceptance: report `a_late_window` at both grids, plus whatever waterline
diagnostic is cheapest to add (fraction of body volume below the local water
surface, if that number is already available from the existing buoyancy
check pattern in `sim_standing.py`, do not invent a new one).

Section 8b of C1_ROOT_CAUSE.md already has a closely related partial-immersion
result from job 895448's heave-oscillation trace. Read that section before
starting this rung, you may be able to reuse its geometry rather than
re-deriving from zero. If you do reuse it, cite the job ID and say so.

### Rung (c): partial submersion, floor at restitution 0.05

Same as (b), but the floor plane now carries `restitution=0.05`, matching
the 17 gated runs (`renders/yaris_render_s1/sim_standing.py`, confirm the
exact value live rather than trusting this number, read the file). Side
walls stay at whatever (b) used; only change the floor. This isolates the
second variable named in C1_ROOT_CAUSE.md's objection 1: the mechanism at
`mpm_solver_warp.py:1915`, `if restitution != 0.0`, which makes a
restitution-0.0 plane invisible to the rigid body and a nonzero-restitution
plane NOT invisible. C1 could not have exercised this path at all. This rung
is the first one that can.

Acceptance: same as (b), plus explicitly note whether `_apply_rigid_restitution`
fires (it should, now) and what its measurable effect on the late-window
acceleration is, comparing directly against rung (b)'s number at the same
grid.

### Rung (d): add flow

Same as (c), but add the velocity-clamp mechanism from `sim_standing.py`
(read `_sustain_inflow` there, re-implement or call it, do not guess its
signature). Use the depth and velocity from one of the 17 canonical runs so
this rung is directly comparable to a real published case, not an arbitrary
new point. State which run (which mass class, which velocity) you matched.

Acceptance: same as (b) and (c), plus a direct statement of whether the
late-window buoyant response measured here, under the SAME restitution and
flow conditions as a real published run, is consistent in sign and rough
magnitude with what that published run's displacement data implied. This is
the actual closing comparison the whole ladder exists to produce.

## 4. Two independent small fixes, do these regardless of ladder progress

Both are specified precisely enough in `C1_ROOT_CAUSE.md` section 9 that
they do not need design work, only implementation. Do them in the new file
(or, if truly minimal and you are certain no other session is mid-edit on
the exact lines, as a tightly scoped patch to the owning file, checked
immediately before and after).

**Fix A: C3's estimator.** Section 9: `run_c3` reports
`a_as_fraction_of_g` from `a_headline_first3`, the same contaminated
early-window estimator section 2 discredits. For a null test this is worse
than for C1, because C3's pin injects a nonzero `dV` by construction, so it
reads nonzero even with perfect coupling. Switch it to use `a_late_window`,
which `run_c1` already computes. Do not touch `a_expected_compressible`,
section 9 says it is assigned once and read by nothing, that is a separate,
lower-priority cleanup.

**Fix B: the P2G guard's error message.** Section 8b: `core/solver.py:506`
computes `g = x[:, 1:] if self.periodic_x else x`, checks all three axes,
but the raised message hardcodes the label `"x"` regardless of which axis
actually tripped. Section 8b's own open item: "the identity of the tripping
particle is UNKNOWN" for C2's crash, specifically because this message does
not say which axis or which material. Print `x.min(0)` per axis and the
material of the argmin particle before the raise, matching the same
diagnostic pattern C1_ROOT_CAUSE.md recommends. This directly unblocks C2's
open question about whether the tripping particle is water, hull, or a
rotated corner.

## 5. What NOT to do

- Do not extend this ladder's conclusions to the 17 published verdicts
  yourself. Report rung (d)'s result plainly. Whether it changes any
  verdict is a decision for whoever owns the register, not this dispatch.
- Do not touch `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` or
  `docs/COUPLING_VALIDATION_J1_2026-08-07.md` directly.
- Do not start the Kumar in/outflow-BC implementation or the Bingham/
  Herschel-Bulkley rheology sweep as part of this dispatch. Both are real
  and both are documented elsewhere (`CLAUDE.md` v8 Part 3.5;
  `docs/UNEXPLORED_AREAS_ASSESSMENT_2026-08-07.md`; a worktree
  `claude/bingham-material-sweep-2026-08-07` already has partial results in
  `analysis/bingham_sweep/bingham_sweep_results.csv` per an earlier session's
  summary, not independently confirmed by this dispatch). They build
  interesting physics on top of a coupling path this ladder has not yet
  finished validating. Sequence matters: close this gap first. If rung (d)
  closes cleanly, that is the point to open a fresh dispatch for either of
  those, not before.
- Do not report a number without its grid, its window, and its settle-gate
  status attached.

## 6. Deliverable

`docs/REGIME_LADDER_RESULTS_2026-08-0X.md`, additive, provenance-tagged,
containing: rung (b), (c), (d) results at both grids with settle status;
Fix A and Fix B confirmed working, with a before/after example of the guard
message for Fix B; an explicit statement of which published run rung (d)
was matched against and how close the comparison came; and an explicit,
separate paragraph on what remains open (the 7.59x dV grid ratio; whether
this generalizes to a moving, not-yet-topped-out vehicle rather than a
uniform cube or box).

## 7. Check before you start

1. `git status -sb`, confirm the three protected files' state.
2. `git log --all --oneline -- simulation/validate_coupling_force.py | grep -i sdf`,
   confirm whether `run_c1_sdf` has been committed since HEAD `9d53acc`.
3. `cat docs/SESSION_CLAIMS.md`, confirm no other session already claims
   this exact work.
4. TACC SU balance on Vista, live, not recalled.

If any of those four surprise you, stop and report the surprise before
writing code. That is the whole point of this section.
