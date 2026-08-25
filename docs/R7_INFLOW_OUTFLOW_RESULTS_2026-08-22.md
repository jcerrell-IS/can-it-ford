# R7 recycling in/outflow BC: result, independently re-reduced

Date 2026-08-22. This document was commissioned as "run the experiment, it has never
been run". **It had already been run.** What follows is therefore not a new run. It is
an independent re-reduction of the existing output tree straight off Vista, a live
re-verification of every Step Zero precondition, and a plain answer to each question
the dispatch asked.

Zero SU were spent producing this document.

The physics write-up is `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md` (500 lines,
commit `a6e534a`). This file does not duplicate it. It records what reproduces, what
the dispatch got wrong, and the two pre-registered predictions judged plainly.

---

## 0. Two premises in the dispatch that are false, both read-directly

**1. The instrument is not on `claude/r8-bc-merge`.** Commit `5ecf725` is not an
ancestor of that branch, and none of the five instrument files exist at its tip.

```
git merge-base --is-ancestor 5ecf725 claude/r8-bc-merge   ->  NOT an ancestor
git branch -a --contains 5ecf725                          ->  claude/r7-inflow
                                                              claude/r8-persistence
                                                              remotes/origin/claude/r7-inflow
```

The instrument lives on **`claude/r7-inflow`**, which is also the only one of the three
pushed to `origin`. A worktree on `r8-bc-merge` was added per the dispatch, found to be
the wrong branch, verified unchanged, and removed; `.claude/worktrees/r7-inflow` was
added in its place.

**2. It has been run.** Not once but twice, on 2026-08-17/18, and the results are
committed. Confirmed live in Vista's own accounting database, not from a document:

```
      JobID          JobName  Partition       State ExitCode    Elapsed
     918501  r7_inflow_smoke         gh   COMPLETED      0:0   00:00:57
     918506        r7_inflow         gh   COMPLETED      0:0   00:13:27
```

The output tree is live on Vista at `/work/11603/jcerrell0629/vista/r7_inflow_918506`,
**34 run directories, 9.9 GB**. Every path carries `918506`, so the dispatch's
"confirm SLURM_JOB_ID is in the output paths" checks out (read-directly).

Because of this, steps 2 to 5 of the dispatch (smoke, estimate, stop for go-ahead,
submit) were not executed. Re-running a completed pre-registered design would have
spent real SU to produce a duplicate. That call is flagged for Josie in section 7.

---

## 1. Step Zero, all three checks, live

| check | result | how |
|---|---|---|
| SU balance, before | **581** on BCS20003, expires 2026-09-30 | `/usr/local/etc/taccinfo` |
| SU balance, after | **581**, unchanged | same, re-read at end of session |
| SU spent by this session | **0** | balance identical before and after |
| pinned driver sha256 | **matches exactly** | `sha256sum` on Vista |

Driver, read-directly:

```
4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9
  /work/11603/jcerrell0629/vista/can-it-ford-track1-6dof/renders/yaris_render_s1/sim_standing.py
```

That is the pinned value character for character, so the wrapper's sha refusal would
not have fired. Three other copies on Vista carry the same hash; three carry different
hashes (`5215c38b...`, `7236e474...`) and would correctly be refused.

**The balance is falling.** 670 on 2026-08-12, 609 on 2026-08-19, **581 today**. Down
28 SU in three days, and 89 since 2026-08-12. None of that is this experiment, which
predates the 609 reading.

**Live now and burning:** job `928087` (`idv03583`), partition `gh-dev`, RUNNING on
node `c642-021`, a 2:00:00 interactive allocation. An idle idev bills the same as a
working one. This is the node the dispatch was written against, and with the
experiment already complete there is no longer any work for it to do.

### SU actually spent by the experiment, when it ran

Combined elapsed is 00:14:24 on 1 node, **0.24 node-hours** (read-directly from
`sacct`). At the Vista `gh` rate of 1.0 SU per node-hour and TACC's 0.25 h per-job
billing floor, two jobs floor to **about 0.50 SU** (inferred; the rate and the floor
are recalled, not re-read today).

Commit `a6e534a` states "About 0.24 node-hours and roughly 5 SU". Those two are
inconsistent with each other by a factor of ten at rate 1.0. **The node-hours figure
is the reliable one.** Treat "roughly 5 SU" as an overestimate. The practical
consequence is the opposite of alarming: this experiment is cheap, and a full
replication would cost well under 1 SU of the 581 available.

---

## 2. Smoke test, verified from its own log

Job `918501`, g48 plumbing, COMPLETED 00:00:57, ExitCode 0:0. Read directly from
`$WORK/logs/r7_inflow_smoke_918501.out`: **11 named assertions PASS, 0 FAIL**, plus
5 wrapper selftest groups and 11 `openchannel_bc` selftest checks, terminating
`ALLDONE`. The load-bearing ones:

```
PASS closed arm drops 0 planes (got 0)
PASS recycle arm drops 2 planes (got 2)
PASS dropped planes are x-normal: [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]
PASS closed arm never recycles
PASS max overshoot 0.03618 m < 1.5*dx = 0.29443 m, the P2G guard margin
PASS same water count in every arm (18194 / 18194 / 18194)
PASS outflow plane sits exactly where the closed arm's downstream wall does
```

That last pair is what makes the comparison fair: identical water, identical
reflection geometry, only the two x-normal planes differing. The smoke run measures no
physics and is not quoted as a result.

---

## 3. The re-reduction reproduces the committed result exactly

Pulled the tree from Vista excluding `rollout.npz` (4.3 MB of the 9.9 GB; the rollouts
are 170 to 650 MB per run and stay on Vista), then ran
`analysis/inflow_vehicle_stats.py` at the `claude/r7-inflow` tip.

**34 of 34 runs, 2,047 fields compared against the committed
`data/r7_inflow_918506/runs.json`, ZERO differences.**

Every table below was regenerated by `analysis/inflow_vehicle_tables.py` from my own
reduction, not transcribed from the 08-18 document.

Matrix as actually run, 34 runs, not the 40 the dispatch estimated: the `bare` control
is N=1 and the no-band sensitivity arm is N=3.

| config | bare | closed | recycle | recycle no-band |
|---|---|---|---|---|
| g64 m1100 v1.5 (baseline) | 1 | 5 | 5 | 3 |
| g64 m1100 v0.5 (the only STUCK of the 17) | . | 5 | 5 | . |
| g96 m2337 v1.5 (tightest published margin) | . | 5 | 5 | . |

---

## 4. Closed vs recycle at all three regimes, both horizons

Note on rows: the record is 251 metrics rows. The canonical horizon is **row 90**. The
dispatch says "row 249"; displacement is reported at the final row, **row 250**, and
the slope time series is fitted at row 249. Both labels are stated wherever used.

### 4a. Verdicts. Tallied, never meaned.

| config | arm | N | row 90 | row 250 |
|---|---|---|---|---|
| g64 m1100 v0.5 | closed | 5 | 5 STUCK | 5 STUCK |
| g64 m1100 v0.5 | recycle | 5 | 5 STUCK | 5 STUCK |
| g64 m1100 v1.5 | bare | 1 | 1 SLIDE | 1 SLIDE |
| g64 m1100 v1.5 | closed | 5 | 5 SLIDE | 5 SLIDE |
| g64 m1100 v1.5 | recycle | 5 | 5 SLIDE | 5 SLIDE |
| g64 m1100 v1.5 | recycle, no band | 3 | 3 SLIDE | 3 SLIDE |
| g96 m2337 v1.5 | closed | 5 | 5 SLIDE | 5 SLIDE |
| g96 m2337 v1.5 | recycle | 5 | 5 SLIDE | 5 SLIDE |

**Not one verdict moves.** 3 configurations x 2 horizons x N=5.

### 4b. Displacement magnitude. The verdicts do not move; these do.

| config | row | closed, m | recycle, m | change | ranges disjoint |
|---|---|---|---|---|---|
| g64 m1100 v1.5 | 90 | 0.6579 +/- 0.0014 | 0.8909 +/- 0.0028 | **+35.4%** | yes |
| g64 m1100 v1.5 | 250 | 0.2577 +/- 0.0019 | 1.0491 +/- 0.0039 | **+307.1%** | yes |
| g64 m1100 v0.5 | 90 | 0.0575 +/- 0.0009 | 0.0795 +/- 0.0015 | **+38.3%** | yes |
| g64 m1100 v0.5 | 250 | 0.0289 +/- 0.0013 | 0.1793 +/- 0.0045 | **+521.2%** | yes |
| g96 m2337 v1.5 | 90 | 0.0854 +/- 0.0008 | 0.0982 +/- 0.0015 | **+15.0%** | yes |
| g96 m2337 v1.5 | 250 | 0.0697 +/- 0.0013 | 0.1309 +/- 0.0017 | **+87.8%** | yes |

Every closed and recycle range is completely disjoint, against a within-arm spread of
at most 4.78 percent (0.46, 0.65, 3.85, 4.78, 2.57, 3.75 percent across the six arms).
The separation is far larger than the draw-to-draw noise, so N=5 was warranted.

The direction is systematic and was checked run by run: **all 16 closed runs end row
250 closer to their start than at row 90; all 18 recycling runs end further.**

The single most quotable line: the **v0.5 recycle arm reaches 0.1793 m, 3.6x the
0.05 m `slide_m` threshold and 6.2x its own closed control, and is still classified
STUCK.**

