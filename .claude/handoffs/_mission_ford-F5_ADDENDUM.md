# F5 ADDENDUM, 2026-07-25. Read this in full and apply it to docs/POSTER_ASSET_TABLE.md

This supersedes parts of your original mission file. Constraints are unchanged: read-only on data, no commits, no pushes, no GPU, no warpmpm import, no em-dashes.

## 1. CORRECT seed row 2. The framing was wrong, not just the number.

Do NOT describe the traction result as a 2.30x uncertainty band. That framing is retracted.

The correct framing: true traction is 3495.2 N and lies OUTSIDE the measured range entirely. All three resolutions understate it. This is a one-sided bias that shrinks with resolution, not a symmetric uncertainty band around a central value.

Understatement by resolution: 60 percent, 30 percent, 8.3 percent.

Why the distinction matters, and it must be visible in the row: a band implies the true value sits somewhere inside the measured spread, so refining resolution narrows uncertainty toward a midpoint. A one-sided bias means every measurement is wrong in the same direction and the true value is never bracketed. A reviewer reading "2.30x spread" would conclude the answer is somewhere in that range. It is not. It is above all of it.

Row 2 status stays unverified, blocker unchanged: awaiting one true-hull-volume number.

## 2. ADD row 4. Status VERIFIED, no blocker. This is now the most important row.

Track 2 null-result finding.

- Water x extent = [-1.975, -1.625]
- Vehicle x extent = [-1.330, 3.330]
- Gap = 0.295 m, and velocity = 0.0, so nothing ever closes it
- x_disp = 0.0000 m at every one of 500 logged steps
- Reported max_vel 0.8240 m/s is the vehicle's free-fall impact on the dry ground plane, not water loading. Vehicle center z = 0.755, half-height 0.72, bottom at 0.035 m, falls 0.035 m.
- Crash isolation is single-variable and clean: coup_softness = 0.002 was active and UNCHANGED in both runs. grid_density 64 ran 500/500 steps exit 0. grid_density 128 crashed with CUDA_ERROR_ILLEGAL_ADDRESS in p2g at step 1. The crash is isolated to grid_density. coup_softness is ruled out.

Plain statement for the row: every Track 2 FORD verdict ever produced is a 1390 kg box free-falling 3.5 cm onto dry ground beside a 0.189 m3 puddle it never contacted. It is a valid crash-isolation result and nothing more. It is not a forded crossing.

SOURCE, and note this carefully: logs/c0_crash_isolation_result_20260725.md exists on VISTA at /work/11603/jcerrell0629/vista/can-it-ford/logs/, 3010 bytes. It does NOT exist on the Mac. If you want to quote it you must ssh vista to read it. Do not record it as a local path in the table without that qualifier, or the next reader will look for it here and not find it.

PRECISION NOTE, include it, do not smooth it over. The claim is that max_vel 0.8240 equals sqrt(2 * 9.81 * 0.035). Computed exactly, sqrt(2 * 9.81 * 0.035) = 0.8287 m/s, while the measured value is 0.8240 m/s. That is a 0.6 percent difference. Inverting, 0.8240 m/s implies a drop of 3.461 cm rather than 3.500 cm. The source document itself is careful here and writes "sqrt(2*9.81*0.035) = 0.83 m/s. Matches." So the finding is sound and the free-fall signature is real. Phrase it as matching free-fall to within 0.6 percent rather than as an exact identity, because a reviewer who recomputes it will get 0.8287 and a poster that claims equality invites exactly that check.

## 3. RELABEL every asset that cites a Track 2 FORD verdict as RETRACTED. Not BLOCKED.

These two labels are not interchangeable and the distinction is the point.

- BLOCKED means the asset is waiting on a run that has not happened yet. The number could still turn out real.
- RETRACTED means the number was never real. No future run rehabilitates it, because the measurement did not measure what it claimed to measure.

Any asset resting on a Track 2 FORD verdict is the second case. The poster must not carry a BLOCKED label on a RETRACTED condition. Go through every row you have already written and every candidate C5 hands you, and apply this. Say in your handoff how many rows you relabelled.

## 4. Two contamination paths you must record, found in the source document

FIRST, the null run wrote into shared result files. Per the source document's own file list, that run appended to:
- data/track2_sweep/manifest.csv
- data/phase_space_results_mpm.csv

So both of those CSVs now contain a null-result row. Any asset whose data file is either of those inherits the contamination. Check live which assets read them and flag each one. Do not edit the CSVs.

SECOND, the retest script is on superseded physics. The source document flags, without acting on it, that VEHICLE_RHO = 115.7 with VEHICLE_SIZE = (4.66, 1.79, 1.44) gives 12.0116 m3 * 115.7 = 1389.7 kg, which is the superseded 1390 kg box target. The canonical value per the July 20 correction is 1100 kg via yaris_coarse_v1l_watertight.ply at rho 310.47. The document's own conclusion: fine for crash isolation, wrong for physics. Record that as a caveat on row 4 so nobody later mistakes the crash-isolation result for a physics result.

## 5. Then hold

Finish the table, write your handoff, print the complete table in your final chat message, and stop. Do not start new work. Do not commit. Do not push.

When finished, run: tmux wait-for -S ford-F5-done
