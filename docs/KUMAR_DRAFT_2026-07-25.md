# Can It Ford: progress, 2026-07-25

Josie Cerrell. Every number below was read live from this repo before it was written. Where a
number could not be reproduced on this machine, it is labeled as reported rather than as
verified.

Deadlines this covers: **poster Monday July 27, 09:00 CST**, **session July 30**,
**paper July 31**.

Scope note on credit. The query-conditioned physically-viable-world-model framework is
Thorpe et al., arXiv:2605.30542. My contribution is the closed reconstruct-to-decide pipeline
and the L0/L1/L2 abstraction-ladder experiment built on top of it.

---

## 0. Where this stands

The headline changed today. For most of the summer the strongest result was negative, a
geometry bias that made every buoyancy and traction number untrustworthy. That bias was
isolated, fixed, and verified this afternoon, and the corrected pipeline then produced the
first render-verified coupled MPM flood simulation with a real car-scale vehicle at correct
mass and correct displaced volume.

Three results now stand, in order of how hard I would defend them:

1. **A published safety criterion returns one answer per vehicle class, not one answer.**
   12 of 70 conditions flip verdict on vehicle class alone.
2. **The abstraction ladder diverges at exactly one class, and only under one reading of the
   criterion.** At 0.30 m and 1.5 m/s, L1 and L2 agree for small passenger and Large 4WD and
   disagree for large passenger. Under the local-flow reading of the same criterion, all three
   agree.
3. **A geometry pipeline can silently double a vehicle's displaced volume, and watertightness
   does not protect against it.** Diagnosed, quantified at 2.18x, and fixed to 1.0023x.

The honest caveat that governs all three: the fix is uncommitted, and the coupled result exists
at one depth-velocity condition, not a sweep.

---

## 1. What is verified

**The three-class AR&R L1 rule is implemented and sourced.**
`vehicle_params.py:165` defines `AR_R_STABILITY_LIMITS`. `vehicle_params.py:186` defines
`L1_verdict`, which returns NO-FORD if depth exceeds the class depth cap, or velocity exceeds
the class velocity cap, or the depth-velocity product exceeds the class hazard cap. All three
conditions apply jointly.

| Class | Depth cap (m) | Velocity cap (m/s) | D x V cap (m2/s) |
|---|---|---|---|
| small_passenger | 0.30 | 3.0 | 0.30 |
| large_passenger | 0.40 | 3.0 | 0.45 |
| large_4wd | 0.50 | 3.0 | 0.60 |

The citation string carried in the module, `AR_R_SOURCE`, verbatim:

> Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2, P10/S2/020,
> ISBN 978-0-85825-948-5, Table 3 'Proposed DRAFT Stability Criteria for Stationary Vehicles',
> PDF p.24 / printed p.14. Values are the report's own DRAFT INTERIM figures for STATIONARY
> vehicles, not an endorsed safety standard.

The draft-interim-stationary qualifier is in the code, not only in the prose, so no consumer
can pick up the numbers without it.

**The sweep is 70 rows, 10 columns.** `data/scenario_sweep.csv`, read live: 70 data rows,
10 depths from 0.1 to 1.0 m crossed with 7 velocities from 0.0 to 3.0 m/s. Header:

    depth_m, velocity_ms, L0_verdict, L1_haz, L1_haz_product_only, L1_verdict,
    L1_verdict_small_passenger, L1_verdict_large_passenger, L1_verdict_large_4wd,
    L1_class_sensitive

L0 is the static rule at `scripts/gen_scenario_sweep.py:24`, FORD if depth <= 0.15 m, which
clears 7 of 70 rows.

**Counts recomputed from the live file, not copied from any figure or summary:**

| Class | FORD | NO-FORD |
|---|---|---|
| Small passenger | 14 | 56 |
| Large passenger | 19 | 51 |
| Large 4WD | 26 | 44 |

12 of 70 cells are class-sensitive, meaning at least two classes disagree. The class regions
nest strictly: no cell clears a small passenger car and fails a Large 4WD. The headline case
holds, 0.30 m of water at 1.5 m/s is NO-FORD for a small passenger car and FORD for a large
passenger vehicle and a Large 4WD.

**Two corrections that a reader of the repo will otherwise hit.**

