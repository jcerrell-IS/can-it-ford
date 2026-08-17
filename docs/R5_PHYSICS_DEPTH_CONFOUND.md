# D4: the velocity sweep is also a depth sweep, and the labels are not the depths

> ## CORRECTED BY MY OWN FOLLOW-UP, 2026-08-17. The headline drops from 2.6x to 1.8x.
>
> Section 5 of the first version flagged that I had not read `local_depth_footprint`'s
> definition. I read it, and it contains a confound I had not anticipated
> **[read, `sim_standing.py:473-475`]**: the selection window is the vehicle's **current**
> bounding box, `lo_v`/`hi_v`, which **slides downstream with the vehicle** into the very
> pile-up whose depth it is measuring. So the diagnostic entangles the water getting deeper
> with the measurement window moving into deeper water.
>
> I separated them by recomputing the identical statistic (same 99.5th percentile, same
> floor datum, same `>= 20` guard) over the vehicle's **frame-0 footprint held fixed**.
> Script committed at `simulation/r5_physics/depth_station.py`. Velocity sweep, all
> labelled 0.30 m, settle 8 **[measured]**:
>
> | v (m/s) | moving window | **fixed station** | drift (m) |
> |---|---|---|---|
> | 0.5 | 0.2341 | **0.2400** | 0.050 |
> | 1.0 | 0.2586 | **0.3139** | 0.225 |
> | 1.5 | 0.3313 | **0.3581** | 0.637 |
> | 2.0 | 0.4050 | **0.3832** | 0.992 |
> | 2.5 | 0.5002 | **0.4067** | 1.192 |
> | 3.0 | 0.6049 | **0.4356** | 1.326 |
>
> **The confound is real and still monotone, but it is 1.81x, not the 2.58x I reported.**
> Depth at a fixed station still runs from **-20% to +45%** of the 0.30 m label. My central
> claim survives; its size does not, and I overstated it by about 40%.
>
> **The remainder is a defect in the diagnostic itself, and it is worth its own line.** The
> gap between the moving and fixed readings correlates with vehicle drift at **+0.907**
> across the 17 runs **[measured]**. `local_depth_footprint` reads high exactly in
> proportion to how far the vehicle has travelled, so **anything downstream of that
> diagnostic inherits a drift-proportional bias**. The depth sweep is affected too: labels
> 0.35 and 0.45 read 0.4433 and 0.5201 on the moving window but **0.4055 and 0.4602** at a
> fixed station, and both of those runs drift more than 0.94 m.
>
> Everything below stands except the 2.6x figure and the per-run moving-window depths in
> section 4, which should be read as the fixed-station column above.

2026-08-17. Branch `claude/r5-physics`. Mac only, no GPU. Reproduce with
`simulation/r5_physics/spin_down.py` for the spin-down and with the snippet in section 5
for the depth figures.

Claim tags: **[read]** primary source this session, **[measured]** computed here from
local artifacts, **[unreviewed]** no skeptic pass.

---

## 1. How I got here

Chasing Option A, I read `simulation/coupling_force/inflow_outflow.py`, which turns out to
carry both a better blocker than the one I derived and a measured claim I had not seen
**[read]**. I set out to verify the measured claim and it reproduces, by a different route
and on a different quantity. It bears on every published verdict, so it gets its own
document.

## 2. The real Option A blocker, from the primary source

My own re-diagnosis said the blocker was mass conservation. **The file gives a better one**
**[read, `inflow_outflow.py:14-21`]**:

> Zhao et al.'s outflow is PRESSURE-CONTROLLED. Register B7, verified live:
> `grep -ci pressure kernels/mpm_solver_warp.py` returns 0 across 3,181 lines at pinned SHA
> 544c93dd. There is NO pressure field in warpmpm at any point. [...] A literal port would
> have to Dirichlet-constrain a field that does not exist.

That is structural and checkable, and it is a cleaner reason than mine: **the BC's control
variable does not exist in this engine.** Pressure lives only implicitly, per particle, via
`J = det(F)` inside the weakly compressible EOS. My "mass conservation" framing was not
wrong so much as beside the point.

**But the file's engine constraint does not bind, and that changes its conclusion.** It
argues **[read, `:25-30`]** that particle count is fixed at load, so "a naive inlet that
injects particles and an outlet that deletes them is not expressible without changing the
allocation, which would fork every gated run", and picks a recycling conveyor instead.

Deletion is not the only way to remove mass. `particle_selection` gates the P2G scatter at
six sites, `mpm_utils.py:922, 1049, 1157, 1173, 1380, 1472`, and
`mpm_solver_warp.py:1679 import_particle_selection_from_torch` writes that array at runtime
**[read]**. A deselected particle contributes nothing to `grid_m`, **at fixed allocation,
with no fork of any gated run**. That is exactly the register's own B7 recommendation,
which the same file quotes: "a depth-controlled outflow, **deactivating** particles above a
target free-surface height".

