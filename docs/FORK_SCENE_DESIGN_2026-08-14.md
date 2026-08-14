# The fork scene, and the constraint that decides its size

Dispatch 10, 2026-08-14. Branch `claude/fork-scene`.

Every number below was computed on this machine from a primary source and is
reproducible by running the module named beside it. Nothing is carried from a
summary. Claims are tagged `[read]` for a direct source read, `[run]` for
something this session computed, and `[inherited]` for something taken from
another session and not independently re-derived.

**Engine tag.** Every solver claim here is about **warpmpm at pinned SHA
`544c93dd02cb9c7ead89e1155a62967243244fce`**, read from the vendored copy at
`third_party/mpm-engine-544c93dd-solver-core/`. Nothing here is a Genesis claim
and nothing here is a Chrono claim.

---

## 0. What Dispatch 13's GO changes, and what it does not

`[read]` Verified independently before relying on it: commit `1f92205` on
`claude/fork-chrono-eval`, "GO: Chrono::FSI-SPH builds and runs on GH200
aarch64", `docs/CHRONO_GH200_GO_NO_GO_2026-08-14.md` records VERDICT: GO with
`demo_FSI-SPH_DamBreak` at RC 0 / 30,327 markers and `demo_FSI-SPH_ObjectDrop`
at RC 0 / 78,772 markers.

**DO NOT READ THE GO AS "THE CUBE PROBLEM IS SOLVED". IT IS NOT YET MEASURED.**
`[2026-08-14, coordinator]` A GH200 node (Vista JobId 911518, c642-011) has been
assigned to D13 to measure three things this design turns on: what terrain
geometry Chrono::FSI actually ingests, BCE marker spacing versus SPH particle
spacing and the smallest near-floor layer that implies, and **whether Chrono
carries a domain-shape constraint of its own**. Until that returns, the escape
is a hypothesis.

The failure branch is specific and must be stated in advance so it cannot be
quietly dropped: **if Chrono's SPH domain is also isotropic, then switching buys
the aspect-ratio saving and nothing else**, and the honest finding becomes
*"neither engine expresses a long shallow channel"* rather than *"switch to
escape the cube"*. Section 2.3 is already written so that either outcome can be
read straight off the same table: see 2.5 for exactly which column becomes
operative under each answer, and `docs/FORK_SCENE_FLAGGED_FOR_OWNERS_2026-08-14.md`
F-5 for the measurement request handed to D13.

Subject to that, the GO makes the cubic-domain constraint below **potentially
escapable by switching engines rather than by patching a grid**. It does not
make this document obsolete either way, for three reasons:

1. **Section 2 is the evidence for the switch, not a casualty of it.** The cost
   of road scale in warpmpm is the quantitative case for paying Chrono's
   migration cost. It had to be computed either way.
2. **Section 4 is engine-independent.** The cross-slope traction result is
   statics. It transfers to Chrono unchanged, and to any future engine.
3. **Section 4 also bears directly on how much Chrono's terrain ingest is
   worth.** Chrono's `RigidTerrain::AddPatch` and `SCMDeformableTerrain` can
   take an OBJ or heightfield, which is the single hardest thing to do in
   warpmpm. But that capability is only worth using if terrain geometry moves a
   verdict. Section 4 is the test of exactly that, and it is cheaper than the
   capability it is evaluating.

---

## 1. The hard architectural constraint

`[read]` `third_party/mpm-engine-544c93dd-solver-core/core/solver.py:48-54`:

```python
@dataclass
class GridConfig:
    n_grid: int = 64
    grid_lim: float = 0.4  # cubic domain edge, metres

    @property
    def dx(self) -> float:
        return self.grid_lim / self.n_grid
```

One scalar. The domain is a **cube** and the cell is **isotropic**. There is no
per-axis field, so this is not a default that can be overridden; it is the data
model. Two consequences, and the second is the one that is usually missed:

