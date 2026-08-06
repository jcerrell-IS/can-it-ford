# Can It Ford: Verified Facts Ledger
## July 24 2026. Supersedes all secondary summaries where they conflict.

**Rule this file exists to enforce:** a claim is only listed under VERIFIED if it was read
from primary source (a paper PDF, or the actual code file) or derived by arithmetic from
one. DeepWiki output, Perplexity reports, prior session summaries, and this project's own
markdown docs are HYPOTHESES, not sources. Two claims were retracted on July 24 for
exactly this reason.

---

## CORRECTIONS APPLIED ON INTAKE, 2026-07-24

This file was audited against a live read of
`citations/ARR_Project_10_Stage2_Report_Final.pdf` and against the repo on disk before
being committed. Corrections are marked inline as **[CORRECTED]**, **[FILLED]**, or
**[FLAG]**. Nothing was silently changed.

| ID | Section | What changed |
|---|---|---|
| D1 | A3, E | "clearly non-conservative" was attributed to Table 3. The source applies it to the PRE-EXISTING guidelines and offers Table 3 as the revision. Load-bearing, propagated to Section E |
| D2 | A3 | The "interim, informal values" quote is item 1 of a numbered proposal list, not a standalone disclaimer |
| D3 | A1, G2 | Large passenger and Large 4WD boundary cells were blank. Now read and filled |
| D4 | A5 | Yaris length 4.2826 m conflicts with `paper_draft.md:33` which states 4.30 m. Unresolved, decides the class |
| D5 | A5 | Kerb weight 1100 kg conflicts with `paper_draft.md:33` which states 1078 kg. Does not change the verdict |
| D6 | A11 | Was one commit stale. HEAD is now `85e2252`, not `af1db6d` |
| D7 | A9, A10 | Sit under "VERIFIED AT PRIMARY SOURCE" but were not independently reproduced this pass. Provenance downgraded |
| F-1 | F1 | Two byte-identical duplicate meshes in the nested `can-it-ford/can-it-ford/` tree were unlisted. Added |
| F-2 | F1 | `truck_trimmed.ply` is present in THIS repo at `data/`, 45.20 MB, and is UNTRACKED by git |

**Second pass, same day, after review:**

| ID | Section | What changed |
|---|---|---|
| D1b | A3, E | A3 rewritten to carry the source's full three-part argument in order, with the pre-2011 referent named explicitly and the "Such a revision... is suggested below" sentence retained as the fixing context. Section E reframed to the accurate and stronger claim: the authors found the then-current guidelines non-conservative, proposed Table 3 as an interim draft revision, and asked for further testing |
| D8 | A9 | "68 percent over-fill" had no named basis and is wrong under both readings. Now states both explicitly: 67.8 percent OF the 11.348 m3 bounding box, and +117 percent OVER the 3.5427 m3 hull (2.17x). The displacement-relevant figure is the hull one |

**Verified correct on this pass, no change needed:** A1's Small passenger row and all
quotes, A2, A4 in full, A6, A8's line reference, A11's numbers, A12's commit hash,
F1's vertex and face counts, G3's FORD counts, G4's inclusivity finding.

---

## SECTION A: VERIFIED AT PRIMARY SOURCE

### A1. AR&R stability criteria (Shand, Cox, Blacka, Smith 2011, P10/S2/020, ISBN 978-0-85825-948-5)

Read directly from `citations/ARR_Project_10_Stage2_Report_Final.pdf`, Table 3,
PDF page 24 (printed page 14). Footnotes render on PDF page 9 (printed vii).

**[FILLED]** All boundary cells now read verbatim from Table 3.

| Class (verbatim) | Limiting still water depth | Limiting velocity | Equation of stability | Limiting high velocity flow depth | Length | Kerb weight | Ground clearance |
|---|---|---|---|---|---|---|---|
| Small passenger | 0.3 m | 3.0 m/s | DV <= 0.3 | 0.1 m | < 4.3 m | < 1250 kg | < 0.12 m |
| Large passenger | 0.4 m | 3.0 m/s | DV <= 0.45 | 0.15 m | > 4.3 m | > 1250 kg | > 0.12 m |
| Large 4WD | 0.5 m | 3.0 m/s | DV <= 0.6 | 0.2 m | > 4.5 m | > 2000 kg | > 0.22 m |

Column headers verbatim: `Length (m)`, `Kerb Weight (kg)`, `Ground clearance (m)`.

**[FLAG] The class bounds are open on both sides and do not partition the space.** There is
no upper bound on Large 4WD, and a vehicle between 4.3 m and 4.5 m satisfies Large
passenger only. The report gives no tie-break rule when length, weight, and clearance
disagree with each other. Do not present the three classes as a clean partition.

**Applied jointly, not as a single curve.** Table 3 footnotes: "1 At velocity = 0 ms-1;
2 at velocity = 3ms-1; 3 at low depth". The still-water depth binds at v=0, the DV equation
binds at low depth, and the high-velocity flow depth column binds at v=3.0. That fourth
column is internally consistent with DV/3.0 (0.3/3=0.1, 0.45/3=0.15, 0.6/3=0.2), so it is
the same envelope rather than a fourth independent constraint.

**Selection rationale, PDF p.24 verbatim:** "The experimental and analytical data can be
reasonably represented by either a linear relationship between D and V or a constant D.V
value... For consistency with the proposed human stability criteria, the constant DV
relationships... is preferred."

