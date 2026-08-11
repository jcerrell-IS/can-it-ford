# Regime ladder results: rungs (b), (c), (d), plus Fix A and Fix B

Date: 2026-08-07. Executes `docs/REGIME_LADDER_DISPATCH_2026-08-07.md`, which executes
section 8 of `docs/C1_ROOT_CAUSE_2026-08-07.md`.

ADDITIVE. This file edits nothing. `docs/C1_ROOT_CAUSE_2026-08-07.md`,
`docs/COUPLING_VALIDATION_J1_2026-08-07.md` and
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` were not touched, and neither was
`simulation/validate_coupling_force.py`. Promotion into the register is for whoever owns
it, not for this file.

## 0. Provenance tiers

- **T1 READ LIVE BY THIS SESSION** at the stated path.
- **T2 MEASURED ON VISTA** in jobs `895648` and `895653`, or read out of a stored JSON
  under `$WORK/can-it-ford/data/coupling_validation/`.
- **T3 DERIVED** here, arithmetic shown so it can be rerun.

No claim in this file is tier "a doc said so". Where a number is quoted from
`C1_ROOT_CAUSE.md` it was re-read from the Vista JSON first and the re-read value is the
one given.

## 1. The one-line answer

At the exact gated water depth, with the gated floor restitution and the gated inflow, the
free rigid body's vertical acceleration carries **no measurable buoyant signal**: rung (d)
reads **0.14 to 0.18 percent** of the analytic partial-submersion value at g96 and g64.
Rung (b), the only rung where the floor is removed and the coupling is therefore
observable in isolation, reads **-9.25 percent** at g96, wrong in sign. The rung (b) and
rung (c) g64 arms did not settle and are discarded.

**Read section 5.3 before quoting the 0.14 to 0.18 percent as a defect.** In rungs (c) and
(d) the body rests on the floor, where the physically correct vertical acceleration is
zero, so a near-zero reading there is expected and is NOT by itself evidence of a broken
coupling. The rung that carries the evidence is (b).

## 2. What was run

Job `895653`, Vista, partition `gh`, node `c609-141`, `COMPLETED 00:01:38`, exit `0:0`,
all eight steps `rc=0` (T2). Superseded job `895648` (`00:01:44`) ran an earlier revision
of the harness; its rung (b) g64 arm crashed on the P2G guard and its rung (c) g64 arm was
an unsettled discard. Every number in this file comes from `895653` so that all six rungs
share one code revision, md5 `f650d762635fb3415d2cf202f5a5c979` of
`simulation/validate_coupling_force_ladder.py`, stamped into the job log (T2).

Total cluster cost of this dispatch: `00:01:44 + 00:01:38` on one node, about **0.056
node-hours**. `taccinfo` read 669 SU on BCS20003 before and after (T2).

Harness: `simulation/validate_coupling_force_ladder.py`, new, additive. It imports
`simulation/validate_coupling_force.py` read-only and never writes it. Its geometry
constants are AST-parsed out of that file rather than restated, and `_load_vcf()` asserts
the parsed values against the imported ones at run time, so the constant fork CLAUDE.md
item 16 warns about cannot open silently.

## 3. The rung geometry is the gated scene, not an invented one

Verified 5 of 5 EXACT at both grids against `data/all_runs_inventory.csv` (T1 for the CSV,
T3 for the ladder side):

| quantity | ladder g64 | gated `g64_m1100` | ladder g96 | gated `g96_m1100` |
|---|---|---|---|---|
| `grid_lim` | 9.421742313727737 | same | 9.421742313727737 | same |
| `dx` | 0.1472147236519959 | same | 0.0981431491013306 | same |
| `h` | 0.07360736182599795 | same | 0.0490715745506653 | same |
| water depth | 0.2944294473039918 | same | 0.2944294473039918 | same |
| water layers | 4 | 4 | 6 | 6 |

The depth match is not a coincidence and not a fit. `realized_depth_m` is
0.2944294473039918 m in **all 17** gated runs, and that is exactly `2 * DX_CANON`, so
`--depth-cells 2` lands on it to the last digit (T3). This also reproduces the 2-cell
waterline resolution CLAUDE.md L-3 records as a limitation, rather than quietly improving
it away.

Body: cube of side `L_BOX = 10*DX_CANON = 1.4721472365199588 m`, `rho_box = 600` unchanged
from C1, bottom face spawned on the floor plane. Nominal submerged fraction
`0.2944294/1.4721472 = 0.2000` exactly, so the analytic target is the exact negative of
C1's (T3):

```
a_ideal = g*(rho_w*h_sub/(rho_box*L) - 1)
C1, h_sub/L = 1:      9.81*(5/3 - 1) = +6.5400 m/s^2
rungs b/c/d, 0.2:     9.81*(1/3 - 1) = -6.5400 m/s^2
```

Realised submerged fractions after settle came out 0.186 to 0.211 rather than 0.200
because the settled free surface is not the nominal one, so each run's own
`a_ideal_partial` is computed from its own measured `h_sub` and is the value tabulated
below.

**Why the body must sit on the floor here, which is a property of the regime and not a
choice.** Twenty percent of the cube's height IS the entire 0.2944294 m water depth. A
20-percent-submerged body in 0.2944294 m of water therefore has its bottom face on the
floor. There is no configuration at the gated depth in which this body is partially
submerged and also clear of the floor.

## 4. Pre-registered predictions, and how they did

Stated in the harness docstring before the runs, so they could not be fitted afterwards.

**Prediction (b): `a_late_window` about 0, with a downward drift of order 0.1 m/s, not
-6.54 m/s^2.** Reasoning: C1_ROOT_CAUSE section 1 (T1) establishes the body has no
equation of motion, so `v_cm` is reassigned each substep to the mass-weighted mean grid
velocity at its own particles. Modelling that as a blend of a dry population at
`v + dt*g` and a wet population near zero gives the fixed point
`v* = f_dry*dt*g/(1 - f_dry)`, which is -0.1189 m/s at g64 and -0.0817 m/s at g96 (T3).

**Outcome: directionally right, quantitatively wrong by about 2.6x.** Measured
`v_mean_late` at rung (b) g96 is **-0.21757 m/s** against the predicted -0.0827 (T2).

**Why the prediction was too small, and this is the substantive finding of section 4.**
The blend model assumed the wet fraction is the submerged fraction by height. It is not.
`BoxTank.__init__` carves every water particle that falls inside the cube, and the cube's
bottom face is on the floor, so the carve removes **the entire water column under the
footprint**. Measured directly (T2, `water_under_body_at_release`): rung (b) and rung (c)
at g96 have **0** water particles under the body, and at g64 they have 7 and 8, out of
48576 and 163944 water particles. There is essentially no water beneath the body at all.
A buoyant force is a pressure difference across a body; with nothing underneath, the only
coupling left is lateral shear on the wetted sides, which is why the body descends far
faster than a height-weighted blend predicts.

This carries directly to the gated scene, where the Yaris hull carves water the same way
and also rests on the floor.

**Prediction (c): floor restitution 0.05 arrests the descent.** Reasoning:
`mpm_solver_warp.py:1915` `if restitution != 0.0` registers the plane as a rigid contact
surface, and `_apply_rigid_restitution` at `:936-943` does positional stabilization, not
only an impulse, with its own comment stating the impulse alone cannot hold a resting body
because the grid gather resets `v_cm` (T1).

**Outcome: confirmed.** Vertical travel over the window collapses from **-1.4412 dx**
(rung b, g96) to **-0.2493 dx** (rung c, g96) to **-0.0003 dx** (rung d, g96) (T2).

## 5. Results

### 5.1 The table

All six arms, both grids, reported separately and never averaged, per the dispatch. Window
is 160 substeps requested. `a_ideal` is each arm's own analytic partial-submersion value
from its own measured `h_sub`. Every number T2.

| rung | grid | settle gate | window | sub frac | `a_ideal` | `a_late_window` | % of ideal | `v_mean_late` | travel (dx) |
|---|---|---|---|---|---|---|---|---|---|
| b | 64 | **FALSE, cap** | **35/160, guard** | 0.18593 | -6.7700 | +27.241 | -402.4 % | -1.49319 | -1.4381 |
| b | 96 | True, 20 fr | 160/160 | 0.19809 | -6.5713 | +0.608004 | **-9.25 %** | -0.21757 | -1.4412 |
| c | 64 | **FALSE, cap** | 160/160 | 0.18577 | -6.7727 | +0.00192854 | -0.0285 % | -0.03406 | -0.2497 |
| c | 96 | True, 20 fr | 160/160 | 0.19809 | -6.5713 | +0.00166336 | **-0.0253 %** | -0.02273 | -0.2493 |
| d | 64 | True, 974 fr | 160/160 | 0.21054 | -6.3676 | -0.0112807 | **+0.1772 %** | -0.03752 | +0.0004 |
| d | 96 | True, 20 fr | 160/160 | 0.20628 | -6.4373 | -0.00879440 | **+0.1366 %** | -0.02520 | -0.0003 |

**Two arms are discards and their numbers must not be quoted as results.** `ladder_b_g64`
and `ladder_c_g64` ran the full 1200-frame settle cap without meeting the gate, finishing
at `settle_vmax_final` 0.865234 and 0.861557 m/s against the gate's requirement of
`c/20 = 0.6423` m/s. The dispatch's own rule is that a cap hit is a discard, not a result.
They are shown struck only so the record is complete. `ladder_b_g64` was additionally
truncated at substep 35 of 160 by the P2G guard.

For reference, re-read live from Vista rather than from any doc (T2): C1's own late-window
numbers are `c1_g64` **+0.1001239441**, 1.531 percent of +6.5400, settled True; `c1_g96`
+0.0437416421, 0.669 percent, **settled False**; `c1_rigid_g64` +0.1002611535, 1.533
percent, settled True; `c1_rigid_g96` +0.0550858591, 0.842 percent, **settled False**.
Both C1 g96 arms are themselves unsettled, exactly as C1_ROOT_CAUSE section 4 records, so
the only settled C1 measurements are the two g64 arms at about 1.53 percent.

### 5.2 Rung (b), the rung that actually measures the coupling

Only the g96 arm survives. With every plane at restitution 0.0 the floor is invisible to
the rigid body, so the body descends through it: travel **-1.4412 dx** over 0.333 s, mean
late velocity **-0.21757 m/s**, submerged fraction rising 0.198 to 0.294 as it sinks. Its
`a_late_window` is **+0.608004** against an analytic **-6.5713**, so **-9.25 percent, sign
inverted**.

Stated plainly: a partially submerged free rigid body reproduces neither the magnitude nor
the sign of its own partial-submersion dynamics. It sinks at about a tenth of the speed a
real body of that density and draft would, and its late-window acceleration points the
wrong way. This is the partial-submersion analogue of C1's fully submerged 1.53 percent,
and it is worse.

### 5.3 Rungs (c) and (d), and the caveat that has to travel with them

Once the floor is registered, the body rests on it. Travel over the whole window is
-0.2493 dx at rung (c) g96 and -0.0003 dx at rung (d) g96, and `a_late_window` collapses to
0.03 to 0.18 percent of analytic.

**A resting body's correct vertical acceleration is zero.** Weight is balanced by the
normal force plus whatever buoyancy is present. So "0.03 percent of the free-body analytic
value" is what a correctly supported body should read, and it is ALSO what a body with no
buoyant coupling at all would read. **The vertical acceleration channel cannot distinguish
the two once the floor is active.** Anyone quoting these two rows as a measurement of
coupling error is quoting them wrongly. What rungs (c) and (d) establish is narrower and
still worth having:

1. `_apply_rigid_restitution` **does fire**, and its effect is large and monotone across
   the ladder: -1.4412 dx of travel becomes -0.2493 dx becomes -0.0003 dx (T2). C1 could
   not exercise this path at all, and now it has been exercised.
2. The floor, not buoyancy, sets the body's vertical position in this regime.
3. Therefore any buoyancy error in this regime shows up in the **normal force**, not in
   `a_z`, and the free-rigid path materialises no force, so it is not directly readable
   at all. That is the same wall C1_ROOT_CAUSE section 1 and register A3 describe.

### 5.4 Rung (d), the closing comparison

Matched against **`g64_m1100`** and **`g96_m1100`**: mass class 1100 kg, `n_grid` 64 and
96, `realized_depth_m` 0.2944294473039918, `velocity_ms` **1.5**, 4 and 6 water layers.
Those are the canonical baseline runs of the 17 (T1, `data/all_runs_inventory.csv`).

The inflow was reproduced from `renders/yaris_render_s1/sim_standing.py` read live (T1):
the one-shot additive kick at `:160-162` and the per-frame overwrite clamp at `:190-198`
over the upstream band `x < wall + 1.5`. It reached the body: mean water `vx` in a slab
spanning the box footprint went from 0.00846 to **0.80542** m/s at g64 and from -0.00366
to **0.46552** m/s at g96 over 60 flow frames, with 95th percentiles 1.12317 and 0.79139
against the 1.5 m/s clamp (T2). So the body was measured in developed flow, not in still
water with a clamp on the far wall.

**Is rung (d) consistent in sign and rough magnitude with what the matched published runs
imply?** The dispatch asks for this explicitly, and the honest answer has two halves.

**Vertically, yes, and quite precisely.** Rung (d) ends with the body's bottom face on the
floor plane, travel 6.45e-05 m at g64 and -2.66e-05 m at g96, both under 4e-4 dx. The
matched published runs do the same thing: across **all 17** gated runs, `C2_veh_zmin_final`
equals `3*grid_lim/n_grid`, the floor plane, to within 8e-9 to 4e-8 m, which is float32
round-off at that magnitude (T3 over T1 inventory data). `g64_m1100` starts 0.00708 m above
the floor and settles onto it; `g96_m1100` starts on it and stays. Rung (d) reproduces the
gated vertical behaviour: the vehicle is a floor-supported body, in the ladder and in the
published runs alike.

**On buoyant response, the comparison cannot be made, and that is the result.** The
published runs report no force and no vertical acceleration that is not subject to the
same back-computation objection C1_ROOT_CAUSE section 8 raises. Rung (d)'s own vertical
channel is floor-dominated per section 5.3. So the two are consistent in the only quantity
both can express, vertical position, and mute in the quantity the ladder was built to
compare. The ladder has walked the regime gap to its end and found that the end of it is
not a measurement.

Per the dispatch's section 5, whether this changes any of the 17 verdicts is not decided
here.

### 5.5 An unplanned finding: the g64 settle is non-deterministic at fixed configuration

The settle phase is identical code, identical geometry and identical `seed=0` for rungs
(b), (c) and (d) at a given grid; restitution is registered and flow is applied only after
it returns. Three identical g64 settle phases gave three different outcomes (T2):

| arm | frames run | gate met | `settle_vmax_final` | `settle_vmax_peak` |
|---|---|---|---|---|
| `ladder_b_g64` | 1200 (cap) | False | 0.865234 | 2.0488 |
| `ladder_c_g64` | 1200 (cap) | False | 0.861557 | 2.0488 |
| `ladder_d_g64` | **974** | **True** | 0.594807 | 2.0488 |

Same peak to four decimals, divergent tails. The g96 arms all met the gate at the
`min_frames` floor of 20 with `settle_vmax_final` 0.352205, 0.352217 and 0.352215, which
differ in the fifth decimal for the same reason.

This is consistent with non-deterministic atomic accumulation in P2G and with CLAUDE.md's
existing record that this stack is "non-deterministic at fixed config". Its practical
consequence for this dispatch is direct: **the settle gate is a coin flip at g64 in this
scene**, so a g64 arm can be a result or a discard depending on nothing the operator
controls. Anyone re-running this ladder should expect that and should not read a changed
verdict on a g64 arm as a changed physics.

### 5.6 Passthrough under flow

`water_under_body_at_release` counts water particles inside the body's footprint column
(T2). In still water it is essentially zero: 7 and 8 particles at g64, **0** at g96. After
60 frames of 1.5 m/s inflow it is **1444** at g64 and **3906** at g96, which is 2.97 and
2.38 percent of the water particle count. So flow drives water into the volume the body
occupies. This is the same passthrough failure mode gate P-2 measures in the gated runs
(`passthrough_max_frac` 0.073 to 0.159 there, so the gated runs are worse), recorded here
because the ladder now reproduces it rather than only inheriting it.

## 6. Fix A: C3's estimator. Confirmed working.

C1_ROOT_CAUSE section 9: `run_c3` reports `a_as_fraction_of_g` from `a_headline_first3`,
the estimator section 2 discredits, and for a null test that is strictly worse than for C1
because C3's pin injects a nonzero `dV` by construction.

The owning file is held by another session and the dispatch forbids editing it, so the fix
landed in the new file as a pure function over a C3 result. That turned out to be better
than a patch, not merely permitted: because the corrected value is a function of fields
already stored in every C3 JSON, it applies **retroactively to runs already paid for** and
was validated on a Vista login node at zero SU and with no GPU.

Applied to the only stored C3 artifact, `c3_fixed2_g64.json` (T2):

```
a_headline_first3            -19.94267423450947
a_late_window                 -1.2445799884091344
a_as_fraction_of_g  before    -2.0328923786452058
a_as_fraction_of_g  after     -0.12686850034751623
stored_matches_before         true
abs_change                     1.906
```

`stored_matches_before: true` is the load-bearing line. It proves the stored field is
exactly `a_headline_first3 / G`, so the defective expression was identified correctly and
not guessed. The correction moves the reported null-test metric by a factor of **16.0**.

Two caveats that must travel with this number:

1. **That run is itself a discard.** `settle_gate_met` is `false`, it ran its 60-frame cap,
   and `settle_vmax_final` is **7.337545 m/s**. The gate requires
   `sound_speed/vmax >= 20`, that is `vmax <= 12.8452/20 = 0.64226` m/s, so the water was
   still moving at **11.4 times** the allowed maximum when the body was released, and the
   achieved ratio was 1.75 against a target of 20 (T3). So -0.1269 is a demonstration that
   Fix A works, not a physics result.
2. **Only one C3 artifact exists.** A live listing of
   `$WORK/can-it-ford/data/coupling_validation/` including `smoke/` finds exactly one
   `*c3*.json` out of 15 JSONs total (T2). Fix A's retroactive scope is that one file.

An incidental check while there. C1_ROOT_CAUSE section 2's two-constant model
`a(N) = 6*dV/(dt*(N+1)(N+2)) + a_s` reproduces the C1 window ladders to 1.71 and 1.55
percent max residual (those two figures are quoted from that doc's own section 2 table and
were not re-derived here). Fitted to this C3 run's six published windows it reaches only **23.6 percent**
max residual, with `dV = -0.220247` m/s and `a_s = -2.061952` m/s^2 (T3). The qualitative
diagnosis still holds, the ladder decays monotonically from -31.07 at N=2 to -2.278 at
N=40 exactly as a 1/K release weight implies, but the clean step-plus-constant form does
not transfer to an unsettled run. Do not reuse the C1 fit quality as evidence about C3.

The one-line patch for whoever owns `simulation/validate_coupling_force.py`:

```
in run_c3, replace
    res["a_as_fraction_of_g"] = res["a_headline_first3"] / G
