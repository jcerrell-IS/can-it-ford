# Unexplored areas assessment, 2026-08-07

Scope: the five unexplored simulation areas and three Claude-harness degradations raised
this session. Every claim below was read live from source on 2026-08-07. Claims that a
prior session or an agent asserted and that did NOT survive an independent read are
marked REFUTED and kept, with the correction, so they are not re-proposed.

Method note: findings were produced by six parallel deep-dive agents, then each
non-trivial claim was independently attacked by a separate adversarial verifier, then
the load-bearing survivors were re-read by hand against the live files. Several agent
claims were refuted at both later stages. Where this document and an agent transcript
disagree, this document is the one that was hand-checked.

---

## 0. The single most useful discovery: the engine is readable locally

A complete `warpmpm` install exists at
`/Users/josie/.venvs/canitford-mpm/lib/python3.12/site-packages/warpmpm/`.
`pip`'s `direct_url.json` pins it to `github.com/kks32/mpm-engine` commit
`544c93dd02cb9c7ead89e1155a62967243244fce`, the SAME SHA as the partial vendored copy at
`third_party/mpm-engine-544c93dd-solver-core/`.

That makes the full engine readable on the Mac, with provenance, at the pinned SHA:
`kernels/mpm_solver_warp.py` (3181 lines), `kernels/mpm_utils.py` (1588),
`core/solver.py` (642), `geometry/mesh_sdf.py` (563), `colliders/glass.py` (405),
`vehicle.py` (380), `materials/__init__.py` (166), `scenes.py` (34).

**One critical exception, see item 5.** `vehicle.py` in the install is NOT the module that
ran the 17 gated runs. For the vehicle layer, `renders/yaris_render_s1/vehicle_live.py`
is primary. For `core/`, `kernels/` and `materials/`, the install is primary.

---

## Item 1. `warpmpm/coupling/` is not hypothesis zero. REFUTED.

**Verdict: refuted as a cause of C1. Closed.**

`coupling/` is a robot-tool force-feedback stack for a kinematic box end-effector
pressing into dough. It has **zero references anywhere in this repo** (verified with
`/usr/bin/grep` for `warpmpm.coupling`, `WarpMPMBackend`, `box_contact_wrench`,
`ForceAdmittance`, `attach_tool`, excluding the nested duplicate, `third_party/` and
worktrees).

| module | what it is | in the vehicle path? |
|---|---|---|
| `wrench.py` (46 lines) | post-hoc numpy Cauchy-traction integral in a contact band under a box | no |
| `admittance.py` (71) | `ForceAdmittance`, `Impedance1D` controllers; never touches the solver | no |
| `backend.py` (81) | `WarpMPMBackend` over `add_box` / `set_box` / `tool_force` | no |

The intuition that "a package named `coupling` containing `wrench` is where an inverted
coupling force lives" was reasonable and is wrong: the name refers to robot-to-material
coupling, not fluid-structure coupling.

**What it was still worth reading for.** It documents the sign conventions and points at
the four reaction-force accessors, which is what made item 2 tractable.

---

## Item 2. `sdf_wrench` is a real force meter, and the free-rigid path has no analogue

**Verdict: the discriminator is sound. A peer session is already building it.**

`Solver` exposes **four** reaction-force accessors, all on KINEMATIC colliders:

| accessor | collider | `core/solver.py` |
|---|---|---|
| `cup_wrench` | revolved SDF (glass) | :302-313 |
| `sdf_wrench` | closed mesh SDF | :354-361 |
| `cdf_wrench` | CPIC open sheet | :401-413 |
| `tool_force` | axis-aligned box | :420-427 |

The free rigid body, which is what all 17 gated runs use, has **none**. `rigid_state()`
(`core/solver.py:200-210`) returns `com`, `v`, `omega`, `R` and nothing else.

