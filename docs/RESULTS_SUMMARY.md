# Four findings worth defending, each with its number, its command, and its limitation

Written 2026-08-26. Three of the four were re-measured today and one was not; the difference is
marked on each. If you are preparing to defend this work in an interview, these are the four, and
the limitation matters as much as the number.

---

## 1. The binary verdict is grid-invariant. The displacement behind it is not.

**The number.** Across n_grid 48, 64 and 96 at fixed depth and velocity, `final_disp_mag_m`
moves non-monotonically, and the direction depends on mass:

| mass | g48 | g64 | g96 | 48 to 64 | 64 to 96 |
|---|---|---|---|---|---|
| 1100 kg | 0.350717 | 0.658537 | 0.268638 | **+87.8%** | **-59.2%** |
| 1609 kg | 0.256830 | 0.314076 | 0.155959 | +22.3% | -50.3% |
| 2337 kg | 0.187542 | 0.135559 | 0.089439 | -27.7% | -34.0% |

**All nine runs return NO-FORD regardless.** [CONFIRMED 2026-08-26]

```bash
make facts   # and see the table above, re-derived from data/all_runs_inventory.csv
```

**Why it is defensible.** The verdict survives a 2x change in grid resolution, so the conclusion
does not rest on a resolution choice. Steffen, Kirby and Berzins 2008 is the citable mechanism for
MPM losing convergence under refinement at fixed particles-per-cell, and Syamlal, Celik and
Benyahia 2017 establish that grid refinement does not converge an instantaneous quantity anyway.
Non-monotone displacement is documented expected behaviour for an instantaneous value, not
necessarily a solver defect.

**The limitation, and say it before you are asked.** **Cite the verdict, never the displacement
magnitude.** The g64 run alone carries two disagreeing displacement measures: `summary.json` says
0.658537 and `rollout.npz` says 0.637019, a 3.4 percent gap. If grid convergence were the claim,
this study would not support it: that would need a time-averaged observable over a demonstrated
stationary window with a GCI, and `params_check.py` reports live that the apparent order cannot
even be computed here because the refinement ratio is not constant.

**Third row is new.** The 2337 kg row is monotone decreasing. The non-monotonicity is
mass-dependent, and the write-ups that quote only 1100 and 1609 kg omit the case that does not
show it.

---

## 2. Fifteen of seventeen runs violate the weak-compressibility rule they are built on

**The number.** Every gated run uses a single artificial sound speed, **12.845 m/s**. The
weak-compressibility convention is that sound speed should be at least 10x the flow velocity, so
that the Mach number stays near 0.1. **15 of 17 runs fail that**. [CONFIRMED 2026-08-26]

```bash
python -c "
import csv
r=list(csv.DictReader(open('data/all_runs_inventory.csv')))
print(sorted({float(x['sound_speed_ms']) for x in r}))
print(sum(1 for x in r if float(x['sound_speed_ms']) < 10*float(x['velocity_ms'])), 'of', len(r))"
```

**Why it is defensible.** This is a disclosed limitation with an automated gate, not a discovered
error. Isik and He 2022 show artificial sound speed can qualitatively flip a rigid-body outcome,
which makes this the single most consequential unswept parameter in the study, and it is named as
such rather than buried.

**The limitation.** Naming a limitation is not bounding it. Nothing here establishes which way the
outcome would move at a higher sound speed, and the sweep that would answer it has not been run at
the gated configuration.

---

## 3. Twelve of seventy L1 cells change verdict on the class label alone, and some land exactly on the cap

**The number.** In the 70-condition analytical sweep, **12 cells** return different verdicts under
the small-passenger, large-passenger and large-4WD limit sets. FORD counts are 14, 19 and 26
respectively. [CONFIRMED 2026-08-26]

```bash
python -c "
import csv
s=list(csv.DictReader(open('data/scenario_sweep.csv')))
print(sum(1 for r in s if len({r['L1_verdict_small_passenger'],
      r['L1_verdict_large_passenger'],r['L1_verdict_large_4wd']})>1), 'of', len(s))"
```

**The sharper version, measured today.** Several cells land on a class cap with a margin of
**exactly 0.000000 m2/s**: depth 0.1 at v 3.0 and depth 0.2 at v 1.5 both give `L1_haz` = 0.300000
against the 0.30 small-passenger cap; depth 0.3 at v 1.5 gives 0.450000 against the 0.45 cap; depth
0.2 at v 3.0 gives 0.600000 against the 0.60 cap. **At those cells the verdict is decided by the
direction of a floating-point comparison, not by physics.**

**Why it is defensible.** It shows the criterion's own class assignment, not the physics, produces
a large share of the disagreement, and the project caught this in its own poster: 12 of the 23
reclassified cells came from evaluating a 1100 kg car against its published class rather than the
Large 4WD limits.

**The limitation.** **[UNVERIFIED]** A margin of `0.0084 m2/s` appears in earlier write-ups as the
tightest class-label flip. It does **not** reproduce from `data/scenario_sweep.csv`, where the
tightest margins are exactly zero. Either it comes from a different dataset or it is stale. Do not
quote it until its source is found.

---

## 4. The project's own settle length is contradicted by all of its own runs

**The number.** `sim_standing.py` uses `settle_frames=8`. Applying a stationarity test to all 25
local runs, **25 of 25 need more than 8 frames discarded**: minimum 29, median 48, maximum 80, out
of 91 total frames. Effective sample size is 2.9 to 11.0, so any uncertainty computed from N=91 is
overstated by roughly 3x to 5x. **[DOC, from CLAUDE.md, NOT re-run in this session.]**

```bash
python analysis/settle_audit.py      # re-run before quoting; no GPU needed
```

**Why it is defensible.** It is a self-audit that contradicts a published choice, reached by a
different route from the earlier settle-length sweep, so the two corroborate rather than repeat.
Use `effective_sample_size`, never the frame count.

**The limitation, and it is the interesting part.** **Do not remove the transient before a SLIDE
verdict.** Incipient motion is an event, not a steady state. Removing the transient drops SLIDE
from 21 of 24 runs to 5 of 24 and would silently contradict the published 16 SLIDE / 1 STUCK. So
the correct settle length for a *mean* is the wrong one for an *event*, and the published verdicts
use the full record deliberately.

---

## The finding that is not here

**No reconstruction has ever entered a simulation.** The reconstruct-to-decide front end is
designed and not built. Do not present the splat work and the simulation work as one pipeline.
They are two stages that are not connected, and the poster says exactly that under Scope.