1. A long shallow channel costs cubically in extent.
2. **A road-shaped region of interest must be inscribed in a cube whose side is
   its longest dimension**, so most of the domain is air.

Consequence 2 is a property of the aspect ratio alone and **no grid choice
reduces it**:

> `[run]` For a 30 x 12 x 3 m road, the cube is 30 m on a side and the waste
> factor is **30² / (12 x 3) = 25.0x**.

That is the strongest single argument against an arXiv-2607.00673-scale scene in
this engine, and it is stronger than the cell-count argument because it survives
any resolution you choose.

---

## 2. The resolution-versus-extent trade

Reproduce with `python simulation/fork_scene/resolution_extent.py`.

### 2.1 The cost model is not cell count

`[read]` The canonical driver's own CFL rule, from the 389-line canonical copy
`renders/yaris_render_s1/_incoming/sim_standing.py:147-153` (sha256
`5215c38bed607ef6...`):

```python
c              = sqrt(1.1 * bulk_modulus / water_density)
term_acoustic  = c / (0.28 * dx)
term_viscous   = 6.0 * water_eta / (water_density * dx * dx)
term_advective = max(velocity, 1e-6) / (0.5 * dx)
substeps       = ceil(max(...) / fps)
```

`[run]` **Checked against the as-run record before use**, which is the only
reason to trust anything downstream of it:

| run | recorded `substeps` | model |
|---|---|---|
| `g64_m1100` | 11 | **11** |
| `g96_m1100` | 16 | **16** |

and `c = sqrt(1.1 x 150000 / 1000) = 12.84523257866513` m/s reproduces the
inventory's `sound_speed_ms` exactly. The acoustic term dominates and scales as
`1/dx`, so per-frame work is

```
cells x substeps  ~  n_grid^3 x (1/dx)  =  n_grid^4 / lim
```

> **Refining by 2x in `n_grid` costs 16x, not 8x.** Every cells-only refinement
> estimate in this project understates the cost by exactly the refinement factor.

### 2.2 A premise from the dispatch that does not survive checking

The dispatch states *"the validated near-floor regime is about 18 cells across
that depth, so dz = 0.01636 m"*, and its 246.8 M / 279x figures follow from it.

`[run]` **The arithmetic reproduces exactly**, so the figures are auditable:

| dispatch figure | reproduced here |
|---|---|
| 30 x 12 x 3 m box at isotropic dz | **246,772,943** cells |
| canonical Yaris tank at g96 | **884,736** cells |
| ratio | **278.9x** |
| anisotropic dxy 0.08 / dz 0.01636 | **10,316,563** cells, **23.9x** reduction |

`[read]` **But the 18 is not a validated regime.** Traced to
`docs/C1_ROOT_CAUSE_2026-08-07.md:337-347`, which records that commit `20dd999`
*"deepened C2 to 18 cells on the argument that the box grounded out for lack of
clearance"*, that `scripts/c2only.sbatch:19-20` passed `--depth-cells 18` as job
`894676`, and that job's *"four C2 arms all crashed at the same guard anyway"*.
`run_c2`'s own default is still `depth_cells=10`.

So 18 is a **proposed fix in a validation arm that failed**. Nothing in this
project has validated any cells-per-depth figure. What the project has actually
run is 2 cells per depth at g64 and 3 at g96, against a rules-of-thumb ~10
particles per flow depth (~5 cells at `h = dx/2`), which CLAUDE.md L-3 already
records as a stated limitation.

### 2.3 The trade across the whole plausible range

`[run]` Cells-per-depth is therefore treated as a free parameter. The forced
cube is 30 m on a side in every row; only the resolution changes.