**The 3.0 m/s cap is real but its rationale is not vehicle stability.** PDF p.24 verbatim:
"These draft stability criteria all have limiting depths and a limiting velocity of
3.0 ms-1. This was incorporated to provide agreement with human stability criteria
presented within Cox, Shand and Blacka (2010) and to ensure that, in the event of vehicle
failure, safety was not compromised once people abandoned their cars." It is an evacuation
safety limit imported from human stability work, not a vehicle result. State it that way.

**Units caveat:** Table 3 cells print "DV <= 0.3" with no units. m2/s follows from D in m
and V in ms-1 used elsewhere in the table. That inference is not the report's own text.

### A2. Table 3 is titled "Proposed DRAFT Stability Criteria for Stationary Vehicles"

These are stationary-vehicle criteria. A stationary vehicle in flow is in scope. A vehicle
driving through, which is the literal "Can It Ford" framing, is an extension beyond the
source's stated scope and must be declared as such.

Note the executive-summary version of the same table (PDF p.9, printed vii) carries a
different title: "Proposed DRAFT INTERIM criteria for stationary vehicle stability". Both
support the stationary-scope point.

### A3. **[CORRECTED]** What the report found non-conservative, and about which criteria

The previous version of this section was headed "The report disclaims its own numbers" and
asserted that the authors call Table 3 non-conservative. **That is a misattribution.** Both
quotes are verbatim, but neither says what the section claimed. The corrected reading is
not weaker, it is a different and more useful claim.

**The three-part structure of the source's own argument, PDF p.24, in order:**

1. **Why the pre-2011 guidelines fail.** Verbatim: "On the basis of changes in modern
   vehicle design, the limited nature of the earlier experimental work and the lack of
   calibration in computational studies, it is unlikely that the earlier results are
   directly applicable and conservative when applied to modern vehicles."

2. **The finding, and its subject.** Verbatim, with the following sentence included because
   it is what fixes the referent:

   > "In the interim, however, the existing AR&R guidelines are clearly non-conservative
   > and revision of the criteria should be considered until further testing is
   > undertaken. **Such a revision to provide Draft interim criteria for stationary vehicle
   > stability is suggested below.**"

   "the existing AR&R guidelines" means the **pre-2011** guidelines in force at the time of
   writing. Table 3 IS the revision suggested in the very next sentence. The authors found
   the then-current guidelines non-conservative and offered Table 3 as the interim fix.

3. **What they asked for next, PDF p.9.** A five-point program of full-scale testing,
   frictional-coefficient measurement, computational-model calibration, and field
   verification, introduced by "To provide robust and accurate criterion, we propose that:".
   Item 1 of that list, which is a recommendation for adoption and not a standalone
   disclaimer **[D2]**:

   > "1. The draft stability criteria presented below are adopted as interim, informal values;"

   And the closing condition, verbatim: "Only criteria developed in such a rigorous way are
   suitable for presenting as true safety guidelines."

**What this licenses.** That the AR&R authors found the guidelines then in force to be
non-conservative, proposed Table 3 as an explicitly interim draft revision, and stated that
further full-scale testing and calibration was required before any such criteria could be
presented as true safety guidelines.

**What does NOT survive:** any sentence of the form "the AR&R authors called their own
Table 3 criteria non-conservative." They said that of the guidelines Table 3 replaces. Do
not write the unqualified version on a poster or in a paper.

### A4. Flow regime behind the AR&R curves: NOT STATED

Strings `steady`, `unsteady`, `surge`, `dam-break`, `transient` appear zero times in the
report. Extraction verified complete (94,042 characters; control term "stability" appears
87 times). The closest available, both describing cited source studies rather than the
criteria derivation:

- Bonham & Hattersley 1967, PDF p.15: model Ford Falcon, 1:25 geometric scale, restrained
  by fine threads, perpendicular flow on a causeway, "46 different combinations of depth
  and velocity" with depth 0.11 to 0.57 m and velocity 0.48 to 3.09 ms-1 (prototype scale)
- Keller & Mitsch 1993, PDF p.19: "Flow depth was incrementally increased from 0.025 m to
  0.4 m. At each depth, vertical reaction forces at the front and rear axle were evaluated
  separately"

Both read as incremental and quasi-static, but the report does not label the regime. Any
claim that AR&R was calibrated on steady flow is UNSUPPORTED by this source. The honest
statement is that the source does not specify, and its underlying experiments were
incremental.

### A5. Yaris class assignment against the primary-source boundaries

The report never mentions a Yaris. It names Corolla, Falcon, Landcruiser, Swift, Laser,
LTD, Mini. Testing the canonical hull against Small passenger boundaries:

| Boundary | Yaris value | Result |
|---|---|---|
| Length < 4.3 m | 4.2826 m **[FLAG, contested]** | PASS by 0.0174 m, IF 4.2826 is right |
| Kerb weight < 1250 kg | 1100 kg **[FLAG, contested]** | PASS either way |
| Ground clearance < 0.12 m | **UNKNOWN** | must be measured from the hull |

**[FLAG] D4, the length is contested and it decides the class.** This ledger says 4.2826 m.
`paper_draft.md:33` says "4.30 m Toyota Yaris". 4.2826 passes `< 4.3`; 4.30 does not. The
margin is 1.7 cm. Neither figure was reproduced from the mesh on this pass. Measure the
bounding box from `yaris_coarse_v1l_watertight.ply` before asserting Small passenger.

**[FLAG] D5, the mass is contested but does not change the verdict.** This ledger says
1100 kg, matching `vehicle_params.py`. `paper_draft.md:33` says "real 1078 kg". Both pass
`< 1250 kg`, so the class is unaffected, but the project still carries two numbers.

Ground clearance is not derivable from a bounding box, and published clearance for a real
2007-2011 Yaris is roughly 0.135 m, which would fail the 0.12 m boundary. That published
figure is secondary and unverified. Measure it from the mesh before asserting the class.

