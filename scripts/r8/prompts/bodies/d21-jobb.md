## YOUR SLOT: d21-jobb, branch `claude/r9-jobb-route`, worktree `.claude/worktrees/r9-jobb-route`

Preflight, then go straight to work. No scope-confirmation gate.

## THE SITUATION, AND YOUR JOB IS TO DECIDE THE ROUTE

Slot d11-accessor has established, by recomputing from raw geometry rather than transcribing, that **Job B FAILS criterion 3 at 24 of 24 gradings**: six runs times four windows, +34.4 to +64.2 percent. The implementation reproduces the emitted ratios to machine precision and the nominal denominator recomputes to 69.217987 N against the manifest's 69.2180. **The code was never in question. One implementation, three disagreeing prose statements.**

`docs/R5_PHYSICS_BATCH_MANIFEST.md:214` says "Any FAIL stops the ladder." Job C has not run and was scheduled to reuse this template.

The coordinator's judgement is: accept the FAIL and stop the ladder, because the error is three to six times any defensible band. **But the FAIL does not localise the defect, and that is your unit.**

## THE HYPOTHESIS NOBODY HAS TESTED, AND IT CAN EXPLAIN EVERYTHING WITH ZERO PHYSICS ERROR

`simulation/r5_physics/sphere_heave.py`, function `measure_surface`, **excludes every particle within 2R of the sphere axis.** Confirmed live. That annulus is exactly where the free surface is deformed by the body and where the pressure generating `fz` acts, so the near-field surface is unmeasured BY CONSTRUCTION.

Sensitivity is roughly **0.0277 ratio-points per millimetre**. An **18.1 mm** surface offset, about **0.97 dx at g64**, accounts for the ENTIRE +50 percent with no solver error at all.

So there are three live explanations and nobody has separated them:
1. **The denominator is wrong** because the surface estimator is biased by its own exclusion.
2. **The force is genuinely over-predicted** by the weakly-compressible scheme.
3. **The force is contaminated** by the contact or restitution treatment rather than being a clean pressure integral. Note `_apply_rigid_restitution` is live at restitution 0.05 in all 17 canonical runs.

## YOUR UNIT: DESIGN AND RUN THE TEST THAT DISTINGUISHES THEM

1. **Read `measure_surface` in full** and establish whether the 2R exclusion is a defect or a deliberate trade. The docstring says the annulus "carries the..."; read the rest and quote it.
2. **Vary the exclusion radius** and see whether the ratio moves as the sensitivity predicts. If the ratio tracks the estimator, explanation 1 is confirmed and the criterion is measuring the instrument rather than the solver. This is the cheapest decisive test available and it may run on existing data.
3. **A no-body control**: measure the surface with the same estimator and no sphere present. Any offset there is pure estimator bias.
4. **Check whether the restitution path contributes**, by whatever means is cheapest. Do not assume it does or does not.

A deep search is running for exactly this question, "free surface elevation estimator error in particle method buoyancy validation", in Undermind workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`. **Check whether it has completed before you design your tests**; it was commissioned to find how other groups measure free-surface elevation near a body and whether anyone has quantified estimator-induced error in a force ratio.

## RESOURCES

A GPU node may still be live: job 922255, `srun -p gh -N 1 -n 1 -t 00:20:00 --overlap --jobid=922255 <cmd>`, all five flags required. Check `squeue` first. **If it has expired, submit a BATCH job rather than waiting for another interactive window**: 605 SUs remain on BCS20003 and this project has historically burned 98.5 to 99.1 percent of its node-hours interactively with 95 of 184 runs ending in TIMEOUT.

## DEFINITION OF DONE

`docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md` stating: which of the three explanations the evidence supports, what test decided it, and therefore whether the FAIL is a solver defect or an instrument artifact. Then the recommendation for job C, which is Josie's decision to take or leave.

**If your test shows the estimator explains it, say so even though it overturns a verdict two sessions have now committed.** Write the result the same way whether it confirms or overturns.

Do NOT edit `sphere_heave.py`, `grade_job_b.py`, the manifest, or `r7_jobb_bcfix_ab.py`. d11-accessor owns the first three and the fourth belongs to another branch. You write your document and your own test script only.