1. A float-comparison defect at the D x V boundary was found and fixed, and the fix is
   uncommitted. `vehicle_params.py:197` now reads `round(depth_m * velocity_ms, 6)`. Before
   the fix it compared the raw product, so `0.1 * 3.0` evaluated to `0.30000000000000004` and
   the bound meant to be inclusive excluded exactly the grid points it was written to include.
   Four of 70 rows flipped. `data/scenario_sweep.csv` has been regenerated and is also
   uncommitted.

2. That regeneration briefly left `figures/fig1_l1_three_class.pdf` and its caption stale
   against the CSV, with four wrong count claims. Both have since been reissued and the figure
   now agrees with the file. Verified live: CSV mtime 17:11, figure regenerated 17:35, caption
   17:42, and the script's own tripwire constants updated from 12/19/24 to 14/19/26. The four
   corrected counts are 14 cells clearing all three classes, 44 clearing none, 7 class-sensitive
   cells clearing only Large 4WD, and 5 clearing both 4WD and large passenger.

   The 12 class-sensitive total, the strict nesting, and the headline example never changed.
   The old figure was a correct rendering of a superseded CSV, not a wrong figure.

   Worth noting how this was caught, because the mechanism generalizes. The plotting script
   carries hardcoded expected counts and raises `SystemExit` rather than redrawing when the CSV
   stops matching them. That tripwire is why a four-row data change could not silently reach
   print through the figure path.

`vehicle_params.py:83` carries `mass_kg: 1100.0`, confirmed live.

---

## 2. The geometry finding, and the fix

This was the strongest original result for most of the day and it was a negative one. It is no
longer negative: the mechanism was isolated, and a corrected algorithm was written and verified
this afternoon. The diagnosis below is what matters and it is unchanged. What changed is that
the bias it describes is now fixed on the mesh path.

**Mechanism.** `solidify_columns` in the engine's `vehicle.py` voxelizes the vehicle surface
sample at pitch h, groups the voxels into (x, y) columns, and for each column emits every cell
between that column's own lowest and highest occupied z. There is no interiority test, no ray
cast, no winding number, no flood fill. Each column is bridged floor to ceiling. Its own
docstring names the tradeoff, that wheel wells and window openings merge into the solid and
that for blocking flow this is the right approximation.

The consequence is the one that matters here. Watertightness buys nothing, because the
algorithm never asks whether a point is inside the body. A watertight hull occupies nearly
every column, so nothing hollows out, and instead every concavity gets bridged shut, including
the gap under the floor pan. **A watertight hull is over-filled, not hollow.** That inverts the
failure mode recorded earlier in this project, which was a hollowing failure specific to a
sparse surface-only splat.

**Measured, before the fix.** At n_grid=64 the solidified body occupied 7.71011 m3 against a
true hull volume of 3.542739 m3 from `mesh.volume` on the watertight Yaris. That is a ratio of
**2.1763**, or 118 percent more displaced volume than the vehicle actually has. At a 0.30 m
waterline the submerged volume was **0.8499 m3** against **0.51920 m3**, a **1.64x buoyancy
bias**. Buoyant force scales with displaced volume, so that error propagated at full strength
into flotation and with the opposite sign into normal force and therefore traction. No FLOAT
verdict from the pipeline was safe in that state, and every sweep produced before today
inherits it.

**The fix.** `solidify_watertight(mesh, h)` in `src/warpmpm/vehicle.py`, exact vertical ray
parity. Per grid column it collects every z where the column axis crosses the surface, sorts
them, and fills only between successive entry and exit pairs, so genuine voids stay empty. It
is exact for a closed surface, resolution independent, and runs in about 0.1 s. `VehicleBody`
gained a `mesh` field carrying the oriented hull; `solidify()` uses parity fill when a
watertight mesh is present and otherwise falls back to `solidify_columns`.

Verified standalone against the true hull volume of 3.54274 m3, target rho 310.49:

| n_grid | h (mm) | N | volume (m3) | ratio | rho |
|---|---|---|---|---|---|
| 48 | 98.14 | 3846 | 3.63566 | 1.0262 | 302.56 |
| 64 | 73.61 | 8904 | 3.55094 | 1.0023 | 309.78 |
| 96 | 49.07 | 29807 | 3.52211 | 0.9942 | 312.31 |
| 128 | 36.80 | 71154 | 3.54705 | 1.0012 | 310.12 |