### 4c. The closed-tank artifact, defined as closed minus recycle so the vehicle's own backwater cancels

| config | closed slope | recycle slope | artifact | vs a 3 degree road |
|---|---|---|---|---|
| g64 m1100 v1.5 | +0.06742 | -0.00372 | **+0.07114 m/m** | **1.36x** |
| g96 m2337 v1.5 | +0.03098 | -0.01615 | **+0.04713 m/m** | 0.90x |
| g64 m1100 v0.5 | +0.02583 | -0.00633 | **+0.03216 m/m** | 0.61x |

tan(3 deg) = 0.05241. Slope over rows 60 to 89. At the canonical velocity the
reflecting walls manufacture a free surface tilt **steeper than a 3 degree road**. The
closed arm drains 2 of 12 streamwise bins at the baseline and 1 of 12 at g96; **no
recycle arm ever drains a bin.**

### 4d. Bow depth, which is what any depth criterion reads

| config | closed | recycle | change |
|---|---|---|---|
| g64 m1100 v1.5 | 0.3958 m at row 50 | 0.4941 m at row 224 | **+24.8%** |
| g96 m2337 v1.5 | 0.5093 m at row 17 | 0.7933 m at row 201 | **+55.7%** |
| g64 m1100 v0.5 | 0.2954 m at row 23 | 0.2954 m at row 24 | -0.0% |

The peak both grows and moves late by roughly 180 rows. The closed tank drains the
upstream reservoir that feeds the bow wave.

---

## 5. The two pre-registered predictions, judged plainly

### (a) "First reflection shifts from ~112 frames toward ~145.5" -> **FAILED**

Failed on its premise, not on its arithmetic, which is the more useful outcome.

The detector built to test it, `reflection_arrivals()`, **does not discriminate.**
Measured arrivals: closed rows 91/91/92, recycle rows 93/94/96. Both arms fire
immediately at the start of the detector's own search window, because a line fitted
over rows 40 to 89 does not extrapolate past 89 in either arm. The residual crosses
4 sigma at once regardless of boundary condition. **The prediction is not resolvable
by this instrument**, and the shift from 112 to 145.5 is neither observed nor excluded.

Worse for the framing, the 112.3 number does not survive scrutiny as a mechanism. It
reproduces to 0.04 of a frame as a **still-water** shallow-water round trip
(sqrt(g*d) = 1.6995 m/s). But the scene runs at 1.5 m/s over a realized depth of
0.2944294 m, so **Fr = 0.88**, and an upstream-travelling wave against that current
makes 1.6995 - 1.5 = 0.1995 m/s and needs about **478 frames**, not 112. Arithmetic
that reproduces a number is not arithmetic that explains it.

What separates the arms instead is a slower, basin-scale redistribution, caught by
fitting the slope independently at every row. A closed basin conserves volume, so
water piled downstream must come back and the slope must reverse. An open channel
carries no such obligation:

| config | arm | slope row 89 | row 149 | row 249 | first sustained sign reversal |
|---|---|---|---|---|---|
| g64 m1100 v1.5 | closed | +0.0602 | +0.0076 | -0.0162 | **row 179, all 5 reps** |
| g64 m1100 v1.5 | recycle | -0.0114 | -0.0300 | -0.0249 | never positive after startup |
| g96 m2337 v1.5 | closed | +0.0286 | +0.0240 | +0.0166 | **never reverses** |
| g96 m2337 v1.5 | recycle | -0.0203 | -0.0286 | -0.0232 | never positive |

That is a clean discriminator. It is not the predicted one.

### (b) "Recycled particles stay outside the vehicle window through frame 90" -> **FAILED at 2 of the 3 regimes**

First row a recycled-tagged particle is inside the vehicle's streamwise window,
per repeat, read-directly:

| config | predicted | measured | verdict |
|---|---|---|---|
| g64 m1100 v1.5 (baseline) | > 90 (about 130) | **64, 64, 64, 64, 64** | **FAILED**, arrives 26 rows early |
| g96 m2337 v1.5 | > 90 | **70, 70, 70, 70, 70** | **FAILED**, arrives 20 rows early |
| g64 m1100 v0.5 | > 90 | 161, 162, 162, 162, 162 | **HELD** |
| g64 m1100 v1.5 no band | > 90 | 92, 92, 92 | held, but by 2 rows |

Identical across every repeat, so this is structural, not a draw. The prediction holds
only at the low-velocity case, and **fails at the canonical baseline, which is the one
that matters.** By the final row, 33.9 to 66.3 percent of all water has been recycled
at least once.

This is the honest cost of the recycling BC: it removes the reflecting wall and
replaces it with a recirculation that contaminates the vehicle's own neighbourhood
inside the published horizon. Neither boundary is clean at the baseline.

**Summary: prediction (a) failed, prediction (b) failed at 2 of 3 regimes.** Both were
written into the wrapper before any run, which is why they are worth this much space.