| cells/depth | dz (m) | ROI box cells | CUBE `n_grid` | CUBE cells | substeps | cells vs g96 | **work vs g96** |
|---|---|---|---|---|---|---|---|
| 2 *(= as-run g64)* | 0.14721 | 351,288 | 204 | 8,489,664 | 11 | 10x | **7x** |
| 3 *(= as-run g96)* | 0.09814 | 1,166,778 | 306 | 28,652,616 | 16 | 32x | **32x** |
| 5 *(~10 particles/depth)* | 0.05889 | 5,306,040 | 510 | 132,651,000 | 26 | 150x | **244x** |
| 10 *(`run_c2` default)* | 0.02944 | 42,406,704 | 1,019 | 1,058,089,859 | 52 | 1,196x | **3,887x** |
| 18 *(dispatch's figure)* | 0.01636 | 247,827,760 | 1,835 | 6,178,857,875 | 94 | 6,984x | **41,030x** |

**The correction, stated as the coordinator asked, with the resolution beside
each figure:**

> The cubic constraint alone costs **25.0x** for a 30 x 12 x 3 m road. That
> figure assumes no resolution at all; it is pure aspect ratio.
>
> The road-scale cube is **10x** the canonical g96 tank in cells **at 2 cells
> across the water depth**, which is the as-run g64 resolution, against
> **6,984x** **at 18 cells across the depth**, which is the dispatch's
> unvalidated figure.

`[run]` **The defensible claim is therefore not "road scale is impossible in
warpmpm". It is "road scale is reachable only at a resolution this project has
already labelled a limitation."** At the resolution the 17 gated runs actually
used, a road-scale cube is 8.5 M cells and 7x the g96 per-frame work, which is
entirely runnable. What is not defensible is the physics inside it.

### 2.4 What an engine switch would and would not buy

The table in 2.3 already contains both answers, and which column is operative
depends entirely on D13's pending measurement. This is written **before** that
measurement so neither outcome can be presented as the expected one.

- **`CUBE cells`** is warpmpm: one scalar edge, so the road must be inscribed in
  a 30 m cube.
- **`ROI box cells`** is what an engine with three independent domain extents
  but still-isotropic cells would cost: the 30 x 12 x 3 m region only.

`[run]` The ratio between those two columns is the aspect-ratio waste factor and
nothing else. It is **24.17x, 24.56x, 25.00x, 24.95x, 24.93x** down the five
rows, approaching the exact `30²/(12x3) = 25.000` from below; the scatter is
per-axis integer ceiling, not physics, and it shrinks as the grid refines.

> **If Chrono's domain is an arbitrary box with isotropic spacing, switching
> buys exactly 25.0x and not one thing more.** The resolution penalty is
> untouched: 5,306,040 cells at 5 cells across the depth against 247,827,760 at
> 18 is a 47x spread that no engine choice affects.
>
> **If Chrono's domain is also shape-constrained, switching buys nothing here**
> and the finding becomes "neither engine expresses a long shallow channel."
>
> **Only a per-axis-gradeable spacing would change the resolution story**, and
> that is a different capability from a box-shaped domain. The two are routinely
> conflated and must not be.

Note that ~25x is worth having: `[run]` at 5 cells across the depth it is the
difference between **244x** and **9.7x** the canonical g96 per-frame work, which
moves road scale from "no" to "yes" at that resolution. It is just far smaller
than the 279x headline suggested, and it does not rescue the finer rows: at 10
cells across the depth the box is still **155.8x** and at 18 it is **1,645.7x**.

### 2.5 Anisotropy is not a way out

Two independent reasons, both of which must be stated because either alone
invites the other as a workaround:

1. `[read]` **`GridConfig` cannot express it.** One scalar, section 1.
2. **Even if it could, the explicit timestep follows the smallest cell
   dimension**, so grading buys memory and per-step work and **not step count**.

Anisotropy is therefore a reason to change engine or patch the grid, not a free
win. `[inherited]` And any refinement scheme must co-refine or explicitly
control particles-per-cell: Steffen, Wallstedt, Guilkey, Kirby and Berzins 2008,
DOI 10.3970/CMES.2008.031.107, shows fixed PPC can *lose* convergence under
refinement, and this stack holds PPC constant at 8.

---

## 3. Domain sizing, and the axis trap closed by construction

Reproduce with `python simulation/fork_scene/domain.py` and
`python tests/test_fork_scene_domain.py`.

### 3.1 The rule

```
lim = max(2.2 * ext_long, 3.5 * ext_short, 6.0 * depth)
```

`[read]` This is the as-ran rule, live at `_incoming/sim_standing.py:82`,
`sim_enhanced.py:232`, `vehicle_live.py:349` and `gp_surrogate.py:26`.

> **Citation drift, worth recording.** The dispatch cites
> `sim_standing.py:82`. That resolves in the `_incoming/` copy (389 lines,
> sha256 `5215c38b...`), which register D4a names as the canonical per-run tree.
> The **top-level** `renders/yaris_render_s1/sim_standing.py` is 564 lines,
> sha256 `4696c3b2...`, and carries the same rule at **:160**. Cite the copy,
> not just the line.

### 3.2 The trap

`[run]` Measured from the canonical PLY's own vertex block (327,212 vertices,
sha256 `b379fa44..e9949a95`; the same artifact is on LS6 `/work`, sha head
`b379fa4472c68065`):

