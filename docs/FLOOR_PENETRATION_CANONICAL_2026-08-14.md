# Does the floor-penetration plateau transfer to the canonical scene?

**Answer: NO, on the penetration criterion, and the ~50 percent corrupted-column
inference does not hold.** Dispatch 12 Part C, 2026-08-14, branch
`claude/fork-protocol`.

Tags: **[read]** direct source read, **[measured]** run live today, **[cited]**
external literature not re-verified here, **[inferred]** reasoning from those.

---

## The question, as posed

- **MEASURED elsewhere:** penetration saturates at **0.93 to 1.01 dx** in the MOVING
  scene **[cited, from the dispatch]**.
- **MEASURED LIVE here:** canonical g64 has `realized_depth_m / dx = 0.2944294473 /
  0.1472147237 = 2.000` cells across the water depth **[measured]**.
- **INFERRED AND EXPLICITLY NOT TO BE ASSERTED:** if that penetration is a property of
  the enforced plane BC rather than of one scene, a corrupted fraction of about
  `1/depth_cells` puts roughly **50 percent** of the canonical column in a
  boundary-corrupted layer.

This document measures it instead.

## No GPU run was required

The dispatch budgeted "one small LS6 BATCH instrumentation run". None was needed and
none was submitted. `rollout.npz` already stores the **full water particle field for
every frame** (`water`, shape `(frames, n_water, 3)`) together with `floor`, `dx` and
`h` **[read, `sim_standing.py:485-499`]**. All 17 gated runs are present under
`renders/yaris_render_s1/_incoming/` **[measured]**. So the instrumentation the
dispatch describes already exists on disk, and measuring it there is strictly better
than a re-run: it measures **the published runs themselves**, not a new run that would
have to be argued equivalent to them.

Analysis: `analysis/floor_penetration_canonical.py`. Read-only over the canonical tree;
outputs land under this branch.

## Result 1: the numbers

All 17 canonical runs, penetration measured as `(floor - z)/dx` for water particles
below the plane **[measured]**.

| Grid | dx (m) | depth (cells) | runs | % particle-frames below plane | max pen (dx) | p99 (dx) | mean (dx) |
|---|---|---|---|---|---|---|---|
| g48 | 0.196286 | 1.500 | 3 | **0.0000** | 0.000 | n/a | 0.000 |
| g64 | 0.147215 | 1.5 / 2.0 / 3.0 | 11 | 9.55 to 12.57 | 0.273 to 0.321 | 0.244 to 0.272 | 0.067 to 0.126 |
| g96 | 0.098143 | 3.000 | 3 | **0.0000** | 0.000 | n/a | 0.000 |

**Six of seventeen runs have exactly zero penetrating particle-frames**, out of
4.91 million particle-frames at g48 and 48.6 million at g96 **[measured]**. Their
minimum water height sits *above* the plane throughout: g48_m1100 at `floor + 0.089 dx`
and g96_m1100 at `floor + 0.035 dx`, taken over all frames and all particles.

**The deepest penetration anywhere in the canonical set is 0.321 dx** (sweepV_g64_v3p0).
The moving-scene plateau is 0.93 to 1.01 dx. The canonical maximum is therefore about
**one third of the plateau's lower end**, and the mean penetration is 0.067 to 0.126 dx.

## Result 2: dx controls it, not depth-in-cells, and the control is already built in

This is the part that makes the answer more than one number. The mass sweep varies dx at
fixed realized depth; the depth sweep varies realized depth at fixed dx. Together they
**cross** the two variables, so they can be separated rather than confounded
**[measured]**:

| depth (cells) | dx = 0.098143 | dx = 0.147215 | dx = 0.196286 |
|---|---|---|---|
| 1.500 | - | **12.37 %** (sweepD_g64_d0p25) | **0.00 %** (g48) |
| 2.000 | - | 12.57 % (g64 / sweepV) | - |
| 3.000 | **0.00 %** (g96) | **9.55 %** (sweepD_g64_d0p45) | - |

Read the first and last rows. A **1.500-cell** column penetrates 12.37 percent at
dx 0.1472 and 0.00 percent at dx 0.1963. A **3.000-cell** column penetrates 9.55 percent
at dx 0.1472 and 0.00 percent at dx 0.0981. Depth-in-cells is held fixed across each
pair and the outcome flips completely, so **depth-in-cells is not the controlling
variable**. Every run at dx = 0.1472147 penetrates and no run at either other dx does.

Consequently the corrupted fraction is **not** `1/depth_cells`, and the specific
inference that a 2.000-cell column implies ~50 percent corruption **fails its own
test**: the 3.000-cell g64 run penetrates *more* than the 1.500-cell g48 run, which
penetrates not at all.

## Result 3: it is floor-wide, not a vehicle artifact

Where penetration occurs it is spatially uniform over the tank floor, so it is a
property of the boundary rather than of the coupling **[measured, g64_m1100]**:

| frame | % below | under-vehicle share | inflow-band share | open-floor share |
|---|---|---|---|---|
| 0 | 4.83 | 6.00 | 21.08 | 72.92 |
| 3 | 17.49 | 9.55 | 18.50 | 71.95 |
| 20 | 10.80 | 12.69 | 14.22 | 73.09 |
| 89 | 12.72 | 5.80 | 0.76 | 93.44 |

against area shares of **11.09 percent** under the vehicle and 18.19 percent in the
inflow band. The under-vehicle share of penetrating particles tracks the under-vehicle
*area* share, and the open-floor share tracks the open-floor area share. Penetration is
not concentrated beneath the hull.