### A6. kks32/mpm-engine: add_plane friction IS applied to slip surfaces

`kernels/mpm_solver_warp.py:1974-1988`. The friction block at line 1983 sits at the same
indentation as the `surface_type` if/else at 1975/1979, so `param.friction` is read for
slip (type 1) and separable (type 2) alike. `floor_friction` reaches
`collider_param.friction` at line 1912 and is used at 1985.

The "slip (frictionless)" comments at `kernels/warp_utils.py:245` (a struct field comment)
and `kernels/mpm_utils.py:807` (the CDF collider ghost-velocity path, where slip genuinely
is frictionless) describe a different code path than `add_plane`.

Corroborating: `test_restricted_launch.py:26,60`, `test_cuda_graph.py:31`,
`test_sparse_blocks.py:33,59` all pass friction=0.2 to slip planes.

`vehicle.py:313` is correct code. There is no bug here.

Re-verified line by line on 2026-07-24 against the installed package at
`/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/`. Note the nested repo copy numbers
the same call at `vehicle.py:281`; cite the installed package.

### A7. kks32/mpm-engine: add_sdf_collider IS kinematic

Velocity and omega are written from arguments only, at `mpm_solver_warp.py:2668-2669`
(creation) and `2810-2813` (`set_sdf_pose`). The wrench is a write-only accumulator:
allocated zeroed at 2675-2676, accumulated at 2733-2734, read only by `solver.py:353-355`.
Decisive negative grep: no `velocity +=`, `omega +=`, or assignment from force/torque/
wrench anywhere in the package.

Separate mechanism, do not confuse: particles with material `"rigid"` DO get a real body
state via `solver.py:187-204` (`finalize_rigid_bodies`, `rigid_state` exposing
`rigid_v_cm`, `rigid_omega`). That is the FloodScene path and it does free 6-DOF motion.

**Consequence:** `simulation/box_sdf_collider_setup.py` cannot produce a ford verdict by
displacement. It is a force probe on a fixed obstacle. Retired from the verdict path.

**[FLAG]** Not independently re-verified on this pass. Line numbers carried forward from
the originating session.

### A8. FloodScene throws the mesh away before solidifying

`vehicle.py:162`: `pos = np.asarray(mesh.sample(60_000), ...)`. Stored as `surface` at :186.
`solidify` rebuilds from exactly that at :108. Confirmed live at 60,000 points.

Line 162 re-confirmed live on 2026-07-24: `pos = np.asarray(mesh.sample(60_000), dtype=np.float64)`.

The canonical hull's 327,212 vertices and 655,308 faces never reach the solidifier (both
counts independently confirmed from the PLY header, see F1). By the time column fill runs,
the watertight Yaris hull and `truck_trimmed.ply` are both 60k surface point clouds.
Watertightness cannot protect against the hollowing failure mode.

### A9. Solidified volume vs grid resolution, measured

**[FLAG] D7: not reproduced on this pass.** These numbers were produced in an earlier
session and are carried forward. They are the most load-bearing unverified block in this
file. Consequence 2 below is an INTERPRETATION of the trend, not a measurement, and the
table's own note flags `n_grid=192` as contaminated. A dedicated test (raise
`mesh.sample()` well above 60,000, re-run the resolution probe, revert) was specified to
settle convergence versus sampling artifact and has NOT been run.

`ext = (1.7461, 4.2826, 1.5175)`, `lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth) = 9.4217 m`
at depth 0.30. Bounding box 11.348 m3. Trimesh hull volume 3.5427 m3 (31.2 percent fill).

| n_grid | h (m) | solid_volume | % bbox | x hull vol | realized rho (1100 kg) | water layers @ 0.15/0.30/0.45 |
|---|---|---|---|---|---|---|
| 32 | 0.147 | 8.592 | 75.7% | 2.43x | 128.0 | 1 / 2 / 3 |
| **64 (default)** | ~~0.074~~ 0.0736074 | ~~7.698~~ **3.5514** | ~~67.8%~~ **31.3%** | ~~2.17x~~ **1.0024x** | ~~142.9~~ **309.74** | 2 / 4 / 6 |
| 96 | ~~0.049~~ 0.0490716 | ~~7.096~~ **3.5218** | ~~62.5%~~ **31.0%** | ~~2.00x~~ **0.9941x** | ~~155.0~~ **312.34** | 3 / 6 / 9 |
| 128 | 0.037 | 6.356 | 56.0% | 1.79x | 173.1 | 4 / 8 / 12 |
| 192 | 0.025 | 4.440 | 39.1% | 1.25x | 247.8 | 6 / 12 / 18 |
| hull truth | | 3.543 | 31.2% | 1.00x | 310.5 | |

Reference fill fractions from this project's own mesh notes: canonical v1l is ~32 percent
bbox with the underbody open (buoyancy-correct); the deprecated sedan hull was ~62 percent
with the underbody bridged shut (overstates displacement).

**[SUPERSEDED 2026-07-29, method replaced, not a corrected arithmetic error.]** Every
`solid_volume`, `% bbox`, `x hull vol` and `realized rho` figure in the table above was
measured under the **column-fill** solidify path, which fills wheel wells and window
openings into the solid by design. That path has been replaced by `solidify_watertight`,
which does not overfill. The `n_grid=64` and `n_grid=96` rows have been struck through and
corrected above, because `solidify_watertight` runs exist at those two resolutions. Rows
32, 128 and 192 are left as the historical column-fill record: no `solidify_watertight`
run exists at those resolutions, and their values have NOT been interpolated or estimated.
Note that `n_grid=48` has live values (below) but no row in the table above.

