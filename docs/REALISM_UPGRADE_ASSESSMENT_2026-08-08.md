# Realism upgrade: what to change, what NOT to change, measured

Date: 2026-08-08. Owner: the ctx-census session.
Additive. Edits no file owned by another session.

Scope: the three changes proposed as "make the simulation more realistic" —
(1) wire the measured inertia tensor and CG, (2) fix the regime-ladder metric,
(3) re-render with corrected captions — assessed against the research reports in
`~/Downloads` (2026-08-07 08:00 onward) and against measured data from
`renders/yaris_render_s1/g64_m1100/rollout.npz`.

**Headline: change (1) as proposed is a REGRESSION and must not be made.** The
evidence is in section 1. Sections 2 and 3 are worth doing. Section 4 quantifies
the bounded-domain question. Section 5 records what the reports change elsewhere.

Provenance tiers as in `C1_ROOT_CAUSE_2026-08-07.md`: **T1** read live by me,
**T2** measured from data, **T3** arithmetic shown here.

---

## 1. DO NOT wire `inertia_kg_m2`. It is a box, and the axes are transposed.

### 1a. The "measured" tensor is not measured (T1)

`vehicle_params.py:100` declares
`"inertia_kg_m2": {"Ixx": 463.0, "Iyy": 1893.0, "Izz": 1960.0}`.

I reproduced all three from the rectangular-box formula
`Ixx = m(W²+H²)/12` etc. with `m = 1100`, `(L,W,H) = (4.30, 1.70, 1.47)` (T3):

| | file states | box formula | match |
|---|---|---|---|
| Ixx | 463.0 | 463.0 | exact |
| Iyy | 1893.0 | 1893.0 | exact |
| Izz | 1960.0 | 1959.8 | 0.01 % |

It is a solid rectangular box. The file says so itself at `:99`: *"uniform-density
box fallback from Yaris mass+bbox (no measured Yaris tensor exists). box_inertia()
OVERESTIMATES Iyy/Izz; treat as upper bound."*

### 1b. The solver already computes a strictly better tensor (T1 + T2)

`kernels/mpm_solver_warp.py:859-871` builds the tensor from the actual rigid
particle cloud, `I += mᵢ(|rᵢ|²·1 − rᵢ⊗rᵢ)`. Computed from
`veh_particles_scene0` (8905 particles, 1100 kg), about the true centroid:

| | hull cloud (in use) | box fallback, axis-corrected | box error |
|---|---|---|---|
| Ixx | **1501.5** | 1893.0 | +26.1 % |
| Iyy | **395.0** | 463.0 | +17.2 % |
| Izz | **1685.4** | 1959.8 | +16.3 % |

Both assume uniform density. One uses the real hull shape, the other a rectangle.
**The hull fills only 33.2 % of its own bounding box**, so a solid box must
overstate the mass spread; the overstatement above is geometrically necessary, not
incidental. Replacing the cloud tensor with the box tensor is a regression on
every axis.

### 1c. The axis trap, which is the dangerous part (T2)

`vehicle_params.py` documents `bbox_m` as `(L, W, H)` mapped to `(x, y, z)`. The
scene does not. Measured particle extents at frame 0:

```
x extent 1.7078 m     y extent 4.2014 m     z extent 1.4853 m
```

**The hull's long axis is Y, not X.** (The render's own footer says the same: *"The
hull's long axis is y, so it sits BROADSIDE to the +x flow."*)

So a naive `Ixx=463, Iyy=1893, Izz=1960` write puts roll inertia on the pitch axis:

| axis | true (hull) | naive wire | error |
|---|---|---|---|
| Ixx | 1501.5 | 463.0 | **−69.2 %** |
| Iyy | 395.0 | 1893.0 | **+379.2 %** |

A 379 % error on the pitch axis, introduced by a change intended to improve
realism. This is the specific failure mode to record.

### 1d. What the CG number actually says (T2)

| quantity | value |
|---|---|
| cloud CG above floor (in use) | **0.6312 m** |
| hull spans above floor | 0.0000 to 1.4853 m |
| bounding-box mid-height | 0.7427 m |
| `vehicle_params.py:95` `cg_height_m` | 0.51 m, flagged **ESTIMATE** (0.35 × body height), *"CONFIRM before L2/collider"* |

The cloud CG is 23.8 % higher than the subcompact-typical estimate, and it already
sits *below* bbox mid-height (0.6312 vs 0.7427), i.e. the hull shape alone already
pulls the CG down. A real car is bottom-heavy beyond that, so the true CG is
plausibly lower still.

**A too-high CG biases toward topple.** The 17 gated runs report 16 SLIDE and 1
STUCK, zero topples. So the no-topple result is obtained under a CG that is
conservative in the topple direction, which strengthens it rather than weakening
it. That is a reportable robustness statement and it costs nothing.