That asymmetry is the whole of C1. `sdf_wrench` accumulates `sum m*(v_free - v_new)/dt`
over near-surface grid nodes, taken after gravity and before G2P, and it is the force ON
the collider. It is not gated on collider motion, so a stationary collider does
accumulate a wrench, which is what the buoyancy test needs.

### Sign convention, stated correctly

`tool_force`'s docstring says "compression -> +z" and `cup_wrench`'s says a static cup
holding `m` kg of settled liquid reads `(0, 0, -m*g)`. These look contradictory and are
not: both are the force the material exerts on the collider, and the load directions
differ (dough pushes a press up, liquid pushes a cup floor down). **A submerged body
reads buoyancy as +z.**

### Live defects in the peer's in-flight `c1sdf` implementation

`simulation/validate_coupling_force.py` grew from 753 to 869 lines during this session
(modified 12:38:35, uncommitted) and `scripts/c1sdf.sbatch` appeared. **Another session
owns those files; nothing here was edited.** Two argument-default mismatches are live in
that file right now and each would produce a false failure:

- `run_c1_sdf(..., depth_cells=18.0, ...)` at :701, but the CLI is
  `p.add_argument("--depth-cells", type=float, default=10.0)`. `main()` forwards
  `a.depth_cells`, so a bare `--variant c1sdf` runs at **10**, not 18. The function's own
  docstring reasons explicitly about "the C1 defaults (depth_cells=18, box_bottom_cells=8)"
  where `box_top` lands exactly on the nominal free surface. With `box_bottom_cells=8` and
  a box 10 cells long, `depth_cells=10` puts the water surface at the box BOTTOM: roughly
  20 percent submerged, so the run reads about -80 percent against `RHO_W * V * G`.
- `run_c1_sdf(..., settle_frames=600, ...)`, but the CLI default is `60`. A 10x shortfall
  in settling, on a case whose whole point is a hydrostatic column.

The band knife-edge and the Tait-EOS target that an earlier read flagged appear to be
handled already: `sdf_margin_cells(..., band_safety=2.0)` at :138-159 sizes the SDF
margin to clear a 2*dx band and reports `sdf_band_clearance`, and `eos_b`,
`draft_compressible` and `hydrostatic_density` at :63-77 exist. `f_analytic` at :745 is
still the incompressible `RHO_W * volume * G`, so the compressible target should be
reported next to it rather than instead of it.

**Recommendation: pass these two default mismatches to whoever owns that file. Do not
duplicate the harness.**

---

## Item 3. Bingham / Herschel-Bulkley is reachable, and is the strongest novel axis

**Verdict: confirmed, scoped, costed. Build it.**

The composable materials are real and the arguments are not silently dropped.
`kirchoff_stress_newtonian` (`kernels/mpm_utils.py:32-54`) implements, verbatim:

```
gd      = sqrt(2 * dev(D):dev(D) + eps^2),  eps = 0.02   (hardcoded)
eta_app = eta + tau_y / gd + K * gd^(n - 1)
Cauchy  = -p I + 2 * eta_app * dev(D)
```

That is Herschel-Bulkley plus an additive Newtonian term, with bi-viscosity
regularization. `tau_y = 0, K = 0` recovers the current Newtonian water exactly.
`Solver.set_material` takes any composed `Material` via `.resolve()`, so the driver
change is one line:

```python
s.set_material(newtonian(eta=water_eta, density=water_density,
                         bulk_modulus=bulk_modulus)
               .with_yield(tau_y).with_powerlaw(K=hb_K, n=hb_n))
```

Upstream's own idiom for this is `scenes.dough()`:
`newtonian(eta=40.0, density=1000.0).with_yield(200.0)`.

### The CFL trap, which is the part that would have bitten

`sim_standing.py:149` computes `term_viscous = 6.0 * water_eta / (water_density * dx * dx)`
from the NEWTONIAN viscosity. The kernel's apparent viscosity is capped at the
regularization floor at `eta + 50*tau_y + K*0.02^(n-1)`, four orders of magnitude larger
for a modest yield stress. The settle loop at :156-158 runs the water at rest, where `gd`
sits exactly on the eps floor by construction, so this is the first thing that breaks,
not a corner case. `core/solver.py:429-452` has no CFL check and no NaN guard, so silent
degradation is the likely failure mode, not a crash.

