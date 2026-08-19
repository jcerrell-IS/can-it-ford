# Provenance audit of the R9 headline results, 2026-08-19

Run under the `provenance-audit` skill, whose prime directive is that an audit never
terminates in self-review: the last step must be a live read of a primary source. Every
row below ends in a read of the job's own output on Vista, not in a reading of the commit
message that reported it.

Scope: the two results tonight's session prescriptions were about to rest on, plus the
coordinator's own relayed claims.

## The finding that applies to both sessions

**NEITHER HEADLINE RESULT HAS A DATA ARTIFACT IN THE REPOSITORY.** Both are carried by a
markdown document and, in one case, an analysis script. The underlying JSON exists only on
Vista under `/work/11603/jcerrell0629/vista/`, which no reader of this repository can see
and which is not backed up by git.

    git show --stat 03cd132   ->  docs/R9_ACCESSOR_DEFECT_2026-08-18.md only
    git show --stat 3f4c1ec   ->  docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md
                                  analysis/r9_jobb_estimator_test.py

This is the same shape as `renders/yaris_render_s1/failure_modes_result.json`, which this
project condemned for having no run identifier and being written by no script. The numbers
are almost certainly right. They are simply not re-derivable by anyone else, and this
project's own rule, adopted after the DRIFT_THRESHOLD count moved three times in one day,
is that a number which will be published must be enumerable by a command someone else can
run.

## Row 1: d11, KE/PE rises with particles per cell

CLAIM, from 03cd132: "KE/PE 1.0913e-02 -> 1.3735e-02 from 8 to 27 particles per cell,
+25.86 percent, difference 2.8220e-03 +/- 2.8529e-04 blocked = 9.89 SIGMA."

LIVE READ of `/work/11603/jcerrell0629/vista/d11_lock_923270/column_ppc{2,3}.json`, every
KE-bearing field:

| field | ppc 8 | ppc 27 | change |
|---|---|---|---|
| ke_over_pe_above_floor_final | 0.009252180 | 0.011997877 | +29.68 pct |
| ke_over_pe_above_floor_min   | 0.008458624 | 0.010423584 | +23.23 pct |
| ke_over_pe_all_final         | 0.009334239 | 0.012468973 | +33.58 pct |

**DIRECTION: VERIFIED at T1, on three independent field definitions.** Every one rises.
The conclusion that KE/PE rises with particles per cell, and therefore that quadrature and
sampling are excluded because they predict the opposite sign, stands on primary data.

**THE SPECIFIC NUMBERS: UNVERIFIED.** Neither 1.0913e-02 nor 1.3735e-02 appears in any
summary field on disk, and both are HIGHER than every final-frame value, so they are a
window statistic whose window and field the commit does not name. The +25.86 percent
likewise matches none of the three measured pairs. The 9.89 sigma cannot come from the
`blocked` block either: that block's `se_blocked` is 0.0331 and 0.0505, and it is computed
on the PRESSURE GRADIENT, with `blocked_se_pct` 3.31 and 5.05.

NOTE THE DIRECTION OF THE ERROR: two of the three field definitions give a LARGER effect
than claimed, 29.68 and 33.58 percent against 25.86. The conclusion strengthens under
audit. Only its reproducibility fails.

UNREPORTED CONTEXT, from the same file. In the ppc 27 arm the hydrostatic gradient's own
relative error swings from -94.988 percent at frame 0 to +49.883 percent at frame 140 and
back to -29.379 at frame 180, while `stationary_3sigma` reads True. Both can be true if
the graded window is a late slice, but a reader of the commit would not know the series
does that, and it is material to any claim about that arm.

## Row 2: d21, the PPC and grid prongs

CLAIM, from 3f4c1ec: k_fit 0.687, 0.726, 0.727, 0.829 across PPC 3.375 to 64, log-log
slope +0.0596; and grid prong excess = 2.669*dx_mm - 4.217 at 1.86 sigma.

LIVE READ of `/work/11603/jcerrell0629/vista/d4_r9est_923239.out`: the job wrote
`r9_ppc{1.5,3.0,4.0}.json`, 300 frames each, RC 0 on every arm. **The string `k_fit`
appears nowhere in the job output.** It is a quantity the session derived from those JSONs
afterwards, and the derivation is not in the committed script.

VERDICT: **UNVERIFIED AT T1 IN THE REPOSITORY**, not contradicted. The runs demonstrably
happened and completed cleanly. The derived statistic that the conclusion rests on cannot
be recomputed from anything committed.

The grid prong is separately self-labelled by its own author as 1.86 sigma against this
project's 3 sigma bar, with g128 resting on 35 frames. That is an honest label and it is
why the extension to a long record is the right next job rather than a new hypothesis.

## Row 3: the coordinator's relayed claims

Two were withdrawn in ac0f0d8 after d21 read the paper directly: that Wallstedt and
Guilkey state the projection error is a constant systematic bias for a fixed body (it is
not in the paper, and the paper's own emphasis runs the other way), and that the plateau
scales as O(h) (measured off a figure by eye; the paper's analytic reference has an h^2
grid term). Both originated in a PDF-reading subagent's own reasoning section being
relayed as the paper's text. VERDICT: CONTRADICTED, corrected at the root, carrier file
updated rather than only the chat.

## Actions

1. d11 and d21: commit the run JSONs, or a distilled CSV of them, into the repository, and
   commit the few lines that turn those files into the headline number. Name the field and
   the window.
2. d11 specifically: state which field and window give 1.0913e-02 and 1.3735e-02, since
   three plausible fields give +23.23, +29.68 and +33.58 percent and the paper-facing
   number should be the one whose definition is written down.
3. d21: extend g128 to a long record and re-grade the grid prong, which is a sample-size
   problem rather than a physics problem.
4. Nobody: neither result should be quoted outside the fleet until action 1 is done. The
   direction of d11's result is safe to quote now; its magnitude is not.
