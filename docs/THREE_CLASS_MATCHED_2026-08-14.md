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
| yaris | 111 | 0.0848806 | 0.297082 | 7 | 3.500 | **291,245** |
| rogue | 123 | 0.0848987 | 0.297145 | 7 | 3.500 | **362,440** |
| silverado | 154 | 0.0848567 | 0.296998 | 7 | 3.500 | **590,422** |

`n_water` above is **measured from the run summaries**, not predicted. The planner's
`axis_count()` applies `ceil` to a quantity that is analytically the exact integer
`2*n_grid - 17`, so it flips by one grid line on last-bit noise and **mispredicts pre-carve
water count in 6 of 9 checkable runs**. `dx`, `grid_lim` and `water_layers` reproduce 9 of 9,
so the matched-dx design is unaffected, but no predicted particle count should be quoted.

**dx spread 0.0494 percent, realized-depth spread 0.0494 percent**: a factor of about **780**
reduction in the dx confound and about **402** in the realized-depth confound (one factor must
not be quoted for both), at 7 water layers and `depth/dx` exactly 3.500 for all three.

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

**The two retracted digests, named here in full so the guard can never be rebuilt from a
filename list again:**

| sha256 | hull | known aliases on disk |
|---|---|---|
| `5ef646213e00c86357a6b5c983fbd7b60fe40c0c93af93e0c260de4c2b924006` | rogue pd6, 2.597364 m3, **47.53 %** below converged | `candidates/rogue_candidate_euler-32.ply`, `rogue_g96_pd6_coarse_watertight.ply` |
| `c9c58ca7b931d09dc6291280b08695a5eac87cad4283b8cd2a3bb66121759ba1` | silverado g32 dq0.02, 5.462160 m3, **31.40 %** below converged, 2108 verts / 4380 faces | `candidates/silverado_candidate_euler-82.ply`, `silverado_g32_pd8_dq0.02_coarse_watertight.ply` |

**RESOLVED, without touching the driver.** `analysis/preflight_hull_guard.py` is a standalone
content-based checker: it hashes every `.ply` in a pool and refuses any digest in the
retracted set regardless of filename. It runs BEFORE the driver, changes no stamped sha256
and touches no shared file. Verified on the live pool: it catches **all four** reachable
copies (both `candidates/` names and both pool aliases) and exits 1, passes the three
approved hulls and exits 0, and exits 1 on `rogue_g96_pd6_coarse_watertight.ply` alone, which
is precisely the case the driver's filename guard misses.

**Handed to D4** as a register entry: the in-driver sha256 fix above should be applied only
once the matched-dx set is final, because applying it changes the driver sha256 that stamps
every run in this document.

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

### 6.1 Independent NHTSA grounding, and where it says I chose wrong `[inherited]`

A live NHTSA Canadian Vehicle Specifications pull, delivered 2026-08-14, grounds all three
masses against real published trims:

| figure used | NHTSA reality | verdict |
|---|---|---|
| Rogue **1609** (AR&R class) | AWD **1610**, FWD 1550 | matches the AWD trim almost exactly, **well grounded** |
| Rogue **1571.3** (what arms S and M used) | falls **between** FWD and AWD | **pins to no published trim, provenance still open** |
| Silverado **2337** (AR&R class) | range **2020 to 2440** across trims | plausible, inside the real range, no single-trim match, expected given dozens of trims |
| Yaris **1078** (NCAC page) | **1043 to 1071** across trims | deck figure is **0.6 to 3.4 percent above** the top of the real range |
| Yaris **1100** (what every run here used) | same range | **further out still**, and it is the canonical figure the 17 gated runs use |

**Recording this against my own choice rather than around it: arms S and M used 1571.3, and
on grounding 1609 is the better number.** The reason for 1571.3 was pairing each hull with
that vehicle's own figure plus continuity with `rs_sweep_v2`; that is a defensible reason for
comparability and a weak one for provenance, and the NHTSA pull makes the trade explicit.
1609 matches a real trim, 1571.3 matches none.

**This is measured rather than argued.** Arm D already ran the Rogue at 1537.052 kg and arm X
(section 10.12) adds 1609 kg at identical geometry and resolution, so the Rogue is measured at
**three** masses spanning 1537.052 to 1609, a 4.7 percent range that brackets both candidate
figures. Whether the choice mattered is therefore a reported number, not a judgement call.

The Yaris row deserves noting even though nothing here can act on it: **the canonical 1100 kg
is above the top of the real trim range**, and it is not this dispatch's to change, since it
is `vehicle_params.py mass_kg` and the basis of all 17 gated runs.

### 6.2 Why 2337 kg attaches to both the Silverado and the Ram 1500 `[inherited]`

A standing ambiguity, now resolved with a mechanism rather than left as a coincidence.
2337 kg appears against **both** the 2007 Silverado and the 2018 Ram 1500 in different project
documents. **That is not an error.** Both are **MASH-2270P class pickups, engineered to the
same nominal test weight by design**; the 2018 Ram 1500 Crew Cab 5.7 ft Box 4x4 is 2336 kg, a
near-exact match.

So the register's existing rule, that **Silverado geometry is not Ram 1500 geometry and the
two must not be conflated**, is correct and now has a documented reason: the shared number is a
*class test weight*, not a shared vehicle. This converts a confusing coincidence into a citable
class definition, and it reinforces rather than weakens the section 6 point that 2337 is a
class figure and 2270 is this vehicle's deck mass.

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
| **D** | matched dx, bulk density held equal at 310.494225 kg/m3 | rules **density** out. It does NOT separate geometry from mass, see 10.4 |

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
with the same driver. The non-determinism at fixed configuration, and the fact that
`determinism_identical` reported True on six runs that differ, are recorded in **register
item 17, which exists ONLY on branch `claude/rtfd-test-phase-1-4-569130`**. Main's register
ends Section J at item 16, verified live, so "register item 17" is a dangling citation in
any checkout of main and must be qualified with its branch. The flag is recorded but not
trusted. The `M_yaris` versus `D_yaris` difference is
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
difference. Blockage ratio is close for Rogue and Silverado but **10.73 percent** lower for the Yaris.

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

### 10.1 The headline: a shared `n_grid` was masking a class-dependent verdict

**State the finding this way round.** It is *not* "the Silverado is STUCK". That is one
verdict from one companion set that fails a containment gate (10.7). The finding is that
**a shared `n_grid` was masking a class-dependent verdict, and the confound it introduced
was 38.7 percent in resolution.** The Silverado flip is the evidence for that, not the
claim itself.

The consequence is general rather than about one truck: **every prior cross-vehicle
statement made at a shared `n_grid` is suspect for the same reason**, whichever direction
it happened to fall. Section 10.10 names the specific ones.

| arm | mu | yaris | rogue | silverado |
|---|---|---|---|---|
| **S** shared n_grid 96 | 0.55 | SLIDE, margin 15 | SLIDE, margin 41 | **SLIDE, margin 0** |
| **M** matched dx | 0.55 | SLIDE, margin 40 | SLIDE, margin 21 | **STUCK, margin -3** |
| **D** matched dx, equal rho | 0.55 | SLIDE, margin 40 | SLIDE, margin 24 | **STUCK, margin -3** |
| **MU** matched dx | **0.30** | SLIDE, margin 45 | not run | **SLIDE, margin 11** |

**Every verdict row carries its `mu`, and that is not decoration.** Section 10.14 shows the
large_4wd STUCK verdict needs `mu` at or above roughly 0.40, so an unlabelled verdict in this
table would invite exactly the misreading retracted below. `mu = 0.55` is the project
canonical value and is Azhar, Pauwels and Bui (2023)'s own spring-balance measurement of a
laboratory rubber mat, citing Wong, *Theory of Ground Vehicles*. **DOI
`10.1111/jfr3.12885`**, and note it is **an SPH paper**, not MPM: the coefficient is imported
across both a method boundary and a contact-model boundary. See the guard in 10.14.

**RETRACTED 2026-08-14, same day, on review.** This subsection previously read "removing the
resolution confound flips the large_4wd verdict". That causal attribution is **false** and is
withdrawn. Register J item 15 (register line 625) already published this exact flip, same
vehicle and same 2270 kg mass, from plain shared-`n_grid` refinement on 2026-08-13:
*"puts Silverado at SLIDE at g64 and g96 and STUCK at g128"*. The Silverado ladder is
`dx` 0.204186 (g64) SLIDE, 0.136124 (g96) SLIDE at margin 0, 0.102093 (g128) **STUCK**, and
this work's matched arm sits at 0.084857, which is 16.9 percent **finer than the g128 where
the flip was already known to occur**.

**Corrected claim: refining dx below about 0.10 m flips the large_4wd verdict, reproducing
register J15 at a finer dx. Matching dx is what makes the three vehicles COMPARABLE; it is
not what produced the flip.** The confound measurement in section 2 stands on its own and is
unaffected.

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
| `S_silverado` vs published `rs_silverado_g96` (job 3362208) | cross-job | **1.21 %** |

**CORRECTED.** The "roughly 40 times the floor" comparison previously here was the wrong
quantity: it set a between-configuration change against a within-configuration draw. A floor
on `ratio_slide` does not bound a **verdict** flip. The right number is already a column in
the shipped CSV and was not being quoted: `headroom_x`. The arm S SLIDE endpoint survives
only a **4.28 percent** weakening of the surge response (`k_crit` 0.957236,
`headroom_x` 1.0447), against a measured cross-job draw on that exact configuration of
**1.21 percent**. **The safety factor is about 3.5, not 40.**

The floor itself is also undersampled: four single differences at four configurations, only
one at matched-dx resolution. Two later additions fix the worst of that. `F_silverado_n154_m2270_rep`
is a direct repeat of the flip cell, which previously had **none**: it reproduces STUCK at
margin -3 with `k_crit` 2.9596 against 2.7840, a **6.3 percent** draw, which is the number to
quote for that cell rather than 0.112 percent. Three further same-config pairs already existed
in-repo and were not used: `data/g128_canonical_2026-08-13` against `data/g128_canonical_repeat`
give 0.344, 0.017 and 0.922 percent, independently corroborating a roughly 1 percent scale.

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
3. Within a fixed hull, more mass means less slide. **CORRECTED mechanism:** this previously
   read "since Coulomb friction scales with weight". The solver does not work that way.
   `kernels/mpm_solver_warp.py:960-977` forms `J_t = min(v_t/denom_t, mu*J_n)` and applies
   `dv = J_t/M`, with **no weight term anywhere**; the mass channel is
   `vehicle_density = vehicle_mass / solid_volume` (`sim_standing.py:171`) feeding the
   mass-weighted grid velocity average. The observed direction is real, the stated reason was
   not:
   - rogue, mass -2.18 % (1571.3 to 1537.1), `ratio_slide` **+6.17 %**
   - silverado, mass +8.91 % (2270 to 2472.2), `ratio_slide` **-10.34 %**