`analysis/bingham_cfl_crossover.py` (new, this session) quantifies it. It first
reproduces the as-run substep count for **all 17 runs exactly** (8/8/8, 11 x 11, 16/16/16)
from the driver's own formula, as a self-test that the formula it uses is the one that
ran, then solves for the crossover:

| n_grid | dx (m) | acoustic rate | tau_y_crit (Pa) |
|---:|---:|---:|---:|
| 48 | 0.196286 | 233.72 | **30.02** |
| 64 | 0.147215 | 311.63 | **22.51** |
| 96 | 0.098143 | 467.44 | **15.01** |

The threshold **falls** as the grid refines, so a yield stress that is safe at g48 can
under-resolve at g96. Check the finest grid, not the coarsest.

Sweep cost at the g64 baseline, from the same script: a 9-run ladder spanning clear water
to mud flow costs about **13.3 baseline-run-equivalents**. Everything up to tau_y = 10 Pa
is free (still 11 substeps); only the mud-flow end costs real SUs.

### Required paired edit

Do not ship the material line without also replacing `sim_standing.py:149` with

```python
eta_cap = water_eta + tau_y / 0.02 + hb_K * 0.02 ** (hb_n - 1.0)  # kernel eps, mpm_utils.py:41
self.term_viscous = 6.0 * eta_cap / (water_density * dx * dx)
```

Keep the `0.02` inline with that comment. Do NOT lift it into a shared constant with
`mpm_utils.py:41`: that kernel lives in a vendored engine at a pinned SHA and a shared
name would imply changing one changes both. It is also **not** one of the `0.05` literals
in CLAUDE.md item 13; do not sweep it into that deduplication.

### Caveats before this reaches the paper

- The regime labels in the script's ladder are indicative, not cited. Pin `tau_y` and
  `eta` to a primary source before publication. Sediment-laden flow yield stresses span
  orders of magnitude with volumetric concentration, and a tau_y-only ladder at fixed eta
  is not physical; the script includes two eta-coupled points for that reason.
- `bulk_modulus` is 1.5e5 Pa, giving c = 12.845 m/s rather than water's 1481 m/s.
  `tau_y_crit` scales linearly in c, so a physical sound speed would raise every
  threshold by the same factor. CLAUDE.md already records Isik and He 2022 as evidence
  that artificial sound speed can flip a rigid-body outcome.
- Run the tau_y = 0 control FIRST and require `final_disp_mag_m == 0.6585370302200317`
  exactly against `data/all_runs_inventory.csv` row `g64_m1100`. Any difference means the
  plumbing changed the baseline and the whole ladder is uninterpretable.

---

## Item 4. CPIC does not solve ground clearance. Assessed and rejected.

**Verdict: do not build it. Three independent blockers.**

`add_cdf_collider` is real and its docstring does cite Hu et al. 2018 Section 5, with a
caveat the original framing omitted: "the contact treatment is this repository's own
(blocked-deposit masking, distance-weighted ghost with an impulse-capped Coulomb
projection and separation push, scatter-side wrench accounting), **not a line-by-line
implementation of the paper's projection and penetration handling**".

**Blocker 1, category error.** CPIC severs particle-node transfers across a zero-thickness
sheet. That removes the need to resolve a **wall**. Ground clearance is a **gap**. Flow
through a gap needs cells across the gap regardless of collider type, and the quadratic
B-spline stencil is 3 cells wide.

`analysis/verify_cpic_ground_clearance.py` (new, this session) computes this from the
canonical PLY with no solver and no trimesh:

| n_grid | dx (m) | cells across the gap | status |
|---:|---:|---:|---|
| 48 | 0.196286 | 0.920 | gap smaller than one cell |
| **64** | **0.147215** | **1.226** | **sub-stencil, baseline** |
| 96 | 0.098143 | 1.840 | sub-stencil |
| 128 | 0.073607 | 2.453 | gap resolved, stencil still straddles |
| 192 | 0.049072 | 3.679 | stencil fits inside |

Two cells across the gap needs n_grid >= 104 (~4x the g64 cell count); a stencil
contained in the gap needs n_grid >= 157 (~15x). Under the most pessimistic clearance
definition (column minimum, 0.146952 m) the g64 figure is 0.998 cells, i.e. exactly one.

**Blocker 2, closed hull.** `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`
has **0 boundary edges** over 982,962 unique edges, 0 non-manifold edges, 327,212
vertices, 655,308 faces. It is closed. Every CDF entry point specifies an open oriented
mid-surface.

**Blocker 3, decisive: CDF colliders are kinematic-only.** `rigid_g2p_accumulate`
(`mpm_utils.py:1370-1412`) gathers `grid_v_out` with no CPIC masking whatsoever, and
`cdf_reaction_force` is only zeroed and read out, never applied to a body. Attaching a
CDF sheet to the hull would block the hull's p2g deposits into water nodes while leaving
its g2p gather unmasked: momentum non-conserving, and it would suppress rather than
improve the coupling.

One docstring claim did NOT survive: "watertight at any wall thickness, where an SDF
collider needs ~2 cells". The SDF band default is 1 dx, not 2, and CPIC watertightness is
conditional on `band >= 1.5 dx`, which is a GRID condition replacing the wall-thickness
condition rather than removing it. The 1.5 dx floor is a `warnings.warn`, not an error.
`add_cdf_collider` also raises `NotImplementedError` under `periodic_x`, which matters
for the channel work.

**This is a limitation to state honestly in the paper, not a defect to fix.**

---

## Item 5. Upstream scenes/vehicle diff, and a correction to this session's own premise

**Verdict: worth the read, and it overturned something I had asserted.**

**`scenes.py` has no vehicle scene.** It is 34 lines: `dough()` and `block()`. There is no
upstream vehicle scene whose conventions could differ.

**The install's `vehicle.py` is NOT what ran the 17 gated runs.** Verified by hand:

- `solidify_watertight` appears 0 times in the install's `vehicle.py`, 3 times in
  `renders/yaris_render_s1/vehicle_live.py`.
- `is_gaussian_ply` appears 0 times in the install, 2 times in `vehicle_live.py`.
- `sim_standing.py:12` imports all of `FloodHistory, load_vehicle, solidify_watertight`
  from `warpmpm.vehicle`, so the install could not have satisfied that import.
- The install's `vehicle.py` is byte-identical (`cmp`) to
  `third_party/mpm-engine-544c93dd/vehicle_main.py`.

So the Vista-side `warpmpm/vehicle.py` is a **later revision** than the pinned SHA. This
corrects the premise I gave the deep-dive agents. For the vehicle layer read
`vehicle_live.py`; for `core/`, `kernels/` and `materials/` the install remains primary
and its provenance is intact.

**The axis trap, found by my own script failing.** `sim_standing.py:82` reads
`lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)`, but `ext` there is `VehicleBody.extent`
AFTER `load_vehicle(up="z")` permutes axes, so the driver's `ext[1]` is the PLY's **x**
(the 4.28 m length), not its y. Taking the PLY axes at face value gives
lim = 3.5 * 4.2826 = 14.989 m; the as-run value is 2.2 * 4.2826 = **9.421742314** m,
which matches `data/all_runs_inventory.csv` exactly. A 59 percent error that silently
rescales every dx. Any new driver must anchor on the recorded `grid_lim`, not re-derive
it from assumed axis order.

**`canonicalize()` is a repair, not a deviation.** `sim_standing.py:18-27` rewrites
`v.mesh`, `v.surface`, `v.extent` and `v.spacing` because upstream `load_vehicle` derives
extent, shift and spacing from a 60k random surface sampling of a 327,212-vertex mesh
rather than from the vertices. It does leave `v.particles` stale and unshifted, which is a
live trap for any new driver that does not immediately re-solidify.

