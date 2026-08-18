# R7: both floor-leak fixes work, neither rescues Job B

Jobs 918450 (engine one-liner) and 918461 (sacrificial sub-floor) are collected and
graded against the predictions written in their own run scripts BEFORE they ran.
All numbers below come from the run JSONs fetched live from Vista.

## 1. Job 918450, the engine one-liner. Prediction confirmed on all three branches.

`run_jobBbc.sh` pre-registered three falsifiable branches: `n_below_floor` should
FALL but not vanish; the surface drop should shrink by roughly 1.8 cm of 5.6; and
`fz_over_analytic_measured` should move toward 1.0 without reaching it. It also
named the refutation: "If the leak is UNCHANGED the defect-2 hypothesis is refuted.
If it vanishes entirely, the mass-deficiency story was wrong."

| quantity (mean of last 20 of 200 frames) | control 918240 | bcfix 918450 | change |
|---|---|---|---|
| `n_below_floor`, final | 26964 | 1002 | **-96.28 %**, did not vanish |
| floor crossings, final minus frame 0 | 24716 | 1002 | **-95.9 %** |
| `surface_drop_m` | 0.055335 | 0.032338 | -2.300 cm of 5.533 cm, **-41.6 %** |
| `fz_over_analytic_measured` | 1.50056 | 1.34355 | +50.06 % to **+34.35 %** |
| `n_outside_walls`, final | 14423 | 15868 | +10.0 % |

**Branch 1 fired: fell, did not vanish.** Branch 2 predicted 1.8 cm and got 2.3 cm,
the right order and direction, somewhat larger. Branch 3 fired: it moved 0.157
toward 1.0 and did not arrive.

### The A/B is valid on the engine axis, and I verified it rather than assuming it

- `diff` of the two engines returns exactly one line: `1955c1955`,
  `if dotproduct < 0.0:` becomes `if dotproduct <= 0.0:`.
- The treatment `.out` records `ENGINE=$WORK/mpm-engine-bcfix-src` and sha256
  `2309d8a2358d693e...`, against the pinned engine's `285139395097a914...`.
- Particle count is 598505 in both.

**A GAP I FOUND, AND THEN CLOSED.** The run script claims the runs are "identical in
EVERY respect except the engine". The configs are not: the treatment carries six keys
the control lacks (`band_m`, `band_mult`, `ghost_depth_m`, `n_ghost_layers`,
`sdf_band_exceeds_bspline_halfwidth`, `sdf_band_over_dx`), so the treatment used a
NEWER `sphere_heave.py`. Every one of those keys sits at an inert default:
`n_ghost_layers = 0`, `ghost_depth_m = 0.0`, `band_mult = 1.0`,
`sdf_band_over_dx = 1.0`, and `band_m = 0.01875` which is exactly `dx = 1.2/64`, the
engine's documented default.

That is suggestive, not proof, and the control did not record its scene sha. **Job
918461 closes it by accident.** Its `ghost0` arm runs the PINNED engine with the NEW
scene at `--ghost-layers 0`, so it is the missing cell of the design. Over the 200
frames the two overlap:

| quantity | max abs difference, control 918240 vs ghost0 |
|---|---|
| `fz_N` | 0.00122 N against a ~104 N signal, 1.2e-5 relative |
| `n_below_floor` | 6 of ~27000, 0.02 % |
| `surface_drop_m` | 5.0e-6 m of 0.055 m, 0.009 % |
| `water_z_min_m` | 1.5e-7 m |

That is run-to-run nondeterminism, not a systematic offset. **The scene change is
inert, so the boundary A/B's only effective variable really was the engine line.**

### A provenance defect worth fixing

The treatment JSON's `provenance.pinned_sha` reads `544c93dd02cb9c7ead89e...`, the
PINNED engine, while the run used the bcfix engine. It is a hardcoded string in the
scene script, not a live read of the engine actually loaded. Nothing is lost because
the `.out` carries the true sha, but the JSON is self-misdescribing and any later
reader grading from the JSON alone would attribute the result to the wrong engine.

## 2. Job 918461, sacrificial sub-floor. It works, and the obvious metric inverts the answer.

