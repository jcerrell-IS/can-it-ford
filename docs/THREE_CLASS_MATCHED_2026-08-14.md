# Three vehicle classes at matched resolution, 2026-08-14

**NON-CANONICAL COMPANION EXPERIMENT.** This is not an extension of the 17 gated runs.
It writes nothing into `data/all_runs_inventory.csv` or
`renders/yaris_render_s1/gates_results_all_runs.json`, both of which are Yaris-only and
stay that way. Folding vehicle classes into the canonical store is a human decision and
has not been taken. No existing run directory under `renders/` or `data/` was written to:
register item 16 exists because job 866887 overwrote the g48/g96 run directories on
2026-07-26 and made six canonical margins permanently unverifiable.

**Engine: warpmpm.** Not Genesis. Every solver claim below applies to the warpmpm
material-8 free-rigid path via `renders/yaris_render_s1/sim_standing.py`.

Claims are tagged `[live]` when re-derived here against source or a live command,
`[read]` when read directly out of a named file, and `[inherited]` when carried from
project knowledge and not re-checked.

---

## 1. What this set exists to do

Three AR&R vehicle classes have converged, watertight, sha256-anchored hulls, and the
project has never run them together under controlled conditions. The blocker was never
capability. It was that **a cross-vehicle run at a shared `n_grid` is not one experiment
at three sizes**, so any ordering read off such a set could be resolution rather than
geometry.

That claim is now measured rather than asserted.

## 2. The confound, measured `[live]`

`sim_standing.py:160` derives the domain edge from the **loaded hull**:

```python
lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
```

and `third_party/mpm-engine-544c93dd-solver-core/core/solver.py:53-54` sets
`dx = grid_lim / n_grid`. A shared `n_grid` therefore gives each vehicle a different cell
size. At `n_grid = 96`, computed by `analysis/three_class_matched_grid.py`:

| vehicle | dx (m) | realized depth (m) | water layers | depth/dx |
|---|---|---|---|---|
| yaris | 0.0981431 | 0.294429 | 6 | 3.000 |
| rogue | 0.1087764 | 0.326329 | 6 | 3.000 |
| silverado | 0.1361243 | 0.272249 | 4 | 2.000 |

**dx spread 38.70 percent, realized-depth spread 19.86 percent.** The sharper form of the
defect is the last column: the Silverado is resolved across the water column with **two**
cells where the other two get three. That is a categorical difference in how well the flow
is resolved, not a small numerical one, and it runs in the *opposite* direction to vehicle
size, so it systematically disadvantages the largest hull.

## 3. The matched design `[live]`

`n_grid` is the only free integer, so the matched arm chooses it per vehicle:

| vehicle | n_grid | dx (m) | realized depth (m) | water layers | depth/dx | n_water |
|---|---|---|---|---|---|---|
| yaris | 111 | 0.0848806 | 0.297082 | 7 | 3.500 | 294,175 |
| rogue | 123 | 0.0848987 | 0.297145 | 7 | 3.500 | 367,087 |
| silverado | 154 | 0.0848567 | 0.296998 | 7 | 3.500 | 592,767 |

**dx spread 0.0494 percent, realized-depth spread 0.0494 percent**, a factor of about 780
reduction in the confound, at 7 water layers and `depth/dx` exactly 3.500 for all three.

An **exact** common dx does not exist for any integer triple, because the domain edges are
measured floats. 0.0494 percent is reported as *achieved*, not claimed as *matched*, and
every run stamps its own `dx` into `summary.json`.

### Why matching dx is the only route to matching depth

The water block is built at `sim_standing.py:181` as
`zs = arange(floor + 0.5*h, floor + depth, h)` with `h = dx/2`, so the layer count is
`ceil(depth/h - 0.5)` and the realized depth is `water_layers * h`. The layer count is an
**integer**, and one layer is roughly 25 percent of the depth at these resolutions.
Realized depth therefore cannot be tuned independently of `dx`: matching `dx` matches both,
or neither. The nominal `--depth 0.30` is never the realized value.