Realized mass is 1100.00 kg at every row. In the live simulation the instrumented value is
`solid_volume=3.55086 m3, hull=3.54274 m3, fill_ratio=1.0023`.

The regression check is the part I would point at first. Forcing `mesh` to None returns 19338
particles at ratio **2.1769**, which reproduces the 2.1763 measured for `solidify_columns`
independently. So the two numbers are the same algorithm measured twice, not a disagreement,
and splat shells still take the column-fill path as intended. `truck_trimmed.ply` and any holey
surface-only asset are unaffected by the fix and still carry the 2.18x bias.

**Raising n_grid was never the lever, and no longer needs to be.** Refinement shrank the bridged
volume monotonically because cells get smaller, but the underbody stayed closed for as long as
the algorithm bridged rather than tested interiority, so the ratio never converged to 1.0 at any
resolution from n_grid 32 to 192. Parity fill converges immediately instead: the table above
holds 0.9942 to 1.0262 across n_grid 48 to 128, so resolution can now be chosen on cost and
water resolution rather than to chase a geometry error.

One limit survives the fix untouched and still caps useful resolution: the engine resamples the
mesh to a fixed 60,000-point surface cloud, and an oversampling test against 1,000,000 points
showed the 60k sample diverging by 1.8, 4.6, 12.3 and 37.2 percent at n_grid 64, 96, 128 and
192. Sixty thousand samples are adequate at 64, marginal at 96, and inadequate above that.

**A standing project rule is now wrong and I would rather say so than quietly widen it.**
`CLAUDE.md` carries a vehicle effective-density plausibility band of 100 to 300 kg/m3. The
correct density for a 1100 kg Yaris on a 3.5427 m3 hull is **310.5 kg/m3**, above the band, and
the corrected runs realize 302.6 to 312.3 across n_grid 48 to 192. The band was only ever
satisfied because the over-fill diluted the density. It was a check that passed for the wrong
reason. The band needs restating; the vehicle does not need adjusting.

**The grid is mostly empty water.** The domain is sized `lim = max(2.2 * length, 3.5 * width,
6.0 * depth)`. For the Yaris, `2.2 * 4.2826 = 9.4217 m`, so a 4.28 m car sits in a 9.42 m cube
and most cells resolve water that never touches the vehicle. At n_grid=64 that gives
dx = 0.14721 m and only 4 water layers at 0.30 m depth.

**One provenance conflict, since you read the repo directly.** Two grid-gate handoffs dated
today disagree. `.claude/handoffs/2026-07-25_ford-F0-gridgate.md` reports a ratio of 2.413 and
a solid volume of 8.5475 m3 at n_grid=64, with lim = 14.9890. That pane computed lim from the
raw bounding box and skipped `load_vehicle`'s y-long-axis swap, which fires when
`ext[0] > ext[1]`. The 2.1763 figure is corroborated three ways and the regression check above
independently reproduces it at 2.1769. That handoff has since had a correction block appended
to it and to `INDEX.md`. Anything still quoting 2.41x, 8.5475 m3 or 143 kg/m3 is stale. The
same handoff also states that `load_vehicle` cannot load this PLY at all, which is false: it
was reading a second, non-installed copy of the engine tree. Verified live, the mesh loads, is
watertight, and reports volume 3.5427 with 655,308 faces.

---

## 3. The coupled result: MPM-REAL, and where the ladder diverges

**Single run, job 866214.** First render-verified coupled MPM flood simulation with a real
car-scale vehicle at correct mass and correct displaced volume. Depth 0.30 m, surge 1.5 m/s,
n_grid 64, 90 frames, 1100 kg Yaris, exit code 0.

Read live from `renders/yaris_L2_d0p30_v1p5/metrics.csv`, 91 rows, 15 columns:
final displacement magnitude **0.09043 m**, yaw **+1.2506 deg**, roll +0.0094 deg,
pitch -0.0035 deg. All gate criteria pass, including zero particle-frames outside the domain,
no vertical rise, and 3.71 percent maximum water fraction inside the vehicle bounding box.
Artifacts on the Mac: `flood_vehicle_yaris.mp4` (272270 B), `metrics.csv`, `instrument.npz`,
`run_866214.log`, 45 frames.