Clean internal A/B: same pinned engine, scene sha checked in-script against an
expected value and matching, 300 frames, `--ghost-layers 0` against `3`.

**THE RAW METRIC SAYS THE FIX MADE THINGS WORSE, AND THAT IS AN ARTIFACT.**

| quantity, mean of last 20 of 300 | ghost0 | ghost3 | raw change |
|---|---|---|---|
| `n_below_floor` | 29171 | 38194 | **+30.9 %** |
| `n_outside_walls` | 15022 | 17550 | +16.8 % |
| `occupied_volume_m3` | 0.491815 | 0.528913 | +7.5 % |
| `surface_drop_m` | 0.061501 | 0.038608 | **-37.2 %** |
| `fz_over_analytic_measured` | 1.512162 | 1.380285 | **-8.7 %** |

`n_ghost_layers = 3` seeds 34321 extra particles BELOW the nominal floor, so
`n_below_floor` counts them by construction. Its frame-0 value is 34347 in the ghost
run against 2248 in the control. **Comparing the raw counts compares a seeding choice,
not a leak.** This is the same trap the handoff flagged for `measure_surface`, in a
different column.

**The quantity the fix actually targets is crossings of the nominal floor DURING the
run**, that is `n_below_floor(t)` minus each run's own `n_below_floor(0)`:

| frame | ghost0 crossed | ghost3 crossed | change |
|---|---|---|---|
| 50  | 14363 | 974  | -93.2 % |
| 100 | 19876 | 1600 | -92.0 % |
| 200 | 24753 | 3158 | -87.2 % |
| 299 | 27106 | 3909 | **-85.6 %** |

As a fraction of each run's own real water (598505), floor crossing at frame 299 goes
from **4.529 % to 0.653 %**. The sacrificial sub-floor works, and the mass-deficiency
hypothesis it was built on survives its own test.

## 3. THE HEADLINE: neither fix rescues Job B, and the ladder stays stopped

`fz_over_analytic_measured`, the accessor `sphere_heave.py:669-670` designates as the
number Job B should be graded on. Manifest bands: <=10 % PASS, 10 to 25 %
REPORTABLE PARTIAL, >25 % FAIL.

| run | fix | `fz_over_analytic_measured` | band |
|---|---|---|---|
| 918240 | none, control | +50.06 % | FAIL |
| 918450 | engine `<=` | +34.35 % | **FAIL** |
| 918461 ghost0 | none | +51.2 % | FAIL |
| 918461 ghost3 | 3 sub-floor layers | +38.0 % | **FAIL** |

**Both fixes move the error by roughly 13 to 16 points and both leave it far outside
even the REPORTABLE PARTIAL band.** So the boundary defects account for about a third
of the discrepancy and something else accounts for the rest. R6's conclusion stands
unchanged: Job B FAILS its pre-registered criterion, and per `MANIFEST:214` the ladder
is stopped. Job C stays gated.

**The cheap experiment nobody has run: the two fixes IN COMBINATION.** They address
different defects (an unconstrained node exactly on the plane, and missing mass below
the free surface), they are independent, and each on its own recovers a similar
amount. One 7-minute run of the bcfix engine at `--ghost-layers 3` tests whether they
compose. **Pre-registered prediction, so it is falsifiable: if they are independent
the combined error lands near +20 to +25 %, still short of PASS. If it lands at or
under +10 % they were the whole story and Job B is rescued. If it lands no better
than either alone, they share a mechanism and the mass-deficiency and unconstrained-
node accounts are the same defect counted twice.**

## 4. Verification block

```
bash scripts/tacc.sh vista 'diff $WORK/mpm-engine/src/warpmpm/kernels/mpm_solver_warp.py \
                                 $WORK/mpm-engine-bcfix-src/warpmpm/kernels/mpm_solver_warp.py'
bash scripts/tacc.sh vista 'grep -E "SCENE_SHA256|ENGINE" $WORK/d4_ghost_918461.out $WORK/d4_jobBbc_918450.out'
```

Sources: `$WORK/d4_jobB_918240/sphere_fixed_g64.json`,
`$WORK/d4_jobBbc_918450/sphere_fixed_bcfix.json`,
`$WORK/d4_ghost_918461/sphere_ghost{0,3}.json`.