with
    res["a_as_fraction_of_g"] = res["a_late_window"] / G
and keep the withdrawn value under a distinct key if the record needs it:
    res["a_as_fraction_of_g_headline_first3_WITHDRAWN"] = res["a_headline_first3"] / G
```

`a_expected_compressible` was deliberately left alone, per section 9.

## 7. Fix B: the P2G guard's message. Confirmed working, live, on the real solver.

C1_ROOT_CAUSE section 8b: `core/solver.py:506` computes `g = x[:, 1:] if self.periodic_x
else x`, and `periodic_x` is never set in these scenes, so the guard checks all three axes
while the message at `:508-512` hardcodes the label `"x"` and prints only a global min and
max. Its open item is that "the identity of the tripping particle is UNKNOWN".

Implemented as `install_p2g_guard_diagnostic()`, a runtime patch of
`Solver._update_grid_box`, rather than an edit to the vendored copy under `third_party/`,
whose line numbers C1_ROOT_CAUSE section 0 depends on being stable. It is installed by
every ladder rung, not only by the demo.

Validated end to end on Vista in job `895653` by driving one **rigid** particle 0.05 m
below the low z bound in the real scene and stepping, first unpatched and then patched.
`both_tripped: true`, `patch_reverted: true` (T2).

BEFORE, the message at the pinned SHA:

```
particles within 2 cells of the grid edge (x in [0.1708, 8.8108] m, domain
[0, 9.421742313727737] m, dx=0.1472): the P2G stencil would write out of bounds.
Enlarge grid_lim or add a bounding box / wall collider.
```

AFTER:

```
particles within 2 cells of the grid edge on axis Z (low bound 0.220822 m, breached by
0.050000 m = 0.340 dx): the P2G stencil would write out of bounds. Offender: particle
48576, material 8 (rigid(mat 8)), rigid body 0, at (4.011601, 4.011601, 0.170822).
Domain [0, 9.421742313727737] m, dx=0.1472, guard band [0.2208, 9.0537] m.
  per-axis extrema:
    x: min 0.610947 (particle 285), max 8.810790 (particle 48445)
    y: min 0.610946 (particle 11648), max 8.810778 (particle 26125)
    z: min 0.170822 (particle 48576), max 1.876988 (particle 48595)
  Enlarge grid_lim or add a bounding box / wall collider.
