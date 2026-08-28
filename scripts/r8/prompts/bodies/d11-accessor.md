## YOUR SLOT: d11-accessor, branch `claude/r9-accessor`, worktree `.claude/worktrees/r9-accessor`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d11-accessor` first.

### The defect, established last night by slot d9-kramer and re-verified by the coordinator

`simulation/r5_physics/sphere_heave.py` emits TWO force accessors whose names differ by one word and whose denominators differ by roughly a factor of two:

- `fz_over_analytic_measured` divides by `analytic_buoyancy_at_measured_surface_N`
- `fz_over_analytic_nominal` divides by `RHO_W_BENCHMARK * G_ENGINE * (2/3 pi R^3)`

In job 918240 the measured denominator was 32.33 N, because the free surface had fallen 5.587 cm and the pinned sphere sat at draft 0.09413 m, only 31.4 percent of its diameter. The nominal denominator is 69.2180 N.

**They disagree on the SIGN.** Against nominal the run reads -29.11 to -9.67 percent. Against measured it reads +49.36 to +50.29 percent.

`docs/R5_PHYSICS_BATCH_MANIFEST.md` line 222 states criterion 3 as "The steady vertical reaction against 69.2180 N", so the manifest names the NOMINAL denominator. The source comment at `sphere_heave.py:669-670` says `fz_over_analytic_measured` "is the number job B should actually be graded on". Those two documents designate different quantities, and a published claim was built on the mismatch and had to be withdrawn.

Verify all of the above yourself from the live files before acting on any of it. I am handing you a diagnosis, not a fact.

### Why this is urgent rather than tidy

Manifest line 214: "Any FAIL stops the ladder." Job C is scheduled to be graded on this same template and has not run yet. Fixing the specification before job C is far cheaper than grading job C and then re-litigating which number was meant, which is exactly what happened to job B and cost a slot its headline.

### Your unit

1. Establish, from source and from the on-disk job outputs, exactly which accessor each of `grade_job_b.py` and the manifest actually uses. Do not assume they agree with their own prose.
2. Decide and WRITE DOWN which denominator criterion 3 should name, with the physical argument for it. A pinned sphere in a drained tank is not the same measurement as a nominal fully-submerged buoyancy, and the criterion has to say which one it means and over which window. Criterion 3 currently names no window, and the series is non-stationary at 8.52 sigma on the nominal accessor, so a window is not optional.
3. Make the code and the manifest agree. Renaming for clarity is in scope. Deleting an accessor is NOT: both quantities are meaningful, the defect is that the spec does not say which one it grades.
4. State plainly what this does to job B's recorded verdict. Job B FAILS criterion 3 at every window on the measured accessor. Whether it also fails on whatever you decide criterion 3 should name is a question you must answer explicitly rather than leave implied.

### Boundaries

`measure_surface` (around `sphere_heave.py:676-714`) deliberately excludes every particle within 2R of the sphere axis, which is exactly where the pressure generating `fz` acts. That is a real limitation of the surface estimator and it means a surface-estimator explanation for the discrepancy cannot be excluded by the current instrument. Sensitivity is about 0.0277 ratio-points per mm, so 18.1 mm of surface offset, 0.97 dx at g64, accounts for the entire +50 percent with zero physics error. You may document this. Do NOT rewrite the estimator in this unit; that is a separate change with its own validation burden.

You have NO GPU node. Everything here is source reading, on-disk job output, and specification writing. Do not propose a run as the first step.

Whatever you conclude about whether the ladder is stopped, that is Josie's decision to make and not yours to make for her. Give her the two honest options with the evidence for each.
