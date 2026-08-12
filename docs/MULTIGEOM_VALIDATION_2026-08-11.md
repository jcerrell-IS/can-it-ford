# Multi-geometry validation: Rogue and Silverado

Date: 2026-08-11. Author: session working from the dispatch of the same date.

**Scope statement, read this before anything else.** Nothing in this document is
folded into the 17-run canonical store. `data/all_runs_inventory.csv` and
`renders/yaris_render_s1/gates_results_all_runs.json` remain Yaris-only and were
not touched. Every result below is NON-CANONICAL and is reported as a companion
experiment, not as an extension of the gated set. Folding additional vehicle
classes into the canonical store is a scope decision for a human, not a
consequence of this document.

Everything below was read live from Vista this session, not carried from a prior
summary. Where a claim is external or unverified it says so.

---

## 1. Hull provenance and sha256

Two hulls, both watertight, both confirmed through the same `load_vehicle` branch
the canonical Yaris uses.

| vehicle | file | sha256 |
|---|---|---|
| Rogue | `rogue_g96_pd8_coarse_watertight.ply` | `c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2` |
| Silverado | `silverado_g96_pd8_coarse_watertight.ply` | `46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9` |

**Two paths, one file each.** The two jobs cite the hulls at different paths:
job 896273 reads `$WORK/hulls/`, the multigeom run reads
`$WORK/can-it-ford/vehicle_geometry_research/`. Verified live 2026-08-11 by
`sha256sum` over all four paths: the digests are pairwise identical, so these are
the same two meshes under two paths and no run used a different mesh than it
reported.

Both are real FE vehicle decks, not primitives. Per register E6a and E8 these are
CCSA / George Mason hosted models. Two provenance cautions carry forward
unchanged:

- **Licence is a blocker, not a footnote (register E8).** CCSA-hosted decks
  (E8 names Rogue, Ram, 2014 Silverado) are licence-silent, unlike NHTSA-hosted
  copies. The operative rule stands: do not commit derived NCAC/CCSA geometry to
  the public repo and do not put it in a DesignSafe DOI without written
  permission. **No `.ply` was committed by this session.** Only the numeric
  results CSV was.
- **Mass sourcing is asymmetric and must be labelled that way.** Silverado
  2270.0 kg is primary-sourced from the deck header
  (`silverado-coarse-v3a.key:28`). Rogue 1571.3 kg is WEB-SOURCED ONLY (2020
  Rogue FWD S curb weight 3464 lb, cars.com); the Rogue deck header states no
  mass at all. Do not present the Rogue mass as deck-derived.

**Register correction produced by this work.** Register E3 currently reads
"Rogue and Silverado meshes exist but never entered a simulation." That is now
STALE. Both meshes entered simulations on 2026-08-07 (job 896273) and
2026-08-08 (job 896302), evidenced by the provenance blocks and per-run
`summary.json` cited throughout this document. E3's other half, that the three
AR&R mass classes are one Yaris hull with mass overrides, is unaffected and still
governs the canonical 17.

---

## 2. The two datasets are different experiments, not replicates

This was the central question of the dispatch and the answer changes how both are
cited.

| | class-specific (job 896273) | multigeom (interactive) |
|---|---|---|
| output | `$WORK/class_specific_2026-08-08/` | `$WORK/render_s2/multigeom_2026-08-08/` |
| context | batch, host c642-002, 2026-08-07T23:16:40 | interactive node, host c642-011, 2026-08-08T00:15:08 |
| driver sha256 | `7236e474af6722...` | `4696c3b2d39f4e...` |
| Rogue mass | 1571.3 kg (primary) | 1609.0 kg (primary), 1571.3 as `mass_alt_kg` |
| Silverado mass | 2270.0 kg, deck header (primary) | 2337.0 kg, AR&R class figure; 2270.0 as `mass_alt_kg` |

