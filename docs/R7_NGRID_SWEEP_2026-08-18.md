# R7: refinement removes half the remaining error and then stops at a floor

Job 918722, submitted and collected 2026-08-18. COMPLETED, all three arms `RC=0`, elapsed
20 min 19 s. Fixed sphere, bcfix engine, `--ghost-layers 0`, 300 frames, `lim` 1.2,
`depth` 0.5, SDF cache. Ten config keys verified identical across the three arms; only
`n_grid`, `dx_m`, `h_m`, `substeps` and `n_water` vary.

**The control passes.** The n=64 arm reads 1.35231 against job 918526's bcfix/ghost0 cell at
1.35233, a difference of 2e-5, so the sweep is a valid extension of the 2x2 and not a new
configuration.

## 1. Result

`fz_over_analytic_measured`, mean of last 20 of 300 frames.

| n | dx (m) | n_water | measured | skin predicted | delta | implied skin k (cells) |
|---|---|---|---|---|---|---|
| 64  | 0.018750 | 598,505   | **+35.23 %** | 35.23 (fitted) | control | 0.8467 |
| 96  | 0.012500 | 2,019,044 | **+27.00 %** | 22.70 | +0.0430 | 0.9950 |
| 128 | 0.009375 | 4,784,798 | **+23.68 %** | 16.73 | +0.0695 | 1.1746 |

**PRE-REGISTERED BRANCH C FIRED**: "no single story; both terms present; report the fitted
exponent rather than choosing a story."

**The geometric skin is refuted as a complete explanation.** If a one-cell skin were the
whole story the implied thickness `k` would be CONSTANT across rungs. It grows by 38.7
percent, 0.8467 to 1.1746, so the error falls more slowly than any fixed geometric skin
allows.

## 2. The fitted model, and the floor

Fitting `error(dx) = A*dx^p + C` exactly through the three points:

```
p = 1.6103        A = 103.754        C = 0.18054
```

| n | dx | observed | fit |
|---|---|---|---|
| 64 | 0.018750 | 35.23 % | 35.23 % |
| 96 | 0.012500 | 27.00 % | 27.00 % |
| 128 | 0.009375 | 23.68 % | 23.68 % |

Extrapolated: n=192 gives +20.98 %, n=256 gives +19.90 %, n=512 gives +18.66 %.

**THE ERROR CONVERGES TO A NON-ZERO FLOOR OF +18.05 PERCENT.** Refinement alone never
reaches the 10 percent PASS band, at any resolution. The resolution-dependent part is worth
about 17.2 points of the original 35.2; the floor is the rest.

`p = 1.61` sits between first and second order, consistent with a surface or interface error
term (a skin, or quadrature error at the free surface) rather than a clean bulk second-order
term. That is the shape Baumgarten and Kamrin 2023 (`10.1002/nme.7217`) describe for MPM
integration error, and the non-vanishing floor is the shape Chen 2018
(`10.1016/j.compfluid.2018.09.005`) and Mast et al. 2012
(`10.1016/j.jcp.2012.04.032`, "Mitigating kinematic locking in the material point method")
describe for locking, which is a formulation defect and not a discretization one.

**CAVEAT, and it is not a small one.** Three points and three unknowns is an EXACT fit with
zero residual, so it cannot be validated by goodness of fit. `p` and `C` are a description of
these three numbers, not an established convergence order. A fourth rung would test it.
Separately, there is **one run per rung**: the sphere scene has no repeats anywhere in the
project, so run-to-run spread is unmeasured and none of these deltas has an error bar.

## 3. THE ERROR BUDGET NOW DECOMPOSES INTO THREE ROUGHLY EQUAL THIRDS

Taking the 2x2 baseline (pinned engine, no ghost layers, n=64) at +51.22 percent:

| term | worth | what removes it |
|---|---|---|
| boundary treatment | 16.0 points | the one-line engine fix, already done |
| spatial resolution | 17.2 points | refinement, with diminishing returns |
| **irreducible floor** | **18.05 points** | **neither. Formulation-level.** |

Each accounts for about a third. That is the cleanest statement of Job B's failure the
project has, and it is the first time the residual has been separated from the two things
that were being blamed for it.

## 4. WHAT THIS DOES TO THE LADDER DECISION, which is still Josie's

The manifest bands are: <=10 PASS, 10 to 25 REPORTABLE PARTIAL, >25 FAIL, and
`MANIFEST:214` says any FAIL stops the ladder.

**At n=128 with the boundary fix, the measured value is +23.68 percent, which is inside the
REPORTABLE PARTIAL band, not FAIL.** The extrapolated floor of +18.05 percent is also inside
PARTIAL.

**This does NOT re-grade Job B, and it must not be presented as doing so.** Job B's criterion
was fixed in advance for a specific configuration, `--n-grid 64` on the pinned engine, and
that run genuinely reads +50.06 percent, a FAIL. Changing the engine and the resolution
produces a DIFFERENT run, not a re-scored one. Re-grading a failed test on a configuration
chosen after seeing the failure is exactly the move the project's own discipline forbids.

What it does establish is narrower and still important: **the ladder-stopping FAIL is a
property of the n=64 pinned-engine configuration, and both of those were choices.** A Job B
specified at n=128 on the fixed engine would have landed in PARTIAL and the ladder would not
have stopped.

So the decision Josie faces is now better posed than before. Either accept the FAIL as
graded and stop, or amend the specification in writing, in advance, stating the resolution
and engine, and re-run. The one thing not available is to quietly adopt the n=128 number.

## 5. What to do about the floor

The floor is the only part that no amount of the current approach removes, and it is the
largest single term. It is not the boundary (fixed, and the leak is down to 49 particles of
598505) and not the domain (a 4x domain moved the ratio by 1 percent). The sourced candidates
are volumetric locking and free-surface treatment in weakly compressible MPM, and **both
papers are already in this project's own corpus and both are uncited**.

The cheap next diagnostic is the pressure-surface integral cross-check: integrate pressure
over the sphere surface and compare against the impulse-exchange reading. If the two disagree
by about the floor, the defect is in the force extraction. If they agree, the defect is in
the pressure field itself, which is where locking would live. That is a Mac-side analysis if
the pressure field is dumped, and it is the diagnostic the literature review flagged as
rarely done and worth publishing.

## 6. Verification

```
bash scripts/tacc.sh vista 'grep -E "RC_n|seconds|SUMMARY|ALLDONE" $WORK/d4_ngrid_918722.out'
```
Sources: `$WORK/d4_ngrid_918722/sphere_bcfix_n{64,96,128}.json`, submit script
`$WORK/d4_ngrid_sweep.sh`, which carries the pre-registered branches in its header.