### The chain is verified, not assumed `[live]`

`analysis/three_class_matched_grid.py` refuses to plan unless the extent to dx chain
reproduces five values it did not produce:

| anchor | got | want | source |
|---|---|---|---|
| Yaris g64 dx | 0.1472147237 | 0.1472147236519959 | CLAUDE.md L-3, from `data/all_runs_inventory.csv` |
| Yaris g64 realized depth | 0.2944294473 | 0.2944294473039918 | same |
| Yaris g96 dx | 0.0981431 | 0.0981 | reconciliation dispatch trap 3 |
| Rogue g96 dx | 0.1087764 | 0.1088 | same |
| Silverado g96 dx | 0.1361243 | 0.1361 | same |

All five reproduce. That also **confirms rather than assumes** the axis convention:
`load_vehicle(path, up="z")` puts the mesh long axis, which the `.ply` stores on **x**, onto
scene **y**, so `vehicle.extent[1]` is the raw x extent. The Yaris raw bbox x extent is
4.282610143 m and `2.2 x 4.282610143 = 9.4217423`, which is exactly the `lim` implied by the
published g64 `dx`. This is consistent with CLAUDE.md item 4(c) and with the render branch's
independently derived 90 degree yaw.

## 4. Hulls, anchored by sha256 `[live]`

Computed on the Mac and again on LS6 at the paths the job actually reads. All three match
the digests in the dispatch:

| class | file | sha256 | volume m3 | verts |
|---|---|---|---|---|
| compact_sedan | `yaris_coarse_v1l_watertight.ply` | `b379fa4472c68065…e9949a95` | 3.542739 | 327,212 |
| midsize_suv | `rogue_g96_pd8_coarse_watertight.ply` | `c0b778e2c4432631…06c310b2` | 4.950341 | 36,074 |
| large_4wd | `silverado_g96_pd8_coarse_watertight.ply` | `46fba11e77cd92dd…f7d466d7f9` | 7.962083 | 26,072 |

The vertex counts independently match those in `vehicle_meshes/candidates/SUMMARY.md`,
which measured the volumes with the same trimesh loader the 17 gated runs used.

The mesh pipeline is **not** bit-reproducible, so nothing here was regenerated to "verify"
it; the artifact digest is the anchor.

**Watertightness does not propagate into the sim.** Register E2: `FloodScene vehicle.py:162`
samples the mesh down to 60,000 surface points before solidifying. The hulls are watertight
as artifacts; the solidified particle clouds are what the solver integrates.

## 5. A correction to trap 1, and a live hole in the guard that implements it `[live]`

The dispatch's trap 1 reads: *"Do NOT use anything in `vehicle_meshes/candidates/`. Those
two files are sha256 duplicates of pool files AND are the two worst hulls by volume
convergence."* That sentence conflates two different pairs, and the directory-shaped rule
it implies does not protect anything.

`vehicle_meshes/candidates/` holds **four** `.ply` files, not two:

| file | sha256 | status |
|---|---|---|
| `rogue_g96_pd8_coarse_watertight.ply` | `c0b778e2…` | byte-identical to the **good** pool hull. This is a file the dispatch tells you to use. |
| `silverado_g96_pd8_coarse_watertight.ply` | `46fba11e…` | byte-identical to the **good** pool hull. Same. |
| `rogue_candidate_euler-32.ply` | `5ef64621…` | **retracted**, 47.53 percent below converged volume |
| `silverado_candidate_euler-82.ply` | `c9c58ca7…` | **retracted**, 31.40 percent below converged volume |

So two of the four files in the "do not use" directory are exactly the hulls this
experiment is required to use, distinguished only by name.

**And the retracted pair is reachable from the pool directory under other names.** Verified
by sha256 this session:

```
5ef646213e00c863…  candidates/rogue_candidate_euler-32.ply
5ef646213e00c863…  rogue_g96_pd6_coarse_watertight.ply          <- same bytes, pool dir
c9c58ca7b931d09d…  candidates/silverado_candidate_euler-82.ply
c9c58ca7b931d09d…  silverado_g32_pd8_dq0.02_coarse_watertight.ply  <- same bytes, pool dir
```

The driver already carries a guard, `sim_standing.py:73`:

```python
RETRACTED_HULL_TOKENS = ("candidate_euler",)
```

matched against `path.name` at `:83-89`. It blocks the two `candidates/` filenames and
**does not block either pool alias**, which are the identical bytes. A run pointed at
`rogue_g96_pd6_coarse_watertight.ply` gets the 2.597 m3 hull, a 47.5 percent volume
deficit feeding straight into buoyancy, with no refusal and a plausible-looking log.

**Recommended fix, not applied here** (changing the driver mid-experiment would invalidate
the driver sha256 that stamps these runs, and other dispatches share this file): gate on the
artifact digest rather than the filename, since digests are exactly what the project already
uses to identify these hulls.

```python
RETRACTED_HULL_SHA256 = {
    "5ef646213e00c86357a6b5c983fbd7b60fe40c0c93af93e0c260de4c2b924006",  # rogue pd6
    "c9c58ca7b931d09dc6291280b08695a5eac87cad4283b8cd2a3bb66121759ba1",  # silverado g32
}
```

The existing token check should stay: it is cheaper and catches the common case before a
file is hashed.

Trap 1's percentages are also slightly off against the source it cites: `SUMMARY.md` gives
**47.53 and 31.40** percent, where the dispatch says 47.5 and 31.1. The 31.1 does not appear
in `SUMMARY.md`.

Separately, trap 2 stands and is worth restating because it explains the whole episode:
`euler_number` cannot gate this geometry. The canonical Yaris sits at **-442**, so a gate
selecting for euler near 2 would reject the project's own reference hull. Rank by distance
from converged volume.

## 6. Masses, and closing the dispatch's open trace on 1571.3 `[live]`

The dispatch records as open: *"the string `1571.3` appears nowhere in the project knowledge
that was searched. Trace it in the repo, not from memory."*

**Traced. It is in the repo, in five declaration sites and with a documented source.**

| site | form |
|---|---|
| `renders/yaris_render_s1/sim_standing.py:54` | `"mass_alt_kg": 1571.3` (the registry) |
| `render_s2/multigeom_2026-08-08/sim_standing.py:54` | second copy of the driver |
| `analysis/classify_rogue_silverado_sweep.py:47` | `MASS = {"rogue": 1571.3, ...}` |
| `scripts/class_specific_2026-08-08.sbatch:59` | `MASS_ROGUE=1571.3` |
| `data/rogue_silverado_sweep_2026-08-13/run_rs_sweep.sh:69` | `go rogue 1571.3 "$G"` |

The source is recorded in two committed files, not only on the web:
`scripts/class_specific_2026-08-08.sbatch:53` and
`docs/MESH_RECONCILIATION_2026-08-08.md:233` both give **cars.com, 2020 Rogue FWD S curb
weight 3,464 lb**, flagged secondary because the Rogue deck states no mass at all, which
that document verified directly against `rogue-v3.key`.

Why the trace looked empty: `docs/MESH_RECONCILIATION_2026-08-08.md:151` itself asserts
*"1571.3 kg does not appear in project documentation"*, and that sentence is **contradicted
by line 233 of the same file**. A search that found the earlier line and stopped would
conclude the number was untraceable. The claim should be corrected to: 1571.3 does not
appear in the **vehicle deck**, which is true and is the point being made.

Two arithmetic notes, neither material but both worth recording rather than silently
carrying:

- 3,464 lb is **1571.244 kg** (international avoirdupois pound, 0.45359237 kg exactly;
  cross-checked with Wolfram, which returns 1571 kg to 4 significant figures). The project's
  1571.3 is **+0.056 kg, +0.0036 percent** off a straight conversion, which rounds the wrong
  way. Exactly 1571.3 kg would need 3,464.12 lb.