**The arm that settles it is arm X**, run inside LS6 allocation 3364572, see section 10.11. It is a
*mass swap* that breaks the rank correlation, and together with two runs already in hand it
completes a 2x2 factorial in (hull, mass) at matched dx:

|  | mass 1100 kg | mass 2270 kg |
|---|---|---|
| **Yaris hull** 3.542739 m3 | `M_yaris_n111_m1100` **SLIDE, margin 40** | `X_yaris_n111_m2270` *(arm X)* |
| **Silverado hull** 7.962083 m3 | `X_silverado_n154_m1100` *(arm X)* | `M_silverado_n154_m2270` **STUCK, margin -3** |

Columns give the main effect of geometry at fixed mass, rows the main effect of mass at fixed
geometry, and the diagonal the interaction. Predictions were written into
`scripts/run_three_class_massswap.sh` **before** the runs, so they cannot be fitted afterwards.

One entanglement must be stated or the 2x2 will be over-read: at fixed hull volume, changing
mass changes bulk density, and density sets buoyancy, which sets the normal force, which sets
Coulomb friction. "Mass" in this square therefore means **mass and density together**, and the
square cannot separate those two from each other. It **can** separate them jointly from
geometry, which is the open question.

**Until arm X reports, the A-3 geometry claim is untested here, not supported here.**

### 10.5 Arm S's ordering was substantially a depth artifact `[live]`

Worth stating because it is the cleanest illustration of why the confound matters. The arm S
realized depths were **yaris 0.294429, rogue 0.326329, silverado 0.272249**. The Rogue sat in
**10.83 percent deeper** water than the Yaris and the Silverado **7.53 percent shallower**
(both measured against the Yaris; the "9.0 / 9.1" printed here earlier reproduced under no
convention checked and is withdrawn),
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
| rogue | -22.0 % | **-47.6 %** |
| silverado | -37.7 % | **-48.9 %** |

The Yaris slides **more** under refinement while the other two slide **less**. This is a sign
reversal, not a spread. It is consistent with CLAUDE.md L-5 and **Steffen, Wallstedt, Guilkey,
Kirby and Berzins 2008, DOI `10.3970/CMES.2008.031.107`**, the citable mechanism for MPM losing
convergence under grid refinement at fixed particles-per-cell; PPC is constant at 8 throughout
this stack, exactly that paper's case.

**POSITIONING, now that the catalog has been read.** Steffen 2008 is catalogued as entry #4 of
the multi-resolution report and the report calls it **decisive for AMR**. D9 then co-refined PPC
directly and refuted it as the mechanism *in this scene*. **So this project holds a result the
catalog does not: the PPC trap is real in general and is not what bites here.** That is a
reportable negative, and it is stronger than either the citation or the refutation alone.

**QUALIFIED 2026-08-14 by D9's direct test, which this document must not ignore.** D9 ran the
PPC co-refinement experiment and reports **PPC REFUTED as the mechanism** for the non-monotone
convergence in its scene, with SDF **band width dominant** and `COLLIDER_FRICTION 0.4`
influential instead. So the fixed-PPC reading below is **a candidate mechanism, not an
established one**, and this document does not assert it.

How far that transfers, stated precisely rather than waved through. D9's scene is the **SDF
collider** path, driven; this one is the **material-8 free-rigid** path, stationary, and it
calls no `add_sdf_collider`, so **band width does not exist in this scene and cannot be the
mechanism here**. What does transfer is the refutation itself: PPC is fixed at 8 in both, and a
direct test found it not to be the cause in the sibling scene. This document never claimed a
convergence rate, and 10.6 already states its S-to-M step is not a clean refinement study, so
nothing downstream rests on the mechanism being PPC.

**Cite it under the label D12 assigned it: TRANSFERABLE NUMERICAL ANALYSIS, NOT WATER
VALIDATION.** The paper analyses MPM quadrature error under refinement; it does not validate a
free-surface water result, and it must not be presented as support for the physics being right
here. It supports only the expectation that refinement at fixed PPC need not converge
monotonically, which is what section 10.6 observes.
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

- The failures are **marginal**, 0.4 to 8.9 percent over a 0.10 limit. **RETRACTED:** this
  bullet previously compared them against "21 to 31 percent passthrough already recorded on
  gated g64 runs". That figure is a **Genesis** measurement on an axis-aligned box vehicle
  (`.claude/memory/gd64-runs-have-heavy-particle-passthrough.md`), not warpmpm, and quoting it
  here broke this document's own engine tag and inflated the reassurance about threefold. The
  correct warpmpm comparators are the gated g64 runs at **0.07344 to 0.10670**
  (`data/all_runs_inventory.csv`), which straddle the same limit.
- **RETRACTED: "passthrough rises with refinement" is false**, and it is contradicted by this
  document's own CSV. `S_rogue` 0.10720 falls to `M_rogue` 0.10043, a 6.3 percent **drop**. The
  published sweep falls too (`rs_rogue_g96` 0.107165 to `rs_rogue_g128` 0.098764), as does the
  canonical Yaris series (g64 0.10670 to g96 0.09694), and register J15 states it outright:
  *"Passthrough does not explain it: Rogue's passthrough is flat, 9.95 -> 9.88 percent."*
- **P-2 is not commensurable across vehicles**, which is not previously recorded anywhere. The
  gate divides water particles inside the vehicle AABB by ALL water particles, and both terms
  are vehicle- and tank-dependent. The purely geometric baseline, bbox plan area over free-span
  plan area, is already 0.0905 to 0.1041 across these nine runs, so **the fixed 0.10 limit sits
  inside the baseline spread** and the exceedances are the same size as that spread.
- P-2 is a containment tripwire, not physics. See the gate limitation in section 11.

`C3_oob_particle_frames` is **0** on all nine runs and `C2_veh_zmin_rise` is 0.000 on all
six matched-dx runs. **CORRECTED:** the sentence "no hull sank into or escaped the domain"
was wrong. `S_rogue_n96_m1571p3` has `C2_veh_zmin_rise` **-0.012955 m**, which fails gate P-3
(`gates.py:150-151`, limit 0.01 m): that hull settled downward. It is an arm S run, and it is
one of the runs section 10.5's depth argument leans on, so the correction is recorded rather
than buried. For the matched-dx runs the statement holds: the failure mode there is water
entering the bounding box, not the vehicle leaving the domain.

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

**CORRECTED, twice.** First: **there is no frozen margin.**
`data/failure_modes_by_run_classified.csv` has no `margin_frames` or `longest_joint_frames`
column, which is why the table above prints "-" for it. J16 records the frozen **`ratio_slide`**
values as unreproducible, not the margins, so nothing frozen is corroborated by reproducing a
margin. Second: the "live re-measurement" is itself a measurement of **job 866887's overwrite**
(`analysis/slide_verdict_fragility.py:31-42`), not of the canonical run, so 18/15 agreeing is
agreement between two non-canonical runs.

A third same-config run also exists in-repo and was not cited:
`data/g128_canonical_repeat/canon_g96_m1100` returns `ratio_slide` 5.413961, joint 18,
margin 15, `k_crit` 0.256678. Including the frozen value the four-run spread is **0.62 percent**,
not the 0.234 percent quoted above, which was the closest available comparator.

**Defensible restatement:** the `g96_m1100` configuration returns margin 15 / joint 18 in three
independent runs spanning 0.62 percent in `ratio_slide`. That is a reproducible configuration.
It is not corroboration of a frozen margin, because the frozen store contains no margin.

Stated with its limits: this **cannot** restore the overwritten outputs and **cannot** prove
what the original run did. It establishes that the configuration reproduces its published
margin today, on a different machine and date, at the same driver sha256. That is strictly
more than the register currently has for `g96_m1100`, and it is one of the six, not all six.

### 10.9 Does the flip survive excluding the J16-affected run? Yes, entirely `[live]`

A reviewer will ask, because `S_yaris_n96_m1100` reproduces `g96_m1100`, one of the six runs
register J16 flags. Answer, with the data already in hand:

**The flip does not involve that run at all.** The flip is `S_silverado_n96_m2270` (SLIDE)
against `M_silverado_n154_m2270` and `D_silverado_n154_m2472p2` (both STUCK). Drop
`S_yaris_n96_m1100` and all three of those runs, and the flip, remain untouched.

Everything else it contributes also survives its removal:

| claim | does it depend on `S_yaris`? |
|---|---|
| the flip (10.1) | **no**, three other runs |
| noise floor (10.2) | **no**. Worst-case 1.20 % comes from `S_silverado`, not `S_yaris`; the within-job 0.112 % comes from the `M_yaris`/`D_yaris` pair |
| density ruled out (10.3) | **no**, arms M and D only |
| mass/volume not separated (10.4) | **no**, arms M and D only |
| arm S depth artifact (10.5) | **weakened, not lost**. The Rogue-versus-Silverado depth spread (0.326329 against 0.272249, 19.9 %) carries the argument on its own |
| J16 corroboration (10.8) | **yes**, entirely. That subsection *is* the `S_yaris` result and stands or falls alone |

So 10.8 is the only claim in this document that depends on the J16-affected configuration,
and it is a claim *about* J16 rather than one resting on it.

### 10.10 Prior claims this puts in question, named `[live]`

Correcting these is **not this dispatch's to do**. Naming them is, because the confound is
generic and silent.

1. **`docs/MULTIGEOM_VALIDATION_2026-08-11.md`.** Its cross-vehicle rows are at a shared
   `n_grid`, so any comparison of Yaris against Rogue against Silverado in it is comparing
   different cell sizes and different realized depths. The specific hazard is its
   `class_rogue_g64` row and the g64 cross-vehicle framing around it: at shared `n_grid` the
   Rogue sits in the deepest water of the three, which biases it toward sliding. Its Silverado
   mass-provenance inversion is separately flagged in section 6.
2. **`data/rogue_silverado_grid_sweep_2026-08-13.csv` and
   `data/rogue_silverado_slide_classification_2026-08-13.csv`.** Within one vehicle these are
   clean refinement ladders and remain usable as such. What is not safe is reading a
   Rogue row against a Silverado row at the same `n_grid` as a like-for-like class comparison:
   at `n_grid` 96 those two runs differ by 25.1 percent in dx and 19.9 percent in realized
   depth.
3. **The Silverado SLIDE-to-STUCK-at-g128 result** recorded in register J15 and quoted as
   `ratio_slide` 6.9669 to 1.8105 to 1.5557. This work does **not** contradict it, and at
   n_grid 96 it reproduces its value to 1.20 percent. But that ladder is a single-vehicle
   refinement study, so it should not be paired with a Yaris ladder at matching `n_grid`
   labels and read as a class comparison, because equal `n_grid` is not equal resolution.