**Three-class study, job 866266.** Same hull, same scene, three masses. All numbers below read
live from `renders/yaris_render_s1/gates_results.json` and every verdict independently
re-derived by calling the live `L1_verdict` on the stored depths and velocities.

| Class | Mass (kg) | rho | Final disp (m) | vs 0.05 m | L1 nominal | L2 | Agree? |
|---|---|---|---|---|---|---|---|
| small_passenger | 1100 | 309.75 | 0.09240 | 1.85x | NO-FORD | NO-FORD | AGREE |
| large_passenger | 1609 | 453.13 | 0.05110 | 1.02x | FORD | NO-FORD | **DIVERGE** |
| large_4wd | 2337 | 658.14 | 0.03890 | 0.78x | FORD | FORD | AGREE |

**Read this before quoting the table.** V1 is a **mass-only** sensitivity study. All three runs
use the same 2010 Toyota Yaris hull and only `--vehicle-mass` changes. The 1609 kg row is not a
Nissan Rogue and the 2337 kg row is not a Silverado. Real Silverado and Rogue meshes exist as
NCAC LS-DYNA decks and are not converted. Geometry effects, frontal area, ground clearance and
static stability factor are entirely absent, and ground clearance is exactly what AR&R classes
on. These rows must not carry vehicle names in any figure, poster or paper.

**The divergence is real and it is thin.** The large_passenger drift is 0.05110 m against a
0.05000 m threshold, 2.2 percent above it. That is inside its own uncertainty and I will not
present it as a robust divergence. What survives the thinness is the structural claim: the
divergence is class-dependent, so the earlier class-free statement of a divergence zone was
false for two of the three classes and has been retracted rather than patched.

**The threshold caveat travels with every verdict in that table.** `DRIFT_THRESHOLD = 0.05 m`
is a conservative numerical onset-of-motion tolerance, not a peer-reviewed physical stability
criterion. No such absolute drift criterion exists in the flood-vehicle literature. It must
appear in the same sentence as any FORD or NO-FORD claim, and on the poster it does.

---

## 4. The sharpest open question, and it is a definitional one

AR&R's D and V are undefined for a transient surge, and which definition you pick decides a
verdict.

The nominal condition is depth 0.30 m and velocity 1.5 m/s, giving D x V of 0.4500 m2/s. The
flow the vehicle actually experiences is not that. Measured at the vehicle, local depth rises
because of the bow wave while local speed collapses at stagnation:

| Class | Local depth peak (m) | Local speed peak (m/s) | Local D x V | vs nominal |
|---|---|---|---|---|
| small_passenger | 0.3974 | 0.4760 | 0.1892 | 58 percent lower |
| large_passenger | 0.4159 | 0.3956 | 0.1645 | 63 percent lower |
| large_4wd | 0.4260 | 0.3592 | 0.1530 | 66 percent lower |

Re-running the live `L1_verdict` on those local values, verified by direct execution:

| Class | L1 nominal | L1 local | L2 | Agreement under local reading |
|---|---|---|---|---|
| small_passenger | NO-FORD | NO-FORD | NO-FORD | AGREE |
| large_passenger | **FORD** | **NO-FORD** | NO-FORD | AGREE |
| large_4wd | FORD | FORD | FORD | AGREE |

Under the local reading the single divergence disappears and all three classes agree. The flip
for large_passenger is driven by the **depth** cap, not the product cap: local peak depth of
0.4159 m exceeds its 0.40 m limit even though local D x V of 0.1645 is far under its 0.45 cap.

The report does not say which definition it intends. This is the whole ballgame for that class,
and it is the most interesting thing I found this week, because it says the L1-versus-L2
comparison is not well posed until the criterion's own input is pinned down. I would rather
present that honestly than pick the definition that produces a divergence.

---

## 5. Superseded and retracted artifacts