**LABEL CORRECTED 2026-08-13.** The Silverado row previously called the multigeom
figure "2337.0 kg (primary)", which inverted the provenance hierarchy section 1
of this document already states. 2270.0 kg is primary: it is the vehicle's own
mass, verbatim from `silverado-coarse-v3a.key:28` ("version 3a, 2270 kg"), opened
directly on Vista. 2337.0 kg is the AR&R `large_4wd` **class threshold** from
`gates_both_scenarios.py`, recorded as such in the run's own `summary.json`
`mass_source` field; `vehicle_params.py:42-46` warns that the AR&R class keys and
the vehicle keys are separate taxonomies and not interchangeable. The 2.9 percent
figure below is therefore a gap between a vehicle mass and a class threshold, not
a disagreement between two candidate vehicle masses. No run, CSV or verdict
changes: every Silverado run is NO-FORD at 1100.0, 2270.0 and 2337.0 alike. Full
working, including the confirmation that this hull is the **2007** Silverado and
that register E8's licence blocker names the 2014 model instead, is in
`docs/SILVERADO_MASS_PROVENANCE_2026-08-13.md`.

**They agree exactly on every mass-independent quantity.** `dx`, `water_layers`,
`hull_m3`, `solid_volume_m3`, `fill_ratio` and the tripwire `hull_ref_delta_pct`
match to full printed precision across both datasets.

The **tripwire agrees exactly**: `+39.732019083137` (Rogue) and
`+124.74371141982881` (Silverado) in both. The tripwire exists to catch
`--vehicle` silently failing to take effect, in which case it would read about
0.000 and the run would be the Yaris hull mislabelled. It passes in both
datasets, so both genuinely loaded the hull they claim.

**They differ on every mass-dependent dynamic quantity**, because the masses
differ by 2.4 percent (Rogue) and 2.9 percent (Silverado). Displacement differs
by 4.1 percent (Rogue) and 7.6 percent (Silverado); yaw differs more.

**Consequence for citation.** These are not run-for-run replicates, so
"agreement within noise" is the wrong test and no averaging or picking between
them is defensible. `data/class_specific_runs_2026-08-08.csv` is primary. The
multigeom Rogue and Silverado runs are a **different-mass companion**, NOT a
regression check of it, and must not be described as confirming it.

**The genuine regression check is the third multigeom run.** `g64_yaris_regression`
(1100 kg, canonical Yaris hull, `dx` 0.1472147236519959) returns
`final_disp_mag_m` 0.6592952013015747 against the canonical g64_m1100
`summary.json` value 0.658537, a difference of +0.115 percent. That is a real
pass and it is what confirms the multigeom driver reproduces the canonical
pipeline.

---

## 3. CSV integrity

`data/class_specific_runs_2026-08-08.csv` (7 rows) was verified this session
field by field against the live `summary.json` it transcribes. Every value
matches to full precision, including `final_disp_mag_m`, `final_yaw_deg`,
`passthrough_max_frac`, `C2_veh_zmin_rise`, `realized_rho` and
`solid_volume_m3`.

- rows `class_rogue_g64`, `class_silverado_g64` (job 896273) trace to
  `$WORK/class_specific_2026-08-08/<label>/summary.json`
- rows `hull_{rogue,silverado,yaris}_dxm` and `hull_{rogue,silverado}_g96`
  (job 896302) trace to `$WORK/render_s3_hullsweep/<label>/summary.json`

Two defects found and recorded rather than silently fixed:

1. The dispatch's prescribed commit message attributed the whole file to job
   896302. The two g64 rows carry `job_id` 896273 and come from a different job
   and a different driver. The committed message names both.
2. The file is hidden by `.gitignore:10` (`data/*`) and required `git add -f`.
   This is the same trap that kept `all_runs_inventory.csv` invisible until
   841d666. No script in the repo writes this CSV by name, so its generation step
   is currently unreproducible; that is an open provenance gap.

**Update 2026-08-11: the gap is now closed by a RECONSTRUCTION, and the original
is gone.** `analysis/build_class_specific_inventory.py` rebuilds the CSV from the
seven `summary.json` files and reproduces the committed bytes exactly, verified by
its own `--check` mode. Read that as regenerability restored, not as provenance
recovered. The original generator was not found and on the evidence never existed
as a committed artifact: a live search of the repo including the gitignored
`renders/` and `data/` trees returned nothing, and two of the CSV's columns hold
hand-authored English prose that no `summary.json` field supplies, which points at
hand assembly or a scratch script. The reconstruction says so in its own docstring.
It must not be cited as the original.

Reconstructing it did surface the derivation rules, which were nowhere written
down, and one is a live trap:

- `P3_float` is `abs(C2_veh_zmin_rise) <= 0.01` (`gates.py:151`), an **absolute**
  value, so a hull that SANK fails it exactly as one that rose would. Three of the
  seven rows carry a small negative rise that passes. A plausible-looking
  `rise < 0 means fail` rule flips those three and is wrong.
- `P2_passthrough` is a strict `< 0.10` (`gates.py:148`).
- `tripwire` is the hull-provenance check that `--vehicle` took effect, against the
  per-vehicle `yaris_ref_delta_pct` documented at `sim_standing.py:417-419`
  (about 0 Yaris, +39.7 Rogue, +124.7 Silverado).
- `verdict` is `final_disp_mag_m > 0.05`. That 0.05 is the internal onset-of-motion
  tolerance with no peer-reviewed source, declared 24 times under five names across
  the repo (register D7, count resolved 2026-08-11). Not a cited physical threshold.
- The committed file is **CRLF**. Regenerating with `\n` differs by exactly 8 bytes
  and a line-by-line diff shows nothing, so byte comparison is the only check that
  catches it.

---

## 4. Canonical-g64 free-rigid results, with caveats

Depth 0.30 m, velocity 1.5 m/s, `n_grid` 64, floor friction 0.55, 90 frames.

| run | mass (kg) | dx (m) | water layers | disp (m) | P-2 | P-3 | verdict |
|---|---|---|---|---|---|---|---|
| `class_rogue_g64` | 1571.3 | 0.16316 | 4 | 0.71096 | PASS (0.0995) | **FAIL** | NO-FORD |
| `class_silverado_g64` | 2270.0 | 0.20419 | 3 | 0.34981 | PASS (0.0839) | PASS | NO-FORD |

**Caveats that must travel with these two numbers.**

- **Rogue fails P-3.** `C2_veh_zmin_rise` is -0.022170 m: the hull sank into the
  floor plane rather than rising. This is the same failure signature the three
  g48 canonical runs show. The displacement magnitude from a run whose hull
  penetrated the floor is not trustworthy.
- **Silverado is depth-degraded.** 3 water layers against the canonical 4. Per
  L-3 the canonical g64 baseline is already only 4 particle layers and exactly
  2 grid cells across the water depth, well under the roughly 10-per-depth rule
  of thumb, and 3 layers is worse. This is the least resolved run in the set.
- Neither run exceeds the 10 percent passthrough gate, unlike 7 of the canonical
  17, but both sit close to it.
- **Report the verdict, not the magnitude.** Both are NO-FORD. That is the
  citable result. Section 5 is the reason the displacement numbers are not.

---

## 5. Matched-dx result: corroboration for the convergence contribution

`n_grid` is not resolution. `grid_lim` is derived from the loaded hull's extent,
so a fixed `n_grid` gives each vehicle a different `dx` and a different realized
water depth. Job 896302 therefore ran two arms at a common mass of 1100 kg: one
holding `n_grid` fixed at 96, one matching `dx` across vehicles.

**Arm A, matched dx (spread 0.38 percent across the three vehicles):**

| vehicle | n_grid | dx (m) | layers | disp (m) | P-2 |
|---|---|---|---|---|---|
| Yaris | 96 | 0.0981431 | 6 | 0.27086 | PASS (0.0968) |
| Rogue | 106 | 0.0985145 | 6 | 0.69199 | **FAIL** (0.1230) |
| Silverado | 133 | 0.0982551 | 6 | 0.33538 | **FAIL** (0.1058) |

**Arm B, fixed n_grid 96:**

| vehicle | n_grid | dx (m) | layers | disp (m) | P-2 | P-3 |
|---|---|---|---|---|---|---|
| Yaris | 96 | 0.0981431 | 6 | 0.27086 | PASS | PASS |
| Rogue | 96 | 0.1087764 | 6 | 0.93640 | **FAIL** (0.1209) | **FAIL** (-0.02449) |
| Silverado | 96 | 0.1361243 | 4 | 0.23503 | PASS (0.0929) | PASS |

**The finding.** Refining `dx` at fixed mass moves displacement in **opposite
directions** for the two vehicles:

- Rogue: `dx` 0.108776 to 0.098514 (a 9.4 percent refinement) moves displacement
  0.93640 to 0.69199, **-26.1 percent**.
- Silverado: `dx` 0.136124 to 0.098255 (a 27.8 percent refinement) moves
  displacement 0.23503 to 0.33538, **+42.7 percent**.

For reference, the Yaris on the same driver moves -58.9 percent from its g64
`dx` 0.147215 to its g96 `dx` 0.098143, which reproduces the -59.2 percent
already recorded for the canonical g64-to-g96 step at 1100 kg.

**Why this matters.** The existing Yaris contribution is that the binary verdict
is grid-invariant while the displacement magnitude is not, non-monotonically so.
That result rested on one hull. These two additional hulls reproduce it and
strengthen it: the magnitude is not merely unconverged, the **sign of the
resolution error is vehicle-dependent**, so no single grid-correction factor
could be applied across vehicles even in principle. Every one of the seven runs
returns NO-FORD regardless of arm or resolution, so the verdict is invariant here
too.

Steffen, Kirby and Berzins 2008 remains the citable mechanism for MPM losing
convergence under grid refinement at fixed particles-per-cell (register / L-5).

**Do not overread this.** Three of the six non-Yaris rows fail the 10 percent
passthrough gate and one fails P-3, so these are corroboration of a known
limitation, not a converged cross-vehicle comparison. Both class-specific
densities (316.78 and 285.76 kg/m3) and both 1100 kg matched-dx densities
(223.23 and 138.24 kg/m3) differ from the canonical Yaris 310.494 kg/m3, so mass
and density are not controlled across vehicles either.

---

## 6. SDF-collider cross-check: BLOCKED, no job submitted

The dispatch asked for one Vista job putting both hulls through the SDF-collider
path, conditional on the harness accepting a mesh path, and instructed a stop if
it is not. **It is not. Step stopped, nothing submitted, no SUs spent.**

Verified live 2026-08-11 by direct read of
`simulation/validate_coupling_force.py`:

- The only geometry constructor is `cube_mesh(length)` at line 115, which returns
  a hardcoded 8-vertex, 12-triangle axis-aligned cube centred on the origin.
- `build_box_sdf(length, dx, res, band_safety)` at line 162 feeds exactly that
  cube to `warpmpm.geometry.build_sdf`.
- `run_c1_sdf(n_grid, rho_box, depth_cells, box_bottom_cells, settle_frames,
  measure_substeps, collider, sdf_res, device, seed)` at line 705 has **no mesh
  parameter**.
- `main()` exposes `--collider {sdf,box}` and `--sdf-res` but **no `--mesh`,
  `--hull` or `--vehicle`**. `--collider` selects between a mesh-SDF *of that
  cube* and an axis-aligned primitive; both are the same analytic cube.

`simulation/box_sdf_collider_setup.py` is likewise closed: it hardcodes
`BOX_DIMS_M = (4.66, 1.79, 1.44)` and builds through `trimesh.creation.box`,
with no mesh path argument. (That extent is also the pre-Yaris placeholder
flagged in register E7, 3.391x the canonical hull volume.)

**What has to happen first.** The harness needs a mesh-loading path that reuses
the same `load_vehicle` branch the gated driver uses, so that the SDF collider
and the free-rigid body are demonstrably the same geometry. Writing that is a
code change with its own validation burden and was deliberately not attempted
here.

**Why the SDF path is the architecturally correct comparison.** The 17 canonical
runs use the material-8 free-rigid path, in which the body adopts a mass-weighted
average of grid velocity and **no force is ever formed**, so any force is a
back-computation rather than a measurement. A collider does accumulate
`sum m*(v_free - v_new)` before overwriting node velocity and divides by `dt`,
which is an actual contact-force accumulator. Hu, Fang, Ge, Qu, Zhu, Pradhana and
Jiang (2018), "A moving least squares material point method with displacement
discontinuity and two-way rigid body coupling," *ACM Transactions on Graphics*
37(4), 1-14, doi:10.1145/3197517.3201293, describes genuine two-way MPM/rigid
coupling as requiring accumulated contact force rather than velocity averaging.
Pazouki, Jayakumar and Negrut 2016 is cited in the same role in the register.

