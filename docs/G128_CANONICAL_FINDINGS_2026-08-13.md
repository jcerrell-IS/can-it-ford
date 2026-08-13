# The canonical mass sweep at g128: register J15's direct test

**Engine: warpmpm**, `renders/yaris_render_s1/sim_standing.py:10-12`, on the **material-8
free-rigid** path. Not Genesis. Not the SDF-collider path.

LS6 jobs **3362573** (primary) and **3362619** (independent repeat), both
`gpu-a100-dev`, node `c301-001`, `COMPLETED 0:0` in 6:15 and 4:37. Driver sha256
`4696c3b2d39f...`, byte-identical to `/Users/josie/can-it-ford/renders/yaris_render_s1/
sim_standing.py`. Twelve runs total, all `rc=0`.

Register J15 states: *"The direct test has never been run: the canonical set does not
exist at g128."* It does now, for the mass sweep.

---

## 1. Headline, scoped precisely

**None of the three replicated mass-sweep verdicts flips between g96 and g128. All
remain SLIDE.** Reproduced in both jobs.

**This is 3 of the 17 canonical configurations.** The 3 `sweepD` and 5 `sweepV` runs,
including `sweepV_g64_v0p5`, the only STUCK run in the set, still have **no g128
counterpart**. And these are new runs: a canonical verdict cannot itself flip, only a
replication of it can.

So the Silverado result (SLIDE at g64/g96, STUCK at g128, register J15) does **not**
reproduce on the Yaris mass sweep. The verdict is resolution-dependent for that vehicle
and not, at this refinement, for these three.

| run | grid | mass | mode | ratio_slide | drift_m | onset | margin_frames | k_crit |
|---|---|---|---|---|---|---|---|---|
| canon_g96_m1100 | 96 | 1100 | SLIDE | 5.3724 | 0.2686 | 3 | 15 | 0.2562 |
| canon_g96_m1609 | 96 | 1609 | SLIDE | 3.1075 | 0.1554 | 3 | 7 | 0.4382 |
| canon_g96_m2337 | 96 | 2337 | SLIDE | 1.7143 | 0.0857 | 5 | **1** | 0.8721 |
| canon_g128_m1100 | 128 | 1100 | SLIDE | 9.4704 | 0.4735 | 3 | 39 | 0.1687 |
| canon_g128_m1609 | 128 | 1609 | SLIDE | 3.5580 | 0.1779 | 4 | 11 | 0.3721 |
| canon_g128_m2337 | 128 | 2337 | SLIDE | 1.4734 | 0.0737 | 6 | **0** | **0.9759** |

## 2. The actual finding: the heaviest arm is now at the boundary

`g128_m2337` has **`margin_frames` = 0**. It holds the joint SLIDE condition
(`|dx| >= 0.05` AND `|vx| >= 0.05`) for exactly the 3 consecutive frames the classifier
requires, and no more. Enumerated: the joint condition is met on frames 6, 7, 8 and
nowhere else, a single run. Removing any one of those three frames leaves no window of 3
and the verdict becomes STUCK.

**`k_crit` is the number to quote alongside it.** `margin_frames` counts discrete frames
and understates the closeness; `k_crit` is the multiplicative weakening that would flip
the run:

| arm | margin_frames | k_crit | headroom | weakening needed to flip |
|---|---|---|---|---|
| g96_m2337 | 1 | 0.8721 | 1.147x | **12.8 percent** |
| g128_m2337 | 0 | 0.9759 | 1.025x | **2.4 percent** |

The binding frame at g128 is frame 6, where `|dx| = 0.05124` against `slide_m = 0.05`.
**The heaviest canonical arm survives refinement to g128 by 2.4 percent.**

Note the asymmetry that `margin_frames` alone hides: margin 1 at g96 does not mean "8
percent from flipping". Killing that arm's weakest frame still leaves exactly 3, so g96
needs 12.8 percent. Quote both metrics or the reader will mis-scale them.

## 3. The four-grid ladder, and a correction to my own first reading

My first pass called this "the lighter masses strengthen with refinement while only the
heaviest weakens." **That was wrong, and it was wrong because I read two points where
four exist.** Adversarial review caught it. With the frozen g48/g64/g96 store included:

| mass | g48 | g64 | g96 (frozen) | g128 (new) | steps |
|---|---|---|---|---|---|
| 1100 | 6.9142 | 13.3068 | 5.3854 | 9.4704 | +92.5%, **-59.5%**, +76.3% |
| 1609 | 5.0211 | 6.4287 | 3.1323 | 3.5580 | +28.0%, **-51.3%**, +14.5% |
| 2337 | 3.6205 | 2.8393 | 1.8005 | 1.4734 | -21.6%, -36.6%, -14.1% |

m1100 and m1609 **oscillate**. The +76.3 percent g96-to-g128 step for m1100 has the same
sign and nearly the same magnitude as its g48-to-g64 step, which the next refinement then
reversed by -59.5 percent. Two points cannot establish a trend inside an oscillation of
that amplitude.

**Only m2337 is monotone, across all four grids: -21.6, -36.6, -14.1 percent.** That is
the defensible statement, and it is *stronger* than what I first claimed, because it is
the arm at the boundary.

This is register item 5's non-monotonicity, now extended to a fourth grid. Cite the
verdict and `margin_frames`, never the magnitude. The citable mechanism is **Steffen,
Kirby and Berzins 2008** (register L-5): MPM loses convergence under grid refinement at
fixed particles-per-cell. PPC here is constant at 8 (`h = dx/2`,
`sim_standing.py:163`), which is exactly the case that paper addresses.

## 4. Reproducibility, measured rather than assumed

Job 3362619 repeated all six arms independently on the same node.

**The runs are not bit-reproducible.** All six `metrics.csv` differ between jobs, despite
identical config, identical node and identical driver sha, and despite every run's own
`determinism_identical` flag reporting `True`. That flag does not detect this.

**But the spread is small and the verdict metrics are stable:**

| arm | ratio job1 | ratio job2 | delta | margin job1 | margin job2 |
|---|---|---|---|---|---|
| g96_m1100 | 5.3724 | 5.4140 | +0.77% | 15 | 15 |
| g96_m1609 | 3.1075 | 3.1279 | +0.66% | 7 | 7 |
| g96_m2337 | 1.7143 | 1.7140 | -0.02% | 1 | 1 |
| g128_m1100 | 9.4704 | 9.5030 | +0.34% | 39 | 39 |
| g128_m1609 | 3.5580 | 3.5574 | -0.02% | 11 | 11 |
| g128_m2337 | 1.4734 | 1.4869 | +0.92% | **0** | **0** |

**`margin_frames` is identical in all six.** So `margin 1 -> 0` is a reproduced property,
not a single draw. Same-node run-to-run spread on `ratio_slide` is **under 1 percent**.

**This settles a causal question.** My in-job g96 arms differ from the frozen store by
-0.24 percent (m1100), -0.79 percent (m1609) and **-4.79 percent** (m2337). Since
same-node run-to-run variation is under 1 percent, the 4.79 percent gap is **not**
run-to-run non-determinism. It spans Vista GH200 to LS6 A100, a driver revision, and a
different engine checkout. Describe it as "differs by 4.8 percent across a change of
machine, driver and engine build", never as a non-determinism measurement.

Worth noting on its own: **the least reproducible of the three g96 arms is the most
fragile one.**

## 5. A containment gate fails, and it fails on the arm with the largest number

`canon_g128_m1100` **FAILS gate P-2**: `passthrough_max_frac` 0.11159 against the 0.10
limit at `gates.py:146-148`. Reproduced at 0.11155 in the repeat job.

That is the arm carrying the +76.3 percent ratio. **Treat it as containment-failed, not
as a result.** Water passing through the hull is exactly the artefact that would inflate
a drag-driven surge.

All other eleven runs pass P-2 (0.0797 to 0.0944). All twelve pass P-3
(`C2_veh_zmin_rise` = 0.0, no sinking into the floor). The m1100 configuration also fails
P-2 at g48 and g64 in the canonical set (register item 7), passes at g96, and fails again
at g128: non-monotone in the same way its ratio is.

## 6. What is invariant, and what is not

**Realized water depth is exactly invariant**, which was the confound I was most worried
about and it does not hold:

| arm | floor = 3dx | water layers | realized_depth_m | depth/dx |
|---|---|---|---|---|
| g96 | 0.2944294 | 6 | 0.2944294473 | 3.000 cells |
| g128 | 0.2208221 | 8 | 0.2944294473 | 4.000 cells |

