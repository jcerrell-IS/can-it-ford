# R7: the floor boundary is now essentially perfect, and Job B still fails by +36 percent

Job 918526, submitted and collected 2026-08-18. COMPLETED, both arms `RC=0`, elapsed
2 min 09 s. It is the engine-swap replicate of 918461: same scene sha, same 300 frames,
same SDF cache, same two `--ghost-layers` arms, only `PYTHONPATH` differs. With 918461
that makes a balanced 2x2, verified on 15 config keys with 0 comparability problems and
`n_ghost_layers`, `ghost_depth_m`, `n_water` varying by ghost arm only.

## 1. The 2x2

`fz_over_analytic_measured`, mean of last 20 of 300 frames. Manifest bands:
<=10 PASS, 10 to 25 REPORTABLE PARTIAL, >25 FAIL.

| engine \ ghost layers | 0 | 3 |
|---|---|---|
| **pinned** (`<`)  | +51.22 % FAIL | +38.03 % FAIL |
| **bcfix** (`<=`) | +35.23 % FAIL | **+35.92 % FAIL** |

```
engine effect at ghost=0   -0.15983      ghost effect at pinned   -0.13188
engine effect at ghost=3   -0.02110      ghost effect at bcfix    +0.00686
INTERACTION                +0.13873      strongly NOT additive
additive prediction 1.22045 (+22.05 %)   observed 1.35918 (+35.92 %)
```

**PRE-REGISTERED BRANCH C FIRED.** The prediction written into the sbatch header before
the run said branch C would mean "no better than the better single fix, so the two
accounts are ONE defect counted twice". Observed +35.92 % against the best single fix's
+35.23 %. The combination is very slightly WORSE than the engine fix alone.

**So the two fixes are redundant, not independent.** Once the node lying exactly on the
plane is constrained, adding three sacrificial sub-floor layers buys nothing on the
graded quantity (+0.00686 in ratio units). The "unconstrained node" account and the
"B-spline mass deficiency" account are not two defects. They are one.

## 2. THE DISSOCIATION, and it is the real finding

The two fixes are redundant on FORCE and complementary on LEAKAGE. Floor crossings,
baseline-corrected as `n_below_floor(t) - n_below_floor(0)` because the ghost arms seed
34321 particles below the nominal floor and the raw column would count a seeding choice:

| engine \ ghost | 0 | 3 |
|---|---|---|
| pinned | 4.529 % | 0.653 % |
| bcfix  | 0.180 % | **0.008 %** |

The combined cell leaks **49 particles of 598505** across the whole 300-frame run. That
is a **566-fold** reduction against the 4.529 % baseline. The floor boundary in that cell
is, for practical purposes, no longer leaking.

**And the force error is still +35.92 percent.**

| | baseline | best fix | removed |
|---|---|---|---|
| floor crossings | 4.529 % | 0.008 % | 99.8 % of the leak |
| force error | +51.22 % | +35.92 % | 15.30 points of 51.22, **29.9 % of the error** |

**Eliminating 99.8 percent of the floor leakage removes only 30 percent of the force
error.** Roughly 36 points of overshoot survive a boundary that no longer leaks.

**Therefore the floor leak is not the dominant cause of Job B's failure.** It was a real
defect, it is now essentially fixed, and fixing it does not rescue the benchmark. R5's
mechanism story is confirmed as a description of the leak and refuted as an explanation
of the force error. The remaining ~36 points are a THIRD error source that neither
boundary fix touches, and it is now the only thing standing between Job B and a pass.

## 3. Job B still FAILS. The ladder stays stopped.

All four cells FAIL criterion 3. The best cell, +35.23 %, is not merely short of the
10 % PASS band, it is outside the 25 % REPORTABLE PARTIAL band as well. Per
`R5_PHYSICS_BATCH_MANIFEST.md:214`, "Any FAIL stops the ladder." **Job C stays gated.**

R6's conclusion is unchanged and is now much better supported: it survives two
independent boundary remedies, one of which drives the leak to near zero.

## 4. Consistency check on job 918450

918450 is deliberately NOT a cell of the 2x2, because it ran 200 frames with no SDF
cache and splicing it in would confound the interaction with a settings change. As a
consistency check instead:

| | `fz_over_analytic_measured` | frames |
|---|---|---|
| 918450, no cache | 1.35803, +35.80 % | 200 |
| 918526 bcfix ghost0, cached | 1.35233, +35.23 % | 300 |

A gap of 0.57 points. **918450 reproduces, and frame count plus SDF caching together
move the metric by well under one point.** That bounds a nuisance parameter that had
never been measured.

## 5. Two defects found in the instruments, both fixed

**In my own grader.** The first version compared a config key named `lim` across the
four cells. That key does not exist: the real name is `lim_m`. All four returned `None`,
`None == None` compared equal, and the row printed `OK`. **A check that cannot fail
printed a pass.** It now reports `NOT CHECKED` when a key is absent from every config,
and the key list has grown to 15 real keys including `dx_m`, `h_m`, `substeps`, `seed`
and `wall_m`, all of which genuinely match.

**In job 918450's provenance, carried forward.** Its JSON records
`provenance.pinned_sha = 544c93dd02cb9c7ead89e...`, the PINNED engine, while it ran the
bcfix engine, because that field is a hardcoded string. 918526 does not repeat the
mistake: it resolves `sys.path` the way the import system would and asserts the answer,
without importing `warpmpm`, since that import blocks about 79 s even on a compute node.
It printed:

```
FIRST_ON_SYSPATH=.../mpm-engine-bcfix-src/warpmpm/kernels/mpm_solver_warp.py
FIRST_ON_SYSPATH_SHA256=2309d8a2358d693e91d54e97c80483a5228827d3bb694a326ac7fae1d9cae35a
ENGINE_RESOLUTION_OK
```

Sha-summing a file on disk proves the file exists, not that it is the one imported.

## 6. What to do next, in order

1. **Stop working on the floor boundary.** It is fixed and it was not the cause. Any
   further effort there is capped at the 0.008 % that remains.
2. **Find the third error source.** It is worth about 36 points, an order of magnitude
   more than anything the boundary work recovered. Candidates that this 2x2 does not
   touch: the SDF collider force accessor itself, the added-mass assumption in the
   analytic target, the artificial sound speed, and the `analytic_buoyancy_N` reference
   value. The wall leak is still 15 to 17 % higher in the ghost arms and untouched.
3. **The Job B decision is Josie's and is unchanged.** Accept the FAIL and stop the
   ladder as the manifest instructs, or amend the criterion in writing before Job C.
   The evidence for the FAIL is now much stronger than when the question was first put.

## 7. Verification block

```
/usr/bin/python3 analysis/r7_jobb_2x2.py \
  --pinned-ghost0 <918461 sphere_ghost0.json> --pinned-ghost3 <918461 sphere_ghost3.json> \
  --bcfix-ghost0  <918526 sphere_bcfix_ghost0.json> \
  --bcfix-ghost3  <918526 sphere_bcfix_ghost3.json> \
  --consistency   <918450 sphere_fixed_bcfix.json>
```

Sources: `$WORK/d4_ghost_918461/sphere_ghost{0,3}.json`,
`$WORK/d4_combo_918526/sphere_bcfix_ghost{0,3}.json`,
`$WORK/d4_jobBbc_918450/sphere_fixed_bcfix.json`. Submit script
`$WORK/d4_combo_pair.sh`.