4. **Any figure or caption that labels a cross-vehicle panel with a shared `n_grid`**, for
   example "all three at g96", as though that were a controlled condition. It is not, and the
   correct label is the achieved dx and realized depth per panel.

The general rule this set supports: **`n_grid` is not a physical condition in this scene, it
is a divisor.** Report dx and realized depth, and never let `n_grid` stand in for either.

### 10.11 Arm X, the mass swap: submitted, not yet reported

**Ran inside LS6 allocation 3364572** via `srun --overlap` (batch job 3364582 never started), three runs at the same matched-dx grid (n_grid 111 / 123 /
154), same `--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55`:

| run | purpose | realized rho at hull basis |
|---|---|---|
| `X_yaris_n111_m2270` | Silverado deck mass on the Yaris hull, completes the 2x2 | 640.75 |
| `X_silverado_n154_m1100` | Yaris mass on the Silverado hull, completes the 2x2 | 138.16 |
| `X_rogue_n123_m1609` | the NHTSA-grounded Rogue figure, see 6.1 | 325.03 |

Both swap cells sit at densities well outside the canonical band, and the Silverado arm at
138.15 kg/m3 is far more buoyant than anything in the gated set, so **FLOAT is a plausible and
legitimate outcome there**, not a failed run.

**STATUS CORRECTED, this subsection was stale and contradicted 10.13.** Batch job **3364582
never ran**; it stayed blocked on `QOSMaxJobsPerUserLimit` behind interactive session
`3364572`. **Arm X was instead run inside allocation 3364572 via `srun --overlap`, which is why
every arm X row stamps `job_id=3364572` and not 3364582.** That id is correct and is not a
mis-stamp. This dispatch did not allocate that idev; it ran a step inside an allocation that
already existed. The heading figure 3364582 above is the id of the job that never executed.
Results are in 10.4 and 10.13.

The pre-registered prediction that `X_silverado` might reach FLOAT **did not occur**: it
returned SLIDE at margin 17. Recorded because it was written before the run.

### 10.13 The balanced 3x3 is NON-MONOTONE in displaced volume `[live]`

Arm F completed a balanced 3 hulls x 3 masses factorial at matched dx. `margin_frames`:

| hull | 1100 kg | 1609 kg | 2270 kg |
|---|---|---|---|
| yaris 3.5427 m3 | 40 | 13 | 3 |
| rogue 4.9503 m3 | **46** | **19** | **5** |
| silverado 7.9621 m3 | 17 | 0 | **-3 (STUCK)** |

**At every one of the three masses the Rogue slides MORE than the Yaris**, despite carrying
1.40x the displaced volume, while the Silverado slides far less than both.

**This retracts the reading that the ordering follows displaced volume.** Section 10.4's 2x2
appeared monotone only because it sampled the smallest and largest hulls and omitted the
middle one. Ordering is monotone in **mass within every hull** and **not monotone in displaced
volume across hulls**. That is consistent with CLAUDE.md A-3's actual claim, which is that
thresholds depend on underbody shape, wheelbase, track and CoM and not on mass alone; it is
**not** support for displaced volume as a scalar predictor. The cross-hull comparison also
remains confounded with tank scaling (section 8), so no cross-hull number here is a clean
geometry effect.

### 10.14 The verdict is friction-dependent, and needs mu >= about 0.40 `[live]`

Silverado, n154, 2270 kg, matched dx, everything else held fixed:

| mu | verdict | margin | k_crit | source of the value |
|---|---|---|---|---|
| **0.30** | **SLIDE** | +11 | 0.4764 | Bonham & Hattersley 1967, *Low Level Causeways*; Gordon & Stone 1973; Keller & Mitsch 1993; Shand et al. 2011, which underpins AR&R. **All ADOPT or ASSUME 0.3; none measured it** |
| 0.40 | STUCK | -1 | **1.0027** | on the boundary |
| 0.45 | STUCK | -3 | 1.4886 | |
| 0.50 | STUCK | -3 | 2.1675 | |
| **0.55** | STUCK | -3 | 2.7840 | **canonical**, Azhar, Pauwels & Bui 2023, `10.1111/jfr3.12885`, **SPH** |
| 0.78 | STUCK | -3 | 4.3928 | WRL TR 2017/07, top of measured range |

`k_crit` crosses 1.0 at **mu ~ 0.40**. Control confirms the direction: Yaris at mu 0.30 gives
margin 45 against 40 at 0.55.

**Why this matters more than a sensitivity check.** The canonical `floor_friction = 0.55` is a
genuinely MEASURED value, but of a **laboratory rubber mat used as a road-surface proxy**,
measured with a spring balance (Azhar, Pauwels & Bui 2023), cross-checked against Wong's
wet-asphalt band 0.50-0.70 and terminating in SAE 690214 (Harned, Johnston & Scharpf 1969), a
1969 General Motors tyre brake-force study: real, but general-automotive, neither flood nor
submerged. The flood-vehicle-stability field overwhelmingly uses **0.3**, and Shand et al.
state verbatim: *"While the assumed coefficient of friction of mu = 0.3 is likely conservative,
the present lack of suitable data and wide range of road surfaces and tyre tread conditions
prohibits the refinement of the coefficient."* Azhar's own paper notes it "could drop to as low
as 0.30 in case of poor road conditions."

**A higher mu makes a NO-SLIDE verdict EASIER to reach, so the canonical value points in the
direction that favours this document's headline, and at the field convention the headline
reverses.**

### 10.15 STUCK occupies exactly one corner of the (dx, mu) square `[live]`

| Silverado, 2270 kg | mu 0.30 | mu 0.55 |
|---|---|---|
| n96, dx 0.1361 | SLIDE, margin 10 | SLIDE, margin 0 |
| n154, dx 0.0849 | SLIDE, margin 11 | **STUCK, margin -3** |

Two results, and the second is new.

1. **Both conditions are necessary.** Neither a fine grid alone nor a high friction coefficient
   alone produces STUCK. The verdict is **jointly contingent** on dx and mu, which is a weaker
   and more accurate statement than either "resolution-dependent" or "friction-dependent".
2. **The resolution-dependence is itself friction-dependent.** At mu 0.30 a 37 percent dx
   refinement moves the margin only 10 -> 11 frames, so the verdict is robustly SLIDE at both
   resolutions. The entire resolution sensitivity of this verdict lives at the high-mu end.
   That is an **interaction**, not two independent main effects, and it means a
   grid-convergence statement made at mu 0.55 does not transfer to mu 0.30.

Bearing on register J15, which reports the Silverado SLIDE-to-STUCK flip under refinement at
the canonical mu: that flip is reproduced here and is **not** contradicted, but it is shown to
be **conditional on the friction value**. J15's finding should carry its mu.

Note that the one corner with clean containment is a SLIDE corner: the coarse mu 0.30 run
passes P-2 at 0.09046, while every matched-dx run fails it.

### 10.16 L1 against L2 at matched conditions: agreement is class-dependent AND mu-dependent `[live]`

The dispatch flagged `l1-l2-divergence-is-class-dependent` as an open claim these three classes
were the natural test of. At the realized matched-dx conditions, depth 0.2970 m and velocity
1.5 m/s, so D x V = 0.4456 m2/s:

| vehicle | AR&R class | depth cap | D x V limit | **L1 verdict** | **L2 mode** (mu 0.55) | agree? |
|---|---|---|---|---|---|---|
| yaris | small_passenger | 0.30 m | 0.30 m2/s | **NO-FORD** (D x V exceeds) | SLIDE | yes, both unsafe |
| rogue | large_passenger | 0.40 m | 0.45 m2/s | **FORD** (0.96 % under) | SLIDE | **no, diverges** |
| silverado | large_4wd | 0.50 m | 0.60 m2/s | **FORD** | STUCK | yes, both safe |

**CORRECTED. This is convention-dependent, and the convention used above is the one the
project has already recorded as forbidden.** `.claude/memory/l1-l2-divergence-is-class-dependent.md`,
the very note this section set out to answer, states that **AR&R's D is the depth AT THE
VEHICLE, not the upstream slab**, measures D x V at the vehicle as **58.0 to 66.0 percent below
nominal** (Vista job 866266), and concludes that re-running L1 on local values flips
large_passenger to NO-FORD on the DEPTH limit and that **"Then L1 and L2 agree on all three
classes"**. It ends: *"never feed L1 the nominal upstream slab values while calling the result
an L1-vs-L2 comparison."*

The table above does exactly that. The depth is realized; **the 1.5 m/s velocity is nominal**,
a Dirichlet clamp on an upstream slab (CLAUDE.md item 2) that is never realized at the vehicle.

**Defensible restatement:** under the nominal-upstream convention, L1 and L2 agree for
small_passenger and large_4wd and diverge for large_passenger. Under the at-the-vehicle
convention the project itself measured, all three agree. **Neither convention has been applied
to this matched-dx three-hull set**, because the local depth and speed at the vehicle were not
extracted from these runs. That extraction is possible from `rollout.npz`
(`local_depth_bow`, `local_depth_footprint`) and was not done here.

Two further corrections: the Rogue sits **0.9500** percent under its D x V limit, not 0.96
(the 0.96 came from rounding to 0.4457 first). And "precisely the one sitting hard against its
own limit" does not hold: the **Yaris** sits 0.97 percent under its own 0.30 m depth cap and
does **not** diverge, so proximity to a limit does not distinguish the diverging class.

**And the concordance is mu-dependent.** At mu 0.30 the Silverado becomes SLIDE (10.14), so its
agreement flips to divergence and the score drops from 2 of 3 to 1 of 3. The criterion and the
simulation agree best when the simulation uses a friction value the criterion's own authors
declined to adopt. That is worth stating plainly rather than presenting 2-of-3 as the result.

**The AR&R thresholds are DRAFT INTERIM figures, and the class labels are load-bearing.** The
Project 10 Stage 2 report calls its own table draft and interim, and the 0.60 m2/s figure is
specifically the **Large 4WD** class, not a generic 4WD threshold. Quoting "the 0.6 4WD
threshold" without the class is a citation error the project has already had to correct once.

**Unit discipline, because these two are routinely conflated.** AR&R carries BOTH a limiting
D x V product (0.30 / 0.45 / 0.60 m2/s) AND a buoyancy depth cap (0.30 / 0.40 / 0.50 m) per
class. The small-passenger figure is 0.30 in **both**, which is a numerical coincidence and is
exactly why they get merged. Never quote a bare 0.3 without its unit.

### 10.17 Gate P-2 is not commensurable across vehicles. Numbers for D4 `[live]`

**This is stated in the write-up rather than as an aside, because CLAUDE.md item 7 publishes a
seven-run P-2 failure list that may be partly measuring hull geometry.** D4 owns that item; the
numbers and the method are given here so D4 can verify rather than take them on trust.