- A live NHTSA pull recorded in the reconciliation document puts the real 2020 Rogue trims at
  **FWD 1550 kg / AWD 1610 kg** `[inherited]`. 1571.3 falls between them and **pins to no
  published trim**. The AR&R `large_passenger` class figure, 1609 kg, is the one that matches
  a real trim almost exactly.

### Which masses this set uses

| vehicle | arms S and M | provenance | labelled alternative |
|---|---|---|---|
| yaris | **1100.0** | deck header line 28, and `vehicle_params.py` `mass_kg` | none, the two agree |
| rogue | **1571.3** | web-sourced; the Rogue deck states no mass | AR&R `large_passenger` 1609 |
| silverado | **2270.0** | deck header line 28 | AR&R `large_4wd` 2337 |

This pairs each real hull with that real vehicle's own mass, and matches what `rs_sweep_v2`
ran, so the set stays comparable to the existing Rogue/Silverado sweep. Every
`summary.json` carries `mass_alt_kg` and `mass_alt_source`, so both survive regardless.

**The provenance hierarchy is deliberately not inherited.**
`docs/MULTIGEOM_VALIDATION_2026-08-11.md:71` labels 2337 "primary" for the Silverado and
demotes 2270 to `mass_alt_kg`. That inverts the hierarchy: 2270 is the Silverado deck's own
mass, and 2337 is the AR&R `large_4wd` **class** figure, which is not this vehicle's mass.
2337 is a perfectly good number to run. It is not the stronger-provenance one, and it is not
called that here. Note the driver registry at `sim_standing.py:57-65` carries the same
inversion, for a stated reason (class-label consistency with the Yaris runs); passing
`--mass` explicitly is what avoids inheriting it.

## 7. The three arms

Never averaged, and labelled distinctly in every output.

| arm | design | purpose |
|---|---|---|
| **S** | shared `n_grid = 96`, vehicle-specific masses | the confound, kept for continuity with `rs_sweep_v2`. This is the thing being falsified. |
| **M** | matched dx (111/123/154), vehicle-specific masses | **primary** |
| **D** | matched dx, bulk density held equal at 310.494225 kg/m3 | the control that separates geometry from mass |

**Arm D masses**: `rho_ref * hull_m3` with `rho_ref = 1100/3.542739 = 310.494225`, the
canonical Yaris working density, so the Yaris arm is 1100 kg by construction:
yaris 1100.000, rogue 1537.052, silverado 2472.181.

**Labelled assumption, reversible.** Arm D equalises mass over **hull** volume, but the
solver's own density is mass over **solid** volume, the solidified particle cloud
`n_particles * h^3`. `fill_ratio` runs 0.994 to 1.026 across the 17 gated runs, so the
realized densities should agree to roughly ±1.6 percent rather than exactly. The achieved
`realized_rho` is read back from each `summary.json` and reported; it is not assumed. If the
achieved spread turns out larger than the ±1.6 percent expectation, the control is weaker
than intended and that will be stated rather than glossed.

### Arm S turns out to be three repeats of published runs `[live]`

This was not designed in; it fell out of the configurations and is worth stating because
it gives a **cross-job** reproducibility measurement to sit beside the within-job one.
Each arm S run reproduces the exact configuration of an already-published run:

| arm S run | repeats | published values to compare against |
|---|---|---|
| `S_yaris_n96_m1100` | canonical **`g96_m1100`** | `data/all_runs_inventory.csv`: n_grid 96, 6 layers, h 0.0490715745506653, realized depth 0.2944294473039918, depth 0.3, velocity 1.5 |
| `S_rogue_n96_m1571p3` | `rs_rogue_g96`, job 3362208 | SLIDE, ratio_slide 11.557340621948242, peak surge 1.7913575611712371 g, passthrough 0.10716 |
| `S_silverado_n96_m2270` | `rs_silverado_g96`, job 3362208 | SLIDE, ratio_slide 1.810455322265625, onset frame 5, peak surge 0.9814014242512006 g |