Live replacement values, read from `data/all_runs_inventory.csv` on 2026-07-29 (identical
across all 9 gated `n_grid=64` runs):

| n_grid | h (m) | solid_volume (m3) | fill_ratio | realized rho (1100 kg) |
|---|---|---|---|---|
| 48 | 0.0981431 | 3.6357101018957585 | 1.0262427183870328 | 302.55 |
| 64 | 0.0736074 | 3.5513843861695054 | 1.0024403113437104 | 309.74 |
| 96 | 0.0490716 | 3.5217987479492066 | 0.9940892478811469 | 312.34 |

`renders/from_vista/yaris_g64_m1100_d0p30_v1p5_dx0p090.PROVENANCE.txt` independently
records `solid_volume 3.550864656814358`, `h 0.07360652630115225` and `realized rho
309.78` for its own `n_grid=64` clip. That is a different run from the gated inventory
rows and the two disagree in the fifth significant figure; neither has been declared
canonical over the other. `paper/conference_101719.tex` Table II uses the inventory
values (302.6 / 309.7 / 312.3).

`analysis/plot_geometry_pipeline.py` plots the struck-through column-fill series from this
table and is therefore a historical diagnostic of the replaced method, not a current
result. It now refuses to run without an explicit acknowledgement flag.

**Three consequences.**

1. **[CORRECTED, basis named]** At `n_grid=64` the solidified body has volume 7.698 m3.
   State the over-fill against whichever basis you mean, and always name it:

   | Basis | Value | Figure |
   |---|---|---|
   | Fraction of the 11.348 m3 **bounding box** | 7.698 / 11.348 | **67.8 percent of bbox** |
   | Excess over the 3.5427 m3 **trimesh hull** | 7.698 / 3.5427 = 2.173 | **2.17x the hull, i.e. +117 percent over hull volume** |

   These are two different statements about the same number and they are not
   interchangeable. "68 percent over-fill" with no basis named is wrong under both
   readings: it is 67.8 percent OF the bounding box (not an excess), and the excess over
   the hull is +117 percent (not 68). The displacement-relevant figure is the hull one:
   every FloodScene run **under the column-fill path** used a body displacing **2.17x the
   hull's actual volume**. **[CORRECTED 2026-07-29]** The original wording, "every
   FloodScene run to date", is now false: the 17 runs in render_s2 listed in
   `data/all_runs_inventory.csv` were solidified with `solidify_watertight` and displace
   **1.0024x** the hull at `n_grid=64`, not 2.17x. Do not cite 2.17x, 7.698 m3 or
   142.9 kg/m3 as a property of any current run.

   For comparison on the bbox basis, this is a higher fill fraction than the deprecated
   sedan hull (~62 percent of bbox), which was deprecated for exactly that bias.
2. **[FLAG, interpretation not measurement]** The monotonic decrease is read as convergence
   toward the hull's true 31.2 percent rather than hollowing. The recorded "n_grid=128
   hollows the vehicle" dead end would then be a misdiagnosis when the asset is a
   watertight mesh. It may still be correct for `truck_trimmed.ply`, a genuinely sparse
   splat cloud. The competing hypothesis, that the decrease is a sampling artifact of the
   fixed 60,000-point surface sample, is NOT excluded by this table.
3. `n_grid=192` is the one contaminated point. Surface sample spacing is roughly 0.020 to
   0.024 m and h at 192 is 0.0245 m, so columns begin missing hits. Trust 32 through 128.

`rho = 310.47` is an asymptote as n_grid rises, not an achievable value. At the default
resolution the realized density is 142.9 kg/m3. Stop hand-deriving rho from a fixed hull
volume; read the runtime field.

### A10. Cost of raising resolution, corrected

**[FLAG] D7: not reproduced on this pass.** Carried forward from the originating session.

Earlier estimates used `lim = 14.99` from the wrong extent ordering and were wrong.

| n_grid | water pts | vehicle pts | total | substeps/frame | relative cost |
|---|---|---|---|---|---|
| 64 | 16,128 | 19,303 | 35,431 | 11 | 1.0x |
| 96 | 63,000 | 60,057 | 123,057 | 16 | 5.1x |
| 128 | 158,696 | 127,496 | 286,192 | 21 | 15.4x |
| 192 | 578,496 | 300,575 | 879,071 | 32 | 72.2x |

### A11. **[CORRECTED]** L1 implementation state, current at commit `85e2252`

D6: this section previously described state at `af1db6d` and is updated. Two commits exist,
both local to the Mac and NOT pushed as of this writing.

**`af1db6d`** "L1: apply AR&R depth and velocity caps jointly, fix generator output path".
Introduced `AR_R_STABILITY_LIMITS` and `L1_verdict(depth_m, velocity_ms, vehicle_class)`
applying depth cap, velocity cap, and D x V jointly, with only `small_car` populated.

**`85e2252`** "L1: populate all three AR&R presets from Shand et al. 2011 Table 3, make
vehicle_class explicit, emit small_car and four_wd sensitivity columns". All three presets
now populated and each field verified against Table 3. `--vehicle-class` is an explicit
argparse choice defaulting to `small_car`, no longer hardcoded.

Current CSV schema, 8 columns:

```
depth_m, velocity_ms, L0_verdict, L1_haz, L1_haz_product_only,
L1_verdict, L1_verdict_small_car, L1_verdict_four_wd
```

`L1_verdict` is retained deliberately: `analysis/build_poster_phase_space.py:35` reads it
directly and the poster build breaks without it. It tracks the chosen `--vehicle-class`.