**Method.** `sim_standing.py` computes `frac` as (water particles inside the vehicle AABB) over
(ALL water particles). Both terms are vehicle- and tank-dependent, so even a perfectly still
tank containing a **zero-volume** hull would register a nonzero fraction equal to the purely
geometric ratio (vehicle bbox plan area) / (free-span plan area), with
`free_span = grid_lim - 2*wall` and `wall = 4*dx` (`sim_standing.py:178`). Bbox plan area uses
the SCENE extents, so `extent[0]` is the raw PLY y and `extent[1]` the raw PLY x.

**Recomputed independently for this document, not carried from the review:**

| run | measured | geometric baseline | **excess** | P-2 |
|---|---|---|---|---|
| `S_rogue_n96_m1571p3` | 0.10720 | 0.10413 | +0.00308 | FAIL |
| `S_silverado_n96_m2270` | 0.09041 | 0.09677 | **-0.00636** | pass |
| `S_yaris_n96_m1100` | 0.09695 | 0.10027 | **-0.00332** | pass |
| `M_rogue_n123_m1571p3` | 0.10043 | 0.10009 | **+0.00034** | FAIL |
| `M_silverado_n154_m2270` | 0.10318 | 0.09047 | **+0.01271** | FAIL |
| `M_yaris_n111_m1100` | 0.10892 | 0.09785 | +0.01107 | FAIL |
| `D_rogue_n123_m1537p1` | 0.10073 | 0.10009 | +0.00064 | FAIL |
| `D_silverado_n154_m2472p2` | 0.10145 | 0.09047 | +0.01098 | FAIL |
| `D_yaris_n111_m1100` | 0.10890 | 0.09785 | +0.01105 | FAIL |

> **RETRACTED IN FULL, 2026-08-14, before D4 acted on it. THE BASELINE FORMULA ABOVE IS THE
> WRONG QUANTITY.** Verified at primary source: `sim_standing.py:463-465` computes
> `lo_v, hi_v = veh.min(0), veh.max(0)` then `((w >= lo_v) & (w <= hi_v)).all(axis=1)`, where
> `veh` is the **solidified particle cloud** and `.all(axis=1)` makes it a **3D** test. My
> baseline used the **mesh** bounding box and a **2D plan-area** ratio. Four independent errors,
> all inflating the baseline: (a) mesh bbox instead of the particle-cloud AABB, which is 4.06 /
> 4.25 / 6.69 percent smaller in plan area; (b) the z-condition binds and excludes 5.4 / 26.8 /
> 15.8 percent of in-plan water; (c) the pre-run carve at `:194-195` is ignored; (d) the
> measured side maxes a **per-frame** AABB over 90 frames, which grows up to 5.30 percent with
> yaw. Measured against the three real g64 rollouts, the formula overstates the true settled
> still-tank fraction by **+32 / +62 / +36 percent**, and the spread of that error is **89
> percent of the entire span of the excess column it was meant to produce**. So the excess
> column does not make P-2 commensurable; it substitutes one vehicle-dependent quantity for
> another.
>
> **Everything derived from it below is withdrawn**, including "the 0.10 limit sits inside the
> baseline spread", "`S_silverado` holds less water than a zero-volume hull would" (every real
> hull does, by construction, since it displaces water), and "`M_rogue` fails with essentially
> no containment signal". Also withdrawn: "No new data is needed."
>
> **CORRECTED RECIPE FOR D4, use this instead.** Do not compute an analytic baseline at all.
> Take each run's own frame-0 fraction from `rollout.npz` (`water[0]` against
> `veh_particles_scene0`) as the settled still-tank floor, and report
> `frac_max / frac_frame0` as the containment ratio. One number per run, no geometry
> assumptions, already on disk for every run. Second best, from `summary.json` alone:
> `(cx*cy*cz - n_carved) / (nx*ny*nz - n_carved)` on the cloud AABB, which removes (b) and (c)
> but still carries (a) and (d).
>
> **What SURVIVES, and it is the part that matters for CLAUDE.md item 7:** P-2's numerator and
> denominator are both vehicle- and tank-dependent, so a bare pass/fail is still not comparable
> across vehicles, and item 7's seven-run failure list still cannot be read as a ranking of
> containment quality. That conclusion never depended on my baseline being right. **The numbers
> did, and they were wrong.**

**The gate's pass/fail does not rank the runs by containment.** `M_rogue` FAILS with an excess
of **+0.00034**, which is essentially no containment signal, while `S_silverado` PASSES with an
excess of **-0.00636**, meaning it holds *less* water in the box than a still tank with a
zero-volume hull would. Ordering by the measured fraction makes `M_yaris` the worst run
(0.10892); ordering by excess makes `M_silverado` the worst (+0.01271). **Those are different
orderings, and only the second is about containment.**

**What this does and does not say.** It does NOT say P-2 is wrong or should be relaxed, and it
does not clear any run: three matched-dx runs carry a genuine excess above +0.011. It says the
threshold is compared against a quantity with a vehicle-dependent floor, so a bare pass/fail is
not comparable between vehicles, and a failure list spanning several vehicles cannot be read as
a ranking of containment quality. The excess column is the comparable quantity.

**Reproduce it** from `data/three_class_matched_2026-08-14.csv` plus the `HULLS` extents and
`scene_extent()` in `analysis/three_class_matched_grid.py`. No new data is needed.

### 10.18 Independent corroboration from a different scene, and what it does not establish

D9 reports the same corner structure on a **completely different** setup: a driven rather than
stationary scene, an SDF-collider coupling path rather than the material-8 free-rigid path, and
`COLLIDER_FRICTION 0.4` rather than the 0.55 floor value. In that scene the failure also lives
in the **under-resolved, low-friction, light-vehicle corner**.

**Stated carefully, because this is easy to overclaim.** Two independent origins agreeing on a
*corner shape* is worth recording: different scene, different coupling, same qualitative
structure. It is **not** a replication of this document's numbers, and none of D9's figures may
be quoted alongside these. The two setups do not share a scene, a coupling path, a friction
value, or a verdict definition, so the agreement is about where the sensitivity lives, not
about magnitude.

**RETRACTED: there is no "fourth friction value".** Verified at primary source:
`kernels/mpm_solver_warp.py:2624` declares `friction=0.4` as the **default argument** of
`add_sdf_collider`. An untouched library default is not a chosen parameter and must not be
tabulated beside 0.55 as though someone picked it. This has already been corrected in two
sibling worktrees and neither correction had reached this one. My list also wrongly included
"roughly 0.40 (where this document's flip boundary sits)", which conflates a **measured
boundary** with an **adopted setting**; and it omitted the 0.2 family, where the floor is 0.2
and the vehicle collider 0.55, the opposite assignment from the gated scene.

