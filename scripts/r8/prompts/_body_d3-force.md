# SLOT d3-force

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-force, branch claude/r8-force
(off claude/r5-physics).

You may write ONLY:
  analysis/r8_noforcing_control.py   (new)
  docs/R8_FORCE_ROUTE_2026-08-18.md  (new)

NEVER TOUCH: renders/yaris_render_s1/sim_standing.py; the pinned engine under third_party/;
any other branch or worktree; the main checkout.

## THE TRAP. THE OBVIOUS VERSION OF THIS TASK WAS DONE AND RETRACTED WITHIN A DAY.
Read it first:
  git -C /Users/josie/can-it-ford show claude/r5-research:docs/R5_RESEARCH_FORCE_CONVERGENCE_2026-08-19.md
Its finding, verified from the pinned solver source, is not to be re-litigated:

  M * dv_cm/dt IS NOT A FORCE on the free-rigid material-8 path. v_cm is OVERWRITTEN, not
  integrated. mpm_utils.py:920-923 scatters every particle including rigid material 8 into the
  same grid_v_in/grid_m; :935-941 forms a mass-weighted water plus rigid mixture; :1402-1409
  interpolates that mixed field back at each rigid particle; :1434 assigns
  v_cm_new = rigid_linear_mom/M. No force accumulator exists for the body.

  Plausibility check that should have stopped it: peak_all at g48 is 32552 N, 1.42x the vehicle
  weight of 2337*9.81 = 22926 N, and 36 to 58x a drag anchor 0.5*rho*Cd*A*v^2 = 566 N at Cd=1,
  A=0.5028.

  Three confounds monotone with refinement, none controlled: substeps rise 2.6x from g48 to
  g128; no level resolves the flow depth by more than 4.1 cells; realized_rho varies 642.8 to
  663.6, so even the M being multiplied is not constant along the ladder.

AND THE RETRACTED QUANTITY IS ALREADY SHIPPED ON DISK. data/failure_modes_by_run.json -> runs
carries `peak_surge_force_n`, `peak_vertical_force_n` and `peak_surge_accel_g` for all 17 runs,
written by failure_modes.py:129-131 `force = mass_kg * np.gradient(vel)`. Read live this session:
  g48_m2337 32551.7 N, g64_m2337 31240.5, g96_m2337 26825.4
  g48_m1100 21389.5 N, g64_m1100 20411.6, g96_m1100 19949.7
  peak_surge_accel_g on the 1100 kg arm reads 1.8 to 2.0 g.
A 1100 kg car in 0.29 m of water at 1.5 m/s does not experience 2 g of horizontal acceleration.
Register D6f already condemns `peak_surge_accel_g` by name as "numerical, not physical. It is
np.gradient(vel, t) over a 30 Hz rigid-body trace." DO NOT BUILD A HEADLINE ON THESE.
What MAY survive is the sign-only observation that all three mass arms are monotone DECREASING
under refinement, stated as a property of a numerical artifact, never as a force.

## WHAT YOU ARE ACTUALLY DOING
Item 2 of that document's own section 5, the cheapest discriminator in the project, never run:
THE NO-FORCING CONTROL. Specify a `--velocity 0` run at each grid of the ladder. If the
"converging" curve still moves 20 to 35 percent with no flow at all, it is PIC reprojection
noise and nothing else. You cannot execute it (GPU), so your deliverable is the run
specification, the analysis script that will grade it, both self-tested on the Mac against
existing data, and the PRE-REGISTERED prediction written before any data exists.

ALSO IN SCOPE, Mac-only: `sdf_wrench` is the correct independent force measurement and it
EXISTS. Find it (`/usr/bin/grep -rln sdf_wrench` under simulation/ on claude/r7-collect) and
write up exactly what it accumulates, on which code path, and what a force-vs-resolution curve
built from it would require. Five documented traps fail silently: wrench-dt, the accumulator,
quaternion order, COM offset, periodic_x.

## THE RESEARCH
- ~/Downloads/"Particle Resolution and Force Convergence for Rigid Bodies in Flood-Type Flows-
  A Critical Review.md", recommendation 3 verbatim: report peak and time-integrated
  drag/lift/moment at each of at least three resolutions and the percentage change between
  successive levels, declaring convergence only below a stated tolerance (5 to 10 percent is
  defensible), and "This is currently rare and would materially improve the literature."
  Recommendation 6: such a curve for a vehicle would REPLACE the field's rules of thumb.
  IT IS A SECONDARY, AI-GENERATED SOURCE. Positioning only, never a primary result.
- Its own caveat, the honest novelty framing: "Vehicles specifically are under-studied with
  particle methods... The most detailed flooded-vehicle force work is CFD/VOF (Al-Qadami et al.,
  2023), not particle-based."
- Syamlal, Celik & Benyahia 2017, 10.1002/AIC.15868: refinement does not converge an
  instantaneous quantity. Report a time-averaged observable over a demonstrated-stationary
  window with a GCI. Celik et al 2007, 10.1115/1.2960953, is already in the paper bib.
- Run provenance is weak, say so: canitford_git_commit, grid_density, mesh_sha256,
  solver_git_sha and vehicle_mass are ABSENT from all 20 R6 repeat manifests.

## FIRST STEP
Verify the four solver line citations yourself against third_party/ and say whether each
resolves. Do not take them on the document's word.

## DEFINITION OF DONE
1. A no-forcing control specification with a PRE-REGISTERED prediction and a pass/fail rule
   written before any data exists.
2. A self-tested grading script that runs on the Mac (uv for numpy).
3. A written verdict on whether sdf_wrench can carry the curve, naming the code path and traps.
4. An explicit statement that M*dv/dt is not available and that the on-disk peak_surge_force_n
   IS that quantity, so the next session cannot rediscover the retracted route.