`0.2944294473` is the same value `data/all_runs_inventory.csv` carries for g48/g64/g96,
so depth is held exactly across all four grids. `grid_lim` is identical
(9.421742313727737) because the hull is identical. Depth, velocity, eta, floor_friction,
bulk_modulus, sound speed and frame count are identical across all twelve runs.

**But the domain is not scale-invariant.** `wall = 4.0*dx` (`sim_standing.py:178`) and
`_inflow_x = wall + inflow_len` (`:223`), so refining shrinks the walls and grows the
tank:

| quantity | g96 | g128 | change |
|---|---|---|---|
| tank side | 8.6366 m | 8.8329 m | +2.27% |
| water volume | 21.2777 m3 | 22.4784 m3 | +5.64% |
| inflow-to-hull fetch | 3.7605 m | 3.8586 m | +2.61% |
| displaced hull volume | 3.521799 m3 | 3.547147 m3 | +0.72% |

These are 0.7 to 5.6 percent against observed ratio changes of 14 to 76 percent, so they
are unlikely to dominate, but **they are not bounded and this is therefore not a pure
grid refinement.** Blockage ratio shifts with them, which bears on open register item J13.

**The settle is fixed-duration, not gated.** `settle_frames = 8` (`sim_standing.py:235`).
Residual velocity at t=0 is 2.4 to 2.9 times larger at g96 than g128 (`vmag` 0.078105 vs
0.030115 for m2337). For the arm carrying the finding the surge channel is barely
contaminated, residual `vx` being 0.27 percent of peak at g96_m2337 and 0.17 percent at
g128_m2337, but it reaches 2.3 percent for g128_m1100. **Do not describe the initial
conditions as matched.**

## 7. Mandatory caveats on anything built from this

- **Free-rigid coupling.** These runs use the material-8 path, which forms no force
  (register A3, J1). This refines an independently flawed coupling. **Do not import the
  SDF-collider validation (7.3 to 7.7 percent) as support**: different path. And never
  quote the g96 SDF result, which hit the 900-frame settle cap, as equally reliable.
- **Artificial sound speed 12.845 m/s**, `sqrt(1.1*150000/1000)` from
  `sim_standing.py:225`, about 117x below real water, flow near Mach 0.117. Any
  surge-magnitude claim inherits this. The sound-speed sweep is already done, jobs 895330
  and 895378; do not propose it as untested.
- **Masses.** 1100 / 1609 / 2337 kg on ONE Yaris hull; `n_vehicle` is identical across
  the three masses at each grid (29804 at g96, 71155 at g128), confirming geometry never
  changes. Only 1100 has a source in `vehicle_params.py` (register item 10).
- **Provenance.** The twelve manifests are now stamped by
  `analysis/run_provenance.py --backfill --write` (snapshot taken first to
  `~/can-it-ford-manifest-backup-2026-08-13/g128_manifests_pre_backfill.tar.gz`).
  `solver_git_sha` is labelled *resolved from the pin*. That label is defensible here and
  was checked rather than assumed: the LS6 engine's
  `src/warpmpm/kernels/mpm_solver_warp.py` has sha256 `2851393950...`, **byte-identical**
  to the vendored `third_party/mpm-engine-544c93dd-solver-core/kernels/
  mpm_solver_warp.py`. The engine checkout's git HEAD is `627367ec`, not `544c93dd`, so
  the *solver kernel* is provably the pinned one while the *engine tree* is not.

## 8. What this does and does not settle for J15

**Settles:** the mass sweep does not flip between g96 and g128, and the heaviest arm's
margin closes to zero rather than crossing. "16 SLIDE / 1 STUCK" survives one further
refinement on 3 of its 17 configurations.

**Does not settle:** 14 configurations remain untested at g128, including the only STUCK
run. The heaviest arm sits 2.4 percent from flipping, and its trend is monotone toward
the boundary, so g192 or g256 is the obvious next test and is cheap (six runs cost 6:15).
J15 should stay open, with its scope narrowed rather than closed.

**Recommended wording wherever the figure is published**, unchanged in spirit from J15:
16 SLIDE / 1 STUCK is not established as grid-converged. It is now additionally known
that the heaviest mass-sweep arm reaches `margin_frames` 0 at g128.