### 1e. Verdict

- **Do not** write `inertia_kg_m2` into the solver. It is a box fallback, it is
  worse than what is already computed on all three axes, and its axis convention
  is transposed relative to the scene.
- **Do not** write `cg_height_m = 0.51` either, without deciding deliberately: it
  is an estimate, not a measurement, and the file says to confirm it first.
- CLAUDE.md item 4 currently says *"Do not claim NHTSA-measured inertia or a
  measured CG height is in effect in any gated run."* That is right and should be
  extended: **and do not wire them, because they are not measured.** The correct
  upgrade path is a measured tensor from the NHTSA Light Vehicle Inertial
  Parameter Database (SAE 1999-01-1336), which the research report notes **has no
  Yaris** (the database ends Nov 1998). So there is no measured Yaris tensor to
  wire, from any source, today.

---

## 2. The regime-ladder metric is invalid and must not be reported (T2)

All six rungs completed on Vista (`ladder_[bcd]_g{64,96}.json`). Three defects:

1. **`a_ideal = -9.0` on every rung.** A placeholder, not a target. For a
   *partially submerged* body `g(ρw/ρbox − 1)` does not apply at all; the
   equilibrium target is ≈0. Every derived percentage is meaningless.
2. **`a_headline_first3` = −255.98, −132.47, −257.45, −132.46 m/s².** Twenty-six
   times gravity. The same pin-induced release-step artifact documented in
   `C1_ROOT_CAUSE_2026-08-07.md` §2, amplified.
3. **`ladder_b_g64` reports `a_late_window = +27.24 m/s²`**, 2.8 g upward.
   Unphysical.

Most likely cause of (3), stated as a reading: `a_late_window` is a **linear** fit,
and a body at a free surface oscillates. Fitting a line to an oscillation returns a
slope set by where the window lands. That is why the metric behaved sensibly for
C1 (fully submerged, no restoring force) and returns nonsense at rung b. Needs the
`v_series` to confirm; nothing else explains +27 m/s².

Also, the settle gate is weaker than it reads (T3): `ratio_target = 20` against
`c = 12.8452 m/s` declares "settled" at up to **0.642 m/s** residual, and
`min_settle = max(20, ceil(10·transit·30)) = max(20, 7) = 20` frames is a **floor**,
not a measurement. All three g96 arms met the gate at exactly that floor.

**Do not cite any ladder number until the target and the estimator are replaced.**

---

## 3. The render caption is one line from defensible

`renders_preview/g64_m1100_live_2026-08-07.mp4` (1920×1080, 180 frames, 6.000 s) is
accurate about almost everything and embeds most of the register's corrections. Two
lines in its "Verified state" panel do not hold:

- `floats? no: buoyancy 4.5 kN < weight 10.8 kN` is a **static analytic**
  calculation sitting in a panel headed "Verified state" beside genuine sim
  outputs. The simulation did not verify it and on the material-8 path could not.
- `verdict SLIDE` rests on a displacement curve produced by a coupling that
  registers ≈1.5 % of analytic buoyant response (`C1_ROOT_CAUSE` §3).

Minimal correct caption addition:

> Buoyancy here is analytic, not measured. The material-8 rigid path forms no
> force (`kernels/mpm_utils.py:1434`) and registers ≈1.5 % of analytic buoyant
> response, so displacement and the SLIDE verdict inherit that defect.

### 3a. CORRECTION: the caption cannot be fixed, because the generator does not exist

An earlier revision of this section said the generator was `render_rollout.py` in
`~/Downloads` and that committing it made the render reproducible. **That is wrong
and is withdrawn.** `analysis/render_rollout.py` renders the **s3 enhanced-pipeline**
schema (its own docstring: *"confirmed 2026-08-08 against ctrl_g64 and
enh_g128_real"*), builds a single 3-D axis, and contains none of the dashboard's
panels or strings. It did not produce this video.

Searched for the dashboard's own strings (`"Verified state"`, `"Plan view"`,
`"a real cross-section"`) across the repo, `~/Downloads`, and
`~/canitford_census_2026-08-07/`. **The only hit anywhere is this document.** The
nearest candidate in the tree,
`renders/yaris_render_s1/render_hero_g64_m1100_2026-08-06.py`, is a different
render entirely: marching-cubes free surface, L0/L1a/L1b/L2 verdict strip, no
dashboard panels. A Vista-side search timed out at 60 s and is inconclusive.

**Consequence: `renders_preview/g64_m1100_live_2026-08-07.mp4` is unreproducible.**
The only render in the project cannot be regenerated, so the caption cannot be
corrected by re-rendering. This is the same un-regenerable-artifact defect the
register records for `c1only.sbatch` and `c2only.sbatch`, now applied to the one
headline visual deliverable.