Result, verified live: 25 of 70 rows changed verdict. L1 FORD count 37 -> 12. Every change
was FORD to NO-FORD; zero rows loosened. No surviving FORD row exceeds 0.30 m depth or
3.0 m/s. The "FORD at 1.0 m of standing water" case is closed.

**[FLAG] The default class disagrees with the rest of the project.** The generator defaults
to `small_car` (DV <= 0.30) while `README.md:23`, `analysis/make_phase_space_v2.py:9`, and
`analysis/wandb_backfill.py:24` all use Large 4WD at 0.60, and `paper_draft.md` computes
its divergence result at 0.60. The canonical 0.30 m / 1.5 m/s cell is one of the 12
class-sensitive cells: NO-FORD as small_car, FORD as four_wd. Unresolved.

Prior state, for the record: `analysis/make_phase_space_v2.py:9` and
`designsafe-staging/scripts/make_phase_space.py:9` both computed `'FORD' if h < 0.60` on a
bare D x V product with no depth cap.

### A12. Second bug found and fixed in the same commit

Commit `02ecf9c` moved CSVs to repo root. Hash confirmed live: `02ecf9c`, 2026-07-03,
"Move CSVs to root, add smoke tests, export script, sync automation, DesignSafe PRJ-6388
metadata, update figures". Not a phantom.

`scripts/gen_scenario_sweep.py` was never updated and had been writing to a nonexistent
`designsafe-staging/data/` path while `build_poster_phase_space.py`,
`build_phase_space_plotly.py`, `wandb_backfill.py`, and the schema test all read
`data/scenario_sweep.csv`. Now writes to `data/`.

---

## SECTION B: RETRACTED, PROVEN FALSE

### B1. "friction is silently ignored for surface='slip'"

**FALSE.** Disproved at source, see A6. Origin: a DeepWiki summary that conflated the
`add_plane` grid path with the CDF collider path. Consequences avoided: a pointless
`flood_scene_patched.py`, and a public and incorrect bug report on the PI's own repository.

### B2. "The AR&R 0.3 figure is a still-water depth, not a D x V product of 0.3 m2/s"

**FALSE.** The primary source states both, see A1. They are separate criteria that coincide
numerically for the small passenger class. Origin: the "Avoid this specific error" box in
`AI_Research_Tools_and_Scientific-Computing_Infrastructure_to_Accelerate_Can_It_Ford.md`,
a secondary aggregator summary. `paper_draft.md:54` was right all along.

**The underlying bug was still real, with a narrower cause:** the code applied the product
cap with no depth cap, which is what permitted 1.0 m of still water. The fix stands. The
stated reason for it did not.

### B3. **[NEW]** "The AR&R authors called their own Table 3 criteria non-conservative"

**FALSE.** See A3. The "clearly non-conservative" sentence is about the pre-existing
guidelines; Table 3 is offered as the revision that fixes them. Origin: this ledger's own
Section A3 as first drafted, and it had already propagated into the Section E framing
block. Caught on intake audit before commit.

---

## SECTION C: DOWNGRADED OR STILL UNVERIFIED

| Claim | Status | What would settle it |
|---|---|---|
| AR&R calibrated on steady flow, so comparing against a surge is a regime mismatch | **DOWNGRADED.** Source is silent, see A4 | A different primary source, or state honestly that the regime is unspecified |
| `water_eta` defaults to 1.0 Pa*s, 1000x real water at 1.0e-3 | **LIKELY, unconfirmed** | Read the FloodScene constructor default on the live Vista copy |
| The repo's own dam-break benchmark uses eta=1.0e-3 | **UNVERIFIED**, DeepWiki-sourced | Open `benchmarks/bench_vs_claymore.py` |
| Water depth resolution varies with depth, confounding the 0.30 m yaw-to-roll transition | **STANDS**, arithmetic from A9 | A convergence run at n_grid=128 |
| Divergence figures "16 / 30.4 percent" and "14 / 39.1 percent" | **BOTH UNVERIFIED** | Read the live `paper_draft.md` Section 4 |
| Yaris ground clearance under 0.12 m | **UNKNOWN** | Measure from the hull mesh |
| Yaris hull length 4.2826 m vs `paper_draft.md`'s 4.30 m | **CONTESTED, decides the class** | Measure the bbox from the canonical PLY |
| Yaris kerb weight 1100 kg vs `paper_draft.md`'s 1078 kg | **CONTESTED, verdict-neutral** | Pick one and propagate; both pass < 1250 |
| A9's decrease is convergence, not a sampling artifact | **INTERPRETATION, untested** | Raise `mesh.sample()` above 60k, re-run the probe, revert |
| A7 and A10 line numbers and figures | **CARRIED FORWARD**, not re-verified | Re-read the package |

---

## SECTION D: THE PATTERN, AND THE RULE THAT FOLLOWS

Of the July 24 audit's load-bearing claims:

| Origin of claim | Outcome |
|---|---|
| Read from source code | Correct (A6 refuted a claim, A7, A8, A9 all held) |
| Derived by arithmetic from source | Correct (A9, A10) |
| DeepWiki summary | 1 of 2 wrong (B1 wrong, A7 right) |
| Secondary aggregator report | Wrong (B2) |
| This project's own markdown | Right when it cited a real PDF (`paper_draft.md:54`), wrong when it cited itself |
| **[NEW] This ledger's own first draft** | **B3: one misattributed quote, caught on intake audit** |

**Standing rule.** DeepWiki and Perplexity-class output are hypotheses. A hypothesis may
motivate a source read. It may not drive a code edit, a mentor message, a poster claim, or
a paper claim. This is the same failure class as the recirculated "working MPM simulation"
claim, appearing in new tools.