```
PLY extents (x, y, z)     4.282609940  1.746377945  1.518008113   <- long axis on X
lim, PLY axes face value     14.989134789 m
lim, as-run (inventory)       9.421742314 m
error                            +59.0909 %
```

`load_vehicle(up="z")` swaps x and y so the long axis lands on **y**; the
positional rule `max(2.2*ext[1], 3.5*ext[0], ...)` is written for that frame.
Applied to raw PLY axes it multiplies the **length** by 3.5 instead of 2.2.

`[run]` **New, and it makes the trap easier to spot:** the error is *exactly*
`3.5/2.2 - 1 = +59.0909%` on all three qualified hulls, not three unrelated
percentages, because the `2.2*long` term wins the max for all three. A single
constant is far more visible in a diff.

### 3.3 The fix, and the guard nobody needed yet

The rule is made **invariant** rather than remembered: sort the two horizontal
extents, never read them positionally. `[run]` All three hulls reproduce their
recorded as-run `lim`:

| hull | sha256 head | rule | recorded | residual |
|---|---|---|---|---|
| yaris | `b379fa44` | 9.421741867 | 9.421742314 | 4.5e-7 m |
| rogue | `c0b778e2` | 10.442536068 | 10.442536068 | 3.7e-11 m |
| silverado | `46fba11e` | 13.067932987 | 13.067932987 | 2.1e-10 m |

The yaris residual is 4.7e-8 relative and is precision, not disagreement: rogue
and silverado were recorded from these same meshes, while yaris's recorded value
came off the as-run driver, which sizes from the **loaded** (float32,
post-canonicalization) extent rather than the raw PLY bounding box. Stated
rather than hidden behind a loose tolerance.

`[run]` **Sort the two horizontal extents, not all three.**
`hull_sweep.sbatch:30-33` describes the anchor as derived from "sorted extents".
Sorting all three lets a hull's **height** supply `ext_short` whenever the hull
is taller than it is wide. All three qualified hulls are wider than tall
(yaris 1.746 vs 1.518; rogue 2.010 vs 1.729; silverado 2.338 vs 2.010), so this
**changes no published number today**. It would bite the first van or box truck
to enter the sweep, which is exactly when nobody would be looking.

### 3.4 The test is a test, not a tautology

`[run]` 10/10 pass. The suite includes a **paired negative control**:
`grid_lim_naive_positional` is kept in the module, and
`test_naive_positional_form_is_actually_broken` asserts it *still* diverges
under an axis swap. If the positional form is ever quietly fixed, that test
fails and says the invariance test has stopped being evidence of anything.
`test_anchor_guard_actually_refuses` likewise proves the anchor guard can fail.

---

## 4. Cross-slope: the sensitivity result

Reproduce with `python simulation/fork_scene/cross_slope.py`.