**For `sim_channel_bc.py`, five constraints.**

1. Never set `Solver(periodic_x=True)` in a scene with `finalize_rigid_bodies()`. Only CDF
   raises; rigid bodies fail **silently**.
2. There is no inflow or outflow machinery upstream at all. Zero hits across the install.
   A channel BC has to be written from scratch, and the citable design is Zhao,
   Bolognin, Liang, Rohe and Vardon 2019 (Computers and Fluids 179, 27-33,
   DOI 10.1016/j.compfluid.2018.10.007), not Kumar.
3. Call `canonicalize()` and `solidify(h)` as one atomic step.
4. Anchor `grid_lim` on the recorded value per the axis trap above.
5. `add_box` acts on GRID nodes, and rigid particles read the same grid, so an inlet slab
   placed near the vehicle imposes velocity on the body indirectly. Calibrate it
   water-only first.

Also confirmed: `vehicle_live.py:295-300` does swap two of `pitch_deg`/`roll_deg` into
vehicle-body sense rather than raw Euler. Measured global max `|roll_deg|` across all 17
runs is 4.63 degrees, so the gimbal singularity is nowhere near active today; it only
becomes a risk for a future toppling run.

---

## Item 6. Skills. NOT REPRODUCING.

All 13 project skills under `.claude/skills/` have a `SKILL.md` and **all 13 are
available in this session**, alongside the user-level and plugin skills. The prior
session's "1 skill available" is not reproducing. Nothing in `.claude/settings.json`
prunes skills.

No action. If it recurs, capture the exact session id and the skill count at both start
and recurrence, because a one-shot report with no live repro cannot be diagnosed.

---

## Item 7. Concurrent sessions. CONFIRMED AND WORSE THAN REPORTED.

Five `claude` CLI processes are live, **all five with cwd `/Users/josie/can-it-ford`**:

| PID | started |
|---:|---|
| 42959 | 08:51:57 |
| 10451 | 11:14:14 |
| 15666 | 11:23:24 |
| 22081 | 11:27:41 |
| 61708 | 12:29:22 (this one) |

Four peers with uncoordinated write access to one working tree. This is the same disease
CLAUDE.md records as ACTIVE BREACH 2026-08-07, at larger scale. It was directly observed
this session: `simulation/validate_coupling_force.py` changed under a reader mid-analysis,
and `bbox_probe.py` / `replay_tree.py` diagnostics surfaced for files this session never
touched.

**Gap found and closed.** `.claude/hooks/gate_destructive.sh` gates `git push`,
`git commit` and `rm -r`, but **does not look at `git add` at all**. The exact commands
CLAUDE.md forbids (`git add -A`, `git add .`, `git commit -a`) were ungated, and those are
what caused the 0797b08 / 3470ff9 breach.

`.claude/hooks/gate_concurrent_write.sh` (new, this session, tested) adds two guards:

1. **Bulk staging: deny.** `git add -A`, `git add .`, `git add --all`, `git commit -a`,
   `git commit -am`, with whitespace normalization. Explicit-path staging passes silently.
2. **Cross-session file claims: ask.** A TTL-based advisory registry under
   `.claude/state/locks/` (already gitignored) keyed on file path. If a *different*
   session wrote the same path within 30 minutes, the next Edit/Write asks instead of
   silently clobbering.

Tested: 4/4 bulk-staging cases denied, explicit-path add passes, same-session rewrite
passes, cross-session rewrite asks, unrelated file passes.

**It is not wired in yet.** Wiring requires editing `.claude/settings.json`, which is
itself hook-gated as a shared coordination file, and that is a decision for you, not for
one of five concurrent sessions to take unilaterally. The change is two entries under
`PreToolUse`:

```json
{ "matcher": "Bash",       "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/gate_concurrent_write.sh" }] },
{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/gate_concurrent_write.sh" }] }
```

Note `.claude/settings.json` is itself gitignored, so this change does not propagate to
the other machines by git. It has to be applied on each.

---

## Item 8. `check_claims.py` triage. Counts corrected; the gate's real problem is the hook.

**Verdict: triaged. The headline number was not the problem.**

The reported "165 ERROR / 27 WARN" is **stale, not wrong**: it is the exact output of the
checker at commit `6514bfc` against the tree at `6514bfc`. At HEAD `e0b983a` the live
figure is **161 ERROR / 99 WARN**, 260 hits across 80 files, exit 1. Also `--help` is not
a real flag; it falls through to staged mode and prints a clean 0/0.

Triaged, only **15 of 260 hits (5.8 percent) are REAL** live assertions of a refuted
value. 105 are archive documents legitimately quoting a retired value in order to retire
it, and roughly 127 are checker false positives. Two rules produce half the noise: C9
(72 WARN, whose own message at :183-185 concedes a bare year "is not by itself an error")
and C8 (34 ERROR, which fires on the refutation itself because, unlike C10b and C14, it
carries no `exclude=`).

**Largest single lever, no new logic:** `CORRECTION_LAYER` at `scripts/check_claims.py:60-65`
lists four paths while the repo has six more archive families of the same class. The
consumer at :345 already exists and already applies. Extending that tuple clears about 98
of 260.

**The more urgent problem is not the count.** `.claude/hooks/check_claims_posttool.sh`
invokes named-file mode, which scans the **whole file** rather than the added lines, so
editing any one line of 64 different files returns exit 2 on pre-existing hits the author
did not introduce. That, not the raw total, is why the gate is being ignored. The fix is
an `--added-only <file>` mode that diffs against the HEAD blob, mirroring the staged path
already at :272-287.

**Not applied here.** `scripts/check_claims.py` is clean at HEAD and is exactly the file
CLAUDE.md flags as contested between sessions. Landing rule-table edits from one of five
concurrent sessions is how the last breach happened. It needs a sequenced owner.

---

## Artifacts created this session

| path | what | status |
|---|---|---|
| `analysis/bingham_cfl_crossover.py` | Bingham/HB CFL crossover + sweep cost; self-tests against all 17 as-run substep counts | runs clean, 17/17 reproduced |
| `analysis/verify_cpic_ground_clearance.py` | ground-clearance resolution table + hull closure, pure numpy | runs clean, lim matches as-run exactly |
| `.claude/hooks/gate_concurrent_write.sh` | bulk-staging deny + cross-session claim registry | tested, NOT wired in |
| `docs/UNEXPLORED_AREAS_ASSESSMENT_2026-08-07.md` | this file | |

Run the two scripts with the venv interpreter where numpy is needed:

```
/Users/josie/.venvs/canitford-mpm/bin/python3 analysis/verify_cpic_ground_clearance.py
```

`analysis/bingham_cfl_crossover.py` is stdlib-only and runs under system `python3`.

---

## What is still open

- **C1 is not closed.** The free-rigid path forms no force, so `F_buoy_from_a` is a
  back-computation. The SDF discriminator is the right next step and a peer session is
  building it; the two default mismatches in item 2 must be fixed first or it will
  report a false failure.
- **Rigid particles carry identically zero stress.** `mpm_utils.py:1100` initialises
  `stress` to a zero mat33, :1104 excludes mat 8 from the SVD, and there is **no**
  `mat == 8` branch anywhere in :1105-1147 that assigns one (verified by hand). The hull
  therefore exerts no pressure on the water. This is very likely the same defect as the
  P-2 pass-through failures, not a separate one, but that identification has NOT been
  tested and should not be asserted until it is.
- Whether `vehicle_live.py` is a later upstream revision or a Vista-side hand-patch
  cannot be settled from the Mac.
- Literature values for `tau_y` and `eta` are not yet pinned to primary sources.