The planner's independently predicted Yaris values at `n_grid 96` match the canonical
inventory row exactly, which is a sixth verification anchor on top of the five in section 3.

**This matters for register J16.** `g96_m1100` is one of the six canonical runs whose
frozen margins J16 records as permanently unverifiable, because job 866887 overwrote the
g48/g96 run directories on 2026-07-26. `S_yaris_n96_m1100` is a fresh, independently
produced measurement of that exact configuration, same driver sha256, on LS6. It cannot
restore the lost outputs, and it cannot prove what the original run did, but it does
establish what that configuration produces today, which is strictly more than the register
currently has for it.

**Arm D also carries the no-forcing control.** `D_yaris` is bit-for-bit the same
configuration as `M_yaris` (n_grid 111, 1100 kg), run in the same job, on the same node,
with the same driver. Register item 17 records this stack as **non-deterministic at fixed
configuration**, and `determinism_identical` reported True on six runs that differ, so the
flag is recorded but explicitly not trusted. The `M_yaris` versus `D_yaris` difference is
the run-to-run draw, and **any cross-vehicle difference smaller than it is not a result.**
This is the only way to know whether an ordering is real.

## 8. What matching dx does not fix `[live]`

Stated here so it is not discovered later. The domain edge scales with the hull, so the
three tanks are not the same tank:

| vehicle | free span (m) | water volume (m3) | inflow band to vehicle (m) | hull / water volume |
|---|---|---|---|---|
| yaris | 8.7427 | 22.707 | 3.8135 | 0.15602 |
| rogue | 9.7634 | 28.325 | 4.4259 | 0.17477 |
| silverado | 12.3891 | 45.586 | 6.0013 | 0.17466 |

The inflow band sits at `wall + 1.5 m` with the 1.5 m **fixed in absolute metres**
(`sim_standing.py:155, :223`) while the vehicle sits at `0.60 * lim`, so the upstream fetch
grows with the vehicle: 3.81 m for the Yaris against 6.00 m for the Silverado, a 57 percent
difference. Blockage ratio is close for Rogue and Silverado but 12 percent lower for the
Yaris.

**Matching dx fixes resolution. It does not make these the same experiment**, and no claim
here should be read as if it did. Removing the tank confound would need the domain decoupled
from the hull extent, which is a driver change and is out of scope for this dispatch.

## 9. Not wired, deliberately

`inertia_kg_m2` and `cg_height_m` are **not** wired into the solver, per CLAUDE.md item 4,
and this experiment is exactly where someone would be tempted. The solver already derives a
better tensor from the real hull particle cloud
(`kernels/mpm_solver_warp.py:859-871`); the box tensor overstates every principal moment by
+16.3 to +26.1 percent because the hull fills only 33.2 percent of its own bounding box, and
the documented `(L,W,H)->(x,y,z)` convention is transposed against this scene, which puts the
long axis on y. A naive write gives Ixx -69.2 percent and Iyy +379.2 percent. `[inherited]`

The free result worth reporting instead: the measured cloud CG sits **0.6312 m** above the
floor, below bbox mid-height 0.7427 m, and a too-high CG biases toward topple. The 17 runs
show zero topples, so the no-topple result is **conservative**. `[inherited]`

## 10. Results `[live]`

LS6 job **3364497**, node **c301-004**, partition `gpu-a100-dev`, 9 runs, all rc=0,
**00:06:57** wall. Driver sha256 `4696c3b2…d10d9`, byte-identical to the Mac copy. Full
per-run CSV: `data/three_class_matched_2026-08-14.csv`.

### 10.1 The headline: the Silverado verdict is resolution-dependent

