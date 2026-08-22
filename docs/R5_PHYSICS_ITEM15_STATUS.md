# D4: CLAUDE.md item 15 is half stale, and its own prescribed close-out was already done

2026-08-17. Branch `claude/r5-physics`. Mac only, no GPU. **I own no part of CLAUDE.md or
the register; this is a report, not an edit.**

Claim tags: **[read]** primary source this session, **[measured]** computed here,
**[unreviewed]** no physics-skeptic pass.

---

## What item 15 currently says

CLAUDE.md item 15 records a gravity fork in post-processing:

> post-processing is forked. 9.80665 at `simulation/failure_modes.py:14` and
> `analysis/viability_dashboard_scaffold.py:11`, against 9.81 at five sites including
> `gates_all_runs.py:12`. **TWO sites at 9.80665, not one.**

and prescribes a close-out:

> To close: set `failure_modes.py:14` to 9.81, re-run `analysis/classify_failure_modes.py`,
> and confirm the verdicts are byte-identical. **Do not close it by assertion.**

## Status, read live

**Half of the fork is gone.** `simulation/failure_modes.py:14` is now **`G = 9.81`**
**[read]**, with an in-file comment recording that it was unified on 2026-08-12 and what it
had been. So item 15's citation of that site is **stale**.

**The other half is still live.** `analysis/viability_dashboard_scaffold.py:11` still reads
`G = 9.80665` **[measured]**. So the fork is **halved, not closed**, and item 15's "TWO
sites" should now read one.

Three further 9.80665 strings exist and are **not** declarations: a comment in
`failure_modes.py:15` recording the old value, a docstring in
`analysis/classify_failure_modes.py:30`, and an assertion string in
`scripts/check_claims.py:151`. A naive recount that swept those in would report four or
five sites and be wrong, which is the same scope trap CLAUDE.md item 13 documents for
`DRIFT_THRESHOLD`.

## The close-out was performed, and its answer was NOT what item 15 anticipated

Commit `e495b56`, "Unify post-processing G on 9.81 and record the one figure that moved"
**[read]**, did exactly what item 15 asked: changed the constant, regenerated
`data/failure_modes_by_run_classified.csv` and `data/failure_modes_by_run.json` via
`analysis/classify_failure_modes.py`. The classified store's mtime is the same day, which
is consistent.

**The verdicts are byte-identical: 16 SLIDE / 1 STUCK, all 17 run-to-mode pairs and all
`triggered_*` flags unchanged.** Exactly 3 of 33 columns moved, all direct functions of G:
`ratio_topple`, `peak_surge_accel_g`, `weight_n`.

**But register A6's stated reason was refuted in the process**, and this is the part worth
carrying: A6 predicted no verdict flip because all 13 sub-threshold TOPPLE margins were
supposedly far larger than the 0.034% change. **`g48_m2337`'s margin was 0.0244%, smaller
than the change**, and it crossed 1.000244 to 0.999903. So the `ratio >= 1` count went
**13 to 12** while `triggered_topple` stayed 0 in all 17.

That is a clean instance of the trap CLAUDE.md item 12(a) already names: `ratio_*` is peak
magnitude and `triggered_*` is the verdict, and they disagree. A6 got the right answer for
a reason that was wrong by a factor of about 1.4 on the very run that decided it.

## What I am reporting, not doing

1. Item 15's `failure_modes.py:14` citation is stale; the site is 9.81.
2. "TWO sites at 9.80665" is now one, `viability_dashboard_scaffold.py:11`.
3. Item 15's prescribed close-out **has been done**, by `e495b56`, with the verdicts
   confirmed byte-identical rather than asserted. Item 15 still reads as if it were open.
4. Anyone recounting 9.80665 must exclude the three non-declaration strings.

None of this is in my scope to edit. **[unreviewed]**: no physics-skeptic pass on this
document, though every element is a direct file read or a commit message quote.
