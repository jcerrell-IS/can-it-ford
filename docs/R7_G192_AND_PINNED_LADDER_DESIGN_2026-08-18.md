# R7: g192 collected, and a pinned ladder that buys BOTH controls

Measured 2026-08-18. Every number below was produced by
`analysis/r7_ladder_grade.py` against files fetched live from Vista, or by the
verification block reproduced at the end. Nothing here is carried from a summary.

## 1. Job 918351 (g192) is collected, and it is a SECOND independent STUCK

`$WORK/r6_rep_g192_918351`, COMPLETED, elapsed 00:10:50, 5 repeats, 90 frames.
All five `metrics.csv` are 92 lines (header plus 91 rows, last `t` = 3.0 s at
30 fps, the canonical horizon) and all five are bit-distinct.

```
g192_m2337   5 repeats   dx 0.0490716   water_layers 12   n_water 1594532
verdicts     STUCK x5      joint frames [0,0,0,0,0]      margin [-3,-3,-3,-3,-3]
```

**The g160 flip is not a single-rung artifact.** Two independent grids now give
STUCK 5 of 5 with zero joint SLIDE frames, in 10 runs total.

### The complete ladder, all six rungs regraded through one code path

| grid | layers | dx (m) | n_water | verdict (N=5) | joint frames | margin |
|---|---|---|---|---|---|---|
| g48  | 3  | 0.1962863 | 18194   | SLIDE 5/5 | 11,11,11,11,11 | 8 |
| g64  | 4  | 0.1472147 | 48367   | SLIDE 5/5 | 9,9,9,**10**,9 | 6, one 7 |
| g96  | 6  | 0.0981431 | 180067  | SLIDE 5/5 | 3,**4**,3,**4**,3 | 0 to 1 |
| g128 | 8  | 0.0736074 | 450912  | SLIDE 5/5 | 3,3,3,3,3 | 0 |
| g160 | 10 | 0.0588859 | 906806  | **STUCK 5/5** | 0,0,0,0,0 | -3 |
| **g192** | **12** | **0.0490716** | **1594532** | **STUCK 5/5** | **0,0,0,0,0** | **-3** |

**GRADER VALIDATION, done before the new rung was graded.** `r7_ladder_grade.py`
was first run against g160, whose answers were already published, and reproduced
all five of them exactly (STUCK 5/5, joint 0, margin -3, dx 0.05889, n_water
906806). It then reproduced g48, g64, g96 and g128 against R6's table, including
g64's single minority draw of 10 and g96's 3,4,3,4,3. Only after that was g192
graded. The classifier is the project's own `simulation/failure_modes.py` at
`ssf = 1.42`, `G = 9.81`.

**NO TRUNCATION WAS APPLIED.** These 90-frame runs already end at the canonical
horizon, so the full file is the correct window. `r6_repeat_stats.py` needed its
`_truncate` helper only because job 917797's repeats were 250-frame runs. The
grader asserts the 92-line length and reports any file that differs, rather than
trimming a file that is already the right length and silently losing a row.

### `sustain_frames` sensitivity, extended

| grid | sf=3 (published) | sf=4 | sf=5 |
|---|---|---|---|
| g48  | 5 SLIDE | 5 SLIDE | 5 SLIDE |
| g64  | 5 SLIDE | 5 SLIDE | 5 SLIDE |
| g96  | 5 SLIDE | 2S / 3K | 0S / 5K |
| g128 | 5 SLIDE | **0S / 5K** | 0S / 5K |
| g160 | 5 STUCK | 5 STUCK | 5 STUCK |
| g192 | **5 STUCK** | **5 STUCK** | **5 STUCK** |

g192 reproduces g160's behaviour: with 0 joint frames the verdict is STUCK at
every threshold tested. The `sustain_frames` fragility is confined to g96 and
g128 and is absent at both ends of the ladder.

## 2. THE CONFOUND IS TOTAL IN THIS DATASET. It cannot be argued away.

Per-step geometry, computed from the run summaries rather than from prose:

| step | span | plan area | layers | margin |
|---|---|---|---|---|
| g48 to g64   | +5.00 % | +10.25 % | +1 | -2 |
| g64 to g96   | +4.76 % | +9.75 %  | +2 | -6 |
| g96 to g128  | +2.27 % | +4.60 %  | +2 | 0  |
| g128 to g160 | +1.33 % | +2.68 %  | +2 | -3 |
| g160 to g192 | +0.88 % | +1.76 %  | +2 | 0  |

Totals across the full ladder are **+15.00 % in span and +32.25 % in plan area**,
which supersedes the g48-to-g128 figures of +12.5 % and +26.6 %: those were
correct for the four-rung ladder and the ladder is now six rungs.