| arm | yaris | rogue | silverado |
|---|---|---|---|
| **S** shared n_grid 96 | SLIDE, margin 15 | SLIDE, margin 41 | **SLIDE, margin 0** |
| **M** matched dx | SLIDE, margin 40 | SLIDE, margin 21 | **STUCK, margin -3** |
| **D** matched dx, equal rho | SLIDE, margin 40 | SLIDE, margin 24 | **STUCK, margin -3** |

**Removing the resolution confound flips the large_4wd verdict from SLIDE to STUCK**, and it
does so in both matched arms independently.

The flip is not a threshold wobble. In arm S the Silverado held the joint SLIDE condition for
exactly **3** frames against the 3 required, a margin of 0, already one frame from STUCK. In
arms M and D its longest joint run is **0 frames**: it never satisfies the condition in any
single frame. `ratio_slide` falls below 1.0 (**0.9365** in M, **0.8397** in D), meaning peak
surge drift never even reaches the 0.05 m threshold. Peak surge acceleration drops from
**0.9814 g** to **0.4339 g**, a 55.8 percent reduction.

### 10.2 How big is the noise floor, measured three ways

This matters more than the flip itself, because register item 17 records this stack as
non-deterministic and a verdict change is only a result if it exceeds the draw.

| comparison | kind | `ratio_slide` difference |
|---|---|---|
| `M_yaris` vs `D_yaris`, identical config, same job and node | within-job | **0.112 %**, margin delta 0 |
| `S_rogue` vs published `rs_rogue_g96` (job 3362208) | cross-job | **0.068 %** |
| `S_yaris` vs `g96_m1100` live re-measurement | cross-job | **0.234 %** |
| `S_silverado` vs published `rs_silverado_g96` (job 3362208) | cross-job | **1.20 %** |

So the reproducibility floor is **at worst about 1.2 percent**. The Silverado's `ratio_slide`
moves **-48.9 percent** between arm S and arm M, roughly **40 times** the floor. The flip is
far outside the noise.

`determinism_identical` reported **True** on every run, including pairs that differ. It is
recorded in the CSV under the column name
`determinism_identical_FLAG_DO_NOT_TRUST` and was not used for anything.

### 10.3 Density is ruled out as the driver `[live]`

Arm D equalises bulk density; arm M does not:

| arm | yaris | rogue | silverado | spread |
|---|---|---|---|---|
| M realized rho | 310.76 | 317.99 | 285.46 | **11.4 %** |
| D realized rho | 310.76 | 311.05 | 310.88 | **0.09 %** |

Collapsing an 11.4 percent density spread to 0.09 percent **changed no verdict and did not
reorder the three**. The equal-density control also landed far better than the ±1.6 percent
the section 7 assumption allowed for: achieved spread 0.09 percent. The assumption held.

### 10.4 What this set can and cannot say about mass versus geometry

The dispatch asks for a plain statement of whether the ordering follows mass or displaced
volume. **The honest answer is that this design cannot separate them, and saying otherwise
would be an overclaim.**

In arm M the three vehicles run 1100 / 1571.3 / 2270 kg against 3.543 / 4.950 / 7.962 m3, and
in arm D they run 1100 / 1537.1 / 2472.2 kg against the same volumes. **Mass and displaced
volume are rank-correlated in every arm that was run**, and in arm D they are proportional by
construction, because holding density fixed forces mass to scale with volume. The observed
ordering, slide propensity falling monotonically as the vehicle gets bigger, is equally
consistent with a mass-only account and a geometry-aware one.

What the set does establish:

1. The ordering is **monotone and large**: margin 40 / 21 / -3 in M and 40 / 24 / -3 in D.
2. The ordering is **not a density artifact** (10.3).
3. Within a fixed hull, more mass means less slide, in the expected direction, since Coulomb
   friction scales with weight while the hydrodynamic driving force does not:
   - rogue, mass -2.18 % (1571.3 to 1537.1), `ratio_slide` **+6.17 %**
   - silverado, mass +8.91 % (2270 to 2472.2), `ratio_slide` **-10.34 %**