Until the generator is recovered, the caveat in §3 has to travel **alongside** the
video (figure caption, poster text, paper) rather than inside it.

`analysis/render_rollout.py` was still worth committing on its own merits: it
renders the s3 enhanced-pipeline rollouts, it existed in no commit, and it is now
versioned. It is simply not this video's generator.

---

## 4. The bounded tank is a first-order problem, measured (T2)

From `local_depth_bow` / `local_depth_footprint` in the rollout, against the
nominal 0.30 m printed on every figure:

| probe | min | max | final | excursion |
|---|---|---|---|---|
| bow | 0.2279 | 0.3958 | 0.2279 | **−24.0 % to +31.9 %** |
| footprint | 0.2260 | 0.3750 | 0.3298 | **−24.7 % to +25.0 %** |

**Only 20 of 90 frames (22 %) sit within ±10 % of the nominal depth.** The vehicle
spends 78 % of the run at a depth that is not the labelled depth.

Downstream pile-up against the closed wall, water surface height above floor:

| frame | near downstream edge |
|---|---|
| 0 | 0.2729 m |
| 45 | **0.6750 m** |
| 89 | 0.5868 m |

A 2.5× rise at the wall by mid-run. The streamwise fetch is `lim / hull length =
9.4217 / 4.2014 = 2.2 hull-lengths`.

So "depth 0.30 m" labels the initial condition, not the experiment. This is a tank
that fills and sloshes, not a channel that conveys. The fix is real and known
(Zhao, Bolognin, Liang, Rohe & Vardon 2019, DOI 10.1016/j.compfluid.2018.10.007)
but `docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md` states *"planning only, no BC code
written yet"* and it is an Anura3D→warpmpm translation, not a port.

---

## 5. What the research reports change, and what they do not

Verified against live source before recording:

- **Water viscosity is ALREADY correct.** One report flags `1.0 Pa·s` as 1000×
  too high. `renders/yaris_render_s1/sim_standing.py:75` uses
  `water_eta=1.0e-3`, matching IAPWS/ISO 1.0016e-3 Pa·s. The finding applies to an
  older config, **not** to the 17 gated runs. Do not "fix" it.
- **Quadratic B-spline transfer is ALREADY in use.** A report recommends switching
  to B-spline kernels as the single highest-leverage fix for non-monotonic
  convergence. `kernels/mpm_utils.py:1383-1400` already builds standard quadratic
  B-spline weights. Already done; the non-monotonicity has another cause.
- **Resolution against the literature conventions.** No formally validated
  force-convergence criterion exists (confirms CLAUDE.md L-3). Working conventions
  are `dp ≤ D/10` on a body dimension and ~10 particles per flow depth, with
  `H/dp ≥ 5` as a bare wave-capture minimum. The g64 baseline has **4 water
  particle layers** and `depth/dx = 2.000`, i.e. below even the minimum
  convention. State it that way rather than as "under-resolved".
- **Direction of bias.** Coarse resolution usually **over**-predicts peak
  hydrodynamic force (confirms L-4), so an over-threshold NO-FORD verdict is
  conservative. Not universal; the documented exception is over-fine resolution
  triggering premature breaking.
- **Class-specific AR&R limits** are 0.3 / 0.45 / 0.6 m²/s with limiting depths
  0.3 / 0.4 / 0.5 m, velocity capped at 3 m/s. L1 should encode three curves, not
  one threshold.
- **Cited experimental anchors** worth using instead of generic values: Yaris drag
  coefficient **1.0–1.8** perpendicular to flow, friction **0.55** good road
  dropping to **0.30** poor, and **0.35 m** still-water flotation depth for a
  watertight small passenger vehicle (Smith, Modra & Felder 2019 as reported by
  Azhar 2023). Confirm against the 2019 primary before quoting precisely.

---

## 6. Ranked, with cost

| change | verdict | cost |
|---|---|---|
| wire `inertia_kg_m2` | **DO NOT** — regression, §1 | — |
| wire `cg_height_m` | not without confirming the estimate | low |
| report the CG-bias robustness statement (§1d) | **do** | free |
| fix ladder target + estimator | **do**, before any citation | low |
| render caption + commit the generator | **do** | low |
| decouple `dx` from domain extent to resolve depth | do for the paper | moderate |
| sound-speed sweep (Isik & He 2022) | do for the paper | moderate, SU |
| force-based rigid coupling | needed, not tonight | high |
| open-channel in/outflow BCs | needed, not tonight | high |

## 7. Not done here, deliberately

`simulation/validate_coupling_force.py` and
`simulation/validate_coupling_force_ladder.py` are held by other sessions.
`renders/yaris_render_s1/sim_standing.py` is clean but produced all 17 gated runs;
editing it forks or invalidates them and needs an explicit decision. Nothing in
this file edits any of them.
