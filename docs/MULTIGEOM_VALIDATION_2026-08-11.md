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
| Silverado mass | 2270.0 kg (primary) | 2337.0 kg (primary), 2270.0 as `mass_alt_kg` |

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