```

The old message says `x in [0.1708, ...]`. The true minimum is in **Z**, and the offender
is the **rigid body**, not water. The x axis minimum is 0.610947, nowhere near the bound.
That is precisely the confusion section 8b records.

Fix B then paid for itself immediately and unprompted. In job `895648`, rung (b) at g64
crashed on this guard for real, at 0.2207 against a bound of 0.220822. With the old message
that is an opaque "x in [0.2207, 8.8697]". With Fix B installed and the ladder's own
`water_under_body` diagnostic, the cause is unambiguous and is now section 4's finding:
with restitution 0.0 the floor does not exist for the rigid body, so the body descends
through it into the guard, which is the same mechanism C1_ROOT_CAUSE section 8b attributes
to C2's crash. The harness now truncates the window before the guard and records
`window_truncated_by_p2g_guard`, `window_truncated_at_substep` and `guard_slack_at_stop_m`
instead of dying.

## 8. What remains open

**The 7.59x `dV` grid ratio between g96 and g64 is untouched by this work and stays open.**
This ladder cannot speak to it. The only rung with a clean two-grid comparison is (c) and
(d), where both grids are floor-dominated and the g64-to-g96 ratio of `a_late_window` is
1.159 at rung (c) and 1.283 at rung (d) (T3), nothing like 7.59. That is not a resolution
and must not be read as one: those two rungs measure a resting body, and rung (b), the one
rung that measures the free coupling, has only one usable grid because its g64 arm did not
settle. A second grid for rung (b) needs the g64 settle problem in section 5.5 solved
first.

**Whether any of this generalises to a moving, not-yet-topped-out vehicle is untested.**
The body here is a uniform cube of side 1.472 m with a flat bottom face, spawned axis
aligned and never rotated. The Yaris hull is non-uniform, has a curved underside and a
ground clearance, and in the gated runs it yaws and rolls. Three specific gaps:

1. **Ground clearance.** The cube's flat bottom face sits on the floor, so the water column
   under the footprint is fully carved and zero water is underneath. A real hull has
   clearance, so water can pass beneath it. The gated runs carve the hull's occupied cells
   the same way, but whether the resulting under-hull water volume is zero or merely small
   has not been measured and is exactly the quantity section 4's finding turns on.
2. **Rotation.** `_apply_rigid_restitution` applies its impulse and its positional push at
   the single deepest penetrating particle and uses a lever arm, so it generates torque. A
   cube resting flat cannot exercise that. A yawing, rolling hull can, and does in all 17
   runs.
3. **Floor friction.** This ladder walked restitution only. Its floor stays at BoxTank's
   `friction=0.0`; the 17 gated runs carry `floor_friction=0.55`
   (`sim_standing.py:132`, T1). Since section 5.3 concludes any buoyancy error in this
   regime lands in the normal force, and sliding resistance is friction times normal force,
   floor friction is the obvious next rung and it was not run here.

**Also open, and newly raised rather than inherited:** the g64 settle non-determinism of
section 5.5 makes any single g64 arm of this ladder unreproducible in verdict. Before a g64
number from this file is promoted anywhere, it should be re-run several times and the
spread reported, not the single value.

## 9. Reproduce

Geometry, on a laptop, no solver and no GPU:

```
python3 simulation/validate_coupling_force_ladder.py --geometry-only --n-grid 64
python3 simulation/validate_coupling_force_ladder.py --geometry-only --n-grid 96
```

Fix B, before and after, on a laptop:

```
python3 simulation/validate_coupling_force_ladder.py --demo-fix-b
```

Fix A, on a Vista login node, no GPU and no SU:

```
$WORK/can-it-ford/mpm-engine/.venv/bin/python \
  simulation/validate_coupling_force_ladder.py \
  --fix-a $WORK/can-it-ford/data/coupling_validation/c3_fixed2_g64.json
```

The full ladder, one node, about 100 seconds:

```
sbatch scripts/ladder.sbatch
```

Results land in `$WORK/can-it-ford/data/coupling_validation/ladder_*.json`.

## 10. Files this dispatch added

- `simulation/validate_coupling_force_ladder.py`, new, additive.
- `scripts/ladder.sbatch`, new.
- `docs/REGIME_LADDER_RESULTS_2026-08-07.md`, this file.
- A claim block appended to `docs/SESSION_CLAIMS.md`, which also records four findings
  from the dispatch's own section 7 pre-checks: the SDF code IS committed, on branch
  `worktree-c1-triage` at `6593404` and pushed to `origin/worktree-c1-triage`, but not on
  `main`; the repo's pre-commit gate is currently broken and blocks every session;
  `C1_ROOT_CAUSE_2026-08-07.md` is no longer dirty; and Vista has 669 SU with an idle
  interactive job that has burned roughly 3 node-hours today against 0.056 for this entire
  dispatch.