**A tempting argument, and it does not work.** It is tempting to note that the two
largest tank-growth steps (+10.25 % and +9.75 %) produced no flip while the flip
landed on a step of only +2.68 %, and to call the tank exonerated. That argument
fails: plan area and particle layers are **both monotone increasing in n** across
every rung, so they are perfectly rank-correlated and no ordering or rate argument
on this dataset can separate them. A threshold or nonlinear response in area
reproduces the observed pattern just as well as one in resolution.

**So the confound stands exactly as R6 stated it.** Keep saying "the verdict flips
under a refinement that also enlarges the tank". The one thing the new rung adds
is that the g160-to-g192 step changes the tank by under 1 percent in span while
changing resolution by 20 percent in layers and 76 percent in particle count, and
the verdict does not move. That is a consistency result, not a discriminating one,
because both rungs are already STUCK.

## 3. A PINNED LADDER THAT BUYS BOTH CONTROLS, not one or the other

R6 framed this as a trade-off: pinning the interior span in metres moves the
realized water depth, so you choose which control to buy. **That framing is
avoidable.** The trade-off is real for the default doubling sequence, but it
disappears if the grid sequence itself is chosen.

Pinned span `S` requires `lim_n = S*n/(n-8)`, so `h = S/(2(n-8))`, and preserving
the unpinned ladder's realized depth `L*h = 3*h_48` forces `L = 3(n-8)/40`.
Since `gcd(3,40) = 1` that is integral exactly when `40 | (n - 8)`.

Verified live by calling the wrapper's own `predict()` at `S = 7.851451928106 m`:

| n | lim | dx | h | span | layers | realized depth | dev |
|---|---|---|---|---|---|---|---|
| 48  | 9.421742 | 0.1962863 | 0.0981431 | 7.851452 | 3  | 0.2944294473 | exact |
| 88  | 8.636597 | 0.0981431 | 0.0490716 | 7.851452 | 6  | 0.2944294473 | exact |
| 128 | 8.374882 | 0.0654288 | 0.0327144 | 7.851452 | 9  | 0.2944294473 | exact |
| 168 | 8.244025 | 0.0490716 | 0.0245358 | 7.851452 | 12 | 0.2944294473 | exact |
| 208 | 8.165510 | 0.0392573 | 0.0196286 | 7.851452 | 15 | 0.2944294473 | exact |

`span` is one distinct value across all five rows, and the realized depth equals
the unpinned ladder's 0.2944294473039918 m at every rung. **Both controls held
simultaneously.** The default sequence does not do this: n = 64, 96, 160 and 192
move the depth by -4.76 %, +6.06 %, +5.26 % and +1.45 % respectively.

**Why this ladder is decisive.** The unpinned flip sits between 8 layers (g128,
SLIDE, margin 0) and 10 layers (g160, STUCK, margin -3). The pinned ladder
brackets that with 9 layers at n=128 and 12 layers at n=168, at constant tank and
constant depth.

- If the pinned ladder **still flips** between n=128 and n=168, the tank is
  excluded and the flip is a resolution result.
- If it **does not flip at any rung**, tank growth was doing the work and the
  g160/g192 STUCK is a domain artifact.
- Either outcome is written up identically.

### Cost, measured not estimated

The entire existing six-rung ladder, 30 runs, cost 24 min 31 s of node time
(sacct elapsed: 0:59, 1:07, 1:50, 3:24, 6:21, 10:50). At roughly 20 SU per
node-hour that is about 8 SU against a Vista balance of 617.

**Correction to the R6 handoff on one point.** It states the pinned control is
"CHEAPER than the confounded experiment it replaces" because every dx is finer at
the same n. The cost does not follow: the water column count is `2n - 16`
independent of `lim`, so pinning does not change columns, while a smaller `lim`
raises the layer count. The n=208 rung is about 2.39 M water particles against
g192's 1.59 M, so the pinned ladder is somewhat MORE expensive per rung at the
fine end, not less. It is still cheap in absolute terms, roughly 10 to 12 SU.

## 4. Verification block

```
git -C /Users/josie/can-it-ford log --oneline -1 claude/can-it-ford-round-5-87a6d6
bash /Users/josie/can-it-ford/scripts/tacc.sh --status
/opt/homebrew/bin/uv run --with numpy python3 analysis/r7_ladder_grade.py \
    --reps <dir of rep_*/metrics.csv> --mass 2337
```

Ladder files were fetched from `$WORK/r6_rep_{g48,g64,g96,g128,g160,g192}_{918250,
918249,918248,918247,918350,918351}/rep_{1..5}/`. The 2 GB `rollout.npz` per
repeat were deliberately left on Vista; only `metrics.csv` and `summary.json`
were transferred.

**Still open and unchanged by this round:** the pinned-span control has not run.
Until it does, no resolution claim from this ladder is publishable.
