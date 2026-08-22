# Register-ready: the "7.3 to 7.7%" SDF range averages a solid grid with a drifting one

2026-08-16. D4, branch `claude/r5-physics`. **I have not edited the register or CLAUDE.md.**
Section 2 below is written to be absorbed verbatim; section 1 is the working behind it.

The affected statement appears in at least two places **[measured]**: CLAUDE.md item A-2
("The SDF error range is 7.3 to 7.7 percent, not 1.6 to 7.7") and the register's
corresponding entry. **A-2's own correction stands and is not disturbed here**: merging the
free-rigid late-window fit into this range is still wrong. What follows is a *further*
qualification of the 7.3 to 7.7 figure itself.

---

## 1. Working

Method: Flyvbjerg and Petersen blocking, `10.1063/1.457480`, implemented at
`simulation/r5_physics/blocking.py`, applied to the `f_series` stored in
`data/coupling_validation/c1sdf_*.json`, 160 samples each **[measured]**.

The published figure comes from `validate_coupling_force.py:789`,
`f_steady = float(fz[len(fz)//2:].mean())`. Three properties of that line matter:

1. the window is the **hand-chosen back half**, not a measured transient boundary;
2. the reported `F_steady_tail_std` is a **standard deviation, not a standard error of the
   mean**, so it is not an uncertainty on the quoted percentage;
3. no stationarity was demonstrated for the retained window.

**The point estimates are fine.** Blocking recovers 28897.7 N against the published
28898.4 N for `c1sdf_sdf_g64` **[measured]**. This is not a claim that the numbers are
wrong. It is that they had no valid uncertainty, and that the two grids behind the range
are not equally trustworthy.

**Caveat that bounds everything below.** My truncation rule minimises the blocked standard
error; it does **not** specifically target trend removal. A rule that minimised drift would
choose different exclusion points and could change the stationarity verdicts. That is why
the drift **magnitude** is reported beside every verdict rather than the bare word
"non-stationary".

---

## 2. Proposed register entry, verbatim-absorbable

> **The "7.3 to 7.7 percent" SDF-collider buoyancy range must not be quoted as a single
> range. Verified 2026-08-16 by blocking analysis of the stored `f_series`.** The two grids
> behind it are not equally supported, and the range as written averages a well-behaved
> measurement with one taken on a still-drifting window.
>
> The published numbers come from `validate_coupling_force.py:789`, a mean over the
> **hand-chosen back half** of the series, `fz[len(fz)//2:]`, reported with a standard
> deviation rather than a standard error of the mean. Blocking (Flyvbjerg and Petersen
> 1989, `10.1063/1.457480`) supplies the missing uncertainty and a measured transient
> boundary. The point estimates barely move, so this is a qualification of the range, not a
> refutation of the values.
>
> | run | published | blocked mean and SE | residual drift over the retained window | drift as a fraction of the error being claimed |
> |---|---|---|---|---|
> | `c1sdf_sdf_g96` | +7.2804% | **+7.3449% +/- 0.0750%** | -0.531% of the mean | **0.072x** |
> | `c1sdf_sdf_g64` | -7.6682% | **-7.6704% +/- 0.5422%** | +4.392% of the mean | **0.573x** |
>
> **At g96 the residual drift is 0.07x the discrepancy being reported, which is
> negligible. At g64 it is 0.57x: the "steady" force is still drifting by more than half
> the size of the effect being measured.** The g96 number is well supported. The g64 number
> rests on a window that has not stopped moving. Quote them separately, each with its
> standard error and its drift ratio; do not quote "7.3 to 7.7 percent" as one validated
> band.
>
> Supporting quantities, all measured from the same series:
>
> * Correlation makes the naive route wrong by about 2.7x. SE inflation over the naive
>   estimate is **2.45x** at g64 and **2.69x** at g96, with integrated autocorrelation times
>   of **6.0** and **7.3** frames. Dividing the published `F_steady_tail_std` by `sqrt(n)`
>   would therefore have understated the true error by roughly that factor.
> * Measured transient exclusion is **49 of 160** frames at g64 (111 retained) and **33 of
>   160** at g96 (127 retained), against the published window's fixed 80.
> * Both series are **non-stationary at 2 sigma** after exclusion, on both a halves test and
>   a trend test. Given how tight the blocked errors are, that verdict must always be read
>   with the drift magnitudes above rather than on its own.
>
> The box-collider path, reported for completeness and unchanged in its headline:
> `c1sdf_box_g96` **-21.3386% +/- 0.1627%**, drift ratio 0.110x; `c1sdf_box_g64`
> **-37.9124% +/- 1.3882%**, drift ratio 0.595x, **and its transient search hit the 50%
> cap**, meaning the rule wanted to discard more of the series than exists. That run's
> figure should carry an explicit "window not established" note.
>
> Caveat travelling with this entry: the truncation rule minimises the blocked standard
> error, not the trend, so the exclusion points and the stationarity verdicts are
> conditional on that rule. The drift magnitudes are not.
>
> Working and reproduction command: `docs/R5_PHYSICS_SDF_RANGE_CORRECTION.md` and
> `docs/R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md` section 3, tool at
> `simulation/r5_physics/blocking.py`. **UNREVIEWED**: no physics-skeptic pass has run.

---

## 3. Reproduction

```
cd /Users/josie/can-it-ford/.claude/worktrees/r5-physics
<venv>/bin/python simulation/r5_physics/blocking.py \
  --forces /Users/josie/can-it-ford/data/coupling_validation/c1sdf_*.json \
  --out <path>.json
```

The venv is any Python with numpy; no system Python on this Mac has it, so build one with
`uv venv` and `uv pip install numpy`. No GPU, no TACC access, no network.

**UNREVIEWED.** Not to be promoted to the register until a physics-skeptic pass runs.