**Citation status:** the Hu et al. author list, title, venue, volume, pages, year
and DOI above were verified live 2026-08-11 against the Crossref record for
10.1145/3197517.3201293. The register's shorthand for this paper is "Compatible
Particle-In-Cell"; CPIC is the technique introduced in it, not its title, so cite
the title above. The Pazouki 2016 entry is carried from the register and has
**not** been checked against a primary record.

**What this does and does not change.** It reclassifies the coupling defect from
an unexplained numerical patch to a documented architecture choice with a
literature-backed alternative. It does not change any of the 17 runs' verdicts
and it does not clear them, for the three reasons already on record: the 17 runs
use restitution 0.05 on floor and walls where C1 used 0.0 everywhere, the depth
resolution is 2 grid cells, and self-consistency is not validation. The
validated SDF buoyancy comparison remains 7.3 to 7.7 percent against analytic.

---

## 7. Open items this work leaves

1. Register E3 needs the correction in section 1 applied.
2. `data/class_specific_runs_2026-08-08.csv` has no generating script in the
   repo. Its rows are verified against Vista, but the transcription step is not
   reproducible.
3. The SDF harness mesh path in section 6 does not exist and is the blocker for
   any hull-based coupling cross-check.
4. The Rogue mass remains web-sourced only.
5. Register E8's licence question is unresolved and gates any publication of
   derived geometry.

---

## 8. Frame renders of the multigeom runs, added 2026-08-11

NON-CANONICAL, same scope statement as the top of this document. Nothing here
enters the 17-run gated store. `data/all_runs_inventory.csv` and
`renders/yaris_render_s1/` were not touched.

### Which script rendered these

`analysis/render_multigeom_rollout.py`, written this session because nothing
existing could do it. Checked live before writing, not assumed:

- `render_frames.py` accepts an arbitrary `--input` path but not this schema. Its
  `_first_key` matches the 0-d scalar key `frames` as though it were a position
  array, and `_ensure_TN3` then raises
  `ValueError: Expected positions shape (T,N,3) or (N,3), got ()`. Reproduced by
  running it, not inferred from reading. It also has no vehicle path at all, only a
  static `--box-center` / `--box-size` proxy.
- `render_hero_shot.py` is a Blender `bpy` single still that reads `pos` / `vel` and
  draws a hardcoded 0.85 x 0.55 x 0.50 m cube with no rigid transform.
- `~/Downloads/render_frames_pyvista.py` COULD NOT BE READ. macOS TCC denies this
  process: `EPERM` on the read tool, `/usr/bin/grep`, `wc` and `cp`; only `ls`
  metadata succeeds. It is neither confirmed nor ruled out as a candidate.
- The seven renderers under `renders/yaris_render_s1/` (`render_flood.py`,
  `render_pv.py`, `render_pv3.py`, `render_pv_fixed.py`, `render_realistic.py`,
  `t1_car.py`, `render_hero_g64_m1100_2026-08-06.py`) all draw the vehicle as a
  shaded mesh from a hardcoded Yaris `.ply` (`t1_car.py:17`,
  `render_hero_g64_m1100_2026-08-06.py:47`, `render_flood.py` via `geom_live`).
  Neither non-Yaris `.ply` exists on this machine, and register E8 forbids
  committing derived CCSA geometry. Four of the seven additionally need `pyvista`,
  which is absent from all seven project venvs probed.

The vehicle is therefore drawn from `veh_particles_scene0`, the rigid particle cloud
already inside the npz. No mesh is loaded and no geometry was copied off Vista.

### The transform was reused, not rewritten

Verbatim from `gates.py`, the script that produces the published gate verdicts:

    pv    = (veh_particles_scene0 - t[0]) @ R[0]     gates.py:136
    vp(f) = pv @ R[f].T + t[f]                       gates.py:157

Deriving `pv` from the scene checkpoint rather than from `veh_particles_vehframe` is
what makes the body-frame offset of `t1_car.py:49-58` unnecessary. The script
verifies the reconstruction against the stored `veh_check_45` and `veh_check_last`
every run and aborts above 1e-4 m. Measured max absolute reconstruction error:

| run | max abs error |
|---|---|
| `g64_yaris_regression` | 1.287e-06 m |
| `g64_rogue` | 9.566e-07 m |
| `g64_silverado` | 2.221e-06 m |