**The July 13 render is superseded, not a result.**
`renders/mpm-engine-out/flood_vehicle/flood_vehicle.mp4`, 372509 bytes, 2026-07-13 18:53,
verified live. Its body is the engine's bundled demo splat, `truck_trimmed.ply`, at model scale,
extent 0.45 x 1.447 x 0.411 m and 28.7 kg, at the script's defaults of depth 0.12 m and
velocity 1.5 m/s. It is not the Yaris, not 1100 kg and not 4.28 m. Under Froude scaling with
lam = 5.5 / 1.45 = 3.79, depth by lam, velocity by sqrt(lam), displacement by lam and mass by
lam^3, it reads as 0.455 m of water at 2.921 m/s, D x V of 1.330 m2/s, peak displacement 2.694 m
and mass 1566 kg. At that condition L1 returns NO-FORD for all three classes and the scaled
drift exceeds the threshold by a factor of 54, so both rungs agree. It was a methods
demonstration, never a divergence result. Job 866214 supersedes it for every purpose and it
should not appear on the poster.

**An earlier Track 2 set of FORD verdicts is retracted, not blocked.** In that scene the water
sat 0.295 m from the vehicle with inflow velocity 0, and vehicle displacement logged 0.0000 m at
every one of 500 steps. The single velocity signature in the run matches free fall through the
vehicle's own ground clearance. Those verdicts never measured what they claimed to measure and
no future run rehabilitates them.

**Both existing sweeps are superseded.** `data/track1_sweep_v1` and `data/track1_sweep_v2`
predate the fix and inherit the 2.17x over-fill. v2 additionally inherits `fit_to_bbox`-warped
truck geometry, which produced a 4.6x divergence in a same-condition test and is on the
do-not-ship list.

---

## 6. What is not done

**The fix is uncommitted.** This is the single highest risk item in the project. The patch lives
only as a working-tree edit in `mpm-engine` on Vista, at HEAD `fd390d6`, alongside another
lane's CSV-column work in the same file. Every corrected number above depends on it. A lost
`$WORK` or a stray `git checkout` erases the result, and until it is committed none of these
numbers can be regenerated from a revision.

**No sweep on corrected geometry.** One condition exists, 0.30 m and 1.5 m/s. A phase-space
figure needs a grid, and that is the largest remaining piece of work.

**No reconstructed environment, and the two halves of the pipeline have never been connected.**
`FloodScene` builds a bare box: one floor plane, four inset slip walls, plus the engine's own
domain walls. There is no terrain, no DEM, no reconstructed scene. The gsplat half of the
reconstruct-to-decide pipeline has never fed the simulation half.

**Water viscosity is wrong by three orders of magnitude.** The `FloodScene` constructor defaults
`water_eta = 1.0` Pa s. Real water is 1.0e-3. The separate Track 1 box script sets 0.001
correctly, so the two paths disagree with each other. Bulk modulus is also deliberately softened
to 1.5e5 for timestep stability, so the bulk wave speed is not physical. That one is a
documented tradeoff and belongs in Limitations so it does not read as an oversight.

**It is a finite surge, not a sustained flood.** A finite water slab spawns upstream and receives
a one-shot initial velocity along +x. There is no inlet and no outlet. Local depth at the vehicle
decays from a 0.40 to 0.43 m peak down to 0.107 to 0.124 m by frame 89 as the slab drains
downstream. Any steady-state fording claim needs an inflow boundary condition that does not
exist.

I want to correct one framing I have used before and should not have. It is not defensible to
say this is a surge "where AR&R used steady flow." The AR&R report never states a flow regime.
The strings steady, unsteady, surge, dam-break and transient appear zero times in a verified
complete extraction of 94,042 characters. Its underlying experiments read as incremental and
quasi-static, but the report does not label the regime. The honest limitation is that the source
does not specify the regime and my scene is a one-shot surge, so the comparison is unconstrained
in a direction I cannot bound.

**No ground truth exists for shallow-flood hydrodynamics at this scale.** No published
wave-propagation or bow-wake benchmark exists for either engine. The fluid behavior is
unvalidated, which is not the same as known-bad, and it should be stated as unvalidated.

**Runs are not bit-reproducible.** `mesh.sample(60_000)` is unseeded, so the body's placement
shift jitters run to run. Measured effect is small, 8904 particles locally against 8905 on Vista
from identical inputs, but the exact particle count is not a stable citation and this session's
reproduction of job 866214 gave 0.09240 m against 0.09043 m on disk, 2.2 percent apart.