### 4.1 Why cross-slope is the right terrain property

`[read]` In the canonical scene the hull's long axis lies on **y** and the flow
runs along **x**. A road's direction of travel is therefore y, and its
cross-slope, the camber or superelevation perpendicular to travel, lies along x.

> **The road's cross-slope *is* the bed slope of the cross-road flow.**

It is not a decoration on the floor; it is the channel's S₀. That is why it, and
not surface roughness or local geometry, is the terrain property worth testing
first at this scale.

### 4.2 Two formulations, and they are not equally good

**T, tilted plane.** `add_plane(point, normal=(sin θ, 0, cos θ), ...)`.
`[read]` Arbitrary normals work: `add_surface_collider` normalises whatever it
is handed (`mpm_solver_warp.py:1892-1893`) and the grid test is a half-space dot
product (`:1947-1955`). Two costs, both found by reading the kernel rather than
by running into them:

- `[read]` **It loses the restricted-launch fast path.**
  `mpm_solver_warp.py:1997` selects a bounded launch box only when
  `abs(abs(normal[i]) - 1.0) < 1e-6` for some axis; anything else appends `None`
  to `collider_aabbs` and is labelled `"plane_free"` (`:2013-2016`), i.e. the
  collider kernel launches over the **whole grid** every substep. `[run]` The
  canonical floor at `3*dx` with halo 1 covers about 5 of 65 node layers, so
  tilting it multiplies that kernel's launch volume by **13.0x**. That is one
  kernel's node-layer count, not a whole-run slowdown, and must not be quoted as
  one.
- `[run]` **It eats the tank's headroom.** A cube of edge `lim` with slope S
  drops `S*lim` wall to wall. At the canonical geometry: **S=0.02 drops 0.1884 m
  = 64.0% of the depth; S=0.06 drops 0.5653 m = 192.0%**, at which point the
  upstream end is dry and there is no held-fixed comparison left.
  `scene.py` refuses to build that configuration rather than producing a number
  from it.

**G, tilted gravity in a bed-aligned frame.** Floor stays at `(0,0,1)`; gravity
becomes `g' = (g sin θ, 0, -g cos θ)`. Fast path survives, water depth is
uniform by construction, water volume is identical to the S=0 control.

`[run]` **This requires overriding gravity, and gravity is overridable.** Chain
verified end to end in the vendored solver:

```
core/solver.py:166          params = {**params, **overrides}
core/solver.py:167-169      {"material": name, "g": [0,0,-9.81], **params}
                            -> **params expands AFTER "g", so a caller wins
mpm_solver_warp.py:742-743  if "g" in kwargs: self.set_gravity(kwargs["g"])
```

Confirmed by executing that exact dict-merge: a `g=` override returns the
caller's vector. **No engine patch is needed.** See section 6 for the CLAUDE.md
correction this implies, which is filed rather than applied.

**Recommendation: G for the physics, T only as a cross-check.** They are the
same system in two frames and must agree in the interior, differing only in the
orientation of the domain walls, a 1.15° difference at S=0.02.

### 4.3 The static half, in closed form, needing no simulation

Stationary vehicle, bed-aligned frame, submerged weight `(W - B)`:

```
N   = (W - B) cos θ - L          F_F = μN          F_x = F_D + (W - B) sin θ
M   = F_F - F_x
ΔM  = M(θ) - M(0) = -(W - B) [ sin θ + μ (1 - cos θ) ]
```

`[run]` **ΔM is exactly independent of the drag**, because `F_D` enters
additively and the tilt does not change it. Verified numerically, not just
algebraically: the closed form equals a direct difference of two full balances
evaluated at an arbitrary drag, to < 1e-9 N. **So this result does not depend on
the unresolved C_D 1.22-6.82 joint envelope at all.**

`[run]` As a *fraction* of available traction, `ΔM/(μ(W-B)) = sin θ/μ + (1-cos θ)`,
which contains no vehicle property. It is **vehicle-independent** and
approximately `S/μ`:

| vehicle | W-B (N) | B/W | μ(W-B) (N) | ΔM at S=0.02 | ΔM at S=0.06 |
|---|---|---|---|---|---|
| yaris (1100 kg) | 6,547.3 | 39.3% | 1,964.2 | **-131.3 N (-6.69%)** | **-395.7 N (-20.14%)** |
| rogue (1571.3 kg) | 10,732.4 | 30.4% | 3,219.7 | -215.2 N (-6.69%) | -648.6 N (-20.14%) |
| silverado (2270 kg) | 19,884.6 | 10.7% | 5,965.4 | -398.8 N (-6.69%) | -1,201.6 N (-20.14%) |

Buoyancies are from the measured `phase3.json` displacement curves at the
canonical 0.2944294473 m waterline, μ = 0.30 (Bonham and Hattersley 1967, the
conservative parked baseline).

`[run]` **The normal-load loss is second order in θ; the added downslope weight
is first order.** At S=0.02 the first-order term `-(W-B)S` is -130.9 N against
the exact -131.3 N, so the cos θ correction contributes 0.28%. The slope term
dominates for *any* μ, because μ multiplies only the second-order part. The
fractional loss scales as `1/μ`, so it is **worst exactly where the flood case
lives**, at low tyre friction.

### 4.4 What this reframes

The dispatch asked whether cross-slope changes the traction margin, and framed a
null result as the publishable outcome. The answer is **yes, materially, and by
an amount that is exact and needs no solver**. That is not the interesting part.
The interesting part is what it leaves:

> The static term needs no simulation and can be applied as a post-hoc
> correction to any flat-bed result already in hand, on either engine. So the
> only thing a simulation can contribute is whether a bed slope moves the
> **hydrodynamic** term beyond that static tilt.

That is a cheaper and sharper test than "simulate terrain", and it is the
experiment now queued. **It is also the test that prices Chrono's terrain
ingest:** if the leftover is inside the noise, then the ability to load an OBJ
terrain buys less than it appears to, on any engine.

### 4.5 The measurement, and its confound predicted in advance

`[run]` LS6 job **3364533**, `gpu-a100`, four arms at g64 / 90 frames,
formulation G. Three-way decomposition:

1. **Static** — exact, section 4.3, no run.
2. **Hydrostatic** — in a *closed* tank, tilting gravity tilts the equilibrium
   free surface, so the depth at the vehicle changes with no hydrodynamics at
   all. Derived in advance: the surface is perpendicular to `g'`, giving
   `dz/dx = +tan θ`, and volume conservation pivots it about the water
   x-centroid, so `Δd(x_veh) = S (x_veh - x_centroid)`. The vehicle sits at
   `0.60 lim` and the centroid at `0.50 lim`, so the predicted rise is
   `0.10 S lim` = **+0.0188 m at S=0.02, +6.4% of the depth**.
3. **Hydrodynamic** — measured minus predicted, against the noise floor.

Four falsifiable checks are built into the runner so a broken run cannot look
like a result:

- **C1** the reproduced scene must match `all_runs_inventory.csv` `g64_m1100` on
  `grid_lim`, `dx`, realized depth, `water_layers`, `n_water` (48,367),
  `n_vehicle` (8,905) and `substeps` (11), or it aborts before stepping. The
  scene is *reproduced* rather than imported because `renders/` is gitignored
  and the canonical driver is **not present on LS6** (checked live), so an
  import would be a hidden dependency on an untracked file; asserting against
  the inventory is stronger evidence than importing would have been.
- **C2** `|g'|` must equal 9.81 to 1e-12. A tilt rotates gravity; it must never
  rescale it.
- **C3** the measured free-surface slope must recover `+S`. This is the direct
  test that the gravity override reached the kernels rather than being dropped.