Two axis facts a naive render gets wrong, both confirmed live. The hull's long axis
is Y, so the car profile is the (y, z) plane; an (x, z) "side view" shows the
vehicle's WIDTH and makes any hull look like a tall blob. And the npz scalar `floor`
is the ground plane `3.0 * dx` (`sim_standing.py:164`, used as the domain lower bound
at `:253`), not the vehicle z-min, though the two coincide for a hull at rest.

### Outputs, local only, not committed

90 PNG frames plus one mp4 each. `fps` 30 was read from the npz, not assumed.

| run | frames | fps | mp4 | size | duration |
|---|---|---|---|---|---|
| `g64_rogue` | 90 | 30 | `renders/multigeom_2026-08-08_render/g64_rogue/g64_rogue_multigeom_2026-08-08.mp4` | 1,921,327 B (1.83 MB) | 3.000 s |
| `g64_silverado` | 90 | 30 | `renders/multigeom_2026-08-08_render/g64_silverado/g64_silverado_multigeom_2026-08-08.mp4` | 1,451,596 B (1.38 MB) | 3.000 s |

Both are h264, 1800x1080. Each output directory also carries a `render_manifest.json`
recording the transform errors, the floor plane, the z-min trajectory endpoints and
the exact caption text.

### Caption caveats, and one correction to the prescribed text

Every caption is generated from that run's OWN `summary.json`. Nothing is retyped and
nothing is taken from another run's row. That distinction is load-bearing here,
because the runs rendered are NOT the rows in
`data/class_specific_runs_2026-08-08.csv`. Per section 2 those are a different
experiment at a different mass, and the CSV holds no row for the multigeom runs.

| quantity | `class_rogue_g64` (CSV, job 896273) | `g64_rogue` (rendered, multigeom) |
|---|---|---|
| mass | 1571.3 kg | 1609.0 kg |
| `C2_veh_zmin_rise` | -0.022170 m | -0.022017 m |
| `final_disp_mag_m` | 0.710959 m | 0.682727 m |
| `passthrough_max_frac` | 0.099493 | 0.098428 |

**The prescribed Rogue caption value -0.02217 m belongs to the CSV run, not the
rendered one.** The rendered run's own value is -0.022017 m. Both fail P-3, so the
verdict is unchanged; the attribution is not.

**"Sank into the floor plane" is wrong for the rendered Rogue run and was not used.**
Measured from the verified transform: hull z-min starts 29.095 mm ABOVE the floor
plane, reaches it at frame 2 (t = 0.067 s) and stays there for the remaining 87
frames. Deepest excursion below the floor across all 90 frames is -7.1e-08 m, zero to
float32. The hull settled ONTO the floor plane; it did not penetrate it. The caption
says so.

**The gate's C2 rise is not the drop visible in the video.** `zmin_start` is sampled
at `sim_standing.py:445`, before the frame loop, and the loop calls `scene.step()` at
`:448` before recording the frame-0 checkpoint, so C2 spans one solver step more than
the 90 rendered frames. For the Rogue the hull rises 7.078 mm in that first step and
then falls 29.095 mm across the rendered frames, netting the -22.017 mm the gate
reports. The rendered drop is 32 percent larger in magnitude than the gate rise and
neither number is wrong. The caption states both and names the mechanism.

The Silverado caveat is carried unchanged, because water layers is a mass-independent
quantity and section 2 already establishes those match across both datasets. 3 water
layers against the canonical 4, verified in this run's own `summary.json`, and the
minimum across all seven CSV rows. Per L-3 the canonical g64 baseline is itself only
4 particle layers and exactly 2 grid cells across the water depth.

### What the renders show

- **Rogue.** The floor-sink is real but is a two-frame initial settling transient,
  not a progressive sink, and 29 mm on a 1.73 m hull is not perceptible in the main
  view. It is legible only in the magnified underside panel and the z-min trace,
  which is why the figure carries both. Passthrough is visible in the profile panel
  as water inside the hull silhouette, consistent with its 0.0984 fraction sitting
  just under the 0.10 gate.
- **Silverado.** Reads as a pickup with a distinct cab and bed, and sits on the floor
  plane for all 90 frames (z-min varies by 3e-4 mm, float32 noise). P-2 0.0834 and
  P-3 -0.00030 m both pass. Nothing anomalous.
