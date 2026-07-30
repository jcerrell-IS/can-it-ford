# Mission: pane F4, ford:0.4, 2026-07-25. Poster text blocks

## Hard constraints
1. Mac-local. Writing ONLY to docs/. NO commits, NO pushes. You are not the committer.
2. DO NOT READ vehicle_params.py. Another session is actively editing it.
3. Do not import warpmpm, do not run a simulation, do not request idev or GPU.
4. No em-dashes anywhere. No inline comments or docstrings.
5. Verify live. If a claim is not in the ledger as verified, do not write it.

## Task

Draft docs/POSTER_TEXT_BLOCKS.md, one block per required poster section, using ONLY findings carrying a verified status in docs/VERIFIED_FACTS_LEDGER_july24.md.

Required sections, per the program's own instructions:
- Title
- Authors, Department, School
- Introduction, which MUST name: full name, major and institution, the REU program, and the mentors by name
- Research Goal
- Methods
- Results
- Conclusion
- Acknowledgments, which MUST thank the National Science Foundation and UT Austin TACC and cite NSF REU Site Award #2447887 by that exact number
- References

Results may cite only these four, all verified:

1. Three-class AR&R L1 phase space, 70 cells, 12 class-sensitive.

2. Traction understated at every resolution: true 3495.2 N, measured 1391 / 2459 / 3204, bias 60 / 30 / 8.3 percent. This is a ONE-SIDED BIAS, not an uncertainty band. Frame it that way: the true value lies outside the measured range entirely, every resolution errs in the same direction, and the error shrinks with resolution. Do not write "2.30x spread" or anything implying the answer sits inside the measured range.

3. Geometry pipeline: 60k resample at vehicle.py:162, +117 percent over hull, and the n_grid=128 hollowing was a sampling limit not a resolution limit.

4. Track 2 null result: water sat 0.295 m from the vehicle at velocity 0, so no Track 2 FORD verdict ever represented fluid contact.

On item 4, one precision point. The supporting document reports max_vel 0.8240 m/s as a free-fall signature and writes sqrt(2 * 9.81 * 0.035) = 0.83 m/s, matches. Computed exactly that is 0.8287 m/s against a measured 0.8240 m/s, a 0.6 percent difference. The finding is sound. If you state the identity, phrase it as matching free-fall to within 0.6 percent rather than as an exact equality, because a reviewer who recomputes it will get 0.8287.

Write for a general audience with societal impact stated plainly. Five minutes spoken maximum. Include a Future Directions line.

Flag every place a number is still pending as [PENDING] so it is visibly incomplete rather than quietly wrong.

## Output
docs/POSTER_TEXT_BLOCKS.md and .claude/handoffs/2026-07-25_ford-F4.md.
When finished: tmux wait-for -S ford-F4-done