**Sub-rule for DeepWiki specifically.** It was reliable on a structural question ("is X ever
assigned from Y", grep-verifiable) and unreliable on a control-flow question ("which branch
does this line sit in", indentation-dependent). Treat control-flow claims as unverified
until read.

**Sub-rule added on intake, and it is the one this file exists to survive.** A verbatim
quote is not a verified claim. B3 was a correctly transcribed sentence attached to the
wrong subject. Quoting accurately and attributing accurately are two separate checks. When
a quote carries an argument, read the sentence before and after it.

**Action required on project knowledge.** The
`AI_Research_Tools_and_Scientific-Computing_Infrastructure_to_Accelerate_Can_It_Ford.md`
file contains the refuted "Avoid this specific error" box. Annotate or remove it. Left
alone it will re-poison future sessions, exactly as the stale CLAUDE.md snapshot did.

---

## SECTION E: **[CORRECTED]** HOW THE FRAMING CHANGES

The previous framing block quoted "clearly non-conservative" as though the AR&R authors
said it about Table 3. Per A3 and B3 they did not. The corrected framing below is narrower
and it still supports the project, because what the authors actually asked for is exactly
what this work supplies.

Before: "a full-physics simulation disagrees with the published empirical criterion at N
points in phase space."

After, defensible against the source:

> The AR&R Project 10 Stage 2 authors found the vehicle stability guidelines then in force
> to be "clearly non-conservative," proposed the Table 3 criteria as an explicitly interim
> draft revision, and stated that further testing was required before any such criteria
> could stand: "Only criteria developed in such a rigorous way are suitable for presenting
> as true safety guidelines." They set out a five-point program of full-scale testing,
> frictional-coefficient measurement, computational-model calibration, and field
> verification to get there. Their interim criteria were themselves derived for stationary
> vehicles from 1:25 scale model tests and quasi-static axle-load measurements. This work
> supplies coupled full-scale physics of the kind that program calls for, and identifies
> where in depth-velocity space the interim criteria and a coupled model disagree for a
> small passenger vehicle.

Three limitations that must be declared alongside it:

1. The criteria are for stationary vehicles. The static sweep is in scope. A moving-vehicle
   fording case is an extension beyond the source.
2. The 3.0 m/s velocity cap is an evacuation safety limit imported from human stability
   work, not a vehicle stability result.
3. The AR&R report does not state the flow regime behind its curves. Its underlying
   experiments were incremental and quasi-static, while FloodScene applies an impulsive
   surge after settling. Declare this rather than assume equivalence.

**Do not write:** that the AR&R authors called Table 3 non-conservative. They said that of
the guidelines Table 3 replaces.

---

## SECTION F: VEHICLE ASSET INVENTORY, WHAT ACTUALLY EXISTS

**The honest headline: this project has ONE trustworthy vehicle mesh, not three.** It has
three vehicle PARAMETER SETS, which is a different thing. Any plan that assumes three
simulatable vehicles is assuming an asset that does not exist.

Verified against the repo on disk 2026-07-24 with `find -maxdepth 3`. Five mesh files
exist, resolving to three distinct meshes plus two byte-identical duplicates. **Zero .obj
files exist anywhere in the repo.**

### F1. Mesh assets

| File | Size | Status | Verified properties | Usable? |
|---|---|---|---|---|
| `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` | 11.87 MB | **CANONICAL** | 327,212 verts, 655,308 faces (both confirmed from PLY header), hull volume 3.5427 m3, bbox 4.2826 x 1.7461 x 1.5175 m **[bbox contested, see A5]**, mass 1100 kg (MASH 1100C class), source CCSA/GMU NCAC | **YES**, the only one |
| `vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` | 0.93 MB | DEPRECATED | 25,663 verts, 51,450 faces (both confirmed from PLY header), volume 6.8185 m3 (wrong), underbody bridged shut, ~62% bbox fill | NO |
| `data/truck_trimmed.ply` | 45.20 MB | **[F-2, CORRECTED]** present in THIS repo, and **UNTRACKED by git** | 191,107 vertices, NO face element, confirming surface-only splat point cloud. No native scale | Only via `fit_to_bbox()` anisotropic warping, which changed displacement by 4.6x in a same-condition test. NOT trustworthy |
| `can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` | 11.87 MB | **[F-1, ADDED]** duplicate in the nested repo tree | SHA-256 identical to canonical (`b379fa44...`) | Same content, do not edit this path |
| `can-it-ford/vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` | 0.93 MB | **[F-1, ADDED]** duplicate in the nested repo tree | SHA-256 identical to deprecated (`770ea5fe...`) | NO |
| box proxy 1.0 x 1.6 x 1.5 m | n/a | legacy generic | not a mesh | superseded |
| box proxy 4.66 x 1.79 x 1.44 m | n/a | sedan-scale | not a mesh | proxy only |

**[FLAG] The nested `can-it-ford/can-it-ford/` tree is the known embedded-repo incident**
(see `HANDOFF_AUDIT_2026-07-24/`). Its mesh copies are byte-identical, so there is no
"which one is real" ambiguity here, but edits made in the wrong tree will silently not
apply. The same duplication exists on Vista.

**[FLAG] `data/truck_trimmed.ply` is untracked.** 45.20 MB sitting in the working tree and
not in git. It is one `git add .` away from entering history. Decide deliberately whether
it belongs in the repo, in LFS, or in `.gitignore`.

### F4. **[OPEN PROVENANCE DEFECT]** Track 2 vehicle geometry is a superseded placeholder

`simulation/can_it_ford_L2_mpm.py:26` hardcodes `VEHICLE_SIZE = (4.66, 1.79, 1.44)`. That
value matches no class currently defined in `vehicle_params.py` and it is not the canonical
hull.

| Source | L x W x H (m) | Volume (m3) |
|---|---|---|
| `can_it_ford_L2_mpm.py:26` VEHICLE_SIZE | 4.66 x 1.79 x 1.44 | **12.0116** |
| `vehicle_params.py` compact_sedan (live) | 4.30 x 1.70 x 1.47 | 10.7457 |
| `yaris_coarse_v1l_watertight.ply` hull | 4.283 x 1.746 x 1.518 bbox | **3.5427** (trimesh hull) |

Box volume against hull volume is **12.0116 / 3.5427 = 3.391x**.

**Root cause, traced through git.** 4.66 x 1.79 x 1.44 is the pre-Yaris `compact_sedan`
placeholder. Commit `72974ab` introduced it. Commit `0b59eea` ("Restore Yaris
vehicle_params.py correction...") replaced it with the real 2010 Yaris FE geometry at
4.30 x 1.70 x 1.47. The string `4.66` no longer appears anywhere in `vehicle_params.py`.
The Track 2 script was never updated and is frozen at the superseded value. This is the
same failure class as A12: a constant moved in one file and not in its consumer.

**Consequence.** Any Track 2 density computed as mass over box volume inherits the 3.391x
error. At 1100 kg: 1100 / 12.0116 = 91.6 kg/m3 against 1100 / 3.5427 = 310.5 kg/m3 on the
hull. A 91.6 kg/m3 body is far below the 100 to 300 kg/m3 plausibility band in CLAUDE.md
and would float in almost any depth. Do not report a Track 2 rho, buoyancy, or float
verdict until this is reconciled.

**Not fixed here.** Recorded as an open defect only. Changing `VEHICLE_SIZE` alters every
Track 2 result and must be a deliberate, separately reviewed change.

**No SUV mesh exists. No pickup mesh exists.** Two independent reconstruction attempts to
build one failed: marching cubes stalled at genus 9, and Poisson reconstruction produced a
0.345 m long asset from a mismatched source point cloud.

### F2. Parameter sets, from NHTSA Light Vehicle Inertial Parameter Database and SAE 1999-01-1336

These are measured masses, footprints, and inertia tensors. They are **not** meshes.

| Class | Mass (kg) | bbox L x W x H (m) | CG height (m) | Ixx roll | Iyy pitch | Izz yaw |
|---|---|---|---|---|---|---|
| Compact sedan (Corolla/Civic) | 1390 | 4.66 x 1.79 x 1.44 | 0.52 | 365 | 1617 | 1785 |
| Midsize SUV (Highlander/Explorer) | 1990 | 4.96 x 1.93 x 1.75 | 0.70 | 740 | 3561 | 3682 |
| Light pickup (F-150/Tacoma) | 2300 | 5.89 x 2.03 x 1.96 | 0.69 | 839 | 5067 | 5070 |
| **Yaris hull (the only mesh)** | **1100** | **4.283 x 1.746 x 1.518** | not measured | not measured | not measured | not measured |

Note the inertia tensors are currently unused: FloodScene computes mass and inertia from the
rigid particle cloud via `finalize_rigid_bodies()`, not from a supplied tensor. Measured CG
height also sits well below bbox half-height, so a uniform-density solidified body
overstates the overturning moment. Both are real limitations to declare.

### F3. Materials, complete inventory

There are exactly two materials in this pipeline, not a library.

| Material | Where | Parameters | Correct value |
|---|---|---|---|
| `newtonian` water | FloodScene, `vehicle.py:274` | `eta`, `density`, `bulk_modulus` | FloodScene defaults `eta=1.0` (1000x too viscous), `density=1000`, `bulk_modulus=1.5e5`. Real water `eta=1.0e-3` |
| `newtonian` water | Track 1 box script | `eta=0.001, density=1000.0, bulk_modulus=2.0e5` | eta correct here |
| `"rigid"` | `set_material_range(n_water, n_total, "rigid", obj_id=0, density=vehicle_density)` | `density` back-solved from `vehicle_mass / solid_volume` | mass is exact if `vehicle_mass` is passed |

**[FLAG]** The `eta=1.0` default claim is listed as LIKELY but unconfirmed in Section C.
Read the FloodScene constructor before citing it.

**On the CCSA/GMU source archive:** those are LS-DYNA finite-element crash models and they
do carry real material cards (steel gauges, glass, plastics). **None of that is used and
none of it can be used here.** MPM treats the vehicle as a single rigid body. Only the
surface hull is consumed, and then only as a 60,000-point sample (see A8). Describe the
asset in the paper as a validated-geometry rigid hull at MASH 1100C class mass. Do not
describe it as a validated vehicle model.

---

## SECTION G: THE THREE-CLASS PLAN, DONE CORRECTLY

### G1. The distinction that makes this legitimate

The three AR&R classes are properties of the **criterion**, not of the simulation. You can
evaluate all three L1 thresholds against one L2 simulation. What you cannot do is claim you
simulated three vehicles.

- **Legitimate:** "Divergence between L1 and L2 persists even when L1 is evaluated at the
  most permissive published class threshold."
- **A category error:** "We simulated a 4WD." A 1100 kg Yaris hull is not a 4WD at any
  threshold.

### G2. **[FILLED]** Class assignment of every asset, against the primary-source boundaries

D3 closed. All three boundary rows have now been read verbatim from Table 3, PDF p.24:

| Class | Length (m) | Kerb Weight (kg) | Ground clearance (m) |
|---|---|---|---|
| Small passenger | < 4.3 | < 1250 | < 0.12 |
| Large passenger | > 4.3 | > 1250 | > 0.12 |
| Large 4WD | > 4.5 | > 2000 | > 0.22 |

| Asset | Mass | Length | AR&R class | Confidence |
|---|---|---|---|---|
| Yaris hull | 1100 kg | 4.283 m | **Small passenger** | weight PASS. Length PASS only if 4.2826 is correct, `paper_draft.md` says 4.30 which FAILS. Ground clearance UNVERIFIED and may FAIL |
| Compact sedan proxy | 1390 kg | 4.66 m | **Large passenger** | length > 4.3 and weight > 1250 both satisfied; under the 4.5 m and 2000 kg 4WD bounds |
| Midsize SUV params | 1990 kg | 4.96 m | **Large passenger** | length > 4.5 but weight 1990 < 2000, so it fails the Large 4WD weight bound. Falls to Large passenger on weight |
| Light pickup params | 2300 kg | 5.89 m | **Large 4WD** | length > 4.5 and weight > 2000 both satisfied |

**[FLAG] The SUV is a genuine edge case.** At 1990 kg it misses the Large 4WD weight bound
of > 2000 kg by 10 kg while exceeding the length bound. The report gives no tie-break when
length and weight disagree, so this assignment is a judgement call, not a source fact.
Ground clearance, the third criterion, is unmeasured for every parameter-set asset.

**Consequence worth noting:** the Yaris hull is the only asset in this project that maps to
Small passenger. The 1390 kg sedan box proxy used in earlier work is Large passenger by
weight and length, so historical use of the 0.60 (Large 4WD) threshold with that proxy was
wrong in a different way than previously described.

### G3. All three thresholds evaluated over the existing 70-cell sweep

Recomputed live from `data/scenario_sweep.csv` on 2026-07-24 using the joint criterion
(depth cap AND velocity cap AND D x V cap). All figures below confirmed.

| Criterion | depth cap | v cap | DV cap | FORD | NO-FORD |
|---|---|---|---|---|---|
| Small passenger | 0.30 m | 3.0 m/s | 0.30 | **12** | 58 |
| Large passenger | 0.40 m | 3.0 m/s | 0.45 | **19** | 51 |
| Large 4WD | 0.50 m | 3.0 m/s | 0.60 | **24** | 46 |
| *historical bare product, strict* | none | none | 0.60 | *33* | *37* |
| *historical bare product, inclusive* | none | none | 0.60 | *37* | *33* |

**12 of 70 cells are class-sensitive**, meaning at least two classes disagree. Count
confirmed live. That band is the useful figure, and it is where a class-sensitivity panel
on the poster earns its space:

| depth | velocity | Small passenger | Large passenger | Large 4WD |
|---|---|---|---|---|
| 0.1 | 3.0 | NO-FORD | FORD | FORD |
| 0.2 | 1.5 | NO-FORD | FORD | FORD |
| 0.2 | 2.0 | NO-FORD | FORD | FORD |
| 0.2 | 2.5 | NO-FORD | NO-FORD | FORD |
| 0.3 | 1.5 | NO-FORD | FORD | FORD |
| 0.3 | 2.0 | NO-FORD | NO-FORD | FORD |
| 0.4 | 0.0 | NO-FORD | FORD | FORD |
| 0.4 | 0.5 | NO-FORD | FORD | FORD |
| 0.4 | 1.0 | NO-FORD | FORD | FORD |
| 0.5 | 0.0 | NO-FORD | NO-FORD | FORD |
| 0.5 | 0.5 | NO-FORD | NO-FORD | FORD |
| 0.5 | 1.0 | NO-FORD | NO-FORD | FORD |

The 0.3 / 1.5 row is `paper_draft.md`'s canonical divergence example. It is class-sensitive:
NO-FORD as Small passenger, FORD as Large 4WD. Any claim about that cell must state the
class.

### G4. NEW MINOR BUG: boundary inclusivity disagreement

Confirmed live. The CSV generator used `DV <= 0.60` and the analysis scripts used
`DV < 0.60`. Exactly four cells sit on DV = 0.60, enumerated live as (0.2, 3.0), (0.3, 2.0),
(0.4, 1.5), (0.6, 1.0), so the two implementations disagree by 4 rows: 37 FORD versus
33 FORD.

**The source settles it.** Table 3 writes the criterion as "DV <= 0.3", inclusive. The
strict `<` in the analysis scripts is wrong by the source's own notation. Fix to `<=`
everywhere and note that any previously reported count of 33 was low by 4.

**[FLAG] Not yet fixed.** `analysis/make_phase_space_v2.py:9` still reads `h < 0.60`.

### G5. What to actually build

One L2 simulation on the Yaris hull. Three L1 verdict columns. Emit them all.

Required CSV columns going forward:

```
depth_m, velocity_ms,
L0_verdict,
L1_haz,
L1_verdict_small_passenger, L1_verdict_large_passenger, L1_verdict_large_4wd,
L1_class_sensitive,
L2_verdict, L2_failure_mode, L2_dmag, L2_yaw_deg, L2_pitch_deg, L2_roll_deg,
n_grid, dx, water_layers, solid_volume, realized_rho, water_eta, floor_friction,
vehicle_asset, vehicle_mass_kg
```

The provenance columns at the end are not optional. Every finding retracted on July 24 was
retracted because a number existed without the settings that produced it.

**[FLAG] Current schema is 8 columns, not this.** See A11. The current file emits
`L1_verdict_small_car` and `L1_verdict_four_wd`, missing `large_passenger`,
`L1_class_sensitive`, every L2 column, and every provenance column. G5 is a target, not a
description of what exists.