**Every current poster figure is generated by an untracked script.** `plot_l1_three_class.py`,
`plot_traction_bias.py`, `plot_geometry_pipeline.py` and `recompute_l1_l2.py` are all untracked,
so a clean clone reproduces none of them.

**Track 2 Genesis is blocked and is a separate track.** P2G `CUDA_ERROR_ILLEGAL_ADDRESS` at
grid_density >= 96; grid_density 64 runs to completion but those runs have 21 to 31 percent of
water particles inside the vehicle. Escalated to Cristian Moran. Its numbers must not be mixed
into the L2 results above.

---

## 7. Deliverable readiness against the three deadlines

**Poster, due Monday July 27 at 09:00 CST.** Requirements from the REU instructions and their
current state:

| Requirement | State |
|---|---|
| PDF, under 40 MB | Met. `figures/Cerrell_TACC_42x56.pdf`, 404 KB |
| Filename `Lastname_TACC_PosterSize` | Met. `Cerrell_TACC_42x56.pdf` |
| Size, preferred 42x56, not to exceed 42x60 | **Check this.** MediaBox is 4032 x 3024 pt, which is 56 wide by 42 tall. The file is named 42x56 but the page is landscape 56x42, so either the orientation or the filename is wrong, and 56 inches exceeds 42 on that axis under a strict reading of the limit |
| Intro carries full name, major, institution, REU program, mentors | Drafted in `docs/POSTER_TEXT_BLOCKS.md` sections 2 and 3 |
| Acknowledgments name NSF, UT Austin TACC, and Award #2447887 | Met, wording verified against `Instructions.docx.md:30` |
| General audience, societal impact, future directions | Met in the condensed cut, section 12 |
| Few key data points, not a paper on a board | Met. One L1 figure, one L2 result, one geometry finding |

Poster gaps I would fix in this order: commit the patch, place an L2 asset from the corrected
geometry since the only verified poster figure today is L1-only, resolve the page-size question,
and fill the two empty logo slots. The class-free divergence-zone sentence has already been
retracted.

**Session, July 30.** Needs the corrected-geometry sweep, the density-band restatement, and a
decision on the nominal-versus-local D x V question in section 4.

**Paper, July 31.** IEEE conference format, `paper/conference_101719.tex`, sections
Introduction, Prior Work, Approach, Results, Conclusions, Future Work. Results currently
supports one L1 figure, one coupled condition and one three-class mass study. The three-class
result must be labeled mass-only on one geometry until the Silverado and Rogue decks are
converted, and two prior attempts at that conversion failed, marching cubes stalling at genus 9
and Poisson producing a 0.345 m asset. Limitations must carry the softened bulk modulus, the
unvalidated hydrodynamics, the finite surge, and the drift-threshold framing.

---

## 8. The one question for you

**Should I spend the remaining time on a coarse sweep, or on committing and hardening what
exists?**

I can get one of these done properly before July 31, not both.

The sweep argument is that a phase-space figure needs a grid and I have one point. The
hardening argument is that the single most valuable result of the summer currently exists as an
uncommitted working-tree edit on one machine, the figures come from untracked scripts, and the
runs are not bit-reproducible.

My instinct is hardening first, because a sweep built on an uncommitted solver is a sweep I
cannot defend or regenerate, and because the July 30 session is a better place to show one
verified condition with a clean provenance trail than a grid I cannot reproduce. But the poster
is thin on L2 without a sweep, so I would rather you rule.

The related sizing question, if there is time after: the domain is `lim = 2.2 * vehicle_length`,
which puts a 4.28 m car in a 9.42 m box and spends most of the grid on water that never reaches
the vehicle. Shrinking it buys vehicle resolution far more cheaply than raising n_grid, and
n_grid is expensive at 15.4x for 128 and 72.2x for 192. I have not touched it because box
dimensions are coupled: domain size sets dx, dx sets the water layer count and the substep rate,
and the walls are inset 4 cells specifically so a surge cannot penetrate them. A smaller box also
changes the blockage ratio, which changes the physics rather than just the cost.