**So the substitute was chosen under a constraint that does not apply.** The recommended
path is depth-keyed **deactivation** via `particle_selection`, not the recycling conveyor,
which is additionally unsound as written because it never resets `particle_F`,
`particle_C` or `particle_Jp` and so carries the outlet's compression back to the inlet.
What is missing is only a public wrapper: `core/solver.py` mentions "selection" once, in an
unrelated device docstring **[measured]**.

## 3. The measured claim, reproduced independently

`inflow_outflow.py:47-52` cites `REALISM_UPGRADE_ASSESSMENT_2026-08-08` section 4: the
downstream surface rises 0.2729 to 0.6750 m, a 2.5x pile-up, and **only 20 of 90 frames sit
within +/-10% of the nominal 0.30 m depth**, so the vehicle spends 78% of the run at a
depth that is not its label.

I did not take that on trust. Measured from `rollout.npz`'s own `local_depth_footprint`
diagnostic, **all 17 runs, first retained frame 8** **[measured]**:

| | median | range |
|---|---|---|
| frames within +/-10% of the labelled depth | **19.5%** | 0.0% to 86.6% |
| footprint depth against nominal | **+15.6%** | -22.0% to +102% |

**14 of 17 runs have fewer than half their frames within +/-10% of their own label.** My
19.5% and the assessment's 22% agree closely, from different quantities and different
artifacts.

## 4. The finding that is new: the velocity sweep varies depth by 2.6x

This is what I had not seen anywhere, and it is the reason this document exists
**[measured]**. Median footprint depth across the velocity sweep, all labelled 0.30 m:

| run | nominal | realized footprint depth | vs label |
|---|---|---|---|
| `sweepV_g64_v0p5` | 0.30 | **0.2341** | **-22.0%** |
| `sweepV_g64_v1p0` | 0.30 | 0.2586 | -13.8% |
| `g64_m1100` (v = 1.5) | 0.30 | 0.3313 | +10.4% |
| `sweepV_g64_v2p0` | 0.30 | 0.4050 | +35.0% |
| `sweepV_g64_v2p5` | 0.30 | 0.5002 | +66.7% |
| `sweepV_g64_v3p0` | 0.30 | **0.6049** | **+102%** |

**Perfectly monotone in velocity, spanning 2.6x.** Faster inflow piles more water against
the closed downstream wall, and the vehicle sits in progressively deeper water.

**So the velocity sweep is not a velocity sweep. It is a velocity-and-depth sweep, and the
two are perfectly confounded.** Any quantity that varies monotonically across it cannot be
attributed to velocity from these runs alone.

That has an immediate target. CLAUDE.md item 7 records that the P-2 gate failure rate
"rises monotonically across the whole velocity sweep, 7.99 percent at 0.5 m/s to 15.88
percent at 3.0 m/s". P-2 is the maximum water fraction inside the vehicle bounding box.
**Water depth at the vehicle rises monotonically over the same runs, by a factor of 2.6.**
More water around a fixed box is the null explanation for more water inside it. I am not
claiming the depth confound accounts for the P-2 trend; I am claiming **the velocity
attribution is not established by these runs**, and that a depth-matched control is needed
to separate them.

The depth sweep is distorted too, though less dangerously: labels 0.25 / 0.35 / 0.45
realize footprint depths of **0.2403 / 0.4433 / 0.5201**, so the intervals are uneven and
the top of the range overshoots by 15.6%.

## 5. Reproduction

```python
import numpy as np, glob, os
for p in sorted(glob.glob(".../renders/yaris_render_s1/_incoming/*/rollout.npz")):
    z = np.load(p); nom = float(z["depth"])
    foot = np.asarray(z["local_depth_footprint"], dtype=float)[8:]   # settle 8
    print(os.path.basename(os.path.dirname(p)), nom, np.median(foot),
          np.mean(np.abs(foot - nom) / nom <= 0.10))
```

`local_depth_footprint` is the driver's own diagnostic, not a quantity I defined, so this
inherits whatever that diagnostic measures. I have not read its definition line by line and
that is the first thing to check before this is promoted anywhere.

## 6. What this does and does not touch

- **It does not touch the binary verdicts.** The 16 SLIDE / 1 STUCK verdicts are peak
  statistics on the vehicle's own kinematics; nothing here changes what the vehicle did.
- **It does touch what the runs are labelled as testing.** A run labelled "0.30 m depth,
  3.0 m/s" spent its measured window at 0.60 m. Any figure, table or caption that presents
  the velocity sweep as isolating velocity is overstating what was controlled.
- **It strengthens the case for Option A**, which is where I came in: a working outflow is
  the fix for the pile-up that causes the confound, and the file says exactly that at
  `:47-52`.
- **The STUCK run is the extreme case in the other direction**: `sweepV_g64_v0p5` sat at
  **-22%** of its labelled depth for **0.0%** of frames within +/-10%. My brake-state
  analysis used that run. The brake conclusion rests on a friction bound and peak
  kinematics, not on depth, so I do not believe it moves; but the run is not at the depth
  its label claims and that should travel with it.

## 7. Status

**[unreviewed]**: no physics-skeptic pass on this document. The two claims I would attack
first are the `local_depth_footprint` definition (section 5) and whether the P-2
monotonicity is separable at all from these runs (section 4).