**The import crosses TWO boundaries, not one.** Azhar, Pauwels and Bui 2023 is an **SPH**
study (`10.1111/jfr3.12885`, independently confirmed from the moving-rigid-body catalog at #37,
a third source after D11's provenance chain and artifact 65474f37). So 0.55 travels from an SPH
tyre-on-rubber-mat measurement into an MPM whole-underside Coulomb floor contact. The register's
guard covers the contact-model boundary; the method boundary is additional and is recorded here.

Note also what the 0.3 side actually is: **Bonham and Hattersley 1967 is titled *Low Level
Causeways***, so the convention originates in causeway crossings, and per register G4b that
value is **adopted or assumed** by all four sources and **measured by none**.

**GUARD, carried verbatim as the register requires:** *"The AR&R coefficient is tyre-on-road
across four contact patches in an analytical force balance; ours is a Coulomb coefficient in
the MPM floor contact across the whole hull underside. Comparable in direction and magnitude,
**not the same quantity**. No claim may say 0.55 'is' a measured tyre friction."* Section 10.14
compares the two directly and is subject to this guard.

### 10.20 R2, independent-start ensemble: the discrete gate DOES flip `[live]`

LS6 job **3365305**, node c301-002, 16 runs across three A100s, all rc=0. This answers the
settling report's instruction directly: *"Repeated runs should report outcome spread and
gate-pass frequency; no universal repeat count exists, while independent-start ensembles are
the stronger convergence check"*, and its warning that *"non-associative, order-dependent
reductions can produce small drift or ALTER DISCRETE GATES"*.

**The gap this closes.** `sim_standing.py:155` takes `seed=0` and uses it at :165 and :183 for
the initial water-particle jitter, plus or minus 0.2h on every water particle. `main()` at :397
**never passes a seed**, so all 24 runs in this document share ONE initial condition. Every
repeat reported before this section measured solver and reduction-order noise at a fixed
initial state; none measured sensitivity to the initial state itself. The seed is injected by
`analysis/ensemble_seed_runner.py`, which subclasses the scene, so the driver file and its
stamped sha256 are untouched.

| cell | n | verdict frequency | margin_frames | k_crit mean +/- sd | k_crit spread | P-2 |
|---|---|---|---|---|---|---|
| n96, dx 0.1361, the margin-0 knife edge | 8 | **SLIDE 7/8, STUCK 1/8** | -1, 0, +1 | 0.9292 +/- 0.0656 | **19.0 %** | 8/8 pass |
| n154, dx 0.0849, the flip cell | 8 | **STUCK 8/8** | -3 in all eight | 2.6860 +/- 0.2477 | **25.9 %** | 0/8 pass |

**Three findings, and the first is the important one.**

1. **The discrete verdict flips under initial-condition perturbation alone.** At the margin-0
   cell, 7 of 8 independent starts give SLIDE and 1 gives STUCK, and the ensemble straddles the
   `k_crit = 1.0` gate boundary (0.8429 to 1.0029). This is the settling report's warning
   observed rather than cited. **The single arm S Silverado run reported in 10.1 as "SLIDE,
   margin 0" is one draw from a distribution that contains STUCK**, and must be read that way.
2. **The flip cell is robust.** 8 of 8 STUCK, `margin_frames` exactly -3 in every start, and
   `k_crit` never within 1.37 of the boundary. The STUCK finding at n154 therefore **survives**
   this test and is strengthened by it.
3. **The earlier noise floor understated variability by more than an order of magnitude, and
   the reason is the statistic, not the runs.** Section 10.2's floor was measured on
   `ratio_slide` (0.11 to 1.21 percent). On `k_crit` the same cells spread **19 to 26 percent**.
   `k_crit` is a min-over-windows-of-a-max statistic and is far noisier than `ratio_slide`, so
   **10.2's floor does not transfer to `k_crit` and must not be quoted for it.** The two-run
   6.3 percent estimate for this cell in 10.2 is superseded by the 8-run 25.9 percent.

**`margin_frames` is the more stable statistic, which corroborates an existing project claim.**
At n154 it is -3 in all eight starts while `k_crit` moves 26 percent. That is direct support
for `analysis/slide_verdict_fragility.py`'s own position that `margin_frames` "assumes nothing
and is the number to quote".

**The seed-0 fidelity check is INCONCLUSIVE, and honestly so.** Seed 0 should reproduce the
original runs, because 0 is the value `main()` has always used implicitly and the wrapper's
`setdefault` injects exactly that. It does not: `k_crit` differs by **13.6 percent** at n96 and
**15.9 percent** at n154. The wrapper at seed 0 is provably the same code path, so this is the
stack's own non-determinism at fixed configuration and fixed seed, not a wrapper artifact. It
is a **third** measurement of the fixed-config draw, and at 14 to 16 percent on `k_crit` it is
comparable to the 19 percent independent-start spread at n96. **So at that cell,
initial-condition sensitivity is NOT clearly separable from the stack's own non-determinism**
by this ensemble alone. **SUPERSEDED: the fixed-seed repeat ensemble this sentence called for
WAS subsequently run, on Vista, and it partially separates them. See 10.22.** The fidelity
question raised in the next paragraph is also resolved there.

### 10.21 R6: this set closes the Undermind Phase 0 vehicle-class gap `[live]`

`UNDERMIND_FINDINGS_DEPLOYMENT_ORDER_2026-08-08.md` Phase 0 records that the 17 gated runs
"represent all three AR&R mass classes (1100 / 1609 / 2337 kg) using one hull, the Yaris, with
mass relabeled only", and that buoyancy, drag and lift lever arms, wheel normal loads and
sliding/float/roll thresholds "depend jointly on displaced volume, underbody shape, wheelbase
and track, and center of mass, not on mass alone". It offers **Path A**, wire a `--vehicle`
flag and run the real Rogue and Silverado hulls, or **Path B**, an explicit limitations
sentence.

**The premise is confirmed by direct measurement, not accepted on the report's word.**
`data/all_runs_inventory.csv`, 17 rows: `hull_m3` has **exactly one distinct value**,
`3.542739`, while `mass_kg` has three, `1100.0 / 1609.0 / 2337.0`. One hull, three labels.

**Path A is executed.** This set runs three real converged hulls at a common dx, spanning a
**2.247x** range in displaced volume (3.542739 / 4.950341 / 7.962083 m3) that the gated set
does not span at all, because its displaced volume is constant.

**And the gap was worth closing, which the gated set could not have shown.** Section 10.13's
3x3 holds mass fixed and varies the hull: at 1100 kg the Yaris gives `margin_frames` **40** and
the Silverado **17**; at 2270 kg the Yaris gives **3** and the Silverado **-3**, a different
verdict. A mass-relabelling design holds displaced volume constant by construction and
therefore cannot produce any of those differences. Section 10.13 also shows the ordering is
**not** monotone in displaced volume, so the correct reading of Phase 0's list is its full
form, underbody shape and wheelbase and track and CoM, and **not** displaced volume as a scalar
predictor.

**What is NOT thereby closed**, stated so this is not over-read: the cross-hull comparison here
remains confounded with tank scaling (section 8), the P-2 containment gate fails on every
matched-dx run (10.7, 10.17), and the large_4wd verdict is contingent on `mu` (10.14, 10.15).
Path A is executed; it is not validated.

**Secondary citation, flagged UNREVIEWED.** The same file cites Allen, Klyde, Rosenthal and
Smith 2003, SAE 2003-01-0966, for CoG-height and yaw/roll-inertia regressions, and warns it is
a **different** paper from SAE 1999-01-1336 already in project files. Neither was checked
against a primary record in this session and no citation connector was used, so both remain
unverified here. Do not cite either as settled on this document's authority.

### 10.22 The control 10.20 named as missing, now run: the flip IS initial-condition driven `[live]`

Vista job **912094**, node c642-012, GH200 aarch64, warp 1.15.0, 16 runs, all rc=0. Driver
sha256 `4696c3b2...`, byte-identical to the Mac and to every LS6 run. 10.20 could not attribute
the verdict flip, because seed 0 also failed to reproduce the original run and both effects were
present at once. **Both policies were therefore run on ONE machine**, same cell, everything else
held fixed, so seed policy is not confounded with architecture:

| arm | seed policy | STUCK | k_crit mean +/- sd | min | max | spread |
|---|---|---|---|---|---|---|
| **F** | **pinned at 0**, 8 repeats | **0 / 8** | 0.9558 +/- 0.0345 | 0.9049 | 0.9955 | 10.01 % |
| **I** | **varied 0..7** | **1 / 8** | 0.9661 +/- 0.0413 | 0.8868 | **1.0045** | 13.27 % |

**Arm F never crossed the `k_crit = 1.0` boundary in eight draws; arm I crossed once, at seed 4.**

**The decisive evidence is cross-machine, and it is strong.** Seed 4 returns STUCK on **both**
machines, across two architectures and two warp versions:

| seed | LS6 A100 x86_64, warp 1.12.1 | Vista GH200 aarch64, warp 1.15.0 | diff | verdicts |
|---|---|---|---|---|
| s4 | `k_crit` 1.0029, **STUCK** | `k_crit` 1.0045, **STUCK** | **+0.16 %** | agree |
| s5 | 0.9768, SLIDE | 0.9768, SLIDE | -0.00 % | agree |
| s7 | 0.9743, SLIDE | 0.9743, SLIDE | +0.00 % | agree |
| s0 | 0.8429, SLIDE | 0.9956, SLIDE | +18.11 % | agree |
| s3 | 0.8805, SLIDE | 0.9964, SLIDE | +13.16 % | agree |

**All eight seeds agree on VERDICT across architecture, warp version and machine, 7 SLIDE and
1 STUCK on both.** The crossing seed reproduces to 0.16 percent on hardware that shares
nothing with the original. That is not a random draw.

**Conclusion, and its limit.** The seed-4 initial condition does real, reproducible work: it is
what carries this cell over the gate, not stack noise. **But the attribution is partial, not
total.** Arm F reached 0.9955, only **0.45 percent** below the boundary and well inside its own
10.01 percent spread, so it cannot be said that a fixed-seed ensemble *cannot* cross, only that
it did not in eight draws. The honest statement: **at the margin-0 cell the initial condition
supplies a reproducible push across the boundary, and the cell sits close enough that stack
noise alone might also cross it given more draws.** 10.20's "cannot attribute" is superseded by
this partial attribution; its verdict-frequency result is unchanged.

**This also CLOSES the fidelity question 10.20 left open.** 10.20 reported the seed-0 check as
INCONCLUSIVE because seed 0 did not reproduce the original run. With eight fixed-seed draws the
answer is now clear: the fixed-seed distribution spans 0.9049 to 0.9955 and **contains the
original run's 0.9572 exactly**, at `FIXED_s0_r2`. The original is an ordinary draw from that
distribution, so **the wrapper is faithful** and the earlier 13.6 percent gap was the stack's
own non-determinism, exactly as suspected but not then demonstrable.

**One pattern this does NOT explain, flagged rather than rationalised.** Two seeds reproduce
across machines to four decimal places (s5 at -0.00 percent, s7 at +0.00 percent) while two
others differ by 13 to 18 percent (s3, s0). An exact four-decimal match on foreign hardware is
not what a uniformly chaotic system produces, and nothing here accounts for why some initial
conditions are reproducible across architectures and others are not. **Recorded as unexplained.**

### 10.12 Achieved control, versus intended

| arm | dx spread | realized-depth spread |
|---|---|---|
| S | 38.6997 % | 19.8644 % |
| M | **0.0494 %** | **0.0494 %** |
| D | **0.0494 %** | **0.0494 %** |

The matched arms achieved exactly what section 3 predicted, and the predicted `grid_lim`,
`dx`, layer count and pre-carve water count all reproduced in the run logs, for example the
Silverado at `lim=13.067933` against a predicted 13.06793299 and `dx=0.084857` against a
predicted 0.0848567.

### 10.19 Handoffs, so nothing here waits on this dispatch

**To D4, my one-paragraph line for the consolidated `mu = 0.55` register entry. CONFIRMED as
written, with two precisions added and nothing corrected.** The resolution-dependence of the
large_4wd verdict is itself friction-dependent: for the Silverado at 2270 kg, refining dx from
0.1361243 to 0.0848567, a **37.66 percent** reduction, moves `margin_frames` only **10 to 11**
at `mu = 0.30` while the same refinement at `mu = 0.55` moves it from **0 to -3** and flips the
verdict to STUCK. So the entire resolution sensitivity of this verdict lives at the high-`mu`
end, and **register J15's finding must carry its `mu`**. The two precisions: the numbers are
the Silverado at 2270 kg specifically, not a general result across the three classes; and
`k_crit` crossing 1.0 near `mu = 0.40` locates the boundary between measured rungs at 0.30 and
0.40, it is not a measurement AT 0.40 of anything finer.

**To D4, second item: the in-driver sha256 hull guard.** `sim_standing.py:73` guards by
filename and both retracted hulls are reachable under other names. The digest set and the two
retracted digests are in section 5. Apply it **only once the matched-dx set is final**, because
applying it changes the driver sha256 that stamps every run in this document. Until then
`analysis/preflight_hull_guard.py` covers the gap without touching the driver.

**To D4, third item: gate P-2 and CLAUDE.md item 7.** Section 10.17 gives the geometric
baseline, the per-run excess, and the method to reproduce both from data already committed.
The seven-run P-2 failure list in item 7 may be partly ranking hull geometry rather than
containment. The numbers are recomputed here independently; verify rather than take them on
this document's word.

**To D1, which owns the commit answering J15:** establish which `mu` each J15 rung actually
ran at. If the J15 flip does not reproduce at the 0.3 convention, the corner result in 10.15
inherits that qualifier and so does D9's.

**Not mine to change, recorded so it is not lost:** `vehicle_params.py` carries the canonical
Yaris at 1100 kg, which a live NHTSA pull places **above** the top of the real 1043 to 1071 kg
trim range. Every one of the 17 gated runs rests on it.

## 12. Transferring this design to a realistic domain, and where it breaks `[live]`

The realistic-environment plan credits this dispatch with holding **realized depth fixed by
construction** and asks that any multi-vehicle realistic scene do the same. That recipe as
written here is **not directly transferable**, because it is built around a domain derived from
the hull. This section restates it in a form that survives the change, and quantifies a hazard
the planned architecture would otherwise walk into.

### 12.1 The one constraint that is domain-independent

Everything else in section 3 depends on `lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)`. **This
does not:**

    water_layers  = ceil(depth/h - 0.5)        h = dx/2      sim_standing.py:181
    realized depth = water_layers * h

Realized depth is an **integer multiple of dx/2**, whatever sets dx. An open channel, a road
patch, a reconstructed surface: the quantization is identical, because it comes from how the
water block is built, not from how the domain is sized.

Swept over cell sizes a realistic domain might plausibly choose, at a 0.30 m target:

| dx | h | layers | realized depth | error vs target |
|---|---|---|---|---|
| 0.1500 | 0.07500 | 4 | 0.300000 | **0.00 %** |
| 0.1200 | 0.06000 | 5 | 0.300000 | **0.00 %** |
| 0.1000 | 0.05000 | 6 | 0.300000 | **0.00 %** |
| 0.0849 | 0.04245 | 7 | 0.297150 | -0.95 % |
| **0.0800** | 0.04000 | 7 | **0.280000** | **-6.67 %** |
| 0.0600 | 0.03000 | 10 | 0.300000 | **0.00 %** |

**A badly chosen dx reintroduces a depth error of the same order as the confound this whole
document exists to remove** (arm S's realized-depth spread was 19.86 percent, and its
worst per-vehicle deviation about 9 percent). dx 0.08 gives -6.67 percent for free.

### 12.2 Invert the architecture: pick dx from the DEPTH, not from the hull

In the current scene dx is a consequence (`lim/n_grid`, and `lim` comes from the hull), so
matching depth required an integer search over `n_grid` and still landed 0.95 percent off. **An
open channel removes that constraint**, because the domain is no longer hull-derived. Then the
rule is exact and needs no search:

    choose  dx = 2*D_target/n   for integer n     ->  D_target/h is an integer
                                                  ->  realized depth == D_target exactly

Verified to machine precision at n = 4, 6, 8, 10, 12, 15, 20: absolute error **0.0e+00** at
every level. This is strictly better than what this document achieved, and it is available only
once the domain stops being derived from the hull. **It also makes cross-vehicle depth matching
automatic rather than searched**, since any vehicles sharing that dx share the layer count by
construction.

### 12.3 The AMR hazard, quantified. A refinement window makes realized depth a function of position

The multi-resolution plan calls for a refinement window that follows the vehicle. Because
realized depth is `layers * h` and `h` is **local**, a 2:1 refinement boundary can put
**different water depths on either side of it**, in the same domain, at t=0:

| coarse dx | coarse realized | fine dx | fine realized | jump across the boundary |
|---|---|---|---|---|
| 0.1200 | 0.300000 | 0.0600 | 0.300000 | 0.00 % |
| **0.1100** | **0.275000** | 0.0550 | **0.302500** | **+10.00 %** |
| 0.1000 | 0.300000 | 0.0500 | 0.300000 | 0.00 % |
| 0.0900 | 0.315000 | 0.0450 | 0.292500 | **-7.14 %** |
| **0.0800** | **0.280000** | 0.0400 | **0.300000** | **+7.14 %** |
| 0.0700 | 0.315000 | 0.0350 | 0.297500 | -5.56 % |

**Worst case +10.00 percent**, which is **larger than the 9.09 percent depth change this
document already flags as a confound** in its own (dx, mu) square. A vehicle sitting inside the
fine window would be in 0.3025 m of water while the far field sits in 0.275 m: not a numerical
artifact to be averaged away, but a physically inconsistent initial condition.

**The 12.2 rule removes it exactly.** Where `D/h` is an integer at the coarse level, a 2:1
refinement doubles the layer count and the realized depth is unchanged, giving 0.00 percent at
dx 0.12, 0.10 and 0.06 above. **This costs nothing: it is a constraint on which dx you pick,
not extra computation.**

Note the two properties are separate and both matter. dx 0.0849 shows **0.00 percent jump** yet
is **0.95 percent off target** on both sides: consistent but inaccurate. Only `dx = 2D/n` gives
both.

### 12.4 What this document cannot contribute, stated plainly

**RESTATED 2026-08-14 after the report CATALOGS were read rather than only their summaries.
The blockers below are IMPLEMENTATION blockers, not MPM-method blockers.** MPM has already been
run on a real road surface, twice, and neither paper is cited anywhere in this project:

- **Zhou et al. 2025**, *Physics of Fluids*, DOI `10.1063/5.0276643`: tyre-pavement viscous
  **hydroplaning in MPM**, i.e. a tyre on a pavement with a water film.
- **Chen et al. 2022**, DETC2022-89632: **MPM deformable terrain** for off-road vehicle mobility.

So "MPM cannot host a road" is not the situation. What this document lacks is a domain that is
not derived from the hull and an open boundary with a real mass sink, both of which are
implementation work. **Section 12.1 to 12.3 above are therefore the transferable part and are
unaffected**: the depth quantization and the AMR discontinuity apply to any MPM road domain,
including the two published ones.

**RELATED-WORK CORRECTION, because a reviewer will find these.** Vehicle fording **has** been
simulated before, at least four times, and none is cited in this project: Wasfy, Wasfy and
Peters 2015 (DETC2015-47142, coupled multibody plus SPH), Pazouki, Jayakumar and Negrut 2016
(who are the **Chrono authors**, already in register A-1 for rigid coupling), Khapane and
Ganeshwade 2014 (SAE 2014-01-0936), and He et al. 2026 (`10.1115/1.4071177`, with experimental
validation). **"Nobody has simulated vehicle fording" is FALSE and must never be written.**
What remains true is the narrower statement this document already uses: **no validated
vehicle-fording MPM chain is identified**, because those four are SPH and multibody, not MPM.
This document makes no firstness claim and must not be read as making one.

**No slope result, and not for want of trying.** Every run here sits in a **closed** box: a
floor plane plus four slip walls (`sim_standing.py:210-214`), no terrain, camber, curb or
gradient. A bounded domain cannot measure a slope, because conserving the water volume forces a
redistribution larger than the effect being measured. **The tank confound recorded in section 8
is a symptom of the same closure**, and it is why the cross-hull "geometry" effect in 10.4 and
10.13 cannot be separated from tank scaling. **An open channel with a real mass sink is the
instrument; this set does not have one, so no number here transfers to a sloped or open
domain.**

## 13. Two papers that make this set citable rather than bespoke `[live]`

### 13.1 Martinez-Gomariz et al. 2017: a published methodology for exactly this move

**Martinez-Gomariz, Gomez, Russo and Djordjevic 2017**, *A new experiments-based methodology to
define the stability threshold for any vehicle exposed to flooding*, **Urban Water Journal**,
DOI `10.1080/1573062X.2017.1301501`, 22 March 2017, **83 citations** (moving-rigid-body catalog
entry #5, 100 percent match).

**Where this set agrees with it, structurally.** The paper's whole premise is a threshold
defined **for any vehicle** from that vehicle's own properties, rather than a class label
carrying a mass. That is the same move this set makes and is precisely what
`data/all_runs_inventory.csv` does **not** do: one hull, `hull_m3` a single distinct value
3.542739 across all 17 rows, three mass labels (10.21). So the three-class set is not a bespoke
detour; it is the simulation analogue of an established, well-cited experimental methodology.
**That materially changes how this work should be positioned**: per-vehicle thresholds are
standard practice in the flood-vehicle literature, and the mass-relabelled canonical set is the
departure from it, not the other way round.

**Where it diverges, and this is not a small gap.** Their observable is an experimentally
derived **incipient-motion threshold**, a depth-velocity curve at which motion begins. Ours is a
**discrete SLIDE / STUCK / FLOAT verdict** at one fixed depth and velocity, from an MPM
simulation, under a friction assumption their method does not need. **These are not the same
quantity and no number may be carried between them.** Producing a comparable threshold from
this stack would mean sweeping velocity to incipient motion per vehicle, which is not what any
arm here did.

**MARKED UNREVIEWED, and deliberately so.** The catalog carries this paper's bibliographic
record but **no abstract**, and the paper itself was not retrieved this session. The mapping
above is therefore **structural**, based on the stated methodology in the title and the
project's own A-3 note. **It is not a coefficient-level or formula-level comparison and must not
be cited as one** until the paper is read. Note also CLAUDE.md A-3's caveat: Smith/Modra/Felder
and Arrighi 2015 already appear in the register in adjacent contexts and are **not** independent
support; **Martinez-Gomariz 2017 and Allen 2003 are the genuinely new ones**, and this is the
first use of the former anywhere in the project.

### 13.2 Hu et al. 2023: the axis this set did not sweep, named

**Hu, Li, Wang and Fang 2023**, *Experimental testing to determine stability thresholds for
partially submerged vehicles at different flow orientations*, **Journal of Hydrology**, DOI
`10.1016/j.jhydrol.2023.129525`, 1 April 2023 (catalog entry #12, 100 percent match).

**Every run in this document is at ONE flow orientation, and it is broadside.** This was not a
stated choice and is recorded here for the first time. The flow is `+x`
(`sim_standing.py:240` adds the velocity to `v[:n_water, 0]`) while the hull long axis lies on
scene `y` (established in section 3), so the flow strikes the vehicle **side-on**:

| vehicle | scene extent (x, y, z) m | broadside area m2 | head-on area m2 | ratio |
|---|---|---|---|---|
| yaris | 1.7464, 4.2826, 1.5180 | 6.5010 | 2.6510 | **2.45x** |
| rogue | 2.0101, 4.7466, 1.7294 | 8.2087 | 3.4763 | **2.36x** |
| silverado | 2.3377, 5.9400, 2.0102 | 11.9403 | 4.6991 | **2.54x** |

Rotating from broadside to head-on removes **57.7 to 60.6 percent** of the projected area.
**All 40 runs in this document sit at the maximum-projected-area orientation.**

**That is the conservative choice, and it is published as such.** Azhar, Pauwels and Bui 2023,
the same paper `mu = 0.55` comes from, states verbatim: *"The numerical investigation is
performed using smoothed particle hydrodynamics (SPH) with the vehicle oriented perpendicular to
the flow direction, **as this is the most critical orientation**."* So this set's orientation is
the worst case rather than an arbitrary one, which is worth stating because it was never
justified before.

**But it is still ONE orientation, and the axis matters.** D11 measured `margin` **linear in
yaw** with a **2.2x spread**, 0.26 to 0.57, in the one parameter the margin is linear in. **Hu
et al. 2023 is the experimental dataset for that axis and this set does not sweep it.** Any
three-class ordering here is an ordering **at broadside only**.

**One structural reason the ORDERING may be more robust than the magnitudes.** The
broadside-to-head-on area reduction is nearly uniform across the three hulls, 59.2 / 57.7 / 60.6
percent, so a pure projected-area effect would rescale all three by almost the same factor and
leave their order intact. **This is an indication, not a prediction:** Hu 2023 exists precisely
because orientation is not a pure area scaling, and D11's 2.2x spread is far larger than the
2.9-point spread in those reduction percentages. **The magnitudes in this document should be
read as broadside-specific; the ordering may survive rotation, and that is untested.**

### 13.3 A third thing the same paper already anticipated

Azhar, Pauwels and Bui 2023 also states that *"the ARR stability curve can shift depending on
the road conditions that affect the vehicle's sliding mechanism."* **Section 10.14 is a
measurement of exactly that shift**: `k_crit` moves 0.4764 to 4.3928 across `mu` 0.30 to 0.78,
and the verdict changes at about 0.40. So this document's friction result is **not a criticism
of AR&R**; it quantifies a sensitivity the source paper itself flagged, on the same axis, using
the same coefficient that paper measured.

## 14. Settle length: the ordering was tested against it, and survives `[live]`

D9 re-derived its headline at a 250-frame settle on 2026-08-14 and found that a 60-frame settle
had inflated a spread roughly threefold **and inverted an ordering** (gate error 63.28 / 94.44 /
157.06 increasing with vehicle size at 60 frames; 72.88 / 49.75 / 34.01 decreasing when
converged). Its stated lesson: **state the settle length any number was measured at.**

**This scene settles for 8 frames** (`sim_standing.py:154`, `settle_frames=8`, loop at
`:235-237`), never gated on a stationarity test. That is **7.5x shorter than the value D9 showed
to be inadequate and 31x shorter than its converged value**, and this document's headline
results are **orderings**, which is exactly what inverted. So the exposure was direct rather
than theoretical.

**It was therefore tested rather than disclosed.** Vista job 912094, GH200, 6 runs, all rc=0:
the three hulls at matched dx and a common 1100 kg, run at settle **8** and settle **250**, same
machine, everything else held fixed.

| vehicle | margin @ 8 | margin @ 250 | k_crit @ 8 | k_crit @ 250 | k_crit change |
|---|---|---|---|---|---|
| yaris n111 | 40 | **40** | 0.1466 | 0.1934 | +31.9 % |
| rogue n123 | 46 | **44** | 0.1236 | 0.1389 | +12.4 % |
| silverado n154 | 17 | **17** | 0.3082 | 0.2982 | -3.2 % |

**The ordering is unchanged: rogue > yaris > silverado at both settle lengths**, all three SLIDE,
and `margin_frames` moves by at most **2 frames** across a 31x change in settle. **Section
10.13's non-monotone-in-displaced-volume finding survives a converged settle.**

**`k_crit` does move, by up to +31.9 percent, and that is NOT attributable to the settle.** It
sits inside the 19 to 26 percent independent-start spread measured in 10.20 and the 10.01 percent
fixed-seed spread in 10.22, so a single pair per vehicle cannot separate a settle effect from the
draw. **This is the third independent corroboration that `margin_frames` is the stable statistic
and `k_crit` is not**, after 10.20 and 10.22.

### 14.1 The settle control has discriminating power, which is what makes surviving it mean something

The same control was applied five times across sessions on 2026-08-14, and **it did not simply
confirm what it was pointed at**. Three results dissolved under it and two survived:

| result | outcome under a converged settle |
|---|---|
| D9's at-rest gate | **dissolved** |
| the R7 mirror control | **dissolved** (and refuted) |
| D9's traction-margin spread and gate-error ordering | **dissolved**: 6.07x collapsed to 1.94x, and the ordering INVERTED |
| **CLAUDE.md item 5**, the 1100 kg Yaris displacement ladder | **survived** |
| **this document's three-class ordering** (14 above) | **survived** |

**A control that killed three of five is not a rubber stamp**, so passing it is evidence rather
than a formality. That is the reason to report section 14 as a result and not as due diligence.

**On item 5 specifically**, since this document sits beside it: D9 re-ran it at
`settle_frames=250` against the canonical 8, a **31-fold** increase with everything else held.
The step from g48 to g64 reads **+87.8 percent canonical against +95.9 percent controlled**, and
g64 to g96 reads **-59.2 against -56.1**, non-monotone in **both**, with absolute displacements
at settle 250 of **0.249207 / 0.488112 / 0.214442 m**. Same sign, same shape, same rough
magnitude. **Item 5 may no longer be described as possibly an initial-condition artifact**: the
explanation that killed the other three does not apply to it, so it moved from an unexplained
non-monotonicity to one with the single most likely alternative ruled out. Steffen, Kirby and
Berzins 2008 remains the citation for the phenomenon.

**One distinction that must not be collapsed.** Item 5 is about **displacement magnitude** and
remains **grid-invariant in VERDICT**, all nine NO-FORD. This document's resolution result is a
**verdict** change (the large_4wd SLIDE to STUCK, register J15's, reproduced here at finer dx and
shown in 10.15 to be jointly contingent on `mu`). **Different quantity, different vehicle,
different claim.** Item 5's "cite the verdict, never the displacement magnitude" is unaffected by
anything here.

**What this does NOT test, and the gap matters.** Only the **1100 kg row** was re-run, where all
three vehicles are comfortably SLIDE. **The two cells nearest a boundary were not re-tested at a
converged settle**: the margin-0 knife edge (`S_silverado_n96`) and the STUCK flip cell
(`M_silverado_n154_m2270`). D9's inversion appeared in a quantity near a threshold, and those are
exactly this document's threshold-adjacent cells. **The flip cell's settle sensitivity is
untested and should be assumed open.**

### 14.2 The g128-or-finer determinism requirement, and where it applies here `[live]`

A mirror-symmetry ladder run in the **R7 symmetric test scene** on 2026-08-14, at a 200-frame
settle throughout so it is not the transient artifact that dissolved three other results, found
the mirror asymmetry falling cleanly through g96 (0.1701, 0.0490, 0.0244 m) and then **jumping
about 70x at g112** (1.6744) and g128 (2.0252). The asymmetry **reproduces tightly** across three
independent g128 runs, 2.0252 / 2.0280 / 2.0272, agreeing to 0.14 percent, so it is a property of
the configuration. The **determinism floor does not**: 1.6936 / 0.5220 / 1.4515 m, a 3.2x spread,
i.e. **metre-scale run-to-run variation, larger than the vehicle**.

**UPDATED: the break is a GROWING INSTABILITY, and the threshold is g112, not g128.** A frame
ladder at n_grid 112 gives mirror asymmetry / determinism floor of 0.3608 / 0.00568 at f20,
1.0911 / 0.02012 at f50, 1.9262 / 0.09369 at f100, 1.6744 / 0.28795 at f200. **The asymmetry
GROWS with integration time and saturates near 2 m, which is domain scale.** A setup error would
be constant and a transient would decay; growth-then-saturation is the signature of an
**instability**. The floor grows monotonically too, roughly 4x per doubling of frames, faster
than linear. **Even at f20 the g112 ratio is already 63x**, so the break exists early and simply
has not grown yet, **which is why a short run at fine resolution can look acceptable**.

Against the f200 resolution ladder (0.1701, 0.0490, 0.0244, 1.6744, 2.0252 for
g48/g64/g96/g112/g128), **the transition is sharp between g96 and g112**: below it the control
converges cleanly and passes below the determinism floor at g64 and g96; above it a symmetry the
scene has **by construction** is violated at metre scale, reproducibly, and grows with time.

**BISECTED: the ceiling sits between n_grid 100 and 104**, in a four-unit window, all at a
converged 200-frame settle so the transient explanation that dissolved three other results does
not apply. Mirror asymmetry / determinism floor: g96 **0.0244 / 0.0293 passes**; g100
**0.1895 / 0.2686 still passes**, the mirror sitting *below* the floor at ratio 0.71; g104
**1.5810 / 0.3774** and **1.6027 / 0.1697 fails** at about 8x the floor, the two independent runs
agreeing to 1.4 percent; g112 1.6744 / 0.2880; g128 2.0252 with three runs agreeing to 0.14
percent. **Below the ceiling the asymmetry converges monotonically and sits at or under the
floor, which is what a symmetry control should do. Above it, it jumps ~8x and grows with
integration time.**

**SCOPE, AND THIS IS THE EASY MISTAKE TO MAKE.** That is the R7 symmetric test domain, not this
scene, and `grid_lim` differs between them, so **n_grid 104 there is NOT the same `dx` as n_grid
104 here**. **The threshold must not be translated across scenes by grid number, and nothing in
this document may be read as sitting "above the ceiling" on the grounds that 111, 123 and 154
exceed 104.** They are different domains and the numbers are not commensurable. This document
does **not** by itself say the canonical g128, or any arm here, is broken.
What it establishes is that this solver has a **resolution ceiling in at least one scene**,
sitting between g96 and g112. What it licenses is a **requirement**: any result quoted at **g112
or finer**, in any scene, must carry **both** a repeat-run determinism floor **and** a frame
count, because both matter and both were invisible in every published number so far.

**At the tightened g112 threshold, TWO arms trigger, not one.** Comparing each vehicle's matched
`dx` against that same vehicle's own g112 and g128:

| vehicle | n_grid | matched dx | its g112 dx | its g128 dx | triggers at g112? |
|---|---|---|---|---|---|
| yaris | 111 | 0.0848806 | 0.0841227 | 0.0736074 | no, coarser (narrowly) |
| **rogue** | **123** | **0.0848987** | 0.0932369 | 0.0815823 | **YES** |
| **silverado** | **154** | **0.0848567** | 0.1166780 | 0.1020932 | **YES** |

**Frame count for every run in this document: 90 frames, settle 8**, except section 14's settle
arm at 250. That is now reported because the rule requires it.

**The floor exists and was already run**, `F_silverado_n154_m2270_rep` against
`M_silverado_n154_m2270`, same job class, same everything:

| | verdict | margin_frames | k_crit |
|---|---|---|---|
| `M_silverado_n154_m2270` | STUCK | -3 | 2.7840 |
| `F_silverado_n154_m2270_rep` | **STUCK** | **-3** | 2.9596 |
| floor | identical | **identical** | **6.3 %** |

**The rogue floor did not exist and was run to close the gap.** Every other rogue n123 run
differs in mass or settle, so none was a same-config repeat. Two identical runs, Vista GH200,
90 frames, settle 8:

| | verdict | margin_frames | k_crit |
|---|---|---|---|
| `FLOOR_rogue_n123_m1571p3_a` | SLIDE | 21 | 0.2310 |
| `FLOOR_rogue_n123_m1571p3_b` | SLIDE | 21 | 0.2315 |
| floor | identical | **identical** | **0.22 %** |

The LS6 run of the same configuration, `M_rogue_n123_m1571p3`, returned `k_crit` **0.2315**,
matching run b to four decimals across architecture and warp version.

**This scene shows no sign of the R7 pathology at n123 or n154.** Verdict and `margin_frames` are identical across both repeats, and `k_crit` moves
**0.22 percent** at the rogue arm and **6.3 percent** at the silverado arm, neither of which is
anything like a metre-scale collapse or a time-growing divergence. That is evidence **against** generalising the R7 blow-up to this scene, and it is
offered only as that: an absence in one cell, not a clean bill.

**What DOES transfer is the method, and this scene has never used it.** A symmetry control is
cheap and unambiguous, because the exact answer is known by construction rather than by
comparison, and it located a ceiling **no gate in this project detects**. This scene has no
such control. One is available and was never run: the hulls are left-right symmetric about their
own longitudinal plane, and the flow runs along the vehicle's lateral axis (13.2), so **running
flow `+x` against flow `-x` should give mirrored results**. Any asymmetry beyond the repeat floor
would be solver error, on the same logic as R7.

**One caveat that must be measured first, not assumed:** these are derived hulls, not idealised
bodies, so each carries its **own** left-right asymmetry. That mesh asymmetry has to be
quantified and subtracted before a flow-reversal result means anything, otherwise the control
measures the mesh. That measurement is cheap, is pure geometry, needs no GPU, and was not done.

**Two honest gaps.** First, **the floor here is not the coordinator's quantity.** It measured max
absolute particle displacement in metres; this set records verdict, `margin_frames` and `k_crit`,
and `final_disp_mag_m` is written to `summary.json` but **dropped by the classifier**, so no
metre-scale floor can be produced from the committed CSVs without re-reading the run
directories. Second, `n_grid` is **not comparable across scenes** because `grid_lim` differs, so
"n154 is above g112" carries no meaning against the R7 ladder; only each vehicle's own g128
comparison above does.

## 15. Particle resolution against the published conventions, with the unit stated `[live]`

From `compass_artifact_wf-211aad60`, *Particle Resolution and Force Convergence for Rigid Bodies
in Flood-Type Flows*, read directly this session.

**The headline is a negative and it is worth stating plainly: there is NO formally validated
force-convergence criterion in the SPH, MPM or PIC-FLIP literature.** No paper gives a validated
rule of the form "N particles across the body or flow depth guarantees resolution-independent
drag, lift or moment within X percent". What exists are rules of thumb propagated between papers.
So CLAUDE.md L-3's "~10 particles per flow depth" is a **starting point, not a criterion**, and
this document should not be read as failing a standard that does not exist.

### 15.1 The H/dp >= 5 convention, and the unit it is counted in

The artifact quotes a real-scale DualSPHysics study: *"Roselli et al. (2018) and Altomare et al.
(2017), amongst others, suggest that particle spacing is set to allow for at least 5 particles to
capture the largest wave height... H/dp = 5."*

**`dp` is PARTICLE spacing, and the heuristic counts PARTICLES.** In this scene the particle
spacing is `h = dx/2`, not `dx`, so the comparable quantity is **depth/h**, which is the water
**layer count**, not depth/dx. CLAUDE.md L-3 already makes this distinction: *"4 particle layers
and 2 grid cells."* Counted correctly:

| set | water layers = depth/h | depth/dx | vs H/dp >= 5 | vs ~10 per depth |
|---|---|---|---|---|
| canonical g64 | **4** | 2.000 | **BELOW** | below |
| arm S, n96 yaris | 6 | 3.000 | above | below |
| **matched-dx arm** | **7** | 3.500 | **ABOVE** | below |

**So the two sets sit differently, and conflating the units would misstate it.** The canonical
g64 baseline is **below** the minimum-to-capture-a-wave heuristic at 4 particles. **The matched-dx
three-class set is above it at 7**, and below the ~10-per-depth guideline. Read in grid cells
instead (2.000 and 3.500) both look below 5, but that is not the quantity the heuristic counts.

**Two caveats that cut against over-reading even the correct comparison.** The artifact states
H/dp >= 5 is *"a minimum wave-resolution heuristic, explicitly not a force-convergence rule"*,
and that the same study found halving `dp` to H/dp ~ 7.2 produced *"no significant impact"* on
results while runtime rose from 96 to 768 hours. So the one refinement test reported alongside
this convention found the difference immaterial.

### 15.2 Published resolutions, and where this set sits

Documented values in the artifact span **2 to 60** across a load-bearing feature: girders spanned
by ~2 to 4 particles (Wei and Dalrymple 2016), a cube at dp = D/25, dam-break obstacles at
H/dp = 20 to 60, the SPHERIC benchmark box at dp = H/55. **This set is not unusually coarse by
publication standards; it is coarse against the conventions.** Both statements are true and only
the second is a criticism.

### 15.3 The bias direction, with its documented exception

L-4's "coarse over-predicts, so NO-FORD is conservative" holds *usually*, via kernel truncation,
boundary-particle deficiency and neglected air cushioning in single-phase models. **The exception
is documented and concrete:** Wei and Dalrymple 2016's *finest* resolution under-predicted the
horizontal peak force, because at that resolution the tsunami front broke prematurely before
reaching the deck. **The bias is problem-dependent, not a law, and must not be written as one.**
This matters here because the matched arm is the finest grid in this comparison.

### 15.4 PPC

The artifact independently cites Steffen, Kirby and Berzins 2008 for classic MPM **losing**
convergence as the grid refines at fixed particles-per-cell, and notes MPM PPC is typically
**3.5 to 16**. This stack runs **PPC 8**, mid-range and unremarkable. Combined with D9's direct
refutation of PPC as the mechanism in this scene (10.6), the position is: **a normal PPC, a real
general mechanism, and a measured negative saying it is not what bites here.**

## 11. Standing limitations

- `depth/dx = 3.5` and 7 particle layers is better than the canonical g64 baseline's
  `depth/dx = 2.000` and 4 layers, but still well short of the roughly 10 particles per flow
  depth rule of thumb. **A limitation, never a converged resolution.** `[inherited]`
- No gate is a physics validation. Every gate is a self-consistency or numerical-containment check; G-3 compares against a constant derived from the same pipeline, and G-6/P-4/P-5 have no pass criterion at all. (CLAUDE.md item 6.) The P-2 passthrough limit reported per run is therefore a containment tripwire, not evidence that the physics is right. `[inherited]`
- Steffen, Wallstedt, Guilkey, Kirby and Berzins 2008, DOI `10.3970/CMES.2008.031.107`, is a
  citable mechanism for MPM losing convergence under refinement at fixed particles-per-cell,
  and PPC is constant at 8 in this stack. **It is a candidate, not the established cause:** D9's
  direct co-refinement test REFUTES PPC as the mechanism in its own scene, finding SDF band
  width dominant instead. Band width does not exist on this document's material-8 free-rigid
  path, so that specific alternative cannot apply here, but the refutation means PPC must not be
  asserted. Cite the paper as TRANSFERABLE NUMERICAL ANALYSIS, NOT WATER VALIDATION. `[inherited]`

- **STANDING RULE, from 10.20: every fragility or headroom number must name the statistic it
  was measured on.** The reproducibility floor is not a property of the runs, it is a property
  of the statistic. Measured on the same cells: `ratio_slide` spreads **0.11 to 1.21 percent**
  while `k_crit` spreads **19 to 26 percent**, because `k_crit` is a min-over-windows-of-a-max
  and sits near a threshold. A floor quoted without its statistic is not interpretable, and
  quoting the `ratio_slide` floor against a `k_crit` difference is the specific error this
  document already made once and corrected. `margin_frames` is the most stable of the three and
  is the number to quote where a single figure is needed.
- The AR&R and Shand thresholds describe a **stationary** vehicle in flow, which is what this
  setup is, so this is not a scenario mismatch. `[inherited]`
- CLAUDE.md L-4 says coarse resolution usually **over**-predicts peak hydrodynamic force, so
  over-threshold NO-FORD verdicts are conservative. **Cite it with its condition attached:**
  under-resolution over-predicts via kernel truncation and boundary-particle deficiency, but
  over-FINE resolution can trigger premature wave breaking and **under**-predict. The bias is
  *problem-dependent, not a settled law*. That matters directly here, because the matched arm
  is the finest grid in this comparison, so the conservative-direction argument cannot simply
  be assumed to apply to it. `[inherited]`
- Smith/Modra/Felder 2019 and Arrighi 2015 already appear in the register in adjacent
  contexts, so they are **not** independent support for the geometry framing.
  Martinez-Gomariz 2017 and Allen 2003 (SAE 2003-01-0966) are the new ones, and Allen is
  self-flagged provisional, citable as method and not as validation. `[inherited]`
- **Still-water depth limits must NEVER be conflated with depth-velocity products.** These runs
  sit at realized depth 0.2970 m and D x V 0.4456 m2/s, and both are quoted in 10.16. The
  citable validation targets are separate quantities: total-head criteria of **0.3 m** for
  passenger cars and **0.6 m** for emergency vehicles, against a simulated critical depth
  **0.38 m** with minimum D x V **0.39 m2/s**. One public benchmark carries approximately
  **0.3 percent** experimental uncertainty and is the right locked regression case. **It now has
  a name: Kramer et al. 2021, *Energies* 14(2):269, DOI `10.3390/en14020269`, a PUBLIC and
  downloadable heave-decay dataset for a floating sphere.** None of these has been used as a
  validation target here. **MERGE HAZARD, flagged because this document cites both:** that is a
  DIFFERENT paper from Kramer et al. 2016 (`10.1016/J.IJDRR.2016.04.003`), the watertightness
  study already in the register and referenced in section 4. Same lead author, different year,
  different subject. **Do not merge them.** `[inherited]`
- **Unsteady flow raises drag 40 to 50 percent (Azhar 2026) and is not modelled.** The inflow
  here is a fixed-velocity Dirichlet clamp on an upstream slab, so the flow is as steady as the
  scene can make it. **A realistic domain makes this worse, not better**, so the omission grows
  rather than shrinks when this design is transferred. `[inherited]`
- **Settling has no threshold, only a protocol, and this set does not implement it.** The scene
  runs a **fixed 8-frame settle** (`sim_standing.py:235-237`) that is never gated on a
  stationarity test. The defensible protocol is to exclude initial and final transients,
  demonstrate stationarity for the reported observable, and attach uncertainty from correlated
  samples via autocorrelation, blocking or bootstrap. A longer or more complex domain lengthens
  the transient, so this becomes mandatory rather than optional on transfer. `[inherited]`
- **Order-dependent reductions can alter discrete gates, and this document MEASURED it rather
  than citing it.** Section 10.20's ensemble returns 7 of 8 SLIDE and 1 of 8 STUCK at the
  margin-0 cell, straddling the `k_crit = 1.0` boundary. Any realistic-domain build must use
  reproducible reductions, and must report gate-pass FREQUENCY rather than a single verdict at
  any cell whose margin is small. `[live]`
- **No claim in this document has been through the physics-skeptic subagent yet.** The
  numerical results in sections 2, 3 and 8 are reproducible by running
  `analysis/three_class_matched_grid.py`, which self-verifies against five external anchors,
  but the interpretation is unreviewed until section 10 is complete.