- **C4** arms 0 and 1 are the same configuration at the same seed, so their
  spread is the noise floor. `[inherited]` Register C-7 records six `metrics.csv`
  differing at identical config, node and driver while every
  `determinism_identical` flag reported True, so the flag cannot supply this and
  a repeated arm must.

---

## 5. In/outflow: wiring, not a third implementation

`[read]` Two implementations of the Zhao et al. 2019 BC already exist:

- `simulation/coupling_force/inflow_outflow.py`, **tracked on main**. Its own
  header: *"CPU reference implementation... NOT run against the GPU solver. No
  gated run uses it."* `[run]` A repo-wide search returns **zero code
  consumers**; only `README.md` and two findings docs mention it.
- `simulation/realism/outflow_deactivate.py` on `realism-exploration`, GPU-wired
  through `particle_selection`, already run. Not on main, not in this
  dispatch's scope to move.

`simulation/fork_scene/scene.py` adds `SelectionOutflow`, which **composes** the
tracked module and follows the realism branch's design. This is its first
wiring.

**The defect a naive wiring would hit.** `[read]` `RecyclingConveyor.step()`
sets `self.active[i] = False` and returns the position and velocity arrays
*unchanged* for that particle. `active` is CPU bookkeeping with **no solver-side
effect**: a "retired" particle stays fully simulated, sitting where it died,
still depositing mass and momentum, until it happens to be reissued. The outflow
would be a no-op in the physics while the bookkeeping reported it working. That
is not a criticism of the reference module, which says plainly it was never run
against a solver; it is precisely what the wiring has to add.

**The real sink, verified in the kernels.** `[read]`
`state.particle_selection[p] == 0` gates the four per-particle fluid kernels at
`mpm_utils.py:922` (p2g), `:1049` (g2p), `:1157` (stress) and `:1173` (fused).
Setting it to 1 removes the particle from the fluid **and freezes it in place**,
so `solver.x()` still returns it and every depth or volume measurement must mask
on the active set. `[read]` Two further gates at `:1380` and `:1472` are
`particle_selection[p] == 0 and particle_material[p] == 8`, i.e. the **rigid**
kernels honour it too, so deactivating a rigid index would silently remove part
of the hull; `SelectionOutflow` refuses to touch any index outside the water
range for that reason.

**Never call it a port.** `[inherited, register B7]` Zhao et al.'s outflow is
pressure-controlled and warpmpm has no pressure field at any point; pressure
exists only implicitly per particle through `J = det(F)` and the bulk modulus.
The substitute is depth-keyed and position-keyed deactivation, which is B7's own
re-expression. The **velocity-controlled inlet** is the half that genuinely does
translate.

> Zhao, X., Bolognin, M., Liang, D., Rohe, A., Vardon, P. J. (2019).
> Development of in/outflow boundary conditions for MPM simulation of uniform
> and non-uniform open channel flows. *Computers & Fluids*, 179, 27-33.
> doi:10.1016/j.compfluid.2018.10.007. Implemented by them in Anura3D, a
> Delft-lineage code unrelated to warpmpm, so this is a **translation**, not a
> port. **Not Kumar**; that attribution was corrected 2026-08-07.

`[inherited]` **A measured negative that constrains the design.**
`open_channel.py`'s `ChannelRecycler` was tested 2026-08-12 and **lost to the
closed tank** on depth-hold, 30.0% against 58.9%, and a downstream sponge did
not rescue it at any gain. Recorded mechanism: a streamwise periodic wrap has no
mass or energy sink, so the surge re-injects and circulates. Deactivation is a
real sink and is therefore a different boundary condition, not the same one
again. If it still loses, that is a second negative and gets reported as one.

### 5.1 A defect this session introduced, and the test that caught it

Recorded because it is the most transferable thing in this section.

`[run]` The **first** version of `SelectionOutflow` took its inlet rate from
`InletBC.particles_per_step`, i.e. `n = Q·dt/v_p`, because that is what the
tracked CPU reference does. At the canonical geometry that is **~304 particles
per tick** against an outflow of order tens. So the retired pool drained on
every tick, and **every retired particle was re-injected at the inlet in the
same tick it left**.