---

## 6. Does this change the 17 published verdicts, or the stated limitation?

**The verdicts: no.** Read-directly, 3 configurations x 2 horizons x N=5, no verdict
moves anywhere. 5 of 5 SLIDE stays 5 of 5 SLIDE at the g64 baseline and at the g96
tightest published margin. 5 of 5 STUCK stays 5 of 5 STUCK at v0.5, the only STUCK of
the 17. The published binary verdicts **do not depend on the reflecting streamwise
walls.** That is a null result and it is the headline.

**The limitation: yes, it should be rewritten, and it gets stronger, not weaker.** The
project's open-channel-BC limitation can no longer be stated as "we have a closed tank
and cannot say what it costs". It has been measured:

- the closed tank manufactures a free-surface slope of **1.36x a 3 degree road** at the
  canonical velocity, and drains 2 of 12 streamwise bins;
- the displacement behind the unmoved verdicts rises **15 to 521 percent**, with
  disjoint ranges;
- bow depth rises **24.8 and 55.7 percent** and its peak moves about 180 rows later;
- the canonical horizon sits at **86.5, 86.9 and 42.9 percent of the closed arm's own
  peak artifact**, so the 17 runs stop while the artifact is near maximum rather than
  after it has relaxed;
- and the verdicts survive all of it anyway.

**One thing got worse under recycling, reported not buried.** The below-floor leak
roughly triples at g64: 1.54 to 5.38 percent at the baseline, 0.47 to 6.53 percent at
v0.5. The per-face split diagnoses it as **entirely the floor**, while the wall leak
falls. It is a g64 phenomenon; at g96 it is 0.000 percent in both arms. The no-band
sensitivity arm is worse still at 19.98 percent below floor and 3.24 percent out the x
band, which is why it is a sensitivity arm and not the headline configuration.

**The strongest downstream consequence is about the verdict rule, not the BC.** A
binary that will not move while the quantity under it moves 6.2x is an argument for
reporting gate-pass frequency rather than a persistence-gated pass/fail. The v0.5
recycle arm at 3.6x `slide_m`, still STUCK, is the cleanest example the project has.

Per the dispatch's step 9: nothing here was written into
`data/all_runs_inventory.csv` or `gates_results_all_runs.json`. No published verdict
would change under this BC, so there is nothing to escalate on that front.

---

## 7. Open for Josie

1. **Replication.** The pre-registered design already ran at N=5 per arm and everything
   reproduces bit-exact. A second set of draws would cost well under 1 SU. It is
   defensible and it is not obviously necessary. Not run without a decision.
2. **The idle idev.** Job `928087` on `c642-021` is holding a 2-hour `gh-dev`
   allocation with no remaining work. Not cancelled, since that is your call.
3. **The dispatch's branch pointer** should be corrected wherever it came from: this
   work is on `claude/r7-inflow`, not `claude/r8-bc-merge`.
4. **`roughly 5 SU`** in commit `a6e534a` is inconsistent with its own 0.24 node-hours
   and should read about 0.5 SU.
5. **Two of the four "if you only do three" items** downstream of this now point at
   reporting gate-pass frequency instead of a binary. That is a paper-shaping decision.

## 8. Reproduction

```bash
git -C /Users/josie/can-it-ford worktree add .claude/worktrees/r7-inflow claude/r7-inflow
rsync -a --exclude='rollout.npz' vista:/work/11603/jcerrell0629/vista/r7_inflow_918506/ /tmp/r7/
PY=/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3
W=/Users/josie/can-it-ford/.claude/worktrees/r7-inflow
$PY $W/analysis/inflow_vehicle_stats.py  --runs /tmp/r7 --json /tmp/runs.json
$PY $W/analysis/inflow_vehicle_tables.py --json /tmp/runs.json
```

Source of every number here: Slurm jobs `918501` and `918506`, partition `gh`,
2026-08-17/18; instrument at commit `5ecf725`, reduction at `claude/r7-inflow` tip
`57523c8`. Physics write-up `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md`.

Every number in this document is either read directly from a live file, log or
accounting record, or computed by the reduction scripts named above from the raw Vista
tree. Nothing is transcribed from the 08-18 write-up. The two claims most tempting to
relay were re-derived here rather than carried: the run-by-run direction (16 of 16
closed runs end row 250 closer to their start, max ratio 0.8264; 18 of 18 recycling
runs end further, min ratio 1.0566, zero violations either way) and the peak-artifact
fractions (86.5, 86.9, 42.9 percent), both of which reproduce exactly.

UNREVIEWED: no adversarial physics review was run against this document. The fleet-wide
subagent outage recorded in CLAUDE.md ended on 2026-08-20, so that path is available and
this is a choice not to have run it, not an inability.