- Both: water reads as one connected body, no particles outside the domain, motion
  continuous across frames.

### Solid-surface variant, added the same day

`--vehicle-style mesh` (now the default) draws the vehicle as a shaded closed
surface instead of a particle scatter. `--vehicle-style points` keeps the original.
The surface is reconstructed from the SIMULATED rigid particles, so it shows the
body the solver actually integrated, at the resolution it integrated it. No `.ply`
is read and no geometry was copied off Vista, so register E8 is not engaged.

Method: occupancy lattice of the body-frame particle cloud, dilated by the particle
half-cell, lightly smoothed, then marching cubes, decimated to 9000 faces. Built
ONCE in the body frame because the body is rigid, then transformed per frame by the
same verified `gates.py` pose. Two calibrations were needed and both are measured,
not asserted:

- **Offset.** `summary.json solid_volume_m3` equals `n_particles * h**3` to five
  significant figures in all three runs (Yaris 8905 * 0.07360736^3 = 3.5512 against
  3.551384), so each particle is a cube of side `h` and the true boundary sits at
  `particle_extreme + h/2`. Marching cubes at level 0.5 lands half a grid cell
  beyond the outermost occupied cell centre, so the dilation radius must be
  `r = upsample/2 - 0.5`, integer only for odd `upsample`. Default is 3.
- **Faithfulness.** Enclosed volume against the solver's own `solid_volume_m3`:

| run | surface volume | solver `solid_volume_m3` | error |
|---|---|---|---|
| `g64_rogue` | 4.951871 m3 | 4.960170 m3 | **-0.17 %** |
| `g64_silverado` | 7.967135 m3 | 7.943659 m3 | **+0.30 %** |
| `g64_yaris_regression` | 3.479583 m3 | 3.551384 m3 | -2.02 % |

Every particle lies inside the reconstructed surface's bounding box in all three
runs, and the per-axis margins land on the `h/2` target (Rogue target 0.0408 m,
measured 0.0366 to 0.0465).

Three defects were found and fixed during this, recorded because each would have
been invisible in the finished frames:

1. First reconstruction blurred the bare particle lattice and normalised by the
   field maximum. That ERODED the extremities, putting 209 of the Yaris hull's 8905
   particles outside the surface and lifting the rendered underside off the floor.
   Floor contact is the one thing these frames are read for, so the enclosure check
   now runs every time and warns.
2. Second reconstruction overshot the other way, +57 mm on every axis against a
   36.8 mm target, which would have drawn the hull sunk 20 mm INTO the floor and
   reproduced by accident the very artifact section 8 corrects.
3. Back-face culling tore holes in the 2D silhouette, because faces near-tangent to
   the view have an ill-conditioned normal and the centroid-outward orientation fix
   is unreliable inside the wheel arches. Replaced with a plain painter's sort over
   every face. `t1_car.py`'s 0.30-of-height wheel threshold also painted black
   wedges up to 0.85 m on the Yaris and was tightened to 0.18.

Outputs, local only, alongside the point-style versions rather than replacing them:

| run | frames | fps | mp4 | size | duration |
|---|---|---|---|---|---|
| `g64_rogue` | 90 | 30 | `renders/multigeom_2026-08-08_render/g64_rogue_solid/g64_rogue_solid_multigeom_2026-08-08.mp4` | 1,362,958 B (1.30 MB) | 3.000 s |
| `g64_silverado` | 90 | 30 | `renders/multigeom_2026-08-08_render/g64_silverado_solid/g64_silverado_solid_multigeom_2026-08-08.mp4` | 1,013,777 B (0.97 MB) | 3.000 s |

The solid hulls read as blocky, and that is the honest result rather than a
rendering fault: the Silverado's particle lattice is `h = dx/2 = 0.10209 m`, so a
5.94 m truck is about 58 particles long. Smoothing it further would hide the
resolution the verdicts were computed at.

This changed no verdict, no gate and no number in sections 1 to 7. It is a display
path only. It also required `scikit-image`, `scipy` and `fast_simplification` in
`~/.venvs/canitford-mpm`, which were installed this session and are not otherwise
used by the repo.