## Result 4: the mechanism hypothesis is not supported here

Steffen, Kirby and Berzins 2008 (10.3970/CMES.2008.031.107) is the strongest
mechanistic anchor available, and it systematically varies basis functions, boundary
treatments and GIMP smoothing length **[cited]**. If penetration is a kernel-support
effect, it scales with basis support width, which is measured in cells, so it should be
**constant in dx units** across the three grids.

Measured mean penetration in dx units across g48 / g64 / g96: **0.000 / 0.079 / 0.000**
**[measured]**. That is non-monotone, and it is constant in neither dx units nor metres,
so **neither** a constant-in-dx nor a constant-in-metres mechanism describes it. The
analysis script now says exactly that rather than naming a winner; an earlier version
computed a coefficient of variation over NaNs and printed "supports H_phys", which was
a false conclusion drawn from two grids that in fact showed no penetration at all.

Steffen 2008 does not establish our plateau **[cited]** and this measurement does not
establish its mechanism either. The question stays open.

## The confound, stated because it bounds the whole answer

`sim_standing.py:248-267` (`_project_water`) **hard-clamps every water particle to
`z >= floor - 0.25*dx` at the start of every frame, and zeroes its downward velocity**
**[read]**. So:

- Accumulated penetration in the canonical scene is **capped at 0.25 dx by the driver**,
  not by the physics. The scene is structurally incapable of reaching a 0.93 dx plateau.
- The clamp runs *before* `solver.step()` while the recorded position is read *after*
  it, so within-frame excursions past the clamp are still recorded in full. That is
  where the 0.27 to 0.32 dx maxima come from, and it is why the distribution has a hard
  edge just past 0.25 dx with **no accumulation at 0.25 dx itself** (measured directly:
  zero particles within 1e-4 of the clamp value at frame 10).

**Therefore this measurement cannot refute the moving-scene plateau.** It shows the
plateau is not realized in the canonical scene, and it cannot show what the canonical
scene would do without the clamp. What the clamp emphatically **cannot** explain is the
exact zeros at g48 and g96: a clamp can only stop particles going deeper, never keep
53.5 million particle-frames strictly above the plane.

## What this does and does not license

**Licensed:** the canonical 2.000-cell scene is not boundary corrupted *in the sense the
inference feared*. The sub-plane region is at most 0.32 dx deep at worst, i.e. **16
percent of a 2.000-cell column by depth, not 50 percent**, and it is 0 percent at two of
the three grids.

**Not licensed:** "the canonical scene is uncorrupted". Penetration depth is a **lower
bound** on the disturbed region, not a measurement of it. Schulz and Sutmann 2019 report
traditional grid-based boundary treatment distorting stress **multiple grid lengths into
the body**, and Baumgarten and Kamrin 2023 (10.1002/nme.7217) analyse MPM spatial
integration errors; neither is validated for free-surface water and both are mechanistic
evidence only **[cited]**. A column only 1.5 to 3.0 cells deep also has no "bulk" to
compare a near-floor layer against, so a profile-based corruption test is not available
in this scene at all.

**Not attempted:** no correction or calibration. No paper reports an accepted correction
for a smeared near-wall layer, so inventing one and calling it standard is not on the
table **[cited]**.

## FLAG FOR A HUMAN, not actioned here

Per the dispatch, a finding that bears on a published result is flagged rather than
edited, and the register is outside this branch's write scope.

**F-1. Floor penetration is non-monotone in dx, and this is a new instance of a
non-monotonicity already on file.** CLAUDE.md item 5 records `final_disp_mag_m` moving
+87.8 percent from g48 to g64 then -59.2 percent from g64 to g96 for the 1100 kg arm.
Water floor penetration follows the same shape: absent, present, absent. That is a
second, independent observable showing the same non-monotone g48/g64/g96 signature, on
the same runs. It belongs with item 5. **Owner: whoever holds the register (D4).**

**F-2. `C2_veh_zmin_rise` does not mean the hull sank below the floor.** CLAUDE.md item
7 states "All three g48 runs also fail P-3 with a negative z rise near -0.05 m, the hull
sank into the floor plane." Measured live, `C2_veh_zmin_final - floor` is **0.0000 dx
for all 17 runs** **[measured]**, i.e. the hull bottom ends exactly *at* the plane, never
below it. The vehicle is spawned at `floor + 0.5*h` **[read, `sim_standing.py:175`]**,
so a rise of about `-0.5*h` is the hull **settling onto** the floor from its spawn
offset, and `0.5*h` at g48 is 0.0491 m, which matches the observed -0.043 to -0.054 m.
The gate outcome is not in question; the *interpretation* "sank into the floor plane"
is, and it reads as a penetration claim that the data do not support. **Owner: D4.**

Neither finding changes any verdict. Both are recorded here rather than in the register.

## Reproduce

```
python analysis/floor_penetration_canonical.py \
    --incoming /Users/josie/can-it-ford/renders/yaris_render_s1/_incoming \
    --out data/floor_penetration_2026-08-14
```

Outputs `floor_penetration_by_run.{json,csv}` and `penetration_ladder_verdict.json`.
Requires numpy only. Runtime is a few minutes on a laptop, dominated by reading
~1.5 GB of stored rollouts.

**Stated assumption, reversible:** `renders/yaris_render_s1/_incoming/` is taken as the
canonical per-run tree per register D4a. All 17 gated run names resolve there and
nowhere else in this clone **[measured]**. The nine `g48_*`/`g64_*`/`g96_*` and eight
sweep directories were named explicitly in the script rather than globbed, so a stray
directory cannot silently enter or leave the population.