**The arm that would settle it was not run**, and should be: a *mass swap* that breaks the
rank correlation, for example the Yaris hull at the Silverado's mass and the Silverado hull at
the Yaris's mass. Under a mass-only account the ordering follows the swapped masses; under a
geometry-aware account it does not. That is one additional three-run arm on the existing
matched grid and needs no new machinery. Until it exists, the A-3 geometry claim is
**untested here**, not supported here.

### 10.5 Arm S's ordering was substantially a depth artifact `[live]`

Worth stating because it is the cleanest illustration of why the confound matters. The arm S
realized depths were **yaris 0.294429, rogue 0.326329, silverado 0.272249**. The Rogue sat in
**9.0 percent deeper** water than the Yaris and the Silverado in **9.1 percent shallower**,
purely as a side effect of `n_grid` being shared. Deeper water means more submerged area and
more drag.

That is exactly the direction of arm S's ordering, in which the Rogue slid hardest of the
three (margin 41) and the Silverado barely slid (margin 0). At matched depth the Rogue's
margin falls to 21 and the ordering becomes monotone in size. **An analysis run only on arm S
would have concluded that the midsize SUV is the least stable of the three classes, and that
conclusion would have been an artifact of cell size.**

### 10.6 Refinement does not move the three the same way

| vehicle | dx change S to M | `ratio_slide` change |
|---|---|---|
| yaris | -13.5 % | **+108.4 %** |
| rogue | -21.9 % | **-47.6 %** |
| silverado | -37.7 % | **-48.9 %** |

The Yaris slides **more** under refinement while the other two slide **less**. This is a sign
reversal, not a spread. It is consistent with CLAUDE.md L-5 and Steffen, Kirby and Berzins
2008, the citable mechanism for MPM losing convergence under grid refinement at fixed
particles-per-cell, and PPC is constant at 8 throughout this stack, exactly that paper's case.
Note the arm S to arm M step changes realized depth as well as dx for every vehicle, so this
column is **not** a clean refinement study and must not be quoted as one; it is a statement
that the two arms disagree, not a measurement of a convergence rate.

### 10.7 A containment failure that qualifies the headline `[live]`

**Seven of the nine runs fail gate P-2**, maximum water fraction inside the vehicle bounding
box, limit 0.10:

| run | passthrough | P-2 |
|---|---|---|
| `S_yaris_n96_m1100` | 0.09695 | pass |
| `S_rogue_n96_m1571p3` | 0.10720 | **fail** |
| `S_silverado_n96_m2270` | 0.09041 | pass |
| `M_yaris_n111_m1100` | 0.10892 | **fail** |
| `M_rogue_n123_m1571p3` | 0.10043 | **fail** |
| `M_silverado_n154_m2270` | 0.10318 | **fail** |
| `D_yaris_n111_m1100` | 0.10890 | **fail** |
| `D_rogue_n123_m1537p1` | 0.10073 | **fail** |
| `D_silverado_n154_m2472p2` | 0.10145 | **fail** |

**All six matched-dx runs fail.** This must be stated with the headline, not buried: **the
Silverado flip runs from a P-2-passing coarse run to a P-2-failing fine run.** That is a real
qualification on the flip and it is not resolved here.

Three things bound how much it undermines the result, none of which dismiss it:

- The failures are **marginal**, 0.4 to 8.9 percent over a 0.10 limit, against the 21 to 31
  percent passthrough already recorded on gated g64 runs `[inherited]`.
- Passthrough **rises with refinement** across this set, which reproduces the same behaviour
  independently reported for `canon_g128_m1100` at 0.11159 `[inherited]`. It is a property of
  the finer grids, not of the Silverado specifically.
- P-2 is a containment tripwire, not physics. See the gate limitation in section 11.

`C3_oob_particle_frames` is **0** on all nine runs and `C2_veh_zmin_rise` is 0.000 on all
matched-dx runs, so no hull sank into or escaped the domain. The failure mode is water
entering the bounding box, not the vehicle leaving it.