That is precisely the streamwise periodic wrap that `ChannelRecycler` was
already refuted for. The class would have reported a working outflow, with
plausible retirement and reissue counters, the entire time — while being the
boundary condition this project had already measured as *worse than doing
nothing*.

`tests/test_fork_scene_outflow.py::test_retirement_reaches_the_solver_array`
caught it: it asserts the solver's `particle_selection` array is non-zero after
a tick, and it was zero because everything had been reissued.

Three things changed as a result:

1. `inlet_mode` now defaults to **`"depth"`**, demand-driven on an inlet depth
   deficit, which is what `outflow_deactivate.py` does and what makes the pool
   able to *absorb* a surge instead of re-injecting it. `"discharge"` remains
   available, because "what does a prescribed Q do" is a legitimate question,
   but it is no longer the default.
2. **`wrap_ratio()`** = reissued/retired is now a published diagnostic.
   Sustained ~1.0 with a pool that never accumulates means the BC has
   degenerated into the refuted one. `[run]` Two tests pin both behaviours:
   discharge mode is asserted to give exactly 1.0 with an empty pool, depth mode
   is asserted to retain a pool and stay below 1.0.
3. The class docstring now records the whole episode rather than just the fixed
   design.

**The general lesson, which is not specific to this BC:** the reference module
was correct as a model and its own header said it had never been run against a
solver. The failure was not in it. It was in wiring a *rate* from a module whose
rate had never had to compete with anything. A counter that looks healthy is not
evidence a boundary condition is doing what it says.

### 5.2 Status

`[run]` `SelectionOutflow` now passes **12/12** logic tests against a fake solver
that reproduces `Solver.x()`'s host-copy semantics (so a wiring that mutates the
returned array without calling `set_x` cannot pass). Those tests cover the
solver-array write, the AND-not-OR retirement rule, rigid-particle safety,
count invariance, masked measurement, reissue placement and velocity, state
reset, and both inlet modes.

**It has still NOT been run against the real solver.** What the tests establish
is the bookkeeping; what they cannot establish is that a selection of 1 really
stops a particle, and that rests on the kernel reads above rather than on any
run.

The cross-slope job deliberately **does not use it**, because an unvalidated BC
inside a sensitivity test would confound the thing being measured. The
cross-slope arms use the canonical closed tank with the sustained inflow clamp,
which is exactly the `standing_water_sustained_inflow` scenario all 17 gated
runs use.

---

## 6. Filed for other owners, not edited here

Per the ownership table, these belong to other dispatches. Full detail in
`docs/FORK_SCENE_FLAGGED_FOR_OWNERS_2026-08-14.md`.

1. **CLAUDE.md item 3, the word "unconditionally"** — falsified; `g` is a
   default, not a constant. Item 3's *conclusion* still stands. Relayed to D4.
2. **`sim_standing.py:82` citation drift** — resolves only in the `_incoming/`
   copy; the top-level copy carries the rule at `:160`.
3. **The unvalidated 18-cells figure** — section 2.2; relayed to D13.

---

## 7. What is not done

Stated so it is not mistaken for finished work.

- **The cross-slope hydrodynamic result** is queued as LS6 job 3364533, not
  returned. Section 4.5 states the prediction and the checks in advance so the
  result cannot be fitted to a story afterwards.
- **`SelectionOutflow` has never been run against the solver.** Section 5.
- **Formulation T was never run.** Its costs are read from the kernel and
  computed, not measured. `scene.py` refuses to build it above S≈0.03.
- **No lift term exists anywhere in this project.** `VehicleState.lift_n` is
  0.0, which biases every margin here **optimistic**, so they are upper bounds.
- **No reconstructed terrain was attempted**, per the dispatch. If section 4's
  hydrodynamic leftover turns out to matter, metric scale must be solved at
  capture time with a known-length reference object in frame.