### 10.8 A by-product: register J16's `g96_m1100` margin is now corroborated `[live]`

`S_yaris_n96_m1100` is a fresh, independent reproduction of canonical `g96_m1100`, whose
frozen margin J16 records as permanently unverifiable after job 866887 overwrote the g48/g96
run directories on 2026-07-26.

| quantity | frozen store | live re-measurement | **this run** |
|---|---|---|---|
| mode | SLIDE | SLIDE | **SLIDE** |
| `longest_joint_frames` | - | 18 | **18** |
| `margin_frames` | - | 15 | **15** |
| `k_crit` | - | 0.25639185 | **0.25670946** |
| `ratio_slide` | 5.385389 | 5.405998 | **5.418644** |

Margin and longest-joint-run reproduce **exactly**; `k_crit` agrees to 0.12 percent and
`ratio_slide` sits 0.62 percent above the frozen value and 0.23 percent above the live
re-measurement. Both gaps are **inside the 1.2 percent cross-job reproducibility floor
measured in 10.2**, so the frozen 15-frame margin is consistent with an ordinary run-to-run
draw rather than with a corrupted or mis-attributed run.

Stated with its limits: this **cannot** restore the overwritten outputs and **cannot** prove
what the original run did. It establishes that the configuration reproduces its published
margin today, on a different machine and date, at the same driver sha256. That is strictly
more than the register currently has for `g96_m1100`, and it is one of the six, not all six.

### 10.9 Achieved control, versus intended

| arm | dx spread | realized-depth spread |
|---|---|---|
| S | 38.6997 % | 19.8644 % |
| M | **0.0494 %** | **0.0494 %** |
| D | **0.0494 %** | **0.0494 %** |

The matched arms achieved exactly what section 3 predicted, and the predicted `grid_lim`,
`dx`, layer count and pre-carve water count all reproduced in the run logs, for example the
Silverado at `lim=13.067933` against a predicted 13.06793299 and `dx=0.084857` against a
predicted 0.0848567.

## 11. Standing limitations

- `depth/dx = 3.5` and 7 particle layers is better than the canonical g64 baseline's
  `depth/dx = 2.000` and 4 layers, but still well short of the roughly 10 particles per flow
  depth rule of thumb. **A limitation, never a converged resolution.** `[inherited]`
- No gate is a physics validation. Every gate is a self-consistency or numerical-containment check; G-3 compares against a constant derived from the same pipeline, and G-6/P-4/P-5 have no pass criterion at all. (CLAUDE.md item 6.) The P-2 passthrough limit reported per run is therefore a containment tripwire, not evidence that the physics is right. `[inherited]`
- Steffen, Kirby and Berzins 2008 is the citable mechanism for MPM losing convergence under
  refinement at fixed particles-per-cell. PPC is constant at 8 in this stack, exactly that
  paper's case, so refinement here is not guaranteed to converge and a non-monotone result
  would be expected rather than anomalous. `[inherited]`
- The AR&R and Shand thresholds describe a **stationary** vehicle in flow, which is what this
  setup is, so this is not a scenario mismatch. `[inherited]`
- Coarse resolution usually **over**-predicts peak hydrodynamic force, so over-threshold
  NO-FORD verdicts are conservative. `[inherited]`
- Smith/Modra/Felder 2019 and Arrighi 2015 already appear in the register in adjacent
  contexts, so they are **not** independent support for the geometry framing.
  Martinez-Gomariz 2017 and Allen 2003 (SAE 2003-01-0966) are the new ones, and Allen is
  self-flagged provisional, citable as method and not as validation. `[inherited]`
- **No claim in this document has been through the physics-skeptic subagent yet.** The
  numerical results in sections 2, 3 and 8 are reproducible by running
  `analysis/three_class_matched_grid.py`, which self-verifies against five external anchors,
  but the interpretation is unreviewed until section 10 is complete.
